"""Automata Adversarial Stress Test Suite: 56 Exhaustive Probes.

Executes and verifies 56 distinct stress probes against the HTTP DFA and Step-Execute engine:
- Category 1: Canonical Valid Paths (Probes 1-8)
- Category 2: Pipelined Keep-Alive Valid Sessions (Probes 9-14)
- Category 3: Incomplete Legal Prefixes (Probes 15-20)
- Category 4: Out-of-Order Protocol Transitions (Probes 21-30)
- Category 5: Post-CLOSED Terminal Violations (Probes 31-36)
- Category 6: TRAP State Absorbing Self-Loops for all 13 symbols (Probes 37-49)
- Category 7: Malformed, Empty & Boundary Sequences (Probes 50-56)
"""
import json
import os
import pytest
from app.api.protocols import get_formal_automaton
from app.detection.fsm import FSMEngine
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

PROBES = [
    # Category 1: Canonical Valid Paths (1-8)
    {"id": 1, "name": "Canonical 200 OK", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 2, "name": "Canonical 301 Redirect", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_301", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 3, "name": "Auth Failure 401", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "AUTH_FAILURE", "RESPONSE_401", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 4, "name": "Auth Failure 403", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "AUTH_FAILURE", "RESPONSE_403", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 5, "name": "Server Error 500", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_500", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 6, "name": "Malformed Error Response", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "MALFORMED", "ERROR_RESPONSE", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 7, "name": "Connected Idle Timeout", "category": "Valid Path", "events": ["CONNECT", "TIMEOUT"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 8, "name": "Malformed Direct Close", "category": "Valid Path", "events": ["CONNECT", "REQUEST", "MALFORMED", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},

    # Category 2: Pipelined Keep-Alive Valid Sessions (9-14)
    {"id": 9, "name": "Keep-Alive 2 Cycles", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 10, "name": "Keep-Alive 200 then 301", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_301", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 11, "name": "Keep-Alive 200 then 401", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_FAILURE", "RESPONSE_401", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 12, "name": "Keep-Alive 200 then 500", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_500", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 13, "name": "Keep-Alive with Malformed Recovered", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "MALFORMED", "ERROR_RESPONSE", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 14, "name": "Keep-Alive 4 Cycles", "category": "Keep-Alive", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},

    # Category 3: Incomplete Legal Prefixes (15-20)
    {"id": 15, "name": "Prefix Connect Only", "category": "Incomplete Prefix", "events": ["CONNECT"], "expected": "INCOMPLETE_VALID", "final_state": "CONNECTED"},
    {"id": 16, "name": "Prefix Connect Request", "category": "Incomplete Prefix", "events": ["CONNECT", "REQUEST"], "expected": "INCOMPLETE_VALID", "final_state": "REQUEST_RECEIVED"},
    {"id": 17, "name": "Prefix Auth Passed", "category": "Incomplete Prefix", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS"], "expected": "INCOMPLETE_VALID", "final_state": "AUTH_CHECKED"},
    {"id": 18, "name": "Prefix Auth Failed", "category": "Incomplete Prefix", "events": ["CONNECT", "REQUEST", "AUTH_FAILURE"], "expected": "INCOMPLETE_VALID", "final_state": "AUTH_FAILED"},
    {"id": 19, "name": "Prefix Response Emitted Unclosed", "category": "Incomplete Prefix", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200"], "expected": "INCOMPLETE_VALID", "final_state": "RESPONSE_SENT"},
    {"id": 20, "name": "Prefix In Error State", "category": "Incomplete Prefix", "events": ["CONNECT", "REQUEST", "MALFORMED"], "expected": "INCOMPLETE_VALID", "final_state": "ERROR"},

    # Category 4: Out-of-Order Violations (21-30)
    {"id": 21, "name": "Early Response Before Request", "category": "Out-of-Order", "events": ["CONNECT", "RESPONSE_200"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 22, "name": "Auth Success Before Connect", "category": "Out-of-Order", "events": ["AUTH_SUCCESS"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 23, "name": "Request Without Connect", "category": "Out-of-Order", "events": ["REQUEST"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 24, "name": "Immediate Close from IDLE", "category": "Out-of-Order", "events": ["CLOSE"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 25, "name": "Auth Bypass 200 Direct", "category": "Out-of-Order", "events": ["CONNECT", "REQUEST", "RESPONSE_200"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 26, "name": "Auth Bypass 401 Direct", "category": "Out-of-Order", "events": ["CONNECT", "REQUEST", "RESPONSE_401"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 27, "name": "Timeout from IDLE", "category": "Out-of-Order", "events": ["TIMEOUT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 28, "name": "Timeout from Auth Checked", "category": "Out-of-Order", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "TIMEOUT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 29, "name": "Double Connect Violation", "category": "Out-of-Order", "events": ["CONNECT", "CONNECT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 30, "name": "Connect and Request Twice", "category": "Out-of-Order", "events": ["CONNECT", "REQUEST", "REQUEST"], "expected": "REJECTED", "final_state": "TRAP"},

    # Category 5: Post-CLOSED Terminal Violations (31-36)
    {"id": 31, "name": "Post-Closed Request", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "REQUEST"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 32, "name": "Post-Closed Connect", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "CONNECT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 33, "name": "Post-Closed Response", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "RESPONSE_200"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 34, "name": "Post-Closed Auth", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "AUTH_SUCCESS"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 35, "name": "Post-Closed Close", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "CLOSE"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 36, "name": "Post-Closed Timeout", "category": "Terminal Violation", "events": ["CONNECT", "TIMEOUT", "TIMEOUT"], "expected": "REJECTED", "final_state": "TRAP"},

    # Category 6: TRAP Absorbing Self-Loops for all 13 Symbols (37-49)
    {"id": 37, "name": "TRAP Self-Loop on CONNECT", "category": "Trap Absorption", "events": ["CLOSE", "CONNECT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 38, "name": "TRAP Self-Loop on REQUEST", "category": "Trap Absorption", "events": ["CLOSE", "REQUEST"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 39, "name": "TRAP Self-Loop on AUTH_SUCCESS", "category": "Trap Absorption", "events": ["CLOSE", "AUTH_SUCCESS"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 40, "name": "TRAP Self-Loop on AUTH_FAILURE", "category": "Trap Absorption", "events": ["CLOSE", "AUTH_FAILURE"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 41, "name": "TRAP Self-Loop on RESPONSE_200", "category": "Trap Absorption", "events": ["CLOSE", "RESPONSE_200"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 42, "name": "TRAP Self-Loop on RESPONSE_301", "category": "Trap Absorption", "events": ["CLOSE", "RESPONSE_301"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 43, "name": "TRAP Self-Loop on RESPONSE_401", "category": "Trap Absorption", "events": ["CLOSE", "RESPONSE_401"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 44, "name": "TRAP Self-Loop on RESPONSE_403", "category": "Trap Absorption", "events": ["CLOSE", "RESPONSE_403"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 45, "name": "TRAP Self-Loop on RESPONSE_500", "category": "Trap Absorption", "events": ["CLOSE", "RESPONSE_500"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 46, "name": "TRAP Self-Loop on CLOSE", "category": "Trap Absorption", "events": ["CLOSE", "CLOSE"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 47, "name": "TRAP Self-Loop on TIMEOUT", "category": "Trap Absorption", "events": ["CLOSE", "TIMEOUT"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 48, "name": "TRAP Self-Loop on MALFORMED", "category": "Trap Absorption", "events": ["CLOSE", "MALFORMED"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 49, "name": "TRAP Self-Loop on ERROR_RESPONSE", "category": "Trap Absorption", "events": ["CLOSE", "ERROR_RESPONSE"], "expected": "REJECTED", "final_state": "TRAP"},

    # Category 7: Boundary, Empty & Malformed Symbols (50-56)
    {"id": 50, "name": "Empty Sequence Epsilon", "category": "Boundary", "events": [], "expected": "INCOMPLETE_VALID", "final_state": "IDLE"},
    {"id": 51, "name": "Unknown Symbol Injection", "category": "Boundary", "events": ["CONNECT", "NON_EXISTENT_OPCODE"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 52, "name": "Deep 10-Cycle Persistent Trace", "category": "Boundary", "events": ["CONNECT"] + ["REQUEST", "AUTH_SUCCESS", "RESPONSE_200"] * 10 + ["CLOSE"], "expected": "ACCEPTED", "final_state": "CLOSED"},
    {"id": 53, "name": "Unterminated Deep Trace", "category": "Boundary", "events": ["CONNECT"] + ["REQUEST", "AUTH_SUCCESS", "RESPONSE_200"] * 10, "expected": "INCOMPLETE_VALID", "final_state": "RESPONSE_SENT"},
    {"id": 54, "name": "Malformed Immediate RST", "category": "Boundary", "events": ["MALFORMED"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 55, "name": "Duplicate Response from RESPONSE_SENT", "category": "Boundary", "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "RESPONSE_200"], "expected": "REJECTED", "final_state": "TRAP"},
    {"id": 56, "name": "Auth Failure Without Request", "category": "Boundary", "events": ["CONNECT", "AUTH_FAILURE"], "expected": "REJECTED", "final_state": "TRAP"},
]


@pytest.mark.parametrize("probe", PROBES, ids=[f"probe_{p['id']}_{p['name'].replace(' ', '_')}" for p in PROBES])
def test_adversarial_probe_execution(probe):
    """Execute probe and assert against formal DFA mathematical properties."""
    resp = client.post("/api/protocols/http/step-execute", json={"events": probe["events"]})
    assert resp.status_code == 200, f"Probe {probe['id']} failed with status {resp.status_code}"
    data = resp.json()

    assert data["verdict"] == probe["expected"], (
        f"Probe {probe['id']} ({probe['name']}) expected {probe['expected']}, got {data['verdict']}"
    )
    assert data["final_state"] == probe["final_state"], (
        f"Probe {probe['id']} ({probe['name']}) expected final state {probe['final_state']}, got {data['final_state']}"
    )


def test_export_all_56_probe_results_to_json():
    """Execute all 56 probes and export full audited evidence to qa/phase14_2/adversarial-probe-results.json."""
    results = []
    passed_count = 0

    for p in PROBES:
        resp = client.post("/api/protocols/http/step-execute", json={"events": p["events"]})
        assert resp.status_code == 200
        data = resp.json()

        is_passed = (data["verdict"] == p["expected"]) and (data["final_state"] == p["final_state"])
        if is_passed:
            passed_count += 1

        results.append({
            "probe_id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "input_events": p["events"],
            "expected_verdict": p["expected"],
            "observed_verdict": data["verdict"],
            "expected_final_state": p["final_state"],
            "observed_final_state": data["final_state"],
            "all_transitions_valid": data["all_transitions_valid"],
            "is_in_accepting_state": data["is_in_accepting_state"],
            "status": "PASS" if is_passed else "FAIL"
        })

    assert passed_count == 56, f"Expected 56/56 probes to pass, got {passed_count}/56"

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qa", "phase14_2")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "adversarial-probe-results.json")

    with open(output_file, "w") as f:
        json.dump({
            "total_probes": len(results),
            "passed_probes": passed_count,
            "pass_rate": f"{(passed_count / len(results)) * 100:.1f}%",
            "probes": results
        }, f, indent=2)

    assert os.path.exists(output_file)
