"""IA Influencer Agent - Helm Package Manager
Enterprise Helm chart management and application deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Helm chart lifecycle management
- Custom chart development and packaging
- Release management with rollback capabilities
- Repository management and chart distribution
- Values templating and environment configuration
"""

import asyncio
import logging
import os
import tempfile
import yaml
import json
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import semver

# Note: Import paths adjusted for actual deployment structure
from .base_manager import BaseDeploymentManager

# Mock metrics collector for standalone operation
class MetricsCollector:
    """
Mock metrics collector."""
    def __init__(self):
        """
Initialize Helm metrics collector with chart monitoring capabilities"""
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.helm_metrics = ['chart_deployments', 'release_status', 'upgrade_success_rate']
        self.chart_repositories = ['stable', 'bitnami', 'prometheus-community']
        self.monitoring_hooks = ['pre-install', 'post-install', 'pre-upgrade', 'post-upgrade']
        self.release_metrics = {}
        self.chart_versions = {}
        self.rollback_history = []
        self.logger.info("Helm MetricsCollector initialized with chart monitoring")


class ReleaseStatus(Enum):
    """Helm release status."""

    DEPLOYED = "deployed"
    FAILED = "failed"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    PENDING_ROLLBACK = "pending-rollback"
    SUPERSEDED = "superseded"
    UNINSTALLED = "uninstalled"


class ChartType(Enum):
    """Helm chart types."""

    APPLICATION = "application"
    LIBRARY = "library"


@dataclass
class HelmChart:
    """Helm chart configuration."""
    name: str
    version: str
    app_version: str
    description: str
    chart_type: ChartType
    dependencies: List[Dict[str, str]]
    values: Dict[str, Any]
    templates: Dict[str, str]


@dataclass
class HelmRelease:
    """
Helm release information."""
    name: str
    namespace: str
    chart: str
    chart_version: str
    app_version: str
    status: ReleaseStatus
    revision: int
    updated: str
    values: Dict[str, Any]


@dataclass
class HelmRepository:
    """
Helm repository configuration."""
    name: str
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None


