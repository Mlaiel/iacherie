"""Commission Management System

Système de gestion avancé des commissions avec calculs automatisés,
distribution intelligente et tracking des affiliations pour la plateforme IA Influencer Agent.

Architecture: Multi-tier commission tracking with smart contract integration
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe Projet: Lead AI Developer + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code et concept sont la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Violation = Poursuites judiciaires selon le droit allemand et international.
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
import logging
from dataclasses import dataclass, field
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.security import EncryptionService
from ...utils.financial import CurrencyConverter, TaxCalculator
from ...utils.validation import ValidationService
from ...core.cache import CacheManager
from ...core.events import EventEmitter

logger = logging.getLogger(__name__)

Base = declarative_base()


class CommissionType(Enum):
    """Types de commissions"""    AFFILIATE_REFERRAL = "affiliate_referral"
    COLLABORATION_SPLIT = "collaboration_split"
    PLATFORM_COMMISSION = "platform_commission"
    CREATOR_ROYALTY = "creator_royalty"
    MANAGER_COMMISSION = "manager_commission"
    LABEL_COMMISSION = "label_commission"
    DISTRIBUTOR_FEE = "distributor_fee"
    LICENSING_ROYALTY = "licensing_royalty"
    STREAMING_ROYALTY = "streaming_royalty"
    MERCHANDISE_COMMISSION = "merchandise_commission"


class CommissionStatus(Enum):
    """Status des commissions"""    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    DISPUTED = "disputed"
    REVERSED = "reversed"
    EXPIRED = "expired"


class CommissionTier(Enum):
    """Niveaux de commission"""    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    CUSTOM = "custom"


@dataclass
class CommissionRuleModel(BaseModel, TimestampMixin):
    """    Modèle des règles de commission
    """    __tablename__ = "commission_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(255), nullable=False, index=True)
    rule_description = Column(Text, nullable=True)
    
    # Configuration de la commission
    commission_type = Column(String(50), nullable=False)
    commission_tier = Column(String(20), nullable=False, default="bronze")
    
    # Calcul des pourcentages
    base_percentage = Column(Numeric(5, 4), nullable=False)
    minimum_amount = Column(Numeric(15, 4), nullable=True)
    maximum_amount = Column(Numeric(15, 4), nullable=True)
    
    # Conditions d'application
    revenue_threshold = Column(Numeric(15, 4), nullable=True)
    performance_multiplier = Column(Numeric(3, 2), nullable=False, default=1.0)
    
    # Métadonnées
    applicable_platforms = Column(ARRAY(String), nullable=True)
    content_types = Column(ARRAY(String), nullable=True)
    geographic_restrictions = Column(JSONB, nullable=True)
    
    # Validité
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relations
    commissions = relationship("CommissionRecordModel", back_populates="rule")


@dataclass
class CommissionRecordModel(BaseModel, TimestampMixin):
    """    Modèle des enregistrements de commission
    """    __tablename__ = "commission_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commission_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants liés
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"), nullable=False, index=True)
    commission_rule_id = Column(UUID(as_uuid=True), ForeignKey("commission_rules.id"), nullable=False, index=True)
    recipient_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    originator_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Détails financiers
    base_amount = Column(Numeric(15, 4), nullable=False)
    commission_percentage = Column(Numeric(5, 4), nullable=False)
    commission_amount = Column(Numeric(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Calculs et ajustements
    performance_bonus = Column(Numeric(15, 4), nullable=False, default=0)
    tier_bonus = Column(Numeric(15, 4), nullable=False, default=0)
    tax_withholding = Column(Numeric(15, 4), nullable=False, default=0)
    net_commission = Column(Numeric(15, 4), nullable=False)
    
    # Status et métadonnées
    commission_status = Column(String(20), nullable=False, default="pending")
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    payment_due_date = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    
    # Informations additionnelles
    platform_source = Column(String(100), nullable=False)
    content_type = Column(String(50), nullable=True)
    geographic_region = Column(String(10), nullable=True)
    
    # Métadonnées de calcul
    calculation_metadata = Column(JSONB, nullable=True)
    audit_trail = Column(JSONB, nullable=True)
    
    # Relations
    rule = relationship("CommissionRuleModel", back_populates="commissions")
    revenue_record = relationship("RevenueRecordModel")


@dataclass
class AffiliateTrackingModel(BaseModel, TimestampMixin):
    """    Modèle de suivi des affiliés
    """    __tablename__ = "affiliate_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants
    affiliate_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    referrer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Tracking des performances
    total_referrals = Column(Integer, nullable=False, default=0)
    successful_conversions = Column(Integer, nullable=False, default=0)
    total_revenue_generated = Column(Numeric(15, 4), nullable=False, default=0)
    total_commissions_earned = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Métriques de performance
    conversion_rate = Column(Numeric(5, 4), nullable=False, default=0)
    average_order_value = Column(Numeric(15, 4), nullable=False, default=0)
    lifetime_value = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Configuration
    commission_tier = Column(String(20), nullable=False, default="bronze")
    custom_commission_rate = Column(Numeric(5, 4), nullable=True)
    minimum_payout_threshold = Column(Numeric(15, 4), nullable=False, default=25.0)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    last_activity_date = Column(DateTime, nullable=True)
    tier_upgrade_date = Column(DateTime, nullable=True)
    
    # Métadonnées
    tracking_metadata = Column(JSONB, nullable=True)
    performance_history = Column(JSONB, nullable=True)


class CommissionCalculatorEngine:
    """    Moteur de calcul avancé des commissions
    """    
    def __init__(self, db_session: Session, cache_manager: CacheManager):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.currency_converter = CurrencyConverter()
        self.tax_calculator = TaxCalculator()
        self.event_emitter = EventEmitter()
        
    async def calculate_commission(
        self,
        revenue_record_id: uuid.UUID,
        commission_rule_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> CommissionRecordModel:
        """        Calcule une commission basée sur les règles définies
        """        try:
            # Récupération des données
            revenue_record = await self._get_revenue_record(revenue_record_id)
            commission_rule = await self._get_commission_rule(commission_rule_id)
            
            # Validation de l'éligibilité
            await self._validate_commission_eligibility(
                revenue_record, commission_rule, recipient_user_id
            )
            
            # Calcul de base
            base_amount = revenue_record.amount_net
            commission_percentage = await self._calculate_dynamic_percentage(
                commission_rule, revenue_record, additional_context
            )
            
            # Calcul des bonus
            performance_bonus = await self._calculate_performance_bonus(
                recipient_user_id, revenue_record
            )
            tier_bonus = await self._calculate_tier_bonus(
                recipient_user_id, commission_rule
            )
            
            # Calcul de la commission brute
            commission_amount = (base_amount * commission_percentage / 100)
            total_commission = commission_amount + performance_bonus + tier_bonus
            
            # Calcul des taxes
            tax_withholding = await self._calculate_tax_withholding(
                recipient_user_id, total_commission, revenue_record
            )
            
            net_commission = total_commission - tax_withholding
            
            # Création de l'enregistrement
            commission_record = CommissionRecordModel(
                commission_id=f"COM_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
                revenue_record_id=revenue_record_id,
                commission_rule_id=commission_rule_id,
                recipient_user_id=recipient_user_id,
                base_amount=base_amount,
                commission_percentage=commission_percentage,
                commission_amount=commission_amount,
                performance_bonus=performance_bonus,
                tier_bonus=tier_bonus,
                tax_withholding=tax_withholding,
                net_commission=net_commission,
                currency=revenue_record.currency,
                platform_source=revenue_record.platform_name,
                calculation_metadata={
                    "calculation_method": "advanced_ai_optimized",
                    "factors_considered": {
                        "performance_multiplier": commission_rule.performance_multiplier,
                        "revenue_threshold": commission_rule.revenue_threshold,
                        "geographic_region": revenue_record.geographic_region
                    },
                    "calculation_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Sauvegarde
            self.db_session.add(commission_record)
            await self.db_session.commit()
            
            # Émission d'événement
            await self.event_emitter.emit("commission_calculated", {
                "commission_id": commission_record.commission_id,
                "amount": float(net_commission),
                "recipient_id": str(recipient_user_id)
            })
            
            logger.info(f"Commission calculated: {commission_record.commission_id}")
            return commission_record
            
        except Exception as e:
            logger.error(f"Commission calculation failed: {e}")
            await self.db_session.rollback()
            raise
    
    async def _calculate_dynamic_percentage(
        self,
        commission_rule: CommissionRuleModel,
        revenue_record,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Decimal:
        """        Calcule le pourcentage de commission dynamique
        """        base_percentage = commission_rule.base_percentage
        
        # Ajustement basé sur les performances
        if commission_rule.performance_multiplier > 1.0:
            performance_adjustment = (commission_rule.performance_multiplier - 1.0) * base_percentage
            base_percentage += performance_adjustment
        
        # Ajustement basé sur le seuil de revenus
        if (commission_rule.revenue_threshold and 
            revenue_record.amount_net >= commission_rule.revenue_threshold):
            base_percentage *= Decimal('1.1')  # Bonus de 10%
        
        # Ajustement géographique
        if additional_context and "geographic_premium" in additional_context:
            geographic_multiplier = Decimal(str(additional_context["geographic_premium"]))
            base_percentage *= geographic_multiplier
        
        return base_percentage.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    async def _calculate_performance_bonus(
        self,
        recipient_user_id: uuid.UUID,
        revenue_record
    ) -> Decimal:
        """        Calcule le bonus de performance
        """        # Récupération des métriques de performance
        performance_data = await self._get_user_performance_metrics(recipient_user_id)
        
        if not performance_data:
            return Decimal('0')
        
        # Calcul du bonus basé sur les métriques
        conversion_rate = performance_data.get('conversion_rate', 0)
        revenue_growth = performance_data.get('revenue_growth', 0)
        
        bonus_percentage = Decimal('0')
        
        if conversion_rate > 0.05:  # 5%
            bonus_percentage += Decimal('0.5')  # 0.5%
        if conversion_rate > 0.10:  # 10%
            bonus_percentage += Decimal('0.5')  # +0.5% total 1%
        
        if revenue_growth > 0.20:  # 20% de croissance
            bonus_percentage += Decimal('1.0')  # +1%
        
        bonus_amount = revenue_record.amount_net * bonus_percentage / 100
        return bonus_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_tier_bonus(
        self,
        recipient_user_id: uuid.UUID,
        commission_rule: CommissionRuleModel
    ) -> Decimal:
        """        Calcule le bonus de niveau
        """        affiliate_data = await self._get_affiliate_data(recipient_user_id)
        
        if not affiliate_data:
            return Decimal('0')
        
        tier = affiliate_data.commission_tier
        base_amount = commission_rule.base_percentage
        
        tier_multipliers = {
            'bronze': Decimal('0'),
            'silver': Decimal('0.25'),  # 25% bonus
            'gold': Decimal('0.50'),    # 50% bonus
            'platinum': Decimal('0.75'), # 75% bonus
            'diamond': Decimal('1.00'),  # 100% bonus
            'custom': affiliate_data.custom_commission_rate or Decimal('0')
        }
        
        tier_bonus_percentage = tier_multipliers.get(tier, Decimal('0'))
        tier_bonus = base_amount * tier_bonus_percentage / 100
        
        return tier_bonus.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class CommissionDistributionEngine:
    """    Moteur de distribution automatisée des commissions
    """    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.event_emitter = EventEmitter()
    
    async def process_pending_commissions(self) -> Dict[str, Any]:
        """        Traite toutes les commissions en attente
        """        pending_commissions = await self._get_pending_commissions()
        
        results = {
            'processed': 0,
            'failed': 0,
            'total_amount': Decimal('0'),
            'details': []
        }
        
        for commission in pending_commissions:
            try:
                await self._distribute_commission(commission)
                results['processed'] += 1
                results['total_amount'] += commission.net_commission
                results['details'].append({
                    'commission_id': commission.commission_id,
                    'amount': float(commission.net_commission),
                    'status': 'success'
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'commission_id': commission.commission_id,
                    'error': str(e),
                    'status': 'failed'
                })
                logger.error(f"Commission distribution failed: {commission.commission_id} - {e}")
        
        return results
    
    async def _distribute_commission(self, commission: CommissionRecordModel):
        """        Distribue une commission individuelle
        """        # Validation des fonds
        await self._validate_available_funds(commission)
        
        # Traitement du paiement
        payment_result = await self._process_payment(commission)
        
        if payment_result['success']:
            # Mise à jour du status
            commission.commission_status = CommissionStatus.PAID.value
            commission.payment_date = datetime.utcnow()
            
            # Mise à jour des métriques d'affilié
            await self._update_affiliate_metrics(commission)
            
            # Émission d'événement
            await self.event_emitter.emit("commission_paid", {
                "commission_id": commission.commission_id,
                "recipient_id": str(commission.recipient_user_id),
                "amount": float(commission.net_commission)
            })
            
        else:
            commission.commission_status = CommissionStatus.DISPUTED.value
            raise Exception(f"Payment failed: {payment_result['error']}")


class CommissionManager:
    """    Gestionnaire principal des commissions
    """    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_manager = CacheManager()
        self.calculator = CommissionCalculatorEngine(
            db_manager.get_session(), 
            self.cache_manager
        )
        self.distributor = CommissionDistributionEngine(db_manager.get_session())
    
    async def setup_commission_rule(
        self,
        rule_name: str,
        commission_type: CommissionType,
        base_percentage: Decimal,
        configuration: Dict[str, Any]
    ) -> CommissionRuleModel:
        """        Crée une nouvelle règle de commission
        """        rule = CommissionRuleModel(
            rule_name=rule_name,
            commission_type=commission_type.value,
            base_percentage=base_percentage,
            commission_tier=configuration.get('tier', 'bronze'),
            minimum_amount=configuration.get('minimum_amount'),
            maximum_amount=configuration.get('maximum_amount'),
            revenue_threshold=configuration.get('revenue_threshold'),
            performance_multiplier=Decimal(str(configuration.get('performance_multiplier', 1.0))),
            applicable_platforms=configuration.get('platforms'),
            content_types=configuration.get('content_types'),
            geographic_restrictions=configuration.get('geographic_restrictions'),
            expiration_date=configuration.get('expiration_date')
        )
        
        async with self.db_manager.get_session() as session:
            session.add(rule)
            await session.commit()
            
        logger.info(f"Commission rule created: {rule_name}")
        return rule
    
    async def calculate_and_distribute_commissions(
        self,
        revenue_record_id: uuid.UUID
    ) -> List[CommissionRecordModel]:
        """        Calcule et distribue automatiquement toutes les commissions applicables
        """        applicable_rules = await self._find_applicable_commission_rules(revenue_record_id)
        created_commissions = []
        
        for rule, recipient_id in applicable_rules:
            commission = await self.calculator.calculate_commission(
                revenue_record_id=revenue_record_id,
                commission_rule_id=rule.id,
                recipient_user_id=recipient_id
            )
            created_commissions.append(commission)
        
        # Distribution automatique
        distribution_results = await self.distributor.process_pending_commissions()
        
        logger.info(f"Commissions processed: {len(created_commissions)} created, "
                   f"{distribution_results['processed']} distributed")
        
        return created_commissions
    
    async def get_commission_analytics(
        self,
        user_id: Optional[uuid.UUID] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """        Génère des analyses complètes des commissions
        """        query_filters = {}
        
        if user_id:
            query_filters['recipient_user_id'] = user_id
        
        if date_range:
            query_filters['date_range'] = date_range
        
        analytics = await self._generate_commission_analytics(query_filters)
        return analytics
