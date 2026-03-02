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

## Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/mayurbangera/altpath.git
cd altpath
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Download the spaCy NLP model (required)
python -m spacy download en_core_web_sm

# Create environment file
cp ../.env.example .env
# Or on Windows CMD: copy ..\.env.example .env
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Run the Application

Open **two terminals**:

**Terminal 1 — Backend** (port 8000):
```bash
cd backend
.\venv\Scripts\Activate.ps1   # or source venv/bin/activate on Mac/Linux
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs  (API documentation)
# → http://localhost:8000/health (Health check)
```

**Terminal 2 — Frontend** (port 3000):
```bash
cd frontend
npm run dev
# → http://localhost:3000
```

### 5. Verify Everything Works

- **Frontend**: Open [http://localhost:3000](http://localhost:3000) — you should see the AltPath landing page
- **Backend API Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs) — interactive Swagger UI
- **Health Check**: Open [http://localhost:8000/health](http://localhost:8000/health) — should return `{"status":"healthy"}`

### Environment Variables

The `.env` file (copied from `.env.example`) contains configuration for:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection (optional for demo) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection (optional) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama LLM server (optional) |
| `OLLAMA_MODEL` | `llama3` | LLM model name |
| `MONTE_CARLO_DEFAULT_RUNS` | `10000` | Default simulation runs |

> **Note:** The backend runs in demo/standalone mode without PostgreSQL, Redis, or Ollama. These are optional for enhanced functionality.

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
