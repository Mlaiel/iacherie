"""Database Monitoring Index - Central Registry and Factory

Centralized index for all database monitoring components with factory patterns,
service discovery, and configuration management for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass
from enum import Enum
import logging

from .performance_monitor import DatabasePerformanceMonitor
from .query_analyzer import QueryAnalyzer, QueryOptimizer, ExecutionPlanAnalyzer
from .connection_monitor import ConnectionMonitor, ConnectionPoolManager
from .metrics_collector import MetricsCollector, TimeSeriesMetrics, RealTimeMetrics
from .alert_manager import DatabaseAlertManager, EscalationManager, NotificationRouter
from .health_checker import DatabaseHealthChecker, HealthScoreCalculator, DiagnosticsEngine
from .slow_query_detector import SlowQueryDetector, QueryPatternAnalyzer, PerformanceProfiler
from .resource_monitor import ResourceMonitor, CapacityPlanner, SystemResourceTracker
from .backup_monitor import BackupMonitor, ReplicationHealthChecker, DataIntegrityValidator
from .security_monitor import DatabaseSecurityMonitor, AccessPatternAnalyzer, ThreatDetector
from .compliance_monitor import ComplianceMonitor, AuditTrail, DataGovernanceTracker
from .cost_monitor import DatabaseCostMonitor, ResourceOptimizer, CostAnalyzer
from .ai_insights import DatabaseAIInsights, PredictiveAnalyzer, AnomalyDetector
from .content_pipeline_monitor import ContentPipelineMonitor
from .monetization_performance_monitor import MonetizationPerformanceMonitor

from ...core.config import Settings


class MonitoringComponentType(Enum):
    """Types of monitoring components"""
    PERFORMANCE = "performance"
    QUERY = "query"
    CONNECTION = "connection"
    METRICS = "metrics"
    ALERTS = "alerts"
    HEALTH = "health"
    SLOW_QUERY = "slow_query"
    RESOURCE = "resource"
    BACKUP = "backup"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COST = "cost"
    AI_INSIGHTS = "ai_insights"
    CONTENT_PIPELINE = "content_pipeline"          # New: Content processing pipeline monitoring
    MONETIZATION_PERFORMANCE = "monetization"     # New: Monetization performance monitoring


@dataclass
class ComponentRegistry:
    """Registry for monitoring components"""
    component_type: MonitoringComponentType
    component_class: Type
    dependencies: List[MonitoringComponentType]
    priority: int
    enabled: bool = True
    auto_start: bool = True
    config_section: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'component_type': self.component_type.value,
            'component_class': self.component_class.__name__,
            'dependencies': [dep.value for dep in self.dependencies],
            'priority': self.priority,
            'enabled': self.enabled,
            'auto_start': self.auto_start,
            'config_section': self.config_section
        }


class MonitoringOrchestrator:
    """Central orchestrator for all monitoring components"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Component registry
        self.component_registry: Dict[MonitoringComponentType, ComponentRegistry] = {}
        self.active_components: Dict[MonitoringComponentType, Any] = {}
        self.component_status: Dict[MonitoringComponentType, str] = {}
        
        # Orchestration state
        self._orchestrator_active = False
        self._orchestrator_task = None
        
        # Initialize component registry
        self._initialize_component_registry()
        
    def _initialize_component_registry(self):
        """Initialize the component registry with all monitoring components"""
        try:
            # Register all monitoring components with their dependencies
            components = [
                ComponentRegistry(
                    component_type=MonitoringComponentType.METRICS,
                    component_class=MetricsCollector,
                    dependencies=[],
                    priority=1,
                    config_section="metrics"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.PERFORMANCE,
                    component_class=DatabasePerformanceMonitor,
                    dependencies=[MonitoringComponentType.METRICS],
                    priority=2,
                    config_section="performance"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.QUERY,
                    component_class=QueryAnalyzer,
                    dependencies=[MonitoringComponentType.METRICS],
                    priority=2,
                    config_section="query_analysis"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.CONNECTION,
                    component_class=ConnectionMonitor,
                    dependencies=[MonitoringComponentType.METRICS],
                    priority=2,
                    config_section="connection"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.HEALTH,
                    component_class=DatabaseHealthChecker,
                    dependencies=[MonitoringComponentType.METRICS, MonitoringComponentType.PERFORMANCE],
                    priority=3,
                    config_section="health"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.SLOW_QUERY,
                    component_class=SlowQueryDetector,
                    dependencies=[MonitoringComponentType.QUERY],
                    priority=3,
                    config_section="slow_query"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.RESOURCE,
                    component_class=ResourceMonitor,
                    dependencies=[MonitoringComponentType.METRICS],
                    priority=3,
                    config_section="resource"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.BACKUP,
                    component_class=BackupMonitor,
                    dependencies=[MonitoringComponentType.HEALTH],
                    priority=4,
                    config_section="backup"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.SECURITY,
                    component_class=DatabaseSecurityMonitor,
                    dependencies=[MonitoringComponentType.METRICS],
                    priority=4,
                    config_section="security"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.COMPLIANCE,
                    component_class=ComplianceMonitor,
                    dependencies=[MonitoringComponentType.SECURITY],
                    priority=5,
                    config_section="compliance"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.COST,
                    component_class=DatabaseCostMonitor,
                    dependencies=[MonitoringComponentType.RESOURCE],
                    priority=5,
                    config_section="cost"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.AI_INSIGHTS,
                    component_class=DatabaseAIInsights,
                    dependencies=[
                        MonitoringComponentType.PERFORMANCE,
                        MonitoringComponentType.METRICS,
                        MonitoringComponentType.SECURITY
                    ],
                    priority=6,
                    config_section="ai_insights"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.CONTENT_PIPELINE,
                    component_class=ContentPipelineMonitor,
                    dependencies=[
                        MonitoringComponentType.METRICS,
                        MonitoringComponentType.PERFORMANCE,
                        MonitoringComponentType.AI_INSIGHTS
                    ],
                    priority=6,
                    config_section="content_pipeline"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.MONETIZATION_PERFORMANCE,
                    component_class=MonetizationPerformanceMonitor,
                    dependencies=[
                        MonitoringComponentType.METRICS,
                        MonitoringComponentType.CONTENT_PIPELINE,
                        MonitoringComponentType.AI_INSIGHTS
                    ],
                    priority=6,
                    config_section="monetization"
                ),
                ComponentRegistry(
                    component_type=MonitoringComponentType.ALERTS,
                    component_class=DatabaseAlertManager,
                    dependencies=[
                        MonitoringComponentType.PERFORMANCE,
                        MonitoringComponentType.HEALTH,
                        MonitoringComponentType.SECURITY
                    ],
                    priority=7,
                    config_section="alerts"
                )
            ]
            
            for component in components:
                self.component_registry[component.component_type] = component
                
            self.logger.info(f"Initialized component registry with {len(components)} components")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize component registry: {e}")
            
    async def start_monitoring(self, components: Optional[List[MonitoringComponentType]] = None):
        """Start monitoring with specified components or all enabled components"""
        try:
            if self._orchestrator_active:
                self.logger.warning("Monitoring orchestrator already active")
                return
                
            self._orchestrator_active = True
            
            # Determine which components to start
            if components is None:
                components_to_start = [
                    comp_type for comp_type, registry in self.component_registry.items()
                    if registry.enabled and registry.auto_start
                ]
            else:
                components_to_start = components
                
            # Start components in dependency order
            await self._start_components_by_priority(components_to_start)
            
            # Start orchestrator monitoring loop
            self._orchestrator_task = asyncio.create_task(self._orchestrator_loop())
            
            self.logger.info(f"Started monitoring orchestrator with {len(self.active_components)} components")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self._orchestrator_active = False
            
    async def stop_monitoring(self):
        """Stop all monitoring components"""
        try:
            self._orchestrator_active = False
            
            if self._orchestrator_task:
                self._orchestrator_task.cancel()
                try:
                    await self._orchestrator_task
                except asyncio.CancelledError:
                    pass
                    
            # Stop all components in reverse priority order
            await self._stop_components_by_priority()
            
            self.logger.info("Stopped monitoring orchestrator")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            
    async def _start_components_by_priority(self, components_to_start: List[MonitoringComponentType]):
        """Start components in dependency order"""
        try:
            # Sort components by priority
            sorted_components = sorted(
                components_to_start,
                key=lambda comp: self.component_registry[comp].priority
            )
            
            for comp_type in sorted_components:
                await self._start_component(comp_type)
                
        except Exception as e:
            self.logger.error(f"Failed to start components: {e}")
            
    async def _start_component(self, comp_type: MonitoringComponentType):
        """Start individual monitoring component"""
        try:
            registry = self.component_registry.get(comp_type)
            if not registry or not registry.enabled:
                return
                
            # Check dependencies
            for dep in registry.dependencies:
                if dep not in self.active_components:
                    self.logger.warning(f"Dependency {dep.value} not started for {comp_type.value}")
                    # Start dependency first
                    await self._start_component(dep)
                    
            # Create component instance
            component = registry.component_class(self.settings)
            
            # Start the component
            if hasattr(component, 'start_monitoring'):
                await component.start_monitoring()
                
            self.active_components[comp_type] = component
            self.component_status[comp_type] = "running"
            
            self.logger.info(f"Started monitoring component: {comp_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to start component {comp_type.value}: {e}")
            self.component_status[comp_type] = "failed"
            
    async def _stop_components_by_priority(self):
        """Stop components in reverse priority order"""
        try:
            # Sort components by reverse priority
            sorted_components = sorted(
                self.active_components.keys(),
                key=lambda comp: self.component_registry[comp].priority,
                reverse=True
            )
            
            for comp_type in sorted_components:
                await self._stop_component(comp_type)
                
        except Exception as e:
            self.logger.error(f"Failed to stop components: {e}")
            
    async def _stop_component(self, comp_type: MonitoringComponentType):
        """Stop individual monitoring component"""
        try:
            component = self.active_components.get(comp_type)
            if not component:
                return
                
            # Stop the component
            if hasattr(component, 'stop_monitoring'):
                await component.stop_monitoring()
                
            del self.active_components[comp_type]
            self.component_status[comp_type] = "stopped"
            
            self.logger.info(f"Stopped monitoring component: {comp_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to stop component {comp_type.value}: {e}")
            self.component_status[comp_type] = "error"
            
    async def _orchestrator_loop(self):
        """Main orchestrator monitoring loop"""
        while self._orchestrator_active:
            try:
                await self._health_check_components()
                await self._collect_orchestrator_metrics()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Orchestrator loop error: {e}")
                await asyncio.sleep(60)
                
    async def _health_check_components(self):
        """Health check all active components"""
        try:
            for comp_type, component in self.active_components.items():
                try:
                    # Check if component has health check method
                    if hasattr(component, 'health_check'):
                        health_status = await component.health_check()
                        if health_status:
                            self.component_status[comp_type] = "healthy"
                        else:
                            self.component_status[comp_type] = "unhealthy"
                    else:
                        # Assume healthy if no health check method
                        self.component_status[comp_type] = "running"
                        
                except Exception as e:
                    self.logger.error(f"Health check failed for {comp_type.value}: {e}")
                    self.component_status[comp_type] = "unhealthy"
                    
        except Exception as e:
            self.logger.error(f"Failed to health check components: {e}")
            
    async def _collect_orchestrator_metrics(self):
        """Collect orchestrator metrics"""
        try:
            metrics = {
                'active_components': len(self.active_components),
                'total_components': len(self.component_registry),
                'healthy_components': len([
                    status for status in self.component_status.values()
                    if status in ["running", "healthy"]
                ]),
                'component_status': dict(self.component_status),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store metrics in cache if available
            if hasattr(self, 'cache'):
                await self.cache.set(
                    "monitoring_orchestrator_metrics",
                    json.dumps(metrics),
                    expire=300  # 5 minutes
                )
                
        except Exception as e:
            self.logger.error(f"Failed to collect orchestrator metrics: {e}")
            
    async def get_component(self, comp_type: MonitoringComponentType) -> Optional[Any]:
        """Get active monitoring component"""
        return self.active_components.get(comp_type)
        
    async def restart_component(self, comp_type: MonitoringComponentType):
        """Restart specific monitoring component"""
        try:
            if comp_type in self.active_components:
                await self._stop_component(comp_type)
                
            await self._start_component(comp_type)
            
            self.logger.info(f"Restarted monitoring component: {comp_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to restart component {comp_type.value}: {e}")
            
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        try:
            return {
                'orchestrator_active': self._orchestrator_active,
                'total_components': len(self.component_registry),
                'active_components': len(self.active_components),
                'component_status': dict(self.component_status),
                'component_registry': {
                    comp_type.value: registry.to_dict()
                    for comp_type, registry in self.component_registry.items()
                },
                'health_summary': {
                    'healthy': len([s for s in self.component_status.values() if s in ["running", "healthy"]]),
                    'unhealthy': len([s for s in self.component_status.values() if s in ["unhealthy", "failed"]]),
                    'stopped': len([s for s in self.component_status.values() if s == "stopped"])
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get monitoring status: {e}")
            return {}


class MonitoringComponentFactory:
    """Factory for creating monitoring components"""
    
    @staticmethod
    def create_component(component_type: MonitoringComponentType, settings: Settings) -> Any:
        """Create monitoring component instance"""
        component_map = {
            MonitoringComponentType.PERFORMANCE: DatabasePerformanceMonitor,
            MonitoringComponentType.QUERY: QueryAnalyzer,
            MonitoringComponentType.CONNECTION: ConnectionMonitor,
            MonitoringComponentType.METRICS: MetricsCollector,
            MonitoringComponentType.ALERTS: DatabaseAlertManager,
            MonitoringComponentType.HEALTH: DatabaseHealthChecker,
            MonitoringComponentType.SLOW_QUERY: SlowQueryDetector,
            MonitoringComponentType.RESOURCE: ResourceMonitor,
            MonitoringComponentType.BACKUP: BackupMonitor,
            MonitoringComponentType.SECURITY: DatabaseSecurityMonitor,
            MonitoringComponentType.COMPLIANCE: ComplianceMonitor,
            MonitoringComponentType.COST: DatabaseCostMonitor,
            MonitoringComponentType.AI_INSIGHTS: DatabaseAIInsights
        }
        
        component_class = component_map.get(component_type)
        if not component_class:
            raise ValueError(f"Unknown component type: {component_type}")
            
        return component_class(settings)


# Global orchestrator instance
_orchestrator: Optional[MonitoringOrchestrator] = None


async def create_monitoring_index(settings: Settings) -> MonitoringOrchestrator:
    """Create and configure monitoring orchestrator"""
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = MonitoringOrchestrator(settings)
        
    return _orchestrator


async def get_monitoring_orchestrator() -> Optional[MonitoringOrchestrator]:
    """Get global monitoring orchestrator"""
    return _orchestrator


async def start_all_monitoring(settings: Settings, components: Optional[List[MonitoringComponentType]] = None):
    """Start all monitoring components"""
    orchestrator = await create_monitoring_index(settings)
    await orchestrator.start_monitoring(components)
    return orchestrator


async def stop_all_monitoring():
    """Stop all monitoring components"""
    if _orchestrator:
        await _orchestrator.stop_monitoring()


# Convenience functions for component access
async def get_performance_monitor() -> Optional[DatabasePerformanceMonitor]:
    """Get performance monitoring component"""
    if _orchestrator:
        return await _orchestrator.get_component(MonitoringComponentType.PERFORMANCE)
    return None


async def get_query_analyzer() -> Optional[QueryAnalyzer]:
    """Get query analysis component"""
    if _orchestrator:
        return await _orchestrator.get_component(MonitoringComponentType.QUERY)
    return None


async def get_security_monitor() -> Optional[DatabaseSecurityMonitor]:
    """Get security monitoring component"""
    if _orchestrator:
        return await _orchestrator.get_component(MonitoringComponentType.SECURITY)
    return None


async def get_ai_insights() -> Optional[DatabaseAIInsights]:
    """Get AI insights component"""
    if _orchestrator:
        return await _orchestrator.get_component(MonitoringComponentType.AI_INSIGHTS)
    return None


async def get_backup_monitor() -> Optional[BackupMonitor]:
    """Get backup monitoring component"""
    if _orchestrator:
        return await _orchestrator.get_component(MonitoringComponentType.BACKUP)
    return None
