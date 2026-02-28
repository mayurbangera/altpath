"""
Antigravity – Decisions API
Translate natural language decisions into structured parameters.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.state_model import DecisionDelta
from app.nlp.decision_translator import DecisionTranslator
from app.nlp.adaptive_questioning import AdaptiveQuestioningSystem

router = APIRouter()
translator = DecisionTranslator()
questioner = AdaptiveQuestioningSystem()


class DecisionRequest(BaseModel):
    """Natural language decision input."""
    text: str = Field(..., min_length=5, description="Decision to evaluate")


class DecisionResponse(BaseModel):
    """Structured decision translation result."""
    original_text: str
    delta: DecisionDelta
    clarification_needed: list[str] = []


@router.post("/translate", response_model=DecisionResponse)
async def translate_decision(req: DecisionRequest):
    """
    Translate a natural language decision into structured state vector changes.
    """
    delta = translator.translate(req.text)
    
    # Generate clarification questions if confidence is not extremely high
    clarifications = []
    if delta.confidence < 0.8:
        # Re-run intent and entities just for the questioner API (cached in reality)
        intent = translator.intent_classifier.classify(req.text)
        entities = translator.entity_extractor.extract(req.text)
        clarifications = questioner.generate_questions(intent, entities)

    return DecisionResponse(
        original_text=req.text,
        delta=delta,
        clarification_needed=clarifications,
    )
