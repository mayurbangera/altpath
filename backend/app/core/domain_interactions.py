"""
Antigravity – Non-Linear Domain Interaction Engine
Models life as interconnected subsystems with feedback loops,
saturation effects, and temporal lags.
"""

import numpy as np
from app.core.state_model import UserState


def sigmoid(x: float, k: float = 10.0, midpoint: float = 0.5) -> float:
    """Smooth sigmoid transition."""
    return 1.0 / (1.0 + np.exp(-k * (x - midpoint)))


def log_saturate(x: float, threshold: float = 1.0) -> float:
    """Logarithmic saturation: diminishing returns past threshold."""
    return np.log1p(x / threshold) / np.log1p(1.0)


def quadratic_optimum(x: float, optimal: float = 0.4) -> float:
    """U-shaped / inverted-U: optimal at a specific point."""
    return 1.0 - ((x - optimal) ** 2) / max(optimal, 1 - optimal) ** 2


# ── Temporal Lag Definitions (in months) ─────────────────────
TEMPORAL_LAGS = {
    ("stress_load", "physical_health"): 3,       # Chronic stress → health: 3 months
    ("stress_load", "mental_health"): 1,          # Stress → mental health: 1 month
    ("stress_load", "relationship_quality"): 2,   # Stress → relationships: 2 months
    ("career_momentum", "income_growth_rate"): 6, # Career → income: 6 months
    ("education_level", "career_momentum"): 12,   # Education → career: 12 months
    ("physical_health", "career_momentum"): 2,    # Health → productivity → career
    ("sleep_quality", "mental_health"): 1,        # Sleep → mental health: 1 month
    ("network_strength", "career_momentum"): 3,   # Network → career: 3 months
}


class DomainInteractionEngine:
    """
    Computes non-linear interactions between life domains.
    Called at each simulation timestep to produce interaction effects.
    """

    def compute_interactions(self, state: UserState) -> dict[str, float]:
        """
        Compute interaction deltas for the current state.
        Returns a dict of dimension -> interaction_delta.
        """
        deltas: dict[str, float] = {}

        # ── Finance → Stress ─────────────────────────────────
        # Poor finances increase stress; very good finances reduce it
        financial_stress = -0.02 * sigmoid(1 - state.financial_index, k=8, midpoint=0.4)
        deltas["stress_load"] = deltas.get("stress_load", 0) + financial_stress

        # ── Stress → Health (diminishing returns on damage) ──
        if state.stress_load > 0.4:
            health_damage = -0.015 * sigmoid(state.stress_load, k=6, midpoint=0.6)
            deltas["physical_health"] = deltas.get("physical_health", 0) + health_damage
            deltas["mental_health"] = deltas.get("mental_health", 0) + health_damage * 1.5

        # ── Stress is mean-reverting ─────────────────────────
        stress_reversion = -0.01 * (state.stress_load - 0.35)  # Reverts toward 0.35
        deltas["stress_load"] = deltas.get("stress_load", 0) + stress_reversion

        # ── Sleep → Mental Health ────────────────────────────
        sleep_effect = 0.01 * (state.sleep_quality - 0.5)
        deltas["mental_health"] = deltas.get("mental_health", 0) + sleep_effect

        # ── Relationships buffer stress ──────────────────────
        if state.relationship_quality > 0.6:
            buffer = -0.005 * (state.relationship_quality ** 1.5)
            deltas["stress_load"] = deltas.get("stress_load", 0) + buffer

        # ── Financial security → Happiness (logarithmic) ────
        happiness_finance = 0.005 * log_saturate(
            state.liquid_assets / max(state.expense_ratio, 0.1),
            threshold=0.8
        )
        # (This is captured in composite indices, so small effect here)

        # ── Career stress U-curve ────────────────────────────
        # Moderate stress helps productivity; too much destroys it
        productivity_from_stress = 0.01 * quadratic_optimum(state.stress_load, optimal=0.35)
        deltas["career_momentum"] = deltas.get("career_momentum", 0) + productivity_from_stress

        # ── Burnout proximity ────────────────────────────────
        if state.stress_load > 0.7 and state.sleep_quality < 0.4:
            burnout_push = 0.03
            deltas["burnout_proximity"] = deltas.get("burnout_proximity", 0) + burnout_push
        elif state.stress_load < 0.4 and state.sleep_quality > 0.6:
            burnout_recovery = -0.02
            deltas["burnout_proximity"] = deltas.get("burnout_proximity", 0) + burnout_recovery

        # ── Burnout → Everything ─────────────────────────────
        if state.burnout_proximity > 0.7:
            burnout_damage = -0.03
            deltas["career_momentum"] = deltas.get("career_momentum", 0) + burnout_damage
            deltas["mental_health"] = deltas.get("mental_health", 0) + burnout_damage
            deltas["relationship_quality"] = deltas.get("relationship_quality", 0) + burnout_damage * 0.5

        # ── Network → Career momentum ───────────────────────
        network_effect = 0.005 * (state.network_strength - 0.3)
        deltas["career_momentum"] = deltas.get("career_momentum", 0) + network_effect

        # ── Family obligations → Stress ──────────────────────
        if state.family_obligations > 0.5:
            family_stress = 0.01 * (state.family_obligations - 0.5)
            deltas["stress_load"] = deltas.get("stress_load", 0) + family_stress

        # ── Skill growth → Career momentum ───────────────────
        skill_effect = 0.005 * (state.skill_depth + state.skill_breadth - 0.8)
        deltas["career_momentum"] = deltas.get("career_momentum", 0) + skill_effect

        return deltas

    def apply_interactions(
        self, state: UserState, interaction_deltas: dict[str, float]
    ) -> UserState:
        """Apply interaction deltas to state, clamping to [0, 1]."""
        updates = {}
        for dim, delta in interaction_deltas.items():
            current = getattr(state, dim, None)
            if current is not None:
                updates[dim] = float(np.clip(current + delta, 0.0, 1.0))
        return state.model_copy(update=updates)
