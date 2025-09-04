"""Business API Routes
Consolidated business and monetization functionality including payments, monetization,
collaboration, fingerprinting, protection, licensing, webhooks, alerts, and AI agents.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import json

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monetization.payment_processor import PaymentProcessor
from ...monetization.revenue_calculator import RevenueCalculator
from ...monetization.platform_apis import PlatformAPIsManager
from ...monetization.licensing_manager import LicensingManager
from ...ai_agents.collaboration.matching_engine import CollaborationMatchingEngine
from ...ai_agents.collaboration.compatibility_analyzer import CompatibilityAnalyzer
from ...ai_engine.fingerprinting import fingerprint_engine
from ...protection.content_protector import ContentProtector
from ...ai_agents.text_agent import AITextAgent
from ...ai_agents.moderation_agent import AIModerationAgent

# ========================================
# ENUMS
# ========================================

class PaymentMethod(str, Enum):
    STRIPE_CARD = "stripe_card"
    STRIPE_BANK = "stripe_bank"
    PAYPAL = "paypal"
    WISE_TRANSFER = "wise_transfer"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class CollaborationType(str, Enum):
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_VENTURES = "joint_ventures"
    LICENSING_PARTNERSHIP = "licensing_partnership"
    MENTORSHIP = "mentorship"
    REMIX_COLLABORATION = "remix_collaboration"

class CollaborationStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC = "sync"
    MASTER = "master"
    MECHANICAL = "mechanical"

# ========================================
# PYDANTIC MODELS
# ========================================

# Payment Models
class PaymentRequest(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Field(default=Currency.USD)
    payment_method_id: str
    description: str = Field(..., min_length=1, max_length=500)
    metadata: Optional[Dict[str, Any]] = None

class PayoutRequest(BaseModel):
    payout_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Field(default=Currency.USD)
    destination_method_id: str
    description: str = Field(..., min_length=1, max_length=500)
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")

class PaymentResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: Currency
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

# Monetization Models
class PlatformConnection(BaseModel):
    platform: str = Field(..., regex="^(youtube|spotify|instagram|tiktok|facebook|twitter|patreon|onlyfans)$")
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    channel_id: Optional[str] = None
    account_id: Optional[str] = None
    connection_settings: Optional[Dict[str, Any]] = None

class RevenueStream(BaseModel):
    stream_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str
    content_id: str
    revenue_type: str = Field(..., regex="^(ad_revenue|subscriptions|donations|sponsorships|licensing|merchandise)$")
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", regex="^[A-Z]{3}$")
    date_earned: datetime
    payment_status: str = Field(default="pending", regex="^(pending|processing|paid|failed)$")
    metadata: Optional[Dict[str, Any]] = None

class RevenueReport(BaseModel):
    report_id: str
    user_id: str
    period: str
    total_revenue: Decimal
    platform_breakdown: Dict[str, Decimal]
    top_performing_content: List[Dict[str, Any]]
    payment_summary: Dict[str, Any]
    generated_at: datetime

# Collaboration Models
class CreatorProfile(BaseModel):
    creator_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage_name: str = Field(..., min_length=1, max_length=100)
    genres: List[str] = Field(..., min_items=1, max_items=10)
    skills: List[str] = Field(..., min_items=1, max_items=20)
    skill_levels: Dict[str, SkillLevel]
    bio: str = Field(..., max_length=1000)
    location: Optional[str] = None
    languages: List[str] = Field(default=["english"])
    social_media: Dict[str, str] = Field(default={})
    portfolio_links: List[str] = Field(default=[])
    collaboration_preferences: Dict[str, Any] = Field(default={})
    availability: Dict[str, bool] = Field(default={})
    price_range: Optional[Dict[str, float]] = None

class CollaborationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=2000)
    collaboration_type: CollaborationType
    genres: List[str] = Field(..., min_items=1)
    required_skills: List[str] = Field(..., min_items=1)
    budget_range: Optional[Dict[str, float]] = None
    timeline: Dict[str, str]
    location_requirement: Optional[str] = None
    remote_friendly: bool = Field(default=True)
    experience_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    collaboration_split: Optional[Dict[str, float]] = None

class CollaborationMatch(BaseModel):
    match_id: str
    requester_id: str
    matched_creator_id: str
    collaboration_request_id: str
    compatibility_score: float
    match_reasons: List[str]
    shared_genres: List[str]
    complementary_skills: List[str]
    estimated_success_rate: float
    ai_recommendation: str
    match_created_at: datetime

# Fingerprinting Models
class FingerprintRequest(BaseModel):
    content_id: str
    fingerprint_type: str = Field(..., regex="^(audio|video|image|text)$")
    quality_level: str = Field(default="standard", regex="^(basic|standard|high|premium)$")
    additional_options: Optional[Dict[str, Any]] = None

class FingerprintResponse(BaseModel):
    fingerprint_id: str
    content_id: str
    fingerprint_hash: str
    fingerprint_type: str
    confidence_score: float
    processing_time: float
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class SimilaritySearchRequest(BaseModel):
    query_fingerprint: str
    search_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    content_types: Optional[List[str]] = None
    max_results: int = Field(default=10, ge=1, le=100)

# Protection Models
class ProtectionScanRequest(BaseModel):
    content_id: str
    scan_platforms: List[str] = Field(..., min_items=1)
    scan_depth: str = Field(default="standard", regex="^(basic|standard|deep|comprehensive)$")
    notification_settings: Optional[Dict[str, bool]] = None

class ProtectionAlert(BaseModel):
    alert_id: str
    content_id: str
    violation_type: str
    platform: str
    detected_url: str
    similarity_score: float
    detection_timestamp: datetime
    status: str = Field(..., regex="^(new|investigating|resolved|false_positive)$")
    evidence: Dict[str, Any]

# Licensing Models
class LicensingDeal(BaseModel):
    deal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    licensee_name: str
    license_type: LicenseType
    territory: str = Field(default="worldwide")
    duration_months: int = Field(..., gt=0, le=120)
    total_amount: Decimal = Field(..., gt=0)
    advance_amount: Decimal = Field(default=0)
    royalty_rate: float = Field(..., ge=0, le=100)
    payment_schedule: List[Dict[str, Any]]
    terms_conditions: str

# Webhook Models
class WebhookEndpoint(BaseModel):
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = Field(..., regex=r"^https?://.*")
    events: List[str] = Field(..., min_items=1)
    secret: Optional[str] = None
    is_active: bool = Field(default=True)
    retry_policy: Optional[Dict[str, Any]] = None

class WebhookEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    retry_count: int = Field(default=0)

# Alert Models
class SystemAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str
    priority: AlertPriority
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., max_length=1000)
    source_service: str
    affected_resources: List[str] = Field(default=[])
    metadata: Optional[Dict[str, Any]] = None
    is_resolved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Agent Models
class AIAgentRequest(BaseModel):
    agent_type: str = Field(..., regex="^(text|moderation|analysis|recommendation)$")
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

class AIAgentResponse(BaseModel):
    request_id: str
    agent_type: str
    result: Dict[str, Any]
    confidence_score: float
    processing_time: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

# ========================================
# ROUTER SETUP
# ========================================

business_router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize business components
payment_processor = PaymentProcessor()
revenue_calculator = RevenueCalculator()
platform_apis = PlatformAPIsManager()
licensing_manager = LicensingManager()
collaboration_engine = CollaborationMatchingEngine()
compatibility_analyzer = CompatibilityAnalyzer()
content_protector = ContentProtector()
ai_text_agent = AITextAgent()
ai_moderation_agent = AIModerationAgent()


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
# PAYMENT ENDPOINTS
# ========================================

@business_router.post("/payments/process", response_model=PaymentResponse)
async def process_payment(
    payment_request: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a payment transaction"""
    try:
        # Process payment through payment processor
        result = await payment_processor.process_payment(
            payment_request.dict(),
            current_user["id"]
        )
        
        # Store transaction in database
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO payments 
                (id, user_id, amount, currency, status, payment_method_id, 
                 description, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (payment_request.payment_id, current_user["id"], payment_request.amount,
                 payment_request.currency, result["status"], payment_request.payment_method_id,
                 payment_request.description, payment_request.metadata, datetime.utcnow())
            )
        
        logger.info(f"Payment processed: {payment_request.payment_id} for user {current_user['id']}")
        
        return PaymentResponse(
            payment_id=payment_request.payment_id,
            status=PaymentStatus(result["status"]),
            amount=payment_request.amount,
            currency=payment_request.currency,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=result.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing failed"
        )


