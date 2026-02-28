"""
Antigravity – Simulation Ensemble Engine
Combines Monte Carlo, Bayesian, and Agent-Based results.
"""
import numpy as np
from typing import Dict, Any, Optional
from app.core.state_model import UserState, DecisionDelta, SimulationResult
from app.simulation.monte_carlo import MonteCarloEngine
from app.simulation.bayesian_network import BayesianCausalGraph
from app.simulation.agent_based import AgentBasedModel

class EnsembleEngine:
    """
    Combines three independent simulation approaches:
    1. Monte Carlo (SDE Path Dynamics) - Weight 0.50
    2. Bayesian Network (Causal Constraints) - Weight 0.30
    3. Agent-Based Model (Social Dynamics) - Weight 0.20
    """

    def __init__(self):
        self.mc_engine = MonteCarloEngine()
        self.causal_graph = BayesianCausalGraph()
        self.abm_engine = AgentBasedModel()

    def simulate_ensemble(
        self,
        state: UserState,
        decision: DecisionDelta,
        n_runs: int = 5000,
        months: int = 60
    ) -> Dict[str, Any]:
        """Runs the ensemble and detects model disagreement."""
        
        # 1. Run Monte Carlo (Base)
        mc_result = self.mc_engine.simulate(state, decision, n_runs=n_runs, time_horizon_months=months)
        
        # 2. Run Bayesian Intervention (Causal)
        causal_impact = self.causal_graph.intervene(state, decision.as_delta_dict(), months=months)
        
        # 3. Run Agent-Based Model (Social)
        abm_impact = self.abm_engine.simulate_social_impact(state, decision, months=months)
        
        # 4. Integrate Causal and Social into ensemble metrics
        # We adjust the success probability base on the other two models' alignment
        causal_success_modifier = np.mean(list(causal_impact.values())) if causal_impact else 0
        abm_success_modifier = (abm_impact["happiness"][-1] - state.overall_happiness)
        
        # Weighting
        final_success_prob = (
            mc_result.success_probability * 0.5 +
            np.clip(mc_result.success_probability + causal_success_modifier, 0, 1) * 0.3 +
            np.clip(mc_result.success_probability + abm_success_modifier, 0, 1) * 0.2
        )
        
        # Detect Model Disagreement
        # If the gap between highest and lowest prediction is > 20%
        preds = [
            mc_result.success_probability,
            mc_result.success_probability + causal_success_modifier,
            mc_result.success_probability + abm_success_modifier
        ]
        disagreement_score = np.max(preds) - np.min(preds)
        high_disagreement = disagreement_score > 0.20
        
        return {
            "mc_result": mc_result,
            "final_success_probability": round(final_success_prob, 4),
            "disagreement": {
                "is_significant": bool(high_disagreement),
                "score": round(float(disagreement_score), 4),
                "details": "Models show diverging outcomes due to conflicting causal vs social dynamics." if high_disagreement else "Models are in broad agreement."
            },
            "ensemble_weights": {"mc": 0.5, "causal": 0.3, "abm": 0.2}
        }
