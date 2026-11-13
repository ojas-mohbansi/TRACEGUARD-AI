# TraceGuard AI — System Architecture

## Overview
TraceGuard AI is a cybersecurity SaaS platform that detects anomalous network-protocol event sequences using three detection engines: FSM, ML, and Hybrid.

## Technology Stack
| Layer | Technology |
|---|---|
| Frontend | React 18 + JavaScript (Vite) |
| Styling | Tailwind CSS 3 |
| Charts | Recharts |
| FSM Visualization | React Flow |
| Backend | Python 3.11 + FastAPI |
| ML | Scikit-learn (Isolation Forest, Random Forest) |
| Data Processing | NumPy + Pandas |
| Database | SQLite + SQLAlchemy |
| Real-time | WebSockets (native FastAPI) |
| Auth | JWT (python-jose) + bcrypt |

## Architectural Pattern
Modular monolith. Single FastAPI process serves REST + WebSocket. React SPA talks to it via fetch + WebSocket.

## Directory Ownership
| Directory | Owner |
|---|---|
| `frontend/` | Frontend Engineer |
| `backend/app/api/` | Backend Engineer |
| `backend/app/core/` | Backend Engineer |
| `backend/app/db/` | Backend Engineer |
| `backend/app/models/` | Backend Engineer |
| `backend/app/schemas/` | Backend Engineer |
| `backend/app/simulator/` | Backend Engineer |
| `backend/app/detection/fsm/` | FSM Engineer |
| `backend/app/detection/ml/` | ML Engineer |
| `backend/app/detection/hybrid/` | Backend Engineer (integrates FSM + ML) |
| `backend/app/detection/features/` | ML Engineer |
| `backend/app/evaluation/` | ML Engineer |
| `backend/tests/` | QA Engineer (others may add tests in their own dirs) |
| `datasets/` | ML Engineer |
| `models/` | ML Engineer |
| `docs/` | Product Architect / Orchestrator |

## Detection Pipeline
```
Event Stream → FSM Engine (transition validation)
            → Feature Extractor → ML Engine (anomaly scoring)
            → Hybrid Engine (combines FSM + ML results)
            → Alert Generation → Database + WebSocket broadcast
```

## Data Flow
1. Simulator generates synthetic protocol events
2. Events are stored in SQLite
3. Detection engines process events by session
4. Results are stored as alerts
5. WebSocket pushes live events + alerts to frontend
6. Frontend renders dashboards, visualizations, investigation views

## Key Design Decisions
- SQLite for simplicity (single-file DB, no server needed)
- Synthetic data only (no real packet capture)
- Deterministic seeds for reproducibility
- All three engines independently callable
- Common detection response format across engines
- JWT auth with demo account auto-creation
