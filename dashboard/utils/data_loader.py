"""
Data loading utilities for analytics dashboard
Queries dbt gold layer tables
"""
import pandas as pd
from typing import Optional, Tuple
from datetime import datetime
from .snowflake_connector import get_snowflake_connection, execute_query


def load_order_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_status: Optional[str] = None
) -> pd.DataFrame:
    """
    Load order summary data from gold_fact_order_summary
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        order_status: Order status filter
        
    Returns:
        DataFrame with order summary
    """
    conn = get_snowflake_connection()
    
    query = """
    SELECT 
        ORDER_ID,
        CUSTOMER_ID,
        ORDER_STATUS,
        ORDER_PURCHASE_TIMESTAMP,
        ORDER_DATE_KEY,
        ACTUAL_DELIVERY_DAYS,
        IS_LATE_DELIVERY,
        TOTAL_UNIQUE_PRODUCTS,
        TOTAL_ITEMS,
        TOTAL_PRODUCT_VALUE,
        TOTAL_FREIGHT_VALUE,
        TOTAL_ORDER_VALUE,
        TOTAL_PAYMENT_VALUE,
        MAX_INSTALLMENTS,
        PAYMENT_TYPES_USED,
        REVIEW_SCORE,
        REVIEW_SENTIMENT,
        HAS_REVIEW_COMMENT
    FROM gold_fact_order_summary
    WHERE 1=1
    """
    
    if start_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP >= '{start_date}'"
    if end_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP <= '{end_date}'"
    if order_status and order_status != 'All':
        query += f"\n  AND ORDER_STATUS = '{order_status}'"
    
    query += "\nORDER BY ORDER_PURCHASE_TIMESTAMP DESC"
    
    return execute_query(conn, query)


def load_customer_features() -> pd.DataFrame:
    """
    Load customer features from fs_customer_features
    
    Returns:
        DataFrame with customer features
    """
    conn = get_snowflake_connection()
    
    query = """
    SELECT 
        CUSTOMER_ID,
        CUSTOMER_STATE,
        CUSTOMER_ORDER_COUNT,
        CUSTOMER_LIFETIME_VALUE,
        CUSTOMER_AVG_ORDER_VALUE,
        CUSTOMER_TENURE_DAYS,
        CUSTOMER_SEGMENT,
        FEATURE_TIMESTAMP
    FROM fs_customer_features
    WHERE CUSTOMER_ORDER_COUNT > 0
    ORDER BY CUSTOMER_LIFETIME_VALUE DESC
    """
    
    return execute_query(conn, query)


def load_gold_obt_summary(limit: int = 10000) -> pd.DataFrame:
    """
    Load summary data from gold_obt_orders for analytics
    
    Args:
        limit: Maximum number of rows to return
        
    Returns:
        DataFrame with OBT summary
    """
    conn = get_snowflake_connection()
    
    query = f"""
    SELECT 
        ORDER_ID,
        CUSTOMER_ID,
        ORDER_STATUS,
        ORDER_PURCHASE_TIMESTAMP,
        CUSTOMER_STATE,
        CUSTOMER_CITY,
        PRODUCT_CATEGORY_ENGLISH AS PRODUCT_CATEGORY,
        SELLER_STATE,
        PAYMENT_TYPES,
        MAX_INSTALLMENTS AS PAYMENT_INSTALLMENTS,
        TOTAL_PAYMENT_VALUE AS PAYMENT_VALUE,
        TOTAL_ORDER_VALUE AS PRICE,
        TOTAL_FREIGHT_VALUE AS FREIGHT_VALUE,
        ACTUAL_DELIVERY_DAYS,
        ESTIMATED_DELIVERY_DAYS,
        IS_LATE_DELIVERY,
        REVIEW_SCORE,
        REVIEW_SENTIMENT,
        CUSTOMER_ORDER_COUNT,
        CUSTOMER_LIFETIME_VALUE,
        DAYS_SINCE_LAST_ORDER
    FROM gold_obt_orders
    WHERE ORDER_STATUS IS NOT NULL
    ORDER BY ORDER_PURCHASE_TIMESTAMP DESC
    LIMIT {limit}
    """
    
    return execute_query(conn, query)


