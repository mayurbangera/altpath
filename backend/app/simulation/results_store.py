from typing import Dict, Optional
from app.core.state_model import SimulationResult

class ResultsStore:
    """
    In-memory store for simulation results.
    In production, this would use Redis or PostgreSQL.
    """
    _results: Dict[str, SimulationResult] = {}

    @classmethod
    def save(cls, simulation_id: str, result: SimulationResult):
        cls._results[simulation_id] = result

    @classmethod
    def get(cls, simulation_id: str) -> Optional[SimulationResult]:
        return cls._results.get(simulation_id)

    @classmethod
    def list_all(cls):
        return cls._results
