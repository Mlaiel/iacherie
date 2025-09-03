"""
FastAPI endpoints for validation criteria testing
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from validation.validator import validate_all_criteria, get_validation_criteria
from validation.performance import validate_api_performance, get_load_test_config
from validation.security import validate_security_compliance
from validation.scalability import validate_scalability_requirements  
from validation.quality import validate_quality_requirements

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validation", tags=["validation"])

@router.get("/", response_model=Dict[str, Any])
async def get_validation_status():
    """
    Get comprehensive validation status for all criteria
    
    Returns validation results for:
    - Performance: API response time, page load, concurrent users, uptime, error rate
    - Security: OWASP Top 10, PCI DSS, GDPR, SOC 2, penetration testing readiness
    - Scalability: Horizontal scaling, auto-scaling, database sharding, CDN, multi-region
    - Quality: Test coverage, critical bugs, code quality, documentation, accessibility
    """
    try:
        validation_results = await validate_all_criteria()
        return JSONResponse(
            content=validation_results,
            status_code=200 if validation_results.get("overall_status") == "PASSED" else 206
        )
    except Exception as e:
        logger.error(f"Validation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/criteria", response_model=Dict[str, Any])
async def get_criteria():
    """Get validation criteria requirements"""
    return get_validation_criteria()

@router.get("/performance", response_model=Dict[str, Any])
async def validate_performance():
    """
    Validate performance criteria:
    - API response time < 200ms
    - Page load time < 3s
    - 10k concurrent users support
    - 99.9% uptime SLA
    - < 1% error rate
    """
    try:
        results = await validate_api_performance()
        return JSONResponse(
            content=results,
            status_code=200 if results.get("api_response_time_valid") and results.get("error_rate_valid") else 206
        )
    except Exception as e:
        logger.error(f"Performance validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance validation failed: {str(e)}")

@router.get("/security", response_model=Dict[str, Any])
async def validate_security():
    """
    Validate security criteria:
    - OWASP Top 10 compliant
    - PCI DSS compliant
    - GDPR compliant
    - SOC 2 ready
    - Penetration tested
    """
    try:
        results = await validate_security_compliance()
        return JSONResponse(
            content=results,
            status_code=200 if results.get("compliance_percentage", 0) >= 100 else 206
        )
    except Exception as e:
        logger.error(f"Security validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Security validation failed: {str(e)}")

@router.get("/scalability", response_model=Dict[str, Any])
async def validate_scalability():
    """
    Validate scalability criteria:
    - Horizontal scaling ready
    - Auto-scaling configured
    - Database sharding ready
    - CDN integrated
    - Multi-region support
    """
    try:
        results = await validate_scalability_requirements()
        return JSONResponse(
            content=results,
            status_code=200 if results.get("scalability_score", 0) >= 100 else 206
        )
    except Exception as e:
        logger.error(f"Scalability validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scalability validation failed: {str(e)}")

@router.get("/quality", response_model=Dict[str, Any])
async def validate_quality():
    """
    Validate quality criteria:
    - 90%+ test coverage
    - 0 critical bugs
    - A+ code quality score
    - 100% documentation
    - AA accessibility compliant
    """
    try:
        results = await validate_quality_requirements()
        return JSONResponse(
            content=results,
            status_code=200 if results.get("all_requirements_met", False) else 206
        )
    except Exception as e:
        logger.error(f"Quality validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quality validation failed: {str(e)}")

@router.get("/load-test-config", response_model=Dict[str, Any])
async def get_load_testing_config():
    """Get configuration for 10k concurrent users load testing"""
    return get_load_test_config()

@router.get("/health", response_model=Dict[str, str])
async def validation_health():
    """Validation service health check"""
    return {
        "status": "healthy",
        "service": "validation",
        "message": "Validation service is operational"
    }