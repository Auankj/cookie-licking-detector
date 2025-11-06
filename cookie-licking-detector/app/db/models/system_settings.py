"""
System Settings model for persistent configuration storage.
Ensures multi-worker consistency by storing settings in database.
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.db.database import Base


class SystemSettings(Base):
    """
    System Settings model - single row table for application configuration.
    Provides durability and multi-worker consistency for runtime settings.
    """
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Claim management settings
    claim_timeout_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    max_claims_per_user: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    auto_release_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Integration settings
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Notification settings (stored as JSON)
    notification_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    
    # Rate limiting settings (stored as JSON)
    rate_limiting: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    
    # GitHub integration settings (stored as JSON)
    github_integration: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    def __repr__(self):
        return f"<SystemSettings(id={self.id}, claim_timeout_hours={self.claim_timeout_hours})>"
