"""
Database migrations for performance optimization.
"""

from sqlalchemy import text
from src.database import DatabaseManager
from src.utils import Logger

logger = Logger.get_logger(__name__)


class DatabaseMigrations:
    """
    Database migrations for performance optimization and indexing.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    def apply_indexes(self):
        """
        Apply performance indexes to database tables.
        """
        session = self.db_manager.get_session()
        try:
            logger.info("Applying database indexes for performance optimization...")
            
            # Create indexes on customers table (MySQL syntax)
            indexes_customers = [
                "CREATE INDEX idx_customers_mobile ON customers(mobile_number)",
                "CREATE INDEX idx_customers_region ON customers(region)"
            ]
            
            # Create indexes on orders table (MySQL syntax)
            indexes_orders = [
                "CREATE INDEX idx_orders_mobile ON orders(mobile_number)",
                "CREATE INDEX idx_orders_date ON orders(order_date_time)",
                "CREATE INDEX idx_orders_date_mobile ON orders(order_date_time, mobile_number)"
            ]
            
            # Check if indexes exist before creating them
            existing_indexes_query = """
                SELECT index_name 
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name IN ('customers', 'orders')
            """
            
            result = session.execute(text(existing_indexes_query))
            existing_indexes = [row[0] for row in result.fetchall()]
            
            # Execute index creation statements only if they don't exist
            for statement in indexes_customers + indexes_orders:
                # Extract index name from statement (simplified approach)
                index_name = statement.split()[2]  # Gets the index name from CREATE INDEX statement
                if index_name not in existing_indexes:
                    try:
                        session.execute(text(statement))
                        logger.info(f"Created index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Could not create index {index_name}: {str(e)}")
                else:
                    logger.info(f"Index {index_name} already exists, skipping")
            
            session.commit()
            logger.info("Database indexes applied successfully")
            
        except Exception as e:
            session.rollback()
            Logger.log_error(logger, e, "Failed to apply database indexes")
            raise
        finally:
            session.close()
    
    def optimize_tables(self):
        """
        Apply table optimization techniques.
        """
        session = self.db_manager.get_session()
        try:
            logger.info("Optimizing database tables...")
            
            # Optimize tables (MySQL specific)
            optimization_queries = [
                "OPTIMIZE TABLE customers",
                "OPTIMIZE TABLE orders"
            ]
            
            for query in optimization_queries:
                try:
                    session.execute(text(query))
                except Exception as e:
                    logger.warning(f"Could not optimize table with query '{query}': {str(e)}")
            
            session.commit()
            logger.info("Database table optimization completed")
            
        except Exception as e:
            session.rollback()
            Logger.log_error(logger, e, "Failed to optimize database tables")
            raise
        finally:
            session.close()
    
    def run_migrations(self):
        """
        Run all database migrations.
        """
        logger.info("Running database migrations...")
        self.apply_indexes()
        self.optimize_tables()
        logger.info("Database migrations completed successfully")


if __name__ == "__main__":
    # Run migrations
    db_manager = DatabaseManager()
    try:
        db_manager.initialize()
        migrations = DatabaseMigrations(db_manager)
        migrations.run_migrations()
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        db_manager.close()