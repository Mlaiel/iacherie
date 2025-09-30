"""
⚖️ Platform Compliance Microservice
Platform-specific compliance management for legal, content, and policy adherence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ComplianceType(str, Enum):
    """Types of compliance requirements"""
    CONTENT_POLICY = "content_policy"
    PRIVACY_REGULATION = "privacy_regulation"
    COPYRIGHT = "copyright"
    AGE_RESTRICTION = "age_restriction"
    GEOGRAPHIC_RESTRICTION = "geographic_restriction"
    ADVERTISING_STANDARD = "advertising_standard"
    ACCESSIBILITY = "accessibility"
    DATA_PROTECTION = "data_protection"
    COMMUNITY_GUIDELINES = "community_guidelines"
    MONETIZATION_POLICY = "monetization_policy"


class ComplianceStatus(str, Enum):
    """Compliance status states"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    CONDITIONALLY_COMPLIANT = "conditionally_compliant"
    REQUIRES_ACTION = "requires_action"
    EXEMPT = "exempt"


class Severity(str, Enum):
    """Compliance violation severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ActionType(str, Enum):
    """Required compliance actions"""
    CONTENT_MODIFICATION = "content_modification"
    METADATA_UPDATE = "metadata_update"
    AGE_GATE_ADDITION = "age_gate_addition"
    GEOGRAPHIC_BLOCKING = "geographic_blocking"
    DISCLAIMER_ADDITION = "disclaimer_addition"
    PRIVACY_NOTICE = "privacy_notice"
    CONSENT_COLLECTION = "consent_collection"
    ACCESSIBILITY_IMPROVEMENT = "accessibility_improvement"
    MANUAL_REVIEW = "manual_review"


@dataclass
class ComplianceRule:
    """Platform-specific compliance rule"""
    rule_id: str
    platform_id: str
    compliance_type: ComplianceType
    title: str
    description: str
    requirements: List[str]
    validation_criteria: Dict[str, Any]
    severity: Severity
    auto_enforceable: bool
    applicable_regions: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    content_id: str
    creator_id: str
    platform_id: str
    compliance_type: ComplianceType
    severity: Severity
    description: str
    details: Dict[str, Any]
    required_actions: List[ActionType]
    auto_fixable: bool
    deadline: Optional[datetime] = None
    status: ComplianceStatus = ComplianceStatus.REQUIRES_ACTION
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    check_id: str
    content_id: str
    platform_id: str
    compliance_types: List[ComplianceType]
    overall_status: ComplianceStatus
    violations: List[ComplianceViolation]
    recommendations: List[str]
    checked_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class ComplianceReport:
    """Compliance status report"""
    report_id: str
    creator_id: str
    platform_id: str
    reporting_period: Dict[str, datetime]
    total_content_items: int
    compliant_items: int
    violation_summary: Dict[ComplianceType, int]
    critical_violations: int
    resolved_violations: int
    pending_actions: int
    compliance_score: float  # 0-100
    trends: Dict[str, float]
    generated_at: datetime = field(default_factory=datetime.now)


class ComplianceRuleEngine:
    """Core compliance rule validation engine"""
    
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.platform_rules: Dict[str, List[str]] = {}
        self.validators: Dict[ComplianceType, Callable] = {}
        self._setup_default_rules()
        self._setup_validators()
    
    async def validate_content(
        self,
        content: Dict[str, Any],
        platform_id: str,
        creator_id: str,
        compliance_types: Optional[List[ComplianceType]] = None
    ) -> ComplianceCheck:
        """Validate content against platform compliance rules"""
        try:
            check_id = str(uuid.uuid4())
            content_id = content.get("id", str(uuid.uuid4()))
            
            # Get applicable rules
            applicable_rules = await self._get_applicable_rules(
                platform_id, 
                compliance_types or list(ComplianceType)
            )
            
            violations = []
            
            # Check each rule
            for rule in applicable_rules:
                violation = await self._check_rule(
                    rule=rule,
                    content=content,
                    creator_id=creator_id,
                    content_id=content_id
                )
                if violation:
                    violations.append(violation)
            
            # Determine overall status
            overall_status = self._determine_overall_status(violations)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(violations, content)
            
            return ComplianceCheck(
                check_id=check_id,
                content_id=content_id,
                platform_id=platform_id,
                compliance_types=compliance_types or list(ComplianceType),
                overall_status=overall_status,
                violations=violations,
                recommendations=recommendations,
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
        except Exception as e:
            logger.error(f"Failed to validate content compliance: {e}")
            raise
    
    async def _get_applicable_rules(
        self,
        platform_id: str,
        compliance_types: List[ComplianceType]
    ) -> List[ComplianceRule]:
        """Get applicable compliance rules for platform and types"""
        applicable_rules = []
        
        platform_rule_ids = self.platform_rules.get(platform_id, [])
        
        for rule_id in platform_rule_ids:
            rule = self.rules.get(rule_id)
            if rule and rule.compliance_type in compliance_types:
                applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _check_rule(
        self,
        rule: ComplianceRule,
        content: Dict[str, Any],
        creator_id: str,
        content_id: str
    ) -> Optional[ComplianceViolation]:
        """Check content against a specific rule"""
        try:
            # Use registered validator if available
            if rule.compliance_type in self.validators:
                is_compliant = await self.validators[rule.compliance_type](
                    content, rule.validation_criteria
                )
            else:
                # Default validation logic
                is_compliant = await self._default_validation(content, rule)
            
            if not is_compliant:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    content_id=content_id,
                    creator_id=creator_id,
                    platform_id=rule.platform_id,
                    compliance_type=rule.compliance_type,
                    severity=rule.severity,
                    description=f"Content violates {rule.title}",
                    details={"rule_requirements": rule.requirements},
                    required_actions=self._determine_required_actions(rule),
                    auto_fixable=rule.auto_enforceable
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check rule {rule.rule_id}: {e}")
            return None
    
    async def _default_validation(
        self,
        content: Dict[str, Any],
        rule: ComplianceRule
    ) -> bool:
        """Default validation logic for rules"""
        # Simple keyword-based validation
        text_content = " ".join([
            str(content.get("title", "")),
            str(content.get("description", "")),
            str(content.get("caption", ""))
        ]).lower()
        
        # Check for prohibited keywords (example)
        prohibited_keywords = rule.validation_criteria.get("prohibited_keywords", [])
        for keyword in prohibited_keywords:
            if keyword.lower() in text_content:
                return False
        
        # Check content length requirements
        min_length = rule.validation_criteria.get("min_title_length", 0)
        if len(content.get("title", "")) < min_length:
            return False
        
        return True
    
    def _determine_overall_status(
        self,
        violations: List[ComplianceViolation]
    ) -> ComplianceStatus:
        """Determine overall compliance status"""
        if not violations:
            return ComplianceStatus.COMPLIANT
        
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT
        
        high_violations = [v for v in violations if v.severity == Severity.HIGH]
        if high_violations:
            return ComplianceStatus.REQUIRES_ACTION
        
        return ComplianceStatus.CONDITIONALLY_COMPLIANT
    
    def _determine_required_actions(self, rule: ComplianceRule) -> List[ActionType]:
        """Determine required actions based on rule type"""
        action_mapping = {
            ComplianceType.CONTENT_POLICY: [ActionType.CONTENT_MODIFICATION],
            ComplianceType.AGE_RESTRICTION: [ActionType.AGE_GATE_ADDITION],
            ComplianceType.GEOGRAPHIC_RESTRICTION: [ActionType.GEOGRAPHIC_BLOCKING],
            ComplianceType.ADVERTISING_STANDARD: [ActionType.DISCLAIMER_ADDITION],
            ComplianceType.PRIVACY_REGULATION: [ActionType.PRIVACY_NOTICE],
            ComplianceType.ACCESSIBILITY: [ActionType.ACCESSIBILITY_IMPROVEMENT],
            ComplianceType.DATA_PROTECTION: [ActionType.CONSENT_COLLECTION]
        }
        
        return action_mapping.get(rule.compliance_type, [ActionType.MANUAL_REVIEW])
    
    async def _generate_recommendations(
        self,
        violations: List[ComplianceViolation],
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if not violations:
            recommendations.append("Content is fully compliant with platform policies")
            return recommendations
        
        violation_types = {v.compliance_type for v in violations}
        
        if ComplianceType.CONTENT_POLICY in violation_types:
            recommendations.append("Review and modify content to align with platform community guidelines")
        
        if ComplianceType.AGE_RESTRICTION in violation_types:
            recommendations.append("Add appropriate age restrictions or content warnings")
        
        if ComplianceType.COPYRIGHT in violation_types:
            recommendations.append("Ensure all content is original or properly licensed")
        
        if ComplianceType.PRIVACY_REGULATION in violation_types:
            recommendations.append("Add privacy notices and obtain necessary consents")
        
        if ComplianceType.ACCESSIBILITY in violation_types:
            recommendations.append("Improve content accessibility with captions, alt-text, and descriptions")
        
        return recommendations
    
    def _setup_default_rules(self) -> None:
        """Setup default compliance rules for popular platforms"""
        # YouTube content policy rule
        youtube_content_rule = ComplianceRule(
            rule_id="youtube_content_policy_001",
            platform_id="youtube",
            compliance_type=ComplianceType.CONTENT_POLICY,
            title="YouTube Community Guidelines",
            description="Content must not contain hate speech, harassment, or harmful content",
            requirements=[
                "No hate speech or harassment",
                "No harmful or dangerous content",
                "No spam or misleading content",
                "Appropriate for general audience unless age-restricted"
            ],
            validation_criteria={
                "prohibited_keywords": ["hate", "violence", "spam"],
                "min_title_length": 10
            },
            severity=Severity.HIGH,
            auto_enforceable=True,
            applicable_regions=["global"],
            content_types=["video", "short", "livestream"]
        )
        
        self.rules[youtube_content_rule.rule_id] = youtube_content_rule
        self.platform_rules.setdefault("youtube", []).append(youtube_content_rule.rule_id)
        
        # Instagram advertising standards
        instagram_ad_rule = ComplianceRule(
            rule_id="instagram_advertising_001",
            platform_id="instagram",
            compliance_type=ComplianceType.ADVERTISING_STANDARD,
            title="Instagram Advertising Standards",
            description="Promotional content must be clearly disclosed",
            requirements=[
                "Clear disclosure for sponsored content",
                "No misleading claims",
                "Compliance with FTC guidelines"
            ],
            validation_criteria={
                "required_hashtags": ["#ad", "#sponsored", "#partnership"],
                "disclosure_keywords": ["sponsored", "paid", "advertisement"]
            },
            severity=Severity.MEDIUM,
            auto_enforceable=False,
            applicable_regions=["US", "EU", "CA"],
            content_types=["post", "story", "reel"]
        )
        
        self.rules[instagram_ad_rule.rule_id] = instagram_ad_rule
        self.platform_rules.setdefault("instagram", []).append(instagram_ad_rule.rule_id)
        
        # TikTok age restriction rule
        tiktok_age_rule = ComplianceRule(
            rule_id="tiktok_age_restriction_001",
            platform_id="tiktok",
            compliance_type=ComplianceType.AGE_RESTRICTION,
            title="TikTok Age-Appropriate Content",
            description="Content must be appropriate for users 13+ or include age restrictions",
            requirements=[
                "No adult content",
                "Age-appropriate language",
                "Safe for teen audience"
            ],
            validation_criteria={
                "prohibited_keywords": ["adult", "explicit", "mature"],
                "required_age_rating": "13+"
            },
            severity=Severity.CRITICAL,
            auto_enforceable=True,
            applicable_regions=["global"],
            content_types=["video", "livestream"]
        )
        
        self.rules[tiktok_age_rule.rule_id] = tiktok_age_rule
        self.platform_rules.setdefault("tiktok", []).append(tiktok_age_rule.rule_id)
    
    def _setup_validators(self) -> None:
        """Setup compliance validators"""
        self.validators[ComplianceType.CONTENT_POLICY] = self._validate_content_policy
        self.validators[ComplianceType.ADVERTISING_STANDARD] = self._validate_advertising_standard
        self.validators[ComplianceType.AGE_RESTRICTION] = self._validate_age_restriction
    
    async def _validate_content_policy(
        self,
        content: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """Validate content policy compliance"""
        text = " ".join([
            str(content.get("title", "")),
            str(content.get("description", ""))
        ]).lower()
        
        prohibited = criteria.get("prohibited_keywords", [])
        return not any(keyword.lower() in text for keyword in prohibited)
    
    async def _validate_advertising_standard(
        self,
        content: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """Validate advertising standards compliance"""
        text = " ".join([
            str(content.get("description", "")),
            str(content.get("caption", ""))
        ]).lower()
        
        # Check for required disclosures
        required_hashtags = criteria.get("required_hashtags", [])
        disclosure_keywords = criteria.get("disclosure_keywords", [])
        
        # If content seems promotional, it needs disclosures
        promotional_indicators = ["buy", "purchase", "deal", "discount", "promo"]
        is_promotional = any(indicator in text for indicator in promotional_indicators)
        
        if is_promotional:
            has_hashtag = any(tag.lower() in text for tag in required_hashtags)
            has_disclosure = any(keyword.lower() in text for keyword in disclosure_keywords)
            return has_hashtag or has_disclosure
        
        return True  # Non-promotional content is compliant
    
    async def _validate_age_restriction(
        self,
        content: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """Validate age restriction compliance"""
        text = " ".join([
            str(content.get("title", "")),
            str(content.get("description", ""))
        ]).lower()
        
        prohibited = criteria.get("prohibited_keywords", [])
        age_rating = content.get("age_rating", "13+")
        required_rating = criteria.get("required_age_rating", "13+")
        
        # Check for prohibited content
        has_prohibited_content = any(keyword.lower() in text for keyword in prohibited)
        
        # Check age rating
        appropriate_rating = age_rating == required_rating
        
        return not has_prohibited_content and appropriate_rating


class ComplianceMonitor:
    """Monitors ongoing compliance status"""
    
    def __init__(self):
        self.monitored_content: Dict[str, ComplianceCheck] = {}
        self.violation_history: Dict[str, List[ComplianceViolation]] = {}
    
    async def monitor_compliance(
        self,
        creator_id: str,
        platform_id: str,
        check_interval: int = 3600  # 1 hour
    ) -> None:
        """Start monitoring compliance for creator's content"""
        while True:
            try:
                # Get creator's content
                content_items = await self._fetch_creator_content(creator_id, platform_id)
                
                # Check compliance for each item
                for content in content_items:
                    compliance_check = await self._check_content_compliance(
                        content, platform_id, creator_id
                    )
                    
                    if compliance_check.overall_status != ComplianceStatus.COMPLIANT:
                        await self._handle_compliance_issue(compliance_check)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in compliance monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _fetch_creator_content(
        self,
        creator_id: str,
        platform_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch creator's content for compliance checking"""
        # Simulate content fetching
        return [
            {
                "id": f"content_{i}",
                "title": f"Sample Content {i}",
                "description": f"Description for content {i}",
                "creator_id": creator_id,
                "platform_id": platform_id
            }
            for i in range(5)  # Sample content
        ]
    
    async def _check_content_compliance(
        self,
        content: Dict[str, Any],
        platform_id: str,
        creator_id: str
    ) -> ComplianceCheck:
        """Check compliance for a single content item"""
        rule_engine = ComplianceRuleEngine()
        return await rule_engine.validate_content(content, platform_id, creator_id)
    
    async def _handle_compliance_issue(
        self,
        compliance_check: ComplianceCheck
    ) -> None:
        """Handle detected compliance issues"""
        logger.warning(f"Compliance issue detected: {compliance_check.check_id}")
        
        # Store for tracking
        self.monitored_content[compliance_check.content_id] = compliance_check
        
        # Track violations
        for violation in compliance_check.violations:
            creator_id = violation.creator_id
            if creator_id not in self.violation_history:
                self.violation_history[creator_id] = []
            self.violation_history[creator_id].append(violation)


class PlatformComplianceService:
    """
    ⚖️ Platform Compliance Microservice
    
    Ensures content and operations comply with platform-specific policies,
    legal requirements, and industry standards across multiple platforms.
    
    Features:
    - Multi-platform compliance validation
    - Real-time policy monitoring
    - Automated compliance checking
    - Violation detection and reporting
    - Compliance recommendations
    - Historical compliance tracking
    - Custom rule configuration
    - Integration with legal frameworks
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rule_engine = ComplianceRuleEngine()
        self.monitor = ComplianceMonitor()
        self.is_running = False
        
        # Service configuration
        self.check_interval = self.config.get("check_interval", 3600)  # 1 hour
        self.supported_platforms = self.config.get("supported_platforms", [
            "youtube", "instagram", "tiktok", "twitter", "facebook",
            "linkedin", "spotify", "soundcloud", "medium"
        ])
        
        logger.info("Platform Compliance Service initialized")
    
    async def start(self) -> None:
        """Start the compliance service"""
        try:
            self.is_running = True
            logger.info("Platform Compliance Service started")
            
        except Exception as e:
            logger.error(f"Failed to start Platform Compliance Service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the compliance service"""
        try:
            self.is_running = False
            logger.info("Platform Compliance Service stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop Platform Compliance Service: {e}")
            raise
    
    async def check_content_compliance(
        self,
        content: Dict[str, Any],
        platform_id: str,
        creator_id: str,
        compliance_types: Optional[List[ComplianceType]] = None
    ) -> Dict[str, Any]:
        """Check content compliance against platform rules"""
        try:
            compliance_check = await self.rule_engine.validate_content(
                content=content,
                platform_id=platform_id,
                creator_id=creator_id,
                compliance_types=compliance_types
            )
            
            return {
                "compliance_check": asdict(compliance_check),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check content compliance: {e}")
            raise
    
    async def generate_compliance_report(
        self,
        creator_id: str,
        platform_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for creator"""
        try:
            report_id = str(uuid.uuid4())
            
            # Get violation history
            violations = self.monitor.violation_history.get(creator_id, [])
            period_violations = [
                v for v in violations 
                if start_date <= v.created_at <= end_date
                and v.platform_id == platform_id
            ]
            
            # Calculate metrics
            total_content = 100  # Simulated
            compliant_items = total_content - len(period_violations)
            
            violation_summary = {}
            for violation in period_violations:
                ct = violation.compliance_type
                violation_summary[ct] = violation_summary.get(ct, 0) + 1
            
            critical_violations = len([
                v for v in period_violations 
                if v.severity == Severity.CRITICAL
            ])
            
            resolved_violations = len([
                v for v in period_violations 
                if v.status == ComplianceStatus.COMPLIANT
            ])
            
            pending_actions = len([
                v for v in period_violations 
                if v.status == ComplianceStatus.REQUIRES_ACTION
            ])
            
            compliance_score = (compliant_items / total_content) * 100 if total_content > 0 else 100
            
            report = ComplianceReport(
                report_id=report_id,
                creator_id=creator_id,
                platform_id=platform_id,
                reporting_period={"start": start_date, "end": end_date},
                total_content_items=total_content,
                compliant_items=compliant_items,
                violation_summary=violation_summary,
                critical_violations=critical_violations,
                resolved_violations=resolved_violations,
                pending_actions=pending_actions,
                compliance_score=compliance_score,
                trends={"compliance_trend": 5.2}  # Simulated trend
            )
            
            return {
                "compliance_report": asdict(report),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise
    
    async def get_platform_rules(
        self,
        platform_id: str,
        compliance_types: Optional[List[ComplianceType]] = None
    ) -> Dict[str, Any]:
        """Get compliance rules for a platform"""
        try:
            platform_rule_ids = self.rule_engine.platform_rules.get(platform_id, [])
            
            rules = []
            for rule_id in platform_rule_ids:
                rule = self.rule_engine.rules.get(rule_id)
                if rule and (not compliance_types or rule.compliance_type in compliance_types):
                    rules.append(asdict(rule))
            
            return {
                "platform_id": platform_id,
                "total_rules": len(rules),
                "rules": rules,
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform rules: {e}")
            raise
    
    async def add_custom_rule(
        self,
        platform_id: str,
        compliance_type: ComplianceType,
        title: str,
        description: str,
        requirements: List[str],
        validation_criteria: Dict[str, Any],
        severity: Severity = Severity.MEDIUM
    ) -> str:
        """Add custom compliance rule"""
        try:
            rule_id = str(uuid.uuid4())
            
            rule = ComplianceRule(
                rule_id=rule_id,
                platform_id=platform_id,
                compliance_type=compliance_type,
                title=title,
                description=description,
                requirements=requirements,
                validation_criteria=validation_criteria,
                severity=severity,
                auto_enforceable=False  # Custom rules require manual enforcement
            )
            
            self.rule_engine.rules[rule_id] = rule
            self.rule_engine.platform_rules.setdefault(platform_id, []).append(rule_id)
            
            logger.info(f"Added custom rule {rule_id} for platform {platform_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to add custom rule: {e}")
            raise
    
    async def start_compliance_monitoring(
        self,
        creator_id: str,
        platform_id: str
    ) -> Dict[str, Any]:
        """Start compliance monitoring for creator"""
        try:
            # Start monitoring in background
            asyncio.create_task(
                self.monitor.monitor_compliance(creator_id, platform_id, self.check_interval)
            )
            
            return {
                "message": f"Started compliance monitoring for creator {creator_id} on {platform_id}",
                "check_interval": self.check_interval,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start compliance monitoring: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            "service": "PlatformComplianceService",
            "status": "healthy" if self.is_running else "stopped",
            "supported_platforms": len(self.supported_platforms),
            "total_rules": len(self.rule_engine.rules),
            "monitored_content": len(self.monitor.monitored_content),
            "check_interval": self.check_interval,
            "timestamp": datetime.now().isoformat()
        }


# Service instance
platform_compliance_service = PlatformComplianceService()