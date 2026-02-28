"""
Antigravity – Scenario Branching Tree Generator
Creates branching decision trees with conditional probabilities
for exploring "then what?" paths.
"""

import numpy as np
from typing import Optional
from pydantic import BaseModel, Field
from app.core.state_model import UserState, DecisionDelta
from app.simulation.monte_carlo import MonteCarloEngine


class ScenarioNode(BaseModel):
    """A node in the scenario branching tree."""
    id: str
    label: str
    probability: float
    happiness_range: tuple[float, float]
    financial_index: float
    stress_level: float
    description: str
    children: list["ScenarioNode"] = []
    depth: int = 0
    is_terminal: bool = False


class ScenarioTree(BaseModel):
    """Complete scenario branching tree."""
    decision: str
    root: ScenarioNode
    total_scenarios: int
    best_path: list[str]
    worst_path: list[str]
    expected_value: float


class ScenarioBranchingEngine:
    """
    Generates branching scenario trees from a decision.
    
    Example output:
    Quit Job ─┬─ Startup Succeeds (30%)
              │   ├─ Rapid Growth (40%) → High reward
              │   └─ Moderate Growth (60%) → Stable
              ├─ Startup Pivots (30%)
              │   ├─ Pivot Succeeds (50%) → Moderate
              │   └─ Eventually Closes (50%) → Return to employment
              └─ Startup Fails (40%)
                  ├─ Quick Recovery (70%) → Baseline
                  └─ Extended Struggle (30%) → Stress
    """

    def __init__(self):
        self.mc_engine = MonteCarloEngine()

    def generate_tree(
        self,
        state: UserState,
        decision: DecisionDelta,
        max_depth: int = 3,
    ) -> ScenarioTree:
        """Generate a complete scenario branching tree."""
        decision_type = decision.decision_type
        
        # Select branching template based on decision type
        if decision_type == "career_transition":
            root = self._career_transition_tree(state, decision)
        elif decision_type == "education":
            root = self._education_tree(state, decision)
        elif decision_type == "relocation":
            root = self._relocation_tree(state, decision)
        elif decision_type == "health":
            root = self._health_tree(state, decision)
        elif decision_type == "financial":
            root = self._financial_tree(state, decision)
        elif decision_type == "relationship":
            root = self._relationship_tree(state, decision)
        elif decision_type == "family":
            root = self._family_tree(state, decision)
        else:
            root = self._generic_tree(state, decision)

        # Count total leaf scenarios
        total = self._count_leaves(root)
        
        # Find best and worst paths
        best_path, best_val = self._find_extreme_path(root, maximize=True)
        worst_path, worst_val = self._find_extreme_path(root, maximize=False)
        
        # Compute expected value
        expected = self._compute_expected_value(root)

        return ScenarioTree(
            decision=decision.decision_text,
            root=root,
            total_scenarios=total,
            best_path=best_path,
            worst_path=worst_path,
            expected_value=round(expected, 3),
        )

    def _career_transition_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.1, base_h + 0.1),
            financial_index=state.financial_index, stress_level=state.stress_load,
            description="You decide to make the career transition.", depth=0,
            children=[
                ScenarioNode(
                    id="success", label="Venture Succeeds", probability=0.25,
                    happiness_range=(base_h + 0.1, base_h + 0.3),
                    financial_index=state.financial_index + 0.2, stress_level=max(0, state.stress_load - 0.1),
                    description="Your new venture gains traction. Revenue grows, team is solid.",
                    depth=1,
                    children=[
                        ScenarioNode(id="rapid_growth", label="Rapid Growth", probability=0.35,
                                     happiness_range=(base_h + 0.2, base_h + 0.4),
                                     financial_index=state.financial_index + 0.35,
                                     stress_level=state.stress_load + 0.05,
                                     description="Rapid scaling, significant financial upside. Some new stress from growth.", depth=2, is_terminal=True),
                        ScenarioNode(id="steady_growth", label="Steady Growth", probability=0.65,
                                     happiness_range=(base_h + 0.1, base_h + 0.25),
                                     financial_index=state.financial_index + 0.15,
                                     stress_level=max(0, state.stress_load - 0.05),
                                     description="Sustainable growth with improving work-life balance.", depth=2, is_terminal=True),
                    ]
                ),
                ScenarioNode(
                    id="pivot", label="Needs Pivot", probability=0.35,
                    happiness_range=(base_h - 0.05, base_h + 0.1),
                    financial_index=state.financial_index - 0.05, stress_level=state.stress_load + 0.15,
                    description="Initial approach doesn't work, but you find a new direction.",
                    depth=1,
                    children=[
                        ScenarioNode(id="pivot_success", label="Pivot Succeeds", probability=0.45,
                                     happiness_range=(base_h, base_h + 0.15),
                                     financial_index=state.financial_index + 0.05,
                                     stress_level=state.stress_load + 0.05,
                                     description="The pivot pays off — new product-market fit achieved.", depth=2, is_terminal=True),
                        ScenarioNode(id="pivot_struggle", label="Continued Struggle", probability=0.35,
                                     happiness_range=(base_h - 0.1, base_h),
                                     financial_index=state.financial_index - 0.1,
                                     stress_level=state.stress_load + 0.2,
                                     description="Multiple pivots, burning savings, increasing stress.", depth=2, is_terminal=True),
                        ScenarioNode(id="graceful_exit", label="Graceful Exit", probability=0.20,
                                     happiness_range=(base_h - 0.05, base_h + 0.05),
                                     financial_index=state.financial_index - 0.05,
                                     stress_level=state.stress_load + 0.05,
                                     description="Decide to close down gracefully, return to employment with new skills.", depth=2, is_terminal=True),
                    ]
                ),
                ScenarioNode(
                    id="fail", label="Venture Fails", probability=0.40,
                    happiness_range=(base_h - 0.2, base_h - 0.05),
                    financial_index=state.financial_index - 0.2, stress_level=state.stress_load + 0.25,
                    description="The venture doesn't gain traction and runs out of runway.",
                    depth=1,
                    children=[
                        ScenarioNode(id="quick_recovery", label="Quick Recovery", probability=0.60,
                                     happiness_range=(base_h - 0.1, base_h + 0.05),
                                     financial_index=state.financial_index - 0.08,
                                     stress_level=state.stress_load + 0.1,
                                     description="Leverage new skills and network to land a better role than before.", depth=2, is_terminal=True),
                        ScenarioNode(id="extended_difficulty", label="Extended Difficulty", probability=0.25,
                                     happiness_range=(base_h - 0.25, base_h - 0.1),
                                     financial_index=state.financial_index - 0.25,
                                     stress_level=state.stress_load + 0.3,
                                     description="Difficulty finding new work, financial strain, high stress.", depth=2, is_terminal=True),
                        ScenarioNode(id="new_direction", label="Career Redirect", probability=0.15,
                                     happiness_range=(base_h - 0.05, base_h + 0.1),
                                     financial_index=state.financial_index - 0.1,
                                     stress_level=state.stress_load + 0.05,
                                     description="Failure inspires a entirely new career direction with unexpected upside.", depth=2, is_terminal=True),
                    ]
                ),
            ]
        )

    def _education_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.1, base_h + 0.05), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You pursue higher education.", depth=0,
            children=[
                ScenarioNode(id="complete_excel", label="Graduate with Distinction", probability=0.30,
                    happiness_range=(base_h + 0.05, base_h + 0.25), financial_index=state.financial_index + 0.1,
                    stress_level=state.stress_load + 0.1, description="Excel academically, strong job offers on graduation.", depth=1, is_terminal=True),
                ScenarioNode(id="complete_avg", label="Graduate & Transition", probability=0.50,
                    happiness_range=(base_h - 0.05, base_h + 0.15), financial_index=state.financial_index,
                    stress_level=state.stress_load + 0.15, description="Complete the program and transition to a new role.", depth=1, is_terminal=True),
                ScenarioNode(id="dropout", label="Don't Complete / Pivot", probability=0.15,
                    happiness_range=(base_h - 0.15, base_h - 0.05), financial_index=state.financial_index - 0.15,
                    stress_level=state.stress_load + 0.2, description="Leave program early due to financial or personal reasons.", depth=1, is_terminal=True),
                ScenarioNode(id="debt_burden", label="Degree but Debt Burden", probability=0.05,
                    happiness_range=(base_h - 0.1, base_h + 0.05), financial_index=state.financial_index - 0.2,
                    stress_level=state.stress_load + 0.15, description="Complete but student debt significantly constrains future choices.", depth=1, is_terminal=True),
            ]
        )

    def _relocation_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.15, base_h + 0.15), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You relocate to a new place.", depth=0,
            children=[
                ScenarioNode(id="thrive", label="Thrive in New Location", probability=0.35,
                    happiness_range=(base_h + 0.05, base_h + 0.25), financial_index=state.financial_index + 0.1,
                    stress_level=max(0, state.stress_load - 0.05), description="Build new community, career grows, quality of life improves.", depth=1, is_terminal=True),
                ScenarioNode(id="adjust", label="Gradual Adjustment", probability=0.40,
                    happiness_range=(base_h - 0.05, base_h + 0.1), financial_index=state.financial_index,
                    stress_level=state.stress_load + 0.1, description="Takes 1-2 years to fully adjust, but eventually settles.", depth=1, is_terminal=True),
                ScenarioNode(id="struggle", label="Struggle to Adapt", probability=0.15,
                    happiness_range=(base_h - 0.2, base_h - 0.05), financial_index=state.financial_index - 0.1,
                    stress_level=state.stress_load + 0.2, description="Cultural mismatch, loneliness, considering return.", depth=1, is_terminal=True),
                ScenarioNode(id="return", label="Return Home", probability=0.10,
                    happiness_range=(base_h - 0.1, base_h + 0.05), financial_index=state.financial_index - 0.15,
                    stress_level=state.stress_load + 0.1, description="Move back after 6-12 months, financial hit but lessons learned.", depth=1, is_terminal=True),
            ]
        )
    
    def _health_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h, base_h + 0.15), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You commit to health improvement.", depth=0,
            children=[
                ScenarioNode(id="sustained", label="Sustained Habit Change", probability=0.35,
                    happiness_range=(base_h + 0.1, base_h + 0.25), financial_index=state.financial_index,
                    stress_level=max(0, state.stress_load - 0.15), description="Consistent practice becomes a lifestyle. Significant improvements.", depth=1, is_terminal=True),
                ScenarioNode(id="moderate", label="Moderate Improvement", probability=0.40,
                    happiness_range=(base_h + 0.05, base_h + 0.15), financial_index=state.financial_index,
                    stress_level=max(0, state.stress_load - 0.08), description="Good progress with occasional lapses. Net positive.", depth=1, is_terminal=True),
                ScenarioNode(id="relapse", label="Initial Progress then Relapse", probability=0.25,
                    happiness_range=(base_h - 0.05, base_h + 0.05), financial_index=state.financial_index,
                    stress_level=state.stress_load, description="Start strong but don't sustain. Back to baseline.", depth=1, is_terminal=True),
            ]
        )

    def _financial_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.1, base_h + 0.15), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You make a major financial decision.", depth=0,
            children=[
                ScenarioNode(id="good_outcome", label="Strong Returns", probability=0.30,
                    happiness_range=(base_h + 0.05, base_h + 0.2), financial_index=state.financial_index + 0.2,
                    stress_level=max(0, state.stress_load - 0.05), description="Investment or purchase pays off well.", depth=1, is_terminal=True),
                ScenarioNode(id="neutral", label="Break Even", probability=0.40,
                    happiness_range=(base_h - 0.05, base_h + 0.05), financial_index=state.financial_index,
                    stress_level=state.stress_load, description="Neither great nor bad outcome. Slight opportunity cost.", depth=1, is_terminal=True),
                ScenarioNode(id="loss", label="Financial Loss", probability=0.30,
                    happiness_range=(base_h - 0.15, base_h - 0.05), financial_index=state.financial_index - 0.15,
                    stress_level=state.stress_load + 0.15, description="Loss of capital, need to rebuild savings.", depth=1, is_terminal=True),
            ]
        )
    
    def _relationship_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.05, base_h + 0.15), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You make a relationship decision.", depth=0,
            children=[
                ScenarioNode(id="strengthen", label="Relationship Strengthens", probability=0.45,
                    happiness_range=(base_h + 0.1, base_h + 0.25), financial_index=state.financial_index,
                    stress_level=max(0, state.stress_load - 0.1), description="The relationship deepens and brings stability.", depth=1, is_terminal=True),
                ScenarioNode(id="stable", label="Stable Adjustment", probability=0.35,
                    happiness_range=(base_h - 0.05, base_h + 0.1), financial_index=state.financial_index - 0.05,
                    stress_level=state.stress_load + 0.05, description="Normal adjustment period with gradual stabilization.", depth=1, is_terminal=True),
                ScenarioNode(id="strain", label="Unexpected Strain", probability=0.20,
                    happiness_range=(base_h - 0.15, base_h), financial_index=state.financial_index - 0.1,
                    stress_level=state.stress_load + 0.15, description="Unexpected compatibility issues create tension.", depth=1, is_terminal=True),
            ]
        )

    def _family_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.1, base_h + 0.15), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You make a family decision.", depth=0,
            children=[
                ScenarioNode(id="joyful", label="Joyful & Manageable", probability=0.40,
                    happiness_range=(base_h + 0.05, base_h + 0.2), financial_index=state.financial_index - 0.1,
                    stress_level=state.stress_load + 0.1, description="Family grows in a manageable, fulfilling way.", depth=1, is_terminal=True),
                ScenarioNode(id="challenging", label="Challenging but Rewarding", probability=0.40,
                    happiness_range=(base_h - 0.05, base_h + 0.1), financial_index=state.financial_index - 0.15,
                    stress_level=state.stress_load + 0.2, description="Significant adjustment required. Rewarding long-term.", depth=1, is_terminal=True),
                ScenarioNode(id="overwhelming", label="Overwhelming Demands", probability=0.20,
                    happiness_range=(base_h - 0.2, base_h - 0.05), financial_index=state.financial_index - 0.2,
                    stress_level=state.stress_load + 0.3, description="Financial and emotional strain exceeds expectations.", depth=1, is_terminal=True),
            ]
        )

    def _generic_tree(self, state: UserState, decision: DecisionDelta) -> ScenarioNode:
        base_h = state.overall_happiness
        return ScenarioNode(
            id="root", label=decision.decision_text, probability=1.0,
            happiness_range=(base_h - 0.1, base_h + 0.1), financial_index=state.financial_index,
            stress_level=state.stress_load, description="You proceed with this decision.", depth=0,
            children=[
                ScenarioNode(id="positive", label="Positive Outcome", probability=0.35,
                    happiness_range=(base_h + 0.05, base_h + 0.2), financial_index=state.financial_index + 0.05,
                    stress_level=max(0, state.stress_load - 0.05), description="Decision pays off as hoped.", depth=1, is_terminal=True),
                ScenarioNode(id="neutral", label="Neutral Outcome", probability=0.40,
                    happiness_range=(base_h - 0.05, base_h + 0.05), financial_index=state.financial_index,
                    stress_level=state.stress_load, description="Minimal net impact.", depth=1, is_terminal=True),
                ScenarioNode(id="negative", label="Negative Outcome", probability=0.25,
                    happiness_range=(base_h - 0.15, base_h - 0.05), financial_index=state.financial_index - 0.1,
                    stress_level=state.stress_load + 0.1, description="Decision doesn't work out. Recovery needed.", depth=1, is_terminal=True),
            ]
        )

    def _count_leaves(self, node: ScenarioNode) -> int:
        if node.is_terminal or not node.children:
            return 1
        return sum(self._count_leaves(c) for c in node.children)

    def _find_extreme_path(
        self, node: ScenarioNode, maximize: bool = True
    ) -> tuple[list[str], float]:
        if node.is_terminal or not node.children:
            avg = sum(node.happiness_range) / 2
            return [node.label], avg

        best_path = []
        best_val = -float("inf") if maximize else float("inf")

        for child in node.children:
            child_path, child_val = self._find_extreme_path(child, maximize)
            if (maximize and child_val > best_val) or (not maximize and child_val < best_val):
                best_val = child_val
                best_path = [node.label] + child_path

        return best_path, best_val

    def _compute_expected_value(self, node: ScenarioNode) -> float:
        if node.is_terminal or not node.children:
            return sum(node.happiness_range) / 2

        ev = 0.0
        for child in node.children:
            child_ev = self._compute_expected_value(child)
            ev += child.probability * child_ev
        return ev
