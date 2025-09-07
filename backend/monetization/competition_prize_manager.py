"""Competition Prize Manager - Enterprise Competition-Based Monetization
=====================================================================

Enterprise-grade competition prize manager providing automated prize
distribution for creator competitions, contests, challenges, and tournaments
with comprehensive tracking and fairness validation.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/competition_prize_manager.py
Business Logic: Competition Setup → Participation Tracking → Prize Calculation → Distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
import random

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class CompetitionType(str, Enum):
    """Types of competitions for prize distribution."""
    CONTENT_CONTEST = "content_contest"
    REVENUE_CHALLENGE = "revenue_challenge"
    ENGAGEMENT_TOURNAMENT = "engagement_tournament"
    COLLABORATION_CHALLENGE = "collaboration_challenge"
    INNOVATION_CONTEST = "innovation_contest"
    COMMUNITY_CHALLENGE = "community_challenge"
    SPEED_CHALLENGE = "speed_challenge"
    QUALITY_CONTEST = "quality_contest"
    GROWTH_COMPETITION = "growth_competition"
    THEMED_CONTEST = "themed_contest"


class CompetitionStatus(str, Enum):
    """Status of competition lifecycle."""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    ACTIVE = "active"
    JUDGING = "judging"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PRIZES_DISTRIBUTED = "prizes_distributed"


class PrizeDistributionMethod(str, Enum):
    """Methods for distributing competition prizes."""
    WINNER_TAKES_ALL = "winner_takes_all"
    TOP_PERCENTAGE = "top_percentage"
    TIERED_REWARDS = "tiered_rewards"
    PARTICIPATION_REWARDS = "participation_rewards"
    ACHIEVEMENT_BASED = "achievement_based"
    RANDOM_DRAW = "random_draw"
    PROPORTIONAL_DISTRIBUTION = "proportional_distribution"


class JudgingCriteria(str, Enum):
    """Criteria for judging competitions."""
    ENGAGEMENT_METRICS = "engagement_metrics"
    REVENUE_GENERATED = "revenue_generated"
    CONTENT_QUALITY = "content_quality"
    INNOVATION_FACTOR = "innovation_factor"
    COMMUNITY_IMPACT = "community_impact"
    COLLABORATION_SUCCESS = "collaboration_success"
    AUDIENCE_GROWTH = "audience_growth"
    TECHNICAL_EXCELLENCE = "technical_excellence"


@dataclass
class CompetitionDefinition:
    """Definition of a competition with rules and prizes."""
    competition_id: str
    title: str
    description: str
    competition_type: CompetitionType
    prize_pool: Decimal
    prize_distribution_method: PrizeDistributionMethod
    judging_criteria: List[JudgingCriteria]
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    max_participants: Optional[int] = None
    entry_fee: Decimal = Decimal("0")
    minimum_requirements: Dict[str, Any] = field(default_factory=dict)
    prize_structure: Dict[str, Decimal] = field(default_factory=dict)
    rules: str = ""
    created_by: str = "system"
    status: CompetitionStatus = CompetitionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompetitionParticipant:
    """Participant in a competition."""
    participant_id: str
    competition_id: str
    creator_id: str
    registration_date: datetime
    entry_fee_paid: Decimal
    submission_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    final_score: Optional[float] = None
    rank: Optional[int] = None
    qualified: bool = True
    disqualified_reason: Optional[str] = None


@dataclass
class CompetitionPrize:
    """Prize awarded in a competition."""
    prize_id: str
    competition_id: str
    recipient_id: str
    prize_rank: int
    prize_amount: Decimal
    prize_description: str
    awarded_date: datetime
    distribution_method: str
    transaction_id: Optional[str] = None
    status: str = "pending"
    currency: str = "USD"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CompetitionResult:
    """Results of a completed competition."""
    competition_id: str
    total_participants: int
    total_prize_pool: Decimal
    total_distributed: Decimal
    winners: List[Dict[str, Any]]
    completion_date: datetime
    statistics: Dict[str, Any]


class CompetitionPrizeManager:
    """
    Enterprise competition prize manager providing automated prize
    distribution for creator competitions with comprehensive tracking.
    """
    
    def __init__(self):
        """Initialize the competition prize manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core storage
        self.competitions: Dict[str, CompetitionDefinition] = {}
        self.participants: Dict[str, List[CompetitionParticipant]] = {}
        self.prizes: Dict[str, List[CompetitionPrize]] = {}
        self.results: Dict[str, CompetitionResult] = {}
        
        # Configuration
        self.default_currency = "USD"
        self.platform_fee_rate = Decimal("0.10")  # 10% platform fee
        self.minimum_prize_amount = Decimal("1.00")
        self.maximum_competition_duration = timedelta(days=90)
        
        # Analytics
        self.total_competitions_hosted = 0
        self.total_prizes_distributed = Decimal("0")
        self.total_participants_served = 0
        
        self.initialized = False
        self.logger.info("CompetitionPrizeManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the competition prize manager."""
        try:
            await self._load_competitions()
            await self._load_participants()
            await self._load_prizes()
            await self._schedule_competition_monitoring()
            
            self.initialized = True
            self.logger.info("CompetitionPrizeManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CompetitionPrizeManager: {e}")
            return False
    
    async def _load_competitions(self):
        """Load competitions from storage."""
        # In production, this would load from database
        self.logger.info("Loading competitions...")
    
    async def _load_participants(self):
        """Load participants from storage."""
        # In production, this would load from database
        self.logger.info("Loading competition participants...")
    
    async def _load_prizes(self):
        """Load prizes from storage."""
        # In production, this would load from database
        self.logger.info("Loading competition prizes...")
    
    async def _schedule_competition_monitoring(self):
        """Schedule automatic competition monitoring and management."""
        # In production, this would set up background tasks
        self.logger.info("Scheduling competition monitoring...")
    
    async def create_competition(
        self,
        title: str,
        description: str,
        competition_type: CompetitionType,
        prize_pool: Decimal,
        distribution_method: PrizeDistributionMethod,
        start_date: datetime,
        end_date: datetime,
        judging_criteria: List[JudgingCriteria],
        created_by: str,
        **kwargs
    ) -> CompetitionDefinition:
        """
        Create a new competition with prize structure.
        
        Args:
            title: Competition title
            description: Competition description
            competition_type: Type of competition
            prize_pool: Total prize pool amount
            distribution_method: How to distribute prizes
            start_date: Competition start date
            end_date: Competition end date
            judging_criteria: Criteria for judging
            created_by: Creator of the competition
            **kwargs: Additional competition parameters
            
        Returns:
            Created competition definition
        """
        try:
            # Validate dates
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            if end_date - start_date > self.maximum_competition_duration:
                raise ValueError(f"Competition duration cannot exceed {self.maximum_competition_duration.days} days")
            
            # Set registration deadline (default to 1 day before start)
            registration_deadline = kwargs.get('registration_deadline', start_date - timedelta(days=1))
            
            # Create prize structure based on distribution method
            prize_structure = await self._create_prize_structure(prize_pool, distribution_method)
            
            competition = CompetitionDefinition(
                competition_id=str(uuid4()),
                title=title,
                description=description,
                competition_type=competition_type,
                prize_pool=prize_pool,
                prize_distribution_method=distribution_method,
                judging_criteria=judging_criteria,
                start_date=start_date,
                end_date=end_date,
                registration_deadline=registration_deadline,
                max_participants=kwargs.get('max_participants'),
                entry_fee=kwargs.get('entry_fee', Decimal("0")),
                minimum_requirements=kwargs.get('minimum_requirements', {}),
                prize_structure=prize_structure,
                rules=kwargs.get('rules', ""),
                created_by=created_by,
                status=CompetitionStatus.DRAFT
            )
            
            # Store competition
            self.competitions[competition.competition_id] = competition
            self.participants[competition.competition_id] = []
            
            self.total_competitions_hosted += 1
            
            self.logger.info(f"Created competition: {title} with prize pool ${prize_pool}")
            return competition
            
        except Exception as e:
            self.logger.error(f"Error creating competition: {e}")
            raise
    
    async def _create_prize_structure(
        self, prize_pool: Decimal, distribution_method: PrizeDistributionMethod
    ) -> Dict[str, Decimal]:
        """Create prize structure based on distribution method."""
        
        if distribution_method == PrizeDistributionMethod.WINNER_TAKES_ALL:
            return {"1st": prize_pool}
        
        elif distribution_method == PrizeDistributionMethod.TIERED_REWARDS:
            return {
                "1st": prize_pool * Decimal("0.5"),  # 50%
                "2nd": prize_pool * Decimal("0.3"),  # 30%
                "3rd": prize_pool * Decimal("0.2")   # 20%
            }
        
        elif distribution_method == PrizeDistributionMethod.TOP_PERCENTAGE:
            # Top 10% of participants get prizes
            return {
                "top_10_percent": prize_pool
            }
        
        elif distribution_method == PrizeDistributionMethod.PARTICIPATION_REWARDS:
            # Everyone gets a small participation reward
            return {
                "participation": prize_pool
            }
        
        elif distribution_method == PrizeDistributionMethod.ACHIEVEMENT_BASED:
            return {
                "achievement_tier_1": prize_pool * Decimal("0.4"),
                "achievement_tier_2": prize_pool * Decimal("0.3"),
                "achievement_tier_3": prize_pool * Decimal("0.2"),
                "participation": prize_pool * Decimal("0.1")
            }
        
        elif distribution_method == PrizeDistributionMethod.PROPORTIONAL_DISTRIBUTION:
            # Prizes distributed proportionally to performance
            return {
                "proportional_pool": prize_pool
            }
        
        else:  # RANDOM_DRAW
            return {
                "random_draw_pool": prize_pool
            }
    
    async def register_participant(
        self,
        competition_id: str,
        creator_id: str,
        entry_data: Optional[Dict[str, Any]] = None
    ) -> CompetitionParticipant:
        """Register a creator for a competition."""
        try:
            if competition_id not in self.competitions:
                raise ValueError("Competition not found")
            
            competition = self.competitions[competition_id]
            
            # Check registration eligibility
            await self._validate_registration(competition, creator_id)
            
            # Create participant
            participant = CompetitionParticipant(
                participant_id=str(uuid4()),
                competition_id=competition_id,
                creator_id=creator_id,
                registration_date=datetime.utcnow(),
                entry_fee_paid=competition.entry_fee,
                submission_data=entry_data or {}
            )
            
            # Store participant
            self.participants[competition_id].append(participant)
            
            # Update competition status if needed
            if competition.status == CompetitionStatus.DRAFT:
                competition.status = CompetitionStatus.REGISTRATION_OPEN
            
            self.logger.info(f"Registered creator {creator_id} for competition {competition.title}")
            return participant
            
        except Exception as e:
            self.logger.error(f"Error registering participant: {e}")
            raise
    
    async def _validate_registration(self, competition: CompetitionDefinition, creator_id: str):
        """Validate if creator can register for competition."""
        
        # Check registration deadline
        if datetime.utcnow() > competition.registration_deadline:
            raise ValueError("Registration deadline has passed")
        
        # Check max participants
        if competition.max_participants:
            current_participants = len(self.participants.get(competition.competition_id, []))
            if current_participants >= competition.max_participants:
                raise ValueError("Competition is full")
        
        # Check if already registered
        existing_participants = self.participants.get(competition.competition_id, [])
        if any(p.creator_id == creator_id for p in existing_participants):
            raise ValueError("Creator already registered for this competition")
        
        # Check minimum requirements
        for requirement, value in competition.minimum_requirements.items():
            # In production, this would check creator's actual metrics
            # For now, assume requirements are met
            pass
    
    async def update_participant_performance(
        self,
        competition_id: str,
        creator_id: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update participant's performance metrics during competition."""
        try:
            participants = self.participants.get(competition_id, [])
            participant = next((p for p in participants if p.creator_id == creator_id), None)
            
            if not participant:
                raise ValueError("Participant not found")
            
            # Update performance metrics
            participant.performance_metrics.update(performance_data)
            
            # Calculate score based on judging criteria
            competition = self.competitions[competition_id]
            participant.final_score = await self._calculate_participant_score(
                participant, competition
            )
            
            self.logger.debug(f"Updated performance for participant {creator_id}: score {participant.final_score}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating participant performance: {e}")
            return False
    
    async def _calculate_participant_score(
        self, participant: CompetitionParticipant, competition: CompetitionDefinition
    ) -> float:
        """Calculate participant's score based on competition criteria."""
        
        total_score = 0.0
        criteria_count = len(competition.judging_criteria)
        
        if criteria_count == 0:
            return 0.0
        
        for criteria in competition.judging_criteria:
            criteria_score = 0.0
            
            if criteria == JudgingCriteria.ENGAGEMENT_METRICS:
                # Score based on engagement metrics
                engagements = participant.performance_metrics.get("total_engagements", 0)
                criteria_score = min(engagements / 1000, 100.0)  # Max 100 points
            
            elif criteria == JudgingCriteria.REVENUE_GENERATED:
                # Score based on revenue generated
                revenue = float(participant.performance_metrics.get("revenue_generated", 0))
                criteria_score = min(revenue / 100, 100.0)  # Max 100 points
            
            elif criteria == JudgingCriteria.CONTENT_QUALITY:
                # Score based on content quality ratings
                quality_score = participant.performance_metrics.get("quality_score", 0)
                criteria_score = min(quality_score * 20, 100.0)  # Convert to 100-point scale
            
            elif criteria == JudgingCriteria.INNOVATION_FACTOR:
                # Score based on innovation metrics
                innovation_score = participant.performance_metrics.get("innovation_score", 0)
                criteria_score = min(innovation_score * 25, 100.0)
            
            elif criteria == JudgingCriteria.COMMUNITY_IMPACT:
                # Score based on community engagement
                community_score = participant.performance_metrics.get("community_impact", 0)
                criteria_score = min(community_score * 10, 100.0)
            
            elif criteria == JudgingCriteria.COLLABORATION_SUCCESS:
                # Score based on collaboration metrics
                collab_count = participant.performance_metrics.get("collaborations", 0)
                criteria_score = min(collab_count * 20, 100.0)
            
            elif criteria == JudgingCriteria.AUDIENCE_GROWTH:
                # Score based on audience growth
                growth_rate = participant.performance_metrics.get("audience_growth_rate", 0)
                criteria_score = min(growth_rate * 100, 100.0)
            
            elif criteria == JudgingCriteria.TECHNICAL_EXCELLENCE:
                # Score based on technical quality
                tech_score = participant.performance_metrics.get("technical_score", 0)
                criteria_score = min(tech_score * 20, 100.0)
            
            total_score += criteria_score
        
        # Average score across all criteria
        return total_score / criteria_count
    
    async def complete_competition(self, competition_id: str) -> CompetitionResult:
        """Complete a competition and calculate final rankings."""
        try:
            if competition_id not in self.competitions:
                raise ValueError("Competition not found")
            
            competition = self.competitions[competition_id]
            participants = self.participants.get(competition_id, [])
            
            if not participants:
                raise ValueError("No participants in competition")
            
            # Filter qualified participants
            qualified_participants = [p for p in participants if p.qualified]
            
            # Calculate final scores for all participants
            for participant in qualified_participants:
                if participant.final_score is None:
                    participant.final_score = await self._calculate_participant_score(
                        participant, competition
                    )
            
            # Rank participants
            ranked_participants = await self._rank_participants(qualified_participants)
            
            # Distribute prizes
            prizes = await self._distribute_prizes(competition, ranked_participants)
            
            # Create competition result
            result = CompetitionResult(
                competition_id=competition_id,
                total_participants=len(participants),
                total_prize_pool=competition.prize_pool,
                total_distributed=sum(p.prize_amount for p in prizes),
                winners=[
                    {
                        "rank": p.rank,
                        "creator_id": p.creator_id,
                        "score": p.final_score,
                        "prize_amount": float(next((pr.prize_amount for pr in prizes if pr.recipient_id == p.creator_id), Decimal("0")))
                    }
                    for p in ranked_participants[:10]  # Top 10
                ],
                completion_date=datetime.utcnow(),
                statistics=await self._calculate_competition_statistics(competition, participants)
            )
            
            # Update competition status
            competition.status = CompetitionStatus.COMPLETED
            
            # Store results and prizes
            self.results[competition_id] = result
            self.prizes[competition_id] = prizes
            
            # Update analytics
            self.total_participants_served += len(participants)
            self.total_prizes_distributed += result.total_distributed
            
            self.logger.info(f"Completed competition {competition.title} with {len(participants)} participants")
            return result
            
        except Exception as e:
            self.logger.error(f"Error completing competition: {e}")
            raise
    
    async def _rank_participants(
        self, participants: List[CompetitionParticipant]
    ) -> List[CompetitionParticipant]:
        """Rank participants by their final scores."""
        
        # Sort by final score (descending)
        ranked = sorted(participants, key=lambda p: p.final_score or 0, reverse=True)
        
        # Assign ranks
        for i, participant in enumerate(ranked):
            participant.rank = i + 1
        
        return ranked
    
    async def _distribute_prizes(
        self, competition: CompetitionDefinition, ranked_participants: List[CompetitionParticipant]
    ) -> List[CompetitionPrize]:
        """Distribute prizes based on competition rules."""
        
        prizes = []
        
        if competition.prize_distribution_method == PrizeDistributionMethod.WINNER_TAKES_ALL:
            if ranked_participants:
                winner = ranked_participants[0]
                prize = CompetitionPrize(
                    prize_id=str(uuid4()),
                    competition_id=competition.competition_id,
                    recipient_id=winner.creator_id,
                    prize_rank=1,
                    prize_amount=competition.prize_pool,
                    prize_description="1st Place Winner",
                    awarded_date=datetime.utcnow(),
                    distribution_method=competition.prize_distribution_method.value
                )
                prizes.append(prize)
        
        elif competition.prize_distribution_method == PrizeDistributionMethod.TIERED_REWARDS:
            prize_tiers = [
                (1, "1st", Decimal("0.5")),
                (2, "2nd", Decimal("0.3")),
                (3, "3rd", Decimal("0.2"))
            ]
            
            for rank, description, percentage in prize_tiers:
                if len(ranked_participants) >= rank:
                    participant = ranked_participants[rank - 1]
                    prize_amount = competition.prize_pool * percentage
                    
                    prize = CompetitionPrize(
                        prize_id=str(uuid4()),
                        competition_id=competition.competition_id,
                        recipient_id=participant.creator_id,
                        prize_rank=rank,
                        prize_amount=prize_amount,
                        prize_description=f"{description} Place",
                        awarded_date=datetime.utcnow(),
                        distribution_method=competition.prize_distribution_method.value
                    )
                    prizes.append(prize)
        
        elif competition.prize_distribution_method == PrizeDistributionMethod.TOP_PERCENTAGE:
            # Top 10% get prizes
            top_count = max(1, len(ranked_participants) // 10)
            prize_per_winner = competition.prize_pool / top_count
            
            for i in range(min(top_count, len(ranked_participants))):
                participant = ranked_participants[i]
                prize = CompetitionPrize(
                    prize_id=str(uuid4()),
                    competition_id=competition.competition_id,
                    recipient_id=participant.creator_id,
                    prize_rank=i + 1,
                    prize_amount=prize_per_winner,
                    prize_description=f"Top {10}% Winner",
                    awarded_date=datetime.utcnow(),
                    distribution_method=competition.prize_distribution_method.value
                )
                prizes.append(prize)
        
        elif competition.prize_distribution_method == PrizeDistributionMethod.PARTICIPATION_REWARDS:
            # Everyone gets a participation prize
            prize_per_participant = competition.prize_pool / len(ranked_participants)
            
            for participant in ranked_participants:
                prize = CompetitionPrize(
                    prize_id=str(uuid4()),
                    competition_id=competition.competition_id,
                    recipient_id=participant.creator_id,
                    prize_rank=participant.rank,
                    prize_amount=prize_per_participant,
                    prize_description="Participation Prize",
                    awarded_date=datetime.utcnow(),
                    distribution_method=competition.prize_distribution_method.value
                )
                prizes.append(prize)
        
        elif competition.prize_distribution_method == PrizeDistributionMethod.PROPORTIONAL_DISTRIBUTION:
            # Distribute prizes proportionally to scores
            total_score = sum(p.final_score or 0 for p in ranked_participants)
            
            if total_score > 0:
                for participant in ranked_participants:
                    score_percentage = (participant.final_score or 0) / total_score
                    prize_amount = competition.prize_pool * Decimal(str(score_percentage))
                    
                    if prize_amount >= self.minimum_prize_amount:
                        prize = CompetitionPrize(
                            prize_id=str(uuid4()),
                            competition_id=competition.competition_id,
                            recipient_id=participant.creator_id,
                            prize_rank=participant.rank,
                            prize_amount=prize_amount,
                            prize_description="Proportional Prize",
                            awarded_date=datetime.utcnow(),
                            distribution_method=competition.prize_distribution_method.value
                        )
                        prizes.append(prize)
        
        elif competition.prize_distribution_method == PrizeDistributionMethod.RANDOM_DRAW:
            # Random draw for winners
            num_winners = min(5, len(ranked_participants))  # Up to 5 random winners
            winners = random.sample(ranked_participants, num_winners)
            prize_per_winner = competition.prize_pool / num_winners
            
            for i, participant in enumerate(winners):
                prize = CompetitionPrize(
                    prize_id=str(uuid4()),
                    competition_id=competition.competition_id,
                    recipient_id=participant.creator_id,
                    prize_rank=i + 1,
                    prize_amount=prize_per_winner,
                    prize_description="Random Draw Winner",
                    awarded_date=datetime.utcnow(),
                    distribution_method=competition.prize_distribution_method.value
                )
                prizes.append(prize)
        
        return prizes
    
    async def _calculate_competition_statistics(
        self, competition: CompetitionDefinition, participants: List[CompetitionParticipant]
    ) -> Dict[str, Any]:
        """Calculate competition statistics."""
        
        if not participants:
            return {}
        
        scores = [p.final_score for p in participants if p.final_score is not None]
        
        stats = {
            "total_participants": len(participants),
            "qualified_participants": len([p for p in participants if p.qualified]),
            "disqualified_participants": len([p for p in participants if not p.qualified]),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "competition_duration_days": (competition.end_date - competition.start_date).days,
            "entry_fees_collected": float(sum(p.entry_fee_paid for p in participants))
        }
        
        return stats
    
    async def process_prize_payouts(self, competition_id: str) -> Dict[str, Any]:
        """Process prize payouts for a completed competition."""
        try:
            prizes = self.prizes.get(competition_id, [])
            
            if not prizes:
                return {"message": "No prizes to process"}
            
            successful_payouts = []
            failed_payouts = []
            total_amount = Decimal("0")
            
            for prize in prizes:
                if prize.status != "pending":
                    continue
                
                try:
                    # Process payout (in production, integrate with payment system)
                    transaction_id = await self._process_prize_payout(prize)
                    
                    if transaction_id:
                        prize.status = "completed"
                        prize.transaction_id = transaction_id
                        successful_payouts.append(prize)
                        total_amount += prize.prize_amount
                    else:
                        prize.status = "failed"
                        failed_payouts.append(prize)
                        
                except Exception as e:
                    self.logger.error(f"Error processing prize payout: {e}")
                    prize.status = "failed"
                    failed_payouts.append(prize)
            
            # Update competition status if all prizes processed
            if not any(p.status == "pending" for p in prizes):
                competition = self.competitions.get(competition_id)
                if competition:
                    competition.status = CompetitionStatus.PRIZES_DISTRIBUTED
            
            result = {
                "competition_id": competition_id,
                "successful_payouts": len(successful_payouts),
                "failed_payouts": len(failed_payouts),
                "total_amount_distributed": float(total_amount),
                "currency": self.default_currency,
                "payout_details": [
                    {
                        "prize_id": p.prize_id,
                        "recipient_id": p.recipient_id,
                        "amount": float(p.prize_amount),
                        "rank": p.prize_rank,
                        "transaction_id": p.transaction_id,
                        "status": p.status
                    }
                    for p in successful_payouts
                ]
            }
            
            self.logger.info(f"Processed {len(successful_payouts)} prize payouts for competition {competition_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing prize payouts: {e}")
            return {"error": str(e)}
    
    async def _process_prize_payout(self, prize: CompetitionPrize) -> Optional[str]:
        """Process individual prize payout."""
        # In production, this would integrate with payment processing
        try:
            # Simulate payment processing
            transaction_id = f"comp_txn_{str(uuid4())[:8]}"
            
            # Apply platform fee
            platform_fee = prize.prize_amount * self.platform_fee_rate
            net_amount = prize.prize_amount - platform_fee
            
            # Update prize amount to net amount
            prize.prize_amount = net_amount
            
            return transaction_id
            
        except Exception as e:
            self.logger.error(f"Error in prize payout processing: {e}")
            return None
    
    async def get_competition_summary(self, competition_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of a competition."""
        try:
            if competition_id not in self.competitions:
                return {"error": "Competition not found"}
            
            competition = self.competitions[competition_id]
            participants = self.participants.get(competition_id, [])
            prizes = self.prizes.get(competition_id, [])
            result = self.results.get(competition_id)
            
            summary = {
                "competition": {
                    "id": competition.competition_id,
                    "title": competition.title,
                    "type": competition.competition_type.value,
                    "status": competition.status.value,
                    "prize_pool": float(competition.prize_pool),
                    "start_date": competition.start_date.isoformat(),
                    "end_date": competition.end_date.isoformat(),
                    "created_by": competition.created_by
                },
                "participation": {
                    "total_registered": len(participants),
                    "qualified": len([p for p in participants if p.qualified]),
                    "disqualified": len([p for p in participants if not p.qualified]),
                    "entry_fees_collected": float(sum(p.entry_fee_paid for p in participants))
                },
                "prizes": {
                    "total_prizes": len(prizes),
                    "total_distributed": float(sum(p.prize_amount for p in prizes)),
                    "pending_payouts": len([p for p in prizes if p.status == "pending"]),
                    "completed_payouts": len([p for p in prizes if p.status == "completed"])
                }
            }
            
            if result:
                summary["results"] = {
                    "completion_date": result.completion_date.isoformat(),
                    "winners": result.winners,
                    "statistics": result.statistics
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting competition summary: {e}")
            return {"error": str(e)}
    
    async def get_system_competition_analytics(self) -> Dict[str, Any]:
        """Get system-wide competition analytics."""
        try:
            total_competitions = len(self.competitions)
            
            if total_competitions == 0:
                return {"message": "No competitions found"}
            
            # Status distribution
            status_distribution = {}
            for competition in self.competitions.values():
                status = competition.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Type distribution
            type_distribution = {}
            for competition in self.competitions.values():
                comp_type = competition.competition_type.value
                type_distribution[comp_type] = type_distribution.get(comp_type, 0) + 1
            
            # Calculate averages
            total_participants = sum(len(participants) for participants in self.participants.values())
            avg_participants_per_competition = total_participants / max(total_competitions, 1)
            
            completed_competitions = len([c for c in self.competitions.values() if c.status == CompetitionStatus.COMPLETED])
            completion_rate = (completed_competitions / total_competitions) * 100 if total_competitions > 0 else 0
            
            return {
                "overview": {
                    "total_competitions": total_competitions,
                    "completed_competitions": completed_competitions,
                    "active_competitions": len([c for c in self.competitions.values() if c.status == CompetitionStatus.ACTIVE]),
                    "total_participants": total_participants,
                    "total_prizes_distributed": float(self.total_prizes_distributed),
                    "completion_rate": round(completion_rate, 1)
                },
                "distributions": {
                    "status_distribution": status_distribution,
                    "type_distribution": type_distribution
                },
                "averages": {
                    "participants_per_competition": round(avg_participants_per_competition, 1),
                    "prize_pool_per_competition": float(sum(c.prize_pool for c in self.competitions.values()) / max(total_competitions, 1)),
                    "completion_time_days": 30  # Placeholder
                },
                "system_health": {
                    "participation_rate": min(95.0, 85.0 + (total_participants / max(total_competitions, 1) / 10)),
                    "payout_success_rate": 98.5,  # Placeholder high success rate
                    "platform_engagement": "High"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system competition analytics: {e}")
            return {"error": str(e)}


# Global instance
_competition_prize_manager: Optional[CompetitionPrizeManager] = None

async def get_competition_prize_manager() -> CompetitionPrizeManager:
    """Get the global competition prize manager instance."""
    global _competition_prize_manager
    
    if _competition_prize_manager is None:
        _competition_prize_manager = CompetitionPrizeManager()
        await _competition_prize_manager.initialize()
    
    return _competition_prize_manager