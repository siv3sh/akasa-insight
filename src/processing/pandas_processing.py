"""
Pandas-based in-memory KPI processing.
"""

import pandas as pd
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from src.config import Config
from src.utils import Logger, DataHelpers

logger = Logger.get_logger(__name__)


class PandasAnalytics:
    """
    Pandas-based analytics for calculating KPIs using in-memory data processing.
    """
    
    def __init__(self):
        """
        Initialize Pandas analytics.
        """
        self.df_customers = None
        self.df_orders = None
    
    def load_customers_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load customers data from CSV into pandas DataFrame.
        
        Args:
            csv_path: Path to customers CSV file
            
        Returns:
            pd.DataFrame: Customers dataframe
        """
        logger.info(f"Loading customers from CSV: {csv_path}")
        
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read CSV
        df = pd.read_csv(csv_path, dtype=str)
        
        # Clean and normalize data
        df['customer_name'] = df['customer_name'].apply(DataHelpers.clean_string)
        df['mobile_number'] = df['mobile_number'].apply(DataHelpers.normalize_mobile_number)
        df['region'] = df['region'].apply(DataHelpers.clean_string)
        
        # Remove rows with missing required fields
        initial_count = len(df)
        df = df.dropna(subset=['customer_name', 'mobile_number', 'region'])
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            logger.warning(f"Dropped {dropped_count} rows with missing required fields")
        
        logger.info(f"Loaded {len(df)} customers from CSV")
        self.df_customers = df
        return df
    
    def load_orders_from_xml(self, xml_path: str) -> pd.DataFrame:
        """
        Load orders data from XML into pandas DataFrame.
        
        Args:
            xml_path: Path to orders XML file
            
        Returns:
            pd.DataFrame: Orders dataframe
        """
        logger.info(f"Loading orders from XML: {xml_path}")
        
        if not Path(xml_path).exists():
            logger.error(f"XML file not found: {xml_path}")
            raise FileNotFoundError(f"XML file not found: {xml_path}")
        
        # Parse XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        orders_data = []
        for order_elem in root.findall('order'):
            order_dict = {}
            for child in order_elem:
                order_dict[child.tag] = child.text
            orders_data.append(order_dict)
        
        # Create DataFrame
        df = pd.DataFrame(orders_data)
        
        # Clean and normalize data
        df['order_id'] = df['order_id'].apply(lambda x: DataHelpers.safe_int(x))
        df['mobile_number'] = df['mobile_number'].apply(DataHelpers.normalize_mobile_number)
        df['order_date_time'] = df['order_date_time'].apply(DataHelpers.normalize_date)
        df['sku_id'] = df['sku_id'].apply(DataHelpers.clean_string)
        df['sku_count'] = df['sku_count'].apply(lambda x: DataHelpers.safe_int(x))
        df['total_amount'] = df['total_amount'].apply(lambda x: DataHelpers.safe_float(x))
        
        # Remove rows with missing required fields
        initial_count = len(df)
        df = df.dropna(subset=['order_id', 'mobile_number', 'order_date_time', 'sku_id'])
        df = df[df['order_id'] != 0]
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            logger.warning(f"Dropped {dropped_count} rows with missing required fields")
        
        logger.info(f"Loaded {len(df)} orders from XML")
        self.df_orders = df
        return df
    
    def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load both customers and orders data.
        
        Returns:
            tuple: (customers_df, orders_df)
        """
        logger.info("Loading all data using Pandas...")
        customers_df = self.load_customers_from_csv(Config.CUSTOMERS_CSV_PATH)
        orders_df = self.load_orders_from_xml(Config.ORDERS_XML_PATH)
        return customers_df, orders_df
    
    def get_repeat_customers(self, df_customers: pd.DataFrame = None, df_orders: pd.DataFrame = None) -> pd.DataFrame:
        """
        Get customers with more than one order.
        
        Args:
            df_customers: Customers dataframe (optional, uses loaded data if not provided)
            df_orders: Orders dataframe (optional, uses loaded data if not provided)
            
        Returns:
            pd.DataFrame: Repeat customers with order count
        """
        logger.info("Calculating repeat customers using Pandas...")
        
        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders
        
        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Count orders per mobile number
        order_counts = df_orders.groupby('mobile_number').size().reset_index(name='order_count')
        
        # Filter for repeat customers (more than 1 order)
        repeat_order_counts = order_counts[order_counts['order_count'] > 1]
        
        # Join with customer data
        repeat_customers = df_customers.merge(
            repeat_order_counts,
            on='mobile_number',
            how='inner'
        ).sort_values('order_count', ascending=False)
        
        logger.info(f"Found {len(repeat_customers)} repeat customers")
        return repeat_customers
    
    def get_monthly_order_trends(self, df_orders: pd.DataFrame = None) -> pd.DataFrame:
        """
        Get total number of orders per month.
        
        Args:
            df_orders: Orders dataframe (optional, uses loaded data if not provided)
            
        Returns:
            pd.DataFrame: Monthly order trends
        """
        logger.info("Calculating monthly order trends using Pandas...")
        
        df_orders = df_orders if df_orders is not None else self.df_orders
        
        if df_orders is None:
            raise ValueError("Orders data not loaded. Call load_data() first.")
        
        # Extract year and month
        df_orders_copy = df_orders.copy()
        df_orders_copy['year'] = df_orders_copy['order_date_time'].dt.year
        df_orders_copy['month'] = df_orders_copy['order_date_time'].dt.month
        
        # Group by year and month
        monthly_trends = df_orders_copy.groupby(['year', 'month']).agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        
        monthly_trends.columns = ['year', 'month', 'order_count', 'total_revenue']
        monthly_trends['total_revenue'] = monthly_trends['total_revenue'].round(2)
        monthly_trends = monthly_trends.sort_values(['year', 'month'])
        
        logger.info(f"Found {len(monthly_trends)} months with orders")
        return monthly_trends
    
    def get_regional_revenue(self, df_customers: pd.DataFrame = None, df_orders: pd.DataFrame = None) -> pd.DataFrame:
        """
        Get total revenue grouped by region.
        
        Args:
            df_customers: Customers dataframe (optional, uses loaded data if not provided)
            df_orders: Orders dataframe (optional, uses loaded data if not provided)
            
        Returns:
            pd.DataFrame: Regional revenue data
        """
        logger.info("Calculating regional revenue using Pandas...")
        
        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders
        
        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Merge customers and orders
        merged_df = df_orders.merge(
            df_customers[['mobile_number', 'region']],
            on='mobile_number',
            how='inner'
        )
        
        # Group by region
        regional_revenue = merged_df.groupby('region').agg({
            'mobile_number': 'nunique',
            'order_id': 'count',
            'total_amount': ['sum', 'mean']
        }).reset_index()
        
        # Flatten column names
        regional_revenue.columns = ['region', 'customer_count', 'order_count', 'total_revenue', 'avg_order_value']
        regional_revenue['total_revenue'] = regional_revenue['total_revenue'].round(2)
        regional_revenue['avg_order_value'] = regional_revenue['avg_order_value'].round(2)
        regional_revenue = regional_revenue.sort_values('total_revenue', ascending=False)
        
        logger.info(f"Found revenue data for {len(regional_revenue)} regions")
        return regional_revenue
    
    def get_top_spenders(self, df_customers: pd.DataFrame = None, df_orders: pd.DataFrame = None, days: int = 30, limit: int = 10) -> pd.DataFrame:
        """
        Get top customers by spend in the last N days.
        
        Args:
            df_customers: Customers dataframe (optional, uses loaded data if not provided)
            df_orders: Orders dataframe (optional, uses loaded data if not provided)
            days: Number of days to look back (default: 30)
            limit: Number of top customers to return (default: 10)
            
        Returns:
            pd.DataFrame: Top spending customers
        """
        logger.info(f"Calculating top {limit} spenders for last {days} days using Pandas...")
        
        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders
        
        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter orders by date
        recent_orders = df_orders[df_orders['order_date_time'] >= cutoff_date].copy()
        
        # Group by mobile number
        spenders = recent_orders.groupby('mobile_number').agg({
            'order_id': 'count',
            'total_amount': ['sum', 'mean'],
            'order_date_time': 'max'
        }).reset_index()
        
        # Flatten column names
        spenders.columns = ['mobile_number', 'order_count', 'total_spent', 'avg_order_value', 'last_order_date']
        
        # Merge with customer data
        top_spenders = df_customers.merge(
            spenders,
            on='mobile_number',
            how='inner'
        )
        
        # Sort and limit
        top_spenders['total_spent'] = top_spenders['total_spent'].round(2)
        top_spenders['avg_order_value'] = top_spenders['avg_order_value'].round(2)
        top_spenders['last_order_date'] = top_spenders['last_order_date'].dt.strftime('%Y-%m-%d')
        top_spenders = top_spenders.sort_values('total_spent', ascending=False).head(limit)
        
        logger.info(f"Found {len(top_spenders)} top spenders")
        return top_spenders
    
    def get_all_kpis(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate all KPIs and return as a dictionary.
        
        Returns:
            dict: All KPI results as DataFrames
        """
        logger.info("Calculating all KPIs using Pandas...")
        
        return {
            'repeat_customers': self.get_repeat_customers(),
            'monthly_order_trends': self.get_monthly_order_trends(),
            'regional_revenue': self.get_regional_revenue(),
            'top_spenders_30_days': self.get_top_spenders(days=30, limit=10)
        }
