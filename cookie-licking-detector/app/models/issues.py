from sqlalchemy import Column, Integer, BigInteger, String, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import enum

class IssueStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"

class Issue(Base):
    """
    Issue model matching migration 003 schema:
    issues table with GitHub issue data
    """
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    github_repo_id = Column(BigInteger, nullable=False)
    github_issue_id = Column(BigInteger, unique=True, nullable=False)
    github_issue_number = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(IssueStatus, name="issuestatus"), default=IssueStatus.OPEN, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    github_data = Column(JSON, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="issues")
    claims = relationship("Claim", back_populates="issue")

    def __repr__(self):
        return f"<Issue #{self.github_issue_number}: {self.title}>"