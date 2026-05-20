"""
Technical Analysis Module
Compute technical indicators for trading signals.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # EMA
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(
    prices: pd.Series, 
    fast: int = 12, 
    slow: int = 26, 
    signal: int = 9
) -> Dict[str, pd.Series]:
    """Calculate MACD."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    
    return {
        'macd': macd,
        'signal': macd_signal,
        'hist': macd_hist
    }


def calculate_bollinger_bands(
    prices: pd.Series, 
    period: int = 20, 
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return {
        'upper': upper,
        'mid': sma,
        'lower': lower
    }


def calculate_atr(
    high: pd.Series, 
    low: pd.Series, 
    close: pd.Series, 
    period: int = 14
) -> pd.Series:
    """Calculate Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Calculate On-Balance Volume."""
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def calculate_volume_zscore(volume: pd.Series, window: int = 20) -> pd.Series:
    """Calculate volume z-score."""
    rolling_mean = volume.rolling(window=window).mean()
    rolling_std = volume.rolling(window=window).std()
    
    zscore = (volume - rolling_mean) / rolling_std
    return zscore


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return prices.rolling(window=period).mean()


def calculate_returns(
    prices: pd.Series, 
    periods: List[int] = [1, 5, 20, 60]
) -> Dict[str, pd.Series]:
    """Calculate returns over various periods."""
    returns = {}
    for p in periods:
        returns[f'{p}d'] = prices.pct_change(periods=p)
    
    return returns


def calculate_momentum(
    prices: pd.Series, 
    period: int = 252
) -> pd.Series:
    """Calculate 12-1 month momentum."""
    return (prices / prices.shift(period - 21)) - 1  # Approx 12-1 month


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3
) -> Dict[str, pd.Series]:
    """Calculate Stochastic Oscillator."""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()
    
    return {'k': k, 'd': d}


class TechnicalAnalyzer:
    """
    Compute all technical indicators for an asset.
    """
    
    def __init__(self):
        pass
    
    def compute_all(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compute all technical features.
        Expects DataFrame with columns: open, high, low, close, volume
        """
        df = data.copy()
        
        close = df['close'] if 'close' in df else df['_close']
        high = df['high'] if 'high' in df else df['_high']
        low = df['low'] if 'low' in df else df['_low']
        volume = df['volume'] if 'volume' in df else df['_volume']
        
        results = df.copy()
        
        # Trend indicators
        results['sma_20'] = calculate_sma(close, 20)
        results['sma_50'] = calculate_sma(close, 50)
        results['sma_200'] = calculate_sma(close, 200)
        
        # Momentum
        results['rsi_14'] = calculate_rsi(close, 14)
        
        macd = calculate_macd(close)
        results['macd'] = macd['macd']
        results['macd_signal'] = macd['signal']
        results['macd_hist'] = macd['hist']
        
        # Volatility
        bb = calculate_bollinger_bands(close)
        results['bb_upper'] = bb['upper']
        results['bb_mid'] = bb['mid']
        results['bb_lower'] = bb['lower']
        
        results['atr_14'] = calculate_atr(high, low, close, 14)
        
        # Volume
        results['obv'] = calculate_obv(close, volume)
        results['volume_zscore'] = calculate_volume_zscore(volume, 20)
        
        # Returns
        returns = calculate_returns(close)
        results['returns_1d'] = returns['1d']
        results['returns_5d'] = returns['5d']
        results['returns_20d'] = returns['20d']
        
        # Momentum
        results['momentum_12m_1m'] = calculate_momentum(close)
        
        # Stochastic
        stoch = calculate_stochastic(high, low, close)
        results['stoch_k'] = stoch['k']
        results['stoch_d'] = stoch['d']
        
        return results
    
    def compute_features_dict(
        self,
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Compute features and return as dict (latest values).
        """
        tech_df = self.compute_all(data)
        
        # Get latest row
        latest = tech_df.iloc[-1]
        
        features = {}
        
        # Simple features
        feature_cols = [
            'sma_20', 'sma_50', 'sma_200', 'rsi_14',
            'macd', 'macd_signal', 'macd_hist',
            'bb_upper', 'bb_mid', 'bb_lower', 'atr_14',
            'obv', 'volume_zscore',
            'returns_1d', 'returns_5d', 'returns_20d',
            'momentum_12m_1m', 'stoch_k', 'stoch_d'
        ]
        
        for col in feature_cols:
            if col in latest:
                val = latest[col]
                if pd.notna(val):
                    features[col] = float(val)
        
        # Additional derived features
        close = latest.get('close')
        if close:
            # Price position in BB
            bb_upper = latest.get('bb_upper')
            bb_lower = latest.get('bb_lower')
            if bb_upper and bb_lower and bb_upper != bb_lower:
                features['bb_position'] = (close - bb_lower) / (bb_upper - bb_lower)
            
            # SMAs trend
            sma_20 = latest.get('sma_20')
            sma_50 = latest.get('sma_50')
            sma_200 = latest.get('sma_200')
            
            if sma_20 and sma_50:
                features['sma_20_50_ratio'] = close / sma_20 if sma_20 else 0
            if sma_50 and sma_200:
                features['sma_50_200_ratio'] = sma_50 / sma_200 if sma_200 else 0
        
        return features


async def compute_technical_features(
    db,
    ticker: str,
    data_loader
) -> Dict[str, float]:
    """
    Compute technical features for ticker.
    Wrapper function.
    """
    analyzer = TechnicalAnalyzer()
    
    # Get price data
    df = await data_loader.get_price_df(ticker, days=300)
    
    if df.empty:
        logger.warning(f"No price data for {ticker}")
        return {}
    
    # Compute
    return analyzer.compute_features_dict(df)