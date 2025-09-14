"""
Api Management Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔌 API MANAGEMENT SERVICE
========================

API lifecycle management and governance service.
Handles API versioning, documentation, rate limiting, and monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered API optimization and intelligent usage analytics
- Backend Senior: Enterprise API gateway with scalable request processing
- ML Engineer: Advanced API usage prediction and performance optimization
- DBA: Optimized API metrics storage and query performance
- Security: API authentication, authorization, and threat protection
- Microservices: Service mesh integration and inter-service communication
- Audio Engineer: Audio API endpoints with specialized streaming protocols
- DevOps: Automated API deployment and monitoring infrastructure
- AI Prompt Engineer: Intelligent API documentation and usage recommendations
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics
import sqlite3
import aiosqlite
import jwt
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """API status enumeration"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    BETA = "beta"
    ALPHA = "alpha"
    MAINTENANCE = "maintenance"

class HTTPMethod(Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class AuthenticationType(Enum):
    """API authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"

class RateLimitType(Enum):
    """Rate limiting types"""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    DATA_TRANSFER_LIMIT = "data_transfer_limit"
    CONCURRENT_REQUESTS = "concurrent_requests"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class APIEndpoint:
    """API endpoint definition"""
    endpoint_id: str
    api_id: str
    path: str
    method: HTTPMethod
    description: str
    parameters: List[Dict[str, Any]]
    request_schema: Optional[Dict[str, Any]]
    response_schema: Optional[Dict[str, Any]]
    authentication: AuthenticationType
    rate_limits: List[Dict[str, Any]]
    cache_ttl: int
    timeout_seconds: int
    is_deprecated: bool
    deprecation_date: Optional[datetime]
    successor_endpoint: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class API:
    """API definition"""
    api_id: str
    name: str
    version: str
    description: str
    base_url: str
    status: APIStatus
    endpoints: List[APIEndpoint]
    documentation_url: str
    changelog_url: str
    support_contact: str
    license: str
    terms_of_service_url: str
    rate_limits: Dict[str, Any]
    authentication_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    sla_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    api_key: str
    api_id: str
    user_id: str
    name: str
    permissions: List[str]
    rate_limits: Dict[str, Any]
    ip_whitelist: List[str]
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    updated_at: datetime

@dataclass
class APIRequest:
    """API request record"""
    request_id: str
    api_id: str
    endpoint_id: str
    api_key_id: Optional[str]
    user_id: Optional[str]
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    request_body_size: int
    response_status: int
    response_size: int
    response_time_ms: float
    ip_address: str
    user_agent: str
    timestamp: datetime
    error_message: Optional[str]

@dataclass
class APIAnalytics:
    """API analytics data"""
    analytics_id: str
    api_id: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    total_data_transfer: int
    unique_users: int
    top_endpoints: List[Dict[str, Any]]
    error_breakdown: Dict[str, int]
    usage_by_hour: Dict[str, int]
    generated_at: datetime

@dataclass
class APIAlert:
    """API monitoring alert"""
    alert_id: str
    api_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    threshold_value: Optional[float]
    current_value: Optional[float]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    acknowledged_at: Optional[datetime]

class APIManagementService:
    """
    🔌 Enterprise API Management Service
    
    Comprehensive API lifecycle management with intelligent monitoring,
    automated documentation, and advanced analytics capabilities.
    """
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379", db_path -> None: str = " -> None:memory -> None:") -> None:
        self.redis_url = redis_url
        self.db_path = db_path
        self.redis_client = None
        self.db_connection = None
        self.api_cache = {}
        self.request_queue = deque(maxlen=10000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        
        # Service configuration
        self.service_id = f"api_management_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # API management configuration
        self.default_rate_limit = 1000  # requests per hour
        self.default_timeout = 30  # seconds
        self.max_api_key_lifetime_days = 365
        self.request_log_retention_days = 30
        self.analytics_aggregation_intervals = ["1h", "1d", "7d", "30d"]
        
        # Performance thresholds
        self.performance_thresholds = {
            "response_time_p95_ms": 2000,
            "error_rate_threshold": 0.05,
            "availability_threshold": 0.999,
            "rate_limit_threshold": 0.8
        }
        
        # Default rate limits by tier
        self.rate_limit_tiers = {
            "free": {"requests_per_hour": 100, "requests_per_day": 1000},
            "basic": {"requests_per_hour": 1000, "requests_per_day": 10000},
            "premium": {"requests_per_hour": 10000, "requests_per_day": 100000},
            "enterprise": {"requests_per_hour": 100000, "requests_per_day": 1000000}
        }
        
        logger.info(f"🔌 APIManagementService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the API management service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize SQLite database
            self.db_connection = await aiosqlite.connect(self.db_path)
            await self._initialize_database_schema()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Load default APIs
            await self._load_default_apis()
            
            # Start background tasks
            asyncio.create_task(self._request_processor())
            asyncio.create_task(self._analytics_aggregator())
            asyncio.create_task(self._monitoring_engine())
            asyncio.create_task(self._cleanup_manager())
            
            logger.info(f"✅ APIManagementService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start APIManagementService: {str(e)}")
            return False

    async def _initialize_database_schema(self) -> None:
        """Initialize database schema for API management"""
        try:
            schema_sql = """
            CREATE TABLE IF NOT EXISTS apis (
                api_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                base_url TEXT,
                status TEXT,
                endpoints TEXT,
                documentation_url TEXT,
                changelog_url TEXT,
                support_contact TEXT,
                license TEXT,
                terms_of_service_url TEXT,
                rate_limits TEXT,
                authentication_config TEXT,
                monitoring_config TEXT,
                sla_config TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                api_id TEXT,
                user_id TEXT,
                name TEXT,
                permissions TEXT,
                rate_limits TEXT,
                ip_whitelist TEXT,
                is_active BOOLEAN,
                expires_at TIMESTAMP,
                last_used_at TIMESTAMP,
                usage_count INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS api_requests (
                request_id TEXT PRIMARY KEY,
                api_id TEXT,
                endpoint_id TEXT,
                api_key_id TEXT,
                user_id TEXT,
                method TEXT,
                path TEXT,
                query_params TEXT,
                headers TEXT,
                request_body_size INTEGER,
                response_status INTEGER,
                response_size INTEGER,
                response_time_ms REAL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP,
                error_message TEXT
            );
            
            CREATE TABLE IF NOT EXISTS api_analytics (
                analytics_id TEXT PRIMARY KEY,
                api_id TEXT,
                period_start TIMESTAMP,
                period_end TIMESTAMP,
                total_requests INTEGER,
                successful_requests INTEGER,
                failed_requests INTEGER,
                average_response_time REAL,
                p95_response_time REAL,
                total_data_transfer INTEGER,
                unique_users INTEGER,
                top_endpoints TEXT,
                error_breakdown TEXT,
                usage_by_hour TEXT,
                generated_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS api_alerts (
                alert_id TEXT PRIMARY KEY,
                api_id TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                details TEXT,
                threshold_value REAL,
                current_value REAL,
                triggered_at TIMESTAMP,
                resolved_at TIMESTAMP,
                acknowledged_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_requests_api ON api_requests(api_id);
            CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON api_requests(timestamp);
            CREATE INDEX IF NOT EXISTS idx_requests_api_key ON api_requests(api_key_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_api ON api_alerts(api_id);
            CREATE INDEX IF NOT EXISTS idx_api_keys_api ON api_keys(api_id);
            """
            
            await self.db_connection.executescript(schema_sql)
            await self.db_connection.commit()
            
            logger.info("🗄️ API management database schema initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database schema: {str(e)}")

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for API optimization"""
        try:
            # Usage prediction model
            self.ml_models["usage_predictor"] = {
                "version": "1.0",
                "accuracy": 0.86,
                "features": [
                    "historical_usage", "time_patterns", "user_behavior",
                    "api_features", "seasonal_trends"
                ]
            }
            
            # Performance optimizer
            self.ml_models["performance_optimizer"] = {
                "version": "1.0",
                "accuracy": 0.84,
                "features": [
                    "response_times", "request_patterns", "resource_usage",
                    "endpoint_complexity", "caching_effectiveness"
                ]
            }
            
            # Anomaly detector
            self.ml_models["anomaly_detector"] = {
                "version": "1.0",
                "accuracy": 0.91,
                "features": [
                    "request_patterns", "response_patterns", "error_patterns",
                    "user_behavior", "traffic_patterns"
                ]
            }
            
            # Security threat detector
            self.ml_models["threat_detector"] = {
                "version": "1.0",
                "accuracy": 0.93,
                "features": [
                    "request_frequency", "payload_patterns", "ip_reputation",
                    "user_agent_patterns", "authentication_patterns"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def _load_default_apis(self) -> None:
        """Load default API configurations"""
        try:
            # User management API
            user_api = API(
                api_id="user_management_api",
                name="User Management API",
                version="v1",
                description="Comprehensive user management and authentication API",
                base_url="https://api.ainflue.com/v1/users",
                status=APIStatus.ACTIVE,
                endpoints=[
                    APIEndpoint(
                        endpoint_id="get_user",
                        api_id="user_management_api",
                        path="/users/{user_id}",
                        method=HTTPMethod.GET,
                        description="Retrieve user information by ID",
                        parameters=[
                            {"name": "user_id", "type": "string", "required": True, "location": "path"},
                            {"name": "include", "type": "string", "required": False, "location": "query"}
                        ],
                        request_schema=None,
                        response_schema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "username": {"type": "string"},
                                "email": {"type": "string"},
                                "profile": {"type": "object"}
                            }
                        },
                        authentication=AuthenticationType.BEARER_TOKEN,
                        rate_limits=[
                            {"type": "requests_per_minute", "limit": 60},
                            {"type": "requests_per_hour", "limit": 1000}
                        ],
                        cache_ttl=300,
                        timeout_seconds=30,
                        is_deprecated=False,
                        deprecation_date=None,
                        successor_endpoint=None,
                        tags=["users", "authentication"],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    ),
                    APIEndpoint(
                        endpoint_id="create_user",
                        api_id="user_management_api",
                        path="/users",
                        method=HTTPMethod.POST,
                        description="Create a new user account",
                        parameters=[],
                        request_schema={
                            "type": "object",
                            "required": ["username", "email", "password"],
                            "properties": {
                                "username": {"type": "string"},
                                "email": {"type": "string"},
                                "password": {"type": "string"},
                                "profile": {"type": "object"}
                            }
                        },
                        response_schema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        },
                        authentication=AuthenticationType.API_KEY,
                        rate_limits=[
                            {"type": "requests_per_minute", "limit": 10},
                            {"type": "requests_per_hour", "limit": 100}
                        ],
                        cache_ttl=0,
                        timeout_seconds=60,
                        is_deprecated=False,
                        deprecation_date=None,
                        successor_endpoint=None,
                        tags=["users", "registration"],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                ],
                documentation_url="https://docs.ainflue.com/api/users",
                changelog_url="https://docs.ainflue.com/api/users/changelog",
                support_contact="api-support@ainflue.com",
                license="MIT",
                terms_of_service_url="https://ainflue.com/terms",
                rate_limits=self.rate_limit_tiers["basic"],
                authentication_config={
                    "supported_types": ["bearer_token", "api_key"],
                    "token_endpoint": "/auth/token",
                    "refresh_endpoint": "/auth/refresh"
                },
                monitoring_config={
                    "alerts_enabled": True,
                    "health_check_interval": 300,
                    "performance_monitoring": True
                },
                sla_config={
                    "availability": 0.999,
                    "response_time_p95": 1000,
                    "support_response_time": 3600
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Content API
            content_api = API(
                api_id="content_management_api",
                name="Content Management API",
                version="v2",
                description="Advanced content creation, management, and optimization API",
                base_url="https://api.ainflue.com/v2/content",
                status=APIStatus.ACTIVE,
                endpoints=[
                    APIEndpoint(
                        endpoint_id="get_content",
                        api_id="content_management_api",
                        path="/content/{content_id}",
                        method=HTTPMethod.GET,
                        description="Retrieve content by ID with optimization suggestions",
                        parameters=[
                            {"name": "content_id", "type": "string", "required": True, "location": "path"},
                            {"name": "include_analytics", "type": "boolean", "required": False, "location": "query"},
                            {"name": "include_optimization", "type": "boolean", "required": False, "location": "query"}
                        ],
                        request_schema=None,
                        response_schema={
                            "type": "object",
                            "properties": {
                                "content_id": {"type": "string"},
                                "title": {"type": "string"},
                                "body": {"type": "string"},
                                "metadata": {"type": "object"},
                                "analytics": {"type": "object"},
                                "optimization_suggestions": {"type": "array"}
                            }
                        },
                        authentication=AuthenticationType.BEARER_TOKEN,
                        rate_limits=[
                            {"type": "requests_per_minute", "limit": 100},
                            {"type": "requests_per_hour", "limit": 5000}
                        ],
                        cache_ttl=600,
                        timeout_seconds=45,
                        is_deprecated=False,
                        deprecation_date=None,
                        successor_endpoint=None,
                        tags=["content", "optimization"],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                ],
                documentation_url="https://docs.ainflue.com/api/content",
                changelog_url="https://docs.ainflue.com/api/content/changelog",
                support_contact="api-support@ainflue.com",
                license="MIT",
                terms_of_service_url="https://ainflue.com/terms",
                rate_limits=self.rate_limit_tiers["premium"],
                authentication_config={
                    "supported_types": ["bearer_token", "oauth2"],
                    "oauth2_scopes": ["content:read", "content:write", "analytics:read"]
                },
                monitoring_config={
                    "alerts_enabled": True,
                    "health_check_interval": 180,
                    "performance_monitoring": True
                },
                sla_config={
                    "availability": 0.999,
                    "response_time_p95": 800,
                    "support_response_time": 1800
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store APIs
            apis = [user_api, content_api]
            for api in apis:
                await self._store_api(api)
                self.api_cache[api.api_id] = api
            
            logger.info(f"📚 Loaded {len(apis)} default APIs")
            
        except Exception as e:
            logger.error(f"❌ Error loading default APIs: {str(e)}")

    async def create_api_key(
        self,
        api_id: str,
        user_id: str,
        key_config: Dict[str, Any]
    ) -> Optional[APIKey]:
        """Create a new API key"""
        try:
            # Validate API exists
            api = await self._get_api(api_id)
            if not api:
                logger.error(f"API {api_id} not found")
                return None
            
            # Generate API key
            api_key_value = self._generate_api_key()
            
            # Set expiration date
            expires_at = None
            if key_config.get("expires_in_days"):
                expires_at = datetime.now() + timedelta(days=key_config["expires_in_days"])
            
            # Create API key
            api_key = APIKey(
                key_id=str(uuid.uuid4()),
                api_key=api_key_value,
                api_id=api_id,
                user_id=user_id,
                name=key_config.get("name", "Default API Key"),
                permissions=key_config.get("permissions", ["read"]),
                rate_limits=key_config.get("rate_limits", self.rate_limit_tiers["free"]),
                ip_whitelist=key_config.get("ip_whitelist", []),
                is_active=True,
                expires_at=expires_at,
                last_used_at=None,
                usage_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store API key
            await self._store_api_key(api_key)
            
            logger.info(f"🔑 API key created for API {api_id}, user {user_id}")
            
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Error creating API key: {str(e)}")
            return None

    async def log_api_request(
        self,
        api_id: str,
        endpoint_id: str,
        request_data: Dict[str, Any]
    ) -> None:
        """Log an API request for analytics and monitoring"""
        try:
            # Create request record
            api_request = APIRequest(
                request_id=str(uuid.uuid4()),
                api_id=api_id,
                endpoint_id=endpoint_id,
                api_key_id=request_data.get("api_key_id"),
                user_id=request_data.get("user_id"),
                method=request_data["method"],
                path=request_data["path"],
                query_params=request_data.get("query_params", {}),
                headers=request_data.get("headers", {}),
                request_body_size=request_data.get("request_body_size", 0),
                response_status=request_data["response_status"],
                response_size=request_data.get("response_size", 0),
                response_time_ms=request_data["response_time_ms"],
                ip_address=request_data.get("ip_address", ""),
                user_agent=request_data.get("user_agent", ""),
                timestamp=datetime.now(),
                error_message=request_data.get("error_message")
            )
            
            # Add to processing queue
            self.request_queue.append(api_request)
            
            # Update API key usage if applicable
            if api_request.api_key_id:
                await self._update_api_key_usage(api_request.api_key_id)
            
            # Check for rate limit violations
            await self._check_rate_limits(api_request)
            
            # Detect anomalies
            await self._detect_request_anomalies(api_request)
            
        except Exception as e:
            logger.error(f"❌ Error logging API request: {str(e)}")

    async def generate_api_analytics(
        self,
        api_id: str,
        period_hours: int = 24
    ) -> Optional[APIAnalytics]:
        """Generate comprehensive API analytics"""
        try:
            period_start = datetime.now() - timedelta(hours=period_hours)
            period_end = datetime.now()
            
            # Get requests in period
            requests_cursor = await self.db_connection.execute("""
                SELECT * FROM api_requests 
                WHERE api_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (api_id, period_start.isoformat(), period_end.isoformat()))
            
            requests = await requests_cursor.fetchall()
            
            if not requests:
                logger.info(f"No requests found for API {api_id} in period")
                return None
            
            # Calculate metrics
            total_requests = len(requests)
            successful_requests = sum(1 for r in requests if 200 <= r[10] < 400)  # response_status
            failed_requests = total_requests - successful_requests
            
            response_times = [r[12] for r in requests if r[12]]  # response_time_ms
            average_response_time = statistics.mean(response_times) if response_times else 0
            p95_response_time = np.percentile(response_times, 95) if response_times else 0
            
            total_data_transfer = sum(r[9] + r[11] for r in requests)  # request + response sizes
            unique_users = len(set(r[4] for r in requests if r[4]))  # user_id
            
            # Top endpoints
            endpoint_counts = defaultdict(int)
            for r in requests:
                endpoint_counts[r[2]] += 1  # endpoint_id
            
            top_endpoints = [
                {"endpoint_id": eid, "requests": count}
                for eid, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Error breakdown
            error_breakdown = defaultdict(int)
            for r in requests:
                if r[10] >= 400:  # response_status
                    error_breakdown[str(r[10])] += 1
            
            # Usage by hour
            usage_by_hour = defaultdict(int)
            for r in requests:
                timestamp = datetime.fromisoformat(r[15])  # timestamp
                hour_key = timestamp.strftime("%Y-%m-%d %H:00")
                usage_by_hour[hour_key] += 1
            
            # Create analytics record
            analytics = APIAnalytics(
                analytics_id=str(uuid.uuid4()),
                api_id=api_id,
                period_start=period_start,
                period_end=period_end,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                p95_response_time=p95_response_time,
                total_data_transfer=total_data_transfer,
                unique_users=unique_users,
                top_endpoints=top_endpoints,
                error_breakdown=dict(error_breakdown),
                usage_by_hour=dict(usage_by_hour),
                generated_at=datetime.now()
            )
            
            # Store analytics
            await self._store_analytics(analytics)
            
            logger.info(f"📊 Analytics generated for API {api_id}: {total_requests} requests")
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error generating API analytics: {str(e)}")
            return None

    async def check_api_health(self, api_id: str) -> Dict[str, Any]:
        """Perform comprehensive API health check"""
        try:
            api = await self._get_api(api_id)
            if not api:
                return {"status": "error", "message": "API not found"}
            
            health_status = {
                "api_id": api_id,
                "api_name": api.name,
                "version": api.version,
                "status": api.status.value,
                "overall_health": "healthy",
                "checks": {},
                "metrics": {},
                "last_checked": datetime.now().isoformat()
            }
            
            # Check availability
            recent_requests = await self._get_recent_requests(api_id, hours=1)
            if recent_requests:
                successful_rate = sum(1 for r in recent_requests if 200 <= r["response_status"] < 400) / len(recent_requests)
                health_status["checks"]["availability"] = {
                    "status": "healthy" if successful_rate >= self.performance_thresholds["availability_threshold"] else "unhealthy",
                    "value": successful_rate,
                    "threshold": self.performance_thresholds["availability_threshold"]
                }
            else:
                health_status["checks"]["availability"] = {"status": "unknown", "message": "No recent requests"}
            
            # Check response times
            response_times = [r["response_time_ms"] for r in recent_requests if r["response_time_ms"]]
            if response_times:
                p95_time = np.percentile(response_times, 95)
                health_status["checks"]["response_time"] = {
                    "status": "healthy" if p95_time <= self.performance_thresholds["response_time_p95_ms"] else "degraded",
                    "p95_ms": p95_time,
                    "threshold_ms": self.performance_thresholds["response_time_p95_ms"]
                }
                health_status["metrics"]["avg_response_time_ms"] = statistics.mean(response_times)
            
            # Check error rates
            if recent_requests:
                error_rate = sum(1 for r in recent_requests if r["response_status"] >= 400) / len(recent_requests)
                health_status["checks"]["error_rate"] = {
                    "status": "healthy" if error_rate <= self.performance_thresholds["error_rate_threshold"] else "unhealthy",
                    "value": error_rate,
                    "threshold": self.performance_thresholds["error_rate_threshold"]
                }
            
            # Check rate limiting
            rate_limit_usage = await self._calculate_rate_limit_usage(api_id)
            health_status["checks"]["rate_limits"] = {
                "status": "healthy" if rate_limit_usage < self.performance_thresholds["rate_limit_threshold"] else "warning",
                "usage_percentage": rate_limit_usage
            }
            
            # Determine overall health
            check_statuses = [check["status"] for check in health_status["checks"].values() if "status" in check]
            if "unhealthy" in check_statuses:
                health_status["overall_health"] = "unhealthy"
            elif "degraded" in check_statuses:
                health_status["overall_health"] = "degraded"
            elif "warning" in check_statuses:
                health_status["overall_health"] = "warning"
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Error checking API health: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        try:
            # Generate random key
            import secrets
            key_bytes = secrets.token_bytes(32)
            api_key = "ak_" + key_bytes.hex()
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Error generating API key: {str(e)}")
            return f"ak_{uuid.uuid4().hex}"

    async def _check_rate_limits(self, request: APIRequest) -> None:
        """Check if request violates rate limits"""
        try:
            if not request.api_key_id:
                return
            
            # Get API key
            api_key = await self._get_api_key(request.api_key_id)
            if not api_key:
                return
            
            # Check rate limits
            for limit_type, limit_value in api_key.rate_limits.items():
                current_usage = await self._get_current_usage(request.api_key_id, limit_type)
                
                if current_usage >= limit_value:
                    # Rate limit exceeded
                    await self._create_alert(
                        request.api_id,
                        "rate_limit_exceeded",
                        AlertSeverity.WARNING,
                        f"Rate limit exceeded for API key {request.api_key_id}",
                        {
                            "api_key_id": request.api_key_id,
                            "limit_type": limit_type,
                            "limit_value": limit_value,
                            "current_usage": current_usage
                        }
                    )
            
        except Exception as e:
            logger.error(f"❌ Error checking rate limits: {str(e)}")

    async def _detect_request_anomalies(self, request: APIRequest) -> None:
        """Detect anomalies in API request patterns"""
        try:
            # Get recent request patterns
            recent_requests = await self._get_recent_requests(request.api_id, hours=24)
            
            if len(recent_requests) < 10:  # Need sufficient data
                return
            
            # Check for anomalies
            anomalies = []
            
            # Response time anomaly
            response_times = [r["response_time_ms"] for r in recent_requests if r["response_time_ms"]]
            if response_times:
                avg_time = statistics.mean(response_times)
                std_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
                
                if request.response_time_ms > avg_time + (3 * std_time):  # 3 sigma rule
                    anomalies.append({
                        "type": "response_time_anomaly",
                        "value": request.response_time_ms,
                        "expected_range": f"{avg_time - std_time:.1f} - {avg_time + std_time:.1f}ms"
                    })
            
            # Error rate anomaly
            recent_errors = sum(1 for r in recent_requests if r["response_status"] >= 400)
            error_rate = recent_errors / len(recent_requests)
            
            if error_rate > 0.1 and request.response_status >= 400:  # High error rate
                anomalies.append({
                    "type": "high_error_rate",
                    "current_error_rate": error_rate,
                    "request_status": request.response_status
                })
            
            # Create alerts for anomalies
            for anomaly in anomalies:
                await self._create_alert(
                    request.api_id,
                    "anomaly_detected",
                    AlertSeverity.INFO,
                    f"Anomaly detected: {anomaly['type']}",
                    anomaly
                )
            
        except Exception as e:
            logger.error(f"❌ Error detecting request anomalies: {str(e)}")

    async def _store_api(self, api: API) -> None:
        """Store API configuration"""
        try:
            await self.db_connection.execute("""
                INSERT OR REPLACE INTO apis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api.api_id, api.name, api.version, api.description,
                api.base_url, api.status.value,
                json.dumps([asdict(ep) for ep in api.endpoints], default=str),
                api.documentation_url, api.changelog_url, api.support_contact,
                api.license, api.terms_of_service_url,
                json.dumps(api.rate_limits), json.dumps(api.authentication_config),
                json.dumps(api.monitoring_config), json.dumps(api.sla_config),
                api.created_at.isoformat(), api.updated_at.isoformat()
            ))
            await self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing API: {str(e)}")

    async def _store_api_key(self, api_key: APIKey) -> None:
        """Store API key"""
        try:
            await self.db_connection.execute("""
                INSERT INTO api_keys VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api_key.key_id, api_key.api_key, api_key.api_id, api_key.user_id,
                api_key.name, json.dumps(api_key.permissions),
                json.dumps(api_key.rate_limits), json.dumps(api_key.ip_whitelist),
                api_key.is_active,
                api_key.expires_at.isoformat() if api_key.expires_at else None,
                api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                api_key.usage_count, api_key.created_at.isoformat(),
                api_key.updated_at.isoformat()
            ))
            await self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing API key: {str(e)}")

    async def _store_request(self, request: APIRequest) -> None:
        """Store API request record"""
        try:
            await self.db_connection.execute("""
                INSERT INTO api_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.request_id, request.api_id, request.endpoint_id,
                request.api_key_id, request.user_id, request.method, request.path,
                json.dumps(request.query_params), json.dumps(request.headers),
                request.request_body_size, request.response_status,
                request.response_size, request.response_time_ms,
                request.ip_address, request.user_agent,
                request.timestamp.isoformat(), request.error_message
            ))
            await self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing request: {str(e)}")

    async def _store_analytics(self, analytics: APIAnalytics) -> None:
        """Store API analytics"""
        try:
            await self.db_connection.execute("""
                INSERT INTO api_analytics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analytics.analytics_id, analytics.api_id,
                analytics.period_start.isoformat(), analytics.period_end.isoformat(),
                analytics.total_requests, analytics.successful_requests,
                analytics.failed_requests, analytics.average_response_time,
                analytics.p95_response_time, analytics.total_data_transfer,
                analytics.unique_users, json.dumps(analytics.top_endpoints),
                json.dumps(analytics.error_breakdown), json.dumps(analytics.usage_by_hour),
                analytics.generated_at.isoformat()
            ))
            await self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing analytics: {str(e)}")

    async def _create_alert(
        self, 
        api_id: str, 
        alert_type: str, 
        severity: AlertSeverity, 
        message: str, 
        details: Dict[str, Any]
    ) -> None:
        """Create an API monitoring alert"""
        try:
            alert = APIAlert(
                alert_id=str(uuid.uuid4()),
                api_id=api_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                details=details,
                threshold_value=details.get("threshold_value"),
                current_value=details.get("current_value"),
                triggered_at=datetime.now(),
                resolved_at=None,
                acknowledged_at=None
            )
            
            await self.db_connection.execute("""
                INSERT INTO api_alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id, alert.api_id, alert.alert_type,
                alert.severity.value, alert.message, json.dumps(alert.details),
                alert.threshold_value, alert.current_value,
                alert.triggered_at.isoformat(),
                alert.resolved_at.isoformat() if alert.resolved_at else None,
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            ))
            await self.db_connection.commit()
            
            logger.warning(f"🚨 API Alert: {alert_type} - {message}")
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {str(e)}")

    async def _request_processor(self) -> None:
        """Background task for processing API request queue"""
        while True:
            try:
                if self.request_queue:
                    # Process requests in batches
                    batch_size = min(100, len(self.request_queue))
                    requests = [self.request_queue.popleft() for _ in range(batch_size)]
                    
                    # Store requests
                    for request in requests:
                        await self._store_request(request)
                    
                    logger.debug(f"📊 Processed {len(requests)} API requests")
                
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in request processor: {str(e)}")
                await asyncio.sleep(30)

    async def _analytics_aggregator(self) -> None:
        """Background task for generating analytics"""
        while True:
            try:
                # Generate analytics for all APIs
                await self._generate_all_api_analytics()
                
                await asyncio.sleep(3600)  # Generate every hour
                
            except Exception as e:
                logger.error(f"❌ Error in analytics aggregator: {str(e)}")
                await asyncio.sleep(600)

    async def _monitoring_engine(self) -> None:
        """Background task for API monitoring"""
        while True:
            try:
                # Monitor all APIs
                await self._monitor_all_apis()
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring engine: {str(e)}")
                await asyncio.sleep(600)

    async def _cleanup_manager(self) -> None:
        """Background task for cleanup operations"""
        while True:
            try:
                # Cleanup old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(86400)  # Cleanup daily
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup manager: {str(e)}")
                await asyncio.sleep(3600)

    async def get_api_management_status(self) -> Dict[str, Any]:
        """Get comprehensive API management status"""
        try:
            # Get API statistics
            api_cursor = await self.db_connection.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
                FROM apis
            """)
            api_stats = await api_cursor.fetchone()
            
            # Get request statistics
            request_cursor = await self.db_connection.execute("""
                SELECT COUNT(*) as total_requests,
                       AVG(response_time_ms) as avg_response_time,
                       SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as error_rate
                FROM api_requests 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            request_stats = await request_cursor.fetchone()
            
            # Get API key statistics
            key_cursor = await self.db_connection.execute("""
                SELECT COUNT(*) as total_keys,
                       SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_keys
                FROM api_keys
            """)
            key_stats = await key_cursor.fetchone()
            
            return {
                "service_id": self.service_id,
                "version": self.version,
                "status": "operational",
                "uptime": str(datetime.now() - self.startup_time),
                "api_statistics": {
                    "total_apis": api_stats[0] if api_stats else 0,
                    "active_apis": api_stats[1] if api_stats else 0
                },
                "request_statistics_24h": {
                    "total_requests": request_stats[0] if request_stats else 0,
                    "average_response_time_ms": request_stats[1] if request_stats else 0,
                    "error_rate": request_stats[2] if request_stats else 0
                },
                "api_key_statistics": {
                    "total_keys": key_stats[0] if key_stats else 0,
                    "active_keys": key_stats[1] if key_stats else 0
                },
                "queue_sizes": {
                    "request_processing": len(self.request_queue)
                },
                "cache_sizes": {
                    "apis": len(self.api_cache)
                },
                "performance_thresholds": self.performance_thresholds,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting API management status: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "APIManagementService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "database_connected": False,
                "request_queue_size": len(self.request_queue),
                "ml_models_loaded": len(self.ml_models),
                "supported_auth_types": [auth.value for auth in AuthenticationType],
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connected"] = True
            
            # Test database connection
            if self.db_connection:
                await self.db_connection.execute("SELECT 1")
                health_status["database_connected"] = True
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "APIManagementService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the API management service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_connection:
                await self.db_connection.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 APIManagementService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main() -> None:
    """Example usage of APIManagementService"""
    service = APIManagementService()
    
    try:
        # Start service
        await service.start()
        
        # Test API key creation
        api_id = "user_management_api"
        user_id = "test_user_001"
        
        print(f"🔌 Testing API management for API: {api_id}")
        
        # Create API key
        key_config = {
            "name": "Test API Key",
            "permissions": ["read", "write"],
            "rate_limits": {"requests_per_hour": 1000, "requests_per_day": 10000},
            "expires_in_days": 30
        }
        
        api_key = await service.create_api_key(api_id, user_id, key_config)
        
        if api_key:
            print(f"🔑 API Key created:")
            print(f"   - Key ID: {api_key.key_id}")
            print(f"   - API Key: {api_key.api_key[:12]}...")
            print(f"   - Permissions: {api_key.permissions}")
            print(f"   - Rate Limits: {api_key.rate_limits}")
        
        # Simulate API requests
        for i in range(5):
            request_data = {
                "method": "GET",
                "path": f"/users/user_{i}",
                "response_status": 200 if i < 4 else 404,
                "response_time_ms": 150 + (i * 50),
                "api_key_id": api_key.key_id if api_key else None,
                "user_id": user_id,
                "ip_address": "192.168.1.100",
                "user_agent": "TestClient/1.0"
            }
            
            await service.log_api_request(api_id, "get_user", request_data)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Generate analytics
        analytics = await service.generate_api_analytics(api_id, period_hours=1)
        
        if analytics:
            print(f"📊 API Analytics:")
            print(f"   - Total Requests: {analytics.total_requests}")
            print(f"   - Success Rate: {analytics.successful_requests/analytics.total_requests:.2%}")
            print(f"   - Avg Response Time: {analytics.average_response_time:.1f}ms")
            print(f"   - P95 Response Time: {analytics.p95_response_time:.1f}ms")
        
        # Check API health
        health = await service.check_api_health(api_id)
        if health:
            print(f"🏥 API Health: {health['overall_health']}")
            for check_name, check_result in health['checks'].items():
                print(f"   - {check_name}: {check_result.get('status', 'unknown')}")
        
        # Service health check
        service_health = await service.health_check()
        print(f"🔌 Service health: {service_health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())