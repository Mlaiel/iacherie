"""🚀 Split Payments System - IA Influencer Agent Platform Enterprise
=================================================================
Module: backend/platform_core/billing/split_payments.py
Author: Fahed Mlaiel (mlaiel@live.de)
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME PAIEMENTS SPLIT COLLABORATION CRÉATEURS
Gestion avancée des paiements partagés pour collaborations créateurs
- Split automatique revenus selon règles business définies
- Escrow management sécurisé pour projets collaboratifs
- Calcul intelligent pourcentages et commissions
- Gestion fiscale multi-créateurs et juridictions
- Tracking transparent et audit trails complets

Multi-Expert Implementation:
🧠 Lead Dev IA: Algorithmes distribution intelligente, optimisation splits, ML recommendations
🏗️ Backend Senior: Architecture haute performance, transactions atomiques, consistency
🤖 ML Engineer: Modèles prédiction collaboration success, revenue optimization
🗄️ DBA: Transactions ACID, audit trails, performance queries collaboratives
🔒 Security: Sécurisation escrow, protection fonds, audit compliance
🌐 Microservices: Intégration payment gateways, notification services
🎵 Audio: Splits spécifiques music industry, royalties, sync licensing
⚙️ DevOps: Monitoring transactions, alerting, automated reconciliation
💡 AI Prompt: Génération contrats intelligents, communication automatique
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import hashlib

# Configuration logging
logger = logging.getLogger(__name__)


class SplitType(Enum):
    """Types de split payments"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    HYBRID = "hybrid"
    ROYALTY = "royalty"


class CollaborationType(Enum):
    """Types de collaboration"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CREATION = "video_creation"
    PODCAST_SERIES = "podcast_series"
    CONTENT_LICENSING = "content_licensing"
    BRAND_PARTNERSHIP = "brand_partnership"
    COURSE_CREATION = "course_creation"
    LIVE_EVENT = "live_event"
    MERCHANDISE = "merchandise"


class SplitStatus(Enum):
    """États des splits"""
    PENDING = "pending"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class EscrowStatus(Enum):
    """États de l'escrow"""
    CREATED = "created"
    FUNDED = "funded"
    RELEASED = "released"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    EXPIRED = "expired"


@dataclass
class CreatorParticipant:
    """Participant créateur dans un split"""
    creator_id: str
    creator_name: str
    creator_email: str
    role: str
    percentage: Decimal
    fixed_amount: Optional[Decimal] = None
    minimum_payout: Decimal = Decimal('10.00')
    payment_method: str = "stripe"
    tax_id: Optional[str] = None
    country: str = "US"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SplitRule:
    """Règle de distribution des revenus"""
    rule_id: str
    name: str
    split_type: SplitType
    participants: List[CreatorParticipant]
    platform_fee: Decimal = Decimal('5.0')  # Pourcentage
    processing_fee: Decimal = Decimal('2.9')  # Pourcentage
    minimum_split_amount: Decimal = Decimal('1.00')
    auto_release_days: int = 7
    dispute_window_days: int = 30
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SplitTransaction:
    """Transaction de split payment"""
    split_id: str
    original_transaction_id: str
    total_amount: Decimal
    currency: str
    split_rule: SplitRule
    collaboration_type: CollaborationType
    status: SplitStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    dispute_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorPayout:
    """Paiement individuel à un créateur"""
    payout_id: str
    split_id: str
    creator_id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    transaction_id: Optional[str] = None
    fees_deducted: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EscrowAccount:
    """Compte escrow pour projets collaboratifs"""
    escrow_id: str
    project_name: str
    total_amount: Decimal
    currency: str
    participants: List[CreatorParticipant]
    milestone_conditions: List[Dict[str, Any]]
    status: EscrowStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    release_date: Optional[datetime] = None
    dispute_deadline: Optional[datetime] = None


