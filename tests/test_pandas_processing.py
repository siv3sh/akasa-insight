"""
Unit tests for pandas processing module.
"""

import pandas as pd
import pytest
from datetime import datetime
from src.processing.pandas_processing import PandasAnalytics
from src.utils.helpers import DataHelpers


class TestDataHelpers:
    """Test data helper functions."""
    
    def test_clean_string(self):
        """Test string cleaning function."""
        assert DataHelpers.clean_string("  Hello World  ") == "Hello World"
        assert DataHelpers.clean_string(None) == ""
        assert DataHelpers.clean_string("") == ""
    
    def test_normalize_mobile_number(self):
        """Test mobile number normalization."""
        assert DataHelpers.normalize_mobile_number("9876543210") == "9876543210"
        assert DataHelpers.normalize_mobile_number(" 9876543210 ") == "9876543210"
        assert DataHelpers.normalize_mobile_number(None) == ""
    
    def test_normalize_date(self):
        """Test date normalization."""
        # Test standard format
        result = DataHelpers.normalize_date("2024-10-15 10:30:00")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2024
        assert result.month == 10
        assert result.day == 15
        
        # Test None value
        assert DataHelpers.normalize_date(None) is None
    
    def test_safe_int(self):
        """Test safe integer conversion."""
        assert DataHelpers.safe_int("123") == 123
        assert DataHelpers.safe_int("") == 0
        assert DataHelpers.safe_int(None) == 0
        assert DataHelpers.safe_int("abc") == 0
    
    def test_safe_float(self):
        """Test safe float conversion."""
        assert DataHelpers.safe_float("123.45") == 123.45
        assert DataHelpers.safe_float("") == 0.0
        assert DataHelpers.safe_float(None) == 0.0
        assert DataHelpers.safe_float("abc") == 0.0


class TestPandasAnalytics:
    """Test pandas analytics functions."""
    
    @pytest.fixture
    def sample_customers_df(self):
        """Create sample customers DataFrame."""
        return pd.DataFrame({
            'customer_id': [1, 2, 3, 4],
            'customer_name': ['Amit Sharma', 'Priya Patel', 'Rahul Kumar', 'Sneha Reddy'],
            'mobile_number': ['9876543210', '9876543211', '9876543212', '9876543213'],
            'region': ['North', 'West', 'South', 'South']
        })
    
    @pytest.fixture
    def sample_orders_df(self):
        """Create sample orders DataFrame."""
        return pd.DataFrame({
            'order_id': [1001, 1002, 1003, 1004, 1005],
            'mobile_number': ['9876543210', '9876543211', '9876543210', '9876543212', '9876543211'],
            'order_date_time': [
                pd.Timestamp('2024-10-15 10:30:00'),
                pd.Timestamp('2024-10-16 14:20:00'),
                pd.Timestamp('2024-10-20 09:15:00'),
                pd.Timestamp('2024-10-22 16:45:00'),
                pd.Timestamp('2024-10-25 11:30:00')
            ],
            'sku_id': ['SKU001', 'SKU002', 'SKU003', 'SKU001', 'SKU004'],
            'sku_count': [2, 1, 3, 1, 2],
            'total_amount': [5500.00, 3200.50, 8750.00, 2750.00, 4500.00]
        })
    
    def test_get_repeat_customers(self, sample_customers_df, sample_orders_df):
        """Test repeat customers calculation."""
        analytics = PandasAnalytics()
        analytics.df_customers = sample_customers_df
        analytics.df_orders = sample_orders_df
        
        result = analytics.get_repeat_customers()
        
        # Amit Sharma and Priya Patel should be repeat customers (2 orders each)
        assert len(result) == 2
        assert set(result['mobile_number'].values) == {'9876543210', '9876543211'}
        assert all(result['order_count'] == 2)
    
    def test_get_monthly_order_trends(self, sample_orders_df):
        """Test monthly order trends calculation."""
        analytics = PandasAnalytics()
        analytics.df_orders = sample_orders_df
        
        result = analytics.get_monthly_order_trends()
        
        # All orders are in October 2024
        assert len(result) == 1
        assert result.iloc[0]['year'] == 2024
        assert result.iloc[0]['month'] == 10
        assert result.iloc[0]['order_count'] == 5
        assert result.iloc[0]['total_revenue'] == 24700.50
    
    def test_get_regional_revenue(self, sample_customers_df, sample_orders_df):
        """Test regional revenue calculation."""
        analytics = PandasAnalytics()
        analytics.df_customers = sample_customers_df
        analytics.df_orders = sample_orders_df
        
        result = analytics.get_regional_revenue()
        
        # Should have 3 regions: North, West, South
        assert len(result) == 3
        # North: 1 customer, 2 orders (Amit Sharma)
        # West: 1 customer, 2 orders (Priya Patel)
        # South: 2 customers, 1 order (Rahul Kumar)
        
        north_data = result[result['region'] == 'North']
        assert len(north_data) == 1
        assert north_data.iloc[0]['customer_count'] == 1
        assert north_data.iloc[0]['order_count'] == 2
        
        west_data = result[result['region'] == 'West']
        assert len(west_data) == 1
        assert west_data.iloc[0]['customer_count'] == 1
        assert west_data.iloc[0]['order_count'] == 2
        
        south_data = result[result['region'] == 'South']
        assert len(south_data) == 1
        assert south_data.iloc[0]['customer_count'] == 2
        assert south_data.iloc[0]['order_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__])