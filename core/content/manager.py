"""Content Manager - Central Content Management Controller
======================================================

The ContentManager serves as the central orchestrator for all content-related operations
in the IA Influencer Agent platform. It coordinates content processing, protection,
and monetization workflows according to the business logic specification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func

from ..database.models import Content, ContentMetadata, ContentProtection
from ..security.encryption import ContentEncryption
from ..cache.redis_client import RedisClient
from .processor import ContentProcessor
from .validator import ContentValidator
from .analyzer import ContentAnalyzer
from .optimizer import ContentOptimizer
from .tracker import ContentTracker
from .monitor import ContentMonitor


class ContentStatus(Enum):
    """
Content processing status enumeration"""

    UPLOADED = "uploaded"
    VALIDATING = "validating" 
    ANALYZING = "analyzing"
    PROTECTING = "protecting"
    OPTIMIZING = "optimizing"
    DISTRIBUTING = "distributing"
    PUBLISHED = "published"
    PROTECTED = "protected"
    MONETIZING = "monetizing"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class ContentWorkflowConfig:
    """Content workflow configuration"""
    enable_protection: bool = True
    enable_optimization: bool = True
    enable_monetization: bool = True
    enable_distribution: bool = True
    auto_classify: bool = True
    auto_enhance: bool = True
    quality_threshold: float = 0.8
    processing_timeout: int = 300


class ContentManager:
    """
    Central Content Management Controller
    
    Orchestrates the complete content lifecycle from upload to monetization,
    ensuring all business logic requirements are met.
    
    Business Flow:
    Upload → Validation → Analysis → Protection → Optimization → Distribution → Monetization
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: RedisClient,
        encryption: ContentEncryption,
        config: ContentWorkflowConfig = None
    ):
        self.db = db_session
        self.redis = redis_client
        self.encryption = encryption
        self.config = config or ContentWorkflowConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize content processors
        self.processor = ContentProcessor(db_session, redis_client)
        self.validator = ContentValidator()
        self.analyzer = ContentAnalyzer(db_session)
        self.optimizer = ContentOptimizer(db_session)
        self.tracker = ContentTracker(db_session, redis_client)
        self.monitor = ContentMonitor(db_session, redis_client)
        
        # Workflow tracking
        self.active_workflows: Dict[str, Dict] = {}

    async def create_content(
        self,
        user_id: int,
        file_path: str,
        content_type: str,
        metadata: Dict[str, Any] = None,
        workflow_config: ContentWorkflowConfig = None
    ) -> Dict[str, Any]:
        """
        Create new content and initiate processing workflow
        
        Args:
            user_id: Owner user ID
            file_path: Path to uploaded content file
            content_type: Type of content (audio, video, image, text)
            metadata: Additional content metadata
            workflow_config: Custom workflow configuration
            
        Returns:
            Content creation result with processing status
        """
        try:
            workflow_id = str(uuid.uuid4())
            config = workflow_config or self.config
            
            self.logger.info(f"Creating content for user {user_id}, workflow {workflow_id}")
            
            # Step 1: Initial validation
            validation_result = await self.validator.validate_content(
                file_path=file_path,
                content_type=content_type,
                user_id=user_id
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["errors"],
                    "workflow_id": workflow_id
                }
            
            # Step 2: Create content record
            content_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": metadata.get("title", "Untitled"),
                "content_type": content_type,
                "file_path": file_path,
                "status": ContentStatus.UPLOADED.value,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "workflow_id": workflow_id
            }
            
            content = Content(**content_data)
            self.db.add(content)
            await self.db.commit()
            await self.db.refresh(content)
            
            # Step 3: Initialize workflow tracking
            self.active_workflows[workflow_id] = {
                "content_id": content.id,
                "user_id": user_id,
                "status": ContentStatus.UPLOADED.value,
                "config": config,
                "created_at": datetime.utcnow(),
                "steps_completed": ["upload"],
                "current_step": "validation"
            }
            
            # Step 4: Start async processing workflow
            asyncio.create_task(
                self._process_content_workflow(content.id, config)
            )
            
            # Step 5: Cache content info
            await self.redis.set(
                f"content:{content.id}",
                content_data,
                expire=3600
            )
            
            return {
                "success": True,
                "content_id": content.id,
                "workflow_id": workflow_id,
                "status": ContentStatus.UPLOADED.value,
                "message": "Content created and processing initiated"
            }
            
        except Exception as e:
            self.logger.error(f"Content creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Content creation failed: {str(e)}",
                "workflow_id": workflow_id
            }

    async def _process_content_workflow(
        self,
        content_id: str,
        config: ContentWorkflowConfig
    ) -> None:
        """
        Execute complete content processing workflow
        
        Args:
            content_id: Content identifier
            config: Workflow configuration
        """
        try:
            content = await self._get_content(content_id)
            if not content:
                return
                
            workflow_id = content.workflow_id
            
            # Step 1: Content Analysis
            await self._update_workflow_status(workflow_id, "analyzing", "analysis")
            analysis_result = await self.analyzer.analyze_content(content_id)
            
            if not analysis_result["success"]:
                await self._mark_workflow_failed(workflow_id, analysis_result["error"])
                return
                
            # Step 2: Content Protection (if enabled)
            if config.enable_protection:
                await self._update_workflow_status(workflow_id, "protecting", "protection")
                protection_result = await self._protect_content(content_id)
                
                if not protection_result["success"]:
                    await self._mark_workflow_failed(workflow_id, protection_result["error"])
                    return
            
            # Step 3: Content Optimization (if enabled)
            if config.enable_optimization:
                await self._update_workflow_status(workflow_id, "optimizing", "optimization")
                optimization_result = await self.optimizer.optimize_content(content_id)
                
                if not optimization_result["success"]:
                    self.logger.warning(f"Optimization failed for {content_id}: {optimization_result['error']}")
            
            # Step 4: Content Distribution (if enabled)
            if config.enable_distribution:
                await self._update_workflow_status(workflow_id, "distributing", "distribution")
                distribution_result = await self._distribute_content(content_id)
                
                if not distribution_result["success"]:
                    self.logger.warning(f"Distribution failed for {content_id}: {distribution_result['error']}")
            
            # Step 5: Monetization Setup (if enabled)
            if config.enable_monetization:
                await self._update_workflow_status(workflow_id, "monetizing", "monetization")
                monetization_result = await self._setup_monetization(content_id)
                
                if not monetization_result["success"]:
                    self.logger.warning(f"Monetization setup failed for {content_id}: {monetization_result['error']}")
            
            # Step 6: Finalize workflow
            await self._finalize_workflow(workflow_id, ContentStatus.PUBLISHED)
            
        except Exception as e:
            self.logger.error(f"Workflow processing failed for {content_id}: {str(e)}")
            await self._mark_workflow_failed(content_id, str(e))

    async def get_content(self, content_id: str, user_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve content by ID with optional user filtering
        
        Args:
            content_id: Content identifier
            user_id: Optional user ID for ownership verification
            
        Returns:
            Content data or None if not found
        """
        try:
            # Try cache first
            cached_content = await self.redis.get(f"content:{content_id}")
            if cached_content:
                if user_id and cached_content.get("user_id") != user_id:
                    return None
                return cached_content
            
            # Query database
            query = select(Content).where(Content.id == content_id)
            if user_id:
                query = query.where(Content.user_id == user_id)
                
            result = await self.db.execute(query)
            content = result.scalar_one_or_none()
            
            if not content:
                return None
                
            content_data = {
                "id": content.id,
                "user_id": content.user_id,
                "title": content.title,
                "content_type": content.content_type,
                "status": content.status,
                "metadata": content.metadata,
                "created_at": content.created_at.isoformat(),
                "updated_at": content.updated_at.isoformat() if content.updated_at else None
            }
            
            # Cache for future use
            await self.redis.set(f"content:{content_id}", content_data, expire=3600)
            
            return content_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve content {content_id}: {str(e)}")
            return None

    async def list_user_content(
        self,
        user_id: int,
        status: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List content for a specific user with filtering
        
        Args:
            user_id: User identifier
            status: Optional status filter
            content_type: Optional content type filter
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Paginated content list
        """
        try:
            query = select(Content).where(Content.user_id == user_id)
            
            if status:
                query = query.where(Content.status == status)
            if content_type:
                query = query.where(Content.content_type == content_type)
                
            # Get total count
            count_query = select(func.count(Content.id)).where(Content.user_id == user_id)
            if status:
                count_query = count_query.where(Content.status == status)
            if content_type:
                count_query = count_query.where(Content.content_type == content_type)
                
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.order_by(Content.created_at.desc()).limit(limit).offset(offset)
            result = await self.db.execute(query)
            contents = result.scalars().all()
            
            content_list = []
            for content in contents:
                content_list.append({
                    "id": content.id,
                    "title": content.title,
                    "content_type": content.content_type,
                    "status": content.status,
                    "created_at": content.created_at.isoformat(),
                    "metadata": content.metadata
                })
            
            return {
                "success": True,
                "contents": content_list,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list content for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contents": [],
                "total": 0
            }

    async def update_content(
        self,
        content_id: str,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update content metadata and properties
        
        Args:
            content_id: Content identifier
            user_id: User identifier for ownership verification
            updates: Dictionary of fields to update
            
        Returns:
            Update operation result
        """
        try:
            # Verify ownership
            content = await self._get_content(content_id)
            if not content or content.user_id != user_id:
                return {
                    "success": False,
                    "error": "Content not found or access denied"
                }
            
            # Prepare update data
            allowed_fields = ["title", "metadata", "tags", "description"]
            update_data = {k: v for k, v in updates.items() if k in allowed_fields}
            update_data["updated_at"] = datetime.utcnow()
            
            # Update database
            query = update(Content).where(
                Content.id == content_id,
                Content.user_id == user_id
            ).values(**update_data)
            
            await self.db.execute(query)
            await self.db.commit()
            
            # Invalidate cache
            await self.redis.delete(f"content:{content_id}")
            
            return {
                "success": True,
                "message": "Content updated successfully",
                "updated_fields": list(update_data.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update content {content_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_content(self, content_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete content and associated data
        
        Args:
            content_id: Content identifier
            user_id: User identifier for ownership verification
            
        Returns:
            Deletion operation result
        """
        try:
            # Verify ownership
            content = await self._get_content(content_id)
            if not content or content.user_id != user_id:
                return {
                    "success": False,
                    "error": "Content not found or access denied"
                }
            
            # Mark as archived instead of hard delete
            query = update(Content).where(
                Content.id == content_id,
                Content.user_id == user_id
            ).values(
                status=ContentStatus.ARCHIVED.value,
                updated_at=datetime.utcnow()
            )
            
            await self.db.execute(query)
            await self.db.commit()
            
            # Clear cache
            await self.redis.delete(f"content:{content_id}")
            
            # Schedule cleanup tasks
            await self.tracker.track_content_deletion(content_id, user_id)
            
            return {
                "success": True,
                "message": "Content archived successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete content {content_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get current workflow processing status
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status information
        """
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "status": workflow["status"],
                    "current_step": workflow["current_step"],
                    "steps_completed": workflow["steps_completed"],
                    "created_at": workflow["created_at"].isoformat()
                }
            
            # Check completed workflows in cache
            cached_workflow = await self.redis.get(f"workflow:{workflow_id}")
            if cached_workflow:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    **cached_workflow
                }
            
            return {
                "success": False,
                "error": "Workflow not found"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow status {workflow_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # Private helper methods

    async def _get_content(self, content_id: str) -> Optional[Content]:
        """Get content model from database"""
        query = select(Content).where(Content.id == content_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _update_workflow_status(
        self,
        workflow_id: str,
        status: str,
        current_step: str
    ) -> None:
        """
Update workflow status and tracking"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = status
            workflow["current_step"] = current_step
            if current_step not in workflow["steps_completed"]:
                workflow["steps_completed"].append(current_step)

    async def _mark_workflow_failed(self, workflow_id: str, error: str) -> None:
        """Mark workflow as failed"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = ContentStatus.FAILED.value
            workflow["error"] = error
            
            # Update content status
            content_id = workflow["content_id"]
            query = update(Content).where(Content.id == content_id).values(
                status=ContentStatus.FAILED.value,
                updated_at=datetime.utcnow()
            )
            await self.db.execute(query)
            await self.db.commit()

    async def _finalize_workflow(self, workflow_id: str, final_status: ContentStatus) -> None:
        """Finalize workflow processing"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = final_status.value
            workflow["completed_at"] = datetime.utcnow()
            
            # Update content status
            content_id = workflow["content_id"]
            query = update(Content).where(Content.id == content_id).values(
                status=final_status.value,
                updated_at=datetime.utcnow()
            )
            await self.db.execute(query)
            await self.db.commit()
            
            # Cache completed workflow
            await self.redis.set(
                f"workflow:{workflow_id}",
                workflow,
                expire=86400  # 24 hours
            )
            
            # Remove from active workflows
            del self.active_workflows[workflow_id]

    async def _protect_content(self, content_id: str) -> Dict[str, Any]:
        """Initiate content protection workflow"""
        # This would interface with the content protection module
        try:
            # Placeholder for actual protection implementation
            return {"success": True, "message": "Content protection initiated"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _distribute_content(self, content_id: str) -> Dict[str, Any]:
        """Initiate content distribution workflow"""
        try:
            # Placeholder for actual distribution implementation
            return {"success": True, "message": "Content distribution initiated"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_monetization(self, content_id: str) -> Dict[str, Any]:
        """Setup content monetization tracking"""
        try:
            # Placeholder for actual monetization setup
            return {"success": True, "message": "Monetization setup completed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
