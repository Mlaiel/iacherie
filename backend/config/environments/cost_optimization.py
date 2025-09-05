"""Cost Optimization Configuration
==================================

Cost optimization configuration for different cloud environments and
deployment scenarios for the IA-Influencer Agent Platform.

Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, Any, List
import os

def get_config(strategy: str = 'balanced') -> Dict[str, Any]:
    """Get cost optimization configuration"""
    
    strategies = {
        'aggressive': get_aggressive_cost_optimization(),
        'balanced': get_balanced_cost_optimization(),
        'performance_first': get_performance_first_optimization()
    }
    
    return strategies.get(strategy, get_balanced_cost_optimization())

def get_aggressive_cost_optimization() -> Dict[str, Any]:
    """Aggressive cost optimization for maximum savings"""
    return {
        'strategy': 'aggressive',
        'target_cost_reduction': '40-60%',
        
        'compute_optimization': {
            'spot_instances': {
                'enabled': True,
                'percentage': 80,
                'fallback_on_demand': True,
                'diversification': True
            },
            'reserved_instances': {
                'enabled': True,
                'percentage': 70,
                'term': '3_years',
                'payment_option': 'all_upfront'
            },
            'instance_rightsizing': {
                'enabled': True,
                'automated': True,
                'frequency': 'weekly',
                'downsize_threshold': 20
            }
        },
        
        'storage_optimization': {
            'tiered_storage': {
                'enabled': True,
                'frequent_access': 'standard',
                'infrequent_access': 'standard_ia',
                'archive': 'glacier',
                'deep_archive': 'glacier_deep_archive'
            },
            'lifecycle_policies': {
                'transition_to_ia_days': 30,
                'transition_to_archive_days': 90,
                'transition_to_deep_archive_days': 365,
                'delete_after_days': 2555  # 7 years
            }
        },
        
        'database_optimization': {
            'instance_scheduling': {
                'enabled': True,
                'dev_environment_hours': '8:00-18:00',
                'staging_environment_hours': '6:00-22:00'
            },
            'read_replica_optimization': {
                'enabled': True,
                'scale_down_during_low_traffic': True,
                'minimum_replicas': 0
            }
        },
        
        'monitoring_alerts': {
            'cost_thresholds': {
                'daily_limit': 100,
                'monthly_limit': 2000,
                'anomaly_detection': True
            },
            'resource_waste_detection': {
                'idle_resources': True,
                'unused_resources': True,
                'oversized_resources': True
            }
        }
    }

def get_balanced_cost_optimization() -> Dict[str, Any]:
    """Balanced cost optimization maintaining performance"""
    return {
        'strategy': 'balanced',
        'target_cost_reduction': '20-35%',
        
        'compute_optimization': {
            'spot_instances': {
                'enabled': True,
                'percentage': 50,
                'fallback_on_demand': True,
                'diversification': True
            },
            'reserved_instances': {
                'enabled': True,
                'percentage': 40,
                'term': '1_year',
                'payment_option': 'partial_upfront'
            },
            'instance_rightsizing': {
                'enabled': True,
                'automated': False,
                'frequency': 'monthly',
                'downsize_threshold': 30
            }
        },
        
        'storage_optimization': {
            'tiered_storage': {
                'enabled': True,
                'frequent_access': 'standard',
                'infrequent_access': 'standard_ia',
                'archive': 'glacier'
            },
            'lifecycle_policies': {
                'transition_to_ia_days': 60,
                'transition_to_archive_days': 180,
                'delete_after_days': 2555
            }
        },
        
        'database_optimization': {
            'instance_scheduling': {
                'enabled': True,
                'dev_environment_hours': '6:00-20:00'
            },
            'read_replica_optimization': {
                'enabled': True,
                'scale_down_during_low_traffic': False,
                'minimum_replicas': 1
            }
        },
        
        'monitoring_alerts': {
            'cost_thresholds': {
                'daily_limit': 200,
                'monthly_limit': 5000,
                'anomaly_detection': True
            }
        }
    }

def get_performance_first_optimization() -> Dict[str, Any]:
    """Performance-first optimization with minimal cost impact"""
    return {
        'strategy': 'performance_first',
        'target_cost_reduction': '5-15%',
        
        'compute_optimization': {
            'spot_instances': {
                'enabled': True,
                'percentage': 20,
                'fallback_on_demand': True,
                'only_for_batch_jobs': True
            },
            'reserved_instances': {
                'enabled': True,
                'percentage': 60,
                'term': '1_year',
                'payment_option': 'no_upfront'
            },
            'instance_rightsizing': {
                'enabled': True,
                'automated': False,
                'frequency': 'quarterly',
                'conservative_approach': True
            }
        },
        
        'storage_optimization': {
            'tiered_storage': {
                'enabled': True,
                'frequent_access': 'standard',
                'archive_only_old_data': True
            },
            'lifecycle_policies': {
                'transition_to_archive_days': 365,
                'delete_after_days': 2555
            }
        },
        
        'monitoring_alerts': {
            'cost_thresholds': {
                'monthly_limit': 10000,
                'anomaly_detection': True
            }
        }
    }

def get_cost_allocation_tags() -> Dict[str, List[str]]:
    """Get cost allocation tagging strategy"""
    return {
        'mandatory_tags': [
            'Environment',
            'Project',
            'Owner',
            'CostCenter'
        ],
        'optional_tags': [
            'Application',
            'Version',
            'Purpose',
            'CreatedBy',
            'ExpirationDate'
        ],
        'cost_tracking_tags': [
            'Environment',
            'Project',
            'Application',
            'CostCenter'
        ]
    }

def get_budget_alerts() -> Dict[str, Any]:
    """Get budget alert configuration"""
    return {
        'budgets': {
            'overall_monthly': {
                'amount': 5000,
                'alerts': [
                    {'threshold': 50, 'type': 'email'},
                    {'threshold': 80, 'type': 'email_and_slack'},
                    {'threshold': 90, 'type': 'email_slack_and_webhook'},
                    {'threshold': 100, 'type': 'all_channels_and_auto_action'}
                ]
            },
            'development_monthly': {
                'amount': 500,
                'alerts': [
                    {'threshold': 80, 'type': 'email'},
                    {'threshold': 100, 'type': 'email_and_auto_shutdown'}
                ]
            },
            'production_monthly': {
                'amount': 3000,
                'alerts': [
                    {'threshold': 60, 'type': 'email'},
                    {'threshold': 85, 'type': 'email_and_slack'},
                    {'threshold': 95, 'type': 'all_channels'}
                ]
            }
        }
    }