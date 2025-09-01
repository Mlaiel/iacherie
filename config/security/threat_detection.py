"""Threat Detection Configuration Module
====================================

Advanced threat detection and security monitoring configuration for 
IA Influencer Agent platform. Provides comprehensive threat intelligence,
anomaly detection, and security incident response configurations.

Business Logic Integration:
- Content upload threat detection for creator protection
- Platform integration security monitoring
- Revenue operation fraud detection
- AI-powered anomaly detection for creator behavior

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class ThreatLevel(Enum):
    """
Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ThreatCategory(Enum):
    """Categories of security threats."""

    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    ACCOUNT_TAKEOVER = "account_takeover"
    FRAUD = "fraud"
    DDOS = "ddos"
    INJECTION_ATTACK = "injection_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    SOCIAL_ENGINEERING = "social_engineering"
    RANSOMWARE = "ransomware"


class DetectionMethod(Enum):
    """Threat detection methods."""

    SIGNATURE_BASED = "signature_based"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    MACHINE_LEARNING = "machine_learning"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    RULE_BASED = "rule_based"
    ANOMALY_DETECTION = "anomaly_detection"
    THREAT_INTELLIGENCE = "threat_intelligence"
    HEURISTIC_ANALYSIS = "heuristic_analysis"


class ResponseAction(Enum):
    """Automated response actions."""

    ALERT = "alert"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ISOLATE = "isolate"
    TERMINATE_SESSION = "terminate_session"
    DISABLE_ACCOUNT = "disable_account"
    RATE_LIMIT = "rate_limit"
    REDIRECT = "redirect"
    LOG_ONLY = "log_only"


@dataclass
class ThreatSignature:
    """Threat signature definition."""
    signature_id: str
    category: ThreatCategory
    severity: ThreatLevel
    pattern: str
    description: str
    enabled: bool = True
    
    # Signature metadata
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    version: str = "1.0"
    author: str = "IA Security Team"
    
    # Detection criteria
    confidence_threshold: float = 0.8
    false_positive_rate: Optional[float] = None
    
    # Response configuration
    response_actions: List[ResponseAction] = field(default_factory=list)
    escalation_required: bool = False


@dataclass
class MalwareDetectionConfig:
    """Malware detection configuration."""
    
    # Detection engines
    enabled_engines: List[str] = field(default_factory=lambda: [
        "clamav", "yara", "custom_ml", "hash_lookup", "behavioral_analysis"
    ])
    
    # File type scanning
    scan_file_types: Set[str] = field(default_factory=lambda: {
        "exe", "dll", "bat", "cmd", "ps1", "vbs", "js", "jar", "zip", "rar"
    })
    
    # Content scanning for creators
    creator_content_scanning: Dict[str, Any] = field(default_factory=lambda: {
        "audio_files": True,
        "video_files": True,
        "image_files": True,
        "document_files": True,
        "embedded_content": True,
        "metadata_analysis": True
    })
    
    # Behavioral analysis
    behavioral_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "process_monitoring": True,
        "network_activity": True,
        "file_system_changes": True,
        "registry_modifications": True,
        "memory_analysis": True,
        "api_call_monitoring": True
    })
    
    # Machine learning models
    ml_models: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "static_analysis": {
            "model_path": "/opt/ml-models/malware-static.model",
            "confidence_threshold": 0.85,
            "feature_extraction": "pe_headers",
            "update_frequency": "weekly"
        },
        "dynamic_analysis": {
            "model_path": "/opt/ml-models/malware-dynamic.model",
            "confidence_threshold": 0.80,
            "sandbox_integration": True,
            "behavioral_features": True
        }
    })
    
    # Quarantine settings
    quarantine_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "quarantine_path": "/var/quarantine/malware",
        "retention_days": 30,
        "encryption_enabled": True,
        "access_logging": True
    })


