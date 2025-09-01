"""Disaster Recovery Testing Orchestrator
Automated disaster recovery testing and validation system
"""

import asyncio
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import tempfile
import os

# Import backup system
from ..backup.cross_region_backup import BackupStatus, RecoveryObjective

logger = logging.getLogger(__name__)


class DRTestType(Enum):
    """Types of disaster recovery tests"""
    BACKUP_RESTORE = "backup_restore"
    FAILOVER = "failover"
    DATABASE_RECOVERY = "database_recovery"
    APPLICATION_RECOVERY = "application_recovery"
    NETWORK_FAILOVER = "network_failover"
    FULL_SITE_RECOVERY = "full_site_recovery"
    RTO_VALIDATION = "rto_validation"  # Recovery Time Objective
    RPO_VALIDATION = "rpo_validation"  # Recovery Point Objective


class DRTestStatus(Enum):
    """Disaster recovery test status"""
    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    RUNNING = "running"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DRTestConfig:
    """Configuration for disaster recovery testing"""
    name: str
    test_type: DRTestType
    description: str
    
    # Test parameters
    backup_source: str = None
    restore_target: str = None
    test_environment: str = "staging"  # "staging", "production", "isolated"
    
    # Recovery objectives
    rto_target_minutes: int = 60  # Recovery Time Objective
    rpo_target_minutes: int = 15  # Recovery Point Objective
    
    # Test scenarios
    failure_scenarios: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    
    # Automation settings
    automated_cleanup: bool = True
    notification_endpoints: List[str] = field(default_factory=list)
    max_duration_hours: int = 4
    
    # Compliance requirements
    compliance_frameworks: List[str] = field(default_factory=list)
    documentation_required: bool = True


@dataclass
class DRTestStep:
    """Individual step in disaster recovery test"""
    step_id: str
    name: str
    description: str
    start_time: datetime = None
    end_time: datetime = None
    status: str = "pending"  # "pending", "running", "completed", "failed", "skipped"
    duration_seconds: float = 0.0
    output: str = ""
    error_message: str = None
    validation_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DRTestResult:
    """Disaster recovery test result"""
    test_id: str
    config: DRTestConfig
    start_time: datetime
    end_time: datetime = None
    status: DRTestStatus = DRTestStatus.SCHEDULED
    
    # Test execution
    steps: List[DRTestStep] = field(default_factory=list)
    current_step: int = 0
    
    # Performance metrics
    actual_rto_minutes: float = 0.0
    actual_rpo_minutes: float = 0.0
    data_integrity_score: float = 100.0
    system_availability_score: float = 100.0
    
    # Test results
    success: bool = False
    failed_steps: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    
    # Documentation
    test_report_path: str = None
    evidence_artifacts: List[str] = field(default_factory=list)


