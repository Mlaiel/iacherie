#!/usr/bin/env python3
"""
Deployment Orchestrator - IA Influencer Agent
=============================================
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Multi-format Creator Platform with AI Protection & Monetization

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise deployment orchestrator for multi-environment deployments.
Provides automated, secure, and monitored deployment workflows.
=============================================
"""

import os
import sys
import asyncio
import logging
import argparse
import json
import yaml
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.deployment.environments import (
    EnvironmentType,
    EnvironmentCoordinator,
    EnvironmentManagerFactory
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategy enumeration"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"
    A_B_TESTING = "a_b_testing"


class DeploymentPhase(Enum):
    """Deployment phase enumeration"""
    PREPARATION = "preparation"
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post_deployment"
    VALIDATION = "validation"
    ROLLBACK = "rollback"
    CLEANUP = "cleanup"


class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    environment: str
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    version: str = "latest"
    enable_backup: bool = True
    enable_health_checks: bool = True
    enable_rollback: bool = True
    timeout_minutes: int = 30
    health_check_retries: int = 3
    health_check_interval: int = 30
    rollback_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=list)
    approval_required: bool = False
    maintenance_window: Optional[str] = None


@dataclass
class DeploymentResult:
    """Deployment result data structure"""
    deployment_id: str
    environment: str
    strategy: DeploymentStrategy
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    version_deployed: Optional[str] = None
    previous_version: Optional[str] = None
    phases_completed: List[DeploymentPhase] = field(default_factory=list)
    current_phase: Optional[DeploymentPhase] = None
    error_message: Optional[str] = None
    rollback_performed: bool = False
    health_check_results: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)


