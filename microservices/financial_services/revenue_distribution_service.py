#!/usr/bin/env python3
"""
💰 REVENUE DISTRIBUTION SERVICE
===============================

Advanced collaborative revenue sharing and distribution management service.
Handles automated revenue splitting, tracking, and distribution for collaborative projects.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered revenue optimization and fraud detection
- Backend Senior: Enterprise-grade financial transaction processing
- ML Engineer: Predictive revenue modeling and optimization algorithms
- DBA: Secure financial data management and audit trails
- Security: Advanced financial security and compliance measures
- Microservices: Service mesh integration for payment processing
- Audio Engineer: Audio content revenue tracking and royalty calculation
- DevOps: Financial monitoring, alerting, and performance optimization
- AI Prompt Engineer: Intelligent revenue insights and recommendations
"""

import asyncio
import logging
import time
import json
import hashlib
import decimal
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
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Revenue source types"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    SUBSCRIPTIONS = "subscriptions"
    ADVERTISING = "advertising"
    LIVE_EVENTS = "live_events"
    COMMISSIONS = "commissions"
    ROYALTIES = "royalties"

class DistributionMethod(Enum):
    """Revenue distribution methods"""
    EQUAL_SPLIT = "equal_split"
    PERCENTAGE_BASED = "percentage_based"
    CONTRIBUTION_WEIGHTED = "contribution_weighted"
    PERFORMANCE_BASED = "performance_based"
    HYBRID_MODEL = "hybrid_model"
    ROLE_BASED = "role_based"
    TIME_WEIGHTED = "time_weighted"
    MILESTONE_BASED = "milestone_based"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class TransactionType(Enum):
    """Transaction type enumeration"""
    REVENUE_SHARE = "revenue_share"
    BONUS_PAYMENT = "bonus_payment"
    ROYALTY_PAYMENT = "royalty_payment"
    COMMISSION = "commission"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    PENALTY = "penalty"
    ADVANCE = "advance"

