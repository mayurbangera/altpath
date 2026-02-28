"""
Antigravity – Explainability Engine
Multi-level explanations: summary, factor attribution, counterfactual, sensitivity, narrative.
"""

import numpy as np
from app.core.state_model import UserState, DecisionDelta, SimulationResult
from app.simulation.monte_carlo import MonteCarloEngine


class ExplainabilityEngine:
    """
    Generates multi-level explanations for simulation results.
    """

    def __init__(self):
        self.mc_engine = MonteCarloEngine()

    def generate_explanation(
        self,
        state: UserState,
        decision: DecisionDelta,
        result: SimulationResult,
    ) -> dict:
        """Generate comprehensive explanation for a simulation result."""
        return {
            "summary": self._executive_summary(result),
            "factor_attribution": result.top_factors,
            "risk_breakdown": self._risk_breakdown(result),
            "counterfactuals": self._generate_counterfactuals(state, decision),
            "assumptions": self._list_assumptions(state, decision),
            "narrative": self._generate_narrative(state, decision, result),
            "regret_score": self._compute_regret_score(result),
            "disclaimer": (
                "This is a probabilistic decision aid based on simulated scenarios. "
                "It is NOT a prediction of the future. Consult qualified professionals "
                "for major financial, health, or legal decisions."
            ),
        }

    def _executive_summary(self, result: SimulationResult) -> str:
        """One-paragraph summary of outcome."""
        prob = result.success_probability * 100
        risk_parts = []
        if result.burnout_risk > 0.1:
            risk_parts.append(f"{result.burnout_risk*100:.0f}% burnout risk")
        if result.financial_instability_risk > 0.1:
            risk_parts.append(f"{result.financial_instability_risk*100:.0f}% financial instability risk")
        if result.high_stress_risk > 0.1:
            risk_parts.append(f"{result.high_stress_risk*100:.0f}% high-stress risk")

        risk_str = ", ".join(risk_parts) if risk_parts else "manageable risks"

        best = result.p90_happiness
        worst = result.p10_happiness
        likely = result.median_happiness

        return (
            f"Based on {result.n_runs:,} simulated scenarios over "
            f"{result.time_horizon_months // 12} years: "
            f"there is a {prob:.0f}% probability of overall life improvement. "
            f"Key risks include {risk_str}. "
            f"Best case happiness index: {best:.2f}, "
            f"worst case: {worst:.2f}, "
            f"most likely: {likely:.2f}."
        )

    def _risk_breakdown(self, result: SimulationResult) -> list[dict]:
        """Detailed risk breakdown."""
        risks = [
            {
                "risk": "Burnout",
                "probability": round(result.burnout_risk * 100, 1),
                "severity": "high" if result.burnout_risk > 0.3 else "moderate" if result.burnout_risk > 0.1 else "low",
                "description": "Risk of reaching critical burnout levels due to sustained high stress and poor recovery.",
            },
            {
                "risk": "Financial Instability",
                "probability": round(result.financial_instability_risk * 100, 1),
                "severity": "high" if result.financial_instability_risk > 0.3 else "moderate" if result.financial_instability_risk > 0.1 else "low",
                "description": "Risk of financial indices dropping below sustainable levels.",
            },
            {
                "risk": "Chronic High Stress",
                "probability": round(result.high_stress_risk * 100, 1),
                "severity": "high" if result.high_stress_risk > 0.3 else "moderate" if result.high_stress_risk > 0.1 else "low",
                "description": "Risk of sustained elevated stress affecting health, relationships, and productivity.",
            },
        ]
        return sorted(risks, key=lambda r: r["probability"], reverse=True)

    def _generate_counterfactuals(
        self, state: UserState, decision: DecisionDelta
    ) -> list[dict]:
        """
        Generate 'what-if' counterfactuals by perturbing the most influential state dimensions.
        """
        # Identify top influential dimensions from result attribution if available
        # For now, we use a robust set of key pivot variables
        pivot_vars = [
            ("liquid_assets", 0.20, "If you had 20% more savings"),
            ("liquid_assets", -0.20, "If you had 20% less savings"),
            ("stress_load", -0.20, "If your baseline stress were much lower"),
            ("skill_breadth", 0.15, "If you had a broader skill set"),
            ("network_strength", 0.25, "If your professional network were significantly stronger"),
        ]

        counterfactuals = []
        for dim, delta, description in pivot_vars:
            current = getattr(state, dim, 0.5)
            perturbed_val = float(np.clip(current + delta, 0.0, 1.0))
            perturbed_state = state.model_copy(update={dim: perturbed_val})

            # Run a focused 1K simulation to see the delta
            cf_result = self.mc_engine.simulate(
                perturbed_state, decision, n_runs=1000, seed=42
            )

            # Only include if it significantly changes the success probability (>2% absolute change)
            if abs(cf_result.success_probability * 100 - state.overall_happiness * 100) > 2:
                counterfactuals.append({
                    "description": description,
                    "variable": dim,
                    "change": delta,
                    "new_success_prob": round(cf_result.success_probability * 100, 1),
                    "new_mean_happiness": round(cf_result.mean_happiness, 3),
                })

        return sorted(counterfactuals, key=lambda x: abs(x["new_success_prob"]), reverse=True)[:3]

    def _compute_shap_values(self, state: UserState, decision: DecisionDelta, result: SimulationResult):
        """
        SHAP (SHapley Additive exPlanations) values represent the contribution 
        of each variable to the final success probability.
        """
        # Placeholder for real kernel SHAP estimation logic
        # In Phase 6, we map the influence factors to SHAP-ready descriptors
        shap_data = []
        for factor in result.top_factors:
            shap_data.append({
                "feature": factor.factor,
                "shap_value": factor.influence if factor.direction == "positive" else -factor.influence,
                "reasoning": f"This variable accounts for {abs(factor.influence)*100:.0f}% of the model variance."
            })
        return shap_data

    def _list_assumptions(
        self, state: UserState, decision: DecisionDelta
    ) -> list[dict]:
        """List key assumptions baked into the simulation."""
        return [
            {
                "assumption": "Decision parameters are approximately correct",
                "confidence": decision.confidence,
                "impact": "high",
                "editable": True,
            },
            {
                "assumption": "Macro-economic conditions remain stable",
                "confidence": 0.6,
                "impact": "high",
                "editable": False,
            },
            {
                "assumption": "No major health events beyond statistical expectation",
                "confidence": 0.9,
                "impact": "medium",
                "editable": False,
            },
            {
                "assumption": "Relationship dynamics remain within normal range",
                "confidence": 0.7,
                "impact": "medium",
                "editable": False,
            },
            {
                "assumption": f"Risk tolerance remains at {state.risk_tolerance:.2f}",
                "confidence": 0.8,
                "impact": "medium",
                "editable": True,
            },
        ]

    def _generate_narrative(
        self,
        state: UserState,
        decision: DecisionDelta,
        result: SimulationResult,
    ) -> str:
        """Generate a 'Future Self' narrative for the most likely scenario."""
        years = result.time_horizon_months // 12
        median_h = result.median_happiness
        initial_h = state.overall_happiness
        direction = "improved" if median_h > initial_h else "declined slightly"
        
        stress_trend = "decreased" if result.stress_p50[-1] < state.stress_load else "increased"
        fin_trend = "strengthened" if result.financial_p50[-1] > state.financial_index else "weakened"

        narrative = (
            f"In the most likely scenario over {years} years after this decision, "
            f"your overall life satisfaction has {direction} "
            f"(from {initial_h:.2f} to {median_h:.2f}). "
            f"Your financial position has {fin_trend}, "
            f"and your stress levels have {stress_trend}. "
        )

        if result.burnout_risk > 0.2:
            narrative += (
                f"However, there is a notable {result.burnout_risk*100:.0f}% chance of burnout, "
                f"suggesting the need for deliberate recovery periods. "
            )

        if result.success_probability > 0.6:
            narrative += (
                "Overall, the trajectory looks favorable with manageable risks."
            )
        elif result.success_probability > 0.4:
            narrative += (
                "The outcome is uncertain — success depends heavily on your assumptions holding true."
            )
        else:
            narrative += (
                "Caution is advised — the simulation suggests more scenarios "
                "lead to decreased life satisfaction than increased."
            )

        return narrative

    def _compute_regret_score(self, result: SimulationResult) -> dict:
        """
        Regret minimization score.
        How much would you regret this decision in the worst case?
        """
        # Regret = how bad the worst case is relative to doing nothing
        worst_case = result.p10_happiness
        expected = result.median_happiness
        
        # Scale 0-100 where 100 = maximum regret
        regret = max(0, (0.5 - worst_case) * 100)  # 0.5 assumed as "do nothing" baseline
        
        return {
            "score": round(min(100, regret), 1),
            "interpretation": (
                "Very low regret risk" if regret < 20
                else "Moderate regret risk" if regret < 50
                else "High regret risk — consider alternatives" if regret < 75
                else "Very high regret risk — proceed with extreme caution"
            ),
            "worst_case_happiness": round(worst_case, 3),
            "expected_happiness": round(expected, 3),
        }
