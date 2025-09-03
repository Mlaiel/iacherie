"""Competition Engine - Moteur compétitions
========================================

Competition management system for organizing tournaments, competitions,
and competitive events between content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import random


class CompetitionType(str, Enum):
    """Types of competitions available."""
    TOURNAMENT = "tournament"
    BRACKET = "bracket"
    LEAGUE = "league"
    BATTLE = "battle"
    SHOWDOWN = "showdown"
    MARATHON = "marathon"
    CONTEST = "contest"


class CompetitionFormat(str, Enum):
    """Competition format types."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    LADDER = "ladder"
    FREE_FOR_ALL = "free_for_all"


class CompetitionStatus(str, Enum):
    """Competition lifecycle status."""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class ParticipantStatus(str, Enum):
    """Participant status in competition."""
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    WINNER = "winner"
    DISQUALIFIED = "disqualified"
    WITHDREW = "withdrew"


@dataclass
class CompetitionRule:
    """Competition rule definition."""
    rule_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_required: bool = True


@dataclass
class CompetitionReward:
    """Competition reward definition."""
    position: int  # 1st, 2nd, 3rd, etc.
    reward_type: str
    amount: Union[int, float]
    currency: str = "credits"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Competition:
    """Complete competition definition."""
    id: str
    title: str
    description: str
    competition_type: CompetitionType
    format: CompetitionFormat
    status: CompetitionStatus
    rules: List[CompetitionRule]
    rewards: List[CompetitionReward]
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    min_participants: int = 2
    max_participants: Optional[int] = None
    current_participants: int = 0
    entry_fee: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


@dataclass
class CompetitionParticipant:
    """Competition participant."""
    id: str
    user_id: str
    competition_id: str
    status: ParticipantStatus
    registration_date: datetime
    current_score: float = 0.0
    current_rank: int = 0
    matches_played: int = 0
    matches_won: int = 0
    matches_lost: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionMatch:
    """Individual match within a competition."""
    id: str
    competition_id: str
    round_number: int
    match_number: int
    participant1_id: str
    participant2_id: Optional[str] = None  # None for bye rounds
    winner_id: Optional[str] = None
    scores: Dict[str, float] = field(default_factory=dict)
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitionBracket:
    """Competition bracket structure."""
    competition_id: str
    total_rounds: int
    current_round: int = 1
    matches: List[CompetitionMatch] = field(default_factory=list)
    bracket_data: Dict[str, Any] = field(default_factory=dict)


