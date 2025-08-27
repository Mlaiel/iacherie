"""
Crawler Configurations Index
===========================

Centralized index and management interface for all crawler configuration modules.
Provides comprehensive overview, validation, and management capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import asdict

# Import all configuration managers
from . import (
    crawler_config_manager,
    platform_config_manager,
    surveillance_config_manager,
    network_config_manager,
    protection_config_manager,
    storage_config_manager,
    ai_config_manager,
    security_config_manager,
    quality_config_manager,
    analytics_config_manager,
    notification_config_manager
)

# Import configuration classes for type checking
from .platform_configs import PlatformType, PlatformConfig
from .surveillance_configs import SurveillanceConfig
from .ai_configs import AIModelType, ModelConfig
from .security_configs import SecurityLevel, ThreatLevel
from .quality_configs import QualityLevel, ValidationSeverity
from .analytics_configs import MetricType, DashboardType
from .notification_configs import NotificationChannel, NotificationPriority

logger = logging.getLogger(__name__)

class ConfigurationIndex:
    """
    Comprehensive index and management system for all crawler configurations.
    Provides unified access, validation, monitoring, and maintenance capabilities.
    """
    
    def __init__(self):
        """Initialize configuration index."""
        self.version = "2.0.0"
        self.initialized_at = datetime.now()
        self.author = "Fahed Mlaiel <mlaiel@live.de>"
        
        # Configuration managers registry
        self.managers = {
            "platform": platform_config_manager,
            "surveillance": surveillance_config_manager,
            "network": network_config_manager,
            "protection": protection_config_manager,
            "storage": storage_config_manager,
            "ai": ai_config_manager,
            "security": security_config_manager,
            "quality": quality_config_manager,
            "analytics": analytics_config_manager,
            "notification": notification_config_manager
        }
        
        # Unified configuration manager
        self.unified_manager = crawler_config_manager
        
        logger.info(f"Configuration Index v{self.version} initialized")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview."""
        overview = {
            "metadata": {
                "version": self.version,
                "initialized_at": self.initialized_at.isoformat(),
                "author": self.author,
                "total_managers": len(self.managers)
            },
            "modules": {},
            "health": {
                "overall_status": "healthy",
                "issues": [],
                "warnings": []
            },
            "statistics": {
                "total_configurations": 0,
                "enabled_configurations": 0,
                "validation_errors": 0,
                "validation_warnings": 0
            }
        }
        
        # Collect module information
        total_configs = 0
        enabled_configs = 0
        total_errors = 0
        total_warnings = 0
        
        for manager_name, manager in self.managers.items():
            try:
                module_info = self._get_module_info(manager_name, manager)
                overview["modules"][manager_name] = module_info
                
                total_configs += module_info.get("total_items", 0)
                enabled_configs += module_info.get("enabled_items", 0)
                
                # Get validation results if available
                if hasattr(manager, 'validate_configuration'):
                    validation = manager.validate_configuration()
                    errors = len(validation.get("errors", []))
                    warnings = len(validation.get("warnings", []))
                    total_errors += errors
                    total_warnings += warnings
                    
                    module_info["validation"] = {
                        "errors": errors,
                        "warnings": warnings,
                        "status": "valid" if errors == 0 else "invalid"
                    }
                
            except Exception as e:
                overview["health"]["issues"].append(f"Failed to load {manager_name}: {str(e)}")
                logger.error(f"Error loading module {manager_name}: {e}")
        
        # Update statistics
        overview["statistics"]["total_configurations"] = total_configs
        overview["statistics"]["enabled_configurations"] = enabled_configs
        overview["statistics"]["validation_errors"] = total_errors
        overview["statistics"]["validation_warnings"] = total_warnings
        
        # Determine overall health
        if overview["health"]["issues"]:
            overview["health"]["overall_status"] = "unhealthy"
        elif total_errors > 0:
            overview["health"]["overall_status"] = "degraded"
        elif total_warnings > 5:
            overview["health"]["overall_status"] = "warnings"
        
        return overview
    
    def _get_module_info(self, manager_name: str, manager: Any) -> Dict[str, Any]:
        """Get detailed information about a configuration module."""
        info = {
            "name": manager_name,
            "type": type(manager).__name__,
            "status": "loaded",
            "total_items": 0,
            "enabled_items": 0,
            "features": [],
            "capabilities": []
        }
        
        try:
            # Platform-specific information
            if manager_name == "platform":
                info["total_items"] = len(manager.platforms)
                info["enabled_items"] = len([p for p in manager.platforms.values() if p.enabled])
                info["features"] = ["multi_platform", "rate_limiting", "authentication"]
                info["supported_platforms"] = [p.value for p in PlatformType]
            
            elif manager_name == "surveillance":
                info["total_items"] = len(manager.configs)
                info["enabled_items"] = len([c for c in manager.configs.values() if c.enabled])
                info["features"] = ["real_time_monitoring", "fingerprinting", "violation_detection"]
            
            elif manager_name == "ai":
                info["total_items"] = len(manager.models)
                info["enabled_items"] = len(manager.get_enabled_models())
                info["features"] = ["content_analysis", "smart_crawling", "violation_detection"]
                info["supported_models"] = [m.value for m in AIModelType]
            
            elif manager_name == "security":
                info["features"] = ["encryption", "access_control", "threat_protection", "compliance"]
                info["encryption_enabled"] = manager.encryption.enabled
                info["mfa_enabled"] = manager.access_control.mfa_enabled
                info["threat_protection"] = manager.threat_protection.enabled
            
            elif manager_name == "quality":
                info["total_items"] = len(manager.get_quality_metrics()) + len(manager.get_validation_rules())
                info["enabled_items"] = len(manager.get_quality_metrics(enabled_only=True))
                info["features"] = ["data_validation", "quality_metrics", "content_analysis"]
            
            elif manager_name == "analytics":
                info["total_items"] = len(manager.metrics) + len(manager.dashboards)
                info["enabled_items"] = len(manager.get_metrics(enabled_only=True))
                info["features"] = ["real_time_metrics", "dashboards", "reporting", "business_intelligence"]
            
            elif manager_name == "notification":
                info["total_items"] = len(manager.channels) + len(manager.recipients)
                info["enabled_items"] = len(manager.get_enabled_channels())
                info["features"] = ["multi_channel", "escalation", "templates", "alerting"]
                info["supported_channels"] = [c.value for c in NotificationChannel]
            
            # Check for common capabilities
            capabilities = []
            if hasattr(manager, 'validate_configuration'):
                capabilities.append("validation")
            if hasattr(manager, 'export_configuration'):
                capabilities.append("export")
            if hasattr(manager, 'import_configuration'):
                capabilities.append("import")
            if hasattr(manager, 'backup_configuration'):
                capabilities.append("backup")
            
            info["capabilities"] = capabilities
            
        except Exception as e:
            info["status"] = "error"
            info["error"] = str(e)
            logger.error(f"Error getting info for {manager_name}: {e}")
        
        return info
    
    def validate_all_configurations(self) -> Dict[str, Any]:
        """Perform comprehensive validation of all configurations."""
        validation_results = {
            "overall_status": "valid",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_modules": len(self.managers),
                "valid_modules": 0,
                "invalid_modules": 0,
                "total_errors": 0,
                "total_warnings": 0
            },
            "modules": {},
            "critical_issues": [],
            "recommendations": []
        }
        
        total_errors = 0
        total_warnings = 0
        valid_modules = 0
        
        for manager_name, manager in self.managers.items():
            module_result = {
                "status": "valid",
                "errors": [],
                "warnings": [],
                "recommendations": []
            }
            
            try:
                if hasattr(manager, 'validate_configuration'):
                    validation = manager.validate_configuration()
                    errors = validation.get("errors", [])
                    warnings = validation.get("warnings", [])
                    
                    module_result["errors"] = errors
                    module_result["warnings"] = warnings
                    
                    if errors:
                        module_result["status"] = "invalid"
                        total_errors += len(errors)
                        
                        # Check for critical issues
                        for error in errors:
                            if any(keyword in error.lower() for keyword in ["security", "encryption", "authentication"]):
                                validation_results["critical_issues"].append(f"{manager_name}: {error}")
                    else:
                        valid_modules += 1
                    
                    total_warnings += len(warnings)
                    
                    # Add module-specific recommendations
                    if manager_name == "security" and not manager.encryption.enabled:
                        module_result["recommendations"].append("Enable encryption for production use")
                    elif manager_name == "ai" and len(manager.get_enabled_models()) == 0:
                        module_result["recommendations"].append("Configure at least one AI model")
                    elif manager_name == "notification" and len(manager.get_enabled_channels()) == 0:
                        module_result["recommendations"].append("Enable at least one notification channel")
                
                else:
                    module_result["status"] = "no_validation"
                    valid_modules += 1
                    
            except Exception as e:
                module_result["status"] = "error"
                module_result["errors"] = [f"Validation failed: {str(e)}"]
                total_errors += 1
                logger.error(f"Validation error for {manager_name}: {e}")
            
            validation_results["modules"][manager_name] = module_result
        
        # Update summary
        validation_results["summary"]["valid_modules"] = valid_modules
        validation_results["summary"]["invalid_modules"] = len(self.managers) - valid_modules
        validation_results["summary"]["total_errors"] = total_errors
        validation_results["summary"]["total_warnings"] = total_warnings
        
        # Determine overall status
        if total_errors > 0:
            validation_results["overall_status"] = "invalid"
        elif total_warnings > 0:
            validation_results["overall_status"] = "warnings"
        
        # Add general recommendations
        if total_errors == 0 and total_warnings == 0:
            validation_results["recommendations"].append("All configurations are valid and optimal")
        else:
            if total_errors > 0:
                validation_results["recommendations"].append("Address configuration errors before deployment")
            if total_warnings > 5:
                validation_results["recommendations"].append("Review warnings to improve system reliability")
            if len(validation_results["critical_issues"]) > 0:
                validation_results["recommendations"].append("URGENT: Address critical security issues immediately")
        
        return validation_results
    
    def get_configuration_health(self) -> Dict[str, Any]:
        """Get health status of all configurations."""
        health_report = {
            "overall_health": "healthy",
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "issues": [],
            "metrics": {
                "healthy_modules": 0,
                "degraded_modules": 0,
                "unhealthy_modules": 0
            }
        }
        
        for manager_name, manager in self.managers.items():
            module_health = {
                "status": "healthy",
                "issues": [],
                "performance": "good",
                "availability": "online"
            }
            
            try:
                # Check if manager is responding
                if hasattr(manager, 'validate_configuration'):
                    validation = manager.validate_configuration()
                    errors = validation.get("errors", [])
                    warnings = validation.get("warnings", [])
                    
                    if errors:
                        module_health["status"] = "unhealthy"
                        module_health["issues"].extend(errors)
                        health_report["metrics"]["unhealthy_modules"] += 1
                        health_report["issues"].extend([f"{manager_name}: {error}" for error in errors])
                    elif warnings:
                        module_health["status"] = "degraded"
                        module_health["issues"].extend(warnings)
                        health_report["metrics"]["degraded_modules"] += 1
                    else:
                        health_report["metrics"]["healthy_modules"] += 1
                else:
                    health_report["metrics"]["healthy_modules"] += 1
                
            except Exception as e:
                module_health["status"] = "unhealthy"
                module_health["availability"] = "offline"
                module_health["issues"].append(f"Manager error: {str(e)}")
                health_report["metrics"]["unhealthy_modules"] += 1
                health_report["issues"].append(f"{manager_name}: Manager offline - {str(e)}")
            
            health_report["modules"][manager_name] = module_health
        
        # Determine overall health
        if health_report["metrics"]["unhealthy_modules"] > 0:
            health_report["overall_health"] = "unhealthy"
        elif health_report["metrics"]["degraded_modules"] > 2:
            health_report["overall_health"] = "degraded"
        elif health_report["metrics"]["degraded_modules"] > 0:
            health_report["overall_health"] = "warnings"
        
        return health_report
    
    def generate_comprehensive_report(self, include_details: bool = True) -> Dict[str, Any]:
        """Generate comprehensive configuration report."""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": self.version,
                "author": self.author,
                "report_type": "comprehensive_configuration_analysis"
            },
            "system_overview": self.get_system_overview(),
            "validation_results": self.validate_all_configurations(),
            "health_status": self.get_configuration_health(),
            "security_assessment": self._get_security_assessment(),
            "performance_metrics": self._get_performance_metrics(),
            "recommendations": self._generate_recommendations()
        }
        
        if include_details:
            report["detailed_configurations"] = self._get_detailed_configurations()
        
        return report
    
    def _get_security_assessment(self) -> Dict[str, Any]:
        """Get security assessment of configurations."""
        assessment = {
            "overall_score": 0.0,
            "encryption_status": "unknown",
            "authentication_status": "unknown",
            "access_control_status": "unknown",
            "compliance_status": "unknown",
            "recommendations": []
        }
        
        try:
            security_manager = self.managers["security"]
            
            # Check encryption
            if security_manager.encryption.enabled:
                assessment["encryption_status"] = "enabled"
            else:
                assessment["encryption_status"] = "disabled"
                assessment["recommendations"].append("Enable encryption for data protection")
            
            # Check access control
            if security_manager.access_control.mfa_enabled:
                assessment["authentication_status"] = "mfa_enabled"
            else:
                assessment["authentication_status"] = "basic"
                assessment["recommendations"].append("Enable multi-factor authentication")
            
            # Check threat protection
            if security_manager.threat_protection.enabled:
                assessment["access_control_status"] = "protected"
            else:
                assessment["access_control_status"] = "basic"
                assessment["recommendations"].append("Enable threat protection")
            
            # Calculate security score
            score = 0.0
            if assessment["encryption_status"] == "enabled":
                score += 25
            if assessment["authentication_status"] == "mfa_enabled":
                score += 25
            if assessment["access_control_status"] == "protected":
                score += 25
            if len(assessment["recommendations"]) == 0:
                score += 25
            
            assessment["overall_score"] = score
            
        except Exception as e:
            assessment["error"] = f"Security assessment failed: {str(e)}"
            logger.error(f"Security assessment error: {e}")
        
        return assessment
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for configurations."""
        metrics = {
            "configuration_load_time": 0.0,
            "memory_usage": "unknown",
            "validation_time": 0.0,
            "total_configurations": 0,
            "active_configurations": 0
        }
        
        try:
            # Simple performance metrics
            start_time = datetime.now()
            total_configs = 0
            active_configs = 0
            
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'get_enabled_configs'):
                    enabled = manager.get_enabled_configs()
                    active_configs += len(enabled)
                elif hasattr(manager, 'get_enabled_models'):
                    enabled = manager.get_enabled_models()
                    active_configs += len(enabled)
                elif hasattr(manager, 'get_enabled_channels'):
                    enabled = manager.get_enabled_channels()
                    active_configs += len(enabled)
                
                total_configs += 1
            
            end_time = datetime.now()
            metrics["configuration_load_time"] = (end_time - start_time).total_seconds()
            metrics["total_configurations"] = total_configs
            metrics["active_configurations"] = active_configs
            
        except Exception as e:
            metrics["error"] = f"Performance metrics failed: {str(e)}"
            logger.error(f"Performance metrics error: {e}")
        
        return metrics
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on configuration analysis."""
        recommendations = []
        
        try:
            # System-wide recommendations
            validation_results = self.validate_all_configurations()
            
            if validation_results["summary"]["total_errors"] > 0:
                recommendations.append("🚨 CRITICAL: Fix configuration errors before production deployment")
            
            if validation_results["summary"]["total_warnings"] > 5:
                recommendations.append("⚠️ Review and address configuration warnings")
            
            # Security recommendations
            security_assessment = self._get_security_assessment()
            if security_assessment["overall_score"] < 75:
                recommendations.append("🔒 Improve security configuration (current score: {:.1f}/100)".format(security_assessment["overall_score"]))
            
            # Module-specific recommendations
            ai_manager = self.managers["ai"]
            if len(ai_manager.get_enabled_models()) == 0:
                recommendations.append("🤖 Configure AI models for content analysis")
            
            notification_manager = self.managers["notification"]
            if len(notification_manager.get_enabled_channels()) == 0:
                recommendations.append("📧 Setup notification channels for alerts")
            
            # Performance recommendations
            if len(recommendations) == 0:
                recommendations.append("✅ Configuration is optimal - no immediate actions required")
            
        except Exception as e:
            recommendations.append(f"❌ Error generating recommendations: {str(e)}")
            logger.error(f"Recommendations error: {e}")
        
        return recommendations
    
    def _get_detailed_configurations(self) -> Dict[str, Any]:
        """Get detailed configuration data for all modules."""
        detailed_configs = {}
        
        for manager_name, manager in self.managers.items():
            try:
                config_data = {}
                
                if hasattr(manager, 'export_configuration'):
                    config_data = manager.export_configuration()
                elif hasattr(manager, '__dict__'):
                    # Get basic configuration data
                    config_data = {
                        key: str(value) for key, value in manager.__dict__.items()
                        if not key.startswith('_') and not callable(value)
                    }
                
                detailed_configs[manager_name] = config_data
                
            except Exception as e:
                detailed_configs[manager_name] = {"error": f"Failed to get details: {str(e)}"}
                logger.error(f"Error getting details for {manager_name}: {e}")
        
        return detailed_configs
    
    def export_configuration_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive configuration report to file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"crawler_configuration_report_{timestamp}.json"
        
        report = self.generate_comprehensive_report()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Configuration report exported to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            raise
    
    def interactive_configuration_wizard(self) -> Dict[str, Any]:
        """Interactive configuration setup wizard."""
        wizard_results = {
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "configurations_updated": [],
            "recommendations": [],
            "final_status": "incomplete"
        }
        
        # This would implement an interactive wizard
        # For now, return a template
        wizard_results["recommendations"] = [
            "Run validation to check current configuration status",
            "Review security settings for production deployment",
            "Configure AI models for content analysis",
            "Setup notification channels for monitoring",
            "Review platform-specific settings"
        ]
        
        wizard_results["final_status"] = "template_generated"
        return wizard_results

