"""Regional Configuration
========================

Regional configuration settings for compliance, performance optimization,
and localization across different geographical regions for the IA-Influencer Agent Platform.

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

from typing import Dict, Any
import os

def get_config(region: str = 'eu') -> Dict[str, Any]:
    """Get regional configuration"""
    
    if region.lower() in ['eu', 'europe']:
        return get_eu_config()
    elif region.lower() in ['us', 'usa', 'north_america']:
        return get_us_config()
    elif region.lower() in ['asia', 'apac']:
        return get_asia_config()
    else:
        return get_default_config()

def get_eu_config() -> Dict[str, Any]:
    """Get European Union regional configuration"""
    return {
        'region': 'eu',
        'timezone': 'Europe/Berlin',
        'currency': 'EUR',
        'language': 'de',
        'data_residency': 'eu',
        
        # GDPR Compliance
        'compliance': {
            'gdpr': {
                'enabled': True,
                'consent_required': True,
                'data_retention_days': 365,
                'right_to_be_forgotten': True,
                'data_portability': True,
                'privacy_by_design': True
            },
            'cookie_policy': {
                'consent_banner': True,
                'essential_cookies_only': False,
                'analytics_cookies_consent': True
            }
        },
        
        # Data centers and regions
        'infrastructure': {
            'primary_region': 'eu-central-1',
            'backup_region': 'eu-west-1',
            'edge_locations': [
                'Frankfurt', 'Amsterdam', 'London', 'Paris', 'Milan'
            ],
            'data_residency_strict': True,
            'cross_border_transfer': False
        },
        
        # Performance optimization
        'performance': {
            'cdn_endpoints': [
                'https://cdn-eu.ainflue.com',
                'https://assets-eu.ainflue.com'
            ],
            'image_optimization': True,
            'compression': 'brotli',
            'cache_strategy': 'aggressive'
        },
        
        # Localization
        'localization': {
            'supported_languages': ['de', 'en', 'fr', 'es', 'it'],
            'default_language': 'de',
            'date_format': 'DD.MM.YYYY',
            'number_format': 'european',
            'address_format': 'european'
        },
        
        # Payment processing
        'payments': {
            'supported_methods': ['sepa', 'credit_card', 'paypal', 'sofort'],
            'default_currency': 'EUR',
            'tax_calculation': 'vat',
            'vat_rates': {
                'DE': 0.19,
                'FR': 0.20,
                'IT': 0.22,
                'ES': 0.21
            }
        }
    }

def get_us_config() -> Dict[str, Any]:
    """Get United States regional configuration"""
    return {
        'region': 'us',
        'timezone': 'America/New_York',
        'currency': 'USD',
        'language': 'en',
        'data_residency': 'us',
        
        # CCPA Compliance
        'compliance': {
            'ccpa': {
                'enabled': True,
                'opt_out_required': True,
                'data_retention_days': 730,
                'do_not_sell': True,
                'personal_info_disclosure': True
            },
            'cookie_policy': {
                'consent_banner': False,
                'essential_cookies_only': False,
                'opt_out_available': True
            }
        },
        
        # Data centers and regions
        'infrastructure': {
            'primary_region': 'us-east-1',
            'backup_region': 'us-west-2',
            'edge_locations': [
                'New York', 'Los Angeles', 'Chicago', 'Dallas', 'Miami'
            ],
            'data_residency_strict': True,
            'cross_border_transfer': False
        },
        
        # Performance optimization
        'performance': {
            'cdn_endpoints': [
                'https://cdn-us.ainflue.com',
                'https://assets-us.ainflue.com'
            ],
            'image_optimization': True,
            'compression': 'gzip',
            'cache_strategy': 'moderate'
        },
        
        # Localization
        'localization': {
            'supported_languages': ['en', 'es'],
            'default_language': 'en',
            'date_format': 'MM/DD/YYYY',
            'number_format': 'american',
            'address_format': 'american'
        },
        
        # Payment processing
        'payments': {
            'supported_methods': ['credit_card', 'paypal', 'venmo', 'apple_pay'],
            'default_currency': 'USD',
            'tax_calculation': 'sales_tax',
            'state_tax_rates': {
                'CA': 0.0725,
                'NY': 0.08,
                'TX': 0.0625,
                'FL': 0.06
            }
        }
    }

def get_asia_config() -> Dict[str, Any]:
    """Get Asia Pacific regional configuration"""
    return {
        'region': 'asia',
        'timezone': 'Asia/Tokyo',
        'currency': 'JPY',
        'language': 'ja',
        'data_residency': 'asia',
        
        # Regional compliance
        'compliance': {
            'pdpa': {
                'enabled': True,
                'consent_required': True,
                'data_retention_days': 730
            },
            'privacy_laws': {
                'japan_appi': True,
                'singapore_pdpa': True,
                'australia_privacy_act': True
            }
        },
        
        # Data centers and regions
        'infrastructure': {
            'primary_region': 'ap-northeast-1',
            'backup_region': 'ap-southeast-1',
            'edge_locations': [
                'Tokyo', 'Singapore', 'Sydney', 'Seoul', 'Mumbai'
            ],
            'data_residency_strict': True,
            'cross_border_transfer': True
        },
        
        # Performance optimization
        'performance': {
            'cdn_endpoints': [
                'https://cdn-asia.ainflue.com',
                'https://assets-asia.ainflue.com'
            ],
            'image_optimization': True,
            'compression': 'gzip',
            'cache_strategy': 'aggressive'
        },
        
        # Localization
        'localization': {
            'supported_languages': ['ja', 'ko', 'zh', 'en'],
            'default_language': 'ja',
            'date_format': 'YYYY/MM/DD',
            'number_format': 'asian',
            'address_format': 'asian'
        },
        
        # Payment processing
        'payments': {
            'supported_methods': ['credit_card', 'alipay', 'wechat_pay', 'jcb'],
            'default_currency': 'JPY',
            'tax_calculation': 'consumption_tax',
            'country_tax_rates': {
                'JP': 0.10,
                'KR': 0.10,
                'SG': 0.07
            }
        }
    }

def get_default_config() -> Dict[str, Any]:
    """Get default regional configuration"""
    return {
        'region': 'global',
        'timezone': 'UTC',
        'currency': 'USD',
        'language': 'en',
        'data_residency': 'global',
        
        'compliance': {
            'basic_privacy': True,
            'consent_required': True,
            'data_retention_days': 365
        },
        
        'infrastructure': {
            'primary_region': 'us-east-1',
            'backup_region': 'eu-west-1',
            'edge_locations': ['Global CDN'],
            'data_residency_strict': False,
            'cross_border_transfer': True
        },
        
        'performance': {
            'cdn_endpoints': ['https://cdn.ainflue.com'],
            'image_optimization': True,
            'compression': 'gzip',
            'cache_strategy': 'moderate'
        },
        
        'localization': {
            'supported_languages': ['en'],
            'default_language': 'en',
            'date_format': 'YYYY-MM-DD',
            'number_format': 'international',
            'address_format': 'international'
        },
        
        'payments': {
            'supported_methods': ['credit_card', 'paypal'],
            'default_currency': 'USD',
            'tax_calculation': 'basic'
        }
    }

def get_all_regions() -> Dict[str, Dict[str, Any]]:
    """Get configuration for all supported regions"""
    return {
        'eu': get_eu_config(),
        'us': get_us_config(),
        'asia': get_asia_config(),
        'global': get_default_config()
    }