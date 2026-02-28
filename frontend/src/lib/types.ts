/**
 * Antigravity – TypeScript Types
 * Mirrors the backend Pydantic models.
 */

export interface BigFiveVector {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
}

export interface UserState {
  // Financial
  liquid_assets: number;
  debt_ratio: number;
  income_stability: number;
  income_growth_rate: number;
  expense_ratio: number;
  investment_diversity: number;
  // Human Capital
  skill_breadth: number;
  skill_depth: number;
  education_level: number;
  network_strength: number;
  career_momentum: number;
  // Wellbeing
  physical_health: number;
  mental_health: number;
  sleep_quality: number;
  stress_load: number;
  burnout_proximity: number;
  // Social
  relationship_quality: number;
  social_support: number;
  family_obligations: number;
  community_integration: number;
  // Meta
  risk_tolerance: number;
  time_preference: number;
  adaptability: number;
  personality: BigFiveVector;
  // Metadata
  age: number;
  country: string;
}

export interface DecisionDelta {
  decision_text: string;
  decision_type: string;
  confidence: number;
  liquid_assets?: number;
  debt_ratio?: number;
  income_stability?: number;
  income_growth_rate?: number;
  expense_ratio?: number;
  investment_diversity?: number;
  skill_breadth?: number;
  skill_depth?: number;
  education_level?: number;
  network_strength?: number;
  career_momentum?: number;
  physical_health?: number;
  mental_health?: number;
  sleep_quality?: number;
  stress_load?: number;
  burnout_proximity?: number;
  relationship_quality?: number;
  social_support?: number;
  family_obligations?: number;
  community_integration?: number;
  time_to_effect_months: number;
  duration_months?: number;
  delta_uncertainty: number;
}

export interface SimulationResult {
  n_runs: number;
  time_horizon_months: number;
  decision: DecisionDelta;
  success_probability: number;
  mean_happiness: number;
  median_happiness: number;
  p10_happiness: number;
  p90_happiness: number;
  mean_financial_index: number;
  mean_wellbeing_index: number;
  mean_career_index: number;
  mean_social_index: number;
  burnout_risk: number;
  financial_instability_risk: number;
  high_stress_risk: number;
  timeline_months: number[];
  happiness_p10: number[];
  happiness_p25: number[];
  happiness_p50: number[];
  happiness_p75: number[];
  happiness_p90: number[];
  financial_p10: number[];
  financial_p50: number[];
  financial_p90: number[];
  stress_p10: number[];
  stress_p50: number[];
  stress_p90: number[];
  top_factors: { factor: string; influence: number; direction: string }[];
  counterfactuals: any[];
}

export interface ExplanationData {
  summary: string;
  factor_attribution: { factor: string; influence: number; direction: string }[];
  risk_breakdown: {
    risk: string;
    probability: number;
    severity: string;
    description: string;
  }[];
  counterfactuals: {
    description: string;
    variable: string;
    change: number;
    new_success_prob: number;
    new_mean_happiness: number;
  }[];
  assumptions: {
    assumption: string;
    confidence: number;
    impact: string;
    editable: boolean;
  }[];
  narrative: string;
  regret_score: {
    score: number;
    interpretation: string;
    worst_case_happiness: number;
    expected_happiness: number;
  };
  disclaimer: string;
}

export interface EnsembleData {
  disagreement: {
    is_significant: boolean;
    score: number;
    details: string;
  };
  weights: {
    mc: number;
    causal: number;
    abm: number;
  };
}

export interface SimulationResponse {
  result: SimulationResult;
  ensemble: EnsembleData;
  explanation?: ExplanationData;
}

export interface OnboardingFormData {
  age: number;
  country: string;
  annual_income: number;
  monthly_expenses: number;
  total_savings: number;
  total_debt: number;
  income_type: string;
  industry: string;
  years_experience: number;
  education: string;
  num_skills: number;
  exercise_frequency: string;
  sleep_hours: number;
  chronic_conditions: boolean;
  relationship_status: string;
  num_dependents: number;
  social_circle_size: string;
  personality?: BigFiveVector;
  primary_goal: string;
  risk_tolerance: string;
  time_horizon_years: number;
}
