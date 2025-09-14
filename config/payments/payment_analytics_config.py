"""
Payment Analytics Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Payment Analytics Configuration Module
import asyncio

===============================================

Enterprise-grade payment analytics configuration for the Ainflue platform.
Comprehensive payment data analysis, metrics calculation, fraud detection,
revenue optimization, and advanced business intelligence features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json

class AnalyticsMetric(str, Enum):
    """Analytics metrics"""
    REVENUE = "revenue"
    TRANSACTION_COUNT = "transaction_count"
    AVERAGE_ORDER_VALUE = "average_order_value"
    CONVERSION_RATE = "conversion_rate"
    CHURN_RATE = "churn_rate"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    PAYMENT_SUCCESS_RATE = "payment_success_rate"
    FRAUD_RATE = "fraud_rate"
    REFUND_RATE = "refund_rate"
    SUBSCRIPTION_GROWTH = "subscription_growth"
    MARKET_SHARE = "market_share"
    PROFIT_MARGIN = "profit_margin"

class AnalyticsDimension(str, Enum):
    """Analytics dimensions"""
    TIME = "time"
    GEOGRAPHY = "geography"
    PAYMENT_METHOD = "payment_method"
    CURRENCY = "currency"
    CUSTOMER_SEGMENT = "customer_segment"
    PRODUCT_CATEGORY = "product_category"
    CHANNEL = "channel"
    DEVICE = "device"
    PLATFORM = "platform"
    SUBSCRIPTION_TIER = "subscription_tier"

class TimeGranularity(str, Enum):
    """Time granularity"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AggregationType(str, Enum):
    """Aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    DISTINCT_COUNT = "distinct_count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    GROWTH_RATE = "growth_rate"
    CONVERSION = "conversion"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ReportFormat(str, Enum):
    """Report formats"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    HTML = "html"
    DASHBOARD = "dashboard"

