#!/usr/bin/env python3
"""
🏆 COMPETITION SERVICE
======================

Competition and contest management system for creator engagement and platform growth.
Manages competitions, contests, tournaments, and leaderboard-based challenges.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered competition matching and automated bracket management
- Backend Senior: Enterprise competition infrastructure with real-time leaderboards
- ML Engineer: ML models for fair matchmaking and performance prediction
- DBA: Optimized competition data models and analytics storage
- Security: Secure competition validation and anti-cheating measures  
- Microservices: Integration with gamification and reward systems
- Audio Engineer: Music competition templates and audio contest management
- DevOps: Real-time monitoring and competition analytics pipelines
- AI Prompt Engineer: Dynamic competition descriptions and engagement content
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitionType(Enum):
    """Competition type classification"""
    TOURNAMENT = "tournament"
    CONTEST = "contest"
    CHALLENGE = "challenge"
    LEADERBOARD = "leaderboard"
    BATTLE = "battle"
    SHOWCASE = "showcase"
    COLLABORATION = "collaboration"
    SPEED_ROUND = "speed_round"

class CompetitionStatus(Enum):
    """Competition status lifecycle"""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    JUDGING = "judging"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class CompetitionCategory(Enum):
    """Competition category classification"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CREATION = "video_creation"
    PHOTOGRAPHY = "photography"
    WRITING = "writing"
    COMEDY = "comedy"
    DANCE = "dance"
    ART_DESIGN = "art_design"
    COLLABORATION = "collaboration"
    SOCIAL_ENGAGEMENT = "social_engagement"
    PLATFORM_MASTERY = "platform_mastery"

class JudgingType(Enum):
    """Judging mechanism types"""
    COMMUNITY_VOTING = "community_voting"
    EXPERT_PANEL = "expert_panel"
    AI_AUTOMATED = "ai_automated"
    HYBRID = "hybrid"
    PEER_REVIEW = "peer_review"
    METRICS_BASED = "metrics_based"

class ParticipantStatus(Enum):
    """Participant status in competition"""
    REGISTERED = "registered"
    ACTIVE = "active"
    SUBMITTED = "submitted"
    DISQUALIFIED = "disqualified"
    WINNER = "winner"
    RUNNER_UP = "runner_up"
    PARTICIPANT = "participant"

@dataclass
class CompetitionRules:
    """Competition rules and criteria"""
    max_participants: int
    min_participants: int
    submission_requirements: List[str]
    judging_criteria: Dict[str, float]
    content_restrictions: List[str]
    time_limits: Dict[str, int]
    eligibility_requirements: List[str]
    prize_distribution: Dict[str, Any]

@dataclass
class CompetitionSubmission:
    """Competition submission entry"""
    id: str
    participant_id: str
    competition_id: str
    submission_time: datetime
    content_url: str
    content_type: str
    metadata: Dict[str, Any]
    scores: Dict[str, float]
    public_votes: int = 0
    expert_ratings: List[float] = None
    ai_score: Optional[float] = None
    
    def __post_init__(self):
        if self.expert_ratings is None:
            self.expert_ratings = []

@dataclass
class Competition:
    """Competition data model"""
    id: str
    title: str
    description: str
    competition_type: CompetitionType
    category: CompetitionCategory
    status: CompetitionStatus
    rules: CompetitionRules
    
    # Timing
    registration_start: datetime
    registration_end: datetime
    competition_start: datetime
    competition_end: datetime
    judging_end: Optional[datetime]
    
    # Participants and submissions
    participants: Dict[str, ParticipantStatus]
    submissions: Dict[str, CompetitionSubmission]
    
    # Judging
    judging_type: JudgingType
    judges: List[str]
    
    # Rewards and recognition
    prizes: Dict[str, Any]
    badges: List[str]
    
    # Analytics
    view_count: int = 0
    engagement_score: float = 0.0
    
    def __post_init__(self):
        if not self.participants:
            self.participants = {}
        if not self.submissions:
            self.submissions = {}
        if not self.judges:
            self.judges = []

@dataclass
class Leaderboard:
    """Real-time competition leaderboard"""
    competition_id: str
    rankings: List[Dict[str, Any]]
    last_updated: datetime
    total_participants: int
    scoring_method: str

