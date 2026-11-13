# TraceGuard AI - Production SaaS Architecture

## 1. System Architecture Overview

TraceGuard AI is an AI-powered Network Intrusion Detection SaaS designed to capture, simulate, analyze, and detect anomalous network-protocol event sequences across multi-tenant enterprise environments.

### Core Architecture Layers:
- **Client Presentation Layer**: React 18 SPA built with Vite, Tailwind CSS, Lucide Icons, and Recharts, providing low-latency security operations center (SOC) dashboards and interactive protocol explorers.
- **API & Coordination Gateway**: FastAPI (ASGI) exposing RESTful JSON endpoints and asynchronous WebSocket feeds (`/ws/events`).
- **Detection & Inference Subsystems**:
  - **FSM Engine**: Deterministic state-machine sequence validator tracking protocol states and transitions.
  - **ML Engine**: Unsupervised statistical anomaly detector using Isolation Forest trained over 15 normalized session features.
  - **Hybrid Engine**: Weighted fusion model integrating FSM transition violation floors with continuous ML anomaly scores.
- **Persistence & Isolation Layer**: SQLAlchemy 2.0 ORM with Alembic migrations, supporting SQLite for local zero-dependency testing and managed PostgreSQL with connection pooling for enterprise production.

---

## 2. Multi-Tenant Workspace Architecture

TraceGuard partitions all operational data using strict **Workspace-Level Isolation**.

```
+-----------------------------------------------------------+
|                          User                             |
+-----------------------------------------------------------+
                              |
                     Workspace Membership
                              |
                              v
+-----------------------------------------------------------+
|                        Workspace                          |
|  - workspace_id (UUID primary key)                        |
|  - subscription_tier (free | pro | team)                  |
|  - quotas (max_datasets, max_simulations_per_day)         |
+-----------------------------------------------------------+
       |                  |                |            |
       v                  v                v            v
+---------------+  +--------------+  +-----------+  +-------------+
| NetworkEvents |  |    Alerts    |  | Datasets  |  | Simulations |
+---------------+  +--------------+  +-----------+  +-------------+
```

### Isolation Guarantees:
1. **Request-Scoped Context**: Every authenticated request evaluates `WorkspaceContext` extracted from the `X-Workspace-ID` header and user session.
2. **Query Scoping**: Database queries unconditionally filter on `workspace_id == ctx.workspace_id`.
3. **Cross-Tenant Defenses**: Direct object references (e.g., alert details, dataset downloads) verify resource ownership and reject foreign workspace requests with HTTP 403 Forbidden.

---

## 3. Database Migration & Schema Design

Database migrations are managed via **Alembic**. The data model accommodates both SQLite (development) and PostgreSQL (production).

### Schema Tables:
- `users`: ID, username, email, full_name, hashed_password, created_at, is_active.
- `workspaces`: ID, workspace_id, name, slug, owner_id, subscription_tier, max_simulations_per_day, max_uploaded_datasets, created_at.
- `workspace_members`: ID, workspace_id, user_id, role, joined_at.
- `network_events`: ID, workspace_id, event_id, session_id, dataset_id, timestamp, protocol, event_type, source, destination, method, status_code, bytes, label.
- `alerts`: ID, workspace_id, alert_id, session_id, timestamp, engine, severity, risk_score, prediction, status, summary, fsm_result, ml_result, hybrid_result, responsible_events, investigation_notes, processing_time_ms.
- `datasets`: ID, workspace_id, dataset_id, name, description, format, file_path, event_count, session_count, has_labels, created_at.
- `simulations`: ID, workspace_id, simulation_id, mode, config, status, events_generated, started_at, stopped_at.

---

## 4. Production Database Configuration & Backup Strategy

### Connection Pooling:
- Utilizes `pool_size=20`, `max_overflow=10`, and `pool_pre_ping=True` to guarantee robust connection recycling in cloud environments.

### Backup & Disaster Recovery:
- Daily automated snapshots of managed PostgreSQL (`pg_dump` with gzip compression).
- Point-in-time recovery (PITR) retained for 14 rolling days.
- Uploaded dataset persistence mounted to persistent block volumes (`/app/uploaded_datasets`).
