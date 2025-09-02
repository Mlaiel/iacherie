"""Data Classification and Labeling System

Advanced data classification engine for automatic content categorization,
sensitivity labeling, and compliance tagging across all data types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib

from ...core.base import BaseManager
from ...core.exceptions import ClassificationError, ValidationError
from ...ai.models import ContentClassifier, SentimentAnalyzer, TopicExtractor


class AutomaticClassificationEngine:
    """
    Enhanced automatic classification engine with ML-powered detection
    """
    
    def __init__(self, classifier: 'DataClassifier'):
        self.classifier = classifier
        self.logger = logging.getLogger(__name__)
        
        # Enhanced pattern matchers for automatic detection
        self.sensitivity_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
            "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "api_key": r'\b(?:api[_-]?key|token|secret)[\s:="\']([a-zA-Z0-9_-]{20,})\b'
        }
        
        # Compliance framework detection patterns
        self.compliance_indicators = {
            ComplianceTag.GDPR_APPLICABLE: ["personal", "identifiable", "privacy", "consent"],
            ComplianceTag.CCPA_APPLICABLE: ["california", "consumer", "personal information"],
            ComplianceTag.HIPAA_APPLICABLE: ["health", "medical", "patient", "phi"],
            ComplianceTag.PCI_DSS_APPLICABLE: ["payment", "card", "financial", "transaction"],
            ComplianceTag.SOX_APPLICABLE: ["financial", "audit", "accounting", "compliance"]
        }
    
    async def auto_classify_content(
        self, 
        content: str, 
        content_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
        Automatically classify content using ML and pattern matching
        """
        try:
            # Extract features from content
            features = await self._extract_content_features(content)
            
            # Detect sensitivity level using patterns
            sensitivity = await self._detect_sensitivity_level(content, features)
            
            # Determine compliance requirements
            compliance_tags = await self._determine_compliance_tags(content, features)
            
            # Classify content category
            category = await self._classify_content_category(content, features)
            
            # Calculate confidence score
            confidence = await self._calculate_confidence_score(features, sensitivity, category)
            
            # Determine classification level based on sensitivity and compliance
            classification_level = await self._determine_classification_level(
                sensitivity, compliance_tags
            )
            
            result = ClassificationResult(
                content_id=content_id,
                classification_level=classification_level,
                content_category=category,
                sensitivity_label=sensitivity,
                compliance_tags=compliance_tags,
                confidence_score=confidence,
                matched_patterns=features.get("matched_patterns", []),
                classification_metadata={
                    "auto_classified": True,
                    "features_detected": list(features.keys()),
                    "classification_timestamp": datetime.utcnow().isoformat(),
                    "context": context or {}
                },
                recommended_actions=await self._generate_recommended_actions(
                    classification_level, compliance_tags
                )
            )
            
            self.logger.info(
                f"Auto-classified content {content_id}: "
                f"Level={classification_level.value}, "
                f"Sensitivity={sensitivity.value}, "
                f"Confidence={confidence:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Auto-classification failed for {content_id}: {str(e)}")
            raise ClassificationError(f"Auto-classification failed: {str(e)}")
    
    async def _extract_content_features(self, content: str) -> Dict[str, Any]:
        """Extract features from content for classification"""
        features = {
            "length": len(content),
            "word_count": len(content.split()),
            "matched_patterns": []
        }
        
        # Check for sensitive data patterns
        for pattern_name, pattern in self.sensitivity_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                features[f"{pattern_name}_count"] = len(matches)
                features["matched_patterns"].append(pattern_name)
        
        # Check for compliance indicators
        for tag, indicators in self.compliance_indicators.items():
            indicator_count = sum(
                content.lower().count(indicator.lower()) 
                for indicator in indicators
            )
            if indicator_count > 0:
                features[f"{tag.value}_indicators"] = indicator_count
        
        return features
    
    async def _detect_sensitivity_level(
        self, 
        content: str, 
        features: Dict[str, Any]
    ) -> SensitivityLabel:
        """Detect sensitivity level based on content analysis"""
        
        # High sensitivity indicators
        high_sensitivity_patterns = ["ssn", "credit_card", "api_key"]
        if any(pattern in features["matched_patterns"] for pattern in high_sensitivity_patterns):
            return SensitivityLabel.CRITICAL_SENSITIVITY
        
        # Medium-high sensitivity indicators
        medium_high_patterns = ["email", "phone"]
        if any(pattern in features["matched_patterns"] for pattern in medium_high_patterns):
            return SensitivityLabel.HIGH_SENSITIVITY
        
        # Medium sensitivity indicators
        medium_patterns = ["ip_address"]
        if any(pattern in features["matched_patterns"] for pattern in medium_patterns):
            return SensitivityLabel.MEDIUM_SENSITIVITY
        
        # Check for compliance indicators
        compliance_count = sum(
            1 for key in features.keys() 
            if key.endswith("_indicators") and features[key] > 0
        )
        
        if compliance_count >= 2:
            return SensitivityLabel.HIGH_SENSITIVITY
        elif compliance_count == 1:
            return SensitivityLabel.MEDIUM_SENSITIVITY
        
        return SensitivityLabel.LOW_SENSITIVITY
    
    async def _determine_compliance_tags(
        self, 
        content: str, 
        features: Dict[str, Any]
    ) -> List[ComplianceTag]:
        """Determine applicable compliance tags"""
        tags = []
        
        # GDPR - if personal data is detected
        if any(pattern in features["matched_patterns"] 
               for pattern in ["email", "phone", "ssn"]):
            tags.append(ComplianceTag.GDPR_APPLICABLE)
        
        # PCI DSS - if payment card data is detected
        if "credit_card" in features["matched_patterns"]:
            tags.append(ComplianceTag.PCI_DSS_APPLICABLE)
        
        # Add other compliance tags based on indicators
        for tag, indicators in self.compliance_indicators.items():
            if f"{tag.value}_indicators" in features and features[f"{tag.value}_indicators"] > 0:
                tags.append(tag)
        
        # Always require encryption for sensitive data
        if any(pattern in features["matched_patterns"] 
               for pattern in ["ssn", "credit_card", "api_key"]):
            tags.append(ComplianceTag.ENCRYPTION_REQUIRED)
        
        # Access restriction for high sensitivity
        if len(features["matched_patterns"]) >= 2:
            tags.append(ComplianceTag.ACCESS_RESTRICTED)
        
        return list(set(tags))  # Remove duplicates
    
    async def _classify_content_category(
        self, 
        content: str, 
        features: Dict[str, Any]
    ) -> ContentCategory:
        """Classify content category based on detected patterns"""
        
        # Personal data category
        personal_patterns = ["email", "phone", "ssn"]
        if any(pattern in features["matched_patterns"] for pattern in personal_patterns):
            return ContentCategory.PERSONAL_DATA
        
        # Financial data category
        financial_patterns = ["credit_card"]
        if any(pattern in features["matched_patterns"] for pattern in financial_patterns):
            return ContentCategory.FINANCIAL_DATA
        
        # System data category
        system_patterns = ["ip_address", "api_key"]
        if any(pattern in features["matched_patterns"] for pattern in system_patterns):
            return ContentCategory.SYSTEM_DATA
        
        # Default to operational data
        return ContentCategory.OPERATIONAL_DATA
    
    async def _calculate_confidence_score(
        self, 
        features: Dict[str, Any],
        sensitivity: SensitivityLabel,
        category: ContentCategory
    ) -> float:
        """Calculate confidence score for classification"""
        base_confidence = 0.5
        
        # Increase confidence based on pattern matches
        pattern_confidence = min(len(features["matched_patterns"]) * 0.2, 0.4)
        
        # Increase confidence for high sensitivity data
        sensitivity_confidence = {
            SensitivityLabel.CRITICAL_SENSITIVITY: 0.3,
            SensitivityLabel.HIGH_SENSITIVITY: 0.2,
            SensitivityLabel.MEDIUM_SENSITIVITY: 0.1,
            SensitivityLabel.LOW_SENSITIVITY: 0.05,
            SensitivityLabel.NON_SENSITIVE: 0.0
        }.get(sensitivity, 0.0)
        
        total_confidence = min(base_confidence + pattern_confidence + sensitivity_confidence, 1.0)
        
        return round(total_confidence, 2)
    
    async def _determine_classification_level(
        self, 
        sensitivity: SensitivityLabel,
        compliance_tags: List[ComplianceTag]
    ) -> ClassificationLevel:
        """Determine classification level based on sensitivity and compliance"""
        
        # Critical sensitivity always gets restricted classification
        if sensitivity == SensitivityLabel.CRITICAL_SENSITIVITY:
            return ClassificationLevel.RESTRICTED
        
        # High sensitivity with compliance requirements
        if (sensitivity == SensitivityLabel.HIGH_SENSITIVITY and 
            any(tag in compliance_tags for tag in [
                ComplianceTag.GDPR_APPLICABLE, 
                ComplianceTag.PCI_DSS_APPLICABLE
            ])):
            return ClassificationLevel.CONFIDENTIAL
        
        # Medium sensitivity
        if sensitivity == SensitivityLabel.MEDIUM_SENSITIVITY:
            return ClassificationLevel.INTERNAL
        
        # Low or no sensitivity
        return ClassificationLevel.PUBLIC
    
    async def _generate_recommended_actions(
        self,
        classification_level: ClassificationLevel,
        compliance_tags: List[ComplianceTag]
    ) -> List[str]:
        """Generate recommended actions based on classification"""
        actions = []
        
        if classification_level in [ClassificationLevel.RESTRICTED, ClassificationLevel.CONFIDENTIAL]:
            actions.append("Enable access controls and authentication")
            actions.append("Implement audit logging for access")
        
        if ComplianceTag.ENCRYPTION_REQUIRED in compliance_tags:
            actions.append("Enable encryption at rest and in transit")
        
        if ComplianceTag.GDPR_APPLICABLE in compliance_tags:
            actions.append("Implement GDPR data subject rights")
            actions.append("Set appropriate retention policies")
        
        if ComplianceTag.PCI_DSS_APPLICABLE in compliance_tags:
            actions.append("Implement PCI DSS security controls")
            actions.append("Enable payment data tokenization")
        
        if classification_level == ClassificationLevel.RESTRICTED:
            actions.append("Restrict access to authorized personnel only")
            actions.append("Implement multi-factor authentication")
        
        return actions


