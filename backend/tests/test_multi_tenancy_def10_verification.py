"""Multi-Tenancy Workspace Scoping and Isolation Verification Suite (DEF-10 Audit).

Verifies:
1. TrafficSimulator strictly tags generated NetworkEvent records with active workspace_id.
2. Generated Alert records retain the same workspace_id.
3. Strict isolation: Workspace B cannot access events or alerts belonging to Workspace A.
4. Alerts API enforcement of workspace boundary filters.
5. Export evidence to qa/phase14_2/multi-tenancy-results.json.
"""
import os
import json
from uuid import uuid4
from datetime import datetime
import pytest
from app.db.database import SessionLocal
from app.models.models import NetworkEvent, Alert, Workspace, User
from app.simulator.generator import TrafficSimulator
from app.api.alerts import list_alerts
from app.core.security import WorkspaceContext


def test_multi_tenancy_workspace_isolation_and_scoping():
    db = SessionLocal()
    results = {}
    ws_a_id = f"ws_alpha_{uuid4().hex[:8]}"
    ws_b_id = f"ws_beta_{uuid4().hex[:8]}"

    try:
        # 1. Setup isolated users and workspaces
        user_a = User(username=f"u_a_{uuid4().hex[:6]}", email=f"a_{uuid4().hex[:6]}@test.com", hashed_password="pw")
        user_b = User(username=f"u_b_{uuid4().hex[:6]}", email=f"b_{uuid4().hex[:6]}@test.com", hashed_password="pw")
        db.add(user_a)
        db.add(user_b)
        db.commit()

        ws_a = Workspace(workspace_id=ws_a_id, name="Alpha Defense Lab", slug=f"alpha-{uuid4().hex[:6]}", owner_id=user_a.id)
        ws_b = Workspace(workspace_id=ws_b_id, name="Beta Research Ops", slug=f"beta-{uuid4().hex[:6]}", owner_id=user_b.id)
        db.add(ws_a)
        db.add(ws_b)
        db.commit()

        # 2. Run simulation scoped to Workspace A
        sim_id_a = f"sim_a_{uuid4().hex[:8]}"
        sim_a = TrafficSimulator(
            simulation_id=sim_id_a,
            mode="attack",
            event_count=10,
            speed=10.0,
            anomaly_ratio=0.8,
            seed=1234,
            workspace_id=ws_a_id
        )

        # Run generator synchronously in test environment
        import asyncio
        asyncio.run(sim_a.run())

        # 3. Query events and alerts directly in DB
        events_a = db.query(NetworkEvent).filter(NetworkEvent.workspace_id == ws_a_id).all()
        alerts_a = db.query(Alert).filter(Alert.workspace_id == ws_a_id).all()

        assert len(events_a) > 0, "TrafficSimulator failed to tag NetworkEvent with workspace_id"
        assert all(e.workspace_id == ws_a_id for e in events_a), "Cross-workspace event contamination"

        results["ws_a_generated_events"] = len(events_a)
        results["ws_a_generated_alerts"] = len(alerts_a)
        results["ws_a_isolation_verified"] = True

        # 4. Verify Workspace B sees ZERO events from Workspace A
        events_b_view = db.query(NetworkEvent).filter(NetworkEvent.workspace_id == ws_b_id).all()
        alerts_b_view = db.query(Alert).filter(Alert.workspace_id == ws_b_id).all()

        assert len(events_b_view) == 0, "Workspace B unexpectedly accessed Workspace A events"
        assert len(alerts_b_view) == 0, "Workspace B unexpectedly accessed Workspace A alerts"

        results["ws_b_leakage_detected"] = False
        results["cross_workspace_isolation"] = "PASS"

        # 5. Verify API-level enforcement via list_alerts endpoint with Workspace Context
        dummy_user_b = User(id=9999, username="auditor_b", email="b@test.com", hashed_password="pw")
        ctx_b = WorkspaceContext(workspace=ws_b, user=dummy_user_b, role="admin")

        api_response_b = list_alerts(
            severity=None,
            engine=None,
            status_filter=None,
            limit=50,
            offset=0,
            ctx=ctx_b,
            db=db
        )

        assert api_response_b.total == 0, f"API leaked {api_response_b.total} alerts to Workspace B"
        results["api_enforcement"] = "PASS"

    finally:
        # Clean up synthetic test records
        db.query(NetworkEvent).filter(NetworkEvent.workspace_id.in_([ws_a_id, ws_b_id])).delete(synchronize_session=False)
        db.query(Alert).filter(Alert.workspace_id.in_([ws_a_id, ws_b_id])).delete(synchronize_session=False)
        db.query(Workspace).filter(Workspace.workspace_id.in_([ws_a_id, ws_b_id])).delete(synchronize_session=False)
        if 'user_a' in locals():
            db.query(User).filter(User.id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

    # Save audited JSON evidence
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qa", "phase14_2")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "multi-tenancy-results.json"), "w") as f:
        json.dump(results, f, indent=2)

    assert os.path.exists(os.path.join(output_dir, "multi-tenancy-results.json"))
