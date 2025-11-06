from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import enum

class ActivityType(str, enum.Enum):
    CLAIM_DETECTED = "claim_detected"
    CLAIM_RELEASED = "claim_released"
    NUDGE_SENT = "nudge_sent"
    ISSUE_CLOSED = "issue_closed"
    ISSUE_REOPENED = "issue_reopened"
    PROGRESS_UPDATE = "progress_update"
    AUTO_RELEASE = "auto_release"
    MANUAL_RELEASE = "manual_release"

class ActivityLog(Base):
    """
    Activity Log model matching migration 003 schema:
    activity_log table for tracking all system activities
    """
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(Enum(ActivityType, name="activitytype"), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    activity_metadata = Column(JSON, nullable=True)

    # Relationships
    claim = relationship("Claim", back_populates="activity_logs")

    def __repr__(self):
        return f"<ActivityLog {self.activity_type} for Claim {self.claim_id}>"