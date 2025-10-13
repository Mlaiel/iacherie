"""
Health Check Routes
Monitor orchestrator and module connectivity
"""
from fastapi import APIRouter
import httpx
import asyncio
from typing import Dict

router = APIRouter()


async def check_module_health(module_name: str, port: int) -> Dict:
    """Check if a module is responding"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://localhost:{port}/health")
            return {
                "module": module_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "port": port,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
            }
    except Exception as e:
        return {
            "module": module_name,
            "status": "unreachable",
            "port": port,
            "error": str(e),
        }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns orchestrator status and checks connectivity to all modules
    """
    # Check all modules concurrently
    module_checks = await asyncio.gather(
        check_module_health("medcare", 8000),
        check_module_health("ia2good", 8001),
        check_module_health("eduverify", 8002),
        return_exceptions=True,
    )
    
    return {
        "orchestrator": "healthy",
        "timestamp": "2025-10-10T00:00:00Z",
        "modules": module_checks,
        "services": {
            "accessibility": "operational",
            "analytics": "operational",
        },
    }


@router.get("/status")
async def get_status():
    """
    Detailed status of orchestrator and all modules
    """
    return {
        "orchestrator": {
            "version": "1.0.0",
            "status": "operational",
            "uptime": "N/A",
        },
        "modules": {
            "medcare": {
                "port": 8000,
                "purpose": "Healthcare AI consultations",
                "endpoints": 8,
            },
            "ia2good": {
                "port": 8001,
                "purpose": "Volunteer humanitarian platform",
                "endpoints": 15,
            },
            "eduverify": {
                "port": 8002,
                "purpose": "Educational content verification",
                "endpoints": 12,
            },
        },
        "shared_services": {
            "accessibility": {
                "features": [
                    "Text-to-Speech",
                    "Speech-to-Text",
                    "Automatic Captions",
                    "Visual Alerts",
                    "Screen Reader Optimization",
                    "Audio Descriptions",
                ],
                "languages_supported": ["fr", "en", "ar", "es", "de", "zh"],
            },
            "analytics": {
                "features": [
                    "Platform Overview",
                    "Accessibility Tracking",
                    "Usage Reports",
                ],
            },
        },
        "future_integrations": {
            "iacherie": {
                "purpose": "644+ languages/dialects support",
                "status": "planned",
            },
            "guardian": {
                "purpose": "Advanced monitoring and alerts",
                "status": "future",
                "reason": "Cost optimization",
            },
        },
    }
