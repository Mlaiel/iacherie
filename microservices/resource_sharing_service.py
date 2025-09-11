"""
🤝 Resource Sharing Service - Collaborative Resource Sharing & Management
=========================================================================

**Module**: Resource Sharing Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: Backend Senior + Microservices Architect + DBA + Security Specialist

Advanced resource sharing service for collaborative resource management
with real-time sharing, access control, and intelligent allocation.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ResourceSharingService")

class ResourceType(str, Enum):
    FILE = "file"
    TOOL = "tool"
    TEMPLATE = "template"
    ASSET = "asset"
    KNOWLEDGE = "knowledge"
    DATASET = "dataset"
    MODEL = "model"
    WORKSPACE = "workspace"

class AccessLevel(str, Enum):
    NONE = "none"
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class SharingType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    TEAM = "team"
    PROJECT = "project"
    ORGANIZATION = "organization"

@dataclass
class ResourceMetrics:
    """Resource sharing metrics"""
    total_resources: int
    active_shares: int
    usage_rate: float
    average_access_time: float
    collaboration_score: float
    storage_utilization: float
    security_incidents: int

class ResourceModel(BaseModel):
    """Resource model for sharing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    resource_type: ResourceType = ResourceType.FILE
    owner_id: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    sharing_type: SharingType = SharingType.PRIVATE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    version: str = "1.0.0"

