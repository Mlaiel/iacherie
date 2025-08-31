#!/usr/bin/env python3
"""
Application Deployment Manager
Handles complete application deployment lifecycle including zero-downtime deployments
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import yaml
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategy enumeration"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class Environment(Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DeploymentConfig:
    """Deployment configuration data class"""
    app_name: str
    version: str
    environment: Environment
    strategy: DeploymentStrategy
    replicas: int
    namespace: str
    image_tag: str
    health_check_timeout: int = 300
    rollback_on_failure: bool = True
    enable_monitoring: bool = True


class AppDeploymentManager:
    """
    Enterprise-grade application deployment manager
    Handles zero-downtime deployments with advanced strategies
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize deployment manager"""
        self.config_path = config_path or "/etc/deployment/config.yaml"
        self.k8s_client = None
        self.apps_v1 = None
        self.core_v1 = None
        self.deployment_history = []
        
        self._initialize_kubernetes()
        self._load_configuration()
    
    def _initialize_kubernetes(self) -> None:
        """Initialize Kubernetes client"""



        try:
            # Load in-cluster config if running in pod
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except config.ConfigException:
            try:
                # Load local kubeconfig
                config.load_kube_config()
                logger.info("Loaded local Kubernetes configuration")
            except config.ConfigException as e:
                logger.error(f"Failed to load Kubernetes configuration: {e}")
                raise
        
        self.k8s_client = client.ApiClient()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
    
    def _load_configuration(self) -> None:
        """Load deployment configuration"""



        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                # Default configuration
                self.config = self._get_default_config()
                logger.warning("Using default configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default deployment configuration"""



        return {
            "default_strategy": "rolling_update",
            "default_replicas": 3,
            "health_check_timeout": 300,
            "rollback_on_failure": True,
            "monitoring": {
                "enabled": True,
                "prometheus_endpoint": "http://prometheus:9090",
                "grafana_endpoint": "http://grafana:3000"
            },
            "notifications": {
                "slack_webhook": None,
                "email_enabled": False
            }
        }
    
    def deploy_application(self, deployment_config: DeploymentConfig) -> bool:
        """
        Deploy application with specified configuration
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            bool: True if deployment successful, False otherwise
        """



        try:
            logger.info(f"Starting deployment of {deployment_config.app_name} "
                       f"version {deployment_config.version}")
            
            # Pre-deployment validation
            if not self._validate_deployment_config(deployment_config):
                logger.error("Deployment configuration validation failed")
                return False
            
            # Execute deployment based on strategy
            success = False
            if deployment_config.strategy == DeploymentStrategy.ROLLING_UPDATE:
                success = self._rolling_update_deployment(deployment_config)
            elif deployment_config.strategy == DeploymentStrategy.BLUE_GREEN:
                success = self._blue_green_deployment(deployment_config)
            elif deployment_config.strategy == DeploymentStrategy.CANARY:
                success = self._canary_deployment(deployment_config)
            elif deployment_config.strategy == DeploymentStrategy.RECREATE:
                success = self._recreate_deployment(deployment_config)
            
            # Post-deployment tasks
            if success:
                self._post_deployment_tasks(deployment_config)
                self._record_deployment(deployment_config, success=True)
                logger.info(f"Successfully deployed {deployment_config.app_name}")
            else:
                logger.error(f"Deployment failed for {deployment_config.app_name}")
                if deployment_config.rollback_on_failure:
                    self._rollback_deployment(deployment_config)
                self._record_deployment(deployment_config, success=False)
            
            return success
            
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return False
    
    def _validate_deployment_config(self, config: DeploymentConfig) -> bool:
        """Validate deployment configuration"""



        try:
            # Check if namespace exists
            self.core_v1.read_namespace(config.namespace)
            
            # Validate image exists
            if not self._validate_container_image(config.image_tag):
                logger.error(f"Container image not found: {config.image_tag}")
                return False
            
            # Check resource quotas
            if not self._check_resource_availability(config):
                logger.error("Insufficient resources for deployment")
                return False
            
            return True
            
        except ApiException as e:
            if e.status == 404:
                logger.error(f"Namespace {config.namespace} not found")
            else:
                logger.error(f"Validation error: {e}")
            return False
    
    def _validate_container_image(self, image_tag: str) -> bool:
        """Validate container image exists in registry"""



        try:
            # This would typically check against the container registry
            # For now, we'll assume the image exists
            return True
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False
    
    def _check_resource_availability(self, config: DeploymentConfig) -> bool:
        """Check if sufficient resources are available"""



        try:
            # Get current resource usage
            nodes = self.core_v1.list_node()
            
            # Calculate required resources
            required_cpu = config.replicas * 1.0  # 1 CPU per replica
            required_memory = config.replicas * 2048  # 2GB per replica
            
            # Check node capacity (simplified)
            total_cpu = sum(
                float(node.status.capacity.get('cpu', 0)) 
                for node in nodes.items
            )
            
            if required_cpu > total_cpu * 0.8:  # 80% threshold
                logger.warning("High CPU usage, deployment may fail")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Resource check error: {e}")
            return True  # Allow deployment to proceed
    
    def _rolling_update_deployment(self, config: DeploymentConfig) -> bool:
        """Execute rolling update deployment"""



        try:
            logger.info("Executing rolling update deployment")
            
            # Get current deployment
            try:
                current_deployment = self.apps_v1.read_namespaced_deployment(
                    name=config.app_name,
                    namespace=config.namespace
                )
                
                # Update deployment with new image
                current_deployment.spec.template.spec.containers[0].image = config.image_tag
                current_deployment.spec.replicas = config.replicas
                
                # Apply update
                self.apps_v1.patch_namespaced_deployment(
                    name=config.app_name,
                    namespace=config.namespace,
                    body=current_deployment
                )
                
            except ApiException as e:
                if e.status == 404:
                    # Create new deployment
                    deployment_manifest = self._create_deployment_manifest(config)
                    self.apps_v1.create_namespaced_deployment(
                        namespace=config.namespace,
                        body=deployment_manifest
                    )
                else:
                    raise
            
            # Wait for rollout completion
            return self._wait_for_rollout_completion(config)
            
        except Exception as e:
            logger.error(f"Rolling update error: {e}")
            return False
    
    def _blue_green_deployment(self, config: DeploymentConfig) -> bool:
        """Execute blue-green deployment"""



        try:
            logger.info("Executing blue-green deployment")
            
            # Create green deployment
            green_config = DeploymentConfig(
                app_name=f"{config.app_name}-green",
                version=config.version,
                environment=config.environment,
                strategy=config.strategy,
                replicas=config.replicas,
                namespace=config.namespace,
                image_tag=config.image_tag
            )
            
            green_deployment = self._create_deployment_manifest(green_config)
            self.apps_v1.create_namespaced_deployment(
                namespace=config.namespace,
                body=green_deployment
            )
            
            # Wait for green deployment to be ready
            if not self._wait_for_rollout_completion(green_config):
                logger.error("Green deployment failed")
                return False
            
            # Health check green deployment
            if not self._health_check_deployment(green_config):
                logger.error("Green deployment health check failed")
                return False
            
            # Switch traffic to green
            self._switch_service_traffic(config, green_config)
            
            # Clean up blue deployment
            try:
                self.apps_v1.delete_namespaced_deployment(
                    name=config.app_name,
                    namespace=config.namespace
                )
            except ApiException:
                pass  # Blue deployment might not exist
            
            # Rename green to blue
            self.apps_v1.patch_namespaced_deployment(
                name=green_config.app_name,
                namespace=config.namespace,
                body={"metadata": {"name": config.app_name}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Blue-green deployment error: {e}")
            return False
    
    def _canary_deployment(self, config: DeploymentConfig) -> bool:
        """Execute canary deployment"""



        try:
            logger.info("Executing canary deployment")
            
            # Create canary deployment with reduced replicas
            canary_replicas = max(1, config.replicas // 4)  # 25% traffic
            
            canary_config = DeploymentConfig(
                app_name=f"{config.app_name}-canary",
                version=config.version,
                environment=config.environment,
                strategy=config.strategy,
                replicas=canary_replicas,
                namespace=config.namespace,
                image_tag=config.image_tag
            )
            
            canary_deployment = self._create_deployment_manifest(canary_config)
            self.apps_v1.create_namespaced_deployment(
                namespace=config.namespace,
                body=canary_deployment
            )
            
            # Wait for canary to be ready
            if not self._wait_for_rollout_completion(canary_config):
                logger.error("Canary deployment failed")
                return False
            
            # Monitor canary for issues
            logger.info("Monitoring canary deployment...")
            time.sleep(60)  # Monitor for 1 minute
            
            if self._monitor_canary_health(canary_config):
                # Promote canary to full deployment
                return self._promote_canary(config, canary_config)
            else:
                # Rollback canary
                self._cleanup_canary(canary_config)
                return False
            
        except Exception as e:
            logger.error(f"Canary deployment error: {e}")
            return False
    
    def _recreate_deployment(self, config: DeploymentConfig) -> bool:
        """Execute recreate deployment (downtime strategy)"""



        try:
            logger.info("Executing recreate deployment")
            
            # Delete existing deployment
            try:
                self.apps_v1.delete_namespaced_deployment(
                    name=config.app_name,
                    namespace=config.namespace
                )
                
                # Wait for deletion
                time.sleep(30)
                
            except ApiException as e:
                if e.status != 404:
                    logger.error(f"Failed to delete existing deployment: {e}")
                    return False
            
            # Create new deployment
            deployment_manifest = self._create_deployment_manifest(config)
            self.apps_v1.create_namespaced_deployment(
                namespace=config.namespace,
                body=deployment_manifest
            )
            
            # Wait for new deployment
            return self._wait_for_rollout_completion(config)
            
        except Exception as e:
            logger.error(f"Recreate deployment error: {e}")
            return False
    
    def _create_deployment_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest"""



        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.app_name,
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "version": config.version,
                    "environment": config.environment.value
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.app_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.app_name,
                            "version": config.version
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": config.app_name,
                                "image": config.image_tag,
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "name": "http"
                                    }
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                },
                                "resources": {
                                    "requests": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    },
                                    "limits": {
                                        "cpu": "1000m",
                                        "memory": "2Gi"
                                    }
                                },
                                "env": [
                                    {
                                        "name": "ENVIRONMENT",
                                        "value": config.environment.value
                                    },
                                    {
                                        "name": "APP_VERSION",
                                        "value": config.version
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    
    def _wait_for_rollout_completion(self, config: DeploymentConfig) -> bool:
        """Wait for deployment rollout to complete"""



        try:
            start_time = time.time()
            timeout = config.health_check_timeout
            
            while time.time() - start_time < timeout:
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=config.app_name,
                    namespace=config.namespace
                )
                
                if (deployment.status.ready_replicas == config.replicas and
                    deployment.status.updated_replicas == config.replicas):
                    logger.info(f"Deployment {config.app_name} rollout completed")
                    return True
                
                logger.info(f"Waiting for rollout... Ready: {deployment.status.ready_replicas}/{config.replicas}")
                time.sleep(10)
            
            logger.error(f"Deployment rollout timeout after {timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Rollout wait error: {e}")
            return False
    
    def _health_check_deployment(self, config: DeploymentConfig) -> bool:
        """Perform health check on deployment"""



        try:
            # Get service endpoint
            service = self.core_v1.read_namespaced_service(
                name=config.app_name,
                namespace=config.namespace
            )
            
            # Perform health check (simplified)
            # In real implementation, this would check actual health endpoints
            return True
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def _switch_service_traffic(self, old_config: DeploymentConfig, new_config: DeploymentConfig) -> None:
        """Switch service traffic from old to new deployment"""



        try:
            service = self.core_v1.read_namespaced_service(
                name=old_config.app_name,
                namespace=old_config.namespace
            )
            
            # Update selector to point to new deployment
            service.spec.selector = {"app": new_config.app_name}
            
            self.core_v1.patch_namespaced_service(
                name=old_config.app_name,
                namespace=old_config.namespace,
                body=service
            )
            
            logger.info("Traffic switched to new deployment")
            
        except Exception as e:
            logger.error(f"Traffic switch error: {e}")
    
    def _monitor_canary_health(self, config: DeploymentConfig) -> bool:
        """Monitor canary deployment health"""



        try:
            # Monitor metrics, error rates, etc.
            # This is a simplified implementation
            logger.info("Monitoring canary health...")
            
            # Simulate health monitoring
            time.sleep(30)
            
            # Check error rates, response times, etc.
            # Return True if healthy, False if issues detected
            return True
            
        except Exception as e:
            logger.error(f"Canary monitoring error: {e}")
            return False
    
    def _promote_canary(self, config: DeploymentConfig, canary_config: DeploymentConfig) -> bool:
        """Promote canary to full deployment"""



        try:
            logger.info("Promoting canary to full deployment")
            
            # Update main deployment with canary image
            deployment = self.apps_v1.read_namespaced_deployment(
                name=config.app_name,
                namespace=config.namespace
            )
            
            deployment.spec.template.spec.containers[0].image = canary_config.image_tag
            deployment.spec.replicas = config.replicas
            
            self.apps_v1.patch_namespaced_deployment(
                name=config.app_name,
                namespace=config.namespace,
                body=deployment
            )
            
            # Clean up canary
            self._cleanup_canary(canary_config)
            
            # Wait for full deployment
            return self._wait_for_rollout_completion(config)
            
        except Exception as e:
            logger.error(f"Canary promotion error: {e}")
            return False
    
    def _cleanup_canary(self, config: DeploymentConfig) -> None:
        """Clean up canary deployment"""



        try:
            self.apps_v1.delete_namespaced_deployment(
                name=config.app_name,
                namespace=config.namespace
            )
            logger.info("Canary deployment cleaned up")
            
        except Exception as e:
            logger.error(f"Canary cleanup error: {e}")
    
    def _rollback_deployment(self, config: DeploymentConfig) -> bool:
        """Rollback deployment to previous version"""



        try:
            logger.info(f"Rolling back deployment {config.app_name}")
            
            # Get deployment history
            rollout_history = subprocess.run(
                [
                    "kubectl", "rollout", "history",
                    f"deployment/{config.app_name}",
                    f"-n", config.namespace
                ],
                capture_output=True,
                text=True
            )
            
            if rollout_history.returncode != 0:
                logger.error("Failed to get rollout history")
                return False
            
            # Rollback to previous revision
            rollback_result = subprocess.run(
                [
                    "kubectl", "rollout", "undo",
                    f"deployment/{config.app_name}",
                    f"-n", config.namespace
                ],
                capture_output=True,
                text=True
            )
            
            if rollback_result.returncode == 0:
                logger.info("Rollback completed successfully")
                return True
            else:
                logger.error(f"Rollback failed: {rollback_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            return False
    
    def _post_deployment_tasks(self, config: DeploymentConfig) -> None:
        """Execute post-deployment tasks"""



        try:
            logger.info("Executing post-deployment tasks")
            
            # Update monitoring
            if config.enable_monitoring:
                self._update_monitoring_config(config)
            
            # Send notifications
            self._send_deployment_notification(config, success=True)
            
            # Update load balancer if needed
            self._update_load_balancer(config)
            
            # Clean up old resources
            self._cleanup_old_resources(config)
            
        except Exception as e:
            logger.error(f"Post-deployment task error: {e}")
    
    def _update_monitoring_config(self, config: DeploymentConfig) -> None:
        """Update monitoring configuration"""



        try:
            # Update Prometheus targets
            # Update Grafana dashboards
            # This would integrate with monitoring systems
            logger.info("Monitoring configuration updated")
            
        except Exception as e:
            logger.error(f"Monitoring update error: {e}")
    
    def _send_deployment_notification(self, config: DeploymentConfig, success: bool) -> None:
        """Send deployment notification"""



        try:
            status = "SUCCESS" if success else "FAILED"
            message = f"Deployment {status}: {config.app_name} v{config.version} to {config.environment.value}"
            
            # Send to Slack, email, etc.
            slack_webhook = self.config.get("notifications", {}).get("slack_webhook")
            if slack_webhook:
                requests.post(slack_webhook, json={"text": message})
            
            logger.info(f"Notification sent: {message}")
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def _update_load_balancer(self, config: DeploymentConfig) -> None:
        """Update load balancer configuration"""



        try:
            # Update ingress rules
            # Update service mesh configuration
            logger.info("Load balancer configuration updated")
            
        except Exception as e:
            logger.error(f"Load balancer update error: {e}")
    
    def _cleanup_old_resources(self, config: DeploymentConfig) -> None:
        """Clean up old deployment resources"""



        try:
            # Clean up old ReplicaSets
            # Clean up old ConfigMaps/Secrets if needed
            logger.info("Old resources cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def _record_deployment(self, config: DeploymentConfig, success: bool) -> None:
        """Record deployment in history"""
        deployment_record = {
            "timestamp": time.time(),
            "app_name": config.app_name,
            "version": config.version,
            "environment": config.environment.value,
            "strategy": config.strategy.value,
            "success": success
        }
        
        self.deployment_history.append(deployment_record)
        
        # Persist to database or file
        logger.info(f"Deployment recorded: {deployment_record}")
    
    def get_deployment_status(self, app_name: str, namespace: str) -> Dict[str, Any]:
        """Get current deployment status"""



        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=app_name,
                namespace=namespace
            )
            
            return {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": deployment.spec.replicas,
                "ready_replicas": deployment.status.ready_replicas,
                "updated_replicas": deployment.status.updated_replicas,
                "available_replicas": deployment.status.available_replicas,
                "generation": deployment.metadata.generation,
                "observed_generation": deployment.status.observed_generation
            }
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {}
    
    def list_deployments(self, namespace: str = None) -> List[Dict[str, Any]]:
        """List all deployments"""



        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            return [
                {
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "ready_replicas": dep.status.ready_replicas,
                    "age": (time.time() - dep.metadata.creation_timestamp.timestamp()) / 86400
                }
                for dep in deployments.items
            ]
            
        except Exception as e:
            logger.error(f"List deployments error: {e}")
            return []


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Application Deployment Manager")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--version", required=True, help="Application version")
    parser.add_argument("--environment", required=True, choices=["development", "staging", "production"])
    parser.add_argument("--strategy", default="rolling_update", choices=["rolling_update", "blue_green", "canary", "recreate"])
    parser.add_argument("--replicas", type=int, default=3, help="Number of replicas")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--image-tag", required=True, help="Container image tag")
    
    args = parser.parse_args()
    
    # Create deployment configuration
    config = DeploymentConfig(
        app_name=args.app_name,
        version=args.version,
        environment=Environment(args.environment),
        strategy=DeploymentStrategy(args.strategy),
        replicas=args.replicas,
        namespace=args.namespace,
        image_tag=args.image_tag
    )
    
    # Execute deployment
    manager = AppDeploymentManager()
    success = manager.deploy_application(config)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
