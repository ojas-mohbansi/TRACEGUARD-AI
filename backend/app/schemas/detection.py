"""Detection schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class DetectionRequest(BaseModel):
    session_ids: List[str]
    engines: List[str] = ["fsm", "ml", "hybrid"]
    dataset_id: Optional[str] = None


class DetectionResultItem(BaseModel):
    session_id: str
    engine: str
    prediction: str
    risk_score: int
    severity: str
    fsm_violation: bool = False
    ml_anomaly_score: float = 0.0
    explanation: Optional[str] = None
    responsible_events: List[str] = []
    processing_time_ms: float = 0.0


class DetectionResponse(BaseModel):
    results: List[DetectionResultItem]


class EngineMetrics(BaseModel):
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    detection_rate: float = 0.0
    false_positive_rate: float = 0.0
    false_alarms_per_100_benign: float = 0.0
    avg_processing_time_ms: float = 0.0
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    predictions: List[Dict[str, Any]] = []


class DetectionCompareResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    total_sessions: int
    engines: Dict[str, EngineMetrics]
    generalization: Dict[str, Any] = {
        "unseen_templates_tested": 0,
        "unseen_results": {}
    }
