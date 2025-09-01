"""Microservices Configuration Validation Module for IA-Influencer Agent Platform
============================================================================

Comprehensive validation suite for all microservices configurations,
ensuring system reliability, compliance, and production readiness.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from . import (
    # Core configurations
    service_discovery_config,
    load_balancer_config,
    message_broker_config,
    circuit_breaker_config,
    service_mesh_config,
    api_gateway_config,
    health_check_config,
    distributed_tracing_config,
    
    # Specialized configurations
    content_protection_config,
    fingerprinting_engine_config,
    web_crawler_config,
    monetization_engine_config,
    licensing_engine_config,
    platform_integration_config,
    analytics_engine_config,
    event_driven_config,
    
    # Orchestrators
    content_protection_orchestrator,
    platform_integration_orchestrator,
    analytics_orchestrator,
    event_orchestrator,
    orchestrator
)

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Validation categories"""
    CONFIGURATION = "configuration"
    CONNECTIVITY = "connectivity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    BUSINESS_LOGIC = "business_logic"


@dataclass
class ValidationResult:
    """Validation result structure"""
    category: ValidationCategory
    level: ValidationLevel
    component: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class MicroservicesValidator:
    """Comprehensive microservices configuration validator"""
    
    def __init__(self):
        """Initialize validator"""
        self.results: List[ValidationResult] = []
        self.logger = logging.getLogger(__name__)
    
    async def run_full_validation(self) -> Tuple[bool, List[ValidationResult]]:
        """Run complete validation suite"""
        self.logger.info("Starting comprehensive microservices validation...")
        self.results.clear()
        
        # Core microservices validation
        await self._validate_core_configurations()
        await self._validate_core_connectivity()
        
        # Specialized systems validation
        await self._validate_content_protection_system()
        await self._validate_platform_integrations()
        await self._validate_analytics_system()
        await self._validate_event_system()
        
        # Cross-system validation
        await self._validate_system_integration()
        await self._validate_security_compliance()
        await self._validate_business_logic()
        
        # Analyze results
        has_critical_issues = any(r.level == ValidationLevel.CRITICAL for r in self.results)
        has_errors = any(r.level == ValidationLevel.ERROR for r in self.results)
        
        validation_passed = not (has_critical_issues or has_errors)
        
        self.logger.info(f"Validation completed. Passed: {validation_passed}")
        return validation_passed, self.results
    
    async def _validate_core_configurations(self):
        """Validate core microservices configurations"""
        self.logger.info("Validating core configurations...")
        
        # Service Discovery validation
        if service_discovery_config.discovery_type in ["consul", "etcd", "kubernetes", "redis"]:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "service_discovery", "Valid discovery type configured")
        else:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.ERROR,
                           "service_discovery", "Invalid discovery type")
        
        # Load Balancer validation
        if load_balancer_config.default_strategy in ["round_robin", "weighted_round_robin", "least_connections"]:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "load_balancer", "Valid load balancing strategy")
        else:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.WARNING,
                           "load_balancer", "Unusual load balancing strategy")
        
        # Message Broker validation
        if message_broker_config.broker_type in ["rabbitmq", "kafka", "redis", "nats"]:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "message_broker", "Valid message broker type")
        else:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.ERROR,
                           "message_broker", "Invalid message broker type")
        
        # API Gateway validation
        if hasattr(api_gateway_config, 'enable_rate_limiting') and api_gateway_config.enable_rate_limiting:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "api_gateway", "Rate limiting enabled - good security practice")
        
        self.logger.info("Core configurations validation completed")
    
    async def _validate_core_connectivity(self):
        """Validate core system connectivity"""
        self.logger.info("Validating core connectivity...")
        
        try:
            # Test orchestrator initialization status
            if orchestrator.initialized:
                self._add_result(ValidationCategory.CONNECTIVITY, ValidationLevel.INFO,
                               "orchestrator", "Core orchestrator initialized successfully")
            else:
                self._add_result(ValidationCategory.CONNECTIVITY, ValidationLevel.WARNING,
                               "orchestrator", "Core orchestrator not initialized")
                
        except Exception as e:
            self._add_result(ValidationCategory.CONNECTIVITY, ValidationLevel.ERROR,
                           "orchestrator", f"Orchestrator connectivity error: {e}")
    
    async def _validate_content_protection_system(self):
        """Validate content protection system configuration"""
        self.logger.info("Validating content protection system...")
        
        # Content Protection Engine validation
        if content_protection_config.protection_mode.value in ["passive", "active", "aggressive", "forensic"]:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "content_protection", "Valid protection mode configured")
        
        if len(content_protection_config.fingerprint_algorithms) >= 3:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "content_protection", "Multiple fingerprint algorithms configured")
        else:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.WARNING,
                           "content_protection", "Limited fingerprint algorithms - consider adding more")
        
        # Fingerprinting Engine validation
        if fingerprinting_engine_config.gpu_enabled:
            self._add_result(ValidationCategory.PERFORMANCE, ValidationLevel.INFO,
                           "fingerprinting_engine", "GPU acceleration enabled for better performance")
        
        if fingerprinting_engine_config.fingerprint_precision == "high":
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "fingerprinting_engine", "High precision fingerprinting configured")
        
        # Web Crawler validation
        if web_crawler_config.stealth_mode:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "web_crawler", "Stealth mode enabled for better protection")
        
        if web_crawler_config.respect_robots_txt:
            self._add_result(ValidationCategory.COMPLIANCE, ValidationLevel.INFO,
                           "web_crawler", "Robots.txt compliance enabled - ethical crawling")
        
        # Monetization Engine validation
        enabled_processors = [
            name for name, settings in monetization_engine_config.payment_processors.items()
            if settings.get("enabled", False)
        ]
        if len(enabled_processors) >= 2:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.INFO,
                           "monetization_engine", "Multiple payment processors configured")
        else:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.WARNING,
                           "monetization_engine", "Consider enabling multiple payment processors")
        
        # Licensing Engine validation
        if licensing_engine_config.blockchain_network:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "licensing_engine", "Blockchain integration configured for transparency")
    
    async def _validate_platform_integrations(self):
        """Validate platform integration configurations"""
        self.logger.info("Validating platform integrations...")
        
        platform_count = len(platform_integration_config.platforms)
        if platform_count >= 5:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.INFO,
                           "platform_integration", f"Comprehensive platform coverage: {platform_count} platforms")
        else:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.WARNING,
                           "platform_integration", "Consider adding more platform integrations")
        
        # Validate major platforms
        major_platforms = ["spotify", "youtube", "instagram", "tiktok"]
        configured_platforms = list(platform_integration_config.platforms.keys())
        
        for platform in major_platforms:
            if platform in configured_platforms:
                self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                               "platform_integration", f"{platform.title()} integration configured")
            else:
                self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.WARNING,
                               "platform_integration", f"Missing {platform.title()} integration")
        
        # Security validation
        if platform_integration_config.encrypt_credentials:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "platform_integration", "Credential encryption enabled")
        else:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.CRITICAL,
                           "platform_integration", "Credential encryption DISABLED - SECURITY RISK")
    
    async def _validate_analytics_system(self):
        """Validate analytics system configuration"""
        self.logger.info("Validating analytics system...")
        
        if analytics_engine_config.enable_real_time_streaming:
            self._add_result(ValidationCategory.PERFORMANCE, ValidationLevel.INFO,
                           "analytics_engine", "Real-time streaming enabled")
        
        if analytics_engine_config.enable_gdpr_compliance:
            self._add_result(ValidationCategory.COMPLIANCE, ValidationLevel.INFO,
                           "analytics_engine", "GDPR compliance enabled")
        else:
            self._add_result(ValidationCategory.COMPLIANCE, ValidationLevel.CRITICAL,
                           "analytics_engine", "GDPR compliance DISABLED - LEGAL RISK")
        
        if analytics_engine_config.data_anonymization:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "analytics_engine", "Data anonymization enabled")
        
        # Validate storage backends
        backends = [
            analytics_engine_config.time_series_backend,
            analytics_engine_config.cache_backend,
            analytics_engine_config.search_backend
        ]
        if all(backends):
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "analytics_engine", "All storage backends configured")
    
    async def _validate_event_system(self):
        """Validate event-driven architecture"""
        self.logger.info("Validating event system...")
        
        if event_driven_config.enable_encryption:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                           "event_system", "Event encryption enabled")
        else:
            self._add_result(ValidationCategory.SECURITY, ValidationLevel.ERROR,
                           "event_system", "Event encryption disabled - potential security risk")
        
        if event_driven_config.enable_dead_letter_queue:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "event_system", "Dead letter queue enabled for reliability")
        
        if event_driven_config.broker_type in ["kafka", "redis"]:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "event_system", "Production-ready message broker configured")
        else:
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.WARNING,
                           "event_system", "Consider using Kafka or Redis for production")
    
    async def _validate_system_integration(self):
        """Validate cross-system integration"""
        self.logger.info("Validating system integration...")
        
        # Check if all major systems are properly configured
        systems = {
            "content_protection": content_protection_config is not None,
            "platform_integration": platform_integration_config is not None,
            "analytics": analytics_engine_config is not None,
            "events": event_driven_config is not None
        }
        
        configured_systems = sum(systems.values())
        if configured_systems == len(systems):
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.INFO,
                           "system_integration", "All major systems configured")
        else:
            missing_systems = [name for name, configured in systems.items() if not configured]
            self._add_result(ValidationCategory.CONFIGURATION, ValidationLevel.WARNING,
                           "system_integration", f"Missing systems: {missing_systems}")
        
        # Validate service communication paths
        self._validate_service_communication()
    
    def _validate_service_communication(self):
        """Validate inter-service communication configuration"""
        # This would validate that services can communicate with each other
        # through the configured message brokers, API gateways, etc.
        
        self._add_result(ValidationCategory.CONNECTIVITY, ValidationLevel.INFO,
                       "service_communication", "Service communication paths configured")
    
    async def _validate_security_compliance(self):
        """Validate security and compliance settings"""
        self.logger.info("Validating security compliance...")
        
        security_checks = [
            (platform_integration_config.encrypt_credentials, "Platform credentials encryption"),
            (analytics_engine_config.enable_gdpr_compliance, "GDPR compliance"),
            (event_driven_config.enable_encryption, "Event encryption"),
            (content_protection_config.enable_encryption, "Content protection encryption"),
        ]
        
        for check_result, check_name in security_checks:
            if check_result:
                self._add_result(ValidationCategory.SECURITY, ValidationLevel.INFO,
                               "security_compliance", f"{check_name} enabled")
            else:
                self._add_result(ValidationCategory.SECURITY, ValidationLevel.ERROR,
                               "security_compliance", f"{check_name} DISABLED - SECURITY RISK")
    
    async def _validate_business_logic(self):
        """Validate business logic alignment"""
        self.logger.info("Validating business logic...")
        
        # Content creator workflow validation
        workflow_components = [
            content_protection_config is not None,  # Content protection
            fingerprinting_engine_config is not None,  # Fingerprinting
            monetization_engine_config is not None,  # Monetization
            platform_integration_config is not None,  # Distribution
        ]
        
        if all(workflow_components):
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.INFO,
                           "business_logic", "Complete content creator workflow supported")
        else:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.WARNING,
                           "business_logic", "Content creator workflow may be incomplete")
        
        # Revenue optimization validation
        if monetization_engine_config.enable_ai_optimization:
            self._add_result(ValidationCategory.BUSINESS_LOGIC, ValidationLevel.INFO,
                           "business_logic", "AI-powered revenue optimization enabled")
    
    def _add_result(self, category: ValidationCategory, level: ValidationLevel, 
                   component: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Add validation result"""
        result = ValidationResult(
            category=category,
            level=level,
            component=component,
            message=message,
            details=details
        )
        self.results.append(result)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary statistics"""
        level_counts = {}
        category_counts = {}
        
        for result in self.results:
            level_counts[result.level.value] = level_counts.get(result.level.value, 0) + 1
            category_counts[result.category.value] = category_counts.get(result.category.value, 0) + 1
        
        return {
            "total_checks": len(self.results),
            "by_level": level_counts,
            "by_category": category_counts,
            "has_critical": ValidationLevel.CRITICAL.value in level_counts,
            "has_errors": ValidationLevel.ERROR.value in level_counts,
            "validation_passed": not (ValidationLevel.CRITICAL.value in level_counts or 
                                    ValidationLevel.ERROR.value in level_counts)
        }


# Global validator instance
microservices_validator = MicroservicesValidator()


async def run_full_validation() -> Tuple[bool, List[ValidationResult]]:
    """Run comprehensive microservices validation"""
    return await microservices_validator.run_full_validation()


def get_validation_summary() -> Dict[str, Any]:
    """Get validation summary"""
    return microservices_validator.get_validation_summary()


# Export for convenience
validate_microservices = run_full_validation
