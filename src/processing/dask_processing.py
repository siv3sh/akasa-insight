"""
Dask-based KPI processing for large-scale data.
"""

import dask.dataframe as dd
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from src.config import Config
from src.utils import Logger, DataHelpers


logger = Logger.get_logger(__name__)


class DaskAnalytics:
    """
    Dask-based analytics for calculating KPIs using distributed computing.
    """

    def __init__(self):
        """
        Initialize Dask analytics.
        """
        self.df_customers = None
        self.df_orders = None

    def load_customers_from_csv(self, csv_path: str) -> dd.DataFrame:
        """
        Load customers data from CSV into Dask DataFrame.

        Args:
            csv_path: Path to customers CSV file

        Returns:
            dd.DataFrame: Customers dataframe
        """
        logger.info("Loading customers from CSV using Dask: {}".format(csv_path))

        if not Path(csv_path).exists():
            logger.error("CSV file not found: {}".format(csv_path))
            raise FileNotFoundError("CSV file not found: {}".format(csv_path))

        # Read CSV with Dask
        df = dd.read_csv(csv_path, dtype=str)

        # Clean and normalize data
        df["customer_name"] = df["customer_name"].apply(
            DataHelpers.clean_string, meta=("customer_name", "object")
        )
        df["mobile_number"] = df["mobile_number"].apply(
            DataHelpers.normalize_mobile_number, meta=("mobile_number", "object")
        )
        df["region"] = df["region"].apply(
            DataHelpers.clean_string, meta=("region", "object")
        )

        # Remove rows with missing required fields
        df = df.dropna(subset=["customer_name", "mobile_number", "region"])

        logger.info("Loaded customers from CSV using Dask")
        self.df_customers = df
        return df

    def load_orders_from_xml(self, xml_path: str) -> dd.DataFrame:
        """
        Load orders data from XML into Dask DataFrame.

        Args:
            xml_path: Path to orders XML file

        Returns:
            dd.DataFrame: Orders dataframe
        """
        logger.info("Loading orders from XML using Dask: {}".format(xml_path))

        if not Path(xml_path).exists():
            logger.error("XML file not found: {}".format(xml_path))
            raise FileNotFoundError("XML file not found: {}".format(xml_path))

        # Parse XML and convert to pandas first
        tree = ET.parse(xml_path)
        root = tree.getroot()

        orders_data = []
        for order_elem in root.findall("order"):
            order_dict = {}
            for child in order_elem:
                order_dict[child.tag] = child.text
            orders_data.append(order_dict)

        # Create pandas DataFrame first
        pandas_df = pd.DataFrame(orders_data)

        # Convert to Dask DataFrame
        df = dd.from_pandas(pandas_df, npartitions=2)

        # Clean and normalize data
        df["order_id"] = df["order_id"].apply(
            lambda x: DataHelpers.safe_int(x), meta=("order_id", "int64")
        )
        df["mobile_number"] = df["mobile_number"].apply(
            DataHelpers.normalize_mobile_number, meta=("mobile_number", "object")
        )
        df["order_date_time"] = df["order_date_time"].apply(
            DataHelpers.normalize_date, meta=("order_date_time", "datetime64[ns]")
        )
        df["sku_id"] = df["sku_id"].apply(
            DataHelpers.clean_string, meta=("sku_id", "object")
        )
        df["sku_count"] = df["sku_count"].apply(
            lambda x: DataHelpers.safe_int(x), meta=("sku_count", "int64")
        )
        df["total_amount"] = df["total_amount"].apply(
            lambda x: DataHelpers.safe_float(x), meta=("total_amount", "float64")
        )

        # Remove rows with missing required fields
        df = df.dropna(
            subset=["order_id", "mobile_number", "order_date_time", "sku_id"]
        )
        df = df[df["order_id"] != 0]

        logger.info("Loaded orders from XML using Dask")
        self.df_orders = df
        return df

    def load_data(self) -> tuple[dd.DataFrame, dd.DataFrame]:
        """
        Load both customers and orders data.

        Returns:
            tuple: (customers_df, orders_df)
        """
        logger.info("Loading all data using Dask...")
        customers_df = self.load_customers_from_csv(Config.CUSTOMERS_CSV_PATH)
        orders_df = self.load_orders_from_xml(Config.ORDERS_XML_PATH)
        return customers_df, orders_df

    def get_repeat_customers(
        self, df_customers: dd.DataFrame = None, df_orders: dd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Get customers with more than one order.

        Args:
            df_customers: Customers dataframe (optional, uses loaded data if not provided)
            df_orders: Orders dataframe (optional, uses loaded data if not provided)

        Returns:
            pd.DataFrame: Repeat customers with order count
        """
        logger.info("Calculating repeat customers using Dask...")

        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders

        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Count orders per mobile number
        order_counts = df_orders.groupby("mobile_number").size().reset_index()
        order_counts.columns = ["mobile_number", "order_count"]

        # Filter for repeat customers (more than 1 order)
        repeat_order_counts = order_counts[order_counts["order_count"] > 1]

        # Join with customer data (convert to pandas for final join)
        customers_pd = df_customers.compute()
        repeat_orders_pd = repeat_order_counts.compute()

        repeat_customers = customers_pd.merge(
            repeat_orders_pd, on="mobile_number", how="inner"
        ).sort_values("order_count", ascending=False)

        logger.info("Found {} repeat customers".format(len(repeat_customers)))
        return repeat_customers

    def get_monthly_order_trends(self, df_orders: dd.DataFrame = None) -> pd.DataFrame:
        """
        Get total number of orders per month.

        Args:
            df_orders: Orders dataframe (optional, uses loaded data if not provided)

        Returns:
            pd.DataFrame: Monthly order trends
        """
        logger.info("Calculating monthly order trends using Dask...")

        df_orders = df_orders if df_orders is not None else self.df_orders

        if df_orders is None:
            raise ValueError("Orders data not loaded. Call load_data() first.")

        # Extract year and month (convert to pandas for datetime operations)
        orders_pd = df_orders.compute()
        orders_pd["year"] = orders_pd["order_date_time"].dt.year
        orders_pd["month"] = orders_pd["order_date_time"].dt.month

        # Group by year and month
        monthly_trends = (
            orders_pd.groupby(["year", "month"])
            .agg({"order_id": "count", "total_amount": "sum"})
            .reset_index()
        )

        monthly_trends.columns = ["year", "month", "order_count", "total_revenue"]
        monthly_trends["total_revenue"] = monthly_trends["total_revenue"].round(2)
        monthly_trends = monthly_trends.sort_values(["year", "month"])

        logger.info("Found {} months with orders".format(len(monthly_trends)))
        return monthly_trends

    def get_regional_revenue(
        self, df_customers: dd.DataFrame = None, df_orders: dd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Get total revenue grouped by region.

        Args:
            df_customers: Customers dataframe (optional, uses loaded data if not provided)
            df_orders: Orders dataframe (optional, uses loaded data if not provided)

        Returns:
            pd.DataFrame: Regional revenue data
        """
        logger.info("Calculating regional revenue using Dask...")

        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders

        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Merge customers and orders (convert to pandas for join)
        customers_pd = df_customers.compute()
        orders_pd = df_orders.compute()

        merged_df = orders_pd.merge(
            customers_pd[["mobile_number", "region"]], on="mobile_number", how="inner"
        )

        # Group by region
        regional_revenue = (
            merged_df.groupby("region")
            .agg(
                {
                    "mobile_number": "nunique",
                    "order_id": "count",
                    "total_amount": ["sum", "mean"],
                }
            )
            .reset_index()
        )

        # Flatten column names
        regional_revenue.columns = [
            "region",
            "customer_count",
            "order_count",
            "total_revenue",
            "avg_order_value",
        ]
        regional_revenue["total_revenue"] = regional_revenue["total_revenue"].round(2)
        regional_revenue["avg_order_value"] = regional_revenue["avg_order_value"].round(
            2
        )
        regional_revenue = regional_revenue.sort_values(
            "total_revenue", ascending=False
        )

        logger.info("Found revenue data for {} regions".format(len(regional_revenue)))
        return regional_revenue

    def get_top_spenders(
        self,
        df_customers: dd.DataFrame = None,
        df_orders: dd.DataFrame = None,
        days: int = 30,
        limit: int = 10,
    ) -> pd.DataFrame:
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
        logger.info(
            "Calculating top {} spenders for last {} days using Dask...".format(
                limit, days
            )
        )

        df_customers = df_customers if df_customers is not None else self.df_customers
        df_orders = df_orders if df_orders is not None else self.df_orders

        if df_customers is None or df_orders is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Calculate cutoff date (convert to pandas for datetime operations)
        orders_pd = df_orders.compute()
        customers_pd = df_customers.compute()

        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter orders by date
        recent_orders = orders_pd[orders_pd["order_date_time"] >= cutoff_date].copy()

        # Group by mobile number
        spenders = (
            recent_orders.groupby("mobile_number")
            .agg(
                {
                    "order_id": "count",
                    "total_amount": ["sum", "mean"],
                    "order_date_time": "max",
                }
            )
            .reset_index()
        )

        # Flatten column names
        spenders.columns = [
            "mobile_number",
            "order_count",
            "total_spent",
            "avg_order_value",
            "last_order_date",
        ]

        # Merge with customer data
        top_spenders = customers_pd.merge(spenders, on="mobile_number", how="inner")

        # Sort and limit
        top_spenders["total_spent"] = top_spenders["total_spent"].round(2)
        top_spenders["avg_order_value"] = top_spenders["avg_order_value"].round(2)
        top_spenders["last_order_date"] = top_spenders["last_order_date"].dt.strftime(
            "%Y-%m-%d"
        )
        top_spenders = top_spenders.sort_values("total_spent", ascending=False).head(
            limit
        )

        logger.info("Found {} top spenders".format(len(top_spenders)))
        return top_spenders


# Example usage
if __name__ == "__main__":
    # This is just for testing purposes
    try:
        dask_analytics = DaskAnalytics()
        customers_df, orders_df = dask_analytics.load_data()
        print("Data loaded successfully with Dask")

        # Test repeat customers
        repeat_customers = dask_analytics.get_repeat_customers()
        print("Found {} repeat customers".format(len(repeat_customers)))

        # Test monthly trends
        monthly_trends = dask_analytics.get_monthly_order_trends()
        print("Found {} months with orders".format(len(monthly_trends)))

    except Exception as e:
        logger.error("Error in Dask processing: {}".format(str(e)))
        raise
