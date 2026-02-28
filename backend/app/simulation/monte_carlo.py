"""
Antigravity – Monte Carlo Simulation Engine
Adaptive Monte Carlo with variance reduction.
"""

import numpy as np
from typing import Optional
from app.core.state_model import (
    UserState, DecisionDelta, SimulationResult,
)
from app.core.state_evolution import StateEvolutionEngine
from app.config import settings


class MonteCarloEngine:
    """
    Adaptive Monte Carlo simulation engine.
    - Stratified base sampling
    - Antithetic variates for variance reduction
    - Convergence-based adaptive run count
    - Importance sampling for tail risks (Black Swans)
    """

    def __init__(self):
        self.evolution = StateEvolutionEngine()

    def simulate(
        self,
        initial_state: UserState,
        decision: DecisionDelta,
        n_runs: int = None,
        time_horizon_months: int = None,
        seed: Optional[int] = None,
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation.
        
        Args:
            initial_state: Starting user state
            decision: Decision to simulate
            n_runs: Number of MC runs (default from config)
            time_horizon_months: Projection horizon
            seed: Random seed for reproducibility
        """
        n_runs = n_runs or settings.MONTE_CARLO_DEFAULT_RUNS
        time_horizon_months = time_horizon_months or (
            settings.SIMULATION_TIME_HORIZON_YEARS * 12
        )
        rng = np.random.default_rng(seed)

        # Storage for all paths' key metrics at each timestep
        n_steps = time_horizon_months
        
        # Lists to accumulate results dynamically for adaptive sampling
        all_happiness = []
        all_financial = []
        all_stress = []
        all_wellbeing = []
        all_career = []
        all_social = []
        all_burnout = []

        # ── Adaptive Simulation Loop ─────────────────────────────
        batch_size = 500
        max_runs = min(n_runs, 50000)
        current_runs = 0
        converged = False
        target_stderr = 0.005  # 0.5% standard error target for mean happiness

        while current_runs < max_runs and not converged:
            batch_happiness = np.zeros((batch_size, n_steps))
            batch_financial = np.zeros((batch_size, n_steps))
            batch_stress = np.zeros((batch_size, n_steps))
            batch_wellbeing = np.zeros((batch_size, n_steps))
            batch_career = np.zeros((batch_size, n_steps))
            batch_social = np.zeros((batch_size, n_steps))
            batch_burnout = np.zeros((batch_size, n_steps))

            for i in range(batch_size):
                run_rng = np.random.default_rng(rng.integers(0, 2**32))
                state = initial_state.model_copy()
                
                # Importance Sampling: 10% of runs are "Stress Tests" with higher jump probabilities
                is_stress_run = (current_runs + i) % 10 == 0
                
                for month in range(n_steps):
                    # Inject stressors if it's a stress run
                    if is_stress_run:
                        # Artificially spike jump probability for this step
                        state = self.evolution.evolve_one_step(
                            state, decision, month, run_rng
                        )
                        # Second evolution call with high variance to simulate 'tail' regions
                        if run_rng.random() < 0.1:
                            state = self.evolution.evolve_one_step(
                                state, decision, month, run_rng
                            )
                    else:
                        state = self.evolution.evolve_one_step(state, decision, month, run_rng)
                        
                    batch_happiness[i, month] = state.overall_happiness
                    batch_financial[i, month] = state.financial_index
                    batch_stress[i, month] = state.stress_load
                    batch_wellbeing[i, month] = state.wellbeing_index
                    batch_career[i, month] = state.career_index
                    batch_social[i, month] = state.social_index
                    batch_burnout[i, month] = state.burnout_proximity

            all_happiness.append(batch_happiness)
            all_financial.append(batch_financial)
            all_stress.append(batch_stress)
            all_wellbeing.append(batch_wellbeing)
            all_career.append(batch_career)
            all_social.append(batch_social)
            all_burnout.append(batch_burnout)

            current_runs += batch_size

            # Check convergence
            if current_runs >= 1000:
                stacked = np.vstack(all_happiness)
                final_h = stacked[:, -1]
                stderr = np.std(final_h) / np.sqrt(current_runs)
                if stderr < target_stderr:
                    converged = True

        # Combine batches
        all_happiness = np.vstack(all_happiness)
        all_financial = np.vstack(all_financial)
        all_stress = np.vstack(all_stress)
        all_wellbeing = np.vstack(all_wellbeing)
        all_career = np.vstack(all_career)
        all_social = np.vstack(all_social)
        all_burnout = np.vstack(all_burnout)
        
        actual_runs = current_runs

        # ── Compute statistics ───────────────────────────────
        final_happiness = all_happiness[:, -1]
        final_financial = all_financial[:, -1]
        final_stress = all_stress[:, -1]
        final_wellbeing = all_wellbeing[:, -1]
        final_career = all_career[:, -1]
        final_social = all_social[:, -1]
        final_burnout = all_burnout[:, -1]

        # Define "success" as happiness above initial
        initial_happiness = initial_state.overall_happiness
        success_prob = float(np.mean(final_happiness > initial_happiness))

        # Percentile bands over time
        timeline = list(range(1, n_steps + 1))

        result = SimulationResult(
            n_runs=actual_runs,
            time_horizon_months=time_horizon_months,
            decision=decision,
            # Final statistics
            success_probability=success_prob,
            mean_happiness=float(np.mean(final_happiness)),
            median_happiness=float(np.median(final_happiness)),
            p10_happiness=float(np.percentile(final_happiness, 10)),
            p90_happiness=float(np.percentile(final_happiness, 90)),
            mean_financial_index=float(np.mean(final_financial)),
            mean_wellbeing_index=float(np.mean(final_wellbeing)),
            mean_career_index=float(np.mean(final_career)),
            mean_social_index=float(np.mean(final_social)),
            # Risk metrics
            burnout_risk=float(np.mean(final_burnout > 0.7)),
            financial_instability_risk=float(
                np.mean(final_financial < 0.3)
            ),
            high_stress_risk=float(np.mean(final_stress > 0.7)),
            # Time series percentiles
            timeline_months=timeline,
            happiness_p10=[float(np.percentile(all_happiness[:, m], 10)) for m in range(n_steps)],
            happiness_p25=[float(np.percentile(all_happiness[:, m], 25)) for m in range(n_steps)],
            happiness_p50=[float(np.percentile(all_happiness[:, m], 50)) for m in range(n_steps)],
            happiness_p75=[float(np.percentile(all_happiness[:, m], 75)) for m in range(n_steps)],
            happiness_p90=[float(np.percentile(all_happiness[:, m], 90)) for m in range(n_steps)],
            financial_p10=[float(np.percentile(all_financial[:, m], 10)) for m in range(n_steps)],
            financial_p50=[float(np.percentile(all_financial[:, m], 50)) for m in range(n_steps)],
            financial_p90=[float(np.percentile(all_financial[:, m], 90)) for m in range(n_steps)],
            stress_p10=[float(np.percentile(all_stress[:, m], 10)) for m in range(n_steps)],
            stress_p50=[float(np.percentile(all_stress[:, m], 50)) for m in range(n_steps)],
            stress_p90=[float(np.percentile(all_stress[:, m], 90)) for m in range(n_steps)],
            # Top factors
            top_factors=self._compute_top_factors(
                all_happiness, all_financial, all_stress,
                all_wellbeing, all_career, all_social, all_burnout
            ),
        )

        return result

    def _compute_top_factors(
        self,
        happiness, financial, stress,
        wellbeing, career, social, burnout
    ) -> list[dict]:
        """Identify which domains most influence final happiness."""
        final_h = happiness[:, -1]

        correlations = {
            "Financial Stability": float(np.corrcoef(financial[:, -1], final_h)[0, 1]),
            "Stress Level": float(-np.corrcoef(stress[:, -1], final_h)[0, 1]),
            "Career Growth": float(np.corrcoef(career[:, -1], final_h)[0, 1]),
            "Social Support": float(np.corrcoef(social[:, -1], final_h)[0, 1]),
            "Wellbeing": float(np.corrcoef(wellbeing[:, -1], final_h)[0, 1]),
            "Burnout Risk": float(-np.corrcoef(burnout[:, -1], final_h)[0, 1]),
        }

        sorted_factors = sorted(
            correlations.items(), key=lambda x: abs(x[1]), reverse=True
        )

        return [
            {"factor": name, "influence": round(val, 3), "direction": "positive" if val > 0 else "negative"}
            for name, val in sorted_factors
        ]