# Global configuration index instance
configuration_index = ConfigurationIndex()

# Convenience functions for quick access
def get_system_status() -> Dict[str, Any]:
    """Get quick system status overview."""
    return configuration_index.get_system_overview()

def validate_configurations() -> Dict[str, Any]:
    """Validate all configurations."""
    return configuration_index.validate_all_configurations()

def get_health_status() -> Dict[str, Any]:
    """Get configuration health status."""
    return configuration_index.get_configuration_health()

def generate_report() -> Dict[str, Any]:
    """Generate comprehensive configuration report."""
    return configuration_index.generate_comprehensive_report()

def export_report(filepath: Optional[str] = None) -> str:
    """Export configuration report to file."""
    return configuration_index.export_configuration_report(filepath)

# Module initialization
if __name__ == "__main__":
    # Command-line interface for configuration management
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawler Configuration Management")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--validate", action="store_true", help="Validate configurations")
    parser.add_argument("--health", action="store_true", help="Show health status")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--export", type=str, help="Export report to file")
    
    args = parser.parse_args()
    
    if args.status:
        status = get_system_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.validate:
        validation = validate_configurations()
        print(json.dumps(validation, indent=2, default=str))
    
    elif args.health:
        health = get_health_status()
        print(json.dumps(health, indent=2, default=str))
    
    elif args.report:
        report = generate_report()
        print(json.dumps(report, indent=2, default=str))
    
    elif args.export:
        filepath = export_report(args.export)
        print(f"Report exported to: {filepath}")
    
    else:
        # Show basic overview
        overview = get_system_status()
        print("\n🔧 Crawler Configuration System Overview")
        print("="*50)
        print(f"Version: {overview['metadata']['version']}")
        print(f"Modules: {overview['metadata']['total_managers']}")
        print(f"Status: {overview['health']['overall_status']}")
        print(f"Total Configurations: {overview['statistics']['total_configurations']}")
        print(f"Enabled Configurations: {overview['statistics']['enabled_configurations']}")
        
        if overview['health']['issues']:
            print(f"\n⚠️  Issues Found: {len(overview['health']['issues'])}")
            for issue in overview['health']['issues'][:3]:  # Show first 3 issues
                print(f"  - {issue}")
        
        print(f"\nFor detailed analysis, use: python {__file__} --report")
        print(f"To validate configs, use: python {__file__} --validate")
        print(f"To export report, use: python {__file__} --export report.json")

