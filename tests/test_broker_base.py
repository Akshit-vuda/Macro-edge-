"""Tests for the BrokerAdapter interface and its dataclasses (ticket C1)."""

from datetime import datetime, timezone

import pytest

from backend.services.brokers import (
    AccountState,
    BrokerAdapter,
    OrderIntent,
    OrderResult,
    Position,
)


def make_intent(**overrides) -> OrderIntent:
    """Build a valid OrderIntent, with keyword overrides for edge-case tests."""
    kwargs = dict(
        client_id="c-1",
        symbol="AAPL",
        side="buy",
        rationale="momentum breakout",
        signal_id="sig-1",
        model_version="v1",
        stop_price=95.0,
        target_price=120.0,
        qty=1.0,
    )
    kwargs.update(overrides)
    return OrderIntent(**kwargs)


class FakeBroker(BrokerAdapter):
    """In-memory broker used to exercise the interface contract."""

    def __init__(self) -> None:
        self._orders: dict[str, OrderResult] = {}
        self._positions: dict[str, Position] = {}

    def get_account(self) -> AccountState:
        return AccountState(equity=1000.0, cash=500.0, buying_power=500.0)

    def get_positions(self) -> list[Position]:
        return list(self._positions.values())

    def submit_order(self, intent: OrderIntent) -> OrderResult:
        if intent.client_id in self._orders:  # idempotency
            return self._orders[intent.client_id]
        qty = intent.qty if intent.qty is not None else intent.notional / 100.0
        result = OrderResult(
            order_id=f"o-{len(self._orders) + 1}",
            client_id=intent.client_id,
            status="filled",
            filled_qty=qty,
            filled_avg_price=100.0,
            submitted_at=datetime.now(timezone.utc),
        )
        self._orders[intent.client_id] = result
        pos = self._positions.get(intent.symbol)
        signed = qty if intent.side == "buy" else -qty
        new_qty = (pos.qty if pos else 0.0) + signed
        self._positions[intent.symbol] = Position(
            symbol=intent.symbol, qty=new_qty, avg_price=100.0
        )
        return result

    def cancel_order(self, order_id: str) -> None:
        pass

    def is_market_open(self) -> bool:
        return True


class TestFakeBrokerRoundTrip:
    def test_submit_order_round_trip(self):
        broker = FakeBroker()
        intent = make_intent()
        result = broker.submit_order(intent)
        assert result.client_id == intent.client_id
        assert result.status == "filled"
        positions = broker.get_positions()
        assert len(positions) == 1
        assert positions[0].symbol == "AAPL"
        assert positions[0].qty == 1.0

    def test_duplicate_client_id_is_idempotent(self):
        broker = FakeBroker()
        intent = make_intent()
        first = broker.submit_order(intent)
        second = broker.submit_order(intent)
        assert second is first
        assert broker.get_positions()[0].qty == 1.0  # no double fill

    def test_account_and_market_hours(self):
        broker = FakeBroker()
        acct = broker.get_account()
        assert acct.equity == 1000.0
        assert acct.currency == "USD"
        assert acct.day_trade_count == 0
        assert broker.is_market_open() is True

    def test_abstract_base_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BrokerAdapter()  # type: ignore[abstract]


class TestOrderIntentValidation:
    def test_both_qty_and_notional_rejected(self):
        with pytest.raises(ValueError):
            make_intent(qty=1.0, notional=50.0)

    def test_neither_qty_nor_notional_rejected(self):
        with pytest.raises(ValueError):
            make_intent(qty=None, notional=None)

    def test_notional_only_is_valid(self):
        intent = make_intent(qty=None, notional=25.0)
        assert intent.notional == 25.0

    def test_limit_order_requires_limit_price(self):
        with pytest.raises(ValueError):
            make_intent(type="limit", limit_price=None)
        assert make_intent(type="limit", limit_price=99.5).limit_price == 99.5

    def test_bad_side_rejected(self):
        with pytest.raises(ValueError):
            make_intent(side="hold")

    def test_bad_type_rejected(self):
        with pytest.raises(ValueError):
            make_intent(type="stop_limit")

    def test_empty_rationale_rejected(self):
        with pytest.raises(ValueError):
            make_intent(rationale="")

    def test_empty_signal_id_rejected(self):
        with pytest.raises(ValueError):
            make_intent(signal_id="")

    def test_empty_model_version_rejected(self):
        with pytest.raises(ValueError):
            make_intent(model_version="")

    def test_nonpositive_stop_and_target_rejected(self):
        with pytest.raises(ValueError):
            make_intent(stop_price=0.0)
        with pytest.raises(ValueError):
            make_intent(target_price=-1.0)

    def test_missing_exit_plan_is_type_error(self):
        # stop_price/target_price are required fields — "write the exit first".
        with pytest.raises(TypeError):
            OrderIntent(
                client_id="c-1",
                symbol="AAPL",
                side="buy",
                rationale="r",
                signal_id="s",
                model_version="v",
                qty=1.0,
            )

    def test_frozen(self):
        intent = make_intent()
        with pytest.raises(Exception):
            intent.symbol = "MSFT"  # type: ignore[misc]


def test_package_exports():
    import backend.services.brokers as pkg

    for name in ("BrokerAdapter", "AccountState", "Position", "OrderIntent", "OrderResult"):
        assert hasattr(pkg, name)
