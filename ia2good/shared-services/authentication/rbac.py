"""
Role-Based Access Control (RBAC) Manager
Manages permissions and access control across all modules
"""

from typing import Optional, List, Dict, Any
from enum import Enum


class Permission(str, Enum):
    """Standard permissions across all modules"""
    # General permissions
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    
    # IA2GOOD specific
    CASE_CREATE = "ia2good:case:create"
    CASE_ASSIGN = "ia2good:case:assign"
    CASE_CLOSE = "ia2good:case:close"
    VOLUNTEER_MANAGE = "ia2good:volunteer:manage"
    
    # Guardian specific
    ALERT_VIEW = "guardian:alert:view"
    ALERT_MANAGE = "guardian:alert:manage"
    MONITOR_CONFIGURE = "guardian:monitor:configure"
    
    # EduVerify specific
    VERIFICATION_REQUEST = "eduverify:verification:request"
    VERIFICATION_APPROVE = "eduverify:verification:approve"
    INSTITUTION_MANAGE = "eduverify:institution:manage"
    
    # MedCare specific
    CONSULTATION_CREATE = "medcare:consultation:create"
    PRESCRIPTION_MANAGE = "medcare:prescription:manage"
    PATIENT_VIEW = "medcare:patient:view"


class Role(str, Enum):
    """Standard roles across all modules"""
    # System roles
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"
    
    # IA2GOOD roles
    IA2GOOD_VOLUNTEER = "ia2good_volunteer"
    IA2GOOD_COORDINATOR = "ia2good_coordinator"
    IA2GOOD_BENEFICIARY = "ia2good_beneficiary"
    
    # Guardian roles
    GUARDIAN_USER = "guardian_user"
    GUARDIAN_CAREGIVER = "guardian_caregiver"
    GUARDIAN_ADMIN = "guardian_admin"
    
    # EduVerify roles
    EDUVERIFY_STUDENT = "eduverify_student"
    EDUVERIFY_INSTITUTION = "eduverify_institution"
    EDUVERIFY_VERIFIER = "eduverify_verifier"
    
    # MedCare roles
    MEDCARE_PATIENT = "medcare_patient"
    MEDCARE_DOCTOR = "medcare_doctor"
    MEDCARE_ADMIN = "medcare_admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    # Super admin has all permissions
    Role.SUPER_ADMIN: [p for p in Permission],
    
    # Admin has most permissions
    Role.ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
    ],
    
    # Basic user
    Role.USER: [
        Permission.READ,
    ],
    
    # IA2GOOD roles
    Role.IA2GOOD_VOLUNTEER: [
        Permission.READ,
        Permission.CASE_CREATE,
    ],
    Role.IA2GOOD_COORDINATOR: [
        Permission.READ,
        Permission.WRITE,
        Permission.CASE_CREATE,
        Permission.CASE_ASSIGN,
        Permission.CASE_CLOSE,
        Permission.VOLUNTEER_MANAGE,
    ],
    Role.IA2GOOD_BENEFICIARY: [
        Permission.READ,
        Permission.CASE_CREATE,
    ],
    
    # Guardian roles
    Role.GUARDIAN_USER: [
        Permission.READ,
        Permission.ALERT_VIEW,
    ],
    Role.GUARDIAN_CAREGIVER: [
        Permission.READ,
        Permission.WRITE,
        Permission.ALERT_VIEW,
        Permission.ALERT_MANAGE,
    ],
    Role.GUARDIAN_ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.ALERT_VIEW,
        Permission.ALERT_MANAGE,
        Permission.MONITOR_CONFIGURE,
    ],
    
    # EduVerify roles
    Role.EDUVERIFY_STUDENT: [
        Permission.READ,
        Permission.VERIFICATION_REQUEST,
    ],
    Role.EDUVERIFY_INSTITUTION: [
        Permission.READ,
        Permission.VERIFICATION_APPROVE,
    ],
    Role.EDUVERIFY_VERIFIER: [
        Permission.READ,
        Permission.WRITE,
        Permission.VERIFICATION_APPROVE,
        Permission.INSTITUTION_MANAGE,
    ],
    
    # MedCare roles
    Role.MEDCARE_PATIENT: [
        Permission.READ,
        Permission.CONSULTATION_CREATE,
    ],
    Role.MEDCARE_DOCTOR: [
        Permission.READ,
        Permission.WRITE,
        Permission.CONSULTATION_CREATE,
        Permission.PRESCRIPTION_MANAGE,
        Permission.PATIENT_VIEW,
    ],
    Role.MEDCARE_ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.CONSULTATION_CREATE,
        Permission.PRESCRIPTION_MANAGE,
        Permission.PATIENT_VIEW,
    ],
}


class RBACManager:
    """Manage role-based access control"""
    
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS
    
    def has_permission(self, user_roles: List[str], required_permission: Permission) -> bool:
        """
        Check if user has required permission based on their roles
        
        Args:
            user_roles: List of user's role strings
            required_permission: Permission to check
            
        Returns:
            True if user has permission
        """
        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions = self.role_permissions.get(role, [])
                if required_permission in permissions:
                    return True
            except ValueError:
                # Invalid role string
                continue
        
        return False
    
    def has_any_permission(self, user_roles: List[str], required_permissions: List[Permission]) -> bool:
        """
        Check if user has any of the required permissions
        
        Args:
            user_roles: List of user's role strings
            required_permissions: List of permissions to check
            
        Returns:
            True if user has at least one permission
        """
        return any(self.has_permission(user_roles, perm) for perm in required_permissions)
    
    def has_all_permissions(self, user_roles: List[str], required_permissions: List[Permission]) -> bool:
        """
        Check if user has all required permissions
        
        Args:
            user_roles: List of user's role strings
            required_permissions: List of permissions to check
            
        Returns:
            True if user has all permissions
        """
        return all(self.has_permission(user_roles, perm) for perm in required_permissions)
    
    def get_user_permissions(self, user_roles: List[str]) -> List[Permission]:
        """
        Get all permissions for a user based on their roles
        
        Args:
            user_roles: List of user's role strings
            
        Returns:
            List of all permissions
        """
        all_permissions = set()
        
        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions = self.role_permissions.get(role, [])
                all_permissions.update(permissions)
            except ValueError:
                continue
        
        return list(all_permissions)
    
    def can_access_module(self, user_roles: List[str], module: str) -> bool:
        """
        Check if user can access a specific module
        
        Args:
            user_roles: List of user's role strings
            module: Module name (ia2good, guardian, eduverify, medcare)
            
        Returns:
            True if user has any role for that module
        """
        module_prefix = f"{module.lower()}_"
        
        # Super admin and admin can access all modules
        if any(role in [Role.SUPER_ADMIN.value, Role.ADMIN.value] for role in user_roles):
            return True
        
        # Check if user has any role for this module
        return any(role.startswith(module_prefix) for role in user_roles)
