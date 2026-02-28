"use client";

import { useState, useMemo } from "react";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, Legend,
} from "recharts";
import {
    Sparkles, Zap, Play, Loader2, AlertTriangle, Shield, Skull,
    CloudLightning, Heart, TrendingDown, Activity, Brain, GitBranch
} from "lucide-react";
import Link from "next/link";

const BLACK_SWANS = [
    {
        id: "recession", label: "Economic Recession", icon: <TrendingDown size={20} />, color: "#f59e0b",
        description: "Global economic downturn: income drops, job instability, investment losses."
    },
    {
        id: "pandemic", label: "Pandemic", icon: <Skull size={20} />, color: "#ef4444",
        description: "Health crisis with isolation, social disruption, income impact."
    },
    {
        id: "health_crisis", label: "Personal Health Crisis", icon: <Heart size={20} />, color: "#ec4899",
        description: "Major health event: hospitalization, career pause, financial strain."
    },
    {
        id: "market_crash", label: "Market Crash", icon: <CloudLightning size={20} />, color: "#8b5cf6",
        description: "Severe market correction: investment losses, economic anxiety."
    },
    {
        id: "personal_crisis", label: "Personal Crisis", icon: <AlertTriangle size={20} />, color: "#06b6d4",
        description: "Relationship breakdown, family emergency, or existential crisis."
    },
];

function stressSimulate(decision: string, blackSwan: string, severity: number) {
    const isRisky = /quit|startup|business|freelance/i.test(decision);
    const baseSuccess = isRisky ? 0.65 : 0.72;
    const baseHappiness = isRisky ? 0.58 : 0.62;
    const baseBurnout = isRisky ? 0.18 : 0.08;
    const baseStress = isRisky ? 0.40 : 0.28;

    const impactMultipliers: Record<string, number> = {
        recession: 0.85, pandemic: 0.78, health_crisis: 0.75,
        market_crash: 0.82, personal_crisis: 0.72,
    };
    const mult = impactMultipliers[blackSwan] || 0.8;
    const impact = 1 - (1 - mult) * severity;

    const stressedSuccess = baseSuccess * impact;
    const stressedHappiness = baseHappiness * impact;
    const stressedBurnout = Math.min(0.95, baseBurnout + (1 - impact) * 0.35);
    const stressedStress = Math.min(0.95, baseStress + (1 - impact) * 0.3);

    const resilience = (stressedSuccess / baseSuccess) * 100;
    const antifragility = resilience > 85 ? "resilient" : resilience > 60 ? "moderately_fragile" : resilience > 40 ? "fragile" : "very_fragile";

    // Timeline data
    const nMonths = 36;
    const normalTimeline = Array.from({ length: nMonths }, (_, m) => {
        const progress = m / nMonths;
        return {
            month: m + 1,
            normal: +(baseHappiness + progress * 0.08 + (Math.random() - 0.5) * 0.02).toFixed(3),
            stressed: +(stressedHappiness - progress * 0.02 * severity + (Math.random() - 0.5) * 0.03
                + Math.max(0, (m - 12) / nMonths * 0.1)).toFixed(3),
        };
    });

    return {
        normal: { success: +(baseSuccess * 100).toFixed(1), happiness: +baseHappiness.toFixed(3), burnout: +(baseBurnout * 100).toFixed(1), stress: +(baseStress * 100).toFixed(1) },
        stressed: { success: +(stressedSuccess * 100).toFixed(1), happiness: +stressedHappiness.toFixed(3), burnout: +(stressedBurnout * 100).toFixed(1), stress: +(stressedStress * 100).toFixed(1) },
        impact: {
            successDrop: +((baseSuccess - stressedSuccess) * 100).toFixed(1),
            happinessDrop: +(baseHappiness - stressedHappiness).toFixed(3),
            burnoutIncrease: +((stressedBurnout - baseBurnout) * 100).toFixed(1),
        },
        resilience: +resilience.toFixed(1),
        antifragility,
        timeline: normalTimeline,
    };
}

