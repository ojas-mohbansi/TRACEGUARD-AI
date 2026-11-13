"""Simulation schemas."""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SimulationStartRequest(BaseModel):
    mode: str = "mixed"  # normal | anomalous | mixed
    event_count: int = 100
    speed: float = 1.0
    anomaly_ratio: float = 0.2
    seed: Optional[int] = 42
    duration: Optional[int] = None


class SimulationStartResponse(BaseModel):
    simulation_id: str
    status: str = "running"
    message: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class SimulationStopRequest(BaseModel):
    simulation_id: str


class SimulationStopResponse(BaseModel):
    simulation_id: str
    status: str = "stopped"
    events_generated: int
    message: Optional[str] = None
