"""
Database Privilege Manager

Enterprise-grade database privilege management system with role-based access control,
dynamic privilege assignment, and comprehensive access monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced privilege management architecture
- ML Engineer: AI-driven access pattern analysis
- DBA: Database privilege optimization
- Security Expert: Enterprise privilege protocols
- Microservices: Distributed privilege management
- Audio Engineer: Audio data access privileges
- DevOps: Secure privilege infrastructure
- IA Prompt Engineer: AI privilege analysis prompts

Contact: mlaiel@live.de
 LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class PrivilegeType(Enum):
    """Database privilege types"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    INDEX = "INDEX"
    REFERENCES = "REFERENCES"
    TRIGGER = "TRIGGER"
    EXECUTE = "EXECUTE"
    USAGE = "USAGE"
    CONNECT = "CONNECT"
    TEMPORARY = "TEMPORARY"
    ALL = "ALL"


class ResourceType(Enum):
    """Database resource types"""
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    VIEW = "view"
    SEQUENCE = "sequence"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    TYPE = "type"
    DOMAIN = "domain"


class GrantOption(Enum):
    """Grant option types"""
    NONE = "none"
    GRANT_OPTION = "grant_option"
    ADMIN_OPTION = "admin_option"


class PrivilegeScope(Enum):
    """Privilege scope levels"""
    GLOBAL = "global"
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    ROW = "row"


@dataclass
class DatabaseResource:
    """Database resource definition"""
    resource_id: str
    resource_type: ResourceType
    name: str
    schema_name: Optional[str] = None
    database_name: Optional[str] = None
    parent_resource: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrivilegeGrant:
    """Database privilege grant"""
    grant_id: str
    principal_id: str
    principal_type: str  # user, role, group
    resource_id: str
    privilege_type: PrivilegeType
    grant_option: GrantOption = GrantOption.NONE
    granted_by: str = ""
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """Database role definition"""
    role_id: str
    name: str
    description: str
    parent_roles: List[str] = field(default_factory=list)
    child_roles: List[str] = field(default_factory=list)
    is_system_role: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """Database user definition"""
    user_id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    direct_privileges: List[str] = field(default_factory=list)
    is_active: bool = True
    is_system_user: bool = False
    last_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """Privilege access request"""
    request_id: str
    requester_id: str
    user_id: str
    resource_id: str
    privilege_type: PrivilegeType
    justification: str
    requested_at: datetime = field(default_factory=datetime.now)
    requested_duration: Optional[int] = None  # hours
    status: str = "pending"  # pending, approved, denied, expired
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrivilegeAudit:
    """Privilege audit record"""
    audit_id: str
    action: str  # grant, revoke, modify, access
    principal_id: str
    resource_id: str
    privilege_type: Optional[PrivilegeType] = None
    performed_by: str = ""
    performed_at: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class PrivilegeEngine(ABC):
    """Abstract privilege engine interface"""
    
    @abstractmethod
    async def grant_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType,
        grant_option: GrantOption = GrantOption.NONE
    ) -> bool:
        """Grant privilege to principal"""
        pass
    
    @abstractmethod
    async def revoke_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> bool:
        """Revoke privilege from principal"""
        pass
    
    @abstractmethod
    async def check_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> bool:
        """Check if principal has privilege on resource"""
        pass


