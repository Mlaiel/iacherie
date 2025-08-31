"""
Legal Compliance Engine - Enterprise DMCA Compliance System
===========================================================

Advanced legal compliance engine for automated DMCA takedown processing,
copyright verification, and international legal framework compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import re
from pathlib import Path

from ..base import BaseAgent, AgentRequest, AgentResponse
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.legal_validator import LegalValidator
from ...utils.jurisdiction_mapper import JurisdictionMapper
from ...models.legal import LegalJurisdiction, ComplianceRule, LegalTemplate

logger = logging.getLogger(__name__)

class LegalFramework(Enum):
    """Supported legal frameworks"""
    DMCA_US = "dmca_us"
    EU_COPYRIGHT = "eu_copyright"
    UK_COPYRIGHT = "uk_copyright"
    CANADA_COPYRIGHT = "canada_copyright"
    AUSTRALIA_COPYRIGHT = "australia_copyright"
    JAPAN_COPYRIGHT = "japan_copyright"
    CHINA_COPYRIGHT = "china_copyright"
    INDIA_COPYRIGHT = "india_copyright"

class ComplianceStatus(Enum):
    """Legal compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANT = "partial_compliant"
    UNDER_REVIEW = "under_review"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"

@dataclass
class LegalRequirement:
    """Legal requirement specification"""
    framework: LegalFramework
    requirement_id: str
    description: str
    mandatory_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, Any]
    time_limits: Dict[str, int]  # in hours
    escalation_rules: Dict[str, Any]
    
@dataclass
class ComplianceResult:
    """Legal compliance check result"""
    case_id: str
    framework: LegalFramework
    status: ComplianceStatus
    compliance_score: float  # 0-100%
    missing_requirements: List[str]
    recommendations: List[str]
    legal_risks: List[str]
    next_actions: List[str]
    estimated_success_rate: float
    jurisdiction_notes: str
    created_at: datetime = field(default_factory=datetime.now)

class LegalComplianceEngine:
    """
    Enterprise Legal Compliance Engine
    
    Provides comprehensive legal compliance checking, multi-jurisdiction support,
    and automated legal requirement validation for DMCA and international copyright laws.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.legal_validator = LegalValidator()
        self.jurisdiction_mapper = JurisdictionMapper()
        
        # Legal framework definitions
        self.legal_frameworks = self._initialize_legal_frameworks()
        
        # Compliance rules cache
        self.compliance_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Legal templates
        self.legal_templates = self._load_legal_templates()
        
        self.logger.info("Legal Compliance Engine initialized successfully")
    
    def _initialize_legal_frameworks(self) -> Dict[LegalFramework, LegalRequirement]:
        """Initialize legal framework requirements"""
        frameworks = {
            LegalFramework.DMCA_US: LegalRequirement(
                framework=LegalFramework.DMCA_US,
                requirement_id="dmca_us_standard",
                description="US DMCA Title 17 USC Section 512(c)(3) Requirements",
                mandatory_fields=[
                    "copyright_owner_signature",
                    "copyright_owner_info",
                    "copyrighted_work_identification",
                    "infringing_material_location",
                    "good_faith_statement",
                    "accuracy_statement",
                    "contact_information"
                ],
                optional_fields=[
                    "representative_authorization",
                    "additional_evidence",
                    "preferred_remedy"
                ],
                validation_rules={
                    "url_format": r"https?://[^\s<>\"]+",
                    "email_format": r"[^@]+@[^@]+\.[^@]+",
                    "signature_required": True,
                    "min_description_length": 50
                },
                time_limits={
                    "initial_notice": 0,  # immediate
                    "response_expected": 168,  # 7 days
                    "counter_notice_period": 240,  # 10 days
                    "restoration_period": 336  # 14 days
                },
                escalation_rules={
                    "no_response_escalation": 168,
                    "dispute_escalation": 240,
                    "legal_action_threshold": 720
                }
            ),
            
            LegalFramework.EU_COPYRIGHT: LegalRequirement(
                framework=LegalFramework.EU_COPYRIGHT,
                requirement_id="eu_copyright_directive",
                description="EU Copyright Directive 2019/790 Article 17 Requirements",
                mandatory_fields=[
                    "copyright_holder_identity",
                    "copyrighted_work_details",
                    "infringement_evidence",
                    "takedown_request",
                    "legal_basis",
                    "jurisdiction_claim"
                ],
                optional_fields=[
                    "member_state_specifics",
                    "fair_use_consideration",
                    "automated_detection_info"
                ],
                validation_rules={
                    "gdpr_compliance": True,
                    "member_state_validation": True,
                    "proportionality_check": True
                },
                time_limits={
                    "notice_processing": 72,  # 3 days
                    "platform_response": 168,  # 7 days
                    "appeal_period": 336  # 14 days
                },
                escalation_rules={
                    "regulatory_escalation": 336,
                    "cross_border_coordination": 168
                }
            )
        }
        
        return frameworks
    
    def _load_legal_templates(self) -> Dict[str, str]:
        """Load legal document templates"""
        templates = {
            "dmca_takedown_notice": """
