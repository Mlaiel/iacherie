"""Core API Routes
Consolidated core platform functionality including authentication, content management, 
uploads, analytics, monitoring, platform integrations, and compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import bcrypt

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...ai_engine.content_processor import content_processor
from ...ai_engine.fingerprinting import fingerprint_engine
from ...ai_engine.vector_database import vector_database
from ...ai_engine.content_analyzer import content_analyzer

# ========================================
# AUTHENTICATION ROUTES
# ========================================

# Pydantic models for authentication
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    creator_type: str = Field(..., regex="^(musician|blogger|photographer|influencer|comedian|writer|other)$")
    terms_accepted: bool = Field(..., description="Must accept terms of service")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_data: Dict[str, Any]


class UserProfile(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    creator_type: str
    subscription_tier: str
    is_verified: bool
    created_at: datetime
    permissions: List[str]


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ========================================
# CONTENT MANAGEMENT ROUTES
# ========================================

class ContentMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    target_platforms: Optional[List[str]] = []


class ContentResponse(BaseModel):
    content_id: str
    user_id: str
    title: str
    description: Optional[str]
    content_type: str
    file_size: int
    status: str
    fingerprint_id: Optional[str]
    created_at: datetime
    analysis_data: Optional[Dict[str, Any]] = None


# ========================================
# ANALYTICS ROUTES
# ========================================

class AnalyticsQuery(BaseModel):
    metric_types: List[str]
    start_date: datetime
    end_date: datetime
    platforms: Optional[List[str]] = None
    content_ids: Optional[List[str]] = None
    granularity: str = Field(default="daily", regex="^(hourly|daily|weekly|monthly)$")


class AnalyticsResponse(BaseModel):
    query_id: str
    metrics: Dict[str, Any]
    generated_at: datetime
    data_points: List[Dict[str, Any]]
    summary: Dict[str, Any]


# ========================================
# MONITORING ROUTES  
# ========================================

class SystemHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]
    overall_health: float
    uptime: str
    version: str


class MetricsResponse(BaseModel):
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_times: Dict[str, float]


# ========================================
# PLATFORM INTEGRATION ROUTES
# ========================================

class PlatformCredentials(BaseModel):
    platform: str = Field(..., regex="^(youtube|spotify|instagram|tiktok|facebook|twitter)$")
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None


class PlatformConnection(BaseModel):
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[List[str]] = None


# ========================================
# GDPR COMPLIANCE ROUTES
# ========================================

class DataExportRequest(BaseModel):
    data_types: List[str] = Field(..., description="Types of data to export")
    format: str = Field(default="json", regex="^(json|csv|xml)$")
    email_delivery: bool = Field(default=True)


class DataDeletionRequest(BaseModel):
    confirm_deletion: bool = Field(..., description="Must confirm data deletion")
    keep_analytics: bool = Field(default=False)
    reason: Optional[str] = None


class ConsentUpdate(BaseModel):
    consent_type: str = Field(..., regex="^(marketing|analytics|cookies|data_processing)$")
    granted: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ========================================
# ROUTER SETUP
# ========================================

# Create main core API router
core_router = APIRouter()
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token
        payload = security_manager.jwt_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from cache or database
        cache_key = f"user:{user_id}"
        cached_user = await cache_manager.get(cache_key)
        
        if cached_user:
            return cached_user
        
        # Fetch from database
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = true",
                (user_id,)
            )
            user = result.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            user_data = dict(user)
            await cache_manager.set(cache_key, user_data, ttl=300)
            return user_data
            
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@core_router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """Register a new user account"""
    try:
        # Validate terms acceptance
        if not user_data.terms_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Terms of service must be accepted"
            )
        
        # Check if user already exists
        async with database_manager.get_postgres_session() as session:
            existing_user = await session.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user_data.email, user_data.username)
            )
            
            if existing_user.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email or username already exists"
                )
            
            # Hash password
            hashed_password = security_manager.password_manager.hash_password(user_data.password)
            
            # Create user
            user_id = security_manager.password_manager.generate_secure_token(16)
            tenant_id = security_manager.multitenant_manager.get_tenant_id(user_id)
            
            await session.execute(
                """
                INSERT INTO users 
                (id, email, username, password_hash, first_name, last_name, 
                 creator_type, tenant_id, created_at, is_verified, subscription_tier)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, user_data.email, user_data.username, hashed_password,
                 user_data.first_name, user_data.last_name, user_data.creator_type,
                 tenant_id, datetime.utcnow(), False, "free")
            )
            
            # Generate tokens
            access_token = security_manager.jwt_manager.create_access_token(
                data={"sub": user_id, "email": user_data.email}
            )
            refresh_token = security_manager.jwt_manager.create_refresh_token(
                data={"sub": user_id}
            )
            
            # Cache user data
            user_cache_data = {
                "id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "creator_type": user_data.creator_type,
                "subscription_tier": "free",
                "is_verified": False,
                "permissions": await _get_user_permissions("free")
            }
            
            await cache_manager.set(f"user:{user_id}", user_cache_data, ttl=3600)
            
            logger.info(f"New user registered: {user_data.email}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,
                user_data=user_cache_data
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@core_router.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE email = %s AND is_active = true",
                (login_data.email,)
            )
            user = result.fetchone()
            
            if not user or not security_manager.password_manager.verify_password(
                login_data.password, user["password_hash"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Generate tokens
            access_token = security_manager.jwt_manager.create_access_token(
                data={"sub": user["id"], "email": user["email"]}
            )
            refresh_token = security_manager.jwt_manager.create_refresh_token(
                data={"sub": user["id"]}
            )
            
            # Cache user data
            user_cache_data = {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "creator_type": user["creator_type"],
                "subscription_tier": user["subscription_tier"],
                "is_verified": user["is_verified"],
                "permissions": await _get_user_permissions(user["subscription_tier"])
            }
            
            await cache_manager.set(f"user:{user['id']}", user_cache_data, ttl=3600)
            
            logger.info(f"User logged in: {login_data.email}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,
                user_data=user_cache_data
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@core_router.get("/auth/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        user_id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        creator_type=current_user["creator_type"],
        subscription_tier=current_user["subscription_tier"],
        is_verified=current_user["is_verified"],
        created_at=current_user.get("created_at", datetime.utcnow()),
        permissions=current_user.get("permissions", [])
    )


@core_router.post("/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user and invalidate tokens"""
    try:
        user_id = current_user["id"]
        cache_key = f"user:{user_id}"
        await cache_manager.delete(cache_key)
        
        logger.info(f"User logged out: {user_id}")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# ========================================
# CONTENT MANAGEMENT ENDPOINTS
# ========================================

@core_router.post("/content/upload", response_model=ContentResponse)
async def upload_content(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process content file"""
    try:
        import json
        metadata_obj = json.loads(metadata)
        content_metadata = ContentMetadata(**metadata_obj)
        
        # Validate file
        if file.size > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 100MB"
            )
        
        # Generate content ID
        content_id = str(uuid.uuid4())
        
        # Process file
        content_data = await file.read()
        
        # Analyze content
        analysis_result = await content_analyzer.analyze_content(
            content_data, file.content_type, content_metadata.dict()
        )
        
        # Generate fingerprint
        fingerprint_result = await fingerprint_engine.generate_fingerprint(
            content_data, file.content_type
        )
        
        # Store in database
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO content 
                (id, user_id, title, description, content_type, file_size, 
                 fingerprint_id, status, created_at, analysis_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (content_id, current_user["id"], content_metadata.title,
                 content_metadata.description, file.content_type, file.size,
                 fingerprint_result.get("fingerprint_id"), "processed",
                 datetime.utcnow(), analysis_result)
            )
        
        logger.info(f"Content uploaded: {content_id} by user {current_user['id']}")
        
        return ContentResponse(
            content_id=content_id,
            user_id=current_user["id"],
            title=content_metadata.title,
            description=content_metadata.description,
            content_type=file.content_type,
            file_size=file.size,
            status="processed",
            fingerprint_id=fingerprint_result.get("fingerprint_id"),
            created_at=datetime.utcnow(),
            analysis_data=analysis_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content upload failed"
        )


@core_router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get content details"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT * FROM content WHERE id = %s AND user_id = %s",
                (content_id, current_user["id"])
            )
            content = result.fetchone()
            
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
            
            return ContentResponse(**dict(content))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )


# ========================================
# ANALYTICS ENDPOINTS
# ========================================

@core_router.post("/analytics/query", response_model=AnalyticsResponse)
async def query_analytics(
    query: AnalyticsQuery,
    current_user: dict = Depends(get_current_user)
):
    """Query analytics data"""
    try:
        query_id = str(uuid.uuid4())
        
        # Process analytics query
        metrics_data = {}
        data_points = []
        
        # Mock analytics data - in production this would query real analytics
        for metric_type in query.metric_types:
            metrics_data[metric_type] = {
                "total": 1000,
                "average": 50.5,
                "trend": "increasing"
            }
        
        summary = {
            "total_metrics": len(query.metric_types),
            "date_range": f"{query.start_date} to {query.end_date}",
            "platforms_analyzed": len(query.platforms or [])
        }
        
        logger.info(f"Analytics query processed: {query_id} for user {current_user['id']}")
        
        return AnalyticsResponse(
            query_id=query_id,
            metrics=metrics_data,
            generated_at=datetime.utcnow(),
            data_points=data_points,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Analytics query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics query failed"
        )


# ========================================
# MONITORING ENDPOINTS
# ========================================

@core_router.get("/monitoring/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get system health status"""
    try:
        # Mock health check - in production this would check real services
        services = {
            "database": {"status": "healthy", "response_time": 5.2},
            "cache": {"status": "healthy", "response_time": 1.1},
            "ai_engine": {"status": "healthy", "response_time": 15.3},
            "fingerprinting": {"status": "healthy", "response_time": 8.7}
        }
        
        overall_health = sum(1 for s in services.values() if s["status"] == "healthy") / len(services)
        
        return SystemHealthResponse(
            status="healthy" if overall_health > 0.8 else "degraded",
            timestamp=datetime.utcnow(),
            services=services,
            overall_health=overall_health,
            uptime="99.9%",
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@core_router.get("/monitoring/metrics", response_model=MetricsResponse)
async def get_system_metrics(current_user: dict = Depends(get_current_user)):
    """Get system performance metrics"""
    try:
        # Mock metrics - in production this would get real system metrics
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            cpu_usage=45.2,
            memory_usage=67.8,
            disk_usage=23.4,
            network_io={"inbound": 1234.5, "outbound": 987.6},
            active_connections=156,
            response_times={
                "api": 125.3,
                "database": 8.7,
                "cache": 2.1
            }
        )
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics retrieval failed"
        )


# ========================================
# PLATFORM INTEGRATION ENDPOINTS
# ========================================

@core_router.post("/platforms/connect")
async def connect_platform(
    connection: PlatformConnection,
    current_user: dict = Depends(get_current_user)
):
    """Connect to a social media platform"""
    try:
        # Store platform connection
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO platform_connections 
                (user_id, platform, access_token, refresh_token, expires_at, scope, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, platform) 
                DO UPDATE SET 
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    expires_at = EXCLUDED.expires_at,
                    scope = EXCLUDED.scope,
                    updated_at = %s
                """,
                (current_user["id"], connection.platform, connection.access_token,
                 connection.refresh_token, connection.expires_at, connection.scope,
                 datetime.utcnow(), datetime.utcnow())
            )
        
        logger.info(f"Platform connected: {connection.platform} for user {current_user['id']}")
        
        return {"message": f"Successfully connected to {connection.platform}"}
        
    except Exception as e:
        logger.error(f"Platform connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Platform connection failed"
        )


# ========================================
# GDPR COMPLIANCE ENDPOINTS
# ========================================

@core_router.post("/gdpr/export")
async def request_data_export(
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Request data export for GDPR compliance"""
    try:
        export_id = str(uuid.uuid4())
        
        # Add background task to process export
        background_tasks.add_task(
            _process_data_export,
            export_id,
            current_user["id"],
            request.data_types,
            request.format,
            request.email_delivery
        )
        
        logger.info(f"Data export requested: {export_id} for user {current_user['id']}")
        
        return {
            "export_id": export_id,
            "message": "Data export request received. You will be notified when ready.",
            "estimated_time": "24-48 hours"
        }
        
    except Exception as e:
        logger.error(f"Data export request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data export request failed"
        )


@core_router.post("/gdpr/delete")
async def request_data_deletion(
    request: DataDeletionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request account and data deletion"""
    try:
        if not request.confirm_deletion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data deletion must be explicitly confirmed"
            )
        
        deletion_id = str(uuid.uuid4())
        
        # Store deletion request
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO data_deletion_requests 
                (id, user_id, keep_analytics, reason, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (deletion_id, current_user["id"], request.keep_analytics,
                 request.reason, "pending", datetime.utcnow())
            )
        
        logger.info(f"Data deletion requested: {deletion_id} for user {current_user['id']}")
        
        return {
            "deletion_id": deletion_id,
            "message": "Data deletion request received. Processing will begin within 30 days as required by GDPR.",
            "contact_email": "privacy@ainflue.com"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data deletion request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data deletion request failed"
        )


# ========================================
# HELPER FUNCTIONS
# ========================================

async def _get_user_permissions(subscription_tier: str) -> list:
    """Get user permissions based on subscription tier"""
    base_permissions = ["content:create", "content:read", "protection:basic"]
    
    if subscription_tier == "premium":
        base_permissions.extend([
            "protection:advanced", "analytics:detailed", "collaboration:unlimited"
        ])
    elif subscription_tier == "professional":
        base_permissions.extend([
            "protection:advanced", "analytics:detailed", "collaboration:unlimited",
            "api:full_access", "priority_support"
        ])
    
    return base_permissions


async def _process_data_export(export_id: str, user_id: str, data_types: List[str], 
                              format: str, email_delivery: bool):
    """Background task to process data export"""
    try:
        # Mock data export processing
        logger.info(f"Processing data export {export_id} for user {user_id}")
        
        # In production, this would:
        # 1. Collect user data from various sources
        # 2. Format according to requested format
        # 3. Create downloadable archive
        # 4. Send email notification
        
        # Update export status
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                "UPDATE data_export_requests SET status = %s, completed_at = %s WHERE id = %s",
                ("completed", datetime.utcnow(), export_id)
            )
        
        logger.info(f"Data export completed: {export_id}")
        
    except Exception as e:
        logger.error(f"Data export processing failed: {str(e)}")
        # Update status to failed
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                "UPDATE data_export_requests SET status = %s, error_message = %s WHERE id = %s",
                ("failed", str(e), export_id)
            )