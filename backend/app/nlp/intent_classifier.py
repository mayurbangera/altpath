"""
Antigravity - Decision Intent Classifier
Classifies natural language inputs into base decision domains.
"""
import re

INTENT_DOMAINS = [
    "career_transition",
    "financial",
    "education",
    "health",
    "relocation",
    "relationship",
    "family",
    "unknown"
]

class IntentClassifier:
    """MVP tf-idf or regex based intent classifier."""
    def __init__(self):
        self.rules = {
            "career_transition": [r"\bquit\b", r"\bjob\b", r"\bbusiness\b", r"\bstartup\b", r"\bswitch\b", r"\bcareer\b", r"\bfreelance\b"],
            "financial": [r"\bbuy\b", r"\bhouse\b", r"\binvest\b", r"\bmortgage\b", r"\bstock\b"],
            "education": [r"\bstudy\b", r"\buniversity\b", r"\bmaster\b", r"\bphd\b", r"\bdegree\b"],
            "health": [r"\bhealth\b", r"\bgym\b", r"\bexercise\b", r"\bdiet\b", r"\byoga\b"],
            "relocation": [r"\bmove\b", r"\brelocate\b", r"\babroad\b", r"\bmigrate\b"],
            "relationship": [r"\bmarry\b", r"\bmarriage\b", r"\bwedding\b", r"\bpartner\b"],
            "family": [r"\bchild\b", r"\bbaby\b", r"\bfamily\b", r"\bkids\b"],
        }

    def classify(self, text: str) -> str:
        text = text.lower()
        best_intent = "unknown"
        max_matches = 0
        
        for intent, patterns in self.rules.items():
            matches = sum(1 for p in patterns if re.search(p, text))
            if matches > max_matches:
                max_matches = matches
                best_intent = intent
                
        return best_intent
