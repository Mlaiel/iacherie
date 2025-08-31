"""
Performance Monitoring Schemas

Comprehensive Pydantic schemas for performance monitoring, system metrics,
and performance analytics in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.

 COPYRIGHT WARNING 
ALL RIGHTS RESERVED - This code, concept, and implementation are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Unauthorized use, copying, 
modification, or distribution is strictly prohibited and will result in immediate 
legal action under German and international copyright law.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt, PositiveFloat


class MetricTypeEnum(str, Enum):
    """Types of performance metrics"""
    SYSTEM_CPU = "system_cpu"
    SYSTEM_MEMORY = "system_memory"
    SYSTEM_DISK = "system_disk"
    SYSTEM_NETWORK = "system_network"
    DATABASE_PERFORMANCE = "database_performance"
    API_RESPONSE_TIME = "api_response_time"
    API_THROUGHPUT = "api_throughput"
    API_ERROR_RATE = "api_error_rate"
    FINGERPRINT_PROCESSING_TIME = "fingerprint_processing_time"
    DETECTION_ACCURACY = "detection_accuracy"
    STORAGE_UTILIZATION = "storage_utilization"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUEUE_LENGTH = "queue_length"
    USER_SESSION_DURATION = "user_session_duration"
    CONTENT_UPLOAD_TIME = "content_upload_time"
    ALERT_RESPONSE_TIME = "alert_response_time"
    REVENUE_PROCESSING_TIME = "revenue_processing_time"
    COLLABORATION_MATCH_TIME = "collaboration_match_time"
    ML_MODEL_INFERENCE_TIME = "ml_model_inference_time"
    SEARCH_QUERY_TIME = "search_query_time"


class AlertThresholdTypeEnum(str, Enum):
    """Types of alert thresholds"""
    ABSOLUTE_VALUE = "absolute_value"
    PERCENTAGE_CHANGE = "percentage_change"
    STANDARD_DEVIATION = "standard_deviation"
    MOVING_AVERAGE = "moving_average"
    RATE_OF_CHANGE = "rate_of_change"
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY_DETECTION = "anomaly_detection"


class PerformanceStatusEnum(str, Enum):
    """Performance status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ServiceComponentEnum(str, Enum):
    """System service components"""
    API_GATEWAY = "api_gateway"
    USER_SERVICE = "user_service"
    CONTENT_SERVICE = "content_service"
    PROTECTION_SERVICE = "protection_service"
    MONETIZATION_SERVICE = "monetization_service"
    COLLABORATION_SERVICE = "collaboration_service"
    FINGERPRINT_ENGINE = "fingerprint_engine"
    ML_INFERENCE_ENGINE = "ml_inference_engine"
    NOTIFICATION_SERVICE = "notification_service"
    PAYMENT_PROCESSOR = "payment_processor"
    SEARCH_ENGINE = "search_engine"
    ANALYTICS_ENGINE = "analytics_engine"
    DATABASE_CLUSTER = "database_cluster"
    CACHE_CLUSTER = "cache_cluster"
    MESSAGE_QUEUE = "message_queue"
    FILE_STORAGE = "file_storage"
    CDN = "cdn"
    LOAD_BALANCER = "load_balancer"
    MONITORING_SYSTEM = "monitoring_system"


class MetricAggregationEnum(str, Enum):
    """Metric aggregation methods"""
    AVERAGE = "average"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_50 = "percentile_50"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"
    STANDARD_DEVIATION = "standard_deviation"
    RATE = "rate"
    DELTA = "delta"


class PerformanceMetricSchema(BaseModel):
    """Schema for individual performance metrics"""
    metric_id: str = Field(..., description="Unique metric identifier")
    metric_type: MetricTypeEnum = Field(..., description="Type of metric")
    component: ServiceComponentEnum = Field(..., description="System component being measured")
    
    # Metric data
    timestamp: datetime = Field(..., description="Metric timestamp")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    
    # Context and metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags for categorization")
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Additional metric dimensions")
    instance_id: Optional[str] = Field(None, description="Instance identifier")
    region: Optional[str] = Field(None, description="Geographic region")
    
    # Quality indicators
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Metric confidence score")
    data_quality: str = Field("high", description="Data quality assessment")
    collection_method: str = Field(..., description="Method used to collect metric")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_id": "cpu_usage_web01_20240824_103000",
                "metric_type": "system_cpu",
                "component": "api_gateway",
                "timestamp": "2024-08-24T10:30:00Z",
                "value": 45.7,
                "unit": "percentage",
                "tags": {"environment": "production", "datacenter": "eu-west-1"}
            }
        }


