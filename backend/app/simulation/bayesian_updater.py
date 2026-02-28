import numpy as np
from typing import Dict, Any, List
from app.core.state_model import UserState

class BayesianUpdater:
    """
    Implements Bayesian Online Updating for model priors.
    When a user provides feedback (e.g., 'X happened'), we update our
    belief about the transition coefficients or drift parameters.
    """

    def __init__(self):
        # Priors for drift/impact coefficients (mean and variance)
        self.priors_mu = {} # key: (domain, factor), value: mean
        self.priors_sigma = {} # key: (domain, factor), value: variance

    def update_with_feedback(self, 
                             initial_state: UserState, 
                             decision_delta: Dict[str, float], 
                             actual_outcome: Dict[str, float],
                             learning_rate: float = 0.1):
        """
        Performs a Gaussian update on the impact parameters.
        new_mu = (sigma_obs^2 * mu_prior + sigma_prior^2 * x_obs) / (sigma_obs^2 + sigma_prior^2)
        """
        # For simplicity in Phase 6/8, we implement a Momentum update 
        # that shifts the interaction matrix priors based on prediction error.
        
        for domain, actual_val in actual_outcome.items():
            if domain not in decision_delta:
                continue
                
            predicted_delta = decision_delta[domain]
            # Observation error
            error = actual_val - (getattr(initial_state, domain, 0.5) + predicted_delta)
            
            # Prior for this domain
            key = (domain, "global_drift")
            mu_prior = self.priors_mu.get(key, 0.0)
            sigma_prior = self.priors_sigma.get(key, 1.0)
            
            # Assume constant observation variance for this proof-of-concept
            sigma_obs = 0.5
            
            # Gaussian update
            # Posterior Mean
            new_mu = ((sigma_obs**2) * mu_prior + (sigma_prior**2) * error) / (sigma_obs**2 + sigma_prior**2)
            
            # Posterior Variance
            new_sigma = np.sqrt(1 / (1 / (sigma_prior**2) + 1 / (sigma_obs**2)))
            
            # Apply learning rate smoothing
            self.priors_mu[key] = (1 - learning_rate) * mu_prior + learning_rate * new_mu
            self.priors_sigma[key] = (1 - learning_rate) * sigma_prior + learning_rate * new_sigma

    def get_calibrated_drift(self, domain: str, factors: List[str] = None) -> float:
        """Returns the updated drift value based on global/local posterior."""
        key = (domain, "global_drift")
        return self.priors_mu.get(key, 0.001)  # Default drift if prior uninitialized

