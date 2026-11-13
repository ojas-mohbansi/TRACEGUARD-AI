# TraceGuard AI Backend
"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.api import auth, dashboard, simulation, events, alerts, detection, protocols, datasets, health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TraceGuard AI",
    description="AI-Powered Network Intrusion Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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

# WebSocket
from app.api.websocket import router as ws_router
app.include_router(ws_router)
