"""
VolatilityPredictor: Forecast future volatility
Used for: Position sizing, stop loss, risk management
Uses: Historical volatility, volume, regime features
Output: Predicted ATR, volatility percentile
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple


class VolatilityPredictor:
    """
    Predicts future volatility for risk management
    Key inputs: Historical vol, volume, price regime
    """
    
    def __init__(self, symbol: str = "SPY"):
        self.symbol = symbol
        self.model = GradientBoostingRegressor(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def get_vol_features(self, prices: np.ndarray, 
                        volumes: np.ndarray) -> np.ndarray:
        """Extract volatility prediction features"""
        
        features = []
        
        for i in range(30, len(prices)):
            feat = []
            
            # Historical volatilities
            for window in [5, 10, 20, 50]:
                returns = np.diff(prices[i-window:i]) / prices[i-window:-1]
                vol = np.std(returns)
                feat.append(vol)
                
            # Volume features
            vol_ratio = volumes[i] / np.mean(volumes[i-20:i])
            feat.append(vol_ratio)
            
            # Recent return
            ret_5 = (prices[i] - prices[i-5]) / prices[i-5]
            feat.append(ret_5)
            
            # High/low ratio (range)
            high = np.max(prices[i-10:i])
            low = np.min(prices[i-10:i])
            hl_range = (high - low) / np.mean(prices[i-10:i])
            feat.append(hl_range)
            
            features.append(feat)
            
        return np.array(features)
    
    def create_vol_labels(self, prices: np.ndarray, horizon: int = 5) -> np.ndarray:
        """Future volatility as labels"""
        
        labels = []
        
        for i in range(30, len(prices) - horizon):
            #_future realized volatility
            future_returns = np.diff(prices[i:i+horizon]) / prices[i:i+horizon]
            future_vol = np.std(future_returns)
            labels.append(future_vol)
            
        return np.array(labels)
    
    def calculate_atr(self, highs: np.ndarray, lows: np.ndarray, 
                     closes: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range"""
        
        trs = []
        for i in range(1, len(closes)):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr = max(hl, hc, lc)
            trs.append(tr)
            
        return np.mean(trs[-period:])
    
    def train(self, prices: np.ndarray, volumes: np.ndarray,
             test_size: float = 0.2) -> dict:
        """Train volatility predictor"""
        
        X = self.get_vol_features(prices, volumes)
        y = self.create_vol_labels(prices)
        
        if len(X) < 100:
            return {"error": "Insufficient data"}
            
        X_scaled = self.scaler.fit_transform(X)
        
        split = int(len(X) * (1 - test_size))
        X_train, X_test = X_scaled[:split], X_scaled[split:]
        y_train, y_test = y[:split], y[split:]
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        from sklearn.metrics import mean_squared_error
        mse = mean_squared_error(y_test, self.model.predict(X_test))
        
        return {
            "mse": mse,
            "rmse": np.sqrt(mse),
            "train_samples": len(y_train),
            "test_samples": len(y_test)
        }
    
    def predict(self, prices: np.ndarray, 
               volumes: np.ndarray) -> dict:
        """Predict future volatility"""
        
        try:
            features = self.get_vol_features(prices, volumes)
            X = self.scaler.transform(features[-1:])
            
            vol_pred = self.model.predict(X)[0]
            
            # Current volatility for comparison
            returns_now = np.diff(prices[-20:]) / prices[-21:-1]
            vol_now = np.std(returns_now)
            
            # Percentile
            all_vols = features[:, 0]  # 5-day vol history
            percentile = (vol_pred / np.mean(all_vols)) * 50
            
            return {
                "predicted_volatility": float(vol_pred),
                "current_volatility": float(vol_now),
                "vol_change": float(vol_pred - vol_now),
                "percentile": float(min(max(percentile, 1), 99)),
                "action": "increase" if vol_pred > vol_now * 1.2 else "decrease"
            }
            
        except Exception:
            return self._fallback_vol(prices)
    
    def _fallback_vol(self, prices: np.ndarray) -> dict:
        """Simple volatility calculation"""
        
        returns = np.diff(prices[-20:]) / prices[-21:-1]
        vol = np.std(returns)
        
        return {
            "predicted_volatility": vol,
            "current_volatility": vol,
            "vol_change": 0,
            "percentile": 50,
            "method": "historical"
        }
    
    def estimate_position_size(self, portfolio_value: float,
                           volatility: float,
                           risk_per_trade: float = 0.02) -> float:
        """
        Use predicted volatility for position sizing
        Based on: Kelly Criterion concept
        """
        
        # Simplified: risk = vol * position / portfolio
        # position = risk * portfolio / vol
        
        max_vol = 0.30  # Cap at 30%
        effective_vol = min(volatility, max_vol)
        
        position = (risk_per_trade * portfolio_value) / effective_vol
        
        return position


# Convenience function
def predict_volatility(symbol: str, prices: list, volumes: list) -> dict:
    """Predict volatility"""
    model = VolatilityPredictor(symbol)
    return model.predict(np.array(prices), np.array(volumes))


if __name__ == "__main__":
    np.random.seed(42)
    prices = 200 + np.cumsum(np.random.randn(300))
    volumes = np.random.lognormal(15, 0.5, 300)
    
    model = VolatilityPredictor("SPY")
    print("Training:", model.train(prices, volumes))
    
    print("\nPrediction:")
    print(predict_volatility("SPY", prices[-100:], volumes[-100:]))