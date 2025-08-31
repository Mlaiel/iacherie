"""Queue Management System Index - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue System Entry Point & Orchestration
Responsibility: Main entry point for complete queue management ecosystem
Technologies: Multi-Component Integration, System Orchestration, Health Management
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
System initialization → Component discovery → Health verification → Service orchestration →
Performance monitoring → Security enforcement → Continuous optimization → Global coordination
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from . import (
    create_complete_queue_system,
    OptimizationStrategy,
    SecurityLevel,
    CoordinationMode,
    MonitoringLevel,
    DistributionStrategy
)

logger = logging.getLogger(__name__)


class QueueSystemManager:
    """Central manager for the complete queue management ecosystem"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.queue_system = None
        self.system_status = "not_initialized"
        self.startup_timestamp = None
        self.performance_history = []
        
    async def initialize_complete_system(self) -> Dict[str, Any]:
        """Initialize the complete queue management system"""        
        logger.info("🚀 Starting IA-Influencer-Agent Queue Management System")
        logger.info("=" * 80)
        logger.info("Author: Fahed Mlaiel (mlaiel@live.de)")
        logger.info("System: Industrial Crawler Queue Management")
        logger.info("=" * 80)
        
        try:
            self.system_status = "initializing"
            self.startup_timestamp = datetime.now()
            
            # Create complete queue system with advanced features
            self.queue_system = await create_complete_queue_system(
                max_workers=self.config.get('max_workers', 100),
                max_queue_size=self.config.get('max_queue_size', 50000),
                analytics_retention_days=self.config.get('analytics_retention_days', 90),
                enable_monitoring=self.config.get('enable_monitoring', True),
                enable_diagnostics=self.config.get('enable_diagnostics', True),
                enable_auto_recovery=self.config.get('enable_auto_recovery', True)
            )
            
            if self.queue_system.get('status') == 'initialized':
                self.system_status = "operational"
                
                # Log system components
                await self._log_system_components()
                
                # Start health monitoring
                await self._start_health_monitoring()
                
                # Start performance tracking
                await self._start_performance_tracking()
                
                logger.info("✅ Queue Management System successfully initialized")
                logger.info(f"🎯 Features enabled: {list(self.queue_system['features'].keys())}")
                
                return {
                    'status': 'success',
                    'message': 'Queue Management System operational',
                    'components': self._get_component_summary(),
                    'startup_time': (datetime.now() - self.startup_timestamp).total_seconds()
                }
            else:
                self.system_status = "failed"
                error_msg = self.queue_system.get('error', 'Unknown initialization error')
                logger.error(f"❌ System initialization failed: {error_msg}")
                
                return {
                    'status': 'failed',
                    'message': f'Initialization failed: {error_msg}',
                    'components': {},
                    'startup_time': 0
                }
                
        except Exception as e:
            self.system_status = "error"
            logger.error(f"💥 Critical error during initialization: {e}")
            
            return {
                'status': 'error',
                'message': f'Critical initialization error: {str(e)}',
                'components': {},
                'startup_time': 0
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""        
        if not self.queue_system:
            return {
                'system_status': self.system_status,
                'message': 'System not initialized',
                'uptime': 0,
                'components': {}
            }
        
        uptime = (datetime.now() - self.startup_timestamp).total_seconds() if self.startup_timestamp else 0
        
        # Collect component statuses
        component_statuses = {}
        
        try:
            # Queue orchestrator status
            if 'orchestrator' in self.queue_system:
                orchestrator_status = await self.queue_system['orchestrator'].get_orchestration_status()
                component_statuses['orchestrator'] = orchestrator_status
            
            # Monitoring status
            if 'monitor' in self.queue_system and self.queue_system['monitor']:
                monitor_status = await self.queue_system['monitor'].get_monitoring_status()
                component_statuses['monitor'] = monitor_status
            
            # Diagnostics status
            if 'diagnostics' in self.queue_system and self.queue_system['diagnostics']:
                diagnostics_status = await self.queue_system['diagnostics'].get_diagnostic_status()
                component_statuses['diagnostics'] = diagnostics_status
            
            # Security status
            if 'security_manager' in self.queue_system and self.queue_system['security_manager']:
                security_status = await self.queue_system['security_manager'].get_security_status()
                component_statuses['security'] = security_status
            
            # Coordination status
            if 'coordination_engine' in self.queue_system and self.queue_system['coordination_engine']:
                coordination_status = await self.queue_system['coordination_engine'].get_coordination_status()
                component_statuses['coordination'] = coordination_status
            
        except Exception as e:
            logger.error(f"Error collecting component statuses: {e}")
        
        return {
            'system_status': self.system_status,
            'uptime_seconds': uptime,
            'startup_timestamp': self.startup_timestamp.isoformat() if self.startup_timestamp else None,
            'enabled_features': self.queue_system.get('features', {}),
            'component_statuses': component_statuses,
            'performance_summary': await self._get_performance_summary()
        }
    
    async def perform_system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""        
        if not self.queue_system:
            return {
                'overall_health': 'critical',
                'health_score': 0.0,
                'issues': ['System not initialized'],
                'recommendations': ['Initialize system first']
            }
        
        health_results = {
            'overall_health': 'healthy',
            'health_score': 1.0,
            'component_health': {},
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Check orchestrator health
            if 'orchestrator' in self.queue_system:
                orchestrator_health = await self._check_orchestrator_health()
                health_results['component_health']['orchestrator'] = orchestrator_health
            
            # Check monitoring health
            if 'monitor' in self.queue_system and self.queue_system['monitor']:
                monitor_health = await self._check_monitor_health()
                health_results['component_health']['monitor'] = monitor_health
            
            # Check diagnostics health
            if 'diagnostics' in self.queue_system and self.queue_system['diagnostics']:
                diagnostics_health = await self._check_diagnostics_health()
                health_results['component_health']['diagnostics'] = diagnostics_health
            
            # Calculate overall health score
            component_scores = [
                health['health_score'] for health in health_results['component_health'].values()
                if isinstance(health, dict) and 'health_score' in health
            ]
            
            if component_scores:
                overall_score = sum(component_scores) / len(component_scores)
                health_results['health_score'] = overall_score
                
                if overall_score >= 0.9:
                    health_results['overall_health'] = 'excellent'
                elif overall_score >= 0.8:
                    health_results['overall_health'] = 'good'
                elif overall_score >= 0.6:
                    health_results['overall_health'] = 'fair'
                elif overall_score >= 0.4:
                    health_results['overall_health'] = 'poor'
                else:
                    health_results['overall_health'] = 'critical'
        
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            health_results.update({
                'overall_health': 'error',
                'health_score': 0.0,
                'issues': [f'Health check error: {str(e)}'],
                'recommendations': ['Investigate system errors']
            })
        
        return health_results
    
    async def optimize_system_performance(self) -> Dict[str, Any]:
        """Trigger system-wide performance optimization"""        
        if not self.queue_system:
            return {
                'status': 'failed',
                'message': 'System not initialized'
            }
        
        optimization_results = {}
        
        try:
            # Trigger queue optimization
            if 'optimizer' in self.queue_system and self.queue_system['optimizer']:
                optimizer = self.queue_system['optimizer']
                opportunities = await optimizer.analyze_performance_opportunities()
                
                if opportunities:
                    plan = await optimizer.create_optimization_plan(opportunities)
                    result = await optimizer.execute_optimization_plan(plan)
                    optimization_results['performance_optimization'] = result
            
            # Trigger coordination optimization
            if 'coordination_engine' in self.queue_system and self.queue_system['coordination_engine']:
                coordination_result = await self.queue_system['coordination_engine'].coordinate_queue_operations(
                    'resource_optimization'
                )
                optimization_results['coordination_optimization'] = coordination_result
            
            # Trigger security optimization
            if 'security_manager' in self.queue_system and self.queue_system['security_manager']:
                security_audit = await self.queue_system['security_manager'].perform_security_audit()
                optimization_results['security_audit'] = security_audit
            
            return {
                'status': 'completed',
                'optimization_results': optimization_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during system optimization: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'partial_results': optimization_results
            }
    
    async def shutdown_system(self) -> Dict[str, Any]:
        """Gracefully shutdown the queue management system"""        
        logger.info("🛑 Initiating graceful system shutdown")
        
        shutdown_results = {}
        
        try:
            # Stop monitoring
            if 'monitor' in self.queue_system and self.queue_system['monitor']:
                await self.queue_system['monitor'].stop_monitoring()
                shutdown_results['monitor'] = 'stopped'
            
            # Stop diagnostics
            if 'diagnostics' in self.queue_system and self.queue_system['diagnostics']:
                await self.queue_system['diagnostics'].stop_diagnostics()
                shutdown_results['diagnostics'] = 'stopped'
            
            # Stop optimization
            if 'optimizer' in self.queue_system and self.queue_system['optimizer']:
                await self.queue_system['optimizer'].stop_continuous_optimization()
                shutdown_results['optimizer'] = 'stopped'
            
            # Shutdown orchestrator
            if 'orchestrator' in self.queue_system:
                await self.queue_system['orchestrator'].shutdown()
                shutdown_results['orchestrator'] = 'stopped'
            
            self.system_status = "shutdown"
            
            logger.info("✅ System shutdown completed successfully")
            
            return {
                'status': 'success',
                'shutdown_results': shutdown_results,
                'final_uptime': (datetime.now() - self.startup_timestamp).total_seconds() if self.startup_timestamp else 0
            }
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'partial_shutdown': shutdown_results
            }
    
    # Private methods
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default system configuration"""        
        return {
            'max_workers': 100,
            'max_queue_size': 50000,
            'analytics_retention_days': 90,
            'enable_monitoring': True,
            'enable_diagnostics': True,
            'enable_auto_recovery': True,
            'optimization_strategy': OptimizationStrategy.BALANCED_PERFORMANCE,
            'security_level': SecurityLevel.ENHANCED,
            'coordination_mode': CoordinationMode.COOPERATIVE,
            'monitoring_level': MonitoringLevel.COMPREHENSIVE,
            'distribution_strategy': DistributionStrategy.ML_PREDICTED
        }
    
    async def _log_system_components(self):
        """Log information about system components"""        
        components = self.queue_system.keys()
        features = self.queue_system.get('features', {})
        
        logger.info("📋 System Components Initialized:")
        for component in components:
            if component != 'features' and component != 'status':
                status = "✅" if self.queue_system[component] else "❌"
                logger.info(f"  {status} {component}")
        
        logger.info("🎯 Advanced Features:")
        for feature, enabled in features.items():
            status = "✅" if enabled else "❌"
            logger.info(f"  {status} {feature}")
    
    async def _start_health_monitoring(self):
        """Start system health monitoring"""        
        async def health_monitoring_loop():
            while self.system_status == "operational":
                try:
                    health_status = await self.perform_system_health_check()
                    
                    if health_status['health_score'] < 0.5:
                        logger.warning(f"⚠️ System health degraded: {health_status['health_score']:.2f}")
                    
                    await asyncio.sleep(300)  # Check every 5 minutes
                    
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(health_monitoring_loop())
        logger.info("💓 System health monitoring started")
    
    async def _start_performance_tracking(self):
        """Start performance tracking"""        
        async def performance_tracking_loop():
            while self.system_status == "operational":
                try:
                    performance_data = await self._collect_performance_data()
                    self.performance_history.append(performance_data)
                    
                    # Keep only recent history (last 1000 entries)
                    if len(self.performance_history) > 1000:
                        self.performance_history = self.performance_history[-1000:]
                    
                    await asyncio.sleep(60)  # Collect every minute
                    
                except Exception as e:
                    logger.error(f"Performance tracking error: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(performance_tracking_loop())
        logger.info("📊 Performance tracking started")
    
    def _get_component_summary(self) -> Dict[str, str]:
        """Get summary of system components"""        
        summary = {}
        
        if self.queue_system:
            for component_name, component in self.queue_system.items():
                if component_name not in ['features', 'status']:
                    if component:
                        summary[component_name] = "initialized"
                    else:
                        summary[component_name] = "not_available"
        
        return summary
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""        
        if not self.performance_history:
            return {'status': 'no_data'}
        
        recent_data = self.performance_history[-10:]  # Last 10 measurements
        
        # Calculate averages
        avg_metrics = {}
        if recent_data:
            for key in recent_data[0].keys():
                if isinstance(recent_data[0][key], (int, float)):
                    values = [data[key] for data in recent_data if isinstance(data.get(key), (int, float))]
                    if values:
                        avg_metrics[f'avg_{key}'] = sum(values) / len(values)
        
        return {
            'recent_measurements': len(recent_data),
            'total_measurements': len(self.performance_history),
            'average_metrics': avg_metrics,
            'last_measurement': recent_data[-1] if recent_data else None
        }
    
    async def _collect_performance_data(self) -> Dict[str, Any]:
        """Collect current performance data"""        
        data = {
            'timestamp': datetime.now().isoformat(),
            'uptime': (datetime.now() - self.startup_timestamp).total_seconds() if self.startup_timestamp else 0
        }
        
        try:
            # Collect orchestrator metrics
            if 'orchestrator' in self.queue_system:
                status = await self.queue_system['orchestrator'].get_orchestration_status()
                data.update({
                    'active_workers': status.get('resources', {}).get('active_workers', 0),
                    'success_rate': status.get('performance', {}).get('success_rate', 0),
                    'avg_response_time': status.get('performance', {}).get('avg_response_time_ms', 0)
                })
            
            # Collect monitoring metrics
            if 'monitor' in self.queue_system and self.queue_system['monitor']:
                monitor_status = await self.queue_system['monitor'].get_monitoring_status()
                data.update({
                    'health_score': monitor_status.get('health_score', 0),
                    'active_alerts': monitor_status.get('stats', {}).get('active_alerts', 0)
                })
        
        except Exception as e:
            logger.error(f"Error collecting performance data: {e}")
            data['collection_error'] = str(e)
        
        return data
    
    async def _check_orchestrator_health(self) -> Dict[str, Any]:
        """Check orchestrator health"""        
        try:
            status = await self.queue_system['orchestrator'].get_orchestration_status()
            
            health_score = 1.0
            issues = []
            
            # Check success rate
            success_rate = status.get('performance', {}).get('success_rate', 0)
            if success_rate < 0.9:
                health_score -= 0.2
                issues.append(f'Low success rate: {success_rate:.2%}')
            
            # Check response time
            response_time = status.get('performance', {}).get('avg_response_time_ms', 0)
            if response_time > 5000:  # 5 seconds
                health_score -= 0.2
                issues.append(f'High response time: {response_time}ms')
            
            # Check worker count
            active_workers = status.get('resources', {}).get('active_workers', 0)
            if active_workers == 0:
                health_score -= 0.3
                issues.append('No active workers')
            
            return {
                'component': 'orchestrator',
                'health_score': max(0.0, health_score),
                'status': 'healthy' if health_score >= 0.8 else 'degraded' if health_score >= 0.5 else 'unhealthy',
                'issues': issues
            }
            
        except Exception as e:
            return {
                'component': 'orchestrator',
                'health_score': 0.0,
                'status': 'error',
                'issues': [f'Health check failed: {str(e)}']
            }
    
    async def _check_monitor_health(self) -> Dict[str, Any]:
        """Check monitoring system health"""        
        try:
            status = await self.queue_system['monitor'].get_monitoring_status()
            
            health_score = 1.0
            issues = []
            
            # Check if monitoring is active
            if not status.get('monitoring_active', True):
                health_score -= 0.5
                issues.append('Monitoring not active')
            
            # Check alert count
            active_alerts = status.get('stats', {}).get('active_alerts', 0)
            if active_alerts > 10:
                health_score -= 0.2
                issues.append(f'High alert count: {active_alerts}')
            
            return {
                'component': 'monitor',
                'health_score': max(0.0, health_score),
                'status': 'healthy' if health_score >= 0.8 else 'degraded' if health_score >= 0.5 else 'unhealthy',
                'issues': issues
            }
            
        except Exception as e:
            return {
                'component': 'monitor',
                'health_score': 0.0,
                'status': 'error',
                'issues': [f'Health check failed: {str(e)}']
            }
    
    async def _check_diagnostics_health(self) -> Dict[str, Any]:
        """Check diagnostics system health"""        
        try:
            status = await self.queue_system['diagnostics'].get_diagnostic_status()
            
            health_score = 1.0
            issues = []
            
            # Check overall health score
            overall_health = status.get('overall_health_score', 0)
            if overall_health < 0.8:
                health_score -= 0.3
                issues.append(f'Low system health: {overall_health:.2f}')
            
            # Check for active issues
            active_issues = status.get('active_issues', 0)
            if active_issues > 5:
                health_score -= 0.2
                issues.append(f'High issue count: {active_issues}')
            
            return {
                'component': 'diagnostics',
                'health_score': max(0.0, health_score),
                'status': 'healthy' if health_score >= 0.8 else 'degraded' if health_score >= 0.5 else 'unhealthy',
                'issues': issues
            }
            
        except Exception as e:
            return {
                'component': 'diagnostics',
                'health_score': 0.0,
                'status': 'error',
                'issues': [f'Health check failed: {str(e)}']
            }


# Global system manager instance
_system_manager = None


async def initialize_queue_system(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Initialize the complete queue management system"""    
    global _system_manager
    _system_manager = QueueSystemManager(config)
    return await _system_manager.initialize_complete_system()


async def get_system_status() -> Dict[str, Any]:
    """Get current system status"""    
    if not _system_manager:
        return {
            'status': 'not_initialized',
            'message': 'System not initialized. Call initialize_queue_system() first.'
        }
    
    return await _system_manager.get_system_status()


async def perform_health_check() -> Dict[str, Any]:
    """Perform system health check"""    
    if not _system_manager:
        return {
            'status': 'not_initialized',
            'message': 'System not initialized. Call initialize_queue_system() first.'
        }
    
    return await _system_manager.perform_system_health_check()


async def optimize_performance() -> Dict[str, Any]:
    """Trigger system performance optimization"""    
    if not _system_manager:
        return {
            'status': 'not_initialized',
            'message': 'System not initialized. Call initialize_queue_system() first.'
        }
    
    return await _system_manager.optimize_system_performance()


async def shutdown_system() -> Dict[str, Any]:
    """Shutdown the queue management system"""    
    if not _system_manager:
        return {
            'status': 'not_initialized',
            'message': 'System not initialized.'
        }
    
    return await _system_manager.shutdown_system()


def get_system_manager() -> Optional[QueueSystemManager]:
    """Get the global system manager instance"""    return _system_manager


# Export main functions
__all__ = [
    'QueueSystemManager',
    'initialize_queue_system',
    'get_system_status',
    'perform_health_check',
    'optimize_performance',
    'shutdown_system',
    'get_system_manager'
]
