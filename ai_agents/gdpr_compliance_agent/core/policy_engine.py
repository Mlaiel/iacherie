"""
GDPR Policy Engine - Advanced Privacy Policy Management System
Dynamic policy generation, compliance checking, and automated updates

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from fastapi import HTTPException

try:
    from core.database import get_db
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db = DatabaseManager
from ...core.logging import get_logger
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...models.gdpr_models import PrivacyPolicy, PolicyTemplate, ComplianceRule

logger = get_logger(__name__)
settings = get_settings()

class PolicyType(Enum):
    """Types of privacy policies"""
    PRIVACY_POLICY = "privacy_policy"
    COOKIE_POLICY = "cookie_policy"
    DATA_RETENTION_POLICY = "data_retention_policy"
    CONSENT_POLICY = "consent_policy"
    BREACH_NOTIFICATION_POLICY = "breach_notification_policy"
    DATA_PROCESSING_POLICY = "data_processing_policy"

class PolicyStatus(Enum):
    """Policy lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ComplianceFramework(Enum):
    """Regulatory compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    PDPA = "pdpa"

class PolicyLanguage(Enum):
    """Supported policy languages"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"

@dataclass
class PolicyValidationResult:
    """Result of policy validation"""
    is_valid: bool
    compliance_score: float
    validation_errors: List[Dict[str, str]] = field(default_factory=list)
    missing_sections: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    regulatory_requirements_met: Dict[str, bool] = field(default_factory=dict)

@dataclass
class PolicyMetrics:
    """Policy management metrics"""
    total_policies: int
    active_policies: int
    outdated_policies: int
    compliance_rate: float
    policies_by_type: Dict[str, int]
    average_update_frequency_days: float
    last_compliance_check: str

