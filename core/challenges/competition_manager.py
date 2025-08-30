"""
Competition Manager - Enterprise Competition Orchestration and Management

This module provides comprehensive competition management for creator tournaments,
seasonal events, and collaborative competitions with advanced analytics and
real-time monitoring capabilities.

Features:
- Multi-tier competition tournaments with bracket management
- Real-time leaderboards and live competition tracking
- Advanced competition analytics and business intelligence
- Integration with monetization and reward distribution systems
- Cross-platform competition distribution and management
- Professional competition lifecycle management
- Team-based and individual competition support
- Competition template system with customizable rules

Business Logic Integration:
- Creator engagement → Competition participation → Revenue optimization
- Competition performance → Creator matching → Collaboration opportunities
- Competition rewards → Monetization tracking → Business growth metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
import json
import logging
import math
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CompetitionType(Enum):
    """Professional competition type classification"""
    TOURNAMENT = "tournament"
    LEAGUE = "league"
    SEASONAL_EVENT = "seasonal_event"
    COMMUNITY_CHALLENGE = "community_challenge"
    TEAM_COMPETITION = "team_competition"
    CREATOR_BATTLE = "creator_battle"
    SKILL_SHOWCASE = "skill_showcase"
    INNOVATION_CONTEST = "innovation_contest"


class CompetitionStatus(Enum):
    """Competition lifecycle status"""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    SEMIFINALS = "semifinals"
    FINALS = "finals"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class CompetitionFormat(Enum):
    """Competition format types"""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS_SYSTEM = "swiss_system"
    LADDER = "ladder"
    POINTS_BASED = "points_based"


class ParticipantType(Enum):
    """Competition participant types"""
    INDIVIDUAL = "individual"
    TEAM = "team"
    MIXED = "mixed"


@dataclass
class CompetitionRule:
    """Competition rule specification"""
    rule_id: str
    name: str
    description: str
    type: str  # scoring, eligibility, conduct, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    penalty: Optional[str] = None
    is_mandatory: bool = True


@dataclass
class CompetitionReward:
    """Competition reward structure"""
    position: int  # 1st, 2nd, 3rd, etc.
    title: str  # Winner, Runner-up, etc.
    monetary_prize: float
    virtual_rewards: List[str] = field(default_factory=list)
    special_benefits: List[str] = field(default_factory=list)
    recognition_level: str = "standard"  # standard, premium, exclusive


@dataclass
class CompetitionConfiguration:
    """Comprehensive competition configuration"""
    competition_id: str
    title: str
    description: str
    competition_type: CompetitionType
    competition_format: CompetitionFormat
    participant_type: ParticipantType
    
    # Timing
    registration_start: datetime
    registration_end: datetime
    competition_start: datetime
    competition_end: datetime
    
    # Participation
    max_participants: Optional[int] = None
    min_participants: int = 2
    entry_fee: float = 0.0
    team_size_min: int = 1
    team_size_max: int = 1
    
    # Rules and scoring
    rules: List[CompetitionRule] = field(default_factory=list)
    scoring_method: str = "points"
    elimination_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Rewards
    rewards: List[CompetitionReward] = field(default_factory=list)
    total_prize_pool: float = 0.0
    
    # Requirements
    eligibility_requirements: Dict[str, Any] = field(default_factory=dict)
    skill_level_required: str = "beginner"
    
    # Configuration
    is_featured: bool = False
    is_premium: bool = False
    visibility: str = "public"  # public, private, invite_only
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Participant:
    """Competition participant information"""
    participant_id: str
    name: str
    type: ParticipantType
    members: List[str] = field(default_factory=list)  # For teams
    
    # Registration
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registration_data: Dict[str, Any] = field(default_factory=dict)
    
    # Performance
    current_score: float = 0.0
    current_rank: int = 0
    matches_played: int = 0
    matches_won: int = 0
    matches_lost: int = 0
    
    # Status
    is_active: bool = True
    elimination_round: Optional[int] = None
    advancement_status: str = "competing"  # competing, eliminated, advanced
    
    # Analytics
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_activity: Optional[datetime] = None


@dataclass
class CompetitionMatch:
    """Individual competition match/round"""
    match_id: str
    competition_id: str
    round_number: int
    match_number: int
    
    # Participants
    participants: List[str]  # participant IDs
    winner: Optional[str] = None
    
    # Timing
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Results
    scores: Dict[str, float] = field(default_factory=dict)
    match_data: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionRound:
    """Competition round information"""
    round_id: str
    round_number: int
    round_name: str
    competition_id: str
    
    # Matches
    matches: List[CompetitionMatch] = field(default_factory=list)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Status
    status: str = "pending"  # pending, active, completed
    
    # Rules
    advancement_criteria: Dict[str, Any] = field(default_factory=dict)
    elimination_count: int = 0


class CompetitionBracketManager:
    """Manages competition brackets and matchmaking"""
    
    def __init__(self, competition_format: CompetitionFormat):
        self.format = competition_format
    
    async def generate_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate competition bracket based on format"""
        try:
            if self.format == CompetitionFormat.SINGLE_ELIMINATION:
                return await self._generate_single_elimination_bracket(participants, config)
            elif self.format == CompetitionFormat.DOUBLE_ELIMINATION:
                return await self._generate_double_elimination_bracket(participants, config)
            elif self.format == CompetitionFormat.ROUND_ROBIN:
                return await self._generate_round_robin_bracket(participants, config)
            elif self.format == CompetitionFormat.SWISS_SYSTEM:
                return await self._generate_swiss_system_bracket(participants, config)
            else:
                return await self._generate_points_based_bracket(participants, config)
                
        except Exception as e:
            logger.error(f"Error generating bracket: {e}")
            return []
    
    async def _generate_single_elimination_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate single elimination bracket"""
        rounds = []
        participant_count = len(participants)
        
        # Calculate number of rounds needed
        rounds_needed = math.ceil(math.log2(participant_count))
        
        current_participants = [p.participant_id for p in participants]
        
        for round_num in range(1, rounds_needed + 1):
            round_matches = []
            
            # Pair participants for matches
            for i in range(0, len(current_participants), 2):
                if i + 1 < len(current_participants):
                    # Regular match
                    match = CompetitionMatch(
                        match_id=f"{config.competition_id}_r{round_num}_m{i//2 + 1}",
                        competition_id=config.competition_id,
                        round_number=round_num,
                        match_number=i//2 + 1,
                        participants=[current_participants[i], current_participants[i + 1]]
                    )
                else:
                    # Bye - automatic advancement
                    match = CompetitionMatch(
                        match_id=f"{config.competition_id}_r{round_num}_m{i//2 + 1}",
                        competition_id=config.competition_id,
                        round_number=round_num,
                        match_number=i//2 + 1,
                        participants=[current_participants[i]],
                        winner=current_participants[i],
                        status="completed"
                    )
                
                round_matches.append(match)
            
            # Create round
            competition_round = CompetitionRound(
                round_id=f"{config.competition_id}_round_{round_num}",
                round_number=round_num,
                round_name=f"Round {round_num}" if round_num < rounds_needed else "Final",
                competition_id=config.competition_id,
                matches=round_matches
            )
            
            rounds.append(competition_round)
            
            # Prepare for next round (winners advance)
            current_participants = [m.participants[0] for m in round_matches]
        
        return rounds
    
    async def _generate_double_elimination_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate double elimination bracket"""
        # Simplified double elimination - creates winners and losers bracket
        rounds = []
        participant_count = len(participants)
        
        # Generate winners bracket
        winners_rounds = await self._generate_single_elimination_bracket(participants, config)
        
        # Add losers bracket rounds
        for i, round_obj in enumerate(winners_rounds):
            round_obj.round_name = f"Winners Round {round_obj.round_number}"
            rounds.append(round_obj)
            
            # Create corresponding losers bracket round
            if i < len(winners_rounds) - 1:  # Not the final
                losers_round = CompetitionRound(
                    round_id=f"{config.competition_id}_losers_round_{i + 1}",
                    round_number=len(winners_rounds) + i + 1,
                    round_name=f"Losers Round {i + 1}",
                    competition_id=config.competition_id,
                    matches=[]  # Will be populated during tournament
                )
                rounds.append(losers_round)
        
        return rounds
    
    async def _generate_round_robin_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate round robin bracket (everyone plays everyone)"""
        rounds = []
        participant_ids = [p.participant_id for p in participants]
        participant_count = len(participant_ids)
        
        # Calculate all possible matches
        all_matches = []
        match_counter = 1
        
        for i in range(participant_count):
            for j in range(i + 1, participant_count):
                match = CompetitionMatch(
                    match_id=f"{config.competition_id}_rr_m{match_counter}",
                    competition_id=config.competition_id,
                    round_number=1,
                    match_number=match_counter,
                    participants=[participant_ids[i], participant_ids[j]]
                )
                all_matches.append(match)
                match_counter += 1
        
        # Create single round with all matches
        round_robin_round = CompetitionRound(
            round_id=f"{config.competition_id}_round_robin",
            round_number=1,
            round_name="Round Robin",
            competition_id=config.competition_id,
            matches=all_matches
        )
        
        rounds.append(round_robin_round)
        return rounds
    
    async def _generate_swiss_system_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate Swiss system bracket (multiple rounds, pairing by performance)"""
        rounds = []
        participant_count = len(participants)
        
        # Swiss system typically has log2(n) rounds
        rounds_needed = max(3, math.ceil(math.log2(participant_count)))
        
        for round_num in range(1, rounds_needed + 1):
            swiss_round = CompetitionRound(
                round_id=f"{config.competition_id}_swiss_round_{round_num}",
                round_number=round_num,
                round_name=f"Swiss Round {round_num}",
                competition_id=config.competition_id,
                matches=[]  # Will be populated during tournament based on current standings
            )
            rounds.append(swiss_round)
        
        return rounds
    
    async def _generate_points_based_bracket(
        self,
        participants: List[Participant],
        config: CompetitionConfiguration
    ) -> List[CompetitionRound]:
        """Generate points-based competition structure"""
        # Single round where all participants compete simultaneously
        points_round = CompetitionRound(
            round_id=f"{config.competition_id}_points_based",
            round_number=1,
            round_name="Points Competition",
            competition_id=config.competition_id,
            matches=[]  # Points accumulated over time, not match-based
        )
        
        return [points_round]


