# TraceGuard AI — API Contracts

## Base URL
All REST endpoints are prefixed with `/api`.
Backend runs on `http://localhost:8000`.
Frontend runs on `http://localhost:5173` (Vite dev server).

## Authentication
JWT Bearer token in `Authorization: Bearer <token>` header.
Tokens expire after 24 hours.

### POST /api/auth/signup
Request:
```json
{"username": "string", "email": "string", "password": "string"}
```
Response 201:
```json
{"id": 1, "username": "string", "email": "string", "created_at": "ISO8601"}
```

### POST /api/auth/login
Request:
```json
{"username": "string", "password": "string"}
```
Response 200:
```json
{"access_token": "string", "token_type": "bearer", "user": {"id": 1, "username": "string"}}
```

## Dashboard

### GET /api/dashboard/summary
Response 200:
```json
{
  "total_events": 0,
  "active_sessions": 0,
  "suspicious_sessions": 0,
  "critical_alerts": 0,
  "detection_rate": 0.0,
  "avg_processing_time_ms": 0.0,
  "events_by_hour": [{"hour": "string", "count": 0}],
  "recent_threats": [{"alert_id": "string", "severity": "string", "session_id": "string", "timestamp": "ISO8601"}],
  "engine_distribution": {"fsm": 0, "ml": 0, "hybrid": 0}
}
```

## Simulation

### POST /api/simulation/start
Request:
```json
{
  "mode": "normal|anomalous|mixed",
  "event_count": 100,
  "speed": 1.0,
  "anomaly_ratio": 0.2,
  "seed": 42
}
```
Response 200:
```json
{"simulation_id": "string", "status": "running", "config": {}}
```

### POST /api/simulation/stop
Request:
```json
{"simulation_id": "string"}
```
Response 200:
```json
{"simulation_id": "string", "status": "stopped", "events_generated": 0}
```

## Events

### GET /api/events
Query params: `session_id`, `protocol`, `limit` (default 100), `offset` (default 0)
Response 200:
```json
{
  "events": [
    {
      "event_id": "string",
      "session_id": "string",
      "timestamp": "ISO8601",
      "protocol": "HTTP",
      "event_type": "string",
      "source": "string",
      "destination": "string",
      "method": "string|null",
      "path_category": "string|null",
      "status_code": "int|null",
      "bytes": 0,
      "label": "normal|anomalous"
    }
  ],
  "total": 0
}
```

## Alerts

### GET /api/alerts
Query params: `severity`, `engine`, `status`, `limit`, `offset`
Response 200:
```json
{
  "alerts": [
    {
      "alert_id": "string",
      "session_id": "string",
      "timestamp": "ISO8601",
      "engine": "fsm|ml|hybrid",
      "severity": "low|medium|high|critical",
      "risk_score": 0,
      "prediction": "normal|anomalous",
      "status": "new|investigating|resolved|dismissed",
      "summary": "string"
    }
  ],
  "total": 0
}
```

### GET /api/alerts/{alert_id}
Response 200:
```json
{
  "alert_id": "string",
  "session_id": "string",
  "timestamp": "ISO8601",
  "engine": "string",
  "severity": "string",
  "risk_score": 0,
  "prediction": "string",
  "status": "string",
  "fsm_result": {
    "current_state": "string",
    "previous_state": "string",
    "incoming_event": "string",
    "expected_transitions": ["string"],
    "actual_transition": "string",
    "violation": true,
    "violation_reason": "string",
    "transition_history": [{"from": "string", "to": "string", "event": "string", "valid": true}]
  },
  "ml_result": {
    "anomaly_score": 0.0,
    "prediction": "string",
    "feature_importances": {"feature_name": 0.0},
    "model_version": "string"
  },
  "hybrid_result": {
    "combined_risk_score": 0,
    "severity": "string",
    "fsm_weight": 0.6,
    "ml_weight": 0.4,
    "explanation": "string"
  },
  "events": [],
  "investigation_notes": "string"
}
```

### PATCH /api/alerts/{alert_id}
Request:
```json
{"status": "investigating|resolved|dismissed", "investigation_notes": "string"}
```

## Detection

### POST /api/detection/run
Request:
```json
{
  "session_ids": ["string"],
  "engines": ["fsm", "ml", "hybrid"],
  "dataset_id": "string|null"
}
```
Response 200:
```json
{
  "results": [
    {
      "session_id": "string",
      "engine": "string",
      "prediction": "normal|anomalous",
      "risk_score": 0,
      "severity": "string",
      "fsm_violation": false,
      "ml_anomaly_score": 0.0,
      "explanation": "string",
      "responsible_events": ["string"],
      "processing_time_ms": 0.0
    }
  ]
}
```

### GET /api/detection/compare
Query params: `dataset_id` (required)
Response 200:
```json
{
  "dataset_id": "string",
  "dataset_name": "string",
  "total_sessions": 0,
  "engines": {
    "fsm": {
      "precision": 0.0, "recall": 0.0, "f1_score": 0.0,
      "detection_rate": 0.0, "false_positive_rate": 0.0,
      "false_alarms_per_100_benign": 0.0,
      "avg_processing_time_ms": 0.0,
      "true_positives": 0, "false_positives": 0,
      "true_negatives": 0, "false_negatives": 0,
      "predictions": [{"session_id": "string", "prediction": "string", "actual": "string", "correct": true}]
    },
    "ml": { "...same structure..." },
    "hybrid": { "...same structure..." }
  },
  "generalization": {
    "unseen_templates_tested": 0,
    "unseen_results": {}
  }
}
```

