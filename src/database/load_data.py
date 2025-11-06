"""
Data loading module for parsing CSV/XML files and inserting into database.
"""

import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.db_setup import Customer, Order, DatabaseManager
from src.utils import Logger, DataHelpers
from src.config import Config

logger = Logger.get_logger(__name__)


class DataLoader:
    """
    Data loader for parsing and loading data from CSV and XML sources.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize data loader with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    def load_customers_from_csv(self, csv_path: str) -> int:
        """
        Load customer data from CSV file into database.
        
        Args:
            csv_path: Path to customers CSV file
            
        Returns:
            int: Number of customers successfully loaded
        """
        logger.info(f"Loading customers from CSV: {csv_path}")
        
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        session = self.db_manager.get_session()
        customers_loaded = 0
        customers_skipped = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    try:
                        # Clean and validate data
                        customer_name = DataHelpers.clean_string(row.get('customer_name'))
                        mobile_number = DataHelpers.normalize_mobile_number(row.get('mobile_number'))
                        region = DataHelpers.clean_string(row.get('region'))
                        
                        # Validate required fields
                        is_valid, missing_fields = DataHelpers.validate_required_fields(
                            {'customer_name': customer_name, 'mobile_number': mobile_number, 'region': region},
                            ['customer_name', 'mobile_number', 'region']
                        )
                        
                        if not is_valid:
                            Logger.log_data_quality_issue(
                                logger, 
                                "Missing required fields",
                                {'row': row_num, 'missing_fields': missing_fields}
                            )
                            customers_skipped += 1
                            continue
                        
                        # Create customer object
                        customer = Customer(
                            customer_name=customer_name,
                            mobile_number=mobile_number,
                            region=region
                        )
                        
                        session.add(customer)
                        customers_loaded += 1
                        
                    except IntegrityError as e:
                        session.rollback()
                        Logger.log_data_quality_issue(
                            logger,
                            "Duplicate mobile number",
                            {'row': row_num, 'mobile': row.get('mobile_number')}
                        )
                        customers_skipped += 1
                        continue
                    except Exception as e:
                        session.rollback()
                        Logger.log_error(logger, e, f"Error processing customer at row {row_num}")
                        customers_skipped += 1
                        continue
                
                # Commit all changes
                session.commit()
                logger.info(f"Customers loaded: {customers_loaded}, skipped: {customers_skipped}")
                
        except Exception as e:
            session.rollback()
            Logger.log_error(logger, e, "Failed to load customers from CSV")
            raise
        finally:
            session.close()
        
        return customers_loaded
    
    def load_orders_from_xml(self, xml_path: str) -> int:
        """
        Load order data from XML file into database.
        
        Args:
            xml_path: Path to orders XML file
            
        Returns:
            int: Number of orders successfully loaded
        """
        logger.info(f"Loading orders from XML: {xml_path}")
        
        if not Path(xml_path).exists():
            logger.error(f"XML file not found: {xml_path}")
            raise FileNotFoundError(f"XML file not found: {xml_path}")
        
        session = self.db_manager.get_session()
        orders_loaded = 0
        orders_skipped = 0
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for order_elem in root.findall('order'):
                try:
                    # Extract data from XML elements
                    order_id = DataHelpers.safe_int(order_elem.find('order_id').text if order_elem.find('order_id') is not None else None)
                    mobile_number = DataHelpers.normalize_mobile_number(
                        order_elem.find('mobile_number').text if order_elem.find('mobile_number') is not None else None
                    )
                    order_date_str = order_elem.find('order_date_time').text if order_elem.find('order_date_time') is not None else None
                    order_date_time = DataHelpers.normalize_date(order_date_str)
                    sku_id = DataHelpers.clean_string(order_elem.find('sku_id').text if order_elem.find('sku_id') is not None else None)
                    sku_count = DataHelpers.safe_int(order_elem.find('sku_count').text if order_elem.find('sku_count') is not None else None)
                    total_amount = DataHelpers.safe_float(order_elem.find('total_amount').text if order_elem.find('total_amount') is not None else None)
                    
                    # Validate required fields
                    is_valid, missing_fields = DataHelpers.validate_required_fields(
                        {
                            'order_id': order_id,
                            'mobile_number': mobile_number,
                            'order_date_time': order_date_time,
                            'sku_id': sku_id
                        },
                        ['order_id', 'mobile_number', 'order_date_time', 'sku_id']
                    )
                    
                    if not is_valid or order_id == 0:
                        Logger.log_data_quality_issue(
                            logger,
                            "Missing or invalid required fields",
                            {'order_id': order_id, 'missing_fields': missing_fields}
                        )
                        orders_skipped += 1
                        continue
                    
                    # Create order object
                    order = Order(
                        order_id=order_id,
                        mobile_number=mobile_number,
                        order_date_time=order_date_time,
                        sku_id=sku_id,
                        sku_count=sku_count,
                        total_amount=total_amount
                    )
                    
                    session.add(order)
                    orders_loaded += 1
                    
                except IntegrityError as e:
                    session.rollback()
                    Logger.log_data_quality_issue(
                        logger,
                        "Duplicate order ID",
                        {'order_id': order_id}
                    )
                    orders_skipped += 1
                    continue
                except Exception as e:
                    session.rollback()
                    Logger.log_error(logger, e, f"Error processing order {order_id}")
                    orders_skipped += 1
                    continue
            
            # Commit all changes
            session.commit()
            logger.info(f"Orders loaded: {orders_loaded}, skipped: {orders_skipped}")
            
        except Exception as e:
            session.rollback()
            Logger.log_error(logger, e, "Failed to load orders from XML")
            raise
        finally:
            session.close()
        
        return orders_loaded
    
    def load_all_data(self) -> Dict[str, int]:
        """
        Load all data from configured CSV and XML files.
        
        Returns:
            dict: Summary of loaded records
        """
        logger.info("Starting data load process...")
        
        customers_count = self.load_customers_from_csv(Config.CUSTOMERS_CSV_PATH)
        orders_count = self.load_orders_from_xml(Config.ORDERS_XML_PATH)
        
        summary = {
            'customers_loaded': customers_count,
            'orders_loaded': orders_count
        }
        
        logger.info(f"Data load complete: {summary}")
        return summary
