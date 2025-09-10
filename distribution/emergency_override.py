"""
Emergency Override System
========================

Enterprise-grade emergency override system for critical content publication.
Handles urgent posts, crisis management, and system-wide overrides.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class EmergencyLevel(Enum):
    """Emergency severity levels"""
    CRITICAL = 1    # System-wide emergency (security breach, major outage)
    URGENT = 2      # Time-sensitive but localized (breaking news, PR crisis)
    HIGH = 3        # Important but not urgent (product launch, announcement)
    MODERATE = 4    # Standard override (queue jumping)
    LOW = 5         # Minor priority adjustment

class OverrideType(Enum):
    """Types of emergency overrides"""
    QUEUE_BYPASS = "queue_bypass"          # Skip entire queue
    PRIORITY_BOOST = "priority_boost"      # Move to front of queue
    PLATFORM_TAKEOVER = "platform_takeover"  # Take control of platform
    CONTENT_REPLACEMENT = "content_replacement"  # Replace scheduled content
    SYSTEM_PAUSE = "system_pause"          # Pause all publishing
    CRISIS_MODE = "crisis_mode"            # Enter crisis management mode
    ROLLBACK = "rollback"                  # Rollback recent publications
    BLACKOUT = "blackout"                  # Stop all communications

class OverrideStatus(Enum):
    """Status of override requests"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"

class EmergencyReason(Enum):
    """Reasons for emergency overrides"""
    SECURITY_BREACH = "security_breach"
    PR_CRISIS = "pr_crisis"
    BREAKING_NEWS = "breaking_news"
    SYSTEM_OUTAGE = "system_outage"
    LEGAL_REQUIREMENT = "legal_requirement"
    CONTENT_ERROR = "content_error"
    PLATFORM_ISSUE = "platform_issue"
    REPUTATION_THREAT = "reputation_threat"
    COMPLIANCE_VIOLATION = "compliance_violation"
    TECHNICAL_FAILURE = "technical_failure"

