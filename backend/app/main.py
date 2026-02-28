"""
Antigravity – Life Structure Simulation Engine
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import onboarding, decisions, simulations, results, feedback, analysis

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Simulate probable future trajectories under uncertainty.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ──────────────────────────────────────────────
app.include_router(
    onboarding.router,
    prefix=f"{settings.API_PREFIX}/onboarding",
    tags=["Onboarding"],
)
app.include_router(
    decisions.router,
    prefix=f"{settings.API_PREFIX}/decisions",
    tags=["Decisions"],
)
app.include_router(
    simulations.router,
    prefix=f"{settings.API_PREFIX}/simulations",
    tags=["Simulations"],
)
app.include_router(
    results.router,
    prefix=f"{settings.API_PREFIX}/results",
    tags=["Results"],
)
app.include_router(
    feedback.router,
    prefix=f"{settings.API_PREFIX}/feedback",
    tags=["Feedback"],
)
app.include_router(
    analysis.router,
    prefix=f"{settings.API_PREFIX}/analysis",
    tags=["Analysis"],
)


# ── Health Checks ────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to Antigravity – Life Structure Simulation Engine",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }
