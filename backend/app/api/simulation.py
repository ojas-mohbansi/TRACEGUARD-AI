"""Simulation API router with workspace isolation and resource safeguards."""
from datetime import datetime
from uuid import uuid4
import asyncio
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Simulation
from app.schemas.simulation import (
    SimulationStartRequest, SimulationStartResponse,
    SimulationStopRequest, SimulationStopResponse
)
from app.simulator.generator import TrafficSimulator
from app.core.security import get_current_workspace_context, WorkspaceContext
from app.core.config import settings

router = APIRouter()

active_simulators: Dict[str, TrafficSimulator] = {}


@router.post("/start", response_model=SimulationStartResponse)
async def start_simulation(
    req: SimulationStartRequest,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Start generating simulated network traffic with safety boundaries and workspace scoping."""
    if not ctx.can_operate():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Viewer role cannot initiate traffic simulation"
        )

    # Resource guardrails: clamp event count
    event_count = min(req.event_count, settings.MAX_EVENTS_PER_SIMULATION)

    sim_id = f"sim_{uuid4().hex[:12]}"

    sim = Simulation(
        workspace_id=ctx.workspace_id,
        simulation_id=sim_id,
        mode=req.mode,
        config={
            "mode": req.mode,
            "event_count": event_count,
            "speed": req.speed,
            "anomaly_ratio": req.anomaly_ratio,
            "seed": req.seed
        },
        status="running",
        events_generated=0,
        started_at=datetime.utcnow()
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    simulator = TrafficSimulator(
        simulation_id=sim_id,
        mode=req.mode,
        event_count=event_count,
        speed=req.speed,
        anomaly_ratio=req.anomaly_ratio,
        seed=req.seed
    )
    active_simulators[sim_id] = simulator

    # Start simulation loop in background task
    asyncio.create_task(simulator.run())

    return SimulationStartResponse(
        simulation_id=sim_id,
        status="running",
        message=f"Simulation {sim_id} started in {req.mode} mode ({event_count} events limit)"
    )


@router.post("/stop", response_model=SimulationStopResponse)
async def stop_simulation(
    req: SimulationStopRequest,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Stop an active traffic simulation."""
    if not ctx.can_operate():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Viewer role cannot stop simulations"
        )

    sim_id = req.simulation_id
    events_gen = 0

    if sim_id in active_simulators:
        simulator = active_simulators[sim_id]
        simulator.stop()
        events_gen = simulator.generated_count
        del active_simulators[sim_id]

    sim = db.query(Simulation).filter(Simulation.simulation_id == sim_id).first()
    if sim:
        # Enforce workspace check
        if sim.workspace_id and sim.workspace_id != ctx.workspace_id and ctx.workspace_id != "default-workspace":
            raise HTTPException(status_code=403, detail="Access denied: Simulation belongs to another workspace")
        sim.status = "stopped"
        sim.events_generated = events_gen or sim.events_generated
        sim.stopped_at = datetime.utcnow()
        db.commit()

    return SimulationStopResponse(
        simulation_id=sim_id,
        status="stopped",
        events_generated=events_gen,
        message=f"Simulation {sim_id} stopped"
    )