@dataclass
class AnomalyDetectionConfig:
    """Anomaly detection configuration."""
    
    # User behavior analysis
    user_behavior_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "baseline_period_days": 30,
        "deviation_threshold": 2.5,  # Standard deviations
        "learning_rate": 0.1,
        "adaptation_window": 7  # days
    })
    
    # Content creator behavior monitoring
    creator_behavior_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        "upload_patterns": True,
        "platform_usage_patterns": True,
        "revenue_patterns": True,
        "collaboration_patterns": True,
        "api_usage_patterns": True,
        "geographic_patterns": True
    })
    
    # Network anomaly detection
    network_anomaly_detection: Dict[str, Any] = field(default_factory=lambda: {
        "traffic_analysis": True,
        "connection_patterns": True,
        "bandwidth_usage": True,
        "protocol_analysis": True,
        "geolocation_analysis": True,
        "time_based_analysis": True
    })
    
    # System anomaly detection
    system_anomaly_detection: Dict[str, Any] = field(default_factory=lambda: {
        "resource_usage": True,
        "performance_metrics": True,
        "error_rate_analysis": True,
        "response_time_analysis": True,
        "database_query_patterns": True,
        "cache_hit_rates": True
    })
    
    # Machine learning algorithms
    ml_algorithms: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "isolation_forest": {
            "contamination": 0.1,
            "n_estimators": 100,
            "max_features": 1.0
        },
        "one_class_svm": {
            "kernel": "rbf",
            "gamma": "scale",
            "nu": 0.05
        },
        "lstm_autoencoder": {
            "sequence_length": 50,
            "encoding_dim": 32,
            "threshold": 0.02
        }
    })


@dataclass
class FraudDetectionConfig:
    """Fraud detection for revenue and financial operations."""
    
    # Revenue fraud detection
    revenue_fraud_detection: Dict[str, Any] = field(default_factory=lambda: {
        "artificial_streaming": True,
        "bot_engagement": True,
        "fake_metrics": True,
        "revenue_manipulation": True,
        "platform_gaming": True,
        "click_fraud": True
    })
    
    # Payment fraud detection
    payment_fraud_detection: Dict[str, Any] = field(default_factory=lambda: {
        "transaction_velocity": True,
        "unusual_amounts": True,
        "geographic_inconsistencies": True,
        "device_fingerprinting": True,
        "behavioral_biometrics": True,
        "machine_learning_scoring": True
    })
    
    # Identity fraud detection
    identity_fraud_detection: Dict[str, Any] = field(default_factory=lambda: {
        "document_verification": True,
        "biometric_verification": True,
        "social_graph_analysis": True,
        "device_recognition": True,
        "behavioral_patterns": True,
        "third_party_verification": True
    })
    
    # Risk scoring
    risk_scoring: Dict[str, Any] = field(default_factory=lambda: {
        "real_time_scoring": True,
        "composite_score": True,
        "dynamic_thresholds": True,
        "feedback_loop": True,
        "model_updates": "weekly"
    })
    
    # Fraud rules
    fraud_rules: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "rule_id": "high_velocity_payments",
            "condition": "payment_count > 10 in 1 hour",
            "action": ResponseAction.BLOCK,
            "severity": ThreatLevel.HIGH
        },
        {
            "rule_id": "unusual_upload_volume",
            "condition": "upload_count > 100 in 1 day",
            "action": ResponseAction.RATE_LIMIT,
            "severity": ThreatLevel.MEDIUM
        },
        {
            "rule_id": "geographic_inconsistency",
            "condition": "login_location_change > 1000km in 1 hour",
            "action": ResponseAction.ALERT,
            "severity": ThreatLevel.MEDIUM
        }
    ])


@dataclass
class ThreatIntelligenceConfig:
    """Threat intelligence integration configuration."""
    
    # Threat intelligence feeds
    intelligence_feeds: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "commercial_feed_1",
            "type": "ip_reputation",
            "url": "https://api.threatintel.com/ips",
            "api_key": os.getenv("THREAT_INTEL_API_KEY", ""),
            "update_frequency": "hourly",
            "enabled": True
        },
        {
            "name": "malware_hashes",
            "type": "file_hashes", 
            "url": "https://api.malwarehashes.com/v1",
            "update_frequency": "daily",
            "enabled": True
        },
        {
            "name": "phishing_urls",
            "type": "url_reputation",
            "url": "https://api.phishingurls.com/v1",
            "update_frequency": "hourly",
            "enabled": True
        }
    ])
    
    # Intelligence processing
    processing_config: Dict[str, Any] = field(default_factory=lambda: {
        "automatic_import": True,
        "deduplication": True,
        "confidence_scoring": True,
        "aging_policy": True,
        "false_positive_feedback": True,
        "custom_indicators": True
    })
    
    # Indicator types
    indicator_types: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "ip_addresses": {
            "enabled": True,
            "retention_days": 90,
            "confidence_threshold": 0.7
        },
        "domain_names": {
            "enabled": True,
            "retention_days": 180,
            "confidence_threshold": 0.8
        },
        "file_hashes": {
            "enabled": True,
            "retention_days": 365,
            "confidence_threshold": 0.9
        },
        "urls": {
            "enabled": True,
            "retention_days": 60,
            "confidence_threshold": 0.8
        }
    })
    
    # Threat hunting
    threat_hunting: Dict[str, Any] = field(default_factory=lambda: {
        "proactive_hunting": True,
        "hunting_queries": True,
        "hypothesis_testing": True,
        "ttp_mapping": True,  # MITRE ATT&CK
        "hunting_frequency": "daily",
        "automation_level": "semi_automated"
    })