class PolicyEngine:
    """
    Advanced GDPR Policy Engine
    Comprehensive privacy policy management with dynamic generation and compliance checking
    """
    
    def __init__(self):
        # Policy templates by type and framework
        self._policy_templates = self._initialize_policy_templates()
        self._compliance_rules = self._initialize_compliance_rules()
        self._required_sections = self._initialize_required_sections()
        
        # Language support
        self._supported_languages = [lang.value for lang in PolicyLanguage]
        self._policy_translations = self._initialize_translations()
        
        # Policy generation settings
        self._auto_update_enabled = True
        self._compliance_check_interval_days = 30
        self._policy_review_cycle_months = 12
        
        logger.info("GDPR Policy Engine initialized with multi-language support")
    
    def _initialize_policy_templates(self) -> Dict[str, Any]:
        """Initialize policy templates for different types and frameworks"""
        return {
            PolicyType.PRIVACY_POLICY.value: {
                ComplianceFramework.GDPR.value: {
                    "template_id": "gdpr_privacy_policy_v2024",
                    "sections": [
                        "introduction",
                        "data_controller_information",
                        "personal_data_collected",
                        "lawful_basis_for_processing",
                        "purposes_of_processing",
                        "data_retention_periods",
                        "data_subject_rights",
                        "data_sharing_and_transfers",
                        "security_measures",
                        "cookies_and_tracking",
                        "updates_to_policy",
                        "contact_information"
                    ],
                    "mandatory_elements": [
                        "controller_identity",
                        "data_categories",
                        "processing_purposes",
                        "legal_basis",
                        "retention_periods",
                        "subject_rights",
                        "dpo_contact"
                    ]
                }
            },
            PolicyType.COOKIE_POLICY.value: {
                ComplianceFramework.GDPR.value: {
                    "template_id": "gdpr_cookie_policy_v2024",
                    "sections": [
                        "what_are_cookies",
                        "types_of_cookies_used",
                        "purposes_of_cookies",
                        "cookie_categories",
                        "consent_management",
                        "third_party_cookies",
                        "cookie_settings",
                        "policy_updates"
                    ],
                    "cookie_categories": [
                        "strictly_necessary",
                        "performance",
                        "functional",
                        "targeting"
                    ]
                }
            },
            PolicyType.DATA_RETENTION_POLICY.value: {
                ComplianceFramework.GDPR.value: {
                    "template_id": "gdpr_retention_policy_v2024",
                    "sections": [
                        "retention_principles",
                        "data_categories_and_periods",
                        "retention_criteria",
                        "deletion_procedures",
                        "legal_holds",
                        "regular_review_process"
                    ],
                    "default_periods": {
                        "identity_data": "7_years",
                        "financial_data": "10_years",
                        "marketing_data": "3_years",
                        "analytics_data": "26_months",
                        "consent_records": "3_years"
                    }
                }
            }
        }
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance validation rules"""
        return {
            ComplianceFramework.GDPR.value: {
                "article_6_legal_basis": {
                    "required": True,
                    "valid_bases": [
                        "consent",
                        "contract",
                        "legal_obligation",
                        "vital_interests",
                        "public_task",
                        "legitimate_interests"
                    ]
                },
                "article_13_information": {
                    "required_elements": [
                        "controller_identity",
                        "processing_purposes",
                        "legal_basis",
                        "data_categories",
                        "retention_periods",
                        "subject_rights"
                    ]
                },
                "article_25_data_protection_by_design": {
                    "privacy_measures": [
                        "data_minimization",
                        "purpose_limitation",
                        "storage_limitation",
                        "accuracy",
                        "integrity_confidentiality"
                    ]
                },
                "article_30_processing_records": {
                    "required_information": [
                        "processing_purposes",
                        "data_categories",
                        "data_subjects_categories",
                        "recipients",
                        "third_country_transfers",
                        "retention_periods",
                        "security_measures"
                    ]
                }
            }
        }
    
    def _initialize_required_sections(self) -> Dict[str, List[str]]:
        """Initialize required policy sections by type"""
        return {
            PolicyType.PRIVACY_POLICY.value: [
                "data_controller_information",
                "personal_data_collected",
                "lawful_basis_for_processing",
                "data_subject_rights",
                "contact_information"
            ],
            PolicyType.COOKIE_POLICY.value: [
                "types_of_cookies_used",
                "purposes_of_cookies",
                "consent_management"
            ],
            PolicyType.DATA_RETENTION_POLICY.value: [
                "retention_principles",
                "data_categories_and_periods",
                "deletion_procedures"
            ]
        }
    
    def _initialize_translations(self) -> Dict[str, Dict[str, str]]:
        """Initialize policy section translations"""
        return {
            "section_titles": {
                "en": {
                    "introduction": "Introduction",
                    "data_controller_information": "Data Controller Information",
                    "personal_data_collected": "Personal Data We Collect",
                    "lawful_basis_for_processing": "Lawful Basis for Processing",
                    "data_subject_rights": "Your Rights",
                    "contact_information": "Contact Information"
                },
                "de": {
                    "introduction": "Einführung",
                    "data_controller_information": "Informationen zum Datenverarbeiter",
                    "personal_data_collected": "Von uns erhobene personenbezogene Daten",
                    "lawful_basis_for_processing": "Rechtsgrundlage für die Verarbeitung",
                    "data_subject_rights": "Ihre Rechte",
                    "contact_information": "Kontaktinformationen"
                },
                "fr": {
                    "introduction": "Introduction",
                    "data_controller_information": "Informations sur le Responsable du Traitement",
                    "personal_data_collected": "Données Personnelles que Nous Collectons",
                    "lawful_basis_for_processing": "Base Légale du Traitement",
                    "data_subject_rights": "Vos Droits",
                    "contact_information": "Informations de Contact"
                }
            }
        }
    
    async def generate_privacy_policy(
        self, 
        policy_config: Dict[str, Any],
        policy_type: PolicyType = PolicyType.PRIVACY_POLICY,
        compliance_framework: ComplianceFramework = ComplianceFramework.GDPR,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate comprehensive privacy policy based on configuration"""
        try:
            policy_id = str(uuid.uuid4())
            
            # Get appropriate template
            template = await self._get_policy_template(policy_type, compliance_framework)
            
            # Generate policy content
            policy_content = await self._generate_policy_content(
                template, policy_config, language
            )
            
            # Validate generated policy
            validation_result = await self._validate_policy_compliance(
                policy_content, policy_type, compliance_framework
            )
            
            # Create policy record
            privacy_policy = PrivacyPolicy(
                policy_id=policy_id,
                policy_type=policy_type.value,
                compliance_framework=compliance_framework.value,
                language=language,
                title=policy_content["title"],
                content=policy_content["sections"],
                version="1.0",
                status=PolicyStatus.DRAFT.value,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                effective_date=datetime.utcnow() + timedelta(days=30),  # 30 days notice
                review_date=datetime.utcnow() + timedelta(days=365),
                validation_result=validation_result.__dict__,
                policy_config=policy_config
            )
            
            async with get_db() as db:
                db.add(privacy_policy)
                await db.commit()
                await db.refresh(privacy_policy)
            
            logger.info(f"Privacy policy generated: {policy_type.value} - {language}")
            
            return {
                "policy_id": policy_id,
                "policy_type": policy_type.value,
                "compliance_framework": compliance_framework.value,
                "language": language,
                "title": policy_content["title"],
                "sections": list(policy_content["sections"].keys()),
                "version": "1.0",
                "status": PolicyStatus.DRAFT.value,
                "validation_result": {
                    "is_valid": validation_result.is_valid,
                    "compliance_score": validation_result.compliance_score,
                    "validation_errors": validation_result.validation_errors,
                    "recommendations": validation_result.recommendations
                },
                "effective_date": privacy_policy.effective_date.isoformat(),
                "estimated_reading_time_minutes": await self._estimate_reading_time(policy_content)
            }
            
        except Exception as e:
            logger.error(f"Error generating privacy policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy generation failed: {str(e)}")
    
    async def update_policy(
        self, 
        policy_id: str,
        updates: Dict[str, Any],
        reason: str = "Regular update"
    ) -> Dict[str, Any]:
        """Update existing privacy policy with change tracking"""
        try:
            async with get_db() as db:
                # Get existing policy
                policy_query = await db.execute(
                    select(PrivacyPolicy).where(PrivacyPolicy.policy_id == policy_id)
                )
                policy = policy_query.scalar_one_or_none()
                
                if not policy:
                    raise HTTPException(status_code=404, detail="Policy not found")
                
                # Create new version
                old_version = policy.version
                new_version = await self._increment_version(old_version)
                
                # Apply updates
                updated_content = await self._apply_policy_updates(
                    policy.content, updates
                )
                
                # Validate updated policy
                validation_result = await self._validate_policy_compliance(
                    {"sections": updated_content}, 
                    PolicyType(policy.policy_type), 
                    ComplianceFramework(policy.compliance_framework)
                )
                
                # Update policy record
                policy.content = updated_content
                policy.version = new_version
                policy.last_updated = datetime.utcnow()
                policy.status = PolicyStatus.UNDER_REVIEW.value
                policy.validation_result = validation_result.__dict__
                policy.update_reason = reason
                
                # Track changes
                if not policy.change_history:
                    policy.change_history = []
                
                policy.change_history.append({
                    "version": new_version,
                    "updated_at": datetime.utcnow().isoformat(),
                    "reason": reason,
                    "changes": updates,
                    "updated_sections": list(updates.keys()) if isinstance(updates, dict) else ["content"]
                })
                
                await db.commit()
                await db.refresh(policy)
            
            logger.info(f"Policy updated: {policy_id} - Version {new_version}")
            
            return {
                "policy_id": policy_id,
                "old_version": old_version,
                "new_version": new_version,
                "update_reason": reason,
                "updated_sections": list(updates.keys()) if isinstance(updates, dict) else ["content"],
                "validation_result": {
                    "is_valid": validation_result.is_valid,
                    "compliance_score": validation_result.compliance_score
                },
                "status": PolicyStatus.UNDER_REVIEW.value,
                "requires_approval": True,
                "notification_required": await self._requires_user_notification(updates)
            }
            
        except Exception as e:
            logger.error(f"Error updating policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy update failed: {str(e)}")
    
    async def validate_policy_compliance(
        self, 
        policy_id: str,
        compliance_framework: ComplianceFramework = ComplianceFramework.GDPR
    ) -> PolicyValidationResult:
        """Validate policy compliance against regulatory requirements"""
        try:
            async with get_db() as db:
                policy_query = await db.execute(
                    select(PrivacyPolicy).where(PrivacyPolicy.policy_id == policy_id)
                )
                policy = policy_query.scalar_one_or_none()
                
                if not policy:
                    raise HTTPException(status_code=404, detail="Policy not found")
                
                # Perform comprehensive compliance validation
                validation_result = await self._validate_policy_compliance(
                    {"sections": policy.content},
                    PolicyType(policy.policy_type),
                    compliance_framework
                )
                
                # Update validation result in database
                policy.validation_result = validation_result.__dict__
                policy.last_validation_date = datetime.utcnow()
                await db.commit()
                
                logger.info(f"Policy validated: {policy_id} - Score: {validation_result.compliance_score}")
                
                return validation_result
                
        except Exception as e:
            logger.error(f"Error validating policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy validation failed: {str(e)}")
    
    async def check_policy_updates_needed(
        self, 
        data_processing_changes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Check if policy updates are needed based on processing changes"""
        try:
            async with get_db() as db:
                # Get all active policies
                policies_query = await db.execute(
                    select(PrivacyPolicy).where(
                        PrivacyPolicy.status == PolicyStatus.ACTIVE.value
                    )
                )
                policies = policies_query.scalars().all()
                
                update_recommendations = []
                
                for policy in policies:
                    # Check if policy is outdated
                    if await self._is_policy_outdated(policy):
                        update_recommendations.append({
                            "policy_id": policy.policy_id,
                            "policy_type": policy.policy_type,
                            "reason": "Policy is outdated and requires review",
                            "priority": "high",
                            "recommended_updates": await self._get_update_recommendations(policy)
                        })
                    
                    # Check against processing changes
                    if data_processing_changes and await self._policy_affected_by_changes(policy, data_processing_changes):
                        update_recommendations.append({
                            "policy_id": policy.policy_id,
                            "policy_type": policy.policy_type,
                            "reason": "Data processing activities have changed",
                            "priority": "medium",
                            "affected_sections": await self._identify_affected_sections(policy, data_processing_changes)
                        })
                
                return {
                    "total_policies_checked": len(policies),
                    "updates_needed": len(update_recommendations),
                    "update_recommendations": update_recommendations,
                    "check_timestamp": datetime.utcnow().isoformat(),
                    "next_check_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error checking policy updates: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy update check failed: {str(e)}")
    
    async def generate_multilingual_policies(
        self, 
        policy_config: Dict[str, Any],
        languages: List[str] = None
    ) -> Dict[str, Any]:
        """Generate privacy policies in multiple languages"""
        try:
            if languages is None:
                languages = ["en", "de", "fr"]  # Default languages
            
            generated_policies = {}
            
            for language in languages:
                if language not in self._supported_languages:
                    logger.warning(f"Unsupported language: {language}")
                    continue
                
                policy_result = await self.generate_privacy_policy(
                    policy_config=policy_config,
                    language=language
                )
                
                generated_policies[language] = policy_result
            
            # Create policy group for related policies
            group_id = str(uuid.uuid4())
            
            logger.info(f"Multilingual policies generated: {len(generated_policies)} languages")
            
            return {
                "policy_group_id": group_id,
                "languages": list(generated_policies.keys()),
                "policies": generated_policies,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "synchronization_required": True
            }
            
        except Exception as e:
            logger.error(f"Error generating multilingual policies: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Multilingual generation failed: {str(e)}")
    
    async def get_policy_metrics(self) -> PolicyMetrics:
        """Get comprehensive policy management metrics"""
        try:
            async with get_db() as db:
                # Get all policies
                policies_query = await db.execute(select(PrivacyPolicy))
                policies = policies_query.scalars().all()
                
                if not policies:
                    return PolicyMetrics(0, 0, 0, 0.0, {}, 0.0, "never")
                
                total_policies = len(policies)
                active_policies = len([p for p in policies if p.status == PolicyStatus.ACTIVE.value])
                
                # Check for outdated policies
                outdated_policies = 0
                for policy in policies:
                    if await self._is_policy_outdated(policy):
                        outdated_policies += 1
                
                # Calculate compliance rate
                valid_policies = len([p for p in policies if p.validation_result and p.validation_result.get("is_valid")])
                compliance_rate = valid_policies / total_policies if total_policies > 0 else 0.0
                
                # Policies by type
                policies_by_type = {}
                for policy in policies:
                    policy_type = policy.policy_type
                    policies_by_type[policy_type] = policies_by_type.get(policy_type, 0) + 1
                
                # Calculate average update frequency
                update_frequencies = []
                for policy in policies:
                    if policy.change_history:
                        updates_count = len(policy.change_history)
                        days_since_creation = (datetime.utcnow() - policy.created_at).days
                        if days_since_creation > 0:
                            update_frequency = days_since_creation / max(updates_count, 1)
                            update_frequencies.append(update_frequency)
                
                avg_update_frequency = sum(update_frequencies) / len(update_frequencies) if update_frequencies else 0.0
                
                # Last compliance check
                last_checks = [p.last_validation_date for p in policies if p.last_validation_date]
                last_compliance_check = max(last_checks).isoformat() if last_checks else "never"
                
                return PolicyMetrics(
                    total_policies=total_policies,
                    active_policies=active_policies,
                    outdated_policies=outdated_policies,
                    compliance_rate=round(compliance_rate, 3),
                    policies_by_type=policies_by_type,
                    average_update_frequency_days=round(avg_update_frequency, 1),
                    last_compliance_check=last_compliance_check
                )
                
        except Exception as e:
            logger.error(f"Error getting policy metrics: {str(e)}")
            return PolicyMetrics(0, 0, 0, 0.0, {}, 0.0, "error")
    
    # Helper methods for policy generation and management
    
    async def _get_policy_template(
        self, 
        policy_type: PolicyType,
        compliance_framework: ComplianceFramework
    ) -> Dict[str, Any]:
        """Get appropriate policy template"""
        templates = self._policy_templates.get(policy_type.value, {})
        template = templates.get(compliance_framework.value)
        
        if not template:
            # Fallback to GDPR template
            template = templates.get(ComplianceFramework.GDPR.value, {})
        
        if not template:
            raise ValueError(f"No template found for {policy_type.value}")
        
        return template
    
    async def _generate_policy_content(
        self, 
        template: Dict[str, Any],
        config: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Generate policy content from template and configuration"""
        sections = {}
        
        # Generate title
        company_name = config.get("company_name", "Ultra-Industrial AI Solutions")
        policy_title = f"{company_name} - Privacy Policy"
        
        if language == "de":
            policy_title = f"{company_name} - Datenschutzerklärung"
        elif language == "fr":
            policy_title = f"{company_name} - Politique de Confidentialité"
        
        # Generate each section
        for section_key in template.get("sections", []):
            section_content = await self._generate_section_content(
                section_key, config, language
            )
            sections[section_key] = section_content
        
        return {
            "title": policy_title,
            "sections": sections,
            "generated_at": datetime.utcnow().isoformat(),
            "language": language
        }
    
    async def _generate_section_content(
        self, 
        section_key: str,
        config: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Generate content for specific policy section"""
        section_templates = {
            "introduction": {
                "en": f"This privacy policy explains how {config.get('company_name', 'we')} collect, use, and protect your personal data in accordance with the General Data Protection Regulation (GDPR).",
                "de": f"Diese Datenschutzerklärung erklärt, wie {config.get('company_name', 'wir')} Ihre personenbezogenen Daten gemäß der Datenschutz-Grundverordnung (DSGVO) erheben, verwenden und schützen.",
                "fr": f"Cette politique de confidentialité explique comment {config.get('company_name', 'nous')} collectons, utilisons et protégeons vos données personnelles conformément au Règlement Général sur la Protection des Données (RGPD)."
            },
            "data_controller_information": {
                "en": f"Data Controller: {config.get('company_name', 'Ultra-Industrial AI Solutions')}\nAddress: {config.get('address', 'Address not specified')}\nEmail: {config.get('contact_email', 'privacy@company.com')}\nData Protection Officer: {config.get('dpo_email', 'dpo@company.com')}",
                "de": f"Verantwortlicher: {config.get('company_name', 'Ultra-Industrial AI Solutions')}\nAdresse: {config.get('address', 'Adresse nicht angegeben')}\nE-Mail: {config.get('contact_email', 'privacy@company.com')}\nDatenschutzbeauftragter: {config.get('dpo_email', 'dpo@company.com')}",
                "fr": f"Responsable du traitement: {config.get('company_name', 'Ultra-Industrial AI Solutions')}\nAdresse: {config.get('address', 'Adresse non spécifiée')}\nE-mail: {config.get('contact_email', 'privacy@company.com')}\nDélégué à la Protection des Données: {config.get('dpo_email', 'dpo@company.com')}"
            }
        }
        
        template_text = section_templates.get(section_key, {}).get(language, f"Section content for {section_key}")
        
        return {
            "title": await self._get_section_title(section_key, language),
            "content": template_text,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_section_title(self, section_key: str, language: str) -> str:
        """Get localized section title"""
        translations = self._policy_translations.get("section_titles", {})
        language_translations = translations.get(language, {})
        return language_translations.get(section_key, section_key.replace("_", " ").title())
    
    async def _validate_policy_compliance(
        self, 
        policy_content: Dict[str, Any],
        policy_type: PolicyType,
        compliance_framework: ComplianceFramework
    ) -> PolicyValidationResult:
        """Validate policy compliance against regulatory requirements"""
        validation_errors = []
        missing_sections = []
        recommendations = []
        regulatory_requirements_met = {}
        
        sections = policy_content.get("sections", {})
        required_sections = self._required_sections.get(policy_type.value, [])
        
        # Check required sections
        for required_section in required_sections:
            if required_section not in sections:
                missing_sections.append(required_section)
                validation_errors.append({
                    "type": "missing_section",
                    "section": required_section,
                    "severity": "high",
                    "message": f"Required section '{required_section}' is missing"
                })
        
        # Check compliance rules
        if compliance_framework == ComplianceFramework.GDPR:
            gdpr_rules = self._compliance_rules.get("gdpr", {})
            
            # Check Article 13 information requirements
            article_13_elements = gdpr_rules.get("article_13_information", {}).get("required_elements", [])
            for element in article_13_elements:
                if not await self._check_element_presence(sections, element):
                    regulatory_requirements_met[f"article_13_{element}"] = False
                    recommendations.append(f"Include information about {element} (GDPR Article 13)")
                else:
                    regulatory_requirements_met[f"article_13_{element}"] = True
        
        # Calculate compliance score
        total_checks = len(required_sections) + len(regulatory_requirements_met)
        passed_checks = (len(required_sections) - len(missing_sections)) + sum(regulatory_requirements_met.values())
        compliance_score = (passed_checks / total_checks) if total_checks > 0 else 0.0
        
        # Generate recommendations
        if compliance_score < 0.8:
            recommendations.append("Policy needs significant improvements to meet compliance requirements")
        elif compliance_score < 0.9:
            recommendations.append("Policy is mostly compliant but could be improved")
        
        return PolicyValidationResult(
            is_valid=compliance_score >= 0.8 and len(validation_errors) == 0,
            compliance_score=round(compliance_score, 3),
            validation_errors=validation_errors,
            missing_sections=missing_sections,
            recommendations=recommendations,
            regulatory_requirements_met=regulatory_requirements_met
        )
    
    async def _check_element_presence(self, sections: Dict[str, Any], element: str) -> bool:
        """Check if required element is present in policy sections"""
        element_keywords = {
            "controller_identity": ["controller", "company", "organization"],
            "processing_purposes": ["purpose", "use", "process"],
            "legal_basis": ["legal basis", "lawful", "grounds"],
            "data_categories": ["personal data", "information", "data types"],
            "retention_periods": ["retention", "keep", "storage period"],
            "subject_rights": ["rights", "access", "rectification", "erasure"]
        }
        
        keywords = element_keywords.get(element, [element])
        
        # Search for keywords in section content
        for section in sections.values():
            if isinstance(section, dict):
                content = section.get("content", "").lower()
                if any(keyword in content for keyword in keywords):
                    return True
        
        return False
    
    async def _increment_version(self, current_version: str) -> str:
        """Increment policy version number"""
        try:
            parts = current_version.split(".")
            major, minor = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            return f"{major}.{minor + 1}"
        except (ValueError, IndexError):
            return "1.1"
    
    async def _apply_policy_updates(
        self, 
        current_content: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply updates to policy content"""
        updated_content = current_content.copy()
        
        for section_key, update_value in updates.items():
            if section_key in updated_content:
                if isinstance(updated_content[section_key], dict) and isinstance(update_value, dict):
                    updated_content[section_key].update(update_value)
                else:
                    updated_content[section_key] = update_value
            else:
                updated_content[section_key] = update_value
        
        return updated_content
    
    async def _requires_user_notification(self, updates: Dict[str, Any]) -> bool:
        """Determine if policy updates require user notification"""
        significant_changes = [
            "data_collection_changes",
            "new_processing_purposes",
            "third_party_sharing",
            "retention_period_changes"
        ]
        
        return any(change in updates for change in significant_changes)
    
    async def _is_policy_outdated(self, policy: PrivacyPolicy) -> bool:
        """Check if policy is outdated and needs review"""
        if policy.review_date and datetime.utcnow() > policy.review_date:
            return True
        
        if policy.last_updated:
            days_since_update = (datetime.utcnow() - policy.last_updated).days
            if days_since_update > 365:  # More than a year old
                return True
        
        return False
    
    async def _get_update_recommendations(self, policy: PrivacyPolicy) -> List[str]:
        """Get update recommendations for outdated policy"""
        recommendations = []
        
        if policy.review_date and datetime.utcnow() > policy.review_date:
            recommendations.append("Conduct scheduled policy review")
        
        if policy.validation_result:
            score = policy.validation_result.get("compliance_score", 0)
            if score < 0.8:
                recommendations.append("Improve policy compliance")
        
        recommendations.extend([
            "Update contact information",
            "Review data processing activities",
            "Check regulatory changes",
            "Validate technical security measures"
        ])
        
        return recommendations
    
    async def _policy_affected_by_changes(
        self, 
        policy: PrivacyPolicy, 
        changes: Dict[str, Any]
    ) -> bool:
        """Check if policy is affected by processing changes"""
        # Simplified check - in production would be more sophisticated
        affected_areas = [
            "new_data_types",
            "new_processing_purposes",
            "third_party_changes",
            "retention_changes"
        ]
        
        return any(area in changes for area in affected_areas)
    
    async def _identify_affected_sections(
        self, 
        policy: PrivacyPolicy, 
        changes: Dict[str, Any]
    ) -> List[str]:
        """Identify policy sections affected by changes"""
        affected_sections = []
        
        if "new_data_types" in changes:
            affected_sections.append("personal_data_collected")
        
        if "new_processing_purposes" in changes:
            affected_sections.extend(["purposes_of_processing", "lawful_basis_for_processing"])
        
        if "third_party_changes" in changes:
            affected_sections.append("data_sharing_and_transfers")
        
        if "retention_changes" in changes:
            affected_sections.append("data_retention_periods")
        
        return list(set(affected_sections))
    
    async def _estimate_reading_time(self, policy_content: Dict[str, Any]) -> int:
        """Estimate reading time for policy in minutes"""
        total_words = 0
        sections = policy_content.get("sections", {})
        
        for section in sections.values():
            if isinstance(section, dict):
                content = section.get("content", "")
                word_count = len(content.split())
                total_words += word_count
        
        # Average reading speed: 200-250 words per minute
        reading_time = max(1, total_words // 225)  # Round up, minimum 1 minute
        return reading_time

    async def approve_policy(self, policy_id: str, approver_id: str) -> Dict[str, Any]:
        """Approve a policy and make it active"""
        try:
            async with get_db() as db:
                policy_query = await db.execute(
                    select(PrivacyPolicy).where(PrivacyPolicy.policy_id == policy_id)
                )
                policy = policy_query.scalar_one_or_none()
                
                if not policy:
                    raise HTTPException(status_code=404, detail="Policy not found")
                
                if policy.status != PolicyStatus.UNDER_REVIEW.value:
                    raise HTTPException(status_code=400, detail="Policy is not under review")
                
                # Validate before approval
                validation_result = await self._validate_policy_compliance(
                    {"sections": policy.content},
                    PolicyType(policy.policy_type),
                    ComplianceFramework(policy.compliance_framework)
                )
                
                if not validation_result.is_valid:
                    raise HTTPException(status_code=400, detail="Policy does not meet compliance requirements")
                
                # Approve policy
                policy.status = PolicyStatus.APPROVED.value
                policy.approved_at = datetime.utcnow()
                policy.approved_by = approver_id
                
                # Set as active after effective date
                if policy.effective_date <= datetime.utcnow():
                    policy.status = PolicyStatus.ACTIVE.value
                
                await db.commit()
                
                logger.info(f"Policy approved: {policy_id} by {approver_id}")
                
                return {
                    "policy_id": policy_id,
                    "status": policy.status,
                    "approved_at": policy.approved_at.isoformat(),
                    "approved_by": approver_id,
                    "effective_date": policy.effective_date.isoformat(),
                    "compliance_score": validation_result.compliance_score
                }
                
        except Exception as e:
            logger.error(f"Error approving policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy approval failed: {str(e)}")
    
    async def get_policy_by_id(self, policy_id: str) -> Dict[str, Any]:
        """Get policy details by ID"""
        try:
            async with get_db() as db:
                policy_query = await db.execute(
                    select(PrivacyPolicy).where(PrivacyPolicy.policy_id == policy_id)
                )
                policy = policy_query.scalar_one_or_none()
                
                if not policy:
                    raise HTTPException(status_code=404, detail="Policy not found")
                
                return {
                    "policy_id": policy.policy_id,
                    "policy_type": policy.policy_type,
                    "compliance_framework": policy.compliance_framework,
                    "language": policy.language,
                    "title": policy.title,
                    "content": policy.content,
                    "version": policy.version,
                    "status": policy.status,
                    "created_at": policy.created_at.isoformat(),
                    "last_updated": policy.last_updated.isoformat(),
                    "effective_date": policy.effective_date.isoformat(),
                    "review_date": policy.review_date.isoformat() if policy.review_date else None,
                    "validation_result": policy.validation_result,
                    "change_history": policy.change_history or []
                }
                
        except Exception as e:
            logger.error(f"Error getting policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Policy retrieval failed: {str(e)}")
