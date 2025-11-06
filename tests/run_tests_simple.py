#!/usr/bin/env python3
"""
Simple test runner to verify functionality without pytest dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_pandas_processing():
    """Test pandas processing module."""
    print("Testing pandas processing...")

    import pandas as pd

    from src.processing.pandas_processing import PandasAnalytics

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

    # Test repeat customers
    repeat_customers = analytics.get_repeat_customers()
    assert len(repeat_customers) == 2, f"Expected 2 repeat customers, got {len(repeat_customers)}"

    # Test monthly trends
    monthly_trends = analytics.get_monthly_order_trends()
    assert len(monthly_trends) == 1, f"Expected 1 month, got {len(monthly_trends)}"
    assert monthly_trends.iloc[0]['year'] == 2024
    assert monthly_trends.iloc[0]['month'] == 10
    assert monthly_trends.iloc[0]['order_count'] == 5
    assert monthly_trends.iloc[0]['total_revenue'] == 24700.50

    # Test regional revenue
    regional_revenue = analytics.get_regional_revenue()
    assert len(regional_revenue) == 3, f"Expected 3 regions, got {len(regional_revenue)}"

    print("✓ Pandas processing tests passed!")

def test_data_helpers():
    """Test data helper functions."""
    print("Testing data helpers...")

    import pandas as pd

    from src.utils.helpers import DataHelpers

    # Test clean_string
    assert DataHelpers.clean_string("  Hello World  ") == "Hello World"
    assert DataHelpers.clean_string(None) == ""
    assert DataHelpers.clean_string("") == ""

    # Test normalize_mobile_number
    assert DataHelpers.normalize_mobile_number("9876543210") == "9876543210"
    assert DataHelpers.normalize_mobile_number(" 9876543210 ") == "9876543210"
    assert DataHelpers.normalize_mobile_number(None) == ""

    # Test normalize_date
    result = DataHelpers.normalize_date("2024-10-15 10:30:00")
    assert isinstance(result, pd.Timestamp)
    assert result.year == 2024
    assert result.month == 10
    assert result.day == 15
    assert DataHelpers.normalize_date(None) is None

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

def main():
    """Run all tests."""
    print("Running simple verification tests...\n")

    try:
        test_data_helpers()
        test_pandas_processing()
        print("\n🎉 All tests passed! CI pipeline fixes are working correctly.")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
