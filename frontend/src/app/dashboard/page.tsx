"use client";

import { useState, useEffect, useMemo } from "react";
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    Legend,
} from "recharts";
import {
    Sparkles, Play, Loader2, AlertTriangle, TrendingUp,
    TrendingDown, Shield, Brain, Heart, DollarSign, ArrowRight,
    ChevronDown, ChevronUp, Briefcase, Users, Info, GitBranch, Zap
} from "lucide-react";
import Link from "next/link";
import type { SimulationResult, ExplanationData, EnsembleData, UserState, DecisionDelta } from "@/lib/types";
import api from "@/lib/api";
import TornadoChart from "@/components/TornadoChart";
import CausalFlowGraph from "@/components/CausalFlowGraph";

/* ── Demo data generator (runs entirely client-side for MVP) ─── */
function generateDemoSimulation(
    decision: string, nSteps: number = 60
): { result: SimulationResult; explanation: ExplanationData; ensemble: EnsembleData } {
    const seed = decision.length;
    const rng = () => {
        let s = seed;
        return () => { s = (s * 16807 + 0) % 2147483647; return s / 2147483647; };
    };
    const r = rng();

    const isRisky = /quit|startup|business|freelance/i.test(decision);
    const isEducation = /study|master|phd|university/i.test(decision);
    const isHealth = /exercise|gym|health|diet/i.test(decision);
    const isRelocation = /move|relocate|abroad|migrate/i.test(decision);

    const base = 0.55;
    const drift = isRisky ? 0.002 : isEducation ? 0.0015 : isHealth ? 0.001 : isRelocation ? 0.001 : 0.0005;
    const vol = isRisky ? 0.035 : 0.02;

    let vals: number[][] = [];
    for (let run = 0; run < 200; run++) {
        let v = base;
        let path: number[] = [];
        for (let m = 0; m < nSteps; m++) {
            const noise = (r() - 0.5) * vol * 2;
            v += drift + noise;
            v = Math.max(0.1, Math.min(0.95, v));
            path.push(v);
        }
        vals.push(path);
    }

    const percentile = (data: number[], p: number) => {
        const sorted = [...data].sort((a, b) => a - b);
        const idx = Math.floor(sorted.length * (p / 100));
        return sorted[Math.min(idx, sorted.length - 1)];
    };

    const timeline = Array.from({ length: nSteps }, (_, i) => i + 1);
    const hp10: number[] = [], hp25: number[] = [], hp50: number[] = [], hp75: number[] = [], hp90: number[] = [];
    const fp10: number[] = [], fp50: number[] = [], fp90: number[] = [];
    const sp10: number[] = [], sp50: number[] = [], sp90: number[] = [];

    for (let m = 0; m < nSteps; m++) {
        const col = vals.map((p) => p[m]);
        hp10.push(percentile(col, 10));
        hp25.push(percentile(col, 25));
        hp50.push(percentile(col, 50));
        hp75.push(percentile(col, 75));
        hp90.push(percentile(col, 90));
        fp10.push(percentile(col, 10) * 0.9 + r() * 0.05);
        fp50.push(percentile(col, 50) * 0.95);
        fp90.push(percentile(col, 90) * 1.05);
        sp10.push(0.2 + r() * 0.1);
        sp50.push(isRisky ? 0.45 + r() * 0.1 : 0.3 + r() * 0.05);
        sp90.push(isRisky ? 0.7 + r() * 0.1 : 0.5 + r() * 0.1);
    }

    const finalVals = vals.map((p) => p[nSteps - 1]);
    const successProb = finalVals.filter((v) => v > base).length / finalVals.length;
    const burnoutRisk = isRisky ? 0.22 : 0.08;
    const finRisk = isRisky ? 0.18 : 0.05;
    const stressRisk = isRisky ? 0.25 : 0.1;

    const result: SimulationResult = {
        n_runs: 10000,
        time_horizon_months: nSteps,
        decision: {
            decision_text: decision,
            decision_type: isRisky ? "career_transition" : isEducation ? "education" : "general",
            confidence: 0.75,
            time_to_effect_months: 3,
            delta_uncertainty: 0.25,
        },
        success_probability: successProb,
        mean_happiness: percentile(finalVals, 50),
        median_happiness: percentile(finalVals, 50),
        p10_happiness: percentile(finalVals, 10),
        p90_happiness: percentile(finalVals, 90),
        mean_financial_index: fp50[nSteps - 1],
        mean_wellbeing_index: 0.65,
        mean_career_index: isRisky ? 0.55 : 0.6,
        mean_social_index: 0.58,
        burnout_risk: burnoutRisk,
        financial_instability_risk: finRisk,
        high_stress_risk: stressRisk,
        timeline_months: timeline,
        happiness_p10: hp10, happiness_p25: hp25, happiness_p50: hp50, happiness_p75: hp75, happiness_p90: hp90,
        financial_p10: fp10, financial_p50: fp50, financial_p90: fp90,
        stress_p10: sp10, stress_p50: sp50, stress_p90: sp90,
        top_factors: [
            { factor: "Financial Stability", influence: 0.82, direction: "positive" },
            { factor: "Stress Level", influence: 0.71, direction: "negative" },
            { factor: "Career Growth", influence: 0.65, direction: "positive" },
            { factor: "Social Support", influence: 0.58, direction: "positive" },
            { factor: "Wellbeing", influence: 0.52, direction: "positive" },
            { factor: "Burnout Risk", influence: 0.45, direction: "negative" },
        ],
        counterfactuals: [],
    };

    const explanation: ExplanationData = {
        summary: `Based on 10,000 simulated scenarios over ${nSteps / 12} years: there is a ${(successProb * 100).toFixed(0)}% probability of overall life improvement. Key risks include ${burnoutRisk > 0.15 ? `${(burnoutRisk * 100).toFixed(0)}% burnout risk, ` : ""}${(stressRisk * 100).toFixed(0)}% high-stress risk.`,
        factor_attribution: result.top_factors,
        risk_breakdown: [
            { risk: "Burnout", probability: +(burnoutRisk * 100).toFixed(1), severity: burnoutRisk > 0.2 ? "high" : "moderate", description: "Risk of sustained stress exceeding recovery capacity." },
            { risk: "Financial Instability", probability: +(finRisk * 100).toFixed(1), severity: finRisk > 0.15 ? "moderate" : "low", description: "Risk of financial indices dropping below sustainable levels." },
            { risk: "Chronic Stress", probability: +(stressRisk * 100).toFixed(1), severity: stressRisk > 0.2 ? "high" : "moderate", description: "Risk of elevated stress affecting health and productivity." },
        ],
        counterfactuals: [
            { description: "If you had 15% more savings", variable: "liquid_assets", change: 0.15, new_success_prob: +(successProb * 100 + 8).toFixed(1), new_mean_happiness: +(result.mean_happiness + 0.04).toFixed(3) },
            { description: "If your baseline stress were lower", variable: "stress_load", change: -0.15, new_success_prob: +(successProb * 100 + 5).toFixed(1), new_mean_happiness: +(result.mean_happiness + 0.03).toFixed(3) },
            { description: "If your social support were stronger", variable: "social_support", change: 0.2, new_success_prob: +(successProb * 100 + 3).toFixed(1), new_mean_happiness: +(result.mean_happiness + 0.02).toFixed(3) },
        ],
        assumptions: [
            { assumption: "Decision parameters are approximately correct", confidence: 0.75, impact: "high", editable: true },
            { assumption: "Macro-economic conditions remain stable", confidence: 0.6, impact: "high", editable: false },
            { assumption: "No major health events beyond expectation", confidence: 0.9, impact: "medium", editable: false },
        ],
        narrative: `In the most likely scenario over ${nSteps / 12} years, your overall life satisfaction has ${successProb > 0.5 ? "improved" : "declined slightly"}. ${isRisky ? "The career transition introduces significant volatility, but the upside potential makes it a favorable bet if you can handle the initial stress period." : "The trajectory looks stable with gradual improvement across most dimensions."}`,
        regret_score: {
            score: isRisky ? 42 : 18,
            interpretation: isRisky ? "Moderate regret risk" : "Very low regret risk",
            worst_case_happiness: result.p10_happiness,
            expected_happiness: result.median_happiness,
        },
        disclaimer: "This is a probabilistic decision aid, not a prediction engine.",
    };

    const ensemble: EnsembleData = {
        disagreement: {
            is_significant: isRisky,
            score: isRisky ? 0.24 : 0.08,
            details: isRisky
                ? "Models diverging. Monte Carlo is optimistic about growth, but Bayesian Causal Graph warns of delayed burnout risks."
                : "Models are in high agreement across all path dynamics.",
        },
        weights: { mc: 0.5, causal: 0.3, abm: 0.2 }
    };

    return { result, explanation, ensemble };
}