@dataclass
class AnalyticsQuery:
    """Analytics query definition"""
    query_id: str
    name: str
    description: str
    metrics: List[AnalyticsMetric]
    dimensions: List[AnalyticsDimension] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    time_range: Dict[str, datetime] = field(default_factory=dict)
    granularity: TimeGranularity = TimeGranularity.DAY
    aggregation: AggregationType = AggregationType.SUM
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    cache_duration: timedelta = timedelta(minutes=30)
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    is_scheduled: bool = False
    schedule_cron: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary"""
        return {
            "query_id": self.query_id,
            "name": self.name,
            "description": self.description,
            "metrics": [m.value for m in self.metrics],
            "dimensions": [d.value for d in self.dimensions],
            "filters": self.filters,
            "time_range": {
                k: v.isoformat() if isinstance(v, datetime) else v
                for k, v in self.time_range.items()
            },
            "granularity": self.granularity.value,
            "aggregation": self.aggregation.value,
            "limit": self.limit,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "cache_duration_minutes": int(self.cache_duration.total_seconds() / 60),
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "is_scheduled": self.is_scheduled,
            "schedule_cron": self.schedule_cron,
            "metadata": self.metadata
        }

@dataclass
class AnalyticsDataPoint:
    """Analytics data point"""
    timestamp: datetime
    metric: AnalyticsMetric
    value: Union[Decimal, int, float]
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert data point to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric": self.metric.value,
            "value": float(self.value) if isinstance(self.value, Decimal) else self.value,
            "dimensions": self.dimensions,
            "metadata": self.metadata
        }

@dataclass
class AnalyticsAlert:
    """Analytics alert definition"""
    alert_id: str
    name: str
    description: str
    metric: AnalyticsMetric
    condition: str  # e.g., "value > 1000" or "growth_rate < -0.1"
    threshold: Union[Decimal, int, float]
    severity: AlertSeverity = AlertSeverity.WARNING
    time_window: timedelta = timedelta(hours=1)
    frequency: timedelta = timedelta(minutes=15)
    enabled: bool = True
    recipients: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def should_trigger(self, current_value: Union[Decimal, int, float]) -> bool:
        """Check if alert should trigger"""
        if not self.enabled:
            return False
        
        # Simple condition evaluation (in real implementation, use a proper expression evaluator)
        if ">" in self.condition:
            return current_value > self.threshold
        elif "<" in self.condition:
            return current_value < self.threshold
        elif "=" in self.condition:
            return current_value == self.threshold
        elif ">=" in self.condition:
            return current_value >= self.threshold
        elif "<=" in self.condition:
            return current_value <= self.threshold
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "description": self.description,
            "metric": self.metric.value,
            "condition": self.condition,
            "threshold": float(self.threshold) if isinstance(self.threshold, Decimal) else self.threshold,
            "severity": self.severity.value,
            "time_window_minutes": int(self.time_window.total_seconds() / 60),
            "frequency_minutes": int(self.frequency.total_seconds() / 60),
            "enabled": self.enabled,
            "recipients": self.recipients,
            "notification_channels": self.notification_channels,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class AnalyticsReport:
    """Analytics report"""
    report_id: str
    name: str
    description: str
    queries: List[str]  # Query IDs
    format: ReportFormat = ReportFormat.JSON
    template: str = ""
    schedule_cron: str = ""
    recipients: List[str] = field(default_factory=list)
    delivery_channels: List[str] = field(default_factory=list)
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_generated: Optional[datetime] = None
    generation_count: int = 0
    is_automated: bool = False
    retention_days: int = 90
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "report_id": self.report_id,
            "name": self.name,
            "description": self.description,
            "queries": self.queries,
            "format": self.format.value,
            "template": self.template,
            "schedule_cron": self.schedule_cron,
            "recipients": self.recipients,
            "delivery_channels": self.delivery_channels,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_generated": self.last_generated.isoformat() if self.last_generated else None,
            "generation_count": self.generation_count,
            "is_automated": self.is_automated,
            "retention_days": self.retention_days,
            "metadata": self.metadata
        }

@dataclass
class RevenueAnalyticsConfig:
    """Revenue analytics configuration"""
    enabled: bool = True
    
    # Revenue tracking
    revenue_tracking: Dict[str, Any] = field(default_factory=lambda: {
        "real_time_tracking": True,
        "revenue_recognition": "accrual",  # accrual, cash
        "currency_conversion": True,
        "subscription_mrr": True,
        "one_time_revenue": True,
        "refund_tracking": True,
        "chargeback_tracking": True
    })
    
    # Cohort analysis
    cohort_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "cohort_periods": ["daily", "weekly", "monthly"],
        "retention_analysis": True,
        "ltv_calculation": True,
        "churn_prediction": True,
        "revenue_cohorts": True
    })
    
    # Growth metrics
    growth_metrics: Dict[str, Any] = field(default_factory=lambda: {
        "mrr_growth": True,
        "arr_growth": True,
        "user_growth": True,
        "revenue_per_user": True,
        "customer_acquisition_cost": True,
        "payback_period": True,
        "net_revenue_retention": True
    })
    
    # Forecasting
    forecasting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "forecast_periods": [30, 90, 365],  # days
        "models": ["linear", "exponential", "seasonal"],
        "confidence_intervals": True,
        "scenario_analysis": True,
        "budget_variance": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get revenue analytics configuration"""
        return {
            "enabled": self.enabled,
            "revenue_tracking": self.revenue_tracking,
            "cohort_analysis": self.cohort_analysis,
            "growth_metrics": self.growth_metrics,
            "forecasting": self.forecasting
        }

