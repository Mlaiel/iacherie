"""🚀 Dunning Management System - IA Influencer Agent Platform Enterprise
====================================================================
Module: backend/platform_core/billing/dunning_management.py
Author: Fahed Mlaiel (mlaiel@live.de)
====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME GESTION RELANCES PAIEMENTS INTELLIGENT
Dunning management avancé avec ML optimization et recovery workflows
- Intelligent dunning sequences avec ML personalization
- Multi-channel dunning (email, SMS, appels, courrier)
- Smart timing optimization et churn prevention
- Automated payment retry avec success prediction
- Comprehensive recovery analytics et compliance

Multi-Expert Implementation:
🧠 Lead Dev IA: ML dunning optimization, timing prediction, personalization algorithms
🏗️ Backend Senior: High-performance dunning processing, workflow automation
🤖 ML Engineer: Recovery prediction models, customer behavior analysis, success optimization
🗄️ DBA: Dunning history tracking, analytics optimization, performance queries
🔒 Security: Compliance dunning, data protection, audit trails
🌐 Microservices: Multi-channel integrations, notification services, payment gateways
🎵 Audio: Music industry dunning specifics, artist payment recoveries
⚙️ DevOps: Automated dunning monitoring, campaign management, scaling
💡 AI Prompt: Intelligent dunning content generation, personalized messaging
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import statistics
from collections import defaultdict

# Configuration logging
logger = logging.getLogger(__name__)


class DunningStatus(Enum):
    """États de dunning"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DunningAction(Enum):
    """Actions de dunning"""
    EMAIL_REMINDER = "email_reminder"
    SMS_REMINDER = "sms_reminder"
    PHONE_CALL = "phone_call"
    PAYMENT_RETRY = "payment_retry"
    ACCOUNT_SUSPENSION = "account_suspension"
    COLLECTION_AGENCY = "collection_agency"
    WRITE_OFF = "write_off"


class DunningChannel(Enum):
    """Canaux de dunning"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    MAIL = "mail"
    IN_APP = "in_app"
    AUTOMATED = "automated"


class RecoveryStatus(Enum):
    """États de récupération"""
    PENDING = "pending"
    RECOVERED = "recovered"
    PARTIAL_RECOVERY = "partial_recovery"
    FAILED = "failed"
    WRITTEN_OFF = "written_off"


@dataclass
class DunningRule:
    """Règle de dunning"""
    rule_id: str
    name: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DunningCase:
    """Cas de dunning"""
    case_id: str
    customer_id: str
    invoice_id: str
    amount_due: Decimal
    currency: str
    days_overdue: int
    dunning_level: int
    current_action: Optional[DunningAction]
    status: DunningStatus
    created_at: datetime
    last_action_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    recovery_probability: float = 0.0
    total_attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DunningExecution:
    """Exécution d'action dunning"""
    execution_id: str
    case_id: str
    action_type: DunningAction
    channel: DunningChannel
    executed_at: datetime
    success: bool
    response_data: Dict[str, Any] = field(default_factory=dict)
    cost: Decimal = Decimal('0.00')
    error_message: Optional[str] = None


@dataclass
class CustomerDunningProfile:
    """Profil de dunning client"""
    customer_id: str
    preferred_channel: DunningChannel
    best_contact_time: str  # Format HH:MM
    timezone: str
    language: str
    dunning_sensitivity: str  # "low", "medium", "high"
    payment_behavior_score: float
    historical_recovery_rate: float
    last_successful_channel: Optional[DunningChannel] = None
    opt_out_channels: List[DunningChannel] = field(default_factory=list)


