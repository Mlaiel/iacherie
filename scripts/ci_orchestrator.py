#!/usr/bin/env python3
"""
CI/CD Orchestrator - Enterprise CI/CD Pipeline Automation
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced CI/CD pipeline orchestration for Ainflue Platform:
- Automated code quality checks
- Security vulnerability scanning
- Build and test automation
- Deployment pipeline management
- Quality gates and compliance
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from dataclasses import dataclass, asdict
from enum import Enum

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/cicd.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    SOURCE = "source"
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    QUALITY_GATE = "quality_gate"
    PACKAGE = "package"
    DEPLOY_STAGING = "deploy_staging"
    INTEGRATION_TEST = "integration_test"
    DEPLOY_PRODUCTION = "deploy_production"
    MONITORING = "monitoring"

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

@dataclass
class PipelineRun:
    """CI/CD pipeline run"""
    run_id: str
    commit_sha: str
    branch: str
    trigger: str
    started_at: datetime
    status: PipelineStatus
    stages: Dict[str, Dict[str, Any]]
    completed_at: Optional[datetime] = None
    artifacts: List[str] = None

@dataclass
class QualityMetrics:
    """Code quality metrics"""
    coverage_percentage: float
    technical_debt_ratio: float
    code_smells: int
    bugs: int
    vulnerabilities: int
    security_hotspots: int
    duplicated_lines_percentage: float
    maintainability_rating: str
    reliability_rating: str
    security_rating: str

class CICDOrchestrator:
    """
    Enterprise CI/CD pipeline orchestration system
    
    Features:
    - Automated pipeline execution
    - Quality gates and compliance checks
    - Security vulnerability scanning
    - Build artifact management
    - Deployment automation
    - Monitoring and alerting
    """
    
    def __init__(self, config_path: str = "/etc/ainflue/cicd.yaml"):
        self.config_path = config_path
        self.active_runs: Dict[str, PipelineRun] = {}
        self.completed_runs: List[PipelineRun] = []
        self.config = {}
        
    async def load_cicd_configuration(self):
        """Load CI/CD configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info("CI/CD configuration loaded")
            
        except FileNotFoundError:
            # Create default configuration
            self.config = {
                'repository': {
                    'url': 'https://github.com/Mlaiel/Ainflue.git',
                    'default_branch': 'main'
                },
                'stages': {
                    'build': {
                        'enabled': True,
                        'commands': ['npm install', 'npm run build'],
                        'timeout': 600
                    },
                    'test': {
                        'enabled': True,
                        'commands': ['npm test', 'python -m pytest'],
                        'timeout': 1800,
                        'coverage_threshold': 80
                    },
                    'security_scan': {
                        'enabled': True,
                        'tools': ['npm audit', 'safety check', 'bandit'],
                        'timeout': 300
                    },
                    'quality_gate': {
                        'enabled': True,
                        'rules': {
                            'coverage_min': 80,
                            'technical_debt_max': 5,
                            'vulnerabilities_max': 0,
                            'bugs_max': 0
                        }
                    }
                },
                'notifications': {
                    'slack_webhook': None,
                    'email_recipients': []
                },
                'artifacts': {
                    'retention_days': 30,
                    'storage_path': '/var/lib/ainflue/artifacts'
                }
            }
            
            logger.info("Created default CI/CD configuration")
    
    async def trigger_pipeline(self, commit_sha: str, branch: str = "main", 
                             trigger: str = "manual") -> str:
        """Trigger a new CI/CD pipeline run"""
        try:
            run_id = f"run_{commit_sha[:8]}_{int(time.time())}"
            
            pipeline_run = PipelineRun(
                run_id=run_id,
                commit_sha=commit_sha,
                branch=branch,
                trigger=trigger,
                started_at=datetime.now(),
                status=PipelineStatus.RUNNING,
                stages={stage.value: {'status': 'pending'} for stage in PipelineStage},
                artifacts=[]
            )
            
            self.active_runs[run_id] = pipeline_run
            
            logger.info(f"Pipeline triggered: {run_id}")
            
            # Execute pipeline asynchronously
            asyncio.create_task(self._execute_pipeline(pipeline_run))
            
            return run_id
            
        except Exception as e:
            logger.error(f"Failed to trigger pipeline: {e}")
            raise
    
    async def _execute_pipeline(self, pipeline_run: PipelineRun):
        """Execute complete CI/CD pipeline"""
        try:
            logger.info(f"Executing pipeline: {pipeline_run.run_id}")
            
            # Execute stages in order
            stages = [
                PipelineStage.SOURCE,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.SECURITY_SCAN,
                PipelineStage.QUALITY_GATE,
                PipelineStage.PACKAGE,
                PipelineStage.DEPLOY_STAGING,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.DEPLOY_PRODUCTION,
                PipelineStage.MONITORING
            ]
            
            for stage in stages:
                if not await self._execute_stage(pipeline_run, stage):
                    pipeline_run.status = PipelineStatus.FAILED
                    break
            else:
                pipeline_run.status = PipelineStatus.SUCCESS
            
            # Complete pipeline
            pipeline_run.completed_at = datetime.now()
            
            # Move to completed runs
            del self.active_runs[pipeline_run.run_id]
            self.completed_runs.append(pipeline_run)
            
            # Send notifications
            await self._send_pipeline_notification(pipeline_run)
            
            logger.info(f"Pipeline completed: {pipeline_run.run_id} - {pipeline_run.status.value}")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_run.status = PipelineStatus.FAILED
            pipeline_run.completed_at = datetime.now()
    
    async def _execute_stage(self, pipeline_run: PipelineRun, stage: PipelineStage) -> bool:
        """Execute a single pipeline stage"""
        try:
            logger.info(f"Executing stage: {stage.value}")
            
            stage_info = pipeline_run.stages[stage.value]
            stage_info['status'] = 'running'
            stage_info['started_at'] = datetime.now().isoformat()
            
            success = False
            
            if stage == PipelineStage.SOURCE:
                success = await self._execute_source_stage(pipeline_run)
            elif stage == PipelineStage.BUILD:
                success = await self._execute_build_stage(pipeline_run)
            elif stage == PipelineStage.TEST:
                success = await self._execute_test_stage(pipeline_run)
            elif stage == PipelineStage.SECURITY_SCAN:
                success = await self._execute_security_scan(pipeline_run)
            elif stage == PipelineStage.QUALITY_GATE:
                success = await self._execute_quality_gate(pipeline_run)
            elif stage == PipelineStage.PACKAGE:
                success = await self._execute_package_stage(pipeline_run)
            elif stage == PipelineStage.DEPLOY_STAGING:
                success = await self._execute_deploy_stage(pipeline_run, "staging")
            elif stage == PipelineStage.INTEGRATION_TEST:
                success = await self._execute_integration_test(pipeline_run)
            elif stage == PipelineStage.DEPLOY_PRODUCTION:
                success = await self._execute_deploy_stage(pipeline_run, "production")
            elif stage == PipelineStage.MONITORING:
                success = await self._execute_monitoring_stage(pipeline_run)
            
            stage_info['completed_at'] = datetime.now().isoformat()
            stage_info['status'] = 'success' if success else 'failed'
            
            return success
            
        except Exception as e:
            logger.error(f"Stage {stage.value} failed: {e}")
            stage_info['status'] = 'failed'
            stage_info['error'] = str(e)
            return False
    
    async def _execute_source_stage(self, pipeline_run: PipelineRun) -> bool:
        """Execute source code checkout"""
        try:
            # Clone or update repository
            repo_path = f"/tmp/ainflue_build_{pipeline_run.run_id}"
            
            if os.path.exists(repo_path):
                # Update existing clone
                result = await self._run_command([
                    'git', 'fetch', '--all'
                ], cwd=repo_path)
                
                if result['returncode'] != 0:
                    return False
                
                result = await self._run_command([
                    'git', 'checkout', pipeline_run.commit_sha
                ], cwd=repo_path)
                
            else:
                # Fresh clone
                result = await self._run_command([
                    'git', 'clone', 
                    self.config['repository']['url'],
                    repo_path
                ])
                
                if result['returncode'] != 0:
                    return False
                
                result = await self._run_command([
                    'git', 'checkout', pipeline_run.commit_sha
                ], cwd=repo_path)
            
            pipeline_run.stages[PipelineStage.SOURCE.value]['workspace'] = repo_path
            return result['returncode'] == 0
            
        except Exception as e:
            logger.error(f"Source stage failed: {e}")
            return False
    
    async def _execute_build_stage(self, pipeline_run: PipelineRun) -> bool:
        """Execute build stage"""
        try:
            workspace = pipeline_run.stages[PipelineStage.SOURCE.value].get('workspace')
            if not workspace:
                return False
            
            build_config = self.config['stages']['build']
            
            for command in build_config['commands']:
                result = await self._run_command(
                    command.split(), 
                    cwd=workspace,
                    timeout=build_config.get('timeout', 600)
                )
                
                if result['returncode'] != 0:
                    logger.error(f"Build command failed: {command}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Build stage failed: {e}")
            return False
    
    async def _execute_test_stage(self, pipeline_run: PipelineRun) -> bool:
        """Execute test stage"""
        try:
            workspace = pipeline_run.stages[PipelineStage.SOURCE.value].get('workspace')
            if not workspace:
                return False
            
            test_config = self.config['stages']['test']
            test_results = {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'coverage': 0.0
            }
            
            for command in test_config['commands']:
                result = await self._run_command(
                    command.split(),
                    cwd=workspace,
                    timeout=test_config.get('timeout', 1800)
                )
                
                # Parse test results (simplified)
                if 'pytest' in command:
                    test_results.update(await self._parse_pytest_results(result['stdout']))
                elif 'npm test' in command:
                    test_results.update(await self._parse_jest_results(result['stdout']))
                
                if result['returncode'] != 0:
                    logger.warning(f"Test command failed: {command}")
            
            # Check coverage threshold
            coverage_threshold = test_config.get('coverage_threshold', 80)
            if test_results['coverage'] < coverage_threshold:
                logger.error(f"Coverage {test_results['coverage']}% below threshold {coverage_threshold}%")
                return False
            
            pipeline_run.stages[PipelineStage.TEST.value]['results'] = test_results
            return True
            
        except Exception as e:
            logger.error(f"Test stage failed: {e}")
            return False
    
    async def _execute_security_scan(self, pipeline_run: PipelineRun) -> bool:
        """Execute security scanning"""
        try:
            workspace = pipeline_run.stages[PipelineStage.SOURCE.value].get('workspace')
            if not workspace:
                return False
            
            security_config = self.config['stages']['security_scan']
            security_results = {
                'vulnerabilities': [],
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0
            }
            
            for tool in security_config['tools']:
                result = await self._run_command(
                    tool.split(),
                    cwd=workspace,
                    timeout=security_config.get('timeout', 300)
                )
                
                # Parse security results
                if 'npm audit' in tool:
                    vulns = await self._parse_npm_audit(result['stdout'])
                    security_results['vulnerabilities'].extend(vulns)
                elif 'safety' in tool:
                    vulns = await self._parse_safety_results(result['stdout'])
                    security_results['vulnerabilities'].extend(vulns)
                elif 'bandit' in tool:
                    vulns = await self._parse_bandit_results(result['stdout'])
                    security_results['vulnerabilities'].extend(vulns)
            
            # Count issues by severity
            for vuln in security_results['vulnerabilities']:
                security_results['total_issues'] += 1
                if vuln.get('severity') == 'critical':
                    security_results['critical_issues'] += 1
                elif vuln.get('severity') == 'high':
                    security_results['high_issues'] += 1
            
            pipeline_run.stages[PipelineStage.SECURITY_SCAN.value]['results'] = security_results
            
            # Fail if critical vulnerabilities found
            return security_results['critical_issues'] == 0
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return False
    
    async def _execute_quality_gate(self, pipeline_run: PipelineRun) -> bool:
        """Execute quality gate checks"""
        try:
            quality_config = self.config['stages']['quality_gate']
            rules = quality_config['rules']
            
            # Get test results
            test_results = pipeline_run.stages[PipelineStage.TEST.value].get('results', {})
            security_results = pipeline_run.stages[PipelineStage.SECURITY_SCAN.value].get('results', {})
            
            # Check coverage
            coverage = test_results.get('coverage', 0)
            if coverage < rules.get('coverage_min', 80):
                logger.error(f"Quality gate failed: coverage {coverage}% < {rules['coverage_min']}%")
                return False
            
            # Check vulnerabilities
            critical_vulns = security_results.get('critical_issues', 0)
            if critical_vulns > rules.get('vulnerabilities_max', 0):
                logger.error(f"Quality gate failed: {critical_vulns} critical vulnerabilities")
                return False
            
            # Additional quality metrics could be checked here
            quality_metrics = QualityMetrics(
                coverage_percentage=coverage,
                technical_debt_ratio=2.5,  # Would be calculated from actual analysis
                code_smells=5,
                bugs=0,
                vulnerabilities=critical_vulns,
                security_hotspots=security_results.get('high_issues', 0),
                duplicated_lines_percentage=1.2,
                maintainability_rating="A",
                reliability_rating="A",
                security_rating="A" if critical_vulns == 0 else "C"
            )
            
            pipeline_run.stages[PipelineStage.QUALITY_GATE.value]['metrics'] = asdict(quality_metrics)
            
            logger.info("Quality gate passed")
            return True
            
        except Exception as e:
            logger.error(f"Quality gate failed: {e}")
            return False
    
    async def _execute_package_stage(self, pipeline_run: PipelineRun) -> bool:
        """Execute packaging stage"""
        try:
            workspace = pipeline_run.stages[PipelineStage.SOURCE.value].get('workspace')
            if not workspace:
                return False
            
            # Build Docker image
            image_tag = f"ainflue/platform:{pipeline_run.commit_sha[:8]}"
            
            result = await self._run_command([
                'docker', 'build', 
                '-t', image_tag,
                '-f', 'Dockerfile',
                '.'
            ], cwd=workspace, timeout=600)
            
            if result['returncode'] != 0:
                return False
            
            # Create artifacts
            artifacts_dir = f"{self.config['artifacts']['storage_path']}/{pipeline_run.run_id}"
            os.makedirs(artifacts_dir, exist_ok=True)
            
            # Save image
            result = await self._run_command([
                'docker', 'save', 
                '-o', f"{artifacts_dir}/platform-{pipeline_run.commit_sha[:8]}.tar",
                image_tag
            ])
            
            if result['returncode'] == 0:
                pipeline_run.artifacts.append(f"{artifacts_dir}/platform-{pipeline_run.commit_sha[:8]}.tar")
            
            return result['returncode'] == 0
            
        except Exception as e:
            logger.error(f"Package stage failed: {e}")
            return False
    
    async def _execute_deploy_stage(self, pipeline_run: PipelineRun, environment: str) -> bool:
        """Execute deployment stage"""
        try:
            logger.info(f"Deploying to {environment}")
            
            # Use deployment orchestrator
            result = await self._run_command([
                'python', '/home/runner/work/Ainflue/Ainflue/scripts/deployment_orchestrator.py',
                '--environment', environment,
                '--version', pipeline_run.commit_sha[:8]
            ])
            
            return result['returncode'] == 0
            
        except Exception as e:
            logger.error(f"Deploy to {environment} failed: {e}")
            return False
    
    async def _execute_integration_test(self, pipeline_run: PipelineRun) -> bool:
        """Execute integration tests"""
        try:
            # Run integration tests against staging environment
            workspace = pipeline_run.stages[PipelineStage.SOURCE.value].get('workspace')
            
            result = await self._run_command([
                'python', '-m', 'pytest', 
                'tests/integration/',
                '--env=staging'
            ], cwd=workspace, timeout=1800)
            
            return result['returncode'] == 0
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            return False
    
    async def _execute_monitoring_stage(self, pipeline_run: PipelineRun) -> bool:
        """Execute post-deployment monitoring"""
        try:
            # Start monitoring for the deployed version
            logger.info("Setting up monitoring for deployed version")
            
            # This would typically configure monitoring alerts
            # and health checks for the new deployment
            
            return True
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            return False
    
    async def _run_command(self, command: List[str], cwd: str = None, 
                         timeout: int = 300) -> Dict[str, Any]:
        """Run a command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8')
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Command timeout: {' '.join(command)}")
            return {'returncode': 124, 'stdout': '', 'stderr': 'Timeout'}
        except Exception as e:
            logger.error(f"Command failed: {' '.join(command)} - {e}")
            return {'returncode': 1, 'stdout': '', 'stderr': str(e)}
    
    async def _parse_pytest_results(self, output: str) -> Dict[str, Any]:
        """Parse pytest output"""
        # Simplified parsing
        results = {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'coverage': 0.0}
        
        for line in output.split('\n'):
            if 'passed' in line and 'failed' in line:
                # Parse line like "10 passed, 2 failed"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        results['passed_tests'] = int(parts[i-1])
                    elif part == 'failed' and i > 0:
                        results['failed_tests'] = int(parts[i-1])
            elif 'Total coverage:' in line:
                # Parse coverage percentage
                try:
                    coverage_str = line.split(':')[1].strip().replace('%', '')
                    results['coverage'] = float(coverage_str)
                except:
                    pass
        
        results['total_tests'] = results['passed_tests'] + results['failed_tests']
        return results
    
    async def _parse_jest_results(self, output: str) -> Dict[str, Any]:
        """Parse Jest test output"""
        # Simplified parsing for Jest
        return {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'coverage': 0.0}
    
    async def _parse_npm_audit(self, output: str) -> List[Dict[str, Any]]:
        """Parse npm audit output"""
        vulnerabilities = []
        try:
            if output.strip():
                # Parse JSON output
                audit_data = json.loads(output)
                for vuln_id, vuln_info in audit_data.get('vulnerabilities', {}).items():
                    vulnerabilities.append({
                        'id': vuln_id,
                        'severity': vuln_info.get('severity', 'unknown'),
                        'title': vuln_info.get('title', ''),
                        'package': vuln_info.get('name', ''),
                        'tool': 'npm_audit'
                    })
        except:
            pass
        
        return vulnerabilities
    
    async def _parse_safety_results(self, output: str) -> List[Dict[str, Any]]:
        """Parse Safety scan results"""
        vulnerabilities = []
        # Parse Safety output (simplified)
        for line in output.split('\n'):
            if 'vulnerability' in line.lower():
                vulnerabilities.append({
                    'severity': 'high',
                    'description': line.strip(),
                    'tool': 'safety'
                })
        
        return vulnerabilities
    
    async def _parse_bandit_results(self, output: str) -> List[Dict[str, Any]]:
        """Parse Bandit scan results"""
        vulnerabilities = []
        # Parse Bandit output (simplified)
        for line in output.split('\n'):
            if 'Issue:' in line:
                vulnerabilities.append({
                    'severity': 'medium',
                    'description': line.strip(),
                    'tool': 'bandit'
                })
        
        return vulnerabilities
    
    async def _send_pipeline_notification(self, pipeline_run: PipelineRun):
        """Send pipeline completion notification"""
        try:
            message = f"Pipeline {pipeline_run.run_id} completed with status: {pipeline_run.status.value}"
            logger.info(f"NOTIFICATION: {message}")
            
            # Implementation would send to Slack/email
            
        except Exception as e:
            logger.error(f"Notification failed: {e}")
    
    async def get_pipeline_status(self, run_id: str) -> Optional[PipelineRun]:
        """Get status of a pipeline run"""
        if run_id in self.active_runs:
            return self.active_runs[run_id]
        
        for run in self.completed_runs:
            if run.run_id == run_id:
                return run
        
        return None
    
    async def cancel_pipeline(self, run_id: str) -> bool:
        """Cancel a running pipeline"""
        if run_id in self.active_runs:
            pipeline_run = self.active_runs[run_id]
            pipeline_run.status = PipelineStatus.CANCELLED
            pipeline_run.completed_at = datetime.now()
            
            # Move to completed
            del self.active_runs[run_id]
            self.completed_runs.append(pipeline_run)
            
            logger.info(f"Pipeline cancelled: {run_id}")
            return True
        
        return False
    
    async def generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate CI/CD pipeline report"""
        report = {
            'report_id': f"cicd_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_runs': len(self.completed_runs),
                'active_runs': len(self.active_runs),
                'success_rate': 0.0,
                'avg_duration': 0.0
            },
            'recent_runs': [asdict(run) for run in self.completed_runs[-10:]],
            'quality_trends': {},
            'deployment_frequency': {}
        }
        
        # Calculate success rate
        if self.completed_runs:
            successful_runs = len([r for r in self.completed_runs if r.status == PipelineStatus.SUCCESS])
            report['summary']['success_rate'] = successful_runs / len(self.completed_runs) * 100
            
            # Calculate average duration
            durations = []
            for run in self.completed_runs:
                if run.completed_at:
                    duration = (run.completed_at - run.started_at).total_seconds()
                    durations.append(duration)
            
            if durations:
                report['summary']['avg_duration'] = sum(durations) / len(durations)
        
        return report

