"""Tests for Phase 15 Network Intelligence, PCAP ingestion, and Engine Provenance."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from scapy.all import IP, TCP, Raw, wrpcap

from app.main import app
from app.network.pcap_parser import PacketParser
from app.network.capture_service import CaptureService
from app.network.pipeline import IngestionPipeline

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    login_resp = client.post("/api/auth/login", json={"username": "demo", "password": "traceguard2024"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_sample_pcap(file_path: str, is_anomalous: bool = False):
    """Generate a valid synthetic PCAP capture file with TCP/HTTP packets for testing."""
    packets = []

    # 1. TCP SYN (Handshake -> CONNECT)
    syn_pkt = IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=54321, dport=80, flags="S", seq=1000)
    packets.append(syn_pkt)

    if not is_anomalous:
        # 2. HTTP GET Request
        http_req = "GET /api/v1/telemetry HTTP/1.1\r\nHost: traceguard.local\r\nUser-Agent: TestClient\r\n\r\n"
        req_pkt = IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=54321, dport=80, flags="PA", seq=1001, ack=1) / Raw(load=http_req.encode())
        packets.append(req_pkt)

        # 3. HTTP 200 OK Response
        http_resp = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 15\r\n\r\n{\"status\":\"ok\"}"
        resp_pkt = IP(src="192.168.1.1", dst="192.168.1.100") / TCP(sport=80, dport=54321, flags="PA", seq=1, ack=1001 + len(http_req)) / Raw(load=http_resp.encode())
        packets.append(resp_pkt)

        # 4. TCP FIN (Teardown -> CLOSE)
        fin_pkt = IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=54321, dport=80, flags="FA", seq=1001 + len(http_req), ack=1 + len(http_resp))
        packets.append(fin_pkt)
    else:
        # Anomalous: Out-of-order 500 error response without prior request (FSM violation)
        bad_resp = "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n"
        resp_pkt = IP(src="192.168.1.1", dst="192.168.1.100") / TCP(sport=80, dport=54321, flags="PA", seq=1, ack=1001) / Raw(load=bad_resp.encode())
        packets.append(resp_pkt)

    wrpcap(file_path, packets)


def test_pcap_parser_valid_stream():
    """Verify PCAP parser reconstructs bidirectional HTTP flow and extracts standard FSM symbols."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        create_sample_pcap(tmp_name, is_anomalous=False)
        events = PacketParser.parse_pcap_file(tmp_name)
        assert len(events) >= 3

        event_types = [e["event_type"] for e in events]
        assert "CONNECT" in event_types
        assert "REQUEST" in event_types
        assert "RESPONSE_200" in event_types
        assert "CLOSE" in event_types

        # Verify privacy sanitation: No raw Authorization or passwords stored
        for e in events:
            assert e["protocol"] == "HTTP"
            assert "password" not in str(e).lower()
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def test_network_status_endpoint(auth_headers):
    """Verify /api/network/status returns provider diagnosis and active telemetry structure."""
    resp = client.get("/api/network/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "is_capturing" in data
    assert "provider_status" in data
    assert "packets_received" in data
    assert "events_processed" in data
    assert "alerts_generated" in data


def test_network_interfaces_endpoint():
    """Verify /api/network/interfaces enumerates host interfaces."""
    resp = client.get("/api/network/interfaces")
    assert resp.status_code == 200
    data = resp.json()
    assert "interfaces" in data
    assert len(data["interfaces"]) >= 1
    assert any(i["ip"] == "127.0.0.1" for i in data["interfaces"])


def test_pcap_upload_endpoint(auth_headers):
    """Verify /api/network/pcap/upload parses file, runs detection, and returns summary."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        create_sample_pcap(tmp_name, is_anomalous=False)
        with open(tmp_name, "rb") as f:
            resp = client.post(
                "/api/network/pcap/upload",
                files={"file": ("test.pcap", f, "application/vnd.tcpdump.pcap")},
                headers=auth_headers
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["filename"] == "test.pcap"
        assert data["packets_parsed"] >= 3
        assert data["events_processed"] >= 3
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def test_pcap_upload_invalid_extension(auth_headers):
    """Verify reject on unsupported file extension."""
    resp = client.post(
        "/api/network/pcap/upload",
        files={"file": ("test.exe", b"malicious", "application/octet-stream")},
        headers=auth_headers
    )
    assert resp.status_code == 400
    assert "Unsupported capture file format" in resp.json()["detail"]


def test_live_capture_prerequisite_enforcement(auth_headers):
    """Verify live capture start either succeeds or gives actionable prerequisite error when Npcap is missing."""
    service = CaptureService.get_instance()
    prov = service.get_pcap_provider_status()

    resp = client.post("/api/network/capture/start", json={"interface": "default"}, headers=auth_headers)
    if not prov["available"]:
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert detail["error"] == "LIVE_CAPTURE_UNAVAILABLE"
        assert "Npcap" in detail["remedy"]
    else:
        assert resp.status_code == 200


def test_alerts_analytics_endpoint(auth_headers):
    """Verify /api/alerts/analytics aggregates severity, engine provenance, and time series."""
    resp = client.get("/api/alerts/analytics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "severity_distribution" in data
    assert "engine_distribution" in data
    assert "risk_distribution" in data
    assert "engine_correlation" in data
    assert "time_series" in data

    # Verify all expected engine keys exist
    for k in ["fsm", "ml", "hybrid", "unknown"]:
        assert k in data["engine_distribution"]

    # Verify all severity keys exist
    for k in ["critical", "high", "medium", "low"]:
        assert k in data["severity_distribution"]


def test_dashboard_summary_with_time_range(auth_headers):
    """Verify /api/dashboard/summary handles time_range query parameter."""
    resp_all = client.get("/api/dashboard/summary?time_range=all", headers=auth_headers)
    assert resp_all.status_code == 200
    data_all = resp_all.json()
    assert "engine_distribution" in data_all
    assert "unknown" in data_all["engine_distribution"]

    resp_24h = client.get("/api/dashboard/summary?time_range=24h", headers=auth_headers)
    assert resp_24h.status_code == 200
