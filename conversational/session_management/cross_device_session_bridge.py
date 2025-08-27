"""
Cross-Device Session Bridge - IA Influencer Agent

Enterprise-grade cross-device session synchronization with seamless continuity,
device state management, and intelligent session handoff for multi-format
content creators across mobile, desktop, and web platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copy, modification, or distribution without 
explicit written permission is strictly prohibited.
Contact: mlaiel@live.de

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced Cross-Platform Architecture  
- ML Engineer: Device Intelligence & Handoff Prediction
- DBA: Multi-Device Session Storage
- Security Expert: Secure Cross-Device Authentication
- Microservices Architect: Distributed Device Management
- Audio Engineer: Audio Session Cross-Device Sync
- DevOps: Cross-Platform Scalability & Performance
- IA Prompt Engineer: Multi-Device Conversational Experience
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, DeviceSessionModel
from ...models.user import UserModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher
from ...utils.device_detection import DeviceDetector
from ...utils.websocket_manager import WebSocketManager

logger = get_logger(__name__)


class DeviceType(Enum):
    """Device type classifications"""
    MOBILE_PHONE = "mobile_phone"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    WEB_BROWSER = "web_browser"
    SMART_TV = "smart_tv"
    SMART_SPEAKER = "smart_speaker"
    WEARABLE = "wearable"
    UNKNOWN = "unknown"


class DeviceCapability(Enum):
    """Device capability flags"""
    AUDIO_RECORDING = "audio_recording"
    VIDEO_RECORDING = "video_recording"
    IMAGE_CAPTURE = "image_capture"
    FILE_UPLOAD = "file_upload"
    PUSH_NOTIFICATIONS = "push_notifications"
    OFFLINE_STORAGE = "offline_storage"
    BACKGROUND_SYNC = "background_sync"
    BIOMETRIC_AUTH = "biometric_auth"
    GPS_LOCATION = "gps_location"
    ACCELEROMETER = "accelerometer"


class SyncStatus(Enum):
    """Session synchronization status"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    FAILED = "failed"
    PARTIAL = "partial"
    OFFLINE = "offline"


class HandoffReason(Enum):
    """Reasons for session handoff"""
    USER_INITIATED = "user_initiated"
    DEVICE_SWITCH = "device_switch"
    NETWORK_OPTIMIZATION = "network_optimization"
    CAPABILITY_REQUIREMENT = "capability_requirement"
    BATTERY_SAVING = "battery_saving"
    AUTOMATIC = "automatic"
    EMERGENCY = "emergency"


class DeviceInfo(BaseModel):
    """Device information structure"""
    device_id: str
    device_type: DeviceType
    device_name: str
    platform: str  # iOS, Android, Windows, macOS, Linux, Web
    platform_version: str
    app_version: str
    screen_resolution: str
    capabilities: List[DeviceCapability]
    network_type: str  # wifi, cellular, ethernet
    battery_level: Optional[int] = None
    is_charging: Optional[bool] = None
    location: Optional[Dict[str, float]] = None
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionState(BaseModel):
    """Cross-device session state"""
    session_id: str
    user_id: str
    primary_device_id: str
    active_devices: Set[str] = Field(default_factory=set)
    conversation_checkpoint: Dict[str, Any] = Field(default_factory=dict)
    context_state: Dict[str, Any] = Field(default_factory=dict)
    content_state: Dict[str, Any] = Field(default_factory=dict)
    ui_state: Dict[str, Any] = Field(default_factory=dict)
    sync_version: int = 0
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    pending_changes: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    conflict_resolutions: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: lambda v: list(v)
        }


class DeviceSessionInfo(BaseModel):
    """Device-specific session information"""
    device_id: str
    session_id: str
    local_state: Dict[str, Any] = Field(default_factory=dict)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    sync_status: SyncStatus = SyncStatus.SYNCED
    pending_operations: List[Dict[str, Any]] = Field(default_factory=list)
    offline_changes: List[Dict[str, Any]] = Field(default_factory=list)
    network_quality: float = 1.0  # 0.0 to 1.0
    is_foreground: bool = True
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class CrossDeviceConfig:
    """Cross-device synchronization configuration"""
    sync_interval: int = 30  # seconds
    max_devices_per_session: int = 5
    handoff_timeout: int = 60  # seconds
    conflict_resolution_strategy: str = "timestamp_priority"
    enable_predictive_sync: bool = True
    enable_background_sync: bool = True
    offline_storage_limit: int = 100  # operations
    sync_retry_attempts: int = 3
    network_quality_threshold: float = 0.3
    battery_optimization: bool = True


