"""{{service_name}} Service for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field
from fastapi import HTTPException, status

from core.database import get_db_session
from core.config import get_settings
from utils.exceptions import ServiceException


logger = logging.getLogger(__name__)
settings = get_settings()


# Request/Response Models
class {{service_name}}Request(BaseModel):
    """Request model for {{service_name}} operations"""
    # Add your request fields here
    pass


class {{service_name}}Response(BaseModel):
    """Response model for {{service_name}} operations"""
    # Add your response fields here
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Service Interface
class I{{service_name}}Service(ABC):
    """Interface for {{service_name}} service"""
    
    @abstractmethod
    async def process(self, request: {{service_name}}Request) -> {{service_name}}Response:
        """Process {{service_name}} request"""
        pass


# Service Implementation
class {{service_name}}Service(I{{service_name}}Service):
    """{{service_name}} service implementation"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def process(self, request: {{service_name}}Request) -> {{service_name}}Response:
        """Process {{service_name}} request"""
        try:
            self.logger.info(f"Processing {{service_name}} request")
            
            # Validate request
            await self._validate_request(request)
            
            # Process the request
            result = await self._process_internal(request)
            
            # Return response
            return {{service_name}}Response(
                success=True,
                message="{{service_name}} processed successfully",
                data=result
            )
            
        except Exception as e:
            self.logger.error(f"Error processing {{service_name}} request: {str(e)}")
            raise ServiceException(
                message=f"{{service_name}} processing failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def _validate_request(self, request: {{service_name}}Request) -> None:
        """Validate the request data"""
        # Add your validation logic here
        pass
    
    async def _process_internal(self, request: {{service_name}}Request) -> Dict[str, Any]:
        """Internal processing logic"""
        # Add your processing logic here
        return {"processed": True}


# Service Factory
class {{service_name}}ServiceFactory:
    """Factory for creating {{service_name}} service instances"""
    
    _instance: Optional[{{service_name}}Service] = None
    
    @classmethod
    def get_service(cls) -> {{service_name}}Service:
        """Get singleton service instance"""
        if cls._instance is None:
            cls._instance = {{service_name}}Service()
        return cls._instance


# Helper functions
async def create_{{service_name_lower}}_service() -> {{service_name}}Service:
    """Dependency injection helper for {{service_name}} service"""
    return {{service_name}}ServiceFactory.get_service()


# Service configuration
{{service_name_upper}}_CONFIG = {
    "name": "{{service_name}}",
    "version": "1.0.0",
    "description": "{{service_description}}",
    "author": "{{author_name}}",
    "created": "{{created_date}}"
}