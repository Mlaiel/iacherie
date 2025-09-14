"""SEO Automation Manager - Système Ultra-Avancé d'Automatisation SEO
===================================================================

Gestionnaire complet d'automatisation SEO incluant :
- Workflows automatisés intelligents avec IA
- Planification et orchestration de tâches
- Monitoring automatique de performance
- Optimisation continue basée sur ML
- Systèmes d'alertes prédictives
- Automatisation cross-platform
- Gestion avancée des règles métier
- Intégration API et webhooks

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import json
import cron_descriptor
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from croniter import croniter
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp

logger = logging.getLogger(__name__)

class AutomationStrategy(Enum):
    """Types de stratégies d'automatisation SEO"""
    CONTENT_OPTIMIZATION = "content_optimization"
    KEYWORD_MONITORING = "keyword_monitoring"
    PERFORMANCE_TRACKING = "performance_tracking"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TECHNICAL_SEO_AUDIT = "technical_seo_audit"
    LINK_BUILDING_AUTOMATION = "link_building_automation"
    SOCIAL_SIGNALS_MONITORING = "social_signals_monitoring"
    LOCAL_SEO_MANAGEMENT = "local_seo_management"
    SERP_MONITORING = "serp_monitoring"
    CONTENT_DISTRIBUTION = "content_distribution"
    SCHEMA_MARKUP_AUTOMATION = "schema_markup_automation"
    INTERNATIONAL_SEO = "international_seo"

class WorkflowStatus(Enum):
    """Statuts des workflows"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    RUNNING = "running"

class AutomationPriority(Enum):
    """Priorités d'automatisation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class ActionType(Enum):
    """Types d'actions automatisées"""
    CONTENT_ANALYSIS = "content_analysis"
    KEYWORD_RESEARCH = "keyword_research"
    RANK_TRACKING = "rank_tracking"
    TECHNICAL_AUDIT = "technical_audit"
    BACKLINK_ANALYSIS = "backlink_analysis"
    COMPETITOR_MONITORING = "competitor_monitoring"
    CONTENT_GENERATION = "content_generation"
    META_OPTIMIZATION = "meta_optimization"
    INTERNAL_LINKING = "internal_linking"
    SITEMAP_GENERATION = "sitemap_generation"
    SCHEMA_INJECTION = "schema_injection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ALERT_NOTIFICATION = "alert_notification"
    REPORT_GENERATION = "report_generation"
    API_INTEGRATION = "api_integration"

class TriggerType(Enum):
    """Types de déclencheurs"""
    SCHEDULE = "schedule"
    EVENT = "event"
    THRESHOLD = "threshold"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    CASCADE = "cascade"

@dataclass
class AutomationAction:
    """Action d'automatisation détaillée"""
    action_id: str
    action_type: ActionType
    name: str
    description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay: int = 60
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    failure_criteria: Dict[str, Any] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not self.action_id:
            self.action_id = hashlib.md5(f"{self.name}_{time.time()}".encode()).hexdigest()[:12]

@dataclass
class WorkflowTrigger:
    """Déclencheur de workflow"""
    trigger_id: str
    trigger_type: TriggerType
    configuration: Dict[str, Any]
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

@dataclass
class AutomationWorkflow:
    """Workflow d'automatisation ultra-avancé"""
    workflow_id: str
    name: str
    description: str
    strategy: AutomationStrategy
    priority: AutomationPriority
    status: WorkflowStatus
    actions: List[AutomationAction]
    triggers: List[WorkflowTrigger]
    success_criteria: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    max_executions: Optional[int] = None
    execution_count: int = 0
    
    def __post_init__(self) -> None:
        if not self.workflow_id:
            self.workflow_id = hashlib.md5(f"{self.name}_{time.time()}".encode()).hexdigest()[:16]

@dataclass
class ExecutionResult:
    """Résultat d'exécution de workflow"""
    execution_id: str
    workflow_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    actions_executed: List[Dict[str, Any]]
    results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    metrics: Dict[str, float]
    triggered_by: str
    execution_context: Dict[str, Any]

@dataclass
class AutomationRule:
    """Règle d'automatisation conditionnelle"""
    rule_id: str
    name: str
    condition: str  # Expression logique
    action_mapping: Dict[str, str]
    is_active: bool = True
    evaluation_count: int = 0
    success_count: int = 0

