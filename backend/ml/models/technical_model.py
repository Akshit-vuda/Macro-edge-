"""
TechnicalModel: XGBoost directional predictor.
Combines technical, sentiment, and macro features into an up/down/hold call.

Migrated from the legacy backend/ml/models.py so the canonical package owns it
(the old standalone file shadowed this package and broke `from backend.ml.models
import TechnicalModel`).
"""

import logging
import json
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
import xgboost as xgb

from config.settings import MIN_SIGNAL_CONFIDENCE

logger = logging.getLogger(__name__)


def create_features(
    tech_data: dict,
    sentiment_data: dict,
    macro_data: dict
) -> np.ndarray:
    """Combine technical, sentiment, and macro features into one vector."""
    features = []

    tech_keys = [
        'rsi_14', 'macd', 'macd_signal', 'macd_hist',
        'bb_position', 'atr_14', 'volume_zscore',
        'returns_1d', 'returns_5d', 'momentum_12m_1m',
        'sma_20_50_ratio', 'sma_50_200_ratio'
    ]
    for key in tech_keys:
        features.append(tech_data.get(key, 0))

    sent_keys = ['avg_sentiment', 'sentiment_std', 'pos_neg_ratio']
    for key in sent_keys:
        features.append(sentiment_data.get(key, 0))

    macro_keys = ['vix', 'yield_curve', 'dxy']
    for key in macro_keys:
        features.append(macro_data.get(key, 0))

    return np.array(features)


class TechnicalModel:
    """XGBoost model for directional prediction."""

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


if __name__ == "__main__":
    # ponytail: smoke check the untrained default path (no XGBoost training needed)
    m = TechnicalModel()
    assert m.predict_direction({}) == ("hold", 0.0)
    assert create_features({}, {}, {}).shape == (18,)
    print("TechnicalModel self-check passed")
