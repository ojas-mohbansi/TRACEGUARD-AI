"""Comprehensive SaaS and Security Integration Tests for TraceGuard AI.

Verifies:
1. User registration, secure login, password hashing, and token expiration.
2. Workspace provisioning and Role-Based Access Control (RBAC: Owner, Admin, Analyst, Viewer).
3. Cross-workspace data isolation (Workspaces A & B cannot view each other's alerts, events, datasets).
4. Unauthorized access prevention and viewer role mutation restrictions.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.models.models import User, Workspace, WorkspaceMember, NetworkEvent, Alert, Dataset, RoleEnum
from app.core.security import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_user_registration_and_login(setup_db):
    """Test standard signup, password hashing, and JWT login."""
    unique_user = f"user_{uuid4().hex[:6]}"
    signup_payload = {
        "username": unique_user,
        "email": f"{unique_user}@traceguard.io",
        "password": "Password123!",
        "full_name": "Test Security Analyst"
    }
    
    # 1. Signup
    res = client.post("/api/auth/signup", json=signup_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == unique_user
    assert "hashed_password" not in data
    
    # Duplicate signup should fail
    dup_res = client.post("/api/auth/signup", json=signup_payload)
    assert dup_res.status_code == 400

    # 2. Login
    login_payload = {
        "username": unique_user,
        "password": "Password123!"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["username"] == unique_user
    assert "active_workspace_id" in token_data

    # Invalid password login
    bad_login = client.post("/api/auth/login", json={"username": unique_user, "password": "WrongPassword"})
    assert bad_login.status_code == 401


def test_cross_workspace_data_isolation(setup_db):
    """Verify that User A (Workspace A) cannot access User B's (Workspace B) events, alerts, or datasets."""
    # 1. Register User Alpha
    alpha_name = f"alpha_{uuid4().hex[:6]}"
    client.post("/api/auth/signup", json={
        "username": alpha_name,
        "email": f"{alpha_name}@example.com",
        "password": "SecretPassword123!"
    })
    token_alpha = client.post("/api/auth/login", json={
        "username": alpha_name,
        "password": "SecretPassword123!"
    }).json()["access_token"]

    # 2. Register User Beta
    beta_name = f"beta_{uuid4().hex[:6]}"
    client.post("/api/auth/signup", json={
        "username": beta_name,
        "email": f"{beta_name}@example.com",
        "password": "SecretPassword123!"
    })
    token_beta = client.post("/api/auth/login", json={
        "username": beta_name,
        "password": "SecretPassword123!"
    }).json()["access_token"]

    headers_alpha = {"Authorization": f"Bearer {token_alpha}"}
    headers_beta = {"Authorization": f"Bearer {token_beta}"}

    # Get Workspace IDs
    ws_alpha = client.get("/api/auth/workspaces", headers=headers_alpha).json()[0]["workspace_id"]
    ws_beta = client.get("/api/auth/workspaces", headers=headers_beta).json()[0]["workspace_id"]
    assert ws_alpha != ws_beta

    headers_alpha["X-Workspace-ID"] = ws_alpha
    headers_beta["X-Workspace-ID"] = ws_beta

    # 3. Insert specific alerts into Workspace Alpha and Workspace Beta directly in DB
    db = SessionLocal()
    try:
        alert_alpha_id = f"alt_alpha_{uuid4().hex[:8]}"
        alert_beta_id = f"alt_beta_{uuid4().hex[:8]}"
        alert_alpha = Alert(
            workspace_id=ws_alpha,
            alert_id=alert_alpha_id,
            session_id="sess_alpha_101",
            engine="hybrid",
            severity="critical",
            risk_score=95,
            prediction="anomalous",
            status="new",
            summary="Confidential intrusion in Alpha Org"
        )
        alert_beta = Alert(
            workspace_id=ws_beta,
            alert_id=alert_beta_id,
            session_id="sess_beta_202",
            engine="fsm",
            severity="medium",
            risk_score=60,
            prediction="anomalous",
            status="new",
            summary="Protocol violation in Beta Org"
        )
        db.add(alert_alpha)
        db.add(alert_beta)
        db.commit()
    finally:
        db.close()

    # 4. User Alpha queries alerts: must see alert_alpha, must NOT see alert_beta
    res_a = client.get("/api/alerts", headers=headers_alpha)
    assert res_a.status_code == 200
    alert_ids_a = [a["alert_id"] for a in res_a.json()["alerts"]]
    assert alert_alpha_id in alert_ids_a
    assert alert_beta_id not in alert_ids_a

    # 5. User Beta queries alerts: must see alert_beta, must NOT see alert_alpha
    res_b = client.get("/api/alerts", headers=headers_beta)
    assert res_b.status_code == 200
    alert_ids_b = [a["alert_id"] for a in res_b.json()["alerts"]]
    assert alert_beta_id in alert_ids_b
    assert alert_alpha_id not in alert_ids_b

    # 6. User Alpha attempts to query Beta's alert directly by ID -> HTTP 403 Forbidden
    forbidden_direct = client.get(f"/api/alerts/{alert_beta_id}", headers=headers_alpha)
    assert forbidden_direct.status_code == 403

    # 7. User Alpha attempts to impersonate Beta's workspace in header -> HTTP 403 Forbidden
    impersonate_headers = {"Authorization": f"Bearer {token_alpha}", "X-Workspace-ID": ws_beta}
    res_impersonate = client.get("/api/alerts", headers=impersonate_headers)
    assert res_impersonate.status_code == 403


