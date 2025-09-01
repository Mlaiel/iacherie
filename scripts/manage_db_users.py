#!/usr/bin/env python3
"""Production Database User Management with Minimal Privileges

This script creates and manages database users with service-specific
minimal privileges following the principle of least privilege.

Usage:
    python scripts/manage_db_users.py create
    python scripts/manage_db_users.py update
    python scripts/manage_db_users.py audit

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import os
import sys
import logging
import argparse
import secrets
import string
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseUser:
    """Database user configuration."""
    username: str
    password: str
    role: str
    description: str
    privileges: List[str]
    connection_limit: int = 20
    valid_until: Optional[str] = None
    schemas: List[str] = None
    tables: List[str] = None

class ProductionUserManager:
    """Production database user management with minimal privileges."""
    
    def __init__(self):
        self.admin_connection_string = self._get_admin_connection_string()
        self.users_config = self._define_service_users()
    
    def _get_admin_connection_string(self) -> str:
        """Get admin connection string for user management."""
        return "postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
            user=os.getenv('POSTGRES_ADMIN_USER', 'postgres'),
            password=os.getenv('POSTGRES_ADMIN_PASSWORD', ''),
            host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
            database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
        )
    
    def _generate_password(self, length: int = 32) -> str:
        """Generate secure password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _define_service_users(self) -> List[DatabaseUser]:
        """Define all service users with minimal privileges."""
        return [
            # Application read-write user
            DatabaseUser(
                username="ainflue_app",
                password=os.getenv('POSTGRES_APP_PASSWORD') or self._generate_password(),
                role="application",
                description="Main application user with read-write access to application tables",
                privileges=[
                    "CONNECT",
                    "SELECT ON ALL TABLES IN SCHEMA public",
                    "INSERT ON content_metadata, users, creators, analytics_events",
                    "UPDATE ON content_metadata, users, creators, analytics_events",
                    "DELETE ON content_metadata WHERE creator_id = current_user_id()",
                    "USAGE ON ALL SEQUENCES IN SCHEMA public"
                ],
                connection_limit=50,
                schemas=["public"],
                tables=["content_metadata", "users", "creators", "analytics_events", "payment_records"]
            ),
            
            # Read-only user for analytics and reporting
            DatabaseUser(
                username="ainflue_read",
                password=os.getenv('POSTGRES_READ_PASSWORD') or self._generate_password(),
                role="readonly",
                description="Read-only user for analytics and reporting",
                privileges=[
                    "CONNECT",
                    "SELECT ON ALL TABLES IN SCHEMA public"
                ],
                connection_limit=25,
                schemas=["public"]
            ),
            
            # Backup user with minimal required privileges
            DatabaseUser(
                username="backup_user",
                password=os.getenv('POSTGRES_BACKUP_PASSWORD') or self._generate_password(),
                role="backup",
                description="Backup user with minimal privileges for pg_dump",
                privileges=[
                    "CONNECT",
                    "SELECT ON ALL TABLES IN SCHEMA public",
                    "USAGE ON SCHEMA public"
                ],
                connection_limit=5,
                schemas=["public"]
            ),
            
            # Monitoring user
            DatabaseUser(
                username="monitoring",
                password=os.getenv('POSTGRES_MONITORING_PASSWORD') or self._generate_password(),
                role="monitoring",
                description="Monitoring user for health checks and metrics",
                privileges=[
                    "CONNECT",
                    "SELECT ON pg_stat_database",
                    "SELECT ON pg_stat_activity",
                    "SELECT ON pg_stat_replication",
                    "SELECT ON pg_stat_statements",
                    "SELECT ON pg_database_size",
                    "EXECUTE ON FUNCTION pg_database_size(name)"
                ],
                connection_limit=10,
                schemas=["pg_catalog", "information_schema"]
            ),
            
            # Replication user
            DatabaseUser(
                username="replicator",
                password=os.getenv('POSTGRES_REPLICATION_PASSWORD') or self._generate_password(),
                role="replication",
                description="Replication user for master-slave setup",
                privileges=[
                    "REPLICATION",
                    "LOGIN"
                ],
                connection_limit=10
            ),
            
            # Rights tracking service user
            DatabaseUser(
                username="rights_service",
                password=os.getenv('POSTGRES_RIGHTS_PASSWORD') or self._generate_password(),
                role="service",
                description="Rights tracking service with access to protection tables",
                privileges=[
                    "CONNECT",
                    "SELECT ON ALL TABLES IN SCHEMA public",
                    "INSERT ON rights_records, license_agreements, audit_logs",
                    "UPDATE ON rights_records, license_agreements",
                    "USAGE ON ALL SEQUENCES IN SCHEMA public"
                ],
                connection_limit=15,
                schemas=["public"],
                tables=["rights_records", "license_agreements", "audit_logs", "content_metadata"]
            ),
            
            # Analytics service user
            DatabaseUser(
                username="analytics_service",
                password=os.getenv('POSTGRES_ANALYTICS_PASSWORD') or self._generate_password(),
                role="service",
                description="Analytics service with read access and write to analytics tables",
                privileges=[
                    "CONNECT",
                    "SELECT ON ALL TABLES IN SCHEMA public",
                    "INSERT ON analytics_events",
                    "UPDATE ON analytics_events",
                    "USAGE ON ALL SEQUENCES IN SCHEMA public"
                ],
                connection_limit=20,
                schemas=["public"],
                tables=["analytics_events", "content_metadata", "users"]
            )
        ]
    
    def create_role_if_not_exists(self, engine: Engine, role_name: str, privileges: List[str]):
        """Create database role with specific privileges."""
        with engine.connect() as conn:
            conn.execute(text("SET autocommit = ON"))
            
            # Check if role exists
            result = conn.execute(text("""
                SELECT 1 FROM pg_roles WHERE rolname = :role_name
            """), {"role_name": role_name})
            
            if not result.fetchone():
                # Create role
                conn.execute(text(f"CREATE ROLE {role_name}"))
                logger.info(f"Created role: {role_name}")
                
                # Grant privileges
                for privilege in privileges:
                    try:
                        conn.execute(text(f"GRANT {privilege} TO {role_name}"))
                        logger.info(f"Granted '{privilege}' to role {role_name}")
                    except Exception as e:
                        logger.warning(f"Could not grant '{privilege}' to {role_name}: {e}")
    
    def create_user(self, engine: Engine, user: DatabaseUser) -> bool:
        """Create database user with minimal privileges."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SET autocommit = ON"))
                
                # Check if user already exists
                result = conn.execute(text("""
                    SELECT 1 FROM pg_user WHERE usename = :username
                """), {"username": user.username})
                
                if result.fetchone():
                    logger.info(f"User {user.username} already exists, updating...")
                    return self.update_user(engine, user)
                
                # Create user
                create_sql = f"""
                    CREATE USER {user.username} 
                    WITH PASSWORD %s
                    CONNECTION LIMIT {user.connection_limit}
                """
                
                if user.valid_until:
                    create_sql += f" VALID UNTIL '{user.valid_until}'"
                
                # Use raw psycopg2 for password parameter
                raw_conn = psycopg2.connect(self.admin_connection_string)
                raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = raw_conn.cursor()
                
                cursor.execute(create_sql, (user.password,))
                logger.info(f"Created user: {user.username}")
                
                # Grant database connection
                cursor.execute(f"GRANT CONNECT ON DATABASE ainflue_production TO {user.username}")
                
                # Grant schema usage if specified
                if user.schemas:
                    for schema in user.schemas:
                        cursor.execute(f"GRANT USAGE ON SCHEMA {schema} TO {user.username}")
                
                # Grant table-specific privileges
                if user.role == "replication":
                    cursor.execute(f"ALTER USER {user.username} REPLICATION")
                else:
                    # Grant basic privileges
                    for privilege in user.privileges:
                        try:
                            if "ON" in privilege.upper():
                                cursor.execute(f"GRANT {privilege} TO {user.username}")
                            else:
                                # Handle non-table privileges
                                if privilege == "CONNECT":
                                    pass  # Already granted
                                else:
                                    cursor.execute(f"GRANT {privilege} TO {user.username}")
                        except Exception as e:
                            logger.warning(f"Could not grant '{privilege}' to {user.username}: {e}")
                
                # Create application-specific function for row-level security
                if user.username == "ainflue_app":
                    cursor.execute("""
                        CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
                        BEGIN
                            RETURN COALESCE(current_setting('app.current_user_id', true)::UUID, '00000000-0000-0000-0000-000000000000'::UUID);
                        END;
                        $$ LANGUAGE plpgsql SECURITY DEFINER;
                    """)
                    cursor.execute(f"GRANT EXECUTE ON FUNCTION current_user_id() TO {user.username}")
                
                cursor.close()
                raw_conn.close()
                
                logger.info(f"Successfully created user {user.username} with role {user.role}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create user {user.username}: {e}")
            return False
    
    def update_user(self, engine: Engine, user: DatabaseUser) -> bool:
        """Update existing user privileges."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SET autocommit = ON"))
                
                # Update connection limit
                conn.execute(text(f"""
                    ALTER USER {user.username} CONNECTION LIMIT {user.connection_limit}
                """))
                
                # Update password if provided
                if user.password:
                    raw_conn = psycopg2.connect(self.admin_connection_string)
                    raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    cursor = raw_conn.cursor()
                    cursor.execute(f"ALTER USER {user.username} PASSWORD %s", (user.password,))
                    cursor.close()
                    raw_conn.close()
                
                logger.info(f"Updated user: {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update user {user.username}: {e}")
            return False
    
    def create_all_users(self) -> Dict[str, bool]:
        """Create all service users."""
        results = {}
        
        engine = create_engine(self.admin_connection_string)
        
        try:
            # Create roles first
            roles = {
                "app_role": ["CONNECT", "USAGE ON SCHEMA public"],
                "readonly_role": ["CONNECT", "USAGE ON SCHEMA public"],
                "backup_role": ["CONNECT", "USAGE ON SCHEMA public"],
                "monitoring_role": ["CONNECT"],
                "service_role": ["CONNECT", "USAGE ON SCHEMA public"]
            }
            
            for role_name, privileges in roles.items():
                self.create_role_if_not_exists(engine, role_name, privileges)
            
            # Create users
            for user in self.users_config:
                success = self.create_user(engine, user)
                results[user.username] = success
            
            logger.info(f"User creation completed: {sum(results.values())}/{len(results)} successful")
            
        except Exception as e:
            logger.error(f"Failed to create users: {e}")
        finally:
            engine.dispose()
        
        return results
    
    def audit_user_privileges(self) -> Dict[str, Any]:
        """Audit current user privileges."""
        engine = create_engine(self.admin_connection_string)
        audit_results = {}
        
        try:
            with engine.connect() as conn:
                # Get all users and their privileges
                result = conn.execute(text("""
                    SELECT 
                        u.usename,
                        u.usesysid,
                        u.usecreatedb,
                        u.usesuper,
                        u.userepl,
                        u.usebypassrls,
                        u.valuntil,
                        u.useconfig
                    FROM pg_user u
                    WHERE u.usename NOT LIKE 'pg_%'
                    AND u.usename != 'postgres'
                    ORDER BY u.usename
                """))
                
                users = result.fetchall()
                
                for user_row in users:
                    username = user_row.usename
                    
                    # Get table privileges
                    table_privs = conn.execute(text("""
                        SELECT 
                            table_schema,
                            table_name,
                            privilege_type
                        FROM information_schema.table_privileges
                        WHERE grantee = :username
                        ORDER BY table_schema, table_name, privilege_type
                    """), {"username": username}).fetchall()
                    
                    # Get schema privileges
                    schema_privs = conn.execute(text("""
                        SELECT 
                            schema_name,
                            privilege_type
                        FROM information_schema.schema_privileges
                        WHERE grantee = :username
                        ORDER BY schema_name, privilege_type
                    """), {"username": username}).fetchall()
                    
                    audit_results[username] = {
                        "user_info": dict(user_row._mapping),
                        "table_privileges": [dict(row._mapping) for row in table_privs],
                        "schema_privileges": [dict(row._mapping) for row in schema_privs],
                        "is_superuser": user_row.usesuper,
                        "can_create_db": user_row.usecreatedb,
                        "can_replicate": user_row.userepl,
                        "bypass_rls": user_row.usebypassrls
                    }
        
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            
        finally:
            engine.dispose()
        
        return audit_results
    
    def export_user_credentials(self, output_file: str = "db_credentials.json"):
        """Export user credentials for deployment."""
        credentials = {}
        
        for user in self.users_config:
            credentials[user.username] = {
                "username": user.username,
                "password": user.password,
                "role": user.role,
                "description": user.description,
                "connection_limit": user.connection_limit
            }
        
        with open(output_file, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        logger.info(f"Credentials exported to {output_file}")
        
        # Also create environment file
        env_file = "production.env"
        with open(env_file, 'w') as f:
            f.write("# Production Database Credentials\n")
            f.write("# Generated on " + datetime.now().isoformat() + "\n\n")
            for user in self.users_config:
                env_var = f"POSTGRES_{user.role.upper()}_PASSWORD"
                f.write(f"{env_var}={user.password}\n")
        
        logger.info(f"Environment variables exported to {env_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Production Database User Management')
    parser.add_argument('action', choices=['create', 'update', 'audit', 'export'],
                       help='Action to perform')
    parser.add_argument('--output', help='Output file for export action')
    
    args = parser.parse_args()
    
    manager = ProductionUserManager()
    
    try:
        if args.action == 'create':
            results = manager.create_all_users()
            success_count = sum(1 for success in results.values() if success)
            print(f"Created {success_count}/{len(results)} users successfully")
            
        elif args.action == 'update':
            results = manager.create_all_users()  # This will update existing users
            success_count = sum(1 for success in results.values() if success)
            print(f"Updated {success_count}/{len(results)} users successfully")
            
        elif args.action == 'audit':
            audit_results = manager.audit_user_privileges()
            print(json.dumps(audit_results, indent=2, default=str))
            
        elif args.action == 'export':
            output_file = args.output or "db_credentials.json"
            manager.export_user_credentials(output_file)
            print(f"Credentials exported to {output_file}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"User management failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()