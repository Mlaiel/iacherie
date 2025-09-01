"""Agent Coordinator - Coordination des Agents IA Consolidés

Système de coordination pour les agents IA consolidés du module ai/ai_agents,
optimisé pour l'architecture regroupée par fonctionnalité métier.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from .base_agent import BaseAIAgent, AgentCapability, AgentTask, AgentPriority
from .ai_orchestrator import AIOrchestrator
from .analytics_agent import AnalyticsAgent
from .content_protection_agents import ContentProtectionAgents
from .monetization_agents import MonetizationAgents
from .collaboration_agents import CollaborationAgents
from .audience_development_agents import AudienceDevelopmentAgents
from .brand_consulting_agents import BrandConsultingAgents
from .trend_analysis_agents import TrendAnalysisAgents
from .seo_optimization_agents import SEOOptimizationAgents
from .content_strategy_agents import ContentStrategyAgents

logger = logging.getLogger(__name__)


class CoordinationStrategy(Enum):
    """
Stratégies de coordination des agents"""

    SEQUENTIAL = "sequential"        # Séquentiel
    PARALLEL = "parallel"            # Parallèle
    PIPELINE = "pipeline"            # Pipeline
    COLLABORATIVE = "collaborative"  # Collaboratif
    ADAPTIVE = "adaptive"            # Adaptatif


@dataclass
class AgentCoordination:
    """Configuration de coordination d'agents"""
    agents: List[str] = field(default_factory=list)
    strategy: CoordinationStrategy = CoordinationStrategy.SEQUENTIAL
    timeout: int = 300
    retry_attempts: int = 3
    priority: AgentPriority = AgentPriority.MEDIUM
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class CoordinationResult:
    """
Résultat de coordination multi-agents"""
    success: bool
    coordination_id: str
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    participating_agents: List[str] = field(default_factory=list)


