"""Security Monitoring Configuration Module for IA-Influencer Agent Platform
==========================================================================

Professional security monitoring configuration for comprehensive
threat detection, intrusion prevention, and security incident response.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import ipaddress


class ThreatLevel(Enum):
    """Security threat levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Security event types"""    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    NETWORK_INTRUSION = "network_intrusion"
    MALWARE = "malware"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_BREACH = "data_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class ResponseAction(Enum):
    """Security response actions"""    ALERT = "alert"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    QUARANTINE = "quarantine"
    INVESTIGATE = "investigate"
    ESCALATE = "escalate"


@dataclass
class SecurityRule:
    """Security monitoring rule"""    name: str
    event_type: SecurityEventType
    condition: str
    threat_level: ThreatLevel
    response_action: ResponseAction
    description: str
    enabled: bool = True
    threshold: Optional[float] = None
    time_window: str = "5m"


@dataclass
class ThreatIntelligence:
    """Threat intelligence configuration"""    enabled: bool
    feeds: List[str] = field(default_factory=list)
    update_interval: str = "1h"
    reputation_threshold: float = 0.7
    auto_block: bool = False


class SecurityMonitoringConfig:
    """Professional security monitoring configuration for IA-Influencer platform"""    
    def __init__(self):
        self.security_monitoring_enabled = os.getenv("SECURITY_MONITORING_ENABLED", "true").lower() == "true"
        self.intrusion_detection_enabled = os.getenv("INTRUSION_DETECTION_ENABLED", "true").lower() == "true"
        self.threat_intelligence_enabled = os.getenv("THREAT_INTELLIGENCE_ENABLED", "true").lower() == "true"
        self.auto_response_enabled = os.getenv("AUTO_RESPONSE_ENABLED", "false").lower() == "true"
        self.security_log_level = os.getenv("SECURITY_LOG_LEVEL", "INFO")
        self.max_failed_attempts = int(os.getenv("MAX_FAILED_AUTH_ATTEMPTS", "5"))
        self.account_lockout_duration = int(os.getenv("ACCOUNT_LOCKOUT_DURATION", "300"))  # seconds
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
        self.suspicious_activity_threshold = float(os.getenv("SUSPICIOUS_ACTIVITY_THRESHOLD", "0.8"))
        self.environment = os.getenv("ENVIRONMENT", "production")
    
    def get_authentication_monitoring_config(self) -> Dict[str, Any]:
        """Get authentication monitoring configuration"""        return {
            "enabled": self.security_monitoring_enabled,
            "failed_login_threshold": self.max_failed_attempts,
            "lockout_duration": self.account_lockout_duration,
            "monitoring_rules": {
                "brute_force_detection": {
                    "enabled": True,
                    "max_attempts": self.max_failed_attempts,
                    "time_window": "5m",
                    "action": "block_ip",
                    "duration": "1h"
                },
                "credential_stuffing": {
                    "enabled": True,
                    "max_users_per_ip": 20,
                    "time_window": "10m",
                    "action": "rate_limit"
                },
                "impossible_travel": {
                    "enabled": True,
                    "max_distance_km": 1000,
                    "min_time_hours": 1,
                    "action": "alert"
                },
                "unusual_login_patterns": {
                    "enabled": True,
                    "track_user_agents": True,
                    "track_locations": True,
                    "deviation_threshold": 0.8
                }
            },
            "multi_factor_authentication": {
                "enforce_for_admin": True,
                "enforce_for_suspicious": True,
                "bypass_trusted_networks": False
            },
            "session_security": {
                "session_timeout": 3600,
                "concurrent_session_limit": 5,
                "secure_cookie_flags": True,
                "session_fixation_protection": True
            }
        }
    
    def get_network_security_monitoring_config(self) -> Dict[str, Any]:
        """Get network security monitoring configuration"""        return {
            "enabled": self.security_monitoring_enabled,
            "intrusion_detection": {
                "enabled": self.intrusion_detection_enabled,
                "signature_based": True,
                "anomaly_based": True,
                "machine_learning": True,
                "update_interval": "1h"
            },
            "ddos_protection": {
                "enabled": True,
                "rate_limits": {
                    "requests_per_ip_per_minute": 1000,
                    "requests_per_ip_per_hour": 10000,
                    "bandwidth_mbps": 100
                },
                "mitigation": {
                    "auto_block": self.auto_response_enabled,
                    "challenge_response": True,
                    "traffic_shaping": True
                }
            },
            "port_scanning_detection": {
                "enabled": True,
                "threshold_ports": 10,
                "time_window": "1m",
                "action": "block_ip"
            },
            "geo_blocking": {
                "enabled": True,
                "blocked_countries": [],  # Configure based on business needs
                "allowed_countries": [],
                "whitelist_override": True
            },
            "ip_reputation": {
                "enabled": self.threat_intelligence_enabled,
                "block_known_bad": True,
                "reputation_threshold": 0.7,
                "whitelist_internal": True
            }
        }
    
    def get_application_security_monitoring_config(self) -> Dict[str, Any]:
        """Get application security monitoring configuration"""        return {
            "enabled": self.security_monitoring_enabled,
            "web_application_firewall": {
                "enabled": True,
                "rule_sets": [
                    "OWASP_Core_Rule_Set",
                    "Custom_IA_Influencer_Rules"
                ],
                "paranoia_level": 2,
                "block_mode": self.auto_response_enabled
            },
            "injection_attacks": {
                "sql_injection": {
                    "enabled": True,
                    "detection_patterns": [
                        r"('|(\\')|(;)|(\\;)|(\\x27)|(\\x2D\\x2D))",
                        r"(union|select|insert|delete|drop|create|alter|exec)"
                    ],
                    "action": "block"
                },
                "xss_protection": {
                    "enabled": True,
                    "detection_patterns": [
                        r"<script[^>]*>.*?</script>",
                        r"javascript:",
                        r"on\w+\s*="
                    ],
                    "action": "sanitize"
                },
                "command_injection": {
                    "enabled": True,
                    "detection_patterns": [
                        r"(;|\||\&|\$\(|\`)",
                        r"(rm|wget|curl|nc|cat|etc/passwd)"
                    ],
                    "action": "block"
                }
            },
            "csrf_protection": {
                "enabled": True,
                "token_validation": True,
                "same_site_cookies": True,
                "referer_validation": True
            },
            "file_upload_security": {
                "enabled": True,
                "max_file_size_mb": 100,
                "allowed_extensions": [".jpg", ".png", ".mp3", ".wav", ".mp4"],
                "virus_scanning": True,
                "content_type_validation": True
            },
            "api_security": {
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 1000,
                    "burst_allowance": 100
                },
                "input_validation": {
                    "enabled": True,
                    "schema_validation": True,
                    "parameter_pollution": True
                },
                "output_filtering": {
                    "enabled": True,
                    "sensitive_data_masking": True,
                    "error_information_leakage": True
                }
            }
        }
    
    def get_data_security_monitoring_config(self) -> Dict[str, Any]:
        """Get data security monitoring configuration"""        return {
            "enabled": self.security_monitoring_enabled,
            "data_loss_prevention": {
                "enabled": True,
                "sensitive_data_patterns": [
                    r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",  # Credit cards
                    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email
                ],
                "action": "alert",
                "quarantine_suspicious": True
            },
            "database_monitoring": {
                "enabled": True,
                "query_monitoring": True,
                "privilege_escalation_detection": True,
                "unusual_access_patterns": True,
                "data_exfiltration_detection": {
                    "large_query_threshold": 10000,
                    "bulk_export_threshold": 1000,
                    "off_hours_access": True
                }
            },
            "file_integrity_monitoring": {
                "enabled": True,
                "critical_files": [
                    "/etc/passwd",
                    "/etc/shadow",
                    "/app/config/",
                    "/app/backend/security/"
                ],
                "check_interval": "1h",
                "hash_algorithm": "sha256"
            },
            "encryption_monitoring": {
                "enabled": True,
                "tls_version_compliance": True,
                "certificate_expiry_monitoring": True,
                "weak_cipher_detection": True
            }
        }
    
    def get_user_behavior_monitoring_config(self) -> Dict[str, Any]:
        """Get user behavior monitoring configuration"""        return {
            "enabled": self.security_monitoring_enabled,
            "behavioral_analytics": {
                "enabled": True,
                "learning_period_days": 30,
                "anomaly_threshold": self.suspicious_activity_threshold,
                "track_patterns": [
                    "login_times",
                    "access_locations",
                    "resource_usage",
                    "navigation_patterns"
                ]
            },
            "privilege_monitoring": {
                "enabled": True,
                "privilege_escalation_detection": True,
                "admin_activity_logging": True,
                "sensitive_operation_monitoring": True
            },
            "content_access_monitoring": {
                "enabled": True,
                "unusual_download_patterns": True,
                "bulk_access_detection": True,
                "unauthorized_sharing_detection": True
            },
            "insider_threat_detection": {
                "enabled": True,
                "data_access_anomalies": True,
                "working_hours_violations": True,
                "suspicious_file_operations": True
            }
        }
    
    def get_security_rules(self) -> List[SecurityRule]:
        """Get security monitoring rules"""        return [
            # Authentication rules
            SecurityRule(
                name="Failed Login Attempts",
                event_type=SecurityEventType.AUTHENTICATION,
                condition=f"failed_login_count > {self.max_failed_attempts}",
                threat_level=ThreatLevel.MEDIUM,
                response_action=ResponseAction.BLOCK,
                description="Multiple failed login attempts detected",
                threshold=self.max_failed_attempts,
                time_window="5m"
            ),
            SecurityRule(
                name="Suspicious Login Location",
                event_type=SecurityEventType.AUTHENTICATION,
                condition="login_location_anomaly_score > 0.8",
                threat_level=ThreatLevel.HIGH,
                response_action=ResponseAction.INVESTIGATE,
                description="Login from unusual location detected"
            ),
            
            # Network intrusion rules
            SecurityRule(
                name="Port Scanning Detected",
                event_type=SecurityEventType.NETWORK_INTRUSION,
                condition="unique_ports_accessed > 10",
                threat_level=ThreatLevel.HIGH,
                response_action=ResponseAction.BLOCK,
                description="Port scanning activity detected",
                threshold=10,
                time_window="1m"
            ),
            SecurityRule(
                name="DDoS Attack",
                event_type=SecurityEventType.DDoS,
                condition="requests_per_minute > 1000",
                threat_level=ThreatLevel.CRITICAL,
                response_action=ResponseAction.RATE_LIMIT,
                description="DDoS attack pattern detected",
                threshold=1000,
                time_window="1m"
            ),
            
            # Application security rules
            SecurityRule(
                name="SQL Injection Attempt",
                event_type=SecurityEventType.SQL_INJECTION,
                condition="sql_injection_pattern_detected",
                threat_level=ThreatLevel.HIGH,
                response_action=ResponseAction.BLOCK,
                description="SQL injection attempt detected"
            ),
            SecurityRule(
                name="XSS Attempt",
                event_type=SecurityEventType.XSS,
                condition="xss_pattern_detected",
                threat_level=ThreatLevel.MEDIUM,
                response_action=ResponseAction.BLOCK,
                description="Cross-site scripting attempt detected"
            ),
            
            # Data security rules
            SecurityRule(
                name="Unusual Data Access",
                event_type=SecurityEventType.DATA_ACCESS,
                condition="data_access_anomaly_score > 0.7",
                threat_level=ThreatLevel.HIGH,
                response_action=ResponseAction.INVESTIGATE,
                description="Unusual data access pattern detected"
            ),
            SecurityRule(
                name="Potential Data Breach",
                event_type=SecurityEventType.DATA_BREACH,
                condition="bulk_data_export > 1000",
                threat_level=ThreatLevel.CRITICAL,
                response_action=ResponseAction.ESCALATE,
                description="Potential data breach detected",
                threshold=1000
            ),
            
            # Suspicious activity rules
            SecurityRule(
                name="Privilege Escalation",
                event_type=SecurityEventType.PRIVILEGE_ESCALATION,
                condition="privilege_change_detected",
                threat_level=ThreatLevel.HIGH,
                response_action=ResponseAction.ALERT,
                description="Privilege escalation attempt detected"
            ),
            SecurityRule(
                name="Malware Detection",
                event_type=SecurityEventType.MALWARE,
                condition="malware_signature_detected",
                threat_level=ThreatLevel.CRITICAL,
                response_action=ResponseAction.QUARANTINE,
                description="Malware detected in uploaded content"
            )
        ]
    
    def get_threat_intelligence_config(self) -> ThreatIntelligence:
        """Get threat intelligence configuration"""        return ThreatIntelligence(
            enabled=self.threat_intelligence_enabled,
            feeds=[
                "https://rules.emergingthreats.net/open/suricata/rules/",
                "https://reputation.alienvault.com/reputation.data",
                "https://www.spamhaus.org/drop/drop.txt",
                "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
            ],
            update_interval="1h",
            reputation_threshold=0.7,
            auto_block=self.auto_response_enabled
        )
    
    def get_incident_response_config(self) -> Dict[str, Any]:
        """Get security incident response configuration"""        return {
            "enabled": True,
            "automated_response": {
                "enabled": self.auto_response_enabled,
                "response_levels": {
                    "low": ["alert"],
                    "medium": ["alert", "rate_limit"],
                    "high": ["alert", "block", "investigate"],
                    "critical": ["alert", "block", "quarantine", "escalate"]
                },
                "escalation_thresholds": {
                    "multiple_high_severity": 3,
                    "critical_severity": 1,
                    "time_window": "1h"
                }
            },
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "recipients": ["security@ia-influencer.com"],
                    "severity_filter": "medium"
                },
                "slack": {
                    "enabled": True,
                    "channel": "#security-alerts",
                    "severity_filter": "high"
                },
                "pagerduty": {
                    "enabled": True,
                    "service_key": os.getenv("PAGERDUTY_SECURITY_KEY"),
                    "severity_filter": "critical"
                }
            },
            "forensics": {
                "enabled": True,
                "data_retention_days": 365,
                "packet_capture": True,
                "log_preservation": True,
                "evidence_chain_custody": True
            },
            "recovery_procedures": {
                "automatic_backup_restore": False,
                "service_isolation": True,
                "user_notification": True,
                "compliance_reporting": True
            }
        }
    
    def get_compliance_monitoring_config(self) -> Dict[str, Any]:
        """Get compliance monitoring configuration"""        return {
            "enabled": True,
            "frameworks": {
                "gdpr": {
                    "enabled": True,
                    "data_processing_logging": True,
                    "consent_tracking": True,
                    "data_portability": True,
                    "right_to_erasure": True
                },
                "pci_dss": {
                    "enabled": True,
                    "cardholder_data_monitoring": True,
                    "network_segmentation_compliance": True,
                    "access_control_monitoring": True
                },
                "iso27001": {
                    "enabled": True,
                    "risk_assessment": True,
                    "security_controls_monitoring": True,
                    "continuous_improvement": True
                }
            },
            "audit_logging": {
                "enabled": True,
                "log_integrity": True,
                "immutable_storage": True,
                "regular_audits": True
            },
            "reporting": {
                "automated_reports": True,
                "compliance_dashboard": True,
                "violation_alerts": True,
                "remediation_tracking": True
            }
        }
    
    def get_security_metrics_config(self) -> Dict[str, Any]:
        """Get security metrics configuration"""        return {
            "key_metrics": {
                "security_incidents_count": {
                    "enabled": True,
                    "granularity": "severity",
                    "time_aggregation": "1h"
                },
                "threat_detection_rate": {
                    "enabled": True,
                    "calculate_precision_recall": True,
                    "baseline_comparison": True
                },
                "response_time": {
                    "enabled": True,
                    "measure_mttr": True,  # Mean Time To Response
                    "sla_target_minutes": 15
                },
                "false_positive_rate": {
                    "enabled": True,
                    "target_rate": 0.05,
                    "continuous_tuning": True
                },
                "compliance_score": {
                    "enabled": True,
                    "frameworks": ["gdpr", "pci_dss", "iso27001"],
                    "target_score": 95
                }
            },
            "dashboards": {
                "security_overview": {
                    "refresh_interval": "1m",
                    "widgets": [
                        "threat_level", "active_incidents", "blocked_attacks",
                        "compliance_status", "vulnerability_count"
                    ]
                },
                "incident_response": {
                    "refresh_interval": "30s",
                    "widgets": [
                        "open_incidents", "response_times", "escalation_status",
                        "automated_actions", "manual_interventions"
                    ]
                },
                "threat_intelligence": {
                    "refresh_interval": "5m",
                    "widgets": [
                        "threat_feeds_status", "ip_reputation", "malware_detections",
                        "attack_patterns", "geographic_threats"
                    ]
                }
            }
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete security monitoring configuration"""        return {
            "global": {
                "enabled": self.security_monitoring_enabled,
                "environment": self.environment,
                "log_level": self.security_log_level,
                "auto_response_enabled": self.auto_response_enabled
            },
            "authentication": self.get_authentication_monitoring_config(),
            "network_security": self.get_network_security_monitoring_config(),
            "application_security": self.get_application_security_monitoring_config(),
            "data_security": self.get_data_security_monitoring_config(),
            "user_behavior": self.get_user_behavior_monitoring_config(),
            "security_rules": [rule.__dict__ for rule in self.get_security_rules()],
            "threat_intelligence": self.get_threat_intelligence_config().__dict__,
            "incident_response": self.get_incident_response_config(),
            "compliance": self.get_compliance_monitoring_config(),
            "metrics": self.get_security_metrics_config()
        }
