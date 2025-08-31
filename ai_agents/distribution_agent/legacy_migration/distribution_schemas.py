"""Distribution Schemas for IA Influencer Agent - Professional Content Distribution Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

🚀 Professional Team Expertise:
- Lead IA Developer: Advanced AI/ML Architecture
- Senior Backend Engineer: Enterprise-grade Infrastructure  
- ML Engineer: Deep Learning & Data Processing
- Database Architect: High-performance Data Management
- Security Engineer: Advanced Cybersecurity & Protection
- Microservices Architect: Scalable Distributed Systems
- Audio Engineer: Professional Audio Processing
- DevOps Engineer: Cloud Infrastructure & CI/CD
- IA Prompt Engineer: Advanced Prompt Engineering & LLM Integration
"""
from marshmallow import Schema, fields, validate, post_load, ValidationError
from typing import Dict, List, Any
from datetime import datetime
import re

from .distribution_models import (
    ContentType, PlatformType, DistributionStatus,
    DistributionRequest, DistributionResult, ContentMetadata,
    DistributionConfig, PlatformCredentials, DistributionAnalytics
)


class ContentMetadataSchema(Schema):
    """Professional content metadata schema with advanced validation"""    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Content title is required'}
    )
    description = fields.Str(
        validate=validate.Length(max=5000),
        allow_none=True
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        validate=validate.Length(max=50),
        missing=[]
    )
    category = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True
    )
    language = fields.Str(
        validate=validate.Regexp(r'^[a-z]{2}$'),
        missing='en'
    )
    duration = fields.Int(
        validate=validate.Range(min=1),
        allow_none=True
    )
    file_size = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )
    resolution = fields.Str(
        validate=validate.Regexp(r'^\d+x\d+$'),
        allow_none=True
    )
    bitrate = fields.Int(
        validate=validate.Range(min=1),
        allow_none=True
    )
    format = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=10)
    )
    created_at = fields.DateTime(missing=datetime.now)
    updated_at = fields.DateTime(missing=datetime.now)

    @post_load
    def make_content_metadata(self, data, **kwargs):
        return ContentMetadata(**data)


class DistributionConfigSchema(Schema):
    """Professional distribution configuration schema"""    
    platform = fields.Enum(
        PlatformType,
        required=True,
        error_messages={'required': 'Platform is required'}
    )
    content_type = fields.Enum(
        ContentType,
        required=True,
        error_messages={'required': 'Content type is required'}
    )
    publish_immediately = fields.Bool(missing=True)
    scheduled_time = fields.DateTime(allow_none=True)
    visibility = fields.Str(
        validate=validate.OneOf(['public', 'private', 'unlisted', 'friends']),
        missing='public'
    )
    enable_comments = fields.Bool(missing=True)
    enable_monetization = fields.Bool(missing=False)
    notification_settings = fields.Dict(
        keys=fields.Str(),
        values=fields.Bool(),
        missing=dict
    )
    custom_thumbnail = fields.Str(allow_none=True)
    custom_settings = fields.Dict(missing=dict)

    def validate_scheduled_time(self, value):
        """Validate scheduled time is in the future"""        if value and value <= datetime.now():
            raise ValidationError("Scheduled time must be in the future")

    @post_load
    def make_distribution_config(self, data, **kwargs):
        return DistributionConfig(**data)


class DistributionRequestSchema(Schema):
    """Professional distribution request schema"""    
    id = fields.Str(missing=lambda: str(__import__('uuid').uuid4()))
    user_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'User ID is required'}
    )
    content_path = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500),
        error_messages={'required': 'Content path is required'}
    )
    content_metadata = fields.Nested(
        ContentMetadataSchema,
        required=True,
        error_messages={'required': 'Content metadata is required'}
    )
    distribution_configs = fields.List(
        fields.Nested(DistributionConfigSchema),
        required=True,
        validate=validate.Length(min=1, max=20),
        error_messages={'required': 'At least one distribution config is required'}
    )
    priority = fields.Int(
        validate=validate.Range(min=1, max=10),
        missing=1
    )
    max_retries = fields.Int(
        validate=validate.Range(min=0, max=10),
        missing=3
    )
    created_at = fields.DateTime(missing=datetime.now)
    updated_at = fields.DateTime(missing=datetime.now)

    def validate_content_path(self, value):
        """Validate content path format"""        if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', value):
            raise ValidationError("Invalid content path format")

    @post_load
    def make_distribution_request(self, data, **kwargs):
        return DistributionRequest(**data)


