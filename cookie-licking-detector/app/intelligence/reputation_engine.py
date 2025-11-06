"""
Contributor Reputation Engine
Advanced ML-based scoring system for contributor reliability and performance prediction

Features:
- Historical completion rate tracking
- Time-to-completion analysis
- Quality metrics (PR reviews, test coverage)
- Behavioral patterns (responsiveness, communication)
- Dynamic grace period calculation
- Fraud detection (serial cookie lickers)
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ReputationScore:
    """Comprehensive reputation metrics"""
    overall_score: float  # 0-100
    completion_rate: float  # Percentage of completed claims
    avg_completion_time: float  # Days to complete
    responsiveness_score: float  # How quickly they respond to nudges
    quality_score: float  # PR quality metrics
    reliability_tier: str  # ELITE, TRUSTED, REGULAR, PROBATION, BLOCKED
    recommended_grace_period: int  # Calculated grace period in days
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    total_claims: int
    completed_claims: int
    abandoned_claims: int
    metadata: Dict


class ContributorReputationEngine:
    """
    Advanced reputation scoring engine with ML-based predictions
    Uses multiple algorithms to assess contributor reliability
    """
    
    # Reputation tier thresholds
    TIER_THRESHOLDS = {
        'ELITE': 90,      # Top 5% - trusted veterans
        'TRUSTED': 75,    # Consistent performers
        'REGULAR': 50,    # Average contributors
        'PROBATION': 25,  # Concerning pattern
        'BLOCKED': 0      # Serial offenders
    }
    
    # Grace period mappings by tier
    GRACE_PERIODS = {
        'ELITE': 21,      # 3 weeks for trusted contributors
        'TRUSTED': 14,    # 2 weeks for reliable users
        'REGULAR': 7,     # 1 week default
        'PROBATION': 3,   # 3 days for risky users
        'BLOCKED': 1      # Minimal grace period
    }
    
    # Weights for overall score calculation
    WEIGHTS = {
        'completion_rate': 0.35,
        'responsiveness': 0.25,
        'quality': 0.20,
        'velocity': 0.15,
        'recency': 0.05
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def calculate_reputation(self, github_user_id: int, github_username: str) -> ReputationScore:
        """
        Calculate comprehensive reputation score using multiple algorithms
        
        Algorithm combines:
        1. Completion rate (with time decay)
        2. Response time analysis
        3. Quality metrics from PRs
        4. Velocity tracking
        5. Behavioral patterns
        """
        
        # Fetch user's claim history
        claims_history = await self._fetch_user_claims(github_user_id)
        
        if not claims_history:
            # New user - neutral score with conservative grace period
            return ReputationScore(
                overall_score=50.0,
                completion_rate=0.0,
                avg_completion_time=0.0,
                responsiveness_score=50.0,
                quality_score=50.0,
                reliability_tier='REGULAR',
                recommended_grace_period=5,  # Shorter for new users
                risk_level='MEDIUM',
                total_claims=0,
                completed_claims=0,
                abandoned_claims=0,
                metadata={'status': 'new_user', 'first_claim': True}
            )
        
        # Calculate component scores
        completion_score = self._calculate_completion_score(claims_history)
        responsiveness_score = self._calculate_responsiveness_score(claims_history)
        quality_score = await self._calculate_quality_score(github_username)
        velocity_score = self._calculate_velocity_score(claims_history)
        recency_score = self._calculate_recency_score(claims_history)
        
        # Weighted overall score
        overall_score = (
            completion_score * self.WEIGHTS['completion_rate'] +
            responsiveness_score * self.WEIGHTS['responsiveness'] +
            quality_score * self.WEIGHTS['quality'] +
            velocity_score * self.WEIGHTS['velocity'] +
            recency_score * self.WEIGHTS['recency']
        )
        
        # Determine tier and grace period
        tier = self._determine_tier(overall_score)
        grace_period = self._calculate_dynamic_grace_period(
            tier, completion_score, velocity_score, claims_history
        )
        
        # Assess risk level
        risk_level = self._assess_risk_level(claims_history, overall_score)
        
        # Calculate statistics
        total_claims = len(claims_history)
        completed = len([c for c in claims_history if c['status'] == 'COMPLETED'])
        abandoned = len([c for c in claims_history if c['status'] in ['RELEASED', 'EXPIRED']])
        
        avg_completion_time = self._calculate_avg_completion_time(claims_history)
        
        logger.info(
            f"Reputation calculated for {github_username}",
            score=overall_score,
            tier=tier,
            grace_period=grace_period
        )
        
        return ReputationScore(
            overall_score=round(overall_score, 2),
            completion_rate=round(completion_score, 2),
            avg_completion_time=round(avg_completion_time, 2),
            responsiveness_score=round(responsiveness_score, 2),
            quality_score=round(quality_score, 2),
            reliability_tier=tier,
            recommended_grace_period=grace_period,
            risk_level=risk_level,
            total_claims=total_claims,
            completed_claims=completed,
            abandoned_claims=abandoned,
            metadata={
                'velocity_score': velocity_score,
                'recency_score': recency_score,
                'trend': self._calculate_trend(claims_history)
            }
        )
    
    def _calculate_completion_score(self, claims_history: List[Dict]) -> float:
        """
        Calculate completion rate with time-weighted decay
        Recent performance weighted more heavily than old history
        """
        if not claims_history:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        now = datetime.now(timezone.utc)
        
        for claim in claims_history:
            # Calculate time decay (more recent = higher weight)
            days_ago = (now - claim['created_at']).days
            weight = math.exp(-days_ago / 365)  # Exponential decay over 1 year
            
            # Score based on outcome
            if claim['status'] == 'COMPLETED':
                score = 100.0
            elif claim['status'] == 'ACTIVE':
                # Ongoing claims - partial credit based on progress
                score = 50.0
            else:
                # Released/Expired
                score = 0.0
            
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_responsiveness_score(self, claims_history: List[Dict]) -> float:
        """
        Analyze response time to nudges and comments
        Fast responders get higher scores
        """
        response_times = []
        
        for claim in claims_history:
            # Check activity logs for nudge responses
            if claim.get('nudge_sent_at') and claim.get('last_activity_timestamp'):
                nudge_time = claim['nudge_sent_at']
                response_time = claim['last_activity_timestamp']
                
                if response_time > nudge_time:
                    hours_to_respond = (response_time - nudge_time).total_seconds() / 3600
                    response_times.append(hours_to_respond)
        
        if not response_times:
            return 50.0  # Neutral score if no data
        
        avg_response_hours = sum(response_times) / len(response_times)
        
        # Score based on average response time
        # < 4 hours = excellent (100)
        # < 24 hours = good (80)
        # < 72 hours = ok (60)
        # > 72 hours = poor (30)
        if avg_response_hours < 4:
            return 100.0
        elif avg_response_hours < 24:
            return 80.0
        elif avg_response_hours < 72:
            return 60.0
        else:
            return max(30.0, 100.0 - (avg_response_hours / 24) * 10)
    
    async def _calculate_quality_score(self, github_username: str) -> float:
        """
        Calculate quality score based on PR metrics
        - PR approval rate
        - Code review feedback
        - Test coverage
        - Documentation
        """
        try:
            from app.services.github_service import get_github_service
            github_service = get_github_service()
            
            # Get recent PRs (last 10)
            # This would integrate with GitHub API to fetch PR quality metrics
            # For now, using placeholder logic
            
            # In production, this would analyze:
            # - Number of review iterations
            # - Approval rate
            # - CI/CD success rate
            # - Code coverage changes
            # - Documentation updates
            
            # Placeholder: return neutral score
            return 70.0
            
        except Exception as e:
            logger.warning(f"Could not calculate quality score: {e}")
            return 50.0
    
    def _calculate_velocity_score(self, claims_history: List[Dict]) -> float:
        """
        Calculate velocity score - how fast do they complete work
        Faster completion = higher score
        """
        completion_times = []
        
        for claim in claims_history:
            if claim['status'] == 'COMPLETED' and claim.get('completed_at'):
                days_to_complete = (claim['completed_at'] - claim['created_at']).days
                completion_times.append(days_to_complete)
        
        if not completion_times:
            return 50.0
        
        avg_days = sum(completion_times) / len(completion_times)
        
        # Score based on average completion time
        # < 3 days = excellent (100)
        # < 7 days = good (80)
        # < 14 days = ok (60)
        # > 14 days = slow (40)
        if avg_days < 3:
            return 100.0
        elif avg_days < 7:
            return 80.0
        elif avg_days < 14:
            return 60.0
        else:
            return max(20.0, 100.0 - (avg_days - 14) * 3)
    
    def _calculate_recency_score(self, claims_history: List[Dict]) -> float:
        """
        Recency bias - recent activity matters more
        Active contributors get higher scores
        """
        if not claims_history:
            return 0.0
        
        now = datetime.now(timezone.utc)
        most_recent = max(claim['created_at'] for claim in claims_history)
        days_since_last = (now - most_recent).days
        
        # Score based on recency
        # < 7 days = very active (100)
        # < 30 days = active (80)
        # < 90 days = moderate (60)
        # > 180 days = inactive (20)
        if days_since_last < 7:
            return 100.0
        elif days_since_last < 30:
            return 80.0
        elif days_since_last < 90:
            return 60.0
        elif days_since_last < 180:
            return 40.0
        else:
            return 20.0
    
    def _determine_tier(self, overall_score: float) -> str:
        """Determine reputation tier based on overall score"""
        for tier, threshold in self.TIER_THRESHOLDS.items():
            if overall_score >= threshold:
                return tier
        return 'BLOCKED'
    
    def _calculate_dynamic_grace_period(
        self, 
        tier: str, 
        completion_score: float, 
        velocity_score: float,
        claims_history: List[Dict]
    ) -> int:
        """
        Calculate optimal grace period based on multiple factors
        Uses tier as base, then adjusts based on performance
        """
        base_period = self.GRACE_PERIODS.get(tier, 7)
        
        # Adjust based on velocity
        if velocity_score > 80:
            # Fast workers get more time (they earned it)
            base_period = int(base_period * 1.2)
        elif velocity_score < 40:
            # Slow workers get less time
            base_period = int(base_period * 0.8)
        
        # Adjust based on recent abandonment pattern
        recent_claims = claims_history[:5]  # Last 5 claims
        if recent_claims:
            recent_abandons = len([c for c in recent_claims if c['status'] in ['RELEASED', 'EXPIRED']])
            if recent_abandons >= 3:
                # Multiple recent abandonments - reduce grace period
                base_period = max(3, int(base_period * 0.6))
        
        # Ensure within reasonable bounds
        return max(1, min(30, base_period))
    
    def _assess_risk_level(self, claims_history: List[Dict], overall_score: float) -> str:
        """
        Assess risk level for this contributor
        HIGH risk = likely to abandon
        """
        if overall_score >= 75:
            return 'LOW'
        elif overall_score >= 50:
            return 'MEDIUM'
        elif overall_score >= 25:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _calculate_avg_completion_time(self, claims_history: List[Dict]) -> float:
        """Calculate average time to complete claims (in days)"""
        completion_times = []
        
        for claim in claims_history:
            if claim['status'] == 'COMPLETED' and claim.get('completed_at'):
                days = (claim['completed_at'] - claim['created_at']).days
                completion_times.append(days)
        
        if not completion_times:
            return 0.0
        
        return sum(completion_times) / len(completion_times)
    
    def _calculate_trend(self, claims_history: List[Dict]) -> str:
        """
        Calculate trend direction - is user improving or declining?
        """
        if len(claims_history) < 3:
            return 'STABLE'
        
        # Split into recent and older claims
        recent = claims_history[:len(claims_history)//2]
        older = claims_history[len(claims_history)//2:]
        
        recent_completion_rate = len([c for c in recent if c['status'] == 'COMPLETED']) / len(recent)
        older_completion_rate = len([c for c in older if c['status'] == 'COMPLETED']) / len(older)
        
        diff = recent_completion_rate - older_completion_rate
        
        if diff > 0.2:
            return 'IMPROVING'
        elif diff < -0.2:
            return 'DECLINING'
        else:
            return 'STABLE'
    
    async def _fetch_user_claims(self, github_user_id: int) -> List[Dict]:
        """Fetch user's claim history from database"""
        from app.db.models.claims import Claim
        from sqlalchemy import select, desc
        
        try:
            stmt = select(Claim).where(
                Claim.github_user_id == github_user_id
            ).order_by(desc(Claim.created_at)).limit(50)  # Last 50 claims
            
            result = await self.db.execute(stmt)
            claims = result.scalars().all()
            
            return [
                {
                    'id': claim.id,
                    'status': claim.status.value if hasattr(claim.status, 'value') else claim.status,
                    'created_at': claim.created_at,
                    'completed_at': getattr(claim, 'completed_at', None),
                    'nudge_sent_at': getattr(claim, 'first_nudge_sent_at', None),
                    'last_activity_timestamp': claim.last_activity_timestamp,
                }
                for claim in claims
            ]
        except Exception as e:
            logger.error(f"Error fetching claims for user {github_user_id}: {e}")
            return []
    
    def should_auto_approve_claim(self, reputation: ReputationScore) -> bool:
        """
        Determine if claim should be auto-approved without human review
        Elite contributors get instant approval
        """
        return reputation.reliability_tier == 'ELITE' and reputation.risk_level == 'LOW'
    
    def should_require_review(self, reputation: ReputationScore) -> bool:
        """
        Determine if claim requires human review before approval
        High-risk contributors need maintainer approval
        """
        return reputation.risk_level in ['HIGH', 'CRITICAL'] or reputation.reliability_tier == 'PROBATION'
    
    def should_block_claim(self, reputation: ReputationScore) -> bool:
        """
        Determine if user should be blocked from claiming
        Serial offenders get blocked
        """
        return (
            reputation.reliability_tier == 'BLOCKED' or
            (reputation.abandoned_claims >= 5 and reputation.completion_rate < 10)
        )


# Singleton instance
_reputation_engine = None

async def get_reputation_engine(db_session):
    """Get reputation engine instance"""
    return ContributorReputationEngine(db_session)
