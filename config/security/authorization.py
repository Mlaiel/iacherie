"""Authorization Configuration Module
==================================

Advanced role-based access control (RBAC) and permission management
configuration for IA Influencer Agent platform.

Supports fine-grained permissions for content creators, multi-platform
operations, and enterprise-grade authorization workflows.

Business Logic Integration:
- Creator role-based content access
- Platform-specific permissions for distribution
- Content protection authorization levels
- Revenue sharing authorization controls

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum


class CreatorType(Enum):
    """
Content creator types supported by the platform."""

    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class SubscriptionTier(Enum):
    """Subscription tiers with different permission levels."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class Permission(Enum):
    """System permissions for granular access control."""
    # Content permissions
    CONTENT_UPLOAD = "content:upload"
    CONTENT_VIEW = "content:view"
    CONTENT_EDIT = "content:edit"
    CONTENT_DELETE = "content:delete"
    CONTENT_DOWNLOAD = "content:download"
    
    # Content protection permissions
    FINGERPRINT_CREATE = "fingerprint:create"
    FINGERPRINT_MANAGE = "fingerprint:manage"
    PROTECTION_ENABLE = "protection:enable"
    PROTECTION_CONFIGURE = "protection:configure"
    
    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    REPORTS_GENERATE = "reports:generate"
    INSIGHTS_ADVANCED = "insights:advanced"
    
    # Revenue permissions
    REVENUE_VIEW = "revenue:view"
    REVENUE_MANAGE = "revenue:manage"
    PAYMENTS_PROCESS = "payments:process"
    PAYOUTS_REQUEST = "payouts:request"
    
    # Platform integration permissions
    SPOTIFY_CONNECT = "spotify:connect"
    YOUTUBE_CONNECT = "youtube:connect"
    INSTAGRAM_CONNECT = "instagram:connect"
    TIKTOK_CONNECT = "tiktok:connect"
    
    # Collaboration permissions
    COLLABORATE_INVITE = "collaborate:invite"
    COLLABORATE_MANAGE = "collaborate:manage"
    SHARE_REVENUE = "share:revenue"
    
    # Administrative permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_SECURITY = "admin:security"


class Role(Enum):
    """System roles with predefined permission sets."""

    GUEST = "guest"
    CREATOR_FREE = "creator_free"
    CREATOR_BASIC = "creator_basic"
    CREATOR_PRO = "creator_pro"
    CREATOR_ENTERPRISE = "creator_enterprise"
    COLLABORATOR = "collaborator"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class ResourceAccess:
    """Resource-specific access configuration."""
    resource_type: str
    permissions: Set[Permission]
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Content-specific conditions
    max_file_size_mb: Optional[int] = None
    allowed_formats: Optional[List[str]] = None
    daily_upload_limit: Optional[int] = None
    
    # Platform-specific conditions
    platform_restrictions: Optional[List[str]] = None
    geographic_restrictions: Optional[List[str]] = None


@dataclass
class RoleDefinition:
    """
Role definition with permissions and constraints."""
    name: str
    display_name: str
    description: str
    permissions: Set[Permission]
    resource_access: Dict[str, ResourceAccess] = field(default_factory=dict)
    
    # Role constraints
    max_storage_gb: Optional[int] = None
    max_monthly_uploads: Optional[int] = None
    api_rate_limit: Optional[str] = None
    
    # Feature access
    ai_features_enabled: bool = False
    premium_features_enabled: bool = False
    collaboration_features_enabled: bool = False
    
    # Platform integration limits
    max_platform_connections: int = 1
    allowed_platforms: Optional[List[str]] = None


@dataclass
class CreatorPermissionMatrix:
    """
Permission matrix for different creator types and tiers."""
    
    # Free tier permissions by creator type
    free_permissions: Dict[CreatorType, Set[Permission]] = field(default_factory=lambda: {
        CreatorType.MUSICIAN: {
            Permission.CONTENT_UPLOAD,
            Permission.CONTENT_VIEW,
            Permission.FINGERPRINT_CREATE,
            Permission.ANALYTICS_VIEW,
            Permission.SPOTIFY_CONNECT
        },
        CreatorType.BLOGGER: {
            Permission.CONTENT_UPLOAD,
            Permission.CONTENT_VIEW,
            Permission.FINGERPRINT_CREATE,
            Permission.ANALYTICS_VIEW
        },
        CreatorType.PHOTOGRAPHER: {
            Permission.CONTENT_UPLOAD,
            Permission.CONTENT_VIEW,
            Permission.FINGERPRINT_CREATE,
            Permission.INSTAGRAM_CONNECT
        },
        CreatorType.INFLUENCER: {
            Permission.CONTENT_UPLOAD,
            Permission.CONTENT_VIEW,
            Permission.ANALYTICS_VIEW,
            Permission.INSTAGRAM_CONNECT,
            Permission.TIKTOK_CONNECT
        },
        CreatorType.COMEDIAN: {
            Permission.CONTENT_UPLOAD,
            Permission.CONTENT_VIEW,
            Permission.YOUTUBE_CONNECT,
            Permission.TIKTOK_CONNECT
        }
    })
    
    # Professional tier additional permissions
    professional_permissions: Set[Permission] = field(default_factory=lambda: {
        Permission.CONTENT_EDIT,
        Permission.FINGERPRINT_MANAGE,
        Permission.PROTECTION_ENABLE,
        Permission.ANALYTICS_EXPORT,
        Permission.REVENUE_VIEW,
        Permission.COLLABORATE_INVITE
    })
    
    # Enterprise tier additional permissions
    enterprise_permissions: Set[Permission] = field(default_factory=lambda: {
        Permission.CONTENT_DELETE,
        Permission.PROTECTION_CONFIGURE,
        Permission.REPORTS_GENERATE,
        Permission.INSIGHTS_ADVANCED,
        Permission.REVENUE_MANAGE,
        Permission.PAYMENTS_PROCESS,
        Permission.COLLABORATE_MANAGE,
        Permission.SHARE_REVENUE
    })


