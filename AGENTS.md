# AGENTS.md — MacroEdge multi-agent operating guide

How agents build MacroEdge: roles, rules, how to think, how to report, and how to
run **several tickets in parallel** without stepping on each other. Read
`CLAUDE.md` first for working context and guardrails; this file is the
orchestration layer on top.

---

## 1. The outcome (what "done" means)

An AI-supervised, self-learning macro trading system starting from a **$200**
account: **Claude + Obsidian** research brain, a **from-scratch RL** strategy
engine, **Alpaca** (paper) + **moomoo** (live) execution behind one
`BrokerAdapter`, **Slack** human-in-the-loop approvals. The system is "done" when
the full loop runs on **Alpaca paper**, gated by walk-forward metrics, with a
hard **PDT/settlement compliance** engine and a Slack **approve/reject** gate on
every order. Live (moomoo REAL) is deliberately **last**, behind a promotion gate
and human sign-off. Full spec: `docs/architecture-v2.md`, `docs/build-backlog.md`,
Confluence page `557057`.

**Non-negotiables that shape every ticket:** paper/SIMULATE only in code until an
explicit live-gate; a real PDT/settlement gate (not advice); fractional sizing
(not a flat 2%); every order carries provenance (signal_id, model_version,
rationale); no live order without risk-pass **and** human approval.

---

## 2. Roles

| Role | Who | Owns |
|---|---|---|
| **Orchestrator** | the main Claude session | The plan, context curation, dispatch, review, **all git commits + pushes**, and syncing Jira + Confluence. The orchestrator is the ONLY thing that runs `git` and `pip`. |
| **Implementer** | a dispatched sub-agent | ONE ticket, TDD, edits only its files, returns a dev-note. Never commits, never runs git/pip installs that race. |
| **Reviewer** | a dispatched sub-agent | Independent review of one ticket: spec compliance + code quality + over-engineering + test-coverage. Reports findings by severity; does not fix. |
| **Fixer** | a dispatched sub-agent | Applies Critical/Important review findings, re-runs the covering tests, reports. |

Correctness-critical tickets (C5 PDT/risk, E2/E3 RL reward + promotion gate) — the
**orchestrator owns the spec and review directly**; delegate only boilerplate.

---

## 3. How agents work (rules — put these in every implementer prompt)

- **TDD.** Tests first (happy path + ≥1 edge/failure), then implement.
- **Reuse, don't reinvent.** Match the style of the nearest sibling (e.g. a new
  provider mirrors `backend/services/data_providers/moomoo_provider.py`). Look
  before you write.
- **Vendors only through adapters.** Strategy/risk code never calls a broker/data
  SDK directly — only the B1 interfaces / C1 `BrokerAdapter`.
- **Never raise on I/O.** Network/SDK errors → return empty (right-shaped) + log a
  warning. Callers degrade gracefully.
- **No secrets in code.** Read from `config.settings` / env only. `.env` is
  gitignored; `.env.example` holds placeholders only — never real keys.
- **Type hints + docstrings** on every public function. Keep the diff **scoped to
  the ticket** — no drive-by rewrites.
- **Verify** with the project venv:
  `C:\Users\akshi\Brain\projects\Macro-edge-\.venv\Scripts\python.exe` —
  `python -m py_compile <files>` then `python -m pytest <your test files> -q`
  (set `PYTHONPATH` to the repo root if imports fail).

## 4. How agents think

- **Climb the lazy ladder** (YAGNI → reuse → stdlib → native → one line → minimal
  code that works). The first lazy solution that actually works — *after* you
  understand the problem — is the right one.
- **Root cause, not symptom.** Before editing a shared function, grep its callers.
  Fix once where all callers route through.
- **Read fully before editing.** Trace the real flow end to end. A small diff in
  the wrong place is a second bug.
- **Stay in your lane.** Touch only your ticket's files. If you spot an
  out-of-scope problem, **report it — don't fix it inline** (the orchestrator will
  file it as its own ticket/bug, as happened with the models-collision bug).

## 5. How agents report (the dev-note — required, every ticket)

Every implementer/fixer ends with a **dev-note**, returned to the orchestrator
(the agent does NOT commit):

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
Files: <created/changed>
Interface: <exact signatures / schema / column list>
Verification: <command run> → <pass/fail counts, output tail>
Decisions: <choices + why>
Deviations / concerns: <anything off-spec, or "none">
```

The **orchestrator** then, per ticket: reviews → commits (scoped, one ticket per
commit, `Co-Authored-By: Claude ...`) → pushes → transitions the Jira ticket →
appends the dev-note to Confluence **Development Notes** (`1343489`) and updates
the **Status Log** (`884738`). This is the durable trail of *why* the code looks
the way it does.

## 6. Running more than one ticket at a time

Parallelism is allowed and encouraged — but only when it's genuinely safe.

**Eligible batch:** tickets that are all (a) unblocked — every `Blocks`
predecessor is Done — and (b) **file-disjoint** (no shared source/test files).
Check the dependency graph on the Jira KAN board / `docs/build-backlog.md`
"Depends-on" before batching.

- ✅ Safe example: **B4** (`backend/services/lake.py`) + **C1**
  (`backend/services/brokers/base.py`) — different files, no dependency edge.
- ❌ Not safe: **B4 + B5** (B5 depends on B4); or two tickets that both edit
  `config/settings.py` / `requirements.txt`.

**Environment constraints (important — learned the hard way):**
- **Worktree isolation is unavailable** in this setup. So parallel implementers
  must edit **disjoint files** and must **NOT run `git` or `pip`** — those race on
  the index / the venv. The orchestrator serializes all git and dependency work.
- **One pusher.** Only the orchestrator commits and pushes. Integrate agent
  outputs **sequentially, in dependency order**.

**Batch procedure:**
1. Orchestrator curates each ticket's brief (interfaces, sibling to mirror,
   constraints) and dispatches the implementers in parallel.
2. On return, orchestrator runs the **full** test suite once, then reviews each
   ticket (self or Reviewer agent) — spec + quality + over-engineering + coverage.
3. Fix Critical/Important findings (Fixer agent), re-review.
4. Commit each ticket as its own scoped commit, in dependency order; push.
5. Update Jira (status) + Confluence (dev-note + Status Log) for each.

## 7. Where everything lives (keep in sync after each ticket)

- **Code:** this repo (`Akshit-vuda/Macro-edge-`), branch
  `claude/equity-analyst-stock-research-3xu1e2`.
- **Plan (canonical):** Confluence `557057` · **Dev log:** `1343489` ·
  **Status Log:** `884738` (site `akki0102.atlassian.net`, space `MFS`,
  cloudId `6e98d988-6393-4d87-ae14-b877b9dacc94`).
- **Jira mirror:** board **KAN "Macro Edge"** (Epics A–F, tasks A1…F3, `Blocks`
  links). Flip a ticket's status + comment when its work lands.
- **Obsidian vault:** `C:\Users\akshi\Brain` (journal folders match ticket D3).

## 8. Delivery order

`A1 → A2 → B1 → B2/B3 → B4 → B5 → C1 → C2 → C5 → C4 → D1 → D3 → D4 → D2 → F1 → F2
→ E1 → E2 → E3 → E4 → F3 → C3 (live, LAST) → live-gate`

**Done + pushed:** A1, A2, B1, B2, B3, and the models-collision bug fix. **Next:**
B4. Independent tickets from here that can be batched: B4 ∥ C1 (disjoint files).
