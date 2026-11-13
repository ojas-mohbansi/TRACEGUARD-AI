"""Authentication, User, and Workspace Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TokenUser(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: TokenUser
    active_workspace_id: Optional[str] = None


# Workspace Schemas
class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class WorkspaceMemberAdd(BaseModel):
    username: str
    role: str = Field("analyst", pattern="^(owner|admin|analyst|viewer)$")


class WorkspaceMemberResponse(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class WorkspaceResponse(BaseModel):
    id: int
    workspace_id: str
    name: str
    slug: str
    owner_id: int
    subscription_tier: str
    max_simulations_per_day: int
    max_uploaded_datasets: int
    created_at: datetime
    role: Optional[str] = None  # Current user's role in this workspace

    class Config:
        from_attributes = True


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