export default function StressTestPage() {
    const [decision, setDecision] = useState("");
    const [selectedSwan, setSelectedSwan] = useState("recession");
    const [severity, setSeverity] = useState(0.5);
    const [isRunning, setIsRunning] = useState(false);
    const [result, setResult] = useState<ReturnType<typeof stressSimulate> | null>(null);

    const runTest = async () => {
        if (!decision.trim()) return;
        setIsRunning(true);
        await new Promise((r) => setTimeout(r, 1800));
        setResult(stressSimulate(decision, selectedSwan, severity));
        setIsRunning(false);
    };

    const swanInfo = BLACK_SWANS.find((s) => s.id === selectedSwan)!;

    const comparisonData = useMemo(() => {
        if (!result) return [];
        return [
            { metric: "Success %", Normal: result.normal.success, Stressed: result.stressed.success },
            { metric: "Stress %", Normal: result.normal.stress, Stressed: result.stressed.stress },
            { metric: "Burnout %", Normal: result.normal.burnout, Stressed: result.stressed.burnout },
        ];
    }, [result]);

    return (
        <div className="min-h-screen" style={{ zIndex: 1, position: "relative" }}>
            <header className="px-6 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                            <Sparkles size={18} className="text-white" />
                        </div>
                        <span className="text-lg font-bold">AltPath</span>
                    </div>

                    <nav className="hidden md:flex items-center gap-1 ml-4 p-1 rounded-lg" style={{ background: "rgba(17, 24, 39, 0.5)" }}>
                        <Link href="/dashboard" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-white/5 transition-colors" style={{ color: "var(--text-secondary)" }}>
                            <Brain size={16} /> Simulation
                        </Link>
                        <Link href="/compare" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-white/5 transition-colors" style={{ color: "var(--text-secondary)" }}>
                            <GitBranch size={16} /> Compare
                        </Link>
                        <Link href="/stress-test" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2" style={{ background: "rgba(245, 158, 11, 0.1)", color: "#f59e0b" }}>
                            <Zap size={16} /> Stress Test
                        </Link>
                    </nav>
                </div>
            </header>

            <div className="max-w-6xl mx-auto px-6 py-8">
                {/* Input Section */}
                <div className="glass-card p-6 mb-8 animate-fade-in-up">
                    <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
                        <Zap size={22} style={{ color: "#f59e0b" }} />
                        Black Swan Stress Testing
                    </h2>
                    <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
                        How robust is your decision under extreme scenarios? Inject a black swan event and see.
                    </p>

                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Decision to stress-test</label>
                            <input className="input-field" placeholder='e.g., "Should I quit my job and start a startup?"'
                                value={decision} onChange={(e) => setDecision(e.target.value)} />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>Select Black Swan Event</label>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                                {BLACK_SWANS.map((swan) => (
                                    <button key={swan.id} onClick={() => setSelectedSwan(swan.id)}
                                        className="p-3 rounded-xl text-left transition-all"
                                        style={{
                                            background: selectedSwan === swan.id ? `${swan.color}15` : "rgba(17, 24, 39, 0.5)",
                                            border: `1px solid ${selectedSwan === swan.id ? `${swan.color}50` : "var(--border-subtle)"}`,
                                        }}>
                                        <div style={{ color: swan.color }} className="mb-1">{swan.icon}</div>
                                        <div className="text-xs font-medium">{swan.label}</div>
                                    </button>
                                ))}
                            </div>
                            <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>{swanInfo.description}</p>
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>Severity</label>
                                <span className="text-sm font-bold" style={{
                                    color: severity < 0.3 ? "#10b981" : severity < 0.6 ? "#f59e0b" : "#ef4444"
                                }}>{(severity * 100).toFixed(0)}%</span>
                            </div>
                            <input type="range" min={0} max={1} step={0.05} value={severity}
                                onChange={(e) => setSeverity(+e.target.value)}
                                className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                                style={{ background: `linear-gradient(to right, #10b981, #f59e0b, #ef4444)` }} />
                            <div className="flex justify-between text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                                <span>Mild</span><span>Moderate</span><span>Extreme</span>
                            </div>
                        </div>

                        <button className="btn-primary flex items-center gap-2" onClick={runTest}
                            disabled={isRunning || !decision.trim()}>
                            {isRunning ? <><Loader2 size={16} className="animate-spin" /> Stress testing...</> : <><Zap size={16} /> Run Stress Test</>}
                        </button>
                    </div>
                </div>

                {/* Results */}
                {result && !isRunning && (
                    <div className="space-y-6 animate-fade-in-up">
                        {/* Resilience Banner */}
                        <div className="glass-card p-6" style={{
                            borderColor: result.resilience > 70 ? "rgba(16, 185, 129, 0.3)" : result.resilience > 40 ? "rgba(245, 158, 11, 0.3)" : "rgba(239, 68, 68, 0.3)",
                        }}>
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <Shield size={22} style={{ color: result.resilience > 70 ? "#10b981" : result.resilience > 40 ? "#f59e0b" : "#ef4444" }} />
                                        <span className="text-lg font-semibold">Resilience Score</span>
                                    </div>
                                    <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                                        {result.resilience > 70
                                            ? "This decision is robust under this stress scenario."
                                            : result.resilience > 40
                                                ? "This decision is moderately fragile — consider building more safety nets."
                                                : "This decision is very fragile under this scenario — consider alternatives."}
                                    </p>
                                </div>
                                <div className="text-right">
                                    <div className="text-4xl font-bold" style={{
                                        color: result.resilience > 70 ? "#10b981" : result.resilience > 40 ? "#f59e0b" : "#ef4444"
                                    }}>{result.resilience}%</div>
                                    <div className={`risk-badge mt-1 ${result.antifragility === "resilient" ? "low" :
                                        result.antifragility === "moderately_fragile" ? "moderate" : "high"
                                        }`}>
                                        {result.antifragility.replace("_", " ")}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Impact Cards */}
                        <div className="grid md:grid-cols-3 gap-4">
                            {[
                                { label: "Success Drop", value: `${result.impact.successDrop}%`, color: "#ef4444", icon: <TrendingDown size={18} /> },
                                { label: "Happiness Drop", value: result.impact.happinessDrop.toFixed(3), color: "#f59e0b", icon: <Activity size={18} /> },
                                { label: "Burnout Increase", value: `+${result.impact.burnoutIncrease}%`, color: "#ec4899", icon: <AlertTriangle size={18} /> },
                            ].map((m, i) => (
                                <div key={i} className="glass-card p-5">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span style={{ color: m.color }}>{m.icon}</span>
                                        <span className="text-sm" style={{ color: "var(--text-muted)" }}>{m.label}</span>
                                    </div>
                                    <div className="text-3xl font-bold" style={{ color: m.color }}>{m.value}</div>
                                </div>
                            ))}
                        </div>

                        <div className="grid lg:grid-cols-2 gap-6">
                            {/* Normal vs Stressed Bar Chart */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4">Normal vs Stressed Comparison</h3>
                                <ResponsiveContainer width="100%" height={260}>
                                    <BarChart data={comparisonData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                        <XAxis dataKey="metric" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(99,102,241,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Bar dataKey="Normal" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="Stressed" fill="#ef4444" radius={[4, 4, 0, 0]} />
                                        <Legend wrapperStyle={{ fontSize: 11 }} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Timeline Divergence */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4">Happiness Trajectory: Normal vs Stressed</h3>
                                <ResponsiveContainer width="100%" height={260}>
                                    <AreaChart data={result.timeline}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <YAxis domain={[0.3, 0.8]} tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(99,102,241,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Area type="monotone" dataKey="normal" stroke="#6366f1" fill="rgba(99,102,241,0.15)" strokeWidth={2} name="Normal" />
                                        <Area type="monotone" dataKey="stressed" stroke="#ef4444" fill="rgba(239,68,68,0.1)" strokeWidth={2} name="Stressed" strokeDasharray="5 5" />
                                        <Legend wrapperStyle={{ fontSize: 11 }} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {!result && !isRunning && (
                    <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                        <div className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 animate-float"
                            style={{ background: "rgba(245, 158, 11, 0.1)", border: "1px solid rgba(245, 158, 11, 0.2)" }}>
                            <Zap size={40} style={{ color: "#f59e0b", opacity: 0.6 }} />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Stress Test Your Decisions</h3>
                        <p className="text-sm max-w-md text-center" style={{ color: "var(--text-muted)" }}>
                            Select a decision and a black swan event. Adjust severity to see how your decision holds up under extreme conditions.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
