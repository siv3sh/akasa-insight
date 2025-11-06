"""
Main entry point for the Akasa Air Data Engineering Task.
Orchestrates both SQL-based and Pandas-based analytics approaches.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Optional
from tabulate import tabulate

from src.config import Config
from src.database import DatabaseManager, DataLoader
from src.processing import SQLAnalytics, PandasAnalytics
from src.utils import Logger

# Initialize logger
logger = Logger.get_logger(__name__)


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def display_results(title: str, data: Any, headers: Optional[list] = None):
    """
    Display results in a formatted table.
    
    Args:
        title: Title of the results
        data: List of dictionaries, DataFrame, or other tabular data
        headers: Optional list of headers
    """
    print(f"\n{title}")
    print("-" * len(title))
    
    # Check if data is empty
    if data is None:
        print("No data available.")
        return
        
    # Check if it's a DataFrame
    if hasattr(data, 'empty') and data.empty:
        print("No data available.")
        return
        
    # Check if it's a list or similar sequence
    if hasattr(data, '__len__') and len(data) == 0:
        print("No data available.")
        return
    
    # Convert list of dicts to list of lists for tabulate
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        if not headers:
            headers = list(data[0].keys())
        rows = [[row.get(h, '') for h in headers] for row in data]
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    else:
        # Handle DataFrame or other tabular data
        print(tabulate(data, headers='keys', tablefmt='grid'))
    print()


def save_results_to_file(filename: str, data: Any, format: str = 'json'):
    """
    Save results to a file.
    
    Args:
        filename: Name of the output file
        data: Data to save
        format: Format to save (json or csv)
    """
    output_dir = Path(Config.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    
    try:
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Results saved to {output_path}")
        elif format == 'csv':
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                data.to_csv(output_path, index=False)
            else:
                pd.DataFrame(data).to_csv(output_path, index=False)
            logger.info(f"Results saved to {output_path}")
    except Exception as e:
        Logger.log_error(logger, e, f"Failed to save results to {output_path}")


def run_sql_approach():
    """
    Run SQL-based analytics approach.
    """
    print_separator("SQL-BASED ANALYTICS APPROACH")
    
    db_manager = None
    try:
        # Initialize database
        logger.info("Initializing database connection...")
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Reset database (drop and recreate tables)
        logger.info("Resetting database tables...")
        db_manager.reset_database()
        
        # Load data into database
        logger.info("Loading data into database...")
        data_loader = DataLoader(db_manager)
        load_summary = data_loader.load_all_data()
        
        print("Data Load Summary:")
        print(f"  - Customers loaded: {load_summary['customers_loaded']}")
        print(f"  - Orders loaded: {load_summary['orders_loaded']}")
        
        # Calculate KPIs
        logger.info("Calculating KPIs using SQL...")
        sql_analytics = SQLAnalytics(db_manager)
        
        # 1. Repeat Customers
        print_separator("KPI 1: Repeat Customers")
        repeat_customers = sql_analytics.get_repeat_customers()
        display_results("Repeat Customers (SQL)", repeat_customers)
        save_results_to_file('sql_repeat_customers.json', repeat_customers)
        
        # 2. Monthly Order Trends
        print_separator("KPI 2: Monthly Order Trends")
        monthly_trends = sql_analytics.get_monthly_order_trends()
        display_results("Monthly Order Trends (SQL)", monthly_trends)
        save_results_to_file('sql_monthly_trends.json', monthly_trends)
        
        # 3. Regional Revenue
        print_separator("KPI 3: Regional Revenue")
        regional_revenue = sql_analytics.get_regional_revenue()
        display_results("Regional Revenue (SQL)", regional_revenue)
        save_results_to_file('sql_regional_revenue.json', regional_revenue)
        
        # 4. Top Spenders (Last 30 Days)
        print_separator("KPI 4: Top 10 Spenders (Last 30 Days)")
        top_spenders = sql_analytics.get_top_spenders(days=30, limit=10)
        display_results("Top Spenders - Last 30 Days (SQL)", top_spenders)
        save_results_to_file('sql_top_spenders.json', top_spenders)
        
        logger.info("SQL-based analytics completed successfully")
        
    except Exception as e:
        Logger.log_error(logger, e, "Error in SQL-based approach")
        raise
    finally:
        if db_manager:
            db_manager.close()


def run_pandas_approach():
    """
    Run Pandas-based in-memory analytics approach.
    """
    print_separator("PANDAS IN-MEMORY ANALYTICS APPROACH")
    
    try:
        # Initialize Pandas analytics
        pandas_analytics = PandasAnalytics()
        
        # Load data
        logger.info("Loading data into memory using Pandas...")
        df_customers, df_orders = pandas_analytics.load_data()
        
        print("Data Load Summary:")
        print(f"  - Customers loaded: {len(df_customers)}")
        print(f"  - Orders loaded: {len(df_orders)}")
        
        # Calculate KPIs
        logger.info("Calculating KPIs using Pandas...")
        
        # 1. Repeat Customers
        print_separator("KPI 1: Repeat Customers")
        repeat_customers = pandas_analytics.get_repeat_customers()
        display_results("Repeat Customers (Pandas)", repeat_customers)
        save_results_to_file('pandas_repeat_customers.csv', repeat_customers, format='csv')
        
        # 2. Monthly Order Trends
        print_separator("KPI 2: Monthly Order Trends")
        monthly_trends = pandas_analytics.get_monthly_order_trends()
        display_results("Monthly Order Trends (Pandas)", monthly_trends)
        save_results_to_file('pandas_monthly_trends.csv', monthly_trends, format='csv')
        
        # 3. Regional Revenue
        print_separator("KPI 3: Regional Revenue")
        regional_revenue = pandas_analytics.get_regional_revenue()
        display_results("Regional Revenue (Pandas)", regional_revenue)
        save_results_to_file('pandas_regional_revenue.csv', regional_revenue, format='csv')
        
        # 4. Top Spenders (Last 30 Days)
        print_separator("KPI 4: Top 10 Spenders (Last 30 Days)")
        top_spenders = pandas_analytics.get_top_spenders(days=30, limit=10)
        display_results("Top Spenders - Last 30 Days (Pandas)", top_spenders)
        save_results_to_file('pandas_top_spenders.csv', top_spenders, format='csv')
        
        logger.info("Pandas-based analytics completed successfully")
        
    except Exception as e:
        Logger.log_error(logger, e, "Error in Pandas-based approach")
        raise


def run_dask_approach():
    """
    Run Dask-based distributed analytics approach.
    """
    print_separator("DASK DISTRIBUTED ANALYTICS APPROACH")
    
    try:
        # Import Dask analytics (only when needed)
        from src.processing.dask_processing import DaskAnalytics
        
        # Initialize Dask analytics
        dask_analytics = DaskAnalytics()
        
        # Load data
        logger.info("Loading data into memory using Dask...")
        df_customers, df_orders = dask_analytics.load_data()
        
        print("Data Load Summary:")
        print(f"  - Customers loaded: {len(df_customers.compute())}")
        print(f"  - Orders loaded: {len(df_orders.compute())}")
        
        # Calculate KPIs
        logger.info("Calculating KPIs using Dask...")
        
        # 1. Repeat Customers
        print_separator("KPI 1: Repeat Customers")
        repeat_customers = dask_analytics.get_repeat_customers()
        display_results("Repeat Customers (Dask)", repeat_customers)
        save_results_to_file('dask_repeat_customers.csv', repeat_customers, format='csv')
        
        # 2. Monthly Order Trends
        print_separator("KPI 2: Monthly Order Trends")
        monthly_trends = dask_analytics.get_monthly_order_trends()
        display_results("Monthly Order Trends (Dask)", monthly_trends)
        save_results_to_file('dask_monthly_trends.csv', monthly_trends, format='csv')
        
        # 3. Regional Revenue
        print_separator("KPI 3: Regional Revenue")
        regional_revenue = dask_analytics.get_regional_revenue()
        display_results("Regional Revenue (Dask)", regional_revenue)
        save_results_to_file('dask_regional_revenue.csv', regional_revenue, format='csv')
        
        # 4. Top Spenders (Last 30 Days)
        print_separator("KPI 4: Top 10 Spenders (Last 30 Days)")
        top_spenders = dask_analytics.get_top_spenders(days=30, limit=10)
        display_results("Top Spenders - Last 30 Days (Dask)", top_spenders)
        save_results_to_file('dask_top_spenders.csv', top_spenders, format='csv')
        
        logger.info("Dask-based analytics completed successfully")
        
    except ImportError:
        logger.error("Dask is not installed or not available. Please install it with: pip install dask[dataframe]")
        raise
    except Exception as e:
        Logger.log_error(logger, e, "Error in Dask-based approach")
        raise


def main(engine: str = 'pandas'):
    """
    Main execution function.
    
    Args:
        engine: Processing engine to use ('pandas', 'dask', or 'both')
    """
    print_separator("AKASA AIR - DATA ENGINEERING TASK")
    print("Processing customer and order data using both SQL and Pandas approaches...\n")
    
    try:
        # Validate configuration
        if not Config.validate_config():
            logger.error("Configuration validation failed. Please check your .env file.")
            sys.exit(1)
        
        # Run SQL-based approach
        run_sql_approach()
        
        # Run in-memory approach based on engine selection
        if engine == 'pandas':
            run_pandas_approach()
        elif engine == 'dask':
            run_dask_approach()
        elif engine == 'both':
            run_pandas_approach()
            run_dask_approach()
        else:
            logger.warning(f"Unknown engine '{engine}', defaulting to pandas")
            run_pandas_approach()
        
        print_separator("ANALYSIS COMPLETE")
        print("All KPIs have been calculated using both approaches.")
        print(f"Results saved to: {Config.OUTPUT_DIR}")
        print("\nThank you for using Akasa Air Data Engineering Solution!")
        
    except KeyboardInterrupt:
        logger.warning("\nExecution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Akasa Air Data Engineering Task")
    parser.add_argument(
        '--engine', 
        choices=['pandas', 'dask', 'both'], 
        default='pandas',
        help='Processing engine to use (default: pandas)'
    )
    
    args = parser.parse_args()
    main(engine=args.engine)