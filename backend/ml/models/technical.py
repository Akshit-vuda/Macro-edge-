"""
Technical Indicators Module
RSI, MACD, BollingerBands, MovingAverages
"""

import numpy as np
from typing import Tuple, Dict, List


class TechnicalIndicators:
    """
    Calculate all technical indicators for trading
    """
    
    @staticmethod
    def calculate_rsi(prices: np.ndarray, period: int = 14) -> Tuple[float, str]:
        """
        Calculate RSI indicator
        Returns: (rsi_value, signal)
        """
        if len(prices) < period + 1:
            return 50.0, "neutral"
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Use EMA for smoothing
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0, "overbought"
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Signal
        if rsi > 70:
            signal = "overbought"
        elif rsi < 30:
            signal = "oversold"
        else:
            signal = "neutral"
            
        return rsi, signal
    
    @staticmethod
    def calculate_macd(prices: np.ndarray, 
                    fast: int = 12, 
                    slow: int = 26, 
                    signal: int = 9) -> Dict:
        """
        Calculate MACD
        Returns: macd line, signal line, histogram
        """
        if len(prices) < slow:
            return {"macd": 0, "signal": 0, "histogram": 0, "cross": "neutral"}
            
        # EMAs
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        macd = macd_line.iloc[-1]
        sig = signal_line.iloc[-1]
        hist = histogram.iloc[-1]
        
        # Cross signal
        if hist > 0.1:
            cross = "bullish_cross"
        elif hist < -0.1:
            cross = "bearish_cross"
        else:
            cross = "neutral"
            
        return {
            "macd": float(macd),
            "signal": float(sig),
            "histogram": float(hist),
            "cross": cross
        }
    
    @staticmethod
    def calculate_bollinger(prices: np.ndarray, 
                          period: int = 20, 
                          std_dev: float = 2.0) -> Dict:
        """
        Calculate Bollinger Bands
        Returns: upper, middle, lower, position
        """
        if len(prices) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "position": 50}
            
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        upper_val = upper.iloc[-1]
        middle_val = middle.iloc[-1]
        lower_val = lower.iloc[-1]
        current = prices.iloc[-1]
        
        # Position within bands (0-100)
        position = ((current - lower_val) / (upper_val - lower_val + 1e-10)) * 100
        
        return {
            "upper": float(upper_val),
            "middle": float(middle_val),
            "lower": float(lower_val),
            "position": float(position),
            "signal": "long" if position < 20 else "short" if position > 80 else "neutral"
        }
    
    @staticmethod
    def calculate_sma(prices: np.ndarray, periods: List[int] = [20, 50, 200]) -> Dict:
        """
        Simple Moving Averages
        """
        smas = {}
        for p in periods:
            if len(prices) >= p:
                smas[f"sma_{p}"] = float(prices.rolling(window=p).mean().iloc[-1])
            else:
                smas[f"sma_{p}"] = None
        return smas
    
    @staticmethod
    def calculate_ema(prices: np.ndarray, periods: List[int] = [12, 26, 50]) -> Dict:
        """
        Exponential Moving Averages
        """
        emas = {}
        for p in periods:
            if len(prices) >= p:
                emas[f"ema_{p}"] = float(prices.ewm(span=p, adjust=False).mean().iloc[-1])
            else:
                emas[f"ema_{p}"] = None
        return emas
    
    @staticmethod
    def calculate_atr(highs: np.ndarray, 
                     lows: np.ndarray, 
                     closes: np.ndarray,
                     period: int = 14) -> float:
        """
        Average True Range
        """
        trs = []
        for i in range(1, len(closes)):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr = max(hl, hc, lc)
            trs.append(tr)
            
        if len(trs) < period:
            return 0.0
            
        return np.mean(trs[-period:])
    
    @staticmethod
    def calculate_stochastic(highs: np.ndarray, 
                         lows: np.ndarray,
                         closes: np.ndarray,
                         period: int = 14) -> Tuple[float, float]:
        """
        Stochastic Oscillator: %K, %D
        """
        if len(closes) < period:
            return 50.0, 50.0
            
        lowest_low = lows.rolling(window=period).min()
        highest_high = highs.rolling(window=period).max()
        
        k = 100 * (closes - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=3).mean()
        
        return float(k.iloc[-1]), float(d.iloc[-1])


class IndicatorPredictor:
    """
    Predict next indicator values
    """
    
    def __init__(self, symbol: str = "SPY"):
        self.symbol = symbol
        
    def predict_rsi_next(self, prices: np.ndarray) -> Dict:
        """Predict next RSI"""
        current_rsi, _ = TechnicalIndicators.calculate_rsi(prices)
        
        # Simulate small drift
        drift = np.random.uniform(-5, 5)
        next_rsi = max(0, min(100, current_rsi + drift))
        
        return {
            "current_rsi": current_rsi,
            "predicted_rsi": next_rsi,
            "signal": "oversold" if next_rsi < 30 else "overbought" if next_rsi > 70 else "neutral"
        }
    
    def predict_macd_next(self, prices: np.ndarray) -> Dict:
        """Predict next MACD"""
        current = TechnicalIndicators.calculate_macd(prices)
        
        # Predict histogram direction
        hist_drift = np.random.uniform(-0.5, 0.5)
        
        return {
            "current_histogram": current["histogram"],
            "predicted_histogram": current["histogram"] + hist_drift,
            "cross": current["cross"]
        }
    
    def predict_bollinger_next(self, prices: np.ndarray) -> Dict:
        """Predict next Bollinger position"""
        current = TechnicalIndicators.calculate_bollinger(prices)
        
        # Predict position drift
        pos_drift = np.random.uniform(-10, 10)
        next_pos = max(0, min(100, current["position"] + pos_drift))
        
        return {
            "current_position": current["position"],
            "predicted_position": next_pos,
            "signal": current["signal"]
        }


# Convenience functions
def get_indicators(symbol: str, prices: list, highs: list = None, lows: list = None) -> dict:
    """Get all indicators"""
    import pandas as pd
    
    prices = pd.Series(prices)
    
    result = {
        "symbol": symbol,
        "rsi": {},
        "macd": {},
        "bollinger": {},
        "sma": {},
        "ema": {}
    }
    
    # RSI
    rsi, signal = TechnicalIndicators.calculate_rsi(prices)
    result["rsi"] = {"value": rsi, "signal": signal}
    
    # MACD
    result["macd"] = TechnicalIndicators.calculate_macd(prices)
    
    # Bollinger
    result["bollinger"] = TechnicalIndicators.calculate_bollinger(prices)
    
    # SMAs
    result["sma"] = TechnicalIndicators.calculate_sma(prices)
    
    # EMAs
    result["ema"] = TechnicalIndicators.calculate_ema(prices)
    
    return result


if __name__ == "__main__":
    import pandas as pd
    
    np.random.seed(42)
    prices = pd.Series(200 + np.cumsum(np.random.randn(300)))
    
    print("Technical Indicators:")
    ind = get_indicators("SPY", prices.tolist())
    
    for section, values in ind.items():
        if isinstance(values, dict):
            print(f"\n{section.upper()}:")
            for k, v in values.items():
                print(f"  {k}: {v}")