"""
Settings API Routes
Provides system configuration and monitoring endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

from app.db.database import get_async_session
from app.db.models import Repository, User
from app.core.security import get_current_user, require_admin

router = APIRouter()

class NotificationSettings(BaseModel):
    email_enabled: bool = False
    slack_enabled: bool = False
    discord_enabled: bool = False

class RateLimitingSettings(BaseModel):
    enabled: bool = True
    requests_per_minute: int = 60

class GitHubIntegrationSettings(BaseModel):
    app_id: Optional[str] = None
    installation_id: Optional[str] = None
    webhook_url: Optional[str] = None

class SystemSettingsModel(BaseModel):
    claim_timeout_hours: int = Field(default=24, ge=1, le=168)
    max_claims_per_user: int = Field(default=3, ge=1, le=10)
    auto_release_enabled: bool = True
    webhook_secret: Optional[str] = None
    notification_settings: NotificationSettings = NotificationSettings()
    rate_limiting: RateLimitingSettings = RateLimitingSettings()
    github_integration: GitHubIntegrationSettings = GitHubIntegrationSettings()

class SystemStats(BaseModel):
    total_requests: int
    average_response_time: int  # in milliseconds
    uptime_hours: float
    last_restart: str
    database_size: str
    cache_hit_rate: float

# Global settings store (in production, this should be in database table: system_settings)
# TODO: Migrate to database-backed storage for production scale-out
_system_settings = SystemSettingsModel()

@router.get("/settings", response_model=SystemSettingsModel)
async def get_settings(current_user: User = Depends(require_admin)):
    """
    Get current system settings (admin only)
    """
    return _system_settings

@router.put("/settings", response_model=SystemSettingsModel)
async def update_settings(
    settings: SystemSettingsModel,
    current_user: User = Depends(require_admin)
):
    """
    Update system settings (admin only)
    """
    global _system_settings
    
    # Basic validation
    if settings.claim_timeout_hours < 1 or settings.claim_timeout_hours > 168:
        raise HTTPException(
            status_code=400,
            detail="claim_timeout_hours must be between 1 and 168 hours"
        )
    
    if settings.max_claims_per_user < 1 or settings.max_claims_per_user > 10:
        raise HTTPException(
            status_code=400,
            detail="max_claims_per_user must be between 1 and 10"
        )
    
    _system_settings = settings
    return _system_settings

@router.get("/system/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Get system performance statistics (admin only)
    """
    
    # Get database statistics
    repo_count_stmt = select(func.count(Repository.id))
    repo_count_result = await db.execute(repo_count_stmt)
    repo_count = repo_count_result.scalar()
    
    # Calculate uptime (mock for now)
    uptime_hours = 168.5  # 1 week example
    
    # Mock stats (in production, these would come from monitoring systems)
    stats = SystemStats(
        total_requests=15420 + repo_count * 100,  # Mock calculation
        average_response_time=45,  # milliseconds
        uptime_hours=uptime_hours,
        last_restart=datetime.utcnow().isoformat(),
        database_size="12.4 MB",
        cache_hit_rate=89.2
    )
    
    return stats

@router.post("/system/restart")
async def restart_system(current_user: User = Depends(require_admin)):
    """
    Restart system (mock endpoint) - admin only
    In production, this would trigger a graceful restart
    """
    return {
        "message": "System restart initiated",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/health")
async def get_system_health(db: AsyncSession = Depends(get_async_session)):
    """
    Get system health status (public endpoint)
    """
    try:
        # Test database connection
        test_stmt = select(1)
        await db.execute(test_stmt)
        db_healthy = True
    except Exception:
        db_healthy = False
    
    health_status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    if not db_healthy:
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status