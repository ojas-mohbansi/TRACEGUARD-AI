"""Dashboard schemas."""
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel


class EventByHour(BaseModel):
    hour: str
    count: int


class RecentThreat(BaseModel):
    alert_id: str
    severity: str
    session_id: str
    timestamp: datetime


class EngineDistribution(BaseModel):
    fsm: int = 0
    ml: int = 0
    hybrid: int = 0
    unknown: int = 0


class DashboardSummaryResponse(BaseModel):
    total_events: int
    active_sessions: int
    suspicious_sessions: int
    critical_alerts: int
    detection_rate: float
    avg_processing_time_ms: float
    events_by_hour: List[EventByHour]
    recent_threats: List[RecentThreat]
    engine_distribution: EngineDistribution
