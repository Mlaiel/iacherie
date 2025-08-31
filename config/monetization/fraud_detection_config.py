"""Fraud Detection and Risk Management Configuration
===============================================

Professional fraud detection and risk management configuration for revenue protection.
Advanced ML-based fraud detection, risk scoring, and automated prevention systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class RiskLevel(str, Enum):
    """Risk level classification."""    VERY_LOW = "very_low"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class FraudType(str, Enum):
    """Types of fraud detection."""    PAYMENT_FRAUD = "payment_fraud"
    IDENTITY_FRAUD = "identity_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    VELOCITY_ABUSE = "velocity_abuse"
    CHARGEBACKS = "chargebacks"
    MONEY_LAUNDERING = "money_laundering"
    FAKE_STREAMS = "fake_streams"
    BOT_ACTIVITY = "bot_activity"
    CLICK_FRAUD = "click_fraud"
    REVENUE_MANIPULATION = "revenue_manipulation"


class DetectionMethod(str, Enum):
    """Fraud detection methods."""    RULE_BASED = "rule_based"
    MACHINE_LEARNING = "machine_learning"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    DEVICE_FINGERPRINTING = "device_fingerprinting"
    GEOLOCATION_ANALYSIS = "geolocation_analysis"
    VELOCITY_CHECKING = "velocity_checking"
    BLACKLIST_CHECKING = "blacklist_checking"
    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    CONSORTIUM_DATA = "consortium_data"


class ActionType(str, Enum):
    """Actions to take when fraud is detected."""    ALLOW = "allow"
    REVIEW = "review"
    CHALLENGE = "challenge"  # Request additional verification
    BLOCK = "block"
    QUARANTINE = "quarantine"
    SUSPEND_ACCOUNT = "suspend_account"
    LIMIT_ACTIVITY = "limit_activity"
    REQUIRE_VERIFICATION = "require_verification"
    ALERT_ADMIN = "alert_admin"
    LOG_ONLY = "log_only"


@dataclass
class RiskThreshold:
    """Risk threshold configuration for different actions."""    risk_level: RiskLevel
    min_score: Decimal
    max_score: Decimal
    action: ActionType
    requires_manual_review: bool = False
    automatic_escalation: bool = False
    escalation_delay_minutes: int = 30


@dataclass
class FraudRule:
    """Individual fraud detection rule configuration."""    rule_id: str
    rule_name: str
    fraud_type: FraudType
    detection_method: DetectionMethod
    enabled: bool = True
    weight: Decimal = Decimal("1.0")  # Rule weight in scoring
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    threshold_values: Dict[str, Union[int, float, Decimal]] = field(default_factory=dict)
    
    # Actions
    action_on_match: ActionType = ActionType.REVIEW
    escalation_required: bool = False
    
    # Metadata
    description: str = ""
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    effectiveness_score: Optional[Decimal] = None


@dataclass
class MLModelConfig:
    """Machine Learning model configuration for fraud detection."""    model_name: str
    model_type: str  # "random_forest", "neural_network", "gradient_boosting", etc.
    model_path: str
    enabled: bool = True
    
    # Training Configuration
    training_data_sources: List[str] = field(default_factory=list)
    feature_columns: List[str] = field(default_factory=list)
    target_column: str = "is_fraud"
    retraining_frequency_days: int = 7
    minimum_training_samples: int = 10000
    
    # Performance Metrics
    accuracy_threshold: Decimal = Decimal("0.95")
    precision_threshold: Decimal = Decimal("0.90")
    recall_threshold: Decimal = Decimal("0.85")
    f1_score_threshold: Decimal = Decimal("0.88")
    
    # Prediction Configuration
    prediction_threshold: Decimal = Decimal("0.5")
    confidence_threshold: Decimal = Decimal("0.8")
    batch_prediction_enabled: bool = True
    real_time_prediction_enabled: bool = True


@dataclass
class DeviceFingerprinting:
    """Device fingerprinting configuration."""    enabled: bool = True
    collect_browser_info: bool = True
    collect_screen_info: bool = True
    collect_timezone_info: bool = True
    collect_language_info: bool = True
    collect_plugin_info: bool = True
    collect_canvas_fingerprint: bool = True
    collect_webgl_fingerprint: bool = True
    collect_audio_fingerprint: bool = True
    
    # Privacy Settings
    hash_fingerprints: bool = True
    anonymize_ip: bool = True
    retention_days: int = 365
    consent_required: bool = True  # GDPR compliance


@dataclass
class VelocityCheck:
    """Velocity checking configuration."""    enabled: bool = True
    time_windows: List[int] = field(default_factory=lambda: [60, 300, 3600, 86400])  # 1m, 5m, 1h, 1d
    
    # Transaction Velocity Limits
    max_transactions_per_minute: int = 10
    max_transactions_per_hour: int = 100
    max_transactions_per_day: int = 1000
    max_amount_per_hour: Decimal = Decimal("1000.00")
    max_amount_per_day: Decimal = Decimal("10000.00")
    
    # User Behavior Velocity
    max_login_attempts_per_minute: int = 5
    max_password_resets_per_hour: int = 3
    max_payment_method_changes_per_day: int = 5
    
    # Geographic Velocity
    impossible_travel_detection: bool = True
    max_travel_speed_kmh: int = 1000  # Max realistic travel speed


class FraudDetectionConfig:
    """    Professional fraud detection and risk management configuration.
    Comprehensive fraud prevention with ML, rule engine, and behavioral analysis.
    """    
    def __init__(self):
        """Initialize fraud detection configuration."""        
        # Database Configuration
        self.FRAUD_DB_URL = os.getenv(
            "FRAUD_DB_URL",
            "postgresql://user:pass@localhost:5432/fraud_detection_db"
        )
        
        # Redis for real-time data
        self.REDIS_FRAUD_URL = os.getenv(
            "FRAUD_REDIS_URL",
            "redis://localhost:6379/7"
        )
        
        # ML Model Storage
        self.ML_MODELS_PATH = os.getenv("FRAUD_ML_MODELS_PATH", "/data/fraud_models")
        self.MODEL_REGISTRY_URL = os.getenv("ML_REGISTRY_URL", "http://localhost:5001")
        
        # General Configuration
        self.ENABLE_FRAUD_DETECTION = True
        self.ENABLE_REAL_TIME_SCORING = True
        self.ENABLE_BATCH_PROCESSING = True
        self.ENABLE_ML_PREDICTIONS = True
        
        # Risk Scoring Configuration
        self.RISK_THRESHOLDS = self._initialize_risk_thresholds()
        
        # Fraud Detection Rules
        self.FRAUD_RULES = self._initialize_fraud_rules()
        
        # ML Models Configuration
        self.ML_MODELS = self._initialize_ml_models()
        
        # Device Fingerprinting
        self.DEVICE_FINGERPRINTING = DeviceFingerprinting()
        
        # Velocity Checking
        self.VELOCITY_CHECKS = VelocityCheck()
        
        # Blacklists and Whitelists
        self.BLACKLIST_CONFIG = {
            "ip_blacklist_enabled": True,
            "email_blacklist_enabled": True,
            "device_blacklist_enabled": True,
            "country_blacklist": ["CU", "IR", "KP", "SY"],  # Sanctioned countries
            "high_risk_countries": ["NG", "GH", "PK", "BD"],
            "automatic_blacklist_updates": True,
            "consortium_blacklist_enabled": True
        }
        
        self.WHITELIST_CONFIG = {
            "trusted_ip_ranges": [],
            "verified_merchants": [],
            "whitelisted_countries": ["DE", "US", "GB", "FR", "IT", "ES", "NL"],
            "bypass_fraud_checks": False  # Even whitelisted should be monitored
        }
        
        # Behavioral Analysis
        self.BEHAVIORAL_ANALYSIS = {
            "enabled": True,
            "track_user_patterns": True,
            "track_session_behavior": True,
            "track_payment_patterns": True,
            "anomaly_detection_enabled": True,
            "learning_period_days": 30,
            "deviation_threshold_std": 2.5
        }
        
        # Alert Configuration
        self.ALERT_CONFIG = {
            "enable_real_time_alerts": True,
            "alert_channels": ["email", "slack", "webhook", "sms"],
            "escalation_matrix": {
                RiskLevel.HIGH: ["fraud_team_lead", "security_manager"],
                RiskLevel.VERY_HIGH: ["fraud_team_lead", "security_manager", "cto"],
                RiskLevel.CRITICAL: ["fraud_team_lead", "security_manager", "cto", "ceo"]
            },
            "alert_rate_limiting": True,
            "max_alerts_per_minute": 10,
            "alert_deduplication_window_minutes": 5
        }
        
        # Performance Configuration
        self.PERFORMANCE_CONFIG = {
            "max_concurrent_scoring_requests": 100,
            "scoring_timeout_ms": 500,
            "batch_processing_size": 1000,
            "cache_scoring_results": True,
            "cache_ttl_minutes": 15,
            "async_rule_execution": True,
            "parallel_ml_inference": True
        }
        
        # Data Retention and Privacy
        self.DATA_RETENTION_CONFIG = {
            "fraud_scores_retention_days": 2555,  # 7 years
            "device_fingerprints_retention_days": 365,
            "behavior_data_retention_days": 730,  # 2 years
            "anonymize_after_days": 1095,  # 3 years
            "gdpr_compliance": True,
            "right_to_be_forgotten": True,
            "data_encryption_at_rest": True
        }
        
        # Integration Configuration
        self.INTEGRATION_CONFIG = {
            "payment_processor_integration": True,
            "kyc_provider_integration": True,
            "credit_bureau_integration": False,  # Enterprise feature
            "law_enforcement_reporting": True,
            "regulatory_reporting": True,
            "third_party_data_enrichment": True
        }
    
    def _initialize_risk_thresholds(self) -> List[RiskThreshold]:
        """Initialize risk threshold configurations."""        return [
            RiskThreshold(
                risk_level=RiskLevel.VERY_LOW,
                min_score=Decimal("0.0"),
                max_score=Decimal("0.1"),
                action=ActionType.ALLOW
            ),
            RiskThreshold(
                risk_level=RiskLevel.LOW,
                min_score=Decimal("0.1"),
                max_score=Decimal("0.3"),
                action=ActionType.ALLOW
            ),
            RiskThreshold(
                risk_level=RiskLevel.MEDIUM,
                min_score=Decimal("0.3"),
                max_score=Decimal("0.6"),
                action=ActionType.REVIEW,
                requires_manual_review=False
            ),
            RiskThreshold(
                risk_level=RiskLevel.HIGH,
                min_score=Decimal("0.6"),
                max_score=Decimal("0.8"),
                action=ActionType.CHALLENGE,
                requires_manual_review=True,
                automatic_escalation=True,
                escalation_delay_minutes=15
            ),
            RiskThreshold(
                risk_level=RiskLevel.VERY_HIGH,
                min_score=Decimal("0.8"),
                max_score=Decimal("0.95"),
                action=ActionType.BLOCK,
                requires_manual_review=True,
                automatic_escalation=True,
                escalation_delay_minutes=5
            ),
            RiskThreshold(
                risk_level=RiskLevel.CRITICAL,
                min_score=Decimal("0.95"),
                max_score=Decimal("1.0"),
                action=ActionType.SUSPEND_ACCOUNT,
                requires_manual_review=True,
                automatic_escalation=True,
                escalation_delay_minutes=0  # Immediate
            )
        ]
    
    def _initialize_fraud_rules(self) -> List[FraudRule]:
        """Initialize fraud detection rules."""        return [
            # Payment Fraud Rules
            FraudRule(
                rule_id="PF001",
                rule_name="High Velocity Transactions",
                fraud_type=FraudType.PAYMENT_FRAUD,
                detection_method=DetectionMethod.VELOCITY_CHECKING,
                conditions={
                    "transaction_count_1h": ">= 20",
                    "unique_payment_methods": ">= 5"
                },
                threshold_values={"transaction_count": 20, "time_window": 3600},
                action_on_match=ActionType.REVIEW,
                weight=Decimal("0.7"),
                description="Detects unusually high transaction velocity"
            ),
            
            FraudRule(
                rule_id="PF002",
                rule_name="Unusual Geographic Activity",
                fraud_type=FraudType.PAYMENT_FRAUD,
                detection_method=DetectionMethod.GEOLOCATION_ANALYSIS,
                conditions={
                    "impossible_travel": "true",
                    "high_risk_country": "true"
                },
                action_on_match=ActionType.CHALLENGE,
                weight=Decimal("0.8"),
                description="Detects impossible travel patterns or high-risk locations"
            ),
            
            FraudRule(
                rule_id="PF003",
                rule_name="Suspicious Payment Amount",
                fraud_type=FraudType.PAYMENT_FRAUD,
                detection_method=DetectionMethod.PATTERN_RECOGNITION,
                conditions={
                    "amount_deviation": "> 5.0",  # Standard deviations from user's norm
                    "round_number_pattern": "true"
                },
                action_on_match=ActionType.REVIEW,
                weight=Decimal("0.5"),
                description="Detects unusual payment amounts or suspicious patterns"
            ),
            
            # Identity Fraud Rules
            FraudRule(
                rule_id="IF001",
                rule_name="Device Fingerprint Mismatch",
                fraud_type=FraudType.IDENTITY_FRAUD,
                detection_method=DetectionMethod.DEVICE_FINGERPRINTING,
                conditions={
                    "device_change_frequency": "> 3",  # Per week
                    "fingerprint_similarity": "< 0.5"
                },
                action_on_match=ActionType.REQUIRE_VERIFICATION,
                weight=Decimal("0.6"),
                description="Detects frequent device changes or fingerprint anomalies"
            ),
            
            # Account Takeover Rules
            FraudRule(
                rule_id="AT001",
                rule_name="Login Pattern Anomaly",
                fraud_type=FraudType.ACCOUNT_TAKEOVER,
                detection_method=DetectionMethod.BEHAVIORAL_ANALYSIS,
                conditions={
                    "login_time_anomaly": "true",
                    "failed_login_attempts": ">= 5",
                    "password_reset_requests": ">= 2"
                },
                action_on_match=ActionType.CHALLENGE,
                weight=Decimal("0.8"),
                escalation_required=True,
                description="Detects suspicious login patterns indicating account takeover"
            ),
            
            # Revenue Manipulation Rules
            FraudRule(
                rule_id="RM001",
                rule_name="Artificial Stream Inflation",
                fraud_type=FraudType.FAKE_STREAMS,
                detection_method=DetectionMethod.PATTERN_RECOGNITION,
                conditions={
                    "stream_spike": "> 10.0",  # 10x normal rate
                    "unique_listeners_ratio": "< 0.1",  # Low unique listener ratio
                    "bot_score": "> 0.7"
                },
                action_on_match=ActionType.QUARANTINE,
                weight=Decimal("0.9"),
                escalation_required=True,
                description="Detects artificial stream inflation and bot activity"
            ),
            
            FraudRule(
                rule_id="RM002",
                rule_name="Click Fraud Detection",
                fraud_type=FraudType.CLICK_FRAUD,
                detection_method=DetectionMethod.ANOMALY_DETECTION,
                conditions={
                    "click_through_rate": "> 0.05",  # Unusually high CTR
                    "session_duration": "< 5",  # Very short sessions
                    "bounce_rate": "> 0.95"
                },
                action_on_match=ActionType.LIMIT_ACTIVITY,
                weight=Decimal("0.7"),
                description="Detects fraudulent click activity"
            )
        ]
    
    def _initialize_ml_models(self) -> Dict[str, MLModelConfig]:
        """Initialize ML model configurations."""        return {
            "payment_fraud_classifier": MLModelConfig(
                model_name="Payment Fraud Classifier",
                model_type="gradient_boosting",
                model_path=os.path.join(self.ML_MODELS_PATH, "payment_fraud_model.pkl"),
                feature_columns=[
                    "transaction_amount", "payment_method", "merchant_category",
                    "user_age_days", "historical_transaction_count", "device_score",
                    "geographic_risk_score", "velocity_score", "behavior_score"
                ],
                retraining_frequency_days=3,
                accuracy_threshold=Decimal("0.96"),
                prediction_threshold=Decimal("0.6")
            ),
            
            "behavioral_anomaly_detector": MLModelConfig(
                model_name="Behavioral Anomaly Detector",
                model_type="isolation_forest",
                model_path=os.path.join(self.ML_MODELS_PATH, "behavioral_anomaly_model.pkl"),
                feature_columns=[
                    "login_frequency", "session_duration", "pages_visited",
                    "click_patterns", "typing_patterns", "navigation_patterns"
                ],
                retraining_frequency_days=1,  # Daily retraining for behavior
                accuracy_threshold=Decimal("0.92"),
                prediction_threshold=Decimal("0.4")  # More sensitive
            ),
            
            "revenue_manipulation_detector": MLModelConfig(
                model_name="Revenue Manipulation Detector",
                model_type="neural_network",
                model_path=os.path.join(self.ML_MODELS_PATH, "revenue_manipulation_model.h5"),
                feature_columns=[
                    "stream_velocity", "unique_listener_ratio", "geographic_distribution",
                    "time_pattern_score", "device_diversity", "engagement_metrics"
                ],
                retraining_frequency_days=7,
                accuracy_threshold=Decimal("0.94"),
                prediction_threshold=Decimal("0.5")
            )
        }
    
    def get_risk_threshold(self, score: Decimal) -> Optional[RiskThreshold]:
        """Get risk threshold for a given score."""        for threshold in self.RISK_THRESHOLDS:
            if threshold.min_score <= score <= threshold.max_score:
                return threshold
        return None
    
    def get_fraud_rule(self, rule_id: str) -> Optional[FraudRule]:
        """Get fraud rule by ID."""        return next((rule for rule in self.FRAUD_RULES if rule.rule_id == rule_id), None)
    
    def get_enabled_rules(self, fraud_type: Optional[FraudType] = None) -> List[FraudRule]:
        """Get enabled fraud rules, optionally filtered by fraud type."""        rules = [rule for rule in self.FRAUD_RULES if rule.enabled]
        if fraud_type:
            rules = [rule for rule in rules if rule.fraud_type == fraud_type]
        return rules
    
    def get_ml_model(self, model_name: str) -> Optional[MLModelConfig]:
        """Get ML model configuration by name."""        return self.ML_MODELS.get(model_name)
    
    def calculate_composite_risk_score(self, individual_scores: Dict[str, Decimal]) -> Decimal:
        """Calculate composite risk score from individual rule scores."""        if not individual_scores:
            return Decimal("0.0")
        
        # Weighted average of all scores
        total_weight = Decimal("0.0")
        weighted_sum = Decimal("0.0")
        
        for rule_id, score in individual_scores.items():
            rule = self.get_fraud_rule(rule_id)
            if rule and rule.enabled:
                weight = rule.weight
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight == Decimal("0.0"):
            return Decimal("0.0")
        
        composite_score = weighted_sum / total_weight
        
        # Ensure score is between 0 and 1
        return max(Decimal("0.0"), min(Decimal("1.0"), composite_score))
    
    def should_escalate(self, risk_score: Decimal) -> Tuple[bool, Optional[int]]:
        """Determine if a case should be escalated and when."""        threshold = self.get_risk_threshold(risk_score)
        if threshold and threshold.automatic_escalation:
            return True, threshold.escalation_delay_minutes
        return False, None
    
    def get_recommended_action(self, risk_score: Decimal) -> ActionType:
        """Get recommended action based on risk score."""        threshold = self.get_risk_threshold(risk_score)
        return threshold.action if threshold else ActionType.LOG_ONLY


# Global configuration instance
fraud_detection_config = FraudDetectionConfig()
