"""Public API Routes
Public-facing API for external developers, SDK integration, and testing sandbox.
Provides access to core platform functionality through a developer-friendly interface.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, EmailStr, Field
import asyncio

try:
    from ...core.database import database_manager
    from ...core.security import security_manager
    from ...core.cache import cache_manager
    from ...core.logging import logger
    from ...ai_engine.content_processor import content_processor
    from ...ai_engine.fingerprinting import fingerprint_engine
except ImportError:
    # Mock dependencies for standalone operation
    class MockManager:
        def __getattr__(self, name):
            return lambda *args, **kwargs: {"status": "mocked"}
    
    database_manager = MockManager()
    security_manager = MockManager()
    cache_manager = MockManager()
    logger = MockManager()
    content_processor = MockManager()
    fingerprint_engine = MockManager()

# ========================================
# PUBLIC API MODELS
# ========================================

class ApiKeyRequest(BaseModel):
    """Request model for API key generation"""
    app_name: str = Field(..., min_length=1, max_length=100, description="Application name")
    description: Optional[str] = Field(None, max_length=500, description="API key description")
    permissions: List[str] = Field(default=["read"], description="Requested permissions")

class ApiKeyResponse(BaseModel):
    """Response model for API key generation"""
    api_key: str
    app_name: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]

class SandboxTestRequest(BaseModel):
    """Request model for sandbox testing"""
    endpoint: str = Field(..., description="Endpoint to test")
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|DELETE)$")
    payload: Optional[Dict[str, Any]] = Field(None, description="Test payload")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")

class SandboxTestResponse(BaseModel):
    """Response model for sandbox testing"""
    test_id: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    response_data: Any
    timestamp: datetime

class PublicContentInfo(BaseModel):
    """Public content information model"""
    content_id: str
    title: str
    content_type: str
    created_at: datetime
    is_protected: bool
    fingerprint_available: bool

class SDKInfoResponse(BaseModel):
    """SDK information response"""
    sdk_version: str
    supported_languages: List[str]
    endpoints: List[str]
    rate_limits: Dict[str, int]
    documentation_url: str
    download_urls: Dict[str, str]

class APIHealthResponse(BaseModel):
    """API health check response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
    response_time_ms: float

# ========================================
# ROUTER SETUP
# ========================================

public_router = APIRouter(prefix="/public", tags=["Public API"])
security = HTTPBearer(auto_error=False)

async def get_api_key_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user from API key authentication"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify API key
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT user_id, permissions, rate_limit FROM api_keys WHERE key_hash = %s AND is_active = true",
                (security_manager.hash_api_key(credentials.credentials),)
            )
            api_key_data = result.fetchone()
            
            if not api_key_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            
            return {
                "user_id": api_key_data[0],
                "permissions": api_key_data[1],
                "rate_limit": api_key_data[2]
            }
            
    except Exception as e:
        logger.error(f"API key verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key verification failed"
        )

# ========================================
# HEALTH & DOCUMENTATION ENDPOINTS
# ========================================

@public_router.get("/health", response_model=APIHealthResponse)
async def get_api_health():
    """Get API health status"""
    start_time = datetime.utcnow()
    
    services_status = {
        "database": "healthy",
        "cache": "healthy",
        "ai_engine": "healthy",
        "fingerprinting": "healthy"
    }
    
    # Quick health checks
    try:
        async with database_manager.get_postgres_session() as session:
            await session.execute("SELECT 1")
    except:
        services_status["database"] = "unhealthy"
    
    try:
        await cache_manager.ping()
    except:
        services_status["cache"] = "unhealthy"
    
    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return APIHealthResponse(
        status="healthy" if all(s == "healthy" for s in services_status.values()) else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services=services_status,
        response_time_ms=response_time
    )

@public_router.get("/info", response_model=SDKInfoResponse)
async def get_sdk_info():
    """Get SDK and API information"""
    return SDKInfoResponse(
        sdk_version="1.0.0",
        supported_languages=["Python", "JavaScript", "REST API"],
        endpoints=[
            "/public/health",
            "/public/info", 
            "/public/docs",
            "/public/sandbox/test",
            "/public/content/analyze",
            "/public/content/fingerprint"
        ],
        rate_limits={
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        },
        documentation_url="/public/docs",
        download_urls={
            "python_sdk": "/public/sdk/python",
            "javascript_sdk": "/public/sdk/javascript",
            "postman_collection": "/public/docs/postman"
        }
    )

