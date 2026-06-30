# MacroEdge v2 — System Architecture & Build Plan

**Author:** Research/architecture desk note
**Status:** Draft v1 — starting point for the rebuild
**Scope:** Fold a Claude+Obsidian "brain," Slack ChatOps, Alpaca paper + live execution, moomoo screening, Yahoo news, and a from-scratch reinforcement-learning strategy engine into the existing MacroEdge codebase, starting from a **$200** account.

> This is an engineering/architecture plan, not investment advice. Capital at $200 is a *learning lab*, not a wealth engine — size expectations accordingly.

---

## 0. Senior-desk reality checks (read before building)

A senior asset-management / IB team would put these on the table on day one, because they change the design:

1. **Robinhood has no official retail trading API.** There is no supported, ToS-compliant REST API for automated equity trading on Robinhood. The only routes are:
   - `robin_stocks` — an **unofficial, reverse-engineered** library. It violates Robinhood's ToS, breaks on every app update, fights 2FA, and can get the account **locked**. Not suitable for an automated, capital-bearing system.
   - Robinhood **Legend / Crypto API** — narrow scope, not general equities automation.
   - **Recommendation:** use **Alpaca for *both* paper and live** automated equity execution (it has a real, supported brokerage API and live accounts). Keep Robinhood as an **optional manual-execution venue**, where the system posts a fully-specified order ticket to Slack and a human places it. (moomoo's OpenAPI *also* supports live trading and is a stronger automation candidate than Robinhood — see §10 open decision.)

2. **$200 + the Pattern Day Trader (PDT) rule.** Under $25k equity, a **margin** account is capped at **3 day-trades per rolling 5 business days**; a 4th triggers a 90-day restriction. A **cash account** avoids PDT but is bound by **T+1 settlement** (you can't immediately reuse unsettled proceeds). At $200, **fractional shares are mandatory** (Alpaca + Robinhood support them), and the existing `MAX_POSITION_SIZE = 2%` (= $4/trade) is meaningless — the micro-account needs a different risk model (§6). The compliance engine must *enforce* PDT/settlement (§5), not just advise.

3. **RL on financial data is genuinely hard.** Markets are non-stationary, signal-to-noise is brutal, and naïve deep-RL overfits and "reward-hacks." Live $-bearing RL with no track record is how accounts get vaporized. The discipline:
   - Train RL **only in simulation** first; gate to **paper**, then to **tiny live** with a **human-in-the-loop (Claude + you) approval** on every order.
   - Prefer **sample-efficient, auditable** formulations (contextual bandits for sizing, RL for allocation/timing) before full deep-RL.
   - **Walk-forward** validation, not single-split backtests; assume any backtest Sharpe is inflated.

4. **Data licensing.** `yfinance` is *personal use only* (no redistribution); Alpaca market data has entitlement tiers; moomoo OpenD has its own ToS. Keep all of it **internal**, never re-serve it publicly.

---

## 1. The "trading desk" as a system (the org-chart → layer mapping)

Mapping the request to how a real desk is organized makes the responsibilities clean:

| Desk role (asset-mgmt / IB analogy) | System layer | Named tools |
|---|---|---|
| **Market Data & Quant Research** | L1 Ingestion + L2 Storage/Features | moomoo (screen), Alpaca (bars), yfinance (news/prices) |
| **CIO / Macro Strategist ("the brain")** | L3 Research & Reasoning | **Claude + Obsidian** |
| **Portfolio Managers / Quants** | L4 Signal & Strategy (RL + supervised) | from-scratch ML |
| **Risk & Compliance** | L5 Risk / PDT / limits | (build) |
| **Trading / Execution desk** | L6 Order management | **Alpaca** (auto) · Robinhood (manual) |
| **Front office / ChatOps** | L7 Interface & approvals | **Slack** |
| **Ops / Performance & Audit** | L8 Observability, learning-progress, governance | MLflow/W&B, audit log |

Data and capital flow **down** (research → decision → order); evidence and accountability flow **up** (fills → attribution → audit). Every order must carry **provenance**: which signal, which model version, which Claude rationale produced it.

---

## 2. Layered architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│  L7  INTERFACE / ChatOps          Slack bot (Bolt + Socket Mode) · React UI │
│      - commands, approvals, alerts, daily brief, kill-switch                 │
├───────────────────────────────────────────────────────────────────────────┤
│  L3  BRAIN (CIO)                  Claude API (tool-use + MCP) · Obsidian      │
│      - macro thesis, signal review, risk narrative, trade rationale          │
│      - Obsidian vault = second brain + trade journal (RAG via vector DB)     │
├───────────────────────────────────────────────────────────────────────────┤
│  L4  STRATEGY / ML                Feature eng · Supervised signals · RL agent│
│      - Gym env ← backtester · Stable-Baselines3 / FinRL · signal fusion       │
│      - MLflow/W&B experiment + learning-curve tracking                        │
├───────────────────────────────────────────────────────────────────────────┤
│  L5  RISK & COMPLIANCE            Sizing · PDT/settlement engine · kill-switch│
├───────────────────────────────────────────────────────────────────────────┤
│  L6  EXECUTION (OMS)              Alpaca (paper→live) · Robinhood (manual)    │
│      - idempotent orders, reconciliation, fill capture                        │
├───────────────────────────────────────────────────────────────────────────┤
│  L2  STORAGE & FEATURES          DuckDB+Parquet (lake) · SQLite/Postgres (state)│
│      - feature store · vector DB (LanceDB) for Obsidian RAG                   │
├───────────────────────────────────────────────────────────────────────────┤
│  L1  INGESTION                    moomoo OpenD · Alpaca data · yfinance · RSS │
├───────────────────────────────────────────────────────────────────────────┤
│  L0  FOUNDATION                   Config/secrets · Orchestrator (Prefect) ·   │
│      Docker Compose · logging/metrics (Prometheus+Grafana, Sentry)           │
└───────────────────────────────────────────────────────────────────────────┘
```

### L0 — Foundation & Security
- **Config/secrets:** keep the env-var pattern in `config/settings.py`, but **never commit keys**. Add `.env` to `.gitignore`, manage secrets with **SOPS+age** (encrypted-in-repo) or **Doppler/1Password CLI**. Start with **paper-only** Alpaca keys; live keys are added only at the live-gate.
- **Orchestration:** graduate the `APScheduler` in `main.py` to **Prefect** (Pythonic, retries, observability) for the nightly retrain / walk-forward / data-pull DAGs. Keep APScheduler for trivial intraday cron.
- **Runtime:** extend the existing `docker-compose.yaml` into services: `api`, `worker` (Prefect), `data`, `slackbot`, `grafana`, `mlflow`.
- **Observability:** structured logging (`structlog`), **Prometheus + Grafana** for system/portfolio metrics, **Sentry** for errors.

### L1 — Data Ingestion
- **Prices/bars (execution-grade):** Alpaca (`get_bars`, already wrapped in `backend/services/trading.py`).
- **Screening / discovery:** **moomoo OpenAPI** via the **OpenD gateway** + `futu`/`moomoo` SDK — run OpenD as a sidecar; pull screeners, fundamentals, L2 where entitled.
- **News:** Yahoo Finance via `yfinance` (`.news`) + the existing `RSS_FEEDS`; optional NewsAPI (already in config). Normalize into a single `NewsItem` schema.
- **Reliability:** every source behind an adapter interface (`MarketDataProvider`, `NewsProvider`) so providers are swappable; **pandera/Great Expectations** validation on every batch; ret/backoff + caching.

### L2 — Storage & Feature Store
- **Raw lake:** **Parquet partitioned by symbol/date**, queried with **DuckDB** — ideal at this scale, zero-ops, columnar, fast for feature builds. (Graduate to TimescaleDB/Postgres only if data volume demands.)
- **System state:** keep SQLite (`config.settings.DATABASE_URL`) for orders/positions/journal now; Postgres later.
- **Feature store:** a versioned `features/` table keyed by `(symbol, timestamp, feature_set_version)` so models train/serve on **identical** definitions (kills training/serving skew). Reuse `backend/ml/technical_analysis.py`.
- **Vector DB:** **LanceDB** (local-first, on-disk — privacy-friendly) to embed Obsidian notes + research for Claude RAG.

### L3 — The Brain (Claude + Obsidian)
- **Claude** is the CIO/strategist, not the trader. Extend the existing `ClaudeSupervisor` (`backend/services/claude_brain.py`) to:
  - Generate the **daily macro brief**, **signal review**, **risk narrative**, **trade rationale**, **anomaly triage** (methods already stubbed — wire them to real data).
  - Run **tool-use**: expose system functions (get_portfolio, get_signals, get_risk, query_journal, propose_trade) as Claude tools, and stand up an **MCP server** so both the app *and* Claude Code can drive the system.
  - **Cost control:** the `enforce_daily_token_cap` stub becomes real — token accounting + **prompt caching** + a hard daily $ cap. Use a **current** Claude model (the pinned `claude-sonnet-4-20250514` is stale; pick a current Sonnet for cost or Opus for hard reasoning, Haiku for cheap classification).
- **Obsidian** is the durable "second brain" and **trade journal**:
  - Vault structure: `/Theses` (macro views), `/Tickers/<SYM>` (per-name notes), `/Journal/<date>` (every decision + outcome), `/Models/<run>` (model cards), `/Playbooks` (strategy rules).
  - The system **writes** structured Markdown notes (trade tickets, post-mortems) into the vault; Claude **reads** them via the LanceDB RAG index → decisions are grounded in your accumulated history. Vault stays **local / end-to-end-encrypted sync** (privacy by default).

### L4 — Strategy & ML (the from-scratch RL engine)
See §6 for the full RL design. In brief:
- **Supervised signal models** (direction, regime, volatility, sentiment) → feature inputs.
- **RL agent** (the new core) decides **allocation, sizing, and timing** inside a **Gym environment wrapping a realistic backtester**.
- **Signal fusion** (existing `backend/ml/models/fusion.py`) combines supervised signals + RL policy into a final, risk-checked order intent.
- **Experiment & learning-progress tracking** via **MLflow** (self-hosted, free) or **Weights & Biases** — this is literally how "you will see the progress of their learning."

### L5 — Risk & Compliance
- **Micro-account sizing** (§6.4): fractional-share aware, volatility-targeted, **not** a flat 2%.
- **PDT/settlement engine:** hard pre-trade gate that counts day-trades in the rolling 5-day window and blocks the 4th; tracks unsettled cash in a cash account. **This is non-negotiable.**
- **Guards:** keep `kelly_criterion` (half-Kelly), the `-8%` drawdown kill-switch, sector caps — but re-scale for a 1–3 position micro-portfolio.
- Every order passes a **pre-trade check chain** (sizing → exposure → PDT → liquidity → confidence ≥ `MIN_SIGNAL_CONFIDENCE`) before it can reach L6.

### L6 — Execution / OMS
- **One `BrokerAdapter` interface, two implementations.** Define a single abstract interface (`get_account`, `get_positions`, `submit_order`, `cancel_order`, `get_bars`, `is_market_open`) so the OMS, risk layer, and RL env never know which broker is live:
  - **`AlpacaAdapter`** (paper) — wrap the existing `AlpacaClient`; fix the `iterable(bars)` bug.
  - **`MoomooAdapter`** (live, **decided**) — `futu`/`moomoo` SDK talking to the **OpenD gateway** sidecar; handles auth, trade-context unlock, fractional/qty rules, and HK/US market routing.
- **OMS:** idempotency keys, order-state reconciliation, and fill capture into the journal.
- **Manual venue (Robinhood):** optional only — OMS emits a **fully-specified ticket** to Slack; human executes and confirms the fill, which the OMS records. No unofficial-API automation.
- **Sim↔live parity:** the same order-intent object flows through backtest → Alpaca paper → moomoo live, so behavior is consistent across all three.

### L7 — Interface / ChatOps (Slack)
- **Slack Bolt for Python + Socket Mode** (no public URL, good for a private setup).
- Capabilities: `/brief` (daily Claude brief), `/positions`, `/signals`, `/propose`, **approve/reject buttons** on every proposed trade (human-in-the-loop gate), `/killswitch`, push alerts (fills, drawdown, anomalies, learning milestones).
- The existing **React dashboard** (`frontend/`) remains the rich view (portfolio, learning curves, predictions.json already exists as a sync target).

### L8 — Observability, Learning-Progress & Governance
- **Learning progress:** MLflow/W&B dashboards of RL **episode reward, Sharpe-in-sim, policy entropy, value loss, walk-forward OOS metrics**, plus model cards in Obsidian. Weekly Claude-written "model report card" to Slack.
- **Drift detection:** monitor feature/label drift (PSI/KL) → auto-flag retrain.
- **Audit trail:** immutable log linking every fill → order → signal → model version → Claude rationale (provenance), satisfying the IB-grade "who decided this and why" standard.

---

## 3. End-to-end data flow (one cycle)

```
moomoo screen ─┐
Alpaca bars  ──┼─► validate ─► Parquet/DuckDB lake ─► feature store ─┐
yfinance news ─┘                                                     │
                                                                     ▼
                                            supervised signals  +  RL policy
                                                                     │
                                                                     ▼
                                   Claude (RAG over Obsidian) reviews → rationale
                                                                     │
                                                          risk + PDT pre-trade checks
                                                                     │
                                                       Slack approval (human gate)
                                                                     │
                                              Alpaca order (paper/live) / manual ticket
                                                                     │
                                       fill ─► journal (Obsidian) ─► attribution ─► MLflow
                                                                     │
                                                  reward signal feeds next RL update
```

---

## 4. Recommended tech stack (named tools + additions)

| Function | You named | Recommended addition / how it fits |
|---|---|---|
| Brain / reasoning | **Claude, Obsidian** | Anthropic Messages API (tool-use), **MCP server**, **LanceDB** (RAG over vault), prompt caching |
| ChatOps | **Slack** | **slack-bolt** + Socket Mode; approve/reject buttons |
| Live execution | **moomoo (decided)** | **moomoo OpenAPI** via OpenD gateway — consolidates screening + live execution in one vendor. Robinhood = manual ticket only (no official API). |
| Paper trading | **Alpaca** | already wrapped — keep. Both brokers sit behind one `BrokerAdapter` interface for sim↔paper↔live parity |
| Screening | **moomoo** | **moomoo OpenD gateway** + `futu` SDK (also a live-trading option) |
| News | **Yahoo Finance** | `yfinance.news` + existing RSS; optional NewsAPI |
| ML / RL | **from scratch** | **Gymnasium + Stable-Baselines3** (PPO/SAC), **FinRL** patterns, **vectorbt** (research backtest), **Nautilus Trader** (event-driven sim↔live parity) |
| Experiment tracking | — | **MLflow** (free, self-host) or **W&B** — the "see learning progress" surface |
| Orchestration | (APScheduler) | **Prefect** for DAGs |
| Storage | (SQLite) | **DuckDB + Parquet** lake; Postgres later |
| Data validation | — | **pandera** / Great Expectations |
| Secrets | (env vars) | **SOPS+age** or Doppler; `.env` git-ignored |
| Monitoring | — | **Prometheus + Grafana**, **Sentry**, `structlog` |

---

## 5. Data handling, privacy & governance

- **Secrets:** never in git. Encrypted at rest (SOPS/age), least-privilege scopes, **paper keys until the live-gate**, rotation policy. The repo already reads from env — finish the job by encrypting and gitignoring.
- **Local-first / privacy:** Obsidian vault and the DuckDB lake live **on your machine**; if synced, use **end-to-end-encrypted** sync. Minimal PII (it's your own account); the only sensitive material is API keys and the trade journal — both encrypted.
- **Data licensing:** yfinance/moomoo/Alpaca data is **internal-use only**; do not republish it through the public website (the current `WebsiteSyncer` should export only **derived signals**, never raw vendor data).
- **Encryption:** DB at rest encrypted; secrets vault encrypted; TLS for any remote calls.
- **Audit & reproducibility:** every model run is versioned (data hash + code commit + params in MLflow); every order is provenance-linked; the journal is append-only. This is the IB-grade control that lets you answer "why did we hold X on date Y?"
- **Cost governance:** hard daily caps on Claude tokens and data API calls; alert on breach.
- **Kill-switch & human gate:** no live order executes without (a) passing risk/PDT checks and (b) human approval in Slack. The `-8%` drawdown kill-switch halts new risk automatically.

---

## 6. The reinforcement-learning strategy engine (from scratch)

### 6.1 Why RL here, and where it actually helps
RL is best aimed at **sequential allocation/sizing/timing under your own risk constraints**, *fed by* supervised signals — not at predicting raw price (let supervised models do that). Framing: supervised models answer "what's likely?"; the RL agent answers "given that and my risk limits, **how much and when**?"

### 6.2 Environment (Gym)
- Wrap a **realistic event-driven backtester** (start vectorbt for speed; move to Nautilus Trader for sim↔live parity) in a `gymnasium.Env`.
- **State:** supervised signal outputs (direction/regime/vol/sentiment) + technical features + current positions + cash + **PDT/settlement counters** + drawdown.
- **Action:** target portfolio weights / fractional notional per asset (continuous → SAC/PPO) or discrete {buy, hold, sell, size-bucket} (→ DQN/PPO).
- **Reward:** **risk-adjusted, not raw PnL** — e.g. differential Sharpe or `Δequity − λ·drawdown − costs − turnover_penalty − PDT_violation_penalty`. Bake transaction costs, slippage, and the micro-account frictions **into the reward** so the policy learns the real environment.

### 6.3 Algorithms & training discipline
- Start **Stable-Baselines3 PPO** (robust) and **SAC** (continuous sizing); borrow **FinRL** env/reward patterns.
- **Walk-forward**: train on rolling windows, evaluate strictly **out-of-sample**; reject policies that only win in-sample.
- **Curriculum:** train on synthetic regimes first (the existing `TrainingDataGenerator` is a fine *sandbox*, **not** a substitute for real data), then real history, then paper.
- **Offline RL option** (CQL/IQL) to learn from logged paper-trading data without risky exploration in live markets.

### 6.4 Micro-account ($200) sizing model
Replace the flat 2% with: **fractional-notional, volatility-targeted** sizing — target a fixed portfolio vol, cap single-name exposure, respect cash settlement, and **concentrate** (1–3 positions) because diversification is impossible at $200. Half-Kelly as an upper bound, never the target.

### 6.5 Saving data & "seeing the learning"
- **Every** training run → MLflow: params, data hash, code commit, learning curves (reward, OOS Sharpe, entropy, losses), model artifact.
- **Checkpoints** versioned in `backend/ml/trained_models/` (fix the hardcoded `/workspace/project` paths first).
- **Weekly Claude "report card"** summarizing whether the policy is improving and **proposing strategy adjustments** — closing your "adjust strategies if required" loop with a human approving the change.
- Dashboard panel (React) + Slack milestone alerts ("policy OOS Sharpe crossed 1.0 on walk-forward").

### 6.6 Promotion gate (sim → paper → live)
A policy may only advance when it clears explicit, pre-registered thresholds at each stage (e.g. OOS walk-forward Sharpe, max-DD, min trades), and **live** additionally requires human sign-off and starts at **minimum size**. No auto-promotion to live.

---

## 7. Phased roadmap (folding into MacroEdge)

**Phase 0 — Stabilize (week 1).** Fix the import-blocking bug in `claude_brain.py:71`, the `iterable()` bug in `trading.py`, and the hardcoded `/workspace/project` paths; gitignore `.env`; update `CLAUDE_MODEL`. Stand up Docker Compose services + MLflow.

**Phase 1 — Real data (weeks 1–2).** Replace synthetic-only training with **real** Alpaca/yfinance/moomoo ingestion → DuckDB/Parquet lake → versioned feature store, with pandera validation. Keep the synthetic generator as a **sandbox**.

**Phase 2 — Brain online (weeks 2–3).** Wire `ClaudeSupervisor` to real data; build the **MCP server** + Claude tool-use; create the **Obsidian vault** structure + LanceDB RAG + auto-journaling.

**Phase 3 — Signals + backtester (weeks 3–5).** Train the supervised models on real data; build the Gym-wrapped backtester; establish walk-forward evaluation in MLflow.

**Phase 4 — RL core (weeks 5–8).** Implement the PPO/SAC agent, reward, and promotion gate; train in sim; track learning curves.

**Phase 5 — Risk + Slack + paper (weeks 8–10).** PDT/settlement engine + micro-sizing; Slack Bolt approval flow; run the full loop on **Alpaca paper**.

**Phase 6 — Live gate (when metrics earn it).** Only after sustained paper performance: enable Alpaca live at **minimum size**, human-approved, with the kill-switch armed. (Decide Robinhood-manual vs moomoo-live vs Alpaca-live per §10.)

---

## 8. Immediate quick-win fixes (independent of the big build)
- `backend/services/claude_brain.py:71` → `f"VaR (95%): ..."` (missing opening quote; module currently won't import).
- `backend/services/trading.py:226` → `iterable(bars)` is undefined; iterate `bars` directly.
- `backend/ml/training_pipeline.py` → replace hardcoded `/workspace/project/...` paths with config-relative paths.
- `config/settings.py` → move `CLAUDE_MODEL` to a current model; ensure `.env` is gitignored.

---

## 9. Decided: live-execution venue = moomoo OpenAPI
**moomoo OpenAPI (via the OpenD gateway)** is the chosen live venue, consolidating screening + execution in one vendor. Alpaca remains the **paper** venue. Both sit behind the single `BrokerAdapter` interface (§L6) so the rest of the system is venue-agnostic and sim↔paper↔live parity holds. Robinhood is manual-ticket-only if used at all. Practical notes for implementation: moomoo requires the **OpenD desktop/headless gateway running** and a **trade-context unlock** before live orders; US-equity trading entitlements and fractional-share rules must be confirmed for the account.
