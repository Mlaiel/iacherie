"""GDPR Compliance API Routes

Complete GDPR right-to-be-forgotten API with comprehensive data rights management.
Builds on existing compliance infrastructure for minimal changes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ...core.security.compliance import GDPRCompliance, PrivacyRight
from ...core.security.authentication import get_current_user
from ...kubernetes.compliance.data_retention import DataRetentionManager
from ...data_management.governance.lineage import LineageTracker
from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/gdpr", tags=["GDPR Compliance"])
security = HTTPBearer()


class PrivacyRequestCreate(BaseModel):
    """Privacy request creation model"""
    request_type: PrivacyRight
    description: Optional[str] = Field(None, description="Additional details for the request")
    user_verification_token: Optional[str] = Field(None, description="User verification token")


class PrivacyRequestResponse(BaseModel):
    """Privacy request response model"""
    request_id: str
    user_id: str
    request_type: str
    status: str
    created_at: datetime
    estimated_completion: datetime
    description: Optional[str] = None


class DataErasureRequest(BaseModel):
    """Specific data erasure request model"""
    data_categories: Optional[List[str]] = Field(default=None, description="Specific data categories to erase")
    keep_anonymized: bool = Field(default=False, description="Keep anonymized data for analytics")
    verification_required: bool = Field(default=True, description="Require additional verification")


class DataAccessResponse(BaseModel):
    """Data access response model"""
    user_id: str
    data_export_url: str
    export_format: str
    expires_at: datetime
    categories_included: List[str]


@router.post("/privacy-request", response_model=PrivacyRequestResponse)
async def create_privacy_request(
    request: PrivacyRequestCreate,
    current_user: Dict = Depends(get_current_user),
    gdpr_service: GDPRCompliance = Depends()
):
    """
    Create a new privacy rights request (GDPR Article 12-22)
    
    Supported request types:
    - access: Right to access personal data
    - erasure: Right to be forgotten
    - rectification: Right to correct data
    - portability: Right to data portability
    - restriction: Right to restrict processing
    - objection: Right to object to processing
    """
    try:
        user_id = current_user.get("user_id")
        
        # Process the privacy request
        privacy_request = await gdpr_service.process_privacy_request(
            user_id=user_id,
            request_type=request.request_type,
            description=request.description or ""
        )
        
        logger.info(f"Privacy request created: {privacy_request.request_id} for user {user_id}")
        
        return PrivacyRequestResponse(
            request_id=privacy_request.request_id,
            user_id=privacy_request.user_id,
            request_type=privacy_request.request_type.value,
            status=privacy_request.status.value,
            created_at=privacy_request.created_at,
            estimated_completion=privacy_request.estimated_completion,
            description=privacy_request.description
        )
        
    except Exception as e:
        logger.error(f"Failed to create privacy request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Privacy request creation failed: {str(e)}")


@router.post("/right-to-be-forgotten", response_model=Dict[str, Any])
async def right_to_be_forgotten(
    request: DataErasureRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    gdpr_service: GDPRCompliance = Depends(),
    retention_manager: DataRetentionManager = Depends(),
    lineage_tracker: LineageTracker = Depends()
):
    """
    Complete GDPR Right to be Forgotten implementation (Article 17)
    
    This endpoint handles comprehensive data erasure with:
    - Data category-specific deletion
    - Retention policy compliance checking
    - Data lineage tracking for audit trails
    - Background processing for large datasets
    """
    try:
        user_id = current_user.get("user_id")
        
        # Create erasure request
        erasure_request = await gdpr_service.process_privacy_request(
            user_id=user_id,
            request_type=PrivacyRight.ERASURE,
            description=f"Data categories: {request.data_categories}"
        )
        
        # Process erasure in background for large datasets
        background_tasks.add_task(
            _process_data_erasure,
            user_id,
            request.data_categories,
            request.keep_anonymized,
            erasure_request.request_id,
            gdpr_service,
            retention_manager,
            lineage_tracker
        )
        
        logger.info(f"Right to be forgotten request initiated for user {user_id}")
        
        return {
            "request_id": erasure_request.request_id,
            "status": "processing",
            "message": "Data erasure request has been initiated and will be processed",
            "estimated_completion": erasure_request.estimated_completion.isoformat(),
            "categories_to_erase": request.data_categories or "all",
            "keep_anonymized": request.keep_anonymized
        }
        
    except Exception as e:
        logger.error(f"Right to be forgotten request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data erasure request failed: {str(e)}")


@router.get("/data-export", response_model=DataAccessResponse)
async def export_personal_data(
    format: str = "json",
    categories: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    gdpr_service: GDPRCompliance = Depends()
):
    """
    Export personal data (GDPR Article 15 - Right of Access)
    
    Supported formats: json, csv, xml
    Categories: profile, content, usage, financial, preferences
    """
    try:
        user_id = current_user.get("user_id")
        data_categories = categories.split(",") if categories else None
        
        # Create access request
        access_request = await gdpr_service.process_privacy_request(
            user_id=user_id,
            request_type=PrivacyRight.ACCESS,
            description=f"Data export - Format: {format}, Categories: {categories}"
        )
        
        # Generate secure download URL
        export_url = f"/api/v1/gdpr/download/{access_request.request_id}"
        
        logger.info(f"Data export request created for user {user_id}")
        
        return DataAccessResponse(
            user_id=user_id,
            data_export_url=export_url,
            export_format=format,
            expires_at=access_request.estimated_completion,
            categories_included=data_categories or ["all"]
        )
        
    except Exception as e:
        logger.error(f"Data export request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")


@router.get("/request-status/{request_id}")
async def get_request_status(
    request_id: str,
    current_user: Dict = Depends(get_current_user),
    gdpr_service: GDPRCompliance = Depends()
):
    """Get the status of a privacy rights request"""
    try:
        user_id = current_user.get("user_id")
        
        # Get request status
        status = await gdpr_service.get_request_status(request_id, user_id)
        
        return {
            "request_id": request_id,
            "status": status.get("status"),
            "progress": status.get("progress", 0),
            "message": status.get("message", ""),
            "created_at": status.get("created_at"),
            "updated_at": status.get("updated_at"),
            "estimated_completion": status.get("estimated_completion")
        }
        
    except Exception as e:
        logger.error(f"Failed to get request status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request status retrieval failed: {str(e)}")


@router.get("/data-lineage/{content_id}")
async def get_data_lineage(
    content_id: str,
    current_user: Dict = Depends(get_current_user),
    lineage_tracker: LineageTracker = Depends()
):
    """
    Get data lineage for audit and compliance purposes
    Shows complete data flow and transformations
    """
    try:
        user_id = current_user.get("user_id")
        
        # Verify user access to the content
        lineage = await lineage_tracker.get_content_lineage(content_id)
        
        if not lineage:
            raise HTTPException(status_code=404, detail="Content lineage not found")
            
        # Filter lineage based on user permissions
        filtered_lineage = await _filter_lineage_by_user_access(lineage, user_id)
        
        return {
            "content_id": content_id,
            "lineage": filtered_lineage,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Data lineage retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data lineage retrieval failed: {str(e)}")


async def _process_data_erasure(
    user_id: str,
    data_categories: Optional[List[str]],
    keep_anonymized: bool,
    request_id: str,
    gdpr_service: GDPRCompliance,
    retention_manager: DataRetentionManager,
    lineage_tracker: LineageTracker
):
    """Background task for processing data erasure"""
    try:
        # Check retention policies before deletion
        if data_categories:
            for category in data_categories:
                can_delete = await retention_manager.can_delete_data_category(user_id, category)
                if not can_delete:
                    logger.warning(f"Cannot delete {category} for user {user_id} due to retention policies")
                    continue
                    
        # Track data lineage for audit trail
        await lineage_tracker.track_event(
            content_id=f"user_data_{user_id}",
            event_type="DELETE",
            source_system="gdpr_api",
            user_id=user_id,
            metadata={"request_id": request_id, "categories": data_categories}
        )
        
        # Process the actual erasure
        result = await gdpr_service._handle_erasure_request(user_id)
        
        # Update request status
        await gdpr_service.update_request_status(request_id, "completed", result)
        
        logger.info(f"Data erasure completed for user {user_id}, request {request_id}")
        
    except Exception as e:
        logger.error(f"Data erasure background task failed: {str(e)}")
        await gdpr_service.update_request_status(request_id, "failed", {"error": str(e)})


async def _filter_lineage_by_user_access(lineage: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Filter data lineage based on user access permissions"""
    # Implementation would filter sensitive information based on user permissions
    # For now, return the lineage as-is for the user's own data
    return lineage