class ClassificationLevel(Enum):
    """
Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ContentCategory(Enum):
    """Content category types"""

    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    OPERATIONAL_DATA = "operational_data"
    MARKETING_DATA = "marketing_data"
    CUSTOMER_DATA = "customer_data"
    EMPLOYEE_DATA = "employee_data"
    SYSTEM_DATA = "system_data"
    RESEARCH_DATA = "research_data"


class SensitivityLabel(Enum):
    """Sensitivity labels for content"""

    NON_SENSITIVE = "non_sensitive"
    LOW_SENSITIVITY = "low_sensitivity"
    MEDIUM_SENSITIVITY = "medium_sensitivity"
    HIGH_SENSITIVITY = "high_sensitivity"
    CRITICAL_SENSITIVITY = "critical_sensitivity"


class ComplianceTag(Enum):
    """Compliance requirement tags"""

    GDPR_APPLICABLE = "gdpr_applicable"
    CCPA_APPLICABLE = "ccpa_applicable"
    HIPAA_APPLICABLE = "hipaa_applicable"
    PCI_DSS_APPLICABLE = "pci_dss_applicable"
    SOX_APPLICABLE = "sox_applicable"
    DMCA_APPLICABLE = "dmca_applicable"
    RETENTION_REQUIRED = "retention_required"
    ENCRYPTION_REQUIRED = "encryption_required"
    ACCESS_RESTRICTED = "access_restricted"


@dataclass
class ClassificationRule:
    """Data classification rule definition"""
    rule_id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    classification_level: ClassificationLevel
    content_category: ContentCategory
    sensitivity_label: SensitivityLabel
    compliance_tags: List[ComplianceTag]
    confidence_threshold: float = 0.8
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ClassificationResult:
    """
