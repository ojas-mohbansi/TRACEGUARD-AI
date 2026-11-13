"""Alerts API router with workspace isolation and RBAC."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Alert, NetworkEvent
from app.schemas.alerts import AlertListResponse, AlertListItem, AlertDetailResponse, AlertUpdate
from app.core.security import get_current_workspace_context, WorkspaceContext

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: Optional[str] = Query(None),
    engine: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """List security alerts isolated to current workspace."""
    query = db.query(Alert).filter(
        (Alert.workspace_id == ctx.workspace_id) | (Alert.workspace_id == None) | (Alert.workspace_id == "default-workspace")
    ) if ctx.workspace_id == "default-workspace" else db.query(Alert).filter(Alert.workspace_id == ctx.workspace_id)

    if severity:
        query = query.filter(Alert.severity == severity)
    if engine:
        query = query.filter(Alert.engine == engine)
    if status_filter:
        query = query.filter(Alert.status == status_filter)

    total = query.count()
    alerts = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()

    return AlertListResponse(
        alerts=[AlertListItem.model_validate(a) for a in alerts],
        total=total
    )


@router.get("/{alert_id}", response_model=AlertDetailResponse)
def get_alert_detail(
    alert_id: str,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Get full details of a specific alert with workspace boundary check."""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Enforce workspace isolation unless default-workspace backward compatibility
    if alert.workspace_id and alert.workspace_id != ctx.workspace_id and ctx.workspace_id != "default-workspace":
        raise HTTPException(status_code=403, detail="Access forbidden: Alert belongs to another workspace")

    # Fetch events associated with this session
    events = (
        db.query(NetworkEvent)
        .filter(NetworkEvent.session_id == alert.session_id)
        .order_by(NetworkEvent.timestamp.asc())
        .all()
    )

    serialized_events = []
    for ev in events:
        serialized_events.append({
            "event_id": ev.event_id,
            "session_id": ev.session_id,
            "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
            "event_type": ev.event_type,
            "method": ev.method,
            "status_code": ev.status_code,
            "bytes": ev.bytes,
        })

    alert_dict = {
        "id": alert.id,
        "alert_id": alert.alert_id,
        "session_id": alert.session_id,
        "dataset_id": getattr(alert, "dataset_id", None),
        "timestamp": alert.timestamp,
        "engine": alert.engine,
        "severity": alert.severity,
        "risk_score": alert.risk_score,
        "prediction": alert.prediction,
        "status": alert.status,
        "summary": getattr(alert, "summary", None),
        "fsm_result": getattr(alert, "fsm_result", None),
        "ml_result": getattr(alert, "ml_result", None),
        "hybrid_result": getattr(alert, "hybrid_result", None),
        "responsible_events": getattr(alert, "responsible_events", None) or [],
        "investigation_notes": getattr(alert, "investigation_notes", None),
        "processing_time_ms": getattr(alert, "processing_time_ms", None),
        "events": serialized_events,
    }
    return alert_dict


@router.patch("/{alert_id}", response_model=AlertDetailResponse)
def update_alert(
    alert_id: str,
    body: AlertUpdate,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Update alert status or investigation notes (Analyst, Admin, Owner)."""
    if not ctx.can_operate():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Viewer role cannot update alerts")

    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.workspace_id and alert.workspace_id != ctx.workspace_id and ctx.workspace_id != "default-workspace":
        raise HTTPException(status_code=403, detail="Access forbidden: Alert belongs to another workspace")

    if body.status is not None:
        alert.status = body.status
    if body.investigation_notes is not None:
        alert.investigation_notes = body.investigation_notes

    db.commit()
    db.refresh(alert)
    return get_alert_detail(alert_id, ctx, db)
