# Open Rocket Defense System Research

## Overview
Research project identifying cost-effective alternatives to expensive missile defense systems for protecting Ukrainian civilians from Russian rocket, artillery, and missile attacks.

## Key Finding
**Layered defense with open systems saves 82% vs. Patriot-only approach:**
- C-RAM: $750 per engagement (vs. $4M Patriot)
- Gepard: $1,000 per engagement
- ZU-23-2: $200 per engagement
- EW Jamming: $10 per engagement (drones)

**Total system cost: $2.65B vs. $15B for Patriot-only**

## Monte Carlo Analysis (New)
10,000-simulation Monte Carlo analysis of the AI-Enabled Distributed Defense System concept. **Critical finding: 0% of simulations achieved the 60% hit-rate target.**

- **Report**: `research/monte_carlo_report.txt`
- **Data**: `research/monte_carlo_results.csv`
- **Simulation code**: `scripts/monte_carlo_defense_analysis.py`
- **Interactive dashboard**: [site/](site/index.html) (GitHub Pages)

## GitHub Pages Info Site
Two linked pages are published at
[`tobias-weiss-ai-xr.github.io/open-rocket-defense-system-research/`](https://tobias-weiss-ai-xr.github.io/open-rocket-defense-system-research/):

- **Explainer** ([`site/explain.html`](site/explain.html)) — the story-driven page: threat landscape with
  verified threat cards, speed/warhead/cost-asymmetry charts, why we simulate, Monte Carlo + Bayesian decision
  methods, the recommended portfolio, and the claim-verification audit.
- **Dashboard** ([`site/index.html`](site/index.html)) — interactive Monte Carlo statistics and the
  Bayesian decision-proposal section.

**To publish/refresh:** push to `main`; GitHub Actions deploys `site/*` automatically (see
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)).

**To update with new simulation data:**
```bash
python3 scripts/monte_carlo_defense_analysis.py
cp research/monte_carlo_analysis.json site/data/
cp research/monte_carlo_results.csv site/data/
git add site/data && git commit -m "Update simulation data" && git push
```

The data files are published alongside the site (see `site/data/`); refresh them the same way whenever
analysis outputs change. See [`site/README.md`](site/README.md) and [`site/DEPLOYMENT.md`](site/DEPLOYMENT.md)
for full details.

## Project Structure
```
├── README.md              # Project overview
├── research/              # Main research documents + Monte Carlo results
│   └── ukraine-missile-defense-analysis.md
├── docs/                  # Technical documentation
├── data/                  # Data files and datasets
├── sources/               # Source materials and citations
├── scripts/               # Analysis scripts (Monte Carlo, visualization, ingestion)
└── site/                  # GitHub Pages info site (dashboard)
```

## Research Areas
1. Russian offensive systems (Kinzhals, Iskanders, Kalibrs, drones)
2. Patriot system analysis (cost, effectiveness, limitations)
3. Alternative defense systems (Iron Dome, IRIS-T, NASAMS, etc.)
4. **Open rocket defense systems** (C-RAM, Gepard, ZU-23-2, lasers)
5. Cost-effectiveness analysis
6. Civilian protection strategies

## Status
- [x] Research framework created
- [x] Open rocket defense systems analysis
- [x] Monte Carlo simulation (10,000 runs)
- [x] GitHub Pages dashboard
- [ ] Data collection
- [ ] Cost analysis
- [ ] Alternative evaluation
- [ ] Recommendations

## License
Research project - all sources properly cited
