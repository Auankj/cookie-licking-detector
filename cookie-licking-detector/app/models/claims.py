from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import enum

class ClaimStatus(str, enum.Enum):
    ACTIVE = "active"
    RELEASED = "released"
    COMPLETED = "completed"
    EXPIRED = "expired"

class Claim(Base):
    """
    Claims model matching migration 003 schema:
    claims table with confidence scoring and context metadata
    """
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    github_user_id = Column(BigInteger, nullable=False)
    github_username = Column(String(255), nullable=False)
    claim_comment_id = Column(BigInteger, nullable=True)
    claim_text = Column(Text, nullable=True)
    claim_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(Enum(ClaimStatus, name="claimstatus"), default=ClaimStatus.ACTIVE, nullable=False)
    first_nudge_sent_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    auto_release_timestamp = Column(DateTime(timezone=True), nullable=True)
    release_reason = Column(String(255), nullable=True)
    confidence_score = Column(Integer, nullable=True)
    context_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)

    # Relationships
    issue = relationship("Issue", back_populates="claims")
    repository = relationship("Repository", foreign_keys=[repository_id])
    user = relationship("User", foreign_keys=[user_id])
    activity_logs = relationship("ActivityLog", back_populates="claim")
    progress_tracking = relationship("ProgressTracking", back_populates="claim", uselist=False)

    def __repr__(self):
        return f"<Claim by {self.github_username} on Issue #{self.issue_id}>"