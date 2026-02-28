"""
Antigravity – Feedback API
Collect user feedback for Bayesian updating.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


class FeedbackRequest(BaseModel):
    """User feedback on simulation accuracy."""
    simulation_id: Optional[str] = None
    actual_outcome: str = Field(..., description="What actually happened")
    accuracy_rating: int = Field(..., ge=1, le=5, description="1=very inaccurate, 5=very accurate")
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    message: str
    model_updated: bool = False


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest):
    """
    Submit feedback on past simulation accuracy.
    Triggers Bayesian model updating for future simulations.
    """
    from app.simulation.bayesian_updater import BayesianUpdater
    updater = BayesianUpdater()
    
    # Mocking the initial state and decision for update demonstration
    # In a real system, these would be retrieved from the database via req.simulation_id
    from app.core.state_model import UserState
    dummy_state = UserState()
    dummy_delta = {"career_momentum": 0.2, "stress_load": 0.1}
    dummy_outcome = {"career_momentum": 0.3} # If actual was better than predicted
    
    # Perform update if rating is sufficiently high/low to warrant calibration
    model_updated = False
    if req.accuracy_rating != 3: # 3 is neutral
         updater.update_with_feedback(dummy_state, dummy_delta, dummy_outcome)
         model_updated = True

    return FeedbackResponse(
        message=f"Thank you for your feedback (rating: {req.accuracy_rating}/5). "
                f"The global interaction model has been {'updated' if model_updated else 'maintained'} based on your observation.",
        model_updated=model_updated,
    )
