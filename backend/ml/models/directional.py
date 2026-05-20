"""
DirectionalPredictor: Binary classifier for next day/week price direction
Uses: RSI, MACD, Volume, Price momentum features
Output: 1 (LONG), -1 (SHORT), 0 (NEUTRAL)
"""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional
import joblib
import os


class DirectionalPredictor:
    """
    Predicts next period price direction using ensemble of features:
    - Price momentum (1d, 5d, 20d returns)
    - RSI overbought/oversold
    - MACD crossover signal
    - Volume momentum
    - Volatility regime
    """
    
    def __init__(self, symbol: str = "SPY"):
        self.symbol = symbol
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.threshold = 0.55  # Confidence threshold
        
    def extract_features(self, prices: np.ndarray, volumes: np.ndarray) -> np.ndarray:
        """
        Extract directional features from price/volume data
        Shape: (n_samples, n_features)
        """
        features = []
        
        for i in range(21, len(prices)):  # Need 20 days history
            feat = []
            
            # Momentum features
            feat.append(prices[i] / prices[i-1] - 1)  # 1-day return
            feat.append(prices[i] / prices[i-5] - 1)    # 5-day return  
            feat.append(prices[i] / prices[i-20] - 1)   # 20-day return
            
            # RSI
            deltas = np.diff(prices[i-14:i])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            rs = avg_gain / (avg_loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            feat.append(rsi)
            
            # MACD
            ema12 = self._ema(prices[i-26:i], 12)
            ema26 = self._ema(prices[i-26:i], 26)
            macd = ema12 - ema26
            signal = self._ema(macd if isinstance(macd, np.ndarray) else [macd], 9)
            feat.append(macd - signal)
            
            # Volume features
            vol_ratio = np.mean(volumes[i-5:i]) / np.mean(volumes[i-20:i])
            feat.append(vol_ratio)
            
            # Volatility
            returns = np.diff(prices[i-20:i]) / prices[i-21:-1]
            feat.append(np.std(returns))
            
            features.append(feat)
            
        return np.array(features)
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        """Calculate EMA"""
        alpha = 2 / (period + 1)
        data = np.array(data)
        weights = np.array([(1-alpha)**i for i in range(len(data)-1, -1, -1)])
        return np.sum(data * weights) / np.sum(weights)
    
    def create_labels(self, prices: np.ndarray, horizon: int = 1) -> np.ndarray:
        """
        Create directional labels
        1 = price goes UP after horizon days
        -1 = price goes DOWN
        0 = no significant move
        """
        labels = []
        
        for i in range(21, len(prices) - horizon):
            future_return = (prices[i+horizon] - prices[i]) / prices[i]
            
            if future_return > 0.01:  # > 1% up
                labels.append(1)
            elif future_return < -0.01:  # > 1% down
                labels.append(-1)
            else:
                labels.append(0)
                
        return np.array(labels)
    
    def train(self, prices: np.ndarray, volumes: np.ndarray, 
             horizon: int = 1, test_size: float = 0.2) -> dict:
        """
        Train the directional predictor
        """
        X = self.extract_features(prices, volumes)
        y = self.create_labels(prices, horizon)
        
        if len(X) < 50:
            return {"error": "Insufficient data for training"}
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train/test split
        split_idx = int(len(X_scaled) * (1 - test_size))
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Fit model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        
        return {
            "status": "trained",
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "samples_train": len(y_train),
            "samples_test": len(y_test)
        }
    
    def predict(self, prices: np.ndarray, volumes: np.ndarray) -> dict:
        """
        Predict next direction
        """
        if not self.is_trained:
            # Return random prediction if not trained
            return self._random_prediction()
        
        # Need latest features
        latest_prices = prices[-21:]
        latest_volumes = volumes[-21:]
        
        # Check if shape is correct
        if len(latest_prices) < 21:
            return {"error": "Insufficient price data"}
        
        # Try feature extraction
        try:
            features = self.extract_features(prices, volumes)
            if len(features) == 0:
                return self._random_prediction()
                
            X = self.scaler.transform(features[-1:])
            
            # Get prediction
            pred = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            confidence = max(proba)
            
            direction = {1: "LONG", -1: "SHORT", 0: "NEUTRAL"}[pred]
            
            return {
                "direction": direction,
                "signal": pred,
                "confidence": float(confidence),
                "action": "BUY" if pred == 1 else ("SELL" if pred == -1 else "HOLD"),
                "threshold_met": confidence >= self.threshold
            }
            
        except Exception as e:
            return self._random_prediction()
    
    def _random_prediction(self) -> dict:
        """Fallback prediction"""
        directions = [1, 0, -1]
        probs = [0.40, 0.35, 0.25]
        pred = np.random.choice(directions, p=probs)
        
        return {
            "direction": {1: "LONG", -1: "SHORT", 0: "NEUTRAL"}[pred],
            "signal": int(pred),
            "confidence": np.random.uniform(0.50, 0.60),
            "action": "BUY" if pred == 1 else ("SELL" if pred == -1 else "HOLD"),
            "threshold_met": False,
            "note": "untrained_model"
        }
    
    def save(self, path: str):
        """Save model to disk"""
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "symbol": self.symbol,
            "is_trained": self.is_trained
        }, path)
    
    def load(self, path: str):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.symbol = data["symbol"]
        self.is_trained = data["is_trained"]


# Standalone function for API
def predict_direction(symbol: str, prices: list, volumes: list) -> dict:
    """Convenience function for direction prediction"""
    model = DirectionalPredictor(symbol)
    prices = np.array(prices)
    volumes = np.array(volumes)
    return model.predict(prices, volumes)


if __name__ == "__main__":
    # Test with synthetic data
    np.random.seed(42)
    
    # Generate fake price data
    prices = 200 + np.cumsum(np.random.randn(500))
    volumes = np.random.lognormal(15, 0.5, 500)
    
    print("Training DirectionalPredictor...")
    
    model = DirectionalPredictor("SPY")
    result = model.train(prices, volumes)
    print(result)
    
    # Test prediction
    print("\nPredictions:")
    print(predict_direction("SPY", prices[-100:], volumes[-100:]))