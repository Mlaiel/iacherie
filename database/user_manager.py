"""Database User Privilege Management System
============================================

Production database user and privilege management with minimal privilege
principle implementation for service-based access control.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
try:
    import asyncpg
except ImportError:
    asyncpg = None
import secrets
import hashlib
import base64

logger = logging.getLogger(__name__)

class ServiceRole(Enum):
    """Service roles with specific access patterns"""
    APPLICATION = "ainflue_app"
    READ_ONLY = "ainflue_readonly"
    BACKUP = "ainflue_backup"
    REPLICATION = "ainflue_replication"
    ADMIN = "ainflue_admin"
    MONITORING = "ainflue_monitor"
    ANALYTICS = "ainflue_analytics"
    MIGRATION = "ainflue_migration"

class PrivilegeLevel(Enum):
    """Privilege levels from most to least restrictive"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    DDL = "ddl"
    ADMIN = "admin"
    SUPERUSER = "superuser"

@dataclass
class DatabaseSchema:
    """Database schema definition"""
    name: str
    tables: List[str] = field(default_factory=list)
    views: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    sequences: List[str] = field(default_factory=list)
    description: str = ""

@dataclass
class ServicePrivileges:
    """Privileges for a specific service"""
    service_role: ServiceRole
    schemas: List[str] = field(default_factory=list)
    tables: Dict[str, List[str]] = field(default_factory=dict)  # schema.table: [SELECT, INSERT, etc.]
    privilege_level: PrivilegeLevel = PrivilegeLevel.READ_ONLY
    connection_limit: int = 10
    password_expires: Optional[datetime] = None
    ip_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Optional[Dict[str, str]] = None
    additional_grants: List[str] = field(default_factory=list)

@dataclass
class UserAccount:
    """Database user account information"""
    username: str
    service_role: ServiceRole
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    password_expires: Optional[datetime] = None
    is_active: bool = True
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    connection_limit: int = 10
    privileges: Optional[ServicePrivileges] = None

