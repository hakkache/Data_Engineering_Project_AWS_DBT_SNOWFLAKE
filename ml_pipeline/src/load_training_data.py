"""
Load training data from Snowflake Gold layer OBT
"""
import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from typing import Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SnowflakeDataLoader:
    """Load data from Snowflake OBT for ML training"""
    
    def __init__(self):
        """Initialize Snowflake connection"""
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role=os.getenv('SNOWFLAKE_ROLE')
        )
        logger.info("Connected to Snowflake successfully")
    
    def load_obt_data(self, 
                      start_date: Optional[str] = None, 
                      end_date: Optional[str] = None,
                      sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load data from gold_obt_orders_ml_export view
        
        Args:
            start_date: Filter data from this date (YYYY-MM-DD)
            end_date: Filter data until this date (YYYY-MM-DD)
            sample_size: Limit number of rows (for testing)
            
        Returns:
            DataFrame with ML-ready features
        """
        query = """
        SELECT * FROM gold_obt_orders_ml_export
        WHERE 1=1
        """
        
        if start_date:
            query += f"\n  AND order_purchase_timestamp >= '{start_date}'"
        if end_date:
            query += f"\n  AND order_purchase_timestamp <= '{end_date}'"
        if sample_size:
            query += f"\n  LIMIT {sample_size}"
        
        logger.info(f"Executing query:\n{query}")
        df = pd.read_sql(query, self.conn)
        logger.info(f"Loaded {len(df):,} rows with {len(df.columns)} features")
        
        return df
    
    def load_full_obt(self, filters: Optional[dict] = None) -> pd.DataFrame:
        """
        Load full OBT with all features (including categorical)
        
        Args:
            filters: Dictionary of column: value filters
            
        Returns:
            Full OBT DataFrame
        """
        query = "SELECT * FROM gold_obt_orders WHERE 1=1"
        
        if filters:
            for col, val in filters.items():
                if isinstance(val, str):
                    query += f"\n  AND {col} = '{val}'"
                else:
                    query += f"\n  AND {col} = {val}"
        
        df = pd.read_sql(query, self.conn)
        logger.info(f"Loaded full OBT: {len(df):,} rows")
        return df
    
    def get_data_summary(self) -> dict:
        """Get summary statistics from Snowflake"""
        queries = {
            'total_orders': "SELECT COUNT(*) as cnt FROM gold_obt_orders",
            'delivered_orders': "SELECT COUNT(*) as cnt FROM gold_obt_orders WHERE order_status = 'delivered'",
            'date_range': "SELECT MIN(order_purchase_timestamp) as min_date, MAX(order_purchase_timestamp) as max_date FROM gold_obt_orders",
            'avg_order_value': "SELECT AVG(total_order_value) as avg_val FROM gold_obt_orders",
            'late_delivery_rate': "SELECT AVG(is_delayed::FLOAT) as rate FROM gold_obt_orders WHERE order_status = 'delivered'"
        }
        
        summary = {}
        for name, query in queries.items():
            result = pd.read_sql(query, self.conn)
            summary[name] = result.iloc[0].to_dict()
        
        return summary
    
    def close(self):
        """Close Snowflake connection"""
        self.conn.close()
        logger.info("Snowflake connection closed")


def prepare_ml_dataset(df: pd.DataFrame, 
                       target_col: str,
                       drop_cols: list = None) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features and target for ML
    
    Args:
        df: Input DataFrame
        target_col: Name of target column
        drop_cols: Additional columns to drop
        
    Returns:
        Tuple of (X, y)
    """
    # Default columns to drop
    default_drop = ['ORDER_ID', 'order_id']
    
    # Target columns to exclude from features (all possible variations)
    target_cols = ['IS_DELAYED', 'IS_CANCELED', 'IS_SATISFIED',
                   'is_delayed', 'is_canceled', 'is_satisfied', 
                   'target_review_score', 'TARGET_REVIEW_SCORE',
                   'target_delivery_days', 'TARGET_DELIVERY_DAYS',
                   'review_score', 'REVIEW_SCORE',
                   'order_status', 'ORDER_STATUS']
    
    # Combine drop lists
    all_drops = default_drop + target_cols
    if drop_cols:
        all_drops.extend(drop_cols)
    
    # Remove duplicates
    all_drops = list(set(all_drops))
    
    # Get target (check if exists)
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe. Available columns: {df.columns.tolist()}")
    y = df[target_col].copy()
    
    # Get features (drop target and ID columns)
    X = df.drop(columns=[col for col in all_drops if col in df.columns])
    
    # Handle missing values
    X = X.fillna(X.median())
    
    logger.info(f"Features: {X.shape[1]} columns")
    logger.info(f"Target ({target_col}): {len(y)} samples")
    logger.info(f"Target distribution:\n{y.value_counts()}")
    
    return X, y


def save_dataset(X: pd.DataFrame, y: pd.Series, 
                 output_dir: str = 'data',
                 prefix: str = 'train'):
    """Save processed dataset to parquet"""
    os.makedirs(output_dir, exist_ok=True)
    
    X.to_parquet(f"{output_dir}/{prefix}_features.parquet", index=False)
    y.to_frame('target').to_parquet(f"{output_dir}/{prefix}_target.parquet", index=False)
    
    logger.info(f"Saved dataset to {output_dir}/")


if __name__ == "__main__":
    # Example usage
    loader = SnowflakeDataLoader()
    
    # Get summary
    summary = loader.get_data_summary()
    print("\n=== Data Summary ===")
    for key, val in summary.items():
        print(f"{key}: {val}")
    
    # Load data for delivery prediction
    print("\n=== Loading Training Data ===")
    df = loader.load_obt_data(start_date='2017-01-01')
    
    # Prepare dataset for delivery delay prediction
    # Use the correct column name from Snowflake (uppercase)
    target_col = 'IS_DELAYED' if 'IS_DELAYED' in df.columns else 'is_delayed'
    X, y = prepare_ml_dataset(df, target_col=target_col)
    
    # Save
    save_dataset(X, y, output_dir='data', prefix='delivery_prediction')
    
    loader.close()
    print("\n✅ Data loading complete!")