class PerformanceAggregateSchema(BaseModel):
    """Schema for aggregated performance metrics"""
    aggregate_id: str = Field(..., description="Unique aggregate identifier")
    metric_type: MetricTypeEnum = Field(..., description="Type of metric")
    component: ServiceComponentEnum = Field(..., description="System component")
    
    # Time window
    period_start: datetime = Field(..., description="Start of aggregation period")
    period_end: datetime = Field(..., description="End of aggregation period")
    aggregation_method: MetricAggregationEnum = Field(..., description="Aggregation method used")
    
    # Aggregated values
    value: float = Field(..., description="Aggregated metric value")
    min_value: float = Field(..., description="Minimum value in period")
    max_value: float = Field(..., description="Maximum value in period")
    average_value: float = Field(..., description="Average value in period")
    sample_count: PositiveInt = Field(..., description="Number of samples in aggregate")
    
    # Statistical measures
    percentile_50: Optional[float] = Field(None, description="50th percentile value")
    percentile_95: Optional[float] = Field(None, description="95th percentile value")
    percentile_99: Optional[float] = Field(None, description="99th percentile value")
    standard_deviation: Optional[float] = Field(None, description="Standard deviation")
    
    # Context
    tags: Dict[str, str] = Field(default_factory=dict, description="Aggregate tags")
    unit: str = Field(..., description="Unit of measurement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "aggregate_id": "cpu_usage_hourly_20240824_10",
                "metric_type": "system_cpu",
                "component": "api_gateway",
                "period_start": "2024-08-24T10:00:00Z",
                "period_end": "2024-08-24T11:00:00Z",
                "aggregation_method": "average",
                "value": 42.3,
                "sample_count": 120
            }
        }


class AlertRuleSchema(BaseModel):
    """Schema for performance alert rules"""
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    description: str = Field(..., description="Rule description")
    
    # Target configuration
    metric_type: MetricTypeEnum = Field(..., description="Target metric type")
    component: Optional[ServiceComponentEnum] = Field(None, description="Target component")
    metric_filter: Optional[Dict[str, Any]] = Field(None, description="Metric filter criteria")
    
    # Threshold configuration
    threshold_type: AlertThresholdTypeEnum = Field(..., description="Type of threshold")
    threshold_value: float = Field(..., description="Threshold value")
    comparison_operator: str = Field(..., description="Comparison operator (>, <, >=, <=, ==)")
    evaluation_window: int = Field(..., description="Evaluation window in minutes")
    
    # Alert behavior
    severity: str = Field(..., description="Alert severity level")
    notification_channels: List[str] = Field(..., description="Notification channels")
    escalation_rules: Optional[List[Dict[str, Any]]] = Field(None, description="Escalation rules")
    auto_resolve: bool = Field(True, description="Whether alert auto-resolves")
    
    # Status and metadata
    enabled: bool = Field(True, description="Whether rule is enabled")
    created_by: PositiveInt = Field(..., description="User who created the rule")
    created_at: datetime = Field(..., description="Rule creation timestamp")
    last_triggered: Optional[datetime] = Field(None, description="Last trigger timestamp")
    trigger_count: int = Field(0, description="Number of times rule has triggered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "high_cpu_alert",
                "rule_name": "High CPU Usage Alert",
                "metric_type": "system_cpu",
                "component": "api_gateway",
                "threshold_type": "absolute_value",
                "threshold_value": 80.0,
                "comparison_operator": ">",
                "evaluation_window": 5,
                "severity": "warning"
            }
        }


