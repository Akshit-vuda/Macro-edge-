"""
MacroEdge Configuration
All settings managed from this central file.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Base Paths
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/macroedge.db")

# API Keys (set in environment)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
CLAUDE_DAILY_USD_CAP = float(os.getenv("CLAUDE_DAILY_USD_CAP", "5.00"))

# moomoo / Futu (LIVE execution via OpenD gateway)
MOOMOO_OPEND_HOST = os.getenv("MOOMOO_OPEND_HOST", "127.0.0.1")
MOOMOO_OPEND_PORT = int(os.getenv("MOOMOO_OPEND_PORT", "11111"))
MOOMOO_TRADE_PWD = os.getenv("MOOMOO_TRADE_PWD", "")
MOOMOO_TRADE_ENV = os.getenv("MOOMOO_TRADE_ENV", "SIMULATE")
MOOMOO_ACCOUNT_ID = os.getenv("MOOMOO_ACCOUNT_ID", "")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Market Data
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
USE_POLYGON = os.getenv("USE_POLYGON", "false").lower() == "true"

# Slack (ChatOps)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
SLACK_APPROVAL_CHANNEL = os.getenv("SLACK_APPROVAL_CHANNEL", "")

# MLflow (learning tracking)
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")

# Asset Universe
TARGET_ASSETS = {
    "commodities": ["GLD", "SLV", "USO"],
    "sectors": ["XLK", "XLE", "XLF", "XLV"],  # Tech, Energy, Finance, Health
    "macro_etf": ["SPY", "QQQ", "IWM", "TLT"]
}

# Risk Parameters
MAX_POSITION_SIZE = 0.02  # 2% max per trade
MAX_SECTOR_CONCENTRATION = 0.20  # 20% max sector
DRAWDOWN_KILL_SWITCH = -0.08  # -8% drawdown

# Signals
SIGNAL_HORIZONS = [3, 5, 7]  # Days
MIN_SIGNAL_CONFIDENCE = 0.55  # 55% min confidence
SHARPE_TARGET = 1.0
WIN_RATE_TARGET = 0.52

# ML Parameters
FEATURE_WINDOWS = {
    "technical": [5, 10, 20, 60],  # Days
    "sentiment": [1, 3, 5],  # Days  
    "macro_event": [5, 10, 20]  # Days
}

# News Sources
RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/markets",
    "http://feeds.bbci.co.uk/news/business/rss.xml"
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DAILY_REPORT_TIME = "07:00"  # UTC

# Critical keys required for full functionality; missing ones only warn (see validate_settings).
_CRITICAL_KEYS = {
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "ALPACA_API_KEY": ALPACA_API_KEY,
    "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
}


def validate_settings() -> None:
    """Log a WARNING for each missing critical setting. Never raises.

    Intended to be called at startup so missing config is visible in logs
    without blocking import or process start (e.g. paper-trading-only runs
    that don't need every key set).
    """
    for name, value in _CRITICAL_KEYS.items():
        if not value:
            logger.warning("Missing critical setting: %s is not set", name)