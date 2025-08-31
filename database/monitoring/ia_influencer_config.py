"""IA Influencer Agent Monitoring Configuration

Specialized configuration for IA Influencer Agent monitoring components including
content pipeline monitoring and monetization performance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class MonitoringProfile(Enum):
    """Monitoring profiles for different deployment environments"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"


@dataclass
class IAInfluencerMonitoringConfig:
    """Configuration for IA Influencer Agent monitoring system"""    
    # Content Pipeline Monitoring Configuration
    content_pipeline_config = {
        'monitoring_enabled': True,
        'real_time_tracking': True,
        'ai_analysis_enabled': True,
        'retention_days': 90,
        
        # Content type specific thresholds
        'processing_thresholds': {
            'audio': {
                'max_processing_time_seconds': 30.0,
                'max_file_size_mb': 500,
                'min_quality_score': 0.8,
                'min_ai_confidence': 0.85
            },
            'video': {
                'max_processing_time_seconds': 120.0,
                'max_file_size_mb': 2000,
                'min_quality_score': 0.75,
                'min_ai_confidence': 0.8
            },
            'image': {
                'max_processing_time_seconds': 10.0,
                'max_file_size_mb': 100,
                'min_quality_score': 0.85,
                'min_ai_confidence': 0.9
            },
            'text': {
                'max_processing_time_seconds': 5.0,
                'max_file_size_mb': 10,
                'min_quality_score': 0.8,
                'min_ai_confidence': 0.85
            }
        },
        
        # Pipeline performance thresholds
        'pipeline_thresholds': {
            'min_success_rate': 0.98,
            'max_error_rate': 0.02,
            'min_throughput_mb_per_second': 1.0,
            'max_queue_size': 1000,
            'max_processing_delay_minutes': 5
        },
        
        # AI processing configuration
        'ai_processing': {
            'fingerprinting_accuracy_minimum': 0.95,
            'content_analysis_depth': 'advanced',
            'protection_effectiveness_minimum': 0.9,
            'seo_optimization_enabled': True,
            'collaboration_matching_enabled': True
        }
    }
    
    # Monetization Performance Monitoring Configuration
    monetization_config = {
        'monitoring_enabled': True,
        'real_time_revenue_tracking': True,
        'ai_optimization_enabled': True,
        'retention_days': 365,  # Keep revenue data for 1 year
        
        # Revenue performance thresholds
        'revenue_thresholds': {
            'minimum_conversion_rate': 0.02,
            'minimum_roi_percentage': 150.0,
            'maximum_cost_per_acquisition': 50.0,
            'minimum_lifetime_value': 200.0,
            'revenue_growth_target_monthly': 5.0
        },
        
        # Platform-specific configurations
        'platform_configs': {
            'spotify': {
                'revenue_model': 'streaming',
                'min_payout_threshold': 20.0,
                'expected_conversion_rate': 0.03,
                'revenue_per_stream': 0.004,
                'payout_schedule': 'monthly'
            },
            'youtube': {
                'revenue_model': 'advertisement',
                'min_payout_threshold': 100.0,
                'expected_conversion_rate': 0.05,
                'revenue_per_view': 0.001,
                'payout_schedule': 'monthly'
            },
            'instagram': {
                'revenue_model': 'sponsored_content',
                'min_payout_threshold': 50.0,
                'expected_conversion_rate': 0.08,
                'revenue_per_post': 10.0,
                'payout_schedule': 'weekly'
            },
            'tiktok': {
                'revenue_model': 'creator_fund',
                'min_payout_threshold': 10.0,
                'expected_conversion_rate': 0.04,
                'revenue_per_view': 0.02,
                'payout_schedule': 'weekly'
            }
        },
        
        # Business intelligence settings
        'analytics': {
            'creator_satisfaction_minimum': 4.0,
            'platform_efficiency_minimum': 0.8,
            'revenue_prediction_enabled': True,
            'market_trend_analysis': True,
            'competitor_analysis_enabled': False  # Privacy compliant
        }
    }
    
    # Database Performance Configuration for IA Influencer Agent
    database_performance_config = {
        'monitoring_interval_seconds': 60,
        'ai_analysis_enabled': True,
        'predictive_scaling': True,
        
        # IA-specific database thresholds
        'thresholds': {
            'content_processing_query_time_ms': 500,
            'fingerprinting_query_time_ms': 200,
            'monetization_query_time_ms': 100,
            'analytics_query_time_ms': 1000,
            'content_search_query_time_ms': 300,
            
            # Connection pool settings for high-throughput content processing
            'max_connections_content_processing': 50,
            'max_connections_analytics': 20,
            'max_connections_monetization': 30,
            
            # Cache hit ratios for different workloads
            'content_cache_hit_ratio_minimum': 0.9,
            'analytics_cache_hit_ratio_minimum': 0.85,
            'monetization_cache_hit_ratio_minimum': 0.95
        }
    }
    
    # Alert Configuration
    alert_config = {
        'enabled': True,
        'escalation_enabled': True,
        'multi_channel_notifications': True,
        
        # Alert channels
        'channels': {
            'slack': {
                'enabled': True,
                'webhook_url': '${SLACK_WEBHOOK_URL}',
                'channel': '#ia-influencer-monitoring'
            },
            'email': {
                'enabled': True,
                'smtp_config': {
                    'host': '${SMTP_HOST}',
                    'port': 587,
                    'username': '${SMTP_USERNAME}',
                    'password': '${SMTP_PASSWORD}',
                    'use_tls': True
                },
                'recipients': ['${ADMIN_EMAIL}', 'mlaiel@live.de']
            },
            'discord': {
                'enabled': False,
                'webhook_url': '${DISCORD_WEBHOOK_URL}'
            }
        },
        
        # Alert thresholds by severity
        'severity_thresholds': {
            'critical': {
                'pipeline_failure_rate': 0.1,
                'revenue_drop_percentage': 20.0,
                'database_performance_degradation': 50.0,
                'content_processing_backlog_hours': 2.0
            },
            'warning': {
                'pipeline_failure_rate': 0.05,
                'revenue_drop_percentage': 10.0,
                'database_performance_degradation': 25.0,
                'content_processing_backlog_hours': 1.0
            },
            'info': {
                'pipeline_optimization_opportunities': True,
                'revenue_optimization_suggestions': True,
                'performance_improvement_recommendations': True
            }
        },
        
        # Escalation rules
        'escalation': {
            'enabled': True,
            'escalation_delay_minutes': 15,
            'max_escalation_levels': 3,
            'escalation_contacts': [
                'mlaiel@live.de',
                '${TECHNICAL_LEAD_EMAIL}',
                '${OPERATIONS_MANAGER_EMAIL}'
            ]
        }
    }
    
    # Security and Compliance Configuration
    security_config = {
        'monitoring_enabled': True,
        'compliance_tracking': True,
        'audit_logging': True,
        
        # Data protection settings
        'data_protection': {
            'pii_detection_enabled': True,
            'gdpr_compliance_mode': True,
            'data_retention_policies': {
                'creator_data_retention_days': 2555,  # 7 years for financial records
                'content_metadata_retention_days': 1095,  # 3 years
                'analytics_data_retention_days': 365,  # 1 year
                'performance_logs_retention_days': 90
            }
        },
        
        # Access monitoring
        'access_monitoring': {
            'track_database_access': True,
            'detect_anomalous_patterns': True,
            'threat_detection_enabled': True,
            'failed_login_threshold': 5,
            'suspicious_activity_threshold': 10
        }
    }


