"""
Database Models for MacroEdge
SQLAlchemy models for all data entities.
"""

import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, Index, Enum
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class EventType(str, enum.Enum):
    GEOPOLITICAL = "geopolitical"
    MONETARY = "monetary"
    SUPPLY_CHAIN = "supply_chain"
    NATURAL_DISASTER = "disaster"
    EARNINGS = "earnings"


class MarketRegime(str, enum.Enum):
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    TRANSITIONAL = "transitional"


class SignalDirection(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    HOLD = "hold"


class NewsArticle(Base):
    """News articles with sentiment scores."""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True)
    headline = Column(String(500), nullable=False)
    summary = Column(Text)
    source = Column(String(100))
    url = Column(String(500), unique=True)
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Sentiment
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_label = Column(Enum(SignalDirection))  # positive/negative/neutral
    
    # Entity extraction
    entities_json = Column(Text)  # Extracted tickers/commodities
    
    # Classification
    event_type = Column(Enum(EventType))
    
    def __repr__(self):
        return f"<News {self.id}: {self.headline[:50]}...>"


class PriceData(Base):
    """OHLCV price data for assets."""
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # Computed
    returns = Column(Float)  # Daily return
    log_return = Column(Float)
    
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'timestamp'),
    )


class TechnicalFeatures(Base):
    """Precomputed technical indicators."""
    __tablename__ = "technical_features"
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Trend
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    
    # Momentum
    rsi_14 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    
    # Volatility
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    bb_mid = Column(Float)
    atr_14 = Column(Float)
    
    # Volume
    volume_zscore = Column(Float)
    obv = Column(Float)  # On-balance volume
    
    # Custom
    returns_1d = Column(Float)
    returns_5d = Column(Float)
    returns_20d = Column(Float)
    momentum_12m_1m = Column(Float)  # 12-1 month


class TradeSignal(Base):
    """Generated trading signals."""
    __tablename__ = "trade_signals"
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Prediction
    horizon_days = Column(Integer)  # 3, 5, or 7
    direction = Column(Enum(SignalDirection))
    confidence = Column(Float)  # 0-1
    
    # Components
    technical_score = Column(Float)
    sentiment_score = Column(Float)
    macro_score = Column(Float)
    fused_score = Column(Float)
    
    # Position
    position_size = Column(Float)  # Kelly-sized
    expected_return = Column(Float)
    
    # Status
    executed = Column(Boolean, default=False)
    executed_at = Column(DateTime)
    
    # P&L
    actual_return = Column(Float)
    
    __table_args__ = (
        Index('idx_ticker_gen', 'ticker', 'generated_at'),
    )


class Portfolio(Base):
    """Portfolio positions and history."""
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Holdings snapshot
    holdings_json = Column(Text)  # {ticker: weight}
    
    # Performance
    total_value = Column(Float)
    daily_pnl = Column(Float)
    total_return = Column(Float)
    
    # Risk metrics
    portfolio_vol = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    var_95 = Column(Float)


class ModelMetrics(Base):
    """Model performance tracking."""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1 = Column(Float)
    auc_roc = Column(Float)
    sharpe = Column(Float)
    win_rate = Column(Float)
    
    # Dataset info
    train_samples = Column(Integer)
    test_samples = Column(Integer)


class DailyLog(Base):
    """Daily system logs for Claude analysis."""
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Summary data
    portfolio_summary_json = Column(Text)
    signals_json = Column(Text)
    risk_metrics_json = Column(Text)
    model_performance_json = Column(Text)
    
    # Claude analysis
    claude_report = Column(Text)
    
    # Alerts
    has_alerts = Column(Boolean, default=False)


def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)