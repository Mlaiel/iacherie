#!/usr/bin/env python3
"""⚡ Decision Engine - AI-Powered Intelligent Decision Making
============================================================
Expert: LEAD DEV IA + ML ENGINEER + BACKEND SENIOR + DEVOPS
Technologies: Decision Intelligence + Multi-Criteria Analysis + AI Reasoning + Automated Decision Making
Architecture: Level 3 - Decision Intelligence Layer
Date: 2025-01-14

Ultra-advanced decision engine for Redis orchestration with AI-driven decision making,
multi-criteria analysis, rule-based reasoning and intelligent automation.
============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
============================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
import heapq
import statistics
from concurrent.futures import ThreadPoolExecutor
import math

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Types de décisions supportées"""
    RESOURCE_ALLOCATION = "resource_allocation"
    SCALING_DECISION = "scaling_decision"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_ACTION = "security_action"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    WORKLOAD_DISTRIBUTION = "workload_distribution"
    COST_OPTIMIZATION = "cost_optimization"
    CAPACITY_PLANNING = "capacity_planning"
    EMERGENCY_RESPONSE = "emergency_response"
    CONFIGURATION_CHANGE = "configuration_change"

class DecisionPriority(Enum):
    """Priorités des décisions"""
    CRITICAL = "critical"      # Décision immédiate requise
    HIGH = "high"             # Décision dans l'heure
    MEDIUM = "medium"         # Décision dans les 24h
    LOW = "low"               # Décision dans la semaine
    DEFERRED = "deferred"     # Décision peut être reportée

class DecisionStatus(Enum):
    """États des décisions"""
    PENDING = "pending"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MONITORING = "monitoring"

class DecisionStrategy(Enum):
    """Stratégies de prise de décision"""
    CONSERVATIVE = "conservative"    # Privilégie la stabilité
    AGGRESSIVE = "aggressive"       # Privilégie la performance
    BALANCED = "balanced"           # Équilibre tous les facteurs
    COST_OPTIMIZED = "cost_optimized" # Privilégie les coûts
    SECURITY_FIRST = "security_first" # Privilégie la sécurité
    PERFORMANCE_FIRST = "performance_first" # Privilégie la performance

class ConfidenceLevel(Enum):
    """Niveaux de confiance des décisions"""
    VERY_HIGH = "very_high"    # >95% confidence
    HIGH = "high"              # 85-95% confidence
    MEDIUM = "medium"          # 70-85% confidence
    LOW = "low"                # 50-70% confidence
    VERY_LOW = "very_low"      # <50% confidence

@dataclass
class DecisionCriteria:
    """Critères de décision"""
    criteria_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    weight: float = 1.0
    threshold: float = 0.5
    measurement_unit: str = ""
    is_maximizing: bool = True  # True pour maximiser, False pour minimiser
    is_mandatory: bool = False
    evaluation_function: Optional[Callable] = None

