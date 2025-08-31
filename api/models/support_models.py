"""IA Influencer Agent Platform - Support Models
Additional models for notifications, analytics, monitoring, and system support

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .base import BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, MetadataMixin, StatusMixin


# License Models
class License(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Licensing system for content usage rights"""    
    __tablename__ = 'licenses'
    
    content_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='CASCADE'), nullable=False, index=True)
    licensor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    license_name: Mapped[str] = mapped_column(String(200), nullable=False)
    license_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    terms_and_conditions: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    
    __table_args__ = (Index('idx_licenses_type_status', 'license_type', 'status'),)


class LicenseAgreement(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """License agreements between parties"""    
    __tablename__ = 'license_agreements'
    
    license_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('licenses.id', ondelete='CASCADE'), nullable=False, index=True)
    licensee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    agreement_terms: Mapped[str] = mapped_column(Text, nullable=False)
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (Index('idx_agreements_signed_expires', 'signed_at', 'expires_at'),)


class LicenseUsage(BaseModel, UUIDMixin, TimestampMixin):
    """License usage tracking and analytics"""    
    __tablename__ = 'license_usage'
    
    agreement_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('license_agreements.id', ondelete='CASCADE'), nullable=False, index=True)
    
    usage_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    usage_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    __table_args__ = (Index('idx_usage_type_created', 'usage_type', 'created_at'),)


class LicenseRevenue(BaseModel, UUIDMixin, TimestampMixin):
    """Revenue tracking for licenses"""    
    __tablename__ = 'license_revenues'
    
    agreement_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('license_agreements.id', ondelete='CASCADE'), nullable=False, index=True)
    
    revenue_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    revenue_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revenue_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_license_revenue_period', 'revenue_period_start', 'revenue_period_end'),)


