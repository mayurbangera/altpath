"""
Antigravity – Configuration
Centralized settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Antigravity"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/antigravity"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Simulation defaults
    MONTE_CARLO_DEFAULT_RUNS: int = 10_000
    MONTE_CARLO_MAX_RUNS: int = 100_000
    SIMULATION_TIME_HORIZON_YEARS: int = 10
    SIMULATION_TIME_STEP_MONTHS: int = 1
    
    # NLP / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Confidence thresholds
    NLP_CONFIDENCE_THRESHOLD: float = 0.6
    ENSEMBLE_DISAGREEMENT_THRESHOLD: float = 0.15
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