class HelmManager(BaseDeploymentManager):
    """
    Enterprise Helm package manager.
    
    Manages Helm charts, releases, and repositories for the
    IA Influencer Agent platform with enterprise features.
    """
    def __init__(
        self,
        helm_binary: str = "helm",
        kubeconfig: Optional[str] = None,
        default_namespace: str = "ia-influencer-agent",
        metrics_collector: Optional[MetricsCollector] = None
    ):
        super().__init__()
        self.helm_binary = helm_binary
        self.kubeconfig = kubeconfig
        self.default_namespace = default_namespace
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Chart and release management
        self.managed_releases: Dict[str, HelmRelease] = {}
        self.chart_cache: Dict[str, HelmChart] = {}
        self.repositories: Dict[str, HelmRepository] = {}
        
        # Verify Helm installation
        self._verify_helm_installation()

    def _verify_helm_installation(self) -> None:
        """Verify Helm is installed and accessible."""
        try:
            result = self._run_helm_command(["version", "--short"])
            self.logger.info(f"Helm version: {result.strip()}")
        except Exception as e:
            self.logger.error(f"Helm not found or not accessible: {e}")
            raise

    def _run_helm_command(
        self,
        args: List[str],
        namespace: Optional[str] = None,
        timeout: int = 300
    ) -> str:
        """
        Run Helm command and return output.
        
        Args:
            args: Helm command arguments
            namespace: Kubernetes namespace
            timeout: Command timeout in seconds
            
        Returns:
            Command output
        """
        cmd = [self.helm_binary] + args
        
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        
        env = os.environ.copy()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                check=True
            )
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Helm command failed: {' '.join(cmd)}")
            self.logger.error(f"Error: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            self.logger.error(f"Helm command timed out: {' '.join(cmd)}")
            raise

    async def add_repository(self, repository: HelmRepository) -> bool:
        """
        Add Helm repository.
        
        Args:
            repository: Repository configuration
            
        Returns:
            True if repository added successfully, False otherwise
        """
        try:
            cmd = ["repo", "add", repository.name, repository.url]
            
            if repository.username and repository.password:
                cmd.extend(["--username", repository.username])
                cmd.extend(["--password", repository.password])
            
            if repository.cert_file:
                cmd.extend(["--cert-file", repository.cert_file])
            
            if repository.key_file:
                cmd.extend(["--key-file", repository.key_file])
            
            if repository.ca_file:
                cmd.extend(["--ca-file", repository.ca_file])
            
            self._run_helm_command(cmd)
            
            # Update repository cache
            await self.update_repositories()
            
            self.repositories[repository.name] = repository
            self.logger.info(f"Repository '{repository.name}' added successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add repository '{repository.name}': {e}")
            return False

    async def update_repositories(self) -> bool:
        """
        Update all Helm repositories.
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            self._run_helm_command(["repo", "update"])
            self.logger.info("Repositories updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update repositories: {e}")
            return False

    async def search_charts(self, keyword: str, repo: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Search for Helm charts.
        
        Args:
            keyword: Search keyword
            repo: Optional repository name to search in
            
        Returns:
            List of chart information
        """
        try:
            cmd = ["search", "repo", keyword]
            if repo:
                cmd = ["search", "repo", f"{repo}/{keyword}"]
            
            output = self._run_helm_command(cmd + ["--output", "json"])
            
            if output.strip():
                charts = json.loads(output)
                return [
                    {
                        "name": chart["name"],
                        "version": chart["version"],
                        "app_version": chart.get("app_version", ""),
                        "description": chart.get("description", "")
                    }
                    for chart in charts
                ]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to search charts with keyword '{keyword}': {e}")
            return []

    async def install_chart(
        self,
        release_name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        create_namespace: bool = True,
        wait: bool = True,
        timeout: str = "5m"
    ) -> bool:
        """
        Install Helm chart.
        
        Args:
            release_name: Name for the release
            chart: Chart name or path
            namespace: Target namespace
            values: Values to override
            version: Chart version to install
            create_namespace: Whether to create namespace if it doesn't exist
            wait: Wait for installation to complete
            timeout: Installation timeout
            
        Returns:
            True if installation successful, False otherwise
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["install", release_name, chart]
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            
            if create_namespace:
                cmd.append("--create-namespace")
            
            if version:
                cmd.extend(["--version", version])
            
            if wait:
                cmd.append("--wait")
            
            if timeout:
                cmd.extend(["--timeout", timeout])
            
            # Handle values
            if values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["--values", values_file])
                
                try:
                    self._run_helm_command(cmd, timeout=300)
                finally:
                    os.unlink(values_file)
            else:
                self._run_helm_command(cmd, timeout=300)
            
            # Store release information
            release_info = await self.get_release_info(release_name, namespace)
            if release_info:
                self.managed_releases[f"{namespace}/{release_name}"] = release_info
            
            self.logger.info(f"Chart '{chart}' installed as '{release_name}' successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install chart '{chart}' as '{release_name}': {e}")
            return False

    async def upgrade_release(
        self,
        release_name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        wait: bool = True,
        timeout: str = "5m"
    ) -> bool:
        """
        Upgrade Helm release.
        
        Args:
            release_name: Name of the release
            chart: Chart name or path
            namespace: Target namespace
            values: Values to override
            version: Chart version to upgrade to
            wait: Wait for upgrade to complete
            timeout: Upgrade timeout
            
        Returns:
            True if upgrade successful, False otherwise
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["upgrade", release_name, chart]
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            
            if version:
                cmd.extend(["--version", version])
            
            if wait:
                cmd.append("--wait")
            
            if timeout:
                cmd.extend(["--timeout", timeout])
            
            # Handle values
            if values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["--values", values_file])
                
                try:
                    self._run_helm_command(cmd, timeout=300)
                finally:
                    os.unlink(values_file)
            else:
                self._run_helm_command(cmd, timeout=300)
            
            # Update release information
            release_info = await self.get_release_info(release_name, namespace)
            if release_info:
                self.managed_releases[f"{namespace}/{release_name}"] = release_info
            
            self.logger.info(f"Release '{release_name}' upgraded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upgrade release '{release_name}': {e}")
            return False

    async def rollback_release(
        self,
        release_name: str,
        revision: Optional[int] = None,
        namespace: Optional[str] = None,
        wait: bool = True,
        timeout: str = "5m"
    ) -> bool:
        """
        Rollback Helm release.
        
        Args:
            release_name: Name of the release
            revision: Revision to rollback to (defaults to previous)
            namespace: Target namespace
            wait: Wait for rollback to complete
            timeout: Rollback timeout
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["rollback", release_name]
            
            if revision:
                cmd.append(str(revision))
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            
            if wait:
                cmd.append("--wait")
            
            if timeout:
                cmd.extend(["--timeout", timeout])
            
            self._run_helm_command(cmd, timeout=300)
            
            # Update release information
            release_info = await self.get_release_info(release_name, namespace)
            if release_info:
                self.managed_releases[f"{namespace}/{release_name}"] = release_info
            
            self.logger.info(f"Release '{release_name}' rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback release '{release_name}': {e}")
            return False

    async def uninstall_release(
        self,
        release_name: str,
        namespace: Optional[str] = None,
        keep_history: bool = False,
        wait: bool = True,
        timeout: str = "5m"
    ) -> bool:
        """
        Uninstall Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Target namespace
            keep_history: Keep release history
            wait: Wait for uninstallation to complete
            timeout: Uninstallation timeout
            
        Returns:
            True if uninstallation successful, False otherwise
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["uninstall", release_name]
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            
            if keep_history:
                cmd.append("--keep-history")
            
            if wait:
                cmd.append("--wait")
            
            if timeout:
                cmd.extend(["--timeout", timeout])
            
            self._run_helm_command(cmd, timeout=300)
            
            # Remove from managed releases
            release_key = f"{namespace}/{release_name}"
            if release_key in self.managed_releases:
                del self.managed_releases[release_key]
            
            self.logger.info(f"Release '{release_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall release '{release_name}': {e}")
            return False

    async def get_release_info(self, release_name: str, namespace: Optional[str] = None) -> Optional[HelmRelease]:
        """
        Get Helm release information.
        
        Args:
            release_name: Name of the release
            namespace: Target namespace
            
        Returns:
            Release information or None if not found
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["get", "all", release_name, "--output", "json"]
            output = self._run_helm_command(cmd, namespace=namespace)
            
            release_data = json.loads(output)
            
            return HelmRelease(
                name=release_data["name"],
                namespace=release_data["namespace"],
                chart=release_data["chart"]["metadata"]["name"],
                chart_version=release_data["chart"]["metadata"]["version"],
                app_version=release_data["chart"]["metadata"].get("appVersion", ""),
                status=ReleaseStatus(release_data["info"]["status"]),
                revision=release_data["version"],
                updated=release_data["info"]["last_deployed"],
                values=release_data.get("config", {})
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get release info for '{release_name}': {e}")
            return None

    async def list_releases(self, namespace: Optional[str] = None) -> List[HelmRelease]:
        """
        List all Helm releases.
        
        Args:
            namespace: Target namespace (all namespaces if None)
            
        Returns:
            List of releases
        """
        try:
            cmd = ["list", "--output", "json"]
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            else:
                cmd.append("--all-namespaces")
            
            output = self._run_helm_command(cmd)
            
            if output.strip():
                releases_data = json.loads(output)
                
                return [
                    HelmRelease(
                        name=release["name"],
                        namespace=release["namespace"],
                        chart=release["chart"],
                        chart_version=release["chart_version"] if "chart_version" in release else "",
                        app_version=release["app_version"] if "app_version" in release else "",
                        status=ReleaseStatus(release["status"]),
                        revision=release["revision"],
                        updated=release["updated"],
                        values={}
                    )
                    for release in releases_data
                ]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list releases: {e}")
            return []

    async def get_release_history(self, release_name: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get release history.
        
        Args:
            release_name: Name of the release
            namespace: Target namespace
            
        Returns:
            List of release revisions
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["history", release_name, "--output", "json"]
            output = self._run_helm_command(cmd, namespace=namespace)
            
            if output.strip():
                history_data = json.loads(output)
                return [
                    {
                        "revision": revision["revision"],
                        "updated": revision["updated"],
                        "status": revision["status"],
                        "chart": revision["chart"],
                        "app_version": revision.get("app_version", ""),
                        "description": revision.get("description", "")
                    }
                    for revision in history_data
                ]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get release history for '{release_name}': {e}")
            return []

    async def create_chart(self, chart_config: HelmChart, output_dir: str) -> bool:
        """
        Create new Helm chart.
        
        Args:
            chart_config: Chart configuration
            output_dir: Output directory for the chart
            
        Returns:
            True if chart created successfully, False otherwise
        """
        try:
            chart_dir = Path(output_dir) / chart_config.name
            
            # Create chart structure
            chart_dir.mkdir(parents=True, exist_ok=True)
            (chart_dir / "templates").mkdir(exist_ok=True)
            (chart_dir / "charts").mkdir(exist_ok=True)
            
            # Create Chart.yaml
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_config.name,
                "description": chart_config.description,
                "type": chart_config.chart_type.value,
                "version": chart_config.version,
                "appVersion": chart_config.app_version,
                "dependencies": chart_config.dependencies
            }
            
            with open(chart_dir / "Chart.yaml", "w") as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # Create values.yaml
            with open(chart_dir / "values.yaml", "w") as f:
                yaml.dump(chart_config.values, f, default_flow_style=False)
            
            # Create templates
            for template_name, template_content in chart_config.templates.items():
                with open(chart_dir / "templates" / template_name, "w") as f:
                    f.write(template_content)
            
            self.logger.info(f"Chart '{chart_config.name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create chart '{chart_config.name}': {e}")
            return False

    async def package_chart(self, chart_path: str, output_dir: str) -> Optional[str]:
        """
        Package Helm chart.
        
        Args:
            chart_path: Path to the chart directory
            output_dir: Output directory for the package
            
        Returns:
            Path to the packaged chart or None if failed
        """
        try:
            cmd = ["package", chart_path, "--destination", output_dir]
            
            output = self._run_helm_command(cmd)
            
            # Extract package path from output
            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith("Successfully packaged chart"):
                    package_path = line.split(": ")[-1]
                    self.logger.info(f"Chart packaged successfully: {package_path}")
                    return package_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to package chart at '{chart_path}': {e}")
            return None

    async def lint_chart(self, chart_path: str) -> Dict[str, Any]:
        """
        Lint Helm chart.
        
        Args:
            chart_path: Path to the chart directory
            
        Returns:
            Lint results
        """
        try:
            cmd = ["lint", chart_path, "--output", "json"]
            
            output = self._run_helm_command(cmd)
            
            if output.strip():
                lint_results = json.loads(output)
                return lint_results
            else:
                return {"status": "success", "errors": [], "warnings": []}
                
        except Exception as e:
            self.logger.error(f"Failed to lint chart at '{chart_path}': {e}")
            return {"status": "error", "errors": [str(e)], "warnings": []}

    async def template_chart(
        self,
        chart: str,
        values: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> str:
        """
        Render chart templates locally.
        
        Args:
            chart: Chart name or path
            values: Values to use for templating
            name: Release name
            namespace: Target namespace
            
        Returns:
            Rendered templates
        """
        try:
            cmd = ["template"]
            
            if name:
                cmd.append(name)
            
            cmd.append(chart)
            
            if namespace:
                cmd.extend(["--namespace", namespace])
            
            # Handle values
            if values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["--values", values_file])
                
                try:
                    output = self._run_helm_command(cmd)
                    return output
                finally:
                    os.unlink(values_file)
            else:
                output = self._run_helm_command(cmd)
                return output
                
        except Exception as e:
            self.logger.error(f"Failed to template chart '{chart}': {e}")
            return ""

    async def get_values(self, release_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get values for a release.
        
        Args:
            release_name: Name of the release
            namespace: Target namespace
            
        Returns:
            Release values
        """
        try:
            namespace = namespace or self.default_namespace
            
            cmd = ["get", "values", release_name, "--output", "json"]
            output = self._run_helm_command(cmd, namespace=namespace)
            
            if output.strip():
                return json.loads(output)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to get values for release '{release_name}': {e}")
            return {}

    async def validate_dependencies(self, chart_path: str) -> bool:
        """
        Validate chart dependencies.
        
        Args:
            chart_path: Path to the chart directory
            
        Returns:
            True if dependencies are valid, False otherwise
        """
        try:
            cmd = ["dependency", "build", chart_path]
            self._run_helm_command(cmd)
            
            self.logger.info(f"Dependencies validated for chart at '{chart_path}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate dependencies for chart at '{chart_path}': {e}")
            return False

    async def cleanup_releases(self, max_age_days: int = 30) -> bool:
        """
        Clean up old failed releases.
        
        Args:
            max_age_days: Maximum age in days for failed releases
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            releases = await self.list_releases()
            
            for release in releases:
                if release.status in [ReleaseStatus.FAILED, ReleaseStatus.SUPERSEDED]:
                    # Check if release is old enough to be cleaned up
                    from datetime import datetime, timedelta
                    try:
                        updated_time = datetime.fromisoformat(release.updated.replace('Z', '+00:00'))
                        if (datetime.now(updated_time.tzinfo) - updated_time).days > max_age_days:
                            await self.uninstall_release(
                                release.name,
                                release.namespace,
                                keep_history=False
                            )
                    except ValueError:
                        # Skip if we can't parse the date
                        continue
            
            self.logger.info("Release cleanup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup releases: {e}")
            return False
