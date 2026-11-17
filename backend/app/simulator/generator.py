"""Traffic Simulator generating events according to HTTP FSM transitions."""
from datetime import datetime, timedelta
from uuid import uuid4
import random
from typing import List, Dict, Any, Optional
import asyncio
import logging

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import NetworkEvent, Alert, Simulation
from app.api.websocket import ws_manager

logger = logging.getLogger(__name__)

# Valid HTTP FSM Transitions
VALID_TRANSITIONS = {
    "IDLE": [("CONNECTED", "CONNECT")],
    "CONNECTED": [("REQUEST_RECEIVED", "REQUEST"), ("CLOSED", "TIMEOUT")],
    "REQUEST_RECEIVED": [
        ("AUTH_CHECKED", "AUTH_SUCCESS"),
        ("AUTH_FAILED", "AUTH_FAILURE"),
        ("ERROR", "MALFORMED")
    ],
    "AUTH_CHECKED": [
        ("RESPONSE_SENT", "RESPONSE_200"),
        ("RESPONSE_SENT", "RESPONSE_301"),
        ("ERROR", "RESPONSE_500")
    ],
    "AUTH_FAILED": [
        ("RESPONSE_SENT", "RESPONSE_401"),
        ("RESPONSE_SENT", "RESPONSE_403")
    ],
    "RESPONSE_SENT": [
        ("REQUEST_RECEIVED", "REQUEST"),
        ("CLOSED", "CLOSE")
    ],
    "ERROR": [
        ("CLOSED", "CLOSE"),
        ("RESPONSE_SENT", "ERROR_RESPONSE")
    ]
}

ALL_EVENT_TYPES = [
    "CONNECT", "REQUEST", "AUTH_SUCCESS", "AUTH_FAILURE",
    "RESPONSE_200", "RESPONSE_301", "RESPONSE_401", "RESPONSE_403",
    "RESPONSE_500", "CLOSE", "TIMEOUT", "MALFORMED", "ERROR_RESPONSE"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]
PATH_CATEGORIES = ["api", "static", "auth", "admin", "docs", "data"]