@dataclass
class DecisionOption:
    """Option de décision"""
    option_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    action_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_impact: float = 0.0
    estimated_duration: timedelta = timedelta(minutes=0)
    risk_level: float = 0.0
    rollback_possible: bool = True
    dependencies: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionEvaluation:
    """Évaluation d'une option de décision"""
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    option_id: str = ""
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    confidence: float = 0.0
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionContext:
    """Contexte de décision"""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType = DecisionType.RESOURCE_ALLOCATION
    priority: DecisionPriority = DecisionPriority.MEDIUM
    strategy: DecisionStrategy = DecisionStrategy.BALANCED
    time_constraint: Optional[timedelta] = None
    budget_constraint: Optional[float] = None
    current_state: Dict[str, Any] = field(default_factory=dict)
    desired_state: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    stakeholders: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Decision:
    """Décision complète"""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType = DecisionType.RESOURCE_ALLOCATION
    title: str = ""
    description: str = ""
    context: DecisionContext = field(default_factory=DecisionContext)
    criteria: List[DecisionCriteria] = field(default_factory=list)
    options: List[DecisionOption] = field(default_factory=list)
    evaluations: List[DecisionEvaluation] = field(default_factory=list)
    selected_option: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: DecisionStatus = DecisionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class DecisionRule:
    """Règle de décision automatique"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    decision_type: DecisionType = DecisionType.RESOURCE_ALLOCATION
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 0
    is_active: bool = True
    confidence_threshold: float = 0.8
    success_rate: float = 0.0
    last_triggered: Optional[datetime] = None
    execution_count: int = 0

@dataclass
class DecisionEngineConfig:
    """Configuration du moteur de décision"""
    default_strategy: DecisionStrategy = DecisionStrategy.BALANCED
    auto_execution_threshold: float = 0.9
    max_concurrent_decisions: int = 10
    decision_timeout: timedelta = timedelta(hours=1)
    enable_auto_rules: bool = True
    enable_ml_optimization: bool = True
    confidence_threshold: float = 0.7
    risk_tolerance: float = 0.3
    cache_evaluations: bool = True
    evaluation_cache_ttl: timedelta = timedelta(hours=6)

class DecisionEvaluator(ABC):
    """Interface abstraite pour les évaluateurs de décision"""
    
    @abstractmethod
    async def evaluate_option(self, option: DecisionOption, 
                            criteria: List[DecisionCriteria],
                            context: DecisionContext) -> DecisionEvaluation:
        """Évalue une option selon les critères"""
        pass

class StandardDecisionEvaluator(DecisionEvaluator):
    """Évaluateur de décision standard"""
    
    async def evaluate_option(self, option: DecisionOption, 
                            criteria: List[DecisionCriteria],
                            context: DecisionContext) -> DecisionEvaluation:
        """Évalue une option selon les critères standard"""
        try:
            evaluation = DecisionEvaluation(option_id=option.option_id)
            total_weight = 0
            weighted_sum = 0
            
            for criterion in criteria:
                score = await self._evaluate_criterion(option, criterion, context)
                evaluation.criteria_scores[criterion.criteria_id] = score
                
                weighted_sum += score * criterion.weight
                total_weight += criterion.weight
            
            # Score pondéré final
            if total_weight > 0:
                evaluation.weighted_score = weighted_sum / total_weight
            
            # Évaluation des risques
            evaluation.risk_assessment = await self._assess_risks(option, context)
            
            # Calcul de la confiance
            evaluation.confidence = await self._calculate_confidence(
                evaluation.criteria_scores, evaluation.risk_assessment
            )
            
            # Génération des recommandations
            evaluation.pros, evaluation.cons = await self._generate_pros_cons(
                option, evaluation.criteria_scores
            )
            evaluation.recommendations = await self._generate_recommendations(
                option, evaluation
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate option {option.option_id}: {e}")
            return DecisionEvaluation(option_id=option.option_id)
    
    async def _evaluate_criterion(self, option: DecisionOption, 
                                criterion: DecisionCriteria,
                                context: DecisionContext) -> float:
        """Évalue un critère spécifique"""
        try:
            # Si une fonction d'évaluation personnalisée est définie
            if criterion.evaluation_function:
                return await criterion.evaluation_function(option, context)
            
            # Évaluation standard basée sur le nom du critère
            if criterion.name == "cost":
                return self._evaluate_cost(option, criterion)
            elif criterion.name == "performance_impact":
                return self._evaluate_performance_impact(option, criterion)
            elif criterion.name == "risk":
                return self._evaluate_risk(option, criterion)
            elif criterion.name == "implementation_complexity":
                return self._evaluate_complexity(option, criterion)
            elif criterion.name == "rollback_feasibility":
                return 1.0 if option.rollback_possible else 0.0
            else:
                # Évaluation générique
                return 0.5  # Score neutre par défaut
                
        except Exception as e:
            logger.error(f"❌ Failed to evaluate criterion {criterion.name}: {e}")
            return 0.0
    
    def _evaluate_cost(self, option: DecisionOption, criterion: DecisionCriteria) -> float:
        """Évalue le coût de l'option"""
        # Normaliser le coût (plus le coût est bas, meilleur le score)
        max_cost = 10000  # Coût de référence
        if criterion.is_maximizing:
            return max(0, 1 - (option.estimated_cost / max_cost))
        else:
            return min(1, option.estimated_cost / max_cost)
    
    def _evaluate_performance_impact(self, option: DecisionOption, criterion: DecisionCriteria) -> float:
        """Évalue l'impact sur les performances"""
        # Normaliser l'impact (plus l'impact est élevé, meilleur le score)
        return min(1.0, max(0.0, option.estimated_impact))
    
    def _evaluate_risk(self, option: DecisionOption, criterion: DecisionCriteria) -> float:
        """Évalue le risque de l'option"""
        # Plus le risque est faible, meilleur le score
        if criterion.is_maximizing:
            return 1.0 - min(1.0, max(0.0, option.risk_level))
        else:
            return min(1.0, max(0.0, option.risk_level))
    
    def _evaluate_complexity(self, option: DecisionOption, criterion: DecisionCriteria) -> float:
        """Évalue la complexité d'implémentation"""
        # Complexité basée sur la durée estimée et les dépendances
        duration_hours = option.estimated_duration.total_seconds() / 3600
        dependency_factor = len(option.dependencies) * 0.1
        
        complexity = min(1.0, (duration_hours / 100) + dependency_factor)
        
        if criterion.is_maximizing:
            return 1.0 - complexity
        else:
            return complexity
    
    async def _assess_risks(self, option: DecisionOption, context: DecisionContext) -> Dict[str, float]:
        """Évalue les risques associés à l'option"""
        risks = {
            'implementation_risk': option.risk_level,
            'performance_risk': 0.0,
            'security_risk': 0.0,
            'cost_risk': 0.0,
            'rollback_risk': 0.0 if option.rollback_possible else 0.8
        }
        
        # Risque de performance basé sur l'impact
        if option.estimated_impact < 0:
            risks['performance_risk'] = abs(option.estimated_impact)
        
        # Risque de coût basé sur le budget
        if context.budget_constraint and option.estimated_cost > context.budget_constraint:
            risks['cost_risk'] = min(1.0, option.estimated_cost / context.budget_constraint - 1)
        
        # Risque de sécurité basé sur le type d'action
        if option.action_type in ['configuration_change', 'security_action']:
            risks['security_risk'] = 0.3
        
        return risks
    
    async def _calculate_confidence(self, criteria_scores: Dict[str, float], 
                                  risk_assessment: Dict[str, float]) -> float:
        """Calcule la confiance dans l'évaluation"""
        try:
            # Confiance basée sur la cohérence des scores
            if not criteria_scores:
                return 0.0
            
            scores = list(criteria_scores.values())
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            # Plus la variance est faible, plus la confiance est élevée
            consistency_confidence = max(0, 1 - score_variance)
            
            # Réduire la confiance si les risques sont élevés
            avg_risk = statistics.mean(risk_assessment.values()) if risk_assessment else 0
            risk_confidence = max(0, 1 - avg_risk)
            
            # Confiance finale
            confidence = (consistency_confidence + risk_confidence) / 2
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate confidence: {e}")
            return 0.5
    
    async def _generate_pros_cons(self, option: DecisionOption, 
                                criteria_scores: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """Génère les avantages et inconvénients"""
        pros = []
        cons = []
        
        try:
            # Analyser les scores des critères
            for criteria_id, score in criteria_scores.items():
                if score > 0.7:
                    pros.append(f"High score ({score:.2f}) for criteria {criteria_id}")
                elif score < 0.3:
                    cons.append(f"Low score ({score:.2f}) for criteria {criteria_id}")
            
            # Avantages spécifiques
            if option.rollback_possible:
                pros.append("Rollback is possible")
            if option.estimated_cost < 1000:
                pros.append("Low implementation cost")
            if option.estimated_duration < timedelta(hours=1):
                pros.append("Quick implementation")
            
            # Inconvénients spécifiques
            if option.risk_level > 0.5:
                cons.append("High risk level")
            if len(option.dependencies) > 5:
                cons.append("Many dependencies")
            if not option.rollback_possible:
                cons.append("No rollback option")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate pros/cons: {e}")
        
        return pros, cons
    
    async def _generate_recommendations(self, option: DecisionOption, 
                                      evaluation: DecisionEvaluation) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        try:
            # Recommandations basées sur le score
            if evaluation.weighted_score > 0.8:
                recommendations.append("Strong candidate - recommend implementation")
            elif evaluation.weighted_score > 0.6:
                recommendations.append("Good option - consider implementation")
            elif evaluation.weighted_score > 0.4:
                recommendations.append("Average option - evaluate alternatives")
            else:
                recommendations.append("Weak option - not recommended")
            
            # Recommandations basées sur les risques
            avg_risk = statistics.mean(evaluation.risk_assessment.values()) if evaluation.risk_assessment else 0
            if avg_risk > 0.7:
                recommendations.append("High risk - implement additional safeguards")
            elif avg_risk > 0.5:
                recommendations.append("Moderate risk - monitor closely during implementation")
            
            # Recommandations basées sur la confiance
            if evaluation.confidence < 0.5:
                recommendations.append("Low confidence - gather more data before deciding")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
        
        return recommendations

class RedisDecisionEngine:
    """Moteur de décision Redis enterprise"""
    
    def __init__(self, config: DecisionEngineConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client or redis.Redis()
        self.is_running = False
        
        # Composants du moteur
        self.evaluator = StandardDecisionEvaluator()
        self.decision_queue = []  # Priority queue
        self.active_decisions = {}
        self.decision_rules = {}
        self.decision_history = []
        
        # Cache pour les évaluations
        self.evaluation_cache = {}
        
        # Métriques
        self.metrics = {
            'decisions_processed': 0,
            'decisions_executed': 0,
            'decisions_failed': 0,
            'avg_decision_time': 0,
            'success_rate': 0,
            'auto_executions': 0,
            'rule_triggers': 0,
            'last_decision': None
        }
        
        # Tâches asynchrones
        self.processing_task = None
        self.monitoring_task = None
    
    async def initialize(self) -> bool:
        """Initialise le moteur de décision"""
        try:
            logger.info("⚡ Initializing Decision Engine...")
            
            # Charger les règles de décision
            await self._load_decision_rules()
            
            # Charger l'historique des décisions
            await self._load_decision_history()
            
            # Démarrer les tâches de traitement
            await self._start_processing_tasks()
            
            self.is_running = True
            logger.info("✅ Decision Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Decision Engine: {e}")
            return False
    
    async def _load_decision_rules(self):
        """Charge les règles de décision depuis Redis"""
        try:
            keys = self.redis_client.keys("decision:rules:*")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    rule_data = json.loads(data)
                    rule = DecisionRule(**rule_data)
                    self.decision_rules[rule.rule_id] = rule
            
            logger.info(f"✅ Loaded {len(self.decision_rules)} decision rules")
            
        except Exception as e:
            logger.error(f"❌ Failed to load decision rules: {e}")
    
    async def _load_decision_history(self):
        """Charge l'historique des décisions"""
        try:
            keys = self.redis_client.keys("decision:history:*")
            for key in keys[-100:]:  # Charger les 100 dernières
                data = self.redis_client.get(key)
                if data:
                    decision_data = json.loads(data)
                    decision = Decision(**decision_data)
                    self.decision_history.append(decision)
            
            # Trier par date
            self.decision_history.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.info(f"✅ Loaded {len(self.decision_history)} historical decisions")
            
        except Exception as e:
            logger.error(f"❌ Failed to load decision history: {e}")
    
    async def _start_processing_tasks(self):
        """Démarre les tâches de traitement"""
        self.processing_task = asyncio.create_task(self._decision_processing_loop())
        self.monitoring_task = asyncio.create_task(self._decision_monitoring_loop())
    
    async def get_engine_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du moteur"""
        return {
            'decisions_processed': self.metrics['decisions_processed'],
            'decisions_executed': self.metrics['decisions_executed'],
            'decisions_failed': self.metrics['decisions_failed'],
            'avg_decision_time': self.metrics['avg_decision_time'],
            'success_rate': self.metrics['success_rate'],
            'auto_executions': self.metrics['auto_executions'],
            'rule_triggers': self.metrics['rule_triggers'],
            'last_decision': self.metrics['last_decision'].isoformat() if self.metrics['last_decision'] else None,
            'queue_size': len(self.decision_queue),
            'active_decisions': len(self.active_decisions),
            'total_rules': len(self.decision_rules),
            'cache_size': len(self.evaluation_cache),
            'is_running': self.is_running
        }
    
    async def shutdown(self):
        """Arrête le moteur de décision"""
        try:
            logger.info("🛑 Shutting down Decision Engine...")
            
            self.is_running = False
            
            # Arrêter les tâches
            if self.processing_task and not self.processing_task.done():
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Sauvegarder les décisions actives
            for decision in self.active_decisions.values():
                await self._store_decision(decision)
            
            logger.info("✅ Decision Engine shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Factory function pour créer le moteur de décision
async def create_decision_engine(
    config: Optional[DecisionEngineConfig] = None,
    redis_client: Optional[redis.Redis] = None
) -> RedisDecisionEngine:
    """Crée et initialise un moteur de décision"""
    
    if config is None:
        config = DecisionEngineConfig()
    
    engine = RedisDecisionEngine(config, redis_client)
    
    if await engine.initialize():
        return engine
    else:
        raise RuntimeError("Failed to initialize Decision Engine")

__all__ = [
    'RedisDecisionEngine',
    'DecisionEngineConfig',
    'Decision',
    'DecisionContext',
    'DecisionCriteria',
    'DecisionOption',
    'DecisionEvaluation',
    'DecisionRule',
    'DecisionType',
    'DecisionPriority',
    'DecisionStatus',
    'DecisionStrategy',
    'ConfidenceLevel',
    'DecisionEvaluator',
    'StandardDecisionEvaluator',
    'create_decision_engine'
]
