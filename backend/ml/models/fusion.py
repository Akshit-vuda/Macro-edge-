"""
SignalFusion: Combines all ML model signals
Meta-learner: Weighted ensemble of all predictions
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class TradeSignal(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class CombinedSignal:
    """Combined signal from all models"""
    symbol: str
    primary_signal: str
    confidence: float
    consensus: float
    models_agreeing: int
    total_models: int
    breakdown: Dict[str, Any]


class SignalFusion:
    """
    Meta-learner: Combines predictions from:
    - DirectionalPredictor
    - RegimeClassifier  
    - SentimentModel
    - VolatilityPredictor
    - Technical indicators
    """
    
    DEFAULT_WEIGHTS = {
        "directional": 0.25,
        "rsi": 0.10,
        "macd": 0.10,
        "bollinger": 0.10,
        "regime": 0.10,
        "sentiment": 0.15,
        "volatility": 0.10,
        "atr": 0.05,
        "stochastic": 0.05
    }
    
    def __init__(self, symbol: str = "SPY", weights: Dict[str, float] = None):
        self.symbol = symbol
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.model_predictions = {}
        
    def add_prediction(self, model_name: str, prediction: Any, confidence: float):
        """Add a model prediction to the ensemble"""
        self.model_predictions[model_name] = {
            "prediction": prediction,
            "confidence": confidence
        }
    
    def _convert_to_score(self, prediction: Any) -> float:
        """Convert any prediction to a -1 to 1 score"""
        
        if isinstance(prediction, str):
            # Convert string to score
            lower = prediction.lower()
            if "long" in lower or "bullish" in lower or "buy" in lower:
                return 1.0
            elif "short" in lower or "bearish" in lower or "sell" in lower:
                return -1.0
            else:
                return 0.0
                
        elif isinstance(prediction, (int, float)):
            return float(prediction)
            
        elif isinstance(prediction, dict):
            # Handle dict predictions
            if "direction" in prediction:
                d = prediction["direction"].upper()
                if "LONG" in d or "BUY" in d:
                    return 1.0
                elif "SHORT" in d or "SELL" in d:
                    return -1.0
            if "sentiment" in prediction:
                s = prediction["sentiment"].lower()
                if "bul" in s:
                    return 1.0
                elif "bear" in s:
                    return -1.0
            if "signal" in prediction:
                sig = prediction["signal"].lower()
                if "bullish" in sig or "buy" in sig or "long" in sig:
                    return 1.0
                elif "bearish" in sig or "sell" in sig or "short" in sig:
                    return -1.0
            if "regime" in prediction:
                r = prediction["regime"].lower()
                if "bull" in r:
                    return 0.5
                elif "bear" in r:
                    return -0.5
            return 0.0
            
        else:
            return 0.0
    
    def combine(self) -> CombinedSignal:
        """Combine all signals into final prediction"""
        
        if not self.model_predictions:
            return CombinedSignal(
                symbol=self.symbol,
                primary_signal="HOLD",
                confidence=0.5,
                consensus=0.0,
                models_agreeing=0,
                total_models=0,
                breakdown={}
            )
        
        # Calculate weighted score
        total_weight = 0
        weighted_score = 0
        breakdown = {}
        
        for model_name in self.weights:
            if model_name in self.model_predictions:
                pred_data = self.model_predictions[model_name]
                weight = self.weights[model_name]
                
                score = self._convert_to_score(pred_data["prediction"])
                confidence = pred_data["confidence"]
                
                weighted_score += score * weight * confidence
                total_weight += weight
                
                breakdown[model_name] = {
                    "prediction": pred_data["prediction"],
                    "score": score,
                    "weight": weight,
                    "contribution": score * weight * confidence
                }
        
        if total_weight == 0:
            return CombinedSignal(
                symbol=self.symbol,
                primary_signal="HOLD",
                confidence=0.5,
                consensus=0.0,
                models_agreeing=0,
                total_models=len(self.model_predictions),
                breakdown=breakdown
            )
        
        # Normalize
        normalized_score = weighted_score / total_weight
        
        # Determine signal
        if normalized_score > 0.3:
            primary = "STRONG_BUY" if normalized_score > 0.6 else "BUY"
        elif normalized_score < -0.3:
            primary = "STRONG_SELL" if normalized_score < -0.6 else "SELL"
        else:
            primary = "HOLD"
        
        # Consensus (how many models agree on direction)
        positive_votes = 0
        negative_votes = 0
        
        for model_name, data in self.model_predictions.items():
            score = self._convert_to_score(data["prediction"])
            if score > 0.2:
                positive_votes += 1
            elif score < -0.2:
                negative_votes += 1
                
        total_models = len(self.model_predictions)
        models_agreeing = max(positive_votes, negative_votes)
        consensus = models_agreeing / total_models if total_models > 0 else 0
        
        # Confidence
        confidence = min(abs(normalized_score) * 0.5 + 0.5, 0.95)
        
        return CombinedSignal(
            symbol=self.symbol,
            primary_signal=primary,
            confidence=confidence,
            consensus=consensus,
            models_agreeing=models_agreeing,
            total_models=total_models,
            breakdown=breakdown
        )
    
    def should_trade(self, min_confidence: float = 0.55) -> bool:
        """Determine if we should take the trade"""
        
        signal = self.combine()
        
        # Must meet confidence threshold
        if signal.confidence < min_confidence:
            return False
            
        # Must be a non-zero signal
        if signal.primary_signal == "HOLD":
            return False
            
        # Need consensus
        if signal.consensus < 0.4:
            return False
            
        return True
    
    def get_position_size_multiplier(self) -> float:
        """Scale position size based on conviction"""
        
        signal = self.combine()
        
        # Base on confidence and consensus
        base = signal.confidence * signal.consensus
        
        # Strong signals get larger positions
        multiplier = {
            "STRONG_BUY": 1.0,
            "BUY": 0.75,
            "HOLD": 0.0,
            "SELL": 0.75,
            "STRONG_SELL": 1.0
        }.get(signal.primary_signal, 0.5)
        
        return base * multiplier


def fuse_signals(symbol: str, **predictions) -> CombinedSignal:
    """Convenience function to fuse signals"""
    
    fusion = SignalFusion(symbol)
    
    for model_name, data in predictions.items():
        if isinstance(data, dict):
            prediction = data.get("prediction", data.get("direction", "neutral"))
            confidence = data.get("confidence", 0.5)
        else:
            prediction = data
            confidence = 0.5
            
        fusion.add_prediction(model_name, prediction, confidence)
    
    return fusion.combine()


if __name__ == "__main__":
    # Test signal fusion
    print("Signal Fusion Test:\n")
    
    predictions = {
        "directional": {"prediction": "LONG", "confidence": 0.70},
        "rsi": {"prediction": "oversold", "confidence": 0.65},
        "macd": {"prediction": "bullish_cross", "confidence": 0.60},
        "regime": {"prediction": "bull", "confidence": 0.75},
        "sentiment": {"prediction": "bullish", "confidence": 0.68},
    }
    
    fused = fuse_signals("SPY", **predictions)
    
    print(f"Symbol: {fused.symbol}")
    print(f"Primary Signal: {fused.primary_signal}")
    print(f"Confidence: {fused.confidence:.1%}")
    print(f"Consensus: {fused.consensus:.1%}")
    print(f"Models Agreeing: {fused.models_agreeing}/{fused.total_models}")
    
    print(f"\nShould Trade: {fused.should_trade()}")
    print(f"Position Multiplier: {fused.get_position_size_multiplier():.2f}")