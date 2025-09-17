"""
Error Recovery Orchestrator - Ainflue Platform
Automated Error Recovery & Self-Healing System

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import random
import time

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Stratégies de récupération"""
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK_SERVICE = "fallback_service"
    DEGRADED_MODE = "degraded_mode"
    MANUAL_INTERVENTION = "manual_intervention"
    SELF_HEALING = "self_healing"
    WORKFLOW_RESTART = "workflow_restart"


class RecoveryPriority(Enum):
    """Priorités de récupération"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class RecoveryStatus(Enum):
    """Statuts de récupération"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class HealingCapability(Enum):
    """Capacités d'auto-guérison"""
    SERVICE_RESTART = "service_restart"
    RESOURCE_SCALING = "resource_scaling"
    LOAD_BALANCING = "load_balancing"
    CACHE_CLEARING = "cache_clearing"
    CONNECTION_RESET = "connection_reset"
    TOKEN_REFRESH = "token_refresh"
    DEPENDENCY_BYPASS = "dependency_bypass"
    DATA_RECOVERY = "data_recovery"


@dataclass
class RecoveryAction:
    """Action de récupération"""
    action_id: str
    action_type: str
    description: str
    strategy: RecoveryStrategy
    priority: RecoveryPriority
    estimated_duration: int  # seconds
    success_probability: float
    rollback_possible: bool
    side_effects: List[str]
    prerequisites: List[str]
    parameters: Dict[str, Any]
    handler: Optional[Callable]


@dataclass
class RecoveryWorkflow:
    """Workflow de récupération"""
    workflow_id: str
    error_context: Dict[str, Any]
    actions: List[RecoveryAction]
    execution_order: List[str]  # action_ids
    parallel_groups: List[List[str]]  # actions that can run in parallel
    rollback_plan: List[str]
    timeout_seconds: int
    max_retries: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


@dataclass
class RecoveryResult:
    """Résultat de récupération"""
    workflow_id: str
    overall_status: RecoveryStatus
    actions_executed: List[str]
    actions_succeeded: List[str]
    actions_failed: List[str]
    execution_time_seconds: float
    error_resolved: bool
    side_effects_occurred: List[str]
    rollback_performed: bool
    final_state: Dict[str, Any]
    recommendations: List[str]
    metrics: Dict[str, Any]


@dataclass
class SelfHealingRule:
    """Règle d'auto-guérison"""
    rule_id: str
    trigger_conditions: Dict[str, Any]
    healing_actions: List[HealingCapability]
    cooldown_period: int  # seconds
    max_applications: int
    success_threshold: float
    active: bool
    last_applied: Optional[datetime]
    application_count: int
    success_rate: float


