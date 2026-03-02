"""
Antigravity – Advanced Analysis API
Causal graph, scenario branching, and stress testing endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.core.state_model import UserState, DecisionDelta
from app.simulation.bayesian_network import BayesianCausalGraph
from app.simulation.scenario_tree import ScenarioBranchingEngine, ScenarioTree
from app.core.regional_calibration import RegionalCalibrator

router = APIRouter()
causal_graph = BayesianCausalGraph()
branching_engine = ScenarioBranchingEngine()
calibrator = RegionalCalibrator()


# ── Causal Analysis ──────────────────────────────────────────

class CausalPathRequest(BaseModel):
    source: str
    target: str
    state: UserState


class InterventionRequest(BaseModel):
    state: UserState
    interventions: dict[str, float] = Field(..., description="Variable name -> new value")
    propagation_months: int = Field(12, ge=1, le=60)


class ScenarioRequest(BaseModel):
    state: UserState
    decision: DecisionDelta


@router.post("/causal/paths")
async def get_causal_paths(req: CausalPathRequest):
    """Find all causal paths between two life dimensions."""
    result = causal_graph.get_total_causal_effect(req.source, req.target, req.state)
    return result


@router.post("/causal/intervene")
async def intervene(req: InterventionRequest):
    """
    Do-calculus style intervention: set a variable and see downstream effects.
    """
    effects = causal_graph.intervene(req.state, req.interventions, req.propagation_months)
    return {
        "interventions": req.interventions,
        "propagation_months": req.propagation_months,
        "downstream_effects": effects,
    }


@router.post("/causal/sensitivity")
async def sensitivity_analysis(req: BaseModel):
    """Rank variables by their causal influence across the network."""
    # Use default state for analysis if not provided
    state = UserState()
    analysis = causal_graph.get_sensitivity_analysis(state)
    return {"sensitivity_ranking": analysis}


@router.post("/causal/flow")
async def get_causal_flow(req: ScenarioRequest):
    """
    Returns a directed graph of domains affected by the decision.
    Uses the new subgraph extraction logic.
    """
    delta_dict = req.decision.as_delta_dict()
    starting_vars = [k for k, v in delta_dict.items() if v is not None and v != 0]
    
    if not starting_vars:
        # Default to overall clusters if no decision delta
        starting_vars = ["liquid_assets", "career_momentum", "physical_health", "relationship_quality"]

    graph_data = causal_graph.get_affected_subgraph(starting_vars)
    return graph_data


@router.post("/sensitivity/tornado")
async def get_tornado_analysis(req: ScenarioRequest):
    """
    Tornado Diagram logic: perturb each decision parameter by ±20% 
    and measure the impact on Success Probability.
    """
    from app.simulation.monte_carlo import MonteCarloEngine
    mc = MonteCarloEngine()
    
    base_results = mc.simulate(req.state, req.decision, n_runs=1000, time_horizon_months=60)
    base_success = base_results.success_probability
    
    delta_dict = req.decision.as_delta_dict()
    impacts = []
    
    # Only test variables that have a non-zero effect in the decision
    test_vars = [k for k, v in delta_dict.items() if v is not None and v != 0 and k not in ["decision_text", "decision_type"]]
    
    for var in test_vars:
        original_val = delta_dict[var]
        
        # Upper perturbation (+20%)
        up_decision = req.decision.model_copy(update={var: original_val * 1.2})
        up_res = mc.simulate(req.state, up_decision, n_runs=500, time_horizon_months=60)
        
        # Lower perturbation (-20%)
        down_decision = req.decision.model_copy(update={var: original_val * 0.8})
        down_res = mc.simulate(req.state, down_decision, n_runs=500, time_horizon_months=60)
        
        impacts.append({
            "variable": var.replace("_", " ").title(),
            "low": round(down_res.success_probability - base_success, 4),
            "high": round(up_res.success_probability - base_success, 4),
            "total_swing": abs(up_res.success_probability - down_res.success_probability)
        })
        
    return sorted(impacts, key=lambda x: x["total_swing"], reverse=True)


@router.get("/causal/graph")
async def get_graph():
    """Get the full causal graph structure for visualization."""
    return causal_graph.get_graph_summary()


# ── Scenario Branching ───────────────────────────────────────


@router.post("/scenarios/tree", response_model=ScenarioTree)
async def generate_scenario_tree(req: ScenarioRequest):
    """Generate a branching scenario tree for a decision."""
    tree = branching_engine.generate_tree(req.state, req.decision)
    return tree


# ── Stress Testing ───────────────────────────────────────────

class StressTestRequest(BaseModel):
    state: UserState
    decision: DecisionDelta
    black_swan: str = Field(..., description="Type: recession, pandemic, health_crisis, market_crash, personal_crisis")
    severity: float = Field(0.5, ge=0.0, le=1.0, description="Severity 0=mild, 1=extreme")


BLACK_SWAN_EFFECTS = {
    "recession": {
        "liquid_assets": -0.25,
        "income_stability": -0.3,
        "income_growth_rate": -0.15,
        "expense_ratio": 0.1,
        "career_momentum": -0.15,
        "stress_load": 0.25,
        "investment_diversity": -0.2,
    },
    "pandemic": {
        "physical_health": -0.15,
        "mental_health": -0.2,
        "sleep_quality": -0.1,
        "stress_load": 0.3,
        "social_support": -0.25,
        "community_integration": -0.3,
        "income_stability": -0.15,
    },
    "health_crisis": {
        "physical_health": -0.35,
        "mental_health": -0.2,
        "stress_load": 0.3,
        "liquid_assets": -0.2,
        "career_momentum": -0.2,
        "burnout_proximity": 0.25,
        "relationship_quality": -0.1,
    },
    "market_crash": {
        "liquid_assets": -0.35,
        "investment_diversity": -0.4,
        "income_growth_rate": -0.1,
        "stress_load": 0.2,
        "expense_ratio": 0.05,
    },
    "personal_crisis": {
        "mental_health": -0.3,
        "relationship_quality": -0.35,
        "stress_load": 0.35,
        "sleep_quality": -0.2,
        "burnout_proximity": 0.2,
        "career_momentum": -0.1,
        "social_support": -0.15,
    },
}


@router.post("/stress-test")
async def run_stress_test(req: StressTestRequest):
    """
    Apply a black swan event to the simulation and compare outcomes.
    Shows how robust a decision is under extreme scenarios.
    """
    from app.simulation.monte_carlo import MonteCarloEngine
    mc = MonteCarloEngine()

    # Normal simulation
    normal_result = mc.simulate(req.state, req.decision, n_runs=2000, time_horizon_months=60)

    # Apply black swan shock to initial state
    effects = BLACK_SWAN_EFFECTS.get(req.black_swan, {})
    stressed_updates = {}
    for dim, delta in effects.items():
        current = getattr(req.state, dim, 0.5)
        stressed_updates[dim] = float(max(0.0, min(1.0, current + delta * req.severity)))
    
    stressed_state = req.state.model_copy(update=stressed_updates)
    
    # Stressed simulation
    stressed_result = mc.simulate(stressed_state, req.decision, n_runs=2000, time_horizon_months=60)

    # Compute antifragility score
    normal_success = normal_result.success_probability
    stressed_success = stressed_result.success_probability
    resilience = stressed_success / max(normal_success, 0.01)
    antifragility = "antifragile" if resilience > 1.0 else "resilient" if resilience > 0.7 else "fragile" if resilience > 0.4 else "very_fragile"

    return {
        "black_swan": req.black_swan,
        "severity": req.severity,
        "normal": {
            "success_probability": round(normal_success, 3),
            "mean_happiness": round(normal_result.mean_happiness, 3),
            "burnout_risk": round(normal_result.burnout_risk, 3),
        },
        "stressed": {
            "success_probability": round(stressed_success, 3),
            "mean_happiness": round(stressed_result.mean_happiness, 3),
            "burnout_risk": round(stressed_result.burnout_risk, 3),
        },
        "impact": {
            "success_drop": round((normal_success - stressed_success) * 100, 1),
            "happiness_drop": round((normal_result.mean_happiness - stressed_result.mean_happiness), 3),
            "burnout_increase": round((stressed_result.burnout_risk - normal_result.burnout_risk) * 100, 1),
        },
        "resilience_score": round(resilience * 100, 1),
        "antifragility": antifragility,
        "recommendation": (
            "This decision is robust under this stress scenario." if resilience > 0.7
            else "This decision is moderately fragile — consider building more runway or safety nets."
            if resilience > 0.4
            else "This decision is very fragile under this scenario — strongly consider alternatives or hedging strategies."
        ),
    }


# ── Regional Info ────────────────────────────────────────────

@router.get("/calibration/{country_code}")
async def get_regional_profile(country_code: str):
    """Get the regional calibration profile for a country."""
    profile = calibrator.get_profile(country_code)
    return profile.model_dump()
