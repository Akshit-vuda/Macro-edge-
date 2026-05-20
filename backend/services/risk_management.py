"""
Risk Management Module
Position sizing, Kelly Criterion, and risk guards.
"""

import logging
import numpy as np
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# Risk parameters
MAX_POSITION_SIZE = 0.02  # 2% max per trade
MAX_SECTOR_CONCENTRATION = 0.20  # 20% max sector
DRAWDOWN_KILL_SWITCH = -0.08  # -8% drawdown
MIN_SIGNAL_CONFIDENCE = 0.55


def kelly_criterion(
    win_rate: float,
    avg_win: float,
    avg_loss: float = None,
    fraction: float = 1.0
) -> float:
    """
    Calculate Kelly Criterion position size.
    
    Args:
        win_rate: Probability of winning (0-1)
        avg_win: Average win amount
        avg_loss: Average loss amount (negative)
        fraction: Kelly fraction (0.5 = half-Kelly)
    
    Returns:
        Optimal position size as fraction of portfolio
    """
    if win_rate <= 0 or win_rate >= 1:
        return 0
    
    # Calculate odds
    if avg_loss is None:
        avg_loss = -avg_win  # Assume symmetric
    
    odds = avg_win / abs(avg_loss) if avg_loss != 0 else 1
    
    # Kelly formula: f* = (bp - q) / b
    # b = odds, p = win probability, q = 1-p
    b = odds
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    
    # Apply fraction (typically half-Kelly)
    kelly *= fraction
    
    # Normalize to portfolio percentage
    position_pct = kelly * MAX_POSITION_SIZE
    
    # Bounds
    return max(0, min(position_pct, MAX_POSITION_SIZE))


def fractional_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float = None,
    fraction: float = 0.5
) -> float:
    """Half-Kelly for more conservative sizing."""
    return kelly_criterion(win_rate, avg_win, avg_loss, fraction)


