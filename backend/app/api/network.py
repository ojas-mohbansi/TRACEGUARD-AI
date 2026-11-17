"""Network Intelligence & Live Traffic API Router for TraceGuard AI."""
from datetime import datetime
import os
import shutil
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from pydantic import BaseModel

from app.core.security import get_current_workspace_context, WorkspaceContext
from app.network.capture_service import CaptureService
from app.network.pcap_parser import PacketParser
from app.network.pipeline import IngestionPipeline

router = APIRouter()

# Max allowed PCAP file size: 50MB
MAX_PCAP_SIZE_BYTES = 50 * 1024 * 1024


class CaptureStartRequest(BaseModel):
    interface: str = "default"
    promiscuous: bool = False


@router.get("/status")
def get_network_status(ctx: WorkspaceContext = Depends(get_current_workspace_context)):
    """Retrieve active network capture telemetry and PCAP provider status."""
    service = CaptureService.get_instance()
    status = service.get_status()
    status["workspace_id"] = ctx.workspace_id
    return status


@router.get("/interfaces")
def get_interfaces():
    """Enumerate host network interfaces and capture readiness."""
    service = CaptureService.get_instance()
    return {
        "provider_status": service.get_pcap_provider_status(),
        "interfaces": service.list_interfaces()
    }


@router.post("/diagnose")
def run_capture_diagnostics(ctx: WorkspaceContext = Depends(get_current_workspace_context)):
    """Run full live diagnostic check of Npcap / packet capture runtime."""
    service = CaptureService.get_instance()
    diag = service.run_host_diagnostics(force=True)
    return {
        "status": "success",
        "diagnostic": diag,
        "provider_status": service.get_pcap_provider_status(force=True),
        "interfaces": service.list_interfaces()
    }


@router.post("/capture/start")
def start_live_capture(
    req: CaptureStartRequest,
    ctx: WorkspaceContext = Depends(get_current_workspace_context)
):
    """
    Start passive live packet capture on selected interface.
    Returns 400 with actionable prerequisite if Npcap is missing.
    Defaults to non-promiscuous capture.
    """
    service = CaptureService.get_instance()
    try:
        res = service.start_live_capture(interface=req.interface, promiscuous=req.promiscuous)
        return res
    except RuntimeError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "LIVE_CAPTURE_UNAVAILABLE",
                "message": str(e),
                "remedy": "Install Npcap (https://npcap.com) with WinPcap-compatible mode on Windows, or use PCAP/PCAPNG upload."
            }
        )


@router.post("/capture/stop")
def stop_live_capture(ctx: WorkspaceContext = Depends(get_current_workspace_context)):
    """Stop active packet capture."""
    service = CaptureService.get_instance()
    return service.stop_capture()


@router.post("/clear")
def clear_capture_session(ctx: WorkspaceContext = Depends(get_current_workspace_context)):
    """Reset capture session counters and telemetry buffer."""
    service = CaptureService.get_instance()
    service.clear_session()
    return {"status": "cleared"}


@router.post("/pcap/upload")
async def upload_and_process_pcap(
    file: UploadFile = File(...),
    stream_live: bool = Query(False, description="Whether to stream events incrementally to WebSocket"),
    ctx: WorkspaceContext = Depends(get_current_workspace_context)
):
    """
    Upload and parse real PCAP/PCAPNG network capture file.
    Validates file format, enforces size limits, extracts protocol events,
    and runs the verified multi-engine detection pipeline.
    """
    filename = file.filename or "unknown.pcap"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pcap", ".pcapng", ".cap"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported capture file format '{ext}'. Supported formats: .pcap, .pcapng, .cap"
        )

    # Save to safe temporary file and check size
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp_path = tmp.name
        content_size = 0
        chunk_size = 1024 * 64

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content_size += len(chunk)
            if content_size > MAX_PCAP_SIZE_BYTES:
                tmp.close()
                os.unlink(tmp_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds maximum size limit of {MAX_PCAP_SIZE_BYTES // (1024 * 1024)}MB."
                )
            tmp.write(chunk)

    try:
        # Parse PCAP file into structured protocol events
        events = PacketParser.parse_pcap_file(tmp_path, max_packets=5000)

        # Count distinct flows/sessions
        sessions_set = set(e["session_id"] for e in events)

        # Ingest through multi-engine detection pipeline
        pipeline = IngestionPipeline(workspace_id=ctx.workspace_id)
        delay = 50.0 if stream_live else 0.0
        pipeline_result = await pipeline.process_parsed_events(
            events,
            source_type="pcap_replay",
            stream_delay_ms=delay
        )

        # Record PCAP replay session in capture service
        service = CaptureService.get_instance()
        service.record_pcap_session(
            filename=filename,
            packets=len(events),
            flows=len(sessions_set),
            events=pipeline_result["events_processed"],
            alerts=pipeline_result["alerts_generated"],
            bytes_count=pipeline_result["bytes_processed"]
        )

        return {
            "status": "success",
            "filename": filename,
            "packets_parsed": len(events),
            "sessions_count": len(sessions_set),
            "events_processed": pipeline_result["events_processed"],
            "alerts_generated": pipeline_result["alerts_generated"],
            "bytes_processed": pipeline_result["bytes_processed"]
        }

    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