@business_router.post("/payments/payout")
async def request_payout(
    payout_request: PayoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request a payout to external account"""
    try:
        # Validate payout eligibility
        balance = await _get_user_balance(current_user["id"])
        if balance < payout_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for payout"
            )
        
        # Process payout
        result = await payment_processor.process_payout(
            payout_request.dict(),
            current_user["id"]
        )
        
        # Store payout request
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO payouts 
                (id, user_id, amount, currency, destination_method_id, 
                 description, priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (payout_request.payout_id, current_user["id"], payout_request.amount,
                 payout_request.currency, payout_request.destination_method_id,
                 payout_request.description, payout_request.priority, "pending", datetime.utcnow())
            )
        
        logger.info(f"Payout requested: {payout_request.payout_id} for user {current_user['id']}")
        
        return {
            "payout_id": payout_request.payout_id,
            "status": "pending",
            "message": "Payout request submitted successfully",
            "estimated_processing_time": "1-3 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payout request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payout request failed"
        )


# ========================================
# MONETIZATION ENDPOINTS
# ========================================

@business_router.post("/monetization/connect-platform")
async def connect_monetization_platform(
    connection: PlatformConnection,
    current_user: dict = Depends(get_current_user)
):
    """Connect to a monetization platform"""
    try:
        # Validate platform credentials
        validation_result = await platform_apis.validate_connection(
            connection.platform,
            connection.dict()
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform credentials: {validation_result['error']}"
            )
        
        # Store platform connection
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO platform_monetization_connections 
                (user_id, platform, api_key, access_token, channel_id, 
                 account_id, connection_settings, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, platform) 
                DO UPDATE SET 
                    api_key = EXCLUDED.api_key,
                    access_token = EXCLUDED.access_token,
                    channel_id = EXCLUDED.channel_id,
                    account_id = EXCLUDED.account_id,
                    connection_settings = EXCLUDED.connection_settings,
                    updated_at = %s
                """,
                (current_user["id"], connection.platform, connection.api_key,
                 connection.access_token, connection.channel_id, connection.account_id,
                 connection.connection_settings, datetime.utcnow(), datetime.utcnow())
            )
        
        logger.info(f"Monetization platform connected: {connection.platform} for user {current_user['id']}")
        
        return {
            "message": f"Successfully connected to {connection.platform}",
            "platform": connection.platform,
            "status": "connected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Platform connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Platform connection failed"
        )


