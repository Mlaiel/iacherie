"""
Global Legal Compliance Configuration
=====================================

Configuration for worldwide legal compliance frameworks including
GDPR, CCPA, DMCA, PIPEDA, LGPD, and PDPA.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ComplianceFrameworkConfig:
    """Configuration for a compliance framework"""
    framework_id: str
    name: str
    jurisdiction: str
    effective_date: str
    enforcement_authority: str
    enabled: bool = True
    priority: int = 1  # 1 = highest priority
    auto_assess: bool = True
    notification_required: bool = True
    breach_notification_hours: int = 72
    data_subject_rights: List[str] = field(default_factory=list)
    key_requirements: List[str] = field(default_factory=list)
    penalty_description: str = ""
    website_url: str = ""


class GlobalComplianceConfig:
    """Global configuration for legal compliance frameworks"""
    
    def __init__(self):
        """Initialize global compliance configuration"""
        self.frameworks = self._initialize_compliance_frameworks()
        self.jurisdiction_mapping = self._initialize_jurisdiction_mapping()
        self.content_type_requirements = self._initialize_content_requirements()
        self.notification_settings = self._initialize_notification_settings()
    
    def _initialize_compliance_frameworks(self) -> Dict[str, ComplianceFrameworkConfig]:
        """Initialize all supported compliance frameworks"""
        return {
            "gdpr": ComplianceFrameworkConfig(
                framework_id="gdpr",
                name="General Data Protection Regulation",
                jurisdiction="European Union",
                effective_date="2018-05-25",
                enforcement_authority="Data Protection Authorities",
                priority=1,
                breach_notification_hours=72,
                data_subject_rights=[
                    "right_to_information",
                    "right_of_access", 
                    "right_to_rectification",
                    "right_to_erasure",
                    "right_to_restrict_processing",
                    "right_to_data_portability",
                    "right_to_object",
                    "rights_automated_decision_making"
                ],
                key_requirements=[
                    "Lawful basis for processing",
                    "Data subject consent",
                    "Data minimization",
                    "Purpose limitation",
                    "Storage limitation",
                    "Integrity and confidentiality",
                    "Accountability"
                ],
                penalty_description="Up to 4% of annual revenue or €20M",
                website_url="https://gdpr.eu/"
            ),
            
            "ccpa": ComplianceFrameworkConfig(
                framework_id="ccpa",
                name="California Consumer Privacy Act",
                jurisdiction="California, USA",
                effective_date="2020-01-01",
                enforcement_authority="California Attorney General",
                priority=2,
                breach_notification_hours=72,
                data_subject_rights=[
                    "right_to_know",
                    "right_to_delete",
                    "right_to_opt_out",
                    "right_to_non_discrimination"
                ],
                key_requirements=[
                    "Consumer right to know",
                    "Consumer right to delete",
                    "Consumer right to opt-out",
                    "Disclosure requirements",
                    "Non-discrimination provisions"
                ],
                penalty_description="Up to $7,500 per violation",
                website_url="https://oag.ca.gov/privacy/ccpa"
            ),
            
            "dmca": ComplianceFrameworkConfig(
                framework_id="dmca",
                name="Digital Millennium Copyright Act",
                jurisdiction="United States",
                effective_date="1998-10-28",
                enforcement_authority="US Copyright Office",
                priority=1,
                breach_notification_hours=24,
                data_subject_rights=[],
                key_requirements=[
                    "Copyright ownership documentation",
                    "DMCA takedown procedures", 
                    "Safe harbor compliance",
                    "Designated agent registration"
                ],
                penalty_description="Statutory damages up to $150,000 per work",
                website_url="https://www.copyright.gov/legislation/dmca.pdf"
            ),
            
            "pipeda": ComplianceFrameworkConfig(
                framework_id="pipeda",
                name="Personal Information Protection and Electronic Documents Act",
                jurisdiction="Canada",
                effective_date="2001-01-01",
                enforcement_authority="Office of the Privacy Commissioner of Canada",
                priority=2,
                breach_notification_hours=72,
                data_subject_rights=[
                    "individual_access",
                    "challenging_compliance"
                ],
                key_requirements=[
                    "Accountability",
                    "Identifying purposes",
                    "Consent",
                    "Limiting collection",
                    "Limiting use, disclosure, and retention",
                    "Accuracy",
                    "Safeguards",
                    "Openness",
                    "Individual access",
                    "Challenging compliance"
                ],
                penalty_description="Up to CAD $100,000 per violation",
                website_url="https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/"
            ),
            
            "lgpd": ComplianceFrameworkConfig(
                framework_id="lgpd",
                name="Lei Geral de Proteção de Dados",
                jurisdiction="Brazil",
                effective_date="2020-09-18",
                enforcement_authority="Autoridade Nacional de Proteção de Dados (ANPD)",
                priority=2,
                breach_notification_hours=72,
                data_subject_rights=[
                    "access",
                    "rectification",
                    "erasure",
                    "portability",
                    "opposition",
                    "explanation_automated_decisions"
                ],
                key_requirements=[
                    "Purpose",
                    "Adequacy", 
                    "Necessity",
                    "Free access",
                    "Data quality",
                    "Transparency",
                    "Security",
                    "Prevention",
                    "Non-discrimination",
                    "Accountability"
                ],
                penalty_description="Up to 2% of annual revenue or R$ 50M",
                website_url="https://www.gov.br/anpd/pt-br"
            ),
            
            "pdpa_singapore": ComplianceFrameworkConfig(
                framework_id="pdpa_singapore",
                name="Personal Data Protection Act (Singapore)",
                jurisdiction="Singapore",
                effective_date="2014-07-02",
                enforcement_authority="Personal Data Protection Commission (PDPC)",
                priority=3,
                breach_notification_hours=72,
                data_subject_rights=[
                    "access",
                    "correction"
                ],
                key_requirements=[
                    "Consent",
                    "Purpose limitation",
                    "Notification",
                    "Access and correction",
                    "Accuracy",
                    "Protection",
                    "Retention limitation",
                    "Transfer limitation"
                ],
                penalty_description="Up to SGD $1M for organizations",
                website_url="https://www.pdpc.gov.sg/"
            ),
            
            "pdpa_thailand": ComplianceFrameworkConfig(
                framework_id="pdpa_thailand",
                name="Personal Data Protection Act (Thailand)",
                jurisdiction="Thailand",
                effective_date="2022-06-01",
                enforcement_authority="Personal Data Protection Committee (PDPC)",
                priority=3,
                breach_notification_hours=72,
                data_subject_rights=[
                    "access",
                    "rectification",
                    "erasure",
                    "restriction",
                    "portability",
                    "objection"
                ],
                key_requirements=[
                    "Lawful basis for processing",
                    "Consent",
                    "Purpose limitation",
                    "Data minimization",
                    "Accuracy",
                    "Storage limitation",
                    "Security",
                    "Accountability"
                ],
                penalty_description="Up to THB 5M or 4% of annual revenue",
                website_url="https://www.pdpc.or.th/"
            )
        }
    
    def _initialize_jurisdiction_mapping(self) -> Dict[str, List[str]]:
        """Initialize jurisdiction to framework mapping"""
        return {
            "EU": ["gdpr"],
            "AT": ["gdpr"],  # Austria
            "BE": ["gdpr"],  # Belgium
            "BG": ["gdpr"],  # Bulgaria
            "HR": ["gdpr"],  # Croatia
            "CY": ["gdpr"],  # Cyprus
            "CZ": ["gdpr"],  # Czech Republic
            "DK": ["gdpr"],  # Denmark
            "EE": ["gdpr"],  # Estonia
            "FI": ["gdpr"],  # Finland
            "FR": ["gdpr"],  # France
            "DE": ["gdpr"],  # Germany
            "GR": ["gdpr"],  # Greece
            "HU": ["gdpr"],  # Hungary
            "IE": ["gdpr"],  # Ireland
            "IT": ["gdpr"],  # Italy
            "LV": ["gdpr"],  # Latvia
            "LT": ["gdpr"],  # Lithuania
            "LU": ["gdpr"],  # Luxembourg
            "MT": ["gdpr"],  # Malta
            "NL": ["gdpr"],  # Netherlands
            "PL": ["gdpr"],  # Poland
            "PT": ["gdpr"],  # Portugal
            "RO": ["gdpr"],  # Romania
            "SK": ["gdpr"],  # Slovakia
            "SI": ["gdpr"],  # Slovenia
            "ES": ["gdpr"],  # Spain
            "SE": ["gdpr"],  # Sweden
            "US": ["dmca"],
            "CA": ["pipeda", "dmca"],  # California also has CCPA
            "BR": ["lgpd"],
            "SG": ["pdpa_singapore"],
            "TH": ["pdpa_thailand"],
            "GLOBAL": ["dmca"]  # Default for international content
        }
    
    def _initialize_content_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content type specific requirements"""
        return {
            "audio": {
                "required_frameworks": ["dmca"],
                "optional_frameworks": ["gdpr", "ccpa", "pipeda", "lgpd"],
                "special_considerations": [
                    "Voice biometric data may be sensitive under GDPR",
                    "Audio fingerprinting for copyright protection",
                    "Lyrics may contain personal information"
                ]
            },
            "video": {
                "required_frameworks": ["dmca"],
                "optional_frameworks": ["gdpr", "ccpa", "pipeda", "lgpd", "pdpa_singapore", "pdpa_thailand"],
                "special_considerations": [
                    "Facial recognition data is highly sensitive",
                    "Location data from metadata",
                    "Voice and visual biometric data"
                ]
            },
            "image": {
                "required_frameworks": ["dmca"],
                "optional_frameworks": ["gdpr", "ccpa", "pipeda", "lgpd", "pdpa_singapore", "pdpa_thailand"],
                "special_considerations": [
                    "Facial recognition and biometric data",
                    "EXIF data may contain location information",
                    "People in images may have privacy rights"
                ]
            },
            "text": {
                "required_frameworks": [],
                "optional_frameworks": ["gdpr", "ccpa", "pipeda", "lgpd", "pdpa_singapore", "pdpa_thailand", "dmca"],
                "special_considerations": [
                    "May contain personal names and information",
                    "Copyright protection for written content",
                    "Sensitive personal data detection required"
                ]
            }
        }
    
    def _initialize_notification_settings(self) -> Dict[str, Any]:
        """Initialize notification settings for compliance"""
        return {
            "breach_notification": {
                "enabled": True,
                "immediate_notification_frameworks": ["gdpr", "ccpa", "lgpd"],
                "notification_channels": ["email", "dashboard", "webhook"],
                "escalation_hours": 24
            },
            "audit_logging": {
                "enabled": True,
                "log_all_assessments": True,
                "retention_days": 2555,  # 7 years
                "encryption_required": True
            },
            "compliance_monitoring": {
                "enabled": True,
                "continuous_monitoring": True,
                "alert_thresholds": {
                    "critical_issues": 1,
                    "high_issues": 5,
                    "medium_issues": 20
                },
                "reporting_frequency": "daily"
            }
        }
    
    def get_applicable_frameworks(
        self, 
        jurisdiction: Optional[str] = None,
        content_type: Optional[str] = None,
        user_location: Optional[str] = None
    ) -> List[ComplianceFrameworkConfig]:
        """
        Get applicable compliance frameworks based on context
        
        Args:
            jurisdiction: Legal jurisdiction code
            content_type: Type of content (audio, video, image, text)
            user_location: Location of user/data subject
            
        Returns:
            List of applicable compliance framework configs
        """
        applicable_frameworks = []
        
        # Determine jurisdictions to check
        jurisdictions_to_check = set()
        
        if jurisdiction:
            jurisdictions_to_check.add(jurisdiction.upper())
        
        if user_location:
            jurisdictions_to_check.add(user_location.upper())
        
        # Add frameworks based on jurisdictions
        for jur in jurisdictions_to_check:
            if jur in self.jurisdiction_mapping:
                for framework_id in self.jurisdiction_mapping[jur]:
                    if framework_id in self.frameworks:
                        framework = self.frameworks[framework_id]
                        if framework.enabled and framework not in applicable_frameworks:
                            applicable_frameworks.append(framework)
        
        # Add content-specific frameworks
        if content_type and content_type in self.content_type_requirements:
            content_req = self.content_type_requirements[content_type]
            
            # Add required frameworks
            for framework_id in content_req.get("required_frameworks", []):
                if framework_id in self.frameworks:
                    framework = self.frameworks[framework_id]
                    if framework.enabled and framework not in applicable_frameworks:
                        applicable_frameworks.append(framework)
        
        # If no specific frameworks found, add global defaults
        if not applicable_frameworks:
            for framework_id in ["dmca"]:  # Global default
                if framework_id in self.frameworks:
                    framework = self.frameworks[framework_id]
                    if framework.enabled:
                        applicable_frameworks.append(framework)
        
        # Sort by priority
        applicable_frameworks.sort(key=lambda f: f.priority)
        
        return applicable_frameworks
    
    def get_framework_config(self, framework_id: str) -> Optional[ComplianceFrameworkConfig]:
        """Get configuration for specific framework"""
        return self.frameworks.get(framework_id)
    
    def get_all_frameworks(self) -> Dict[str, ComplianceFrameworkConfig]:
        """Get all configured frameworks"""
        return self.frameworks
    
    def get_enabled_frameworks(self) -> Dict[str, ComplianceFrameworkConfig]:
        """Get all enabled frameworks"""
        return {k: v for k, v in self.frameworks.items() if v.enabled}
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration"""
        return self.notification_settings
    
    def get_jurisdiction_frameworks(self, jurisdiction: str) -> List[str]:
        """Get frameworks applicable to a jurisdiction"""
        return self.jurisdiction_mapping.get(jurisdiction.upper(), [])
    
    def get_content_requirements(self, content_type: str) -> Dict[str, Any]:
        """Get requirements for specific content type"""
        return self.content_type_requirements.get(content_type, {})
    
    def is_framework_enabled(self, framework_id: str) -> bool:
        """Check if a framework is enabled"""
        framework = self.frameworks.get(framework_id)
        return framework.enabled if framework else False
    
    def enable_framework(self, framework_id: str) -> bool:
        """Enable a compliance framework"""
        if framework_id in self.frameworks:
            self.frameworks[framework_id].enabled = True
            return True
        return False
    
    def disable_framework(self, framework_id: str) -> bool:
        """Disable a compliance framework"""
        if framework_id in self.frameworks:
            self.frameworks[framework_id].enabled = False
            return True
        return False
    
    def get_breach_notification_requirements(self, framework_id: str) -> Dict[str, Any]:
        """Get breach notification requirements for framework"""
        framework = self.frameworks.get(framework_id)
        if not framework:
            return {}
        
        return {
            "framework": framework.name,
            "jurisdiction": framework.jurisdiction,
            "notification_required": framework.notification_required,
            "notification_hours": framework.breach_notification_hours,
            "enforcement_authority": framework.enforcement_authority,
            "penalty_description": framework.penalty_description
        }
    
    def validate_compliance_configuration(self) -> Dict[str, Any]:
        """Validate the compliance configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        # Check that all frameworks have required fields
        for framework_id, framework in self.frameworks.items():
            if not framework.name:
                validation_results["errors"].append(f"Framework {framework_id} missing name")
                validation_results["valid"] = False
            
            if not framework.jurisdiction:
                validation_results["errors"].append(f"Framework {framework_id} missing jurisdiction")
                validation_results["valid"] = False
            
            if not framework.enforcement_authority:
                validation_results["warnings"].append(f"Framework {framework_id} missing enforcement authority")
        
        # Check jurisdiction mapping
        for jurisdiction, frameworks in self.jurisdiction_mapping.items():
            for framework_id in frameworks:
                if framework_id not in self.frameworks:
                    validation_results["errors"].append(f"Jurisdiction {jurisdiction} references unknown framework {framework_id}")
                    validation_results["valid"] = False
        
        # Generate summary
        validation_results["summary"] = {
            "total_frameworks": len(self.frameworks),
            "enabled_frameworks": len(self.get_enabled_frameworks()),
            "jurisdictions_covered": len(self.jurisdiction_mapping),
            "content_types_covered": len(self.content_type_requirements)
        }
        
        return validation_results


# Global instance
global_compliance_config = GlobalComplianceConfig()