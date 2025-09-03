"""Competition Engine - Advanced Competition and Event Management
==============================================================

Sophisticated competition management system providing tournament creation,
competitive events, real-time leaderboards, bracket management, and
comprehensive competition analytics for content creator engagement.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/challenges/competition_engine.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
import random

logger = logging.getLogger(__name__)


class CompetitionType(str, Enum):
    """Types of competitions."""
    TOURNAMENT = "tournament"
    LEADERBOARD = "leaderboard"
    BRACKET = "bracket"
    BATTLE_ROYALE = "battle_royale"
    TEAM_COMPETITION = "team_competition"
    SEASONAL_EVENT = "seasonal_event"
    SPEED_CHALLENGE = "speed_challenge"
    ENDURANCE = "endurance"
    SKILL_SHOWCASE = "skill_showcase"
    COMMUNITY_VOTE = "community_vote"


class CompetitionStatus(str, Enum):
    """Competition status states."""
    UPCOMING = "upcoming"
    REGISTRATION = "registration"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ParticipantType(str, Enum):
    """Types of competition participants."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    GUILD = "guild"


class ScoringMethod(str, Enum):
    """Methods for scoring competitions."""
    TOTAL_POINTS = "total_points"
    AVERAGE_SCORE = "average_score"
    BEST_SUBMISSION = "best_submission"
    WEIGHTED_SCORE = "weighted_score"
    PEER_VOTING = "peer_voting"
    JUDGE_SCORE = "judge_score"
    COMPOSITE = "composite"


@dataclass
class CompetitionPrize:
    """Prize definition for competition rankings."""
    rank_range: Tuple[int, int]  # (min_rank, max_rank) e.g., (1, 1) for 1st place
    prize_type: str  # currency, badge, trophy, feature_access, etc.
    value: Union[float, int, str, Dict[str, Any]]
    description: str
    rarity: str = "common"
    is_transferable: bool = False


@dataclass
class CompetitionRules:
    """Competition rules and configuration."""
    scoring_method: ScoringMethod
    submission_requirements: Dict[str, Any]
    evaluation_criteria: List[Dict[str, Any]]
    max_submissions_per_participant: int = 1
    allow_team_participation: bool = False
    max_team_size: int = 1
    voting_enabled: bool = False
    judge_review_required: bool = False
    elimination_rounds: bool = False
    qualification_threshold: Optional[float] = None


@dataclass
class Competition:
    """Competition definition and management."""
    id: str
    title: str
    description: str
    competition_type: CompetitionType
    status: CompetitionStatus
    rules: CompetitionRules
    prizes: List[CompetitionPrize]
    registration_start: datetime
    registration_end: datetime
    competition_start: datetime
    competition_end: datetime
    max_participants: Optional[int] = None
    min_participants: int = 2
    current_participants: int = 0
    entry_fee: Optional[float] = None
    sponsor_info: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    creator_id: Optional[str] = None
    is_featured: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompetitionParticipant:
    """Competition participant information."""
    id: str
    competition_id: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    participant_type: ParticipantType = ParticipantType.INDIVIDUAL
    registration_date: datetime = field(default_factory=datetime.utcnow)
    current_score: float = 0.0
    current_rank: int = 0
    submissions: List[Dict[str, Any]] = field(default_factory=list)
    elimination_round: Optional[int] = None
    is_qualified: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionSubmission:
    """Competition submission data."""
    id: str
    competition_id: str
    participant_id: str
    content_data: Dict[str, Any]
    submission_date: datetime = field(default_factory=datetime.utcnow)
    score: Optional[float] = None
    votes: int = 0
    judge_scores: List[float] = field(default_factory=list)
    is_validated: bool = False
    validation_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionLeaderboard:
    """Competition leaderboard data."""
    competition_id: str
    participants: List[CompetitionParticipant]
    last_updated: datetime = field(default_factory=datetime.utcnow)
    round_number: int = 1
    elimination_data: Optional[Dict[str, Any]] = None


