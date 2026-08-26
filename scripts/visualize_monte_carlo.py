#!/usr/bin/env python3
"""
Visualization of Monte Carlo Simulation Results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import json

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load results
results = pd.read_csv('/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_results.csv')

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# 1. Cost Distribution
ax1 = fig.add_subplot(gs[0, 0])
ax1.hist(results['total_5yr_cost']/1e9, bins=50, alpha=0.7, edgecolor='black')
ax1.axvline(results['total_5yr_cost'].mean()/1e9, color='red', linestyle='--', linewidth=2, label=f'Mean: ${results["total_5yr_cost"].mean()/1e9:.1f}B')
ax1.axvline(results['total_5yr_cost'].quantile(0.10)/1e9, color='orange', linestyle=':', label=f'10th: ${results["total_5yr_cost"].quantile(0.10)/1e9:.1f}B')
ax1.axvline(results['total_5yr_cost'].quantile(0.90)/1e9, color='green', linestyle=':', label=f'90th: ${results["total_5yr_cost"].quantile(0.90)/1e9:.1f}B')
ax1.set_xlabel('5-Year Total Cost (Billions USD)')
ax1.set_ylabel('Frequency')
ax1.set_title('Cost Distribution (10,000 Simulations)')
ax1.legend()

# 2. Hit Probability Distribution
ax2 = fig.add_subplot(gs[0, 1])
ax2.hist(results['hit_probability']*100, bins=50, alpha=0.7, edgecolor='black', color='green')
ax2.axvline(results['hit_probability'].mean()*100, color='red', linestyle='--', linewidth=2, label=f'Mean: {results["hit_probability"].mean()*100:.1f}%')
ax2.axvline(60, color='orange', linestyle=':', linewidth=2, label='Target: 60%')
ax2.set_xlabel('Hit Probability (%)')
ax2.set_ylabel('Frequency')
ax2.set_title('Hit Probability Distribution')
ax2.legend()

# 3. Cost vs Performance Scatter
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(results['total_5yr_cost']/1e9, results['hit_probability']*100, 
           alpha=0.01, s=1, c='blue')
ax3.axhline(60, color='red', linestyle='--', linewidth=2, label='Performance Target')
ax3.axvline(4, color='orange', linestyle='--', linewidth=2, label='Budget Target ($4B)')
ax3.set_xlabel('5-Year Cost (Billions USD)')
ax3.set_ylabel('Hit Probability (%)')
ax3.set_title('Cost vs Performance Trade-off')
ax3.legend()

# Add quadrant labels
ax3.text(2, 70, 'High Cost\nHigh Perf', fontsize=10, ha='center')
ax3.text(6, 70, 'High Cost\nLow Perf', fontsize=10, ha='center')
ax3.text(2, 30, 'Low Cost\nHigh Perf', fontsize=10, ha='center')
ax3.text(6, 30, 'Low Cost\nLow Perf', fontsize=10, ha='center')

# 4. Network Availability vs Hit Probability
ax4 = fig.add_subplot(gs[1, 0])
ax4.scatter(results['network_availability']*100, results['hit_probability']*100,
           alpha=0.01, s=1, c='green')
ax4.set_xlabel('Network Availability (%)')
ax4.set_ylabel('Hit Probability (%)')
ax4.set_title('Network Availability vs Hit Probability')

# 5. AI Accuracy vs Hit Probability
ax5 = fig.add_subplot(gs[1, 1])
ax5.scatter(results['ai_accuracy']*100, results['hit_probability']*100,
           alpha=0.01, s=1, c='purple')
ax5.set_xlabel('AI Classification Accuracy (%)')
ax5.set_ylabel('Hit Probability (%)')
ax5.set_title('AI Accuracy vs Hit Probability')

# 6. Cumulative Distribution Function (Cost)
ax6 = fig.add_subplot(gs[1, 2])
sorted_costs = np.sort(results['total_5yr_cost'])
cdf = np.arange(1, len(sorted_costs)+1) / len(sorted_costs)
ax6.plot(sorted_costs/1e9, cdf, linewidth=2)
ax6.axvline(4, color='red', linestyle='--', linewidth=2, label='$4B Target')
ax6.set_xlabel('5-Year Cost (Billions USD)')
ax6.set_ylabel('Cumulative Probability')
ax6.set_title('Cost Cumulative Distribution')
ax6.legend()

# 7. Sensitivity Analysis
ax7 = fig.add_subplot(gs[2, 0])
sensitivity_data = {
    'Capital Cost': 0.947,
    'Network Availability': 0.023,
    'EW Effectiveness': 0.016,
    'AI Accuracy': 0.014
}
colors = ['red' if v > 0.5 else 'orange' for v in sensitivity_data.values()]
bars = ax7.barh(list(sensitivity_data.keys()), list(sensitivity_data.values()), color=colors)
ax7.set_xlabel('Variance Explained')
ax7.set_title('Cost Sensitivity (Top Drivers)')
for bar, val in zip(bars, sensitivity_data.values()):
    ax7.text(val + 0.02, bar.get_y() + bar.get_height()/2, 
            f'{val:.1%}', va='center', fontsize=10)

# 8. Performance Sensitivity
ax8 = fig.add_subplot(gs[2, 1])
perf_sensitivity = {
    'Network Availability': 0.817,
    'AI Accuracy': 0.135,
    'EW Effectiveness': 0.014
}
colors = ['red' if v > 0.5 else 'orange' for v in perf_sensitivity.values()]
bars = ax8.barh(list(perf_sensitivity.keys()), list(perf_sensitivity.values()), color=colors)
ax8.set_xlabel('Variance Explained')
ax8.set_title('Performance Sensitivity (Top Drivers)')
for bar, val in zip(bars, perf_sensitivity.values()):
    ax8.text(val + 0.02, bar.get_y() + bar.get_height()/2, 
            f'{val:.1%}', va='center', fontsize=10)

# 9. Key Metrics Summary
ax9 = fig.add_subplot(gs[2, 2])
ax9.axis('off')
summary_text = f"""
KEY METRICS SUMMARY
{'='*50}

