"""
Make predictions using trained models
"""
import pandas as pd
import numpy as np
import joblib
import logging
import os
from typing import Union, List
from load_training_data import SnowflakeDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Make predictions using trained models"""
    
    def __init__(self, model_path: str):
        """
        Initialize predictor
        
        Args:
            model_path: Path to saved model file
        """
        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of predictions
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of probabilities
        """
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            logger.warning("Model does not support probability predictions")
            return None
    
    def predict_with_confidence(self, X: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        """
        Make predictions with confidence scores
        
        Args:
            X: Feature DataFrame
            threshold: Classification threshold
            
        Returns:
            DataFrame with predictions and confidence
        """
        predictions = self.predict(X)
        probabilities = self.predict_proba(X)
        
        results = pd.DataFrame({
            'prediction': predictions,
            'confidence': np.max(probabilities, axis=1) if probabilities is not None else None,
            'prob_class_0': probabilities[:, 0] if probabilities is not None else None,
            'prob_class_1': probabilities[:, 1] if probabilities is not None else None
        })
        
        return results
    
    def batch_predict(self, X: pd.DataFrame, batch_size: int = 1000) -> pd.DataFrame:
        """
        Make predictions in batches
        
        Args:
            X: Feature DataFrame
            batch_size: Size of each batch
            
        Returns:
            DataFrame with predictions
        """
        all_predictions = []
        
        for i in range(0, len(X), batch_size):
            batch = X.iloc[i:i+batch_size]
            predictions = self.predict_with_confidence(batch)
            all_predictions.append(predictions)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(X)-1)//batch_size + 1}")
        
        return pd.concat(all_predictions, ignore_index=True)


