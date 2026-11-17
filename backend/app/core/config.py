"""Application configuration."""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "TraceGuard AI"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "traceguard-dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Resolve absolute path to backend/traceguard.db so working directory doesn't cause split DBs
    _default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "traceguard.db"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")
    
    DEMO_USERNAME: str = os.getenv("DEMO_USERNAME", "demo")
    DEMO_PASSWORD: str = os.getenv("DEMO_PASSWORD", "traceguard2024")
    DEMO_EMAIL: str = os.getenv("DEMO_EMAIL", "demo@traceguard.ai")

    # Operating Mode: LOCAL_ACADEMIC (default, auth-free academic demo) vs PRODUCTION (strict JWT/RBAC)
    TRACEGUARD_MODE: str = os.getenv("TRACEGUARD_MODE", "LOCAL_ACADEMIC")
    LOCAL_ACADEMIC_MODE: bool = os.getenv("TRACEGUARD_MODE", "LOCAL_ACADEMIC").upper() in ["LOCAL_ACADEMIC", "ACADEMIC", "LOCAL"]
    ALLOW_PUBLIC_ACADEMIC_MODE: bool = os.getenv("ALLOW_PUBLIC_ACADEMIC_MODE", "false").lower() == "true"

    # Production SaaS Settings
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,https://traceguard.ai")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Rate Limiting & Upload Quotas
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_EVENTS_PER_SIMULATION: int = 2000
    RATE_LIMIT_PER_MINUTE: int = 120

    class Config:
        env_file = ".env"


settings = Settings()
