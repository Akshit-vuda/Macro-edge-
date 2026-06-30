# The AI Infrastructure Stack — Senior Analyst Deep-Dive

**Prepared for:** MacroEdge Intelligence Platform
**Analyst desk view | Data pulled via live web search 2026-06-30**
**Source universe:** the 6-layer "AI infrastructure" map (equity.by.mp), ~30 names

> **This is analysis, not financial advice.** Prices and financials were web-sourced on 2026-06-30 and several momentum names traded with wide intraday spreads and stale aggregator quotes (flagged inline). **Verify every number against a live feed before acting.** Foreign-listed names (TSMC ADR aside; SK hynix, Samsung, Kioxia) carry FX and liquidity considerations.

---

## PART I — THE INTERLINK THESIS (read this first)

The infographic lays the AI economy out as **six serial layers**. The single most important insight for an investor is that this is **one trade wearing thirty tickers**: a vertically-dependent supply chain where the same dollar of hyperscaler capex propagates through every layer.

```
  CAPITAL FLOWS DOWN ▼                            PHYSICAL DEPENDENCY FLOWS UP ▲
  (hyperscaler/sovereign AI $)                    (no lower layer ships without the one above)

  L1  Fab Enablers      ASML ▸ TSMC ▸ KLA ▸ Lam        ── the tools & the foundry
  L2  Silicon           NVIDIA ▸ Broadcom ▸ AMD ▸ Intel ── the compute
  L3  Memory            SK hynix ▸ Micron ▸ Samsung ▸ Kioxia/SanDisk/WDC/Seagate ── HBM on the package
  L4  Networking/Optics Astera ▸ Marvell ▸ Arista ▸ Coherent ▸ Lumentum ▸ Rambus ▸ SiMotion ── the wiring
  L5  Neoclouds         CoreWeave ▸ Nebius ▸ IREN ▸ Applied Digital ── the rentable compute
  L6  Energy/Power      Constellation ▸ Vistra ▸ GE Vernova ▸ NextEra ▸ Bloom ▸ Quanta ▸ Eos ── the electrons
```

### 1. The bottleneck keeps migrating — follow it, because that's where pricing power sits.
- **2023:** the bottleneck was **GPUs** (NVIDIA).
- **2024–25:** it moved up the package to **HBM memory + TSMC CoWoS advanced packaging**.
- **2026 (now):** it has split into **optics** (NVIDIA just took **$2B strategic stakes in *both* Coherent and Lumentum** — a flashing signal that the EML-laser supply chain is the new choke point) **and power** (turbine slots booked through 2030, multi-year grid-interconnection queues).
- **Investable read:** the layer that is *currently* supply-constrained earns peak margins. Right now that is **memory (HBM)**, **optics**, and **power generation/equipment** — not the GPU itself, where the multiple has actually *compressed*.

### 2. Where the margin pool actually sits — own the monopolies/oligopolies.
The profit concentrates at the **non-substitutable nodes**, and bleeds out at the **commoditized/competitive** ones:

| Pricing power | Nodes | Why |
|---|---|---|
| **Monopoly** | ASML (EUV), TSMC (leading-edge foundry), NVIDIA (CUDA) | Literally irreplaceable; multi-decade lead |
| **Tight oligopoly** | HBM (SK hynix/Micron/Samsung), EML optics (Coherent/Lumentum), large gas turbines (GE Vernova), HDD (WDC/Seagate), custom ASIC (Broadcom/Marvell) | 2–3 players, supply discipline, structural scarcity |
| **Competitive / commoditizing** | NAND (Kioxia/SanDisk), neoclouds (CoreWeave/Nebius/IREN/APLD), grid storage (Eos) | Price-takers, capex-heavy, thin or negative margins |

### 3. NVIDIA is the keystone — and the source of the system's biggest *hidden* risk.
NVIDIA is simultaneously the chain's **supplier** (GPUs), **allocator** (who gets chips), **customer** (it signs cloud deals with IREN, CoreWeave), **and equity investor** (stakes in Nebius, Coherent, Lumentum; deals with CoreWeave). This creates **circular financing**: NVIDIA invests in / commits to buy from neoclouds and optics suppliers, who in turn buy NVIDIA silicon. It magnifies the up-cycle — but it means **a single demand-side wobble (hyperscaler capex digestion) de-rates the entire stack at once.** Treat the 30 names as **highly correlated**, not diversified.

### 4. The daisy-chain concentration risk.
**Microsoft → CoreWeave (~67% of CRWV revenue) → leases data centers from Applied Digital.** Stress at the top of that chain propagates straight down. Note the contrary tell: **NVIDIA *exited* its Applied Digital stake** — a signal worth respecting.

### 5. The cleanest "priced-in" screen we found.
A striking number of momentum names now trade **ABOVE their average analyst price target** — meaning the Street's estimates are *chasing the stock*, not leading it. This is the single best caution flag in the basket:

> **Trading above consensus target (good news arguably over-priced):** KLA, Lam Research, SanDisk, Western Digital, Seagate, Astera Labs, Marvell, Bloom Energy, AMD (≈at), Intel (≈25% *above* a Hold-rated target).
> **Still trading below target with upside (Street not yet caught up):** NVIDIA, Broadcom, TSMC, Micron, SK hynix, Constellation, Vistra, NextEra, Quanta, Rambus.

### 6. Portfolio architecture the desk would recommend (a barbell).
- **Core (own the chokepoints + picks-and-shovels):** TSMC, NVIDIA, Broadcom, SK hynix/Micron (HBM), KLA/Lam (WFE), GE Vernova/Quanta (buildout), Vistra/Constellation (power). These capture the theme *regardless of which model or chip wins*.
- **Satellite (high-beta, size small):** optics (Coherent, Lumentum, Astera), neoclouds (CoreWeave is the contrarian one — down ~27% on the year while peers ran), Bloom.
- **Avoid / show-me:** Intel (fundamentals lag the price by ~25%), SanDisk (>4,000% since spin, targets below price), Eos (pre-profit micro-cap).
- **The defensives *within* the theme** — names with contracted backlog and low multiples — are **Vistra, Micron (forward P/E ~8–9x), TSMC, Constellation**. If you want exposure but fear a capex digestion, these have the most valuation cushion.

