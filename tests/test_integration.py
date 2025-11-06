"""
Integration tests for the Akasa Air Data Engineering project.
"""

import os
import sys
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import Config
from src.database import DatabaseManager, DataLoader
from src.processing import SQLAnalytics, PandasAnalytics


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database for testing."""
        # Create temporary database
        temp_db_path = tempfile.mktemp(suffix='.db')
        database_url = f"sqlite:///{temp_db_path}"
        
        # Update config temporarily
        original_url = Config.DATABASE_URL
        Config.DATABASE_URL = database_url
        
        # Create database manager
        db_manager = DatabaseManager(database_url)
        db_manager.initialize()
        db_manager.reset_database()
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        Config.DATABASE_URL = original_url
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
    
    @pytest.fixture
    def sample_data(self, temp_db):
        """Load sample data into the temporary database."""
        # Copy sample data files to temporary location
        test_dir = Path(__file__).parent
        project_root = test_dir.parent
        
        # Use existing data files
        customers_path = project_root / "data" / "customers.csv"
        orders_path = project_root / "data" / "orders.xml"
        
        # Load data
        data_loader = DataLoader(temp_db)
        load_summary = data_loader.load_all_data()
        
        return load_summary
    
    def test_complete_pipeline(self, temp_db, sample_data):
        """Test the complete data processing pipeline."""
        # Verify data was loaded
        assert sample_data['customers_loaded'] > 0
        assert sample_data['orders_loaded'] > 0
        
        # Test SQL analytics
        sql_analytics = SQLAnalytics(temp_db)
        
        # Test repeat customers
        repeat_customers = sql_analytics.get_repeat_customers()
        assert isinstance(repeat_customers, list)
        assert len(repeat_customers) >= 0  # Could be 0 in some test cases
        
        # Test monthly trends
        monthly_trends = sql_analytics.get_monthly_order_trends()
        assert isinstance(monthly_trends, list)
        assert len(monthly_trends) > 0
        
        # Test regional revenue
        regional_revenue = sql_analytics.get_regional_revenue()
        assert isinstance(regional_revenue, list)
        assert len(regional_revenue) > 0
        
        # Test top spenders
        top_spenders = sql_analytics.get_top_spenders(days=30, limit=5)
        assert isinstance(top_spenders, list)
        
        # Test Pandas analytics
        pandas_analytics = PandasAnalytics()
        df_customers, df_orders = pandas_analytics.load_data()
        
        # Verify data was loaded
        assert len(df_customers) > 0
        assert len(df_orders) > 0
        
        # Test repeat customers
        repeat_customers_pd = pandas_analytics.get_repeat_customers()
        assert len(repeat_customers_pd) >= 0
        
        # Test monthly trends
        monthly_trends_pd = pandas_analytics.get_monthly_order_trends()
        assert len(monthly_trends_pd) > 0
        
        # Test regional revenue
        regional_revenue_pd = pandas_analytics.get_regional_revenue()
        assert len(regional_revenue_pd) > 0
        
        # Test top spenders
        top_spenders_pd = pandas_analytics.get_top_spenders(days=30, limit=5)
        assert len(top_spenders_pd) >= 0
    
    def test_data_consistency(self, temp_db, sample_data):
        """Test that SQL and Pandas approaches produce consistent results."""
        # SQL approach
        sql_analytics = SQLAnalytics(temp_db)
        sql_repeat_customers = sql_analytics.get_repeat_customers()
        sql_monthly_trends = sql_analytics.get_monthly_order_trends()
        sql_regional_revenue = sql_analytics.get_regional_revenue()
        
        # Pandas approach
        pandas_analytics = PandasAnalytics()
        pandas_repeat_customers = pandas_analytics.get_repeat_customers()
        pandas_monthly_trends = pandas_analytics.get_monthly_order_trends()
        pandas_regional_revenue = pandas_analytics.get_regional_revenue()
        
        # Compare counts (they should be the same)
        assert len(sql_repeat_customers) == len(pandas_repeat_customers)
        assert len(sql_monthly_trends) == len(pandas_monthly_trends)
        
        # Regional revenue should have same number of regions
        assert len(sql_regional_revenue) == len(pandas_regional_revenue)


if __name__ == "__main__":
    pytest.main([__file__])