@dataclass
class ResourceQuotas:
    """
Resource usage quotas by subscription tier."""
    
    quotas_by_tier: Dict[SubscriptionTier, Dict[str, Any]] = field(default_factory=lambda: {
        SubscriptionTier.FREE: {
            "storage_gb": 1,
            "monthly_uploads": 10,
            "fingerprints_count": 50,
            "api_calls_per_hour": 100,
            "platform_connections": 1,
            "collaboration_projects": 1
        },
        SubscriptionTier.BASIC: {
            "storage_gb": 10,
            "monthly_uploads": 100,
            "fingerprints_count": 500,
            "api_calls_per_hour": 500,
            "platform_connections": 3,
            "collaboration_projects": 5
        },
        SubscriptionTier.PROFESSIONAL: {
            "storage_gb": 100,
            "monthly_uploads": 1000,
            "fingerprints_count": 5000,
            "api_calls_per_hour": 2000,
            "platform_connections": 10,
            "collaboration_projects": 25
        },
        SubscriptionTier.ENTERPRISE: {
            "storage_gb": 1000,
            "monthly_uploads": 10000,
            "fingerprints_count": 50000,
            "api_calls_per_hour": 10000,
            "platform_connections": -1,  # unlimited
            "collaboration_projects": -1  # unlimited
        }
    })


@dataclass
class PlatformAccessControl:
    """Platform-specific access control configuration."""
    
    # Platform permissions by tier
    platform_access: Dict[SubscriptionTier, List[str]] = field(default_factory=lambda: {
        SubscriptionTier.FREE: ["spotify"],
        SubscriptionTier.BASIC: ["spotify", "instagram", "youtube"],
        SubscriptionTier.PROFESSIONAL: ["spotify", "instagram", "youtube", "tiktok"],
        SubscriptionTier.ENTERPRISE: ["spotify", "instagram", "youtube", "tiktok", "facebook", "twitter"]
    })
    
    # Platform-specific rate limits
    platform_rate_limits: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "spotify": {"requests_per_hour": 1000, "uploads_per_day": 50},
        "youtube": {"requests_per_hour": 500, "uploads_per_day": 20},
        "instagram": {"requests_per_hour": 200, "posts_per_day": 10},
        "tiktok": {"requests_per_hour": 100, "uploads_per_day": 5}
    })


@dataclass
class CollaborationPermissions:
    """Collaboration-specific permission management."""
    
    # Collaboration roles
    collaboration_roles: Dict[str, Set[Permission]] = field(default_factory=lambda: {
        "owner": {
            Permission.CONTENT_VIEW, Permission.CONTENT_EDIT, Permission.CONTENT_DELETE,
            Permission.COLLABORATE_MANAGE, Permission.SHARE_REVENUE, Permission.ANALYTICS_VIEW
        },
        "editor": {
            Permission.CONTENT_VIEW, Permission.CONTENT_EDIT,
            Permission.ANALYTICS_VIEW
        },
        "viewer": {
            Permission.CONTENT_VIEW, Permission.ANALYTICS_VIEW
        },
        "revenue_partner": {
            Permission.CONTENT_VIEW, Permission.REVENUE_VIEW,
            Permission.ANALYTICS_VIEW
        }
    })
    
    # Revenue sharing permissions
    revenue_sharing_tiers: Dict[SubscriptionTier, Dict[str, Any]] = field(default_factory=lambda: {
        SubscriptionTier.FREE: {"max_partners": 0, "revenue_split_enabled": False},
        SubscriptionTier.BASIC: {"max_partners": 2, "revenue_split_enabled": True},
        SubscriptionTier.PROFESSIONAL: {"max_partners": 10, "revenue_split_enabled": True},
        SubscriptionTier.ENTERPRISE: {"max_partners": -1, "revenue_split_enabled": True}
    })