### 7. The one risk that rules them all.
**Every name here is long the same factor: AI capex.** The bull case is a multi-year super-cycle (NVIDIA's ~$1T Blackwell+Rubin guide, $100B+ Broadcom AI-semi FY27 target, sold-out HBM through 2027). The bear case is that hyperscaler capex *digests* and the whole correlated stack de-rates together. Position sizing — not stock selection — is the dominant risk lever in this basket.

---

## PART II — SCOREBOARD (all 30, ranked)

Rubric (100 pts): **Financial Health & Profitability (25) · Growth & Forward Estimates (20) · Valuation vs Peers/History (20) · Catalysts & Momentum (20) · Risk Profile (15, inverse)**

| Rank | Ticker | Company | Layer | Score | Fin/25 | Grw/20 | Val/20 | Cat/20 | Rsk/15 | Consensus |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | NVDA | NVIDIA | Silicon | **87** | 24 | 19 | 17 | 17 | 10 | Strong Buy |
| 2 | MU | Micron | Memory | **85** | 22 | 20 | 18 | 17 | 8 | Strong Buy |
| 3 | AVGO | Broadcom | Silicon | **84** | 23 | 19 | 15 | 17 | 10 | Strong Buy |
| 4 | TSM | TSMC | Fab | **83** | 23 | 18 | 17 | 16 | 9 | Strong Buy |
| 4 | 000660 | SK hynix | Memory | **83** | 22 | 20 | 16 | 16 | 9 | Strong Buy |
| 6 | VST | Vistra | Energy | **80** | 20 | 16 | 17 | 17 | 10 | Strong Buy |
| 7 | CEG | Constellation | Energy | **79** | 20 | 17 | 16 | 16 | 10 | Buy |
| 8 | 005930 | Samsung | Memory | **78** | 20 | 17 | 15 | 16 | 10 | Buy |
| 9 | ANET | Arista | Networking | **77** | 22 | 17 | 13 | 15 | 10 | Strong Buy |
| 10 | PWR | Quanta | Energy | **75** | 21 | 16 | 13 | 14 | 11 | Buy |
| 11 | MRVL | Marvell | Networking | **73** | 19 | 18 | 11 | 16 | 9 | Buy |
| 12 | ASML | ASML | Fab | **72** | 22 | 15 | 12 | 14 | 9 | Strong Buy |
| 12 | AMD | AMD | Silicon | **72** | 18 | 18 | 10 | 17 | 9 | Strong Buy |
| 14 | RMBS | Rambus | Networking | **71** | 20 | 15 | 13 | 13 | 10 | Buy |
| 14 | LITE | Lumentum | Networking | **71** | 18 | 18 | 10 | 17 | 8 | Buy |
| 14 | NEE | NextEra | Energy | **71** | 18 | 14 | 16 | 13 | 10 | Buy |
| 17 | KLAC | KLA | Fab | **69** | 21 | 14 | 10 | 15 | 9 | Buy |
| 17 | LRCX | Lam Research | Fab | **69** | 20 | 16 | 9 | 16 | 8 | Buy |
| 17 | STX | Seagate | Memory | **69** | 19 | 15 | 13 | 14 | 8 | Buy |
| 17 | SIMO | Silicon Motion | Networking | **69** | 17 | 16 | 13 | 14 | 9 | Strong Buy |
| 21 | GEV | GE Vernova | Energy | **68** | 18 | 18 | 8 | 16 | 8 | Buy |
| 21 | KIOXIA | Kioxia (285A) | Memory | **68** | 17 | 15 | 15 | 13 | 8 | Buy |
| 23 | COHR | Coherent | Networking | **67** | 15 | 16 | 11 | 17 | 8 | Buy |
| 24 | WDC | Western Digital | Memory | **67** | 19 | 14 | 12 | 13 | 9 | Strong Buy |
| 25 | ALAB | Astera Labs | Networking | **66** | 19 | 18 | 6 | 16 | 7 | Buy |
| 25 | BE | Bloom Energy | Energy | **66** | 16 | 19 | 7 | 17 | 7 | Buy |
| 27 | NBIS | Nebius | Neocloud | **64** | 14 | 19 | 7 | 17 | 7 | Mod. Buy |
| 28 | CRWV | CoreWeave | Neocloud | **62** | 12 | 19 | 12 | 16 | 3 | Buy |
| 29 | SNDK | SanDisk | Memory | **60** | 17 | 17 | 6 | 14 | 6 | Buy |
| 30 | IREN | IREN | Neocloud | **58** | 11 | 18 | 9 | 15 | 5 | Buy |
| 31 | APLD | Applied Digital | Neocloud | **57** | 11 | 17 | 9 | 14 | 6 | Strong Buy |
| 32 | INTC | Intel | Silicon | **47** | 8 | 11 | 7 | 15 | 6 | Hold |
| 33 | EOSE | Eos Energy | Energy | **52** | 8 | 16 | 11 | 12 | 5 | Buy/Hold |

*(Ranks 32–33 sort by score; Intel and Eos are the two lowest on fundamentals.)*

---

## PART III — COMPANY DEEP-DIVES BY LAYER

Each entry follows your 7-part framework, condensed, ending in sub-scores and a one-line verdict. Prices as of **2026-06-30** unless noted.

---
### LAYER 1 — MANUFACTURING ENABLERS

#### TSMC (NYSE: TSM) — $468.80 · Score 83/100
1. **Overview.** World's dominant pure-play foundry (~60%+ of foundry revenue, the lion's share of <7nm). Fabs for the entire fabless ecosystem; **HPC = 61% of Q1'26 revenue**. Moat: process leadership (N2 in HVM since Q4'25), unmatched yield/scale, and **CoWoS advanced packaging** — the physical bottleneck for every AI accelerator.
2. **Financials.** Rev 2023 $69.3B → 2024 $90.1B (+30%) → 2025 ~$120B+ (+31.6%). Q1'26 rev $35.9B (**+40.6% YoY**), GM 66.2%. FY25 margins: gross ~60%, op ~51%, net ~45% — best-in-class. FCF ~$33B, net cash. P/E ~29x, EV/EBITDA ~18x — **cheapest of the fab group**.
3. **Outlook.** Q2'26 guide $39.0–40.2B; FY26 revenue growth **>30% USD**; record capex **$52–56B** (AI-driven).
4. **Catalysts.** Mid-July Q2 earnings; **monthly revenue prints**; N2 ramp / A16 roadmap (2H26–27); Arizona output.
5. **Risks.** Taiwan-concentration geopolitics, US/China controls, chip-tariff risk, cyclicality. Near 52-wk high but valuation least-stretched of the group → only partly priced in.
6. **Sentiment.** 52-wk $221.18–$476.79. **Strong Buy**, avg target $487.56 (high $700).
7. **Interlink.** The keystone: fabricates NVIDIA/AMD/Broadcom/Marvell silicon, its CoWoS binds HBM to logic, and its capex *is* the demand for ASML/KLA/Lam.
> Sub-scores — Fin 23 · Grw 18 · Val 17 · Cat 16 · Rsk 9. **Verdict: the lowest-risk way to own the entire stack at a reasonable multiple — core holding.**

#### ASML (NASDAQ: ASML) — €1,673.60 · Score 72/100
1. **Overview.** Sole supplier of EUV lithography (Low-NA + High-NA) — the irreplaceable tool for sub-7nm. Strongest moat in tech.
2. **Financials.** Rev 2024 €28.3B → 2025 €32.7B; Q1'26 net sales €8.8B (+13% YoY), GM 52.8%. Backlog ~€38.8B. FCF ~€11B. **P/E ~62x (richest of the fab group; 5-yr avg ~40x).**
3. **Outlook.** FY26 guide raised to **€36–40B**; ≥60 EUV systems in 2026, ≥80 in 2027; €44–60B revenue target by 2030.
4. **Catalysts.** Mid-July Q2 (bookings is the swing number); High-NA EXE:5200 adoption 2026–27.
5. **Risks.** China ~20% of revenue + export-control tightening; **lumpy bookings** swing the stock; rich multiple near 52-wk high.
6. **Sentiment.** 52-wk €587.80–€1,711.40. **Strong Buy**, US-line avg ~$2,019.
7. **Interlink.** The single upstream chokepoint — no EUV, no leading-edge logic *or* advanced memory anywhere below it.
> Sub-scores — Fin 22 · Grw 15 · Val 12 · Cat 14 · Rsk 9. **Verdict: best moat in the basket, but you pay 62x and ride lumpy orders — own it, size for volatility.**

#### KLA Corp (NASDAQ: KLAC) — ~$302 (post 10-for-1 split, high-vol day) · Score 69/100
1. **Overview.** ~50%+ share of process control / inspection & metrology — the clear #1; mission-critical to fab yield. Advanced-packaging inspection is a growth vector.
2. **Financials.** FY25 (Jun) rev $12.16B; Q2'FY26 rev $3.30B, non-GAAP GM 62.6% — among the highest in equipment. Record FCF. **P/E ~43x / EV/EBITDA ~34x.**
3. **Outlook.** Jun-26 quarter guide $3.575B ±$200M; CY26 GM ~62% (near-term DRAM-component cost headwind).
4. **Catalysts.** Late-July earnings; advanced-packaging adoption; post-split liquidity/index effects; dividend hike.
5. **Risks.** China exposure; DRAM cost headwind; **average target (~$210 split-adj) sits BELOW the ~$302 price** — clearest "over-priced" flag in Layer 1.
6. **Sentiment.** 52-wk (split-adj) ~$83–$270; broke above on post-split rally. **Buy**, avg target ~$210 (below price).
7. **Interlink.** Sells to every fab; directly levered to CoWoS/advanced packaging and total WFE spend.
> Sub-scores — Fin 21 · Grw 14 · Val 10 · Cat 15 · Rsk 9. **Verdict: elite franchise, but momentum has outrun the Street — wait for a pullback toward target.**