@dataclass
class IncidentResponseConfig:
    """Security incident response configuration."""
    
    # Response team
    response_team: Dict[str, str] = field(default_factory=lambda: {
        "incident_commander": "security@ia-influencer.com",
        "technical_lead": "devops@ia-influencer.com",
        "communications_lead": "communications@ia-influencer.com",
        "legal_counsel": "legal@ia-influencer.com"
    })
    
    # Escalation matrix
    escalation_matrix: Dict[ThreatLevel, Dict[str, Any]] = field(default_factory=lambda: {
        ThreatLevel.LOW: {
            "auto_response": True,
            "notification_delay": 60,  # minutes
            "escalation_time": 240     # minutes
        },
        ThreatLevel.MEDIUM: {
            "auto_response": True,
            "notification_delay": 15,  # minutes
            "escalation_time": 60      # minutes
        },
        ThreatLevel.HIGH: {
            "auto_response": True,
            "notification_delay": 5,   # minutes
            "escalation_time": 30      # minutes
        },
        ThreatLevel.CRITICAL: {
            "auto_response": True,
            "notification_delay": 1,   # minutes
            "escalation_time": 15      # minutes
        }
    })
    
    # Response playbooks
    response_playbooks: Dict[ThreatCategory, Dict[str, Any]] = field(default_factory=lambda: {
        ThreatCategory.MALWARE: {
            "playbook_id": "PLAY-001",
            "automated_containment": True,
            "isolation_required": True,
            "forensic_imaging": True,
            "stakeholder_notification": ["security", "legal", "communications"]
        },
        ThreatCategory.DATA_BREACH: {
            "playbook_id": "PLAY-002",
            "automated_containment": True,
            "data_classification": True,
            "regulatory_notification": True,
            "customer_notification": True,
            "stakeholder_notification": ["security", "legal", "communications", "privacy"]
        },
        ThreatCategory.ACCOUNT_TAKEOVER: {
            "playbook_id": "PLAY-003",
            "account_suspension": True,
            "password_reset": True,
            "session_termination": True,
            "security_questions_reset": True
        }
    })
    
    # Communication templates
    communication_templates: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "internal_alert": {
            "template_id": "INT-001",
            "subject": "Security Incident Alert - {incident_id}",
            "priority": "urgent",
            "channels": ["email", "slack", "sms"]
        },
        "customer_notification": {
            "template_id": "CUST-001",
            "subject": "Important Security Notice",
            "channels": ["email", "in_app"],
            "approval_required": True
        },
        "regulatory_notification": {
            "template_id": "REG-001",
            "format": "formal",
            "timeline_hours": 72,
            "approval_required": True
        }
    })


@dataclass
class ThreatDetectionMetrics:
    """Threat detection performance metrics configuration."""
    
    # Detection metrics
    detection_metrics: List[str] = field(default_factory=lambda: [
        "true_positive_rate",
        "false_positive_rate", 
        "detection_accuracy",
        "mean_time_to_detection",
        "mean_time_to_response",
        "incident_resolution_time"
    ])
    
    # Performance thresholds
    performance_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "minimum_accuracy": 0.95,
        "maximum_false_positive_rate": 0.05,
        "maximum_detection_time_minutes": 5,
        "maximum_response_time_minutes": 15
    })
    
    # Reporting
    reporting_config: Dict[str, Any] = field(default_factory=lambda: {
        "real_time_dashboard": True,
        "daily_reports": True,
        "weekly_summaries": True,
        "monthly_analysis": True,
        "trend_analysis": True,
        "comparative_analysis": True
    })


