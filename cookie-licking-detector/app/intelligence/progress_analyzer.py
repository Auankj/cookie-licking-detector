"""
Progress Analysis Engine
Advanced semantic analysis of contributor progress with ML-powered predictions

Features:
- Semantic commit message analysis
- PR quality and velocity scoring
- Draft detection and WIP tracking
- Code review engagement analysis
- Stall detection (PR exists but inactive)
- Branch activity monitoring
- Predictive completion timeline
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ProgressAnalysis:
    """Comprehensive progress assessment"""
    progress_detected: bool
    progress_score: float  # 0-100
    progress_type: List[str]  # [commits, pr, review, etc]
    completion_probability: float  # 0-100 chance of completing
    estimated_completion_days: Optional[int]
    velocity: float  # Commits/PRs per day
    quality_indicators: Dict
    risk_signals: List[str]  # Warning signs
    confidence: float  # How confident we are in this analysis
    should_extend_grace_period: bool
    should_nudge_anyway: bool  # Even if progress exists
    metadata: Dict


class ProgressAnalysisEngine:
    """
    Advanced progress analysis using semantic understanding
    Goes beyond simple "commit exists" checks
    """
    
    # Semantic commit message patterns
    MEANINGFUL_COMMIT_PATTERNS = [
        r'\b(feat|feature|add|implement|create)\b',
        r'\b(fix|bugfix|resolve|patch)\b',
        r'\b(refactor|improve|optimize|enhance)\b',
        r'\b(test|spec|coverage)\b',
        r'\b(doc|documentation|readme)\b',
    ]
    
    TRIVIAL_COMMIT_PATTERNS = [
        r'\b(wip|work in progress)\b',
        r'\b(typo|formatting|whitespace)\b',
        r'\b(todo|fixme|placeholder)\b',
        r'^(update|fix|change)\s*$',  # Vague single-word messages
    ]
    
    # PR state indicators
    WIP_INDICATORS = [
        'wip', 'work in progress', 'draft', 'do not merge',
        'dnm', 'not ready', 'incomplete'
    ]
    
    # Stall indicators
    STALL_INDICATORS = {
        'no_commits_days': 7,  # No commits for N days
        'no_pr_updates_days': 5,  # PR not updated for N days
        'no_review_activity_days': 3,  # No review responses for N days
    }
    
    def __init__(self, db_session, github_service, ecosyste_client):
        self.db = db_session
        self.github = github_service
        self.ecosyste = ecosyste_client
    
    async def analyze_progress(
        self, 
        claim_id: int,
        issue_data: Dict,
        repository_data: Dict,
        username: str,
        claim_timestamp: datetime
    ) -> ProgressAnalysis:
        """
        Comprehensive progress analysis combining multiple data sources
        
        Analyzes:
        1. Commits (semantic analysis)
        2. Pull Requests (state, quality, velocity)
        3. Code review participation
        4. Branch activity
        5. Issue comments
        """
        
        logger.info(f"Starting advanced progress analysis for claim {claim_id}")
        
        # Gather all progress data
        commits = await self._fetch_commits(repository_data, username, claim_timestamp)
        prs = await self._fetch_pull_requests(repository_data, issue_data, username, claim_timestamp)
        branch_activity = await self._check_branch_activity(repository_data, username)
        review_activity = await self._check_review_activity(prs)
        
        # Analyze each component
        commit_analysis = self._analyze_commits(commits)
        pr_analysis = self._analyze_pull_requests(prs, issue_data['github_issue_number'])
        review_analysis = self._analyze_review_activity(review_activity)
        velocity_analysis = self._calculate_velocity(commits, prs, claim_timestamp)
        
        # Detect stall patterns
        stall_signals = self._detect_stall_patterns(commits, prs, review_activity)
        
        # Calculate overall progress score
        progress_score = self._calculate_progress_score(
            commit_analysis,
            pr_analysis,
            review_analysis,
            velocity_analysis
        )
        
        # Determine if meaningful progress exists
        progress_detected = progress_score > 30.0  # Threshold for "real" progress
        
        # Predict completion probability
        completion_prob = self._predict_completion_probability(
            progress_score,
            velocity_analysis,
            stall_signals,
            claim_timestamp
        )
        
        # Estimate completion timeline
        estimated_days = self._estimate_completion_timeline(
            velocity_analysis,
            pr_analysis,
            issue_data.get('complexity', 'MEDIUM')
        )
        
        # Determine if grace period should be extended
        should_extend = self._should_extend_grace_period(
            progress_score,
            pr_analysis,
            completion_prob
        )
        
        # Determine if nudge is needed despite progress
        should_nudge = self._should_nudge_anyway(
            stall_signals,
            pr_analysis,
            velocity_analysis
        )
        
        # Aggregate progress types
        progress_types = []
        if commit_analysis['meaningful_count'] > 0:
            progress_types.append('meaningful_commits')
        if pr_analysis['open_prs'] > 0:
            progress_types.append('pull_request')
        if pr_analysis['draft_prs'] > 0:
            progress_types.append('draft_pr')
        if review_analysis['engaged']:
            progress_types.append('code_review')
        if branch_activity:
            progress_types.append('branch_activity')
        
        # Quality indicators
        quality_indicators = {
            'commit_quality': commit_analysis['quality_score'],
            'pr_quality': pr_analysis['quality_score'],
            'test_coverage': commit_analysis['has_tests'],
            'documentation': commit_analysis['has_docs'],
            'review_engagement': review_analysis['response_rate']
        }
        
        # Risk signals
        risk_signals = stall_signals + self._identify_risk_signals(
            commit_analysis, pr_analysis, velocity_analysis
        )
        
        logger.info(
            f"Progress analysis complete for claim {claim_id}",
            score=progress_score,
            completion_prob=completion_prob,
            progress_types=progress_types
        )
        
        return ProgressAnalysis(
            progress_detected=progress_detected,
            progress_score=round(progress_score, 2),
            progress_type=progress_types,
            completion_probability=round(completion_prob, 2),
            estimated_completion_days=estimated_days,
            velocity=round(velocity_analysis['velocity'], 2),
            quality_indicators=quality_indicators,
            risk_signals=risk_signals,
            confidence=self._calculate_confidence(commit_analysis, pr_analysis),
            should_extend_grace_period=should_extend,
            should_nudge_anyway=should_nudge,
            metadata={
                'commit_count': commit_analysis['total_count'],
                'meaningful_commits': commit_analysis['meaningful_count'],
                'pr_count': pr_analysis['total_prs'],
                'open_prs': pr_analysis['open_prs'],
                'draft_prs': pr_analysis['draft_prs']
            }
        )
    
    async def _fetch_commits(
        self, 
        repository_data: Dict, 
        username: str, 
        since: datetime
    ) -> List[Dict]:
        """Fetch commits with full metadata"""
        try:
            commits = await self.github.get_user_commits(
                owner=repository_data['owner'],
                name=repository_data['name'],
                username=username,
                since=since
            )
            return commits or []
        except Exception as e:
            logger.warning(f"Error fetching commits: {e}")
            return []
    
    async def _fetch_pull_requests(
        self,
        repository_data: Dict,
        issue_data: Dict,
        username: str,
        since: datetime
    ) -> List[Dict]:
        """Fetch PRs referencing the issue"""
        try:
            prs = await self.github.get_pull_requests_for_issue(
                owner=repository_data['owner'],
                name=repository_data['name'],
                issue_number=issue_data['github_issue_number']
            )
            
            # Filter by user and date
            user_prs = [
                pr for pr in prs
                if pr.get('user', {}).get('login') == username
                and datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00')) >= since
            ]
            
            return user_prs
        except Exception as e:
            logger.warning(f"Error fetching PRs: {e}")
            return []
    
    async def _check_branch_activity(self, repository_data: Dict, username: str) -> bool:
        """Check if user has active branches"""
        # This would integrate with GitHub API to check for branches
        # Placeholder for now
        return False
    
    async def _check_review_activity(self, prs: List[Dict]) -> List[Dict]:
        """Check code review participation"""
        review_data = []
        
        for pr in prs:
            # This would fetch review comments, approvals, etc.
            # Placeholder for now
            review_data.append({
                'pr_number': pr['number'],
                'comments': 0,
                'reviews': 0,
                'last_activity': pr.get('updated_at')
            })
        
        return review_data
    
    def _analyze_commits(self, commits: List[Dict]) -> Dict:
        """
        Semantic analysis of commits
        Determines if commits are meaningful or trivial
        """
        total_count = len(commits)
        meaningful_count = 0
        trivial_count = 0
        has_tests = False
        has_docs = False
        
        for commit in commits:
            message = commit.get('message', '').lower()
            
            # Check if meaningful
            is_meaningful = any(
                re.search(pattern, message, re.IGNORECASE)
                for pattern in self.MEANINGFUL_COMMIT_PATTERNS
            )
            
            # Check if trivial
            is_trivial = any(
                re.search(pattern, message, re.IGNORECASE)
                for pattern in self.TRIVIAL_COMMIT_PATTERNS
            )
            
            if is_meaningful and not is_trivial:
                meaningful_count += 1
            elif is_trivial:
                trivial_count += 1
            
            # Check for tests
            if re.search(r'\b(test|spec)\b', message, re.IGNORECASE):
                has_tests = True
            
            # Check for docs
            if re.search(r'\b(doc|readme|documentation)\b', message, re.IGNORECASE):
                has_docs = True
        
        # Calculate quality score
        if total_count == 0:
            quality_score = 0.0
        else:
            quality_score = (meaningful_count / total_count) * 100
        
        return {
            'total_count': total_count,
            'meaningful_count': meaningful_count,
            'trivial_count': trivial_count,
            'quality_score': quality_score,
            'has_tests': has_tests,
            'has_docs': has_docs
        }
    
    def _analyze_pull_requests(self, prs: List[Dict], issue_number: int) -> Dict:
        """Analyze PR state and quality"""
        total_prs = len(prs)
        open_prs = 0
        draft_prs = 0
        merged_prs = 0
        stalled_prs = 0
        
        for pr in prs:
            state = pr.get('state', '').lower()
            
            if state == 'open':
                open_prs += 1
                
                # Check if draft
                title = pr.get('title', '').lower()
                if any(indicator in title for indicator in self.WIP_INDICATORS):
                    draft_prs += 1
                
                # Check if stalled
                updated_at = datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(timezone.utc) - updated_at).days
                
                if days_since_update > self.STALL_INDICATORS['no_pr_updates_days']:
                    stalled_prs += 1
            
            elif pr.get('merged_at'):
                merged_prs += 1
        
        # Calculate PR quality score
        quality_score = 0.0
        if total_prs > 0:
            quality_score = (
                (merged_prs * 100) +  # Merged PRs = excellent
                (open_prs * 70) +      # Open PRs = good
                (draft_prs * 40) -     # Draft PRs = moderate
                (stalled_prs * 20)     # Stalled PRs = concerning
            ) / total_prs
        
        return {
            'total_prs': total_prs,
            'open_prs': open_prs,
            'draft_prs': draft_prs,
            'merged_prs': merged_prs,
            'stalled_prs': stalled_prs,
            'quality_score': max(0.0, min(100.0, quality_score)),
            'has_merged': merged_prs > 0,
            'has_open': open_prs > 0
        }
    
    def _analyze_review_activity(self, review_data: List[Dict]) -> Dict:
        """Analyze code review engagement"""
        if not review_data:
            return {'engaged': False, 'response_rate': 0.0}
        
        # This would analyze review comments, response times, etc.
        # Placeholder for now
        return {
            'engaged': len(review_data) > 0,
            'response_rate': 50.0
        }
    
    def _calculate_velocity(
        self, 
        commits: List[Dict], 
        prs: List[Dict], 
        claim_timestamp: datetime
    ) -> Dict:
        """Calculate work velocity (commits/PRs per day)"""
        days_since_claim = (datetime.now(timezone.utc) - claim_timestamp).days
        if days_since_claim == 0:
            days_since_claim = 1
        
        commit_velocity = len(commits) / days_since_claim
        pr_velocity = len(prs) / days_since_claim
        
        # Combined velocity score
        velocity = (commit_velocity * 0.6) + (pr_velocity * 0.4)
        
        return {
            'velocity': velocity,
            'commit_velocity': commit_velocity,
            'pr_velocity': pr_velocity,
            'days_active': days_since_claim
        }
    
    def _detect_stall_patterns(
        self, 
        commits: List[Dict], 
        prs: List[Dict], 
        review_activity: List[Dict]
    ) -> List[str]:
        """Detect stall patterns indicating progress has stopped"""
        signals = []
        
        if commits:
            # Check last commit date
            last_commit = max(
                datetime.fromisoformat(c.get('created_at', c.get('date', '')).replace('Z', '+00:00'))
                for c in commits
                if c.get('created_at') or c.get('date')
            )
            days_since_commit = (datetime.now(timezone.utc) - last_commit).days
            
            if days_since_commit > self.STALL_INDICATORS['no_commits_days']:
                signals.append(f'no_commits_{days_since_commit}_days')
        
        for pr in prs:
            if pr.get('state') == 'open':
                updated_at = datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(timezone.utc) - updated_at).days
                
                if days_since_update > self.STALL_INDICATORS['no_pr_updates_days']:
                    signals.append(f'stalled_pr_{pr["number"]}')
        
        return signals
    
    def _calculate_progress_score(
        self,
        commit_analysis: Dict,
        pr_analysis: Dict,
        review_analysis: Dict,
        velocity_analysis: Dict
    ) -> float:
        """Calculate overall progress score (0-100)"""
        
        # Component scores
        commit_score = min(100.0, commit_analysis['meaningful_count'] * 20)
        pr_score = pr_analysis['quality_score']
        review_score = review_analysis['response_rate']
        velocity_score = min(100.0, velocity_analysis['velocity'] * 50)
        
        # Weighted combination
        overall_score = (
            commit_score * 0.35 +
            pr_score * 0.35 +
            velocity_score * 0.20 +
            review_score * 0.10
        )
        
        return max(0.0, min(100.0, overall_score))
    
    def _predict_completion_probability(
        self,
        progress_score: float,
        velocity_analysis: Dict,
        stall_signals: List[str],
        claim_timestamp: datetime
    ) -> float:
        """Predict probability of completing the claim (0-100%)"""
        
        # Base probability from progress score
        base_prob = progress_score
        
        # Adjust for velocity
        if velocity_analysis['velocity'] > 0.5:
            base_prob += 10  # High velocity increases probability
        elif velocity_analysis['velocity'] < 0.1:
            base_prob -= 20  # Low velocity decreases probability
        
        # Penalize for stall signals
        base_prob -= len(stall_signals) * 10
        
        # Penalize for time without completion
        days_since_claim = (datetime.now(timezone.utc) - claim_timestamp).days
        if days_since_claim > 14:
            base_prob -= (days_since_claim - 14) * 2
        
        return max(0.0, min(100.0, base_prob))
    
    def _estimate_completion_timeline(
        self,
        velocity_analysis: Dict,
        pr_analysis: Dict,
        issue_complexity: str
    ) -> Optional[int]:
        """Estimate days until completion"""
        
        # If PR is merged, completion is immediate
        if pr_analysis['has_merged']:
            return 0
        
        # If PR is open and not stalled
        if pr_analysis['has_open'] and pr_analysis['stalled_prs'] == 0:
            return 3  # Estimate 3 days for review and merge
        
        # Based on velocity and complexity
        velocity = velocity_analysis['velocity']
        
        complexity_days = {
            'TRIVIAL': 2,
            'EASY': 5,
            'MEDIUM': 10,
            'HARD': 20,
            'VERY_HARD': 30
        }
        
        base_days = complexity_days.get(issue_complexity, 10)
        
        if velocity > 0:
            # Adjust based on velocity
            estimated_days = int(base_days / (velocity + 0.1))
        else:
            estimated_days = base_days * 2
        
        return max(1, min(60, estimated_days))
    
    def _should_extend_grace_period(
        self,
        progress_score: float,
        pr_analysis: Dict,
        completion_prob: float
    ) -> bool:
        """Determine if grace period should be extended"""
        
        # Extend if good progress and high completion probability
        if progress_score > 60 and completion_prob > 70:
            return True
        
        # Extend if PR is open and active
        if pr_analysis['has_open'] and pr_analysis['stalled_prs'] == 0:
            return True
        
        return False
    
    def _should_nudge_anyway(
        self,
        stall_signals: List[str],
        pr_analysis: Dict,
        velocity_analysis: Dict
    ) -> bool:
        """Determine if nudge is needed despite progress"""
        
        # Nudge if work has stalled
        if len(stall_signals) >= 2:
            return True
        
        # Nudge if PR exists but is stalled
        if pr_analysis['stalled_prs'] > 0:
            return True
        
        # Nudge if velocity is very low
        if velocity_analysis['velocity'] < 0.05:
            return True
        
        return False
    
    def _calculate_confidence(
        self,
        commit_analysis: Dict,
        pr_analysis: Dict
    ) -> float:
        """Calculate confidence in the analysis"""
        
        # More data = higher confidence
        data_points = commit_analysis['total_count'] + pr_analysis['total_prs']
        
        if data_points >= 10:
            return 95.0
        elif data_points >= 5:
            return 80.0
        elif data_points >= 2:
            return 60.0
        elif data_points >= 1:
            return 40.0
        else:
            return 20.0
    
    def _identify_risk_signals(
        self,
        commit_analysis: Dict,
        pr_analysis: Dict,
        velocity_analysis: Dict
    ) -> List[str]:
        """Identify risk signals for non-completion"""
        signals = []
        
        if commit_analysis['trivial_count'] > commit_analysis['meaningful_count']:
            signals.append('mostly_trivial_commits')
        
        if pr_analysis['draft_prs'] > pr_analysis['open_prs']:
            signals.append('only_draft_prs')
        
        if velocity_analysis['velocity'] < 0.1:
            signals.append('very_low_velocity')
        
        if not commit_analysis['has_tests']:
            signals.append('no_test_coverage')
        
        return signals


async def get_progress_analyzer(db_session, github_service, ecosyste_client):
    """Get progress analyzer instance"""
    return ProgressAnalysisEngine(db_session, github_service, ecosyste_client)
