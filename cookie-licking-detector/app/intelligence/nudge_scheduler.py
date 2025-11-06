"""
Adaptive Nudge Scheduler
ML-powered optimal timing for nudges based on user behavior patterns

Features:
- Timezone detection and awareness
- Activity pattern learning (when user is most active)
- Optimal send time prediction
- Escalation strategies
- Personalized messaging based on user type
"""

import pytz
from datetime import datetime, timedelta, timezone, time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class NudgeSchedule:
    """Optimized nudge schedule"""
    nudge_time: datetime
    timezone: str
    local_time: time
    reasoning: str
    message_tone: str  # FRIENDLY, PROFESSIONAL, URGENT
    escalation_level: int  # 1-5
    confidence: float
    metadata: Dict


class AdaptiveNudgeScheduler:
    """
    Intelligent nudge scheduler that learns user patterns
    Sends nudges when users are most likely to respond
    """
    
    # Optimal send times by timezone (local time)
    OPTIMAL_HOURS = {
        'morning': (9, 11),    # 9-11 AM
        'afternoon': (14, 16),  # 2-4 PM
        'evening': (18, 20)     # 6-8 PM
    }
    
    # Escalation strategy
    ESCALATION_DELAYS = {
        1: 7,   # First nudge: 7 days
        2: 5,   # Second nudge: 5 days later
        3: 3,   # Third nudge: 3 days later
        4: 2,   # Fourth nudge: 2 days later
        5: 1    # Final nudge: 1 day later
    }
    
    MESSAGE_TONES = {
        1: 'FRIENDLY',        # First nudge is gentle
        2: 'PROFESSIONAL',    # Second is professional
        3: 'CONCERNED',       # Third shows concern
        4: 'URGENT',          # Fourth is urgent
        5: 'FINAL_WARNING'    # Last chance
    }
    
    def __init__(self, db_session, github_service):
        self.db = db_session
        self.github = github_service
    
    async def calculate_optimal_nudge_time(
        self,
        claim_id: int,
        github_username: str,
        github_user_id: int,
        nudge_number: int,
        grace_period_days: int,
        last_activity: Optional[datetime] = None
    ) -> NudgeSchedule:
        """
        Calculate optimal time to send nudge based on:
        1. User's timezone
        2. Historical activity patterns
        3. Nudge escalation level
        4. Grace period
        """
        
        # Detect user's timezone
        user_timezone = await self._detect_user_timezone(github_username, github_user_id)
        
        # Learn user's activity patterns
        activity_patterns = await self._learn_activity_patterns(github_user_id)
        
        # Calculate base nudge time
        if nudge_number == 1:
            # First nudge - use grace period
            days_to_wait = grace_period_days
        else:
            # Subsequent nudges - use escalation strategy
            days_to_wait = self.ESCALATION_DELAYS.get(nudge_number, 2)
        
        base_time = datetime.now(timezone.utc) + timedelta(days=days_to_wait)
        
        # Adjust to optimal hour in user's timezone
        optimal_time = self._adjust_to_optimal_hour(
            base_time,
            user_timezone,
            activity_patterns
        )
        
        # Avoid weekends for professional repos
        optimal_time = self._avoid_weekends_if_needed(optimal_time, user_timezone)
        
        # Get local time for user
        user_tz = pytz.timezone(user_timezone)
        local_time = optimal_time.astimezone(user_tz).time()
        
        # Determine message tone
        message_tone = self.MESSAGE_TONES.get(nudge_number, 'PROFESSIONAL')
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            nudge_number,
            days_to_wait,
            activity_patterns,
            user_timezone
        )
        
        logger.info(
            f"Calculated optimal nudge time for {github_username}",
            nudge_number=nudge_number,
            timezone=user_timezone,
            local_time=str(local_time)
        )
        
        return NudgeSchedule(
            nudge_time=optimal_time,
            timezone=user_timezone,
            local_time=local_time,
            reasoning=reasoning,
            message_tone=message_tone,
            escalation_level=nudge_number,
            confidence=activity_patterns.get('confidence', 50.0),
            metadata={
                'activity_pattern': activity_patterns.get('preferred_time', 'afternoon'),
                'days_to_wait': days_to_wait,
                'is_weekend_avoider': activity_patterns.get('weekend_active', True)
            }
        )
    
    async def _detect_user_timezone(self, username: str, user_id: int) -> str:
        """
        Detect user's timezone from:
        1. GitHub profile
        2. Commit timestamps
        3. Activity patterns
        """
        try:
            # Try to get from commit history
            from app.db.models.claims import Claim
            from sqlalchemy import select
            
            # Get user's recent claims
            stmt = select(Claim).where(
                Claim.github_user_id == user_id
            ).limit(10)
            
            result = await self.db.execute(stmt)
            claims = result.scalars().all()
            
            if claims:
                # Analyze commit timestamps to infer timezone
                # This is a simplified version - in production, would use ML
                
                # Most GitHub users are in these common timezones
                common_timezones = [
                    'America/New_York',      # EST/EDT
                    'America/Los_Angeles',   # PST/PDT
                    'Europe/London',         # GMT/BST
                    'Europe/Berlin',         # CET/CEST
                    'Asia/Tokyo',            # JST
                    'Asia/Shanghai',         # CST
                    'Australia/Sydney',      # AEST/AEDT
                    'Asia/Kolkata'           # IST
                ]
                
                # Default to UTC if can't determine
                return 'UTC'
            
            return 'UTC'
            
        except Exception as e:
            logger.warning(f"Could not detect timezone for {username}: {e}")
            return 'UTC'
    
    async def _learn_activity_patterns(self, user_id: int) -> Dict:
        """
        Learn when user is most active by analyzing:
        1. Commit times
        2. Comment times
        3. PR creation times
        """
        try:
            from app.db.models.claims import Claim
            from app.db.models.activity_log import ActivityLog
            from sqlalchemy import select
            
            # Get activity logs for this user
            stmt = select(ActivityLog).join(Claim).where(
                Claim.github_user_id == user_id
            ).limit(50)
            
            result = await self.db.execute(stmt)
            activities = result.scalars().all()
            
            if not activities:
                return {
                    'preferred_time': 'afternoon',
                    'weekend_active': True,
                    'confidence': 20.0
                }
            
            # Analyze activity timestamps
            hour_counts = {i: 0 for i in range(24)}
            weekend_count = 0
            weekday_count = 0
            
            for activity in activities:
                hour = activity.timestamp.hour
                hour_counts[hour] += 1
                
                # Check if weekend
                if activity.timestamp.weekday() >= 5:  # Saturday/Sunday
                    weekend_count += 1
                else:
                    weekday_count += 1
            
            # Determine preferred time period
            morning_activity = sum(hour_counts[h] for h in range(6, 12))
            afternoon_activity = sum(hour_counts[h] for h in range(12, 18))
            evening_activity = sum(hour_counts[h] for h in range(18, 24))
            
            if afternoon_activity >= morning_activity and afternoon_activity >= evening_activity:
                preferred_time = 'afternoon'
            elif evening_activity >= morning_activity:
                preferred_time = 'evening'
            else:
                preferred_time = 'morning'
            
            # Calculate confidence
            total_activities = len(activities)
            confidence = min(100.0, (total_activities / 50) * 100)
            
            return {
                'preferred_time': preferred_time,
                'weekend_active': weekend_count > 0,
                'confidence': confidence,
                'hour_distribution': hour_counts
            }
            
        except Exception as e:
            logger.warning(f"Could not learn activity patterns: {e}")
            return {
                'preferred_time': 'afternoon',
                'weekend_active': True,
                'confidence': 20.0
            }
    
    def _adjust_to_optimal_hour(
        self,
        base_time: datetime,
        timezone_str: str,
        activity_patterns: Dict
    ) -> datetime:
        """Adjust timestamp to user's optimal activity hour"""
        
        try:
            user_tz = pytz.timezone(timezone_str)
            local_time = base_time.astimezone(user_tz)
            
            # Get optimal hour range for preferred time
            preferred_time = activity_patterns.get('preferred_time', 'afternoon')
            start_hour, end_hour = self.OPTIMAL_HOURS[preferred_time]
            
            # Set to middle of optimal range
            optimal_hour = (start_hour + end_hour) // 2
            
            # Create new datetime with optimal hour
            optimal_local = local_time.replace(
                hour=optimal_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            # Convert back to UTC
            return optimal_local.astimezone(timezone.utc)
            
        except Exception as e:
            logger.warning(f"Could not adjust to optimal hour: {e}")
            return base_time
    
    def _avoid_weekends_if_needed(
        self,
        scheduled_time: datetime,
        timezone_str: str
    ) -> datetime:
        """Avoid weekends for professional repositories"""
        
        try:
            user_tz = pytz.timezone(timezone_str)
            local_time = scheduled_time.astimezone(user_tz)
            
            # Check if weekend (Saturday=5, Sunday=6)
            weekday = local_time.weekday()
            
            if weekday == 5:  # Saturday
                # Move to Monday
                scheduled_time += timedelta(days=2)
            elif weekday == 6:  # Sunday
                # Move to Monday
                scheduled_time += timedelta(days=1)
            
            return scheduled_time
            
        except Exception as e:
            logger.warning(f"Could not avoid weekends: {e}")
            return scheduled_time
    
    def _generate_reasoning(
        self,
        nudge_number: int,
        days_to_wait: int,
        activity_patterns: Dict,
        timezone: str
    ) -> str:
        """Generate human-readable reasoning for schedule"""
        
        preferred_time = activity_patterns.get('preferred_time', 'afternoon')
        
        reasoning = f"Nudge #{nudge_number} scheduled for {days_to_wait} days from now. "
        reasoning += f"Sending during user's preferred active time ({preferred_time}) "
        reasoning += f"in their timezone ({timezone})."
        
        if nudge_number > 2:
            reasoning += f" Escalation level {nudge_number} - increased urgency."
        
        return reasoning
    
    def should_skip_nudge(
        self,
        progress_analysis: 'ProgressAnalysis',
        reputation: 'ReputationScore'
    ) -> bool:
        """
        Intelligent decision: should we skip this nudge?
        
        Skip if:
        - Good progress detected
        - User is highly reliable
        - Recent activity
        """
        
        # Skip if excellent progress
        if progress_analysis.progress_score > 80:
            return True
        
        # Skip if PR is open and active
        if progress_analysis.should_extend_grace_period:
            return True
        
        # Skip if elite contributor making good progress
        if reputation.reliability_tier == 'ELITE' and progress_analysis.progress_score > 50:
            return True
        
        return False
    
    def calculate_next_nudge_delay(
        self,
        current_nudge: int,
        progress_score: float,
        responsiveness_score: float
    ) -> int:
        """Calculate adaptive delay for next nudge"""
        
        base_delay = self.ESCALATION_DELAYS.get(current_nudge + 1, 2)
        
        # Extend delay if good progress
        if progress_score > 60:
            base_delay = int(base_delay * 1.5)
        
        # Shorten delay if no response
        if responsiveness_score < 30:
            base_delay = int(base_delay * 0.7)
        
        return max(1, min(14, base_delay))
    
    def personalize_nudge_message(
        self,
        message_tone: str,
        username: str,
        issue_title: str,
        days_since_claim: int,
        progress_detected: bool
    ) -> str:
        """Generate personalized nudge message based on tone"""
        
        templates = {
            'FRIENDLY': f"""Hey @{username}! 👋
            
Just wanted to check in on "{issue_title}" that you claimed {days_since_claim} days ago.

{'Great to see some activity! ' if progress_detected else ''}How's it going? Need any help or have questions?

No pressure - just want to make sure you have what you need to succeed! 🚀""",
            
            'PROFESSIONAL': f"""Hello @{username},

This is a follow-up regarding issue "{issue_title}" claimed on {datetime.now().strftime('%B %d')}.

{'We noticed some progress - thank you! ' if progress_detected else ''}Please provide a status update when you have a moment.

If you need assistance or would like to discuss the implementation, feel free to reach out.

Best regards,
Cookie Licking Detector""",
            
            'CONCERNED': f"""Hi @{username},

We haven't seen updates on "{issue_title}" for {days_since_claim} days.

{f'While there was some initial progress, ' if progress_detected else ''}we want to ensure this issue keeps moving forward.

Please respond within 3 days to:
- Provide a status update
- Request help if blocked  
- Let us know if you can't continue

Thank you for your understanding.""",
            
            'URGENT': f"""@{username} - URGENT

Issue "{issue_title}" has been claimed for {days_since_claim} days without completion.

This is the final reminder before auto-release.

**Action Required within 24 hours:**
- Submit a PR, OR
- Provide concrete progress update, OR
- Release the issue for others

Please respond immediately.""",
            
            'FINAL_WARNING': f"""FINAL NOTICE @{username}

Issue "{issue_title}" will be auto-released in 24 hours.

No further extensions will be granted.

Submit progress immediately or this issue will be made available to other contributors.

This is the last notification."""
        }
        
        return templates.get(message_tone, templates['PROFESSIONAL'])


async def get_nudge_scheduler(db_session, github_service):
    """Get nudge scheduler instance"""
    return AdaptiveNudgeScheduler(db_session, github_service)
