"""
Snowflake connection utilities for Streamlit dashboard
"""
import os
import streamlit as st
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
from typing import Optional
import logging
from pathlib import Path

# Load environment variables from ml_pipeline/.env
env_path = Path(__file__).parent.parent.parent / 'ml_pipeline' / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


@st.cache_resource
def get_snowflake_connection():
    """
    Get cached Snowflake connection
    
    Returns:
        Snowflake connection object
    """
    # Get credentials
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    database = os.getenv('SNOWFLAKE_DATABASE')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'gold')
    role = os.getenv('SNOWFLAKE_ROLE')
    
    # Check if credentials are loaded
    if not user or not password or not account:
        error_msg = "❌ Snowflake credentials not found!"
        logger.error(error_msg)
        st.error(error_msg)
        st.info("""
        **Please ensure your `.env` file exists in the `dbt_snowflake/` folder with:**
        ```
        SNOWFLAKE_USER=your_username
        SNOWFLAKE_PASSWORD=your_password
        SNOWFLAKE_ACCOUNT=your_account
        SNOWFLAKE_WAREHOUSE=COMPUTE_WH
        SNOWFLAKE_DATABASE=BRAZILIANECOMMERCE
        SNOWFLAKE_SCHEMA=gold
        SNOWFLAKE_ROLE=your_role
        ```
        """)
        return None
    
    try:
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )
        logger.info("✅ Connected to Snowflake successfully")
        st.success(f"✅ Connected to Snowflake: {database}.{schema}")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to Snowflake: {e}")
        st.error(f"Failed to connect to Snowflake: {e}")
        st.info("Check your credentials and ensure your Snowflake warehouse is running.")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def execute_query(_conn, query: str) -> pd.DataFrame:
    """
    Execute Snowflake query and return results as DataFrame
    
    Args:
        _conn: Snowflake connection (underscore prefix prevents hashing)
        query: SQL query to execute
        
    Returns:
        DataFrame with query results
    """
    if _conn is None:
        st.error("No Snowflake connection available")
        return pd.DataFrame()
    
    try:
        df = pd.read_sql(query, _conn)
        logger.info(f"✅ Query executed: {len(df)} rows returned")
        return df
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        st.error(f"Query execution failed: {e}")
        return pd.DataFrame()


def clear_cache():
    """Clear all Streamlit caches"""
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("✅ Cache cleared!")
