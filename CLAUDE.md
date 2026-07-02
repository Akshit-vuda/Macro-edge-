# CLAUDE.md — MacroEdge working context

Auto-loaded every session. Read this first, then `MacroEdge - Home.md`, `docs/architecture-v2.md`, and `docs/build-backlog.md`.

## What this is
An AI-supervised, self-learning macro/futures trading system starting from a **$200** account. Stack: **Claude + Obsidian** research brain, a **from-scratch reinforcement-learning** strategy engine, **Alpaca** (paper) + **moomoo** (live) execution, **Slack** human-in-the-loop approvals, moomoo/yfinance data.

## Operating model (IMPORTANT — this changed)
- It is **just the user and Claude**. No external coding agents (Antigravity/Lovable) anymore.
- **Claude builds directly**: implement tickets in this repo, write tests, run them, commit, and push to the working branch. The "delegate to Antigravity" language in `docs/build-backlog.md` is obsolete — treat those tickets as **your own** work items; the interface contracts, acceptance criteria, and Review Gate still apply as **self-review** before you push.
- Working branch: **`claude/equity-analyst-stock-research-3xu1e2`**. Commit and push there unless told otherwise.

## Key decisions (locked)
- Live venue = **moomoo OpenAPI** (via OpenD gateway); paper = **Alpaca**. Both behind ONE `BrokerAdapter` interface.
- **$200 micro-account** → fractional shares mandatory; a hard **PDT/settlement** compliance engine is required.
- **RL trained sim → paper → tiny live**, gated by walk-forward metrics + human approval. **No auto-promotion to live.**
- Robinhood has no official API → manual-ticket only, never automated.

## Where things live
- **Code:** this repo (`Akshit-vuda/Macro-edge-`).
- **Plan & tickets (canonical):** Confluence space "My first space" → *MacroEdge v2 — Development Plan & Build Tickets* (+ Epic A–F child pages + a Status Log). Mirror of `docs/build-backlog.md`.
- **Obsidian vault:** `C:\Users\akshi\Brain` (this repo lives at `Projects/MacroEdge`; journal folders `Theses/Tickers/Journal/Models/Playbooks` match ticket D3).

## Architecture at a glance (layers)
L0 foundation · L1 ingestion (moomoo/Alpaca/yfinance) · L2 DuckDB+Parquet lake + feature store · L3 brain (Claude+Obsidian+MCP+RAG) · L4 strategy/RL (Gym env + PPO/SAC + MLflow) · L5 risk/PDT compliance · L6 execution (BrokerAdapter) · L7 Slack ChatOps · L8 observability. Full detail in `docs/architecture-v2.md`.

## Build order (next up)
`A1 → A2 → B1 → B2/B3 → B4 → B5 → C1 → C2 → C5 → C4 → D1 → D3 → D4 → D2 → F1 → F2 → E1 → E2 → E3 → E4 → F3 → C3 (live, LAST)`. Phase 0 stabilization fixes are already done.

## Guardrails / conventions
- No secrets in code — read from `config.settings` / env only (see `.env.example`).
- Reuse existing modules (`backend/services/*`, `backend/ml/*`, `config/settings.py`); match their style.
- Every public function: type signature + docstring. Every change: **pytest tests** (happy path + ≥1 edge/failure).
- Brokers/data are touched **only** through the adapter interfaces — never a vendor SDK from strategy/risk code.
- **Paper/SIMULATE only** in code until an explicit live-gate; never hardcode live trading.
- Keep each commit scoped to one ticket; self-run the Review Gate (parent Confluence page) before pushing.

## Commands
```bash
# setup
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # then fill keys

# run / test
python main.py              # FastAPI on :8000
python -m pytest -q
python -m py_compile <file> # quick syntax check
docker compose up           # once A1 lands: api/worker/mlflow/grafana/prometheus
```

## First-session checklist
1. `git status` + `git log --oneline -5` — check for **uncommitted local work** (e.g. an earlier A1/B1 attempt) before starting; if present, review/salvage or discard deliberately.
2. `git fetch && git status` vs the working branch; pull if behind.
3. Confirm which ticket to build, implement it end-to-end with tests, self-run the Review Gate, commit, push.
4. Update the Confluence **Status Log** page after each ticket.
