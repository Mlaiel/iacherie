"""Ultra-Advanced Configuration for Audit Logs Module

Revolutionary comprehensive configuration system for the enterprise-grade audit logging
ecosystem of the IA Influencer Agent platform. Provides fine-grained control over
system auditing, user activity tracking, security event management, compliance monitoring,
AI-powered analytics, forensic capabilities, and business intelligence features.

Enterprise Features:
- Multi-tenant audit isolation
- Real-time threat detection configuration  
- Compliance framework integration
- AI model configuration for behavioral analysis
- Digital forensics evidence management
- Cross-platform audit synchronization

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Multi-Expert Lead AI Developer & Security Audit Specialist

⚠️ ULTRA-STRONG INTELLECTUAL PROPERTY WARNING ⚠️
This revolutionary audit configuration system is the EXCLUSIVE property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or exploitation is STRICTLY PROHIBITED.
Legal action will be taken against violators under international IP law.
Contact: mlaiel@live.de for authorization.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class LogLevel(Enum):
    """
Audit log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StorageBackend(Enum):
    """Storage backend options."""

    POSTGRESQL = "postgresql"
    ELASTICSEARCH = "elasticsearch"
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    HYBRID = "hybrid"


class RetentionPolicy(Enum):
    """Data retention policies."""

    STANDARD = "standard"  # 7 years
    EXTENDED = "extended"  # 10 years
    MINIMAL = "minimal"    # 3 years
    CUSTOM = "custom"      # User-defined


