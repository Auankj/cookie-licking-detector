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
from app.db.models import Repository, User, SystemSettings
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


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """
    Get settings from database or create default settings if none exist.
    Ensures single row table for application configuration.
    """
    stmt = select(SystemSettings).limit(1)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings on first access
        settings = SystemSettings(
            id=1,
            claim_timeout_hours=24,
            max_claims_per_user=3,
            auto_release_enabled=True,
            webhook_secret=None,
            notification_settings={
                "email_enabled": False,
                "slack_enabled": False,
                "discord_enabled": False
            },
            rate_limiting={
                "enabled": True,
                "requests_per_minute": 60
            },
            github_integration={
                "app_id": None,
                "installation_id": None,
                "webhook_url": None
            }
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.get("/settings", response_model=SystemSettingsModel)
async def get_settings(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get current system settings from database (admin only)
    """
    settings = await get_or_create_settings(db)
    
    # Convert database model to response model
    return SystemSettingsModel(
        claim_timeout_hours=settings.claim_timeout_hours,
        max_claims_per_user=settings.max_claims_per_user,
        auto_release_enabled=settings.auto_release_enabled,
        webhook_secret=settings.webhook_secret,
        notification_settings=NotificationSettings(**settings.notification_settings) if settings.notification_settings else NotificationSettings(),
        rate_limiting=RateLimitingSettings(**settings.rate_limiting) if settings.rate_limiting else RateLimitingSettings(),
        github_integration=GitHubIntegrationSettings(**settings.github_integration) if settings.github_integration else GitHubIntegrationSettings()
    )


@router.put("/settings", response_model=SystemSettingsModel)
async def update_settings(
    settings_update: SystemSettingsModel,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update system settings in database (admin only)
    """
    # Basic validation
    if settings_update.claim_timeout_hours < 1 or settings_update.claim_timeout_hours > 168:
        raise HTTPException(
            status_code=400,
            detail="claim_timeout_hours must be between 1 and 168 hours"
        )
    
    if settings_update.max_claims_per_user < 1 or settings_update.max_claims_per_user > 10:
        raise HTTPException(
            status_code=400,
            detail="max_claims_per_user must be between 1 and 10"
        )
    
    # Get existing settings or create new
    settings = await get_or_create_settings(db)
    
    # Update settings in database
    settings.claim_timeout_hours = settings_update.claim_timeout_hours
    settings.max_claims_per_user = settings_update.max_claims_per_user
    settings.auto_release_enabled = settings_update.auto_release_enabled
    settings.webhook_secret = settings_update.webhook_secret
    settings.notification_settings = settings_update.notification_settings.dict()
    settings.rate_limiting = settings_update.rate_limiting.dict()
    settings.github_integration = settings_update.github_integration.dict()
    
    await db.commit()
    await db.refresh(settings)
    
    return settings_update

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