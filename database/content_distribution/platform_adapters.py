"""
Platform Adapters Database Module - Enterprise Multi-Platform Integration System

Advanced database architecture for managing platform adapters, API integrations,
and platform-specific content adaptation within the IA Influencer Agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL NOTICE:
This code and database architecture are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties: Lead AI Developer + Senior Backend Engineer + Database Administrator + 
Security Specialist + Microservices Architect + Platform Integration Expert + API Engineer
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from contextlib import asynccontextmanager
import logging
import hashlib
from urllib.parse import urlparse

import asyncpg
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import pydantic
from pydantic import BaseModel, Field, validator
import httpx

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class PlatformType(str, Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"
    BANDCAMP = "bandcamp"
    AUDIOMACK = "audiomack"

class AdapterStatus(str, Enum):
    """Platform adapter operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"

class IntegrationLevel(str, Enum):
    """Platform integration capability levels"""
    BASIC = "basic"              # Read-only access
    STANDARD = "standard"        # Read/Write content
    ADVANCED = "advanced"        # Full API access
    ENTERPRISE = "enterprise"    # Custom enterprise features
    PREMIUM = "premium"          # White-glove service

class AuthenticationMethod(str, Enum):
    """Platform authentication methods"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"
    WEBHOOK = "webhook"

@dataclass
class PlatformCapabilities:
    """Platform technical capabilities and limitations"""
    max_file_size: int = 0
    supported_formats: List[str] = field(default_factory=list)
    max_concurrent_uploads: int = 1
    supports_scheduling: bool = False
    supports_analytics: bool = False
    supports_monetization: bool = False
    supports_live_streaming: bool = False
    supports_stories: bool = False
    supports_shorts: bool = False
    api_rate_limit: int = 100
    burst_rate_limit: int = 10
    requires_authentication: bool = True
    content_restrictions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentRequirements:
    """Platform-specific content requirements"""
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    aspect_ratios: List[str] = field(default_factory=list)
    resolutions: List[str] = field(default_factory=list)
    audio_bitrates: List[int] = field(default_factory=list)
    video_bitrates: List[int] = field(default_factory=list)
    thumbnail_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata_requirements: Dict[str, Any] = field(default_factory=dict)
    title_max_length: int = 100
    description_max_length: int = 5000
    tags_max_count: int = 30
    hashtags_max_count: int = 30

class PlatformAdapter(Base):
    """Platform adapter database model"""
    __tablename__ = "platform_adapters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, unique=True)
    platform_type = Column(String(30), nullable=False)
    adapter_version = Column(String(20), nullable=False)
    
    # Configuration
    api_base_url = Column(String(200), nullable=False)
    api_version = Column(String(20), nullable=True)
    authentication_method = Column(String(30), nullable=False)
    integration_level = Column(String(20), nullable=False, default=IntegrationLevel.STANDARD)
    
    # Status and Health
    status = Column(String(20), nullable=False, default=AdapterStatus.ACTIVE)
    health_score = Column(Float, nullable=True, default=100.0)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    uptime_percentage = Column(Float, nullable=True, default=100.0)
    
    # Capabilities
    capabilities = Column(JSONB, nullable=False)
    content_requirements = Column(JSONB, nullable=False)
    supported_operations = Column(ARRAY(String), nullable=False)
    
    # Rate Limiting
    rate_limit_requests_per_hour = Column(Integer, nullable=False, default=1000)
    rate_limit_requests_per_minute = Column(Integer, nullable=False, default=60)
    burst_limit = Column(Integer, nullable=False, default=10)
    current_rate_usage = Column(Integer, nullable=False, default=0)
    rate_limit_reset_time = Column(DateTime(timezone=True), nullable=True)
    
    # Performance Metrics
    average_response_time = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True, default=100.0)
    error_rate = Column(Float, nullable=True, default=0.0)
    total_requests = Column(Integer, nullable=False, default=0)
    failed_requests = Column(Integer, nullable=False, default=0)
    
    # Configuration Settings
    configuration = Column(JSONB, nullable=True)
    feature_flags = Column(JSONB, nullable=True)
    custom_settings = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    is_deprecated = Column(Boolean, nullable=False, default=False)
    deprecation_date = Column(DateTime(timezone=True), nullable=True)

class PlatformCredential(Base):
    """Platform credentials database model"""
    __tablename__ = "platform_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_id = Column(UUID(as_uuid=True), ForeignKey('platform_adapters.id'), nullable=False)
    credential_name = Column(String(100), nullable=False)
    
    # Authentication Data (encrypted)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)
    oauth_data = Column(JSONB, nullable=True)
    
    # Token Management
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    token_scope = Column(ARRAY(String), nullable=True)
    last_refreshed = Column(DateTime(timezone=True), nullable=True)
    refresh_attempts = Column(Integer, nullable=False, default=0)
    
    # Account Information
    platform_user_id = Column(String(100), nullable=True)
    platform_username = Column(String(100), nullable=True)
    account_email = Column(String(200), nullable=True)
    account_status = Column(String(30), nullable=True)
    account_tier = Column(String(30), nullable=True)
    
    # Permissions and Scope
    granted_permissions = Column(ARRAY(String), nullable=True)
    permission_level = Column(String(30), nullable=True)
    can_read = Column(Boolean, nullable=False, default=True)
    can_write = Column(Boolean, nullable=False, default=False)
    can_delete = Column(Boolean, nullable=False, default=False)
    can_moderate = Column(Boolean, nullable=False, default=False)
    
    # Status Tracking
    is_active = Column(Boolean, nullable=False, default=True)
    is_valid = Column(Boolean, nullable=False, default=True)
    last_validation = Column(DateTime(timezone=True), nullable=True)
    validation_errors = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime(timezone=True), nullable=True)

class PlatformOperation(Base):
    """Platform operation tracking database model"""
    __tablename__ = "platform_operations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id = Column(UUID(as_uuid=True), ForeignKey('platform_adapters.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Operation Details
    operation_type = Column(String(50), nullable=False)  # upload, update, delete, fetch
    operation_status = Column(String(30), nullable=False)  # pending, success, failed, retry
    platform_content_id = Column(String(200), nullable=True)
    platform_url = Column(String(500), nullable=True)
    
    # Request/Response Data
    request_data = Column(JSONB, nullable=True)
    response_data = Column(JSONB, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Timing Information
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Performance Metrics
    response_time_ms = Column(Integer, nullable=True)
    bytes_transferred = Column(Integer, nullable=True)
    api_calls_used = Column(Integer, nullable=False, default=1)
    cost_cents = Column(Integer, nullable=True)
    
    # Metadata
    correlation_id = Column(String(100), nullable=True, index=True)
    trace_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)

class PlatformAnalytics(Base):
    """Platform analytics and insights database model"""
    __tablename__ = "platform_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id = Column(UUID(as_uuid=True), ForeignKey('platform_adapters.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Analytics Period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    analytics_type = Column(String(30), nullable=False)  # content, account, campaign
    
    # Engagement Metrics
    views = Column(Integer, nullable=True, default=0)
    likes = Column(Integer, nullable=True, default=0)
    dislikes = Column(Integer, nullable=True, default=0)
    comments = Column(Integer, nullable=True, default=0)
    shares = Column(Integer, nullable=True, default=0)
    saves = Column(Integer, nullable=True, default=0)
    
    # Reach and Impressions
    impressions = Column(Integer, nullable=True, default=0)
    reach = Column(Integer, nullable=True, default=0)
    unique_viewers = Column(Integer, nullable=True, default=0)
    click_through_rate = Column(Float, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    
    # Demographic Data
    audience_demographics = Column(JSONB, nullable=True)
    geographic_data = Column(JSONB, nullable=True)
    device_data = Column(JSONB, nullable=True)
    traffic_sources = Column(JSONB, nullable=True)
    
    # Revenue Metrics
    revenue_cents = Column(Integer, nullable=True, default=0)
    ad_revenue_cents = Column(Integer, nullable=True, default=0)
    subscription_revenue_cents = Column(Integer, nullable=True, default=0)
    donation_revenue_cents = Column(Integer, nullable=True, default=0)
    
    # Performance Scores
    viral_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    trending_score = Column(Float, nullable=True)
    algorithm_score = Column(Float, nullable=True)
    
    # Additional Metrics
    watch_time_minutes = Column(Integer, nullable=True)
    average_view_duration = Column(Float, nullable=True)
    bounce_rate = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    
    # Raw Analytics Data
    raw_analytics = Column(JSONB, nullable=True)
    platform_specific_metrics = Column(JSONB, nullable=True)
    
    # Metadata
    collected_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_source = Column(String(50), nullable=True)
    is_estimated = Column(Boolean, nullable=False, default=False)

# Pydantic Models for API
class PlatformAdapterRequest(BaseModel):
    """Request model for platform adapters"""
    platform_name: str
    platform_type: PlatformType
    api_base_url: str
    api_version: Optional[str] = None
    authentication_method: AuthenticationMethod
    integration_level: IntegrationLevel = IntegrationLevel.STANDARD
    capabilities: Dict[str, Any]
    content_requirements: Dict[str, Any]
    supported_operations: List[str]
    rate_limit_requests_per_hour: int = 1000
    configuration: Optional[Dict[str, Any]] = None

class CredentialRequest(BaseModel):
    """Request model for platform credentials"""
    platform_id: str
    credential_name: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    oauth_data: Optional[Dict[str, Any]] = None
    granted_permissions: Optional[List[str]] = None

class PlatformOperationRequest(BaseModel):
    """Request model for platform operations"""
    platform_id: str
    content_id: Optional[str] = None
    operation_type: str
    request_data: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

class PlatformAdapterManager:
    """Enterprise platform adapter management system"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.cache_ttl = 3600  # 1 hour
        self.http_client = httpx.AsyncClient()
        
    async def register_platform_adapter(
        self,
        adapter_request: PlatformAdapterRequest
    ) -> PlatformAdapter:
        """Register new platform adapter"""



        try:
            # Validate platform requirements
            await self._validate_platform_configuration(adapter_request)
            
            # Create adapter instance
            adapter = PlatformAdapter(
                platform_name=adapter_request.platform_name,
                platform_type=adapter_request.platform_type,
                adapter_version="1.0.0",
                api_base_url=adapter_request.api_base_url,
                api_version=adapter_request.api_version,
                authentication_method=adapter_request.authentication_method,
                integration_level=adapter_request.integration_level,
                capabilities=adapter_request.capabilities,
                content_requirements=adapter_request.content_requirements,
                supported_operations=adapter_request.supported_operations,
                rate_limit_requests_per_hour=adapter_request.rate_limit_requests_per_hour,
                configuration=adapter_request.configuration
            )
            
            # Perform initial health check
            health_status = await self._perform_health_check(adapter)
            adapter.health_score = health_status.get('score', 0.0)
            adapter.last_health_check = datetime.utcnow()
            
            # Save to database
            self.db_session.add(adapter)
            await self.db_session.commit()
            await self.db_session.refresh(adapter)
            
            # Cache adapter data
            await self._cache_adapter(adapter)
            
            logger.info(f"Registered platform adapter: {adapter.platform_name}")
            return adapter
            
        except Exception as e:
            logger.error(f"Error registering platform adapter: {str(e)}")
            await self.db_session.rollback()
            raise
    
    async def add_platform_credentials(
        self,
        user_id: str,
        credential_request: CredentialRequest
    ) -> PlatformCredential:
        """Add platform credentials for user"""



        try:
            # Encrypt sensitive data before storage
            encrypted_data = await self._encrypt_credential_data(credential_request)
            
            # Create credential instance
            credential = PlatformCredential(
                user_id=uuid.UUID(user_id),
                platform_id=uuid.UUID(credential_request.platform_id),
                credential_name=credential_request.credential_name,
                access_token=encrypted_data.get('access_token'),
                refresh_token=encrypted_data.get('refresh_token'),
                api_key=encrypted_data.get('api_key'),
                api_secret=encrypted_data.get('api_secret'),
                oauth_data=encrypted_data.get('oauth_data'),
                granted_permissions=credential_request.granted_permissions
            )
            
            # Validate credentials
            validation_result = await self._validate_credentials(credential)
            credential.is_valid = validation_result.get('valid', False)
            credential.validation_errors = validation_result.get('errors')
            credential.last_validation = datetime.utcnow()
            
            # Get account information
            account_info = await self._fetch_account_info(credential)
            if account_info:
                credential.platform_user_id = account_info.get('user_id')
                credential.platform_username = account_info.get('username')
                credential.account_email = account_info.get('email')
                credential.account_status = account_info.get('status')
                credential.account_tier = account_info.get('tier')
            
            # Save to database
            self.db_session.add(credential)
            await self.db_session.commit()
            await self.db_session.refresh(credential)
            
            logger.info(f"Added credentials for user {user_id} on platform {credential_request.platform_id}")
            return credential
            
        except Exception as e:
            logger.error(f"Error adding platform credentials: {str(e)}")
            await self.db_session.rollback()
            raise
    
    async def execute_platform_operation(
        self,
        user_id: str,
        operation_request: PlatformOperationRequest
    ) -> PlatformOperation:
        """Execute operation on platform"""



        try:
            # Get platform adapter and credentials
            adapter = await self._get_adapter_by_id(operation_request.platform_id)
            credentials = await self._get_user_credentials(user_id, operation_request.platform_id)
            
            if not adapter or not credentials:
                raise ValueError("Platform adapter or credentials not found")
            
            # Check rate limits
            await self._check_rate_limits(adapter)
            
            # Create operation record
            operation = PlatformOperation(
                platform_id=uuid.UUID(operation_request.platform_id),
                user_id=uuid.UUID(user_id),
                content_id=uuid.UUID(operation_request.content_id) if operation_request.content_id else None,
                operation_type=operation_request.operation_type,
                operation_status="pending",
                request_data=operation_request.request_data,
                correlation_id=operation_request.correlation_id
            )
            
            self.db_session.add(operation)
            await self.db_session.commit()
            await self.db_session.refresh(operation)
            
            # Execute the operation
            try:
                result = await self._execute_platform_api_call(
                    adapter=adapter,
                    credentials=credentials,
                    operation=operation
                )
                
                # Update operation with success
                operation.operation_status = "success"
                operation.completed_at = datetime.utcnow()
                operation.duration_ms = int((operation.completed_at - operation.started_at).total_seconds() * 1000)
                operation.response_data = result.get('response')
                operation.platform_content_id = result.get('content_id')
                operation.platform_url = result.get('url')
                operation.response_time_ms = result.get('response_time_ms')
                operation.bytes_transferred = result.get('bytes_transferred')
                
            except Exception as e:
                # Update operation with failure
                operation.operation_status = "failed"
                operation.completed_at = datetime.utcnow()
                operation.duration_ms = int((operation.completed_at - operation.started_at).total_seconds() * 1000)
                operation.error_details = {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                
                # Schedule retry if applicable
                if operation.retry_count < 3:
                    operation.next_retry_at = datetime.utcnow() + timedelta(minutes=2 ** operation.retry_count)
                
                raise
            
            finally:
                await self.db_session.commit()
            
            return operation
            
        except Exception as e:
            logger.error(f"Error executing platform operation: {str(e)}")
            raise
    
    async def get_platform_analytics(
        self,
        user_id: str,
        platform_id: str,
        content_id: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PlatformAnalytics]:
        """Get platform analytics data"""



        try:
            # Build query
            query = self.db_session.query(PlatformAnalytics).filter(
                PlatformAnalytics.user_id == uuid.UUID(user_id),
                PlatformAnalytics.platform_id == uuid.UUID(platform_id)
            )
            
            if content_id:
                query = query.filter(PlatformAnalytics.content_id == uuid.UUID(content_id))
            
            if date_range:
                start_date, end_date = date_range
                query = query.filter(
                    PlatformAnalytics.period_start >= start_date,
                    PlatformAnalytics.period_end <= end_date
                )
            
            analytics = await query.order_by(
                PlatformAnalytics.period_start.desc()
            ).all()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {str(e)}")
            return []
    
    async def update_adapter_health(self, adapter_id: str) -> Dict[str, Any]:
        """Update platform adapter health status"""



        try:
            adapter = await self._get_adapter_by_id(adapter_id)
            if not adapter:
                raise ValueError(f"Adapter {adapter_id} not found")
            
            # Perform health check
            health_status = await self._perform_health_check(adapter)
            
            # Update adapter
            adapter.health_score = health_status.get('score', 0.0)
            adapter.last_health_check = datetime.utcnow()
            adapter.average_response_time = health_status.get('response_time')
            
            if health_status.get('score', 0) < 50:
                adapter.status = AdapterStatus.ERROR
            elif health_status.get('score', 0) < 80:
                adapter.status = AdapterStatus.MAINTENANCE
            else:
                adapter.status = AdapterStatus.ACTIVE
            
            await self.db_session.commit()
            
            # Update cache
            await self._cache_adapter(adapter)
            
            return {
                'adapter_id': adapter_id,
                'health_score': adapter.health_score,
                'status': adapter.status,
                'last_check': adapter.last_health_check
            }
            
        except Exception as e:
            logger.error(f"Error updating adapter health: {str(e)}")
            raise
    
    async def _validate_platform_configuration(self, request: PlatformAdapterRequest):
        """Validate platform adapter configuration"""
        # Validate URL format
        parsed_url = urlparse(request.api_base_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid API base URL")
        
        # Validate required capabilities
        required_fields = ['max_file_size', 'supported_formats', 'api_rate_limit']
        for field in required_fields:
            if field not in request.capabilities:
                raise ValueError(f"Missing required capability: {field}")
        
        # Validate supported operations
        valid_operations = ['upload', 'update', 'delete', 'fetch', 'analytics']
        for operation in request.supported_operations:
            if operation not in valid_operations:
                raise ValueError(f"Invalid operation: {operation}")
    
    async def _perform_health_check(self, adapter: PlatformAdapter) -> Dict[str, Any]:
        """Perform health check on platform adapter"""



        try:
            start_time = datetime.utcnow()
            
            # Attempt API call to platform
            health_url = f"{adapter.api_base_url}/health"
            response = await self.http_client.get(
                health_url,
                timeout=10.0,
                headers={'User-Agent': 'IA-Influencer-Agent/1.0'}
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                score = 100.0
            elif response.status_code < 500:
                score = 75.0
            else:
                score = 25.0
            
            return {
                'score': score,
                'response_time': response_time,
                'status_code': response.status_code,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def _cache_adapter(self, adapter: PlatformAdapter):
        """Cache adapter data in Redis"""



        try:
            cache_key = f"adapter:{adapter.id}"
            adapter_data = {
                'id': str(adapter.id),
                'platform_name': adapter.platform_name,
                'platform_type': adapter.platform_type,
                'status': adapter.status,
                'health_score': adapter.health_score,
                'capabilities': adapter.capabilities,
                'rate_limit_requests_per_hour': adapter.rate_limit_requests_per_hour
            }
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(adapter_data, default=str)
            )
            
        except Exception as e:
            logger.warning(f"Error caching adapter: {str(e)}")
    
    async def _get_adapter_by_id(self, adapter_id: str) -> Optional[PlatformAdapter]:
        """Get adapter by ID with caching"""



        try:
            # Try cache first
            cache_key = f"adapter:{adapter_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # Get full data from database
                adapter_uuid = uuid.UUID(adapter_id)
                adapter = await self.db_session.query(PlatformAdapter).filter(
                    PlatformAdapter.id == adapter_uuid
                ).first()
                return adapter
            
            # Get from database
            adapter_uuid = uuid.UUID(adapter_id)
            adapter = await self.db_session.query(PlatformAdapter).filter(
                PlatformAdapter.id == adapter_uuid
            ).first()
            
            if adapter:
                await self._cache_adapter(adapter)
            
            return adapter
            
        except Exception as e:
            logger.error(f"Error getting adapter by ID: {str(e)}")
            return None
    
    # Additional helper methods would be implemented here for:
    # - _encrypt_credential_data
    # - _validate_credentials
    # - _fetch_account_info
    # - _get_user_credentials
    # - _check_rate_limits
    # - _execute_platform_api_call

# Export classes and functions
__all__ = [
    'PlatformAdapter',
    'PlatformCredential',
    'PlatformOperation',
    'PlatformAnalytics',
    'PlatformAdapterManager',
    'PlatformAdapterRequest',
    'CredentialRequest',
    'PlatformOperationRequest',
    'PlatformType',
    'AdapterStatus',
    'IntegrationLevel',
    'AuthenticationMethod',
    'PlatformCapabilities',
    'ContentRequirements'
]
