"""SQLAlchemy database models for TraceGuard AI with Multi-Tenant Workspaces & Role-Based Access Control."""
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class RoleEnum(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class SubscriptionTierEnum(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"ws_{uuid.uuid4().hex[:12]}")
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_tier = Column(String(20), default=SubscriptionTierEnum.FREE.value)
    max_simulations_per_day = Column(Integer, default=50)
    max_uploaded_datasets = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    events = relationship("NetworkEvent", back_populates="workspace", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="workspace", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="workspace", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="workspace", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Workspaces user is member of
    memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default=RoleEnum.ANALYST.value, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")


class NetworkEvent(Base):
    __tablename__ = "network_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=True, index=True, default="default-workspace")
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    dataset_id = Column(String(50), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    protocol = Column(String(20), default="HTTP")
    event_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    method = Column(String(10), nullable=True)
    path_category = Column(String(50), nullable=True)
    status_code = Column(Integer, nullable=True)
    bytes = Column(Integer, default=0)
    label = Column(String(20), default="normal")  # normal | anomalous
    simulation_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="events")


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=True, index=True, default="default-workspace")
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    dataset_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    engine = Column(String(20), nullable=False)  # fsm | ml | hybrid
    severity = Column(String(20), nullable=False)  # low | medium | high | critical
    risk_score = Column(Integer, default=0)
    prediction = Column(String(20), nullable=False)  # normal | anomalous
    status = Column(String(20), default="new")  # new | investigating | resolved | dismissed
    summary = Column(Text, nullable=True)
    fsm_result = Column(JSON, nullable=True)
    ml_result = Column(JSON, nullable=True)
    hybrid_result = Column(JSON, nullable=True)
    responsible_events = Column(JSON, nullable=True)  # list of event_ids
    investigation_notes = Column(Text, nullable=True)
    processing_time_ms = Column(Float, default=0.0)

    workspace = relationship("Workspace", back_populates="alerts")


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=True, index=True, default="default-workspace")
    dataset_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    format = Column(String(10), nullable=False)  # csv | json
    file_path = Column(String(500), nullable=False)
    event_count = Column(Integer, default=0)
    session_count = Column(Integer, default=0)
    has_labels = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="datasets")


class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(50), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=True, index=True, default="default-workspace")
    simulation_id = Column(String(50), unique=True, nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    config = Column(JSON, nullable=True)
    status = Column(String(20), default="running")  # running | stopped | completed
    events_generated = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", back_populates="simulations")
