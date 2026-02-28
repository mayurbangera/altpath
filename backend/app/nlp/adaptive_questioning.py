"""
Antigravity - Adaptive Questioning System
Generates targeted clarifying questions based on missing information in a decision delta.
"""

class AdaptiveQuestioningSystem:
    def generate_questions(self, intent: str, entities: dict) -> list[str]:
        """Generate up to 3 context-aware clarification questions based on missing entities."""
        questions = []
        
        # Financial specifics
        if not entities.get("MONEY"):
            if intent in ["career_transition", "financial"]:
                questions.append("Could you clarify the expected financial impact (e.g., salary change or investment amount)?")
            elif intent == "buy_house":
                questions.append("What is the approximate budget or mortgage amount you are considering?")
                
        # Timeline specifics
        if not entities.get("DATE"):
            questions.append("What is your expected timeline for making this transition happen?")
            
        # Relocation specifics
        if intent == "relocation" and not entities.get("GPE"):
            questions.append("Where exactly are you planning to relocate to (e.g., city, country)?")
            
        # Education specifics
        if intent == "education" and not entities.get("ORG"):
            questions.append("Which institution, university, or type of degree program are you considering?")
            
        # Career specifics
        if intent == "career_transition" and not entities.get("ORG"):
            questions.append("Which company or specific role are you transitioning to?")
            
        # Catch-all
        if len(questions) < 2:
            questions.append("Are there any other specific factors or constraints driving this decision?")
            
        return questions[:3]