# Import all configuration components for easy access
from . import (
    # Main module
    master_config_manager,
    MasterConfigManager,
    GlobalCrawlerConfig,
    
    # Platform configurations
    platform_config_manager,
    PlatformConfigManager,
    PlatformType,
    PlatformConfig,
    ContentType,
    AuthMethod,
    ScrapeMethod,
    
    # Surveillance configurations
    surveillance_config_manager,
    SurveillanceConfigManager,
    SurveillanceConfig,
    SurveillanceMode,
    MonitoringType,
    AlertSeverity,
    AlertChannel,
    FingerprintEngine,
    
    # Protection configurations
    protection_config_manager,
    ProtectionConfigManager,
    ProtectionConfig,
    ProtectionLevel,
    ViolationType,
    ProtectionMethod,
    AudioProtectionConfig,
    VideoProtectionConfig,
    ImageProtectionConfig,
    TextProtectionConfig,
    
    # Network configurations
    network_config_manager,
    NetworkConfigManager,
    NetworkConfig,
    ProxyType,
    UserAgentType,
    RateLimitStrategy,
    LoadBalancingStrategy,
    CacheStrategy,
    
    # Storage configurations
    storage_config_manager,
    StorageConfigManager,
    StorageConfig,
    StorageBackend,
    DatabaseType,
    CompressionType,
    EncryptionType,
    
    # Convenience functions
    get_platform_config,
    get_surveillance_config,
    get_protection_config,
    get_network_config,
    get_storage_config,
    get_system_status,
    validate_all_configs
)