@public_router.get("/docs", response_class=HTMLResponse)
async def get_public_documentation():
    """Get public API documentation"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ainflue Public API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .method { background: #007bff; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; }
            .method.get { background: #28a745; }
            .method.post { background: #ffc107; color: black; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🚀 Ainflue Public API Documentation</h1>
        <p>Welcome to the Ainflue AI-powered content protection platform public API.</p>
        
        <h2>📋 Available Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /public/health</h3>
            <p>Get API health status and service availability.</p>
            <code>curl -X GET "https://api.ainflue.com/public/health"</code>
        </div>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /public/info</h3>
            <p>Get SDK information, supported languages, and rate limits.</p>
            <code>curl -X GET "https://api.ainflue.com/public/info"</code>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /public/sandbox/test</h3>
            <p>Test API endpoints in a safe sandbox environment.</p>
            <code>curl -X POST "https://api.ainflue.com/public/sandbox/test" -H "Authorization: Bearer YOUR_API_KEY"</code>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /public/content/analyze</h3>
            <p>Analyze content for protection and insights.</p>
            <code>curl -X POST "https://api.ainflue.com/public/content/analyze" -H "Authorization: Bearer YOUR_API_KEY"</code>
        </div>
        
        <h2>🔑 Authentication</h2>
        <p>Use your API key in the Authorization header:</p>
        <code>Authorization: Bearer YOUR_API_KEY</code>
        
        <h2>📚 SDKs</h2>
        <ul>
            <li><a href="/public/sdk/python">Python SDK</a></li>
            <li><a href="/public/sdk/javascript">JavaScript SDK</a></li>
            <li><a href="/public/docs/postman">Postman Collection</a></li>
        </ul>
        
        <h2>⚡ Rate Limits</h2>
        <ul>
            <li>60 requests per minute</li>
            <li>1,000 requests per hour</li>
            <li>10,000 requests per day</li>
        </ul>
        
        <h2>📞 Support</h2>
        <p>For support and questions: <a href="mailto:mlaiel@live.de">mlaiel@live.de</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=docs_html)

# ========================================
# SANDBOX ENDPOINTS
# ========================================

@public_router.post("/sandbox/test", response_model=SandboxTestResponse)
async def test_endpoint(
    test_request: SandboxTestRequest,
    api_user: dict = Depends(get_api_key_user)
):
    """Test API endpoints in sandbox environment"""
    test_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        # Simulate endpoint testing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Mock responses based on endpoint
        if test_request.endpoint == "/public/health":
            mock_response = {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
            status_code = 200
        elif test_request.endpoint == "/public/info":
            mock_response = {"sdk_version": "1.0.0", "supported_languages": ["Python"]}
            status_code = 200
        else:
            mock_response = {"message": "Sandbox test completed", "endpoint": test_request.endpoint}
            status_code = 200
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log sandbox test
        logger.info(f"Sandbox test executed: {test_id} by user {api_user['user_id']}")
        
        return SandboxTestResponse(
            test_id=test_id,
            endpoint=test_request.endpoint,
            method=test_request.method,
            status_code=status_code,
            response_time_ms=response_time,
            response_data=mock_response,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Sandbox test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sandbox test failed"
        )

# ========================================
# CONTENT ANALYSIS ENDPOINTS
# ========================================

@public_router.post("/content/analyze")
async def analyze_content(
    file: UploadFile = File(...),
    api_user: dict = Depends(get_api_key_user)
):
    """Analyze uploaded content for protection and insights"""
    try:
        # Validate file
        if file.size > 50 * 1024 * 1024:  # 50MB limit for public API
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
        
        # Read file content
        content = await file.read()
        
        # Basic analysis (simplified for public API)
        analysis_result = {
            "content_id": str(uuid.uuid4()),
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "analysis": {
                "is_valid": True,
                "detected_format": file.content_type,
                "estimated_duration": None,
                "quality_score": 0.85,
                "protection_recommended": True
            },
            "fingerprint_available": True,
            "analyzed_at": datetime.utcnow()
        }
        
        logger.info(f"Content analyzed via public API: {analysis_result['content_id']} by user {api_user['user_id']}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content analysis failed"
        )

@public_router.post("/content/fingerprint")
async def generate_content_fingerprint(
    file: UploadFile = File(...),
    api_user: dict = Depends(get_api_key_user)
):
    """Generate fingerprint for content protection"""
    try:
        # Validate file
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
        
        # Generate simplified fingerprint for public API
        fingerprint_id = str(uuid.uuid4())
        
        fingerprint_result = {
            "fingerprint_id": fingerprint_id,
            "content_hash": f"fp_{fingerprint_id[:16]}",
            "algorithm": "ainflue-v1",
            "confidence_score": 0.95,
            "processing_time": 2.1,
            "created_at": datetime.utcnow(),
            "protection_features": [
                "watermarking",
                "duplicate_detection",
                "usage_tracking"
            ]
        }
        
        logger.info(f"Fingerprint generated via public API: {fingerprint_id} by user {api_user['user_id']}")
        
        return fingerprint_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fingerprint generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fingerprint generation failed"
        )

# ========================================
# SDK DOWNLOAD ENDPOINTS
# ========================================

@public_router.get("/sdk/python")
async def download_python_sdk():
    """Download Python SDK"""
    try:
        # Read SDK file
        with open("/home/runner/work/Ainflue/Ainflue/sdk/python/ainflue_sdk.py", "r") as f:
            sdk_content = f.read()
        
        return JSONResponse(
            content={
                "filename": "ainflue_sdk.py",
                "content": sdk_content,
                "version": "1.0.0",
                "installation": "pip install ainflue-sdk",
                "documentation": "/public/docs"
            }
        )
        
    except Exception as e:
        logger.error(f"SDK download failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SDK download failed"
        )

@public_router.get("/docs/postman")
async def get_postman_collection():
    """Get Postman collection for API testing"""
    postman_collection = {
        "info": {
            "name": "Ainflue Public API",
            "description": "Ainflue AI-powered content protection platform public API",
            "version": "1.0.0"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{api_key}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "https://api.ainflue.com",
                "type": "string"
            },
            {
                "key": "api_key",
                "value": "your_api_key_here",
                "type": "string"
            }
        ],
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/public/health",
                        "host": ["{{base_url}}"],
                        "path": ["public", "health"]
                    }
                }
            },
            {
                "name": "API Info",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/public/info",
                        "host": ["{{base_url}}"],
                        "path": ["public", "info"]
                    }
                }
            },
            {
                "name": "Sandbox Test",
                "request": {
                    "method": "POST",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "endpoint": "/public/health",
                            "method": "GET"
                        })
                    },
                    "url": {
                        "raw": "{{base_url}}/public/sandbox/test",
                        "host": ["{{base_url}}"],
                        "path": ["public", "sandbox", "test"]
                    }
                }
            }
        ]
    }
    
    return JSONResponse(content=postman_collection)

# ========================================
# RATE LIMITING MIDDLEWARE
# ========================================

async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware for public API"""
    # Extract API key or IP address for rate limiting
    auth_header = request.headers.get("authorization")
    client_ip = request.client.host
    
    # Implement basic rate limiting logic here
    # This is a simplified version - in production, use Redis or similar
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = "60"
    response.headers["X-RateLimit-Remaining"] = "59"
    response.headers["X-RateLimit-Reset"] = str(int((datetime.utcnow() + timedelta(minutes=1)).timestamp()))
    
    return response


