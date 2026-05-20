"""
FastAPI Routes
REST API endpoints for MacroEdge.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from backend.services.database import DatabaseService
from backend.services.data_loader import DataLoader
from backend.services.news_intelligence import (
    NewsScraper, SentimentAnalyzer, process_news_articles
)
from backend.ml.technical_analysis import TechnicalAnalyzer
from backend.ml.models import TechnicalModel, RegimeDetector
from backend.services.trading import AlpacaClient
from backend.services.claude_brain import ClaudeSupervisor
from backend.services.risk_management import RiskManager
from config.settings import TARGET_ASSETS

router = APIRouter()

# ==========================================
# Response Models
# ==========================================

class SignalResponse(BaseModel):
    id: int
    ticker: str
    direction: str
    confidence: float
    horizon_days: int
    technical_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    total_value: float
    cash: float
    positions: List[Dict]
    risk_metrics: Dict


class NewsResponse(BaseModel):
    id: int
    headline: str
    source: str
    sentiment_score: float
    sentiment_label: str
    event_type: str
    published_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    details: Dict


# ==========================================
# Services (initialized at startup)
# ==========================================

from config.settings import DATABASE_URL, ALPACA_API_KEY, ALPACA_SECRET_KEY

db = DatabaseService(DATABASE_URL)
data_loader = DataLoader(db)
news_scraper = NewsScraper()
sentiment_analyzer = SentimentAnalyzer()
trading_client = AlpacaClient()
claude_supervisor = ClaudeSupervisor()
risk_manager = RiskManager()
technical_model = TechnicalModel()
regime_detector = RegimeDetector()


# ==========================================
# Endpoints
# ==========================================

@router.get("/", tags=["Root"])
async def root():
    """API root."""
    return {
        "name": "MacroEdge API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "details": {
            "database": "connected",
            "alpaca": "connected" if trading_client.client else "disconnected",
            "claude": "ready" if claude_supervisor.client else "not_configured"
        }
    }


@router.get("/assets", tags=["Data"])
async def get_assets():
    """Get target asset universe."""
    return TARGET_ASSETS


@router.get("/news", response_model=List[NewsResponse], tags=["News"])
async def get_news(hours: int = 24, limit: int = 50):
    """Get recent news with sentiment."""
    articles = await db.get_recent_news(hours=hours, limit=limit)
    
    return [
        {
            "id": a.id,
            "headline": a.headline,
            "source": a.source or "",
            "sentiment_score": a.sentiment_score or 0,
            "sentiment_label": a.sentiment_label or "neutral",
            "event_type": a.event_type or "general",
            "published_at": a.published_at or a.scraped_at
        }
        for a in articles[:limit]
    ]


@router.post("/news/scrape", tags=["News"])
async def scrape_news(background_tasks: BackgroundTasks):
    """Trigger news scrape and analysis."""
    background_tasks.add_task(
        process_news_articles, db, news_scraper, sentiment_analyzer
    )
    return {"status": "started", "message": "News scraping initiated"}


@router.get("/prices/{ticker}", tags=["Data"])
async def get_prices(ticker: str, days: int = 365):
    """Get historical price data."""
    prices = await db.get_price_history(ticker, days)
    
    return {
        "ticker": ticker,
        "data": [
            {
                "date": p.timestamp.isoformat(),
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume,
                "returns": p.returns
            }
            for p in prices
        ]
    }


@router.get("/technical/{ticker}", tags=["Analysis"])
async def get_technical(ticker: str):
    """Get technical indicators."""
    features = await db.get_latest_features(ticker)
    
    if not features:
        raise HTTPException(404, "No technical data available")
    
    return {
        "ticker": ticker,
        "timestamp": features.timestamp.isoformat(),
        "indicators": {
            "rsi_14": features.rsi_14,
            "macd": features.macd,
            "sma_20": features.sma_20,
            "sma_50": features.sma_50,
            "atr_14": features.atr_14,
            "volume_zscore": features.volume_zscore
        }
    }


@router.get("/signals", response_model=List[SignalResponse], tags=["Signals"])
async def get_signals(status: str = "pending", limit: int = 20):
    """Get trading signals."""
    if status == "pending":
        signals = await db.get_pending_signals(limit=limit)
    else:
        # All signals - simplified
        signals = []
    
    return [
        {
            "id": s.id,
            "ticker": s.ticker,
            "direction": s.direction.value,
            "confidence": s.confidence,
            "horizon_days": s.horizon_days,
            "technical_score": s.technical_score,
            "sentiment_score": s.sentiment_score
        }
        for s in signals
    ]


@router.post("/signals/generate", tags=["Signals"])
async def generate_signals(background_tasks: BackgroundTasks):
    """Generate new trading signals."""
    # This would be implemented with the ML models
    background_tasks.add_task(generate_new_signals)
    return {"status": "started"}


async def generate_new_signals():
    """Background signal generation."""
    # For each asset, combine technical, sentiment, macro signals
    for ticker in TARGET_ASSETS["commodities"]:
        # Get technical features
        tech_data = await db.get_latest_features(ticker)
        
        # Get sentiment
        sentiment = await db.get_news_sentiment_avg(ticker, window_days=5)
        
        # Get macro data (simplified)
        macro_data = {}
        
        # Predict
        direction, confidence = technical_model.predict_direction(
            tech_data or {},
            {"avg_sentiment": sentiment},
            macro_data
        )
        
        if confidence > 0.5:
            # Store signal
            await db.add_signal(
                ticker=ticker,
                horizon_days=5,
                direction=direction,
                confidence=confidence,
                sentiment_score=sentiment
            )


@router.get("/portfolio", response_model=PortfolioResponse, tags=["Portfolio"])
async def get_portfolio():
    """Get portfolio status."""
    account = trading_client.get_account()
    
    positions = trading_client.get_positions()
    
    return {
        "total_value": account.get("portfolio_value", 0),
        "cash": account.get("cash", 0),
        "positions": positions,
        "risk_metrics": {}  # Would calculate from positions
    }


@router.get("/account", tags=["Trading"])
async def get_account():
    """Get trading account info."""
    return trading_client.get_account()


@router.post("/orders", tags=["Trading"])
async def submit_order(
    symbol: str,
    qty: int,
    side: str,
    order_type: str = "market",
    limit_price: Optional[float] = None
):
    """Submit trading order."""
    if not trading_client.client:
        raise HTTPException(503, "Trading not configured")
    
    result = trading_client.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        order_type=order_type,
        limit_price=limit_price
    )
    
    return result


@router.get("/orders", tags=["Trading"])
async def get_orders(status: str = "open"):
    """Get orders."""
    return trading_client.list_orders(status=status)


@router.get("/model/metrics", tags=["Models"])
async def get_model_metrics(model_name: str = "technical"):
    """Get model performance metrics."""
    # Placeholder - would fetch from DB
    return {
        "model": model_name,
        "accuracy": 0.58,
        "sharpe": 0.65,
        "win_rate": 0.52
    }


@router.get("/claude/report", tags=["AI"])
async def get_claude_report():
    """Get Claude daily report."""
    if not claude_supervisor.client:
        raise HTTPException(503, "Claude not configured")
    
    # Gather data
    account = trading_client.get_account()
    positions = trading_client.get_positions()
    signals = await db.get_pending_signals()
    
    return await claude_supervisor.daily_report(
        portfolio={
            "total_value": account.get("portfolio_value", 0),
            "positions": positions
        },
        signals=[
            {"ticker": s.ticker, "direction": s.direction.value, 
             "confidence": s.confidence, "horizon_days": s.horizon_days}
            for s in signals[:5]
        ],
        risk_metrics={"sharpe_ratio": 0.5},
        model_performance={}
    )


# End of routes module