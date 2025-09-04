"""Affiliate Service - Module d'Affiliation Professional
================================================================

Comprehensive affiliate management system providing partner programs,
commission tracking, and automatic payment processing for the IA Influencer Agent platform.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/affiliate.py

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

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import asyncio

# Define our own data models to avoid dependency issues
class AffiliateStatus(str, Enum):
    """Statut du compte affilié"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"
    BANNED = "banned"


class CommissionStatus(str, Enum):
    """Statut des commissions"""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    HOLD = "hold"


class PayoutMethod(str, Enum):
    """Méthodes de paiement disponibles"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CHECK = "check"
    CRYPTOCURRENCY = "cryptocurrency"
    WISE = "wise"


@dataclass
class Affiliate:
    """Informations sur le partenaire affilié"""
    affiliate_id: str
    user_id: str
    name: str
    email: str
    status: AffiliateStatus
    commission_rule_id: str
    referral_code: str
    total_earnings: Decimal = Decimal("0")
    total_referrals: int = 0
    conversion_rate: float = 0.0
    payout_method: PayoutMethod = PayoutMethod.PAYPAL
    payout_details: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert affiliate to dictionary"""
        return {
            "affiliate_id": self.affiliate_id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "status": self.status.value,
            "commission_rule_id": self.commission_rule_id,
            "referral_code": self.referral_code,
            "total_earnings": float(self.total_earnings),
            "total_referrals": self.total_referrals,
            "conversion_rate": self.conversion_rate,
            "payout_method": self.payout_method.value,
            "payout_details": self.payout_details,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Commission:
    """Enregistrement de commission individuel"""
    commission_id: str
    affiliate_id: str
    transaction_id: str
    amount: Decimal
    commission_amount: Decimal
    rule_id: str
    status: CommissionStatus = CommissionStatus.PENDING
    reference_type: str = "sale"
    reference_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert commission to dictionary"""
        return {
            "commission_id": self.commission_id,
            "affiliate_id": self.affiliate_id,
            "transaction_id": self.transaction_id,
            "amount": float(self.amount),
            "commission_amount": float(self.commission_amount),
            "rule_id": self.rule_id,
            "status": self.status.value,
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "metadata": self.metadata,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PayoutBatch:
    """Traitement des paiements par lot"""
    batch_id: str
    total_amount: Decimal
    commission_count: int
    status: str = "pending"
    commission_ids: List[str] = field(default_factory=list)
    payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."


class ProgramType(str, Enum):
    """Types de programmes partenaires"""
    BASIC_AFFILIATE = "basic_affiliate"
    PREMIUM_PARTNER = "premium_partner"
    BRAND_AMBASSADOR = "brand_ambassador"
    INFLUENCER_NETWORK = "influencer_network"
    ENTERPRISE_PARTNER = "enterprise_partner"


class TrackingEventType(str, Enum):
    """Types d'événements de tracking"""
    REGISTRATION = "registration"
    FIRST_PURCHASE = "first_purchase"
    SUBSCRIPTION = "subscription"
    REFERRAL_CLICK = "referral_click"
    COMMISSION_EARNED = "commission_earned"
    PAYOUT_PROCESSED = "payout_processed"


@dataclass
class PartnerProgram:
    """Programme partenaire configuration"""
    program_id: str
    program_type: ProgramType
    name: str
    description: str
    commission_rate: Decimal
    minimum_payout: Decimal = Decimal("50.00")
    payment_schedule: int = 30  # jours
    requirements: Dict[str, Any] = field(default_factory=dict)
    benefits: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrackingEvent:
    """Événement de tracking des commissions"""
    event_id: str
    affiliate_id: str
    event_type: TrackingEventType
    amount: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    reference_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PaymentSchedule:
    """Planning des paiements automatiques"""
    schedule_id: str
    affiliate_id: str
    next_payment_date: datetime
    payment_amount: Decimal
    payment_method: PayoutMethod
    frequency: str = "monthly"  # monthly, weekly, bi-weekly
    auto_payment_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class AffiliateService:
    """
    Service principal de gestion des affiliés
    Handles partner programs, commission tracking, and automatic payments
    """
    
    def __init__(self):
        """Initialize affiliate service"""
        self.affiliates: Dict[str, Affiliate] = {}
        self.commissions: Dict[str, Commission] = {}
        self.payout_batches: Dict[str, PayoutBatch] = {}
        self.partner_programs: Dict[str, PartnerProgram] = {}
        self.tracking_events: List[TrackingEvent] = []
        self.payment_schedules: Dict[str, PaymentSchedule] = {}
        self.min_payout_amount = Decimal("50.00")
        self.is_initialized = False
        
        logger.info("🤝 Affiliate Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize service and dependencies"""
        try:
            # Create default partner programs
            await self._create_default_programs()
            
            self.is_initialized = True
            logger.info("✅ Affiliate Service fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Affiliate Service initialization failed: {e}")
            return False
    
    # ==========================================
    # PROGRAMME PARTENAIRES (Partner Programs)
    # ==========================================
    
    async def create_partner_program(
        self,
        program_type: ProgramType,
        name: str,
        description: str,
        commission_rate: Decimal,
        minimum_payout: Decimal = Decimal("50.00"),
        requirements: Dict[str, Any] = None,
        benefits: List[str] = None
    ) -> Optional[PartnerProgram]:
        """Créer un nouveau programme partenaire"""
        try:
            program_id = str(uuid.uuid4())
            
            program = PartnerProgram(
                program_id=program_id,
                program_type=program_type,
                name=name,
                description=description,
                commission_rate=commission_rate,
                minimum_payout=minimum_payout,
                requirements=requirements or {},
                benefits=benefits or []
            )
            
            self.partner_programs[program_id] = program
            
            logger.info(f"🎯 Partner program created: {name} ({program_type.value})")
            return program
            
        except Exception as e:
            logger.error(f"❌ Failed to create partner program: {e}")
            return None
    
    async def register_affiliate_to_program(
        self,
        user_id: str,
        name: str,
        email: str,
        program_id: str
    ) -> Optional[Affiliate]:
        """Inscrire un affilié à un programme"""
        try:
            program = self.partner_programs.get(program_id)
            if not program:
                logger.error(f"Program not found: {program_id}")
                return None
            
            # Check program requirements
            if not await self._check_program_requirements(user_id, program):
                logger.warning(f"User {user_id} does not meet program requirements")
                return None
            
            # Generate unique affiliate ID and referral code
            affiliate_id = str(uuid.uuid4())
            referral_code = self._generate_referral_code(name)
            
            # Create affiliate
            affiliate = Affiliate(
                affiliate_id=affiliate_id,
                user_id=user_id,
                name=name,
                email=email,
                status=AffiliateStatus.PENDING_APPROVAL,
                commission_rule_id=program_id,
                referral_code=referral_code
            )
            
            self.affiliates[affiliate_id] = affiliate
            
            # Track registration event
            await self._track_event(
                affiliate_id,
                TrackingEventType.REGISTRATION,
                metadata={"program_id": program_id}
            )
            
            logger.info(f"✅ Affiliate registered to program: {name} -> {program.name}")
            return affiliate
            
        except Exception as e:
            logger.error(f"❌ Failed to register affiliate: {e}")
            return None
    
    async def get_partner_programs(
        self,
        active_only: bool = True
    ) -> List[PartnerProgram]:
        """Obtenir la liste des programmes partenaires"""
        programs = list(self.partner_programs.values())
        
        if active_only:
            programs = [p for p in programs if p.is_active]
        
        return programs
    
    async def get_program_stats(self, program_id: str) -> Dict[str, Any]:
        """Obtenir les statistiques d'un programme"""
        program = self.partner_programs.get(program_id)
        if not program:
            return {}
        
        try:
            # Count affiliates in this program
            affiliate_count = len([
                a for a in self.affiliates.values()
                if a.commission_rule_id == program_id
            ])
            
            # Calculate total commissions
            total_commissions = sum([
                c.commission_amount for c in self.commissions.values()
                if self.affiliates.get(c.affiliate_id, {}).commission_rule_id == program_id
            ], Decimal("0"))
            
            return {
                "program_id": program_id,
                "program_name": program.name,
                "affiliate_count": affiliate_count,
                "total_commissions": float(total_commissions),
                "commission_rate": float(program.commission_rate),
                "active": program.is_active
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get program stats: {e}")
            return {}
    
    # ==========================================
    # TRACKING COMMISSIONS
    # ==========================================
    
    async def track_commission_event(
        self,
        affiliate_id: str,
        transaction_id: str,
        amount: Decimal,
        reference_type: str = "sale",
        reference_id: str = "",
        metadata: Dict[str, Any] = None
    ) -> Optional[Commission]:
        """Tracker un événement de commission"""
        try:
            affiliate = self.affiliates.get(affiliate_id)
            if not affiliate:
                logger.error(f"Affiliate not found: {affiliate_id}")
                return None
            
            # Get program to calculate commission
            program = self.partner_programs.get(affiliate.commission_rule_id)
            if not program:
                logger.error(f"Program not found: {affiliate.commission_rule_id}")
                return None
            
            # Calculate commission amount
            commission_amount = (amount * program.commission_rate / Decimal("100")).quantize(
                Decimal("0.01")
            )
            
            # Create commission record
            commission_id = str(uuid.uuid4())
            commission = Commission(
                commission_id=commission_id,
                affiliate_id=affiliate_id,
                transaction_id=transaction_id,
                amount=amount,
                commission_amount=commission_amount,
                rule_id=affiliate.commission_rule_id,
                status=CommissionStatus.PENDING,
                reference_type=reference_type,
                reference_id=reference_id,
                metadata=metadata or {}
            )
            
            self.commissions[commission_id] = commission
            
            # Update affiliate totals
            affiliate.total_earnings += commission_amount
            affiliate.total_referrals += 1
            affiliate.updated_at = datetime.utcnow()
            
            # Track the commission event
            await self._track_event(
                affiliate_id,
                TrackingEventType.COMMISSION_EARNED,
                amount=amount,
                commission_amount=commission_amount,
                reference_id=transaction_id,
                metadata=metadata or {}
            )
            
            logger.info(f"📈 Commission tracked: {commission_amount} for affiliate {affiliate_id}")
            return commission
            
        except Exception as e:
            logger.error(f"❌ Failed to track commission: {e}")
            return None
    
    async def get_affiliate_commissions(
        self,
        affiliate_id: str,
        status: Optional[CommissionStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Commission]:
        """Obtenir les commissions d'un affilié"""
        try:
            # Get all commissions for the affiliate
            commissions = [
                c for c in self.commissions.values()
                if c.affiliate_id == affiliate_id
            ]
            
            # Filter by status if provided
            if status:
                commissions = [c for c in commissions if c.status == status]
            
            # Filter by date range if provided
            if date_from:
                commissions = [c for c in commissions if c.created_at >= date_from]
            if date_to:
                commissions = [c for c in commissions if c.created_at <= date_to]
            
            return commissions
            
        except Exception as e:
            logger.error(f"❌ Failed to get affiliate commissions: {e}")
            return []
    
    async def get_commission_analytics(
        self,
        affiliate_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Obtenir les analytics des commissions"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get commissions for the period
            if affiliate_id:
                commissions = await self.get_affiliate_commissions(
                    affiliate_id=affiliate_id,
                    date_from=start_date,
                    date_to=end_date
                )
            else:
                commissions = [
                    c for c in self.commissions.values()
                    if start_date <= c.created_at <= end_date
                ]
            
            # Calculate analytics
            total_commissions = sum([c.commission_amount for c in commissions], Decimal("0"))
            total_transactions = len(commissions)
            average_commission = total_commissions / total_transactions if total_transactions > 0 else Decimal("0")
            
            # Commission by status
            status_breakdown = {}
            for status in CommissionStatus:
                count = len([c for c in commissions if c.status == status])
                status_breakdown[status.value] = count
            
            return {
                "period_days": period_days,
                "total_commissions": float(total_commissions),
                "total_transactions": total_transactions,
                "average_commission": float(average_commission),
                "status_breakdown": status_breakdown,
                "affiliate_id": affiliate_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get commission analytics: {e}")
            return {}
    
    # ==========================================
    # PAIEMENTS AUTOMATIQUES (Automatic Payments)
    # ==========================================
    
    async def setup_automatic_payments(
        self,
        affiliate_id: str,
        payment_method: PayoutMethod,
        frequency: str = "monthly",
        minimum_amount: Decimal = Decimal("50.00")
    ) -> Optional[PaymentSchedule]:
        """Configurer les paiements automatiques"""
        try:
            schedule_id = str(uuid.uuid4())
            
            # Calculate next payment date based on frequency
            next_payment_date = self._calculate_next_payment_date(frequency)
            
            schedule = PaymentSchedule(
                schedule_id=schedule_id,
                affiliate_id=affiliate_id,
                next_payment_date=next_payment_date,
                payment_amount=minimum_amount,
                payment_method=payment_method,
                frequency=frequency,
                auto_payment_enabled=True
            )
            
            self.payment_schedules[schedule_id] = schedule
            
            logger.info(f"⚡ Automatic payments configured for affiliate {affiliate_id}")
            return schedule
            
        except Exception as e:
            logger.error(f"❌ Failed to setup automatic payments: {e}")
            return None
    
    async def process_automatic_payments(self) -> Dict[str, Any]:
        """Traiter les paiements automatiques programmés"""
        processed_count = 0
        failed_count = 0
        current_time = datetime.utcnow()
        
        try:
            for schedule in self.payment_schedules.values():
                if not schedule.auto_payment_enabled:
                    continue
                
                # Check if payment is due
                if current_time >= schedule.next_payment_date:
                    try:
                        # Get pending commissions for affiliate
                        eligible_commissions = await self.get_affiliate_commissions(
                            affiliate_id=schedule.affiliate_id,
                            status=CommissionStatus.APPROVED
                        )
                        
                        # Calculate total amount
                        total_amount = sum([c.commission_amount for c in eligible_commissions], Decimal("0"))
                        
                        if total_amount >= schedule.payment_amount:
                            # Create payout batch
                            batch_id = str(uuid.uuid4())
                            payout_batch = PayoutBatch(
                                batch_id=batch_id,
                                total_amount=total_amount,
                                commission_count=len(eligible_commissions),
                                status="processed",
                                commission_ids=[c.commission_id for c in eligible_commissions],
                                payout_method=schedule.payment_method,
                                processed_at=current_time
                            )
                            
                            self.payout_batches[batch_id] = payout_batch
                            
                            # Mark commissions as paid
                            for commission in eligible_commissions:
                                commission.status = CommissionStatus.PAID
                                commission.paid_at = current_time
                            
                            # Track payment event
                            await self._track_event(
                                schedule.affiliate_id,
                                TrackingEventType.PAYOUT_PROCESSED,
                                amount=total_amount,
                                reference_id=batch_id
                            )
                            
                            # Update next payment date
                            schedule.next_payment_date = self._calculate_next_payment_date(
                                schedule.frequency
                            )
                            
                            processed_count += 1
                            logger.info(f"💸 Automatic payment processed: {total_amount} for affiliate {schedule.affiliate_id}")
                    
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"❌ Failed to process payment for affiliate {schedule.affiliate_id}: {e}")
            
            logger.info(f"🔄 Automatic payments processing completed: {processed_count} processed, {failed_count} failed")
            
            return {
                "processed": processed_count,
                "failed": failed_count,
                "total_schedules": len(self.payment_schedules)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process automatic payments: {e}")
            return {"processed": 0, "failed": 0}
    
    async def get_payment_schedule(self, affiliate_id: str) -> Optional[PaymentSchedule]:
        """Obtenir le planning de paiement d'un affilié"""
        for schedule in self.payment_schedules.values():
            if schedule.affiliate_id == affiliate_id:
                return schedule
        return None
    
    async def update_payment_schedule(
        self,
        affiliate_id: str,
        payment_method: Optional[PayoutMethod] = None,
        frequency: Optional[str] = None,
        auto_payment_enabled: Optional[bool] = None
    ) -> bool:
        """Mettre à jour le planning de paiement"""
        try:
            schedule = await self.get_payment_schedule(affiliate_id)
            if not schedule:
                return False
            
            if payment_method:
                schedule.payment_method = payment_method
            if frequency:
                schedule.frequency = frequency
                schedule.next_payment_date = self._calculate_next_payment_date(frequency)
            if auto_payment_enabled is not None:
                schedule.auto_payment_enabled = auto_payment_enabled
            
            logger.info(f"📅 Payment schedule updated for affiliate {affiliate_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update payment schedule: {e}")
            return False
    
    # ==========================================
    # MÉTHODES UTILITAIRES (Utility Methods)
    # ==========================================
    
    async def _create_default_programs(self):
        """Créer les programmes partenaires par défaut"""
        default_programs = [
            {
                "type": ProgramType.BASIC_AFFILIATE,
                "name": "Programme Affilié Basique",
                "description": "Programme d'entrée pour nouveaux affiliés",
                "commission_rate": Decimal("3.0"),
                "requirements": {"min_followers": 1000}
            },
            {
                "type": ProgramType.PREMIUM_PARTNER,
                "name": "Partenaire Premium",
                "description": "Programme avancé pour partenaires expérimentés",
                "commission_rate": Decimal("5.0"),
                "requirements": {"min_followers": 10000, "min_engagement": 0.03}
            },
            {
                "type": ProgramType.BRAND_AMBASSADOR,
                "name": "Ambassadeur de Marque",
                "description": "Programme exclusif pour ambassadeurs",
                "commission_rate": Decimal("8.0"),
                "requirements": {"min_followers": 50000, "brand_alignment": True}
            }
        ]
        
        for program_data in default_programs:
            await self.create_partner_program(**program_data)
    
    def _generate_referral_code(self, name: str) -> str:
        """Générer un code de parrainage unique"""
        # Create a simple referral code based on name and timestamp
        clean_name = ''.join(c for c in name.upper() if c.isalnum())[:6]
        timestamp_part = str(int(datetime.utcnow().timestamp()))[-4:]
        return f"{clean_name}{timestamp_part}"
    
    async def _check_program_requirements(
        self,
        user_id: str,
        program: PartnerProgram
    ) -> bool:
        """Vérifier les exigences du programme"""
        # Placeholder for requirement checking logic
        # This would typically check user metrics, social media stats, etc.
        return True
    
    async def _track_event(
        self,
        affiliate_id: str,
        event_type: TrackingEventType,
        amount: Optional[Decimal] = None,
        commission_amount: Optional[Decimal] = None,
        reference_id: str = "",
        metadata: Dict[str, Any] = None
    ):
        """Tracker un événement"""
        try:
            event = TrackingEvent(
                event_id=str(uuid.uuid4()),
                affiliate_id=affiliate_id,
                event_type=event_type,
                amount=amount,
                commission_amount=commission_amount,
                reference_id=reference_id,
                metadata=metadata or {}
            )
            
            self.tracking_events.append(event)
            logger.debug(f"📊 Event tracked: {event_type.value} for affiliate {affiliate_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to track event: {e}")
    
    def _calculate_next_payment_date(self, frequency: str) -> datetime:
        """Calculer la prochaine date de paiement"""
        current_time = datetime.utcnow()
        
        if frequency == "weekly":
            return current_time + timedelta(weeks=1)
        elif frequency == "bi-weekly":
            return current_time + timedelta(weeks=2)
        elif frequency == "monthly":
            return current_time + timedelta(days=30)
        else:
            return current_time + timedelta(days=30)  # Default to monthly
    
    # ==========================================
    # MÉTHODES ADDITIONNELLES (Additional Methods)
    # ==========================================
    
    async def approve_affiliate(self, affiliate_id: str) -> bool:
        """Approuver un affilié"""
        try:
            affiliate = self.affiliates.get(affiliate_id)
            if not affiliate:
                return False
            
            affiliate.status = AffiliateStatus.ACTIVE
            affiliate.updated_at = datetime.utcnow()
            
            logger.info(f"✅ Affiliate approved: {affiliate_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to approve affiliate: {e}")
            return False
    
    async def get_affiliate(self, affiliate_id: str) -> Optional[Affiliate]:
        """Obtenir un affilié par ID"""
        return self.affiliates.get(affiliate_id)
    
    async def get_affiliate_by_referral_code(self, referral_code: str) -> Optional[Affiliate]:
        """Obtenir un affilié par code de parrainage"""
        for affiliate in self.affiliates.values():
            if affiliate.referral_code == referral_code:
                return affiliate
        return None
    
    async def list_affiliates(
        self,
        status: Optional[AffiliateStatus] = None,
        program_id: Optional[str] = None
    ) -> List[Affiliate]:
        """Lister les affiliés avec filtres optionnels"""
        affiliates = list(self.affiliates.values())
        
        if status:
            affiliates = [a for a in affiliates if a.status == status]
        
        if program_id:
            affiliates = [a for a in affiliates if a.commission_rule_id == program_id]
        
        return affiliates
    
    async def approve_commission(self, commission_id: str) -> bool:
        """Approuver une commission"""
        try:
            commission = self.commissions.get(commission_id)
            if not commission:
                return False
            
            commission.status = CommissionStatus.APPROVED
            commission.approved_at = datetime.utcnow()
            
            logger.info(f"✅ Commission approved: {commission_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to approve commission: {e}")
            return False
    
    async def get_payout_batches(
        self,
        affiliate_id: Optional[str] = None
    ) -> List[PayoutBatch]:
        """Obtenir les lots de paiement"""
        batches = list(self.payout_batches.values())
        
        if affiliate_id:
            # Filter batches that contain commissions for this affiliate
            affiliate_batches = []
            for batch in batches:
                for commission_id in batch.commission_ids:
                    commission = self.commissions.get(commission_id)
                    if commission and commission.affiliate_id == affiliate_id:
                        affiliate_batches.append(batch)
                        break
            return affiliate_batches
        
        return batches
    
    async def get_affiliate_dashboard(self, affiliate_id: str) -> Dict[str, Any]:
        """Obtenir le tableau de bord de l'affilié"""
        try:
            # Get affiliate info
            affiliate = self.affiliates.get(affiliate_id)
            if not affiliate:
                return {}
            
            # Get commissions analytics
            analytics = await self.get_commission_analytics(affiliate_id=affiliate_id)
            
            # Get payment schedule
            payment_schedule = await self.get_payment_schedule(affiliate_id)
            
            # Get recent commissions
            recent_commissions = await self.get_affiliate_commissions(
                affiliate_id=affiliate_id,
                date_from=datetime.utcnow() - timedelta(days=30)
            )
            
            return {
                "affiliate": affiliate.to_dict(),
                "analytics": analytics,
                "payment_schedule": {
                    "next_payment_date": payment_schedule.next_payment_date.isoformat() if payment_schedule else None,
                    "frequency": payment_schedule.frequency if payment_schedule else None,
                    "auto_payment_enabled": payment_schedule.auto_payment_enabled if payment_schedule else False
                },
                "recent_commissions": [c.to_dict() for c in recent_commissions[-10:]],  # Last 10
                "total_recent_commissions": len(recent_commissions)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get affiliate dashboard: {e}")
            return {}


# Global service instance
affiliate_service = AffiliateService()


# Export main classes and service
__all__ = [
    "AffiliateService",
    "PartnerProgram", 
    "TrackingEvent",
    "PaymentSchedule",
    "ProgramType",
    "TrackingEventType",
    "affiliate_service"
]

logger.info(f"🤝 Affiliate Service v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")