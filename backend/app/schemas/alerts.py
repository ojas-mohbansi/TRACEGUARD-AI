"""Alert schemas."""
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class AlertListItem(BaseModel):
    alert_id: str
    session_id: str
    timestamp: datetime
    engine: str
    severity: str
    risk_score: int
    prediction: str
    status: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: List[AlertListItem]
    total: int


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    investigation_notes: Optional[str] = None


class AlertDetailResponse(BaseModel):
    alert_id: str
    session_id: str
    timestamp: datetime
    engine: str
    severity: str
    risk_score: int
    prediction: str
    status: str
    fsm_result: Optional[Dict[str, Any]] = None
    ml_result: Optional[Dict[str, Any]] = None
    hybrid_result: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]] = []
    investigation_notes: Optional[str] = None

    class Config:
        from_attributes = True
