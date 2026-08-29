# AI-Enabled Distributed Defense System - Analysis Dashboard

A GitHub Pages-ready interactive dashboard for visualizing Monte Carlo simulation results.

## 🚨 **CRITICAL FINDING PRONOUNCED**

**0% of 10,000 simulations achieved the 60% hit rate target.** This means the AI-Enabled Distributed Defense System, as currently designed, **cannot meet its primary performance objective**.

## 📊 What This Dashboard Shows

### 🎯 **Hero Section - Critical Finding**
- **0% success rate** prominently displayed
- Plain-language explanation of what this means
- Clear recommended actions for decision-makers

### 📈 **Key Metrics**
1. **Failure Rate**: 0% meet 60% hit rate, 69.1% system failure risk
2. **Cost Reality**: Mean $4.03B, 48.3% chance of budget overrun
3. **Timeline Risk**: 40 months to deployment (too slow for current crisis)
4. **Alternative Success**: Shelters are 8x more cost-effective

### 📊 **Visualizations**
- Cost Distribution Chart (bar chart of percentiles)
- Hit Probability Distribution (bar chart of percentiles)
- **Critical**: Cost vs. Performance Scatter showing EMPTY success zone
- Sensitivity Analysis (doughnut chart - Network Availability drives 82% of performance)

### 🔄 **System Comparison**
Honest comparison with clear methodology notes:
- **AI Distributed System**: $4.03B, 46.2% hit rate, 40 months ⚠️
- **Patriot Batteries**: ~$6-7B, 40-50% hit rate, 6-12 months ⚠️
- **Shelters**: $500M, 90%+ protection, 3-6 months ✅
- **Hybrid Approach**: $3.15B, phased deployment, proven systems ✅

### 🎯 **Decision Proposal — Best Long-Term Defense** *(NEW)*
Bayesian decision analysis across **20,000 paired scenarios** (10-yr horizon, 5% discount):
- **Comparison table** of 5 strategies (cost/life, lives saved, P(best))
- **Three-phase portfolio banner**: Passive-first (0–6 mo) → Conditional insurance (6–18 mo) → Critical-node high-end only
- Key findings:
  - Passive-first wins lowest cost-per-life in **100%** of scenarios ($3,458/life)
  - Hybrid saves the most lives in **37%** of scenarios (+39K lives in surges — conditional insurance)
  - AI-killer confirmed dominated from a second, independent modeling angle
  - Value of information: ~0% on cost/life — collect threat-rate data, not more system-cost trivia

> Loads from `data/bayesian_decision.json` (compact export of `research/bayesian_decision_analysis.json`).

### 📋 **Detailed Statistical Analysis**
- Complete cost statistics (mean, median, percentiles, std dev)
- Performance statistics (hit rates, AI accuracy, network availability)
- Sensitivity breakdown by driver
- Risk probability metrics

### ✅ **Data-Driven Recommendations**
**Do NOT:**
- Deploy AI system as primary defense
- Invest full $4B upfront
- Wait 40 months for deployment

**DO:**
- Invest in shelters immediately ($140/life saved)
- Deploy proven systems (Gepard, IRIS-T)
- Build early warning network
- Research AI in parallel with clear milestones

### 📚 **Methodology**
- Open source code
- 10,000 Monte Carlo simulations
- All assumptions documented
- Clear limitations listed

## 🚀 Deployment

### GitHub Pages (Recommended)

1. **Move site files to root or docs**:
   ```bash
   # Option A: Use site/ directory
   git mv site/* .
   git mv site/data/ .
   
   # Option B: Use docs/ directory (clear existing docs first)
   rm -rf docs/*.md
   mv site/* docs/
   mv site/data/ docs/
   ```

2. **Enable GitHub Pages**:
   - Repository Settings → Pages
   - Source: `main` branch, `/ (root)` or `/docs` folder
   - Save

3. **Access**: `https://<username>.github.io/open-rocket-defense-system-research/`