class PerformanceAlertSchema(BaseModel):
    """Schema for performance alerts"""
    alert_id: str = Field(..., description="Unique alert identifier")
    rule_id: str = Field(..., description="Rule that triggered the alert")
    metric_type: MetricTypeEnum = Field(..., description="Metric type that triggered alert")
    component: ServiceComponentEnum = Field(..., description="Affected component")
    
    # Alert details
    triggered_at: datetime = Field(..., description="Alert trigger timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution timestamp")
    current_value: float = Field(..., description="Current metric value")
    threshold_value: float = Field(..., description="Threshold that was breached")
    severity: str = Field(..., description="Alert severity")
    
    # Status and resolution
    status: str = Field(..., description="Alert status (open, acknowledged, resolved)")
    acknowledged_by: Optional[PositiveInt] = Field(None, description="User who acknowledged alert")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    
    # Impact assessment
    impact_level: str = Field(..., description="Assessed impact level")
    affected_users: Optional[int] = Field(None, description="Number of affected users")
    business_impact: Optional[str] = Field(None, description="Business impact description")
    
    # Response and actions
    response_actions: List[str] = Field([], description="Actions taken in response")
    escalated: bool = Field(False, description="Whether alert was escalated")
    escalated_to: Optional[List[str]] = Field(None, description="Escalation recipients")
    
    # Context data
    related_metrics: Optional[List[Dict[str, Any]]] = Field(None, description="Related metric data")
    diagnostic_data: Optional[Dict[str, Any]] = Field(None, description="Diagnostic information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "ALT-2024-001234",
                "rule_id": "high_cpu_alert",
                "metric_type": "system_cpu",
                "component": "api_gateway",
                "triggered_at": "2024-08-24T10:30:00Z",
                "current_value": 85.2,
                "threshold_value": 80.0,
                "severity": "warning",
                "status": "open"
            }
        }


class ServiceHealthSchema(BaseModel):
    """Schema for overall service health status"""
    service_id: str = Field(..., description="Unique service identifier")
    component: ServiceComponentEnum = Field(..., description="Service component")
    health_status: PerformanceStatusEnum = Field(..., description="Overall health status")
    
    # Health indicators
    availability: float = Field(..., ge=0.0, le=1.0, description="Service availability (0-1)")
    response_time_avg: float = Field(..., description="Average response time in ms")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")
    throughput: float = Field(..., description="Current throughput")
    
    # Resource utilization
    cpu_utilization: Optional[float] = Field(None, description="CPU utilization percentage")
    memory_utilization: Optional[float] = Field(None, description="Memory utilization percentage")
    disk_utilization: Optional[float] = Field(None, description="Disk utilization percentage")
    network_utilization: Optional[float] = Field(None, description="Network utilization percentage")
    
    # Dependencies
    dependency_status: Dict[str, str] = Field(default_factory=dict, description="Status of dependencies")
    external_service_status: Optional[Dict[str, str]] = Field(None, description="External service status")
    
    # Metrics summary
    active_alerts: int = Field(0, description="Number of active alerts")
    recent_incidents: int = Field(0, description="Recent incidents count")
    last_health_check: datetime = Field(..., description="Last health check timestamp")
    uptime_percentage: float = Field(..., description="Uptime percentage")
    
    # Performance trends
    performance_trend: str = Field(..., description="Performance trend (improving, stable, degrading)")
    capacity_remaining: Optional[float] = Field(None, description="Remaining capacity percentage")
    predicted_capacity_exhaustion: Optional[datetime] = Field(None, description="Predicted capacity exhaustion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "api_gateway_cluster",
                "component": "api_gateway",
                "health_status": "good",
                "availability": 0.999,
                "response_time_avg": 125.5,
                "error_rate": 0.001,
                "throughput": 1500.0,
                "active_alerts": 0
            }
        }