class AccessPermissionModel(BaseModel):
    """Access permission model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    user_id: str
    access_level: AccessLevel = AccessLevel.VIEW
    granted_by: str
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class ShareRequestModel(BaseModel):
    """Resource sharing request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    requester_id: str
    requested_access: AccessLevel = AccessLevel.VIEW
    justification: Optional[str] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, approved, rejected
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class ResourceSharingService:
    """Advanced resource sharing and management service"""
    
    def __init__(self):
        self.resources: Dict[str, ResourceModel] = {}
        self.permissions: Dict[str, AccessPermissionModel] = {}
        self.share_requests: Dict[str, ShareRequestModel] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.metrics = ResourceMetrics(
            total_resources=0,
            active_shares=0,
            usage_rate=0.0,
            average_access_time=0.0,
            collaboration_score=0.0,
            storage_utilization=0.0,
            security_incidents=0
        )
        logger.info("Resource Sharing Service initialized successfully")

    async def create_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shareable resource"""
        try:
            resource = ResourceModel(**resource_data)
            self.resources[resource.id] = resource
            self.metrics.total_resources += 1
            
            # Create owner permission
            owner_permission = AccessPermissionModel(
                resource_id=resource.id,
                user_id=resource.owner_id,
                access_level=AccessLevel.OWNER,
                granted_by=resource.owner_id
            )
            self.permissions[owner_permission.id] = owner_permission
            
            logger.info(f"Created resource: {resource.id}")
            return {
                "success": True,
                "resource_id": resource.id,
                "message": "Resource created successfully",
                "resource": resource.dict()
            }
        except Exception as e:
            logger.error(f"Error creating resource: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create resource: {str(e)}")

    async def share_resource(self, resource_id: str, user_id: str, access_level: AccessLevel, 
                           granted_by: str, expires_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Share resource with a user"""
        try:
            if resource_id not in self.resources:
                raise HTTPException(status_code=404, detail="Resource not found")
            
            # Check if granter has permission to share
            if not await self._check_permission(resource_id, granted_by, AccessLevel.ADMIN):
                raise HTTPException(status_code=403, detail="Insufficient permissions to share resource")
            
            # Check if permission already exists
            existing_permission = next(
                (p for p in self.permissions.values() 
                 if p.resource_id == resource_id and p.user_id == user_id and p.is_active),
                None
            )
            
            if existing_permission:
                # Update existing permission
                existing_permission.access_level = access_level
                existing_permission.expires_at = expires_at
                existing_permission.granted_at = datetime.utcnow()
                permission = existing_permission
            else:
                # Create new permission
                permission = AccessPermissionModel(
                    resource_id=resource_id,
                    user_id=user_id,
                    access_level=access_level,
                    granted_by=granted_by,
                    expires_at=expires_at
                )
                self.permissions[permission.id] = permission
                self.metrics.active_shares += 1
            
            logger.info(f"Shared resource {resource_id} with user {user_id}")
            return {
                "success": True,
                "permission_id": permission.id,
                "message": "Resource shared successfully",
                "permission": permission.dict()
            }
        except Exception as e:
            logger.error(f"Error sharing resource: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to share resource: {str(e)}")

    async def request_access(self, resource_id: str, requester_id: str, 
                           requested_access: AccessLevel, justification: Optional[str] = None) -> Dict[str, Any]:
        """Request access to a resource"""
        try:
            if resource_id not in self.resources:
                raise HTTPException(status_code=404, detail="Resource not found")
            
            resource = self.resources[resource_id]
            
            # Check if resource is public
            if resource.sharing_type == SharingType.PUBLIC:
                # Grant immediate access for public resources
                permission = AccessPermissionModel(
                    resource_id=resource_id,
                    user_id=requester_id,
                    access_level=min(requested_access, AccessLevel.VIEW),
                    granted_by="system"
                )
                self.permissions[permission.id] = permission
                self.metrics.active_shares += 1
                
                return {
                    "success": True,
                    "access_granted": True,
                    "permission_id": permission.id,
                    "message": "Access granted immediately for public resource"
                }
            
            # Create access request for non-public resources
            request = ShareRequestModel(
                resource_id=resource_id,
                requester_id=requester_id,
                requested_access=requested_access,
                justification=justification
            )
            self.share_requests[request.id] = request
            
            # Notify resource owner/admins
            await self._notify_access_request(request)
            
            logger.info(f"Created access request for resource {resource_id} by user {requester_id}")
            return {
                "success": True,
                "request_id": request.id,
                "message": "Access request submitted successfully",
                "request": request.dict()
            }
        except Exception as e:
            logger.error(f"Error requesting access: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to request access: {str(e)}")

    async def approve_access_request(self, request_id: str, reviewer_id: str, 
                                   approved: bool, notes: Optional[str] = None) -> Dict[str, Any]:
        """Approve or reject access request"""
        try:
            if request_id not in self.share_requests:
                raise HTTPException(status_code=404, detail="Access request not found")
            
            request = self.share_requests[request_id]
            
            # Check if reviewer has permission to approve
            if not await self._check_permission(request.resource_id, reviewer_id, AccessLevel.ADMIN):
                raise HTTPException(status_code=403, detail="Insufficient permissions to review request")
            
            request.status = "approved" if approved else "rejected"
            request.reviewed_by = reviewer_id
            request.reviewed_at = datetime.utcnow()
            
            if approved:
                # Grant access
                permission = AccessPermissionModel(
                    resource_id=request.resource_id,
                    user_id=request.requester_id,
                    access_level=request.requested_access,
                    granted_by=reviewer_id
                )
                self.permissions[permission.id] = permission
                self.metrics.active_shares += 1
                
                # Notify requester
                await self._notify_access_granted(request, permission)
                
                logger.info(f"Approved access request {request_id}")
                return {
                    "success": True,
                    "approved": True,
                    "permission_id": permission.id,
                    "message": "Access request approved successfully"
                }
            else:
                # Notify requester of rejection
                await self._notify_access_rejected(request, notes)
                
                logger.info(f"Rejected access request {request_id}")
                return {
                    "success": True,
                    "approved": False,
                    "message": "Access request rejected"
                }
        except Exception as e:
            logger.error(f"Error reviewing access request: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to review access request: {str(e)}")

    async def access_resource(self, resource_id: str, user_id: str, 
                            access_type: str = "read") -> Dict[str, Any]:
        """Access a shared resource"""
        try:
            if resource_id not in self.resources:
                raise HTTPException(status_code=404, detail="Resource not found")
            
            # Check access permission
            required_level = AccessLevel.EDIT if access_type == "write" else AccessLevel.VIEW
            if not await self._check_permission(resource_id, user_id, required_level):
                raise HTTPException(status_code=403, detail="Access denied")
            
            resource = self.resources[resource_id]
            resource.last_accessed = datetime.utcnow()
            resource.access_count += 1
            
            # Create access session
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = {
                "resource_id": resource_id,
                "user_id": user_id,
                "access_type": access_type,
                "started_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            logger.info(f"User {user_id} accessed resource {resource_id}")
            return {
                "success": True,
                "session_id": session_id,
                "resource": resource.dict(),
                "access_type": access_type,
                "message": "Resource accessed successfully"
            }
        except Exception as e:
            logger.error(f"Error accessing resource: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to access resource: {str(e)}")

    async def _check_permission(self, resource_id: str, user_id: str, 
                              required_level: AccessLevel) -> bool:
        """Check if user has required permission level"""
        permission = next(
            (p for p in self.permissions.values() 
             if p.resource_id == resource_id and p.user_id == user_id and p.is_active),
            None
        )
        
        if not permission:
            return False
        
        # Check expiration
        if permission.expires_at and permission.expires_at < datetime.utcnow():
            permission.is_active = False
            return False
        
        # Check access level hierarchy
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.VIEW: 1,
            AccessLevel.EDIT: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        return level_hierarchy.get(permission.access_level, 0) >= level_hierarchy.get(required_level, 0)

    async def _notify_access_request(self, request: ShareRequestModel):
        """Notify resource administrators about access request"""
        # In real implementation, this would send notifications
        logger.info(f"Notifying administrators about access request {request.id}")

    async def _notify_access_granted(self, request: ShareRequestModel, permission: AccessPermissionModel):
        """Notify requester that access was granted"""
        logger.info(f"Notifying user {request.requester_id} about granted access to resource {request.resource_id}")

    async def _notify_access_rejected(self, request: ShareRequestModel, notes: Optional[str]):
        """Notify requester that access was rejected"""
        logger.info(f"Notifying user {request.requester_id} about rejected access to resource {request.resource_id}")

    async def revoke_access(self, resource_id: str, user_id: str, revoked_by: str) -> Dict[str, Any]:
        """Revoke user access to resource"""
        try:
            # Check if revoker has permission
            if not await self._check_permission(resource_id, revoked_by, AccessLevel.ADMIN):
                raise HTTPException(status_code=403, detail="Insufficient permissions to revoke access")
            
            # Find and deactivate permission
            permission = next(
                (p for p in self.permissions.values() 
                 if p.resource_id == resource_id and p.user_id == user_id and p.is_active),
                None
            )
            
            if not permission:
                raise HTTPException(status_code=404, detail="Permission not found")
            
            permission.is_active = False
            self.metrics.active_shares -= 1
            
            # End any active sessions
            for session_id, session in list(self.active_sessions.items()):
                if session["resource_id"] == resource_id and session["user_id"] == user_id:
                    del self.active_sessions[session_id]
            
            logger.info(f"Revoked access for user {user_id} to resource {resource_id}")
            return {
                "success": True,
                "message": "Access revoked successfully"
            }
        except Exception as e:
            logger.error(f"Error revoking access: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to revoke access: {str(e)}")

    async def get_user_resources(self, user_id: str) -> Dict[str, Any]:
        """Get resources accessible to user"""
        try:
            accessible_resources = []
            
            for permission in self.permissions.values():
                if permission.user_id == user_id and permission.is_active:
                    if permission.expires_at and permission.expires_at < datetime.utcnow():
                        permission.is_active = False
                        continue
                    
                    resource = self.resources.get(permission.resource_id)
                    if resource:
                        accessible_resources.append({
                            "resource": resource.dict(),
                            "access_level": permission.access_level,
                            "granted_at": permission.granted_at,
                            "expires_at": permission.expires_at
                        })
            
            return {
                "user_id": user_id,
                "accessible_resources": accessible_resources,
                "count": len(accessible_resources)
            }
        except Exception as e:
            logger.error(f"Error getting user resources: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get user resources: {str(e)}")

    async def get_resource_permissions(self, resource_id: str, requester_id: str) -> Dict[str, Any]:
        """Get permissions for a resource"""
        try:
            if resource_id not in self.resources:
                raise HTTPException(status_code=404, detail="Resource not found")
            
            # Check if requester has admin access
            if not await self._check_permission(resource_id, requester_id, AccessLevel.ADMIN):
                raise HTTPException(status_code=403, detail="Insufficient permissions to view permissions")
            
            permissions = [
                p.dict() for p in self.permissions.values() 
                if p.resource_id == resource_id and p.is_active
            ]
            
            return {
                "resource_id": resource_id,
                "permissions": permissions,
                "count": len(permissions)
            }
        except Exception as e:
            logger.error(f"Error getting resource permissions: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get resource permissions: {str(e)}")

    async def get_pending_requests(self, reviewer_id: str) -> Dict[str, Any]:
        """Get pending access requests for resources managed by user"""
        try:
            pending_requests = []
            
            for request in self.share_requests.values():
                if request.status == "pending":
                    # Check if reviewer can approve this request
                    if await self._check_permission(request.resource_id, reviewer_id, AccessLevel.ADMIN):
                        resource = self.resources.get(request.resource_id)
                        if resource:
                            pending_requests.append({
                                "request": request.dict(),
                                "resource": {
                                    "id": resource.id,
                                    "name": resource.name,
                                    "type": resource.resource_type
                                }
                            })
            
            return {
                "pending_requests": pending_requests,
                "count": len(pending_requests)
            }
        except Exception as e:
            logger.error(f"Error getting pending requests: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get pending requests: {str(e)}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get resource sharing metrics"""
        # Update metrics
        active_sessions_count = len(self.active_sessions)
        total_accesses = sum(r.access_count for r in self.resources.values())
        
        if total_accesses > 0:
            self.metrics.usage_rate = (active_sessions_count / len(self.resources)) * 100 if self.resources else 0
        
        return {
            "total_resources": self.metrics.total_resources,
            "active_shares": self.metrics.active_shares,
            "active_sessions": active_sessions_count,
            "usage_rate": self.metrics.usage_rate,
            "collaboration_score": self.metrics.collaboration_score,
            "storage_utilization": self.metrics.storage_utilization,
            "security_incidents": self.metrics.security_incidents
        }

# FastAPI application setup
app = FastAPI(title="Resource Sharing Service")
service = ResourceSharingService()

@app.post("/resources/")
async def create_resource(resource_data: Dict[str, Any]):
    """Create a new shareable resource"""
    return await service.create_resource(resource_data)

@app.post("/resources/{resource_id}/share")
async def share_resource(resource_id: str, user_id: str, access_level: AccessLevel, 
                        granted_by: str, expires_at: Optional[datetime] = None):
    """Share resource with a user"""
    return await service.share_resource(resource_id, user_id, access_level, granted_by, expires_at)

@app.post("/resources/{resource_id}/request-access")
async def request_access(resource_id: str, requester_id: str, requested_access: AccessLevel, 
                        justification: Optional[str] = None):
    """Request access to a resource"""
    return await service.request_access(resource_id, requester_id, requested_access, justification)

@app.post("/requests/{request_id}/review")
async def approve_access_request(request_id: str, reviewer_id: str, approved: bool, 
                               notes: Optional[str] = None):
    """Approve or reject access request"""
    return await service.approve_access_request(request_id, reviewer_id, approved, notes)

@app.post("/resources/{resource_id}/access")
async def access_resource(resource_id: str, user_id: str, access_type: str = "read"):
    """Access a shared resource"""
    return await service.access_resource(resource_id, user_id, access_type)

@app.delete("/resources/{resource_id}/access/{user_id}")
async def revoke_access(resource_id: str, user_id: str, revoked_by: str):
    """Revoke user access to resource"""
    return await service.revoke_access(resource_id, user_id, revoked_by)

@app.get("/users/{user_id}/resources")
async def get_user_resources(user_id: str):
    """Get resources accessible to user"""
    return await service.get_user_resources(user_id)

@app.get("/resources/{resource_id}/permissions")
async def get_resource_permissions(resource_id: str, requester_id: str):
    """Get permissions for a resource"""
    return await service.get_resource_permissions(resource_id, requester_id)

@app.get("/requests/pending")
async def get_pending_requests(reviewer_id: str):
    """Get pending access requests"""
    return await service.get_pending_requests(reviewer_id)

@app.get("/metrics")
async def get_metrics():
    """Get resource sharing metrics"""
    return await service.get_metrics()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ResourceSharingService"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)