class MLDunningOptimizer:
    """🤖 Optimiseur ML pour dunning"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.recovery_factors = {
            "days_overdue": 0.25,
            "amount_due": 0.20,
            "customer_history": 0.20,
            "payment_method": 0.15,
            "channel_effectiveness": 0.10,
            "timing_optimization": 0.10
        }
    
    def predict_recovery_probability(
        self,
        dunning_case: DunningCase,
        customer_profile: CustomerDunningProfile,
        proposed_action: DunningAction
    ) -> float:
        """🎯 Prédiction de probabilité de récupération"""
        
        factors = {}
        
        # Facteur jours de retard
        if dunning_case.days_overdue <= 7:
            factors["days_overdue"] = 0.9  # Très bon
        elif dunning_case.days_overdue <= 30:
            factors["days_overdue"] = 0.7  # Bon
        elif dunning_case.days_overdue <= 90:
            factors["days_overdue"] = 0.4  # Moyen
        else:
            factors["days_overdue"] = 0.1  # Difficile
        
        # Facteur montant
        if dunning_case.amount_due <= Decimal('50'):
            factors["amount_due"] = 0.8  # Petits montants plus faciles
        elif dunning_case.amount_due <= Decimal('500'):
            factors["amount_due"] = 0.6  # Montants moyens
        else:
            factors["amount_due"] = 0.3  # Gros montants plus difficiles
        
        # Facteur historique client
        factors["customer_history"] = customer_profile.historical_recovery_rate
        
        # Facteur méthode de paiement (simulé)
        payment_method = dunning_case.metadata.get("payment_method", "card")
        method_scores = {
            "card": 0.8,
            "bank_transfer": 0.6,
            "wallet": 0.7,
            "cash": 0.3
        }
        factors["payment_method"] = method_scores.get(payment_method, 0.5)
        
        # Facteur efficacité du canal
        channel_effectiveness = self._get_channel_effectiveness(
            proposed_action, customer_profile
        )
        factors["channel_effectiveness"] = channel_effectiveness
        
        # Facteur timing
        timing_score = self._calculate_timing_score(customer_profile)
        factors["timing_optimization"] = timing_score
        
        # Calcul final
        weighted_score = sum(
            factors[factor] * weight
            for factor, weight in self.recovery_factors.items()
        )
        
        return min(1.0, max(0.0, weighted_score))
    
    def _get_channel_effectiveness(
        self,
        action: DunningAction,
        customer_profile: CustomerDunningProfile
    ) -> float:
        """📊 Efficacité du canal pour ce client"""
        
        # Mapping action -> canal
        action_channels = {
            DunningAction.EMAIL_REMINDER: DunningChannel.EMAIL,
            DunningAction.SMS_REMINDER: DunningChannel.SMS,
            DunningAction.PHONE_CALL: DunningChannel.PHONE,
            DunningAction.PAYMENT_RETRY: DunningChannel.AUTOMATED
        }
        
        channel = action_channels.get(action, DunningChannel.EMAIL)
        
        # Bonus si c'est le canal préféré
        if channel == customer_profile.preferred_channel:
            return 0.9
        
        # Malus si le canal est opt-out
        if channel in customer_profile.opt_out_channels:
            return 0.1
        
        # Bonus si c'est le dernier canal ayant réussi
        if channel == customer_profile.last_successful_channel:
            return 0.8
        
        # Score par défaut selon le canal
        default_scores = {
            DunningChannel.EMAIL: 0.7,
            DunningChannel.SMS: 0.6,
            DunningChannel.PHONE: 0.8,
            DunningChannel.AUTOMATED: 0.5
        }
        
        return default_scores.get(channel, 0.5)
    
    def _calculate_timing_score(self, customer_profile: CustomerDunningProfile) -> float:
        """⏰ Score d'optimisation timing"""
        
        current_hour = datetime.utcnow().hour
        
        # Parse de l'heure préférée
        try:
            preferred_hour = int(customer_profile.best_contact_time.split(':')[0])
            
            # Distance par rapport à l'heure préférée
            hour_distance = abs(current_hour - preferred_hour)
            
            # Normalisé sur 12 heures max
            timing_score = 1 - (hour_distance / 12)
            
            return max(0.3, timing_score)  # Minimum 30%
            
        except:
            return 0.5  # Score neutre si erreur
    
    def optimize_dunning_sequence(
        self,
        dunning_case: DunningCase,
        customer_profile: CustomerDunningProfile,
        available_actions: List[DunningAction]
    ) -> List[Tuple[DunningAction, datetime, float]]:
        """🎯 Optimisation de séquence de dunning"""
        
        optimized_sequence = []
        current_time = datetime.utcnow()
        
        # Tri des actions par probabilité de succès
        action_probabilities = []
        
        for action in available_actions:
            probability = self.predict_recovery_probability(
                dunning_case, customer_profile, action
            )
            action_probabilities.append((action, probability))
        
        # Tri par probabilité décroissante
        action_probabilities.sort(key=lambda x: x[1], reverse=True)
        
        # Planification avec espacement optimal
        for i, (action, probability) in enumerate(action_probabilities):
            # Calcul du délai optimal
            if i == 0:
                # Première action: immédiate si probabilité élevée
                delay_hours = 0 if probability > 0.7 else 2
            else:
                # Actions suivantes: espacement progressif
                delay_hours = 24 * (i + 1)  # 1 jour, 2 jours, etc.
            
            scheduled_time = current_time + timedelta(hours=delay_hours)
            optimized_sequence.append((action, scheduled_time, probability))
        
        return optimized_sequence


