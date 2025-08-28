"""
Authorization Security Tests
Comprehensive tests for access control and authorization
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional
from enum import Enum


class Permission(Enum):
    """System permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER_MANAGEMENT = "user_management"
    CONTENT_MANAGEMENT = "content_management"
    ANALYTICS_VIEW = "analytics_view"


class Role(Enum):
    """System roles"""
    ADMIN = "admin"
    MODERATOR = "moderator" 
    USER = "user"
    VIEWER = "viewer"
    CONTENT_CREATOR = "content_creator"
    ANALYST = "analyst"


class TestRoleBasedAccessControl:
    """Test Role-Based Access Control (RBAC)"""
    
    @pytest.mark.security
    def test_role_permission_mapping(self):
        """Test role to permission mapping"""
        role_permissions = {
            Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, 
                        Permission.ADMIN, Permission.USER_MANAGEMENT, 
                        Permission.CONTENT_MANAGEMENT, Permission.ANALYTICS_VIEW],
            Role.MODERATOR: [Permission.READ, Permission.WRITE, Permission.MODERATOR,
                           Permission.CONTENT_MANAGEMENT],
            Role.CONTENT_CREATOR: [Permission.READ, Permission.WRITE, Permission.CONTENT_MANAGEMENT],
            Role.ANALYST: [Permission.READ, Permission.ANALYTICS_VIEW],
            Role.USER: [Permission.READ],
            Role.VIEWER: [Permission.READ]
        }
        
        # Validate role hierarchies
        assert Permission.ADMIN in role_permissions[Role.ADMIN]
        assert Permission.READ in role_permissions[Role.USER]
        assert Permission.DELETE not in role_permissions[Role.USER]
        assert Permission.USER_MANAGEMENT not in role_permissions[Role.MODERATOR]
    
    @pytest.mark.security
    def test_permission_inheritance(self):
        """Test permission inheritance in role hierarchy"""
        def has_permission(user_role: Role, required_permission: Permission) -> bool:
            role_permissions = {
                Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, 
                           Permission.ADMIN, Permission.USER_MANAGEMENT],
                Role.MODERATOR: [Permission.READ, Permission.WRITE, Permission.MODERATOR],
                Role.USER: [Permission.READ],
                Role.VIEWER: [Permission.READ]
            }
            
            return required_permission in role_permissions.get(user_role, [])
        
        # Test various role permissions
        assert has_permission(Role.ADMIN, Permission.READ) is True
        assert has_permission(Role.ADMIN, Permission.DELETE) is True
        assert has_permission(Role.USER, Permission.READ) is True
        assert has_permission(Role.USER, Permission.DELETE) is False
        assert has_permission(Role.VIEWER, Permission.WRITE) is False
    
    @pytest.mark.security
    def test_dynamic_role_assignment(self):
        """Test dynamic role assignment and revocation"""
        # Mock user role management
        user_roles = {}
        
        def assign_role(user_id: str, role: Role) -> bool:
            if user_id not in user_roles:
                user_roles[user_id] = set()
            user_roles[user_id].add(role)
            return True
        
        def revoke_role(user_id: str, role: Role) -> bool:
            if user_id in user_roles and role in user_roles[user_id]:
                user_roles[user_id].remove(role)
                return True
            return False
        
        def get_user_roles(user_id: str) -> Set[Role]:
            return user_roles.get(user_id, set())
        
        # Test role assignment
        user_id = "user123"
        assert assign_role(user_id, Role.USER) is True
        assert Role.USER in get_user_roles(user_id)
        
        # Test role promotion
        assert assign_role(user_id, Role.MODERATOR) is True
        assert Role.MODERATOR in get_user_roles(user_id)
        
        # Test role revocation
        assert revoke_role(user_id, Role.USER) is True
        assert Role.USER not in get_user_roles(user_id)


