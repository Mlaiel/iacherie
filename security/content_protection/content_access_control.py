"""
Content Access Control System
============================

Advanced multi-layered access control system for content protection with
role-based permissions, geographic restrictions, device management,
and real-time access monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import ipaddress
from functools import wraps


class AccessLevel(Enum):
    """Access levels for content"""
    NONE = "none"
    VIEW = "view"
    DOWNLOAD = "download"
    MODIFY = "modify"
    ADMIN = "admin"
    OWNER = "owner"


class PermissionType(Enum):
    """Types of permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    MONETIZE = "monetize"
    DISTRIBUTE = "distribute"
    MODIFY_PERMISSIONS = "modify_permissions"


class RestrictionType(Enum):
    """Types of access restrictions"""
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"
    DEVICE_BASED = "device_based"
    IP_BASED = "ip_based"
    USER_AGENT = "user_agent"
    REFERRER = "referrer"
    CONCURRENT_SESSIONS = "concurrent_sessions"


class AccessResult(Enum):
    """Results of access attempts"""
    GRANTED = "granted"
    DENIED = "denied"
    RESTRICTED = "restricted"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class AccessPolicy:
    """Access control policy definition"""
    policy_id: str
    content_id: str
    owner_id: str
    policy_name: str
    access_levels: Dict[str, AccessLevel]  # role -> access_level
    permissions: Dict[str, List[PermissionType]]  # role -> permissions
    restrictions: List[Dict[str, Any]]
    expiration_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class AccessRequest:
    """Access request structure"""
    request_id: str
    user_id: str
    content_id: str
    requested_permissions: List[PermissionType]
    request_context: Dict[str, Any]  # IP, device, location, etc.
    requested_at: datetime
    expires_at: Optional[datetime] = None
    status: str = "pending"


@dataclass
class AccessGrant:
    """Access grant/token"""
    grant_id: str
    policy_id: str
    user_id: str
    content_id: str
    granted_permissions: List[PermissionType]
    access_level: AccessLevel
    granted_at: datetime
    expires_at: datetime
    session_data: Dict[str, Any]
    usage_count: int = 0
    last_accessed: Optional[datetime] = None
    is_active: bool = True


@dataclass
class AccessLog:
    """Access attempt log entry"""
    log_id: str
    user_id: str
    content_id: str
    access_result: AccessResult
    attempted_action: str
    request_context: Dict[str, Any]
    policy_applied: Optional[str]
    denial_reason: Optional[str]
    timestamp: datetime
    session_id: Optional[str] = None


