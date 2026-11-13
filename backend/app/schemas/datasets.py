"""Dataset schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    name: str
    description: Optional[str] = None
    format: str = "csv"
    event_count: int
    session_count: int
    created_at: Optional[datetime] = None
    message: Optional[str] = None


class DatasetItem(BaseModel):
    dataset_id: str
    name: str
    description: Optional[str] = None
    format: str
    event_count: int
    session_count: int
    created_at: datetime
    has_labels: bool

    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    datasets: List[DatasetItem]
    total: int = 0