class CompetitionManager:
    """
    Enterprise-grade competition management system
    
    Provides comprehensive competition lifecycle management with advanced
    bracket generation, real-time tracking, and business analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize competition manager with configuration"""
        self.config = config or {}
        
        # Core storage
        self._active_competitions: Dict[str, CompetitionConfiguration] = {}
        self._participants: Dict[str, Dict[str, Participant]] = {}
        self._brackets: Dict[str, List[CompetitionRound]] = {}
        self._match_results: Dict[str, List[CompetitionMatch]] = {}
        
        # Managers
        self._bracket_managers: Dict[CompetitionFormat, CompetitionBracketManager] = {
            format_type: CompetitionBracketManager(format_type)
            for format_type in CompetitionFormat
        }
        
        # Performance tracking
        self._competition_analytics: Dict[str, Dict[str, Any]] = {}
        self._leaderboards: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configuration
        self.max_concurrent_competitions = self.config.get('max_concurrent_competitions', 50)
        self.real_time_updates = self.config.get('real_time_updates', True)
        self.analytics_enabled = self.config.get('analytics_enabled', True)
        
        logger.info("Competition Manager initialized successfully")
    
    async def create_competition(
        self,
        competition_config: CompetitionConfiguration
    ) -> bool:
        """Create and initialize a new competition"""
        try:
            competition_id = competition_config.competition_id
            
            if competition_id in self._active_competitions:
                logger.warning(f"Competition {competition_id} already exists")
                return False
            
            # Validate configuration
            validation_result = await self._validate_competition_config(competition_config)
            if not validation_result['valid']:
                logger.error(f"Invalid competition configuration: {validation_result['errors']}")
                return False
            
            # Initialize competition
            self._active_competitions[competition_id] = competition_config
            self._participants[competition_id] = {}
            self._brackets[competition_id] = []
            self._match_results[competition_id] = []
            self._leaderboards[competition_id] = []
            
            # Initialize analytics
            self._competition_analytics[competition_id] = {
                'created_at': datetime.now(timezone.utc),
                'registration_count': 0,
                'total_matches': 0,
                'completed_matches': 0,
                'total_prize_pool': competition_config.total_prize_pool,
                'revenue_generated': 0.0
            }
            
            logger.info(f"Competition {competition_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating competition: {e}")
            return False
    
    async def register_participant(
        self,
        competition_id: str,
        participant_data: Dict[str, Any]
    ) -> bool:
        """Register participant for competition"""
        try:
            if competition_id not in self._active_competitions:
                logger.error(f"Competition {competition_id} not found")
                return False
            
            competition = self._active_competitions[competition_id]
            
            # Check registration window
            now = datetime.now(timezone.utc)
            if now < competition.registration_start:
                logger.error(f"Registration not yet open for {competition_id}")
                return False
            
            if now > competition.registration_end:
                logger.error(f"Registration closed for {competition_id}")
                return False
            
            # Check participant limits
            current_count = len(self._participants[competition_id])
            if competition.max_participants and current_count >= competition.max_participants:
                logger.error(f"Competition {competition_id} is full")
                return False
            
            # Create participant
            participant_id = participant_data.get('participant_id', f"participant_{current_count + 1}")
            
            if participant_id in self._participants[competition_id]:
                logger.warning(f"Participant {participant_id} already registered")
                return False
            
            participant = Participant(
                participant_id=participant_id,
                name=participant_data.get('name', ''),
                type=ParticipantType(participant_data.get('type', 'individual')),
                members=participant_data.get('members', []),
                registration_data=participant_data.get('registration_data', {})
            )
            
            # Validate eligibility
            if not await self._check_eligibility(competition, participant):
                logger.error(f"Participant {participant_id} not eligible for {competition_id}")
                return False
            
            # Register participant
            self._participants[competition_id][participant_id] = participant
            self._competition_analytics[competition_id]['registration_count'] = current_count + 1
            
            logger.info(f"Participant {participant_id} registered for {competition_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering participant: {e}")
            return False
    
    async def start_competition(self, competition_id: str) -> bool:
        """Start competition and generate brackets"""
        try:
            if competition_id not in self._active_competitions:
                logger.error(f"Competition {competition_id} not found")
                return False
            
            competition = self._active_competitions[competition_id]
            participants = list(self._participants[competition_id].values())
            
            # Check minimum participants
            if len(participants) < competition.min_participants:
                logger.error(f"Not enough participants for {competition_id}")
                return False
            
            # Generate bracket
            bracket_manager = self._bracket_managers[competition.competition_format]
            bracket = await bracket_manager.generate_bracket(participants, competition)
            
            if not bracket:
                logger.error(f"Failed to generate bracket for {competition_id}")
                return False
            
            self._brackets[competition_id] = bracket
            
            # Update analytics
            total_matches = sum(len(round_obj.matches) for round_obj in bracket)
            self._competition_analytics[competition_id]['total_matches'] = total_matches
            
            # Initialize leaderboard
            await self._update_leaderboard(competition_id)
            
            logger.info(f"Competition {competition_id} started with {len(participants)} participants")
            return True
            
        except Exception as e:
            logger.error(f"Error starting competition: {e}")
            return False
    
    async def submit_match_result(
        self,
        competition_id: str,
        match_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Submit and process match result"""
        try:
            if competition_id not in self._active_competitions:
                return False
            
            # Find match in bracket
            match = None
            round_obj = None
            
            for bracket_round in self._brackets[competition_id]:
                for bracket_match in bracket_round.matches:
                    if bracket_match.match_id == match_id:
                        match = bracket_match
                        round_obj = bracket_round
                        break
                if match:
                    break
            
            if not match:
                logger.error(f"Match {match_id} not found in {competition_id}")
                return False
            
            # Process results
            match.scores = results.get('scores', {})
            match.match_data = results.get('match_data', {})
            match.winner = results.get('winner')
            match.status = "completed"
            match.actual_end = datetime.now(timezone.utc)
            
            # Update participant stats
            for participant_id in match.participants:
                if participant_id in self._participants[competition_id]:
                    participant = self._participants[competition_id][participant_id]
                    participant.matches_played += 1
                    
                    if participant_id == match.winner:
                        participant.matches_won += 1
                        participant.current_score += results.get('winner_points', 3)
                    else:
                        participant.matches_lost += 1
                        participant.current_score += results.get('loser_points', 1)
                    
                    participant.last_activity = datetime.now(timezone.utc)
            
            # Store result
            self._match_results[competition_id].append(match)
            
            # Update analytics
            analytics = self._competition_analytics[competition_id]
            analytics['completed_matches'] += 1
            
            # Update leaderboard
            await self._update_leaderboard(competition_id)
            
            # Check if round is complete
            await self._check_round_completion(competition_id, round_obj)
            
            logger.info(f"Match result submitted for {match_id} in {competition_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting match result: {e}")
            return False
    
    async def get_competition_status(
        self,
        competition_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive competition status"""
        try:
            if competition_id not in self._active_competitions:
                return {}
            
            competition = self._active_competitions[competition_id]
            participants = self._participants[competition_id]
            bracket = self._brackets[competition_id]
            analytics = self._competition_analytics[competition_id]
            
            # Determine current status
            now = datetime.now(timezone.utc)
            
            if now < competition.registration_start:
                status = CompetitionStatus.DRAFT
            elif now < competition.registration_end:
                status = CompetitionStatus.REGISTRATION_OPEN
            elif now < competition.competition_start:
                status = CompetitionStatus.REGISTRATION_CLOSED
            elif now < competition.competition_end:
                status = CompetitionStatus.IN_PROGRESS
            else:
                status = CompetitionStatus.COMPLETED
            
            # Get current round info
            current_round = None
            if bracket:
                for round_obj in bracket:
                    if round_obj.status in ["active", "pending"]:
                        current_round = {
                            'round_number': round_obj.round_number,
                            'round_name': round_obj.round_name,
                            'matches_total': len(round_obj.matches),
                            'matches_completed': sum(1 for m in round_obj.matches if m.status == "completed")
                        }
                        break
            
            return {
                'competition_info': {
                    'competition_id': competition_id,
                    'title': competition.title,
                    'type': competition.competition_type.value,
                    'format': competition.competition_format.value,
                    'status': status.value
                },
                'participation': {
                    'total_participants': len(participants),
                    'max_participants': competition.max_participants,
                    'registration_open': now < competition.registration_end
                },
                'progress': {
                    'current_round': current_round,
                    'total_rounds': len(bracket),
                    'matches_completed': analytics.get('completed_matches', 0),
                    'matches_total': analytics.get('total_matches', 0)
                },
                'leaderboard': self._leaderboards.get(competition_id, [])[:10],  # Top 10
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting competition status: {e}")
            return {}
    
    async def get_leaderboard(
        self,
        competition_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get competition leaderboard"""
        try:
            if competition_id not in self._leaderboards:
                await self._update_leaderboard(competition_id)
            
            return self._leaderboards[competition_id][:limit]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_bracket(self, competition_id: str) -> List[Dict[str, Any]]:
        """Get competition bracket structure"""
        try:
            if competition_id not in self._brackets:
                return []
            
            bracket_data = []
            
            for round_obj in self._brackets[competition_id]:
                round_data = {
                    'round_id': round_obj.round_id,
                    'round_number': round_obj.round_number,
                    'round_name': round_obj.round_name,
                    'status': round_obj.status,
                    'matches': []
                }
                
                for match in round_obj.matches:
                    match_data = {
                        'match_id': match.match_id,
                        'participants': match.participants,
                        'winner': match.winner,
                        'scores': match.scores,
                        'status': match.status,
                        'scheduled_start': match.scheduled_start.isoformat() if match.scheduled_start else None
                    }
                    round_data['matches'].append(match_data)
                
                bracket_data.append(round_data)
            
            return bracket_data
            
        except Exception as e:
            logger.error(f"Error getting bracket: {e}")
            return []
    
    # Helper methods
    
    async def _validate_competition_config(
        self,
        config: CompetitionConfiguration
    ) -> Dict[str, Any]:
        """Validate competition configuration"""
        errors = []
        
        # Basic validation
        if not config.title:
            errors.append("Competition title is required")
        
        if config.registration_start >= config.registration_end:
            errors.append("Registration end must be after registration start")
        
        if config.competition_start <= config.registration_end:
            errors.append("Competition start must be after registration end")
        
        if config.min_participants < 2:
            errors.append("Minimum participants must be at least 2")
        
        if config.max_participants and config.max_participants < config.min_participants:
            errors.append("Maximum participants must be greater than minimum participants")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _check_eligibility(
        self,
        competition: CompetitionConfiguration,
        participant: Participant
    ) -> bool:
        """Check participant eligibility"""
        try:
            requirements = competition.eligibility_requirements
            
            # Check skill level
            if 'min_skill_level' in requirements:
                # Placeholder for skill level check
                pass
            
            # Check team size for team competitions
            if competition.participant_type == ParticipantType.TEAM:
                team_size = len(participant.members)
                if team_size < competition.team_size_min or team_size > competition.team_size_max:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {e}")
            return False
    
    async def _update_leaderboard(self, competition_id: str) -> None:
        """Update competition leaderboard"""
        try:
            if competition_id not in self._participants:
                return
            
            participants = list(self._participants[competition_id].values())
            
            # Sort by score, then by wins, then by matches played
            participants.sort(
                key=lambda p: (p.current_score, p.matches_won, -p.matches_played),
                reverse=True
            )
            
            # Update ranks
            leaderboard = []
            for i, participant in enumerate(participants):
                participant.current_rank = i + 1
                
                leaderboard.append({
                    'rank': i + 1,
                    'participant_id': participant.participant_id,
                    'name': participant.name,
                    'type': participant.type.value,
                    'score': participant.current_score,
                    'matches_played': participant.matches_played,
                    'matches_won': participant.matches_won,
                    'matches_lost': participant.matches_lost,
                    'win_rate': participant.matches_won / max(participant.matches_played, 1),
                    'advancement_status': participant.advancement_status,
                    'last_activity': participant.last_activity.isoformat() if participant.last_activity else None
                })
            
            self._leaderboards[competition_id] = leaderboard
            
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
    
    async def _check_round_completion(
        self,
        competition_id: str,
        round_obj: CompetitionRound
    ) -> None:
        """Check if round is completed and advance tournament"""
        try:
            # Check if all matches in round are completed
            completed_matches = sum(1 for m in round_obj.matches if m.status == "completed")
            total_matches = len(round_obj.matches)
            
            if completed_matches == total_matches:
                round_obj.status = "completed"
                round_obj.end_time = datetime.now(timezone.utc)
                
                # Advance winners to next round
                await self._advance_participants(competition_id, round_obj)
                
                logger.info(f"Round {round_obj.round_number} completed in {competition_id}")
            
        except Exception as e:
            logger.error(f"Error checking round completion: {e}")
    
    async def _advance_participants(
        self,
        competition_id: str,
        completed_round: CompetitionRound
    ) -> None:
        """Advance participants to next round"""
        try:
            competition = self._active_competitions[competition_id]
            bracket = self._brackets[competition_id]
            
            # Find next round
            next_round = None
            for round_obj in bracket:
                if round_obj.round_number == completed_round.round_number + 1:
                    next_round = round_obj
                    break
            
            if not next_round:
                # Tournament completed
                await self._finalize_competition(competition_id)
                return
            
            # Get winners from completed round
            winners = []
            for match in completed_round.matches:
                if match.winner:
                    winners.append(match.winner)
            
            # Generate matches for next round
            if competition.competition_format == CompetitionFormat.SINGLE_ELIMINATION:
                await self._generate_next_elimination_matches(next_round, winners)
            
            next_round.status = "active"
            next_round.start_time = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error advancing participants: {e}")
    
    async def _generate_next_elimination_matches(
        self,
        next_round: CompetitionRound,
        winners: List[str]
    ) -> None:
        """Generate matches for next elimination round"""
        try:
            next_round.matches = []
            
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    match = CompetitionMatch(
                        match_id=f"{next_round.competition_id}_r{next_round.round_number}_m{i//2 + 1}",
                        competition_id=next_round.competition_id,
                        round_number=next_round.round_number,
                        match_number=i//2 + 1,
                        participants=[winners[i], winners[i + 1]]
                    )
                else:
                    # Bye
                    match = CompetitionMatch(
                        match_id=f"{next_round.competition_id}_r{next_round.round_number}_m{i//2 + 1}",
                        competition_id=next_round.competition_id,
                        round_number=next_round.round_number,
                        match_number=i//2 + 1,
                        participants=[winners[i]],
                        winner=winners[i],
                        status="completed"
                    )
                
                next_round.matches.append(match)
            
        except Exception as e:
            logger.error(f"Error generating next round matches: {e}")
    
    async def _finalize_competition(self, competition_id: str) -> None:
        """Finalize competition and distribute rewards"""
        try:
            # Update final leaderboard
            await self._update_leaderboard(competition_id)
            
            # Distribute rewards
            await self._distribute_rewards(competition_id)
            
            # Update analytics
            analytics = self._competition_analytics[competition_id]
            analytics['completed_at'] = datetime.now(timezone.utc)
            analytics['final_participant_count'] = len(self._participants[competition_id])
            
            logger.info(f"Competition {competition_id} finalized")
            
        except Exception as e:
            logger.error(f"Error finalizing competition: {e}")
    
    async def _distribute_rewards(self, competition_id: str) -> None:
        """Distribute rewards to competition winners"""
        try:
            competition = self._active_competitions[competition_id]
            leaderboard = self._leaderboards[competition_id]
            
            for reward in competition.rewards:
                if reward.position <= len(leaderboard):
                    winner = leaderboard[reward.position - 1]
                    
                    # Record reward distribution
                    if 'rewards_earned' not in winner:
                        winner['rewards_earned'] = []
                    
                    winner['rewards_earned'].append({
                        'title': reward.title,
                        'monetary_prize': reward.monetary_prize,
                        'virtual_rewards': reward.virtual_rewards,
                        'special_benefits': reward.special_benefits
                    })
                    
                    logger.info(f"Reward distributed to {winner['participant_id']}: {reward.title}")
            
        except Exception as e:
            logger.error(f"Error distributing rewards: {e}")