class DisasterRecoveryTestOrchestrator:
    """
    Orchestrator for disaster recovery testing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, DRTestResult] = {}
        self.test_history: List[DRTestResult] = []
        self.test_templates: Dict[str, DRTestConfig] = {}
        
        # Initialize test templates
        self._initialize_test_templates()
    
    def _initialize_test_templates(self):
        """Initialize predefined test templates"""
        
        # Database backup/restore test
        self.test_templates["database_backup_restore"] = DRTestConfig(
            name="Database Backup Restore Test",
            test_type=DRTestType.DATABASE_RECOVERY,
            description="Test database backup and restore procedures",
            rto_target_minutes=30,
            rpo_target_minutes=5,
            failure_scenarios=["database_corruption", "server_failure"],
            validation_checks=[
                "data_integrity_check",
                "application_connectivity_check",
                "performance_baseline_check"
            ],
            compliance_frameworks=["SOC2", "ISO27001"]
        )
        
        # Application failover test
        self.test_templates["application_failover"] = DRTestConfig(
            name="Application Failover Test",
            test_type=DRTestType.APPLICATION_RECOVERY,
            description="Test application failover to backup systems",
            rto_target_minutes=15,
            rpo_target_minutes=1,
            failure_scenarios=["primary_server_failure", "network_partition"],
            validation_checks=[
                "service_availability_check",
                "load_balancer_check",
                "session_continuity_check"
            ]
        )
        
        # Full site recovery test
        self.test_templates["full_site_recovery"] = DRTestConfig(
            name="Full Site Recovery Test",
            test_type=DRTestType.FULL_SITE_RECOVERY,
            description="Complete disaster recovery simulation",
            rto_target_minutes=120,
            rpo_target_minutes=15,
            max_duration_hours=8,
            failure_scenarios=[
                "datacenter_outage",
                "complete_infrastructure_failure",
                "network_infrastructure_failure"
            ],
            validation_checks=[
                "full_system_functionality_check",
                "data_consistency_check",
                "performance_validation",
                "security_validation",
                "monitoring_system_check"
            ],
            compliance_frameworks=["SOC2", "ISO27001", "PCI_DSS"]
        )
    
    async def schedule_dr_test(self, config: DRTestConfig, schedule_time: datetime = None) -> str:
        """Schedule a disaster recovery test"""
        test_id = f"dr_test_{config.test_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"Scheduling DR test: {test_id}")
            
            # Create test result
            result = DRTestResult(
                test_id=test_id,
                config=config,
                start_time=schedule_time or datetime.now()
            )
            
            # Initialize test steps based on test type
            await self._initialize_test_steps(result)
            
            self.active_tests[test_id] = result
            
            # Start test execution if immediate
            if schedule_time is None or schedule_time <= datetime.now():
                asyncio.create_task(self._execute_dr_test(test_id))
            
            return test_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling DR test: {e}")
            raise
    
    async def _initialize_test_steps(self, result: DRTestResult):
        """Initialize test steps based on test type"""
        config = result.config
        
        if config.test_type == DRTestType.BACKUP_RESTORE:
            result.steps = [
                DRTestStep("prepare", "Prepare test environment", "Set up isolated test environment"),
                DRTestStep("backup", "Create backup", "Create backup of source data"),
                DRTestStep("simulate_failure", "Simulate failure", "Simulate data loss or corruption"),
                DRTestStep("restore", "Restore from backup", "Restore data from backup"),
                DRTestStep("validate", "Validate restoration", "Verify data integrity and completeness"),
                DRTestStep("cleanup", "Cleanup", "Clean up test environment")
            ]
        
        elif config.test_type == DRTestType.DATABASE_RECOVERY:
            result.steps = [
                DRTestStep("prepare", "Prepare test database", "Set up test database instance"),
                DRTestStep("baseline", "Create baseline", "Create baseline data and metrics"),
                DRTestStep("backup", "Create database backup", "Create full database backup"),
                DRTestStep("simulate_failure", "Simulate database failure", "Simulate database corruption or loss"),
                DRTestStep("restore", "Restore database", "Restore database from backup"),
                DRTestStep("validate_data", "Validate data integrity", "Check data consistency and integrity"),
                DRTestStep("validate_performance", "Validate performance", "Check database performance"),
                DRTestStep("cleanup", "Cleanup", "Clean up test resources")
            ]
        
        elif config.test_type == DRTestType.FULL_SITE_RECOVERY:
            result.steps = [
                DRTestStep("prepare", "Prepare recovery environment", "Set up complete recovery environment"),
                DRTestStep("backup_verification", "Verify backups", "Verify all backup systems are current"),
                DRTestStep("simulate_disaster", "Simulate disaster", "Simulate complete site failure"),
                DRTestStep("initiate_recovery", "Initiate recovery", "Start disaster recovery procedures"),
                DRTestStep("restore_infrastructure", "Restore infrastructure", "Restore network and compute infrastructure"),
                DRTestStep("restore_data", "Restore data", "Restore all data systems"),
                DRTestStep("restore_applications", "Restore applications", "Restore and configure applications"),
                DRTestStep("validate_functionality", "Validate functionality", "Test all system functionality"),
                DRTestStep("validate_performance", "Validate performance", "Verify performance meets requirements"),
                DRTestStep("validate_security", "Validate security", "Verify security controls are in place"),
                DRTestStep("switchover", "Complete switchover", "Complete switchover to recovery systems"),
                DRTestStep("cleanup", "Cleanup", "Clean up test resources")
            ]
        
        else:
            # Default steps for other test types
            result.steps = [
                DRTestStep("prepare", "Prepare test", "Prepare test environment"),
                DRTestStep("execute", "Execute test", "Execute disaster recovery test"),
                DRTestStep("validate", "Validate results", "Validate test results"),
                DRTestStep("cleanup", "Cleanup", "Clean up test environment")
            ]
    
    async def _execute_dr_test(self, test_id: str):
        """Execute disaster recovery test"""
        result = self.active_tests[test_id]
        
        try:
            self.logger.info(f"Starting DR test execution: {test_id}")
            result.status = DRTestStatus.PREPARING
            result.start_time = datetime.now()
            
            # Execute each step
            for i, step in enumerate(result.steps):
                result.current_step = i
                await self._execute_test_step(result, step)
                
                # Check if step failed and should stop
                if step.status == "failed" and not result.config.test_type == DRTestType.FULL_SITE_RECOVERY:
                    self.logger.error(f"DR test {test_id} failed at step: {step.name}")
                    result.status = DRTestStatus.FAILED
                    result.failed_steps.append(step.step_id)
                    break
                elif step.status == "failed":
                    result.failed_steps.append(step.step_id)
            
            # Calculate final metrics
            await self._calculate_test_metrics(result)
            
            # Generate compliance report
            await self._evaluate_compliance(result)
            
            # Determine overall success
            result.success = len(result.failed_steps) == 0
            result.status = DRTestStatus.COMPLETED if result.success else DRTestStatus.FAILED
            result.end_time = datetime.now()
            
            # Generate test report
            await self._generate_test_report(result)
            
            # Move to history
            self.test_history.append(result)
            del self.active_tests[test_id]
            
            self.logger.info(f"DR test {test_id} completed with status: {result.status.value}")
            
        except Exception as e:
            self.logger.error(f"Error executing DR test {test_id}: {e}")
            result.status = DRTestStatus.FAILED
            result.end_time = datetime.now()
            if test_id in self.active_tests:
                self.test_history.append(result)
                del self.active_tests[test_id]
    
    async def _execute_test_step(self, result: DRTestResult, step: DRTestStep):
        """Execute individual test step"""
        try:
            self.logger.info(f"Executing step: {step.name}")
            step.status = "running"
            step.start_time = datetime.now()
            
            # Execute step based on step_id
            if step.step_id == "prepare":
                await self._execute_prepare_step(result, step)
            elif step.step_id == "backup":
                await self._execute_backup_step(result, step)
            elif step.step_id == "simulate_failure":
                await self._execute_simulate_failure_step(result, step)
            elif step.step_id == "restore":
                await self._execute_restore_step(result, step)
            elif step.step_id == "validate":
                await self._execute_validate_step(result, step)
            elif step.step_id == "cleanup":
                await self._execute_cleanup_step(result, step)
            else:
                # Generic step execution
                await self._execute_generic_step(result, step)
            
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            
            if step.status == "running":  # If not explicitly set to failed
                step.status = "completed"
            
        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            step.end_time = datetime.now()
            if step.start_time:
                step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            self.logger.error(f"Step {step.name} failed: {e}")
    
    async def _execute_prepare_step(self, result: DRTestResult, step: DRTestStep):
        """Execute preparation step"""
        config = result.config
        
        # Create test workspace
        test_workspace = f"/tmp/dr_test_{result.test_id}"
        os.makedirs(test_workspace, exist_ok=True)
        
        step.output += f"Created test workspace: {test_workspace}\n"
        
        # Validate test environment
        if config.test_environment == "production":
            step.output += "WARNING: Test configured for production environment\n"
        
        # Verify backup sources exist
        if config.backup_source:
            if os.path.exists(config.backup_source):
                step.output += f"Backup source verified: {config.backup_source}\n"
            else:
                step.status = "failed"
                step.error_message = f"Backup source not found: {config.backup_source}"
                return
        
        # Prepare monitoring
        step.output += "Test environment prepared successfully\n"
    
    async def _execute_backup_step(self, result: DRTestResult, step: DRTestStep):
        """Execute backup step"""
        config = result.config
        
        if config.backup_source:
            # Simulate backup creation
            backup_start = datetime.now()
            
            step.output += f"Starting backup of: {config.backup_source}\n"
            
            # Simulate backup time (in real implementation, this would be actual backup)
            await asyncio.sleep(2)  # Simulate backup process
            
            backup_end = datetime.now()
            backup_duration = (backup_end - backup_start).total_seconds()
            
            step.output += f"Backup completed in {backup_duration:.2f} seconds\n"
            step.validation_results["backup_duration_seconds"] = backup_duration
        else:
            step.output += "No backup source specified, skipping backup creation\n"
    
    async def _execute_simulate_failure_step(self, result: DRTestResult, step: DRTestStep):
        """Execute failure simulation step"""
        config = result.config
        
        step.output += "Simulating failure scenarios:\n"
        
        for scenario in config.failure_scenarios:
            step.output += f"- Simulating: {scenario}\n"
            
            # Simulate different failure types
            if "database" in scenario.lower():
                step.output += "  * Database connectivity interrupted\n"
                step.output += "  * Database files marked as corrupted\n"
            elif "server" in scenario.lower():
                step.output += "  * Server marked as unreachable\n"
                step.output += "  * Services marked as stopped\n"
            elif "network" in scenario.lower():
                step.output += "  * Network connectivity disrupted\n"
                step.output += "  * Network routes updated\n"
            
            # Small delay to simulate realistic failure timing
            await asyncio.sleep(1)
        
        step.output += "Failure simulation completed\n"
    
    async def _execute_restore_step(self, result: DRTestResult, step: DRTestStep):
        """Execute restore step"""
        config = result.config
        
        restore_start = datetime.now()
        step.output += "Starting restore process\n"
        
        # Simulate restore process
        if config.test_type == DRTestType.DATABASE_RECOVERY:
            step.output += "Restoring database from backup\n"
            await asyncio.sleep(3)  # Simulate database restore
            step.output += "Database schema restored\n"
            step.output += "Database data restored\n"
            step.output += "Database indexes rebuilt\n"
        elif config.test_type == DRTestType.APPLICATION_RECOVERY:
            step.output += "Restoring application services\n"
            await asyncio.sleep(2)  # Simulate application restore
            step.output += "Application binaries restored\n"
            step.output += "Configuration files restored\n"
            step.output += "Services restarted\n"
        else:
            step.output += "Restoring from backup\n"
            await asyncio.sleep(2)  # Generic restore simulation
        
        restore_end = datetime.now()
        restore_duration = (restore_end - restore_start).total_seconds()
        
        # Calculate RTO (Recovery Time Objective)
        total_recovery_time = (restore_end - result.start_time).total_seconds() / 60
        result.actual_rto_minutes = total_recovery_time
        
        step.output += f"Restore completed in {restore_duration:.2f} seconds\n"
        step.output += f"Total recovery time: {total_recovery_time:.2f} minutes\n"
        
        step.validation_results.update({
            "restore_duration_seconds": restore_duration,
            "total_recovery_time_minutes": total_recovery_time,
            "rto_target_met": total_recovery_time <= config.rto_target_minutes
        })
    
    async def _execute_validate_step(self, result: DRTestResult, step: DRTestStep):
        """Execute validation step"""
        config = result.config
        
        step.output += "Starting validation checks\n"
        
        validation_results = {}
        
        for check in config.validation_checks:
            step.output += f"Running validation: {check}\n"
            
            # Simulate different validation checks
            if "data_integrity" in check.lower():
                # Simulate data integrity check
                await asyncio.sleep(1)
                integrity_score = 100.0  # Assume perfect integrity for simulation
                validation_results[check] = {
                    "passed": True,
                    "score": integrity_score,
                    "details": "All data integrity checks passed"
                }
                result.data_integrity_score = integrity_score
                step.output += f"  ✓ Data integrity: {integrity_score}%\n"
                
            elif "performance" in check.lower():
                # Simulate performance check
                await asyncio.sleep(1)
                performance_score = 95.0  # Simulate slight performance degradation
                validation_results[check] = {
                    "passed": performance_score >= 90,
                    "score": performance_score,
                    "details": "Performance within acceptable range"
                }
                step.output += f"  ✓ Performance: {performance_score}%\n"
                
            elif "availability" in check.lower():
                # Simulate availability check
                await asyncio.sleep(0.5)
                availability_score = 100.0
                validation_results[check] = {
                    "passed": True,
                    "score": availability_score,
                    "details": "All services available"
                }
                result.system_availability_score = availability_score
                step.output += f"  ✓ System availability: {availability_score}%\n"
                
            elif "connectivity" in check.lower():
                # Simulate connectivity check
                await asyncio.sleep(0.5)
                validation_results[check] = {
                    "passed": True,
                    "details": "All network connections established"
                }
                step.output += f"  ✓ Connectivity: OK\n"
                
            else:
                # Generic validation
                await asyncio.sleep(0.5)
                validation_results[check] = {
                    "passed": True,
                    "details": "Validation completed successfully"
                }
                step.output += f"  ✓ {check}: OK\n"
        
        # Overall validation result
        all_passed = all(result.get("passed", True) for result in validation_results.values())
        step.validation_results = validation_results
        result.validation_results.update(validation_results)
        
        if not all_passed:
            step.status = "failed"
            step.error_message = "Some validation checks failed"
        
        step.output += f"Validation completed - {'All checks passed' if all_passed else 'Some checks failed'}\n"
    
    async def _execute_cleanup_step(self, result: DRTestResult, step: DRTestStep):
        """Execute cleanup step"""
        step.output += "Starting cleanup process\n"
        
        # Cleanup test workspace
        test_workspace = f"/tmp/dr_test_{result.test_id}"
        if os.path.exists(test_workspace):
            shutil.rmtree(test_workspace)
            step.output += f"Removed test workspace: {test_workspace}\n"
        
        # Reset any test configurations
        step.output += "Reset test configurations\n"
        
        # Archive test artifacts
        step.output += "Archived test artifacts\n"
        
        step.output += "Cleanup completed\n"
    
    async def _execute_generic_step(self, result: DRTestResult, step: DRTestStep):
        """Execute generic test step"""
        step.output += f"Executing {step.name}\n"
        
        # Simulate step execution
        await asyncio.sleep(1)
        
        step.output += f"{step.description} completed\n"
    
    async def _calculate_test_metrics(self, result: DRTestResult):
        """Calculate final test metrics"""
        config = result.config
        
        # Calculate total test duration
        if result.end_time:
            total_duration = (result.end_time - result.start_time).total_seconds() / 60
        else:
            total_duration = 0
        
        # Calculate RPO (Recovery Point Objective) - simulated
        result.actual_rpo_minutes = 5.0  # Simulate 5-minute RPO
        
        # Update metrics based on validation results
        if not result.validation_results:
            result.data_integrity_score = 0.0
            result.system_availability_score = 0.0
    
    async def _evaluate_compliance(self, result: DRTestResult):
        """Evaluate compliance status"""
        config = result.config
        
        for framework in config.compliance_frameworks:
            compliance_met = True
            
            if framework == "SOC2":
                # SOC2 requires documented procedures and successful execution
                compliance_met = (
                    result.success and
                    result.actual_rto_minutes <= config.rto_target_minutes and
                    result.data_integrity_score >= 99.0
                )
            elif framework == "ISO27001":
                # ISO27001 requires risk-based approach and continuous improvement
                compliance_met = (
                    result.success and
                    len(result.failed_steps) == 0 and
                    result.system_availability_score >= 95.0
                )
            elif framework == "PCI_DSS":
                # PCI DSS requires specific data protection measures
                compliance_met = (
                    result.success and
                    result.data_integrity_score == 100.0 and
                    "security_validation" in [step.step_id for step in result.steps if step.status == "completed"]
                )
            
            result.compliance_status[framework] = compliance_met
    
    async def _generate_test_report(self, result: DRTestResult):
        """Generate comprehensive test report"""
        config = result.config
        
        report = {
            "test_summary": {
                "test_id": result.test_id,
                "test_name": config.name,
                "test_type": config.test_type.value,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration_minutes": (result.end_time - result.start_time).total_seconds() / 60 if result.end_time else 0,
                "status": result.status.value,
                "success": result.success
            },
            "recovery_objectives": {
                "rto_target_minutes": config.rto_target_minutes,
                "rto_actual_minutes": result.actual_rto_minutes,
                "rto_met": result.actual_rto_minutes <= config.rto_target_minutes,
                "rpo_target_minutes": config.rpo_target_minutes,
                "rpo_actual_minutes": result.actual_rpo_minutes,
                "rpo_met": result.actual_rpo_minutes <= config.rpo_target_minutes
            },
            "test_execution": {
                "total_steps": len(result.steps),
                "completed_steps": len([s for s in result.steps if s.status == "completed"]),
                "failed_steps": len(result.failed_steps),
                "step_details": [
                    {
                        "step_id": step.step_id,
                        "name": step.name,
                        "status": step.status,
                        "duration_seconds": step.duration_seconds,
                        "error_message": step.error_message
                    }
                    for step in result.steps
                ]
            },
            "validation_results": result.validation_results,
            "performance_metrics": {
                "data_integrity_score": result.data_integrity_score,
                "system_availability_score": result.system_availability_score
            },
            "compliance_status": result.compliance_status
        }
        
        # Save report to file
        report_filename = f"dr_test_report_{result.test_id}.json"
        report_path = f"/tmp/{report_filename}"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        result.test_report_path = report_path
        result.evidence_artifacts.append(report_path)
    
    async def get_test_status(self, test_id: str) -> Optional[DRTestResult]:
        """Get status of a specific test"""
        if test_id in self.active_tests:
            return self.active_tests[test_id]
        
        for result in self.test_history:
            if result.test_id == test_id:
                return result
        
        return None
    
    async def get_active_tests(self) -> List[DRTestResult]:
        """Get all active tests"""
        return list(self.active_tests.values())
    
    async def get_test_history(self, limit: int = 50) -> List[DRTestResult]:
        """Get test history"""
        return sorted(self.test_history, key=lambda x: x.start_time, reverse=True)[:limit]
    
    async def cancel_test(self, test_id: str) -> bool:
        """Cancel a running test"""
        if test_id in self.active_tests:
            result = self.active_tests[test_id]
            result.status = DRTestStatus.CANCELLED
            result.end_time = datetime.now()
            
            # Move to history
            self.test_history.append(result)
            del self.active_tests[test_id]
            
            self.logger.info(f"DR test {test_id} cancelled")
            return True
        
        return False
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status based on recent tests"""
        recent_tests = [t for t in self.test_history if 
                       t.end_time and t.end_time >= datetime.now() - timedelta(days=90)]
        
        if not recent_tests:
            return {"message": "No recent tests found"}
        
        # Aggregate compliance status
        frameworks = set()
        for test in recent_tests:
            frameworks.update(test.compliance_status.keys())
        
        compliance_summary = {}
        for framework in frameworks:
            framework_tests = [t for t in recent_tests if framework in t.compliance_status]
            if framework_tests:
                compliant_tests = [t for t in framework_tests if t.compliance_status[framework]]
                compliance_summary[framework] = {
                    "compliant": len(compliant_tests) == len(framework_tests),
                    "compliance_rate": len(compliant_tests) / len(framework_tests) * 100,
                    "total_tests": len(framework_tests),
                    "compliant_tests": len(compliant_tests)
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "period": "Last 90 days",
            "total_tests": len(recent_tests),
            "successful_tests": len([t for t in recent_tests if t.success]),
            "success_rate": len([t for t in recent_tests if t.success]) / len(recent_tests) * 100,
            "compliance_by_framework": compliance_summary,
            "avg_rto_minutes": sum(t.actual_rto_minutes for t in recent_tests) / len(recent_tests),
            "avg_rpo_minutes": sum(t.actual_rpo_minutes for t in recent_tests) / len(recent_tests)
        }


# Global disaster recovery test orchestrator
dr_test_orchestrator = DisasterRecoveryTestOrchestrator()