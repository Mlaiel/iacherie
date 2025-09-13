"""
Infrastructure Core - Enterprise Infrastructure Management Hub
© 2025 Fahed Mlaiel. All rights reserved.

Central infrastructure management providing backup, failover, orchestration,
and performance optimization for Ainflue creator platform.
"""

from typing import Dict, List, Optional, Any

# Core infrastructure imports
try:
    from .backup_manager import BackupManager
except ImportError:
    BackupManager = None

try:
    from .failover_manager import FailoverManager
except ImportError:
    FailoverManager = None

try:
    from .recovery_orchestrator import RecoveryOrchestrator
except ImportError:
    RecoveryOrchestrator = None

try:
    from .disaster_core import DisasterCore
except ImportError:
    DisasterCore = None

try:
    from .service_orchestrator import ServiceOrchestrator
except ImportError:
    ServiceOrchestrator = None

try:
    from .resource_orchestrator import ResourceOrchestrator
except ImportError:
    ResourceOrchestrator = None

try:
    from .deployment_orchestrator import DeploymentOrchestrator
except ImportError:
    DeploymentOrchestrator = None

try:
    from .core_orchestrator import CoreOrchestrator
except ImportError:
    CoreOrchestrator = None

try:
    from .cpu_optimizer import CPUOptimizer
except ImportError:
    CPUOptimizer = None

try:
    from .memory_optimizer import MemoryOptimizer
except ImportError:
    MemoryOptimizer = None

try:
    from .network_optimizer import NetworkOptimizer
except ImportError:
    NetworkOptimizer = None

try:
    from .storage_optimizer import StorageOptimizer
except ImportError:
    StorageOptimizer = None

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Infrastructure Core Management"

# Exports
__all__ = [
    'BackupManager',
    'FailoverManager', 
    'RecoveryOrchestrator',
    'DisasterCore',
    'ServiceOrchestrator',
    'ResourceOrchestrator',
    'DeploymentOrchestrator',
    'CoreOrchestrator',
    'CPUOptimizer',
    'MemoryOptimizer',
    'NetworkOptimizer',
    'StorageOptimizer'
]

# Configuration for Ainflue creator platform
AINFLUE_INFRASTRUCTURE_CONFIG = {
    'creator_workflow_support': True,
    'multi_platform_distribution': 65,
    'ai_agents_supported': 53,
    'languages_supported': 644,
    'enterprise_grade': True,
    'disaster_recovery_tiers': 4,
    'backup_strategies': 5,
    'orchestration_levels': 3
}