# Configuration presets for different environments
DEVELOPMENT_PRESET = {
    "global": {
        "debug_mode": True,
        "verbose_logging": True,
        "max_concurrent_crawlers": 5,
        "security_mode": "relaxed"
    },
    "network": {
        "rate_limiting": {"requests_per_second": 2.0},
        "proxy_rotation": {"enabled": False},
        "caching": {"enabled": True, "memory_cache_size_mb": 256}
    },
    "protection": {
        "level": ProtectionLevel.BASIC,
        "human_verification_threshold": 0.5
    }
}

STAGING_PRESET = {
    "global": {
        "debug_mode": False,
        "verbose_logging": True,
        "max_concurrent_crawlers": 20,
        "security_mode": "standard"
    },
    "network": {
        "rate_limiting": {"requests_per_second": 1.0},
        "proxy_rotation": {"enabled": True},
        "caching": {"enabled": True, "memory_cache_size_mb": 512}
    },
    "protection": {
        "level": ProtectionLevel.STANDARD,
        "human_verification_threshold": 0.75
    }
}

PRODUCTION_PRESET = {
    "global": {
        "debug_mode": False,
        "verbose_logging": False,
        "max_concurrent_crawlers": 50,
        "security_mode": "strict"
    },
    "network": {
        "rate_limiting": {"requests_per_second": 0.5},
        "proxy_rotation": {"enabled": True},
        "caching": {"enabled": True, "memory_cache_size_mb": 1024}
    },
    "protection": {
        "level": ProtectionLevel.ENTERPRISE,
        "human_verification_threshold": 0.85
    }
}

