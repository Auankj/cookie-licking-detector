"""
Nudge check Celery tasks - COMPLETE PRODUCTION IMPLEMENTATION
All fields, methods, and imports corrected - no placeholders
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.db.database import get_async_session_factory
from app.db.models.claims import Claim, ClaimStatus
from app.db.models.issues import Issue
from app.db.models.repositories import Repository
from app.db.models.activity_log import ActivityLog, ActivityType
from app.services.notification_service import NotificationService
from app.services.github_service import GitHubAPIService

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def check_stale_claims_task(self):
    """
    Check for stale claims that need nudging.
    
    Production implementation:
    - Calculates staleness from last_activity_timestamp + grace_period_days
    - Counts nudges from ActivityLog (ActivityType.PROGRESS_NUDGE)
    - Uses existing notification methods (send_nudge_email, post_nudge_comment)
    - Creates ActivityLog entries for tracking
    - Auto-releases after max nudges
    """
    try:
        async def process_stale_claims():
            session_factory = get_async_session_factory()
            async with session_factory() as session:
                try:
                    # Find all active claims with relationships
                    now = datetime.now(timezone.utc)
                    
                    stmt = select(Claim).where(
                        Claim.status == ClaimStatus.ACTIVE
                    ).options(
                        selectinload(Claim.issue).selectinload(Issue.repository),
                        selectinload(Claim.user)
                    )
                    
                    result = await session.execute(stmt)
                    active_claims = result.scalars().all()
                    
                    logger.info(f"Checking {len(active_claims)} active claims for staleness")
                    
                    processed_claims = []
                    
                    for claim in active_claims:
                        try:
                            # Get repository configuration
                            issue = claim.issue
                            repository = issue.repository
                            grace_period_days = repository.grace_period_days or 7
                            max_nudges = repository.nudge_count or 2
                            
                            # Calculate when grace period expires
                            grace_period_end = claim.last_activity_timestamp + timedelta(days=grace_period_days)
                            
                            # Check if claim is stale (past grace period)
                            if now <= grace_period_end:
                                logger.debug(f"Claim {claim.id} is still within grace period")
                                continue
                            
                            # Count previous nudges from ActivityLog
                            nudge_count_stmt = select(func.count(ActivityLog.id)).where(
                                ActivityLog.claim_id == claim.id,
                                ActivityLog.activity_type == ActivityType.PROGRESS_NUDGE
                            )
                            nudge_result = await session.execute(nudge_count_stmt)
                            nudge_count = nudge_result.scalar() or 0
                            
                            logger.info(f"Claim {claim.id} is stale ({nudge_count}/{max_nudges} nudges sent)")
                            
                            # If max nudges reached, auto-release
                            if nudge_count >= max_nudges:
                                logger.info(f"Claim {claim.id} has reached max nudges, scheduling auto-release")
                                auto_release_task.delay(claim.id)
                                continue
                            
                            # Send nudge
                            notification_service = NotificationService()
                            github_service = GitHubAPIService()
                            
                            # Send email nudge
                            email_sent = await notification_service.send_nudge_email(
                                claim=claim,
                                nudge_count=nudge_count + 1
                            )
                            
                            # Post comment on GitHub issue
                            repo_full_name = f"{repository.owner_name}/{repository.name}"
                            comment_posted = await github_service.post_nudge_comment(
                                repo_full_name=repo_full_name,
                                issue_number=issue.github_issue_number,
                                username=claim.github_username,
                                nudge_count=nudge_count + 1
                            )
                            
                            # Create activity log entry
                            activity_log = ActivityLog(
                                claim_id=claim.id,
                                issue_id=issue.id,
                                repository_id=repository.id,
                                activity_type=ActivityType.PROGRESS_NUDGE,
                                description=f"Sent nudge {nudge_count + 1}/{max_nudges} to {claim.github_username}",
                                timestamp=now,
                                activity_metadata={
                                    "nudge_number": nudge_count + 1,
                                    "max_nudges": max_nudges,
                                    "email_sent": email_sent,
                                    "comment_posted": comment_posted,
                                    "days_since_claim": (now - claim.claim_timestamp).days,
                                    "days_since_activity": (now - claim.last_activity_timestamp).days
                                }
                            )
                            session.add(activity_log)
                            
                            processed_claims.append({
                                "claim_id": claim.id,
                                "username": claim.github_username,
                                "issue_number": issue.github_issue_number,
                                "repository": repo_full_name,
                                "nudge_number": nudge_count + 1,
                                "email_sent": email_sent,
                                "comment_posted": comment_posted
                            })
                            
                        except Exception as e:
                            logger.error(f"Failed to process nudge for claim {claim.id}: {e}")
                            continue
                    
                    await session.commit()
                    return processed_claims
                    
                except Exception as e:
                    await session.rollback()
                    raise e
        
        # Run async operations
        processed_claims = asyncio.run(process_stale_claims())
        
        logger.info(f"Processed {len(processed_claims)} stale claims for nudging")
        
        return {
            "status": "completed",
            "claims_processed": len(processed_claims),
            "claims": processed_claims
        }
        
    except Exception as exc:
        logger.error(f"Stale claims check failed: {exc}")
        raise self.retry(countdown=300, exc=exc)  # Retry after 5 minutes


@celery_app.task(bind=True, max_retries=3)
def auto_release_task(self, claim_id: int):
    """
    Automatically release a stale claim after max nudges.
    
    Production implementation:
    - Sets status to ClaimStatus.RELEASED (not AUTO_RELEASED which doesn't exist)
    - Sets auto_release_timestamp and release_reason fields
    - Uses GitHubAPIService (not GitHubService)
    - Uses existing notification methods
    - Creates ActivityLog entry with ActivityType.AUTO_RELEASE
    """
    try:
        async def release_claim():
            session_factory = get_async_session_factory()
            async with session_factory() as session:
                try:
                    # Get the claim with relationships
                    stmt = select(Claim).where(
                        Claim.id == claim_id
                    ).options(
                        selectinload(Claim.issue).selectinload(Issue.repository),
                        selectinload(Claim.user)
                    )
                    result = await session.execute(stmt)
                    claim = result.scalar_one_or_none()
                    
                    if not claim or claim.status != ClaimStatus.ACTIVE:
                        logger.warning(f"Claim {claim_id} not found or not active")
                        return None
                    
                    # Get related data
                    issue = claim.issue
                    repository = issue.repository
                    now = datetime.now(timezone.utc)
                    
                    # Count nudges sent
                    nudge_count_stmt = select(func.count(ActivityLog.id)).where(
                        ActivityLog.claim_id == claim.id,
                        ActivityLog.activity_type == ActivityType.PROGRESS_NUDGE
                    )
                    nudge_result = await session.execute(nudge_count_stmt)
                    nudge_count = nudge_result.scalar() or 0
                    
                    # Update claim status - use RELEASED, not AUTO_RELEASED
                    claim.status = ClaimStatus.RELEASED
                    claim.auto_release_timestamp = now
                    claim.release_reason = "auto_released_after_max_nudges"
                    claim.release_timestamp = now
                    
                    # Create activity log with proper ActivityType
                    activity_log = ActivityLog(
                        claim_id=claim.id,
                        issue_id=issue.id,
                        repository_id=repository.id,
                        activity_type=ActivityType.AUTO_RELEASE,
                        description=f"Auto-released claim by {claim.github_username} after {nudge_count} nudges",
                        timestamp=now,
                        activity_metadata={
                            "reason": "max_nudges_exceeded",
                            "nudge_count": nudge_count,
                            "claim_duration_days": (now - claim.claim_timestamp).days,
                            "days_since_activity": (now - claim.last_activity_timestamp).days
                        }
                    )
                    session.add(activity_log)
                    
                    # Unassign issue on GitHub if assigned
                    github_service = GitHubAPIService()
                    repo_full_name = f"{repository.owner_name}/{repository.name}"
                    
                    try:
                        # Get current issue state from GitHub
                        github_issue = await github_service.get_issue(
                            owner=repository.owner_name,
                            name=repository.name,
                            issue_number=issue.github_issue_number
                        )
                        
                        # Check if user is assigned
                        assignees = github_issue.get('assignees', [])
                        is_assigned = any(
                            assignee.get('login') == claim.github_username 
                            for assignee in assignees
                        )
                        
                        if is_assigned:
                            await github_service.unassign_issue(
                                owner=repository.owner_name,
                                name=repository.name,
                                issue_number=issue.github_issue_number,
                                username=claim.github_username
                            )
                            logger.info(f"Unassigned {claim.github_username} from issue #{issue.github_issue_number}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to unassign issue on GitHub: {e}")
                    
                    # Send notifications
                    notification_service = NotificationService()
                    
                    # Send auto-release email to contributor
                    try:
                        await notification_service.send_auto_release_email(
                            claim=claim,
                            reason="Maximum nudges exceeded without progress"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send auto-release email to contributor: {e}")
                    
                    # Post auto-release comment on GitHub
                    try:
                        await github_service.post_auto_release_comment(
                            repo_full_name=repo_full_name,
                            issue_number=issue.github_issue_number,
                            username=claim.github_username,
                            claim_duration_days=(now - claim.claim_timestamp).days,
                            nudge_count=nudge_count
                        )
                    except Exception as e:
                        logger.warning(f"Failed to post auto-release comment: {e}")
                    
                    # Notify maintainers
                    try:
                        await notification_service.send_maintainer_notification(
                            repository_full_name=repo_full_name,
                            event_type="auto_release",
                            details={
                                "issue_number": issue.github_issue_number,
                                "issue_title": issue.title,
                                "username": claim.github_username,
                                "claim_duration_days": (now - claim.claim_timestamp).days,
                                "nudge_count": nudge_count
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send maintainer notification: {e}")
                    
                    await session.commit()
                    
                    return {
                        "claim_id": claim.id,
                        "username": claim.github_username,
                        "issue_number": issue.github_issue_number,
                        "repository": repo_full_name,
                        "duration_days": (now - claim.claim_timestamp).days,
                        "nudge_count": nudge_count
                    }
                    
                except Exception as e:
                    await session.rollback()
                    raise e
        
        # Run async operations
        result = asyncio.run(release_claim())
        
        if result:
            logger.info(
                f"Auto-released claim {claim_id} for {result['username']} "
                f"on issue #{result['issue_number']} after {result['nudge_count']} nudges"
            )
        
        return {
            "status": "released",
            "claim_data": result
        }
        
    except Exception as exc:
        logger.error(f"Auto-release failed for claim {claim_id}: {exc}")
        raise self.retry(countdown=300, exc=exc)


@celery_app.task
def schedule_nudge_task(claim_id: int, delay_seconds: int):
    """
    Schedule a nudge check for a specific claim.
    """
    # Schedule the nudge check task to run after the grace period
    check_stale_claims_task.apply_async(
        countdown=delay_seconds,
        task_id=f"nudge_check_{claim_id}_{datetime.now(timezone.utc).isoformat()}"
    )
    
    logger.info(f"Scheduled nudge check for claim {claim_id} in {delay_seconds} seconds")
    
    return {
        "status": "scheduled",
        "claim_id": claim_id,
        "delay_seconds": delay_seconds
    }
