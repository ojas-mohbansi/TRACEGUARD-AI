"""Alerts API router with workspace isolation and RBAC."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.models import Alert, NetworkEvent
from app.schemas.alerts import AlertListResponse, AlertListItem, AlertDetailResponse, AlertUpdate
from app.core.security import get_current_workspace_context, WorkspaceContext

router = APIRouter()


@router.get("/analytics")
def get_alert_analytics(
    time_range: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    engine: Optional[str] = Query(None),
    dataset_filter: Optional[str] = Query("all"),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Compute rich threat triage and forensic distribution analytics from actual alert and event records.
    Provides:
    1. Final Alert Attribution (Mutually Exclusive)
    2. Component Detection Contributions (Overlapping)
    3. FSM Protocol Violation Analytics (States, Symbols, TRAP transitions)
    """
    query = db.query(Alert).filter(
        (Alert.workspace_id == ctx.workspace_id) | (Alert.workspace_id == None) | (Alert.workspace_id == "default-workspace")
    ) if ctx.workspace_id == "default-workspace" else db.query(Alert).filter(Alert.workspace_id == ctx.workspace_id)

    if dataset_filter and dataset_filter != "all":
        if dataset_filter == "benchmark":
            query = query.filter(Alert.dataset_id == "academic_benchmark")
        elif dataset_filter == "pcap":
            query = query.filter(Alert.dataset_id.like("%pcap%") | Alert.session_id.like("%pcap%"))
        elif dataset_filter == "live_historical":
            query = query.filter((Alert.dataset_id != "academic_benchmark") | (Alert.dataset_id == None))
        elif dataset_filter == "showcase":
            query = query.filter(Alert.dataset_id == "demo_showcase")

    if severity and severity != "all":
        query = query.filter(Alert.severity == severity)
    if engine and engine != "all":
        query = query.filter(Alert.engine == engine)

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
            query = query.filter(Alert.timestamp >= cutoff)

    alerts = query.order_by(Alert.timestamp.desc()).all()
    total_alerts = len(alerts)

    # 1. Severity Distribution
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    # 2. Engine Distribution (Final Attribution)
    eng_counts = {"fsm": 0, "ml": 0, "hybrid": 0, "unknown": 0}
    # 3. Risk Distribution (0-25, 26-50, 51-75, 76-100)
    risk_bands = {"0-25 (Low)": 0, "26-50 (Med)": 0, "51-75 (High)": 0, "76-100 (Crit)": 0}
    # 4. FSM vs ML correlation
    correlation = {"fsm_only": 0, "ml_only": 0, "hybrid_overlap": 0}
    # 5. Timeline / time series (hour or day)
    time_bins: Dict[str, int] = {}

    # Component evaluations vs detections (Overlapping)
    fsm_evals = 0
    fsm_violations = 0
    ml_evals = 0
    ml_anomalies = 0

    # FSM Violation Invariant Breakdown
    violations_by_state: Dict[str, int] = {}
    violations_by_symbol: Dict[str, int] = {}
    trap_transitions_count = 0

    total_risk = 0
    for a in alerts:
        # Severity
        s = (a.severity or "low").lower()
        if s in sev_counts:
            sev_counts[s] += 1

        # Engine Attribution
        e = (a.engine or "").lower()
        if e in ["fsm", "ml", "hybrid"]:
            eng_counts[e] += 1
        else:
            eng_counts["unknown"] += 1

        # Risk score
        r = a.risk_score or 0
        total_risk += r
        if r <= 25:
            risk_bands["0-25 (Low)"] += 1
        elif r <= 50:
            risk_bands["26-50 (Med)"] += 1
        elif r <= 75:
            risk_bands["51-75 (High)"] += 1
        else:
            risk_bands["76-100 (Crit)"] += 1

        # Overlapping Component Contributions
        f_res = a.fsm_result or {}
        m_res = a.ml_result or {}
        has_fsm_viol = bool(f_res.get("fsm_violation") or a.engine == "fsm")
        has_ml_anom = bool(m_res.get("prediction") == "anomalous" or (m_res.get("anomaly_score") or 0) >= 0.55 or a.engine == "ml")

        fsm_evals += 1
        if has_fsm_viol:
            fsm_violations += 1
            trap_transitions_count += 1
            # Extract state and symbol
            viols = f_res.get("violations", [])
            v0 = viols[0] if viols else {}
            st = v0.get("previous_state") or v0.get("current_state") or "CONNECTED"
            sym = v0.get("incoming_event") or "UNKNOWN"
            violations_by_state[st] = violations_by_state.get(st, 0) + 1
            violations_by_symbol[sym] = violations_by_symbol.get(sym, 0) + 1

        ml_evals += 1
        if has_ml_anom:
            ml_anomalies += 1

        # Correlation
        if has_fsm_viol and has_ml_anom:
            correlation["hybrid_overlap"] += 1
        elif has_fsm_viol:
            correlation["fsm_only"] += 1
        elif has_ml_anom:
            correlation["ml_only"] += 1
        else:
            if e == "fsm":
                correlation["fsm_only"] += 1
            elif e == "ml":
                correlation["ml_only"] += 1
            else:
                correlation["hybrid_overlap"] += 1

        # Time series bin
        if a.timestamp:
            hour_str = a.timestamp.strftime("%Y-%m-%d %H:00")
            time_bins[hour_str] = time_bins.get(hour_str, 0) + 1

    # Sorted time series
    time_series = [{"timestamp": k, "count": v} for k, v in sorted(time_bins.items())]

    # Extract distinct FSM detection evidence items
    fsm_evidence = []
    for a in alerts:
        fsm_res = a.fsm_result or {}
        if fsm_res.get("fsm_violation") or a.engine == "fsm":
            violations = fsm_res.get("violations", [])
            v_info = violations[0] if violations else {}
            trans_hist = fsm_res.get("transition_history", [])
            last_trans = trans_hist[-1] if trans_hist else {}

            if a.dataset_id == "academic_benchmark":
                src = "SYNTHETIC ACADEMIC BENCHMARK"
            elif a.dataset_id == "demo_showcase" or (a.session_id and "demo" in a.session_id):
                src = "SYNTHETIC DEMONSTRATION"
            elif a.dataset_id and "pcap" in a.dataset_id.lower():
                src = "PCAP REPLAY"
            elif a.session_id and "pkt_" in a.session_id:
                src = "LIVE NETWORK"
            else:
                src = "SYNTHETIC SIMULATION"

            fsm_evidence.append({
                "alert_id": a.alert_id,
                "session_id": a.session_id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "rule_violated": v_info.get("violation_reason") or fsm_res.get("explanation") or "Protocol state violation",
                "previous_state": v_info.get("previous_state") or v_info.get("current_state") or last_trans.get("from") or "CONNECTED",
                "input_symbol": v_info.get("incoming_event") or last_trans.get("event") or "UNKNOWN",
                "next_state": "TRAP",
                "expected_transitions": v_info.get("expected_transitions", []),
                "explanation": fsm_res.get("explanation") or a.summary or "",
                "risk_score": a.risk_score,
                "hybrid_score": (a.hybrid_result or {}).get("combined_risk_score", a.risk_score),
                "source_type": src,
                "severity": a.severity,
                "engine": a.engine
            })

    # Protocol distribution
    protocol_distribution = [
        {"protocol": "HTTP/1.1", "count": total_alerts, "percentage": 100.0 if total_alerts > 0 else 0.0}
    ]

    avg_risk = round(total_risk / max(total_alerts, 1), 1)

    # Component contributions
    component_contributions = {
        "fsm": {
            "name": "Deterministic FSM Engine",
            "evaluations": fsm_evals,
            "detections": fsm_violations,
            "detection_rate": round(fsm_violations / max(fsm_evals, 1), 4),
            "detection_type": "Protocol Violations (DFA Invariant)"
        },
        "ml": {
            "name": "Statistical ML Engine",
            "evaluations": ml_evals,
            "detections": ml_anomalies,
            "detection_rate": round(ml_anomalies / max(ml_evals, 1), 4),
            "detection_type": "Isolation Forest Outliers"
        },
        "hybrid": {
            "name": "Hybrid Consensus Engine",
            "evaluations": total_alerts,
            "detections": eng_counts["hybrid"],
            "detection_rate": round(eng_counts["hybrid"] / max(total_alerts, 1), 4),
            "detection_type": "Dual-Engine Consensus"
        }
    }

    # Format violations by state and symbol for charts
    fsm_state_distribution = [{"state": k, "count": v} for k, v in sorted(violations_by_state.items(), key=lambda x: -x[1])]
    fsm_symbol_distribution = [{"symbol": k, "count": v} for k, v in sorted(violations_by_symbol.items(), key=lambda x: -x[1])]

    return {
        "total_alerts": total_alerts,
        "avg_risk_score": avg_risk,
        "severity_distribution": sev_counts,
        "engine_distribution": eng_counts,
        "risk_distribution": risk_bands,
        "engine_correlation": correlation,
        "component_contributions": component_contributions,
        "fsm_violation_analytics": {
            "total_violations": fsm_violations,
            "trap_transitions_count": trap_transitions_count,
            "by_state": fsm_state_distribution,
            "by_symbol": fsm_symbol_distribution
        },
        "time_series": time_series,
        "protocol_distribution": protocol_distribution,
        "fsm_evidence": fsm_evidence[:50]
    }