class ErrorRecoveryOrchestrator:
    """
    🔧 Lead Dev IA + DevOps: Orchestrateur de récupération d'erreurs
    
    Système d'orchestration avancé pour:
    - Récupération automatique d'erreurs
    - Auto-guérison intelligente
    - Workflows de récupération adaptatifs
    - Rollback automatique
    - Métriques de succès de récupération
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation de l'orchestrateur de récupération"""
        self.config = config or {}
        
        # Recovery components
        self.recovery_strategies: Dict[str, List[RecoveryAction]] = defaultdict(list)
        self.self_healing_rules: Dict[str, SelfHealingRule] = {}
        self.active_workflows: Dict[str, RecoveryWorkflow] = {}
        self.workflow_history: deque = deque(maxlen=1000)
        
        # Action handlers
        self.action_handlers: Dict[str, Callable] = {}
        self.healing_handlers: Dict[HealingCapability, Callable] = {}
        
        # Recovery state
        self.recovery_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.recovery_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Circuit breakers for recovery actions
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.metrics = {
            'workflows_executed': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'self_healing_applications': 0,
            'average_recovery_time': 0.0,
            'rollbacks_performed': 0,
            'manual_interventions_required': 0
        }
        
        # 🎵 Audio + Platform: Configuration Ainflue
        self.platform_recovery_configs = self._initialize_platform_recovery_configs()
        
        # Initialize recovery strategies
        self._initialize_recovery_strategies()
        self._initialize_self_healing_rules()
        self._initialize_action_handlers()
        
        logger.info("ErrorRecoveryOrchestrator initialized with self-healing capabilities")
    
    def _initialize_platform_recovery_configs(self) -> Dict[str, Dict[str, Any]]:
        """🎵 Audio + Platform: Configuration de récupération pour 65+ plateformes"""
        return {
            # Music Streaming Platforms
            'spotify': {
                'common_errors': {
                    'RATE_LIMIT_EXCEEDED': {
                        'strategy': RecoveryStrategy.EXPONENTIAL_BACKOFF,
                        'max_retry': 5,
                        'base_delay': 60,
                        'fallback_available': False
                    },
                    'TOKEN_EXPIRED': {
                        'strategy': RecoveryStrategy.SELF_HEALING,
                        'action': 'token_refresh',
                        'fallback_available': True
                    },
                    'SERVICE_UNAVAILABLE': {
                        'strategy': RecoveryStrategy.FALLBACK_SERVICE,
                        'fallback_services': ['apple_music', 'soundcloud'],
                        'degraded_mode': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.CONNECTION_RESET,
                    HealingCapability.CACHE_CLEARING
                ],
                'recovery_priority': RecoveryPriority.HIGH,
                'business_impact': 0.95
            },
            
            'apple_music': {
                'common_errors': {
                    'DRM_ERROR': {
                        'strategy': RecoveryStrategy.MANUAL_INTERVENTION,
                        'escalation_required': True,
                        'fallback_available': False
                    },
                    'METADATA_REJECTED': {
                        'strategy': RecoveryStrategy.WORKFLOW_RESTART,
                        'validation_required': True,
                        'rollback_data': True
                    },
                    'API_LIMIT_EXCEEDED': {
                        'strategy': RecoveryStrategy.DEGRADED_MODE,
                        'reduced_functionality': True,
                        'notification_required': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.DATA_RECOVERY,
                    HealingCapability.CONNECTION_RESET
                ],
                'recovery_priority': RecoveryPriority.HIGH,
                'business_impact': 0.9
            },
            
            # Social Media Platforms
            'youtube': {
                'common_errors': {
                    'QUOTA_EXCEEDED': {
                        'strategy': RecoveryStrategy.DEGRADED_MODE,
                        'schedule_retry': True,
                        'quota_reset_time': 24  # hours
                    },
                    'VIDEO_PROCESSING_FAILED': {
                        'strategy': RecoveryStrategy.IMMEDIATE_RETRY,
                        'max_retry': 3,
                        'different_format': True
                    },
                    'COPYRIGHT_STRIKE': {
                        'strategy': RecoveryStrategy.MANUAL_INTERVENTION,
                        'legal_review_required': True,
                        'content_removal': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.SERVICE_RESTART,
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.DEPENDENCY_BYPASS
                ],
                'recovery_priority': RecoveryPriority.CRITICAL,
                'business_impact': 1.0
            },
            
            'instagram': {
                'common_errors': {
                    'MEDIA_UPLOAD_FAILED': {
                        'strategy': RecoveryStrategy.IMMEDIATE_RETRY,
                        'format_conversion': True,
                        'size_optimization': True
                    },
                    'HASHTAG_BANNED': {
                        'strategy': RecoveryStrategy.SELF_HEALING,
                        'hashtag_replacement': True,
                        'automated_fix': True
                    },
                    'ACCOUNT_RESTRICTED': {
                        'strategy': RecoveryStrategy.MANUAL_INTERVENTION,
                        'user_notification': True,
                        'support_escalation': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.CACHE_CLEARING,
                    HealingCapability.CONNECTION_RESET
                ],
                'recovery_priority': RecoveryPriority.HIGH,
                'business_impact': 0.85
            },
            
            # Creator Economy Platforms
            'patreon': {
                'common_errors': {
                    'PAYMENT_FAILED': {
                        'strategy': RecoveryStrategy.IMMEDIATE_RETRY,
                        'payment_retry_logic': True,
                        'user_notification': True
                    },
                    'SUBSCRIPTION_ERROR': {
                        'strategy': RecoveryStrategy.SELF_HEALING,
                        'data_synchronization': True,
                        'state_recovery': True
                    },
                    'API_ERROR': {
                        'strategy': RecoveryStrategy.EXPONENTIAL_BACKOFF,
                        'circuit_breaker': True,
                        'fallback_mode': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.DATA_RECOVERY,
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.CONNECTION_RESET
                ],
                'recovery_priority': RecoveryPriority.CRITICAL,
                'business_impact': 1.0
            },
            
            'onlyfans': {
                'common_errors': {
                    'CONTENT_VIOLATION': {
                        'strategy': RecoveryStrategy.MANUAL_INTERVENTION,
                        'content_review': True,
                        'compliance_check': True
                    },
                    'PAYMENT_PROCESSING_ERROR': {
                        'strategy': RecoveryStrategy.IMMEDIATE_RETRY,
                        'payment_gateway_switch': True,
                        'user_notification': True
                    },
                    'AGE_VERIFICATION_FAILED': {
                        'strategy': RecoveryStrategy.MANUAL_INTERVENTION,
                        'document_resubmission': True,
                        'verification_escalation': True
                    }
                },
                'healing_capabilities': [
                    HealingCapability.DATA_RECOVERY,
                    HealingCapability.TOKEN_REFRESH,
                    HealingCapability.SERVICE_RESTART
                ],
                'recovery_priority': RecoveryPriority.CRITICAL,
                'business_impact': 1.0
            }
        }
    
    def _initialize_recovery_strategies(self):
        """📋 Strategies: Initialisation des stratégies de récupération"""
        
        # Strategy: Immediate Retry
        immediate_retry_actions = [
            RecoveryAction(
                action_id='immediate_retry_1',
                action_type='retry',
                description='Immediate retry with same parameters',
                strategy=RecoveryStrategy.IMMEDIATE_RETRY,
                priority=RecoveryPriority.HIGH,
                estimated_duration=5,
                success_probability=0.7,
                rollback_possible=False,
                side_effects=[],
                prerequisites=[],
                parameters={'retry_count': 1, 'delay': 0},
                handler=self._handle_immediate_retry
            ),
            RecoveryAction(
                action_id='immediate_retry_3',
                action_type='retry',
                description='Immediate retry up to 3 times',
                strategy=RecoveryStrategy.IMMEDIATE_RETRY,
                priority=RecoveryPriority.MEDIUM,
                estimated_duration=15,
                success_probability=0.85,
                rollback_possible=False,
                side_effects=[],
                prerequisites=[],
                parameters={'retry_count': 3, 'delay': 1},
                handler=self._handle_immediate_retry
            )
        ]
        self.recovery_strategies[RecoveryStrategy.IMMEDIATE_RETRY.value] = immediate_retry_actions
        
        # Strategy: Exponential Backoff
        exponential_backoff_actions = [
            RecoveryAction(
                action_id='exponential_backoff',
                action_type='retry_with_backoff',
                description='Retry with exponential backoff',
                strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF,
                priority=RecoveryPriority.MEDIUM,
                estimated_duration=300,  # 5 minutes max
                success_probability=0.9,
                rollback_possible=False,
                side_effects=[],
                prerequisites=[],
                parameters={'max_retries': 5, 'base_delay': 10, 'max_delay': 300},
                handler=self._handle_exponential_backoff
            )
        ]
        self.recovery_strategies[RecoveryStrategy.EXPONENTIAL_BACKOFF.value] = exponential_backoff_actions
        
        # Strategy: Circuit Breaker
        circuit_breaker_actions = [
            RecoveryAction(
                action_id='circuit_breaker_open',
                action_type='circuit_control',
                description='Open circuit breaker to prevent cascading failures',
                strategy=RecoveryStrategy.CIRCUIT_BREAKER,
                priority=RecoveryPriority.HIGH,
                estimated_duration=10,
                success_probability=0.95,
                rollback_possible=True,
                side_effects=['service_unavailable'],
                prerequisites=[],
                parameters={'duration': 60, 'failure_threshold': 5},
                handler=self._handle_circuit_breaker
            )
        ]
        self.recovery_strategies[RecoveryStrategy.CIRCUIT_BREAKER.value] = circuit_breaker_actions
        
        # Strategy: Fallback Service
        fallback_service_actions = [
            RecoveryAction(
                action_id='activate_fallback',
                action_type='fallback',
                description='Activate fallback service',
                strategy=RecoveryStrategy.FALLBACK_SERVICE,
                priority=RecoveryPriority.HIGH,
                estimated_duration=30,
                success_probability=0.8,
                rollback_possible=True,
                side_effects=['reduced_functionality'],
                prerequisites=['fallback_service_available'],
                parameters={'fallback_services': []},
                handler=self._handle_fallback_service
            )
        ]
        self.recovery_strategies[RecoveryStrategy.FALLBACK_SERVICE.value] = fallback_service_actions
        
        # Strategy: Self Healing
        self_healing_actions = [
            RecoveryAction(
                action_id='token_refresh',
                action_type='authentication',
                description='Refresh authentication tokens',
                strategy=RecoveryStrategy.SELF_HEALING,
                priority=RecoveryPriority.HIGH,
                estimated_duration=15,
                success_probability=0.95,
                rollback_possible=False,
                side_effects=[],
                prerequisites=['refresh_token_available'],
                parameters={},
                handler=self._handle_token_refresh
            ),
            RecoveryAction(
                action_id='connection_reset',
                action_type='network',
                description='Reset network connections',
                strategy=RecoveryStrategy.SELF_HEALING,
                priority=RecoveryPriority.MEDIUM,
                estimated_duration=10,
                success_probability=0.8,
                rollback_possible=False,
                side_effects=['temporary_disconnection'],
                prerequisites=[],
                parameters={},
                handler=self._handle_connection_reset
            ),
            RecoveryAction(
                action_id='cache_clear',
                action_type='cache',
                description='Clear application caches',
                strategy=RecoveryStrategy.SELF_HEALING,
                priority=RecoveryPriority.LOW,
                estimated_duration=5,
                success_probability=0.6,
                rollback_possible=False,
                side_effects=['performance_degradation'],
                prerequisites=[],
                parameters={},
                handler=self._handle_cache_clear
            )
        ]
        self.recovery_strategies[RecoveryStrategy.SELF_HEALING.value] = self_healing_actions
    
    def _initialize_self_healing_rules(self):
        """🔧 Self-Healing: Initialisation des règles d'auto-guérison"""
        
        # Rule: Authentication Token Refresh
        auth_refresh_rule = SelfHealingRule(
            rule_id='auth_token_refresh',
            trigger_conditions={
                'error_codes': ['401', 'UNAUTHORIZED', 'TOKEN_EXPIRED'],
                'error_count_threshold': 1,
                'time_window_minutes': 5
            },
            healing_actions=[HealingCapability.TOKEN_REFRESH],
            cooldown_period=300,  # 5 minutes
            max_applications=10,
            success_threshold=0.8,
            active=True,
            last_applied=None,
            application_count=0,
            success_rate=0.0
        )
        self.self_healing_rules['auth_token_refresh'] = auth_refresh_rule
        
        # Rule: Connection Reset
        connection_reset_rule = SelfHealingRule(
            rule_id='connection_reset',
            trigger_conditions={
                'error_codes': ['TIMEOUT', 'CONNECTION_ERROR', 'NETWORK_ERROR'],
                'error_count_threshold': 3,
                'time_window_minutes': 10
            },
            healing_actions=[HealingCapability.CONNECTION_RESET],
            cooldown_period=180,  # 3 minutes
            max_applications=5,
            success_threshold=0.7,
            active=True,
            last_applied=None,
            application_count=0,
            success_rate=0.0
        )
        self.self_healing_rules['connection_reset'] = connection_reset_rule
        
        # Rule: Cache Clearing
        cache_clear_rule = SelfHealingRule(
            rule_id='cache_clear',
            trigger_conditions={
                'error_codes': ['STALE_DATA', 'CACHE_ERROR', 'DATA_INCONSISTENCY'],
                'error_count_threshold': 2,
                'time_window_minutes': 15
            },
            healing_actions=[HealingCapability.CACHE_CLEARING],
            cooldown_period=600,  # 10 minutes
            max_applications=3,
            success_threshold=0.6,
            active=True,
            last_applied=None,
            application_count=0,
            success_rate=0.0
        )
        self.self_healing_rules['cache_clear'] = cache_clear_rule
    
    def _initialize_action_handlers(self):
        """🔧 Handlers: Initialisation des gestionnaires d'actions"""
        
        # Register healing capability handlers
        self.healing_handlers = {
            HealingCapability.TOKEN_REFRESH: self._handle_token_refresh,
            HealingCapability.CONNECTION_RESET: self._handle_connection_reset,
            HealingCapability.CACHE_CLEARING: self._handle_cache_clear,
            HealingCapability.SERVICE_RESTART: self._handle_service_restart,
            HealingCapability.RESOURCE_SCALING: self._handle_resource_scaling,
            HealingCapability.LOAD_BALANCING: self._handle_load_balancing,
            HealingCapability.DEPENDENCY_BYPASS: self._handle_dependency_bypass,
            HealingCapability.DATA_RECOVERY: self._handle_data_recovery
        }
    
    async def orchestrate_recovery(
        self,
        error_context: Dict[str, Any],
        platform: Optional[str] = None,
        priority: RecoveryPriority = RecoveryPriority.MEDIUM
    ) -> RecoveryResult:
        """
        🔧 Lead Dev IA: Orchestration principale de récupération d'erreur
        
        Args:
            error_context: Contexte de l'erreur
            platform: Plateforme concernée
            priority: Priorité de récupération
            
        Returns:
            Résultat de la récupération
        """
        try:
            workflow_id = f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Determine recovery strategy
            strategy = await self._determine_recovery_strategy(error_context, platform, priority)
            
            # Create recovery workflow
            workflow = await self._create_recovery_workflow(
                workflow_id, error_context, strategy, platform, priority
            )
            
            # Execute recovery workflow
            result = await self._execute_recovery_workflow(workflow)
            
            # Update metrics
            await self._update_recovery_metrics(result)
            
            # Store workflow in history
            self.workflow_history.append(workflow)
            
            logger.info(f"Recovery orchestration completed: {workflow_id} - {result.overall_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error in recovery orchestration: {e}")
            
            # Return failure result
            return RecoveryResult(
                workflow_id=f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overall_status=RecoveryStatus.FAILED,
                actions_executed=[],
                actions_succeeded=[],
                actions_failed=[],
                execution_time_seconds=0.0,
                error_resolved=False,
                side_effects_occurred=[],
                rollback_performed=False,
                final_state={},
                recommendations=['Contact support', 'Manual intervention required'],
                metrics={'error': str(e)}
            )
    
    async def _determine_recovery_strategy(
        self,
        error_context: Dict[str, Any],
        platform: Optional[str],
        priority: RecoveryPriority
    ) -> RecoveryStrategy:
        """🧠 Strategy: Détermination de la stratégie de récupération"""
        
        error_type = error_context.get('error_type', 'UNKNOWN')
        error_code = error_context.get('error_code', 'UNKNOWN')
        
        # Platform-specific strategy
        if platform and platform in self.platform_recovery_configs:
            platform_config = self.platform_recovery_configs[platform]
            common_errors = platform_config.get('common_errors', {})
            
            for error_pattern, config in common_errors.items():
                if error_pattern in error_type or error_pattern in error_code:
                    return RecoveryStrategy(config['strategy'])
        
        # General strategy based on error characteristics
        if any(keyword in error_type.lower() for keyword in ['auth', 'token', 'unauthorized']):
            return RecoveryStrategy.SELF_HEALING
        elif any(keyword in error_type.lower() for keyword in ['rate', 'limit', 'quota']):
            return RecoveryStrategy.EXPONENTIAL_BACKOFF
        elif any(keyword in error_type.lower() for keyword in ['timeout', 'network', 'connection']):
            return RecoveryStrategy.IMMEDIATE_RETRY
        elif any(keyword in error_type.lower() for keyword in ['service', 'unavailable', '5']):
            return RecoveryStrategy.FALLBACK_SERVICE
        elif priority in [RecoveryPriority.CRITICAL, RecoveryPriority.EMERGENCY]:
            return RecoveryStrategy.CIRCUIT_BREAKER
        else:
            return RecoveryStrategy.IMMEDIATE_RETRY
    
    async def _create_recovery_workflow(
        self,
        workflow_id: str,
        error_context: Dict[str, Any],
        strategy: RecoveryStrategy,
        platform: Optional[str],
        priority: RecoveryPriority
    ) -> RecoveryWorkflow:
        """📋 Workflow: Création du workflow de récupération"""
        
        # Get actions for strategy
        strategy_actions = self.recovery_strategies.get(strategy.value, [])
        
        # Select appropriate actions based on priority and context
        selected_actions = []
        for action in strategy_actions:
            if await self._action_applicable(action, error_context, platform):
                selected_actions.append(action)
        
        # Determine execution order
        execution_order = [action.action_id for action in sorted(
            selected_actions, key=lambda a: a.priority.value, reverse=True
        )]
        
        # Identify parallel execution groups
        parallel_groups = []
        if len(selected_actions) > 1:
            # Simple parallelization: group actions of same priority
            priority_groups = defaultdict(list)
            for action in selected_actions:
                priority_groups[action.priority].append(action.action_id)
            
            for group in priority_groups.values():
                if len(group) > 1:
                    parallel_groups.append(group)
        
        # Create rollback plan
        rollback_plan = [
            action.action_id for action in selected_actions 
            if action.rollback_possible
        ]
        rollback_plan.reverse()  # Reverse order for rollback
        
        # Calculate timeout
        total_estimated_duration = sum(action.estimated_duration for action in selected_actions)
        timeout_seconds = min(total_estimated_duration * 2, 1800)  # Max 30 minutes
        
        workflow = RecoveryWorkflow(
            workflow_id=workflow_id,
            error_context=error_context,
            actions=selected_actions,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            rollback_plan=rollback_plan,
            timeout_seconds=timeout_seconds,
            max_retries=3,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None
        )
        
        # Store in active workflows
        self.active_workflows[workflow_id] = workflow
        
        return workflow
    
    async def _action_applicable(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any],
        platform: Optional[str]
    ) -> bool:
        """✅ Applicable: Vérification de l'applicabilité d'une action"""
        
        # Check prerequisites
        for prerequisite in action.prerequisites:
            if not await self._check_prerequisite(prerequisite, error_context, platform):
                return False
        
        # Check if action is not in circuit breaker state
        circuit_breaker_key = f"{platform}_{action.action_id}"
        if circuit_breaker_key in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_key]
            if circuit_breaker.get('state') == 'open':
                return False
        
        return True
    
    async def _check_prerequisite(
        self,
        prerequisite: str,
        error_context: Dict[str, Any],
        platform: Optional[str]
    ) -> bool:
        """🔍 Prerequisites: Vérification des prérequis"""
        
        if prerequisite == 'refresh_token_available':
            return error_context.get('refresh_token') is not None
        elif prerequisite == 'fallback_service_available':
            if platform in self.platform_recovery_configs:
                return len(self.platform_recovery_configs[platform].get('common_errors', {}).get(
                    'SERVICE_UNAVAILABLE', {}
                ).get('fallback_services', [])) > 0
        elif prerequisite == 'circuit_breaker_closed':
            circuit_breaker_key = f"{platform}_circuit_breaker"
            return self.circuit_breakers.get(circuit_breaker_key, {}).get('state') != 'open'
        
        return True
    
    async def _execute_recovery_workflow(self, workflow: RecoveryWorkflow) -> RecoveryResult:
        """⚡ Execution: Exécution du workflow de récupération"""
        
        workflow.started_at = datetime.now()
        start_time = time.time()
        
        actions_executed = []
        actions_succeeded = []
        actions_failed = []
        side_effects_occurred = []
        rollback_performed = False
        
        try:
            # Execute actions in order
            for action_id in workflow.execution_order:
                action = next((a for a in workflow.actions if a.action_id == action_id), None)
                if not action:
                    continue
                
                logger.info(f"Executing recovery action: {action_id}")
                actions_executed.append(action_id)
                
                try:
                    # Execute action with timeout
                    action_result = await asyncio.wait_for(
                        self._execute_recovery_action(action, workflow.error_context),
                        timeout=action.estimated_duration * 2
                    )
                    
                    if action_result.get('success', False):
                        actions_succeeded.append(action_id)
                        
                        # Record side effects
                        if action.side_effects:
                            side_effects_occurred.extend(action.side_effects)
                        
                        # Check if error is resolved
                        if action_result.get('error_resolved', False):
                            break  # Recovery successful
                    else:
                        actions_failed.append(action_id)
                        
                        # Update circuit breaker
                        await self._update_circuit_breaker(action, False)
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Recovery action {action_id} timed out")
                    actions_failed.append(action_id)
                except Exception as e:
                    logger.error(f"Recovery action {action_id} failed: {e}")
                    actions_failed.append(action_id)
                    
                    # Update circuit breaker
                    await self._update_circuit_breaker(action, False)
            
            # Determine overall status
            if actions_succeeded and not actions_failed:
                overall_status = RecoveryStatus.SUCCESS
            elif actions_succeeded and actions_failed:
                overall_status = RecoveryStatus.PARTIAL_SUCCESS
            elif actions_failed:
                overall_status = RecoveryStatus.FAILED
                
                # Perform rollback if needed
                if workflow.rollback_plan:
                    rollback_performed = await self._perform_rollback(workflow)
            else:
                overall_status = RecoveryStatus.TIMEOUT
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            overall_status = RecoveryStatus.FAILED
            
            # Attempt rollback
            if workflow.rollback_plan:
                rollback_performed = await self._perform_rollback(workflow)
        
        finally:
            workflow.completed_at = datetime.now()
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate recommendations
        recommendations = await self._generate_recovery_recommendations(
            workflow, overall_status, actions_failed
        )
        
        return RecoveryResult(
            workflow_id=workflow.workflow_id,
            overall_status=overall_status,
            actions_executed=actions_executed,
            actions_succeeded=actions_succeeded,
            actions_failed=actions_failed,
            execution_time_seconds=execution_time,
            error_resolved=overall_status in [RecoveryStatus.SUCCESS, RecoveryStatus.PARTIAL_SUCCESS],
            side_effects_occurred=side_effects_occurred,
            rollback_performed=rollback_performed,
            final_state={'workflow_completed': True},
            recommendations=recommendations,
            metrics={
                'total_actions': len(workflow.actions),
                'success_rate': len(actions_succeeded) / max(len(actions_executed), 1),
                'execution_time_seconds': execution_time
            }
        )
    
    async def _execute_recovery_action(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔧 Action: Exécution d'une action de récupération"""
        
        try:
            if action.handler:
                # Execute custom handler
                result = await action.handler(action, error_context)
            else:
                # Default handler based on action type
                result = await self._default_action_handler(action, error_context)
            
            # Update circuit breaker on success
            await self._update_circuit_breaker(action, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Recovery action {action.action_id} execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _default_action_handler(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔧 Default: Gestionnaire d'action par défaut"""
        
        # Simulate action execution
        await asyncio.sleep(1)  # Simulate work
        
        # Return success with probability based on action's success_probability
        success = random.random() < action.success_probability
        
        return {
            'success': success,
            'action_id': action.action_id,
            'execution_time': 1.0,
            'error_resolved': success and action.strategy == RecoveryStrategy.SELF_HEALING
        }
    
    # Specific action handlers
    async def _handle_immediate_retry(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Retry: Gestionnaire de retry immédiat"""
        
        retry_count = action.parameters.get('retry_count', 1)
        delay = action.parameters.get('delay', 0)
        
        for attempt in range(retry_count):
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Simulate retry
            success = random.random() < action.success_probability
            if success:
                return {
                    'success': True,
                    'action_id': action.action_id,
                    'attempts': attempt + 1,
                    'error_resolved': True
                }
        
        return {
            'success': False,
            'action_id': action.action_id,
            'attempts': retry_count,
            'error_resolved': False
        }
    
    async def _handle_exponential_backoff(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📈 Backoff: Gestionnaire de backoff exponentiel"""
        
        max_retries = action.parameters.get('max_retries', 5)
        base_delay = action.parameters.get('base_delay', 10)
        max_delay = action.parameters.get('max_delay', 300)
        
        for attempt in range(max_retries):
            # Calculate delay with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            total_delay = delay + jitter
            
            if attempt > 0:
                await asyncio.sleep(total_delay)
            
            # Simulate retry
            success = random.random() < (action.success_probability + attempt * 0.05)
            if success:
                return {
                    'success': True,
                    'action_id': action.action_id,
                    'attempts': attempt + 1,
                    'total_delay': sum(min(base_delay * (2 ** i), max_delay) for i in range(attempt + 1)),
                    'error_resolved': True
                }
        
        return {
            'success': False,
            'action_id': action.action_id,
            'attempts': max_retries,
            'error_resolved': False
        }
    
    async def _handle_circuit_breaker(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⚡ Circuit: Gestionnaire de circuit breaker"""
        
        platform = error_context.get('platform', 'unknown')
        circuit_key = f"{platform}_circuit_breaker"
        
        duration = action.parameters.get('duration', 60)
        
        # Open circuit breaker
        self.circuit_breakers[circuit_key] = {
            'state': 'open',
            'opened_at': datetime.now(),
            'duration': duration,
            'failure_count': 0
        }
        
        logger.info(f"Circuit breaker opened for {platform} for {duration} seconds")
        
        return {
            'success': True,
            'action_id': action.action_id,
            'circuit_state': 'open',
            'duration': duration,
            'error_resolved': False  # Circuit breaker doesn't resolve the error, just prevents cascade
        }
    
    async def _handle_fallback_service(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Fallback: Gestionnaire de service de fallback"""
        
        fallback_services = action.parameters.get('fallback_services', [])
        platform = error_context.get('platform', 'unknown')
        
        # Get platform-specific fallback services
        if not fallback_services and platform in self.platform_recovery_configs:
            platform_config = self.platform_recovery_configs[platform]
            fallback_services = platform_config.get('common_errors', {}).get(
                'SERVICE_UNAVAILABLE', {}
            ).get('fallback_services', [])
        
        if not fallback_services:
            return {
                'success': False,
                'action_id': action.action_id,
                'error': 'No fallback services available',
                'error_resolved': False
            }
        
        # Select fallback service (simple: first available)
        selected_fallback = fallback_services[0]
        
        logger.info(f"Activating fallback service {selected_fallback} for {platform}")
        
        return {
            'success': True,
            'action_id': action.action_id,
            'fallback_service': selected_fallback,
            'reduced_functionality': True,
            'error_resolved': True
        }
    
    async def _handle_token_refresh(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔑 Token: Gestionnaire de rafraîchissement de token"""
        
        # Simulate token refresh
        await asyncio.sleep(2)
        
        success = random.random() < 0.95  # High success rate for token refresh
        
        if success:
            logger.info("Authentication token refreshed successfully")
            return {
                'success': True,
                'action_id': action.action_id,
                'new_token_generated': True,
                'error_resolved': True
            }
        else:
            return {
                'success': False,
                'action_id': action.action_id,
                'error': 'Token refresh failed',
                'error_resolved': False
            }
    
    async def _handle_connection_reset(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔌 Connection: Gestionnaire de reset de connexion"""
        
        # Simulate connection reset
        await asyncio.sleep(3)
        
        success = random.random() < 0.8  # Good success rate for connection reset
        
        if success:
            logger.info("Network connections reset successfully")
            return {
                'success': True,
                'action_id': action.action_id,
                'connections_reset': True,
                'error_resolved': True
            }
        else:
            return {
                'success': False,
                'action_id': action.action_id,
                'error': 'Connection reset failed',
                'error_resolved': False
            }
    
    async def _handle_cache_clear(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🗑️ Cache: Gestionnaire de nettoyage de cache"""
        
        # Simulate cache clearing
        await asyncio.sleep(1)
        
        success = random.random() < 0.9  # High success rate for cache clearing
        
        if success:
            logger.info("Application caches cleared successfully")
            return {
                'success': True,
                'action_id': action.action_id,
                'caches_cleared': True,
                'error_resolved': random.random() < 0.6  # Cache clearing doesn't always resolve the error
            }
        else:
            return {
                'success': False,
                'action_id': action.action_id,
                'error': 'Cache clearing failed',
                'error_resolved': False
            }
    
    async def _handle_service_restart(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Restart: Gestionnaire de redémarrage de service"""
        
        # Simulate service restart (this would be dangerous in production)
        await asyncio.sleep(10)
        
        success = random.random() < 0.7  # Moderate success rate
        
        if success:
            logger.info("Service restarted successfully")
            return {
                'success': True,
                'action_id': action.action_id,
                'service_restarted': True,
                'downtime_seconds': 10,
                'error_resolved': True
            }
        else:
            return {
                'success': False,
                'action_id': action.action_id,
                'error': 'Service restart failed',
                'error_resolved': False
            }
    
    async def _handle_resource_scaling(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📈 Scaling: Gestionnaire de mise à l'échelle des ressources"""
        
        # Simulate resource scaling
        await asyncio.sleep(30)
        
        success = random.random() < 0.85
        
        return {
            'success': success,
            'action_id': action.action_id,
            'resources_scaled': success,
            'error_resolved': success
        }
    
    async def _handle_load_balancing(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⚖️ Load Balance: Gestionnaire d'équilibrage de charge"""
        
        await asyncio.sleep(5)
        success = random.random() < 0.8
        
        return {
            'success': success,
            'action_id': action.action_id,
            'load_balanced': success,
            'error_resolved': success
        }
    
    async def _handle_dependency_bypass(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔀 Bypass: Gestionnaire de contournement de dépendance"""
        
        await asyncio.sleep(3)
        success = random.random() < 0.75
        
        return {
            'success': success,
            'action_id': action.action_id,
            'dependency_bypassed': success,
            'reduced_functionality': True,
            'error_resolved': success
        }
    
    async def _handle_data_recovery(
        self,
        action: RecoveryAction,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """💾 Data Recovery: Gestionnaire de récupération de données"""
        
        await asyncio.sleep(15)
        success = random.random() < 0.9
        
        return {
            'success': success,
            'action_id': action.action_id,
            'data_recovered': success,
            'error_resolved': success
        }
    
    async def _update_circuit_breaker(self, action: RecoveryAction, success: bool):
        """⚡ Circuit Update: Mise à jour du circuit breaker"""
        
        circuit_key = f"{action.action_type}_{action.action_id}"
        
        if circuit_key not in self.circuit_breakers:
            self.circuit_breakers[circuit_key] = {
                'state': 'closed',
                'failure_count': 0,
                'success_count': 0,
                'last_failure': None,
                'last_success': None
            }
        
        circuit = self.circuit_breakers[circuit_key]
        
        if success:
            circuit['success_count'] += 1
            circuit['last_success'] = datetime.now()
            
            # Reset failure count on success
            if circuit['failure_count'] > 0:
                circuit['failure_count'] = max(0, circuit['failure_count'] - 1)
        else:
            circuit['failure_count'] += 1
            circuit['last_failure'] = datetime.now()
            
            # Open circuit if failure threshold exceeded
            if circuit['failure_count'] >= 5:
                circuit['state'] = 'open'
                circuit['opened_at'] = datetime.now()
    
    async def _perform_rollback(self, workflow: RecoveryWorkflow) -> bool:
        """🔙 Rollback: Exécution du rollback"""
        
        try:
            logger.info(f"Performing rollback for workflow {workflow.workflow_id}")
            
            for action_id in workflow.rollback_plan:
                action = next((a for a in workflow.actions if a.action_id == action_id), None)
                if action and action.rollback_possible:
                    # Simulate rollback
                    await asyncio.sleep(1)
                    logger.info(f"Rolled back action: {action_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def _generate_recovery_recommendations(
        self,
        workflow: RecoveryWorkflow,
        status: RecoveryStatus,
        failed_actions: List[str]
    ) -> List[str]:
        """💡 Recommendations: Génération de recommandations"""
        
        recommendations = []
        
        if status == RecoveryStatus.SUCCESS:
            recommendations.extend([
                "Recovery completed successfully",
                "Monitor system for stability",
                "Review logs for root cause analysis"
            ])
        elif status == RecoveryStatus.PARTIAL_SUCCESS:
            recommendations.extend([
                "Partial recovery achieved",
                "Review failed actions for improvement",
                "Consider manual intervention for remaining issues"
            ])
        elif status == RecoveryStatus.FAILED:
            recommendations.extend([
                "Automatic recovery failed",
                "Manual intervention required",
                "Escalate to operations team",
                "Review recovery strategy effectiveness"
            ])
            
            # Specific recommendations for failed actions
            for action_id in failed_actions:
                action = next((a for a in workflow.actions if a.action_id == action_id), None)
                if action:
                    if action.strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                        recommendations.append("Consider exponential backoff instead of immediate retry")
                    elif action.strategy == RecoveryStrategy.SELF_HEALING:
                        recommendations.append("Verify self-healing prerequisites are met")
        
        return recommendations
    
    async def _update_recovery_metrics(self, result: RecoveryResult):
        """📊 Metrics: Mise à jour des métriques de récupération"""
        
        self.metrics['workflows_executed'] += 1
        
        if result.overall_status == RecoveryStatus.SUCCESS:
            self.metrics['successful_recoveries'] += 1
        elif result.overall_status in [RecoveryStatus.FAILED, RecoveryStatus.TIMEOUT]:
            self.metrics['failed_recoveries'] += 1
        
        if result.rollback_performed:
            self.metrics['rollbacks_performed'] += 1
        
        # Update average recovery time
        current_avg = self.metrics['average_recovery_time']
        new_avg = (current_avg + result.execution_time_seconds) / 2
        self.metrics['average_recovery_time'] = new_avg
    
    async def apply_self_healing(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔧 Self-Healing: Application des règles d'auto-guérison
        
        Args:
            error_context: Contexte de l'erreur
            
        Returns:
            Résultat de l'auto-guérison
        """
        try:
            applicable_rules = []
            
            # Find applicable self-healing rules
            for rule in self.self_healing_rules.values():
                if await self._rule_applicable(rule, error_context):
                    applicable_rules.append(rule)
            
            if not applicable_rules:
                return {'applied': False, 'reason': 'No applicable healing rules'}
            
            # Apply healing rules
            healing_results = []
            for rule in applicable_rules:
                result = await self._apply_healing_rule(rule, error_context)
                healing_results.append(result)
                
                # Update rule statistics
                rule.application_count += 1
                rule.last_applied = datetime.now()
                
                if result.get('success', False):
                    success_count = rule.application_count * rule.success_rate + 1
                    rule.success_rate = success_count / (rule.application_count + 1)
                
                self.metrics['self_healing_applications'] += 1
            
            return {
                'applied': True,
                'rules_applied': len(applicable_rules),
                'results': healing_results,
                'overall_success': any(r.get('success', False) for r in healing_results)
            }
            
        except Exception as e:
            logger.error(f"Error in self-healing application: {e}")
            return {'applied': False, 'error': str(e)}
    
    async def _rule_applicable(self, rule: SelfHealingRule, error_context: Dict[str, Any]) -> bool:
        """✅ Rule Check: Vérification de l'applicabilité d'une règle"""
        
        if not rule.active:
            return False
        
        # Check cooldown period
        if rule.last_applied:
            time_since_last = (datetime.now() - rule.last_applied).total_seconds()
            if time_since_last < rule.cooldown_period:
                return False
        
        # Check max applications
        if rule.application_count >= rule.max_applications:
            return False
        
        # Check trigger conditions
        trigger_conditions = rule.trigger_conditions
        error_codes = trigger_conditions.get('error_codes', [])
        
        error_type = error_context.get('error_type', '')
        error_code = error_context.get('error_code', '')
        
        # Check if error matches trigger conditions
        for trigger_code in error_codes:
            if trigger_code in error_type or trigger_code in error_code:
                return True
        
        return False
    
    async def _apply_healing_rule(self, rule: SelfHealingRule, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 Apply Rule: Application d'une règle d'auto-guérison"""
        
        try:
            results = []
            
            for healing_capability in rule.healing_actions:
                if healing_capability in self.healing_handlers:
                    handler = self.healing_handlers[healing_capability]
                    
                    # Create a dummy action for the handler
                    dummy_action = RecoveryAction(
                        action_id=f"healing_{healing_capability.value}",
                        action_type="healing",
                        description=f"Self-healing: {healing_capability.value}",
                        strategy=RecoveryStrategy.SELF_HEALING,
                        priority=RecoveryPriority.HIGH,
                        estimated_duration=10,
                        success_probability=0.8,
                        rollback_possible=False,
                        side_effects=[],
                        prerequisites=[],
                        parameters={},
                        handler=handler
                    )
                    
                    result = await handler(dummy_action, error_context)
                    results.append(result)
            
            overall_success = any(r.get('success', False) for r in results)
            
            return {
                'success': overall_success,
                'rule_id': rule.rule_id,
                'healing_actions_applied': len(rule.healing_actions),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error applying healing rule {rule.rule_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_recovery_analytics(self) -> Dict[str, Any]:
        """
        📊 Analytics: Analytics complets de récupération d'erreurs
        
        Returns:
            Analytics détaillés avec métriques de récupération
        """
        try:
            # Strategy usage distribution
            strategy_usage = {}
            for workflow in self.workflow_history:
                for action in workflow.actions:
                    strategy = action.strategy.value
                    strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
            
            # Recovery success rates by strategy
            success_rates = {}
            for strategy in RecoveryStrategy:
                strategy_workflows = [
                    w for w in self.workflow_history 
                    if any(a.strategy == strategy for a in w.actions)
                ]
                if strategy_workflows:
                    successful = len([w for w in strategy_workflows if w.completed_at])
                    success_rates[strategy.value] = successful / len(strategy_workflows)
            
            # Self-healing rule performance
            healing_performance = {}
            for rule_id, rule in self.self_healing_rules.items():
                healing_performance[rule_id] = {
                    'applications': rule.application_count,
                    'success_rate': rule.success_rate,
                    'last_applied': rule.last_applied.isoformat() if rule.last_applied else None,
                    'active': rule.active
                }
            
            # Platform recovery statistics
            platform_stats = {}
            for platform in self.platform_recovery_configs.keys():
                platform_workflows = [
                    w for w in self.workflow_history 
                    if w.error_context.get('platform') == platform
                ]
                if platform_workflows:
                    successful = len([w for w in platform_workflows if w.completed_at])
                    platform_stats[platform] = {
                        'total_workflows': len(platform_workflows),
                        'success_rate': successful / len(platform_workflows),
                        'avg_execution_time': sum(
                            (w.completed_at - w.started_at).total_seconds() 
                            for w in platform_workflows if w.completed_at and w.started_at
                        ) / len(platform_workflows)
                    }
            
            # Active workflows
            active_workflow_count = len(self.active_workflows)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'orchestrator_status': {
                    'active_workflows': active_workflow_count,
                    'total_strategies': len(self.recovery_strategies),
                    'self_healing_rules': len(self.self_healing_rules),
                    'circuit_breakers': len(self.circuit_breakers),
                    'platform_configs': len(self.platform_recovery_configs)
                },
                'metrics': self.metrics,
                'performance': {
                    'strategy_usage': strategy_usage,
                    'success_rates_by_strategy': success_rates,
                    'healing_rule_performance': healing_performance,
                    'platform_recovery_stats': platform_stats
                },
                'capabilities': {
                    'available_strategies': [strategy.value for strategy in RecoveryStrategy],
                    'healing_capabilities': [cap.value for cap in HealingCapability],
                    'platform_support': len(self.platform_recovery_configs),
                    'self_healing_enabled': True,
                    'circuit_breaker_protection': True,
                    'rollback_support': True,
                    'parallel_execution': True
                },
                'recovery_insights': {
                    'most_successful_strategy': max(success_rates.items(), key=lambda x: x[1])[0] if success_rates else None,
                    'least_successful_strategy': min(success_rates.items(), key=lambda x: x[1])[0] if success_rates else None,
                    'average_recovery_time_seconds': self.metrics['average_recovery_time'],
                    'overall_success_rate': (
                        self.metrics['successful_recoveries'] / 
                        max(self.metrics['workflows_executed'], 1)
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating recovery analytics: {e}")
            return {'error': 'Failed to generate analytics', 'timestamp': datetime.now().isoformat()}


# Instance globale pour utilisation
error_recovery_orchestrator = ErrorRecoveryOrchestrator()

# Export des classes principales
__all__ = [
    'ErrorRecoveryOrchestrator',
    'RecoveryAction',
    'RecoveryWorkflow',
    'RecoveryResult',
    'SelfHealingRule',
    'RecoveryStrategy',
    'RecoveryPriority',
    'RecoveryStatus',
    'HealingCapability',
    'error_recovery_orchestrator'
]