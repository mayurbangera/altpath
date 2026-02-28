"use client";

import { useState, useMemo } from "react";
import {
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Legend,
} from "recharts";
import {
    Sparkles, GitBranch, Play, Loader2, Plus, Trash2, Trophy, Shield, Brain, Zap
} from "lucide-react";
import Link from "next/link";

function quickSim(decision: string) {
    const isRisky = /quit|startup|business|freelance/i.test(decision);
    const isEdu = /study|master|phd|university|degree/i.test(decision);
    const isHealth = /exercise|gym|health|diet|yoga/i.test(decision);
    const base = 0.55;
    const r = () => Math.random();

    const success = isRisky ? 0.55 + r() * 0.3 : isEdu ? 0.6 + r() * 0.2 : isHealth ? 0.7 + r() * 0.2 : 0.5 + r() * 0.3;
    const fin = isRisky ? 0.4 + r() * 0.3 : 0.5 + r() * 0.3;
    const well = isHealth ? 0.65 + r() * 0.2 : 0.5 + r() * 0.25;
    const career = isRisky ? 0.45 + r() * 0.35 : isEdu ? 0.55 + r() * 0.25 : 0.5 + r() * 0.2;
    const social = 0.45 + r() * 0.3;
    const stress = isRisky ? 0.3 + r() * 0.3 : 0.15 + r() * 0.25;
    const burnout = isRisky ? 0.15 + r() * 0.2 : 0.05 + r() * 0.15;
    const happiness = success * 0.3 + (1 - stress) * 0.2 + well * 0.25 + social * 0.25;

    return {
        name: decision,
        success: +(success * 100).toFixed(0),
        financial: +(fin * 100).toFixed(0),
        wellbeing: +(well * 100).toFixed(0),
        career: +(career * 100).toFixed(0),
        social: +(social * 100).toFixed(0),
        stress: +(stress * 100).toFixed(0),
        burnout: +(burnout * 100).toFixed(0),
        stability: +((1 - stress) * 100).toFixed(0),
        resilience: +((1 - burnout) * 100).toFixed(0),
        happiness: +(happiness * 100).toFixed(0),
    };
}

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444"];

