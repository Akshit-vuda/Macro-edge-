# MacroEdge v2 — Build Backlog (delegatable work packages)

**Operating model:** You (architect/manager, via Claude) write and own these specs and **review every delivery**; implementation is delegated to coding platforms (Lovable, Cursor, Claude Code, etc.). Each ticket is **self-contained** — interface contract + acceptance criteria + tests — so a coding agent can execute it without re-deriving context. Nothing is "done" until it passes the **Review Gate** (§3).

Companion docs: `docs/architecture-v2.md` (the design). Live venue = **moomoo OpenAPI**; paper = **Alpaca**.

---

## 1. How we work (manager → delegate → review)

1. **Manager (Claude/you)** hands a coding platform a single ticket below, verbatim.
2. **Delegate** implements on a branch, runs the ticket's tests, opens a PR.
3. **Manager** runs the **Review Gate** (§3): reads the diff, checks the interface contract and acceptance criteria, runs tests, fixes small gaps directly, sends larger gaps back with specific notes.
4. Merge only when green. Move to the next ticket respecting `Depends-on`.

**Golden rules for every delegate (put this in the platform's system prompt):**
- Match existing code style; **reuse** existing modules (`backend/services/*`, `backend/ml/*`, `config/settings.py`) — don't reinvent.
- **No secrets in code** — read from `config.settings` / env only.
- Every public function gets a **type signature + docstring**; every ticket ships **pytest tests**.
- Talk to brokers/data **only through the adapter interfaces** defined here — never call a vendor SDK directly from strategy/risk code.
- **Paper/SIMULATE only** until the live-gate; never hardcode live trading.

## 2. Delegation routing (which platform for which work)

| Work type | Best-fit delegate |
|---|---|
| Backend Python (adapters, OMS, ML, data) | Cursor / Claude Code (repo-aware, test-driven) |
| Frontend React dashboard + Slack UX | Lovable (TS/Tailwind/shadcn) |
| Glue/infra (Docker, Prefect, MLflow) | Cursor / Claude Code |
| Tricky/correctness-critical (RL reward, PDT engine, risk) | Keep with Claude here for spec + review; delegate only the boilerplate |

## 3. Review Gate (Definition of Done — the manager checklist)

A ticket merges only when ALL hold:
- [ ] Interface contract implemented **exactly** as specified (names, signatures, return shapes).
- [ ] All acceptance criteria demonstrably met.
- [ ] `pytest` green; new tests cover the happy path + at least one failure/edge case.
- [ ] `python -m py_compile` clean; no import errors; no hardcoded absolute paths or secrets.
- [ ] Only talks to vendors through the defined adapters.
- [ ] Diff is scoped to the ticket (no drive-by rewrites).

---

## 4. Status: Phase 0 (DONE — by manager, already in repo)
- [x] `.gitignore` + `.env.example` added; `.env` untracked.
- [x] Fixed import-blocking bug `claude_brain.py` (VaR f-string).
- [x] Fixed `trading.py` `iterable(bars)` bug.
- [x] Removed hardcoded `/workspace/project` paths in `training_pipeline.py` (now repo-relative).
- [x] `CLAUDE_MODEL` → env-driven, current model.

---

## 5. EPIC A — Foundation & infra

### A1 · Compose stack + MLflow + Prefect skeleton
- **Depends-on:** —  · **Delegate:** Cursor/Claude Code
- **Objective:** extend `docker-compose.yaml` with services: `api` (existing FastAPI), `worker` (Prefect), `mlflow`, `grafana`, `prometheus`. Add a `Makefile` (`make up`, `make test`, `make lint`).
- **Acceptance:** `docker compose up` starts all services; MLflow UI reachable at `:5000`; Prefect agent runs a trivial flow; `make test` runs pytest.
- **Tests:** a smoke test that imports each service module without error.

### A2 · Settings hardening + secrets
- **Depends-on:** —  · **Delegate:** Cursor
- **Objective:** extend `config/settings.py` with the new keys in `.env.example` (moomoo, slack, mlflow, claude cap). Add a `validate_settings()` that warns on missing critical keys at startup.
- **Acceptance:** importing settings with a missing key logs a warning, never crashes; `CLAUDE_DAILY_USD_CAP` is read as float.
- **Tests:** unit test for `validate_settings()` with/without keys.

---

## 6. EPIC B — Data ingestion & lake

### B1 · Provider interfaces
- **Depends-on:** —  · **Delegate:** Cursor
- **Objective:** define abstract base classes in `backend/services/data_providers/base.py`.
- **Interface contract:**
  ```python
  class MarketDataProvider(ABC):
      def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame: ...  # cols: ts,open,high,low,close,volume
  class NewsProvider(ABC):
      def get_news(self, symbols: list[str], since: datetime) -> list[NewsItem]: ...
  class ScreenerProvider(ABC):
      def screen(self, criteria: dict) -> pd.DataFrame: ...  # cols incl. symbol
  ```
- **Acceptance:** `NewsItem` is a typed dataclass (`symbol, ts, source, headline, summary, url`). Interfaces import cleanly.
- **Tests:** a `FakeProvider` implements each and is exercised.

### B2 · Alpaca + yfinance adapters
- **Depends-on:** B1  · **Delegate:** Cursor
- **Objective:** `AlpacaDataProvider` (wrap existing `AlpacaClient.get_bars`, normalize to the B1 DataFrame schema) and `YahooNewsProvider` (yfinance `.news` + RSS from `settings.RSS_FEEDS`).
- **Acceptance:** both return the exact schemas from B1; network errors return empty + log, never raise.
- **Tests:** mock the SDK; assert schema/columns and graceful failure.

### B3 · moomoo OpenD ingestion (screening + bars)
- **Depends-on:** B1  · **Delegate:** Cursor
- **Objective:** `MoomooDataProvider` + `MoomooScreener` using `futu`/`moomoo` SDK against the OpenD gateway (`MOOMOO_OPEND_HOST/PORT`). Read-only here (no trading).
- **Acceptance:** connects to OpenD if running; `screen()` returns a DataFrame with `symbol`; clean error if OpenD is down.
- **Tests:** mock the SDK connection; assert schema + down-gateway handling.

### B4 · DuckDB/Parquet lake + validation
- **Depends-on:** B2  · **Delegate:** Cursor
- **Objective:** `backend/services/lake.py` — write provider output to Parquet partitioned by `symbol/date`; query via DuckDB. Validate every batch with **pandera** schemas; reject/quarantine bad rows.
- **Acceptance:** `lake.write_bars(df)` then `lake.read_bars(symbol, start, end)` round-trips; a malformed batch is rejected with a logged reason.
- **Tests:** round-trip test + a validation-failure test.

### B5 · Versioned feature store
- **Depends-on:** B4  · **Delegate:** Cursor
- **Objective:** `backend/ml/feature_store.py` — build features (reuse `backend/ml/technical_analysis.py`) keyed by `(symbol, ts, feature_set_version)`; same code path for train + serve (no skew).
- **Acceptance:** `build_features(symbol, version)` is deterministic; serving a single latest row matches the training definition exactly.
- **Tests:** determinism test (same input → same output); train-vs-serve parity test.

---

## 7. EPIC C — Broker adapter, OMS & compliance

### C1 · BrokerAdapter interface
- **Depends-on:** —  · **Delegate:** Cursor
- **Objective:** `backend/services/brokers/base.py` abstract `BrokerAdapter`.
- **Interface contract:**
  ```python
  class BrokerAdapter(ABC):
      def get_account(self) -> AccountState: ...
      def get_positions(self) -> list[Position]: ...
      def submit_order(self, intent: OrderIntent) -> OrderResult: ...   # idempotent on intent.client_id
      def cancel_order(self, order_id: str) -> None: ...
      def is_market_open(self) -> bool: ...
  ```
  `OrderIntent` carries `client_id, symbol, side, qty|notional, type, limit_price, tif, rationale, signal_id, model_version`.
- **Acceptance:** typed dataclasses for `AccountState/Position/OrderIntent/OrderResult`; provenance fields (`rationale, signal_id, model_version`) are required on `OrderIntent`.
- **Tests:** a `FakeBroker` implements the interface and round-trips an order.

### C2 · AlpacaAdapter (paper)
- **Depends-on:** C1  · **Delegate:** Cursor
- **Objective:** implement `BrokerAdapter` over the existing `AlpacaClient`; map fractional notional; enforce idempotency on `client_id`.
- **Acceptance:** paper order via `OrderIntent` returns a populated `OrderResult`; duplicate `client_id` does not double-submit.
- **Tests:** mock Alpaca; assert mapping + idempotency.

### C3 · MoomooAdapter (live, SIMULATE first)
- **Depends-on:** C1  · **Delegate:** Cursor
- **Objective:** implement `BrokerAdapter` over `futu`/`moomoo` trade SDK via OpenD; handle **trade-context unlock** (`MOOMOO_TRADE_PWD`), `MOOMOO_TRADE_ENV` (default `SIMULATE`), US-equity routing, qty/fractional rules.
- **Acceptance:** with `TRADE_ENV=SIMULATE`, places a sim order end-to-end; **refuses to run REAL** unless an explicit `allow_live=True` flag is passed (defense-in-depth).
- **Tests:** mock SDK; assert unlock flow, SIMULATE default, and the REAL guard.

### C4 · OMS (order management + reconciliation)
- **Depends-on:** C2  · **Delegate:** Cursor
- **Objective:** `backend/services/oms.py` — accept `OrderIntent`, run the pre-trade check chain (calls C5 + risk), submit via the active adapter, persist order/fill, reconcile state, write a journal entry.
- **Acceptance:** an intent that fails any pre-trade check is rejected with a reason and never submitted; every fill is persisted with full provenance.
- **Tests:** reject-on-failed-check test; fill-persistence test.

### C5 · Risk + PDT/settlement engine (correctness-critical)
- **Depends-on:** C1  · **Delegate:** spec+review by Claude; boilerplate by Cursor
- **Objective:** `backend/services/compliance.py` — hard pre-trade gate: micro-account vol-targeted fractional sizing, exposure caps, `-8%` drawdown kill-switch (reuse `risk_management.py`), and a **PDT counter** (≤3 day-trades / rolling 5 business days under $25k) + cash-settlement tracker.
- **Acceptance:** the 4th day-trade in a 5-day window is **blocked**; unsettled cash cannot be reused in a cash account; sizing returns fractional notional, never a flat 2%.
- **Tests:** PDT 4th-trade block test; settlement-reuse block test; sizing test at $200.

---

## 8. EPIC D — Brain (Claude + Obsidian)

### D1 · Wire ClaudeSupervisor to real data + token cap
- **Depends-on:** B5  · **Delegate:** Cursor
- **Objective:** connect the existing `ClaudeSupervisor` methods to real portfolio/signal/risk data; implement `enforce_daily_token_cap` for real against `CLAUDE_DAILY_USD_CAP`; add prompt caching.
- **Acceptance:** daily brief runs on real data; exceeding the cap blocks further calls + alerts; token spend is logged per call.
- **Tests:** cap-enforcement test (mock spend over cap → blocked).

### D2 · MCP server exposing system tools
- **Depends-on:** C4, D1  · **Delegate:** Cursor
- **Objective:** an MCP server exposing `get_portfolio`, `get_signals`, `get_risk`, `query_journal`, `propose_trade` so Claude (app + Claude Code) can drive the system via tool-use.
- **Acceptance:** each tool returns typed JSON; `propose_trade` creates an `OrderIntent` that still must pass C5 + Slack approval (never auto-executes).
- **Tests:** tool-schema test; `propose_trade` cannot bypass the approval gate.

### D3 · Obsidian vault + auto-journaling
- **Depends-on:** C4  · **Delegate:** Cursor
- **Objective:** `backend/services/journal.py` — write structured Markdown (trade tickets, daily briefs, post-mortems, model cards) into the vault layout (`/Theses,/Tickers,/Journal,/Models,/Playbooks`).
- **Acceptance:** every fill produces a `/Journal/<date>` note linking signal + rationale + outcome; notes are valid Markdown with frontmatter.
- **Tests:** a fill produces a parseable note with required frontmatter fields.

### D4 · LanceDB RAG over the vault
- **Depends-on:** D3  · **Delegate:** Cursor
- **Objective:** embed vault notes into **LanceDB** (local); `query_journal(q)` returns relevant notes for Claude grounding.
- **Acceptance:** querying returns semantically relevant notes; index updates incrementally on new notes.
- **Tests:** retrieval test on a seeded vault.

---

## 9. EPIC E — Strategy & RL (the from-scratch engine)

### E1 · Supervised signal models on real data
- **Depends-on:** B5  · **Delegate:** Cursor
- **Objective:** retrain directional/regime/volatility/sentiment models (`backend/ml/models/*`) on **real** feature-store data with **walk-forward** splits; log to MLflow. Keep the synthetic generator as a sandbox only.
- **Acceptance:** each model logs OOS metrics to MLflow; no leakage (strictly time-ordered splits).
- **Tests:** leakage guard test (train ts < test ts); MLflow logging test.

### E2 · Gym backtest environment
- **Depends-on:** B5, C1  · **Delegate:** spec by Claude; impl by Cursor
- **Objective:** `backend/ml/rl/env.py` — `gymnasium.Env` wrapping a backtester (start vectorbt). State = signals + positions + cash + PDT/settlement + drawdown; action = target fractional weights; reward = risk-adjusted (`Δequity − λ·drawdown − costs − turnover − PDT_penalty`).
- **Acceptance:** env passes `gymnasium` API checks; transaction costs/slippage are inside the reward; deterministic with a seed.
- **Tests:** `gymnasium.utils.env_checker`; reward includes cost terms (assert a costed step < frictionless).

### E3 · RL agent (PPO/SAC) + promotion gate
- **Depends-on:** E2  · **Delegate:** spec by Claude; impl by Cursor
- **Objective:** train **Stable-Baselines3 PPO** (and SAC for continuous sizing) on E2; checkpoints to `backend/ml/trained_models/` (gitignored); promotion gate sim→paper→live with pre-registered thresholds (OOS Sharpe, max-DD, min trades); **no auto-promotion to live**.
- **Acceptance:** a trained policy is evaluated walk-forward and only flagged "paper-ready" if it clears thresholds; live requires a manual flag.
- **Tests:** promotion-gate logic test (below-threshold policy is NOT promoted).

### E4 · Learning-progress tracking
- **Depends-on:** E3  · **Delegate:** Cursor (backend) + Lovable (UI panel)
- **Objective:** log RL curves (episode reward, OOS Sharpe, entropy, value loss) to MLflow/W&B; expose a `/learning` dashboard panel + Slack milestone alerts; weekly Claude "report card".
- **Acceptance:** training runs appear in MLflow with curves; dashboard reads them; a milestone (e.g. OOS Sharpe ≥ 1.0) fires a Slack alert.
- **Tests:** metrics-logging test; alert-trigger test.

---

## 10. EPIC F — Slack ChatOps

### F1 · Slack Bolt app (Socket Mode)
- **Depends-on:** A1  · **Delegate:** Cursor
- **Objective:** `backend/services/slackbot.py` using **slack-bolt** + Socket Mode (`SLACK_APP_TOKEN`). Commands: `/brief`, `/positions`, `/signals`, `/killswitch`.
- **Acceptance:** commands return live data; `/killswitch` flips the drawdown halt flag.
- **Tests:** command handlers unit-tested with a mock Slack client.

### F2 · Trade approval flow (human-in-the-loop)
- **Depends-on:** F1, C4  · **Delegate:** Cursor
- **Objective:** when D2/strategy proposes an `OrderIntent`, post it to `SLACK_APPROVAL_CHANNEL` with **Approve/Reject** buttons; Approve → OMS submit; Reject → journal + discard. Live orders **require** this approval.
- **Acceptance:** no live/paper order from the auto-pipeline executes without an Approve click; Reject is recorded with reason.
- **Tests:** approve→submit and reject→no-submit interaction tests.

### F3 · Alerts
- **Depends-on:** F1  · **Delegate:** Cursor
- **Objective:** push fills, drawdown breaches, anomalies (via `ClaudeSupervisor.anomaly_alert`), and learning milestones to Slack.
- **Acceptance:** each event type posts a formatted message; rate-limited to avoid spam.
- **Tests:** formatting + rate-limit tests.

---

## 11. Recommended delivery order (dependency-correct)
`A1 → A2 → B1 → B2/B3 → B4 → B5 → C1 → C2 → C5 → C4 → D1 → D3 → D4 → D2 → F1 → F2 → E1 → E2 → E3 → E4 → F3 → C3 (live, last) → live-gate`

Live (`C3` REAL + moomoo) is **deliberately last**, only after paper performance and the promotion gate earn it.
