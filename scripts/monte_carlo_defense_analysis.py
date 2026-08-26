#!/usr/bin/env python3
"""
Monte Carlo Simulation for AI-Enabled Distributed Defense System Analysis

This simulation quantifies uncertainty across multiple dimensions:
- Capital and operating costs
- Timeline to deployment
- System performance (hit rates, availability)
- Threat levels and attrition
- Technical success probabilities

Author: Analysis for Open Rocket Defense System Research
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation"""
    n_simulations: int = 10000
    time_horizon_years: int = 5
    discount_rate: float = 0.05
    kinzhal_daily_rate: float = 50  # Average daily Kinzhal attacks
    civilian_casualties_per_leak: float = 100  # Avg casualties per unintercepted Kinzhal

class CostModel:
    """Cost uncertainty model"""
    
    @staticmethod
    def sensor_node_cost() -> float:
        """
        Cost per sensor node (radar, IR, EW, compute, power)
        Distribution: Triangular (optimistic, most likely, pessimistic)
        """
        return np.random.triangular(
            left=100000,      # Optimistic: $100K (as originally estimated)
            mode=500000,      # Most likely: $500K (realistic military-grade)
            right=1000000     # Pessimistic: $1M (high-end systems)
        )
    
    @staticmethod
    def interceptor_node_cost() -> float:
        """Cost per interceptor node (system + integration)"""
        return np.random.triangular(
            left=2000000,     # Optimistic: $2M
            mode=5000000,     # Most likely: $5M
            right=10000000    # Pessimistic: $10M
        )
    
    @staticmethod
    def ai_development_cost() -> float:
        """Total AI development cost"""
        return np.random.triangular(
            left=50000000,    # Optimistic: $50M
            mode=150000000,   # Most likely: $150M
            right=300000000   # Pessimistic: $300M
        )
    
    @staticmethod
    def annual_operating_cost(capital_cost: float) -> float:
        """Annual operating cost as % of capital + fixed costs"""
        personnel = np.random.normal(150000000, 30000000)  # $150M ± $30M
        fuel = np.random.normal(50000000, 15000000)         # $50M ± $15M
        maintenance = np.random.normal(100000000, 30000000) # $100M ± $30M
        interceptors = np.random.normal(200000000, 80000000) # $200M ± $80M
        other = np.random.normal(50000000, 15000000)         # $50M ± $15M
        
        return max(personnel + fuel + maintenance + interceptors + other, 100000000)
    
    @staticmethod
    def patriot_battery_cost() -> float:
        """Cost per Patriot battery"""
        return np.random.normal(1500000000, 300000000)  # $1.5B ± $300M

class TimelineModel:
    """Timeline uncertainty model"""
    
    @staticmethod
    def prototype_months() -> float:
        """Months to prototype deployment"""
        return np.random.triangular(
            left=12,
            mode=18,
            right=30
        )
    
    @staticmethod
    def partial_deployment_months() -> float:
        """Months to 200-node deployment"""
        return np.random.triangular(
            left=18,
            mode=24,
            right=36
        )
    
    @staticmethod
    def full_deployment_months() -> float:
        """Months to full 500-node deployment"""
        return np.random.triangular(
            left=24,
            mode=36,
            right=60
        )
    
    @staticmethod
    def shelter_deployment_months() -> float:
        """Months to shelter network (faster alternative)"""
        return np.random.triangular(
            left=3,
            mode=6,
            right=12
        )

class PerformanceModel:
    """System performance uncertainty model"""
    
    @staticmethod
    def ai_classification_accuracy() -> float:
        """AI threat classification accuracy"""
        # Beta distribution bounded between 0 and 1
        return np.random.beta(18, 2)  # Mean ~0.9, but can be lower
    
    @staticmethod
    def network_availability() -> float:
        """Network uptime (surviving EW, SEAD, failures)"""
        return np.random.beta(8, 2)  # Mean ~0.8
    
    @staticmethod
    def kinzhal_hit_probability(
        ai_accuracy: float,
        network_availability: float,
        baseline_patriot: float = 0.4
    ) -> float:
        """
        Kinzhal intercept probability
        Depends on AI accuracy and network availability
        """
        # Base probability from AI performance
        base_prob = baseline_patriot * (1 + ai_accuracy * 0.5)
        
        # Apply network availability
        effective_prob = base_prob * network_availability
        
        # Cap at reasonable maximum
        return min(effective_prob, 0.85)
    
    @staticmethod
    def shelter_casualty_reduction() -> float:
        """Casualty reduction if shelter available"""
        return np.random.beta(18, 2)  # Mean ~0.9 (90% reduction)
    
    @staticmethod
    def shelter_coverage() -> float:
        """Percentage of population with shelter access"""
        return np.random.triangular(
            left=0.3,    # 30% coverage (poor)
            mode=0.7,    # 70% coverage (moderate)
            right=0.95   # 95% coverage (excellent)
        )

