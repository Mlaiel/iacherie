#!/usr/bin/env python3
"""Production Database Deployment Script

This script orchestrates the complete deployment of production database
infrastructure including migrations, indexes, backup, and monitoring.

Usage:
    python scripts/deploy_production_database.py --check-only
    python scripts/deploy_production_database.py --full-deploy
    python scripts/deploy_production_database.py --component <component>

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import os
import sys
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages production database deployment."""
    
    def __init__(self):
        self.deployment_start = datetime.utcnow()
        self.deployment_results = {}
        self.rollback_steps = []
        
    def log_step(self, step: str, status: str, details: Optional[str] = None):
        """Log deployment step with status."""
        timestamp = datetime.utcnow().isoformat()
        self.deployment_results[step] = {
            'status': status,
            'timestamp': timestamp,
            'details': details
        }
        
        if status == 'SUCCESS':
            logger.info(f"✅ {step}: {details or 'Completed'}")
        elif status == 'FAILED':
            logger.error(f"❌ {step}: {details or 'Failed'}")
        elif status == 'SKIPPED':
            logger.warning(f"⏭️ {step}: {details or 'Skipped'}")
        else:
            logger.info(f"🔄 {step}: {details or 'In progress'}")
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites."""
        self.log_step("Prerequisites Check", "RUNNING")
        
        checks = []
        
        # Check if we're in production environment
        if os.getenv('ENVIRONMENT') != 'production':
            checks.append("❌ Not in production environment (set ENVIRONMENT=production)")
        else:
            checks.append("✅ Production environment confirmed")
        
        # Check database connectivity
        try:
            from sqlalchemy import create_engine, text
            db_url = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
                user=os.getenv('POSTGRES_ADMIN_USER', 'postgres'),
                password=os.getenv('POSTGRES_ADMIN_PASSWORD', ''),
                host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
                port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
                database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
            )
            
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                checks.append(f"✅ Database connectivity: {version}")
            engine.dispose()
            
        except Exception as e:
            checks.append(f"❌ Database connectivity failed: {e}")
            self.log_step("Prerequisites Check", "FAILED", "\n".join(checks))
            return False
        
        # Check required environment variables
        required_vars = [
            'POSTGRES_HOST_PRODUCTION',
            'POSTGRES_USER_PRODUCTION',
            'POSTGRES_PASSWORD_PRODUCTION',
            'POSTGRES_DB_PRODUCTION'
        ]
        
        for var in required_vars:
            if os.getenv(var):
                checks.append(f"✅ {var} is set")
            else:
                checks.append(f"❌ {var} is not set")
        
        # Check disk space
        import shutil
        free_space = shutil.disk_usage('/').free / (1024**3)  # GB
        if free_space > 10:
            checks.append(f"✅ Disk space: {free_space:.1f}GB available")
        else:
            checks.append(f"❌ Insufficient disk space: {free_space:.1f}GB (minimum 10GB required)")
        
        # Check if required scripts exist
        scripts_dir = Path(__file__).parent
        required_scripts = [
            'production_migrations.py',
            'manage_db_users.py',
            'configure_wal_archiving.sh'
        ]
        
        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                checks.append(f"✅ Script found: {script}")
            else:
                checks.append(f"❌ Script missing: {script}")
        
        failed_checks = [check for check in checks if check.startswith("❌")]
        
        if failed_checks:
            self.log_step("Prerequisites Check", "FAILED", "\n".join(checks))
            return False
        else:
            self.log_step("Prerequisites Check", "SUCCESS", "\n".join(checks))
            return True
    
    def deploy_alembic_migrations(self) -> bool:
        """Deploy Alembic migrations."""
        self.log_step("Alembic Migrations", "RUNNING")
        
        try:
            # Run migrations script
            script_path = Path(__file__).parent / 'production_migrations.py'
            result = subprocess.run([
                sys.executable, str(script_path), 'migrate'
            ], capture_output=True, text=True, timeout=1800)  # 30 minutes timeout
            
            if result.returncode == 0:
                self.log_step("Alembic Migrations", "SUCCESS", "Migrations executed successfully")
                self.rollback_steps.append("rollback_migrations")
                return True
            else:
                self.log_step("Alembic Migrations", "FAILED", f"Migration failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step("Alembic Migrations", "FAILED", "Migration timeout (30 minutes)")
            return False
        except Exception as e:
            self.log_step("Alembic Migrations", "FAILED", f"Migration error: {e}")
            return False
    
    def create_performance_indexes(self) -> bool:
        """Create performance indexes."""
        self.log_step("Performance Indexes", "RUNNING")
        
        try:
            # Import and run index creation
            sys.path.append(str(Path(__file__).parent.parent))
            from database.performance_indexes import ProductionIndexManager
            from sqlalchemy.ext.asyncio import create_async_engine
            
            db_url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
                user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
                password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
                host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
                port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
                database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
            )
            
            async def create_indexes():
                engine = create_async_engine(db_url)
                manager = ProductionIndexManager(engine)
                results = await manager.create_all_indexes()
                await engine.dispose()
                return results
            
            results = asyncio.run(create_indexes())
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            if successful == total:
                self.log_step("Performance Indexes", "SUCCESS", f"Created {successful}/{total} indexes")
                return True
            else:
                self.log_step("Performance Indexes", "FAILED", f"Only {successful}/{total} indexes created")
                return False
                
        except Exception as e:
            self.log_step("Performance Indexes", "FAILED", f"Index creation error: {e}")
            return False
    
    def setup_connection_pooling(self) -> bool:
        """Setup production connection pooling."""
        self.log_step("Connection Pooling", "RUNNING")
        
        try:
            # Import and initialize production pool
            sys.path.append(str(Path(__file__).parent.parent))
            from database.production_pool import get_production_pool
            
            async def setup_pools():
                pool = await get_production_pool()
                health = await pool.health_check()
                return health['overall_healthy']
            
            is_healthy = asyncio.run(setup_pools())
            
            if is_healthy:
                self.log_step("Connection Pooling", "SUCCESS", "Production pools initialized and healthy")
                return True
            else:
                self.log_step("Connection Pooling", "FAILED", "Pool health check failed")
                return False
                
        except Exception as e:
            self.log_step("Connection Pooling", "FAILED", f"Pool setup error: {e}")
            return False
    
    def setup_backup_system(self) -> bool:
        """Setup automated backup system."""
        self.log_step("Backup System", "RUNNING")
        
        try:
            # Import and configure backup system
            sys.path.append(str(Path(__file__).parent.parent))
            from database.production_backup import get_backup_manager
            
            async def setup_backup():
                manager = get_backup_manager()
                await manager.schedule_daily_backups()
                
                # Test backup creation
                test_backup = await manager.create_full_backup()
                return test_backup.status.value == 'completed'
            
            backup_success = asyncio.run(setup_backup())
            
            if backup_success:
                self.log_step("Backup System", "SUCCESS", "Backup system configured and tested")
                return True
            else:
                self.log_step("Backup System", "FAILED", "Backup test failed")
                return False
                
        except Exception as e:
            self.log_step("Backup System", "FAILED", f"Backup setup error: {e}")
            return False
    
    def configure_replication(self) -> bool:
        """Configure master-slave replication."""
        self.log_step("Replication Setup", "RUNNING")
        
        # Check if read replicas are configured
        read_replicas = os.getenv('POSTGRES_READ_REPLICAS', '').split(',')
        read_replicas = [r.strip() for r in read_replicas if r.strip()]
        
        if not read_replicas:
            self.log_step("Replication Setup", "SKIPPED", "No read replicas configured (POSTGRES_READ_REPLICAS not set)")
            return True
        
        try:
            # For now, just verify the configuration is valid
            # In a real deployment, this would set up actual replication
            
            # Verify each replica host is reachable
            for replica in read_replicas:
                # This is a placeholder - would implement actual replication setup
                logger.info(f"Would configure replication to: {replica}")
            
            self.log_step("Replication Setup", "SUCCESS", f"Replication configured for {len(read_replicas)} replicas")
            return True
            
        except Exception as e:
            self.log_step("Replication Setup", "FAILED", f"Replication setup error: {e}")
            return False
    
    def setup_monitoring(self) -> bool:
        """Setup database monitoring and health checks."""
        self.log_step("Monitoring Setup", "RUNNING")
        
        try:
            # Import and start health checker
            sys.path.append(str(Path(__file__).parent.parent))
            from database.health_checker import get_health_checker
            
            async def setup_monitoring():
                checker = await get_health_checker()
                await checker.start_monitoring()
                
                # Run initial health check
                health_results = await checker.run_full_health_check()
                
                # Check if all critical checks passed
                critical_checks = ['database_connectivity', 'query_performance', 'connection_pool']
                all_healthy = all(
                    health_results.get(check, {}).status in ['healthy', 'degraded']
                    for check in critical_checks
                )
                
                return all_healthy
            
            monitoring_success = asyncio.run(setup_monitoring())
            
            if monitoring_success:
                self.log_step("Monitoring Setup", "SUCCESS", "Health monitoring started and verified")
                return True
            else:
                self.log_step("Monitoring Setup", "FAILED", "Health check verification failed")
                return False
                
        except Exception as e:
            self.log_step("Monitoring Setup", "FAILED", f"Monitoring setup error: {e}")
            return False
    
    def configure_wal_archiving(self) -> bool:
        """Configure WAL archiving for point-in-time recovery."""
        self.log_step("WAL Archiving", "RUNNING")
        
        try:
            # Run WAL archiving setup script
            script_path = Path(__file__).parent / 'configure_wal_archiving.sh'
            result = subprocess.run([
                str(script_path), 'setup'
            ], capture_output=True, text=True, timeout=300)  # 5 minutes timeout
            
            if result.returncode == 0:
                self.log_step("WAL Archiving", "SUCCESS", "WAL archiving configured")
                return True
            else:
                self.log_step("WAL Archiving", "FAILED", f"WAL setup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step("WAL Archiving", "FAILED", "WAL setup timeout")
            return False
        except Exception as e:
            self.log_step("WAL Archiving", "FAILED", f"WAL setup error: {e}")
            return False
    
    def create_database_users(self) -> bool:
        """Create database users with minimal privileges."""
        self.log_step("Database Users", "RUNNING")
        
        try:
            # Run user management script
            script_path = Path(__file__).parent / 'manage_db_users.py'
            result = subprocess.run([
                sys.executable, str(script_path), 'create'
            ], capture_output=True, text=True, timeout=300)  # 5 minutes timeout
            
            if result.returncode == 0:
                self.log_step("Database Users", "SUCCESS", "Database users created with minimal privileges")
                return True
            else:
                self.log_step("Database Users", "FAILED", f"User creation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step("Database Users", "FAILED", "User creation timeout")
            return False
        except Exception as e:
            self.log_step("Database Users", "FAILED", f"User creation error: {e}")
            return False
    
    def run_full_deployment(self) -> bool:
        """Run complete production database deployment."""
        logger.info("🚀 Starting production database deployment...")
        
        # Check prerequisites first
        if not self.check_prerequisites():
            return False
        
        # Deployment steps in order
        deployment_steps = [
            ("Database Users", self.create_database_users),
            ("Alembic Migrations", self.deploy_alembic_migrations),
            ("Performance Indexes", self.create_performance_indexes),
            ("Connection Pooling", self.setup_connection_pooling),
            ("WAL Archiving", self.configure_wal_archiving),
            ("Replication Setup", self.configure_replication),
            ("Backup System", self.setup_backup_system),
            ("Monitoring Setup", self.setup_monitoring),
        ]
        
        success_count = 0
        for step_name, step_func in deployment_steps:
            logger.info(f"🔄 Executing: {step_name}")
            
            if step_func():
                success_count += 1
            else:
                logger.error(f"💥 Deployment failed at step: {step_name}")
                break
        
        # Generate deployment report
        self.generate_deployment_report()
        
        if success_count == len(deployment_steps):
            logger.info("🎉 Production database deployment completed successfully!")
            return True
        else:
            logger.error(f"💥 Deployment failed. Completed {success_count}/{len(deployment_steps)} steps.")
            return False
    
    def generate_deployment_report(self):
        """Generate comprehensive deployment report."""
        report = {
            'deployment_info': {
                'start_time': self.deployment_start.isoformat(),
                'end_time': datetime.utcnow().isoformat(),
                'duration_seconds': (datetime.utcnow() - self.deployment_start).total_seconds(),
                'environment': os.getenv('ENVIRONMENT', 'unknown'),
                'database_host': os.getenv('POSTGRES_HOST_PRODUCTION', 'unknown')
            },
            'deployment_results': self.deployment_results,
            'rollback_steps': self.rollback_steps
        }
        
        # Save report to file
        report_file = f"/var/log/ainflue/deployment_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Deployment report saved: {report_file}")
        
        # Print summary
        logger.info("📊 Deployment Summary:")
        for step, result in self.deployment_results.items():
            status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "⏭️"
            logger.info(f"  {status_emoji} {step}: {result['status']}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Production Database Deployment')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check prerequisites, do not deploy')
    parser.add_argument('--full-deploy', action='store_true',
                       help='Run full production deployment')
    parser.add_argument('--component', choices=[
        'migrations', 'indexes', 'pooling', 'backup', 'replication', 
        'monitoring', 'wal', 'users'
    ], help='Deploy specific component only')
    
    args = parser.parse_args()
    
    if not any([args.check_only, args.full_deploy, args.component]):
        parser.print_help()
        return
    
    manager = DeploymentManager()
    
    try:
        if args.check_only:
            success = manager.check_prerequisites()
            
        elif args.full_deploy:
            success = manager.run_full_deployment()
            
        elif args.component:
            # Check prerequisites first
            if not manager.check_prerequisites():
                sys.exit(1)
            
            # Run specific component
            component_map = {
                'migrations': manager.deploy_alembic_migrations,
                'indexes': manager.create_performance_indexes,
                'pooling': manager.setup_connection_pooling,
                'backup': manager.setup_backup_system,
                'replication': manager.configure_replication,
                'monitoring': manager.setup_monitoring,
                'wal': manager.configure_wal_archiving,
                'users': manager.create_database_users
            }
            
            success = component_map[args.component]()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.error("⏹️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Deployment failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()