@dataclass
class FraudAnalyticsConfig:
    """Fraud analytics configuration"""
    enabled: bool = True
    
    # Fraud detection
    fraud_detection: Dict[str, Any] = field(default_factory=lambda: {
        "real_time_scoring": True,
        "machine_learning": True,
        "rule_based_detection": True,
        "behavioral_analysis": True,
        "device_fingerprinting": True,
        "geolocation_analysis": True,
        "velocity_checks": True
    })
    
    # Risk scoring
    risk_scoring: Dict[str, Any] = field(default_factory=lambda: {
        "dynamic_scoring": True,
        "score_thresholds": {
            "low_risk": 30,
            "medium_risk": 60,
            "high_risk": 80,
            "block_threshold": 95
        },
        "score_factors": [
            "transaction_amount",
            "payment_method",
            "user_history",
            "device_reputation",
            "geolocation",
            "time_patterns"
        ]
    })
    
    # Pattern detection
    pattern_detection: Dict[str, Any] = field(default_factory=lambda: {
        "anomaly_detection": True,
        "clustering_analysis": True,
        "time_series_analysis": True,
        "network_analysis": True,
        "correlation_analysis": True,
        "outlier_detection": True
    })
    
    # Investigation tools
    investigation_tools: Dict[str, Any] = field(default_factory=lambda: {
        "case_management": True,
        "evidence_collection": True,
        "timeline_reconstruction": True,
        "relationship_mapping": True,
        "pattern_visualization": True,
        "automated_reporting": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get fraud analytics configuration"""
        return {
            "enabled": self.enabled,
            "fraud_detection": self.fraud_detection,
            "risk_scoring": self.risk_scoring,
            "pattern_detection": self.pattern_detection,
            "investigation_tools": self.investigation_tools
        }

@dataclass
class CustomerAnalyticsConfig:
    """Customer analytics configuration"""
    enabled: bool = True
    
    # Segmentation
    segmentation: Dict[str, Any] = field(default_factory=lambda: {
        "behavioral_segmentation": True,
        "demographic_segmentation": True,
        "geographic_segmentation": True,
        "value_based_segmentation": True,
        "lifecycle_segmentation": True,
        "payment_behavior_segmentation": True,
        "dynamic_segments": True
    })
    
    # Customer journey
    customer_journey: Dict[str, Any] = field(default_factory=lambda: {
        "journey_mapping": True,
        "touchpoint_analysis": True,
        "conversion_funnel": True,
        "drop_off_analysis": True,
        "path_analysis": True,
        "attribution_modeling": True
    })
    
    # Lifetime value
    lifetime_value: Dict[str, Any] = field(default_factory=lambda: {
        "ltv_calculation": True,
        "predictive_ltv": True,
        "ltv_segments": True,
        "cohort_ltv": True,
        "ltv_to_cac_ratio": True,
        "value_optimization": True
    })
    
    # Churn analysis
    churn_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "churn_prediction": True,
        "churn_drivers": True,
        "at_risk_identification": True,
        "retention_strategies": True,
        "win_back_campaigns": True,
        "churn_prevention": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get customer analytics configuration"""
        return {
            "enabled": self.enabled,
            "segmentation": self.segmentation,
            "customer_journey": self.customer_journey,
            "lifetime_value": self.lifetime_value,
            "churn_analysis": self.churn_analysis
        }

@dataclass
class PaymentMethodAnalyticsConfig:
    """Payment method analytics configuration"""
    enabled: bool = True
    
    # Performance analysis
    performance_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "success_rates": True,
        "authorization_rates": True,
        "decline_analysis": True,
        "processing_times": True,
        "cost_analysis": True,
        "routing_optimization": True
    })
    
    # Preference analysis
    preference_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "method_preferences": True,
        "geographic_preferences": True,
        "demographic_preferences": True,
        "seasonal_trends": True,
        "device_preferences": True,
        "channel_preferences": True
    })
    
    # Optimization
    optimization: Dict[str, Any] = field(default_factory=lambda: {
        "method_ranking": True,
        "smart_routing": True,
        "fallback_optimization": True,
        "cost_optimization": True,
        "conversion_optimization": True,
        "user_experience_optimization": True
    })
    
    # Risk analysis
    risk_analysis: Dict[str, Any] = field(default_factory=lambda: {
        "method_risk_profiles": True,
        "fraud_rates_by_method": True,
        "chargeback_rates": True,
        "dispute_analysis": True,
        "compliance_monitoring": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get payment method analytics configuration"""
        return {
            "enabled": self.enabled,
            "performance_analysis": self.performance_analysis,
            "preference_analysis": self.preference_analysis,
            "optimization": self.optimization,
            "risk_analysis": self.risk_analysis
        }

class PaymentAnalyticsConfiguration:
    """Main payment analytics configuration manager"""
    
    def __init__(self) -> None:
        """Initialize payment analytics configuration"""
        # Configuration components
        self.revenue_analytics = RevenueAnalyticsConfig()
        self.fraud_analytics = FraudAnalyticsConfig()
        self.customer_analytics = CustomerAnalyticsConfig()
        self.payment_method_analytics = PaymentMethodAnalyticsConfig()
        
        # Data storage
        self.queries: Dict[str, AnalyticsQuery] = {}
        self.data_points: List[AnalyticsDataPoint] = []
        self.alerts: Dict[str, AnalyticsAlert] = {}
        self.reports: Dict[str, AnalyticsReport] = {}
        
        # Global settings
        self.analytics_enabled = True
        self.real_time_analytics = True
        self.data_retention_days = 2555  # 7 years
        self.export_enabled = True
        
        # Data sources
        self.data_sources = {
            "payment_transactions": {
                "enabled": True,
                "table": "payment_transactions",
                "real_time": True,
                "retention_days": 2555
            },
            "subscription_events": {
                "enabled": True,
                "table": "subscription_events",
                "real_time": True,
                "retention_days": 2555
            },
            "user_events": {
                "enabled": True,
                "table": "user_events",
                "real_time": True,
                "retention_days": 365
            },
            "fraud_events": {
                "enabled": True,
                "table": "fraud_events",
                "real_time": True,
                "retention_days": 2555
            }
        }
        
        # Processing settings
        self.processing_settings = {
            "batch_size": 1000,
            "processing_interval_seconds": 60,
            "parallel_processing": True,
            "max_workers": 4,
            "memory_limit_mb": 1024,
            "timeout_seconds": 300
        }
        
        # Caching settings
        self.caching_settings = {
            "enabled": True,
            "cache_backend": "redis",
            "default_ttl_minutes": 30,
            "max_cache_size_mb": 512,
            "cache_compression": True,
            "cache_invalidation": "smart"
        }
        
        # Export settings
        self.export_settings = {
            "max_export_rows": 1000000,
            "supported_formats": ["csv", "excel", "json", "pdf"],
            "compression_enabled": True,
            "encryption_enabled": True,
            "retention_days": 30
        }
        
        # Machine learning settings
        self.ml_settings = {
            "enabled": True,
            "auto_training": True,
            "model_refresh_days": 7,
            "feature_engineering": True,
            "model_validation": True,
            "explainable_ai": True,
            "bias_detection": True
        }
        
        # Compliance settings
        self.compliance_settings = {
            "gdpr_compliance": True,
            "data_anonymization": True,
            "audit_logging": True,
            "access_controls": True,
            "data_lineage": True,
            "privacy_protection": True
        }
        
        # Initialize default queries and alerts
        self._initialize_default_queries()
        self._initialize_default_alerts()
    
    def _initialize_default_queries(self) -> None:
        """Initialize default analytics queries"""
        
        # Daily revenue query
        daily_revenue = AnalyticsQuery(
            query_id="daily_revenue",
            name="Daily Revenue",
            description="Daily revenue aggregated by payment method and currency",
            metrics=[AnalyticsMetric.REVENUE],
            dimensions=[AnalyticsDimension.TIME, AnalyticsDimension.PAYMENT_METHOD, AnalyticsDimension.CURRENCY],
            granularity=TimeGranularity.DAY,
            aggregation=AggregationType.SUM,
            time_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            is_scheduled=True,
            schedule_cron="0 9 * * *"  # Daily at 9 AM
        )
        
        self.queries[daily_revenue.query_id] = daily_revenue
        
        # Conversion funnel query
        conversion_funnel = AnalyticsQuery(
            query_id="conversion_funnel",
            name="Payment Conversion Funnel",
            description="Conversion rates through payment funnel",
            metrics=[AnalyticsMetric.CONVERSION_RATE],
            dimensions=[AnalyticsDimension.CHANNEL, AnalyticsDimension.DEVICE],
            granularity=TimeGranularity.HOUR,
            aggregation=AggregationType.CONVERSION,
            time_range={
                "start": datetime.now() - timedelta(days=7),
                "end": datetime.now()
            }
        )
        
        self.queries[conversion_funnel.query_id] = conversion_funnel
        
        # Fraud detection query
        fraud_detection = AnalyticsQuery(
            query_id="fraud_detection",
            name="Fraud Rate Analysis",
            description="Fraud detection rates by geography and payment method",
            metrics=[AnalyticsMetric.FRAUD_RATE],
            dimensions=[AnalyticsDimension.GEOGRAPHY, AnalyticsDimension.PAYMENT_METHOD],
            granularity=TimeGranularity.HOUR,
            aggregation=AggregationType.AVERAGE,
            time_range={
                "start": datetime.now() - timedelta(days=1),
                "end": datetime.now()
            }
        )
        
        self.queries[fraud_detection.query_id] = fraud_detection
    
    def _initialize_default_alerts(self) -> None:
        """Initialize default analytics alerts"""
        
        # Revenue drop alert
        revenue_drop = AnalyticsAlert(
            alert_id="revenue_drop",
            name="Revenue Drop Alert",
            description="Alert when hourly revenue drops by more than 50%",
            metric=AnalyticsMetric.REVENUE,
            condition="growth_rate < -0.5",
            threshold=Decimal('-0.5'),
            severity=AlertSeverity.ERROR,
            time_window=timedelta(hours=1),
            frequency=timedelta(minutes=15),
            recipients=["finance@ainflue.com", "alerts@ainflue.com"],
            notification_channels=["email", "slack", "webhook"]
        )
        
        self.alerts[revenue_drop.alert_id] = revenue_drop
        
        # High fraud rate alert
        fraud_rate = AnalyticsAlert(
            alert_id="high_fraud_rate",
            name="High Fraud Rate Alert",
            description="Alert when fraud rate exceeds 5%",
            metric=AnalyticsMetric.FRAUD_RATE,
            condition="value > 0.05",
            threshold=Decimal('0.05'),
            severity=AlertSeverity.CRITICAL,
            time_window=timedelta(minutes=30),
            frequency=timedelta(minutes=5),
            recipients=["security@ainflue.com", "alerts@ainflue.com"],
            notification_channels=["email", "slack", "sms", "webhook"]
        )
        
        self.alerts[fraud_rate.alert_id] = fraud_rate
        
        # Low conversion rate alert
        conversion_rate = AnalyticsAlert(
            alert_id="low_conversion_rate",
            name="Low Conversion Rate Alert",
            description="Alert when conversion rate drops below 85%",
            metric=AnalyticsMetric.CONVERSION_RATE,
            condition="value < 0.85",
            threshold=Decimal('0.85'),
            severity=AlertSeverity.WARNING,
            time_window=timedelta(hours=2),
            frequency=timedelta(minutes=30),
            recipients=["payments@ainflue.com", "alerts@ainflue.com"],
            notification_channels=["email", "slack"]
        )
        
        self.alerts[conversion_rate.alert_id] = conversion_rate
    
    def add_query(self, query_data: Dict[str, Any]) -> AnalyticsQuery:
        """Add analytics query"""
        
        query = AnalyticsQuery(
            query_id=query_data.get("query_id", f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=query_data.get("name", ""),
            description=query_data.get("description", ""),
            metrics=[AnalyticsMetric(m) for m in query_data.get("metrics", [])],
            dimensions=[AnalyticsDimension(d) for d in query_data.get("dimensions", [])],
            filters=query_data.get("filters", {}),
            time_range=query_data.get("time_range", {}),
            granularity=TimeGranularity(query_data.get("granularity", "day")),
            aggregation=AggregationType(query_data.get("aggregation", "sum")),
            limit=query_data.get("limit"),
            sort_by=query_data.get("sort_by"),
            sort_order=query_data.get("sort_order", "desc"),
            cache_duration=timedelta(minutes=query_data.get("cache_duration_minutes", 30)),
            created_by=query_data.get("created_by", ""),
            is_scheduled=query_data.get("is_scheduled", False),
            schedule_cron=query_data.get("schedule_cron", ""),
            metadata=query_data.get("metadata", {})
        )
        
        self.queries[query.query_id] = query
        return query
    
    def add_alert(self, alert_data: Dict[str, Any]) -> AnalyticsAlert:
        """Add analytics alert"""
        
        alert = AnalyticsAlert(
            alert_id=alert_data.get("alert_id", f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=alert_data.get("name", ""),
            description=alert_data.get("description", ""),
            metric=AnalyticsMetric(alert_data.get("metric", "revenue")),
            condition=alert_data.get("condition", "value > 0"),
            threshold=Decimal(str(alert_data.get("threshold", "0"))),
            severity=AlertSeverity(alert_data.get("severity", "warning")),
            time_window=timedelta(minutes=alert_data.get("time_window_minutes", 60)),
            frequency=timedelta(minutes=alert_data.get("frequency_minutes", 15)),
            enabled=alert_data.get("enabled", True),
            recipients=alert_data.get("recipients", []),
            notification_channels=alert_data.get("notification_channels", []),
            created_by=alert_data.get("created_by", ""),
            metadata=alert_data.get("metadata", {})
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
    
    async def execute_query(self, query_id: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute analytics query"""
        
        query_result = {
            "success": False,
            "query_id": query_id,
            "data": [],
            "metadata": {},
            "error": None
        }
        
        try:
            if query_id not in self.queries:
                query_result["error"] = f"Query {query_id} not found"
                return query_result
            
            query = self.queries[query_id]
            
            # Apply overrides
            if overrides:
                if "time_range" in overrides:
                    query.time_range.update(overrides["time_range"])
                if "filters" in overrides:
                    query.filters.update(overrides["filters"])
            
            # Check cache first
            cache_key = f"query_{query_id}_{hash(str(query.to_dict()))}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                query_result.update(cached_result)
                query_result["from_cache"] = True
                return query_result
            
            # Execute query
            execution_result = await self._execute_query_logic(query)
            
            if execution_result["success"]:
                # Cache result
                await self._cache_result(cache_key, execution_result, query.cache_duration)
                
                query_result.update(execution_result)
                query_result["from_cache"] = False
            else:
                query_result["error"] = execution_result.get("error", "Query execution failed")
        
        except Exception as e:
            query_result["error"] = str(e)
        
        return query_result
    
    def check_alerts(self, data_points: List[AnalyticsDataPoint]) -> List[Dict[str, Any]]:
        """Check analytics alerts"""
        
        triggered_alerts = []
        
        for data_point in data_points:
            for alert in self.alerts.values():
                if alert.metric == data_point.metric:
                    if alert.should_trigger(data_point.value):
                        triggered_alert = {
                            "alert_id": alert.alert_id,
                            "alert_name": alert.name,
                            "metric": alert.metric.value,
                            "current_value": float(data_point.value),
                            "threshold": float(alert.threshold),
                            "severity": alert.severity.value,
                            "timestamp": data_point.timestamp.isoformat(),
                            "dimensions": data_point.dimensions
                        }
                        
                        triggered_alerts.append(triggered_alert)
                        
                        # Update alert statistics
                        alert.last_triggered = datetime.now()
                        alert.trigger_count += 1
        
        return triggered_alerts
    
    async def generate_report(self, report_id: str) -> Dict[str, Any]:
        """Generate analytics report"""
        
        report_result = {
            "success": False,
            "report_id": report_id,
            "content": None,
            "format": None,
            "error": None
        }
        
        try:
            if report_id not in self.reports:
                report_result["error"] = f"Report {report_id} not found"
                return report_result
            
            report = self.reports[report_id]
            
            # Execute all queries for the report
            report_data = {}
            for query_id in report.queries:
                query_result = await self.execute_query(query_id)
                if query_result["success"]:
                    report_data[query_id] = query_result["data"]
                else:
                    report_result["error"] = f"Failed to execute query {query_id}: {query_result['error']}"
                    return report_result
            
            # Generate report content
            content = await self._generate_report_content(report, report_data)
            
            # Update report statistics
            report.last_generated = datetime.now()
            report.generation_count += 1
            
            report_result.update({
                "success": True,
                "content": content,
                "format": report.format.value,
                "generation_date": datetime.now().isoformat()
            })
        
        except Exception as e:
            report_result["error"] = str(e)
        
        return report_result
    
    def get_analytics_dashboard(self, user_id: str = None) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        
        dashboard = {
            "summary_metrics": self._get_summary_metrics(),
            "revenue_trends": self._get_revenue_trends(),
            "payment_method_performance": self._get_payment_method_performance(),
            "fraud_statistics": self._get_fraud_statistics(),
            "customer_metrics": self._get_customer_metrics(),
            "recent_alerts": self._get_recent_alerts(),
            "top_queries": self._get_top_queries(),
            "system_health": self._get_system_health()
        }
        
        return dashboard
    
    def get_analytics_statistics(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        
        stats = {
            "total_queries": len(self.queries),
            "total_alerts": len(self.alerts),
            "total_reports": len(self.reports),
            "total_data_points": len(self.data_points),
            "active_alerts": len([a for a in self.alerts.values() if a.enabled]),
            "scheduled_queries": len([q for q in self.queries.values() if q.is_scheduled]),
            "automated_reports": len([r for r in self.reports.values() if r.is_automated]),
            "queries_by_metric": {},
            "alerts_by_severity": {},
            "data_points_by_metric": {}
        }
        
        # Query statistics
        for query in self.queries.values():
            for metric in query.metrics:
                metric_name = metric.value
                stats["queries_by_metric"][metric_name] = stats["queries_by_metric"].get(metric_name, 0) + 1
        
        # Alert statistics
        for alert in self.alerts.values():
            severity = alert.severity.value
            stats["alerts_by_severity"][severity] = stats["alerts_by_severity"].get(severity, 0) + 1
        
        # Data point statistics
        for data_point in self.data_points:
            metric = data_point.metric.value
            stats["data_points_by_metric"][metric] = stats["data_points_by_metric"].get(metric, 0) + 1
        
        return stats
    
    # Helper methods
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        # Simulate cache lookup
        return None
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any], duration: timedelta) -> None:
        """Cache query result"""
        # Simulate caching
        pass
    
    async def _execute_query_logic(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute query logic"""
        # Simulate query execution
        sample_data = []
        
        # Generate sample data based on query
        for i in range(10):
            data_point = {
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "metric": query.metrics[0].value if query.metrics else "revenue",
                "value": 1000 + (i * 100),
                "dimensions": {dim.value: f"sample_{dim.value}_{i}" for dim in query.dimensions}
            }
            sample_data.append(data_point)
        
        return {
            "success": True,
            "data": sample_data,
            "metadata": {
                "query_time_ms": 150,
                "row_count": len(sample_data),
                "data_freshness": datetime.now().isoformat()
            }
        }
    
    async def _generate_report_content(self, report: AnalyticsReport, data: Dict[str, Any]) -> Any:
        """Generate report content"""
        if report.format == ReportFormat.JSON:
            return json.dumps(data, indent=2)
        elif report.format == ReportFormat.CSV:
            return "timestamp,metric,value\n" + "\n".join([
                f"{row['timestamp']},{row['metric']},{row['value']}"
                for query_data in data.values()
                for row in query_data
            ])
        else:
            return data
    
    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary metrics for dashboard"""
        return {
            "total_revenue_30d": 125000.00,
            "transaction_count_30d": 15420,
            "average_order_value": 8.11,
            "conversion_rate": 0.92,
            "fraud_rate": 0.03,
            "refund_rate": 0.02
        }
    
    def _get_revenue_trends(self) -> List[Dict[str, Any]]:
        """Get revenue trends"""
        return [
            {"date": "2025-01-01", "revenue": 4200.00},
            {"date": "2025-01-02", "revenue": 4350.00},
            {"date": "2025-01-03", "revenue": 4100.00},
            {"date": "2025-01-04", "revenue": 4500.00},
            {"date": "2025-01-05", "revenue": 4680.00}
        ]
    
    def _get_payment_method_performance(self) -> Dict[str, Any]:
        """Get payment method performance"""
        return {
            "credit_card": {"success_rate": 0.94, "volume_share": 0.65},
            "paypal": {"success_rate": 0.96, "volume_share": 0.20},
            "bank_transfer": {"success_rate": 0.98, "volume_share": 0.10},
            "crypto": {"success_rate": 0.89, "volume_share": 0.05}
        }
    
    def _get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud statistics"""
        return {
            "fraud_rate": 0.03,
            "blocked_transactions": 125,
            "false_positives": 8,
            "manual_reviews": 23,
            "top_fraud_indicators": ["suspicious_velocity", "unusual_location", "device_mismatch"]
        }
    
    def _get_customer_metrics(self) -> Dict[str, Any]:
        """Get customer metrics"""
        return {
            "total_customers": 12450,
            "new_customers_30d": 890,
            "customer_lifetime_value": 156.78,
            "churn_rate": 0.05,
            "retention_rate_90d": 0.78
        }
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return [
            {
                "alert_id": "fraud_rate",
                "severity": "warning",
                "message": "Fraud rate increased to 4.2%",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _get_top_queries(self) -> List[Dict[str, Any]]:
        """Get top queries"""
        return [
            {"query_id": "daily_revenue", "execution_count": 45, "avg_time_ms": 120},
            {"query_id": "conversion_funnel", "execution_count": 32, "avg_time_ms": 95},
            {"query_id": "fraud_detection", "execution_count": 28, "avg_time_ms": 180}
        ]
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        return {
            "data_freshness": "real-time",
            "query_success_rate": 0.99,
            "average_query_time_ms": 135,
            "cache_hit_rate": 0.78,
            "system_load": 0.65
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete payment analytics configuration"""
        return {
            "analytics_statistics": self.get_analytics_statistics(),
            "revenue_analytics": self.revenue_analytics.get_config(),
            "fraud_analytics": self.fraud_analytics.get_config(),
            "customer_analytics": self.customer_analytics.get_config(),
            "payment_method_analytics": self.payment_method_analytics.get_config(),
            "queries_count": len(self.queries),
            "alerts_count": len(self.alerts),
            "reports_count": len(self.reports),
            "data_points_count": len(self.data_points),
            "global_settings": {
                "analytics_enabled": self.analytics_enabled,
                "real_time_analytics": self.real_time_analytics,
                "data_retention_days": self.data_retention_days,
                "export_enabled": self.export_enabled
            },
            "data_sources": self.data_sources,
            "processing_settings": self.processing_settings,
            "caching_settings": self.caching_settings,
            "export_settings": self.export_settings,
            "ml_settings": self.ml_settings,
            "compliance_settings": self.compliance_settings
        }

# Global payment analytics configuration instance
payment_analytics_config = PaymentAnalyticsConfiguration()

# Export main classes
__all__ = [
    "PaymentAnalyticsConfiguration",
    "AnalyticsMetric",
    "AnalyticsDimension",
    "TimeGranularity",
    "AggregationType",
    "AlertSeverity",
    "ReportFormat",
    "AnalyticsQuery",
    "AnalyticsDataPoint",
    "AnalyticsAlert",
    "AnalyticsReport",
    "RevenueAnalyticsConfig",
    "FraudAnalyticsConfig",
    "CustomerAnalyticsConfig",
    "PaymentMethodAnalyticsConfig",
    "payment_analytics_config"
]
