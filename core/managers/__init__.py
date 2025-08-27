"""
Core Managers Module - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Core Managers (Level 3)
Created: 2025-08-19
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
User (créateur) → Upload multi-format → IA protection → SEO pro → 
Matching collaboration → Distribution multi-plateformes → Monétisation avancée
"""

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer"

# Core imports for industrial-grade managers
from typing import Any, Dict, List, Optional, Union, Protocol, TypeVar, Generic
import logging
import asyncio
from abc import ABC, abstractmethod

# Configuration logging module
logger = logging.getLogger(__name__)

# Manager imports - existing
from .analytics_manager import AnalyticsManager, get_analytics_manager
from .backup_manager import BackupManager, get_backup_manager
from .cache_manager import CacheManager, get_cache_manager
from .collaboration_manager import CollaborationManager, get_collaboration_manager
from .database_manager import DatabaseManager, get_database_manager
from .license_manager import LicenseManager, get_license_manager
from .migration_manager import MigrationManager, get_migration_manager
from .notification_manager import NotificationManager, get_notification_manager
from .queue_manager import QueueManager, get_queue_manager
from .resource_manager import ResourceManager, get_resource_manager
from .security_manager import SecurityManager, get_security_manager
from .session_manager import SessionManager, get_session_manager
from .storage_manager import StorageManager, get_storage_manager
from .tenant_manager import TenantManager, get_tenant_manager
from .workflow_manager import WorkflowManager, get_workflow_manager

# New industrial managers for IA-Influencer-Agent
from .protection_manager import ProtectionManager, get_protection_manager
from .fingerprinting_manager import FingerprintingManager, get_fingerprinting_manager
from .revenue_manager import RevenueManager, get_revenue_manager
from .monetization_manager import MonetizationManager, get_monetization_manager
from .content_manager import ContentManager, get_content_manager
from .ai_agent_manager import AiAgentManager, get_ai_agent_manager
from .multilingual_manager import MultilingualManager, get_multilingual_manager
from .distribution_manager import DistributionManager, get_distribution_manager
from .compliance_manager import ComplianceManager, get_compliance_manager
from .performance_manager import PerformanceManager, get_performance_manager

# Global manager registry for enterprise-grade coordination
_MANAGER_REGISTRY: Dict[str, Any] = {}

def register_manager(name: str, manager: Any) -> None:
    """Register a manager in the global registry"""
    _MANAGER_REGISTRY[name] = manager
    logger.info(f"🎯 Manager registered: {name}")

def get_manager(name: str) -> Optional[Any]:
    """Get a manager from the global registry"""
    return _MANAGER_REGISTRY.get(name)

def get_all_managers() -> Dict[str, Any]:
    """Get all registered managers"""
    return _MANAGER_REGISTRY.copy()

# Initialize all managers for enterprise deployment
async def initialize_all_managers() -> bool:
    """
    Initialize all enterprise managers for production deployment
    
    Returns:
        bool: True if all managers initialized successfully
    """
    try:
        managers = [
            ("analytics", get_analytics_manager()),
            ("backup", get_backup_manager()),
            ("cache", get_cache_manager()),
            ("collaboration", get_collaboration_manager()),
            ("database", get_database_manager()),
            ("license", get_license_manager()),
            ("migration", get_migration_manager()),
            ("notification", get_notification_manager()),
            ("queue", get_queue_manager()),
            ("resource", get_resource_manager()),
            ("security", get_security_manager()),
            ("session", get_session_manager()),
            ("storage", get_storage_manager()),
            ("tenant", get_tenant_manager()),
            ("workflow", get_workflow_manager()),
            # New industrial managers
            ("protection", get_protection_manager()),
            ("fingerprinting", get_fingerprinting_manager()),
            ("revenue", get_revenue_manager()),
            ("monetization", get_monetization_manager()),
            ("content", get_content_manager()),
            ("ai_agent", get_ai_agent_manager()),
            ("multilingual", get_multilingual_manager()),
            ("distribution", get_distribution_manager()),
            ("compliance", get_compliance_manager()),
            ("performance", get_performance_manager()),
        ]
        
        # Initialize all managers concurrently for optimal performance
        results = await asyncio.gather(
            *[manager.initialize_pool() for _, manager in managers],
            return_exceptions=True
        )
        
        # Register successfully initialized managers
        for (name, manager), result in zip(managers, results):
            if result is True:
                register_manager(name, manager)
            else:
                logger.error(f"❌ Failed to initialize {name}: {result}")
                return False
        
        logger.info("🚀 All IA-Influencer-Agent managers initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize managers: {e}")
        return False

