"""
Antigravity – Results API
Retrieve and inspect simulation results.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """
    Fetch a past simulation result by its ID.
    """
    from app.simulation.results_store import ResultsStore
    from fastapi import HTTPException
    
    result = ResultsStore.get(simulation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Simulation result not found")
        
    return result

@router.get("/")
async def list_results():
    """List all recent simulation results."""
    from app.simulation.results_store import ResultsStore
    return ResultsStore.list_all()

