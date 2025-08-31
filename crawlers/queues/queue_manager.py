"""Complete Queue System Usage Example - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/example_usage.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Example & Integration Demonstration
Responsibility: Complete system usage examples, best practices, integration demos
Technologies: Full System Integration, Advanced Configuration, Real-world Scenarios
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
System initialization → Configuration generation → Component setup → Task processing →
Performance monitoring → Security verification → Analytics collection → System optimization
"""

import asyncio

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

import random

# Import queue system components
from . import (
    # Configuration
    create_queue_configuration_manager,
    SecurityProfile,
    EnvironmentType,
    ResourceTier,
    
    # System management
    initialize_queue_system,
    get_system_status,
    perform_health_check,
    optimize_performance,
    
    # Core components
    create_complete_queue_system,
    OptimizationStrategy,
    SecurityLevel,
    CoordinationMode,
    MonitoringLevel,
    DistributionStrategy
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueSystemDemo:
    """
Complete demonstration of queue system capabilities"""
    
    def __init__(self):
        self.config_manager = None
        self.queue_system = None
        self.system_manager = None
        
    async def run_complete_demonstration(self):
        """
Run complete system demonstration"""
        
        logger.info("🚀 Starting IA-Influencer-Agent Queue System Demonstration")
        logger.info("=" * 80)
        logger.info("Author: Fahed Mlaiel (mlaiel@live.de)")
        logger.info("Demonstration: Complete Queue Management System")
        logger.info("=" * 80)
        
        try:
            # Step 1: Configuration Management
            await self._demonstrate_configuration_management()
            
            # Step 2: System Initialization
            await self._demonstrate_system_initialization()
            
            # Step 3: Basic Queue Operations
            await self._demonstrate_basic_operations()
            
            # Step 4: Advanced Features
            await self._demonstrate_advanced_features()
            
            # Step 5: Performance Monitoring
            await self._demonstrate_performance_monitoring()
            
            # Step 6: Security Features
            await self._demonstrate_security_features()
            
            # Step 7: System Optimization
            await self._demonstrate_optimization()
            
            # Step 8: Health Management
            await self._demonstrate_health_management()
            
            logger.info("✅ Complete demonstration finished successfully")
            
        except Exception as e:
            logger.error(f"💥 Demonstration error: {e}")
            raise
    
    async def _demonstrate_configuration_management(self):
        """Demonstrate configuration management capabilities"""
        
        logger.info("\n📋 Step 1: Configuration Management Demonstration")
        logger.info("-" * 50)
        
        # Create configuration manager
        self.config_manager = create_queue_configuration_manager("./demo_config")
        
        # Generate optimal configuration for different scenarios
        scenarios = [
            ("Development Environment", SecurityProfile.BASIC, "balanced"),
            ("Production Environment", SecurityProfile.ENHANCED, "speed"),
            ("High-Security Environment", SecurityProfile.MAXIMUM, "memory")
        ]
        
        for scenario_name, security_profile, performance_priority in scenarios:
            logger.info(f"\n🎯 Generating configuration for: {scenario_name}")
            
            config = self.config_manager.generate_optimal_configuration(
                security_profile=security_profile,
                performance_priority=performance_priority
            )
            
            # Validate configuration
            validation = self.config_manager.validate_configuration(config)
            
            logger.info(f"Configuration valid: {validation['valid']}")
            if validation['warnings']:
                logger.warning(f"Warnings: {len(validation['warnings'])}")
            if validation['recommendations']:
                logger.info(f"Recommendations: {len(validation['recommendations'])}")
        
        # Export configuration template
        template_path = self.config_manager.export_configuration_template()
        logger.info(f"📄 Configuration template exported to: {template_path}")
    
    async def _demonstrate_system_initialization(self):
        """Demonstrate system initialization"""
        
        logger.info("\n🚀 Step 2: System Initialization Demonstration")
        logger.info("-" * 50)
        
        # Initialize system with optimal configuration
        config = self.config_manager.generate_optimal_configuration(
            security_profile=SecurityProfile.STANDARD,
            performance_priority="balanced"
        )
        
        # Initialize the queue system
        initialization_result = await initialize_queue_system({
            'max_workers': config.max_workers,
            'max_queue_size': config.max_queue_size,
            'analytics_retention_days': config.metrics_retention_days,
            'enable_monitoring': config.monitoring_enabled,
            'enable_diagnostics': True,
            'enable_auto_recovery': config.auto_recovery_enabled
        })
        
        logger.info(f"Initialization status: {initialization_result['status']}")
        logger.info(f"Startup time: {initialization_result.get('startup_time', 0):.2f}s")
        logger.info(f"Components: {list(initialization_result.get('components', {}).keys())}")
    
    async def _demonstrate_basic_operations(self):
        """Demonstrate basic queue operations"""
        
        logger.info("\n⚙️ Step 3: Basic Operations Demonstration")
        logger.info("-" * 50)
        
        # Get system status
        status = await get_system_status()
        logger.info(f"System status: {status['system_status']}")
        logger.info(f"Uptime: {status.get('uptime_seconds', 0):.2f}s")
        
        # Create sample tasks
        sample_tasks = [
            {
                'task_id': f'demo_task_{i}',
                'task_type': 'crawler_task',
                'priority': random.randint(1, 10),
                'url': f'https://example{i}.com',
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'demo_task': True
                }
            }
            for i in range(20)
        ]
        
        logger.info(f"📤 Generated {len(sample_tasks)} demo tasks")
        
        # Simulate task processing
        logger.info("🔄 Simulating task processing...")
        await asyncio.sleep(2)  # Simulate processing time
        
        logger.info("✅ Basic operations completed")
    
    async def _demonstrate_advanced_features(self):
        """Demonstrate advanced system features"""
        
        logger.info("\n🎯 Step 4: Advanced Features Demonstration")
        logger.info("-" * 50)
        
        # Get current system status to access components
        status = await get_system_status()
        
        if 'component_statuses' in status:
            components = status['component_statuses']
            
            # Demonstrate orchestrator features
            if 'orchestrator' in components:
                logger.info("🎭 Orchestrator features:")
                orchestrator_status = components['orchestrator']
                logger.info(f"  Active workers: {orchestrator_status.get('resources', {}).get('active_workers', 0)}")
                logger.info(f"  Success rate: {orchestrator_status.get('performance', {}).get('success_rate', 0):.2%}")
            
            # Demonstrate monitoring features
            if 'monitor' in components:
                logger.info("📊 Monitoring features:")
                monitor_status = components['monitor']
                logger.info(f"  Health score: {monitor_status.get('health_score', 0):.2f}")
                logger.info(f"  Active alerts: {monitor_status.get('stats', {}).get('active_alerts', 0)}")
            
            # Demonstrate security features
            if 'security' in components:
                logger.info("🔒 Security features:")
                security_status = components['security']
                logger.info(f"  Security level: {security_status.get('security_level', 'unknown')}")
                logger.info(f"  Encryption active: {security_status.get('encryption_active', False)}")
            
            # Demonstrate coordination features
            if 'coordination' in components:
                logger.info("🤝 Coordination features:")
                coordination_status = components['coordination']
                logger.info(f"  Coordination mode: {coordination_status.get('coordination_mode', 'unknown')}")
                logger.info(f"  Active nodes: {coordination_status.get('active_nodes', 0)}")
    
    async def _demonstrate_performance_monitoring(self):
        """Demonstrate performance monitoring capabilities"""
        
        logger.info("\n📈 Step 5: Performance Monitoring Demonstration")
        logger.info("-" * 50)
        
        # Get performance summary
        status = await get_system_status()
        performance_summary = status.get('performance_summary', {})
        
        logger.info("📊 Performance Metrics:")
        logger.info(f"  Total measurements: {performance_summary.get('total_measurements', 0)}")
        logger.info(f"  Recent measurements: {performance_summary.get('recent_measurements', 0)}")
        
        # Display average metrics if available
        avg_metrics = performance_summary.get('average_metrics', {})
        if avg_metrics:
            logger.info("📈 Average Performance Metrics:")
            for metric, value in avg_metrics.items():
                if isinstance(value, float):
                    logger.info(f"  {metric}: {value:.2f}")
                else:
                    logger.info(f"  {metric}: {value}")
        
        # Get tuning recommendations
        recommendations = self.config_manager.get_performance_tuning_recommendations()
        if recommendations:
            logger.info("💡 Performance Recommendations:")
            for i, recommendation in enumerate(recommendations[:5], 1):
                logger.info(f"  {i}. {recommendation}")
    
    async def _demonstrate_security_features(self):
        """Demonstrate security features"""
        
        logger.info("\n🔒 Step 6: Security Features Demonstration")
        logger.info("-" * 50)
        
        # Test different security profiles
        security_profiles = [
            SecurityProfile.BASIC,
            SecurityProfile.STANDARD,
            SecurityProfile.ENHANCED,
            SecurityProfile.MAXIMUM
        ]
        
        for profile in security_profiles:
            logger.info(f"\n🛡️ Testing {profile.value} security profile:")
            
            config = self.config_manager.generate_optimal_configuration(
                security_profile=profile,
                performance_priority="balanced"
            )
            
            logger.info(f"  Encryption: {'Enabled' if config.encryption_enabled else 'Disabled'}")
            logger.info(f"  Authentication: {'Required' if config.auth_required else 'Optional'}")
            logger.info(f"  SSL: {'Enabled' if config.ssl_enabled else 'Disabled'}")
            logger.info(f"  Token expiry: {config.token_expiry_hours}h")
        
        logger.info("\n🔐 Security best practices applied")
    
    async def _demonstrate_optimization(self):
        """Demonstrate system optimization"""
        
        logger.info("\n⚡ Step 7: System Optimization Demonstration")
        logger.info("-" * 50)
        
        # Trigger system optimization
        logger.info("🔧 Starting system optimization...")
        
        optimization_result = await optimize_performance()
        
        logger.info(f"Optimization status: {optimization_result['status']}")
        
        if optimization_result['status'] == 'completed':
            results = optimization_result.get('optimization_results', {})
            
            if 'performance_optimization' in results:
                perf_result = results['performance_optimization']
                logger.info(f"Performance optimization: {perf_result.get('status', 'unknown')}")
            
            if 'coordination_optimization' in results:
                coord_result = results['coordination_optimization']
                logger.info(f"Coordination optimization: {coord_result.get('status', 'completed')}")
            
            if 'security_audit' in results:
                security_result = results['security_audit']
                logger.info(f"Security audit: {security_result.get('status', 'completed')}")
        
        logger.info("✅ System optimization completed")
    
    async def _demonstrate_health_management(self):
        """Demonstrate health management"""
        
        logger.info("\n💓 Step 8: Health Management Demonstration")
        logger.info("-" * 50)
        
        # Perform comprehensive health check
        health_result = await perform_health_check()
        
        logger.info(f"Overall health: {health_result['overall_health']}")
        logger.info(f"Health score: {health_result['health_score']:.2f}")
        
        # Show component health
        component_health = health_result.get('component_health', {})
        if component_health:
            logger.info("\n🏥 Component Health Status:")
            for component, health_data in component_health.items():
                if isinstance(health_data, dict):
                    status = health_data.get('status', 'unknown')
                    score = health_data.get('health_score', 0)
                    logger.info(f"  {component}: {status} (score: {score:.2f})")
        
        # Show issues and recommendations
        issues = health_result.get('issues', [])
        if issues:
            logger.info("\n⚠️ Health Issues:")
            for issue in issues[:3]:
                logger.info(f"  - {issue}")
        
        recommendations = health_result.get('recommendations', [])
        if recommendations:
            logger.info("\n💡 Health Recommendations:")
            for recommendation in recommendations[:3]:
                logger.info(f"  - {recommendation}")


