"""Tests for config.settings: validate_settings() and CLAUDE_DAILY_USD_CAP."""

import logging

from config import settings


def test_claude_daily_usd_cap_is_float() -> None:
    assert isinstance(settings.CLAUDE_DAILY_USD_CAP, float)


def test_validate_settings_all_present_no_warning(monkeypatch, caplog) -> None:
    monkeypatch.setattr(settings, "_CRITICAL_KEYS", {"ANTHROPIC_API_KEY": "sk-test"})
    with caplog.at_level(logging.WARNING):
        settings.validate_settings()
    assert not caplog.records


def test_validate_settings_missing_keys_warns_and_does_not_raise(monkeypatch, caplog) -> None:
    monkeypatch.setattr(
        settings,
        "_CRITICAL_KEYS",
        {"ANTHROPIC_API_KEY": "", "ALPACA_API_KEY": ""},
    )
    with caplog.at_level(logging.WARNING):
        settings.validate_settings()  # must not raise
    assert len(caplog.records) == 2
    assert "ANTHROPIC_API_KEY" in caplog.text
    assert "ALPACA_API_KEY" in caplog.text