#### Lam Research (NASDAQ: LRCX) — $379.09 (6/26) · Score 69/100
1. **Overview.** Etch & deposition leader; **most memory-levered** of the fab group (3D NAND, DRAM, GAA logic).
2. **Financials.** FY25 (Jun) rev $18.4B record (NI $5.36B, +40%); Q3'FY26 rev $5.84B, non-GAAP GM 49.8%, EPS $1.47; Jun-26 guide $6.60B ±$400M. FCF ~$5.4B. **P/E ~76x trailing (avg ~39x), EV/EBITDA ~60x.**
3. **Outlook.** ~$40B NAND-conversion capex pulling forward; DRAM SAM +>20% on 1C-node; SAM-% of WFE expanding to high-30s.
4. **Catalysts.** Late-July earnings; NAND-conversion cycle 2026–27; HBM/DRAM spend.
5. **Risks.** Highest **memory cyclicality** (FY24 was −14%); China controls; **consensus target (~$310–343) below ~$379 price.**
6. **Sentiment.** 52-wk $90.94–$409.75. **Buy**, avg target below price; bull $500 (Cantor).
7. **Interlink.** The pick-and-shovel on the memory boom (Micron/SK hynix/Samsung capex) plus GAA logic for TSMC.
> Sub-scores — Fin 20 · Grw 16 · Val 9 · Cat 16 · Rsk 8. **Verdict: best proxy for the HBM/DRAM capex wave, but priced for perfection — a memory-cycle name, trade it as one.**

---
### LAYER 2 — SILICON

