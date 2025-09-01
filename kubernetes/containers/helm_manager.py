"""⚓ Helm Chart Manager - IA-Influencer-Agent Infrastructure
===========================================================
Expert: DevOps Engineer + Kubernetes Specialist + Helm Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Helm chart management and Kubernetes deployment automation.
Includes chart templating, dependency management, and release lifecycle.
"""

import os
import yaml
import json
import asyncio
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class ReleaseStatus(Enum):
    """
Helm release status"""

    UNKNOWN = "unknown"
    DEPLOYED = "deployed"
    UNINSTALLED = "uninstalled"
    SUPERSEDED = "superseded"
    FAILED = "failed"
    UNINSTALLING = "uninstalling"
    PENDING_INSTALL = "pending-install"
    PENDING_UPGRADE = "pending-upgrade"
    PENDING_ROLLBACK = "pending-rollback"

class ChartVersion(Enum):
    """Chart API versions"""

    V1 = "v1"
    V2 = "v2"

@dataclass
class HelmChart:
    """Helm chart configuration"""
    name: str
    version: str
    app_version: str
    description: str
    chart_path: str
    api_version: ChartVersion = ChartVersion.V2
    type: str = "application"
    keywords: List[str] = field(default_factory=list)
    home: str = ""
    sources: List[str] = field(default_factory=list)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    maintainers: List[Dict[str, str]] = field(default_factory=list)
    icon: str = ""
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class HelmRelease:
    """Helm release information"""
    name: str
    namespace: str
    chart: str
    version: str
    app_version: str
    status: ReleaseStatus
    revision: int
    updated: datetime
    values: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

@dataclass
class HelmRepository:
    """Helm repository configuration"""
    name: str
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None
    insecure_skip_tls_verify: bool = False

@dataclass
class DeploymentConfig:
    """
Deployment configuration"""
    release_name: str
    namespace: str
    chart_path: str
    values: Dict[str, Any] = field(default_factory=dict)
    values_files: List[str] = field(default_factory=list)
    set_values: Dict[str, str] = field(default_factory=dict)
    wait: bool = True
    timeout: int = 600
    atomic: bool = True
    cleanup_on_fail: bool = True
    create_namespace: bool = True