class TrafficSimulator:
    """Simulates realistic HTTP protocol sessions conforming or violating FSM rules."""

    def __init__(self, simulation_id: str, mode: str = "mixed", event_count: int = 100,
                 speed: float = 1.0, anomaly_ratio: float = 0.2, seed: Optional[int] = 42,
                 workspace_id: Optional[str] = "default-workspace"):
        self.simulation_id = simulation_id
        self.workspace_id = workspace_id or "default-workspace"
        self.mode = mode
        self.event_count = event_count
        self.speed = max(speed, 0.1)
        self.anomaly_ratio = anomaly_ratio
        self.is_running = False
        self.generated_count: int = 0
        self._task: Optional[asyncio.Task] = None
        if seed is not None:
            random.seed(seed)

    def _generate_normal_session(self, session_id: str, start_time: datetime) -> List[Dict[str, Any]]:
        events = []
        current_state = "IDLE"
        current_time = start_time
        source_ip = f"192.168.1.{random.randint(10, 250)}"
        dest_ip = "10.0.0.1"

        # Walk through valid transitions until CLOSED or safe stop
        while current_state != "CLOSED":
            choices = VALID_TRANSITIONS.get(current_state, [])
            if not choices:
                break
            # Weight towards completion
            next_state, event_type = random.choice(choices)

            status_code = None
            if "200" in event_type:
                status_code = 200
            elif "301" in event_type:
                status_code = 301
            elif "401" in event_type:
                status_code = 401
            elif "403" in event_type:
                status_code = 403
            elif "500" in event_type:
                status_code = 500

            method = random.choice(HTTP_METHODS) if event_type in ["REQUEST", "CONNECT"] else None
            path = random.choice(PATH_CATEGORIES) if event_type in ["REQUEST"] else None
            bytes_val = random.randint(128, 4096) if "RESPONSE" in event_type else random.randint(32, 512)

            events.append({
                "event_id": f"evt_{uuid4().hex[:12]}",
                "session_id": session_id,
                "timestamp": current_time,
                "protocol": "HTTP",
                "event_type": event_type,
                "source": source_ip,
                "destination": dest_ip,
                "method": method,
                "path_category": path,
                "status_code": status_code,
                "bytes": bytes_val,
                "label": "normal"
            })
            current_state = next_state
            current_time += timedelta(milliseconds=random.randint(20, 250))

        return events

    def _generate_anomalous_session(self, session_id: str, start_time: datetime) -> List[Dict[str, Any]]:
        # Start normal then inject an impossible transition or violation
        events = self._generate_normal_session(session_id, start_time)
        if len(events) >= 2:
            # Violate transition by picking an invalid transition event
            bad_idx = random.randint(1, len(events) - 1)
            bad_event_type = random.choice(["RESPONSE_200", "RESPONSE_500", "ERROR_RESPONSE", "AUTH_SUCCESS"])
            events[bad_idx]["event_type"] = bad_event_type
            events[bad_idx]["label"] = "anomalous"
            for ev in events[bad_idx:]:
                ev["label"] = "anomalous"
        return events

    async def run(self):
        """Asynchronously stream events, persist to DB, and broadcast to WebSocket."""
        self.is_running = True
        generated_count = 0
        db: Session = SessionLocal()

        # Try to resolve hybrid engine for alert creation
        try:
            from app.detection.hybrid import HybridEngine
            from app.detection.fsm import FSMEngine
            from app.detection.ml import MLEngine
            engine = HybridEngine(fsm_engine=FSMEngine(), ml_engine=MLEngine())
        except Exception:
            engine = None

        try:
            while self.is_running and generated_count < self.event_count:
                session_id = f"sess_{uuid4().hex[:8]}"
                is_anom = False
                if self.mode == "anomalous":
                    is_anom = True
                elif self.mode == "mixed":
                    is_anom = (random.random() < self.anomaly_ratio)

                start_ts = datetime.utcnow()
                if is_anom:
                    session_events = self._generate_anomalous_session(session_id, start_ts)
                else:
                    session_events = self._generate_normal_session(session_id, start_ts)

                db_events = []
                for ev in session_events:
                    if not self.is_running or generated_count >= self.event_count:
                        break
                    ne = NetworkEvent(
                        workspace_id=self.workspace_id,
                        event_id=ev["event_id"],
                        session_id=ev["session_id"],
                        timestamp=ev["timestamp"],
                        protocol=ev["protocol"],
                        event_type=ev["event_type"],
                        source=ev["source"],
                        destination=ev["destination"],
                        method=ev["method"],
                        path_category=ev["path_category"],
                        status_code=ev["status_code"],
                        bytes=ev["bytes"],
                        label=ev["label"],
                        simulation_id=self.simulation_id
                    )
                    db_events.append(ne)
                    generated_count += 1

                    # Broadcast event over WebSocket
                    await ws_manager.broadcast("event", {
                        "event_id": ne.event_id,
                        "session_id": ne.session_id,
                        "timestamp": ne.timestamp.isoformat(),
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

                    # Sleep based on simulation speed
                    delay = (1.0 / self.speed) * 0.05
                    await asyncio.sleep(delay)

                if db_events:
                    db.bulk_save_objects(db_events)
                    db.commit()

                # Run detection on this session and create alert if anomalous
                if engine and session_events:
                    try:
                        res = engine.detect_session(session_events)
                        fsm_res = res.get("fsm_result") or {}
                        ml_res = res.get("ml_result") or {}
                        fsm_viol = bool(res.get("fsm_violation") or fsm_res.get("fsm_violation"))
                        ml_anom = bool(res.get("ml_anomalous") or (ml_res.get("prediction") == "anomalous") or (res.get("ml_anomaly_score", 0) >= 0.55))

                        engine_label = res.get("attribution")
                        if not engine_label or engine_label == "none":
                            if fsm_viol and ml_anom:
                                engine_label = "hybrid"
                            elif fsm_viol:
                                engine_label = "fsm"
                            elif ml_anom:
                                engine_label = "ml"
                            else:
                                engine_label = "hybrid"

                        if fsm_viol or ml_anom or res.get("prediction") == "anomalous" or res.get("risk_score", 0) >= 40:

                            alert = Alert(
                                workspace_id=self.workspace_id,
                                alert_id=f"alrt_{uuid4().hex[:12]}",
                                session_id=session_id,
                                timestamp=datetime.utcnow(),
                                engine=engine_label,
                                severity=res["severity"],
                                risk_score=res["risk_score"],
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

                            await ws_manager.broadcast("alert", {
                                "alert_id": alert.alert_id,
                                "session_id": alert.session_id,
                                "timestamp": alert.timestamp.isoformat(),
                                "engine": alert.engine,
                                "severity": alert.severity,
                                "risk_score": alert.risk_score,
                                "prediction": alert.prediction,
                                "status": alert.status,
                                "summary": alert.summary
                            })
                    except Exception as e:
                        logger.error(f"Error during real-time session alert detection: {e}")

                # Update simulation status
                sim_record = db.query(Simulation).filter(Simulation.simulation_id == self.simulation_id).first()
                if sim_record:
                    sim_record.events_generated = generated_count
                    db.commit()

                await ws_manager.broadcast("simulation_status", {
                    "simulation_id": self.simulation_id,
                    "status": "running" if self.is_running else "stopped",
                    "events_generated": generated_count
                })

        except Exception as e:
            logger.error(f"Simulator exception: {e}")
        finally:
            self.is_running = False
            sim_record = db.query(Simulation).filter(Simulation.simulation_id == self.simulation_id).first()
            if sim_record:
                sim_record.status = "completed" if generated_count >= self.event_count else "stopped"
                sim_record.stopped_at = datetime.utcnow()
                sim_record.events_generated = generated_count
                db.commit()

            await ws_manager.broadcast("simulation_status", {
                "simulation_id": self.simulation_id,
                "status": sim_record.status if sim_record else "stopped",
                "events_generated": generated_count
            })
            db.close()

    def stop(self):
        self.is_running = False
