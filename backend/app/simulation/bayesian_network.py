"""
Antigravity – Bayesian Causal Graph
Dynamic causal network modeling life domain interactions
with temporal lags, interventions, and belief propagation.
"""

import networkx as nx
import numpy as np
from typing import Optional
from app.core.state_model import UserState


# ── Causal Edge Definition ───────────────────────────────────

class CausalEdge:
    """
    A directed causal edge in the life domain graph.
    """
    def __init__(
        self,
        source: str,
        target: str,
        weight: float,
        lag_months: int = 0,
        nonlinear: str = "linear",
        threshold: Optional[float] = None,
        description: str = "",
    ):
        self.source = source
        self.target = target
        self.weight = weight
        self.lag_months = lag_months
        self.nonlinear = nonlinear  # linear, sigmoid, log, quadratic
        self.threshold = threshold
        self.description = description


# ── Full Causal Graph Definition ─────────────────────────────

CAUSAL_EDGES = [
    # ── Finance → Stress ─────────────────────────────────────
    CausalEdge("liquid_assets", "stress_load", weight=-0.20, lag_months=0,
               nonlinear="sigmoid", threshold=0.3,
               description="Low savings creates immediate financial stress"),
    CausalEdge("debt_ratio", "stress_load", weight=0.25, lag_months=0,
               nonlinear="sigmoid", threshold=0.5,
               description="High debt increases stress non-linearly"),
    CausalEdge("income_stability", "stress_load", weight=-0.15, lag_months=0,
               description="Income instability generates chronic stress"),

    # ── Stress → Health (delayed) ────────────────────────────
    CausalEdge("stress_load", "physical_health", weight=-0.18, lag_months=3,
               nonlinear="sigmoid", threshold=0.6,
               description="Chronic stress degrades physical health over 3 months"),
    CausalEdge("stress_load", "mental_health", weight=-0.25, lag_months=1,
               nonlinear="sigmoid", threshold=0.5,
               description="Stress hits mental health within a month"),
    CausalEdge("stress_load", "sleep_quality", weight=-0.20, lag_months=0,
               description="High stress immediately disrupts sleep"),

    # ── Sleep → Wellbeing ────────────────────────────────────
    CausalEdge("sleep_quality", "mental_health", weight=0.15, lag_months=1,
               description="Good sleep improves mental health over a month"),
    CausalEdge("sleep_quality", "physical_health", weight=0.10, lag_months=2,
               description="Sleep quality affects physical recovery"),
    CausalEdge("sleep_quality", "career_momentum", weight=0.08, lag_months=1,
               description="Well-rested people are more productive"),

    # ── Health → Productivity → Career ───────────────────────
    CausalEdge("physical_health", "career_momentum", weight=0.12, lag_months=2,
               description="Health enables sustained career effort"),
    CausalEdge("mental_health", "career_momentum", weight=0.18, lag_months=1,
               description="Mental health strongly drives work performance"),
    CausalEdge("mental_health", "relationship_quality", weight=0.15, lag_months=1,
               description="Mental health affects relationship dynamics"),

    # ── Career → Finance (delayed) ──────────────────────────
    CausalEdge("career_momentum", "income_growth_rate", weight=0.20, lag_months=6,
               description="Career growth translates to income after ~6 months"),
    CausalEdge("career_momentum", "network_strength", weight=0.10, lag_months=3,
               description="Career activity builds professional network"),
    CausalEdge("skill_depth", "career_momentum", weight=0.15, lag_months=3,
               description="Deep skills accelerate career trajectory"),
    CausalEdge("skill_breadth", "income_stability", weight=0.10, lag_months=6,
               description="Versatile skills improve job security"),

    # ── Education → Career (long delay) ─────────────────────
    CausalEdge("education_level", "career_momentum", weight=0.12, lag_months=12,
               description="Education boosts career but with significant lag"),
    CausalEdge("education_level", "income_growth_rate", weight=0.08, lag_months=18,
               description="Higher education slowly increases earnings trajectory"),
    CausalEdge("education_level", "network_strength", weight=0.10, lag_months=6,
               description="Education expands professional circles"),

    # ── Network → Career & Opportunities ────────────────────
    CausalEdge("network_strength", "career_momentum", weight=0.12, lag_months=3,
               description="Strong network accelerates career growth"),
    CausalEdge("network_strength", "income_stability", weight=0.08, lag_months=6,
               description="Network provides safety net for employment"),

    # ── Stress → Relationships (delayed) ────────────────────
    CausalEdge("stress_load", "relationship_quality", weight=-0.18, lag_months=2,
               nonlinear="sigmoid", threshold=0.6,
               description="Chronic high stress erodes relationships"),
    CausalEdge("burnout_proximity", "relationship_quality", weight=-0.22, lag_months=1,
               nonlinear="sigmoid", threshold=0.6,
               description="Burnout proximity strains close relationships"),

    # ── Relationships → Stress Buffer ───────────────────────
    CausalEdge("relationship_quality", "stress_load", weight=-0.12, lag_months=0,
               nonlinear="log",
               description="Strong relationships buffer stress"),
    CausalEdge("social_support", "stress_load", weight=-0.10, lag_months=0,
               description="Social support network reduces stress"),
    CausalEdge("social_support", "mental_health", weight=0.12, lag_months=1,
               description="Social support improves mental wellbeing"),

    # ── Burnout Dynamics ────────────────────────────────────
    CausalEdge("stress_load", "burnout_proximity", weight=0.20, lag_months=1,
               nonlinear="sigmoid", threshold=0.65,
               description="Sustained high stress pushes toward burnout"),
    CausalEdge("sleep_quality", "burnout_proximity", weight=-0.15, lag_months=1,
               description="Good sleep prevents burnout accumulation"),
    CausalEdge("burnout_proximity", "career_momentum", weight=-0.25, lag_months=0,
               nonlinear="sigmoid", threshold=0.7,
               description="Near-burnout destroys productivity"),
    CausalEdge("burnout_proximity", "mental_health", weight=-0.20, lag_months=0,
               nonlinear="sigmoid", threshold=0.6,
               description="Burnout proximity directly damages mental health"),

    # ── Family → Stress & Finances ──────────────────────────
    CausalEdge("family_obligations", "stress_load", weight=0.10, lag_months=0,
               description="Family responsibilities add baseline stress"),
    CausalEdge("family_obligations", "expense_ratio", weight=0.15, lag_months=0,
               description="Dependents increase expenses"),
    CausalEdge("family_obligations", "community_integration", weight=0.08, lag_months=3,
               description="Family involvement builds community ties"),

    # ── Adaptability (meta) ─────────────────────────────────
    CausalEdge("adaptability", "stress_load", weight=-0.08, lag_months=0,
               description="Adaptable people handle change with less stress"),
    CausalEdge("adaptability", "career_momentum", weight=0.06, lag_months=3,
               description="Adaptability helps navigate career transitions"),
]


