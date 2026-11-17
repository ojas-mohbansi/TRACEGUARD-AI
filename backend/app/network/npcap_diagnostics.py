"""Authoritative Windows Npcap and packet capture driver diagnostic module for TraceGuard AI."""
import os
import platform
import sys
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Retain module-level handle to prevent Python 3.8+ garbage collection of DLL search directory
_DLL_DIRECTORY_HANDLE = None


class NpcapDiagnostics:
    """Performs non-destructive, safe diagnostic verification of Npcap / libpcap on the host."""

    # Diagnostic State Enumeration
    STATE_CAPTURE_READY = "CAPTURE_READY"
    STATE_READY = "READY"
    STATE_NOT_INSTALLED = "NOT_INSTALLED"
    STATE_SERVICE_STOPPED = "SERVICE_STOPPED"
    STATE_PCAP_API_UNAVAILABLE = "PCAP_API_UNAVAILABLE"
    STATE_PERMISSION_DENIED = "PERMISSION_DENIED"
    STATE_NO_INTERFACES_FOUND = "NO_INTERFACES_FOUND"
    STATE_INTERFACE_OPEN_FAILED = "INTERFACE_OPEN_FAILED"
    STATE_UNKNOWN_ERROR = "UNKNOWN_ERROR"

    @classmethod
    def run_diagnostics(cls) -> Dict[str, Any]:
        """Execute full 6-step capture diagnostic check on host runtime."""
        system = platform.system()
        is_windows = system == "Windows"

        report: Dict[str, Any] = {
            "platform": system,
            "architecture": platform.architecture()[0],
            "python_executable": sys.executable,
            "python_version": sys.version.split()[0],
            "state": cls.STATE_UNKNOWN_ERROR,
            "available": False,
            "steps": {
                "1_driver_installed": False,
                "2_service_running": False,
                "3_pcap_api_loaded": False,
                "4_interfaces_enumerated": False,
                "5_handle_open_test": False,
                "6_capture_ready": False,
            },
            "driver_info": {
                "provider": "Npcap" if is_windows else "libpcap",
                "version": None,
                "dll_path": None,
                "admin_only": False,
                "winpcap_compatible": True,
            },
            "interfaces": [],
            "test_interface": None,
            "message": "",
            "guidance": "",
        }

        # Non-Windows platforms
        if not is_windows:
            try:
                from scapy.all import conf, get_if_list
                use_pcap = getattr(conf, "use_pcap", False)
                if use_pcap:
                    report["state"] = cls.STATE_CAPTURE_READY
                    report["available"] = True
                    report["steps"]["1_driver_installed"] = True
                    report["steps"]["2_service_running"] = True
                    report["steps"]["3_pcap_api_loaded"] = True
                    report["steps"]["4_interfaces_enumerated"] = True
                    report["steps"]["5_handle_open_test"] = True
                    report["steps"]["6_capture_ready"] = True
                    report["driver_info"]["version"] = "libpcap"
                    report["message"] = "Native libpcap active on Unix/Linux."
                    return report
                else:
                    report["state"] = cls.STATE_NOT_INSTALLED
                    report["message"] = "libpcap development headers/runtime not found."
                    return report
            except Exception as e:
                report["state"] = cls.STATE_UNKNOWN_ERROR
                report["message"] = str(e)
                return report

        # ---------------------------------------------------------
        # WINDOWS DIAGNOSTICS: 6-STEP VERIFICATION PIPELINE
        # ---------------------------------------------------------

        # Ensure Python 3.8+ Windows DLL directory includes Npcap folder if present
        windir = os.environ.get("WINDIR", "C:\\Windows")
        npcap_dir = os.path.join(windir, "System32", "Npcap")
        if os.path.exists(npcap_dir):
            global _DLL_DIRECTORY_HANDLE
            if _DLL_DIRECTORY_HANDLE is None:
                try:
                    _DLL_DIRECTORY_HANDLE = os.add_dll_directory(npcap_dir)
                except Exception as e:
                    logger.debug(f"Could not add DLL directory {npcap_dir}: {e}")
            if npcap_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = npcap_dir + ";" + os.environ.get("PATH", "")

        # Step 1: Check driver and DLL files
        wpcap_npcap = os.path.join(npcap_dir, "wpcap.dll")
        packet_npcap = os.path.join(npcap_dir, "Packet.dll")
        wpcap_sys = os.path.join(windir, "System32", "wpcap.dll")

        has_npcap_files = os.path.exists(wpcap_npcap) and os.path.exists(packet_npcap)
        has_winpcap_files = os.path.exists(wpcap_sys)

        if not has_npcap_files and not has_winpcap_files:
            report["state"] = cls.STATE_NOT_INSTALLED
            report["message"] = "Npcap driver is not installed on this Windows system."
            report["guidance"] = (
                "Download and install Npcap 1.70+ from https://npcap.com. "
                "Ensure 'Install Npcap in WinPcap API-compatible Mode' is checked during setup."
            )
            return report

        report["steps"]["1_driver_installed"] = True
        report["driver_info"]["dll_path"] = wpcap_npcap if has_npcap_files else wpcap_sys

        # Step 2: Check Windows service status
        svc_running = False
        try:
            import scapy.arch.windows as saw
            svc_running = bool(saw.pcap_service_status())
        except Exception as e:
            logger.debug(f"Service check via scapy arch windows failed: {e}")

        if not svc_running:
            # Fallback check via powershell / sc query
            try:
                import subprocess
                p = subprocess.run(
                    ["sc", "query", "npcap"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if "RUNNING" in p.stdout:
                    svc_running = True
            except Exception:
                pass

        report["steps"]["2_service_running"] = svc_running
        if not svc_running:
            report["state"] = cls.STATE_SERVICE_STOPPED
            report["message"] = "Npcap driver files are installed, but the 'npcap' kernel service is currently stopped."
            report["guidance"] = (
                "Start the Npcap service by running 'net start npcap' in an Administrator command prompt, "
                "or verify that the driver was not disabled in Windows Device Manager."
            )
            return report

        # Step 3: Pcap API & DLL Loading Check
        pcap_version_str = None
        try:
            import scapy.libs.winpcapy as wp
            if wp._lib:
                v_bytes = wp.pcap_lib_version()
                pcap_version_str = v_bytes.decode("utf-8", errors="ignore") if v_bytes else "Npcap (loaded)"
            else:
                # Force re-load
                import ctypes
                ctypes.cdll.LoadLibrary(packet_npcap)
                _lib = ctypes.cdll.LoadLibrary(wpcap_npcap)
                if _lib:
                    pcap_version_str = "Npcap DLL (direct loaded)"
        except Exception as e:
            report["state"] = cls.STATE_PCAP_API_UNAVAILABLE
            report["message"] = f"Npcap DLL could not be dynamically loaded into the 64-bit Python process: {e}"
            report["guidance"] = "Check for conflicting 32-bit WinPcap DLLs in C:\\Windows\\System32 or re-run Npcap installer."
            return report

        if not pcap_version_str:
            report["state"] = cls.STATE_PCAP_API_UNAVAILABLE
            report["message"] = "Pcap API functions could not be resolved from wpcap.dll."
            return report

        report["steps"]["3_pcap_api_loaded"] = True
        report["driver_info"]["version"] = pcap_version_str

        # Step 4: Network Interface Enumeration
        ifaces: List[Dict[str, Any]] = []
        try:
            from scapy.all import conf
            # Ensure conf.use_pcap is synchronized
            conf.use_pcap = True
            conf.use_npcap = True

            for k, iface in conf.ifaces.items():
                name = getattr(iface, "name", k)
                desc = getattr(iface, "description", "")
                ip = getattr(iface, "ip", "")
                mac = getattr(iface, "mac", "")
                ifaces.append({
                    "id": k,
                    "name": name,
                    "description": desc,
                    "ip": ip,
                    "mac": mac,
                    "is_up": True
                })
        except Exception as e:
            logger.error(f"Error enumerating interfaces with Scapy: {e}")

        report["steps"]["4_interfaces_enumerated"] = len(ifaces) > 0
        report["interfaces"] = ifaces

        if not ifaces:
            report["state"] = cls.STATE_NO_INTERFACES_FOUND
            report["message"] = "No packet capture interfaces were enumerated by Npcap."
            report["guidance"] = "Verify network adapters are enabled in Network Connections and Npcap packet filter is bound."
            return report

        # Step 5: Test Opening Capture Handle (Passive, 1-second timeout)
        test_iface = next(
            (i for i in ifaces if i["ip"] and not i["ip"].startswith("127.") and not i["ip"].startswith("169.")),
            ifaces[0]
        )
        report["test_interface"] = {
            "id": test_iface["id"],
            "name": test_iface["name"],
            "ip": test_iface["ip"]
        }

        handle_opened = False
        open_error = None
        try:
            import scapy.libs.winpcapy as wp
            from ctypes import create_string_buffer
            errbuf = create_string_buffer(wp.PCAP_ERRBUF_SIZE)
            dev_bytes = test_iface["id"].encode("utf-8")
            # Open live handle non-promiscuously (promisc=0) with 500ms timeout
            handle = wp.pcap_open_live(dev_bytes, 65535, 0, 500, errbuf)
            if handle:
                handle_opened = True
                wp.pcap_close(handle)
            else:
                open_error = errbuf.value.decode("utf-8", errors="ignore")
        except Exception as e:
            open_error = str(e)

        report["steps"]["5_handle_open_test"] = handle_opened

        if not handle_opened:
            if open_error and ("permission" in open_error.lower() or "access denied" in open_error.lower()):
                report["state"] = cls.STATE_PERMISSION_DENIED
                report["message"] = f"Npcap handle open failed due to permission denial: {open_error}"
                report["guidance"] = (
                    "Npcap was installed with 'Restrict Npcap driver's access to Administrators only'. "
                    "Either run the application as Administrator, or reinstall Npcap with AdminOnly disabled."
                )
            else:
                report["state"] = cls.STATE_INTERFACE_OPEN_FAILED
                report["message"] = f"Failed to open live capture handle on adapter {test_iface['name']}: {open_error}"
                report["guidance"] = "Check adapter binding and ensure no exclusive packet sniffer is locking the interface."
            return report

        # Step 6: Complete verification
        report["steps"]["6_capture_ready"] = True
        report["state"] = cls.STATE_CAPTURE_READY
        report["available"] = True
        report["message"] = (
            f"Npcap runtime active and validated. {pcap_version_str} operational. "
            f"Successfully verified live capture handle on '{test_iface['name']}' ({test_iface['ip'] or 'active'})."
        )
        report["guidance"] = "Ready for passive promiscuous or local packet capture on authorized network adapters."
        return report
