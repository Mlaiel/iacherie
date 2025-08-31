"""
Anomaly Detection Module - Advanced anomaly detection, fraud detection, and content moderation
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive anomaly detection capabilities for content protection,
fraud detection, and automated content moderation using advanced ML algorithms.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib
import json

# Try to import optional ML libraries
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.svm import OneClassSVM
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    CONTENT_ANOMALY = "content_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly" 
    FRAUD_PATTERN = "fraud_pattern"
    SPAM_CONTENT = "spam_content"
    FAKE_ENGAGEMENT = "fake_engagement"
    SECURITY_THREAT = "security_threat"
    POLICY_VIOLATION = "policy_violation"

class SeverityLevel(Enum):
    """Severity levels for detected anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnomalyAlert:
    """Data structure for anomaly alerts"""
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence_score: float
    timestamp: datetime
    description: str
    metadata: Dict[str, Any]
    recommended_action: str

@dataclass
class DetectionConfig:
    """Configuration for anomaly detection"""
    sensitivity: float = 0.8
    min_confidence: float = 0.7
    lookback_hours: int = 24
    enable_real_time: bool = True
    custom_rules: List[Dict[str, Any]] = None

class BaseDetector(ABC):
    """Base class for all anomaly detectors"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_models()
    
    @abstractmethod
    def _initialize_models(self):
        """Initialize detection models"""
        pass
    
    @abstractmethod
    def detect(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect anomalies in the provided data"""
        pass

