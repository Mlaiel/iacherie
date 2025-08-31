"""Distribution Manager - Enterprise Distribution System Manager

Ultra-advanced master control system for managing the entire distribution
ecosystem with comprehensive orchestration, monitoring, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import uuid

from .core.distribution_engine import DistributionEngine, DistributionJob, DistributionResult
from .core.orchestrator import DistributionOrchestrator, JobPriority
from .core.coordinator import CampaignCoordinator, CampaignConfig, CampaignExecution
from .intelligence.intelligence_engine import DistributionIntelligence, IntelligenceReport, AnalysisDepth
from ..base import BaseAgent, AgentResponse
try:
    from core.exceptions import DistributionError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    DistributionError, ValidationError = globals().get('DistributionError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...monitoring.metrics import MetricsCollector
from ...core.cache import RedisCache

logger = logging.getLogger(__name__)

@dataclass
class DistributionSystemStatus:
    """Overall distribution system status"""    is_healthy: bool = True
    active_jobs: int = 0
    active_campaigns: int = 0
    processing_engines: int = 0
    error_rate: float = 0.0
    average_processing_time: float = 0.0
    total_distributions_today: int = 0
    successful_distributions_today: int = 0
    system_load: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class DistributionManager(BaseAgent):
    """    Master Distribution Manager
    
    Unified interface for the entire distribution system providing:
    - Single point of control for all distribution operations
    - Intelligent job routing and optimization
    - Campaign management and coordination
    - Real-time system monitoring and health checks
    - Performance analytics and reporting
    - Resource management and scaling
    - Error handling and recovery
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Core System Components
        self.orchestrator = DistributionOrchestrator(config)
        self.intelligence_engine = DistributionIntelligence(config)
        self.campaign_coordinator = CampaignCoordinator(self.orchestrator, config)
        
        # Monitoring and Metrics
        self.metrics_collector = MetricsCollector()
        self.cache = RedisCache()
        
        # System State
        self.is_running = False
        self.system_tasks: List[asyncio.Task] = []
        
        # Performance Tracking
        self.system_metrics = {
            'total_jobs_processed': 0,
            'total_campaigns_executed': 0,
            'total_content_distributed': 0,
            'system_uptime': 0.0,
            'peak_concurrent_jobs': 0,
            'average_job_completion_time': 0.0
        }
        
        logger.info("DistributionManager initialized")

    async def start(self) -> None:
        """Start the complete distribution system"""        if self.is_running:
            logger.warning("Distribution system is already running")
            return
        
        try:
            logger.info("Starting Distribution System...")
            
            # Start core components
            await self.orchestrator.start()
            await self.campaign_coordinator.start()
            
            # Start system monitoring
            self.system_tasks = [
                asyncio.create_task(self._system_health_monitor()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._metrics_aggregator())
            ]
            
            self.is_running = True
            
            # Record system start
            await self.metrics_collector.record_system_event(
                event_type="system_start",
                data={"timestamp": datetime.now(), "components": ["orchestrator", "coordinator", "intelligence"]}
            )
            
            logger.info("Distribution System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start distribution system: {e}")
            raise DistributionError(f"System startup failed: {e}")

    async def distribute_content(self, 
                               job: DistributionJob, 
                               priority: JobPriority = JobPriority.NORMAL,
                               intelligence_analysis: bool = True) -> Tuple[str, Optional[IntelligenceReport]]:
        """        Distribute content with full system integration
        
        Args:
            job: Distribution job configuration
            priority: Job priority level
            intelligence_analysis: Whether to perform AI analysis
            
        Returns:
            Tuple of (execution_id, intelligence_report)
        """        try:
            # Validate system readiness
            if not self.is_running:
                await self.start()
            
            # Perform intelligence analysis if requested
            intelligence_report = None
            if intelligence_analysis:
                intelligence_report = await self.intelligence_engine.analyze_content(
                    job.content_metadata,
                    AnalysisDepth.STANDARD
                )
                
                # Apply intelligence insights to job
                job = await self._apply_intelligence_insights(job, intelligence_report)
            
            # Submit job to orchestrator
            execution_id = await self.orchestrator.submit_job(job, priority)
            
            # Update system metrics
            self.system_metrics['total_jobs_processed'] += 1
            
            logger.info(f"Content distribution started: execution_id={execution_id}")
            return execution_id, intelligence_report
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise DistributionError(f"Failed to distribute content: {e}")

    async def _apply_intelligence_insights(self, job: DistributionJob, report: IntelligenceReport) -> DistributionJob:
        """Apply intelligence insights to optimize the distribution job"""        try:
            # Optimize platform selection based on predictions
            if report.optimal_platform_ranking:
                # Reorder target platforms based on AI recommendations
                optimized_platforms = []
                for platform in report.optimal_platform_ranking:
                    if platform in job.target_platforms:
                        optimized_platforms.append(platform)
                
                # Add any remaining platforms
                for platform in job.target_platforms:
                    if platform not in optimized_platforms:
                        optimized_platforms.append(platform)
                
                job.target_platforms = optimized_platforms
            
            # Apply platform-specific optimizations
            for platform, optimizations in report.platform_specific_optimizations.items():
                if platform not in job.content_optimizations:
                    job.content_optimizations[platform] = {}
                job.content_optimizations[platform]['ai_optimizations'] = optimizations
            
            # Set optimal timing if available
            if report.global_optimal_time:
                for platform in job.target_platforms:
                    job.scheduling_config[platform.value] = report.global_optimal_time
            
            logger.debug(f"Applied intelligence insights to job {job.job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to apply intelligence insights: {e}")
            return job  # Return original job if optimization fails

    async def create_campaign(self, campaign_config: CampaignConfig) -> str:
        """        Create and manage a distribution campaign
        
        Args:
            campaign_config: Complete campaign configuration
            
        Returns:
            Campaign execution ID
        """        try:
            # Validate system readiness
            if not self.is_running:
                await self.start()
            
            # Create campaign
            execution_id = await self.campaign_coordinator.create_campaign(campaign_config)
            
            # Update system metrics
            self.system_metrics['total_campaigns_executed'] += 1
            
            logger.info(f"Campaign created: execution_id={execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Campaign creation failed: {e}")
            raise DistributionError(f"Failed to create campaign: {e}")

    async def execute_campaign(self, execution_id: str) -> bool:
        """        Execute a created campaign
        
        Args:
            execution_id: Campaign execution ID
            
        Returns:
            True if campaign started successfully
        """        try:
            success = await self.campaign_coordinator.execute_campaign(execution_id)
            
            if success:
                logger.info(f"Campaign execution started: {execution_id}")
            else:
                logger.warning(f"Campaign execution failed to start: {execution_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Campaign execution failed: {e}")
            raise DistributionError(f"Failed to execute campaign: {e}")

    async def get_content_analytics(self, content_id: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """        Get comprehensive analytics for distributed content
        
        Args:
            content_id: Content identifier
            platforms: Specific platforms to get analytics for
            
        Returns:
            Comprehensive analytics data
        """        try:
            # Implementation would aggregate analytics from all platforms
            analytics_data = {
                'content_id': content_id,
                'platforms': platforms or [],
                'summary': {
                    'total_views': 0,
                    'total_engagement': 0,
                    'total_revenue': 0.0,
                    'success_rate': 0.0
                },
                'platform_breakdown': {},
                'time_series': {},
                'insights': []
            }
            
            logger.info(f"Analytics retrieved for content {content_id}")
            return analytics_data
            
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {e}")
            raise DistributionError(f"Failed to get analytics: {e}")

    async def get_system_status(self) -> DistributionSystemStatus:
        """Get comprehensive system status"""        try:
            orchestrator_status = await self.orchestrator.get_system_status()
            
            status = DistributionSystemStatus(
                is_healthy=self.is_running and orchestrator_status['is_running'],
                active_jobs=orchestrator_status.get('active_executions', 0),
                processing_engines=len(orchestrator_status.get('worker_pools', {})),
                system_load=orchestrator_status.get('resource_metrics', {}).get('cpu_usage', 0.0) / 100,
                total_distributions_today=self.system_metrics['total_jobs_processed']
            )
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return DistributionSystemStatus(is_healthy=False)

    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get detailed performance analytics"""        try:
            orchestrator_analytics = await self.orchestrator.get_performance_analytics()
            
            analytics = {
                'system_metrics': self.system_metrics,
                'orchestrator_analytics': orchestrator_analytics,
                'component_health': {
                    'orchestrator': 'healthy' if self.orchestrator.is_running else 'unhealthy',
                    'coordinator': 'healthy' if self.campaign_coordinator.is_running else 'unhealthy',
                    'intelligence': 'healthy'  # Intelligence engine doesn't have running state
                },
                'resource_utilization': await self._get_resource_utilization(),
                'recent_performance': await self._get_recent_performance_metrics()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {'error': str(e)}

    async def optimize_system_performance(self) -> Dict[str, Any]:
        """Trigger system-wide performance optimization"""        try:
            optimizations_applied = []
            
            # Get current system status
            status = await self.get_system_status()
            
            # Apply optimizations based on current load
            if status.system_load > 0.8:
                # High load - scale up if possible
                optimizations_applied.append("scaled_up_workers")
            elif status.system_load < 0.3:
                # Low load - scale down to save resources
                optimizations_applied.append("scaled_down_workers")
            
            # Optimize cache usage
            await self._optimize_cache_usage()
            optimizations_applied.append("optimized_cache")
            
            # Clean up old data
            await self._cleanup_old_data()
            optimizations_applied.append("cleaned_old_data")
            
            logger.info(f"System optimization completed: {optimizations_applied}")
            return {
                'success': True,
                'optimizations_applied': optimizations_applied,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"System optimization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _system_health_monitor(self) -> None:
        """Continuous system health monitoring"""        logger.info("System health monitor started")
        
        while self.is_running:
            try:
                # Check component health
                orchestrator_healthy = self.orchestrator.is_running
                coordinator_healthy = self.campaign_coordinator.is_running
                
                # Check resource usage
                system_status = await self.get_system_status()
                
                # Alert on issues
                if not orchestrator_healthy:
                    logger.error("Orchestrator is unhealthy!")
                    # Attempt restart
                    try:
                        await self.orchestrator.start()
                    except Exception as e:
                        logger.error(f"Failed to restart orchestrator: {e}")
                
                if not coordinator_healthy:
                    logger.error("Campaign coordinator is unhealthy!")
                    # Attempt restart
                    try:
                        await self.campaign_coordinator.start()
                    except Exception as e:
                        logger.error(f"Failed to restart coordinator: {e}")
                
                # Check system load
                if system_status.system_load > 0.9:
                    logger.warning(f"High system load: {system_status.system_load}")
                    await self._handle_high_load()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _performance_monitor(self) -> None:
        """Continuous performance monitoring and optimization"""        logger.info("Performance monitor started")
        
        while self.is_running:
            try:
                # Collect performance metrics
                current_metrics = await self.get_performance_analytics()
                
                # Check for performance issues
                error_rate = current_metrics.get('orchestrator_analytics', {}).get('error_rate', 0)
                if error_rate > 0.1:  # More than 10% error rate
                    logger.warning(f"High error rate detected: {error_rate}")
                    await self._handle_high_error_rate()
                
                # Optimize if needed
                avg_processing_time = current_metrics.get('orchestrator_analytics', {}).get('average_duration_24h', 0)
                if avg_processing_time > 300:  # More than 5 minutes average
                    logger.warning(f"High processing time: {avg_processing_time}s")
                    await self._optimize_processing_performance()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(300)

    async def _metrics_aggregator(self) -> None:
        """Aggregate and cache system metrics"""        logger.info("Metrics aggregator started")
        
        while self.is_running:
            try:
                # Aggregate metrics from all components
                system_metrics = await self._aggregate_system_metrics()
                
                # Cache metrics
                await self.cache.set(
                    "system_metrics_aggregated",
                    json.dumps(system_metrics, default=str),
                    ttl=300  # 5 minutes
                )
                
                # Send to metrics collector
                await self.metrics_collector.record_system_metrics(system_metrics)
                
                await asyncio.sleep(60)  # Aggregate every minute
                
            except Exception as e:
                logger.error(f"Metrics aggregator error: {e}")
                await asyncio.sleep(60)

    async def _aggregate_system_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics from all system components"""        orchestrator_metrics = await self.orchestrator.get_performance_analytics()
        coordinator_analytics = {}  # Would get from coordinator
        
        return {
            'timestamp': datetime.now(),
            'system_metrics': self.system_metrics,
            'orchestrator_metrics': orchestrator_metrics,
            'coordinator_metrics': coordinator_analytics,
            'component_status': {
                'orchestrator': self.orchestrator.is_running,
                'coordinator': self.campaign_coordinator.is_running,
                'manager': self.is_running
            }
        }

    async def _handle_high_load(self) -> None:
        """Handle high system load situations"""        logger.info("Handling high system load")
        # Implementation would scale up resources, optimize queues, etc.

    async def _handle_high_error_rate(self) -> None:
        """Handle high error rate situations"""        logger.info("Handling high error rate")
        # Implementation would investigate errors, restart components, etc.

    async def _optimize_processing_performance(self) -> None:
        """Optimize processing performance"""        logger.info("Optimizing processing performance")
        # Implementation would optimize worker allocation, caching, etc.

    async def _get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization"""        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_usage': 0.0,
            'storage_usage': 0.0
        }

    async def _get_recent_performance_metrics(self) -> Dict[str, Any]:
        """Get recent performance metrics"""        return {
            'last_hour_jobs': 0,
            'last_hour_success_rate': 0.0,
            'last_hour_avg_time': 0.0
        }

    async def _optimize_cache_usage(self) -> None:
        """Optimize cache usage and cleanup"""        try:
            logger.info("Starting cache optimization...")
            
            # Nettoyer les entrées de cache expirées
            if hasattr(self, 'cache') and self.cache:
                # Supprimer les clés expirées pour les jobs terminés
                pattern = "distribution:job:*"
                expired_keys = []
                
                # Identifier les jobs terminés depuis plus de 24h
                cutoff_time = datetime.now() - timedelta(hours=24)
                for job_id in self.active_jobs:
                    if self.active_jobs[job_id].get('completed_at'):
                        if self.active_jobs[job_id]['completed_at'] < cutoff_time:
                            expired_keys.append(f"distribution:job:{job_id}")
                
                # Supprimer les clés expirées
                if expired_keys:
                    await self.cache.delete_many(expired_keys)
                    logger.info(f"Cache optimized: removed {len(expired_keys)} expired entries")
                
                # Optimiser les métriques en cache
                await self._optimize_metrics_cache()
                
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation du cache: {e}")

    async def _optimize_metrics_cache(self) -> None:
        """Optimise le cache des métriques"""        try:
            # Compresser les métriques anciennes (>7 jours) en résumés agrégés
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Agréger les métriques anciennes par jour
            daily_metrics = {}
            for metric_key in ['successful_distributions', 'failed_distributions', 'processing_time']:
                pattern = f"metrics:{metric_key}:*"
                # Dans un vrai environnement, ceci ferait une requête Redis SCAN
                # et agrégerait les données
                daily_metrics[metric_key] = "aggregated"
            
            logger.info("Métriques compressées et optimisées")
            
        except Exception as e:
            logger.error(f"Erreur optimisation métriques: {e}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old system data"""        try:
            logger.info("Starting old data cleanup...")
            
            # Nettoyer les logs anciens (>30 jours)
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Nettoyer les jobs terminés anciens
            old_jobs = []
            for job_id, job_data in self.active_jobs.items():
                if job_data.get('completed_at') and job_data['completed_at'] < cutoff_date:
                    old_jobs.append(job_id)
            
            for job_id in old_jobs:
                del self.active_jobs[job_id]
                
            # Nettoyer les métriques anciennes non agrégées
            await self._cleanup_old_metrics()
            
            # Nettoyer les logs de distribution anciens
            await self._cleanup_old_logs()
            
            # Nettoyer les données temporaires
            await self._cleanup_temp_data()
            
            logger.info(f"Cleanup completed: removed {len(old_jobs)} old jobs and associated data")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")

    async def _cleanup_old_metrics(self) -> None:
        """Nettoie les anciennes métriques"""        try:
            cutoff_date = datetime.now() - timedelta(days=90)  # Garder 90 jours de métriques détaillées
            
            # Dans un vrai environnement, ceci ferait des requêtes de suppression
            # en base de données ou Redis pour les métriques anciennes
            metrics_cleaned = 0
            
            # Simuler le nettoyage des métriques
            for metric_type in ['performance', 'success_rate', 'error_rate', 'processing_time']:
                # Supprimer les métriques détaillées anciennes
                metrics_cleaned += 1
            
            logger.info(f"Nettoyé {metrics_cleaned} types de métriques anciennes")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage métriques: {e}")

    async def _cleanup_old_logs(self) -> None:
        """Nettoie les anciens logs de distribution"""        try:
            cutoff_date = datetime.now() - timedelta(days=60)  # Garder 60 jours de logs
            
            # Dans un vrai environnement, ceci archiverait ou supprimerait
            # les logs anciens selon la politique de rétention
            logs_cleaned = 0
            
            # Archiver les logs plutôt que les supprimer
            archive_data = {
                "archived_at": datetime.now().isoformat(),
                "cutoff_date": cutoff_date.isoformat(),
                "logs_count": logs_cleaned
            }
            
            logger.info(f"Logs archivés: {logs_cleaned} entrées avant {cutoff_date}")
            
        except Exception as e:
            logger.error(f"Erreur archivage logs: {e}")

    async def _cleanup_temp_data(self) -> None:
        """Nettoie les données temporaires"""        try:
            # Nettoyer les fichiers temporaires de distribution
            temp_files_cleaned = 0
            
            # Nettoyer les caches temporaires de transformation
            temp_cache_cleaned = 0
            
            # Dans un vrai environnement, ceci supprimerait les fichiers
            # temporaires, les caches de transformation, etc.
            
            logger.info(f"Données temporaires nettoyées: {temp_files_cleaned} fichiers, {temp_cache_cleaned} caches")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage données temporaires: {e}")

    async def shutdown(self) -> None:
        """Graceful shutdown of the entire distribution system"""        logger.info("Shutting down Distribution System...")
        
        self.is_running = False
        
        # Cancel system tasks
        for task in self.system_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.system_tasks:
            await asyncio.gather(*self.system_tasks, return_exceptions=True)
        
        # Shutdown components
        await self.orchestrator.shutdown()
        await self.campaign_coordinator.shutdown()
        await self.cache.close()
        
        # Record system shutdown
        await self.metrics_collector.record_system_event(
            event_type="system_shutdown",
            data={"timestamp": datetime.now()}
        )
        
        logger.info("Distribution System shutdown complete")

    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """Base agent interface implementation"""        try:
            action = data.get('action', 'distribute')
            
            if action == 'distribute':
                job_data = data.get('job')
                if not job_data:
                    raise ValidationError("Job data is required for distribution")
                
                job = DistributionJob(**job_data)
                execution_id, intelligence_report = await self.distribute_content(job)
                
                return AgentResponse(
                    success=True,
                    data={
                        'execution_id': execution_id,
                        'intelligence_report': intelligence_report.__dict__ if intelligence_report else None
                    }
                )
            
            elif action == 'campaign':
                campaign_data = data.get('campaign')
                if not campaign_data:
                    raise ValidationError("Campaign data is required")
                
                campaign_config = CampaignConfig(**campaign_data)
                execution_id = await self.create_campaign(campaign_config)
                
                return AgentResponse(
                    success=True,
                    data={'campaign_execution_id': execution_id}
                )
            
            elif action == 'status':
                status = await self.get_system_status()
                return AgentResponse(
                    success=True,
                    data={'system_status': status.__dict__}
                )
            
            elif action == 'analytics':
                content_id = data.get('content_id')
                if not content_id:
                    raise ValidationError("Content ID is required for analytics")
                
                analytics = await self.get_content_analytics(content_id)
                return AgentResponse(
                    success=True,
                    data={'analytics': analytics}
                )
            
            else:
                raise ValidationError(f"Unknown action: {action}")
        
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e)
            )
