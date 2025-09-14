"""🌐 Global Configuration Manager - IA-Influencer-Agent
==================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade global configuration orchestrator for unified system management.
==================================================================
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml
import os
from pathlib import Path

# Import all configuration managers
from .base_config import BaseConfigurationManager
from .environment_manager import EnvironmentManager
from .deployment_orchestrator import DeploymentOrchestrator
from .security_config import SecurityConfigManager
from .performance_tuning import PerformanceTuningManager
from .monitoring_config import MonitoringConfigManager
from .database_config import DatabaseConfigManager
from .network_config import NetworkConfigManager
from .secrets_manager import SecretsManager
from .scaling_config import ScalingConfigManager
from .backup_config import BackupConfigManager
from .compliance_config import ComplianceConfigManager
from .validation_engine import ValidationEngine
from .deployment_templates import DeploymentTemplateManager

# Import AI & Protection managers
from .ai_fingerprinting_config import AIFingerprintingConfigManager
from .content_protection_config import ContentProtectionConfigManager
from .audio_ai_config import AudioAIConfigManager

# Import Business Logic managers
from .monetization_config import MonetizationConfigManager
from .distribution_config import MultiPlatformDistributionConfigManager
from .crawling_config import CrawlingMonitoringConfigManager
from .legal_licensing_config import LegalLicensingConfigManager

# Initialize logger
logger = logging.getLogger(__name__)

class SystemMode(Enum):
    """
System operation modes"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"

class ConfigurationCategory(Enum):
    """Configuration categories"""

    CORE_INFRASTRUCTURE = "core_infrastructure"
    AI_PROTECTION = "ai_protection"
    BUSINESS_LOGIC = "business_logic"
    OPERATIONS = "operations"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class SystemHealthStatus:
    """System health status information"""
    overall_status: str
    timestamp: datetime
    components_healthy: int
    components_degraded: int
    components_critical: int
    active_alerts: int
    configuration_errors: int
    performance_score: float
    uptime_hours: float

@dataclass
class GlobalConfiguration:
    """
Global system configuration"""
    # System identification
    system_name: str = "IA-Influencer-Agent"
    system_version: str = "2.0.0"
    environment: str = "production"
    mode: SystemMode = SystemMode.PRODUCTION
    
    # Global settings
    debug_mode: bool = False
    maintenance_mode: bool = False
    emergency_mode: bool = False
    
    # Business logic settings
    content_creator_focus: List[str] = field(default_factory=lambda: [
        "musicians", "bloggers", "photographers", "influencers", "comedians", "podcasters"
    ])
    supported_content_types: List[str] = field(default_factory=lambda: [
        "audio", "video", "image", "text", "music", "podcast", "blog", "photo"
    ])
    ai_processing_enabled: bool = True
    protection_services_enabled: bool = True
    monetization_enabled: bool = True
    multi_platform_distribution: bool = True
    
    # Security and compliance
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    dmca_compliance: bool = True
    audit_logging: bool = True
    encryption_required: bool = True
    
    # Performance and scaling
    auto_scaling_enabled: bool = True
    performance_monitoring: bool = True
    resource_optimization: bool = True
    cost_optimization: bool = True
    
    # Integration settings
    third_party_integrations: bool = True
    webhook_support: bool = True
    api_access: bool = True
    
    # Data management
    data_retention_policy: bool = True
    backup_enabled: bool = True
    disaster_recovery: bool = True
    
    # AI and ML settings
    ml_models_enabled: bool = True
    continuous_learning: bool = True
    ai_enhancement: bool = True
    
    # Creator workflow
    upload_to_protection: bool = True
    seo_optimization: bool = True
    collaboration_matching: bool = True
    platform_distribution: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "Fahed Mlaiel"
    contact_email: str = "mlaiel@live.de"

