"""Academic Detection Engine Showcase API for TraceGuard AI.

Provides controlled, reproducible demonstration scenarios proving:
1. Normal Protocol Sequence (FSM=Normal, ML=Normal)
2. FSM-Only Protocol Violation (FSM=Violation/TRAP, ML=Normal) -> engine='fsm'
3. ML-Only Statistical Anomaly (FSM=Normal/Conforms, ML=Anomalous) -> engine='ml'
4. Combined Consensus Detection (FSM=Violation/TRAP, ML=Anomalous) -> engine='hybrid'

All records are tagged under dataset_id='demo_showcase' and session_id prefix 'sess_demo_'.
"""
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import NetworkEvent, Alert
from app.core.security import get_current_workspace_context, WorkspaceContext
from app.detection.fsm import FSMEngine
from app.detection.ml import MLEngine
from app.detection.hybrid import HybridEngine

logger = logging.getLogger(__name__)
router = APIRouter()

DEMO_DATASET_ID = "demo_showcase"


class ShowcaseRunRequest(BaseModel):
    scenario: str  # "normal" | "fsm_only" | "ml_only" | "hybrid"
    custom_notes: Optional[str] = None


@router.get("/scenarios")
def get_available_scenarios():
    """List the 4 academic demonstration scenarios and their theoretical basis."""
    return {
        "dataset_id": DEMO_DATASET_ID,
        "scenarios": [
            {
                "id": "normal",
                "name": "Scenario 1: Legitimate HTTP Session",
                "description": "Full compliance with canonical 9-state HTTP DFA and standard statistical profile.",
                "fsm_expected": "Conforms (S_FSM = 0.0, State=CLOSED)",
                "ml_expected": "Normal (S_ML < 0.50)",
                "hybrid_expected": "Normal (Low Risk)",
                "attribution": "none (no alert generated)"
            },
            {
                "id": "fsm_only",
                "name": "Scenario 2: Deterministic FSM Protocol Violation Only",
                "description": "Legitimate statistical traffic profile with an invalid DFA state transition into TRAP.",
                "fsm_expected": "Violation Detected (S_FSM = 1.0, State=TRAP, Min 60% floor)",
                "ml_expected": "Normal (S_ML < 0.50)",
                "hybrid_expected": "Attributed to FSM Engine (S_h >= 60%)",
                "attribution": "fsm"
            },
            {
                "id": "ml_only",
                "name": "Scenario 3: Statistical Machine Learning Anomaly Only",
                "description": "Sequence strictly conforms to HTTP DFA, but traffic exhibits extreme byte and rate outliers.",
                "fsm_expected": "Conforms (S_FSM = 0.0, State=CLOSED)",
                "ml_expected": "Statistical Outlier (S_ML >= 0.55)",
                "hybrid_expected": "Attributed to ML Engine",
                "attribution": "ml"
            },
            {
                "id": "hybrid",
                "name": "Scenario 4: Dual-Engine Hybrid Consensus",
                "description": "Protocol rule violation combined with statistical anomaly; consensus detection.",
                "fsm_expected": "Violation Detected (S_FSM = 1.0, State=TRAP)",
                "ml_expected": "Statistical Outlier (S_ML >= 0.55)",
                "hybrid_expected": "Consensus Attribution (S_h = 0.6*100 + 0.4*S_ML >= 80%)",
                "attribution": "hybrid"
            }
        ]
    }


