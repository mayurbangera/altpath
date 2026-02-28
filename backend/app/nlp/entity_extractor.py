"""
Antigravity - SpaCy Entity Extractor
Extracts dates, money, organizations, locations, and other metadata.
"""
import logging

logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self):
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy en_core_web_sm model")
        except Exception as e:
            logger.warning(f"Failed to load spaCy model: {e}")

    def extract(self, text: str) -> dict:
        """Extract named entities and temporal/numeric values."""
        entities = {
            "MONEY": [],
            "DATE": [],
            "GPE": [],
            "ORG": [],
            "PERSON": [],
            "CARDINAL": []
        }
        
        if not self.nlp:
            return entities
            
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
                
        # Deduplicate
        for k in entities:
            entities[k] = list(set(entities[k]))
            
        return entities
