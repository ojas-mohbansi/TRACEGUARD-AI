"""API Health Check Router."""
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint confirming database and model availability."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Check if models exist (ml model file in project root models/ or backend/models/)
    root_models = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "models")
    backend_models = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
    models_loaded = (
        os.path.exists(os.path.join(root_models, "isolation_forest.joblib")) or
        os.path.exists(os.path.join(backend_models, "isolation_forest.joblib"))
    )

    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": db_status,
        "models_loaded": models_loaded,
    }
