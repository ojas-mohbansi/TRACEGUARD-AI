# TraceGuard AI - Security Model & Access Controls

## 1. Authentication Architecture

TraceGuard AI implements token-based authentication using **JSON Web Tokens (JWT)** and cryptographic password hashing.

### Password Security:
- Passwords are encrypted using **bcrypt** with a dynamic salt (`bcrypt.gensalt()`).
- Passwords are strictly encoded to UTF-8 and safely truncated to 72 bytes to mitigate bcrypt overflow bugs.

### JWT Token Management:
- Algorithmic standard: HMAC-SHA256 (`HS256`).
- Expiration: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (defaults to 24 hours / 1440 min).
- Signature validation: Enforces token payload integrity, rejecting forged, malformed, or expired bearer tokens with HTTP 401 Unauthorized.

---

## 2. Role-Based Access Control (RBAC) Matrix

Permissions are partitioned across four standardized roles within any given workspace:

| Permission / Action | Owner | Admin | Analyst | Viewer |
|---------------------|:-----:|:-----:|:-------:|:------:|
| View Dashboard & Metrics | ✅ | ✅ | ✅ | ✅ |
| View Live Monitor & Events | ✅ | ✅ | ✅ | ✅ |
| View Threat Details & Reports | ✅ | ✅ | ✅ | ✅ |
| Update Alert Status & Notes | ✅ | ✅ | ✅ | ❌ |
| Run Traffic Simulations | ✅ | ✅ | ✅ | ❌ |
| Upload & Manage Datasets | ✅ | ✅ | ✅ | ❌ |
| Run Detection Lab Benchmarks | ✅ | ✅ | ✅ | ❌ |
| Manage Workspace Members | ✅ | ✅ | ❌ | ❌ |
| Change Workspace Settings | ✅ | ✅ | ❌ | ❌ |
| Delete Workspace / Ownership Transfer | ✅ | ❌ | ❌ | ❌ |

All permission checks are executed server-side via `WorkspaceContext.can_operate()` and `WorkspaceContext.can_manage_members()`. Frontend role indications serve presentation purposes only.

---

## 3. Data Protection & Defense-in-Depth

### Cross-Workspace Boundary Enforcement:
- Automated tests (`backend/tests/test_saas_security.py`) formally verify that a user in Workspace A receives HTTP 403 / 404 when attempting to query or alter alerts, datasets, or simulations belonging to Workspace B.

### Input Sanitization & Request Throttling:
- **File Upload Protection**: Content length checks enforce `MAX_UPLOAD_SIZE_BYTES` (10MB maximum). Upload extension allowlisting restricts accepted inputs to `.csv` and `.json`.
- **Simulation Caps**: Clamped to a maximum of 2,000 synthetic events per run to safeguard ASGI event loops from thread starvation.
- **CORS Allowlisting**: Strict header and origin validation configured through `CORSMiddleware`.
- **Sensitive Data Scrubbing**: TraceGuard never exposes database passwords, JWT secrets, or internal filesystem absolute paths in logs or public API responses.