# Revenue Models
class Revenue(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Core revenue tracking"""    
    __tablename__ = 'revenues'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    content_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='SET NULL'), nullable=True, index=True)
    
    revenue_source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    revenue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_revenues_creator_date', 'creator_id', 'revenue_date'),)


class RevenueStream(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Revenue stream configuration"""    
    __tablename__ = 'revenue_streams'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    stream_name: Mapped[str] = mapped_column(String(200), nullable=False)
    stream_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_revenue_streams_type', 'stream_type'),)


class RevenueShare(BaseModel, UUIDMixin, TimestampMixin):
    """Revenue sharing between collaborators"""    
    __tablename__ = 'revenue_shares'
    
    revenue_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('revenues.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    share_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    share_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    __table_args__ = (CheckConstraint('share_percentage >= 0 AND share_percentage <= 100', name='valid_share_percentage'),)


class PaymentRecord(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Payment processing records"""    
    __tablename__ = 'payment_records'
    
    revenue_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('revenues.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    __table_args__ = (Index('idx_payments_provider_reference', 'payment_provider', 'payment_reference'),)


class RoyaltyCalculation(BaseModel, UUIDMixin, TimestampMixin):
    """Royalty calculations and distributions"""    
    __tablename__ = 'royalty_calculations'
    
    content_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    calculation_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    calculation_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    total_royalties: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    calculation_details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_royalties_period', 'calculation_period_start', 'calculation_period_end'),)


class RevenueReport(BaseModel, UUIDMixin, TimestampMixin):
    """Revenue reporting and analytics"""    
    __tablename__ = 'revenue_reports'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    report_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    report_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    report_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_reports_creator_type_period', 'creator_id', 'report_type', 'report_period_start'),)


# Distribution Models
class Distribution(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Content distribution management"""    
    __tablename__ = 'distributions'
    
    content_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    distribution_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_platforms: Mapped[List[str]] = mapped_column(ARRAY(String(100)), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (Index('idx_distributions_scheduled', 'scheduled_at'),)


class DistributionChannel(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Distribution channel configuration"""    
    __tablename__ = 'distribution_channels'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    channel_name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_channels_platform', 'platform'),)


class DistributionMetrics(BaseModel, UUIDMixin, TimestampMixin):
    """Distribution performance metrics"""    
    __tablename__ = 'distribution_metrics'
    
    distribution_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('distributions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metrics_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_metrics_platform_recorded', 'platform', 'recorded_at'),)


class PlatformIntegration(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Platform integration management"""    
    __tablename__ = 'platform_integrations'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    integration_type: Mapped[str] = mapped_column(String(50), nullable=False)
    credentials: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_integrations_platform', 'platform_name'),)


class ContentDelivery(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Content delivery tracking"""    
    __tablename__ = 'content_deliveries'
    
    distribution_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('distributions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    delivery_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (Index('idx_deliveries_platform_delivered', 'platform', 'delivered_at'),)


# Analytics Models
class Analytics(BaseModel, UUIDMixin, TimestampMixin):
    """Core analytics data"""    
    __tablename__ = 'analytics'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    content_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='SET NULL'), nullable=True, index=True)
    
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_analytics_creator_metric_date', 'creator_id', 'metric_type', 'recorded_at'),)


class PerformanceMetrics(BaseModel, UUIDMixin, TimestampMixin):
    """Detailed performance analytics"""    
    __tablename__ = 'performance_metrics'
    
    content_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metrics_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_performance_content_platform_period', 'content_id', 'platform', 'period_start'),)


class AudienceInsights(BaseModel, UUIDMixin, TimestampMixin):
    """Audience analytics and demographics"""    
    __tablename__ = 'audience_insights'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    audience_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    insights_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_audience_creator_platform_date', 'creator_id', 'platform', 'insights_date'),)


class EngagementMetrics(BaseModel, UUIDMixin, TimestampMixin):
    """Engagement tracking and analysis"""    
    __tablename__ = 'engagement_metrics'
    
    content_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('contents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    engagement_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    engagement_value: Mapped[int] = mapped_column(Integer, nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    __table_args__ = (Index('idx_engagement_content_type_platform', 'content_id', 'engagement_type', 'platform'),)


class TrendAnalysis(BaseModel, UUIDMixin, TimestampMixin):
    """Trend analysis and predictions"""    
    __tablename__ = 'trend_analysis'
    
    trend_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    trend_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_trends_category_date', 'trend_category', 'analysis_date'),)


class PredictiveAnalytics(BaseModel, UUIDMixin, TimestampMixin):
    """Predictive analytics and forecasting"""    
    __tablename__ = 'predictive_analytics'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prediction_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence_level: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    prediction_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    __table_args__ = (Index('idx_predictions_creator_type', 'creator_id', 'prediction_type'),)


# Monitoring Models
class MonitoringJob(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Content monitoring job management"""    
    __tablename__ = 'monitoring_jobs'
    
    protection_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('content_protections.id', ondelete='CASCADE'), nullable=False, index=True)
    
    job_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    schedule_expression: Mapped[str] = mapped_column(String(200), nullable=False)
    next_execution: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    __table_args__ = (Index('idx_monitoring_next_execution', 'next_execution'),)


class CrawlerResult(BaseModel, UUIDMixin, TimestampMixin):
    """Web crawler results"""    
    __tablename__ = 'crawler_results'
    
    monitoring_job_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('monitoring_jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    
    crawled_url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    crawl_result: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    similarity_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    __table_args__ = (Index('idx_crawler_similarity', 'similarity_detected'),)


class AlertRule(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Alert rule configuration"""    
    __tablename__ = 'alert_rules'
    
    creator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    actions: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_alert_rules_type', 'rule_type'),)


class NotificationEvent(BaseModel, UUIDMixin, TimestampMixin):
    """Notification event tracking"""    
    __tablename__ = 'notification_events'
    
    alert_rule_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('alert_rules.id', ondelete='SET NULL'), nullable=True, index=True)
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    __table_args__ = (Index('idx_events_type_processed', 'event_type', 'is_processed'),)


class SystemHealth(BaseModel, UUIDMixin, TimestampMixin):
    """System health monitoring"""    
    __tablename__ = 'system_health'
    
    component_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    health_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_health_component_status', 'component_name', 'health_status'),)


class PerformanceLog(BaseModel, UUIDMixin, TimestampMixin):
    """System performance logging"""    
    __tablename__ = 'performance_logs'
    
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_usage: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (Index('idx_performance_operation_time', 'operation_type', 'execution_time_ms'),)


# Notification Models
class Notification(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """User notifications"""    
    __tablename__ = 'notifications'
    
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    __table_args__ = (Index('idx_notifications_user_read', 'user_id', 'is_read'),)


class NotificationTemplate(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Notification templates"""    
    __tablename__ = 'notification_templates'
    
    template_name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    template_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject_template: Mapped[str] = mapped_column(String(300), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    
    __table_args__ = (Index('idx_templates_type', 'template_type'),)


class NotificationLog(BaseModel, UUIDMixin, TimestampMixin):
    """Notification delivery logging"""    
    __tablename__ = 'notification_logs'
    
    notification_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False, index=True)
    
    delivery_channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    delivery_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    delivery_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (Index('idx_logs_channel_status', 'delivery_channel', 'delivery_status'),)


# Audit Models
class AuditLog(BaseModel, UUIDMixin, TimestampMixin):
    """System audit logging"""    
    __tablename__ = 'audit_logs'
    
    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    action_details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_audit_user_action', 'user_id', 'action_type'),)


class SecurityEvent(BaseModel, UUIDMixin, TimestampMixin):
    """Security event tracking"""    
    __tablename__ = 'security_events'
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    event_details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (Index('idx_security_type_severity', 'event_type', 'severity_level'),)


class ComplianceRecord(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Compliance and regulatory records"""    
    __tablename__ = 'compliance_records'
    
    compliance_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    regulation_name: Mapped[str] = mapped_column(String(200), nullable=False)
    compliance_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    audit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (Index('idx_compliance_type_audit', 'compliance_type', 'audit_date'),)