class TestAttributeBasedAccessControl:
    """Test Attribute-Based Access Control (ABAC)"""
    
    @pytest.mark.security
    def test_resource_based_access(self):
        """Test access control based on resource attributes"""
        def check_resource_access(user_id: str, resource_id: str, action: str) -> bool:
            # Mock resource ownership
            resource_owners = {
                "content_1": "user123",
                "content_2": "user456",
                "content_3": "user789"
            }
            
            # Mock user attributes
            user_attributes = {
                "user123": {"department": "marketing", "level": "senior"},
                "user456": {"department": "content", "level": "junior"},
                "user789": {"department": "admin", "level": "manager"}
            }
            
            # Access control logic
            if action == "read":
                return True  # Anyone can read
            
            if action in ["edit", "delete"]:
                # Owner can edit/delete
                if resource_owners.get(resource_id) == user_id:
                    return True
                
                # Managers can edit/delete any content
                user_attr = user_attributes.get(user_id, {})
                if user_attr.get("level") == "manager":
                    return True
            
            return False
        
        # Test resource ownership
        assert check_resource_access("user123", "content_1", "edit") is True
        assert check_resource_access("user456", "content_1", "edit") is False
        
        # Test manager override
        assert check_resource_access("user789", "content_1", "delete") is True
        
        # Test read access
        assert check_resource_access("user456", "content_3", "read") is True
    
    @pytest.mark.security
    def test_time_based_access_control(self):
        """Test time-based access restrictions"""
        def check_time_based_access(user_id: str, resource: str) -> bool:
            # Mock time-based restrictions
            business_hours = {
                "start": 9,  # 9 AM
                "end": 17    # 5 PM
            }
            
            restricted_resources = ["sensitive_data", "financial_reports"]
            
            current_hour = datetime.now().hour
            
            # Sensitive resources only during business hours
            if resource in restricted_resources:
                return business_hours["start"] <= current_hour <= business_hours["end"]
            
            return True
        
        # Test with modified data but use timing-independent approach
        with patch('datetime.datetime') as mock_datetime:
            # Test during business hours (14:00)
            mock_datetime.now.return_value.hour = 14
            assert check_time_based_access("user123", "sensitive_data") is True
            
            # Test outside business hours (22:00)
            mock_datetime.now.return_value.hour = 22
            assert check_time_based_access("user123", "sensitive_data") is False
            
            # Test non-restricted resource outside hours
            assert check_time_based_access("user123", "public_content") is True
    
    @pytest.mark.security
    def test_location_based_access_control(self):
        """Test location-based access restrictions"""
        def check_location_access(user_id: str, user_ip: str, resource: str) -> bool:
            # Mock IP whitelist for sensitive resources
            allowed_ip_ranges = [
                "192.168.1.0/24",   # Office network
                "10.0.0.0/8",       # VPN network
                "203.0.113.0/24"    # Approved external network
            ]
            
            restricted_resources = ["admin_panel", "user_data", "financial_data"]
            
            def ip_in_range(ip: str, ip_range: str) -> bool:
                # Simplified IP range check
                if "/" not in ip_range:
                    return ip == ip_range
                
                network, prefix = ip_range.split("/")
                prefix_len = int(prefix)
                
                # Simplified: just check network portion
                ip_parts = ip.split(".")
                network_parts = network.split(".")
                
                if prefix_len >= 24:
                    return ".".join(ip_parts[:3]) == ".".join(network_parts[:3])
                elif prefix_len >= 16:
                    return ".".join(ip_parts[:2]) == ".".join(network_parts[:2])
                elif prefix_len >= 8:
                    return ip_parts[0] == network_parts[0]
                
                return True
            
            # Check if resource requires location restriction
            if resource not in restricted_resources:
                return True
            
            # Check if IP is in allowed ranges
            for ip_range in allowed_ip_ranges:
                if ip_in_range(user_ip, ip_range):
                    return True
            
            return False
        
        # Test allowed IP
        assert check_location_access("user123", "192.168.1.100", "admin_panel") is True
        
        # Test disallowed IP
        assert check_location_access("user123", "203.0.114.100", "admin_panel") is False
        
        # Test unrestricted resource
        assert check_location_access("user123", "203.0.114.100", "public_content") is True