# Cleanup all managers
async def cleanup_all_managers() -> bool:
    """
    Cleanup all enterprise managers for graceful shutdown
    
    Returns:
        bool: True if all managers cleaned up successfully
    """
    try:
        managers = list(_MANAGER_REGISTRY.values())
        
        # Cleanup all managers concurrently
        results = await asyncio.gather(
            *[manager.cleanup() for manager in managers],
            return_exceptions=True
        )
        
        success = all(result is True for result in results)
        _MANAGER_REGISTRY.clear()
        
        logger.info("🧹 All IA-Influencer-Agent managers cleaned up")
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup managers: {e}")
        return False

# Export all managers and utilities
__all__ = [
    # Existing managers
    "AnalyticsManager", "get_analytics_manager",
    "BackupManager", "get_backup_manager", 
    "CacheManager", "get_cache_manager",
    "CollaborationManager", "get_collaboration_manager",
    "DatabaseManager", "get_database_manager",
    "LicenseManager", "get_license_manager",
    "MigrationManager", "get_migration_manager",
    "NotificationManager", "get_notification_manager",
    "QueueManager", "get_queue_manager",
    "ResourceManager", "get_resource_manager",
    "SecurityManager", "get_security_manager",
    "SessionManager", "get_session_manager",
    "StorageManager", "get_storage_manager",
    "TenantManager", "get_tenant_manager",
    "WorkflowManager", "get_workflow_manager",
    
    # New industrial managers for IA-Influencer-Agent
    "ProtectionManager", "get_protection_manager",
    "FingerprintingManager", "get_fingerprinting_manager",
    "RevenueManager", "get_revenue_manager",
    "MonetizationManager", "get_monetization_manager",
    "ContentManager", "get_content_manager",
    "AiAgentManager", "get_ai_agent_manager",
    "MultilingualManager", "get_multilingual_manager",
    "DistributionManager", "get_distribution_manager",
    "ComplianceManager", "get_compliance_manager",
    "PerformanceManager", "get_performance_manager",
    
    # Manager registry utilities
    "register_manager",
    "get_manager", 
    "get_all_managers",
    "initialize_all_managers",
    "cleanup_all_managers",
]

# Import centralized manager registry and utilities from index
from .index import (
    initialize_all_managers as index_initialize_all_managers,
    shutdown_all_managers,
    perform_health_checks,
    get_manager as index_get_manager,
    get_all_managers as index_get_all_managers,
    get_manager_health_status,
    register_startup_callback,
    register_shutdown_callback,
    get_database_manager_instance,
    get_cache_manager_instance,
    get_queue_manager_instance,
    get_storage_manager_instance,
    get_backup_manager_instance,
    get_protection_manager_instance,
    get_fingerprinting_manager_instance,
    get_monetization_manager_instance,
    get_ai_agent_manager_instance,
    ManagerRegistry,
    manager_registry,
)

# Extended __all__ with registry utilities
__all__.extend([
    "shutdown_all_managers",
    "perform_health_checks",
    "get_manager_health_status",
    "register_startup_callback",
    "register_shutdown_callback",
    "get_database_manager_instance",
    "get_cache_manager_instance", 
    "get_queue_manager_instance",
    "get_storage_manager_instance",
    "get_backup_manager_instance",
    "get_protection_manager_instance",
    "get_fingerprinting_manager_instance",
    "get_monetization_manager_instance",
    "get_ai_agent_manager_instance",
    "ManagerRegistry",
    "manager_registry",
])