class SplitPaymentCalculator:
    """🧮 Calculateur de splits intelligents"""
    
    def __init__(self):
        self.precision = Decimal('0.01')
        self.rounding = ROUND_HALF_UP
    
    def calculate_splits(
        self,
        total_amount: Decimal,
        split_rule: SplitRule,
        collaboration_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """🎯 Calcul des splits selon la règle définie"""
        
        try:
            results = {}
            remaining_amount = total_amount
            
            # Déduction des frais de plateforme
            platform_fee_amount = self._calculate_platform_fee(total_amount, split_rule.platform_fee)
            remaining_amount -= platform_fee_amount
            
            # Déduction des frais de traitement
            processing_fee_amount = self._calculate_processing_fee(total_amount, split_rule.processing_fee)
            remaining_amount -= processing_fee_amount
            
            results["fees"] = {
                "platform_fee": platform_fee_amount,
                "processing_fee": processing_fee_amount,
                "total_fees": platform_fee_amount + processing_fee_amount
            }
            
            # Calcul des montants par créateur
            creator_amounts = {}
            
            if split_rule.split_type == SplitType.PERCENTAGE:
                creator_amounts = self._calculate_percentage_splits(remaining_amount, split_rule.participants)
            
            elif split_rule.split_type == SplitType.FIXED_AMOUNT:
                creator_amounts = self._calculate_fixed_amount_splits(remaining_amount, split_rule.participants)
            
            elif split_rule.split_type == SplitType.TIERED:
                creator_amounts = self._calculate_tiered_splits(remaining_amount, split_rule.participants, collaboration_context)
            
            elif split_rule.split_type == SplitType.HYBRID:
                creator_amounts = self._calculate_hybrid_splits(remaining_amount, split_rule.participants, collaboration_context)
            
            elif split_rule.split_type == SplitType.ROYALTY:
                creator_amounts = self._calculate_royalty_splits(remaining_amount, split_rule.participants, collaboration_context)
            
            results["creators"] = creator_amounts
            results["total_distributed"] = sum(creator_amounts.values())
            results["remaining"] = remaining_amount - results["total_distributed"]
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des splits: {e}")
            raise
    
    def _calculate_platform_fee(self, amount: Decimal, fee_percentage: Decimal) -> Decimal:
        """💰 Calcul des frais de plateforme"""
        
        fee_amount = (amount * fee_percentage / Decimal('100')).quantize(self.precision, self.rounding)
        return fee_amount
    
    def _calculate_processing_fee(self, amount: Decimal, fee_percentage: Decimal) -> Decimal:
        """💳 Calcul des frais de traitement"""
        
        fee_amount = (amount * fee_percentage / Decimal('100')).quantize(self.precision, self.rounding)
        return fee_amount
    
    def _calculate_percentage_splits(
        self,
        amount: Decimal,
        participants: List[CreatorParticipant]
    ) -> Dict[str, Decimal]:
        """📊 Calcul splits par pourcentage"""
        
        results = {}
        total_percentage = sum(p.percentage for p in participants)
        
        # Normalisation si total != 100%
        if total_percentage != Decimal('100'):
            logger.warning(f"Total percentage {total_percentage} != 100%, normalizing")
        
        for participant in participants:
            normalized_percentage = participant.percentage / total_percentage * Decimal('100')
            participant_amount = (amount * normalized_percentage / Decimal('100')).quantize(self.precision, self.rounding)
            
            # Vérification montant minimum
            if participant_amount >= participant.minimum_payout:
                results[participant.creator_id] = participant_amount
            else:
                logger.warning(f"Payout for {participant.creator_id} below minimum ({participant_amount} < {participant.minimum_payout})")
                results[participant.creator_id] = Decimal('0.00')
        
        return results
    
    def _calculate_fixed_amount_splits(
        self,
        amount: Decimal,
        participants: List[CreatorParticipant]
    ) -> Dict[str, Decimal]:
        """💵 Calcul splits montant fixe"""
        
        results = {}
        total_fixed = sum(p.fixed_amount or Decimal('0') for p in participants)
        
        if total_fixed > amount:
            # Réduction proportionnelle si montants fixes > montant total
            reduction_factor = amount / total_fixed
            for participant in participants:
                if participant.fixed_amount:
                    reduced_amount = (participant.fixed_amount * reduction_factor).quantize(self.precision, self.rounding)
                    results[participant.creator_id] = reduced_amount
        else:
            # Distribution normale
            for participant in participants:
                if participant.fixed_amount:
                    results[participant.creator_id] = participant.fixed_amount
        
        return results
    
    def _calculate_tiered_splits(
        self,
        amount: Decimal,
        participants: List[CreatorParticipant],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Decimal]:
        """🏆 Calcul splits par niveaux (basé sur performance)"""
        
        results = {}
        
        # Récupération des métriques de performance depuis le contexte
        performance_metrics = context.get("performance_metrics", {}) if context else {}
        
        # Distribution basée sur les tiers de performance
        total_performance_score = sum(performance_metrics.get(p.creator_id, 1.0) for p in participants)
        
        for participant in participants:
            performance_score = performance_metrics.get(participant.creator_id, 1.0)
            performance_ratio = performance_score / total_performance_score
            
            # Application du pourcentage de base ajusté par la performance
            base_percentage = participant.percentage
            adjusted_percentage = base_percentage * Decimal(str(performance_ratio))
            
            participant_amount = (amount * adjusted_percentage / Decimal('100')).quantize(self.precision, self.rounding)
            results[participant.creator_id] = participant_amount
        
        return results
    
    def _calculate_hybrid_splits(
        self,
        amount: Decimal,
        participants: List[CreatorParticipant],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Decimal]:
        """🔄 Calcul splits hybrides (fixe + pourcentage)"""
        
        results = {}
        remaining_after_fixed = amount
        
        # Phase 1: Distribution des montants fixes
        for participant in participants:
            if participant.fixed_amount and participant.fixed_amount > 0:
                results[participant.creator_id] = participant.fixed_amount
                remaining_after_fixed -= participant.fixed_amount
        
        # Phase 2: Distribution du reste selon pourcentages
        percentage_participants = [p for p in participants if p.percentage > 0]
        
        if percentage_participants and remaining_after_fixed > 0:
            total_percentage = sum(p.percentage for p in percentage_participants)
            
            for participant in percentage_participants:
                percentage_amount = (remaining_after_fixed * participant.percentage / total_percentage).quantize(self.precision, self.rounding)
                
                if participant.creator_id in results:
                    results[participant.creator_id] += percentage_amount
                else:
                    results[participant.creator_id] = percentage_amount
        
        return results
    
    def _calculate_royalty_splits(
        self,
        amount: Decimal,
        participants: List[CreatorParticipant],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Decimal]:
        """🎵 Calcul splits royalties (spécifique musique)"""
        
        results = {}
        
        # Récupération des informations de royalties
        royalty_info = context.get("royalty_info", {}) if context else {}
        
        # Types de royalties musicales
        royalty_types = royalty_info.get("types", ["performance", "mechanical", "synchronization"])
        
        for participant in participants:
            total_royalty = Decimal('0.00')
            
            # Calcul par type de royalty
            for royalty_type in royalty_types:
                type_percentage = royalty_info.get(f"{royalty_type}_percentage", {}).get(participant.creator_id, 0)
                type_amount = (amount * Decimal(str(type_percentage)) / Decimal('100')).quantize(self.precision, self.rounding)
                total_royalty += type_amount
            
            # Application du pourcentage de base si pas de royalties spécifiques
            if total_royalty == Decimal('0.00'):
                total_royalty = (amount * participant.percentage / Decimal('100')).quantize(self.precision, self.rounding)
            
            results[participant.creator_id] = total_royalty
        
        return results


class SplitPaymentManager:
    """🚀 Gestionnaire des Split Payments Enterprise"""
    
    def __init__(self):
        self.calculator = SplitPaymentCalculator()
        self.split_rules: Dict[str, SplitRule] = {}
        self.split_transactions: Dict[str, SplitTransaction] = {}
        self.escrow_accounts: Dict[str, EscrowAccount] = {}
        self.creator_payouts: Dict[str, List[CreatorPayout]] = {}
        self.tax_rates: Dict[str, Decimal] = self._load_tax_rates()
    
    def _load_tax_rates(self) -> Dict[str, Decimal]:
        """📊 Chargement des taux de taxe par pays"""
        
        return {
            "US": Decimal('24.0'),  # Taux fédéral moyen
            "FR": Decimal('30.0'),  # IR + charges sociales
            "DE": Decimal('26.5'),  # Impôt sur le revenu
            "UK": Decimal('20.0'),  # Basic rate
            "CA": Decimal('26.8'),  # Taux combiné moyen
            "AU": Decimal('32.5'),  # Taux marginal moyen
        }
    
    async def create_split_payment(
        self,
        original_transaction_id: str,
        total_amount: Decimal,
        currency: str,
        split_rule_id: str,
        collaboration_type: CollaborationType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SplitTransaction:
        """🎯 Création d'un paiement split"""
        
        try:
            split_id = f"split_{uuid.uuid4().hex[:12]}"
            
            # Vérification de la règle de split
            split_rule = self.split_rules.get(split_rule_id)
            if not split_rule:
                raise ValueError(f"Split rule {split_rule_id} not found")
            
            # Vérification montant minimum
            if total_amount < split_rule.minimum_split_amount:
                raise ValueError(f"Amount {total_amount} below minimum {split_rule.minimum_split_amount}")
            
            # Création de la transaction split
            split_transaction = SplitTransaction(
                split_id=split_id,
                original_transaction_id=original_transaction_id,
                total_amount=total_amount,
                currency=currency,
                split_rule=split_rule,
                collaboration_type=collaboration_type,
                status=SplitStatus.PENDING,
                metadata=metadata or {}
            )
            
            self.split_transactions[split_id] = split_transaction
            
            # Calcul des splits
            split_calculations = self.calculator.calculate_splits(
                total_amount, split_rule, metadata
            )
            
            # Création des payouts individuels
            await self._create_creator_payouts(split_transaction, split_calculations)
            
            # Logging
            logger.info(f"Split payment created: {split_id} for {total_amount} {currency}")
            
            return split_transaction
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du split payment: {e}")
            raise
    
    async def _create_creator_payouts(
        self,
        split_transaction: SplitTransaction,
        split_calculations: Dict[str, Dict[str, Decimal]]
    ):
        """💰 Création des payouts individuels pour chaque créateur"""
        
        creator_amounts = split_calculations.get("creators", {})
        
        for participant in split_transaction.split_rule.participants:
            creator_id = participant.creator_id
            gross_amount = creator_amounts.get(creator_id, Decimal('0.00'))
            
            if gross_amount > Decimal('0.00'):
                # Calcul des taxes
                tax_amount = await self._calculate_tax_withholding(gross_amount, participant.country)
                net_amount = gross_amount - tax_amount
                
                # Création du payout
                payout = CreatorPayout(
                    payout_id=f"payout_{uuid.uuid4().hex[:12]}",
                    split_id=split_transaction.split_id,
                    creator_id=creator_id,
                    amount=gross_amount,
                    currency=split_transaction.currency,
                    status="pending",
                    payment_method=participant.payment_method,
                    fees_deducted=tax_amount,
                    net_amount=net_amount
                )
                
                # Stockage du payout
                if creator_id not in self.creator_payouts:
                    self.creator_payouts[creator_id] = []
                
                self.creator_payouts[creator_id].append(payout)
    
    async def _calculate_tax_withholding(self, amount: Decimal, country: str) -> Decimal:
        """🏛️ Calcul de la retenue fiscale"""
        
        tax_rate = self.tax_rates.get(country, Decimal('0.0'))
        tax_amount = (amount * tax_rate / Decimal('100')).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        return tax_amount
    
    async def process_split_payment(self, split_id: str) -> Dict[str, Any]:
        """⚡ Traitement d'un split payment"""
        
        try:
            split_transaction = self.split_transactions.get(split_id)
            if not split_transaction:
                raise ValueError(f"Split transaction {split_id} not found")
            
            if split_transaction.status != SplitStatus.PENDING:
                raise ValueError(f"Split transaction {split_id} is not pending")
            
            # Mise à jour du statut
            split_transaction.status = SplitStatus.PROCESSING
            
            # Traitement des payouts individuels
            processing_results = []
            
            for participant in split_transaction.split_rule.participants:
                creator_payouts = self.creator_payouts.get(participant.creator_id, [])
                split_payouts = [p for p in creator_payouts if p.split_id == split_id]
                
                for payout in split_payouts:
                    try:
                        result = await self._process_individual_payout(payout)
                        processing_results.append(result)
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du payout {payout.payout_id}: {e}")
                        processing_results.append({
                            "payout_id": payout.payout_id,
                            "success": False,
                            "error": str(e)
                        })
            
            # Vérification du succès global
            successful_payouts = [r for r in processing_results if r.get("success")]
            failed_payouts = [r for r in processing_results if not r.get("success")]
            
            if len(successful_payouts) == len(processing_results):
                split_transaction.status = SplitStatus.COMPLETED
                split_transaction.processed_at = datetime.utcnow()
            elif len(successful_payouts) > 0:
                split_transaction.status = SplitStatus.PROCESSING  # Partiellement traité
            else:
                split_transaction.status = SplitStatus.PENDING  # Échec complet
            
            result = {
                "split_id": split_id,
                "status": split_transaction.status.value,
                "total_payouts": len(processing_results),
                "successful_payouts": len(successful_payouts),
                "failed_payouts": len(failed_payouts),
                "processing_results": processing_results,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Notification aux créateurs
            await self._notify_creators_payment_processed(split_transaction, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du split payment: {e}")
            return {"error": str(e)}
    
    async def _process_individual_payout(self, payout: CreatorPayout) -> Dict[str, Any]:
        """💳 Traitement d'un payout individuel"""
        
        try:
            # Simulation du traitement de paiement
            # En production: intégration avec les gateways de paiement
            
            # Génération d'un ID de transaction
            transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
            
            # Simulation du succès/échec
            success = True  # En production: résultat de l'API gateway
            
            if success:
                payout.status = "completed"
                payout.transaction_id = transaction_id
                payout.processed_at = datetime.utcnow()
                
                return {
                    "payout_id": payout.payout_id,
                    "success": True,
                    "transaction_id": transaction_id,
                    "amount": float(payout.net_amount),
                    "currency": payout.currency
                }
            else:
                payout.status = "failed"
                
                return {
                    "payout_id": payout.payout_id,
                    "success": False,
                    "error": "Payment gateway error"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du payout individuel: {e}")
            return {
                "payout_id": payout.payout_id,
                "success": False,
                "error": str(e)
            }
    
    async def create_escrow_account(
        self,
        project_name: str,
        total_amount: Decimal,
        currency: str,
        participants: List[CreatorParticipant],
        milestone_conditions: List[Dict[str, Any]],
        auto_release_days: int = 30
    ) -> EscrowAccount:
        """🏦 Création d'un compte escrow pour projets collaboratifs"""
        
        try:
            escrow_id = f"escrow_{uuid.uuid4().hex[:12]}"
            
            # Calcul de la date de release automatique
            release_date = datetime.utcnow() + timedelta(days=auto_release_days)
            dispute_deadline = release_date + timedelta(days=7)  # 7 jours pour contester
            
            escrow_account = EscrowAccount(
                escrow_id=escrow_id,
                project_name=project_name,
                total_amount=total_amount,
                currency=currency,
                participants=participants,
                milestone_conditions=milestone_conditions,
                status=EscrowStatus.CREATED,
                release_date=release_date,
                dispute_deadline=dispute_deadline
            )
            
            self.escrow_accounts[escrow_id] = escrow_account
            
            # Logging
            logger.info(f"Escrow account created: {escrow_id} for project {project_name}")
            
            return escrow_account
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du compte escrow: {e}")
            raise
    
    async def fund_escrow_account(self, escrow_id: str, payment_source: Dict[str, Any]) -> Dict[str, Any]:
        """💰 Financement du compte escrow"""
        
        try:
            escrow_account = self.escrow_accounts.get(escrow_id)
            if not escrow_account:
                raise ValueError(f"Escrow account {escrow_id} not found")
            
            if escrow_account.status != EscrowStatus.CREATED:
                raise ValueError(f"Escrow account {escrow_id} cannot be funded in status {escrow_account.status}")
            
            # Simulation du traitement de paiement
            # En production: traitement réel avec payment gateway
            funding_success = True
            
            if funding_success:
                escrow_account.status = EscrowStatus.FUNDED
                
                # Notification aux participants
                await self._notify_escrow_funded(escrow_account)
                
                return {
                    "escrow_id": escrow_id,
                    "status": "funded",
                    "amount": float(escrow_account.total_amount),
                    "currency": escrow_account.currency,
                    "release_date": escrow_account.release_date.isoformat() if escrow_account.release_date else None
                }
            else:
                return {
                    "escrow_id": escrow_id,
                    "status": "funding_failed",
                    "error": "Payment processing failed"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du financement de l'escrow: {e}")
            return {"error": str(e)}
    
    async def release_escrow_funds(
        self,
        escrow_id: str,
        milestone_completed: Optional[str] = None,
        force_release: bool = False
    ) -> Dict[str, Any]:
        """🔓 Release des fonds escrow"""
        
        try:
            escrow_account = self.escrow_accounts.get(escrow_id)
            if not escrow_account:
                raise ValueError(f"Escrow account {escrow_id} not found")
            
            if escrow_account.status != EscrowStatus.FUNDED:
                raise ValueError(f"Escrow account {escrow_id} is not funded")
            
            # Vérification des conditions de release
            release_authorized = force_release or await self._check_release_conditions(
                escrow_account, milestone_completed
            )
            
            if not release_authorized:
                return {
                    "escrow_id": escrow_id,
                    "status": "release_denied",
                    "reason": "Release conditions not met"
                }
            
            # Création du split payment pour distribuer les fonds
            split_rule = await self._create_escrow_split_rule(escrow_account)
            
            split_transaction = await self.create_split_payment(
                original_transaction_id=f"escrow_{escrow_id}",
                total_amount=escrow_account.total_amount,
                currency=escrow_account.currency,
                split_rule_id=split_rule.rule_id,
                collaboration_type=CollaborationType.CONTENT_LICENSING,  # Par défaut
                metadata={"escrow_id": escrow_id, "project_name": escrow_account.project_name}
            )
            
            # Traitement du split payment
            processing_result = await self.process_split_payment(split_transaction.split_id)
            
            if processing_result.get("successful_payouts", 0) > 0:
                escrow_account.status = EscrowStatus.RELEASED
                
                # Notification aux participants
                await self._notify_escrow_released(escrow_account, processing_result)
                
                return {
                    "escrow_id": escrow_id,
                    "status": "released",
                    "split_id": split_transaction.split_id,
                    "processing_result": processing_result
                }
            else:
                return {
                    "escrow_id": escrow_id,
                    "status": "release_failed",
                    "error": "Failed to process payouts"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du release de l'escrow: {e}")
            return {"error": str(e)}
    
    async def _check_release_conditions(
        self,
        escrow_account: EscrowAccount,
        milestone_completed: Optional[str]
    ) -> bool:
        """✅ Vérification des conditions de release"""
        
        # Vérification auto-release par date
        if escrow_account.release_date and datetime.utcnow() >= escrow_account.release_date:
            return True
        
        # Vérification des milestones
        if milestone_completed and escrow_account.milestone_conditions:
            for condition in escrow_account.milestone_conditions:
                if condition.get("milestone_id") == milestone_completed:
                    if condition.get("auto_release", False):
                        return True
        
        return False
    
    async def _create_escrow_split_rule(self, escrow_account: EscrowAccount) -> SplitRule:
        """📋 Création d'une règle de split pour l'escrow"""
        
        rule_id = f"escrow_rule_{uuid.uuid4().hex[:8]}"
        
        split_rule = SplitRule(
            rule_id=rule_id,
            name=f"Escrow Split - {escrow_account.project_name}",
            split_type=SplitType.PERCENTAGE,
            participants=escrow_account.participants,
            platform_fee=Decimal('2.0'),  # Frais réduits pour escrow
            processing_fee=Decimal('1.5'),
            minimum_split_amount=Decimal('1.00')
        )
        
        self.split_rules[rule_id] = split_rule
        return split_rule
    
    async def calculate_creator_shares(
        self,
        split_rule_id: str,
        total_amount: Decimal,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """🧮 Calcul des parts créateurs avec optimisation ML"""
        
        try:
            split_rule = self.split_rules.get(split_rule_id)
            if not split_rule:
                raise ValueError(f"Split rule {split_rule_id} not found")
            
            # Calcul de base
            split_calculations = self.calculator.calculate_splits(
                total_amount, split_rule, performance_data
            )
            
            # Enrichissement avec données fiscales
            creator_details = {}
            
            for participant in split_rule.participants:
                creator_id = participant.creator_id
                gross_amount = split_calculations["creators"].get(creator_id, Decimal('0.00'))
                
                if gross_amount > Decimal('0.00'):
                    tax_amount = await self._calculate_tax_withholding(gross_amount, participant.country)
                    net_amount = gross_amount - tax_amount
                    
                    creator_details[creator_id] = {
                        "name": participant.creator_name,
                        "email": participant.creator_email,
                        "role": participant.role,
                        "percentage": float(participant.percentage),
                        "gross_amount": float(gross_amount),
                        "tax_withholding": float(tax_amount),
                        "net_amount": float(net_amount),
                        "country": participant.country,
                        "payment_method": participant.payment_method
                    }
            
            return {
                "split_rule_id": split_rule_id,
                "total_amount": float(total_amount),
                "fees": {
                    "platform_fee": float(split_calculations["fees"]["platform_fee"]),
                    "processing_fee": float(split_calculations["fees"]["processing_fee"]),
                    "total_fees": float(split_calculations["fees"]["total_fees"])
                },
                "creators": creator_details,
                "total_distributed": float(split_calculations["total_distributed"]),
                "remaining": float(split_calculations["remaining"]),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des parts créateurs: {e}")
            return {"error": str(e)}
    
    async def manage_escrow_funds(
        self,
        escrow_id: str,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """🏛️ Gestion des fonds escrow (release, dispute, refund)"""
        
        try:
            escrow_account = self.escrow_accounts.get(escrow_id)
            if not escrow_account:
                raise ValueError(f"Escrow account {escrow_id} not found")
            
            if action == "release":
                return await self.release_escrow_funds(
                    escrow_id,
                    kwargs.get("milestone_completed"),
                    kwargs.get("force_release", False)
                )
            
            elif action == "dispute":
                return await self._handle_escrow_dispute(escrow_account, kwargs)
            
            elif action == "refund":
                return await self._refund_escrow_funds(escrow_account, kwargs)
            
            elif action == "extend":
                return await self._extend_escrow_deadline(escrow_account, kwargs)
            
            else:
                raise ValueError(f"Unknown escrow action: {action}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la gestion de l'escrow: {e}")
            return {"error": str(e)}
    
    async def _handle_escrow_dispute(
        self,
        escrow_account: EscrowAccount,
        dispute_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⚖️ Gestion des disputes escrow"""
        
        if escrow_account.status != EscrowStatus.FUNDED:
            raise ValueError("Cannot dispute unfunded escrow")
        
        if escrow_account.dispute_deadline and datetime.utcnow() > escrow_account.dispute_deadline:
            raise ValueError("Dispute deadline has passed")
        
        escrow_account.status = EscrowStatus.DISPUTED
        
        # Notification aux parties
        await self._notify_escrow_disputed(escrow_account, dispute_data)
        
        return {
            "escrow_id": escrow_account.escrow_id,
            "status": "disputed",
            "dispute_reason": dispute_data.get("reason"),
            "dispute_initiated_by": dispute_data.get("initiator"),
            "dispute_deadline": escrow_account.dispute_deadline.isoformat() if escrow_account.dispute_deadline else None
        }
    
    async def _refund_escrow_funds(
        self,
        escrow_account: EscrowAccount,
        refund_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """💸 Remboursement des fonds escrow"""
        
        if escrow_account.status not in [EscrowStatus.FUNDED, EscrowStatus.DISPUTED]:
            raise ValueError(f"Cannot refund escrow in status {escrow_account.status}")
        
        # Simulation du remboursement
        refund_success = True
        
        if refund_success:
            escrow_account.status = EscrowStatus.REFUNDED
            
            # Notification
            await self._notify_escrow_refunded(escrow_account, refund_data)
            
            return {
                "escrow_id": escrow_account.escrow_id,
                "status": "refunded",
                "refund_amount": float(escrow_account.total_amount),
                "refund_reason": refund_data.get("reason")
            }
        else:
            return {
                "escrow_id": escrow_account.escrow_id,
                "status": "refund_failed",
                "error": "Refund processing failed"
            }
    
    async def _extend_escrow_deadline(
        self,
        escrow_account: EscrowAccount,
        extension_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📅 Extension du délai escrow"""
        
        additional_days = extension_data.get("additional_days", 7)
        
        if escrow_account.release_date:
            escrow_account.release_date += timedelta(days=additional_days)
        
        if escrow_account.dispute_deadline:
            escrow_account.dispute_deadline += timedelta(days=additional_days)
        
        # Notification
        await self._notify_escrow_extended(escrow_account, extension_data)
        
        return {
            "escrow_id": escrow_account.escrow_id,
            "status": "extended",
            "new_release_date": escrow_account.release_date.isoformat() if escrow_account.release_date else None,
            "additional_days": additional_days
        }
    
    async def generate_tax_documents(
        self,
        creator_id: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """📄 Génération des documents fiscaux pour un créateur"""
        
        try:
            # Récupération des payouts de l'année
            creator_payouts = self.creator_payouts.get(creator_id, [])
            year_payouts = [
                p for p in creator_payouts
                if p.processed_at and p.processed_at.year == tax_year and p.status == "completed"
            ]
            
            if not year_payouts:
                return {
                    "creator_id": creator_id,
                    "tax_year": tax_year,
                    "total_earnings": 0.0,
                    "total_tax_withheld": 0.0,
                    "payouts_count": 0,
                    "documents": []
                }
            
            # Calculs fiscaux
            total_earnings = sum(p.amount for p in year_payouts)
            total_tax_withheld = sum(p.fees_deducted for p in year_payouts)
            total_net = sum(p.net_amount for p in year_payouts)
            
            # Génération du document 1099 (US) ou équivalent
            tax_document = {
                "document_type": "1099-NEC",  # Exemple US
                "creator_id": creator_id,
                "tax_year": tax_year,
                "total_earnings": float(total_earnings),
                "total_tax_withheld": float(total_tax_withheld),
                "total_net_paid": float(total_net),
                "payouts_count": len(year_payouts),
                "generated_at": datetime.utcnow().isoformat(),
                "payouts_detail": [
                    {
                        "payout_id": p.payout_id,
                        "date": p.processed_at.isoformat() if p.processed_at else None,
                        "amount": float(p.amount),
                        "tax_withheld": float(p.fees_deducted),
                        "net_amount": float(p.net_amount)
                    }
                    for p in year_payouts
                ]
            }
            
            return {
                "creator_id": creator_id,
                "tax_year": tax_year,
                "documents": [tax_document],
                "summary": {
                    "total_earnings": float(total_earnings),
                    "total_tax_withheld": float(total_tax_withheld),
                    "total_net_paid": float(total_net),
                    "payouts_count": len(year_payouts)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des documents fiscaux: {e}")
            return {"error": str(e)}
    
    # Méthodes de notification (simulation)
    async def _notify_creators_payment_processed(self, split_transaction: SplitTransaction, result: Dict[str, Any]):
        """📧 Notification traitement paiement"""
        logger.info(f"Notifying creators for split {split_transaction.split_id}")
    
    async def _notify_escrow_funded(self, escrow_account: EscrowAccount):
        """📧 Notification escrow financé"""
        logger.info(f"Notifying escrow funded: {escrow_account.escrow_id}")
    
    async def _notify_escrow_released(self, escrow_account: EscrowAccount, result: Dict[str, Any]):
        """📧 Notification escrow released"""
        logger.info(f"Notifying escrow released: {escrow_account.escrow_id}")
    
    async def _notify_escrow_disputed(self, escrow_account: EscrowAccount, dispute_data: Dict[str, Any]):
        """📧 Notification dispute escrow"""
        logger.info(f"Notifying escrow disputed: {escrow_account.escrow_id}")
    
    async def _notify_escrow_refunded(self, escrow_account: EscrowAccount, refund_data: Dict[str, Any]):
        """📧 Notification remboursement escrow"""
        logger.info(f"Notifying escrow refunded: {escrow_account.escrow_id}")
    
    async def _notify_escrow_extended(self, escrow_account: EscrowAccount, extension_data: Dict[str, Any]):
        """📧 Notification extension escrow"""
        logger.info(f"Notifying escrow extended: {escrow_account.escrow_id}")
    
    def create_split_rule(
        self,
        name: str,
        split_type: SplitType,
        participants: List[CreatorParticipant],
        **kwargs
    ) -> SplitRule:
        """📋 Création d'une règle de split"""
        
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        
        split_rule = SplitRule(
            rule_id=rule_id,
            name=name,
            split_type=split_type,
            participants=participants,
            platform_fee=kwargs.get("platform_fee", Decimal('5.0')),
            processing_fee=kwargs.get("processing_fee", Decimal('2.9')),
            minimum_split_amount=kwargs.get("minimum_split_amount", Decimal('1.00')),
            auto_release_days=kwargs.get("auto_release_days", 7),
            dispute_window_days=kwargs.get("dispute_window_days", 30)
        )
        
        self.split_rules[rule_id] = split_rule
        
        logger.info(f"Split rule created: {rule_id} - {name}")
        
        return split_rule
    
    def get_split_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Statistiques des split payments"""
        
        try:
            # Simulation de statistiques
            return {
                "period_days": period_days,
                "total_splits": len(self.split_transactions),
                "total_volume": float(sum(s.total_amount for s in self.split_transactions.values())),
                "completed_splits": len([s for s in self.split_transactions.values() if s.status == SplitStatus.COMPLETED]),
                "pending_splits": len([s for s in self.split_transactions.values() if s.status == SplitStatus.PENDING]),
                "active_escrows": len([e for e in self.escrow_accounts.values() if e.status == EscrowStatus.FUNDED]),
                "total_creators": len(self.creator_payouts),
                "average_split_amount": float(sum(s.total_amount for s in self.split_transactions.values()) / len(self.split_transactions)) if self.split_transactions else 0.0
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"error": str(e)}