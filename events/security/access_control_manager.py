"""Access Control Manager for Events Security

Advanced RBAC with business context awareness for Ainflue platform.
Manages granular permissions for content, collaboration, and monetization events.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PermissionScope(Enum):
    """Permission scopes for different business areas"""
    CONTENT = "content"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    DISTRIBUTION = "distribution"
    ANALYTICS = "analytics"
    ADMIN = "admin"


@dataclass
class Permission:
    """Represents a specific permission"""
    name: str
    scope: PermissionScope
    description: str
    required_role_level: int = 1  # 1=basic, 2=premium, 3=enterprise, 4=admin
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.name == other.name
        return self.name == other


@dataclass
class BusinessRole:
    """Represents a business role with context"""
    name: str
    permissions: Set[Permission]
    role_level: int
    context: Dict[str, Any] = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class TemporaryGrant:
    """Temporary permission grant"""
    permission: Permission
    granted_until: datetime
    justification: str
    approval_required: bool = False
    approved_by: Optional[str] = None


@dataclass
class AuthorizationResult:
    """Result of authorization check"""
    granted: bool
    granted_permissions: List[Permission]
    denied_permissions: List[Permission]
    business_justification: str
    temporary_grants: List[TemporaryGrant]
    audit_trail_id: Optional[str] = None


@dataclass
class PermissionValidationResult:
    """Result of permission validation"""
    granted: bool
    granted_permissions: List[Permission]
    denied_permissions: List[Permission]
    temporary_grants: List[TemporaryGrant]
    business_justification: str


class AccessControlManager:
    """
    Advanced access control manager for Ainflue business events.
    Provides RBAC with dynamic business context awareness.
    """
    
    def __init__(self):
        self.enabled = True
        self.permissions_registry = self._initialize_permissions_registry()
        self.business_roles = self._initialize_business_roles()
        self.user_roles = {}  # user_id -> List[BusinessRole]
        self.temporary_grants = {}  # user_id -> List[TemporaryGrant]
        self.authorization_history = []
        logger.info("AccessControlManager initialized")
    
    async def authorize_event_access(self, 
                                   event: Any,
                                   requesting_user_id: str,
                                   business_context: Dict[str, Any] = None) -> AuthorizationResult:
        """
        Authorize access to perform an event with business context awareness.
        
        Args:
            event: Domain event to authorize
            requesting_user_id: ID of user requesting access
            business_context: Business context for authorization
            
        Returns:
            AuthorizationResult with authorization decision
        """
        if not self.enabled:
            return self._create_permissive_result(event)
        
        try:
            business_context = business_context or {}
            event_type = getattr(event, 'event_type', 'unknown')
            event_data = getattr(event, 'data', {})
            
            # Resolve user's business roles
            user_roles = await self._resolve_user_business_roles(
                requesting_user_id, business_context
            )
            
            # Get required permissions for event
            required_permissions = await self._get_event_required_permissions(
                event_type, event_data, business_context
            )
            
            # Validate permissions with escalation
            validation_result = await self._validate_permissions_with_escalation(
                requesting_user_id, user_roles, required_permissions, business_context
            )
            
            # Generate business justification
            business_justification = self._generate_business_justification(
                requesting_user_id, user_roles, required_permissions, 
                validation_result, business_context
            )
            
            result = AuthorizationResult(
                granted=validation_result.granted,
                granted_permissions=validation_result.granted_permissions,
                denied_permissions=validation_result.denied_permissions,
                business_justification=business_justification,
                temporary_grants=validation_result.temporary_grants
            )
            
            # Store in authorization history
            self._store_authorization_history(
                requesting_user_id, event_type, result, business_context
            )
            
            logger.debug(f"Authorization result for user {requesting_user_id} on {event_type}: {result.granted}")
            return result
            
        except Exception as e:
            logger.error(f"Error in access authorization: {str(e)}")
            return self._create_error_result(event, str(e))
    
    async def _resolve_user_business_roles(self, 
                                         user_id: str, 
                                         business_context: Dict[str, Any]) -> List[BusinessRole]:
        """Resolve user's business roles with dynamic context"""
        
        # Get base roles
        base_roles = self.user_roles.get(user_id, [])
        
        # Add dynamic roles based on context
        dynamic_roles = await self._evaluate_dynamic_roles(user_id, business_context)
        
        # Add contextual roles
        contextual_roles = await self._evaluate_contextual_roles(user_id, business_context)
        
        # Combine and deduplicate
        all_roles = base_roles + dynamic_roles + contextual_roles
        unique_roles = self._deduplicate_roles(all_roles)
        
        return unique_roles
    
    async def _evaluate_dynamic_roles(self, 
                                    user_id: str, 
                                    business_context: Dict[str, Any]) -> List[BusinessRole]:
        """Evaluate dynamic roles based on user performance and activity"""
        
        dynamic_roles = []
        
        # Creator performance roles (simulated)
        creator_stats = business_context.get('creator_stats', {})
        monthly_revenue = creator_stats.get('monthly_revenue', 0)
        collaboration_success_rate = creator_stats.get('collaboration_success_rate', 0.0)
        content_quality_score = creator_stats.get('content_quality_score', 0.0)
        
        # High earning creator role
        if monthly_revenue > 10000:
            dynamic_roles.append(BusinessRole(
                name="high_earning_creator",
                permissions=self._get_high_earner_permissions(),
                role_level=3,
                context={"monthly_revenue": monthly_revenue}
            ))
        
        # Trusted collaborator role
        if collaboration_success_rate > 0.9:
            dynamic_roles.append(BusinessRole(
                name="trusted_collaborator",
                permissions=self._get_trusted_collaborator_permissions(),
                role_level=2,
                context={"success_rate": collaboration_success_rate}
            ))
        
        # Premium content creator role
        if content_quality_score > 0.95:
            dynamic_roles.append(BusinessRole(
                name="premium_content_creator",
                permissions=self._get_premium_creator_permissions(),
                role_level=2,
                context={"quality_score": content_quality_score}
            ))
        
        return dynamic_roles
    
    async def _evaluate_contextual_roles(self, 
                                       user_id: str, 
                                       business_context: Dict[str, Any]) -> List[BusinessRole]:
        """Evaluate contextual roles based on current situation"""
        
        contextual_roles = []
        
        # Project-specific roles
        if business_context.get("project_type") == "collaboration":
            project_role = business_context.get("user_role_in_project", "participant")
            
            if project_role == "lead":
                contextual_roles.append(BusinessRole(
                    name="project_lead",
                    permissions=self._get_project_lead_permissions(),
                    role_level=3,
                    context={"project_id": business_context.get("project_id")},
                    expires_at=datetime.utcnow() + timedelta(days=30)
                ))
            elif project_role == "specialist":
                contextual_roles.append(BusinessRole(
                    name="project_specialist",
                    permissions=self._get_project_specialist_permissions(),
                    role_level=2,
                    context={"project_id": business_context.get("project_id")},
                    expires_at=datetime.utcnow() + timedelta(days=30)
                ))
        
        # Revenue sharing roles
        if business_context.get("revenue_sharing_active"):
            revenue_percentage = business_context.get("revenue_percentage", 0)
            
            if revenue_percentage > 50:
                contextual_roles.append(BusinessRole(
                    name="primary_revenue_recipient",
                    permissions=self._get_primary_revenue_permissions(),
                    role_level=3,
                    context={"revenue_percentage": revenue_percentage}
                ))
            else:
                contextual_roles.append(BusinessRole(
                    name="secondary_revenue_recipient",
                    permissions=self._get_secondary_revenue_permissions(),
                    role_level=1,
                    context={"revenue_percentage": revenue_percentage}
                ))
        
        # Geographic compliance roles
        user_region = business_context.get("user_region", "US")
        if user_region in ["EU", "UK"]:
            contextual_roles.append(BusinessRole(
                name="gdpr_region_user",
                permissions=self._get_gdpr_permissions(),
                role_level=1,
                context={"region": user_region}
            ))
        
        return contextual_roles
    
    async def _get_event_required_permissions(self, 
                                            event_type: str, 
                                            event_data: Dict[str, Any],
                                            business_context: Dict[str, Any]) -> List[Permission]:
        """Get required permissions for an event based on type and context"""
        
        permissions = []
        
        # Content events permissions
        if event_type.startswith("content."):
            permissions.extend(self._get_content_permissions(event_type, event_data, business_context))
        
        # Collaboration events permissions
        elif event_type.startswith("collaboration."):
            permissions.extend(self._get_collaboration_permissions(event_type, event_data, business_context))
        
        # Monetization events permissions
        elif event_type.startswith("monetization."):
            permissions.extend(self._get_monetization_permissions(event_type, event_data, business_context))
        
        # Distribution events permissions
        elif event_type.startswith("distribution."):
            permissions.extend(self._get_distribution_permissions(event_type, event_data, business_context))
        
        # User events permissions
        elif event_type.startswith("user."):
            permissions.extend(self._get_user_permissions(event_type, event_data, business_context))
        
        return permissions
    
    def _get_content_permissions(self, 
                               event_type: str, 
                               event_data: Dict[str, Any],
                               business_context: Dict[str, Any]) -> List[Permission]:
        """Get permissions required for content events"""
        
        permissions = []
        
        if "upload" in event_type:
            permissions.append(Permission("content.upload.create", PermissionScope.CONTENT, "Create content uploads"))
            
            # Premium content permissions
            content_type = business_context.get("content_type", "standard")
            if content_type == "premium":
                permissions.append(Permission("content.upload.premium", PermissionScope.CONTENT, "Upload premium content"))
            
            # Large file permissions
            file_size = event_data.get("file_size", 0)
            if file_size > 100_000_000:  # 100MB
                permissions.append(Permission("content.upload.large_files", PermissionScope.CONTENT, "Upload large files"))
        
        elif "processing" in event_type:
            permissions.append(Permission("content.processing.trigger", PermissionScope.CONTENT, "Trigger content processing"))
            
            processing_type = business_context.get("processing_type", "basic")
            if processing_type == "advanced":
                permissions.append(Permission("ai.processing.advanced", PermissionScope.CONTENT, "Advanced AI processing"))
        
        elif "edit" in event_type:
            permissions.append(Permission("content.edit", PermissionScope.CONTENT, "Edit content"))
            
            # Own content vs others' content
            owner_id = event_data.get("content_owner_id")
            user_id = business_context.get("requesting_user_id")
            if owner_id != user_id:
                permissions.append(Permission("content.edit.others", PermissionScope.CONTENT, "Edit others' content"))
        
        return permissions
    
    def _get_collaboration_permissions(self, 
                                     event_type: str, 
                                     event_data: Dict[str, Any],
                                     business_context: Dict[str, Any]) -> List[Permission]:
        """Get permissions required for collaboration events"""
        
        permissions = []
        
        permissions.append(Permission("collaboration.participate", PermissionScope.COLLABORATION, "Participate in collaborations"))
        
        if "initiate" in event_type:
            permissions.append(Permission("collaboration.initiate", PermissionScope.COLLABORATION, "Initiate collaborations"))
        
        if "manage" in event_type:
            permissions.append(Permission("collaboration.manage", PermissionScope.COLLABORATION, "Manage collaborations"))
        
        # Premium collaboration features
        collaboration_type = business_context.get("collaboration_type", "standard")
        if collaboration_type == "premium":
            permissions.append(Permission("collaboration.premium_features", PermissionScope.COLLABORATION, "Premium collaboration features"))
        
        # Revenue sharing permissions
        if "revenue" in event_type:
            permissions.extend([
                Permission("monetization.revenue_sharing", PermissionScope.MONETIZATION, "Revenue sharing"),
                Permission("financial.collaboration_agreements", PermissionScope.MONETIZATION, "Financial collaboration agreements")
            ])
        
        return permissions
    
    def _get_monetization_permissions(self, 
                                    event_type: str, 
                                    event_data: Dict[str, Any],
                                    business_context: Dict[str, Any]) -> List[Permission]:
        """Get permissions required for monetization events"""
        
        permissions = []
        
        permissions.extend([
            Permission("monetization.access", PermissionScope.MONETIZATION, "Access monetization features"),
            Permission("financial.transactions", PermissionScope.MONETIZATION, "Financial transactions")
        ])
        
        # High-value transaction permissions
        transaction_amount = event_data.get("amount", 0)
        if transaction_amount > 10000:  # $10,000+
            permissions.append(Permission("financial.high_value_transactions", PermissionScope.MONETIZATION, "High-value transactions"))
        
        # International transactions
        if business_context.get("cross_border", False):
            permissions.append(Permission("financial.international_transactions", PermissionScope.MONETIZATION, "International transactions"))
        
        # Withdrawal permissions
        if "withdrawal" in event_type:
            permissions.append(Permission("financial.withdrawals", PermissionScope.MONETIZATION, "Financial withdrawals"))
        
        return permissions
    
    def _get_distribution_permissions(self, 
                                    event_type: str, 
                                    event_data: Dict[str, Any],
                                    business_context: Dict[str, Any]) -> List[Permission]:
        """Get permissions required for distribution events"""
        
        permissions = []
        
        permissions.append(Permission("distribution.trigger", PermissionScope.DISTRIBUTION, "Trigger content distribution"))
        
        # Multi-platform distribution
        target_platforms = business_context.get("target_platforms", [])
        if len(target_platforms) > 1:
            permissions.append(Permission("distribution.multi_platform", PermissionScope.DISTRIBUTION, "Multi-platform distribution"))
        
        # Premium platform access
        premium_platforms = ["youtube_premium", "spotify_premium", "netflix"]
        if any(p in premium_platforms for p in target_platforms):
            permissions.append(Permission("distribution.premium_platforms", PermissionScope.DISTRIBUTION, "Premium platform distribution"))
        
        return permissions
    
    def _get_user_permissions(self, 
                            event_type: str, 
                            event_data: Dict[str, Any],
                            business_context: Dict[str, Any]) -> List[Permission]:
        """Get permissions required for user events"""
        
        permissions = []
        
        if "profile" in event_type:
            permissions.append(Permission("user.profile.edit", PermissionScope.ADMIN, "Edit user profile"))
            
            # Edit others' profiles
            target_user_id = event_data.get("target_user_id")
            requesting_user_id = business_context.get("requesting_user_id")
            if target_user_id != requesting_user_id:
                permissions.append(Permission("user.profile.edit.others", PermissionScope.ADMIN, "Edit others' profiles"))
        
        if "settings" in event_type:
            permissions.append(Permission("user.settings.modify", PermissionScope.ADMIN, "Modify user settings"))
        
        return permissions
    
    async def _validate_permissions_with_escalation(self,
                                                  user_id: str,
                                                  user_roles: List[BusinessRole],
                                                  required_permissions: List[Permission],
                                                  business_context: Dict[str, Any]) -> PermissionValidationResult:
        """Validate permissions with intelligent temporary escalation"""
        
        # Get all permissions from roles
        user_permissions = set()
        for role in user_roles:
            user_permissions.update(role.permissions)
        
        # Get temporary grants
        temp_grants = self.temporary_grants.get(user_id, [])
        valid_temp_grants = [g for g in temp_grants if g.granted_until > datetime.utcnow()]
        temp_permissions = {g.permission for g in valid_temp_grants}
        
        # All available permissions
        all_user_permissions = user_permissions | temp_permissions
        
        granted_permissions = []
        denied_permissions = []
        new_temporary_grants = []
        
        for permission in required_permissions:
            if permission in all_user_permissions:
                granted_permissions.append(permission)
            else:
                # Evaluate temporary grant eligibility
                temp_grant = await self._evaluate_temporary_grant(
                    user_id, permission, user_roles, business_context
                )
                
                if temp_grant:
                    new_temporary_grants.append(temp_grant)
                    granted_permissions.append(permission)
                else:
                    denied_permissions.append(permission)
        
        # Apply temporary grants
        if new_temporary_grants:
            if user_id not in self.temporary_grants:
                self.temporary_grants[user_id] = []
            self.temporary_grants[user_id].extend(new_temporary_grants)
        
        # All granted
        all_granted = len(denied_permissions) == 0
        
        business_justification = self._generate_permission_justification(
            user_id, user_roles, required_permissions, granted_permissions, 
            denied_permissions, new_temporary_grants, business_context
        )
        
        return PermissionValidationResult(
            granted=all_granted,
            granted_permissions=granted_permissions,
            denied_permissions=denied_permissions,
            temporary_grants=new_temporary_grants,
            business_justification=business_justification
        )
    
    async def _evaluate_temporary_grant(self,
                                      user_id: str,
                                      permission: Permission,
                                      user_roles: List[BusinessRole],
                                      business_context: Dict[str, Any]) -> Optional[TemporaryGrant]:
        """Evaluate if a temporary permission grant should be allowed"""
        
        # Get user's maximum role level
        max_role_level = max([role.role_level for role in user_roles]) if user_roles else 0
        
        # Simple escalation rules
        
        # Allow one level up for trusted users
        if max_role_level >= 2 and permission.required_role_level <= max_role_level + 1:
            return TemporaryGrant(
                permission=permission,
                granted_until=datetime.utcnow() + timedelta(hours=1),
                justification=f"Temporary escalation for trusted user (level {max_role_level})",
                approval_required=False
            )
        
        # Allow emergency access for content creators
        if (permission.scope == PermissionScope.CONTENT and 
            any(role.name == "content_creator" for role in user_roles)):
            return TemporaryGrant(
                permission=permission,
                granted_until=datetime.utcnow() + timedelta(minutes=30),
                justification="Emergency content access for creator",
                approval_required=True
            )
        
        # Allow project-specific access
        if business_context.get("project_type") == "collaboration":
            project_role = business_context.get("user_role_in_project")
            if project_role in ["lead", "specialist"]:
                return TemporaryGrant(
                    permission=permission,
                    granted_until=datetime.utcnow() + timedelta(hours=24),
                    justification=f"Project-specific access as {project_role}",
                    approval_required=False
                )
        
        return None
    
    def _generate_business_justification(self,
                                       user_id: str,
                                       user_roles: List[BusinessRole],
                                       required_permissions: List[Permission],
                                       validation_result: PermissionValidationResult,
                                       business_context: Dict[str, Any]) -> str:
        """Generate business justification for authorization decision"""
        
        role_names = [role.name for role in user_roles]
        
        if validation_result.granted:
            justification = f"Access granted to user {user_id} with roles: {', '.join(role_names)}. "
            
            if validation_result.temporary_grants:
                temp_count = len(validation_result.temporary_grants)
                justification += f"Includes {temp_count} temporary permission grants. "
            
            justification += f"Business context: {business_context.get('action_purpose', 'Standard operation')}"
            
        else:
            denied_perms = [p.name for p in validation_result.denied_permissions]
            justification = f"Access denied to user {user_id}. Missing permissions: {', '.join(denied_perms)}. "
            justification += f"Current roles: {', '.join(role_names)}. "
            justification += "Consider role upgrade or manual approval for access."
        
        return justification
    
    def _generate_permission_justification(self,
                                         user_id: str,
                                         user_roles: List[BusinessRole],
                                         required_permissions: List[Permission],
                                         granted_permissions: List[Permission],
                                         denied_permissions: List[Permission],
                                         temporary_grants: List[TemporaryGrant],
                                         business_context: Dict[str, Any]) -> str:
        """Generate detailed permission validation justification"""
        
        justification_parts = []
        
        # User context
        role_names = [role.name for role in user_roles]
        justification_parts.append(f"User {user_id} with roles: {', '.join(role_names)}")
        
        # Permission summary
        total_required = len(required_permissions)
        total_granted = len(granted_permissions)
        justification_parts.append(f"Permissions: {total_granted}/{total_required} granted")
        
        # Temporary grants
        if temporary_grants:
            temp_descriptions = [f"{g.permission.name} ({g.justification})" for g in temporary_grants]
            justification_parts.append(f"Temporary grants: {'; '.join(temp_descriptions)}")
        
        # Denied permissions
        if denied_permissions:
            denied_names = [p.name for p in denied_permissions]
            justification_parts.append(f"Denied: {', '.join(denied_names)}")
        
        return ". ".join(justification_parts)
    
    def _deduplicate_roles(self, roles: List[BusinessRole]) -> List[BusinessRole]:
        """Remove duplicate roles, keeping the highest level"""
        
        role_map = {}
        
        for role in roles:
            existing = role_map.get(role.name)
            if not existing or role.role_level > existing.role_level:
                role_map[role.name] = role
        
        return list(role_map.values())
    
    def _initialize_permissions_registry(self) -> Dict[str, Permission]:
        """Initialize the permissions registry"""
        
        permissions = [
            # Content permissions
            Permission("content.upload.create", PermissionScope.CONTENT, "Create content uploads", 1),
            Permission("content.upload.premium", PermissionScope.CONTENT, "Upload premium content", 2),
            Permission("content.upload.large_files", PermissionScope.CONTENT, "Upload large files", 2),
            Permission("content.processing.trigger", PermissionScope.CONTENT, "Trigger content processing", 1),
            Permission("content.edit", PermissionScope.CONTENT, "Edit content", 1),
            Permission("content.edit.others", PermissionScope.CONTENT, "Edit others' content", 3),
            Permission("ai.processing.advanced", PermissionScope.CONTENT, "Advanced AI processing", 3),
            
            # Collaboration permissions
            Permission("collaboration.participate", PermissionScope.COLLABORATION, "Participate in collaborations", 1),
            Permission("collaboration.initiate", PermissionScope.COLLABORATION, "Initiate collaborations", 2),
            Permission("collaboration.manage", PermissionScope.COLLABORATION, "Manage collaborations", 3),
            Permission("collaboration.premium_features", PermissionScope.COLLABORATION, "Premium collaboration features", 2),
            
            # Monetization permissions
            Permission("monetization.access", PermissionScope.MONETIZATION, "Access monetization features", 1),
            Permission("monetization.revenue_sharing", PermissionScope.MONETIZATION, "Revenue sharing", 2),
            Permission("financial.transactions", PermissionScope.MONETIZATION, "Financial transactions", 1),
            Permission("financial.high_value_transactions", PermissionScope.MONETIZATION, "High-value transactions", 3),
            Permission("financial.international_transactions", PermissionScope.MONETIZATION, "International transactions", 2),
            Permission("financial.withdrawals", PermissionScope.MONETIZATION, "Financial withdrawals", 2),
            Permission("financial.collaboration_agreements", PermissionScope.MONETIZATION, "Financial collaboration agreements", 3),
            
            # Distribution permissions
            Permission("distribution.trigger", PermissionScope.DISTRIBUTION, "Trigger content distribution", 1),
            Permission("distribution.multi_platform", PermissionScope.DISTRIBUTION, "Multi-platform distribution", 2),
            Permission("distribution.premium_platforms", PermissionScope.DISTRIBUTION, "Premium platform distribution", 3),
            
            # User permissions
            Permission("user.profile.edit", PermissionScope.ADMIN, "Edit user profile", 1),
            Permission("user.profile.edit.others", PermissionScope.ADMIN, "Edit others' profiles", 4),
            Permission("user.settings.modify", PermissionScope.ADMIN, "Modify user settings", 1),
        ]
        
        return {p.name: p for p in permissions}
    
    def _initialize_business_roles(self) -> Dict[str, BusinessRole]:
        """Initialize business roles"""
        
        roles = {
            "basic_user": BusinessRole(
                name="basic_user",
                permissions={
                    self.permissions_registry["content.upload.create"],
                    self.permissions_registry["content.processing.trigger"],
                    self.permissions_registry["collaboration.participate"],
                    self.permissions_registry["user.profile.edit"],
                    self.permissions_registry["user.settings.modify"]
                },
                role_level=1
            ),
            "content_creator": BusinessRole(
                name="content_creator",
                permissions={
                    self.permissions_registry["content.upload.create"],
                    self.permissions_registry["content.upload.large_files"],
                    self.permissions_registry["content.processing.trigger"],
                    self.permissions_registry["content.edit"],
                    self.permissions_registry["collaboration.participate"],
                    self.permissions_registry["collaboration.initiate"],
                    self.permissions_registry["monetization.access"],
                    self.permissions_registry["financial.transactions"],
                    self.permissions_registry["distribution.trigger"]
                },
                role_level=2
            ),
            "premium_creator": BusinessRole(
                name="premium_creator",
                permissions={
                    self.permissions_registry["content.upload.premium"],
                    self.permissions_registry["ai.processing.advanced"],
                    self.permissions_registry["collaboration.premium_features"],
                    self.permissions_registry["monetization.revenue_sharing"],
                    self.permissions_registry["financial.international_transactions"],
                    self.permissions_registry["financial.withdrawals"],
                    self.permissions_registry["distribution.multi_platform"]
                },
                role_level=3
            )
        }
        
        return roles
    
    def _get_high_earner_permissions(self) -> Set[Permission]:
        """Get permissions for high earning creators"""
        return {
            self.permissions_registry["financial.high_value_transactions"],
            self.permissions_registry["distribution.premium_platforms"],
            self.permissions_registry["ai.processing.advanced"]
        }
    
    def _get_trusted_collaborator_permissions(self) -> Set[Permission]:
        """Get permissions for trusted collaborators"""
        return {
            self.permissions_registry["collaboration.manage"],
            self.permissions_registry["financial.collaboration_agreements"]
        }
    
    def _get_premium_creator_permissions(self) -> Set[Permission]:
        """Get permissions for premium content creators"""
        return {
            self.permissions_registry["content.upload.premium"],
            self.permissions_registry["collaboration.premium_features"]
        }
    
    def _get_project_lead_permissions(self) -> Set[Permission]:
        """Get permissions for project leads"""
        return {
            self.permissions_registry["collaboration.manage"],
            self.permissions_registry["content.edit.others"]
        }
    
    def _get_project_specialist_permissions(self) -> Set[Permission]:
        """Get permissions for project specialists"""
        return {
            self.permissions_registry["collaboration.premium_features"]
        }
    
    def _get_primary_revenue_permissions(self) -> Set[Permission]:
        """Get permissions for primary revenue recipients"""
        return {
            self.permissions_registry["financial.high_value_transactions"],
            self.permissions_registry["financial.collaboration_agreements"]
        }
    
    def _get_secondary_revenue_permissions(self) -> Set[Permission]:
        """Get permissions for secondary revenue recipients"""
        return {
            self.permissions_registry["monetization.revenue_sharing"]
        }
    
    def _get_gdpr_permissions(self) -> Set[Permission]:
        """Get permissions for GDPR region users"""
        return {
            self.permissions_registry["user.profile.edit"],
            self.permissions_registry["user.settings.modify"]
        }
    
    def _create_permissive_result(self, event: Any) -> AuthorizationResult:
        """Create permissive result when access control is disabled"""
        
        return AuthorizationResult(
            granted=True,
            granted_permissions=[],
            denied_permissions=[],
            business_justification="Access control disabled - all access granted",
            temporary_grants=[]
        )
    
    def _create_error_result(self, event: Any, error_message: str) -> AuthorizationResult:
        """Create error result when authorization fails"""
        
        return AuthorizationResult(
            granted=False,
            granted_permissions=[],
            denied_permissions=[],
            business_justification=f"Authorization error: {error_message}",
            temporary_grants=[]
        )
    
    def _store_authorization_history(self,
                                   user_id: str,
                                   event_type: str,
                                   result: AuthorizationResult,
                                   business_context: Dict[str, Any]):
        """Store authorization history for audit and analysis"""
        
        self.authorization_history.append({
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'event_type': event_type,
            'granted': result.granted,
            'permissions_count': len(result.granted_permissions),
            'denied_count': len(result.denied_permissions),
            'temporary_grants_count': len(result.temporary_grants),
            'business_context': business_context
        })
        
        # Maintain history size
        if len(self.authorization_history) > 10000:
            self.authorization_history = self.authorization_history[-10000:]
    
    def add_user_role(self, user_id: str, role_name: str):
        """Add a role to a user"""
        
        if role_name in self.business_roles:
            if user_id not in self.user_roles:
                self.user_roles[user_id] = []
            
            role = self.business_roles[role_name]
            self.user_roles[user_id].append(role)
            logger.info(f"Added role {role_name} to user {user_id}")
        else:
            logger.warning(f"Unknown role: {role_name}")
    
    def remove_user_role(self, user_id: str, role_name: str):
        """Remove a role from a user"""
        
        if user_id in self.user_roles:
            self.user_roles[user_id] = [
                role for role in self.user_roles[user_id] 
                if role.name != role_name
            ]
            logger.info(f"Removed role {role_name} from user {user_id}")
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        
        permissions = set()
        user_roles = self.user_roles.get(user_id, [])
        
        for role in user_roles:
            permissions.update(role.permissions)
        
        # Add temporary grants
        temp_grants = self.temporary_grants.get(user_id, [])
        valid_temp_grants = [g for g in temp_grants if g.granted_until > datetime.utcnow()]
        for grant in valid_temp_grants:
            permissions.add(grant.permission)
        
        return permissions
    
    def enable_access_control(self):
        """Enable access control"""
        self.enabled = True
        logger.info("Access control enabled")
    
    def disable_access_control(self):
        """Disable access control"""
        self.enabled = False
        logger.info("Access control disabled")


# Export for module use
__all__ = ['AccessControlManager', 'Permission', 'BusinessRole', 'AuthorizationResult', 'PermissionScope']