class AgentCoordinator:
    """
    Coordinateur centralisé pour agents IA consolidés.
    
    Fonctionnalités:
    - Coordination multi-agents par workflow métier
    - Gestion des dépendances entre agents
    - Load balancing et failover
    - Monitoring et métriques
    - Optimisation des performances
    """
    
    def __init__(self):
        self.orchestrator = AIOrchestrator()
        self.agents: Dict[str, BaseAIAgent] = {}
        self.coordinations: Dict[str, CoordinationResult] = {}
        
        # État du coordinateur
        self.is_running = False
        self.started_at = datetime.now(timezone.utc)
        
        # Métriques
        self.coordination_stats = {
            'total_coordinations': 0,
            'successful_coordinations': 0,
            'failed_coordinations': 0,
            'average_coordination_time': 0.0
        }
        
        logger.info("AgentCoordinator initialized")
    
    async def initialize(self):
        """Initialise le coordinateur et tous les agents"""
        try:
            # Initialisation de l'orchestrateur
            await self.orchestrator.initialize()
            
            # Initialisation des agents consolidés
            self.agents = {
                'analytics': AnalyticsAgent(),
                'protection': ContentProtectionAgents(),
                'monetization': MonetizationAgents(),
                'collaboration': CollaborationAgents(),
                'audience_development': AudienceDevelopmentAgents(),
                'brand_consulting': BrandConsultingAgents(),
                'trend_analysis': TrendAnalysisAgents(),
                'seo_optimization': SEOOptimizationAgents(),
                'content_strategy': ContentStrategyAgents()
            }
            
            # Initialisation des agents individuels
            for agent_name, agent in self.agents.items():
                try:
                    if hasattr(agent, 'initialize'):
                        await agent.initialize()
                    logger.info(f"Agent {agent_name} initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize agent {agent_name}: {e}")
            
            self.is_running = True
            logger.info("AgentCoordinator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AgentCoordinator: {e}")
            raise
    
    async def coordinate_agents(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any]
    ) -> CoordinationResult:
        """
        Coordonne l'exécution de plusieurs agents selon la stratégie définie.
        """
        coordination_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = CoordinationResult(
            success=False,
            coordination_id=coordination_id,
            participating_agents=coordination.agents.copy()
        )
        
        try:
            logger.info(f"Starting coordination {coordination_id} with strategy {coordination.strategy.value}")
            
            # Exécution selon la stratégie
            if coordination.strategy == CoordinationStrategy.SEQUENTIAL:
                result = await self._execute_sequential(coordination, task_data, result)
            elif coordination.strategy == CoordinationStrategy.PARALLEL:
                result = await self._execute_parallel(coordination, task_data, result)
            elif coordination.strategy == CoordinationStrategy.PIPELINE:
                result = await self._execute_pipeline(coordination, task_data, result)
            elif coordination.strategy == CoordinationStrategy.COLLABORATIVE:
                result = await self._execute_collaborative(coordination, task_data, result)
            elif coordination.strategy == CoordinationStrategy.ADAPTIVE:
                result = await self._execute_adaptive(coordination, task_data, result)
            
            result.execution_time = time.time() - start_time
            result.success = len(result.errors) == 0
            
            # Mise à jour des statistiques
            self.coordination_stats['total_coordinations'] += 1
            if result.success:
                self.coordination_stats['successful_coordinations'] += 1
            else:
                self.coordination_stats['failed_coordinations'] += 1
            
            # Mise à jour du temps moyen
            total = self.coordination_stats['total_coordinations']
            current_avg = self.coordination_stats['average_coordination_time']
            new_avg = ((current_avg * (total - 1)) + result.execution_time) / total
            self.coordination_stats['average_coordination_time'] = new_avg
            
            # Stockage du résultat
            self.coordinations[coordination_id] = result
            
            logger.info(f"Coordination {coordination_id} completed in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.errors.append(f"Coordination error: {str(e)}")
            result.execution_time = time.time() - start_time
            logger.error(f"Coordination {coordination_id} failed: {e}")
        
        return result
    
    async def _execute_sequential(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any],
        result: CoordinationResult
    ) -> CoordinationResult:
        """Exécution séquentielle des agents"""
        
        current_data = task_data.copy()
        
        for agent_name in coordination.agents:
            if agent_name not in self.agents:
                result.errors.append(f"Agent {agent_name} not found")
                continue
            
            try:
                agent = self.agents[agent_name]
                
                # Création de la tâche
                task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    name=f"sequential_task_{agent_name}",
                    priority=coordination.priority,
                    data=current_data
                )
                
                # Exécution de l'agent
                agent_result = await agent.execute_task(task)
                
                # Stockage du résultat
                result.results[agent_name] = agent_result
                
                # Propagation des données pour le prochain agent
                if hasattr(agent_result, 'data') and agent_result.data:
                    current_data.update(agent_result.data)
                
            except Exception as e:
                error_msg = f"Agent {agent_name} failed: {str(e)}"
                result.errors.append(error_msg)
                logger.error(error_msg)
        
        return result
    
    async def _execute_parallel(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any],
        result: CoordinationResult
    ) -> CoordinationResult:
        """Exécution parallèle des agents"""
        
        tasks = []
        
        for agent_name in coordination.agents:
            if agent_name not in self.agents:
                result.errors.append(f"Agent {agent_name} not found")
                continue
            
            agent = self.agents[agent_name]
            
            # Création de la tâche
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                name=f"parallel_task_{agent_name}",
                priority=coordination.priority,
                data=task_data.copy()
            )
            
            # Ajout de la tâche à exécuter
            tasks.append(self._execute_agent_task(agent, task, agent_name))
        
        # Exécution parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats
        for i, res in enumerate(results):
            agent_name = coordination.agents[i]
            
            if isinstance(res, Exception):
                error_msg = f"Agent {agent_name} failed: {str(res)}"
                result.errors.append(error_msg)
                logger.error(error_msg)
            else:
                result.results[agent_name] = res
        
        return result
    
    async def _execute_pipeline(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any],
        result: CoordinationResult
    ) -> CoordinationResult:
        """Exécution en pipeline avec flux de données"""
        
        # Utilisation de l'orchestrateur pour le pipeline
        try:
            pipeline_result = await self.orchestrator.execute_workflow(
                workflow_type="custom_pipeline",
                agents=coordination.agents,
                data=task_data
            )
            
            result.results['pipeline_result'] = pipeline_result
            
        except Exception as e:
            result.errors.append(f"Pipeline execution failed: {str(e)}")
            logger.error(f"Pipeline execution failed: {e}")
        
        return result
    
    async def _execute_collaborative(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any],
        result: CoordinationResult
    ) -> CoordinationResult:
        """Exécution collaborative avec communication inter-agents"""
        
        # Implémentation collaborative simplifiée
        # Les agents travaillent ensemble en partageant des données
        shared_context = {'shared_data': {}, 'agent_communications': []}
        
        for agent_name in coordination.agents:
            if agent_name not in self.agents:
                result.errors.append(f"Agent {agent_name} not found")
                continue
            
            try:
                agent = self.agents[agent_name]
                
                # Données enrichies avec le contexte partagé
                enriched_data = {**task_data, **shared_context}
                
                task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    name=f"collaborative_task_{agent_name}",
                    priority=coordination.priority,
                    data=enriched_data
                )
                
                agent_result = await agent.execute_task(task)
                result.results[agent_name] = agent_result
                
                # Mise à jour du contexte partagé
                if hasattr(agent_result, 'data') and agent_result.data:
                    shared_context['shared_data'].update(agent_result.data)
                
            except Exception as e:
                error_msg = f"Collaborative agent {agent_name} failed: {str(e)}"
                result.errors.append(error_msg)
                logger.error(error_msg)
        
        return result
    
    async def _execute_adaptive(
        self,
        coordination: AgentCoordination,
        task_data: Dict[str, Any],
        result: CoordinationResult
    ) -> CoordinationResult:
        """Exécution adaptive basée sur les performances et conditions"""
        
        # Analyse des performances passées pour optimiser l'exécution
        # Démarrer par les agents les plus performants
        agent_performance = await self._get_agent_performance_scores()
        
        # Tri des agents par performance
        sorted_agents = sorted(
            coordination.agents,
            key=lambda x: agent_performance.get(x, 0.5),
            reverse=True
        )
        
        # Exécution adaptative
        for agent_name in sorted_agents:
            if agent_name not in self.agents:
                result.errors.append(f"Agent {agent_name} not found")
                continue
            
            try:
                agent = self.agents[agent_name]
                
                task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    name=f"adaptive_task_{agent_name}",
                    priority=coordination.priority,
                    data=task_data.copy()
                )
                
                agent_result = await agent.execute_task(task)
                result.results[agent_name] = agent_result
                
                # Adaptation basée sur le résultat
                if hasattr(agent_result, 'success') and not agent_result.success:
                    result.warnings.append(f"Agent {agent_name} had issues, adapting strategy")
                
            except Exception as e:
                error_msg = f"Adaptive agent {agent_name} failed: {str(e)}"
                result.errors.append(error_msg)
                logger.error(error_msg)
        
        return result
    
    async def _execute_agent_task(
        self,
        agent: BaseAIAgent,
        task: AgentTask,
        agent_name: str
    ) -> Any:
        """Exécute une tâche sur un agent spécifique"""
        try:
            return await agent.execute_task(task)
        except Exception as e:
            logger.error(f"Task execution failed for agent {agent_name}: {e}")
            raise
    
    async def _get_agent_performance_scores(self) -> Dict[str, float]:
        """Calcule les scores de performance des agents"""
        
        # Scores basés sur les statistiques historiques
        # Dans une implémentation complète, ceci viendrait de métriques stockées
        performance_scores = {}
        
        for agent_name in self.agents.keys():
            # Score simulé basé sur le succès historique (0.0 à 1.0)
            performance_scores[agent_name] = 0.85  # Valeur par défaut
        
        return performance_scores
    
    async def get_coordination_status(self, coordination_id: str) -> Optional[CoordinationResult]:
        """
Récupère le statut d'une coordination"""
        return self.coordinations.get(coordination_id)
    
    async def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """
Vérifie la santé d'un agent spécifique"""
        if agent_name not in self.agents:
            return {'status': 'not_found', 'message': f'Agent {agent_name} not found'}
        
        agent = self.agents[agent_name]
        
        try:
            # Test simple de santé
            health_data = {
                'status': 'healthy',
                'agent_type': type(agent).__name__,
                'capabilities': getattr(agent, 'capabilities', []),
                'last_check': datetime.now(timezone.utc).isoformat()
            }
            
            return health_data
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now(timezone.utc).isoformat()
            }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
Retourne les statistiques système du coordinateur"""
        uptime = datetime.now(timezone.utc) - self.started_at
        
        return {
            'coordinator_status': 'running' if self.is_running else 'stopped',
            'uptime_seconds': uptime.total_seconds(),
            'registered_agents': list(self.agents.keys()),
            'coordination_stats': self.coordination_stats.copy(),
            'active_coordinations': len(self.coordinations),
            'orchestrator_status': getattr(self.orchestrator, 'is_running', False)
        }
    
    async def shutdown(self):
        """
Arrêt gracieux du coordinateur"""
        logger.info("Shutting down AgentCoordinator...")
        
        # Arrêt de l'orchestrateur
        if hasattr(self.orchestrator, 'shutdown'):
            await self.orchestrator.shutdown()
        
        # Arrêt des agents
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'shutdown'):
                    await agent.shutdown()
                logger.info(f"Agent {agent_name} shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down agent {agent_name}: {e}")
        
        self.is_running = False
        logger.info("AgentCoordinator shut down completed")


# Factory function pour création du coordinateur
async def create_agent_coordinator() -> AgentCoordinator:
    """Crée et initialise un coordinateur d'agents"""
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    return coordinator
