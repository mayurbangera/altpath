"""
Antigravity - LLM Parameter Mapper
Uses Ollama (Llama 3 or similar) to map decisions and entities to state vector deltas.
"""
import json
import logging
import httpx
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class ParameterMapper:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate" if settings.OLLAMA_BASE_URL else None
        self.model = settings.OLLAMA_MODEL if hasattr(settings, "OLLAMA_MODEL") else "llama3"
        
    async def map_parameters_async(self, text: str, intent: str, entities: dict) -> dict:
        """
        Calls local LLM to predict parameter deltas. 
        Falls back to safe defaults if LLM is unavailable or fails.
        """
        if not self.ollama_url:
            return {}
            
        prompt = f"""
        You are an expert decision science AI. Map the following life decision to structured parameter changes (-1.0 to 1.0).
        
        Decision: "{text}"
        Classified Intent: {intent}
        Extracted Entities: {json.dumps(entities)}
        
        Return ONLY valid JSON with keys corresponding to Antigravity UserState dimensions 
        (e.g., 'liquid_assets', 'stress_load', 'career_momentum', etc.) and float values.
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.ollama_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return json.loads(data.get("response", "{}"))
        except Exception as e:
            logger.error(f"LLM Parameter Mapping failed: {e}")
            return {}

    def map_parameters_sync(self, text: str, intent: str, entities: dict) -> dict:
        """Synchronous wrapper for current DecisionTranslator usage."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # In a running loop, we can't easily block, but translator MVP might be sync
            # Using thread executor if needed, but for MVP we just return empty
            return {}
        return loop.run_until_complete(self.map_parameters_async(text, intent, entities))
