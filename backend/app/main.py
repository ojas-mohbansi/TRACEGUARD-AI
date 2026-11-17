# TraceGuard AI Backend
"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.api import auth, dashboard, simulation, events, alerts, detection, protocols, datasets, health, network, showcase, benchmark
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup and enforce security invariants."""
    Base.metadata.create_all(bind=engine)
    # Security Invariant: LOCAL_ACADEMIC_MODE requires loopback binding unless explicitly permitted
    if settings.LOCAL_ACADEMIC_MODE and not settings.ALLOW_PUBLIC_ACADEMIC_MODE:
        import sys
        cmd_args = " ".join(sys.argv)
        if "--host 0.0.0.0" in cmd_args or "--host=0.0.0.0" in cmd_args:
            raise RuntimeError(
                "SECURITY ERROR: TraceGuard AI is running in LOCAL_ACADEMIC_MODE but bound to public interface 0.0.0.0. "
                "Local academic mode must only bind to loopback (127.0.0.1 or localhost) to prevent unauthorized network access. "
                "To bind to public interfaces, set TRACEGUARD_MODE=PRODUCTION or ALLOW_PUBLIC_ACADEMIC_MODE=true."
            )
    yield


app = FastAPI(
    title="TraceGuard AI",
    description="AI-Powered Network Intrusion Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
cors_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
if "http://localhost:5173" not in cors_origins:
    cors_origins.append("http://localhost:5173")
if "http://127.0.0.1:5173" not in cors_origins:
    cors_origins.append("http://127.0.0.1:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(detection.router, prefix="/api/detection", tags=["Detection"])
app.include_router(protocols.router, prefix="/api/protocols", tags=["Protocols"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(showcase.router, prefix="/api/detection/showcase", tags=["Showcase"])
app.include_router(benchmark.router, prefix="/api/detection/benchmark", tags=["Academic Benchmark"])

# WebSocket
from app.api.websocket import router as ws_router
app.include_router(ws_router)
