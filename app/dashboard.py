"""
Streamlit dashboard for visualizing Akasa Air KPIs.
"""

import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

# Add the project root to the path to enable imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.database import DatabaseManager
from src.processing.sql_queries import SQLAnalytics


def load_data():
    """Load all KPI data from SQL analytics."""
    db_manager = DatabaseManager()
    try:
        db_manager.initialize()
        analytics = SQLAnalytics(db_manager)
        
        # Load all KPIs
        repeat_customers = analytics.get_repeat_customers()
        monthly_trends = analytics.get_monthly_order_trends()
        regional_revenue = analytics.get_regional_revenue()
        top_spenders = analytics.get_top_spenders(days=30)
        
        return {
            'repeat_customers': repeat_customers,
            'monthly_trends': monthly_trends,
            'regional_revenue': regional_revenue,
            'top_spenders': top_spenders
        }
    finally:
        db_manager.close()


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format dataframe for better display."""
    # Round numeric columns
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].round(2)
    return df


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Akasa Air Analytics Dashboard",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("✈️ Akasa Air - Customer Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            data = load_data()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter for monthly trends
    if data['monthly_trends'] and len(data['monthly_trends']) > 0:
        df_monthly = pd.DataFrame(data['monthly_trends'])
        df_monthly['date'] = pd.to_datetime(df_monthly[['year', 'month']].assign(day=1))
        min_date = df_monthly['date'].min()
        max_date = df_monthly['date'].max()
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Region filter for regional revenue
    if data['regional_revenue']:
        regions = [item['region'] for item in data['regional_revenue']]
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            options=regions,
            default=regions
        )
    else:
        selected_regions = []
    
    # Tabs for different KPIs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Repeat Customers", 
        "Monthly Trends", 
        "Regional Revenue", 
        "Top Spenders"
    ])
    
    with tab1:
        st.header("Repeat Customers Analysis")
        if data['repeat_customers']:
            df = pd.DataFrame(data['repeat_customers'])
            df = format_dataframe(df)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Repeat Customers", len(df))
            if len(df) > 0:
                col2.metric("Avg Orders per Repeat Customer", 
                           round(df['order_count'].mean(), 1))
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # Visualization
            if len(df) > 0:
                fig = px.bar(df, x='customer_name', y='order_count',
                            title='Orders per Repeat Customer',
                            labels={'order_count': 'Number of Orders'})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No repeat customers found.")
    
    with tab2:
        st.header("Monthly Order Trends")
        if data['monthly_trends'] and len(data['monthly_trends']) > 0:
            df = pd.DataFrame(data['monthly_trends'])
            df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
            df = format_dataframe(df)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            total_orders = df['order_count'].sum()
            total_revenue = df['total_revenue'].sum()
            col1.metric("Total Orders", f"{total_orders:,}")
            col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
            if len(df) > 0:
                col3.metric("Avg Monthly Revenue", f"₹{total_revenue/len(df):,.2f}")
            
            # Time series chart
            if len(df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['date'], y=df['order_count'],
                                       mode='lines+markers', name='Orders'))
                fig.add_trace(go.Scatter(x=df['date'], y=df['total_revenue'],
                                       mode='lines+markers', name='Revenue',
                                       yaxis='y2'))
                
                fig.update_layout(
                    title='Monthly Orders and Revenue Trends',
                    xaxis_title='Month',
                    yaxis=dict(title='Number of Orders'),
                    yaxis2=dict(title='Revenue (₹)', overlaying='y', side='right')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            display_df = df[['year', 'month', 'order_count', 'total_revenue']]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No monthly trends data available.")
    
    with tab3:
        st.header("Regional Revenue Analysis")
        if data['regional_revenue'] and len(data['regional_revenue']) > 0:
            df = pd.DataFrame(data['regional_revenue'])
            df = format_dataframe(df)
            
            # Filter by selected regions
            if selected_regions:
                df = df[df['region'].isin(selected_regions)]
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Regions", len(df))
            if len(df) > 0:
                col2.metric("Total Customers", f"{df['customer_count'].sum():,}")
                col3.metric("Total Orders", f"{df['order_count'].sum():,}")
                col4.metric("Total Revenue", f"₹{df['total_revenue'].sum():,.2f}")
            
            # Revenue by region chart
            if len(df) > 0:
                fig = px.pie(df, values='total_revenue', names='region',
                            title='Revenue Distribution by Region')
                st.plotly_chart(fig, use_container_width=True)
                
                # Bar chart for multiple metrics
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=df['region'], y=df['customer_count'],
                                    name='Customers'))
                fig2.add_trace(go.Bar(x=df['region'], y=df['order_count'],
                                    name='Orders', yaxis='y2'))
                
                fig2.update_layout(
                    title='Customers and Orders by Region',
                    xaxis=dict(title='Region'),
                    yaxis=dict(title='Number of Customers'),
                    yaxis2=dict(title='Number of Orders', overlaying='y', side='right')
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Display table
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No regional revenue data available.")
    
    with tab4:
        st.header("Top Spenders (Last 30 Days)")
        if data['top_spenders']:
            df = pd.DataFrame(data['top_spenders'])
            df = format_dataframe(df)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Top Spenders", len(df))
            if len(df) > 0:
                col2.metric("Highest Spender", f"₹{df['total_spent'].max():,.2f}")
                col3.metric("Average Spending", f"₹{df['total_spent'].mean():,.2f}")
            
            # Bar chart
            if len(df) > 0:
                fig = px.bar(df.head(10), x='customer_name', y='total_spent',
                            title='Top 10 Customers by Spending',
                            labels={'total_spent': 'Total Spent (₹)'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No top spenders data available in the last 30 days.")
    
    # Footer
    st.markdown("---")
    st.caption("Akasa Air Analytics Dashboard | Data refreshed in real-time")


if __name__ == "__main__":
    main()