class CompetitionEngine:
    """
    Advanced competition and event management system.
    
    Provides tournament creation, competitive events, real-time leaderboards,
    bracket management, and comprehensive competition analytics.
    """
    
    def __init__(self):
        """Initialize the competition engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Competition management
        self.competitions: Dict[str, Competition] = {}
        self.participants: Dict[str, List[CompetitionParticipant]] = {}
        self.submissions: Dict[str, List[CompetitionSubmission]] = {}
        self.leaderboards: Dict[str, CompetitionLeaderboard] = {}
        
        # Competition templates for quick creation
        self.competition_templates: Dict[str, Dict[str, Any]] = {}
        
        # Event scheduling and management
        self.scheduled_events: List[Dict[str, Any]] = []
        
        # Statistics and analytics
        self.competition_statistics: Dict[str, Any] = {}
        
        self.logger.info("CompetitionEngine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the competition engine with default templates."""
        try:
            # Load default competition templates
            await self._load_default_templates()
            
            # Start background tasks
            asyncio.create_task(self._manage_competition_lifecycle())
            asyncio.create_task(self._update_leaderboards())
            asyncio.create_task(self._process_scheduled_events())
            
            self.initialized = True
            self.logger.info(f"✅ CompetitionEngine initialized with {len(self.competition_templates)} templates")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize CompetitionEngine: {e}")
            return False
    
    async def _load_default_templates(self):
        """Load default competition templates."""
        default_templates = {
            "weekly_content_battle": {
                "title": "Weekly Content Battle",
                "description": "Compete to create the best content this week",
                "competition_type": CompetitionType.LEADERBOARD,
                "duration_hours": 168,  # 7 days
                "rules": {
                    "scoring_method": ScoringMethod.COMPOSITE,
                    "submission_requirements": {
                        "content_type": "any",
                        "min_quality_score": 0.6,
                        "max_submissions": 5
                    },
                    "evaluation_criteria": [
                        {"name": "Quality", "weight": 0.4},
                        {"name": "Engagement", "weight": 0.3},
                        {"name": "Creativity", "weight": 0.3}
                    ],
                    "max_submissions_per_participant": 5
                },
                "prizes": [
                    {"rank_range": (1, 1), "prize_type": "currency", "value": 1000, "description": "First place prize"},
                    {"rank_range": (2, 2), "prize_type": "currency", "value": 500, "description": "Second place prize"},
                    {"rank_range": (3, 3), "prize_type": "currency", "value": 250, "description": "Third place prize"},
                    {"rank_range": (4, 10), "prize_type": "badge", "value": "top_performer", "description": "Top performer badge"}
                ],
                "max_participants": 100,
                "tags": ["weekly", "content", "competitive"]
            },
            "speed_creation_challenge": {
                "title": "Speed Creation Challenge",
                "description": "Create amazing content in record time",
                "competition_type": CompetitionType.SPEED_CHALLENGE,
                "duration_hours": 2,
                "rules": {
                    "scoring_method": ScoringMethod.WEIGHTED_SCORE,
                    "submission_requirements": {
                        "time_limit_minutes": 90,
                        "min_quality_score": 0.5
                    },
                    "evaluation_criteria": [
                        {"name": "Speed", "weight": 0.4},
                        {"name": "Quality", "weight": 0.6}
                    ],
                    "max_submissions_per_participant": 1
                },
                "prizes": [
                    {"rank_range": (1, 1), "prize_type": "trophy", "value": "speed_master", "description": "Speed Master trophy"},
                    {"rank_range": (2, 5), "prize_type": "badge", "value": "speed_demon", "description": "Speed Demon badge"}
                ],
                "max_participants": 50,
                "tags": ["speed", "challenge", "skill"]
            },
            "collaboration_tournament": {
                "title": "Collaboration Tournament",
                "description": "Team up and compete in collaborative challenges",
                "competition_type": CompetitionType.TEAM_COMPETITION,
                "duration_hours": 336,  # 14 days
                "rules": {
                    "scoring_method": ScoringMethod.TOTAL_POINTS,
                    "submission_requirements": {
                        "team_size": {"min": 2, "max": 4},
                        "collaboration_proof": True
                    },
                    "evaluation_criteria": [
                        {"name": "Teamwork", "weight": 0.3},
                        {"name": "Output Quality", "weight": 0.4},
                        {"name": "Innovation", "weight": 0.3}
                    ],
                    "allow_team_participation": True,
                    "max_team_size": 4,
                    "max_submissions_per_participant": 3
                },
                "prizes": [
                    {"rank_range": (1, 1), "prize_type": "team_trophy", "value": "collaboration_champions", "description": "Collaboration Champions trophy"},
                    {"rank_range": (1, 1), "prize_type": "currency", "value": 2000, "description": "Winning team prize pool"},
                    {"rank_range": (2, 2), "prize_type": "currency", "value": 1000, "description": "Runner-up prize pool"}
                ],
                "max_participants": 80,  # 20 teams max
                "tags": ["collaboration", "team", "tournament"]
            },
            "seasonal_showcase": {
                "title": "Seasonal Creator Showcase",
                "description": "Showcase your best seasonal content",
                "competition_type": CompetitionType.SKILL_SHOWCASE,
                "duration_hours": 720,  # 30 days
                "rules": {
                    "scoring_method": ScoringMethod.PEER_VOTING,
                    "submission_requirements": {
                        "seasonal_theme": True,
                        "min_quality_score": 0.7,
                        "community_voting": True
                    },
                    "evaluation_criteria": [
                        {"name": "Creativity", "weight": 0.4},
                        {"name": "Seasonal Relevance", "weight": 0.3},
                        {"name": "Community Appeal", "weight": 0.3}
                    ],
                    "voting_enabled": True,
                    "max_submissions_per_participant": 2
                },
                "prizes": [
                    {"rank_range": (1, 1), "prize_type": "seasonal_crown", "value": "winter_creator_crown", "description": "Seasonal Creator Crown"},
                    {"rank_range": (1, 3), "prize_type": "featured_placement", "value": {"duration": 30}, "description": "Featured creator placement"},
                    {"rank_range": (4, 10), "prize_type": "seasonal_badge", "value": "showcase_participant", "description": "Showcase participant badge"}
                ],
                "max_participants": 200,
                "tags": ["seasonal", "showcase", "community"]
            },
            "innovation_bracket": {
                "title": "Innovation Bracket Challenge",
                "description": "Bracket-style competition for most innovative creators",
                "competition_type": CompetitionType.BRACKET,
                "duration_hours": 240,  # 10 days
                "rules": {
                    "scoring_method": ScoringMethod.JUDGE_SCORE,
                    "submission_requirements": {
                        "innovation_focus": True,
                        "judge_review": True
                    },
                    "evaluation_criteria": [
                        {"name": "Innovation", "weight": 0.5},
                        {"name": "Execution", "weight": 0.3},
                        {"name": "Impact", "weight": 0.2}
                    ],
                    "elimination_rounds": True,
                    "judge_review_required": True,
                    "max_submissions_per_participant": 1
                },
                "prizes": [
                    {"rank_range": (1, 1), "prize_type": "innovation_award", "value": "innovation_champion", "description": "Innovation Champion award"},
                    {"rank_range": (1, 1), "prize_type": "feature_access", "value": "beta_program", "description": "Exclusive beta program access"},
                    {"rank_range": (2, 4), "prize_type": "innovation_badge", "value": "innovation_finalist", "description": "Innovation finalist badge"}
                ],
                "max_participants": 32,  # Power of 2 for bracket
                "tags": ["innovation", "bracket", "judged"]
            }
        }
        
        self.competition_templates = default_templates
        self.logger.info(f"Loaded {len(default_templates)} default competition templates")
    
    async def create_competition(
        self,
        template_id: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        creator_id: Optional[str] = None
    ) -> Optional[Competition]:
        """Create a new competition from template or custom configuration."""
        try:
            if template_id and template_id in self.competition_templates:
                # Create from template
                template = self.competition_templates[template_id]
                config = template.copy()
                
                # Apply custom overrides
                if custom_config:
                    config.update(custom_config)
            elif custom_config:
                # Create from custom configuration
                config = custom_config
            else:
                self.logger.error("No template or custom configuration provided")
                return None
            
            # Generate competition instance
            competition_id = str(uuid4())
            
            # Calculate dates
            now = datetime.utcnow()
            registration_start = config.get("registration_start", now)
            registration_duration = config.get("registration_duration_hours", 24)
            registration_end = registration_start + timedelta(hours=registration_duration)
            competition_start = config.get("competition_start", registration_end)
            competition_duration = config.get("duration_hours", 168)
            competition_end = competition_start + timedelta(hours=competition_duration)
            
            # Create rules
            rules_config = config.get("rules", {})
            rules = CompetitionRules(
                scoring_method=ScoringMethod(rules_config.get("scoring_method", "total_points")),
                submission_requirements=rules_config.get("submission_requirements", {}),
                evaluation_criteria=rules_config.get("evaluation_criteria", []),
                max_submissions_per_participant=rules_config.get("max_submissions_per_participant", 1),
                allow_team_participation=rules_config.get("allow_team_participation", False),
                max_team_size=rules_config.get("max_team_size", 1),
                voting_enabled=rules_config.get("voting_enabled", False),
                judge_review_required=rules_config.get("judge_review_required", False),
                elimination_rounds=rules_config.get("elimination_rounds", False),
                qualification_threshold=rules_config.get("qualification_threshold")
            )
            
            # Create prizes
            prizes = []
            for prize_config in config.get("prizes", []):
                prize = CompetitionPrize(
                    rank_range=tuple(prize_config["rank_range"]),
                    prize_type=prize_config["prize_type"],
                    value=prize_config["value"],
                    description=prize_config["description"],
                    rarity=prize_config.get("rarity", "common"),
                    is_transferable=prize_config.get("is_transferable", False)
                )
                prizes.append(prize)
            
            # Create competition
            competition = Competition(
                id=competition_id,
                title=config["title"],
                description=config["description"],
                competition_type=CompetitionType(config["competition_type"]),
                status=CompetitionStatus.UPCOMING,
                rules=rules,
                prizes=prizes,
                registration_start=registration_start,
                registration_end=registration_end,
                competition_start=competition_start,
                competition_end=competition_end,
                max_participants=config.get("max_participants"),
                min_participants=config.get("min_participants", 2),
                entry_fee=config.get("entry_fee"),
                sponsor_info=config.get("sponsor_info"),
                tags=config.get("tags", []),
                creator_id=creator_id,
                is_featured=config.get("is_featured", False),
                metadata=config.get("metadata", {})
            )
            
            # Store competition
            self.competitions[competition_id] = competition
            self.participants[competition_id] = []
            self.submissions[competition_id] = []
            
            # Create initial leaderboard
            self.leaderboards[competition_id] = CompetitionLeaderboard(
                competition_id=competition_id,
                participants=[]
            )
            
            self.logger.info(f"Created competition: {competition.title} (ID: {competition_id})")
            
            return competition
            
        except Exception as e:
            self.logger.error(f"Error creating competition: {e}")
            return None
    
    async def register_participant(
        self,
        competition_id: str,
        user_id: str,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a participant for a competition."""
        try:
            if competition_id not in self.competitions:
                return {"success": False, "error": "Competition not found"}
            
            competition = self.competitions[competition_id]
            
            # Check registration period
            now = datetime.utcnow()
            if now < competition.registration_start:
                return {"success": False, "error": "Registration not yet open"}
            if now > competition.registration_end:
                return {"success": False, "error": "Registration period ended"}
            
            # Check participant limit
            if (competition.max_participants and 
                competition.current_participants >= competition.max_participants):
                return {"success": False, "error": "Competition is full"}
            
            # Check if already registered
            for participant in self.participants[competition_id]:
                if participant.user_id == user_id:
                    return {"success": False, "error": "Already registered"}
            
            # Determine participant type
            participant_type = ParticipantType.TEAM if team_id else ParticipantType.INDIVIDUAL
            
            # Validate team participation
            if participant_type == ParticipantType.TEAM and not competition.rules.allow_team_participation:
                return {"success": False, "error": "Team participation not allowed"}
            
            # Create participant
            participant = CompetitionParticipant(
                id=str(uuid4()),
                competition_id=competition_id,
                user_id=user_id,
                team_id=team_id,
                participant_type=participant_type
            )
            
            # Add to participants
            self.participants[competition_id].append(participant)
            competition.current_participants += 1
            
            # Update leaderboard
            self.leaderboards[competition_id].participants.append(participant)
            
            self.logger.info(f"Registered participant {user_id} for competition {competition.title}")
            
            return {
                "success": True,
                "participant_id": participant.id,
                "competition": {
                    "id": competition.id,
                    "title": competition.title,
                    "competition_start": competition.competition_start,
                    "competition_end": competition.competition_end,
                    "rules": {
                        "max_submissions": competition.rules.max_submissions_per_participant,
                        "submission_requirements": competition.rules.submission_requirements
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error registering participant: {e}")
            return {"success": False, "error": str(e)}
    
    async def submit_entry(
        self,
        competition_id: str,
        participant_id: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit an entry to a competition."""
        try:
            if competition_id not in self.competitions:
                return {"success": False, "error": "Competition not found"}
            
            competition = self.competitions[competition_id]
            
            # Check if competition is active
            if competition.status != CompetitionStatus.ACTIVE:
                return {"success": False, "error": "Competition is not active"}
            
            # Find participant
            participant = None
            for p in self.participants[competition_id]:
                if p.id == participant_id:
                    participant = p
                    break
            
            if not participant:
                return {"success": False, "error": "Participant not found"}
            
            # Check submission limits
            current_submissions = len(participant.submissions)
            if current_submissions >= competition.rules.max_submissions_per_participant:
                return {"success": False, "error": "Maximum submissions reached"}
            
            # Validate submission requirements
            validation_result = await self._validate_submission(
                content_data, competition.rules.submission_requirements
            )
            if not validation_result["valid"]:
                return {"success": False, "error": f"Validation failed: {validation_result['reason']}"}
            
            # Create submission
            submission = CompetitionSubmission(
                id=str(uuid4()),
                competition_id=competition_id,
                participant_id=participant_id,
                content_data=content_data,
                is_validated=True
            )
            
            # Add to submissions
            self.submissions[competition_id].append(submission)
            participant.submissions.append({
                "id": submission.id,
                "submission_date": submission.submission_date,
                "content_summary": content_data.get("title", "Submission")
            })
            
            # Calculate initial score if possible
            if competition.rules.scoring_method in [ScoringMethod.TOTAL_POINTS, ScoringMethod.AVERAGE_SCORE]:
                score = await self._calculate_submission_score(submission, competition)
                submission.score = score
                
                # Update participant score
                if competition.rules.scoring_method == ScoringMethod.TOTAL_POINTS:
                    participant.current_score += score
                elif competition.rules.scoring_method == ScoringMethod.AVERAGE_SCORE:
                    total_score = sum(s.score for s in self.submissions[competition_id] 
                                    if s.participant_id == participant_id and s.score is not None)
                    participant.current_score = total_score / len(participant.submissions)
                elif competition.rules.scoring_method == ScoringMethod.BEST_SUBMISSION:
                    participant.current_score = max(
                        participant.current_score, score
                    )
            
            # Update leaderboard
            await self._update_competition_leaderboard(competition_id)
            
            self.logger.info(f"Submission received for competition {competition.title}")
            
            return {
                "success": True,
                "submission_id": submission.id,
                "current_score": participant.current_score,
                "current_rank": participant.current_rank,
                "submissions_remaining": competition.rules.max_submissions_per_participant - len(participant.submissions)
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting entry: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_submission(
        self,
        content_data: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate submission against competition requirements."""
        try:
            # Check content type
            if "content_type" in requirements:
                required_type = requirements["content_type"]
                actual_type = content_data.get("type", "unknown")
                if required_type != "any" and actual_type != required_type:
                    return {"valid": False, "reason": f"Expected {required_type}, got {actual_type}"}
            
            # Check quality score
            if "min_quality_score" in requirements:
                min_quality = requirements["min_quality_score"]
                actual_quality = content_data.get("quality_score", 0)
                if actual_quality < min_quality:
                    return {"valid": False, "reason": f"Quality score {actual_quality} below minimum {min_quality}"}
            
            # Check time limit (for speed challenges)
            if "time_limit_minutes" in requirements:
                time_limit = requirements["time_limit_minutes"]
                creation_time = content_data.get("creation_time_minutes", 0)
                if creation_time > time_limit:
                    return {"valid": False, "reason": f"Creation time {creation_time}min exceeds limit {time_limit}min"}
            
            # Check seasonal theme
            if requirements.get("seasonal_theme"):
                if not content_data.get("has_seasonal_theme", False):
                    return {"valid": False, "reason": "Missing required seasonal theme"}
            
            # Check collaboration proof
            if requirements.get("collaboration_proof"):
                if not content_data.get("collaboration_verified", False):
                    return {"valid": False, "reason": "Collaboration proof required"}
            
            return {"valid": True}
            
        except Exception as e:
            self.logger.error(f"Error validating submission: {e}")
            return {"valid": False, "reason": "Validation error"}
    
    async def _calculate_submission_score(
        self,
        submission: CompetitionSubmission,
        competition: Competition
    ) -> float:
        """Calculate score for a submission."""
        try:
            content_data = submission.content_data
            criteria = competition.rules.evaluation_criteria
            
            if not criteria:
                # Default scoring based on quality and engagement
                quality_score = content_data.get("quality_score", 0.5)
                engagement_score = content_data.get("engagement_score", 0.5)
                return (quality_score * 0.6 + engagement_score * 0.4) * 100
            
            # Weighted scoring based on criteria
            total_score = 0.0
            total_weight = sum(criterion.get("weight", 1.0) for criterion in criteria)
            
            for criterion in criteria:
                criterion_name = criterion["name"].lower()
                weight = criterion.get("weight", 1.0)
                
                # Map criterion to content data
                if criterion_name == "quality":
                    score = content_data.get("quality_score", 0.5)
                elif criterion_name == "engagement":
                    score = content_data.get("engagement_score", 0.5)
                elif criterion_name == "creativity":
                    score = content_data.get("creativity_score", 0.5)
                elif criterion_name == "speed":
                    # Score based on time efficiency
                    time_limit = content_data.get("time_limit_minutes", 60)
                    actual_time = content_data.get("creation_time_minutes", time_limit)
                    score = max(0, (time_limit - actual_time) / time_limit)
                elif criterion_name == "innovation":
                    score = content_data.get("innovation_score", 0.5)
                elif criterion_name == "teamwork":
                    score = content_data.get("teamwork_score", 0.5)
                elif criterion_name == "seasonal relevance":
                    score = content_data.get("seasonal_relevance_score", 0.5)
                else:
                    score = 0.5  # Default score
                
                total_score += score * weight
            
            # Normalize to 0-100 scale
            final_score = (total_score / total_weight) * 100
            
            return round(final_score, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating submission score: {e}")
            return 0.0
    
    async def _update_competition_leaderboard(self, competition_id: str):
        """Update the leaderboard for a competition."""
        try:
            if competition_id not in self.leaderboards:
                return
            
            leaderboard = self.leaderboards[competition_id]
            participants = self.participants[competition_id]
            
            # Sort participants by score (descending)
            participants.sort(key=lambda p: p.current_score, reverse=True)
            
            # Update ranks
            for i, participant in enumerate(participants):
                participant.current_rank = i + 1
            
            # Update leaderboard
            leaderboard.participants = participants.copy()
            leaderboard.last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error updating leaderboard: {e}")
    
    async def get_competition_leaderboard(
        self,
        competition_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get competition leaderboard."""
        try:
            if competition_id not in self.competitions:
                return {"error": "Competition not found"}
            
            competition = self.competitions[competition_id]
            leaderboard = self.leaderboards.get(competition_id)
            
            if not leaderboard:
                return {"error": "Leaderboard not found"}
            
            # Format leaderboard data
            leaderboard_data = []
            for participant in leaderboard.participants[:limit]:
                participant_data = {
                    "rank": participant.current_rank,
                    "participant_id": participant.id,
                    "user_id": participant.user_id,
                    "team_id": participant.team_id,
                    "score": participant.current_score,
                    "submissions_count": len(participant.submissions),
                    "registration_date": participant.registration_date
                }
                leaderboard_data.append(participant_data)
            
            return {
                "competition_id": competition_id,
                "competition_title": competition.title,
                "competition_status": competition.status.value,
                "leaderboard": leaderboard_data,
                "total_participants": len(leaderboard.participants),
                "last_updated": leaderboard.last_updated,
                "prizes": [
                    {
                        "rank_range": prize.rank_range,
                        "description": prize.description,
                        "prize_type": prize.prize_type,
                        "value": prize.value
                    } for prize in competition.prizes
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting competition leaderboard: {e}")
            return {"error": str(e)}
    
    async def get_user_competitions(self, user_id: str) -> Dict[str, Any]:
        """Get competitions for a specific user."""
        try:
            user_competitions = {
                "active": [],
                "completed": [],
                "upcoming": []
            }
            
            for competition_id, competition in self.competitions.items():
                # Check if user is participating
                user_participant = None
                for participant in self.participants.get(competition_id, []):
                    if participant.user_id == user_id:
                        user_participant = participant
                        break
                
                if user_participant:
                    competition_data = {
                        "id": competition.id,
                        "title": competition.title,
                        "description": competition.description,
                        "type": competition.competition_type.value,
                        "status": competition.status.value,
                        "start_date": competition.competition_start,
                        "end_date": competition.competition_end,
                        "participant_data": {
                            "current_score": user_participant.current_score,
                            "current_rank": user_participant.current_rank,
                            "submissions": len(user_participant.submissions),
                            "max_submissions": competition.rules.max_submissions_per_participant
                        },
                        "prizes": [
                            {
                                "rank_range": prize.rank_range,
                                "description": prize.description
                            } for prize in competition.prizes
                        ]
                    }
                    
                    if competition.status == CompetitionStatus.ACTIVE:
                        user_competitions["active"].append(competition_data)
                    elif competition.status == CompetitionStatus.COMPLETED:
                        user_competitions["completed"].append(competition_data)
                else:
                    # Available competitions
                    if (competition.status in [CompetitionStatus.UPCOMING, CompetitionStatus.REGISTRATION] and
                        datetime.utcnow() <= competition.registration_end):
                        
                        competition_data = {
                            "id": competition.id,
                            "title": competition.title,
                            "description": competition.description,
                            "type": competition.competition_type.value,
                            "registration_end": competition.registration_end,
                            "start_date": competition.competition_start,
                            "participants": competition.current_participants,
                            "max_participants": competition.max_participants,
                            "entry_fee": competition.entry_fee,
                            "tags": competition.tags
                        }
                        user_competitions["upcoming"].append(competition_data)
            
            return user_competitions
            
        except Exception as e:
            self.logger.error(f"Error getting user competitions: {e}")
            return {}
    
    async def _manage_competition_lifecycle(self):
        """Background task to manage competition lifecycle."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                
                for competition in self.competitions.values():
                    # Update status based on timestamps
                    if (competition.status == CompetitionStatus.UPCOMING and 
                        current_time >= competition.registration_start):
                        competition.status = CompetitionStatus.REGISTRATION
                        self.logger.info(f"Competition {competition.title} opened for registration")
                    
                    elif (competition.status == CompetitionStatus.REGISTRATION and 
                          current_time >= competition.competition_start):
                        competition.status = CompetitionStatus.ACTIVE
                        self.logger.info(f"Competition {competition.title} started")
                    
                    elif (competition.status == CompetitionStatus.ACTIVE and 
                          current_time >= competition.competition_end):
                        competition.status = CompetitionStatus.COMPLETED
                        await self._finalize_competition(competition.id)
                        self.logger.info(f"Competition {competition.title} completed")
                
            except Exception as e:
                self.logger.error(f"Error in competition lifecycle management: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _finalize_competition(self, competition_id: str):
        """Finalize a completed competition."""
        try:
            competition = self.competitions[competition_id]
            participants = self.participants[competition_id]
            
            # Final leaderboard update
            await self._update_competition_leaderboard(competition_id)
            
            # Award prizes
            for participant in participants:
                for prize in competition.prizes:
                    min_rank, max_rank = prize.rank_range
                    if min_rank <= participant.current_rank <= max_rank:
                        await self._award_prize(participant, prize, competition)
            
            self.logger.info(f"Finalized competition {competition.title}")
            
        except Exception as e:
            self.logger.error(f"Error finalizing competition: {e}")
    
    async def _award_prize(
        self,
        participant: CompetitionParticipant,
        prize: CompetitionPrize,
        competition: Competition
    ):
        """Award a prize to a participant."""
        try:
            # This would integrate with reward distribution system
            self.logger.info(f"Awarded prize '{prize.description}' to participant {participant.user_id} for {competition.title}")
            
        except Exception as e:
            self.logger.error(f"Error awarding prize: {e}")
    
    async def _update_leaderboards(self):
        """Background task to update all competition leaderboards."""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                for competition_id in self.competitions:
                    competition = self.competitions[competition_id]
                    if competition.status == CompetitionStatus.ACTIVE:
                        await self._update_competition_leaderboard(competition_id)
                
            except Exception as e:
                self.logger.error(f"Error updating leaderboards: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _process_scheduled_events(self):
        """Background task to process scheduled competition events."""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Process any scheduled events (tournament rounds, eliminations, etc.)
                current_time = datetime.utcnow()
                
                for event in self.scheduled_events[:]:
                    if current_time >= event["scheduled_time"]:
                        await self._process_event(event)
                        self.scheduled_events.remove(event)
                
            except Exception as e:
                self.logger.error(f"Error processing scheduled events: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process a scheduled competition event."""
        try:
            event_type = event["type"]
            
            if event_type == "elimination_round":
                await self._process_elimination_round(event["competition_id"], event["round_number"])
            elif event_type == "final_judging":
                await self._process_final_judging(event["competition_id"])
            elif event_type == "auto_complete":
                await self._finalize_competition(event["competition_id"])
            
        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
    
    async def _process_elimination_round(self, competition_id: str, round_number: int):
        """Process an elimination round for bracket competitions."""
        try:
            # This would implement bracket-style elimination logic
            self.logger.info(f"Processing elimination round {round_number} for competition {competition_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing elimination round: {e}")
    
    async def _process_final_judging(self, competition_id: str):
        """Process final judging for judge-reviewed competitions."""
        try:
            # This would implement judge scoring aggregation
            self.logger.info(f"Processing final judging for competition {competition_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing final judging: {e}")
    
    async def get_competition_statistics(self) -> Dict[str, Any]:
        """Get comprehensive competition system statistics."""
        try:
            total_competitions = len(self.competitions)
            active_competitions = len([c for c in self.competitions.values() if c.status == CompetitionStatus.ACTIVE])
            
            # Participation statistics
            total_participants = sum(len(participants) for participants in self.participants.values())
            total_submissions = sum(len(submissions) for submissions in self.submissions.values())
            
            # Competition type distribution
            type_distribution = {}
            for competition in self.competitions.values():
                comp_type = competition.competition_type.value
                type_distribution[comp_type] = type_distribution.get(comp_type, 0) + 1
            
            return {
                "total_competitions": total_competitions,
                "active_competitions": active_competitions,
                "completed_competitions": len([c for c in self.competitions.values() if c.status == CompetitionStatus.COMPLETED]),
                "total_participants": total_participants,
                "total_submissions": total_submissions,
                "average_participants_per_competition": total_participants / total_competitions if total_competitions > 0 else 0,
                "type_distribution": type_distribution,
                "templates_available": len(self.competition_templates)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting competition statistics: {e}")
            return {}