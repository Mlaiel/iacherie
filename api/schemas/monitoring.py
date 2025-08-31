"""Monitoring & Surveillance Schemas for IA Influencer Agent Platform
Advanced monitoring, content surveillance, and system observability schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class MonitoringConfiguration(UUIDSchema, TimestampSchema):
    """Content monitoring configuration schema."""    
    creator_id: UUID
    monitoring_name: str = Field(description="Monitoring configuration name")
    monitoring_type: str = Field(description="Type of monitoring")
    
    # Monitoring scope
    content_ids_to_monitor: List[UUID] = Field(default_factory=list)
    platforms_to_monitor: List[str] = Field(description="Platforms to monitor")
    keywords_to_monitor: List[str] = Field(default_factory=list)
    hashtags_to_monitor: List[str] = Field(default_factory=list)
    
    # Monitoring parameters
    monitoring_frequency: str = Field(description="Monitoring frequency")
    monitoring_depth: str = Field(description="Depth of monitoring")
    geographic_scope: List[str] = Field(default_factory=list)
    language_filters: List[str] = Field(default_factory=list)
    
    # Detection settings
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    copyright_detection_enabled: bool = Field(default=True)
    trademark_detection_enabled: bool = Field(default=True)
    brand_mention_detection: bool = Field(default=True)
    sentiment_monitoring: bool = Field(default=False)
    
    # Alert configuration
    real_time_alerts: bool = Field(default=True)
    alert_channels: List[str] = Field(default_factory=list)
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    escalation_rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Advanced detection
    ai_fingerprinting_enabled: bool = Field(default=True)
    blockchain_verification: bool = Field(default=False)
    metadata_analysis: bool = Field(default=True)
    behavioral_analysis: bool = Field(default=False)
    
    # Filtering and exclusions
    whitelist_sources: List[str] = Field(default_factory=list)
    blacklist_sources: List[str] = Field(default_factory=list)
    false_positive_filters: List[str] = Field(default_factory=list)
    
    # Monitoring status
    is_active: bool = Field(default=True)
    last_monitoring_run: Optional[datetime] = None
    next_scheduled_run: Optional[datetime] = None
    
    @validator('monitoring_type')
    def validate_monitoring_type(cls, v):
        """Validate monitoring type."""        allowed_types = {
            "copyright_protection", "trademark_monitoring", "brand_surveillance",
            "content_piracy", "unauthorized_usage", "reputation_monitoring",
            "competitive_intelligence", "trend_tracking", "sentiment_analysis"
        }
        if v not in allowed_types:
            raise ValueError(f'Monitoring type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('monitoring_frequency')
    def validate_monitoring_frequency(cls, v):
        """Validate monitoring frequency."""        allowed_frequencies = {
            "real_time", "every_hour", "every_6_hours", "daily", 
            "weekly", "monthly", "custom"
        }
        if v not in allowed_frequencies:
            raise ValueError(f'Monitoring frequency must be one of: {", ".join(allowed_frequencies)}')
        return v


class ContentViolation(UUIDSchema, TimestampSchema, AuditSchema):
    """Content violation detection result schema."""    
    monitoring_config_id: UUID
    original_content_id: UUID
    violation_type: str = Field(description="Type of violation detected")
    severity_level: str = Field(description="Severity of the violation")
    
    # Violation details
    violating_url: HttpUrl = Field(description="URL where violation was found")
    violating_platform: str = Field(description="Platform hosting the violation")
    violating_account: Optional[str] = Field(None, description="Account responsible for violation")
    violating_account_id: Optional[str] = None
    
    # Detection metrics
    similarity_score: float = Field(ge=0.0, le=1.0, description="Content similarity score")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    detection_method: str = Field(description="Method used for detection")
    detection_timestamp: datetime = Field(description="When violation was detected")
    
    # Content analysis
    violating_content_metadata: Dict[str, Any] = Field(default_factory=dict)
    content_modifications: List[str] = Field(default_factory=list)
    usage_context: str = Field(description="Context of content usage")
    commercial_usage: bool = Field(default=False)
    
    # Impact assessment
    potential_revenue_loss: Optional[Decimal] = Field(None, ge=0)
    brand_reputation_risk: str = Field(description="Brand reputation risk level")
    legal_risk_assessment: str = Field(description="Legal risk level")
    urgency_score: float = Field(ge=0.0, le=1.0)
    
    # Violation evidence
    evidence_screenshots: List[HttpUrl] = Field(default_factory=list)
    evidence_metadata: Dict[str, Any] = Field(default_factory=dict)
    evidence_hash: Optional[str] = None
    evidence_timestamp: datetime = Field(description="When evidence was collected")
    
    # Response status
    violation_status: str = Field(default="detected")
    response_actions_taken: List[str] = Field(default_factory=list)
    takedown_requests_sent: List[Dict[str, Any]] = Field(default_factory=list)
    legal_notices_sent: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Resolution tracking
    resolution_status: Optional[str] = None
    resolution_date: Optional[datetime] = None
    resolution_method: Optional[str] = None
    compensation_received: Optional[Decimal] = None
    
    # Follow-up monitoring
    follow_up_required: bool = Field(default=True)
    follow_up_date: Optional[datetime] = None
    recurrence_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    
    @validator('violation_type')
    def validate_violation_type(cls, v):
        """Validate violation type."""        allowed_types = {
            "copyright_infringement", "trademark_violation", "unauthorized_usage",
            "content_piracy", "brand_impersonation", "plagiarism",
            "fair_use_violation", "license_breach", "attribution_missing"
        }
        if v not in allowed_types:
            raise ValueError(f'Violation type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('severity_level')
    def validate_severity_level(cls, v):
        """Validate severity level."""        allowed_levels = {"low", "medium", "high", "critical", "urgent"}
        if v not in allowed_levels:
            raise ValueError(f'Severity level must be one of: {", ".join(allowed_levels)}')
        return v


class SurveillanceReport(UUIDSchema, TimestampSchema):
    """Comprehensive surveillance and monitoring report schema."""    
    creator_id: UUID
    report_period_start: datetime
    report_period_end: datetime
    monitoring_scope: List[str] = Field(description="Scope of monitoring activities")
    
    # Monitoring summary
    total_scans_performed: int = Field(default=0, ge=0)
    total_violations_detected: int = Field(default=0, ge=0)
    total_false_positives: int = Field(default=0, ge=0)
    detection_accuracy_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Violation breakdown
    violations_by_type: Dict[str, int] = Field(default_factory=dict)
    violations_by_platform: Dict[str, int] = Field(default_factory=dict)
    violations_by_severity: Dict[str, int] = Field(default_factory=dict)
    violation_trends: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Platform analysis
    platform_risk_assessment: Dict[str, str] = Field(default_factory=dict)
    most_problematic_platforms: List[str] = Field(default_factory=list)
    platform_cooperation_levels: Dict[str, str] = Field(default_factory=dict)
    new_platforms_discovered: List[str] = Field(default_factory=list)
    
    # Content protection effectiveness
    protection_success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_takedown_time: float = Field(default=0.0, ge=0.0)
    successful_takedowns: int = Field(default=0, ge=0)
    disputed_takedowns: int = Field(default=0, ge=0)
    
    # Financial impact
    estimated_revenue_protected: Decimal = Field(default=Decimal('0.00'), ge=0)
    potential_losses_prevented: Decimal = Field(default=Decimal('0.00'), ge=0)
    monitoring_cost_effectiveness: float = Field(default=0.0)
    roi_of_monitoring: float = Field(default=0.0)
    
    # Threat analysis
    emerging_threats: List[str] = Field(default_factory=list)
    repeat_offenders: List[Dict[str, Any]] = Field(default_factory=list)
    threat_evolution_patterns: List[str] = Field(default_factory=list)
    geographic_threat_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Response effectiveness
    response_time_metrics: Dict[str, float] = Field(default_factory=dict)
    action_success_rates: Dict[str, float] = Field(default_factory=dict)
    escalation_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Technology performance
    ai_detection_accuracy: float = Field(default=0.0, ge=0.0, le=100.0)
    fingerprinting_effectiveness: float = Field(default=0.0, ge=0.0, le=100.0)
    false_positive_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    system_performance_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Strategic insights
    protection_strategy_effectiveness: Dict[str, float] = Field(default_factory=dict)
    recommended_strategy_adjustments: List[str] = Field(default_factory=list)
    investment_priority_recommendations: List[str] = Field(default_factory=list)
    
    # Future outlook
    threat_predictions: List[str] = Field(default_factory=list)
    monitoring_expansion_recommendations: List[str] = Field(default_factory=list)
    technology_upgrade_suggestions: List[str] = Field(default_factory=list)


class SystemMonitoring(UUIDSchema, TimestampSchema):
    """System performance and health monitoring schema."""    
    system_component: str = Field(description="System component being monitored")
    monitoring_type: str = Field(description="Type of system monitoring")
    
    # Performance metrics
    cpu_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    disk_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    network_throughput: float = Field(default=0.0, ge=0.0)
    
    # Application metrics
    response_time: float = Field(default=0.0, ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    throughput: int = Field(default=0, ge=0)
    active_connections: int = Field(default=0, ge=0)
    
    # Database metrics
    database_connections: Optional[int] = None
    query_performance: Optional[Dict[str, float]] = None
    database_size: Optional[float] = None
    slow_queries: Optional[List[str]] = None
    
    # AI processing metrics
    ai_model_latency: Optional[float] = None
    ai_processing_queue_size: Optional[int] = None
    gpu_utilization: Optional[float] = None
    model_accuracy_metrics: Optional[Dict[str, float]] = None
    
    # Security metrics
    failed_login_attempts: int = Field(default=0, ge=0)
    security_alerts: List[str] = Field(default_factory=list)
    suspicious_activities: List[Dict[str, Any]] = Field(default_factory=list)
    vulnerability_scan_results: Optional[Dict[str, Any]] = None
    
    # Monitoring alerts
    critical_alerts: List[str] = Field(default_factory=list)
    warning_alerts: List[str] = Field(default_factory=list)
    performance_degradations: List[str] = Field(default_factory=list)
    
    # System health indicators
    overall_health_score: float = Field(default=100.0, ge=0.0, le=100.0)
    availability_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    reliability_score: float = Field(default=100.0, ge=0.0, le=100.0)
    
    # Predictive indicators
    capacity_projections: Dict[str, float] = Field(default_factory=dict)
    performance_trends: List[float] = Field(default_factory=list)
    maintenance_recommendations: List[str] = Field(default_factory=list)
    
    @validator('monitoring_type')
    def validate_monitoring_type(cls, v):
        """Validate monitoring type."""        allowed_types = {
            "performance", "security", "availability", "capacity",
            "application", "database", "network", "ai_processing"
        }
        if v not in allowed_types:
            raise ValueError(f'Monitoring type must be one of: {", ".join(allowed_types)}')
        return v


class TrendAnalysis(UUIDSchema, TimestampSchema):
    """Advanced trend analysis and prediction schema."""    
    analysis_scope: str = Field(description="Scope of trend analysis")
    analysis_period: str = Field(description="Time period for analysis")
    data_sources: List[str] = Field(description="Data sources used for analysis")
    
    # Content trends
    trending_content_types: List[Dict[str, Any]] = Field(default_factory=list)
    emerging_content_formats: List[str] = Field(default_factory=list)
    declining_content_trends: List[str] = Field(default_factory=list)
    content_lifecycle_patterns: Dict[str, List[float]] = Field(default_factory=dict)
    
    # Audience behavior trends
    engagement_pattern_changes: Dict[str, Any] = Field(default_factory=dict)
    platform_usage_trends: Dict[str, List[float]] = Field(default_factory=dict)
    demographic_shift_indicators: Dict[str, float] = Field(default_factory=dict)
    consumption_behavior_evolution: List[str] = Field(default_factory=list)
    
    # Technology trends
    emerging_technologies: List[str] = Field(default_factory=list)
    ai_adoption_trends: Dict[str, float] = Field(default_factory=dict)
    platform_feature_evolution: Dict[str, List[str]] = Field(default_factory=dict)
    technical_innovation_impact: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Market trends
    industry_growth_indicators: Dict[str, float] = Field(default_factory=dict)
    competitive_landscape_changes: List[str] = Field(default_factory=list)
    monetization_trend_evolution: Dict[str, Any] = Field(default_factory=dict)
    regulatory_trend_impact: List[str] = Field(default_factory=list)
    
    # Predictive analysis
    short_term_predictions: Dict[str, Any] = Field(default_factory=dict)
    long_term_forecasts: Dict[str, Any] = Field(default_factory=dict)
    trend_confidence_scores: Dict[str, float] = Field(default_factory=dict)
    prediction_accuracy_history: Dict[str, float] = Field(default_factory=dict)
    
    # Risk and opportunity identification
    emerging_risks: List[Dict[str, str]] = Field(default_factory=list)
    market_opportunities: List[Dict[str, str]] = Field(default_factory=list)
    disruption_indicators: List[str] = Field(default_factory=list)
    adaptation_requirements: List[str] = Field(default_factory=list)
    
    # Strategic implications
    business_strategy_impacts: List[str] = Field(default_factory=list)
    content_strategy_recommendations: List[str] = Field(default_factory=list)
    investment_priority_adjustments: List[str] = Field(default_factory=list)
    competitive_positioning_advice: List[str] = Field(default_factory=list)
    
    # Trend validation
    trend_verification_sources: List[str] = Field(default_factory=list)
    cross_validation_results: Dict[str, bool] = Field(default_factory=dict)
    expert_opinion_alignment: Dict[str, float] = Field(default_factory=dict)
    
    @validator('analysis_scope')
    def validate_analysis_scope(cls, v):
        """Validate analysis scope."""        allowed_scopes = {
            "content_trends", "audience_behavior", "technology_trends",
            "market_analysis", "competitive_intelligence", "platform_evolution",
            "monetization_trends", "regulatory_changes", "global_trends"
        }
        if v not in allowed_scopes:
            raise ValueError(f'Analysis scope must be one of: {", ".join(allowed_scopes)}')
        return v


class AlertConfiguration(UUIDSchema, TimestampSchema):
    """Advanced alert and notification configuration schema."""    
    creator_id: UUID
    alert_name: str = Field(description="Alert configuration name")
    alert_type: str = Field(description="Type of alert")
    priority_level: str = Field(description="Alert priority level")
    
    # Alert triggers
    trigger_conditions: List[Dict[str, Any]] = Field(default_factory=list)
    threshold_values: Dict[str, float] = Field(default_factory=dict)
    composite_conditions: Optional[str] = None
    time_window_requirements: Optional[str] = None
    
    # Notification channels
    email_notifications: bool = Field(default=True)
    sms_notifications: bool = Field(default=False)
    push_notifications: bool = Field(default=True)
    webhook_notifications: List[HttpUrl] = Field(default_factory=list)
    dashboard_alerts: bool = Field(default=True)
    
    # Notification customization
    notification_templates: Dict[str, str] = Field(default_factory=dict)
    personalization_rules: List[str] = Field(default_factory=list)
    localization_settings: Dict[str, str] = Field(default_factory=dict)
    
    # Escalation rules
    escalation_enabled: bool = Field(default=False)
    escalation_levels: List[Dict[str, Any]] = Field(default_factory=list)
    escalation_timeouts: Dict[str, int] = Field(default_factory=dict)
    escalation_recipients: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Frequency controls
    rate_limiting: bool = Field(default=True)
    max_alerts_per_hour: int = Field(default=10, ge=1)
    cooldown_period: int = Field(default=300, ge=0)
    duplicate_suppression: bool = Field(default=True)
    
    # Advanced features
    intelligent_grouping: bool = Field(default=True)
    contextual_information: bool = Field(default=True)
    predictive_alerting: bool = Field(default=False)
    ml_anomaly_detection: bool = Field(default=False)
    
    # Alert effectiveness
    acknowledgment_required: bool = Field(default=False)
    response_tracking: bool = Field(default=True)
    effectiveness_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Status and control
    is_active: bool = Field(default=True)
    last_triggered: Optional[datetime] = None
    trigger_count: int = Field(default=0, ge=0)
    false_positive_count: int = Field(default=0, ge=0)
    
    @validator('alert_type')
    def validate_alert_type(cls, v):
        """Validate alert type."""        allowed_types = {
            "content_violation", "system_performance", "security_threat",
            "revenue_threshold", "engagement_anomaly", "competitive_intelligence",
            "trend_deviation", "capacity_warning", "error_spike", "custom"
        }
        if v not in allowed_types:
            raise ValueError(f'Alert type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('priority_level')
    def validate_priority_level(cls, v):
        """Validate priority level."""        allowed_levels = {"low", "medium", "high", "critical", "emergency"}
        if v not in allowed_levels:
            raise ValueError(f'Priority level must be one of: {", ".join(allowed_levels)}')
        return v


class CrawlerConfiguration(UUIDSchema, TimestampSchema):
    """Web crawler and data collection configuration schema."""    
    crawler_name: str = Field(description="Crawler configuration name")
    crawler_type: str = Field(description="Type of web crawler")
    target_scope: str = Field(description="Crawling target scope")
    
    # Crawling targets
    target_websites: List[HttpUrl] = Field(default_factory=list)
    target_social_platforms: List[str] = Field(default_factory=list)
    search_engines_to_query: List[str] = Field(default_factory=list)
    api_endpoints: List[HttpUrl] = Field(default_factory=list)
    
    # Crawling parameters
    crawl_frequency: str = Field(description="How often to crawl")
    crawl_depth: int = Field(default=3, ge=1, le=10)
    max_pages_per_session: int = Field(default=1000, ge=1)
    concurrent_requests: int = Field(default=5, ge=1, le=50)
    request_delay: float = Field(default=1.0, ge=0.1)
    
    # Content filtering
    content_type_filters: List[str] = Field(default_factory=list)
    language_filters: List[str] = Field(default_factory=list)
    date_range_filters: Optional[Dict[str, datetime]] = None
    size_filters: Optional[Dict[str, int]] = None
    
    # Data extraction
    extraction_rules: List[Dict[str, str]] = Field(default_factory=list)
    metadata_extraction: bool = Field(default=True)
    image_extraction: bool = Field(default=True)
    video_extraction: bool = Field(default=False)
    
    # Ethical crawling
    robots_txt_compliance: bool = Field(default=True)
    rate_limit_compliance: bool = Field(default=True)
    user_agent_rotation: bool = Field(default=True)
    proxy_rotation: bool = Field(default=False)
    
    # Storage and processing
    data_storage_format: str = Field(default="json")
    compression_enabled: bool = Field(default=True)
    duplicate_detection: bool = Field(default=True)
    content_hashing: bool = Field(default=True)
    
    # Monitoring and alerts
    success_rate_threshold: float = Field(default=95.0, ge=0.0, le=100.0)
    error_rate_threshold: float = Field(default=5.0, ge=0.0, le=100.0)
    performance_monitoring: bool = Field(default=True)
    
    # Status tracking
    is_active: bool = Field(default=True)
    last_crawl_timestamp: Optional[datetime] = None
    next_scheduled_crawl: Optional[datetime] = None
    crawl_statistics: Dict[str, int] = Field(default_factory=dict)
    
    @validator('crawler_type')
    def validate_crawler_type(cls, v):
        """Validate crawler type."""        allowed_types = {
            "content_discovery", "copyright_monitoring", "competitive_intelligence",
            "trend_analysis", "brand_monitoring", "market_research",
            "social_listening", "news_tracking", "academic_research"
        }
        if v not in allowed_types:
            raise ValueError(f'Crawler type must be one of: {", ".join(allowed_types)}')
        return v
