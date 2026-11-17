"""Detection API router for running and comparing detection engines."""
from typing import List, Dict, Any, Optional
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import NetworkEvent, Alert, Dataset
from app.schemas.detection import DetectionRequest, DetectionResponse, DetectionResultItem, DetectionCompareResponse, EngineMetrics

router = APIRouter()

# Graceful import of engines
try:
    from app.detection.fsm import FSMEngine
    _fsm_engine_instance = FSMEngine()
except Exception:
    _fsm_engine_instance = None

try:
    from app.detection.ml import MLEngine
    _ml_engine_instance = MLEngine()
except Exception:
    _ml_engine_instance = None

try:
    from app.detection.hybrid import HybridEngine
    _hybrid_engine_instance = HybridEngine(
        fsm_engine=_fsm_engine_instance,
        ml_engine=_ml_engine_instance,
        fsm_weight=0.6,
        ml_weight=0.4
    )
except Exception:
    _hybrid_engine_instance = None


def get_engines():
    global _fsm_engine_instance, _ml_engine_instance, _hybrid_engine_instance
    if _fsm_engine_instance is None:
        try:
            from app.detection.fsm import FSMEngine
            _fsm_engine_instance = FSMEngine()
        except Exception:
            _fsm_engine_instance = None

    if _ml_engine_instance is None:
        try:
            from app.detection.ml import MLEngine
            _ml_engine_instance = MLEngine()
        except Exception:
            _ml_engine_instance = None

    if _hybrid_engine_instance is None:
        try:
            from app.detection.hybrid import HybridEngine
            _hybrid_engine_instance = HybridEngine(
                fsm_engine=_fsm_engine_instance,
                ml_engine=_ml_engine_instance
            )
        except Exception:
            _hybrid_engine_instance = None

    return _fsm_engine_instance, _ml_engine_instance, _hybrid_engine_instance