export default function ComparePage() {
    const [decisions, setDecisions] = useState<string[]>(["", ""]);
    const [results, setResults] = useState<ReturnType<typeof quickSim>[] | null>(null);
    const [isRunning, setIsRunning] = useState(false);

    const addDecision = () => {
        if (decisions.length < 4) setDecisions([...decisions, ""]);
    };
    const removeDecision = (i: number) => {
        if (decisions.length > 2) setDecisions(decisions.filter((_, idx) => idx !== i));
    };
    const updateDecision = (i: number, v: string) => {
        const copy = [...decisions];
        copy[i] = v;
        setDecisions(copy);
    };

    const runComparison = async () => {
        setIsRunning(true);
        await new Promise((res) => setTimeout(res, 1500));
        setResults(decisions.filter((d) => d.trim()).map((d) => quickSim(d)));
        setIsRunning(false);
    };

    const radarData = useMemo(() => {
        if (!results) return [];
        const dims = ["financial", "wellbeing", "career", "social", "stability", "resilience"] as const;
        return dims.map((d) => {
            const row: any = { domain: d.charAt(0).toUpperCase() + d.slice(1) };
            results.forEach((r, i) => { row[`decision_${i}`] = (r as any)[d]; });
            return row;
        });
    }, [results]);

    const barData = useMemo(() => {
        if (!results) return [];
        return results.map((r) => ({
            name: r.name.length > 25 ? r.name.slice(0, 25) + "…" : r.name,
            "Success %": r.success,
            "Happiness": r.happiness,
            "Stress %": r.stress,
        }));
    }, [results]);

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
                        <Link href="/compare" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2" style={{ background: "rgba(16, 185, 129, 0.1)", color: "#10b981" }}>
                            <GitBranch size={16} /> Compare
                        </Link>
                        <Link href="/stress-test" className="px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-white/5 transition-colors" style={{ color: "var(--text-secondary)" }}>
                            <Zap size={16} /> Stress Test
                        </Link>
                    </nav>
                </div>
            </header>

            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="glass-card p-6 mb-8 animate-fade-in-up">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <GitBranch size={22} style={{ color: "var(--accent-primary)" }} />
                        Compare Decisions Side by Side
                    </h2>
                    <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
                        Enter 2–4 alternative decisions to see how they stack up across all dimensions.
                    </p>

                    <div className="space-y-3">
                        {decisions.map((d, i) => (
                            <div key={i} className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-sm font-bold"
                                    style={{ background: `${COLORS[i]}22`, color: COLORS[i], border: `1px solid ${COLORS[i]}44` }}>
                                    {String.fromCharCode(65 + i)}
                                </div>
                                <input
                                    className="input-field flex-1"
                                    placeholder={`Decision ${String.fromCharCode(65 + i)}...`}
                                    value={d}
                                    onChange={(e) => updateDecision(i, e.target.value)}
                                />
                                {decisions.length > 2 && (
                                    <button onClick={() => removeDecision(i)} className="p-2 rounded-lg hover:bg-red-500/10 transition-colors">
                                        <Trash2 size={16} style={{ color: "#ef4444" }} />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="flex items-center gap-3 mt-4">
                        {decisions.length < 4 && (
                            <button onClick={addDecision} className="btn-secondary text-sm flex items-center gap-2">
                                <Plus size={14} /> Add Decision
                            </button>
                        )}
                        <button
                            className="btn-primary flex items-center gap-2"
                            onClick={runComparison}
                            disabled={isRunning || decisions.filter((d) => d.trim()).length < 2}
                        >
                            {isRunning ? <><Loader2 size={16} className="animate-spin" /> Comparing...</> : <><Play size={16} /> Compare</>}
                        </button>
                    </div>
                </div>

                {results && !isRunning && (
                    <div className="space-y-6 animate-fade-in-up">
                        {/* Winner Banner */}
                        {(() => {
                            const best = results.reduce((a, b) => a.success > b.success ? a : b);
                            const safest = results.reduce((a, b) => a.stress < b.stress ? a : b);
                            return (
                                <div className="grid md:grid-cols-2 gap-4">
                                    <div className="glass-card p-5" style={{ borderColor: "rgba(16, 185, 129, 0.3)" }}>
                                        <div className="flex items-center gap-3 mb-2">
                                            <Trophy size={20} style={{ color: "#10b981" }} />
                                            <span className="text-sm font-semibold" style={{ color: "#10b981" }}>Highest Success Probability</span>
                                        </div>
                                        <p className="font-medium">{best.name}</p>
                                        <p className="text-2xl font-bold mt-1" style={{ color: "#10b981" }}>{best.success}%</p>
                                    </div>
                                    <div className="glass-card p-5" style={{ borderColor: "rgba(6, 182, 212, 0.3)" }}>
                                        <div className="flex items-center gap-3 mb-2">
                                            <Shield size={20} style={{ color: "#06b6d4" }} />
                                            <span className="text-sm font-semibold" style={{ color: "#06b6d4" }}>Lowest Risk</span>
                                        </div>
                                        <p className="font-medium">{safest.name}</p>
                                        <p className="text-2xl font-bold mt-1" style={{ color: "#06b6d4" }}>{safest.stress}% stress</p>
                                    </div>
                                </div>
                            );
                        })()}

                        <div className="grid lg:grid-cols-2 gap-6">
                            {/* Radar Comparison */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4">Domain Balance Comparison</h3>
                                <ResponsiveContainer width="100%" height={320}>
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                        <PolarAngleAxis dataKey="domain" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <PolarRadiusAxis tick={false} domain={[0, 100]} />
                                        {results.map((_, i) => (
                                            <Radar key={i} name={results[i].name.slice(0, 20)} dataKey={`decision_${i}`}
                                                stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.15} strokeWidth={2} />
                                        ))}
                                        <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Bar Comparison */}
                            <div className="glass-card p-6">
                                <h3 className="text-base font-semibold mb-4">Key Metrics Comparison</h3>
                                <ResponsiveContainer width="100%" height={320}>
                                    <BarChart data={barData} layout="vertical" margin={{ left: 10 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#64748b" }} />
                                        <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }} width={100} />
                                        <Tooltip contentStyle={{ background: "#1a1f35", border: "1px solid rgba(99,102,241,0.3)", borderRadius: 8, fontSize: 12 }} />
                                        <Bar dataKey="Success %" fill="#6366f1" radius={[0, 4, 4, 0]} />
                                        <Bar dataKey="Happiness" fill="#10b981" radius={[0, 4, 4, 0]} />
                                        <Bar dataKey="Stress %" fill="#ef4444" radius={[0, 4, 4, 0]} />
                                        <Legend wrapperStyle={{ fontSize: 11 }} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Detail Cards */}
                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {results.map((r, i) => (
                                <div key={i} className="glass-card p-5" style={{ borderColor: `${COLORS[i]}33` }}>
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold"
                                            style={{ background: `${COLORS[i]}22`, color: COLORS[i] }}>
                                            {String.fromCharCode(65 + i)}
                                        </div>
                                        <span className="text-sm font-medium truncate">{r.name}</span>
                                    </div>
                                    <div className="space-y-2">
                                        {[
                                            { label: "Success", val: r.success, color: "#10b981" },
                                            { label: "Happiness", val: r.happiness, color: "#6366f1" },
                                            { label: "Burnout Risk", val: r.burnout, color: "#ef4444" },
                                            { label: "Stress", val: r.stress, color: "#f59e0b" },
                                        ].map((m) => (
                                            <div key={m.label}>
                                                <div className="flex justify-between text-xs mb-1">
                                                    <span style={{ color: "var(--text-muted)" }}>{m.label}</span>
                                                    <span style={{ color: m.color }}>{m.val}%</span>
                                                </div>
                                                <div className="progress-bar">
                                                    <div className="progress-fill" style={{ width: `${m.val}%`, background: m.color }} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="p-4 rounded-xl text-center" style={{ background: "rgba(245, 158, 11, 0.05)", border: "1px solid rgba(245, 158, 11, 0.2)" }}>
                            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                                ⚠️ The &quot;best&quot; decision depends on your personal risk tolerance and priorities. These are probabilistic estimates.
                            </p>
                        </div>
                    </div>
                )}

                {!results && !isRunning && (
                    <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                        <div className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 animate-float"
                            style={{ background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
                            <GitBranch size={40} style={{ color: "var(--accent-primary)", opacity: 0.6 }} />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Compare alternative futures</h3>
                        <p className="text-sm max-w-md text-center" style={{ color: "var(--text-muted)" }}>
                            Enter two or more decisions above to see radar charts, success probabilities, and risk profiles compared side by side.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