class PerformanceBenchmarkSchema(BaseModel):
    """Schema for performance benchmarks"""
    benchmark_id: str = Field(..., description="Unique benchmark identifier")
    benchmark_name: str = Field(..., description="Benchmark name")
    component: ServiceComponentEnum = Field(..., description="Component being benchmarked")
    
    # Benchmark configuration
    test_configuration: Dict[str, Any] = Field(..., description="Test configuration parameters")
    workload_description: str = Field(..., description="Description of workload")
    test_duration: int = Field(..., description="Test duration in seconds")
    concurrent_users: Optional[int] = Field(None, description="Number of concurrent users")
    
    # Benchmark results
    execution_date: datetime = Field(..., description="Benchmark execution date")
    avg_response_time: float = Field(..., description="Average response time in ms")
    min_response_time: float = Field(..., description="Minimum response time in ms")
    max_response_time: float = Field(..., description="Maximum response time in ms")
    percentile_95_response_time: float = Field(..., description="95th percentile response time")
    
    # Throughput metrics
    requests_per_second: float = Field(..., description="Requests per second")
    peak_throughput: float = Field(..., description="Peak throughput achieved")
    error_rate: float = Field(..., description="Error rate during test")
    
    # Resource utilization during test
    peak_cpu_usage: float = Field(..., description="Peak CPU usage percentage")
    peak_memory_usage: float = Field(..., description="Peak memory usage percentage")
    peak_disk_io: Optional[float] = Field(None, description="Peak disk I/O")
    peak_network_io: Optional[float] = Field(None, description="Peak network I/O")
    
    # Comparison metrics
    baseline_comparison: Optional[Dict[str, float]] = Field(None, description="Comparison with baseline")
    performance_score: float = Field(..., description="Overall performance score")
    regression_detected: bool = Field(False, description="Whether performance regression detected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "benchmark_id": "BENCH-2024-001234",
                "benchmark_name": "API Gateway Load Test",
                "component": "api_gateway",
                "test_duration": 300,
                "concurrent_users": 1000,
                "avg_response_time": 125.5,
                "requests_per_second": 850.0,
                "performance_score": 0.92
            }
        }


class CapacityPlanningSchema(BaseModel):
    """Schema for capacity planning data"""
    planning_id: str = Field(..., description="Unique planning identifier")
    component: ServiceComponentEnum = Field(..., description="Component for capacity planning")
    planning_horizon: int = Field(..., description="Planning horizon in months")
    
    # Current capacity
    current_capacity: Dict[str, float] = Field(..., description="Current capacity metrics")
    current_utilization: Dict[str, float] = Field(..., description="Current utilization levels")
    peak_utilization: Dict[str, float] = Field(..., description="Peak utilization observed")
    
    # Growth projections
    projected_growth_rate: float = Field(..., description="Projected monthly growth rate")
    user_growth_projection: Optional[Dict[str, float]] = Field(None, description="User growth projections")
    usage_growth_projection: Dict[str, float] = Field(..., description="Usage growth projections")
    
    # Capacity requirements
    predicted_capacity_needs: Dict[str, float] = Field(..., description="Predicted capacity needs")
    recommended_scaling_timeline: List[Dict[str, Any]] = Field(..., description="Recommended scaling timeline")
    cost_projections: Optional[Dict[str, float]] = Field(None, description="Cost projections")
    
    # Risk assessment
    capacity_risks: List[str] = Field([], description="Identified capacity risks")
    mitigation_strategies: List[str] = Field([], description="Risk mitigation strategies")
    contingency_plans: List[str] = Field([], description="Contingency plans")
    
    # Analysis metadata
    analysis_date: datetime = Field(..., description="Analysis date")
    analyst_id: PositiveInt = Field(..., description="Analyst who performed planning")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in projections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planning_id": "CAP-2024-Q4",
                "component": "database_cluster",
                "planning_horizon": 12,
                "projected_growth_rate": 0.15,
                "confidence_level": 0.85,
                "capacity_risks": ["storage_growth", "query_complexity"]
            }
        }


# Export schemas
__all__ = [
    # Enums
    "MetricTypeEnum",
    "AlertThresholdTypeEnum",
    "PerformanceStatusEnum",
    "ServiceComponentEnum",
    "MetricAggregationEnum",
    
    # Main schemas
    "PerformanceMetricSchema",
    "PerformanceAggregateSchema",
    "AlertRuleSchema",
    "PerformanceAlertSchema",
    "ServiceHealthSchema",
    "PerformanceBenchmarkSchema",
    "CapacityPlanningSchema"
]
