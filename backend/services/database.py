"""
Database Service for MacroEdge
Async database operations using SQLAlchemy.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import sessionmaker

from ..models import database as db
from config.settings import DATABASE_URL


class DatabaseService:
    """Async database operations."""
    
    def __init__(self, url: str = None):
        self.url = url or DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
        self.engine = create_async_engine(self.url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_tables(self):
        """Initialize all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Get async session."""
        return self.async_session()
    
    # ============ NEWS ARTICLES ============
    
    async def add_news_article(
        self,
        headline: str,
        source: str,
        url: str,
        summary: str = None,
        published_at: datetime = None,
        sentiment_score: float = None,
        sentiment_label: str = None,
        entities: List[str] = None,
        event_type: str = None
    ) -> db.NewsArticle:
        """Add news article."""
        async with await self.get_session() as session:
            article = db.NewsArticle(
                headline=headline,
                summary=summary,
                source=source,
                url=url,
                published_at=published_at or datetime.utcnow(),
                scraped_at=datetime.utcnow(),
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                entities_json=json.dumps(entities) if entities else None,
                event_type=event_type
            )
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article
    
    async def get_recent_news(
        self, 
        hours: int = 24, 
        limit: int = 100
    ) -> List[db.NewsArticle]:
        """Get recent news articles."""
        async with await self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            stmt = select(db.NewsArticle).where(
                db.NewsArticle.scraped_at >= cutoff
            ).order_by(db.NewsArticle.scraped_at.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_news_sentiment_avg(
        self, 
        ticker: str, 
        window_days: int = 5
    ) -> float:
        """Get average sentiment for ticker over window."""
        async with await self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=window_days)
            stmt = select(func.avg(db.NewsArticle.sentiment_score)).where(
                and_(
                    db.NewsArticle.entities_json.like(f'%{ticker}%'),
                    db.NewsArticle.scraped_at >= cutoff,
                    db.NewsArticle.sentiment_score.isnot(None)
                )
            )
            result = await session.execute(stmt)
            return result.scalar() or 0.0
    
    # ============ PRICE DATA ============
    
    async def add_price_data(
        self,
        ticker: str,
        timestamp: datetime,
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: int
    ) -> db.PriceData:
        """Add OHLCV price data."""
        returns = (close - open_price) / open_price
        log_return = (close / open_price) if open_price > 0 else 0
        
        async with await self.get_session() as session:
            price = db.PriceData(
                ticker=ticker,
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                returns=returns,
                log_return=log_return
            )
            session.add(price)
            await session.commit()
            await session.refresh(price)
            return price
    
    async def get_price_history(
        self,
        ticker: str,
        days: int = 365
    ) -> List[db.PriceData]:
        """Get price history."""
        async with await self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            stmt = select(db.PriceData).where(
                and_(
                    db.PriceData.ticker == ticker,
                    db.PriceData.timestamp >= cutoff
                )
            ).order_by(db.PriceData.timestamp.asc())
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    # ============ TECHNICAL FEATURES ============
    
    async def add_technical_features(
        self,
        ticker: str,
        timestamp: datetime,
        **features
    ) -> db.TechnicalFeatures:
        """Add technical features."""
        async with await self.get_session() as session:
            feat = db.TechnicalFeatures(
                ticker=ticker,
                timestamp=timestamp,
                **features
            )
            session.add(feat)
            await session.commit()
            await session.refresh(feat)
            return feat
    
    async def get_latest_features(
        self,
        ticker: str
    ) -> Optional[db.TechnicalFeatures]:
        """Get latest technical features."""
        async with await self.get_session() as session:
            stmt = select(db.TechnicalFeatures).where(
                db.TechnicalFeatures.ticker == ticker
            ).order_by(db.TechnicalFeatures.timestamp.desc()).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    # ============ TRADE SIGNALS ============
    
    async def add_signal(
        self,
        ticker: str,
        horizon_days: int,
        direction: str,
        confidence: float,
        technical_score: float = None,
        sentiment_score: float = None,
        macro_score: float = None,
        fused_score: float = None,
        position_size: float = None,
        expected_return: float = None
    ) -> db.TradeSignal:
        """Add trading signal."""
        async with await self.get_session() as session:
            signal = db.TradeSignal(
                ticker=ticker,
                horizon_days=horizon_days,
                direction=direction,
                confidence=confidence,
                technical_score=technical_score,
                sentiment_score=sentiment_score,
                macro_score=macro_score,
                fused_score=fused_score,
                position_size=position_size,
                expected_return=expected_return
            )
            session.add(signal)
            await session.commit()
            await session.refresh(signal)
            return signal
    
    async def get_pending_signals(
        self,
        limit: int = 20
    ) -> List[db.TradeSignal]:
        """Get pending (non-executed) signals."""
        async with await self.get_session() as session:
            stmt = select(db.TradeSignal).where(
                db.TradeSignal.executed == False
            ).order_by(db.TradeSignal.confidence.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def mark_signal_executed(
        self,
        signal_id: int,
        actual_return: float = None
    ):
        """Mark signal as executed."""
        async with await self.get_session() as session:
            stmt = select(db.TradeSignal).where(
                db.TradeSignal.id == signal_id
            )
            result = await session.execute(stmt)
            signal = result.scalar_one()
            signal.executed = True
            signal.executed_at = datetime.utcnow()
            if actual_return is not None:
                signal.actual_return = actual_return
            await session.commit()
    
    # ============ PORTFOLIO ============
    
    async def record_portfolio_snapshot(
        self,
        holdings: Dict[str, float],
        total_value: float,
        risk_metrics: Dict[str, float] = None
    ) -> db.Portfolio:
        """Record portfolio snapshot."""
        async with await self.get_session() as session:
            portfolio = db.Portfolio(
                holdings_json=json.dumps(holdings),
                total_value=total_value,
                risk_metrics_json=json.dumps(risk_metrics) if risk_metrics else None,
                timestamp=datetime.utcnow()
            )
            session.add(portfolio)
            await session.commit()
            await session.refresh(portfolio)
            return portfolio
    
    async def get_portfolio_history(
        self,
        days: int = 90
    ) -> List[db.Portfolio]:
        """Get portfolio history."""
        async with await self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            stmt = select(db.Portfolio).where(
                db.Portfolio.timestamp >= cutoff
            ).order_by(db.Portfolio.timestamp.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    # ============ MODEL METRICS ============
    
    async def record_model_metrics(
        self,
        model_name: str,
        metrics: Dict[str, float],
        train_samples: int = None,
        test_samples: int = None
    ) -> db.ModelMetrics:
        """Record model metrics."""
        async with await self.get_session() as session:
            m = db.ModelMetrics(
                model_name=model_name,
                train_samples=train_samples or 0,
                test_samples=test_samples or 0,
                **metrics
            )
            session.add(m)
            await session.commit()
            await session.refresh(m)
            return m
    
    # ============ DAILY LOGS ============
    
    async def create_daily_log(
        self,
        portfolio_summary: Dict[str, Any],
        signals: List[Dict[str, Any]],
        risk_metrics: Dict[str, Any],
        model_performance: Dict[str, Any]
    ) -> db.DailyLog:
        """Create daily log entry."""
        async with await self.get_session() as session:
            log = db.DailyLog(
                date=datetime.utcnow().date(),
                portfolio_summary_json=json.dumps(portfolio_summary),
                signals_json=json.dumps(signals),
                risk_metrics_json=json.dumps(risk_metrics),
                model_performance_json=json.dumps(model_performance)
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)
            return log
    
    async def update_daily_log_report(
        self,
        log_id: int,
        report: str,
        has_alerts: bool = False
    ):
        """Update daily log with Claude report."""
        async with await self.get_session() as session:
            stmt = select(db.DailyLog).where(db.DailyLog.id == log_id)
            result = await session.execute(stmt)
            log = result.scalar_one()
            log.claude_report = report
            log.has_alerts = has_alerts
            await session.commit()
    
    # ============ UTILITY ============
    
    async def get_correlation_matrix(
        self,
        tickers: List[str],
        window_days: int = 60
    ) -> Dict[str, Dict[str, float]]:
        """Calculate rolling correlation matrix."""
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        correlations = {}
        
        async with await self.get_session() as session:
            for t1 in tickers:
                correlations[t1] = {}
                for t2 in tickers:
                    stmt = select(
                        db.PriceData.returns
                    ).where(
                        and_(
                            db.PriceData.ticker == t1,
                            db.PriceData.timestamp >= cutoff
                        )
                    ).order_by(db.PriceData.timestamp.asc())
                    result = await session.execute(stmt)
                    returns1 = [r.returns for r in result.scalars().all() if r.returns]
                    
                    # Similar for t2...
                    correlations[t1][t2] = 0.0  # Simplified - implement proper corr
        
        return correlations
    
    async def close(self):
        """Close engine."""
        await self.engine.dispose()