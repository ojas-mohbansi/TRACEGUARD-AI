"""Tests for Phase 16.1 Capture Privacy Defaults, Non-Promiscuous Enforcment, and Payload Redaction."""
import pytest
from unittest.mock import MagicMock, patch
from scapy.all import IP, TCP, Raw

from app.network.capture_service import CaptureService
from app.network.pcap_parser import PacketParser, sanitize_payload_metadata
from app.models.models import NetworkEvent, Alert


def test_capture_service_defaults_to_non_promiscuous():
    """1. Verify default capture mode is non-promiscuous (promiscuous=False)."""
    service = CaptureService()
    
    with patch.object(service, "run_host_diagnostics") as mock_diag, \
         patch.object(service, "_resolve_scapy_interface", return_value="eth0"), \
         patch("app.network.capture_service.AsyncSniffer") as mock_sniffer:
        
        mock_diag.return_value = {"available": True, "state": "CAPTURE_READY", "message": "Ready", "guidance": ""}
        
        res = service.start_live_capture(interface="eth0")
        assert res["status"] == "started"
        assert res["promiscuous"] is False
        
        # Verify AsyncSniffer was initialized with promisc=False
        mock_sniffer.assert_called_once()
        _, kwargs = mock_sniffer.call_args
        assert kwargs["promisc"] is False
        assert kwargs["store"] is False
        assert kwargs["iface"] == "eth0"
        
        service.stop_capture()


def test_capture_service_explicit_promiscuous_opt_in():
    """2. Verify explicit opt-in behavior when promiscuous=True is requested."""
    service = CaptureService()
    
    with patch.object(service, "run_host_diagnostics") as mock_diag, \
         patch.object(service, "_resolve_scapy_interface", return_value="eth0"), \
         patch("app.network.capture_service.AsyncSniffer") as mock_sniffer, \
         patch("app.network.capture_service.logger.warning") as mock_log_warn:
        
        mock_diag.return_value = {"available": True, "state": "CAPTURE_READY", "message": "Ready", "guidance": ""}
        
        res = service.start_live_capture(interface="eth0", promiscuous=True)
        assert res["status"] == "started"
        assert res["promiscuous"] is True
        
        # Verify warning log was emitted
        assert mock_log_warn.called
        assert "PROMISCUOUS" in mock_log_warn.call_args[0][0].upper()
        
        # Verify AsyncSniffer received promisc=True
        _, kwargs = mock_sniffer.call_args
        assert kwargs["promisc"] is True
        
        service.stop_capture()


def test_interface_isolation_restricts_to_selected_adapter():
    """3. Verify capture is restricted strictly to the user-selected network interface."""
    service = CaptureService()
    
    with patch.object(service, "run_host_diagnostics") as mock_diag, \
         patch.object(service, "_resolve_scapy_interface", return_value=r"\Device\NPF_{SPECIFIC_NIC_GUID}"), \
         patch("app.network.capture_service.AsyncSniffer") as mock_sniffer:
        
        mock_diag.return_value = {"available": True, "state": "CAPTURE_READY", "message": "Ready", "guidance": ""}
        
        res = service.start_live_capture(interface="Local Area Connection 2")
        assert res["status"] == "started"
        assert res["interface"] == "Local Area Connection 2"
        assert res["device"] == r"\Device\NPF_{SPECIFIC_NIC_GUID}"
        
        _, kwargs = mock_sniffer.call_args
        assert kwargs["iface"] == r"\Device\NPF_{SPECIFIC_NIC_GUID}"
        
        service.stop_capture()


def test_sensitive_headers_and_payload_redaction():
    """4. Verify raw headers containing tokens, cookies, passwords, and auth secrets are redacted."""
    raw_http = (
        "POST /api/login HTTP/1.1\r\n"
        "Host: traceguard.local\r\n"
        "Authorization: Bearer secret_jwt_token_1234567890abcdef\r\n"
        "Cookie: session_id=sess_cookie_xyz789; auth_token=secret_abc123\r\n"
        "Set-Cookie: user_id=admin; Secure; HttpOnly\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"username": "admin", "password": "super_secret_password_999", "api_key": "live_key_abcdef"}'
    )
    
    sanitized = sanitize_payload_metadata(raw_http)
    
    assert "secret_jwt_token_1234567890abcdef" not in sanitized
    assert "sess_cookie_xyz789" not in sanitized
    assert "secret_abc123" not in sanitized
    assert "super_secret_password_999" not in sanitized
    assert "live_key_abcdef" not in sanitized
    assert "[REDACTED_FOR_PRIVACY]" in sanitized


def test_absence_of_raw_packet_payloads_in_models():
    """5. Verify that database models (NetworkEvent, Alert) do not contain raw payload columns."""
    event_columns = [c.name for c in NetworkEvent.__table__.columns]
    assert "payload" not in event_columns
    assert "raw_payload" not in event_columns
    assert "packet_bytes" not in event_columns
    assert "headers" not in event_columns
    
    alert_columns = [c.name for c in Alert.__table__.columns]
    assert "raw_payload" not in alert_columns
    assert "packet_dump" not in alert_columns


def test_clean_capture_stop_releases_sniffer():
    """6. Verify capture stop releases resources, sets is_capturing to False, and nulls sniffer."""
    service = CaptureService()
    
    mock_sniffer_instance = MagicMock()
    with patch.object(service, "run_host_diagnostics") as mock_diag, \
         patch.object(service, "_resolve_scapy_interface", return_value="eth0"), \
         patch("app.network.capture_service.AsyncSniffer", return_value=mock_sniffer_instance):
        
        mock_diag.return_value = {"available": True, "state": "CAPTURE_READY", "message": "Ready", "guidance": ""}
        
        service.start_live_capture(interface="eth0")
        assert service.is_capturing is True
        assert service._sniffer is not None
        
        stop_res = service.stop_capture()
        assert stop_res["status"] == "stopped"
        assert service.is_capturing is False
        assert service._sniffer is None
        mock_sniffer_instance.stop.assert_called_once()
