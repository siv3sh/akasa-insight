"""
Database models and setup using SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional

from src.config import Config
from src.utils import Logger

logger = Logger.get_logger(__name__)

Base = declarative_base()


class Customer(Base):
    """
    Customer model representing the customers table.
    """
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    mobile_number = Column(String(20), nullable=False, unique=True)
    region = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Index for faster lookups
    __table_args__ = (
        Index('idx_mobile_number', 'mobile_number'),
        Index('idx_region', 'region'),
    )
    
    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name='{self.customer_name}', mobile='{self.mobile_number}', region='{self.region}')>"


class Order(Base):
    """
    Order model representing the orders table.
    """
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    mobile_number = Column(String(20), nullable=False)
    order_date_time = Column(DateTime, nullable=False)
    sku_id = Column(String(50), nullable=False)
    sku_count = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_order_mobile', 'mobile_number'),
        Index('idx_order_date', 'order_date_time'),
        Index('idx_order_date_mobile', 'order_date_time', 'mobile_number'),
    )
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, mobile='{self.mobile_number}', date='{self.order_date_time}', amount={self.total_amount})>"


class DatabaseManager:
    """
    Database manager for handling connections and operations.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager with connection URL.
        
        Args:
            database_url: Database connection URL (defaults to Config.DATABASE_URL)
        """
        self.database_url = database_url or Config.get_database_url()
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """
        Initialize database engine and create tables.
        """
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,  # Verify connections before using them
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False           # Set to True for SQL query logging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            
            logger.info("Database connection established successfully")
        except Exception as e:
            Logger.log_error(logger, e, "Failed to initialize database connection")
            raise
    
    def create_tables(self):
        """
        Create all tables defined in the models.
        """
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            Logger.log_error(logger, e, "Failed to create database tables")
            raise
    
    def drop_tables(self):
        """
        Drop all tables (use with caution).
        """
        try:
            logger.info("Dropping all database tables...")
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            Logger.log_error(logger, e, "Failed to drop database tables")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session object
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    def close(self):
        """
        Close database connection.
        """
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def reset_database(self):
        """
        Reset database by dropping and recreating all tables.
        """
        logger.info("Resetting database...")
        self.drop_tables()
        self.create_tables()
        logger.info("Database reset complete")
