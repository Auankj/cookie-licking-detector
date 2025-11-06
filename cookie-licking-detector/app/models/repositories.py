from sqlalchemy import Column, Integer, BigInteger, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Repository(Base):
    """
    Repository model matching migration 003 schema:
    repositories table with monitoring configuration
    """
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_repo_id = Column(BigInteger, unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # FK to users table
    owner_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), unique=True, nullable=False)
    url = Column(String(512), nullable=False)
    is_monitored = Column(Boolean, default=True, nullable=False)
    grace_period_days = Column(Integer, default=7, nullable=False)
    nudge_count = Column(Integer, default=2, nullable=False)
    notification_settings = Column(JSON, nullable=True)
    claim_detection_threshold = Column(Integer, default=75, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], backref="repositories")
    issues = relationship("Issue", back_populates="repository")

    def __repr__(self):
        return f"<Repository {self.full_name}>"