class DunningManagementEngine:
    """🚀 Moteur de Gestion Dunning Enterprise"""
    
    def __init__(self):
        self.ml_optimizer = MLDunningOptimizer()
        self.dunning_rules: Dict[str, DunningRule] = {}
        self.dunning_cases: Dict[str, DunningCase] = {}
        self.customer_profiles: Dict[str, CustomerDunningProfile] = {}
        self.executions: List[DunningExecution] = []
        self.recovery_stats = defaultdict(float)
        self._initialize_default_rules()
        self._initialize_sample_profiles()
    
    def _initialize_default_rules(self):
        """🔧 Initialisation des règles par défaut"""
        
        default_rules = [
            {
                "name": "Early Stage Dunning",
                "trigger_conditions": {
                    "days_overdue_min": 1,
                    "days_overdue_max": 7,
                    "amount_min": 0
                },
                "actions": [
                    {"type": "email_reminder", "delay_hours": 0, "channel": "email"},
                    {"type": "sms_reminder", "delay_hours": 48, "channel": "sms"},
                    {"type": "payment_retry", "delay_hours": 72, "channel": "automated"}
                ]
            },
            {
                "name": "Medium Stage Dunning",
                "trigger_conditions": {
                    "days_overdue_min": 8,
                    "days_overdue_max": 30,
                    "amount_min": 0
                },
                "actions": [
                    {"type": "email_reminder", "delay_hours": 0, "channel": "email"},
                    {"type": "phone_call", "delay_hours": 24, "channel": "phone"},
                    {"type": "sms_reminder", "delay_hours": 48, "channel": "sms"},
                    {"type": "payment_retry", "delay_hours": 96, "channel": "automated"}
                ]
            },
            {
                "name": "Late Stage Dunning",
                "trigger_conditions": {
                    "days_overdue_min": 31,
                    "days_overdue_max": 90,
                    "amount_min": 100
                },
                "actions": [
                    {"type": "phone_call", "delay_hours": 0, "channel": "phone"},
                    {"type": "email_reminder", "delay_hours": 12, "channel": "email"},
                    {"type": "account_suspension", "delay_hours": 168, "channel": "automated"}
                ]
            },
            {
                "name": "Collection Stage",
                "trigger_conditions": {
                    "days_overdue_min": 91,
                    "amount_min": 50
                },
                "actions": [
                    {"type": "collection_agency", "delay_hours": 0, "channel": "automated"},
                    {"type": "write_off", "delay_hours": 720, "channel": "automated"}  # 30 jours
                ]
            }
        ]
        
        for rule_data in default_rules:
            rule_id = f"rule_{uuid.uuid4().hex[:8]}"
            rule = DunningRule(
                rule_id=rule_id,
                name=rule_data["name"],
                trigger_conditions=rule_data["trigger_conditions"],
                actions=rule_data["actions"]
            )
            self.dunning_rules[rule_id] = rule
    
    def _initialize_sample_profiles(self):
        """👥 Initialisation des profils échantillons"""
        
        # Quelques profils type pour la démonstration
        sample_profiles = [
            {
                "customer_id": "cust_001",
                "preferred_channel": DunningChannel.EMAIL,
                "best_contact_time": "10:00",
                "timezone": "UTC",
                "language": "en",
                "dunning_sensitivity": "low",
                "payment_behavior_score": 0.8,
                "historical_recovery_rate": 0.75
            },
            {
                "customer_id": "cust_002", 
                "preferred_channel": DunningChannel.SMS,
                "best_contact_time": "14:00",
                "timezone": "UTC",
                "language": "fr",
                "dunning_sensitivity": "medium",
                "payment_behavior_score": 0.6,
                "historical_recovery_rate": 0.5
            }
        ]
        
        for profile_data in sample_profiles:
            profile = CustomerDunningProfile(**profile_data)
            self.customer_profiles[profile.customer_id] = profile
    
    async def create_dunning_case(
        self,
        customer_id: str,
        invoice_id: str,
        amount_due: Decimal,
        currency: str,
        days_overdue: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DunningCase:
        """📋 Création d'un cas de dunning"""
        
        try:
            case_id = f"dunning_{uuid.uuid4().hex[:12]}"
            
            # Récupération du profil client
            customer_profile = self.customer_profiles.get(
                customer_id,
                self._create_default_profile(customer_id)
            )
            
            # Création du cas
            dunning_case = DunningCase(
                case_id=case_id,
                customer_id=customer_id,
                invoice_id=invoice_id,
                amount_due=amount_due,
                currency=currency,
                days_overdue=days_overdue,
                dunning_level=1,
                current_action=None,
                status=DunningStatus.PENDING,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Calcul de la probabilité de récupération initiale
            dunning_case.recovery_probability = self.ml_optimizer.predict_recovery_probability(
                dunning_case, customer_profile, DunningAction.EMAIL_REMINDER
            )
            
            self.dunning_cases[case_id] = dunning_case
            
            # Planification automatique de la première action
            await self._schedule_next_action(dunning_case)
            
            logger.info(f"Cas de dunning créé: {case_id} pour {amount_due} {currency}")
            
            return dunning_case
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du cas de dunning: {e}")
            raise
    
    def _create_default_profile(self, customer_id: str) -> CustomerDunningProfile:
        """👤 Création d'un profil par défaut"""
        
        profile = CustomerDunningProfile(
            customer_id=customer_id,
            preferred_channel=DunningChannel.EMAIL,
            best_contact_time="10:00",
            timezone="UTC",
            language="en",
            dunning_sensitivity="medium",
            payment_behavior_score=0.5,
            historical_recovery_rate=0.6
        )
        
        self.customer_profiles[customer_id] = profile
        return profile
    
    async def _schedule_next_action(self, dunning_case: DunningCase):
        """📅 Planification de la prochaine action"""
        
        # Recherche de la règle applicable
        applicable_rule = self._find_applicable_rule(dunning_case)
        
        if not applicable_rule:
            logger.warning(f"Aucune règle applicable pour le cas {dunning_case.case_id}")
            return
        
        # Récupération du profil client
        customer_profile = self.customer_profiles.get(dunning_case.customer_id)
        if not customer_profile:
            return
        
        # Sélection de l'action optimale
        available_actions = [
            DunningAction(action["type"]) 
            for action in applicable_rule.actions
        ]
        
        if not available_actions:
            return
        
        # Optimisation de la séquence avec ML
        optimized_sequence = self.ml_optimizer.optimize_dunning_sequence(
            dunning_case, customer_profile, available_actions
        )
        
        if optimized_sequence:
            best_action, scheduled_time, probability = optimized_sequence[0]
            
            dunning_case.current_action = best_action
            dunning_case.next_action_at = scheduled_time
            dunning_case.recovery_probability = probability
            dunning_case.status = DunningStatus.ACTIVE
            
            logger.info(f"Prochaine action programmée: {best_action} à {scheduled_time}")
    
    def _find_applicable_rule(self, dunning_case: DunningCase) -> Optional[DunningRule]:
        """🔍 Recherche de règle applicable"""
        
        for rule in self.dunning_rules.values():
            if not rule.enabled:
                continue
            
            conditions = rule.trigger_conditions
            
            # Vérification jours de retard
            days_min = conditions.get("days_overdue_min", 0)
            days_max = conditions.get("days_overdue_max", float('inf'))
            
            if not (days_min <= dunning_case.days_overdue <= days_max):
                continue
            
            # Vérification montant
            amount_min = Decimal(str(conditions.get("amount_min", 0)))
            amount_max = Decimal(str(conditions.get("amount_max", float('inf'))))
            
            if not (amount_min <= dunning_case.amount_due <= amount_max):
                continue
            
            # Vérification niveau de dunning
            level_min = conditions.get("dunning_level_min", 1)
            level_max = conditions.get("dunning_level_max", 10)
            
            if not (level_min <= dunning_case.dunning_level <= level_max):
                continue
            
            return rule
        
        return None
    
    async def process_dunning_actions(self) -> Dict[str, Any]:
        """⚡ Traitement des actions de dunning programmées"""
        
        try:
            current_time = datetime.utcnow()
            processed_count = 0
            success_count = 0
            
            # Recherche des cas prêts pour action
            ready_cases = [
                case for case in self.dunning_cases.values()
                if (case.status == DunningStatus.ACTIVE and 
                    case.next_action_at and 
                    case.next_action_at <= current_time and
                    case.current_action)
            ]
            
            results = []
            
            for case in ready_cases:
                try:
                    result = await self._execute_dunning_action(case)
                    results.append(result)
                    processed_count += 1
                    
                    if result.get("success"):
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution pour le cas {case.case_id}: {e}")
                    results.append({
                        "case_id": case.case_id,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "processed_cases": processed_count,
                "successful_executions": success_count,
                "failed_executions": processed_count - success_count,
                "results": results,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des actions: {e}")
            return {"error": str(e)}
    
    async def _execute_dunning_action(self, dunning_case: DunningCase) -> Dict[str, Any]:
        """🎯 Exécution d'une action de dunning"""
        
        try:
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            action = dunning_case.current_action
            
            if not action:
                return {"success": False, "error": "No action defined"}
            
            # Détermination du canal
            channel = self._determine_channel(action, dunning_case.customer_id)
            
            # Exécution selon le type d'action
            if action == DunningAction.EMAIL_REMINDER:
                success, response_data, cost = await self._send_email_reminder(dunning_case)
            
            elif action == DunningAction.SMS_REMINDER:
                success, response_data, cost = await self._send_sms_reminder(dunning_case)
            
            elif action == DunningAction.PHONE_CALL:
                success, response_data, cost = await self._initiate_phone_call(dunning_case)
            
            elif action == DunningAction.PAYMENT_RETRY:
                success, response_data, cost = await self._retry_payment(dunning_case)
            
            elif action == DunningAction.ACCOUNT_SUSPENSION:
                success, response_data, cost = await self._suspend_account(dunning_case)
            
            elif action == DunningAction.COLLECTION_AGENCY:
                success, response_data, cost = await self._send_to_collection(dunning_case)
            
            elif action == DunningAction.WRITE_OFF:
                success, response_data, cost = await self._write_off_debt(dunning_case)
            
            else:
                success, response_data, cost = False, {"error": "Unknown action"}, Decimal('0')
            
            # Enregistrement de l'exécution
            execution = DunningExecution(
                execution_id=execution_id,
                case_id=dunning_case.case_id,
                action_type=action,
                channel=channel,
                executed_at=datetime.utcnow(),
                success=success,
                response_data=response_data,
                cost=cost,
                error_message=response_data.get("error") if not success else None
            )
            
            self.executions.append(execution)
            
            # Mise à jour du cas
            dunning_case.last_action_at = execution.executed_at
            dunning_case.total_attempts += 1
            
            if success:
                # Succès: vérifier si paiement récupéré
                if action == DunningAction.PAYMENT_RETRY and response_data.get("payment_successful"):
                    dunning_case.status = DunningStatus.COMPLETED
                    self.recovery_stats["successful_recoveries"] += 1
                else:
                    # Planifier la prochaine action
                    await self._schedule_next_action(dunning_case)
            else:
                # Échec: incrementer le niveau et replanifier
                dunning_case.dunning_level += 1
                await self._schedule_next_action(dunning_case)
            
            return {
                "case_id": dunning_case.case_id,
                "execution_id": execution_id,
                "action": action.value,
                "channel": channel.value,
                "success": success,
                "cost": float(cost),
                "response_data": response_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'action: {e}")
            return {
                "case_id": dunning_case.case_id,
                "success": False,
                "error": str(e)
            }
    
    def _determine_channel(self, action: DunningAction, customer_id: str) -> DunningChannel:
        """📡 Détermination du canal optimal"""
        
        # Mapping par défaut
        default_channels = {
            DunningAction.EMAIL_REMINDER: DunningChannel.EMAIL,
            DunningAction.SMS_REMINDER: DunningChannel.SMS,
            DunningAction.PHONE_CALL: DunningChannel.PHONE,
            DunningAction.PAYMENT_RETRY: DunningChannel.AUTOMATED,
            DunningAction.ACCOUNT_SUSPENSION: DunningChannel.AUTOMATED,
            DunningAction.COLLECTION_AGENCY: DunningChannel.AUTOMATED,
            DunningAction.WRITE_OFF: DunningChannel.AUTOMATED
        }
        
        # Optimisation basée sur le profil client
        customer_profile = self.customer_profiles.get(customer_id)
        if customer_profile:
            # Utiliser le canal préféré si compatible
            preferred = customer_profile.preferred_channel
            default = default_channels.get(action, DunningChannel.EMAIL)
            
            if action in [DunningAction.EMAIL_REMINDER, DunningAction.SMS_REMINDER]:
                if preferred in [DunningChannel.EMAIL, DunningChannel.SMS]:
                    return preferred
        
        return default_channels.get(action, DunningChannel.EMAIL)
    
    async def _send_email_reminder(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """📧 Envoi de rappel par email"""
        
        try:
            # Simulation d'envoi d'email
            customer_profile = self.customer_profiles.get(dunning_case.customer_id)
            
            email_content = self._generate_email_content(dunning_case, customer_profile)
            
            # Simulation du succès/échec
            import random
            success = random.random() > 0.1  # 90% de succès
            
            if success:
                response_data = {
                    "message_id": f"email_{uuid.uuid4().hex[:8]}",
                    "sent_to": f"customer_{dunning_case.customer_id}@example.com",
                    "content": email_content,
                    "delivered": True
                }
                cost = Decimal('0.05')  # Coût d'envoi email
            else:
                response_data = {
                    "error": "Email delivery failed",
                    "reason": "Invalid email address"
                }
                cost = Decimal('0.00')
            
            logger.info(f"Email reminder {'sent' if success else 'failed'} for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _send_sms_reminder(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """📱 Envoi de rappel par SMS"""
        
        try:
            # Simulation d'envoi de SMS
            customer_profile = self.customer_profiles.get(dunning_case.customer_id)
            
            sms_content = self._generate_sms_content(dunning_case, customer_profile)
            
            # Simulation du succès/échec
            import random
            success = random.random() > 0.05  # 95% de succès
            
            if success:
                response_data = {
                    "message_id": f"sms_{uuid.uuid4().hex[:8]}",
                    "sent_to": f"+1234567890",
                    "content": sms_content,
                    "delivered": True
                }
                cost = Decimal('0.10')  # Coût d'envoi SMS
            else:
                response_data = {
                    "error": "SMS delivery failed",
                    "reason": "Invalid phone number"
                }
                cost = Decimal('0.00')
            
            logger.info(f"SMS reminder {'sent' if success else 'failed'} for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _initiate_phone_call(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """📞 Lancement d'appel téléphonique"""
        
        try:
            # Simulation d'appel téléphonique
            import random
            
            call_outcomes = ["answered", "voicemail", "no_answer", "busy"]
            outcome = random.choice(call_outcomes)
            
            success = outcome in ["answered", "voicemail"]
            
            response_data = {
                "call_id": f"call_{uuid.uuid4().hex[:8]}",
                "outcome": outcome,
                "duration_seconds": random.randint(30, 300) if outcome == "answered" else 0,
                "answered": outcome == "answered"
            }
            
            cost = Decimal('2.50')  # Coût d'appel
            
            logger.info(f"Phone call {outcome} for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _retry_payment(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """💳 Nouvelle tentative de paiement"""
        
        try:
            # Simulation de nouvelle tentative de paiement
            import random
            
            # Probabilité de succès basée sur l'historique du client
            customer_profile = self.customer_profiles.get(dunning_case.customer_id)
            base_success_rate = customer_profile.payment_behavior_score if customer_profile else 0.5
            
            # Réduction basée sur les jours de retard
            success_rate = base_success_rate * (1 - (dunning_case.days_overdue / 100))
            success_rate = max(0.1, success_rate)  # Minimum 10%
            
            payment_successful = random.random() < success_rate
            
            if payment_successful:
                response_data = {
                    "payment_id": f"pay_{uuid.uuid4().hex[:8]}",
                    "amount_charged": float(dunning_case.amount_due),
                    "currency": dunning_case.currency,
                    "payment_successful": True,
                    "transaction_id": f"txn_{uuid.uuid4().hex[:8]}"
                }
                cost = Decimal('0.00')  # Pas de coût pour retry automatique
                success = True
            else:
                response_data = {
                    "payment_successful": False,
                    "decline_reason": random.choice([
                        "insufficient_funds",
                        "card_expired",
                        "payment_method_invalid",
                        "bank_decline"
                    ])
                }
                cost = Decimal('0.00')
                success = False
            
            logger.info(f"Payment retry {'successful' if payment_successful else 'failed'} for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _suspend_account(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """🚫 Suspension de compte"""
        
        try:
            # Simulation de suspension de compte
            response_data = {
                "account_id": dunning_case.customer_id,
                "suspended": True,
                "suspension_reason": "Payment overdue",
                "suspension_date": datetime.utcnow().isoformat(),
                "reactivation_conditions": f"Payment of {dunning_case.amount_due} {dunning_case.currency}"
            }
            
            cost = Decimal('0.00')  # Pas de coût pour suspension automatique
            success = True
            
            logger.warning(f"Account suspended for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _send_to_collection(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """🏢 Envoi en agence de recouvrement"""
        
        try:
            # Simulation d'envoi en agence de recouvrement
            response_data = {
                "collection_agency": "Professional Recovery Services",
                "case_reference": f"PRS_{uuid.uuid4().hex[:8]}",
                "amount_sent": float(dunning_case.amount_due),
                "agency_fee_percentage": 25.0,
                "estimated_recovery_time": "30-90 days"
            }
            
            # Coût = pourcentage de l'agence
            cost = dunning_case.amount_due * Decimal('0.25')  # 25% de commission
            success = True
            
            logger.info(f"Case {dunning_case.case_id} sent to collection agency")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    async def _write_off_debt(self, dunning_case: DunningCase) -> Tuple[bool, Dict[str, Any], Decimal]:
        """❌ Annulation de créance"""
        
        try:
            # Simulation d'annulation de créance
            response_data = {
                "write_off_amount": float(dunning_case.amount_due),
                "write_off_date": datetime.utcnow().isoformat(),
                "reason": "Uncollectable debt",
                "tax_implications": "Deductible as bad debt"
            }
            
            cost = Decimal('0.00')  # Pas de coût direct, mais perte de revenus
            success = True
            
            # Mise à jour du statut
            dunning_case.status = DunningStatus.COMPLETED
            
            logger.info(f"Debt written off for case {dunning_case.case_id}")
            
            return success, response_data, cost
            
        except Exception as e:
            return False, {"error": str(e)}, Decimal('0.00')
    
    def _generate_email_content(
        self,
        dunning_case: DunningCase,
        customer_profile: Optional[CustomerDunningProfile]
    ) -> str:
        """📝 Génération contenu email"""
        
        language = customer_profile.language if customer_profile else "en"
        
        if language == "fr":
            subject = f"Rappel de paiement - Facture en retard"
            content = f"""Cher client,

Nous vous rappelons que votre facture #{dunning_case.invoice_id} d'un montant de {dunning_case.amount_due} {dunning_case.currency} est en retard de {dunning_case.days_overdue} jour(s).

Merci de procéder au paiement dans les plus brefs délais pour éviter toute interruption de service.

Cordialement,
L'équipe IA Chéries"""
        else:
            subject = f"Payment Reminder - Overdue Invoice"
            content = f"""Dear Customer,

This is a reminder that your invoice #{dunning_case.invoice_id} for {dunning_case.amount_due} {dunning_case.currency} is {dunning_case.days_overdue} day(s) overdue.

Please make payment as soon as possible to avoid service interruption.

Best regards,
The IA Chéries Team"""
        
        return content
    
    def _generate_sms_content(
        self,
        dunning_case: DunningCase,
        customer_profile: Optional[CustomerDunningProfile]
    ) -> str:
        """📱 Génération contenu SMS"""
        
        language = customer_profile.language if customer_profile else "en"
        
        if language == "fr":
            content = f"IA Chéries: Votre facture de {dunning_case.amount_due} {dunning_case.currency} est en retard. Payez maintenant: [lien]"
        else:
            content = f"IA Chéries: Your invoice of {dunning_case.amount_due} {dunning_case.currency} is overdue. Pay now: [link]"
        
        return content
    
    async def resolve_dunning_case(
        self,
        case_id: str,
        resolution_type: str,
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """✅ Résolution d'un cas de dunning"""
        
        try:
            dunning_case = self.dunning_cases.get(case_id)
            if not dunning_case:
                return {"error": f"Dunning case {case_id} not found"}
            
            if resolution_type == "payment_received":
                # Paiement reçu
                amount_paid = Decimal(str(resolution_data.get("amount_paid", 0)))
                
                if amount_paid >= dunning_case.amount_due:
                    dunning_case.status = DunningStatus.COMPLETED
                    self.recovery_stats["full_recoveries"] += 1
                else:
                    dunning_case.amount_due -= amount_paid
                    self.recovery_stats["partial_recoveries"] += 1
                
                # Mise à jour du profil client (succès)
                customer_profile = self.customer_profiles.get(dunning_case.customer_id)
                if customer_profile:
                    customer_profile.historical_recovery_rate = min(1.0, customer_profile.historical_recovery_rate + 0.1)
            
            elif resolution_type == "manual_write_off":
                # Annulation manuelle
                dunning_case.status = DunningStatus.COMPLETED
                self.recovery_stats["write_offs"] += 1
            
            elif resolution_type == "dispute":
                # Dispute
                dunning_case.status = DunningStatus.PAUSED
                self.recovery_stats["disputes"] += 1
            
            elif resolution_type == "customer_deceased":
                # Client décédé
                dunning_case.status = DunningStatus.CANCELLED
            
            else:
                return {"error": f"Unknown resolution type: {resolution_type}"}
            
            return {
                "case_id": case_id,
                "status": dunning_case.status.value,
                "resolution_type": resolution_type,
                "resolved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la résolution du cas: {e}")
            return {"error": str(e)}
    
    def get_dunning_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Statistiques de dunning"""
        
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Filtrage des cas de la période
            period_cases = [
                case for case in self.dunning_cases.values()
                if start_date <= case.created_at <= end_date
            ]
            
            # Filtrage des exécutions de la période
            period_executions = [
                execution for execution in self.executions
                if start_date <= execution.executed_at <= end_date
            ]
            
            # Statistiques par statut
            status_counts = defaultdict(int)
            for case in period_cases:
                status_counts[case.status.value] += 1
            
            # Statistiques par action
            action_counts = defaultdict(int)
            action_success_rates = defaultdict(lambda: {"total": 0, "successful": 0})
            
            for execution in period_executions:
                action_type = execution.action_type.value
                action_counts[action_type] += 1
                action_success_rates[action_type]["total"] += 1
                if execution.success:
                    action_success_rates[action_type]["successful"] += 1
            
            # Calcul des taux de succès
            success_rates = {}
            for action, stats in action_success_rates.items():
                if stats["total"] > 0:
                    success_rates[action] = round((stats["successful"] / stats["total"]) * 100, 2)
                else:
                    success_rates[action] = 0
            
            # Métriques financières
            total_amount_dunning = sum(case.amount_due for case in period_cases)
            total_recovery_cost = sum(execution.cost for execution in period_executions)
            
            completed_cases = [case for case in period_cases if case.status == DunningStatus.COMPLETED]
            recovered_amount = sum(case.amount_due for case in completed_cases)
            
            recovery_rate = (len(completed_cases) / len(period_cases) * 100) if period_cases else 0
            
            return {
                "period_days": period_days,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "case_statistics": {
                    "total_cases": len(period_cases),
                    "by_status": dict(status_counts),
                    "recovery_rate_percentage": round(recovery_rate, 2)
                },
                "action_statistics": {
                    "total_executions": len(period_executions),
                    "by_action_type": dict(action_counts),
                    "success_rates": success_rates
                },
                "financial_metrics": {
                    "total_amount_in_dunning": float(total_amount_dunning),
                    "amount_recovered": float(recovered_amount),
                    "total_recovery_costs": float(total_recovery_cost),
                    "cost_recovery_ratio": float(total_recovery_cost / recovered_amount) if recovered_amount > 0 else 0
                },
                "ml_model_version": self.ml_optimizer.model_version,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des statistiques: {e}")
            return {"error": str(e)}