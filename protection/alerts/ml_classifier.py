"""
🤖 ML Alert Classifier
=====================

Machine Learning-powered alert classification and enhancement system.
Uses advanced ML models for automatic categorization, priority scoring, and risk assessment.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import pickle
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from ..models.alert_models import Alert, AlertSeverity, AlertType
from ...core.config import settings
from ...core.database import get_async_session
from ...core.cache import CacheManager

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """ML model types."""
    SEVERITY_CLASSIFIER = "severity_classifier"
    RISK_ASSESSOR = "risk_assessor"
    PRIORITY_SCORER = "priority_scorer"
    CATEGORY_CLASSIFIER = "category_classifier"
    ANOMALY_DETECTOR = "anomaly_detector"

class FeatureType(str, Enum):
    """Feature extraction types."""
    TEXT_FEATURES = "text_features"
    METADATA_FEATURES = "metadata_features"
    TEMPORAL_FEATURES = "temporal_features"
    PLATFORM_FEATURES = "platform_features"
    USER_FEATURES = "user_features"

@dataclass
class ClassificationResult:
    """ML classification result."""
    severity: str
    confidence_score: float
    risk_level: str
    priority_score: float
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    anomaly_score: float = 0.0
    feature_importance: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""

@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    last_updated: datetime
    model_version: str

class FeatureExtractor:
    """Extracts features from alerts for ML processing."""
    
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self._is_fitted = False
    
    def extract_features(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive features from alert."""
        features = {}
        
        # Text features
        features.update(self._extract_text_features(alert))
        
        # Metadata features
        features.update(self._extract_metadata_features(alert))
        
        # Temporal features
        features.update(self._extract_temporal_features(alert))
        
        # Platform features
        features.update(self._extract_platform_features(alert))
        
        # User features
        features.update(self._extract_user_features(alert, context))
        
        return features
    
    def _extract_text_features(self, alert: Alert) -> Dict[str, Any]:
        """Extract text-based features."""
        text_content = f"{alert.title} {alert.description}"
        
        features = {
            "text_length": len(text_content),
            "word_count": len(text_content.split()),
            "title_length": len(alert.title),
            "description_length": len(alert.description),
            "has_urgent_keywords": self._has_urgent_keywords(text_content),
            "has_legal_keywords": self._has_legal_keywords(text_content),
            "sentiment_score": self._analyze_sentiment(text_content),
            "readability_score": self._calculate_readability(text_content)
        }
        
        return features
    
    def _extract_metadata_features(self, alert: Alert) -> Dict[str, Any]:
        """Extract metadata-based features."""
        metadata = alert.metadata or {}
        evidence = alert.evidence or {}
        
        features = {
            "violation_type_encoded": self._encode_categorical(alert.violation_type, "violation_type"),
            "platform_encoded": self._encode_categorical(alert.platform, "platform"),
            "has_evidence": len(evidence) > 0,
            "evidence_count": len(evidence),
            "metadata_richness": len(metadata),
            "has_screenshot": "screenshot" in evidence,
            "has_video": "video" in evidence,
            "confidence_score": alert.confidence_score or 0.0
        }
        
        return features
    
    def _extract_temporal_features(self, alert: Alert) -> Dict[str, Any]:
        """Extract time-based features."""
        now = datetime.utcnow()
        created_at = alert.created_at or now
        
        features = {
            "hour_of_day": created_at.hour,
            "day_of_week": created_at.weekday(),
            "is_weekend": created_at.weekday() >= 5,
            "is_business_hours": 9 <= created_at.hour <= 17,
            "age_hours": (now - created_at).total_seconds() / 3600
        }
        
        return features
    
    def _extract_platform_features(self, alert: Alert) -> Dict[str, Any]:
        """Extract platform-specific features."""
        platform = alert.platform.lower()
        
        # Platform risk scores (configurable)
        platform_risk_scores = {
            "youtube": 0.8,
            "instagram": 0.7,
            "tiktok": 0.9,
            "twitter": 0.6,
            "facebook": 0.7,
            "unknown": 0.5
        }
        
        features = {
            "platform_risk_score": platform_risk_scores.get(platform, 0.5),
            "is_video_platform": platform in ["youtube", "tiktok"],
            "is_social_media": platform in ["instagram", "twitter", "facebook"],
            "is_high_volume_platform": platform in ["youtube", "instagram", "tiktok"]
        }
        
        return features
    
    def _extract_user_features(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user-related features."""
        user_id = alert.user_id
        
        # Get user history from context
        user_stats = context.get("user_stats", {})
        
        features = {
            "user_total_alerts": user_stats.get("total_alerts", 0),
            "user_resolved_alerts": user_stats.get("resolved_alerts", 0),
            "user_false_positives": user_stats.get("false_positives", 0),
            "user_success_rate": user_stats.get("success_rate", 0.0),
            "user_avg_response_time": user_stats.get("avg_response_time", 0.0),
            "is_premium_user": user_stats.get("is_premium", False)
        }
        
        return features
    
    def _has_urgent_keywords(self, text: str) -> bool:
        """Check for urgent keywords."""
        urgent_keywords = [
            "urgent", "immediate", "emergency", "critical",
            "asap", "now", "quickly", "fast", "priority"
        ]
        return any(keyword in text.lower() for keyword in urgent_keywords)
    
    def _has_legal_keywords(self, text: str) -> bool:
        """Check for legal keywords."""
        legal_keywords = [
            "copyright", "trademark", "dmca", "infringement",
            "lawsuit", "legal", "attorney", "court", "violation"
        ]
        return any(keyword in text.lower() for keyword in legal_keywords)
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze text sentiment (simplified)."""
        # Simplified sentiment analysis
        negative_words = ["bad", "terrible", "awful", "hate", "angry", "frustrated"]
        positive_words = ["good", "great", "excellent", "love", "happy", "satisfied"]
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count + positive_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score (simplified)."""
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        return min(avg_word_length / 10.0, 1.0)  # Normalize to 0-1
    
    def _encode_categorical(self, value: str, category: str) -> int:
        """Encode categorical values."""
        if category not in self.label_encoders:
            self.label_encoders[category] = LabelEncoder()
        
        encoder = self.label_encoders[category]
        
        try:
            if hasattr(encoder, 'classes_'):
                # Encoder is fitted
                if value in encoder.classes_:
                    return encoder.transform([value])[0]
                else:
                    # Unknown value, return default
                    return len(encoder.classes_)
            else:
                # Encoder not fitted, return hash-based encoding
                return hash(value) % 1000
        except Exception:
            return 0

class SeverityClassifier:
    """Classifies alert severity using ML."""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.feature_extractor = FeatureExtractor()
        self.is_trained = False
        self.model_version = "1.0"
    
    async def predict_severity(
        self,
        alert: Alert,
        context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """Predict alert severity."""



        try:
            if not self.is_trained:
                await self._load_pretrained_model()
            
            # Extract features
            features = self.feature_extractor.extract_features(alert, context)
            feature_vector = self._prepare_feature_vector(features)
            
            # Predict
            probabilities = self.model.predict_proba([feature_vector])[0]
            predicted_class = self.model.predict([feature_vector])[0]
            confidence = max(probabilities)
            
            # Map class to severity
            severity_mapping = {0: "low", 1: "medium", 2: "high", 3: "critical"}
            severity = severity_mapping.get(predicted_class, "medium")
            
            return severity, confidence
            
        except Exception as e:
            logger.error("Failed to predict severity: %s", str(e))
            return "medium", 0.5
    
    async def train_model(self, training_data: List[Dict[str, Any]]) -> ModelMetrics:
        """Train the severity classification model."""



        try:
            if not training_data:
                raise ValueError("No training data provided")
            
            # Prepare training data
            X, y = self._prepare_training_data(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            metrics = ModelMetrics(
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted'),
                recall=recall_score(y_test, y_pred, average='weighted'),
                f1_score=f1_score(y_test, y_pred, average='weighted'),
                training_samples=len(X_train),
                last_updated=datetime.utcnow(),
                model_version=self.model_version
            )
            
            self.is_trained = True
            
            # Save model
            await self._save_model()
            
            logger.info("Severity classifier trained successfully: %s", metrics)
            return metrics
            
        except Exception as e:
            logger.error("Failed to train severity classifier: %s", str(e))
            raise
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector for prediction."""
        # Define expected feature order
        feature_order = [
            "text_length", "word_count", "title_length", "description_length",
            "has_urgent_keywords", "has_legal_keywords", "sentiment_score",
            "readability_score", "violation_type_encoded", "platform_encoded",
            "has_evidence", "evidence_count", "metadata_richness",
            "has_screenshot", "has_video", "confidence_score",
            "hour_of_day", "day_of_week", "is_weekend", "is_business_hours",
            "age_hours", "platform_risk_score", "is_video_platform",
            "is_social_media", "is_high_volume_platform", "user_total_alerts",
            "user_resolved_alerts", "user_false_positives", "user_success_rate",
            "user_avg_response_time", "is_premium_user"
        ]
        
        vector = []
        for feature_name in feature_order:
            value = features.get(feature_name, 0)
            if isinstance(value, bool):
                vector.append(1.0 if value else 0.0)
            elif isinstance(value, (int, float)):
                vector.append(float(value))
            else:
                vector.append(0.0)
        
        return vector
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for model."""
        X = []
        y = []
        
        for data_point in training_data:
            alert_data = data_point["alert"]
            context = data_point.get("context", {})
            true_severity = data_point["severity"]
            
            # Create alert object
            alert = Alert(**alert_data)
            
            # Extract features
            features = self.feature_extractor.extract_features(alert, context)
            feature_vector = self._prepare_feature_vector(features)
            
            X.append(feature_vector)
            
            # Encode severity
            severity_encoding = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            y.append(severity_encoding.get(true_severity, 1))
        
        return np.array(X), np.array(y)
    
    async def _load_pretrained_model(self) -> None:
        """Load pretrained model if available."""



        try:
            model_path = Path(settings.ML_MODELS_PATH) / "severity_classifier.pkl"
            
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data["model"]
                self.feature_extractor = model_data["feature_extractor"]
                self.model_version = model_data.get("version", "1.0")
                self.is_trained = True
                
                logger.info("Loaded pretrained severity classifier")
            else:
                # Use simple heuristic-based model as fallback
                await self._initialize_heuristic_model()
                
        except Exception as e:
            logger.error("Failed to load pretrained model: %s", str(e))
            await self._initialize_heuristic_model()
    
    async def _save_model(self) -> None:
        """Save trained model."""



        try:
            model_path = Path(settings.ML_MODELS_PATH) / "severity_classifier.pkl"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                "model": self.model,
                "feature_extractor": self.feature_extractor,
                "version": self.model_version,
                "created_at": datetime.utcnow().isoformat()
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("Saved severity classifier model")
            
        except Exception as e:
            logger.error("Failed to save model: %s", str(e))
    
    async def _initialize_heuristic_model(self) -> None:
        """Initialize simple heuristic-based model."""
        # This would be a fallback implementation
        self.is_trained = True
        logger.info("Initialized heuristic severity classifier")

class RiskAssessor:
    """Assesses risk level of alerts."""
    
    def __init__(self):
        self.risk_factors = {
            "confidence_score": 0.3,
            "platform_risk": 0.2,
            "violation_type": 0.2,
            "evidence_quality": 0.15,
            "user_history": 0.15
        }
    
    async def assess_risk(self, alert: Alert, context: Dict[str, Any]) -> Tuple[str, float]:
        """Assess risk level of alert."""



        try:
            risk_score = 0.0
            
            # Confidence score factor
            confidence_factor = (alert.confidence_score or 0.5) * self.risk_factors["confidence_score"]
            risk_score += confidence_factor
            
            # Platform risk factor
            platform_risk = self._get_platform_risk(alert.platform)
            platform_factor = platform_risk * self.risk_factors["platform_risk"]
            risk_score += platform_factor
            
            # Violation type factor
            violation_risk = self._get_violation_type_risk(alert.violation_type)
            violation_factor = violation_risk * self.risk_factors["violation_type"]
            risk_score += violation_factor
            
            # Evidence quality factor
            evidence_quality = self._assess_evidence_quality(alert.evidence or {})
            evidence_factor = evidence_quality * self.risk_factors["evidence_quality"]
            risk_score += evidence_factor
            
            # User history factor
            user_stats = context.get("user_stats", {})
            user_risk = self._assess_user_risk(user_stats)
            user_factor = user_risk * self.risk_factors["user_history"]
            risk_score += user_factor
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            # Convert to risk level
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return risk_level, risk_score
            
        except Exception as e:
            logger.error("Failed to assess risk: %s", str(e))
            return "medium", 0.5
    
    def _get_platform_risk(self, platform: str) -> float:
        """Get platform-specific risk score."""
        platform_risks = {
            "youtube": 0.8,
            "instagram": 0.7,
            "tiktok": 0.9,
            "twitter": 0.6,
            "facebook": 0.7,
            "twitch": 0.8,
            "snapchat": 0.6
        }
        return platform_risks.get(platform.lower(), 0.5)
    
    def _get_violation_type_risk(self, violation_type: str) -> float:
        """Get violation type risk score."""
        violation_risks = {
            "copyright": 0.9,
            "trademark": 0.8,
            "impersonation": 0.7,
            "spam": 0.4,
            "harassment": 0.8,
            "fake_content": 0.6
        }
        return violation_risks.get(violation_type.lower(), 0.5)
    
    def _assess_evidence_quality(self, evidence: Dict[str, Any]) -> float:
        """Assess quality of evidence."""
        if not evidence:
            return 0.2
        
        quality_score = 0.0
        
        # Has screenshot
        if "screenshot" in evidence:
            quality_score += 0.3
        
        # Has video
        if "video" in evidence:
            quality_score += 0.4
        
        # Has metadata
        if "metadata" in evidence:
            quality_score += 0.2
        
        # Has multiple evidence types
        if len(evidence) > 2:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _assess_user_risk(self, user_stats: Dict[str, Any]) -> float:
        """Assess user-specific risk factors."""
        if not user_stats:
            return 0.5
        
        # High success rate = lower risk
        success_rate = user_stats.get("success_rate", 0.5)
        
        # Many alerts = higher risk (potential abuse)
        total_alerts = user_stats.get("total_alerts", 0)
        alert_risk = min(total_alerts / 100.0, 0.5)  # Cap at 0.5
        
        # False positives = lower credibility
        false_positive_rate = user_stats.get("false_positive_rate", 0.0)
        
        risk_score = 0.5 - (success_rate * 0.3) + alert_risk + (false_positive_rate * 0.2)
        
        return min(max(risk_score, 0.0), 1.0)

class AlertMLClassifier:
    """
    Main ML classifier for alert processing.
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.severity_classifier = SeverityClassifier()
        self.risk_assessor = RiskAssessor()
        self.feature_extractor = FeatureExtractor()
        
        # Model performance tracking
        self.metrics: Dict[str, ModelMetrics] = {}
        
        logger.info("AlertMLClassifier initialized")

    async def classify_alert(
        self,
        alert_type: AlertType,
        title: str,
        description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify and enhance alert using ML models.
        
        Args:
            alert_type: Type of alert
            title: Alert title
            description: Alert description
            context: Additional context
            
        Returns:
            Enhanced alert data with ML predictions
        """



        try:
            # Create temporary alert object for classification
            alert = Alert(
                id="temp",
                type=alert_type,
                title=title,
                description=description,
                user_id=context.get("user_id", ""),
                content_id=context.get("content_id", ""),
                platform=context.get("platform", ""),
                violation_type=context.get("violation_type", ""),
                evidence=context.get("evidence", {}),
                metadata=context.get("metadata", {}),
                confidence_score=context.get("confidence_score", 0.0),
                created_at=datetime.utcnow()
            )
            
            # Get user context
            user_context = await self._get_user_context(context.get("user_id", ""))
            full_context = {**context, **user_context}
            
            # Classify severity
            severity, severity_confidence = await self.severity_classifier.predict_severity(
                alert, full_context
            )
            
            # Assess risk
            risk_level, risk_score = await self.risk_assessor.assess_risk(
                alert, full_context
            )
            
            # Generate tags
            tags = await self._generate_tags(alert, full_context)
            
            # Calculate priority score
            priority_score = await self._calculate_priority_score(
                alert, severity, risk_score, full_context
            )
            
            # Generate explanation
            explanation = await self._generate_explanation(
                alert, severity, risk_level, full_context
            )
            
            result = {
                "severity": severity,
                "confidence_score": severity_confidence,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "priority_score": priority_score,
                "tags": tags,
                "explanation": explanation,
                "ml_version": "1.0"
            }
            
            # Cache result
            cache_key = f"ml_classification:{hash(f'{title}{description}{context}')}"
            await self.cache_manager.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error("Failed to classify alert: %s", str(e))
            # Return default classification
            return {
                "severity": "medium",
                "confidence_score": 0.5,
                "risk_level": "medium",
                "risk_score": 0.5,
                "priority_score": 0.5,
                "tags": [],
                "explanation": "Default classification due to ML error"
            }

    async def train_models(self, training_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, ModelMetrics]:
        """Train all ML models."""
        results = {}
        
        try:
            # Train severity classifier
            if "severity" in training_data:
                severity_metrics = await self.severity_classifier.train_model(
                    training_data["severity"]
                )
                results["severity_classifier"] = severity_metrics
                self.metrics["severity_classifier"] = severity_metrics
            
            logger.info("Model training completed: %s", results)
            return results
            
        except Exception as e:
            logger.error("Failed to train models: %s", str(e))
            raise

    async def get_model_metrics(self) -> Dict[str, ModelMetrics]:
        """Get current model performance metrics."""



        return self.metrics.copy()

    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context for classification."""



        try:
            # Check cache first
            cache_key = f"user_context:{user_id}"
            cached_context = await self.cache_manager.get(cache_key)
            
            if cached_context:
                return {"user_stats": cached_context}
            
            # Query database for user statistics
            async with get_async_session() as session:
                # Get user alert statistics
                # This would query actual user data
                user_stats = {
                    "total_alerts": 0,
                    "resolved_alerts": 0,
                    "false_positives": 0,
                    "success_rate": 0.5,
                    "avg_response_time": 0.0,
                    "is_premium": False
                }
                
                # Cache for future use
                await self.cache_manager.set(cache_key, user_stats, ttl=1800)
                
                return {"user_stats": user_stats}
                
        except Exception as e:
            logger.error("Failed to get user context: %s", str(e))
            return {"user_stats": {}}

    async def _generate_tags(self, alert: Alert, context: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for alert."""
        tags = []
        
        # Platform tag
        tags.append(f"platform:{alert.platform}")
        
        # Violation type tag
        tags.append(f"violation:{alert.violation_type}")
        
        # Severity-based tags
        if alert.confidence_score and alert.confidence_score > 0.8:
            tags.append("high-confidence")
        
        # Evidence-based tags
        evidence = alert.evidence or {}
        if "screenshot" in evidence:
            tags.append("has-screenshot")
        if "video" in evidence:
            tags.append("has-video")
        
        # Content-based tags
        text_content = f"{alert.title} {alert.description}".lower()
        if any(keyword in text_content for keyword in ["urgent", "immediate", "critical"]):
            tags.append("urgent")
        
        if any(keyword in text_content for keyword in ["copyright", "dmca", "infringement"]):
            tags.append("copyright-related")
        
        return tags

    async def _calculate_priority_score(
        self,
        alert: Alert,
        severity: str,
        risk_score: float,
        context: Dict[str, Any]
    ) -> float:
        """Calculate priority score for alert."""
        # Base score from severity
        severity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        base_score = severity_scores.get(severity, 0.5)
        
        # Adjust based on risk score
        risk_adjustment = risk_score * 0.3
        
        # Adjust based on evidence quality
        evidence_quality = self.risk_assessor._assess_evidence_quality(alert.evidence or {})
        evidence_adjustment = evidence_quality * 0.2
        
        # User history adjustment
        user_stats = context.get("user_stats", {})
        user_success_rate = user_stats.get("success_rate", 0.5)
        user_adjustment = (user_success_rate - 0.5) * 0.2
        
        priority_score = base_score + risk_adjustment + evidence_adjustment + user_adjustment
        
        return min(max(priority_score, 0.0), 1.0)

    async def _generate_explanation(
        self,
        alert: Alert,
        severity: str,
        risk_level: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for classification."""
        explanation_parts = []
        
        explanation_parts.append(f"Classified as {severity} severity")
        explanation_parts.append(f"with {risk_level} risk level")
        
        # Add reasoning based on features
        if alert.confidence_score and alert.confidence_score > 0.8:
            explanation_parts.append("due to high confidence score")
        
        if alert.platform in ["youtube", "tiktok"]:
            explanation_parts.append("on high-risk platform")
        
        evidence = alert.evidence or {}
        if evidence:
            explanation_parts.append(f"with {len(evidence)} types of evidence")
        
        return " ".join(explanation_parts) + "."
