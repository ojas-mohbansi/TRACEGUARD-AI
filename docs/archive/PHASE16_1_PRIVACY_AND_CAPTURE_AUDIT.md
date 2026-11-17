# TRACEGUARD AI — PHASE 16.1: PRIVACY & CAPTURE SAFEGUARD AUDIT

**Document ID:** `TG-DOC-P16_1-PRIVACY`  
**Date:** `2026-11-17`  
**Classification:** Academic Engineering & Security Compliance  
**Author:** Security & Network Intelligence Lead  
**Scope:** `backend/app/network/capture_service.py`, `backend/app/api/network.py`, `backend/app/network/pcap_parser.py`, `backend/app/models/models.py`, `backend/tests/test_capture_privacy.py`

---

## 1. Executive Summary

Phase 16 introduced live network capture leveraging native Npcap 1.90 on Windows. However, production network monitoring requires rigorous privacy guarantees to ensure that sensitive payload contents, user credentials, authorization tokens, and session cookies are never intercepted, persisted, or leaked.

In Phase 16.1, we performed an exhaustive security and privacy hardening of all network capture paths:
1. **Promiscuous Mode Default Hardening**: `promiscuous` is now strictly `False` by default in both `CaptureService` and the FastAPI API schema `CaptureStartRequest`.
2. **Explicit Opt-in & Legal Warning**: Promiscuous capture requires an explicit, audited opt-in flag. When activated, an explicit security warning is logged.
3. **Interface Isolation**: Capture is locked to the specific network interface selected by the user.
4. **Zero Raw Payload Persistence**: Database models (`NetworkEvent` and `Alert`) possess no columns for packet payloads or raw dumps. Raw payload bytes are inspected solely in memory for protocol framing (`CONNECT`, `REQUEST`, `RESPONSE_*`, `CLOSE`) and immediately discarded.
5. **Credential & Token Redaction**: In any payload inspection or parsing pathway, sensitive headers (`Authorization: Bearer ...`, `Cookie`, `Set-Cookie`, `password`, `api_key`) are sanitized via regex substitution with `[REDACTED_FOR_PRIVACY]`.
6. **Clean Capture Stop & Resource Reclamation**: `stop_capture()` halts the Scapy `AsyncSniffer`, safely releases interface handles, and sets the sniffer reference to `None`.

---

## 2. Technical Implementation Audit

### 2.1 Default Non-Promiscuous Enforcement

In `backend/app/network/capture_service.py`:
```python
def start_live_capture(self, interface: str = "default", promiscuous: bool = False) -> Dict[str, Any]:
    ...
    # Privacy & Security Safeguard: Default to non-promiscuous capture
    if promiscuous:
        logger.warning(
            "SECURITY WARNING: Promiscuous mode capture explicitly enabled on interface '%s'. "
            "Ensure proper authorization and compliance before capturing non-local host traffic.",
            actual_device
        )
    else:
        logger.info("Starting safe non-promiscuous live capture on interface '%s'", actual_device)

    self._sniffer = AsyncSniffer(
        iface=actual_device,
        prn=self._on_packet,
        store=False,
        promisc=promiscuous,  # Strictly False by default
        filter="ip or ip6"
    )
    self._sniffer.start()
```

In `backend/app/api/network.py`:
```python
class CaptureStartRequest(BaseModel):
    interface: str = "default"
    promiscuous: bool = False  # Defaults to False

@router.post("/capture/start")
def start_live_capture(
    req: CaptureStartRequest,
    ctx: WorkspaceContext = Depends(get_current_workspace_context)
):
    service = CaptureService.get_instance()
    res = service.start_live_capture(interface=req.interface, promiscuous=req.promiscuous)
    return res
```

### 2.2 Sensitive Header & Credential Redaction

In `backend/app/network/pcap_parser.py`:
```python
SENSITIVE_PATTERNS = [
    re.compile(r'(Authorization:\s*)([^\r\n]+)', re.IGNORECASE),
    re.compile(r'(Cookie:\s*)([^\r\n]+)', re.IGNORECASE),
    re.compile(r'(Set-Cookie:\s*)([^\r\n]+)', re.IGNORECASE),
    re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', re.IGNORECASE),
    re.compile(r'(api[-_]?key["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', re.IGNORECASE),
]

def sanitize_payload_metadata(raw_text: str) -> str:
    """Sanitize sensitive credentials from raw payload headers for privacy compliance."""
    sanitized = raw_text
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r'\1[REDACTED_FOR_PRIVACY]', sanitized)
    return sanitized
```

### 2.3 Absence of Raw Payload in Database Schema

Inspection of `backend/app/models/models.py` confirms that `NetworkEvent` records only derived metadata conforming to the formal HTTP automaton:
- `event_id`: String (e.g., `pkt_14_request`)
- `session_id`: String (e.g., `sess_54321_80`)
- `timestamp`: DateTime
- `protocol`: String (e.g., `HTTP`)
- `event_type`: String (e.g., `REQUEST`, `RESPONSE_200`, `CLOSE`)
- `source`: String (`IP:PORT`)
- `destination`: String (`IP:PORT`)
- `method`: String (`GET`, `POST`, etc.)
- `path_category`: String (`api`, `auth`, `static`, etc.)
- `status_code`: Integer (`200`, `401`, `500`)
- `bytes`: Integer (frame byte count)
- `label`: String (`normal`, `anomalous`)

No packet payload text, raw bytes, or decrypted contents are stored.

### 2.4 Clean Resource Release on Capture Stop

In `backend/app/network/capture_service.py`:
```python
def stop_capture(self) -> Dict[str, Any]:
    """Stop active capture immediately and release all network resources."""
    if not self.is_capturing:
        return {"status": "not_running"}

    if self._sniffer:
        try:
            self._sniffer.stop()
        except Exception as e:
            logger.warning(f"Error while stopping AsyncSniffer: {e}")
        finally:
            self._sniffer = None

    self.is_capturing = False
    duration = (datetime.utcnow() - self.capture_start_time).total_seconds() if self.capture_start_time else 0
    return {
        "status": "stopped",
        "source": self.active_source,
        "duration_seconds": round(duration, 2),
        "packets_received": self.packets_received,
        "events_processed": self.events_processed,
        "alerts_generated": self.alerts_generated
    }
```

---

## 3. Automated Privacy Test Suite Verification

A dedicated verification suite was authored in `backend/tests/test_capture_privacy.py` and executed:

```
backend/tests/test_capture_privacy.py::test_capture_service_defaults_to_non_promiscuous PASSED [ 16%]
backend/tests/test_capture_privacy.py::test_capture_service_explicit_promiscuous_opt_in PASSED [ 33%]
backend/tests/test_capture_privacy.py::test_interface_isolation_restricts_to_selected_adapter PASSED [ 50%]
backend/tests/test_capture_privacy.py::test_sensitive_headers_and_payload_redaction PASSED [ 66%]
backend/tests/test_capture_privacy.py::test_absence_of_raw_packet_payloads_in_models PASSED [ 83%]
backend/tests/test_capture_privacy.py::test_clean_capture_stop_releases_sniffer PASSED [100%]

======================== 6 passed, 1 warning in 0.73s =========================
```

All 6 test cases passed without regression.
