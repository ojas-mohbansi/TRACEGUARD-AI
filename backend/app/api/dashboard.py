"""Dashboard statistics API router with workspace isolation and PostgreSQL/SQLite cross-compatibility."""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db, engine
from app.models.models import NetworkEvent, Alert
from app.schemas.dashboard import DashboardSummaryResponse, EventByHour, RecentThreat, EngineDistribution
from app.core.security import get_current_workspace_context, WorkspaceContext

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    time_range: Optional[str] = Query(None),
    include_demo: bool = Query(True),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Compute and return live dashboard metrics scoped to current workspace with optional time filtering."""
    if ctx.workspace_id == "default-workspace":
        event_filter = (NetworkEvent.workspace_id == ctx.workspace_id) | (NetworkEvent.workspace_id == None) | (NetworkEvent.workspace_id == "default-workspace")
        alert_filter = (Alert.workspace_id == ctx.workspace_id) | (Alert.workspace_id == None) | (Alert.workspace_id == "default-workspace")
    else:
        event_filter = (NetworkEvent.workspace_id == ctx.workspace_id)
        alert_filter = (Alert.workspace_id == ctx.workspace_id)

    if not include_demo:
        alert_filter = alert_filter & (Alert.dataset_id != "demo_showcase") & (~Alert.session_id.like("sess_demo_%"))
        event_filter = event_filter & (NetworkEvent.dataset_id != "demo_showcase") & (~NetworkEvent.session_id.like("sess_demo_%"))

    if time_range and time_range != "all":
        now = datetime.utcnow()
        if time_range == "1h":
            cutoff = now - timedelta(hours=1)
        elif time_range == "24h":
            cutoff = now - timedelta(hours=24)
        elif time_range == "7d":
            cutoff = now - timedelta(days=7)
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None

        if cutoff:
            event_filter = event_filter & (NetworkEvent.timestamp >= cutoff)
            alert_filter = alert_filter & (Alert.timestamp >= cutoff)

    total_events = db.query(NetworkEvent).filter(event_filter).count()
    active_sessions = db.query(func.count(func.distinct(NetworkEvent.session_id))).filter(event_filter).scalar() or 0

    # Suspicious sessions: count distinct sessions that have alerts or anomalous events
    suspicious_alerts_sessions = db.query(Alert.session_id).filter(
        alert_filter,
        (Alert.prediction == "anomalous") | (Alert.risk_score >= 50)
    ).distinct().subquery()
    suspicious_sessions = db.query(func.count(suspicious_alerts_sessions.c.session_id)).scalar() or 0

    critical_alerts = db.query(Alert).filter(alert_filter, Alert.severity == "critical").count()

    # Detection rate
    total_anomalous_events = db.query(NetworkEvent).filter(event_filter, NetworkEvent.label == "anomalous").count()
    if total_anomalous_events > 0:
        anomalous_sessions = db.query(func.count(func.distinct(NetworkEvent.session_id))).filter(
            event_filter,
            NetworkEvent.label == "anomalous"
        ).scalar() or 1
        detection_rate = round(min(1.0, suspicious_sessions / max(anomalous_sessions, 1)), 4)
    elif active_sessions > 0:
        detection_rate = round(suspicious_sessions / active_sessions, 4)
    else:
        detection_rate = 0.0

    # Average processing time
    avg_proc = db.query(func.avg(Alert.processing_time_ms)).filter(alert_filter).scalar()
    avg_processing_time_ms = round(float(avg_proc), 2) if avg_proc else 0.0

    # Events by hour (cross-dialect: sqlite strftime vs postgres to_char)
    is_postgres = "postgres" in str(engine.url)
    if is_postgres:
        date_expr = func.to_char(NetworkEvent.timestamp, "YYYY-MM-DD HH24:00").label("hour")
    else:
        date_expr = func.strftime("%Y-%m-%d %H:00", NetworkEvent.timestamp).label("hour")

    hourly_counts = (
        db.query(date_expr, func.count(NetworkEvent.id).label("count"))
        .filter(event_filter)
        .group_by("hour")
        .order_by("hour")
        .limit(24)
        .all()
    )
    events_by_hour = [EventByHour(hour=h or "00:00", count=c) for h, c in hourly_counts]

    # Recent threats
    recent_alerts = (
        db.query(Alert)
        .filter(alert_filter)
        .order_by(Alert.timestamp.desc())
        .limit(5)
        .all()
    )
    recent_threats = [
        RecentThreat(
            alert_id=a.alert_id,
            session_id=a.session_id,
            timestamp=a.timestamp,
            severity=a.severity
        )
        for a in recent_alerts
    ]

    # Engine distribution
    engine_counts = (
        db.query(Alert.engine, func.count(Alert.id))
        .filter(alert_filter)
        .group_by(Alert.engine)
        .all()
    )
    dist_map = {e.lower(): c for e, c in engine_counts if e}
    unknown_count = sum(c for e, c in engine_counts if not e or e.lower() not in ["fsm", "ml", "hybrid"])
    engine_distribution = EngineDistribution(
        fsm=dist_map.get("fsm", 0),
        ml=dist_map.get("ml", 0),
        hybrid=dist_map.get("hybrid", 0),
        unknown=unknown_count
    )

    return DashboardSummaryResponse(
        total_events=total_events,
        active_sessions=active_sessions,
        suspicious_sessions=suspicious_sessions,
        critical_alerts=critical_alerts,
        detection_rate=detection_rate,
        avg_processing_time_ms=avg_processing_time_ms,
        events_by_hour=events_by_hour,
        recent_threats=recent_threats,
        engine_distribution=engine_distribution
    )