class ExportFormat(Enum):
    """Export format options."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    AVRO = "avro"


@dataclass
class DatabaseConfig:
    """Database configuration for audit logs."""
    primary_url: str = os.getenv("AUDIT_DB_URL", "postgresql://user:pass@localhost/audit_db")
    replica_urls: List[str] = field(default_factory=list)
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo_sql: bool = False
    isolation_level: str = "READ_COMMITTED"
    
    # Advanced settings
    enable_query_logging: bool = True
    slow_query_threshold_ms: int = 1000
    connection_retry_attempts: int = 3
    connection_retry_delay: int = 5


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration for search and analytics."""
    hosts: List[str] = field(default_factory=lambda: ["http://localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = True
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    
    # Index settings
    index_prefix: str = "audit_logs"
    number_of_shards: int = 3
    number_of_replicas: int = 1
    refresh_interval: str = "1s"
    
    # Performance settings
    bulk_size: int = 1000
    bulk_timeout: int = 30
    max_retries: int = 3
    timeout: int = 60


@dataclass
class RedisConfig:
    """Redis configuration for caching and real-time features."""
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    db: int = int(os.getenv("REDIS_DB", "0"))
    
    # Connection settings
    max_connections: int = 50
    connection_timeout: int = 10
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=lambda: {
        "TCP_KEEPIDLE": 1,
        "TCP_KEEPINTVL": 3,
        "TCP_KEEPCNT": 5
    })
    
    # Cache settings
    default_ttl: int = 3600  # 1 hour
    alert_cache_ttl: int = 300  # 5 minutes
    session_cache_ttl: int = 1800  # 30 minutes


@dataclass
class S3Config:
    """S3 configuration for evidence storage."""
    bucket_name: str = os.getenv("AUDIT_S3_BUCKET", "audit-evidence-storage")
    region: str = os.getenv("AWS_REGION", "eu-west-1")
    access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    endpoint_url: Optional[str] = os.getenv("S3_ENDPOINT_URL")
    
    # Storage settings
    storage_class: str = "STANDARD_IA"
    multipart_threshold: int = 100 * 1024 * 1024  # 100MB
    multipart_chunksize: int = 8 * 1024 * 1024   # 8MB
    max_concurrency: int = 10
    
    # Security settings
    server_side_encryption: str = "AES256"
    encryption_context: Dict[str, str] = field(default_factory=lambda: {
        "Purpose": "AuditEvidence",
        "Compliance": "GDPR-CCPA-PCI"
    })


@dataclass
class SecurityConfig:
    """Security configuration for audit logs."""
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    hash_algorithm: str = "SHA-256"
    
    # API Security
    api_rate_limit_per_minute: int = 1000
    api_burst_limit: int = 100
    api_key_length: int = 32
    session_timeout_minutes: int = 30
    
    # Data protection
    enable_field_encryption: bool = True
    encrypted_fields: List[str] = field(default_factory=lambda: [
        "user_email", "ip_address", "user_agent", "device_fingerprint"
    ])
    enable_data_masking: bool = True
    enable_anonymization: bool = True
    
    # Access control
    require_mfa_for_admin: bool = True
    admin_session_timeout_minutes: int = 15
    failed_login_lockout_attempts: int = 5
    failed_login_lockout_duration_minutes: int = 30


@dataclass
class ComplianceConfig:
    """Compliance configuration for audit logs."""
    enabled_frameworks: List[str] = field(default_factory=lambda: [
        "GDPR", "CCPA", "PCI_DSS", "HIPAA", "SOX", "ISO_27001", "NIST"
    ])
    
    # Data retention policies
    gdpr_retention_years: int = 7
    ccpa_retention_years: int = 7
    pci_retention_years: int = 5
    hipaa_retention_years: int = 6
    sox_retention_years: int = 7
    
    # Notification settings
    breach_notification_email: str = os.getenv("COMPLIANCE_EMAIL", "compliance@platform.com")
    breach_notification_threshold_hours: int = 72
    regulatory_notification_threshold_hours: int = 24
    
    # Data subject rights
    enable_right_to_be_forgotten: bool = True
    enable_data_portability: bool = True
    enable_data_rectification: bool = True
    data_subject_request_deadline_days: int = 30
    
    # Automated compliance
    auto_anonymize_after_retention: bool = True
    auto_delete_after_extended_retention: bool = False
    compliance_audit_frequency_days: int = 30


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration."""
    enable_real_time_monitoring: bool = True
    enable_anomaly_detection: bool = True
    enable_threat_intelligence: bool = True
    
    # Performance monitoring
    performance_alert_threshold_ms: int = 5000
    memory_usage_alert_threshold_percent: int = 85
    disk_usage_alert_threshold_percent: int = 80
    error_rate_alert_threshold_percent: int = 5
    
    # Security monitoring
    failed_login_alert_threshold: int = 10
    suspicious_activity_alert_threshold: int = 50
    ddos_alert_threshold_rps: int = 1000
    brute_force_alert_threshold: int = 5
    
    # Notification channels
    email_notifications: List[str] = field(default_factory=lambda: [
        "security@platform.com", "admin@platform.com"
    ])
    slack_webhook_url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    teams_webhook_url: Optional[str] = os.getenv("TEAMS_WEBHOOK_URL")
    
    # Alert escalation
    escalation_after_minutes: int = 30
    escalation_contacts: List[str] = field(default_factory=lambda: [
        "ciso@platform.com", "ceo@platform.com"
    ])


@dataclass
class ForensicsConfig:
    """Forensics and investigation configuration."""
    enable_forensic_mode: bool = True
    evidence_collection_enabled: bool = True
    chain_of_custody_enabled: bool = True
    
    # Evidence storage
    evidence_storage_backend: str = "s3"
    evidence_encryption_enabled: bool = True
    evidence_compression_enabled: bool = True
    evidence_retention_years: int = 10
    
    # Investigation settings
    max_concurrent_investigations: int = 10
    auto_evidence_collection: bool = True
    evidence_validation_required: bool = True
    legal_hold_enabled: bool = True
    
    # Reporting
    forensic_report_formats: List[str] = field(default_factory=lambda: [
        "PDF", "JSON", "XML"
    ])
    include_technical_details: bool = True
    include_timeline_analysis: bool = True
    include_risk_assessment: bool = True


@dataclass
class ExportConfig:
    """Data export and backup configuration."""
    enabled_formats: List[ExportFormat] = field(default_factory=lambda: [
        ExportFormat.JSON, ExportFormat.CSV, ExportFormat.PARQUET
    ])
    
    # Export settings
    max_export_records: int = 1000000
    export_batch_size: int = 10000
    export_timeout_minutes: int = 60
    export_compression_enabled: bool = True
    
    # Backup settings
    auto_backup_enabled: bool = True
    backup_frequency_hours: int = 24
    backup_retention_days: int = 30
    backup_encryption_enabled: bool = True
    
    # Storage locations
    export_storage_path: str = "/tmp/audit_exports"
    backup_storage_path: str = "/backup/audit_logs"
    s3_export_bucket: Optional[str] = os.getenv("AUDIT_EXPORT_S3_BUCKET")


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    # Database optimization
    enable_query_caching: bool = True
    query_cache_ttl_seconds: int = 300
    enable_connection_pooling: bool = True
    enable_read_replicas: bool = True
    
    # Indexing
    auto_create_indexes: bool = True
    index_maintenance_enabled: bool = True
    index_optimization_frequency_hours: int = 24
    
    # Caching
    enable_redis_caching: bool = True
    cache_frequently_accessed_data: bool = True
    cache_user_sessions: bool = True
    cache_system_metrics: bool = True
    
    # Async processing
    enable_async_logging: bool = True
    async_worker_count: int = 4
    async_queue_size: int = 10000
    async_batch_size: int = 100
    
    # Data compression
    enable_data_compression: bool = True
    compression_algorithm: str = "gzip"
    compression_level: int = 6


@dataclass
class AuditLogsConfig:
    """Main configuration class for audit logs module."""
    
    # Core settings
    service_name: str = "ia_influencer_agent"
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug_mode: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: LogLevel = LogLevel.INFO
    
    # Storage configuration
    storage_backend: StorageBackend = StorageBackend.HYBRID
    retention_policy: RetentionPolicy = RetentionPolicy.STANDARD
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    s3: S3Config = field(default_factory=S3Config)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    forensics: ForensicsConfig = field(default_factory=ForensicsConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Feature flags
    enable_user_activity_logging: bool = True
    enable_system_event_logging: bool = True
    enable_security_event_logging: bool = True
    enable_compliance_tracking: bool = True
    enable_forensic_analysis: bool = True
    enable_real_time_analytics: bool = True
    enable_automated_response: bool = True
    
    def validate(self) -> List[str]:
        """
        Validate the configuration and return any errors.
        
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        # Validate database URL
        if not self.database.primary_url:
            errors.append("Database primary URL is required")
        
        # Validate storage backend compatibility
        if self.storage_backend == StorageBackend.HYBRID:
            if not self.elasticsearch.hosts:
                errors.append("Elasticsearch hosts required for hybrid storage")
        
        # Validate compliance requirements
        if self.compliance.enable_right_to_be_forgotten and not self.enable_user_activity_logging:
            errors.append("User activity logging required for right to be forgotten")
        
        # Validate forensics requirements
        if self.forensics.enable_forensic_mode and not self.forensics.evidence_storage_backend:
            errors.append("Evidence storage backend required for forensic mode")
        
        # Validate monitoring settings
        if self.monitoring.enable_real_time_monitoring and not self.redis.host:
            errors.append("Redis required for real-time monitoring")
        
        return errors
    
    @classmethod
    def from_env(cls) -> 'AuditLogsConfig':
        """
        Create configuration from environment variables.
        
        Returns:
            AuditLogsConfig: Configuration instance
        """
        return cls(
            service_name=os.getenv("AUDIT_SERVICE_NAME", "ia_influencer_agent"),
            environment=os.getenv("ENVIRONMENT", "production"),
            debug_mode=os.getenv("DEBUG", "false").lower() == "true",
            log_level=LogLevel(os.getenv("LOG_LEVEL", "info")),
            storage_backend=StorageBackend(os.getenv("STORAGE_BACKEND", "hybrid")),
            retention_policy=RetentionPolicy(os.getenv("RETENTION_POLICY", "standard"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            "service_name": self.service_name,
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level.value,
            "storage_backend": self.storage_backend.value,
            "retention_policy": self.retention_policy.value,
            "database": {
                "primary_url": self.database.primary_url,
                "connection_pool_size": self.database.connection_pool_size,
                "echo_sql": self.database.echo_sql
            },
            "elasticsearch": {
                "hosts": self.elasticsearch.hosts,
                "index_prefix": self.elasticsearch.index_prefix,
                "bulk_size": self.elasticsearch.bulk_size
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db
            },
            "security": {
                "encryption_algorithm": self.security.encryption_algorithm,
                "enable_field_encryption": self.security.enable_field_encryption,
                "enable_data_masking": self.security.enable_data_masking
            },
            "compliance": {
                "enabled_frameworks": self.compliance.enabled_frameworks,
                "gdpr_retention_years": self.compliance.gdpr_retention_years,
                "enable_right_to_be_forgotten": self.compliance.enable_right_to_be_forgotten
            },
            "monitoring": {
                "enable_real_time_monitoring": self.monitoring.enable_real_time_monitoring,
                "enable_anomaly_detection": self.monitoring.enable_anomaly_detection,
                "email_notifications": self.monitoring.email_notifications
            },
            "forensics": {
                "enable_forensic_mode": self.forensics.enable_forensic_mode,
                "evidence_collection_enabled": self.forensics.evidence_collection_enabled,
                "evidence_retention_years": self.forensics.evidence_retention_years
            }
        }


# Default configuration instance
default_config = AuditLogsConfig()

# Environment-specific configurations
def get_development_config() -> AuditLogsConfig:
    """Get development environment configuration."""
    config = AuditLogsConfig()
    config.environment = "development"
    config.debug_mode = True
    config.log_level = LogLevel.DEBUG
    config.database.echo_sql = True
    config.security.require_mfa_for_admin = False
    config.performance.enable_query_caching = False
    return config


def get_testing_config() -> AuditLogsConfig:
    """Get testing environment configuration."""
    config = AuditLogsConfig()
    config.environment = "testing"
    config.debug_mode = True
    config.log_level = LogLevel.INFO
    config.database.primary_url = "sqlite:///test_audit.db"
    config.redis.db = 15  # Use separate Redis DB for tests
    config.compliance.auto_delete_after_extended_retention = True
    return config


def get_production_config() -> AuditLogsConfig:
    """Get production environment configuration."""
    config = AuditLogsConfig()
    config.environment = "production"
    config.debug_mode = False
    config.log_level = LogLevel.WARNING
    config.security.require_mfa_for_admin = True
    config.compliance.auto_anonymize_after_retention = True
    config.monitoring.enable_real_time_monitoring = True
    config.forensics.enable_forensic_mode = True
    return config


# Configuration factory
def create_config(environment: str = None) -> AuditLogsConfig:
    """
    Create configuration based on environment.
    
    Args:
        environment: Environment name (development, testing, production)
        
    Returns:
        AuditLogsConfig: Environment-specific configuration
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "production")
    
    if environment.lower() == "development":
        return get_development_config()
    elif environment.lower() == "testing":
        return get_testing_config()
    elif environment.lower() == "production":
        return get_production_config()
    else:
        return AuditLogsConfig.from_env()
