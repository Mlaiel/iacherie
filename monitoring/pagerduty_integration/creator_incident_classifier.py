"""
Creator Incident Classifier for IA Chérie Platform
ML-powered incident categorization for Creator Economy workflow

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import re
import hashlib

try:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.multioutput import MultiOutputClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = pd = None

from .pagerduty_client import IncidentSeverity, IncidentStatus

logger = logging.getLogger(__name__)


class CreatorWorkflowStage(Enum):
    """Creator Economy workflow stages"""
    CONTENT_UPLOAD = "content_upload"
    AI_PROCESSING = "ai_processing"
    IP_PROTECTION = "ip_protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    GAMIFICATION = "gamification"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION = "distribution"
    ANALYTICS = "analytics"
    UNKNOWN = "unknown"


class IncidentCategory(Enum):
    """Creator-specific incident categories"""
    CONTENT_FAILURE = "content_failure"
    AI_MODEL_ERROR = "ai_model_error"
    PROTECTION_VIOLATION = "protection_violation"
    REVENUE_IMPACT = "revenue_impact"
    COLLABORATION_DISRUPTION = "collaboration_disruption"
    ENGAGEMENT_DROP = "engagement_drop"
    SEO_DEGRADATION = "seo_degradation"
    DISTRIBUTION_FAILURE = "distribution_failure"
    SECURITY_BREACH = "security_breach"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INTEGRATION_FAILURE = "integration_failure"
    COMPLIANCE_VIOLATION = "compliance_violation"


class BusinessImpactLevel(Enum):
    """Business impact assessment levels"""
    CRITICAL = "critical"      # >1000 creators affected, >$10K/hour
    HIGH = "high"              # >100 creators affected, >$1K/hour
    MEDIUM = "medium"          # >10 creators affected, >$100/hour
    LOW = "low"                # <10 creators affected, <$100/hour


class TeamAssignment(Enum):
    """Specialized team assignments"""
    DEVOPS_ONCALL = "devops_oncall"
    AI_ML_TEAM = "ai_ml_team"
    SECURITY_TEAM = "security_team"
    CONTENT_PROTECTION = "content_protection"
    BUSINESS_OPERATIONS = "business_operations"
    CREATOR_SUCCESS = "creator_success"
    LEGAL_COMPLIANCE = "legal_compliance"
    PLATFORM_ENGINEERING = "platform_engineering"


@dataclass
class IncidentFeatures:
    """Incident feature extraction for ML classification"""
    incident_id: str
    title: str
    description: str
    source_system: str
    service_name: str
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    labels: Optional[Dict[str, str]] = None
    timestamp: Optional[datetime] = None
    affected_creators: Optional[int] = None
    revenue_impact_hourly: Optional[float] = None
    
    def to_feature_vector(self) -> Dict[str, Any]:
        """Convert incident to feature vector for ML"""
        features = {
            'title_length': len(self.title) if self.title else 0,
            'description_length': len(self.description) if self.description else 0,
            'has_error_message': bool(self.error_message),
            'affected_creators': self.affected_creators or 0,
            'revenue_impact': self.revenue_impact_hourly or 0.0,
            'source_system': self.source_system or 'unknown',
            'service_name': self.service_name or 'unknown',
            'hour_of_day': self.timestamp.hour if self.timestamp else 0,
            'day_of_week': self.timestamp.weekday() if self.timestamp else 0
        }
        
        # Add text features
        text_content = f"{self.title} {self.description} {self.error_message or ''}"
        features['text_content'] = text_content.lower()
        
        # Add metrics features
        if self.metrics:
            for key, value in self.metrics.items():
                features[f'metric_{key}'] = float(value) if isinstance(value, (int, float)) else 0.0
        
        # Add label features
        if self.labels:
            for key, value in self.labels.items():
                features[f'label_{key}'] = str(value)
        
        return features


@dataclass
class ClassificationResult:
    """ML classification result"""
    incident_id: str
    workflow_stage: CreatorWorkflowStage
    incident_category: IncidentCategory
    business_impact: BusinessImpactLevel
    team_assignment: TeamAssignment
    confidence_scores: Dict[str, float]
    severity_recommendation: IncidentSeverity
    auto_escalate: bool
    reasoning: str
    classification_timestamp: datetime


class CreatorIncidentClassifier:
    """
    ML-powered incident classification for Creator Economy
    Intelligently categorizes incidents and recommends actions
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the classifier"""
        self.model_path = model_path
        self.workflow_classifier = None
        self.category_classifier = None
        self.impact_classifier = None
        self.team_classifier = None
        self.text_vectorizer = None
        self.label_encoders = {}
        self.is_trained = False
        
        # Pattern matching rules for quick classification
        self.workflow_patterns = self._initialize_workflow_patterns()
        self.category_patterns = self._initialize_category_patterns()
        self.business_rules = self._initialize_business_rules()
        
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available. Using rule-based classification only.")
    
    def _initialize_workflow_patterns(self) -> Dict[str, List[str]]:
        """Initialize workflow stage detection patterns"""
        return {
            CreatorWorkflowStage.CONTENT_UPLOAD.value: [
                'upload', 'file', 'media', 'video', 'audio', 'image', 'content creation',
                'storage', 's3', 'blob', 'multipart', 'codec', 'format', 'transcoding'
            ],
            CreatorWorkflowStage.AI_PROCESSING.value: [
                'ai', 'ml', 'model', 'inference', 'tensorflow', 'pytorch', 'gpu',
                'processing', 'algorithm', 'neural', 'classification', 'generation'
            ],
            CreatorWorkflowStage.IP_PROTECTION.value: [
                'copyright', 'dmca', 'protection', 'piracy', 'violation', 'takedown',
                'intellectual property', 'plagiarism', 'unauthorized', 'theft'
            ],
            CreatorWorkflowStage.MONETIZATION.value: [
                'payment', 'revenue', 'stripe', 'paypal', 'billing', 'subscription',
                'monetization', 'earnings', 'payout', 'commission', 'transaction'
            ],
            CreatorWorkflowStage.COLLABORATION.value: [
                'collaboration', 'partnership', 'brand', 'sponsor', 'campaign',
                'matching', 'network', 'team', 'shared', 'workflow'
            ],
            CreatorWorkflowStage.GAMIFICATION.value: [
                'gamification', 'achievement', 'badge', 'leaderboard', 'points',
                'level', 'reward', 'engagement', 'competition', 'social'
            ],
            CreatorWorkflowStage.SEO_OPTIMIZATION.value: [
                'seo', 'search', 'ranking', 'optimization', 'indexing', 'crawl',
                'sitemap', 'meta', 'keywords', 'discovery', 'visibility'
            ],
            CreatorWorkflowStage.DISTRIBUTION.value: [
                'distribution', 'publish', 'platform', 'api', 'integration',
                'youtube', 'tiktok', 'instagram', 'twitter', 'social media'
            ]
        }
    
    def _initialize_category_patterns(self) -> Dict[str, List[str]]:
        """Initialize incident category detection patterns"""
        return {
            IncidentCategory.CONTENT_FAILURE.value: [
                'upload failed', 'content error', 'file corrupt', 'media processing'
            ],
            IncidentCategory.AI_MODEL_ERROR.value: [
                'model error', 'inference failed', 'ai processing', 'gpu error'
            ],
            IncidentCategory.PROTECTION_VIOLATION.value: [
                'copyright violation', 'dmca', 'unauthorized use', 'ip theft'
            ],
            IncidentCategory.REVENUE_IMPACT.value: [
                'payment failed', 'revenue loss', 'billing error', 'transaction'
            ],
            IncidentCategory.COLLABORATION_DISRUPTION.value: [
                'partnership failed', 'collaboration error', 'brand disconnect'
            ],
            IncidentCategory.ENGAGEMENT_DROP.value: [
                'engagement down', 'user activity', 'social metrics', 'interaction'
            ],
            IncidentCategory.SEO_DEGRADATION.value: [
                'seo drop', 'ranking down', 'search visibility', 'indexing'
            ],
            IncidentCategory.DISTRIBUTION_FAILURE.value: [
                'publish failed', 'platform error', 'distribution', 'api error'
            ],
            IncidentCategory.SECURITY_BREACH.value: [
                'security', 'breach', 'unauthorized access', 'hack', 'vulnerability'
            ],
            IncidentCategory.PERFORMANCE_DEGRADATION.value: [
                'slow', 'latency', 'timeout', 'performance', 'response time'
            ]
        }
    
    def _initialize_business_rules(self) -> Dict[str, Any]:
        """Initialize business impact assessment rules"""
        return {
            'critical_services': [
                'payment', 'authentication', 'content-upload', 'ai-processing'
            ],
            'critical_keywords': [
                'payment failed', 'auth down', 'database error', 'ai model crash'
            ],
            'impact_thresholds': {
                'creators_affected': {
                    BusinessImpactLevel.CRITICAL: 1000,
                    BusinessImpactLevel.HIGH: 100,
                    BusinessImpactLevel.MEDIUM: 10,
                    BusinessImpactLevel.LOW: 0
                },
                'revenue_hourly': {
                    BusinessImpactLevel.CRITICAL: 10000.0,
                    BusinessImpactLevel.HIGH: 1000.0,
                    BusinessImpactLevel.MEDIUM: 100.0,
                    BusinessImpactLevel.LOW: 0.0
                }
            }
        }
    
    def classify_incident(self, features: IncidentFeatures) -> ClassificationResult:
        """
        Classify incident using ML models and business rules
        
        Args:
            features: Incident features for classification
            
        Returns:
            ClassificationResult with predictions and recommendations
        """
        try:
            # Start with rule-based classification
            rule_result = self._rule_based_classification(features)
            
            # Enhance with ML if available and trained
            if ML_AVAILABLE and self.is_trained:
                ml_result = self._ml_classification(features)
                # Combine rule-based and ML results
                final_result = self._combine_classifications(rule_result, ml_result)
            else:
                final_result = rule_result
            
            # Apply business rules for final adjustments
            final_result = self._apply_business_rules(final_result, features)
            
            logger.info(f"Classified incident {features.incident_id}: "
                       f"{final_result.incident_category.value} "
                       f"({final_result.business_impact.value})")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Classification failed for incident {features.incident_id}: {e}")
            # Return default classification
            return self._default_classification(features)
    
    def _rule_based_classification(self, features: IncidentFeatures) -> ClassificationResult:
        """Rule-based incident classification"""
        text_content = f"{features.title} {features.description} {features.error_message or ''}".lower()
        
        # Classify workflow stage
        workflow_stage = self._classify_workflow_stage(text_content)
        
        # Classify incident category
        incident_category = self._classify_incident_category(text_content)
        
        # Assess business impact
        business_impact = self._assess_business_impact(features)
        
        # Assign team
        team_assignment = self._assign_team(workflow_stage, incident_category)
        
        # Determine severity
        severity = self._determine_severity(business_impact, incident_category)
        
        # Auto-escalation logic
        auto_escalate = self._should_auto_escalate(business_impact, severity)
        
        confidence_scores = {
            'workflow': 0.8,  # Rule-based confidence
            'category': 0.8,
            'impact': 0.9,
            'team': 0.85
        }
        
        reasoning = f"Rule-based classification: {workflow_stage.value} → {incident_category.value}"
        
        return ClassificationResult(
            incident_id=features.incident_id,
            workflow_stage=workflow_stage,
            incident_category=incident_category,
            business_impact=business_impact,
            team_assignment=team_assignment,
            confidence_scores=confidence_scores,
            severity_recommendation=severity,
            auto_escalate=auto_escalate,
            reasoning=reasoning,
            classification_timestamp=datetime.utcnow()
        )
    
    def _classify_workflow_stage(self, text_content: str) -> CreatorWorkflowStage:
        """Classify workflow stage using pattern matching"""
        max_score = 0
        best_stage = CreatorWorkflowStage.UNKNOWN
        
        for stage, patterns in self.workflow_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_content)
            if score > max_score:
                max_score = score
                best_stage = CreatorWorkflowStage(stage)
        
        return best_stage
    
    def _classify_incident_category(self, text_content: str) -> IncidentCategory:
        """Classify incident category using pattern matching"""
        max_score = 0
        best_category = IncidentCategory.PERFORMANCE_DEGRADATION
        
        for category, patterns in self.category_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_content)
            if score > max_score:
                max_score = score
                best_category = IncidentCategory(category)
        
        return best_category
    
    def _assess_business_impact(self, features: IncidentFeatures) -> BusinessImpactLevel:
        """Assess business impact based on metrics"""
        thresholds = self.business_rules['impact_thresholds']
        
        # Check creators affected
        creators_affected = features.affected_creators or 0
        for level in [BusinessImpactLevel.CRITICAL, BusinessImpactLevel.HIGH, 
                     BusinessImpactLevel.MEDIUM, BusinessImpactLevel.LOW]:
            if creators_affected >= thresholds['creators_affected'][level]:
                return level
        
        # Check revenue impact
        revenue_impact = features.revenue_impact_hourly or 0.0
        for level in [BusinessImpactLevel.CRITICAL, BusinessImpactLevel.HIGH,
                     BusinessImpactLevel.MEDIUM, BusinessImpactLevel.LOW]:
            if revenue_impact >= thresholds['revenue_hourly'][level]:
                return level
        
        # Check critical services
        if features.service_name in self.business_rules['critical_services']:
            return BusinessImpactLevel.HIGH
        
        return BusinessImpactLevel.LOW
    
    def _assign_team(self, workflow_stage: CreatorWorkflowStage, 
                    category: IncidentCategory) -> TeamAssignment:
        """Assign specialized team based on classification"""
        team_mapping = {
            CreatorWorkflowStage.AI_PROCESSING: TeamAssignment.AI_ML_TEAM,
            CreatorWorkflowStage.IP_PROTECTION: TeamAssignment.CONTENT_PROTECTION,
            CreatorWorkflowStage.MONETIZATION: TeamAssignment.BUSINESS_OPERATIONS,
            CreatorWorkflowStage.COLLABORATION: TeamAssignment.CREATOR_SUCCESS,
            IncidentCategory.SECURITY_BREACH: TeamAssignment.SECURITY_TEAM,
            IncidentCategory.COMPLIANCE_VIOLATION: TeamAssignment.LEGAL_COMPLIANCE,
            IncidentCategory.AI_MODEL_ERROR: TeamAssignment.AI_ML_TEAM,
            IncidentCategory.PROTECTION_VIOLATION: TeamAssignment.CONTENT_PROTECTION
        }
        
        # Check category first (higher priority)
        if category in team_mapping:
            return team_mapping[category]
        
        # Check workflow stage
        if workflow_stage in team_mapping:
            return team_mapping[workflow_stage]
        
        # Default to DevOps
        return TeamAssignment.DEVOPS_ONCALL
    
    def _determine_severity(self, impact: BusinessImpactLevel, 
                          category: IncidentCategory) -> IncidentSeverity:
        """Determine incident severity"""
        severity_mapping = {
            BusinessImpactLevel.CRITICAL: IncidentSeverity.CRITICAL,
            BusinessImpactLevel.HIGH: IncidentSeverity.ERROR,
            BusinessImpactLevel.MEDIUM: IncidentSeverity.WARNING,
            BusinessImpactLevel.LOW: IncidentSeverity.INFO
        }
        
        # Security and compliance are always critical
        critical_categories = [
            IncidentCategory.SECURITY_BREACH,
            IncidentCategory.COMPLIANCE_VIOLATION,
            IncidentCategory.REVENUE_IMPACT
        ]
        
        if category in critical_categories:
            return IncidentSeverity.CRITICAL
        
        return severity_mapping.get(impact, IncidentSeverity.WARNING)
    
    def _should_auto_escalate(self, impact: BusinessImpactLevel, 
                            severity: IncidentSeverity) -> bool:
        """Determine if incident should auto-escalate"""
        auto_escalate_conditions = [
            impact == BusinessImpactLevel.CRITICAL,
            severity == IncidentSeverity.CRITICAL
        ]
        
        return any(auto_escalate_conditions)
    
    def _ml_classification(self, features: IncidentFeatures) -> Optional[ClassificationResult]:
        """ML-based classification (placeholder for trained models)"""
        if not self.is_trained:
            return None
        
        # TODO: Implement actual ML inference
        # This would use trained models to predict classifications
        logger.info("ML classification not yet implemented")
        return None
    
    def _combine_classifications(self, rule_result: ClassificationResult,
                               ml_result: Optional[ClassificationResult]) -> ClassificationResult:
        """Combine rule-based and ML classification results"""
        if not ml_result:
            return rule_result
        
        # TODO: Implement intelligent combination logic
        # For now, prefer rule-based with ML confidence scores
        return rule_result
    
    def _apply_business_rules(self, result: ClassificationResult,
                            features: IncidentFeatures) -> ClassificationResult:
        """Apply final business rules and adjustments"""
        # Critical service override
        if features.service_name in self.business_rules['critical_services']:
            if result.business_impact == BusinessImpactLevel.LOW:
                result.business_impact = BusinessImpactLevel.MEDIUM
                result.severity_recommendation = IncidentSeverity.WARNING
        
        # Weekend/off-hours escalation
        if features.timestamp:
            is_weekend = features.timestamp.weekday() >= 5
            is_off_hours = features.timestamp.hour < 8 or features.timestamp.hour > 18
            
            if (is_weekend or is_off_hours) and result.severity_recommendation == IncidentSeverity.CRITICAL:
                result.auto_escalate = True
        
        return result
    
    def _default_classification(self, features: IncidentFeatures) -> ClassificationResult:
        """Default classification when all else fails"""
        return ClassificationResult(
            incident_id=features.incident_id,
            workflow_stage=CreatorWorkflowStage.UNKNOWN,
            incident_category=IncidentCategory.PERFORMANCE_DEGRADATION,
            business_impact=BusinessImpactLevel.MEDIUM,
            team_assignment=TeamAssignment.DEVOPS_ONCALL,
            confidence_scores={'overall': 0.5},
            severity_recommendation=IncidentSeverity.WARNING,
            auto_escalate=False,
            reasoning="Default classification - classification failed",
            classification_timestamp=datetime.utcnow()
        )
    
    def train_models(self, training_data: List[Tuple[IncidentFeatures, ClassificationResult]]) -> bool:
        """
        Train ML models on historical incident data
        
        Args:
            training_data: List of (features, expected_result) tuples
            
        Returns:
            bool: True if training successful
        """
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available. Cannot train models.")
            return False
        
        try:
            logger.info(f"Training models on {len(training_data)} incidents")
            
            # Prepare training data
            X = []
            y_workflow = []
            y_category = []
            y_impact = []
            y_team = []
            
            for features, result in training_data:
                feature_vector = features.to_feature_vector()
                X.append(feature_vector)
                y_workflow.append(result.workflow_stage.value)
                y_category.append(result.incident_category.value)
                y_impact.append(result.business_impact.value)
                y_team.append(result.team_assignment.value)
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(X)
            
            # Prepare text vectorizer
            self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            text_features = self.text_vectorizer.fit_transform(df['text_content'])
            
            # Combine with numerical features
            numerical_cols = ['title_length', 'description_length', 'affected_creators',
                            'revenue_impact', 'hour_of_day', 'day_of_week']
            numerical_features = df[numerical_cols].fillna(0)
            
            # Create final feature matrix
            import scipy.sparse
            X_combined = scipy.sparse.hstack([text_features, numerical_features])
            
            # Train classifiers
            self.workflow_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.category_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.impact_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.team_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            
            self.workflow_classifier.fit(X_combined, y_workflow)
            self.category_classifier.fit(X_combined, y_category)
            self.impact_classifier.fit(X_combined, y_impact)
            self.team_classifier.fit(X_combined, y_team)
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics and health metrics"""
        return {
            'is_ml_available': ML_AVAILABLE,
            'is_trained': self.is_trained,
            'workflow_patterns_count': sum(len(patterns) for patterns in self.workflow_patterns.values()),
            'category_patterns_count': sum(len(patterns) for patterns in self.category_patterns.values()),
            'business_rules_count': len(self.business_rules),
            'supported_workflow_stages': [stage.value for stage in CreatorWorkflowStage],
            'supported_categories': [cat.value for cat in IncidentCategory],
            'supported_impact_levels': [level.value for level in BusinessImpactLevel],
            'supported_teams': [team.value for team in TeamAssignment]
        }


# Factory function
def create_creator_incident_classifier(model_path: Optional[str] = None) -> CreatorIncidentClassifier:
    """Create new creator incident classifier instance"""
    return CreatorIncidentClassifier(model_path)


# Export all classes and functions
__all__ = [
    'CreatorIncidentClassifier',
    'CreatorWorkflowStage',
    'IncidentCategory',
    'BusinessImpactLevel',
    'TeamAssignment',
    'IncidentFeatures',
    'ClassificationResult',
    'create_creator_incident_classifier'
]