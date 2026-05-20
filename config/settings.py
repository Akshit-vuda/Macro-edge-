"""
MacroEdge Configuration
All settings managed from this central file.
"""

import os
from pathlib import Path

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
CLAUDE_MODEL = "claude-sonnet-4-20250514"

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Market Data
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
USE_POLYGON = os.getenv("USE_POLYGON", "false").lower() == "true"

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