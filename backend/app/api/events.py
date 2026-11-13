"""Network Events API router with workspace scoping."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import NetworkEvent
from app.schemas.events import EventListResponse, EventItem
from app.core.security import get_current_workspace_context, WorkspaceContext

router = APIRouter()


@router.get("", response_model=EventListResponse)
def list_events(
    session_id: Optional[str] = Query(None),
    protocol: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Retrieve network events isolated to the current workspace."""
    if ctx.workspace_id == "default-workspace":
        query = db.query(NetworkEvent).filter(
            (NetworkEvent.workspace_id == ctx.workspace_id) | 
            (NetworkEvent.workspace_id == None) | 
            (NetworkEvent.workspace_id == "default-workspace")
        )
    else:
        query = db.query(NetworkEvent).filter(NetworkEvent.workspace_id == ctx.workspace_id)

    if session_id:
        query = query.filter(NetworkEvent.session_id == session_id)
    if protocol:
        query = query.filter(NetworkEvent.protocol == protocol)

    total = query.count()
    events = query.order_by(NetworkEvent.timestamp.desc()).offset(offset).limit(limit).all()

    return EventListResponse(
        events=[EventItem.model_validate(e) for e in events],
        total=total
    )