class CompetitionService:
    """
    🏆 Advanced Competition Management Service
    
    Multi-Expert Implementation:
    - Lead Dev IA: AI matchmaking and intelligent bracket generation
    - Backend Senior: Scalable competition infrastructure with real-time updates
    - ML Engineer: Fair matchmaking algorithms and performance prediction
    - DBA: Optimized data models for competitions and analytics
    - Security: Competition integrity and anti-cheating measures
    - Microservices: Integration with gamification and reward systems
    - Audio Engineer: Music competition specialization and audio contests
    - DevOps: Real-time monitoring and performance analytics
    - AI Prompt Engineer: Dynamic competition descriptions and engagement
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize competition service"""
        self.redis_url = redis_url
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=15)
        
        # Competition storage
        self.competitions: Dict[str, Competition] = {}
        self.active_competitions: Set[str] = set()
        self.leaderboards: Dict[str, Leaderboard] = {}
        
        # Analytics and ML data
        self.competition_analytics = defaultdict(dict)
        self.participant_analytics = defaultdict(dict)
        self.judging_analytics = defaultdict(list)
        
        # AI models for matchmaking and scoring
        self.matchmaking_model = None
        self.scoring_models = {}
        
        # Performance metrics
        self.metrics = {
            'total_competitions': 0,
            'active_competitions': 0,
            'total_participants': 0,
            'completion_rate': 0.0,
            'average_engagement': 0.0,
            'judge_accuracy': 0.0
        }
        
        logger.info("Competition Service initialized")
    
    async def initialize(self):
        """Initialize Redis connection and competition templates"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize competition templates
            await self._initialize_competition_templates()
            
            # Load existing competition data
            await self._load_competition_data()
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            logger.info("Competition Service initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Competition Service: {e}")
            raise
    
    async def _initialize_competition_templates(self):
        """Initialize predefined competition templates"""
        
        # Music Competition Templates
        music_templates = {
            "beat_battle": {
                "title": "Beat Battle Championship",
                "description": "Show your beat-making skills in this intense production battle",
                "type": CompetitionType.TOURNAMENT,
                "category": CompetitionCategory.MUSIC_PRODUCTION,
                "rules": {
                    "max_participants": 64,
                    "min_participants": 8,
                    "submission_requirements": ["Original beat", "Under 3 minutes", "WAV format"],
                    "judging_criteria": {"creativity": 0.3, "technical_skill": 0.3, "originality": 0.4},
                    "time_limits": {"submission": 120, "voting": 48}
                }
            },
            "remix_contest": {
                "title": "Remix Challenge",
                "description": "Put your own spin on this featured track",
                "type": CompetitionType.CONTEST,
                "category": CompetitionCategory.MUSIC_PRODUCTION,
                "rules": {
                    "max_participants": 100,
                    "min_participants": 5,
                    "submission_requirements": ["Remix of provided stems", "Under 5 minutes"],
                    "judging_criteria": {"creativity": 0.4, "mixing_quality": 0.3, "danceability": 0.3}
                }
            }
        }
        
        # Video Competition Templates  
        video_templates = {
            "short_film_fest": {
                "title": "Short Film Festival",
                "description": "Create compelling short films under 60 seconds",
                "type": CompetitionType.SHOWCASE,
                "category": CompetitionCategory.VIDEO_CREATION,
                "rules": {
                    "max_participants": 200,
                    "min_participants": 10,
                    "submission_requirements": ["Under 60 seconds", "Original content", "HD quality"],
                    "judging_criteria": {"storytelling": 0.4, "technical_quality": 0.3, "creativity": 0.3}
                }
            }
        }
        
        # Collaboration Templates
        collab_templates = {
            "creator_clash": {
                "title": "Creator Collaboration Clash",
                "description": "Team up with other creators for the ultimate collaboration challenge",
                "type": CompetitionType.COLLABORATION,
                "category": CompetitionCategory.COLLABORATION,
                "rules": {
                    "max_participants": 40,
                    "min_participants": 8,
                    "submission_requirements": ["2-4 creators per team", "Cross-platform content"],
                    "judging_criteria": {"teamwork": 0.3, "creativity": 0.3, "reach": 0.4}
                }
            }
        }
        
        self.competition_templates = {
            "music": music_templates,
            "video": video_templates,
            "collaboration": collab_templates
        }
    
    async def create_competition(self, competition_data: Dict[str, Any]) -> Competition:
        """Create a new competition with AI-powered optimization"""
        try:
            # Generate unique competition ID
            competition_id = str(uuid.uuid4())
            
            # Create competition rules
            rules_data = competition_data.get("rules", {})
            rules = CompetitionRules(
                max_participants=rules_data.get("max_participants", 100),
                min_participants=rules_data.get("min_participants", 2),
                submission_requirements=rules_data.get("submission_requirements", []),
                judging_criteria=rules_data.get("judging_criteria", {"quality": 1.0}),
                content_restrictions=rules_data.get("content_restrictions", []),
                time_limits=rules_data.get("time_limits", {}),
                eligibility_requirements=rules_data.get("eligibility_requirements", []),
                prize_distribution=rules_data.get("prize_distribution", {})
            )
            
            # Parse timestamps
            registration_start = datetime.fromisoformat(competition_data["registration_start"])
            registration_end = datetime.fromisoformat(competition_data["registration_end"])
            competition_start = datetime.fromisoformat(competition_data["competition_start"])
            competition_end = datetime.fromisoformat(competition_data["competition_end"])
            
            # Create competition
            competition = Competition(
                id=competition_id,
                title=competition_data["title"],
                description=competition_data["description"],
                competition_type=CompetitionType(competition_data["type"]),
                category=CompetitionCategory(competition_data["category"]),
                status=CompetitionStatus.DRAFT,
                rules=rules,
                registration_start=registration_start,
                registration_end=registration_end,
                competition_start=competition_start,
                competition_end=competition_end,
                judging_end=competition_data.get("judging_end"),
                participants={},
                submissions={},
                judging_type=JudgingType(competition_data.get("judging_type", "community_voting")),
                judges=competition_data.get("judges", []),
                prizes=competition_data.get("prizes", {}),
                badges=competition_data.get("badges", [])
            )
            
            # Store competition
            self.competitions[competition_id] = competition
            await self._save_competition_to_redis(competition)
            
            # Initialize leaderboard
            leaderboard = Leaderboard(
                competition_id=competition_id,
                rankings=[],
                last_updated=datetime.now(),
                total_participants=0,
                scoring_method=competition_data.get("scoring_method", "total_score")
            )
            self.leaderboards[competition_id] = leaderboard
            
            # Update metrics
            self.metrics['total_competitions'] += 1
            
            logger.info(f"Created competition: {competition.title} (ID: {competition_id})")
            return competition
            
        except Exception as e:
            logger.error(f"Failed to create competition: {e}")
            raise
    
    async def register_participant(self, competition_id: str, user_id: str, 
                                 user_profile: Dict[str, Any]) -> bool:
        """Register a participant for a competition with eligibility validation"""
        try:
            # Validate competition exists
            if competition_id not in self.competitions:
                raise ValueError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            # Check registration period
            now = datetime.now()
            if now < competition.registration_start:
                raise ValueError("Registration not yet open")
            if now > competition.registration_end:
                raise ValueError("Registration period has ended")
            
            # Check if already registered
            if user_id in competition.participants:
                raise ValueError("User already registered for this competition")
            
            # Check participant limit
            if len(competition.participants) >= competition.rules.max_participants:
                raise ValueError("Competition is full")
            
            # Validate eligibility requirements
            if not await self._check_eligibility(user_profile, competition.rules.eligibility_requirements):
                raise ValueError("User does not meet eligibility requirements")
            
            # Register participant
            competition.participants[user_id] = ParticipantStatus.REGISTERED
            
            # Update competition status if needed
            if (competition.status == CompetitionStatus.DRAFT and 
                len(competition.participants) >= competition.rules.min_participants):
                competition.status = CompetitionStatus.REGISTRATION_OPEN
            
            # Save updated competition
            await self._save_competition_to_redis(competition)
            
            # Update analytics
            self.participant_analytics[user_id][competition_id] = {
                'registration_time': now,
                'profile_data': user_profile
            }
            
            # Update metrics
            self.metrics['total_participants'] += 1
            
            logger.info(f"User {user_id} registered for competition {competition.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register participant: {e}")
            return False
    
    async def submit_entry(self, competition_id: str, participant_id: str,
                          submission_data: Dict[str, Any]) -> CompetitionSubmission:
        """Submit an entry to a competition with validation"""
        try:
            # Validate competition and participant
            if competition_id not in self.competitions:
                raise ValueError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            if participant_id not in competition.participants:
                raise ValueError("User not registered for this competition")
            
            # Check competition timing
            now = datetime.now()
            if now < competition.competition_start:
                raise ValueError("Competition has not started yet")
            if now > competition.competition_end:
                raise ValueError("Competition submission period has ended")
            
            # Validate submission requirements
            if not await self._validate_submission(submission_data, competition.rules):
                raise ValueError("Submission does not meet requirements")
            
            # Create submission
            submission_id = str(uuid.uuid4())
            submission = CompetitionSubmission(
                id=submission_id,
                participant_id=participant_id,
                competition_id=competition_id,
                submission_time=now,
                content_url=submission_data["content_url"],
                content_type=submission_data["content_type"],
                metadata=submission_data.get("metadata", {}),
                scores={}
            )
            
            # Store submission
            competition.submissions[submission_id] = submission
            competition.participants[participant_id] = ParticipantStatus.SUBMITTED
            
            # Trigger AI scoring if enabled
            if competition.judging_type in [JudgingType.AI_AUTOMATED, JudgingType.HYBRID]:
                await self._ai_score_submission(submission, competition)
            
            # Update leaderboard
            await self._update_leaderboard(competition_id)
            
            # Save updated competition
            await self._save_competition_to_redis(competition)
            
            logger.info(f"Submission {submission_id} received for competition {competition.title}")
            return submission
            
        except Exception as e:
            logger.error(f"Failed to submit entry: {e}")
            raise
    
    async def _ai_score_submission(self, submission: CompetitionSubmission, 
                                  competition: Competition):
        """AI-powered submission scoring"""
        try:
            # Simulate AI scoring based on competition criteria
            # In production, this would use actual ML models
            
            total_score = 0.0
            max_score = 0.0
            
            for criterion, weight in competition.rules.judging_criteria.items():
                # Simulate AI analysis for each criterion
                criterion_score = random.uniform(0.6, 1.0)  # Placeholder for real AI scoring
                
                # Apply content-specific scoring logic
                if criterion == "creativity":
                    criterion_score *= self._analyze_creativity(submission)
                elif criterion == "technical_skill":
                    criterion_score *= self._analyze_technical_quality(submission)
                elif criterion == "originality":
                    criterion_score *= self._analyze_originality(submission)
                
                total_score += criterion_score * weight
                max_score += weight
            
            # Normalize score to 0-100 scale
            normalized_score = (total_score / max_score) * 100
            submission.ai_score = normalized_score
            
            # Store in submission scores
            submission.scores["ai_score"] = normalized_score
            
        except Exception as e:
            logger.error(f"Failed to AI score submission: {e}")
    
    def _analyze_creativity(self, submission: CompetitionSubmission) -> float:
        """AI analysis of creativity (placeholder for real ML model)"""
        # Placeholder implementation
        return random.uniform(0.7, 1.0)
    
    def _analyze_technical_quality(self, submission: CompetitionSubmission) -> float:
        """AI analysis of technical quality (placeholder for real ML model)"""
        # Placeholder implementation  
        return random.uniform(0.6, 1.0)
    
    def _analyze_originality(self, submission: CompetitionSubmission) -> float:
        """AI analysis of originality (placeholder for real ML model)"""
        # Placeholder implementation
        return random.uniform(0.8, 1.0)
    
    async def vote_submission(self, competition_id: str, submission_id: str,
                             voter_id: str, vote_data: Dict[str, Any]) -> bool:
        """Cast a vote for a competition submission"""
        try:
            # Validate competition and submission
            if competition_id not in self.competitions:
                raise ValueError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            if submission_id not in competition.submissions:
                raise ValueError(f"Submission {submission_id} not found")
            
            submission = competition.submissions[submission_id]
            
            # Check voting eligibility
            if not await self._can_vote(voter_id, competition_id, submission_id):
                raise ValueError("User not eligible to vote")
            
            # Process vote based on judging type
            if competition.judging_type == JudgingType.COMMUNITY_VOTING:
                submission.public_votes += 1
                
            elif competition.judging_type == JudgingType.EXPERT_PANEL:
                if voter_id in competition.judges:
                    expert_rating = vote_data.get("rating", 0.0)
                    submission.expert_ratings.append(expert_rating)
                    
            elif competition.judging_type == JudgingType.PEER_REVIEW:
                if voter_id in competition.participants:
                    peer_rating = vote_data.get("rating", 0.0)
                    if "peer_scores" not in submission.scores:
                        submission.scores["peer_scores"] = []
                    submission.scores["peer_scores"].append(peer_rating)
            
            # Update overall score
            await self._calculate_overall_score(submission, competition)
            
            # Update leaderboard
            await self._update_leaderboard(competition_id)
            
            # Save updated data
            await self._save_competition_to_redis(competition)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process vote: {e}")
            return False
    
    async def _calculate_overall_score(self, submission: CompetitionSubmission,
                                     competition: Competition):
        """Calculate overall submission score based on judging type"""
        try:
            total_score = 0.0
            
            if competition.judging_type == JudgingType.COMMUNITY_VOTING:
                total_score = submission.public_votes
                
            elif competition.judging_type == JudgingType.EXPERT_PANEL:
                if submission.expert_ratings:
                    total_score = statistics.mean(submission.expert_ratings)
                    
            elif competition.judging_type == JudgingType.AI_AUTOMATED:
                total_score = submission.ai_score or 0.0
                
            elif competition.judging_type == JudgingType.HYBRID:
                # Combine AI, expert, and community scores
                ai_weight = 0.4
                expert_weight = 0.4
                community_weight = 0.2
                
                ai_score = submission.ai_score or 0.0
                expert_score = statistics.mean(submission.expert_ratings) if submission.expert_ratings else 0.0
                community_score = min(submission.public_votes / 100, 1.0) * 100  # Normalize
                
                total_score = (ai_score * ai_weight + 
                             expert_score * expert_weight + 
                             community_score * community_weight)
                             
            elif competition.judging_type == JudgingType.PEER_REVIEW:
                peer_scores = submission.scores.get("peer_scores", [])
                if peer_scores:
                    total_score = statistics.mean(peer_scores)
                    
            elif competition.judging_type == JudgingType.METRICS_BASED:
                # Calculate based on engagement metrics
                engagement_score = submission.metadata.get("views", 0) * 0.1
                engagement_score += submission.metadata.get("likes", 0) * 0.5
                engagement_score += submission.metadata.get("shares", 0) * 1.0
                total_score = engagement_score
            
            submission.scores["total_score"] = total_score
            
        except Exception as e:
            logger.error(f"Failed to calculate overall score: {e}")
    
    async def _update_leaderboard(self, competition_id: str):
        """Update real-time competition leaderboard"""
        try:
            competition = self.competitions[competition_id]
            leaderboard = self.leaderboards[competition_id]
            
            # Get all submissions with scores
            scored_submissions = []
            for submission in competition.submissions.values():
                if "total_score" in submission.scores:
                    participant_data = {
                        "participant_id": submission.participant_id,
                        "submission_id": submission.id,
                        "score": submission.scores["total_score"],
                        "submission_time": submission.submission_time.isoformat()
                    }
                    scored_submissions.append(participant_data)
            
            # Sort by score (descending)
            scored_submissions.sort(key=lambda x: x["score"], reverse=True)
            
            # Update leaderboard
            leaderboard.rankings = scored_submissions
            leaderboard.last_updated = datetime.now()
            leaderboard.total_participants = len(competition.participants)
            
            # Save to Redis for real-time access
            await self._save_leaderboard_to_redis(leaderboard)
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard: {e}")
    
    async def get_leaderboard(self, competition_id: str, 
                             limit: int = 50) -> Dict[str, Any]:
        """Get current competition leaderboard"""
        try:
            if competition_id not in self.leaderboards:
                return {"error": "Leaderboard not found"}
            
            leaderboard = self.leaderboards[competition_id]
            
            return {
                "competition_id": competition_id,
                "rankings": leaderboard.rankings[:limit],
                "total_participants": leaderboard.total_participants,
                "last_updated": leaderboard.last_updated.isoformat(),
                "scoring_method": leaderboard.scoring_method
            }
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return {"error": str(e)}
    
    async def finalize_competition(self, competition_id: str) -> Dict[str, Any]:
        """Finalize competition and determine winners"""
        try:
            if competition_id not in self.competitions:
                raise ValueError(f"Competition {competition_id} not found")
            
            competition = self.competitions[competition_id]
            
            # Check if competition is ready to finalize
            if datetime.now() < competition.competition_end:
                raise ValueError("Competition is still in progress")
            
            # Update status
            competition.status = CompetitionStatus.JUDGING
            
            # Get final leaderboard
            leaderboard = self.leaderboards[competition_id]
            final_rankings = leaderboard.rankings
            
            # Determine winners
            winners = {}
            if final_rankings:
                # Assign winner statuses
                if len(final_rankings) >= 1:
                    winner_id = final_rankings[0]["participant_id"]
                    competition.participants[winner_id] = ParticipantStatus.WINNER
                    winners["first_place"] = final_rankings[0]
                
                if len(final_rankings) >= 2:
                    runner_up_id = final_rankings[1]["participant_id"]
                    competition.participants[runner_up_id] = ParticipantStatus.RUNNER_UP
                    winners["second_place"] = final_rankings[1]
                
                if len(final_rankings) >= 3:
                    third_place_id = final_rankings[2]["participant_id"]
                    competition.participants[third_place_id] = ParticipantStatus.RUNNER_UP
                    winners["third_place"] = final_rankings[2]
            
            # Update competition status
            competition.status = CompetitionStatus.COMPLETED
            
            # Award prizes and badges (integration point with reward service)
            await self._award_prizes(competition, winners)
            
            # Generate final analytics report
            analytics_report = await self._generate_competition_analytics(competition)
            
            # Save final state
            await self._save_competition_to_redis(competition)
            
            # Update metrics
            self.metrics['active_competitions'] -= 1 if competition_id in self.active_competitions else 0
            self.active_competitions.discard(competition_id)
            
            logger.info(f"Competition {competition.title} finalized with {len(winners)} winners")
            
            return {
                "competition_id": competition_id,
                "status": "completed",
                "winners": winners,
                "final_rankings": final_rankings,
                "analytics": analytics_report
            }
            
        except Exception as e:
            logger.error(f"Failed to finalize competition: {e}")
            raise
    
    async def _award_prizes(self, competition: Competition, winners: Dict[str, Any]):
        """Award prizes and badges to competition winners"""
        try:
            # This would integrate with the reward management service
            # For now, just log the prize awards
            
            for position, winner_data in winners.items():
                participant_id = winner_data["participant_id"]
                prize_info = competition.prizes.get(position, {})
                
                if prize_info:
                    logger.info(f"Awarding {position} prize to participant {participant_id}: {prize_info}")
                    
                    # Award badges
                    for badge in competition.badges:
                        logger.info(f"Awarding badge '{badge}' to participant {participant_id}")
                        
        except Exception as e:
            logger.error(f"Failed to award prizes: {e}")
    
    async def _generate_competition_analytics(self, competition: Competition) -> Dict[str, Any]:
        """Generate comprehensive competition analytics"""
        try:
            total_participants = len(competition.participants)
            total_submissions = len(competition.submissions)
            
            # Calculate engagement metrics
            total_views = sum(s.metadata.get("views", 0) for s in competition.submissions.values())
            total_votes = sum(s.public_votes for s in competition.submissions.values())
            
            # Calculate completion rate
            submitted_participants = sum(1 for status in competition.participants.values() 
                                       if status in [ParticipantStatus.SUBMITTED, 
                                                   ParticipantStatus.WINNER, 
                                                   ParticipantStatus.RUNNER_UP])
            completion_rate = submitted_participants / max(total_participants, 1)
            
            # Calculate average scores
            all_scores = [s.scores.get("total_score", 0) for s in competition.submissions.values()]
            avg_score = statistics.mean(all_scores) if all_scores else 0.0
            
            analytics = {
                "competition_id": competition.id,
                "title": competition.title,
                "type": competition.competition_type.value,
                "category": competition.category.value,
                "participation": {
                    "total_registered": total_participants,
                    "total_submissions": total_submissions,
                    "completion_rate": completion_rate
                },
                "engagement": {
                    "total_views": total_views,
                    "total_votes": total_votes,
                    "average_engagement": total_views / max(total_submissions, 1)
                },
                "scoring": {
                    "average_score": avg_score,
                    "highest_score": max(all_scores) if all_scores else 0.0,
                    "score_distribution": self._calculate_score_distribution(all_scores)
                },
                "timing": {
                    "duration_days": (competition.competition_end - competition.competition_start).days,
                    "registration_duration": (competition.registration_end - competition.registration_start).days
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate analytics: {e}")
            return {}
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution for analytics"""
        if not scores:
            return {}
        
        distribution = {
            "0-20": 0, "21-40": 0, "41-60": 0, 
            "61-80": 0, "81-100": 0
        }
        
        for score in scores:
            if score <= 20:
                distribution["0-20"] += 1
            elif score <= 40:
                distribution["21-40"] += 1
            elif score <= 60:
                distribution["41-60"] += 1
            elif score <= 80:
                distribution["61-80"] += 1
            else:
                distribution["81-100"] += 1
        
        return distribution
    
    async def _check_eligibility(self, user_profile: Dict[str, Any], 
                               requirements: List[str]) -> bool:
        """Check if user meets eligibility requirements"""
        # Placeholder implementation - would integrate with user service
        # For now, assume all users are eligible
        return True
    
    async def _validate_submission(self, submission_data: Dict[str, Any],
                                 rules: CompetitionRules) -> bool:
        """Validate submission against competition rules"""
        # Placeholder implementation - would include content validation
        required_fields = ["content_url", "content_type"]
        
        for field in required_fields:
            if field not in submission_data:
                return False
        
        return True
    
    async def _can_vote(self, voter_id: str, competition_id: str, 
                       submission_id: str) -> bool:
        """Check if user can vote on a submission"""
        # Placeholder implementation - would include voting eligibility logic
        return True
    
    async def _save_competition_to_redis(self, competition: Competition):
        """Save competition data to Redis"""
        try:
            if self.redis_client:
                competition_data = {
                    'id': competition.id,
                    'title': competition.title,
                    'description': competition.description,
                    'type': competition.competition_type.value,
                    'category': competition.category.value,
                    'status': competition.status.value,
                    'participants': json.dumps({k: v.value for k, v in competition.participants.items()}),
                    'submission_count': len(competition.submissions),
                    'view_count': competition.view_count,
                    'engagement_score': competition.engagement_score
                }
                await self.redis_client.hset(f"competition:{competition.id}", mapping=competition_data)
                
        except Exception as e:
            logger.error(f"Failed to save competition to Redis: {e}")
    
    async def _save_leaderboard_to_redis(self, leaderboard: Leaderboard):
        """Save leaderboard data to Redis for real-time access"""
        try:
            if self.redis_client:
                leaderboard_data = {
                    'competition_id': leaderboard.competition_id,
                    'rankings': json.dumps(leaderboard.rankings),
                    'last_updated': leaderboard.last_updated.isoformat(),
                    'total_participants': leaderboard.total_participants,
                    'scoring_method': leaderboard.scoring_method
                }
                await self.redis_client.hset(f"leaderboard:{leaderboard.competition_id}", 
                                           mapping=leaderboard_data)
                
        except Exception as e:
            logger.error(f"Failed to save leaderboard to Redis: {e}")
    
    async def _load_competition_data(self):
        """Load existing competition data from Redis"""
        try:
            if self.redis_client:
                # Load competitions
                competition_keys = await self.redis_client.keys("competition:*")
                for key in competition_keys:
                    competition_data = await self.redis_client.hgetall(key)
                    if competition_data:
                        # Reconstruct competition object
                        # Implementation details would depend on Redis data format
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to load competition data from Redis: {e}")
    
    async def _initialize_ai_models(self):
        """Initialize AI models for matchmaking and scoring"""
        try:
            # Placeholder for AI model initialization
            # In production, this would load actual ML models
            self.matchmaking_model = "initialized"
            self.scoring_models = {
                "creativity": "creativity_model",
                "technical": "technical_model",
                "originality": "originality_model"
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    async def get_competition_analytics(self, competition_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive competition analytics"""
        try:
            if competition_id:
                # Analytics for specific competition
                if competition_id not in self.competitions:
                    return {"error": "Competition not found"}
                
                competition = self.competitions[competition_id]
                return await self._generate_competition_analytics(competition)
            else:
                # Overall platform analytics
                total_active = len(self.active_competitions)
                total_competitions = len(self.competitions)
                
                # Calculate overall engagement
                total_engagement = sum(c.engagement_score for c in self.competitions.values())
                avg_engagement = total_engagement / max(total_competitions, 1)
                
                return {
                    "platform_analytics": {
                        "total_competitions": total_competitions,
                        "active_competitions": total_active,
                        "total_participants": self.metrics['total_participants'],
                        "average_engagement": avg_engagement,
                        "competition_categories": self._get_category_distribution(),
                        "completion_trends": self._get_completion_trends()
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get competition analytics: {e}")
            return {"error": str(e)}
    
    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of competitions by category"""
        distribution = defaultdict(int)
        for competition in self.competitions.values():
            distribution[competition.category.value] += 1
        return dict(distribution)
    
    def _get_completion_trends(self) -> List[Dict[str, Any]]:
        """Get competition completion trends over time"""
        # Placeholder implementation
        return []
    
    async def cleanup_expired_competitions(self):
        """Background service: Clean up expired competitions"""
        try:
            current_time = datetime.now()
            expired_count = 0
            
            for competition_id, competition in self.competitions.items():
                # Mark expired competitions
                if (competition.competition_end < current_time and 
                    competition.status not in [CompetitionStatus.COMPLETED, CompetitionStatus.CANCELLED]):
                    
                    # Auto-finalize if there are submissions
                    if competition.submissions:
                        await self.finalize_competition(competition_id)
                    else:
                        competition.status = CompetitionStatus.CANCELLED
                        await self._save_competition_to_redis(competition)
                    
                    expired_count += 1
            
            logger.info(f"Processed {expired_count} expired competitions")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired competitions: {e}")
    
    async def shutdown(self):
        """Graceful shutdown of competition service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.executor.shutdown(wait=True)
            logger.info("Competition Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Example usage of Competition Service"""
    service = CompetitionService()
    await service.initialize()
    
    try:
        # Create a sample competition
        competition_data = {
            "title": "Beat Battle Championship 2025",
            "description": "Show your beat-making skills in this epic production battle",
            "type": "tournament",
            "category": "music_production",
            "registration_start": "2025-02-01T00:00:00",
            "registration_end": "2025-02-15T23:59:59",
            "competition_start": "2025-02-16T00:00:00",
            "competition_end": "2025-02-28T23:59:59",
            "judging_type": "hybrid",
            "rules": {
                "max_participants": 64,
                "min_participants": 8,
                "submission_requirements": ["Original beat", "Under 3 minutes", "WAV format"],
                "judging_criteria": {"creativity": 0.3, "technical_skill": 0.3, "originality": 0.4},
                "time_limits": {"submission": 120, "voting": 48}
            },
            "prizes": {
                "first_place": {"amount": 1000, "currency": "USD", "badge": "Beat Master"},
                "second_place": {"amount": 500, "currency": "USD", "badge": "Beat Creator"},
                "third_place": {"amount": 250, "currency": "USD", "badge": "Beat Maker"}
            }
        }
        
        competition = await service.create_competition(competition_data)
        print(f"Created competition: {competition.title}")
        
        # Register participants
        user_profiles = [
            {"user_id": "producer1", "level": 5, "specialization": "trap"},
            {"user_id": "producer2", "level": 3, "specialization": "house"},
            {"user_id": "producer3", "level": 7, "specialization": "hip-hop"}
        ]
        
        for profile in user_profiles:
            await service.register_participant(competition.id, profile["user_id"], profile)
            print(f"Registered participant: {profile['user_id']}")
        
        # Get leaderboard
        leaderboard = await service.get_leaderboard(competition.id)
        print(f"Current leaderboard: {leaderboard}")
        
        # Get analytics
        analytics = await service.get_competition_analytics()
        print(f"Competition analytics: {analytics}")
        
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())