@business_router.post("/monetization/revenue-stream", response_model=RevenueStream)
async def create_revenue_stream(
    revenue_stream: RevenueStream,
    current_user: dict = Depends(get_current_user)
):
    """Create a new revenue stream entry"""
    try:
        # Store revenue stream
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO revenue_streams 
                (id, user_id, platform, content_id, revenue_type, amount, 
                 currency, date_earned, payment_status, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (revenue_stream.stream_id, current_user["id"], revenue_stream.platform,
                 revenue_stream.content_id, revenue_stream.revenue_type, revenue_stream.amount,
                 revenue_stream.currency, revenue_stream.date_earned, revenue_stream.payment_status,
                 revenue_stream.metadata, datetime.utcnow())
            )
        
        logger.info(f"Revenue stream created: {revenue_stream.stream_id} for user {current_user['id']}")
        
        return revenue_stream
        
    except Exception as e:
        logger.error(f"Revenue stream creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Revenue stream creation failed"
        )


@business_router.get("/monetization/revenue-report", response_model=RevenueReport)
async def generate_revenue_report(
    period: str = "monthly",
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive revenue report"""
    try:
        # Calculate revenue metrics
        report_data = await revenue_calculator.generate_report(
            current_user["id"],
            period
        )
        
        report_id = str(uuid.uuid4())
        
        # Store report
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO revenue_reports 
                (id, user_id, period, total_revenue, platform_breakdown, 
                 top_performing_content, payment_summary, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (report_id, current_user["id"], period, report_data["total_revenue"],
                 report_data["platform_breakdown"], report_data["top_performing_content"],
                 report_data["payment_summary"], datetime.utcnow())
            )
        
        logger.info(f"Revenue report generated: {report_id} for user {current_user['id']}")
        
        return RevenueReport(
            report_id=report_id,
            user_id=current_user["id"],
            period=period,
            **report_data,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Revenue report generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Revenue report generation failed"
        )


# ========================================
# COLLABORATION ENDPOINTS
# ========================================

@business_router.post("/collaboration/profile", response_model=CreatorProfile)
async def create_creator_profile(
    profile: CreatorProfile,
    current_user: dict = Depends(get_current_user)
):
    """Create or update creator collaboration profile"""
    try:
        # Store creator profile
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO creator_profiles 
                (id, user_id, stage_name, genres, skills, skill_levels, bio, 
                 location, languages, social_media, portfolio_links, 
                 collaboration_preferences, availability, price_range, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    stage_name = EXCLUDED.stage_name,
                    genres = EXCLUDED.genres,
                    skills = EXCLUDED.skills,
                    skill_levels = EXCLUDED.skill_levels,
                    bio = EXCLUDED.bio,
                    location = EXCLUDED.location,
                    languages = EXCLUDED.languages,
                    social_media = EXCLUDED.social_media,
                    portfolio_links = EXCLUDED.portfolio_links,
                    collaboration_preferences = EXCLUDED.collaboration_preferences,
                    availability = EXCLUDED.availability,
                    price_range = EXCLUDED.price_range,
                    updated_at = %s
                """,
                (profile.creator_id, current_user["id"], profile.stage_name, profile.genres,
                 profile.skills, profile.skill_levels, profile.bio, profile.location,
                 profile.languages, profile.social_media, profile.portfolio_links,
                 profile.collaboration_preferences, profile.availability, profile.price_range,
                 datetime.utcnow(), datetime.utcnow())
            )
        
        logger.info(f"Creator profile created: {profile.creator_id} for user {current_user['id']}")
        
        return profile
        
    except Exception as e:
        logger.error(f"Creator profile creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creator profile creation failed"
        )