class PostgreSQLPrivilegeEngine(PrivilegeEngine):
    """PostgreSQL-specific privilege engine"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        # In production, this would initialize database connection
    
    async def grant_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType,
        grant_option: GrantOption = GrantOption.NONE
    ) -> bool:
        """Grant PostgreSQL privilege"""



        try:
            # Construct GRANT statement
            grant_sql = self._build_grant_statement(
                principal_id, resource_id, privilege_type, grant_option
            )
            
            # In production, execute SQL statement
            logger.info(f"Would execute: {grant_sql}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant privilege: {e}")
            return False
    
    async def revoke_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> bool:
        """Revoke PostgreSQL privilege"""



        try:
            # Construct REVOKE statement
            revoke_sql = self._build_revoke_statement(
                principal_id, resource_id, privilege_type
            )
            
            # In production, execute SQL statement
            logger.info(f"Would execute: {revoke_sql}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke privilege: {e}")
            return False
    
    async def check_privilege(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> bool:
        """Check PostgreSQL privilege"""



        try:
            # Query privilege information
            check_sql = self._build_privilege_check(
                principal_id, resource_id, privilege_type
            )
            
            # In production, execute query and return result
            logger.info(f"Would execute: {check_sql}")
            
            return True  # Simulated result
            
        except Exception as e:
            logger.error(f"Failed to check privilege: {e}")
            return False
    
    def _build_grant_statement(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType,
        grant_option: GrantOption
    ) -> str:
        """Build PostgreSQL GRANT statement"""
        privilege = privilege_type.value
        resource = resource_id  # Simplified
        
        sql = f"GRANT {privilege} ON {resource} TO {principal_id}"
        
        if grant_option == GrantOption.GRANT_OPTION:
            sql += " WITH GRANT OPTION"
        
        return sql
    
    def _build_revoke_statement(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> str:
        """Build PostgreSQL REVOKE statement"""
        privilege = privilege_type.value
        resource = resource_id  # Simplified
        
        return f"REVOKE {privilege} ON {resource} FROM {principal_id}"
    
    def _build_privilege_check(
        self, 
        principal_id: str, 
        resource_id: str, 
        privilege_type: PrivilegeType
    ) -> str:
        """Build PostgreSQL privilege check query"""
        # Simplified query - in production would check information_schema
        return f"""
        SELECT has_table_privilege('{principal_id}', '{resource_id}', '{privilege_type.value}')
        """


class PrivilegeManager:
    """
    Enterprise-grade database privilege manager
    
    Provides comprehensive privilege management capabilities including:
    - Role-based access control (RBAC)
    - Dynamic privilege assignment
    - Privilege inheritance and delegation
    - Access request workflows
    - Comprehensive audit logging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize privilege manager"""
        self.config = config or {}
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, DatabaseResource] = {}
        self.privilege_grants: Dict[str, PrivilegeGrant] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.audit_records: List[PrivilegeAudit] = []
        
        # Privilege engines by database type
        self.privilege_engines: Dict[str, PrivilegeEngine] = {}
        
        # Configuration
        self.auto_approve_low_risk = self.config.get("auto_approve_low_risk", False)
        self.max_privilege_duration = self.config.get("max_privilege_duration", 24 * 7)  # hours
        self.require_justification = self.config.get("require_justification", True)
        self.enable_privilege_escalation_detection = self.config.get("escalation_detection", True)
        
        # Initialize default roles and resources
        self._initialize_system_roles()
        
        logger.info("Database privilege manager initialized successfully")
    
    def _initialize_system_roles(self):
        """Initialize system roles"""



        try:
            # Create default system roles
            system_roles = [
                Role(
                    role_id="db_admin",
                    name="Database Administrator",
                    description="Full database administration privileges",
                    is_system_role=True
                ),
                Role(
                    role_id="data_reader",
                    name="Data Reader",
                    description="Read-only access to data tables",
                    is_system_role=True
                ),
                Role(
                    role_id="data_writer",
                    name="Data Writer",
                    description="Read and write access to data tables",
                    is_system_role=True,
                    parent_roles=["data_reader"]
                ),
                Role(
                    role_id="schema_owner",
                    name="Schema Owner",
                    description="Full control over specific schema",
                    is_system_role=True,
                    parent_roles=["data_writer"]
                ),
                Role(
                    role_id="backup_operator",
                    name="Backup Operator",
                    description="Database backup and restore privileges",
                    is_system_role=True
                )
            ]
            
            for role in system_roles:
                self.roles[role.role_id] = role
            
            logger.info(f"Initialized {len(system_roles)} system roles")
            
        except Exception as e:
            logger.error(f"Failed to initialize system roles: {e}")
            raise
    
    async def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        initial_roles: Optional[List[str]] = None
    ) -> str:
        """
        Create new database user
        
        Args:
            username: Username
            email: Email address
            full_name: Full name
            initial_roles: Initial roles to assign
            
        Returns:
            User ID
        """



        try:
            # Check if username already exists
            if any(user.username == username for user in self.users.values()):
                raise ValueError(f"Username already exists: {username}")
            
            # Create user
            user = User(
                user_id=str(uuid.uuid4()),
                username=username,
                email=email,
                full_name=full_name,
                roles=initial_roles or []
            )
            
            # Store user
            self.users[user.user_id] = user
            
            # Audit user creation
            await self._audit_action(
                action="create_user",
                principal_id=user.user_id,
                resource_id="system",
                details={"username": username, "roles": initial_roles}
            )
            
            logger.info(f"Created user: {username} ({user.user_id})")
            return user.user_id
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def create_role(
        self,
        name: str,
        description: str,
        parent_roles: Optional[List[str]] = None,
        created_by: str = ""
    ) -> str:
        """
        Create new database role
        
        Args:
            name: Role name
            description: Role description
            parent_roles: Parent roles for inheritance
            created_by: Creator user ID
            
        Returns:
            Role ID
        """



        try:
            # Check if role name already exists
            if any(role.name == name for role in self.roles.values()):
                raise ValueError(f"Role name already exists: {name}")
            
            # Validate parent roles exist
            if parent_roles:
                for parent_role_id in parent_roles:
                    if parent_role_id not in self.roles:
                        raise ValueError(f"Parent role not found: {parent_role_id}")
            
            # Create role
            role = Role(
                role_id=str(uuid.uuid4()),
                name=name,
                description=description,
                parent_roles=parent_roles or [],
                created_by=created_by
            )
            
            # Store role
            self.roles[role.role_id] = role
            
            # Update child roles in parent roles
            if parent_roles:
                for parent_role_id in parent_roles:
                    parent_role = self.roles[parent_role_id]
                    if role.role_id not in parent_role.child_roles:
                        parent_role.child_roles.append(role.role_id)
            
            # Audit role creation
            await self._audit_action(
                action="create_role",
                principal_id=role.role_id,
                resource_id="system",
                details={"name": name, "parent_roles": parent_roles}
            )
            
            logger.info(f"Created role: {name} ({role.role_id})")
            return role.role_id
            
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            raise
    
    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str = ""
    ) -> bool:
        """
        Assign role to user
        
        Args:
            user_id: User ID
            role_id: Role ID
            assigned_by: Assigner user ID
            
        Returns:
            True if successful, False otherwise
        """



        try:
            # Validate user and role exist
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            if role_id not in self.roles:
                raise ValueError(f"Role not found: {role_id}")
            
            user = self.users[user_id]
            role = self.roles[role_id]
            
            # Check if user already has role
            if role_id in user.roles:
                logger.warning(f"User {user.username} already has role {role.name}")
                return True
            
            # Assign role
            user.roles.append(role_id)
            
            # Audit role assignment
            await self._audit_action(
                action="assign_role",
                principal_id=user_id,
                resource_id=role_id,
                performed_by=assigned_by,
                details={"user": user.username, "role": role.name}
            )
            
            logger.info(f"Assigned role {role.name} to user {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            await self._audit_action(
                action="assign_role",
                principal_id=user_id,
                resource_id=role_id,
                performed_by=assigned_by,
                success=False,
                error_message=str(e)
            )
            return False
    
    async def revoke_role_from_user(
        self,
        user_id: str,
        role_id: str,
        revoked_by: str = ""
    ) -> bool:
        """
        Revoke role from user
        
        Args:
            user_id: User ID
            role_id: Role ID
            revoked_by: Revoker user ID
            
        Returns:
            True if successful, False otherwise
        """



        try:
            # Validate user and role exist
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            if role_id not in self.roles:
                raise ValueError(f"Role not found: {role_id}")
            
            user = self.users[user_id]
            role = self.roles[role_id]
            
            # Check if user has role
            if role_id not in user.roles:
                logger.warning(f"User {user.username} does not have role {role.name}")
                return True
            
            # Revoke role
            user.roles.remove(role_id)
            
            # Audit role revocation
            await self._audit_action(
                action="revoke_role",
                principal_id=user_id,
                resource_id=role_id,
                performed_by=revoked_by,
                details={"user": user.username, "role": role.name}
            )
            
            logger.info(f"Revoked role {role.name} from user {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke role: {e}")
            await self._audit_action(
                action="revoke_role",
                principal_id=user_id,
                resource_id=role_id,
                performed_by=revoked_by,
                success=False,
                error_message=str(e)
            )
            return False
    
    async def grant_privilege(
        self,
        principal_id: str,
        resource_id: str,
        privilege_type: PrivilegeType,
        grant_option: GrantOption = GrantOption.NONE,
        granted_by: str = "",
        expires_at: Optional[datetime] = None
    ) -> str:
        """
        Grant privilege to principal
        
        Args:
            principal_id: Principal ID (user or role)
            resource_id: Resource ID
            privilege_type: Type of privilege
            grant_option: Grant option
            granted_by: Granter user ID
            expires_at: Privilege expiration time
            
        Returns:
            Grant ID
        """



        try:
            # Create privilege grant
            grant = PrivilegeGrant(
                grant_id=str(uuid.uuid4()),
                principal_id=principal_id,
                principal_type=self._get_principal_type(principal_id),
                resource_id=resource_id,
                privilege_type=privilege_type,
                grant_option=grant_option,
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            # Store grant
            self.privilege_grants[grant.grant_id] = grant
            
            # Execute privilege grant in database (if privilege engine available)
            await self._execute_privilege_grant(grant)
            
            # Audit privilege grant
            await self._audit_action(
                action="grant_privilege",
                principal_id=principal_id,
                resource_id=resource_id,
                privilege_type=privilege_type,
                performed_by=granted_by,
                details={
                    "grant_id": grant.grant_id,
                    "grant_option": grant_option.value,
                    "expires_at": expires_at.isoformat() if expires_at else None
                }
            )
            
            logger.info(f"Granted {privilege_type.value} on {resource_id} to {principal_id}")
            return grant.grant_id
            
        except Exception as e:
            logger.error(f"Failed to grant privilege: {e}")
            await self._audit_action(
                action="grant_privilege",
                principal_id=principal_id,
                resource_id=resource_id,
                privilege_type=privilege_type,
                performed_by=granted_by,
                success=False,
                error_message=str(e)
            )
            raise
    
    async def revoke_privilege(
        self,
        principal_id: str,
        resource_id: str,
        privilege_type: PrivilegeType,
        revoked_by: str = ""
    ) -> bool:
        """
        Revoke privilege from principal
        
        Args:
            principal_id: Principal ID
            resource_id: Resource ID
            privilege_type: Type of privilege
            revoked_by: Revoker user ID
            
        Returns:
            True if successful, False otherwise
        """



        try:
            # Find matching grant
            grant_to_revoke = None
            for grant in self.privilege_grants.values():
                if (grant.principal_id == principal_id and
                    grant.resource_id == resource_id and
                    grant.privilege_type == privilege_type and
                    grant.is_active):
                    grant_to_revoke = grant
                    break
            
            if not grant_to_revoke:
                logger.warning(f"No active grant found to revoke")
                return False
            
            # Deactivate grant
            grant_to_revoke.is_active = False
            
            # Execute privilege revocation in database
            await self._execute_privilege_revoke(grant_to_revoke)
            
            # Audit privilege revocation
            await self._audit_action(
                action="revoke_privilege",
                principal_id=principal_id,
                resource_id=resource_id,
                privilege_type=privilege_type,
                performed_by=revoked_by,
                details={"grant_id": grant_to_revoke.grant_id}
            )
            
            logger.info(f"Revoked {privilege_type.value} on {resource_id} from {principal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke privilege: {e}")
            await self._audit_action(
                action="revoke_privilege",
                principal_id=principal_id,
                resource_id=resource_id,
                privilege_type=privilege_type,
                performed_by=revoked_by,
                success=False,
                error_message=str(e)
            )
            return False
    
    async def check_user_privilege(
        self,
        user_id: str,
        resource_id: str,
        privilege_type: PrivilegeType
    ) -> bool:
        """
        Check if user has privilege on resource
        
        Args:
            user_id: User ID
            resource_id: Resource ID
            privilege_type: Type of privilege
            
        Returns:
            True if user has privilege, False otherwise
        """



        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            
            # Check direct user privileges
            if await self._has_direct_privilege(user_id, resource_id, privilege_type):
                return True
            
            # Check role-based privileges
            all_roles = await self._get_all_user_roles(user_id)
            for role_id in all_roles:
                if await self._has_direct_privilege(role_id, resource_id, privilege_type):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check user privilege: {e}")
            return False
    
    async def _has_direct_privilege(
        self,
        principal_id: str,
        resource_id: str,
        privilege_type: PrivilegeType
    ) -> bool:
        """Check if principal has direct privilege"""
        current_time = datetime.now()
        
        for grant in self.privilege_grants.values():
            if (grant.principal_id == principal_id and
                grant.resource_id == resource_id and
                grant.privilege_type == privilege_type and
                grant.is_active):
                
                # Check expiration
                if grant.expires_at and grant.expires_at < current_time:
                    grant.is_active = False
                    continue
                
                return True
        
        return False
    
    async def _get_all_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for user including inherited roles"""
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        all_roles = set()
        
        # Process direct roles
        roles_to_process = user.roles.copy()
        
        while roles_to_process:
            role_id = roles_to_process.pop(0)
            if role_id in all_roles:
                continue
            
            all_roles.add(role_id)
            
            # Add parent roles
            if role_id in self.roles:
                role = self.roles[role_id]
                roles_to_process.extend(role.parent_roles)
        
        return list(all_roles)
    
    def _get_principal_type(self, principal_id: str) -> str:
        """Determine principal type"""
        if principal_id in self.users:
            return "user"
        elif principal_id in self.roles:
            return "role"
        else:
            return "unknown"
    
    async def _execute_privilege_grant(self, grant: PrivilegeGrant):
        """Execute privilege grant in database"""
        # In production, this would use appropriate privilege engine
        logger.info(f"Would execute privilege grant: {grant.grant_id}")
    
    async def _execute_privilege_revoke(self, grant: PrivilegeGrant):
        """Execute privilege revocation in database"""
        # In production, this would use appropriate privilege engine
        logger.info(f"Would execute privilege revoke: {grant.grant_id}")
    
    async def _audit_action(
        self,
        action: str,
        principal_id: str,
        resource_id: str,
        privilege_type: Optional[PrivilegeType] = None,
        performed_by: str = "",
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Audit privilege action"""
        audit = PrivilegeAudit(
            audit_id=str(uuid.uuid4()),
            action=action,
            principal_id=principal_id,
            resource_id=resource_id,
            privilege_type=privilege_type,
            performed_by=performed_by,
            success=success,
            error_message=error_message,
            details=details or {}
        )
        
        self.audit_records.append(audit)
        
        # Keep only recent audit records (e.g., last 10000)
        if len(self.audit_records) > 10000:
            self.audit_records = self.audit_records[-10000:]
    
    def get_user_privileges(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive privilege summary for user"""
        if user_id not in self.users:
            return {"error": "User not found"}
        
        user = self.users[user_id]
        
        # Get direct privileges
        direct_privileges = [
            {
                "grant_id": grant.grant_id,
                "resource_id": grant.resource_id,
                "privilege_type": grant.privilege_type.value,
                "grant_option": grant.grant_option.value,
                "expires_at": grant.expires_at.isoformat() if grant.expires_at else None
            }
            for grant in self.privilege_grants.values()
            if grant.principal_id == user_id and grant.is_active
        ]
        
        # Get role privileges
        role_privileges = []
        for role_id in user.roles:
            if role_id in self.roles:
                role = self.roles[role_id]
                role_grants = [
                    {
                        "grant_id": grant.grant_id,
                        "resource_id": grant.resource_id,
                        "privilege_type": grant.privilege_type.value,
                        "role_name": role.name
                    }
                    for grant in self.privilege_grants.values()
                    if grant.principal_id == role_id and grant.is_active
                ]
                role_privileges.extend(role_grants)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "roles": [
                {"role_id": role_id, "name": self.roles[role_id].name}
                for role_id in user.roles
                if role_id in self.roles
            ],
            "direct_privileges": direct_privileges,
            "role_privileges": role_privileges,
            "total_privileges": len(direct_privileges) + len(role_privileges)
        }
    
    def get_privilege_metrics(self) -> Dict[str, Any]:
        """Get privilege management metrics"""
        active_grants = sum(1 for grant in self.privilege_grants.values() if grant.is_active)
        expired_grants = sum(
            1 for grant in self.privilege_grants.values() 
            if grant.expires_at and grant.expires_at < datetime.now()
        )
        
        return {
            "total_users": len(self.users),
            "active_users": sum(1 for user in self.users.values() if user.is_active),
            "total_roles": len(self.roles),
            "system_roles": sum(1 for role in self.roles.values() if role.is_system_role),
            "total_privilege_grants": len(self.privilege_grants),
            "active_grants": active_grants,
            "expired_grants": expired_grants,
            "total_audit_records": len(self.audit_records)
        }


# Module initialization
logger.info("Database privilege manager module loaded successfully")
