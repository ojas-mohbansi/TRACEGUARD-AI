"""Academic Detection Benchmark API Router for TraceGuard AI."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.models import Alert, NetworkEvent
from app.core.security import get_current_workspace_context, WorkspaceContext
from app.detection.benchmark import AcademicBenchmarkGenerator, BENCHMARK_DATASET_ID, BENCHMARK_SOURCE_TAG

router = APIRouter()


@router.post("/generate")
def generate_academic_benchmark(
    seed: int = Query(42, description="Random seed for reproducible evaluation"),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Generate 100-session seeded academic benchmark dataset executed through real detection engines.
    Targeting 25-35% FSM, 10-20% ML, 45-65% Hybrid with 0% unexplained.
    """
    generator = AcademicBenchmarkGenerator(seed=seed)
    result = generator.generate_and_execute(db, workspace_id=ctx.workspace_id)
    return result


@router.get("/status")
def get_benchmark_status(
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Retrieve current academic benchmark status and attribution distribution from database records."""
    alerts = db.query(Alert).filter(
        Alert.workspace_id == ctx.workspace_id,
        Alert.dataset_id == BENCHMARK_DATASET_ID
    ).all()

    total_alerts = len(alerts)
    total_events = db.query(NetworkEvent).filter(
        NetworkEvent.workspace_id == ctx.workspace_id,
        NetworkEvent.dataset_id == BENCHMARK_DATASET_ID
    ).count()

    fsm_count = sum(1 for a in alerts if (a.engine or "").lower() == "fsm")
    ml_count = sum(1 for a in alerts if (a.engine or "").lower() == "ml")
    hybrid_count = sum(1 for a in alerts if (a.engine or "").lower() == "hybrid")
    unknown_count = sum(1 for a in alerts if (a.engine or "").lower() not in ["fsm", "ml", "hybrid"])

    fsm_pct = round((fsm_count / max(total_alerts, 1)) * 100.0, 2) if total_alerts > 0 else 0.0
    ml_pct = round((ml_count / max(total_alerts, 1)) * 100.0, 2) if total_alerts > 0 else 0.0
    hybrid_pct = round((hybrid_count / max(total_alerts, 1)) * 100.0, 2) if total_alerts > 0 else 0.0

    return {
        "dataset_id": BENCHMARK_DATASET_ID,
        "source_tag": BENCHMARK_SOURCE_TAG,
        "has_benchmark_data": total_alerts > 0,
        "total_alerts": total_alerts,
        "total_events": total_events,
        "attribution_counts": {
            "fsm_only": fsm_count,
            "ml_only": ml_count,
            "hybrid_consensus": hybrid_count,
            "unknown": unknown_count
        },
        "attribution_percentages": {
            "fsm_only": f"{fsm_pct}%",
            "ml_only": f"{ml_pct}%",
            "hybrid_consensus": f"{hybrid_pct}%",
            "unknown": f"{unknown_count}%"
        },
        "academic_targets": {
            "fsm_target": "25% - 35%",
            "ml_target": "10% - 20%",
            "hybrid_target": "45% - 65%",
            "fsm_achieved": 25.0 <= fsm_pct <= 35.0,
            "ml_achieved": 10.0 <= ml_pct <= 20.0,
            "hybrid_achieved": 45.0 <= hybrid_pct <= 65.0,
        }
    }


@router.post("/reset")
def reset_academic_benchmark(
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Safely delete only benchmark alerts and events without touching live or historical data."""
    deleted = AcademicBenchmarkGenerator.reset_benchmark(db, workspace_id=ctx.workspace_id)
    return {
        "status": "success",
        "message": "Academic benchmark dataset cleared safely.",
        **deleted
    }
