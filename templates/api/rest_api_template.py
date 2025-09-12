"""{{api_name}} REST API Template for Ainflue Platform
{{api_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path, Body
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user, verify_permissions
from core.rate_limiting import rate_limit
from core.caching import cache_response, invalidate_cache
from core.validation import validate_request
from core.logging import log_api_call
from utils.exceptions import APIException, ValidationException
from utils.pagination import PaginationParams, PaginatedResponse
from utils.filtering import FilterParams
from utils.sorting import SortParams
from monitoring.api_metrics import APIMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


class ResponseStatus(Enum):
    """Response status types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class {{api_name}}CreateRequest(BaseModel):
    """Request model for creating {{resource_name}}"""
    name: str = Field(..., description="Name of the {{resource_name}}")
    description: Optional[str] = Field(None, description="Description of the {{resource_name}}")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Example {{resource_name}}",
                "description": "This is an example {{resource_name}}"
            }
        }


class {{api_name}}UpdateRequest(BaseModel):
    """Request model for updating {{resource_name}}"""
    name: Optional[str] = Field(None, description="Name of the {{resource_name}}")
    description: Optional[str] = Field(None, description="Description of the {{resource_name}}")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated {{resource_name}}",
                "description": "Updated description"
            }
        }


class {{api_name}}Response(BaseModel):
    """Response model for {{resource_name}}"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the {{resource_name}}")
    description: Optional[str] = Field(None, description="Description of the {{resource_name}}")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True


class StandardAPIResponse(BaseModel):
    """Standard API response wrapper"""
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class {{api_name}}APIRouter:
    """{{api_description}} REST API Router"""
    
    def __init__(self, service: Any, metrics_collector: APIMetricsCollector):
        self.service = service
        self.metrics_collector = metrics_collector
        self.router = APIRouter(
            prefix="/api/v1/{{resource_path}}",
            tags=["{{api_tag}}"]
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.router.get("/health")
        @log_api_call
        async def health_check():
            return StandardAPIResponse(
                status=ResponseStatus.SUCCESS,
                message="{{api_name}} API is healthy",
                data={"status": "ok", "version": "1.0.0"}
            )
        
        @self.router.post("/", status_code=status.HTTP_201_CREATED)
        @rate_limit(max_calls=100, window=60)
        @log_api_call
        async def create_{{resource_name_lower}}(
            request: {{api_name}}CreateRequest,
            current_user = Depends(get_current_user),
            db: AsyncSession = Depends(get_db_session)
        ):
            try:
                await verify_permissions(current_user, "{{resource_name_lower}}:create")
                await validate_request(request)
                
                result = await self.service.create_{{resource_name_lower}}(
                    data=request.dict(),
                    user_id=current_user.id,
                    db=db
                )
                
                return StandardAPIResponse(
                    status=ResponseStatus.SUCCESS,
                    message="{{resource_name}} created successfully",
                    data={{api_name}}Response.from_orm(result)
                )
                
            except ValidationException as e:
                raise HTTPException(status_code=422, detail=str(e))
            except APIException as e:
                raise HTTPException(status_code=e.status_code, detail=e.message)
            except Exception as e:
                logger.error(f"Error creating {{resource_name_lower}}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")


def create_{{api_name_lower}}_router(service: Any, metrics_collector: APIMetricsCollector) -> APIRouter:
    """Create and configure the {{api_name}} router"""
    api_router = {{api_name}}APIRouter(service=service, metrics_collector=metrics_collector)
    return api_router.router


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "rest_api_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive REST API template with full CRUD operations",
    "required_parameters": [
        "api_name",
        "api_description",
        "resource_name",
        "resource_name_lower",
        "resource_path",
        "api_tag",
        "author_name",
        "author_email",
        "created_date"
    ],
    "dependencies": [
        "fastapi>=0.104.1",
        "pydantic>=2.5.0",
        "sqlalchemy[asyncio]>=2.0.23"
    ],
    "features": [
        "Full CRUD operations",
        "Authentication and authorization",
        "Input validation",
        "Error handling",
        "API metrics",
        "Rate limiting",
        "Caching"
    ]
}