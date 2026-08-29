#!/usr/bin/env python3
"""
Visualize Bayesian decision simulation results for best long-term defense.
Reads research/bayesian_decision_results.csv (paired draws).

Panels:
  1. Cost-per-life medians + 90% HDI (log scale) — the headline
  2. Lives saved expected + HDI
  3. P(best cost/life) and P(most lives) per strategy
  4. Pairwise heatmap P(row beats column on cost/life)
  5. Cost vs lives tradeoff scatter (sampled draws) with dominance frontier
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STRAT = {
    "passive":        ("A", "#2ecc71", "Passive-first"),
    "cruise_active":  ("B", "#3498db", "Cruise-active"),
    "ai_killer":      ("C", "#e67e22", "AI-killer"),
    "hybrid":         ("D", "#9b59b6", "Hybrid doctrine"),
    "high_end":       ("E", "#e74c3c", "High-end missile"),
}

df = pd.read_csv("/home/weissto_local/git/open-rocket-defense-system-research/research/bayesian_decision_results.csv")
df = df.dropna(subset=["strategy"])

fig, axes = plt.subplots(2, 3, figsize=(20, 11))
fig.suptitle("Bayesian Decision Analysis — Best Long-Term Defense (10-yr, discounted, paired draws)",
             fontsize=16, fontweight="bold")

# Panel 1: cost per life
ax = axes[0][0]
order = df.groupby("strategy")["cost_per_life"].median().sort_values().index
labels, meds, lo, hi = [], [], [], []
for s in order:
    sub = df[df.strategy == s]["cost_per_life"]
    labels.append(f"{STRAT[s][0]} · {STRAT[s][2]}")
    meds.append(sub.median()); lo.append(sub.quantile(0.05)); hi.append(sub.quantile(0.95))
y = np.arange(len(labels))
ax.barh(y, meds, color=[STRAT[s][1] for s in order], alpha=0.85)
ax.errorbar(meds, y, xerr=[np.array(meds)-np.array(lo), np.array(hi)-np.array(meds)],
            fmt="none", ecolor="black", capsize=4)
ax.set_yticks(y, labels); ax.set_xscale("log")
ax.set_xlabel("Cost per life saved (USD, log scale)")
ax.set_title("Cost-effectiveness (90% HDI)")
ax.axvline(meds[0], color="gray", ls=":", lw=1)
for i, m in enumerate(meds):
    ax.text(m*1.15, i, f"${m:,.0f}", va="center", fontsize=9)

# Panel 2: lives saved
ax = axes[0][1]
lives_med = df.groupby("strategy")["lives_saved"].median().sort_values(ascending=False)
labels, meds, lo, hi = [], [], [], []
for s in lives_med.index:
    sub = df[df.strategy == s]["lives_saved"]
    labels.append(f"{STRAT[s][0]} · {STRAT[s][2]}")
    meds.append(sub.median()); lo.append(sub.quantile(0.05)); hi.append(sub.quantile(0.95))
y = np.arange(len(labels))
ax.barh(y, meds, color=[STRAT[s][1] for s in lives_med.index], alpha=0.85)
ax.errorbar(meds, y, xerr=[np.array(meds)-np.array(lo), np.array(hi)-np.array(meds)],
            fmt="none", ecolor="black", capsize=4)
ax.set_yticks(y, labels)
ax.set_xlabel("Lives saved (10-yr, discounted)")
ax.set_title("Effectiveness (90% HDI)")
ax.xaxis.set_major_formatter(lambda x, _: f"{x/1e3:.0f}K")

# Panel 3: probability of being best
ax = axes[0][2]
piv_cpl = df.pivot(index="scenario", columns="strategy", values="cost_per_life")
piv_lives = df.pivot(index="scenario", columns="strategy", values="lives_saved")
best_cpl = piv_cpl.idxmin(axis=1).value_counts(normalize=True) * 100
best_lives = piv_lives.idxmax(axis=1).value_counts(normalize=True) * 100
sids = list(STRAT.keys())
x = np.arange(len(sids)); w = 0.38
ax.bar(x - w/2, [best_cpl.get(s, 0) for s in sids], w, color=[STRAT[s][1] for s in sids], alpha=0.8, label="P(best cost/life)")
ax.bar(x + w/2, [best_lives.get(s, 0) for s in sids], w, color=[STRAT[s][1] for s in sids], alpha=0.35, hatch="//", label="P(most lives)")
ax.set_xticks(x, [f"{STRAT[s][0]} · {STRAT[s][2]}" for s in sids], rotation=20, ha="right")
ax.set_ylabel("% of scenarios"); ax.set_title("Probability of being best")
ax.legend(fontsize=8)

# Panel 4: pairwise heatmap
ax = axes[1][0]
n = len(sids)
mat = np.zeros((n, n))
for i, a in enumerate(sids):
    for j, b in enumerate(sids):
        if a != b:
            mat[i, j] = (piv_cpl[a] < piv_cpl[b]).mean() * 100
im = ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=100)
ax.set_xticks(range(n), [STRAT[s][0] for s in sids])
ax.set_yticks(range(n), [STRAT[s][0] for s in sids])
for i in range(n):
    for j in range(n):
        if i != j:
            ax.text(j, i, f"{mat[i,j]:.0f}%", ha="center", va="center", fontsize=9)
ax.set_xlabel("column beats row"); ax.set_ylabel("row beats column")
ax.set_title("P(row beats column on cost/life)"); fig.colorbar(im, ax=ax, shrink=0.85)

# Panel 5: cost vs lives tradeoff scatter (sampled)
ax = axes[1][1]
rng = np.random.default_rng(7)
sample = df.sample(n=4000, random_state=7)
colors = {"passive": "#2ecc71", "cruise_active": "#3498db", "ai_killer": "#e67e22",
          "hybrid": "#9b59b6", "high_end": "#e74c3c"}
for s, c in colors.items():
    sub = sample[sample.strategy == s]
    ax.scatter(sub["cost_per_life"], sub["lives_saved"], s=8, alpha=0.25, color=c,
               label=f"{STRAT[s][0]} · {STRAT[s][2]}")
ax.set_xscale("log"); ax.set_xlabel("Cost per life (USD, log)"); ax.set_ylabel("Lives saved")
ax.set_title("Tradeoff: cost-effectiveness vs lives (4000 sampled scenarios)")
ax.legend(fontsize=8, markerscale=2)

# Panel 6: cost vs lives tradeoff means
ax = axes[1][2]
for s in sids:
    sub = df[df.strategy == s]
    ax.scatter(sub["cost_per_life"].median(), sub["lives_saved"].median(), s=200, color=colors[s],
               edgecolor="black", zorder=5, label=f"{STRAT[s][0]} · {STRAT[s][2]}")
    ax.annotate(STRAT[s][0], (sub["cost_per_life"].median(), sub["lives_saved"].median()),
                textcoords="offset points", xytext=(12, -6), fontsize=11, fontweight="bold")
ax.set_xscale("log"); ax.set_xlabel("Cost per life (USD, log)"); ax.set_ylabel("Lives saved (median)")
ax.set_title("Median strategic frontier")
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out = "/home/weissto_local/git/open-rocket-defense-system-research/research/bayesian_decision_visualization.png"
plt.savefig(out, dpi=150)
print(f"Saved: {out}")
