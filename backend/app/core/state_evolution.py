"""
Antigravity – State Evolution Engine
SDE-inspired state transitions with drift, diffusion, and jump components.
"""

import numpy as np
from app.core.state_model import UserState, DecisionDelta
from app.core.domain_interactions import DomainInteractionEngine


class StateEvolutionEngine:
    """
    Evolves the user state forward in time using a stochastic model:
      dX = μ(X, decision) * dt + σ(X) * dW + J * dN
    
    Discretized per month for simulation.
    """

    def __init__(self):
        self.interaction_engine = DomainInteractionEngine()
        self.dt = 1.0 / 12.0  # 1 month in years

    def evolve_one_step(
        self,
        state: UserState,
        decision: DecisionDelta,
        month: int,
        rng: np.random.Generator,
    ) -> UserState:
        """
        Evolve state by one month.
        
        Args:
            state: Current user state
            decision: Active decision parameters
            month: Current simulation month (from start)
            rng: Random number generator for reproducibility
        """
        arr = state.as_array()  # 23 floats
        n_dims = len(arr)

        # ── 1. Drift: deterministic trend from decision ──────
        drift = self._compute_drift(state, decision, month)

        # ── 2. Diffusion: everyday uncertainty ───────────────
        diffusion = self._compute_diffusion(state, rng, n_dims)

        # ── 3. Jump: rare events ─────────────────────────────
        jump = self._compute_jumps(state, rng, n_dims)

        # ── 4. Domain interactions ───────────────────────────
        interactions = self.interaction_engine.compute_interactions(state)
        interaction_arr = np.zeros(n_dims)
        dim_names = [
            "liquid_assets", "debt_ratio", "income_stability",
            "income_growth_rate", "expense_ratio", "investment_diversity",
            "skill_breadth", "skill_depth", "education_level",
            "network_strength", "career_momentum",
            "physical_health", "mental_health", "sleep_quality",
            "stress_load", "burnout_proximity",
            "relationship_quality", "social_support",
            "family_obligations", "community_integration",
            "risk_tolerance", "time_preference", "adaptability",
        ]
        for i, name in enumerate(dim_names):
            if name in interactions:
                interaction_arr[i] = interactions[name]

        # ── 5. Combine ──────────────────────────────────────
        new_arr = arr + drift * self.dt + diffusion + jump + interaction_arr * self.dt
        new_arr = np.clip(new_arr, 0.0, 1.0)

        return state.from_array(new_arr)

    def _compute_drift(
        self, state: UserState, decision: DecisionDelta, month: int
    ) -> np.ndarray:
        """Deterministic drift from decision + natural aging."""
        delta_arr = decision.as_delta_array()
        # Pad to 23 dimensions (delta has 20, meta traits don't change)
        full_delta = np.zeros(23)
        full_delta[:20] = delta_arr

        # Decision effect ramps in over time_to_effect_months
        if month < decision.time_to_effect_months:
            ramp = month / max(decision.time_to_effect_months, 1)
        else:
            ramp = 1.0

        # Decision effect fades if duration is specified
        if decision.duration_months is not None:
            if month > decision.time_to_effect_months + decision.duration_months:
                ramp = max(0.0, ramp - 0.1)

        drift = full_delta * ramp

        # Natural aging effects (very small per month)
        age_factor = state.age / 100.0
        drift[11] -= 0.001 * age_factor  # physical_health slow decline
        drift[6] += 0.002 * (1 - state.skill_breadth)  # skill_breadth grows slowly
        drift[9] += 0.001  # network slowly grows

        return drift

    def _compute_diffusion(
        self, state: UserState, rng: np.random.Generator, n_dims: int
    ) -> np.ndarray:
        """Brownian motion component — everyday randomness."""
        # Base volatility per dimension
        base_vol = np.array([
            0.015,  # liquid_assets
            0.010,  # debt_ratio
            0.005,  # income_stability
            0.008,  # income_growth_rate
            0.010,  # expense_ratio
            0.005,  # investment_diversity
            0.008,  # skill_breadth
            0.005,  # skill_depth
            0.002,  # education_level (very stable)
            0.008,  # network_strength
            0.010,  # career_momentum
            0.005,  # physical_health
            0.012,  # mental_health (more volatile)
            0.010,  # sleep_quality
            0.015,  # stress_load (most volatile)
            0.010,  # burnout_proximity
            0.008,  # relationship_quality
            0.005,  # social_support
            0.003,  # family_obligations
            0.005,  # community_integration
            0.002,  # risk_tolerance (stable)
            0.002,  # time_preference (stable)
            0.003,  # adaptability
        ])

        noise = rng.normal(0, 1, n_dims)
        return base_vol * noise * np.sqrt(self.dt)

    def _compute_jumps(
        self, state: UserState, rng: np.random.Generator, n_dims: int
    ) -> np.ndarray:
        """
        Jump-diffusion: rare but impactful events.
        Modeled as Poisson-triggered shocks.
        """
        jumps = np.zeros(n_dims)

        # Job loss event: ~2% annual probability
        if rng.random() < 0.02 / 12:
            jumps[0] -= 0.15   # liquid_assets drop
            jumps[2] -= 0.4    # income_stability crash
            jumps[14] += 0.2   # stress spike
            jumps[12] -= 0.1   # mental_health hit

        # Windfall event (bonus, inheritance): ~3% annual
        if rng.random() < 0.03 / 12:
            jumps[0] += 0.1    # liquid_assets boost
            jumps[14] -= 0.05  # stress relief

        # Health crisis: ~1% annual
        if rng.random() < 0.01 / 12:
            jumps[11] -= 0.2   # physical_health
            jumps[14] += 0.15  # stress
            jumps[0] -= 0.1   # medical costs

        # Relationship crisis: ~5% annual
        if rng.random() < 0.05 / 12:
            jumps[16] -= 0.2   # relationship_quality
            jumps[14] += 0.1   # stress
            jumps[12] -= 0.1   # mental_health

        # Career breakthrough: ~5% annual
        if rng.random() < 0.05 / 12:
            jumps[10] += 0.15  # career_momentum
            jumps[3] += 0.05   # income_growth
            jumps[9] += 0.1    # network_strength

        return jumps
