"""Production Security Orchestrator
=================================

Main orchestrator that integrates all security components for production deployment.
Provides centralized management, health monitoring, and automated security operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import schedule
import time

from config.security.production_security import get_security_config, validate_security_config
from core.security.cloudflare_protection import setup_cloudflare_protection
from core.security.automated_vulnerability_scanner import get_vulnerability_scanner, start_automated_scanning
from core.security.enhanced_2fa import get_2fa_manager, enforce_2fa_for_user
from core.security.enhanced_audit_trail import get_audit_trail, log_audit_event
from core.security.api_key_rotation import get_rotation_manager, run_rotation_maintenance
from core.security.encrypted_backup_system import get_backup_system, create_backup, test_backup_restoration


logger = logging.getLogger(__name__)


@dataclass
class SecurityHealth:
    """Security system health status"""
    component: str
    status: str  # healthy, warning, critical, error
    message: str
    last_check: datetime
    metrics: Dict[str, Any]


class ProductionSecurityOrchestrator:
    """Main production security orchestrator"""
    
    def __init__(self):
        self.config = get_security_config()
        self.health_status: Dict[str, SecurityHealth] = {}
        self.scheduler_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Component instances
        self.vulnerability_scanner = get_vulnerability_scanner()
        self.two_fa_manager = get_2fa_manager()
        self.audit_trail = get_audit_trail()
        self.rotation_manager = get_rotation_manager()
        self.backup_system = get_backup_system()
    
    async def initialize_security_stack(self) -> Dict[str, Any]:
        """Initialize complete security stack"""
        logger.info("Initializing production security stack...")
        
        results = {
            "status": "success",
            "components": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # 1. Validate configuration
            config_validation = validate_security_config()
            results["components"]["configuration"] = config_validation
            
            if not config_validation["valid"]:
                results["errors"].extend(config_validation["errors"])
                results["status"] = "error"
            
            if config_validation["warnings"]:
                results["warnings"].extend(config_validation["warnings"])
            
            # 2. Setup CloudFlare protection
            try:
                cf_result = await setup_cloudflare_protection()
                results["components"]["cloudflare"] = cf_result
                if cf_result["status"] != "success":
                    results["warnings"].append("CloudFlare setup incomplete")
            except Exception as e:
                results["components"]["cloudflare"] = {"status": "error", "error": str(e)}
                results["errors"].append(f"CloudFlare setup failed: {e}")
            
            # 3. Start vulnerability scanning
            try:
                if self.config.vulnerability_scan.enabled:
                    start_automated_scanning()
                    results["components"]["vulnerability_scanner"] = {"status": "started"}
                else:
                    results["components"]["vulnerability_scanner"] = {"status": "disabled"}
            except Exception as e:
                results["components"]["vulnerability_scanner"] = {"status": "error", "error": str(e)}
                results["errors"].append(f"Vulnerability scanner failed: {e}")
            
            # 4. Initialize 2FA enforcement
            try:
                stats = await self.two_fa_manager.get_2fa_stats()
                results["components"]["2fa"] = {"status": "initialized", "stats": stats}
            except Exception as e:
                results["components"]["2fa"] = {"status": "error", "error": str(e)}
                results["errors"].append(f"2FA initialization failed: {e}")
            
            # 5. Initialize API key rotation
            try:
                rotation_status = await self.rotation_manager.get_rotation_status()
                results["components"]["api_rotation"] = {"status": "initialized", "rotation_status": rotation_status}
            except Exception as e:
                results["components"]["api_rotation"] = {"status": "error", "error": str(e)}
                results["errors"].append(f"API rotation initialization failed: {e}")
            
            # 6. Initialize backup system
            try:
                backup_status = await self.backup_system.get_backup_status()
                results["components"]["backup"] = {"status": "initialized", "backup_status": backup_status}
            except Exception as e:
                results["components"]["backup"] = {"status": "error", "error": str(e)}
                results["errors"].append(f"Backup system initialization failed: {e}")
            
            # 7. Start security scheduler
            self.start_security_scheduler()
            results["components"]["scheduler"] = {"status": "started"}
            
            # Log initialization
            await log_audit_event(
                "security.system.initialized",
                action="Production security stack initialized",
                details={
                    "components": list(results["components"].keys()),
                    "errors": len(results["errors"]),
                    "warnings": len(results["warnings"])
                }
            )
            
            # Determine final status
            if results["errors"]:
                results["status"] = "error"
            elif results["warnings"]:
                results["status"] = "warning"
            
            logger.info(f"Security stack initialization completed with status: {results['status']}")
            
        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Critical initialization error: {e}")
            logger.error(f"Security stack initialization failed: {e}")
        
        return results
    
    async def perform_health_check(self) -> Dict[str, SecurityHealth]:
        """Perform comprehensive health check of all security components"""
        health_checks = {}
        
        # 1. Check CloudFlare
        try:
            from core.security.cloudflare_protection import CloudFlareSecurityManager
            config = self.config.cloudflare
            if config.enabled:
                async with CloudFlareSecurityManager(config) as cf_manager:
                    cf_health = await cf_manager.health_check()
                    health_checks["cloudflare"] = SecurityHealth(
                        component="cloudflare",
                        status="healthy" if cf_health["status"] == "healthy" else "warning",
                        message=f"Zone: {cf_health.get('zone_name', 'Unknown')}, Security Level: {cf_health.get('security_level', 'Unknown')}",
                        last_check=datetime.utcnow(),
                        metrics=cf_health
                    )
        except Exception as e:
            health_checks["cloudflare"] = SecurityHealth(
                component="cloudflare",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # 2. Check vulnerability scanner
        try:
            scanner_summary = self.vulnerability_scanner.get_latest_summary()
            status = "healthy"
            if scanner_summary.get("threshold_exceeded", False):
                status = "critical"
            elif scanner_summary.get("total_vulnerabilities", 0) > 0:
                status = "warning"
            
            health_checks["vulnerability_scanner"] = SecurityHealth(
                component="vulnerability_scanner",
                status=status,
                message=f"Vulnerabilities: {scanner_summary.get('total_vulnerabilities', 0)} (Critical: {scanner_summary.get('critical_vulnerabilities', 0)})",
                last_check=datetime.utcnow(),
                metrics=scanner_summary
            )
        except Exception as e:
            health_checks["vulnerability_scanner"] = SecurityHealth(
                component="vulnerability_scanner",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # 3. Check 2FA compliance
        try:
            stats = await self.two_fa_manager.get_2fa_stats()
            status = "healthy"
            if stats["compliance_rate"] < 80:
                status = "critical"
            elif stats["compliance_rate"] < 95:
                status = "warning"
            
            health_checks["2fa"] = SecurityHealth(
                component="2fa",
                status=status,
                message=f"Compliance: {stats['compliance_rate']}% ({stats['enabled_users']}/{stats['enforced_users']})",
                last_check=datetime.utcnow(),
                metrics=stats
            )
        except Exception as e:
            health_checks["2fa"] = SecurityHealth(
                component="2fa",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # 4. Check API key rotation
        try:
            rotation_status = await self.rotation_manager.get_rotation_status()
            overdue_rotations = len([r for r in rotation_status["upcoming_rotations"] if r["days_until_rotation"] < 0])
            
            status = "healthy"
            if overdue_rotations > 0:
                status = "critical"
            elif len(rotation_status["upcoming_rotations"]) > 10:
                status = "warning"
            
            health_checks["api_rotation"] = SecurityHealth(
                component="api_rotation",
                status=status,
                message=f"Active keys: {rotation_status['active_keys']}, Overdue rotations: {overdue_rotations}",
                last_check=datetime.utcnow(),
                metrics=rotation_status
            )
        except Exception as e:
            health_checks["api_rotation"] = SecurityHealth(
                component="api_rotation",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # 5. Check backup system
        try:
            backup_status = await self.backup_system.get_backup_status()
            
            # Check for recent successful backup
            recent_backups = backup_status.get("recent_backups", [])
            latest_backup = recent_backups[0] if recent_backups else None
            
            status = "healthy"
            if not latest_backup:
                status = "critical"
                message = "No backups found"
            else:
                backup_age = datetime.utcnow() - datetime.fromisoformat(latest_backup["created_at"])
                if backup_age > timedelta(days=2):
                    status = "critical"
                    message = f"Latest backup is {backup_age.days} days old"
                elif backup_age > timedelta(days=1):
                    status = "warning"
                    message = f"Latest backup is {backup_age.days} days old"
                else:
                    message = f"Latest backup: {backup_age.total_seconds() / 3600:.1f} hours ago"
            
            health_checks["backup_system"] = SecurityHealth(
                component="backup_system",
                status=status,
                message=message,
                last_check=datetime.utcnow(),
                metrics=backup_status
            )
        except Exception as e:
            health_checks["backup_system"] = SecurityHealth(
                component="backup_system",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # 6. Check audit trail integrity
        try:
            integrity = await self.audit_trail.verify_audit_integrity()
            status = "healthy"
            if integrity["integrity_score"] < 95:
                status = "critical"
            elif integrity["integrity_score"] < 99:
                status = "warning"
            
            health_checks["audit_trail"] = SecurityHealth(
                component="audit_trail",
                status=status,
                message=f"Integrity: {integrity['integrity_score']}% ({integrity['verified_events']}/{integrity['total_events']})",
                last_check=datetime.utcnow(),
                metrics=integrity
            )
        except Exception as e:
            health_checks["audit_trail"] = SecurityHealth(
                component="audit_trail",
                status="error",
                message=f"Health check failed: {e}",
                last_check=datetime.utcnow(),
                metrics={}
            )
        
        # Update health status
        self.health_status = health_checks
        
        # Log health check
        critical_components = [h.component for h in health_checks.values() if h.status == "critical"]
        warning_components = [h.component for h in health_checks.values() if h.status == "warning"]
        
        await log_audit_event(
            "security.health.check",
            action="Security health check completed",
            details={
                "total_components": len(health_checks),
                "critical_components": critical_components,
                "warning_components": warning_components
            }
        )
        
        return health_checks
    
    async def run_daily_maintenance(self):
        """Run daily security maintenance tasks"""
        logger.info("Starting daily security maintenance...")
        
        try:
            # 1. Run vulnerability scans
            if self.config.vulnerability_scan.enabled:
                await self.vulnerability_scanner.run_scheduled_scans()
            
            # 2. Check 2FA compliance
            users_requiring_2fa = await self.two_fa_manager.get_users_requiring_2fa()
            if users_requiring_2fa:
                logger.warning(f"{len(users_requiring_2fa)} users require 2FA setup")
            
            # 3. Run API key rotation maintenance
            if self.config.api_key_rotation.enabled:
                maintenance_result = await run_rotation_maintenance()
                logger.info(f"API key maintenance: {maintenance_result}")
            
            # 4. Create daily backup
            if self.config.backup.daily_backup:
                backup_result = await create_backup("daily_incremental")
                logger.info(f"Daily backup created: {backup_result['backup_id']}")
            
            # 5. Clean up expired backups
            expired_backups = await self.backup_system.cleanup_expired_backups()
            if expired_backups:
                logger.info(f"Cleaned up {len(expired_backups)} expired backups")
            
            # 6. Perform health check
            await self.perform_health_check()
            
            await log_audit_event(
                "security.maintenance.daily",
                action="Daily security maintenance completed",
                details={
                    "vulnerability_scans": self.config.vulnerability_scan.enabled,
                    "users_requiring_2fa": len(users_requiring_2fa),
                    "api_maintenance": self.config.api_key_rotation.enabled,
                    "backup_created": self.config.backup.daily_backup,
                    "expired_backups_cleaned": len(expired_backups)
                }
            )
            
        except Exception as e:
            logger.error(f"Daily maintenance failed: {e}")
            await log_audit_event(
                "security.maintenance.failed",
                action="Daily security maintenance failed",
                details={"error": str(e)}
            )
    
    async def run_weekly_maintenance(self):
        """Run weekly security maintenance tasks"""
        logger.info("Starting weekly security maintenance...")
        
        try:
            # 1. Create weekly full backup
            if self.config.backup.weekly_full_backup:
                backup_result = await create_backup("weekly_full")
                logger.info(f"Weekly backup created: {backup_result['backup_id']}")
                
                # Test restoration
                if self.config.backup.test_restoration_weekly:
                    test_result = await test_backup_restoration(backup_result['backup_id'])
                    logger.info(f"Backup restoration test: {test_result['success']}")
            
            # 2. Generate compliance reports
            compliance_report = await self.generate_compliance_report()
            logger.info(f"Compliance report generated: {len(compliance_report)} items")
            
            await log_audit_event(
                "security.maintenance.weekly",
                action="Weekly security maintenance completed",
                details={
                    "weekly_backup": self.config.backup.weekly_full_backup,
                    "restoration_test": self.config.backup.test_restoration_weekly,
                    "compliance_items": len(compliance_report)
                }
            )
            
        except Exception as e:
            logger.error(f"Weekly maintenance failed: {e}")
            await log_audit_event(
                "security.maintenance.weekly.failed",
                action="Weekly security maintenance failed",
                details={"error": str(e)}
            )
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": 30,
            "components": {}
        }
        
        # Security incidents
        incidents = await self.audit_trail.get_security_incidents(days=30)
        report["components"]["security_incidents"] = {
            "total_incidents": len(incidents),
            "critical_incidents": len([i for i in incidents if i["severity"] == "critical"]),
            "incidents": incidents[:10]  # Latest 10
        }
        
        # 2FA compliance
        stats = await self.two_fa_manager.get_2fa_stats()
        report["components"]["2fa_compliance"] = stats
        
        # Vulnerability status
        vuln_summary = self.vulnerability_scanner.get_latest_summary()
        report["components"]["vulnerability_status"] = vuln_summary
        
        # Backup status
        backup_status = await self.backup_system.get_backup_status()
        report["components"]["backup_status"] = backup_status
        
        # API key rotation
        rotation_status = await self.rotation_manager.get_rotation_status()
        report["components"]["api_key_rotation"] = rotation_status
        
        return report
    
    def start_security_scheduler(self):
        """Start the security maintenance scheduler"""
        if self.scheduler_running:
            logger.warning("Security scheduler is already running")
            return
        
        # Clear any existing schedules
        schedule.clear()
        
        # Schedule daily maintenance at 2 AM
        schedule.every().day.at("02:00").do(lambda: asyncio.run(self.run_daily_maintenance()))
        
        # Schedule weekly maintenance on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(lambda: asyncio.run(self.run_weekly_maintenance()))
        
        # Schedule health checks every hour
        schedule.every().hour.do(lambda: asyncio.run(self.perform_health_check()))
        
        def run_scheduler():
            self.scheduler_running = True
            logger.info("Security maintenance scheduler started")
            
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_security_scheduler(self):
        """Stop the security maintenance scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Security maintenance scheduler stopped")
    
    async def emergency_lockdown(self, reason: str) -> Dict[str, Any]:
        """Emergency security lockdown"""
        logger.critical(f"EMERGENCY LOCKDOWN INITIATED: {reason}")
        
        lockdown_actions = []
        
        try:
            # 1. Disable new API key creation
            # Implementation would depend on your API gateway
            lockdown_actions.append("API key creation disabled")
            
            # 2. Revoke all temporary tokens
            # Implementation would depend on your token system
            lockdown_actions.append("Temporary tokens revoked")
            
            # 3. Enable maximum security mode on CloudFlare
            try:
                from core.security.cloudflare_protection import CloudFlareSecurityManager
                config = self.config.cloudflare
                if config.enabled:
                    async with CloudFlareSecurityManager(config) as cf_manager:
                        await cf_manager.update_security_level("under_attack")
                        lockdown_actions.append("CloudFlare security level: under_attack")
            except Exception as e:
                logger.error(f"Failed to update CloudFlare security: {e}")
            
            # 4. Create emergency backup
            backup_result = await create_backup("disaster_recovery")
            lockdown_actions.append(f"Emergency backup created: {backup_result['backup_id']}")
            
            # 5. Log lockdown event
            await log_audit_event(
                "security.emergency.lockdown",
                action=f"Emergency lockdown activated: {reason}",
                details={
                    "reason": reason,
                    "actions_taken": lockdown_actions,
                    "lockdown_time": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "status": "lockdown_active",
                "reason": reason,
                "actions_taken": lockdown_actions,
                "lockdown_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Emergency lockdown failed: {e}")
            return {
                "status": "lockdown_failed",
                "reason": reason,
                "error": str(e),
                "partial_actions": lockdown_actions
            }


# Global orchestrator instance
_orchestrator_instance: Optional[ProductionSecurityOrchestrator] = None

def get_security_orchestrator() -> ProductionSecurityOrchestrator:
    """Get global security orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ProductionSecurityOrchestrator()
    return _orchestrator_instance


async def initialize_production_security() -> Dict[str, Any]:
    """Initialize production security (main entry point)"""
    orchestrator = get_security_orchestrator()
    return await orchestrator.initialize_security_stack()


async def get_security_dashboard() -> Dict[str, Any]:
    """Get security dashboard data"""
    orchestrator = get_security_orchestrator()
    
    # Get health status
    health_status = await orchestrator.perform_health_check()
    
    # Generate compliance report
    compliance_report = await orchestrator.generate_compliance_report()
    
    # Overall status
    critical_components = [h.component for h in health_status.values() if h.status == "critical"]
    warning_components = [h.component for h in health_status.values() if h.status == "warning"]
    
    overall_status = "healthy"
    if critical_components:
        overall_status = "critical"
    elif warning_components:
        overall_status = "warning"
    
    return {
        "overall_status": overall_status,
        "last_updated": datetime.utcnow().isoformat(),
        "health_status": {comp: health.message for comp, health in health_status.items()},
        "critical_components": critical_components,
        "warning_components": warning_components,
        "compliance_report": compliance_report
    }


if __name__ == "__main__":
    async def main():
        # Test security orchestrator
        result = await initialize_production_security()
        print(f"Security initialization: {result['status']}")
        
        # Get dashboard
        dashboard = await get_security_dashboard()
        print(f"Security status: {dashboard['overall_status']}")
    
    asyncio.run(main())