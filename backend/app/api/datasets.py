"""Datasets API router with workspace isolation and file upload security controls."""
from datetime import datetime
from uuid import uuid4
import os
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Dataset, NetworkEvent
from app.schemas.datasets import DatasetListResponse, DatasetItem, DatasetUploadResponse
from app.core.security import get_current_workspace_context, WorkspaceContext
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploaded_datasets")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Upload a dataset file (CSV or JSON) and parse events into database with security boundaries."""
    if not ctx.can_operate():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Viewer role cannot upload datasets"
        )

    # Check workspace dataset quota
    current_count = db.query(Dataset).filter(Dataset.workspace_id == ctx.workspace_id).count()
    if current_count >= ctx.workspace.max_uploaded_datasets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quota exceeded: Your workspace plan allows up to {ctx.workspace.max_uploaded_datasets} datasets."
        )

    filename = file.filename or "dataset"
    ext = filename.split(".")[-1].lower()
    if ext not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are supported")

    ds_id = f"ds_{uuid4().hex[:12]}"
    file_path = os.path.join(UPLOAD_DIR, f"{ds_id}_{filename}")

    # Read content with file size limit check
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload size limit ({settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB)"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    events_to_insert = []
    has_labels = False

    try:
        if ext == "csv":
            df = pd.read_csv(file_path)
            has_labels = "label" in df.columns
            for _, row in df.iterrows():
                ts_raw = row.get("timestamp")
                try:
                    ts = pd.to_datetime(ts_raw).to_pydatetime() if pd.notnull(ts_raw) else datetime.utcnow()
                except Exception:
                    ts = datetime.utcnow()

                event = NetworkEvent(
                    workspace_id=ctx.workspace_id,
                    event_id=str(row.get("event_id") or f"evt_{uuid4().hex[:12]}"),
                    session_id=str(row.get("session_id") or f"sess_{uuid4().hex[:8]}"),
                    dataset_id=ds_id,
                    timestamp=ts,
                    protocol=str(row.get("protocol") or "HTTP"),
                    event_type=str(row.get("event_type") or "UNKNOWN"),
                    source=str(row.get("source") or "127.0.0.1"),
                    destination=str(row.get("destination") or "127.0.0.1"),
                    method=str(row.get("method")) if pd.notnull(row.get("method")) else None,
                    path_category=str(row.get("path_category")) if pd.notnull(row.get("path_category")) else None,
                    status_code=int(row["status_code"]) if pd.notnull(row.get("status_code")) else None,
                    bytes=int(row["bytes"]) if pd.notnull(row.get("bytes")) else 0,
                    label=str(row.get("label") or "normal")
                )
                events_to_insert.append(event)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    has_labels = has_labels or ("label" in item)
                    ts_raw = item.get("timestamp")
                    try:
                        ts = datetime.fromisoformat(ts_raw) if ts_raw else datetime.utcnow()
                    except Exception:
                        ts = datetime.utcnow()

                    event = NetworkEvent(
                        workspace_id=ctx.workspace_id,
                        event_id=item.get("event_id", f"evt_{uuid4().hex[:12]}"),
                        session_id=item.get("session_id", f"sess_{uuid4().hex[:8]}"),
                        dataset_id=ds_id,
                        timestamp=ts,
                        protocol=item.get("protocol", "HTTP"),
                        event_type=item.get("event_type", "UNKNOWN"),
                        source=item.get("source", "127.0.0.1"),
                        destination=item.get("destination", "127.0.0.1"),
                        method=item.get("method"),
                        path_category=item.get("path_category"),
                        status_code=item.get("status_code"),
                        bytes=item.get("bytes", 0),
                        label=item.get("label", "normal")
                    )
                    events_to_insert.append(event)

        db.bulk_save_objects(events_to_insert)

        session_count = len(set(e.session_id for e in events_to_insert))
        dataset = Dataset(
            workspace_id=ctx.workspace_id,
            dataset_id=ds_id,
            name=name,
            description=description,
            format=ext,
            file_path=file_path,
            event_count=len(events_to_insert),
            session_count=session_count,
            has_labels=has_labels,
            created_at=datetime.utcnow()
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return DatasetUploadResponse(
            dataset_id=dataset.dataset_id,
            name=dataset.name,
            event_count=dataset.event_count,
            session_count=dataset.session_count,
            format=dataset.format,
            message="Dataset uploaded and ingested successfully"
        )
    except Exception as e:
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse and store dataset: {str(e)}")


@router.get("", response_model=DatasetListResponse)
def list_datasets(
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """List datasets scoped to active workspace."""
    if ctx.workspace_id == "default-workspace":
        query = db.query(Dataset).filter(
            (Dataset.workspace_id == ctx.workspace_id) | 
            (Dataset.workspace_id == None) | 
            (Dataset.workspace_id == "default-workspace")
        )
    else:
        query = db.query(Dataset).filter(Dataset.workspace_id == ctx.workspace_id)

    datasets = query.order_by(Dataset.created_at.desc()).all()
    return DatasetListResponse(
        datasets=[DatasetItem.model_validate(d) for d in datasets],
        total=len(datasets)
    )


@router.get("/{dataset_id}/download")
def download_dataset(
    dataset_id: str,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Download the original dataset file with workspace authorization check."""
    ds = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if ds.workspace_id and ds.workspace_id != ctx.workspace_id and ctx.workspace_id != "default-workspace":
        raise HTTPException(status_code=403, detail="Access denied: Dataset belongs to another workspace")

    if not os.path.exists(ds.file_path):
        raise HTTPException(status_code=404, detail="Dataset file missing on server")

    media_type = "text/csv" if ds.format == "csv" else "application/json"
    filename = os.path.basename(ds.file_path)
    return FileResponse(ds.file_path, media_type=media_type, filename=filename)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: str,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Delete a dataset and its events (Analyst, Admin, Owner)."""
    if not ctx.can_operate():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Viewer role cannot delete datasets")

    ds = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if ds.workspace_id and ds.workspace_id != ctx.workspace_id and ctx.workspace_id != "default-workspace":
        raise HTTPException(status_code=403, detail="Access denied: Dataset belongs to another workspace")

    if os.path.exists(ds.file_path):
        os.remove(ds.file_path)

    db.query(NetworkEvent).filter(NetworkEvent.dataset_id == dataset_id).delete()
    db.delete(ds)
    db.commit()
    return None
