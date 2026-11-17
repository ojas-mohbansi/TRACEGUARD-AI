# TraceGuard AI — API Contracts & Protocol Specifications

**Document:** `04_API_CONTRACTS_AND_PROTOCOLS.md`  
**Classification:** Complete Technical API Reference  
**Version:** 2.0.0 (Authoritative)  
**Repository:** `C:\Projects\FSM-NIDS`  
**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`  

---

## 1. Authentication & Session Protocol

### 1.1 Local Academic Mode vs. JWT Bearer Tokens
The API implements dual-mode authentication:
- **Local Academic Mode (Default)**: When requests originate from loopback (`127.0.0.1`, `::1`), the `get_current_user` dependency automatically resolves to the built-in `Academic Evaluator` account scoped to `default-workspace`. No `Authorization` header is required.
- **Enterprise Mode**: When deployed outside loopback, requests require a valid Bearer token in the HTTP header:
  `Authorization: Bearer <jwt_access_token>`

---

## 2. Authentication Endpoints (`/auth`)

### 2.1 User Signup
- **Endpoint**: `POST /api/v1/auth/signup`
- **Request Body**:
  ```json
  {
    "username": "evaluator",
    "email": "evaluator@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "id": 1,
    "username": "evaluator",
    "email": "evaluator@university.edu",
    "workspace_id": "ws-eval-101",
    "created_at": "2026-11-18T00:00:00Z"
  }
  ```

### 2.2 User Login (Token Issuance)
- **Endpoint**: `POST /api/v1/auth/login`
- **Request Body**: Form-encoded `username` and `password` or JSON credentials.
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "evaluator",
      "workspace_id": "ws-eval-101"
    }
  }
  ```

### 2.3 User Identity & Workspace Profile
- **Endpoint**: `GET /api/v1/auth/me`
- **Response `200 OK`**:
  ```json
  {
    "id": 1,
    "username": "Academic Evaluator",
    "role": "admin",
    "mode": "LOCAL_ACADEMIC",
    "workspace_id": "default-workspace"
  }
  ```

---

## 3. Automata & FSM Endpoints (`/fsm`)

### 3.1 Retrieve Formal Automaton Model
- **Endpoint**: `GET /api/v1/fsm/model`
- **Description**: Returns the complete formal 5-tuple specification $M = (Q, \Sigma, \delta, q_0, F)$ and full 117-transition matrix.
- **Response `200 OK`**:
  ```json
  {
    "name": "HTTP Protocol State Machine DFA",
    "states": ["IDLE", "CONNECTED", "REQUEST_RECEIVED", "AUTH_CHECKED", "AUTH_FAILED", "RESPONSE_SENT", "CHUNK_DATA", "CLOSED", "TRAP"],
    "alphabet": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "AUTH_FAILURE", "RESPONSE_200", "RESPONSE_301", "RESPONSE_401", "RESPONSE_403", "RESPONSE_500", "CLOSE", "TIMEOUT", "MALFORMED", "ERROR_RESPONSE"],
    "initial_state": "IDLE",
    "accepting_states": ["CLOSED"],
    "trap_state": "TRAP",
    "total_transitions": 117,
    "transition_matrix": {
      "IDLE": { "CONNECT": "CONNECTED", "REQUEST": "TRAP", "...": "TRAP" },
      "CONNECTED": { "REQUEST": "REQUEST_RECEIVED", "TIMEOUT": "CLOSED", "...": "TRAP" }
    }
  }
  ```

### 3.2 Validate Trace Sequence
- **Endpoint**: `POST /api/v1/fsm/validate`
- **Request Body**:
  ```json
  {
    "trace": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"]
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "is_accepted": true,
    "final_state": "CLOSED",
    "violation_detected": false,
    "state_history": ["IDLE", "CONNECTED", "REQUEST_RECEIVED", "AUTH_CHECKED", "RESPONSE_SENT", "CLOSED"],
    "step_count": 5
  }
  ```

---

## 4. Threat Triage & Alerts Endpoints (`/threats`)

