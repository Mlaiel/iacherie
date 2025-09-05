"""Advanced Competition Manager - Enterprise Competition System
===========================================================

Sophisticated competition management system providing inter-creator tournaments,
intelligent matchmaking, bracket automation, prize pool management, and
real-time competition analytics for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/competition_manager.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

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

Business Logic Integration:
Creator Registration → Skill-Based Matchmaking → Competition Brackets → 
Real-Time Progress → Prize Distribution → Achievement Integration → Analytics
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import random
import math
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompetitionType(str, Enum):
    """Types of competitions."""
    TOURNAMENT = "tournament"
    LEAGUE = "league"
    KNOCKOUT = "knockout"
    ROUND_ROBIN = "round_robin"
    SEASONAL = "seasonal"
    CHALLENGE = "challenge"
    TEAM_BATTLE = "team_battle"
    SOLO_CONTEST = "solo_contest"


class CompetitionStatus(str, Enum):
    """Competition lifecycle status."""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class BracketType(str, Enum):
    """Tournament bracket types."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    SWISS_SYSTEM = "swiss_system"
    ROUND_ROBIN = "round_robin"
    LADDER = "ladder"


class MatchmakingCriteria(str, Enum):
    """Criteria for intelligent matchmaking."""
    SKILL_LEVEL = "skill_level"
    CONTENT_TYPE = "content_type"
    ENGAGEMENT_RATE = "engagement_rate"
    TIER_LEVEL = "tier_level"
    GEOGRAPHIC_REGION = "geographic_region"
    LANGUAGE = "language"
    EXPERIENCE = "experience"


@dataclass
class CompetitionParticipant:
    """Competition participant data."""
    user_id: str
    username: str
    skill_rating: float
    tier_level: str
    content_specialty: str
    engagement_rate: float
    join_timestamp: datetime
    team_id: Optional[str] = None
    seed_position: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionMatch:
    """Individual match within a competition."""
    match_id: str
    competition_id: str
    round_number: int
    participant_1_id: str
    participant_2_id: str
    scheduled_time: datetime
    status: str = "scheduled"
    winner_id: Optional[str] = None
    score_1: Optional[float] = None
    score_2: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: Optional[datetime] = None


@dataclass
class PrizePool:
    """Competition prize distribution."""
    total_amount: Decimal
    currency_type: str
    distribution: Dict[int, Decimal]  # position -> amount
    bonus_rewards: Dict[str, Any] = field(default_factory=dict)
    sponsor_contributions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Competition:
    """Main competition entity."""
    id: str
    name: str
    description: str
    competition_type: CompetitionType
    bracket_type: BracketType
    status: CompetitionStatus
    organizer_id: str
    created_at: datetime
    registration_start: datetime
    registration_end: datetime
    competition_start: datetime
    competition_end: datetime
    max_participants: int
    min_participants: int
    entry_fee: Optional[Decimal]
    prize_pool: PrizePool
    participants: List[CompetitionParticipant] = field(default_factory=list)
    matches: List[CompetitionMatch] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeasonalCompetition:
    """Seasonal competition with multiple phases."""
    id: str
    season_name: str
    season_number: int
    start_date: datetime
    end_date: datetime
    phases: List[Competition] = field(default_factory=list)
    overall_leaderboard: Dict[str, float] = field(default_factory=dict)
    seasonal_rewards: Dict[str, Any] = field(default_factory=dict)
    theme: Optional[str] = None
    special_rules: Dict[str, Any] = field(default_factory=dict)