class HelmChartManager:
    """
Professional Helm chart manager"""
    
    def __init__(self, charts_path: str = "/app/charts", config_path: str = "/app/config/helm"):
        self.charts_path = Path(charts_path)
        self.config_path = Path(config_path)
        self.repositories = {}
        self.charts = {}
        self.releases = {}
        self.templates_cache = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize Helm chart manager"""
        try:
            # Check Helm installation
            if not await self._check_helm_installation():
                self.logger.error("❌ Helm is not installed or not accessible")
                return False
            
            # Create directories
            self.charts_path.mkdir(parents=True, exist_ok=True)
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing repositories
            await self._load_repositories()
            
            # Setup default repositories
            await self._setup_default_repositories()
            
            # Load existing charts
            await self._load_charts()
            
            # Create default charts for IA-Influencer
            await self._create_default_charts()
            
            # Load release information
            await self._load_releases()
            
            self.initialized = True
            self.logger.info("✅ HelmChartManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing HelmChartManager: {e}")
            return False
    
    async def _check_helm_installation(self) -> bool:
        """Check if Helm is installed"""
        try:
            result = subprocess.run(
                ["helm", "version", "--short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"✅ Helm found: {version}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error checking Helm installation: {e}")
            return False
    
    async def _load_repositories(self) -> None:
        """Load existing Helm repositories"""
        try:
            repo_file = self.config_path / "repositories.yml"
            if repo_file.exists():
                with open(repo_file, 'r') as f:
                    repos_data = yaml.safe_load(f)
                    
                for repo_data in repos_data.get('repositories', []):
                    repo = HelmRepository(**repo_data)
                    self.repositories[repo.name] = repo
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading repositories: {e}")
    
    async def _setup_default_repositories(self) -> None:
        """Setup default Helm repositories"""
        try:
            default_repos = [
                HelmRepository(
                    name="bitnami",
                    url="https://charts.bitnami.com/bitnami"
                ),
                HelmRepository(
                    name="prometheus-community",
                    url="https://prometheus-community.github.io/helm-charts"
                ),
                HelmRepository(
                    name="grafana",
                    url="https://grafana.github.io/helm-charts"
                ),
                HelmRepository(
                    name="jetstack",
                    url="https://charts.jetstack.io"
                ),
                HelmRepository(
                    name="ingress-nginx",
                    url="https://kubernetes.github.io/ingress-nginx"
                ),
                HelmRepository(
                    name="stable",
                    url="https://charts.helm.sh/stable"
                ),
                HelmRepository(
                    name="ia-influencer",
                    url="https://charts.ia-influencer-agent.com",
                    username="${CHART_REPO_USERNAME}",
                    password="${CHART_REPO_PASSWORD}"
                )
            ]
            
            for repo in default_repos:
                if repo.name not in self.repositories:
                    self.repositories[repo.name] = repo
                    await self.add_repository(repo)
            
            # Save repositories
            await self._save_repositories()
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default repositories: {e}")
    
    async def _save_repositories(self) -> None:
        """Save repositories configuration"""
        try:
            repo_file = self.config_path / "repositories.yml"
            repos_data = {
                "repositories": [asdict(repo) for repo in self.repositories.values()]
            }
            
            with open(repo_file, 'w') as f:
                yaml.dump(repos_data, f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving repositories: {e}")
    
    async def _load_charts(self) -> None:
        """Load existing charts"""
        try:
            chart_dirs = [d for d in self.charts_path.iterdir() if d.is_dir()]
            
            for chart_dir in chart_dirs:
                chart_yaml = chart_dir / "Chart.yaml"
                if chart_yaml.exists():
                    with open(chart_yaml, 'r') as f:
                        chart_data = yaml.safe_load(f)
                        
                    chart = HelmChart(
                        name=chart_data.get('name', chart_dir.name),
                        version=chart_data.get('version', '0.1.0'),
                        app_version=chart_data.get('appVersion', '1.0.0'),
                        description=chart_data.get('description', ''),
                        chart_path=str(chart_dir),
                        api_version=ChartVersion(chart_data.get('apiVersion', 'v2')),
                        type=chart_data.get('type', 'application'),
                        keywords=chart_data.get('keywords', []),
                        home=chart_data.get('home', ''),
                        sources=chart_data.get('sources', []),
                        dependencies=chart_data.get('dependencies', []),
                        maintainers=chart_data.get('maintainers', []),
                        icon=chart_data.get('icon', ''),
                        annotations=chart_data.get('annotations', {})
                    )
                    
                    self.charts[chart.name] = chart
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading charts: {e}")
    
    async def _create_default_charts(self) -> None:
        """Create default charts for IA-Influencer platform"""
        try:
            # Web API Chart
            web_api_chart = await self._create_web_api_chart()
            if web_api_chart:
                self.charts["ia-influencer-web-api"] = web_api_chart
            
            # AI Engine Chart
            ai_engine_chart = await self._create_ai_engine_chart()
            if ai_engine_chart:
                self.charts["ia-influencer-ai-engine"] = ai_engine_chart
            
            # Database Chart
            database_chart = await self._create_database_chart()
            if database_chart:
                self.charts["ia-influencer-database"] = database_chart
            
            # Full Platform Chart (umbrella)
            platform_chart = await self._create_platform_chart()
            if platform_chart:
                self.charts["ia-influencer-platform"] = platform_chart
                
        except Exception as e:
            self.logger.error(f"❌ Error creating default charts: {e}")
    
    async def _create_web_api_chart(self) -> Optional[HelmChart]:
        """Create Web API Helm chart"""
        try:
            chart_name = "ia-influencer-web-api"
            chart_path = self.charts_path / chart_name
            
            if chart_path.exists():
                return None  # Chart already exists
            
            chart_path.mkdir(parents=True, exist_ok=True)
            templates_path = chart_path / "templates"
            templates_path.mkdir(exist_ok=True)
            
            # Chart.yaml
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_name,
                "description": "IA-Influencer Web API Helm Chart",
                "type": "application",
                "version": "0.1.0",
                "appVersion": "1.0.0",
                "maintainers": [
                    {
                        "name": "Fahed Mlaiel",
                        "email": "mlaiel@live.de"
                    }
                ],
                "keywords": ["ia-influencer", "api", "web", "microservice"],
                "home": "https://ia-influencer-agent.com",
                "sources": ["https://github.com/fahed-mlaiel/ia-influencer-agent"]
            }
            
            with open(chart_path / "Chart.yaml", 'w') as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # values.yaml
            values_yaml = {
                "replicaCount": 3,
                "image": {
                    "repository": "ia-influencer/web-api",
                    "pullPolicy": "IfNotPresent",
                    "tag": "latest"
                },
                "imagePullSecrets": [],
                "nameOverride": "",
                "fullnameOverride": "",
                "serviceAccount": {
                    "create": True,
                    "annotations": {},
                    "name": ""
                },
                "podAnnotations": {},
                "podSecurityContext": {
                    "fsGroup": 2000
                },
                "securityContext": {
                    "capabilities": {
                        "drop": ["ALL"]
                    },
                    "readOnlyRootFilesystem": True,
                    "runAsNonRoot": True,
                    "runAsUser": 1000
                },
                "service": {
                    "type": "ClusterIP",
                    "port": 80,
                    "targetPort": 8000
                },
                "ingress": {
                    "enabled": True,
                    "className": "nginx",
                    "annotations": {
                        "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                        "nginx.ingress.kubernetes.io/rate-limit": "100"
                    },
                    "hosts": [
                        {
                            "host": "api.ia-influencer-agent.com",
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix"
                                }
                            ]
                        }
                    ],
                    "tls": [
                        {
                            "secretName": "api-tls",
                            "hosts": ["api.ia-influencer-agent.com"]
                        }
                    ]
                },
                "resources": {
                    "limits": {
                        "cpu": "500m",
                        "memory": "512Mi"
                    },
                    "requests": {
                        "cpu": "250m",
                        "memory": "256Mi"
                    }
                },
                "autoscaling": {
                    "enabled": True,
                    "minReplicas": 3,
                    "maxReplicas": 10,
                    "targetCPUUtilizationPercentage": 80,
                    "targetMemoryUtilizationPercentage": 80
                },
                "nodeSelector": {},
                "tolerations": [],
                "affinity": {
                    "podAntiAffinity": {
                        "preferredDuringSchedulingIgnoredDuringExecution": [
                            {
                                "weight": 100,
                                "podAffinityTerm": {
                                    "labelSelector": {
                                        "matchExpressions": [
                                            {
                                                "key": "app.kubernetes.io/name",
                                                "operator": "In",
                                                "values": [chart_name]
                                            }
                                        ]
                                    },
                                    "topologyKey": "kubernetes.io/hostname"
                                }
                            }
                        ]
                    }
                },
                "env": {
                    "DATABASE_URL": "postgresql://user:pass@ia-influencer-database:5432/ia_influencer",
                    "REDIS_URL": "redis://ia-influencer-redis:6379",
                    "LOG_LEVEL": "INFO"
                },
                "configMap": {
                    "create": True,
                    "data": {
                        "app.properties": "environment=production\napi.version=v1\n"
                    }
                },
                "secrets": {
                    "create": True,
                    "data": {
                        "db-password": "base64encodedpassword",
                        "jwt-secret": "base64encodedjwtsecret"
                    }
                }
            }
            
            with open(chart_path / "values.yaml", 'w') as f:
                yaml.dump(values_yaml, f, default_flow_style=False)
            
            # Template files
            await self._create_deployment_template(templates_path, chart_name, "web-api")
            await self._create_service_template(templates_path, chart_name)
            await self._create_ingress_template(templates_path, chart_name)
            await self._create_hpa_template(templates_path, chart_name)
            await self._create_configmap_template(templates_path, chart_name)
            await self._create_secret_template(templates_path, chart_name)
            await self._create_serviceaccount_template(templates_path, chart_name)
            
            chart = HelmChart(
                name=chart_name,
                version="0.1.0",
                app_version="1.0.0",
                description="IA-Influencer Web API Helm Chart",
                chart_path=str(chart_path)
            )
            
            self.logger.info(f"✅ Created Web API chart: {chart_name}")
            return chart
            
        except Exception as e:
            self.logger.error(f"❌ Error creating Web API chart: {e}")
            return None
    
    async def _create_ai_engine_chart(self) -> Optional[HelmChart]:
        """Create AI Engine Helm chart"""
        try:
            chart_name = "ia-influencer-ai-engine"
            chart_path = self.charts_path / chart_name
            
            if chart_path.exists():
                return None
            
            chart_path.mkdir(parents=True, exist_ok=True)
            templates_path = chart_path / "templates"
            templates_path.mkdir(exist_ok=True)
            
            # Chart.yaml
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_name,
                "description": "IA-Influencer AI Engine Helm Chart",
                "type": "application",
                "version": "0.1.0",
                "appVersion": "1.0.0",
                "maintainers": [{"name": "Fahed Mlaiel", "email": "mlaiel@live.de"}],
                "keywords": ["ia-influencer", "ai", "machine-learning", "gpu"]
            }
            
            with open(chart_path / "Chart.yaml", 'w') as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # values.yaml for AI Engine
            values_yaml = {
                "replicaCount": 2,
                "image": {
                    "repository": "ia-influencer/ai-engine",
                    "pullPolicy": "IfNotPresent",
                    "tag": "latest"
                },
                "resources": {
                    "limits": {
                        "cpu": "4000m",
                        "memory": "8Gi",
                        "nvidia.com/gpu": 1
                    },
                    "requests": {
                        "cpu": "2000m",
                        "memory": "4Gi",
                        "nvidia.com/gpu": 1
                    }
                },
                "nodeSelector": {
                    "accelerator": "nvidia-tesla-v100"
                },
                "tolerations": [
                    {
                        "key": "nvidia.com/gpu",
                        "operator": "Exists",
                        "effect": "NoSchedule"
                    }
                ],
                "env": {
                    "CUDA_VISIBLE_DEVICES": "0",
                    "MODEL_PATH": "/app/models",
                    "BATCH_SIZE": "32"
                },
                "persistence": {
                    "enabled": True,
                    "storageClass": "fast-ssd",
                    "size": "100Gi",
                    "mountPath": "/app/models"
                }
            }
            
            with open(chart_path / "values.yaml", 'w') as f:
                yaml.dump(values_yaml, f, default_flow_style=False)
            
            # Create AI-specific templates
            await self._create_deployment_template(templates_path, chart_name, "ai-engine")
            await self._create_service_template(templates_path, chart_name)
            await self._create_pvc_template(templates_path, chart_name)
            
            chart = HelmChart(
                name=chart_name,
                version="0.1.0",
                app_version="1.0.0",
                description="IA-Influencer AI Engine Helm Chart",
                chart_path=str(chart_path)
            )
            
            self.logger.info(f"✅ Created AI Engine chart: {chart_name}")
            return chart
            
        except Exception as e:
            self.logger.error(f"❌ Error creating AI Engine chart: {e}")
            return None
    
    async def _create_database_chart(self) -> Optional[HelmChart]:
        """Create Database Helm chart"""
        try:
            chart_name = "ia-influencer-database"
            chart_path = self.charts_path / chart_name
            
            if chart_path.exists():
                return None
            
            chart_path.mkdir(parents=True, exist_ok=True)
            templates_path = chart_path / "templates"
            templates_path.mkdir(exist_ok=True)
            
            # Chart.yaml
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_name,
                "description": "IA-Influencer Database Helm Chart",
                "type": "application",
                "version": "0.1.0",
                "appVersion": "15.0.0",
                "dependencies": [
                    {
                        "name": "postgresql",
                        "version": "12.x.x",
                        "repository": "https://charts.bitnami.com/bitnami"
                    },
                    {
                        "name": "redis",
                        "version": "17.x.x",
                        "repository": "https://charts.bitnami.com/bitnami"
                    }
                ]
            }
            
            with open(chart_path / "Chart.yaml", 'w') as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # values.yaml
            values_yaml = {
                "postgresql": {
                    "enabled": True,
                    "auth": {
                        "postgresPassword": "supersecret",
                        "username": "ia_user",
                        "password": "ia_password",
                        "database": "ia_influencer"
                    },
                    "primary": {
                        "persistence": {
                            "enabled": True,
                            "size": "50Gi",
                            "storageClass": "fast-ssd"
                        },
                        "resources": {
                            "limits": {
                                "cpu": "1000m",
                                "memory": "2Gi"
                            },
                            "requests": {
                                "cpu": "500m",
                                "memory": "1Gi"
                            }
                        }
                    }
                },
                "redis": {
                    "enabled": True,
                    "auth": {
                        "enabled": True,
                        "password": "redis_password"
                    },
                    "master": {
                        "persistence": {
                            "enabled": True,
                            "size": "10Gi"
                        }
                    }
                }
            }
            
            with open(chart_path / "values.yaml", 'w') as f:
                yaml.dump(values_yaml, f, default_flow_style=False)
            
            chart = HelmChart(
                name=chart_name,
                version="0.1.0",
                app_version="15.0.0",
                description="IA-Influencer Database Helm Chart",
                chart_path=str(chart_path)
            )
            
            self.logger.info(f"✅ Created Database chart: {chart_name}")
            return chart
            
        except Exception as e:
            self.logger.error(f"❌ Error creating Database chart: {e}")
            return None
    
    async def _create_platform_chart(self) -> Optional[HelmChart]:
        """Create umbrella platform chart"""
        try:
            chart_name = "ia-influencer-platform"
            chart_path = self.charts_path / chart_name
            
            if chart_path.exists():
                return None
            
            chart_path.mkdir(parents=True, exist_ok=True)
            
            # Chart.yaml with dependencies
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_name,
                "description": "IA-Influencer Complete Platform Helm Chart",
                "type": "application",
                "version": "0.1.0",
                "appVersion": "1.0.0",
                "dependencies": [
                    {
                        "name": "ia-influencer-web-api",
                        "version": "0.1.0",
                        "repository": "file://../ia-influencer-web-api"
                    },
                    {
                        "name": "ia-influencer-ai-engine",
                        "version": "0.1.0",
                        "repository": "file://../ia-influencer-ai-engine"
                    },
                    {
                        "name": "ia-influencer-database",
                        "version": "0.1.0",
                        "repository": "file://../ia-influencer-database"
                    }
                ]
            }
            
            with open(chart_path / "Chart.yaml", 'w') as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # values.yaml for platform
            values_yaml = {
                "global": {
                    "imageRegistry": "registry.ia-influencer-agent.com",
                    "imagePullSecrets": ["ia-influencer-registry"],
                    "storageClass": "fast-ssd"
                },
                "ia-influencer-web-api": {
                    "enabled": True,
                    "replicaCount": 3
                },
                "ia-influencer-ai-engine": {
                    "enabled": True,
                    "replicaCount": 2
                },
                "ia-influencer-database": {
                    "enabled": True,
                    "postgresql": {
                        "primary": {
                            "persistence": {
                                "size": "100Gi"
                            }
                        }
                    }
                }
            }
            
            with open(chart_path / "values.yaml", 'w') as f:
                yaml.dump(values_yaml, f, default_flow_style=False)
            
            chart = HelmChart(
                name=chart_name,
                version="0.1.0",
                app_version="1.0.0",
                description="IA-Influencer Complete Platform Helm Chart",
                chart_path=str(chart_path)
            )
            
            self.logger.info(f"✅ Created Platform chart: {chart_name}")
            return chart
            
        except Exception as e:
            self.logger.error(f"❌ Error creating Platform chart: {e}")
            return None
    
    async def _create_deployment_template(self, templates_path: Path, chart_name: str, app_type: str) -> None:
        """Create deployment template"""
        try:
            deployment_template = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  {{{{- end }}}}
  selector:
    matchLabels:
      {{{{- include "{chart_name}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      {{{{- with .Values.podAnnotations }}}}
      annotations:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      labels:
        {{{{- include "{chart_name}.selectorLabels" . | nindent 8 }}}}
    spec:
      {{{{- with .Values.imagePullSecrets }}}}
      imagePullSecrets:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      serviceAccountName: {{{{ include "{chart_name}.serviceAccountName" . }}}}
      securityContext:
        {{{{- toYaml .Values.podSecurityContext | nindent 8 }}}}
      containers:
        - name: {{{{ .Chart.Name }}}}
          securityContext:
            {{{{- toYaml .Values.securityContext | nindent 12 }}}}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
          imagePullPolicy: {{{{ .Values.image.pullPolicy }}}}
          ports:
            - name: http
              containerPort: {{{{ .Values.service.targetPort | default 8000 }}}}
              protocol: TCP
          env:
            {{{{- range $key, $value := .Values.env }}}}
            - name: {{{{ $key }}}}
              value: "{{{{ $value }}}}"
            {{{{- end }}}}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{{{- toYaml .Values.resources | nindent 12 }}}}
          {{{{- if .Values.persistence.enabled }}}}
          volumeMounts:
            - name: data
              mountPath: {{{{ .Values.persistence.mountPath | default "/app/data" }}}}
          {{{{- end }}}}
      {{{{- if .Values.persistence.enabled }}}}
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: {{{{ include "{chart_name}.fullname" . }}}}-data
      {{{{- end }}}}
      {{{{- with .Values.nodeSelector }}}}
      nodeSelector:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.affinity }}}}
      affinity:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.tolerations }}}}
      tolerations:
        {{{{- toYaml . | nindent 8 }}}}
      {{{{- end }}}}
"""
            
            with open(templates_path / "deployment.yaml", 'w') as f:
                f.write(deployment_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating deployment template: {e}")
    
    async def _create_service_template(self, templates_path: Path, chart_name: str) -> None:
        """Create service template"""
        try:
            service_template = f"""
apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  type: {{{{ .Values.service.type }}}}
  ports:
    - port: {{{{ .Values.service.port }}}}
      targetPort: {{{{ .Values.service.targetPort | default "http" }}}}
      protocol: TCP
      name: http
  selector:
    {{{{- include "{chart_name}.selectorLabels" . | nindent 4 }}}}
"""
            
            with open(templates_path / "service.yaml", 'w') as f:
                f.write(service_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating service template: {e}")
    
    async def _create_ingress_template(self, templates_path: Path, chart_name: str) -> None:
        """Create ingress template"""
        try:
            ingress_template = f"""{{{{- if .Values.ingress.enabled -}}}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
  {{{{- with .Values.ingress.annotations }}}}
  annotations:
    {{{{- toYaml . | nindent 4 }}}}
  {{{{- end }}}}
spec:
  {{{{- if and .Values.ingress.className (semverCompare ">=1.18-0" .Capabilities.KubeVersion.GitVersion) }}}}
  ingressClassName: {{{{ .Values.ingress.className }}}}
  {{{{- end }}}}
  {{{{- if .Values.ingress.tls }}}}
  tls:
    {{{{- range .Values.ingress.tls }}}}
    - hosts:
        {{{{- range .hosts }}}}
        - {{{{ . | quote }}}}
        {{{{- end }}}}
      secretName: {{{{ .secretName }}}}
    {{{{- end }}}}
  {{{{- end }}}}
  rules:
    {{{{- range .Values.ingress.hosts }}}}
    - host: {{{{ .host | quote }}}}
      http:
        paths:
          {{{{- range .paths }}}}
          - path: {{{{ .path }}}}
            {{{{- if and .pathType (semverCompare ">=1.18-0" $.Capabilities.KubeVersion.GitVersion) }}}}
            pathType: {{{{ .pathType }}}}
            {{{{- end }}}}
            backend:
              {{{{- if semverCompare ">=1.19-0" $.Capabilities.KubeVersion.GitVersion }}}}
              service:
                name: {{{{ include "{chart_name}.fullname" $ }}}}
                port:
                  number: {{{{ $.Values.service.port }}}}
              {{{{- else }}}}
              serviceName: {{{{ include "{chart_name}.fullname" $ }}}}
              servicePort: {{{{ $.Values.service.port }}}}
              {{{{- end }}}}
          {{{{- end }}}}
    {{{{- end }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "ingress.yaml", 'w') as f:
                f.write(ingress_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating ingress template: {e}")
    
    async def _create_hpa_template(self, templates_path: Path, chart_name: str) -> None:
        """Create HPA template"""
        try:
            hpa_template = f"""{{{{- if .Values.autoscaling.enabled }}}}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{{{ include "{chart_name}.fullname" . }}}}
  minReplicas: {{{{ .Values.autoscaling.minReplicas }}}}
  maxReplicas: {{{{ .Values.autoscaling.maxReplicas }}}}
  metrics:
    {{{{- if .Values.autoscaling.targetCPUUtilizationPercentage }}}}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{{{ .Values.autoscaling.targetCPUUtilizationPercentage }}}}
    {{{{- end }}}}
    {{{{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}}}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{{{ .Values.autoscaling.targetMemoryUtilizationPercentage }}}}
    {{{{- end }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "hpa.yaml", 'w') as f:
                f.write(hpa_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating HPA template: {e}")
    
    async def _create_configmap_template(self, templates_path: Path, chart_name: str) -> None:
        """Create ConfigMap template"""
        try:
            configmap_template = f"""{{{{- if .Values.configMap.create }}}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
data:
  {{{{- range $key, $value := .Values.configMap.data }}}}
  {{{{ $key }}}}: |
    {{{{ $value | nindent 4 }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "configmap.yaml", 'w') as f:
                f.write(configmap_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating ConfigMap template: {e}")
    
    async def _create_secret_template(self, templates_path: Path, chart_name: str) -> None:
        """Create Secret template"""
        try:
            secret_template = f"""{{{{- if .Values.secrets.create }}}}
apiVersion: v1
kind: Secret
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
type: Opaque
data:
  {{{{- range $key, $value := .Values.secrets.data }}}}
  {{{{ $key }}}}: {{{{ $value }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "secret.yaml", 'w') as f:
                f.write(secret_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating Secret template: {e}")
    
    async def _create_serviceaccount_template(self, templates_path: Path, chart_name: str) -> None:
        """Create ServiceAccount template"""
        try:
            serviceaccount_template = f"""{{{{- if .Values.serviceAccount.create -}}}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{{{ include "{chart_name}.serviceAccountName" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
  {{{{- with .Values.serviceAccount.annotations }}}}
  annotations:
    {{{{- toYaml . | nindent 4 }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "serviceaccount.yaml", 'w') as f:
                f.write(serviceaccount_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating ServiceAccount template: {e}")
    
    async def _create_pvc_template(self, templates_path: Path, chart_name: str) -> None:
        """Create PVC template"""
        try:
            pvc_template = f"""{{{{- if .Values.persistence.enabled }}}}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}-data
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  accessModes:
    - ReadWriteOnce
  {{{{- if .Values.persistence.storageClass }}}}
  storageClassName: {{{{ .Values.persistence.storageClass }}}}
  {{{{- end }}}}
  resources:
    requests:
      storage: {{{{ .Values.persistence.size }}}}
{{{{- end }}}}
"""
            
            with open(templates_path / "pvc.yaml", 'w') as f:
                f.write(pvc_template)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating PVC template: {e}")
    
    async def _load_releases(self) -> None:
        """Load existing Helm releases"""
        try:
            result = subprocess.run(
                ["helm", "list", "--all-namespaces", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                releases_data = json.loads(result.stdout)
                
                for release_data in releases_data:
                    release = HelmRelease(
                        name=release_data.get("name", ""),
                        namespace=release_data.get("namespace", ""),
                        chart=release_data.get("chart", ""),
                        version=release_data.get("app_version", ""),
                        app_version=release_data.get("app_version", ""),
                        status=ReleaseStatus(release_data.get("status", "unknown").lower()),
                        revision=int(release_data.get("revision", 1)),
                        updated=datetime.fromisoformat(release_data.get("updated", "").replace("Z", "+00:00"))
                    )
                    
                    self.releases[f"{release.namespace}/{release.name}"] = release
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading releases: {e}")
    
    async def add_repository(self, repository: HelmRepository) -> bool:
        """Add Helm repository"""
        try:
            cmd = ["helm", "repo", "add", repository.name, repository.url]
            
            if repository.username and repository.password:
                cmd.extend(["--username", repository.username, "--password", repository.password])
            
            if repository.cert_file:
                cmd.extend(["--cert-file", repository.cert_file])
            
            if repository.key_file:
                cmd.extend(["--key-file", repository.key_file])
            
            if repository.ca_file:
                cmd.extend(["--ca-file", repository.ca_file])
            
            if repository.insecure_skip_tls_verify:
                cmd.append("--insecure-skip-tls-verify")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.repositories[repository.name] = repository
                await self._save_repositories()
                
                # Update repository
                await self.update_repository(repository.name)
                
                self.logger.info(f"✅ Added repository: {repository.name}")
                return True
            else:
                self.logger.error(f"❌ Failed to add repository {repository.name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error adding repository: {e}")
            return False
    
    async def update_repository(self, repo_name: str = None) -> bool:
        """Update Helm repositories"""
        try:
            if repo_name:
                cmd = ["helm", "repo", "update", repo_name]
            else:
                cmd = ["helm", "repo", "update"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Updated repository: {repo_name or 'all'}")
                return True
            else:
                self.logger.error(f"❌ Failed to update repository: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error updating repository: {e}")
            return False
    
    async def install_release(self, config: DeploymentConfig) -> bool:
        """Install Helm release"""
        try:
            cmd = [
                "helm", "install", config.release_name, config.chart_path,
                "--namespace", config.namespace
            ]
            
            if config.create_namespace:
                cmd.append("--create-namespace")
            
            if config.wait:
                cmd.extend(["--wait", "--timeout", f"{config.timeout}s"])
            
            if config.atomic:
                cmd.append("--atomic")
            
            if config.cleanup_on_fail:
                cmd.append("--cleanup-on-fail")
            
            # Add values files
            for values_file in config.values_files:
                cmd.extend(["-f", values_file])
            
            # Add set values
            for key, value in config.set_values.items():
                cmd.extend(["--set", f"{key}={value}"])
            
            # Add values from dict
            if config.values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config.values, f)
                    cmd.extend(["-f", f.name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout + 60)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Installed release: {config.release_name}")
                await self._load_releases()  # Refresh releases
                return True
            else:
                self.logger.error(f"❌ Failed to install release {config.release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error installing release: {e}")
            return False
    
    async def upgrade_release(self, config: DeploymentConfig) -> bool:
        """Upgrade Helm release"""
        try:
            cmd = [
                "helm", "upgrade", config.release_name, config.chart_path,
                "--namespace", config.namespace
            ]
            
            if config.wait:
                cmd.extend(["--wait", "--timeout", f"{config.timeout}s"])
            
            if config.atomic:
                cmd.append("--atomic")
            
            if config.cleanup_on_fail:
                cmd.append("--cleanup-on-fail")
            
            # Add values files
            for values_file in config.values_files:
                cmd.extend(["-f", values_file])
            
            # Add set values
            for key, value in config.set_values.items():
                cmd.extend(["--set", f"{key}={value}"])
            
            # Add values from dict
            if config.values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config.values, f)
                    cmd.extend(["-f", f.name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout + 60)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Upgraded release: {config.release_name}")
                await self._load_releases()  # Refresh releases
                return True
            else:
                self.logger.error(f"❌ Failed to upgrade release {config.release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error upgrading release: {e}")
            return False
    
    async def uninstall_release(self, release_name: str, namespace: str, keep_history: bool = False) -> bool:
        """Uninstall Helm release"""
        try:
            cmd = ["helm", "uninstall", release_name, "--namespace", namespace]
            
            if keep_history:
                cmd.append("--keep-history")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Uninstalled release: {release_name}")
                
                # Remove from releases
                release_key = f"{namespace}/{release_name}"
                if release_key in self.releases:
                    del self.releases[release_key]
                
                return True
            else:
                self.logger.error(f"❌ Failed to uninstall release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error uninstalling release: {e}")
            return False
    
    async def rollback_release(self, release_name: str, namespace: str, revision: int = None) -> bool:
        """Rollback Helm release"""
        try:
            cmd = ["helm", "rollback", release_name, "--namespace", namespace]
            
            if revision:
                cmd.append(str(revision))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Rolled back release: {release_name}")
                await self._load_releases()  # Refresh releases
                return True
            else:
                self.logger.error(f"❌ Failed to rollback release {release_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error rolling back release: {e}")
            return False
    
    async def get_release_values(self, release_name: str, namespace: str) -> Dict[str, Any]:
        """Get release values"""
        try:
            result = subprocess.run([
                "helm", "get", "values", release_name,
                "--namespace", namespace,
                "--output", "json"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"❌ Failed to get values for release {release_name}: {result.stderr}")
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting release values: {e}")
            return {}
    
    async def get_release_manifest(self, release_name: str, namespace: str) -> str:
        """Get release manifest"""
        try:
            result = subprocess.run([
                "helm", "get", "manifest", release_name,
                "--namespace", namespace
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"❌ Failed to get manifest for release {release_name}: {result.stderr}")
                return ""
                
        except Exception as e:
            self.logger.error(f"❌ Error getting release manifest: {e}")
            return ""
    
    async def template_chart(self, chart_path: str, values: Dict[str, Any] = None) -> str:
        """Template chart without installing"""
        try:
            cmd = ["helm", "template", chart_path]
            
            # Add values from dict
            if values:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(values, f)
                    cmd.extend(["-f", f.name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"❌ Failed to template chart {chart_path}: {result.stderr}")
                return ""
                
        except Exception as e:
            self.logger.error(f"❌ Error templating chart: {e}")
            return ""
    
    async def validate_chart(self, chart_path: str) -> Tuple[bool, List[str]]:
        """Validate Helm chart"""
        try:
            errors = []
            
            # Lint chart
            result = subprocess.run([
                "helm", "lint", chart_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                errors.append(f"Lint errors: {result.stderr}")
            
            # Template chart to check for errors
            template_result = await self.template_chart(chart_path)
            if not template_result:
                errors.append("Failed to template chart")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Error validating chart: {e}")
            return False, [str(e)]
    
    async def package_chart(self, chart_path: str, destination: str = None) -> str:
        """Package Helm chart"""
        try:
            cmd = ["helm", "package", chart_path]
            
            if destination:
                cmd.extend(["--destination", destination])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Extract package path from output
                output_lines = result.stdout.strip().split('\n')
                package_path = output_lines[-1].split(': ')[-1]
                
                self.logger.info(f"✅ Packaged chart: {package_path}")
                return package_path
            else:
                self.logger.error(f"❌ Failed to package chart {chart_path}: {result.stderr}")
                return ""
                
        except Exception as e:
            self.logger.error(f"❌ Error packaging chart: {e}")
            return ""
    
    async def search_charts(self, keyword: str, repository: str = None) -> List[Dict[str, Any]]:
        """Search for charts"""
        try:
            cmd = ["helm", "search", "repo", keyword, "--output", "json"]
            
            if repository:
                cmd.append(f"{repository}/{keyword}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"❌ Failed to search charts: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error searching charts: {e}")
            return []
    
    async def get_chart_history(self, release_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get release history"""
        try:
            result = subprocess.run([
                "helm", "history", release_name,
                "--namespace", namespace,
                "--output", "json"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"❌ Failed to get history for release {release_name}: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error getting chart history: {e}")
            return []

__all__ = [
    "HelmChartManager",
    "HelmChart",
    "HelmRelease",
    "HelmRepository",
    "DeploymentConfig",
    "ReleaseStatus",
    "ChartVersion"
]
