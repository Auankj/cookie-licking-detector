"""
Predictive Release Engine
ML-powered prediction system for optimal auto-release decisions

Features:
- Issue complexity analysis
- Completion probability prediction
- Risk assessment for early/late release
- Dynamic threshold adjustment
- Cost-benefit analysis of releasing vs waiting
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ReleaseDecision:
    """Comprehensive release recommendation"""
    should_release: bool
    confidence: float  # 0-100
    reasoning: str
    risk_level: str  # LOW, MEDIUM, HIGH
    recommended_action: str  # RELEASE, WAIT, EXTEND_GRACE
    days_to_wait: Optional[int]
    alternative_actions: List[str]
    metadata: Dict


class PredictiveReleaseEngine:
    """
    Advanced ML-based system for optimal release decisions
    Considers multiple factors to minimize false releases
    """
    
    # Issue complexity indicators
    COMPLEXITY_KEYWORDS = {
        'TRIVIAL': ['typo', 'docs', 'readme', 'comment', 'formatting'],
        'EASY': ['ui', 'css', 'style', 'text', 'label'],
        'MEDIUM': ['feature', 'add', 'implement', 'update'],
        'HARD': ['refactor', 'architecture', 'api', 'database', 'security'],
        'VERY_HARD': ['breaking change', 'migration', 'redesign', 'critical']
    }
    
    # Release thresholds by complexity
    COMPLEXITY_THRESHOLDS = {
        'TRIVIAL': {'min_days': 3, 'max_nudges': 1},
        'EASY': {'min_days': 5, 'max_nudges': 2},
        'MEDIUM': {'min_days': 7, 'max_nudges': 2},
        'HARD': {'min_days': 14, 'max_nudges': 3},
        'VERY_HARD': {'min_days': 21, 'max_nudges': 4}
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def predict_release_decision(
        self,
        claim_data: Dict,
        issue_data: Dict,
        repository_data: Dict,
        reputation_score: 'ReputationScore',
        progress_analysis: 'ProgressAnalysis'
    ) -> ReleaseDecision:
        """
        Comprehensive analysis to determine if claim should be released
        
        Considers:
        1. Issue complexity
        2. Time since claim
        3. Progress quality
        4. User reputation
        5. Repository urgency
        6. Community impact
        """
        
        logger.info(f"Analyzing release decision for claim {claim_data['id']}")
        
        # Analyze issue complexity
        complexity = self._analyze_issue_complexity(issue_data)
        
        # Calculate time factors
        days_since_claim = (datetime.now(timezone.utc) - claim_data['created_at']).days
        nudge_count = claim_data.get('nudge_count', 0)
        
        # Get complexity thresholds
        thresholds = self.COMPLEXITY_THRESHOLDS.get(complexity, self.COMPLEXITY_THRESHOLDS['MEDIUM'])
        
        # Calculate release probability
        release_prob = self._calculate_release_probability(
            claim_data=claim_data,
            complexity=complexity,
            reputation_score=reputation_score,
            progress_analysis=progress_analysis,
            days_since_claim=days_since_claim,
            nudge_count=nudge_count
        )
        
        # Assess risks of releasing vs waiting
        release_risk = self._assess_release_risk(
            progress_analysis=progress_analysis,
            reputation_score=reputation_score,
            complexity=complexity
        )
        
        # Make decision
        decision = self._make_release_decision(
            release_prob=release_prob,
            release_risk=release_risk,
            progress_analysis=progress_analysis,
            reputation_score=reputation_score,
            complexity=complexity,
            thresholds=thresholds,
            days_since_claim=days_since_claim,
            nudge_count=nudge_count
        )
        
        logger.info(
            f"Release decision for claim {claim_data['id']}: {decision['action']}",
            probability=release_prob,
            risk=release_risk
        )
        
        return decision
    
    def _analyze_issue_complexity(self, issue_data: Dict) -> str:
        """
        Analyze issue complexity from:
        1. Title keywords
        2. Description length
        3. Labels
        4. Estimated effort
        """
        
        title = issue_data.get('title', '').lower()
        description = issue_data.get('description', '')
        labels = [label.get('name', '').lower() for label in issue_data.get('labels', [])]
        
        # Check labels first
        label_complexity = None
        for label in labels:
            if 'good first issue' in label or 'beginner' in label:
                label_complexity = 'TRIVIAL'
            elif 'easy' in label:
                label_complexity = 'EASY'
            elif 'hard' in label or 'difficult' in label:
                label_complexity = 'HARD'
            elif 'critical' in label or 'blocker' in label:
                label_complexity = 'VERY_HARD'
        
        if label_complexity:
            return label_complexity
        
        # Analyze title keywords
        for complexity, keywords in self.COMPLEXITY_KEYWORDS.items():
            if any(keyword in title for keyword in keywords):
                return complexity
        
        # Analyze description length as fallback
        if description:
            desc_length = len(description)
            if desc_length < 100:
                return 'TRIVIAL'
            elif desc_length < 300:
                return 'EASY'
            elif desc_length < 800:
                return 'MEDIUM'
            elif desc_length < 1500:
                return 'HARD'
            else:
                return 'VERY_HARD'
        
        return 'MEDIUM'  # Default
    
    def _calculate_release_probability(
        self,
        claim_data: Dict,
        complexity: str,
        reputation_score: 'ReputationScore',
        progress_analysis: 'ProgressAnalysis',
        days_since_claim: int,
        nudge_count: int
    ) -> float:
        """
        Calculate probability that release is appropriate
        Higher score = more confident should release
        """
        
        base_score = 50.0
        
        # Factor 1: Time elapsed vs complexity threshold
        min_days = self.COMPLEXITY_THRESHOLDS[complexity]['min_days']
        if days_since_claim >= min_days * 1.5:
            base_score += 30
        elif days_since_claim >= min_days:
            base_score += 15
        else:
            base_score -= 20  # Too early
        
        # Factor 2: Nudge count vs threshold
        max_nudges = self.COMPLEXITY_THRESHOLDS[complexity]['max_nudges']
        if nudge_count >= max_nudges:
            base_score += 25
        elif nudge_count >= max_nudges - 1:
            base_score += 10
        
        # Factor 3: Lack of progress
        if progress_analysis.progress_score < 20:
            base_score += 20
        elif progress_analysis.progress_score < 40:
            base_score += 10
        elif progress_analysis.progress_score > 70:
            base_score -= 30  # Good progress, don't release
        
        # Factor 4: Low completion probability
        if progress_analysis.completion_probability < 30:
            base_score += 15
        elif progress_analysis.completion_probability > 70:
            base_score -= 25
        
        # Factor 5: User reputation (be lenient with good contributors)
        if reputation_score.reliability_tier in ['ELITE', 'TRUSTED']:
            base_score -= 15
        elif reputation_score.reliability_tier == 'PROBATION':
            base_score += 15
        
        # Factor 6: Stall signals
        base_score += len(progress_analysis.risk_signals) * 5
        
        return max(0.0, min(100.0, base_score))
    
    def _assess_release_risk(
        self,
        progress_analysis: 'ProgressAnalysis',
        reputation_score: 'ReputationScore',
        complexity: str
    ) -> str:
        """
        Assess risk of releasing prematurely
        LOW = safe to release
        HIGH = might regret releasing
        """
        
        risk_score = 0
        
        # Risk: Has active PR
        if progress_analysis.progress_type and 'pull_request' in progress_analysis.progress_type:
            risk_score += 30
        
        # Risk: Good contributor
        if reputation_score.reliability_tier in ['ELITE', 'TRUSTED']:
            risk_score += 20
        
        # Risk: Complex issue
        if complexity in ['HARD', 'VERY_HARD']:
            risk_score += 15
        
        # Risk: Some progress exists
        if progress_analysis.progress_score > 40:
            risk_score += 15
        
        # Risk: High completion probability
        if progress_analysis.completion_probability > 60:
            risk_score += 20
        
        if risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _make_release_decision(
        self,
        release_prob: float,
        release_risk: str,
        progress_analysis: 'ProgressAnalysis',
        reputation_score: 'ReputationScore',
        complexity: str,
        thresholds: Dict,
        days_since_claim: int,
        nudge_count: int
    ) -> ReleaseDecision:
        """Make final release decision with reasoning"""
        
        # Decision logic
        should_release = False
        action = 'WAIT'
        days_to_wait = None
        reasoning_parts = []
        alternatives = []
        
        # Strong release indicators
        if release_prob > 75 and release_risk == 'LOW':
            should_release = True
            action = 'RELEASE'
            reasoning_parts.append(f"High release probability ({release_prob:.1f}%) with low risk")
        
        # Moderate release with low risk
        elif release_prob > 60 and release_risk != 'HIGH':
            if nudge_count >= thresholds['max_nudges']:
                should_release = True
                action = 'RELEASE'
                reasoning_parts.append(f"Max nudges ({nudge_count}) reached")
            else:
                action = 'WAIT'
                days_to_wait = 3
                reasoning_parts.append("One more nudge recommended before release")
                alternatives.append('SEND_URGENT_NUDGE')
        
        # Good progress detected
        elif progress_analysis.progress_score > 60:
            action = 'EXTEND_GRACE'
            days_to_wait = 7
            reasoning_parts.append(f"Good progress detected ({progress_analysis.progress_score:.1f}%)")
            alternatives.append('MONITOR_CLOSELY')
        
        # Elite contributor with some progress
        elif reputation_score.reliability_tier == 'ELITE' and progress_analysis.progress_score > 30:
            action = 'EXTEND_GRACE'
            days_to_wait = 5
            reasoning_parts.append("Elite contributor showing progress")
            alternatives.append('SEND_FRIENDLY_CHECK_IN')
        
        # High risk of false release
        elif release_risk == 'HIGH':
            action = 'WAIT'
            days_to_wait = 5
            reasoning_parts.append(f"High risk of premature release - {release_risk}")
            alternatives.extend(['REQUEST_STATUS_UPDATE', 'MAINTAINER_REVIEW'])
        
        # Default: not enough evidence either way
        else:
            if days_since_claim >= thresholds['min_days'] * 2:
                should_release = True
                action = 'RELEASE'
                reasoning_parts.append(f"Exceeded 2x minimum days ({days_since_claim} vs {thresholds['min_days']})")
            else:
                action = 'WAIT'
                days_to_wait = thresholds['min_days'] - days_since_claim
                reasoning_parts.append("Waiting for minimum threshold")
        
        # Add context to reasoning
        reasoning_parts.append(f"Issue complexity: {complexity}")
        reasoning_parts.append(f"Reputation tier: {reputation_score.reliability_tier}")
        
        if progress_analysis.risk_signals:
            reasoning_parts.append(f"Risk signals: {', '.join(progress_analysis.risk_signals[:3])}")
        
        reasoning = ". ".join(reasoning_parts)
        
        return ReleaseDecision(
            should_release=should_release,
            confidence=release_prob,
            reasoning=reasoning,
            risk_level=release_risk,
            recommended_action=action,
            days_to_wait=days_to_wait,
            alternative_actions=alternatives,
            metadata={
                'complexity': complexity,
                'release_probability': release_prob,
                'days_since_claim': days_since_claim,
                'nudge_count': nudge_count,
                'progress_score': progress_analysis.progress_score,
                'completion_probability': progress_analysis.completion_probability
            }
        )
    
    def calculate_community_impact(
        self,
        issue_data: Dict,
        repository_data: Dict
    ) -> float:
        """
        Calculate impact on community if issue stays claimed
        Higher score = more urgent to release
        """
        
        impact_score = 50.0
        
        # Check if issue is blocking others
        labels = [label.get('name', '').lower() for label in issue_data.get('labels', [])]
        if any(label in ['blocker', 'critical', 'high priority'] for label in labels):
            impact_score += 30
        
        # Check number of watchers/subscribers
        watchers = issue_data.get('watchers', 0)
        if watchers > 10:
            impact_score += 20
        elif watchers > 5:
            impact_score += 10
        
        # Check comment activity from others
        comments = issue_data.get('comments', 0)
        if comments > 15:
            impact_score += 15
        elif comments > 8:
            impact_score += 8
        
        return min(100.0, impact_score)


async def get_release_predictor(db_session):
    """Get release predictor instance"""
    return PredictiveReleaseEngine(db_session)
