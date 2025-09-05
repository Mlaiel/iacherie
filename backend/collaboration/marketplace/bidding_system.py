"""Bidding System - Real-Time Bidding Engine for Creator Collaborations
=====================================================================

Advanced bidding system providing:
- Real-time bid processing
- Multiple bidding strategies
- Automatic bid optimization
- Anti-fraud protection
- Bid analytics and insights
- Multi-tier bidding support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid

logger = logging.getLogger(__name__)


class BidType(Enum):
    """Types of bids"""
    FIXED_PRICE = "fixed_price"
    HOURLY_RATE = "hourly_rate"
    PROJECT_BASED = "project_based"
    REVENUE_SHARE = "revenue_share"
    MILESTONE_BASED = "milestone_based"
    SUBSCRIPTION = "subscription"


class BidStatus(Enum):
    """Status of bids"""
    PENDING = "pending"
    ACTIVE = "active"
    WINNING = "winning"
    LOST = "lost"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class BiddingStrategy(Enum):
    """Bidding strategies"""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"
    VALUE_BASED = "value_based"
    COMPETITIVE = "competitive"
    PREMIUM = "premium"


@dataclass
class Bid:
    """Comprehensive bid representation"""
    bid_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    auction_id: str = ""
    bidder_id: str = ""
    service_id: str = ""
    bid_type: BidType = BidType.FIXED_PRICE
    amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    status: BidStatus = BidStatus.PENDING
    strategy: BiddingStrategy = BiddingStrategy.COMPETITIVE
    
    # Bid details
    description: str = ""
    delivery_time: int = 0  # days
    revision_count: int = 0
    additional_services: List[str] = field(default_factory=list)
    terms_and_conditions: str = ""
    
    # Proposal details
    portfolio_items: List[str] = field(default_factory=list)
    experience_years: int = 0
    similar_projects: int = 0
    success_rate: float = 0.0
    client_testimonials: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Analytics
    view_count: int = 0
    favorited_count: int = 0
    response_rate: float = 0.0
    
    # Auto-bidding configuration
    auto_bid_enabled: bool = False
    max_auto_bid: Optional[Decimal] = None
    bid_increment: Optional[Decimal] = None
    
    # Quality metrics
    quality_score: float = 0.0
    value_score: float = 0.0
    competitiveness_score: float = 0.0
    
    def calculate_total_cost(self) -> Decimal:
        """Calculate total cost including additional services"""
        total = self.amount
        
        # Add costs for additional services (simplified)
        additional_cost = Decimal(str(len(self.additional_services) * 100))
        total += additional_cost
        
        return total
    
    def get_hourly_rate(self, estimated_hours: int = None) -> Decimal:
        """Calculate equivalent hourly rate"""
        if self.bid_type == BidType.HOURLY_RATE:
            return self.amount
        
        if not estimated_hours:
            estimated_hours = max(self.delivery_time * 8, 40)  # 8 hours per day, min 40 hours
        
        return self.amount / Decimal(str(estimated_hours))
    
    def is_expired(self) -> bool:
        """Check if bid has expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def get_competitiveness_rating(self) -> str:
        """Get human-readable competitiveness rating"""
        if self.competitiveness_score >= 0.8:
            return "highly_competitive"
        elif self.competitiveness_score >= 0.6:
            return "competitive"
        elif self.competitiveness_score >= 0.4:
            return "moderate"
        elif self.competitiveness_score >= 0.2:
            return "weak"
        else:
            return "non_competitive"


@dataclass
class BidAnalysis:
    """Bid analysis and recommendations"""
    bid_id: str
    market_position: str  # high, medium, low
    win_probability: float
    recommended_adjustments: List[str] = field(default_factory=list)
    competitive_analysis: Dict[str, Any] = field(default_factory=dict)
    value_proposition: str = ""
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)