class CompetitionEngine:
    """
    Advanced competition management system providing tournament organization,
    bracket management, match scheduling, and comprehensive competition analytics.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the competition engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.active_competitions: Dict[str, Competition] = {}
        self.participants: Dict[str, List[CompetitionParticipant]] = {}
        self.brackets: Dict[str, CompetitionBracket] = {}
        self.matches: Dict[str, List[CompetitionMatch]] = {}
        
        self.logger.info("CompetitionEngine initialized")
    
    async def create_competition(
        self,
        title: str,
        description: str,
        competition_type: CompetitionType,
        format: CompetitionFormat,
        start_date: datetime,
        duration_days: int,
        registration_deadline: datetime,
        rules: List[Dict[str, Any]],
        rewards: List[Dict[str, Any]],
        min_participants: int = 2,
        max_participants: Optional[int] = None,
        entry_fee: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> Optional[str]:
        """Create a new competition."""
        try:
            competition_id = str(uuid.uuid4())
            end_date = start_date + timedelta(days=duration_days)
            
            # Create rules
            competition_rules = []
            for rule_data in rules:
                rule = CompetitionRule(
                    rule_type=rule_data["rule_type"],
                    description=rule_data["description"],
                    parameters=rule_data.get("parameters", {}),
                    is_required=rule_data.get("is_required", True)
                )
                competition_rules.append(rule)
            
            # Create rewards
            competition_rewards = []
            for reward_data in rewards:
                reward = CompetitionReward(
                    position=reward_data["position"],
                    reward_type=reward_data["reward_type"],
                    amount=reward_data["amount"],
                    currency=reward_data.get("currency", "credits"),
                    description=reward_data.get("description", ""),
                    metadata=reward_data.get("metadata", {})
                )
                competition_rewards.append(reward)
            
            # Create competition
            competition = Competition(
                id=competition_id,
                title=title,
                description=description,
                competition_type=competition_type,
                format=format,
                status=CompetitionStatus.DRAFT,
                rules=competition_rules,
                rewards=competition_rewards,
                start_date=start_date,
                end_date=end_date,
                registration_deadline=registration_deadline,
                min_participants=min_participants,
                max_participants=max_participants,
                entry_fee=entry_fee,
                tags=tags or [],
                created_by=created_by
            )
            
            # Store competition
            self.active_competitions[competition_id] = competition
            self.participants[competition_id] = []
            self.matches[competition_id] = []
            
            self.logger.info(f"Created competition '{title}' with ID {competition_id}")
            return competition_id
            
        except Exception as e:
            self.logger.error(f"Error creating competition: {e}")
            return None
    
    async def open_registration(self, competition_id: str) -> bool:
        """Open registration for a competition."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                self.logger.warning(f"Competition {competition_id} not found")
                return False
            
            if competition.status != CompetitionStatus.DRAFT:
                self.logger.warning(f"Competition {competition_id} not in draft status")
                return False
            
            competition.status = CompetitionStatus.REGISTRATION_OPEN
            self.logger.info(f"Opened registration for competition '{competition.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening registration: {e}")
            return False
    
    async def register_participant(
        self,
        competition_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a participant for a competition."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                self.logger.warning(f"Competition {competition_id} not found")
                return False
            
            if competition.status != CompetitionStatus.REGISTRATION_OPEN:
                self.logger.warning(f"Registration not open for competition {competition_id}")
                return False
            
            # Check registration deadline
            now = datetime.now(timezone.utc)
            if now > competition.registration_deadline:
                self.logger.warning(f"Registration deadline passed for competition {competition_id}")
                return False
            
            # Check if user already registered
            competition_participants = self.participants.get(competition_id, [])
            if any(p.user_id == user_id for p in competition_participants):
                self.logger.warning(f"User {user_id} already registered for competition {competition_id}")
                return False
            
            # Check participant limit
            if competition.max_participants and len(competition_participants) >= competition.max_participants:
                self.logger.warning(f"Competition {competition_id} is full")
                return False
            
            # Check entry fee (simplified)
            if competition.entry_fee:
                # In a real implementation, would process payment
                self.logger.info(f"Entry fee required: {competition.entry_fee}")
            
            # Create participant
            participant = CompetitionParticipant(
                id=f"{user_id}_{competition_id}",
                user_id=user_id,
                competition_id=competition_id,
                status=ParticipantStatus.REGISTERED,
                registration_date=now,
                metadata=metadata or {}
            )
            
            # Add participant
            competition_participants.append(participant)
            competition.current_participants = len(competition_participants)
            
            self.logger.info(f"User {user_id} registered for competition '{competition.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering participant: {e}")
            return False
    
    async def close_registration(self, competition_id: str) -> bool:
        """Close registration and prepare competition."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                return False
            
            if competition.status != CompetitionStatus.REGISTRATION_OPEN:
                return False
            
            # Check minimum participants
            if competition.current_participants < competition.min_participants:
                self.logger.warning(f"Not enough participants for competition {competition_id}")
                competition.status = CompetitionStatus.CANCELLED
                return False
            
            competition.status = CompetitionStatus.REGISTRATION_CLOSED
            
            # Generate bracket if needed
            if competition.format in [CompetitionFormat.SINGLE_ELIMINATION, CompetitionFormat.DOUBLE_ELIMINATION]:
                await self._generate_bracket(competition_id)
            
            self.logger.info(f"Closed registration for competition '{competition.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing registration: {e}")
            return False
    
    async def _generate_bracket(self, competition_id: str) -> bool:
        """Generate tournament bracket."""
        try:
            competition = self.active_competitions.get(competition_id)
            participants = self.participants.get(competition_id, [])
            
            if not competition or not participants:
                return False
            
            # Shuffle participants for fair bracket
            random.shuffle(participants)
            
            # Calculate rounds needed
            participant_count = len(participants)
            total_rounds = 1
            while (2 ** total_rounds) < participant_count:
                total_rounds += 1
            
            # Create bracket
            bracket = CompetitionBracket(
                competition_id=competition_id,
                total_rounds=total_rounds
            )
            
            # Generate first round matches
            matches = []
            match_number = 1
            
            for i in range(0, len(participants), 2):
                participant1 = participants[i]
                participant2 = participants[i + 1] if i + 1 < len(participants) else None
                
                match = CompetitionMatch(
                    id=f"{competition_id}_r1_m{match_number}",
                    competition_id=competition_id,
                    round_number=1,
                    match_number=match_number,
                    participant1_id=participant1.user_id,
                    participant2_id=participant2.user_id if participant2 else None,
                    status="scheduled"
                )
                
                # If no opponent, automatic win (bye)
                if not participant2:
                    match.winner_id = participant1.user_id
                    match.status = "completed"
                
                matches.append(match)
                match_number += 1
            
            bracket.matches = matches
            self.brackets[competition_id] = bracket
            self.matches[competition_id] = matches
            
            self.logger.info(f"Generated bracket for competition '{competition.title}' with {len(matches)} first round matches")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating bracket: {e}")
            return False
    
    async def start_competition(self, competition_id: str) -> bool:
        """Start a competition."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                return False
            
            if competition.status != CompetitionStatus.REGISTRATION_CLOSED:
                return False
            
            # Check start date
            now = datetime.now(timezone.utc)
            if now < competition.start_date:
                self.logger.warning(f"Competition {competition_id} not ready to start")
                return False
            
            competition.status = CompetitionStatus.IN_PROGRESS
            
            # Update participant statuses
            participants = self.participants.get(competition_id, [])
            for participant in participants:
                participant.status = ParticipantStatus.ACTIVE
            
            self.logger.info(f"Started competition '{competition.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting competition: {e}")
            return False
    
    async def submit_match_result(
        self,
        competition_id: str,
        match_id: str,
        winner_user_id: str,
        scores: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Submit result for a match."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition or competition.status != CompetitionStatus.IN_PROGRESS:
                return False
            
            # Find match
            matches = self.matches.get(competition_id, [])
            match = next((m for m in matches if m.id == match_id), None)
            
            if not match or match.status == "completed":
                return False
            
            # Validate winner
            if winner_user_id not in [match.participant1_id, match.participant2_id]:
                return False
            
            # Update match
            match.winner_id = winner_user_id
            match.scores = scores or {}
            match.status = "completed"
            match.end_time = datetime.now(timezone.utc)
            match.metadata.update(metadata or {})
            
            # Update participant stats
            participants = self.participants.get(competition_id, [])
            for participant in participants:
                if participant.user_id == match.participant1_id or participant.user_id == match.participant2_id:
                    participant.matches_played += 1
                    if participant.user_id == winner_user_id:
                        participant.matches_won += 1
                    else:
                        participant.matches_lost += 1
            
            # Check if round is complete and advance bracket
            await self._check_round_completion(competition_id)
            
            self.logger.info(f"Match result submitted: {winner_user_id} won in competition '{competition.title}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting match result: {e}")
            return False
    
    async def _check_round_completion(self, competition_id: str):
        """Check if current round is complete and advance to next round."""
        try:
            bracket = self.brackets.get(competition_id)
            if not bracket:
                return
            
            # Find matches in current round
            matches = self.matches.get(competition_id, [])
            current_round_matches = [m for m in matches if m.round_number == bracket.current_round]
            
            # Check if all matches are completed
            completed_matches = [m for m in current_round_matches if m.status == "completed"]
            
            if len(completed_matches) == len(current_round_matches):
                # Round is complete, advance to next round
                if bracket.current_round < bracket.total_rounds:
                    await self._generate_next_round(competition_id)
                else:
                    # Tournament is complete
                    await self._complete_competition(competition_id)
        
        except Exception as e:
            self.logger.error(f"Error checking round completion: {e}")
    
    async def _generate_next_round(self, competition_id: str):
        """Generate matches for the next round."""
        try:
            bracket = self.brackets.get(competition_id)
            matches = self.matches.get(competition_id, [])
            
            if not bracket:
                return
            
            next_round = bracket.current_round + 1
            
            # Get winners from current round
            current_round_matches = [m for m in matches if m.round_number == bracket.current_round]
            winners = [m.winner_id for m in current_round_matches if m.winner_id]
            
            # Generate next round matches
            new_matches = []
            match_number = 1
            
            for i in range(0, len(winners), 2):
                participant1 = winners[i]
                participant2 = winners[i + 1] if i + 1 < len(winners) else None
                
                match = CompetitionMatch(
                    id=f"{competition_id}_r{next_round}_m{match_number}",
                    competition_id=competition_id,
                    round_number=next_round,
                    match_number=match_number,
                    participant1_id=participant1,
                    participant2_id=participant2,
                    status="scheduled"
                )
                
                # If odd number of winners, bye to finals
                if not participant2:
                    match.winner_id = participant1
                    match.status = "completed"
                
                new_matches.append(match)
                matches.append(match)
                match_number += 1
            
            bracket.current_round = next_round
            
            self.logger.info(f"Generated round {next_round} with {len(new_matches)} matches")
            
        except Exception as e:
            self.logger.error(f"Error generating next round: {e}")
    
    async def _complete_competition(self, competition_id: str):
        """Complete a competition and award prizes."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                return
            
            competition.status = CompetitionStatus.COMPLETED
            
            # Determine final rankings
            rankings = await self._calculate_final_rankings(competition_id)
            
            # Award prizes
            await self._award_competition_prizes(competition_id, rankings)
            
            # Update participant statuses
            participants = self.participants.get(competition_id, [])
            for i, participant in enumerate(participants):
                if i == 0:  # Winner
                    participant.status = ParticipantStatus.WINNER
                else:
                    participant.status = ParticipantStatus.ELIMINATED
                participant.current_rank = i + 1
            
            self.logger.info(f"🏆 Competition '{competition.title}' completed")
            
        except Exception as e:
            self.logger.error(f"Error completing competition: {e}")
    
    async def _calculate_final_rankings(self, competition_id: str) -> List[str]:
        """Calculate final rankings for participants."""
        try:
            competition = self.active_competitions.get(competition_id)
            participants = self.participants.get(competition_id, [])
            
            if competition.format in [CompetitionFormat.SINGLE_ELIMINATION, CompetitionFormat.DOUBLE_ELIMINATION]:
                # For tournaments, use bracket results
                bracket = self.brackets.get(competition_id)
                if bracket:
                    final_matches = [m for m in self.matches.get(competition_id, []) if m.round_number == bracket.total_rounds]
                    if final_matches:
                        final_match = final_matches[0]
                        winner = final_match.winner_id
                        runner_up = final_match.participant1_id if final_match.participant2_id == winner else final_match.participant2_id
                        
                        # Build ranking (simplified)
                        rankings = [winner, runner_up] if runner_up else [winner]
                        
                        # Add other participants (simplified ranking)
                        other_participants = [p.user_id for p in participants if p.user_id not in rankings]
                        rankings.extend(other_participants)
                        
                        return rankings
            
            # For other formats, rank by wins/score
            participants.sort(key=lambda p: (p.matches_won, p.current_score), reverse=True)
            return [p.user_id for p in participants]
            
        except Exception as e:
            self.logger.error(f"Error calculating final rankings: {e}")
            return []
    
    async def _award_competition_prizes(self, competition_id: str, rankings: List[str]):
        """Award prizes to competition winners."""
        try:
            competition = self.active_competitions.get(competition_id)
            if not competition:
                return
            
            from ..rewards.reward_distributor import get_reward_distributor
            reward_distributor = get_reward_distributor()
            
            for reward in competition.rewards:
                if reward.position <= len(rankings):
                    winner_user_id = rankings[reward.position - 1]  # Convert to 0-based index
                    
                    await reward_distributor.distribute_reward(
                        user_id=winner_user_id,
                        reward_type=reward.reward_type,
                        name=f"Competition Prize - {competition.title}",
                        description=f"{reward.description} (Position: {reward.position})",
                        value=reward.amount,
                        currency_type=reward.currency,
                        trigger_source_id=competition_id,
                        metadata={
                            "competition_id": competition_id,
                            "position": reward.position,
                            "competition_type": competition.competition_type
                        }
                    )
            
        except Exception as e:
            self.logger.error(f"Error awarding competition prizes: {e}")
    
    async def get_active_competitions(
        self,
        competition_type: Optional[CompetitionType] = None,
        status: Optional[CompetitionStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get active competitions with optional filtering."""
        try:
            competitions = []
            
            for competition in self.active_competitions.values():
                # Apply filters
                if competition_type and competition.competition_type != competition_type:
                    continue
                if status and competition.status != status:
                    continue
                
                competitions.append({
                    "id": competition.id,
                    "title": competition.title,
                    "description": competition.description,
                    "competition_type": competition.competition_type,
                    "format": competition.format,
                    "status": competition.status,
                    "start_date": competition.start_date.isoformat(),
                    "end_date": competition.end_date.isoformat(),
                    "registration_deadline": competition.registration_deadline.isoformat(),
                    "current_participants": competition.current_participants,
                    "max_participants": competition.max_participants,
                    "min_participants": competition.min_participants,
                    "entry_fee": competition.entry_fee,
                    "tags": competition.tags,
                    "rewards": [
                        {
                            "position": r.position,
                            "reward_type": r.reward_type,
                            "amount": r.amount,
                            "currency": r.currency,
                            "description": r.description
                        }
                        for r in competition.rewards
                    ]
                })
            
            return competitions
            
        except Exception as e:
            self.logger.error(f"Error getting active competitions: {e}")
            return []
    
    async def get_competition_leaderboard(
        self,
        competition_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific competition."""
        try:
            participants = self.participants.get(competition_id, [])
            
            # Sort by current rank or performance metrics
            sorted_participants = sorted(
                participants,
                key=lambda p: (p.current_rank if p.current_rank > 0 else 999, -p.matches_won, -p.current_score)
            )
            
            leaderboard = []
            for i, participant in enumerate(sorted_participants[:limit]):
                leaderboard.append({
                    "rank": i + 1,
                    "user_id": participant.user_id,
                    "status": participant.status,
                    "current_score": participant.current_score,
                    "matches_played": participant.matches_played,
                    "matches_won": participant.matches_won,
                    "matches_lost": participant.matches_lost,
                    "win_rate": participant.matches_won / max(participant.matches_played, 1),
                    "registration_date": participant.registration_date.isoformat()
                })
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Error getting competition leaderboard: {e}")
            return []
    
    async def get_user_competitions(
        self,
        user_id: str,
        status: Optional[ParticipantStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get competitions a user is participating in."""
        try:
            user_competitions = []
            
            for competition_id, participants in self.participants.items():
                user_participant = next((p for p in participants if p.user_id == user_id), None)
                
                if user_participant and (not status or user_participant.status == status):
                    competition = self.active_competitions.get(competition_id)
                    if competition:
                        user_competitions.append({
                            "competition_id": competition.id,
                            "title": competition.title,
                            "competition_type": competition.competition_type,
                            "status": competition.status,
                            "participant_status": user_participant.status,
                            "current_rank": user_participant.current_rank,
                            "matches_played": user_participant.matches_played,
                            "matches_won": user_participant.matches_won,
                            "start_date": competition.start_date.isoformat(),
                            "end_date": competition.end_date.isoformat()
                        })
            
            return user_competitions
            
        except Exception as e:
            self.logger.error(f"Error getting user competitions: {e}")
            return []


# Global instance
_competition_engine = None

def get_competition_engine(database_connection=None, cache_client=None) -> CompetitionEngine:
    """Get the global competition engine instance."""
    global _competition_engine
    if _competition_engine is None:
        _competition_engine = CompetitionEngine(database_connection, cache_client)
    return _competition_engine