"""
🔌 MICROSERVICES API ENDPOINTS
================================
API pour contrôler les 454 microservices
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from backend.core.microservices_gateway import microservices_gateway

router = APIRouter()
logger = logging.getLogger(__name__)

class ServiceCallRequest(BaseModel):
    """
        Requête d'appel de service"""
    method: str
    params: Dict[str, Any] = {}

class ServiceResponse(BaseModel):
    """
        Réponse d'un service"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("/microservices/list")
async def list_all_microservices():
    """📋 Liste tous les microservices disponibles"""
    try:
        services_info = microservices_gateway.list_services()
        return {
            "success": True,
            "total_services": services_info["total"],
            "services": services_info["services"],
            "categories": {
                "ai_services": ["content_analysis", "recommendation_engine", "sentiment_analysis"],
                "communication_services": ["chat", "notification", "video_call"],
                "analytics_services": ["real_time_analytics", "predictive_analytics", "business_intelligence"],
                "security_services": ["fraud_detection", "security_monitoring", "compliance"],
                "seo_services": ["seo_optimization", "keyword_research", "content_optimization"],
                "platform_services": ["platform_connector", "platform_analytics", "platform_authentication"]
            }
        }
    except Exception as e:
        logger.error(f"❌ Error listing microservices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microservices/{service_name}/call")
async def call_microservice(service_name: str, request: ServiceCallRequest):
    """🔌 Appelle un microservice spécifique"""
    try:
        result = await microservices_gateway.call_service(
            service_name=service_name,
            method=request.method,
            **request.params
        )

        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "non trouvé" in result.get("error", "") else 500,
                detail=result.get("error", "Unknown error")
            )

        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Service call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/microservices/{service_name}/info")
async def get_service_info(service_name: str):
    """📊 Info sur un microservice spécifique"""
    try:
        services_info = microservices_gateway.list_services()

        
        if service_name not in services_info["services"]:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

        
        return {
            "success": True,
            "service_name": service_name,
            "type": services_info["services"][service_name],
            "status": "ready",
            "available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Service info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/microservices/categories")
async def get_service_categories():
    """🗂️ Liste toutes les catégories de services"""
    return {
        "success": True,
        "total_categories": 6,
        "categories": [
            {
                "name": "AI Services",
                "count": 3,
                "services": [
                    {"id": "content_analysis", "name": "Content Analysis Service"},
                    {"id": "recommendation_engine", "name": "Recommendation Engine"},
                    {"id": "sentiment_analysis", "name": "Sentiment Analysis"}
                ]
            },
            {
                "name": "Communication Services",
                "count": 3,
                "services": [
                    {"id": "chat", "name": "Chat Service"},
                    {"id": "notification", "name": "Notification Service"},
                    {"id": "video_call", "name": "Video Call Service"}
                ]
            },
            {
                "name": "Analytics Services",
                "count": 3,
                "services": [
                    {"id": "real_time_analytics", "name": "Real-time Analytics"},
                    {"id": "predictive_analytics", "name": "Predictive Analytics"},
                    {"id": "business_intelligence", "name": "Business Intelligence"}
                ]
            },
            {
                "name": "Security Services",
                "count": 3,
                "services": [
                    {"id": "fraud_detection", "name": "Fraud Detection"},
                    {"id": "security_monitoring", "name": "Security Monitoring"},
                    {"id": "compliance", "name": "Compliance Service"}
                ]
            },
            {
                "name": "SEO Services",
                "count": 3,
                "services": [
                    {"id": "seo_optimization", "name": "SEO Optimization"},
                    {"id": "keyword_research", "name": "Keyword Research"},
                    {"id": "content_optimization", "name": "Content Optimization"}
                ]
            },
            {
                "name": "Platform Services",
                "count": 3,
                "services": [
                    {"id": "platform_connector", "name": "Platform Connector"},
                    {"id": "platform_analytics", "name": "Platform Analytics"},
                    {"id": "platform_authentication", "name": "Platform Authentication"}
                ]
            }
        ]
    }

@router.get("/microservices/health")
async def check_microservices_health():
    """🏥 Health check de tous les microservices"""
    try:
        services_info = microservices_gateway.list_services()

        
        return {
            "success": True,
            "status": "healthy",
            "total_services": services_info["total"],
            "initialized": microservices_gateway.initialized,
            "services_ready": list(services_info["services"].keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }
