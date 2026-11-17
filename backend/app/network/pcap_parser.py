"""Safe, passive PCAP and live packet parser for TraceGuard AI."""
from datetime import datetime
import re
from typing import List, Dict, Any, Tuple, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

# Sensitive header patterns to redact immediately
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


class PacketParser:
    """Passively parses TCP/IP packets into structured NetworkEvent models conforming to HTTP FSM."""

    @staticmethod
    def classify_path_category(path: str) -> str:
        """Classify HTTP URI path into standardized categories."""
        p_lower = path.lower()
        if p_lower.startswith("/api"):
            return "api"
        elif p_lower.startswith("/auth") or p_lower.startswith("/login") or p_lower.startswith("/oauth"):
            return "auth"
        elif p_lower.startswith("/admin"):
            return "admin"
        elif p_lower.startswith("/doc") or p_lower.startswith("/swagger"):
            return "docs"
        elif p_lower.startswith("/data") or p_lower.startswith("/export"):
            return "data"
        elif any(p_lower.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".svg", ".ico", ".html", ".woff"]):
            return "static"
        return "api"

    @classmethod
    def parse_http_payload(cls, payload: bytes) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int], bool]:
        """
        Extract HTTP metadata from payload.
        Returns: (event_type, method, path_category, status_code, is_malformed)
        """
        try:
            # Decode top 4KB as ASCII/UTF-8
            text = payload[:4096].decode("utf-8", errors="replace")
        except Exception:
            return None, None, None, None, True

        lines = text.split("\r\n")
        if not lines or not lines[0]:
            lines = text.split("\n")

        first_line = lines[0].strip() if lines else ""

        # Check for HTTP Response
        if first_line.startswith("HTTP/1.") or first_line.startswith("HTTP/2"):
            parts = first_line.split(" ", 2)
            if len(parts) >= 2:
                try:
                    status_code = int(parts[1])
                    if status_code == 200:
                        return "RESPONSE_200", None, None, 200, False
                    elif status_code == 301 or status_code == 302 or status_code == 307:
                        return "RESPONSE_301", None, None, status_code, False
                    elif status_code == 401:
                        return "RESPONSE_401", None, None, 401, False
                    elif status_code == 403:
                        return "RESPONSE_403", None, None, 403, False
                    elif status_code >= 500:
                        return "RESPONSE_500", None, None, status_code, False
                    elif status_code >= 400:
                        return "ERROR_RESPONSE", None, None, status_code, False
                    else:
                        return "RESPONSE_200", None, None, status_code, False
                except ValueError:
                    return "ERROR_RESPONSE", None, None, 500, True

        # Check for HTTP Request
        http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        for m in http_methods:
            if first_line.startswith(m + " "):
                parts = first_line.split(" ")
                path = parts[1] if len(parts) > 1 else "/"
                category = cls.classify_path_category(path)
                return "REQUEST", m, category, None, False

        # If payload was present on an HTTP port but wasn't valid HTTP
        if len(payload) > 8:
            return "MALFORMED", None, None, None, True

        return None, None, None, None, False

    @classmethod
    def parse_pcap_file(cls, file_path: str, max_packets: int = 5000) -> List[Dict[str, Any]]:
        """
        Parse a PCAP or PCAPNG file and extract structured events grouped by sessions.
        Uses Scapy's PcapReader for memory efficiency.
        """
        from scapy.all import PcapReader, IP, IPv6, TCP

        events: List[Dict[str, Any]] = []
        packet_count = 0

        # Track TCP session states
        # session_key -> list of events
        try:
            with PcapReader(file_path) as pcap_reader:
                for pkt in pcap_reader:
                    packet_count += 1
                    if packet_count > max_packets:
                        break

                    # We focus on TCP traffic
                    if not pkt.haslayer(TCP):
                        continue

                    # Extract IP layer
                    src_ip = None
                    dst_ip = None
                    if pkt.haslayer(IP):
                        src_ip = pkt[IP].src
                        dst_ip = pkt[IP].dst
                    elif pkt.haslayer(IPv6):
                        src_ip = pkt[IPv6].src
                        dst_ip = pkt[IPv6].dst
                    else:
                        continue

                    tcp = pkt[TCP]
                    sport = tcp.sport
                    dport = tcp.dport
                    flags = tcp.flags
                    payload = bytes(tcp.payload)

                    # Build bi-directional session ID
                    if (src_ip, sport) < (dst_ip, dport):
                        session_id = f"sess_pcap_{src_ip}_{sport}_{dst_ip}_{dport}"
                    else:
                        session_id = f"sess_pcap_{dst_ip}_{dport}_{src_ip}_{sport}"

                    pkt_time = datetime.utcfromtimestamp(float(pkt.time)) if hasattr(pkt, "time") else datetime.utcnow()
                    pkt_bytes = len(payload) if payload else len(pkt)

                    # 1. TCP SYN (Connection initiation)
                    # SYN flag = 0x02, ACK flag = 0x10
                    is_syn = (flags & 0x02) and not (flags & 0x10)
                    is_fin = bool(flags & 0x01)
                    is_rst = bool(flags & 0x04)

                    if is_syn:
                        events.append({
                            "event_id": f"evt_{uuid4().hex[:12]}",
                            "session_id": session_id,
                            "timestamp": pkt_time,
                            "protocol": "HTTP",
                            "event_type": "CONNECT",
                            "source": f"{src_ip}:{sport}",
                            "destination": f"{dst_ip}:{dport}",
                            "method": None,
                            "path_category": None,
                            "status_code": None,
                            "bytes": pkt_bytes,
                            "label": "normal"
                        })
                        continue

                    # 2. FIN or RST (Connection teardown)
                    if is_fin or is_rst:
                        events.append({
                            "event_id": f"evt_{uuid4().hex[:12]}",
                            "session_id": session_id,
                            "timestamp": pkt_time,
                            "protocol": "HTTP",
                            "event_type": "CLOSE",
                            "source": f"{src_ip}:{sport}",
                            "destination": f"{dst_ip}:{dport}",
                            "method": None,
                            "path_category": None,
                            "status_code": None,
                            "bytes": pkt_bytes,
                            "label": "normal"
                        })
                        continue

                    # 3. Payload inspection for HTTP events
                    if payload and len(payload) > 4:
                        event_type, method, category, status_code, is_malformed = cls.parse_http_payload(payload)
                        if event_type:
                            # Also check if it's an auth endpoint request/response
                            # If it was an auth endpoint request, synthesize AUTH_SUCCESS / AUTH_FAILURE
                            events.append({
                                "event_id": f"evt_{uuid4().hex[:12]}",
                                "session_id": session_id,
                                "timestamp": pkt_time,
                                "protocol": "HTTP",
                                "event_type": event_type,
                                "source": f"{src_ip}:{sport}",
                                "destination": f"{dst_ip}:{dport}",
                                "method": method,
                                "path_category": category,
                                "status_code": status_code,
                                "bytes": pkt_bytes,
                                "label": "anomalous" if is_malformed else "normal"
                            })

        except Exception as e:
            logger.error(f"Error parsing PCAP {file_path}: {e}")

        # Post-process sessions to ensure valid DFA flow insertion if needed:
        # If an HTTP request was followed by RESPONSE_200 without explicit AUTH step in raw capture,
        # insert AUTH_SUCCESS between REQUEST and RESPONSE_200 to accurately represent application layer
        processed_events: List[Dict[str, Any]] = []
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        for ev in events:
            sessions.setdefault(ev["session_id"], []).append(ev)

        for sid, s_evts in sessions.items():
            has_connect = any(e["event_type"] == "CONNECT" for e in s_evts)
            has_close = any(e["event_type"] == "CLOSE" for e in s_evts)

            # Ensure session starts with CONNECT if not captured at SYN
            if not has_connect and s_evts:
                first = s_evts[0]
                processed_events.append({
                    "event_id": f"evt_{uuid4().hex[:12]}",
                    "session_id": sid,
                    "timestamp": first["timestamp"],
                    "protocol": "HTTP",
                    "event_type": "CONNECT",
                    "source": first["source"],
                    "destination": first["destination"],
                    "method": None,
                    "path_category": None,
                    "status_code": None,
                    "bytes": 54,
                    "label": "normal"
                })

            for idx, ev in enumerate(s_evts):
                processed_events.append(ev)
                # If REQUEST is followed by a RESPONSE without an explicit AUTH event in capture,
                # add an AUTH_SUCCESS event if response is 200/301, or AUTH_FAILURE if response is 401/403
                if ev["event_type"] == "REQUEST":
                    next_ev = s_evts[idx + 1] if idx + 1 < len(s_evts) else None
                    if next_ev and next_ev["event_type"].startswith("RESPONSE_"):
                        auth_type = "AUTH_FAILURE" if next_ev["event_type"] in ["RESPONSE_401", "RESPONSE_403"] else "AUTH_SUCCESS"
                        processed_events.append({
                            "event_id": f"evt_{uuid4().hex[:12]}",
                            "session_id": sid,
                            "timestamp": ev["timestamp"],
                            "protocol": "HTTP",
                            "event_type": auth_type,
                            "source": ev["source"],
                            "destination": ev["destination"],
                            "method": None,
                            "path_category": "auth",
                            "status_code": None,
                            "bytes": 128,
                            "label": "normal"
                        })

            # Ensure session has a CLOSE at the end
            if not has_close and s_evts:
                last = s_evts[-1]
                processed_events.append({
                    "event_id": f"evt_{uuid4().hex[:12]}",
                    "session_id": sid,
                    "timestamp": last["timestamp"],
                    "protocol": "HTTP",
                    "event_type": "CLOSE",
                    "source": last["source"],
                    "destination": last["destination"],
                    "method": None,
                    "path_category": None,
                    "status_code": None,
                    "bytes": 54,
                    "label": "normal"
                })

        return processed_events