class BayesianCausalGraph:
    """
    A dynamic Bayesian causal graph for life domain interactions.
    Uses NetworkX for graph structure and provides:
    - Intervention analysis (do-calculus style)
    - Causal path identification
    - Temporal unrolling for lagged effects
    - Sensitivity to causal assumptions
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Construct the causal DAG from edge definitions."""
        for edge in CAUSAL_EDGES:
            self.graph.add_edge(
                edge.source, edge.target,
                weight=edge.weight,
                lag_months=edge.lag_months,
                nonlinear=edge.nonlinear,
                threshold=edge.threshold,
                description=edge.description,
            )

    def get_causal_paths(self, source: str, target: str) -> list[list[str]]:
        """Find all causal paths from source to target."""
        try:
            return list(nx.all_simple_paths(self.graph, source, target, cutoff=5))
        except nx.NetworkXError:
            return []

    def get_total_causal_effect(
        self, source: str, target: str, state: UserState
    ) -> dict:
        """
        Estimate total causal effect of source on target,
        accounting for all direct and mediated paths.
        """
        paths = self.get_causal_paths(source, target)
        if not paths:
            return {"effect": 0.0, "paths": [], "total_lag": 0}

        total_effect = 0.0
        path_details = []

        for path in paths:
            path_effect = 1.0
            path_lag = 0
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i + 1]]
                weight = edge_data["weight"]
                
                # Apply non-linear transformation
                src_val = getattr(state, path[i], 0.5)
                weight = self._apply_nonlinearity(
                    weight, src_val,
                    edge_data.get("nonlinear", "linear"),
                    edge_data.get("threshold"),
                )
                
                path_effect *= weight
                path_lag += edge_data.get("lag_months", 0)

            total_effect += path_effect
            path_details.append({
                "path": " → ".join(path),
                "effect": round(path_effect, 4),
                "lag_months": path_lag,
            })

        return {
            "effect": round(total_effect, 4),
            "paths": sorted(path_details, key=lambda p: abs(p["effect"]), reverse=True),
            "total_lag_range": (
                min(p["lag_months"] for p in path_details),
                max(p["lag_months"] for p in path_details),
            ),
        }

    def intervene(
        self, state: UserState, intervention: dict[str, float], months: int = 12
    ) -> dict[str, float]:
        """
        Do-calculus style intervention: set variable to value and
        propagate effects through the causal graph, respecting temporal lags.
        
        Returns predicted changes in all downstream variables.
        """
        effects: dict[str, float] = {}
        
        for var, new_value in intervention.items():
            current = getattr(state, var, 0.5)
            delta = new_value - current
            
            # BFS through successors, accumulating effects
            queue = [(var, delta, 0)]  # (node, accumulated_effect, depth)
            visited = set()
            
            while queue:
                node, effect, depth = queue.pop(0)
                if node in visited or depth > 6:
                    continue
                visited.add(node)
                
                for successor in self.graph.successors(node):
                    edge = self.graph[node][successor]
                    lag = edge.get("lag_months", 0)
                    
                    if lag <= months:
                        src_val = getattr(state, node, 0.5)
                        w = self._apply_nonlinearity(
                            edge["weight"], src_val,
                            edge.get("nonlinear", "linear"),
                            edge.get("threshold"),
                        )
                        propagated = effect * w
                        effects[successor] = effects.get(successor, 0) + propagated
                        queue.append((successor, propagated, depth + 1))
        
        return {k: round(v, 4) for k, v in effects.items()}

    def get_sensitivity_analysis(self, state: UserState) -> list[dict]:
        """
        Identify which variables are most sensitive (have most downstream influence).
        """
        sensitivities = []
        
        for node in self.graph.nodes():
            # Count downstream effects
            descendants = nx.descendants(self.graph, node)
            total_influence = 0.0
            
            for desc in descendants:
                paths = self.get_causal_paths(node, desc)
                for path in paths:
                    path_weight = 1.0
                    for i in range(len(path) - 1):
                        path_weight *= abs(self.graph[path[i]][path[i + 1]]["weight"])
                    total_influence += abs(path_weight)
            
            sensitivities.append({
                "variable": node,
                "downstream_count": len(descendants),
                "total_influence": round(total_influence, 4),
                "current_value": round(getattr(state, node, 0.0), 3),
            })
        
        return sorted(sensitivities, key=lambda s: s["total_influence"], reverse=True)

    def get_affected_subgraph(self, starting_vars: list[str], max_depth: int = 3) -> dict:
        """
        Extract the subgraph containing all nodes influenced by the starting variables
        up to a certain depth. Returns format suitable for D3.js.
        """
        nodes = set(starting_vars)
        edges = []
        
        for start_var in starting_vars:
            if start_var not in self.graph:
                continue
                
            # BFS to find affected nodes
            queue = [(start_var, 0)]
            visited = {start_var}
            
            while queue:
                u, depth = queue.pop(0)
                if depth >= max_depth:
                    continue
                    
                for v in self.graph.successors(u):
                    edge_data = self.graph[u][v]
                    edges.append({
                        "source": u,
                        "target": v,
                        "weight": edge_data["weight"],
                        "lag": edge_data.get("lag_months", 0),
                        "description": edge_data.get("description", "")
                    })
                    if v not in visited:
                        visited.add(v)
                        nodes.add(v)
                        queue.append((v, depth + 1))
        
        return {
            "nodes": [{"id": n, "label": n.replace("_", " ").title()} for n in nodes],
            "edges": edges
        }

    def get_graph_summary(self) -> dict:
        """Get summary statistics of the causal graph."""
        return {
            "nodes": list(self.graph.nodes()),
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "weight": d["weight"],
                    "lag_months": d.get("lag_months", 0),
                    "description": d.get("description", ""),
                }
                for u, v, d in self.graph.edges(data=True)
            ],
        }

    def _apply_nonlinearity(
        self, weight: float, value: float, kind: str, threshold: Optional[float]
    ) -> float:
        """Apply non-linear transformation to edge weight."""
        if kind == "sigmoid" and threshold is not None:
            activation = 1.0 / (1.0 + np.exp(-10 * (value - threshold)))
            return weight * activation
        elif kind == "log":
            return weight * np.log1p(value) / np.log(2)
        elif kind == "quadratic":
            opt = threshold or 0.5
            return weight * (1.0 - ((value - opt) ** 2) / max(opt, 1 - opt) ** 2)
        return weight