#### NVIDIA (NASDAQ: NVDA) — ~$195.14 · Score 87/100 ★ top pick
1. **Overview.** The AI compute platform. Data Center ~92% of revenue ($75B of $81.6B in Q1'FY27; compute $60B +77%, networking $15B ~3x). Moat = CUDA + rack-scale systems (GB200/GB300 NVL72) + networking lock-in.
2. **Financials.** Rev FY24 ~$61B → FY25 ~$130B → FY26 ~$215B. Q1'FY27 $81.6B (**+85% YoY**), adj EPS $1.87. Gross ~75%, net ~56%. **FCF $49B in the quarter**, net cash, $80B buyback. **Forward P/E only ~20x** — multiple has compressed despite ~85% growth.
3. **Outlook.** Q2'FY27 guide ~$91B (zero China assumed); ~**$1T combined Blackwell+Rubin** across 2026–27; Rubin in trial production at TSMC.
4. **Catalysts.** Late-Aug earnings; Rubin ramp into late-26/27; potential China H200 re-opening.
5. **Risks.** China export controls (June'26 loophole closure), hyperscaler concentration, capex-digestion, custom-ASIC competition. Stock −23% from May ATH → **good news only partly priced in.**
6. **Sentiment.** 52-wk $151.49–$236.54. **Strong Buy**, avg target ~$275–309 (~40–55% upside).
7. **Interlink.** The keystone — buys TSMC fab + HBM, sells to clouds, invests in optics & neoclouds. Everything else is a derivative of NVIDIA demand.
> Sub-scores — Fin 24 · Grw 19 · Val 17 · Cat 17 · Rsk 10. **Verdict: highest-quality, best-scored name — de-rated into a growth re-acceleration; the anchor holding.**

#### Broadcom (NASDAQ: AVGO) — ~$375.51 · Score 84/100
1. **Overview.** Custom AI ASIC ("XPU") for Google/Meta/OpenAI/Anthropic + dominant AI networking (Tomahawk/Jericho) + sticky VMware software. AI semi Q2'FY26 $10.8B (**+143% YoY**).
2. **Financials.** Rev FY25 $63.9B; Q2'FY26 $22.2B (+48%), adj EBITDA ~69% of revenue. FCF FY25 $26.9B (+39%). **Forward P/E ~28–35x.**
3. **Outlook.** Q3 AI-semi guide ~$16B (>200% YoY); FY26 AI semi ~$56B; **FY27 AI semi reiterated >$100B** (the bull thesis).
4. **Catalysts.** Early-Sept earnings; new XPU customer ramps (OpenAI/Anthropic); 3nm/2nm tape-outs.
5. **Risks.** Hyperscaler-program concentration/lumpiness; VMware softness; the $100B FY27 target must hold. Target upside intact.
6. **Sentiment.** 52-wk $262.66–$495.00. **Strong Buy**, avg target ~$517–524.
7. **Interlink.** The "anti-NVIDIA" — supplies custom silicon *and* the networking that wires it; both substitute and complement to NVDA.
> Sub-scores — Fin 23 · Grw 19 · Val 15 · Cat 17 · Rsk 10. **Verdict: the premier custom-silicon + networking play with target upside — core holding alongside NVDA.**

#### AMD (NASDAQ: AMD) — ~$579 · Score 72/100
1. **Overview.** Credible #2 GPU (Instinct MI3xx/MI4xx) + share-gaining EPYC server CPUs. Data Center now largest segment ($5.8B, +57% in Q1'26).
2. **Financials.** Rev FY25 $34.6B; Q1'26 $10.3B (+38%), GM 53%, EPS $1.37; Q2 guide ~$11.2B. **Forward P/E ~60–69x.**
3. **Outlook.** 2026E rev ~$48.4B, EPS ~$4.99. **MI450 first 1GW deployments (OpenAI + Meta) 2H26.**
4. **Catalysts.** **Aug 4 earnings**; OpenAI 6GW + Meta 6GW deals (Meta warrant ~10% of AMD); MI400 launch.
5. **Risks.** MI450 execution; ROCm-vs-CUDA gap; **stock has run past avg target ~$502–506**; warrant dilution; customer concentration.
6. **Sentiment.** 52-wk $133.50–$582.58 (~4x). **Strong Buy**, avg target ≈/below price.
7. **Interlink.** TSMC fab + Korean/US HBM; sells to OpenAI/Meta; rack-scale via OCP/Helios.
> Sub-scores — Fin 18 · Grw 18 · Val 10 · Cat 17 · Rsk 9. **Verdict: real share gains and mega-deals, but priced for flawless MI450 execution — a momentum name, not a value one.**

#### Intel (NASDAQ: INTC) — ~$129.70 · Score 47/100 ▼ lowest score
1. **Overview.** IDM turnaround: Client + DCAI + **Intel Foundry**. Only US-based leading-edge logic foundry; US govt holds ~10% equity. 18A node is the bet.
2. **Financials.** Rev FY25 $52.9B (stagnant); **FY25 net loss ~$20.5B**, foundry op loss ~$10.3B (breakeven not before 2027). Q1'26 showed improvement (non-GAAP GM 41%, +650bps on 18A yields). Cash ~$32.8B vs debt ~$45B. Not valued on earnings — pure foundry option value.
3. **Outlook.** 18A HVM 2H26; 14A ~2028; CEO expects multiple foundry-customer commitments 2H26.
4. **Catalysts.** **July 23 earnings**; Apple foundry deal (18A-P production began June'26); prospective MSFT/AMZN/Tesla wins (NVIDIA tested 18A, reportedly paused).
5. **Risks.** **Stock trades ~25% ABOVE a Hold-rated ~$96–98 target** — fundamentals lag the price most of any name; ongoing foundry losses; 18A yield/ramp execution; political complexity.
6. **Sentiment.** 52-wk $18.97–$141.45 (~6–7x rebound). **Hold**, avg target below price.
7. **Interlink.** Uniquely spans fab *and* silicon layers; a foundry win would make it a TSMC alternative for the whole stack.
> Sub-scores — Fin 8 · Grw 11 · Val 7 · Cat 15 · Rsk 6. **Verdict: highest-asymmetry "show-me" lottery ticket — the price already embeds the turnaround; only for risk-tolerant capital.**

---
### LAYER 3 — MEMORY & STORAGE

> **Macro context (drives the whole layer):** the most violent memory up-cycle in 15+ years. TrendForce: Q2'26 DRAM contract prices **+58–63% QoQ**, NAND **+70–75% QoQ**; 2026 deficits DRAM −4.9%, NAND −4.2%, HBM −5.1%. HBM/enterprise-SSD output is **sold out for 2026**; new capacity unlikely before late-2027/28. **The shared risk: today's peak-cycle margins are not durable.**

#### Micron (NASDAQ: MU) — ~$1,199 (6/24) · Score 85/100 ★ #2 overall
1. **Overview.** Only US-based major DRAM/NAND maker; credible #2–3 in HBM; one of three companies on earth that can make leading-edge DRAM.
2. **Financials.** Rev FY24 $25.1B → FY25 $37.4B (+49%). **Q3'FY26 record rev $41.46B**, EPS $25.11, **GM 84.9%, op margin 81.2%** (records). Cash ~$13.9B vs debt ~$10.8B. **Forward P/E ~8–9x** (vs ~25x trailing) — cheapest growth in the basket.
3. **Outlook.** Q4'FY26 guide ~$50.0B. **HBM fully booked through CY2027 with CY28 visibility**; HBM4 12-high ramping ~2x faster than HBM3E.
4. **Catalysts.** ~Sept earnings; HBM4 qualification at NVIDIA Vera Rubin; quarterly DRAM/NAND price hikes.
5. **Risks.** 85% GM is peak-cycle and *not durable*; 2027/28 oversupply risk; China; concentration.
6. **Sentiment.** **Strong Buy**, avg targets $1,311–1,564 (high $2,000, Cantor).
7. **Interlink.** HBM sits physically on the GPU package — volume scales ~1:1 with NVIDIA/AMD accelerator shipments.
> Sub-scores — Fin 22 · Grw 20 · Val 18 · Cat 17 · Rsk 8. **Verdict: the best growth-for-the-multiple in the basket — forward P/E ~8–9x on a structural HBM tailwind, just respect the cycle.**

#### SK hynix (KRX: 000660; OTC HXSCL) — ~₩2,650,000 · Score 83/100
1. **Overview.** **#1 HBM (~56–57% share), NVIDIA's lead HBM partner**; #2 DRAM, #2 NAND (incl. Solidigm). The strongest moat in memory.
2. **Financials.** **Q1'26 rev ₩52.6T (~$35.5B), +198% YoY; operating profit ₩37.6T = 72% op margin (all-time high)** — one quarter's op profit exceeded all of FY24.
3. **Outlook.** 2026 HBM sold out; HBM4 mass production began early-26 and ramps through the year.
4. **Catalysts.** ~late-July earnings; HBM4 ramp at NVIDIA; watch Samsung reclaiming #1 DRAM *revenue* in Q4'25.
5. **Risks.** Cyclicality; Samsung/Micron closing the HBM gap; Korea/FX; **foreign-listing liquidity (ADR thin).**
6. **Sentiment.** 52-wk high ₩2,987,000. **Strong Buy**, avg target ₩3,094,448 (~+17%).
7. **Interlink.** Deepest HBM tie to NVIDIA of any name — owns the AI-memory bottleneck most directly.
> Sub-scores — Fin 22 · Grw 20 · Val 16 · Cat 16 · Rsk 9. **Verdict: the purest HBM leader at a reasonable multiple — own via local line or ADR, mind FX/liquidity.**

#### Samsung Electronics (KRX: 005930; OTC SSNLF) — ~₩323,000 · Score 78/100
1. **Overview.** Largest memory maker by capacity; **reclaimed #1 DRAM revenue Q4'25**; the HBM4 catch-up story. Diversified (foundry, mobile, displays) — not pure-play.
2. **Financials.** Q1'26 record: rev ₩134T (+43% QoQ), **op profit ₩57.1T (43% margin)**; chip division ~94% of profit, chip margin >70%.
3. **Outlook.** **First to mass-produce HBM4 (Feb 12, 2026)**; now qualified into **NVIDIA Vera Rubin**; cumulative HBM4 revenue >$1B in ~4 months.
4. **Catalysts.** **July 23 earnings**; HBM4 NVIDIA ramp (the re-rating catalyst); DRAM #1 defense; foundry turnaround.
5. **Risks.** Was the HBM laggard — execution risk; conglomerate dilutes pure-memory exposure; Korea labor/FX.
6. **Sentiment.** 52-wk/ATH ₩374,500; ~5.7x in 2026. Bullish, targets to ₩480,000.
7. **Interlink.** Newest qualified HBM4 supplier to NVIDIA — the marginal supplier expanding GPU HBM supply.
> Sub-scores — Fin 20 · Grw 17 · Val 15 · Cat 16 · Rsk 10. **Verdict: cheapest way into HBM4 with conglomerate ballast — the catch-up optionality is the upside.**

#### Kioxia (TSE: 285A) — ¥89,680 · Score 68/100 · *public since Dec-2024 IPO*
1. **Overview.** Pure-play **NAND/SSD** (ex-Toshiba Memory); #3 NAND (~14%); fab JV with SanDisk in Japan. **It is public** (often mistaken for private).
2. **Financials.** FY26 rev ¥2.34T (+37%), earnings ¥554.49B (+104%) on the NAND price surge.
3. **Outlook.** Leveraged to NAND contract prices (+70–75% QoQ) and enterprise-SSD demand; under-covered vs US peers.
4. **Catalysts.** NAND pricing; SanDisk JV capacity; ~Aug earnings.
5. **Risks.** Pure NAND = no DRAM/HBM diversification, most commoditized/oversupply-prone; PE lock-up overhang; Japan FX/liquidity.
6. **Sentiment.** **Buy**, target ¥110,594 (~+23%).
7. **Interlink.** Supplies enterprise SSD storage tier feeding AI clusters — complements, not part of, the HBM-on-GPU story.
> Sub-scores — Fin 17 · Grw 15 · Val 15 · Cat 13 · Rsk 8. **Verdict: cheapest, least-crowded NAND exposure — a value-y cyclical for those who want storage, not HBM.**

#### Western Digital (NASDAQ: WDC) — ~$638.57 · Score 67/100
1. **Overview.** **Pure-play HDD** since the SanDisk spin (early-2025); exascale nearline storage; duopoly with Seagate. AI "data gravity" demand.
2. **Financials.** Q3'FY26 rev $3.34B (+45.5%), EPS $9.26, **GM 50.5% (first >50%)**; Q4 guide ~$3.65B. **P/E ~31x.**
3. **Outlook.** HDD supply discipline; HAMR roadmap vs Seagate Mozaic.
4. **Catalysts.** Late-Jul/Aug earnings; nearline pricing; HAMR ramp.
5. **Risks.** Mature HDD market; long-run SSD substitution; **stock above avg target ~$585** after +115% in 2026.
6. **Sentiment.** **Strong Buy**, avg target ~$584.79 (below price).
7. **Interlink.** Bulk cold/warm storage tier for AI data lakes; volumes track hyperscaler exabyte growth.
> Sub-scores — Fin 19 · Grw 14 · Val 12 · Cat 13 · Rsk 9. **Verdict: a real beneficiary of data-gravity, but the easy re-rating is done — trades above target.**

#### Seagate (NASDAQ: STX) — ~$899.90 (6/27) · Score 69/100
1. **Overview.** The other HDD duopolist; **HAMR/Mozaic leader** (44TB/drive, ~50TB by late-27).
2. **Financials.** Q3'FY26 rev $3.11B (+44%), non-GAAP GM 47.0% (rising fast), EPS $4.10; FCF ~$1B/qtr; net leverage cut to 0.7x. Raised LT growth target to **≥20%**.
3. **Outlook.** HAMR ramp; nearline pricing; same data-gravity demand.
4. **Catalysts.** Late-Jul earnings; Mozaic ramp.
5. **Risks.** HDD maturity/SSD substitution; **+245% YTD, high volatility** (pulled back from ~$1,025).
6. **Sentiment.** 52-wk range to ~$1,085; spot ≈ avg target ~$898.
7. **Interlink.** Same role as WDC — HAMR capacity lets data centers store more exabytes per watt.
> Sub-scores — Fin 19 · Grw 15 · Val 13 · Cat 14 · Rsk 8. **Verdict: better tech (HAMR) and deleveraging story than WDC, but the run has been parabolic — size for the volatility.**

#### SanDisk (NASDAQ: SNDK) — ~$2,050–2,238 (6/29–30) · Score 60/100
1. **Overview.** Pure-play **NAND/SSD** spun from WDC (early-25); NAND fab JV with Kioxia. The most extreme momentum name in the basket.
2. **Financials.** ~**251% YoY revenue growth**; 2026 capacity sold out. (Young standalone — limited history.)
3. **Outlook.** NAND price hikes; enterprise-SSD AI demand; Bernstein target $3,000 (from $1,700).
4. **Catalysts.** NAND pricing; Kioxia JV capacity; earnings cadence.
5. **Risks.** **>4,000% since the spin; many targets sit BELOW price** — good news more than priced in; pure NAND = highest oversupply risk on the turn.
6. **Sentiment.** **Buy**, avg target below spot (caution flag).
7. **Interlink.** Enterprise SSD tier between HBM/DRAM and cold HDD storage; no GPU-package exposure.
> Sub-scores — Fin 17 · Grw 17 · Val 6 · Cat 14 · Rsk 6. **Verdict: spectacular momentum on a commoditizing product at a stretched price — the basket's clearest "don't chase."**

---
### LAYER 4 — NETWORKING & OPTICS

#### Arista Networks (NYSE: ANET) — ~$165.46 (6/29) · Score 77/100
1. **Overview.** Premier data-center Ethernet switching (400/800G) + EOS software; pivoting to AI back-end (Etherlink, Ultra Ethernet). Debt-free, ~64% GM software-like economics.
2. **Financials.** FY25 rev ~$9B (+28.6%), GM 64.1%, OCF $4.25B on ~$120M capex; Q1'26 rev $2.709B (**+35.1% YoY**), EPS $0.87. ~24x sales.
3. **Outlook.** FY26 guide ~$11.5B (+27.7%); **AI target raised to $3.5B**; >100 cumulative 800G customers; 1.6T at scale 2027.
4. **Catalysts.** XPO liquid-cooled pluggable optics; 1.6T ramp; Ultra-Ethernet-vs-InfiniBand wins; ~early-Aug earnings.
5. **Risks.** **Microsoft ~26% + Meta ~15% (~40% combined)** concentration; NVIDIA Spectrum-X competition; Broadcom-silicon reliance; premium multiple.
6. **Sentiment.** 52-wk $97.14–$179.80. **Strong Buy**, avg target ~$190 (upside).
7. **Interlink.** The Ethernet alternative to NVIDIA InfiniBand; pulls through 800G/1.6T optics (Coherent/Lumentum) and Broadcom/Marvell DSPs.
> Sub-scores — Fin 22 · Grw 17 · Val 13 · Cat 15 · Rsk 10. **Verdict: highest-quality balance sheet in Layer 4 with real target upside — the cleanest networking compounder.**

#### Marvell (NASDAQ: MRVL) — ~$278–297 · Score 73/100
1. **Overview.** Custom AI ASIC (one of two credible houses with Broadcom) + dominant optical DSPs (Inphi/PAM4) + switching. Data center ~76% of revenue; 50+ custom design wins.
2. **Financials.** FY26 (Jan) rev $8.195B (+42%); Q1'FY27 $2.418B (+28%), non-GAAP GM 59.0%, EPS $0.80. Cash ~$3.8B vs debt ~$5.0B; FCF ~$1.4B. P/S ~25–30x.
3. **Outlook.** FY27 rev raised ~$11.5B (+40%); FY28 ~$16.5B; custom chip >$10B by FY29.
4. **Catalysts.** New custom-ASIC wins/ramps; 1.6T/800G DSP cycle; ~late-Aug earnings.
5. **Risks.** Hyperscaler-program concentration (binary win/loss); Broadcom competition; **+247% in 2026, trades above avg target ~$176.**
6. **Sentiment.** 52-wk $61.44–$329.88. **Buy** (~86% Buy), bull KeyBanc $385.
7. **Interlink.** Deepest cross-layer footprint — XPUs (vs NVIDIA), optical DSPs (in Coherent/Lumentum modules), switching.
> Sub-scores — Fin 19 · Grw 18 · Val 11 · Cat 16 · Rsk 9. **Verdict: the #2 custom-silicon franchise riding the same wave as Broadcom — strong growth, but momentum has outrun targets.**

#### Lumentum (NASDAQ: LITE) — ~$846–970 (wide spread) · Score 71/100
1. **Overview.** **EML-laser duopoly with Coherent** — the scarce light source in 800G/1.6T transceivers; pivoting telecom→AI datacom. **NVIDIA $2B investment** funds capacity.
2. **Financials.** Steep inflection: Q3'FY26 record rev $808.4M, adj EPS $2.37; Q4 guide $960M–$1.01B (~85% YoY). FY26 EPS modeled ~$8.12.
3. **Outlook.** EML supply for AI clusters; 800G→1.6T ramp; NVIDIA-funded NC/Japan capacity; CPO optionality.
4. **Catalysts.** Q4 print + >$1B/qtr milestone; NVIDIA capacity execution; 1.6T ramp.
5. **Risks.** AI-capex cyclicality; pricing/competition; legacy telecom drag; **~10x move = stretched expectations.**
6. **Sentiment.** 52-wk $88.37–$1,085.68. **Buy**, avg targets ~$879–1,111.
7. **Interlink.** Upstream optical-component layer; NVIDIA $2B deal hardwires it into the optics roadmap; its EMLs power Coherent/Marvell/Innolight modules consumed by Arista fabrics.
> Sub-scores — Fin 18 · Grw 18 · Val 10 · Cat 17 · Rsk 8. **Verdict: a duopoly choke-point with NVIDIA capital behind it — own the optics theme here, but it's high-beta.**

#### Coherent (NYSE: COHR) — ~$391 (ATH $426.89 6/2) · Score 67/100
1. **Overview.** Vertically integrated optics (makes the lasers *and* the 800G/1.6T transceivers); **NVIDIA $2B investment / ~$1.9B equity stake + purchase commitment**; post-merger deleveraging turnaround.
2. **Financials.** FY25 record rev $5.81B, non-GAAP GM 37.9%, non-GAAP EPS $3.53; Q3'FY26 rev $1.81B (+21% YoY), GAAP EPS $0.97. Repaid ~$437M debt. Still carries merger leverage.
3. **Outlook.** Consensus EPS ~$4.09 next FY; 1.6T ramp; NVIDIA co-development incl. CPO; industrial recovery optionality.
4. **Catalysts.** NVIDIA partnership execution; 1.6T volume; aerospace/defense unit sale; FY26 segment realignment.
5. **Risks.** Lower GM (mid-30s) than fabless peers; **balance-sheet leverage**; transceiver pricing/competition; **+349% over 1 year.**
6. **Sentiment.** 52-wk $76.88–$440.00. **Buy**, avg target ~$384.
7. **Interlink.** Core optics for AI back-end; NVIDIA investment hardwires it; EML duopoly with Lumentum.
> Sub-scores — Fin 15 · Grw 16 · Val 11 · Cat 17 · Rsk 8. **Verdict: a leveraged turnaround with NVIDIA in the cap table — the catalyst-rich, higher-risk optics pick.**

#### Rambus (NASDAQ: RMBS) — ~$123.32 · Score 71/100
1. **Overview.** DDR5 register-clock-driver chips (on every server DIMM, ~mid-40s% share) + high-margin memory/security IP licensing. 80%+ blended GM.
2. **Financials.** 2025 product rev $347.8M (+41%), total $707.63M (+27%); Q1'26 product $88.0M (+15%); Q2 guide $95–101M. P/E ~54x.
3. **Outlook.** DDR5 mix-up; **MRDIMM ~$600M opportunity ramping 2027**; CXL; PCIe/security attach. Ex-AMD president Victor Peng joined the board.
4. **Catalysts.** MRDIMM ramp 2027; CXL adoption; new IP licenses; memory-roadmap updates.
5. **Risks.** Smaller-cap, lumpy royalty timing; DDR5 share defense; "AI narrative vs modest product revenue" skepticism.
6. **Sentiment.** 52-wk $61.16–$174.10. **Buy**, avg target ~$144.57 (~+23%).
7. **Interlink.** Memory-interface layer beneath every accelerator — enables the HBM/DDR5 subsystem; less hyperscaler-concentrated.
> Sub-scores — Fin 20 · Grw 15 · Val 13 · Cat 13 · Rsk 10. **Verdict: high-margin, ubiquitous, less-crowded memory-interface play with target upside — a quieter way to own the memory build.**

#### Silicon Motion (NASDAQ: SIMO) — ~$319 (6/23) · Score 69/100
1. **Overview.** Leading merchant NAND-controller supplier (client SSD, mobile UFS) + newer **MonTitan enterprise/datacenter SSD controllers** aimed at CSPs.
2. **Financials.** Q1'26 record rev $342.1M (**+105% YoY**), GM 47.2%, EPS $1.58; Q2 guide $393–411M. ~1.4% dividend.
3. **Outlook.** PCIe 5.0 client; MonTitan qualification at Tier-1 CSPs; PCIe 6 tape-out Q3'26; BofA models >$1.5B (2026), >$2B (2028).
4. **Catalysts.** MonTitan qualification→volume; PCIe 6 tape-out; AI-storage demand.
5. **Risks.** NAND cyclicality; mature smartphone exposure; enterprise success unproven at scale; Taiwan geopolitics.
6. **Sentiment.** 52-wk $70.12–$355.00. **Strong Buy**; BofA $450 (legacy $140–180 marks are stale).
7. **Interlink.** Storage-controller layer feeding AI data centers; less NVIDIA-coupled, more a hyperscaler-storage-capex play.
> Sub-scores — Fin 17 · Grw 16 · Val 13 · Cat 14 · Rsk 9. **Verdict: a reasonably-valued AI-storage controller with enterprise optionality — the value-tilt in Layer 4.**

#### Astera Labs (NASDAQ: ALAB) — ~$456–493 (wide spread) · Score 66/100
1. **Overview.** Pure-play AI connectivity (Aries PCIe/CXL retimers, Taurus cables, Leo CXL controllers, Scorpio fabric switches). ~75%+ GM; transitioning component→rack-platform.
2. **Financials.** Rev FY24 $396.3M (+242%) → FY25 $852.5M (+115%); GAAP loss → +$1.32 EPS. **P/S ~50–80x, forward P/E >100x.**
3. **Outlook.** 2026 rev consensus ~$1.35B, EPS ~$1.63; Scorpio ramp, PCIe Gen6, CXL, content-per-rack growth.
4. **Catalysts.** Scorpio scaling; PCIe 6 ramp; design wins beyond NVIDIA; ~late-Jul/Aug earnings.
5. **Risks.** **Heavy NVIDIA dependence; valuation leaves zero margin for error; targets ($263–273) far below price.**
6. **Sentiment.** 52-wk ~$85.85–$499.48. **Buy**, avg target well below price (red flag).
7. **Interlink.** The connective tissue *inside* NVIDIA racks; direct leverage to GB200/GB300 unit volumes.
> Sub-scores — Fin 19 · Grw 18 · Val 6 · Cat 16 · Rsk 7. **Verdict: best-in-class product economics, but the most valuation-stretched name in Layer 4 — wait for a reset.**

---
### LAYER 5 — CLOUD INFRASTRUCTURE (NEOCLOUDS)

> All four are **pre-profit, capex-furnace** GPU/data-center operators financing NVIDIA hardware with debt + converts + preferred + dilution. **Power is their real bottleneck** (Nebius 4GW, IREN 5GW, APLD 4GW). NVIDIA is supplier, allocator, customer, and sometimes investor — the circular-financing risk lives here.

#### Nebius (NASDAQ: NBIS) — $264.15 · Score 64/100
1. **Overview.** Full-stack AI cloud (ex-Yandex, renamed Aug-24). AI cloud ~98% of revenue; **NVIDIA-preferred + $2B NVIDIA equity stake**; fast-growing backlog. Closest to GAAP breakeven of the four.
2. **Financials.** Rev FY24 ~$117M → FY25 $529.8M (+351%); **Q1'26 $399M (+684% YoY)**; core AI-cloud ARR ~$1.92B (+54% QoQ); FY25 net income ~+$9.8M. Cash ~$3.7B. **Capex guided $20–25B for 2026** (multiples of revenue). EV/rev ~19–20x 2026E.
3. **Outlook.** FY26: ARR $7–9B, revenue $3.0–3.4B, ~40% adj-EBITDA margin, 4GW contracted. Drivers: ~$27B Meta deal, multi-billion Microsoft, NVIDIA allocation.
4. **Catalysts.** **Q2 earnings July 29, 2026**; new GW capacity; further large contracts; capex financing rounds.
5. **Risks.** Capex >> revenue → financing/execution risk; Meta/Microsoft concentration; dilution; +167–187% YTD.
6. **Sentiment.** 52-wk $43.89–$299.86. **Moderate Buy**, mean target ~$244 (≈at price; wide dispersion).
7. **Interlink.** NVIDIA-backed; 4GW makes it a major energy-demand driver; supplies compute to Meta/Microsoft.
> Sub-scores — Fin 14 · Grw 19 · Val 7 · Cat 17 · Rsk 7. **Verdict: the best-capitalized, closest-to-profit neocloud — but priced for flawless 4GW execution; satellite-size only.**

#### CoreWeave (NASDAQ: CRWV) — ~$95.51 · Score 62/100 · *the contrarian*
1. **Overview.** Largest independent NVIDIA GPU cloud. **Microsoft ~67% of FY25 revenue** (moat + risk). $99B disclosed pipeline.
2. **Financials.** Rev 2024 $1.92B → **FY25 $5.13B (+167%)**; Q1'26 ~$2.08B (+111.6%). **Unprofitable**; cash $2.27B vs **debt $35.15B** (net debt ~−$32.9B). **Capex $30–35B for 2026** (triggered a selloff).
3. **Outlook.** FY26 rev consensus ~$12B (+~135%); OpenAI ~$22.4B + Meta ~$14.2B (to 2031) + Microsoft anchor.
4. **Catalysts.** **Aug 18 earnings**; capacity ramps; OpenAI/Meta expansions; debt raises.
5. **Risks.** Extreme MSFT concentration; **~$35B debt**; persistent negative FCF; market now punishing capex guidance — **near 52-wk lows, −27% on the year (the only laggard in the basket).**
6. **Sentiment.** IPO'd Mar-25 at $40; 52-wk $63.80–$183.98. **Buy**, avg target ~$132.68 (~30% upside); bull $250.
7. **Interlink.** Archetypal NVIDIA-dependent neocloud; buys from NVIDIA, leases from Applied Digital, sells to OpenAI/Meta/Microsoft.
> Sub-scores — Fin 12 · Grw 19 · Val 12 · Cat 16 · Rsk 3. **Verdict: huge backlog and the only beaten-down name here — a high-risk contrarian on a ~$35B debt load; deep-value optionality, not a core hold.**

#### IREN (NASDAQ: IREN) — ~$45.56 · Score 58/100
1. **Overview.** Bitcoin-miner→AI-cloud pivot; owns power-rich sites (Childress, TX). Mining shrinking, AI cloud surging.
2. **Financials.** Q3'FY26 rev $144.8M (mining $111.2M −33.6% QoQ; **AI cloud $33.6M +839% YoY**); **net loss $247.8M** ($140.4M impairment). Cash $2.21B; convertibles ~$3.69B.
3. **Outlook.** **5GW secured power; ~$3.1B contracted ARR**; Microsoft 5-yr ~$9.7B (GB300 at Childress) + NVIDIA 5-yr ~$3.4B.
4. **Catalysts.** Childress GB300 phases through 2026; further hyperscaler deals; mining→GPU conversion milestones.
5. **Risks.** Volatile earnings (impairments); BTC-price exposure; convertible-debt/dilution; **+657% over 1 year.**
6. **Sentiment.** 52-wk $13.99–$76.87. Avg target ~$70.40 (~+46%).
7. **Interlink.** Buys NVIDIA GB300, sells to Microsoft/NVIDIA; 5GW makes it as much a power story as compute; BTC legacy adds crypto beta.
> Sub-scores — Fin 11 · Grw 18 · Val 9 · Cat 15 · Rsk 5. **Verdict: a leveraged pivot story with real contracts but messy financials and crypto beta — speculative.**

#### Applied Digital (NASDAQ: APLD) — ~$38–47 (volatile) · Score 57/100
1. **Overview.** AI data-center **landlord** (build-to-suit leases, keeps >85% site ownership) + cloud services. Anchor tenant **CoreWeave**.
2. **Financials.** FQ3'26 rev $126.6M (+139% YoY), net loss $100.9M. Cash ~$2.3B vs debt ~$2.6B (9.25% notes); **Macquarie ~$5B preferred facility** funds 4GW pipeline while limiting dilution. Loss-making.
3. **Outlook.** **>$23B contracted lease revenue** (CoreWeave 600MW/~$16B + $7.5B 15-yr Delta Forge hyperscaler lease); 4GW pipeline.
4. **Catalysts.** New leases; CoreWeave capacity online; Macquarie draws; FQ4'26 earnings.
5. **Risks.** **NVIDIA exited its APLD stake**; **counterparty concentration on CoreWeave** (itself MSFT-concentrated — daisy-chain); up-to-19.99% dilution risk; 9.25% debt.
6. **Sentiment.** 52-wk $9.02–$50.73. **Strong Buy**, avg target ~$73.36.
7. **Interlink.** One layer below the GPU clouds — the landlord powering CoreWeave/hyperscalers; a power-and-real-estate play.
> Sub-scores — Fin 11 · Grw 17 · Val 9 · Cat 14 · Rsk 6. **Verdict: contracted-revenue optionality offset by daisy-chain concentration and NVIDIA's exit — the riskiest name in the basket; small, speculative only.**

---
### LAYER 6 — ENERGY & POWER

> This layer **powers the entire stack**. The bottleneck is increasingly **physical** — turbine slots booked through 2030, transformer/skilled-labor scarcity, multi-year interconnection queues. Watch **backlogs** (GEV $163B, PWR $48.5B, BE ~$20–24B) and **long-dated PPAs** as the key metrics.

#### Vistra (NYSE: VST) — ~$160.23 · Score 80/100 ★ best-scored energy name
1. **Overview.** Largest US merchant power producer (gas + nuclear + retail). Integrated generation+retail hedge; ERCOT/PJM scale.
2. **Financials.** FY25 Ongoing-Ops adj EBITDA $5.7–5.9B; Q1'26 adj EBITDA $1.494B (+~20%). **Forward P/E ~16x — cheapest IPP.**
3. **Outlook.** FY26 adj EBITDA **$6.8–7.6B**, FCF $3.9–4.7B (reaffirmed). Drivers: power-demand growth, nuclear PPAs.
4. **Catalysts.** Early-Aug earnings; **Helix Digital JV ($10B with KKR, NVIDIA & KIA)**; 3,800MW Meta/AWS PPAs; Comanche Peak/PJM-nuclear PPAs.
5. **Risks.** Merchant commodity/price volatility; coal-retirement timing; recent run-up.
6. **Sentiment.** **Strong Buy** (19/0/1), median target ~$225–232 (~40%+ upside).
7. **Interlink.** Dispatchable + nuclear straight to hyperscalers; the Helix JV (with NVIDIA/KKR) directly links merchant power to AI data centers.
> Sub-scores — Fin 20 · Grw 16 · Val 17 · Cat 17 · Rsk 10. **Verdict: the rare AI-power name that's cheap (~16x) with ~40% target upside and a direct NVIDIA-linked JV — top energy pick.**

#### Constellation Energy (NASDAQ: CEG) — ~$259 · Score 79/100
1. **Overview.** Largest US carbon-free producer (~22GW nuclear) + ~28GW gas/geothermal after the **$22B Calpine deal (closed Jan-26)** — now #1 US electricity producer.
2. **Financials.** FY25 adj operating EPS $9.39; Q1'26 rev +64% YoY (~$11B, Calpine-driven). **P/E ~21x, EV/EBITDA ~13.9x** (premium to regulated utilities).
3. **Outlook.** FY26 adj EPS guide **$11.00–12.00**; 2029 target $11.40–11.90 (~20% CAGR, *excluding* new nuclear PPAs).
4. **Catalysts.** ~Aug 6 earnings; new data-center nuclear PPAs (Meta Clinton, Walmart); **Crane/TMI-1 restart for Microsoft**; Calpine synergies.
5. **Risks.** Premium valuation; merchant power-price exposure; nuclear outage risk; Calpine integration.
6. **Sentiment.** 52-wk $240.51–$412.70 (well off highs). **Buy**, avg target ~$360 (~39% upside).
7. **Interlink.** The premier "clean baseload behind the meter" supplier to hyperscalers via long-dated nuclear PPAs.
> Sub-scores — Fin 20 · Grw 17 · Val 16 · Cat 16 · Rsk 10. **Verdict: the cleanest nuclear-to-AI play, off its highs with target upside and PPA optionality — core energy holding.**

#### Quanta Services (NYSE: PWR) — ~$701.88 (6/25) · Score 75/100
1. **Overview.** Largest specialty contractor for electric-power infrastructure (T&D, substations, renewables, data-center electrical). Moat = skilled-labor scale (the binding constraint on grid buildout).
2. **Financials.** FY25 rev $28.48B, adj EPS $10.75; Q1'26 rev $7.87B, adj EPS $2.68 (+50%). **Record backlog $48.5B.**
3. **Outlook.** FY26 rev $33.25–33.75B, adj EPS **$12.65–13.35**, FCF $1.55–2.05B.
4. **Catalysts.** Late-Jul/Aug earnings; data-center/grid awards; further M&A.
5. **Risks.** Labor availability/wage inflation; fixed-price execution; rich multiple.
6. **Sentiment.** 52-wk $363.01–$788.75. **Buy**, avg target ~$761 (~+8%).
7. **Interlink.** The builder that physically connects generation to data centers — a pure beneficiary regardless of which generation tech wins.
> Sub-scores — Fin 21 · Grw 16 · Val 13 · Cat 14 · Rsk 11. **Verdict: the highest-quality, lowest-risk picks-and-shovels on the grid buildout — quality at a full but fair price.**

#### NextEra Energy (NYSE: NEE) — ~$87.79 · Score 71/100
1. **Overview.** FPL (regulated FL utility) + Energy Resources (world's largest wind/solar/storage developer). Lowest-cost renewables at scale + stable rate base.
2. **Financials.** Q1'26 adj EPS $1.09 (+10%); record renewables origination (+4GW backlog, ~30% hyperscaler). **Most reasonably valued in the layer.**
3. **Outlook.** FY26 adj EPS **$3.92–4.02**; **8%+ EPS CAGR through ~2032–35**; 40 data-center hubs by YE26; DOC-selected for 9.5GW new gas.
4. **Catalysts.** Late-Jul earnings; Dominion deal regulatory progress; backlog adds; gas expansion.
5. **Risks.** **Rate/interest-rate sensitivity** (capital-intensive); IRA/tax-credit policy risk; Dominion execution.
6. **Sentiment.** 52-wk $67.20–$98.75. **Buy**, avg target ~$98.47 (~+14%); MS $117.
7. **Interlink.** Renewable + increasingly gas power to data centers via PPAs and co-located hubs.
> Sub-scores — Fin 18 · Grw 14 · Val 16 · Cat 13 · Rsk 10. **Verdict: the defensive, reasonably-valued way to own AI power demand — lower beta, rate-sensitive, steady compounder.**

#### GE Vernova (NYSE: GEV) — ~$1,087 (6/29) · Score 68/100
1. **Overview.** Power (gas turbines, nuclear/SMR) + Electrification (grid) + Wind. The "arms dealer" for the electricity buildout; large-turbine oligopoly with **slots booked through 2030**.
2. **Financials.** Q1'26 EPS $1.98, rev $9.34B; orders $18.3B; **record backlog $163B**; **$2.4B data-center equipment orders in Q1 alone**. **Rich: fwd P/E ~60x, EV/EBITDA ~85x.**
3. **Outlook.** FY26 rev raised $44.5–45.5B; $200B backlog target by 2027.
4. **Catalysts.** ~July 22 earnings; turbine reservations; BWRX-300 SMR milestones; further guidance raises.
5. **Risks.** **Most priced-in name in Layer 6** — valuation leaves no margin for error; wind profitability; turbine-ramp execution.
6. **Sentiment.** 52-wk $482.20–$1,181.95 (+69% YTD). **Buy**, avg target ~$1,212.
7. **Interlink.** Supplies turbines + grid hardware every data-center buildout depends on.
> Sub-scores — Fin 18 · Grw 18 · Val 8 · Cat 16 · Rsk 8. **Verdict: best demand visibility (slots to 2030) but the priciest multiple — a great business at a demanding price; buy weakness.**

#### Bloom Energy (NYSE: BE) — ~$307 · Score 66/100
1. **Overview.** Solid-oxide fuel cells for fast-deploy on-site power — the **speed-to-power** answer when the grid queue is too slow.
2. **Financials.** FY25 rev $2.02B (+37.3%), GM 29.0%; **Q1'26 rev $751.1M (+130.4%)**, net income $70.7M (turned profitable). Backlog ~$20–24B.
3. **Outlook.** FY26 rev raised **$3.4–3.8B** (~80% growth), non-GAAP EPS $1.85–2.25; ~2GW capacity. FERC rules favor on-site power.
4. **Catalysts.** ~late-Jul/Aug earnings; **Oracle "Project Jupiter" up to 2.45GW**; expanded 2.8GW Oracle agreement; **$5B Brookfield** AI-factory partnership.
5. **Risks.** Highest-multiple/most-speculative; gas feedstock (not zero-carbon); concentration; **trades above avg target ~$267.**
6. **Sentiment.** 52-wk $21.52–$351.28 (~+1,600% in a year). **Buy**, avg target below price.
7. **Interlink.** Speed-to-power for hyperscalers facing interconnection queues; tied to AI via Oracle/Brookfield.
> Sub-scores — Fin 16 · Grw 19 · Val 7 · Cat 17 · Rsk 7. **Verdict: explosive growth and marquee deals, but a stretched, speculative multiple — a high-beta satellite on the power-shortage theme.**

#### Eos Energy (NASDAQ: EOSE) — ~$6–8 (sources spread) · Score 52/100
1. **Overview.** US-made **zinc-based** long-duration grid storage — non-lithium LDES. Smallest/highest-risk name; still scaling to profit.
2. **Financials.** Rev $15.6M (2024) → $114.2M (2025); **Q1'26 $57.0M (+445% YoY)**; backlog $644.6M, pipeline $24.3B. **Pre-profit, cash-burn**; Cerberus-backed.
3. **Outlook.** FY26 rev guide **$300–400M** (reaffirmed); drivers: renewables-firming + data-center load + domestic-content incentives.
4. **Catalysts.** ~Aug earnings; backlog conversion; Frontier Power USA scaling; reaching positive gross margin/EBITDA.
5. **Risks.** Execution/cash-burn/dilution; profitability unproven; policy-dependent; lumpy orders.
6. **Sentiment.** 52-wk $4.37–$19.86. Mixed (Buy/Hold), avg target ~$9.2–9.6.
7. **Interlink.** Indirect — grid-firming storage supporting reliability for data-center/renewables-heavy grids.
> Sub-scores — Fin 8 · Grw 16 · Val 11 · Cat 12 · Rsk 5. **Verdict: a venture-style call option on non-lithium LDES — highest risk in the basket; only for speculative capital.**

---

## PART IV — HOW TO TRACK THIS BASKET (the "keep a track for investment" piece)

A companion **`research/ai-infra-tracker.csv`** captures the monitorable snapshot (price, 52-wk range, score + sub-scores, consensus, target, verdict) for all 30 names so you can refresh it each quarter and watch the score migrate.

**The signals that actually move this thesis — check these, in this order:**
1. **Hyperscaler capex guides** (Microsoft, Meta, Amazon, Google, Oracle quarterly) — the master demand variable for *all 30 names*. A cut here de-rates the whole stack.
2. **TSMC monthly revenue prints** — the highest-frequency real-time read on AI silicon demand.
3. **HBM qualification milestones** (Micron/SK hynix/Samsung HBM4 at NVIDIA Vera Rubin) — confirms the memory up-cycle's durability.
4. **The "above-target" screen** — re-run it each quarter; names crossing back *below* target are where the Street has caught up (entry windows); names pushing further *above* are momentum-risk.
5. **Optics 1.6T ramp + NVIDIA's optics stakes** (Coherent/Lumentum) — confirms the new bottleneck.
6. **Power PPAs & backlogs** (Constellation/Vistra deals; GE Vernova/Quanta backlog) — the physical buildout's leading indicator.
7. **Neocloud financing & capex guides** (CoreWeave/Nebius/IREN/APLD) — the credit-risk canary; debt loads + dilution are where this cycle would crack first.

**Watch-triggers (next ~8 weeks from 2026-06-30):** GE Vernova (Jul 22), Intel & Samsung (Jul 23), Nebius (Jul 29), AMD (Aug 4), Constellation (~Aug 6), CoreWeave (Aug 18); TSMC/ASML/KLA/Lam all report mid-to-late July.

---

## PART V — DESK SUMMARY

- **Top of the board:** NVIDIA (87), Micron (85), Broadcom (84), TSMC & SK hynix (83). These combine elite financials, sold-out/contracted demand, and — crucially — **still trade with upside to consensus targets.** They are the basket's quality core.
- **Best risk-adjusted value:** **Micron** (forward P/E ~8–9x on a structural HBM tailwind), **Vistra** (~16x with ~40% target upside and an NVIDIA-linked JV), **TSMC** (~29x for the keystone), **Constellation** (off its highs with PPA optionality).
- **Highest quality, full price:** Arista, Quanta, GE Vernova — own on weakness.
- **Momentum that has outrun the Street (caution):** SanDisk, Astera Labs, Marvell, Bloom, KLA, Lam, Western Digital, Seagate — all trade *above* average targets.
- **Speculative / show-me:** the neoclouds (CoreWeave the beaten-down contrarian; IREN/APLD the riskiest), Intel (price ~25% above a Hold target), Eos (pre-profit micro-cap).
- **The governing risk:** all 30 are the *same* long-AI-capex trade. Diversify *across layers* for thesis breadth, but recognize they will **rise and fall together** — manage exposure with position sizing, not ticker count.

> **This is analysis for research purposes only — not financial advice. All figures were web-sourced on 2026-06-30, several with wide intraday/aggregator spreads (flagged inline). Verify every number against a live feed and consult a licensed advisor before investing.**
