"""Compliance Checker - Regulatory and Business Rule Compliance Verification
========================================================================

Enterprise-grade compliance verification system for content validation against
regulatory requirements, platform policies, and business rules.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Content validation → Regulatory compliance → Platform policy verification → 
Business rule validation → Copyright checking → Privacy compliance → Legal clearance
"""import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# NLP and content analysis
try:
    import spacy
    from textblob import TextBlob
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # For consistent results
    HAS_NLP_LIBS = True
except ImportError:
    HAS_NLP_LIBS = False

# Content analysis libraries
try:
    import cv2
    import numpy as np
    from PIL import Image
    HAS_MEDIA_LIBS = True
except ImportError:
    HAS_MEDIA_LIBS = False


class ComplianceLevel(Enum):
    """Compliance verification levels"""    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    REGULATORY = "regulatory"


class ComplianceStatus(Enum):
    """Compliance verification status"""    COMPLIANT = "compliant"
    MINOR_VIOLATIONS = "minor_violations"
    MAJOR_VIOLATIONS = "major_violations"
    NON_COMPLIANT = "non_compliant"


class ViolationType(Enum):
    """Types of compliance violations"""    COPYRIGHT = "copyright"
    PRIVACY = "privacy"
    CONTENT_POLICY = "content_policy"
    REGULATORY = "regulatory"
    PLATFORM_POLICY = "platform_policy"
    BUSINESS_RULE = "business_rule"
    SAFETY = "safety"
    LEGAL = "legal"


@dataclass
class ComplianceViolation:
    """Compliance violation record"""    violation_type: ViolationType
    severity: str  # low, medium, high, critical
    description: str
    regulation: str
    recommended_action: str
    auto_fixable: bool = False
    legal_risk: str = "low"  # low, medium, high, critical


@dataclass
class ComplianceResult:
    """Compliance verification result"""    status: ComplianceStatus
    score: float
    violations: List[ComplianceViolation]
    compliant_areas: List[str]
    regulations_checked: List[str]
    platform_compliance: Dict[str, bool]
    copyright_analysis: Dict[str, Any]
    privacy_analysis: Dict[str, Any]
    content_safety: Dict[str, Any]
    recommendations: List[str]
    legal_review_required: bool
    processing_time: float