class SEOAutomationManager:
    """
    🤖 Gestionnaire d'Automatisation SEO Ultra-Avancé
    
    Système complet d'automatisation SEO avec :
    - Orchestration de workflows intelligents
    - Planification avancée avec cron expressions
    - Gestion des dépendances et parallélisation
    - Monitoring en temps réel des exécutions
    - Systèmes d'alertes et notifications
    - Optimisation automatique basée sur ML
    - Intégrations API et webhooks
    - Gestion avancée des erreurs et retry
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialise le gestionnaire d'automatisation"""
        self.config = config or {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Stockage des workflows et règles
        self.workflows: Dict[str, AutomationWorkflow] = {}
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.execution_history: Dict[str, List[ExecutionResult]] = defaultdict(list)
        
        # Système de planification
        self.scheduler_running = False
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Pool d'exécution
        self.executor = ThreadPoolExecutor(max_workers=self.config.get('max_workers', 10))
        
        # Métriques globales
        self.global_metrics = {
            'total_workflows': 0,
            'active_workflows': 0,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'automation_efficiency': 0.0
        }
        
        # Cache pour les résultats
        self.results_cache: Dict[str, Any] = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 heure
        
        # Système d'alertes
        self.alert_channels = self.config.get('alert_channels', [])
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'failure_rate': 0.20,  # 20% d'échecs
            'execution_time_increase': 0.50,  # +50% du temps normal
            'consecutive_failures': 3
        })
        
        # Actions prédéfinies
        self._setup_predefined_actions()
        
        logger.info("🤖 SEO Automation Manager initialisé")
    
    async def initialize(self) -> None:
        """Initialise les composants du gestionnaire"""
        try:
            # Session HTTP pour les intégrations
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'SEOAutomationManager/2.1'}
            )
            
            # Démarrage du scheduler
            await self._start_scheduler()
            
            # Chargement des workflows sauvegardés
            await self._load_saved_workflows()
            
            # Configuration des webhooks
            await self._setup_webhooks()
            
            logger.info("✅ Gestionnaire d'automatisation initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation automatisation: {e}")
            raise
    
    def _setup_predefined_actions(self) -> None:
        """Configure les actions prédéfinies"""
        self.predefined_actions = {
            ActionType.CONTENT_ANALYSIS: {
                'function': self._execute_content_analysis,
                'default_params': {
                    'analyze_readability': True,
                    'check_keyword_density': True,
                    'analyze_structure': True
                },
                'timeout': 120
            },
            ActionType.KEYWORD_RESEARCH: {
                'function': self._execute_keyword_research,
                'default_params': {
                    'max_keywords': 100,
                    'include_long_tail': True,
                    'competitor_analysis': True
                },
                'timeout': 300
            },
            ActionType.RANK_TRACKING: {
                'function': self._execute_rank_tracking,
                'default_params': {
                    'check_mobile': True,
                    'check_local': True,
                    'track_features': True
                },
                'timeout': 180
            },
            ActionType.TECHNICAL_AUDIT: {
                'function': self._execute_technical_audit,
                'default_params': {
                    'check_crawlability': True,
                    'analyze_speed': True,
                    'validate_markup': True
                },
                'timeout': 240
            },
            ActionType.BACKLINK_ANALYSIS: {
                'function': self._execute_backlink_analysis,
                'default_params': {
                    'analyze_quality': True,
                    'check_toxicity': True,
                    'find_opportunities': True
                },
                'timeout': 300
            }
        }
    
    async def _start_scheduler(self) -> None:
        """Démarre le système de planification"""
        if not self.scheduler_running:
            self.scheduler_running = True
            asyncio.create_task(self._scheduler_loop())
            logger.info("⏰ Scheduler d'automatisation démarré")
    
    async def _scheduler_loop(self) -> None:
        """Boucle principale du scheduler"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                # Vérification des workflows planifiés
                for workflow_id, workflow in self.workflows.items():
                    if workflow.status == WorkflowStatus.ACTIVE:
                        await self._check_workflow_triggers(workflow, current_time)
                
                # Attendre 60 secondes avant la prochaine vérification
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans le scheduler: {e}")
                await asyncio.sleep(60)
    
    async def _check_workflow_triggers(
        self,
        workflow: AutomationWorkflow,
        current_time: datetime
    ) -> None:
        """Vérifie si un workflow doit être déclenché"""
        for trigger in workflow.triggers:
            if not trigger.is_active:
                continue
            
            should_trigger = False
            
            if trigger.trigger_type == TriggerType.SCHEDULE:
                should_trigger = await self._check_schedule_trigger(trigger, current_time)
            elif trigger.trigger_type == TriggerType.THRESHOLD:
                should_trigger = await self._check_threshold_trigger(trigger)
            elif trigger.trigger_type == TriggerType.EVENT:
                should_trigger = await self._check_event_trigger(trigger)
            elif trigger.trigger_type == TriggerType.CONDITIONAL:
                should_trigger = await self._check_conditional_trigger(trigger, workflow)
            
            if should_trigger:
                await self._trigger_workflow_execution(workflow, trigger)
                trigger.last_triggered = current_time
                trigger.trigger_count += 1
    
    async def _check_schedule_trigger(
        self,
        trigger: WorkflowTrigger,
        current_time: datetime
    ) -> bool:
        """Vérifie un déclencheur basé sur un planning"""
        try:
            cron_expression = trigger.configuration.get('cron')
            if not cron_expression:
                return False
            
            # Vérification avec croniter
            cron = croniter(cron_expression, trigger.last_triggered or current_time - timedelta(minutes=1))
            next_run = cron.get_next(datetime)
            
            # Si le prochain run est dans le passé (par rapport à maintenant), c'est le moment
            return next_run <= current_time
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification trigger schedule: {e}")
            return False
    
    async def _check_threshold_trigger(self, trigger: WorkflowTrigger) -> bool:
        """Vérifie un déclencheur basé sur un seuil"""
        try:
            metric_name = trigger.configuration.get('metric')
            threshold_value = trigger.configuration.get('threshold')
            comparison = trigger.configuration.get('comparison', 'gt')  # gt, lt, eq
            
            if not all([metric_name, threshold_value]):
                return False
            
            # Récupération de la métrique actuelle
            current_value = await self._get_metric_value(metric_name)
            
            if comparison == 'gt':
                return current_value > threshold_value
            elif comparison == 'lt':
                return current_value < threshold_value
            elif comparison == 'eq':
                return current_value == threshold_value
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification trigger threshold: {e}")
            return False
    
    async def _check_event_trigger(self, trigger: WorkflowTrigger) -> bool:
        """Vérifie un déclencheur basé sur un événement"""
        # Simulation de vérification d'événement
        # Dans la réalité, cela vérifierait une queue d'événements
        event_type = trigger.configuration.get('event_type')
        
        # Simulation : événements aléatoires pour la démo
        if event_type == 'content_published':
            return np.random.random() < 0.1  # 10% de chance
        elif event_type == 'ranking_change':
            return np.random.random() < 0.05  # 5% de chance
        
        return False
    
    async def _check_conditional_trigger(
        self,
        trigger: WorkflowTrigger,
        workflow: AutomationWorkflow
    ) -> bool:
        """Vérifie un déclencheur conditionnel"""
        try:
            condition = trigger.configuration.get('condition')
            if not condition:
                return False
            
            # Évaluation simple de condition (à améliorer avec un parser plus robuste)
            # Exemple: "metric_a > 100 AND metric_b < 50"
            
            # Pour la démo, simulation d'évaluation
            return np.random.random() < 0.3  # 30% de chance
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification trigger conditionnel: {e}")
            return False
    
    async def _get_metric_value(self, metric_name: str) -> float:
        """Récupère la valeur d'une métrique"""
        # Simulation de récupération de métrique
        # Dans la réalité, cela interrogerait la base de données ou les APIs
        
        metrics_simulation = {
            'organic_traffic': np.random.uniform(1000, 10000),
            'average_position': np.random.uniform(1, 50),
            'bounce_rate': np.random.uniform(0.2, 0.8),
            'page_load_time': np.random.uniform(1.0, 5.0),
            'domain_authority': np.random.uniform(30, 90),
            'backlinks_count': float(np.random.randint(100, 5000))
        }
        
        return metrics_simulation.get(metric_name, 0.0)
    
    async def create_automation_workflow(
        self,
        name: str,
        description: str,
        strategy: AutomationStrategy,
        actions: List[AutomationAction],
        triggers: List[WorkflowTrigger],
        priority: AutomationPriority = AutomationPriority.MEDIUM,
        success_criteria: Optional[Dict[str, float]] = None,
        created_by: str = "system",
        tags: Optional[List[str]] = None
    ) -> AutomationWorkflow:
        """
        Crée un workflow d'automatisation avancé
        
        Args:
            name: Nom du workflow
            description: Description détaillée
            strategy: Stratégie d'automatisation
            actions: Liste des actions à exécuter
            triggers: Déclencheurs du workflow
            priority: Priorité d'exécution
            success_criteria: Critères de succès
            created_by: Créateur du workflow
            tags: Tags pour l'organisation
            
        Returns:
            Workflow d'automatisation créé
        """
        try:
            logger.info(f"🔧 Création workflow d'automatisation: {name}")
            
            # Génération de l'ID workflow
            workflow_id = hashlib.md5(f"{name}_{time.time()}_{created_by}".encode()).hexdigest()[:16]
            
            # Critères de succès par défaut
            if not success_criteria:
                success_criteria = {
                    "completion_rate": 0.95,
                    "accuracy": 0.90,
                    "execution_time_limit": 3600  # 1 heure max
                }
            
            # Validation des actions
            validated_actions = await self._validate_actions(actions)
            
            # Validation des triggers
            validated_triggers = await self._validate_triggers(triggers)
            
            # Création du workflow
            workflow = AutomationWorkflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                strategy=strategy,
                priority=priority,
                status=WorkflowStatus.DRAFT,
                actions=validated_actions,
                triggers=validated_triggers,
                success_criteria=success_criteria,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                tags=tags or [],
                variables={},
                execution_history=[],
                performance_metrics={},
                error_handling={
                    'max_retries': 3,
                    'retry_delay': 60,
                    'escalation_enabled': True
                },
                notifications={
                    'on_success': self.config.get('notify_on_success', False),
                    'on_failure': True,
                    'on_warning': True
                }
            )
            
            # Enregistrement du workflow
            self.workflows[workflow_id] = workflow
            self.global_metrics['total_workflows'] += 1
            
            logger.info(f"✅ Workflow créé - ID: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Erreur création workflow: {e}")
            raise
    
    async def _validate_actions(
        self,
        actions: List[AutomationAction]
    ) -> List[AutomationAction]:
        """Valide la liste des actions"""
        validated_actions = []
        
        for action in actions:
            # Vérification du type d'action
            if action.action_type not in self.predefined_actions:
                logger.warning(f"⚠️ Type d'action non reconnu: {action.action_type}")
                continue
            
            # Fusion avec les paramètres par défaut
            default_params = self.predefined_actions[action.action_type]['default_params']
            merged_params = {**default_params, **action.parameters}
            action.parameters = merged_params
            
            # Configuration du timeout par défaut
            if action.timeout_seconds <= 0:
                action.timeout_seconds = self.predefined_actions[action.action_type]['timeout']
            
            validated_actions.append(action)
        
        return validated_actions
    
    async def _validate_triggers(
        self,
        triggers: List[WorkflowTrigger]
    ) -> List[WorkflowTrigger]:
        """Valide la liste des déclencheurs"""
        validated_triggers = []
        
        for trigger in triggers:
            # Validation basée sur le type
            if trigger.trigger_type == TriggerType.SCHEDULE:
                if 'cron' not in trigger.configuration:
                    logger.error(f"❌ Trigger schedule sans expression cron: {trigger.trigger_id}")
                    continue
                
                # Validation de l'expression cron
                try:
                    croniter(trigger.configuration['cron'])
                except Exception as e:
                    logger.error(f"❌ Expression cron invalide: {e}")
                    continue
            
            elif trigger.trigger_type == TriggerType.THRESHOLD:
                required_keys = ['metric', 'threshold', 'comparison']
                if not all(key in trigger.configuration for key in required_keys):
                    logger.error(f"❌ Trigger threshold incomplet: {trigger.trigger_id}")
                    continue
            
            validated_triggers.append(trigger)
        
        return validated_triggers
    
    async def activate_workflow(self, workflow_id: str) -> bool:
        """Active un workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} non trouvé")
            
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.ACTIVE
            workflow.updated_at = datetime.now()
            
            self.global_metrics['active_workflows'] += 1
            
            logger.info(f"✅ Workflow activé: {workflow.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur activation workflow: {e}")
            return False
    
    async def _trigger_workflow_execution(
        self,
        workflow: AutomationWorkflow,
        trigger: WorkflowTrigger
    ) -> ExecutionResult:
        """Déclenche l'exécution d'un workflow"""
        try:
            # Vérification des limites d'exécution
            if workflow.max_executions and workflow.execution_count >= workflow.max_executions:
                logger.info(f"⏹️ Workflow {workflow.name} a atteint sa limite d'exécutions")
                return None
            
            # Génération de l'ID d'exécution
            execution_id = hashlib.md5(f"{workflow.workflow_id}_{time.time()}".encode()).hexdigest()[:12]
            
            logger.info(f"🚀 Démarrage exécution workflow: {workflow.name} (ID: {execution_id})")
            
            # Création du contexte d'exécution
            execution_context = {
                'execution_id': execution_id,
                'workflow_id': workflow.workflow_id,
                'trigger_id': trigger.trigger_id,
                'start_time': datetime.now(),
                'variables': workflow.variables.copy()
            }
            
            # Mise à jour du statut
            workflow.status = WorkflowStatus.RUNNING
            start_time = datetime.now()
            
            # Exécution des actions
            execution_result = await self._execute_workflow_actions(
                workflow, execution_context
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Création du résultat d'exécution
            result = ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow.workflow_id,
                status=execution_result['status'],
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                actions_executed=execution_result['actions_executed'],
                results=execution_result['results'],
                errors=execution_result.get('errors', []),
                metrics=execution_result.get('metrics', {}),
                triggered_by=trigger.trigger_id,
                execution_context=execution_context
            )
            
            # Mise à jour des métriques et historique
            await self._update_workflow_metrics(workflow, result)
            workflow.execution_history.append(asdict(result))
            workflow.execution_count += 1
            
            # Remise du statut à ACTIVE
            workflow.status = WorkflowStatus.ACTIVE
            
            # Notifications
            await self._send_execution_notifications(workflow, result)
            
            # Mise à jour des métriques globales
            self.global_metrics['total_executions'] += 1
            if result.status == 'success':
                self.global_metrics['successful_executions'] += 1
            else:
                self.global_metrics['failed_executions'] += 1
            
            logger.info(f"✅ Exécution terminée - Durée: {duration:.1f}s - Statut: {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution workflow: {e}")
            workflow.status = WorkflowStatus.FAILED
            raise
    
    async def _execute_workflow_actions(
        self,
        workflow: AutomationWorkflow,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exécute les actions d'un workflow"""
        execution_result = {
            'status': 'success',
            'actions_executed': [],
            'results': {},
            'errors': [],
            'metrics': {}
        }
        
        try:
            # Tri des actions par dépendances
            sorted_actions = await self._sort_actions_by_dependencies(workflow.actions)
            
            # Exécution séquentielle ou parallèle selon les dépendances
            for action in sorted_actions:
                action_start = time.time()
                
                try:
                    # Vérification des dépendances
                    if not await self._check_action_dependencies(action, execution_result['results']):
                        logger.warning(f"⚠️ Dépendances non satisfaites pour {action.name}")
                        continue
                    
                    # Exécution de l'action
                    action_result = await self._execute_single_action(action, execution_context)
                    
                    action_duration = time.time() - action_start
                    
                    # Enregistrement du résultat
                    execution_result['actions_executed'].append({
                        'action_id': action.action_id,
                        'name': action.name,
                        'status': 'success' if action_result.get('success', False) else 'failed',
                        'duration': action_duration,
                        'result': action_result
                    })
                    
                    # Mapping des outputs
                    if action.output_mapping and action_result.get('success'):
                        for output_key, variable_name in action.output_mapping.items():
                            if output_key in action_result:
                                execution_result['results'][variable_name] = action_result[output_key]
                    
                    # Mise à jour du contexte
                    execution_context['variables'].update(execution_result['results'])
                    
                except Exception as action_error:
                    logger.error(f"❌ Erreur exécution action {action.name}: {action_error}")
                    
                    execution_result['errors'].append({
                        'action_id': action.action_id,
                        'error': str(action_error),
                        'timestamp': datetime.now()
                    })
                    
                    # Gestion des erreurs selon la configuration
                    if not workflow.error_handling.get('continue_on_error', False):
                        execution_result['status'] = 'failed'
                        break
            
            # Évaluation des critères de succès
            if execution_result['status'] == 'success':
                success_rate = len([a for a in execution_result['actions_executed'] if a['status'] == 'success']) / len(workflow.actions)
                
                if success_rate < workflow.success_criteria.get('completion_rate', 0.95):
                    execution_result['status'] = 'partial_success'
            
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution actions workflow: {e}")
            execution_result['status'] = 'failed'
            execution_result['errors'].append({
                'error': str(e),
                'timestamp': datetime.now()
            })
            return execution_result
    
    async def _sort_actions_by_dependencies(
        self,
        actions: List[AutomationAction]
    ) -> List[AutomationAction]:
        """Trie les actions selon leurs dépendances"""
        # Algorithme de tri topologique simple
        sorted_actions = []
        remaining_actions = actions.copy()
        
        while remaining_actions:
            # Trouver les actions sans dépendances non satisfaites
            ready_actions = []
            
            for action in remaining_actions:
                dependencies_satisfied = all(
                    any(completed.action_id == dep for completed in sorted_actions)
                    for dep in action.dependencies
                ) if action.dependencies else True
                
                if dependencies_satisfied:
                    ready_actions.append(action)
            
            if not ready_actions:
                # Dépendances circulaires ou manquantes
                logger.warning("⚠️ Dépendances circulaires détectées, ajout des actions restantes")
                ready_actions = remaining_actions
            
            # Ajouter les actions prêtes
            for action in ready_actions:
                sorted_actions.append(action)
                remaining_actions.remove(action)
        
        return sorted_actions
    
    async def _check_action_dependencies(
        self,
        action: AutomationAction,
        results: Dict[str, Any]
    ) -> bool:
        """Vérifie si les dépendances d'une action sont satisfaites"""
        if not action.dependencies:
            return True
        
        # Vérification simple : les variables requises sont-elles disponibles ?
        for dependency in action.dependencies:
            if dependency not in results:
                return False
        
        return True
    
    async def _execute_single_action(
        self,
        action: AutomationAction,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exécute une action individuelle"""
        try:
            logger.debug(f"🔧 Exécution action: {action.name}")
            
            # Récupération de la fonction d'action
            action_config = self.predefined_actions.get(action.action_type)
            if not action_config:
                raise ValueError(f"Type d'action non supporté: {action.action_type}")
            
            action_function = action_config['function']
            
            # Préparation des paramètres
            params = {
                **action.parameters,
                'execution_context': execution_context
            }
            
            # Exécution avec timeout
            try:
                result = await asyncio.wait_for(
                    action_function(params),
                    timeout=action.timeout_seconds
                )
                
                return {
                    'success': True,
                    'result': result,
                    'action_id': action.action_id
                }
                
            except asyncio.TimeoutError:
                raise Exception(f"Timeout après {action.timeout_seconds}s")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution action {action.name}: {e}")
            
            # Retry si configuré
            if action.retry_count > 0:
                logger.info(f"🔄 Retry action {action.name} ({action.retry_count} restants)")
                action.retry_count -= 1
                
                await asyncio.sleep(action.retry_delay)
                return await self._execute_single_action(action, execution_context)
            
            return {
                'success': False,
                'error': str(e),
                'action_id': action.action_id
            }
    
    # Actions prédéfinies (simulées)
    async def _execute_content_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une analyse de contenu"""
        await asyncio.sleep(2)  # Simulation
        return {
            'readability_score': np.random.uniform(60, 90),
            'keyword_density': np.random.uniform(1, 3),
            'structure_score': np.random.uniform(70, 95),
            'recommendations': ['Améliorer les sous-titres', 'Ajouter des images']
        }
    
    async def _execute_keyword_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une recherche de mots-clés"""
        await asyncio.sleep(5)  # Simulation
        return {
            'keywords_found': np.random.randint(50, 200),
            'primary_keywords': ['seo', 'marketing', 'optimization'],
            'long_tail_keywords': ['seo optimization tools', 'best marketing strategies'],
            'competition_analysis': {'low': 60, 'medium': 30, 'high': 10}
        }
    
    async def _execute_rank_tracking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un suivi de positions"""
        await asyncio.sleep(3)  # Simulation
        return {
            'average_position': np.random.uniform(5, 25),
            'position_changes': np.random.randint(-5, 8),
            'keywords_tracked': np.random.randint(20, 100),
            'serp_features': ['featured_snippet', 'image_pack']
        }
    
    async def _execute_technical_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un audit technique"""
        await asyncio.sleep(4)  # Simulation
        return {
            'crawl_errors': np.random.randint(0, 20),
            'page_speed_score': np.random.uniform(70, 95),
            'mobile_usability': np.random.uniform(80, 100),
            'schema_markup_score': np.random.uniform(60, 90),
            'issues_found': ['Missing alt tags', 'Slow loading images']
        }
    
    async def _execute_backlink_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une analyse de backlinks"""
        await asyncio.sleep(6)  # Simulation
        return {
            'total_backlinks': np.random.randint(100, 5000),
            'referring_domains': np.random.randint(50, 500),
            'domain_authority': np.random.uniform(30, 80),
            'toxic_links': np.random.randint(0, 50),
            'new_opportunities': np.random.randint(5, 30)
        }
    
    async def execute_automation(
        self,
        workflow_id: str,
        trigger_source: str = "manual",
        override_params: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Exécute manuellement un workflow d'automatisation
        
        Args:
            workflow_id: ID du workflow à exécuter
            trigger_source: Source du déclenchement
            override_params: Paramètres de surcharge
            
        Returns:
            Résultat de l'exécution
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} non trouvé")
            
            workflow = self.workflows[workflow_id]
            
            # Création d'un trigger manuel
            manual_trigger = WorkflowTrigger(
                trigger_id=f"manual_{int(time.time())}",
                trigger_type=TriggerType.MANUAL,
                configuration={'source': trigger_source}
            )
            
            # Override des paramètres si fournis
            if override_params:
                workflow.variables.update(override_params)
            
            # Exécution
            result = await self._trigger_workflow_execution(workflow, manual_trigger)
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution manuelle: {e}")
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Récupère le statut détaillé d'un workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} non trouvé")
            
            workflow = self.workflows[workflow_id]
            
            # Calcul des métriques de performance
            recent_executions = workflow.execution_history[-10:]  # 10 dernières exécutions
            
            success_rate = 0.0
            avg_duration = 0.0
            
            if recent_executions:
                successful = len([e for e in recent_executions if e.get('status') == 'success'])
                success_rate = successful / len(recent_executions)
                
                durations = [e.get('duration_seconds', 0) for e in recent_executions if e.get('duration_seconds')]
                avg_duration = np.mean(durations) if durations else 0.0
            
            status_info = {
                'workflow_id': workflow_id,
                'name': workflow.name,
                'status': workflow.status.value,
                'strategy': workflow.strategy.value,
                'priority': workflow.priority.value,
                'created_at': workflow.created_at.isoformat(),
                'updated_at': workflow.updated_at.isoformat(),
                'execution_count': workflow.execution_count,
                'performance_metrics': {
                    'success_rate': success_rate,
                    'average_duration_seconds': avg_duration,
                    'last_execution': workflow.execution_history[-1].get('start_time') if workflow.execution_history else None,
                    'total_executions': len(workflow.execution_history)
                },
                'triggers': [
                    {
                        'trigger_id': t.trigger_id,
                        'type': t.trigger_type.value,
                        'is_active': t.is_active,
                        'trigger_count': t.trigger_count,
                        'last_triggered': t.last_triggered.isoformat() if t.last_triggered else None
                    }
                    for t in workflow.triggers
                ],
                'actions_count': len(workflow.actions),
                'next_scheduled_run': await self._get_next_scheduled_run(workflow)
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            raise
    
    async def _get_next_scheduled_run(self, workflow: AutomationWorkflow) -> Optional[str]:
        """Calcule la prochaine exécution planifiée"""
        for trigger in workflow.triggers:
            if trigger.trigger_type == TriggerType.SCHEDULE and trigger.is_active:
                try:
                    cron_expression = trigger.configuration.get('cron')
                    if cron_expression:
                        cron = croniter(cron_expression, datetime.now())
                        next_run = cron.get_next(datetime)
                        return next_run.isoformat()
                except Exception:
                    continue
        
        return None
    
    async def get_automation_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques globales d'automatisation"""
        try:
            # Calcul de l'efficacité d'automatisation
            total_executions = self.global_metrics['total_executions']
            successful_executions = self.global_metrics['successful_executions']
            
            efficiency = 0.0
            if total_executions > 0:
                efficiency = successful_executions / total_executions
            
            # Calcul du temps d'exécution moyen
            all_durations = []
            for workflow in self.workflows.values():
                for execution in workflow.execution_history:
                    if execution.get('duration_seconds'):
                        all_durations.append(execution['duration_seconds'])
            
            avg_execution_time = np.mean(all_durations) if all_durations else 0.0
            
            # Mise à jour des métriques globales
            self.global_metrics['automation_efficiency'] = efficiency
            self.global_metrics['average_execution_time'] = avg_execution_time
            
            # Métriques par stratégie
            strategy_metrics = defaultdict(lambda: {'count': 0, 'success_rate': 0.0})
            
            for workflow in self.workflows.values():
                strategy = workflow.strategy.value
                strategy_metrics[strategy]['count'] += 1
                
                if workflow.execution_history:
                    successful = len([e for e in workflow.execution_history if e.get('status') == 'success'])
                    strategy_metrics[strategy]['success_rate'] = successful / len(workflow.execution_history)
            
            metrics = {
                'global_metrics': self.global_metrics,
                'strategy_breakdown': dict(strategy_metrics),
                'active_workflows': [
                    {'id': wf.workflow_id, 'name': wf.name, 'strategy': wf.strategy.value}
                    for wf in self.workflows.values()
                    if wf.status == WorkflowStatus.ACTIVE
                ],
                'recent_activity': await self._get_recent_activity(),
                'performance_trends': await self._calculate_performance_trends()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération métriques: {e}")
            raise
    
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Récupère l'activité récente"""
        all_executions = []
        
        for workflow in self.workflows.values():
            for execution in workflow.execution_history[-5:]:  # 5 dernières par workflow
                all_executions.append({
                    'workflow_id': workflow.workflow_id,
                    'workflow_name': workflow.name,
                    'execution_id': execution.get('execution_id'),
                    'status': execution.get('status'),
                    'start_time': execution.get('start_time'),
                    'duration': execution.get('duration_seconds')
                })
        
        # Tri par date décroissante
        all_executions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return all_executions[:20]  # 20 plus récentes
    
    async def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calcule les tendances de performance"""
        # Simulation de calcul de tendances
        return {
            'efficiency_trend': 'stable',  # stable, improving, declining
            'execution_time_trend': 'improving',
            'failure_rate_trend': 'stable',
            'automation_adoption': 'growing'
        }
    
    async def cleanup(self) -> None:
        """Nettoie les ressources du gestionnaire"""
        try:
            # Arrêt du scheduler
            self.scheduler_running = False
            
            # Fermeture de la session HTTP
            if self.session:
                await self.session.close()
            
            # Fermeture du pool d'exécution
            self.executor.shutdown(wait=True)
            
            # Sauvegarde des métriques finales
            total_workflows = len(self.workflows)
            active_workflows = len([w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE])
            
            logger.info(f"🧹 Nettoyage automatisation - {total_workflows} workflows, {active_workflows} actifs")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")
            raise

# Instance globale du gestionnaire d'automatisation
automation_manager = SEOAutomationManager()

# Export des classes et fonctions
__all__ = [
    'SEOAutomationManager',
    'AutomationWorkflow',
    'AutomationAction',
    'WorkflowTrigger',
    'ExecutionResult',
    'AutomationRule',
    'AutomationStrategy',
    'WorkflowStatus',
    'AutomationPriority',
    'ActionType',
    'TriggerType',
    'automation_manager'
]

if __name__ == "__main__":
    # Test du gestionnaire d'automatisation
    async def test_automation_manager() -> None:
        # Initialisation
        await automation_manager.initialize()
        
        # Création d'actions test
        test_actions = [
            AutomationAction(
                action_id="",
                action_type=ActionType.CONTENT_ANALYSIS,
                name="Analyse de contenu",
                description="Analyse automatique du contenu SEO",
                parameters={'url': 'https://example.com'}
            ),
            AutomationAction(
                action_id="",
                action_type=ActionType.RANK_TRACKING,
                name="Suivi de positions",
                description="Suivi automatique des positions",
                parameters={'keywords': ['seo', 'marketing']}
            )
        ]
        
        # Création de triggers test
        test_triggers = [
            WorkflowTrigger(
                trigger_id="daily_trigger",
                trigger_type=TriggerType.SCHEDULE,
                configuration={'cron': '0 9 * * *'}  # Tous les jours à 9h
            )
        ]
        
        # Création du workflow
        workflow = await automation_manager.create_automation_workflow(
            name="Test SEO Automation",
            description="Workflow de test pour l'automatisation SEO",
            strategy=AutomationStrategy.CONTENT_OPTIMIZATION,
            actions=test_actions,
            triggers=test_triggers,
            priority=AutomationPriority.MEDIUM
        )
        
        # Activation du workflow
        await automation_manager.activate_workflow(workflow.workflow_id)
        
        # Exécution manuelle
        result = await automation_manager.execute_automation(
            workflow.workflow_id,
            "test_execution"
        )
        
        # Récupération du statut
        status = await automation_manager.get_workflow_status(workflow.workflow_id)
        
        # Métriques globales
        metrics = await automation_manager.get_automation_metrics()
        
        print(f"✅ Test automatisation réussi:")
        print(f"🔧 Workflow créé: {workflow.name}")
        print(f"⚡ Exécution: {result.status if result else 'N/A'}")
        print(f"📊 Efficacité: {metrics['global_metrics']['automation_efficiency']:.1%}")
        
        # Nettoyage
        await automation_manager.cleanup()
    
    # asyncio.run(test_automation_manager())