class ContentAccessControl:
    """
    Advanced Content Access Control System
    
    Provides comprehensive access control capabilities:
    - Role-based access control (RBAC)
    - Attribute-based access control (ABAC)
    - Geographic and temporal restrictions
    - Device and IP-based controls
    - Real-time access monitoring
    - Session management
    - Permission delegation
    - Audit logging and compliance
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize content access control system"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage (in production, use database with caching)
        self.policies: Dict[str, AccessPolicy] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.access_grants: Dict[str, AccessGrant] = {}
        self.access_logs: List[AccessLog] = []
        
        # Active sessions tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        
        # Default roles and permissions
        self.default_roles = {
            'viewer': {
                'access_level': AccessLevel.VIEW,
                'permissions': [PermissionType.READ]
            },
            'contributor': {
                'access_level': AccessLevel.MODIFY,
                'permissions': [PermissionType.READ, PermissionType.WRITE, PermissionType.SHARE]
            },
            'moderator': {
                'access_level': AccessLevel.ADMIN,
                'permissions': [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, 
                              PermissionType.SHARE, PermissionType.MODIFY_PERMISSIONS]
            },
            'owner': {
                'access_level': AccessLevel.OWNER,
                'permissions': list(PermissionType)
            }
        }
        
        # Geographic data (simplified - in production use GeoIP database)
        self.country_codes = {
            'US': 'United States',
            'CA': 'Canada',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'JP': 'Japan',
            'AU': 'Australia'
        }
        
        # Performance metrics
        self.metrics = {
            'total_policies': 0,
            'access_requests': 0,
            'access_granted': 0,
            'access_denied': 0,
            'active_sessions': 0,
            'policy_violations': 0
        }
        
        self.logger.info("Content Access Control System initialized")

    async def create_access_policy(self, 
                                 content_id: str,
                                 owner_id: str,
                                 policy_name: str,
                                 role_permissions: Dict[str, List[str]] = None,
                                 restrictions: List[Dict[str, Any]] = None) -> AccessPolicy:
        """Create new access control policy"""
        
        policy_id = str(uuid.uuid4())
        
        # Set default permissions if none provided
        if role_permissions is None:
            role_permissions = {
                'owner': ['read', 'write', 'delete', 'share', 'monetize', 'distribute', 'modify_permissions'],
                'viewer': ['read']
            }
        
        # Convert permission strings to enums
        access_levels = {}
        permissions = {}
        
        for role, perms in role_permissions.items():
            # Determine access level based on permissions
            perm_enums = [PermissionType(p) for p in perms if p in [pt.value for pt in PermissionType]]
            permissions[role] = perm_enums
            
            # Assign access level
            if PermissionType.MODIFY_PERMISSIONS in perm_enums:
                access_levels[role] = AccessLevel.OWNER
            elif PermissionType.DELETE in perm_enums:
                access_levels[role] = AccessLevel.ADMIN
            elif PermissionType.WRITE in perm_enums:
                access_levels[role] = AccessLevel.MODIFY
            elif PermissionType.SHARE in perm_enums:
                access_levels[role] = AccessLevel.DOWNLOAD
            else:
                access_levels[role] = AccessLevel.VIEW
        
        policy = AccessPolicy(
            policy_id=policy_id,
            content_id=content_id,
            owner_id=owner_id,
            policy_name=policy_name,
            access_levels=access_levels,
            permissions=permissions,
            restrictions=restrictions or []
        )
        
        self.policies[policy_id] = policy
        self.metrics['total_policies'] += 1
        
        self.logger.info(f"Access policy created: {policy_id} for content: {content_id}")
        return policy

    async def request_access(self, 
                           user_id: str,
                           content_id: str,
                           requested_permissions: List[str],
                           request_context: Dict[str, Any] = None) -> AccessRequest:
        """Request access to content"""
        
        request_id = str(uuid.uuid4())
        
        # Convert permission strings to enums
        perm_enums = [PermissionType(p) for p in requested_permissions 
                     if p in [pt.value for pt in PermissionType]]
        
        request = AccessRequest(
            request_id=request_id,
            user_id=user_id,
            content_id=content_id,
            requested_permissions=perm_enums,
            request_context=request_context or {},
            requested_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour expiration
        )
        
        self.access_requests[request_id] = request
        self.metrics['access_requests'] += 1
        
        self.logger.info(f"Access requested: {request_id} by user: {user_id}")
        return request

    async def evaluate_access(self, 
                            user_id: str,
                            content_id: str,
                            requested_action: str,
                            context: Dict[str, Any] = None) -> Tuple[AccessResult, Optional[AccessGrant]]:
        """Evaluate access request against policies"""
        
        context = context or {}
        
        # Find applicable policies
        applicable_policies = [
            p for p in self.policies.values() 
            if p.content_id == content_id and p.is_active
        ]
        
        if not applicable_policies:
            await self._log_access_attempt(
                user_id, content_id, AccessResult.DENIED, 
                requested_action, context, None, "No applicable policy found"
            )
            return AccessResult.DENIED, None
        
        # Use the most restrictive policy (or implement policy combination logic)
        policy = applicable_policies[0]
        
        # Determine user role (simplified - in production, get from user service)
        user_role = await self._determine_user_role(user_id, content_id, policy)
        
        # Check if user has required permissions
        if user_role not in policy.permissions:
            await self._log_access_attempt(
                user_id, content_id, AccessResult.DENIED,
                requested_action, context, policy.policy_id, f"User role '{user_role}' not in policy"
            )
            return AccessResult.DENIED, None
        
        required_permission = self._action_to_permission(requested_action)
        user_permissions = policy.permissions[user_role]
        
        if required_permission not in user_permissions:
            await self._log_access_attempt(
                user_id, content_id, AccessResult.DENIED,
                requested_action, context, policy.policy_id, f"Permission '{required_permission.value}' not granted"
            )
            return AccessResult.DENIED, None
        
        # Check restrictions
        restriction_result = await self._check_restrictions(policy, user_id, context)
        if not restriction_result['allowed']:
            await self._log_access_attempt(
                user_id, content_id, AccessResult.RESTRICTED,
                requested_action, context, policy.policy_id, restriction_result['reason']
            )
            return AccessResult.RESTRICTED, None
        
        # Create access grant
        grant = await self._create_access_grant(
            policy, user_id, user_role, user_permissions, context
        )
        
        await self._log_access_attempt(
            user_id, content_id, AccessResult.GRANTED,
            requested_action, context, policy.policy_id, None
        )
        
        self.metrics['access_granted'] += 1
        return AccessResult.GRANTED, grant

    async def validate_access_grant(self, grant_id: str, 
                                  requested_action: str) -> bool:
        """Validate existing access grant"""
        
        if grant_id not in self.access_grants:
            return False
        
        grant = self.access_grants[grant_id]
        
        # Check if grant is active
        if not grant.is_active:
            return False
        
        # Check expiration
        if datetime.utcnow() > grant.expires_at:
            grant.is_active = False
            return False
        
        # Check if action is permitted
        required_permission = self._action_to_permission(requested_action)
        if required_permission not in grant.granted_permissions:
            return False
        
        # Update usage
        grant.usage_count += 1
        grant.last_accessed = datetime.utcnow()
        
        return True

    async def revoke_access(self, grant_id: str, reason: str = "Manual revocation") -> bool:
        """Revoke access grant"""
        
        if grant_id not in self.access_grants:
            return False
        
        grant = self.access_grants[grant_id]
        grant.is_active = False
        
        # End related sessions
        await self._end_user_sessions(grant.user_id, grant.content_id)
        
        await self._log_access_attempt(
            grant.user_id, grant.content_id, AccessResult.DENIED,
            "access_revoked", {}, None, f"Access revoked: {reason}"
        )
        
        self.logger.info(f"Access revoked: {grant_id}, reason: {reason}")
        return True

    async def _determine_user_role(self, user_id: str, content_id: str, 
                                 policy: AccessPolicy) -> str:
        """Determine user role for content"""
        
        # Check if user is the owner
        if user_id == policy.owner_id:
            return 'owner'
        
        # In production, check user roles from database/service
        # For now, assign based on simple rules
        if user_id.startswith('admin_'):
            return 'moderator'
        elif user_id.startswith('contrib_'):
            return 'contributor'
        else:
            return 'viewer'

    def _action_to_permission(self, action: str) -> PermissionType:
        """Convert action to required permission"""
        
        action_map = {
            'view': PermissionType.READ,
            'read': PermissionType.READ,
            'download': PermissionType.READ,
            'edit': PermissionType.WRITE,
            'modify': PermissionType.WRITE,
            'upload': PermissionType.WRITE,
            'delete': PermissionType.DELETE,
            'remove': PermissionType.DELETE,
            'share': PermissionType.SHARE,
            'monetize': PermissionType.MONETIZE,
            'distribute': PermissionType.DISTRIBUTE,
            'change_permissions': PermissionType.MODIFY_PERMISSIONS
        }
        
        return action_map.get(action.lower(), PermissionType.READ)

    async def _check_restrictions(self, policy: AccessPolicy, 
                                user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check access restrictions"""
        
        for restriction in policy.restrictions:
            restriction_type = RestrictionType(restriction['type'])
            
            if restriction_type == RestrictionType.GEOGRAPHIC:
                result = await self._check_geographic_restriction(restriction, context)
                if not result['allowed']:
                    return result
            
            elif restriction_type == RestrictionType.TIME_BASED:
                result = await self._check_time_restriction(restriction, context)
                if not result['allowed']:
                    return result
            
            elif restriction_type == RestrictionType.DEVICE_BASED:
                result = await self._check_device_restriction(restriction, context)
                if not result['allowed']:
                    return result
            
            elif restriction_type == RestrictionType.IP_BASED:
                result = await self._check_ip_restriction(restriction, context)
                if not result['allowed']:
                    return result
            
            elif restriction_type == RestrictionType.CONCURRENT_SESSIONS:
                result = await self._check_concurrent_sessions(restriction, user_id)
                if not result['allowed']:
                    return result
        
        return {'allowed': True, 'reason': None}

    async def _check_geographic_restriction(self, restriction: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Check geographic access restrictions"""
        
        user_country = context.get('country_code', 'UNKNOWN')
        allowed_countries = restriction.get('allowed_countries', [])
        blocked_countries = restriction.get('blocked_countries', [])
        
        if blocked_countries and user_country in blocked_countries:
            return {
                'allowed': False,
                'reason': f"Access blocked from country: {user_country}"
            }
        
        if allowed_countries and user_country not in allowed_countries:
            return {
                'allowed': False,
                'reason': f"Access not allowed from country: {user_country}"
            }
        
        return {'allowed': True, 'reason': None}

    async def _check_time_restriction(self, restriction: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Check time-based access restrictions"""
        
        now = datetime.utcnow()
        
        # Check time range
        start_time = restriction.get('start_time')
        end_time = restriction.get('end_time')
        
        if start_time and now < datetime.fromisoformat(start_time):
            return {
                'allowed': False,
                'reason': f"Access not available until {start_time}"
            }
        
        if end_time and now > datetime.fromisoformat(end_time):
            return {
                'allowed': False,
                'reason': f"Access expired on {end_time}"
            }
        
        # Check allowed hours (e.g., business hours only)
        allowed_hours = restriction.get('allowed_hours')
        if allowed_hours:
            current_hour = now.hour
            if current_hour not in allowed_hours:
                return {
                    'allowed': False,
                    'reason': f"Access not allowed at hour {current_hour}"
                }
        
        # Check allowed days
        allowed_days = restriction.get('allowed_days')  # 0=Monday, 6=Sunday
        if allowed_days:
            current_day = now.weekday()
            if current_day not in allowed_days:
                return {
                    'allowed': False,
                    'reason': f"Access not allowed on day {current_day}"
                }
        
        return {'allowed': True, 'reason': None}

    async def _check_device_restriction(self, restriction: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Check device-based access restrictions"""
        
        user_agent = context.get('user_agent', '')
        device_id = context.get('device_id', '')
        
        # Check allowed devices
        allowed_devices = restriction.get('allowed_devices', [])
        if allowed_devices and device_id not in allowed_devices:
            return {
                'allowed': False,
                'reason': f"Device not authorized: {device_id}"
            }
        
        # Check blocked devices
        blocked_devices = restriction.get('blocked_devices', [])
        if device_id in blocked_devices:
            return {
                'allowed': False,
                'reason': f"Device blocked: {device_id}"
            }
        
        # Check device types
        allowed_device_types = restriction.get('allowed_device_types', [])
        if allowed_device_types:
            device_type = self._detect_device_type(user_agent)
            if device_type not in allowed_device_types:
                return {
                    'allowed': False,
                    'reason': f"Device type not allowed: {device_type}"
                }
        
        return {'allowed': True, 'reason': None}

    async def _check_ip_restriction(self, restriction: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Check IP-based access restrictions"""
        
        user_ip = context.get('ip_address', '')
        if not user_ip:
            return {'allowed': True, 'reason': None}
        
        try:
            user_ip_obj = ipaddress.ip_address(user_ip)
        except ValueError:
            return {
                'allowed': False,
                'reason': f"Invalid IP address: {user_ip}"
            }
        
        # Check allowed IP ranges
        allowed_ip_ranges = restriction.get('allowed_ip_ranges', [])
        if allowed_ip_ranges:
            allowed = False
            for ip_range in allowed_ip_ranges:
                try:
                    network = ipaddress.ip_network(ip_range, strict=False)
                    if user_ip_obj in network:
                        allowed = True
                        break
                except ValueError:
                    continue
            
            if not allowed:
                return {
                    'allowed': False,
                    'reason': f"IP address not in allowed ranges: {user_ip}"
                }
        
        # Check blocked IP ranges
        blocked_ip_ranges = restriction.get('blocked_ip_ranges', [])
        for ip_range in blocked_ip_ranges:
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
                if user_ip_obj in network:
                    return {
                        'allowed': False,
                        'reason': f"IP address blocked: {user_ip}"
                    }
            except ValueError:
                continue
        
        return {'allowed': True, 'reason': None}

    async def _check_concurrent_sessions(self, restriction: Dict[str, Any], 
                                       user_id: str) -> Dict[str, Any]:
        """Check concurrent session limits"""
        
        max_sessions = restriction.get('max_concurrent_sessions', 1)
        current_sessions = len(self.user_sessions.get(user_id, set()))
        
        if current_sessions >= max_sessions:
            return {
                'allowed': False,
                'reason': f"Maximum concurrent sessions exceeded ({current_sessions}/{max_sessions})"
            }
        
        return {'allowed': True, 'reason': None}

    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent"""
        
        user_agent_lower = user_agent.lower()
        
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            return 'mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            return 'tablet'
        elif 'bot' in user_agent_lower or 'crawler' in user_agent_lower:
            return 'bot'
        else:
            return 'desktop'

    async def _create_access_grant(self, policy: AccessPolicy, user_id: str,
                                 user_role: str, permissions: List[PermissionType],
                                 context: Dict[str, Any]) -> AccessGrant:
        """Create access grant for user"""
        
        grant_id = str(uuid.uuid4())
        
        grant = AccessGrant(
            grant_id=grant_id,
            policy_id=policy.policy_id,
            user_id=user_id,
            content_id=policy.content_id,
            granted_permissions=permissions,
            access_level=policy.access_levels[user_role],
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=8),  # 8-hour session
            session_data=context
        )
        
        self.access_grants[grant_id] = grant
        
        # Create session
        await self._create_session(grant_id, user_id, policy.content_id, context)
        
        return grant

    async def _create_session(self, grant_id: str, user_id: str, 
                            content_id: str, context: Dict[str, Any]):
        """Create user session"""
        
        session_id = str(uuid.uuid4())
        
        session_data = {
            'session_id': session_id,
            'grant_id': grant_id,
            'user_id': user_id,
            'content_id': content_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'context': context
        }
        
        self.active_sessions[session_id] = session_data
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        self.metrics['active_sessions'] += 1

    async def _end_user_sessions(self, user_id: str, content_id: str = None):
        """End user sessions for specific content or all content"""
        
        user_session_ids = self.user_sessions.get(user_id, set()).copy()
        
        for session_id in user_session_ids:
            session = self.active_sessions.get(session_id)
            if session and (content_id is None or session['content_id'] == content_id):
                # Remove session
                del self.active_sessions[session_id]
                self.user_sessions[user_id].discard(session_id)
                self.metrics['active_sessions'] -= 1

    async def _log_access_attempt(self, user_id: str, content_id: str,
                                result: AccessResult, action: str,
                                context: Dict[str, Any], policy_id: Optional[str],
                                denial_reason: Optional[str]):
        """Log access attempt for audit"""
        
        log_id = str(uuid.uuid4())
        
        log_entry = AccessLog(
            log_id=log_id,
            user_id=user_id,
            content_id=content_id,
            access_result=result,
            attempted_action=action,
            request_context=context,
            policy_applied=policy_id,
            denial_reason=denial_reason,
            timestamp=datetime.utcnow()
        )
        
        self.access_logs.append(log_entry)
        
        if result == AccessResult.DENIED:
            self.metrics['access_denied'] += 1
        elif result == AccessResult.RESTRICTED:
            self.metrics['policy_violations'] += 1

    async def update_policy(self, policy_id: str, 
                          updates: Dict[str, Any]) -> bool:
        """Update access policy"""
        
        if policy_id not in self.policies:
            return False
        
        policy = self.policies[policy_id]
        
        # Update allowed fields
        for field, value in updates.items():
            if hasattr(policy, field):
                setattr(policy, field, value)
        
        policy.updated_at = datetime.utcnow()
        
        self.logger.info(f"Policy updated: {policy_id}")
        return True

    async def get_user_permissions(self, user_id: str, 
                                 content_id: str) -> Dict[str, Any]:
        """Get user permissions for content"""
        
        # Find applicable policies
        applicable_policies = [
            p for p in self.policies.values() 
            if p.content_id == content_id and p.is_active
        ]
        
        if not applicable_policies:
            return {
                'user_id': user_id,
                'content_id': content_id,
                'permissions': [],
                'access_level': AccessLevel.NONE.value,
                'restrictions': []
            }
        
        policy = applicable_policies[0]
        user_role = await self._determine_user_role(user_id, content_id, policy)
        
        user_permissions = policy.permissions.get(user_role, [])
        access_level = policy.access_levels.get(user_role, AccessLevel.NONE)
        
        return {
            'user_id': user_id,
            'content_id': content_id,
            'role': user_role,
            'permissions': [p.value for p in user_permissions],
            'access_level': access_level.value,
            'restrictions': policy.restrictions,
            'policy_id': policy.policy_id
        }

    async def get_access_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get access analytics for content"""
        
        # Filter logs for this content
        content_logs = [log for log in self.access_logs if log.content_id == content_id]
        
        # Calculate metrics
        total_attempts = len(content_logs)
        granted_attempts = len([log for log in content_logs if log.access_result == AccessResult.GRANTED])
        denied_attempts = len([log for log in content_logs if log.access_result == AccessResult.DENIED])
        
        # Access rate
        access_rate = (granted_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Popular actions
        action_counts = {}
        for log in content_logs:
            action_counts[log.attempted_action] = action_counts.get(log.attempted_action, 0) + 1
        
        # Recent activity
        recent_logs = [
            log for log in content_logs 
            if log.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        analytics = {
            'content_id': content_id,
            'total_access_attempts': total_attempts,
            'granted_attempts': granted_attempts,
            'denied_attempts': denied_attempts,
            'access_rate_percent': round(access_rate, 2),
            'popular_actions': sorted(action_counts.items(), key=lambda x: x[1], reverse=True),
            'recent_activity_24h': len(recent_logs),
            'unique_users': len(set(log.user_id for log in content_logs)),
            'most_common_denial_reason': self._get_most_common_denial_reason(content_logs)
        }
        
        return analytics

    def _get_most_common_denial_reason(self, logs: List[AccessLog]) -> Optional[str]:
        """Get most common denial reason from logs"""
        
        denial_reasons = [
            log.denial_reason for log in logs 
            if log.access_result == AccessResult.DENIED and log.denial_reason
        ]
        
        if not denial_reasons:
            return None
        
        reason_counts = {}
        for reason in denial_reasons:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return max(reason_counts.items(), key=lambda x: x[1])[0] if reason_counts else None

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall access control system metrics"""
        
        return {
            'metrics': self.metrics,
            'total_active_sessions': len(self.active_sessions),
            'total_access_logs': len(self.access_logs),
            'policies_count': len(self.policies),
            'supported_restrictions': [rt.value for rt in RestrictionType],
            'supported_permissions': [pt.value for pt in PermissionType],
            'system_status': 'operational'
        }

    async def cleanup_expired_grants(self) -> int:
        """Clean up expired access grants and sessions"""
        
        current_time = datetime.utcnow()
        expired_count = 0
        
        # Clean up expired grants
        for grant_id, grant in list(self.access_grants.items()):
            if current_time > grant.expires_at:
                grant.is_active = False
                expired_count += 1
        
        # Clean up expired sessions
        for session_id, session in list(self.active_sessions.items()):
            if current_time > session['created_at'] + timedelta(hours=8):
                user_id = session['user_id']
                del self.active_sessions[session_id]
                self.user_sessions[user_id].discard(session_id)
                self.metrics['active_sessions'] -= 1
        
        self.logger.info(f"Cleaned up {expired_count} expired grants")
        return expired_count


# Utility functions
async def create_access_control_system(config: Dict[str, Any] = None) -> ContentAccessControl:
    """Factory function to create access control system"""
    system = ContentAccessControl(config)
    return system


# Decorator for access control
def require_access(content_id_param: str = 'content_id', 
                  required_action: str = 'view'):
    """Decorator to enforce access control on functions"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get access control system (simplified - in practice, inject as dependency)
            access_system = kwargs.get('access_system')
            user_id = kwargs.get('user_id')
            content_id = kwargs.get(content_id_param)
            
            if access_system and user_id and content_id:
                result, grant = await access_system.evaluate_access(
                    user_id, content_id, required_action, kwargs.get('context', {})
                )
                
                if result != AccessResult.GRANTED:
                    raise PermissionError(f"Access denied for action: {required_action}")
                
                # Add grant to kwargs for downstream use
                kwargs['access_grant'] = grant
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate access control system capabilities"""
        system = await create_access_control_system()
        
        # Create access policy
        policy = await system.create_access_policy(
            content_id="video_123",
            owner_id="creator_456",
            policy_name="Premium Video Access",
            role_permissions={
                'owner': ['read', 'write', 'delete', 'share', 'modify_permissions'],
                'premium_user': ['read', 'download', 'share'],
                'viewer': ['read']
            },
            restrictions=[
                {
                    'type': 'geographic',
                    'allowed_countries': ['US', 'CA', 'GB']
                },
                {
                    'type': 'time_based',
                    'allowed_hours': list(range(9, 17))  # 9 AM to 5 PM
                },
                {
                    'type': 'concurrent_sessions',
                    'max_concurrent_sessions': 3
                }
            ]
        )
        
        print(f"Access policy created: {policy.policy_id}")
        
        # Test access evaluation
        context = {
            'ip_address': '192.168.1.100',
            'country_code': 'US',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'device_id': 'device_123'
        }
        
        result, grant = await system.evaluate_access(
            user_id="user_789",
            content_id="video_123",
            requested_action="view",
            context=context
        )
        
        print(f"Access evaluation result: {result}")
        if grant:
            print(f"Access grant issued: {grant.grant_id}")
            print(f"Permissions: {[p.value for p in grant.granted_permissions]}")
        
        # Get user permissions
        permissions = await system.get_user_permissions("user_789", "video_123")
        print(f"User permissions: {permissions}")
        
        # Get access analytics
        analytics = await system.get_access_analytics("video_123")
        print(f"Access analytics: {analytics}")
        
        # Get system metrics
        metrics = await system.get_system_metrics()
        print(f"System metrics: {metrics}")
    
    asyncio.run(demo())