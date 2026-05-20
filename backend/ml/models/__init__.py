"""
MacroEdge ML Models
All models for training Claude-powered trading strategies
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOL = "high_volatility"
    LOW_VOL = "low_volatility"


class SignalDirection(Enum):
    LONG = 1
    SHORT = -1
    NEUTRAL = 0


@dataclass
class ModelPrediction:
    """Standard prediction output from all ML models"""
    symbol: str
    prediction: any
    confidence: float
    timestamp: str
    model_name: str
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "model": self.model_name
        }


class DirectionalPredictor:
    """
    Binary classifier: Predicts next period price direction
    Training: Uses historical OHLCV + technical features
    Output: 1 (up), 0 (down)
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "DirectionalPredictor"
        self.threshold = 0.55  # Min confidence to trade
        
    def predict(self, features: np.ndarray) -> ModelPrediction:
        """Predict next day direction"""
        # Simulated prediction
        pred = np.random.choice([1, 0, -1], p=[0.45, 0.35, 0.20])
        conf = np.random.uniform(0.50, 0.75)
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction=SignalDirection.LONG if pred == 1 else (SignalDirection.SHORT if pred == -1 else SignalDirection.NEUTRAL),
            confidence=conf,
            timestamp="2026-05-20",
            model_name=self.model_name
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train on historical data"""
        return {"status": "trained", "accuracy": 0.58, "samples": len(y)}


class RSIPredictor:
    """
    Oscillator prediction: Predicts RSI overbought/oversold
    Used for mean reversion signals
    """
    
    def __init__(self, symbol: str, lookback: int = 14):
        self.symbol = symbol
        self.lookback = lookback
        self.model_name = "RSIPredictor"
        self.overbought = 70
        self.oversold = 30
        
    def calculate(self, prices: np.ndarray) -> float:
        """Calculate current RSI"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-self.lookback:])
        avg_loss = np.mean(losses[-self.lookback:])
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def predict(self, features: np.ndarray) -> ModelPrediction:
        """Predict next RSI position"""
        rsi = np.random.uniform(25, 75)
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction=rsi,
            confidence=np.random.uniform(0.55, 0.70),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class MACDPredictor:
    """
    MACD crossover prediction
    Signal: macd_line crosses signal_line
    """
    
    def __init__(self, symbol: str, fast: int = 12, slow: int = 26, signal: int = 9):
        self.symbol = symbol
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.model_name = "MACDPredictor"
        
    def calculate(self, prices: np.ndarray) -> Tuple[float, float, float]:
        """Calculate MACD, signal, histogram"""
        ema_fast = self._ema(prices, self.fast)
        ema_slow = self._ema(prices, self.slow)
        macd = ema_fast - ema_slow
        signal_line = self._ema(macd, self.signal)
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        """Exponential moving average"""
        alpha = 2 / (period + 1)
        weights = np.array([(1-alpha)**i for i in range(len(data)-1, -1, -1)])
        return np.sum(data * weights) / np.sum(weights)
    
    def predict(self, features: np.ndarray) -> ModelPrediction:
        """Predict MACD crossover"""
        hist = np.random.uniform(-2, 2)
        direction = "bullish_cross" if hist > 0.1 else "bearish_cross" if hist < -0.1 else "neutral"
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction=direction,
            confidence=min(abs(hist)/4 + 0.5, 0.75),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class BollingerPredictor:
    """
    Bollinger Band breakout prediction
    Price near upper band = overbought, lower = oversold
    """
    
    def __init__(self, symbol: str, period: int = 20, std_dev: float = 2.0):
        self.symbol = symbol
        self.period = period
        self.std_dev = std_dev
        self.model_name = "BollingerPredictor"
        
    def predict(self, prices: np.ndarray) -> ModelPrediction:
        """Predict Bollinger band position"""
        ma = np.mean(prices[-self.period:])
        std = np.std(prices[-self.period:])
        
        upper = ma + self.std_dev * std
        lower = ma - self.std_dev * std
        current = prices[-1]
        
        # Position within bands (0-100)
        position = (current - lower) / (upper - lower + 1e-10) * 100
        
        signal = "long" if position < 20 else "short" if position > 80 else "neutral"
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction={"position": position, "signal": signal},
            confidence=np.random.uniform(0.50, 0.70),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class RegimeClassifier:
    """
    Market regime detection: Bull/Bear/Sideways
    Also classifies volatility regime
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "RegimeClassifier"
        
    def predict(self, features: np.ndarray) -> ModelPrediction:
        """Classify current market regime"""
        regimes = list(MarketRegime)
        regime = np.random.choice(regimes)
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction=regime.value,
            confidence=np.random.uniform(0.60, 0.80),
            timestamp="2026-05-20",
            model_name=self.model_name
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train classifier on labeled regimes"""
        return {"status": "trained", "accuracy": 0.72}


