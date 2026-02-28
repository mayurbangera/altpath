"""
Antigravity – Agent-Based Model (ABM)
Simulates social dynamics, networking, and peer effects.
"""
import numpy as np
from typing import List, Dict
from app.core.state_model import UserState, DecisionDelta

class AgentBasedModel:
    """
    Simulates a small 'social neighborhood' around the user to model:
    - Networking ROI (information cascades)
    - Peer pressure (behavioral drift)
    - Social support dynamics
    """

    def __init__(self, n_peers: int = 50):
        self.n_peers = n_peers

    def simulate_social_impact(
        self,
        state: UserState,
        decision: DecisionDelta,
        months: int = 60,
        rng: np.random.Generator = None
    ) -> Dict[str, np.ndarray]:
        """
        Run an ABM simulation where the user's state is influenced
        by a generated peer group.
        """
        if rng is None:
            rng = np.random.default_rng()

        # Generate a synthetic peer group around the user's initial state
        peers = self._initialize_peers(state, rng)
        
        # User trajectory influenced by peers
        user_happiness = np.zeros(months)
        user_career = np.zeros(months)
        user_stress = np.zeros(months)
        
        current_state = state.model_copy()
        
        for m in range(months):
            # 1. Peer updates (simple mean reversion to their own targets)
            peers = self._evolve_peers(peers, rng)
            
            # 2. Influence: User picks up traits from the top 10% of network
            # if their networking_strength is high.
            network_quality = np.mean([p['career'] for p in peers])
            peer_influence = (state.network_strength * (network_quality - current_state.career_index)) * 0.05
            
            # 3. Apply influence to current state
            current_state.career_momentum += peer_influence
            current_state.stress_load += (np.mean([p['stress'] for p in peers]) - current_state.stress_load) * 0.02
            
            # 4. Extract metrics
            user_happiness[m] = current_state.overall_happiness
            user_career[m] = current_state.career_index
            user_stress[m] = current_state.stress_load
            
        return {
            "happiness": user_happiness,
            "career": user_career,
            "stress": user_stress
        }

    def _initialize_peers(self, user_state: UserState, rng: np.random.Generator) -> List[Dict]:
        """Create a diverse set of agents in the user's sphere."""
        peers = []
        for _ in range(self.n_peers):
            peers.append({
                "career": np.clip(rng.normal(user_state.career_index, 0.2), 0, 1),
                "stress": np.clip(rng.normal(user_state.stress_load, 0.2), 0, 1),
                "ambition": rng.random(),
                "supportiveness": rng.random()
            })
        return peers

    def _evolve_peers(self, peers: List[Dict], rng: np.random.Generator) -> List[Dict]:
        """Peers also change over time (adding noise/drift)."""
        for p in peers:
            p['career'] = np.clip(p['career'] + rng.normal(0, 0.02), 0, 1)
            p['stress'] = np.clip(p['stress'] + rng.normal(0, 0.03), 0, 1)
        return peers