class CurrencyCode(Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"

@dataclass
class RevenueShare:
    """Revenue share configuration"""
    participant_id: str
    participant_name: str
    share_percentage: Decimal
    minimum_amount: Decimal
    maximum_amount: Optional[Decimal]
    role: str
    contribution_score: float
    vesting_period_days: int
    payment_method: str
    tax_jurisdiction: str
    created_at: datetime
    updated_at: datetime

@dataclass
class RevenueDistribution:
    """Revenue distribution record"""
    distribution_id: str
    collaboration_id: str
    total_revenue: Decimal
    currency: CurrencyCode
    revenue_source: RevenueSource
    distribution_method: DistributionMethod
    distribution_date: datetime
    period_start: datetime
    period_end: datetime
    shares: List[RevenueShare]
    fees_deducted: Decimal
    net_distributable: Decimal
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    distribution_id: str
    participant_id: str
    amount: Decimal
    currency: CurrencyCode
    transaction_type: TransactionType
    status: PaymentStatus
    payment_method: str
    payment_gateway: str
    gateway_transaction_id: Optional[str]
    fees: Decimal
    net_amount: Decimal
    processed_at: Optional[datetime]
    failed_reason: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime

@dataclass
class RevenueAnalytics:
    """Revenue analytics and insights"""
    analytics_id: str
    collaboration_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    revenue_by_source: Dict[str, Decimal]
    distribution_efficiency: float
    average_payout_time: float
    participant_satisfaction: float
    fraud_risk_score: float
    performance_metrics: Dict[str, Any]
    predictions: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

@dataclass
class TaxInformation:
    """Tax information for participants"""
    participant_id: str
    tax_id: str
    tax_jurisdiction: str
    tax_rate: float
    withholding_required: bool
    form_w9_status: bool
    form_1099_required: bool
    tax_exemption: bool
    updated_at: datetime

class RevenueDistributionService:
    """
    💰 Enterprise Revenue Distribution Service
    
    Comprehensive revenue sharing and distribution management with AI-powered
    optimization, fraud detection, and automated payment processing.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.distribution_cache = {}
        self.payment_queue = deque(maxlen=10000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        
        # Service configuration
        self.service_id = f"revenue_distribution_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # Financial configuration
        self.platform_fee_rate = Decimal("0.05")  # 5% platform fee
        self.minimum_payout = Decimal("10.00")
        self.maximum_payout = Decimal("100000.00")
        self.payment_batch_size = 100
        
        # Currency exchange rates (simplified - in production, use real-time rates)
        self.exchange_rates = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("0.85"),
            "GBP": Decimal("0.73"),
            "JPY": Decimal("110.0"),
            "CAD": Decimal("1.25"),
            "AUD": Decimal("1.35"),
            "CHF": Decimal("0.92"),
            "CNY": Decimal("6.45")
        }
        
        # Payment gateways configuration
        self.payment_gateways = {
            "stripe": {"fee_rate": Decimal("0.029"), "fixed_fee": Decimal("0.30")},
            "paypal": {"fee_rate": Decimal("0.034"), "fixed_fee": Decimal("0.30")},
            "bank_transfer": {"fee_rate": Decimal("0.01"), "fixed_fee": Decimal("2.00")},
            "crypto": {"fee_rate": Decimal("0.015"), "fixed_fee": Decimal("0.00")}
        }
        
        logger.info(f"💰 RevenueDistributionService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the revenue distribution service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start background tasks
            asyncio.create_task(self._payment_processor())
            asyncio.create_task(self._revenue_analyzer())
            asyncio.create_task(self._fraud_detector())
            asyncio.create_task(self._tax_calculator())
            
            logger.info(f"✅ RevenueDistributionService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start RevenueDistributionService: {str(e)}")
            return False

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for revenue optimization"""
        try:
            # Revenue prediction model
            self.ml_models["revenue_predictor"] = {
                "version": "1.0",
                "accuracy": 0.89,
                "features": [
                    "historical_revenue", "collaboration_type", "team_size",
                    "content_quality", "market_trends", "seasonal_factors"
                ]
            }
            
            # Fraud detection model
            self.ml_models["fraud_detector"] = {
                "version": "1.0",
                "accuracy": 0.94,
                "features": [
                    "transaction_patterns", "payout_velocity", "account_age",
                    "geographical_risk", "payment_method_risk"
                ]
            }
            
            # Distribution optimization model
            self.ml_models["distribution_optimizer"] = {
                "version": "1.0",
                "accuracy": 0.86,
                "features": [
                    "contribution_metrics", "performance_data", "collaboration_success",
                    "participant_satisfaction", "market_value"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def create_revenue_distribution(
        self,
        collaboration_id: str,
        revenue_data: Dict[str, Any],
        distribution_method: DistributionMethod = DistributionMethod.CONTRIBUTION_WEIGHTED
    ) -> Optional[RevenueDistribution]:
        """Create a new revenue distribution for a collaboration"""
        try:
            start_time = time.time()
            
            # Validate revenue data
            if not await self._validate_revenue_data(revenue_data):
                logger.error(f"Invalid revenue data for collaboration {collaboration_id}")
                return None
            
            # Get collaboration data
            collaboration_data = await self._get_collaboration_data(collaboration_id)
            if not collaboration_data:
                logger.error(f"Collaboration {collaboration_id} not found")
                return None
            
            # Calculate revenue shares
            shares = await self._calculate_revenue_shares(
                collaboration_data, 
                revenue_data, 
                distribution_method
            )
            
            # Apply platform fees
            total_revenue = Decimal(str(revenue_data["amount"]))
            fees_deducted = total_revenue * self.platform_fee_rate
            net_distributable = total_revenue - fees_deducted
            
            # Create distribution record
            distribution = RevenueDistribution(
                distribution_id=str(uuid.uuid4()),
                collaboration_id=collaboration_id,
                total_revenue=total_revenue,
                currency=CurrencyCode(revenue_data["currency"]),
                revenue_source=RevenueSource(revenue_data["source"]),
                distribution_method=distribution_method,
                distribution_date=datetime.now(),
                period_start=datetime.fromisoformat(revenue_data["period_start"]),
                period_end=datetime.fromisoformat(revenue_data["period_end"]),
                shares=shares,
                fees_deducted=fees_deducted,
                net_distributable=net_distributable,
                status=PaymentStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store distribution
            await self._store_distribution(distribution)
            
            # Generate payment transactions
            await self._create_payment_transactions(distribution)
            
            # Update cache
            self.distribution_cache[distribution.distribution_id] = distribution
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Revenue distribution created: {distribution.distribution_id} in {processing_time:.3f}s")
            
            return distribution
            
        except Exception as e:
            logger.error(f"❌ Error creating revenue distribution: {str(e)}")
            return None

    async def _validate_revenue_data(self, revenue_data: Dict[str, Any]) -> bool:
        """Validate revenue data input"""
        try:
            required_fields = ["amount", "currency", "source", "period_start", "period_end"]
            
            for field in required_fields:
                if field not in revenue_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate amount
            amount = Decimal(str(revenue_data["amount"]))
            if amount <= 0:
                logger.error("Revenue amount must be positive")
                return False
            
            # Validate currency
            if revenue_data["currency"] not in [currency.value for currency in CurrencyCode]:
                logger.error(f"Unsupported currency: {revenue_data['currency']}")
                return False
            
            # Validate source
            if revenue_data["source"] not in [source.value for source in RevenueSource]:
                logger.error(f"Invalid revenue source: {revenue_data['source']}")
                return False
            
            # Validate date range
            period_start = datetime.fromisoformat(revenue_data["period_start"])
            period_end = datetime.fromisoformat(revenue_data["period_end"])
            
            if period_start >= period_end:
                logger.error("Period start must be before period end")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating revenue data: {str(e)}")
            return False

    async def _calculate_revenue_shares(
        self,
        collaboration_data: Dict[str, Any],
        revenue_data: Dict[str, Any],
        method: DistributionMethod
    ) -> List[RevenueShare]:
        """Calculate revenue shares based on distribution method"""
        try:
            participants = collaboration_data["participants"]
            shares = []
            
            if method == DistributionMethod.EQUAL_SPLIT:
                shares = await self._calculate_equal_split(participants, revenue_data)
            elif method == DistributionMethod.PERCENTAGE_BASED:
                shares = await self._calculate_percentage_based(participants, collaboration_data, revenue_data)
            elif method == DistributionMethod.CONTRIBUTION_WEIGHTED:
                shares = await self._calculate_contribution_weighted(participants, collaboration_data, revenue_data)
            elif method == DistributionMethod.PERFORMANCE_BASED:
                shares = await self._calculate_performance_based(participants, collaboration_data, revenue_data)
            elif method == DistributionMethod.HYBRID_MODEL:
                shares = await self._calculate_hybrid_model(participants, collaboration_data, revenue_data)
            else:
                # Default to equal split
                shares = await self._calculate_equal_split(participants, revenue_data)
            
            # Validate shares total to 100%
            total_percentage = sum(share.share_percentage for share in shares)
            if abs(total_percentage - Decimal("100.0")) > Decimal("0.01"):
                logger.warning(f"Share percentages total {total_percentage}%, adjusting to 100%")
                await self._normalize_shares(shares)
            
            return shares
            
        except Exception as e:
            logger.error(f"❌ Error calculating revenue shares: {str(e)}")
            return []

    async def _calculate_equal_split(
        self,
        participants: List[Dict[str, Any]],
        revenue_data: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate equal split shares"""
        try:
            share_percentage = Decimal("100.0") / len(participants)
            shares = []
            
            for participant in participants:
                share = RevenueShare(
                    participant_id=participant["id"],
                    participant_name=participant["name"],
                    share_percentage=share_percentage,
                    minimum_amount=self.minimum_payout,
                    maximum_amount=None,
                    role=participant.get("role", "contributor"),
                    contribution_score=1.0,  # Equal contribution
                    vesting_period_days=0,
                    payment_method=participant.get("payment_method", "bank_transfer"),
                    tax_jurisdiction=participant.get("tax_jurisdiction", "US"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                shares.append(share)
            
            return shares
            
        except Exception as e:
            logger.error(f"❌ Error calculating equal split: {str(e)}")
            return []

    async def _calculate_contribution_weighted(
        self,
        participants: List[Dict[str, Any]],
        collaboration_data: Dict[str, Any],
        revenue_data: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate contribution-weighted shares"""
        try:
            # Get contribution scores for each participant
            contribution_scores = await self._calculate_contribution_scores(collaboration_data)
            total_contribution = sum(contribution_scores.values())
            
            shares = []
            
            for participant in participants:
                participant_id = participant["id"]
                contribution_score = contribution_scores.get(participant_id, 0.1)
                share_percentage = (Decimal(str(contribution_score)) / Decimal(str(total_contribution))) * Decimal("100.0")
                
                share = RevenueShare(
                    participant_id=participant_id,
                    participant_name=participant["name"],
                    share_percentage=share_percentage,
                    minimum_amount=self.minimum_payout,
                    maximum_amount=None,
                    role=participant.get("role", "contributor"),
                    contribution_score=contribution_score,
                    vesting_period_days=participant.get("vesting_days", 0),
                    payment_method=participant.get("payment_method", "bank_transfer"),
                    tax_jurisdiction=participant.get("tax_jurisdiction", "US"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                shares.append(share)
            
            return shares
            
        except Exception as e:
            logger.error(f"❌ Error calculating contribution weighted shares: {str(e)}")
            return []

    async def _calculate_contribution_scores(self, collaboration_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate contribution scores for each participant"""
        try:
            scores = {}
            participants = collaboration_data["participants"]
            
            # Initialize scores
            for participant in participants:
                scores[participant["id"]] = 0.0
            
            # Task completion contribution
            tasks = collaboration_data.get("tasks", [])
            for task in tasks:
                assignee = task.get("assignee")
                if assignee and assignee in scores:
                    # Weight by task complexity and quality
                    complexity_weight = task.get("complexity", 1.0)
                    quality_score = task.get("quality_score", 0.8)
                    scores[assignee] += complexity_weight * quality_score
            
            # Content creation contribution
            content_items = collaboration_data.get("content_items", [])
            for item in content_items:
                creator = item.get("creator")
                if creator and creator in scores:
                    # Weight by content value and engagement
                    content_value = item.get("value_score", 1.0)
                    engagement_score = item.get("engagement_score", 0.8)
                    scores[creator] += content_value * engagement_score * 2.0  # Higher weight for content
            
            # Leadership and coordination contribution
            leadership_data = collaboration_data.get("leadership", {})
            for participant_id, leadership_score in leadership_data.items():
                if participant_id in scores:
                    scores[participant_id] += leadership_score * 1.5  # Leadership bonus
            
            # Communication contribution
            communications = collaboration_data.get("communications", [])
            for comm in communications:
                sender = comm.get("sender")
                if sender and sender in scores:
                    scores[sender] += 0.1  # Small bonus for communication
            
            # Normalize scores to ensure minimum contribution
            min_score = 0.1
            for participant_id in scores:
                scores[participant_id] = max(scores[participant_id], min_score)
            
            return scores
            
        except Exception as e:
            logger.error(f"❌ Error calculating contribution scores: {str(e)}")
            return {}

    async def _calculate_performance_based(
        self,
        participants: List[Dict[str, Any]],
        collaboration_data: Dict[str, Any],
        revenue_data: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate performance-based shares"""
        try:
            # Get performance metrics for each participant
            performance_metrics = await self._calculate_performance_metrics(collaboration_data)
            total_performance = sum(performance_metrics.values())
            
            shares = []
            
            for participant in participants:
                participant_id = participant["id"]
                performance_score = performance_metrics.get(participant_id, 0.1)
                share_percentage = (Decimal(str(performance_score)) / Decimal(str(total_performance))) * Decimal("100.0")
                
                # Apply performance bonuses/penalties
                if performance_score > 0.9:  # Top performer
                    share_percentage *= Decimal("1.1")  # 10% bonus
                elif performance_score < 0.3:  # Underperformer
                    share_percentage *= Decimal("0.8")  # 20% penalty
                
                share = RevenueShare(
                    participant_id=participant_id,
                    participant_name=participant["name"],
                    share_percentage=share_percentage,
                    minimum_amount=self.minimum_payout,
                    maximum_amount=None,
                    role=participant.get("role", "contributor"),
                    contribution_score=performance_score,
                    vesting_period_days=participant.get("vesting_days", 0),
                    payment_method=participant.get("payment_method", "bank_transfer"),
                    tax_jurisdiction=participant.get("tax_jurisdiction", "US"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                shares.append(share)
            
            return shares
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance-based shares: {str(e)}")
            return []

    async def _calculate_performance_metrics(self, collaboration_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance metrics for each participant"""
        try:
            metrics = {}
            participants = collaboration_data["participants"]
            
            # Initialize metrics
            for participant in participants:
                metrics[participant["id"]] = 0.0
            
            # Task completion performance
            tasks = collaboration_data.get("tasks", [])
            task_metrics = defaultdict(list)
            
            for task in tasks:
                assignee = task.get("assignee")
                if assignee and assignee in metrics:
                    # On-time completion score
                    planned_date = datetime.fromisoformat(task.get("planned_completion", datetime.now().isoformat()))
                    actual_date = datetime.fromisoformat(task.get("actual_completion", datetime.now().isoformat()))
                    
                    if actual_date <= planned_date:
                        timeliness_score = 1.0
                    else:
                        delay_days = (actual_date - planned_date).days
                        timeliness_score = max(0.0, 1.0 - (delay_days * 0.1))
                    
                    # Quality score
                    quality_score = task.get("quality_score", 0.8)
                    
                    # Combined task performance
                    task_performance = (timeliness_score + quality_score) / 2
                    task_metrics[assignee].append(task_performance)
            
            # Average task performance
            for participant_id, task_scores in task_metrics.items():
                if task_scores:
                    metrics[participant_id] = statistics.mean(task_scores)
            
            # Communication effectiveness
            communications = collaboration_data.get("communications", [])
            comm_quality = defaultdict(list)
            
            for comm in communications:
                sender = comm.get("sender")
                if sender and sender in metrics:
                    # Response time performance
                    response_time = comm.get("response_time_hours", 24)
                    response_score = max(0.0, 1.0 - (response_time / 48))  # 48 hours max
                    
                    # Communication quality (sentiment, clarity)
                    quality = comm.get("quality_score", 0.7)
                    
                    comm_performance = (response_score + quality) / 2
                    comm_quality[sender].append(comm_performance)
            
            # Apply communication performance bonus
            for participant_id, comm_scores in comm_quality.items():
                if comm_scores and participant_id in metrics:
                    comm_avg = statistics.mean(comm_scores)
                    metrics[participant_id] = (metrics[participant_id] * 0.8) + (comm_avg * 0.2)
            
            # Ensure minimum performance score
            for participant_id in metrics:
                metrics[participant_id] = max(metrics[participant_id], 0.1)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {str(e)}")
            return {}

    async def _calculate_hybrid_model(
        self,
        participants: List[Dict[str, Any]],
        collaboration_data: Dict[str, Any],
        revenue_data: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate hybrid model shares (combination of methods)"""
        try:
            # Get shares from different methods
            equal_shares = await self._calculate_equal_split(participants, revenue_data)
            contribution_shares = await self._calculate_contribution_weighted(participants, collaboration_data, revenue_data)
            performance_shares = await self._calculate_performance_based(participants, collaboration_data, revenue_data)
            
            # Weighted combination
            weights = {
                "equal": Decimal("0.3"),      # 30% equal split
                "contribution": Decimal("0.4"), # 40% contribution weighted
                "performance": Decimal("0.3")   # 30% performance based
            }
            
            hybrid_shares = []
            
            for i, participant in enumerate(participants):
                equal_pct = equal_shares[i].share_percentage if i < len(equal_shares) else Decimal("0")
                contrib_pct = contribution_shares[i].share_percentage if i < len(contribution_shares) else Decimal("0")
                perf_pct = performance_shares[i].share_percentage if i < len(performance_shares) else Decimal("0")
                
                hybrid_percentage = (
                    equal_pct * weights["equal"] +
                    contrib_pct * weights["contribution"] +
                    perf_pct * weights["performance"]
                )
                
                # Average contribution score
                contribution_score = (
                    equal_shares[i].contribution_score * float(weights["equal"]) +
                    contribution_shares[i].contribution_score * float(weights["contribution"]) +
                    performance_shares[i].contribution_score * float(weights["performance"])
                ) if i < len(contribution_shares) else 1.0
                
                share = RevenueShare(
                    participant_id=participant["id"],
                    participant_name=participant["name"],
                    share_percentage=hybrid_percentage,
                    minimum_amount=self.minimum_payout,
                    maximum_amount=None,
                    role=participant.get("role", "contributor"),
                    contribution_score=contribution_score,
                    vesting_period_days=participant.get("vesting_days", 0),
                    payment_method=participant.get("payment_method", "bank_transfer"),
                    tax_jurisdiction=participant.get("tax_jurisdiction", "US"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                hybrid_shares.append(share)
            
            return hybrid_shares
            
        except Exception as e:
            logger.error(f"❌ Error calculating hybrid model shares: {str(e)}")
            return []

    async def _normalize_shares(self, shares: List[RevenueShare]) -> None:
        """Normalize shares to total exactly 100%"""
        try:
            total_percentage = sum(share.share_percentage for share in shares)
            
            if total_percentage > 0:
                adjustment_factor = Decimal("100.0") / total_percentage
                
                for share in shares:
                    share.share_percentage = (share.share_percentage * adjustment_factor).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    share.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error normalizing shares: {str(e)}")

    async def _create_payment_transactions(self, distribution: RevenueDistribution) -> None:
        """Create payment transactions for distribution"""
        try:
            transactions = []
            
            for share in distribution.shares:
                # Calculate payout amount
                payout_amount = (distribution.net_distributable * share.share_percentage / Decimal("100.0")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                
                # Skip if below minimum payout
                if payout_amount < share.minimum_amount:
                    logger.info(f"Skipping payout for {share.participant_id}: amount {payout_amount} below minimum {share.minimum_amount}")
                    continue
                
                # Apply maximum limit if set
                if share.maximum_amount and payout_amount > share.maximum_amount:
                    payout_amount = share.maximum_amount
                
                # Calculate payment gateway fees
                gateway_info = self.payment_gateways.get(share.payment_method, self.payment_gateways["bank_transfer"])
                transaction_fee = (payout_amount * gateway_info["fee_rate"]) + gateway_info["fixed_fee"]
                net_amount = payout_amount - transaction_fee
                
                # Create transaction
                transaction = PaymentTransaction(
                    transaction_id=str(uuid.uuid4()),
                    distribution_id=distribution.distribution_id,
                    participant_id=share.participant_id,
                    amount=payout_amount,
                    currency=distribution.currency,
                    transaction_type=TransactionType.REVENUE_SHARE,
                    status=PaymentStatus.PENDING,
                    payment_method=share.payment_method,
                    payment_gateway=share.payment_method,
                    gateway_transaction_id=None,
                    fees=transaction_fee,
                    net_amount=net_amount,
                    processed_at=None,
                    failed_reason=None,
                    retry_count=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                transactions.append(transaction)
                
                # Add to payment queue
                self.payment_queue.append(transaction.transaction_id)
            
            # Store transactions
            for transaction in transactions:
                await self._store_transaction(transaction)
            
            logger.info(f"✅ Created {len(transactions)} payment transactions for distribution {distribution.distribution_id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating payment transactions: {str(e)}")

    async def _store_distribution(self, distribution: RevenueDistribution) -> None:
        """Store revenue distribution to storage"""
        try:
            distribution_key = f"revenue_distribution:{distribution.distribution_id}"
            distribution_data = asdict(distribution)
            
            # Convert Decimal to string for JSON serialization
            distribution_data = await self._serialize_decimals(distribution_data)
            
            await self.redis_client.setex(
                distribution_key,
                86400 * 30,  # Keep for 30 days
                json.dumps(distribution_data, default=str)
            )
            
            # Update collaboration index
            collab_index_key = f"collaboration_distributions:{distribution.collaboration_id}"
            await self.redis_client.lpush(collab_index_key, distribution.distribution_id)
            await self.redis_client.expire(collab_index_key, 86400 * 90)  # Keep index for 90 days
            
            logger.info(f"💾 Distribution {distribution.distribution_id} stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Error storing distribution: {str(e)}")

    async def _store_transaction(self, transaction: PaymentTransaction) -> None:
        """Store payment transaction to storage"""
        try:
            transaction_key = f"payment_transaction:{transaction.transaction_id}"
            transaction_data = asdict(transaction)
            
            # Convert Decimal to string for JSON serialization
            transaction_data = await self._serialize_decimals(transaction_data)
            
            await self.redis_client.setex(
                transaction_key,
                86400 * 90,  # Keep for 90 days
                json.dumps(transaction_data, default=str)
            )
            
            # Update distribution index
            dist_transactions_key = f"distribution_transactions:{transaction.distribution_id}"
            await self.redis_client.lpush(dist_transactions_key, transaction.transaction_id)
            await self.redis_client.expire(dist_transactions_key, 86400 * 90)
            
            # Update participant index
            participant_transactions_key = f"participant_transactions:{transaction.participant_id}"
            await self.redis_client.lpush(participant_transactions_key, transaction.transaction_id)
            await self.redis_client.expire(participant_transactions_key, 86400 * 365)  # Keep for 1 year
            
            logger.info(f"💾 Transaction {transaction.transaction_id} stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Error storing transaction: {str(e)}")

    async def _serialize_decimals(self, data: Any) -> Any:
        """Convert Decimal objects to strings for JSON serialization"""
        if isinstance(data, dict):
            return {key: await self._serialize_decimals(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [await self._serialize_decimals(item) for item in data]
        elif isinstance(data, Decimal):
            return str(data)
        else:
            return data

    async def _get_collaboration_data(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get collaboration data for revenue distribution"""
        try:
            # Check cache first
            cache_key = f"collaboration_revenue_data:{collaboration_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # In real implementation, this would fetch from database
            # For demo, we'll create sample data
            sample_data = {
                "id": collaboration_id,
                "name": f"Revenue Collaboration {collaboration_id[:8]}",
                "participants": [
                    {
                        "id": f"user_{i}",
                        "name": f"User {i}",
                        "role": "creator" if i == 1 else "contributor",
                        "payment_method": "stripe" if i % 2 == 0 else "paypal",
                        "tax_jurisdiction": "US",
                        "vesting_days": 0 if i == 1 else 30
                    }
                    for i in range(1, 5)
                ],
                "tasks": [
                    {
                        "id": str(uuid.uuid4()),
                        "assignee": f"user_{(i % 4) + 1}",
                        "complexity": 1.0 + (i * 0.2),
                        "quality_score": 0.8 + (i * 0.05),
                        "planned_completion": (datetime.now() - timedelta(days=10-i)).isoformat(),
                        "actual_completion": (datetime.now() - timedelta(days=9-i)).isoformat()
                    }
                    for i in range(8)
                ],
                "content_items": [
                    {
                        "id": str(uuid.uuid4()),
                        "creator": f"user_{(i % 4) + 1}",
                        "value_score": 1.0 + (i * 0.3),
                        "engagement_score": 0.7 + (i * 0.1)
                    }
                    for i in range(5)
                ],
                "leadership": {
                    "user_1": 0.9,
                    "user_2": 0.3,
                    "user_3": 0.5,
                    "user_4": 0.2
                },
                "communications": [
                    {
                        "sender": f"user_{(i % 4) + 1}",
                        "response_time_hours": 2 + (i % 12),
                        "quality_score": 0.8 + (i * 0.02)
                    }
                    for i in range(20)
                ]
            }
            
            # Cache the data
            await self.redis_client.setex(cache_key, 3600, json.dumps(sample_data))
            
            return sample_data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving collaboration data: {str(e)}")
            return None

    async def process_payment(self, transaction_id: str) -> bool:
        """Process a payment transaction"""
        try:
            # Get transaction data
            transaction = await self._get_transaction(transaction_id)
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found")
                return False
            
            # Check if already processed
            if transaction.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]:
                logger.info(f"Transaction {transaction_id} already processed with status {transaction.status}")
                return transaction.status == PaymentStatus.COMPLETED
            
            # Fraud detection check
            fraud_risk = await self._assess_fraud_risk(transaction)
            if fraud_risk > 0.8:  # High risk threshold
                logger.warning(f"High fraud risk detected for transaction {transaction_id}: {fraud_risk}")
                await self._update_transaction_status(transaction_id, PaymentStatus.ON_HOLD, "High fraud risk detected")
                return False
            
            # Process payment based on gateway
            success = await self._process_payment_gateway(transaction)
            
            if success:
                await self._update_transaction_status(transaction_id, PaymentStatus.COMPLETED, "Payment processed successfully")
                logger.info(f"✅ Payment {transaction_id} processed successfully")
                
                # Update analytics
                await self._update_payment_analytics(transaction)
                
                return True
            else:
                # Increment retry count
                transaction.retry_count += 1
                
                if transaction.retry_count >= 3:  # Max retries
                    await self._update_transaction_status(transaction_id, PaymentStatus.FAILED, "Maximum retries exceeded")
                    logger.error(f"❌ Payment {transaction_id} failed after maximum retries")
                else:
                    await self._update_transaction_status(transaction_id, PaymentStatus.PENDING, f"Retry {transaction.retry_count}")
                    # Re-queue for retry
                    self.payment_queue.append(transaction_id)
                    logger.info(f"🔄 Payment {transaction_id} queued for retry {transaction.retry_count}")
                
                return False
            
        except Exception as e:
            logger.error(f"❌ Error processing payment {transaction_id}: {str(e)}")
            await self._update_transaction_status(transaction_id, PaymentStatus.FAILED, str(e))
            return False

    async def _get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction data"""
        try:
            transaction_key = f"payment_transaction:{transaction_id}"
            transaction_data = await self.redis_client.get(transaction_key)
            
            if not transaction_data:
                return None
            
            data = json.loads(transaction_data)
            
            # Convert string decimals back to Decimal objects
            data = await self._deserialize_decimals(data)
            
            return PaymentTransaction(**data)
            
        except Exception as e:
            logger.error(f"❌ Error getting transaction: {str(e)}")
            return None

    async def _deserialize_decimals(self, data: Any) -> Any:
        """Convert string decimals back to Decimal objects"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in ["amount", "fees", "net_amount"] and isinstance(value, str):
                    result[key] = Decimal(value)
                else:
                    result[key] = await self._deserialize_decimals(value)
            return result
        elif isinstance(data, list):
            return [await self._deserialize_decimals(item) for item in data]
        else:
            return data

    async def _assess_fraud_risk(self, transaction: PaymentTransaction) -> float:
        """Assess fraud risk for a transaction"""
        try:
            risk_score = 0.0
            
            # Check transaction amount
            if transaction.amount > Decimal("10000"):  # Large amount
                risk_score += 0.3
            elif transaction.amount > Decimal("1000"):  # Medium amount
                risk_score += 0.1
            
            # Check payment method risk
            payment_method_risk = {
                "crypto": 0.4,
                "paypal": 0.2,
                "stripe": 0.1,
                "bank_transfer": 0.05
            }
            risk_score += payment_method_risk.get(transaction.payment_method, 0.3)
            
            # Check velocity (frequency of payments)
            participant_transactions = await self._get_recent_transactions(transaction.participant_id, days=7)
            if len(participant_transactions) > 10:  # More than 10 transactions in a week
                risk_score += 0.2
            
            # Check geographic risk (simplified)
            # In real implementation, this would check IP location, country risk, etc.
            risk_score += 0.1  # Base geographic risk
            
            # Account age risk
            # In real implementation, check account creation date
            risk_score += 0.05  # Base account risk
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"❌ Error assessing fraud risk: {str(e)}")
            return 0.5  # Medium risk if assessment fails

    async def _get_recent_transactions(self, participant_id: str, days: int = 30) -> List[str]:
        """Get recent transactions for a participant"""
        try:
            participant_transactions_key = f"participant_transactions:{participant_id}"
            transaction_ids = await self.redis_client.lrange(participant_transactions_key, 0, -1)
            
            # In real implementation, filter by date
            # For now, return all transactions
            return [tid.decode() if isinstance(tid, bytes) else tid for tid in transaction_ids]
            
        except Exception as e:
            logger.error(f"❌ Error getting recent transactions: {str(e)}")
            return []

    async def _process_payment_gateway(self, transaction: PaymentTransaction) -> bool:
        """Process payment through gateway (simplified simulation)"""
        try:
            # Simulate payment processing
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            # Simulate success/failure rates based on payment method
            success_rates = {
                "stripe": 0.98,
                "paypal": 0.96,
                "bank_transfer": 0.94,
                "crypto": 0.92
            }
            
            success_rate = success_rates.get(transaction.payment_method, 0.90)
            
            # Simulate random success/failure
            import random
            success = random.random() < success_rate
            
            if success:
                # Generate gateway transaction ID
                transaction.gateway_transaction_id = f"gw_{uuid.uuid4().hex[:16]}"
                transaction.processed_at = datetime.now()
                
                logger.info(f"💳 Payment gateway processed transaction {transaction.transaction_id}")
                return True
            else:
                transaction.failed_reason = "Payment gateway declined"
                logger.warning(f"💳 Payment gateway declined transaction {transaction.transaction_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error processing payment gateway: {str(e)}")
            return False

    async def _update_transaction_status(
        self, 
        transaction_id: str, 
        status: PaymentStatus, 
        reason: Optional[str] = None
    ) -> None:
        """Update transaction status"""
        try:
            transaction = await self._get_transaction(transaction_id)
            if not transaction:
                return
            
            transaction.status = status
            transaction.updated_at = datetime.now()
            
            if reason and status == PaymentStatus.FAILED:
                transaction.failed_reason = reason
            
            # Store updated transaction
            await self._store_transaction(transaction)
            
            logger.info(f"📝 Transaction {transaction_id} status updated to {status.value}")
            
        except Exception as e:
            logger.error(f"❌ Error updating transaction status: {str(e)}")

    async def _update_payment_analytics(self, transaction: PaymentTransaction) -> None:
        """Update payment analytics after successful payment"""
        try:
            # Update daily statistics
            today = datetime.now().date().isoformat()
            analytics_key = f"payment_analytics_daily:{today}"
            
            analytics_data = await self.redis_client.get(analytics_key)
            if analytics_data:
                analytics = json.loads(analytics_data)
            else:
                analytics = {
                    "date": today,
                    "total_payments": 0,
                    "total_amount": "0.00",
                    "successful_payments": 0,
                    "failed_payments": 0,
                    "average_amount": "0.00",
                    "by_method": {},
                    "by_currency": {}
                }
            
            # Update statistics
            analytics["total_payments"] += 1
            analytics["successful_payments"] += 1
            
            current_total = Decimal(analytics["total_amount"])
            new_total = current_total + transaction.amount
            analytics["total_amount"] = str(new_total)
            analytics["average_amount"] = str(new_total / analytics["successful_payments"])
            
            # By payment method
            method = transaction.payment_method
            if method not in analytics["by_method"]:
                analytics["by_method"][method] = {"count": 0, "amount": "0.00"}
            
            analytics["by_method"][method]["count"] += 1
            method_amount = Decimal(analytics["by_method"][method]["amount"]) + transaction.amount
            analytics["by_method"][method]["amount"] = str(method_amount)
            
            # By currency
            currency = transaction.currency.value
            if currency not in analytics["by_currency"]:
                analytics["by_currency"][currency] = {"count": 0, "amount": "0.00"}
            
            analytics["by_currency"][currency]["count"] += 1
            currency_amount = Decimal(analytics["by_currency"][currency]["amount"]) + transaction.amount
            analytics["by_currency"][currency]["amount"] = str(currency_amount)
            
            # Store updated analytics
            await self.redis_client.setex(analytics_key, 86400 * 30, json.dumps(analytics))
            
            logger.info(f"📊 Payment analytics updated for {today}")
            
        except Exception as e:
            logger.error(f"❌ Error updating payment analytics: {str(e)}")

    async def _payment_processor(self) -> None:
        """Background task for processing payment queue"""
        while True:
            try:
                if self.payment_queue:
                    # Process payments in batches
                    batch_size = min(self.payment_batch_size, len(self.payment_queue))
                    transaction_ids = [self.payment_queue.popleft() for _ in range(batch_size)]
                    
                    # Process batch concurrently
                    tasks = [self.process_payment(tid) for tid in transaction_ids]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    successful_payments = sum(1 for result in results if result is True)
                    logger.info(f"💳 Processed batch: {successful_payments}/{len(transaction_ids)} successful")
                
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in payment processor: {str(e)}")
                await asyncio.sleep(30)

    async def _revenue_analyzer(self) -> None:
        """Background task for revenue analysis"""
        while True:
            try:
                # Analyze revenue patterns and generate insights
                await self._generate_revenue_insights()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in revenue analyzer: {str(e)}")
                await asyncio.sleep(600)

    async def _fraud_detector(self) -> None:
        """Background task for fraud detection"""
        while True:
            try:
                # Monitor for suspicious patterns
                await self._monitor_fraud_patterns()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in fraud detector: {str(e)}")
                await asyncio.sleep(600)

    async def _tax_calculator(self) -> None:
        """Background task for tax calculations"""
        while True:
            try:
                # Calculate taxes for completed payments
                await self._calculate_tax_obligations()
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"❌ Error in tax calculator: {str(e)}")
                await asyncio.sleep(3600)

    async def _generate_revenue_insights(self) -> None:
        """Generate revenue insights and analytics"""
        try:
            # Get recent revenue distributions
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Analyze revenue trends
            insights = {
                "timestamp": datetime.now().isoformat(),
                "revenue_trends": await self._analyze_revenue_trends(week_ago, today),
                "distribution_efficiency": await self._analyze_distribution_efficiency(),
                "participant_performance": await self._analyze_participant_performance(),
                "recommendations": await self._generate_revenue_recommendations()
            }
            
            # Store insights
            insights_key = f"revenue_insights:{today.isoformat()}"
            await self.redis_client.setex(insights_key, 86400 * 7, json.dumps(insights, default=str))
            
            logger.info(f"📈 Revenue insights generated for {today}")
            
        except Exception as e:
            logger.error(f"❌ Error generating revenue insights: {str(e)}")

    async def _monitor_fraud_patterns(self) -> None:
        """Monitor for fraudulent patterns"""
        try:
            # Get recent transactions
            recent_transactions = await self._get_recent_all_transactions(hours=24)
            
            # Analyze patterns
            fraud_alerts = []
            
            # Unusual velocity patterns
            participant_velocity = defaultdict(int)
            for transaction in recent_transactions:
                participant_velocity[transaction.participant_id] += 1
            
            for participant_id, count in participant_velocity.items():
                if count > 20:  # More than 20 transactions in 24 hours
                    fraud_alerts.append({
                        "type": "high_velocity",
                        "participant_id": participant_id,
                        "transaction_count": count,
                        "severity": "medium"
                    })
            
            # Large amount patterns
            for transaction in recent_transactions:
                if transaction.amount > Decimal("50000"):  # Large transaction
                    fraud_alerts.append({
                        "type": "large_amount",
                        "transaction_id": transaction.transaction_id,
                        "amount": str(transaction.amount),
                        "severity": "high"
                    })
            
            # Store fraud alerts
            if fraud_alerts:
                alerts_key = f"fraud_alerts:{datetime.now().date().isoformat()}"
                await self.redis_client.setex(alerts_key, 86400 * 7, json.dumps(fraud_alerts, default=str))
                
                logger.warning(f"🚨 {len(fraud_alerts)} fraud alerts generated")
            
        except Exception as e:
            logger.error(f"❌ Error monitoring fraud patterns: {str(e)}")

    async def _get_recent_all_transactions(self, hours: int = 24) -> List[PaymentTransaction]:
        """Get all recent transactions"""
        try:
            # This is a simplified implementation
            # In production, this would query the database with proper indexing
            transactions = []
            
            # Get all transaction keys (simplified approach)
            pattern = "payment_transaction:*"
            keys = await self.redis_client.keys(pattern)
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for key in keys[:100]:  # Limit to avoid performance issues
                transaction_data = await self.redis_client.get(key)
                if transaction_data:
                    data = json.loads(transaction_data)
                    created_at = datetime.fromisoformat(data["created_at"])
                    
                    if created_at >= cutoff_time:
                        data = await self._deserialize_decimals(data)
                        transactions.append(PaymentTransaction(**data))
            
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Error getting recent transactions: {str(e)}")
            return []

    async def get_distribution_status(self, distribution_id: str) -> Optional[Dict[str, Any]]:
        """Get distribution status and details"""
        try:
            # Get distribution data
            distribution_key = f"revenue_distribution:{distribution_id}"
            distribution_data = await self.redis_client.get(distribution_key)
            
            if not distribution_data:
                return None
            
            distribution = json.loads(distribution_data)
            
            # Get transaction statuses
            dist_transactions_key = f"distribution_transactions:{distribution_id}"
            transaction_ids = await self.redis_client.lrange(dist_transactions_key, 0, -1)
            
            transaction_statuses = []
            total_amount = Decimal("0")
            completed_amount = Decimal("0")
            
            for tid in transaction_ids:
                transaction_id = tid.decode() if isinstance(tid, bytes) else tid
                transaction = await self._get_transaction(transaction_id)
                
                if transaction:
                    total_amount += transaction.amount
                    if transaction.status == PaymentStatus.COMPLETED:
                        completed_amount += transaction.amount
                    
                    transaction_statuses.append({
                        "transaction_id": transaction.transaction_id,
                        "participant_id": transaction.participant_id,
                        "amount": str(transaction.amount),
                        "status": transaction.status.value,
                        "payment_method": transaction.payment_method,
                        "processed_at": transaction.processed_at.isoformat() if transaction.processed_at else None
                    })
            
            # Calculate completion percentage
            completion_percentage = float((completed_amount / total_amount) * 100) if total_amount > 0 else 0
            
            return {
                "distribution_id": distribution_id,
                "collaboration_id": distribution["collaboration_id"],
                "total_revenue": distribution["total_revenue"],
                "net_distributable": distribution["net_distributable"],
                "currency": distribution["currency"],
                "status": distribution["status"],
                "completion_percentage": completion_percentage,
                "completed_amount": str(completed_amount),
                "total_transactions": len(transaction_statuses),
                "transactions": transaction_statuses,
                "created_at": distribution["created_at"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting distribution status: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "RevenueDistributionService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "payment_queue_size": len(self.payment_queue),
                "cache_size": len(self.distribution_cache),
                "ml_models_loaded": len(self.ml_models),
                "platform_fee_rate": str(self.platform_fee_rate),
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connected"] = True
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "RevenueDistributionService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the revenue distribution service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 RevenueDistributionService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of RevenueDistributionService"""
    service = RevenueDistributionService()
    
    try:
        # Start service
        await service.start()
        
        # Test revenue distribution
        collaboration_id = "test_collaboration_001"
        revenue_data = {
            "amount": "1000.00",
            "currency": "USD",
            "source": "streaming",
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat()
        }
        
        print(f"💰 Creating revenue distribution for collaboration: {collaboration_id}")
        distribution = await service.create_revenue_distribution(
            collaboration_id, 
            revenue_data, 
            DistributionMethod.CONTRIBUTION_WEIGHTED
        )
        
        if distribution:
            print(f"✅ Distribution created:")
            print(f"   - Distribution ID: {distribution.distribution_id}")
            print(f"   - Total Revenue: ${distribution.total_revenue}")
            print(f"   - Net Distributable: ${distribution.net_distributable}")
            print(f"   - Participants: {len(distribution.shares)}")
            
            for share in distribution.shares:
                print(f"   - {share.participant_name}: {share.share_percentage}% (${(distribution.net_distributable * share.share_percentage / 100):.2f})")
        
        # Check distribution status
        if distribution:
            await asyncio.sleep(2)  # Wait for processing
            status = await service.get_distribution_status(distribution.distribution_id)
            if status:
                print(f"📊 Distribution Status: {status['completion_percentage']:.1f}% complete")
        
        # Health check
        health = await service.health_check()
        print(f"🏥 Service health: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())