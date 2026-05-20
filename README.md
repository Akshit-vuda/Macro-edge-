# MacroEdge Intelligence Platform

An AI-powered macro trading intelligence platform that learns global market relationships over a six-month observation window before generating predictive trade signals.

## Features

- **News Intelligence**: Real-time news scraping with FinBERT sentiment analysis
- **Technical Analysis**: RSI, MACD, Bollinger Bands, ATR, and advanced technical indicators
- **ML Models**: XGBoost classifiers for directional prediction, signal fusion, regime detection
- **Alpaca Integration**: Paper trading with eventual live trading support
- **Claude AI Brain**: Human-in-the-loop supervision with risk narration
- **Risk Management**: Kelly Criterion position sizing, VaR, drawdown protection
- **React Dashboard**: Interactive real-time monitoring dashboard

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see below)

### Installation

1. Clone and enter the project:
   ```bash
   cd macroedge
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend && npm install && cd ..
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Running

#### Development Mode

**Backend:**
```bash
python main.py
```

**Frontend:**
```bash
cd frontend && npm run dev
```

Access the dashboard at http://localhost:3000

#### Docker

```bash
docker-compose up
```

## API Keys Required

| Service | Purpose | Cost |
|---------|--------|------|
| Alpaca Markets | Paper/live trading | Free (paper) |
| Anthropic Claude | AI supervision | ~$45/month |
| NewsAPI | News aggregation | $149/month |
| Polygon.io | Real-time data | $29/month |

## Architecture

```
macroedge/
├── backend/
│   ├── api/           # FastAPI routes
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   │   ├── database.py
│   │   ├── trading.py
│   │   ├── news_intelligence.py
│   │   ├── claude_brain.py
│   │   └── risk_management.py
│   └── ml/           # ML models
│       ├── technical_analysis.py
│       └── models.py
├── frontend/
│   └── src/
│       ├── pages/   # Dashboard pages
│       └── components/
├── config/
│   └── settings.py
└── main.py
```

## Phase Plan

See [SPEC.pdf](/workspace/MY FINANCIAL PROJECT .pdf) for complete 18-month roadmap:

- **Phase 0**: Foundation setup
- **Phase 1**: Data infrastructure
- **Phase 2**: News intelligence
- **Phase 3**: Trade intelligence
- **Phase 4**: Signal fusion
- **Phase 5**: Claude brain
- **Phase 6**: Paper trading validation
- **Phase 7**: Live deployment

## Risk Parameters

- Max position: 2% per trade
- Max sector: 20%
- Drawdown kill-switch: -8%
- Min confidence: 55%

## Target Assets

- **Commodities**: GLD, SLV, USO
- **Sectors**: XLK, XLE, XLF, XLV
- **Macro ETF**: SPY, QQQ, IWM, TLT

## Documentation

- FastAPI docs: http://localhost:8000/docs
- CFA alignment: See SPEC.pdf Section 9

## License

Confidential - Internal use only