"""
Train ML models for various prediction tasks
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
import joblib
import logging
from typing import Tuple, Dict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLTrainer:
    """Train and evaluate ML models"""
    
    def __init__(self, model_type: str = 'xgboost', task: str = 'classification'):
        """
        Initialize trainer
        
        Args:
            model_type: Type of model ('xgboost', 'lightgbm', 'catboost', 'random_forest')
            task: 'classification' or 'regression'
        """
        self.model_type = model_type
        self.task = task
        self.model = self._get_model()
        self.best_model = None
        
    def _get_model(self):
        """Get model based on type"""
        if self.task == 'classification':
            models = {
                'xgboost': XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='logloss'
                ),
                'lightgbm': LGBMClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                ),
                'catboost': CatBoostClassifier(
                    iterations=100,
                    depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    verbose=False
                ),
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            }
        else:
            raise NotImplementedError("Regression models not yet implemented")
        
        return models[self.model_type]
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train model"""
        logger.info(f"Training {self.model_type} model...")
        logger.info(f"Training data shape: {X_train.shape}")
        
        self.model.fit(X_train, y_train)
        logger.info("✅ Training complete")
        
        return self.model
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Evaluate model performance"""
        logger.info("Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        logger.info("\n=== Model Performance ===")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"\nConfusion Matrix:\n{cm}")
        
        # Classification Report
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        return metrics
    
    def get_feature_importance(self, feature_names: list, top_n: int = 20) -> pd.DataFrame:
        """Get feature importance"""
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.info(f"\n=== Top {top_n} Important Features ===")
            logger.info(importance_df.head(top_n).to_string(index=False))
            
            return importance_df
        else:
            logger.warning("Model does not support feature importance")
            return None
    
    def hyperparameter_tuning(self, X_train: pd.DataFrame, y_train: pd.Series,
                             param_grid: dict, cv: int = 5):
        """Perform hyperparameter tuning"""
        logger.info("Starting hyperparameter tuning...")
        
        grid_search = GridSearchCV(
            self.model, 
            param_grid, 
            cv=cv, 
            scoring='roc_auc',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
        
        self.best_model = grid_search.best_estimator_
        return grid_search
    
    def save_model(self, filepath: str, metrics: dict = None):
        """Save trained model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
        
        # Save metrics
        if metrics:
            metrics_path = filepath.replace('.pkl', '_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Metrics saved to {metrics_path}")
    
    @staticmethod
    def load_model(filepath: str):
        """Load trained model"""
        model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
        return model


def train_delivery_prediction_model():
    """Train delivery delay prediction model"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING DELIVERY DELAY PREDICTION MODEL")
    logger.info("="*50)
    
    # Load data (use notebook naming convention)
    try:
        X_train = pd.read_parquet('../data/X_train_delayed.parquet')
        y_train = pd.read_parquet('../data/y_train_delayed.parquet')['IS_DELAYED']
        X_test = pd.read_parquet('../data/X_test_delayed.parquet')
        y_test = pd.read_parquet('../data/y_test_delayed.parquet')['IS_DELAYED']
        
        logger.info(f"Loaded datasets from notebooks")
    except FileNotFoundError:
        logger.error("Dataset files not found. Please run notebook 02_feature_engineering.ipynb first")
        raise
    
    logger.info(f"Train set: {X_train.shape[0]:,} samples")
    logger.info(f"Test set: {X_test.shape[0]:,} samples")
    
    # Check class distribution
    logger.info(f"Train class distribution:\n{y_train.value_counts()}")
    logger.info(f"Test class distribution:\n{y_test.value_counts()}")
    
    # Train model
    trainer = MLTrainer(model_type='xgboost', task='classification')
    trainer.train(X_train, y_train)
    
    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)
    
    # Feature importance
    importance_df = trainer.get_feature_importance(X.columns.tolist())
    
    # Save model with notebook naming convention
    os.makedirs('../models', exist_ok=True)
    trainer.save_model('../models/IS_DELAYED_xgboost_model.pkl', metrics=metrics)
    
    # Save feature importance
    if importance_df is not None:
        importance_df.to_csv('../models/IS_DELAYED_xgboost_feature_importance.csv', index=False)
    
    return trainer, metrics


def train_churn_prediction_model():
    """Train customer churn prediction model"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING CHURN PREDICTION MODEL")
    logger.info("="*50)
    
    # Load and prepare data
    from load_training_data import SnowflakeDataLoader, prepare_ml_dataset
    
    loader = SnowflakeDataLoader()
    df = loader.load_obt_data()
    
    # Create churn label (no order in last 90 days)
    # Check column name (case-insensitive)
    days_col = None
    for col in ['DAYS_SINCE_LAST_ORDER', 'days_since_last_order']:
        if col in df.columns:
            days_col = col
            break
    
    if days_col is None:
        logger.error("Column 'days_since_last_order' not found in dataframe")
        loader.close()
        raise ValueError("Required column not found")
    
    df['is_churned'] = (df[days_col] > 90).astype(int)
    
    X, y = prepare_ml_dataset(df, target_col='is_churned')
    loader.close()
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train
    trainer = MLTrainer(model_type='lightgbm', task='classification')
    trainer.train(X_train, y_train)
    
    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save
    trainer.save_model('models/churn_prediction_model.pkl', metrics=metrics)
    
    return trainer, metrics


def train_review_score_model():
    """Train review score prediction model"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING REVIEW SCORE PREDICTION MODEL")
    logger.info("="*50)
    
    from load_training_data import SnowflakeDataLoader, prepare_ml_dataset
    
    loader = SnowflakeDataLoader()
    df = loader.load_obt_data()
    loader.close()
    
    # Binary classification: positive (4-5) vs negative (1-3)
    # WARNING: This uses review_score which is DATA LEAKAGE for satisfaction prediction
    # Find the review score column
    review_col = None
    for col in ['TARGET_REVIEW_SCORE', 'target_review_score', 'REVIEW_SCORE', 'review_score']:
        if col in df.columns:
            review_col = col
            break
    
    if review_col is None:
        logger.error("Review score column not found. Cannot train review prediction model.")
        logger.warning("Note: This model would have data leakage anyway - reviews happen after delivery")
        loader.close()
        raise ValueError("Review score column not found")
    
    df['positive_review'] = (df[review_col] >= 4).astype(int)
    
    X, y = prepare_ml_dataset(df, target_col='positive_review')
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train
    trainer = MLTrainer(model_type='catboost', task='classification')
    trainer.train(X_train, y_train)
    
    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save
    trainer.save_model('models/review_score_model.pkl', metrics=metrics)
    
    return trainer, metrics


if __name__ == "__main__":
    # Create models directory
    os.makedirs('../models', exist_ok=True)
    
    print("\n⚠️  NOTE: For full model training, use notebook 03_model_training.ipynb")
    print("This script trains only the delivery delay model as an example.\n")
    
    # Train delivery delay prediction model
    try:
        trainer, metrics = train_delivery_prediction_model()
        
        print("\n✅ Model training complete!")
        print(f"Model saved to: ../models/IS_DELAYED_xgboost_model.pkl")
        print(f"ROC-AUC Score: {metrics['roc_auc']:.4f}")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease run these notebooks first:")
        print("  1. notebooks/02_feature_engineering.ipynb")
        print("  2. notebooks/03_model_training.ipynb")
