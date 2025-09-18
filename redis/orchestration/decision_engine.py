#!/usr/bin/env python3
"""🎯 Redis Decision Engine - AI-Powered Intelligent Decision Making System
===========================================================================
Expert: LEAD DEV IA + ML ENGINEER + BACKEND SENIOR + DEVOPS
Technologies: Decision Intelligence + Machine Learning + Multi-Criteria Analysis + Automated Reasoning
Architecture: Level 3 - Decision Intelligence Layer
Date: 2025-01-14

Ultra-advanced decision engine with AI-powered reasoning, multi-criteria optimization,
automated decision making, risk assessment and creator economy optimization.
===========================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
===========================================================================
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
import json
import math
import statistics
from collections import deque, defaultdict
import redis
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
import networkx as nx
import heapq
import uuid

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Types de décisions orchestration"""
    RESOURCE_ALLOCATION = "resource_allocation"
    SCALING_DECISION = "scaling_decision"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_ACTION = "security_action"
    LOAD_BALANCING = "load_balancing"
    FAILOVER_TRIGGER = "failover_trigger"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    CREATOR_RECOMMENDATION = "creator_recommendation"
    CONTENT_ROUTING = "content_routing"
    MONETIZATION_STRATEGY = "monetization_strategy"

class DecisionPriority(Enum):
    """Priorités des décisions"""
    CRITICAL = "critical"     # Impact immédiat system
    HIGH = "high"            # Impact business significatif
    MEDIUM = "medium"        # Impact modéré
    LOW = "low"             # Impact mineur
    BACKGROUND = "background" # Optimisations arrière-plan

class DecisionStatus(Enum):
    """États des décisions"""
    PENDING = "pending"           # En attente évaluation
    EVALUATING = "evaluating"     # En cours d'évaluation
    APPROVED = "approved"         # Approuvée pour exécution
    EXECUTING = "executing"       # En cours d'exécution
    COMPLETED = "completed"       # Exécutée avec succès
    FAILED = "failed"            # Échec exécution
    ROLLED_BACK = "rolled_back"   # Annulée/rollback
    CANCELLED = "cancelled"       # Annulée avant exécution

class RiskLevel(Enum):
    """Niveaux de risque"""
    VERY_LOW = "very_low"     # < 10%
    LOW = "low"              # 10-25%
    MEDIUM = "medium"        # 25-50%
    HIGH = "high"           # 50-75%
    VERY_HIGH = "very_high"  # > 75%

class ConfidenceLevel(Enum):
    """Niveaux de confiance"""
    VERY_HIGH = "very_high"   # > 90%
    HIGH = "high"            # 75-90%
    MEDIUM = "medium"        # 50-75%
    LOW = "low"             # 25-50%
    VERY_LOW = "very_low"    # < 25%

@dataclass
class DecisionCriteria:
    """Critères d'évaluation décision"""
    name: str = ""
    weight: float = 1.0
    min_value: float = 0.0
    max_value: float = 100.0
    target_value: Optional[float] = None
    direction: str = "maximize"  # maximize, minimize, target
    
    # Contraintes
    mandatory: bool = False
    threshold: Optional[float] = None
    
    # Métadonnées
    description: str = ""
    unit: str = ""
    data_source: str = ""

@dataclass
class DecisionOption:
    """Option de décision"""
    option_id: str = ""
    name: str = ""
    description: str = ""
    
    # Scores critères
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    
    # Évaluation
    total_score: float = 0.0
    confidence: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Ressources requises
    cpu_cost: float = 0.0
    memory_cost: float = 0.0
    time_cost: float = 0.0
    financial_cost: float = 0.0
    
    # Impact estimé
    performance_impact: float = 0.0
    business_impact: float = 0.0
    user_impact: float = 0.0
    
    # Métadonnées
    implementation_complexity: str = "medium"
    rollback_difficulty: str = "medium"
    dependencies: List[str] = field(default_factory=list)

@dataclass
class DecisionContext:
    """Contexte de décision"""
    context_id: str = ""
    decision_type: DecisionType = DecisionType.RESOURCE_ALLOCATION
    priority: DecisionPriority = DecisionPriority.MEDIUM
    
    # État système
    current_state: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    objectives: List[str] = field(default_factory=list)
    
    # Temporel
    deadline: Optional[datetime] = None
    time_horizon: int = 3600  # Horizon temporel en secondes
    
    # Données contextuelles
    user_context: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    technical_context: Dict[str, Any] = field(default_factory=dict)
    
    # Historique
    previous_decisions: List[str] = field(default_factory=list)
    success_rate: float = 0.8