@business_router.post("/collaboration/request")
async def create_collaboration_request(
    request: CollaborationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new collaboration request"""
    try:
        # Store collaboration request
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO collaboration_requests 
                (id, user_id, title, description, collaboration_type, genres, 
                 required_skills, budget_range, timeline, location_requirement, 
                 remote_friendly, experience_level, collaboration_split, 
                 additional_requirements, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (request.request_id, current_user["id"], request.title, request.description,
                 request.collaboration_type, request.genres, request.required_skills,
                 request.budget_range, request.timeline, request.location_requirement,
                 request.remote_friendly, request.experience_level, request.collaboration_split,
                 request.additional_requirements, "open", datetime.utcnow())
            )
        
        # Find potential matches
        matches = await collaboration_engine.find_matches(
            request.dict(),
            current_user["id"]
        )
        
        logger.info(f"Collaboration request created: {request.request_id} for user {current_user['id']}")
        
        return {
            "request_id": request.request_id,
            "status": "created",
            "message": "Collaboration request created successfully",
            "potential_matches": len(matches),
            "matches": matches[:5]  # Return top 5 matches
        }
        
    except Exception as e:
        logger.error(f"Collaboration request creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collaboration request creation failed"
        )


@business_router.get("/collaboration/matches", response_model=List[CollaborationMatch])
async def get_collaboration_matches(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get matches for a collaboration request"""
    try:
        # Get collaboration request
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT * FROM collaboration_requests WHERE id = %s AND user_id = %s",
                (request_id, current_user["id"])
            )
            request_data = result.fetchone()
            
            if not request_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Collaboration request not found"
                )
        
        # Find matches using AI engine
        matches = await collaboration_engine.find_matches(
            dict(request_data),
            current_user["id"]
        )
        
        logger.info(f"Collaboration matches retrieved: {len(matches)} for request {request_id}")
        
        return matches
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Collaboration matches retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collaboration matches retrieval failed"
        )


# ========================================
# FINGERPRINTING ENDPOINTS
# ========================================

