"""Creator Workflow Mobile Integration
====================================

Creator workflow mobile integration layer providing seamless mobile workflow
coordination, real-time progress tracking, and creator-specific optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
from pathlib import Path

# Import mobile backend components
from .mobile_content_orchestrator import (
    MobileContentOrchestrator, 
    MobileContentRequest, 
    WorkflowStatus,
    CreatorType,
    WorkflowStage
)
from .creator_upload_manager import (
    CreatorUploadManager, 
    UploadRequest, 
    UploadProgress,
    CreatorUploadSettings,
    ContentFormat
)
from .mobile_media_processor import (
    MobileMediaProcessor, 
    ProcessingRequest, 
    ProcessingResult,
    MobileProcessingSettings,
    QualityLevel
)

logger = logging.getLogger(__name__)


class WorkflowEvent(str, Enum):
    """Workflow events for mobile notifications."""
    WORKFLOW_STARTED = "workflow_started"
    UPLOAD_PROGRESS = "upload_progress"
    UPLOAD_COMPLETED = "upload_completed"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    AI_ANALYSIS_STARTED = "ai_analysis_started"
    AI_ANALYSIS_COMPLETED = "ai_analysis_completed"
    PROTECTION_APPLIED = "protection_applied"
    SEO_OPTIMIZED = "seo_optimized"
    COLLABORATION_INVITED = "collaboration_invited"
    DISTRIBUTION_READY = "distribution_ready"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    GAMIFICATION_REWARD = "gamification_reward"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class MobileWorkflowEvent:
    """Mobile workflow event data."""
    event_id: str
    workflow_id: str
    creator_id: str
    event_type: WorkflowEvent
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    mobile_device_id: str
    created_at: datetime = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class CreatorWorkflowState:
    """Creator workflow state tracking."""
    creator_id: str
    creator_type: CreatorType
    active_workflows: List[str]
    completed_workflows: List[str]
    failed_workflows: List[str]
    total_uploads: int
    successful_uploads: int
    total_processing_time: float
    gamification_points: int
    achievement_level: int
    mobile_preferences: Dict[str, Any]
    collaboration_invites: List[str]
    pending_notifications: List[MobileWorkflowEvent]
    last_activity: datetime = None

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()


@dataclass
class MobileWorkflowConfiguration:
    """Mobile workflow configuration."""
    creator_id: str
    auto_upload_settings: CreatorUploadSettings
    processing_preferences: MobileProcessingSettings
    notification_settings: Dict[str, bool]
    collaboration_settings: Dict[str, Any]
    gamification_enabled: bool = True
    real_time_progress: bool = True
    background_processing: bool = True
    wifi_only_uploads: bool = False
    battery_optimization: bool = True
    adaptive_quality: bool = True
    offline_mode_enabled: bool = True

    def __post_init__(self):
        if not hasattr(self, 'notification_settings') or not self.notification_settings:
            self.notification_settings = {
                "upload_progress": True,
                "processing_updates": True,
                "collaboration_invites": True,
                "gamification_rewards": True,
                "workflow_completion": True,
                "error_alerts": True
            }
        if not hasattr(self, 'collaboration_settings') or not self.collaboration_settings:
            self.collaboration_settings = {
                "auto_accept_collaborations": False,
                "preferred_collaboration_types": [],
                "maximum_collaborators": 5,
                "collaboration_notifications": True
            }


class CreatorWorkflowMobile:
    """Creator workflow mobile integration layer."""

    def __init__(self):
        # Initialize mobile backend components
        self.content_orchestrator = MobileContentOrchestrator()
        self.upload_manager = CreatorUploadManager()
        self.media_processor = MobileMediaProcessor()
        
        # Workflow state management
        self.creator_states: Dict[str, CreatorWorkflowState] = {}
        self.workflow_configurations: Dict[str, MobileWorkflowConfiguration] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Event handling
        self.event_handlers: Dict[WorkflowEvent, List[Callable]] = {}
        self.mobile_event_queue: Dict[str, List[MobileWorkflowEvent]] = {}
        
        # Integration callbacks
        self.notification_service = None
        self.gamification_service = None
        self.collaboration_service = None
        
        # Initialize event handlers
        self._initialize_event_handlers()

    def _initialize_event_handlers(self):
        """Initialize default event handlers."""
        self.event_handlers = {
            WorkflowEvent.WORKFLOW_STARTED: [self._handle_workflow_started],
            WorkflowEvent.UPLOAD_PROGRESS: [self._handle_upload_progress],
            WorkflowEvent.UPLOAD_COMPLETED: [self._handle_upload_completed],
            WorkflowEvent.PROCESSING_COMPLETED: [self._handle_processing_completed],
            WorkflowEvent.WORKFLOW_COMPLETED: [self._handle_workflow_completed],
            WorkflowEvent.WORKFLOW_FAILED: [self._handle_workflow_failed],
            WorkflowEvent.GAMIFICATION_REWARD: [self._handle_gamification_reward]
        }

    async def initialize_creator_workflow(self, creator_id: str, creator_type: str,
                                         mobile_device_id: str,
                                         configuration: Optional[MobileWorkflowConfiguration] = None) -> CreatorWorkflowState:
        """Initialize creator workflow for mobile."""
        try:
            logger.info(f"Initializing mobile workflow for creator {creator_id}")
            
            # Create default configuration if not provided
            if not configuration:
                configuration = await self._create_default_configuration(creator_id, creator_type)
            
            # Store configuration
            self.workflow_configurations[creator_id] = configuration
            
            # Initialize creator state
            creator_state = CreatorWorkflowState(
                creator_id=creator_id,
                creator_type=CreatorType(creator_type),
                active_workflows=[],
                completed_workflows=[],
                failed_workflows=[],
                total_uploads=0,
                successful_uploads=0,
                total_processing_time=0.0,
                gamification_points=0,
                achievement_level=1,
                mobile_preferences={
                    "mobile_device_id": mobile_device_id,
                    "notifications_enabled": True,
                    "real_time_updates": True
                },
                collaboration_invites=[],
                pending_notifications=[]
            )
            
            # Store creator state
            self.creator_states[creator_id] = creator_state
            
            # Initialize mobile event queue
            self.mobile_event_queue[creator_id] = []
            
            logger.info(f"Mobile workflow initialized for creator {creator_id}")
            return creator_state
            
        except Exception as e:
            logger.error(f"Failed to initialize creator workflow: {e}")
            raise

    async def start_mobile_content_workflow(self, creator_id: str, file_path: str,
                                           content_type: str, metadata: Dict[str, Any] = None) -> str:
        """Start complete mobile content workflow."""
        try:
            if creator_id not in self.creator_states:
                raise ValueError(f"Creator {creator_id} not initialized")
            
            creator_state = self.creator_states[creator_id]
            configuration = self.workflow_configurations[creator_id]
            
            # Generate workflow ID
            workflow_id = f"{creator_id}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting mobile content workflow {workflow_id}")
            
            # Detect content format
            content_format = await self._detect_content_format(file_path)
            
            # Create upload request
            upload_request = UploadRequest(
                upload_id=f"upload_{workflow_id}",
                creator_id=creator_id,
                creator_type=creator_state.creator_type.value,
                file_name=Path(file_path).name,
                file_size=Path(file_path).stat().st_size,
                content_type=content_type,
                content_format=content_format,
                mobile_device_id=creator_state.mobile_preferences["mobile_device_id"],
                device_type="mobile",  # Could be detected
                network_type="wifi",   # Could be detected
                upload_settings=configuration.auto_upload_settings,
                metadata=metadata or {}
            )
            
            # Create mobile content request
            mobile_request = MobileContentRequest(
                content_id=workflow_id,
                creator_id=creator_id,
                creator_type=creator_state.creator_type,
                content_type=content_type,
                file_path=file_path,
                mobile_device_id=creator_state.mobile_preferences["mobile_device_id"],
                device_type="mobile",
                network_type="wifi",
                upload_settings=asdict(configuration.auto_upload_settings),
                workflow_preferences=asdict(configuration),
                metadata=metadata or {}
            )
            
            # Store workflow context
            self.active_workflows[workflow_id] = {
                "upload_request": upload_request,
                "mobile_request": mobile_request,
                "creator_id": creator_id,
                "started_at": datetime.utcnow(),
                "current_stage": "initialization"
            }
            
            # Add to creator's active workflows
            creator_state.active_workflows.append(workflow_id)
            creator_state.total_uploads += 1
            
            # Emit workflow started event
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.WORKFLOW_STARTED,
                "Workflow Started", "Your content workflow has started",
                {"workflow_id": workflow_id, "content_type": content_type}
            )
            
            # Start upload process
            await self._start_upload_process(workflow_id)
            
            logger.info(f"Mobile content workflow {workflow_id} started")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start mobile content workflow: {e}")
            raise

    async def _start_upload_process(self, workflow_id: str) -> None:
        """Start the upload process for a workflow."""
        try:
            workflow_context = self.active_workflows[workflow_id]
            upload_request = workflow_context["upload_request"]
            creator_id = workflow_context["creator_id"]
            
            # Initialize upload
            upload_progress = await self.upload_manager.initialize_upload(upload_request)
            
            # Update workflow context
            workflow_context["upload_progress"] = upload_progress
            workflow_context["current_stage"] = "uploading"
            
            # Emit upload started event
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.UPLOAD_PROGRESS,
                "Upload Started", "File upload has begun",
                {"progress": upload_progress.progress_percentage}
            )
            
            # Start monitoring upload progress
            asyncio.create_task(self._monitor_upload_progress(workflow_id))
            
        except Exception as e:
            logger.error(f"Failed to start upload process for {workflow_id}: {e}")
            await self._handle_workflow_error(workflow_id, "upload_start", str(e))

    async def _monitor_upload_progress(self, workflow_id: str) -> None:
        """Monitor upload progress and emit events."""
        try:
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            upload_request = workflow_context["upload_request"]
            
            # Simulate chunked upload monitoring
            while True:
                await asyncio.sleep(1)  # Check every second
                
                # Get current upload progress
                upload_progress = await self.upload_manager.get_upload_progress(upload_request.upload_id)
                
                if not upload_progress:
                    break
                
                # Update workflow context
                workflow_context["upload_progress"] = upload_progress
                
                # Emit progress events
                if upload_progress.progress_percentage > 0:
                    await self._emit_mobile_event(
                        creator_id, workflow_id, WorkflowEvent.UPLOAD_PROGRESS,
                        f"Upload Progress: {upload_progress.progress_percentage:.1f}%",
                        f"Uploading... {upload_progress.bytes_uploaded}/{upload_progress.total_bytes} bytes",
                        {
                            "progress": upload_progress.progress_percentage,
                            "bytes_uploaded": upload_progress.bytes_uploaded,
                            "upload_speed": upload_progress.upload_speed_mbps
                        }
                    )
                
                # Check if upload completed
                if upload_progress.status.value == "completed":
                    await self._handle_upload_completion(workflow_id)
                    break
                elif upload_progress.status.value == "failed":
                    await self._handle_workflow_error(workflow_id, "upload", "Upload failed")
                    break
                    
        except Exception as e:
            logger.error(f"Upload monitoring failed for {workflow_id}: {e}")
            await self._handle_workflow_error(workflow_id, "upload_monitoring", str(e))

    async def _handle_upload_completion(self, workflow_id: str) -> None:
        """Handle upload completion and start processing."""
        try:
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            
            # Emit upload completed event
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.UPLOAD_COMPLETED,
                "Upload Completed", "Your file has been uploaded successfully",
                {"workflow_id": workflow_id}
            )
            
            # Start mobile content orchestration
            mobile_request = workflow_context["mobile_request"]
            workflow_status = await self.content_orchestrator.orchestrate_mobile_workflow(mobile_request)
            
            # Update workflow context
            workflow_context["workflow_status"] = workflow_status
            workflow_context["current_stage"] = "orchestrating"
            
            # Start monitoring orchestration progress
            asyncio.create_task(self._monitor_orchestration_progress(workflow_id))
            
        except Exception as e:
            logger.error(f"Upload completion handling failed for {workflow_id}: {e}")
            await self._handle_workflow_error(workflow_id, "upload_completion", str(e))

    async def _monitor_orchestration_progress(self, workflow_id: str) -> None:
        """Monitor orchestration progress and emit events."""
        try:
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            mobile_request = workflow_context["mobile_request"]
            
            while True:
                await asyncio.sleep(2)  # Check every 2 seconds
                
                # Get workflow status
                workflow_status = await self.content_orchestrator.get_workflow_status(mobile_request.content_id)
                
                if not workflow_status:
                    break
                
                # Update workflow context
                workflow_context["workflow_status"] = workflow_status
                
                # Emit stage-specific events
                await self._emit_stage_events(creator_id, workflow_id, workflow_status)
                
                # Check if workflow completed
                if workflow_status.current_stage == WorkflowStage.COMPLETED:
                    await self._handle_workflow_completion(workflow_id)
                    break
                elif workflow_status.status == "failed":
                    await self._handle_workflow_error(workflow_id, "orchestration", "Workflow orchestration failed")
                    break
                    
        except Exception as e:
            logger.error(f"Orchestration monitoring failed for {workflow_id}: {e}")
            await self._handle_workflow_error(workflow_id, "orchestration_monitoring", str(e))

    async def _emit_stage_events(self, creator_id: str, workflow_id: str, workflow_status: WorkflowStatus) -> None:
        """Emit events for specific workflow stages."""
        stage = workflow_status.current_stage
        
        if stage == WorkflowStage.IA_PROCESSING:
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.AI_ANALYSIS_STARTED,
                "AI Analysis Started", "Analyzing your content with AI",
                {"stage": stage.value, "progress": workflow_status.progress_percentage}
            )
        elif stage == WorkflowStage.PROTECTION:
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.PROTECTION_APPLIED,
                "Content Protection Applied", "Your content is now protected",
                {"stage": stage.value, "progress": workflow_status.progress_percentage}
            )
        elif stage == WorkflowStage.SEO_OPTIMIZATION:
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.SEO_OPTIMIZED,
                "SEO Optimization Complete", "Your content is optimized for search",
                {"stage": stage.value, "progress": workflow_status.progress_percentage}
            )
        elif stage == WorkflowStage.COLLABORATION:
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.COLLABORATION_INVITED,
                "Collaboration Opportunities", "Found potential collaboration matches",
                {"stage": stage.value, "progress": workflow_status.progress_percentage}
            )

    async def _handle_workflow_completion(self, workflow_id: str) -> None:
        """Handle workflow completion."""
        try:
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            creator_state = self.creator_states[creator_id]
            
            # Update creator state
            creator_state.active_workflows.remove(workflow_id)
            creator_state.completed_workflows.append(workflow_id)
            creator_state.successful_uploads += 1
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - workflow_context["started_at"]).total_seconds()
            creator_state.total_processing_time += processing_time
            
            # Apply gamification rewards
            workflow_status = workflow_context.get("workflow_status")
            if workflow_status and workflow_status.gamification_rewards:
                total_points = sum(workflow_status.gamification_rewards.values())
                creator_state.gamification_points += total_points
                
                # Emit gamification reward event
                await self._emit_mobile_event(
                    creator_id, workflow_id, WorkflowEvent.GAMIFICATION_REWARD,
                    f"Earned {total_points} Points!", "Great work on completing your workflow",
                    {"points_earned": total_points, "total_points": creator_state.gamification_points}
                )
            
            # Emit workflow completed event
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.WORKFLOW_COMPLETED,
                "Workflow Complete!", "Your content is ready for distribution",
                {
                    "workflow_id": workflow_id,
                    "processing_time": processing_time,
                    "total_rewards": workflow_status.gamification_rewards if workflow_status else {}
                }
            )
            
            # Clean up workflow from active list
            del self.active_workflows[workflow_id]
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow completion handling failed for {workflow_id}: {e}")

    async def _handle_workflow_error(self, workflow_id: str, stage: str, error: str) -> None:
        """Handle workflow errors."""
        try:
            if workflow_id not in self.active_workflows:
                return
                
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            creator_state = self.creator_states[creator_id]
            
            # Update creator state
            if workflow_id in creator_state.active_workflows:
                creator_state.active_workflows.remove(workflow_id)
            creator_state.failed_workflows.append(workflow_id)
            
            # Emit error event
            await self._emit_mobile_event(
                creator_id, workflow_id, WorkflowEvent.WORKFLOW_FAILED,
                "Workflow Failed", f"Error in {stage}: {error}",
                {"workflow_id": workflow_id, "stage": stage, "error": error},
                priority=NotificationPriority.HIGH
            )
            
            # Clean up workflow
            del self.active_workflows[workflow_id]
            
            logger.error(f"Workflow {workflow_id} failed at {stage}: {error}")
            
        except Exception as e:
            logger.error(f"Error handling failed for {workflow_id}: {e}")

    async def _emit_mobile_event(self, creator_id: str, workflow_id: str, event_type: WorkflowEvent,
                                title: str, message: str, data: Dict[str, Any],
                                priority: NotificationPriority = NotificationPriority.NORMAL) -> None:
        """Emit mobile workflow event."""
        try:
            creator_state = self.creator_states.get(creator_id)
            if not creator_state:
                return
            
            # Create mobile event
            event = MobileWorkflowEvent(
                event_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                creator_id=creator_id,
                event_type=event_type,
                priority=priority,
                title=title,
                message=message,
                data=data,
                mobile_device_id=creator_state.mobile_preferences["mobile_device_id"]
            )
            
            # Add to event queue
            if creator_id not in self.mobile_event_queue:
                self.mobile_event_queue[creator_id] = []
            self.mobile_event_queue[creator_id].append(event)
            
            # Execute event handlers
            handlers = self.event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event_type}: {e}")
            
            logger.debug(f"Emitted mobile event {event_type} for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"Failed to emit mobile event: {e}")

    # Default event handlers
    async def _handle_workflow_started(self, event: MobileWorkflowEvent) -> None:
        """Handle workflow started event."""
        logger.info(f"Workflow started for creator {event.creator_id}")

    async def _handle_upload_progress(self, event: MobileWorkflowEvent) -> None:
        """Handle upload progress event."""
        # Send real-time progress update via WebSocket or push notification
        if self.notification_service:
            await self.notification_service.send_progress_update(event)

    async def _handle_upload_completed(self, event: MobileWorkflowEvent) -> None:
        """Handle upload completed event."""
        # Send upload completion notification
        if self.notification_service:
            await self.notification_service.send_notification(event)

    async def _handle_processing_completed(self, event: MobileWorkflowEvent) -> None:
        """Handle processing completed event."""
        logger.info(f"Processing completed for workflow {event.workflow_id}")

    async def _handle_workflow_completed(self, event: MobileWorkflowEvent) -> None:
        """Handle workflow completed event."""
        # Send completion notification and update analytics
        if self.notification_service:
            await self.notification_service.send_notification(event)

    async def _handle_workflow_failed(self, event: MobileWorkflowEvent) -> None:
        """Handle workflow failed event."""
        # Send error notification
        if self.notification_service:
            await self.notification_service.send_error_notification(event)

    async def _handle_gamification_reward(self, event: MobileWorkflowEvent) -> None:
        """Handle gamification reward event."""
        # Update gamification system
        if self.gamification_service:
            await self.gamification_service.award_points(event)

    async def _create_default_configuration(self, creator_id: str, creator_type: str) -> MobileWorkflowConfiguration:
        """Create default mobile workflow configuration for creator type."""
        # Create creator-specific upload settings
        upload_settings = CreatorUploadSettings(
            creator_id=creator_id,
            creator_type=creator_type,
            preferred_format=ContentFormat.MP4 if creator_type in ["influencer", "comedian"] else ContentFormat.MP3,
            quality_preference="high",
            upload_method="chunked",
            chunk_size_mb=2,
            max_file_size_mb=500,
            compression_enabled=True,
            auto_validation=True,
            background_upload=True
        )
        
        # Create processing preferences
        processing_preferences = MobileProcessingSettings(
            target_quality=QualityLevel.HIGH,
            output_formats=[],  # Will be set based on creator type
            max_resolution=(1280, 720),
            max_bitrate_kbps=2000,
            frame_rate=30,
            audio_sample_rate=44100
        )
        
        return MobileWorkflowConfiguration(
            creator_id=creator_id,
            auto_upload_settings=upload_settings,
            processing_preferences=processing_preferences,
            notification_settings={},  # Will use defaults
            collaboration_settings={}  # Will use defaults
        )

    async def _detect_content_format(self, file_path: str) -> ContentFormat:
        """Detect content format from file path."""
        file_extension = Path(file_path).suffix.lower().lstrip('.')
        
        # Map extensions to ContentFormat
        extension_map = {
            'mp3': ContentFormat.MP3,
            'wav': ContentFormat.WAV,
            'mp4': ContentFormat.MP4,
            'mov': ContentFormat.MOV,
            'jpg': ContentFormat.JPG,
            'jpeg': ContentFormat.JPEG,
            'png': ContentFormat.PNG,
            'txt': ContentFormat.TXT,
            'md': ContentFormat.MD
        }
        
        return extension_map.get(file_extension, ContentFormat.UNKNOWN)

    # Public API methods
    async def get_creator_workflow_status(self, creator_id: str) -> Optional[CreatorWorkflowState]:
        """Get creator workflow status."""
        return self.creator_states.get(creator_id)

    async def get_workflow_progress(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get specific workflow progress."""
        workflow_context = self.active_workflows.get(workflow_id)
        if not workflow_context:
            return None
        
        return {
            "workflow_id": workflow_id,
            "current_stage": workflow_context.get("current_stage"),
            "upload_progress": asdict(workflow_context.get("upload_progress", {})),
            "workflow_status": asdict(workflow_context.get("workflow_status", {})),
            "started_at": workflow_context.get("started_at").isoformat() if workflow_context.get("started_at") else None
        }

    async def get_mobile_events(self, creator_id: str, limit: int = 50) -> List[MobileWorkflowEvent]:
        """Get mobile events for creator."""
        events = self.mobile_event_queue.get(creator_id, [])
        return events[-limit:]  # Return most recent events

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause active workflow."""
        if workflow_id in self.active_workflows:
            # Pause upload if active
            workflow_context = self.active_workflows[workflow_id]
            upload_request = workflow_context.get("upload_request")
            if upload_request:
                await self.upload_manager.pause_upload(upload_request.upload_id)
            
            # Pause orchestration if active
            mobile_request = workflow_context.get("mobile_request")
            if mobile_request:
                await self.content_orchestrator.pause_workflow(mobile_request.content_id)
            
            return True
        return False

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel active workflow."""
        if workflow_id in self.active_workflows:
            workflow_context = self.active_workflows[workflow_id]
            creator_id = workflow_context["creator_id"]
            
            # Cancel upload if active
            upload_request = workflow_context.get("upload_request")
            if upload_request:
                await self.upload_manager.cancel_upload(upload_request.upload_id)
            
            # Cancel orchestration if active
            mobile_request = workflow_context.get("mobile_request")
            if mobile_request:
                await self.content_orchestrator.cancel_workflow(mobile_request.content_id)
            
            # Update creator state
            creator_state = self.creator_states[creator_id]
            if workflow_id in creator_state.active_workflows:
                creator_state.active_workflows.remove(workflow_id)
            
            # Clean up
            del self.active_workflows[workflow_id]
            
            return True
        return False

    async def get_creator_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive creator analytics."""
        creator_state = self.creator_states.get(creator_id)
        if not creator_state:
            return {}
        
        return {
            "creator_summary": {
                "total_workflows": len(creator_state.completed_workflows) + len(creator_state.failed_workflows),
                "successful_workflows": len(creator_state.completed_workflows),
                "success_rate": len(creator_state.completed_workflows) / max(1, len(creator_state.completed_workflows) + len(creator_state.failed_workflows)),
                "total_uploads": creator_state.total_uploads,
                "successful_uploads": creator_state.successful_uploads,
                "average_processing_time": creator_state.total_processing_time / max(1, len(creator_state.completed_workflows))
            },
            "gamification": {
                "total_points": creator_state.gamification_points,
                "achievement_level": creator_state.achievement_level,
                "active_collaborations": len(creator_state.collaboration_invites)
            },
            "mobile_usage": {
                "active_workflows": len(creator_state.active_workflows),
                "pending_notifications": len(creator_state.pending_notifications),
                "last_activity": creator_state.last_activity.isoformat()
            }
        }

    def set_notification_service(self, service):
        """Set notification service for mobile events."""
        self.notification_service = service

    def set_gamification_service(self, service):
        """Set gamification service integration."""
        self.gamification_service = service

    def set_collaboration_service(self, service):
        """Set collaboration service integration."""
        self.collaboration_service = service

    def add_event_handler(self, event_type: WorkflowEvent, handler: Callable):
        """Add custom event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)