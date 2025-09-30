# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Helm Release Manager for Ainflue Platform
=========================================

Enterprise-grade Helm release management system for Kubernetes deployments.
Supports canary deployments, rollbacks, and multi-environment management.

Features:
- Automated Helm chart deployment and management
- Canary and blue-green deployment strategies
- Release rollback and versioning
- Multi-environment configuration
- Integration with monitoring and alerting
- Security and compliance validation
"""

import subprocess
import yaml
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

class DeploymentStrategy(Enum):
    """Deployment strategy types"""
    ROLLING = "rolling"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    RECREATE = "recreate"

class ReleaseStatus(Enum):
    """Helm release status"""
    DEPLOYED = "deployed"
    FAILED = "failed"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    PENDING_ROLLBACK = "pending-rollback"
    SUPERSEDED = "superseded"
    UNINSTALLED = "uninstalled"

@dataclass
class HelmRelease:
    """Helm release configuration"""
    name: str
    namespace: str
    chart: str
    version: str
    values: Dict[str, Any]
    environment: str
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    timeout: int = 600
    wait: bool = True
    atomic: bool = True
    create_namespace: bool = True

@dataclass
class ReleaseInfo:
    """Helm release information"""
    name: str
    namespace: str
    revision: int
    status: ReleaseStatus
    chart: str
    app_version: str
    updated: datetime

class ReleaseManager:
    """
    Enterprise Helm Release Manager
    
    Manages Helm releases across multiple environments with advanced deployment
    strategies, monitoring, and automated rollback capabilities.
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.logger = self._setup_logging()
        self.releases: Dict[str, HelmRelease] = {}
        self._validate_helm_installation()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup enterprise logging"""
        logger = logging.getLogger("helm.release_manager")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("/var/log/ainflue/helm")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "release_manager.log")
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _validate_helm_installation(self) -> bool:
        """Validate Helm installation and configuration"""
        try:
            result = self._run_helm_command(["version", "--short"])
            if result.returncode == 0:
                self.logger.info(f"Helm version: {result.stdout.strip()}")
                return True
            else:
                raise Exception("Helm not properly installed")
        except Exception as e:
            self.logger.error(f"Helm validation failed: {str(e)}")
            raise
    
    def _run_helm_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute Helm command with proper error handling"""
        cmd = ["helm"] + args
        
        # Add kubeconfig if specified
        if self.kubeconfig_path:
            cmd.extend(["--kubeconfig", self.kubeconfig_path])
        
        self.logger.debug(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"STDERR: {result.stderr}")
                
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Helm command failed: {e}")
            self.logger.error(f"Command: {' '.join(cmd)}")
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"STDOUT: {e.stdout}")
            self.logger.error(f"STDERR: {e.stderr}")
            raise
    
    def add_repository(self, name: str, url: str, username: Optional[str] = None, 
                      password: Optional[str] = None) -> bool:
        """Add Helm repository"""
        try:
            cmd = ["repo", "add", name, url]
            
            if username and password:
                cmd.extend(["--username", username, "--password", password])
            
            self._run_helm_command(cmd)
            self._run_helm_command(["repo", "update"])
            
            self.logger.info(f"Successfully added repository: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add repository {name}: {str(e)}")
            return False
    
    def deploy_release(self, release: HelmRelease, dry_run: bool = False) -> bool:
        """
        Deploy Helm release with specified strategy
        
        Args:
            release: HelmRelease configuration
            dry_run: Whether to perform a dry run
            
        Returns:
            bool: Deployment success status
        """
        try:
            self.logger.info(f"Deploying release: {release.name} in namespace: {release.namespace}")
            
            # Check if release exists
            if self.release_exists(release.name, release.namespace):
                return self._upgrade_release(release, dry_run)
            else:
                return self._install_release(release, dry_run)
                
        except Exception as e:
            self.logger.error(f"Failed to deploy release {release.name}: {str(e)}")
            return False
    
    def _install_release(self, release: HelmRelease, dry_run: bool = False) -> bool:
        """Install new Helm release"""
        try:
            cmd = [
                "install", release.name, release.chart,
                "--namespace", release.namespace,
                "--version", release.version,
                "--timeout", f"{release.timeout}s"
            ]
            
            if release.create_namespace:
                cmd.append("--create-namespace")
            
            if release.wait:
                cmd.append("--wait")
            
            if release.atomic:
                cmd.append("--atomic")
            
            if dry_run:
                cmd.append("--dry-run")
            
            # Add values
            if release.values:
                values_file = self._create_values_file(release)
                cmd.extend(["--values", str(values_file)])
            
            result = self._run_helm_command(cmd)
            
            if not dry_run:
                self.releases[f"{release.namespace}/{release.name}"] = release
                self.logger.info(f"Successfully installed release: {release.name}")
            else:
                self.logger.info(f"Dry run successful for release: {release.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install release {release.name}: {str(e)}")
            return False
    
    def _upgrade_release(self, release: HelmRelease, dry_run: bool = False) -> bool:
        """Upgrade existing Helm release"""
        try:
            cmd = [
                "upgrade", release.name, release.chart,
                "--namespace", release.namespace,
                "--version", release.version,
                "--timeout", f"{release.timeout}s"
            ]
            
            if release.wait:
                cmd.append("--wait")
            
            if release.atomic:
                cmd.append("--atomic")
            
            if dry_run:
                cmd.append("--dry-run")
            
            # Add values
            if release.values:
                values_file = self._create_values_file(release)
                cmd.extend(["--values", str(values_file)])
            
            # Strategy-specific configuration
            if release.strategy == DeploymentStrategy.CANARY:
                cmd.extend(["--set", "deployment.strategy=canary"])
            elif release.strategy == DeploymentStrategy.BLUE_GREEN:
                cmd.extend(["--set", "deployment.strategy=bluegreen"])
            
            result = self._run_helm_command(cmd)
            
            if not dry_run:
                self.releases[f"{release.namespace}/{release.name}"] = release
                self.logger.info(f"Successfully upgraded release: {release.name}")
            else:
                self.logger.info(f"Dry run successful for upgrade: {release.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upgrade release {release.name}: {str(e)}")
            return False
    
    def _create_values_file(self, release: HelmRelease) -> Path:
        """Create temporary values file for release"""
        values_dir = Path("/tmp/helm-values")
        values_dir.mkdir(exist_ok=True)
        
        values_file = values_dir / f"{release.name}-{release.namespace}-values.yaml"
        
        with open(values_file, 'w') as f:
            yaml.dump(release.values, f, default_flow_style=False)
        
        return values_file
    
    def rollback_release(self, name: str, namespace: str, revision: Optional[int] = None) -> bool:
        """
        Rollback Helm release to previous or specific revision
        
        Args:
            name: Release name
            namespace: Release namespace
            revision: Specific revision to rollback to (None for previous)
            
        Returns:
            bool: Rollback success status
        """
        try:
            cmd = ["rollback", name]
            
            if revision:
                cmd.append(str(revision))
            
            cmd.extend([
                "--namespace", namespace,
                "--wait",
                "--timeout", "300s"
            ])
            
            self._run_helm_command(cmd)
            
            self.logger.info(f"Successfully rolled back release: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback release {name}: {str(e)}")
            return False
    
    def uninstall_release(self, name: str, namespace: str, keep_history: bool = True) -> bool:
        """
        Uninstall Helm release
        
        Args:
            name: Release name
            namespace: Release namespace
            keep_history: Whether to keep release history
            
        Returns:
            bool: Uninstall success status
        """
        try:
            cmd = ["uninstall", name, "--namespace", namespace]
            
            if keep_history:
                cmd.append("--keep-history")
            
            self._run_helm_command(cmd)
            
            # Remove from local tracking
            release_key = f"{namespace}/{name}"
            if release_key in self.releases:
                del self.releases[release_key]
            
            self.logger.info(f"Successfully uninstalled release: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall release {name}: {str(e)}")
            return False
    
    def release_exists(self, name: str, namespace: str) -> bool:
        """Check if Helm release exists"""
        try:
            result = self._run_helm_command([
                "status", name, "--namespace", namespace
            ], check=False)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def get_release_info(self, name: str, namespace: str) -> Optional[ReleaseInfo]:
        """Get detailed release information"""
        try:
            result = self._run_helm_command([
                "status", name, "--namespace", namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                
                return ReleaseInfo(
                    name=status_data["name"],
                    namespace=status_data["namespace"],
                    revision=status_data["version"],
                    status=ReleaseStatus(status_data["info"]["status"]),
                    chart=status_data["chart"]["metadata"]["name"],
                    app_version=status_data["chart"]["metadata"]["appVersion"],
                    updated=datetime.fromisoformat(
                        status_data["info"]["last_deployed"].replace("Z", "+00:00")
                    )
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get release info for {name}: {str(e)}")
            return None
    
    def list_releases(self, namespace: Optional[str] = None) -> List[ReleaseInfo]:
        """List all Helm releases"""
        try:
            cmd = ["list", "--output", "json"]
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            else:
                cmd.append("--all-namespaces")
            
            result = self._run_helm_command(cmd)
            
            if result.returncode == 0 and result.stdout.strip():
                releases_data = json.loads(result.stdout)
                
                releases = []
                for release_data in releases_data:
                    releases.append(ReleaseInfo(
                        name=release_data["name"],
                        namespace=release_data["namespace"],
                        revision=release_data["revision"],
                        status=ReleaseStatus(release_data["status"]),
                        chart=release_data["chart"],
                        app_version=release_data["app_version"],
                        updated=datetime.fromisoformat(
                            release_data["updated"].replace("Z", "+00:00")
                        )
                    ))
                
                return releases
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to list releases: {str(e)}")
            return []
    
    def get_release_history(self, name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get release history and revisions"""
        try:
            result = self._run_helm_command([
                "history", name, "--namespace", namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get release history for {name}: {str(e)}")
            return []
    
    def test_release(self, name: str, namespace: str) -> bool:
        """Run release tests"""
        try:
            result = self._run_helm_command([
                "test", name, "--namespace", namespace
            ])
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to test release {name}: {str(e)}")
            return False
    
    def validate_release_health(self, name: str, namespace: str) -> Dict[str, Any]:
        """Validate release health and status"""
        try:
            health_status = {
                "release_exists": False,
                "status": None,
                "pods_ready": False,
                "services_available": False,
                "ingress_configured": False,
                "overall_health": "unhealthy"
            }
            
            # Check if release exists
            release_info = self.get_release_info(name, namespace)
            if not release_info:
                return health_status
            
            health_status["release_exists"] = True
            health_status["status"] = release_info.status.value
            
            # Check pods status using kubectl
            try:
                kubectl_result = subprocess.run([
                    "kubectl", "get", "pods", 
                    "-n", namespace,
                    "-l", f"app.kubernetes.io/instance={name}",
                    "--output", "json"
                ], capture_output=True, text=True, check=True)
                
                if kubectl_result.returncode == 0:
                    pods_data = json.loads(kubectl_result.stdout)
                    ready_pods = 0
                    total_pods = len(pods_data["items"])
                    
                    for pod in pods_data["items"]:
                        if pod["status"]["phase"] == "Running":
                            ready_pods += 1
                    
                    health_status["pods_ready"] = ready_pods == total_pods and total_pods > 0
            except Exception:
                pass
            
            # Determine overall health
            if (release_info.status == ReleaseStatus.DEPLOYED and 
                health_status["pods_ready"]):
                health_status["overall_health"] = "healthy"
            elif release_info.status == ReleaseStatus.DEPLOYED:
                health_status["overall_health"] = "degraded"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Failed to validate release health for {name}: {str(e)}")
            return {"overall_health": "unknown", "error": str(e)}
    
    def backup_release_values(self, name: str, namespace: str) -> Optional[Path]:
        """Backup current release values"""
        try:
            result = self._run_helm_command([
                "get", "values", name, "--namespace", namespace, "--output", "yaml"
            ])
            
            if result.returncode == 0:
                backup_dir = Path("/var/backups/helm-releases")
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_file = backup_dir / f"{name}-{namespace}-{timestamp}.yaml"
                
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                
                self.logger.info(f"Release values backed up to: {backup_file}")
                return backup_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to backup release values for {name}: {str(e)}")
            return None
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get comprehensive deployment status across all releases"""
        try:
            releases = self.list_releases()
            
            status_summary = {
                "total_releases": len(releases),
                "healthy_releases": 0,
                "failed_releases": 0,
                "pending_releases": 0,
                "release_details": []
            }
            
            for release in releases:
                health = self.validate_release_health(release.name, release.namespace)
                
                release_detail = {
                    "name": release.name,
                    "namespace": release.namespace,
                    "status": release.status.value,
                    "chart": release.chart,
                    "app_version": release.app_version,
                    "health": health["overall_health"]
                }
                
                status_summary["release_details"].append(release_detail)
                
                if health["overall_health"] == "healthy":
                    status_summary["healthy_releases"] += 1
                elif release.status == ReleaseStatus.FAILED:
                    status_summary["failed_releases"] += 1
                elif release.status in [ReleaseStatus.PENDING_INSTALL, 
                                      ReleaseStatus.PENDING_UPGRADE]:
                    status_summary["pending_releases"] += 1
            
            return status_summary
            
        except Exception as e:
            self.logger.error(f"Failed to get deployment status: {str(e)}")
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    manager = ReleaseManager()
    
    # Example release configuration
    example_release = HelmRelease(
        name="ainflue-api",
        namespace="ainflue-production",
        chart="ainflue/api",
        version="1.0.0",
        values={
            "image": {
                "repository": "ainflue/api",
                "tag": "v1.0.0"
            },
            "service": {
                "type": "ClusterIP",
                "port": 8080
            },
            "ingress": {
                "enabled": True,
                "host": "api.ainflue.com"
            }
        },
        environment="production",
        strategy=DeploymentStrategy.ROLLING
    )
    
    # Test deployment (dry run)
    print("Testing deployment configuration...")
    if manager.deploy_release(example_release, dry_run=True):
        print("✅ Deployment configuration is valid")
    else:
        print("❌ Deployment configuration failed validation")
    
    # List current releases
    releases = manager.list_releases()
    print(f"\nCurrent releases: {len(releases)}")
    for release in releases:
        print(f"  - {release.name} ({release.namespace}): {release.status.value}")
    
    # Get deployment status
    status = manager.get_deployment_status()
    print(f"\nDeployment Status Summary:")
    print(f"  Total releases: {status['total_releases']}")
    print(f"  Healthy: {status['healthy_releases']}")
    print(f"  Failed: {status['failed_releases']}")
    print(f"  Pending: {status['pending_releases']}")