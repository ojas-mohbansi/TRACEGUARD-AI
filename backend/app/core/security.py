"""Security, authentication, and multi-tenant workspace context utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.models import User, Workspace, WorkspaceMember, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _safe_password_bytes(password: str) -> bytes:
    """Ensure password is byte-encoded and truncated to 72 bytes."""
    return str(password).encode("utf-8")[:72]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    try:
        return bcrypt.checkpw(_safe_password_bytes(plain_password), hashed_password.encode("utf-8"))
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_safe_password_bytes(password), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def _ensure_demo_user(db: Session) -> User:
    """Get or create the demo user (used for unauthenticated dev access)."""
    from app.api.auth import ensure_demo_user_and_workspace
    user, _ = ensure_demo_user_and_workspace(db)
    return user


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to retrieve the authenticated user from JWT token.
    In development mode, unauthenticated requests fall back to the demo user.
    """
    if not token:
        if getattr(settings, "ENVIRONMENT", "development") == "development":
            return _ensure_demo_user(db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency to retrieve user if authenticated, or None if anonymous."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None
        return db.query(User).filter(User.username == username, User.is_active == True).first()
    except Exception:
        return None


class WorkspaceContext:
    """Holds active workspace and the requesting user's role in it."""
    def __init__(self, workspace: Workspace, user: User, role: str):
        self.workspace = workspace
        self.user = user
        self.role = role

    @property
    def workspace_id(self) -> str:
        return self.workspace.workspace_id

    def can_view(self) -> bool:
        return self.role in [RoleEnum.OWNER.value, RoleEnum.ADMIN.value, RoleEnum.ANALYST.value, RoleEnum.VIEWER.value]

    def can_operate(self) -> bool:
        """Can run simulations, start detection, upload datasets."""
        return self.role in [RoleEnum.OWNER.value, RoleEnum.ADMIN.value, RoleEnum.ANALYST.value]

    def can_manage_members(self) -> bool:
        return self.role in [RoleEnum.OWNER.value, RoleEnum.ADMIN.value]

    def is_owner(self) -> bool:
        return self.role == RoleEnum.OWNER.value


def get_current_workspace_context(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceContext:
    """Validate user's membership and permissions in the requested workspace."""
    # If header not provided, find the user's first available workspace
    if not x_workspace_id:
        membership = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
        if not membership:
            # Auto-create a default workspace for this user if none exists
            slug = f"{current_user.username}-personal"
            ws = Workspace(
                name=f"{current_user.username.capitalize()}'s Workspace",
                slug=slug,
                owner_id=current_user.id,
                subscription_tier="free"
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
            return WorkspaceContext(workspace=ws, user=current_user, role=RoleEnum.OWNER.value)

        ws = db.query(Workspace).filter(Workspace.workspace_id == membership.workspace_id).first()
        return WorkspaceContext(workspace=ws, user=current_user, role=membership.role)

    # Check that requested workspace exists
    ws = db.query(Workspace).filter(Workspace.workspace_id == x_workspace_id).first()
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Check user membership
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == x_workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this workspace"
        )

    return WorkspaceContext(workspace=ws, user=current_user, role=membership.role)