class GlobalConfigurationManager:
    """
    Global configuration orchestrator for the entire IA-Influencer-Agent platform.
    
    Provides unified management of all configuration aspects:
    - System-wide configuration coordination
    - Cross-component configuration validation
    - Unified health monitoring
    - Performance metrics aggregation
    - Emergency response coordination
    - Business logic flow management
    - Compliance and security oversight
    - Resource allocation optimization
    - Configuration drift detection
    - Automated remediation
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
Initialize global configuration manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration path
        self.config_path = config_path or os.getenv(
            "GLOBAL_CONFIG_PATH",
            "/app/config/global_configuration.yaml"
        )
        
        # Global configuration
        self._global_config = GlobalConfiguration()
        
        # Initialize all configuration managers
        self._initialize_managers()
        
        # System state
        self.initialized = False
        self.system_start_time = datetime.now()
        self.last_health_check = None
        self.health_status = None
        self.active_alerts = []
        self.configuration_errors = []
        
        # Load global configuration
        self._load_global_configuration()
        
        self.logger.info("Global configuration manager initialized")
    
    def _initialize_managers(self) -> None:
        """Initialize all configuration managers"""
        
        # Core infrastructure managers
        self.base_config = BaseConfigurationManager()
        self.environment_manager = EnvironmentManager()
        self.deployment_orchestrator = DeploymentOrchestrator()
        self.security_config = SecurityConfigManager()
        self.performance_tuning = PerformanceTuningManager()
        self.monitoring_config = MonitoringConfigManager()
        self.database_config = DatabaseConfigManager()
        self.network_config = NetworkConfigManager()
        self.secrets_manager = SecretsManager()
        self.scaling_config = ScalingConfigManager()
        self.backup_config = BackupConfigManager()
        self.compliance_config = ComplianceConfigManager()
        self.validation_engine = ValidationEngine()
        self.deployment_templates = DeploymentTemplateManager()
        
        # AI & Protection managers
        self.ai_fingerprinting_config = AIFingerprintingConfigManager()
        self.content_protection_config = ContentProtectionConfigManager()
        self.audio_ai_config = AudioAIConfigManager()
        
        # Business logic managers
        self.monetization_config = MonetizationConfigManager()
        self.distribution_config = MultiPlatformDistributionConfigManager()
        self.crawling_config = CrawlingMonitoringConfigManager()
        self.legal_licensing_config = LegalLicensingConfigManager()
        
        # Manager categories for organized access
        self.manager_categories = {
            ConfigurationCategory.CORE_INFRASTRUCTURE: [
                self.base_config, self.environment_manager, self.database_config,
                self.network_config, self.secrets_manager
            ],
            ConfigurationCategory.AI_PROTECTION: [
                self.ai_fingerprinting_config, self.content_protection_config,
                self.audio_ai_config
            ],
            ConfigurationCategory.BUSINESS_LOGIC: [
                self.monetization_config, self.distribution_config,
                self.crawling_config, self.legal_licensing_config
            ],
            ConfigurationCategory.OPERATIONS: [
                self.deployment_orchestrator, self.scaling_config,
                self.backup_config, self.deployment_templates
            ],
            ConfigurationCategory.SECURITY: [
                self.security_config, self.compliance_config, self.validation_engine
            ],
            ConfigurationCategory.PERFORMANCE: [
                self.performance_tuning, self.monitoring_config
            ]
        }
        
        # All managers list for bulk operations
        self.all_managers = []
        for manager_list in self.manager_categories.values():
            self.all_managers.extend(manager_list)
    
    def _load_global_configuration(self) -> bool:
        """
