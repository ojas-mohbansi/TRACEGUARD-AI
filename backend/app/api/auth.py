"""Authentication, User profile, and Workspace management endpoints."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Workspace, WorkspaceMember, RoleEnum, SubscriptionTierEnum
from app.schemas.auth import (
    UserSignup, UserLogin, UserResponse, TokenResponse, TokenUser,
    PasswordChangeRequest, UserProfileUpdate,
    WorkspaceCreate, WorkspaceResponse, WorkspaceDetailResponse, WorkspaceMemberAdd, WorkspaceMemberResponse
)
from app.core.security import (
    verify_password, hash_password, create_access_token,
    get_current_user, get_current_workspace_context, WorkspaceContext
)
from app.core.config import settings

router = APIRouter()


def ensure_demo_user_and_workspace(db: Session):
    """Ensure the default demo user and demo workspace exist."""
    user = db.query(User).filter(User.username == settings.DEMO_USERNAME).first()
    if not user:
        user = User(
            username=settings.DEMO_USERNAME,
            email=settings.DEMO_EMAIL,
            full_name="TraceGuard Demo Operator",
            hashed_password=hash_password(settings.DEMO_PASSWORD),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Ensure demo workspace
    ws = db.query(Workspace).filter(Workspace.slug == "default-workspace").first()
    if not ws:
        ws = Workspace(
            workspace_id="default-workspace",
            name="Demo Security Ops",
            slug="default-workspace",
            owner_id=user.id,
            subscription_tier=SubscriptionTierEnum.PRO.value
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)

        member = WorkspaceMember(
            workspace_id=ws.workspace_id,
            user_id=user.id,
            role=RoleEnum.OWNER.value
        )
        db.add(member)
        db.commit()

    return user, ws


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user account and provision their initial personal workspace."""
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name or data.username.capitalize(),
        hashed_password=hash_password(data.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Provision user's personal default workspace
    ws_slug = f"{user.username}-personal-{uuid.uuid4().hex[:6]}"
    ws = Workspace(
        workspace_id=f"ws_{uuid.uuid4().hex[:12]}",
        name=f"{user.username.capitalize()}'s Workspace",
        slug=ws_slug,
        owner_id=user.id,
        subscription_tier=SubscriptionTierEnum.FREE.value
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)

    member = WorkspaceMember(
        workspace_id=ws.workspace_id,
        user_id=user.id,
        role=RoleEnum.OWNER.value
    )
    db.add(member)
    db.commit()

    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token with active workspace."""
    if data.username == settings.DEMO_USERNAME:
        ensure_demo_user_and_workspace(db)

    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find user's active workspace
    first_member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).first()
    active_ws_id = first_member.workspace_id if first_member else "default-workspace"

    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=TokenUser(id=user.id, username=user.username, email=user.email, full_name=user.full_name),
        active_workspace_id=active_ws_id
    )


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user email or full name."""
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
        current_user.email = data.email
    if data.full_name:
        current_user.full_name = data.full_name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password."""
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"status": "success", "message": "Password changed successfully"}


# ---------------- WORKSPACE ENDPOINTS ----------------

@router.get("/workspaces", response_model=List[WorkspaceResponse])
def list_user_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workspaces the current user is a member of."""
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    results = []
    for m in memberships:
        ws = db.query(Workspace).filter(Workspace.workspace_id == m.workspace_id).first()
        if ws:
            results.append(WorkspaceResponse(
                id=ws.id,
                workspace_id=ws.workspace_id,
                name=ws.name,
                slug=ws.slug,
                owner_id=ws.owner_id,
                subscription_tier=ws.subscription_tier,
                max_simulations_per_day=ws.max_simulations_per_day,
                max_uploaded_datasets=ws.max_uploaded_datasets,
                created_at=ws.created_at,
                role=m.role
            ))
    return results


@router.post("/workspaces", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace and assign owner role to creator."""
    slug = f"{data.name.lower().replace(' ', '-')[:30]}-{uuid.uuid4().hex[:6]}"
    ws = Workspace(
        workspace_id=f"ws_{uuid.uuid4().hex[:12]}",
        name=data.name,
        slug=slug,
        owner_id=current_user.id,
        subscription_tier=SubscriptionTierEnum.FREE.value
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)

    member = WorkspaceMember(
        workspace_id=ws.workspace_id,
        user_id=current_user.id,
        role=RoleEnum.OWNER.value
    )
    db.add(member)
    db.commit()

    return WorkspaceResponse(
        id=ws.id,
        workspace_id=ws.workspace_id,
        name=ws.name,
        slug=ws.slug,
        owner_id=ws.owner_id,
        subscription_tier=ws.subscription_tier,
        max_simulations_per_day=ws.max_simulations_per_day,
        max_uploaded_datasets=ws.max_uploaded_datasets,
        created_at=ws.created_at,
        role=RoleEnum.OWNER.value
    )


@router.get("/workspaces/{ws_id}", response_model=WorkspaceDetailResponse)
def get_workspace_details(
    ws_id: str,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Get detailed information about active workspace and its members."""
    ws = ctx.workspace
    members = db.query(WorkspaceMember, User).join(User, WorkspaceMember.user_id == User.id).filter(
        WorkspaceMember.workspace_id == ws.workspace_id
    ).all()

    member_responses = [
        WorkspaceMemberResponse(
            id=m.WorkspaceMember.id,
            user_id=m.User.id,
            username=m.User.username,
            email=m.User.email,
            role=m.WorkspaceMember.role,
            joined_at=m.WorkspaceMember.joined_at
        ) for m in members
    ]

    return WorkspaceDetailResponse(
        id=ws.id,
        workspace_id=ws.workspace_id,
        name=ws.name,
        slug=ws.slug,
        owner_id=ws.owner_id,
        subscription_tier=ws.subscription_tier,
        max_simulations_per_day=ws.max_simulations_per_day,
        max_uploaded_datasets=ws.max_uploaded_datasets,
        created_at=ws.created_at,
        role=ctx.role,
        members=member_responses
    )


@router.post("/workspaces/{ws_id}/members", response_model=WorkspaceMemberResponse)
def add_workspace_member(
    ws_id: str,
    data: WorkspaceMemberAdd,
    ctx: WorkspaceContext = Depends(get_current_workspace_context),
    db: Session = Depends(get_db)
):
    """Add a member to the workspace (Admin or Owner only)."""
    if not ctx.can_manage_members():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin or Owner role required to invite members"
        )

    target_user = db.query(User).filter(User.username == data.username).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == ctx.workspace.workspace_id,
        WorkspaceMember.user_id == target_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")

    new_member = WorkspaceMember(
        workspace_id=ctx.workspace.workspace_id,
        user_id=target_user.id,
        role=data.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return WorkspaceMemberResponse(
        id=new_member.id,
        user_id=target_user.id,
        username=target_user.username,
        email=target_user.email,
        role=new_member.role,
        joined_at=new_member.joined_at
    )
