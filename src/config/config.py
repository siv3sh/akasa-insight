"""
Configuration module for managing environment variables and database connections.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Try to import Streamlit secrets if running in Streamlit
try:
    import streamlit as st
    STREAMLIT_SECRETS = st.secrets
except ImportError:
    STREAMLIT_SECRETS = {}


class Config:
    """
    Configuration class to manage application settings.
    """
    
    # Database Configuration
    DB_HOST = STREAMLIT_SECRETS.get('mysql', {}).get('host') or os.getenv('DB_HOST', 'localhost')
    DB_PORT = STREAMLIT_SECRETS.get('mysql', {}).get('port') or os.getenv('DB_PORT', '3306')
    DB_USER = STREAMLIT_SECRETS.get('mysql', {}).get('user') or os.getenv('DB_USER', 'root')
    DB_PASSWORD = STREAMLIT_SECRETS.get('mysql', {}).get('password') or os.getenv('DB_PASSWORD', '')
    DB_NAME = STREAMLIT_SECRETS.get('mysql', {}).get('database') or os.getenv('DB_NAME', 'akasa_air_db')
    
    # Construct database URL for SQLAlchemy
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Data Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    CUSTOMERS_CSV_PATH = os.getenv('CUSTOMERS_CSV_PATH', str(BASE_DIR / 'data' / 'customers.csv'))
    ORDERS_XML_PATH = os.getenv('ORDERS_XML_PATH', str(BASE_DIR / 'data' / 'orders.xml'))
    
    # Output Directory
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', str(BASE_DIR / 'outputs'))
    
    @classmethod
    def validate_config(cls):
        """
        Validate that all required configuration values are present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = ['DB_HOST', 'DB_USER', 'DB_NAME']
        for field in required_fields:
            if not getattr(cls, field):
                return False
        return True
    
    @classmethod
    def get_database_url(cls):
        """
        Get the database connection URL.
        
        Returns:
            str: Database connection URL
        """
        return cls.DATABASE_URL