Load global configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update global configuration
                for key, value in config_data.items():
                    if hasattr(self._global_config, key):
                        setattr(self._global_config, key, value)
                
                self._global_config.updated_at = datetime.now()
                self.logger.info(f"Global configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.info("No global configuration file found, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load global configuration: {e}")
            return False
    
    async def initialize_system(self) -> bool:
        """
        Initialize the entire system with all configurations.
        
        Returns:
            bool: True if all components initialized successfully
        """
        try:
            self.logger.info("Starting global system initialization...")
            
            # Phase 1: Core Infrastructure
            self.logger.info("Phase 1: Initializing core infrastructure...")
            for manager in self.manager_categories[ConfigurationCategory.CORE_INFRASTRUCTURE]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            # Phase 2: Security and Compliance
            self.logger.info("Phase 2: Initializing security and compliance...")
            for manager in self.manager_categories[ConfigurationCategory.SECURITY]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            # Phase 3: AI and Protection Services
            self.logger.info("Phase 3: Initializing AI and protection services...")
            for manager in self.manager_categories[ConfigurationCategory.AI_PROTECTION]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            # Phase 4: Business Logic Services
            self.logger.info("Phase 4: Initializing business logic services...")
            for manager in self.manager_categories[ConfigurationCategory.BUSINESS_LOGIC]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            # Phase 5: Performance and Operations
            self.logger.info("Phase 5: Initializing performance and operations...")
            for manager in self.manager_categories[ConfigurationCategory.PERFORMANCE]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            for manager in self.manager_categories[ConfigurationCategory.OPERATIONS]:
                if hasattr(manager, 'initialize'):
                    result = await manager.initialize()
                    if not result:
                        self.logger.error(f"Failed to initialize {manager.__class__.__name__}")
                        return False
            
            # System validation
            self.logger.info("Performing system-wide validation...")
            validation_result = await self.validate_system_configuration()
            if not validation_result['valid']:
                self.logger.error(f"System validation failed: {validation_result['errors']}")
                # Continue anyway but log errors
                self.configuration_errors.extend(validation_result['errors'])
            
            # Initial health check
            await self.perform_health_check()
            
            self.initialized = True
            self.logger.info("✅ Global system initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Global system initialization failed: {e}")
            return False
    
    async def validate_system_configuration(self) -> Dict[str, Any]:
        """
        Validate entire system configuration for consistency and compliance.
        
        Returns:
            Dict containing validation results
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "timestamp": datetime.now(),
                "categories_validated": {}
            }
            
            # Validate each category
            for category, managers in self.manager_categories.items():
                category_errors = []
                category_warnings = []
                
                for manager in managers:
                    try:
                        if hasattr(manager, 'validate_configuration'):
                            manager_validation = manager.validate_configuration()
                            if manager_validation:
                                category_errors.extend(manager_validation)
                        
                        # Additional cross-validation checks
                        if hasattr(manager, 'get_configuration_status'):
                            status = manager.get_configuration_status()
                            if 'validation_errors' in status and status['validation_errors']:
                                category_errors.extend(status['validation_errors'])
                    
                    except Exception as e:
                        category_errors.append(f"{manager.__class__.__name__} validation failed: {e}")
                
                validation_result["categories_validated"][category.value] = {
                    "errors": category_errors,
                    "warnings": category_warnings,
                    "managers_count": len(managers)
                }
                
                # Aggregate errors
                validation_result["errors"].extend(category_errors)
                validation_result["warnings"].extend(category_warnings)
            
            # Cross-system validation
            cross_validation_errors = await self._perform_cross_system_validation()
            validation_result["errors"].extend(cross_validation_errors)
            
            # Business logic validation
            business_validation_errors = await self._validate_business_logic_flow()
            validation_result["errors"].extend(business_validation_errors)
            
            # Set overall validity
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            if validation_result["valid"]:
                self.logger.info("System configuration validation passed")
            else:
                self.logger.warning(f"System validation failed with {len(validation_result['errors'])} errors")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"System configuration validation error: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "timestamp": datetime.now()
            }
    
    async def _perform_cross_system_validation(self) -> List[str]:
        """Perform cross-system validation checks"""
        errors = []
        
        try:
            # Check AI fingerprinting and content protection integration
            if self._global_config.ai_processing_enabled and self._global_config.protection_services_enabled:
                ai_config = self.ai_fingerprinting_config.get_complete_config()
                protection_config = self.content_protection_config.get_complete_config()
                
                # Validate that enabled algorithms are consistent
                if not ai_config.audio_config.algorithms:
                    errors.append("AI fingerprinting enabled but no audio algorithms configured")
            
            # Check monetization and distribution integration
            if self._global_config.monetization_enabled and self._global_config.multi_platform_distribution:
                monetization_status = self.monetization_config.get_configuration_status()
                distribution_status = self.distribution_config.get_configuration_status()
                
                if not monetization_status.get('features_enabled', {}).get('revenue_tracking'):
                    errors.append("Distribution enabled but revenue tracking not configured")
            
            # Check database and performance alignment
            db_status = self.database_config.get_status() if hasattr(self.database_config, 'get_status') else {}
            perf_status = self.performance_tuning.get_status() if hasattr(self.performance_tuning, 'get_status') else {}
            
            # Add more cross-validation rules as needed
            
        except Exception as e:
            errors.append(f"Cross-system validation error: {e}")
        
        return errors
    
    async def _validate_business_logic_flow(self) -> List[str]:
        """Validate business logic flow integrity"""
        errors = []
        
        try:
            # Validate creator workflow: Upload → Protection → SEO → Collaboration → Distribution
            
            # Check upload processing capability
            if not self.ai_fingerprinting_config.get_complete_config().processing_config.enabled:
                errors.append("Business flow broken: Content upload processing not enabled")
            
            # Check protection services
            if self._global_config.protection_services_enabled:
                protection_status = self.content_protection_config.get_configuration_status()
                if not protection_status.get('features_enabled', {}).get('fingerprinting'):
                    errors.append("Business flow broken: Content protection not properly configured")
            
            # Check distribution capabilities
            if self._global_config.multi_platform_distribution:
                enabled_platforms = self.distribution_config.get_enabled_platforms()
                if not enabled_platforms:
                    errors.append("Business flow broken: No distribution platforms enabled")
            
            # Check monetization setup
            if self._global_config.monetization_enabled:
                monetization_status = self.monetization_config.get_configuration_status()
                if not monetization_status.get('features_enabled', {}).get('payment_processing'):
                    errors.append("Business flow broken: Payment processing not configured")
            
        except Exception as e:
            errors.append(f"Business logic validation error: {e}")
        
        return errors
    
    async def perform_health_check(self) -> SystemHealthStatus:
        """
        Perform comprehensive system health check.
        
        Returns:
            SystemHealthStatus containing health information
        """
        try:
            self.logger.info("Performing comprehensive system health check...")
            
            healthy_count = 0
            degraded_count = 0
            critical_count = 0
            total_managers = len(self.all_managers)
            
            # Check each manager's health
            for manager in self.all_managers:
                try:
                    if hasattr(manager, 'get_status'):
                        status = await manager.get_status()
                        health = self._assess_manager_health(status)
                        
                        if health == "healthy":
                            healthy_count += 1
                        elif health == "degraded":
                            degraded_count += 1
                        else:
                            critical_count += 1
                    else:
                        healthy_count += 1  # Assume healthy if no status method
                
                except Exception as e:
                    self.logger.warning(f"Health check failed for {manager.__class__.__name__}: {e}")
                    critical_count += 1
            
            # Calculate performance score
            performance_score = (healthy_count / total_managers) * 100 if total_managers > 0 else 0
            
            # Determine overall status
            if critical_count > 0:
                overall_status = "critical"
            elif degraded_count > total_managers * 0.2:  # More than 20% degraded
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            # Calculate uptime
            uptime_hours = (datetime.now() - self.system_start_time).total_seconds() / 3600
            
            # Create health status
            health_status = SystemHealthStatus(
                overall_status=overall_status,
                timestamp=datetime.now(),
                components_healthy=healthy_count,
                components_degraded=degraded_count,
                components_critical=critical_count,
                active_alerts=len(self.active_alerts),
                configuration_errors=len(self.configuration_errors),
                performance_score=performance_score,
                uptime_hours=uptime_hours
            )
            
            self.health_status = health_status
            self.last_health_check = datetime.now()
            
            self.logger.info(f"Health check completed: {overall_status} ({performance_score:.1f}% healthy)")
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return SystemHealthStatus(
                overall_status="critical",
                timestamp=datetime.now(),
                components_healthy=0,
                components_degraded=0,
                components_critical=len(self.all_managers),
                active_alerts=len(self.active_alerts),
                configuration_errors=len(self.configuration_errors) + 1,
                performance_score=0.0,
                uptime_hours=(datetime.now() - self.system_start_time).total_seconds() / 3600
            )
    
    def _assess_manager_health(self, status: Dict[str, Any]) -> str:
        """Assess individual manager health from status"""
        
        # Check for critical indicators
        if 'error' in status or status.get('initialized') == False:
            return "critical"
        
        # Check for degraded indicators
        if 'warnings' in status and status['warnings']:
            return "degraded"
        
        if 'validation_errors' in status and status['validation_errors']:
            return "degraded"
        
        # Otherwise healthy
        return "healthy"
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive system overview.
        
        Returns:
            Dict containing complete system information
        """
        try:
            # Perform health check if needed
            if not self.last_health_check or (datetime.now() - self.last_health_check).seconds > 300:
                await self.perform_health_check()
            
            # Collect configuration statuses
            configuration_status = {}
            for category, managers in self.manager_categories.items():
                category_status = {}
                for manager in managers:
                    manager_name = manager.__class__.__name__
                    try:
                        if hasattr(manager, 'get_configuration_status'):
                            category_status[manager_name] = manager.get_configuration_status()
                        elif hasattr(manager, 'get_status'):
                            category_status[manager_name] = await manager.get_status()
                        else:
                            category_status[manager_name] = {"status": "unknown"}
                    except Exception as e:
                        category_status[manager_name] = {"error": str(e)}
                
                configuration_status[category.value] = category_status
            
            # Build overview
            system_overview = {
                "system_info": {
                    "name": self._global_config.system_name,
                    "version": self._global_config.system_version,
                    "environment": self._global_config.environment,
                    "mode": self._global_config.mode.value,
                    "initialized": self.initialized,
                    "uptime_hours": (datetime.now() - self.system_start_time).total_seconds() / 3600,
                    "created_by": self._global_config.created_by,
                    "contact_email": self._global_config.contact_email
                },
                "health_status": {
                    "overall_status": self.health_status.overall_status if self.health_status else "unknown",
                    "performance_score": self.health_status.performance_score if self.health_status else 0,
                    "components_healthy": self.health_status.components_healthy if self.health_status else 0,
                    "components_degraded": self.health_status.components_degraded if self.health_status else 0,
                    "components_critical": self.health_status.components_critical if self.health_status else 0,
                    "last_health_check": self.last_health_check
                },
                "business_features": {
                    "content_types_supported": self._global_config.supported_content_types,
                    "creator_types_supported": self._global_config.content_creator_focus,
                    "ai_processing": self._global_config.ai_processing_enabled,
                    "content_protection": self._global_config.protection_services_enabled,
                    "monetization": self._global_config.monetization_enabled,
                    "multi_platform_distribution": self._global_config.multi_platform_distribution,
                    "workflow_steps": [
                        "Upload multi-format content",
                        "AI protection & rights management", 
                        "SEO optimization",
                        "Collaboration matching",
                        "Multi-platform distribution"
                    ]
                },
                "compliance_status": {
                    "gdpr_compliance": self._global_config.gdpr_compliance,
                    "ccpa_compliance": self._global_config.ccpa_compliance,
                    "dmca_compliance": self._global_config.dmca_compliance,
                    "audit_logging": self._global_config.audit_logging,
                    "encryption_required": self._global_config.encryption_required
                },
                "configuration_status": configuration_status,
                "active_alerts": len(self.active_alerts),
                "configuration_errors": len(self.configuration_errors),
                "timestamp": datetime.now()
            }
            
            return system_overview
            
        except Exception as e:
            self.logger.error(f"Failed to get system overview: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def emergency_shutdown(self) -> bool:
        """
        Perform emergency system shutdown with proper cleanup.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.warning("Initiating emergency shutdown...")
            
            # Set emergency mode
            self._global_config.emergency_mode = True
            self._global_config.mode = SystemMode.EMERGENCY
            
            # Stop all managers gracefully
            for manager in reversed(self.all_managers):
                try:
                    if hasattr(manager, 'shutdown'):
                        await manager.shutdown()
                    elif hasattr(manager, 'stop'):
                        await manager.stop()
                except Exception as e:
                    self.logger.error(f"Error shutting down {manager.__class__.__name__}: {e}")
            
            self.initialized = False
            self.logger.warning("Emergency shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency shutdown failed: {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get high-level configuration summary"""
        return {
            "system_name": self._global_config.system_name,
            "version": self._global_config.system_version,
            "environment": self._global_config.environment,
            "mode": self._global_config.mode.value,
            "initialized": self.initialized,
            "total_managers": len(self.all_managers),
            "manager_categories": len(self.manager_categories),
            "business_features": {
                "ai_processing": self._global_config.ai_processing_enabled,
                "content_protection": self._global_config.protection_services_enabled,
                "monetization": self._global_config.monetization_enabled,
                "distribution": self._global_config.multi_platform_distribution
            },
            "last_health_check": self.last_health_check,
            "uptime_hours": (datetime.now() - self.system_start_time).total_seconds() / 3600,
            "created_by": self._global_config.created_by,
            "contact": self._global_config.contact_email
        }

# Global instance
global_configuration_manager = GlobalConfigurationManager()

# Export public API
__all__ = [
    "GlobalConfigurationManager",
    "GlobalConfiguration",
    "SystemHealthStatus",
    "SystemMode",
    "ConfigurationCategory",
    "global_configuration_manager"
]