@dataclass
class Decision:
    """Décision prise par le moteur"""
    decision_id: str = ""
    context: DecisionContext = field(default_factory=DecisionContext)
    
    # Options évaluées
    options_evaluated: List[DecisionOption] = field(default_factory=list)
    selected_option: Optional[DecisionOption] = None
    
    # Justification
    reasoning: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    risk_assessment: RiskLevel = RiskLevel.MEDIUM
    
    # Exécution
    status: DecisionStatus = DecisionStatus.PENDING
    execution_plan: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)
    
    # Monitoring
    success_metrics: List[str] = field(default_factory=list)
    monitoring_duration: int = 3600
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Résultats
    execution_success: bool = False
    actual_impact: Dict[str, float] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)

@dataclass
class DecisionRule:
    """Règle de décision automatisée"""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    
    # Conditions
    conditions: List[str] = field(default_factory=list)  # Conditions logiques
    triggers: List[str] = field(default_factory=list)    # Déclencheurs
    
    # Actions
    action_type: DecisionType = DecisionType.RESOURCE_ALLOCATION
    action_params: Dict[str, Any] = field(default_factory=dict)
    
    # Validation
    safety_checks: List[str] = field(default_factory=list)
    approval_required: bool = False
    
    # Métadonnées
    priority: DecisionPriority = DecisionPriority.MEDIUM
    enabled: bool = True
    confidence_threshold: float = 0.7
    
    # Statistiques
    execution_count: int = 0
    success_rate: float = 1.0
    last_executed: Optional[datetime] = None

