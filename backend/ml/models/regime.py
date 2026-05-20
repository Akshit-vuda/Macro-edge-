"""
RegimeClassifier: Market regime detection
Bull, Bear, Sideways, High/Low Volatility
Uses: Price patterns, volume, volatility features
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple
from enum import Enum


class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOL = "high_volatility"
    LOW_VOL = "low_volatility"


class RegimeClassifier:
    """
    Classifies market regime using multiple features:
    - Trend direction (SMA crossover)
    - Volatility level (ATR percentile)
    - Volume profile
    - Price momentum
    """
    
    def __init__(self, symbol: str = "SPY"):
        self.symbol = symbol
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def get_regime_features(self, prices: np.ndarray, 
                          volumes: np.ndarray) -> np.ndarray:
        """Extract regime detection features"""
        
        features = []
        
        for i in range(50, len(prices)):
            feat = []
            
            # SMA crossover - trend
            sma_20 = np.mean(prices[i-20:i])
            sma_50 = np.mean(prices[i-50:i])
            sma_ratio = sma_20 / sma_50
            feat.append(sma_ratio)
            
            # Price vs SMA
            price_vs_sma20 = prices[i] / sma_20
            feat.append(price_vs_sma20)
            
            # Volatility (ATR-style)
            high = np.max(prices[i-14:i])
            low = np.min(prices[i-14:i])
            atr = (high - low) / np.mean(prices[i-14:i])
            feat.append(atr)
            
            # Volume regime
            vol_ma = np.mean(volumes[i-20:i])
            vol_ratio = volumes[i] / vol_ma
            feat.append(vol_ratio)
            
            # Momentum
            mom_20 = (prices[i] - prices[i-20]) / prices[i-20]
            feat.append(mom_20)
            
            # Drawdown from peak
            peak = np.max(prices[i-50:i])
            drawdown = (prices[i] - peak) / peak
            feat.append(drawdown)
            
            # Returns distribution
            returns = np.diff(prices[i-20:i]) / prices[i-21:-1]
            feat.append(np.std(returns))  # vol
            feat.append(np.mean(returns))  # mean return
            
            features.append(feat)
            
        return np.array(features)
    
    def _label_regime(self, prices: np.ndarray) -> np.ndarray:
        """Label regime based on price action (unsupervised clustering)"""
        
        labels = []
        
        for i in range(50, len(prices)):
            # Calculate key metrics
            sma_20 = np.mean(prices[i-20:i])
            sma_50 = np.mean(prices[i-50:i])
            
            # Trend
            if sma_20 > sma_50 * 1.02:
                trend = 1  # Bull
            elif sma_20 < sma_50 * 0.98:
                trend = -1  # Bear  
            else:
                trend = 0  # Sideways
                
            # Volatility
            returns = np.diff(prices[i-20:i]) / prices[i-21:-1]
            vol = np.std(returns)
            
            if vol > 0.02:  # High vol
                vol_regime = 1
            elif vol < 0.008:  # Low vol
                vol_regime = -1
            else:
                vol_regime = 0
                
            # Combine into regime
            if trend == 1 and vol_regime <= 0:
                regime = 0  # BULL
            elif trend == -1 and vol_regime <= 0:
                regime = 1  # BEAR
            elif trend == 0:
                regime = 2  # SIDEWAYS
            elif vol_regime == 1:
                regime = 3  # HIGH_VOL
            else:
                regime = 2  # Default to sideways
                
            labels.append(regime)
            
        return np.array(labels)
    
    def train(self, prices: np.ndarray, volumes: np.ndarray,
              test_size: float = 0.2) -> dict:
        """Train the regime classifier"""
        
        X = self.get_regime_features(prices, volumes)
        y = self._label_regime(prices)
        
        if len(X) < 100:
            return {"error": "Need more samples"}
        
        X_scaled = self.scaler.fit_transform(X)
        
        split = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        return {
            "train_acc": self.model.score(X_train, y_train),
            "test_acc": self.model.score(X_test, y_test)
        }
    
    def predict(self, prices: np.ndarray, 
                volumes: np.ndarray) -> dict:
        """Detect current market regime"""
        
        if not self.is_trained:
            return self._fallback_regime(prices)
            
        try:
            features = self.get_regime_features(prices, volumes)
            X = self.scaler.transform(features[-1:])
            
            regime_id = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            confidence = max(proba)
            
            regime_names = {
                0: "bull", 
                1: "bear", 
                2: "sideways", 
                3: "high_volatility"
            }
            
            return {
                "regime": regime_names.get(regime_id, "sideways"),
                "regime_id": int(regime_id),
                "confidence": float(confidence),
                "action": "momentum" if regime_id == 0 else "defensive" if regime_id == 1 else "neutral"
            }
            
        except Exception as e:
            return self._fallback_regime(prices)
    
    def _fallback_regime(self, prices: np.ndarray) -> dict:
        """Fallback regime detection without ML"""
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        if sma_20 > sma_50 * 1.02:
            regime = "bull"
        elif sma_20 < sma_50 * 0.98:
            regime = "bear"
        else:
            regime = "sideways"
            
        returns = np.diff(prices[-20:]) / prices[-21:-1]
        vol = np.std(returns)
        
        if vol > 0.02:
            regime = "high_volatility"
            
        return {
            "regime": regime,
            "confidence": 0.65,
            "method": "rule_based"
        }
    
    def get_trade_bias(self, regime: str) -> str:
        """Get trade bias based on regime"""
        
        biases = {
            "bull": "overweight_long",
            "bear": "underweight_long",
            "sideways": "neutral",
            "high_volatility": "reduce_size",
            "low_volatility": "normal_size"
        }
        
        return biases.get(regime, "neutral")


# Convenience function
def classify_regime(symbol: str, prices: list, volumes: list) -> dict:
    """Detect market regime"""
    model = RegimeClassifier(symbol)
    return model.predict(np.array(prices), np.array(volumes))


if __name__ == "__main__":
    # Test
    np.random.seed(42)
    prices = 200 + np.cumsum(np.random.randn(300))
    volumes = np.random.lognormal(15, 0.5, 300)
    
    clf = RegimeClassifier("SPY")
    result = clf.train(prices, volumes)
    print("Training:", result)
    
    print("\nCurrent regime:")
    print(classify_regime("SPY", prices[-100:], volumes[-100:]))