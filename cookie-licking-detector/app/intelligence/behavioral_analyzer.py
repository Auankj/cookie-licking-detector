"""
Behavioral Analyzer
Advanced pattern detection for fraud prevention and collaboration intelligence

Features:
- Anomaly detection (suspicious patterns)
- Serial cookie licker identification
- Team collaboration detection
- Bot/automation detection
- Gaming the system detection
- Genuine contribution validation
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BehavioralAnalysis:
    """Behavioral pattern assessment"""
    is_suspicious: bool
    anomalies: List[str]
    fraud_score: float  # 0-100, higher = more suspicious
    behavior_type: str  # GENUINE, COLLABORATIVE, SUSPICIOUS, FRAUDULENT
    is_bot: bool
    is_team_claim: bool
    recommended_actions: List[str]
    confidence: float
    metadata: Dict


class BehavioralAnalyzer:
    """
    Advanced behavioral analysis for fraud detection and collaboration
    Uses pattern recognition to identify suspicious behavior
    """
    
    # Anomaly thresholds
    ANOMALY_THRESHOLDS = {
        'rapid_claiming': 5,  # > 5 claims in 1 hour
        'claim_hoarding': 10,  # > 10 active claims simultaneously
        'serial_abandonment': 5,  # > 5 abandoned in a row
        'velocity_spike': 10,  # 10x normal activity
        'identical_patterns': 0.9  # 90% similarity in messages
    }
    
    # Bot indicators
    BOT_PATTERNS = [
        r'\[bot\]',
        r'automated',
        r'github-actions',
        r'dependabot',
        r'renovate'
    ]
    
    # Collaboration keywords
    COLLABORATION_KEYWORDS = [
        'team', 'together', 'pair', 'collaborate',
        'we can', 'let\'s', 'help with', 'part of'
    ]
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def analyze_claim_behavior(
        self,
        github_user_id: int,
        github_username: str,
        claim_text: str,
        issue_data: Dict,
        claim_history: List[Dict]
    ) -> BehavioralAnalysis:
        """
        Comprehensive behavioral analysis
        Detects fraud, bots, and collaboration patterns
        """
        
        logger.info(f"Analyzing behavior for user {github_username}")
        
        anomalies = []
        fraud_score = 0.0
        
        # Check for rapid claiming
        rapid_claim_score = await self._detect_rapid_claiming(github_user_id)
        if rapid_claim_score > 0:
            anomalies.append(f"Rapid claiming detected ({rapid_claim_score} claims/hour)")
            fraud_score += 20
        
        # Check for claim hoarding
        active_claims = await self._count_active_claims(github_user_id)
        if active_claims > self.ANOMALY_THRESHOLDS['claim_hoarding']:
            anomalies.append(f"Claim hoarding ({active_claims} active claims)")
            fraud_score += 25
        
        # Check for serial abandonment
        abandonment_rate = self._calculate_abandonment_rate(claim_history)
        if abandonment_rate > 0.7:  # 70% abandonment rate
            anomalies.append(f"High abandonment rate ({abandonment_rate*100:.1f}%)")
            fraud_score += 30
        
        # Check for velocity anomalies
        velocity_anomaly = self._detect_velocity_anomaly(claim_history)
        if velocity_anomaly:
            anomalies.append("Suspicious activity velocity spike")
            fraud_score += 15
        
        # Check for copy-paste behavior
        similarity_score = await self._detect_identical_patterns(github_user_id, claim_text)
        if similarity_score > self.ANOMALY_THRESHOLDS['identical_patterns']:
            anomalies.append("Repeated identical claim messages")
            fraud_score += 20
        
        # Check if bot
        is_bot = self._is_bot_account(github_username, claim_text)
        if is_bot:
            anomalies.append("Bot account detected")
        
        # Check for team collaboration
        is_team_claim = self._detect_team_collaboration(claim_text, issue_data)
        
        # Check for gaming patterns
        gaming_detected = self._detect_gaming_patterns(claim_history)
        if gaming_detected:
            anomalies.append("Gaming the system detected")
            fraud_score += 25
        
        # Determine behavior type
        behavior_type = self._classify_behavior(
            fraud_score=fraud_score,
            is_bot=is_bot,
            is_team=is_team_claim,
            abandonment_rate=abandonment_rate
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            fraud_score=fraud_score,
            anomalies=anomalies,
            is_bot=is_bot,
            behavior_type=behavior_type
        )
        
        # Calculate confidence
        confidence = min(100.0, len(claim_history) * 10)  # More history = more confidence
        
        logger.info(
            f"Behavioral analysis complete for {github_username}",
            fraud_score=fraud_score,
            behavior_type=behavior_type,
            anomalies=len(anomalies)
        )
        
        return BehavioralAnalysis(
            is_suspicious=fraud_score > 50,
            anomalies=anomalies,
            fraud_score=round(fraud_score, 2),
            behavior_type=behavior_type,
            is_bot=is_bot,
            is_team_claim=is_team_claim,
            recommended_actions=recommendations,
            confidence=round(confidence, 2),
            metadata={
                'active_claims': active_claims,
                'abandonment_rate': round(abandonment_rate, 2),
                'similarity_score': round(similarity_score, 2),
                'rapid_claim_score': rapid_claim_score
            }
        )
    
    async def _detect_rapid_claiming(self, user_id: int) -> float:
        """Detect if user is claiming issues too rapidly"""
        
        try:
            from app.db.models.claims import Claim
            from sqlalchemy import select, func
            
            # Check claims in last hour
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            
            stmt = select(func.count(Claim.id)).where(
                Claim.github_user_id == user_id,
                Claim.created_at >= one_hour_ago
            )
            
            result = await self.db.execute(stmt)
            claims_last_hour = result.scalar() or 0
            
            return claims_last_hour
            
        except Exception as e:
            logger.warning(f"Could not detect rapid claiming: {e}")
            return 0
    
    async def _count_active_claims(self, user_id: int) -> int:
        """Count currently active claims"""
        
        try:
            from app.db.models.claims import Claim, ClaimStatus
            from sqlalchemy import select, func
            
            stmt = select(func.count(Claim.id)).where(
                Claim.github_user_id == user_id,
                Claim.status == ClaimStatus.ACTIVE
            )
            
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            logger.warning(f"Could not count active claims: {e}")
            return 0
    
    def _calculate_abandonment_rate(self, claim_history: List[Dict]) -> float:
        """Calculate percentage of abandoned claims"""
        
        if not claim_history:
            return 0.0
        
        abandoned = len([
            c for c in claim_history
            if c.get('status') in ['RELEASED', 'EXPIRED', 'AUTO_RELEASED']
        ])
        
        return abandoned / len(claim_history)
    
    def _detect_velocity_anomaly(self, claim_history: List[Dict]) -> bool:
        """Detect sudden spikes in activity (possible automation)"""
        
        if len(claim_history) < 10:
            return False
        
        # Calculate recent vs historical velocity
        recent = claim_history[:5]
        historical = claim_history[5:]
        
        if not recent or not historical:
            return False
        
        # Calculate time spans
        recent_span = (recent[0]['created_at'] - recent[-1]['created_at']).days or 1
        historical_span = (historical[0]['created_at'] - historical[-1]['created_at']).days or 1
        
        recent_velocity = len(recent) / recent_span
        historical_velocity = len(historical) / historical_span
        
        # Check for 10x spike
        if recent_velocity > historical_velocity * self.ANOMALY_THRESHOLDS['velocity_spike']:
            return True
        
        return False
    
    async def _detect_identical_patterns(self, user_id: int, current_text: str) -> float:
        """Detect if user copy-pastes same claim message"""
        
        try:
            from app.db.models.claims import Claim
            from sqlalchemy import select
            
            # Get recent claims
            stmt = select(Claim.claim_text).where(
                Claim.github_user_id == user_id
            ).limit(10)
            
            result = await self.db.execute(stmt)
            past_texts = [row[0] for row in result.all() if row[0]]
            
            if not past_texts:
                return 0.0
            
            # Simple similarity check (in production, use ML similarity)
            current_lower = current_text.lower().strip()
            matches = sum(1 for text in past_texts if text.lower().strip() == current_lower)
            
            return matches / len(past_texts)
            
        except Exception as e:
            logger.warning(f"Could not detect identical patterns: {e}")
            return 0.0
    
    def _is_bot_account(self, username: str, claim_text: str) -> bool:
        """Detect if this is a bot account"""
        
        import re
        
        # Check username
        username_lower = username.lower()
        for pattern in self.BOT_PATTERNS:
            if re.search(pattern, username_lower):
                return True
        
        # Check claim text
        text_lower = claim_text.lower()
        for pattern in self.BOT_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _detect_team_collaboration(self, claim_text: str, issue_data: Dict) -> bool:
        """Detect if this is a team collaboration claim"""
        
        text_lower = claim_text.lower()
        
        # Check for collaboration keywords
        for keyword in self.COLLABORATION_KEYWORDS:
            if keyword in text_lower:
                return True
        
        # Check for multiple @ mentions
        mention_count = claim_text.count('@')
        if mention_count >= 2:
            return True
        
        return False
    
    def _detect_gaming_patterns(self, claim_history: List[Dict]) -> bool:
        """
        Detect gaming patterns:
        - Claiming easy issues only
        - Claiming right before deadlines
        - Claiming multiple repos simultaneously
        """
        
        if len(claim_history) < 5:
            return False
        
        # Check if only claiming "good first issue" type work
        # This would require label analysis from issue data
        # Placeholder for now
        
        # Check time-based gaming (claiming at specific times)
        claim_hours = [c['created_at'].hour for c in claim_history]
        
        # If all claims at same hour (automation/scripting)
        unique_hours = len(set(claim_hours))
        if unique_hours <= 2 and len(claim_history) > 5:
            return True
        
        return False
    
    def _classify_behavior(
        self,
        fraud_score: float,
        is_bot: bool,
        is_team: bool,
        abandonment_rate: float
    ) -> str:
        """Classify overall behavior type"""
        
        if is_bot:
            return 'BOT'
        
        if is_team:
            return 'COLLABORATIVE'
        
        if fraud_score > 70:
            return 'FRAUDULENT'
        
        if fraud_score > 40 or abandonment_rate > 0.6:
            return 'SUSPICIOUS'
        
        return 'GENUINE'
    
    def _generate_recommendations(
        self,
        fraud_score: float,
        anomalies: List[str],
        is_bot: bool,
        behavior_type: str
    ) -> List[str]:
        """Generate action recommendations based on analysis"""
        
        recommendations = []
        
        if is_bot:
            recommendations.append('BLOCK_BOT_CLAIMS')
            recommendations.append('ALERT_MAINTAINERS')
        
        elif fraud_score > 70:
            recommendations.append('BLOCK_USER')
            recommendations.append('REVIEW_ALL_ACTIVE_CLAIMS')
            recommendations.append('NOTIFY_SECURITY_TEAM')
        
        elif fraud_score > 50:
            recommendations.append('REQUIRE_MANUAL_APPROVAL')
            recommendations.append('REDUCE_GRACE_PERIOD')
            recommendations.append('INCREASE_MONITORING')
        
        elif behavior_type == 'COLLABORATIVE':
            recommendations.append('ALLOW_TEAM_CLAIM')
            recommendations.append('REQUEST_TEAM_MEMBERS')
        
        elif len(anomalies) > 2:
            recommendations.append('FLAG_FOR_REVIEW')
            recommendations.append('SEND_WARNING_MESSAGE')
        
        else:
            recommendations.append('PROCEED_NORMALLY')
        
        return recommendations
    
    def should_block_claim(self, analysis: BehavioralAnalysis) -> bool:
        """Determine if claim should be blocked"""
        return (
            analysis.fraud_score > 70 or
            analysis.behavior_type == 'FRAUDULENT' or
            'BLOCK_USER' in analysis.recommended_actions
        )
    
    def should_require_approval(self, analysis: BehavioralAnalysis) -> bool:
        """Determine if claim requires manual approval"""
        return (
            analysis.fraud_score > 40 or
            analysis.is_suspicious or
            'REQUIRE_MANUAL_APPROVAL' in analysis.recommended_actions
        )


async def get_behavioral_analyzer(db_session):
    """Get behavioral analyzer instance"""
    return BehavioralAnalyzer(db_session)
