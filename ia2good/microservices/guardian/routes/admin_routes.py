"""
Guardian Admin Routes
Administration, moderation, audit logs, statistics
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from moderation import get_moderator, ModerationResult
from rate_limiting import get_rate_limiter
from audit import get_audit_logger, AuditAction, AuditLevel
from auth import get_auth_manager, UserRole, Permission, User

router = APIRouter()

# ============================================================================
# AUDIT LOGS
# ============================================================================

@router.get("/admin/audit/logs")
def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get audit logs"""
    audit_logger = get_audit_logger()
    
    # Convert string to enum if provided
    action_enum = AuditAction(action) if action else None
    level_enum = AuditLevel(level) if level else None
    
    logs = audit_logger.get_logs(
        user_id=user_id,
        action=action_enum,
        level=level_enum,
        limit=limit
    )
    
    return {
        "success": True,
        "total": len(logs),
        "logs": [log.dict() for log in logs]
    }

@router.get("/admin/audit/security")
def get_security_events(limit: int = Query(100, le=500)):
    """Get security-related events"""
    audit_logger = get_audit_logger()
    events = audit_logger.get_security_events(limit=limit)
    
    return {
        "success": True,
        "total": len(events),
        "events": [event.dict() for event in events]
    }

@router.get("/admin/audit/user/{user_id}")
def get_user_activity(user_id: str, limit: int = Query(50, le=200)):
    """Get activity for specific user"""
    audit_logger = get_audit_logger()
    activity = audit_logger.get_user_activity(user_id, limit=limit)
    
    return {
        "success": True,
        "user_id": user_id,
        "total": len(activity),
        "activity": [log.dict() for log in activity]
    }

# ============================================================================
# MODERATION
# ============================================================================

@router.post("/admin/moderate/text")
def moderate_text_endpoint(text: str, strict: bool = False):
    """Test text moderation"""
    moderator = get_moderator()
    result = moderator.moderate_text(text, strict=strict)
    
    return {
        "success": True,
        "moderation": result.dict(),
        "filtered_text": moderator.filter_text(text) if not result.is_clean else text
    }

@router.post("/admin/moderate/file")
def moderate_file_endpoint(
    filename: str,
    file_size: int,
    mime_type: Optional[str] = None
):
    """Test file moderation"""
    moderator = get_moderator()
    result = moderator.moderate_file(filename, file_size, mime_type)
    
    return {
        "success": True,
        "moderation": result.dict()
    }

# ============================================================================
# RATE LIMITING
# ============================================================================

@router.get("/admin/ratelimit/check")
def check_rate_limit_endpoint(
    identifier: str,
    limit_type: str = "api_general"
):
    """Check rate limit for identifier"""
    from rate_limiting import RATE_LIMITS
    
    rate_limiter = get_rate_limiter()
    config = RATE_LIMITS.get(limit_type, RATE_LIMITS["api_general"])
    
    remaining = rate_limiter.get_remaining(
        f"{limit_type}:{identifier}",
        config["max_requests"],
        config["window"]
    )
    
    return {
        "success": True,
        "identifier": identifier,
        "limit_type": limit_type,
        "max_requests": config["max_requests"],
        "window_seconds": config["window"],
        "remaining": remaining
    }

@router.post("/admin/ratelimit/reset")
def reset_rate_limit_endpoint(identifier: str, limit_type: str):
    """Reset rate limit for identifier"""
    rate_limiter = get_rate_limiter()
    rate_limiter.reset(f"{limit_type}:{identifier}")
    
    return {
        "success": True,
        "message": f"Rate limit reset for {identifier}"
    }

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/admin/users")
def list_users():
    """List all users"""
    auth_manager = get_auth_manager()
    
    users_list = []
    for user in auth_manager.users.values():
        users_list.append({
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_banned": user.is_banned,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    
    return {
        "success": True,
        "total": len(users_list),
        "users": users_list
    }

@router.post("/admin/users/create")
def create_user(
    username: str,
    email: Optional[str] = None,
    role: UserRole = UserRole.VOLUNTEER
):
    """Create a new user"""
    auth_manager = get_auth_manager()
    user = auth_manager.create_user(username, email, role)
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.USER_REGISTER,
        user_id=user.user_id,
        username=user.username,
        details={"role": user.role, "email": email}
    )
    
    return {
        "success": True,
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/admin/users/{user_id}/ban")
def ban_user(user_id: str):
    """Ban a user"""
    auth_manager = get_auth_manager()
    auth_manager.ban_user(user_id)
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.USER_BANNED,
        level=AuditLevel.WARNING,
        user_id=user_id,
        resource_type="user",
        resource_id=user_id
    )
    
    return {
        "success": True,
        "message": f"User {user_id} banned"
    }

@router.post("/admin/users/{user_id}/unban")
def unban_user(user_id: str):
    """Unban a user"""
    auth_manager = get_auth_manager()
    auth_manager.unban_user(user_id)
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.USER_UNBANNED,
        user_id=user_id,
        resource_type="user",
        resource_id=user_id
    )
    
    return {
        "success": True,
        "message": f"User {user_id} unbanned"
    }

@router.post("/admin/users/{user_id}/role")
def change_user_role(user_id: str, new_role: UserRole):
    """Change user role"""
    auth_manager = get_auth_manager()
    auth_manager.change_role(user_id, new_role)
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.USER_ROLE_CHANGED,
        user_id=user_id,
        resource_type="user",
        resource_id=user_id,
        details={"new_role": new_role}
    )
    
    return {
        "success": True,
        "message": f"User {user_id} role changed to {new_role}"
    }

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/admin/stats/overview")
def get_platform_stats():
    """Get overall platform statistics"""
    audit_logger = get_audit_logger()
    auth_manager = get_auth_manager()
    
    # Count events by type
    logs = audit_logger.logs
    event_counts = {}
    for log in logs:
        event_counts[log.action] = event_counts.get(log.action, 0) + 1
    
    # Security events
    security_events = audit_logger.get_security_events(limit=100)
    
    # User stats
    total_users = len(auth_manager.users)
    verified_users = sum(1 for u in auth_manager.users.values() if u.is_verified)
    banned_users = sum(1 for u in auth_manager.users.values() if u.is_banned)
    
    # Role distribution
    role_counts = {}
    for user in auth_manager.users.values():
        role_counts[user.role] = role_counts.get(user.role, 0) + 1
    
    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat(),
        "audit": {
            "total_logs": len(logs),
            "security_events": len(security_events),
            "event_types": event_counts
        },
        "users": {
            "total": total_users,
            "verified": verified_users,
            "banned": banned_users,
            "by_role": role_counts
        }
    }

@router.get("/admin/stats/activity")
def get_activity_stats(hours: int = Query(24, le=168)):
    """Get activity statistics for last N hours"""
    audit_logger = get_audit_logger()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    recent_logs = [log for log in audit_logger.logs if log.timestamp >= cutoff]
    
    # Count by hour
    hourly_counts = {}
    for log in recent_logs:
        hour = log.timestamp.replace(minute=0, second=0, microsecond=0)
        hour_str = hour.isoformat()
        hourly_counts[hour_str] = hourly_counts.get(hour_str, 0) + 1
    
    # Top users
    user_counts = {}
    for log in recent_logs:
        if log.user_id:
            user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1
    
    top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "success": True,
        "period_hours": hours,
        "total_events": len(recent_logs),
        "hourly_activity": hourly_counts,
        "top_users": [{"user_id": uid, "events": count} for uid, count in top_users]
    }
