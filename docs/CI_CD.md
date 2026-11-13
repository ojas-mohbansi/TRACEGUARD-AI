# TraceGuard AI - CI/CD & Engineering Infrastructure

## 1. Automated Workflow Pipeline

TraceGuard AI leverages **GitHub Actions** for continuous integration and automated quality gates located at `.github/workflows/ci.yml`.

### Pipeline Stages:
1. **Linting & Code Quality**:
   - Python code style inspection.
   - Pydantic schema validation checks.
2. **Backend Unit & Integration Testing**:
   - Executes 26 comprehensive automated test suites via `pytest`.
   - Boots a live ephemeral FastAPI ASGI background server to validate WebSocket streams and asynchronous simulator event dispatching.
   - Tests FSM state transitions, Isolation Forest anomaly scoring, and Hybrid risk fusion.
   - Tests security policies: user registration, password hashing, workspace isolation, and RBAC permission barriers.
3. **Frontend Production Build**:
   - Runs `npm ci` and `npm run build` using Vite.
   - Validates asset bundling, tree-shaking, CSS minification, and zero-error compilation.

---

## 2. Secrets Management & Operational Security

- **Repository Hygiene**: `.env` and SQLite `.db` binaries are strictly banned via `.gitignore` and `.dockerignore`.
- **Pre-Commit Checks**: Verify no hardcoded secrets or unhashed passwords exist in git staging.
- **Dependency Locking**: Python `requirements.txt` and npm `package-lock.json` specify deterministic package versions.
