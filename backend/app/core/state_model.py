"""
Antigravity – Core State Model
24-dimensional hierarchical state vector representing a user's life state.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import numpy as np
from pydantic import BaseModel, Field


# ── Big Five Personality Model ───────────────────────────────
class BigFiveVector(BaseModel):
    """OCEAN personality model (0.0 – 1.0 each)."""
    openness: float = Field(0.5, ge=0.0, le=1.0)
    conscientiousness: float = Field(0.5, ge=0.0, le=1.0)
    extraversion: float = Field(0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(0.5, ge=0.0, le=1.0)
    neuroticism: float = Field(0.5, ge=0.0, le=1.0)

    def as_array(self) -> np.ndarray:
        return np.array([
            self.openness, self.conscientiousness,
            self.extraversion, self.agreeableness, self.neuroticism
        ])


# ── 24-Dimension User State ─────────────────────────────────
class UserState(BaseModel):
    """
    Complete life-state vector with 24 observable dimensions
    grouped into 5 clusters, plus meta traits.
    All indices are normalized 0.0–1.0 unless stated otherwise.
    """

    # ── Financial Cluster ────────────────────────────────────
    liquid_assets: float = Field(0.3, description="Normalized liquid assets")
    debt_ratio: float = Field(0.2, description="Debt-to-income ratio (0=none, 1=extreme)")
    income_stability: float = Field(0.7, description="0=gig/volatile, 1=tenured/stable")
    income_growth_rate: float = Field(0.05, description="Annual growth rate")
    expense_ratio: float = Field(0.6, description="Monthly expenses / income")
    investment_diversity: float = Field(0.2, description="Portfolio diversification (Herfindahl)")

    # ── Human Capital Cluster ────────────────────────────────
    skill_breadth: float = Field(0.4, description="Number of marketable skills (norm.)")
    skill_depth: float = Field(0.5, description="Expertise in primary domain")
    education_level: float = Field(0.5, description="Credential value (norm.)")
    network_strength: float = Field(0.3, description="Professional network quality")
    career_momentum: float = Field(0.5, description="Career trajectory derivative")

    # ── Wellbeing Cluster ────────────────────────────────────
    physical_health: float = Field(0.7, description="Composite health score")
    mental_health: float = Field(0.7, description="Inverse anxiety/depression")
    sleep_quality: float = Field(0.6, description="Sleep efficiency")
    stress_load: float = Field(0.3, description="Allostatic load proxy")
    burnout_proximity: float = Field(0.2, description="Distance to burnout (0=far, 1=burning)")

    # ── Social Cluster ───────────────────────────────────────
    relationship_quality: float = Field(0.6, description="Primary relationship health")
    social_support: float = Field(0.5, description="Support network breadth")
    family_obligations: float = Field(0.3, description="Dependents + care duties")
    community_integration: float = Field(0.4, description="Belonging index")

    # ── Meta Cluster ─────────────────────────────────────────
    risk_tolerance: float = Field(0.5, description="From psychometric assessment")
    time_preference: float = Field(0.5, description="Discount rate / patience")
    adaptability: float = Field(0.5, description="Change resilience")
    personality: BigFiveVector = Field(default_factory=BigFiveVector)

    # ── Metadata ─────────────────────────────────────────────
    age: int = Field(25, ge=16, le=100)
    country: str = Field("US", max_length=3)

    def as_array(self) -> np.ndarray:
        """Convert numeric dimensions to a flat numpy array (23 floats)."""
        return np.array([
            self.liquid_assets, self.debt_ratio, self.income_stability,
            self.income_growth_rate, self.expense_ratio, self.investment_diversity,
            self.skill_breadth, self.skill_depth, self.education_level,
            self.network_strength, self.career_momentum,
            self.physical_health, self.mental_health, self.sleep_quality,
            self.stress_load, self.burnout_proximity,
            self.relationship_quality, self.social_support,
            self.family_obligations, self.community_integration,
            self.risk_tolerance, self.time_preference, self.adaptability,
        ])

    def from_array(self, arr: np.ndarray) -> "UserState":
        """Reconstruct state from flat array (personality unchanged)."""
        keys = [
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
        updates = {k: float(np.clip(v, 0.0, 1.0)) for k, v in zip(keys, arr)}
        return self.model_copy(update=updates)

    @property
    def financial_index(self) -> float:
        return (
            self.liquid_assets * 0.25
            + (1 - self.debt_ratio) * 0.25
            + self.income_stability * 0.2
            + self.income_growth_rate * 0.15
            + (1 - self.expense_ratio) * 0.15
        )

    @property
    def wellbeing_index(self) -> float:
        return (
            self.physical_health * 0.25
            + self.mental_health * 0.25
            + self.sleep_quality * 0.15
            + (1 - self.stress_load) * 0.2
            + (1 - self.burnout_proximity) * 0.15
        )

    @property
    def career_index(self) -> float:
        return (
            self.skill_breadth * 0.15
            + self.skill_depth * 0.25
            + self.education_level * 0.15
            + self.network_strength * 0.2
            + self.career_momentum * 0.25
        )

    @property
    def social_index(self) -> float:
        return (
            self.relationship_quality * 0.35
            + self.social_support * 0.3
            + self.community_integration * 0.2
            + (1 - self.family_obligations) * 0.15
        )

    @property
    def overall_happiness(self) -> float:
        """Weighted composite happiness score."""
        return (
            self.financial_index * 0.20
            + self.wellbeing_index * 0.30
            + self.career_index * 0.20
            + self.social_index * 0.30
        )


# ── Decision Delta ───────────────────────────────────────────
class DecisionDelta(BaseModel):
    """
    Structured representation of how a decision changes the state vector.
    Each field is a delta (positive = increase, negative = decrease).
    None means no effect on that dimension.
    """
    decision_text: str
    decision_type: str = "general"
    confidence: float = 0.5

    # Deltas per dimension (None = no change)
    liquid_assets: Optional[float] = None
    debt_ratio: Optional[float] = None
    income_stability: Optional[float] = None
    income_growth_rate: Optional[float] = None
    expense_ratio: Optional[float] = None
    investment_diversity: Optional[float] = None
    skill_breadth: Optional[float] = None
    skill_depth: Optional[float] = None
    education_level: Optional[float] = None
    network_strength: Optional[float] = None
    career_momentum: Optional[float] = None
    physical_health: Optional[float] = None
    mental_health: Optional[float] = None
    sleep_quality: Optional[float] = None
    stress_load: Optional[float] = None
    burnout_proximity: Optional[float] = None
    relationship_quality: Optional[float] = None
    social_support: Optional[float] = None
    family_obligations: Optional[float] = None
    community_integration: Optional[float] = None

    # Temporal parameters
    time_to_effect_months: int = 1
    duration_months: Optional[int] = None  # None = permanent
    
    # Uncertainty in the delta itself
    delta_uncertainty: float = 0.1

    def as_delta_array(self) -> np.ndarray:
        """Convert to delta array (0.0 for None values)."""
        vals = [
            self.liquid_assets, self.debt_ratio, self.income_stability,
            self.income_growth_rate, self.expense_ratio, self.investment_diversity,
            self.skill_breadth, self.skill_depth, self.education_level,
            self.network_strength, self.career_momentum,
            self.physical_health, self.mental_health, self.sleep_quality,
            self.stress_load, self.burnout_proximity,
            self.relationship_quality, self.social_support,
            self.family_obligations, self.community_integration,
        ]
        return np.array([v if v is not None else 0.0 for v in vals])


# ── Simulation Result ────────────────────────────────────────
class SimulationTimeStep(BaseModel):
    """State at a single point in time."""
    month: int
    state: UserState
    financial_index: float
    wellbeing_index: float
    career_index: float
    social_index: float
    happiness: float


class SimulationPath(BaseModel):
    """A single Monte Carlo simulation path."""
    path_id: int
    timesteps: list[SimulationTimeStep]


class SimulationResult(BaseModel):
    """Aggregate result from Monte Carlo ensemble."""
    n_runs: int
    time_horizon_months: int
    decision: DecisionDelta

    # Summary statistics at final timestep
    success_probability: float
    mean_happiness: float
    median_happiness: float
    p10_happiness: float
    p90_happiness: float

    mean_financial_index: float
    mean_wellbeing_index: float
    mean_career_index: float
    mean_social_index: float

    # Risk metrics
    burnout_risk: float
    financial_instability_risk: float
    high_stress_risk: float

    # Time-series of percentile bands (for visualization)
    timeline_months: list[int]
    happiness_p10: list[float]
    happiness_p25: list[float]
    happiness_p50: list[float]
    happiness_p75: list[float]
    happiness_p90: list[float]

    financial_p10: list[float]
    financial_p50: list[float]
    financial_p90: list[float]

    stress_p10: list[float]
    stress_p50: list[float]
    stress_p90: list[float]

    # Top influential factors
    top_factors: list[dict]

    # Counterfactuals
    counterfactuals: list[dict] = []