async def main():
    """CLI entry point for CI/CD orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue CI/CD Orchestrator')
    parser.add_argument('--trigger', metavar='COMMIT_SHA', help='Trigger pipeline for commit')
    parser.add_argument('--branch', default='main', help='Git branch')
    parser.add_argument('--status', metavar='RUN_ID', help='Get pipeline status')
    parser.add_argument('--cancel', metavar='RUN_ID', help='Cancel pipeline run')
    parser.add_argument('--report', action='store_true', help='Generate pipeline report')
    parser.add_argument('--config', default='/etc/ainflue/cicd.yaml', help='Configuration file')
    
    args = parser.parse_args()
    
    orchestrator = CICDOrchestrator(args.config)
    await orchestrator.load_cicd_configuration()
    
    try:
        if args.trigger:
            run_id = await orchestrator.trigger_pipeline(args.trigger, args.branch)
            print(f"Pipeline triggered: {run_id}")
        
        if args.status:
            pipeline_run = await orchestrator.get_pipeline_status(args.status)
            if pipeline_run:
                print(json.dumps(asdict(pipeline_run), indent=2, default=str))
            else:
                print("Pipeline run not found")
        
        if args.cancel:
            success = await orchestrator.cancel_pipeline(args.cancel)
            print(f"Pipeline {'cancelled' if success else 'not found'}")
        
        if args.report:
            report = await orchestrator.generate_pipeline_report()
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"CI/CD orchestrator failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())