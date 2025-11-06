#!/usr/bin/env python3
"""
Test script to verify that our CI pipeline fixes work correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_pandas_processing():
    """Test pandas processing module."""
    print("Testing pandas processing...")
    
    import pandas as pd
    from src.processing.pandas_processing import PandasAnalytics
    from src.utils.helpers import DataHelpers
    
    # Create sample data
    sample_customers_df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4],
        'customer_name': ['Amit Sharma', 'Priya Patel', 'Rahul Kumar', 'Sneha Reddy'],
        'mobile_number': ['9876543210', '9876543211', '9876543212', '9876543213'],
        'region': ['North', 'West', 'South', 'South']
    })
    
    sample_orders_df = pd.DataFrame({
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
    
    # Test analytics
    analytics = PandasAnalytics()
    analytics.df_customers = sample_customers_df
    analytics.df_orders = sample_orders_df
    
    # Test regional revenue
    result = analytics.get_regional_revenue()
    
    # Verify results
    assert len(result) == 3, f"Expected 3 regions, got {len(result)}"
    
    # North: 1 customer, 2 orders
    north_data = result[result['region'] == 'North']
    assert len(north_data) == 1, "Expected 1 North region entry"
    assert north_data.iloc[0]['customer_count'] == 1, "Expected 1 customer in North"
    assert north_data.iloc[0]['order_count'] == 2, "Expected 2 orders in North"
    
    # West: 1 customer, 2 orders
    west_data = result[result['region'] == 'West']
    assert len(west_data) == 1, "Expected 1 West region entry"
    assert west_data.iloc[0]['customer_count'] == 1, "Expected 1 customer in West"
    assert west_data.iloc[0]['order_count'] == 2, "Expected 2 orders in West"
    
    # South: 1 customer, 1 order (Sneha Reddy has no orders, so excluded)
    south_data = result[result['region'] == 'South']
    assert len(south_data) == 1, "Expected 1 South region entry"
    assert south_data.iloc[0]['customer_count'] == 1, "Expected 1 customer in South"
    assert south_data.iloc[0]['order_count'] == 1, "Expected 1 order in South"
    
    print("✓ Pandas processing tests passed!")
    return True

def test_data_helpers():
    """Test data helper functions."""
    print("Testing data helpers...")
    
    from src.utils.helpers import DataHelpers
    
    # Test clean_string
    assert DataHelpers.clean_string("  Hello World  ") == "Hello World"
    assert DataHelpers.clean_string(None) == ""
    assert DataHelpers.clean_string("") == ""
    
    # Test normalize_mobile_number
    assert DataHelpers.normalize_mobile_number("9876543210") == "9876543210"
    assert DataHelpers.normalize_mobile_number(" 9876543210 ") == "9876543210"
    assert DataHelpers.normalize_mobile_number(None) == ""
    
    # Test safe_int
    assert DataHelpers.safe_int("123") == 123
    assert DataHelpers.safe_int("") == 0
    assert DataHelpers.safe_int(None) == 0
    assert DataHelpers.safe_int("abc") == 0
    
    # Test safe_float
    assert DataHelpers.safe_float("123.45") == 123.45
    assert DataHelpers.safe_float("") == 0.0
    assert DataHelpers.safe_float(None) == 0.0
    assert DataHelpers.safe_float("abc") == 0.0
    
    print("✓ Data helper tests passed!")
    return True

if __name__ == "__main__":
    print("Running CI pipeline fix verification tests...\n")
    
    try:
        test_data_helpers()
        test_pandas_processing()
        print("\n🎉 All tests passed! CI pipeline fixes are working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)