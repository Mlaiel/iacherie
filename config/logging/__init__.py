"""Enterprise Logging Configuration Module for IA-Influencer Agent Platform
========================================================================

Industrial-grade logging and audit trail configuration management for multi-format
content creators (musicians, bloggers, photographers, influencers, comedians)
with AI protection, SEO optimization, collaboration matching, and monetization tracking.

Business Logic Flow:
User Upload → AI Protection & Rights → SEO Optimization → 
Collaboration Matching → Multi-Platform Distribution → Revenue Tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer

  CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

Contact: mlaiel@live.de for licensing inquiries only.
"""
# Import main enterprise logging system
from .index import (
    EnterpriseLoggingSystem,
    SystemLoggingConfig,
    LoggingSystemTier,
    LoggingModuleType,
    
    # Factory functions
    create_development_logging_system,
    create_staging_logging_system,
    create_production_logging_system,
    create_enterprise_logging_system,
    create_high_security_logging_system,
    
    # Global system functions
    initialize_global_logging_system,
    get_global_logging_system,
    shutdown_global_logging_system
)

from .log_config import LogConfig
from .structured_logging_config import StructuredLoggingConfig
from .audit_config import AuditConfig
from .log_rotation_config import LogRotationConfig
from .log_aggregation_config import LogAggregationConfig
from .log_filtering_config import LogFilteringConfig
from .security_logging_config import SecurityLoggingConfig
from .performance_logging_config import PerformanceLoggingConfig
from .content_protection_logging_config import ContentProtectionLoggingConfig
from .monetization_logging_config import MonetizationLoggingConfig
from .collaboration_logging_config import CollaborationLoggingConfig
from .ai_processing_logging_config import AIProcessingLoggingConfig
from .platform_integration_logging_config import PlatformIntegrationLoggingConfig
from .creator_analytics_logging_config import CreatorAnalyticsLoggingConfig
from .rights_management_logging_config import RightsManagementLoggingConfig
from .multi_format_logging_config import MultiFormatLoggingConfig
from .compliance_logging_config import ComplianceLoggingConfig
from .real_time_logging_config import RealTimeLoggingConfig

__all__ = [
    'LogConfig',
    'StructuredLoggingConfig', 
    'AuditConfig',
    'LogRotationConfig',
    'LogAggregationConfig',
    'LogFilteringConfig',
    'SecurityLoggingConfig',
    'PerformanceLoggingConfig',
    'ContentProtectionLoggingConfig',
    'MonetizationLoggingConfig',
    'CollaborationLoggingConfig',
    'AIProcessingLoggingConfig',
    'PlatformIntegrationLoggingConfig',
    'CreatorAnalyticsLoggingConfig',
    'RightsManagementLoggingConfig',
    'MultiFormatLoggingConfig',
    'ComplianceLoggingConfig',
    'RealTimeLoggingConfig'
]
