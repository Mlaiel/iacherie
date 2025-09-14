"""
Chart Deployment Engine module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - Helm Chart Deployment Engine
# ============================================================
# 
# Enterprise-grade Helm chart deployment for Ainflue platform
# Supports multi-cloud Kubernetes and enterprise orchestration
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
import yaml
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import kubernetes
from kubernetes import client, config

class ChartType(Enum):
    """Types of Helm charts"""
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    SECURITY = "security"
    DATABASE = "database"

class ReleaseStatus(Enum):
    """Helm release status"""
    DEPLOYED = "deployed"
    FAILED = "failed"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    SUPERSEDED = "superseded"
    UNINSTALLED = "uninstalled"

@dataclass
class HelmConfig:
    """Configuration for Helm operations"""
    kubeconfig_path: Optional[str] = None
    namespace: str = "default"
    timeout: int = 600
    wait: bool = True
    atomic: bool = True
    create_namespace: bool = True

@dataclass
class ChartDeployment:
    """Helm chart deployment configuration"""
    release_name: str
    chart_path: str
    namespace: str
    values: Dict[str, Any]
    chart_version: Optional[str] = None
    repository_url: Optional[str] = None
    wait_for_jobs: bool = True
    timeout: int = 600

class HelmChartDeploymentEngine:
    """Enterprise Helm chart deployment engine for multi-cloud Kubernetes"""
    
    def __init__(self, config -> None: HelmConfig) -> None:
        """Initialize Helm deployment engine
        
        Args:
            config: Helm configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize Kubernetes client
        self._initialize_k8s_client()
        
        # Define standard charts
        self.standard_charts = self._define_standard_charts()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"ainflue.infra.helm.deployment_engine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _initialize_k8s_client(self) -> None:
        """Initialize Kubernetes client"""
        try:
            if self.config.kubeconfig_path:
                config.load_kube_config(config_file=self.config.kubeconfig_path)
            else:
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    def _define_standard_charts(self) -> Dict[str, ChartDeployment]:
        """Define standard Helm charts for Ainflue platform"""
        return {
            # Ainflue Core Application Charts
            "ainflue-api": ChartDeployment(
                release_name="ainflue-api",
                chart_path="./charts/ainflue-api",
                namespace="ainflue",
                values={
                    "image": {
                        "repository": "ainflue/api",
                        "tag": "latest",
                        "pullPolicy": "Always"
                    },
                    "replicaCount": 3,
                    "service": {
                        "type": "ClusterIP",
                        "port": 80,
                        "targetPort": 8080
                    },
                    "ingress": {
                        "enabled": True,
                        "hosts": [
                            {
                                "host": "api.ainflue.com",
                                "paths": ["/"]
                            }
                        ],
                        "tls": [
                            {
                                "secretName": "ainflue-api-tls",
                                "hosts": ["api.ainflue.com"]
                            }
                        ]
                    },
                    "resources": {
                        "requests": {
                            "memory": "512Mi",
                            "cpu": "250m"
                        },
                        "limits": {
                            "memory": "1Gi",
                            "cpu": "500m"
                        }
                    },
                    "autoscaling": {
                        "enabled": True,
                        "minReplicas": 2,
                        "maxReplicas": 10,
                        "targetCPUUtilizationPercentage": 70
                    },
                    "env": [
                        {
                            "name": "DATABASE_URL",
                            "valueFrom": {
                                "secretKeyRef": {
                                    "name": "ainflue-secrets",
                                    "key": "database-url"
                                }
                            }
                        },
                        {
                            "name": "REDIS_URL",
                            "valueFrom": {
                                "secretKeyRef": {
                                    "name": "ainflue-secrets",
                                    "key": "redis-url"
                                }
                            }
                        }
                    ]
                }
            ),
            
            "ainflue-ai-engine": ChartDeployment(
                release_name="ainflue-ai-engine",
                chart_path="./charts/ainflue-ai-engine",
                namespace="ainflue",
                values={
                    "image": {
                        "repository": "ainflue/ai-engine",
                        "tag": "latest",
                        "pullPolicy": "Always"
                    },
                    "replicaCount": 2,
                    "service": {
                        "type": "ClusterIP",
                        "port": 80,
                        "targetPort": 8080
                    },
                    "resources": {
                        "requests": {
                            "memory": "2Gi",
                            "cpu": "1000m",
                            "nvidia.com/gpu": 1
                        },
                        "limits": {
                            "memory": "4Gi",
                            "cpu": "2000m",
                            "nvidia.com/gpu": 1
                        }
                    },
                    "nodeSelector": {
                        "node-type": "gpu-enabled"
                    },
                    "tolerations": [
                        {
                            "key": "nvidia.com/gpu",
                            "operator": "Exists",
                            "effect": "NoSchedule"
                        }
                    ],
                    "persistentVolume": {
                        "enabled": True,
                        "size": "100Gi",
                        "storageClass": "fast-ssd",
                        "mountPath": "/models"
                    }
                }
            ),
            
            "ainflue-mobile-api": ChartDeployment(
                release_name="ainflue-mobile-api",
                chart_path="./charts/ainflue-mobile-api",
                namespace="ainflue",
                values={
                    "image": {
                        "repository": "ainflue/mobile-api",
                        "tag": "latest",
                        "pullPolicy": "Always"
                    },
                    "replicaCount": 2,
                    "service": {
                        "type": "ClusterIP",
                        "port": 80,
                        "targetPort": 8080
                    },
                    "ingress": {
                        "enabled": True,
                        "hosts": [
                            {
                                "host": "mobile.ainflue.com",
                                "paths": ["/"]
                            }
                        ]
                    },
                    "resources": {
                        "requests": {
                            "memory": "256Mi",
                            "cpu": "125m"
                        },
                        "limits": {
                            "memory": "512Mi",
                            "cpu": "250m"
                        }
                    }
                }
            ),
            
            # Infrastructure Charts
            "nginx-ingress": ChartDeployment(
                release_name="nginx-ingress",
                chart_path="ingress-nginx/ingress-nginx",
                namespace="ingress-nginx",
                repository_url="https://kubernetes.github.io/ingress-nginx",
                values={
                    "controller": {
                        "replicaCount": 2,
                        "service": {
                            "type": "LoadBalancer",
                            "annotations": {
                                "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                                "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true"
                            }
                        },
                        "metrics": {
                            "enabled": True,
                            "serviceMonitor": {
                                "enabled": True
                            }
                        },
                        "config": {
                            "use-gzip": "true",
                            "gzip-level": "6",
                            "client-body-buffer-size": "64k",
                            "proxy-body-size": "100m",
                            "ssl-protocols": "TLSv1.2 TLSv1.3"
                        }
                    }
                }
            ),
            
            "cert-manager": ChartDeployment(
                release_name="cert-manager",
                chart_path="cert-manager/cert-manager",
                namespace="cert-manager",
                repository_url="https://charts.jetstack.io",
                values={
                    "installCRDs": True,
                    "global": {
                        "leaderElection": {
                            "namespace": "cert-manager"
                        }
                    },
                    "prometheus": {
                        "enabled": True,
                        "servicemonitor": {
                            "enabled": True
                        }
                    }
                }
            ),
            
            # Monitoring Charts
            "prometheus-stack": ChartDeployment(
                release_name="prometheus-stack",
                chart_path="prometheus-community/kube-prometheus-stack",
                namespace="monitoring",
                repository_url="https://prometheus-community.github.io/helm-charts",
                values={
                    "prometheus": {
                        "prometheusSpec": {
                            "retention": "30d",
                            "retentionSize": "50GiB",
                            "storageSpec": {
                                "volumeClaimTemplate": {
                                    "spec": {
                                        "storageClassName": "fast-ssd",
                                        "accessModes": ["ReadWriteOnce"],
                                        "resources": {
                                            "requests": {
                                                "storage": "100Gi"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "grafana": {
                        "adminPassword": "{{ vault_grafana_password }}",
                        "persistence": {
                            "enabled": True,
                            "size": "10Gi",
                            "storageClassName": "fast-ssd"
                        },
                        "ingress": {
                            "enabled": True,
                            "hosts": ["grafana.ainflue.com"]
                        }
                    },
                    "alertmanager": {
                        "alertmanagerSpec": {
                            "storage": {
                                "volumeClaimTemplate": {
                                    "spec": {
                                        "storageClassName": "fast-ssd",
                                        "accessModes": ["ReadWriteOnce"],
                                        "resources": {
                                            "requests": {
                                                "storage": "10Gi"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ),
            
            # Database Charts
            "postgresql": ChartDeployment(
                release_name="postgresql",
                chart_path="bitnami/postgresql",
                namespace="database",
                repository_url="https://charts.bitnami.com/bitnami",
                values={
                    "auth": {
                        "postgresPassword": "{{ vault_postgres_password }}",
                        "database": "ainflue"
                    },
                    "primary": {
                        "persistence": {
                            "enabled": True,
                            "size": "100Gi",
                            "storageClass": "fast-ssd"
                        },
                        "resources": {
                            "requests": {
                                "memory": "2Gi",
                                "cpu": "1000m"
                            },
                            "limits": {
                                "memory": "4Gi",
                                "cpu": "2000m"
                            }
                        }
                    },
                    "readReplicas": {
                        "replicaCount": 2,
                        "persistence": {
                            "enabled": True,
                            "size": "100Gi",
                            "storageClass": "fast-ssd"
                        }
                    },
                    "metrics": {
                        "enabled": True,
                        "serviceMonitor": {
                            "enabled": True
                        }
                    }
                }
            ),
            
            "redis": ChartDeployment(
                release_name="redis",
                chart_path="bitnami/redis",
                namespace="database",
                repository_url="https://charts.bitnami.com/bitnami",
                values={
                    "auth": {
                        "enabled": True,
                        "password": "{{ vault_redis_password }}"
                    },
                    "master": {
                        "persistence": {
                            "enabled": True,
                            "size": "20Gi",
                            "storageClass": "fast-ssd"
                        },
                        "resources": {
                            "requests": {
                                "memory": "1Gi",
                                "cpu": "500m"
                            },
                            "limits": {
                                "memory": "2Gi",
                                "cpu": "1000m"
                            }
                        }
                    },
                    "replica": {
                        "replicaCount": 2,
                        "persistence": {
                            "enabled": True,
                            "size": "20Gi",
                            "storageClass": "fast-ssd"
                        }
                    },
                    "metrics": {
                        "enabled": True,
                        "serviceMonitor": {
                            "enabled": True
                        }
                    }
                }
            )
        }
    
    async def add_helm_repository(self, name: str, url: str) -> bool:
        """Add a Helm repository
        
        Args:
            name: Repository name
            url: Repository URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add repository
            result = subprocess.run(
                ["helm", "repo", "add", name, url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Update repository
                subprocess.run(
                    ["helm", "repo", "update"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                self.logger.info(f"Added Helm repository: {name} ({url})")
                return True
            else:
                self.logger.error(f"Failed to add Helm repository {name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding Helm repository {name}: {e}")
            return False
    
    async def deploy_chart(self, deployment: ChartDeployment) -> bool:
        """Deploy a Helm chart
        
        Args:
            deployment: Chart deployment configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create namespace if it doesn't exist
            if self.config.create_namespace:
                await self._ensure_namespace(deployment.namespace)
            
            # Prepare Helm command
            helm_cmd = [
                "helm", "upgrade", "--install",
                deployment.release_name,
                deployment.chart_path,
                "--namespace", deployment.namespace
            ]
            
            # Add repository if specified
            if deployment.repository_url:
                repo_name = deployment.chart_path.split('/')[0]
                await self.add_helm_repository(repo_name, deployment.repository_url)
            
            # Add chart version if specified
            if deployment.chart_version:
                helm_cmd.extend(["--version", deployment.chart_version])
            
            # Add timeout
            helm_cmd.extend(["--timeout", f"{deployment.timeout}s"])
            
            # Add wait flag
            if deployment.wait_for_jobs:
                helm_cmd.append("--wait")
                helm_cmd.append("--wait-for-jobs")
            
            # Add atomic flag for rollback on failure
            if self.config.atomic:
                helm_cmd.append("--atomic")
            
            # Create values file
            values_file = await self._create_values_file(deployment)
            helm_cmd.extend(["--values", values_file])
            
            # Execute Helm command
            self.logger.info(f"Deploying Helm chart: {deployment.release_name}")
            
            result = subprocess.run(
                helm_cmd,
                capture_output=True,
                text=True,
                timeout=deployment.timeout + 60
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully deployed chart: {deployment.release_name}")
                
                # Verify deployment
                if await self._verify_deployment(deployment):
                    return True
                else:
                    self.logger.warning(f"Deployment verification failed for: {deployment.release_name}")
                    return False
            else:
                self.logger.error(f"Failed to deploy chart {deployment.release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying chart {deployment.release_name}: {e}")
            return False
        finally:
            # Clean up values file
            if 'values_file' in locals():
                Path(values_file).unlink(missing_ok=True)
    
    async def _ensure_namespace(self, namespace: str) -> bool:
        """Ensure Kubernetes namespace exists
        
        Args:
            namespace: Namespace name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if namespace exists
            try:
                self.core_v1.read_namespace(name=namespace)
                return True
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create namespace
                    namespace_manifest = client.V1Namespace(
                        metadata=client.V1ObjectMeta(
                            name=namespace,
                            labels={
                                "managed-by": "ainflue-helm-engine"
                            }
                        )
                    )
                    
                    self.core_v1.create_namespace(body=namespace_manifest)
                    self.logger.info(f"Created namespace: {namespace}")
                    return True
                else:
                    raise
                    
        except Exception as e:
            self.logger.error(f"Failed to ensure namespace {namespace}: {e}")
            return False
    
    async def _create_values_file(self, deployment: ChartDeployment) -> str:
        """Create a temporary values file for Helm deployment
        
        Args:
            deployment: Chart deployment configuration
            
        Returns:
            str: Path to values file
        """
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(deployment.values, f, default_flow_style=False, indent=2)
            return f.name
    
    async def _verify_deployment(self, deployment: ChartDeployment) -> bool:
        """Verify that a Helm deployment was successful
        
        Args:
            deployment: Chart deployment configuration
            
        Returns:
            bool: True if deployment is healthy, False otherwise
        """
        try:
            # Check deployment status using kubectl
            result = subprocess.run(
                [
                    "kubectl", "get", "deployments",
                    "-n", deployment.namespace,
                    "-l", f"app.kubernetes.io/instance={deployment.release_name}",
                    "-o", "json"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                deployments = json.loads(result.stdout)
                
                for deploy in deployments.get("items", []):
                    status = deploy.get("status", {})
                    replicas = status.get("replicas", 0)
                    ready_replicas = status.get("readyReplicas", 0)
                    
                    if replicas != ready_replicas:
                        self.logger.warning(f"Deployment {deploy['metadata']['name']} not fully ready: {ready_replicas}/{replicas}")
                        return False
                
                self.logger.info(f"Deployment verification passed for: {deployment.release_name}")
                return True
            else:
                self.logger.error(f"Failed to verify deployment: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying deployment {deployment.release_name}: {e}")
            return False
    
    async def get_release_status(self, release_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get the status of a Helm release
        
        Args:
            release_name: Name of the Helm release
            namespace: Kubernetes namespace
            
        Returns:
            Dict containing release status information
        """
        try:
            result = subprocess.run(
                ["helm", "status", release_name, "--namespace", namespace, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                return {
                    "name": status_data.get("name"),
                    "namespace": status_data.get("namespace"),
                    "status": status_data.get("info", {}).get("status"),
                    "revision": status_data.get("version"),
                    "updated": status_data.get("info", {}).get("last_deployed"),
                    "chart": status_data.get("chart", {}).get("metadata", {}).get("name"),
                    "app_version": status_data.get("chart", {}).get("metadata", {}).get("appVersion")
                }
            else:
                self.logger.error(f"Failed to get status for release {release_name}: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting release status for {release_name}: {e}")
            return None
    
    async def rollback_release(self, release_name: str, namespace: str, revision: Optional[int] = None) -> bool:
        """Rollback a Helm release to a previous revision
        
        Args:
            release_name: Name of the Helm release
            namespace: Kubernetes namespace
            revision: Specific revision to rollback to (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            helm_cmd = ["helm", "rollback", release_name, "--namespace", namespace]
            
            if revision:
                helm_cmd.append(str(revision))
            
            result = subprocess.run(
                helm_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully rolled back release: {release_name}")
                return True
            else:
                self.logger.error(f"Failed to rollback release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error rolling back release {release_name}: {e}")
            return False
    
    async def uninstall_release(self, release_name: str, namespace: str) -> bool:
        """Uninstall a Helm release
        
        Args:
            release_name: Name of the Helm release
            namespace: Kubernetes namespace
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["helm", "uninstall", release_name, "--namespace", namespace],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully uninstalled release: {release_name}")
                return True
            else:
                self.logger.error(f"Failed to uninstall release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uninstalling release {release_name}: {e}")
            return False
    
    async def list_releases(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all Helm releases
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            List of release information
        """
        try:
            helm_cmd = ["helm", "list", "--output", "json"]
            
            if namespace:
                helm_cmd.extend(["--namespace", namespace])
            else:
                helm_cmd.append("--all-namespaces")
            
            result = subprocess.run(
                helm_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                releases = json.loads(result.stdout) if result.stdout.strip() else []
                return releases
            else:
                self.logger.error(f"Failed to list releases: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing releases: {e}")
            return []

# Enterprise Helm orchestrator
class AinflueHelmOrchestrator:
    """High-level Helm orchestration for Ainflue platform"""
    
    def __init__(self, environment -> None: str = "production") -> None:
        """Initialize Helm orchestrator
        
        Args:
            environment: Deployment environment
        """
        self.environment = environment
        self.logger = logging.getLogger(f"ainflue.infra.helm.orchestrator")
        
        # Configuration
        self.config = HelmConfig(
            namespace="ainflue",
            timeout=600 if environment == "production" else 300,
            create_namespace=True
        )
        
        self.engine = HelmChartDeploymentEngine(self.config)
    
    async def deploy_ainflue_platform(self) -> Dict[str, bool]:
        """Deploy the complete Ainflue platform using Helm charts
        
        Returns:
            Dict mapping chart names to deployment status
        """
        try:
            results = {}
            
            # Deployment order matters for dependencies
            deployment_order = [
                # Infrastructure first
                "nginx-ingress",
                "cert-manager",
                
                # Monitoring
                "prometheus-stack",
                
                # Databases
                "postgresql",
                "redis",
                
                # Applications
                "ainflue-api",
                "ainflue-ai-engine",
                "ainflue-mobile-api"
            ]
            
            for chart_name in deployment_order:
                if chart_name in self.engine.standard_charts:
                    deployment = self.engine.standard_charts[chart_name]
                    
                    # Customize for environment
                    if self.environment != "production":
                        deployment = self._customize_for_environment(deployment)
                    
                    success = await self.engine.deploy_chart(deployment)
                    results[chart_name] = success
                    
                    if not success:
                        self.logger.error(f"Failed to deploy {chart_name}, stopping deployment")
                        break
                    
                    # Brief pause between deployments
                    await asyncio.sleep(5)
                else:
                    self.logger.warning(f"Unknown chart: {chart_name}")
                    results[chart_name] = False
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Ainflue platform: {e}")
            return {}
    
    def _customize_for_environment(self, deployment: ChartDeployment) -> ChartDeployment:
        """Customize deployment for non-production environments"""
        
        if self.environment in ["development", "staging"]:
            # Reduce resource requirements
            if "resources" in deployment.values:
                if "requests" in deployment.values["resources"]:
                    deployment.values["resources"]["requests"]["memory"] = "128Mi"
                    deployment.values["resources"]["requests"]["cpu"] = "100m"
                
                if "limits" in deployment.values["resources"]:
                    deployment.values["resources"]["limits"]["memory"] = "256Mi"
                    deployment.values["resources"]["limits"]["cpu"] = "200m"
            
            # Reduce replica count
            if "replicaCount" in deployment.values:
                deployment.values["replicaCount"] = 1
            
            # Disable autoscaling for dev/staging
            if "autoscaling" in deployment.values:
                deployment.values["autoscaling"]["enabled"] = False
        
        return deployment

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        orchestrator = AinflueHelmOrchestrator(environment="production")
        
        # Deploy platform
        results = await orchestrator.deploy_ainflue_platform()
        
        print("Deployment Results:")
        for chart, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {chart}: {status}")
    
    asyncio.run(main())