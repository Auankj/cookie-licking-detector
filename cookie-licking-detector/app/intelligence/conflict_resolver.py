"""
Claim Conflict Resolver
Intelligent resolution system for competing claims

Features:
- Priority scoring for multiple claimers
- Skill matching (user experience vs issue needs)
- Fair assignment algorithms
- Collaboration matching
- Time-based priority
- Contribution diversity optimization
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ConflictResolution:
    """Conflict resolution recommendation"""
    winner: Optional[str]  # GitHub username
    resolution_strategy: str
    reasoning: str
    priority_scores: Dict[str, float]
    should_allow_both: bool  # For team claims
    recommended_split: Optional[List[Dict]]  # How to split work
    confidence: float
    metadata: Dict


class ClaimConflictResolver:
    """
    Advanced conflict resolution using priority scoring
    Optimizes for fairness, skill match, and community health
    """
    
    # Priority weights
    PRIORITY_WEIGHTS = {
        'reputation_score': 0.25,
        'skill_match': 0.20,
        'response_speed': 0.15,
        'contribution_history': 0.15,
        'time_priority': 0.10,
        'maintainer_preference': 0.10,
        'diversity_factor': 0.05
    }
    
    # Resolution strategies
    STRATEGIES = {
        'FIRST_COME': 'First claimer gets priority',
        'SKILL_MATCH': 'Best skill match wins',
        'REPUTATION': 'Higher reputation wins',
        'TEAM_CLAIM': 'Allow both as team',
        'SPLIT_WORK': 'Split into subtasks',
        'MAINTAINER_CHOICE': 'Let maintainer decide'
    }
    
    def __init__(self, db_session, reputation_engine):
        self.db = db_session
        self.reputation_engine = reputation_engine
    
    async def resolve_conflict(
        self,
        issue_data: Dict,
        repository_data: Dict,
        existing_claim: Dict,
        new_claimer: Dict,
        new_claim_text: str
    ) -> ConflictResolution:
        """
        Resolve conflict between existing and new claimer
        
        Analyzes:
        1. Reputation of both users
        2. Skill match with issue
        3. Response time
        4. Contribution history in repo
        5. Team collaboration potential
        """
        
        logger.info(
            f"Resolving conflict for issue #{issue_data['github_issue_number']}",
            existing=existing_claim['github_username'],
            new=new_claimer['username']
        )
        
        # Get reputation scores
        existing_reputation = await self.reputation_engine.calculate_reputation(
            existing_claim['github_user_id'],
            existing_claim['github_username']
        )
        
        new_reputation = await self.reputation_engine.calculate_reputation(
            new_claimer['user_id'],
            new_claimer['username']
        )
        
        # Calculate priority scores for each claimer
        existing_score = await self._calculate_priority_score(
            user_id=existing_claim['github_user_id'],
            username=existing_claim['github_username'],
            reputation=existing_reputation,
            claim_data=existing_claim,
            issue_data=issue_data,
            repository_data=repository_data,
            is_existing=True
        )
        
        new_score = await self._calculate_priority_score(
            user_id=new_claimer['user_id'],
            username=new_claimer['username'],
            reputation=new_reputation,
            claim_data={'claim_text': new_claim_text, 'created_at': datetime.now(timezone.utc)},
            issue_data=issue_data,
            repository_data=repository_data,
            is_existing=False
        )
        
        # Check if team collaboration is possible
        is_collaboration = self._detect_collaboration_intent(
            existing_claim['claim_text'],
            new_claim_text
        )
        
        # Determine resolution strategy
        resolution = self._determine_resolution_strategy(
            existing_score=existing_score,
            new_score=new_score,
            existing_reputation=existing_reputation,
            new_reputation=new_reputation,
            is_collaboration=is_collaboration,
            issue_data=issue_data
        )
        
        logger.info(
            f"Conflict resolution: {resolution['strategy']}",
            existing_score=existing_score,
            new_score=new_score
        )
        
        return resolution
    
    async def _calculate_priority_score(
        self,
        user_id: int,
        username: str,
        reputation: 'ReputationScore',
        claim_data: Dict,
        issue_data: Dict,
        repository_data: Dict,
        is_existing: bool
    ) -> float:
        """Calculate comprehensive priority score (0-100)"""
        
        score = 0.0
        
        # Component 1: Reputation (25%)
        reputation_component = (
            reputation.overall_score * self.PRIORITY_WEIGHTS['reputation_score']
        )
        score += reputation_component
        
        # Component 2: Skill match (20%)
        skill_match = await self._calculate_skill_match(
            username=username,
            issue_data=issue_data,
            repository_data=repository_data
        )
        skill_component = skill_match * self.PRIORITY_WEIGHTS['skill_match']
        score += skill_component
        
        # Component 3: Response speed (15%)
        if is_existing:
            # Existing claimer gets full response points
            response_component = 100 * self.PRIORITY_WEIGHTS['response_speed']
        else:
            # New claimer gets points based on how quickly they responded
            response_component = 70 * self.PRIORITY_WEIGHTS['response_speed']
        score += response_component
        
        # Component 4: Contribution history in this repo (15%)
        contribution_history = await self._get_repo_contribution_score(
            username=username,
            repository_data=repository_data
        )
        contribution_component = contribution_history * self.PRIORITY_WEIGHTS['contribution_history']
        score += contribution_component
        
        # Component 5: Time priority (10%)
        if is_existing:
            time_component = 100 * self.PRIORITY_WEIGHTS['time_priority']
        else:
            time_component = 50 * self.PRIORITY_WEIGHTS['time_priority']
        score += time_component
        
        # Component 6: Maintainer status (10%)
        is_maintainer = await self._is_maintainer(username, repository_data)
        if is_maintainer:
            maintainer_component = 100 * self.PRIORITY_WEIGHTS['maintainer_preference']
        else:
            maintainer_component = 50 * self.PRIORITY_WEIGHTS['maintainer_preference']
        score += maintainer_component
        
        # Component 7: Diversity factor (5%)
        # Encourage new contributors
        if reputation.total_claims < 3:
            diversity_component = 80 * self.PRIORITY_WEIGHTS['diversity_factor']
        else:
            diversity_component = 50 * self.PRIORITY_WEIGHTS['diversity_factor']
        score += diversity_component
        
        return min(100.0, max(0.0, score))
    
    async def _calculate_skill_match(
        self,
        username: str,
        issue_data: Dict,
        repository_data: Dict
    ) -> float:
        """
        Calculate how well user's skills match issue requirements
        Analyzes past contributions to similar issues
        """
        
        # This would use ML to match user's past work with issue requirements
        # For now, using simplified logic
        
        try:
            # Check if user has experience with similar labels
            issue_labels = {label['name'].lower() for label in issue_data.get('labels', [])}
            
            # Get user's past issues (would query from database)
            # For now, return moderate score
            
            return 70.0
            
        except Exception as e:
            logger.warning(f"Could not calculate skill match: {e}")
            return 50.0
    
    async def _get_repo_contribution_score(
        self,
        username: str,
        repository_data: Dict
    ) -> float:
        """
        Score based on user's past contributions to this specific repo
        Higher score for established contributors
        """
        
        try:
            from app.db.models.claims import Claim
            from sqlalchemy import select, func
            
            # Count completed claims in this repo
            stmt = select(func.count(Claim.id)).where(
                Claim.github_username == username,
                Claim.repository_id == repository_data.get('id'),
                Claim.status == 'COMPLETED'
            )
            
            result = await self.db.execute(stmt)
            completed_count = result.scalar() or 0
            
            # Score: 10 points per completed claim, max 100
            return min(100.0, completed_count * 10)
            
        except Exception as e:
            logger.warning(f"Could not get contribution score: {e}")
            return 0.0
    
    async def _is_maintainer(self, username: str, repository_data: Dict) -> bool:
        """Check if user is a maintainer of the repository"""
        
        # This would check GitHub permissions
        # For now, simplified check
        
        maintainers = repository_data.get('maintainers', [])
        return username.lower() in [m.lower() for m in maintainers]
    
    def _detect_collaboration_intent(
        self,
        existing_text: str,
        new_text: str
    ) -> bool:
        """Detect if new claimer wants to collaborate, not compete"""
        
        collaboration_phrases = [
            'help', 'assist', 'collaborate', 'together', 'team up',
            'work with', 'join', 'contribute to', 'part of'
        ]
        
        new_text_lower = new_text.lower()
        
        # Check if new claimer mentions the existing claimer
        if '@' in new_text:
            return True
        
        # Check for collaboration keywords
        for phrase in collaboration_phrases:
            if phrase in new_text_lower:
                return True
        
        return False
    
    def _determine_resolution_strategy(
        self,
        existing_score: float,
        new_score: float,
        existing_reputation: 'ReputationScore',
        new_reputation: 'ReputationScore',
        is_collaboration: bool,
        issue_data: Dict
    ) -> ConflictResolution:
        """Determine optimal resolution strategy"""
        
        priority_scores = {
            'existing': existing_score,
            'new': new_score
        }
        
        # Strategy 1: Collaboration detected
        if is_collaboration:
            return ConflictResolution(
                winner=None,
                resolution_strategy='TEAM_CLAIM',
                reasoning="New claimer expressed intent to collaborate. Recommend allowing team claim.",
                priority_scores=priority_scores,
                should_allow_both=True,
                recommended_split=self._suggest_work_split(issue_data),
                confidence=85.0,
                metadata={'collaboration_detected': True}
            )
        
        # Strategy 2: Clear winner by significant margin
        score_difference = abs(existing_score - new_score)
        if score_difference > 20:
            winner = 'existing' if existing_score > new_score else 'new'
            winner_username = (
                existing_reputation.metadata.get('username', 'existing')
                if winner == 'existing'
                else new_reputation.metadata.get('username', 'new')
            )
            
            return ConflictResolution(
                winner=winner,
                resolution_strategy='PRIORITY_SCORE',
                reasoning=f"Clear winner based on priority scoring. {winner} scored {max(existing_score, new_score):.1f} vs {min(existing_score, new_score):.1f}",
                priority_scores=priority_scores,
                should_allow_both=False,
                recommended_split=None,
                confidence=90.0,
                metadata={'score_difference': score_difference}
            )
        
        # Strategy 3: Both are elite - maintainer decides
        if (existing_reputation.reliability_tier == 'ELITE' and 
            new_reputation.reliability_tier == 'ELITE'):
            return ConflictResolution(
                winner=None,
                resolution_strategy='MAINTAINER_CHOICE',
                reasoning="Both claimers are elite contributors. Recommend maintainer makes final decision.",
                priority_scores=priority_scores,
                should_allow_both=False,
                recommended_split=None,
                confidence=75.0,
                metadata={'both_elite': True}
            )
        
        # Strategy 4: Complex issue - consider splitting
        complexity = self._assess_issue_complexity(issue_data)
        if complexity in ['HARD', 'VERY_HARD'] and existing_score > 60 and new_score > 60:
            return ConflictResolution(
                winner=None,
                resolution_strategy='SPLIT_WORK',
                reasoning=f"Complex issue ({complexity}) with two qualified contributors. Recommend splitting work.",
                priority_scores=priority_scores,
                should_allow_both=True,
                recommended_split=self._suggest_work_split(issue_data),
                confidence=70.0,
                metadata={'complexity': complexity}
            )
        
        # Strategy 5: First come first served (small difference)
        return ConflictResolution(
            winner='existing',
            resolution_strategy='FIRST_COME',
            reasoning=f"Similar qualifications (scores within 20 points). First claimer gets priority.",
            priority_scores=priority_scores,
            should_allow_both=False,
            recommended_split=None,
            confidence=65.0,
            metadata={'close_scores': True}
        )
    
    def _assess_issue_complexity(self, issue_data: Dict) -> str:
        """Assess issue complexity for split decisions"""
        
        # Check labels
        labels = {label['name'].lower() for label in issue_data.get('labels', [])}
        
        if any(label in ['blocker', 'critical'] for label in labels):
            return 'VERY_HARD'
        elif any(label in ['enhancement', 'feature'] for label in labels):
            return 'HARD'
        elif any(label in ['bug', 'improvement'] for label in labels):
            return 'MEDIUM'
        elif any(label in ['good first issue', 'documentation'] for label in labels):
            return 'EASY'
        
        # Check description length
        desc_length = len(issue_data.get('description', ''))
        if desc_length > 1000:
            return 'HARD'
        elif desc_length > 500:
            return 'MEDIUM'
        
        return 'MEDIUM'
    
    def _suggest_work_split(self, issue_data: Dict) -> List[Dict]:
        """Suggest how to split work between multiple contributors"""
        
        # This would use NLP to analyze issue and suggest subtasks
        # For now, generic suggestions
        
        return [
            {
                'task': 'Implementation',
                'description': 'Core functionality implementation',
                'estimated_effort': 'HIGH'
            },
            {
                'task': 'Testing',
                'description': 'Write comprehensive tests',
                'estimated_effort': 'MEDIUM'
            },
            {
                'task': 'Documentation',
                'description': 'Update documentation and examples',
                'estimated_effort': 'LOW'
            }
        ]


async def get_conflict_resolver(db_session, reputation_engine):
    """Get conflict resolver instance"""
    return ClaimConflictResolver(db_session, reputation_engine)