class RiskManager:
    """
    Comprehensive risk management.
    """
    
    def __init__(
        self,
        max_position: float = MAX_POSITION_SIZE,
        max_drawdown: float = DRAWDOWN_KILL_SWITCH,
        max_sector: float = MAX_SECTOR_CONCENTRATION
    ):
        self.max_position = max_position
        self.max_drawdown = max_drawdown
        self.max_sector = max_sector
        
        self.position_sizes = {}  # {ticker: weight}
        self.sector_weights = {}  # {sector: weight}
        
        # Tracking
        self.daily_losses = []
        self.peak_value = 0
        self.current_drawdown = 0
    
    def check_position_size(
        self,
        ticker: str,
        proposed_size: float,
        portfolio_value: float
    ) -> float:
        """
        Check and adjust position size.
        """
        pct = proposed_size / portfolio_value
        
        if pct > self.max_position:
            logger.warning(
                f"Position {ticker} exceeds max ({pct:.1%} > {self.max_position:.1%})"
            )
            return portfolio_value * self.max_position
        
        return proposed_size
    
    def check_sector_concentration(
        self,
        sector: str,
        proposed_size: float,
        portfolio_value: float
    ) -> float:
        """
        Check sector concentration.
        """
        current = self.sector_weights.get(sector, 0)
        
        proposal = (current + proposed_size) / portfolio_value
        
        if proposal > self.max_sector:
            excess = proposal - self.max_sector
            adjustment = portfolio_value * excess
            adjusted = proposed_size - adjustment
            
            logger.warning(
                f"Sector {sector} exceeds max - adjusting: {proposal:.1%} -> {adjusted/portfolio_value:.1%}"
            )
            
            return adjusted
        
        return proposed_size
    
    def calculate_var(
        self,
        returns: List[float],
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk.
        """
        if not returns:
            return 0
        
        returns = np.array(returns)
        
        # Parametric VaR
        mu = np.mean(returns)
        sigma = np.std(returns)
        
        # z-score for confidence level
        from scipy import stats
        z = stats.norm.ppf(1 - confidence)
        
        var = mu + sigma * z
        
        return var
    
    def calculate_max_drawdown(
        self,
        equity_curve: List[float]
    ) -> float:
        """
        Calculate maximum drawdown from equity curve.
        """
        if not equity_curve:
            return 0
        
        values = np.array(equity_curve)
        
        # Running maximum
        running_max = np.maximum.accumulate(values)
        
        # Drawdown
        drawdowns = (values - running_max) / running_max
        
        return np.min(drawdowns)
    
    def check_drawdown_kill_switch(
        self,
        portfolio_value: float,
        killswitch: float = None
    ) -> bool:
        """
        Check if kill switch triggered.
        """
        if self.peak_value == 0:
            self.peak_value = portfolio_value
            return False
        
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        
        drawdown = (portfolio_value - self.peak_value) / self.peak_value
        self.current_drawdown = drawdown
        
        threshold = killswitch or self.max_drawdown
        
        if drawdown < threshold:
            logger.critical(
                f"DRAWDOWN KILL SWITCH TRIGGERED: {drawdown:.1%} < {threshold:.1%}"
            )
            return True
        
        return False
    
    def calculate_portfolio_risk(
        self,
        positions: List[Dict],
        returns_history: List[float]
    ) -> Dict[str, float]:
        """
        Calculate portfolio-level risk metrics.
        """
        # Volatility
        vol = np.std(returns_history) if returns_history else 0
        
        # Sharpe (assumes 0% risk-free for simplicity)
        returns_mean = np.mean(returns_history) if returns_history else 0
        sharpe = returns_mean / vol if vol > 0 else 0
        
        # VaR
        var95 = self.calculate_var(returns_history, 0.95)
        
        # Max DD
        max_dd = self.calculate_max_drawdown(returns_history)
        
        return {
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'var_95': var95,
            'max_drawdown': max_dd
        }
    
    def validate_trade(
        self,
        ticker: str,
        sector: str,
        proposed_size: float,
        portfolio_value: float,
        confidence: float
    ) -> tuple:
        """
        Complete trade validation.
        Returns: (approved: bool, size: float, reason: str)
        """
        # Check confidence
        if confidence < MIN_SIGNAL_CONFIDENCE:
            return False, 0, f"Confidence too low: {confidence:.0%} < {MIN_SIGNAL_CONFIDENCE:.0%}"
        
        # Check position size
        size = self.check_position_size(ticker, proposed_size, portfolio_value)
        if size < proposed_size:
            return True, size, "Reduced due to max position"
        
        # Check sector concentration
        size = self.check_sector_concentration(sector, proposed_size, portfolio_value)
        if size < proposed_size:
            return True, size, "Reduced due to sector concentration"
        
        # Check drawdown
        if self.current_drawdown < self.max_drawdown * 0.5:
            return True, size, "Near drawdown threshold - reduced"
        
        return True, size, "Approved"
    
    def get_rebalance_recommendations(
        self,
        positions: List[Dict],
        target_weights: Dict[str, float]
    ) -> List[Dict]:
        """
        Get rebalancing recommendations.
        """
        recs = []
        
        for ticker, target in target_weights.items():
            current = next(
                (p for p in positions if p['ticker'] == ticker), 
                {'weight': 0}
            ).get('weight', 0)
            
            diff = target - current
            
            if abs(diff) > 0.01:  # 1% threshold
                recs.append({
                    'ticker': ticker,
                    'action': 'buy' if diff > 0 else 'sell',
                    'size': abs(diff),
                    'reason': f"rebalance to {target:.1%}"
                })
        
        return recs


def calculate_expected_return(
    direction: str,
    horizon_days: int,
    confidence: float,
    base_return: float = 0.02
) -> float:
    """
    Estimate expected return for signal.
    """
    # Scale by confidence and horizon
    mult = confidence * (horizon_days / 5)  # Normalize to 5 days
    
    if direction == "up":
        return base_return * mult
    else:
        return -base_return * mult * 0.5  # Downside is smaller


def assess_signal_quality(
    technical_score: float,
    sentiment_score: float,
    macro_score: float,
    confidence: float
) -> str:
    """
    Overall signal quality assessment.
    """
    scores = [technical_score, sentiment_score, macro_score, confidence]
    avg = np.mean(scores)
    
    if avg > 0.7:
        return "strong"
    elif avg > 0.5:
        return "moderate"
    elif avg > 0.3:
        return "weak"
    else:
        return "very_weak"