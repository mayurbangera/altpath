"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Brain,
  ChartArea,
  Shield,
  Zap,
  GitBranch,
  Eye,
  ArrowRight,
  Sparkles,
} from "lucide-react";

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);

  const features = [
    {
      icon: <Brain size={28} />,
      title: "24-Dimension State Model",
      description:
        "Your life quantified across financial, career, health, social, and personality dimensions.",
      gradient: "from-indigo-500 to-purple-500",
    },
    {
      icon: <ChartArea size={28} />,
      title: "10,000+ Simulations",
      description:
        "Monte Carlo engine runs thousands of parallel futures with realistic uncertainty.",
      gradient: "from-emerald-500 to-teal-500",
    },
    {
      icon: <GitBranch size={28} />,
      title: "Decision Comparison",
      description:
        "Compare up to 4 life decisions side by side with probability distributions.",
      gradient: "from-amber-500 to-orange-500",
    },
    {
      icon: <Eye size={28} />,
      title: "Explainability Engine",
      description:
        "Understand WHY outcomes happen with SHAP analysis, counterfactuals, and narratives.",
      gradient: "from-cyan-500 to-blue-500",
    },
    {
      icon: <Shield size={28} />,
      title: "Risk Quantification",
      description:
        "Burnout risk, financial instability, stress trajectories — all probabilistically assessed.",
      gradient: "from-rose-500 to-pink-500",
    },
    {
      icon: <Zap size={28} />,
      title: "NLP Decision Parser",
      description:
        'Type "Should I quit my job?" and watch it transform into simulation parameters.',
      gradient: "from-violet-500 to-fuchsia-500",
    },
  ];

  return (
    <div className="relative min-h-screen" style={{ zIndex: 1 }}>
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
        <div
          className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3 rounded-2xl"
          style={{
            background: "rgba(10, 14, 26, 0.8)",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(99, 102, 241, 0.15)",
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: "var(--gradient-primary)" }}
            >
              <Sparkles size={22} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">
              AltPath
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#features"
              className="text-sm font-medium"
              style={{ color: "var(--text-secondary)" }}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-sm font-medium"
              style={{ color: "var(--text-secondary)" }}
            >
              How It Works
            </a>
            <Link href="/onboarding" className="btn-primary text-sm">
              Get Started <ArrowRight size={14} className="inline ml-1" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-40 pb-24 px-6">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8 animate-fade-in-up"
            style={{
              background: "rgba(99, 102, 241, 0.1)",
              border: "1px solid rgba(99, 102, 241, 0.3)",
              animationDelay: "0ms",
            }}
          >
            <span
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ background: "var(--accent-success)" }}
            ></span>
            <span
              className="text-sm font-medium"
              style={{ color: "var(--accent-primary)" }}
            >
              Decision Science × Probability × Systems Modeling
            </span>
          </div>

          {/* Title */}
          <h1
            className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 animate-fade-in-up"
            style={{
              animationDelay: "100ms",
              lineHeight: 1.1,
            }}
          >
            Simulate Your{" "}
            <span
              style={{
                background: "var(--gradient-primary)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Future
            </span>
            <br />
            Before You Live It
          </h1>

          {/* Subtitle */}
          <p
            className="text-lg md:text-xl max-w-2xl mx-auto mb-10 animate-fade-in-up"
            style={{
              color: "var(--text-secondary)",
              animationDelay: "200ms",
              lineHeight: 1.7,
            }}
          >
            Turn life decisions into{" "}
            <strong style={{ color: "var(--text-primary)" }}>
              measurable simulations
            </strong>
            . Run 10,000+ probabilistic scenarios across finance, health,
            career, and relationships — and understand exactly{" "}
            <strong style={{ color: "var(--text-primary)" }}>why</strong>{" "}
            outcomes happen.
          </p>

          {/* CTA Buttons */}
          <div
            className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up"
            style={{ animationDelay: "300ms" }}
          >
            <Link
              href="/onboarding"
              className="btn-primary text-lg px-10 py-4 flex items-center gap-2"
            >
              Start Simulation
              <ArrowRight size={18} />
            </Link>
            <Link href="/dashboard" className="btn-secondary text-lg px-10 py-4">
              View Demo
            </Link>
          </div>

          {/* Stats bar */}
          <div
            className="mt-16 grid grid-cols-3 gap-6 max-w-2xl mx-auto animate-fade-in-up"
            style={{ animationDelay: "500ms" }}
          >
            {[
              ["24", "Life Dimensions"],
              ["10K+", "Simulations / Run"],
              ["10", "Decision Templates"],
            ].map(([num, label]) => (
              <div key={label} className="text-center">
                <div
                  className="text-3xl font-bold"
                  style={{
                    background: "var(--gradient-primary)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  {num}
                </div>
                <div
                  className="text-xs mt-1 font-medium"
                  style={{ color: "var(--text-muted)" }}
                >
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Engineered for{" "}
              <span
                style={{
                  background: "var(--gradient-primary)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Serious Decisions
              </span>
            </h2>
            <p style={{ color: "var(--text-secondary)" }} className="text-lg">
              Not a chatbot. Not a fortune teller. Decision science
              infrastructure.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
            {features.map((feature, i) => (
              <div
                key={i}
                className="glass-card p-6 animate-fade-in-up cursor-default"
                style={{ opacity: 0, animationDelay: `${i * 100}ms` }}
                onMouseEnter={() => setHoveredFeature(i)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 bg-gradient-to-br ${feature.gradient}`}
                  style={{ opacity: hoveredFeature === i ? 1 : 0.8 }}
                >
                  <span className="text-white">{feature.icon}</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
          </div>

          <div className="space-y-8">
            {[
              {
                step: "01",
                title: "Onboard Your Life Data",
                desc: "Answer questions about your finances, career, health, relationships, and personality. We build your 24-dimension state vector.",
              },
              {
                step: "02",
                title: "Describe Your Decision",
                desc: 'Type naturally: "Should I quit my job and start a business?" Our NLP engine converts this into simulation parameters.',
              },
              {
                step: "03",
                title: "Run 10,000 Futures",
                desc: "Monte Carlo simulation with SDE state evolution, domain interactions, and rare event modeling runs thousands of parallel timelines.",
              },
              {
                step: "04",
                title: "Understand Your Outcomes",
                desc: "Get probability distributions, risk metrics, counterfactual analysis, and a narrative of your most likely future.",
              },
            ].map((item) => (
              <div key={item.step} className="glass-card p-6 flex gap-6 items-start">
                <div
                  className="text-4xl font-black shrink-0"
                  style={{
                    background: "var(--gradient-primary)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    opacity: 0.5,
                  }}
                >
                  {item.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p style={{ color: "var(--text-secondary)" }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-12 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div
            className="glass-card p-8"
            style={{
              borderColor: "rgba(245, 158, 11, 0.3)",
              background: "rgba(245, 158, 11, 0.05)",
            }}
          >
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--text-secondary)" }}
            >
              ⚠️ <strong>Important:</strong> AltPath is a probabilistic
              decision aid, not a prediction engine. It cannot foresee
              unpredictable events, emotional shifts, or black swan scenarios.
              Always consult qualified professionals for major life decisions.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 text-center">
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          © 2026 AltPath — Decision Science Infrastructure
        </p>
      </footer>
    </div>
  );
}
