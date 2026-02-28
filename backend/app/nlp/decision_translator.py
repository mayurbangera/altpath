"""
Antigravity – NLP Decision Translation Pipeline
Converts natural language decisions into structured parameter changes.
Uses rule-based + keyword matching (with Ollama/LLM upgrade path).
"""

import re
import logging
from typing import Optional
from app.core.state_model import DecisionDelta
from app.nlp.intent_classifier import IntentClassifier
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.parameter_mapper import ParameterMapper
from app.nlp.confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


# ── Decision Templates (Rule-Based MVP) ──────────────────────
DECISION_TEMPLATES = {
    "quit_job_startup": {
        "keywords": ["quit job", "start business", "startup", "entrepreneurship", "leave job start"],
        "type": "career_transition",
        "deltas": {
            "liquid_assets": -0.15,
            "income_stability": -0.4,
            "income_growth_rate": 0.1,
            "expense_ratio": 0.15,
            "skill_breadth": 0.2,
            "career_momentum": 0.1,
            "stress_load": 0.2,
            "burnout_proximity": 0.1,
            "network_strength": 0.1,
            "relationship_quality": -0.05,
        },
        "time_to_effect": 3,
        "confidence": 0.75,
    },
    "higher_education": {
        "keywords": ["masters", "mba", "phd", "higher studies", "graduate school", "university abroad"],
        "type": "education",
        "deltas": {
            "liquid_assets": -0.2,
            "debt_ratio": 0.15,
            "income_stability": -0.3,
            "education_level": 0.2,
            "skill_depth": 0.15,
            "skill_breadth": 0.1,
            "network_strength": 0.15,
            "stress_load": 0.15,
            "career_momentum": -0.1,  # Short-term dip
            "community_integration": -0.1,
        },
        "time_to_effect": 6,
        "confidence": 0.70,
    },
    "relocation": {
        "keywords": ["move to", "relocate", "migrate", "immigration", "move abroad"],
        "type": "relocation",
        "deltas": {
            "liquid_assets": -0.1,
            "income_stability": -0.15,
            "stress_load": 0.2,
            "community_integration": -0.3,
            "social_support": -0.2,
            "relationship_quality": -0.1,
            "network_strength": -0.1,
            "career_momentum": 0.05,
            "adaptability": 0.1,
        },
        "time_to_effect": 6,
        "confidence": 0.65,
    },
    "career_switch": {
        "keywords": ["switch career", "change field", "new industry", "career change", "pivot"],
        "type": "career_transition",
        "deltas": {
            "income_stability": -0.2,
            "income_growth_rate": -0.05,
            "skill_breadth": 0.15,
            "skill_depth": -0.2,
            "career_momentum": -0.15,
            "stress_load": 0.15,
            "network_strength": -0.1,
        },
        "time_to_effect": 6,
        "confidence": 0.70,
    },
    "marriage": {
        "keywords": ["get married", "marry", "wedding", "tie the knot"],
        "type": "relationship",
        "deltas": {
            "liquid_assets": -0.1,
            "relationship_quality": 0.15,
            "social_support": 0.1,
            "stress_load": 0.05,
            "community_integration": 0.1,
            "family_obligations": 0.1,
        },
        "time_to_effect": 1,
        "confidence": 0.60,
    },
    "have_child": {
        "keywords": ["have a baby", "have child", "start family", "become parent", "having kids"],
        "type": "family",
        "deltas": {
            "liquid_assets": -0.15,
            "expense_ratio": 0.2,
            "stress_load": 0.2,
            "sleep_quality": -0.3,
            "family_obligations": 0.3,
            "relationship_quality": -0.05,
            "career_momentum": -0.1,
        },
        "time_to_effect": 1,
        "confidence": 0.65,
    },
    "buy_house": {
        "keywords": ["buy house", "buy home", "purchase property", "real estate", "mortgage"],
        "type": "financial",
        "deltas": {
            "liquid_assets": -0.3,
            "debt_ratio": 0.3,
            "income_stability": 0.0,
            "expense_ratio": 0.15,
            "investment_diversity": 0.1,
            "stress_load": 0.1,
            "community_integration": 0.1,
        },
        "time_to_effect": 3,
        "confidence": 0.75,
    },
    "invest_aggressively": {
        "keywords": ["invest", "stock market", "crypto", "aggressive investment", "portfolio"],
        "type": "financial",
        "deltas": {
            "liquid_assets": -0.1,
            "investment_diversity": 0.2,
            "stress_load": 0.05,
        },
        "time_to_effect": 1,
        "confidence": 0.55,
    },
    "freelance": {
        "keywords": ["freelance", "freelancing", "self-employed", "independent contractor", "gig work"],
        "type": "career_transition",
        "deltas": {
            "income_stability": -0.3,
            "income_growth_rate": 0.05,
            "skill_breadth": 0.1,
            "stress_load": 0.1,
            "career_momentum": -0.05,
            "community_integration": -0.05,
        },
        "time_to_effect": 2,
        "confidence": 0.70,
    },
    "health_improvement": {
        "keywords": ["exercise", "gym", "diet", "health", "fitness", "yoga", "meditation"],
        "type": "health",
        "deltas": {
            "physical_health": 0.15,
            "mental_health": 0.1,
            "sleep_quality": 0.1,
            "stress_load": -0.1,
            "burnout_proximity": -0.05,
            "expense_ratio": 0.02,
        },
        "time_to_effect": 3,
        "confidence": 0.80,
    },
}