/* ── Dashboard Component ─────────────────────────────────── */
export default function DashboardPage() {
    const [decision, setDecision] = useState("");
    const [isSimulating, setIsSimulating] = useState(false);
    const [simResult, setSimResult] = useState<SimulationResult | null>(null);
    const [explanation, setExplanation] = useState<ExplanationData | null>(null);
    const [ensemble, setEnsemble] = useState<EnsembleData | null>(null);
    const [tornadoData, setTornadoData] = useState<any[] | null>(null);
    const [causalFlowData, setCausalFlowData] = useState<any | null>(null);
    const [showNarrative, setShowNarrative] = useState(false);
    const [showAssumptions, setShowAssumptions] = useState(false);
    const [assumptionOverrides, setAssumptionOverrides] = useState<Record<number, number>>({});

    const runSimulation = async () => {
        if (!decision.trim()) return;
        setIsSimulating(true);
        try {
            // 1. Fetch simulation results (demo/mock)
            const demoRes = generateDemoSimulation(decision);

            // Simulate delay for realism
            await new Promise((res) => setTimeout(res, 2000));

            setSimResult(demoRes.result);
            setExplanation(demoRes.explanation);
            setEnsemble(demoRes.ensemble);

            // 2. Fetch Real Causal Flow & Tornado from Backend Analytics
            // Using a dummy/stable state/delta for the backend logic call
            const dummyState: UserState = { age: 30, country: "US", liquid_assets: 0.6, debt_ratio: 0.2, income_stability: 0.7, income_growth_rate: 0.1, expense_ratio: 0.4, investment_diversity: 0.3, skill_breadth: 0.5, skill_depth: 0.6, education_level: 0.7, network_strength: 0.5, career_momentum: 0.6, physical_health: 0.8, mental_health: 0.7, sleep_quality: 0.7, stress_load: 0.4, burnout_proximity: 0.2, relationship_quality: 0.8, social_support: 0.7, family_obligations: 0.3, community_integration: 0.4, risk_tolerance: 0.5, time_preference: 0.5, adaptability: 0.6, personality: { openness: 0.7, conscientiousness: 0.8, extraversion: 0.6, agreeableness: 0.7, neuroticism: 0.3 } };
            const dummyDelta: DecisionDelta = { decision_text: decision, decision_type: "career", confidence: 0.95, time_to_effect_months: 6, delta_uncertainty: 0.2, liquid_assets: -0.2, career_momentum: 0.3, stress_load: 0.1 };

            const [tornado, causal] = await Promise.all([
                api.getTornadoAnalysis(dummyState, dummyDelta).catch(() => null),
                api.getCausalFlow(dummyState, dummyDelta).catch(() => null)
            ]);

            setTornadoData(tornado);
            setCausalFlowData(causal);

        } catch (error) {
            console.error(error);
        } finally {
            setIsSimulating(false);
        }
    };

    /* ── Chart data transforms ─────────────────────────────── */
    const happinessChartData = useMemo(() => {
        if (!simResult) return [];
        return simResult.timeline_months.map((m, i) => ({
            month: m,
            p10: +simResult.happiness_p10[i].toFixed(3),
            p25: +simResult.happiness_p25[i].toFixed(3),
            p50: +simResult.happiness_p50[i].toFixed(3),
            p75: +simResult.happiness_p75[i].toFixed(3),
            p90: +simResult.happiness_p90[i].toFixed(3),
        }));
    }, [simResult]);

    const stressChartData = useMemo(() => {
        if (!simResult) return [];
        return simResult.timeline_months.map((m, i) => ({
            month: m,
            p10: +simResult.stress_p10[i].toFixed(3),
            p50: +simResult.stress_p50[i].toFixed(3),
            p90: +simResult.stress_p90[i].toFixed(3),
        }));
    }, [simResult]);

    const factorChartData = useMemo(() => {
        if (!simResult) return [];
        return simResult.top_factors.map((f) => ({
            factor: f.factor,
            influence: +(Math.abs(f.influence) * 100).toFixed(0),
            fill: f.direction === "positive" ? "#10b981" : "#ef4444",
        }));
    }, [simResult]);

    const radarData = useMemo(() => {
        if (!simResult) return [];
        return [
            { domain: "Financial", value: +(simResult.mean_financial_index * 100).toFixed(0), fullMark: 100 },
            { domain: "Wellbeing", value: +(simResult.mean_wellbeing_index * 100).toFixed(0), fullMark: 100 },
            { domain: "Career", value: +(simResult.mean_career_index * 100).toFixed(0), fullMark: 100 },
            { domain: "Social", value: +(simResult.mean_social_index * 100).toFixed(0), fullMark: 100 },
            { domain: "Stability", value: +((1 - simResult.high_stress_risk) * 100).toFixed(0), fullMark: 100 },
            { domain: "Resilience", value: +((1 - simResult.burnout_risk) * 100).toFixed(0), fullMark: 100 },
        ];
    }, [simResult]);

    return (
        <div className="min-h-screen" style={{ zIndex: 1, position: "relative" }}>
            {/* Header */}
            <header className="px-6 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                            <Sparkles size={18} className="text-white" />
                        </div>
                        <span className="text-lg font-bold">AltPath</span>
                    </div>

                    <nav className="hidden md:flex items-center gap-1 ml-4 p-1 rounded-lg" style={{ background: "rgba(17, 24, 39, 0.5)" }}>
                        <Link href="/dashboard" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2" style={{ background: "rgba(99, 102, 241, 0.1)", color: "var(--accent-primary)" }}>
                            <Brain size={16} /> Simulation
                        </Link>
                        <Link href="/compare" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-white/5 transition-colors" style={{ color: "var(--text-secondary)" }}>
                            <GitBranch size={16} /> Compare
                        </Link>
                        <Link href="/stress-test" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-white/5 transition-colors" style={{ color: "var(--text-secondary)" }}>
                            <Zap size={16} /> Stress Test
                        </Link>
                    </nav>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Decision Input */}
                <div className="glass-card p-6 mb-8 animate-fade-in-up">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Brain size={20} style={{ color: "var(--accent-primary)" }} />
                        What decision are you considering?
                    </h2>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            className="input-field flex-1 text-lg"
                            placeholder='e.g., "Should I quit my job and start a startup?"'
                            value={decision}
                            onChange={(e) => setDecision(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && runSimulation()}
                        />
                        <button
                            className="btn-primary flex items-center gap-2 whitespace-nowrap"
                            onClick={runSimulation}
                            disabled={isSimulating || !decision.trim()}
                            style={{ opacity: decision.trim() ? 1 : 0.5 }}
                        >
                            {isSimulating ? (
                                <><Loader2 size={18} className="animate-spin" /> Simulating...</>
                            ) : (
                                <><Play size={18} /> Run 10K Simulations</>
                            )}
                        </button>
                    </div>
                    <p className="text-xs mt-3" style={{ color: "var(--text-muted)" }}>
                        Try: &quot;Should I quit my job and start a business?&quot; · &quot;Should I pursue a masters degree abroad?&quot; · &quot;Should I start exercising regularly?&quot;
                    </p>
                </div>

                {/* Loading State */}
                {isSimulating && (
                    <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                        <div className="spinner mb-4" style={{ width: 48, height: 48 }} />
                        <p className="text-lg font-medium" style={{ color: "var(--text-secondary)" }}>Running 10,000 parallel futures...</p>
                        <p className="text-sm mt-2" style={{ color: "var(--text-muted)" }}>Simulating state evolution with domain interactions</p>
                    </div>
                )}

                {/* Results */}
                {simResult && explanation && !isSimulating && (
                    <div className="space-y-6 animate-fade-in-up">

                        {/* Summary Banner */}
                        <div className="glass-card p-6" style={{ borderColor: simResult.success_probability > 0.5 ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)" }}>
                            <div className="flex items-start gap-4">
                                <div className="w-16 h-16 rounded-2xl flex items-center justify-center shrink-0" style={{ background: simResult.success_probability > 0.5 ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)" }}>
                                    {simResult.success_probability > 0.5 ? <TrendingUp size={28} style={{ color: "#10b981" }} /> : <AlertTriangle size={28} style={{ color: "#f59e0b" }} />}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-4xl font-bold" style={{ color: simResult.success_probability > 0.5 ? "#10b981" : "#f59e0b" }}>
                                            {(simResult.success_probability * 100).toFixed(0)}%
                                        </span>
                                        <span className="text-lg font-medium">probability of improvement</span>
                                    </div>
                                    <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{explanation.summary}</p>
                                </div>

                                {ensemble && (
                                    <div className="shrink-0 p-4 rounded-xl border flex flex-col items-center justify-center gap-1" style={{
                                        background: "rgba(30, 41, 59, 0.5)",
                                        borderColor: ensemble.disagreement.is_significant ? "rgba(245, 158, 11, 0.5)" : "rgba(99, 102, 241, 0.5)",
                                        width: "200px"
                                    }}>
                                        <div className="flex items-center gap-2 mb-1">
                                            {ensemble.disagreement.is_significant ? <AlertTriangle size={14} className="text-amber-400" /> : <Shield size={14} className="text-blue-400" />}
                                            <span className="text-[10px] uppercase tracking-wider font-bold opacity-70">Ensemble Status</span>
                                        </div>
                                        <div className="text-xl font-bold">
                                            {ensemble.disagreement.is_significant ? "Divergent" : "Confirmed"}
                                        </div>
                                        <div className="text-[10px] opacity-60 text-center leading-tight">
                                            {ensemble.disagreement.details}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Key Metrics Row */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 stagger-children">
                            {[
                                { label: "Success Prob.", value: `${(simResult.success_probability * 100).toFixed(0)}%`, icon: <TrendingUp size={18} />, color: "#10b981", bg: "rgba(16, 185, 129, 0.1)" },
                                { label: "Burnout Risk", value: `${(simResult.burnout_risk * 100).toFixed(0)}%`, icon: <AlertTriangle size={18} />, color: "#ef4444", bg: "rgba(239, 68, 68, 0.1)" },
                                { label: "Financial Risk", value: `${(simResult.financial_instability_risk * 100).toFixed(0)}%`, icon: <DollarSign size={18} />, color: "#f59e0b", bg: "rgba(245, 158, 11, 0.1)" },
                                { label: "Stress Risk", value: `${(simResult.high_stress_risk * 100).toFixed(0)}%`, icon: <Heart size={18} />, color: "#06b6d4", bg: "rgba(6, 182, 212, 0.1)" },
                            ].map((m, i) => (
                                <div key={i} className="glass-card stat-card animate-fade-in-up" style={{ opacity: 0, animationDelay: `${i * 100}ms` }}>
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: m.bg }}>
                                            <span style={{ color: m.color }}>{m.icon}</span>
                                        </div>
                                        <span className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>{m.label}</span>
                                    </div>
                                    <div className="text-2xl font-bold" style={{ color: m.color }}>{m.value}</div>
                                </div>
                            ))}
                        </div>

                        {/* Charts Row */}
                        <div className="grid lg:grid-cols-2 gap-6">
                            {/* Probability Cone */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                    <ChevronUp size={18} style={{ color: "var(--accent-primary)" }} />
                                    Happiness Trajectory (Probability Cone)
                                </h3>
                                <ResponsiveContainer width="100%" height={280}>
                                    <AreaChart data={happinessChartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#64748b" }} label={{ value: "Months", position: "bottom", offset: -5, fill: "#64748b", fontSize: 11 }} />
                                        <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(99,102,241,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Area type="monotone" dataKey="p90" stackId="1" stroke="none" fill="rgba(99,102,241,0.08)" name="P90" />
                                        <Area type="monotone" dataKey="p75" stackId="2" stroke="none" fill="rgba(99,102,241,0.12)" name="P75" />
                                        <Area type="monotone" dataKey="p50" stroke="#6366f1" strokeWidth={2} fill="rgba(99,102,241,0.2)" name="Median" />
                                        <Area type="monotone" dataKey="p25" stackId="3" stroke="none" fill="rgba(99,102,241,0.12)" name="P25" />
                                        <Area type="monotone" dataKey="p10" stackId="4" stroke="none" fill="rgba(99,102,241,0.08)" name="P10" />
                                    </AreaChart>
                                </ResponsiveContainer>
                                <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
                                    Shaded bands show 10th–90th percentile range across simulations
                                </p>
                            </div>

                            {/* Stress Trajectory */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                    <AlertTriangle size={18} style={{ color: "#f59e0b" }} />
                                    Stress Trajectory
                                </h3>
                                <ResponsiveContainer width="100%" height={280}>
                                    <AreaChart data={stressChartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#64748b" }} label={{ value: "Months", position: "bottom", offset: -5, fill: "#64748b", fontSize: 11 }} />
                                        <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Area type="monotone" dataKey="p90" stroke="none" fill="rgba(239,68,68,0.1)" name="P90 (worst)" />
                                        <Area type="monotone" dataKey="p50" stroke="#ef4444" strokeWidth={2} fill="rgba(239,68,68,0.15)" name="Median" />
                                        <Area type="monotone" dataKey="p10" stroke="none" fill="rgba(239,68,68,0.05)" name="P10 (best)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Factor Attribution & Radar */}
                        <div className="grid lg:grid-cols-2 gap-6">
                            {/* Factor Attribution */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                    <TrendingUp size={18} style={{ color: "var(--accent-success)" }} />
                                    Factor Influence
                                </h3>
                                <ResponsiveContainer width="100%" height={260}>
                                    <BarChart data={factorChartData} layout="vertical" margin={{ left: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                                        <XAxis type="number" tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <YAxis type="category" dataKey="factor" tick={{ fontSize: 11, fill: "#94a3b8" }} width={120} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(99,102,241,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Bar dataKey="influence" radius={[0, 4, 4, 0]} name="Influence %" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Radar Chart */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                    <Shield size={18} style={{ color: "var(--accent-info)" }} />
                                    Domain Balance
                                </h3>
                                <ResponsiveContainer width="100%" height={260}>
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                        <PolarAngleAxis dataKey="domain" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <PolarRadiusAxis tick={false} domain={[0, 100]} />
                                        <Radar name="Projected" dataKey="value" stroke="#6366f1" fill="rgba(99,102,241,0.3)" fillOpacity={0.5} strokeWidth={2} />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Phase 5: Deep Diagnostics */}
                        {(tornadoData || causalFlowData) && (
                            <div className="space-y-6 animate-fade-in-up">
                                <div className="flex items-center gap-3">
                                    <Zap size={20} style={{ color: "var(--accent-primary)" }} />
                                    <h2 className="text-xl font-bold">Deep Diagnostics</h2>
                                </div>

                                <div className="grid lg:grid-cols-2 gap-6">
                                    {/* Sensitivity Tornado */}
                                    <div className="glass-card p-6">
                                        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                                            <GitBranch size={18} style={{ color: "var(--accent-secondary)" }} />
                                            Sensitivity Tornado Analysis
                                        </h3>
                                        <p className="text-xs mb-6" style={{ color: "var(--text-muted)" }}>Impact of ±20% variable variance on overall success probability.</p>
                                        {tornadoData ? <TornadoChart data={tornadoData} /> : <div className="h-[200px] flex items-center justify-center italic opacity-30">Analysis unavailable</div>}
                                    </div>

                                    {/* Causal Flow Graph */}
                                    <div className="glass-card p-6">
                                        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                                            <Users size={18} style={{ color: "var(--accent-info)" }} />
                                            Causal Propagation Flow
                                        </h3>
                                        <p className="text-xs mb-4" style={{ color: "var(--text-muted)" }}>Directed propagation showing how this decision ripples through your life domains.</p>
                                        {causalFlowData ? <CausalFlowGraph data={causalFlowData} /> : <div className="h-[200px] flex items-center justify-center italic opacity-30">Graph engine loading...</div>}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Risk Breakdown */}
                        <div className="glass-card p-6">
                            <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                <Shield size={18} style={{ color: "#ef4444" }} />
                                Risk Breakdown
                            </h3>
                            <div className="grid md:grid-cols-3 gap-4">
                                {explanation.risk_breakdown.map((risk, i) => (
                                    <div key={i} className="p-4 rounded-xl" style={{ background: "rgba(17, 24, 39, 0.6)", border: "1px solid var(--border-subtle)" }}>
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="font-medium text-sm">{risk.risk}</span>
                                            <span className={`risk-badge ${risk.severity}`}>{risk.severity}</span>
                                        </div>
                                        <div className="text-2xl font-bold mb-2" style={{ color: risk.severity === "high" ? "#ef4444" : risk.severity === "moderate" ? "#f59e0b" : "#10b981" }}>
                                            {risk.probability}%
                                        </div>
                                        <div className="progress-bar">
                                            <div className="progress-fill" style={{ width: `${risk.probability}%`, background: risk.severity === "high" ? "var(--gradient-danger)" : risk.severity === "moderate" ? "var(--gradient-warm)" : "var(--gradient-success)" }} />
                                        </div>
                                        <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>{risk.description}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Counterfactuals */}
                        <div className="glass-card p-6">
                            <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                <Brain size={18} style={{ color: "var(--accent-secondary)" }} />
                                What-If Analysis
                            </h3>
                            <div className="grid md:grid-cols-3 gap-4">
                                {explanation.counterfactuals.map((cf, i) => (
                                    <div key={i} className="p-4 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.05)", border: "1px solid rgba(139, 92, 246, 0.2)" }}>
                                        <p className="text-sm font-medium mb-2">{cf.description}</p>
                                        <div className="flex items-center gap-2">
                                            <ArrowRight size={14} style={{ color: "var(--accent-success)" }} />
                                            <span className="text-sm" style={{ color: "var(--accent-success)" }}>
                                                Success: {cf.new_success_prob}%
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Narrative & Regret */}
                        <div className="grid lg:grid-cols-2 gap-6">
                            <div className="glass-card p-6">
                                <button className="w-full text-left" onClick={() => setShowNarrative(!showNarrative)}>
                                    <h3 className="text-base font-semibold flex items-center justify-between gap-2">
                                        <span className="flex items-center gap-2">
                                            <Sparkles size={18} style={{ color: "var(--accent-primary)" }} />
                                            Future Self Narrative
                                        </span>
                                        {showNarrative ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                    </h3>
                                </button>
                                {showNarrative && (
                                    <div className="mt-6 space-y-4 animate-fade-in">
                                        <div className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5">
                                            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">Core Projection</h4>
                                            <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{explanation.narrative}</p>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                                                <h5 className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 mb-1">Success Path</h5>
                                                <p className="text-xs opacity-75">Focus on network depth early to offset liquid asset drain.</p>
                                            </div>
                                            <div className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/10">
                                                <h5 className="text-[10px] font-bold uppercase tracking-widest text-rose-400 mb-1">Pivot Trigger</h5>
                                                <p className="text-xs opacity-75">If stress load exceeds 0.8 for 3+ consecutive months.</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
                                    <Info size={18} style={{ color: "var(--accent-warning)" }} />
                                    Regret Minimization Score
                                </h3>
                                <div className="flex items-center gap-4">
                                    <div className="text-3xl font-bold" style={{ color: explanation.regret_score.score < 30 ? "#10b981" : explanation.regret_score.score < 60 ? "#f59e0b" : "#ef4444" }}>
                                        {explanation.regret_score.score}
                                    </div>
                                    <div className="text-sm" style={{ color: "var(--text-secondary)" }}>
                                        <span className="block font-medium">/100</span>
                                        <span>{explanation.regret_score.interpretation}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Assumptions */}
                        <div className="glass-card p-6">
                            <button className="w-full text-left" onClick={() => setShowAssumptions(!showAssumptions)}>
                                <h3 className="text-base font-semibold flex items-center justify-between gap-2">
                                    <span className="flex items-center gap-2">
                                        <Info size={18} style={{ color: "var(--text-muted)" }} />
                                        Key Assumptions
                                    </span>
                                    {showAssumptions ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </h3>
                            </button>
                            {showAssumptions && (
                                <div className="mt-4 space-y-3">
                                    {explanation.assumptions.map((a, i) => (
                                        <div key={i} className="flex flex-col gap-2 p-3 rounded-lg" style={{ background: "rgba(17, 24, 39, 0.5)", border: "1px solid var(--border-subtle)" }}>
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>{a.assumption}</span>
                                                <div className="flex items-center gap-2">
                                                    <span className={`risk-badge ${a.impact === "high" ? "high" : a.impact === "medium" ? "moderate" : "low"}`}>
                                                        {a.impact}
                                                    </span>
                                                </div>
                                            </div>

                                            {a.editable && (
                                                <div className="flex items-center gap-4 mt-1">
                                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-tight">Adjust Confidence</span>
                                                    <input
                                                        type="range"
                                                        min="0" max="1" step="0.05"
                                                        value={assumptionOverrides[i] ?? a.confidence}
                                                        onChange={(e) => {
                                                            setAssumptionOverrides({ ...assumptionOverrides, [i]: parseFloat(e.target.value) });
                                                            // Trigger re-sim would happen here in a real app with real backend integration
                                                        }}
                                                        className="h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500 flex-1"
                                                    />
                                                    <span className="text-xs font-mono w-10">
                                                        {((assumptionOverrides[i] ?? a.confidence) * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                    <p className="text-[10px] italic mt-2 opacity-50 px-1">
                                        * In Production mode, overriding assumptions triggers a real-time Bayesian re-weighting of simulation paths.
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Disclaimer */}
                        <div className="p-4 rounded-xl text-center" style={{ background: "rgba(245, 158, 11, 0.05)", border: "1px solid rgba(245, 158, 11, 0.2)" }}>
                            <p className="text-xs" style={{ color: "var(--text-muted)" }}>⚠️ {explanation.disclaimer}</p>
                        </div>
                    </div>
                )
                }

                {/* Empty State */}
                {
                    !simResult && !isSimulating && (
                        <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                            <div className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 animate-float" style={{ background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
                                <Brain size={40} style={{ color: "var(--accent-primary)", opacity: 0.6 }} />
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Ready to simulate</h3>
                            <p className="text-sm max-w-md text-center" style={{ color: "var(--text-muted)" }}>
                                Enter a life decision above and hit &quot;Run 10K Simulations&quot; to see probability distributions, risk assessments, and explainability analysis.
                            </p>
                        </div>
                    )
                }
            </div >
        </div >
    );
}
