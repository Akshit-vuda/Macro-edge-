"""
Broker Adapter Interface
Abstract base class that broker integrations (Alpaca, Moomoo, ...) must implement.
Strategy/execution code talks to brokers only through this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderIntent:
    """
    A validated, broker-agnostic order request.

    Exactly one of `qty` or `notional` must be set. Provenance fields
    (rationale, signal_id, model_version) and the exit plan
    (stop_price, target_price) are required — playbook rule: write the exit first.
    `client_id` is the idempotency key: submitting the same intent twice
    must not place two orders.
    """

    client_id: str
    symbol: str
    side: str  # "buy" | "sell"
    rationale: str
    signal_id: str
    model_version: str
    stop_price: float
    target_price: float
    qty: float | None = None
    notional: float | None = None  # fractional dollars (micro-account sizing)
    type: str = "market"  # "market" | "limit"
    limit_price: float | None = None
    tif: str = "day"  # "day" | "gtc"

    def __post_init__(self) -> None:
        """Validate the intent; raise ValueError on any inconsistency."""
        if (self.qty is None) == (self.notional is None):
            raise ValueError("exactly one of qty or notional must be set")
        if self.side not in ("buy", "sell"):
            raise ValueError(f"side must be 'buy' or 'sell', got {self.side!r}")
        if self.type not in ("market", "limit"):
            raise ValueError(f"type must be 'market' or 'limit', got {self.type!r}")
        if self.type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require limit_price")
        for field_name in ("rationale", "signal_id", "model_version"):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} must be non-empty")
        if self.stop_price <= 0:
            raise ValueError(f"stop_price must be > 0, got {self.stop_price}")
        if self.target_price <= 0:
            raise ValueError(f"target_price must be > 0, got {self.target_price}")


@dataclass
class AccountState:
    """Broker account snapshot normalized across brokers."""

    equity: float
    cash: float
    buying_power: float
    currency: str = "USD"
    pattern_day_trader: bool = False
    day_trade_count: int = 0  # rolling 5-business-day count, used by the C5 PDT gate


@dataclass
class Position:
    """An open position; qty may be fractional, negative = short."""

    symbol: str
    qty: float
    avg_price: float
    market_value: float = 0.0
    unrealized_pl: float = 0.0


@dataclass
class OrderResult:
    """Broker response to a submitted order."""

    order_id: str
    client_id: str
    status: str  # "accepted" | "filled" | "rejected" | "canceled" ...
    filled_qty: float = 0.0
    filled_avg_price: float | None = None
    submitted_at: datetime | None = None


class BrokerAdapter(ABC):
    """Broker-agnostic trading interface implemented by C2/C3 adapters."""

    @abstractmethod
    def get_account(self) -> AccountState:
        """Return the current account snapshot."""
        ...

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """Return all currently open positions."""
        ...

    @abstractmethod
    def submit_order(self, intent: OrderIntent) -> OrderResult:
        """
        Submit an order.

        Must be idempotent on `intent.client_id`: re-submitting the same
        client_id returns the original OrderResult without placing a new order.
        """
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """Cancel an open order by broker order id."""
        ...

    @abstractmethod
    def is_market_open(self) -> bool:
        """Return True if the market is currently open for trading."""
        ...