class AnomalyDetector(BaseDetector):
    """General purpose anomaly detector"""
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        if config is None:
            config = DetectionConfig()
        super().__init__(config)
        self.logger.info("AnomalyDetector initialized successfully")
    
    def _initialize_models(self):
        """Initialize anomaly detection models"""



        try:
            if SKLEARN_AVAILABLE:
                self.isolation_forest = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                self.one_class_svm = OneClassSVM(
                    kernel='rbf',
                    gamma='scale'
                )
                self.scaler = StandardScaler()
            else:
                self.logger.warning("Scikit-learn not available, using simplified detection")
            
            self.pattern_cache = {}
            self.baseline_metrics = {}
            
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
    
    def detect(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect general anomalies in content and behavior"""
        alerts = []
        
        try:
            # Content-based anomaly detection
            content_alerts = self._detect_content_anomalies(data)
            alerts.extend(content_alerts)
            
            # Behavioral anomaly detection
            behavior_alerts = self._detect_behavioral_anomalies(data)
            alerts.extend(behavior_alerts)
            
            # Statistical anomaly detection
            if SKLEARN_AVAILABLE and 'metrics' in data:
                stat_alerts = self._detect_statistical_anomalies(data['metrics'])
                alerts.extend(stat_alerts)
            
            self.logger.info(f"Detected {len(alerts)} anomalies")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _detect_content_anomalies(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect anomalies in content patterns"""
        alerts = []
        
        content = data.get('content', {})
        if not content:
            return alerts
        
        # Check for unusual content length
        text = content.get('text', '')
        if len(text) > 10000:  # Unusually long content
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.CONTENT_ANOMALY,
                severity=SeverityLevel.MEDIUM,
                confidence_score=0.8,
                timestamp=datetime.utcnow(),
                description="Unusually long content detected",
                metadata={"content_length": len(text)},
                recommended_action="Review content for spam or irrelevant information"
            ))
        
        # Check for repetitive patterns
        if self._detect_repetitive_content(text):
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.SPAM_CONTENT,
                severity=SeverityLevel.HIGH,
                confidence_score=0.9,
                timestamp=datetime.utcnow(),
                description="Repetitive content pattern detected",
                metadata={"pattern_type": "repetitive_text"},
                recommended_action="Flag for manual review or auto-moderate"
            ))
        
        return alerts
    
    def _detect_behavioral_anomalies(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect anomalies in user behavior"""
        alerts = []
        
        behavior = data.get('behavior', {})
        if not behavior:
            return alerts
        
        # Check posting frequency
        posting_rate = behavior.get('posts_per_hour', 0)
        if posting_rate > 10:  # More than 10 posts per hour
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.BEHAVIORAL_ANOMALY,
                severity=SeverityLevel.HIGH,
                confidence_score=0.85,
                timestamp=datetime.utcnow(),
                description="Unusually high posting frequency",
                metadata={"posting_rate": posting_rate},
                recommended_action="Implement rate limiting or investigate bot activity"
            ))
        
        # Check engagement patterns
        engagement_ratio = behavior.get('engagement_ratio', 0)
        if engagement_ratio > 0.5:  # Suspiciously high engagement
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.FAKE_ENGAGEMENT,
                severity=SeverityLevel.MEDIUM,
                confidence_score=0.75,
                timestamp=datetime.utcnow(),
                description="Potentially artificial engagement detected",
                metadata={"engagement_ratio": engagement_ratio},
                recommended_action="Analyze engagement sources for authenticity"
            ))
        
        return alerts
    
    def _detect_statistical_anomalies(self, metrics: Dict[str, float]) -> List[AnomalyAlert]:
        """Detect statistical anomalies using ML models"""
        alerts = []
        
        if not SKLEARN_AVAILABLE:
            return alerts
        
        try:
            # Prepare data for analysis
            values = list(metrics.values())
            if len(values) < 2:
                return alerts
            
            data_array = np.array(values).reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(data_array)
            
            # Use Isolation Forest for anomaly detection
            outliers = self.isolation_forest.fit_predict(scaled_data)
            
            for i, is_outlier in enumerate(outliers):
                if is_outlier == -1:  # Anomaly detected
                    metric_name = list(metrics.keys())[i]
                    metric_value = values[i]
                    
                    alerts.append(AnomalyAlert(
                        anomaly_type=AnomalyType.BEHAVIORAL_ANOMALY,
                        severity=SeverityLevel.MEDIUM,
                        confidence_score=0.8,
                        timestamp=datetime.utcnow(),
                        description=f"Statistical anomaly in metric: {metric_name}",
                        metadata={"metric": metric_name, "value": metric_value},
                        recommended_action="Investigate unusual metric values"
                    ))
            
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {e}")
        
        return alerts
    
    def _detect_repetitive_content(self, text: str) -> bool:
        """Check for repetitive content patterns"""
        if len(text) < 10:
            return False
        
        # Simple repetition check
        words = text.lower().split()
        if len(words) < 5:
            return False
        
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Check if any word appears more than 50% of the time
        total_words = len(words)
        for count in word_counts.values():
            if count / total_words > 0.5:
                return True
        
        return False

class FraudDetector(BaseDetector):
    """Specialized fraud detection system"""
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        if config is None:
            config = DetectionConfig(sensitivity=0.9, min_confidence=0.8)
        super().__init__(config)
        self.known_fraud_patterns = set()
        self.suspicious_ips = set()
        self.logger.info("FraudDetector initialized successfully")
    
    def _initialize_models(self):
        """Initialize fraud detection models"""



        try:
            # Load known fraud patterns
            self.fraud_signatures = {
                'fake_accounts': [
                    'rapid_account_creation',
                    'bulk_similar_profiles',
                    'automated_interactions'
                ],
                'payment_fraud': [
                    'unusual_payment_patterns',
                    'multiple_failed_attempts',
                    'geographical_inconsistencies'
                ],
                'content_fraud': [
                    'plagiarized_content',
                    'fake_reviews',
                    'manipulated_metrics'
                ]
            }
            
            self.risk_thresholds = {
                'account_age': 7,  # days
                'interaction_velocity': 100,  # interactions per hour
                'content_similarity': 0.8  # similarity threshold
            }
            
        except Exception as e:
            self.logger.error(f"Fraud model initialization failed: {e}")
    
    def detect(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect fraud patterns"""
        alerts = []
        
        try:
            # Account fraud detection
            account_alerts = self._detect_account_fraud(data)
            alerts.extend(account_alerts)
            
            # Payment fraud detection
            payment_alerts = self._detect_payment_fraud(data)
            alerts.extend(payment_alerts)
            
            # Content fraud detection
            content_alerts = self._detect_content_fraud(data)
            alerts.extend(content_alerts)
            
            self.logger.info(f"Fraud detector found {len(alerts)} suspicious activities")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Fraud detection failed: {e}")
            return []
    
    def _detect_account_fraud(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect fraudulent account activities"""
        alerts = []
        
        account = data.get('account', {})
        if not account:
            return alerts
        
        # Check account age and activity correlation
        creation_date = account.get('created_at')
        if creation_date:
            account_age = (datetime.utcnow() - creation_date).days
            activity_count = account.get('activity_count', 0)
            
            if account_age < 1 and activity_count > 50:
                alerts.append(AnomalyAlert(
                    anomaly_type=AnomalyType.FRAUD_PATTERN,
                    severity=SeverityLevel.HIGH,
                    confidence_score=0.9,
                    timestamp=datetime.utcnow(),
                    description="Suspicious new account with high activity",
                    metadata={"account_age": account_age, "activity_count": activity_count},
                    recommended_action="Flag account for manual verification"
                ))
        
        # Check for bulk account patterns
        ip_address = account.get('ip_address')
        if ip_address and self._is_suspicious_ip(ip_address):
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.FRAUD_PATTERN,
                severity=SeverityLevel.HIGH,
                confidence_score=0.85,
                timestamp=datetime.utcnow(),
                description="Account created from suspicious IP address",
                metadata={"ip_address": ip_address},
                recommended_action="Block or restrict IP address"
            ))
        
        return alerts
    
    def _detect_payment_fraud(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect payment-related fraud"""
        alerts = []
        
        payment = data.get('payment', {})
        if not payment:
            return alerts
        
        # Check for unusual payment patterns
        amount = payment.get('amount', 0)
        if amount > 10000:  # Large transaction
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.FRAUD_PATTERN,
                severity=SeverityLevel.MEDIUM,
                confidence_score=0.7,
                timestamp=datetime.utcnow(),
                description="Large transaction amount detected",
                metadata={"amount": amount},
                recommended_action="Require additional verification"
            ))
        
        # Check for multiple failed attempts
        failed_attempts = payment.get('failed_attempts', 0)
        if failed_attempts > 3:
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.FRAUD_PATTERN,
                severity=SeverityLevel.HIGH,
                confidence_score=0.8,
                timestamp=datetime.utcnow(),
                description="Multiple failed payment attempts",
                metadata={"failed_attempts": failed_attempts},
                recommended_action="Temporarily block payment method"
            ))
        
        return alerts
    
    def _detect_content_fraud(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect fraudulent content patterns"""
        alerts = []
        
        content = data.get('content', {})
        if not content:
            return alerts
        
        # Check for content manipulation
        engagement_metrics = content.get('engagement', {})
        likes = engagement_metrics.get('likes', 0)
        views = engagement_metrics.get('views', 1)
        
        engagement_rate = likes / max(views, 1)
        if engagement_rate > 0.5:  # Suspiciously high engagement rate
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.FAKE_ENGAGEMENT,
                severity=SeverityLevel.HIGH,
                confidence_score=0.85,
                timestamp=datetime.utcnow(),
                description="Artificially inflated engagement detected",
                metadata={"engagement_rate": engagement_rate},
                recommended_action="Investigate engagement sources"
            ))
        
        return alerts
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if an IP address is suspicious"""
        # Simple check - in production, this would use threat intelligence feeds
        return ip_address in self.suspicious_ips

class ContentModerator(BaseDetector):
    """Automated content moderation system"""
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        if config is None:
            config = DetectionConfig(sensitivity=0.85, min_confidence=0.75)
        super().__init__(config)
        self.logger.info("ContentModerator initialized successfully")
    
    def _initialize_models(self):
        """Initialize content moderation models"""



        try:
            # Define moderation categories and keywords
            self.moderation_rules = {
                'hate_speech': {
                    'keywords': ['hate', 'discrimination', 'offensive'],
                    'severity': SeverityLevel.CRITICAL
                },
                'spam': {
                    'keywords': ['buy now', 'limited offer', 'click here'],
                    'severity': SeverityLevel.MEDIUM
                },
                'adult_content': {
                    'keywords': ['adult', 'explicit'],
                    'severity': SeverityLevel.HIGH
                },
                'violence': {
                    'keywords': ['violence', 'harm', 'threat'],
                    'severity': SeverityLevel.CRITICAL
                }
            }
            
            self.policy_violations = {
                'copyright': 'Content appears to violate copyright',
                'privacy': 'Content contains private information',
                'misinformation': 'Content flagged as potentially misleading'
            }
            
        except Exception as e:
            self.logger.error(f"Content moderation initialization failed: {e}")
    
    def detect(self, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Detect policy violations and inappropriate content"""
        alerts = []
        
        try:
            content = data.get('content', {})
            if not content:
                return alerts
            
            text = content.get('text', '')
            images = content.get('images', [])
            videos = content.get('videos', [])
            
            # Text content moderation
            text_alerts = self._moderate_text_content(text)
            alerts.extend(text_alerts)
            
            # Media content moderation
            media_alerts = self._moderate_media_content(images, videos)
            alerts.extend(media_alerts)
            
            # Policy compliance check
            policy_alerts = self._check_policy_compliance(content)
            alerts.extend(policy_alerts)
            
            self.logger.info(f"Content moderation found {len(alerts)} issues")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Content moderation failed: {e}")
            return []
    
    def _moderate_text_content(self, text: str) -> List[AnomalyAlert]:
        """Moderate text content for policy violations"""
        alerts = []
        
        if not text:
            return alerts
        
        text_lower = text.lower()
        
        # Check against moderation rules
        for category, rules in self.moderation_rules.items():
            keyword_matches = 0
            matched_keywords = []
            
            for keyword in rules['keywords']:
                if keyword in text_lower:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            if keyword_matches > 0:
                confidence = min(0.9, keyword_matches * 0.3)
                alerts.append(AnomalyAlert(
                    anomaly_type=AnomalyType.POLICY_VIOLATION,
                    severity=rules['severity'],
                    confidence_score=confidence,
                    timestamp=datetime.utcnow(),
                    description=f"Content flagged for {category}",
                    metadata={"category": category, "matched_keywords": matched_keywords},
                    recommended_action="Review and potentially remove content"
                ))
        
        return alerts
    
    def _moderate_media_content(self, images: List[str], videos: List[str]) -> List[AnomalyAlert]:
        """Moderate image and video content"""
        alerts = []
        
        # Placeholder for media content analysis
        # In production, this would use computer vision models
        total_media = len(images) + len(videos)
        
        if total_media > 10:
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.SPAM_CONTENT,
                severity=SeverityLevel.MEDIUM,
                confidence_score=0.6,
                timestamp=datetime.utcnow(),
                description="Excessive media content detected",
                metadata={"media_count": total_media},
                recommended_action="Review media content for spam"
            ))
        
        return alerts
    
    def _check_policy_compliance(self, content: Dict[str, Any]) -> List[AnomalyAlert]:
        """Check content for policy compliance"""
        alerts = []
        
        # Check for potential copyright violations
        if self._check_copyright_risk(content):
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.POLICY_VIOLATION,
                severity=SeverityLevel.HIGH,
                confidence_score=0.8,
                timestamp=datetime.utcnow(),
                description="Potential copyright violation detected",
                metadata={"violation_type": "copyright"},
                recommended_action="Conduct copyright review"
            ))
        
        # Check for privacy violations
        if self._check_privacy_risk(content):
            alerts.append(AnomalyAlert(
                anomaly_type=AnomalyType.POLICY_VIOLATION,
                severity=SeverityLevel.HIGH,
                confidence_score=0.75,
                timestamp=datetime.utcnow(),
                description="Potential privacy violation detected",
                metadata={"violation_type": "privacy"},
                recommended_action="Review for private information"
            ))
        
        return alerts
    
    def _check_copyright_risk(self, content: Dict[str, Any]) -> bool:
        """Check for potential copyright violations"""
        # Simplified copyright check
        text = content.get('text', '')
        if 'copyright' in text.lower() or '©' in text:
            return True
        return False
    
    def _check_privacy_risk(self, content: Dict[str, Any]) -> bool:
        """Check for potential privacy violations"""
        # Simplified privacy check
        text = content.get('text', '')
        privacy_indicators = ['phone number', 'email', 'address', 'ssn']
        return any(indicator in text.lower() for indicator in privacy_indicators)

# Export classes for external use
__all__ = [
    'AnomalyType',
    'SeverityLevel', 
    'AnomalyAlert',
    'DetectionConfig',
    'BaseDetector',
    'AnomalyDetector',
    'FraudDetector',
    'ContentModerator'
]

logger.info("Anomaly detection module loaded successfully")
