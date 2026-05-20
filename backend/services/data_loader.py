"""
Data Loading Service
Historical data fetching via yfinance and Alpaca.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import yfinance as yf
import numpy as np
import pandas as pd

from config.settings import TARGET_ASSETS
from ..services.database import DatabaseService

logger = logging.getLogger(__name__)


class DataLoader:
    """Load historical price data."""
    
    def __init__(self, db: DatabaseService):
        self.db = db
        self.assets = []
        for cat in TARGET_ASSETS.values():
            self.assets.extend(cat)
    
    async def load_historical_data(
        self,
        ticker: str,
        years: int = 5
    ) -> pd.DataFrame:
        """
        Load historical OHLCV data from yfinance.
        """
        logger.info(f"Loading {years} years of {ticker} data")
        
        # Calculate dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=years * 365)
        
        # Fetch from yfinance
        try:
            data = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )
            
            if data.empty:
                logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()
            
            # Reset index to make DateTime a column
            data = data.reset_index()
            data.columns = [c.lower() for c in data.columns]
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading {ticker}: {e}")
            return pd.DataFrame()
    
    async def load_all_assets(
        self,
        years: int = 5,
        delay: float = 0.5
    ) -> dict:
        """
        Load historical data for all target assets.
        """
        results = {}
        
        for ticker in self.assets:
            data = await self.load_historical_data(ticker, years=years)
            if not data.empty:
                results[ticker] = data
                
                # Store in database
                for _, row in data.iterrows():
                    await self.db.add_price_data(
                        ticker=ticker,
                        timestamp=row['date'],
                        open_price=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=int(row['volume'])
                    )
            
            # Rate limiting
            await asyncio.sleep(delay)
        
        return results
    
    async def update_price_data(
        self,
        ticker: str
    ) -> bool:
        """
        Update with latest data for a single ticker.
        """
        data = await self.load_historical_data(ticker, years=0.1)  # Last ~36 days
        
        if data.empty:
            return False
        
        # Get last row
        latest = data.iloc[-1]
        await self.db.add_price_data(
            ticker=ticker,
            timestamp=latest['date'],
            open_price=latest['open'],
            high=latest['high'],
            low=latest['low'],
            close=latest['close'],
            volume=int(latest['volume'])
        )
        
        return True
    
    async def get_price_df(
        self,
        ticker: str,
        days: int = 365
    ) -> pd.DataFrame:
        """
        Get price data as DataFrame for analysis.
        """
        prices = await self.db.get_price_history(ticker, days)
        
        if not prices:
            return pd.DataFrame()
        
        data = {
            'date': [p.timestamp for p in prices],
            'open': [p.open for p in prices],
            'high': [p.high for p in prices],
            'low': [p.low for p in prices],
            'close': [p.close for p in prices],
            'volume': [p.volume for p in prices],
            'returns': [p.returns for p in prices]
        }
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        
        return df