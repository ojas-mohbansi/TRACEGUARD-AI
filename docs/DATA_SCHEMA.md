# TraceGuard AI — Data Schema

## SQLAlchemy Models (SQLite)

### User
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### NetworkEvent
```python
class NetworkEvent(Base):
    __tablename__ = "network_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    dataset_id = Column(String(50), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    protocol = Column(String(20), default="HTTP")
    event_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    method = Column(String(10), nullable=True)
    path_category = Column(String(50), nullable=True)
    status_code = Column(Integer, nullable=True)
    bytes = Column(Integer, default=0)
    label = Column(String(20), default="normal")  # normal | anomalous
    simulation_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Alert
```python
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    dataset_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    engine = Column(String(20), nullable=False)  # fsm | ml | hybrid
    severity = Column(String(20), nullable=False)  # low | medium | high | critical
    risk_score = Column(Integer, default=0)
    prediction = Column(String(20), nullable=False)  # normal | anomalous
    status = Column(String(20), default="new")  # new | investigating | resolved | dismissed
    summary = Column(Text, nullable=True)
    fsm_result = Column(JSON, nullable=True)
    ml_result = Column(JSON, nullable=True)
    hybrid_result = Column(JSON, nullable=True)
    responsible_events = Column(JSON, nullable=True)  # list of event_ids
    investigation_notes = Column(Text, nullable=True)
    processing_time_ms = Column(Float, default=0.0)
```

### Dataset
```python
class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    format = Column(String(10), nullable=False)  # csv | json
    file_path = Column(String(500), nullable=False)
    event_count = Column(Integer, default=0)
    session_count = Column(Integer, default=0)
    has_labels = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Simulation
```python
class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(String(50), unique=True, nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    config = Column(JSON, nullable=True)
    status = Column(String(20), default="running")  # running | stopped | completed
    events_generated = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
```

## Protocol Event Schema (JSON/CSV)
Required fields for import:
```
event_id, session_id, timestamp, event_type
```

Optional fields (defaults applied if missing):
```
protocol (default: "HTTP"), source, destination, method, path_category, status_code, bytes, label
```

## FSM State Machine Definition
States: IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED, AUTH_FAILED, RESPONSE_SENT, ERROR, CLOSED
See API_CONTRACTS.md for full transition table.

## Feature Vector (ML)
The feature extractor produces these per-session features:
1. `event_count` — number of events in session
2. `unique_event_types` — distinct event types
3. `session_duration_seconds` — time from first to last event
4. `avg_inter_event_time` — mean time between events
5. `std_inter_event_time` — stddev of inter-event times
6. `invalid_transition_count` — FSM violations found
7. `auth_failure_count` — number of AUTH_FAILURE events
8. `error_count` — number of error-related events
9. `response_2xx_ratio` — ratio of 200-range responses
10. `response_4xx_ratio` — ratio of 400-range responses
11. `response_5xx_ratio` — ratio of 500-range responses
12. `avg_bytes` — mean bytes per event
13. `has_close` — whether session ended with CLOSE
14. `request_rate` — requests per second
15. `unique_methods` — distinct HTTP methods used

## Severity Mapping
```python
def risk_to_severity(risk_score: int) -> str:
    if risk_score >= 76: return "critical"
    if risk_score >= 51: return "high"
    if risk_score >= 26: return "medium"
    return "low"
```

## Hybrid Scoring Formula
```python
hybrid_score = (fsm_weight * fsm_score) + (ml_weight * ml_score)
# Default weights: fsm_weight=0.6, ml_weight=0.4
# fsm_score: 100 if violation detected, 0 otherwise
# ml_score: anomaly_score * 100
# If FSM violation detected, minimum hybrid_score = 60
```
