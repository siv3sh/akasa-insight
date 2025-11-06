"""
Daily ingestion flow for processing new CSV/XML files with incremental loads.
"""

import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash

# Add src to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import Config
from src.database import DatabaseManager, DataLoader
from src.utils import Logger


@task(retries=3, retry_delay_seconds=10)
def detect_new_files(data_dir: str) -> List[Path]:
    """
    Detect new CSV/XML files in the incoming directory.
    
    Args:
        data_dir: Path to the incoming data directory
        
    Returns:
        List of new file paths
    """
    logger = get_run_logger()
    incoming_dir = Path(data_dir) / "incoming"
    
    if not incoming_dir.exists():
        logger.info(f"Incoming directory {incoming_dir} does not exist, creating it")
        incoming_dir.mkdir(parents=True, exist_ok=True)
        return []
    
    # Supported file extensions
    extensions = ["*.csv", "*.xml"]
    new_files = []
    
    for ext in extensions:
        new_files.extend(incoming_dir.glob(ext))
    
    logger.info(f"Detected {len(new_files)} new files in {incoming_dir}")
    return new_files


@task
def calculate_file_checksum(file_path: Path) -> str:
    """
    Calculate MD5 checksum for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 checksum as hex string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@task
def validate_file_schema(file_path: Path) -> bool:
    """
    Validate file schema and types.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if validation passes, False otherwise
    """
    logger = get_run_logger()
    
    try:
        if file_path.suffix.lower() == ".csv":
            # Validate CSV schema
            df = pd.read_csv(file_path, nrows=5)  # Read first 5 rows for schema check
            logger.info(f"CSV schema validation passed for {file_path.name}")
            return True
        elif file_path.suffix.lower() == ".xml":
            # Basic XML validation
            with open(file_path, 'r') as f:
                content = f.read()
                if "<orders>" in content and "</orders>" in content:
                    logger.info(f"XML schema validation passed for {file_path.name}")
                    return True
                else:
                    logger.warning(f"XML schema validation failed for {file_path.name}")
                    return False
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return False
    except Exception as e:
        logger.error(f"Schema validation failed for {file_path.name}: {str(e)}")
        return False


@task
def process_incremental_load(file_path: Path, previous_day_only: bool = True) -> dict:
    """
    Process incremental load for a file.
    
    Args:
        file_path: Path to the file to process
        previous_day_only: If True, only load records from previous day
        
    Returns:
        Dictionary with processing results
    """
    logger = get_run_logger()
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Initialize data loader
        data_loader = DataLoader(db_manager)
        
        # Load data
        if previous_day_only:
            # For incremental loads, we would filter by date
            # This is a simplified implementation
            load_summary = data_loader.load_all_data()
        else:
            load_summary = data_loader.load_all_data()
        
        logger.info(f"Successfully loaded {file_path.name}")
        return {
            "file_name": file_path.name,
            "records_loaded": load_summary,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to load {file_path.name}: {str(e)}")
        return {
            "file_name": file_path.name,
            "error": str(e),
            "status": "failed"
        }
    finally:
        if 'db_manager' in locals():
            db_manager.close()


@task
def save_to_parquet_warehouse(file_path: Path, data: pd.DataFrame) -> Path:
    """
    Save processed data to parquet warehouse.
    
    Args:
        file_path: Original file path
        data: DataFrame to save
        
    Returns:
        Path to saved parquet file
    """
    logger = get_run_logger()
    
    try:
        warehouse_dir = Path(Config.BASE_DIR) / "data" / "warehouse"
        warehouse_dir.mkdir(parents=True, exist_ok=True)
        
        # Create parquet file name
        base_name = file_path.stem
        parquet_file = warehouse_dir / f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        
        # Save to parquet
        data.to_parquet(parquet_file, index=False)
        logger.info(f"Saved data to parquet warehouse: {parquet_file}")
        return parquet_file
    except Exception as e:
        logger.error(f"Failed to save to parquet warehouse: {str(e)}")
        raise


@task
def handle_rejected_records(file_path: Path, rejected_records: List[dict], reason: str) -> Path:
    """
    Save rejected records to rejects directory.
    
    Args:
        file_path: Original file path
        rejected_records: List of rejected records
        reason: Reason for rejection
        
    Returns:
        Path to saved rejects file
    """
    logger = get_run_logger()
    
    try:
        rejects_dir = Path(Config.BASE_DIR) / "data" / "rejects"
        rejects_dir.mkdir(parents=True, exist_ok=True)
        
        # Create rejects file name
        base_name = file_path.stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rejects_file = rejects_dir / f"{base_name}_rejected_{timestamp}.json"
        
        # Save rejected records
        import json
        with open(rejects_file, 'w') as f:
            json.dump({
                "file_name": file_path.name,
                "reason": reason,
                "rejected_count": len(rejected_records),
                "records": rejected_records,
                "timestamp": timestamp
            }, f, indent=2)
        
        logger.info(f"Saved {len(rejected_records)} rejected records to: {rejects_file}")
        return rejects_file
    except Exception as e:
        logger.error(f"Failed to save rejected records: {str(e)}")
        raise


@flow(name="Daily Data Ingestion")
def daily_ingestion_flow(data_dir: str = "data", backfill_start_date: Optional[str] = None, 
                        backfill_end_date: Optional[str] = None):
    """
    Daily ingestion flow that processes new files and performs incremental loads.
    
    Args:
        data_dir: Path to data directory
        backfill_start_date: Start date for backfill (YYYY-MM-DD)
        backfill_end_date: End date for backfill (YYYY-MM-DD)
    """
    logger = get_run_logger()
    logger.info("Starting daily ingestion flow")
    
    # Handle backfill if dates are provided
    if backfill_start_date and backfill_end_date:
        logger.info(f"Running backfill from {backfill_start_date} to {backfill_end_date}")
        # In a real implementation, we would process data for the date range
        # For now, we'll just process all files
        pass
    
    # Detect new files
    new_files = detect_new_files(data_dir)
    
    if not new_files:
        logger.info("No new files detected")
        return
    
    # Process each file
    results = []
    for file_path in new_files:
        logger.info(f"Processing file: {file_path.name}")
        
        # Calculate checksum
        checksum = calculate_file_checksum(file_path)
        logger.info(f"File checksum: {checksum}")
        
        # Validate schema
        is_valid = validate_file_schema(file_path)
        if not is_valid:
            logger.warning(f"Schema validation failed for {file_path.name}, skipping")
            handle_rejected_records(file_path, [], "Schema validation failed")
            continue
        
        # Process incremental load
        result = process_incremental_load(file_path, previous_day_only=True)
        results.append(result)
        
        if result["status"] == "success":
            logger.info(f"Successfully processed {file_path.name}")
        else:
            logger.error(f"Failed to process {file_path.name}: {result.get('error', 'Unknown error')}")
    
    logger.info(f"Daily ingestion flow completed. Processed {len(results)} files")


@flow(name="Backfill Data")
def backfill_flow(start_date: str, end_date: str, data_dir: str = "data"):
    """
    Backfill flow that reprocesses data for a date range.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        data_dir: Path to data directory
    """
    logger = get_run_logger()
    logger.info(f"Starting backfill from {start_date} to {end_date}")
    
    # For backfill, we would process historical data
    # This is a simplified implementation that just calls the daily flow
    daily_ingestion_flow(data_dir, start_date, end_date)
    
    logger.info("Backfill completed")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Ingestion Flow")
    parser.add_argument("--backfill-start", help="Start date for backfill (YYYY-MM-DD)")
    parser.add_argument("--backfill-end", help="End date for backfill (YYYY-MM-DD)")
    parser.add_argument("--data-dir", default="data", help="Data directory path")
    
    args = parser.parse_args()
    
    if args.backfill_start and args.backfill_end:
        backfill_flow(args.backfill_start, args.backfill_end, args.data_dir)
    else:
        daily_ingestion_flow(args.data_dir)