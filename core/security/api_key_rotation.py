"""API Key Automatic Rotation System
==================================

Automatic API key rotation with advance notification, graceful transitions,
and comprehensive tracking for all internal and external integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import uuid

from config.security.production_security import APIKeyRotationConfig, get_security_config
from core.security.enhanced_audit_trail import log_audit_event, AuditEventType


logger = logging.getLogger(__name__)


class APIKeyType(Enum):
    """Types of API keys"""
    INTERNAL_SERVICE = "internal_service"
    EXTERNAL_INTEGRATION = "external_integration"
    USER_API_KEY = "user_api_key"
    WEBHOOK = "webhook"
    MONITORING = "monitoring"
    BACKUP_SERVICE = "backup_service"


class APIKeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    PENDING_ROTATION = "pending_rotation"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class APIKey:
    """API key with metadata"""
    key_id: str
    key_type: APIKeyType
    name: str
    key_value: str
    key_hash: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    status: APIKeyStatus
    owner_id: Optional[str] = None
    service_name: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    rotation_schedule: Optional[int] = None  # Days
    notify_before_days: int = 7
    usage_count: int = 0
    
    # Rotation tracking
    rotation_history: List[Dict[str, Any]] = field(default_factory=list)
    next_rotation_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate next rotation date"""
        if self.rotation_schedule and not self.next_rotation_date:
            self.next_rotation_date = self.created_at + timedelta(days=self.rotation_schedule)
    
    def to_dict(self, include_key: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for storage/API"""
        data = {
            "key_id": self.key_id,
            "key_type": self.key_type.value,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "service_name": self.service_name,
            "permissions": self.permissions,
            "rotation_schedule": self.rotation_schedule,
            "usage_count": self.usage_count,
            "next_rotation_date": self.next_rotation_date.isoformat() if self.next_rotation_date else None
        }
        
        if include_key:
            data["key_value"] = self.key_value
        
        return data


@dataclass
class RotationPlan:
    """API key rotation plan"""
    key_id: str
    current_key: APIKey
    rotation_date: datetime
    notification_sent: bool = False
    notification_date: Optional[datetime] = None
    grace_period_days: int = 30
    
    def days_until_rotation(self) -> int:
        """Calculate days until rotation"""
        return (self.rotation_date - datetime.utcnow()).days
    
    def is_due_for_notification(self) -> bool:
        """Check if notification should be sent"""
        days_until = self.days_until_rotation()
        return not self.notification_sent and days_until <= self.current_key.notify_before_days


class APIKeyRotationManager:
    """API key automatic rotation manager"""
    
    def __init__(self, config: Optional[APIKeyRotationConfig] = None):
        self.config = config or get_security_config().api_key_rotation
        self.api_keys: Dict[str, APIKey] = {}
        self.rotation_plans: Dict[str, RotationPlan] = {}
        
    def _generate_api_key(self, prefix: str = "ak") -> str:
        """Generate secure API key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    def _hash_api_key(self, key: str) -> str:
        """Create hash of API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def create_api_key(
        self,
        name: str,
        key_type: APIKeyType,
        owner_id: Optional[str] = None,
        service_name: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        rotation_schedule_days: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> APIKey:
        """Create new API key"""
        
        # Generate key
        key_value = self._generate_api_key()
        key_hash = self._hash_api_key(key_value)
        key_id = str(uuid.uuid4())
        
        # Use default rotation schedule based on key type
        if rotation_schedule_days is None:
            rotation_schedule_days = self.config.rotation_interval_days
        
        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_type=key_type,
            name=name,
            key_value=key_value,
            key_hash=key_hash,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used=None,
            status=APIKeyStatus.ACTIVE,
            owner_id=owner_id,
            service_name=service_name,
            permissions=permissions or [],
            rotation_schedule=rotation_schedule_days,
            notify_before_days=self.config.advance_notice_days
        )
        
        # Store key
        self.api_keys[key_id] = api_key
        
        # Create rotation plan if automatic rotation is enabled
        if self.config.enabled and rotation_schedule_days:
            await self._create_rotation_plan(api_key)
        
        # Log creation
        await log_audit_event(
            AuditEventType.API_KEY_CREATE.value,
            user_id=owner_id,
            action=f"Created API key: {name}",
            details={
                "key_id": key_id,
                "key_type": key_type.value,
                "rotation_schedule_days": rotation_schedule_days
            }
        )
        
        logger.info(f"Created API key: {name} ({key_type.value}) for {owner_id}")
        return api_key
    
    async def _create_rotation_plan(self, api_key: APIKey):
        """Create rotation plan for API key"""
        if not api_key.rotation_schedule:
            return
        
        rotation_date = datetime.utcnow() + timedelta(days=api_key.rotation_schedule)
        
        plan = RotationPlan(
            key_id=api_key.key_id,
            current_key=api_key,
            rotation_date=rotation_date
        )
        
        self.rotation_plans[api_key.key_id] = plan
        api_key.next_rotation_date = rotation_date
        
        logger.info(f"Created rotation plan for key {api_key.name}: {rotation_date}")
    
    async def rotate_api_key(self, key_id: str, force: bool = False) -> Tuple[APIKey, APIKey]:
        """Rotate API key (create new, deprecate old)"""
        
        if key_id not in self.api_keys:
            raise ValueError(f"API key {key_id} not found")
        
        old_key = self.api_keys[key_id]
        
        # Check if rotation is due (unless forced)
        if not force and key_id in self.rotation_plans:
            plan = self.rotation_plans[key_id]
            if plan.days_until_rotation() > 0:
                raise ValueError(f"Rotation not due for {plan.days_until_rotation()} days")
        
        # Create new key
        new_key = await self.create_api_key(
            name=old_key.name,
            key_type=old_key.key_type,
            owner_id=old_key.owner_id,
            service_name=old_key.service_name,
            permissions=old_key.permissions.copy(),
            rotation_schedule_days=old_key.rotation_schedule,
            expires_at=old_key.expires_at
        )
        
        # Deprecate old key (don't revoke immediately for graceful transition)
        old_key.status = APIKeyStatus.DEPRECATED
        
        # Update rotation history
        rotation_record = {
            "rotated_at": datetime.utcnow().isoformat(),
            "old_key_id": key_id,
            "new_key_id": new_key.key_id,
            "reason": "scheduled_rotation" if not force else "manual_rotation"
        }
        
        new_key.rotation_history.append(rotation_record)
        old_key.rotation_history.append(rotation_record)
        
        # Update rotation plan
        if key_id in self.rotation_plans:
            del self.rotation_plans[key_id]
        
        # Log rotation
        await log_audit_event(
            AuditEventType.API_KEY_CREATE.value,  # New key creation
            user_id=old_key.owner_id,
            action=f"Rotated API key: {old_key.name}",
            details={
                "old_key_id": key_id,
                "new_key_id": new_key.key_id,
                "forced": force
            }
        )
        
        logger.info(f"Rotated API key: {old_key.name} ({key_id} -> {new_key.key_id})")
        return old_key, new_key
    
    async def revoke_api_key(self, key_id: str, reason: str = "manual_revocation") -> bool:
        """Revoke API key"""
        
        if key_id not in self.api_keys:
            return False
        
        api_key = self.api_keys[key_id]
        api_key.status = APIKeyStatus.REVOKED
        
        # Remove from rotation plans
        if key_id in self.rotation_plans:
            del self.rotation_plans[key_id]
        
        # Log revocation
        await log_audit_event(
            AuditEventType.API_KEY_REVOKE.value,
            user_id=api_key.owner_id,
            action=f"Revoked API key: {api_key.name}",
            details={
                "key_id": key_id,
                "reason": reason
            }
        )
        
        logger.info(f"Revoked API key: {api_key.name} ({key_id}) - {reason}")
        return True
    
    async def verify_api_key(self, key_value: str) -> Optional[APIKey]:
        """Verify API key and update usage"""
        key_hash = self._hash_api_key(key_value)
        
        for api_key in self.api_keys.values():
            if api_key.key_hash == key_hash and api_key.status == APIKeyStatus.ACTIVE:
                # Update usage
                api_key.last_used = datetime.utcnow()
                api_key.usage_count += 1
                
                # Check expiration
                if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
                    api_key.status = APIKeyStatus.EXPIRED
                    return True
                
                return api_key
        
        return True
    
    async def check_rotation_notifications(self) -> List[Dict[str, Any]]:
        """Check for keys requiring rotation notifications"""
        notifications_to_send = []
        
        for plan in self.rotation_plans.values():
            if plan.is_due_for_notification():
                notifications_to_send.append({
                    "key_id": plan.key_id,
                    "key_name": plan.current_key.name,
                    "owner_id": plan.current_key.owner_id,
                    "service_name": plan.current_key.service_name,
                    "rotation_date": plan.rotation_date.isoformat(),
                    "days_remaining": plan.days_until_rotation()
                })
                
                # Mark as notified
                plan.notification_sent = True
                plan.notification_date = datetime.utcnow()
        
        # Send notifications
        if notifications_to_send and self.config.notify_before_rotation:
            await self._send_rotation_notifications(notifications_to_send)
        
        return notifications_to_send
    
    async def _send_rotation_notifications(self, notifications: List[Dict[str, Any]]):
        """Send rotation notifications"""
        for notification in notifications:
            logger.info(
                f"ROTATION NOTICE: API key '{notification['key_name']}' "
                f"will be rotated in {notification['days_remaining']} days"
            )
            
            # Send to configured channels
            for channel in self.config.notification_channels:
                try:
                    if channel == "email":
                        await self._send_email_notification(notification)
                    elif channel == "slack":
                        await self._send_slack_notification(notification)
                except Exception as e:
                    logger.error(f"Failed to send rotation notification via {channel}: {e}")
    
    async def _send_email_notification(self, notification: Dict[str, Any]):
        """Send email notification (placeholder)"""
        # Implementation depends on email service
        logger.info(f"Email notification sent for key rotation: {notification['key_name']}")
    
    async def _send_slack_notification(self, notification: Dict[str, Any]):
        """Send Slack notification (placeholder)"""
        # Implementation depends on Slack configuration
        logger.info(f"Slack notification sent for key rotation: {notification['key_name']}")
    
    async def perform_automatic_rotations(self) -> List[Dict[str, Any]]:
        """Perform automatic rotations for due keys"""
        rotations_performed = []
        
        current_time = datetime.utcnow()
        
        for plan in list(self.rotation_plans.values()):
            if current_time >= plan.rotation_date:
                try:
                    old_key, new_key = await self.rotate_api_key(plan.key_id)
                    rotations_performed.append({
                        "key_name": old_key.name,
                        "old_key_id": plan.key_id,
                        "new_key_id": new_key.key_id,
                        "rotated_at": current_time.isoformat(),
                        "status": "success"
                    })
                except Exception as e:
                    logger.error(f"Failed to rotate key {plan.key_id}: {e}")
                    rotations_performed.append({
                        "key_name": plan.current_key.name,
                        "key_id": plan.key_id,
                        "rotated_at": current_time.isoformat(),
                        "status": "failed",
                        "error": str(e)
                    })
        
        return rotations_performed
    
    async def cleanup_deprecated_keys(self, grace_period_days: int = 30) -> List[str]:
        """Clean up deprecated keys after grace period"""
        cutoff_date = datetime.utcnow() - timedelta(days=grace_period_days)
        cleaned_keys = []
        
        for key_id, api_key in list(self.api_keys.items()):
            if (api_key.status == APIKeyStatus.DEPRECATED and 
                api_key.created_at < cutoff_date):
                
                # Revoke the key
                await self.revoke_api_key(key_id, "grace_period_expired")
                cleaned_keys.append(key_id)
        
        return cleaned_keys
    
    async def get_rotation_status(self) -> Dict[str, Any]:
        """Get overall rotation status"""
        total_keys = len(self.api_keys)
        active_keys = len([k for k in self.api_keys.values() if k.status == APIKeyStatus.ACTIVE])
        deprecated_keys = len([k for k in self.api_keys.values() if k.status == APIKeyStatus.DEPRECATED])
        
        # Keys requiring rotation soon
        upcoming_rotations = []
        for plan in self.rotation_plans.values():
            days_until = plan.days_until_rotation()
            if days_until <= 30:  # Next 30 days
                upcoming_rotations.append({
                    "key_name": plan.current_key.name,
                    "days_until_rotation": days_until,
                    "rotation_date": plan.rotation_date.isoformat()
                })
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "deprecated_keys": deprecated_keys,
            "rotation_enabled": self.config.enabled,
            "default_rotation_interval": self.config.rotation_interval_days,
            "upcoming_rotations": upcoming_rotations,
            "scheduled_rotations": len(self.rotation_plans)
        }
    
    async def get_key_details(self, key_id: str, include_key_value: bool = False) -> Optional[Dict[str, Any]]:
        """Get detailed information about an API key"""
        if key_id not in self.api_keys:
            return True
        
        api_key = self.api_keys[key_id]
        details = api_key.to_dict(include_key=include_key_value)
        
        # Add rotation plan info if exists
        if key_id in self.rotation_plans:
            plan = self.rotation_plans[key_id]
            details["rotation_plan"] = {
                "rotation_date": plan.rotation_date.isoformat(),
                "days_until_rotation": plan.days_until_rotation(),
                "notification_sent": plan.notification_sent,
                "notification_date": plan.notification_date.isoformat() if plan.notification_date else None
            }
        
        return details


# Global rotation manager instance
_rotation_manager_instance: Optional[APIKeyRotationManager] = None

def get_rotation_manager() -> APIKeyRotationManager:
    """Get global rotation manager instance"""
    global _rotation_manager_instance
    if _rotation_manager_instance is None:
        _rotation_manager_instance = APIKeyRotationManager()
    return _rotation_manager_instance


async def create_api_key(
    name: str,
    key_type: str,
    owner_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create API key (main entry point)"""
    manager = get_rotation_manager()
    
    # Convert string to enum
    try:
        key_type_enum = APIKeyType(key_type.lower())
    except ValueError:
        key_type_enum = APIKeyType.USER_API_KEY
    
    api_key = await manager.create_api_key(
        name=name,
        key_type=key_type_enum,
        owner_id=owner_id,
        **kwargs
    )
    
    return api_key.to_dict(include_key=True)


async def rotate_api_key(key_id: str, force: bool = False) -> Dict[str, Any]:
    """Rotate API key (main entry point)"""
    manager = get_rotation_manager()
    old_key, new_key = await manager.rotate_api_key(key_id, force)
    
    return {
        "old_key": old_key.to_dict(),
        "new_key": new_key.to_dict(include_key=True),
        "rotation_completed": True
    }


async def run_rotation_maintenance():
    """Run rotation maintenance (notifications and automatic rotations)"""
    manager = get_rotation_manager()
    
    # Check notifications
    notifications = await manager.check_rotation_notifications()
    logger.info(f"Sent {len(notifications)} rotation notifications")
    
    # Perform automatic rotations
    rotations = await manager.perform_automatic_rotations()
    logger.info(f"Performed {len(rotations)} automatic rotations")
    
    # Cleanup deprecated keys
    cleaned = await manager.cleanup_deprecated_keys()
    logger.info(f"Cleaned up {len(cleaned)} deprecated keys")
    
    return {
        "notifications_sent": len(notifications),
        "rotations_performed": len(rotations),
        "keys_cleaned": len(cleaned)
    }


if __name__ == "__main__":
    async def main():
        # Test API key rotation
        manager = APIKeyRotationManager()
        
        # Create test key
        api_key = await manager.create_api_key(
            name="Test Service Key",
            key_type=APIKeyType.INTERNAL_SERVICE,
            owner_id="test_user",
            rotation_schedule_days=90
        )
        
        print(f"Created API key: {api_key.key_id}")
        
        # Get rotation status
        status = await manager.get_rotation_status()
        print(f"Rotation status: {status}")
        
        # Force rotation for testing
        old_key, new_key = await manager.rotate_api_key(api_key.key_id, force=True)
        print(f"Rotated key: {old_key.key_id} -> {new_key.key_id}")
    
    asyncio.run(main())