COST METRICS:
• Mean 5-year cost: ${results['total_5yr_cost'].mean()/1e9:.2f}B
• Median cost: ${results['total_5yr_cost'].median()/1e9:.2f}B
• Cost range (10-90%): ${results['total_5yr_cost'].quantile(0.10)/1e9:.2f}B - ${results['total_5yr_cost'].quantile(0.90)/1e9:.2f}B
• Budget target hit rate: {results['hits_target_budget'].mean()*100:.1f}%

PERFORMANCE METRICS:
• Mean hit probability: {results['hit_probability'].mean()*100:.1f}%
• Median hit probability: {results['hit_probability'].median()*100:.1f}%
• Performance target hit rate: {results['hits_target_performance'].mean()*100:.1f}%
• Both targets hit rate: {((results['hits_target_budget']==1) & (results['hits_target_performance']==1)).mean()*100:.1f}%

RISK METRICS:
• System failure risk: {results['system_failure_risk'].mean()*100:.1f}%
• Budget overrun risk: {results['budget_overrun_risk'].mean()*100:.1f}%

COMPARATIVE:
• Cheaper than Patriot: {results['is_cheaper_than_patriot'].mean()*100:.1f}%
• Cheaper than shelters: {results['is_cheaper_than_shelters'].mean()*100:.1f}%
"""
ax9.text(0.1, 0.9, summary_text, transform=ax9.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('Monte Carlo Simulation Results: AI-Enabled Distributed Defense System', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_visualization.png', 
           dpi=150, bbox_inches='tight', facecolor='white')
print("Visualization saved to: monte_carlo_visualization.png")

# Create additional detailed analysis
fig2, axes = plt.subplots(2, 2, figsize=(16, 12))
fig2.suptitle('Advanced Analysis', fontsize=14, fontweight='bold')

# 1. Cost vs Timeline
axes[0, 0].scatter(results['full_months'], results['total_5yr_cost']/1e9, alpha=0.01, s=1)
axes[0, 0].set_xlabel('Full Deployment Time (months)')
axes[0, 0].set_ylabel('5-Year Cost (Billions USD)')
axes[0, 0].set_title('Deployment Time vs Cost')

# 2. Hit Probability vs Attrition
axes[0, 1].scatter(results['sead_attrition_rate']*100, results['hit_probability']*100, alpha=0.01, s=1, c='red')
axes[0, 1].set_xlabel('SEAD Attrition Rate (%) per month')
axes[0, 1].set_ylabel('Hit Probability (%)')
axes[0, 1].set_title('SEAD Attrition vs Hit Probability')

# 3. Cost Per Life Saved Distribution
axes[1, 0].hist(results['cost_per_life_saved'], bins=50, alpha=0.7, edgecolor='black', color='green')
axes[1, 0].set_xlabel('Cost Per Life Saved (USD)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Cost-Effectiveness Distribution')
axes[1, 0].axvline(results['cost_per_life_saved'].median(), color='red', linestyle='--', linewidth=2, 
                  label=f'Median: ${results["cost_per_life_saved"].median():,.0f}')
axes[1, 0].legend()

# 4. Lives Saved Distribution
axes[1, 1].hist(results['lives_saved_by_ai']/1000, bins=50, alpha=0.7, edgecolor='black', color='blue')
axes[1, 1].set_xlabel('Lives Saved (Thousands)')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Lives Saved Distribution')
axes[1, 1].axvline(results['lives_saved_by_ai'].mean()/1000, color='red', linestyle='--', linewidth=2,
                  label=f'Mean: {results["lives_saved_by_ai"].mean()/1000:.1f}K')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_advanced_analysis.png', 
           dpi=150, bbox_inches='tight', facecolor='white')
print("Advanced analysis saved to: monte_carlo_advanced_analysis.png")

plt.show()