class DistributionResultSchema(Schema):
    """Professional distribution result schema"""    
    id = fields.Str(required=True)
    request_id = fields.Str(required=True)
    platform = fields.Enum(PlatformType, required=True)
    status = fields.Enum(DistributionStatus, required=True)
    platform_id = fields.Str(allow_none=True)
    platform_url = fields.Url(allow_none=True)
    error_message = fields.Str(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    retry_count = fields.Int(
        validate=validate.Range(min=0),
        missing=0
    )
    processing_time = fields.Float(
        validate=validate.Range(min=0),
        allow_none=True
    )
    created_at = fields.DateTime(missing=datetime.now)
    completed_at = fields.DateTime(allow_none=True)
    metadata = fields.Dict(missing=dict)

    @post_load
    def make_distribution_result(self, data, **kwargs):
        return DistributionResult(**data)


class PlatformCredentialsSchema(Schema):
    """Professional platform credentials schema with security validation"""    
    platform = fields.Enum(PlatformType, required=True)
    user_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    access_token = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=2000)
    )
    refresh_token = fields.Str(
        validate=validate.Length(min=10, max=2000),
        allow_none=True
    )
    token_expires_at = fields.DateTime(allow_none=True)
    client_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    client_secret = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    additional_data = fields.Dict(missing=dict)
    created_at = fields.DateTime(missing=datetime.now)
    updated_at = fields.DateTime(missing=datetime.now)

    def validate_token_format(self, token):
        """Validate token format (basic validation)"""        if token and len(token) < 10:
            raise ValidationError("Token too short")
        return True

    @post_load
    def make_platform_credentials(self, data, **kwargs):
        return PlatformCredentials(**data)


class DistributionAnalyticsSchema(Schema):
    """Professional distribution analytics schema"""    
    id = fields.Str(missing=lambda: str(__import__('uuid').uuid4()))
    distribution_result_id = fields.Str(required=True)
    platform = fields.Enum(PlatformType, required=True)
    views = fields.Int(validate=validate.Range(min=0), missing=0)
    likes = fields.Int(validate=validate.Range(min=0), missing=0)
    comments = fields.Int(validate=validate.Range(min=0), missing=0)
    shares = fields.Int(validate=validate.Range(min=0), missing=0)
    reach = fields.Int(validate=validate.Range(min=0), missing=0)
    engagement_rate = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=0.0
    )
    click_through_rate = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=0.0
    )
    conversion_rate = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=0.0
    )
    revenue = fields.Float(validate=validate.Range(min=0), missing=0.0)
    collected_at = fields.DateTime(missing=datetime.now)
    period_start = fields.DateTime(required=True)
    period_end = fields.DateTime(required=True)
    raw_data = fields.Dict(missing=dict)

    def validate_date_range(self, data):
        """Validate date range consistency"""        if data.get('period_start') and data.get('period_end'):
            if data['period_start'] >= data['period_end']:
                raise ValidationError("Period start must be before period end")

    @post_load
    def make_distribution_analytics(self, data, **kwargs):
        return DistributionAnalytics(**data)


class CollaborationRequestSchema(Schema):
    """Professional collaboration request schema"""    
    id = fields.Str(missing=lambda: str(__import__('uuid').uuid4()))
    creator_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    collaborator_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    content_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    collaboration_type = fields.Str(
        required=True,
        validate=validate.OneOf(['revenue_share', 'cross_promotion', 'co_creation', 'endorsement'])
    )
    platforms = fields.List(
        fields.Enum(PlatformType),
        required=True,
        validate=validate.Length(min=1)
    )
    revenue_split = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(validate=validate.Range(min=0, max=100)),
        required=True
    )
    status = fields.Str(
        validate=validate.OneOf(['pending', 'accepted', 'rejected', 'expired', 'completed']),
        missing='pending'
    )
    terms = fields.Dict(missing=dict)
    created_at = fields.DateTime(missing=datetime.now)
    expires_at = fields.DateTime(allow_none=True)

    def validate_revenue_split(self, data):
        """Validate revenue split adds up to 100%"""        if data.get('revenue_split'):
            total = sum(data['revenue_split'].values())
            if abs(total - 100.0) > 0.01:  # Allow small floating point errors
                raise ValidationError("Revenue split must add up to 100%")