## Protocols

### GET /api/protocols/http/fsm
Response 200:
```json
{
  "protocol": "HTTP",
  "states": [
    {"id": "IDLE", "label": "Idle", "description": "No active connection", "is_initial": true, "is_final": false},
    {"id": "CONNECTED", "label": "Connected", "description": "TCP connection established", "is_initial": false, "is_final": false},
    {"id": "REQUEST_RECEIVED", "label": "Request Received", "description": "HTTP request received", "is_initial": false, "is_final": false},
    {"id": "AUTH_CHECKED", "label": "Auth Checked", "description": "Authentication verified", "is_initial": false, "is_final": false},
    {"id": "AUTH_FAILED", "label": "Auth Failed", "description": "Authentication failed", "is_initial": false, "is_final": false},
    {"id": "RESPONSE_SENT", "label": "Response Sent", "description": "HTTP response sent", "is_initial": false, "is_final": false},
    {"id": "ERROR", "label": "Error", "description": "Error state", "is_initial": false, "is_final": false},
    {"id": "CLOSED", "label": "Closed", "description": "Connection closed", "is_initial": false, "is_final": true}
  ],
  "transitions": [
    {"from": "IDLE", "to": "CONNECTED", "event": "CONNECT", "description": "Client connects"},
    {"from": "CONNECTED", "to": "REQUEST_RECEIVED", "event": "REQUEST", "description": "HTTP request received"},
    {"from": "REQUEST_RECEIVED", "to": "AUTH_CHECKED", "event": "AUTH_SUCCESS", "description": "Auth passed"},
    {"from": "REQUEST_RECEIVED", "to": "AUTH_FAILED", "event": "AUTH_FAILURE", "description": "Auth failed"},
    {"from": "AUTH_CHECKED", "to": "RESPONSE_SENT", "event": "RESPONSE_200", "description": "Success response"},
    {"from": "AUTH_CHECKED", "to": "RESPONSE_SENT", "event": "RESPONSE_301", "description": "Redirect response"},
    {"from": "AUTH_CHECKED", "to": "ERROR", "event": "RESPONSE_500", "description": "Server error"},
    {"from": "AUTH_FAILED", "to": "RESPONSE_SENT", "event": "RESPONSE_401", "description": "Unauthorized response"},
    {"from": "AUTH_FAILED", "to": "RESPONSE_SENT", "event": "RESPONSE_403", "description": "Forbidden response"},
    {"from": "RESPONSE_SENT", "to": "REQUEST_RECEIVED", "event": "REQUEST", "description": "Keep-alive request"},
    {"from": "RESPONSE_SENT", "to": "CLOSED", "event": "CLOSE", "description": "Connection closed"},
    {"from": "ERROR", "to": "CLOSED", "event": "CLOSE", "description": "Close after error"},
    {"from": "ERROR", "to": "RESPONSE_SENT", "event": "ERROR_RESPONSE", "description": "Error response sent"},
    {"from": "CONNECTED", "to": "CLOSED", "event": "TIMEOUT", "description": "Connection timeout"},
    {"from": "REQUEST_RECEIVED", "to": "ERROR", "event": "MALFORMED", "description": "Malformed request"}
  ],
  "event_types": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "AUTH_FAILURE", "RESPONSE_200", "RESPONSE_301", "RESPONSE_401", "RESPONSE_403", "RESPONSE_500", "CLOSE", "TIMEOUT", "MALFORMED", "ERROR_RESPONSE"]
}
```

## Datasets

### POST /api/datasets/upload
Content-Type: multipart/form-data
Field: `file` (CSV or JSON), `name` (string), `description` (string)
Response 201:
```json
{
  "dataset_id": "string",
  "name": "string",
  "description": "string",
  "format": "csv|json",
  "event_count": 0,
  "session_count": 0,
  "created_at": "ISO8601"
}
```

### GET /api/datasets
Response 200:
```json
{
  "datasets": [
    {"dataset_id": "string", "name": "string", "description": "string", "format": "string", "event_count": 0, "session_count": 0, "created_at": "ISO8601", "has_labels": true}
  ]
}
```

### GET /api/datasets/{dataset_id}/download
Returns the dataset file.

## Health

### GET /api/health
Response 200:
```json
{"status": "healthy", "version": "1.0.0", "database": "connected", "models_loaded": true}
```

## WebSocket

### WS /ws/events
After connection, server pushes JSON messages:
```json
{"type": "event", "data": {"event_id": "...", ...}}
{"type": "alert", "data": {"alert_id": "...", ...}}
{"type": "simulation_status", "data": {"simulation_id": "...", "status": "...", "events_generated": 0}}
{"type": "stats_update", "data": {"total_events": 0, "active_sessions": 0, ...}}
```

Client can send:
```json
{"action": "subscribe", "channels": ["events", "alerts", "stats"]}
```

## Score Semantics
- `risk_score`: 0-100 integer. Higher = more suspicious.
- `ml_anomaly_score`: 0.0-1.0 float from Isolation Forest. Higher = more anomalous.
- `severity`: derived from risk_score: low (0-25), medium (26-50), high (51-75), critical (76-100).
