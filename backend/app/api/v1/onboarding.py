"""
Antigravity – Onboarding API
Collect user profile data and generate initial state vector.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.core.state_model import UserState, BigFiveVector

router = APIRouter()


# ── Request / Response Schemas ───────────────────────────────
class OnboardingRequest(BaseModel):
    """User onboarding form data."""
    # Demographics
    age: int = Field(..., ge=16, le=100)
    country: str = Field(..., max_length=3, description="ISO 3166-1 alpha-2/3")
    
    # Financial
    annual_income: float = Field(..., ge=0, description="Annual income in local currency")
    monthly_expenses: float = Field(..., ge=0)
    total_savings: float = Field(0, ge=0)
    total_debt: float = Field(0, ge=0)
    income_type: str = Field("salaried", description="salaried, freelance, business, gig")
    
    # Career
    industry: str = Field(..., description="Current industry")
    years_experience: int = Field(0, ge=0)
    education: str = Field("bachelors", description="high_school, bachelors, masters, phd, other")
    num_skills: int = Field(3, ge=1, description="Number of marketable skills")
    
    # Health
    exercise_frequency: str = Field("moderate", description="none, light, moderate, heavy")
    sleep_hours: float = Field(7.0, ge=3, le=12)
    chronic_conditions: bool = Field(False)
    
    # Social
    relationship_status: str = Field("single", description="single, dating, married, divorced")
    num_dependents: int = Field(0, ge=0)
    social_circle_size: str = Field("medium", description="small, medium, large")
    
    # Personality (optional Big Five mini quiz)
    personality: Optional[BigFiveVector] = None
    
    # Goals
    primary_goal: str = Field("", description="User's primary life goal")
    risk_tolerance: str = Field("moderate", description="very_low, low, moderate, high, very_high")
    time_horizon_years: int = Field(5, ge=1, le=20)


class OnboardingResponse(BaseModel):
    """Generated initial state vector + summary."""
    state: UserState
    summary: dict
    next_step: str = "Enter a decision to simulate"


# ── Conversion Logic ─────────────────────────────────────────
def _income_type_to_stability(income_type: str) -> float:
    return {"salaried": 0.8, "freelance": 0.4, "business": 0.5, "gig": 0.25}.get(income_type, 0.5)

def _education_to_level(edu: str) -> float:
    return {"high_school": 0.3, "bachelors": 0.5, "masters": 0.7, "phd": 0.9, "other": 0.4}.get(edu, 0.5)

def _exercise_to_health(freq: str) -> float:
    return {"none": 0.4, "light": 0.55, "moderate": 0.7, "heavy": 0.85}.get(freq, 0.6)

def _risk_str_to_float(risk: str) -> float:
    return {"very_low": 0.15, "low": 0.3, "moderate": 0.5, "high": 0.7, "very_high": 0.85}.get(risk, 0.5)

def _social_to_support(size: str) -> float:
    return {"small": 0.3, "medium": 0.5, "large": 0.75}.get(size, 0.5)

def _relationship_to_quality(status: str) -> float:
    return {"single": 0.4, "dating": 0.55, "married": 0.7, "divorced": 0.35}.get(status, 0.5)


def build_initial_state(req: OnboardingRequest) -> UserState:
    """Convert onboarding form data to 24-dim state vector."""
    
    # Financial cluster
    income = max(req.annual_income, 1)
    debt_ratio = min(req.total_debt / income, 1.0) if income > 0 else 0.5
    expense_ratio = min((req.monthly_expenses * 12) / income, 1.0)
    savings_months = req.total_savings / max(req.monthly_expenses, 1)
    liquid_assets = min(savings_months / 24, 1.0)  # Norm: 24 months = 1.0

    # Health cluster
    sleep_quality = min(max((req.sleep_hours - 4) / 5, 0), 1.0)  # 4h=0, 9h=1
    physical_health = _exercise_to_health(req.exercise_frequency)
    if req.chronic_conditions:
        physical_health *= 0.7

    # Career cluster
    skill_depth = min(req.years_experience / 15, 1.0)
    skill_breadth = min(req.num_skills / 8, 1.0)

    return UserState(
        # Financial
        liquid_assets=round(liquid_assets, 2),
        debt_ratio=round(debt_ratio, 2),
        income_stability=_income_type_to_stability(req.income_type),
        income_growth_rate=0.05,
        expense_ratio=round(expense_ratio, 2),
        investment_diversity=0.2,
        # Human Capital
        skill_breadth=round(skill_breadth, 2),
        skill_depth=round(skill_depth, 2),
        education_level=_education_to_level(req.education),
        network_strength=min(req.years_experience / 20, 0.8),
        career_momentum=0.5,
        # Wellbeing
        physical_health=round(physical_health, 2),
        mental_health=0.7,
        sleep_quality=round(sleep_quality, 2),
        stress_load=0.3,
        burnout_proximity=0.15,
        # Social
        relationship_quality=_relationship_to_quality(req.relationship_status),
        social_support=_social_to_support(req.social_circle_size),
        family_obligations=min(req.num_dependents / 4, 1.0),
        community_integration=0.4,
        # Meta
        risk_tolerance=_risk_str_to_float(req.risk_tolerance),
        time_preference=0.5,
        adaptability=0.5,
        personality=req.personality or BigFiveVector(),
        # Metadata
        age=req.age,
        country=req.country.upper(),
    )


# ── API Endpoints ────────────────────────────────────────────
@router.post("/", response_model=OnboardingResponse)
async def onboard_user(req: OnboardingRequest):
    """
    Process user onboarding and generate initial state vector.
    """
    state = build_initial_state(req)

    summary = {
        "financial_index": round(state.financial_index, 3),
        "wellbeing_index": round(state.wellbeing_index, 3),
        "career_index": round(state.career_index, 3),
        "social_index": round(state.social_index, 3),
        "overall_happiness": round(state.overall_happiness, 3),
    }

    return OnboardingResponse(
        state=state,
        summary=summary,
        next_step="Enter a decision to simulate using /api/v1/decisions/translate",
    )