@dataclass
class ThreatDetectionConfig:
    """Main threat detection configuration container."""
    
    # Core detection modules
    malware_detection: MalwareDetectionConfig = field(default_factory=MalwareDetectionConfig)
    anomaly_detection: AnomalyDetectionConfig = field(default_factory=AnomalyDetectionConfig)
    fraud_detection: FraudDetectionConfig = field(default_factory=FraudDetectionConfig)
    threat_intelligence: ThreatIntelligenceConfig = field(default_factory=ThreatIntelligenceConfig)
    incident_response: IncidentResponseConfig = field(default_factory=IncidentResponseConfig)
    metrics: ThreatDetectionMetrics = field(default_factory=ThreatDetectionMetrics)
    
    # Global detection settings
    threat_detection_enabled: bool = True
    real_time_detection: bool = True
    automated_response_enabled: bool = True
    
    # Detection tuning
    global_sensitivity: float = 0.8
    false_positive_tolerance: float = 0.05
    detection_delay_seconds: int = 1
    
    # Threat signatures
    custom_signatures: List[ThreatSignature] = field(default_factory=list)
    signature_updates: Dict[str, Any] = field(default_factory=lambda: {
        "automatic_updates": True,
        "update_frequency": "daily",
        "update_source": "security_vendor",
        "manual_approval": False
    })
    
    # Integration settings
    siem_integration: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "siem_platform": "splunk",
        "log_forwarding": True,
        "alert_forwarding": True,
        "bidirectional_sync": True
    })
    
    # Storage and retention
    threat_data_storage: Dict[str, Any] = field(default_factory=lambda: {
        "storage_backend": "elasticsearch",
        "retention_days": 365,
        "compression_enabled": True,
        "encryption_enabled": True,
        "backup_enabled": True
    })
    
    # Performance optimization
    performance_config: Dict[str, Any] = field(default_factory=lambda: {
        "parallel_processing": True,
        "max_concurrent_scans": 10,
        "resource_limits": {
            "cpu_limit_percent": 70,
            "memory_limit_mb": 4096,
            "disk_io_limit_mbps": 100
        },
        "caching_enabled": True,
        "cache_size_mb": 1024
    })


# Default configuration instance
threat_detection_config = ThreatDetectionConfig()


def get_threat_detection_config() -> ThreatDetectionConfig:
    """Get the threat detection configuration instance."""
    return threat_detection_config


def get_threat_signature(signature_id: str) -> Optional[ThreatSignature]:
    """
Get a specific threat signature by ID."""
    config = get_threat_detection_config()
    for signature in config.custom_signatures:
        if signature.signature_id == signature_id:
            return signature
    return None


def get_response_actions(threat_category: ThreatCategory, threat_level: ThreatLevel) -> List[ResponseAction]:
    """
Get appropriate response actions for a threat category and level."""
    config = get_threat_detection_config()
    
    # Get category-specific playbook
    playbook = config.incident_response.response_playbooks.get(threat_category)
    if playbook:
        actions = []
        if playbook.get("automated_containment"):
            actions.append(ResponseAction.QUARANTINE)
        if playbook.get("isolation_required"):
            actions.append(ResponseAction.ISOLATE)
        if playbook.get("account_suspension"):
            actions.append(ResponseAction.DISABLE_ACCOUNT)
        return actions
    
    # Default actions based on threat level
    action_mapping = {
        ThreatLevel.LOW: [ResponseAction.LOG_ONLY, ResponseAction.ALERT],
        ThreatLevel.MEDIUM: [ResponseAction.ALERT, ResponseAction.RATE_LIMIT],
        ThreatLevel.HIGH: [ResponseAction.BLOCK, ResponseAction.ALERT],
        ThreatLevel.CRITICAL: [ResponseAction.QUARANTINE, ResponseAction.ALERT]
    }
    
    return action_mapping.get(threat_level, [ResponseAction.ALERT])


def validate_threat_detection_config(config: ThreatDetectionConfig) -> bool:
    """Validate threat detection configuration settings."""
    # Validate sensitivity thresholds
    if not (0 <= config.global_sensitivity <= 1):
        raise ValueError(f"Global sensitivity must be between 0 and 1: {config.global_sensitivity}")
    
    if not (0 <= config.false_positive_tolerance <= 1):
        raise ValueError(f"False positive tolerance must be between 0 and 1: {config.false_positive_tolerance}")
    
    # Validate performance thresholds
    for threshold in config.metrics.performance_thresholds.values():
        if threshold < 0:
            raise ValueError(f"Performance threshold must be non-negative: {threshold}")
    
    # Validate custom signatures
    for signature in config.custom_signatures:
        if not signature.signature_id:
            raise ValueError("Signature ID is required")
        if not signature.pattern:
            raise ValueError("Signature pattern is required")
    
    return True