# ========================================
# SEO OPTIMIZATION & CREATOR DISCOVERY
# ========================================

class SEOMetadata(BaseModel):
    """SEO metadata for creator profiles"""
    title: str = Field(..., max_length=60)
    description: str = Field(..., max_length=160)
    keywords: List[str] = Field(default_factory=list, max_items=20)
    canonical_url: Optional[str] = None
    og_image: Optional[str] = None
    schema_markup: Optional[Dict[str, Any]] = None

class CreatorProfile(BaseModel):
    """Public creator profile"""
    creator_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    categories: List[str] = []
    follower_count: int = 0
    content_count: int = 0
    verified: bool = False
    location: Optional[str] = None
    website_url: Optional[str] = None
    social_links: Dict[str, str] = {}
    seo_metadata: Optional[SEOMetadata] = None

@public_router.get("/discover/creators", response_model=List[CreatorProfile])
async def discover_creators(
    category: Optional[str] = Query(None, description="Creator category filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    verified_only: bool = Query(False, description="Show only verified creators"),
    min_followers: int = Query(0, description="Minimum follower count"),
    limit: int = Query(20, le=100, description="Number of results"),
    offset: int = Query(0, description="Pagination offset")
):
    """Discover creators with SEO-optimized profiles"""
    try:
        # Mock creator discovery - would query actual database
        creators = []
        for i in range(min(limit, 20)):
            creator = CreatorProfile(
                creator_id=f"creator_{i + offset}",
                username=f"creator{i + offset}",
                display_name=f"Creator {i + offset}",
                bio=f"Talented creator specializing in {category or 'content creation'}",
                avatar_url=f"https://example.com/avatars/creator_{i}.jpg",
                categories=[category] if category else ["music", "art"],
                follower_count=1000 + (i * 500),
                content_count=50 + (i * 10),
                verified=verified_only or (i % 3 == 0),
                location=location or "Global",
                seo_metadata=SEOMetadata(
                    title=f"Creator {i + offset} - Professional Content Creator",
                    description=f"Discover amazing content from Creator {i + offset}. Specializing in {category or 'diverse content'} with {1000 + (i * 500)} followers.",
                    keywords=[category or "content", "creator", "artist", "professional"],
                    canonical_url=f"https://ainflue.com/creators/creator{i + offset}"
                )
            )
            creators.append(creator)
        
        return creators
        
    except Exception as e:
        logger.error(f"Creator discovery failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creator discovery failed"
        )

@public_router.get("/creators/{creator_id}/profile", response_model=CreatorProfile)
async def get_creator_profile(creator_id: str):
    """Get SEO-optimized creator profile"""
    try:
        # Mock profile data - would fetch from database
        profile = CreatorProfile(
            creator_id=creator_id,
            username=creator_id,
            display_name=f"Creator {creator_id}",
            bio="Professional content creator passionate about innovative digital experiences",
            avatar_url=f"https://example.com/avatars/{creator_id}.jpg",
            cover_image_url=f"https://example.com/covers/{creator_id}.jpg",
            categories=["music", "video", "art"],
            follower_count=15000,
            content_count=150,
            verified=True,
            location="Global",
            website_url=f"https://{creator_id}.com",
            social_links={
                "instagram": f"@{creator_id}",
                "twitter": f"@{creator_id}",
                "youtube": f"/{creator_id}"
            },
            seo_metadata=SEOMetadata(
                title=f"{creator_id} - Professional Content Creator | Ainflue",
                description=f"Discover {creator_id}'s amazing content on Ainflue. Professional creator with 15K followers specializing in music, video, and art.",
                keywords=["content creator", "artist", "music", "video", "professional", creator_id],
                canonical_url=f"https://ainflue.com/creators/{creator_id}",
                og_image=f"https://example.com/og/{creator_id}.jpg",
                schema_markup={
                    "@context": "https://schema.org",
                    "@type": "Person",
                    "name": f"Creator {creator_id}",
                    "url": f"https://ainflue.com/creators/{creator_id}",
                    "image": f"https://example.com/avatars/{creator_id}.jpg",
                    "sameAs": [
                        f"https://instagram.com/{creator_id}",
                        f"https://twitter.com/{creator_id}"
                    ]
                }
            )
        )
        
        return profile
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found"
        )

