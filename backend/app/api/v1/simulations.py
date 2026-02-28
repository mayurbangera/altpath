"""
Antigravity – Simulations API
Run Monte Carlo simulations on decisions.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.core.state_model import UserState, DecisionDelta, SimulationResult
from app.simulation.monte_carlo import MonteCarloEngine
from app.simulation.results_store import ResultsStore
import uuid
from app.simulation.ensemble import EnsembleEngine
from app.explainability.explainer import ExplainabilityEngine

router = APIRouter()
ensemble_engine = EnsembleEngine()
explain_engine = ExplainabilityEngine()


class SimulationRequest(BaseModel):
    """Request to run a simulation."""
    state: UserState
    decision: DecisionDelta
    n_runs: int = Field(10000, ge=100, le=100000)
    time_horizon_years: int = Field(5, ge=1, le=20)
    seed: Optional[int] = None
    include_explanation: bool = True
    include_counterfactuals: bool = False


class SimulationResponse(BaseModel):
    """Full simulation result with ensemble metadata and optional explanation."""
    result: SimulationResult
    ensemble: dict
    explanation: Optional[dict] = None


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(req: SimulationRequest):
    """
    Run an ensemble simulation for a given state + decision.
    Combines MC (Path Dynamics), Bayesian (Causal), and ABM (Social).
    """
    ensemble_results = ensemble_engine.simulate_ensemble(
        state=req.state,
        decision=req.decision,
        n_runs=req.n_runs,
        months=req.time_horizon_years * 12
    )
    
    result = ensemble_results["mc_result"]
    # Adjust success probability in the main result object based on ensemble
    result.success_probability = ensemble_results["final_success_probability"]
    
    ensemble_meta = {
        "disagreement": ensemble_results["disagreement"],
        "weights": ensemble_results["ensemble_weights"]
    }

    explanation = None
    if req.include_explanation:
        explanation = explain_engine.generate_explanation(
            state=req.state,
            decision=req.decision,
            result=result,
        )
        # Only include counterfactuals if explicitly requested (expensive)
        if not req.include_counterfactuals:
            explanation["counterfactuals"] = []

    # Assign ID and save to store
    sim_id = str(uuid.uuid4())
    ResultsStore.save(sim_id, result)

    return SimulationResponse(
        result=result, 
        ensemble=ensemble_meta, 
        explanation=explanation
    )


class CompareRequest(BaseModel):
    """Compare multiple decisions side by side."""
    state: UserState
    decisions: list[DecisionDelta] = Field(..., min_length=2, max_length=4)
    n_runs: int = Field(5000, ge=100, le=50000)
    time_horizon_years: int = Field(5, ge=1, le=20)


class CompareResponse(BaseModel):
    """Side-by-side comparison of multiple decisions."""
    results: list[SimulationResponse]
    recommendation: dict


@router.post("/compare", response_model=CompareResponse)
async def compare_decisions(req: CompareRequest):
    """
    Run simulations for multiple decisions and compare outcomes.
    """
    results = []
    for decision in req.decisions:
        ensemble_res = ensemble_engine.simulate_ensemble(
            state=req.state,
            decision=decision,
            n_runs=req.n_runs,
            months=req.time_horizon_years * 12,
        )
        sim_result = ensemble_res["mc_result"]
        sim_result.success_probability = ensemble_res["final_success_probability"]
        
        explanation = explain_engine.generate_explanation(
            state=req.state, decision=decision, result=sim_result,
        )
        explanation["counterfactuals"] = []  # Skip for comparison
        results.append(SimulationResponse(
            result=sim_result, 
            ensemble={
                "disagreement": ensemble_res["disagreement"],
                "weights": ensemble_res["ensemble_weights"]
            },
            explanation=explanation
        ))

    # Determine recommendation
    best_idx = max(range(len(results)), key=lambda i: results[i].result.success_probability)
    safest_idx = min(range(len(results)), key=lambda i: max(
        results[i].result.burnout_risk,
        results[i].result.financial_instability_risk,
        results[i].result.high_stress_risk,
    ))

    recommendation = {
        "highest_success": {
            "decision": req.decisions[best_idx].decision_text,
            "probability": round(results[best_idx].result.success_probability * 100, 1),
        },
        "safest": {
            "decision": req.decisions[safest_idx].decision_text,
            "max_risk": round(max(
                results[safest_idx].result.burnout_risk,
                results[safest_idx].result.financial_instability_risk,
                results[safest_idx].result.high_stress_risk,
            ) * 100, 1),
        },
        "note": "The 'best' decision depends on your risk tolerance and priorities.",
    }

    return CompareResponse(results=results, recommendation=recommendation)