def _create_showcase_events(scenario: str, session_id: str, workspace_id: str) -> List[NetworkEvent]:
    """Construct real event sequence for the requested academic scenario."""
    now = datetime.utcnow()
    events: List[NetworkEvent] = []

    if scenario == "normal":
        # Canonical 5-step sequence: IDLE -> CONNECTED -> REQUEST_RECEIVED -> AUTH_CHECKED -> RESPONSE_SENT -> CLOSED
        types_methods_bytes = [
            ("CONNECT", None, None, 64, 0),
            ("REQUEST", "GET", "api", 320, 20),
            ("AUTH_SUCCESS", None, None, 128, 40),
            ("RESPONSE_200", None, None, 1450, 70),
            ("CLOSE", None, None, 64, 110)
        ]
        for idx, (etype, method, path, bsize, offset_ms) in enumerate(types_methods_bytes):
            events.append(NetworkEvent(
                workspace_id=workspace_id,
                event_id=f"evt_demo_norm_{idx}_{uuid4().hex[:6]}",
                session_id=session_id,
                dataset_id=DEMO_DATASET_ID,
                timestamp=now + timedelta(milliseconds=offset_ms),
                protocol="HTTP",
                event_type=etype,
                source="192.168.1.150:49210",
                destination="10.0.0.1:80",
                method=method,
                path_category=path,
                status_code=200 if etype == "RESPONSE_200" else None,
                bytes=bsize,
                label="normal"
            ))

    elif scenario == "fsm_only":
        # Post-Close Request Violation:
        # CONNECT -> REQUEST -> AUTH_SUCCESS -> RESPONSE_200 -> CLOSE -> REQUEST (illegal transition from CLOSED)
        # Statistical profile is realistic and normal (moderate payload, standard inter-event intervals)
        types_methods_bytes = [
            ("CONNECT", None, None, 64, 0),
            ("REQUEST", "GET", "api", 320, 25),
            ("AUTH_SUCCESS", None, None, 128, 50),
            ("RESPONSE_200", None, None, 1450, 80),
            ("CLOSE", None, None, 64, 120),
            ("REQUEST", "GET", "api", 380, 160)  # Illegal in CLOSED state -> TRAP
        ]
        for idx, (etype, method, path, bsize, offset_ms) in enumerate(types_methods_bytes):
            events.append(NetworkEvent(
                workspace_id=workspace_id,
                event_id=f"evt_demo_fsm_{idx}_{uuid4().hex[:6]}",
                session_id=session_id,
                dataset_id=DEMO_DATASET_ID,
                timestamp=now + timedelta(milliseconds=offset_ms),
                protocol="HTTP",
                event_type=etype,
                source="192.168.1.175:51000",
                destination="10.0.0.1:80",
                method=method,
                path_category=path,
                status_code=200 if etype == "RESPONSE_200" else None,
                bytes=bsize,
                label="anomalous" if idx == 5 else "normal"
            ))

    elif scenario == "ml_only":
        # Conforms to DFA: CONNECT -> (REQUEST -> AUTH_FAILURE -> RESPONSE_401) * 6 -> CLOSE
        # Sequence strictly conforms to formal automaton rules (all transitions legal),
        # but exhibits extreme statistical anomaly (brute force authentication retry pattern)
        events.append(NetworkEvent(
            workspace_id=workspace_id,
            event_id=f"evt_demo_ml_0_{uuid4().hex[:6]}",
            session_id=session_id,
            dataset_id=DEMO_DATASET_ID,
            timestamp=now,
            protocol="HTTP",
            event_type="CONNECT",
            source="192.168.1.180:52300",
            destination="10.0.0.1:80",
            bytes=64,
            label="normal"
        ))
        for i in range(6):
            events.extend([
                NetworkEvent(
                    workspace_id=workspace_id,
                    event_id=f"evt_demo_ml_{i}_1_{uuid4().hex[:6]}",
                    session_id=session_id,
                    dataset_id=DEMO_DATASET_ID,
                    timestamp=now + timedelta(milliseconds=20*i + 5),
                    protocol="HTTP",
                    event_type="REQUEST",
                    source="192.168.1.180:52300",
                    destination="10.0.0.1:80",
                    method="POST",
                    path_category="login",
                    bytes=360,
                    label="anomalous"
                ),
                NetworkEvent(
                    workspace_id=workspace_id,
                    event_id=f"evt_demo_ml_{i}_2_{uuid4().hex[:6]}",
                    session_id=session_id,
                    dataset_id=DEMO_DATASET_ID,
                    timestamp=now + timedelta(milliseconds=20*i + 10),
                    protocol="HTTP",
                    event_type="AUTH_FAILURE",
                    source="192.168.1.180:52300",
                    destination="10.0.0.1:80",
                    bytes=0,
                    label="anomalous"
                ),
                NetworkEvent(
                    workspace_id=workspace_id,
                    event_id=f"evt_demo_ml_{i}_3_{uuid4().hex[:6]}",
                    session_id=session_id,
                    dataset_id=DEMO_DATASET_ID,
                    timestamp=now + timedelta(milliseconds=20*i + 15),
                    protocol="HTTP",
                    event_type="RESPONSE_401",
                    source="192.168.1.180:52300",
                    destination="10.0.0.1:80",
                    status_code=401,
                    bytes=210,
                    label="anomalous"
                ),
            ])
        events.append(NetworkEvent(
            workspace_id=workspace_id,
            event_id=f"evt_demo_ml_close_{uuid4().hex[:6]}",
            session_id=session_id,
            dataset_id=DEMO_DATASET_ID,
            timestamp=now + timedelta(milliseconds=135),
            protocol="HTTP",
            event_type="CLOSE",
            source="192.168.1.180:52300",
            destination="10.0.0.1:80",
            bytes=32,
            label="normal"
        ))

    elif scenario == "hybrid":
        # Out-of-order transition + massive burst exfiltration:
        # CONNECT -> RESPONSE_200 (direct response without request -> FSM Violation) + 9MB payload
        types_methods_bytes = [
            ("CONNECT", None, None, 64, 0),
            ("RESPONSE_200", None, None, 9200000, 25),  # Direct response (Illegal in CONNECTED) + 9.2MB
            ("REQUEST", "GET", "admin", 520, 50),
            ("RESPONSE_500", None, None, 840, 80),
            ("CLOSE", None, None, 64, 120)
        ]
        for idx, (etype, method, path, bsize, offset_ms) in enumerate(types_methods_bytes):
            events.append(NetworkEvent(
                workspace_id=workspace_id,
                event_id=f"evt_demo_hyb_{idx}_{uuid4().hex[:6]}",
                session_id=session_id,
                dataset_id=DEMO_DATASET_ID,
                timestamp=now + timedelta(milliseconds=offset_ms),
                protocol="HTTP",
                event_type=etype,
                source="192.168.1.199:53400",
                destination="10.0.0.1:80",
                method=method,
                path_category=path,
                status_code=200 if etype == "RESPONSE_200" else (500 if etype == "RESPONSE_500" else None),
                bytes=bsize,
                label="anomalous"
            ))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown showcase scenario '{scenario}'.")

    return events


