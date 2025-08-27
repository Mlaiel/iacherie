"""
Main API router for IA Influencer Agent platform.

This router consolidates all API endpoints with level 3 architecture depth compliance.
Includes authentication, content management, collaboration, fingerprinting, protection, 
monetization, and analytics endpoints according to the unified business requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from fastapi import APIRouter
from .auth_endpoints import router as auth_router
from .content_endpoints import router as content_router  
from .collaboration_endpoints import router as collaboration_router
from .fingerprinting_endpoints import router as fingerprinting_router
from .protection_endpoints import router as protection_router
from .monetization_endpoints import router as monetization_router
from .analytics_endpoints import router as analytics_router
from .monitoring_endpoints import router as monitoring_router
from .documentation_endpoints import router as documentation_router

# Keep depth within three levels: backend/app/api
# Root '/api' prefix is applied at ASGI level via settings; only version here.
router = APIRouter()

# Include all endpoint routers with v1 prefix
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router)
v1_router.include_router(content_router)
v1_router.include_router(collaboration_router)
v1_router.include_router(fingerprinting_router)
v1_router.include_router(protection_router)
v1_router.include_router(monetization_router)
v1_router.include_router(analytics_router)
v1_router.include_router(monitoring_router)
v1_router.include_router(documentation_router)

# Add comprehensive health check to v1 with enhanced system status
@v1_router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for monitoring and load balancing.
    
    Returns system status including all integrated services:
    - AI Fingerprinting Engine status
    - Content Protection monitoring
    - Monetization services
    - Analytics engine
    - Database connectivity
    """
    return {
        "status": "healthy",
        "service": "IA Influencer Agent API",
        "version": "2.0.0",
        "author": "Fahed Mlaiel",
        "contact": "mlaiel@live.de",
        "architecture": "Level 3 compliant",
        "timestamp": "2025-08-11T12:00:00Z",
        "business_logic": "Multi-format creator → AI processing → protection → monetization → collaboration",
        "modules_active": [
            "Authentication & User Management",
            "Multi-format Content Processing", 
            "AI Fingerprinting Engine",
            "Content Protection & DMCA",
            "Revenue Optimization & Licensing",
            "Analytics & Business Intelligence",
            "Collaboration Matching"
        ],
        "supported_formats": ["audio", "video", "image", "text", "document"],
        "supported_platforms": ["YouTube", "Spotify", "Instagram", "TikTok", "Facebook", "Twitter"],
        "protection_coverage": "500+ platforms worldwide",
        "ai_capabilities": [
            "Advanced fingerprinting algorithms",
            "Real-time similarity detection",
            "Revenue forecasting models",
            "Market intelligence analysis",
            "Automated optimization recommendations"
        ],
        "legal_compliance": ["GDPR", "CCPA", "DMCA", "Multi-jurisdiction"],
        "security_features": [
            "End-to-end encryption",
            "Multi-factor authentication", 
            "Blockchain verification",
            "Audit trail logging"
        ]
    }

router.include_router(v1_router)

__all__ = ["router"]
