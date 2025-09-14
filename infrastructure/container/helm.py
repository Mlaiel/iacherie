"""Helm Infrastructure Management - Consolidated Module
=====================================================
All Helm functionality consolidated into a single module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

import asyncio
import logging
import subprocess
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class ChartType(Enum):
    """Helm chart types"""
    APPLICATION = "application"
    LIBRARY = "library"

class ReleaseStatus(Enum):
    """Helm release status"""
    DEPLOYED = "deployed"
    UNINSTALLED = "uninstalled"
    SUPERSEDED = "superseded"
    FAILED = "failed"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    PENDING_ROLLBACK = "pending-rollback"

@dataclass
class HelmChartConfig:
    """Helm chart configuration"""
    name: str
    version: str
    description: str
    chart_type: ChartType = ChartType.APPLICATION
    app_version: Optional[str] = None
    dependencies: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class HelmReleaseConfig:
    """Helm release configuration"""
    name: str
    chart: str
    namespace: str = "default"
    values: Dict[str, Any] = field(default_factory=dict)
    timeout: str = "300s"
    wait: bool = True

class HelmManager:
    """Unified Helm management interface"""
    
    def __init__(self) -> None:
        self.chart_manager = ChartManager()
        self.release_manager = HelmReleaseManager()
        self.repository_manager = RepositoryManager()
        self.logger = logging.getLogger(__name__)

class ChartManager:
    """Helm chart management"""
    
    def __init__(self) -> None:
        self.charts = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_chart(self, config: HelmChartConfig) -> bool:
        """Create Helm chart"""
        try:
            self.logger.info(f"Creating Helm chart: {config.name}")
            
            # Create chart directory structure
            chart_path = Path(f"charts/{config.name}")
            chart_path.mkdir(parents=True, exist_ok=True)
            
            # Create Chart.yaml
            await self._create_chart_yaml(chart_path, config)
            
            # Create default templates
            await self._create_default_templates(chart_path)
            
            # Create values.yaml
            await self._create_values_yaml(chart_path)
            
            self.charts[config.name] = config
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create chart: {e}")
            return False
    
    async def _create_chart_yaml(self, chart_path -> None: Path, config -> None: HelmChartConfig) -> None:
        """Create Chart.yaml file"""
        chart_yaml = {
            'apiVersion': 'v2',
            'name': config.name,
            'description': config.description,
            'type': config.chart_type.value,
            'version': config.version
        }
        
        if config.app_version:
            chart_yaml['appVersion'] = config.app_version
        
        if config.dependencies:
            chart_yaml['dependencies'] = config.dependencies
        
        with open(chart_path / 'Chart.yaml', 'w') as f:
            yaml.dump(chart_yaml, f, default_flow_style=False)
    
    async def _create_default_templates(self, chart_path -> None: Path) -> None:
        """Create default template files"""
        templates_path = chart_path / 'templates'
        templates_path.mkdir(exist_ok=True)
        
        # Create deployment template
        deployment_template = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "chart.fullname" . }}
  labels:
    {{- include "chart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "chart.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
'''
        
        with open(templates_path / 'deployment.yaml', 'w') as f:
            f.write(deployment_template)
        
        # Create service template
        service_template = '''
apiVersion: v1
kind: Service
metadata:
  name: {{ include "chart.fullname" . }}
  labels:
    {{- include "chart.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "chart.selectorLabels" . | nindent 4 }}
'''
        
        with open(templates_path / 'service.yaml', 'w') as f:
            f.write(service_template)
    
    async def _create_values_yaml(self, chart_path -> None: Path) -> None:
        """Create values.yaml file"""
        values = {
            'replicaCount': 1,
            'image': {
                'repository': 'nginx',
                'pullPolicy': 'IfNotPresent',
                'tag': 'latest'
            },
            'service': {
                'type': 'ClusterIP',
                'port': 80
            },
            'ingress': {
                'enabled': False
            },
            'resources': {},
            'autoscaling': {
                'enabled': False,
                'minReplicas': 1,
                'maxReplicas': 100,
                'targetCPUUtilizationPercentage': 80
            }
        }
        
        with open(chart_path / 'values.yaml', 'w') as f:
            yaml.dump(values, f, default_flow_style=False)

class HelmReleaseManager:
    """Helm release management"""
    
    def __init__(self) -> None:
        self.releases = {}
        self.logger = logging.getLogger(__name__)
    
    async def install_release(self, config: HelmReleaseConfig) -> bool:
        """Install Helm release"""
        try:
            self.logger.info(f"Installing Helm release: {config.name}")
            
            cmd = [
                "helm", "install", config.name, config.chart,
                "--namespace", config.namespace,
                "--timeout", config.timeout
            ]
            
            if config.wait:
                cmd.append("--wait")
            
            # Add values
            if config.values:
                values_file = f"/tmp/{config.name}-values.yaml"
                with open(values_file, 'w') as f:
                    yaml.dump(config.values, f)
                cmd.extend(["--values", values_file])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.releases[config.name] = {
                'name': config.name,
                'chart': config.chart,
                'namespace': config.namespace,
                'status': ReleaseStatus.DEPLOYED,
                'revision': 1
            }
            
            self.logger.info(f"Release {config.name} installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install release: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to install release: {e}")
            return False
    
    async def upgrade_release(self, 
                            release_name: str, 
                            chart: str,
                            values: Optional[Dict[str, Any]] = None) -> bool:
        """Upgrade Helm release"""
        try:
            self.logger.info(f"Upgrading Helm release: {release_name}")
            
            cmd = [
                "helm", "upgrade", release_name, chart,
                "--wait"
            ]
            
            if values:
                values_file = f"/tmp/{release_name}-values.yaml"
                with open(values_file, 'w') as f:
                    yaml.dump(values, f)
                cmd.extend(["--values", values_file])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if release_name in self.releases:
                self.releases[release_name]['revision'] += 1
            
            self.logger.info(f"Release {release_name} upgraded successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to upgrade release: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to upgrade release: {e}")
            return False
    
    async def uninstall_release(self, release_name: str) -> bool:
        """Uninstall Helm release"""
        try:
            self.logger.info(f"Uninstalling Helm release: {release_name}")
            
            cmd = ["helm", "uninstall", release_name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if release_name in self.releases:
                self.releases[release_name]['status'] = ReleaseStatus.UNINSTALLED
            
            self.logger.info(f"Release {release_name} uninstalled successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to uninstall release: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to uninstall release: {e}")
            return False

class RepositoryManager:
    """Helm repository management"""
    
    def __init__(self) -> None:
        self.repositories = {}
        self.logger = logging.getLogger(__name__)
    
    async def add_repository(self, name: str, url: str) -> bool:
        """Add Helm repository"""
        try:
            self.logger.info(f"Adding Helm repository: {name}")
            
            cmd = ["helm", "repo", "add", name, url]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.repositories[name] = url
            self.logger.info(f"Repository {name} added successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to add repository: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to add repository: {e}")
            return False
    
    async def update_repositories(self) -> bool:
        """Update Helm repositories"""
        try:
            self.logger.info("Updating Helm repositories")
            
            cmd = ["helm", "repo", "update"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("Repositories updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update repositories: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update repositories: {e}")
            return False

# Global instances
helm_manager = HelmManager()
chart_manager = ChartManager()
helm_release_manager = HelmReleaseManager()
repository_manager = RepositoryManager()

__all__ = [
    "HelmManager",
    "ChartManager",
    "HelmReleaseManager",
    "RepositoryManager",
    "HelmChartConfig",
    "HelmReleaseConfig",
    "ChartType",
    "ReleaseStatus",
    "helm_manager",
    "chart_manager",
    "helm_release_manager",
    "repository_manager"
]