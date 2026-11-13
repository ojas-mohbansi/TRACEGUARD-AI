"""Network Event schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class EventItem(BaseModel):
    event_id: str
    session_id: str
    timestamp: datetime
    protocol: str = "HTTP"
    event_type: str
    source: str
    destination: str
    method: Optional[str] = None
    path_category: Optional[str] = None
    status_code: Optional[int] = None
    bytes: int = 0
    label: str = "normal"

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventItem]
    total: int