Result of data classification"""
    content_id: str
    classification_level: ClassificationLevel
    content_category: ContentCategory
    sensitivity_label: SensitivityLabel
    compliance_tags: List[ComplianceTag]
    confidence_score: float
    applied_rules: List[str]
    detected_patterns: List[str]
    ai_predictions: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    classified_at: datetime = field(default_factory=datetime.utcnow)
    classifier_version: str = "1.0"


@dataclass
class ContentFeatures:
    """Extracted content features for classification"""
    content_id: str
    text_features: Dict[str, Any] = field(default_factory=dict)
    metadata_features: Dict[str, Any] = field(default_factory=dict)
    pattern_matches: List[str] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    topics: List[str] = field(default_factory=list)
    language: Optional[str] = None
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.utcnow)


class BaseClassifier(ABC):
    """
Base class for content classifiers"""
    
    @abstractmethod
    async def classify(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
Classify content and return predictions"""
        try:
            self.logger.info(f"Starting classification for content type: {content_type}")
            
            if content_type not in self.get_supported_types():
                raise ValidationError(f"Unsupported content type: {content_type}")
            
            # Extract text for classification
            text_content = self._extract_text_content(content, content_type, metadata)
            
            # Initialize classification results
            results = {
                "content_categories": {},
                "sensitivity_labels": {},
                "confidence_scores": {},
                "metadata": {
                    "classifier_type": "pattern",
                    "content_type": content_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Classify content categories
            for category, patterns in self.content_patterns.items():
                confidence = self._calculate_pattern_confidence(text_content, patterns)
                if confidence > 0.1:  # Minimum confidence threshold
                    results["content_categories"][category.value] = confidence
                    results["confidence_scores"][f"{category.value}_confidence"] = confidence
            
            # Classify sensitivity levels
            for sensitivity, patterns in self.sensitivity_patterns.items():
                confidence = self._calculate_pattern_confidence(text_content, patterns)
                if confidence > 0.1:
                    results["sensitivity_labels"][sensitivity.value] = confidence
                    results["confidence_scores"][f"{sensitivity.value}_confidence"] = confidence
            
            # Add default categories if none found
            if not results["content_categories"]:
                results["content_categories"][ContentCategory.GENERAL.value] = 0.5
                results["confidence_scores"]["general_confidence"] = 0.5
            
            if not results["sensitivity_labels"]:
                results["sensitivity_labels"][SensitivityLabel.LOW_SENSITIVITY.value] = 0.5
                results["confidence_scores"]["low_sensitivity_confidence"] = 0.5
            
            self.logger.info(f"Classification completed with {len(results['content_categories'])} categories")
            return results
            
        except Exception as e:
            self.logger.error(f"Classification failed: {str(e)}")
            raise ClassificationError(f"Classification failed: {str(e)}")
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get supported content types"""
        return [
            "text",
            "document", 
            "json",
            "xml",
            "csv",
            "audio",
            "video", 
            "image",
            "metadata"
        ]
    
    def _extract_text_content(self, content: Any, content_type: str, metadata: Optional[Dict[str, Any]]) -> str:
        """Extract text content for pattern matching"""
        try:
            text_content = ""
            
            if content_type == "text" or isinstance(content, str):
                text_content = str(content)
            elif content_type == "json" and isinstance(content, dict):
                text_content = json.dumps(content, indent=2)
            elif content_type == "metadata" and metadata:
                text_content = json.dumps(metadata, indent=2)
            elif hasattr(content, '__dict__'):
                text_content = str(content.__dict__)
            else:
                text_content = str(content)
            
            # Include metadata in text analysis
            if metadata:
                metadata_text = json.dumps(metadata, indent=2)
                text_content = f"{text_content}\n{metadata_text}"
            
            return text_content[:10000]  # Limit to first 10k characters for performance
            
        except Exception as e:
            self.logger.error(f"Error extracting text content: {str(e)}")
            return str(content)[:1000] if content else ""
    
    def _calculate_pattern_confidence(self, text: str, patterns: List) -> float:
        """Calculate confidence score based on pattern matches"""
        if not text or not patterns:
            return 0.0
        
        total_matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if hasattr(pattern, 'search'):  # regex pattern
                matches = len(pattern.findall(text.lower()))
                if matches > 0:
                    total_matches += min(matches / 10.0, 1.0)  # Normalize multiple matches
            elif isinstance(pattern, str):
                if pattern.lower() in text.lower():
                    total_matches += 1
        
        if total_patterns == 0:
            return 0.0
        
        confidence = total_matches / total_patterns
        return min(confidence, 1.0)  # Cap at 1.0


class PatternClassifier(BaseClassifier):
    """
Pattern-based content classifier"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Define classification patterns
        self.patterns = {
            ContentCategory.PERSONAL_DATA: [
                re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email
                re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),  # Phone
                re.compile(r'\b(?!000)(?!666)(?!9)\d{3}[-.\s]?(?!00)\d{2}[-.\s]?(?!0000)\d{4}\b')  # SSN
            ],
            ContentCategory.FINANCIAL_DATA: [
                re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b'),  # Credit card
                re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b'),  # IBAN
                re.compile(r'\$[0-9,]+\.?[0-9]*|\b[0-9,]+\.?[0-9]*\s*(?:USD|EUR|GBP)\b')  # Currency
            ],
            ContentCategory.HEALTH_DATA: [
                re.compile(r'\b(?:patient|medical|diagnosis|treatment|prescription)\b', re.IGNORECASE),
                re.compile(r'\b(?:ICD-\d+|CPT-\d+)\b'),  # Medical codes
                re.compile(r'\b(?:blood pressure|heart rate|temperature)\b', re.IGNORECASE)
            ],
            ContentCategory.INTELLECTUAL_PROPERTY: [
                re.compile(r'\b(?:patent|trademark|copyright|proprietary|confidential)\b', re.IGNORECASE),
                re.compile(r'\b(?:trade secret|intellectual property)\b', re.IGNORECASE)
            ]
        }
        
        # Sensitivity patterns
        self.sensitivity_patterns = {
            SensitivityLabel.CRITICAL_SENSITIVITY: [
                re.compile(r'\b(?:top secret|classified|restricted)\b', re.IGNORECASE),
                re.compile(r'\b(?:password|private key|secret key)\b', re.IGNORECASE)
            ],
            SensitivityLabel.HIGH_SENSITIVITY: [
                re.compile(r'\b(?:confidential|sensitive|internal only)\b', re.IGNORECASE),
                re.compile(r'\b(?:social security|credit card|bank account)\b', re.IGNORECASE)
            ],
            SensitivityLabel.MEDIUM_SENSITIVITY: [
                re.compile(r'\b(?:internal|limited access)\b', re.IGNORECASE),
                re.compile(r'\b(?:employee|customer|personal)\b', re.IGNORECASE)
            ]
        }
    
    async def classify(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
Classify content using pattern matching"""
        try:
            if content_type != "text":
                return {"error": "Pattern classifier only supports text content"}
            
            content_str = str(content)
            predictions = {
                "content_categories": {},
                "sensitivity_labels": {},
                "pattern_matches": [],
                "confidence_score": 0.0
            }
            
            # Check content category patterns
            for category, patterns in self.patterns.items():
                matches = 0
                matched_patterns = []
                
                for pattern in patterns:
                    pattern_matches = pattern.findall(content_str)
                    if pattern_matches:
                        matches += len(pattern_matches)
                        matched_patterns.extend(pattern_matches)
                
                if matches > 0:
                    confidence = min(matches * 0.2, 1.0)
                    predictions["content_categories"][category.value] = confidence
                    predictions["pattern_matches"].extend(matched_patterns)
            
            # Check sensitivity patterns
            for sensitivity, patterns in self.sensitivity_patterns.items():
                matches = 0
                
                for pattern in patterns:
                    if pattern.search(content_str):
                        matches += 1
                
                if matches > 0:
                    confidence = min(matches * 0.3, 1.0)
                    predictions["sensitivity_labels"][sensitivity.value] = confidence
            
            # Calculate overall confidence
            if predictions["content_categories"] or predictions["sensitivity_labels"]:
                all_scores = (
                    list(predictions["content_categories"].values()) +
                    list(predictions["sensitivity_labels"].values())
                )
                predictions["confidence_score"] = max(all_scores)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in pattern classification: {e}")
            return {"error": f"Pattern classification failed: {e}"}
    
    def get_supported_types(self) -> List[str]:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_supported_types_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_supported_types failed: {e}")
                    return {"status": "error", "message": str(e)}
class AIClassifier(BaseClassifier):
    """AI-powered content classifier"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI models
        self.content_classifier = ContentClassifier(config)
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.topic_extractor = TopicExtractor(config)
    
    async def classify(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
Classify content using AI models"""
        try:
            predictions = {
                "content_categories": {},
                "sensitivity_labels": {},
                "sentiment": {},
                "topics": [],
                "confidence_score": 0.0
            }
            
            # Content classification
            content_results = await self.content_classifier.classify(content, content_type)
            if content_results.get("categories"):
                predictions["content_categories"] = content_results["categories"]
            
            # Sentiment analysis (for text content)
            if content_type == "text":
                sentiment_results = await self.sentiment_analyzer.analyze(content)
                predictions["sentiment"] = sentiment_results
                
                # Topic extraction
                topic_results = await self.topic_extractor.extract_topics(content)
                predictions["topics"] = topic_results.get("topics", [])
            
            # Calculate sensitivity based on content categories
            predictions["sensitivity_labels"] = self._infer_sensitivity_from_categories(
                predictions["content_categories"]
            )
            
            # Calculate overall confidence
            all_scores = []
            if predictions["content_categories"]:
                all_scores.extend(predictions["content_categories"].values())
            if predictions["sensitivity_labels"]:
                all_scores.extend(predictions["sensitivity_labels"].values())
            
            if all_scores:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_supported_types_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_supported_types failed: {e}")
                    return {"status": "error", "message": str(e)}
            if all_scores:
                predictions["confidence_score"] = max(all_scores)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in AI classification: {e}")
            return {"error": f"AI classification failed: {e}"}
    
    def get_supported_types(self) -> List[str]:
        return ["text", "audio", "video", "image"]
    
    def _infer_sensitivity_from_categories(
        self,
        categories: Dict[str, float]
    ) -> Dict[str, float]:
        """Infer sensitivity labels from content categories"""
        sensitivity_mapping = {
            ContentCategory.PERSONAL_DATA.value: SensitivityLabel.HIGH_SENSITIVITY,
            ContentCategory.FINANCIAL_DATA.value: SensitivityLabel.CRITICAL_SENSITIVITY,
            ContentCategory.HEALTH_DATA.value: SensitivityLabel.CRITICAL_SENSITIVITY,
            ContentCategory.INTELLECTUAL_PROPERTY.value: SensitivityLabel.HIGH_SENSITIVITY,
            ContentCategory.EMPLOYEE_DATA.value: SensitivityLabel.MEDIUM_SENSITIVITY,
            ContentCategory.CUSTOMER_DATA.value: SensitivityLabel.MEDIUM_SENSITIVITY,
            ContentCategory.OPERATIONAL_DATA.value: SensitivityLabel.LOW_SENSITIVITY,
            ContentCategory.MARKETING_DATA.value: SensitivityLabel.LOW_SENSITIVITY,
            ContentCategory.SYSTEM_DATA.value: SensitivityLabel.MEDIUM_SENSITIVITY,
            ContentCategory.RESEARCH_DATA.value: SensitivityLabel.MEDIUM_SENSITIVITY
        }
        
        sensitivity_scores = {}
        
        for category, score in categories.items():
            if category in sensitivity_mapping:
                sensitivity = sensitivity_mapping[category].value
                if sensitivity not in sensitivity_scores:
                    sensitivity_scores[sensitivity] = 0.0
                sensitivity_scores[sensitivity] = max(sensitivity_scores[sensitivity], score)
        
        return sensitivity_scores


class ComplianceTaggingEngine:
    """
    Engine for applying compliance tags based on content classification
    
    Automatically applies compliance tags based on detected content
    categories, sensitivity levels, and regulatory requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Compliance mapping rules
        self.compliance_mappings = {
            ContentCategory.PERSONAL_DATA: [
                ComplianceTag.GDPR_APPLICABLE,
                ComplianceTag.CCPA_APPLICABLE,
                ComplianceTag.RETENTION_REQUIRED,
                ComplianceTag.ACCESS_RESTRICTED
            ],
            ContentCategory.FINANCIAL_DATA: [
                ComplianceTag.PCI_DSS_APPLICABLE,
                ComplianceTag.SOX_APPLICABLE,
                ComplianceTag.ENCRYPTION_REQUIRED,
                ComplianceTag.ACCESS_RESTRICTED
            ],
            ContentCategory.HEALTH_DATA: [
                ComplianceTag.HIPAA_APPLICABLE,
                ComplianceTag.ENCRYPTION_REQUIRED,
                ComplianceTag.ACCESS_RESTRICTED,
                ComplianceTag.RETENTION_REQUIRED
            ],
            ContentCategory.INTELLECTUAL_PROPERTY: [
                ComplianceTag.DMCA_APPLICABLE,
                ComplianceTag.ACCESS_RESTRICTED,
                ComplianceTag.RETENTION_REQUIRED
            ]
        }
        
        # Sensitivity-based tags
        self.sensitivity_mappings = {
            SensitivityLabel.CRITICAL_SENSITIVITY: [
                ComplianceTag.ENCRYPTION_REQUIRED,
                ComplianceTag.ACCESS_RESTRICTED
            ],
            SensitivityLabel.HIGH_SENSITIVITY: [
                ComplianceTag.ACCESS_RESTRICTED
            ]
        }
    
    async def apply_compliance_tags(
        self,
        classification_result: ClassificationResult
    ) -> List[ComplianceTag]:
        """
        Apply compliance tags based on classification result
        
        Args:
            classification_result: Classification result
            
        Returns:
            List of applicable compliance tags
        """
        try:
            tags = set()
            
            # Apply category-based tags
            if classification_result.content_category in self.compliance_mappings:
                category_tags = self.compliance_mappings[classification_result.content_category]
                tags.update(category_tags)
            
            # Apply sensitivity-based tags
            if classification_result.sensitivity_label in self.sensitivity_mappings:
                sensitivity_tags = self.sensitivity_mappings[classification_result.sensitivity_label]
                tags.update(sensitivity_tags)
            
            # Additional logic based on detected patterns
            if any("credit card" in pattern.lower() for pattern in classification_result.detected_patterns):
                tags.add(ComplianceTag.PCI_DSS_APPLICABLE)
            
            if any("medical" in pattern.lower() for pattern in classification_result.detected_patterns):
                tags.add(ComplianceTag.HIPAA_APPLICABLE)
            
            return list(tags)
            
        except Exception as e:
            self.logger.error(f"Error applying compliance tags: {e}")
            return []


class ClassificationEngine:
    """
    Main classification engine
    
    Coordinates multiple classifiers and applies business rules
    to produce comprehensive classification results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize classifiers
        self.pattern_classifier = PatternClassifier(config)
        self.ai_classifier = AIClassifier(config)
        self.compliance_tagger = ComplianceTaggingEngine(config)
        
        # Classification rules
        self.rules: Dict[str, ClassificationRule] = {}
        
        # Feature extractors
        self.feature_extractors = {
            "text": self._extract_text_features,
            "audio": self._extract_audio_features,
            "video": self._extract_video_features,
            "image": self._extract_image_features
        }
    
    async def classify_content(
        self,
        content_id: str,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
        Classify content using multiple approaches
        
        Args:
            content_id: Content identifier
            content: Content to classify
            content_type: Type of content
            metadata: Optional metadata
            
        Returns:
            ClassificationResult: Comprehensive classification result
        """
        try:
            # Extract features
            features = await self._extract_features(content_id, content, content_type, metadata)
            
            # Run pattern-based classification
            pattern_results = await self.pattern_classifier.classify(content, content_type, metadata)
            
            # Run AI-based classification
            ai_results = await self.ai_classifier.classify(content, content_type, metadata)
            
            # Apply classification rules
            rule_results = await self._apply_classification_rules(features, pattern_results, ai_results)
            
            # Combine results
            combined_result = await self._combine_classification_results(
                content_id, pattern_results, ai_results, rule_results, features
            )
            
            # Apply compliance tags
            compliance_tags = await self.compliance_tagger.apply_compliance_tags(combined_result)
            combined_result.compliance_tags = compliance_tags
            
            self.logger.info(f"Classified content {content_id}: {combined_result.classification_level.value}")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Error classifying content {content_id}: {e}")
            raise ClassificationError(f"Content classification failed: {e}")
    
    async def add_classification_rule(self, rule: ClassificationRule) -> None:
        """Add a new classification rule"""
        try:
            # Validate rule
            await self._validate_classification_rule(rule)
            
            # Store rule
            self.rules[rule.rule_id] = rule
            
            self.logger.info(f"Added classification rule: {rule.rule_id}")
            
        except Exception as e:
            self.logger.error(f"Error adding classification rule {rule.rule_id}: {e}")
            raise ClassificationError(f"Rule creation failed: {e}")
    
    async def update_classification_rule(
        self,
        rule_id: str,
        updates: Dict[str, Any]
    ) -> ClassificationRule:
        """Update an existing classification rule"""
        try:
            rule = self.rules.get(rule_id)
            if not rule:
                raise ClassificationError(f"Rule {rule_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.utcnow()
            
            # Validate updated rule
            await self._validate_classification_rule(rule)
            
            self.logger.info(f"Updated classification rule: {rule_id}")
            return rule
            
        except Exception as e:
            self.logger.error(f"Error updating classification rule {rule_id}: {e}")
            raise ClassificationError(f"Rule update failed: {e}")
    
    async def _extract_features(
        self,
        content_id: str,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentFeatures:
        """Extract features from content"""
        features = ContentFeatures(content_id=content_id)
        
        # Extract type-specific features
        extractor = self.feature_extractors.get(content_type)
        if extractor:
            type_features = await extractor(content, metadata)
            features.text_features.update(type_features.get("text_features", {}))
            features.metadata_features.update(type_features.get("metadata_features", {}))
            features.pattern_matches.extend(type_features.get("pattern_matches", []))
        
        # Extract metadata features
        if metadata:
            features.metadata_features.update({
                "file_size": metadata.get("file_size"),
                "file_format": metadata.get("file_format"),
                "creation_date": metadata.get("creation_date"),
                "source_system": metadata.get("source_system")
            })
        
        return features
    
    async def _extract_text_features(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features from text content"""
        features = {
            "text_features": {
                "length": len(content),
                "word_count": len(content.split()),
                "has_special_chars": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', content)),
                "has_numbers": bool(re.search(r'\d', content)),
                "has_uppercase": bool(re.search(r'[A-Z]', content)),
                "avg_word_length": sum(len(word) for word in content.split()) / max(len(content.split()), 1)
            },
            "pattern_matches": [],
            "metadata_features": {}
        }
        
        # Extract pattern matches
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b')
        
        if email_pattern.search(content):
            features["pattern_matches"].append("email")
        if phone_pattern.search(content):
            features["pattern_matches"].append("phone")
        
        return features
    
    async def _extract_audio_features(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features from audio content"""
        return {
            "text_features": {},
            "pattern_matches": [],
            "metadata_features": {
                "duration": metadata.get("duration") if metadata else None,
                "sample_rate": metadata.get("sample_rate") if metadata else None,
                "channels": metadata.get("channels") if metadata else None
            }
        }
    
    async def _extract_video_features(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features from video content"""
        return {
            "text_features": {},
            "pattern_matches": [],
            "metadata_features": {
                "duration": metadata.get("duration") if metadata else None,
                "resolution": metadata.get("resolution") if metadata else None,
                "fps": metadata.get("fps") if metadata else None
            }
        }
    
    async def _extract_image_features(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features from image content"""
        return {
            "text_features": {},
            "pattern_matches": [],
            "metadata_features": {
                "width": metadata.get("width") if metadata else None,
                "height": metadata.get("height") if metadata else None,
                "format": metadata.get("format") if metadata else None
            }
        }
    
    async def _apply_classification_rules(
        self,
        features: ContentFeatures,
        pattern_results: Dict[str, Any],
        ai_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply business classification rules"""
        rule_results = {
            "applied_rules": [],
            "classification_level": None,
            "content_category": None,
            "sensitivity_label": None,
            "confidence_score": 0.0
        }
        
        # Sort rules by priority
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if await self._evaluate_rule_conditions(rule, features, pattern_results, ai_results):
                rule_results["applied_rules"].append(rule.rule_id)
                
                # Apply rule classifications with highest priority
                if not rule_results["classification_level"]:
                    rule_results["classification_level"] = rule.classification_level
                if not rule_results["content_category"]:
                    rule_results["content_category"] = rule.content_category
                if not rule_results["sensitivity_label"]:
                    rule_results["sensitivity_label"] = rule.sensitivity_label
                
                # Update confidence based on rule
                rule_results["confidence_score"] = max(
                    rule_results["confidence_score"],
                    0.9  # High confidence for rule-based classification
                )
        
        return rule_results
    
    async def _evaluate_rule_conditions(
        self,
        rule: ClassificationRule,
        features: ContentFeatures,
        pattern_results: Dict[str, Any],
        ai_results: Dict[str, Any]
    ) -> bool:
        """Evaluate if rule conditions are met"""
        for condition in rule.conditions:
            condition_type = condition.get("type")
            
            if condition_type == "pattern_match":
                required_patterns = condition.get("patterns", [])
                if not any(pattern in features.pattern_matches for pattern in required_patterns):
                    return False
            
            elif condition_type == "ai_category":
                required_category = condition.get("category")
                threshold = condition.get("threshold", 0.5)
                ai_categories = ai_results.get("content_categories", {})
                if ai_categories.get(required_category, 0) < threshold:
                    return False
            
            elif condition_type == "metadata":
                metadata_key = condition.get("key")
                expected_value = condition.get("value")
                if features.metadata_features.get(metadata_key) != expected_value:
                    return False
        
        return True
    
    async def _combine_classification_results(
        self,
        content_id: str,
        pattern_results: Dict[str, Any],
        ai_results: Dict[str, Any],
        rule_results: Dict[str, Any],
        features: ContentFeatures
    ) -> ClassificationResult:
        """Combine results from all classification approaches"""
        # Determine final classification with priority: rules > AI > patterns
        classification_level = (
            rule_results.get("classification_level") or
            self._get_highest_confidence_classification_level(ai_results, pattern_results) or
            ClassificationLevel.INTERNAL
        )
        
        content_category = (
            rule_results.get("content_category") or
            self._get_highest_confidence_content_category(ai_results, pattern_results) or
            ContentCategory.OPERATIONAL_DATA
        )
        
        sensitivity_label = (
            rule_results.get("sensitivity_label") or
            self._get_highest_confidence_sensitivity_label(ai_results, pattern_results) or
            SensitivityLabel.LOW_SENSITIVITY
        )
        
        # Calculate combined confidence
        confidence_scores = [
            rule_results.get("confidence_score", 0),
            ai_results.get("confidence_score", 0),
            pattern_results.get("confidence_score", 0)
        ]
        combined_confidence = max([s for s in confidence_scores if s > 0], default=0.5)
        
        # Collect applied rules and detected patterns
        applied_rules = rule_results.get("applied_rules", [])
        detected_patterns = (
            pattern_results.get("pattern_matches", []) +
            features.pattern_matches
        )
        
        return ClassificationResult(
            content_id=content_id,
            classification_level=classification_level,
            content_category=content_category,
            sensitivity_label=sensitivity_label,
            compliance_tags=[],  # Will be populated by compliance tagger
            confidence_score=combined_confidence,
            applied_rules=applied_rules,
            detected_patterns=list(set(detected_patterns)),
            ai_predictions={
                "ai_results": ai_results,
                "pattern_results": pattern_results
            },
            metadata={
                "features": features.__dict__,
                "rule_results": rule_results
            }
        )
    
    def _get_highest_confidence_classification_level(
        self,
        ai_results: Dict[str, Any],
        pattern_results: Dict[str, Any]
    ) -> Optional[ClassificationLevel]:
        """Get classification level with highest confidence"""
        # Simplified logic - real implementation would be more sophisticated
        if pattern_results.get("confidence_score", 0) > 0.7:
            return ClassificationLevel.CONFIDENTIAL
        elif ai_results.get("confidence_score", 0) > 0.8:
            return ClassificationLevel.INTERNAL
        return None
    
    def _get_highest_confidence_content_category(
        self,
        ai_results: Dict[str, Any],
        pattern_results: Dict[str, Any]
    ) -> Optional[ContentCategory]:
        """Get content category with highest confidence"""
        # Combine categories from both sources
        all_categories = {}
        all_categories.update(ai_results.get("content_categories", {}))
        all_categories.update(pattern_results.get("content_categories", {}))
        
        if all_categories:
            best_category = max(all_categories.items(), key=lambda x: x[1])
            try:
                return ContentCategory(best_category[0])
            except ValueError:
                self.logger.warning(f"Invalid content category: {best_category[0]}")
                return ContentCategory.OPERATIONAL_DATA
        
        return None
    
    def _get_highest_confidence_sensitivity_label(
        self,
        ai_results: Dict[str, Any],
        pattern_results: Dict[str, Any]
    ) -> Optional[SensitivityLabel]:
        """Get sensitivity label with highest confidence"""
        # Combine sensitivity labels from both sources
        all_labels = {}
        all_labels.update(ai_results.get("sensitivity_labels", {}))
        all_labels.update(pattern_results.get("sensitivity_labels", {}))
        
        if all_labels:
            best_label = max(all_labels.items(), key=lambda x: x[1])
            try:
                return SensitivityLabel(best_label[0])
            except ValueError:
                self.logger.warning(f"Invalid sensitivity label: {best_label[0]}")
                return SensitivityLabel.LOW_SENSITIVITY
        
        return None
    
    async def _validate_classification_rule(self, rule: ClassificationRule) -> None:
        """Validate classification rule configuration"""
        if not rule.rule_id or not rule.name:
            raise ValidationError("Rule ID and name are required")
        
        if not rule.conditions:
            raise ValidationError("Rule must have at least one condition")
        
        for condition in rule.conditions:
            if "type" not in condition:
                raise ValidationError("Condition must specify a type")


class DataClassificationManager(BaseManager):
    """
    Central data classification management system
    
    Coordinates content classification, manages classification rules,
    and provides comprehensive labeling and tagging services.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the data classification manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize classification engine
        self.classification_engine = ClassificationEngine(config)
        
        # Classification storage
        self.classification_results: Dict[str, ClassificationResult] = {}
        self.classification_history: List[ClassificationResult] = []
        
        # Performance metrics
        self.metrics = {
            "total_classifications": 0,
            "successful_classifications": 0,
            "average_confidence": 0.0,
            "classifications_by_level": {},
            "classifications_by_category": {},
            "compliance_tags_applied": 0
        }
    
    async def initialize(self) -> None:
        """Initialize the data classification manager"""
        try:
            # Create default classification rules
            await self._create_default_classification_rules()
            
            self.logger.info("Data classification manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data classification manager: {e}")
            raise ClassificationError(f"Classification manager initialization failed: {e}")
    
    async def classify_content(
        self,
        content_id: str,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
        Classify content and store results
        
        Args:
            content_id: Content identifier
            content: Content to classify
            content_type: Type of content
            metadata: Optional metadata
            
        Returns:
            ClassificationResult: Classification result
        """
        try:
            # Perform classification
            result = await self.classification_engine.classify_content(
                content_id, content, content_type, metadata
            )
            
            # Store results
            self.classification_results[content_id] = result
            self.classification_history.append(result)
            
            # Update metrics
            self._update_metrics(result)
            
            self.logger.info(f"Classified content {content_id}: {result.classification_level.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying content {content_id}: {e}")
            raise ClassificationError(f"Content classification failed: {e}")
    
    async def get_classification_result(self, content_id: str) -> Optional[ClassificationResult]:
        """Get classification result for content"""
        return self.classification_results.get(content_id)
    
    async def reclassify_content(
        self,
        content_id: str,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
Reclassify existing content"""
        return await self.classify_content(content_id, content, content_type, metadata)
    
    async def add_classification_rule(self, rule: ClassificationRule) -> None:
        """
Add a new classification rule"""
        await self.classification_engine.add_classification_rule(rule)
    
    async def get_classification_statistics(self) -> Dict[str, Any]:
        """
Get classification statistics"""
        total_results = len(self.classification_results)
        
        # Calculate statistics
        if total_results > 0:
            avg_confidence = sum(
                r.confidence_score for r in self.classification_results.values()
            ) / total_results
            
            # Count by classification level
            level_counts = {}
            for result in self.classification_results.values():
                level = result.classification_level.value
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # Count by content category
            category_counts = {}
            for result in self.classification_results.values():
                category = result.content_category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count compliance tags
            tag_counts = {}
            for result in self.classification_results.values():
                for tag in result.compliance_tags:
                    tag_value = tag.value
                    tag_counts[tag_value] = tag_counts.get(tag_value, 0) + 1
        else:
            avg_confidence = 0.0
            level_counts = {}
            category_counts = {}
            tag_counts = {}
        
        return {
            "total_classified_content": total_results,
            "average_confidence_score": avg_confidence,
            "classifications_by_level": level_counts,
            "classifications_by_category": category_counts,
            "compliance_tags_distribution": tag_counts,
            "performance_metrics": self.metrics
        }
    
    async def search_classified_content(
        self,
        classification_level: Optional[ClassificationLevel] = None,
        content_category: Optional[ContentCategory] = None,
        sensitivity_label: Optional[SensitivityLabel] = None,
        compliance_tags: Optional[List[ComplianceTag]] = None,
        min_confidence: float = 0.0
    ) -> List[ClassificationResult]:
        """
        Search classified content by criteria
        
        Args:
            classification_level: Filter by classification level
            content_category: Filter by content category
            sensitivity_label: Filter by sensitivity label
            compliance_tags: Filter by compliance tags
            min_confidence: Minimum confidence score
            
        Returns:
            List of matching classification results
        """
        results = list(self.classification_results.values())
        
        # Apply filters
        if classification_level:
            results = [r for r in results if r.classification_level == classification_level]
        
        if content_category:
            results = [r for r in results if r.content_category == content_category]
        
        if sensitivity_label:
            results = [r for r in results if r.sensitivity_label == sensitivity_label]
        
        if compliance_tags:
            results = [
                r for r in results
                if any(tag in r.compliance_tags for tag in compliance_tags)
            ]
        
        if min_confidence > 0.0:
            results = [r for r in results if r.confidence_score >= min_confidence]
        
        # Sort by confidence score (descending)
        results.sort(key=lambda r: r.confidence_score, reverse=True)
        
        return results
    
    def _update_metrics(self, result: ClassificationResult) -> None:
        """
Update performance metrics"""
        self.metrics["total_classifications"] += 1
        self.metrics["successful_classifications"] += 1
        
        # Update average confidence
        total_confidence = (
            self.metrics["average_confidence"] * (self.metrics["total_classifications"] - 1) +
            result.confidence_score
        )
        self.metrics["average_confidence"] = total_confidence / self.metrics["total_classifications"]
        
        # Update level counts
        level = result.classification_level.value
        if level not in self.metrics["classifications_by_level"]:
            self.metrics["classifications_by_level"][level] = 0
        self.metrics["classifications_by_level"][level] += 1
        
        # Update category counts
        category = result.content_category.value
        if category not in self.metrics["classifications_by_category"]:
            self.metrics["classifications_by_category"][category] = 0
        self.metrics["classifications_by_category"][category] += 1
        
        # Update compliance tag count
        self.metrics["compliance_tags_applied"] += len(result.compliance_tags)
    
    async def _create_default_classification_rules(self) -> None:
        """Create default classification rules"""
        # Personal data rule
        personal_data_rule = ClassificationRule(
            rule_id="personal_data_high_sensitivity",
            name="Personal Data High Sensitivity",
            description="Classify content with personal data as high sensitivity",
            conditions=[
                {
                    "type": "pattern_match",
                    "patterns": ["email", "phone", "ssn"]
                }
            ],
            classification_level=ClassificationLevel.CONFIDENTIAL,
            content_category=ContentCategory.PERSONAL_DATA,
            sensitivity_label=SensitivityLabel.HIGH_SENSITIVITY,
            compliance_tags=[ComplianceTag.GDPR_APPLICABLE, ComplianceTag.ACCESS_RESTRICTED],
            priority=10
        )
        await self.classification_engine.add_classification_rule(personal_data_rule)
        
        # Financial data rule
        financial_data_rule = ClassificationRule(
            rule_id="financial_data_critical",
            name="Financial Data Critical",
            description="Classify financial data as critical sensitivity",
            conditions=[
                {
                    "type": "ai_category",
                    "category": "financial_data",
                    "threshold": 0.7
                }
            ],
            classification_level=ClassificationLevel.RESTRICTED,
            content_category=ContentCategory.FINANCIAL_DATA,
            sensitivity_label=SensitivityLabel.CRITICAL_SENSITIVITY,
            compliance_tags=[ComplianceTag.PCI_DSS_APPLICABLE, ComplianceTag.ENCRYPTION_REQUIRED],
            priority=15
        )
        await self.classification_engine.add_classification_rule(financial_data_rule)
