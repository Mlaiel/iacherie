#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Privacy Configuration Module
====================================

Enterprise-grade privacy configuration for the Ainflue platform.
Data privacy protection, consent management, anonymization, pseudonymization,
data minimization, and comprehensive privacy-by-design implementation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

class DataCategory(str, Enum):
    """Categories of personal data"""
    BASIC_IDENTITY = "basic_identity"
    CONTACT_INFO = "contact_info"
    DEMOGRAPHIC = "demographic"
    FINANCIAL = "financial"
    BEHAVIORAL = "behavioral"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    DEVICE_INFO = "device_info"
    CONTENT_DATA = "content_data"
    COMMUNICATION = "communication"
    SPECIAL_CATEGORY = "special_category"

class ConsentType(str, Enum):
    """Types of consent"""
    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    NECESSARY = "necessary"
    LEGITIMATE_INTEREST = "legitimate_interest"

class ProcessingPurpose(str, Enum):
    """Purposes for data processing"""
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    RESEARCH = "research"
    COMMUNICATION = "communication"

class PrivacyRight(str, Enum):
    """Privacy rights under various regulations"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    WITHDRAW_CONSENT = "withdraw_consent"

@dataclass
class ConsentRecord:
    """Individual consent record"""
    consent_id: str
    user_id: str
    data_category: DataCategory
    processing_purpose: ProcessingPurpose
    consent_type: ConsentType
    consent_given: bool
    timestamp: datetime
    expiry_date: Optional[datetime] = None
    withdrawal_date: Optional[datetime] = None
    consent_string: str = ""
    legal_basis: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert consent record to dictionary"""
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "data_category": self.data_category.value,
            "processing_purpose": self.processing_purpose.value,
            "consent_type": self.consent_type.value,
            "consent_given": self.consent_given,
            "timestamp": self.timestamp.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "withdrawal_date": self.withdrawal_date.isoformat() if self.withdrawal_date else None,
            "consent_string": self.consent_string,
            "legal_basis": self.legal_basis
        }

@dataclass
class ConsentManagementConfig:
    """Consent management configuration"""
    enabled: bool = True
    
    # Consent collection
    consent_collection: Dict[str, Any] = field(default_factory=lambda: {
        "granular_consent": True,
        "purpose_specific_consent": True,
        "consent_layering": True,
        "just_in_time_consent": True,
        "progressive_consent": True,
        "consent_receipts": True,
        "consent_proof_storage": True
    })
    
    # Consent UI/UX
    consent_interface: Dict[str, Any] = field(default_factory=lambda: {
        "user_friendly_language": True,
        "clear_explanations": True,
        "easy_withdrawal": True,
        "consent_dashboard": True,
        "mobile_optimized": True,
        "accessibility_compliant": True,
        "multi_language_support": True
    })
    
    # Consent lifecycle
    consent_lifecycle: Dict[str, Any] = field(default_factory=lambda: {
        "consent_expiry": True,
        "default_expiry_months": 24,
        "renewal_reminders": True,
        "automatic_withdrawal_detection": True,
        "consent_history_tracking": True,
        "audit_trail": True
    })
    
    # Legal compliance
    legal_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "gdpr_compliant": True,
        "ccpa_compliant": True,
        "cpra_compliant": True,
        "lgpd_compliant": True,
        "pipeda_compliant": True,
        "legal_basis_documentation": True,
        "regulatory_reporting": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get consent management configuration"""
        return {
            "enabled": self.enabled,
            "consent_collection": self.consent_collection,
            "consent_interface": self.consent_interface,
            "consent_lifecycle": self.consent_lifecycle,
            "legal_compliance": self.legal_compliance
        }

@dataclass
class DataMinimizationConfig:
    """Data minimization configuration"""
    enabled: bool = True
    
    # Collection minimization
    collection_minimization: Dict[str, Any] = field(default_factory=lambda: {
        "purpose_limitation": True,
        "necessity_assessment": True,
        "proportionality_check": True,
        "alternative_data_sources": True,
        "synthetic_data_preference": True,
        "data_collection_approval": True
    })
    
    # Storage minimization
    storage_minimization: Dict[str, Any] = field(default_factory=lambda: {
        "automated_deletion": True,
        "retention_schedules": True,
        "archive_instead_of_delete": True,
        "compression_techniques": True,
        "summarization_techniques": True,
        "data_lifecycle_management": True
    })
    
    # Processing minimization
    processing_minimization: Dict[str, Any] = field(default_factory=lambda: {
        "purpose_binding": True,
        "processing_logs": True,
        "access_controls": True,
        "need_to_know_basis": True,
        "automated_processing_limits": True,
        "human_oversight": True
    })
    
    # Data quality
    data_quality: Dict[str, Any] = field(default_factory=lambda: {
        "accuracy_checks": True,
        "completeness_validation": True,
        "consistency_verification": True,
        "timeliness_assessment": True,
        "relevance_scoring": True,
        "data_profiling": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get data minimization configuration"""
        return {
            "enabled": self.enabled,
            "collection_minimization": self.collection_minimization,
            "storage_minimization": self.storage_minimization,
            "processing_minimization": self.processing_minimization,
            "data_quality": self.data_quality
        }