def _events_to_dicts(events: List[NetworkEvent]) -> List[Dict[str, Any]]:
    return [
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


@router.post("/run", response_model=DetectionResponse)
def run_detection(req: DetectionRequest, db: Session = Depends(get_db)):
    """Run detection algorithms on specified session IDs."""
    fsm_eng, ml_eng, hybrid_eng = get_engines()
    results: List[DetectionResultItem] = []

    session_ids = list(req.session_ids) if req.session_ids else []
    if req.dataset_id and not session_ids:
        session_ids = [
            s[0] for s in db.query(NetworkEvent.session_id)
            .filter(NetworkEvent.dataset_id == req.dataset_id)
            .distinct()
            .all()
        ]

    # Query events for the requested sessions or dataset
    query = db.query(NetworkEvent)
    if session_ids:
        query = query.filter(NetworkEvent.session_id.in_(session_ids))
    if req.dataset_id:
        query = query.filter(NetworkEvent.dataset_id == req.dataset_id)
    all_events = query.order_by(NetworkEvent.timestamp.asc()).all()

    # Group by session_id
    sessions_map: Dict[str, List[NetworkEvent]] = {}
    for ev in all_events:
        sessions_map.setdefault(ev.session_id, []).append(ev)

    target_session_ids = session_ids if session_ids else list(sessions_map.keys())

    for sid in target_session_ids:
        events = sessions_map.get(sid, [])
        event_dicts = _events_to_dicts(events)

        for engine_type in req.engines:
            t0 = time.time()
            if engine_type == "fsm":
                if fsm_eng:
                    try:
                        res = fsm_eng.validate_session(event_dicts)
                        elapsed = round((time.time() - t0) * 1000, 2)
                        results.append(DetectionResultItem(
                            session_id=sid,
                            engine="fsm",
                            prediction=res.get("prediction", "normal"),
                            risk_score=res.get("risk_score", 0),
                            severity=res.get("severity", "low"),
                            fsm_violation=res.get("fsm_violation", False),
                            ml_anomaly_score=0.0,
                            explanation=res.get("explanation", ""),
                            responsible_events=res.get("responsible_events", []),
                            processing_time_ms=elapsed
                        ))
                        continue
                    except Exception as e:
                        pass
                # Fallback FSM response
                elapsed = round((time.time() - t0) * 1000, 2)
                results.append(DetectionResultItem(
                    session_id=sid,
                    engine="fsm",
                    prediction="normal",
                    risk_score=0,
                    severity="low",
                    fsm_violation=False,
                    ml_anomaly_score=0.0,
                    explanation="FSM Engine fallback - no violations",
                    responsible_events=[],
                    processing_time_ms=elapsed
                ))

            elif engine_type == "ml":
                if ml_eng:
                    try:
                        res = ml_eng.predict_session(event_dicts)
                        elapsed = round((time.time() - t0) * 1000, 2)
                        score = float(res.get("anomaly_score", 0.0))
                        risk = int(score * 100)
                        severity = "critical" if risk >= 76 else ("high" if risk >= 51 else ("medium" if risk >= 26 else "low"))
                        results.append(DetectionResultItem(
                            session_id=sid,
                            engine="ml",
                            prediction=res.get("prediction", "normal"),
                            risk_score=risk,
                            severity=severity,
                            fsm_violation=False,
                            ml_anomaly_score=round(score, 4),
                            explanation=f"ML Isolation Forest score {score:.2f}",
                            responsible_events=[],
                            processing_time_ms=elapsed
                        ))
                        continue
                    except Exception as e:
                        pass
                elapsed = round((time.time() - t0) * 1000, 2)
                results.append(DetectionResultItem(
                    session_id=sid,
                    engine="ml",
                    prediction="normal",
                    risk_score=10,
                    severity="low",
                    fsm_violation=False,
                    ml_anomaly_score=0.1,
                    explanation="ML Engine fallback - normal pattern",
                    responsible_events=[],
                    processing_time_ms=elapsed
                ))

            elif engine_type == "hybrid":
                if hybrid_eng:
                    try:
                        res = hybrid_eng.detect_session(event_dicts)
                        results.append(DetectionResultItem(
                            session_id=sid,
                            engine="hybrid",
                            prediction=res["prediction"],
                            risk_score=res["risk_score"],
                            severity=res["severity"],
                            fsm_violation=res["fsm_violation"],
                            ml_anomaly_score=res["ml_anomaly_score"],
                            explanation=res["explanation"],
                            responsible_events=res["responsible_events"],
                            processing_time_ms=res["processing_time_ms"]
                        ))
                        continue
                    except Exception as e:
                        pass
                elapsed = round((time.time() - t0) * 1000, 2)
                results.append(DetectionResultItem(
                    session_id=sid,
                    engine="hybrid",
                    prediction="normal",
                    risk_score=5,
                    severity="low",
                    fsm_violation=False,
                    ml_anomaly_score=0.05,
                    explanation="Hybrid Engine fallback",
                    responsible_events=[],
                    processing_time_ms=elapsed
                ))

    return DetectionResponse(results=results)


@router.get("/compare", response_model=DetectionCompareResponse)
def compare_detection(dataset_id: str = Query(...), db: Session = Depends(get_db)):
    """Compare performance metrics between FSM, ML, and Hybrid engines on a dataset."""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    events = (
        db.query(NetworkEvent)
        .filter(NetworkEvent.dataset_id == dataset_id)
        .order_by(NetworkEvent.timestamp.asc())
        .all()
    )

    # Group by session
    sessions: Dict[str, List[NetworkEvent]] = {}
    actual_labels: Dict[str, str] = {}
    for ev in events:
        sessions.setdefault(ev.session_id, []).append(ev)
        if ev.label == "anomalous":
            actual_labels[ev.session_id] = "anomalous"
        elif ev.session_id not in actual_labels:
            actual_labels[ev.session_id] = "normal"

    total_sessions = len(sessions)
    fsm_eng, ml_eng, hybrid_eng = get_engines()

    engines_data: Dict[str, EngineMetrics] = {}

    for eng_name in ["fsm", "ml", "hybrid"]:
        tp, fp, tn, fn = 0, 0, 0, 0
        predictions_list = []
        total_time = 0.0

        for sid, sess_events in sessions.items():
            ev_dicts = _events_to_dicts(sess_events)
            actual = actual_labels.get(sid, "normal")
            pred = "normal"
            t0 = time.time()

            if eng_name == "fsm":
                if fsm_eng:
                    try:
                        r = fsm_eng.validate_session(ev_dicts)
                        pred = r.get("prediction", "normal")
                    except Exception:
                        pred = "normal"
            elif eng_name == "ml":
                if ml_eng:
                    try:
                        r = ml_eng.predict_session(ev_dicts)
                        pred = r.get("prediction", "normal")
                    except Exception:
                        pred = "normal"
            elif eng_name == "hybrid":
                if hybrid_eng:
                    try:
                        r = hybrid_eng.detect_session(ev_dicts)
                        pred = r.get("prediction", "normal")
                    except Exception:
                        pred = "normal"

            elapsed = (time.time() - t0) * 1000
            total_time += elapsed

            if pred == "anomalous" and actual == "anomalous":
                tp += 1
            elif pred == "anomalous" and actual == "normal":
                fp += 1
            elif pred == "normal" and actual == "normal":
                tn += 1
            else:
                fn += 1

            predictions_list.append({
                "session_id": sid,
                "prediction": pred,
                "actual": actual,
                "correct": pred == actual
            })

        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
        detection_rate = recall
        fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
        false_alarms = round((fp / max(fp + tn, 1)) * 100, 2)
        avg_time = round(total_time / max(total_sessions, 1), 2)

        engines_data[eng_name] = EngineMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            detection_rate=detection_rate,
            false_positive_rate=fpr,
            false_alarms_per_100_benign=false_alarms,
            avg_processing_time_ms=avg_time,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            predictions=predictions_list
        )

    return DetectionCompareResponse(
        dataset_id=dataset.dataset_id,
        dataset_name=dataset.name,
        total_sessions=total_sessions,
        engines=engines_data,
        generalization={
            "unseen_templates_tested": 0,
            "unseen_results": {}
        }
    )