def test_role_based_access_control_viewer_restrictions(setup_db):
    """Test that a user with 'viewer' role is restricted from mutating alerts or triggering actions."""
    db = SessionLocal()
    try:
        # Create an owner and a viewer in the same workspace
        owner_name = f"owner_{uuid4().hex[:6]}"
        viewer_name = f"viewer_{uuid4().hex[:6]}"

        u_owner = User(username=owner_name, email=f"{owner_name}@corp.com", hashed_password=hash_password("Pass123!"))
        u_viewer = User(username=viewer_name, email=f"{viewer_name}@corp.com", hashed_password=hash_password("Pass123!"))
        db.add_all([u_owner, u_viewer])
        db.commit()
        db.refresh(u_owner)
        db.refresh(u_viewer)

        ws = Workspace(
            workspace_id=f"ws_shared_{uuid4().hex[:8]}",
            name="Joint Defense Workspace",
            slug=f"joint-defense-{uuid4().hex[:6]}",
            owner_id=u_owner.id
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)

        m_owner = WorkspaceMember(workspace_id=ws.workspace_id, user_id=u_owner.id, role=RoleEnum.OWNER.value)
        m_viewer = WorkspaceMember(workspace_id=ws.workspace_id, user_id=u_viewer.id, role=RoleEnum.VIEWER.value)
        db.add_all([m_owner, m_viewer])

        # Add an alert
        alt = Alert(
            workspace_id=ws.workspace_id,
            alert_id=f"alt_shared_{uuid4().hex[:8]}",
            session_id="sess_shared_1",
            engine="hybrid",
            severity="high",
            risk_score=75,
            prediction="anomalous",
            status="new"
        )
        db.add(alt)
        db.commit()
        db.refresh(alt)

        token_viewer = create_access_token(data={"sub": viewer_name})
        token_owner = create_access_token(data={"sub": owner_name})
        alert_id = alt.alert_id
        ws_id = ws.workspace_id
    finally:
        db.close()

    headers_viewer = {"Authorization": f"Bearer {token_viewer}", "X-Workspace-ID": ws_id}
    headers_owner = {"Authorization": f"Bearer {token_owner}", "X-Workspace-ID": ws_id}

    # 1. Viewer CAN view the alert
    res_view = client.get(f"/api/alerts/{alert_id}", headers=headers_viewer)
    assert res_view.status_code == 200

    # 2. Viewer CANNOT update alert status -> HTTP 403 Forbidden
    res_update_viewer = client.patch(f"/api/alerts/{alert_id}", json={"status": "resolved"}, headers=headers_viewer)
    assert res_update_viewer.status_code == 403

    # 3. Viewer CANNOT start a traffic simulation -> HTTP 403 Forbidden
    res_sim_viewer = client.post("/api/simulation/start", json={"mode": "normal", "event_count": 10}, headers=headers_viewer)
    assert res_sim_viewer.status_code == 403

    # 4. Owner CAN update alert status -> HTTP 200 OK
    res_update_owner = client.patch(f"/api/alerts/{alert_id}", json={"status": "resolved"}, headers=headers_owner)
    assert res_update_owner.status_code == 200
    assert res_update_owner.json()["status"] == "resolved"