### Local Testing

```bash
cd site
python3 -m http.server 8000
# Open http://localhost:8000
```

### Any Static Host

Upload `site/` directory contents to:
- Netlify
- Vercel
- Cloudflare Pages
- AWS S3 + CloudFront
- Any web server

## 🔄 Updating Data

To update with new simulation results:

```bash
# 1. Run new simulations
python3 scripts/monte_carlo_defense_analysis.py

# 2. Copy results to site/data/
cp research/monte_carlo_analysis.json site/data/
cp research/monte_carlo_results.csv site/data/

# 3. Commit and push
git add site/data/
git commit -m "Update simulation data"
git push
```

GitHub Pages rebuilds automatically in 1-2 minutes.

## 📁 File Structure

```
site/
├── index.html                 # Main dashboard HTML
├── favicon.svg                # Site favicon
├── assets/
│   ├── css/
│   │   └── styles.css         # All styling (CSS variables, dark mode, print)
│   └── js/
│       └── dashboard.js       # All logic (data loading, charts, updates)
├── data/
│   ├── monte_carlo_analysis.json  # Structured analysis results
│   ├── monte_carlo_results.csv    # Sampled simulation data (1,500 of 10,000 rows)
│   └── bayesian_decision.json     # Bayesian decision proposal results (compact export)
├── README.md                  # This file
└── DEPLOYMENT.md              # Deployment guide
```

## 🔍 Key Statistics (Summary)

| Metric | Value | Assessment |
|--------|-------|------------|
| Mean 5-Year Cost | $4.03B | ⚠️ Over budget estimate |
| Mean Hit Probability | 46.2% | ❌ Below 60% target |
| System Failure Risk | 69.1% | ❌ High |
| Meets Budget Target | 48.3% | ⚠️ Coin flip |
| Meets 60% Hit Rate | 0.0% | ❌ Impossible |
| Meets Both Targets | 0.0% | ❌ Not possible |
| Cheaper than Patriot | 100% | ✅ Yes |
| Cheaper than Shelters | 0.0% | ❌ No |
| Full Deployment | 40 months | ❌ Too slow |

## 🛠️ Technical Details

### Dependencies
- **Chart.js 4.4.0** (via CDN) - Interactive charts
- **No build process** - Pure HTML/CSS/JavaScript
- **No server required** - Fully static

### Features
- ✅ Responsive design (mobile-friendly)
- ✅ Keyboard navigation
- ✅ Screen reader support (aria-labels)
- ✅ Print-friendly styles
- ✅ Graceful error handling
- ✅ Loading states
- ✅ Real simulation data
- ✅ Clear methodology disclosure
- ✅ Risk-based recommendations

### Accessibility
- Semantic HTML
- ARIA labels on interactive elements
- Color + text indicators
- Keyboard-operable
- Screens reader compatible

## 🎨 Design Principles

1. **Critical finding first**: Most important information at the top
2. **Honesty over polish**: Real data, clear limitations
3. **Actionable insights**: Every metric connects to a decision
4. **Mobile-first**: Works on all device sizes
5. **Fast**: Static site, minimal dependencies

## 📖 Background

This analysis began as part of the Open Rocket Defense System Research project, examining Ukraine's missile defense options against Kinzhal and other threats.

The Monte Carlo simulation models uncertainty across multiple dimensions:
- Capital and operating costs
- Deployment timelines
- Technical performance
- Threat environment

The result: **The proposed AI system cannot achieve its targets under any realistic scenario.**

## 📞 Support / Questions

For questions about the analysis:
- Review the methodology section in the dashboard
- Check the GitHub repository README
- Examine the simulation code in `scripts/monte_carlo_defense_analysis.py`

## 📝 License

This dashboard and analysis are part of the Open Rocket Defense System Research project. The code is open source and the data is publicly available.

---

**🚨 Remember: 0% of simulations achieved the target. Adjust strategy accordingly.**