@router.get("/engine-activity")
def get_engine_activity(
    time_range: Optional[str] = Query("all"),
    include_demo: bool = Query(True),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """
    Returns two separate analytical metrics:
    1. Final Alert Attribution (mutually exclusive: fsm, ml, hybrid, unknown - sums to total alerts)
    2. Engine Contribution & Activity (overlapping event & component evaluations)
    """
    query = db.query(Alert).filter(
        (Alert.workspace_id == ctx.workspace_id) | (Alert.workspace_id == None) | (Alert.workspace_id == "default-workspace")
    ) if ctx.workspace_id == "default-workspace" else db.query(Alert).filter(Alert.workspace_id == ctx.workspace_id)

    if not include_demo:
        query = query.filter(Alert.dataset_id != "demo_showcase", ~Alert.session_id.like("sess_demo_%"))

    if time_range and time_range != "all":
        now = datetime.utcnow()
        if time_range == "24h":
            cutoff = now - timedelta(hours=24)
        elif time_range == "7d":
            cutoff = now - timedelta(days=7)
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None
        if cutoff:
            query = query.filter(Alert.timestamp >= cutoff)

    alerts = query.all()
    total_alerts = len(alerts)

    # 1. Final Alert Attribution (Mutually Exclusive)
    attribution = {"fsm": 0, "ml": 0, "hybrid": 0, "unknown": 0}
    for a in alerts:
        eng = (a.engine or "").lower()
        if eng in attribution:
            attribution[eng] += 1
        else:
            attribution["unknown"] += 1

    # 2. Engine Contribution / Evaluation Activity (Overlapping)
    fsm_evals = 0
    fsm_violations = 0
    ml_evals = 0
    ml_anomalies = 0
    hybrid_evals = total_alerts
    hybrid_consensus = attribution["hybrid"]

    for a in alerts:
        f_res = a.fsm_result or {}
        m_res = a.ml_result or {}
        if f_res or a.engine == "fsm" or a.engine == "hybrid":
            fsm_evals += 1
            if f_res.get("fsm_violation") or a.engine == "fsm":
                fsm_violations += 1

        if m_res or a.engine == "ml" or a.engine == "hybrid":
            ml_evals += 1
            if m_res.get("prediction") == "anomalous" or (m_res.get("anomaly_score") or 0) >= 0.55 or a.engine == "ml":
                ml_anomalies += 1

    return {
        "final_attribution": {
            **attribution,
            "total": total_alerts
        },
        "engine_activity": {
            "fsm": {
                "name": "Deterministic FSM Engine",
                "evaluations": max(fsm_evals, fsm_violations),
                "detections": fsm_violations,
                "detection_type": "Protocol Violations (DFA Invariant)",
                "color": "#06b6d4"
            },
            "ml": {
                "name": "Statistical ML Engine",
                "evaluations": max(ml_evals, ml_anomalies),
                "detections": ml_anomalies,
                "detection_type": "Isolation Forest Outliers",
                "color": "#a855f7"
            },
            "hybrid": {
                "name": "Hybrid Consensus Engine",
                "evaluations": hybrid_evals,
                "detections": hybrid_consensus,
                "detection_type": "Dual-Engine Consensus",
                "color": "#10b981"
            }
        },
        "definitions": {
            "attribution": "Mutually exclusive final classification assigned to each alert. Sums strictly to total alert count.",
            "activity": "Total event sessions evaluated and component anomalies flagged by each engine. Detections may overlap across engines."
        }
    }



@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: Optional[str] = Query(None),
    engine: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    dataset_filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """List security alerts isolated to current workspace."""
    query = db.query(Alert).filter(
        (Alert.workspace_id == ctx.workspace_id) | (Alert.workspace_id == None) | (Alert.workspace_id == "default-workspace")
    ) if ctx.workspace_id == "default-workspace" else db.query(Alert).filter(Alert.workspace_id == ctx.workspace_id)

    if dataset_filter and dataset_filter != "all":
        if dataset_filter == "benchmark":
            query = query.filter(Alert.dataset_id == "academic_benchmark")
        elif dataset_filter == "pcap":
            query = query.filter(Alert.dataset_id.like("%pcap%") | Alert.session_id.like("%pcap%"))
        elif dataset_filter == "live_historical":
            query = query.filter((Alert.dataset_id != "academic_benchmark") | (Alert.dataset_id == None))
        elif dataset_filter == "showcase":
            query = query.filter(Alert.dataset_id == "demo_showcase")

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

    fsm_res = getattr(alert, "fsm_result", None) or {}
    ml_res = getattr(alert, "ml_result", None) or {}
    fsm_violation = fsm_res.get("fsm_violation", False) if isinstance(fsm_res, dict) else False
    ml_score = ml_res.get("ml_anomaly_score", ml_res.get("anomaly_score", 0.0)) if isinstance(ml_res, dict) else 0.0

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
        "fsm_violation": fsm_violation,
        "ml_anomaly_score": round(float(ml_score), 4),
        "responsible_events": getattr(alert, "responsible_events", None) or [],
        "investigation_notes": getattr(alert, "investigation_notes", None),
        "processing_time_ms": getattr(alert, "processing_time_ms", None),
        "fsm_result": fsm_res,
        "ml_result": ml_res,
        "hybrid_result": getattr(alert, "hybrid_result", None),
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
