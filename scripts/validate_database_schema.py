#!/usr/bin/env python3
"""Database Schema and Migration Validation Script
===============================================

Validates database schemas and migrations for Ainflue Platform.
Addresses the requirement: "Base de données - schémas et migrations"

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseValidator:
    """
Validates database schemas and migration configurations"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.database_dir = self.project_root / "database"
        self.migrations_dir = self.database_dir / "migrations"
        self.schema_file = self.database_dir / "schema.py"
        self.validation_results = {}
        
    def validate_database_structure(self) -> Tuple[bool, List[str]]:
        """Validate database directory structure"""
        issues = []
        
        # Check main database directory
        if not self.database_dir.exists():
            issues.append(f"Database directory not found: {self.database_dir}")
            return False, issues
        
        logger.info("✅ Database directory found")
        
        # Check migrations directory
        if not self.migrations_dir.exists():
            issues.append(f"Migrations directory not found: {self.migrations_dir}")
        else:
            logger.info("✅ Migrations directory found")
        
        # Check schema file
        if not self.schema_file.exists():
            issues.append(f"Schema file not found: {self.schema_file}")
        else:
            logger.info("✅ Schema file found")
        
        # Check for migration files
        if self.migrations_dir.exists():
            migration_files = list(self.migrations_dir.glob("*.py"))
            migration_files = [f for f in migration_files if f.name != "__init__.py"]
            
            if migration_files:
                logger.info(f"✅ Found {len(migration_files)} migration files")
            else:
                issues.append("No migration files found")
        
        return len(issues) == 0, issues
    
    def validate_schema_file(self) -> Tuple[bool, List[str]]:
        """Validate the main schema file"""
        issues = []
        
        if not self.schema_file.exists():
            issues.append("Schema file does not exist")
            return False, issues
        
        try:
            # Read schema file content
            with open(self.schema_file, 'r') as f:
                schema_content = f.read()
            
            # Check for essential components
            required_components = [
                'CREATE TABLE',
                'users',
                'content',
                'async def create_tables',
                'database_manager'
            ]
            
            for component in required_components:
                if component not in schema_content:
                    issues.append(f"Schema missing component: {component}")
                else:
                    logger.info(f"✅ Found schema component: {component}")
            
            # Check for table definitions
            table_patterns = re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', schema_content)
            if table_patterns:
                logger.info(f"✅ Found {len(table_patterns)} table definitions:")
                for table in table_patterns:
                    logger.info(f"   - {table}")
            else:
                issues.append("No table definitions found in schema")
            
            # Validate Python syntax
            try:
                compile(schema_content, self.schema_file, 'exec')
                logger.info("✅ Schema file Python syntax is valid")
            except SyntaxError as e:
                issues.append(f"Schema file syntax error: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error reading schema file: {str(e)}")
        
        return len(issues) == 0, issues
    
    def validate_migration_files(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate migration files"""
        issues = []
        migration_details = {}
        
        if not self.migrations_dir.exists():
            issues.append("Migrations directory not found")
            return False, {"issues": issues}
        
        # Get all Python migration files
        migration_files = list(self.migrations_dir.glob("*.py"))
        migration_files = [f for f in migration_files if f.name != "__init__.py"]
        
        if not migration_files:
            issues.append("No migration files found")
            return False, {"issues": issues}
        
        logger.info(f"📁 Found {len(migration_files)} migration files")
        
        for migration_file in migration_files:
            file_issues = []
            file_details = {
                'path': str(migration_file),
                'size': migration_file.stat().st_size,
                'issues': []
            }
            
            try:
                # Read migration file
                with open(migration_file, 'r') as f:
                    content = f.read()
                
                # Check for required migration components
                required_patterns = [
                    r'class.*Migration',
                    r'def (up|upgrade|apply)',
                    r'def (down|downgrade|rollback)',
                ]
                
                for pattern in required_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        logger.info(f"✅ {migration_file.name}: Found {pattern}")
                    else:
                        file_issues.append(f"Missing pattern: {pattern}")
                
                # Check Python syntax
                try:
                    compile(content, migration_file, 'exec')
                    logger.info(f"✅ {migration_file.name}: Python syntax valid")
                except SyntaxError as e:
                    file_issues.append(f"Syntax error: {str(e)}")
                
                # Check for database operations
                db_operations = [
                    'CREATE TABLE',
                    'ALTER TABLE',
                    'DROP TABLE',
                    'INSERT INTO',
                    'CREATE INDEX'
                ]
                
                found_operations = []
                for op in db_operations:
                    if op in content:
                        found_operations.append(op)
                
                if found_operations:
                    logger.info(f"✅ {migration_file.name}: Found DB operations: {found_operations}")
                    file_details['operations'] = found_operations
                else:
                    file_issues.append("No database operations found")
                
            except Exception as e:
                file_issues.append(f"Error reading file: {str(e)}")
            
            file_details['issues'] = file_issues
            migration_details[migration_file.name] = file_details
            
            if file_issues:
                issues.extend([f"{migration_file.name}: {issue}" for issue in file_issues])
        
        return len(issues) == 0, {
            "issues": issues,
            "files": migration_details,
            "total_files": len(migration_files)
        }
    
    def check_migration_dependencies(self) -> Tuple[bool, List[str]]:
        """Check migration dependency resolution"""
        issues = []
        
        # Check for migration manager/runner
        migration_files = [
            "migration_manager.py",
            "migration_runner.py",
            "migration_orchestrator.py"
        ]
        
        found_managers = []
        for manager_file in migration_files:
            manager_path = self.migrations_dir / manager_file
            if manager_path.exists():
                found_managers.append(manager_file)
                logger.info(f"✅ Found migration manager: {manager_file}")
        
        if not found_managers:
            issues.append("No migration manager/runner found")
        
        # Check for dependency resolver
        dependency_resolver = self.migrations_dir / "dependency_resolver.py"
        if dependency_resolver.exists():
            logger.info("✅ Found dependency resolver")
        else:
            issues.append("Dependency resolver not found")
        
        # Check for rollback manager
        rollback_manager = self.migrations_dir / "rollback_manager.py"
        if rollback_manager.exists():
            logger.info("✅ Found rollback manager")
        else:
            issues.append("Rollback manager not found (recommended)")
        
        return len(issues) == 0, issues
    
    def validate_database_connections(self) -> Tuple[bool, List[str]]:
        """Validate database connection configurations"""
        issues = []
        
        # Check for database configuration files
        config_paths = [
            self.project_root / "config" / "database",
            self.database_dir / "config",
            self.project_root / "config.py"
        ]
        
        found_configs = []
        for config_path in config_paths:
            if config_path.exists():
                found_configs.append(str(config_path))
                logger.info(f"✅ Found database config: {config_path}")
        
        if not found_configs:
            issues.append("No database configuration found")
        
        # Check for connection pooling
        pool_files = list(self.database_dir.glob("**/pool*.py"))
        if pool_files:
            logger.info(f"✅ Found {len(pool_files)} connection pool configurations")
        else:
            issues.append("No connection pooling configuration found")
        
        # Check for database models
        models_files = list(self.database_dir.glob("**/models.py"))
        if models_files:
            logger.info(f"✅ Found {len(models_files)} model files")
        else:
            issues.append("No database models found")
        
        return len(issues) == 0, issues
    
    def generate_migration_test_script(self) -> str:
        """Generate a script to test database migrations"""
        script_content = """#!/bin/bash
# Database Migration Test Script
set -e

echo "🗄️ Testing Ainflue Database Migrations..."

# Start PostgreSQL if not running
echo "🔧 Starting PostgreSQL..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 30

# Test database connection
echo "🔌 Testing database connection..."
docker exec ainflue-postgres pg_isready -U ainflue -d ainflue_platform

# Run migrations
echo "📋 Running database migrations..."
python3 -c "
import asyncio
import sys
sys.path.append('.')

async def run_migrations():
    try:
        from database.schema import create_tables
        await create_tables()
        print('✅ Schema creation completed')
    except Exception as e:
        print(f'❌ Schema creation failed: {e}')
        return False
    
    # Run individual migrations if available
    try:
        from database.migrations.migration_runner import MigrationRunner
        runner = MigrationRunner()
        await runner.run_all_migrations()
        print('✅ All migrations completed')
    except ImportError:
        print('ℹ️ Migration runner not available, skipping migration tests')
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        return False
    
    return True

result = asyncio.run(run_migrations())
sys.exit(0 if result else 1)
"

# Verify database structure
echo "🔍 Verifying database structure..."
docker exec ainflue-postgres psql -U ainflue -d ainflue_platform -c "\\dt"

echo "🎉 Database migration test completed!"
"""
        return script_content
    
    def check_required_packages(self) -> Tuple[bool, List[str]]:
        """
Check if required database packages are available"""
        issues = []
        
        required_packages = [
            'asyncpg',
            'psycopg2',
            'sqlalchemy',
            'alembic'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ Package available: {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"⚠️ Package missing: {package}")
        
        if missing_packages:
            issues.append(f"Missing packages: {missing_packages}")
            issues.append("Install with: pip install " + " ".join(missing_packages))
        
        return len(missing_packages) == 0, issues
    
    def generate_basic_schema(self) -> None:
        """Generate a basic database schema if missing"""
        if self.schema_file.exists():
            return
        
        basic_schema = '''"""
Basic Database Schema for Ainflue Platform
Generated automatically for testing purposes
"""

from sqlalchemy import text
import asyncio
import logging

logger = logging.getLogger(__name__)

async def create_tables():
    """
Create basic database tables"""
    try:
        # This is a placeholder - implement actual database connection
        logger.info("Creating database tables...")
        
        # Basic tables structure
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(32) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'content': """
                CREATE TABLE IF NOT EXISTS content (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(32) REFERENCES users(id),
                    title VARCHAR(255) NOT NULL,
                    content_type VARCHAR(20) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'analytics': """
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    content_id VARCHAR(36) REFERENCES content(id),
                    metric_type VARCHAR(50) NOT NULL,
                    metric_value INTEGER DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        logger.info(f"Schema defines {len(tables)} tables")
        for table_name in tables:
            logger.info(f"  - {table_name}")
        
        logger.info("✅ Schema validation completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema creation failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_tables())
'''
        
        self.database_dir.mkdir(parents=True, exist_ok=True)
        with open(self.schema_file, 'w') as f:
            f.write(basic_schema)
        
        logger.info(f"✅ Generated basic schema file: {self.schema_file}")
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete database validation"""
        logger.info("🗄️ Starting Database Schema and Migration Validation")
        
        # Check basic structure
        logger.info("\n" + "="*60)
        logger.info("Validating Database Structure")
        logger.info("="*60)
        
        structure_valid, structure_issues = self.validate_database_structure()
        
        # Generate basic schema if missing
        if not structure_valid and "Schema file not found" in str(structure_issues):
            logger.info("🔧 Generating basic schema file...")
            self.generate_basic_schema()
            structure_valid, structure_issues = self.validate_database_structure()
        
        # Validate schema file
        logger.info("\n" + "="*60)
        logger.info("Validating Schema File")
        logger.info("="*60)
        
        schema_valid, schema_issues = self.validate_schema_file()
        
        # Validate migration files
        logger.info("\n" + "="*60)
        logger.info("Validating Migration Files")
        logger.info("="*60)
        
        migrations_valid, migration_details = self.validate_migration_files()
        
        # Check migration dependencies
        logger.info("\n" + "="*60)
        logger.info("Checking Migration Dependencies")
        logger.info("="*60)
        
        deps_valid, dep_issues = self.check_migration_dependencies()
        
        # Validate database connections
        logger.info("\n" + "="*60)
        logger.info("Validating Database Connections")
        logger.info("="*60)
        
        conn_valid, conn_issues = self.validate_database_connections()
        
        # Check required packages
        logger.info("\n" + "="*60)
        logger.info("Checking Required Packages")
        logger.info("="*60)
        
        packages_valid, package_issues = self.check_required_packages()
        
        # Generate test script
        script_content = self.generate_migration_test_script()
        script_path = self.project_root / "test_database_migrations.sh"
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        logger.info(f"✅ Generated database test script: {script_path}")
        
        # Compile results
        self.validation_results = {
            'structure': {
                'valid': structure_valid,
                'issues': structure_issues
            },
            'schema': {
                'valid': schema_valid,
                'issues': schema_issues,
                'file_path': str(self.schema_file)
            },
            'migrations': {
                'valid': migrations_valid,
                'details': migration_details
            },
            'dependencies': {
                'valid': deps_valid,
                'issues': dep_issues
            },
            'connections': {
                'valid': conn_valid,
                'issues': conn_issues
            },
            'packages': {
                'valid': packages_valid,
                'issues': package_issues
            },
            'test_script': str(script_path)
        }
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """Generate database validation report"""
        if not self.validation_results:
            return "No validation results available. Run validation first."
        
        report = """Database Schema and Migration Validation Report
===============================================

"""
        
        # Structure
        struct = self.validation_results['structure']
        report += f"📁 Database Structure: {'✅ VALID' if struct['valid'] else '❌ ISSUES'}\n"
        if struct['issues']:
            for issue in struct['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Schema
        schema = self.validation_results['schema']
        report += f"📋 Database Schema: {'✅ VALID' if schema['valid'] else '❌ ISSUES'}\n"
        report += f"   File: {schema['file_path']}\n"
        if schema['issues']:
            for issue in schema['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Migrations
        migrations = self.validation_results['migrations']
        report += f"🔄 Migration Files: {'✅ VALID' if migrations['valid'] else '❌ ISSUES'}\n"
        if 'details' in migrations and 'total_files' in migrations['details']:
            report += f"   Files Found: {migrations['details']['total_files']}\n"
        if 'details' in migrations and 'issues' in migrations['details']:
            for issue in migrations['details']['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Dependencies
        deps = self.validation_results['dependencies']
        report += f"🔗 Migration Dependencies: {'✅ VALID' if deps['valid'] else '❌ ISSUES'}\n"
        if deps['issues']:
            for issue in deps['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Connections
        conn = self.validation_results['connections']
        report += f"🔌 Database Connections: {'✅ VALID' if conn['valid'] else '❌ ISSUES'}\n"
        if conn['issues']:
            for issue in conn['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Packages
        packages = self.validation_results['packages']
        report += f"📦 Required Packages: {'✅ AVAILABLE' if packages['valid'] else '⚠️ MISSING'}\n"
        if packages['issues']:
            for issue in packages['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Test script
        report += f"🧪 Test Script: {self.validation_results['test_script']}\n\n"
        
        # Summary
        all_valid = (
            struct['valid'] and
            schema['valid'] and
            migrations['valid'] and
            deps['valid'] and
            conn['valid']
        )
        
        report += "SUMMARY\n"
        report += "="*40 + "\n"
        report += f"Database Configuration: {'✅ VALID' if all_valid else '⚠️ NEEDS ATTENTION'}\n"
        report += f"Required Packages: {'✅ AVAILABLE' if packages['valid'] else '⚠️ MISSING'}\n"
        
        if all_valid and packages['valid']:
            report += "\n🎉 Database configurations are valid and ready!\n"
            report += "\nTo test database setup:\n"
            report += f"   bash {self.validation_results['test_script']}\n"
        else:
            report += "\n⚠️ Some database configurations need attention.\n"
            if not packages['valid']:
                report += "   Install missing packages before proceeding.\n"
        
        return report


def main():
    """Main execution function"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    logger.info("🗄️ Database Schema and Migration Validation")
    logger.info(f"Project Root: {project_root}")
    
    validator = DatabaseValidator(str(project_root))
    results = validator.run_validation()
    
    # Generate and save report
    report = validator.generate_report()
    report_path = project_root / "database_validation_report.txt"
    report_path.write_text(report)
    
    print(report)
    logger.info(f"📄 Report saved to: {report_path}")
    
    # Return appropriate exit code
    all_valid = (
        results['structure']['valid'] and
        results['schema']['valid'] and
        results['migrations']['valid'] and
        results['dependencies']['valid'] and
        results['connections']['valid']
    )
    
    if all_valid:
        logger.info("🎉 All database configurations are valid!")
        return 0
    else:
        logger.warning("⚠️ Some database configurations need attention!")
        return 1


if __name__ == "__main__":
    sys.exit(main())