def get_monitoring_config(profile: MonitoringProfile = MonitoringProfile.PRODUCTION) -> Dict[str, Any]:
    """Get monitoring configuration for specified profile"""    
    base_config = IAInfluencerMonitoringConfig()
    
    # Profile-specific adjustments
    if profile == MonitoringProfile.DEVELOPMENT:
        # More relaxed thresholds for development
        base_config.content_pipeline_config['processing_thresholds']['audio']['max_processing_time_seconds'] = 60.0
        base_config.content_pipeline_config['processing_thresholds']['video']['max_processing_time_seconds'] = 300.0
        base_config.monetization_config['revenue_thresholds']['minimum_conversion_rate'] = 0.01
        base_config.alert_config['escalation']['enabled'] = False
        
    elif profile == MonitoringProfile.STAGING:
        # Staging environment adjustments
        base_config.content_pipeline_config['retention_days'] = 30
        base_config.monetization_config['retention_days'] = 90
        base_config.alert_config['channels']['slack']['channel'] = '#ia-influencer-staging'
        
    elif profile == MonitoringProfile.HIGH_PERFORMANCE:
        # Stricter thresholds for high-performance environments
        base_config.content_pipeline_config['processing_thresholds']['audio']['max_processing_time_seconds'] = 15.0
        base_config.content_pipeline_config['processing_thresholds']['video']['max_processing_time_seconds'] = 60.0
        base_config.database_performance_config['thresholds']['content_processing_query_time_ms'] = 250
        base_config.monetization_config['revenue_thresholds']['minimum_conversion_rate'] = 0.03
    
    return {
        'content_pipeline': base_config.content_pipeline_config,
        'monetization': base_config.monetization_config,
        'database_performance': base_config.database_performance_config,
        'alerts': base_config.alert_config,
        'security': base_config.security_config,
        'profile': profile.value
    }


# Default configuration instance
DEFAULT_MONITORING_CONFIG = get_monitoring_config(MonitoringProfile.PRODUCTION)
