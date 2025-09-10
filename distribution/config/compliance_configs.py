"""
Platform Compliance Configurations
=================================

Platform compliance and regulatory settings for Ainflue Distribution Platform.
Handles content policies, data privacy, and regulatory compliance across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import os
import json

class ComplianceFramework(Enum):
    """Regulatory compliance frameworks"""
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    SOX = "sox"  # Sarbanes-Oxley Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard

class ContentCategory(Enum):
    """Content categories for compliance checking"""
    GENERAL = "general"
    ADULT = "adult"
    CHILDREN = "children"
    HEALTH = "health"
    FINANCIAL = "financial"
    POLITICAL = "political"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceAction(Enum):
    """Actions to take for compliance violations"""
    WARN = "warn"
    BLOCK = "block"
    REVIEW = "review"
    MODIFY = "modify"
    ESCALATE = "escalate"
    LOG_ONLY = "log_only"

@dataclass
class PlatformPolicy:
    """Platform-specific content policy"""
    platform: str
    policy_name: str
    description: str
    content_categories: List[ContentCategory] = field(default_factory=list)
    prohibited_content: List[str] = field(default_factory=list)
    required_disclosures: List[str] = field(default_factory=list)
    age_restrictions: Dict[str, int] = field(default_factory=dict)
    geographic_restrictions: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
@dataclass
class ComplianceRule:
    """Individual compliance rule"""
    rule_id: str
    name: str
    framework: ComplianceFramework
    description: str
    risk_level: RiskLevel
    applicable_platforms: List[str] = field(default_factory=list)
    content_categories: List[ContentCategory] = field(default_factory=list)
    validation_logic: str = ""  # Could be regex, keywords, or function name
    action_on_violation: ComplianceAction = ComplianceAction.WARN
    remediation_steps: List[str] = field(default_factory=list)
    enabled: bool = True
    
@dataclass
class DataHandlingRule:
    """Data handling and privacy rule"""
    rule_id: str
    framework: ComplianceFramework
    data_type: str  # personal, sensitive, financial, health, etc.
    collection_allowed: bool = True
    processing_allowed: bool = True
    storage_duration_days: Optional[int] = None
    encryption_required: bool = False
    consent_required: bool = False
    deletion_on_request: bool = False
    cross_border_transfer_allowed: bool = True
    audit_logging_required: bool = False
    
@dataclass
class AgeVerificationConfig:
    """Age verification requirements"""
    platform: str
    minimum_age: int = 13
    verification_method: str = "self_declaration"  # self_declaration, document_verification, credit_card
    parental_consent_required: bool = False
    restricted_features: List[str] = field(default_factory=list)
    grace_period_days: int = 7
    
@dataclass
class ConsentManagement:
    """User consent management configuration"""
    framework: ComplianceFramework
    consent_types: List[str] = field(default_factory=lambda: ["data_processing", "marketing", "analytics"])
    opt_in_required: bool = True
    withdrawal_method: str = "self_service"  # self_service, contact_support
    consent_duration_days: Optional[int] = None
    renewal_required: bool = False
    granular_consent: bool = True

class ComplianceConfigs:
    """
    Platform compliance configuration manager
    
    Features:
    - Multi-framework compliance (GDPR, CCPA, etc.)
    - Platform-specific policies
    - Content category management
    - Age verification rules
    - Data handling policies
    - Consent management
    - Automated compliance checking
    """
    
    def __init__(self):
        self.platform_policies: Dict[str, List[PlatformPolicy]] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.data_handling_rules: Dict[str, DataHandlingRule] = {}
        self.age_verification_configs: Dict[str, AgeVerificationConfig] = {}
        self.consent_management: Dict[ComplianceFramework, ConsentManagement] = {}
        self.global_settings = self._get_default_global_settings()
        self._load_default_configurations()
        
    def _get_default_global_settings(self) -> Dict[str, Any]:
        """Get default global compliance settings"""
        return {
            "compliance_checking_enabled": True,
            "auto_block_violations": False,
            "audit_logging_enabled": True,
            "data_retention_default_days": 365,
            "consent_renewal_days": 365,
            "privacy_by_design": True,
            "data_minimization": True,
            "anonymization_enabled": True,
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "backup_encryption": True,
            "incident_reporting_enabled": True,
            "breach_notification_hours": 72,
            "dpo_contact": "dpo@ainflue.com",
            "legal_contact": "legal@ainflue.com"
        }
        
    def _load_default_configurations(self):
        """Load default compliance configurations"""
        
        # Platform policies
        self.platform_policies.update({
            "instagram": [
                PlatformPolicy(
                    platform="instagram",
                    policy_name="Community Guidelines",
                    description="Instagram community guidelines compliance",
                    prohibited_content=[
                        "nudity", "hate_speech", "harassment", "violence", 
                        "misinformation", "spam", "fake_accounts"
                    ],
                    required_disclosures=["sponsored_content", "partnerships"],
                    age_restrictions={"minimum_age": 13},
                    last_updated=datetime(2024, 1, 1)
                ),
                PlatformPolicy(
                    platform="instagram",
                    policy_name="Commerce Policy",
                    description="Instagram commerce and advertising policies",
                    content_categories=[ContentCategory.COMMERCIAL],
                    prohibited_content=[
                        "illegal_products", "weapons", "adult_products", 
                        "tobacco", "prescription_drugs"
                    ],
                    required_disclosures=["ad_disclosure", "price_accuracy"],
                    last_updated=datetime(2024, 1, 1)
                )
            ],
            "youtube": [
                PlatformPolicy(
                    platform="youtube",
                    policy_name="Community Guidelines",
                    description="YouTube community guidelines",
                    prohibited_content=[
                        "hate_speech", "harassment", "harmful_content", 
                        "misinformation", "spam", "copyrighted_content"
                    ],
                    required_disclosures=["paid_promotion"],
                    age_restrictions={"minimum_age": 13, "mature_content": 18},
                    last_updated=datetime(2024, 1, 1)
                ),
                PlatformPolicy(
                    platform="youtube",
                    policy_name="Monetization Policies",
                    description="YouTube Partner Program policies",
                    content_categories=[ContentCategory.COMMERCIAL],
                    prohibited_content=[
                        "clickbait", "misleading_content", "repetitious_content"
                    ],
                    required_disclosures=["sponsorship", "affiliate_links"],
                    last_updated=datetime(2024, 1, 1)
                )
            ],
            "tiktok": [
                PlatformPolicy(
                    platform="tiktok",
                    policy_name="Community Guidelines",
                    description="TikTok community guidelines",
                    prohibited_content=[
                        "adult_content", "violence", "harassment", "hate_speech",
                        "dangerous_acts", "illegal_activities", "misinformation"
                    ],
                    required_disclosures=["branded_content"],
                    age_restrictions={"minimum_age": 13, "live_streaming": 16},
                    geographic_restrictions=["CN", "IN"],  # Example restrictions
                    last_updated=datetime(2024, 1, 1)
                )
            ]
        })
        
        # GDPR compliance rules
        self.compliance_rules.update({
            "gdpr_data_consent": ComplianceRule(
                rule_id="gdpr_data_consent",
                name="GDPR Data Processing Consent",
                framework=ComplianceFramework.GDPR,
                description="Explicit consent required for personal data processing",
                risk_level=RiskLevel.HIGH,
                applicable_platforms=["all"],
                validation_logic="check_explicit_consent",
                action_on_violation=ComplianceAction.BLOCK,
                remediation_steps=[
                    "Obtain explicit user consent",
                    "Provide clear privacy notice",
                    "Enable consent withdrawal"
                ]
            ),
            "gdpr_data_minimization": ComplianceRule(
                rule_id="gdpr_data_minimization",
                name="GDPR Data Minimization",
                framework=ComplianceFramework.GDPR,
                description="Collect only necessary personal data",
                risk_level=RiskLevel.MEDIUM,
                applicable_platforms=["all"],
                validation_logic="check_data_necessity",
                action_on_violation=ComplianceAction.REVIEW,
                remediation_steps=[
                    "Review data collection necessity",
                    "Remove unnecessary data fields",
                    "Update privacy policy"
                ]
            ),
            "gdpr_right_to_erasure": ComplianceRule(
                rule_id="gdpr_right_to_erasure",
                name="GDPR Right to be Forgotten",
                framework=ComplianceFramework.GDPR,
                description="Users can request data deletion",
                risk_level=RiskLevel.HIGH,
                applicable_platforms=["all"],
                validation_logic="check_deletion_capability",
                action_on_violation=ComplianceAction.ESCALATE,
                remediation_steps=[
                    "Implement data deletion process",
                    "Verify complete data removal",
                    "Notify third parties if applicable"
                ]
            )
        })
        
        # CCPA compliance rules
        self.compliance_rules.update({
            "ccpa_opt_out": ComplianceRule(
                rule_id="ccpa_opt_out",
                name="CCPA Sale Opt-Out",
                framework=ComplianceFramework.CCPA,
                description="Right to opt out of personal information sale",
                risk_level=RiskLevel.HIGH,
                applicable_platforms=["all"],
                validation_logic="check_opt_out_mechanism",
                action_on_violation=ComplianceAction.BLOCK,
                remediation_steps=[
                    "Implement opt-out mechanism",
                    "Honor opt-out requests within 15 days",
                    "Update privacy policy"
                ]
            ),
            "ccpa_disclosure": ComplianceRule(
                rule_id="ccpa_disclosure",
                name="CCPA Information Disclosure",
                framework=ComplianceFramework.CCPA,
                description="Disclose personal information categories and purposes",
                risk_level=RiskLevel.MEDIUM,
                applicable_platforms=["all"],
                validation_logic="check_disclosure_completeness",
                action_on_violation=ComplianceAction.WARN,
                remediation_steps=[
                    "Update privacy policy with disclosures",
                    "Provide consumer request portal",
                    "Maintain disclosure records"
                ]
            )
        })
        
        # COPPA compliance rules
        self.compliance_rules.update({
            "coppa_parental_consent": ComplianceRule(
                rule_id="coppa_parental_consent",
                name="COPPA Parental Consent",
                framework=ComplianceFramework.COPPA,
                description="Parental consent required for children under 13",
                risk_level=RiskLevel.CRITICAL,
                applicable_platforms=["all"],
                content_categories=[ContentCategory.CHILDREN],
                validation_logic="check_parental_consent",
                action_on_violation=ComplianceAction.BLOCK,
                remediation_steps=[
                    "Implement age verification",
                    "Obtain verifiable parental consent",
                    "Limit data collection from children"
                ]
            ),
            "coppa_data_limitation": ComplianceRule(
                rule_id="coppa_data_limitation",
                name="COPPA Data Collection Limitation",
                framework=ComplianceFramework.COPPA,
                description="Limited data collection from children",
                risk_level=RiskLevel.HIGH,
                applicable_platforms=["all"],
                content_categories=[ContentCategory.CHILDREN],
                validation_logic="check_child_data_collection",
                action_on_violation=ComplianceAction.BLOCK,
                remediation_steps=[
                    "Minimize data collection from children",
                    "Implement data retention limits",
                    "Provide child-friendly privacy notices"
                ]
            )
        })
        
        # Data handling rules
        self.data_handling_rules.update({
            "personal_data_gdpr": DataHandlingRule(
                rule_id="personal_data_gdpr",
                framework=ComplianceFramework.GDPR,
                data_type="personal",
                collection_allowed=True,
                processing_allowed=True,
                storage_duration_days=365,
                encryption_required=True,
                consent_required=True,
                deletion_on_request=True,
                cross_border_transfer_allowed=False,  # Requires adequacy decision
                audit_logging_required=True
            ),
            "sensitive_data_gdpr": DataHandlingRule(
                rule_id="sensitive_data_gdpr",
                framework=ComplianceFramework.GDPR,
                data_type="sensitive",
                collection_allowed=False,  # Requires special conditions
                processing_allowed=False,
                encryption_required=True,
                consent_required=True,
                deletion_on_request=True,
                cross_border_transfer_allowed=False,
                audit_logging_required=True
            ),
            "financial_data_pci": DataHandlingRule(
                rule_id="financial_data_pci",
                framework=ComplianceFramework.PCI_DSS,
                data_type="financial",
                collection_allowed=True,
                processing_allowed=True,
                storage_duration_days=90,  # Minimize storage
                encryption_required=True,
                consent_required=True,
                deletion_on_request=True,
                cross_border_transfer_allowed=True,
                audit_logging_required=True
            )
        })
        
        # Age verification configs
        self.age_verification_configs.update({
            "instagram": AgeVerificationConfig(
                platform="instagram",
                minimum_age=13,
                verification_method="self_declaration",
                parental_consent_required=False,
                restricted_features=["shopping", "creator_fund"],
                grace_period_days=30
            ),
            "youtube": AgeVerificationConfig(
                platform="youtube",
                minimum_age=13,
                verification_method="self_declaration",
                parental_consent_required=True,  # For children mode
                restricted_features=["live_streaming", "comments_on_videos", "monetization"],
                grace_period_days=14
            ),
            "tiktok": AgeVerificationConfig(
                platform="tiktok",
                minimum_age=13,
                verification_method="self_declaration",
                parental_consent_required=False,
                restricted_features=["live_streaming", "direct_messaging", "creator_fund"],
                grace_period_days=7
            )
        })
        
        # Consent management
        self.consent_management.update({
            ComplianceFramework.GDPR: ConsentManagement(
                framework=ComplianceFramework.GDPR,
                consent_types=[
                    "data_processing", "marketing", "analytics", 
                    "third_party_sharing", "profiling"
                ],
                opt_in_required=True,
                withdrawal_method="self_service",
                consent_duration_days=365,
                renewal_required=True,
                granular_consent=True
            ),
            ComplianceFramework.CCPA: ConsentManagement(
                framework=ComplianceFramework.CCPA,
                consent_types=["data_sale_opt_out", "marketing", "analytics"],
                opt_in_required=False,  # Opt-out model
                withdrawal_method="self_service",
                granular_consent=True
            ),
            ComplianceFramework.COPPA: ConsentManagement(
                framework=ComplianceFramework.COPPA,
                consent_types=["data_collection", "data_sharing"],
                opt_in_required=True,
                withdrawal_method="parental_action",
                granular_consent=False
            )
        })
        
    def get_platform_policies(self, platform: str) -> List[PlatformPolicy]:
        """Get all policies for a platform"""
        return self.platform_policies.get(platform, [])
        
    def get_compliance_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get specific compliance rule"""
        return self.compliance_rules.get(rule_id)
        
    def get_data_handling_rule(self, rule_id: str) -> Optional[DataHandlingRule]:
        """Get specific data handling rule"""
        return self.data_handling_rules.get(rule_id)
        
    def get_age_verification_config(self, platform: str) -> Optional[AgeVerificationConfig]:
        """Get age verification config for platform"""
        return self.age_verification_configs.get(platform)
        
    def validate_content_compliance(
        self, 
        content: Dict[str, Any], 
        platform: str,
        user_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validate content against compliance rules"""
        violations = []
        warnings = []
        actions = []
        
        # Check platform policies
        policies = self.get_platform_policies(platform)
        for policy in policies:
            violation_result = self._check_policy_compliance(content, policy, user_age)
            if violation_result["violations"]:
                violations.extend(violation_result["violations"])
                actions.extend(violation_result["actions"])
                
        # Check applicable compliance rules
        for rule in self.compliance_rules.values():
            if not rule.enabled:
                continue
                
            if "all" not in rule.applicable_platforms and platform not in rule.applicable_platforms:
                continue
                
            if self._evaluate_compliance_rule(content, rule, user_age):
                violations.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "framework": rule.framework.value,
                    "risk_level": rule.risk_level.value,
                    "action": rule.action_on_violation.value,
                    "remediation_steps": rule.remediation_steps
                })
                actions.append(rule.action_on_violation.value)
                
        # Determine overall compliance status
        has_critical_violations = any(v.get("risk_level") == "critical" for v in violations)
        has_high_violations = any(v.get("risk_level") == "high" for v in violations)
        
        compliance_status = "compliant"
        if has_critical_violations:
            compliance_status = "critical_violations"
        elif has_high_violations:
            compliance_status = "high_risk_violations"
        elif violations:
            compliance_status = "minor_violations"
            
        return {
            "compliant": len(violations) == 0,
            "status": compliance_status,
            "violations": violations,
            "warnings": warnings,
            "recommended_actions": list(set(actions)),
            "platform": platform,
            "frameworks_checked": list(set(rule.framework.value for rule in self.compliance_rules.values() if rule.enabled))
        }
        
    def _check_policy_compliance(
        self, 
        content: Dict[str, Any], 
        policy: PlatformPolicy, 
        user_age: Optional[int]
    ) -> Dict[str, Any]:
        """Check content against platform policy"""
        violations = []
        actions = []
        
        # Check prohibited content
        content_text = content.get("text", "").lower()
        content_tags = [tag.lower() for tag in content.get("tags", [])]
        
        for prohibited_item in policy.prohibited_content:
            if (prohibited_item in content_text or 
                any(prohibited_item in tag for tag in content_tags)):
                violations.append({
                    "type": "prohibited_content",
                    "item": prohibited_item,
                    "policy": policy.policy_name
                })
                actions.append("review")
                
        # Check required disclosures
        for required_disclosure in policy.required_disclosures:
            if content.get("type") == "commercial" and required_disclosure not in content.get("disclosures", []):
                violations.append({
                    "type": "missing_disclosure",
                    "required": required_disclosure,
                    "policy": policy.policy_name
                })
                actions.append("modify")
                
        # Check age restrictions
        if user_age and "minimum_age" in policy.age_restrictions:
            if user_age < policy.age_restrictions["minimum_age"]:
                violations.append({
                    "type": "age_restriction",
                    "minimum_age": policy.age_restrictions["minimum_age"],
                    "user_age": user_age,
                    "policy": policy.policy_name
                })
                actions.append("block")
                
        return {
            "violations": violations,
            "actions": actions
        }
        
    def _evaluate_compliance_rule(
        self, 
        content: Dict[str, Any], 
        rule: ComplianceRule, 
        user_age: Optional[int]
    ) -> bool:
        """Evaluate if content violates compliance rule"""
        # Simplified rule evaluation - in practice, this would be more sophisticated
        
        if rule.framework == ComplianceFramework.COPPA:
            if user_age and user_age < 13:
                # Check if collecting personal data from children
                if content.get("collects_personal_data", False):
                    return not content.get("has_parental_consent", False)
                    
        elif rule.framework == ComplianceFramework.GDPR:
            if rule.rule_id == "gdpr_data_consent":
                return not content.get("has_explicit_consent", False)
            elif rule.rule_id == "gdpr_data_minimization":
                return content.get("data_fields_count", 0) > 10  # Example threshold
                
        elif rule.framework == ComplianceFramework.CCPA:
            if rule.rule_id == "ccpa_opt_out":
                return not content.get("has_opt_out_mechanism", False)
                
        return False
        
    def check_data_handling_compliance(
        self, 
        data_type: str, 
        operation: str, 
        framework: ComplianceFramework
    ) -> Dict[str, Any]:
        """Check if data handling operation is compliant"""
        rule_id = f"{data_type}_{framework.value}"
        rule = self.get_data_handling_rule(rule_id)
        
        if not rule:
            return {"allowed": True, "warnings": ["No specific rule found"]}
            
        result = {
            "allowed": True,
            "warnings": [],
            "requirements": []
        }
        
        if operation == "collection" and not rule.collection_allowed:
            result["allowed"] = False
            result["warnings"].append("Data collection not allowed for this type")
            
        if operation == "processing" and not rule.processing_allowed:
            result["allowed"] = False
            result["warnings"].append("Data processing not allowed for this type")
            
        if rule.consent_required:
            result["requirements"].append("explicit_consent")
            
        if rule.encryption_required:
            result["requirements"].append("encryption")
            
        if rule.audit_logging_required:
            result["requirements"].append("audit_logging")
            
        return result
        
    def get_consent_requirements(self, framework: ComplianceFramework) -> Optional[ConsentManagement]:
        """Get consent requirements for framework"""
        return self.consent_management.get(framework)
        
    def validate_age_verification(self, platform: str, user_age: int) -> Dict[str, Any]:
        """Validate age verification for platform"""
        config = self.get_age_verification_config(platform)
        if not config:
            return {"valid": True, "warnings": ["No age verification config"]}
            
        result = {
            "valid": user_age >= config.minimum_age,
            "minimum_age": config.minimum_age,
            "user_age": user_age,
            "restricted_features": [],
            "requirements": []
        }
        
        if user_age < config.minimum_age:
            result["restricted_features"] = config.restricted_features
            if config.parental_consent_required:
                result["requirements"].append("parental_consent")
        elif user_age < 18:  # Minor but above platform minimum
            # Some features may still be restricted
            result["restricted_features"] = [f for f in config.restricted_features if "adult" in f]
            
        return result
        
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance configuration summary"""
        return {
            "total_platforms": len(self.platform_policies),
            "total_policies": sum(len(policies) for policies in self.platform_policies.values()),
            "compliance_rules": {
                framework.value: len([r for r in self.compliance_rules.values() if r.framework == framework])
                for framework in ComplianceFramework
            },
            "data_handling_rules": len(self.data_handling_rules),
            "age_verification_platforms": len(self.age_verification_configs),
            "consent_frameworks": len(self.consent_management),
            "global_settings": self.global_settings
        }
        
    def export_config(self, output_path: str):
        """Export configuration to JSON file"""
        config_data = {
            "global_settings": self.global_settings,
            "platform_policies": {
                platform: [
                    {
                        "platform": policy.platform,
                        "policy_name": policy.policy_name,
                        "description": policy.description,
                        "content_categories": [cat.value for cat in policy.content_categories],
                        "prohibited_content": policy.prohibited_content,
                        "required_disclosures": policy.required_disclosures,
                        "age_restrictions": policy.age_restrictions,
                        "geographic_restrictions": policy.geographic_restrictions,
                        "last_updated": policy.last_updated.isoformat()
                    }
                    for policy in policies
                ]
                for platform, policies in self.platform_policies.items()
            },
            "compliance_rules": {
                rule_id: {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "framework": rule.framework.value,
                    "description": rule.description,
                    "risk_level": rule.risk_level.value,
                    "applicable_platforms": rule.applicable_platforms,
                    "content_categories": [cat.value for cat in rule.content_categories],
                    "validation_logic": rule.validation_logic,
                    "action_on_violation": rule.action_on_violation.value,
                    "remediation_steps": rule.remediation_steps,
                    "enabled": rule.enabled
                }
                for rule_id, rule in self.compliance_rules.items()
            },
            "data_handling_rules": {
                rule_id: {
                    "rule_id": rule.rule_id,
                    "framework": rule.framework.value,
                    "data_type": rule.data_type,
                    "collection_allowed": rule.collection_allowed,
                    "processing_allowed": rule.processing_allowed,
                    "storage_duration_days": rule.storage_duration_days,
                    "encryption_required": rule.encryption_required,
                    "consent_required": rule.consent_required,
                    "deletion_on_request": rule.deletion_on_request,
                    "cross_border_transfer_allowed": rule.cross_border_transfer_allowed,
                    "audit_logging_required": rule.audit_logging_required
                }
                for rule_id, rule in self.data_handling_rules.items()
            },
            "age_verification_configs": {
                platform: {
                    "platform": config.platform,
                    "minimum_age": config.minimum_age,
                    "verification_method": config.verification_method,
                    "parental_consent_required": config.parental_consent_required,
                    "restricted_features": config.restricted_features,
                    "grace_period_days": config.grace_period_days
                }
                for platform, config in self.age_verification_configs.items()
            },
            "consent_management": {
                framework.value: {
                    "framework": config.framework.value,
                    "consent_types": config.consent_types,
                    "opt_in_required": config.opt_in_required,
                    "withdrawal_method": config.withdrawal_method,
                    "consent_duration_days": config.consent_duration_days,
                    "renewal_required": config.renewal_required,
                    "granular_consent": config.granular_consent
                }
                for framework, config in self.consent_management.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

# Global instance
compliance_configs = ComplianceConfigs()

# Environment-based configuration loading
config_file = os.getenv('COMPLIANCE_CONFIG_FILE')
if config_file and os.path.exists(config_file):
    # Load custom configuration logic would go here
    pass

# Export configuration for external use
def get_compliance_configs() -> ComplianceConfigs:
    """Get the global compliance configurations instance"""
    return compliance_configs

def validate_content_compliance(
    content: Dict[str, Any], 
    platform: str, 
    user_age: Optional[int] = None
) -> Dict[str, Any]:
    """Validate content compliance"""
    return compliance_configs.validate_content_compliance(content, platform, user_age)

def check_data_handling_compliance(
    data_type: str, 
    operation: str, 
    framework: ComplianceFramework
) -> Dict[str, Any]:
    """Check data handling compliance"""
    return compliance_configs.check_data_handling_compliance(data_type, operation, framework)

def validate_age_verification(platform: str, user_age: int) -> Dict[str, Any]:
    """Validate age verification"""
    return compliance_configs.validate_age_verification(platform, user_age)

def get_platform_policies(platform: str) -> List[PlatformPolicy]:
    """Get platform policies"""
    return compliance_configs.get_platform_policies(platform)