class TestAccessControlEnforcement:
    """Test access control enforcement mechanisms"""
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_api_endpoint_protection(self):
        """Test API endpoint access control"""
        # Mock endpoint permissions
        endpoint_permissions = {
            "/api/admin/users": [Permission.ADMIN, Permission.USER_MANAGEMENT],
            "/api/content/create": [Permission.WRITE, Permission.CONTENT_MANAGEMENT],
            "/api/content/read": [Permission.READ],
            "/api/analytics/report": [Permission.ANALYTICS_VIEW],
            "/api/user/profile": [Permission.READ]  # Own profile
        }
        
        def check_endpoint_access(user_permissions: List[Permission], endpoint: str) -> bool:
            required_permissions = endpoint_permissions.get(endpoint, [])
            
            if not required_permissions:
                return True  # No restrictions
            
            # User needs at least one of the required permissions
            return any(perm in user_permissions for perm in required_permissions)
        
        # Test admin access
        admin_permissions = [Permission.ADMIN, Permission.READ, Permission.WRITE]
        assert check_endpoint_access(admin_permissions, "/api/admin/users") is True
        
        # Test regular user access
        user_permissions = [Permission.READ]
        assert check_endpoint_access(user_permissions, "/api/admin/users") is False
        assert check_endpoint_access(user_permissions, "/api/content/read") is True
    
    @pytest.mark.security
    def test_method_level_authorization(self):
        """Test method-level authorization decorators"""
        # Mock authorization decorator
        def require_permission(required_perm: Permission):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    # Mock: get current user permissions
                    current_user_permissions = kwargs.get('user_permissions', [])
                    
                    if required_perm not in current_user_permissions:
                        raise PermissionError(f"Permission {required_perm.value} required")
                    
                    return func(*args, **kwargs)
                return wrapper
            return decorator
        
        # Mock protected function
        @require_permission(Permission.ADMIN)
        def delete_user(user_id: str, **kwargs):
            return f"User {user_id} deleted"
        
        # Test with admin permissions
        try:
            result = delete_user("user123", user_permissions=[Permission.ADMIN])
            assert "deleted" in result
        except PermissionError:
            pytest.fail("Should have admin access")
        
        # Test without admin permissions
        with pytest.raises(PermissionError):
            delete_user("user123", user_permissions=[Permission.READ])
    
    @pytest.mark.security
    def test_data_filtering_by_permissions(self):
        """Test data filtering based on user permissions"""
        # Mock data with different sensitivity levels
        all_data = [
            {"id": 1, "content": "Public content", "level": "public"},
            {"id": 2, "content": "Internal memo", "level": "internal"},
            {"id": 3, "content": "Confidential report", "level": "confidential"},
            {"id": 4, "content": "Top secret data", "level": "secret"}
        ]
        
        def filter_data_by_clearance(user_clearance: str, data: List[Dict]) -> List[Dict]:
            clearance_levels = {
                "public": ["public"],
                "internal": ["public", "internal"],
                "confidential": ["public", "internal", "confidential"],
                "secret": ["public", "internal", "confidential", "secret"]
            }
            
            allowed_levels = clearance_levels.get(user_clearance, ["public"])
            
            return [item for item in data if item["level"] in allowed_levels]
        
        # Test different clearance levels
        public_data = filter_data_by_clearance("public", all_data)
        assert len(public_data) == 1
        assert public_data[0]["level"] == "public"
        
        internal_data = filter_data_by_clearance("internal", all_data)
        assert len(internal_data) == 2
        
        confidential_data = filter_data_by_clearance("confidential", all_data)
        assert len(confidential_data) == 3
        
        secret_data = filter_data_by_clearance("secret", all_data)
        assert len(secret_data) == 4


