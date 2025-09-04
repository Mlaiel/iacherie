"""Donation Handler System
=======================

Advanced donation processing system for live streaming with real-time payment
processing, donation alerts, goal tracking, and comprehensive analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import hashlib
import hmac

Base = declarative_base()
logger = logging.getLogger(__name__)


class DonationStatus(Enum):
    """Donation processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class DonationType(Enum):
    """Types of donations"""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    GOAL_CONTRIBUTION = "goal_contribution"
    TIP = "tip"
    SUPERCHAT = "superchat"
    GIFT_SUBSCRIPTION = "gift_subscription"


class CurrencyCode(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    BTC = "BTC"
    ETH = "ETH"


class AlertType(Enum):
    """Donation alert types"""
    POPUP = "popup"
    BANNER = "banner"
    SOUND = "sound"
    ANIMATION = "animation"
    TEXT_TO_SPEECH = "text_to_speech"
    OVERLAY = "overlay"


@dataclass
class DonationGoal:
    """Stream donation goal"""
    goal_id: str
    title: str
    description: str
    target_amount: Decimal
    current_amount: Decimal = Decimal('0.00')
    currency: CurrencyCode = CurrencyCode.USD
    deadline: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    achieved_at: Optional[datetime] = None
    contributors_count: int = 0


@dataclass
class DonationAlert:
    """Donation alert configuration"""
    alert_id: str
    alert_type: AlertType
    min_amount: Decimal
    max_amount: Optional[Decimal] = None
    currency: CurrencyCode = CurrencyCode.USD
    message_template: str = "Thank you {donor_name} for the ${amount} donation!"
    duration_seconds: int = 5
    sound_file: Optional[str] = None
    animation_name: Optional[str] = None
    text_color: str = "#FFFFFF"
    background_color: str = "#1E3A8A"
    font_size: int = 24
    is_enabled: bool = True


@dataclass
class DonationConfig:
    """Stream donation configuration"""
    enabled: bool = True
    min_amount: Decimal = Decimal('1.00')
    max_amount: Decimal = Decimal('10000.00')
    currency: CurrencyCode = CurrencyCode.USD
    accepted_currencies: List[CurrencyCode] = field(default_factory=lambda: [CurrencyCode.USD])
    payment_methods: List[PaymentMethod] = field(default_factory=lambda: [PaymentMethod.STRIPE, PaymentMethod.PAYPAL])
    goals: List[DonationGoal] = field(default_factory=list)
    alerts: List[DonationAlert] = field(default_factory=list)
    moderator_approval_required: bool = False
    anonymous_donations_allowed: bool = True
    message_max_length: int = 500
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DonationMetrics:
    """Donation performance metrics"""
    stream_id: str
    total_donations: Decimal = Decimal('0.00')
    total_count: int = 0
    average_donation: Decimal = Decimal('0.00')
    largest_donation: Decimal = Decimal('0.00')
    unique_donors: int = 0
    donations_per_hour: float = 0.0
    conversion_rate: float = 0.0
    goal_progress: Dict[str, float] = field(default_factory=dict)
    top_donors: List[Dict[str, Any]] = field(default_factory=list)
    recent_donations: List[Dict[str, Any]] = field(default_factory=list)
    currency_breakdown: Dict[str, Decimal] = field(default_factory=dict)


class Donation(Base):
    """Database model for donations"""
    __tablename__ = "donations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Donor information
    donor_name = Column(String(255))
    donor_email = Column(String(255))
    is_anonymous = Column(Boolean, default=False)
    
    # Donation details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    donation_type = Column(String(50), default=DonationType.ONE_TIME.value)
    
    # Payment details
    payment_method = Column(String(50))
    payment_processor = Column(String(50))
    transaction_id = Column(String(255), unique=True)
    processor_fee = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2))
    
    # Message and metadata
    message = Column(Text)
    is_message_approved = Column(Boolean, default=True)
    additional_data = Column(JSON, default=dict)
    
    # Status and processing
    status = Column(String(50), default=DonationStatus.PENDING.value)
    processed_at = Column(DateTime(timezone=True))
    failed_reason = Column(String(500))
    
    # Goal association
    goal_id = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DonationGoalRecord(Base):
    """Database model for donation goals"""
    __tablename__ = "donation_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(String(255), unique=True, nullable=False, index=True)
    stream_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Goal details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    target_amount = Column(Numeric(10, 2), nullable=False)
    current_amount = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    
    # Status and timing
    is_active = Column(Boolean, default=True)
    deadline = Column(DateTime(timezone=True))
    achieved_at = Column(DateTime(timezone=True))
    contributors_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DonationHandler:
    """Advanced donation processing and management system"""
    
    def __init__(self, redis_client: Any, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.active_streams: Dict[str, DonationConfig] = {}
        self.payment_processors: Dict[str, Any] = {}
        self.webhook_secrets: Dict[str, str] = {}
        self.metrics_cache: Dict[str, DonationMetrics] = {}
        self.is_running = False
        
    async def start_handler(self):
        """Start the donation handler system"""
        self.is_running = True
        logger.info("Donation handler system started")
        
        # Initialize payment processors
        await self._initialize_payment_processors()
        
        # Start background tasks
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._goal_monitor())
        asyncio.create_task(self._payment_processor())
        
    async def stop_handler(self):
        """Stop the donation handler system"""
        self.is_running = False
        logger.info("Donation handler system stopped")
        
    async def configure_stream_donations(
        self,
        stream_id: str,
        user_id: str,
        config: DonationConfig
    ) -> bool:
        """Configure donations for a stream"""
        try:
            self.active_streams[stream_id] = config
            
            # Store configuration in Redis
            await self.redis.hset(
                f"donation_config:{stream_id}",
                mapping={
                    "user_id": user_id,
                    "config": json.dumps(asdict(config), default=str),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Initialize metrics
            self.metrics_cache[stream_id] = DonationMetrics(stream_id=stream_id)
            
            # Setup goals in database
            for goal in config.goals:
                await self._create_goal_record(stream_id, user_id, goal)
                
            logger.info(f"Donations configured for stream: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure donations for stream {stream_id}: {str(e)}")
            return False
            
    async def process_donation(
        self,
        stream_id: str,
        donor_info: Dict[str, Any],
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethod,
        message: Optional[str] = None,
        goal_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a new donation"""
        try:
            config = self.active_streams.get(stream_id)
            if not config or not config.enabled:
                return {"success": False, "error": "Donations not enabled for this stream"}
                
            # Validate donation amount
            if amount < config.min_amount or amount > config.max_amount:
                return {
                    "success": False,
                    "error": f"Amount must be between {config.min_amount} and {config.max_amount}"
                }
                
            # Validate currency
            if currency not in config.accepted_currencies:
                return {"success": False, "error": f"Currency {currency.value} not accepted"}
                
            # Validate payment method
            if payment_method not in config.payment_methods:
                return {"success": False, "error": f"Payment method {payment_method.value} not supported"}
                
            # Create donation record
            donation_id = str(uuid.uuid4())
            transaction_id = await self._generate_transaction_id(donation_id)
            
            donation = Donation(
                id=donation_id,
                stream_id=stream_id,
                user_id=donor_info.get("user_id", ""),
                donor_name=donor_info.get("name", "Anonymous"),
                donor_email=donor_info.get("email"),
                is_anonymous=donor_info.get("is_anonymous", False),
                amount=amount,
                currency=currency.value,
                donation_type=DonationType.ONE_TIME.value,
                payment_method=payment_method.value,
                transaction_id=transaction_id,
                message=message,
                goal_id=goal_id,
                additional_data=metadata or {},
                status=DonationStatus.PENDING.value
            )
            
            self.db.add(donation)
            self.db.commit()
            
            # Process payment
            payment_result = await self._process_payment(donation, payment_method)
            
            if payment_result["success"]:
                # Update donation status
                donation.status = DonationStatus.PROCESSING.value
                donation.processor_fee = Decimal(str(payment_result.get("fee", 0)))
                donation.net_amount = amount - donation.processor_fee
                self.db.commit()
                
                # Add to processing queue
                await self.redis.lpush(
                    "donation_processing_queue",
                    json.dumps({
                        "donation_id": donation_id,
                        "stream_id": stream_id,
                        "amount": str(amount),
                        "currency": currency.value,
                        "payment_result": payment_result
                    })
                )
                
                # Send immediate response
                return {
                    "success": True,
                    "donation_id": donation_id,
                    "transaction_id": transaction_id,
                    "status": "processing",
                    "estimated_completion": "2-5 seconds"
                }
            else:
                # Update donation as failed
                donation.status = DonationStatus.FAILED.value
                donation.failed_reason = payment_result.get("error", "Payment processing failed")
                self.db.commit()
                
                return {
                    "success": False,
                    "error": payment_result.get("error", "Payment processing failed"),
                    "donation_id": donation_id
                }
                
        except Exception as e:
            logger.error(f"Failed to process donation for stream {stream_id}: {str(e)}")
            return {"success": False, "error": "Internal processing error"}
            
    async def complete_donation(self, donation_id: str) -> bool:
        """Complete a donation and trigger alerts"""
        try:
            donation = self.db.query(Donation).filter(Donation.id == donation_id).first()
            if not donation:
                logger.error(f"Donation not found: {donation_id}")
                return False
                
            # Update status
            donation.status = DonationStatus.COMPLETED.value
            donation.processed_at = datetime.now(timezone.utc)
            self.db.commit()
            
            # Update goal progress if applicable
            if donation.goal_id:
                await self._update_goal_progress(donation.goal_id, donation.amount)
                
            # Update metrics
            await self._update_donation_metrics(donation.stream_id, donation)
            
            # Trigger donation alert
            await self._trigger_donation_alert(donation)
            
            # Send webhook notifications
            await self._send_webhook_notifications(donation)
            
            # Publish donation event
            await self.redis.publish(
                f"donations:{donation.stream_id}",
                json.dumps({
                    "type": "donation_completed",
                    "donation_id": donation_id,
                    "amount": str(donation.amount),
                    "currency": donation.currency,
                    "donor_name": donation.donor_name if not donation.is_anonymous else "Anonymous",
                    "message": donation.message,
                    "timestamp": donation.processed_at.isoformat()
                })
            )
            
            logger.info(f"Donation completed: {donation_id} - ${donation.amount}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete donation {donation_id}: {str(e)}")
            return False
            
    async def create_donation_goal(
        self,
        stream_id: str,
        user_id: str,
        title: str,
        target_amount: Decimal,
        currency: CurrencyCode = CurrencyCode.USD,
        description: str = "",
        deadline: Optional[datetime] = None
    ) -> str:
        """Create a new donation goal"""
        try:
            goal_id = str(uuid.uuid4())
            
            goal = DonationGoal(
                goal_id=goal_id,
                title=title,
                description=description,
                target_amount=target_amount,
                currency=currency,
                deadline=deadline
            )
            
            # Create database record
            await self._create_goal_record(stream_id, user_id, goal)
            
            # Add to stream config
            config = self.active_streams.get(stream_id)
            if config:
                config.goals.append(goal)
                
            # Store in Redis
            await self.redis.hset(
                f"donation_goals:{stream_id}",
                goal_id,
                json.dumps(asdict(goal), default=str)
            )
            
            logger.info(f"Donation goal created: {goal_id} for stream: {stream_id}")
            return goal_id
            
        except Exception as e:
            logger.error(f"Failed to create donation goal: {str(e)}")
            raise
            
    async def update_donation_goal(
        self,
        goal_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a donation goal"""
        try:
            # Update database record
            goal_record = self.db.query(DonationGoalRecord).filter(
                DonationGoalRecord.goal_id == goal_id
            ).first()
            
            if not goal_record:
                logger.error(f"Goal not found: {goal_id}")
                return False
                
            # Apply updates
            for field, value in updates.items():
                if hasattr(goal_record, field):
                    setattr(goal_record, field, value)
                    
            goal_record.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            
            # Update Redis cache
            goal_data = {
                "goal_id": goal_record.goal_id,
                "title": goal_record.title,
                "description": goal_record.description,
                "target_amount": str(goal_record.target_amount),
                "current_amount": str(goal_record.current_amount),
                "currency": goal_record.currency,
                "deadline": goal_record.deadline.isoformat() if goal_record.deadline else None,
                "is_active": goal_record.is_active,
                "achieved_at": goal_record.achieved_at.isoformat() if goal_record.achieved_at else None,
                "contributors_count": goal_record.contributors_count
            }
            
            await self.redis.hset(
                f"donation_goals:{goal_record.stream_id}",
                goal_id,
                json.dumps(goal_data)
            )
            
            logger.info(f"Donation goal updated: {goal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update donation goal {goal_id}: {str(e)}")
            return False
            
    async def get_donation_metrics(self, stream_id: str) -> Optional[DonationMetrics]:
        """Get donation metrics for a stream"""
        try:
            # Return cached metrics if available
            if stream_id in self.metrics_cache:
                return self.metrics_cache[stream_id]
                
            # Load from database
            donations = self.db.query(Donation).filter(
                Donation.stream_id == stream_id,
                Donation.status == DonationStatus.COMPLETED.value
            ).all()
            
            if not donations:
                return DonationMetrics(stream_id=stream_id)
                
            # Calculate metrics
            total_amount = sum(Decimal(str(d.amount)) for d in donations)
            total_count = len(donations)
            average_amount = total_amount / total_count if total_count > 0 else Decimal('0')
            largest_amount = max(Decimal(str(d.amount)) for d in donations) if donations else Decimal('0')
            unique_donors = len(set(d.user_id for d in donations if d.user_id))
            
            # Calculate currency breakdown
            currency_breakdown = {}
            for donation in donations:
                currency = donation.currency
                currency_breakdown[currency] = currency_breakdown.get(currency, Decimal('0')) + Decimal(str(donation.amount))
                
            # Get recent donations (last 10)
            recent_donations = []
            for donation in sorted(donations, key=lambda x: x.created_at, reverse=True)[:10]:
                recent_donations.append({
                    "amount": str(donation.amount),
                    "currency": donation.currency,
                    "donor_name": donation.donor_name if not donation.is_anonymous else "Anonymous",
                    "message": donation.message,
                    "timestamp": donation.created_at.isoformat()
                })
                
            # Create metrics object
            metrics = DonationMetrics(
                stream_id=stream_id,
                total_donations=total_amount,
                total_count=total_count,
                average_donation=average_amount,
                largest_donation=largest_amount,
                unique_donors=unique_donors,
                recent_donations=recent_donations,
                currency_breakdown={k: str(v) for k, v in currency_breakdown.items()}
            )
            
            # Cache metrics
            self.metrics_cache[stream_id] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get donation metrics for stream {stream_id}: {str(e)}")
            return None
            
    async def get_donation_goals(self, stream_id: str) -> List[Dict[str, Any]]:
        """Get all donation goals for a stream"""
        try:
            goals_data = await self.redis.hgetall(f"donation_goals:{stream_id}")
            
            goals = []
            for goal_id, goal_json in goals_data.items():
                goal_data = json.loads(goal_json)
                goals.append(goal_data)
                
            return goals
            
        except Exception as e:
            logger.error(f"Failed to get donation goals for stream {stream_id}: {str(e)}")
            return []
            
    async def handle_webhook(
        self,
        processor: str,
        signature: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment processor webhook"""
        try:
            # Verify webhook signature
            if not await self._verify_webhook_signature(processor, signature, payload):
                return {"success": False, "error": "Invalid signature"}
                
            # Process webhook based on processor
            if processor == "stripe":
                return await self._handle_stripe_webhook(payload)
            elif processor == "paypal":
                return await self._handle_paypal_webhook(payload)
            else:
                return {"success": False, "error": "Unknown processor"}
                
        except Exception as e:
            logger.error(f"Failed to handle webhook from {processor}: {str(e)}")
            return {"success": False, "error": "Webhook processing failed"}
            
    async def refund_donation(
        self,
        donation_id: str,
        reason: str = "",
        amount: Optional[Decimal] = None
    ) -> bool:
        """Refund a donation"""
        try:
            donation = self.db.query(Donation).filter(Donation.id == donation_id).first()
            if not donation:
                logger.error(f"Donation not found: {donation_id}")
                return False
                
            if donation.status != DonationStatus.COMPLETED.value:
                logger.error(f"Cannot refund donation in status: {donation.status}")
                return False
                
            # Process refund with payment processor
            refund_amount = amount or donation.amount
            refund_result = await self._process_refund(donation, refund_amount, reason)
            
            if refund_result["success"]:
                # Update donation status
                donation.status = DonationStatus.REFUNDED.value
                donation.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                
                # Update goal progress if applicable
                if donation.goal_id:
                    await self._update_goal_progress(donation.goal_id, -refund_amount)
                    
                # Update metrics
                await self._update_refund_metrics(donation.stream_id, refund_amount)
                
                logger.info(f"Donation refunded: {donation_id} - ${refund_amount}")
                return True
            else:
                logger.error(f"Refund failed for donation {donation_id}: {refund_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to refund donation {donation_id}: {str(e)}")
            return False
            
    async def _initialize_payment_processors(self):
        """Initialize payment processor configurations"""
        # This would be configured with actual API keys and settings
        self.payment_processors = {
            PaymentMethod.STRIPE: {
                "api_key": "sk_test_...",  # Would be from config
                "webhook_secret": "whsec_...",
                "enabled": True
            },
            PaymentMethod.PAYPAL: {
                "client_id": "...",
                "client_secret": "...",
                "webhook_id": "...",
                "enabled": True
            }
        }
        
        logger.info("Payment processors initialized")
        
    async def _generate_transaction_id(self, donation_id: str) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"TXN_{timestamp}_{donation_id[:8]}"
        
    async def _process_payment(
        self,
        donation: Donation,
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """Process payment with appropriate processor"""
        try:
            if payment_method == PaymentMethod.STRIPE:
                return await self._process_stripe_payment(donation)
            elif payment_method == PaymentMethod.PAYPAL:
                return await self._process_paypal_payment(donation)
            else:
                # Mock success for other payment methods in this implementation
                return {
                    "success": True,
                    "processor_transaction_id": f"mock_{donation.transaction_id}",
                    "fee": float(donation.amount) * 0.029 + 0.30  # Mock Stripe fee
                }
                
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _process_stripe_payment(self, donation: Donation) -> Dict[str, Any]:
        """Process payment through Stripe"""
        # Mock Stripe integration
        return {
            "success": True,
            "processor_transaction_id": f"pi_{donation.transaction_id}",
            "fee": float(donation.amount) * 0.029 + 0.30
        }
        
    async def _process_paypal_payment(self, donation: Donation) -> Dict[str, Any]:
        """Process payment through PayPal"""
        # Mock PayPal integration
        return {
            "success": True,
            "processor_transaction_id": f"pp_{donation.transaction_id}",
            "fee": float(donation.amount) * 0.034 + 0.49
        }
        
    async def _process_refund(
        self,
        donation: Donation,
        amount: Decimal,
        reason: str
    ) -> Dict[str, Any]:
        """Process refund with payment processor"""
        # Mock refund processing
        return {
            "success": True,
            "refund_id": f"ref_{donation.transaction_id}",
            "amount": str(amount)
        }
        
    async def _create_goal_record(
        self,
        stream_id: str,
        user_id: str,
        goal: DonationGoal
    ):
        """Create donation goal database record"""
        try:
            goal_record = DonationGoalRecord(
                goal_id=goal.goal_id,
                stream_id=stream_id,
                user_id=user_id,
                title=goal.title,
                description=goal.description,
                target_amount=goal.target_amount,
                current_amount=goal.current_amount,
                currency=goal.currency.value,
                deadline=goal.deadline,
                is_active=goal.is_active
            )
            
            self.db.add(goal_record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create goal record: {str(e)}")
            self.db.rollback()
            raise
            
    async def _update_goal_progress(self, goal_id: str, amount: Decimal):
        """Update goal progress with donation amount"""
        try:
            goal_record = self.db.query(DonationGoalRecord).filter(
                DonationGoalRecord.goal_id == goal_id
            ).first()
            
            if goal_record:
                goal_record.current_amount += amount
                goal_record.contributors_count += 1 if amount > 0 else 0
                
                # Check if goal is achieved
                if goal_record.current_amount >= goal_record.target_amount and not goal_record.achieved_at:
                    goal_record.achieved_at = datetime.now(timezone.utc)
                    
                    # Publish goal achievement event
                    await self.redis.publish(
                        f"donations:{goal_record.stream_id}",
                        json.dumps({
                            "type": "goal_achieved",
                            "goal_id": goal_id,
                            "title": goal_record.title,
                            "target_amount": str(goal_record.target_amount),
                            "achieved_at": goal_record.achieved_at.isoformat()
                        })
                    )
                    
                goal_record.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                
                # Update Redis cache
                goal_data = {
                    "goal_id": goal_record.goal_id,
                    "title": goal_record.title,
                    "description": goal_record.description,
                    "target_amount": str(goal_record.target_amount),
                    "current_amount": str(goal_record.current_amount),
                    "currency": goal_record.currency,
                    "deadline": goal_record.deadline.isoformat() if goal_record.deadline else None,
                    "is_active": goal_record.is_active,
                    "achieved_at": goal_record.achieved_at.isoformat() if goal_record.achieved_at else None,
                    "contributors_count": goal_record.contributors_count
                }
                
                await self.redis.hset(
                    f"donation_goals:{goal_record.stream_id}",
                    goal_id,
                    json.dumps(goal_data)
                )
                
        except Exception as e:
            logger.error(f"Failed to update goal progress: {str(e)}")
            self.db.rollback()
            
    async def _update_donation_metrics(self, stream_id: str, donation: Donation):
        """Update donation metrics"""
        try:
            metrics = self.metrics_cache.get(stream_id)
            if not metrics:
                metrics = DonationMetrics(stream_id=stream_id)
                self.metrics_cache[stream_id] = metrics
                
            # Update metrics
            metrics.total_donations += Decimal(str(donation.amount))
            metrics.total_count += 1
            metrics.average_donation = metrics.total_donations / metrics.total_count
            
            if Decimal(str(donation.amount)) > metrics.largest_donation:
                metrics.largest_donation = Decimal(str(donation.amount))
                
            # Add to recent donations
            donation_data = {
                "amount": str(donation.amount),
                "currency": donation.currency,
                "donor_name": donation.donor_name if not donation.is_anonymous else "Anonymous",
                "message": donation.message,
                "timestamp": donation.created_at.isoformat()
            }
            
            metrics.recent_donations.insert(0, donation_data)
            if len(metrics.recent_donations) > 10:
                metrics.recent_donations = metrics.recent_donations[:10]
                
            # Store metrics in Redis
            await self.redis.hset(
                f"donation_metrics:{stream_id}",
                mapping=asdict(metrics)
            )
            
        except Exception as e:
            logger.error(f"Failed to update donation metrics: {str(e)}")
            
    async def _update_refund_metrics(self, stream_id: str, refund_amount: Decimal):
        """Update metrics after refund"""
        try:
            metrics = self.metrics_cache.get(stream_id)
            if metrics:
                metrics.total_donations -= refund_amount
                metrics.total_count -= 1
                if metrics.total_count > 0:
                    metrics.average_donation = metrics.total_donations / metrics.total_count
                else:
                    metrics.average_donation = Decimal('0')
                    
        except Exception as e:
            logger.error(f"Failed to update refund metrics: {str(e)}")
            
    async def _trigger_donation_alert(self, donation: Donation):
        """Trigger donation alert for stream"""
        try:
            config = self.active_streams.get(donation.stream_id)
            if not config:
                return
                
            # Find matching alert configuration
            amount = Decimal(str(donation.amount))
            matching_alert = None
            
            for alert in config.alerts:
                if not alert.is_enabled:
                    continue
                    
                if amount >= alert.min_amount:
                    if alert.max_amount is None or amount <= alert.max_amount:
                        matching_alert = alert
                        break
                        
            if not matching_alert:
                return
                
            # Format alert message
            message = matching_alert.message_template.format(
                donor_name=donation.donor_name if not donation.is_anonymous else "Anonymous",
                amount=donation.amount,
                currency=donation.currency,
                message=donation.message or ""
            )
            
            # Create alert data
            alert_data = {
                "type": "donation_alert",
                "alert_id": matching_alert.alert_id,
                "alert_type": matching_alert.alert_type.value,
                "message": message,
                "amount": str(donation.amount),
                "currency": donation.currency,
                "donor_name": donation.donor_name if not donation.is_anonymous else "Anonymous",
                "duration_seconds": matching_alert.duration_seconds,
                "sound_file": matching_alert.sound_file,
                "animation_name": matching_alert.animation_name,
                "text_color": matching_alert.text_color,
                "background_color": matching_alert.background_color,
                "font_size": matching_alert.font_size,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Publish alert
            await self.redis.publish(
                f"donation_alerts:{donation.stream_id}",
                json.dumps(alert_data)
            )
            
            logger.info(f"Donation alert triggered for stream {donation.stream_id}: ${donation.amount}")
            
        except Exception as e:
            logger.error(f"Failed to trigger donation alert: {str(e)}")
            
    async def _send_webhook_notifications(self, donation: Donation):
        """Send webhook notifications to external services"""
        try:
            # This would send webhooks to configured endpoints
            webhook_data = {
                "event": "donation.completed",
                "donation_id": str(donation.id),
                "stream_id": donation.stream_id,
                "amount": str(donation.amount),
                "currency": donation.currency,
                "donor_name": donation.donor_name if not donation.is_anonymous else "Anonymous",
                "message": donation.message,
                "timestamp": donation.processed_at.isoformat()
            }
            
            logger.info(f"Webhook notification prepared for donation {donation.id}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notifications: {str(e)}")
            
    async def _verify_webhook_signature(
        self,
        processor: str,
        signature: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Verify webhook signature"""
        try:
            secret = self.webhook_secrets.get(processor)
            if not secret:
                return False
                
            # Mock signature verification
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {str(e)}")
            return False
            
    async def _handle_stripe_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook"""
        try:
            event_type = payload.get("type")
            
            if event_type == "payment_intent.succeeded":
                # Handle successful payment
                payment_intent = payload.get("data", {}).get("object", {})
                transaction_id = payment_intent.get("metadata", {}).get("transaction_id")
                
                if transaction_id:
                    donation = self.db.query(Donation).filter(
                        Donation.transaction_id == transaction_id
                    ).first()
                    
                    if donation:
                        await self.complete_donation(str(donation.id))
                        
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to handle Stripe webhook: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _handle_paypal_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PayPal webhook"""
        try:
            event_type = payload.get("event_type")
            
            if event_type == "PAYMENT.CAPTURE.COMPLETED":
                # Handle successful payment
                resource = payload.get("resource", {})
                custom_id = resource.get("custom_id")
                
                if custom_id:
                    donation = self.db.query(Donation).filter(
                        Donation.transaction_id == custom_id
                    ).first()
                    
                    if donation:
                        await self.complete_donation(str(donation.id))
                        
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to handle PayPal webhook: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _metrics_updater(self):
        """Background task to update metrics"""
        while self.is_running:
            try:
                for stream_id in self.active_streams.keys():
                    await self.get_donation_metrics(stream_id)
                    
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in metrics updater: {str(e)}")
                await asyncio.sleep(60)
                
    async def _goal_monitor(self):
        """Background task to monitor goal progress"""
        while self.is_running:
            try:
                # Check for expired goals
                expired_goals = self.db.query(DonationGoalRecord).filter(
                    DonationGoalRecord.is_active == True,
                    DonationGoalRecord.deadline < datetime.now(timezone.utc)
                ).all()
                
                for goal in expired_goals:
                    goal.is_active = False
                    goal.updated_at = datetime.now(timezone.utc)
                    
                self.db.commit()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in goal monitor: {str(e)}")
                await asyncio.sleep(600)
                
    async def _payment_processor(self):
        """Background task to process donation queue"""
        while self.is_running:
            try:
                # Process pending donations from queue
                donation_data = await self.redis.brpop("donation_processing_queue", timeout=1)
                
                if donation_data:
                    _, data_json = donation_data
                    data = json.loads(data_json)
                    
                    # Complete the donation
                    await self.complete_donation(data["donation_id"])
                    
            except Exception as e:
                logger.error(f"Error in payment processor: {str(e)}")
                await asyncio.sleep(5)


# Factory function for easy integration
def create_donation_handler(redis_client: Any, db_session: Session) -> DonationHandler:
    """Create and return a configured DonationHandler instance"""
    return DonationHandler(redis_client, db_session)