class DeliveryDelayPredictor:
    """Specialized predictor for delivery delays"""
    
    def __init__(self, model_path: str = '../models/IS_DELAYED_xgboost_model.pkl'):
        try:
            self.predictor = ModelPredictor(model_path)
        except FileNotFoundError:
            logger.error(f"Model not found at {model_path}")
            logger.info("Please train the model first using notebook 03_model_training.ipynb")
            raise
    
    def predict_from_snowflake(self, order_ids: List[str] = None) -> pd.DataFrame:
        """
        Predict delivery delays for orders in Snowflake
        
        Args:
            order_ids: List of order IDs to predict (None = all)
            
        Returns:
            DataFrame with predictions
        """
        loader = SnowflakeDataLoader()
        
        # Load data
        if order_ids:
            # Build IN clause properly
            order_ids_str = ','.join([f"'{oid}'" for oid in order_ids])
            query = f"SELECT * FROM gold_obt_orders_ml_export WHERE order_id IN ({order_ids_str})"
            df = pd.read_sql(query, loader.conn)
        else:
            df = loader.load_obt_data()
        
        loader.close()
        
        # Prepare features
        # Find order ID column (case-insensitive)
        order_id_col = None
        for col in ['ORDER_ID', 'order_id']:
            if col in df.columns:
                order_id_col = df[col].copy()
                break
        
        # Drop target and leakage columns (check existence first)
        cols_to_drop = ['ORDER_ID', 'order_id', 'IS_DELAYED', 'IS_CANCELED', 'IS_SATISFIED',
                       'is_delayed', 'is_canceled', 'is_satisfied',
                       'target_review_score', 'TARGET_REVIEW_SCORE',
                       'target_delivery_days', 'TARGET_DELIVERY_DAYS',
                       'review_score', 'REVIEW_SCORE', 'order_status', 'ORDER_STATUS',
                       'status', 'STATUS']
        
        X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
        
        # Handle missing values only for numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
        
        # Predict
        predictions = self.predictor.predict_with_confidence(X)
        
        # Combine with order IDs
        results = pd.concat([order_id_col.reset_index(drop=True), predictions], axis=1)
        results.columns = ['order_id', 'will_be_delayed', 'confidence', 
                          'prob_on_time', 'prob_delayed']
        
        # Add risk category
        results['risk_category'] = pd.cut(
            results['prob_delayed'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        return results
    
    def get_high_risk_orders(self, threshold: float = 0.7) -> pd.DataFrame:
        """Get orders with high risk of delay"""
        all_predictions = self.predict_from_snowflake()
        high_risk = all_predictions[all_predictions['prob_delayed'] >= threshold]
        
        logger.info(f"Found {len(high_risk)} high-risk orders (>{threshold*100}% delay probability)")
        
        return high_risk.sort_values('prob_delayed', ascending=False)


class ChurnPredictor:
    """Specialized predictor for customer churn"""
    
    def __init__(self, model_path: str = '../models/churn_prediction_model.pkl'):
        try:
            self.predictor = ModelPredictor(model_path)
        except FileNotFoundError:
            logger.error(f"Model not found at {model_path}")
            logger.info("Churn prediction model not yet implemented in notebooks")
            raise
    
    def predict_customer_churn(self, customer_ids: List[str] = None) -> pd.DataFrame:
        """
        Predict churn for customers
        
        Args:
            customer_ids: List of customer IDs
            
        Returns:
            DataFrame with churn predictions
        """
        loader = SnowflakeDataLoader()
        
        # Load latest order per customer
        if customer_ids:
            customer_ids_str = ','.join([f"'{cid}'" for cid in customer_ids])
            filter_clause = f"WHERE customer_id IN ({customer_ids_str})"
        else:
            filter_clause = ""
        
        query = f"""
        SELECT *
        FROM gold_obt_orders_ml_export
        WHERE order_id IN (
            SELECT order_id
            FROM gold_obt_orders
            QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_purchase_timestamp DESC) = 1
        )
        {filter_clause}
        """
        
        df = pd.read_sql(query, loader.conn)
        loader.close()
        
        # Calculate churn label (handle column name case-insensitively)
        days_col = None
        for col in ['DAYS_SINCE_LAST_ORDER', 'days_since_last_order']:
            if col in df.columns:
                days_col = col
                break
        
        if days_col is None:
            raise ValueError("Column 'days_since_last_order' not found in dataframe")
        
        df['is_churned'] = (df[days_col] > 90).astype(int)
        
        # Prepare features
        customer_id_col = None
        for col in ['CUSTOMER_ID', 'customer_id']:
            if col in df.columns:
                customer_id_col = df[col].copy()
                break
        
        # Drop columns safely
        cols_to_drop = ['ORDER_ID', 'order_id', 'CUSTOMER_ID', 'customer_id',
                       'IS_DELAYED', 'IS_CANCELED', 'IS_SATISFIED',
                       'is_delayed', 'is_canceled', 'is_satisfied',
                       'target_review_score', 'TARGET_REVIEW_SCORE',
                       'target_delivery_days', 'TARGET_DELIVERY_DAYS',
                       'review_score', 'REVIEW_SCORE', 'order_status', 'ORDER_STATUS',
                       'status', 'STATUS', 'is_churned']
        
        X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
        
        # Handle missing values for numeric columns only
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
        
        # Predict
        predictions = self.predictor.predict_with_confidence(X)
        
        results = pd.DataFrame({
            'customer_id': customer_id_col if customer_id_col is not None else range(len(predictions)),
            'will_churn': predictions['prediction'],
            'churn_probability': predictions['prob_class_1'],
            'retention_probability': predictions['prob_class_0']
        })
        
        # Add priority
        results['priority'] = pd.cut(
            results['churn_probability'],
            bins=[0, 0.4, 0.7, 1.0],
            labels=['Low Priority', 'Medium Priority', 'High Priority']
        )
        
        return results
    
    def get_at_risk_customers(self, threshold: float = 0.6) -> pd.DataFrame:
        """Get customers at risk of churning"""
        predictions = self.predict_customer_churn()
        at_risk = predictions[predictions['churn_probability'] >= threshold]
        
        logger.info(f"Found {len(at_risk)} at-risk customers (>{threshold*100}% churn probability)")
        
        return at_risk.sort_values('churn_probability', ascending=False)


def predict_new_orders(new_orders_df: pd.DataFrame, 
                       model_path: str = '../models/IS_DELAYED_xgboost_model.pkl') -> pd.DataFrame:
    """
    Predict delivery delays for new orders
    
    Args:
        new_orders_df: DataFrame with new order features
        model_path: Path to trained model
        
    Returns:
        DataFrame with predictions
    """
    predictor = ModelPredictor(model_path)
    
    # Ensure all required features are present
    # Fill missing values for numeric columns only
    numeric_cols = new_orders_df.select_dtypes(include=[np.number]).columns
    new_orders_df[numeric_cols] = new_orders_df[numeric_cols].fillna(new_orders_df[numeric_cols].median())
    
    # Predict
    predictions = predictor.predict_with_confidence(new_orders_df)
    
    logger.info(f"Predictions made for {len(predictions)} new orders")
    
    return predictions


if __name__ == "__main__":
    print("="*60)
    print("DELIVERY DELAY PREDICTION")
    print("="*60)
    
    try:
        # Predict delivery delays
        delay_predictor = DeliveryDelayPredictor()
        
        # Get high-risk orders
        high_risk = delay_predictor.get_high_risk_orders(threshold=0.7)
        print(f"\nHigh-Risk Orders: {len(high_risk)}")
        print(high_risk.head(10))
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nPlease train the model first:")
        print("  1. Run notebook: 02_feature_engineering.ipynb")
        print("  2. Run notebook: 03_model_training.ipynb")
    except Exception as e:
        print(f"❌ Error during delivery delay prediction: {e}")
    
    print("\n" + "="*60)
    print("CUSTOMER CHURN PREDICTION")
    print("="*60)
    
    try:
        # Predict churn
        churn_predictor = ChurnPredictor()
        at_risk = churn_predictor.get_at_risk_customers(threshold=0.6)
        print(f"\nAt-Risk Customers: {len(at_risk)}")
        print(at_risk.head(10))
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nChurn prediction model not yet implemented in notebooks.")
    except Exception as e:
        print(f"❌ Error during churn prediction: {e}")
    
    print("\n✅ Script execution complete!")
