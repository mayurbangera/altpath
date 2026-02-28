"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, ArrowLeft, Sparkles, User, DollarSign, Briefcase, Heart, Brain } from "lucide-react";

type Step = "personal" | "financial" | "career" | "health" | "goals";

export default function OnboardingPage() {
    const router = useRouter();
    const [step, setStep] = useState<Step>("personal");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [form, setForm] = useState({
        age: 25,
        country: "US",
        annual_income: 50000,
        monthly_expenses: 3000,
        total_savings: 10000,
        total_debt: 5000,
        income_type: "salaried",
        industry: "technology",
        years_experience: 3,
        education: "bachelors",
        num_skills: 4,
        exercise_frequency: "moderate",
        sleep_hours: 7,
        chronic_conditions: false,
        relationship_status: "single",
        num_dependents: 0,
        social_circle_size: "medium",
        primary_goal: "",
        risk_tolerance: "moderate",
        time_horizon_years: 5,
    });

    const update = (key: string, val: any) => setForm((prev) => ({ ...prev, [key]: val }));

    const steps: { id: Step; label: string; icon: React.ReactNode }[] = [
        { id: "personal", label: "Personal", icon: <User size={18} /> },
        { id: "financial", label: "Financial", icon: <DollarSign size={18} /> },
        { id: "career", label: "Career", icon: <Briefcase size={18} /> },
        { id: "health", label: "Health & Social", icon: <Heart size={18} /> },
        { id: "goals", label: "Goals", icon: <Brain size={18} /> },
    ];

    const stepIdx = steps.findIndex((s) => s.id === step);
    const canGoBack = stepIdx > 0;
    const isLast = stepIdx === steps.length - 1;

    const handleSubmit = async () => {
        setIsSubmitting(true);
        // Store form data in sessionStorage and navigate to dashboard
        sessionStorage.setItem("antigravity_profile", JSON.stringify(form));
        router.push("/dashboard");
    };

    return (
        <div className="min-h-screen flex flex-col" style={{ zIndex: 1, position: "relative" }}>
            {/* Header */}
            <header className="px-6 py-4">
                <div className="max-w-3xl mx-auto flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                        <Sparkles size={18} className="text-white" />
                    </div>
                    <span className="text-lg font-bold">AltPath</span>
                    <span className="text-sm ml-2" style={{ color: "var(--text-muted)" }}>/ Onboarding</span>
                </div>
            </header>

            {/* Progress Steps */}
            <div className="px-6 py-6">
                <div className="max-w-3xl mx-auto flex items-center gap-2">
                    {steps.map((s, i) => (
                        <div key={s.id} className="flex items-center flex-1">
                            <button
                                onClick={() => setStep(s.id)}
                                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
                                style={{
                                    background: step === s.id ? "rgba(99, 102, 241, 0.15)" : "transparent",
                                    color: step === s.id ? "var(--accent-primary)" : i <= stepIdx ? "var(--text-primary)" : "var(--text-muted)",
                                    border: step === s.id ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
                                }}
                            >
                                {s.icon}
                                <span className="hidden sm:inline">{s.label}</span>
                            </button>
                            {i < steps.length - 1 && (
                                <div className="flex-1 h-px mx-2" style={{ background: i < stepIdx ? "var(--accent-primary)" : "var(--border-subtle)" }} />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Form Content */}
            <div className="flex-1 px-6 py-4">
                <div className="max-w-3xl mx-auto">
                    <div className="glass-card p-8 animate-fade-in-up">
                        {step === "personal" && (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-bold mb-2">Personal Information</h2>
                                <p style={{ color: "var(--text-secondary)" }} className="mb-6">Let&apos;s start with the basics to calibrate your simulation.</p>
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Age</label>
                                        <input type="number" className="input-field" value={form.age} onChange={(e) => update("age", +e.target.value)} min={16} max={100} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Country</label>
                                        <select className="select-field" value={form.country} onChange={(e) => update("country", e.target.value)}>
                                            <option value="US">United States</option>
                                            <option value="IN">India</option>
                                            <option value="DE">Germany</option>
                                            <option value="GB">United Kingdom</option>
                                            <option value="CA">Canada</option>
                                            <option value="AU">Australia</option>
                                            <option value="AE">UAE</option>
                                            <option value="SG">Singapore</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Relationship Status</label>
                                        <select className="select-field" value={form.relationship_status} onChange={(e) => update("relationship_status", e.target.value)}>
                                            <option value="single">Single</option>
                                            <option value="dating">Dating</option>
                                            <option value="married">Married</option>
                                            <option value="divorced">Divorced</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Number of Dependents</label>
                                        <input type="number" className="input-field" value={form.num_dependents} onChange={(e) => update("num_dependents", +e.target.value)} min={0} max={10} />
                                    </div>
                                </div>
                            </div>
                        )}

                        {step === "financial" && (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-bold mb-2">Financial Profile</h2>
                                <p style={{ color: "var(--text-secondary)" }} className="mb-6">Your financial baseline shapes the simulation&apos;s economics.</p>
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Annual Income ($)</label>
                                        <input type="number" className="input-field" value={form.annual_income} onChange={(e) => update("annual_income", +e.target.value)} min={0} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Monthly Expenses ($)</label>
                                        <input type="number" className="input-field" value={form.monthly_expenses} onChange={(e) => update("monthly_expenses", +e.target.value)} min={0} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Total Savings ($)</label>
                                        <input type="number" className="input-field" value={form.total_savings} onChange={(e) => update("total_savings", +e.target.value)} min={0} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Total Debt ($)</label>
                                        <input type="number" className="input-field" value={form.total_debt} onChange={(e) => update("total_debt", +e.target.value)} min={0} />
                                    </div>
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Income Type</label>
                                        <select className="select-field" value={form.income_type} onChange={(e) => update("income_type", e.target.value)}>
                                            <option value="salaried">Salaried / Full-time</option>
                                            <option value="freelance">Freelance</option>
                                            <option value="business">Business Owner</option>
                                            <option value="gig">Gig Worker</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        )}

                        {step === "career" && (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-bold mb-2">Career & Education</h2>
                                <p style={{ color: "var(--text-secondary)" }} className="mb-6">Your skills and career trajectory affect multiple life domains.</p>
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Industry</label>
                                        <select className="select-field" value={form.industry} onChange={(e) => update("industry", e.target.value)}>
                                            <option value="technology">Technology</option>
                                            <option value="finance">Finance</option>
                                            <option value="healthcare">Healthcare</option>
                                            <option value="education">Education</option>
                                            <option value="consulting">Consulting</option>
                                            <option value="manufacturing">Manufacturing</option>
                                            <option value="retail">Retail</option>
                                            <option value="creative">Creative / Media</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Years of Experience</label>
                                        <input type="number" className="input-field" value={form.years_experience} onChange={(e) => update("years_experience", +e.target.value)} min={0} max={50} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Education Level</label>
                                        <select className="select-field" value={form.education} onChange={(e) => update("education", e.target.value)}>
                                            <option value="high_school">High School</option>
                                            <option value="bachelors">Bachelor&apos;s Degree</option>
                                            <option value="masters">Master&apos;s Degree</option>
                                            <option value="phd">PhD / Doctorate</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Number of Marketable Skills</label>
                                        <input type="number" className="input-field" value={form.num_skills} onChange={(e) => update("num_skills", +e.target.value)} min={1} max={20} />
                                    </div>
                                </div>
                            </div>
                        )}

                        {step === "health" && (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-bold mb-2">Health & Social</h2>
                                <p style={{ color: "var(--text-secondary)" }} className="mb-6">Health and social connections profoundly affect life outcomes.</p>
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Exercise Frequency</label>
                                        <select className="select-field" value={form.exercise_frequency} onChange={(e) => update("exercise_frequency", e.target.value)}>
                                            <option value="none">None</option>
                                            <option value="light">Light (1-2x/week)</option>
                                            <option value="moderate">Moderate (3-4x/week)</option>
                                            <option value="heavy">Heavy (5+/week)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Average Sleep (hours)</label>
                                        <input type="number" className="input-field" value={form.sleep_hours} onChange={(e) => update("sleep_hours", +e.target.value)} min={3} max={12} step={0.5} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Social Circle</label>
                                        <select className="select-field" value={form.social_circle_size} onChange={(e) => update("social_circle_size", e.target.value)}>
                                            <option value="small">Small (&lt; 5 close friends)</option>
                                            <option value="medium">Medium (5-15)</option>
                                            <option value="large">Large (15+)</option>
                                        </select>
                                    </div>
                                    <div className="flex items-center gap-3 pt-6">
                                        <input type="checkbox" id="chronic" className="w-5 h-5 rounded accent-indigo-500" checked={form.chronic_conditions} onChange={(e) => update("chronic_conditions", e.target.checked)} />
                                        <label htmlFor="chronic" className="text-sm" style={{ color: "var(--text-secondary)" }}>I have a chronic health condition</label>
                                    </div>
                                </div>
                            </div>
                        )}

                        {step === "goals" && (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-bold mb-2">Goals & Risk</h2>
                                <p style={{ color: "var(--text-secondary)" }} className="mb-6">Final step — tell us what matters most to you.</p>
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Primary Life Goal</label>
                                        <input type="text" className="input-field" placeholder="e.g., Financial independence, Start a company, Better work-life balance..." value={form.primary_goal} onChange={(e) => update("primary_goal", e.target.value)} />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Risk Tolerance</label>
                                        <select className="select-field" value={form.risk_tolerance} onChange={(e) => update("risk_tolerance", e.target.value)}>
                                            <option value="very_low">Very Low — I hate uncertainty</option>
                                            <option value="low">Low — I prefer stability</option>
                                            <option value="moderate">Moderate — Balanced approach</option>
                                            <option value="high">High — I embrace calculated risks</option>
                                            <option value="very_high">Very High — Go big or go home</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Simulation Time Horizon</label>
                                        <select className="select-field" value={form.time_horizon_years} onChange={(e) => update("time_horizon_years", +e.target.value)}>
                                            <option value={1}>1 Year</option>
                                            <option value={3}>3 Years</option>
                                            <option value={5}>5 Years</option>
                                            <option value={10}>10 Years</option>
                                            <option value={20}>20 Years</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Navigation */}
                    <div className="flex items-center justify-between mt-6">
                        <button
                            className="btn-secondary flex items-center gap-2"
                            onClick={() => setStep(steps[stepIdx - 1]?.id)}
                            disabled={!canGoBack}
                            style={{ opacity: canGoBack ? 1 : 0.3 }}
                        >
                            <ArrowLeft size={16} /> Back
                        </button>
                        {isLast ? (
                            <button className="btn-primary flex items-center gap-2" onClick={handleSubmit} disabled={isSubmitting}>
                                {isSubmitting ? <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> : <><Sparkles size={16} /> Launch Simulation</>}
                            </button>
                        ) : (
                            <button className="btn-primary flex items-center gap-2" onClick={() => setStep(steps[stepIdx + 1].id)}>
                                Next <ArrowRight size={16} />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
