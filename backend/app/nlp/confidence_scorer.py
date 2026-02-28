"""
Antigravity - Confidence Scorer
Assigns a confidence score to translations based on entity presence and intent clarity.
"""

class ConfidenceScorer:
    def score(self, text: str, intent: str, entities: dict, llm_params: dict) -> float:
        """
        Calculate a 0.0 to 1.0 confidence score for the translation.
        """
        score = 0.5  # Base score
        
        # Intent penalty/bonus
        if intent == "unknown":
            score -= 0.3
        else:
            score += 0.2
            
        # Entity bonus (more specific = higher confidence)
        total_entities = sum(len(v) for v in entities.values())
        if total_entities > 0:
            score += min(0.2, total_entities * 0.05)
            
        # Text length penalty (too short = vague, too long = confusing without LLM)
        words = len(text.split())
        if words < 3:
            score -= 0.2
            
        # LLM active bonus
        if llm_params:
            score += 0.1
            
        return max(0.1, min(0.95, score))