def get_kpi_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get high-level KPI metrics
    
    Args:
        start_date: Start date filter
        end_date: End date filter
        
    Returns:
        Dictionary with KPI metrics
    """
    conn = get_snowflake_connection()
    
    query = """
    SELECT 
        COUNT(DISTINCT ORDER_ID) AS TOTAL_ORDERS,
        COUNT(DISTINCT CUSTOMER_ID) AS TOTAL_CUSTOMERS,
        SUM(TOTAL_ORDER_VALUE) AS TOTAL_REVENUE,
        AVG(TOTAL_ORDER_VALUE) AS AVG_ORDER_VALUE,
        AVG(ACTUAL_DELIVERY_DAYS) AS AVG_DELIVERY_DAYS,
        AVG(CASE WHEN IS_LATE_DELIVERY = 1 THEN 1.0 ELSE 0.0 END) AS LATE_DELIVERY_RATE,
        AVG(REVIEW_SCORE) AS AVG_REVIEW_SCORE,
        COUNT(DISTINCT CASE WHEN ORDER_STATUS = 'canceled' THEN ORDER_ID END) AS CANCELED_ORDERS,
        AVG(CASE WHEN ORDER_STATUS = 'canceled' THEN 1.0 ELSE 0.0 END) AS CANCELLATION_RATE
    FROM gold_fact_order_summary
    WHERE 1=1
    """
    
    if start_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP >= '{start_date}'"
    if end_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP <= '{end_date}'"
    
    df = execute_query(conn, query)
    
    if not df.empty:
        return df.iloc[0].to_dict()
    return {}


def get_sales_over_time(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = 'day'
) -> pd.DataFrame:
    """
    Get sales trends over time
    
    Args:
        start_date: Start date filter
        end_date: End date filter
        granularity: 'day', 'week', or 'month'
        
    Returns:
        DataFrame with time series data
    """
    conn = get_snowflake_connection()
    
    date_trunc_map = {
        'day': 'DAY',
        'week': 'WEEK',
        'month': 'MONTH'
    }
    
    date_trunc = date_trunc_map.get(granularity, 'DAY')
    
    query = f"""
    SELECT 
        DATE_TRUNC('{date_trunc}', ORDER_PURCHASE_TIMESTAMP) AS DATE,
        COUNT(DISTINCT ORDER_ID) AS ORDER_COUNT,
        SUM(TOTAL_ORDER_VALUE) AS REVENUE,
        AVG(TOTAL_ORDER_VALUE) AS AVG_ORDER_VALUE,
        COUNT(DISTINCT CUSTOMER_ID) AS UNIQUE_CUSTOMERS
    FROM gold_fact_order_summary
    WHERE ORDER_STATUS != 'canceled'
    """
    
    if start_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP >= '{start_date}'"
    if end_date:
        query += f"\n  AND ORDER_PURCHASE_TIMESTAMP <= '{end_date}'"
    
    query += f"\nGROUP BY DATE_TRUNC('{date_trunc}', ORDER_PURCHASE_TIMESTAMP)"
    query += "\nORDER BY DATE"
    
    return execute_query(conn, query)


def get_top_products(limit: int = 10) -> pd.DataFrame:
    """
    Get top selling products
    
    Args:
        limit: Number of top products to return
        
    Returns:
        DataFrame with top products
    """
    conn = get_snowflake_connection()
    
    query = f"""
    SELECT 
        PRODUCT_CATEGORY_ENGLISH AS PRODUCT_CATEGORY,
        COUNT(DISTINCT ORDER_ID) AS ORDER_COUNT,
        SUM(TOTAL_ORDER_VALUE) AS TOTAL_REVENUE,
        AVG(TOTAL_ORDER_VALUE) AS AVG_PRICE,
        AVG(REVIEW_SCORE) AS AVG_REVIEW_SCORE
    FROM gold_obt_orders
    WHERE PRODUCT_CATEGORY_ENGLISH IS NOT NULL
    GROUP BY PRODUCT_CATEGORY_ENGLISH
    ORDER BY TOTAL_REVENUE DESC
    LIMIT {limit}
    """
    
    return execute_query(conn, query)


def get_customer_segments() -> pd.DataFrame:
    """
    Get customer segmentation data
    
    Returns:
        DataFrame with customer segments
    """
    conn = get_snowflake_connection()
    
    query = """
    SELECT 
        CUSTOMER_SEGMENT,
        COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMER_COUNT,
        AVG(CUSTOMER_LIFETIME_VALUE) AS AVG_REVENUE,
        AVG(CUSTOMER_AVG_ORDER_VALUE) AS AVG_ORDER_VALUE
    FROM fs_customer_features
    WHERE CUSTOMER_ORDER_COUNT > 0
    GROUP BY CUSTOMER_SEGMENT
    ORDER BY CUSTOMER_COUNT DESC
    """
    
    return execute_query(conn, query)


def get_delivery_performance_by_state() -> pd.DataFrame:
    """
    Get delivery performance metrics by state
    
    Returns:
        DataFrame with state-level delivery metrics
    """
    conn = get_snowflake_connection()
    
    query = """
    SELECT 
        CUSTOMER_STATE,
        COUNT(DISTINCT ORDER_ID) AS ORDER_COUNT,
        AVG(ACTUAL_DELIVERY_DAYS) AS AVG_DELIVERY_DAYS,
        AVG(CASE WHEN IS_LATE_DELIVERY = 1 THEN 1.0 ELSE 0.0 END) AS LATE_DELIVERY_RATE,
        AVG(REVIEW_SCORE) AS AVG_REVIEW_SCORE
    FROM gold_obt_orders
    WHERE ORDER_STATUS = 'delivered'
      AND CUSTOMER_STATE IS NOT NULL
    GROUP BY CUSTOMER_STATE
    ORDER BY ORDER_COUNT DESC
    """
    
    return execute_query(conn, query)
