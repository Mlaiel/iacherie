"""Competition Management Workflow

AI-powered competition and tournament management workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class CompetitionType(Enum):
    """Types of competitions"""
    CONTENT_CONTEST = "content_contest"
    ENGAGEMENT_CHALLENGE = "engagement_challenge"
    SKILL_TOURNAMENT = "skill_tournament"
    COLLABORATION_CONTEST = "collaboration_contest"
    INNOVATION_CHALLENGE = "innovation_challenge"
    SPEED_CHALLENGE = "speed_challenge"


class CompetitionStatus(Enum):
    """Competition status"""
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


@dataclass
class Competition:
    """Competition definition"""
    competition_id: str
    title: str
    description: str
    competition_type: CompetitionType
    status: CompetitionStatus
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int]
    entry_requirements: Dict[str, Any]
    judging_criteria: List[str]
    prizes: Dict[str, Any]
    participants: List[str] = field(default_factory=list)
    submissions: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompetitionSubmission:
    """Competition submission"""
    submission_id: str
    competition_id: str
    user_id: str
    submission_data: Dict[str, Any]
    score: float = 0.0
    rank: int = 0
    submitted_at: datetime = field(default_factory=datetime.utcnow)


class CompetitionManagementWorkflow:
    """AI-powered competition management workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.competitions: Dict[str, Competition] = {}
        self.submissions: Dict[str, CompetitionSubmission] = {}
        
    async def create_competition(
        self,
        title: str,
        description: str,
        competition_type: CompetitionType,
        duration_days: int,
        max_participants: Optional[int] = None,
        entry_requirements: Dict[str, Any] = None,
        prizes: Dict[str, Any] = None
    ) -> Competition:
        """
        Create a new competition
        
        Args:
            title: Competition title
            description: Competition description
            competition_type: Type of competition
            duration_days: Competition duration in days
            max_participants: Maximum number of participants
            entry_requirements: Requirements to join
            prizes: Prize structure
            
        Returns:
            Competition object
        """
        try:
            start_time = datetime.utcnow()
            competition_id = f"comp_{int(start_time.timestamp())}"
            
            # Set default values
            if entry_requirements is None:
                entry_requirements = {"minimum_level": 1}
            
            if prizes is None:
                prizes = await self._get_default_prizes(competition_type)
            
            # Determine judging criteria
            judging_criteria = await self._get_judging_criteria(competition_type)
            
            competition = Competition(
                competition_id=competition_id,
                title=title,
                description=description,
                competition_type=competition_type,
                status=CompetitionStatus.UPCOMING,
                start_date=start_time + timedelta(hours=1),  # Start in 1 hour
                end_date=start_time + timedelta(days=duration_days),
                max_participants=max_participants,
                entry_requirements=entry_requirements,
                judging_criteria=judging_criteria,
                prizes=prizes
            )
            
            # Store competition
            self.competitions[competition_id] = competition
            
            # Record metrics
            await self.metrics_collector.record_metric("competitions_created", 1)
            await self.metrics_collector.record_metric(f"competition_{competition_type.value}", 1)
            
            logger.info(f"Competition created: {title} ({competition_id})")
            return competition
            
        except Exception as e:
            logger.error(f"Competition creation failed: {e}")
            raise WorkflowError(f"Competition creation failed: {e}")
    
    async def join_competition(self, competition_id: str, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        User joins a competition
        
        Args:
            competition_id: Competition identifier
            user_id: User identifier
            user_data: User profile data for requirement checking
            
        Returns:
            True if successfully joined
        """
        try:
            if competition_id not in self.competitions:
                raise WorkflowError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            # Check if competition is open for registration
            now = datetime.utcnow()
            if competition.status != CompetitionStatus.UPCOMING and competition.status != CompetitionStatus.ACTIVE:
                raise WorkflowError("Competition is not open for registration")
            
            if now > competition.end_date:
                raise WorkflowError("Competition has ended")
            
            # Check if user already joined
            if user_id in competition.participants:
                return False  # Already joined
            
            # Check capacity
            if competition.max_participants and len(competition.participants) >= competition.max_participants:
                raise WorkflowError("Competition is full")
            
            # Check entry requirements
            if not await self._check_entry_requirements(competition.entry_requirements, user_data):
                raise WorkflowError("User does not meet entry requirements")
            
            # Add user to participants
            competition.participants.append(user_id)
            
            logger.info(f"User {user_id} joined competition {competition_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join competition: {e}")
            raise WorkflowError(f"Failed to join competition: {e}")
    
    async def submit_entry(
        self,
        competition_id: str,
        user_id: str,
        submission_data: Dict[str, Any]
    ) -> CompetitionSubmission:
        """
        Submit entry to competition
        
        Args:
            competition_id: Competition identifier
            user_id: User identifier
            submission_data: Submission content and metadata
            
        Returns:
            CompetitionSubmission object
        """
        try:
            if competition_id not in self.competitions:
                raise WorkflowError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            # Check if user is participant
            if user_id not in competition.participants:
                raise WorkflowError("User is not a participant in this competition")
            
            # Check if competition is active
            now = datetime.utcnow()
            if now < competition.start_date:
                raise WorkflowError("Competition has not started yet")
            
            if now > competition.end_date:
                raise WorkflowError("Competition submission period has ended")
            
            submission_id = f"sub_{int(datetime.utcnow().timestamp())}_{user_id}"
            
            submission = CompetitionSubmission(
                submission_id=submission_id,
                competition_id=competition_id,
                user_id=user_id,
                submission_data=submission_data
            )
            
            # Store submission
            self.submissions[submission_id] = submission
            competition.submissions[user_id] = submission_id
            
            logger.info(f"Submission received: {submission_id} for competition {competition_id}")
            return submission
            
        except Exception as e:
            logger.error(f"Submission failed: {e}")
            raise WorkflowError(f"Submission failed: {e}")
    
    async def evaluate_submissions(self, competition_id: str) -> Dict[str, Any]:
        """
        Evaluate all submissions for a competition
        
        Args:
            competition_id: Competition identifier
            
        Returns:
            Evaluation results
        """
        try:
            if competition_id not in self.competitions:
                raise WorkflowError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            # Get all submissions for this competition
            competition_submissions = [
                submission for submission in self.submissions.values()
                if submission.competition_id == competition_id
            ]
            
            if not competition_submissions:
                return {"message": "No submissions to evaluate"}
            
            # Evaluate each submission
            evaluated_submissions = []
            for submission in competition_submissions:
                score = await self._evaluate_submission(submission, competition)
                submission.score = score
                evaluated_submissions.append(submission)
            
            # Rank submissions
            evaluated_submissions.sort(key=lambda x: x.score, reverse=True)
            
            # Assign ranks
            for i, submission in enumerate(evaluated_submissions):
                submission.rank = i + 1
            
            # Store results
            competition.results = {
                "evaluated_at": datetime.utcnow().isoformat(),
                "total_submissions": len(evaluated_submissions),
                "winner": evaluated_submissions[0].user_id if evaluated_submissions else None,
                "top_3": [s.user_id for s in evaluated_submissions[:3]]
            }
            
            # Award prizes
            await self._award_prizes(competition, evaluated_submissions)
            
            logger.info(f"Competition {competition_id} evaluated. Winner: {competition.results.get('winner')}")
            
            return {
                "competition_id": competition_id,
                "results": competition.results,
                "rankings": [
                    {
                        "rank": s.rank,
                        "user_id": s.user_id,
                        "score": s.score
                    }
                    for s in evaluated_submissions
                ]
            }
            
        except Exception as e:
            logger.error(f"Competition evaluation failed: {e}")
            raise WorkflowError(f"Competition evaluation failed: {e}")
    
    async def get_active_competitions(self) -> List[Competition]:
        """Get all active competitions"""
        
        now = datetime.utcnow()
        active_competitions = []
        
        for competition in self.competitions.values():
            if (competition.status == CompetitionStatus.ACTIVE or 
                (competition.status == CompetitionStatus.UPCOMING and 
                 competition.start_date <= now <= competition.end_date)):
                active_competitions.append(competition)
        
        return active_competitions
    
    async def get_user_competitions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get competitions user is participating in"""
        
        user_competitions = []
        
        for competition in self.competitions.values():
            if user_id in competition.participants:
                user_data = {
                    "competition": competition,
                    "has_submitted": user_id in competition.submissions,
                    "submission_id": competition.submissions.get(user_id),
                    "status": self._get_user_competition_status(competition, user_id)
                }
                user_competitions.append(user_data)
        
        return user_competitions
    
    async def get_competition_leaderboard(self, competition_id: str) -> List[Dict[str, Any]]:
        """Get live leaderboard for competition"""
        
        if competition_id not in self.competitions:
            return []
        
        competition = self.competitions[competition_id]
        
        # Get submissions with scores
        leaderboard = []
        for user_id, submission_id in competition.submissions.items():
            if submission_id in self.submissions:
                submission = self.submissions[submission_id]
                leaderboard.append({
                    "user_id": user_id,
                    "score": submission.score,
                    "rank": submission.rank,
                    "submitted_at": submission.submitted_at
                })
        
        # Sort by score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard
    
    async def _get_default_prizes(self, competition_type: CompetitionType) -> Dict[str, Any]:
        """Get default prize structure for competition type"""
        
        base_prizes = {
            "1st_place": {"points": 1000, "badge": "Competition Winner", "feature_access": "premium_month"},
            "2nd_place": {"points": 500, "badge": "Competition Runner-up", "feature_access": "premium_week"},
            "3rd_place": {"points": 250, "badge": "Competition Bronze", "feature_access": "premium_trial"},
            "participation": {"points": 50, "badge": "Competition Participant"}
        }
        
        # Adjust based on competition type
        if competition_type == CompetitionType.INNOVATION_CHALLENGE:
            base_prizes["1st_place"]["special_recognition"] = "Innovation Spotlight"
        
        return base_prizes
    
    async def _get_judging_criteria(self, competition_type: CompetitionType) -> List[str]:
        """Get judging criteria for competition type"""
        
        criteria_map = {
            CompetitionType.CONTENT_CONTEST: ["creativity", "quality", "engagement", "originality"],
            CompetitionType.ENGAGEMENT_CHALLENGE: ["engagement_rate", "community_interaction", "viral_potential"],
            CompetitionType.SKILL_TOURNAMENT: ["technical_skill", "execution", "innovation"],
            CompetitionType.COLLABORATION_CONTEST: ["teamwork", "coordination", "combined_impact"],
            CompetitionType.INNOVATION_CHALLENGE: ["innovation", "feasibility", "impact", "creativity"],
            CompetitionType.SPEED_CHALLENGE: ["completion_time", "quality", "accuracy"]
        }
        
        return criteria_map.get(competition_type, ["quality", "creativity", "impact"])
    
    async def _check_entry_requirements(self, requirements: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Check if user meets entry requirements"""
        
        # Check minimum level
        min_level = requirements.get("minimum_level", 1)
        user_level = user_data.get("level", 1)
        if user_level < min_level:
            return False
        
        # Check follower count if required
        min_followers = requirements.get("minimum_followers")
        if min_followers:
            user_followers = user_data.get("followers_count", 0)
            if user_followers < min_followers:
                return False
        
        # Check content count if required
        min_content = requirements.get("minimum_content")
        if min_content:
            user_content = user_data.get("content_count", 0)
            if user_content < min_content:
                return False
        
        return True
    
    async def _evaluate_submission(self, submission: CompetitionSubmission, competition: Competition) -> float:
        """Evaluate individual submission based on criteria"""
        
        # Simulate AI-powered evaluation
        criteria_scores = {}
        
        for criterion in competition.judging_criteria:
            # In real implementation, this would use AI models
            import random
            criteria_scores[criterion] = random.uniform(0.5, 1.0)
        
        # Calculate weighted average
        total_score = sum(criteria_scores.values()) / len(criteria_scores)
        
        # Apply any bonus factors
        submission_data = submission.submission_data
        if submission_data.get("premium_features_used"):
            total_score *= 1.1  # 10% bonus
        
        if submission_data.get("collaboration"):
            total_score *= 1.05  # 5% bonus
        
        return min(total_score, 1.0)
    
    async def _award_prizes(self, competition: Competition, ranked_submissions: List[CompetitionSubmission]):
        """Award prizes to winners"""
        
        prizes = competition.prizes
        
        for i, submission in enumerate(ranked_submissions[:3]):  # Top 3
            prize_key = ["1st_place", "2nd_place", "3rd_place"][i]
            if prize_key in prizes:
                prize = prizes[prize_key]
                await self._grant_prize(submission.user_id, prize, competition.competition_id)
        
        # Participation prizes for all
        if "participation" in prizes:
            for submission in ranked_submissions:
                if submission.rank > 3:  # Not already awarded
                    await self._grant_prize(submission.user_id, prizes["participation"], competition.competition_id)
    
    async def _grant_prize(self, user_id: str, prize: Dict[str, Any], competition_id: str):
        """Grant prize to user"""
        
        logger.info(f"Granting prize to {user_id} for competition {competition_id}: {prize}")
        
        # In real implementation, this would:
        # 1. Add points to user account
        # 2. Grant badges
        # 3. Activate feature access
        # 4. Send notifications
    
    def _get_user_competition_status(self, competition: Competition, user_id: str) -> str:
        """Get user's status in competition"""
        
        now = datetime.utcnow()
        
        if now < competition.start_date:
            return "registered"
        elif now <= competition.end_date:
            if user_id in competition.submissions:
                return "submitted"
            else:
                return "active"
        else:
            if competition.results:
                return "completed"
            else:
                return "ended"