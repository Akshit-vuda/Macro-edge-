---
type: project-home
project: MacroEdge
updated: 2026-07-01
tags: [macroedge, trading, home]
---

# 🧠 MacroEdge — Home

The index note for the MacroEdge project. Open the **Brain** vault in Obsidian and this repo (cloned at `Projects/MacroEdge`) becomes fully navigable.

## 📑 Key documents
- [[docs/architecture-v2|Architecture v2 — layered system design]] (brain, RL engine, brokers, risk, Slack)
- [[docs/build-backlog|Build Backlog — delegatable tickets A1…F3]] (what Antigravity builds, with Review Gate)
- [[research/ai-infrastructure-deep-dive|AI Infrastructure Deep-Dive]] (30-stock analysis + interlink thesis)
- `research/ai-infra-tracker.csv` — the scored watchlist (refresh quarterly)

## 🗺️ Where work lives
| Thing | Location |
|---|---|
| Plan & tickets (canonical for Antigravity) | Confluence → *MacroEdge v2 — Development Plan & Build Tickets* |
| Code | GitHub `Akshit-vuda/Macro-edge-` |
| Working branch | `claude/equity-analyst-stock-research-3xu1e2` |
| This vault | `C:\Users\akshi\Brain` |

## ✅ Status
- **Phase 0** (stabilization fixes) — done, on the working branch.
- **A1 / B1** — handed to Antigravity; work is local-only until committed & pushed (see below).
- Next after A1/B1 review: `A2 → B2/B3 → B4 → B5 → C1 …`

## 🔁 Getting Antigravity's work reviewed
From the folder where Antigravity worked:
```powershell
cd C:\Users\akshi\Brain\Projects\MacroEdge
git checkout -b antigravity/a1-b1
git add -A
git commit -m "A1: compose stack + MLflow/Prefect; B1: data provider interfaces"
git push -u origin antigravity/a1-b1
```
Then ask Claude to review the branch against the Review Gate.

## 📦 One-time move: Downloads → Brain vault
```powershell
# 1. Create the vault structure
New-Item -ItemType Directory -Force -Path C:\Users\akshi\Brain\Projects, C:\Users\akshi\Brain\Theses, C:\Users\akshi\Brain\Tickers, C:\Users\akshi\Brain\Journal, C:\Users\akshi\Brain\Models, C:\Users\akshi\Brain\Playbooks

# 2. Move the project (keeps git history + Antigravity's uncommitted work)
Move-Item "C:\Users\akshi\Downloads\Macro-edge-" "C:\Users\akshi\Brain\Projects\MacroEdge"

# 3. Open C:\Users\akshi\Brain as a vault in Obsidian (Open folder as vault)
```
The vault folders (`Theses/Tickers/Journal/Models/Playbooks`) match the auto-journaling layout in ticket **D3**, so when the journaling service ships it writes straight into this vault.
