"""
Repository Management Endpoints
As specified in MD file API Design section:
- POST /api/repositories
- GET /api/repositories  
- PUT /api/repositories/{id}
- DELETE /api/repositories/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_async_session
from app.db.models import Repository, User
from app.core.security import get_current_user

router = APIRouter()

# Pydantic models for API
class RepositoryCreate(BaseModel):
    owner: str
    name: str
    grace_period_days: int = 7
    nudge_count: int = 2
    claim_detection_threshold: int = 75
    notification_settings: dict = {}

class RepositoryUpdate(BaseModel):
    grace_period_days: Optional[int] = None
    nudge_count: Optional[int] = None
    is_monitored: Optional[bool] = None
    claim_detection_threshold: Optional[int] = None
    notification_settings: Optional[dict] = None

class RepositoryResponse(BaseModel):
    id: int
    github_repo_id: int
    owner_name: str
    name: str
    full_name: str
    url: str
    is_monitored: bool
    grace_period_days: int
    nudge_count: int
    claim_detection_threshold: int
    notification_settings: Optional[dict] = {}
    total_issues: int = 0
    active_claims_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/repositories", response_model=RepositoryResponse)
async def register_repository(
    repo_data: RepositoryCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new repository for monitoring
    As specified in MD file: POST /api/repositories
    """
    
    try:
        # Check if repository already exists
        stmt = select(Repository).where(
            Repository.owner_name == repo_data.owner,
            Repository.name == repo_data.name
        )
        result = await db.execute(stmt)
        existing_repo = result.scalar_one_or_none()
        
        if existing_repo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Repository {repo_data.owner}/{repo_data.name} already registered"
            )
        
        # Fetch real GitHub repository data
        from app.services.github_service import get_github_service
        github_service = get_github_service()
        
        try:
            repo_info = await github_service.get_repository(repo_data.owner, repo_data.name)
            github_repo_id = repo_info['id']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not find repository {repo_data.owner}/{repo_data.name} on GitHub: {str(e)}"
            )
        
        # Create repository record
        new_repo = Repository(
            github_repo_id=github_repo_id,
            owner_name=repo_data.owner,
            name=repo_data.name,
            full_name=f"{repo_data.owner}/{repo_data.name}",
            url=f"https://github.com/{repo_data.owner}/{repo_data.name}",
            grace_period_days=repo_data.grace_period_days,
            nudge_count=repo_data.nudge_count,
            claim_detection_threshold=repo_data.claim_detection_threshold,
            notification_settings=repo_data.notification_settings,
            is_monitored=True
        )
        
        db.add(new_repo)
        await db.commit()
        await db.refresh(new_repo)
        
        return new_repo
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering repository: {str(e)}"
        )

@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    status_filter: Optional[str] = Query(None, description="Filter by monitoring status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List monitored repositories
    As specified in MD file: GET /api/repositories
    """
    from sqlalchemy import func
    from app.db.models.issues import Issue
    from app.db.models.claims import Claim, ClaimStatus
    
    stmt = select(Repository)
    
    # Apply status filter
    if status_filter == "active":
        stmt = stmt.where(Repository.is_monitored == True)
    elif status_filter == "inactive":
        stmt = stmt.where(Repository.is_monitored == False)
    
    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    repositories = result.scalars().all()
    
    # Enrich with counts
    enriched_repos = []
    for repo in repositories:
        # Count total issues
        issues_stmt = select(func.count(Issue.id)).where(Issue.repository_id == repo.id)
        issues_result = await db.execute(issues_stmt)
        total_issues = issues_result.scalar() or 0
        
        # Count active claims
        claims_stmt = select(func.count(Claim.id)).where(
            Claim.repository_id == repo.id,
            Claim.status == ClaimStatus.ACTIVE
        )
        claims_result = await db.execute(claims_stmt)
        active_claims = claims_result.scalar() or 0
        
        # Create response dict
        repo_dict = {
            "id": repo.id,
            "github_repo_id": repo.github_repo_id,
            "owner_name": repo.owner_name,
            "name": repo.name,
            "full_name": repo.full_name,
            "url": repo.url,
            "is_monitored": repo.is_monitored,
            "grace_period_days": repo.grace_period_days,
            "nudge_count": repo.nudge_count,
            "claim_detection_threshold": repo.claim_detection_threshold,
            "notification_settings": repo.notification_settings or {},
            "total_issues": total_issues,
            "active_claims_count": active_claims,
            "created_at": repo.created_at,
            "updated_at": repo.updated_at
        }
        enriched_repos.append(repo_dict)
    
    return enriched_repos

@router.put("/repositories/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: int,
    repo_update: RepositoryUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update repository settings
    As specified in MD file: PUT /api/repositories/{id}
    """
    
    # Get repository
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {repo_id} not found"
        )
    
    try:
        # Update fields
        update_data = repo_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(repository, field, value)
        
        await db.commit()
        await db.refresh(repository)
        
        return repository
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating repository: {str(e)}"
        )

@router.delete("/repositories/{repo_id}")
async def stop_monitoring_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Stop monitoring a repository  
    As specified in MD file: DELETE /api/repositories/{id}
    """
    
    # Get repository
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {repo_id} not found"
        )
    
    try:
        # Instead of deleting, mark as not monitored
        repository.is_monitored = False
        await db.commit()
        
        return {
            "message": f"Stopped monitoring repository {repository.owner_name}/{repository.name}",
            "repository_id": repo_id
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping monitoring: {str(e)}"
        )