class DecisionTranslator:
    """
    Translates natural language decisions into structured DecisionDelta objects.
    
    Multi-stage NLP pipeline: Intent -> Entity -> LLM Mapping -> Confidence
    Falls back to rule-based templates if LLM is unavailable.
    """

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.parameter_mapper = ParameterMapper()
        self.confidence_scorer = ConfidenceScorer()

    def translate(self, decision_text: str) -> DecisionDelta:
        """
        Convert decision text to structured parameters.
        
        Returns DecisionDelta with extracted parameters and confidence score.
        """
        # Step 1: Extract intent
        intent = self.intent_classifier.classify(decision_text)
        
        # Step 2: Extract entities
        entities = self.entity_extractor.extract(decision_text)
        
        # Step 3: Try LLM mapping (sync wrapper for MVP)
        llm_params = self.parameter_mapper.map_parameters_sync(decision_text, intent, entities)
        
        # Step 4: Confidence scoring
        confidence = self.confidence_scorer.score(decision_text, intent, entities, llm_params)
        
        # If LLM mapping failed or returned empty (MVP state)
        if not llm_params:
            return self._fallback_translate(decision_text, match_score=confidence)
            
        time_to_effect = llm_params.pop("time_to_effect_months", 3)
        
        return DecisionDelta(
            decision_text=decision_text,
            decision_type=intent if intent != "unknown" else llm_params.get("decision_type", "unknown"),
            confidence=round(confidence, 2),
            time_to_effect_months=time_to_effect,
            delta_uncertainty=round(1 - confidence, 2),
            **llm_params
        )

    def _fallback_translate(self, decision_text: str, match_score: float) -> DecisionDelta:
        text_lower = decision_text.lower().strip()
        best_match = None
        best_score = 0

        for template_name, template in DECISION_TEMPLATES.items():
            score = self._match_score(text_lower, template["keywords"])
            if score > best_score:
                best_score = score
                best_match = template

        if best_match and best_score > 0:
            return self._template_to_delta(decision_text, best_match, max(match_score, best_score))
        else:
            return self._generic_delta(decision_text, match_score)

    def _match_score(self, text: str, keywords: list[str]) -> float:
        """Score how well text matches keywords (0.0–1.0)."""
        matches = sum(1 for kw in keywords if kw in text)
        if matches == 0:
            return 0.0
        return min(1.0, matches / len(keywords) + 0.3)

    def _template_to_delta(
        self, text: str, template: dict, match_score: float
    ) -> DecisionDelta:
        """Convert a matched template to DecisionDelta."""
        deltas = template["deltas"]
        confidence = template["confidence"] * match_score

        return DecisionDelta(
            decision_text=text,
            decision_type=template["type"],
            confidence=round(confidence, 2),
            time_to_effect_months=template["time_to_effect"],
            delta_uncertainty=round(1 - confidence, 2),
            **{k: v for k, v in deltas.items()},
        )

    def _generic_delta(self, text: str, match_score: float) -> DecisionDelta:
        """Fallback: small generic perturbation with low confidence."""
        return DecisionDelta(
            decision_text=text,
            decision_type="unknown",
            confidence=round(match_score, 2),
            stress_load=0.05,
            delta_uncertainty=round(1 - match_score, 2),
            time_to_effect_months=3,
        )
