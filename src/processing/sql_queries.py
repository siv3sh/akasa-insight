"""
SQL-based KPI processing using SQLAlchemy queries.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session

from src.database.db_setup import Customer, Order, DatabaseManager
from src.utils import Logger

logger = Logger.get_logger(__name__)


class SQLAnalytics:
    """
    SQL-based analytics for calculating KPIs using SQLAlchemy.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SQL analytics with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    def get_repeat_customers(self) -> List[Dict[str, Any]]:
        """
        Get customers with more than one order.
        
        Returns:
            list: List of repeat customers with order count
        """
        logger.info("Calculating repeat customers using SQL...")
        session = self.db_manager.get_session()
        
        try:
            # Query to find customers with more than 1 order
            query = session.query(
                Customer.customer_id,
                Customer.customer_name,
                Customer.mobile_number,
                Customer.region,
                func.count(Order.order_id).label('order_count')
            ).join(
                Order, Customer.mobile_number == Order.mobile_number
            ).group_by(
                Customer.customer_id,
                Customer.customer_name,
                Customer.mobile_number,
                Customer.region
            ).having(
                func.count(Order.order_id) > 1
            ).order_by(
                desc('order_count')
            )
            
            results = query.all()
            
            repeat_customers = [
                {
                    'customer_id': r.customer_id,
                    'customer_name': r.customer_name,
                    'mobile_number': r.mobile_number,
                    'region': r.region,
                    'order_count': r.order_count
                }
                for r in results
            ]
            
            logger.info(f"Found {len(repeat_customers)} repeat customers")
            return repeat_customers
            
        except Exception as e:
            Logger.log_error(logger, e, "Error calculating repeat customers")
            raise
        finally:
            session.close()
    
    def get_monthly_order_trends(self) -> List[Dict[str, Any]]:
        """
        Get total number of orders per month.
        
        Returns:
            list: List of monthly order counts
        """
        logger.info("Calculating monthly order trends using SQL...")
        session = self.db_manager.get_session()
        
        try:
            # Query to group orders by year-month
            query = session.query(
                func.year(Order.order_date_time).label('year'),
                func.month(Order.order_date_time).label('month'),
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('total_revenue')
            ).group_by(
                func.year(Order.order_date_time),
                func.month(Order.order_date_time)
            ).order_by(
                'year', 'month'
            )
            
            results = query.all()
            
            monthly_trends = [
                {
                    'year': r.year,
                    'month': r.month,
                    'order_count': r.order_count,
                    'total_revenue': round(r.total_revenue, 2) if r.total_revenue else 0
                }
                for r in results
            ]
            
            logger.info(f"Found {len(monthly_trends)} months with orders")
            return monthly_trends
            
        except Exception as e:
            Logger.log_error(logger, e, "Error calculating monthly order trends")
            raise
        finally:
            session.close()
    
    def get_regional_revenue(self) -> List[Dict[str, Any]]:
        """
        Get total revenue grouped by region.
        
        Returns:
            list: List of regional revenue data
        """
        logger.info("Calculating regional revenue using SQL...")
        session = self.db_manager.get_session()
        
        try:
            # Query to calculate revenue by region
            query = session.query(
                Customer.region,
                func.count(func.distinct(Customer.customer_id)).label('customer_count'),
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('total_revenue'),
                func.avg(Order.total_amount).label('avg_order_value')
            ).join(
                Order, Customer.mobile_number == Order.mobile_number
            ).group_by(
                Customer.region
            ).order_by(
                desc('total_revenue')
            )
            
            results = query.all()
            
            regional_revenue = [
                {
                    'region': r.region,
                    'customer_count': r.customer_count,
                    'order_count': r.order_count,
                    'total_revenue': round(r.total_revenue, 2) if r.total_revenue else 0,
                    'avg_order_value': round(r.avg_order_value, 2) if r.avg_order_value else 0
                }
                for r in results
            ]
            
            logger.info(f"Found revenue data for {len(regional_revenue)} regions")
            return regional_revenue
            
        except Exception as e:
            Logger.log_error(logger, e, "Error calculating regional revenue")
            raise
        finally:
            session.close()
    
    def get_top_spenders(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top customers by spend in the last N days.
        
        Args:
            days: Number of days to look back (default: 30)
            limit: Number of top customers to return (default: 10)
            
        Returns:
            list: List of top spending customers
        """
        logger.info(f"Calculating top {limit} spenders for last {days} days using SQL...")
        session = self.db_manager.get_session()
        
        try:
            # Calculate the cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Query to find top spenders
            query = session.query(
                Customer.customer_id,
                Customer.customer_name,
                Customer.mobile_number,
                Customer.region,
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('total_spent'),
                func.avg(Order.total_amount).label('avg_order_value'),
                func.max(Order.order_date_time).label('last_order_date')
            ).join(
                Order, Customer.mobile_number == Order.mobile_number
            ).filter(
                Order.order_date_time >= cutoff_date
            ).group_by(
                Customer.customer_id,
                Customer.customer_name,
                Customer.mobile_number,
                Customer.region
            ).order_by(
                desc('total_spent')
            ).limit(limit)
            
            results = query.all()
            
            top_spenders = [
                {
                    'customer_id': r.customer_id,
                    'customer_name': r.customer_name,
                    'mobile_number': r.mobile_number,
                    'region': r.region,
                    'order_count': r.order_count,
                    'total_spent': round(r.total_spent, 2) if r.total_spent else 0,
                    'avg_order_value': round(r.avg_order_value, 2) if r.avg_order_value else 0,
                    'last_order_date': r.last_order_date.strftime('%Y-%m-%d') if r.last_order_date else None
                }
                for r in results
            ]
            
            logger.info(f"Found {len(top_spenders)} top spenders")
            return top_spenders
            
        except Exception as e:
            Logger.log_error(logger, e, "Error calculating top spenders")
            raise
        finally:
            session.close()
    
    def get_all_kpis(self) -> Dict[str, Any]:
        """
        Calculate all KPIs and return as a dictionary.
        
        Returns:
            dict: All KPI results
        """
        logger.info("Calculating all KPIs using SQL...")
        
        return {
            'repeat_customers': self.get_repeat_customers(),
            'monthly_order_trends': self.get_monthly_order_trends(),
            'regional_revenue': self.get_regional_revenue(),
            'top_spenders_30_days': self.get_top_spenders(days=30, limit=10)
        }
