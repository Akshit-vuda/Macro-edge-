"""
ML Models for MacroEdge
XGBoost classifiers and ensemble models.
"""

import logging
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score
)
import xgboost as xgb
from scipy.stats import zscore

from config.settings import MIN_SIGNAL_CONFIDENCE

logger = logging.getLogger(__name__)


def create_features(
    tech_data: dict,
    sentiment_data: dict,
    macro_data: dict
) -> np.ndarray:
    """
    Combine technical, sentiment, and macro features.
    """
    features = []
    
    # Technical features
    tech_keys = [
        'rsi_14', 'macd', 'macd_signal', 'macd_hist',
        'bb_position', 'atr_14', 'volume_zscore',
        'returns_1d', 'returns_5d', 'momentum_12m_1m',
        'sma_20_50_ratio', 'sma_50_200_ratio'
    ]
    for key in tech_keys:
        features.append(tech_data.get(key, 0))
    
    # Sentiment features
    sent_keys = ['avg_sentiment', 'sentiment_std', 'pos_neg_ratio']
    for key in sent_keys:
        features.append(sentiment_data.get(key, 0))
    
    # Macro features
    macro_keys = ['vix', 'yield_curve', 'dxy']
    for key in macro_keys:
        features.append(macro_data.get(key, 0))
    
    return np.array(features)


def create_labels(returns: pd.Series, threshold: float = 0.005) -> np.ndarray:
    """
    Create binary labels: up (1) if return > threshold, else down (0).
    """
    labels = (returns > threshold).astype(int)
    return labels.values


class TechnicalModel:
    """
    XGBoost model for directional prediction.
    """
    
    def __init__(
        self,
        name: str = "technical_model",
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1
    ):
        self.name = name
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        
        self.model = None
        self.scaler = None
        self.is_trained = False
    
    def _create_model(self):
        """Create XGBoost classifier."""
        return xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            objective='binary:logistic',
            eval_metric='logloss',
            use_label_encoder=False
        )
    
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: list = None
    ):
        """Train the model."""
        if len(X) < 50:
            logger.warning("Not enough training samples")
            return
        
        logger.info(f"Training {self.name} on {len(X)} samples")
        
        self.model = self._create_model()
        
        # Handle NaN values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        self.model.fit(X, y)
        
        # Track feature names
        self.feature_names = feature_names
        
        self.is_trained = True
        logger.info(f"{self.name} trained successfully")
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probability of up/down."""
        if not self.is_trained:
            return np.array([[0.5, 0.5]])
        
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            probs = self.model.predict_proba(X)
            return probs
        except:
            return np.array([[0.5, 0.5]])
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class."""
        probs = self.predict_proba(X)
        return (probs[:, 1] > 0.5).astype(int)
    
    def predict_direction(
        self,
        tech_data: dict,
        sentiment_data: dict = None,
        macro_data: dict = None
    ) -> tuple:
        """
        Predict direction with confidence.
        Returns: (direction, confidence)
        direction: 'up' or 'down'
        confidence: 0-1
        """
        if not self.is_trained:
            logger.warning("Model not trained")
            return "hold", 0.0
        
        # Create feature vector
        features = create_features(
            tech_data or {},
            sentiment_data or {},
            macro_data or {}
        ).reshape(1, -1)
        
        probs = self.predict_proba(features)[0]
        
        # Threshold
        conf = probs[1]
        if conf > MIN_SIGNAL_CONFIDENCE:
            direction = "up"
        elif conf < (1 - MIN_SIGNAL_CONFIDENCE):
            direction = "down"
            conf = 1 - conf
        else:
            direction = "hold"
        
        return direction, conf
    
    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> dict:
        """Evaluate on test set."""
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        y_pred = self.predict(X)
        y_prob = self.predict_proba(X)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1': f1_score(y, y_pred, zero_division=0),
            'auc_roc': roc_auc_score(y, y_prob)
        }
        
        return metrics
    
    def save(self, path: str):
        """Save model."""
        if self.model:
            joblib.dump(self.model, path)
            if hasattr(self, 'feature_names'):
                with open(path + '.meta', 'w') as f:
                    json.dump({'feature_names': self.feature_names}, f)
    
    def load(self, path: str):
        """Load model."""
        self.model = joblib.load(path)
        if hasattr(self, 'feature_names'):
            try:
                with open(path + '.meta', 'r') as f:
                    meta = json.load(f)
                    self.feature_names = meta.get('feature_names')
            except:
                pass
        self.is_trained = True


