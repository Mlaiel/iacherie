"""Compliance Module

Advanced compliance and legal verification system for content creators and influencers.
Ensures adherence to platform policies, legal requirements, and industry standards.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from ..core.base_models import BaseAIModel, ModelConfig
from ..core.exceptions import QualityCheckError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance severity levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL_VIOLATION = "critical_violation"
    BANNED_CONTENT = "banned_content"


class ViolationType(Enum):
    """Types of compliance violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    HARASSMENT_BULLYING = "harassment_bullying"
    HATE_SPEECH = "hate_speech"
    MISINFORMATION = "misinformation"
    SPAM = "spam"
    ADULT_CONTENT = "adult_content"
    VIOLENCE = "violence"
    DANGEROUS_ACTIVITIES = "dangerous_activities"
    ILLEGAL_ACTIVITIES = "illegal_activities"
    FINANCIAL_FRAUD = "financial_fraud"
    IMPERSONATION = "impersonation"
    FAKE_ENGAGEMENT = "fake_engagement"
    UNDISCLOSED_ADVERTISING = "undisclosed_advertising"
    MINOR_SAFETY = "minor_safety"


class Platform(Enum):
    """Supported platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"


class LegalJurisdiction(Enum):
    """Legal jurisdictions"""
    UNITED_STATES = "united_states"
    EUROPEAN_UNION = "european_union"
    UNITED_KINGDOM = "united_kingdom"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GERMANY = "germany"
    FRANCE = "france"
    INTERNATIONAL = "international"


@dataclass
class ComplianceViolation:
    """Individual compliance violation"""
    violation_type: ViolationType
    severity: ComplianceLevel
    description: str
    evidence: List[str] = field(default_factory=list)
    affected_platforms: List[Platform] = field(default_factory=list)
    legal_implications: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)
    risk_score: float = field(default=50.0)
    confidence: float = field(default=0.8)


@dataclass
class PlatformCompliance:
    """Platform-specific compliance analysis"""
    platform: Platform
    compliance_score: float = field(default=100.0)
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Platform-specific metrics
    content_policy_score: float = field(default=100.0)
    community_guidelines_score: float = field(default=100.0)
    copyright_compliance_score: float = field(default=100.0)
    advertising_disclosure_score: float = field(default=100.0)
    
    # Risk assessment
    account_risk_level: ComplianceLevel = field(default=ComplianceLevel.COMPLIANT)
    monetization_eligibility: bool = field(default=True)
    content_removal_risk: float = field(default=0.0)
    account_suspension_risk: float = field(default=0.0)


@dataclass
class LegalCompliance:
    """Legal compliance analysis"""
    jurisdiction: LegalJurisdiction
    overall_compliance_score: float = field(default=100.0)
    
    # Legal areas
    copyright_compliance: float = field(default=100.0)
    privacy_compliance: float = field(default=100.0)
    advertising_law_compliance: float = field(default=100.0)
    data_protection_compliance: float = field(default=100.0)
    consumer_protection_compliance: float = field(default=100.0)
    
    # Specific legal requirements
    gdpr_compliance: float = field(default=100.0)  # EU
    ccpa_compliance: float = field(default=100.0)  # California
    ftc_compliance: float = field(default=100.0)   # US FTC
    
    # Legal risks
    legal_violations: List[ComplianceViolation] = field(default_factory=list)
    lawsuit_risk: float = field(default=0.0)
    regulatory_action_risk: float = field(default=0.0)
    financial_penalty_risk: float = field(default=0.0)


@dataclass
class ContentSafety:
    """Content safety and moderation analysis"""
    safety_score: float = field(default=100.0)
    
    # Safety categories
    violence_safety: float = field(default=100.0)
    hate_speech_safety: float = field(default=100.0)
    harassment_safety: float = field(default=100.0)
    adult_content_safety: float = field(default=100.0)
    minor_safety: float = field(default=100.0)
    
    # Content classification
    age_appropriateness: str = field(default="all_ages")
    content_warnings: List[str] = field(default_factory=list)
    restricted_audiences: List[str] = field(default_factory=list)
    
    # Safety violations
    safety_violations: List[ComplianceViolation] = field(default_factory=list)
    content_moderation_actions: List[str] = field(default_factory=list)


@dataclass
class IntellectualPropertyCompliance:
    """Intellectual property compliance analysis"""
    ip_compliance_score: float = field(default=100.0)
    
    # IP categories
    copyright_score: float = field(default=100.0)
    trademark_score: float = field(default=100.0)
    patent_score: float = field(default=100.0)
    trade_secret_score: float = field(default=100.0)
    
    # Detected IP issues
    copyrighted_content: List[str] = field(default_factory=list)
    trademark_conflicts: List[str] = field(default_factory=list)
    fair_use_analysis: Dict[str, str] = field(default_factory=dict)
    
    # IP violations
    ip_violations: List[ComplianceViolation] = field(default_factory=list)
    takedown_notice_risk: float = field(default=0.0)
    infringement_claims_risk: float = field(default=0.0)


@dataclass
class ComplianceProfile:
    """Comprehensive compliance profile"""
    # Overall compliance
    overall_compliance_score: float = field(default=100.0)
    compliance_level: ComplianceLevel = field(default=ComplianceLevel.COMPLIANT)
    
    # Core compliance areas
    platform_compliance: Dict[Platform, PlatformCompliance] = field(default_factory=dict)
    legal_compliance: LegalCompliance = field(default_factory=LegalCompliance)
    content_safety: ContentSafety = field(default_factory=ContentSafety)
    ip_compliance: IntellectualPropertyCompliance = field(default_factory=IntellectualPropertyCompliance)
    
    # All violations
    all_violations: List[ComplianceViolation] = field(default_factory=list)
    critical_violations: List[ComplianceViolation] = field(default_factory=list)
    
    # Risk assessment
    overall_risk_score: float = field(default=0.0)
    immediate_action_required: bool = field(default=False)
    legal_review_recommended: bool = field(default=False)
    
    # Recommendations
    priority_actions: List[str] = field(default_factory=list)
    compliance_recommendations: List[str] = field(default_factory=list)
    risk_mitigation_strategies: List[str] = field(default_factory=list)


@dataclass
class ComplianceAnalysisMetrics:
    """Compliance analysis metrics container"""
    profile: ComplianceProfile = field(default_factory=ComplianceProfile)
    
    # Analysis metadata
    platforms_analyzed: List[Platform] = field(default_factory=list)
    jurisdictions_covered: List[LegalJurisdiction] = field(default_factory=list)
    content_types_analyzed: List[str] = field(default_factory=list)
    
    # Detection statistics
    total_checks_performed: int = field(default=0)
    violations_detected: int = field(default=0)
    warnings_issued: int = field(default=0)
    false_positive_rate: float = field(default=5.0)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class ComplianceAnalyzer(BaseAIModel):
    """
    Professional Compliance Analyzer
    
    Provides comprehensive compliance verification for:
    - Content creators and influencers
    - Digital marketing agencies
    - Brand safety teams
    - Legal compliance departments
    - Platform risk management
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize compliance analyzer"""
        super().__init__(config or ModelConfig(
            model_name="compliance_analyzer",
            provider="internal",
            version="1.0.0"
        ))
        
        self.performance_monitor = performance_monitor
        self.metrics_collector = metrics_collector
        
        # Initialize compliance databases
        self._initialize_compliance_rules()
        self._initialize_violation_patterns()
        self._initialize_legal_requirements()
        
        logger.info("Compliance Analyzer initialized successfully")
    
    def _initialize_compliance_rules(self):
        """Initialize platform compliance rules"""
        self.platform_rules = {
            Platform.INSTAGRAM: {
                'max_hashtags': 30,
                'prohibited_content': ['nudity', 'hate_speech', 'violence', 'harassment'],
                'advertising_disclosure_required': True,
                'min_age_requirement': 13,
                'copyright_enforcement': 'strict'
            },
            Platform.TIKTOK: {
                'max_video_length': 600,  # 10 minutes
                'prohibited_content': ['dangerous_activities', 'hate_speech', 'harassment'],
                'advertising_disclosure_required': True,
                'min_age_requirement': 13,
                'copyright_enforcement': 'strict'
            },
            Platform.YOUTUBE: {
                'max_video_length': 43200,  # 12 hours
                'prohibited_content': ['hate_speech', 'harassment', 'misinformation'],
                'advertising_disclosure_required': True,
                'min_age_requirement': 13,
                'copyright_enforcement': 'very_strict'
            },
            Platform.LINKEDIN: {
                'professional_content_only': True,
                'prohibited_content': ['adult_content', 'hate_speech', 'spam'],
                'advertising_disclosure_required': True,
                'min_age_requirement': 16,
                'copyright_enforcement': 'moderate'
            }
        }
    
    def _initialize_violation_patterns(self):
        """Initialize violation detection patterns"""
        self.violation_patterns = {
            ViolationType.HATE_SPEECH: {
                'keywords': ['hate', 'racist', 'nazi', 'terrorist', 'kill'],
                'severity': ComplianceLevel.CRITICAL_VIOLATION,
                'confidence_threshold': 0.7
            },
            ViolationType.HARASSMENT_BULLYING: {
                'keywords': ['bully', 'harass', 'threaten', 'stalk', 'abuse'],
                'severity': ComplianceLevel.VIOLATION,
                'confidence_threshold': 0.6
            },
            ViolationType.SPAM: {
                'patterns': [r'click\s+here', r'buy\s+now', r'limited\s+time'],
                'severity': ComplianceLevel.WARNING,
                'confidence_threshold': 0.5
            },
            ViolationType.UNDISCLOSED_ADVERTISING: {
                'keywords': ['sponsored', 'paid', 'affiliate', 'partnership'],
                'required_disclosures': ['#ad', '#sponsored', '#partnership'],
                'severity': ComplianceLevel.VIOLATION,
                'confidence_threshold': 0.8
            },
            ViolationType.COPYRIGHT_INFRINGEMENT: {
                'indicators': ['copyrighted_music', 'branded_content', 'trademarked_logos'],
                'severity': ComplianceLevel.CRITICAL_VIOLATION,
                'confidence_threshold': 0.9
            },
            ViolationType.MISINFORMATION: {
                'keywords': ['fake_news', 'conspiracy', 'hoax', 'false_claim'],
                'severity': ComplianceLevel.VIOLATION,
                'confidence_threshold': 0.6
            }
        }
    
    def _initialize_legal_requirements(self):
        """Initialize legal requirements by jurisdiction"""
        self.legal_requirements = {
            LegalJurisdiction.UNITED_STATES: {
                'ftc_disclosure_required': True,
                'coppa_compliance': True,
                'ada_compliance': True,
                'privacy_policy_required': True
            },
            LegalJurisdiction.EUROPEAN_UNION: {
                'gdpr_compliance': True,
                'cookie_consent_required': True,
                'right_to_be_forgotten': True,
                'data_portability': True
            },
            LegalJurisdiction.UNITED_KINGDOM: {
                'uk_gdpr_compliance': True,
                'advertising_standards_authority': True,
                'ofcom_compliance': True
            }
        }
    
    @monitor_performance
    async def analyze_compliance(
        self,
        content_data: Dict[str, Any],
        platforms: Optional[List[Platform]] = None,
        jurisdictions: Optional[List[LegalJurisdiction]] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive compliance analysis
        
        Args:
            content_data: Content information and metadata
            platforms: List of platforms to check compliance for
            jurisdictions: Legal jurisdictions to consider
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete compliance analysis
            
        Raises:
            QualityCheckError: If analysis fails
            QualityCheckError: If critical violations are detected
        """
        start_time = datetime.now()
        
        try:
            if not content_data:
                raise QualityCheckError("Empty content data provided")
            
            # Set defaults
            platforms = platforms or [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE]
            jurisdictions = jurisdictions or [LegalJurisdiction.UNITED_STATES, LegalJurisdiction.EUROPEAN_UNION]
            
            # Create compliance profile
            profile = ComplianceProfile()
            
            # Perform comprehensive compliance analysis
            await self._analyze_content_safety(content_data, profile)
            await self._analyze_intellectual_property(content_data, profile)
            await self._analyze_platform_compliance(content_data, platforms, profile)
            await self._analyze_legal_compliance(content_data, jurisdictions, profile)
            
            # Calculate overall compliance
            self._calculate_overall_compliance(profile)
            
            # Generate recommendations
            self._generate_compliance_recommendations(profile)
            
            # Check for critical violations
            self._assess_critical_violations(profile)
            
            # Create metrics
            metrics = ComplianceAnalysisMetrics(profile=profile)
            metrics.platforms_analyzed = platforms
            metrics.jurisdictions_covered = jurisdictions
            await self._calculate_analysis_metrics(content_data, profile, metrics)
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile, content_data)
            
            # Prepare result
            result = {
                'overall_compliance_score': profile.overall_compliance_score,
                'compliance_level': profile.compliance_level.value,
                'confidence': metrics.confidence,
                'content_safety': {
                    'safety_score': profile.content_safety.safety_score,
                    'age_appropriateness': profile.content_safety.age_appropriateness,
                    'content_warnings': profile.content_safety.content_warnings,
                    'violence_safety': profile.content_safety.violence_safety,
                    'hate_speech_safety': profile.content_safety.hate_speech_safety,
                    'harassment_safety': profile.content_safety.harassment_safety,
                    'adult_content_safety': profile.content_safety.adult_content_safety,
                    'minor_safety': profile.content_safety.minor_safety
                },
                'intellectual_property': {
                    'ip_compliance_score': profile.ip_compliance.ip_compliance_score,
                    'copyright_score': profile.ip_compliance.copyright_score,
                    'trademark_score': profile.ip_compliance.trademark_score,
                    'copyrighted_content': profile.ip_compliance.copyrighted_content,
                    'trademark_conflicts': profile.ip_compliance.trademark_conflicts,
                    'takedown_notice_risk': profile.ip_compliance.takedown_notice_risk
                },
                'platform_compliance': {
                    platform.value: {
                        'compliance_score': compliance.compliance_score,
                        'content_policy_score': compliance.content_policy_score,
                        'community_guidelines_score': compliance.community_guidelines_score,
                        'copyright_compliance_score': compliance.copyright_compliance_score,
                        'advertising_disclosure_score': compliance.advertising_disclosure_score,
                        'account_risk_level': compliance.account_risk_level.value,
                        'monetization_eligibility': compliance.monetization_eligibility,
                        'content_removal_risk': compliance.content_removal_risk,
                        'account_suspension_risk': compliance.account_suspension_risk,
                        'violations': [
                            {
                                'type': v.violation_type.value,
                                'severity': v.severity.value,
                                'description': v.description,
                                'risk_score': v.risk_score,
                                'remediation_steps': v.remediation_steps
                            } for v in compliance.violations
                        ],
                        'warnings': compliance.warnings,
                        'recommendations': compliance.recommendations
                    } for platform, compliance in profile.platform_compliance.items()
                },
                'legal_compliance': {
                    'overall_compliance_score': profile.legal_compliance.overall_compliance_score,
                    'copyright_compliance': profile.legal_compliance.copyright_compliance,
                    'privacy_compliance': profile.legal_compliance.privacy_compliance,
                    'advertising_law_compliance': profile.legal_compliance.advertising_law_compliance,
                    'data_protection_compliance': profile.legal_compliance.data_protection_compliance,
                    'gdpr_compliance': profile.legal_compliance.gdpr_compliance,
                    'ccpa_compliance': profile.legal_compliance.ccpa_compliance,
                    'ftc_compliance': profile.legal_compliance.ftc_compliance,
                    'lawsuit_risk': profile.legal_compliance.lawsuit_risk,
                    'regulatory_action_risk': profile.legal_compliance.regulatory_action_risk,
                    'financial_penalty_risk': profile.legal_compliance.financial_penalty_risk
                },
                'violations_summary': {
                    'total_violations': len(profile.all_violations),
                    'critical_violations': len(profile.critical_violations),
                    'violation_types': list(set([v.violation_type.value for v in profile.all_violations])),
                    'affected_platforms': list(set([
                        platform.value for v in profile.all_violations 
                        for platform in v.affected_platforms
                    ]))
                },
                'risk_assessment': {
                    'overall_risk_score': profile.overall_risk_score,
                    'immediate_action_required': profile.immediate_action_required,
                    'legal_review_recommended': profile.legal_review_recommended
                },
                'recommendations': {
                    'priority_actions': profile.priority_actions,
                    'compliance_recommendations': profile.compliance_recommendations,
                    'risk_mitigation_strategies': profile.risk_mitigation_strategies
                },
                'analysis_statistics': {
                    'total_checks_performed': metrics.total_checks_performed,
                    'violations_detected': metrics.violations_detected,
                    'warnings_issued': metrics.warnings_issued,
                    'false_positive_rate': metrics.false_positive_rate,
                    'processing_time': metrics.processing_time
                }
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="compliance_analysis_completed",
                value=1,
                metadata={
                    'compliance_score': profile.overall_compliance_score,
                    'violations_count': len(profile.all_violations),
                    'critical_violations': len(profile.critical_violations),
                    'processing_time': metrics.processing_time
                }
            )
            
            # Check for critical violations
            if profile.compliance_level in [ComplianceLevel.CRITICAL_VIOLATION, ComplianceLevel.BANNED_CONTENT]:
                logger.warning(f"Critical compliance violations detected: {profile.compliance_level.value}")
            
            logger.info(f"Compliance analysis completed: {profile.overall_compliance_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("compliance_analysis_error", str(e))
            raise QualityCheckError(f"Compliance analysis failed: {str(e)}") from e
    
    async def _analyze_content_safety(self, content_data: Dict[str, Any], profile: ComplianceProfile):
        """Analyze content safety and moderation requirements"""
        try:
            text_content = content_data.get('text', '').lower()
            media_type = content_data.get('media_type', 'unknown')
            metadata = content_data.get('metadata', {})
            
            safety = profile.content_safety
            safety_violations = []
            
            # Violence safety analysis
            violence_keywords = [
                'violence', 'kill', 'murder', 'assault', 'fight', 'blood',
                'weapon', 'gun', 'knife', 'bomb', 'terror', 'war'
            ]
            
            violence_score = 100.0
            for keyword in violence_keywords:
                if keyword in text_content:
                    violence_score -= 15
                    if violence_score <= 70:
                        violation = ComplianceViolation(
                            violation_type=ViolationType.VIOLENCE,
                            severity=ComplianceLevel.VIOLATION,
                            description=f"Violent content detected: {keyword}",
                            evidence=[keyword],
                            risk_score=30 + (100 - violence_score)
                        )
                        safety_violations.append(violation)
            
            safety.violence_safety = max(0, violence_score)
            
            # Hate speech analysis
            hate_keywords = [
                'hate', 'racist', 'nazi', 'terrorist', 'supremacist',
                'genocide', 'ethnic cleansing', 'discrimination'
            ]
            
            hate_score = 100.0
            for keyword in hate_keywords:
                if keyword in text_content:
                    hate_score -= 25
                    violation = ComplianceViolation(
                        violation_type=ViolationType.HATE_SPEECH,
                        severity=ComplianceLevel.CRITICAL_VIOLATION,
                        description=f"Hate speech detected: {keyword}",
                        evidence=[keyword],
                        risk_score=50 + (100 - hate_score)
                    )
                    safety_violations.append(violation)
            
            safety.hate_speech_safety = max(0, hate_score)
            
            # Harassment analysis
            harassment_keywords = [
                'bully', 'harass', 'threaten', 'stalk', 'abuse',
                'intimidate', 'cyberbully', 'doxx'
            ]
            
            harassment_score = 100.0
            for keyword in harassment_keywords:
                if keyword in text_content:
                    harassment_score -= 20
                    if harassment_score <= 60:
                        violation = ComplianceViolation(
                            violation_type=ViolationType.HARASSMENT_BULLYING,
                            severity=ComplianceLevel.VIOLATION,
                            description=f"Harassment content detected: {keyword}",
                            evidence=[keyword],
                            risk_score=40 + (100 - harassment_score)
                        )
                        safety_violations.append(violation)
            
            safety.harassment_safety = max(0, harassment_score)
            
            # Adult content analysis
            adult_keywords = [
                'adult', 'explicit', 'sexual', 'nude', 'porn',
                'erotic', 'xxx', 'mature', 'nsfw'
            ]
            
            adult_score = 100.0
            for keyword in adult_keywords:
                if keyword in text_content:
                    adult_score -= 20
                    if adult_score <= 70:
                        violation = ComplianceViolation(
                            violation_type=ViolationType.ADULT_CONTENT,
                            severity=ComplianceLevel.WARNING,
                            description=f"Adult content indicator: {keyword}",
                            evidence=[keyword],
                            risk_score=20 + (100 - adult_score)
                        )
                        safety_violations.append(violation)
            
            safety.adult_content_safety = max(0, adult_score)
            
            # Minor safety analysis
            minor_keywords = [
                'child', 'minor', 'kid', 'teen', 'young', 'school',
                'playground', 'family'
            ]
            
            minor_safety_score = 100.0
            has_minor_content = any(keyword in text_content for keyword in minor_keywords)
            
            if has_minor_content:
                # Additional scrutiny for content involving minors
                if any(keyword in text_content for keyword in adult_keywords):
                    minor_safety_score = 0
                    violation = ComplianceViolation(
                        violation_type=ViolationType.MINOR_SAFETY,
                        severity=ComplianceLevel.CRITICAL_VIOLATION,
                        description="Adult content in context involving minors",
                        evidence=["minor_content", "adult_content"],
                        risk_score=100
                    )
                    safety_violations.append(violation)
            
            safety.minor_safety = minor_safety_score
            
            # Age appropriateness
            if safety.adult_content_safety < 80:
                safety.age_appropriateness = "18+"
                safety.content_warnings.append("Adult content")
            elif safety.violence_safety < 70:
                safety.age_appropriateness = "13+"
                safety.content_warnings.append("Violence")
            else:
                safety.age_appropriateness = "all_ages"
            
            # Overall safety score
            safety_scores = [
                safety.violence_safety,
                safety.hate_speech_safety,
                safety.harassment_safety,
                safety.adult_content_safety,
                safety.minor_safety
            ]
            
            safety.safety_score = min(safety_scores)
            safety.safety_violations = safety_violations
            
            # Content moderation actions
            if safety.safety_score < 50:
                safety.content_moderation_actions.append("Manual review required")
            if safety.hate_speech_safety < 70:
                safety.content_moderation_actions.append("Hate speech review")
            if safety.minor_safety < 100:
                safety.content_moderation_actions.append("Minor safety review")
            
        except Exception as e:
            logger.warning(f"Content safety analysis failed: {str(e)}")
    
    async def _analyze_intellectual_property(self, content_data: Dict[str, Any], profile: ComplianceProfile):
        """Analyze intellectual property compliance"""
        try:
            text_content = content_data.get('text', '').lower()
            media_info = content_data.get('media_info', {})
            
            ip_compliance = profile.ip_compliance
            ip_violations = []
            
            # Copyright analysis
            copyright_indicators = [
                'copyrighted', 'all rights reserved', '©', 'copyright',
                'music', 'song', 'artist', 'album', 'track'
            ]
            
            copyright_score = 100.0
            copyrighted_content = []
            
            for indicator in copyright_indicators:
                if indicator in text_content:
                    copyright_score -= 10
                    copyrighted_content.append(indicator)
            
            # Check for music/audio copyright
            if media_info.get('has_music', False):
                music_info = media_info.get('music_info', {})
                if not music_info.get('royalty_free', False):
                    copyright_score -= 30
                    copyrighted_content.append("background_music")
                    
                    violation = ComplianceViolation(
                        violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
                        severity=ComplianceLevel.CRITICAL_VIOLATION,
                        description="Potentially copyrighted music detected",
                        evidence=["background_music"],
                        affected_platforms=[Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE],
                        risk_score=70
                    )
                    ip_violations.append(violation)
            
            ip_compliance.copyright_score = max(0, copyright_score)
            ip_compliance.copyrighted_content = copyrighted_content
            
            # Trademark analysis
            trademark_indicators = [
                'trademark', '™', '®', 'brand', 'logo', 'company name'
            ]
            
            trademark_score = 100.0
            trademark_conflicts = []
            
            # Known trademark keywords (simplified)
            known_trademarks = [
                'nike', 'apple', 'google', 'facebook', 'instagram',
                'youtube', 'microsoft', 'amazon', 'coca-cola', 'mcdonald'
            ]
            
            for trademark in known_trademarks:
                if trademark in text_content:
                    trademark_score -= 15
                    trademark_conflicts.append(trademark)
                    
                    violation = ComplianceViolation(
                        violation_type=ViolationType.TRADEMARK_VIOLATION,
                        severity=ComplianceLevel.WARNING,
                        description=f"Trademark reference detected: {trademark}",
                        evidence=[trademark],
                        risk_score=25
                    )
                    ip_violations.append(violation)
            
            ip_compliance.trademark_score = max(0, trademark_score)
            ip_compliance.trademark_conflicts = trademark_conflicts
            
            # Fair use analysis (simplified)
            fair_use_factors = {
                'educational_purpose': 'education' in text_content or 'learn' in text_content,
                'commentary_or_criticism': 'review' in text_content or 'opinion' in text_content,
                'parody': 'parody' in text_content or 'satire' in text_content,
                'news_reporting': 'news' in text_content or 'report' in text_content
            }
            
            ip_compliance.fair_use_analysis = {
                factor: "present" if present else "absent"
                for factor, present in fair_use_factors.items()
            }
            
            # Overall IP compliance
            ip_scores = [
                ip_compliance.copyright_score,
                ip_compliance.trademark_score,
                100,  # Patent score (default)
                100   # Trade secret score (default)
            ]
            
            ip_compliance.ip_compliance_score = min(ip_scores)
            ip_compliance.ip_violations = ip_violations
            
            # Risk assessment
            if ip_compliance.copyright_score < 70:
                ip_compliance.takedown_notice_risk = 40.0
            if ip_compliance.trademark_score < 60:
                ip_compliance.infringement_claims_risk = 30.0
            
        except Exception as e:
            logger.warning(f"IP compliance analysis failed: {str(e)}")
    
    async def _analyze_platform_compliance(self, content_data: Dict[str, Any], platforms: List[Platform], profile: ComplianceProfile):
        """Analyze platform-specific compliance"""
        try:
            text_content = content_data.get('text', '')
            hashtags = content_data.get('hashtags', [])
            media_info = content_data.get('media_info', {})
            
            for platform in platforms:
                compliance = PlatformCompliance(platform=platform)
                platform_violations = []
                warnings = []
                recommendations = []
                
                # Get platform rules
                rules = self.platform_rules.get(platform, {})
                
                # Content policy compliance
                content_policy_score = 100.0
                
                # Check prohibited content
                prohibited = rules.get('prohibited_content', [])
                for content_type in prohibited:
                    if content_type.replace('_', ' ') in text_content.lower():
                        content_policy_score -= 20
                        violation = ComplianceViolation(
                            violation_type=ViolationType(content_type.lower()),
                            severity=ComplianceLevel.VIOLATION,
                            description=f"Prohibited content for {platform.value}: {content_type}",
                            affected_platforms=[platform],
                            risk_score=40
                        )
                        platform_violations.append(violation)
                
                # Platform-specific checks
                if platform == Platform.INSTAGRAM:
                    # Hashtag limit
                    if len(hashtags) > rules.get('max_hashtags', 30):
                        content_policy_score -= 10
                        warnings.append("Exceeds hashtag limit")
                    
                elif platform == Platform.TIKTOK:
                    # Video length check
                    video_duration = media_info.get('duration', 0)
                    if video_duration > rules.get('max_video_length', 600):
                        content_policy_score -= 15
                        warnings.append("Video exceeds maximum length")
                
                elif platform == Platform.YOUTUBE:
                    # Copyright enforcement
                    if media_info.get('has_music', False) and not media_info.get('royalty_free', False):
                        content_policy_score -= 25
                        violation = ComplianceViolation(
                            violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
                            severity=ComplianceLevel.CRITICAL_VIOLATION,
                            description="Copyright music detected on YouTube",
                            affected_platforms=[platform],
                            risk_score=60
                        )
                        platform_violations.append(violation)
                
                compliance.content_policy_score = max(0, content_policy_score)
                
                # Community guidelines compliance
                community_score = profile.content_safety.safety_score
                compliance.community_guidelines_score = community_score
                
                # Copyright compliance
                copyright_score = profile.ip_compliance.copyright_score
                compliance.copyright_compliance_score = copyright_score
                
                # Advertising disclosure compliance
                disclosure_score = 100.0
                advertising_keywords = ['sponsored', 'ad', 'affiliate', 'partnership', 'paid']
                
                has_advertising = any(keyword in text_content.lower() for keyword in advertising_keywords)
                disclosure_present = any(disclosure in text_content.lower() for disclosure in ['#ad', '#sponsored', '#partnership'])
                
                if has_advertising and not disclosure_present:
                    disclosure_score = 30
                    violation = ComplianceViolation(
                        violation_type=ViolationType.UNDISCLOSED_ADVERTISING,
                        severity=ComplianceLevel.VIOLATION,
                        description="Advertising content without proper disclosure",
                        affected_platforms=[platform],
                        risk_score=50,
                        remediation_steps=["Add #ad or #sponsored disclosure"]
                    )
                    platform_violations.append(violation)
                
                compliance.advertising_disclosure_score = disclosure_score
                
                # Overall platform compliance
                platform_scores = [
                    compliance.content_policy_score,
                    compliance.community_guidelines_score,
                    compliance.copyright_compliance_score,
                    compliance.advertising_disclosure_score
                ]
                
                compliance.compliance_score = min(platform_scores)
                
                # Risk assessment
                if compliance.compliance_score < 60:
                    compliance.account_risk_level = ComplianceLevel.VIOLATION
                    compliance.content_removal_risk = 40.0
                    compliance.account_suspension_risk = 20.0
                    compliance.monetization_eligibility = False
                elif compliance.compliance_score < 80:
                    compliance.account_risk_level = ComplianceLevel.WARNING
                    compliance.content_removal_risk = 15.0
                    compliance.account_suspension_risk = 5.0
                
                # Generate recommendations
                if compliance.advertising_disclosure_score < 100:
                    recommendations.append("Add proper advertising disclosures")
                if compliance.copyright_compliance_score < 80:
                    recommendations.append("Use only royalty-free music and content")
                if len(warnings) > 0:
                    recommendations.append("Address content policy warnings")
                
                compliance.violations = platform_violations
                compliance.warnings = warnings
                compliance.recommendations = recommendations
                
                profile.platform_compliance[platform] = compliance
                profile.all_violations.extend(platform_violations)
            
        except Exception as e:
            logger.warning(f"Platform compliance analysis failed: {str(e)}")
    
    async def _analyze_legal_compliance(self, content_data: Dict[str, Any], jurisdictions: List[LegalJurisdiction], profile: ComplianceProfile):
        """Analyze legal compliance requirements"""
        try:
            text_content = content_data.get('text', '')
            user_data = content_data.get('user_data', {})
            
            # Initialize legal compliance for primary jurisdiction
            primary_jurisdiction = jurisdictions[0] if jurisdictions else LegalJurisdiction.INTERNATIONAL
            legal = profile.legal_compliance
            legal.jurisdiction = primary_jurisdiction
            
            legal_violations = []
            
            # Privacy compliance
            privacy_score = 100.0
            privacy_keywords = ['personal data', 'email', 'phone', 'address', 'private']
            
            for keyword in privacy_keywords:
                if keyword in text_content.lower():
                    privacy_score -= 10
            
            # Check for GDPR compliance (EU)
            if LegalJurisdiction.EUROPEAN_UNION in jurisdictions:
                gdpr_requirements = ['consent', 'privacy policy', 'data protection']
                gdpr_score = 100.0
                
                for requirement in gdpr_requirements:
                    if requirement not in text_content.lower():
                        gdpr_score -= 15
                
                if user_data.get('collects_personal_data', False) and not user_data.get('has_privacy_policy', False):
                    gdpr_score -= 40
                    violation = ComplianceViolation(
                        violation_type=ViolationType.PRIVACY_VIOLATION,
                        severity=ComplianceLevel.VIOLATION,
                        description="GDPR violation: Missing privacy policy",
                        legal_implications=["Regulatory fines up to 4% of revenue"],
                        risk_score=60
                    )
                    legal_violations.append(violation)
                
                legal.gdpr_compliance = max(0, gdpr_score)
            
            # FTC compliance (US)
            if LegalJurisdiction.UNITED_STATES in jurisdictions:
                ftc_score = 100.0
                
                # Check for proper advertising disclosures
                has_advertising = any(word in text_content.lower() for word in ['sponsored', 'affiliate', 'paid'])
                has_disclosure = any(disclosure in text_content.lower() for disclosure in ['#ad', '#sponsored'])
                
                if has_advertising and not has_disclosure:
                    ftc_score = 40
                    violation = ComplianceViolation(
                        violation_type=ViolationType.UNDISCLOSED_ADVERTISING,
                        severity=ComplianceLevel.VIOLATION,
                        description="FTC violation: Undisclosed advertising",
                        legal_implications=["FTC fines and penalties"],
                        risk_score=50
                    )
                    legal_violations.append(violation)
                
                legal.ftc_compliance = max(0, ftc_score)
            
            # Copyright law compliance
            copyright_compliance = profile.ip_compliance.copyright_score
            legal.copyright_compliance = copyright_compliance
            
            # Advertising law compliance
            advertising_compliance = 100.0
            misleading_keywords = ['guaranteed', 'miracle', 'instant', 'secret', 'scam']
            
            for keyword in misleading_keywords:
                if keyword in text_content.lower():
                    advertising_compliance -= 20
            
            legal.advertising_law_compliance = max(0, advertising_compliance)
            
            # Data protection compliance
            data_protection_score = 100.0
            if user_data.get('collects_data', False):
                required_protections = ['encryption', 'secure_storage', 'access_control']
                for protection in required_protections:
                    if not user_data.get(protection, False):
                        data_protection_score -= 20
            
            legal.data_protection_compliance = data_protection_score
            legal.privacy_compliance = privacy_score
            
            # Consumer protection compliance
            consumer_protection_score = 100.0
            if 'refund' in text_content.lower() and 'policy' not in text_content.lower():
                consumer_protection_score -= 20
            
            legal.consumer_protection_compliance = consumer_protection_score
            
            # Overall legal compliance
            legal_scores = [
                legal.copyright_compliance,
                legal.privacy_compliance,
                legal.advertising_law_compliance,
                legal.data_protection_compliance,
                legal.consumer_protection_compliance
            ]
            
            legal.overall_compliance_score = min(legal_scores)
            legal.legal_violations = legal_violations
            
            # Risk assessment
            if legal.overall_compliance_score < 60:
                legal.lawsuit_risk = 30.0
                legal.regulatory_action_risk = 40.0
                legal.financial_penalty_risk = 25.0
            elif legal.overall_compliance_score < 80:
                legal.lawsuit_risk = 10.0
                legal.regulatory_action_risk = 15.0
                legal.financial_penalty_risk = 10.0
            
            profile.all_violations.extend(legal_violations)
            
        except Exception as e:
            logger.warning(f"Legal compliance analysis failed: {str(e)}")
    
    def _calculate_overall_compliance(self, profile: ComplianceProfile):
        """Calculate overall compliance score and level"""
        try:
            # Collect all compliance scores
            scores = []
            
            # Content safety (high weight)
            scores.extend([profile.content_safety.safety_score] * 3)
            
            # IP compliance (high weight)
            scores.extend([profile.ip_compliance.ip_compliance_score] * 2)
            
            # Legal compliance (high weight)
            scores.extend([profile.legal_compliance.overall_compliance_score] * 2)
            
            # Platform compliance (medium weight)
            for platform_compliance in profile.platform_compliance.values():
                scores.append(platform_compliance.compliance_score)
            
            # Calculate weighted average
            profile.overall_compliance_score = np.mean(scores) if scores else 100.0
            
            # Determine compliance level
            critical_violations = [v for v in profile.all_violations 
                                 if v.severity == ComplianceLevel.CRITICAL_VIOLATION]
            profile.critical_violations = critical_violations
            
            if len(critical_violations) > 0:
                profile.compliance_level = ComplianceLevel.CRITICAL_VIOLATION
            elif profile.overall_compliance_score < 50:
                profile.compliance_level = ComplianceLevel.VIOLATION
            elif profile.overall_compliance_score < 80:
                profile.compliance_level = ComplianceLevel.WARNING
            else:
                profile.compliance_level = ComplianceLevel.COMPLIANT
            
            # Calculate overall risk score
            risk_factors = [
                len(profile.all_violations) * 10,
                len(critical_violations) * 25,
                (100 - profile.overall_compliance_score)
            ]
            
            profile.overall_risk_score = min(100, sum(risk_factors))
            
        except Exception as e:
            logger.warning(f"Overall compliance calculation failed: {str(e)}")
    
    def _generate_compliance_recommendations(self, profile: ComplianceProfile):
        """Generate compliance recommendations"""
        try:
            priority_actions = []
            compliance_recommendations = []
            risk_mitigation = []
            
            # Critical violations - immediate action required
            if profile.critical_violations:
                profile.immediate_action_required = True
                priority_actions.append("Address critical compliance violations immediately")
                
                for violation in profile.critical_violations:
                    priority_actions.extend(violation.remediation_steps)
            
            # Legal review recommendations
            if profile.legal_compliance.overall_compliance_score < 70:
                profile.legal_review_recommended = True
                priority_actions.append("Conduct legal compliance review")
            
            # Content safety recommendations
            if profile.content_safety.safety_score < 80:
                compliance_recommendations.append("Review content for safety compliance")
                if profile.content_safety.hate_speech_safety < 90:
                    compliance_recommendations.append("Remove or modify hate speech content")
                if profile.content_safety.violence_safety < 80:
                    compliance_recommendations.append("Reduce violent content elements")
            
            # IP compliance recommendations
            if profile.ip_compliance.ip_compliance_score < 80:
                compliance_recommendations.append("Address intellectual property concerns")
                if profile.ip_compliance.copyrighted_content:
                    compliance_recommendations.append("Replace copyrighted content with original or licensed alternatives")
                if profile.ip_compliance.trademark_conflicts:
                    compliance_recommendations.append("Review trademark usage and add disclaimers if necessary")
            
            # Platform-specific recommendations
            for platform, compliance in profile.platform_compliance.items():
                if compliance.compliance_score < 80:
                    compliance_recommendations.append(f"Improve {platform.value} compliance")
                    compliance_recommendations.extend(compliance.recommendations)
            
            # Risk mitigation strategies
            if profile.overall_risk_score > 30:
                risk_mitigation.append("Implement compliance monitoring system")
                risk_mitigation.append("Establish content review process")
                risk_mitigation.append("Create compliance documentation")
            
            if len(profile.all_violations) > 3:
                risk_mitigation.append("Conduct comprehensive compliance audit")
            
            # Legal protection strategies
            if profile.legal_compliance.lawsuit_risk > 20:
                risk_mitigation.append("Consider legal liability insurance")
                risk_mitigation.append("Establish terms of service and privacy policy")
            
            profile.priority_actions = priority_actions
            profile.compliance_recommendations = compliance_recommendations
            profile.risk_mitigation_strategies = risk_mitigation
            
        except Exception as e:
            logger.warning(f"Compliance recommendations generation failed: {str(e)}")
    
    def _assess_critical_violations(self, profile: ComplianceProfile):
        """Assess and handle critical violations"""
        try:
            critical_types = [
                ViolationType.HATE_SPEECH,
                ViolationType.COPYRIGHT_INFRINGEMENT,
                ViolationType.MINOR_SAFETY,
                ViolationType.ILLEGAL_ACTIVITIES
            ]
            
            for violation in profile.all_violations:
                if violation.violation_type in critical_types:
                    profile.immediate_action_required = True
                    
                    # Add to critical violations if not already there
                    if violation not in profile.critical_violations:
                        profile.critical_violations.append(violation)
            
            # Check for banned content patterns
            banned_indicators = 0
            if profile.content_safety.hate_speech_safety < 50:
                banned_indicators += 1
            if profile.content_safety.minor_safety < 50:
                banned_indicators += 1
            if len(profile.critical_violations) >= 3:
                banned_indicators += 1
            
            if banned_indicators >= 2:
                profile.compliance_level = ComplianceLevel.BANNED_CONTENT
                profile.immediate_action_required = True
            
        except Exception as e:
            logger.warning(f"Critical violation assessment failed: {str(e)}")
    
    async def _calculate_analysis_metrics(self, content_data: Dict[str, Any], profile: ComplianceProfile, metrics: ComplianceAnalysisMetrics):
        """Calculate analysis metrics and statistics"""
        try:
            # Count total checks performed
            checks_performed = 0
            checks_performed += len(self.violation_patterns)  # Pattern checks
            checks_performed += len(profile.platform_compliance) * 5  # Platform checks
            checks_performed += 10  # Legal checks
            checks_performed += 5   # IP checks
            checks_performed += 5   # Safety checks
            
            metrics.total_checks_performed = checks_performed
            metrics.violations_detected = len(profile.all_violations)
            
            # Count warnings
            warnings_count = 0
            for platform_compliance in profile.platform_compliance.values():
                warnings_count += len(platform_compliance.warnings)
            
            metrics.warnings_issued = warnings_count
            
            # Estimate false positive rate (simplified)
            confidence_scores = [v.confidence for v in profile.all_violations if hasattr(v, 'confidence')]
            if confidence_scores:
                avg_confidence = np.mean(confidence_scores)
                metrics.false_positive_rate = (1 - avg_confidence) * 10  # Convert to percentage
            else:
                metrics.false_positive_rate = 5.0  # Default
            
            # Content types analyzed
            content_types = []
            if content_data.get('text'):
                content_types.append('text')
            if content_data.get('media_type'):
                content_types.append(content_data['media_type'])
            if content_data.get('hashtags'):
                content_types.append('hashtags')
            
            metrics.content_types_analyzed = content_types
            
        except Exception as e:
            logger.warning(f"Analysis metrics calculation failed: {str(e)}")
    
    def _calculate_confidence(self, profile: ComplianceProfile, content_data: Dict[str, Any]) -> float:
        """Calculate analysis confidence score"""
        confidence = 0.85  # Base confidence
        
        # Adjust based on content completeness
        if content_data.get('text'):
            confidence += 0.05
        if content_data.get('media_info'):
            confidence += 0.05
        if content_data.get('hashtags'):
            confidence += 0.03
        
        # Adjust based on analysis depth
        if len(profile.platform_compliance) > 2:
            confidence += 0.05
        
        # Adjust based on violation confidence
        if profile.all_violations:
            violation_confidences = [v.confidence for v in profile.all_violations if hasattr(v, 'confidence')]
            if violation_confidences:
                avg_violation_confidence = np.mean(violation_confidences)
                confidence = (confidence + avg_violation_confidence) / 2
        
        return max(0.6, min(1.0, confidence))


# Global compliance analyzer instance
# compliance_analyzer = ComplianceAnalyzer()  # Commented out for testing


async def analyze_content_compliance(
    content_data: Dict[str, Any],
    platforms: Optional[List[Platform]] = None,
    jurisdictions: Optional[List[LegalJurisdiction]] = None
) -> Dict[str, Any]:
    """
    Convenient function for content compliance analysis
    
    Args:
        content_data: Content information and metadata
        platforms: List of platforms to check compliance for
        jurisdictions: Legal jurisdictions to consider
        
    Returns:
        Dict containing compliance analysis results
    """
    try:
        result = await compliance_analyzer.analyze_compliance(
            content_data, platforms, jurisdictions
        )
        return result
    except Exception as e:
        logger.error(f"Compliance analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