@business_router.post("/fingerprinting/generate", response_model=FingerprintResponse)
async def generate_fingerprint(
    file: UploadFile = File(...),
    fingerprint_request: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate content fingerprint"""
    try:
        if fingerprint_request:
            request_data = json.loads(fingerprint_request)
            request_obj = FingerprintRequest(**request_data)
        else:
            request_obj = FingerprintRequest(
                content_id=str(uuid.uuid4()),
                fingerprint_type="auto"
            )
        
        # Read file content
        content_data = await file.read()
        
        # Generate fingerprint
        fingerprint_result = await fingerprint_engine.generate_fingerprint(
            content_data,
            file.content_type,
            request_obj.quality_level,
            request_obj.additional_options
        )
        
        fingerprint_id = str(uuid.uuid4())
        
        # Store fingerprint
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO content_fingerprints 
                (id, user_id, content_id, fingerprint_hash, fingerprint_type, 
                 confidence_score, processing_time, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (fingerprint_id, current_user["id"], request_obj.content_id,
                 fingerprint_result["hash"], request_obj.fingerprint_type,
                 fingerprint_result["confidence"], fingerprint_result["processing_time"],
                 fingerprint_result.get("metadata"), datetime.utcnow())
            )
        
        logger.info(f"Fingerprint generated: {fingerprint_id} for user {current_user['id']}")
        
        return FingerprintResponse(
            fingerprint_id=fingerprint_id,
            content_id=request_obj.content_id,
            fingerprint_hash=fingerprint_result["hash"],
            fingerprint_type=request_obj.fingerprint_type,
            confidence_score=fingerprint_result["confidence"],
            processing_time=fingerprint_result["processing_time"],
            created_at=datetime.utcnow(),
            metadata=fingerprint_result.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Fingerprint generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fingerprint generation failed"
        )


@business_router.post("/fingerprinting/search")
async def search_similar_content(
    search_request: SimilaritySearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search for similar content using fingerprint"""
    try:
        # Perform similarity search
        results = await fingerprint_engine.search_similar(
            search_request.query_fingerprint,
            search_request.search_threshold,
            search_request.content_types,
            search_request.max_results,
            current_user["id"]
        )
        
        logger.info(f"Similarity search performed: {len(results)} results for user {current_user['id']}")
        
        return {
            "search_id": str(uuid.uuid4()),
            "query_fingerprint": search_request.query_fingerprint,
            "threshold": search_request.search_threshold,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Similarity search failed"
        )


# ========================================
# PROTECTION ENDPOINTS
# ========================================

@business_router.post("/protection/scan")
async def scan_content_protection(
    scan_request: ProtectionScanRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Scan for content protection violations"""
    try:
        scan_id = str(uuid.uuid4())
        
        # Start protection scan as background task
        background_tasks.add_task(
            _perform_protection_scan,
            scan_id,
            scan_request,
            current_user["id"]
        )
        
        # Store scan request
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO protection_scans 
                (id, user_id, content_id, scan_platforms, scan_depth, 
                 notification_settings, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (scan_id, current_user["id"], scan_request.content_id,
                 scan_request.scan_platforms, scan_request.scan_depth,
                 scan_request.notification_settings, "initiated", datetime.utcnow())
            )
        
        logger.info(f"Protection scan initiated: {scan_id} for user {current_user['id']}")
        
        return {
            "scan_id": scan_id,
            "status": "initiated",
            "message": "Content protection scan started",
            "estimated_completion": "5-15 minutes"
        }
        
    except Exception as e:
        logger.error(f"Protection scan failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Protection scan failed"
        )


@business_router.get("/protection/alerts", response_model=List[ProtectionAlert])
async def get_protection_alerts(
    status: str = "new",
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get content protection alerts"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """
                SELECT * FROM protection_alerts 
                WHERE user_id = %s AND status = %s 
                ORDER BY detection_timestamp DESC 
                LIMIT %s
                """,
                (current_user["id"], status, limit)
            )
            alerts = result.fetchall()
        
        logger.info(f"Protection alerts retrieved: {len(alerts)} for user {current_user['id']}")
        
        return [ProtectionAlert(**dict(alert)) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Protection alerts retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Protection alerts retrieval failed"
        )


# ========================================
# LICENSING ENDPOINTS
# ========================================

@business_router.post("/licensing/deal", response_model=LicensingDeal)
async def create_licensing_deal(
    deal: LicensingDeal,
    current_user: dict = Depends(get_current_user)
):
    """Create a new licensing deal"""
    try:
        # Store licensing deal
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO licensing_deals 
                (id, user_id, content_id, licensee_name, license_type, territory, 
                 duration_months, total_amount, advance_amount, royalty_rate, 
                 payment_schedule, terms_conditions, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (deal.deal_id, current_user["id"], deal.content_id, deal.licensee_name,
                 deal.license_type, deal.territory, deal.duration_months, deal.total_amount,
                 deal.advance_amount, deal.royalty_rate, deal.payment_schedule,
                 deal.terms_conditions, "draft", datetime.utcnow())
            )
        
        logger.info(f"Licensing deal created: {deal.deal_id} for user {current_user['id']}")
        
        return deal
        
    except Exception as e:
        logger.error(f"Licensing deal creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Licensing deal creation failed"
        )


# ========================================
# WEBHOOK ENDPOINTS
# ========================================

@business_router.post("/webhooks/endpoint")
async def create_webhook_endpoint(
    endpoint: WebhookEndpoint,
    current_user: dict = Depends(get_current_user)
):
    """Create a new webhook endpoint"""
    try:
        # Store webhook endpoint
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO webhook_endpoints 
                (id, user_id, url, events, secret, is_active, retry_policy, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (endpoint.endpoint_id, current_user["id"], endpoint.url, endpoint.events,
                 endpoint.secret, endpoint.is_active, endpoint.retry_policy, datetime.utcnow())
            )
        
        logger.info(f"Webhook endpoint created: {endpoint.endpoint_id} for user {current_user['id']}")
        
        return {
            "endpoint_id": endpoint.endpoint_id,
            "message": "Webhook endpoint created successfully",
            "status": "active" if endpoint.is_active else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Webhook endpoint creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook endpoint creation failed"
        )


# ========================================
# ALERT ENDPOINTS
# ========================================

@business_router.get("/alerts/system", response_model=List[SystemAlert])
async def get_system_alerts(
    priority: AlertPriority = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get system alerts for user"""
    try:
        query = "SELECT * FROM system_alerts WHERE user_id = %s"
        params = [current_user["id"]]
        
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            alerts = result.fetchall()
        
        logger.info(f"System alerts retrieved: {len(alerts)} for user {current_user['id']}")
        
        return [SystemAlert(**dict(alert)) for alert in alerts]
        
    except Exception as e:
        logger.error(f"System alerts retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System alerts retrieval failed"
        )


# ========================================
# AI AGENT ENDPOINTS
# ========================================

@business_router.post("/ai-agent/process", response_model=AIAgentResponse)
async def process_ai_request(
    agent_request: AIAgentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process request through AI agents"""
    try:
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Route to appropriate AI agent
        if agent_request.agent_type == "text":
            result = await ai_text_agent.process(agent_request.input_data, agent_request.context)
        elif agent_request.agent_type == "moderation":
            result = await ai_moderation_agent.process(agent_request.input_data, agent_request.context)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported agent type: {agent_request.agent_type}"
            )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Store AI agent interaction
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """
                INSERT INTO ai_agent_interactions 
                (id, user_id, agent_type, input_data, result, confidence_score, 
                 processing_time, context, options, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (request_id, current_user["id"], agent_request.agent_type,
                 agent_request.input_data, result["result"], result["confidence"],
                 processing_time, agent_request.context, agent_request.options, start_time)
            )
        
        logger.info(f"AI agent request processed: {request_id} for user {current_user['id']}")
        
        return AIAgentResponse(
            request_id=request_id,
            agent_type=agent_request.agent_type,
            result=result["result"],
            confidence_score=result["confidence"],
            processing_time=processing_time,
            timestamp=start_time,
            metadata=result.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI agent processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI agent processing failed"
        )


# ========================================
# HELPER FUNCTIONS
# ========================================

async def _get_user_balance(user_id: str) -> Decimal:
    """Get user's current balance"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT balance FROM user_balances WHERE user_id = %s",
                (user_id,)
            )
            balance_row = result.fetchone()
            return balance_row["balance"] if balance_row else Decimal("0.00")
    except Exception:
        return Decimal("0.00")


async def _perform_protection_scan(scan_id: str, scan_request: ProtectionScanRequest, user_id: str):
    """Background task to perform content protection scan"""
    try:
        logger.info(f"Starting protection scan {scan_id} for user {user_id}")
        
        # Perform actual protection scan
        scan_results = await content_protector.scan_platforms(
            scan_request.content_id,
            scan_request.scan_platforms,
            scan_request.scan_depth
        )
        
        # Update scan status
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                "UPDATE protection_scans SET status = %s, completed_at = %s WHERE id = %s",
                ("completed", datetime.utcnow(), scan_id)
            )
            
            # Store any violations found
            for violation in scan_results.get("violations", []):
                await session.execute(
                    """
                    INSERT INTO protection_alerts 
                    (id, user_id, content_id, violation_type, platform, detected_url, 
                     similarity_score, detection_timestamp, status, evidence)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (str(uuid.uuid4()), user_id, scan_request.content_id,
                     violation["type"], violation["platform"], violation["url"],
                     violation["similarity"], datetime.utcnow(), "new", violation["evidence"])
                )
        
        logger.info(f"Protection scan completed: {scan_id}")
        
    except Exception as e:
        logger.error(f"Protection scan failed: {str(e)}")
        # Update scan status to failed
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                "UPDATE protection_scans SET status = %s, error_message = %s WHERE id = %s",
                ("failed", str(e), scan_id)
            )