class DeploymentOrchestrator:
    """
    Enterprise deployment orchestrator for multi-environment deployments.
    
    Features:
    - Multiple deployment strategies
    - Automated rollback on failure
    - Health checks and validation
    - Blue-green and canary deployments
    - Database migrations
    - Configuration management
    - Monitoring and alerting
    - Approval workflows
    """
    
    def __init__(self):
        self.coordinator = EnvironmentCoordinator()
        self.active_deployments: Dict[str, DeploymentResult] = {}
        
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Execute deployment with specified configuration"""



        try:
            deployment_id = self._generate_deployment_id()
            
            deployment_result = DeploymentResult(
                deployment_id=deployment_id,
                environment=config.environment,
                strategy=config.strategy,
                status=DeploymentStatus.PENDING,
                start_time=datetime.now()
            )
            
            self.active_deployments[deployment_id] = deployment_result
            
            logger.info(f"Starting deployment {deployment_id} to {config.environment}")
            
            # Execute deployment phases
            try:
                deployment_result.status = DeploymentStatus.IN_PROGRESS
                
                # Phase 1: Preparation
                await self._execute_preparation_phase(config, deployment_result)
                
                # Phase 2: Pre-deployment
                await self._execute_pre_deployment_phase(config, deployment_result)
                
                # Phase 3: Deployment
                await self._execute_deployment_phase(config, deployment_result)
                
                # Phase 4: Post-deployment
                await self._execute_post_deployment_phase(config, deployment_result)
                
                # Phase 5: Validation
                await self._execute_validation_phase(config, deployment_result)
                
                # Phase 6: Cleanup
                await self._execute_cleanup_phase(config, deployment_result)
                
                deployment_result.status = DeploymentStatus.SUCCESS
                deployment_result.end_time = datetime.now()
                deployment_result.duration_seconds = (
                    deployment_result.end_time - deployment_result.start_time
                ).total_seconds()
                
                logger.info(f"Deployment {deployment_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Deployment {deployment_id} failed: {e}")
                deployment_result.status = DeploymentStatus.FAILED
                deployment_result.error_message = str(e)
                deployment_result.end_time = datetime.now()
                
                # Attempt rollback if enabled
                if config.rollback_on_failure:
                    await self._execute_rollback(config, deployment_result)
                
            return deployment_result
            
        except Exception as e:
            logger.error(f"Error during deployment: {e}")
            raise
    
    async def _execute_preparation_phase(self, config: DeploymentConfig, 
                                       result: DeploymentResult):
        """Execute preparation phase"""



        try:
            logger.info("Executing preparation phase...")
            result.current_phase = DeploymentPhase.PREPARATION
            
            # Register environment
            env_type = EnvironmentType(config.environment)
            self.coordinator.register_environment(env_type)
            
            # Validate configuration
            await self._validate_deployment_config(config)
            
            # Check prerequisites
            await self._check_deployment_prerequisites(config)
            
            # Create backup if enabled
            if config.enable_backup:
                await self._create_pre_deployment_backup(config)
            
            # Notify deployment start
            await self._send_deployment_notification(
                config, f"Deployment to {config.environment} started"
            )
            
            result.phases_completed.append(DeploymentPhase.PREPARATION)
            logger.info("Preparation phase completed")
            
        except Exception as e:
            logger.error(f"Preparation phase failed: {e}")
            raise
    
    async def _execute_pre_deployment_phase(self, config: DeploymentConfig,
                                          result: DeploymentResult):
        """Execute pre-deployment phase"""



        try:
            logger.info("Executing pre-deployment phase...")
            result.current_phase = DeploymentPhase.PRE_DEPLOYMENT
            
            # Database migrations
            await self._execute_database_migrations(config)
            
            # Configuration updates
            await self._update_configurations(config)
            
            # Security checks
            await self._perform_security_checks(config)
            
            # Resource provisioning
            await self._provision_resources(config)
            
            result.phases_completed.append(DeploymentPhase.PRE_DEPLOYMENT)
            logger.info("Pre-deployment phase completed")
            
        except Exception as e:
            logger.error(f"Pre-deployment phase failed: {e}")
            raise
    
    async def _execute_deployment_phase(self, config: DeploymentConfig,
                                      result: DeploymentResult):
        """Execute deployment phase based on strategy"""



        try:
            logger.info(f"Executing deployment phase with {config.strategy.value} strategy...")
            result.current_phase = DeploymentPhase.DEPLOYMENT
            
            if config.strategy == DeploymentStrategy.ROLLING:
                await self._execute_rolling_deployment(config, result)
            elif config.strategy == DeploymentStrategy.BLUE_GREEN:
                await self._execute_blue_green_deployment(config, result)
            elif config.strategy == DeploymentStrategy.CANARY:
                await self._execute_canary_deployment(config, result)
            elif config.strategy == DeploymentStrategy.RECREATE:
                await self._execute_recreate_deployment(config, result)
            elif config.strategy == DeploymentStrategy.A_B_TESTING:
                await self._execute_ab_testing_deployment(config, result)
            else:
                raise ValueError(f"Unsupported deployment strategy: {config.strategy}")
            
            result.phases_completed.append(DeploymentPhase.DEPLOYMENT)
            logger.info("Deployment phase completed")
            
        except Exception as e:
            logger.error(f"Deployment phase failed: {e}")
            raise
    
    async def _execute_post_deployment_phase(self, config: DeploymentConfig,
                                           result: DeploymentResult):
        """Execute post-deployment phase"""



        try:
            logger.info("Executing post-deployment phase...")
            result.current_phase = DeploymentPhase.POST_DEPLOYMENT
            
            # Start services
            await self._start_services(config)
            
            # Update load balancer
            await self._update_load_balancer(config)
            
            # Warm up caches
            await self._warm_up_caches(config)
            
            # Update monitoring
            await self._update_monitoring_configuration(config)
            
            result.phases_completed.append(DeploymentPhase.POST_DEPLOYMENT)
            logger.info("Post-deployment phase completed")
            
        except Exception as e:
            logger.error(f"Post-deployment phase failed: {e}")
            raise
    
    async def _execute_validation_phase(self, config: DeploymentConfig,
                                      result: DeploymentResult):
        """Execute validation phase"""



        try:
            logger.info("Executing validation phase...")
            result.current_phase = DeploymentPhase.VALIDATION
            
            # Health checks
            if config.enable_health_checks:
                health_results = await self._perform_health_checks(config)
                result.health_check_results = health_results
                
                if not health_results.get('all_healthy', False):
                    raise Exception("Health checks failed")
            
            # Smoke tests
            await self._run_smoke_tests(config)
            
            # Performance validation
            await self._validate_performance(config)
            
            # Security validation
            await self._validate_security(config)
            
            result.phases_completed.append(DeploymentPhase.VALIDATION)
            logger.info("Validation phase completed")
            
        except Exception as e:
            logger.error(f"Validation phase failed: {e}")
            raise
    
    async def _execute_cleanup_phase(self, config: DeploymentConfig,
                                   result: DeploymentResult):
        """Execute cleanup phase"""



        try:
            logger.info("Executing cleanup phase...")
            result.current_phase = DeploymentPhase.CLEANUP
            
            # Clean up old versions
            await self._cleanup_old_versions(config)
            
            # Clean up temporary resources
            await self._cleanup_temporary_resources(config)
            
            # Update deployment records
            await self._update_deployment_records(config, result)
            
            # Send success notification
            await self._send_deployment_notification(
                config, f"Deployment to {config.environment} completed successfully"
            )
            
            result.phases_completed.append(DeploymentPhase.CLEANUP)
            logger.info("Cleanup phase completed")
            
        except Exception as e:
            logger.error(f"Cleanup phase failed: {e}")
            # Don't fail deployment for cleanup issues
            logger.warning("Continuing despite cleanup issues")
    
    async def _execute_rollback(self, config: DeploymentConfig,
                              result: DeploymentResult):
        """Execute rollback procedure"""



        try:
            logger.info("Executing rollback...")
            result.current_phase = DeploymentPhase.ROLLBACK
            
            # Stop current deployment
            await self._stop_current_deployment(config)
            
            # Restore previous version
            await self._restore_previous_version(config)
            
            # Restore database if needed
            await self._restore_database_backup(config)
            
            # Restore configurations
            await self._restore_configurations(config)
            
            # Validate rollback
            await self._validate_rollback(config)
            
            result.rollback_performed = True
            result.status = DeploymentStatus.ROLLED_BACK
            
            # Send rollback notification
            await self._send_deployment_notification(
                config, f"Deployment to {config.environment} rolled back due to failure"
            )
            
            logger.info("Rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            # This is critical - rollback failure needs immediate attention
            await self._send_critical_alert(config, f"CRITICAL: Rollback failed - {e}")
    
    # Deployment strategy implementations
    async def _execute_rolling_deployment(self, config: DeploymentConfig,
                                        result: DeploymentResult):
        """Execute rolling deployment strategy"""
        logger.info("Executing rolling deployment...")
        
        # Implementation would include:
        # - Gradual instance replacement
        # - Health checks between batches
        # - Automatic rollback on failure
        
        # Simulate deployment
        await asyncio.sleep(2)
        result.version_deployed = config.version
    
    async def _execute_blue_green_deployment(self, config: DeploymentConfig,
                                           result: DeploymentResult):
        """Execute blue-green deployment strategy"""
        logger.info("Executing blue-green deployment...")
        
        # Implementation would include:
        # - Deploy to green environment
        # - Validate green environment
        # - Switch traffic to green
        # - Keep blue as backup
        
        # Simulate deployment
        await asyncio.sleep(3)
        result.version_deployed = config.version
    
    async def _execute_canary_deployment(self, config: DeploymentConfig,
                                       result: DeploymentResult):
        """Execute canary deployment strategy"""
        logger.info("Executing canary deployment...")
        
        # Implementation would include:
        # - Deploy to small subset of instances
        # - Monitor metrics and errors
        # - Gradually increase traffic
        # - Full rollout or rollback based on metrics
        
        # Simulate deployment
        await asyncio.sleep(4)
        result.version_deployed = config.version
    
    async def _execute_recreate_deployment(self, config: DeploymentConfig,
                                         result: DeploymentResult):
        """Execute recreate deployment strategy"""
        logger.info("Executing recreate deployment...")
        
        # Implementation would include:
        # - Stop all instances
        # - Deploy new version
        # - Start all instances
        # - Accept downtime
        
        # Simulate deployment
        await asyncio.sleep(2)
        result.version_deployed = config.version
    
    async def _execute_ab_testing_deployment(self, config: DeploymentConfig,
                                           result: DeploymentResult):
        """Execute A/B testing deployment strategy"""
        logger.info("Executing A/B testing deployment...")
        
        # Implementation would include:
        # - Deploy version B alongside version A
        # - Split traffic based on rules
        # - Collect metrics for comparison
        # - Choose winning version
        
        # Simulate deployment
        await asyncio.sleep(5)
        result.version_deployed = config.version
    
    # Helper methods
    async def _validate_deployment_config(self, config: DeploymentConfig):
        """Validate deployment configuration"""
        logger.info("Validating deployment configuration...")
        
        # Validate environment exists
        try:
            EnvironmentType(config.environment)
        except ValueError:
            raise ValueError(f"Invalid environment: {config.environment}")
        
        # Validate strategy
        if not isinstance(config.strategy, DeploymentStrategy):
            raise ValueError(f"Invalid deployment strategy: {config.strategy}")
        
        # Validate timeout
        if config.timeout_minutes <= 0:
            raise ValueError("Timeout must be positive")
    
    async def _check_deployment_prerequisites(self, config: DeploymentConfig):
        """Check deployment prerequisites"""
        logger.info("Checking deployment prerequisites...")
        
        # Check resource availability
        # Check network connectivity
        # Check permissions
        # Check maintenance windows
        
        # Simulate checks
        await asyncio.sleep(1)
    
    async def _create_pre_deployment_backup(self, config: DeploymentConfig):
        """Create pre-deployment backup"""
        logger.info("Creating pre-deployment backup...")
        
        # Implementation would create backups of:
        # - Database
        # - Configurations
        # - Application files
        # - Certificates
        
        # Simulate backup
        await asyncio.sleep(2)
    
    async def _execute_database_migrations(self, config: DeploymentConfig):
        """Execute database migrations"""
        logger.info("Executing database migrations...")
        
        # Implementation would:
        # - Run migration scripts
        # - Validate schema changes
        # - Update data if needed
        
        # Simulate migrations
        await asyncio.sleep(1)
    
    async def _update_configurations(self, config: DeploymentConfig):
        """Update configurations"""
        logger.info("Updating configurations...")
        
        # Implementation would update:
        # - Application configuration
        # - Environment variables
        # - Service configurations
        
        # Simulate configuration update
        await asyncio.sleep(1)
    
    async def _perform_security_checks(self, config: DeploymentConfig):
        """Perform security checks"""
        logger.info("Performing security checks...")
        
        # Implementation would check:
        # - Vulnerabilities
        # - Security policies
        # - Access controls
        # - Certificates
        
        # Simulate security checks
        await asyncio.sleep(1)
    
    async def _provision_resources(self, config: DeploymentConfig):
        """Provision required resources"""
        logger.info("Provisioning resources...")
        
        # Implementation would provision:
        # - Compute resources
        # - Storage
        # - Network resources
        # - Load balancers
        
        # Simulate resource provisioning
        await asyncio.sleep(2)
    
    async def _start_services(self, config: DeploymentConfig):
        """Start services"""
        logger.info("Starting services...")
        
        # Implementation would start:
        # - Application services
        # - Background workers
        # - Monitoring agents
        
        # Simulate service startup
        await asyncio.sleep(1)
    
    async def _update_load_balancer(self, config: DeploymentConfig):
        """Update load balancer configuration"""
        logger.info("Updating load balancer...")
        
        # Implementation would:
        # - Update target groups
        # - Configure health checks
        # - Update routing rules
        
        # Simulate load balancer update
        await asyncio.sleep(1)
    
    async def _warm_up_caches(self, config: DeploymentConfig):
        """Warm up caches"""
        logger.info("Warming up caches...")
        
        # Implementation would:
        # - Preload cache with critical data
        # - Prime CDN caches
        # - Initialize application caches
        
        # Simulate cache warm-up
        await asyncio.sleep(1)
    
    async def _update_monitoring_configuration(self, config: DeploymentConfig):
        """Update monitoring configuration"""
        logger.info("Updating monitoring configuration...")
        
        # Implementation would:
        # - Update metrics collection
        # - Configure alerts
        # - Update dashboards
        
        # Simulate monitoring update
        await asyncio.sleep(1)
    
    async def _perform_health_checks(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Perform health checks"""
        logger.info("Performing health checks...")
        
        # Implementation would check:
        # - Service health endpoints
        # - Database connectivity
        # - External dependencies
        # - Performance metrics
        
        # Simulate health checks
        await asyncio.sleep(2)
        
        return {
            'all_healthy': True,
            'services': {
                'api': {'status': 'healthy', 'response_time_ms': 150},
                'database': {'status': 'healthy', 'connections': 45},
                'cache': {'status': 'healthy', 'hit_rate': 95}
            }
        }
    
    async def _run_smoke_tests(self, config: DeploymentConfig):
        """Run smoke tests"""
        logger.info("Running smoke tests...")
        
        # Implementation would run:
        # - Basic functionality tests
        # - API endpoint tests
        # - Database connectivity tests
        # - Integration tests
        
        # Simulate smoke tests
        await asyncio.sleep(2)
    
    async def _validate_performance(self, config: DeploymentConfig):
        """Validate performance"""
        logger.info("Validating performance...")
        
        # Implementation would check:
        # - Response times
        # - Throughput
        # - Resource utilization
        # - Error rates
        
        # Simulate performance validation
        await asyncio.sleep(1)
    
    async def _validate_security(self, config: DeploymentConfig):
        """Validate security"""
        logger.info("Validating security...")
        
        # Implementation would check:
        # - Security configurations
        # - Access controls
        # - Encryption
        # - Vulnerability scans
        
        # Simulate security validation
        await asyncio.sleep(1)
    
    async def _cleanup_old_versions(self, config: DeploymentConfig):
        """Clean up old versions"""
        logger.info("Cleaning up old versions...")
        
        # Implementation would:
        # - Remove old application versions
        # - Clean up old containers
        # - Remove unused resources
        
        # Simulate cleanup
        await asyncio.sleep(1)
    
    async def _cleanup_temporary_resources(self, config: DeploymentConfig):
        """Clean up temporary resources"""
        logger.info("Cleaning up temporary resources...")
        
        # Implementation would clean:
        # - Temporary files
        # - Build artifacts
        # - Staging resources
        
        # Simulate cleanup
        await asyncio.sleep(1)
    
    async def _update_deployment_records(self, config: DeploymentConfig,
                                       result: DeploymentResult):
        """Update deployment records"""
        logger.info("Updating deployment records...")
        
        # Implementation would:
        # - Log deployment to database
        # - Update version tracking
        # - Record metrics
        
        # Simulate record update
        await asyncio.sleep(1)
    
    async def _send_deployment_notification(self, config: DeploymentConfig, message: str):
        """Send deployment notification"""
        logger.info(f"Sending notification: {message}")
        
        # Implementation would send notifications via:
        # - Slack
        # - Email
        # - PagerDuty
        # - Microsoft Teams
        
        # Simulate notification
        await asyncio.sleep(0.5)
    
    async def _send_critical_alert(self, config: DeploymentConfig, message: str):
        """Send critical alert"""
        logger.critical(f"CRITICAL ALERT: {message}")
        
        # Implementation would send immediate alerts via:
        # - PagerDuty
        # - SMS
        # - Phone calls
        # - Multiple channels
        
        # Simulate critical alert
        await asyncio.sleep(0.5)
    
    # Rollback helper methods
    async def _stop_current_deployment(self, config: DeploymentConfig):
        """Stop current deployment"""
        logger.info("Stopping current deployment...")
        await asyncio.sleep(1)
    
    async def _restore_previous_version(self, config: DeploymentConfig):
        """Restore previous version"""
        logger.info("Restoring previous version...")
        await asyncio.sleep(2)
    
    async def _restore_database_backup(self, config: DeploymentConfig):
        """Restore database backup"""
        logger.info("Restoring database backup...")
        await asyncio.sleep(3)
    
    async def _restore_configurations(self, config: DeploymentConfig):
        """Restore configurations"""
        logger.info("Restoring configurations...")
        await asyncio.sleep(1)
    
    async def _validate_rollback(self, config: DeploymentConfig):
        """Validate rollback"""
        logger.info("Validating rollback...")
        await asyncio.sleep(1)
    
    def _generate_deployment_id(self) -> str:
        """Generate unique deployment ID"""
        from uuid import uuid4
        return f"deploy-{uuid4().hex[:8]}"
    
    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get deployment status"""



        return self.active_deployments.get(deployment_id)
    
    def list_active_deployments(self) -> List[DeploymentResult]:
        """List active deployments"""



        return list(self.active_deployments.values())


async def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='IA Influencer Agent Deployment Orchestrator')
    parser.add_argument(
        'environment',
        help='Target environment for deployment',
        choices=[env.value for env in EnvironmentType]
    )
    parser.add_argument(
        '--strategy',
        choices=[strategy.value for strategy in DeploymentStrategy],
        default='rolling',
        help='Deployment strategy'
    )
    parser.add_argument(
        '--version',
        default='latest',
        help='Version to deploy'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    parser.add_argument(
        '--no-health-checks',
        action='store_true',
        help='Skip health checks'
    )
    parser.add_argument(
        '--no-rollback',
        action='store_true',
        help='Disable automatic rollback'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Deployment timeout in minutes'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without actual deployment'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'yaml', 'text'],
        default='text',
        help='Output format for results'
    )
    
    args = parser.parse_args()
    
    try:
        # Create deployment configuration
        config = DeploymentConfig(
            environment=args.environment,
            strategy=DeploymentStrategy(args.strategy),
            version=args.version,
            enable_backup=not args.no_backup,
            enable_health_checks=not args.no_health_checks,
            enable_rollback=not args.no_rollback,
            timeout_minutes=args.timeout
        )
        
        orchestrator = DeploymentOrchestrator()
        
        if args.dry_run:
            logger.info("Performing dry run...")
            # Validate configuration without executing
            await orchestrator._validate_deployment_config(config)
            print("Dry run completed successfully")
            sys.exit(0)
        
        # Execute deployment
        result = await orchestrator.deploy(config)
        
        # Output results
        if args.output_format == 'json':
            output = json.dumps({
                'deployment_id': result.deployment_id,
                'status': result.status.value,
                'environment': result.environment,
                'duration_seconds': result.duration_seconds,
                'phases_completed': [phase.value for phase in result.phases_completed]
            }, indent=2)
        elif args.output_format == 'yaml':
            output = yaml.dump({
                'deployment_id': result.deployment_id,
                'status': result.status.value,
                'environment': result.environment,
                'duration_seconds': result.duration_seconds
            })
        else:
            output = f"""
Deployment Results:
==================
Deployment ID: {result.deployment_id}
Environment: {result.environment}
Status: {result.status.value}
Duration: {result.duration_seconds:.2f}s
Phases Completed: {', '.join([phase.value for phase in result.phases_completed])}
"""
        
        print(output)
        
        # Exit with appropriate code
        if result.status in [DeploymentStatus.SUCCESS]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
