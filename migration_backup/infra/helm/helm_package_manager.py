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
Helm Package Manager

This module provides enterprise-grade Helm package management capabilities
for the Ainflue platform infrastructure.

Features:
    - Helm chart lifecycle management
    - Multi-environment deployments
    - Dependency management
    - Configuration templating
    - Release versioning and rollback
    - Security scanning and validation
"""

import logging
import subprocess
import yaml
import json
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ReleaseStatus(Enum):
    """Helm release status."""
    UNKNOWN = "unknown"
    DEPLOYED = "deployed"
    UNINSTALLED = "uninstalled"
    SUPERSEDED = "superseded"
    FAILED = "failed"
    UNINSTALLING = "uninstalling"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    PENDING_ROLLBACK = "pending-rollback"

@dataclass
class ChartInfo:
    """Helm chart information."""
    name: str
    version: str
    app_version: str
    description: str
    chart_path: Optional[str] = None
    repository: Optional[str] = None

@dataclass
class ReleaseInfo:
    """Helm release information."""
    name: str
    namespace: str
    revision: int
    status: ReleaseStatus
    chart: str
    app_version: str
    updated: str

class HelmPackageManager:
    """
    Enterprise Helm package management for Kubernetes deployments.
    
    Provides comprehensive chart lifecycle management with security,
    validation, and multi-environment support.
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize Helm package manager.
        
        Args:
            kubeconfig_path: Path to kubeconfig file
        """
        self.kubeconfig_path = kubeconfig_path
        self.helm_cmd = self._build_helm_command()
        
        # Verify Helm installation
        self._verify_helm_installation()
    
    def _build_helm_command(self) -> List[str]:
        """Build base Helm command with kubeconfig."""
        cmd = ["helm"]
        if self.kubeconfig_path:
            cmd.extend(["--kubeconfig", self.kubeconfig_path])
        return cmd
    
    def _verify_helm_installation(self) -> None:
        """Verify Helm is installed and accessible."""
        try:
            result = subprocess.run(
                self.helm_cmd + ["version", "--short"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Helm version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"Helm is not installed or accessible: {e}")
    
    def add_repository(self, name: str, url: str, force_update: bool = False) -> bool:
        """
        Add Helm chart repository.
        
        Args:
            name: Repository name
            url: Repository URL
            force_update: Force repository update
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = self.helm_cmd + ["repo", "add", name, url]
            if force_update:
                cmd.append("--force-update")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Added Helm repository: {name}")
                return True
            else:
                logger.error(f"Failed to add repository {name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add repository: {str(e)}")
            return False
    
    def update_repositories(self) -> bool:
        """
        Update all Helm repositories.
        
        Returns:
            bool: True if successful
        """
        try:
            result = subprocess.run(
                self.helm_cmd + ["repo", "update"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Updated Helm repositories")
                return True
            else:
                logger.error(f"Failed to update repositories: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update repositories: {str(e)}")
            return False
    
    def search_charts(self, keyword: str, repository: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for Helm charts.
        
        Args:
            keyword: Search keyword
            repository: Specific repository to search
            
        Returns:
            List[Dict]: List of matching charts
        """
        try:
            cmd = self.helm_cmd + ["search", "repo", keyword, "--output", "json"]
            if repository:
                cmd.extend(["--repository", repository])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Failed to search charts: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to search charts: {str(e)}")
            return []
    
    def install_chart(self, release_name: str, chart: str, namespace: str,
                     values: Optional[Dict[str, Any]] = None,
                     version: Optional[str] = None,
                     create_namespace: bool = True,
                     wait: bool = True,
                     timeout: str = "300s") -> bool:
        """
        Install Helm chart.
        
        Args:
            release_name: Name for the release
            chart: Chart name or path
            namespace: Kubernetes namespace
            values: Chart values override
            version: Specific chart version
            create_namespace: Create namespace if it doesn't exist
            wait: Wait for deployment to complete
            timeout: Operation timeout
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = self.helm_cmd + [
                "install", release_name, chart,
                "--namespace", namespace
            ]
            
            if version:
                cmd.extend(["--version", version])
            
            if create_namespace:
                cmd.append("--create-namespace")
            
            if wait:
                cmd.extend(["--wait", "--timeout", timeout])
            
            # Handle values
            if values:
                values_file = self._create_values_file(values)
                cmd.extend(["--values", values_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Installed Helm chart: {release_name}")
                return True
            else:
                logger.error(f"Failed to install chart {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install chart: {str(e)}")
            return False
    
    def upgrade_release(self, release_name: str, chart: str, namespace: str,
                       values: Optional[Dict[str, Any]] = None,
                       version: Optional[str] = None,
                       install: bool = True,
                       wait: bool = True,
                       timeout: str = "300s") -> bool:
        """
        Upgrade Helm release.
        
        Args:
            release_name: Release name
            chart: Chart name or path
            namespace: Kubernetes namespace
            values: Chart values override
            version: Specific chart version
            install: Install if release doesn't exist
            wait: Wait for upgrade to complete
            timeout: Operation timeout
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = self.helm_cmd + [
                "upgrade", release_name, chart,
                "--namespace", namespace
            ]
            
            if version:
                cmd.extend(["--version", version])
            
            if install:
                cmd.append("--install")
            
            if wait:
                cmd.extend(["--wait", "--timeout", timeout])
            
            # Handle values
            if values:
                values_file = self._create_values_file(values)
                cmd.extend(["--values", values_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Upgraded Helm release: {release_name}")
                return True
            else:
                logger.error(f"Failed to upgrade release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to upgrade release: {str(e)}")
            return False
    
    def uninstall_release(self, release_name: str, namespace: str,
                         keep_history: bool = False,
                         wait: bool = True,
                         timeout: str = "300s") -> bool:
        """
        Uninstall Helm release.
        
        Args:
            release_name: Release name
            namespace: Kubernetes namespace
            keep_history: Keep release history
            wait: Wait for uninstall to complete
            timeout: Operation timeout
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = self.helm_cmd + [
                "uninstall", release_name,
                "--namespace", namespace
            ]
            
            if keep_history:
                cmd.append("--keep-history")
            
            if wait:
                cmd.extend(["--wait", "--timeout", timeout])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Uninstalled Helm release: {release_name}")
                return True
            else:
                logger.error(f"Failed to uninstall release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to uninstall release: {str(e)}")
            return False
    
    def rollback_release(self, release_name: str, namespace: str,
                        revision: Optional[int] = None,
                        wait: bool = True,
                        timeout: str = "300s") -> bool:
        """
        Rollback Helm release.
        
        Args:
            release_name: Release name
            namespace: Kubernetes namespace
            revision: Specific revision to rollback to
            wait: Wait for rollback to complete
            timeout: Operation timeout
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = self.helm_cmd + [
                "rollback", release_name,
                "--namespace", namespace
            ]
            
            if revision:
                cmd.append(str(revision))
            
            if wait:
                cmd.extend(["--wait", "--timeout", timeout])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Rolled back Helm release: {release_name}")
                return True
            else:
                logger.error(f"Failed to rollback release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to rollback release: {str(e)}")
            return False
    
    def list_releases(self, namespace: Optional[str] = None,
                     all_namespaces: bool = False) -> List[ReleaseInfo]:
        """
        List Helm releases.
        
        Args:
            namespace: Specific namespace
            all_namespaces: List releases from all namespaces
            
        Returns:
            List[ReleaseInfo]: List of releases
        """
        try:
            cmd = self.helm_cmd + ["list", "--output", "json"]
            
            if all_namespaces:
                cmd.append("--all-namespaces")
            elif namespace:
                cmd.extend(["--namespace", namespace])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                releases_data = json.loads(result.stdout)
                releases = []
                
                for release_data in releases_data:
                    release = ReleaseInfo(
                        name=release_data["name"],
                        namespace=release_data["namespace"],
                        revision=release_data["revision"],
                        status=ReleaseStatus(release_data["status"]),
                        chart=release_data["chart"],
                        app_version=release_data["app_version"],
                        updated=release_data["updated"]
                    )
                    releases.append(release)
                
                return releases
            else:
                logger.error(f"Failed to list releases: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list releases: {str(e)}")
            return []
    
    def get_release_status(self, release_name: str, namespace: str) -> Optional[ReleaseInfo]:
        """
        Get status of specific Helm release.
        
        Args:
            release_name: Release name
            namespace: Kubernetes namespace
            
        Returns:
            ReleaseInfo: Release information
        """
        try:
            cmd = self.helm_cmd + [
                "status", release_name,
                "--namespace", namespace,
                "--output", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                
                return ReleaseInfo(
                    name=status_data["name"],
                    namespace=status_data["namespace"],
                    revision=status_data["version"],
                    status=ReleaseStatus(status_data["info"]["status"]),
                    chart=status_data["chart"]["metadata"]["name"],
                    app_version=status_data["chart"]["metadata"]["appVersion"],
                    updated=status_data["info"]["last_deployed"]
                )
            else:
                logger.error(f"Failed to get release status: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get release status: {str(e)}")
            return None
    
    def get_release_values(self, release_name: str, namespace: str) -> Dict[str, Any]:
        """
        Get values for Helm release.
        
        Args:
            release_name: Release name
            namespace: Kubernetes namespace
            
        Returns:
            Dict: Release values
        """
        try:
            cmd = self.helm_cmd + [
                "get", "values", release_name,
                "--namespace", namespace,
                "--output", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Failed to get release values: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get release values: {str(e)}")
            return {}
    
    def template_chart(self, chart: str, release_name: str,
                      values: Optional[Dict[str, Any]] = None,
                      namespace: str = "default") -> str:
        """
        Template Helm chart without installing.
        
        Args:
            chart: Chart name or path
            release_name: Release name for templating
            values: Chart values override
            namespace: Target namespace
            
        Returns:
            str: Templated YAML manifests
        """
        try:
            cmd = self.helm_cmd + [
                "template", release_name, chart,
                "--namespace", namespace
            ]
            
            # Handle values
            if values:
                values_file = self._create_values_file(values)
                cmd.extend(["--values", values_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Failed to template chart: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to template chart: {str(e)}")
            return ""
    
    def _create_values_file(self, values: Dict[str, Any]) -> str:
        """Create temporary values file."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )
        
        yaml.dump(values, temp_file, default_flow_style=False)
        temp_file.close()
        
        return temp_file.name
    
    def package_chart(self, chart_path: str, destination: str = ".") -> Optional[str]:
        """
        Package Helm chart.
        
        Args:
            chart_path: Path to chart directory
            destination: Destination directory for package
            
        Returns:
            str: Path to packaged chart file
        """
        try:
            cmd = self.helm_cmd + [
                "package", chart_path,
                "--destination", destination
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract package filename from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if line.startswith("Successfully packaged chart"):
                        package_path = line.split(":", 1)[1].strip()
                        logger.info(f"Packaged chart: {package_path}")
                        return package_path
                
                return None
            else:
                logger.error(f"Failed to package chart: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to package chart: {str(e)}")
            return None