class DatabaseUserManager:
    """Comprehensive database user and privilege management"""
    
    def __init__(self, admin_connection_pool):
        self.admin_pool = admin_connection_pool
        self.schemas = self._define_schemas()
        self.service_privileges = self._define_service_privileges()
        
    def _define_schemas(self) -> Dict[str, DatabaseSchema]:
        """Define application schemas and their components"""
        return {
            "public": DatabaseSchema(
                name="public",
                description="Main application schema"
            ),
            "content": DatabaseSchema(
                name="content",
                tables=["creators", "content_items", "fingerprints", "metadata"],
                description="Content and creator management"
            ),
            "protection": DatabaseSchema(
                name="protection", 
                tables=["violations", "monitoring", "reports", "licenses"],
                description="Content protection and monitoring"
            ),
            "analytics": DatabaseSchema(
                name="analytics",
                tables=["events", "metrics", "aggregations", "reports"],
                description="Analytics and reporting data"
            ),
            "revenue": DatabaseSchema(
                name="revenue",
                tables=["transactions", "payments", "royalties", "billing"],
                description="Revenue and monetization"
            ),
            "system": DatabaseSchema(
                name="system",
                tables=["migrations", "audit_logs", "configurations", "health_checks"],
                description="System and operational data"
            )
        }
    
    def _define_service_privileges(self) -> Dict[ServiceRole, ServicePrivileges]:
        """Define privilege sets for each service role"""
        return {
            ServiceRole.APPLICATION: ServicePrivileges(
                service_role=ServiceRole.APPLICATION,
                schemas=["public", "content", "protection", "revenue"],
                tables={
                    "content.*": ["SELECT", "INSERT", "UPDATE", "DELETE"],
                    "protection.*": ["SELECT", "INSERT", "UPDATE"],
                    "revenue.*": ["SELECT", "INSERT", "UPDATE"],
                    "system.configurations": ["SELECT"],
                    "system.health_checks": ["INSERT", "UPDATE"]
                },
                privilege_level=PrivilegeLevel.READ_WRITE,
                connection_limit=50,
                additional_grants=[
                    "USAGE ON ALL SEQUENCES IN SCHEMA content",
                    "USAGE ON ALL SEQUENCES IN SCHEMA protection",
                    "USAGE ON ALL SEQUENCES IN SCHEMA revenue"
                ]
            ),
            
            ServiceRole.READ_ONLY: ServicePrivileges(
                service_role=ServiceRole.READ_ONLY,
                schemas=["public", "content", "protection", "revenue", "analytics"],
                tables={
                    "content.*": ["SELECT"],
                    "protection.*": ["SELECT"],
                    "revenue.*": ["SELECT"],
                    "analytics.*": ["SELECT"],
                    "system.configurations": ["SELECT"]
                },
                privilege_level=PrivilegeLevel.READ_ONLY,
                connection_limit=20
            ),
            
            ServiceRole.BACKUP: ServicePrivileges(
                service_role=ServiceRole.BACKUP,
                schemas=["public", "content", "protection", "revenue", "analytics", "system"],
                tables={
                    "*.*": ["SELECT"]  # Full read access for backup
                },
                privilege_level=PrivilegeLevel.READ_ONLY,
                connection_limit=5,
                additional_grants=[
                    "pg_read_all_data",  # PostgreSQL 14+ role for backup access
                    "USAGE ON SCHEMA information_schema",
                    "USAGE ON SCHEMA pg_catalog"
                ]
            ),
            
            ServiceRole.REPLICATION: ServicePrivileges(
                service_role=ServiceRole.REPLICATION,
                schemas=["public", "content", "protection", "revenue", "analytics", "system"],
                tables={},  # Replication doesn't use table-level privileges
                privilege_level=PrivilegeLevel.READ_ONLY,
                connection_limit=10,
                additional_grants=[
                    "REPLICATION",
                    "pg_read_all_data"
                ]
            ),
            
            ServiceRole.MONITORING: ServicePrivileges(
                service_role=ServiceRole.MONITORING,
                schemas=["public", "system"],
                tables={
                    "system.health_checks": ["SELECT", "INSERT", "UPDATE"],
                    "system.audit_logs": ["SELECT"],
                    "pg_stat_*": ["SELECT"],  # PostgreSQL stats tables
                    "pg_catalog.*": ["SELECT"]
                },
                privilege_level=PrivilegeLevel.READ_ONLY,
                connection_limit=15,
                additional_grants=[
                    "pg_monitor",  # PostgreSQL monitoring role
                    "pg_read_all_stats"
                ]
            ),
            
            ServiceRole.ANALYTICS: ServicePrivileges(
                service_role=ServiceRole.ANALYTICS,
                schemas=["analytics", "content", "protection", "revenue"],
                tables={
                    "analytics.*": ["SELECT", "INSERT", "UPDATE", "DELETE"],
                    "content.*": ["SELECT"],
                    "protection.*": ["SELECT"],
                    "revenue.*": ["SELECT"]
                },
                privilege_level=PrivilegeLevel.READ_WRITE,
                connection_limit=25,
                additional_grants=[
                    "USAGE ON ALL SEQUENCES IN SCHEMA analytics"
                ]
            ),
            
            ServiceRole.MIGRATION: ServicePrivileges(
                service_role=ServiceRole.MIGRATION,
                schemas=["public", "content", "protection", "revenue", "analytics", "system"],
                tables={
                    "*.*": ["SELECT", "INSERT", "UPDATE", "DELETE"]
                },
                privilege_level=PrivilegeLevel.DDL,
                connection_limit=3,
                additional_grants=[
                    "CREATE ON DATABASE ainflue_prod",
                    "CREATE ON ALL SCHEMAS"
                ]
            ),
            
            ServiceRole.ADMIN: ServicePrivileges(
                service_role=ServiceRole.ADMIN,
                schemas=["public", "content", "protection", "revenue", "analytics", "system"],
                tables={
                    "*.*": ["ALL PRIVILEGES"]
                },
                privilege_level=PrivilegeLevel.ADMIN,
                connection_limit=5,
                additional_grants=[
                    "CREATE ON DATABASE ainflue_prod",
                    "CREATE ON ALL SCHEMAS",
                    "ALL PRIVILEGES ON ALL TABLES",
                    "ALL PRIVILEGES ON ALL SEQUENCES",
                    "ALL PRIVILEGES ON ALL FUNCTIONS"
                ]
            )
        }
    
    async def setup_user_management_system(self) -> Dict[str, Any]:
        """Setup complete user management system"""
        try:
            setup_results = {}
            
            # 1. Create schemas if they don't exist
            schema_result = await self._create_application_schemas()
            setup_results["schemas"] = schema_result
            
            # 2. Create service roles and users
            users_result = await self._create_service_users()
            setup_results["users"] = users_result
            
            # 3. Configure privileges for each service
            privileges_result = await self._configure_service_privileges()
            setup_results["privileges"] = privileges_result
            
            # 4. Setup security policies
            security_result = await self._setup_security_policies()
            setup_results["security"] = security_result
            
            # 5. Create monitoring and audit tables
            monitoring_result = await self._setup_user_monitoring()
            setup_results["monitoring"] = monitoring_result
            
            logger.info("User management system setup completed successfully")
            return {
                "success": True,
                "results": setup_results,
                "setup_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User management system setup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_application_schemas(self) -> Dict[str, Any]:
        """Create application schemas"""
        try:
            created_schemas = []
            existing_schemas = []
            
            async with self.admin_pool.acquire() as conn:
                for schema_name, schema_def in self.schemas.items():
                    if schema_name == "public":  # Skip public schema
                        continue
                    
                    # Check if schema exists
                    exists = await conn.fetchval("""
                        SELECT EXISTS(SELECT 1 FROM information_schema.schemata 
                                    WHERE schema_name = $1)
                    """, schema_name)
                    
                    if not exists:
                        await conn.execute(f"CREATE SCHEMA {schema_name}")
                        await conn.execute(f"COMMENT ON SCHEMA {schema_name} IS '{schema_def.description}'")
                        created_schemas.append(schema_name)
                        logger.info(f"Created schema: {schema_name}")
                    else:
                        existing_schemas.append(schema_name)
            
            return {
                "created": created_schemas,
                "existing": existing_schemas,
                "total_schemas": len(self.schemas)
            }
            
        except Exception as e:
            logger.error(f"Schema creation failed: {e}")
            raise
    
    async def _create_service_users(self) -> Dict[str, Any]:
        """Create service users with secure passwords"""
        try:
            created_users = []
            existing_users = []
            user_credentials = {}
            
            async with self.admin_pool.acquire() as conn:
                for service_role in ServiceRole:
                    username = service_role.value
                    
                    # Check if user exists
                    exists = await conn.fetchval("""
                        SELECT EXISTS(SELECT 1 FROM pg_user WHERE usename = $1)
                    """, username)
                    
                    if not exists:
                        # Generate secure password
                        password = self._generate_secure_password()
                        
                        # Create user with connection limit
                        privileges = self.service_privileges[service_role]
                        await conn.execute(f"""
                            CREATE USER {username} 
                            WITH PASSWORD '{password}'
                            CONNECTION LIMIT {privileges.connection_limit}
                        """)
                        
                        # Set password expiration if specified
                        if privileges.password_expires:
                            await conn.execute(f"""
                                ALTER USER {username} 
                                VALID UNTIL '{privileges.password_expires}'
                            """)
                        
                        created_users.append(username)
                        user_credentials[username] = {
                            "password": password,
                            "role": service_role.value,
                            "connection_limit": privileges.connection_limit
                        }
                        
                        logger.info(f"Created user: {username}")
                    else:
                        existing_users.append(username)
            
            return {
                "created": created_users,
                "existing": existing_users,
                "credentials": user_credentials,  # Store securely in production
                "total_users": len(ServiceRole)
            }
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise
    
    async def _configure_service_privileges(self) -> Dict[str, Any]:
        """Configure privileges for each service user"""
        try:
            configured_privileges = {}
            
            async with self.admin_pool.acquire() as conn:
                for service_role, privileges in self.service_privileges.items():
                    username = service_role.value
                    privilege_summary = []
                    
                    # Grant schema usage
                    for schema_name in privileges.schemas:
                        await conn.execute(f"GRANT USAGE ON SCHEMA {schema_name} TO {username}")
                        privilege_summary.append(f"USAGE on schema {schema_name}")
                    
                    # Grant table privileges
                    for table_pattern, perms in privileges.tables.items():
                        if table_pattern == "*.*":
                            # Grant on all tables in all schemas
                            for schema_name in privileges.schemas:
                                if schema_name == "public":
                                    continue
                                for perm in perms:
                                    if perm == "ALL PRIVILEGES":
                                        await conn.execute(f"""
                                            GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {username}
                                        """)
                                    else:
                                        await conn.execute(f"""
                                            GRANT {perm} ON ALL TABLES IN SCHEMA {schema_name} TO {username}
                                        """)
                                privilege_summary.append(f"{', '.join(perms)} on all tables in {schema_name}")
                        
                        elif ".*" in table_pattern:
                            # Grant on all tables in specific schema
                            schema_name = table_pattern.split(".")[0]
                            for perm in perms:
                                await conn.execute(f"""
                                    GRANT {perm} ON ALL TABLES IN SCHEMA {schema_name} TO {username}
                                """)
                            privilege_summary.append(f"{', '.join(perms)} on all tables in {schema_name}")
                        
                        else:
                            # Grant on specific table
                            table_name = table_pattern
                            for perm in perms:
                                await conn.execute(f"GRANT {perm} ON {table_name} TO {username}")
                            privilege_summary.append(f"{', '.join(perms)} on {table_name}")
                    
                    # Grant additional privileges
                    for grant in privileges.additional_grants:
                        try:
                            if grant.startswith("pg_"):
                                # PostgreSQL predefined roles
                                await conn.execute(f"GRANT {grant} TO {username}")
                            else:
                                # Custom grants
                                await conn.execute(f"GRANT {grant} TO {username}")
                            privilege_summary.append(grant)
                        except Exception as e:
                            logger.warning(f"Failed to grant '{grant}' to {username}: {e}")
                    
                    # Set default privileges for future objects
                    await self._set_default_privileges(conn, username, privileges)
                    
                    configured_privileges[username] = {
                        "privilege_level": privileges.privilege_level.value,
                        "schemas": privileges.schemas,
                        "grants": privilege_summary
                    }
                    
                    logger.info(f"Configured privileges for user: {username}")
            
            return {
                "configured_users": list(configured_privileges.keys()),
                "privilege_details": configured_privileges
            }
            
        except Exception as e:
            logger.error(f"Privilege configuration failed: {e}")
            raise
    
    async def _set_default_privileges(self, conn, username: str, privileges: ServicePrivileges):
        """Set default privileges for future objects"""
        try:
            for schema_name in privileges.schemas:
                if schema_name == "public":
                    continue
                
                # Default privileges on tables
                if privileges.privilege_level in [PrivilegeLevel.READ_WRITE, PrivilegeLevel.DDL, PrivilegeLevel.ADMIN]:
                    await conn.execute(f"""
                        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
                        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {username}
                    """)
                    
                    await conn.execute(f"""
                        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
                        GRANT USAGE, SELECT ON SEQUENCES TO {username}
                    """)
                else:
                    await conn.execute(f"""
                        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
                        GRANT SELECT ON TABLES TO {username}
                    """)
        
        except Exception as e:
            logger.warning(f"Failed to set default privileges for {username}: {e}")
    
    async def _setup_security_policies(self) -> Dict[str, Any]:
        """Setup security policies and constraints"""
        try:
            security_features = []
            
            async with self.admin_pool.acquire() as conn:
                # 1. Enable row level security on sensitive tables
                sensitive_tables = [
                    "content.creators",
                    "revenue.transactions",
                    "revenue.payments",
                    "system.audit_logs"
                ]
                
                for table in sensitive_tables:
                    try:
                        await conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
                        security_features.append(f"RLS enabled on {table}")
                    except Exception as e:
                        logger.warning(f"Failed to enable RLS on {table}: {e}")
                
                # 2. Create security policies
                policies = [
                    {
                        "table": "content.creators",
                        "policy": "creator_access",
                        "rule": "USING (created_by = current_user OR current_user = 'ainflue_admin')"
                    },
                    {
                        "table": "system.audit_logs", 
                        "policy": "audit_read_only",
                        "rule": "USING (current_user IN ('ainflue_admin', 'ainflue_monitor'))"
                    }
                ]
                
                for policy in policies:
                    try:
                        await conn.execute(f"""
                            CREATE POLICY {policy['policy']} ON {policy['table']}
                            FOR ALL TO PUBLIC {policy['rule']}
                        """)
                        security_features.append(f"Policy {policy['policy']} created on {policy['table']}")
                    except Exception as e:
                        logger.warning(f"Failed to create policy {policy['policy']}: {e}")
                
                # 3. Setup connection security
                await conn.execute("ALTER SYSTEM SET log_connections = on")
                await conn.execute("ALTER SYSTEM SET log_disconnections = on")
                await conn.execute("ALTER SYSTEM SET log_statement = 'ddl'")
                
                security_features.extend([
                    "Connection logging enabled",
                    "DDL statement logging enabled"
                ])
            
            return {
                "security_features": security_features,
                "policies_created": len([f for f in security_features if "Policy" in f])
            }
            
        except Exception as e:
            logger.error(f"Security policy setup failed: {e}")
            raise
    
    async def _setup_user_monitoring(self) -> Dict[str, Any]:
        """Setup user activity monitoring"""
        try:
            monitoring_features = []
            
            async with self.admin_pool.acquire() as conn:
                # Create audit log table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS system.user_audit_log (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(64) NOT NULL,
                        action VARCHAR(50) NOT NULL,
                        table_name VARCHAR(128),
                        record_id VARCHAR(50),
                        old_values JSONB,
                        new_values JSONB,
                        client_ip INET,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create login tracking table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS system.user_login_log (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(64) NOT NULL,
                        client_ip INET,
                        success BOOLEAN NOT NULL,
                        failure_reason VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create privilege changes table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS system.privilege_changes (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(64) NOT NULL,
                        changed_by VARCHAR(64) NOT NULL,
                        privilege_type VARCHAR(50) NOT NULL,
                        old_privilege VARCHAR(255),
                        new_privilege VARCHAR(255),
                        reason TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                monitoring_features.extend([
                    "User audit log table created",
                    "Login tracking table created", 
                    "Privilege changes table created"
                ])
                
                # Create monitoring views
                await conn.execute("""
                    CREATE OR REPLACE VIEW system.user_activity_summary AS
                    SELECT 
                        username,
                        COUNT(*) as total_actions,
                        COUNT(DISTINCT DATE(created_at)) as active_days,
                        MAX(created_at) as last_activity,
                        COUNT(CASE WHEN action = 'LOGIN' THEN 1 END) as login_count
                    FROM system.user_audit_log
                    WHERE created_at > NOW() - INTERVAL '30 days'
                    GROUP BY username
                """)
                
                monitoring_features.append("User activity summary view created")
                
                # Grant monitoring access
                await conn.execute("GRANT SELECT ON system.user_audit_log TO ainflue_monitor")
                await conn.execute("GRANT SELECT ON system.user_login_log TO ainflue_monitor")
                await conn.execute("GRANT SELECT ON system.user_activity_summary TO ainflue_monitor")
                
                monitoring_features.append("Monitoring privileges granted")
            
            return {
                "monitoring_features": monitoring_features,
                "tables_created": 3,
                "views_created": 1
            }
            
        except Exception as e:
            logger.error(f"User monitoring setup failed: {e}")
            raise
    
    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        # Use cryptographically secure random generator
        password_bytes = secrets.token_bytes(length)
        # Encode as base64 and remove padding for cleaner password
        password = base64.urlsafe_b64encode(password_bytes).decode('utf-8').rstrip('=')
        return password[:length]
    
    async def create_user_account(self, service_role: ServiceRole, custom_privileges: Optional[ServicePrivileges] = None) -> Dict[str, Any]:
        """Create a new user account with specified privileges"""
        try:
            username = service_role.value
            privileges = custom_privileges or self.service_privileges[service_role]
            password = self._generate_secure_password()
            
            async with self.admin_pool.acquire() as conn:
                # Create user
                await conn.execute(f"""
                    CREATE USER {username} 
                    WITH PASSWORD '{password}'
                    CONNECTION LIMIT {privileges.connection_limit}
                """)
                
                # Apply privileges
                await self._apply_user_privileges(conn, username, privileges)
                
                # Log user creation
                await conn.execute("""
                    INSERT INTO system.privilege_changes 
                    (username, changed_by, privilege_type, new_privilege, reason)
                    VALUES ($1, $2, $3, $4, $5)
                """, username, "system", "CREATE_USER", service_role.value, f"Created {service_role.value} user")
                
                logger.info(f"Created user account: {username}")
                
                return {
                    "success": True,
                    "username": username,
                    "password": password,  # Store securely in production
                    "service_role": service_role.value,
                    "connection_limit": privileges.connection_limit,
                    "created_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"User account creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _apply_user_privileges(self, conn, username: str, privileges: ServicePrivileges):
        """Apply privileges to a user"""
        # Grant schema usage
        for schema_name in privileges.schemas:
            await conn.execute(f"GRANT USAGE ON SCHEMA {schema_name} TO {username}")
        
        # Grant table privileges  
        for table_pattern, perms in privileges.tables.items():
            for perm in perms:
                if "*.*" in table_pattern:
                    for schema_name in privileges.schemas:
                        await conn.execute(f"""
                            GRANT {perm} ON ALL TABLES IN SCHEMA {schema_name} TO {username}
                        """)
                else:
                    await conn.execute(f"GRANT {perm} ON {table_pattern} TO {username}")
        
        # Grant additional privileges
        for grant in privileges.additional_grants:
            await conn.execute(f"GRANT {grant} TO {username}")
    
    async def rotate_user_password(self, username: str) -> Dict[str, Any]:
        """Rotate password for a user"""
        try:
            new_password = self._generate_secure_password()
            
            async with self.admin_pool.acquire() as conn:
                await conn.execute(f"ALTER USER {username} WITH PASSWORD '{new_password}'")
                
                # Log password rotation
                await conn.execute("""
                    INSERT INTO system.privilege_changes 
                    (username, changed_by, privilege_type, reason)
                    VALUES ($1, $2, $3, $4)
                """, username, "system", "PASSWORD_ROTATION", "Scheduled password rotation")
                
                logger.info(f"Rotated password for user: {username}")
                
                return {
                    "success": True,
                    "username": username,
                    "new_password": new_password,  # Store securely in production
                    "rotated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Password rotation failed for {username}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def audit_user_privileges(self) -> Dict[str, Any]:
        """Audit current user privileges and detect anomalies"""
        try:
            audit_results = {}
            
            async with self.admin_pool.acquire() as conn:
                # Get current users and their privileges
                users = await conn.fetch("""
                    SELECT rolname, rolconnlimit, rolvaliduntil, 
                           rolcanlogin, rolsuper, rolcreaterole, rolcreatedb
                    FROM pg_roles 
                    WHERE rolname LIKE 'ainflue_%'
                    ORDER BY rolname
                """)
                
                for user in users:
                    username = user['rolname']
                    
                    # Get user's table privileges
                    table_privs = await conn.fetch("""
                        SELECT schemaname, tablename, privilege_type
                        FROM information_schema.table_privileges
                        WHERE grantee = $1
                        ORDER BY schemaname, tablename
                    """, username)
                    
                    # Get user's schema privileges
                    schema_privs = await conn.fetch("""
                        SELECT schema_name, privilege_type
                        FROM information_schema.usage_privileges
                        WHERE grantee = $1
                        ORDER BY schema_name
                    """, username)
                    
                    audit_results[username] = {
                        "connection_limit": user['rolconnlimit'],
                        "password_expires": user['rolvaliduntil'].isoformat() if user['rolvaliduntil'] else None,
                        "can_login": user['rolcanlogin'],
                        "is_superuser": user['rolsuper'],
                        "can_create_roles": user['rolcreaterole'],
                        "can_create_db": user['rolcreatedb'],
                        "table_privileges": [
                            f"{row['schemaname']}.{row['tablename']}: {row['privilege_type']}"
                            for row in table_privs
                        ],
                        "schema_privileges": [
                            f"{row['schema_name']}: {row['privilege_type']}"
                            for row in schema_privs
                        ]
                    }
                
                # Check for privilege anomalies
                anomalies = []
                for username, privileges in audit_results.items():
                    if privileges["is_superuser"] and username != "ainflue_admin":
                        anomalies.append(f"{username} has superuser privileges")
                    
                    if privileges["can_create_roles"] and username not in ["ainflue_admin", "ainflue_migration"]:
                        anomalies.append(f"{username} can create roles")
                
                return {
                    "audit_timestamp": datetime.utcnow().isoformat(),
                    "users_audited": len(audit_results),
                    "user_privileges": audit_results,
                    "anomalies": anomalies,
                    "anomalies_detected": len(anomalies)
                }
                
        except Exception as e:
            logger.error(f"User privilege audit failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_activity_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate user activity report"""
        try:
            async with self.admin_pool.acquire() as conn:
                # User activity summary
                activity = await conn.fetch("""
                    SELECT username, total_actions, active_days, 
                           last_activity, login_count
                    FROM system.user_activity_summary
                """)
                
                # Recent login attempts
                recent_logins = await conn.fetch("""
                    SELECT username, client_ip, success, failure_reason, created_at
                    FROM system.user_login_log
                    WHERE created_at > NOW() - INTERVAL %s DAY
                    ORDER BY created_at DESC
                    LIMIT 100
                """, days)
                
                # Current connections
                current_connections = await conn.fetch("""
                    SELECT usename, client_addr, state, 
                           query_start, state_change
                    FROM pg_stat_activity
                    WHERE usename LIKE 'ainflue_%'
                    AND state != 'idle'
                """)
                
                return {
                    "report_period_days": days,
                    "generated_at": datetime.utcnow().isoformat(),
                    "user_activity": [dict(row) for row in activity],
                    "recent_logins": [dict(row) for row in recent_logins],
                    "current_connections": [dict(row) for row in current_connections],
                    "total_users": len(activity)
                }
                
        except Exception as e:
            logger.error(f"User activity report generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }