"""Passive live network capture manager and interface inspector for TraceGuard AI."""
import asyncio
from datetime import datetime
import logging
import platform
import socket
from typing import Dict, Any, List, Optional
from scapy.all import conf, AsyncSniffer, IP, TCP, Raw

from app.network.npcap_diagnostics import NpcapDiagnostics
from app.network.pcap_parser import PacketParser

logger = logging.getLogger(__name__)


class CaptureService:
    """Manages safe, passive live capture and interface enumeration."""

    _instance: Optional["CaptureService"] = None

    def __init__(self):
        self.is_capturing: bool = False
        self.active_interface: Optional[str] = None
        self.active_source: str = "none"  # "none", "live_network", "pcap_replay", "synthetic"
        self.capture_start_time: Optional[datetime] = None
        self.packets_received: int = 0
        self.flows_identified: int = 0
        self.events_processed: int = 0
        self.alerts_generated: int = 0
        self.bytes_processed: int = 0
        self.recent_events: List[Dict[str, Any]] = []
        self.recent_alerts: List[Dict[str, Any]] = []
        self.source_label: str = "INACTIVE"
        self._sniffer: Optional[AsyncSniffer] = None
        self._async_task: Optional[asyncio.Task] = None
        self._active_sessions: set = set()
        self._cached_diag: Optional[Dict[str, Any]] = None

    @classmethod
    def get_instance(cls) -> "CaptureService":
        if cls._instance is None:
            cls._instance = CaptureService()
        return cls._instance

    def run_host_diagnostics(self, force: bool = False) -> Dict[str, Any]:
        """Run or return cached host packet capture diagnostics."""
        if self._cached_diag is None or force:
            self._cached_diag = NpcapDiagnostics.run_diagnostics()
        return self._cached_diag

    @classmethod
    def get_pcap_provider_status(cls, force: bool = False) -> Dict[str, Any]:
        """Check whether a native packet capture driver (Npcap/libpcap) is available."""
        diag = NpcapDiagnostics.run_diagnostics()
        return {
            "available": diag["available"],
            "state": diag["state"],
            "provider": diag["driver_info"]["provider"],
            "version": diag["driver_info"]["version"],
            "platform": diag["platform"],
            "architecture": diag["architecture"],
            "steps": diag["steps"],
            "message": diag["message"],
            "guidance": diag["guidance"],
            "test_interface": diag["test_interface"]
        }

    @classmethod
    def list_interfaces(cls) -> List[Dict[str, Any]]:
        """List local network interfaces with IP addresses and driver status."""
        diag = NpcapDiagnostics.run_diagnostics()
        interfaces = []
        for iface in diag.get("interfaces", []):
            interfaces.append({
                "id": iface["id"],
                "name": iface["name"],
                "ip": iface["ip"] or "Unassigned",
                "is_up": True,
                "description": iface["description"] or iface["name"],
                "live_capture_ready": diag["available"]
            })

        if not interfaces:
            # Fallback local loopback
            interfaces.append({
                "id": "loopback",
                "name": "Loopback Pseudo-Interface",
                "ip": "127.0.0.1",
                "is_up": True,
                "description": "Software Loopback Interface",
                "live_capture_ready": diag["available"]
            })
        return interfaces

    def _resolve_scapy_interface(self, target: str) -> Optional[str]:
        """Map user-friendly interface name or ID to Scapy device string."""
        if not target or target == "default":
            # Prefer active adapter with IP
            diag = self.run_host_diagnostics()
            if diag.get("test_interface"):
                return diag["test_interface"]["id"]
            if diag.get("interfaces"):
                return diag["interfaces"][0]["id"]
            return None

        # Direct match or substring match in conf.ifaces
        for k, iface in conf.ifaces.items():
            if k == target or getattr(iface, "name", "") == target:
                return k
            if target.lower() in getattr(iface, "name", "").lower():
                return k
            if target.lower() in k.lower():
                return k
        return target

    def _on_packet(self, pkt):
        """Passive packet handler invoked by AsyncSniffer."""
        try:
            self.packets_received += 1
            pkt_len = len(pkt)
            self.bytes_processed += pkt_len

            if not pkt.haslayer(TCP) or not pkt.haslayer(IP):
                return

            ip = pkt[IP]
            tcp = pkt[TCP]
            flow_key = f"{ip.src}:{tcp.sport}->{ip.dst}:{tcp.dport}"
            self._active_sessions.add(flow_key)
            self.flows_identified = len(self._active_sessions)

            # Extract basic event type
            event_type = None
            if tcp.flags & 0x02:  # SYN
                event_type = "CONNECT"
            elif tcp.flags & 0x01:  # FIN
                event_type = "CLOSE"
            elif pkt.haslayer(Raw):
                payload = bytes(pkt[Raw].load)
                if payload.startswith((b"GET ", b"POST ", b"PUT ", b"DELETE ", b"HEAD ", b"OPTIONS ")):
                    event_type = "REQUEST"
                elif payload.startswith(b"HTTP/1."):
                    if b" 200 " in payload:
                        event_type = "RESPONSE_200"
                    elif b" 301 " in payload or b" 302 " in payload:
                        event_type = "RESPONSE_301"
                    elif b" 401 " in payload:
                        event_type = "RESPONSE_401"
                    elif b" 403 " in payload:
                        event_type = "RESPONSE_403"
                    elif b" 500 " in payload:
                        event_type = "RESPONSE_500"

            if event_type:
                self.events_processed += 1
                evt = {
                    "event_id": f"pkt_{self.packets_received}_{event_type.lower()}",
                    "session_id": f"sess_{tcp.sport}_{tcp.dport}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "protocol": "HTTP",
                    "event_type": event_type,
                    "source": f"{ip.src}:{tcp.sport}",
                    "destination": f"{ip.dst}:{tcp.dport}",
                    "bytes": pkt_len,
                    "label": "normal"
                }
                self.recent_events.append(evt)
                if len(self.recent_events) > 100:
                    self.recent_events.pop(0)

                # Broadcast live packet event over WebSocket
                try:
                    from app.api.websocket import ws_manager
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            ws_manager.broadcast("event", evt),
                            loop
                        )
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Packet processing warning: {e}")

    def start_live_capture(self, interface: str = "default", promiscuous: bool = False) -> Dict[str, Any]:
        """Start passive live interface capture with default non-promiscuous mode."""
        diag = self.run_host_diagnostics(force=True)
        if not diag["available"]:
            raise RuntimeError(
                f"Cannot start live interface capture: State={diag['state']}. {diag['message']} {diag['guidance']}"
            )

        if self.is_capturing:
            return {"status": "already_running", "interface": self.active_interface, "promiscuous": promiscuous}

        actual_device = self._resolve_scapy_interface(interface)
        if not actual_device:
            raise RuntimeError(f"Requested network interface '{interface}' could not be resolved.")

        # Privacy & Security Safeguard: Default to non-promiscuous capture
        if promiscuous:
            logger.warning(
                "SECURITY WARNING: Promiscuous mode capture explicitly enabled on interface '%s'. "
                "Ensure proper authorization and compliance before capturing non-local host traffic.",
                actual_device
            )
        else:
            logger.info("Starting safe non-promiscuous live capture on interface '%s'", actual_device)

        self.is_capturing = True
        self.active_interface = interface
        self.active_source = "live_network"
        self.source_label = f"LIVE NETWORK ({interface})"
        self.capture_start_time = datetime.utcnow()
        self.packets_received = 0
        self.flows_identified = 0
        self.events_processed = 0
        self.alerts_generated = 0
        self.bytes_processed = 0
        self.recent_events.clear()
        self.recent_alerts.clear()
        self._active_sessions.clear()

        try:
            # Start real Scapy AsyncSniffer on the resolved interface with promisc=promiscuous (strictly False by default)
            self._sniffer = AsyncSniffer(
                iface=actual_device,
                prn=self._on_packet,
                store=False,
                promisc=promiscuous,
                filter="ip or ip6"
            )
            self._sniffer.start()
            logger.info(f"Live network capture started on {actual_device} (promisc={promiscuous})")
        except Exception as e:
            self.is_capturing = False
            self.active_source = "none"
            raise RuntimeError(f"Failed to start live packet sniffer on {actual_device}: {e}")

        return {
            "status": "started",
            "source": self.active_source,
            "interface": interface,
            "device": actual_device,
            "promiscuous": promiscuous,
            "started_at": self.capture_start_time.isoformat()
        }

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

    def record_pcap_session(self, filename: str, packets: int, flows: int, events: int, alerts: int, bytes_count: int):
        """Record a completed or active PCAP ingestion session."""
        self.active_source = "pcap_replay"
        self.active_interface = filename
        self.source_label = f"PCAP REPLAY ({filename})"
        self.is_capturing = False
        self.packets_received = packets
        self.flows_identified = flows
        self.events_processed = events
        self.alerts_generated = alerts
        self.bytes_processed = bytes_count
        self.capture_start_time = datetime.utcnow()

    def clear_session(self):
        """Reset current capture telemetry buffer."""
        self.packets_received = 0
        self.flows_identified = 0
        self.events_processed = 0
        self.alerts_generated = 0
        self.bytes_processed = 0
        self.recent_events.clear()
        self.recent_alerts.clear()
        self.active_source = "none"
        self.source_label = "INACTIVE"
        self.active_interface = None
        self.capture_start_time = None

    def get_status(self) -> Dict[str, Any]:
        """Return current live telemetry snapshot."""
        prov = self.get_pcap_provider_status()
        duration_s = (datetime.utcnow() - self.capture_start_time).total_seconds() if self.capture_start_time else 0.0

        return {
            "is_capturing": self.is_capturing,
            "active_source": self.active_source,
            "source_label": self.source_label,
            "active_interface": self.active_interface,
            "capture_start_time": self.capture_start_time.isoformat() if self.capture_start_time else None,
            "duration_seconds": round(duration_s, 1),
            "packets_received": self.packets_received,
            "flows_identified": self.flows_identified,
            "events_processed": self.events_processed,
            "alerts_generated": self.alerts_generated,
            "bytes_processed": self.bytes_processed,
            "provider_status": prov,
            "recent_events": self.recent_events[-10:],
            "recent_alerts": self.recent_alerts[-10:]
        }
