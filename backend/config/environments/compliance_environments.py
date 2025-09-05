"""Compliance Environments Configuration
=======================================

Compliance configuration for different regulatory environments including
GDPR, CCPA, and other regional compliance requirements.

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

def get_config(compliance_type: str = 'gdpr') -> Dict[str, Any]:
    """Get compliance environment configuration"""
    
    if compliance_type.lower() == 'gdpr':
        return get_gdpr_config()
    elif compliance_type.lower() == 'ccpa':
        return get_ccpa_config()
    elif compliance_type.lower() == 'pipeda':
        return get_pipeda_config()
    else:
        return get_general_compliance_config()

def get_gdpr_config() -> Dict[str, Any]:
    """GDPR compliance configuration for European Union"""
    return {
        'compliance_type': 'gdpr',
        'region': 'eu',
        'data_residency': 'eu_only',
        
        'data_protection': {
            'consent_required': True,
            'explicit_consent': True,
            'consent_withdrawal': True,
            'data_minimization': True,
            'purpose_limitation': True,
            'storage_limitation': True,
            'accuracy_principle': True,
            'integrity_confidentiality': True,
            'accountability': True
        },
        
        'user_rights': {
            'right_to_information': True,
            'right_of_access': True,
            'right_to_rectification': True,
            'right_to_erasure': True,
            'right_to_restrict_processing': True,
            'right_to_data_portability': True,
            'right_to_object': True,
            'rights_related_to_automated_decision_making': True
        },
        
        'data_handling': {
            'lawful_basis_required': True,
            'dpo_required': True,
            'privacy_impact_assessment': True,
            'data_breach_notification_72h': True,
            'records_of_processing': True,
            'privacy_by_design': True,
            'privacy_by_default': True
        },
        
        'technical_measures': {
            'encryption_at_rest': 'AES-256',
            'encryption_in_transit': 'TLS-1.3',
            'pseudonymization': True,
            'anonymization': True,
            'access_controls': 'role_based',
            'audit_logging': True,
            'data_loss_prevention': True
        },
        
        'retention_policies': {
            'personal_data_retention_days': 365,
            'consent_records_retention_years': 3,
            'audit_logs_retention_years': 6,
            'automated_deletion': True
        }
    }

def get_ccpa_config() -> Dict[str, Any]:
    """CCPA compliance configuration for California"""
    return {
        'compliance_type': 'ccpa',
        'region': 'california',
        'data_residency': 'us_preferred',
        
        'consumer_rights': {
            'right_to_know': True,
            'right_to_delete': True,
            'right_to_opt_out_of_sale': True,
            'right_to_non_discrimination': True,
            'right_to_correct_inaccurate_information': True
        },
        
        'business_obligations': {
            'privacy_policy_disclosure': True,
            'collection_notice': True,
            'opt_out_methods': ['website_form', 'toll_free_number'],
            'verification_procedures': True,
            'employee_training': True
        },
        
        'data_handling': {
            'purpose_disclosure': True,
            'source_disclosure': True,
            'third_party_sharing_disclosure': True,
            'retention_period_disclosure': True,
            'do_not_sell_requests': True
        },
        
        'technical_measures': {
            'encryption_at_rest': 'AES-256',
            'encryption_in_transit': 'TLS-1.2',
            'access_controls': 'attribute_based',
            'audit_logging': True,
            'data_mapping': True
        },
        
        'retention_policies': {
            'personal_information_retention_days': 730,
            'consumer_request_records_retention_years': 2,
            'automated_deletion': True
        }
    }

def get_pipeda_config() -> Dict[str, Any]:
    """PIPEDA compliance configuration for Canada"""
    return {
        'compliance_type': 'pipeda',
        'region': 'canada',
        'data_residency': 'canada_preferred',
        
        'privacy_principles': {
            'accountability': True,
            'identifying_purposes': True,
            'consent': True,
            'limiting_collection': True,
            'limiting_use_disclosure': True,
            'accuracy': True,
            'safeguards': True,
            'openness': True,
            'individual_access': True,
            'challenging_compliance': True
        },
        
        'consent_requirements': {
            'meaningful_consent': True,
            'express_consent_sensitive': True,
            'implied_consent_non_sensitive': True,
            'withdrawal_mechanisms': True
        },
        
        'technical_measures': {
            'encryption_at_rest': 'AES-256',
            'encryption_in_transit': 'TLS-1.2',
            'access_controls': 'role_based',
            'breach_notification': True,
            'privacy_impact_assessment': True
        },
        
        'retention_policies': {
            'personal_information_retention_days': 365,
            'consent_records_retention_years': 1,
            'automated_deletion': True
        }
    }

def get_general_compliance_config() -> Dict[str, Any]:
    """General compliance configuration for global operations"""
    return {
        'compliance_type': 'general',
        'region': 'global',
        'data_residency': 'flexible',
        
        'basic_principles': {
            'data_minimization': True,
            'purpose_limitation': True,
            'transparency': True,
            'user_control': True,
            'security_safeguards': True
        },
        
        'user_rights': {
            'access_to_data': True,
            'data_correction': True,
            'data_deletion': True,
            'opt_out_mechanisms': True
        },
        
        'technical_measures': {
            'encryption_at_rest': 'AES-256',
            'encryption_in_transit': 'TLS-1.2',
            'access_controls': 'basic',
            'audit_logging': True
        },
        
        'retention_policies': {
            'default_retention_days': 365,
            'audit_logs_retention_years': 1,
            'automated_deletion': True
        }
    }

def get_all_compliance_configs() -> Dict[str, Dict[str, Any]]:
    """Get all compliance configurations"""
    return {
        'gdpr': get_gdpr_config(),
        'ccpa': get_ccpa_config(),
        'pipeda': get_pipeda_config(),
        'general': get_general_compliance_config()
    }