@dataclass
class EmergencyOverride:
    """Emergency override request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: EmergencyLevel = EmergencyLevel.MODERATE
    override_type: OverrideType = OverrideType.PRIORITY_BOOST
    reason: EmergencyReason = EmergencyReason.CONTENT_ERROR
    description: str = ""
    requested_by: str = ""
    approved_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    status: OverrideStatus = OverrideStatus.PENDING
    affected_platforms: List[str] = field(default_factory=list)
    affected_content_ids: List[str] = field(default_factory=list)
    replacement_content: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = True
    auto_expire_minutes: int = 60
    callback_url: Optional[str] = None

@dataclass
class OverrideAction:
    """Action taken during override"""
    action_type: str
    timestamp: datetime
    details: Dict[str, Any]
    result: bool
    error_message: Optional[str] = None

@dataclass
class EmergencyLog:
    """Emergency override log entry"""
    override_id: str
    timestamp: datetime
    event_type: str
    details: Dict[str, Any]
    severity: EmergencyLevel
    user_id: Optional[str] = None

class EmergencyAuthority(ABC):
    """Abstract base class for emergency authorities"""
    
    @abstractmethod
    async def can_authorize(self, override: EmergencyOverride, user_id: str) -> bool:
        """Check if user can authorize this override"""
        pass
    
    @abstractmethod
    async def get_required_approvals(self, override: EmergencyOverride) -> int:
        """Get number of required approvals"""
        pass

class DefaultEmergencyAuthority(EmergencyAuthority):
    """Default emergency authority implementation"""
    
    def __init__(self):
        self.authorized_users = {
            "admin": [EmergencyLevel.CRITICAL, EmergencyLevel.URGENT, EmergencyLevel.HIGH, EmergencyLevel.MODERATE, EmergencyLevel.LOW],
            "manager": [EmergencyLevel.URGENT, EmergencyLevel.HIGH, EmergencyLevel.MODERATE, EmergencyLevel.LOW],
            "supervisor": [EmergencyLevel.HIGH, EmergencyLevel.MODERATE, EmergencyLevel.LOW],
            "operator": [EmergencyLevel.MODERATE, EmergencyLevel.LOW]
        }
        
        self.approval_requirements = {
            EmergencyLevel.CRITICAL: 2,  # Requires 2 approvals
            EmergencyLevel.URGENT: 1,
            EmergencyLevel.HIGH: 1,
            EmergencyLevel.MODERATE: 0,  # Auto-approved
            EmergencyLevel.LOW: 0
        }
    
    async def can_authorize(self, override: EmergencyOverride, user_id: str) -> bool:
        """Check if user can authorize this override"""
        # Simple role-based check (in production, integrate with proper auth system)
        user_role = self._get_user_role(user_id)
        authorized_levels = self.authorized_users.get(user_role, [])
        return override.level in authorized_levels
    
    async def get_required_approvals(self, override: EmergencyOverride) -> int:
        """Get number of required approvals"""
        return self.approval_requirements.get(override.level, 1)
    
    def _get_user_role(self, user_id: str) -> str:
        """Get user role (simplified - integrate with actual auth system)"""
        # In production, this would query the user management system
        if user_id.startswith("admin"):
            return "admin"
        elif user_id.startswith("manager"):
            return "manager"
        elif user_id.startswith("supervisor"):
            return "supervisor"
        else:
            return "operator"

class EmergencyOverrideSystem:
    """Main emergency override system"""
    
    def __init__(self, authority: Optional[EmergencyAuthority] = None):
        self.authority = authority or DefaultEmergencyAuthority()
        self.active_overrides: Dict[str, EmergencyOverride] = {}
        self.override_history: List[EmergencyOverride] = []
        self.emergency_logs: List[EmergencyLog] = []
        self.actions_taken: Dict[str, List[OverrideAction]] = {}
        
        # Callbacks for different override types
        self.override_handlers: Dict[OverrideType, Callable] = {}
        
        # Configuration
        self.max_active_overrides = 10
        self.auto_cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.now(timezone.utc)
        
        # Emergency contacts
        self.emergency_contacts = []
        self.notification_channels = []
    
    async def request_override(
        self, 
        override: EmergencyOverride,
        requester_id: str
    ) -> str:
        """Request an emergency override"""
        try:
            # Set requester
            override.requested_by = requester_id
            
            # Auto-expire time
            if not override.expires_at and override.auto_expire_minutes > 0:
                override.expires_at = (
                    datetime.now(timezone.utc) + 
                    timedelta(minutes=override.auto_expire_minutes)
                )
            
            # Check if approval is required
            required_approvals = await self.authority.get_required_approvals(override)
            
            if required_approvals == 0:
                # Auto-approve
                override.requires_approval = False
                override.approved_by = "system"
                override.status = OverrideStatus.ACTIVE
                
                # Execute immediately
                await self._execute_override(override)
            else:
                # Require manual approval
                override.requires_approval = True
                override.status = OverrideStatus.PENDING
            
            # Store override
            self.active_overrides[override.id] = override
            
            # Log the request
            await self._log_emergency_event(
                override.id,
                "override_requested",
                {
                    "level": override.level.name,
                    "type": override.override_type.value,
                    "reason": override.reason.value,
                    "requester": requester_id
                },
                override.level,
                requester_id
            )
            
            # Send notifications
            await self._send_emergency_notification(override, "requested")
            
            logger.info(f"Emergency override {override.id} requested by {requester_id}")
            
            return override.id
            
        except Exception as e:
            logger.error(f"Failed to request emergency override: {e}")
            raise
    
    async def approve_override(
        self, 
        override_id: str,
        approver_id: str,
        additional_notes: Optional[str] = None
    ) -> bool:
        """Approve an emergency override"""
        try:
            if override_id not in self.active_overrides:
                raise ValueError(f"Override {override_id} not found")
            
            override = self.active_overrides[override_id]
            
            if override.status != OverrideStatus.PENDING:
                raise ValueError(f"Override {override_id} is not pending approval")
            
            # Check authorization
            can_approve = await self.authority.can_authorize(override, approver_id)
            if not can_approve:
                raise PermissionError(f"User {approver_id} cannot approve this override")
            
            # Approve
            override.approved_by = approver_id
            override.status = OverrideStatus.ACTIVE
            
            if additional_notes:
                override.metadata["approval_notes"] = additional_notes
            
            # Execute the override
            success = await self._execute_override(override)
            
            if not success:
                override.status = OverrideStatus.FAILED
                return False
            
            # Log approval
            await self._log_emergency_event(
                override.id,
                "override_approved",
                {
                    "approver": approver_id,
                    "notes": additional_notes
                },
                override.level,
                approver_id
            )
            
            # Send notifications
            await self._send_emergency_notification(override, "approved")
            
            logger.info(f"Emergency override {override_id} approved by {approver_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve emergency override: {e}")
            raise
    
    async def cancel_override(
        self, 
        override_id: str,
        canceller_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel an emergency override"""
        try:
            if override_id not in self.active_overrides:
                raise ValueError(f"Override {override_id} not found")
            
            override = self.active_overrides[override_id]
            
            # Check authorization (same as approval for simplicity)
            can_cancel = await self.authority.can_authorize(override, canceller_id)
            if not can_cancel:
                raise PermissionError(f"User {canceller_id} cannot cancel this override")
            
            # Update status
            override.status = OverrideStatus.CANCELLED
            override.metadata["cancelled_by"] = canceller_id
            override.metadata["cancellation_reason"] = reason
            
            # Execute cancellation actions
            await self._cancel_override_actions(override)
            
            # Move to history
            self.override_history.append(override)
            del self.active_overrides[override_id]
            
            # Log cancellation
            await self._log_emergency_event(
                override.id,
                "override_cancelled",
                {
                    "canceller": canceller_id,
                    "reason": reason
                },
                override.level,
                canceller_id
            )
            
            # Send notifications
            await self._send_emergency_notification(override, "cancelled")
            
            logger.info(f"Emergency override {override_id} cancelled by {canceller_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel emergency override: {e}")
            raise
    
    async def _execute_override(self, override: EmergencyOverride) -> bool:
        """Execute an emergency override"""
        try:
            actions = []
            
            # Execute based on override type
            if override.override_type == OverrideType.QUEUE_BYPASS:
                success = await self._execute_queue_bypass(override)
                actions.append(OverrideAction(
                    action_type="queue_bypass",
                    timestamp=datetime.now(timezone.utc),
                    details={"platforms": override.affected_platforms},
                    result=success
                ))
            
            elif override.override_type == OverrideType.PRIORITY_BOOST:
                success = await self._execute_priority_boost(override)
                actions.append(OverrideAction(
                    action_type="priority_boost",
                    timestamp=datetime.now(timezone.utc),
                    details={"content_ids": override.affected_content_ids},
                    result=success
                ))
            
            elif override.override_type == OverrideType.PLATFORM_TAKEOVER:
                success = await self._execute_platform_takeover(override)
                actions.append(OverrideAction(
                    action_type="platform_takeover",
                    timestamp=datetime.now(timezone.utc),
                    details={"platforms": override.affected_platforms},
                    result=success
                ))
            
            elif override.override_type == OverrideType.CONTENT_REPLACEMENT:
                success = await self._execute_content_replacement(override)
                actions.append(OverrideAction(
                    action_type="content_replacement",
                    timestamp=datetime.now(timezone.utc),
                    details={"content_ids": override.affected_content_ids},
                    result=success
                ))
            
            elif override.override_type == OverrideType.SYSTEM_PAUSE:
                success = await self._execute_system_pause(override)
                actions.append(OverrideAction(
                    action_type="system_pause",
                    timestamp=datetime.now(timezone.utc),
                    details={"platforms": override.affected_platforms},
                    result=success
                ))
            
            elif override.override_type == OverrideType.CRISIS_MODE:
                success = await self._execute_crisis_mode(override)
                actions.append(OverrideAction(
                    action_type="crisis_mode",
                    timestamp=datetime.now(timezone.utc),
                    details={"reason": override.reason.value},
                    result=success
                ))
            
            elif override.override_type == OverrideType.ROLLBACK:
                success = await self._execute_rollback(override)
                actions.append(OverrideAction(
                    action_type="rollback",
                    timestamp=datetime.now(timezone.utc),
                    details={"content_ids": override.affected_content_ids},
                    result=success
                ))
            
            elif override.override_type == OverrideType.BLACKOUT:
                success = await self._execute_blackout(override)
                actions.append(OverrideAction(
                    action_type="blackout",
                    timestamp=datetime.now(timezone.utc),
                    details={"platforms": override.affected_platforms},
                    result=success
                ))
            
            else:
                success = False
                actions.append(OverrideAction(
                    action_type="unknown",
                    timestamp=datetime.now(timezone.utc),
                    details={},
                    result=False,
                    error_message=f"Unknown override type: {override.override_type}"
                ))
            
            # Store actions
            self.actions_taken[override.id] = actions
            
            # Log execution
            await self._log_emergency_event(
                override.id,
                "override_executed",
                {
                    "type": override.override_type.value,
                    "success": success,
                    "actions_count": len(actions)
                },
                override.level
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute override {override.id}: {e}")
            
            # Log failure
            await self._log_emergency_event(
                override.id,
                "override_execution_failed",
                {"error": str(e)},
                override.level
            )
            
            return False
    
    async def _execute_queue_bypass(self, override: EmergencyOverride) -> bool:
        """Execute queue bypass override"""
        # Implementation would integrate with queue system
        logger.info(f"Executing queue bypass for override {override.id}")
        
        # Simulate queue bypass
        for platform in override.affected_platforms:
            logger.info(f"Bypassing queue for platform {platform}")
        
        return True
    
    async def _execute_priority_boost(self, override: EmergencyOverride) -> bool:
        """Execute priority boost override"""
        logger.info(f"Executing priority boost for override {override.id}")
        
        # Simulate priority boost
        for content_id in override.affected_content_ids:
            logger.info(f"Boosting priority for content {content_id}")
        
        return True
    
    async def _execute_platform_takeover(self, override: EmergencyOverride) -> bool:
        """Execute platform takeover override"""
        logger.info(f"Executing platform takeover for override {override.id}")
        
        # This would pause all normal publishing and take control
        for platform in override.affected_platforms:
            logger.info(f"Taking control of platform {platform}")
        
        return True
    
    async def _execute_content_replacement(self, override: EmergencyOverride) -> bool:
        """Execute content replacement override"""
        logger.info(f"Executing content replacement for override {override.id}")
        
        if not override.replacement_content:
            logger.error("No replacement content provided")
            return False
        
        # Replace scheduled content
        for content_id in override.affected_content_ids:
            logger.info(f"Replacing content {content_id}")
        
        return True
    
    async def _execute_system_pause(self, override: EmergencyOverride) -> bool:
        """Execute system pause override"""
        logger.info(f"Executing system pause for override {override.id}")
        
        # Pause all publishing activities
        for platform in override.affected_platforms:
            logger.info(f"Pausing publishing for platform {platform}")
        
        return True
    
    async def _execute_crisis_mode(self, override: EmergencyOverride) -> bool:
        """Execute crisis mode override"""
        logger.info(f"Executing crisis mode for override {override.id}")
        
        # Enter crisis management mode
        # - Pause non-essential publishing
        # - Enable emergency channels
        # - Activate crisis response team
        
        return True
    
    async def _execute_rollback(self, override: EmergencyOverride) -> bool:
        """Execute rollback override"""
        logger.info(f"Executing rollback for override {override.id}")
        
        # Rollback recent publications
        for content_id in override.affected_content_ids:
            logger.info(f"Rolling back content {content_id}")
        
        return True
    
    async def _execute_blackout(self, override: EmergencyOverride) -> bool:
        """Execute communication blackout override"""
        logger.info(f"Executing blackout for override {override.id}")
        
        # Stop all communications on affected platforms
        for platform in override.affected_platforms:
            logger.info(f"Initiating blackout for platform {platform}")
        
        return True
    
    async def _cancel_override_actions(self, override: EmergencyOverride):
        """Cancel or reverse override actions"""
        logger.info(f"Cancelling actions for override {override.id}")
        
        # Reverse the actions taken
        if override.id in self.actions_taken:
            for action in self.actions_taken[override.id]:
                if action.action_type == "system_pause":
                    logger.info("Resuming system operations")
                elif action.action_type == "blackout":
                    logger.info("Ending communication blackout")
                # Add more reversal logic as needed
    
    async def _log_emergency_event(
        self,
        override_id: str,
        event_type: str,
        details: Dict[str, Any],
        severity: EmergencyLevel,
        user_id: Optional[str] = None
    ):
        """Log emergency event"""
        log_entry = EmergencyLog(
            override_id=override_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            details=details,
            severity=severity,
            user_id=user_id
        )
        
        self.emergency_logs.append(log_entry)
        
        # In production, also send to centralized logging system
        logger.info(f"Emergency event logged: {event_type} for override {override_id}")
    
    async def _send_emergency_notification(
        self,
        override: EmergencyOverride,
        event_type: str
    ):
        """Send emergency notifications"""
        try:
            notification_data = {
                "override_id": override.id,
                "level": override.level.name,
                "type": override.override_type.value,
                "reason": override.reason.value,
                "description": override.description,
                "event": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Send to configured channels (email, SMS, Slack, etc.)
            for channel in self.notification_channels:
                await self._send_to_channel(channel, notification_data)
            
            # Alert emergency contacts for critical overrides
            if override.level in [EmergencyLevel.CRITICAL, EmergencyLevel.URGENT]:
                for contact in self.emergency_contacts:
                    await self._alert_contact(contact, notification_data)
            
        except Exception as e:
            logger.error(f"Failed to send emergency notification: {e}")
    
    async def _send_to_channel(self, channel: str, data: Dict[str, Any]):
        """Send notification to specific channel"""
        # Implementation would integrate with notification systems
        logger.info(f"Sending emergency notification to {channel}")
    
    async def _alert_contact(self, contact: str, data: Dict[str, Any]):
        """Alert emergency contact"""
        # Implementation would integrate with alerting systems
        logger.info(f"Alerting emergency contact {contact}")
    
    async def cleanup_expired_overrides(self):
        """Clean up expired overrides"""
        current_time = datetime.now(timezone.utc)
        expired_ids = []
        
        for override_id, override in self.active_overrides.items():
            if override.expires_at and current_time > override.expires_at:
                override.status = OverrideStatus.EXPIRED
                expired_ids.append(override_id)
        
        # Move expired overrides to history
        for override_id in expired_ids:
            override = self.active_overrides[override_id]
            self.override_history.append(override)
            del self.active_overrides[override_id]
            
            # Cancel any active actions
            await self._cancel_override_actions(override)
            
            logger.info(f"Expired override {override_id} cleaned up")
    
    async def get_active_overrides(self) -> List[EmergencyOverride]:
        """Get all active overrides"""
        await self.cleanup_expired_overrides()
        return list(self.active_overrides.values())
    
    async def get_override_status(self, override_id: str) -> Optional[EmergencyOverride]:
        """Get status of specific override"""
        if override_id in self.active_overrides:
            return self.active_overrides[override_id]
        
        # Check history
        for override in self.override_history:
            if override.id == override_id:
                return override
        
        return None
    
    async def get_emergency_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity_filter: Optional[EmergencyLevel] = None
    ) -> List[EmergencyLog]:
        """Get emergency logs with optional filtering"""
        logs = self.emergency_logs.copy()
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        if severity_filter:
            logs = [log for log in logs if log.severity == severity_filter]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs
    
    def add_emergency_contact(self, contact: str):
        """Add emergency contact"""
        if contact not in self.emergency_contacts:
            self.emergency_contacts.append(contact)
    
    def add_notification_channel(self, channel: str):
        """Add notification channel"""
        if channel not in self.notification_channels:
            self.notification_channels.append(channel)
    
    def register_override_handler(self, override_type: OverrideType, handler: Callable):
        """Register custom override handler"""
        self.override_handlers[override_type] = handler


# Export main components
__all__ = [
    "EmergencyOverrideSystem",
    "EmergencyOverride",
    "OverrideAction",
    "EmergencyLog",
    "EmergencyAuthority",
    "DefaultEmergencyAuthority",
    "EmergencyLevel",
    "OverrideType",
    "OverrideStatus",
    "EmergencyReason"
]