@router.post("/run")
def execute_showcase_scenario(
    req: ShowcaseRunRequest,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Execute scenario through real detection engines and persist demonstration records."""
    scenario = req.scenario.lower()
    session_id = f"sess_demo_{scenario}_{uuid4().hex[:8]}"

    events = _create_showcase_events(scenario, session_id, ctx.workspace_id)
    db.add_all(events)
    db.commit()

    # Convert events for engine consumption
    event_dicts = [
        {
            "event_id": e.event_id,
            "session_id": e.session_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "protocol": e.protocol,
            "event_type": e.event_type,
            "source": e.source,
            "destination": e.destination,
            "method": e.method,
            "path_category": e.path_category,
            "status_code": e.status_code,
            "bytes": e.bytes,
            "label": e.label
        }
        for e in events
    ]

    # Instantiate real detection engines
    fsm_eng = FSMEngine()
    ml_eng = MLEngine()
    hybrid_eng = HybridEngine(fsm_engine=fsm_eng, ml_engine=ml_eng, fsm_weight=0.6, ml_weight=0.4)

    # 1. Independent FSM evaluation
    fsm_result = fsm_eng.validate_session(event_dicts)

    # 2. Independent ML evaluation
    ml_result = ml_eng.predict_session(event_dicts)

    # 3. Hybrid evaluation
    hybrid_result = hybrid_eng.detect_session(event_dicts)

    created_alert = None
    attribution = hybrid_result.get("attribution", "none")

    # If an alert is warranted, persist demonstration alert
    if attribution in ["fsm", "ml", "hybrid"]:
        created_alert = Alert(
            workspace_id=ctx.workspace_id,
            alert_id=f"alrt_demo_{scenario}_{uuid4().hex[:8]}",
            session_id=session_id,
            dataset_id=DEMO_DATASET_ID,
            timestamp=datetime.utcnow(),
            engine=attribution,
            severity=hybrid_result["severity"],
            risk_score=hybrid_result["risk_score"],
            prediction=hybrid_result["prediction"],
            status="new",
            summary=f"[SYNTHETIC DEMONSTRATION] {hybrid_result['explanation'][:220]}",
            fsm_result=fsm_result,
            ml_result=ml_result,
            hybrid_result=hybrid_result.get("hybrid_result"),
            responsible_events=hybrid_result.get("responsible_events", []),
            processing_time_ms=hybrid_result.get("processing_time_ms", 0.0),
            investigation_notes=req.custom_notes or f"Controlled demonstration run for scenario: {scenario}"
        )
        db.add(created_alert)
        db.commit()
        db.refresh(created_alert)

    return {
        "status": "success",
        "scenario": scenario,
        "session_id": session_id,
        "dataset_id": DEMO_DATASET_ID,
        "source_label": "SYNTHETIC DEMONSTRATION",
        "events_count": len(events),
        "fsm_evaluation": {
            "violation": fsm_result.get("fsm_violation", False),
            "risk_score": fsm_result.get("risk_score", 0),
            "final_state": fsm_result.get("final_state") or (fsm_result["transition_history"][-1]["to"] if fsm_result.get("transition_history") else "UNKNOWN"),
            "transitions": fsm_result.get("transition_history", []),
            "violations": fsm_result.get("violations", []),
            "explanation": fsm_result.get("explanation", "")
        },
        "ml_evaluation": {
            "prediction": ml_result.get("prediction", "normal"),
            "anomaly_score": ml_result.get("anomaly_score", 0.0),
            "risk_score": ml_result.get("risk_score", 0),
            "feature_importances": ml_result.get("feature_importances", {})
        },
        "hybrid_evaluation": {
            "attribution": attribution,
            "prediction": hybrid_result.get("prediction", "normal"),
            "combined_risk_score": hybrid_result.get("risk_score", 0),
            "severity": hybrid_result.get("severity", "low"),
            "formula": hybrid_result.get("hybrid_result", {}).get("formula", "0.6*S_FSM + 0.4*S_ML"),
            "floor_applied": hybrid_result.get("hybrid_result", {}).get("floor_applied", False),
            "explanation": hybrid_result.get("explanation", "")
        },
        "created_alert": {
            "alert_id": created_alert.alert_id,
            "engine": created_alert.engine,
            "severity": created_alert.severity,
            "risk_score": created_alert.risk_score
        } if created_alert else None
    }


@router.post("/reset")
def reset_showcase_data(
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Cleanly delete only demonstration records without altering real alerts or telemetry."""
    # Delete demo alerts
    demo_alerts = db.query(Alert).filter(
        Alert.workspace_id == ctx.workspace_id,
        (Alert.dataset_id == DEMO_DATASET_ID) | (Alert.session_id.like("sess_demo_%"))
    ).all()
    alerts_deleted = len(demo_alerts)
    for a in demo_alerts:
        db.delete(a)

    # Delete demo events
    demo_events = db.query(NetworkEvent).filter(
        NetworkEvent.workspace_id == ctx.workspace_id,
        (NetworkEvent.dataset_id == DEMO_DATASET_ID) | (NetworkEvent.session_id.like("sess_demo_%"))
    ).all()
    events_deleted = len(demo_events)
    for e in demo_events:
        db.delete(e)

    db.commit()

    return {
        "status": "success",
        "message": f"Demonstration data reset complete. Cleaned {alerts_deleted} demo alerts and {events_deleted} demo events.",
        "alerts_deleted": alerts_deleted,
        "events_deleted": events_deleted
    }