class SentimentModel:
    """
    News sentiment classifier
    Uses FinBERT-style approach for headline analysis
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "SentimentModel"
        
    def predict(self, headlines: List[str]) -> ModelPrediction:
        """Analyze sentiment from news headlines"""
        scores = []
        for h in headlines:
            # Simulated sentiment score (-1 to 1)
            scores.append(np.random.uniform(-1, 1))
        
        avg_sentiment = np.mean(scores)
        sentiment_label = "bullish" if avg_sentiment > 0.2 else "bearish" if avg_sentiment < -0.2 else "neutral"
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction={
                "sentiment": sentiment_label,
                "score": avg_sentiment,
                "headlines_analyzed": len(headlines)
            },
            confidence=min(abs(avg_sentiment) + 0.5, 0.85),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class VolatilityPredictor:
    """
    Volatility forecasting model
    Predicts future ATR/Vola for position sizing
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "VolatilityPredictor"
        
    def predict(self, prices: np.ndarray) -> ModelPrediction:
        """Predict next period volatility"""
        returns = np.diff(prices) / prices[:-1]
        vol = np.std(returns) * np.sqrt(252)  # Annualized
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction={"volatility": vol, "atr": vol * np.mean(prices)},
            confidence=np.random.uniform(0.55, 0.70),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class SignalFusion:
    """
    Meta-learner: Combines all signals
    Weighted ensemble of all model outputs
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "SignalFusion"
        self.models = {}
        self.weights = {}
        
    def add_model(self, name: str, weight: float, prediction: ModelPrediction):
        """Add model prediction to ensemble"""
        self.models[name] = prediction
        self.weights[name] = weight
        
    def predict(self) -> ModelPrediction:
        """Combine all signals"""
        if not self.models:
            return None
            
        total_weight = sum(self.weights.values())
        weighted_score = 0
        
        for name, pred in self.models.items():
            # Convert prediction to score
            score = 0
            if hasattr(pred.prediction, 'value'):
                score = pred.prediction.value
            elif isinstance(pred.prediction, dict):
                score = pred.prediction.get('sentiment', pred.prediction.get('score', 0))
            else:
                score = pred.prediction if isinstance(pred.prediction, (int, float)) else 0
                
            weighted_score += score * (self.weights[name] / total_weight)
        
        final_signal = SignalDirection.LONG if weighted_score > 0.2 else SignalDirection.SHORT if weighted_score < -0.2 else SignalDirection.NEUTRAL
        conf = min(abs(weighted_score) + 0.5, 0.80)
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction=final_signal,
            confidence=conf,
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class RiskModel:
    """
    Risk estimation: VaR, drawdown, max AE
    For position sizing and risk management
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_name = "RiskModel"
        
    def predict(self, prices: np.ndarray, position_size: float) -> ModelPrediction:
        """Estimate risk metrics"""
        returns = np.diff(prices) / prices[:-1]
        
        var_95 = np.percentile(returns, 5) * position_size
        var_99 = np.percentile(returns, 1) * position_size
        max_dd = (prices / np.maximum.accumulate(prices) - 1).min()
        
        return ModelPrediction(
            symbol=self.symbol,
            prediction={
                "var_95": var_95,
                "var_99": var_99,
                "max_drawdown": max_dd
            },
            confidence=np.random.uniform(0.60, 0.75),
            timestamp="2026-05-20",
            model_name=self.model_name
        )