@dataclass
class AnonymizationConfig:
    """Data anonymization configuration"""
    enabled: bool = True
    
    # Anonymization techniques
    techniques: Dict[str, Any] = field(default_factory=lambda: {
        "k_anonymity": {
            "enabled": True,
            "k_value": 5,
            "quasi_identifiers": ["age", "gender", "location", "profession"]
        },
        "l_diversity": {
            "enabled": True,
            "l_value": 3,
            "sensitive_attributes": ["health_data", "financial_data"]
        },
        "t_closeness": {
            "enabled": True,
            "t_value": 0.2,
            "earth_mover_distance": True
        },
        "differential_privacy": {
            "enabled": True,
            "epsilon": 0.1,
            "delta": 0.00001,
            "noise_mechanisms": ["laplace", "gaussian"]
        }
    })
    
    # Data transformation
    transformation_methods: Dict[str, Any] = field(default_factory=lambda: {
        "generalization": {
            "enabled": True,
            "hierarchical_generalization": True,
            "value_suppression": True,
            "range_replacement": True
        },
        "suppression": {
            "enabled": True,
            "random_suppression": True,
            "systematic_suppression": True,
            "conditional_suppression": True
        },
        "perturbation": {
            "enabled": True,
            "noise_addition": True,
            "micro_aggregation": True,
            "data_swapping": True
        },
        "synthetic_data": {
            "enabled": True,
            "generative_models": True,
            "statistical_models": True,
            "privacy_preserving_generation": True
        }
    })
    
    # Quality assessment
    quality_metrics: Dict[str, Any] = field(default_factory=lambda: {
        "information_loss": True,
        "disclosure_risk": True,
        "utility_preservation": True,
        "statistical_properties": True,
        "re_identification_risk": True,
        "privacy_budget_tracking": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get anonymization configuration"""
        return {
            "enabled": self.enabled,
            "techniques": self.techniques,
            "transformation_methods": self.transformation_methods,
            "quality_metrics": self.quality_metrics
        }

@dataclass
class PseudonymizationConfig:
    """Data pseudonymization configuration"""
    enabled: bool = True
    
    # Pseudonymization methods
    methods: Dict[str, Any] = field(default_factory=lambda: {
        "deterministic_pseudonyms": {
            "enabled": True,
            "hash_functions": ["sha256", "blake2b"],
            "salting": True,
            "key_derivation": True
        },
        "random_pseudonyms": {
            "enabled": True,
            "uuid_generation": True,
            "sequential_numbering": True,
            "custom_formats": True
        },
        "format_preserving": {
            "enabled": True,
            "fpe_algorithms": ["ff1", "ff3"],
            "character_set_preservation": True,
            "length_preservation": True
        },
        "tokenization": {
            "enabled": True,
            "vault_based": True,
            "vaultless": True,
            "reversible": True
        }
    })
    
    # Key management
    key_management: Dict[str, Any] = field(default_factory=lambda: {
        "secure_key_storage": True,
        "key_rotation": True,
        "key_versioning": True,
        "access_controls": True,
        "audit_logging": True,
        "backup_recovery": True
    })
    
    # Linking controls
    linking_controls: Dict[str, Any] = field(default_factory=lambda: {
        "cross_dataset_linking": False,
        "temporal_linking": True,
        "context_separation": True,
        "purpose_separation": True,
        "domain_separation": True,
        "re_pseudonymization": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get pseudonymization configuration"""
        return {
            "enabled": self.enabled,
            "methods": self.methods,
            "key_management": self.key_management,
            "linking_controls": self.linking_controls
        }

@dataclass
class DataSubjectRightsConfig:
    """Data subject rights configuration"""
    enabled: bool = True
    
    # Rights implementation
    rights_implementation: Dict[str, Any] = field(default_factory=lambda: {
        "access_right": {
            "enabled": True,
            "automated_response": True,
            "response_time_days": 30,
            "data_formats": ["json", "xml", "csv", "pdf"],
            "verification_required": True
        },
        "rectification_right": {
            "enabled": True,
            "automated_updates": True,
            "validation_required": True,
            "audit_trail": True,
            "notification_to_processors": True
        },
        "erasure_right": {
            "enabled": True,
            "hard_deletion": True,
            "soft_deletion": True,
            "retention_overrides": True,
            "third_party_notification": True
        },
        "portability_right": {
            "enabled": True,
            "structured_formats": True,
            "machine_readable": True,
            "direct_transmission": True,
            "secure_transfer": True
        }
    })
    
    # Request processing
    request_processing: Dict[str, Any] = field(default_factory=lambda: {
        "automated_workflow": True,
        "identity_verification": True,
        "request_validation": True,
        "status_tracking": True,
        "communication_templates": True,
        "escalation_procedures": True
    })
    
    # Response management
    response_management: Dict[str, Any] = field(default_factory=lambda: {
        "standardized_responses": True,
        "multilingual_support": True,
        "secure_delivery": True,
        "delivery_confirmation": True,
        "follow_up_procedures": True,
        "satisfaction_tracking": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get data subject rights configuration"""
        return {
            "enabled": self.enabled,
            "rights_implementation": self.rights_implementation,
            "request_processing": self.request_processing,
            "response_management": self.response_management
        }

@dataclass
class PrivacyByDesignConfig:
    """Privacy by design configuration"""
    enabled: bool = True
    
    # Design principles
    design_principles: Dict[str, Any] = field(default_factory=lambda: {
        "proactive_not_reactive": True,
        "privacy_as_default": True,
        "full_functionality": True,
        "end_to_end_security": True,
        "visibility_transparency": True,
        "respect_for_privacy": True,
        "architecture_integration": True
    })
    
    # Technical measures
    technical_measures: Dict[str, Any] = field(default_factory=lambda: {
        "privacy_enhancing_technologies": True,
        "secure_multi_party_computation": True,
        "homomorphic_encryption": True,
        "zero_knowledge_proofs": True,
        "federated_learning": True,
        "edge_computing": True,
        "privacy_preserving_analytics": True
    })
    
    # Organizational measures
    organizational_measures: Dict[str, Any] = field(default_factory=lambda: {
        "privacy_governance": True,
        "data_protection_impact_assessments": True,
        "privacy_training": True,
        "vendor_privacy_assessments": True,
        "privacy_incident_response": True,
        "continuous_monitoring": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get privacy by design configuration"""
        return {
            "enabled": self.enabled,
            "design_principles": self.design_principles,
            "technical_measures": self.technical_measures,
            "organizational_measures": self.organizational_measures
        }

class PrivacyConfiguration:
    """Main privacy configuration manager"""
    
    def __init__(self):
        """Initialize privacy configuration"""
        # Privacy components
        self.consent_management = ConsentManagementConfig()
        self.data_minimization = DataMinimizationConfig()
        self.anonymization_config = AnonymizationConfig()
        self.pseudonymization_config = PseudonymizationConfig()
        self.data_subject_rights = DataSubjectRightsConfig()
        self.privacy_by_design = PrivacyByDesignConfig()
        
        # Global privacy settings
        self.privacy_first_approach = True
        self.default_privacy_level = "high"
        self.privacy_impact_assessments = True
        self.cross_border_data_transfers = True
        
        # Data protection settings
        self.data_protection_officer = True
        self.regular_privacy_audits = True
        self.vendor_privacy_requirements = True
        self.employee_privacy_training = True
        
        # Regulatory compliance
        self.supported_regulations = [
            "GDPR", "CCPA", "CPRA", "LGPD", "PIPEDA", "PDPA", "DSGVO"
        ]
        
        # Privacy metrics and KPIs
        self.privacy_metrics_tracking = True
        self.consent_rate_monitoring = True
        self.privacy_incident_tracking = True
        self.data_breach_notification = True
    
    def get_privacy_maturity_score(self) -> float:
        """Calculate privacy maturity score (0-1)"""
        score = 0.0
        
        # Consent management sophistication
        if self.consent_management.enabled:
            score += 0.25
        
        # Data minimization practices
        if self.data_minimization.enabled:
            score += 0.20
        
        # Anonymization/pseudonymization capabilities
        if self.anonymization_config.enabled and self.pseudonymization_config.enabled:
            score += 0.20
        
        # Data subject rights implementation
        if self.data_subject_rights.enabled:
            score += 0.20
        
        # Privacy by design implementation
        if self.privacy_by_design.enabled:
            score += 0.15
        
        return min(score, 1.0)
    
    async def collect_consent(self, 
                            user_id: str,
                            data_category: DataCategory,
                            processing_purpose: ProcessingPurpose,
                            consent_details: Dict[str, Any]) -> ConsentRecord:
        """Collect and record user consent"""
        
        consent_record = ConsentRecord(
            consent_id=f"consent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            user_id=user_id,
            data_category=data_category,
            processing_purpose=processing_purpose,
            consent_type=ConsentType(consent_details.get("consent_type", "explicit")),
            consent_given=consent_details.get("consent_given", False),
            timestamp=datetime.now(),
            expiry_date=consent_details.get("expiry_date"),
            consent_string=consent_details.get("consent_string", ""),
            legal_basis=consent_details.get("legal_basis", "")
        )
        
        # Store consent record
        await self._store_consent_record(consent_record)
        
        # Generate consent receipt
        if self.consent_management.consent_collection["consent_receipts"]:
            await self._generate_consent_receipt(consent_record)
        
        return consent_record
    
    async def withdraw_consent(self, 
                             user_id: str,
                             consent_id: str) -> bool:
        """Withdraw user consent"""
        
        consent_record = await self._get_consent_record(consent_id)
        
        if consent_record and consent_record.user_id == user_id:
            consent_record.consent_given = False
            consent_record.withdrawal_date = datetime.now()
            
            # Update consent record
            await self._update_consent_record(consent_record)
            
            # Process data according to withdrawal
            await self._process_consent_withdrawal(consent_record)
            
            return True
        
        return False
    
    async def anonymize_data(self, 
                           dataset: List[Dict[str, Any]],
                           anonymization_level: str = "high") -> List[Dict[str, Any]]:
        """Anonymize dataset according to configuration"""
        
        if not self.anonymization_config.enabled:
            return dataset
        
        anonymized_dataset = []
        
        for record in dataset:
            anonymized_record = await self._apply_anonymization_techniques(
                record, 
                anonymization_level
            )
            anonymized_dataset.append(anonymized_record)
        
        # Assess anonymization quality
        quality_metrics = await self._assess_anonymization_quality(
            dataset, 
            anonymized_dataset
        )
        
        return anonymized_dataset
    
    async def pseudonymize_identifier(self, 
                                    identifier: str,
                                    context: str = "default") -> str:
        """Pseudonymize a data identifier"""
        
        if not self.pseudonymization_config.enabled:
            return identifier
        
        # Select pseudonymization method based on context
        method = self._select_pseudonymization_method(context)
        
        # Apply pseudonymization
        pseudonym = await self._apply_pseudonymization(identifier, method, context)
        
        # Log pseudonymization for audit
        await self._log_pseudonymization(identifier, pseudonym, method, context)
        
        return pseudonym
    
    async def process_data_subject_request(self, 
                                         request: Dict[str, Any]) -> Dict[str, Any]:
        """Process data subject rights request"""
        
        request_response = {
            "request_id": request.get("request_id"),
            "user_id": request.get("user_id"),
            "request_type": request.get("request_type"),
            "status": "processing",
            "response_data": None,
            "completion_date": None
        }
        
        try:
            # Verify user identity
            if not await self._verify_user_identity(request):
                request_response["status"] = "identity_verification_failed"
                return request_response
            
            # Process based on request type
            request_type = request.get("request_type")
            
            if request_type == PrivacyRight.ACCESS.value:
                response_data = await self._process_access_request(request)
            elif request_type == PrivacyRight.ERASURE.value:
                response_data = await self._process_erasure_request(request)
            elif request_type == PrivacyRight.RECTIFICATION.value:
                response_data = await self._process_rectification_request(request)
            elif request_type == PrivacyRight.PORTABILITY.value:
                response_data = await self._process_portability_request(request)
            else:
                request_response["status"] = "unsupported_request_type"
                return request_response
            
            request_response["response_data"] = response_data
            request_response["status"] = "completed"
            request_response["completion_date"] = datetime.now().isoformat()
            
        except Exception as e:
            request_response["status"] = "failed"
            request_response["error"] = str(e)
        
        return request_response
    
    async def conduct_privacy_impact_assessment(self, 
                                              processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct privacy impact assessment"""
        
        pia_result = {
            "pia_id": f"pia_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "activity": processing_activity.get("name"),
            "assessment_date": datetime.now().isoformat(),
            "risk_level": "unknown",
            "privacy_risks": [],
            "mitigation_measures": [],
            "recommendation": "proceed_with_caution"
        }
        
        # Assess privacy risks
        privacy_risks = await self._assess_privacy_risks(processing_activity)
        pia_result["privacy_risks"] = privacy_risks
        
        # Determine risk level
        risk_level = self._calculate_privacy_risk_level(privacy_risks)
        pia_result["risk_level"] = risk_level
        
        # Recommend mitigation measures
        mitigation_measures = await self._recommend_mitigation_measures(privacy_risks)
        pia_result["mitigation_measures"] = mitigation_measures
        
        # Final recommendation
        pia_result["recommendation"] = self._determine_pia_recommendation(risk_level)
        
        return pia_result
    
    async def _store_consent_record(self, consent_record: ConsentRecord) -> None:
        """Store consent record in database"""
        # Implement consent record storage
        pass
    
    async def _generate_consent_receipt(self, consent_record: ConsentRecord) -> None:
        """Generate consent receipt for user"""
        # Implement consent receipt generation
        pass
    
    async def _get_consent_record(self, consent_id: str) -> Optional[ConsentRecord]:
        """Retrieve consent record from database"""
        # Implement consent record retrieval
        return None
    
    async def _update_consent_record(self, consent_record: ConsentRecord) -> None:
        """Update consent record in database"""
        # Implement consent record update
        pass
    
    async def _process_consent_withdrawal(self, consent_record: ConsentRecord) -> None:
        """Process data according to consent withdrawal"""
        # Implement consent withdrawal processing
        pass
    
    async def _apply_anonymization_techniques(self, 
                                            record: Dict[str, Any],
                                            level: str) -> Dict[str, Any]:
        """Apply anonymization techniques to a record"""
        # Implement anonymization logic
        return record
    
    async def _assess_anonymization_quality(self, 
                                          original: List[Dict[str, Any]],
                                          anonymized: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess quality of anonymization"""
        # Implement quality assessment
        return {"information_loss": 0.2, "disclosure_risk": 0.1}
    
    def _select_pseudonymization_method(self, context: str) -> str:
        """Select appropriate pseudonymization method"""
        # Implement method selection logic
        return "deterministic_hash"
    
    async def _apply_pseudonymization(self, 
                                    identifier: str,
                                    method: str,
                                    context: str) -> str:
        """Apply pseudonymization to identifier"""
        # Implement pseudonymization logic
        import hashlib
        return hashlib.sha256(f"{identifier}_{context}".encode()).hexdigest()[:16]
    
    async def _log_pseudonymization(self, 
                                  original: str,
                                  pseudonym: str,
                                  method: str,
                                  context: str) -> None:
        """Log pseudonymization for audit"""
        # Implement pseudonymization logging
        pass
    
    async def _verify_user_identity(self, request: Dict[str, Any]) -> bool:
        """Verify user identity for data subject request"""
        # Implement identity verification
        return True
    
    async def _process_access_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process data access request"""
        # Implement access request processing
        return {"personal_data": {}, "consent_records": []}
    
    async def _process_erasure_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process data erasure request"""
        # Implement erasure request processing
        return {"deleted_records": 0, "retained_records": 0, "retention_reasons": []}
    
    async def _process_rectification_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process data rectification request"""
        # Implement rectification request processing
        return {"updated_fields": [], "verification_required": []}
    
    async def _process_portability_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process data portability request"""
        # Implement portability request processing
        return {"export_format": "json", "download_link": "", "expiry_date": ""}
    
    async def _assess_privacy_risks(self, activity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess privacy risks for processing activity"""
        # Implement privacy risk assessment
        return [
            {
                "risk_type": "data_breach",
                "probability": "medium",
                "impact": "high",
                "description": "Risk of unauthorized access to personal data"
            }
        ]
    
    def _calculate_privacy_risk_level(self, risks: List[Dict[str, Any]]) -> str:
        """Calculate overall privacy risk level"""
        # Implement risk level calculation
        return "medium"
    
    async def _recommend_mitigation_measures(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Recommend mitigation measures for privacy risks"""
        # Implement mitigation recommendations
        return [
            "Implement end-to-end encryption",
            "Regular security audits",
            "Access control measures"
        ]
    
    def _determine_pia_recommendation(self, risk_level: str) -> str:
        """Determine PIA recommendation based on risk level"""
        risk_recommendations = {
            "low": "proceed",
            "medium": "proceed_with_mitigation",
            "high": "additional_consultation_required",
            "critical": "do_not_proceed"
        }
        return risk_recommendations.get(risk_level, "proceed_with_caution")
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete privacy configuration"""
        return {
            "privacy_maturity_score": self.get_privacy_maturity_score(),
            "consent_management": self.consent_management.get_config(),
            "data_minimization": self.data_minimization.get_config(),
            "anonymization": self.anonymization_config.get_config(),
            "pseudonymization": self.pseudonymization_config.get_config(),
            "data_subject_rights": self.data_subject_rights.get_config(),
            "privacy_by_design": self.privacy_by_design.get_config(),
            "global_settings": {
                "privacy_first_approach": self.privacy_first_approach,
                "default_privacy_level": self.default_privacy_level,
                "privacy_impact_assessments": self.privacy_impact_assessments,
                "cross_border_data_transfers": self.cross_border_data_transfers
            },
            "data_protection": {
                "data_protection_officer": self.data_protection_officer,
                "regular_privacy_audits": self.regular_privacy_audits,
                "vendor_privacy_requirements": self.vendor_privacy_requirements,
                "employee_privacy_training": self.employee_privacy_training
            },
            "regulatory_compliance": {
                "supported_regulations": self.supported_regulations
            },
            "monitoring": {
                "privacy_metrics_tracking": self.privacy_metrics_tracking,
                "consent_rate_monitoring": self.consent_rate_monitoring,
                "privacy_incident_tracking": self.privacy_incident_tracking,
                "data_breach_notification": self.data_breach_notification
            }
        }

# Global privacy configuration instance
privacy_config = PrivacyConfiguration()

# Export main classes
__all__ = [
    "PrivacyConfiguration",
    "DataCategory",
    "ConsentType",
    "ProcessingPurpose",
    "PrivacyRight",
    "ConsentRecord",
    "ConsentManagementConfig",
    "DataMinimizationConfig",
    "AnonymizationConfig",
    "PseudonymizationConfig",
    "DataSubjectRightsConfig",
    "PrivacyByDesignConfig",
    "privacy_config"
]