def get_environment_preset(environment: str) -> dict:
    """Get configuration preset for specific environment."""
    presets = {
        "development": DEVELOPMENT_PRESET,
        "staging": STAGING_PRESET,
        "production": PRODUCTION_PRESET
    }
    return presets.get(environment.lower(), PRODUCTION_PRESET)

def apply_environment_preset(environment: str) -> None:
    """Apply configuration preset for specific environment."""
    preset = get_environment_preset(environment)
    
    # Apply global settings
    if "global" in preset:
        master_config_manager.update_global_config(**preset["global"])
    
    # Apply network settings
    if "network" in preset:
        network_config = network_config_manager.get_config()
        for key, value in preset["network"].items():
            if hasattr(network_config, key):
                if isinstance(value, dict):
                    # Update nested configuration
                    nested_config = getattr(network_config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(network_config, key, value)
        network_config_manager.update_config(network_config)
    
    # Apply protection settings
    if "protection" in preset:
        protection_config = protection_config_manager.get_config()
        for key, value in preset["protection"].items():
            if hasattr(protection_config, key):
                setattr(protection_config, key, value)
        protection_config_manager.update_config(protection_config)

def quick_setup(
    environment: str = "production",
    platforms: list = None,
    enable_surveillance: bool = True,
    enable_protection: bool = True
) -> dict:
    """Quick setup for crawler configuration system."""
    
    # Apply environment preset
    apply_environment_preset(environment)
    
    # Configure platforms
    if platforms:
        for platform_name in platforms:
            try:
                platform_type = PlatformType(platform_name.lower())
                config = platform_config_manager.get_config(platform_type)
                if config:
                    config.enabled = True
                    platform_config_manager.update_config(platform_type, config)
            except ValueError:
                print(f"Unknown platform: {platform_name}")
    
    # Configure surveillance
    surveillance_config = surveillance_config_manager.get_config()
    surveillance_config.enabled = enable_surveillance
    surveillance_config_manager.update_config(surveillance_config)
    
    # Configure protection
    protection_config = protection_config_manager.get_config()
    protection_config.enabled = enable_protection
    protection_config_manager.update_config(protection_config)
    
    # Return setup summary
    return {
        "environment": environment,
        "enabled_platforms": platforms or [],
        "surveillance_enabled": enable_surveillance,
        "protection_enabled": enable_protection,
        "status": "configured"
    }

def health_check() -> dict:
    """Perform comprehensive health check of configuration system."""
    results = {
        "timestamp": "2025-08-20T00:00:00Z",
        "overall_status": "healthy",
        "components": {}
    }
    
    try:
        # Check master config
        global_config = master_config_manager.get_global_config()
        results["components"]["master"] = {
            "status": "healthy" if global_config.enabled else "disabled",
            "version": global_config.version,
            "environment": global_config.environment
        }
        
        # Check platform configs
        enabled_platforms = master_config_manager.get_enabled_platforms()
        results["components"]["platforms"] = {
            "status": "healthy",
            "enabled_count": len(enabled_platforms),
            "platforms": [p.value for p in enabled_platforms]
        }
        
        # Check surveillance config
        surveillance = surveillance_config_manager.get_config()
        results["components"]["surveillance"] = {
            "status": "healthy" if surveillance.enabled else "disabled",
            "mode": surveillance.mode.value,
            "engines": len(surveillance.fingerprinting.engines)
        }
        
        # Check protection config
        protection = protection_config_manager.get_config()
        results["components"]["protection"] = {
            "status": "healthy" if protection.enabled else "disabled",
            "level": protection.protection_level.value,
            "audio": protection.audio.enabled,
            "video": protection.video.enabled,
            "image": protection.image.enabled,
            "text": protection.text.enabled
        }
        
        # Check network config
        network = network_config_manager.get_config()
        results["components"]["network"] = {
            "status": "healthy",
            "proxy_rotation": network.proxy_rotation.enabled,
            "rate_limiting": network.rate_limiting.strategy.value,
            "caching": network.caching.enabled
        }
        
        # Check storage config
        storage = storage_config_manager.get_config()
        results["components"]["storage"] = {
            "status": "healthy",
            "backend": storage.file_storage.backend.value,
            "database": storage.database.primary_db.value,
            "encryption": storage.encryption.enabled
        }
        
        # Validate all configurations
        validation_results = validate_all_configs()
        error_count = sum(len(errors) for errors in validation_results.values())
        
        if error_count > 0:
            results["overall_status"] = "warnings"
            results["validation_errors"] = validation_results
        
    except Exception as e:
        results["overall_status"] = "error"
        results["error"] = str(e)
    
    return results

def export_configuration_summary() -> dict:
    """Export comprehensive configuration summary."""
    return {
        "system_info": {
            "name": "IA Influencer Agent - Content Protection Platform",
            "author": "Fahed Mlaiel",
            "contact": "mlaiel@live.de",
            "version": "2.0.0"
        },
        "configuration_summary": master_config_manager.get_configuration_summary(),
        "health_check": health_check(),
        "export_timestamp": "2025-08-20T00:00:00Z"
    }

# Quick access aliases
configs = master_config_manager
platforms = platform_config_manager
surveillance = surveillance_config_manager
protection = protection_config_manager
network = network_config_manager
storage = storage_config_manager

# Export everything for easy imports
__all__ = [
    # Main managers
    'master_config_manager', 'configs',
    'platform_config_manager', 'platforms',
    'surveillance_config_manager', 'surveillance',
    'protection_config_manager', 'protection',
    'network_config_manager', 'network',
    'storage_config_manager', 'storage',
    
    # Configuration classes
    'MasterConfigManager', 'GlobalCrawlerConfig',
    'PlatformConfigManager', 'PlatformConfig', 'PlatformType',
    'SurveillanceConfigManager', 'SurveillanceConfig',
    'ProtectionConfigManager', 'ProtectionConfig',
    'NetworkConfigManager', 'NetworkConfig',
    'StorageConfigManager', 'StorageConfig',
    
    # Enums
    'ContentType', 'AuthMethod', 'ScrapeMethod',
    'SurveillanceMode', 'MonitoringType', 'AlertSeverity', 'AlertChannel',
    'ProtectionLevel', 'ViolationType', 'ProtectionMethod',
    'ProxyType', 'UserAgentType', 'RateLimitStrategy',
    'StorageBackend', 'DatabaseType', 'CompressionType',
    
    # Utility functions
    'get_platform_config', 'get_surveillance_config', 'get_protection_config',
    'get_network_config', 'get_storage_config', 'get_system_status',
    'validate_all_configs', 'quick_setup', 'health_check',
    'apply_environment_preset', 'export_configuration_summary',
    
    # Presets
    'DEVELOPMENT_PRESET', 'STAGING_PRESET', 'PRODUCTION_PRESET'
]