class TestPrivilegeEscalation:
    """Test privilege escalation prevention"""
    
    @pytest.mark.security
    def test_vertical_privilege_escalation_prevention(self):
        """Test prevention of vertical privilege escalation"""
        def can_modify_user_role(current_user_role: Role, target_user_role: Role, new_role: Role) -> bool:
            # Role hierarchy (higher number = more privileges)
            role_hierarchy = {
                Role.VIEWER: 1,
                Role.USER: 2,
                Role.CONTENT_CREATOR: 3,
                Role.ANALYST: 3,
                Role.MODERATOR: 4,
                Role.ADMIN: 5
            }
            
            current_level = role_hierarchy.get(current_user_role, 0)
            target_level = role_hierarchy.get(target_user_role, 0)
            new_level = role_hierarchy.get(new_role, 0)
            
            # Users can only modify roles below their level
            # Users cannot promote others to their level or above
            return (current_level > target_level and 
                   new_level < current_level)
        
        # Test admin can demote moderator to user
        assert can_modify_user_role(Role.ADMIN, Role.MODERATOR, Role.USER) is True
        
        # Test moderator cannot promote user to admin
        assert can_modify_user_role(Role.MODERATOR, Role.USER, Role.ADMIN) is False
        
        # Test user cannot modify anyone
        assert can_modify_user_role(Role.USER, Role.VIEWER, Role.USER) is False
    
    @pytest.mark.security
    def test_horizontal_privilege_escalation_prevention(self):
        """Test prevention of horizontal privilege escalation"""
        def can_access_user_data(current_user_id: str, target_user_id: str, 
                                current_user_role: Role) -> bool:
            # Users can access their own data
            if current_user_id == target_user_id:
                return True
            
            # Admins and moderators can access other users' data
            privileged_roles = [Role.ADMIN, Role.MODERATOR]
            return current_user_role in privileged_roles
        
        # Test user accessing own data
        assert can_access_user_data("user123", "user123", Role.USER) is True
        
        # Test user accessing other user's data
        assert can_access_user_data("user123", "user456", Role.USER) is False
        
        # Test admin accessing any user's data
        assert can_access_user_data("admin1", "user456", Role.ADMIN) is True
    
    @pytest.mark.security
    def test_permission_escalation_audit(self):
        """Test auditing of permission escalation attempts"""
        audit_log = []
        
        def audit_permission_change(user_id: str, action: str, target: str, 
                                  success: bool, reason: str = "") -> None:
            audit_log.append({
                "timestamp": datetime.now(),
                "user_id": user_id,
                "action": action,
                "target": target,
                "success": success,
                "reason": reason
            })
        
        # Mock failed escalation attempt
        audit_permission_change("user123", "promote_role", "user456", 
                               False, "Insufficient privileges")
        
        # Mock successful permission grant
        audit_permission_change("admin1", "grant_permission", "user123", 
                               True, "Admin approval")
        
        assert len(audit_log) == 2
        assert audit_log[0]["success"] is False
        assert audit_log[1]["success"] is True
        assert "Insufficient privileges" in audit_log[0]["reason"]


class TestAccessControlTesting:
    """Test access control testing utilities"""
    
    @pytest.mark.security
    def test_permission_matrix_validation(self):
        """Test validation of permission matrix completeness"""
        # Mock permission matrix
        permission_matrix = {
            (Role.ADMIN, "user_management"): True,
            (Role.ADMIN, "content_management"): True,
            (Role.MODERATOR, "content_management"): True,
            (Role.MODERATOR, "user_management"): False,
            (Role.USER, "content_management"): False,
            (Role.USER, "user_management"): False
        }
        
        # Validate matrix completeness
        roles = [Role.ADMIN, Role.MODERATOR, Role.USER]
        resources = ["user_management", "content_management"]
        
        expected_entries = len(roles) * len(resources)
        actual_entries = len(permission_matrix)
        
        assert actual_entries == expected_entries, "Permission matrix should be complete"
        
        # Validate no conflicting permissions
        conflicts = []
        for (role, resource), allowed in permission_matrix.items():
            # Check for logical conflicts (e.g., lower role having permission that higher role doesn't)
            if role == Role.USER and allowed:
                for higher_role in [Role.MODERATOR, Role.ADMIN]:
                    if not permission_matrix.get((higher_role, resource), False):
                        conflicts.append(f"User has {resource} but {higher_role.value} doesn't")
        
        assert len(conflicts) == 0, f"Found permission conflicts: {conflicts}"
    
    @pytest.mark.security
    def test_access_control_boundary_testing(self):
        """Test boundary conditions in access control"""
        def test_boundary_access(user_level: int, required_level: int) -> bool:
            return user_level >= required_level
        
        # Test exact boundary
        assert test_boundary_access(5, 5) is True
        
        # Test just below boundary
        assert test_boundary_access(4, 5) is False
        
        # Test just above boundary
        assert test_boundary_access(6, 5) is True
        
        # Test edge cases
        assert test_boundary_access(0, 0) is True
        assert test_boundary_access(-1, 0) is False