### 4.1 Query Active Security Alerts
- **Endpoint**: `GET /api/v1/threats/alerts`
- **Query Parameters**:
  - `limit`: `int` (default: 50)
  - `severity`: `string` (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `engine`: `string` (`fsm`, `ml`, `hybrid`)
- **Response `200 OK`**:
  ```json
  {
    "total": 42,
    "alerts": [
      {
        "id": 101,
        "session_id": "sess-8f3a92",
        "engine": "fsm",
        "severity": "CRITICAL",
        "risk_score": 100.0,
        "rule_name": "FSM_PROTOCOL_VIOLATION_TRAP",
        "description": "Illegal transition from CONNECTED on symbol RESPONSE_200. Absorbing trap state entered.",
        "triggered_at": "2026-11-18T01:15:30Z"
      }
    ]
  }
  ```

### 4.2 Threat Forensics Timeline
- **Endpoint**: `GET /api/v1/threats/forensics/{session_id}`
- **Response `200 OK`**:
  ```json
  {
    "session_id": "sess-8f3a92",
    "src_ip": "192.168.1.105",
    "dst_ip": "10.0.0.1",
    "src_port": 54210,
    "dst_port": 80,
    "current_state": "TRAP",
    "fsm_score": 100.0,
    "ml_score": 28.5,
    "hybrid_score": 60.0,
    "timeline": [
      { "step": 1, "symbol": "CONNECT", "resulting_state": "CONNECTED", "timestamp": "0.000s" },
      { "step": 2, "symbol": "RESPONSE_200", "resulting_state": "TRAP", "timestamp": "0.045s", "violation": true }
    ]
  }
  ```

---

## 5. Dashboard Summary Endpoints (`/dashboard`)

### 5.1 Real-Time Security Metrics
- **Endpoint**: `GET /api/v1/dashboard/summary`
- **Response `200 OK`**:
  ```json
  {
    "total_sessions": 1284,
    "total_alerts": 86,
    "engine_distribution": {
      "fsm": 18,
      "ml": 12,
      "hybrid": 56
    },
    "severity_distribution": {
      "critical": 14,
      "high": 42,
      "medium": 20,
      "low": 10
    },
    "fsm_states_count": {
      "CLOSED": 1150,
      "TRAP": 74,
      "CONNECTED": 40,
      "REQUEST_RECEIVED": 20
    }
  }
  ```

---

## 6. Network Ingestion & Replay Endpoints (`/network`)

### 6.1 List Available Network Interfaces
- **Endpoint**: `GET /api/v1/network/interfaces`
- **Response `200 OK`**:
  ```json
  {
    "driver": "Npcap (WinPcap compatible)",
    "available_interfaces": [
      { "name": "\\Device\\NPF_{...}", "description": "Ethernet0", "ip": "192.168.1.10" },
      { "name": "\\Device\\NPF_Loopback", "description": "Loopback Adapter", "ip": "127.0.0.1" }
    ]
  }
  ```

### 6.2 Start / Stop Passive Capture
- **Start**: `POST /api/v1/network/capture/start` (`{"interface": "\\Device\\NPF_Loopback", "bpf_filter": "tcp and port 8000"}`)
- **Stop**: `POST /api/v1/network/capture/stop`

---

## 7. Academic Showcase & Benchmark Endpoints (`/benchmark`)

### 7.1 Execute Academic Benchmark Corpus
- **Endpoint**: `POST /api/v1/benchmark/run`
- **Request Body**: `{"corpus": "ACADEMIC_120_SESSIONS"}`
- **Response `200 OK`**:
  ```json
  {
    "total_sessions": 120,
    "total_events": 806,
    "fsm_accuracy": 1.0,
    "ml_accuracy": 0.942,
    "hybrid_recall": 0.988,
    "scenarios_evaluated": 6
  }
  ```

---

## 8. Real-Time Telemetry WebSocket (`/ws/telemetry`)

- **URI**: `ws://127.0.0.1:8000/ws/telemetry`
- **Protocol**: JSON-encoded streaming messages.
- **Client Subscription Message**:
  ```json
  { "action": "subscribe", "workspace_id": "default-workspace" }
  ```
- **Server Broadcast Message (Live Transition)**:
  ```json
  {
    "type": "FSM_TRANSITION",
    "data": {
      "session_id": "sess-live-99",
      "symbol": "CONNECT",
      "from_state": "IDLE",
      "to_state": "CONNECTED",
      "timestamp": "2026-11-18T02:00:00.123Z"
    }
  }
  ```
- **Server Broadcast Message (Security Alert)**:
  ```json
  {
    "type": "THREAT_ALERT",
    "data": {
      "session_id": "sess-live-99",
      "engine": "fsm",
      "severity": "CRITICAL",
      "risk_score": 100.0,
      "rule": "FSM_PROTOCOL_VIOLATION_TRAP"
    }
  }
  ```
