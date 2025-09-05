"""
Validation Endpoints
API endpoints for data validation and verification
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json

router = APIRouter()

class ValidationRequest(BaseModel):
    data: Dict[str, Any]
    validation_type: str
    strict: bool = False

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    validated_data: Optional[Dict[str, Any]] = None

@router.post("/validate", response_model=ValidationResponse)
async def validate_data(request: ValidationRequest):
    """Validate data according to specified rules"""
    try:
        errors = []
        warnings = []
        validated_data = request.data.copy()
        
        # Basic validation logic
        if request.validation_type == "content":
            if "name" not in request.data:
                errors.append("Content name is required")
            if "type" not in request.data:
                errors.append("Content type is required")
            elif request.data["type"] not in ["audio", "video", "image", "text"]:
                errors.append("Invalid content type")
                
        elif request.validation_type == "agent":
            if "name" not in request.data:
                errors.append("Agent name is required")
            if "type" not in request.data:
                errors.append("Agent type is required")
                
        elif request.validation_type == "crawler":
            if "url" not in request.data:
                errors.append("URL is required for crawler")
            if "platform" not in request.data:
                errors.append("Platform is required")
                
        valid = len(errors) == 0
        
        return ValidationResponse(
            valid=valid,
            errors=errors,
            warnings=warnings,
            validated_data=validated_data if valid else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/validation-rules/{validation_type}")
async def get_validation_rules(validation_type: str):
    """Get validation rules for a specific type"""
    rules = {
        "content": {
            "required_fields": ["name", "type"],
            "optional_fields": ["description", "tags", "protection_level"],
            "valid_types": ["audio", "video", "image", "text"]
        },
        "agent": {
            "required_fields": ["name", "type", "configuration"],
            "optional_fields": ["description", "priority", "schedule"],
            "valid_types": ["content_analyzer", "copyright_detector", "violation_scanner"]
        },
        "crawler": {
            "required_fields": ["url", "platform"],
            "optional_fields": ["user_agent", "delay", "depth"],
            "valid_platforms": ["youtube", "facebook", "instagram", "twitter", "tiktok"]
        }
    }
    
    if validation_type not in rules:
        raise HTTPException(status_code=404, detail="Validation type not found")
    
    return rules[validation_type]

__all__ = ["router"]