DMCA TAKEDOWN NOTICE
Digital Millennium Copyright Act - 17 U.S.C. § 512

To: {platform_name}
{platform_address}

Date: {notice_date}

Subject: DMCA Takedown Notice - Copyright Infringement

I, {copyright_owner_name}, am the owner of the exclusive rights, or an authorized representative of the owner, of an exclusive right that is allegedly infringed.

1. IDENTIFICATION OF COPYRIGHTED WORK:
{copyrighted_work_description}

2. IDENTIFICATION OF INFRINGING MATERIAL:
The following URLs contain material that infringes the above-described copyrighted work:
{infringing_urls}

3. CONTACT INFORMATION:
Name: {contact_name}
Address: {contact_address}
Phone: {contact_phone}
Email: {contact_email}

4. GOOD FAITH STATEMENT:
I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law.

5. ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.

Signature: {electronic_signature}
Date: {signature_date}

{additional_evidence}
            """,
            
            "eu_copyright_notice": """
EUROPEAN UNION COPYRIGHT TAKEDOWN NOTICE
EU Copyright Directive 2019/790 - Article 17

To: {platform_name}
{platform_address}

Date: {notice_date}
Jurisdiction: {eu_member_state}

Subject: Copyright Infringement Notice - EU Copyright Directive

I, {rights_holder_name}, am the rightsholder or authorized representative of copyrighted content being infringed on your platform.

1. RIGHTS HOLDER IDENTIFICATION:
{rights_holder_details}

2. COPYRIGHTED WORK IDENTIFICATION:
{work_identification}

3. INFRINGEMENT DETAILS:
Location of infringing content: {infringing_locations}
Type of infringement: {infringement_type}

4. LEGAL BASIS:
This notice is served under EU Copyright Directive 2019/790, Article 17, and applicable national legislation in {jurisdiction}.

5. REQUESTED ACTION:
{requested_remedy}

6. GOOD FAITH DECLARATION:
I declare in good faith that the use of the described material is not authorized by the rights holder, its agent, or the law.

Contact Information:
{contact_details}

