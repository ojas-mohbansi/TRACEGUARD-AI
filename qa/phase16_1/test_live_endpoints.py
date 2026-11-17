import os
import sys
import json
import asyncio
import requests
import websockets

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/events"

def run_endpoint_audit():
    audit_results = {}
    
    # 1. Health check
    print("Testing /api/health...")
    r = requests.get(f"{BASE_URL}/api/health")
    audit_results["health"] = {
        "status_code": r.status_code,
        "response": r.json()
    }
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    
    # Authenticate to obtain token for protected endpoints
    print("Authenticating demo user...")
    r_auth = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "demo", "password": "traceguard2024"})
    assert r_auth.status_code == 200, f"Auth failed: {r_auth.status_code}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    audit_results["auth"] = {
        "status_code": r_auth.status_code,
        "token_type": r_auth.json().get("token_type")
    }
    
    # 2. Network Diagnostic Endpoint
    print("Testing /api/network/diagnose...")
    r_diag = requests.post(f"{BASE_URL}/api/network/diagnose", headers=headers)
    audit_results["network_diagnose"] = {
        "status_code": r_diag.status_code,
        "state": r_diag.json().get("provider_status", {}).get("state"),
        "available": r_diag.json().get("provider_status", {}).get("available"),
        "driver": r_diag.json().get("provider_status", {}).get("provider"),
        "version": r_diag.json().get("provider_status", {}).get("version")
    }
    assert r_diag.status_code == 200, f"Network diagnose failed: {r_diag.status_code}"
    
    # 3. Network Interface Enumeration
    print("Testing /api/network/interfaces...")
    r_ifaces = requests.get(f"{BASE_URL}/api/network/interfaces", headers=headers)
    audit_results["network_interfaces"] = {
        "status_code": r_ifaces.status_code,
        "count": len(r_ifaces.json().get("interfaces", [])),
        "interfaces_sample": [
            {"id": i["id"], "name": i["name"], "ip": i.get("ip")}
            for i in r_ifaces.json().get("interfaces", [])[:3]
        ]
    }
    assert r_ifaces.status_code == 200, f"Network interfaces failed: {r_ifaces.status_code}"
    
    # 4. Showcase Scenario Execution (All 4 scenarios)
    audit_results["showcase_scenarios"] = {}
    for sc in ["normal", "fsm_only", "ml_only", "hybrid"]:
        print(f"Testing /api/detection/showcase/run with scenario '{sc}'...")
        r_sc = requests.post(
            f"{BASE_URL}/api/detection/showcase/run",
            json={"scenario": sc, "custom_notes": f"Phase 16.1 Live Audit: {sc}"},
            headers=headers
        )
        assert r_sc.status_code == 200, f"Showcase {sc} failed: {r_sc.status_code} - {r_sc.text}"
        data = r_sc.json()
        audit_results["showcase_scenarios"][sc] = {
            "status_code": r_sc.status_code,
            "session_id": data.get("session_id"),
            "events_count": data.get("events_count"),
            "attribution": data.get("attribution"),
            "risk_score": data.get("risk_score"),
            "severity": data.get("severity"),
            "fsm_violation": data.get("fsm_evaluation", {}).get("violation"),
            "ml_anomalous": data.get("ml_evaluation", {}).get("is_anomalous")
        }
        
    # 5. Engine Activity Aggregation
    print("Testing /api/alerts/engine-activity...")
    r_act = requests.get(f"{BASE_URL}/api/alerts/engine-activity", headers=headers)
    assert r_act.status_code == 200, f"Engine activity failed: {r_act.status_code}"
    act_data = r_act.json()
    audit_results["engine_activity"] = {
        "status_code": r_act.status_code,
        "final_attribution": act_data.get("final_attribution"),
        "engine_activity": act_data.get("engine_activity")
    }
    
    # 6. Final Alert Attribution & Analytics
    print("Testing /api/alerts/analytics...")
    r_an = requests.get(f"{BASE_URL}/api/alerts/analytics", headers=headers)
    assert r_an.status_code == 200, f"Alert analytics failed: {r_an.status_code}"
    an_data = r_an.json()
    audit_results["alert_analytics"] = {
        "status_code": r_an.status_code,
        "total_alerts": an_data.get("total_alerts"),
        "avg_risk_score": an_data.get("avg_risk_score"),
        "engine_distribution": an_data.get("engine_distribution"),
        "engine_correlation": an_data.get("engine_correlation"),
        "fsm_evidence_count": len(an_data.get("fsm_evidence", []))
    }
    
    # 7. Threat Forensics & Alerts detail endpoint
    print("Testing /api/alerts (list & detail)...")
    r_list = requests.get(f"{BASE_URL}/api/alerts?limit=5", headers=headers)
    assert r_list.status_code == 200, f"Alerts list failed: {r_list.status_code}"
    alerts_list = r_list.json().get("alerts", [])
    assert len(alerts_list) > 0, "Expected at least 1 alert"
    first_alert_id = alerts_list[0]["alert_id"]
    
    r_det = requests.get(f"{BASE_URL}/api/alerts/{first_alert_id}", headers=headers)
    assert r_det.status_code == 200, f"Alert detail failed: {r_det.status_code}"
    det_data = r_det.json()
    audit_results["threat_forensics"] = {
        "status_code": r_det.status_code,
        "alert_id": det_data.get("alert_id"),
        "engine": det_data.get("engine"),
        "risk_score": det_data.get("risk_score"),
        "has_events": "events" in det_data and len(det_data["events"]) > 0,
        "has_fsm_result": det_data.get("fsm_result") is not None,
        "has_ml_result": det_data.get("ml_result") is not None
    }
    
    # 8. WebSocket Connection and Event Updates
    print("Testing WebSocket connection...")
    async def test_ws():
        async with websockets.connect(WS_URL) as ws:
            # Trigger simulation run with 10 events to see live WS broadcast
            requests.post(
                f"{BASE_URL}/api/simulation/start",
                json={"duration": 1, "mode": "mixed", "event_count": 10, "speed": 0.01},
                headers=headers
            )
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(msg)
            return {"connected": True, "received_message_type": data.get("type", "event")}
            
    try:
        ws_res = asyncio.run(test_ws())
        audit_results["websocket"] = {
            "status": "connected_and_received",
            "details": ws_res
        }
    except Exception as e:
        audit_results["websocket"] = {
            "status": "warning",
            "error": str(e)
        }
        
    print("=== LIVE ENDPOINT AUDIT COMPLETE ===")
    print(json.dumps(audit_results, indent=2))
    
    with open("qa/phase16_1/endpoint_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

if __name__ == "__main__":
    run_endpoint_audit()