class ContentProtectionSchema(Schema):
    """Professional content protection schema"""    
    content_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    protection_level = fields.Str(
        validate=validate.OneOf(['basic', 'standard', 'premium', 'enterprise']),
        missing='standard'
    )
    watermark_enabled = fields.Bool(missing=True)
    drm_enabled = fields.Bool(missing=False)
    geographic_restrictions = fields.List(
        fields.Str(validate=validate.Length(min=2, max=3)),  # Country codes
        missing=[]
    )
    access_restrictions = fields.Dict(missing=dict)
    copyright_metadata = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        missing=dict
    )
    monitoring_enabled = fields.Bool(missing=True)
    takedown_requests = fields.List(fields.Dict(), missing=[])
    created_at = fields.DateTime(missing=datetime.now)


class DistributionBatchSchema(Schema):
    """Professional distribution batch schema"""    
    id = fields.Str(missing=lambda: str(__import__('uuid').uuid4()))
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=1000), allow_none=True)
    requests = fields.List(
        fields.Nested(DistributionRequestSchema),
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    status = fields.Str(
        validate=validate.OneOf(['pending', 'processing', 'completed', 'failed', 'cancelled']),
        missing='pending'
    )
    total_requests = fields.Int(validate=validate.Range(min=1), required=True)
    completed_requests = fields.Int(validate=validate.Range(min=0), missing=0)
    failed_requests = fields.Int(validate=validate.Range(min=0), missing=0)
    created_at = fields.DateTime(missing=datetime.now)
    started_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)


class ValidationErrorSchema(Schema):
    """Professional validation error schema"""    
    field = fields.Str(required=True)
    message = fields.Str(required=True)
    code = fields.Str(missing='validation_error')
    details = fields.Dict(missing=dict)


class APIResponseSchema(Schema):
    """Professional API response schema"""    
    success = fields.Bool(required=True)
    data = fields.Raw(allow_none=True)
    message = fields.Str(allow_none=True)
    errors = fields.List(fields.Nested(ValidationErrorSchema), missing=[])
    pagination = fields.Dict(allow_none=True)
    timestamp = fields.DateTime(missing=datetime.now)
    request_id = fields.Str(allow_none=True)


class PlatformStatusSchema(Schema):
    """Professional platform status schema"""    
    platform = fields.Enum(PlatformType, required=True)
    status = fields.Str(
        validate=validate.OneOf(['online', 'offline', 'maintenance', 'limited']),
        required=True
    )
    last_checked = fields.DateTime(required=True)
    response_time = fields.Float(validate=validate.Range(min=0), allow_none=True)
    error_rate = fields.Float(validate=validate.Range(min=0, max=100), missing=0.0)
    rate_limit_remaining = fields.Int(validate=validate.Range(min=0), allow_none=True)
    rate_limit_reset = fields.DateTime(allow_none=True)
    capabilities = fields.Dict(missing=dict)


# Schema registry for easy access
SCHEMA_REGISTRY = {
    'content_metadata': ContentMetadataSchema,
    'distribution_config': DistributionConfigSchema,
    'distribution_request': DistributionRequestSchema,
    'distribution_result': DistributionResultSchema,
    'platform_credentials': PlatformCredentialsSchema,
    'distribution_analytics': DistributionAnalyticsSchema,
    'collaboration_request': CollaborationRequestSchema,
    'content_protection': ContentProtectionSchema,
    'distribution_batch': DistributionBatchSchema,
    'validation_error': ValidationErrorSchema,
    'api_response': APIResponseSchema,
    'platform_status': PlatformStatusSchema
}


def get_schema(schema_name: str) -> Schema:
    """Get schema instance by name"""    if schema_name not in SCHEMA_REGISTRY:
        raise ValueError(f"Unknown schema: {schema_name}")
    return SCHEMA_REGISTRY[schema_name]()


def validate_data(schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data using specified schema"""    schema = get_schema(schema_name)
    try:
        return schema.load(data)
    except ValidationError as e:
        raise ValidationError(f"Validation failed for {schema_name}: {e.messages}")


# Export all schemas for external use
__all__ = [
    'ContentMetadataSchema',
    'DistributionConfigSchema',
    'DistributionRequestSchema',
    'DistributionResultSchema',
    'PlatformCredentialsSchema',
    'DistributionAnalyticsSchema',
    'CollaborationRequestSchema',
    'ContentProtectionSchema',
    'DistributionBatchSchema',
    'ValidationErrorSchema',
    'APIResponseSchema',
    'PlatformStatusSchema',
    'SCHEMA_REGISTRY',
    'get_schema',
    'validate_data'
]
