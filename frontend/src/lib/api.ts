/**
 * Antigravity – API Client
 * Handles all communication with the FastAPI backend.
 */

import type {
    OnboardingFormData,
    UserState,
    DecisionDelta,
    SimulationResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            headers: { "Content-Type": "application/json", ...options.headers },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(error.detail || `API error: ${response.status}`);
        }

        return response.json();
    }

    /** Submit onboarding data and get initial state vector */
    async onboard(data: OnboardingFormData): Promise<{ state: UserState; summary: Record<string, number> }> {
        return this.request("/onboarding/", {
            method: "POST",
            body: JSON.stringify(data),
        });
    }

    /** Translate natural language decision to structured delta */
    async translateDecision(text: string): Promise<{
        original_text: string;
        delta: DecisionDelta;
        clarification_needed: string[];
    }> {
        return this.request("/decisions/translate", {
            method: "POST",
            body: JSON.stringify({ text }),
        });
    }

    /** Run Monte Carlo simulation */
    async runSimulation(
        state: UserState,
        decision: DecisionDelta,
        options?: {
            n_runs?: number;
            time_horizon_years?: number;
            include_explanation?: boolean;
            include_counterfactuals?: boolean;
        }
    ): Promise<SimulationResponse> {
        return this.request("/simulations/run", {
            method: "POST",
            body: JSON.stringify({
                state,
                decision,
                n_runs: options?.n_runs ?? 10000,
                time_horizon_years: options?.time_horizon_years ?? 5,
                include_explanation: options?.include_explanation ?? true,
                include_counterfactuals: options?.include_counterfactuals ?? false,
            }),
        });
    }

    /** Compare multiple decisions */
    async compareDecisions(
        state: UserState,
        decisions: DecisionDelta[],
        options?: { n_runs?: number; time_horizon_years?: number }
    ): Promise<{
        results: SimulationResponse[];
        recommendation: Record<string, any>;
    }> {
        return this.request("/simulations/compare", {
            method: "POST",
            body: JSON.stringify({
                state,
                decisions,
                n_runs: options?.n_runs ?? 5000,
                time_horizon_years: options?.time_horizon_years ?? 5,
            }),
        });
    }

    async submitFeedback(data: {
        actual_outcome: string;
        accuracy_rating: number;
        notes?: string;
    }): Promise<{ message: string }> {
        return this.request("/feedback/", {
            method: "POST",
            body: JSON.stringify(data),
        });
    }

    /** Get causal flow graph */
    async getCausalFlow(state: UserState, decision: DecisionDelta): Promise<{
        nodes: { id: string; label: string }[];
        edges: { source: string; target: string; weight: number; description: string; lag: number }[];
    }> {
        return this.request("/analysis/causal/flow", {
            method: "POST",
            body: JSON.stringify({ state, decision }),
        });
    }

    /** Get sensitivity tornado data */
    async getTornadoAnalysis(state: UserState, decision: DecisionDelta): Promise<{
        variable: string;
        low: number;
        high: number;
        total_swing: number;
    }[]> {
        return this.request("/analysis/sensitivity/tornado", {
            method: "POST",
            body: JSON.stringify({ state, decision }),
        });
    }
}

export const api = new ApiClient();
export default api;