class SignalFusion:
    """
    Combine multiple signals into single output.
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {
            'technical': 0.4,
            'sentiment': 0.3,
            'macro': 0.3
        }
    
    def add_model(self, name: str, model, weight: float = None):
        """Add a component model."""
        self.models[name] = model
        if weight:
            self.weights[name] = weight
    
    def fuse(
        self,
        direction_probs: dict
    ) -> tuple:
        """
        Fuse predictions from multiple models.
        Returns: (direction, confidence, components)
        """
        total_weight = sum(self.weights.values())
        
        prob_up = 0
        components = {}
        
        for name, prob in direction_probs.items():
            weight = self.weights.get(name, 0)
            normalized_weight = weight / total_weight
            
            prob_up += prob * normalized_weight
            components[name] = {
                'weight': normalized_weight,
                'prob': prob
            }
        
        # Generate signal
        if prob_up > MIN_SIGNAL_CONFIDENCE:
            direction = "up"
            confidence = prob_up
        elif prob_up < (1 - MIN_SIGNAL_CONFIDENCE):
            direction = "down"
            confidence = 1 - prob_up
        else:
            direction = "hold"
            confidence = abs(0.5 - prob_up) * 2
        
        return direction, confidence, components


class RegimeDetector:
    """
    Detect market regime (risk-on, risk-off, transitional).
    """
    
    def __init__(self, n_regimes: int = 3):
        self.n_regimes = n_regimes
        self.model = None
        self.features = None
        self.regimes = ['risk_on', 'risk_off', 'transitional']
    
    def create_features(
        self,
        vix_history: pd.Series,
        yields: pd.Series,
        dxy_history: pd.Series
    ) -> np.ndarray:
        """Create regime detection features."""
        from scipy.cluster.hierarchy import linkage, fcluster
        
        # Z-score normalize
        features = np.column_stack([
            zscore(vix_history.dropna()),
            zscore(yields.dropna()),
            zscore(dxy_history.dropna())
        ])
        
        return features
    
    def fit(self, features: np.ndarray):
        """Fit regime detector using clustering."""
        from sklearn.cluster import KMeans
        
        if len(features) < 30:
            logger.warning("Not enough data for regime detection")
            return
        
        self.model = KMeans(n_clusters=self.n_regimes, random_state=42)
        self.model.fit(features)
        self.features_mean = features.mean(axis=0)
        self.features_std = features.std(axis=0)
    
    def predict(
        self,
        vix: float,
        yield_slope: float,
        dxy: float
    ) -> str:
        """Predict current regime."""
        if self.model is None:
            return "transitional"
        
        features = np.array([[vix, yield_slope, dxy]])
        features = (features - self.features_mean) / self.features_std
        
        cluster = self.model.predict(features)[0]
        
        return self.regimes[cluster]
    
    def get_regime_weights(
        self,
        vix: float,
        yield_curve: dict,
        dxy: float,
        assets: list
    ) -> dict:
        """
        Get regime-aware model weights.
        """
        regime = self.predict(vix, yield_curve, dxy)
        
        # Adjust weights based on regime
        if regime == 'risk_off':
            # Defensive positioning
            weights = {
                'technical': 0.5,
                'sentiment': 0.2,
                'macro': 0.3
            }
        elif regime == 'risk_on':
            # Aggressive positioning
            weights = {
                'technical': 0.3,
                'sentiment': 0.4,
                'macro': 0.3
            }
        else:
            # Balanced
            weights = {
                'technical': 0.4,
                'sentiment': 0.3,
                'macro': 0.3
            }
        
        return {
            'regime': regime,
            'weights': weights
        }