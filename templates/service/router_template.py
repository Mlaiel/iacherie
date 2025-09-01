"""{{service_name}} API Routes for Ainflue Platform
FastAPI router for {{service_name}} service endpoints

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from services.{{service_name_lower}}_service import (
    {{service_name}}Service,
    {{service_name}}Request,
    {{service_name}}Response,
    create_{{service_name_lower}}_service
)
from core.security import get_current_user
from core.rate_limiter import rate_limit
from utils.logging import get_logger


logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/{{service_name_lower}}",
    tags=["{{service_name}}"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/process", response_model={{service_name}}Response)
@rate_limit(requests_per_minute=60)
async def process_{{service_name_lower}}(
    request: {{service_name}}Request,
    service: {{service_name}}Service = Depends(create_{{service_name_lower}}_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> {{service_name}}Response:
    """
    Process {{service_name}} request
    
    This endpoint processes {{service_name}} requests with the following features:
    - Input validation
    - Rate limiting
    - User authentication
    - Error handling
    """
    try:
        logger.info(f"{{service_name}} process request from user {current_user.get('id')}")
        
        # Process the request
        response = await service.process(request)
        
        logger.info(f"{{service_name}} processing completed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in {{service_name}} processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for {{service_name}} service
    """
    return {
        "service": "{{service_name}}",
        "status": "healthy",
        "timestamp": "{{created_date}}"
    }


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """
    Get service information
    """
    return {
        "name": "{{service_name}}",
        "version": "1.0.0",
        "description": "{{service_description}}",
        "author": "{{author_name}}",
        "endpoints": [
            {"path": "/process", "method": "POST", "description": "Process {{service_name}} request"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/info", "method": "GET", "description": "Service information"}
        ]
    }