# Decision Proposal — Best Long-Term Defense

**Derived from Bayesian decision simulation** (`scripts/bayesian_defense_decision.py`)
**Date:** 2026-08-29 | **Paired scenarios:** 20,000 | **Horizon:** 10 years @ 5% discount

---

## Bottom line

> **Build the passive layer now (warning + shelters + basic C2). Then buy the active
> cruise/counter-drone/deception layer as conditional insurance against threat surges.
> Treat the AI-killer system and city-wide high-end missile defense as dominated
> — neither is a sound primary investment under any of the plausible posteriors.**

---

## The candidates evaluated

| ID | Strategy | Capital (mean) | Deploy to full effect |
|----|----------|---------------|----------------------|
| A | Passive-first (warning + shelters + basic C2) | $0.8B | ~6 months |
| B | Cruise-active (IRIS-T/NASAMS + C-RAM/Gepard + point defense) | $2.5B | ~18 months |
| C | AI-enabled distributed kinetic system (prior Monte Carlo design) | $4.0B | ~40 months |
| D | Hybrid doctrine (passive + cruise layer + counter-drone + deception) | $3.15B | ~12 months (phased) |
| E | High-end missile defense (Patriot/SAMP-T heavy) | $12B | ~24 months |

Each strategy's PK per threat class was modeled as a **Beta posterior** with
source-informed priors (see `sources/REFERENCES.csv`); costs as **Gamma priors**
(right-skewed, reflecting systematic cost growth); threat flows as **Gamma-Poisson**
posterior-predictives. All scenarios use **paired draws** — every strategy faces the
*identical* threat scenario, so the rankings isolate strategy differences rather than
shared uncertainty.

---

## Headline results (10-year, discounted)

| Strategy | Expected lives saved | Cost | Cost/life (median) |
|----------|---------------------|------|--------------------|
| **A. Passive-first** | **391,820** (90% HDI 177K–727K) | **$1.30B** | **$3,458** (HDI $1.3K–8.5K) |
| D. Hybrid doctrine | 379,288 (176K–694K) | $7.55B | $21,450 |
| B. Cruise-active | 224,706 (92K–437K) | $7.33B | $36,296 |
| C. AI-killer | 181,647 (79K–346K) | $13.27B | $80,477 |
| E. High-end missile | 213,591 (92K–410K) | $37.98B | $197,838 |

### Probability of being best (across 20,000 scenarios)

| Strategy | P(best cost/life) | P(most lives saved) |
|----------|-------------------|---------------------|
| **A. Passive-first** | **100%** | **62.8%** |
| D. Hybrid | 0% | **37.2%** |
| B / C / E | 0% | 0% |

---

## The decision logic (why this is the right proposal)

**Finding 1 — Passive-first [A] is the cost-effectiveness bedrock.**
It wins the cost-per-life comparison in ~100% of scenarios. Not because it intercepts
anything (it does not), but because it protects against *every* threat class — including
Kinzhal and Iskander, which no active system reliably stops — at ~1/6 the cost-per-life
of the next best option, and it deploys in ~6 months (vs 18–40 for active alternatives).
This echoes the verified cost-asymmetry data: shelters cost roughly $140/life in the 5-yr
model, while any interceptor-based system costs an order of magnitude more.

**Finding 2 — Lives-saved is contested; that's the insurance argument.**
Option D (hybrid) saves more lives than A in **37.2%** of scenarios — and in exactly
those high-threat scenarios it saves on average **~39,000 additional lives**. In
low-threat scenarios the active layer is wasted money. This is the textbook
cost-vs-lives portfolio tension. The resolution is *not* to pick one; it is to **own
the passive layer unconditionally and add the active layer conditionally**, gated on
observed threat escalation.

**Finding 3 — Two strategies are dominated.**
- **C (AI-killer):** worse than D on every axis (higher cost, fewer lives, slowest to
  deploy) under every posterior in the simulation. The prior Monte Carlo already showed
  0% probability of meeting its 60% hit-rate target. It belongs in **funded R&D** with
  18/30-month decision gates — never as primary defense.
- **E (high-end missile defense city-wide):** best single-system ballistic capability
  but catastrophically expensive ($197K/life, ~57x A) and *worst* against drone swarms
  ($4M interceptor vs $48–193K Shahed). Reserve it for **critical national nodes**
  (power, rail, command), where its value is concentrated.

---

## Recommended portfolio (phased build)

| Phase | Time | Action | Rationale (from simulation) |
|-------|------|--------|-----------------------------|
| **1** | 0–6 mo | Passive layer: mass warning/shelter network + basic C2 | Non-negotiable foundation; ~$0.6–1B; saves ~390K lives expected; works vs all threats |
| **2** | 6–18 mo | Conditional insurance: cruise layer (IRIS-T/NASAMS) + counter-drone (C-RAM/Gepard) + deception | Buys 37% chance of ~+39K lives exactly when threat surges; gate on escalation |
| **3** | gate-based | Critical-node terminal defense (Patriot/SAMP-T) only | High-end defense where it pays: pinpoint, not area |
| **R&D track** | parallel | AI-killer as funded R&D with decision gates at 18/30 months | Hedge on future tech; never primary until proven at scale |

---

## What would change our minds (value of information)

Perfect information about which strategy is best changes the **mean cost-per-life by 0%**
(option A is so dominant on cost that oracle information can't improve it) but could add
**~3.7% more lives saved** — i.e., the *next* question worth answering is not "which
system?" but "when does the threat surge warrant activating Phase 2?". The highest-value
data to collect is therefore: **real shelter-utilization rates + verified casualties per
leaked warhead + threat-rate trends** (THR-16, PERF-03 in `sources/REFERENCES.csv`),
not more system-cost trivia.

---

## Honest limitations

1. **PK priors are estimates.** Kinzhal/Iskander interception probabilities have almost
   no public confirmation data; the simulation's *ranking* is robust to these priors
   (paired design), but the *absolute lives saved* numbers carry the uncertainty shown
   in the HDIs.
2. **Unit costs remain `[estimate]`** (COST-01..11) — notably Gepard $1K and the laser
   figures. Shahed cost was verified at $48–193K and incorporated; the Patriot $4M
   figure is still from earlier analysis.
3. **Casualty coefficients (lives-per-leak) are `[estimate]`** and drive the absolute
   magnitude of all lives-saved figures. They do not drive the *relative ranking*
   because they are shared across strategies in the paired design.
4. This is a **civilian-protection portfolio** view. Military operational-tempo
   priorities (defending forward-deployed forces, airbases sustaining sorties) would
   shift weight toward active layers for those specific nodes.

---

## Files

- `scripts/bayesian_defense_decision.py` — the simulation (paired-draw Bayesian decision engine)
- `scripts/visualize_bayesian_decision.py` — 6-panel visualization
- `research/bayesian_decision_report.txt` — full text report
- `research/bayesian_decision_analysis.json` — structured results (all probabilities, EVSI, conflict analysis)
- `research/bayesian_decision_results.csv` — 100,000 strategy-scenario rows (20,000 × 5)
- `research/bayesian_decision_visualization.png` — charts