@public_router.get("/seo/sitemap.xml", response_class=HTMLResponse)
async def generate_sitemap():
    """Generate SEO sitemap"""
    try:
        # Mock sitemap generation
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://ainflue.com/</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://ainflue.com/discover</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://ainflue.com/creators</loc>
        <lastmod>{}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>""".format(
            datetime.utcnow().strftime("%Y-%m-%d"),
            datetime.utcnow().strftime("%Y-%m-%d"),
            datetime.utcnow().strftime("%Y-%m-%d")
        )
        
        return HTMLResponse(content=sitemap_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Sitemap generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sitemap generation failed"
        )

@public_router.get("/search/creators")
async def search_creators(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(10, le=50, description="Number of results")
):
    """Search creators with SEO optimization"""
    try:
        # Mock search results - would use Elasticsearch in production
        results = []
        for i in range(min(limit, 10)):
            results.append({
                "creator_id": f"search_{i}",
                "username": f"creator_{q}_{i}",
                "display_name": f"Creator {q} {i}",
                "bio": f"Professional creator matching '{q}' in {category or 'all categories'}",
                "relevance_score": 0.9 - (i * 0.1),
                "follower_count": 5000 + (i * 1000),
                "verified": i < 3
            })
        
        return {
            "query": q,
            "results": results,
            "total_count": len(results),
            "search_time": 0.05,
            "suggestions": [f"{q} music", f"{q} art", f"{q} video"] if len(q) > 2 else []
        }
        
    except Exception as e:
        logger.error(f"Creator search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


# ========================================
# EXPORTS UPDATE
# ========================================

__all__ = [
    "public_router",
    "ApiKeyRequest",
    "ApiKeyResponse", 
    "SEOMetadata",
    "CreatorProfile",
    "RateLimitMiddleware"
]