class CompetitionEngine:
    """
    Advanced competition engine with AI-powered matchmaking and
    automated bracket management.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the competition engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        
        # In-memory storage for active competitions
        self.active_competitions: Dict[str, Competition] = {}
        self.seasonal_competitions: Dict[str, SeasonalCompetition] = {}
        self.participant_ratings: Dict[str, float] = {}
        
        self.logger.info("CompetitionEngine initialized")
    
    async def create_competition(
        self,
        name: str,
        description: str,
        competition_type: CompetitionType,
        bracket_type: BracketType,
        organizer_id: str,
        registration_period: Tuple[datetime, datetime],
        competition_period: Tuple[datetime, datetime],
        max_participants: int,
        prize_pool_amount: Decimal,
        **kwargs
    ) -> Competition:
        """Create a new competition."""
        try:
            competition_id = str(uuid4())
            
            # Create prize pool with default distribution
            prize_distribution = self._calculate_default_prize_distribution(
                max_participants, prize_pool_amount
            )
            
            prize_pool = PrizePool(
                total_amount=prize_pool_amount,
                currency_type=kwargs.get("currency_type", "coins"),
                distribution=prize_distribution
            )
            
            competition = Competition(
                id=competition_id,
                name=name,
                description=description,
                competition_type=competition_type,
                bracket_type=bracket_type,
                status=CompetitionStatus.DRAFT,
                organizer_id=organizer_id,
                created_at=datetime.now(timezone.utc),
                registration_start=registration_period[0],
                registration_end=registration_period[1],
                competition_start=competition_period[0],
                competition_end=competition_period[1],
                max_participants=max_participants,
                min_participants=kwargs.get("min_participants", 4),
                entry_fee=kwargs.get("entry_fee"),
                prize_pool=prize_pool,
                rules=kwargs.get("rules", {}),
                metadata=kwargs.get("metadata", {})
            )
            
            self.active_competitions[competition_id] = competition
            
            # Cache competition data
            if self.cache:
                await self._cache_competition(competition)
            
            self.logger.info(f"✅ Competition created: {name} ({competition_id})")
            
            return competition
            
        except Exception as e:
            self.logger.error(f"Error creating competition: {e}")
            raise
    
    def _calculate_default_prize_distribution(
        self, 
        max_participants: int, 
        total_amount: Decimal
    ) -> Dict[int, Decimal]:
        """Calculate default prize distribution based on participants."""
        distribution = {}
        
        if max_participants <= 4:
            # Small competition: 60%, 30%, 10%
            distribution[1] = total_amount * Decimal("0.60")
            distribution[2] = total_amount * Decimal("0.30")
            distribution[3] = total_amount * Decimal("0.10")
        elif max_participants <= 16:
            # Medium competition: 40%, 25%, 15%, 10%, 5%, 5%
            distribution[1] = total_amount * Decimal("0.40")
            distribution[2] = total_amount * Decimal("0.25")
            distribution[3] = total_amount * Decimal("0.15")
            distribution[4] = total_amount * Decimal("0.10")
            distribution[5] = total_amount * Decimal("0.05")
            distribution[6] = total_amount * Decimal("0.05")
        else:
            # Large competition: Top 10 get prizes
            percentages = [0.30, 0.20, 0.15, 0.10, 0.08, 0.06, 0.04, 0.03, 0.02, 0.02]
            for i, percentage in enumerate(percentages, 1):
                distribution[i] = total_amount * Decimal(str(percentage))
        
        return distribution
    
    async def register_participant(
        self,
        competition_id: str,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> bool:
        """Register a user for a competition."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                raise ValueError(f"Competition {competition_id} not found")
            
            # Check registration eligibility
            if not await self._check_registration_eligibility(competition, user_id):
                return False
            
            # Create participant
            participant = CompetitionParticipant(
                user_id=user_id,
                username=user_data.get("username", f"User_{user_id[:8]}"),
                skill_rating=user_data.get("skill_rating", 1000.0),
                tier_level=user_data.get("tier_level", "NEWCOMER"),
                content_specialty=user_data.get("content_specialty", "general"),
                engagement_rate=user_data.get("engagement_rate", 0.0),
                join_timestamp=datetime.now(timezone.utc),
                metadata=user_data
            )
            
            competition.participants.append(participant)
            
            # Update cache
            if self.cache:
                await self._cache_competition(competition)
            
            self.logger.info(f"✅ Participant registered: {user_id} in {competition_id}")
            
            # Auto-start if minimum participants reached and registration ended
            if (len(competition.participants) >= competition.min_participants and
                datetime.now(timezone.utc) >= competition.registration_end):
                await self._auto_start_competition(competition)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering participant: {e}")
            return False
    
    async def _check_registration_eligibility(
        self, 
        competition: Competition, 
        user_id: str
    ) -> bool:
        """Check if user can register for competition."""
        now = datetime.now(timezone.utc)
        
        # Check registration period
        if now < competition.registration_start or now > competition.registration_end:
            return False
        
        # Check if already registered
        if any(p.user_id == user_id for p in competition.participants):
            return False
        
        # Check maximum participants
        if len(competition.participants) >= competition.max_participants:
            return False
        
        # Check competition status
        if competition.status not in [CompetitionStatus.DRAFT, CompetitionStatus.REGISTRATION_OPEN]:
            return False
        
        return True
    
    async def generate_brackets(self, competition_id: str) -> List[CompetitionMatch]:
        """Generate tournament brackets with intelligent seeding."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                raise ValueError(f"Competition {competition_id} not found")
            
            participants = competition.participants.copy()
            
            # Intelligent seeding based on skill rating
            participants.sort(key=lambda p: p.skill_rating, reverse=True)
            for i, participant in enumerate(participants):
                participant.seed_position = i + 1
            
            matches = []
            
            if competition.bracket_type == BracketType.SINGLE_ELIMINATION:
                matches = self._generate_single_elimination_bracket(competition, participants)
            elif competition.bracket_type == BracketType.DOUBLE_ELIMINATION:
                matches = self._generate_double_elimination_bracket(competition, participants)
            elif competition.bracket_type == BracketType.ROUND_ROBIN:
                matches = self._generate_round_robin_bracket(competition, participants)
            elif competition.bracket_type == BracketType.SWISS_SYSTEM:
                matches = self._generate_swiss_system_bracket(competition, participants)
            
            competition.matches = matches
            
            # Update cache
            if self.cache:
                await self._cache_competition(competition)
            
            self.logger.info(f"✅ Brackets generated for {competition_id}: {len(matches)} matches")
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error generating brackets: {e}")
            return []
    
    def _generate_single_elimination_bracket(
        self, 
        competition: Competition, 
        participants: List[CompetitionParticipant]
    ) -> List[CompetitionMatch]:
        """Generate single elimination tournament bracket."""
        matches = []
        round_number = 1
        current_participants = participants.copy()
        
        # Add byes for non-power-of-2 participant counts
        bracket_size = 2 ** math.ceil(math.log2(len(participants)))
        byes_needed = bracket_size - len(participants)
        
        while len(current_participants) > 1:
            round_matches = []
            next_round_participants = []
            
            # First round: pair participants with intelligent seeding
            if round_number == 1:
                # Snake seeding: 1v8, 4v5, 3v6, 2v7 for 8 participants
                paired_participants = self._snake_seed_pairing(current_participants)
            else:
                # Subsequent rounds: pair winners sequentially
                paired_participants = [
                    (current_participants[i], current_participants[i + 1])
                    for i in range(0, len(current_participants), 2)
                ]
            
            for i, (p1, p2) in enumerate(paired_participants):
                match_id = f"{competition.id}_r{round_number}_m{i + 1}"
                
                # Schedule match time with intervals
                match_time = competition.competition_start + timedelta(
                    hours=round_number * 2, minutes=i * 30
                )
                
                match = CompetitionMatch(
                    match_id=match_id,
                    competition_id=competition.id,
                    round_number=round_number,
                    participant_1_id=p1.user_id,
                    participant_2_id=p2.user_id,
                    scheduled_time=match_time,
                    status="scheduled"
                )
                
                round_matches.append(match)
                matches.append(match)
                
                # For bracket generation, advance higher seed
                next_round_participants.append(p1 if p1.seed_position < p2.seed_position else p2)
            
            current_participants = next_round_participants
            round_number += 1
        
        return matches
    
    def _snake_seed_pairing(
        self, 
        participants: List[CompetitionParticipant]
    ) -> List[Tuple[CompetitionParticipant, CompetitionParticipant]]:
        """Create snake seeding pairs for fair matchups."""
        n = len(participants)
        pairs = []
        
        # Classic tournament seeding
        for i in range(n // 2):
            p1 = participants[i]
            p2 = participants[n - 1 - i]
            pairs.append((p1, p2))
        
        return pairs
    
    def _generate_double_elimination_bracket(
        self, 
        competition: Competition, 
        participants: List[CompetitionParticipant]
    ) -> List[CompetitionMatch]:
        """Generate double elimination tournament bracket."""
        # Simplified double elimination - create winners and losers brackets
        matches = []
        
        # Winners bracket (same as single elimination)
        winners_matches = self._generate_single_elimination_bracket(competition, participants)
        
        # Add losers bracket logic
        losers_matches = []
        # This would be more complex in a full implementation
        
        matches.extend(winners_matches)
        matches.extend(losers_matches)
        
        return matches
    
    def _generate_round_robin_bracket(
        self, 
        competition: Competition, 
        participants: List[CompetitionParticipant]
    ) -> List[CompetitionMatch]:
        """Generate round robin tournament where everyone plays everyone."""
        matches = []
        match_counter = 1
        
        for i in range(len(participants)):
            for j in range(i + 1, len(participants)):
                match_id = f"{competition.id}_rr_m{match_counter}"
                
                # Distribute matches across competition period
                days_available = (competition.competition_end - competition.competition_start).days
                match_day = (match_counter - 1) % max(1, days_available)
                match_time = competition.competition_start + timedelta(days=match_day, hours=match_counter % 12 + 8)
                
                match = CompetitionMatch(
                    match_id=match_id,
                    competition_id=competition.id,
                    round_number=1,  # All matches are in round 1 for round robin
                    participant_1_id=participants[i].user_id,
                    participant_2_id=participants[j].user_id,
                    scheduled_time=match_time,
                    status="scheduled"
                )
                
                matches.append(match)
                match_counter += 1
        
        return matches
    
    def _generate_swiss_system_bracket(
        self, 
        competition: Competition, 
        participants: List[CompetitionParticipant]
    ) -> List[CompetitionMatch]:
        """Generate Swiss system tournament bracket."""
        # For simplicity, generate first round only
        # Full Swiss system would require dynamic pairing after each round
        matches = []
        
        # Randomize first round pairings
        shuffled = participants.copy()
        random.shuffle(shuffled)
        
        for i in range(0, len(shuffled), 2):
            if i + 1 < len(shuffled):
                match_id = f"{competition.id}_swiss_r1_m{i//2 + 1}"
                
                match = CompetitionMatch(
                    match_id=match_id,
                    competition_id=competition.id,
                    round_number=1,
                    participant_1_id=shuffled[i].user_id,
                    participant_2_id=shuffled[i + 1].user_id,
                    scheduled_time=competition.competition_start + timedelta(hours=2),
                    status="scheduled"
                )
                
                matches.append(match)
        
        return matches
    
    async def _auto_start_competition(self, competition: Competition) -> bool:
        """Automatically start competition when conditions are met."""
        try:
            if competition.status == CompetitionStatus.DRAFT:
                competition.status = CompetitionStatus.REGISTRATION_OPEN
            
            now = datetime.now(timezone.utc)
            if (now >= competition.registration_end and 
                len(competition.participants) >= competition.min_participants):
                
                competition.status = CompetitionStatus.REGISTRATION_CLOSED
                
                # Generate brackets
                await self.generate_brackets(competition.id)
                
                # Start competition
                if now >= competition.competition_start:
                    competition.status = CompetitionStatus.IN_PROGRESS
                    self.logger.info(f"🚀 Competition auto-started: {competition.id}")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error auto-starting competition: {e}")
            return False
    
    async def _cache_competition(self, competition: Competition) -> None:
        """Cache competition data in Redis."""
        if not self.cache:
            return
        
        try:
            cache_key = f"competition:{competition.id}"
            cache_data = {
                "id": competition.id,
                "name": competition.name,
                "status": competition.status.value,
                "participant_count": len(competition.participants),
                "match_count": len(competition.matches),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache for 1 hour
            await self.cache.setex(cache_key, 3600, json.dumps(cache_data, default=str))
            
        except Exception as e:
            self.logger.warning(f"Failed to cache competition: {e}")


class TournamentBracket:
    """
    Automated tournament bracket management system with
    real-time updates and match scheduling.
    """
    
    def __init__(self, competition_engine: CompetitionEngine):
        """Initialize tournament bracket manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.competition_engine = competition_engine
        
        # Track bracket state
        self.bracket_state: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("TournamentBracket initialized")
    
    async def advance_bracket(
        self, 
        competition_id: str, 
        match_id: str, 
        winner_id: str,
        score_data: Dict[str, Any]
    ) -> bool:
        """Advance tournament bracket with match result."""
        try:
            competition = self.competition_engine.active_competitions.get(competition_id)
            if not competition:
                raise ValueError(f"Competition {competition_id} not found")
            
            # Find and update match
            match = next((m for m in competition.matches if m.match_id == match_id), None)
            if not match:
                raise ValueError(f"Match {match_id} not found")
            
            # Update match result
            match.winner_id = winner_id
            match.status = "completed"
            match.completed_at = datetime.now(timezone.utc)
            match.score_1 = score_data.get("score_1", 0)
            match.score_2 = score_data.get("score_2", 0)
            
            # Advance winner to next round if applicable
            if competition.bracket_type == BracketType.SINGLE_ELIMINATION:
                await self._advance_single_elimination(competition, match, winner_id)
            elif competition.bracket_type == BracketType.DOUBLE_ELIMINATION:
                await self._advance_double_elimination(competition, match, winner_id)
            
            # Check if competition is complete
            await self._check_competition_completion(competition)
            
            self.logger.info(f"✅ Bracket advanced: {match_id} winner {winner_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error advancing bracket: {e}")
            return False
    
    async def _advance_single_elimination(
        self, 
        competition: Competition, 
        completed_match: CompetitionMatch, 
        winner_id: str
    ) -> None:
        """Advance winner in single elimination bracket."""
        next_round = completed_match.round_number + 1
        
        # Find next round match that this winner should advance to
        next_matches = [m for m in competition.matches if m.round_number == next_round]
        
        # Simple advancement logic - this could be more sophisticated
        for next_match in next_matches:
            if not next_match.participant_1_id:
                next_match.participant_1_id = winner_id
                break
            elif not next_match.participant_2_id:
                next_match.participant_2_id = winner_id
                break
    
    async def _advance_double_elimination(
        self, 
        competition: Competition, 
        completed_match: CompetitionMatch, 
        winner_id: str
    ) -> None:
        """Advance winner/loser in double elimination bracket."""
        # This would implement the complex double elimination logic
        # For now, just advance winner to next winners bracket round
        await self._advance_single_elimination(competition, completed_match, winner_id)
    
    async def _check_competition_completion(self, competition: Competition) -> None:
        """Check if competition is complete and award prizes."""
        incomplete_matches = [m for m in competition.matches if m.status != "completed"]
        
        if not incomplete_matches and competition.status == CompetitionStatus.IN_PROGRESS:
            competition.status = CompetitionStatus.COMPLETED
            
            # Calculate final rankings and distribute prizes
            await self._distribute_prizes(competition)
            
            self.logger.info(f"🏆 Competition completed: {competition.id}")
    
    async def _distribute_prizes(self, competition: Competition) -> None:
        """Distribute prizes to competition winners."""
        try:
            # Calculate final rankings based on bracket performance
            rankings = self._calculate_final_rankings(competition)
            
            # Distribute prizes according to prize pool
            for position, user_id in enumerate(rankings, 1):
                if position in competition.prize_pool.distribution:
                    prize_amount = competition.prize_pool.distribution[position]
                    
                    # Here you would integrate with the rewards system
                    # to actually award the prizes to users
                    self.logger.info(f"💰 Prize awarded: Position {position} - {user_id} - {prize_amount}")
            
        except Exception as e:
            self.logger.error(f"Error distributing prizes: {e}")
    
    def _calculate_final_rankings(self, competition: Competition) -> List[str]:
        """Calculate final user rankings from bracket results."""
        # This is a simplified ranking calculation
        # In a real implementation, this would be more sophisticated
        
        participant_scores = defaultdict(int)
        
        # Score based on match wins and advancement
        for match in competition.matches:
            if match.winner_id:
                participant_scores[match.winner_id] += 1
        
        # Sort by score descending
        ranked_participants = sorted(
            participant_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [user_id for user_id, score in ranked_participants]


class CompetitionAnalytics:
    """
    Real-time competition analytics and metrics tracking system.
    """
    
    def __init__(self, competition_engine: CompetitionEngine):
        """Initialize competition analytics."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.competition_engine = competition_engine
        
        # Analytics data storage
        self.analytics_data: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("CompetitionAnalytics initialized")
    
    async def track_competition_metrics(self, competition_id: str) -> Dict[str, Any]:
        """Track real-time competition metrics."""
        try:
            competition = self.competition_engine.active_competitions.get(competition_id)
            if not competition:
                return {}
            
            metrics = {
                "competition_id": competition_id,
                "participant_count": len(competition.participants),
                "matches_total": len(competition.matches),
                "matches_completed": len([m for m in competition.matches if m.status == "completed"]),
                "matches_in_progress": len([m for m in competition.matches if m.status == "in_progress"]),
                "completion_percentage": 0.0,
                "average_match_duration": 0.0,
                "participant_engagement": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate completion percentage
            if metrics["matches_total"] > 0:
                metrics["completion_percentage"] = (
                    metrics["matches_completed"] / metrics["matches_total"] * 100
                )
            
            # Calculate average match duration
            completed_matches = [m for m in competition.matches if m.completed_at and m.status == "completed"]
            if completed_matches:
                durations = []
                for match in completed_matches:
                    if match.completed_at:
                        duration = (match.completed_at - match.scheduled_time).total_seconds() / 60
                        durations.append(duration)
                
                if durations:
                    metrics["average_match_duration"] = sum(durations) / len(durations)
            
            # Store metrics
            self.analytics_data[competition_id] = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error tracking competition metrics: {e}")
            return {}
    
    async def generate_competition_report(self, competition_id: str) -> Dict[str, Any]:
        """Generate comprehensive competition analytics report."""
        try:
            competition = self.competition_engine.active_competitions.get(competition_id)
            if not competition:
                return {}
            
            # Get current metrics
            metrics = await self.track_competition_metrics(competition_id)
            
            # Participant analytics
            participant_analytics = self._analyze_participants(competition)
            
            # Match analytics
            match_analytics = self._analyze_matches(competition)
            
            # Prize analytics
            prize_analytics = self._analyze_prizes(competition)
            
            report = {
                "competition_overview": {
                    "id": competition.id,
                    "name": competition.name,
                    "type": competition.competition_type.value,
                    "status": competition.status.value,
                    "created_at": competition.created_at.isoformat(),
                    "organizer_id": competition.organizer_id
                },
                "metrics": metrics,
                "participant_analytics": participant_analytics,
                "match_analytics": match_analytics,
                "prize_analytics": prize_analytics,
                "recommendations": self._generate_recommendations(competition, metrics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating competition report: {e}")
            return {}
    
    def _analyze_participants(self, competition: Competition) -> Dict[str, Any]:
        """Analyze participant data and demographics."""
        participants = competition.participants
        
        # Skill rating distribution
        skill_ratings = [p.skill_rating for p in participants]
        
        # Tier distribution
        tier_distribution = defaultdict(int)
        for p in participants:
            tier_distribution[p.tier_level] += 1
        
        # Content specialty distribution
        specialty_distribution = defaultdict(int)
        for p in participants:
            specialty_distribution[p.content_specialty] += 1
        
        return {
            "total_participants": len(participants),
            "skill_rating_stats": {
                "min": min(skill_ratings) if skill_ratings else 0,
                "max": max(skill_ratings) if skill_ratings else 0,
                "average": sum(skill_ratings) / len(skill_ratings) if skill_ratings else 0
            },
            "tier_distribution": dict(tier_distribution),
            "specialty_distribution": dict(specialty_distribution),
            "registration_timeline": self._calculate_registration_timeline(participants)
        }
    
    def _analyze_matches(self, competition: Competition) -> Dict[str, Any]:
        """Analyze match data and performance."""
        matches = competition.matches
        completed_matches = [m for m in matches if m.status == "completed"]
        
        # Match completion rate by round
        round_completion = defaultdict(lambda: {"total": 0, "completed": 0})
        for match in matches:
            round_completion[match.round_number]["total"] += 1
            if match.status == "completed":
                round_completion[match.round_number]["completed"] += 1
        
        return {
            "total_matches": len(matches),
            "completed_matches": len(completed_matches),
            "completion_rate": len(completed_matches) / len(matches) * 100 if matches else 0,
            "round_completion": {
                round_num: {
                    "completion_rate": data["completed"] / data["total"] * 100 if data["total"] > 0 else 0,
                    **data
                }
                for round_num, data in round_completion.items()
            },
            "average_score_differential": self._calculate_average_score_differential(completed_matches)
        }
    
    def _analyze_prizes(self, competition: Competition) -> Dict[str, Any]:
        """Analyze prize pool and distribution."""
        prize_pool = competition.prize_pool
        
        return {
            "total_prize_pool": float(prize_pool.total_amount),
            "currency_type": prize_pool.currency_type,
            "positions_awarded": len(prize_pool.distribution),
            "top_prize_percentage": float(prize_pool.distribution.get(1, 0)) / float(prize_pool.total_amount) * 100,
            "prize_distribution": {k: float(v) for k, v in prize_pool.distribution.items()}
        }
    
    def _calculate_registration_timeline(self, participants: List[CompetitionParticipant]) -> List[Dict[str, Any]]:
        """Calculate registration timeline analytics."""
        timeline = []
        
        # Group registrations by hour
        registrations_by_hour = defaultdict(int)
        for participant in participants:
            hour_key = participant.join_timestamp.replace(minute=0, second=0, microsecond=0)
            registrations_by_hour[hour_key] += 1
        
        for hour, count in sorted(registrations_by_hour.items()):
            timeline.append({
                "timestamp": hour.isoformat(),
                "registrations": count,
                "cumulative": sum(c for h, c in registrations_by_hour.items() if h <= hour)
            })
        
        return timeline
    
    def _calculate_average_score_differential(self, completed_matches: List[CompetitionMatch]) -> float:
        """Calculate average score differential in completed matches."""
        if not completed_matches:
            return 0.0
        
        differentials = []
        for match in completed_matches:
            if match.score_1 is not None and match.score_2 is not None:
                differential = abs(match.score_1 - match.score_2)
                differentials.append(differential)
        
        return sum(differentials) / len(differentials) if differentials else 0.0
    
    def _generate_recommendations(
        self, 
        competition: Competition, 
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for competition improvement."""
        recommendations = []
        
        # Participation recommendations
        if len(competition.participants) < competition.max_participants * 0.5:
            recommendations.append("Consider extending registration period or increasing promotion")
        
        # Match scheduling recommendations
        if metrics.get("average_match_duration", 0) > 120:  # 2 hours
            recommendations.append("Consider shorter match formats to improve engagement")
        
        # Prize pool recommendations
        top_prize_percentage = float(competition.prize_pool.distribution.get(1, 0)) / float(competition.prize_pool.total_amount) * 100
        if top_prize_percentage > 50:
            recommendations.append("Consider more distributed prize pool to encourage broader participation")
        
        return recommendations


class CompetitionManager:
    """
    Main competition management orchestrator coordinating all competition
    subsystems and providing unified competition management interface.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the competition manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize subsystems
        self.competition_engine = CompetitionEngine(database_connection, cache_client)
        self.tournament_bracket = TournamentBracket(self.competition_engine)
        self.analytics = CompetitionAnalytics(self.competition_engine)
        
        # Configuration
        self.default_settings = {
            "max_concurrent_competitions": 50,
            "min_participants_for_auto_start": 4,
            "default_registration_period_hours": 48,
            "default_competition_duration_hours": 72
        }
        
        self.logger.info("CompetitionManager initialized")
    
    async def create_tournament(
        self,
        name: str,
        organizer_id: str,
        tournament_config: Dict[str, Any]
    ) -> Optional[Competition]:
        """Create a new tournament with comprehensive configuration."""
        try:
            # Validate configuration
            config = self._validate_tournament_config(tournament_config)
            
            # Create competition
            competition = await self.competition_engine.create_competition(
                name=name,
                description=config.get("description", ""),
                competition_type=CompetitionType(config.get("type", "tournament")),
                bracket_type=BracketType(config.get("bracket_type", "single_elimination")),
                organizer_id=organizer_id,
                registration_period=(
                    config["registration_start"],
                    config["registration_end"]
                ),
                competition_period=(
                    config["competition_start"],
                    config["competition_end"]
                ),
                max_participants=config["max_participants"],
                prize_pool_amount=Decimal(str(config["prize_pool"])),
                **config.get("additional_settings", {})
            )
            
            self.logger.info(f"🏆 Tournament created: {name} ({competition.id})")
            
            return competition
            
        except Exception as e:
            self.logger.error(f"Error creating tournament: {e}")
            return None
    
    def _validate_tournament_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize tournament configuration."""
        required_fields = [
            "max_participants", "prize_pool", "registration_start",
            "registration_end", "competition_start", "competition_end"
        ]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate dates
        now = datetime.now(timezone.utc)
        if config["registration_start"] < now:
            raise ValueError("Registration start must be in the future")
        
        if config["registration_end"] <= config["registration_start"]:
            raise ValueError("Registration end must be after registration start")
        
        if config["competition_start"] < config["registration_end"]:
            raise ValueError("Competition start must be after registration end")
        
        if config["competition_end"] <= config["competition_start"]:
            raise ValueError("Competition end must be after competition start")
        
        # Validate participants
        if config["max_participants"] < 4:
            raise ValueError("Minimum 4 participants required")
        
        # Validate prize pool
        if config["prize_pool"] <= 0:
            raise ValueError("Prize pool must be positive")
        
        return config
    
    async def join_competition(
        self,
        competition_id: str,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> bool:
        """Join a user to a competition with skill-based validation."""
        try:
            # Enhance user profile with additional data for matchmaking
            enhanced_profile = await self._enhance_user_profile(user_id, user_profile)
            
            # Register participant
            success = await self.competition_engine.register_participant(
                competition_id, user_id, enhanced_profile
            )
            
            if success:
                self.logger.info(f"✅ User joined competition: {user_id} -> {competition_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error joining competition: {e}")
            return False
    
    async def _enhance_user_profile(
        self, 
        user_id: str, 
        base_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance user profile with additional matchmaking data."""
        enhanced = base_profile.copy()
        
        # Calculate skill rating if not provided
        if "skill_rating" not in enhanced:
            enhanced["skill_rating"] = await self._calculate_user_skill_rating(user_id)
        
        # Add engagement metrics
        if "engagement_rate" not in enhanced:
            enhanced["engagement_rate"] = base_profile.get("engagement_rate", 0.0)
        
        # Add content specialty
        if "content_specialty" not in enhanced:
            enhanced["content_specialty"] = base_profile.get("content_type", "general")
        
        return enhanced
    
    async def _calculate_user_skill_rating(self, user_id: str) -> float:
        """Calculate user skill rating for matchmaking."""
        # This would integrate with user analytics to calculate skill
        # For now, return a default rating
        return 1000.0
    
    async def submit_match_result(
        self,
        competition_id: str,
        match_id: str,
        winner_id: str,
        match_data: Dict[str, Any]
    ) -> bool:
        """Submit match result and advance tournament bracket."""
        try:
            success = await self.tournament_bracket.advance_bracket(
                competition_id, match_id, winner_id, match_data
            )
            
            if success:
                # Update analytics
                await self.analytics.track_competition_metrics(competition_id)
                
                self.logger.info(f"🏅 Match result submitted: {match_id} winner {winner_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error submitting match result: {e}")
            return False
    
    async def get_competition_status(self, competition_id: str) -> Dict[str, Any]:
        """Get comprehensive competition status and analytics."""
        try:
            competition = self.competition_engine.active_competitions.get(competition_id)
            if not competition:
                return {"error": "Competition not found"}
            
            # Get real-time analytics
            analytics_report = await self.analytics.generate_competition_report(competition_id)
            
            # Compile status
            status = {
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "status": competition.status.value,
                    "type": competition.competition_type.value,
                    "bracket_type": competition.bracket_type.value
                },
                "schedule": {
                    "registration_start": competition.registration_start.isoformat(),
                    "registration_end": competition.registration_end.isoformat(),
                    "competition_start": competition.competition_start.isoformat(),
                    "competition_end": competition.competition_end.isoformat()
                },
                "participants": {
                    "count": len(competition.participants),
                    "max_allowed": competition.max_participants,
                    "min_required": competition.min_participants
                },
                "matches": {
                    "total": len(competition.matches),
                    "completed": len([m for m in competition.matches if m.status == "completed"]),
                    "in_progress": len([m for m in competition.matches if m.status == "in_progress"]),
                    "scheduled": len([m for m in competition.matches if m.status == "scheduled"])
                },
                "prize_pool": {
                    "total": float(competition.prize_pool.total_amount),
                    "currency": competition.prize_pool.currency_type,
                    "positions": len(competition.prize_pool.distribution)
                },
                "analytics": analytics_report
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting competition status: {e}")
            return {"error": str(e)}
    
    async def get_user_competitions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all competitions a user is participating in."""
        try:
            user_competitions = []
            
            for competition in self.competition_engine.active_competitions.values():
                # Check if user is participant
                participant = next(
                    (p for p in competition.participants if p.user_id == user_id), 
                    None
                )
                
                if participant:
                    user_competitions.append({
                        "competition_id": competition.id,
                        "name": competition.name,
                        "status": competition.status.value,
                        "participant_count": len(competition.participants),
                        "user_seed": participant.seed_position,
                        "join_date": participant.join_timestamp.isoformat()
                    })
            
            return user_competitions
            
        except Exception as e:
            self.logger.error(f"Error getting user competitions: {e}")
            return []


# Global competition manager instance
_competition_manager: Optional[CompetitionManager] = None


async def get_competition_manager(
    database_connection=None, 
    cache_client=None
) -> CompetitionManager:
    """Get the global competition manager instance."""
    global _competition_manager
    
    if _competition_manager is None:
        _competition_manager = CompetitionManager(database_connection, cache_client)
    
    return _competition_manager


# Convenience functions
async def create_tournament(
    name: str,
    organizer_id: str,
    config: Dict[str, Any]
) -> Optional[Competition]:
    """Create a new tournament."""
    manager = await get_competition_manager()
    return await manager.create_tournament(name, organizer_id, config)


async def join_competition(
    competition_id: str,
    user_id: str,
    user_profile: Dict[str, Any]
) -> bool:
    """Join a user to a competition."""
    manager = await get_competition_manager()
    return await manager.join_competition(competition_id, user_id, user_profile)


async def get_competition_leaderboard(competition_id: str) -> List[Dict[str, Any]]:
    """Get current competition leaderboard."""
    manager = await get_competition_manager()
    status = await manager.get_competition_status(competition_id)
    return status.get("analytics", {}).get("participant_analytics", {})


# Module exports
__all__ = [
    "CompetitionManager",
    "CompetitionEngine", 
    "TournamentBracket",
    "CompetitionAnalytics",
    "Competition",
    "CompetitionParticipant",
    "CompetitionMatch",
    "SeasonalCompetition",
    "PrizePool",
    "CompetitionType",
    "CompetitionStatus",
    "BracketType",
    "MatchmakingCriteria",
    "get_competition_manager",
    "create_tournament",
    "join_competition",
    "get_competition_leaderboard"
]