Signature: {signature}
Date: {date}
            """
        }
        
        return templates
    
    async def check_compliance(
        self,
        case_data: Dict[str, Any],
        target_framework: LegalFramework,
        jurisdiction: Optional[str] = None
    ) -> ComplianceResult:
        """
        Comprehensive legal compliance check
        
        Args:
            case_data: DMCA case information
            target_framework: Legal framework to check against
            jurisdiction: Specific jurisdiction if applicable
            
        Returns:
            ComplianceResult with detailed compliance status
        """



        try:
            self.logger.info(f"Starting compliance check for case {case_data.get('case_id')}")
            
            # Get framework requirements
            framework_req = self.legal_frameworks.get(target_framework)
            if not framework_req:
                raise ValueError(f"Unsupported legal framework: {target_framework}")
            
            # Initialize compliance result
            result = ComplianceResult(
                case_id=case_data.get('case_id', ''),
                framework=target_framework,
                status=ComplianceStatus.UNDER_REVIEW,
                compliance_score=0.0,
                missing_requirements=[],
                recommendations=[],
                legal_risks=[],
                next_actions=[],
                estimated_success_rate=0.0,
                jurisdiction_notes=""
            )
            
            # Check mandatory fields
            mandatory_score = await self._check_mandatory_requirements(
                case_data, framework_req, result
            )
            
            # Check optional fields (bonus points)
            optional_score = await self._check_optional_requirements(
                case_data, framework_req, result
            )
            
            # Validate data format and content
            validation_score = await self._validate_data_format(
                case_data, framework_req, result
            )
            
            # Check jurisdiction-specific requirements
            jurisdiction_score = await self._check_jurisdiction_requirements(
                case_data, target_framework, jurisdiction, result
            )
            
            # Calculate overall compliance score
            result.compliance_score = (
                mandatory_score * 0.5 +
                optional_score * 0.1 +
                validation_score * 0.2 +
                jurisdiction_score * 0.2
            )
            
            # Determine compliance status
            result.status = self._determine_compliance_status(result.compliance_score)
            
            # Calculate success rate estimation
            result.estimated_success_rate = await self._estimate_success_rate(
                result, case_data, target_framework
            )
            
            # Generate recommendations
            await self._generate_recommendations(result, framework_req)
            
            self.logger.info(f"Compliance check completed: {result.compliance_score:.1f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            raise
    
    async def _check_mandatory_requirements(
        self,
        case_data: Dict[str, Any],
        framework_req: LegalRequirement,
        result: ComplianceResult
    ) -> float:
        """Check mandatory legal requirements"""
        total_fields = len(framework_req.mandatory_fields)
        satisfied_fields = 0
        
        for field in framework_req.mandatory_fields:
            if self._field_exists_and_valid(case_data, field, framework_req):
                satisfied_fields += 1
            else:
                result.missing_requirements.append(field)
                result.legal_risks.append(f"Missing mandatory field: {field}")
        
        return (satisfied_fields / total_fields) * 100 if total_fields > 0 else 0
    
    async def _check_optional_requirements(
        self,
        case_data: Dict[str, Any],
        framework_req: LegalRequirement,
        result: ComplianceResult
    ) -> float:
        """Check optional requirements (bonus points)"""
        total_fields = len(framework_req.optional_fields)
        if total_fields == 0:
            return 100.0
            
        satisfied_fields = 0
        
        for field in framework_req.optional_fields:
            if self._field_exists_and_valid(case_data, field, framework_req):
                satisfied_fields += 1
                result.recommendations.append(f"Good: Optional field '{field}' provided")
        
        return (satisfied_fields / total_fields) * 100
    
    async def _validate_data_format(
        self,
        case_data: Dict[str, Any],
        framework_req: LegalRequirement,
        result: ComplianceResult
    ) -> float:
        """Validate data format and content quality"""
        validation_rules = framework_req.validation_rules
        total_rules = len(validation_rules)
        passed_rules = 0
        
        for rule_name, rule_value in validation_rules.items():
            try:
                if await self._apply_validation_rule(case_data, rule_name, rule_value):
                    passed_rules += 1
                else:
                    result.legal_risks.append(f"Validation failed: {rule_name}")
            except Exception as e:
                self.logger.warning(f"Validation rule {rule_name} failed: {str(e)}")
                result.legal_risks.append(f"Validation error: {rule_name}")
        
        return (passed_rules / total_rules) * 100 if total_rules > 0 else 100.0
    
    async def _check_jurisdiction_requirements(
        self,
        case_data: Dict[str, Any],
        framework: LegalFramework,
        jurisdiction: Optional[str],
        result: ComplianceResult
    ) -> float:
        """Check jurisdiction-specific legal requirements"""



        try:
            if not jurisdiction:
                # Attempt to detect jurisdiction from case data
                jurisdiction = await self._detect_jurisdiction(case_data)
            
            if jurisdiction:
                # Get jurisdiction-specific requirements
                jurisdiction_rules = await self.jurisdiction_mapper.get_rules(
                    jurisdiction, framework
                )
                
                # Apply jurisdiction-specific validations
                compliance_score = await self._apply_jurisdiction_rules(
                    case_data, jurisdiction_rules, result
                )
                
                result.jurisdiction_notes = f"Jurisdiction: {jurisdiction}"
                return compliance_score
            else:
                result.jurisdiction_notes = "Jurisdiction could not be determined"
                result.recommendations.append("Consider specifying jurisdiction explicitly")
                return 50.0  # Neutral score for unknown jurisdiction
                
        except Exception as e:
            self.logger.error(f"Jurisdiction check failed: {str(e)}")
            result.legal_risks.append(f"Jurisdiction validation error: {str(e)}")
            return 0.0
    
    def _field_exists_and_valid(
        self,
        case_data: Dict[str, Any],
        field: str,
        framework_req: LegalRequirement
    ) -> bool:
        """Check if a field exists and meets basic validation"""
        value = case_data.get(field)
        
        if not value:
            return False
        
        # Check minimum length requirements
        if isinstance(value, str):
            if field in ["copyrighted_work_identification", "infringing_material_location"]:
                return len(value.strip()) >= framework_req.validation_rules.get("min_description_length", 10)
            elif "email" in field.lower():
                return bool(re.match(framework_req.validation_rules.get("email_format", r".+"), value))
            elif "url" in field.lower() or "location" in field.lower():
                return bool(re.match(framework_req.validation_rules.get("url_format", r".+"), value))
        
        return True
    
    async def _apply_validation_rule(
        self,
        case_data: Dict[str, Any],
        rule_name: str,
        rule_value: Any
    ) -> bool:
        """Apply specific validation rule"""
        if rule_name == "url_format":
            urls = self._extract_urls_from_case(case_data)
            return all(re.match(rule_value, url) for url in urls)
            
        elif rule_name == "email_format":
            emails = self._extract_emails_from_case(case_data)
            return all(re.match(rule_value, email) for email in emails)
            
        elif rule_name == "signature_required":
            return bool(case_data.get("copyright_owner_signature") or 
                       case_data.get("electronic_signature"))
            
        elif rule_name == "min_description_length":
            description = case_data.get("copyrighted_work_identification", "")
            return len(description.strip()) >= rule_value
            
        elif rule_name == "gdpr_compliance":
            return await self._check_gdpr_compliance(case_data)
            
        elif rule_name == "member_state_validation":
            return await self._validate_eu_member_state(case_data)
            
        elif rule_name == "proportionality_check":
            return await self._check_proportionality(case_data)
        
        return True  # Default to true for unknown rules
    
    def _extract_urls_from_case(self, case_data: Dict[str, Any]) -> List[str]:
        """Extract all URLs from case data"""
        urls = []
        url_fields = [
            "infringing_url", "infringing_urls", "infringing_material_location",
            "infringing_locations", "content_url", "platform_url"
        ]
        
        for field in url_fields:
            value = case_data.get(field)
            if value:
                if isinstance(value, str):
                    urls.append(value)
                elif isinstance(value, list):
                    urls.extend(value)
        
        return urls
    
    def _extract_emails_from_case(self, case_data: Dict[str, Any]) -> List[str]:
        """Extract all email addresses from case data"""
        emails = []
        email_fields = [
            "contact_email", "copyright_owner_email", "representative_email",
            "notification_email", "contact_information"
        ]
        
        for field in email_fields:
            value = case_data.get(field, "")
            if isinstance(value, str):
                # Extract emails using regex
                found_emails = re.findall(r'[^@]+@[^@]+\.[^@]+', value)
                emails.extend(found_emails)
        
        return emails
    
    async def _detect_jurisdiction(self, case_data: Dict[str, Any]) -> Optional[str]:
        """Attempt to detect jurisdiction from case data"""
        # Check explicit jurisdiction fields
        jurisdiction_fields = ["jurisdiction", "country", "legal_jurisdiction"]
        for field in jurisdiction_fields:
            if case_data.get(field):
                return case_data[field]
        
        # Try to detect from URLs
        urls = self._extract_urls_from_case(case_data)
        if urls:
            return await self.jurisdiction_mapper.detect_from_urls(urls)
        
        # Try to detect from platform
        platform = case_data.get("platform", "")
        if platform:
            return await self.jurisdiction_mapper.detect_from_platform(platform)
        
        return None
    
    async def _apply_jurisdiction_rules(
        self,
        case_data: Dict[str, Any],
        jurisdiction_rules: Dict[str, Any],
        result: ComplianceResult
    ) -> float:
        """Apply jurisdiction-specific validation rules"""
        if not jurisdiction_rules:
            return 100.0
        
        total_rules = len(jurisdiction_rules)
        passed_rules = 0
        
        for rule_name, rule_config in jurisdiction_rules.items():
            try:
                if await self._evaluate_jurisdiction_rule(case_data, rule_name, rule_config):
                    passed_rules += 1
                else:
                    result.legal_risks.append(f"Jurisdiction rule failed: {rule_name}")
            except Exception as e:
                self.logger.warning(f"Jurisdiction rule {rule_name} error: {str(e)}")
        
        return (passed_rules / total_rules) * 100 if total_rules > 0 else 100.0
    
    async def _evaluate_jurisdiction_rule(
        self,
        case_data: Dict[str, Any],
        rule_name: str,
        rule_config: Any
    ) -> bool:
        """Evaluate specific jurisdiction rule"""
        # Implement jurisdiction-specific rule evaluation
        # This would contain specific logic for different jurisdictions
        return True  # Placeholder
    
    def _determine_compliance_status(self, compliance_score: float) -> ComplianceStatus:
        """Determine compliance status based on score"""
        if compliance_score >= 95.0:
            return ComplianceStatus.COMPLIANT
        elif compliance_score >= 80.0:
            return ComplianceStatus.PARTIAL_COMPLIANT
        elif compliance_score >= 60.0:
            return ComplianceStatus.REQUIRES_MANUAL_REVIEW
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    async def _estimate_success_rate(
        self,
        result: ComplianceResult,
        case_data: Dict[str, Any],
        framework: LegalFramework
    ) -> float:
        """Estimate legal success rate based on compliance and historical data"""
        base_rate = result.compliance_score
        
        # Adjust based on case factors
        adjustments = 0.0
        
        # Strong evidence bonus
        if case_data.get("evidence_quality", "").lower() in ["high", "strong"]:
            adjustments += 10.0
        
        # Clear infringement bonus
        similarity_score = case_data.get("similarity_score", 0.0)
        if isinstance(similarity_score, (int, float)) and similarity_score > 0.9:
            adjustments += 15.0
        
        # Platform cooperation history
        platform = case_data.get("platform", "")
        if await self._check_platform_cooperation_history(platform):
            adjustments += 5.0
        
        # Legal precedent strength
        if await self._check_legal_precedent_strength(framework, case_data):
            adjustments += 10.0
        
        # Cap at 100%
        return min(100.0, base_rate + adjustments)
    
    async def _generate_recommendations(
        self,
        result: ComplianceResult,
        framework_req: LegalRequirement
    ) -> None:
        """Generate actionable recommendations"""
        if result.missing_requirements:
            result.next_actions.append("Complete missing mandatory requirements")
            
        if result.compliance_score < 80.0:
            result.next_actions.append("Review and strengthen legal documentation")
            
        if result.legal_risks:
            result.next_actions.append("Address identified legal risks before proceeding")
            
        # Framework-specific recommendations
        if framework_req.framework == LegalFramework.DMCA_US:
            if "copyright_owner_signature" in result.missing_requirements:
                result.recommendations.append("Ensure electronic or physical signature is provided")
                
        elif framework_req.framework == LegalFramework.EU_COPYRIGHT:
            if result.compliance_score < 90.0:
                result.recommendations.append("Consider GDPR implications and member state specifics")
    
    async def _check_gdpr_compliance(self, case_data: Dict[str, Any]) -> bool:
        """Check GDPR compliance for EU cases"""
        # Implement GDPR-specific checks
        return True  # Placeholder
    
    async def _validate_eu_member_state(self, case_data: Dict[str, Any]) -> bool:
        """Validate EU member state requirements"""
        # Implement EU member state validation
        return True  # Placeholder
    
    async def _check_proportionality(self, case_data: Dict[str, Any]) -> bool:
        """Check proportionality of takedown request"""
        # Implement proportionality assessment
        return True  # Placeholder
    
    async def _check_platform_cooperation_history(self, platform: str) -> bool:
        """Check historical cooperation of platform"""
        # Implement platform cooperation history check
        return True  # Placeholder
    
    async def _check_legal_precedent_strength(
        self,
        framework: LegalFramework,
        case_data: Dict[str, Any]
    ) -> bool:
        """Check strength of legal precedent"""
        # Implement legal precedent analysis
        return True  # Placeholder
    
    async def get_legal_template(
        self,
        framework: LegalFramework,
        case_data: Dict[str, Any]
    ) -> str:
        """Generate legal document from template"""



        try:
            template_key = f"{framework.value}_notice"
            if template_key.replace(f"_{framework.value.split('_')[1]}", "_takedown") in self.legal_templates:
                template_key = template_key.replace(f"_{framework.value.split('_')[1]}", "_takedown")
            
            template = self.legal_templates.get(template_key)
            if not template:
                raise ValueError(f"No template found for framework: {framework}")
            
            # Fill template with case data
            filled_template = await self._fill_legal_template(template, case_data)
            
            return filled_template
            
        except Exception as e:
            self.logger.error(f"Template generation failed: {str(e)}")
            raise
    
    async def _fill_legal_template(self, template: str, case_data: Dict[str, Any]) -> str:
        """Fill legal template with case data"""
        # Create template variables
        template_vars = {
            'notice_date': datetime.now().strftime('%B %d, %Y'),
            'signature_date': datetime.now().strftime('%B %d, %Y'),
            'platform_name': case_data.get('platform', 'Platform'),
            'platform_address': case_data.get('platform_address', 'Unknown Address'),
            'copyright_owner_name': case_data.get('copyright_owner_name', 'Rights Holder'),
            'copyrighted_work_description': case_data.get('copyrighted_work_identification', 'Copyrighted Work'),
            'infringing_urls': '\n'.join(self._extract_urls_from_case(case_data)),
            'contact_name': case_data.get('contact_name', case_data.get('copyright_owner_name', 'Rights Holder')),
            'contact_address': case_data.get('contact_address', 'Contact Address'),
            'contact_phone': case_data.get('contact_phone', 'Contact Phone'),
            'contact_email': case_data.get('contact_email', 'contact@example.com'),
            'electronic_signature': case_data.get('electronic_signature', case_data.get('copyright_owner_signature', 'Digital Signature')),
            'additional_evidence': case_data.get('additional_evidence', '')
        }
        
        # Fill template
        try:
            return template.format(**template_vars)
        except KeyError as e:
            self.logger.error(f"Template variable missing: {str(e)}")
            # Return template with unfilled variables marked
            return template.format_map(DefaultDict(lambda: "[MISSING]", template_vars))

class DefaultDict(dict):
    """Dictionary that returns a default value for missing keys"""
    def __init__(self, default_factory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory
    
    def __missing__(self, key):
        return self.default_factory()