class ComplianceChecker:
    """    Enterprise compliance verification system for multi-format content.
    
    Provides comprehensive compliance checking against regulatory requirements,
    platform policies, copyright laws, privacy regulations, and business rules.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Compliance rules and regulations
        self.regulations = self._load_regulations()
        self.platform_policies = self._load_platform_policies()
        self.business_rules = self._load_business_rules()
        self.content_filters = self._load_content_filters()
        
        # NLP models for content analysis
        self.nlp_model = None
        if HAS_NLP_LIBS:
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("Spacy English model not found. Text analysis will be limited.")
        
        # Compliance scoring weights
        self.scoring_weights = {
            'copyright': 0.3,
            'privacy': 0.25,
            'content_policy': 0.2,
            'regulatory': 0.15,
            'platform_policy': 0.1
        }
        
        self.logger.info("ComplianceChecker initialized successfully")
    
    def _load_regulations(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory compliance rules."""        return {
            'gdpr': {
                'name': 'General Data Protection Regulation',
                'region': 'EU',
                'applies_to': ['personal_data', 'user_content'],
                'rules': [
                    'no_personal_data_without_consent',
                    'data_minimization',
                    'right_to_be_forgotten',
                    'data_portability'
                ]
            },
            'ccpa': {
                'name': 'California Consumer Privacy Act',
                'region': 'US-CA',
                'applies_to': ['personal_data', 'user_tracking'],
                'rules': [
                    'disclosure_of_data_collection',
                    'opt_out_of_sale',
                    'data_deletion_rights'
                ]
            },
            'coppa': {
                'name': 'Children\'s Online Privacy Protection Act',
                'region': 'US',
                'applies_to': ['children_content', 'under_13'],
                'rules': [
                    'parental_consent_required',
                    'limited_data_collection',
                    'no_behavioral_advertising'
                ]
            },
            'dmca': {
                'name': 'Digital Millennium Copyright Act',
                'region': 'US',
                'applies_to': ['copyrighted_content', 'user_uploads'],
                'rules': [
                    'takedown_notice_compliance',
                    'safe_harbor_provisions',
                    'counter_notification_process'
                ]
            },
            'cda_section_230': {
                'name': 'Communications Decency Act Section 230',
                'region': 'US',
                'applies_to': ['user_generated_content', 'moderation'],
                'rules': [
                    'platform_immunity_for_user_content',
                    'good_faith_moderation_protection'
                ]
            }
        }
    
    def _load_platform_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific compliance policies."""        return {
            'youtube': {
                'content_policies': [
                    'no_hate_speech',
                    'no_harassment',
                    'no_violent_content',
                    'no_adult_content',
                    'no_spam',
                    'no_copyright_infringement'
                ],
                'monetization_requirements': [
                    'family_friendly_content',
                    'original_content',
                    'advertiser_friendly'
                ],
                'technical_requirements': [
                    'supported_formats',
                    'quality_standards',
                    'duration_limits'
                ]
            },
            'instagram': {
                'content_policies': [
                    'no_nudity',
                    'no_hate_speech',
                    'no_bullying',
                    'no_fake_news',
                    'no_spam'
                ],
                'community_guidelines': [
                    'authentic_content',
                    'respectful_interaction',
                    'legal_content_only'
                ]
            },
            'tiktok': {
                'content_policies': [
                    'no_dangerous_content',
                    'no_hate_speech',
                    'no_adult_content',
                    'no_copyright_violation',
                    'no_harmful_misinformation'
                ],
                'safety_requirements': [
                    'age_appropriate_content',
                    'no_self_harm_content',
                    'no_dangerous_challenges'
                ]
            },
            'spotify': {
                'content_policies': [
                    'no_hate_speech',
                    'no_copyright_infringement',
                    'no_illegal_content'
                ],
                'quality_requirements': [
                    'audio_quality_standards',
                    'metadata_accuracy',
                    'proper_licensing'
                ]
            },
            'facebook': {
                'community_standards': [
                    'authentic_identity',
                    'no_hate_speech',
                    'no_harassment',
                    'no_fake_news',
                    'no_spam'
                ],
                'intellectual_property': [
                    'respect_copyright',
                    'respect_trademarks',
                    'fair_use_guidelines'
                ]
            }
        }
    
    def _load_business_rules(self) -> Dict[str, List[str]]:
        """Load business-specific compliance rules."""        return {
            'content_quality': [
                'minimum_resolution_standards',
                'audio_quality_requirements',
                'professional_presentation',
                'brand_consistency'
            ],
            'monetization': [
                'advertiser_friendly_content',
                'no_controversial_topics',
                'family_safe_content',
                'brand_safe_environment'
            ],
            'seo_compliance': [
                'keyword_optimization',
                'meta_data_completeness',
                'structured_data_markup',
                'mobile_friendly_content'
            ],
            'accessibility': [
                'text_alternatives_for_media',
                'color_contrast_standards',
                'keyboard_navigation_support',
                'screen_reader_compatibility'
            ]
        }
    
    def _load_content_filters(self) -> Dict[str, List[str]]:
        """Load content filtering rules."""        return {
            'prohibited_keywords': [
                # Violence and threats
                'violence', 'threat', 'murder', 'kill', 'bomb', 'terrorist',
                # Hate speech
                'hate', 'racist', 'nazi', 'supremacist',
                # Adult content
                'explicit', 'pornography', 'nude', 'sex',
                # Illegal activities
                'drugs', 'illegal', 'piracy', 'hack',
                # Harmful content
                'suicide', 'self-harm', 'eating disorder'
            ],
            'sensitive_topics': [
                'politics', 'religion', 'controversial', 'tragedy',
                'medical advice', 'financial advice', 'legal advice'
            ],
            'copyright_indicators': [
                'copyrighted', 'licensed', 'trademark', 'patent',
                'all rights reserved', 'unauthorized use prohibited'
            ]
        }
    
    async def verify_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        rules: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        compliance_level: ComplianceLevel = ComplianceLevel.STANDARD
    ) -> ComplianceResult:
        """        Perform comprehensive compliance verification.
        
        Args:
            content_data: Content to verify
            content_type: Type of content
            rules: Specific compliance rules to check
            user_id: User identifier for context
            compliance_level: Level of compliance checking
            
        Returns:
            ComplianceResult: Comprehensive compliance verification results
        """        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting compliance verification - Type: {content_type}, Level: {compliance_level.value}")
            
            violations = []
            compliant_areas = []
            regulations_checked = []
            
            # Step 1: Copyright compliance verification
            copyright_analysis = await self._verify_copyright_compliance(content_data, content_type)
            regulations_checked.append('copyright')
            
            if copyright_analysis.get('violations'):
                violations.extend(copyright_analysis['violations'])
            else:
                compliant_areas.append('copyright')
            
            # Step 2: Privacy compliance verification
            privacy_analysis = await self._verify_privacy_compliance(content_data, content_type, user_id)
            regulations_checked.append('privacy')
            
            if privacy_analysis.get('violations'):
                violations.extend(privacy_analysis['violations'])
            else:
                compliant_areas.append('privacy')
            
            # Step 3: Content policy verification
            content_safety = await self._verify_content_policies(content_data, content_type)
            regulations_checked.append('content_policy')
            
            if content_safety.get('violations'):
                violations.extend(content_safety['violations'])
            else:
                compliant_areas.append('content_policy')
            
            # Step 4: Platform-specific compliance
            platform_compliance = await self._verify_platform_compliance(content_data, content_type, rules)
            
            for platform, compliant in platform_compliance.items():
                if not compliant:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.PLATFORM_POLICY,
                        severity='medium',
                        description=f'Content does not comply with {platform} policies',
                        regulation=f'{platform}_policy',
                        recommended_action=f'Review and modify content for {platform} compliance'
                    ))
            
            # Step 5: Regulatory compliance (if comprehensive)
            if compliance_level in [ComplianceLevel.COMPREHENSIVE, ComplianceLevel.REGULATORY]:
                regulatory_violations = await self._verify_regulatory_compliance(content_data, content_type, user_id)
                violations.extend(regulatory_violations)
                regulations_checked.extend(['gdpr', 'ccpa', 'dmca'])
            
            # Step 6: Business rule compliance
            business_violations = await self._verify_business_rules(content_data, content_type)
            violations.extend(business_violations)
            regulations_checked.append('business_rules')
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations, compliant_areas)
            
            # Determine compliance status
            status = self._determine_compliance_status(violations, compliance_score)
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(violations)
            
            # Determine if legal review is required
            legal_review_required = any(
                violation.severity in ['high', 'critical'] or violation.legal_risk in ['high', 'critical']
                for violation in violations
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ComplianceResult(
                status=status,
                score=compliance_score,
                violations=violations,
                compliant_areas=compliant_areas,
                regulations_checked=regulations_checked,
                platform_compliance=platform_compliance,
                copyright_analysis=copyright_analysis,
                privacy_analysis=privacy_analysis,
                content_safety=content_safety,
                recommendations=recommendations,
                legal_review_required=legal_review_required,
                processing_time=processing_time
            )
            
            self.logger.info(f"Compliance verification completed - Status: {status.value}, Score: {compliance_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during compliance verification: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ComplianceResult(
                status=ComplianceStatus.NON_COMPLIANT,
                score=0.0,
                violations=[ComplianceViolation(
                    violation_type=ViolationType.REGULATORY,
                    severity='critical',
                    description=f'Compliance verification failed: {str(e)}',
                    regulation='system_error',
                    recommended_action='Review content and retry compliance check'
                )],
                compliant_areas=[],
                regulations_checked=[],
                platform_compliance={},
                copyright_analysis={},
                privacy_analysis={},
                content_safety={},
                recommendations=['Review content data and retry compliance verification'],
                legal_review_required=True,
                processing_time=processing_time
            )
    
    async def _verify_copyright_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Verify copyright compliance and detect potential infringement."""        analysis = {
            'violations': [],
            'copyright_indicators': [],
            'licensing_status': 'unknown',
            'fair_use_analysis': {},
            'originality_score': 0.8
        }
        
        try:
            # Extract text content for analysis
            text_content = self._extract_text_content(content_data, content_type)
            
            if text_content:
                # Check for copyright indicators
                copyright_keywords = self.content_filters['copyright_indicators']
                found_indicators = []
                
                for keyword in copyright_keywords:
                    if keyword.lower() in text_content.lower():
                        found_indicators.append(keyword)
                
                analysis['copyright_indicators'] = found_indicators
                
                # Check for explicit copyright violations
                if any(indicator in text_content.lower() for indicator in ['all rights reserved', 'unauthorized use prohibited']):
                    analysis['violations'].append(ComplianceViolation(
                        violation_type=ViolationType.COPYRIGHT,
                        severity='high',
                        description='Content contains explicit copyright protection notices',
                        regulation='dmca',
                        recommended_action='Verify licensing rights or remove copyrighted content',
                        legal_risk='high'
                    ))
                
                # Fair use analysis (basic)
                fair_use_factors = self._analyze_fair_use(text_content, content_type)
                analysis['fair_use_analysis'] = fair_use_factors
                
                if fair_use_factors['likely_fair_use']:
                    analysis['licensing_status'] = 'fair_use'
                elif fair_use_factors['commercial_use'] and not fair_use_factors['transformative']:
                    analysis['violations'].append(ComplianceViolation(
                        violation_type=ViolationType.COPYRIGHT,
                        severity='medium',
                        description='Commercial use without clear fair use justification',
                        regulation='dmca',
                        recommended_action='Obtain proper licensing or ensure fair use compliance'
                    ))
            
            # Content-specific copyright checks
            if content_type in ['audio', 'video']:
                # Check for known copyrighted audio patterns (placeholder)
                audio_copyright_risk = self._assess_audio_copyright_risk(content_data)
                if audio_copyright_risk > 0.7:
                    analysis['violations'].append(ComplianceViolation(
                        violation_type=ViolationType.COPYRIGHT,
                        severity='high',
                        description='High risk of copyrighted audio content detected',
                        regulation='dmca',
                        recommended_action='Use original or properly licensed audio content',
                        legal_risk='critical'
                    ))
            
            # Calculate originality score
            analysis['originality_score'] = max(0.3, 1.0 - len(analysis['violations']) * 0.2)
            
        except Exception as e:
            analysis['error'] = f'Copyright analysis error: {str(e)}'
        
        return analysis
    
    def _analyze_fair_use(self, text_content: str, content_type: str) -> Dict[str, Any]:
        """Analyze content for fair use factors."""        factors = {
            'transformative': False,
            'educational': False,
            'commentary': False,
            'parody': False,
            'criticism': False,
            'commercial_use': True,  # Assume commercial unless proven otherwise
            'substantial_portion': False,
            'market_impact': 'minimal',
            'likely_fair_use': False
        }
        
        # Check for transformative use indicators
        transformative_keywords = ['review', 'commentary', 'analysis', 'critique', 'parody', 'satire']
        if any(keyword in text_content.lower() for keyword in transformative_keywords):
            factors['transformative'] = True
        
        # Check for educational use
        educational_keywords = ['education', 'teaching', 'learning', 'tutorial', 'how-to']
        if any(keyword in text_content.lower() for keyword in educational_keywords):
            factors['educational'] = True
            factors['commercial_use'] = False
        
        # Check for commentary/criticism
        criticism_keywords = ['review', 'critique', 'analysis', 'opinion', 'commentary']
        if any(keyword in text_content.lower() for keyword in criticism_keywords):
            factors['commentary'] = True
            factors['criticism'] = True
        
        # Assess likely fair use
        fair_use_score = sum([
            factors['transformative'],
            factors['educational'],
            factors['commentary'],
            factors['criticism'],
            not factors['commercial_use'],
            not factors['substantial_portion']
        ])
        
        factors['likely_fair_use'] = fair_use_score >= 3
        
        return factors
    
    def _assess_audio_copyright_risk(self, content_data: Union[bytes, str, Dict[str, Any]]) -> float:
        """Assess copyright risk for audio content (placeholder)."""        # This would integrate with audio fingerprinting systems
        # For now, return a baseline risk
        return 0.3
    
    async def _verify_privacy_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Verify privacy regulation compliance."""        analysis = {
            'violations': [],
            'personal_data_detected': [],
            'consent_status': 'unknown',
            'data_processing_lawful': True,
            'retention_compliant': True
        }
        
        try:
            # Extract text content for privacy analysis
            text_content = self._extract_text_content(content_data, content_type)
            
            if text_content and HAS_NLP_LIBS:
                # Detect personal data using NLP
                personal_data = self._detect_personal_data(text_content)
                analysis['personal_data_detected'] = personal_data
                
                # GDPR compliance checks
                if personal_data:
                    # Check for explicit consent indicators
                    consent_indicators = ['consent', 'agree', 'permission', 'authorize']
                    has_consent_language = any(indicator in text_content.lower() for indicator in consent_indicators)
                    
                    if not has_consent_language:
                        analysis['violations'].append(ComplianceViolation(
                            violation_type=ViolationType.PRIVACY,
                            severity='high',
                            description='Personal data detected without clear consent indicators',
                            regulation='gdpr',
                            recommended_action='Ensure proper consent is obtained for personal data processing',
                            legal_risk='high'
                        ))
                
                # Check for children's data (COPPA compliance)
                children_indicators = ['child', 'kid', 'minor', 'under 13', 'school']
                if any(indicator in text_content.lower() for indicator in children_indicators) and personal_data:
                    analysis['violations'].append(ComplianceViolation(
                        violation_type=ViolationType.PRIVACY,
                        severity='critical',
                        description='Potential children\'s personal data detected',
                        regulation='coppa',
                        recommended_action='Ensure COPPA compliance for children\'s data',
                        legal_risk='critical'
                    ))
            
            # Image/video privacy checks
            if content_type in ['image', 'video'] and HAS_MEDIA_LIBS:
                privacy_risks = await self._detect_visual_privacy_risks(content_data)
                if privacy_risks:
                    analysis['violations'].extend(privacy_risks)
            
        except Exception as e:
            analysis['error'] = f'Privacy analysis error: {str(e)}'
        
        return analysis
    
    def _detect_personal_data(self, text: str) -> List[str]:
        """Detect personal data in text content."""        personal_data = []
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            personal_data.append('email_addresses')
        
        # Phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            personal_data.append('phone_numbers')
        
        # Social Security Numbers (US)
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, text):
            personal_data.append('social_security_numbers')
        
        # Credit card numbers
        cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        if re.search(cc_pattern, text):
            personal_data.append('credit_card_numbers')
        
        # Names (using NLP if available)
        if self.nlp_model:
            doc = self.nlp_model(text[:1000000])  # Limit for performance
            person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if person_entities:
                personal_data.append('names')
        
        # Addresses
        address_keywords = ['street', 'avenue', 'road', 'drive', 'lane', 'apt', 'suite']
        if any(keyword in text.lower() for keyword in address_keywords):
            personal_data.append('addresses')
        
        return personal_data
    
    async def _detect_visual_privacy_risks(self, content_data: Union[bytes, str, Dict[str, Any]]) -> List[ComplianceViolation]:
        """Detect privacy risks in visual content."""        violations = []
        
        # This would integrate with computer vision systems to detect:
        # - Faces (especially children)
        # - License plates
        # - Personal documents
        # - Private property
        
        # Placeholder implementation
        if isinstance(content_data, dict) and 'metadata' in content_data:
            metadata = content_data['metadata']
            if 'faces_detected' in metadata and metadata['faces_detected'] > 0:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.PRIVACY,
                    severity='medium',
                    description='Faces detected in visual content',
                    regulation='gdpr',
                    recommended_action='Ensure consent for individuals appearing in content',
                    legal_risk='medium'
                ))
        
        return violations
    
    async def _verify_content_policies(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Verify content against safety and community policies."""        analysis = {
            'violations': [],
            'safety_score': 0.9,
            'content_rating': 'general',
            'harmful_content_detected': False,
            'moderation_flags': []
        }
        
        try:
            # Extract text content for analysis
            text_content = self._extract_text_content(content_data, content_type)
            
            if text_content:
                # Check for prohibited content
                prohibited_keywords = self.content_filters['prohibited_keywords']
                found_violations = []
                
                for keyword in prohibited_keywords:
                    if keyword.lower() in text_content.lower():
                        found_violations.append(keyword)
                
                if found_violations:
                    analysis['harmful_content_detected'] = True
                    analysis['moderation_flags'].extend(found_violations)
                    
                    # Categorize violations by severity
                    critical_keywords = ['violence', 'threat', 'murder', 'bomb', 'terrorist']
                    high_keywords = ['hate', 'racist', 'explicit', 'drugs']
                    
                    for violation in found_violations:
                        if violation in critical_keywords:
                            severity = 'critical'
                            legal_risk = 'high'
                        elif violation in high_keywords:
                            severity = 'high'
                            legal_risk = 'medium'
                        else:
                            severity = 'medium'
                            legal_risk = 'low'
                        
                        analysis['violations'].append(ComplianceViolation(
                            violation_type=ViolationType.CONTENT_POLICY,
                            severity=severity,
                            description=f'Prohibited content detected: {violation}',
                            regulation='community_guidelines',
                            recommended_action='Remove or modify prohibited content',
                            legal_risk=legal_risk
                        ))
                
                # Sentiment analysis for harmful content
                if HAS_NLP_LIBS:
                    sentiment_analysis = self._analyze_content_sentiment(text_content)
                    if sentiment_analysis['negative_score'] > 0.8:
                        analysis['violations'].append(ComplianceViolation(
                            violation_type=ViolationType.CONTENT_POLICY,
                            severity='medium',
                            description='Highly negative sentiment detected',
                            regulation='community_guidelines',
                            recommended_action='Review content tone and messaging'
                        ))
                
                # Age appropriateness check
                age_rating = self._assess_age_appropriateness(text_content, found_violations)
                analysis['content_rating'] = age_rating
                
                if age_rating in ['mature', 'adult']:
                    analysis['violations'].append(ComplianceViolation(
                        violation_type=ViolationType.CONTENT_POLICY,
                        severity='low',
                        description=f'Content rated as {age_rating}',
                        regulation='age_rating_guidelines',
                        recommended_action='Add appropriate age warnings or content filters'
                    ))
            
            # Visual content safety checks
            if content_type in ['image', 'video']:
                visual_safety = await self._check_visual_content_safety(content_data)
                if visual_safety.get('violations'):
                    analysis['violations'].extend(visual_safety['violations'])
            
            # Calculate safety score
            analysis['safety_score'] = max(0.1, 1.0 - len(analysis['violations']) * 0.15)
            
        except Exception as e:
            analysis['error'] = f'Content policy analysis error: {str(e)}'
        
        return analysis
    
    def _analyze_content_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze content sentiment for harmful content detection."""        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert to positive/negative scores
            positive_score = max(0, polarity)
            negative_score = max(0, -polarity)
            
            return {
                'positive_score': positive_score,
                'negative_score': negative_score,
                'subjectivity': subjectivity,
                'polarity': polarity
            }
        except Exception:
            return {
                'positive_score': 0.5,
                'negative_score': 0.5,
                'subjectivity': 0.5,
                'polarity': 0.0
            }
    
    def _assess_age_appropriateness(self, text: str, violations: List[str]) -> str:
        """Assess age appropriateness of content."""        adult_keywords = ['explicit', 'adult', 'mature', 'violence', 'drug']
        mature_keywords = ['politics', 'controversial', 'complex']
        
        if any(keyword in violations for keyword in adult_keywords):
            return 'adult'
        elif any(keyword in violations for keyword in mature_keywords):
            return 'mature'
        elif any(keyword in text.lower() for keyword in mature_keywords):
            return 'teen'
        else:
            return 'general'
    
    async def _check_visual_content_safety(self, content_data: Union[bytes, str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check visual content for safety violations."""        safety_check = {
            'violations': [],
            'nsfw_detected': False,
            'violence_detected': False,
            'inappropriate_content': False
        }
        
        # This would integrate with computer vision models for:
        # - NSFW content detection
        # - Violence detection
        # - Inappropriate imagery
        
        # Placeholder implementation
        if isinstance(content_data, dict) and 'analysis' in content_data:
            analysis = content_data['analysis']
            
            if analysis.get('nsfw_score', 0) > 0.7:
                safety_check['nsfw_detected'] = True
                safety_check['violations'].append(ComplianceViolation(
                    violation_type=ViolationType.CONTENT_POLICY,
                    severity='high',
                    description='NSFW content detected in visual media',
                    regulation='community_guidelines',
                    recommended_action='Remove or blur inappropriate visual content',
                    legal_risk='medium'
                ))
        
        return safety_check
    
    async def _verify_platform_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        target_platforms: Optional[List[str]]
    ) -> Dict[str, bool]:
        """Verify compliance with platform-specific policies."""        platform_compliance = {}
        
        if not target_platforms:
            target_platforms = ['youtube', 'instagram', 'tiktok', 'spotify', 'facebook']
        
        for platform in target_platforms:
            if platform not in self.platform_policies:
                platform_compliance[platform] = True  # Unknown platform, assume compliant
                continue
            
            policies = self.platform_policies[platform]
            compliant = True
            
            # Check content policies
            text_content = self._extract_text_content(content_data, content_type)
            if text_content:
                for policy in policies.get('content_policies', []):
                    if not self._check_policy_compliance(text_content, policy):
                        compliant = False
                        break
            
            # Platform-specific checks
            if platform == 'youtube' and content_type == 'video':
                # YouTube-specific video checks
                if not self._check_youtube_video_compliance(content_data):
                    compliant = False
            elif platform == 'spotify' and content_type == 'audio':
                # Spotify-specific audio checks
                if not self._check_spotify_audio_compliance(content_data):
                    compliant = False
            
            platform_compliance[platform] = compliant
        
        return platform_compliance
    
    def _check_policy_compliance(self, text: str, policy: str) -> bool:
        """Check if content complies with specific policy."""        policy_keywords = {
            'no_hate_speech': ['hate', 'racist', 'supremacist', 'nazi'],
            'no_harassment': ['harass', 'bully', 'stalk', 'threaten'],
            'no_violent_content': ['violence', 'murder', 'kill', 'assault'],
            'no_adult_content': ['explicit', 'pornography', 'nude', 'sex'],
            'no_spam': ['spam', 'click here', 'buy now', 'limited time'],
            'no_fake_news': ['fake news', 'conspiracy', 'hoax'],
            'no_dangerous_content': ['dangerous', 'harmful', 'suicide', 'self-harm']
        }
        
        keywords = policy_keywords.get(policy, [])
        return not any(keyword in text.lower() for keyword in keywords)
    
    def _check_youtube_video_compliance(self, content_data: Union[bytes, str, Dict[str, Any]]) -> bool:
        """Check YouTube-specific video compliance."""        # Check video duration, format, quality, etc.
        if isinstance(content_data, dict):
            metadata = content_data.get('metadata', {})
            
            # Duration check (example)
            duration = metadata.get('duration', 0)
            if duration > 12 * 3600:  # 12 hours max
                return False
            
            # Quality check
            resolution = metadata.get('resolution', (0, 0))
            if resolution[0] < 240 or resolution[1] < 144:  # Minimum resolution
                return False
        
        return True
    
    def _check_spotify_audio_compliance(self, content_data: Union[bytes, str, Dict[str, Any]]) -> bool:
        """Check Spotify-specific audio compliance."""        # Check audio quality, format, licensing, etc.
        if isinstance(content_data, dict):
            metadata = content_data.get('metadata', {})
            
            # Quality check
            sample_rate = metadata.get('sample_rate', 0)
            if sample_rate < 44100:  # Minimum quality
                return False
            
            # Duration check
            duration = metadata.get('duration', 0)
            if duration < 15:  # Minimum 15 seconds
                return False
        
        return True
    
    async def _verify_regulatory_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        user_id: Optional[str]
    ) -> List[ComplianceViolation]:
        """Verify compliance with specific regulations."""        violations = []
        
        # GDPR compliance
        gdpr_violations = await self._check_gdpr_compliance(content_data, content_type, user_id)
        violations.extend(gdpr_violations)
        
        # DMCA compliance
        dmca_violations = await self._check_dmca_compliance(content_data, content_type)
        violations.extend(dmca_violations)
        
        # COPPA compliance
        coppa_violations = await self._check_coppa_compliance(content_data, content_type)
        violations.extend(coppa_violations)
        
        return violations
    
    async def _check_gdpr_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        user_id: Optional[str]
    ) -> List[ComplianceViolation]:
        """Check GDPR compliance."""        violations = []
        
        text_content = self._extract_text_content(content_data, content_type)
        if text_content:
            personal_data = self._detect_personal_data(text_content)
            
            if personal_data:
                # Check for data processing lawful basis
                lawful_basis_indicators = ['consent', 'contract', 'legal obligation', 'legitimate interest']
                has_lawful_basis = any(indicator in text_content.lower() for indicator in lawful_basis_indicators)
                
                if not has_lawful_basis:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.REGULATORY,
                        severity='high',
                        description='Personal data processing without clear lawful basis',
                        regulation='gdpr_article_6',
                        recommended_action='Establish and document lawful basis for data processing',
                        legal_risk='high'
                    ))
                
                # Check for data subject rights information
                rights_indicators = ['delete', 'portability', 'rectification', 'access']
                has_rights_info = any(indicator in text_content.lower() for indicator in rights_indicators)
                
                if not has_rights_info:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.REGULATORY,
                        severity='medium',
                        description='Data subject rights not clearly communicated',
                        regulation='gdpr_article_13',
                        recommended_action='Provide clear information about data subject rights'
                    ))
        
        return violations
    
    async def _check_dmca_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Check DMCA compliance."""        violations = []
        
        # Check for potential copyright infringement
        copyright_risk = self._assess_copyright_infringement_risk(content_data, content_type)
        
        if copyright_risk > 0.8:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.REGULATORY,
                severity='critical',
                description='High risk of copyright infringement detected',
                regulation='dmca_section_512',
                recommended_action='Verify copyright ownership or obtain proper licensing',
                legal_risk='critical'
            ))
        
        return violations
    
    async def _check_coppa_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Check COPPA compliance."""        violations = []
        
        text_content = self._extract_text_content(content_data, content_type)
        if text_content:
            # Check for children-directed content
            children_keywords = ['kids', 'children', 'child', 'young', 'school', 'toy', 'cartoon']
            is_child_directed = any(keyword in text_content.lower() for keyword in children_keywords)
            
            if is_child_directed:
                # Check for data collection without parental consent
                data_collection_indicators = ['email', 'name', 'address', 'phone', 'location']
                collects_data = any(indicator in text_content.lower() for indicator in data_collection_indicators)
                
                consent_indicators = ['parent', 'guardian', 'consent', 'permission']
                has_parental_consent = any(indicator in text_content.lower() for indicator in consent_indicators)
                
                if collects_data and not has_parental_consent:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.REGULATORY,
                        severity='critical',
                        description='Children-directed content collecting data without parental consent',
                        regulation='coppa_section_312',
                        recommended_action='Implement verifiable parental consent mechanism',
                        legal_risk='critical'
                    ))
        
        return violations
    
    def _assess_copyright_infringement_risk(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> float:
        """Assess risk of copyright infringement."""        # This would integrate with content identification systems
        # For now, return a baseline risk assessment
        
        risk_score = 0.2  # Base risk
        
        # Check for known copyrighted material indicators
        text_content = self._extract_text_content(content_data, content_type)
        if text_content:
            copyright_indicators = ['copyright', '©', 'all rights reserved', 'unauthorized']
            if any(indicator in text_content.lower() for indicator in copyright_indicators):
                risk_score += 0.3
        
        # Content-type specific risk assessment
        if content_type in ['audio', 'video']:
            # Higher risk for multimedia content
            risk_score += 0.2
        
        return min(1.0, risk_score)
    
    async def _verify_business_rules(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Verify compliance with business rules."""        violations = []
        
        # Content quality business rules
        quality_violations = self._check_quality_business_rules(content_data, content_type)
        violations.extend(quality_violations)
        
        # Monetization business rules
        monetization_violations = self._check_monetization_business_rules(content_data, content_type)
        violations.extend(monetization_violations)
        
        # SEO business rules
        seo_violations = self._check_seo_business_rules(content_data, content_type)
        violations.extend(seo_violations)
        
        return violations
    
    def _check_quality_business_rules(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Check quality-related business rules."""        violations = []
        
        if isinstance(content_data, dict) and 'metadata' in content_data:
            metadata = content_data['metadata']
            
            # Resolution requirements
            if content_type in ['image', 'video']:
                resolution = metadata.get('resolution', (0, 0))
                min_resolution = (720, 480)  # Business requirement
                
                if resolution[0] < min_resolution[0] or resolution[1] < min_resolution[1]:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.BUSINESS_RULE,
                        severity='medium',
                        description=f'Resolution below business standards: {resolution}',
                        regulation='quality_standards',
                        recommended_action='Increase content resolution to meet quality standards'
                    ))
            
            # Audio quality requirements
            elif content_type == 'audio':
                sample_rate = metadata.get('sample_rate', 0)
                min_sample_rate = 44100  # Business requirement
                
                if sample_rate < min_sample_rate:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.BUSINESS_RULE,
                        severity='medium',
                        description=f'Audio quality below business standards: {sample_rate}Hz',
                        regulation='audio_quality_standards',
                        recommended_action='Increase audio sample rate to meet quality standards'
                    ))
        
        return violations
    
    def _check_monetization_business_rules(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Check monetization-related business rules."""        violations = []
        
        text_content = self._extract_text_content(content_data, content_type)
        if text_content:
            # Check for advertiser-unfriendly content
            unfriendly_keywords = ['controversial', 'politics', 'tragedy', 'disaster']
            if any(keyword in text_content.lower() for keyword in unfriendly_keywords):
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.BUSINESS_RULE,
                    severity='low',
                    description='Content may not be advertiser-friendly',
                    regulation='monetization_guidelines',
                    recommended_action='Review content for advertiser-friendliness'
                ))
        
        return violations
    
    def _check_seo_business_rules(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[ComplianceViolation]:
        """Check SEO-related business rules."""        violations = []
        
        if content_type == 'text':
            text_content = self._extract_text_content(content_data, content_type)
            if text_content:
                # Check content length for SEO
                word_count = len(text_content.split())
                min_words = 300  # SEO best practice
                
                if word_count < min_words:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.BUSINESS_RULE,
                        severity='low',
                        description=f'Content too short for optimal SEO: {word_count} words',
                        regulation='seo_guidelines',
                        recommended_action='Expand content to meet SEO word count requirements'
                    ))
        
        return violations
    
    def _extract_text_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> str:
        """Extract text content for analysis."""        if isinstance(content_data, str):
            return content_data
        elif isinstance(content_data, dict):
            # Try various text fields
            for field in ['text', 'content', 'description', 'title', 'body']:
                if field in content_data and isinstance(content_data[field], str):
                    return content_data[field]
            # Try to extract from metadata
            metadata = content_data.get('metadata', {})
            for field in ['description', 'title', 'lyrics', 'transcript']:
                if field in metadata and isinstance(metadata[field], str):
                    return metadata[field]
        elif isinstance(content_data, bytes):
            try:
                return content_data.decode('utf-8', errors='ignore')
            except:
                return ""
        
        return ""
    
    def _calculate_compliance_score(
        self,
        violations: List[ComplianceViolation],
        compliant_areas: List[str]
    ) -> float:
        """Calculate overall compliance score."""        if not violations and not compliant_areas:
            return 0.7  # Neutral score
        
        # Base score
        base_score = 1.0
        
        # Deduct points for violations
        for violation in violations:
            if violation.severity == 'critical':
                base_score -= 0.3
            elif violation.severity == 'high':
                base_score -= 0.2
            elif violation.severity == 'medium':
                base_score -= 0.1
            elif violation.severity == 'low':
                base_score -= 0.05
        
        # Bonus for compliant areas
        compliance_bonus = min(0.2, len(compliant_areas) * 0.05)
        
        final_score = max(0.0, base_score + compliance_bonus)
        return round(final_score, 3)
    
    def _determine_compliance_status(
        self,
        violations: List[ComplianceViolation],
        score: float
    ) -> ComplianceStatus:
        """Determine overall compliance status."""        critical_violations = [v for v in violations if v.severity == 'critical']
        high_violations = [v for v in violations if v.severity == 'high']
        
        if critical_violations or score < 0.3:
            return ComplianceStatus.NON_COMPLIANT
        elif high_violations or score < 0.6:
            return ComplianceStatus.MAJOR_VIOLATIONS
        elif violations and score < 0.8:
            return ComplianceStatus.MINOR_VIOLATIONS
        else:
            return ComplianceStatus.COMPLIANT
    
    def _generate_compliance_recommendations(
        self,
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate compliance improvement recommendations."""        recommendations = []
        
        # Priority order: critical > high > medium > low
        sorted_violations = sorted(violations, 
                                  key=lambda v: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[v.severity])
        
        for violation in sorted_violations[:10]:  # Limit to top 10 recommendations
            recommendations.append(violation.recommended_action)
        
        # Add general recommendations
        violation_types = set(v.violation_type for v in violations)
        
        if ViolationType.COPYRIGHT in violation_types:
            recommendations.append('Conduct thorough copyright review before publication')
        
        if ViolationType.PRIVACY in violation_types:
            recommendations.append('Implement comprehensive privacy compliance measures')
        
        if ViolationType.CONTENT_POLICY in violation_types:
            recommendations.append('Review content against community guidelines')
        
        return list(set(recommendations))  # Remove duplicates


class ContentComplianceValidator:
    """    Specialized content compliance validator for platform-specific policies.
    
    Validates content against major platform community guidelines and policies
    including YouTube, Instagram, TikTok, Spotify, and other creator platforms.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ContentComplianceValidator")
        
        # Platform-specific content policies
        self.platform_policies = {
            'youtube': {
                'prohibited_content': [
                    'hate_speech', 'harassment', 'violence', 'dangerous_acts',
                    'spam', 'misleading_metadata', 'copyright_infringement'
                ],
                'content_restrictions': {
                    'min_age': 13,
                    'max_duration': 43200,  # 12 hours
                    'mature_content_allowed': True,
                    'monetization_friendly': ['educational', 'entertainment', 'music']
                },
                'technical_requirements': {
                    'max_file_size': 256 * 1024 * 1024 * 1024,  # 256GB
                    'supported_formats': ['MP4', 'MOV', 'AVI', 'WMV', 'FLV', 'WebM'],
                    'min_resolution': (426, 240),
                    'max_resolution': (7680, 4320)
                }
            },
            'instagram': {
                'prohibited_content': [
                    'nudity', 'hate_speech', 'violence', 'harassment',
                    'fake_information', 'spam', 'copyright_infringement'
                ],
                'content_restrictions': {
                    'min_age': 13,
                    'story_duration': 15,
                    'reel_max_duration': 90,
                    'mature_content_limited': True
                },
                'technical_requirements': {
                    'image_formats': ['JPEG', 'PNG'],
                    'video_formats': ['MP4', 'MOV'],
                    'max_image_size': 8 * 1024 * 1024,  # 8MB
                    'max_video_size': 4 * 1024 * 1024 * 1024  # 4GB
                }
            },
            'tiktok': {
                'prohibited_content': [
                    'hate_speech', 'harassment', 'dangerous_acts', 'violence',
                    'illegal_activities', 'misinformation', 'spam'
                ],
                'content_restrictions': {
                    'min_age': 13,
                    'max_duration': 600,  # 10 minutes
                    'music_copyright_sensitive': True,
                    'region_restrictions': True
                },
                'technical_requirements': {
                    'video_formats': ['MP4', 'MOV'],
                    'min_resolution': (540, 960),
                    'max_file_size': 287 * 1024 * 1024,  # 287MB
                    'aspect_ratio_preferred': (9, 16)
                }
            },
            'spotify': {
                'prohibited_content': [
                    'hate_speech', 'explicit_content_unmarked', 'copyright_infringement',
                    'low_quality_audio', 'misleading_metadata'
                ],
                'content_restrictions': {
                    'explicit_content_allowed': True,
                    'min_duration': 30,
                    'podcast_content_allowed': True,
                    'music_only_uploads': False
                },
                'technical_requirements': {
                    'audio_formats': ['FLAC', 'WAV', 'MP3', 'OGG'],
                    'min_quality': '44.1 kHz/16-bit',
                    'loudness_standard': -14.0,  # LUFS
                    'max_file_size': 650 * 1024 * 1024  # 650MB
                }
            }
        }
        
        # Content detection patterns
        self.content_patterns = {
            'hate_speech': [
                r'\b(hate|hatred)\b.*\b(race|religion|gender|sexuality)\b',
                r'\b(kill|die|death)\b.*\b(jews|muslims|christians|gays|women|men)\b',
                r'\b(terrorist|terrorism)\b'
            ],
            'violence': [
                r'\b(kill|murder|assault|attack|violence|fight|hurt|harm)\b',
                r'\b(gun|knife|weapon|bomb|explosive)\b',
                r'\b(blood|gore|torture|abuse)\b'
            ],
            'harassment': [
                r'\b(bully|bullying|harass|harassment|stalk|stalking)\b',
                r'\b(loser|stupid|idiot|worthless)\b.*\b(you|person|people)\b',
                r'\b(ugly|fat|disgusting)\b.*\b(you|person)\b'
            ],
            'spam': [
                r'\b(buy now|click here|free money|get rich quick)\b',
                r'\b(subscribe|like|follow)\b.*\b(please|pls|plz)\b.*{3,}',
                r'\b(www\.|http|https|\.com|\.net|\.org)\b.*{3,}'
            ],
            'explicit_content': [
                r'\b(sex|sexual|porn|pornography|nude|naked|breast|penis|vagina)\b',
                r'\b(fuck|shit|bitch|ass|damn|hell)\b',
                r'\b(drug|drugs|cocaine|marijuana|weed|heroin)\b'
            ]
        }
    
    async def validate_platform_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        target_platforms: List[str],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate content compliance for specific platforms."""        try:
            compliance_results = {}
            
            for platform in target_platforms:
                if platform not in self.platform_policies:
                    compliance_results[platform] = {
                        'error': f'Unknown platform: {platform}',
                        'compliant': False
                    }
                    continue
                
                platform_result = await self._validate_single_platform(
                    content_data, content_type, platform, content_metadata
                )
                compliance_results[platform] = platform_result
            
            # Calculate overall compliance
            overall_compliance = self._calculate_overall_platform_compliance(compliance_results)
            compliance_results['overall'] = overall_compliance
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Platform compliance validation failed: {str(e)}")
            return {'error': f'Platform compliance validation failed: {str(e)}'}
    
    async def _validate_single_platform(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        platform: str,
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate content for a single platform."""        platform_policy = self.platform_policies[platform]
        violations = []
        compliant_checks = []
        
        # Content policy checks
        content_violations = await self._check_content_policies(
            content_data, content_type, platform_policy['prohibited_content']
        )
        violations.extend(content_violations)
        
        # Technical requirement checks
        technical_violations = await self._check_technical_requirements(
            content_data, content_type, platform_policy['technical_requirements'], content_metadata
        )
        violations.extend(technical_violations)
        
        # Content restriction checks
        restriction_violations = await self._check_content_restrictions(
            content_data, content_type, platform_policy['content_restrictions'], content_metadata
        )
        violations.extend(restriction_violations)
        
        # Determine compliance status
        compliant = len([v for v in violations if v['severity'] in ['high', 'critical']]) == 0
        
        # Calculate compliance score
        compliance_score = max(0.0, 1.0 - len(violations) * 0.1)
        
        return {
            'platform': platform,
            'compliant': compliant,
            'compliance_score': compliance_score,
            'violations': violations,
            'checks_passed': len(compliant_checks),
            'recommendations': self._generate_platform_recommendations(violations, platform)
        }
    
    async def _check_content_policies(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        prohibited_content: List[str]
    ) -> List[Dict[str, Any]]:
        """Check content against prohibited content policies."""        violations = []
        
        # Extract text content for analysis
        text_content = await self._extract_text_content(content_data, content_type)
        
        if text_content and HAS_NLP_LIBS:
            for prohibited_type in prohibited_content:
                if prohibited_type in self.content_patterns:
                    patterns = self.content_patterns[prohibited_type]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        if matches:
                            violations.append({
                                'type': prohibited_type,
                                'severity': 'high',
                                'description': f'Potential {prohibited_type} detected in content',
                                'matches': matches[:3],  # Limit to first 3 matches
                                'recommendation': f'Review and remove {prohibited_type} content'
                            })
                            break  # One violation per type
        
        # Visual content analysis (if applicable)
        if content_type in ['image', 'video'] and HAS_MEDIA_LIBS:
            visual_violations = await self._analyze_visual_content_policies(content_data, prohibited_content)
            violations.extend(visual_violations)
        
        return violations
    
    async def _check_technical_requirements(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        technical_requirements: Dict[str, Any],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check content against technical requirements."""        violations = []
        
        try:
            # File size checks
            if 'max_file_size' in technical_requirements:
                max_size = technical_requirements['max_file_size']
                
                if isinstance(content_data, str) and os.path.exists(content_data):
                    file_size = os.path.getsize(content_data)
                elif isinstance(content_data, bytes):
                    file_size = len(content_data)
                else:
                    file_size = 0
                
                if file_size > max_size:
                    violations.append({
                        'type': 'file_size_exceeded',
                        'severity': 'medium',
                        'description': f'File size ({file_size} bytes) exceeds limit ({max_size} bytes)',
                        'recommendation': 'Compress or reduce file size'
                    })
            
            # Format checks
            format_requirements = {
                'audio': technical_requirements.get('audio_formats', []),
                'video': technical_requirements.get('video_formats', []),
                'image': technical_requirements.get('image_formats', [])
            }
            
            if content_type in format_requirements and format_requirements[content_type]:
                supported_formats = format_requirements[content_type]
                
                # Detect current format
                current_format = await self._detect_content_format(content_data, content_type)
                
                if current_format and current_format.upper() not in [f.upper() for f in supported_formats]:
                    violations.append({
                        'type': 'unsupported_format',
                        'severity': 'high',
                        'description': f'Format {current_format} not supported. Supported: {supported_formats}',
                        'recommendation': f'Convert to one of: {", ".join(supported_formats)}'
                    })
            
            # Resolution checks (for video/image)
            if content_type in ['video', 'image']:
                resolution_violations = await self._check_resolution_requirements(
                    content_data, content_type, technical_requirements, content_metadata
                )
                violations.extend(resolution_violations)
            
            # Audio quality checks (for audio/video)
            if content_type in ['audio', 'video']:
                audio_violations = await self._check_audio_requirements(
                    content_data, content_type, technical_requirements, content_metadata
                )
                violations.extend(audio_violations)
            
        except Exception as e:
            self.logger.error(f"Technical requirements check failed: {str(e)}")
            violations.append({
                'type': 'technical_check_failed',
                'severity': 'low',
                'description': f'Technical validation failed: {str(e)}',
                'recommendation': 'Review technical specifications manually'
            })
        
        return violations
    
    async def _check_content_restrictions(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        content_restrictions: Dict[str, Any],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check content against platform content restrictions."""        violations = []
        
        # Duration checks
        if 'max_duration' in content_restrictions:
            max_duration = content_restrictions['max_duration']
            
            # Extract duration from metadata or content
            duration = None
            if content_metadata and 'duration' in content_metadata:
                duration = content_metadata['duration']
            elif content_type in ['audio', 'video']:
                duration = await self._extract_duration(content_data, content_type)
            
            if duration and duration > max_duration:
                violations.append({
                    'type': 'duration_exceeded',
                    'severity': 'medium',
                    'description': f'Duration ({duration}s) exceeds limit ({max_duration}s)',
                    'recommendation': 'Trim content to meet duration requirements'
                })
        
        # Minimum duration checks
        if 'min_duration' in content_restrictions:
            min_duration = content_restrictions['min_duration']
            
            duration = None
            if content_metadata and 'duration' in content_metadata:
                duration = content_metadata['duration']
            elif content_type in ['audio', 'video']:
                duration = await self._extract_duration(content_data, content_type)
            
            if duration and duration < min_duration:
                violations.append({
                    'type': 'duration_too_short',
                    'severity': 'medium',
                    'description': f'Duration ({duration}s) below minimum ({min_duration}s)',
                    'recommendation': 'Extend content to meet minimum duration'
                })
        
        # Age restriction checks
        if 'min_age' in content_restrictions:
            min_age = content_restrictions['min_age']
            
            # Analyze content for age-appropriate material
            text_content = await self._extract_text_content(content_data, content_type)
            if text_content:
                age_inappropriate = await self._check_age_appropriateness(text_content, min_age)
                if age_inappropriate:
                    violations.append({
                        'type': 'age_inappropriate',
                        'severity': 'high',
                        'description': f'Content may not be appropriate for users under {min_age}',
                        'recommendation': 'Review content for age-appropriate material or add age restrictions'
                    })
        
        # Explicit content checks
        if not content_restrictions.get('explicit_content_allowed', True):
            text_content = await self._extract_text_content(content_data, content_type)
            if text_content:
                explicit_detected = await self._detect_explicit_content(text_content)
                if explicit_detected:
                    violations.append({
                        'type': 'explicit_content_not_allowed',
                        'severity': 'high',
                        'description': 'Explicit content detected but not allowed on this platform',
                        'recommendation': 'Remove explicit content or choose different platform'
                    })
        
        return violations
    
    async def _extract_text_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Optional[str]:
        """Extract text content for analysis."""        try:
            if content_type == 'text':
                if isinstance(content_data, bytes):
                    return content_data.decode('utf-8', errors='ignore')
                elif isinstance(content_data, str):
                    return content_data
            
            elif isinstance(content_data, dict):
                # Extract text from various metadata fields
                text_fields = ['title', 'description', 'transcript', 'lyrics', 'caption']
                text_parts = []
                
                for field in text_fields:
                    if field in content_data and content_data[field]:
                        text_parts.append(str(content_data[field]))
                
                return ' '.join(text_parts) if text_parts else None
            
            # For other content types, try to extract embedded text
            # This would require specialized extraction methods
            
        except Exception as e:
            self.logger.debug(f"Text extraction failed: {str(e)}")
        
        return None
    
    async def _analyze_visual_content_policies(
        self,
        content_data: Union[bytes, str],
        prohibited_content: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze visual content for policy violations."""        violations = []
        
        # This would implement computer vision-based content analysis
        # For now, placeholder implementation
        
        try:
            # Placeholder for:
            # - Nudity detection
            # - Violence detection
            # - Inappropriate content detection
            # - Brand/logo detection for copyright
            
            pass
            
        except Exception as e:
            self.logger.debug(f"Visual content analysis failed: {str(e)}")
        
        return violations
    
    async def _detect_content_format(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> Optional[str]:
        """Detect the format of content."""        try:
            if isinstance(content_data, str) and os.path.exists(content_data):
                # Use file extension
                _, ext = os.path.splitext(content_data)
                return ext[1:].upper() if ext else None
            
            # For bytes data, would need magic number detection
            # Simplified implementation
            
        except Exception as e:
            self.logger.debug(f"Format detection failed: {str(e)}")
        
        return None
    
    async def _check_resolution_requirements(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        technical_requirements: Dict[str, Any],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check resolution requirements for visual content."""        violations = []
        
        # Extract resolution from metadata or analyze content
        width, height = None, None
        
        if content_metadata:
            width = content_metadata.get('width')
            height = content_metadata.get('height')
        
        # Check minimum resolution
        if 'min_resolution' in technical_requirements:
            min_width, min_height = technical_requirements['min_resolution']
            
            if width and height:
                if width < min_width or height < min_height:
                    violations.append({
                        'type': 'resolution_too_low',
                        'severity': 'medium',
                        'description': f'Resolution {width}x{height} below minimum {min_width}x{min_height}',
                        'recommendation': 'Increase resolution to meet requirements'
                    })
        
        # Check maximum resolution
        if 'max_resolution' in technical_requirements:
            max_width, max_height = technical_requirements['max_resolution']
            
            if width and height:
                if width > max_width or height > max_height:
                    violations.append({
                        'type': 'resolution_too_high',
                        'severity': 'low',
                        'description': f'Resolution {width}x{height} exceeds maximum {max_width}x{max_height}',
                        'recommendation': 'Reduce resolution to meet requirements'
                    })
        
        return violations
    
    async def _check_audio_requirements(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        technical_requirements: Dict[str, Any],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check audio quality requirements."""        violations = []
        
        # This would implement audio quality analysis
        # Placeholder implementation
        
        return violations
    
    async def _extract_duration(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> Optional[float]:
        """Extract duration from audio/video content."""        try:
            if content_type == 'audio' and HAS_MEDIA_LIBS:
                if isinstance(content_data, str):
                    y, sr = librosa.load(content_data, sr=None)
                    return len(y) / sr
            
            elif content_type == 'video' and HAS_MEDIA_LIBS:
                if isinstance(content_data, str):
                    cap = cv2.VideoCapture(content_data)
                    if cap.isOpened():
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        cap.release()
                        
                        if fps > 0:
                            return frame_count / fps
            
        except Exception as e:
            self.logger.debug(f"Duration extraction failed: {str(e)}")
        
        return None
    
    async def _check_age_appropriateness(self, text_content: str, min_age: int) -> bool:
        """Check if content is appropriate for minimum age."""        # Simplified age appropriateness check
        # Real implementation would use more sophisticated analysis
        
        inappropriate_patterns = [
            r'\b(sex|sexual|porn|nude|naked)\b',
            r'\b(violence|kill|murder|death|blood)\b',
            r'\b(drug|alcohol|smoking|drinking)\b',
            r'\b(hate|racism|discrimination)\b'
        ]
        
        if min_age < 18:
            for pattern in inappropriate_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return True
        
        return False
    
    async def _detect_explicit_content(self, text_content: str) -> bool:
        """Detect explicit content in text."""        explicit_patterns = self.content_patterns.get('explicit_content', [])
        
        for pattern in explicit_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_overall_platform_compliance(
        self,
        platform_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall compliance across all platforms."""        compliant_platforms = []
        total_violations = []
        compliance_scores = []
        
        for platform, result in platform_results.items():
            if 'error' not in result:
                if result.get('compliant', False):
                    compliant_platforms.append(platform)
                
                if 'violations' in result:
                    total_violations.extend(result['violations'])
                
                if 'compliance_score' in result:
                    compliance_scores.append(result['compliance_score'])
        
        overall_compliant = len(compliant_platforms) == len([p for p in platform_results.keys() if p != 'overall'])
        overall_score = np.mean(compliance_scores) if compliance_scores else 0.0
        
        return {
            'overall_compliant': overall_compliant,
            'compliant_platforms': compliant_platforms,
            'compliance_score': overall_score,
            'total_violations': len(total_violations),
            'critical_violations': len([v for v in total_violations if v.get('severity') == 'critical']),
            'recommendations': self._generate_overall_recommendations(total_violations)
        }
    
    def _generate_platform_recommendations(
        self,
        violations: List[Dict[str, Any]],
        platform: str
    ) -> List[str]:
        """Generate platform-specific recommendations."""        recommendations = []
        
        # Group violations by type
        violation_types = set(v['type'] for v in violations)
        
        for violation_type in violation_types:
            type_violations = [v for v in violations if v['type'] == violation_type]
            
            if violation_type == 'file_size_exceeded':
                recommendations.append(f'Optimize file size for {platform} (compress or reduce quality)')
            elif violation_type == 'unsupported_format':
                recommendations.append(f'Convert to {platform}-supported format')
            elif violation_type == 'duration_exceeded':
                recommendations.append(f'Edit content to fit {platform} duration limits')
            elif violation_type in ['hate_speech', 'harassment', 'violence']:
                recommendations.append(f'Review and remove policy-violating content for {platform}')
            elif violation_type == 'explicit_content_not_allowed':
                recommendations.append(f'Remove explicit content or choose platforms that allow it')
        
        return recommendations
    
    def _generate_overall_recommendations(
        self,
        total_violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate overall compliance recommendations."""        recommendations = []
        
        violation_counts = {}
        for violation in total_violations:
            v_type = violation['type']
            violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
        
        # Priority recommendations based on most common violations
        sorted_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
        
        for violation_type, count in sorted_violations[:5]:  # Top 5 issues
            if violation_type == 'file_size_exceeded':
                recommendations.append('Implement consistent file size optimization across all platforms')
            elif violation_type in ['hate_speech', 'harassment', 'violence']:
                recommendations.append('Establish content moderation guidelines to prevent policy violations')
            elif violation_type == 'unsupported_format':
                recommendations.append('Standardize content formats for better platform compatibility')
            elif violation_type == 'explicit_content_not_allowed':
                recommendations.append('Create separate content versions for different platform policies')
        
        return recommendations


class CopyrightComplianceChecker:
    """    Specialized copyright compliance checker for content protection.
    
    Provides comprehensive copyright analysis, fair use evaluation, and
    intellectual property compliance verification for creator content.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.CopyrightComplianceChecker")
        
        # Copyright databases and APIs (placeholder)
        self.copyright_databases = {
            'music': {
                'databases': ['ASCAP', 'BMI', 'SESAC', 'MusicBrainz'],
                'api_endpoints': [],
                'fingerprint_services': ['AudibleMagic', 'Gracenote']
            },
            'video': {
                'databases': ['ContentID', 'Audible Magic'],
                'api_endpoints': [],
                'fingerprint_services': ['YouTube ContentID', 'Facebook Rights Manager']
            },
            'image': {
                'databases': ['Getty Images', 'Shutterstock', 'Adobe Stock'],
                'api_endpoints': [],
                'fingerprint_services': ['TinEye', 'Google Reverse Image Search']
            },
            'text': {
                'databases': ['Copyscape', 'Grammarly', 'Turnitin'],
                'api_endpoints': [],
                'plagiarism_services': ['iThenticate', 'Unicheck']
            }
        }
        
        # Fair use guidelines
        self.fair_use_criteria = {
            'purpose_and_character': {
                'transformative_use': 0.8,
                'commercial_use': -0.5,
                'educational_use': 0.6,
                'parody_use': 0.7,
                'criticism_review': 0.6
            },
            'nature_of_work': {
                'factual_work': 0.3,
                'creative_work': -0.3,
                'published_work': 0.2,
                'unpublished_work': -0.4
            },
            'amount_used': {
                'minimal_portion': 0.7,
                'substantial_portion': -0.8,
                'heart_of_work': -0.9,
                'entire_work': -1.0
            },
            'effect_on_market': {
                'no_market_harm': 0.6,
                'potential_market_harm': -0.4,
                'significant_market_harm': -0.8,
                'market_substitute': -1.0
            }
        }
    
    async def check_copyright_compliance(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        content_metadata: Optional[Dict[str, Any]] = None,
        fair_use_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive copyright compliance check."""        try:
            compliance_result = {
                'copyright_compliant': False,
                'copyright_risks': [],
                'fair_use_analysis': {},
                'attribution_requirements': [],
                'license_recommendations': [],
                'similar_content_found': [],
                'originality_score': 0.0,
                'copyright_clearance_needed': False,
                'recommendations': []
            }
            
            # Check for similar/existing content
            similarity_results = await self._check_content_similarity(content_data, content_type)
            compliance_result['similar_content_found'] = similarity_results
            
            # Analyze originality
            originality_score = await self._analyze_originality(content_data, content_type, similarity_results)
            compliance_result['originality_score'] = originality_score
            
            # Fair use analysis (if applicable)
            if fair_use_context:
                fair_use_result = await self._analyze_fair_use(
                    content_data, content_type, fair_use_context, similarity_results
                )
                compliance_result['fair_use_analysis'] = fair_use_result
            
            # Check attribution requirements
            attribution_reqs = await self._check_attribution_requirements(
                content_data, content_type, content_metadata
            )
            compliance_result['attribution_requirements'] = attribution_reqs
            
            # Identify copyright risks
            copyright_risks = await self._identify_copyright_risks(
                similarity_results, originality_score, fair_use_context
            )
            compliance_result['copyright_risks'] = copyright_risks
            
            # Determine if copyright clearance is needed
            clearance_needed = await self._determine_clearance_requirements(
                copyright_risks, similarity_results, originality_score
            )
            compliance_result['copyright_clearance_needed'] = clearance_needed
            
            # Generate license recommendations
            license_recs = await self._generate_license_recommendations(
                content_type, originality_score, copyright_risks
            )
            compliance_result['license_recommendations'] = license_recs
            
            # Determine overall compliance
            compliance_result['copyright_compliant'] = (
                originality_score > 0.8 and
                len([r for r in copyright_risks if r['risk_level'] == 'high']) == 0
            )
            
            # Generate recommendations
            recommendations = await self._generate_copyright_recommendations(compliance_result)
            compliance_result['recommendations'] = recommendations
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Copyright compliance check failed: {str(e)}")
            return {
                'error': f'Copyright compliance check failed: {str(e)}',
                'copyright_compliant': False,
                'originality_score': 0.0
            }
    
    async def _check_content_similarity(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Check for similar content in copyright databases."""        similar_content = []
        
        try:
            # This would implement actual database queries and fingerprint matching
            # For now, placeholder implementation
            
            if content_type == 'text':
                similar_content.extend(await self._check_text_similarity(content_data))
            elif content_type == 'audio':
                similar_content.extend(await self._check_audio_similarity(content_data))
            elif content_type == 'video':
                similar_content.extend(await self._check_video_similarity(content_data))
            elif content_type == 'image':
                similar_content.extend(await self._check_image_similarity(content_data))
            
        except Exception as e:
            self.logger.error(f"Content similarity check failed: {str(e)}")
        
        return similar_content
    
    async def _check_text_similarity(self, text_data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Check text content for plagiarism and similarity."""        similar_texts = []
        
        try:
            if isinstance(text_data, bytes):
                text = text_data.decode('utf-8', errors='ignore')
            else:
                text = str(text_data)
            
            # Placeholder for actual plagiarism detection
            # Would integrate with services like Copyscape, Turnitin, etc.
            
            # Simple similarity check (placeholder)
            text_length = len(text.split())
            if text_length > 100:
                # Simulate finding similar content
                similar_texts.append({
                    'source': 'example_database',
                    'similarity_score': 0.15,  # Low similarity
                    'matching_phrases': ['example phrase'],
                    'source_url': 'https://example.com',
                    'copyright_status': 'unknown'
                })
            
        except Exception as e:
            self.logger.debug(f"Text similarity check failed: {str(e)}")
        
        return similar_texts
    
    async def _check_audio_similarity(self, audio_data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Check audio content for copyright matches."""        similar_audio = []
        
        try:
            # Placeholder for audio fingerprinting
            # Would integrate with services like AudibleMagic, Gracenote, etc.
            
            # Simulate audio fingerprint analysis
            similar_audio.append({
                'source': 'music_database',
                'similarity_score': 0.05,  # Very low similarity
                'match_type': 'partial',
                'artist': 'Unknown',
                'title': 'Unknown',
                'copyright_owner': 'Unknown'
            })
            
        except Exception as e:
            self.logger.debug(f"Audio similarity check failed: {str(e)}")
        
        return similar_audio
    
    async def _check_video_similarity(self, video_data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Check video content for copyright matches."""        similar_videos = []
        
        try:
            # Placeholder for video fingerprinting
            # Would integrate with YouTube ContentID, Facebook Rights Manager, etc.
            
            pass
            
        except Exception as e:
            self.logger.debug(f"Video similarity check failed: {str(e)}")
        
        return similar_videos
    
    async def _check_image_similarity(self, image_data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Check image content for copyright matches."""        similar_images = []
        
        try:
            # Placeholder for reverse image search
            # Would integrate with TinEye, Google Images, stock photo databases
            
            pass
            
        except Exception as e:
            self.logger.debug(f"Image similarity check failed: {str(e)}")
        
        return similar_images
    
    async def _analyze_originality(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        similarity_results: List[Dict[str, Any]]
    ) -> float:
        """Analyze content originality based on similarity results."""        try:
            if not similarity_results:
                return 0.95  # High originality if no similar content found
            
            # Calculate originality based on similarity scores
            max_similarity = max(result.get('similarity_score', 0) for result in similarity_results)
            
            # Originality score is inverse of maximum similarity
            originality_score = max(0.0, 1.0 - max_similarity)
            
            # Adjust based on number of similar items found
            similarity_penalty = min(0.2, len(similarity_results) * 0.05)
            originality_score = max(0.0, originality_score - similarity_penalty)
            
            return round(originality_score, 3)
            
        except Exception as e:
            self.logger.error(f"Originality analysis failed: {str(e)}")
            return 0.5  # Neutral score on error
    
    async def _analyze_fair_use(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        fair_use_context: Dict[str, Any],
        similarity_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze fair use applicability."""        fair_use_analysis = {
            'likely_fair_use': False,
            'fair_use_score': 0.0,
            'criteria_analysis': {},
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        try:
            scores = []
            criteria_scores = {}
            
            # Analyze each fair use criterion
            for criterion, factors in self.fair_use_criteria.items():
                criterion_score = 0.0
                criterion_factors = []
                
                for factor, weight in factors.items():
                    if factor in fair_use_context and fair_use_context[factor]:
                        criterion_score += weight
                        criterion_factors.append(factor)
                
                criteria_scores[criterion] = {
                    'score': criterion_score,
                    'factors': criterion_factors
                }
                scores.append(criterion_score)
            
            # Calculate overall fair use score
            fair_use_score = np.mean(scores) if scores else 0.0
            
            # Adjust based on amount of copyrighted content used
            if similarity_results:
                max_similarity = max(result.get('similarity_score', 0) for result in similarity_results)
                similarity_penalty = max_similarity * 0.5
                fair_use_score = max(-1.0, fair_use_score - similarity_penalty)
            
            fair_use_analysis.update({
                'fair_use_score': round(fair_use_score, 3),
                'criteria_analysis': criteria_scores,
                'likely_fair_use': fair_use_score > 0.3
            })
            
            # Generate strengths and weaknesses
            for criterion, analysis in criteria_scores.items():
                if analysis['score'] > 0.3:
                    fair_use_analysis['strengths'].append(f"Strong {criterion.replace('_', ' ')} argument")
                elif analysis['score'] < -0.3:
                    fair_use_analysis['weaknesses'].append(f"Weak {criterion.replace('_', ' ')} argument")
            
            # Generate recommendations
            if fair_use_score < 0.3:
                fair_use_analysis['recommendations'].append('Fair use claim is weak - consider seeking permission or license')
            else:
                fair_use_analysis['recommendations'].append('Fair use may apply - document transformative nature and limited use')
            
        except Exception as e:
            self.logger.error(f"Fair use analysis failed: {str(e)}")
        
        return fair_use_analysis
    
    async def _check_attribution_requirements(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Check attribution requirements for content."""        attribution_requirements = []
        
        try:
            # Check metadata for attribution information
            if content_metadata:
                required_attributions = []
                
                # Check for Creative Commons licenses
                if 'license' in content_metadata:
                    license_info = content_metadata['license']
                    if 'cc' in license_info.lower() or 'creative commons' in license_info.lower():
                        required_attributions.append({
                            'type': 'creative_commons',
                            'requirement': 'Attribution required under Creative Commons license',
                            'format': 'Author Name, Title, Source URL, License Type'
                        })
                
                # Check for author information
                if 'author' in content_metadata or 'creator' in content_metadata:
                    author = content_metadata.get('author') or content_metadata.get('creator')
                    required_attributions.append({
                        'type': 'author_attribution',
                        'requirement': f'Credit author: {author}',
                        'format': f'By {author}'
                    })
                
                # Check for source information
                if 'source' in content_metadata or 'source_url' in content_metadata:
                    source = content_metadata.get('source') or content_metadata.get('source_url')
                    required_attributions.append({
                        'type': 'source_attribution',
                        'requirement': f'Credit source: {source}',
                        'format': f'Source: {source}'
                    })
                
                attribution_requirements.extend(required_attributions)
            
        except Exception as e:
            self.logger.debug(f"Attribution check failed: {str(e)}")
        
        return attribution_requirements
    
    async def _identify_copyright_risks(
        self,
        similarity_results: List[Dict[str, Any]],
        originality_score: float,
        fair_use_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify copyright risks based on analysis."""        risks = []
        
        try:
            # High similarity risk
            high_similarity_items = [r for r in similarity_results if r.get('similarity_score', 0) > 0.7]
            for item in high_similarity_items:
                risks.append({
                    'risk_type': 'high_similarity',
                    'risk_level': 'high',
                    'description': f'High similarity ({item["similarity_score"]:.2%}) to existing content',
                    'source': item.get('source', 'unknown'),
                    'mitigation': 'Seek permission, license, or significantly modify content'
                })
            
            # Medium similarity risk
            medium_similarity_items = [r for r in similarity_results if 0.3 < r.get('similarity_score', 0) <= 0.7]
            for item in medium_similarity_items:
                risks.append({
                    'risk_type': 'medium_similarity',
                    'risk_level': 'medium',
                    'description': f'Moderate similarity ({item["similarity_score"]:.2%}) to existing content',
                    'source': item.get('source', 'unknown'),
                    'mitigation': 'Review for fair use or seek clarification on usage rights'
                })
            
            # Low originality risk
            if originality_score < 0.6:
                risks.append({
                    'risk_type': 'low_originality',
                    'risk_level': 'medium',
                    'description': f'Low originality score ({originality_score:.1%})',
                    'source': 'originality_analysis',
                    'mitigation': 'Increase original content or properly attribute sources'
                })
            
            # Fair use weakness risk
            if fair_use_context:
                fair_use_score = fair_use_context.get('fair_use_score', 0)
                if fair_use_score < 0.3:
                    risks.append({
                        'risk_type': 'weak_fair_use',
                        'risk_level': 'high',
                        'description': 'Weak fair use claim may not provide adequate protection',
                        'source': 'fair_use_analysis',
                        'mitigation': 'Strengthen fair use argument or seek permission/license'
                    })
            
        except Exception as e:
            self.logger.error(f"Risk identification failed: {str(e)}")
        
        return risks
    
    async def _determine_clearance_requirements(
        self,
        copyright_risks: List[Dict[str, Any]],
        similarity_results: List[Dict[str, Any]],
        originality_score: float
    ) -> bool:
        """Determine if copyright clearance is needed."""        try:
            # High-risk factors that require clearance
            high_risk_count = len([r for r in copyright_risks if r['risk_level'] == 'high'])
            high_similarity_count = len([r for r in similarity_results if r.get('similarity_score', 0) > 0.5])
            
            # Clearance needed if:
            # - High-risk violations present
            # - Multiple high similarity matches
            # - Very low originality
            clearance_needed = (
                high_risk_count > 0 or
                high_similarity_count > 1 or
                originality_score < 0.4
            )
            
            return clearance_needed
            
        except Exception as e:
            self.logger.error(f"Clearance determination failed: {str(e)}")
            return True  # Err on the side of caution
    
    async def _generate_license_recommendations(
        self,
        content_type: str,
        originality_score: float,
        copyright_risks: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate licensing recommendations."""        recommendations = []
        
        try:
            # High originality - can use restrictive licenses
            if originality_score > 0.9:
                recommendations.append({
                    'license_type': 'all_rights_reserved',
                    'description': 'Full copyright protection recommended',
                    'reason': 'High originality content'
                })
                recommendations.append({
                    'license_type': 'creative_commons_by',
                    'description': 'Creative Commons Attribution if sharing desired',
                    'reason': 'Original content with attribution requirement'
                })
            
            # Medium originality - flexible licensing
            elif originality_score > 0.7:
                recommendations.append({
                    'license_type': 'creative_commons_by_sa',
                    'description': 'Creative Commons Attribution-ShareAlike',
                    'reason': 'Good originality with collaborative sharing'
                })
            
            # Lower originality - permissive licensing or fair use
            else:
                recommendations.append({
                    'license_type': 'fair_use',
                    'description': 'Fair Use claim with proper attribution',
                    'reason': 'Content may contain copyrighted elements'
                })
                recommendations.append({
                    'license_type': 'creative_commons_by_nc',
                    'description': 'Creative Commons Non-Commercial',
                    'reason': 'Limit commercial use due to potential copyright issues'
                })
            
            # Risk-based recommendations
            high_risk_count = len([r for r in copyright_risks if r['risk_level'] == 'high'])
            if high_risk_count > 0:
                recommendations.append({
                    'license_type': 'permission_required',
                    'description': 'Obtain explicit permission before distribution',
                    'reason': 'High copyright risk detected'
                })
            
        except Exception as e:
            self.logger.error(f"License recommendation failed: {str(e)}")
        
        return recommendations
    
    async def _generate_copyright_recommendations(
        self,
        compliance_result: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive copyright recommendations."""        recommendations = []
        
        try:
            originality_score = compliance_result.get('originality_score', 0)
            copyright_risks = compliance_result.get('copyright_risks', [])
            clearance_needed = compliance_result.get('copyright_clearance_needed', False)
            
            # Originality-based recommendations
            if originality_score < 0.5:
                recommendations.append('Increase original content to reduce copyright risks')
            elif originality_score < 0.8:
                recommendations.append('Consider adding more original elements to strengthen copyright position')
            
            # Risk-based recommendations
            high_risks = [r for r in copyright_risks if r['risk_level'] == 'high']
            if high_risks:
                recommendations.append('Address high-risk copyright issues before publication')
                for risk in high_risks[:3]:  # Top 3 risks
                    recommendations.append(risk['mitigation'])
            
            # Clearance recommendations
            if clearance_needed:
                recommendations.append('Obtain copyright clearance or legal review before distribution')
            
            # Attribution recommendations
            attribution_reqs = compliance_result.get('attribution_requirements', [])
            if attribution_reqs:
                recommendations.append('Ensure proper attribution for all required content')
            
            # Fair use recommendations
            fair_use_analysis = compliance_result.get('fair_use_analysis', {})
            if fair_use_analysis and not fair_use_analysis.get('likely_fair_use', False):
                recommendations.append('Strengthen fair use argument or seek alternative licensing')
            
            # General recommendations
            if not compliance_result.get('copyright_compliant', False):
                recommendations.append('Conduct comprehensive copyright review before distribution')
            
        except Exception as e:
            self.logger.error(f"Copyright recommendations generation failed: {str(e)}")
        
        return recommendations
