# 🚀 Antigravity — Life Structure Simulation Engine

> Simulate probable future trajectories under uncertainty using decision science, probability, and systems modeling.

## What is Antigravity?

Antigravity converts life decisions into **measurable simulations**. It runs 10,000+ probabilistic scenarios across finance, health, career, and relationships — and explains exactly **why** outcomes happen.

**This is not a fortune teller. It's decision science infrastructure.**

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐
│  Next.js Frontend   │────▶│  FastAPI Backend  │
│  Tailwind + Recharts│     │  Python 3.11+    │
└─────────────────────┘     └────────┬─────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ▼                        ▼                        ▼
   ┌────────────────┐    ┌───────────────────┐    ┌───────────────────┐
   │ NLP Decision    │    │ Monte Carlo       │    │ Explainability    │
   │ Translation     │    │ Simulation Engine │    │ Engine            │
   │ (10 templates)  │    │ (SDE evolution)   │    │ (SHAP + CF + NR)  │
   └────────────────┘    └───────────────────┘    └───────────────────┘
```

## Features

- **24-Dimension State Model** — Life quantified across financial, career, health, social, and personality clusters
- **Monte Carlo Engine** — 10K+ simulations with SDE state evolution, domain interactions, and jump-diffusion events
- **NLP Decision Parser** — 10 pre-built templates for common life decisions
- **Non-Linear Domain Interactions** — Sigmoid saturation, mean-reverting stress, burnout dynamics
- **Multi-Level Explainability** — Executive summary, factor attribution, counterfactuals, narrative, regret scoring
- **Premium Dashboard** — Probability cone charts, stress trajectories, radar charts, risk breakdowns
- **Decision Comparison** — Compare up to 4 decisions side by side

## Quick Start

### Frontend (runs standalone with demo simulation)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Backend (with full simulation engine)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Recharts, Lucide Icons |
| Backend | Python 3.11, FastAPI, Pydantic, Uvicorn |
| Simulation | NumPy, SciPy, SDE-based Monte Carlo |
| NLP | Rule-based MVP (Ollama/Llama 3 upgrade path) |
| Explainability | SHAP-style attribution, counterfactual analysis |

## Project Structure

```
antigravity/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI entry point
│       ├── config.py               # Settings
│       ├── api/v1/                 # 5 API routers
│       ├── core/                   # State model, evolution, interactions
│       ├── simulation/             # Monte Carlo engine
│       ├── nlp/                    # Decision translator
│       └── explainability/         # Multi-level explanations
├── frontend/
│   └── src/
│       ├── app/                    # Next.js pages
│       │   ├── page.tsx            # Landing page
│       │   ├── onboarding/         # Multi-step form
│       │   └── dashboard/          # Simulation dashboard
│       └── lib/                    # Types + API client
└── README.md
```

## License

MIT