class SimpleUsageExample:
    """Simple usage example for quick start"""
    
    @staticmethod
    async def quick_start_example():
        """
Quick start example with minimal setup"""
        
        logger.info("\n🚀 Quick Start Example")
        logger.info("=" * 40)
        
        # 1. Initialize system with default settings
        result = await initialize_queue_system({
            'max_workers': 20,
            'max_queue_size': 5000,
            'enable_monitoring': True
        })
        
        logger.info(f"✅ System initialized: {result['status']}")
        
        # 2. Check system status
        status = await get_system_status()
        logger.info(f"📊 System status: {status['system_status']}")
        
        # 3. Perform health check
        health = await perform_health_check()
        logger.info(f"💓 Health score: {health['health_score']:.2f}")
        
        # 4. Trigger optimization
        optimization = await optimize_performance()
        logger.info(f"⚡ Optimization: {optimization['status']}")
        
        logger.info("🎉 Quick start completed!")


class ProductionDeploymentExample:
    """Production deployment example with full configuration"""
    
    @staticmethod
    async def production_deployment_example():
        """
Production deployment example"""
        
        logger.info("\n🏭 Production Deployment Example")
        logger.info("=" * 50)
        
        # 1. Create configuration manager
        config_manager = create_queue_configuration_manager("/opt/ia-influencer/config")
        
        # 2. Generate production configuration
        config = config_manager.generate_optimal_configuration(
            security_profile=SecurityProfile.ENHANCED,
            performance_priority="speed",
            custom_overrides={
                'max_workers': 100,
                'max_queue_size': 50000,
                'metrics_retention_days': 180,
                'enable_monitoring': True,
                'enable_analytics': True
            }
        )
        
        logger.info("📋 Production configuration generated")
        
        # 3. Validate configuration
        validation = config_manager.validate_configuration(config)
        
        if not validation['valid']:
            logger.error("❌ Configuration validation failed")
            for error in validation['errors']:
                logger.error(f"  Error: {error}")
            return
        
        # 4. Initialize production system
        result = await initialize_queue_system({
            'max_workers': config.max_workers,
            'max_queue_size': config.max_queue_size,
            'analytics_retention_days': config.metrics_retention_days,
            'enable_monitoring': config.monitoring_enabled,
            'enable_diagnostics': True,
            'enable_auto_recovery': config.auto_recovery_enabled
        })
        
        logger.info(f"🚀 Production system: {result['status']}")
        
        # 5. Setup monitoring loop
        await ProductionDeploymentExample._production_monitoring_loop()
    
    @staticmethod
    async def _production_monitoring_loop():
        """Production monitoring loop"""
        
        logger.info("📊 Starting production monitoring...")
        
        for i in range(3):  # Run for 3 iterations in demo
            # Health check
            health = await perform_health_check()
            logger.info(f"Health check {i+1}: {health['overall_health']} (score: {health['health_score']:.2f})")
            
            # Performance optimization
            if health['health_score'] < 0.8:
                logger.info("⚡ Triggering optimization due to low health score")
                await optimize_performance()
            
            await asyncio.sleep(5)  # Wait 5 seconds between checks
        
        logger.info("✅ Production monitoring completed")


# Main demonstration runner
async def run_all_examples():
    """Run all example demonstrations"""
    
    logger.info("🎭 IA-Influencer-Agent Queue System - Complete Examples")
    logger.info("=" * 80)
    logger.info("Author: Fahed Mlaiel (mlaiel@live.de)")
    logger.info("=" * 80)
    
    try:
        # Run quick start example
        await SimpleUsageExample.quick_start_example()
        
        await asyncio.sleep(2)
        
        # Run complete demonstration
        demo = QueueSystemDemo()
        await demo.run_complete_demonstration()
        
        await asyncio.sleep(2)
        
        # Run production example
        await ProductionDeploymentExample.production_deployment_example()
        
        logger.info("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Example execution failed: {e}")
        raise


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())


# Export example classes
__all__ = [
    'QueueSystemDemo',
    'SimpleUsageExample', 
    'ProductionDeploymentExample',
    'run_all_examples'
]