class RedisDecisionEngine:
    """🎯 Moteur de décision Redis ultra-intelligent"""
    
    def __init__(self):
        """Initialisation moteur de décision"""
        self.redis_client = None
        self.is_running = False
        
        # Modèles ML pour décision
        self.decision_classifier = RandomForestClassifier(n_estimators=200, random_state=42)
        self.outcome_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.risk_assessor = RandomForestClassifier(n_estimators=150, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Storage decisions
        self.active_decisions = {}
        self.decision_history = deque(maxlen=10000)
        self.decision_rules = {}
        self.criteria_definitions = {}
        
        # Système de cache intelligent
        self.decision_cache = {}
        self.evaluation_cache = {}
        self.prediction_cache = {}
        
        # Métriques performance
        self.decision_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_confidence": 0.0,
            "average_execution_time": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Graphe de dépendances décisions
        self.decision_graph = nx.DiGraph()
        
        # Règles par défaut
        self._initialize_default_rules()
        
        logger.info("🎯 Moteur de décision Redis initialisé")

    async def start(self, redis_connection=None):
        """Démarrer le moteur de décision"""
        try:
            self.redis_client = redis_connection or redis.Redis(decode_responses=True)
            self.is_running = True
            
            # Démarrer processus décisionnels
            decision_tasks = [
                self._run_decision_monitoring(),
                self._run_rule_evaluation(),
                self._run_outcome_tracking(),
                self._run_model_updates(),
                self._run_cache_maintenance()
            ]
            
            await asyncio.gather(*decision_tasks, return_exceptions=True)
            
            logger.info("🎯 Moteur de décision démarré avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage moteur décision: {e}")
            raise

    async def stop(self):
        """Arrêter le moteur de décision"""
        self.is_running = False
        logger.info("🎯 Moteur de décision arrêté")

    async def make_decision(self, context: DecisionContext, options: List[DecisionOption] = None) -> Decision:
        """Prendre une décision intelligente"""
        try:
            decision_id = str(uuid.uuid4())
            context.context_id = context.context_id or decision_id
            
            # Créer décision
            decision = Decision(
                decision_id=decision_id,
                context=context,
                created_at=datetime.now()
            )
            
            # Vérifier cache décision
            cache_key = self._generate_decision_cache_key(context)
            cached_decision = self.decision_cache.get(cache_key)
            
            if cached_decision and self._is_cache_valid(cached_decision):
                logger.info(f"🎯 Décision récupérée du cache: {decision_id}")
                decision.selected_option = cached_decision["option"]
                decision.confidence = cached_decision["confidence"]
                decision.reasoning = f"Décision mise en cache basée sur contexte similaire"
                self.decision_metrics["cache_hit_rate"] += 1
                return decision
            
            # Générer options si non fournies
            if not options:
                options = await self._generate_decision_options(context)
            
            # Évaluer toutes les options
            for option in options:
                await self._evaluate_option(option, context)
            
            decision.options_evaluated = options
            
            # Sélectionner meilleure option
            best_option = await self._select_best_option(options, context)
            decision.selected_option = best_option
            
            # Évaluer confiance et risque
            decision.confidence = await self._assess_decision_confidence(best_option, context)
            decision.risk_assessment = await self._assess_decision_risk(best_option, context)
            
            # Générer justification
            decision.reasoning = await self._generate_reasoning(best_option, options, context)
            
            # Planifier exécution
            decision.execution_plan = await self._create_execution_plan(best_option, context)
            decision.rollback_plan = await self._create_rollback_plan(best_option, context)
            
            # Définir métriques de succès
            decision.success_metrics = await self._define_success_metrics(best_option, context)
            
            decision.decided_at = datetime.now()
            decision.status = DecisionStatus.APPROVED
            
            # Sauvegarder décision
            self.active_decisions[decision_id] = decision
            await self._persist_decision(decision)
            
            # Mettre en cache
            self.decision_cache[cache_key] = {
                "option": best_option,
                "confidence": decision.confidence,
                "timestamp": datetime.now(),
                "context_hash": hash(str(context))
            }
            
            # Mettre à jour métriques
            self.decision_metrics["total_decisions"] += 1
            
            logger.info(f"🎯 Décision prise: {decision_id} - Option: {best_option.name}")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Erreur prise décision: {e}")
            decision.status = DecisionStatus.FAILED
            return decision

    async def execute_decision(self, decision_id: str) -> bool:
        """Exécuter une décision"""
        try:
            decision = self.active_decisions.get(decision_id)
            if not decision:
                logger.error(f"❌ Décision non trouvée: {decision_id}")
                return False
            
            if decision.status != DecisionStatus.APPROVED:
                logger.error(f"❌ Décision non approuvée: {decision_id}")
                return False
            
            decision.status = DecisionStatus.EXECUTING
            decision.executed_at = datetime.now()
            
            # Exécuter plan d'exécution
            execution_success = True
            for step in decision.execution_plan:
                step_success = await self._execute_step(step, decision)
                if not step_success:
                    execution_success = False
                    break
            
            if execution_success:
                decision.status = DecisionStatus.COMPLETED
                decision.execution_success = True
                decision.completed_at = datetime.now()
                
                # Démarrer monitoring
                await self._start_decision_monitoring(decision)
                
                self.decision_metrics["successful_decisions"] += 1
                logger.info(f"🎯 Décision exécutée avec succès: {decision_id}")
                
            else:
                # Rollback en cas d'échec
                decision.status = DecisionStatus.FAILED
                await self._execute_rollback(decision)
                logger.error(f"❌ Échec exécution décision: {decision_id}")
            
            await self._update_decision_metrics(decision)
            return execution_success
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution décision {decision_id}: {e}")
            return False

    async def evaluate_creator_opportunity(self, creator_id: str, opportunity_data: Dict[str, Any]) -> Decision:
        """Évaluer une opportunité pour un créateur"""
        try:
            # Créer contexte spécialisé créateur
            context = DecisionContext(
                decision_type=DecisionType.CREATOR_RECOMMENDATION,
                priority=DecisionPriority.HIGH,
                user_context={"creator_id": creator_id},
                business_context=opportunity_data,
                objectives=["maximize_creator_revenue", "optimize_engagement", "ensure_brand_safety"]
            )
            
            # Générer options d'opportunité
            options = []
            
            # Option 1: Collaboration recommandée
            if opportunity_data.get("collaboration_potential", 0) > 0.7:
                collab_option = DecisionOption(
                    option_id="collab_opportunity",
                    name="Recommander Collaboration",
                    description="Recommander collaboration avec créateurs similaires",
                    performance_impact=0.8,
                    business_impact=0.9,
                    user_impact=0.7
                )
                options.append(collab_option)
            
            # Option 2: Optimisation contenu
            if opportunity_data.get("content_optimization_score", 0) > 0.6:
                content_option = DecisionOption(
                    option_id="content_optimization",
                    name="Optimiser Stratégie Contenu",
                    description="Optimiser stratégie de contenu basée sur analytics",
                    performance_impact=0.7,
                    business_impact=0.8,
                    user_impact=0.8
                )
                options.append(content_option)
            
            # Option 3: Monétisation avancée
            if opportunity_data.get("monetization_readiness", 0) > 0.8:
                monetization_option = DecisionOption(
                    option_id="advanced_monetization",
                    name="Activer Monétisation Avancée",
                    description="Activer fonctionnalités monétisation premium",
                    performance_impact=0.6,
                    business_impact=1.0,
                    user_impact=0.9
                )
                options.append(monetization_option)
            
            # Prendre décision
            decision = await self.make_decision(context, options)
            
            logger.info(f"🎯 Opportunité évaluée pour créateur {creator_id}")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation opportunité créateur: {e}")
            return Decision()

    async def optimize_resource_allocation(self, resource_data: Dict[str, Any]) -> Decision:
        """Optimiser allocation des ressources"""
        try:
            context = DecisionContext(
                decision_type=DecisionType.RESOURCE_ALLOCATION,
                priority=DecisionPriority.HIGH,
                current_state=resource_data,
                objectives=["minimize_cost", "maximize_performance", "ensure_availability"]
            )
            
            # Générer options d'allocation
            options = []
            
            # Option 1: Scale up conservateur
            conservative_option = DecisionOption(
                option_id="conservative_scale",
                name="Scale Up Conservateur",
                description="Augmentation progressive des ressources",
                cpu_cost=resource_data.get("current_cpu", 0) * 1.2,
                memory_cost=resource_data.get("current_memory", 0) * 1.2,
                financial_cost=100.0,
                performance_impact=0.6,
                risk_level=RiskLevel.LOW
            )
            options.append(conservative_option)
            
            # Option 2: Scale up agressif
            aggressive_option = DecisionOption(
                option_id="aggressive_scale",
                name="Scale Up Agressif",
                description="Augmentation significative des ressources",
                cpu_cost=resource_data.get("current_cpu", 0) * 2.0,
                memory_cost=resource_data.get("current_memory", 0) * 2.0,
                financial_cost=300.0,
                performance_impact=0.9,
                risk_level=RiskLevel.MEDIUM
            )
            options.append(aggressive_option)
            
            # Option 3: Optimisation sans scale
            optimization_option = DecisionOption(
                option_id="optimize_existing",
                name="Optimiser Ressources Existantes",
                description="Optimiser utilisation sans ajout ressources",
                cpu_cost=resource_data.get("current_cpu", 0),
                memory_cost=resource_data.get("current_memory", 0),
                financial_cost=0.0,
                performance_impact=0.4,
                risk_level=RiskLevel.VERY_LOW
            )
            options.append(optimization_option)
            
            decision = await self.make_decision(context, options)
            
            logger.info("🎯 Allocation ressources optimisée")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation allocation: {e}")
            return Decision()

    async def assess_security_action(self, threat_data: Dict[str, Any]) -> Decision:
        """Évaluer action de sécurité"""
        try:
            threat_level = threat_data.get("threat_level", "medium")
            priority = DecisionPriority.CRITICAL if threat_level == "critical" else DecisionPriority.HIGH
            
            context = DecisionContext(
                decision_type=DecisionType.SECURITY_ACTION,
                priority=priority,
                current_state=threat_data,
                objectives=["ensure_security", "minimize_disruption", "maintain_availability"],
                deadline=datetime.now() + timedelta(minutes=5)  # Réaction rapide
            )
            
            options = []
            
            # Option 1: Blocage immédiat
            if threat_data.get("confidence", 0) > 0.8:
                block_option = DecisionOption(
                    option_id="immediate_block",
                    name="Blocage Immédiat",
                    description="Bloquer immédiatement la source de menace",
                    performance_impact=-0.2,  # Impact négatif temporaire
                    business_impact=0.9,      # Protection business
                    user_impact=-0.3,        # Gêne utilisateurs
                    risk_level=RiskLevel.LOW
                )
                options.append(block_option)
            
            # Option 2: Monitoring renforcé
            monitoring_option = DecisionOption(
                option_id="enhanced_monitoring",
                name="Monitoring Renforcé",
                description="Renforcer surveillance sans blocage",
                performance_impact=-0.1,
                business_impact=0.6,
                user_impact=0.0,
                risk_level=RiskLevel.MEDIUM
            )
            options.append(monitoring_option)
            
            # Option 3: Quarantaine
            quarantine_option = DecisionOption(
                option_id="quarantine",
                name="Mise en Quarantaine",
                description="Isoler les éléments suspects",
                performance_impact=-0.15,
                business_impact=0.8,
                user_impact=-0.1,
                risk_level=RiskLevel.LOW
            )
            options.append(quarantine_option)
            
            decision = await self.make_decision(context, options)
            
            logger.info("🎯 Action sécurité évaluée")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation sécurité: {e}")
            return Decision()

    async def get_decision_analytics(self) -> Dict[str, Any]:
        """Obtenir analytics des décisions"""
        try:
            analytics = {
                "decision_metrics": self.decision_metrics.copy(),
                "active_decisions_count": len(self.active_decisions),
                "decision_history_count": len(self.decision_history),
                "decision_rules_count": len(self.decision_rules),
                
                "decision_types_distribution": await self._get_decision_types_stats(),
                "priority_distribution": await self._get_priority_stats(),
                "success_rate_by_type": await self._get_success_rate_by_type(),
                "average_confidence_by_type": await self._get_confidence_stats(),
                "risk_distribution": await self._get_risk_distribution(),
                
                "performance_metrics": {
                    "average_decision_time": await self._calculate_avg_decision_time(),
                    "cache_efficiency": self.decision_metrics.get("cache_hit_rate", 0),
                    "model_accuracy": await self._get_model_accuracy(),
                    "prediction_reliability": await self._get_prediction_reliability()
                },
                
                "recommendations": await self._generate_system_recommendations(),
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Erreur génération analytics: {e}")
            return {"error": str(e)}

    # ================== MÉTHODES PRIVÉES ==================

    def _initialize_default_rules(self):
        """Initialiser règles par défaut"""
        # Règle scaling automatique
        scaling_rule = DecisionRule(
            rule_id="auto_scaling",
            name="Auto-scaling Intelligent",
            description="Déclencher scaling basé sur métriques",
            conditions=["cpu_usage > 80", "memory_usage > 85", "latency > 200ms"],
            triggers=["performance_degradation"],
            action_type=DecisionType.SCALING_DECISION,
            action_params={"scale_factor": 1.5, "max_instances": 10},
            safety_checks=["budget_available", "resource_limits"],
            confidence_threshold=0.8
        )
        self.decision_rules["auto_scaling"] = scaling_rule
        
        # Règle sécurité
        security_rule = DecisionRule(
            rule_id="threat_response",
            name="Réponse Automatique Menaces",
            description="Répondre automatiquement aux menaces détectées",
            conditions=["threat_confidence > 0.9", "threat_severity == 'critical'"],
            triggers=["security_threat_detected"],
            action_type=DecisionType.SECURITY_ACTION,
            action_params={"action": "block", "duration": 3600},
            approval_required=False,
            confidence_threshold=0.9
        )
        self.decision_rules["threat_response"] = security_rule

    async def _run_decision_monitoring(self):
        """Monitoring décisions actives"""
        while self.is_running:
            try:
                for decision in self.active_decisions.values():
                    if decision.status == DecisionStatus.COMPLETED:
                        await self._monitor_decision_outcome(decision)
                await asyncio.sleep(30)  # Check toutes les 30 secondes
            except Exception as e:
                logger.error(f"❌ Erreur monitoring décisions: {e}")
                await asyncio.sleep(60)

    async def _run_rule_evaluation(self):
        """Évaluation règles automatiques"""
        while self.is_running:
            try:
                for rule in self.decision_rules.values():
                    if rule.enabled:
                        await self._evaluate_rule(rule)
                await asyncio.sleep(10)  # Check toutes les 10 secondes
            except Exception as e:
                logger.error(f"❌ Erreur évaluation règles: {e}")
                await asyncio.sleep(30)

    async def _run_outcome_tracking(self):
        """Tracking résultats décisions"""
        while self.is_running:
            try:
                await self._track_decision_outcomes()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur tracking résultats: {e}")
                await asyncio.sleep(600)

    async def _run_model_updates(self):
        """Mise à jour modèles ML"""
        while self.is_running:
            try:
                await self._update_decision_models()
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"❌ Erreur mise à jour modèles: {e}")
                await asyncio.sleep(1800)

    async def _run_cache_maintenance(self):
        """Maintenance cache décisions"""
        while self.is_running:
            try:
                await self._clean_expired_cache()
                await asyncio.sleep(600)  # Toutes les 10 minutes
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
                await asyncio.sleep(300)

    async def _generate_decision_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Générer options de décision"""
        options = []
        
        if context.decision_type == DecisionType.SCALING_DECISION:
            options = [
                DecisionOption(
                    option_id="scale_up",
                    name="Scale Up",
                    description="Augmenter les ressources",
                    performance_impact=0.8,
                    financial_cost=100.0
                ),
                DecisionOption(
                    option_id="scale_down",
                    name="Scale Down",
                    description="Diminuer les ressources",
                    performance_impact=-0.2,
                    financial_cost=-50.0
                ),
                DecisionOption(
                    option_id="maintain",
                    name="Maintenir",
                    description="Garder niveau actuel",
                    performance_impact=0.0,
                    financial_cost=0.0
                )
            ]
            
        return options

    async def _evaluate_option(self, option: DecisionOption, context: DecisionContext):
        """Évaluer une option de décision"""
        try:
            # Score basé sur critères
            total_score = 0.0
            weights_sum = 0.0
            
            # Critères standards
            criteria = {
                "performance": option.performance_impact,
                "cost": -option.financial_cost / 1000.0,  # Normaliser coût
                "risk": -(option.risk_level.value == "high") * 0.5,
                "business_impact": option.business_impact,
                "user_impact": option.user_impact
            }
            
            # Poids critères selon contexte
            weights = {
                "performance": 0.3,
                "cost": 0.2,
                "risk": 0.15,
                "business_impact": 0.2,
                "user_impact": 0.15
            }
            
            for criterion, value in criteria.items():
                weight = weights.get(criterion, 1.0)
                total_score += value * weight
                weights_sum += weight
                option.criteria_scores[criterion] = value
            
            option.total_score = total_score / weights_sum if weights_sum > 0 else 0.0
            option.confidence = min(1.0, max(0.0, option.total_score))
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation option: {e}")
            option.total_score = 0.0

    async def _select_best_option(self, options: List[DecisionOption], context: DecisionContext) -> DecisionOption:
        """Sélectionner la meilleure option"""
        if not options:
            return DecisionOption()
        
        # Trier par score total
        options.sort(key=lambda x: x.total_score, reverse=True)
        
        # Vérifier contraintes
        for option in options:
            if await self._check_constraints(option, context):
                return option
        
        # Si aucune option valide, retourner la première
        return options[0]

    async def _check_constraints(self, option: DecisionOption, context: DecisionContext) -> bool:
        """Vérifier contraintes option"""
        constraints = context.constraints
        
        # Contrainte budget
        if "max_cost" in constraints:
            if option.financial_cost > constraints["max_cost"]:
                return False
        
        # Contrainte risque
        if "max_risk" in constraints:
            risk_values = {"very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5}
            if risk_values.get(option.risk_level.value, 3) > constraints["max_risk"]:
                return False
        
        return True

    async def _assess_decision_confidence(self, option: DecisionOption, context: DecisionContext) -> ConfidenceLevel:
        """Évaluer confiance décision"""
        confidence_score = option.confidence
        
        if confidence_score > 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score > 0.75:
            return ConfidenceLevel.HIGH
        elif confidence_score > 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence_score > 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    async def _assess_decision_risk(self, option: DecisionOption, context: DecisionContext) -> RiskLevel:
        """Évaluer risque décision"""
        # Retourner le niveau de risque de l'option
        return option.risk_level

    async def _generate_reasoning(self, selected_option: DecisionOption, all_options: List[DecisionOption], context: DecisionContext) -> str:
        """Générer justification décision"""
        reasoning = f"Option '{selected_option.name}' sélectionnée avec score {selected_option.total_score:.2f}. "
        
        # Raisons principales
        if selected_option.performance_impact > 0.7:
            reasoning += "Impact performance élevé. "
        if selected_option.financial_cost < 100:
            reasoning += "Coût financier acceptable. "
        if selected_option.risk_level in [RiskLevel.LOW, RiskLevel.VERY_LOW]:
            reasoning += "Risque faible. "
        
        # Comparaison autres options
        other_scores = [opt.total_score for opt in all_options if opt != selected_option]
        if other_scores:
            max_other = max(other_scores)
            if selected_option.total_score > max_other + 0.1:
                reasoning += f"Nettement supérieure aux autres options (écart: {selected_option.total_score - max_other:.2f}). "
        
        return reasoning

    async def _create_execution_plan(self, option: DecisionOption, context: DecisionContext) -> List[str]:
        """Créer plan d'exécution"""
        plan = []
        
        if context.decision_type == DecisionType.SCALING_DECISION:
            if "scale_up" in option.option_id:
                plan = [
                    "validate_resources_available",
                    "prepare_scaling_configuration", 
                    "execute_scaling_operation",
                    "verify_scaling_success",
                    "update_load_balancer",
                    "monitor_new_instances"
                ]
            elif "scale_down" in option.option_id:
                plan = [
                    "identify_instances_to_remove",
                    "drain_traffic_from_instances",
                    "wait_for_connection_cleanup",
                    "terminate_instances",
                    "update_load_balancer",
                    "verify_service_stability"
                ]
        elif context.decision_type == DecisionType.SECURITY_ACTION:
            plan = [
                "backup_current_config",
                "apply_security_rule",
                "test_security_effectiveness",
                "monitor_false_positives",
                "adjust_if_necessary"
            ]
        
        return plan

    async def _create_rollback_plan(self, option: DecisionOption, context: DecisionContext) -> List[str]:
        """Créer plan de rollback"""
        rollback_plan = []
        
        if context.decision_type == DecisionType.SCALING_DECISION:
            rollback_plan = [
                "stop_new_operations",
                "restore_previous_configuration",
                "verify_rollback_success",
                "notify_operations_team"
            ]
        elif context.decision_type == DecisionType.SECURITY_ACTION:
            rollback_plan = [
                "disable_security_rule",
                "restore_previous_access",
                "verify_service_restoration",
                "investigate_false_positive"
            ]
        
        return rollback_plan

    async def _define_success_metrics(self, option: DecisionOption, context: DecisionContext) -> List[str]:
        """Définir métriques de succès"""
        metrics = []
        
        if context.decision_type == DecisionType.SCALING_DECISION:
            metrics = [
                "cpu_utilization_target_range",
                "memory_utilization_target_range", 
                "response_time_improvement",
                "cost_efficiency_ratio"
            ]
        elif context.decision_type == DecisionType.SECURITY_ACTION:
            metrics = [
                "threat_mitigation_success",
                "false_positive_rate",
                "service_availability_maintained",
                "user_experience_impact"
            ]
        
        return metrics

    def _generate_decision_cache_key(self, context: DecisionContext) -> str:
        """Générer clé cache décision"""
        key_components = [
            context.decision_type.value,
            str(hash(str(context.current_state))),
            str(hash(str(context.constraints))),
            context.priority.value
        ]
        return ":".join(key_components)

    def _is_cache_valid(self, cached_decision: Dict[str, Any]) -> bool:
        """Vérifier validité cache"""
        cache_age = (datetime.now() - cached_decision["timestamp"]).total_seconds()
        return cache_age < 300  # Cache valide 5 minutes

    async def _persist_decision(self, decision: Decision):
        """Persister décision"""
        try:
            if self.redis_client:
                key = f"decision:{decision.decision_id}"
                data = {
                    "context_type": decision.context.decision_type.value,
                    "priority": decision.context.priority.value,
                    "status": decision.status.value,
                    "confidence": decision.confidence.value,
                    "risk": decision.risk_assessment.value,
                    "created_at": decision.created_at.isoformat(),
                    "reasoning": decision.reasoning
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence décision: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Récupérer métriques moteur"""
        return {
            "engine_type": "decision_engine",
            "status": "running" if self.is_running else "stopped",
            "active_decisions": len(self.active_decisions),
            "decision_history_size": len(self.decision_history),
            "decision_rules": len(self.decision_rules),
            "performance_metrics": self.decision_metrics,
            "cache_sizes": {
                "decision_cache": len(self.decision_cache),
                "evaluation_cache": len(self.evaluation_cache),
                "prediction_cache": len(self.prediction_cache)
            }
        }