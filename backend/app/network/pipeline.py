"""Real network event detection pipeline for TraceGuard AI."""
import asyncio
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import NetworkEvent, Alert
from app.api.websocket import ws_manager
from app.network.capture_service import CaptureService

logger = logging.getLogger(__name__)


def get_detection_engines():
    """Lazily load the verified FSM, ML, and Hybrid engines."""
    fsm_eng = None
    ml_eng = None
    hybrid_eng = None

    try:
        from app.detection.fsm import FSMEngine
        fsm_eng = FSMEngine()
    except Exception as e:
        logger.warning(f"Could not load FSMEngine: {e}")

    try:
        from app.detection.ml import MLEngine
        ml_eng = MLEngine()
    except Exception as e:
        logger.warning(f"Could not load MLEngine: {e}")

    try:
        from app.detection.hybrid import HybridEngine
        hybrid_eng = HybridEngine(
            fsm_engine=fsm_eng,
            ml_engine=ml_eng,
            fsm_weight=0.6,
            ml_weight=0.4
        )
    except Exception as e:
        logger.warning(f"Could not load HybridEngine: {e}")

    return fsm_eng, ml_eng, hybrid_eng


class IngestionPipeline:
    """
    Real-time & batch network ingestion pipeline:
    Packets -> Flow Session Aggregation -> FSM & ML & Hybrid -> DB & WebSocket Broadcast
    """

    def __init__(self, workspace_id: str = "default-workspace"):
        self.workspace_id = workspace_id or "default-workspace"
        self.capture_service = CaptureService.get_instance()

    async def process_parsed_events(
        self,
        events: List[Dict[str, Any]],
        source_type: str = "pcap_replay",
        stream_delay_ms: float = 0.0,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a list of parsed events, group by session, run hybrid detection,
        persist records to SQLite/PostgreSQL, and broadcast live updates via WebSockets.
        """
        if not events:
            return {"events_processed": 0, "alerts_generated": 0, "sessions_count": 0}

        fsm_eng, ml_eng, hybrid_eng = get_detection_engines()
        db: Session = SessionLocal()

        # Group events by session
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        for ev in events:
            sid = ev.get("session_id", "default_sess")
            sessions.setdefault(sid, []).append(ev)

        total_alerts = 0
        total_events = len(events)
        total_bytes = sum(ev.get("bytes", 0) for ev in events)

        try:
            for session_id, session_events in sessions.items():
                db_events = []
                for ev in session_events:
                    ne = NetworkEvent(
                        workspace_id=self.workspace_id,
                        event_id=ev.get("event_id") or f"evt_{uuid4().hex[:12]}",
                        session_id=session_id,
                        dataset_id=dataset_id,
                        timestamp=ev.get("timestamp") or datetime.utcnow(),
                        protocol=ev.get("protocol", "HTTP"),
                        event_type=ev.get("event_type", "CONNECT"),
                        source=ev.get("source", "127.0.0.1:0"),
                        destination=ev.get("destination", "127.0.0.1:80"),
                        method=ev.get("method"),
                        path_category=ev.get("path_category"),
                        status_code=ev.get("status_code"),
                        bytes=ev.get("bytes", 0),
                        label=ev.get("label", "normal")
                    )
                    db_events.append(ne)

                    # Update in-memory capture service telemetry
                    self.capture_service.events_processed += 1
                    self.capture_service.bytes_processed += ne.bytes
                    self.capture_service.recent_events.append({
                        "event_id": ne.event_id,
                        "session_id": ne.session_id,
                        "timestamp": ne.timestamp.isoformat() if ne.timestamp else None,
                        "protocol": ne.protocol,
                        "event_type": ne.event_type,
                        "source": ne.source,
                        "destination": ne.destination,
                        "bytes": ne.bytes,
                        "label": ne.label
                    })

                    # Live WebSocket broadcast for this event
                    await ws_manager.broadcast("event", {
                        "event_id": ne.event_id,
                        "session_id": ne.session_id,
                        "timestamp": ne.timestamp.isoformat() if ne.timestamp else None,
                        "protocol": ne.protocol,
                        "event_type": ne.event_type,
                        "source": ne.source,
                        "destination": ne.destination,
                        "method": ne.method,
                        "path_category": ne.path_category,
                        "status_code": ne.status_code,
                        "bytes": ne.bytes,
                        "label": ne.label
                    })

                    if stream_delay_ms > 0:
                        await asyncio.sleep(stream_delay_ms / 1000.0)

                db.bulk_save_objects(db_events)
                db.commit()

                # Run Multi-Engine Detection on the completed session
                if hybrid_eng and session_events:
                    try:
                        res = hybrid_eng.detect_session(session_events)
                        is_anomalous = res.get("prediction") == "anomalous"
                        risk_score = res.get("risk_score", 0)

                        fsm_res = res.get("fsm_result") or {}
                        ml_res = res.get("ml_result") or {}
                        fsm_violation = bool(res.get("fsm_violation") or fsm_res.get("fsm_violation"))
                        ml_anomaly = bool(res.get("ml_anomalous") or (ml_res.get("prediction") == "anomalous") or (res.get("ml_anomaly_score", 0) >= 0.55))

                        # Accurate engine classification attribution
                        engine_type = res.get("attribution")
                        if not engine_type or engine_type == "none":
                            if fsm_violation and ml_anomaly:
                                engine_type = "hybrid"
                            elif fsm_violation:
                                engine_type = "fsm"
                            elif ml_anomaly:
                                engine_type = "ml"
                            else:
                                engine_type = "hybrid"

                        if fsm_violation or ml_anomaly or is_anomalous or risk_score >= 40:

                            alert = Alert(
                                workspace_id=self.workspace_id,
                                alert_id=f"alrt_{uuid4().hex[:12]}",
                                session_id=session_id,
                                dataset_id=dataset_id,
                                timestamp=datetime.utcnow(),
                                engine=engine_type,
                                severity=res["severity"],
                                risk_score=risk_score,
                                prediction=res["prediction"],
                                status="new",
                                summary=res["explanation"][:250],
                                fsm_result=fsm_res,
                                ml_result=ml_res,
                                hybrid_result=res.get("hybrid_result"),
                                responsible_events=res.get("responsible_events", []),
                                processing_time_ms=res.get("processing_time_ms", 0.0)
                            )
                            db.add(alert)
                            db.commit()
                            db.refresh(alert)
                            total_alerts += 1

                            self.capture_service.alerts_generated += 1
                            self.capture_service.recent_alerts.append({
                                "alert_id": alert.alert_id,
                                "session_id": alert.session_id,
                                "engine": alert.engine,
                                "severity": alert.severity,
                                "risk_score": alert.risk_score,
                                "summary": alert.summary
                            })

                            # Broadcast alert over WebSocket
                            await ws_manager.broadcast("alert", {
                                "alert_id": alert.alert_id,
                                "session_id": alert.session_id,
                                "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
                                "engine": alert.engine,
                                "severity": alert.severity,
                                "risk_score": alert.risk_score,
                                "prediction": alert.prediction,
                                "summary": alert.summary,
                                "fsm_result": alert.fsm_result,
                                "ml_result": alert.ml_result,
                                "hybrid_result": alert.hybrid_result
                            })

                    except Exception as e:
                        logger.error(f"Error during detection on session {session_id}: {e}")

            # Broadcast updated operational stats
            await ws_manager.broadcast("stats", {
                "total_events": total_events,
                "total_alerts": total_alerts,
                "sessions_count": len(sessions),
                "source": source_type
            })

        finally:
            db.close()

        return {
            "events_processed": total_events,
            "alerts_generated": total_alerts,
            "sessions_count": len(sessions),
            "bytes_processed": total_bytes
        }
