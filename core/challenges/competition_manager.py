"""🏆 Competition Manager - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/core/challenges/competition_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Competition Management System - Production-Ready
Responsibility: Enterprise competition lifecycle and tournament management
==========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Competition Creation → Registration → Tournament Brackets → Matchmaking → 
Live Scoring → Real-time Leaderboards → Prize Distribution → Community Engagement

COMPETITION ARCHITECTURE:
Tournament Engine → Bracket Manager → Matchmaking System → 
Live Score Tracker → Prize Pool Manager → Broadcasting System
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
import asyncio
import uuid
import json
from abc import ABC, abstractmethod

class CompetitionType(Enum):
    """Types of competitions supported"""    TOURNAMENT = "tournament"
    LEAGUE = "league"
    BATTLE_ROYALE = "battle_royale"
    ELIMINATION = "elimination"
    ROUND_ROBIN = "round_robin"
    BRACKET = "bracket"
    LADDER = "ladder"
    TEAM_VS_TEAM = "team_vs_team"
    FREE_FOR_ALL = "free_for_all"
    TIMED_CHALLENGE = "timed_challenge"

class CompetitionStatus(Enum):
    """Competition lifecycle status"""    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class CompetitionPhase(Enum):
    """Competition phases"""    PREPARATION = "preparation"
    REGISTRATION = "registration"
    SEEDING = "seeding"
    QUALIFIER = "qualifier"
    PRELIMINARY = "preliminary"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    FINAL = "final"
    AWARDS = "awards"
    WRAP_UP = "wrap_up"

class ParticipationStatus(Enum):
    """Participant status in competition"""    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    WITHDRAWN = "withdrawn"
    DISQUALIFIED = "disqualified"
    WINNER = "winner"
    RUNNER_UP = "runner_up"

class MatchResult(Enum):
    """Match result outcomes"""    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    FORFEIT = "forfeit"
    NO_CONTEST = "no_contest"
    PENDING = "pending"

@dataclass
class CompetitionRule:
    """Individual competition rule specification"""    rule_id: str
    rule_name: str
    description: str
    rule_type: str  # "scoring", "elimination", "advancement", "conduct"
    parameters: Dict[str, Any]
    is_mandatory: bool = True
    violation_penalty: str = "warning"  # "warning", "point_deduction", "elimination"
    
@dataclass
class PrizePool:
    """Competition prize pool configuration"""    total_value: Decimal
    currency_type: str  # "virtual", "real", "mixed"
    distribution_method: str  # "winner_takes_all", "top_percentage", "participation"
    prize_breakdown: Dict[str, Decimal]  # position -> amount
    bonus_prizes: Dict[str, Any] = field(default_factory=dict)
    sponsor_contributions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MatchConfiguration:
    """Match/round configuration"""    match_id: str
    match_type: str  # "head_to_head", "group", "time_trial"
    participants: List[str]  # participant IDs
    rules: List[CompetitionRule]
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    scoring_method: str = "points"
    tiebreaker_rules: List[str] = field(default_factory=list)

@dataclass
class CompetitionConfiguration:
    """Complete competition configuration"""    competition_id: str
    title: str
    description: str
    competition_type: CompetitionType
    category: str
    
    # Timing and structure
    registration_start: datetime
    registration_end: datetime
    competition_start: datetime
    competition_end: datetime
    timezone: str = "UTC"
    
    # Participation
    max_participants: Optional[int] = None
    min_participants: int = 2
    team_based: bool = False
    max_team_size: int = 1
    allow_substitutes: bool = False
    
    # Competition structure
    phases: List[CompetitionPhase] = field(default_factory=list)
    rules: List[CompetitionRule] = field(default_factory=list)
    elimination_criteria: Dict[str, Any] = field(default_factory=dict)
    advancement_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Rewards and prizes
    prize_pool: Optional[PrizePool] = None
    achievement_rewards: List[str] = field(default_factory=list)
    participation_rewards: Dict[str, Any] = field(default_factory=dict)
    
    # Broadcasting and community
    is_public: bool = True
    allow_spectators: bool = True
    live_streaming: bool = False
    community_voting: bool = False
    
    # Metadata
    organizer_id: str = ""
    sponsors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CompetitionManager:
    """Enterprise competition management system"""    
    def __init__(self,
                 competition_repository=None,
                 challenge_repository=None,
                 user_service=None,
                 analytics_service=None,
                 notification_service=None,
                 reward_service=None,
                 streaming_service=None,
                 matchmaking_service=None):
        """Initialize competition manager with dependencies"""        self.competition_repository = competition_repository
        self.challenge_repository = challenge_repository
        self.user_service = user_service
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.reward_service = reward_service
        self.streaming_service = streaming_service
        self.matchmaking_service = matchmaking_service
        
        self.logger = logging.getLogger(__name__)
        
        # Competition type configurations
        self._competition_type_configs = {
            CompetitionType.TOURNAMENT: {
                "requires_brackets": True,
                "supports_elimination": True,
                "max_phases": 6,
                "recommended_duration_hours": 24
            },
            CompetitionType.LEAGUE: {
                "requires_brackets": False,
                "supports_elimination": False,
                "max_phases": 3,
                "recommended_duration_hours": 168  # 1 week
            },
            CompetitionType.BATTLE_ROYALE: {
                "requires_brackets": False,
                "supports_elimination": True,
                "max_phases": 2,
                "recommended_duration_hours": 2
            },
            CompetitionType.LADDER: {
                "requires_brackets": False,
                "supports_elimination": False,
                "max_phases": 2,
                "recommended_duration_hours": 720  # 30 days
            }
        }
        
        # Phase progression rules
        self._phase_progression = {
            CompetitionPhase.PREPARATION: [CompetitionPhase.REGISTRATION],
            CompetitionPhase.REGISTRATION: [CompetitionPhase.SEEDING, CompetitionPhase.QUALIFIER],
            CompetitionPhase.SEEDING: [CompetitionPhase.PRELIMINARY],
            CompetitionPhase.QUALIFIER: [CompetitionPhase.PRELIMINARY],
            CompetitionPhase.PRELIMINARY: [CompetitionPhase.QUARTER_FINAL],
            CompetitionPhase.QUARTER_FINAL: [CompetitionPhase.SEMI_FINAL],
            CompetitionPhase.SEMI_FINAL: [CompetitionPhase.FINAL],
            CompetitionPhase.FINAL: [CompetitionPhase.AWARDS],
            CompetitionPhase.AWARDS: [CompetitionPhase.WRAP_UP]
        }
    
    async def create_competition(self, config: CompetitionConfiguration) -> Dict[str, Any]:
        """Create a new competition with comprehensive setup"""        try:
            # Validate competition configuration
            validation_result = await self._validate_competition_config(config)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": "Invalid competition configuration",
                    "validation_errors": validation_result["errors"]
                }
            
            # Generate unique competition ID if not provided
            if not config.competition_id:
                config.competition_id = f"comp_{uuid.uuid4().hex[:12]}"
            
            # Apply competition type defaults
            config = self._apply_competition_type_defaults(config)
            
            # Initialize competition phases if not specified
            if not config.phases:
                config.phases = self._generate_default_phases(config.competition_type)
            
            # Create competition record
            competition_data = {
                "competition_id": config.competition_id,
                "configuration": config.__dict__,
                "status": CompetitionStatus.DRAFT.value,
                "current_phase": CompetitionPhase.PREPARATION.value,
                "participants": [],
                "matches": [],
                "leaderboard": [],
                "statistics": {
                    "total_registered": 0,
                    "total_matches": 0,
                    "total_prize_awarded": Decimal("0.00"),
                    "spectators_count": 0
                },
                "creation_timestamp": datetime.now(timezone.utc)
            }
            
            # Save to repository
            competition = await self.competition_repository.create_competition(competition_data)
            
            # Setup initial brackets/structure if required
            if self._competition_type_configs[config.competition_type]["requires_brackets"]:
                await self._initialize_bracket_structure(config)
            
            # Schedule automatic phase transitions
            await self._schedule_phase_transitions(config)
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "competition_created",
                    {
                        "competition_id": config.competition_id,
                        "competition_type": config.competition_type.value,
                        "category": config.category,
                        "organizer_id": config.organizer_id,
                        "max_participants": config.max_participants
                    }
                )
            
            self.logger.info(f"Competition created successfully: {config.competition_id}")
            
            return {
                "success": True,
                "competition_id": config.competition_id,
                "competition": competition,
                "status": CompetitionStatus.DRAFT.value,
                "registration_opens": config.registration_start,
                "estimated_participants": self._estimate_participants(config)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create competition: {str(e)}")
            return {
                "success": False,
                "error": f"Competition creation failed: {str(e)}"
            }
    
    async def register_participant(self, 
                                 competition_id: str,
                                 participant_id: str,
                                 team_id: Optional[str] = None,
                                 registration_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register participant for competition"""        try:
            # Get competition configuration
            competition = await self.competition_repository.get_competition(competition_id)
            if not competition:
                return {"success": False, "error": "Competition not found"}
            
            config = CompetitionConfiguration(**competition["configuration"])
            
            # Validate registration eligibility
            eligibility = await self._check_registration_eligibility(
                competition_id, participant_id, config
            )
            
            if not eligibility["eligible"]:
                return {
                    "success": False,
                    "error": "Registration not allowed",
                    "reason": eligibility["reason"]
                }
            
            # Create participation record
            participation_data = {
                "participant_id": participant_id,
                "competition_id": competition_id,
                "team_id": team_id,
                "registration_date": datetime.now(timezone.utc),
                "status": ParticipationStatus.REGISTERED.value,
                "seed": None,  # Will be assigned during seeding
                "statistics": {
                    "matches_played": 0,
                    "matches_won": 0,
                    "matches_lost": 0,
                    "points_scored": 0,
                    "elimination_round": None
                },
                "registration_metadata": registration_data or {}
            }
            
            # Register in repository
            participation = await self.competition_repository.register_participant(
                competition_id, participant_id, participation_data
            )
            
            # Update competition statistics
            await self._update_competition_statistics(
                competition_id, {"participants_count": 1}
            )
            
            # Send confirmation notification
            if self.notification_service:
                await self.notification_service.send_notification(
                    participant_id,
                    "competition_registration_success",
                    {
                        "competition_title": config.title,
                        "competition_id": competition_id,
                        "start_date": config.competition_start.isoformat()
                    }
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "competition_registration",
                    {
                        "competition_id": competition_id,
                        "participant_id": participant_id,
                        "competition_type": config.competition_type.value,
                        "team_registration": team_id is not None
                    }
                )
            
            return {
                "success": True,
                "participation": participation,
                "competition_starts": config.competition_start,
                "current_participants": await self._get_participants_count(competition_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register participant: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def start_competition(self, competition_id: str) -> Dict[str, Any]:
        """Start competition and begin first phase"""        try:
            # Get competition configuration
            competition = await self.competition_repository.get_competition(competition_id)
            if not competition:
                return {"success": False, "error": "Competition not found"}
            
            config = CompetitionConfiguration(**competition["configuration"])
            current_status = CompetitionStatus(competition["status"])
            
            # Validate competition can be started
            if current_status != CompetitionStatus.REGISTRATION_CLOSED:
                return {
                    "success": False,
                    "error": f"Competition cannot be started from status: {current_status.value}"
                }
            
            # Check minimum participants
            participants_count = await self._get_participants_count(competition_id)
            if participants_count < config.min_participants:
                return {
                    "success": False,
                    "error": f"Insufficient participants. Required: {config.min_participants}, Current: {participants_count}"
                }
            
            # Perform seeding if required
            seeding_result = await self._perform_seeding(competition_id, config)
            if not seeding_result["success"]:
                return {
                    "success": False,
                    "error": "Seeding failed",
                    "details": seeding_result["error"]
                }
            
            # Initialize first competitive phase
            first_phase = self._get_first_competitive_phase(config.phases)
            phase_result = await self._initialize_phase(competition_id, first_phase, config)
            
            if not phase_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to initialize first phase",
                    "details": phase_result["error"]
                }
            
            # Update competition status
            await self.competition_repository.update_competition_status(
                competition_id,
                CompetitionStatus.IN_PROGRESS.value,
                first_phase.value
            )
            
            # Send start notifications to all participants
            if self.notification_service:
                participants = await self.competition_repository.get_competition_participants(
                    competition_id
                )
                
                for participant in participants:
                    await self.notification_service.send_notification(
                        participant["participant_id"],
                        "competition_started",
                        {
                            "competition_title": config.title,
                            "competition_id": competition_id,
                            "current_phase": first_phase.value,
                            "your_seed": participant.get("seed")
                        }
                    )
            
            # Initialize live streaming if enabled
            if config.live_streaming and self.streaming_service:
                streaming_result = await self.streaming_service.start_competition_stream(
                    competition_id, config.__dict__
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "competition_started",
                    {
                        "competition_id": competition_id,
                        "participants_count": participants_count,
                        "competition_type": config.competition_type.value,
                        "first_phase": first_phase.value
                    }
                )
            
            self.logger.info(f"Competition started successfully: {competition_id}")
            
            return {
                "success": True,
                "competition_id": competition_id,
                "status": CompetitionStatus.IN_PROGRESS.value,
                "current_phase": first_phase.value,
                "participants_count": participants_count,
                "seeding_results": seeding_result.get("seeding"),
                "first_matches": phase_result.get("matches")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start competition: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def advance_phase(self, competition_id: str) -> Dict[str, Any]:
        """Advance competition to next phase"""        try:
            # Get current competition state
            competition = await self.competition_repository.get_competition(competition_id)
            if not competition:
                return {"success": False, "error": "Competition not found"}
            
            config = CompetitionConfiguration(**competition["configuration"])
            current_phase = CompetitionPhase(competition["current_phase"])
            
            # Validate phase can be advanced
            phase_validation = await self._validate_phase_advancement(
                competition_id, current_phase, config
            )
            
            if not phase_validation["can_advance"]:
                return {
                    "success": False,
                    "error": "Phase cannot be advanced",
                    "reason": phase_validation["reason"]
                }
            
            # Determine next phase
            next_phase = self._get_next_phase(current_phase, config)
            if not next_phase:
                # Competition is complete
                return await self._complete_competition(competition_id, config)
            
            # Finalize current phase
            finalization_result = await self._finalize_current_phase(
                competition_id, current_phase, config
            )
            
            # Initialize next phase
            phase_result = await self._initialize_phase(competition_id, next_phase, config)
            
            if not phase_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to initialize next phase",
                    "details": phase_result["error"]
                }
            
            # Update competition phase
            await self.competition_repository.update_competition_status(
                competition_id,
                CompetitionStatus.IN_PROGRESS.value,
                next_phase.value
            )
            
            # Send phase advancement notifications
            if self.notification_service:
                await self._send_phase_advancement_notifications(
                    competition_id, current_phase, next_phase, config
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "competition_phase_advanced",
                    {
                        "competition_id": competition_id,
                        "from_phase": current_phase.value,
                        "to_phase": next_phase.value,
                        "competition_type": config.competition_type.value
                    }
                )
            
            return {
                "success": True,
                "competition_id": competition_id,
                "previous_phase": current_phase.value,
                "current_phase": next_phase.value,
                "phase_summary": finalization_result,
                "upcoming_matches": phase_result.get("matches", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to advance competition phase: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def record_match_result(self, 
                                competition_id: str,
                                match_id: str,
                                results: Dict[str, Any]) -> Dict[str, Any]:
        """Record match result and update standings"""        try:
            # Validate match exists and is active
            match = await self.competition_repository.get_match(competition_id, match_id)
            if not match:
                return {"success": False, "error": "Match not found"}
            
            if match["status"] != "active":
                return {"success": False, "error": "Match is not active"}
            
            # Validate result data
            validation_result = await self._validate_match_result(match, results)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": "Invalid match result",
                    "validation_errors": validation_result["errors"]
                }
            
            # Process match result
            processed_result = await self._process_match_result(match, results)
            
            # Update match record
            await self.competition_repository.update_match_result(
                competition_id, match_id, processed_result
            )
            
            # Update participant statistics
            await self._update_participant_statistics(
                competition_id, processed_result["participants"], processed_result["outcome"]
            )
            
            # Update competition leaderboard
            await self._update_competition_leaderboard(competition_id)
            
            # Check if phase is complete
            phase_complete = await self._check_phase_completion(competition_id)
            
            # Send result notifications
            if self.notification_service:
                await self._send_match_result_notifications(
                    competition_id, match_id, processed_result
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "match_result_recorded",
                    {
                        "competition_id": competition_id,
                        "match_id": match_id,
                        "participants": processed_result["participants"],
                        "result_type": processed_result["result_type"]
                    }
                )
            
            result_data = {
                "success": True,
                "match_id": match_id,
                "result": processed_result,
                "leaderboard_updated": True,
                "phase_complete": phase_complete["complete"]
            }
            
            # Auto-advance phase if complete
            if phase_complete["complete"] and phase_complete["can_advance"]:
                advancement_result = await self.advance_phase(competition_id)
                result_data["phase_advanced"] = advancement_result["success"]
                result_data["new_phase"] = advancement_result.get("current_phase")
            
            return result_data
            
        except Exception as e:
            self.logger.error(f"Failed to record match result: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_competition_status(self, competition_id: str) -> Dict[str, Any]:
        """Get comprehensive competition status"""        try:
            # Get competition data
            competition = await self.competition_repository.get_competition(competition_id)
            if not competition:
                return {"success": False, "error": "Competition not found"}
            
            config = CompetitionConfiguration(**competition["configuration"])
            
            # Get participants and their status
            participants = await self.competition_repository.get_competition_participants(
                competition_id
            )
            
            # Get current matches
            current_matches = await self.competition_repository.get_active_matches(
                competition_id
            )
            
            # Get leaderboard
            leaderboard = await self.competition_repository.get_competition_leaderboard(
                competition_id
            )
            
            # Calculate progress metrics
            progress_metrics = await self._calculate_progress_metrics(
                competition, participants, current_matches
            )
            
            return {
                "success": True,
                "competition_id": competition_id,
                "title": config.title,
                "status": competition["status"],
                "current_phase": competition["current_phase"],
                "progress": progress_metrics,
                "participants": {
                    "total": len(participants),
                    "active": len([p for p in participants if p["status"] == "active"]),
                    "eliminated": len([p for p in participants if p["status"] == "eliminated"])
                },
                "matches": {
                    "total": competition["statistics"]["total_matches"],
                    "active": len(current_matches),
                    "completed": competition["statistics"]["total_matches"] - len(current_matches)
                },
                "leaderboard": leaderboard[:10],  # Top 10
                "next_phase": self._get_next_phase(
                    CompetitionPhase(competition["current_phase"]), config
                ),
                "estimated_completion": self._estimate_completion_time(
                    competition, config
                )
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get competition status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_live_leaderboard(self, 
                                 competition_id: str,
                                 limit: int = 50) -> Dict[str, Any]:
        """Get live competition leaderboard"""        try:
            # Get current leaderboard
            leaderboard = await self.competition_repository.get_competition_leaderboard(
                competition_id, limit=limit
            )
            
            # Enrich with real-time data
            enriched_leaderboard = await self._enrich_leaderboard_with_live_data(
                competition_id, leaderboard
            )
            
            # Get competition context
            competition = await self.competition_repository.get_competition(competition_id)
            config = CompetitionConfiguration(**competition["configuration"])
            
            return {
                "success": True,
                "competition_id": competition_id,
                "competition_title": config.title,
                "current_phase": competition["current_phase"],
                "leaderboard": enriched_leaderboard,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_participants": len(enriched_leaderboard),
                "prize_pool": config.prize_pool.__dict__ if config.prize_pool else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get live leaderboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Private helper methods
    
    async def _validate_competition_config(self, config: CompetitionConfiguration) -> Dict[str, Any]:
        """Validate competition configuration"""        errors = []
        
        # Basic validation
        if not config.title or len(config.title.strip()) < 3:
            errors.append("Competition title must be at least 3 characters")
        
        if not config.description or len(config.description.strip()) < 10:
            errors.append("Competition description must be at least 10 characters")
        
        # Date validation
        now = datetime.now(timezone.utc)
        
        if config.registration_start < now - timedelta(minutes=5):
            errors.append("Registration start cannot be in the past")
        
        if config.registration_end <= config.registration_start:
            errors.append("Registration end must be after registration start")
        
        if config.competition_start <= config.registration_end:
            errors.append("Competition start must be after registration end")
        
        if config.competition_end <= config.competition_start:
            errors.append("Competition end must be after competition start")
        
        # Participant validation
        if config.max_participants and config.max_participants < config.min_participants:
            errors.append("Maximum participants cannot be less than minimum")
        
        if config.min_participants < 2:
            errors.append("Minimum participants must be at least 2")
        
        # Team validation
        if config.team_based and config.max_team_size < 2:
            errors.append("Team-based competitions must allow teams of at least 2")
        
        # Prize pool validation
        if config.prize_pool:
            if config.prize_pool.total_value <= 0:
                errors.append("Prize pool total value must be positive")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _apply_competition_type_defaults(self, config: CompetitionConfiguration) -> CompetitionConfiguration:
        """Apply default settings based on competition type"""        type_config = self._competition_type_configs.get(config.competition_type, {})
        
        # Set recommended duration if not specified
        if not config.competition_end:
            recommended_hours = type_config.get("recommended_duration_hours", 24)
            config.competition_end = config.competition_start + timedelta(hours=recommended_hours)
        
        return config
    
    def _generate_default_phases(self, competition_type: CompetitionType) -> List[CompetitionPhase]:
        """Generate default phases for competition type"""        if competition_type == CompetitionType.TOURNAMENT:
            return [
                CompetitionPhase.PREPARATION,
                CompetitionPhase.REGISTRATION,
                CompetitionPhase.SEEDING,
                CompetitionPhase.PRELIMINARY,
                CompetitionPhase.QUARTER_FINAL,
                CompetitionPhase.SEMI_FINAL,
                CompetitionPhase.FINAL,
                CompetitionPhase.AWARDS
            ]
        elif competition_type == CompetitionType.LEAGUE:
            return [
                CompetitionPhase.PREPARATION,
                CompetitionPhase.REGISTRATION,
                CompetitionPhase.PRELIMINARY,
                CompetitionPhase.AWARDS
            ]
        elif competition_type == CompetitionType.BATTLE_ROYALE:
            return [
                CompetitionPhase.PREPARATION,
                CompetitionPhase.REGISTRATION,
                CompetitionPhase.QUALIFIER,
                CompetitionPhase.AWARDS
            ]
        else:
            return [
                CompetitionPhase.PREPARATION,
                CompetitionPhase.REGISTRATION,
                CompetitionPhase.PRELIMINARY,
                CompetitionPhase.AWARDS
            ]
    
    async def _check_registration_eligibility(self, 
                                            competition_id: str,
                                            participant_id: str,
                                            config: CompetitionConfiguration) -> Dict[str, Any]:
        """Check if participant is eligible to register"""        now = datetime.now(timezone.utc)
        
        # Check registration window
        if now < config.registration_start:
            return {"eligible": False, "reason": "Registration has not opened yet"}
        
        if now > config.registration_end:
            return {"eligible": False, "reason": "Registration has closed"}
        
        # Check if already registered
        existing_participation = await self.competition_repository.get_participant(
            competition_id, participant_id
        )
        
        if existing_participation:
            return {"eligible": False, "reason": "Already registered"}
        
        # Check participant limits
        current_participants = await self._get_participants_count(competition_id)
        
        if config.max_participants and current_participants >= config.max_participants:
            return {"eligible": False, "reason": "Competition is at maximum capacity"}
        
        # Check user eligibility (if user service available)
        if self.user_service:
            user_eligibility = await self._check_user_eligibility(participant_id, config)
            if not user_eligibility["eligible"]:
                return user_eligibility
        
        return {"eligible": True}
    
    async def _perform_seeding(self, 
                             competition_id: str,
                             config: CompetitionConfiguration) -> Dict[str, Any]:
        """Perform participant seeding"""        try:
            # Get all registered participants
            participants = await self.competition_repository.get_competition_participants(
                competition_id
            )
            
            # Use matchmaking service if available, otherwise use simple ranking
            if self.matchmaking_service:
                seeding_result = await self.matchmaking_service.generate_seeding(
                    participants, config.__dict__
                )
            else:
                seeding_result = await self._simple_seeding(participants)
            
            # Update participant records with seeds
            for participant_id, seed in seeding_result["seeding"].items():
                await self.competition_repository.update_participant_seed(
                    competition_id, participant_id, seed
                )
            
            return {
                "success": True,
                "seeding": seeding_result["seeding"],
                "method": seeding_result.get("method", "random")
            }
            
        except Exception as e:
            self.logger.error(f"Seeding failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _initialize_phase(self, 
                              competition_id: str,
                              phase: CompetitionPhase,
                              config: CompetitionConfiguration) -> Dict[str, Any]:
        """Initialize a competition phase"""        try:
            if phase in [CompetitionPhase.PRELIMINARY, CompetitionPhase.QUARTER_FINAL,
                        CompetitionPhase.SEMI_FINAL, CompetitionPhase.FINAL]:
                # Generate matches for competitive phases
                matches_result = await self._generate_phase_matches(
                    competition_id, phase, config
                )
                return matches_result
            
            return {"success": True, "phase": phase.value}
            
        except Exception as e:
            self.logger.error(f"Failed to initialize phase {phase}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _generate_phase_matches(self, 
                                    competition_id: str,
                                    phase: CompetitionPhase,
                                    config: CompetitionConfiguration) -> Dict[str, Any]:
        """Generate matches for a competitive phase"""        try:
            # Get active participants for this phase
            participants = await self._get_active_participants(competition_id)
            
            # Generate matchups based on competition type and phase
            if config.competition_type == CompetitionType.TOURNAMENT:
                matches = await self._generate_tournament_matches(participants, phase)
            elif config.competition_type == CompetitionType.LEAGUE:
                matches = await self._generate_league_matches(participants, phase)
            else:
                matches = await self._generate_generic_matches(participants, phase)
            
            # Create match records
            created_matches = []
            for match_config in matches:
                match_record = await self.competition_repository.create_match(
                    competition_id, match_config
                )
                created_matches.append(match_record)
            
            return {
                "success": True,
                "matches": created_matches,
                "phase": phase.value
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate phase matches: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_next_phase(self, 
                       current_phase: CompetitionPhase,
                       config: CompetitionConfiguration) -> Optional[CompetitionPhase]:
        """Get next phase in competition progression"""        current_index = config.phases.index(current_phase) if current_phase in config.phases else -1
        
        if current_index >= 0 and current_index < len(config.phases) - 1:
            return config.phases[current_index + 1]
        
        return None
    
    def _get_first_competitive_phase(self, phases: List[CompetitionPhase]) -> CompetitionPhase:
        """Get first competitive phase from phases list"""        competitive_phases = [
            CompetitionPhase.QUALIFIER,
            CompetitionPhase.PRELIMINARY,
            CompetitionPhase.QUARTER_FINAL,
            CompetitionPhase.SEMI_FINAL,
            CompetitionPhase.FINAL
        ]
        
        for phase in phases:
            if phase in competitive_phases:
                return phase
        
        return CompetitionPhase.PRELIMINARY  # Default fallback
    
    async def _validate_phase_advancement(self, 
                                        competition_id: str,
                                        current_phase: CompetitionPhase,
                                        config: CompetitionConfiguration) -> Dict[str, Any]:
        """Validate if phase can be advanced"""        # Check if all matches in current phase are complete
        active_matches = await self.competition_repository.get_active_matches(competition_id)
        
        if active_matches:
            return {
                "can_advance": False,
                "reason": f"{len(active_matches)} matches still active"
            }
        
        # Check minimum progression requirements
        if current_phase in [CompetitionPhase.QUARTER_FINAL, CompetitionPhase.SEMI_FINAL]:
            active_participants = await self._get_active_participants(competition_id)
            required_participants = {
                CompetitionPhase.QUARTER_FINAL: 4,
                CompetitionPhase.SEMI_FINAL: 2
            }.get(current_phase, 1)
            
            if len(active_participants) < required_participants:
                return {
                    "can_advance": False,
                    "reason": f"Insufficient active participants for next phase"
                }
        
        return {"can_advance": True}
    
    async def _complete_competition(self, 
                                  competition_id: str,
                                  config: CompetitionConfiguration) -> Dict[str, Any]:
        """Complete competition and distribute prizes"""        try:
            # Determine final rankings
            final_leaderboard = await self.competition_repository.get_competition_leaderboard(
                competition_id
            )
            
            # Distribute prizes
            prize_distribution = await self._distribute_prizes(
                competition_id, config, final_leaderboard
            )
            
            # Update competition status
            await self.competition_repository.update_competition_status(
                competition_id,
                CompetitionStatus.COMPLETED.value,
                CompetitionPhase.WRAP_UP.value
            )
            
            # Send completion notifications
            if self.notification_service:
                await self._send_completion_notifications(
                    competition_id, config, final_leaderboard
                )
            
            # Track analytics
            if self.analytics_service:
                await self.analytics_service.track_event(
                    "competition_completed",
                    {
                        "competition_id": competition_id,
                        "participants_count": len(final_leaderboard),
                        "competition_type": config.competition_type.value,
                        "total_prize_awarded": str(prize_distribution.get("total_awarded", 0))
                    }
                )
            
            return {
                "success": True,
                "competition_id": competition_id,
                "status": CompetitionStatus.COMPLETED.value,
                "final_leaderboard": final_leaderboard,
                "prize_distribution": prize_distribution,
                "completion_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to complete competition: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Additional helper methods would continue here...
    # For brevity, I'm including key methods but there would be more helper methods
    # for match processing, leaderboard updates, notifications, etc.
    
    async def _get_participants_count(self, competition_id: str) -> int:
        """Get current participants count"""        participants = await self.competition_repository.get_competition_participants(
            competition_id
        )
        return len(participants)
    
    def _estimate_participants(self, config: CompetitionConfiguration) -> int:
        """Estimate expected number of participants"""        base_estimate = {
            CompetitionType.TOURNAMENT: 64,
            CompetitionType.LEAGUE: 20,
            CompetitionType.BATTLE_ROYALE: 100,
            CompetitionType.LADDER: 200
        }.get(config.competition_type, 50)
        
        # Adjust based on competition duration
        duration_hours = (config.competition_end - config.competition_start).total_seconds() / 3600
        
        if duration_hours < 6:
            base_estimate = int(base_estimate * 1.5)  # Short competitions are more popular
        elif duration_hours > 168:  # More than a week
            base_estimate = int(base_estimate * 0.7)  # Long competitions have lower participation
        
        # Cap at max_participants if specified
        if config.max_participants:
            base_estimate = min(base_estimate, config.max_participants)
        
        return base_estimate
    
    async def _simple_seeding(self, participants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple random seeding for participants"""        import random
        
        participant_ids = [p["participant_id"] for p in participants]
        random.shuffle(participant_ids)
        
        seeding = {}
        for i, participant_id in enumerate(participant_ids):
            seeding[participant_id] = i + 1
        
        return {
            "seeding": seeding,
            "method": "random"
        }
    
    async def _update_competition_statistics(self, 
                                           competition_id: str,
                                           updates: Dict[str, Any]):
        """Update competition statistics"""        await self.competition_repository.update_competition_statistics(
            competition_id, updates
        )
    
    async def _get_active_participants(self, competition_id: str) -> List[Dict[str, Any]]:
        """Get list of active participants"""        all_participants = await self.competition_repository.get_competition_participants(
            competition_id
        )
        
        return [
            p for p in all_participants 
            if p["status"] in ["active", "confirmed", "registered"]
        ]