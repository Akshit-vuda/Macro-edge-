"""
Alpaca Trading Integration
Paper and live trading via Alpaca API.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
try:
    import alpaca_trade_api as alpaca
except ImportError:
    alpaca = None

from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_PAPER

logger = logging.getLogger(__name__)


class AlpacaClient:
    """
    Alpaca API wrapper for paper/live trading.
    """
    
    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        paper: bool = True
    ):
        self.api_key = api_key or ALPACA_API_KEY
        self.secret_key = secret_key or ALPACA_SECRET_KEY
        self.paper = paper or ALPACA_PAPER
        self.client = None
        
        if self.api_key and self.secret_key:
            self._connect()
    
    def _connect(self):
        """Connect to Alpaca."""
        if alpaca is None:
            logger.error("alpaca_trade_api not installed")
            return
        
        try:
            base_url = "https://paper-api.alpaca.markets" if self.paper else "https://api.alpaca.markets"
            
            self.client = alpaca.REST(
                self.api_key,
                self.secret_key,
                base_url
            )
            
            # Check connection
            account = self.client.get_account()
            logger.info(f"Connected to Alpaca: account {account.id}")
            
        except Exception as e:
            logger.error(f"Alpaca connection error: {e}")
            self.client = None
    
    def get_account(self) -> Dict:
        """Get account details."""
        if not self.client:
            return {}
        
        try:
            acc = self.client.get_account()
            return {
                'id': acc.id,
                'cash': float(acc.cash),
                'portfolio_value': float(acc.portfolio_value),
                'buying_power': float(acc.buying_power),
                'status': acc.status,
                'pattern_day_trader': acc.pattern_day_trader
            }
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        if not self.client:
            return []
        
        try:
            positions = self.client.list_positions()
            return [
                {
                    'symbol': p.symbol,
                    'qty': float(p.qty),
                    'side': p.side,
                    'market_value': float(p.market_value),
                    'cost_basis': float(p.cost_basis),
                    'current_price': float(p.current_price),
                    'unrealized_pl': float(p.unrealized_pl),
                    'unrealized_plpc': float(p.unrealized_plpc),
                }
                for p in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get a specific position."""
        if not self.client:
            return None
        
        try:
            pos = self.client.get_position(symbol)
            return {
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'market_value': float(pos.market_value),
                'cost_basis': float(pos.cost_basis),
            }
        except:
            return None
    
    def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "limit",
        limit_price: float = None,
        time_in_force: str = "day"
    ) -> Dict:
        """
        Submit a trading order.
        """
        if not self.client:
            logger.warning("Alpaca not connected, skipping order")
            return {}
        
        try:
            order = self.client.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                limit_price=limit_price,
                time_in_force=time_in_force
            )
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
        except Exception as e:
            logger.error(f"Order submission error: {e}")
            return {'error': str(e)}
    
    def cancel_order(self, order_id: str):
        """Cancel an order."""
        if not self.client:
            return
        
        try:
            self.client.cancel_order(order_id)
        except Exception as e:
            logger.error(f"Cancel error: {e}")
    
    def list_orders(
        self,
        status: str = "open",
        limit: int = 50
    ) -> List[Dict]:
        """List orders."""
        if not self.client:
            return []
        
        try:
            orders = self.client.list_orders(status=status, limit=limit)
            return [
                {
                    'id': o.id,
                    'symbol': o.symbol,
                    'qty': o.qty,
                    'side': o.side,
                    'type': o.type,
                    'status': o.status,
                    'created_at': o.created_at
                }
                for o in orders
            ]
        except Exception as e:
            logger.error(f"List orders error: {e}")
            return []
    
    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Day",
        start: str = None,
        end: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get historical bars."""
        if not self.client:
            return []
        
        try:
            bars = self.client.get_bars(
                symbol,
                timeframe,
                start=start,
                end=end,
                limit=limit
            )
            return [
                {
                    't': b.t,
                    'o': b.o,
                    'h': b.h,
                    'l': b.l,
                    'c': b.c,
                    'v': b.v
                }
                for b in iterable(bars)
            ]
        except Exception as e:
            logger.error(f"Get bars error: {e}")
            return []
    
    def get_clock(self) -> Dict:
        """Get market clock."""
        if not self.client:
            return {}
        
        try:
            clock = self.client.get_clock()
            return {
                'timestamp': clock.timestamp,
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close
            }
        except Exception as e:
            logger.error(f"Get clock error: {e}")
            return {}
    
    def is_market_open(self) -> bool:
        """Check if market is open."""
        clock = self.get_clock()
        return clock.get('is_open', False)


# Alias
TradingClient = AlpacaClient