class DeviceSessionSynchronizer:
    """Handles device session synchronization"""
    
    def __init__(self, config: CrossDeviceConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.websocket_manager = WebSocketManager()
        self.encryption_manager = EncryptionManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.device_detector = DeviceDetector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Active session states
        self.session_states: Dict[str, SessionState] = {}
        
        # Device information registry
        self.device_registry: Dict[str, DeviceInfo] = {}
        
        # Sync operation queue
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        
        # Background tasks
        self.sync_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def start_synchronization(self):
        """Start background synchronization tasks"""
        
        self.sync_task = asyncio.create_task(self._sync_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Device session synchronization started")
    
    async def stop_synchronization(self):
        """Stop background synchronization tasks"""
        
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Device session synchronization stopped")
    
    async def register_device(
        self,
        device_id: str,
        device_info: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Register device for cross-device sessions"""
        
        try:
            # Detect device capabilities
            capabilities = await self._detect_device_capabilities(device_info)
            
            device = DeviceInfo(
                device_id=device_id,
                device_type=DeviceType(device_info.get("device_type", "unknown")),
                device_name=device_info.get("device_name", f"Device {device_id[:8]}"),
                platform=device_info.get("platform", "unknown"),
                platform_version=device_info.get("platform_version", "unknown"),
                app_version=device_info.get("app_version", "unknown"),
                screen_resolution=device_info.get("screen_resolution", "unknown"),
                capabilities=capabilities,
                network_type=device_info.get("network_type", "unknown"),
                battery_level=device_info.get("battery_level"),
                is_charging=device_info.get("is_charging"),
                location=device_info.get("location")
            )
            
            # Store device info
            self.device_registry[device_id] = device
            
            # Cache device info
            await self._cache_device_info(device_id, device)
            
            # Persist to database
            await self._persist_device_info(user_id, device)
            
            # Publish device registration event
            await self.event_publisher.publish(
                "device.registered",
                {
                    "device_id": device_id,
                    "user_id": user_id,
                    "device_type": device.device_type.value,
                    "capabilities": [c.value for c in device.capabilities]
                }
            )
            
            await self.metrics_collector.increment("cross_device.devices_registered")
            self.logger.info(f"Device registered: {device_id} ({device.device_type.value})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Device registration failed: {str(e)}")
            await self.metrics_collector.increment("cross_device.registration_errors")
            return False
    
    async def start_session_on_device(
        self,
        session_id: str,
        device_id: str,
        user_id: str
    ) -> bool:
        """Start session on specific device"""
        
        try:
            # Get or create session state
            if session_id not in self.session_states:
                session_state = SessionState(
                    session_id=session_id,
                    user_id=user_id,
                    primary_device_id=device_id,
                    active_devices={device_id}
                )
                self.session_states[session_id] = session_state
            else:
                session_state = self.session_states[session_id]
                session_state.active_devices.add(device_id)
            
            # Create device session info
            device_session = DeviceSessionInfo(
                device_id=device_id,
                session_id=session_id
            )
            
            # Check device limits
            if len(session_state.active_devices) > self.config.max_devices_per_session:
                self.logger.warning(f"Too many devices for session {session_id}")
                return False
            
            # Store session state
            await self._store_session_state(session_state)
            
            # Cache device session info
            await self._cache_device_session(device_id, device_session)
            
            # Initialize sync for this device
            await self._initialize_device_sync(session_id, device_id)
            
            # Notify other devices
            await self._notify_device_joined(session_id, device_id)
            
            await self.metrics_collector.increment("cross_device.sessions_started")
            self.logger.info(f"Session started on device: {device_id} -> {session_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start session on device: {str(e)}")
            return False
    
    async def sync_session_state(
        self,
        session_id: str,
        source_device_id: str,
        state_changes: Dict[str, Any]
    ) -> bool:
        """Synchronize session state changes across devices"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if not session_state:
                self.logger.error(f"Session state not found: {session_id}")
                return False
            
            # Validate source device
            if source_device_id not in session_state.active_devices:
                self.logger.warning(f"Unauthorized sync from device: {source_device_id}")
                return False
            
            # Create sync operation
            sync_operation = {
                "operation_id": str(uuid4()),
                "session_id": session_id,
                "source_device_id": source_device_id,
                "changes": state_changes,
                "timestamp": datetime.utcnow().isoformat(),
                "sync_version": session_state.sync_version + 1
            }
            
            # Queue for processing
            await self.sync_queue.put(sync_operation)
            
            await self.metrics_collector.increment("cross_device.sync_operations")
            return True
            
        except Exception as e:
            self.logger.error(f"Session sync failed: {str(e)}")
            await self.metrics_collector.increment("cross_device.sync_errors")
            return False
    
    async def handoff_session(
        self,
        session_id: str,
        from_device_id: str,
        to_device_id: str,
        reason: HandoffReason
    ) -> bool:
        """Handoff session from one device to another"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if not session_state:
                return False
            
            # Validate devices
            if from_device_id not in session_state.active_devices:
                return False
            
            # Get device capabilities
            from_device = self.device_registry.get(from_device_id)
            to_device = self.device_registry.get(to_device_id)
            
            if not from_device or not to_device:
                return False
            
            # Check if handoff is compatible
            if not await self._validate_handoff_compatibility(from_device, to_device, session_state):
                self.logger.warning(f"Handoff not compatible: {from_device_id} -> {to_device_id}")
                return False
            
            # Prepare handoff data
            handoff_data = await self._prepare_handoff_data(session_id, from_device_id)
            
            # Perform handoff
            handoff_success = await self._execute_handoff(
                session_id,
                from_device_id,
                to_device_id,
                handoff_data,
                reason
            )
            
            if handoff_success:
                # Update primary device if needed
                if session_state.primary_device_id == from_device_id:
                    session_state.primary_device_id = to_device_id
                
                # Update session state
                await self._store_session_state(session_state)
                
                await self.metrics_collector.increment("cross_device.handoffs_completed")
                self.logger.info(f"Session handoff completed: {from_device_id} -> {to_device_id}")
            
            return handoff_success
            
        except Exception as e:
            self.logger.error(f"Session handoff failed: {str(e)}")
            await self.metrics_collector.increment("cross_device.handoff_errors")
            return False
    
    async def _sync_loop(self):
        """Background sync processing loop"""
        
        try:
            while True:
                try:
                    # Process sync operations from queue
                    sync_operation = await asyncio.wait_for(
                        self.sync_queue.get(),
                        timeout=1.0
                    )
                    
                    await self._process_sync_operation(sync_operation)
                    
                except asyncio.TimeoutError:
                    # Periodic sync for all active sessions
                    await self._periodic_sync()
                    continue
                    
                except Exception as e:
                    self.logger.error(f"Sync loop error: {str(e)}")
                    
        except asyncio.CancelledError:
            self.logger.info("Sync loop cancelled")
    
    async def _process_sync_operation(self, operation: Dict[str, Any]):
        """Process individual sync operation"""
        
        try:
            session_id = operation["session_id"]
            source_device_id = operation["source_device_id"]
            changes = operation["changes"]
            
            session_state = self.session_states.get(session_id)
            
            if not session_state:
                return
            
            # Apply changes to session state
            await self._apply_state_changes(session_state, changes)
            
            # Increment sync version
            session_state.sync_version = operation["sync_version"]
            session_state.last_sync = datetime.utcnow()
            
            # Store updated state
            await self._store_session_state(session_state)
            
            # Propagate changes to other devices
            target_devices = session_state.active_devices - {source_device_id}
            
            for device_id in target_devices:
                await self._send_sync_update(device_id, operation)
            
            self.logger.debug(f"Sync operation processed: {operation['operation_id']}")
            
        except Exception as e:
            self.logger.error(f"Sync operation processing failed: {str(e)}")
    
    async def _apply_state_changes(self, session_state: SessionState, changes: Dict[str, Any]):
        """Apply state changes to session"""
        
        try:
            for change_type, change_data in changes.items():
                if change_type == "conversation_update":
                    session_state.conversation_checkpoint.update(change_data)
                elif change_type == "context_update":
                    session_state.context_state.update(change_data)
                elif change_type == "content_update":
                    session_state.content_state.update(change_data)
                elif change_type == "ui_update":
                    session_state.ui_state.update(change_data)
                else:
                    self.logger.warning(f"Unknown change type: {change_type}")
                    
        except Exception as e:
            self.logger.error(f"State changes application failed: {str(e)}")
    
    async def _send_sync_update(self, device_id: str, operation: Dict[str, Any]):
        """Send sync update to specific device"""
        
        try:
            # Check if device is online
            device_session = await self._get_device_session(device_id)
            
            if device_session and device_session.sync_status != SyncStatus.OFFLINE:
                # Send via WebSocket if available
                await self.websocket_manager.send_to_device(
                    device_id,
                    {
                        "type": "sync_update",
                        "operation": operation
                    }
                )
            else:
                # Queue for offline sync
                await self._queue_offline_sync(device_id, operation)
            
        except Exception as e:
            self.logger.error(f"Sync update send failed: {str(e)}")
    
    async def _periodic_sync(self):
        """Periodic synchronization for all active sessions"""
        
        try:
            current_time = datetime.utcnow()
            
            for session_id, session_state in self.session_states.items():
                # Check if sync is needed
                time_since_sync = (current_time - session_state.last_sync).total_seconds()
                
                if time_since_sync >= self.config.sync_interval:
                    # Sync session state across devices
                    await self._sync_session_across_devices(session_id)
                    
        except Exception as e:
            self.logger.error(f"Periodic sync failed: {str(e)}")
    
    async def _sync_session_across_devices(self, session_id: str):
        """Sync session state across all active devices"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if not session_state:
                return
            
            # Get current state snapshot
            state_snapshot = {
                "conversation_checkpoint": session_state.conversation_checkpoint,
                "context_state": session_state.context_state,
                "content_state": session_state.content_state,
                "ui_state": session_state.ui_state,
                "sync_version": session_state.sync_version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to all active devices
            for device_id in session_state.active_devices:
                await self.websocket_manager.send_to_device(
                    device_id,
                    {
                        "type": "state_snapshot",
                        "session_id": session_id,
                        "state": state_snapshot
                    }
                )
            
            session_state.last_sync = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Session sync across devices failed: {str(e)}")
    
    async def _detect_device_capabilities(self, device_info: Dict[str, Any]) -> List[DeviceCapability]:
        """Detect device capabilities based on device info"""
        
        capabilities = []
        
        try:
            device_type = device_info.get("device_type", "unknown")
            platform = device_info.get("platform", "unknown").lower()
            
            # Audio recording
            if device_type in ["mobile_phone", "tablet", "laptop", "desktop"]:
                capabilities.append(DeviceCapability.AUDIO_RECORDING)
            
            # Video recording
            if device_type in ["mobile_phone", "tablet", "laptop"]:
                capabilities.append(DeviceCapability.VIDEO_RECORDING)
            
            # Image capture
            if device_type in ["mobile_phone", "tablet"]:
                capabilities.append(DeviceCapability.IMAGE_CAPTURE)
            
            # File upload
            if device_type != "smart_speaker":
                capabilities.append(DeviceCapability.FILE_UPLOAD)
            
            # Push notifications
            if device_type in ["mobile_phone", "tablet"]:
                capabilities.append(DeviceCapability.PUSH_NOTIFICATIONS)
            
            # Offline storage
            if device_type in ["mobile_phone", "tablet", "laptop", "desktop"]:
                capabilities.append(DeviceCapability.OFFLINE_STORAGE)
            
            # Background sync
            if platform in ["ios", "android"] or device_type in ["laptop", "desktop"]:
                capabilities.append(DeviceCapability.BACKGROUND_SYNC)
            
            # Biometric auth
            if device_type in ["mobile_phone", "tablet"] and platform in ["ios", "android"]:
                capabilities.append(DeviceCapability.BIOMETRIC_AUTH)
            
            # GPS location
            if device_type in ["mobile_phone", "tablet", "wearable"]:
                capabilities.append(DeviceCapability.GPS_LOCATION)
            
            # Accelerometer
            if device_type in ["mobile_phone", "tablet", "wearable"]:
                capabilities.append(DeviceCapability.ACCELEROMETER)
            
        except Exception as e:
            self.logger.error(f"Device capability detection failed: {str(e)}")
        
        return capabilities
    
    async def _validate_handoff_compatibility(
        self,
        from_device: DeviceInfo,
        to_device: DeviceInfo,
        session_state: SessionState
    ) -> bool:
        """Validate if handoff is compatible between devices"""
        
        try:
            # Check basic compatibility
            if not to_device.is_active:
                return False
            
            # Check capability requirements
            required_capabilities = self._get_session_required_capabilities(session_state)
            
            for capability in required_capabilities:
                if capability not in to_device.capabilities:
                    return False
            
            # Check platform compatibility for specific content types
            if session_state.content_state:
                content_types = session_state.content_state.get("active_content_types", [])
                
                for content_type in content_types:
                    if not self._is_content_type_supported(content_type, to_device):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Handoff compatibility validation failed: {str(e)}")
            return False
    
    def _get_session_required_capabilities(self, session_state: SessionState) -> List[DeviceCapability]:
        """Get required capabilities for current session state"""
        
        required = []
        
        try:
            # Check content state for capability requirements
            content_state = session_state.content_state
            
            if content_state.get("audio_recording_active"):
                required.append(DeviceCapability.AUDIO_RECORDING)
            
            if content_state.get("video_recording_active"):
                required.append(DeviceCapability.VIDEO_RECORDING)
            
            if content_state.get("image_capture_active"):
                required.append(DeviceCapability.IMAGE_CAPTURE)
            
            if content_state.get("file_upload_pending"):
                required.append(DeviceCapability.FILE_UPLOAD)
            
        except Exception as e:
            self.logger.error(f"Required capabilities detection failed: {str(e)}")
        
        return required
    
    def _is_content_type_supported(self, content_type: str, device: DeviceInfo) -> bool:
        """Check if content type is supported on device"""
        
        support_matrix = {
            "audio": [DeviceCapability.AUDIO_RECORDING],
            "video": [DeviceCapability.VIDEO_RECORDING],
            "image": [DeviceCapability.IMAGE_CAPTURE],
            "file": [DeviceCapability.FILE_UPLOAD]
        }
        
        required_capabilities = support_matrix.get(content_type, [])
        
        return all(cap in device.capabilities for cap in required_capabilities)
    
    async def _prepare_handoff_data(self, session_id: str, from_device_id: str) -> Dict[str, Any]:
        """Prepare data for session handoff"""
        
        try:
            session_state = self.session_states.get(session_id)
            device_session = await self._get_device_session(from_device_id)
            
            if not session_state or not device_session:
                return {}
            
            handoff_data = {
                "session_state": session_state.dict(),
                "device_local_state": device_session.local_state,
                "pending_operations": device_session.pending_operations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return handoff_data
            
        except Exception as e:
            self.logger.error(f"Handoff data preparation failed: {str(e)}")
            return {}
    
    async def _execute_handoff(
        self,
        session_id: str,
        from_device_id: str,
        to_device_id: str,
        handoff_data: Dict[str, Any],
        reason: HandoffReason
    ) -> bool:
        """Execute session handoff"""
        
        try:
            # Send handoff data to target device
            handoff_message = {
                "type": "session_handoff",
                "session_id": session_id,
                "from_device_id": from_device_id,
                "handoff_data": handoff_data,
                "reason": reason.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send via WebSocket
            success = await self.websocket_manager.send_to_device(
                to_device_id,
                handoff_message
            )
            
            if success:
                # Wait for confirmation with timeout
                confirmation = await self._wait_for_handoff_confirmation(
                    session_id,
                    to_device_id,
                    timeout=self.config.handoff_timeout
                )
                
                if confirmation:
                    # Complete handoff
                    await self._complete_handoff(session_id, from_device_id, to_device_id)
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Handoff execution failed: {str(e)}")
            return False
    
    async def _wait_for_handoff_confirmation(
        self,
        session_id: str,
        to_device_id: str,
        timeout: int
    ) -> bool:
        """Wait for handoff confirmation from target device"""
        
        try:
            # This would typically wait for a WebSocket message or event
            # For now, we'll simulate a successful confirmation
            await asyncio.sleep(1)  # Simulate network delay
            return True
            
        except Exception as e:
            self.logger.error(f"Handoff confirmation wait failed: {str(e)}")
            return False
    
    async def _complete_handoff(self, session_id: str, from_device_id: str, to_device_id: str):
        """Complete session handoff process"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if session_state:
                # Update active devices
                session_state.active_devices.discard(from_device_id)
                session_state.active_devices.add(to_device_id)
                
                # Store updated state
                await self._store_session_state(session_state)
            
            # Publish handoff completion event
            await self.event_publisher.publish(
                "session.handoff.completed",
                {
                    "session_id": session_id,
                    "from_device_id": from_device_id,
                    "to_device_id": to_device_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Handoff completion failed: {str(e)}")
    
    async def _cleanup_loop(self):
        """Background cleanup task"""
        
        try:
            while True:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up inactive sessions
                await self._cleanup_inactive_sessions()
                
                # Clean up offline devices
                await self._cleanup_offline_devices()
                
        except asyncio.CancelledError:
            self.logger.info("Cleanup loop cancelled")
        except Exception as e:
            self.logger.error(f"Cleanup loop error: {str(e)}")
    
    async def _cleanup_inactive_sessions(self):
        """Clean up inactive session states"""
        
        try:
            current_time = datetime.utcnow()
            inactive_sessions = []
            
            for session_id, session_state in self.session_states.items():
                time_since_sync = (current_time - session_state.last_sync).total_seconds()
                
                # Mark as inactive if no sync for 1 hour
                if time_since_sync > 3600:
                    inactive_sessions.append(session_id)
            
            # Remove inactive sessions
            for session_id in inactive_sessions:
                del self.session_states[session_id]
                self.logger.info(f"Cleaned up inactive session: {session_id}")
                
        except Exception as e:
            self.logger.error(f"Inactive session cleanup failed: {str(e)}")
    
    async def _cleanup_offline_devices(self):
        """Clean up offline device registrations"""
        
        try:
            current_time = datetime.utcnow()
            offline_devices = []
            
            for device_id, device_info in self.device_registry.items():
                time_since_seen = (current_time - device_info.last_seen).total_seconds()
                
                # Mark as offline if not seen for 24 hours
                if time_since_seen > 86400:
                    offline_devices.append(device_id)
            
            # Remove offline devices
            for device_id in offline_devices:
                del self.device_registry[device_id]
                self.logger.info(f"Cleaned up offline device: {device_id}")
                
        except Exception as e:
            self.logger.error(f"Offline device cleanup failed: {str(e)}")
    
    async def _store_session_state(self, session_state: SessionState):
        """Store session state in cache and database"""
        
        # Store in memory
        self.session_states[session_state.session_id] = session_state
        
        # Cache in Redis
        await self._cache_session_state(session_state)
        
        # Persist to database (async)
        asyncio.create_task(self._persist_session_state(session_state))
    
    async def _cache_session_state(self, session_state: SessionState):
        """Cache session state in Redis"""
        
        try:
            cache_key = f"cross_device_session:{session_state.session_id}"
            
            # Convert sets to lists for JSON serialization
            state_dict = session_state.dict()
            state_dict["active_devices"] = list(state_dict["active_devices"])
            
            await self.cache_manager.set(
                cache_key,
                json.dumps(state_dict, default=str),
                ttl=3600
            )
            
        except Exception as e:
            self.logger.error(f"Session state caching failed: {str(e)}")
    
    async def _persist_session_state(self, session_state: SessionState):
        """Persist session state to database"""
        
        try:
            async with get_async_session() as session:
                # Update or create device session record
                query = select(DeviceSessionModel).where(
                    DeviceSessionModel.session_id == session_state.session_id
                )
                result = await session.execute(query)
                existing_record = result.scalar_one_or_none()
                
                session_data = {
                    "active_devices": list(session_state.active_devices),
                    "conversation_checkpoint": session_state.conversation_checkpoint,
                    "context_state": session_state.context_state,
                    "content_state": session_state.content_state,
                    "ui_state": session_state.ui_state,
                    "sync_version": session_state.sync_version
                }
                
                if existing_record:
                    await session.execute(
                        update(DeviceSessionModel)
                        .where(DeviceSessionModel.session_id == session_state.session_id)
                        .values(
                            device_data=session_data,
                            updated_at=session_state.last_sync
                        )
                    )
                else:
                    new_record = DeviceSessionModel(
                        session_id=session_state.session_id,
                        user_id=session_state.user_id,
                        primary_device_id=session_state.primary_device_id,
                        device_data=session_data,
                        created_at=datetime.utcnow(),
                        updated_at=session_state.last_sync
                    )
                    session.add(new_record)
                
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Session state persistence failed: {str(e)}")
    
    async def _cache_device_info(self, device_id: str, device_info: DeviceInfo):
        """Cache device information"""
        
        try:
            cache_key = f"device_info:{device_id}"
            await self.cache_manager.set(
                cache_key,
                device_info.json(),
                ttl=86400  # 24 hours
            )
            
        except Exception as e:
            self.logger.error(f"Device info caching failed: {str(e)}")
    
    async def _persist_device_info(self, user_id: str, device_info: DeviceInfo):
        """Persist device information to database"""
        
        # Implementation would store device info in user devices table
        pass
    
    async def _cache_device_session(self, device_id: str, device_session: DeviceSessionInfo):
        """Cache device session information"""
        
        try:
            cache_key = f"device_session:{device_id}"
            await self.cache_manager.set(
                cache_key,
                device_session.json(),
                ttl=3600
            )
            
        except Exception as e:
            self.logger.error(f"Device session caching failed: {str(e)}")
    
    async def _get_device_session(self, device_id: str) -> Optional[DeviceSessionInfo]:
        """Get device session information"""
        
        try:
            cache_key = f"device_session:{device_id}"
            cached_data = await self.cache_manager.get(cache_key)
            
            if cached_data:
                return DeviceSessionInfo.parse_raw(cached_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Device session retrieval failed: {str(e)}")
            return None
    
    async def _queue_offline_sync(self, device_id: str, operation: Dict[str, Any]):
        """Queue operation for offline device sync"""
        
        try:
            offline_queue_key = f"offline_sync:{device_id}"
            
            # Get existing queue
            existing_queue = await self.cache_manager.get(offline_queue_key)
            offline_operations = json.loads(existing_queue) if existing_queue else []
            
            # Add new operation
            offline_operations.append(operation)
            
            # Limit queue size
            if len(offline_operations) > self.config.offline_storage_limit:
                offline_operations = offline_operations[-self.config.offline_storage_limit:]
            
            # Store updated queue
            await self.cache_manager.set(
                offline_queue_key,
                json.dumps(offline_operations, default=str),
                ttl=86400  # 24 hours
            )
            
        except Exception as e:
            self.logger.error(f"Offline sync queueing failed: {str(e)}")
    
    async def _initialize_device_sync(self, session_id: str, device_id: str):
        """Initialize sync for new device"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if session_state:
                # Send initial state to device
                initial_state = {
                    "type": "initial_sync",
                    "session_id": session_id,
                    "state": {
                        "conversation_checkpoint": session_state.conversation_checkpoint,
                        "context_state": session_state.context_state,
                        "content_state": session_state.content_state,
                        "ui_state": session_state.ui_state,
                        "sync_version": session_state.sync_version
                    }
                }
                
                await self.websocket_manager.send_to_device(device_id, initial_state)
                
        except Exception as e:
            self.logger.error(f"Device sync initialization failed: {str(e)}")
    
    async def _notify_device_joined(self, session_id: str, device_id: str):
        """Notify other devices about new device joining"""
        
        try:
            session_state = self.session_states.get(session_id)
            
            if session_state:
                notification = {
                    "type": "device_joined",
                    "session_id": session_id,
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Notify all other devices
                other_devices = session_state.active_devices - {device_id}
                
                for other_device_id in other_devices:
                    await self.websocket_manager.send_to_device(other_device_id, notification)
                    
        except Exception as e:
            self.logger.error(f"Device join notification failed: {str(e)}")


class MobileDesktopSessionSync:
    """Specialized sync for mobile-desktop session continuity"""
    
    def __init__(self, config: CrossDeviceConfig):
        self.config = config
        self.synchronizer = DeviceSessionSynchronizer(config)
        self.logger = get_logger(self.__class__.__name__)
    
    async def optimize_mobile_sync(self, session_id: str, device_id: str) -> bool:
        """Optimize sync for mobile devices (battery, network)"""
        
        try:
            device_info = self.synchronizer.device_registry.get(device_id)
            
            if not device_info or device_info.device_type not in [DeviceType.MOBILE_PHONE, DeviceType.TABLET]:
                return False
            
            # Battery optimization
            if self.config.battery_optimization and device_info.battery_level and device_info.battery_level < 20:
                # Reduce sync frequency for low battery
                await self._reduce_sync_frequency(session_id, device_id)
            
            # Network optimization
            if device_info.network_type == "cellular":
                # Compress sync data more aggressively
                await self._enable_aggressive_compression(session_id, device_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mobile sync optimization failed: {str(e)}")
            return False
    
    async def _reduce_sync_frequency(self, session_id: str, device_id: str):
        """Reduce sync frequency for battery optimization"""
        # Implementation would adjust sync intervals
        pass
    
    async def _enable_aggressive_compression(self, session_id: str, device_id: str):
        """Enable aggressive compression for cellular networks"""
        # Implementation would enable compression
        pass


class SessionContinuityManager:
    """Manages session continuity across device switches"""
    
    def __init__(self, config: CrossDeviceConfig):
        self.config = config
        self.synchronizer = DeviceSessionSynchronizer(config)
        self.mobile_sync = MobileDesktopSessionSync(config)
        self.logger = get_logger(self.__class__.__name__)
    
    async def ensure_continuity(self, session_id: str) -> bool:
        """Ensure session continuity across all devices"""
        
        try:
            session_state = self.synchronizer.session_states.get(session_id)
            
            if not session_state:
                return False
            
            # Check sync status across devices
            sync_issues = await self._check_sync_issues(session_id)
            
            if sync_issues:
                # Resolve sync issues
                await self._resolve_sync_issues(session_id, sync_issues)
            
            # Validate state consistency
            consistency_check = await self._validate_state_consistency(session_id)
            
            return consistency_check
            
        except Exception as e:
            self.logger.error(f"Session continuity check failed: {str(e)}")
            return False
    
    async def _check_sync_issues(self, session_id: str) -> List[Dict[str, Any]]:
        """Check for synchronization issues"""
        
        issues = []
        
        try:
            session_state = self.synchronizer.session_states.get(session_id)
            
            if session_state:
                for device_id in session_state.active_devices:
                    device_session = await self.synchronizer._get_device_session(device_id)
                    
                    if device_session:
                        if device_session.sync_status in [SyncStatus.CONFLICT, SyncStatus.FAILED]:
                            issues.append({
                                "device_id": device_id,
                                "issue_type": device_session.sync_status.value,
                                "pending_operations": len(device_session.pending_operations)
                            })
        
        except Exception as e:
            self.logger.error(f"Sync issues check failed: {str(e)}")
        
        return issues
    
    async def _resolve_sync_issues(self, session_id: str, issues: List[Dict[str, Any]]):
        """Resolve synchronization issues"""
        
        for issue in issues:
            try:
                device_id = issue["device_id"]
                issue_type = issue["issue_type"]
                
                if issue_type == "conflict":
                    await self._resolve_sync_conflict(session_id, device_id)
                elif issue_type == "failed":
                    await self._retry_failed_sync(session_id, device_id)
                    
            except Exception as e:
                self.logger.error(f"Sync issue resolution failed: {str(e)}")
    
    async def _resolve_sync_conflict(self, session_id: str, device_id: str):
        """Resolve sync conflict for device"""
        # Implementation would resolve conflicts based on strategy
        pass
    
    async def _retry_failed_sync(self, session_id: str, device_id: str):
        """Retry failed sync for device"""
        # Implementation would retry sync operations
        pass
    
    async def _validate_state_consistency(self, session_id: str) -> bool:
        """Validate state consistency across devices"""
        
        try:
            session_state = self.synchronizer.session_states.get(session_id)
            
            if not session_state:
                return False
            
            # Check if all devices have same sync version
            target_version = session_state.sync_version
            
            for device_id in session_state.active_devices:
                device_session = await self.synchronizer._get_device_session(device_id)
                
                if device_session:
                    # Check version consistency (allow small variance)
                    version_diff = abs(target_version - device_session.sync_status.value if hasattr(device_session.sync_status, 'value') else 0)
                    
                    if version_diff > 5:  # Allow up to 5 version difference
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"State consistency validation failed: {str(e)}")
            return False


class CrossDeviceSessionBridge:
    """Main cross-device session bridge controller"""
    
    def __init__(self, config: Optional[CrossDeviceConfig] = None):
        self.config = config or CrossDeviceConfig()
        self.synchronizer = DeviceSessionSynchronizer(self.config)
        self.mobile_sync = MobileDesktopSessionSync(self.config)
        self.continuity_manager = SessionContinuityManager(self.config)
        self.logger = get_logger(self.__class__.__name__)
    
    async def initialize(self):
        """Initialize cross-device session bridge"""
        
        await self.synchronizer.start_synchronization()
        self.logger.info("Cross-device session bridge initialized")
    
    async def shutdown(self):
        """Shutdown cross-device session bridge"""
        
        await self.synchronizer.stop_synchronization()
        self.logger.info("Cross-device session bridge shutdown")
    
    # Expose synchronizer methods
    async def register_device(self, device_id: str, device_info: Dict[str, Any], user_id: str) -> bool:
        return await self.synchronizer.register_device(device_id, device_info, user_id)
    
    async def start_session(self, session_id: str, device_id: str, user_id: str) -> bool:
        return await self.synchronizer.start_session_on_device(session_id, device_id, user_id)
    
    async def sync_session(self, session_id: str, device_id: str, changes: Dict[str, Any]) -> bool:
        return await self.synchronizer.sync_session_state(session_id, device_id, changes)
    
    async def handoff_session(self, session_id: str, from_device: str, to_device: str, reason: HandoffReason = HandoffReason.USER_INITIATED) -> bool:
        return await self.synchronizer.handoff_session(session_id, from_device, to_device, reason)
    
    async def ensure_continuity(self, session_id: str) -> bool:
        return await self.continuity_manager.ensure_continuity(session_id)
    
    async def get_session_devices(self, session_id: str) -> List[str]:
        """Get list of devices active in session"""
        
        session_state = self.synchronizer.session_states.get(session_id)
        return list(session_state.active_devices) if session_state else []
    
    async def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device information"""
        
        return self.synchronizer.device_registry.get(device_id)
    
    async def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bridge statistics"""
        
        try:
            return {
                "active_sessions": len(self.synchronizer.session_states),
                "registered_devices": len(self.synchronizer.device_registry),
                "sync_queue_size": self.synchronizer.sync_queue.qsize(),
                "configuration": {
                    "sync_interval": self.config.sync_interval,
                    "max_devices_per_session": self.config.max_devices_per_session,
                    "handoff_timeout": self.config.handoff_timeout,
                    "enable_predictive_sync": self.config.enable_predictive_sync,
                    "enable_background_sync": self.config.enable_background_sync,
                    "battery_optimization": self.config.battery_optimization
                }
            }
            
        except Exception as e:
            self.logger.error(f"Statistics calculation failed: {str(e)}")
            return {}
