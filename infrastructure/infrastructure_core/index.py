"""
Infrastructure Core - Central Infrastructure Management Hub
© 2025 Fahed Mlaiel. All rights reserved.

Central orchestration point for all Ainflue infrastructure core components including
disaster recovery, performance optimization, and service orchestration.
"""

# Core orchestration imports
from .core_orchestrator import CoreOrchestrator, OrchestrationState, BusinessWorkflow
from .service_orchestrator import ServiceOrchestrator, ServiceState, ServiceType
from .resource_orchestrator import ResourceOrchestrator, ResourceType
from .deployment_orchestrator import DeploymentOrchestrator, DeploymentStatus

# Disaster recovery imports
from .disaster_core import DisasterCore, DisasterType, DisasterSeverity
from .failover_manager import FailoverManager, FailoverTrigger
from .recovery_orchestrator import RecoveryOrchestrator, RecoveryPriority

# Performance optimization imports
from .cpu_optimizer import CPUOptimizer, CPUOptimizationStrategy
from .memory_optimizer import MemoryOptimizer, MemoryOptimizationStrategy
from .network_optimizer import NetworkOptimizer, NetworkOptimizationStrategy
from .storage_optimizer import StorageOptimizer, StorageOptimizationStrategy

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Infrastructure Core Management for Ainflue Platform"

# Public API exports
__all__ = [
    # Core orchestration
    'CoreOrchestrator',
    'ServiceOrchestrator',
    'ResourceOrchestrator', 
    'DeploymentOrchestrator',
    'OrchestrationState',
    'BusinessWorkflow',
    'ServiceState',
    'ServiceType',
    'ResourceType',
    'DeploymentStatus',
    
    # Disaster recovery
    'DisasterCore',
    'FailoverManager',
    'RecoveryOrchestrator',
    'DisasterType',
    'DisasterSeverity',
    'FailoverTrigger',
    'RecoveryPriority',
    
    # Performance optimization
    'CPUOptimizer',
    'MemoryOptimizer',
    'NetworkOptimizer',
    'StorageOptimizer',
    'CPUOptimizationStrategy',
    'MemoryOptimizationStrategy',
    'NetworkOptimizationStrategy',
    'StorageOptimizationStrategy'
]

# Ainflue platform configuration
AINFLUE_INFRASTRUCTURE_CONFIG = {
    'platform_name': 'Ainflue Creator Platform',
    'creator_workflow_support': True,
    'multi_platform_distribution': 65,
    'ai_agents_supported': 53,
    'languages_supported': 644,
    'enterprise_grade': True,
    'disaster_recovery_enabled': True,
    'auto_scaling_enabled': True,
    'performance_optimization_enabled': True,
    'compliance_frameworks': ['GDPR', 'CCPA', 'DMCA'],
    'supported_regions': ['us-west-2', 'us-east-1', 'eu-west-1', 'ap-southeast-1']
}

def create_master_orchestrator():
    """
    Create and configure master infrastructure orchestrator for Ainflue platform.
    
    Returns:
        CoreOrchestrator: Configured master orchestrator
    """
    return CoreOrchestrator()

def create_disaster_recovery_system():
    """
    Create and configure disaster recovery system for Ainflue platform.
    
    Returns:
        tuple: (DisasterCore, FailoverManager, RecoveryOrchestrator)
    """
    disaster_core = DisasterCore()
    failover_manager = FailoverManager()
    recovery_orchestrator = RecoveryOrchestrator()
    
    return disaster_core, failover_manager, recovery_orchestrator

def create_performance_optimization_suite():
    """
    Create and configure performance optimization suite for Ainflue platform.
    
    Returns:
        tuple: (CPUOptimizer, MemoryOptimizer, NetworkOptimizer, StorageOptimizer)
    """
    cpu_optimizer = CPUOptimizer()
    memory_optimizer = MemoryOptimizer()
    network_optimizer = NetworkOptimizer()
    storage_optimizer = StorageOptimizer()
    
    return cpu_optimizer, memory_optimizer, network_optimizer, storage_optimizer

# Enterprise integration helpers
def get_ainflue_business_workflows():
    """Get list of supported Ainflue business workflows."""
    return [workflow.value for workflow in BusinessWorkflow]

def get_supported_optimization_strategies():
    """Get all supported optimization strategies."""
    return {
        'cpu': [strategy.value for strategy in CPUOptimizationStrategy],
        'memory': [strategy.value for strategy in MemoryOptimizationStrategy],
        'network': [strategy.value for strategy in NetworkOptimizationStrategy],
        'storage': [strategy.value for strategy in StorageOptimizationStrategy]
    }

def get_disaster_recovery_capabilities():
    """Get disaster recovery capabilities."""
    return {
        'disaster_types': [disaster_type.value for disaster_type in DisasterType],
        'failover_triggers': [trigger.value for trigger in FailoverTrigger],
        'recovery_priorities': [priority.value for priority in RecoveryPriority],
        'auto_recovery_enabled': True,
        'cross_region_support': True,
        'rto_targets': {
            'critical': '5 minutes',
            'high': '15 minutes',
            'medium': '60 minutes'
        },
        'rpo_targets': {
            'critical': '1 minute',
            'high': '5 minutes', 
            'medium': '30 minutes'
        }
    }