class ThreatModel:
    """Threat level uncertainty model"""
    
    @staticmethod
    def daily_kinzhal_rate() -> float:
        """Daily Kinzhal attacks (varies by conflict phase)"""
        return np.random.lognormal(
            mean=np.log(50),   # Median 50
            sigma=0.5          # Variance
        )
    
    @staticmethod
    def monthly_kinzhal_rate() -> float:
        """Monthly Kinzhal attacks"""
        return self.daily_kinzhal_rate() * 30
    
    @staticmethod
    def sead_attrition_rate() -> float:
        """Monthly node attrition from SEAD attacks"""
        return np.random.triangular(
            left=0.02,   # 2% per month (low)
            mode=0.05,   # 5% per month (moderate)
            right=0.15   # 15% per month (high)
        )
    
    @staticmethod
    def ew_effectiveness() -> float:
        """Russian EW effectiveness (0-1, higher = worse for us)"""
        return np.random.beta(3, 7)  # Mean ~0.3 (moderate threat)

class MonteCarloSimulation:
    """Main Monte Carlo simulation engine"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.results = []
        
    def run_single_simulation(self) -> Dict:
        """Run one simulation iteration"""
        
        # Sample cost parameters
        sensor_cost = CostModel.sensor_node_cost()
        interceptor_cost = CostModel.interceptor_node_cost()
        ai_dev_cost = CostModel.ai_development_cost()
        
        # Calculate capital costs
        n_sensors = 500
        n_interceptors = 200
        
        sensor_network_cost = sensor_cost * n_sensors
        interceptor_network_cost = interceptor_cost * n_interceptors
        ai_infrastructure_cost = ai_dev_cost * 1.5  # 1.5x for infrastructure
        
        total_capital_cost = (
            sensor_network_cost + 
            interceptor_network_cost + 
            ai_infrastructure_cost
        )
        
        # Sample timeline
        prototype_months = TimelineModel.prototype_months()
        partial_months = TimelineModel.partial_deployment_months()
        full_months = TimelineModel.full_deployment_months()
        
        # Sample performance
        ai_accuracy = PerformanceModel.ai_classification_accuracy()
        network_availability = PerformanceModel.network_availability()
        hit_prob = PerformanceModel.kinzhal_hit_probability(
            ai_accuracy, network_availability
        )
        shelter_reduction = PerformanceModel.shelter_casualty_reduction()
        shelter_coverage = PerformanceModel.shelter_coverage()
        
        # Sample threat
        daily_kinzhal = ThreatModel.daily_kinzhal_rate()
        sead_attrition = ThreatModel.sead_attrition_rate()
        ew_effectiveness = ThreatModel.ew_effectiveness()
        
        # Adjust network availability for EW
        network_availability *= (1 - ew_effectiveness * 0.3)
        network_availability = max(network_availability, 0.3)  # Floor
        
        # Calculate annual operating costs
        annual_opex = CostModel.annual_operating_cost(total_capital_cost)
        
        # Calculate 5-year costs (discounted)
        total_costs = [total_capital_cost]
        for year in range(1, self.config.time_horizon_years + 1):
            discounted_opex = annual_opex / ((1 + self.config.discount_rate) ** year)
            total_costs.append(discounted_opex)
        total_5yr_cost = sum(total_costs)
        
        # Calculate effectiveness metrics
        total_kinzhal_5yr = daily_kinzhal * 365 * self.config.time_horizon_years
        intercepted_kinzhal = total_kinzhal_5yr * hit_prob
        leaked_kinzhal = total_kinzhal_5yr - intercepted_kinzhal
        
        # Casualty calculation (with shelter alternative)
        casualties_without_defense = leaked_kinzhal * self.config.civilian_casualties_per_leak
        casualties_with_shelters = casualties_without_defense * (1 - shelter_reduction) * (1 - shelter_coverage)
        casualties_with_ai_system = casualties_without_defense * (1 - shelter_coverage)
        
        # Calculate cost-effectiveness
        cost_per_life_saved = total_5yr_cost / max(1, casualties_without_defense - casualties_with_ai_system)
        
        # Calculate alternative: Patriot-only
        n_patriot_needed = max(1, int(total_kinzhal_5yr / 100))  # Rough estimate
        patriot_cost = n_patriot_needed * CostModel.patriot_battery_cost()
        patriot_5yr_cost = patriot_cost + (CostModel.annual_operating_cost(patriot_cost) * 5)
        
        # Calculate alternative: Shelters-only
        shelter_cost = 500000000  # $500M for comprehensive network
        shelter_5yr_cost = shelter_cost  # No significant OpEx
        
        # ROI calculation
        savings_vs_patriot = patriot_5yr_cost - total_5yr_cost
        savings_vs_shelters = shelter_5yr_cost - total_5yr_cost
        
        # Risk metrics
        system_failure_risk = 1 - (ai_accuracy * network_availability * hit_prob)
        budget_overrun_risk = 1 if total_5yr_cost > 5000000000 else 0  # $5B threshold
        
        return {
            # Costs
            'total_capital_cost': total_capital_cost,
            'annual_opex': annual_opex,
            'total_5yr_cost': total_5yr_cost,
            'patriot_5yr_cost': patriot_5yr_cost,
            'shelter_5yr_cost': shelter_5yr_cost,
            'savings_vs_patriot': savings_vs_patriot,
            'savings_vs_shelters': savings_vs_shelters,
            
            # Timeline
            'prototype_months': prototype_months,
            'partial_months': partial_months,
            'full_months': full_months,
            
            # Performance
            'ai_accuracy': ai_accuracy,
            'network_availability': network_availability,
            'hit_probability': hit_prob,
            'sead_attrition_rate': sead_attrition,
            'ew_effectiveness': ew_effectiveness,
            
            # Threat
            'daily_kinzhal_rate': daily_kinzhal,
            'total_kinzhal_5yr': total_kinzhal_5yr,
            'intercepted_kinzhal': intercepted_kinzhal,
            'leaked_kinzhal': leaked_kinzhal,
            
            # Casualties
            'casualties_without_defense': casualties_without_defense,
            'casualties_with_ai': casualties_with_ai_system,
            'casualties_with_shelters': casualties_with_shelters,
            'lives_saved_by_ai': max(0, casualties_without_defense - casualties_with_ai_system),
            'lives_saved_by_shelters': max(0, casualties_without_defense - casualties_with_shelters),
            
            # Cost-effectiveness
            'cost_per_life_saved': cost_per_life_saved,
            'shelter_cost_per_life': shelter_5yr_cost / max(1, casualties_without_defense - casualties_with_shelters),
            
            # Risk
            'system_failure_risk': system_failure_risk,
            'budget_overrun_risk': budget_overrun_risk,
            
            # Binary outcomes
            'is_cheaper_than_patriot': 1 if savings_vs_patriot > 0 else 0,
            'is_cheaper_than_shelters': 1 if savings_vs_shelters > 0 else 0,
            'hits_target_budget': 1 if total_5yr_cost < 4000000000 else 0,  # $4B target
            'hits_target_performance': 1 if hit_prob > 0.6 else 0,  # 60% hit rate target
        }
    
    def run_simulation(self) -> pd.DataFrame:
        """Run full Monte Carlo simulation"""
        print(f"Running {self.config.n_simulations:,} Monte Carlo simulations...")
        
        results = []
        for i in range(self.config.n_simulations):
            if i % 1000 == 0 and i > 0:
                print(f"  Completed {i:,} simulations...")
            result = self.run_single_simulation()
            results.append(result)
        
        self.results = pd.DataFrame(results)
        print(f"Simulation complete. Analyzing {len(self.results):,} iterations...")
        
        return self.results
    
    def analyze_results(self) -> Dict:
        """Analyze simulation results and generate statistics"""
        
        if self.results is None or len(self.results) == 0:
            raise ValueError("No simulation results available. Run simulation first.")
        
        analysis = {
            'summary': {},
            'cost_analysis': {},
            'performance_analysis': {},
            'risk_analysis': {},
            'correlations': {},
            'sensitivity': {},
            'recommendations': []
        }
        
        # Summary statistics
        analysis['summary'] = {
            'n_simulations': len(self.results),
            'mean_total_cost': self.results['total_5yr_cost'].mean(),
            'median_total_cost': self.results['total_5yr_cost'].median(),
            'std_total_cost': self.results['total_5yr_cost'].std(),
            'p10_total_cost': self.results['total_5yr_cost'].quantile(0.10),
            'p90_total_cost': self.results['total_5yr_cost'].quantile(0.90),
            'mean_hit_probability': self.results['hit_probability'].mean(),
            'mean_lives_saved': self.results['lives_saved_by_ai'].mean(),
            'mean_cost_per_life': self.results['cost_per_life_saved'].mean(),
        }
        
        # Cost analysis
        analysis['cost_analysis'] = {
            'cheaper_than_patriot_pct': self.results['is_cheaper_than_patriot'].mean() * 100,
            'cheaper_than_shelters_pct': self.results['is_cheaper_than_shelters'].mean() * 100,
            'mean_savings_vs_patriot': self.results['savings_vs_patriot'].mean(),
            'median_savings_vs_patriot': self.results['savings_vs_patriot'].median(),
            'p10_savings_vs_patriot': self.results['savings_vs_patriot'].quantile(0.10),
            'p90_savings_vs_patriot': self.results['savings_vs_patriot'].quantile(0.90),
            'budget_target_hit_rate': self.results['hits_target_budget'].mean() * 100,
        }
        
        # Performance analysis
        analysis['performance_analysis'] = {
            'mean_hit_probability': self.results['hit_probability'].mean(),
            'median_hit_probability': self.results['hit_probability'].median(),
            'p10_hit_probability': self.results['hit_probability'].quantile(0.10),
            'p90_hit_probability': self.results['hit_probability'].quantile(0.90),
            'performance_target_hit_rate': self.results['hits_target_performance'].mean() * 100,
            'mean_ai_accuracy': self.results['ai_accuracy'].mean(),
            'mean_network_availability': self.results['network_availability'].mean(),
        }
        
        # Risk analysis
        analysis['risk_analysis'] = {
            'system_failure_risk': self.results['system_failure_risk'].mean(),
            'budget_overrun_risk': self.results['budget_overrun_risk'].mean(),
            'both_targets_hit_rate': (
                (self.results['hits_target_budget'] == 1) & 
                (self.results['hits_target_performance'] == 1)
            ).mean() * 100,
            'worst_case_cost': self.results['total_5yr_cost'].quantile(0.95),
            'worst_case_lives_lost': self.results['casualties_with_ai'].quantile(0.95),
        }
        
        # Correlation analysis
        key_vars = [
            'total_capital_cost',
            'ai_accuracy',
            'network_availability',
            'hit_probability',
            'sead_attrition_rate',
            'ew_effectiveness',
        ]
        
        analysis['correlations'] = {}
        for var in key_vars:
            corr_with_cost = self.results[var].corr(self.results['total_5yr_cost'])
            corr_with_performance = self.results[var].corr(self.results['hit_probability'])
            analysis['correlations'][var] = {
                'correlation_with_cost': corr_with_cost,
                'correlation_with_performance': corr_with_performance,
            }
        
        # Sensitivity analysis (which variables drive outcomes most)
        analysis['sensitivity'] = {
            'cost_drivers': self._calculate_sensitivity('total_5yr_cost'),
            'performance_drivers': self._calculate_sensitivity('hit_probability'),
            'lives_saved_drivers': self._calculate_sensitivity('lives_saved_by_ai'),
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _calculate_sensitivity(self, target_var: str) -> Dict[str, float]:
        """Calculate which input variables most affect target variable"""
        
        input_vars = [
            'total_capital_cost',
            'ai_accuracy',
            'network_availability',
            'sead_attrition_rate',
            'ew_effectiveness',
            'daily_kinzhal_rate',
        ]
        
        sensitivities = {}
        for var in input_vars:
            if var in self.results.columns:
                corr = self.results[var].corr(self.results[target_var])
                sensitivities[var] = abs(corr)
        
        # Normalize to sum to 1
        total = sum(sensitivities.values())
        if total > 0:
            sensitivities = {k: v/total for k, v in sensitivities.items()}
        
        return dict(sorted(sensitivities.items(), key=lambda x: x[1], reverse=True))
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Cost recommendations
        if analysis['cost_analysis']['cheaper_than_patriot_pct'] < 80:
            recommendations.append(
                f"COST RISK: Only {analysis['cost_analysis']['cheaper_than_patriot_pct']:.1f}% "
                "of simulations cheaper than Patriot. Consider cost reduction strategies."
            )
        
        if analysis['cost_analysis']['budget_target_hit_rate'] < 50:
            recommendations.append(
                f"BUDGET RISK: Only {analysis['cost_analysis']['budget_target_hit_rate']:.1f}% "
                "of simulations meet $4B target. Budget estimates may be optimistic."
            )
        
        # Performance recommendations
        if analysis['performance_analysis']['performance_target_hit_rate'] < 50:
            recommendations.append(
                f"PERFORMANCE RISK: Only {analysis['performance_analysis']['performance_target_hit_rate']:.1f}% "
                "of simulations achieve 60%+ hit rate. Technical risk is significant."
            )
        
        # Risk recommendations
        if analysis['risk_analysis']['system_failure_risk'] > 0.3:
            recommendations.append(
                f"HIGH FAILURE RISK: {analysis['risk_analysis']['system_failure_risk']:.1%} "
                "probability of system underperformance. Implement extensive testing and fallback plans."
            )
        
        # Comparative recommendations
        if analysis['cost_analysis']['cheaper_than_shelters_pct'] < 30:
            recommendations.append(
                f"SHELTER ALTERNATIVE: Shelters-only is cheaper in {100-analysis['cost_analysis']['cheaper_than_shelters_pct']:.1f}% "
                "of simulations. Consider shelters as primary investment."
            )
        
        # Sensitivity-based recommendations
        top_cost_driver = list(analysis['sensitivity']['cost_drivers'].keys())[0]
        recommendations.append(
            f"COST FOCUS: {top_cost_driver.replace('_', ' ').title()} is the largest cost driver. "
            "Prioritize cost control in this area."
        )
        
        top_perf_driver = list(analysis['sensitivity']['performance_drivers'].keys())[0]
        recommendations.append(
            f"PERFORMANCE FOCUS: {top_perf_driver.replace('_', ' ').title()} most affects hit rate. "
            "Invest in improving this capability."
        )
        
        # Timeline recommendations
        mean_full_months = self.results['full_months'].mean()
        if mean_full_months > 36:
            recommendations.append(
                f"TIMELINE RISK: Mean deployment time is {mean_full_months:.0f} months "
                "(3+ years). Consider phased approach with interim solutions."
            )
        
        return recommendations
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate human-readable report"""
        
        analysis = self.analyze_results()
        
        report = []
        report.append("=" * 80)
        report.append("MONTE CARLO SIMULATION REPORT")
        report.append("AI-Enabled Distributed Defense System")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Simulations: {analysis['summary']['n_simulations']:,}")
        report.append("")
        
        # Executive Summary
        report.append("-" * 80)
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)
        report.append(f"""
Key Findings:
• Mean 5-year cost: ${analysis['summary']['mean_total_cost']:,.0f}
• Median 5-year cost: ${analysis['summary']['median_total_cost']:,.0f}
• Cost range (10-90%): ${analysis['summary']['p10_total_cost']:,.0f} - ${analysis['summary']['p90_total_cost']:,.0f}
• Mean hit probability: {analysis['performance_analysis']['mean_hit_probability']:.1%}
• Mean lives saved: {analysis['summary']['mean_lives_saved']:,.0f}
• Mean cost per life saved: ${analysis['summary']['mean_cost_per_life']:,.0f}

Probability of Success:
• Cheaper than Patriot: {analysis['cost_analysis']['cheaper_than_patriot_pct']:.1f}%
• Cheaper than shelters: {analysis['cost_analysis']['cheaper_than_shelters_pct']:.1f}%
• Meets budget target: {analysis['cost_analysis']['budget_target_hit_rate']:.1f}%
• Meets performance target: {analysis['performance_analysis']['performance_target_hit_rate']:.1f}%
• Meets BOTH targets: {analysis['risk_analysis']['both_targets_hit_rate']:.1f}%

Risk Assessment:
• System failure risk: {analysis['risk_analysis']['system_failure_risk']:.1%}
• Budget overrun risk: {analysis['risk_analysis']['budget_overrun_risk']:.1%}
• Worst-case cost (95th percentile): ${analysis['risk_analysis']['worst_case_cost']:,.0f}
""")
        
        # Recommendations
        report.append("-" * 80)
        report.append("KEY RECOMMENDATIONS")
        report.append("-" * 80)
        for i, rec in enumerate(analysis['recommendations'], 1):
            report.append(f"{i}. {rec}")
            report.append("")
        
        # Cost Analysis
        report.append("-" * 80)
        report.append("DETAILED COST ANALYSIS")
        report.append("-" * 80)
        report.append(f"""
Capital Cost Statistics:
• Mean: ${analysis['summary']['mean_total_cost']:,.0f}
• Median: ${analysis['summary']['median_total_cost']:,.0f}
• Std Dev: ${analysis['summary']['std_total_cost']:,.0f}
• 10th percentile: ${analysis['summary']['p10_total_cost']:,.0f}
• 90th percentile: ${analysis['summary']['p90_total_cost']:,.0f}

Savings vs. Patriot (5-year):
• Mean savings: ${analysis['cost_analysis']['mean_savings_vs_patriot']:,.0f}
• Median savings: ${analysis['cost_analysis']['median_savings_vs_patriot']:,.0f}
• 10th percentile: ${analysis['cost_analysis']['p10_savings_vs_patriot']:,.0f}
• 90th percentile: ${analysis['cost_analysis']['p90_savings_vs_patriot']:,.0f}
""")
        
        # Performance Analysis
        report.append("-" * 80)
        report.append("DETAILED PERFORMANCE ANALYSIS")
        report.append("-" * 80)
        report.append(f"""
Hit Probability Statistics:
• Mean: {analysis['performance_analysis']['mean_hit_probability']:.1%}
• Median: {analysis['performance_analysis']['median_hit_probability']:.1%}
• 10th percentile: {analysis['performance_analysis']['p10_hit_probability']:.1%}
• 90th percentile: {analysis['performance_analysis']['p90_hit_probability']:.1%}

AI Accuracy: {analysis['performance_analysis']['mean_ai_accuracy']:.1%}
Network Availability: {analysis['performance_analysis']['mean_network_availability']:.1%}
""")
        
        # Sensitivity Analysis
        report.append("-" * 80)
        report.append("SENSITIVITY ANALYSIS")
        report.append("-" * 80)
        report.append("\nTop Cost Drivers:")
        for var, importance in list(analysis['sensitivity']['cost_drivers'].items())[:3]:
            report.append(f"  • {var.replace('_', ' ').title()}: {importance:.1%} of variance")
        
        report.append("\nTop Performance Drivers:")
        for var, importance in list(analysis['sensitivity']['performance_drivers'].items())[:3]:
            report.append(f"  • {var.replace('_', ' ').title()}: {importance:.1%} of variance")
        
        report.append("\nTop Lives-Saved Drivers:")
        for var, importance in list(analysis['sensitivity']['lives_saved_drivers'].items())[:3]:
            report.append(f"  • {var.replace('_', ' ').title()}: {importance:.1%} of variance")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            print(f"\nReport saved to: {output_path}")
        
        return report_text
    
    def save_results(self, path: str):
        """Save simulation results to CSV"""
        self.results.to_csv(path, index=False)
        print(f"Results saved to: {path}")


def main():
    """Main entry point"""
    
    print("=" * 80)
    print("MONTE CARLO SIMULATION FOR AI-ENABLED DISTRIBUTED DEFENSE")
    print("=" * 80)
    print()
    
    # Configure simulation
    config = SimulationConfig(
        n_simulations=10000,
        time_horizon_years=5,
        discount_rate=0.05,
        kinzhal_daily_rate=50,
        civilian_casualties_per_leak=100
    )
    
    # Run simulation
    sim = MonteCarloSimulation(config)
    results = sim.run_simulation()
    
    # Generate report
    report = sim.generate_report(
        output_path='/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_report.txt'
    )
    
    # Save detailed results
    sim.save_results(
        '/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_results.csv'
    )
    
    # Save analysis as JSON
    analysis = sim.analyze_results()
    with open('/home/weissto_local/git/open-rocket-defense-system-research/research/monte_carlo_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print("\nOutput files:")
    print("  • monte_carlo_report.txt - Human-readable report")
    print("  • monte_carlo_results.csv - Detailed simulation data")
    print("  • monte_carlo_analysis.json - Structured analysis")
    print("\n" + report)


if __name__ == "__main__":
    main()
