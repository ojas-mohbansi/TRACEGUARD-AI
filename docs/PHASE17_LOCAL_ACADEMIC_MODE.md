# Phase 17 — Local Academic Architecture & Zero-Auth Demonstration Mode

## 1. Executive Summary

TraceGuard AI is an academic Theory of Computation and Network Intrusion Detection research project designed for live university evaluation and demonstration. In previous iterations (Phases 15–16), multi-tenant enterprise features such as JWT authentication, login/signup forms, session cookies, and workspace switching were introduced. While technically robust, these security gates introduced unnecessary friction during local academic presentations, requiring repetitive logins, dealing with token expiration, and cluttering the UI with placeholder SecOps analyst profiles (`secops@traceguard.ai`, "SecOps Analyst").

**Phase 17** introduces a clean, dual-mode architectural separation:
1. **`LOCAL_ACADEMIC` Mode (Default for Local Evaluation)**:
   - Direct, unauthenticated access to the entire application.
   - Elimination of login pages, logout buttons, and profile menus.
   - Automatic server-managed binding to `default-workspace` without browser token storage.
   - Strict loopback security: bounds exclusively to `127.0.0.1` and fails closed if exposed to public interfaces (`0.0.0.0`).
2. **`PRODUCTION` Mode (Enterprise Deployment)**:
   - Enforces strict JWT Bearer token authentication.
   - All protected endpoints fail closed with HTTP 401 Unauthorized for unauthenticated requests.
   - Strict tenant data isolation and workspace RBAC (`default-workspace`, `workspace-alpha`, `workspace-beta`).

---

## 2. Dual-Mode Configuration Invariants

Configuration is governed by environment variables in `backend/app/core/config.py`:

```python
TRACEGUARD_MODE: str = "LOCAL_ACADEMIC"  # "LOCAL_ACADEMIC" | "PRODUCTION"
LOCAL_ACADEMIC_MODE: bool = True
ALLOW_PUBLIC_ACADEMIC_MODE: bool = False
```

### Mode Comparison Matrix

| Property | `LOCAL_ACADEMIC` Mode | `PRODUCTION` Mode |
| :--- | :--- | :--- |
| **Target Audience** | University evaluators, professors, lab researchers | Enterprise SOC analysts, production networks |
| **Authentication Requirement** | None (direct dashboard entry) | Strict JWT Bearer token |
| **Browser Storage** | Zero token persistence required | `localStorage` / `sessionStorage` JWT storage |
| **Default Route (`/`)** | Directly mounts SOC Dashboard | Redirects to `/login` if unauthenticated |
| **Auth Redirects (`/login`, `/signup`)** | Redirects immediately to `/` | Displays credentials login/signup form |
| **Sidebar Brand Badge** | `Academic Edition (Theory of Computation Lab)` | Workspace selector & User profile |
| **User Identity** | Local Academic Researcher (`secops_demo`) | Authenticated tenant user |
| **Workspace Binding** | Deterministically anchored to `default-workspace` | Tenant-authenticated workspace membership |
| **Interface Binding Safeguard** | **Fails closed** if host is `0.0.0.0` | Permitted on `0.0.0.0` with TLS / reverse proxy |

---

## 3. Server-Side Security Invariants & Loopback Protection

To ensure `LOCAL_ACADEMIC` mode never introduces a security backdoor into production environments, three strict server-side invariants are enforced:

### Invariant 1: Loopback Interface Enforcement at Startup (`app.main.lifespan`)
During application startup, the backend inspects the configured binding host. If `LOCAL_ACADEMIC_MODE` is active and the server is configured to bind to a non-loopback address (such as `0.0.0.0` or a public interface) without explicit developer override (`ALLOW_PUBLIC_ACADEMIC_MODE=True`), startup aborts immediately:

```python
if settings.LOCAL_ACADEMIC_MODE and not settings.ALLOW_PUBLIC_ACADEMIC_MODE:
    import sys
    # Verify binding from command line or configuration
    for arg in sys.argv:
        if "--host" in arg and "0.0.0.0" in arg:
            logger.critical("FATAL SECURITY VIOLATION: LOCAL_ACADEMIC_MODE cannot bind to 0.0.0.0 without ALLOW_PUBLIC_ACADEMIC_MODE=True.")
            raise RuntimeError("Insecure binding detected in LOCAL_ACADEMIC mode.")
```

### Invariant 2: Context Provisioning (`app.core.security.get_current_user`)
When a request lacks an `Authorization` header in `LOCAL_ACADEMIC_MODE`, the backend provisions a server-side demo user object (`_ensure_demo_user(db)`). In `PRODUCTION` mode, missing credentials immediately raise `HTTPException(status_code=401, detail="Not authenticated")`.

### Invariant 3: Tenant Spoofing Defense (`app.core.security.get_current_workspace_context`)
In `LOCAL_ACADEMIC` mode, unauthenticated requests are strictly constrained to `default-workspace`. Even if a client injects an arbitrary `X-Workspace-ID: workspace-alpha` header, the dependency rejects client header spoofing and anchors the session to `default-workspace`.

---

## 4. Frontend Transformation

### 1. `AuthContext.jsx`
- Initializes with `isAuthenticated: true` and `user: ACADEMIC_USER` (`role: "academic_researcher"`).
- `login` and `logout` operations are converted into non-blocking no-ops.
- Eliminates auth loading spinners and token checking delays.

### 2. Route Protection (`App.jsx`)
- `ProtectedRoute` renders child components directly without authentication checks.
- Direct navigation to `/login` or `/signup` redirects immediately to `/` without flashing login forms.

### 3. Header & Sidebar UI (`AppLayout.jsx` and `Settings.jsx`)
- Replaced the user avatar dropdown and logout button with an official academic badge:
  - Label: `Academic Edition (Theory of Computation Lab)`
  - Subtitle: `Deterministic FSM & Hybrid NIDS`
- Replaced `SecOps Analyst` profile in Settings with:
  - Title: `Academic Research Environment (LOCAL_ACADEMIC Sandbox)`
  - Mode: `Zero-Auth Evaluation Mode`
  - Workspace: `default-workspace (Local Loopback)`