@dataclass
class SecurityPolicies:
    """Security policies for authorization."""
    
    # IP-based restrictions
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    
    # Time-based restrictions
    time_based_access_enabled: bool = False
    allowed_hours: Dict[str, List[int]] = field(default_factory=dict)  # day -> hours
    
    # Geographic restrictions
    geographic_restrictions_enabled: bool = False
    blocked_countries: List[str] = field(default_factory=list)
    
    # Device-based restrictions
    device_fingerprinting_enabled: bool = True
    max_devices_per_user: int = 5
    
    # Session security
    concurrent_sessions_limit: int = 3
    session_ip_validation: bool = True


@dataclass
class AuthorizationConfig:
    """
Main authorization configuration container."""
    
    # Core configuration
    permission_matrix: CreatorPermissionMatrix = field(default_factory=CreatorPermissionMatrix)
    resource_quotas: ResourceQuotas = field(default_factory=ResourceQuotas)
    platform_access: PlatformAccessControl = field(default_factory=PlatformAccessControl)
    collaboration: CollaborationPermissions = field(default_factory=CollaborationPermissions)
    security_policies: SecurityPolicies = field(default_factory=SecurityPolicies)
    
    # Role definitions
    roles: Dict[Role, RoleDefinition] = field(default_factory=lambda: {
        Role.GUEST: RoleDefinition(
            name="guest",
            display_name="Guest",
            description="Limited access for non-registered users",
            permissions={Permission.CONTENT_VIEW},
            max_storage_gb=0,
            api_rate_limit="10/hour"
        ),
        Role.CREATOR_FREE: RoleDefinition(
            name="creator_free",
            display_name="Free Creator",
            description="Free tier content creator",
            permissions=set(),  # Populated dynamically
            max_storage_gb=1,
            max_monthly_uploads=10,
            api_rate_limit="100/hour"
        ),
        Role.CREATOR_PRO: RoleDefinition(
            name="creator_pro",
            display_name="Professional Creator",
            description="Professional tier content creator",
            permissions=set(),  # Populated dynamically
            max_storage_gb=100,
            max_monthly_uploads=1000,
            api_rate_limit="2000/hour",
            ai_features_enabled=True,
            premium_features_enabled=True,
            collaboration_features_enabled=True,
            max_platform_connections=10
        ),
        Role.ADMIN: RoleDefinition(
            name="admin",
            display_name="Administrator",
            description="System administrator",
            permissions={Permission.ADMIN_USERS, Permission.ADMIN_SYSTEM},
            max_storage_gb=-1,  # unlimited
            api_rate_limit="10000/hour"
        )
    })
    
    # Global settings
    default_role: Role = Role.GUEST
    auto_assign_creator_role: bool = True
    permission_inheritance_enabled: bool = True
    
    # Audit settings
    log_authorization_events: bool = True
    track_permission_changes: bool = True
    alert_on_privilege_escalation: bool = True


# Default configuration instance
authorization_config = AuthorizationConfig()


def get_authorization_config() -> AuthorizationConfig:
    """Get the authorization configuration instance."""
    return authorization_config


def get_creator_permissions(creator_type: CreatorType, tier: SubscriptionTier) -> Set[Permission]:
    """
Get permissions for a specific creator type and subscription tier."""
    config = get_authorization_config()
    
    # Start with base permissions for creator type
    permissions = config.permission_matrix.free_permissions.get(creator_type, set())
    
    # Add tier-specific permissions
    if tier in [SubscriptionTier.BASIC, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
        permissions.update(config.permission_matrix.professional_permissions)
    
    if tier == SubscriptionTier.ENTERPRISE:
        permissions.update(config.permission_matrix.enterprise_permissions)
    
    return permissions


def get_resource_quotas(tier: SubscriptionTier) -> Dict[str, Any]:
    """
Get resource quotas for a subscription tier."""
    config = get_authorization_config()
    return config.resource_quotas.quotas_by_tier.get(tier, {})


def check_platform_access(tier: SubscriptionTier, platform: str) -> bool:
    """
Check if a subscription tier has access to a specific platform."""
    config = get_authorization_config()
    allowed_platforms = config.platform_access.platform_access.get(tier, [])
    return platform in allowed_platforms


def validate_authorization_config(config: AuthorizationConfig) -> bool:
    """
Validate authorization configuration settings."""
    # Validate that all roles have valid permissions
    for role_def in config.roles.values():
        for permission in role_def.permissions:
            if not isinstance(permission, Permission):
                raise ValueError(f"Invalid permission: {permission}")
    
    # Validate quota configurations
    for tier_quotas in config.resource_quotas.quotas_by_tier.values():
        if "storage_gb" not in tier_quotas:
            raise ValueError("Storage quota must be specified for all tiers")
    
    return True
