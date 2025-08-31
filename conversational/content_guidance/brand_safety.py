"""Brand Safety Engine - Advanced Content Compliance and Safety Analysis
===================================================================

This module provides comprehensive brand safety analysis, content moderation,
and compliance checking for creators and brand partnerships.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import re
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import cv2
from PIL import Image
import librosa
import textblob

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.ml.safety_classifier import SafetyClassificationEngine
from backend.ai.cv.content_analyzer import ContentVisionAnalyzer
from backend.ai.nlp.sentiment_analyzer import SentimentAnalysisEngine

logger = get_logger(__name__)
settings = get_settings()


class SafetyRiskLevel(Enum):
    """Content safety risk levels."""    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    UNSAFE = "unsafe"


class SafetyCategory(Enum):
    """Content safety categories."""    EXPLICIT_CONTENT = "explicit_content"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    COPYRIGHT = "copyright"
    SPAM = "spam"
    DANGEROUS_ACTIVITIES = "dangerous_activities"
    INAPPROPRIATE_LANGUAGE = "inappropriate_language"
    BRAND_CONFLICTS = "brand_conflicts"
    LEGAL_VIOLATIONS = "legal_violations"
    UNDERAGE_CONTENT = "underage_content"


class BrandSafetyStandard(Enum):
    """Brand safety standard levels."""    CONSERVATIVE = "conservative"     # Family-friendly, strict standards
    MODERATE = "moderate"            # Mainstream brand safe
    LIBERAL = "liberal"              # More relaxed, adult-oriented
    CUSTOM = "custom"                # Custom brand guidelines


class ComplianceFramework(Enum):
    """Compliance frameworks."""    COPPA = "coppa"                  # Children's Online Privacy Protection Act
    GDPR = "gdpr"                    # General Data Protection Regulation
    FTC_GUIDELINES = "ftc_guidelines" # Federal Trade Commission Guidelines
    PLATFORM_POLICIES = "platform_policies"  # Platform-specific policies
    ADVERTISING_STANDARDS = "advertising_standards"
    ACCESSIBILITY = "accessibility"   # Accessibility compliance


@dataclass
class SafetyAnalysisResult:
    """Result of content safety analysis."""    content_id: str
    overall_risk_level: SafetyRiskLevel
    safety_score: float  # 0-1, higher is safer
    detected_issues: List[Dict[str, Any]]
    flagged_categories: List[SafetyCategory]
    confidence_scores: Dict[SafetyCategory, float]
    recommendations: List[str]
    requires_manual_review: bool
    approved_for_brands: List[str]
    restricted_for_brands: List[str]
    analysis_metadata: Dict[str, Any]
    analyzed_at: datetime


@dataclass
class BrandCompatibilityScore:
    """Brand compatibility analysis result."""    brand_name: str
    compatibility_score: float
    risk_assessment: SafetyRiskLevel
    alignment_factors: Dict[str, float]
    potential_conflicts: List[str]
    recommendations: List[str]
    content_guidelines: Dict[str, str]
    approval_probability: float


@dataclass
class ComplianceCheckResult:
    """Compliance framework check result."""    framework: ComplianceFramework
    compliance_status: str
    compliance_score: float
    violations: List[Dict[str, Any]]
    requirements: List[str]
    recommendations: List[str]
    next_review_date: datetime


@dataclass
class ContentModerationReport:
    """Comprehensive content moderation report."""    report_id: str
    content_id: str
    creator_id: str
    content_type: str
    safety_analysis: SafetyAnalysisResult
    brand_compatibility: List[BrandCompatibilityScore]
    compliance_checks: List[ComplianceCheckResult]
    moderation_actions: List[str]
    escalation_required: bool
    reviewer_notes: List[str]
    final_decision: str
    generated_at: datetime


class ContentComplianceEngine:
    """    Advanced AI-powered content compliance engine that analyzes content
    for brand safety, legal compliance, and platform policy adherence.
    """    
    def __init__(self):
        """Initialize the content compliance engine."""        self.safety_classifier = SafetyClassificationEngine()
        self.vision_analyzer = ContentVisionAnalyzer()
        self.sentiment_analyzer = SentimentAnalysisEngine()
        
        # ML models for safety analysis
        self.text_safety_model = RandomForestClassifier(n_estimators=200)
        self.image_safety_model = GradientBoostingClassifier(n_estimators=150)
        self.video_safety_model = MLPClassifier(hidden_layer_sizes=(100, 50))
        self.brand_compatibility_model = RandomForestClassifier(n_estimators=100)
        
        # Text processing
        self.text_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.scaler = StandardScaler()
        
        # Safety keyword databases
        self.safety_keywords = self._load_safety_keywords()
        self.brand_safety_guidelines = self._load_brand_guidelines()
        self.compliance_rules = self._load_compliance_rules()
        
        # Content analysis thresholds
        self.safety_thresholds = {
            SafetyRiskLevel.SAFE: 0.9,
            SafetyRiskLevel.LOW_RISK: 0.7,
            SafetyRiskLevel.MEDIUM_RISK: 0.5,
            SafetyRiskLevel.HIGH_RISK: 0.3,
            SafetyRiskLevel.UNSAFE: 0.0
        }
        
        # Load and train models
        self._load_and_train_models()
        
        logger.info("Content compliance engine initialized successfully")
    
    def _load_safety_keywords(self) -> Dict[SafetyCategory, List[str]]:
        """Load safety-related keywords for each category."""        
        return {
            SafetyCategory.EXPLICIT_CONTENT: [
                'nude', 'naked', 'explicit', 'sexual', 'pornographic', 'adult',
                'xxx', 'nsfw', 'mature', 'erotic'
            ],
            SafetyCategory.VIOLENCE: [
                'violence', 'violent', 'fight', 'killing', 'murder', 'assault',
                'weapon', 'gun', 'knife', 'blood', 'death', 'war'
            ],
            SafetyCategory.HATE_SPEECH: [
                'hate', 'racist', 'discrimination', 'bigot', 'prejudice',
                'offensive', 'slur', 'supremacist', 'nazi', 'fascist'
            ],
            SafetyCategory.HARASSMENT: [
                'harassment', 'bullying', 'stalking', 'threatening', 'intimidation',
                'doxxing', 'cyberbullying', 'abuse', 'humiliation'
            ],
            SafetyCategory.MISINFORMATION: [
                'fake news', 'conspiracy', 'hoax', 'misinformation', 'false claim',
                'debunked', 'myth', 'pseudoscience', 'unverified'
            ],
            SafetyCategory.DANGEROUS_ACTIVITIES: [
                'dangerous', 'risky', 'unsafe', 'stunt', 'extreme',
                'self-harm', 'suicide', 'overdose', 'drunk driving'
            ],
            SafetyCategory.INAPPROPRIATE_LANGUAGE: [
                'profanity', 'curse', 'swear', 'vulgar', 'obscene',
                'inappropriate', 'offensive language', 'bad words'
            ]
        }
    
    def _load_brand_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load brand-specific safety guidelines."""        
        return {
            'conservative_brand': {
                'allowed_content': ['family_friendly', 'educational', 'inspirational'],
                'restricted_content': ['controversial', 'political', 'adult_themes'],
                'language_restrictions': ['no_profanity', 'positive_tone'],
                'visual_requirements': ['modest_clothing', 'appropriate_imagery'],
                'safety_threshold': 0.95
            },
            'mainstream_brand': {
                'allowed_content': ['entertainment', 'lifestyle', 'educational', 'humor'],
                'restricted_content': ['extreme_political', 'explicit_content'],
                'language_restrictions': ['minimal_profanity', 'respectful_tone'],
                'visual_requirements': ['appropriate_imagery', 'brand_aligned'],
                'safety_threshold': 0.8
            },
            'progressive_brand': {
                'allowed_content': ['diverse_topics', 'social_issues', 'adult_themes'],
                'restricted_content': ['hate_speech', 'misinformation'],
                'language_restrictions': ['authentic_expression', 'no_hate_speech'],
                'visual_requirements': ['inclusive_imagery', 'authentic_representation'],
                'safety_threshold': 0.7
            }
        }
    
    def _load_compliance_rules(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Load compliance framework rules."""        
        return {
            ComplianceFramework.COPPA: {
                'applies_to': ['content_targeting_children', 'under_13_audience'],
                'requirements': [
                    'no_personal_data_collection',
                    'parental_consent_required',
                    'appropriate_content_only',
                    'no_behavioral_advertising'
                ],
                'prohibited_content': ['inappropriate_for_children', 'data_collection'],
                'disclosure_requirements': ['child_directed_disclosure']
            },
            ComplianceFramework.FTC_GUIDELINES: {
                'applies_to': ['sponsored_content', 'affiliate_marketing', 'endorsements'],
                'requirements': [
                    'clear_disclosure',
                    'honest_testimonials',
                    'material_connection_disclosure',
                    'truthful_claims'
                ],
                'disclosure_keywords': ['#ad', '#sponsored', '#partnership', '#affiliate'],
                'prohibited_practices': ['hidden_advertising', 'false_claims']
            },
            ComplianceFramework.GDPR: {
                'applies_to': ['eu_audience', 'personal_data'],
                'requirements': [
                    'data_protection_notice',
                    'consent_management',
                    'right_to_erasure',
                    'data_portability'
                ],
                'data_categories': ['personal_identifiers', 'behavioral_data'],
                'consent_requirements': ['explicit_consent', 'withdrawable_consent']
            }
        }
    
    def _load_and_train_models(self):
        """Load historical data and train ML models for safety analysis."""        try:
            # Generate synthetic training data for safety classification
            n_samples = 20000
            
            # Text safety features
            text_features = np.random.rand(n_samples, 100)
            
            # Add realistic patterns for unsafe content
            for i in range(n_samples):
                # Simulate keyword presence
                keyword_score = np.random.beta(1, 5)  # Most content is safe
                text_features[i][0] = keyword_score
                
                # Sentiment features
                sentiment_score = np.random.normal(0.5, 0.3)
                text_features[i][1] = max(0, min(1, sentiment_score))
                
                # Language complexity
                complexity = np.random.gamma(2, 0.3)
                text_features[i][2] = min(1, complexity)
            
            # Generate safety labels
            safety_labels = []
            for i in range(n_samples):
                # Base safety on keyword and sentiment scores
                safety_score = (
                    (1 - text_features[i][0]) * 0.4 +  # Lower keyword score = safer
                    text_features[i][1] * 0.3 +        # Higher sentiment = safer
                    np.random.rand() * 0.3             # Random factors
                )
                
                if safety_score > 0.8:
                    safety_labels.append('safe')
                elif safety_score > 0.6:
                    safety_labels.append('low_risk')
                elif safety_score > 0.4:
                    safety_labels.append('medium_risk')
                elif safety_score > 0.2:
                    safety_labels.append('high_risk')
                else:
                    safety_labels.append('unsafe')
            
            # Train text safety model
            self.text_safety_model.fit(text_features, safety_labels)
            
            # Train image safety model (simplified)
            image_features = np.random.rand(n_samples, 50)
            image_labels = np.random.choice(['safe', 'unsafe'], n_samples, p=[0.85, 0.15])
            self.image_safety_model.fit(image_features, image_labels)
            
            # Train brand compatibility model
            brand_features = np.random.rand(n_samples, 30)
            brand_compatibility = np.random.beta(3, 2, n_samples)  # Most content is somewhat compatible
            self.brand_compatibility_model.fit(brand_features, brand_compatibility > 0.6)
            
            # Fit scaler
            self.scaler.fit(text_features)
            
            logger.info("Content safety ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train content safety models: {e}")
            # Continue with default models
    
    async def analyze_content_safety(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        safety_standards: BrandSafetyStandard = BrandSafetyStandard.MODERATE
    ) -> SafetyAnalysisResult:
        """        Analyze content for safety and brand compliance.
        
        Args:
            content_id: Unique content identifier
            content_data: Content to analyze (text, images, video, audio)
            safety_standards: Safety standard level to apply
            
        Returns:
            Comprehensive safety analysis result
        """        
        try:
            detected_issues = []
            flagged_categories = []
            confidence_scores = {}
            
            # Analyze text content
            if 'text' in content_data:
                text_results = await self._analyze_text_safety(
                    content_data['text'], safety_standards
                )
                detected_issues.extend(text_results['issues'])
                flagged_categories.extend(text_results['categories'])
                confidence_scores.update(text_results['confidence'])
            
            # Analyze image content
            if 'images' in content_data:
                for image_data in content_data['images']:
                    image_results = await self._analyze_image_safety(
                        image_data, safety_standards
                    )
                    detected_issues.extend(image_results['issues'])
                    flagged_categories.extend(image_results['categories'])
                    confidence_scores.update(image_results['confidence'])
            
            # Analyze video content
            if 'video' in content_data:
                video_results = await self._analyze_video_safety(
                    content_data['video'], safety_standards
                )
                detected_issues.extend(video_results['issues'])
                flagged_categories.extend(video_results['categories'])
                confidence_scores.update(video_results['confidence'])
            
            # Analyze audio content
            if 'audio' in content_data:
                audio_results = await self._analyze_audio_safety(
                    content_data['audio'], safety_standards
                )
                detected_issues.extend(audio_results['issues'])
                flagged_categories.extend(audio_results['categories'])
                confidence_scores.update(audio_results['confidence'])
            
            # Calculate overall safety score
            overall_safety_score = self._calculate_overall_safety_score(
                detected_issues, confidence_scores
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_safety_score)
            
            # Generate recommendations
            recommendations = self._generate_safety_recommendations(
                detected_issues, flagged_categories, safety_standards
            )
            
            # Determine if manual review is required
            requires_manual_review = self._requires_manual_review(
                risk_level, detected_issues, safety_standards
            )
            
            # Determine brand approvals
            approved_brands, restricted_brands = self._determine_brand_approvals(
                overall_safety_score, flagged_categories, safety_standards
            )
            
            result = SafetyAnalysisResult(
                content_id=content_id,
                overall_risk_level=risk_level,
                safety_score=overall_safety_score,
                detected_issues=detected_issues,
                flagged_categories=list(set(flagged_categories)),
                confidence_scores=confidence_scores,
                recommendations=recommendations,
                requires_manual_review=requires_manual_review,
                approved_for_brands=approved_brands,
                restricted_for_brands=restricted_brands,
                analysis_metadata={
                    'safety_standards': safety_standards.value,
                    'content_types_analyzed': list(content_data.keys()),
                    'total_issues_detected': len(detected_issues)
                },
                analyzed_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"Content safety analysis completed for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze content safety: {e}")
            # Return safe default result
            return SafetyAnalysisResult(
                content_id=content_id,
                overall_risk_level=SafetyRiskLevel.MEDIUM_RISK,
                safety_score=0.5,
                detected_issues=[],
                flagged_categories=[],
                confidence_scores={},
                recommendations=["Manual review recommended due to analysis error"],
                requires_manual_review=True,
                approved_for_brands=[],
                restricted_for_brands=[],
                analysis_metadata={'error': str(e)},
                analyzed_at=datetime.now(timezone.utc)
            )
    
    async def _analyze_text_safety(
        self, text_content: str, safety_standards: BrandSafetyStandard
    ) -> Dict[str, Any]:
        """Analyze text content for safety issues."""        
        issues = []
        categories = []
        confidence = {}
        
        # Keyword analysis
        text_lower = text_content.lower()
        
        for category, keywords in self.safety_keywords.items():
            keyword_matches = []
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_matches.append(keyword)
            
            if keyword_matches:
                categories.append(category)
                confidence[category] = min(1.0, len(keyword_matches) / len(keywords))
                
                issues.append({
                    'type': 'keyword_detection',
                    'category': category.value,
                    'severity': 'high' if len(keyword_matches) > 2 else 'medium',
                    'details': f"Detected keywords: {', '.join(keyword_matches)}",
                    'location': 'text_content'
                })
        
        # Sentiment analysis
        try:
            blob = textblob.TextBlob(text_content)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score < -0.5:
                categories.append(SafetyCategory.INAPPROPRIATE_LANGUAGE)
                confidence[SafetyCategory.INAPPROPRIATE_LANGUAGE] = abs(sentiment_score)
                
                issues.append({
                    'type': 'negative_sentiment',
                    'category': 'inappropriate_language',
                    'severity': 'medium',
                    'details': f"Highly negative sentiment detected (score: {sentiment_score:.2f})",
                    'location': 'text_content'
                })
        
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
        
        # Profanity detection (simple pattern matching)
        profanity_patterns = [
            r'\b(damn|hell|shit|fuck|bitch|ass)\b',
            r'\b[a-z]*fuck[a-z]*\b',
            r'\b[a-z]*shit[a-z]*\b'
        ]
        
        for pattern in profanity_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                if SafetyCategory.INAPPROPRIATE_LANGUAGE not in categories:
                    categories.append(SafetyCategory.INAPPROPRIATE_LANGUAGE)
                
                confidence[SafetyCategory.INAPPROPRIATE_LANGUAGE] = min(
                    1.0, 
                    confidence.get(SafetyCategory.INAPPROPRIATE_LANGUAGE, 0) + len(matches) * 0.2
                )
                
                issues.append({
                    'type': 'profanity_detection',
                    'category': 'inappropriate_language',
                    'severity': 'medium',
                    'details': f"Profanity detected: {', '.join(set(matches))}",
                    'location': 'text_content'
                })
        
        # Check for promotional disclosure compliance
        disclosure_keywords = ['#ad', '#sponsored', '#partnership', '#affiliate', 'paid promotion']
        has_promotional_content = any(
            keyword in text_lower for keyword in ['review', 'recommend', 'love this', 'amazing product']
        )
        has_disclosure = any(
            keyword in text_lower for keyword in disclosure_keywords
        )
        
        if has_promotional_content and not has_disclosure:
            issues.append({
                'type': 'missing_disclosure',
                'category': 'legal_compliance',
                'severity': 'high',
                'details': "Potential promotional content without proper disclosure",
                'location': 'text_content'
            })
        
        return {
            'issues': issues,
            'categories': categories,
            'confidence': confidence
        }
    
    async def _analyze_image_safety(
        self, image_data: Union[str, bytes, np.ndarray], safety_standards: BrandSafetyStandard
    ) -> Dict[str, Any]:
        """Analyze image content for safety issues."""        
        issues = []
        categories = []
        confidence = {}
        
        try:
            # This would use actual computer vision models in production
            # For now, simulate image analysis
            
            # Simulate explicit content detection
            explicit_score = np.random.random()
            if explicit_score > 0.8:
                categories.append(SafetyCategory.EXPLICIT_CONTENT)
                confidence[SafetyCategory.EXPLICIT_CONTENT] = explicit_score
                
                issues.append({
                    'type': 'explicit_content_detection',
                    'category': 'explicit_content',
                    'severity': 'high',
                    'details': f"Potential explicit content detected (confidence: {explicit_score:.2f})",
                    'location': 'image_content'
                })
            
            # Simulate violence detection
            violence_score = np.random.random() * 0.3  # Lower probability
            if violence_score > 0.2:
                categories.append(SafetyCategory.VIOLENCE)
                confidence[SafetyCategory.VIOLENCE] = violence_score
                
                issues.append({
                    'type': 'violence_detection',
                    'category': 'violence',
                    'severity': 'medium',
                    'details': f"Potential violent content detected (confidence: {violence_score:.2f})",
                    'location': 'image_content'
                })
            
            # Simulate text in image analysis (OCR)
            # This would extract and analyze text from images
            extracted_text = ""  # Placeholder
            if extracted_text:
                text_analysis = await self._analyze_text_safety(extracted_text, safety_standards)
                issues.extend(text_analysis['issues'])
                categories.extend(text_analysis['categories'])
                confidence.update(text_analysis['confidence'])
        
        except Exception as e:
            logger.warning(f"Image safety analysis failed: {e}")
            issues.append({
                'type': 'analysis_error',
                'category': 'technical_issue',
                'severity': 'medium',
                'details': f"Image analysis failed: {str(e)}",
                'location': 'image_content'
            })
        
        return {
            'issues': issues,
            'categories': categories,
            'confidence': confidence
        }
    
    async def _analyze_video_safety(
        self, video_data: Union[str, bytes], safety_standards: BrandSafetyStandard
    ) -> Dict[str, Any]:
        """Analyze video content for safety issues."""        
        issues = []
        categories = []
        confidence = {}
        
        try:
            # This would use actual video analysis in production
            # For now, simulate video analysis
            
            # Simulate frame-by-frame analysis
            frame_analysis_results = []
            for frame_num in range(0, 10):  # Analyze 10 sample frames
                # Simulate image analysis for each frame
                frame_result = await self._analyze_image_safety(
                    np.random.rand(224, 224, 3), safety_standards
                )
                frame_analysis_results.append(frame_result)
            
            # Aggregate frame results
            for frame_result in frame_analysis_results:
                issues.extend(frame_result['issues'])
                categories.extend(frame_result['categories'])
                
                # Update confidence scores (take maximum)
                for cat, conf in frame_result['confidence'].items():
                    confidence[cat] = max(confidence.get(cat, 0), conf)
            
            # Simulate audio analysis from video
            # This would extract and analyze audio track
            audio_analysis = {
                'issues': [],
                'categories': [],
                'confidence': {}
            }
            
            issues.extend(audio_analysis['issues'])
            categories.extend(audio_analysis['categories'])
            confidence.update(audio_analysis['confidence'])
        
        except Exception as e:
            logger.warning(f"Video safety analysis failed: {e}")
            issues.append({
                'type': 'analysis_error',
                'category': 'technical_issue',
                'severity': 'medium',
                'details': f"Video analysis failed: {str(e)}",
                'location': 'video_content'
            })
        
        return {
            'issues': issues,
            'categories': categories,
            'confidence': confidence
        }
    
    async def _analyze_audio_safety(
        self, audio_data: Union[str, bytes], safety_standards: BrandSafetyStandard
    ) -> Dict[str, Any]:
        """Analyze audio content for safety issues."""        
        issues = []
        categories = []
        confidence = {}
        
        try:
            # This would use actual audio analysis in production
            # Including speech-to-text and audio classification
            
            # Simulate speech-to-text conversion
            transcribed_text = ""  # Placeholder for actual transcription
            
            if transcribed_text:
                # Analyze transcribed text
                text_analysis = await self._analyze_text_safety(transcribed_text, safety_standards)
                issues.extend(text_analysis['issues'])
                categories.extend(text_analysis['categories'])
                confidence.update(text_analysis['confidence'])
            
            # Simulate audio characteristics analysis
            # This would analyze volume levels, frequency patterns, etc.
            volume_analysis = np.random.random()
            if volume_analysis > 0.9:  # Very loud audio
                issues.append({
                    'type': 'audio_quality',
                    'category': 'technical_issue',
                    'severity': 'low',
                    'details': "Audio volume levels may be too high",
                    'location': 'audio_content'
                })
        
        except Exception as e:
            logger.warning(f"Audio safety analysis failed: {e}")
            issues.append({
                'type': 'analysis_error',
                'category': 'technical_issue',
                'severity': 'medium',
                'details': f"Audio analysis failed: {str(e)}",
                'location': 'audio_content'
            })
        
        return {
            'issues': issues,
            'categories': categories,
            'confidence': confidence
        }
    
    def _calculate_overall_safety_score(
        self, detected_issues: List[Dict[str, Any]], confidence_scores: Dict[SafetyCategory, float]
    ) -> float:
        """Calculate overall safety score from detected issues."""        
        if not detected_issues:
            return 1.0  # Perfect safety score
        
        # Calculate penalty based on issue severity and confidence
        total_penalty = 0
        severity_weights = {'low': 0.1, 'medium': 0.3, 'high': 0.6}
        
        for issue in detected_issues:
            severity = issue.get('severity', 'medium')
            penalty = severity_weights.get(severity, 0.3)
            
            # Adjust penalty based on confidence if available
            category_name = issue.get('category', '')
            category_enum = None
            
            # Find matching enum
            for cat in SafetyCategory:
                if cat.value == category_name:
                    category_enum = cat
                    break
            
            if category_enum and category_enum in confidence_scores:
                confidence = confidence_scores[category_enum]
                penalty *= confidence  # Higher confidence = higher penalty
            
            total_penalty += penalty
        
        # Calculate safety score (1.0 - normalized penalty)
        max_possible_penalty = len(detected_issues) * 0.6  # Assuming all high severity
        normalized_penalty = min(1.0, total_penalty / max(max_possible_penalty, 1))
        
        safety_score = 1.0 - normalized_penalty
        
        return max(0.0, safety_score)
    
    def _determine_risk_level(self, safety_score: float) -> SafetyRiskLevel:
        """Determine risk level based on safety score."""        
        for risk_level, threshold in self.safety_thresholds.items():
            if safety_score >= threshold:
                return risk_level
        
        return SafetyRiskLevel.UNSAFE
    
    def _generate_safety_recommendations(
        self,
        detected_issues: List[Dict[str, Any]],
        flagged_categories: List[SafetyCategory],
        safety_standards: BrandSafetyStandard
    ) -> List[str]:
        """Generate safety improvement recommendations."""        
        recommendations = []
        
        # Category-specific recommendations
        if SafetyCategory.EXPLICIT_CONTENT in flagged_categories:
            recommendations.append("Remove or blur explicit visual content")
            recommendations.append("Add content warning if targeting mature audiences")
        
        if SafetyCategory.INAPPROPRIATE_LANGUAGE in flagged_categories:
            recommendations.append("Replace profanity with acceptable alternatives")
            recommendations.append("Consider audience age demographics when choosing language")
        
        if SafetyCategory.VIOLENCE in flagged_categories:
            recommendations.append("Remove violent imagery or add appropriate warnings")
            recommendations.append("Consider platform-specific violence policies")
        
        if SafetyCategory.MISINFORMATION in flagged_categories:
            recommendations.append("Verify claims with reliable sources")
            recommendations.append("Add disclaimers for opinions vs. facts")
        
        # Missing disclosure issues
        disclosure_issues = [
            issue for issue in detected_issues 
            if issue.get('type') == 'missing_disclosure'
        ]
        if disclosure_issues:
            recommendations.append("Add proper FTC-compliant disclosure for sponsored content")
            recommendations.append("Use clear hashtags like #ad, #sponsored, or #partnership")
        
        # General recommendations based on safety standards
        if safety_standards == BrandSafetyStandard.CONSERVATIVE:
            recommendations.append("Ensure all content is family-friendly")
            recommendations.append("Avoid controversial topics and maintain positive tone")
        
        elif safety_standards == BrandSafetyStandard.MODERATE:
            recommendations.append("Maintain mainstream brand-safe content standards")
            recommendations.append("Balance authenticity with brand safety requirements")
        
        # If no specific issues, provide general guidance
        if not recommendations:
            recommendations.append("Content meets safety standards for most brand partnerships")
            recommendations.append("Consider adding content warnings for sensitive topics")
        
        return recommendations
    
    def _requires_manual_review(
        self,
        risk_level: SafetyRiskLevel,
        detected_issues: List[Dict[str, Any]],
        safety_standards: BrandSafetyStandard
    ) -> bool:
        """Determine if content requires manual review."""        
        # High risk always requires review
        if risk_level in [SafetyRiskLevel.HIGH_RISK, SafetyRiskLevel.UNSAFE]:
            return True
        
        # Conservative standards require review for medium risk
        if safety_standards == BrandSafetyStandard.CONSERVATIVE and risk_level == SafetyRiskLevel.MEDIUM_RISK:
            return True
        
        # Specific issue types require review
        review_required_types = ['missing_disclosure', 'explicit_content_detection', 'violence_detection']
        
        for issue in detected_issues:
            if issue.get('type') in review_required_types:
                return True
            if issue.get('severity') == 'high':
                return True
        
        return False
    
    def _determine_brand_approvals(
        self,
        safety_score: float,
        flagged_categories: List[SafetyCategory],
        safety_standards: BrandSafetyStandard
    ) -> Tuple[List[str], List[str]]:
        """Determine which brands would approve or restrict this content."""        
        approved_brands = []
        restricted_brands = []
        
        # Conservative brands
        conservative_brands = ['disney', 'coca_cola', 'mcdonalds', 'walmart']
        if (safety_score >= 0.9 and 
            not any(cat in flagged_categories for cat in [
                SafetyCategory.EXPLICIT_CONTENT, 
                SafetyCategory.VIOLENCE, 
                SafetyCategory.INAPPROPRIATE_LANGUAGE
            ])):
            approved_brands.extend(conservative_brands)
        else:
            restricted_brands.extend(conservative_brands)
        
        # Mainstream brands
        mainstream_brands = ['nike', 'apple', 'samsung', 'starbucks']
        if safety_score >= 0.7:
            approved_brands.extend(mainstream_brands)
        else:
            restricted_brands.extend(mainstream_brands)
        
        # Progressive brands
        progressive_brands = ['netflix', 'spotify', 'airbnb', 'uber']
        if (safety_score >= 0.6 and 
            not any(cat in flagged_categories for cat in [
                SafetyCategory.HATE_SPEECH, 
                SafetyCategory.MISINFORMATION
            ])):
            approved_brands.extend(progressive_brands)
        else:
            restricted_brands.extend(progressive_brands)
        
        return approved_brands, restricted_brands
    
    async def check_brand_compatibility(
        self,
        content_id: str,
        brand_name: str,
        brand_guidelines: Dict[str, Any],
        safety_analysis: SafetyAnalysisResult
    ) -> BrandCompatibilityScore:
        """        Check content compatibility with specific brand guidelines.
        
        Args:
            content_id: Content identifier
            brand_name: Brand name to check compatibility against
            brand_guidelines: Brand-specific guidelines and requirements
            safety_analysis: Previously completed safety analysis
            
        Returns:
            Brand compatibility score and recommendations
        """        
        try:
            # Analyze alignment factors
            alignment_factors = {}
            
            # Safety score alignment
            required_safety_threshold = brand_guidelines.get('safety_threshold', 0.8)
            safety_alignment = min(1.0, safety_analysis.safety_score / required_safety_threshold)
            alignment_factors['safety_score'] = safety_alignment
            
            # Content category alignment
            allowed_categories = brand_guidelines.get('allowed_content', [])
            restricted_categories = brand_guidelines.get('restricted_content', [])
            
            # This would analyze actual content categories
            content_categories = ['lifestyle', 'entertainment']  # Placeholder
            
            category_score = 0
            for category in content_categories:
                if category in allowed_categories:
                    category_score += 1
                elif category in restricted_categories:
                    category_score -= 1
            
            category_alignment = max(0, min(1, (category_score + len(content_categories)) / (2 * len(content_categories))))
            alignment_factors['content_categories'] = category_alignment
            
            # Visual requirements alignment
            visual_requirements = brand_guidelines.get('visual_requirements', [])
            visual_alignment = 0.8  # Placeholder - would analyze actual visual content
            alignment_factors['visual_requirements'] = visual_alignment
            
            # Language requirements alignment
            language_restrictions = brand_guidelines.get('language_restrictions', [])
            language_alignment = 0.9  # Placeholder - based on language analysis
            alignment_factors['language_compliance'] = language_alignment
            
            # Calculate overall compatibility score
            weights = {
                'safety_score': 0.4,
                'content_categories': 0.3,
                'visual_requirements': 0.2,
                'language_compliance': 0.1
            }
            
            compatibility_score = sum(
                alignment_factors[factor] * weights.get(factor, 0.25)
                for factor in alignment_factors
            )
            
            # Determine risk assessment
            if compatibility_score >= 0.8:
                risk_assessment = SafetyRiskLevel.SAFE
            elif compatibility_score >= 0.6:
                risk_assessment = SafetyRiskLevel.LOW_RISK
            elif compatibility_score >= 0.4:
                risk_assessment = SafetyRiskLevel.MEDIUM_RISK
            else:
                risk_assessment = SafetyRiskLevel.HIGH_RISK
            
            # Identify potential conflicts
            potential_conflicts = []
            
            for flagged_category in safety_analysis.flagged_categories:
                if flagged_category.value in restricted_categories:
                    potential_conflicts.append(f"Content contains {flagged_category.value} which is restricted by {brand_name}")
            
            if safety_analysis.safety_score < required_safety_threshold:
                potential_conflicts.append(f"Safety score ({safety_analysis.safety_score:.2f}) below brand requirement ({required_safety_threshold})")
            
            # Generate recommendations
            recommendations = []
            
            if compatibility_score < 0.8:
                recommendations.append("Content modifications recommended for optimal brand alignment")
            
            if potential_conflicts:
                recommendations.append("Address flagged content issues before brand partnership")
            
            if safety_analysis.requires_manual_review:
                recommendations.append("Manual review recommended before brand approval")
            
            # Content guidelines
            content_guidelines = {
                'tone': brand_guidelines.get('preferred_tone', 'professional'),
                'visual_style': brand_guidelines.get('visual_style', 'clean and modern'),
                'messaging': brand_guidelines.get('key_messages', []),
                'avoid': restricted_categories
            }
            
            # Calculate approval probability
            approval_probability = compatibility_score * (1 - len(potential_conflicts) * 0.1)
            approval_probability = max(0, min(1, approval_probability))
            
            return BrandCompatibilityScore(
                brand_name=brand_name,
                compatibility_score=compatibility_score,
                risk_assessment=risk_assessment,
                alignment_factors=alignment_factors,
                potential_conflicts=potential_conflicts,
                recommendations=recommendations,
                content_guidelines=content_guidelines,
                approval_probability=approval_probability
            )
            
        except Exception as e:
            logger.error(f"Failed to check brand compatibility: {e}")
            return BrandCompatibilityScore(
                brand_name=brand_name,
                compatibility_score=0.5,
                risk_assessment=SafetyRiskLevel.MEDIUM_RISK,
                alignment_factors={},
                potential_conflicts=[f"Analysis error: {str(e)}"],
                recommendations=["Manual review required due to analysis error"],
                content_guidelines={},
                approval_probability=0.3
            )
    
    async def check_compliance(
        self,
        content_data: Dict[str, Any],
        frameworks: List[ComplianceFramework],
        target_audience: Dict[str, Any] = None
    ) -> List[ComplianceCheckResult]:
        """        Check content compliance against regulatory frameworks.
        
        Args:
            content_data: Content to check for compliance
            frameworks: Compliance frameworks to check against
            target_audience: Target audience information
            
        Returns:
            List of compliance check results
        """        
        results = []
        
        for framework in frameworks:
            try:
                result = await self._check_framework_compliance(
                    content_data, framework, target_audience
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to check {framework.value} compliance: {e}")
                
                # Return error result
                error_result = ComplianceCheckResult(
                    framework=framework,
                    compliance_status="error",
                    compliance_score=0.0,
                    violations=[{
                        'type': 'analysis_error',
                        'description': f"Compliance check failed: {str(e)}",
                        'severity': 'high'
                    }],
                    requirements=[],
                    recommendations=["Manual compliance review required"],
                    next_review_date=datetime.now(timezone.utc) + timedelta(days=7)
                )
                results.append(error_result)
        
        return results
    
    async def _check_framework_compliance(
        self,
        content_data: Dict[str, Any],
        framework: ComplianceFramework,
        target_audience: Dict[str, Any] = None
    ) -> ComplianceCheckResult:
        """Check compliance against a specific framework."""        
        framework_rules = self.compliance_rules.get(framework, {})
        violations = []
        requirements = framework_rules.get('requirements', [])
        
        # COPPA compliance check
        if framework == ComplianceFramework.COPPA:
            violations.extend(await self._check_coppa_compliance(content_data, target_audience))
        
        # FTC Guidelines compliance check
        elif framework == ComplianceFramework.FTC_GUIDELINES:
            violations.extend(await self._check_ftc_compliance(content_data))
        
        # GDPR compliance check
        elif framework == ComplianceFramework.GDPR:
            violations.extend(await self._check_gdpr_compliance(content_data, target_audience))
        
        # Calculate compliance score
        if not requirements:
            compliance_score = 1.0 if not violations else 0.5
        else:
            violation_penalty = len(violations) * 0.2
            compliance_score = max(0.0, 1.0 - violation_penalty)
        
        # Determine compliance status
        if compliance_score >= 0.9:
            status = "compliant"
        elif compliance_score >= 0.7:
            status = "mostly_compliant"
        elif compliance_score >= 0.5:
            status = "partially_compliant"
        else:
            status = "non_compliant"
        
        # Generate recommendations
        recommendations = []
        for violation in violations:
            if violation['type'] == 'missing_disclosure':
                recommendations.append("Add proper disclosure statements")
            elif violation['type'] == 'data_collection':
                recommendations.append("Implement proper data collection consent")
            elif violation['type'] == 'age_inappropriate':
                recommendations.append("Review content for age-appropriate messaging")
        
        # Set next review date
        next_review = datetime.now(timezone.utc) + timedelta(days=30)
        if violations:
            next_review = datetime.now(timezone.utc) + timedelta(days=7)
        
        return ComplianceCheckResult(
            framework=framework,
            compliance_status=status,
            compliance_score=compliance_score,
            violations=violations,
            requirements=requirements,
            recommendations=recommendations,
            next_review_date=next_review
        )
    
    async def _check_coppa_compliance(
        self, content_data: Dict[str, Any], target_audience: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Check COPPA compliance for child-directed content."""        
        violations = []
        
        # Check if content is directed at children
        if target_audience:
            age_groups = target_audience.get('age_distribution', {})
            under_13_percentage = age_groups.get('under_13', 0)
            
            if under_13_percentage > 0.3:  # Significant child audience
                # Check for prohibited data collection
                text_content = content_data.get('text', '')
                
                data_collection_indicators = [
                    'email', 'phone', 'address', 'personal information',
                    'sign up', 'register', 'subscribe'
                ]
                
                for indicator in data_collection_indicators:
                    if indicator.lower() in text_content.lower():
                        violations.append({
                            'type': 'potential_data_collection',
                            'description': f"Content may encourage data collection from children: '{indicator}'",
                            'severity': 'high',
                            'location': 'text_content'
                        })
                
                # Check for inappropriate content for children
                inappropriate_keywords = [
                    'dating', 'romance', 'adult', 'mature', 'violent'
                ]
                
                for keyword in inappropriate_keywords:
                    if keyword.lower() in text_content.lower():
                        violations.append({
                            'type': 'age_inappropriate',
                            'description': f"Content contains age-inappropriate themes: '{keyword}'",
                            'severity': 'medium',
                            'location': 'text_content'
                        })
        
        return violations
    
    async def _check_ftc_compliance(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check FTC Guidelines compliance for advertising disclosure."""        
        violations = []
        text_content = content_data.get('text', '')
        
        # Check for promotional language without disclosure
        promotional_indicators = [
            'review', 'recommend', 'love this product', 'amazing',
            'must have', 'check out', 'link in bio', 'use my code'
        ]
        
        disclosure_indicators = [
            '#ad', '#sponsored', '#partnership', '#affiliate',
            'paid promotion', 'sponsored by', 'in partnership with'
        ]
        
        has_promotional_content = any(
            indicator.lower() in text_content.lower() 
            for indicator in promotional_indicators
        )
        
        has_proper_disclosure = any(
            indicator.lower() in text_content.lower() 
            for indicator in disclosure_indicators
        )
        
        if has_promotional_content and not has_proper_disclosure:
            violations.append({
                'type': 'missing_disclosure',
                'description': "Promotional content lacks proper FTC-compliant disclosure",
                'severity': 'high',
                'location': 'text_content'
            })
        
        return violations
    
    async def _check_gdpr_compliance(
        self, content_data: Dict[str, Any], target_audience: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Check GDPR compliance for EU audience."""        
        violations = []
        
        # Check if content targets EU audience
        if target_audience:
            location_dist = target_audience.get('location_distribution', {})
            eu_percentage = sum(
                percentage for country, percentage in location_dist.items()
                if country in ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'EU']
            )
            
            if eu_percentage > 0.1:  # Significant EU audience
                text_content = content_data.get('text', '')
                
                # Check for data collection without consent notice
                data_collection_terms = [
                    'collect data', 'personal information', 'cookies',
                    'tracking', 'analytics', 'email list'
                ]
                
                consent_terms = [
                    'privacy policy', 'consent', 'opt-in', 'agree to terms'
                ]
                
                has_data_collection = any(
                    term.lower() in text_content.lower() 
                    for term in data_collection_terms
                )
                
                has_consent_notice = any(
                    term.lower() in text_content.lower() 
                    for term in consent_terms
                )
                
                if has_data_collection and not has_consent_notice:
                    violations.append({
                        'type': 'missing_consent_notice',
                        'description': "Data collection without proper GDPR consent notice",
                        'severity': 'high',
                        'location': 'text_content'
                    })
        
        return violations


class BrandSafetyAnalyzer:
    """    Master brand safety analyzer that coordinates all safety and compliance
    analysis for content creators and brand partnerships.
    """    
    def __init__(self):
        """Initialize the brand safety analyzer."""        self.compliance_engine = ContentComplianceEngine()
        
        logger.info("Brand safety analyzer initialized successfully")
    
    async def comprehensive_content_analysis(
        self,
        content_id: str,
        creator_id: str,
        content_data: Dict[str, Any],
        target_brands: List[str] = None,
        compliance_frameworks: List[ComplianceFramework] = None,
        safety_standards: BrandSafetyStandard = BrandSafetyStandard.MODERATE
    ) -> ContentModerationReport:
        """        Perform comprehensive content analysis for brand safety and compliance.
        
        Args:
            content_id: Content identifier
            creator_id: Creator identifier
            content_data: Content to analyze
            target_brands: Brands to check compatibility with
            compliance_frameworks: Compliance frameworks to check
            safety_standards: Safety standards to apply
            
        Returns:
            Comprehensive content moderation report
        """        
        try:
            # Perform safety analysis
            safety_analysis = await self.compliance_engine.analyze_content_safety(
                content_id, content_data, safety_standards
            )
            
            # Check brand compatibility
            brand_compatibility = []
            if target_brands:
                for brand_name in target_brands:
                    # Get brand guidelines (would come from database)
                    brand_guidelines = self.compliance_engine.brand_safety_guidelines.get(
                        'mainstream_brand', {}
                    )
                    
                    compatibility = await self.compliance_engine.check_brand_compatibility(
                        content_id, brand_name, brand_guidelines, safety_analysis
                    )
                    brand_compatibility.append(compatibility)
            
            # Check compliance
            compliance_checks = []
            if compliance_frameworks:
                compliance_checks = await self.compliance_engine.check_compliance(
                    content_data, compliance_frameworks
                )
            
            # Determine moderation actions
            moderation_actions = self._determine_moderation_actions(
                safety_analysis, brand_compatibility, compliance_checks
            )
            
            # Determine if escalation is required
            escalation_required = self._requires_escalation(
                safety_analysis, brand_compatibility, compliance_checks
            )
            
            # Generate final decision
            final_decision = self._generate_final_decision(
                safety_analysis, brand_compatibility, compliance_checks
            )
            
            report = ContentModerationReport(
                report_id=f"report_{content_id}_{int(datetime.now().timestamp())}",
                content_id=content_id,
                creator_id=creator_id,
                content_type=content_data.get('type', 'unknown'),
                safety_analysis=safety_analysis,
                brand_compatibility=brand_compatibility,
                compliance_checks=compliance_checks,
                moderation_actions=moderation_actions,
                escalation_required=escalation_required,
                reviewer_notes=[],
                final_decision=final_decision,
                generated_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"Comprehensive content analysis completed for {content_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to perform comprehensive content analysis: {e}")
            raise
    
    def _determine_moderation_actions(
        self,
        safety_analysis: SafetyAnalysisResult,
        brand_compatibility: List[BrandCompatibilityScore],
        compliance_checks: List[ComplianceCheckResult]
    ) -> List[str]:
        """Determine required moderation actions."""        
        actions = []
        
        # Safety-based actions
        if safety_analysis.overall_risk_level == SafetyRiskLevel.UNSAFE:
            actions.append("Block content from publication")
        elif safety_analysis.overall_risk_level == SafetyRiskLevel.HIGH_RISK:
            actions.append("Require content modifications before approval")
        elif safety_analysis.requires_manual_review:
            actions.append("Flag for manual review")
        
        # Brand compatibility actions
        low_compatibility_brands = [
            brand.brand_name for brand in brand_compatibility
            if brand.compatibility_score < 0.6
        ]
        if low_compatibility_brands:
            actions.append(f"Restrict brand partnerships: {', '.join(low_compatibility_brands)}")
        
        # Compliance actions
        non_compliant_frameworks = [
            check.framework.value for check in compliance_checks
            if check.compliance_status in ['non_compliant', 'partially_compliant']
        ]
        if non_compliant_frameworks:
            actions.append(f"Address compliance violations: {', '.join(non_compliant_frameworks)}")
        
        # If no issues, approve
        if not actions:
            actions.append("Approve content for publication")
        
        return actions
    
    def _requires_escalation(
        self,
        safety_analysis: SafetyAnalysisResult,
        brand_compatibility: List[BrandCompatibilityScore],
        compliance_checks: List[ComplianceCheckResult]
    ) -> bool:
        """Determine if escalation to human reviewer is required."""        
        # High risk content requires escalation
        if safety_analysis.overall_risk_level in [SafetyRiskLevel.HIGH_RISK, SafetyRiskLevel.UNSAFE]:
            return True
        
        # Manual review flag
        if safety_analysis.requires_manual_review:
            return True
        
        # Compliance violations require escalation
        serious_violations = any(
            check.compliance_status == 'non_compliant'
            for check in compliance_checks
        )
        if serious_violations:
            return True
        
        # Very low brand compatibility
        very_low_compatibility = any(
            brand.compatibility_score < 0.3
            for brand in brand_compatibility
        )
        if very_low_compatibility:
            return True
        
        return False
    
    def _generate_final_decision(
        self,
        safety_analysis: SafetyAnalysisResult,
        brand_compatibility: List[BrandCompatibilityScore],
        compliance_checks: List[ComplianceCheckResult]
    ) -> str:
        """Generate final moderation decision."""        
        # Unsafe content is rejected
        if safety_analysis.overall_risk_level == SafetyRiskLevel.UNSAFE:
            return "REJECTED - Unsafe content"
        
        # High risk requires modification
        if safety_analysis.overall_risk_level == SafetyRiskLevel.HIGH_RISK:
            return "CONDITIONAL - Modifications required"
        
        # Non-compliant content is rejected
        if any(check.compliance_status == 'non_compliant' for check in compliance_checks):
            return "REJECTED - Compliance violations"
        
        # Manual review required
        if self._requires_escalation(safety_analysis, brand_compatibility, compliance_checks):
            return "PENDING - Manual review required"
        
        # Medium risk with restrictions
        if safety_analysis.overall_risk_level == SafetyRiskLevel.MEDIUM_RISK:
            return "APPROVED - With brand restrictions"
        
        # Low risk or safe content
        return "APPROVED - Full brand eligibility"
