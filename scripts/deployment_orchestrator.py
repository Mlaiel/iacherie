"""
Deployment Orchestrator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Deployment Orchestration Engine - Enterprise Grade
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced deployment orchestration for Ainflue Platform with enterprise features:
- Multi-environment deployment management
- Blue-green deployment support
- Rollback capabilities
- Health checks and validation
- Audit logging and monitoring
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
import docker
import requests
from dataclasses import dataclass, asdict

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Enterprise deployment configuration"""
    environment: str
    version: str
    namespace: str
    replicas: int
    resources: Dict[str, Any]
    health_check_url: str
    rollback_enabled: bool = True
    blue_green_enabled: bool = False
    pre_deploy_hooks: List[str] = None
    post_deploy_hooks: List[str] = None

class DeploymentOrchestrator:
    """
    Enterprise deployment orchestration system
    
    Features:
    - Multi-environment deployment
    - Blue-green deployment strategy
    - Automated rollback on failure
    - Health monitoring and validation
    - Comprehensive audit logging
    """
    
    def __init__(self, config_path -> None: str = "/etc/ainflue/deployment.yaml") -> None:
        self.config_path = config_path
        self.docker_client = docker.from_env()
        self.deployment_history: List[Dict] = []
        self.current_deployment: Optional[Dict] = None
        
    async def load_configuration(self) -> Dict[str, DeploymentConfig]:
        """Load deployment configurations for all environments"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            configurations = {}
            for env_name, env_config in config_data.get('environments', {}).items():
                configurations[env_name] = DeploymentConfig(**env_config)
            
            logger.info(f"Loaded configurations for {len(configurations)} environments")
            return configurations
            
        except Exception as e:
            logger.error(f"Failed to load deployment configuration: {e}")
            raise
    
    async def validate_environment(self, config: DeploymentConfig) -> bool:
        """Validate deployment environment prerequisites"""
        try:
            # Check Kubernetes cluster connectivity
            result = subprocess.run(
                ["kubectl", "cluster-info", "--request-timeout=10s"],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode != 0:
                logger.error("Kubernetes cluster not accessible")
                return False
            
            # Check namespace existence
            result = subprocess.run(
                ["kubectl", "get", "namespace", config.namespace],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                logger.info(f"Creating namespace: {config.namespace}")
                subprocess.run([
                    "kubectl", "create", "namespace", config.namespace
                ], check=True)
            
            # Validate Docker registry access
            try:
                self.docker_client.images.list()
                logger.info("Docker registry accessible")
            except Exception as e:
                logger.error(f"Docker registry access failed: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return False
    
    async def execute_hooks(self, hooks: List[str], stage: str) -> bool:
        """Execute pre/post deployment hooks"""
        if not hooks:
            return True
            
        logger.info(f"Executing {stage} hooks")
        
        for hook in hooks:
            try:
                result = subprocess.run(
                    hook.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
                
                if result.returncode != 0:
                    logger.error(f"Hook failed: {hook} - {result.stderr}")
                    return False
                    
                logger.info(f"Hook completed: {hook}")
                
            except subprocess.TimeoutExpired:
                logger.error(f"Hook timeout: {hook}")
                return False
            except Exception as e:
                logger.error(f"Hook execution error: {hook} - {e}")
                return False
        
        return True
    
    async def deploy_blue_green(self, config: DeploymentConfig) -> bool:
        """Execute blue-green deployment strategy"""
        try:
            logger.info("Starting blue-green deployment")
            
            # Determine current and target environments
            current_env = "blue" if await self._is_active_environment("green", config) else "green"
            target_env = "green" if current_env == "blue" else "blue"
            
            logger.info(f"Deploying to {target_env} environment")
            
            # Deploy to target environment
            deployment_success = await self._deploy_to_environment(target_env, config)
            
            if not deployment_success:
                logger.error(f"Deployment to {target_env} failed")
                return False
            
            # Health check on target environment
            if not await self._health_check(target_env, config):
                logger.error(f"Health check failed for {target_env}")
                await self._cleanup_environment(target_env, config)
                return False
            
            # Switch traffic to target environment
            if not await self._switch_traffic(target_env, config):
                logger.error("Traffic switch failed")
                return False
            
            # Cleanup old environment
            await self._cleanup_environment(current_env, config)
            
            logger.info(f"Blue-green deployment completed successfully to {target_env}")
            return True
            
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            return False
    
    async def deploy_standard(self, config: DeploymentConfig) -> bool:
        """Execute standard rolling deployment"""
        try:
            logger.info("Starting standard deployment")
            
            # Build and push new images
            if not await self._build_and_push_images(config):
                return False
            
            # Update Kubernetes deployments
            if not await self._update_k8s_deployments(config):
                return False
            
            # Wait for rollout completion
            if not await self._wait_for_rollout(config):
                return False
            
            # Perform health checks
            if not await self._health_check("default", config):
                logger.error("Post-deployment health check failed")
                if config.rollback_enabled:
                    await self.rollback_deployment(config)
                return False
            
            logger.info("Standard deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Standard deployment failed: {e}")
            return False
    
    async def rollback_deployment(self, config: DeploymentConfig) -> bool:
        """Rollback to previous deployment version"""
        try:
            logger.warning("Initiating deployment rollback")
            
            if not self.deployment_history:
                logger.error("No previous deployment found for rollback")
                return False
            
            previous_deployment = self.deployment_history[-1]
            previous_version = previous_deployment.get('version')
            
            if not previous_version:
                logger.error("Previous deployment version not found")
                return False
            
            # Create rollback configuration
            rollback_config = DeploymentConfig(
                environment=config.environment,
                version=previous_version,
                namespace=config.namespace,
                replicas=config.replicas,
                resources=config.resources,
                health_check_url=config.health_check_url,
                rollback_enabled=False  # Prevent rollback loops
            )
            
            # Execute rollback deployment
            success = await self.deploy_standard(rollback_config)
            
            if success:
                logger.info(f"Rollback to version {previous_version} completed")
            else:
                logger.error("Rollback deployment failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def _build_and_push_images(self, config: DeploymentConfig) -> bool:
        """Build and push Docker images"""
        try:
            logger.info("Building and pushing Docker images")
            
            # Build main application image
            image_tag = f"ainflue/platform:{config.version}"
            
            result = subprocess.run([
                "docker", "build", 
                "-t", image_tag,
                "-f", "Dockerfile",
                "."
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Docker build failed: {result.stderr}")
                return False
            
            # Push to registry
            result = subprocess.run([
                "docker", "push", image_tag
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Docker push failed: {result.stderr}")
                return False
            
            logger.info(f"Image {image_tag} built and pushed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Image build/push failed: {e}")
            return False
    
    async def _update_k8s_deployments(self, config: DeploymentConfig) -> bool:
        """Update Kubernetes deployments"""
        try:
            logger.info("Updating Kubernetes deployments")
            
            # Update deployment image
            result = subprocess.run([
                "kubectl", "set", "image",
                f"deployment/ainflue-platform",
                f"platform=ainflue/platform:{config.version}",
                f"--namespace={config.namespace}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Kubernetes deployment update failed: {result.stderr}")
                return False
            
            # Scale deployment if needed
            result = subprocess.run([
                "kubectl", "scale",
                f"deployment/ainflue-platform",
                f"--replicas={config.replicas}",
                f"--namespace={config.namespace}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Kubernetes scaling failed: {result.stderr}")
                return False
            
            logger.info("Kubernetes deployments updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Kubernetes update failed: {e}")
            return False
    
    async def _wait_for_rollout(self, config: DeploymentConfig, timeout: int = 600) -> bool:
        """Wait for Kubernetes deployment rollout to complete"""
        try:
            logger.info("Waiting for rollout completion")
            
            result = subprocess.run([
                "kubectl", "rollout", "status",
                f"deployment/ainflue-platform",
                f"--namespace={config.namespace}",
                f"--timeout={timeout}s"
            ], capture_output=True, text=True, timeout=timeout + 30)
            
            if result.returncode != 0:
                logger.error(f"Rollout failed: {result.stderr}")
                return False
            
            logger.info("Rollout completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollout wait failed: {e}")
            return False
    
    async def _health_check(self, environment: str, config: DeploymentConfig) -> bool:
        """Perform comprehensive health checks"""
        try:
            logger.info(f"Performing health check for {environment}")
            
            # Wait for services to be ready
            await asyncio.sleep(30)
            
            # Check service endpoints
            max_retries = 10
            retry_delay = 30
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        config.health_check_url,
                        timeout=10,
                        headers={'User-Agent': 'Ainflue-Deployment-Orchestrator'}
                    )
                    
                    if response.status_code == 200:
                        logger.info("Health check passed")
                        return True
                    
                    logger.warning(f"Health check attempt {attempt + 1} failed: {response.status_code}")
                    
                except requests.RequestException as e:
                    logger.warning(f"Health check attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
            
            logger.error("All health check attempts failed")
            return False
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def _is_active_environment(self, environment: str, config: DeploymentConfig) -> bool:
        """Check if environment is currently active"""
        try:
            result = subprocess.run([
                "kubectl", "get", "service",
                "ainflue-platform-service",
                f"--namespace={config.namespace}",
                "-o", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                service_data = json.loads(result.stdout)
                selector = service_data.get('spec', {}).get('selector', {})
                return selector.get('environment') == environment
            
            return False
            
        except Exception:
            return False
    
    async def _deploy_to_environment(self, environment: str, config: DeploymentConfig) -> bool:
        """Deploy to specific environment"""
        try:
            # Implementation would include environment-specific deployment logic
            logger.info(f"Deploying to {environment} environment")
            
            # This would include the actual deployment steps
            # For now, simulate deployment
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Environment deployment failed: {e}")
            return False
    
    async def _switch_traffic(self, target_environment: str, config: DeploymentConfig) -> bool:
        """Switch traffic to target environment"""
        try:
            logger.info(f"Switching traffic to {target_environment}")
            
            # Update service selector to point to new environment
            result = subprocess.run([
                "kubectl", "patch", "service",
                "ainflue-platform-service",
                f"--namespace={config.namespace}",
                "-p", f'{{"spec":{{"selector":{{"environment":"{target_environment}"}}}}}}'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Traffic switch failed: {result.stderr}")
                return False
            
            logger.info("Traffic switched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Traffic switch failed: {e}")
            return False
    
    async def _cleanup_environment(self, environment: str, config: DeploymentConfig) -> bool:
        """Cleanup old environment"""
        try:
            logger.info(f"Cleaning up {environment} environment")
            
            # Scale down old deployment
            result = subprocess.run([
                "kubectl", "scale",
                f"deployment/ainflue-platform-{environment}",
                "--replicas=0",
                f"--namespace={config.namespace}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Cleanup scaling failed: {result.stderr}")
            
            logger.info(f"Environment {environment} cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"Environment cleanup failed: {e}")
            return False
    
    async def orchestrate_deployment(self, environment: str, version: str) -> bool:
        """Main orchestration entry point"""
        try:
            start_time = datetime.now()
            logger.info(f"Starting deployment orchestration for {environment} v{version}")
            
            # Load configurations
            configurations = await self.load_configuration()
            
            if environment not in configurations:
                logger.error(f"Environment {environment} not found in configuration")
                return False
            
            config = configurations[environment]
            config.version = version
            
            # Validate environment
            if not await self.validate_environment(config):
                return False
            
            # Execute pre-deployment hooks
            if not await self.execute_hooks(config.pre_deploy_hooks or [], "pre-deployment"):
                return False
            
            # Choose deployment strategy
            if config.blue_green_enabled:
                deployment_success = await self.deploy_blue_green(config)
            else:
                deployment_success = await self.deploy_standard(config)
            
            if deployment_success:
                # Execute post-deployment hooks
                await self.execute_hooks(config.post_deploy_hooks or [], "post-deployment")
                
                # Record successful deployment
                deployment_record = {
                    'environment': environment,
                    'version': version,
                    'timestamp': start_time.isoformat(),
                    'duration': (datetime.now() - start_time).total_seconds(),
                    'status': 'success'
                }
                
                self.deployment_history.append(deployment_record)
                self.current_deployment = deployment_record
                
                logger.info(f"Deployment orchestration completed successfully in {deployment_record['duration']:.2f}s")
            
            return deployment_success
            
        except Exception as e:
            logger.error(f"Deployment orchestration failed: {e}")
            return False

async def main() -> None:
    """CLI entry point for deployment orchestration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Deployment Orchestrator')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--version', required=True, help='Version to deploy')
    parser.add_argument('--config', default='/etc/ainflue/deployment.yaml', help='Configuration file path')
    parser.add_argument('--rollback', action='store_true', help='Rollback to previous version')
    
    args = parser.parse_args()
    
    orchestrator = DeploymentOrchestrator(args.config)
    
    if args.rollback:
        configurations = await orchestrator.load_configuration()
        config = configurations.get(args.environment)
        if config:
            success = await orchestrator.rollback_deployment(config)
        else:
            logger.error(f"Environment {args.environment} not found")
            success = False
    else:
        success = await orchestrator.orchestrate_deployment(args.environment, args.version)
    
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())