class BiddingSystem:
    """
    Advanced real-time bidding system for creator marketplace
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize bidding system"""
        self.config = config or {}
        self.active_bids: Dict[str, Bid] = {}
        self.bid_history: List[Bid] = []
        self.bidding_analytics = {}
        
        # Configuration
        self.max_bids_per_auction = self.config.get('max_bids_per_auction', 100)
        self.bid_increment_percentage = self.config.get('bid_increment_percentage', 0.05)  # 5%
        self.auto_bid_enabled = self.config.get('auto_bid_enabled', True)
        self.fraud_detection_enabled = self.config.get('fraud_detection', True)
        
        # Bidding rules
        self.min_bid_amount = Decimal(str(self.config.get('min_bid_amount', 50)))
        self.max_bid_amount = Decimal(str(self.config.get('max_bid_amount', 100000)))
        self.bid_expiry_hours = self.config.get('bid_expiry_hours', 24)
        
        # Real-time tracking
        self.bid_watchers: Dict[str, List] = {}  # auction_id -> list of websocket connections
        self.bid_notifications = []
        
        logger.info("💰 Bidding System initialized")
    
    async def submit_bid(
        self,
        auction_id: str,
        bidder_profile: Dict[str, Any],
        bid_data: Dict[str, Any]
    ) -> Bid:
        """Submit a new bid to an auction"""
        try:
            # Validate bid data
            validation_result = await self._validate_bid(auction_id, bidder_profile, bid_data)
            if not validation_result['valid']:
                raise ValueError(f"Invalid bid: {validation_result['errors']}")
            
            # Create bid object
            bid = Bid(
                auction_id=auction_id,
                bidder_id=bidder_profile['creator_id'],
                service_id=bid_data.get('service_id', ''),
                bid_type=BidType(bid_data.get('bid_type', 'fixed_price')),
                amount=Decimal(str(bid_data['amount'])),
                currency=bid_data.get('currency', 'USD'),
                status=BidStatus.ACTIVE,
                strategy=BiddingStrategy(bid_data.get('strategy', 'competitive')),
                description=bid_data.get('description', ''),
                delivery_time=bid_data.get('delivery_time', 7),
                revision_count=bid_data.get('revisions', 2),
                additional_services=bid_data.get('additional_services', []),
                terms_and_conditions=bid_data.get('terms', ''),
                portfolio_items=bid_data.get('portfolio_items', []),
                experience_years=bidder_profile.get('experience_years', 0),
                similar_projects=bidder_profile.get('similar_projects', 0),
                success_rate=bidder_profile.get('success_rate', 0.0),
                expires_at=datetime.now() + timedelta(hours=self.bid_expiry_hours)
            )
            
            # Calculate quality scores
            bid.quality_score = await self._calculate_quality_score(bid, bidder_profile)
            bid.value_score = await self._calculate_value_score(bid, auction_id)
            bid.competitiveness_score = await self._calculate_competitiveness_score(bid, auction_id)
            
            # Store bid
            self.active_bids[bid.bid_id] = bid
            
            # Update auction analytics
            await self._update_auction_analytics(auction_id, bid)
            
            # Trigger real-time notifications
            await self._notify_bid_watchers(auction_id, bid)
            
            # Check for auto-bidding responses
            await self._process_auto_bids(auction_id, bid)
            
            logger.info(f"✅ Bid {bid.bid_id} submitted successfully for auction {auction_id}")
            
            return bid
            
        except Exception as e:
            logger.error(f"❌ Error submitting bid: {e}")
            raise
    
    async def _validate_bid(
        self,
        auction_id: str,
        bidder_profile: Dict[str, Any],
        bid_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate bid data and bidder eligibility"""
        errors = []
        
        # Amount validation
        try:
            amount = Decimal(str(bid_data['amount']))
            if amount < self.min_bid_amount:
                errors.append(f"Bid amount below minimum: {self.min_bid_amount}")
            if amount > self.max_bid_amount:
                errors.append(f"Bid amount above maximum: {self.max_bid_amount}")
        except (KeyError, ValueError):
            errors.append("Invalid or missing bid amount")
        
        # Bidder validation
        creator_id = bidder_profile.get('creator_id')
        if not creator_id:
            errors.append("Invalid bidder profile")
        
        # Check for existing bids from same bidder
        existing_bids = [
            bid for bid in self.active_bids.values()
            if bid.auction_id == auction_id and bid.bidder_id == creator_id
        ]
        if existing_bids:
            errors.append("Bidder already has active bid for this auction")
        
        # Fraud detection
        if self.fraud_detection_enabled:
            fraud_score = await self._calculate_fraud_score(bidder_profile, bid_data)
            if fraud_score > 0.8:
                errors.append("Bid flagged by fraud detection system")
        
        # Delivery time validation
        delivery_time = bid_data.get('delivery_time', 0)
        if delivery_time <= 0:
            errors.append("Invalid delivery time")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _calculate_quality_score(self, bid: Bid, bidder_profile: Dict[str, Any]) -> float:
        """Calculate bid quality score"""
        factors = []
        
        # Bidder reputation
        reputation = bidder_profile.get('reputation_score', 0.5)
        factors.append(reputation * 0.3)
        
        # Success rate
        success_rate = bidder_profile.get('success_rate', 0.5)
        factors.append(success_rate * 0.2)
        
        # Experience
        experience_years = bidder_profile.get('experience_years', 0)
        experience_score = min(experience_years / 10.0, 1.0)  # Max 10 years
        factors.append(experience_score * 0.2)
        
        # Portfolio quality
        portfolio_count = len(bid.portfolio_items)
        portfolio_score = min(portfolio_count / 10.0, 1.0)  # Max 10 items
        factors.append(portfolio_score * 0.15)
        
        # Proposal completeness
        completeness = 0.0
        if bid.description:
            completeness += 0.25
        if bid.terms_and_conditions:
            completeness += 0.25
        if bid.additional_services:
            completeness += 0.25
        if bid.delivery_time > 0:
            completeness += 0.25
        factors.append(completeness * 0.15)
        
        return sum(factors)
    
    async def _calculate_value_score(self, bid: Bid, auction_id: str) -> float:
        """Calculate bid value score"""
        # Get other bids for comparison
        competing_bids = [
            b for b in self.active_bids.values()
            if b.auction_id == auction_id and b.bid_id != bid.bid_id
        ]
        
        if not competing_bids:
            return 0.5  # No comparison available
        
        # Calculate value metrics
        factors = []
        
        # Price competitiveness
        amounts = [float(b.amount) for b in competing_bids]
        if amounts:
            avg_amount = np.mean(amounts)
            price_ratio = float(bid.amount) / avg_amount if avg_amount > 0 else 1.0
            # Lower price = higher value (inverted score)
            price_score = max(0.0, 2.0 - price_ratio) / 2.0
            factors.append(price_score * 0.4)
        
        # Delivery time competitiveness
        delivery_times = [b.delivery_time for b in competing_bids]
        if delivery_times:
            avg_delivery = np.mean(delivery_times)
            delivery_ratio = bid.delivery_time / avg_delivery if avg_delivery > 0 else 1.0
            # Faster delivery = higher value (inverted score)
            delivery_score = max(0.0, 2.0 - delivery_ratio) / 2.0
            factors.append(delivery_score * 0.3)
        
        # Additional services value
        services_score = min(len(bid.additional_services) / 5.0, 1.0)  # Max 5 services
        factors.append(services_score * 0.2)
        
        # Revision count value
        revision_score = min(bid.revision_count / 5.0, 1.0)  # Max 5 revisions
        factors.append(revision_score * 0.1)
        
        return sum(factors) if factors else 0.5
    
    async def _calculate_competitiveness_score(self, bid: Bid, auction_id: str) -> float:
        """Calculate how competitive the bid is"""
        competing_bids = [
            b for b in self.active_bids.values()
            if b.auction_id == auction_id and b.bid_id != bid.bid_id
        ]
        
        if not competing_bids:
            return 0.5
        
        # Rank by amount (lower is better for buyers)
        all_amounts = [float(b.amount) for b in competing_bids] + [float(bid.amount)]
        all_amounts.sort()
        
        bid_rank = all_amounts.index(float(bid.amount)) + 1
        total_bids = len(all_amounts)
        
        # Convert rank to score (1st place = 1.0, last place = 0.0)
        rank_score = (total_bids - bid_rank) / (total_bids - 1) if total_bids > 1 else 0.5
        
        return rank_score
    
    async def _calculate_fraud_score(
        self,
        bidder_profile: Dict[str, Any],
        bid_data: Dict[str, Any]
    ) -> float:
        """Calculate fraud probability score"""
        risk_factors = []
        
        # New account risk
        account_age_days = bidder_profile.get('account_age_days', 0)
        if account_age_days < 30:
            risk_factors.append(0.3)
        
        # Unusual pricing
        amount = float(bid_data.get('amount', 0))
        if amount < 10 or amount > 50000:  # Suspicious amounts
            risk_factors.append(0.4)
        
        # Poor reputation
        reputation = bidder_profile.get('reputation_score', 1.0)
        if reputation < 0.3:
            risk_factors.append(0.5)
        
        # Incomplete profile
        profile_completeness = bidder_profile.get('profile_completeness', 1.0)
        if profile_completeness < 0.5:
            risk_factors.append(0.2)
        
        # Suspicious delivery time
        delivery_time = bid_data.get('delivery_time', 7)
        if delivery_time < 1 or delivery_time > 365:
            risk_factors.append(0.3)
        
        return min(sum(risk_factors), 1.0)
    
    async def _update_auction_analytics(self, auction_id: str, bid: Bid):
        """Update auction analytics with new bid"""
        if auction_id not in self.bidding_analytics:
            self.bidding_analytics[auction_id] = {
                'total_bids': 0,
                'average_amount': 0.0,
                'min_amount': float('inf'),
                'max_amount': 0.0,
                'bid_history': [],
                'participation_rate': 0.0
            }
        
        analytics = self.bidding_analytics[auction_id]
        analytics['total_bids'] += 1
        analytics['bid_history'].append({
            'bid_id': bid.bid_id,
            'amount': float(bid.amount),
            'timestamp': bid.created_at.isoformat(),
            'bidder_id': bid.bidder_id
        })
        
        # Update amount statistics
        all_amounts = [float(b.amount) for b in self.active_bids.values() if b.auction_id == auction_id]
        if all_amounts:
            analytics['average_amount'] = np.mean(all_amounts)
            analytics['min_amount'] = min(all_amounts)
            analytics['max_amount'] = max(all_amounts)
    
    async def _notify_bid_watchers(self, auction_id: str, bid: Bid):
        """Notify real-time watchers of new bid"""
        if auction_id in self.bid_watchers:
            notification = {
                'type': 'new_bid',
                'auction_id': auction_id,
                'bid_id': bid.bid_id,
                'amount': float(bid.amount),
                'bidder_id': bid.bidder_id,
                'timestamp': bid.created_at.isoformat()
            }
            
            # In a real implementation, this would send WebSocket notifications
            self.bid_notifications.append(notification)
            logger.info(f"📢 Notified {len(self.bid_watchers[auction_id])} watchers of new bid")
    
    async def _process_auto_bids(self, auction_id: str, new_bid: Bid):
        """Process automatic bidding responses"""
        if not self.auto_bid_enabled:
            return
        
        # Find bidders with auto-bidding enabled
        auto_bidders = [
            bid for bid in self.active_bids.values()
            if (bid.auction_id == auction_id and 
                bid.auto_bid_enabled and 
                bid.bidder_id != new_bid.bidder_id)
        ]
        
        for auto_bid in auto_bidders:
            try:
                # Check if auto-bid should respond
                if await self._should_auto_respond(auto_bid, new_bid):
                    new_amount = await self._calculate_auto_bid_amount(auto_bid, new_bid)
                    
                    if new_amount and new_amount <= auto_bid.max_auto_bid:
                        # Update existing bid
                        auto_bid.amount = new_amount
                        auto_bid.updated_at = datetime.now()
                        auto_bid.status = BidStatus.ACTIVE
                        
                        # Recalculate scores
                        auto_bid.competitiveness_score = await self._calculate_competitiveness_score(
                            auto_bid, auction_id
                        )
                        
                        logger.info(f"🤖 Auto-bid updated: {auto_bid.bid_id} to {new_amount}")
                        
                        # Notify watchers of auto-bid update
                        await self._notify_bid_watchers(auction_id, auto_bid)
                        
            except Exception as e:
                logger.warning(f"⚠️ Error processing auto-bid for {auto_bid.bid_id}: {e}")
    
    async def _should_auto_respond(self, auto_bid: Bid, new_bid: Bid) -> bool:
        """Determine if auto-bidder should respond to new bid"""
        # Don't respond to own bids
        if auto_bid.bidder_id == new_bid.bidder_id:
            return False
        
        # Only respond if new bid is lower
        if new_bid.amount >= auto_bid.amount:
            return False
        
        # Check if within auto-bid budget
        increment = auto_bid.bid_increment or (auto_bid.amount * Decimal('0.05'))
        potential_new_amount = new_bid.amount - increment
        
        if potential_new_amount > auto_bid.max_auto_bid:
            return False
        
        return True
    
    async def _calculate_auto_bid_amount(self, auto_bid: Bid, competing_bid: Bid) -> Optional[Decimal]:
        """Calculate new auto-bid amount"""
        try:
            increment = auto_bid.bid_increment or (auto_bid.amount * Decimal('0.05'))
            new_amount = competing_bid.amount - increment
            
            # Ensure minimum increment
            min_increment = Decimal('1.00')
            if auto_bid.amount - new_amount < min_increment:
                new_amount = auto_bid.amount - min_increment
            
            # Check constraints
            if new_amount <= self.min_bid_amount:
                return None
            
            if new_amount > auto_bid.max_auto_bid:
                return None
            
            return new_amount
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating auto-bid amount: {e}")
            return None
    
    async def get_auction_bids(
        self,
        auction_id: str,
        sort_by: str = "amount",
        include_inactive: bool = False
    ) -> List[Bid]:
        """Get all bids for an auction"""
        bids = [
            bid for bid in self.active_bids.values()
            if bid.auction_id == auction_id
        ]
        
        if not include_inactive:
            bids = [bid for bid in bids if bid.status == BidStatus.ACTIVE]
        
        # Sort bids
        if sort_by == "amount":
            bids.sort(key=lambda x: x.amount)
        elif sort_by == "quality":
            bids.sort(key=lambda x: x.quality_score, reverse=True)
        elif sort_by == "value":
            bids.sort(key=lambda x: x.value_score, reverse=True)
        elif sort_by == "created_at":
            bids.sort(key=lambda x: x.created_at)
        
        return bids
    
    async def analyze_bid(self, bid_id: str) -> BidAnalysis:
        """Analyze bid performance and provide recommendations"""
        if bid_id not in self.active_bids:
            raise ValueError(f"Bid {bid_id} not found")
        
        bid = self.active_bids[bid_id]
        
        # Get competing bids
        competing_bids = [
            b for b in self.active_bids.values()
            if b.auction_id == bid.auction_id and b.bid_id != bid_id
        ]
        
        # Market position analysis
        if not competing_bids:
            market_position = "only_bidder"
        else:
            amounts = [float(b.amount) for b in competing_bids]
            amounts.sort()
            bid_amount = float(bid.amount)
            
            if bid_amount <= amounts[0]:
                market_position = "leading"
            elif bid_amount <= np.percentile(amounts, 25):
                market_position = "top_quartile"
            elif bid_amount <= np.percentile(amounts, 75):
                market_position = "middle"
            else:
                market_position = "bottom_quartile"
        
        # Win probability calculation
        win_probability = await self._calculate_win_probability(bid, competing_bids)
        
        # Generate recommendations
        recommendations = await self._generate_bid_recommendations(bid, competing_bids)
        
        # Competitive analysis
        competitive_analysis = await self._analyze_competition(bid, competing_bids)
        
        # Risk assessment
        risk_assessment = await self._assess_bid_risks(bid)
        
        return BidAnalysis(
            bid_id=bid_id,
            market_position=market_position,
            win_probability=win_probability,
            recommended_adjustments=recommendations,
            competitive_analysis=competitive_analysis,
            risk_assessment=risk_assessment
        )
    
    async def _calculate_win_probability(self, bid: Bid, competing_bids: List[Bid]) -> float:
        """Calculate probability of winning the auction"""
        if not competing_bids:
            return 0.8  # High chance if only bidder
        
        factors = []
        
        # Price competitiveness (40% weight)
        amounts = [float(b.amount) for b in competing_bids]
        if amounts:
            min_amount = min(amounts)
            max_amount = max(amounts)
            bid_amount = float(bid.amount)
            
            if max_amount > min_amount:
                price_score = (max_amount - bid_amount) / (max_amount - min_amount)
            else:
                price_score = 1.0 if bid_amount <= min_amount else 0.0
            
            factors.append(price_score * 0.4)
        
        # Quality score (30% weight)
        factors.append(bid.quality_score * 0.3)
        
        # Value score (20% weight)
        factors.append(bid.value_score * 0.2)
        
        # Delivery time competitiveness (10% weight)
        delivery_times = [b.delivery_time for b in competing_bids]
        if delivery_times:
            min_delivery = min(delivery_times)
            if bid.delivery_time <= min_delivery:
                delivery_score = 1.0
            else:
                avg_delivery = np.mean(delivery_times)
                delivery_score = max(0.0, (avg_delivery - bid.delivery_time) / avg_delivery)
        else:
            delivery_score = 0.5
        
        factors.append(delivery_score * 0.1)
        
        return min(sum(factors), 1.0)
    
    async def _generate_bid_recommendations(
        self,
        bid: Bid,
        competing_bids: List[Bid]
    ) -> List[str]:
        """Generate bid improvement recommendations"""
        recommendations = []
        
        # Price recommendations
        if competing_bids:
            amounts = [float(b.amount) for b in competing_bids]
            min_amount = min(amounts)
            
            if float(bid.amount) > min_amount * 1.1:  # 10% above minimum
                savings = float(bid.amount) - min_amount
                recommendations.append(f"Consider reducing price by ${savings:.2f} to be more competitive")
        
        # Quality improvements
        if bid.quality_score < 0.7:
            if len(bid.portfolio_items) < 5:
                recommendations.append("Add more portfolio items to improve credibility")
            
            if not bid.description or len(bid.description) < 100:
                recommendations.append("Provide a more detailed project description")
            
            if not bid.terms_and_conditions:
                recommendations.append("Add clear terms and conditions")
        
        # Delivery time optimization
        if competing_bids:
            delivery_times = [b.delivery_time for b in competing_bids]
            min_delivery = min(delivery_times)
            
            if bid.delivery_time > min_delivery * 1.2:  # 20% longer than fastest
                recommendations.append(f"Consider reducing delivery time to {min_delivery} days")
        
        # Value additions
        if len(bid.additional_services) < 2:
            recommendations.append("Offer additional services to increase value proposition")
        
        if bid.revision_count < 2:
            recommendations.append("Offer more revisions to be more attractive to buyers")
        
        return recommendations
    
    async def _analyze_competition(self, bid: Bid, competing_bids: List[Bid]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        if not competing_bids:
            return {"total_competitors": 0, "analysis": "No competition"}
        
        analysis = {
            "total_competitors": len(competing_bids),
            "price_range": {
                "min": float(min(b.amount for b in competing_bids)),
                "max": float(max(b.amount for b in competing_bids)),
                "avg": float(np.mean([float(b.amount) for b in competing_bids]))
            },
            "delivery_range": {
                "min": min(b.delivery_time for b in competing_bids),
                "max": max(b.delivery_time for b in competing_bids),
                "avg": np.mean([b.delivery_time for b in competing_bids])
            },
            "quality_comparison": {
                "avg_quality": np.mean([b.quality_score for b in competing_bids]),
                "bid_rank": len([b for b in competing_bids if b.quality_score > bid.quality_score]) + 1
            }
        }
        
        return analysis
    
    async def _assess_bid_risks(self, bid: Bid) -> Dict[str, float]:
        """Assess various risks associated with the bid"""
        risks = {}
        
        # Price risk (too low might indicate quality issues)
        if float(bid.amount) < 100:
            risks["low_price_risk"] = 0.8
        elif float(bid.amount) < 500:
            risks["low_price_risk"] = 0.4
        else:
            risks["low_price_risk"] = 0.1
        
        # Delivery risk (too fast might be unrealistic)
        if bid.delivery_time < 3:
            risks["delivery_risk"] = 0.7
        elif bid.delivery_time < 7:
            risks["delivery_risk"] = 0.3
        else:
            risks["delivery_risk"] = 0.1
        
        # Quality risk (based on bidder profile)
        if bid.quality_score < 0.5:
            risks["quality_risk"] = 0.8
        elif bid.quality_score < 0.7:
            risks["quality_risk"] = 0.4
        else:
            risks["quality_risk"] = 0.1
        
        # Competition risk (too many competitors)
        competing_bids_count = len([
            b for b in self.active_bids.values()
            if b.auction_id == bid.auction_id and b.bid_id != bid.bid_id
        ])
        
        if competing_bids_count > 20:
            risks["competition_risk"] = 0.9
        elif competing_bids_count > 10:
            risks["competition_risk"] = 0.6
        elif competing_bids_count > 5:
            risks["competition_risk"] = 0.3
        else:
            risks["competition_risk"] = 0.1
        
        return risks
    
    async def get_bidding_analytics(self, auction_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive bidding analytics"""
        if auction_id:
            return self.bidding_analytics.get(auction_id, {})
        
        # Overall analytics
        total_bids = len(self.active_bids)
        total_auctions = len(set(bid.auction_id for bid in self.active_bids.values()))
        
        if total_bids == 0:
            return {"total_bids": 0, "total_auctions": 0}
        
        all_amounts = [float(bid.amount) for bid in self.active_bids.values()]
        
        analytics = {
            "total_bids": total_bids,
            "total_auctions": total_auctions,
            "average_bids_per_auction": total_bids / max(total_auctions, 1),
            "amount_statistics": {
                "min": min(all_amounts),
                "max": max(all_amounts),
                "avg": np.mean(all_amounts),
                "median": np.median(all_amounts)
            },
            "bid_type_distribution": {},
            "strategy_distribution": {},
            "average_quality_score": np.mean([bid.quality_score for bid in self.active_bids.values()]),
            "average_competitiveness": np.mean([bid.competitiveness_score for bid in self.active_bids.values()])
        }
        
        # Distribution analysis
        for bid in self.active_bids.values():
            bid_type = bid.bid_type.value
            strategy = bid.strategy.value
            
            analytics["bid_type_distribution"][bid_type] = analytics["bid_type_distribution"].get(bid_type, 0) + 1
            analytics["strategy_distribution"][strategy] = analytics["strategy_distribution"].get(strategy, 0) + 1
        
        return analytics
    
    async def cleanup_expired_bids(self):
        """Remove expired bids from active tracking"""
        expired_bids = []
        
        for bid_id, bid in self.active_bids.items():
            if bid.is_expired():
                bid.status = BidStatus.EXPIRED
                expired_bids.append(bid_id)
        
        # Move expired bids to history
        for bid_id in expired_bids:
            expired_bid = self.active_bids.pop(bid_id)
            self.bid_history.append(expired_bid)
            
        if expired_bids:
            logger.info(f"🗑️ Cleaned up {len(expired_bids)} expired bids")
        
        return len(expired_bids)
    
    async def withdraw_bid(self, bid_id: str, bidder_id: str) -> bool:
        """Allow bidder to withdraw their bid"""
        if bid_id not in self.active_bids:
            return False
        
        bid = self.active_bids[bid_id]
        
        # Verify ownership
        if bid.bidder_id != bidder_id:
            return False
        
        # Update status
        bid.status = BidStatus.WITHDRAWN
        bid.updated_at = datetime.now()
        
        # Move to history
        self.bid_history.append(self.active_bids.pop(bid_id))
        
        logger.info(f"📤 Bid {bid_id} withdrawn by {bidder_id}")
        
        return True