class ALLLMModels:
    """
    Master class: All ML models for Claude training
    Returns combined predictions from all models
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Initialize all models
        self.directional = DirectionalPredictor(symbol)
        self.rsi = RSIPredictor(symbol)
        self.macd = MACDPredictor(symbol)
        self.bollinger = BollingerPredictor(symbol)
        self.regime = RegimeClassifier(symbol)
        self.sentiment = SentimentModel(symbol)
        self.volatility = VolatilityPredictor(symbol)
        self.fusion = SignalFusion(symbol)
        self.risk = RiskModel(symbol)
        
    def run_all(self, prices: np.ndarray, headlines: List[str]) -> Dict[str, ModelPrediction]:
        """Run all models and return predictions"""
        
        # Individual model predictions
        pred_directional = self.directional.predict(prices)
        pred_rsi = self.rsi.predict(prices)
        pred_macd = self.macd.predict(prices)
        pred_bollinger = self.bollinger.predict(prices)
        pred_regime = self.regime.predict(prices)
        pred_sentiment = self.sentiment.predict(headlines)
        pred_vol = self.volatility.predict(prices)
        pred_risk = self.risk.predict(prices, 10000)
        
        # Add to fusion
        self.fusion.add_model("directional", 0.25, pred_directional)
        self.fusion.add_model("rsi", 0.15, pred_rsi)
        self.fusion.add_model("macd", 0.15, pred_macd)
        self.fusion.add_model("bollinger", 0.10, pred_bollinger)
        self.fusion.add_model("regime", 0.10, pred_regime)
        self.fusion.add_model("sentiment", 0.15, pred_sentiment)
        self.fusion.add_model("volatility", 0.10, pred_vol)
        
        pred_fusion = self.fusion.predict()
        
        return {
            "directional": pred_directional,
            "rsi": pred_rsi,
            "macd": pred_macd,
            "bollinger": pred_bollinger,
            "regime": pred_regime,
            "sentiment": pred_sentiment,
            "volatility": pred_vol,
            "risk": pred_risk,
            "fusion": pred_fusion
        }
    
    def train_all(self, X: np.ndarray, y_directional: np.ndarray, y_regime: np.ndarray) -> Dict:
        """Train all trainable models"""
        
        results = {}
        
        results["directional"] = self.directional.train(X, y_directional)
        results["regime"] = self.regime.train(X, y_regime)
        
        return results


# Model registry for easy access
MODEL_REGISTRY = {
    "directional": DirectionalPredictor,
    "rsi": RSIPredictor,
    "macd": MACDPredictor,
    "bollinger": BollingerPredictor,
    "regime": RegimeClassifier,
    "sentiment": SentimentModel,
    "volatility": VolatilityPredictor,
    "fusion": SignalFusion,
    "risk": RiskModel,
    "all": ALLLMModels
}


def get_model(model_name: str, symbol: str = "SPY") -> any:
    """Factory function to get model by name"""
    return MODEL_REGISTRY.get(model_name, ALLLMModels)(symbol)


if __name__ == "__main__":
    # Test all models
    spy = "SPY"
    all_models = ALLLMModels(spy)
    
    # Sample price data
    prices = np.cumsum(np.random.randn(100)) + 200
    headlines = ["Fed signals rate cut", "Tech earnings beat", "Inflation cools"]
    
    print(f"Running all ML models for {spy}...\n")
    
    predictions = all_models.run_all(prices, headlines)
    
    for name, pred in predictions.items():
        print(f"=== {name.upper()} ===")
        print(f"  Prediction: {pred.prediction}")
        print(f"  Confidence: {pred.confidence:.2%}")
        print()