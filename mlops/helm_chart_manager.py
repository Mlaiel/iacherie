"""
Helm Chart Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
⚓ Helm Chart Manager - Enterprise MLOps Platform
DevOps Expertise: Manager de Helm charts pour applications ML standardisées

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import os
import subprocess
from pathlib import Path
import tempfile
import shutil
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Types de charts Helm"""
    ML_MODEL_SERVING = "ml_model_serving"
    BATCH_PROCESSING = "batch_processing"
    STREAMING_PIPELINE = "streaming_pipeline"
    MODEL_TRAINING = "model_training"
    DATA_PIPELINE = "data_pipeline"
    MONITORING_STACK = "monitoring_stack"
    SECURITY_STACK = "security_stack"

class CreatorService(Enum):
    """Services par type de créateur"""
    MUSICIAN_AUDIO_SERVICE = "musician_audio_service"
    MUSICIAN_STREAMING_SERVICE = "musician_streaming_service"
    BLOGGER_CONTENT_SERVICE = "blogger_content_service"
    BLOGGER_SEO_SERVICE = "blogger_seo_service"
    PHOTOGRAPHER_IMAGE_SERVICE = "photographer_image_service"
    PHOTOGRAPHER_PORTFOLIO_SERVICE = "photographer_portfolio_service"
    INFLUENCER_ANALYTICS_SERVICE = "influencer_analytics_service"
    INFLUENCER_SOCIAL_SERVICE = "influencer_social_service"
    COMEDIAN_PERFORMANCE_SERVICE = "comedian_performance_service"
    COMEDIAN_CONTENT_SERVICE = "comedian_content_service"

class DeploymentEnvironment(Enum):
    """Environnements de déploiement"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class HelmChart:
    """Configuration d'un chart Helm"""
    chart_name: str
    chart_type: ChartType
    creator_service: CreatorService
    version: str
    description: str
    app_version: str
    chart_path: str
    values_files: Dict[DeploymentEnvironment, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HelmRelease:
    """Release Helm déployée"""
    release_name: str
    chart: HelmChart
    environment: DeploymentEnvironment
    namespace: str
    status: str
    revision: int
    values_override: Dict[str, Any] = field(default_factory=dict)
    deployed_at: datetime = field(default_factory=datetime.now)
    last_deployment: Optional[datetime] = None
    rollback_available: bool = True

@dataclass
class ChartTemplate:
    """Template de chart par créateur"""
    template_name: str
    creator_service: CreatorService
    base_chart_type: ChartType
    template_files: Dict[str, str]
    default_values: Dict[str, Any]
    required_variables: List[str]
    description: str

class HelmChartManager:
    """
    Manager de Helm charts pour applications ML enterprise
    
    Fonctionnalités:
    - Génération automatique de charts par créateur
    - Templates standardisés pour services ML
    - Déploiement multi-environnements
    - Gestion des versions et rollbacks
    - Intégration CI/CD avec validation
    - Monitoring et health checks automatiques
    """
    
    def __init__(self,
                 charts_directory -> None: str = "/tmp/helm_charts",
                 templates_directory -> None: str = "/tmp/chart_templates",
                 helm_binary_path -> None: str = "helm") -> None:
        self.charts_directory = Path(charts_directory)
        self.templates_directory = Path(templates_directory)
        self.helm_binary_path = helm_binary_path
        
        # Stockage des charts et releases
        self.charts: Dict[str, HelmChart] = {}
        self.releases: Dict[str, HelmRelease] = {}
        self.chart_templates: Dict[CreatorService, ChartTemplate] = {}
        
        # Configuration par créateur
        self.creator_configs = {
            CreatorService.MUSICIAN_AUDIO_SERVICE: {
                "resource_limits": {"cpu": "2000m", "memory": "4Gi"},
                "replicas": {"min": 2, "max": 10},
                "ports": [8080, 8443],
                "health_check": "/health",
                "metrics_port": 9090
            },
            CreatorService.BLOGGER_CONTENT_SERVICE: {
                "resource_limits": {"cpu": "1000m", "memory": "2Gi"},
                "replicas": {"min": 1, "max": 5},
                "ports": [8080],
                "health_check": "/health",
                "metrics_port": 9090
            },
            CreatorService.PHOTOGRAPHER_IMAGE_SERVICE: {
                "resource_limits": {"cpu": "4000m", "memory": "8Gi"},
                "replicas": {"min": 2, "max": 8},
                "ports": [8080, 8443],
                "health_check": "/health",
                "metrics_port": 9090
            },
            CreatorService.INFLUENCER_ANALYTICS_SERVICE: {
                "resource_limits": {"cpu": "1500m", "memory": "3Gi"},
                "replicas": {"min": 2, "max": 12},
                "ports": [8080, 8443, 9000],
                "health_check": "/health",
                "metrics_port": 9090
            },
            CreatorService.COMEDIAN_PERFORMANCE_SERVICE: {
                "resource_limits": {"cpu": "1000m", "memory": "2Gi"},
                "replicas": {"min": 1, "max": 6},
                "ports": [8080],
                "health_check": "/health",
                "metrics_port": 9090
            }
        }
        
        # Callbacks
        self.deployment_callbacks: List[Callable] = []
        self.chart_callbacks: List[Callable] = []
        
        self._setup_directories()
        self._setup_chart_templates()
        self._check_helm_installation()
        logger.info("⚓ HelmChartManager initialized for enterprise Kubernetes deployments")
    
    def _setup_directories(self) -> None:
        """Initialisation des répertoires"""
        try:
            self.charts_directory.mkdir(parents=True, exist_ok=True)
            self.templates_directory.mkdir(parents=True, exist_ok=True)
            
            # Sous-répertoires par environnement
            for env in DeploymentEnvironment:
                (self.charts_directory / env.value).mkdir(exist_ok=True)
                
        except Exception as e:
            logger.error(f"❌ Directory setup error: {e}")
            raise
    
    def _check_helm_installation(self) -> None:
        """Vérification de l'installation Helm"""
        try:
            result = subprocess.run(
                [self.helm_binary_path, "version", "--short"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Helm found: {version}")
            else:
                logger.warning("⚠️ Helm not found or not accessible")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not verify Helm installation: {e}")
    
    def _setup_chart_templates(self) -> None:
        """Configuration des templates de charts par créateur"""
        try:
            # Template pour service audio de musicien
            musician_template = ChartTemplate(
                template_name="musician_audio_template",
                creator_service=CreatorService.MUSICIAN_AUDIO_SERVICE,
                base_chart_type=ChartType.ML_MODEL_SERVING,
                template_files={
                    "deployment.yaml": self._get_deployment_template("musician"),
                    "service.yaml": self._get_service_template("musician"),
                    "ingress.yaml": self._get_ingress_template("musician"),
                    "configmap.yaml": self._get_configmap_template("musician"),
                    "hpa.yaml": self._get_hpa_template("musician")
                },
                default_values={
                    "replicaCount": 2,
                    "image": {"repository": "ainflue/musician-audio", "tag": "latest"},
                    "resources": self.creator_configs[CreatorService.MUSICIAN_AUDIO_SERVICE]["resource_limits"],
                    "autoscaling": {"enabled": True, "minReplicas": 2, "maxReplicas": 10}
                },
                required_variables=["image.repository", "image.tag", "service.port"],
                description="Template for musician audio processing services"
            )
            
            # Template pour service contenu de blogueur
            blogger_template = ChartTemplate(
                template_name="blogger_content_template",
                creator_service=CreatorService.BLOGGER_CONTENT_SERVICE,
                base_chart_type=ChartType.ML_MODEL_SERVING,
                template_files={
                    "deployment.yaml": self._get_deployment_template("blogger"),
                    "service.yaml": self._get_service_template("blogger"),
                    "ingress.yaml": self._get_ingress_template("blogger"),
                    "configmap.yaml": self._get_configmap_template("blogger")
                },
                default_values={
                    "replicaCount": 1,
                    "image": {"repository": "ainflue/blogger-content", "tag": "latest"},
                    "resources": self.creator_configs[CreatorService.BLOGGER_CONTENT_SERVICE]["resource_limits"],
                    "autoscaling": {"enabled": True, "minReplicas": 1, "maxReplicas": 5}
                },
                required_variables=["image.repository", "image.tag"],
                description="Template for blogger content generation services"
            )
            
            # Template pour service image de photographe
            photographer_template = ChartTemplate(
                template_name="photographer_image_template",
                creator_service=CreatorService.PHOTOGRAPHER_IMAGE_SERVICE,
                base_chart_type=ChartType.ML_MODEL_SERVING,
                template_files={
                    "deployment.yaml": self._get_deployment_template("photographer"),
                    "service.yaml": self._get_service_template("photographer"),
                    "ingress.yaml": self._get_ingress_template("photographer"),
                    "configmap.yaml": self._get_configmap_template("photographer"),
                    "pvc.yaml": self._get_pvc_template("photographer")
                },
                default_values={
                    "replicaCount": 2,
                    "image": {"repository": "ainflue/photographer-image", "tag": "latest"},
                    "resources": self.creator_configs[CreatorService.PHOTOGRAPHER_IMAGE_SERVICE]["resource_limits"],
                    "storage": {"size": "100Gi", "class": "fast-ssd"}
                },
                required_variables=["image.repository", "image.tag", "storage.size"],
                description="Template for photographer image processing services"
            )
            
            # Template pour service analytics d'influenceur
            influencer_template = ChartTemplate(
                template_name="influencer_analytics_template",
                creator_service=CreatorService.INFLUENCER_ANALYTICS_SERVICE,
                base_chart_type=ChartType.STREAMING_PIPELINE,
                template_files={
                    "deployment.yaml": self._get_deployment_template("influencer"),
                    "service.yaml": self._get_service_template("influencer"),
                    "configmap.yaml": self._get_configmap_template("influencer"),
                    "secret.yaml": self._get_secret_template("influencer")
                },
                default_values={
                    "replicaCount": 2,
                    "image": {"repository": "ainflue/influencer-analytics", "tag": "latest"},
                    "resources": self.creator_configs[CreatorService.INFLUENCER_ANALYTICS_SERVICE]["resource_limits"],
                    "kafka": {"enabled": True, "brokers": "kafka:9092"}
                },
                required_variables=["image.repository", "image.tag", "kafka.brokers"],
                description="Template for influencer analytics services"
            )
            
            # Template pour service performance de comédien
            comedian_template = ChartTemplate(
                template_name="comedian_performance_template",
                creator_service=CreatorService.COMEDIAN_PERFORMANCE_SERVICE,
                base_chart_type=ChartType.ML_MODEL_SERVING,
                template_files={
                    "deployment.yaml": self._get_deployment_template("comedian"),
                    "service.yaml": self._get_service_template("comedian"),
                    "configmap.yaml": self._get_configmap_template("comedian")
                },
                default_values={
                    "replicaCount": 1,
                    "image": {"repository": "ainflue/comedian-performance", "tag": "latest"},
                    "resources": self.creator_configs[CreatorService.COMEDIAN_PERFORMANCE_SERVICE]["resource_limits"]
                },
                required_variables=["image.repository", "image.tag"],
                description="Template for comedian performance analysis services"
            )
            
            # Enregistrement des templates
            templates = [musician_template, blogger_template, photographer_template, 
                        influencer_template, comedian_template]
            
            for template in templates:
                self.chart_templates[template.creator_service] = template
            
            logger.info(f"📋 Loaded {len(templates)} chart templates for creators")
            
        except Exception as e:
            logger.error(f"❌ Error setting up chart templates: {e}")
    
    def _get_deployment_template(self, creator_type: str) -> str:
        """Template de déploiement par créateur"""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
    ainflue.component: ml-service
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  {{{{- end }}}}
  selector:
    matchLabels:
      {{{{- include "{creator_type}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      annotations:
        checksum/config: {{{{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}}}
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
      labels:
        {{{{- include "{creator_type}.selectorLabels" . | nindent 8 }}}}
        creator.type: {creator_type}
    spec:
      serviceAccountName: {{{{ include "{creator_type}.serviceAccountName" . }}}}
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
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
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
          env:
            - name: CREATOR_TYPE
              value: {creator_type}
            - name: ENVIRONMENT
              value: {{{{ .Values.environment | default "production" }}}}
            - name: LOG_LEVEL
              value: {{{{ .Values.logLevel | default "INFO" }}}}
          envFrom:
            - configMapRef:
                name: {{{{ include "{creator_type}.fullname" . }}}}-config
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {{{{}}}}
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
    
    def _get_service_template(self, creator_type: str) -> str:
        """Template de service par créateur"""
        return f"""
apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
spec:
  type: {{{{ .Values.service.type }}}}
  ports:
    - port: {{{{ .Values.service.port }}}}
      targetPort: http
      protocol: TCP
      name: http
    - port: 9090
      targetPort: metrics
      protocol: TCP
      name: metrics
  selector:
    {{{{- include "{creator_type}.selectorLabels" . | nindent 4 }}}}
"""
    
    def _get_ingress_template(self, creator_type: str) -> str:
        """Template d'ingress par créateur"""
        return f"""
{{{{- if .Values.ingress.enabled -}}}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
  {{{{- with .Values.ingress.annotations }}}}
  annotations:
    {{{{- toYaml . | nindent 4 }}}}
  {{{{- end }}}}
spec:
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
            pathType: {{{{ .pathType }}}}
            backend:
              service:
                name: {{{{ include "{creator_type}.fullname" $ }}}}
                port:
                  number: {{{{ $.Values.service.port }}}}
          {{{{- end }}}}
    {{{{- end }}}}
{{{{- end }}}}
"""
    
    def _get_configmap_template(self, creator_type: str) -> str:
        """Template de ConfigMap par créateur"""
        config_data = {
            "musician": {
                "AUDIO_SAMPLE_RATE": "44100",
                "AUDIO_FORMATS": "wav,mp3,flac",
                "MAX_AUDIO_SIZE": "100MB",
                "PROCESSING_TIMEOUT": "300"
            },
            "blogger": {
                "MAX_CONTENT_LENGTH": "50000",
                "SEO_ENABLED": "true",
                "CONTENT_FORMATS": "markdown,html",
                "ANALYSIS_TIMEOUT": "60"
            },
            "photographer": {
                "MAX_IMAGE_SIZE": "50MB",
                "IMAGE_FORMATS": "jpg,png,raw,tiff",
                "PROCESSING_TIMEOUT": "600",
                "STORAGE_BACKEND": "s3"
            },
            "influencer": {
                "PLATFORMS": "instagram,tiktok,youtube,twitter",
                "ANALYTICS_WINDOW": "7d",
                "ENGAGEMENT_THRESHOLD": "0.02",
                "PROCESSING_TIMEOUT": "120"
            },
            "comedian": {
                "MAX_SCRIPT_LENGTH": "10000",
                "HUMOR_TYPES": "observational,standup,sketch",
                "ANALYSIS_TIMEOUT": "90",
                "AUDIENCE_TRACKING": "true"
            }
        }
        
        data = config_data.get(creator_type, {})
        data_yaml = "\n".join([f"  {k}: \"{v}\"" for k, v in data.items()])
        
        return f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}-config
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
data:
{data_yaml}
  # Environment specific config
  {{{{- range $key, $value := .Values.config }}}}
  {{{{ $key }}}}: {{{{ $value | quote }}}}
  {{{{- end }}}}
"""
    
    def _get_hpa_template(self, creator_type: str) -> str:
        """Template HPA par créateur"""
        return f"""
{{{{- if .Values.autoscaling.enabled }}}}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{{{ include "{creator_type}.fullname" . }}}}
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
    
    def _get_pvc_template(self, creator_type: str) -> str:
        """Template PVC par créateur"""
        return f"""
{{{{- if .Values.storage.enabled }}}}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}-storage
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: {{{{ .Values.storage.class }}}}
  resources:
    requests:
      storage: {{{{ .Values.storage.size }}}}
{{{{- end }}}}
"""
    
    def _get_secret_template(self, creator_type: str) -> str:
        """Template Secret par créateur"""
        return f"""
{{{{- if .Values.secrets }}}}
apiVersion: v1
kind: Secret
metadata:
  name: {{{{ include "{creator_type}.fullname" . }}}}-secrets
  labels:
    {{{{- include "{creator_type}.labels" . | nindent 4 }}}}
    creator.type: {creator_type}
type: Opaque
data:
  {{{{- range $key, $value := .Values.secrets }}}}
  {{{{ $key }}}}: {{{{ $value | b64enc }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
    
    async def create_chart(self,
                         chart_name: str,
                         creator_service: CreatorService,
                         app_version: str = "1.0.0",
                         description: Optional[str] = None) -> HelmChart:
        """Création d'un nouveau chart Helm"""
        try:
            if creator_service not in self.chart_templates:
                raise ValueError(f"No template available for {creator_service.value}")
            
            template = self.chart_templates[creator_service]
            chart_path = self.charts_directory / chart_name
            
            # Création de la structure du chart
            await self._create_chart_structure(chart_path, chart_name, template, app_version, description)
            
            # Création de l'objet HelmChart
            helm_chart = HelmChart(
                chart_name=chart_name,
                chart_type=template.base_chart_type,
                creator_service=creator_service,
                version="0.1.0",
                description=description or template.description,
                app_version=app_version,
                chart_path=str(chart_path)
            )
            
            # Génération des values files par environnement
            for env in DeploymentEnvironment:
                values_file = await self._generate_values_file(helm_chart, template, env)
                helm_chart.values_files[env] = values_file
            
            # Stockage
            self.charts[chart_name] = helm_chart
            
            # Callbacks
            for callback in self.chart_callbacks:
                try:
                    await callback(helm_chart)
                except Exception as e:
                    logger.error(f"❌ Chart callback error: {e}")
            
            logger.info(f"📦 Chart created: {chart_name} for {creator_service.value}")
            return helm_chart
            
        except Exception as e:
            logger.error(f"❌ Error creating chart {chart_name}: {e}")
            raise
    
    async def _create_chart_structure(self,
                                    chart_path -> None: Path,
                                    chart_name -> None: str,
                                    template -> None: ChartTemplate,
                                    app_version -> None: str,
                                    description -> None: Optional[str]) -> None:
        """Création de la structure du chart"""
        try:
            # Création des répertoires
            chart_path.mkdir(parents=True, exist_ok=True)
            (chart_path / "templates").mkdir(exist_ok=True)
            (chart_path / "charts").mkdir(exist_ok=True)
            
            # Chart.yaml
            chart_yaml = {
                "apiVersion": "v2",
                "name": chart_name,
                "description": description or template.description,
                "type": "application",
                "version": "0.1.0",
                "appVersion": app_version,
                "keywords": ["ainflue", "ml", "creator", template.creator_service.value.split('_')[0]],
                "home": "https://github.com/Mlaiel/Ainflue",
                "maintainers": [
                    {
                        "name": "Fahed Mlaiel",
                        "email": "mlaiel@live.de"
                    }
                ],
                "annotations": {
                    "creator.type": template.creator_service.value.split('_')[0],
                    "service.type": template.creator_service.value,
                    "chart.type": template.base_chart_type.value
                }
            }
            
            with open(chart_path / "Chart.yaml", 'w') as f:
                yaml.dump(chart_yaml, f, default_flow_style=False)
            
            # Templates
            templates_dir = chart_path / "templates"
            for filename, content in template.template_files.items():
                with open(templates_dir / filename, 'w') as f:
                    f.write(content)
            
            # _helpers.tpl
            helpers_content = self._generate_helpers_template(chart_name)
            with open(templates_dir / "_helpers.tpl", 'w') as f:
                f.write(helpers_content)
            
            # NOTES.txt
            notes_content = self._generate_notes_template(template.creator_service)
            with open(templates_dir / "NOTES.txt", 'w') as f:
                f.write(notes_content)
                
        except Exception as e:
            logger.error(f"❌ Error creating chart structure: {e}")
            raise
    
    def _generate_helpers_template(self, chart_name: str) -> str:
        """Génération du template helpers"""
        return f"""
{{{{/*
Expand the name of the chart.
*/}}}}
{{{{- define "{chart_name}.name" -}}}}
{{{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Create a default fully qualified app name.
*/}}}}
{{{{- define "{chart_name}.fullname" -}}}}
{{{{- if .Values.fullnameOverride }}}}
{{{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- $name := default .Chart.Name .Values.nameOverride }}}}
{{{{- if contains $name .Release.Name }}}}
{{{{- .Release.Name | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}
{{{{- end }}}}
{{{{- end }}}}

{{{{/*
Create chart name and version as used by the chart label.
*/}}}}
{{{{- define "{chart_name}.chart" -}}}}
{{{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Common labels
*/}}}}
{{{{- define "{chart_name}.labels" -}}}}
helm.sh/chart: {{{{ include "{chart_name}.chart" . }}}}
{{{{ include "{chart_name}.selectorLabels" . }}}}
{{{{- if .Chart.AppVersion }}}}
app.kubernetes.io/version: {{{{ .Chart.AppVersion | quote }}}}
{{{{- end }}}}
app.kubernetes.io/managed-by: {{{{ .Release.Service }}}}
app.kubernetes.io/part-of: ainflue-platform
{{{{- end }}}}

{{{{/*
Selector labels
*/}}}}
{{{{- define "{chart_name}.selectorLabels" -}}}}
app.kubernetes.io/name: {{{{ include "{chart_name}.name" . }}}}
app.kubernetes.io/instance: {{{{ .Release.Name }}}}
{{{{- end }}}}

{{{{/*
Create the name of the service account to use
*/}}}}
{{{{- define "{chart_name}.serviceAccountName" -}}}}
{{{{- if .Values.serviceAccount.create }}}}
{{{{- default (include "{chart_name}.fullname" .) .Values.serviceAccount.name }}}}
{{{{- else }}}}
{{{{- default "default" .Values.serviceAccount.name }}}}
{{{{- end }}}}
{{{{- end }}}}
"""
    
    def _generate_notes_template(self, creator_service: CreatorService) -> str:
        """Génération du template NOTES.txt"""
        creator_type = creator_service.value.split('_')[0]
        
        return f"""
🚀 {creator_type.title()} Service Deployment Successful!

Your {creator_type} service has been deployed to Kubernetes.

{{{{- if .Values.ingress.enabled }}}}
1. Get the application URL by running these commands:
{{{{- range $host := .Values.ingress.hosts }}}}
  {{{{- range .paths }}}}
  http{{{{ if $.Values.ingress.tls }}}}s{{{{ end }}}}://{{{{ $host.host }}}}{{{{ .path }}}}
  {{{{- end }}}}
{{{{- end }}}}
{{{{- else if contains "NodePort" .Values.service.type }}}}
1. Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace {{{{ .Release.Namespace }}}} -o jsonpath="{{{{.spec.ports[0].nodePort}}}}" services {{{{ include "{creator_type}.fullname" . }}}})
  export NODE_IP=$(kubectl get nodes --namespace {{{{ .Release.Namespace }}}} -o jsonpath="{{{{.items[0].status.addresses[0].address}}}}")
  echo http://$NODE_IP:$NODE_PORT
{{{{- else if contains "LoadBalancer" .Values.service.type }}}}
1. Get the application URL by running these commands:
     NOTE: It may take a few minutes for the LoadBalancer IP to be available.
           You can watch the status of by running 'kubectl get --namespace {{{{ .Release.Namespace }}}} svc -w {{{{ include "{creator_type}.fullname" . }}}}'
  export SERVICE_IP=$(kubectl get svc --namespace {{{{ .Release.Namespace }}}} {{{{ include "{creator_type}.fullname" . }}}} --template "{{{{ range (index .status.loadBalancer.ingress 0) }}}}{{{{.}}}}{{{{ end }}}}")
  echo http://$SERVICE_IP:{{{{ .Values.service.port }}}}
{{{{- else if contains "ClusterIP" .Values.service.type }}}}
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace {{{{ .Release.Namespace }}}} -l "app.kubernetes.io/name={{{{ include "{creator_type}.name" . }}}},app.kubernetes.io/instance={{{{ .Release.Name }}}}" -o jsonpath="{{{{.items[0].metadata.name}}}}")
  export CONTAINER_PORT=$(kubectl get pod --namespace {{{{ .Release.Namespace }}}} $POD_NAME -o jsonpath="{{{{.spec.containers[0].ports[0].containerPort}}}}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace {{{{ .Release.Namespace }}}} port-forward $POD_NAME 8080:$CONTAINER_PORT
{{{{- end }}}}

2. Check the health of your {creator_type} service:
  kubectl get pods -l app.kubernetes.io/name={{{{ include "{creator_type}.name" . }}}}

3. View logs:
  kubectl logs -l app.kubernetes.io/name={{{{ include "{creator_type}.name" . }}}}

🎯 Creator-Specific Features:
{self._get_creator_specific_notes(creator_service)}

📊 Monitoring:
- Metrics are available at: http://service-url:9090/metrics
- Health check: http://service-url:8080/health

💡 Pro Tips:
- Use 'helm upgrade' to update your deployment
- Monitor resource usage with 'kubectl top pods'
- Scale with 'kubectl scale deployment {{{{ include "{creator_type}.fullname" . }}}} --replicas=X'
"""
    
    def _get_creator_specific_notes(self, creator_service: CreatorService) -> str:
        """Notes spécifiques par créateur"""
        notes = {
            CreatorService.MUSICIAN_AUDIO_SERVICE: """
- Audio processing endpoint: POST /process-audio
- Supported formats: WAV, MP3, FLAC
- Real-time streaming: WebSocket /audio-stream
- Genre detection: GET /detect-genre""",
            
            CreatorService.BLOGGER_CONTENT_SERVICE: """
- Content generation: POST /generate-content
- SEO analysis: GET /analyze-seo
- Sentiment analysis: POST /analyze-sentiment
- Keyword extraction: POST /extract-keywords""",
            
            CreatorService.PHOTOGRAPHER_IMAGE_SERVICE: """
- Image enhancement: POST /enhance-image
- Style detection: POST /detect-style
- Metadata extraction: GET /extract-metadata
- Batch processing: POST /batch-process""",
            
            CreatorService.INFLUENCER_ANALYTICS_SERVICE: """
- Engagement analytics: GET /analytics/engagement
- Trend analysis: GET /analytics/trends
- Audience insights: GET /analytics/audience
- Performance prediction: POST /predict-performance""",
            
            CreatorService.COMEDIAN_PERFORMANCE_SERVICE: """
- Humor analysis: POST /analyze-humor
- Timing optimization: POST /optimize-timing
- Audience reaction: GET /audience-reaction
- Performance scoring: POST /score-performance"""
        }
        
        return notes.get(creator_service, "- Service-specific endpoints available")
    
    async def _generate_values_file(self,
                                  chart: HelmChart,
                                  template: ChartTemplate,
                                  environment: DeploymentEnvironment) -> str:
        """Génération du fichier values par environnement"""
        try:
            base_values = template.default_values.copy()
            
            # Ajustements par environnement
            env_adjustments = {
                DeploymentEnvironment.DEVELOPMENT: {
                    "replicaCount": 1,
                    "environment": "development",
                    "logLevel": "DEBUG",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "256Mi"},
                        "limits": {"cpu": "500m", "memory": "1Gi"}
                    }
                },
                DeploymentEnvironment.STAGING: {
                    "environment": "staging",
                    "logLevel": "INFO",
                    "autoscaling": {"enabled": True, "minReplicas": 1, "maxReplicas": 3}
                },
                DeploymentEnvironment.PRODUCTION: {
                    "environment": "production",
                    "logLevel": "WARN",
                    "autoscaling": {"enabled": True}
                }
            }
            
            # Fusion des valeurs
            env_values = env_adjustments.get(environment, {})
            for key, value in env_values.items():
                if isinstance(value, dict) and key in base_values:
                    base_values[key].update(value)
                else:
                    base_values[key] = value
            
            # Configuration commune
            common_values = {
                "nameOverride": "",
                "fullnameOverride": "",
                "image": {
                    "pullPolicy": "IfNotPresent"
                },
                "service": {
                    "type": "ClusterIP",
                    "port": 8080
                },
                "ingress": {
                    "enabled": environment == DeploymentEnvironment.PRODUCTION,
                    "className": "nginx",
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx",
                        "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                    },
                    "hosts": [{
                        "host": f"{chart.chart_name}-{environment.value}.ainflue.com",
                        "paths": [{"path": "/", "pathType": "Prefix"}]
                    }],
                    "tls": [{
                        "secretName": f"{chart.chart_name}-{environment.value}-tls",
                        "hosts": [f"{chart.chart_name}-{environment.value}.ainflue.com"]
                    }]
                },
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
                    "capabilities": {"drop": ["ALL"]},
                    "readOnlyRootFilesystem": True,
                    "runAsNonRoot": True,
                    "runAsUser": 1000
                },
                "nodeSelector": {},
                "tolerations": [],
                "affinity": {}
            }
            
            # Fusion finale
            final_values = {**common_values, **base_values}
            
            # Sauvegarde du fichier values
            values_file_path = Path(chart.chart_path) / f"values-{environment.value}.yaml"
            with open(values_file_path, 'w') as f:
                yaml.dump(final_values, f, default_flow_style=False, sort_keys=False)
            
            return str(values_file_path)
            
        except Exception as e:
            logger.error(f"❌ Error generating values file: {e}")
            raise
    
    async def deploy_chart(self,
                         chart_name: str,
                         release_name: str,
                         environment: DeploymentEnvironment,
                         namespace: str = "default",
                         values_override: Optional[Dict[str, Any]] = None) -> HelmRelease:
        """Déploiement d'un chart Helm"""
        try:
            if chart_name not in self.charts:
                raise ValueError(f"Chart {chart_name} not found")
            
            chart = self.charts[chart_name]
            
            # Commande helm install/upgrade
            cmd = [
                self.helm_binary_path, "upgrade", "--install",
                release_name, chart.chart_path,
                "--namespace", namespace,
                "--create-namespace"
            ]
            
            # Ajout du fichier values spécifique à l'environnement
            if environment in chart.values_files:
                cmd.extend(["--values", chart.values_files[environment]])
            
            # Override de valeurs si fourni
            if values_override:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(values_override, f)
                    cmd.extend(["--values", f.name])
                    temp_values_file = f.name
            else:
                temp_values_file = None
            
            # Exécution du déploiement
            logger.info(f"🚀 Deploying {release_name} to {environment.value}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Nettoyage du fichier temporaire
            if temp_values_file:
                os.unlink(temp_values_file)
            
            if result.returncode != 0:
                raise RuntimeError(f"Helm deployment failed: {result.stderr}")
            
            # Création de l'objet HelmRelease
            release = HelmRelease(
                release_name=release_name,
                chart=chart,
                environment=environment,
                namespace=namespace,
                status="deployed",
                revision=1,  # Simplifié pour la démo
                values_override=values_override or {}
            )
            
            self.releases[release_name] = release
            
            # Callbacks de déploiement
            for callback in self.deployment_callbacks:
                try:
                    await callback(release)
                except Exception as e:
                    logger.error(f"❌ Deployment callback error: {e}")
            
            logger.info(f"✅ Successfully deployed {release_name}")
            return release
            
        except Exception as e:
            logger.error(f"❌ Error deploying chart {chart_name}: {e}")
            raise
    
    async def rollback_release(self, release_name: str, revision: Optional[int] = None) -> bool:
        """Rollback d'une release"""
        try:
            if release_name not in self.releases:
                raise ValueError(f"Release {release_name} not found")
            
            release = self.releases[release_name]
            
            cmd = [self.helm_binary_path, "rollback", release_name]
            if revision:
                cmd.append(str(revision))
            cmd.extend(["--namespace", release.namespace])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"❌ Rollback failed: {result.stderr}")
                return False
            
            release.last_deployment = datetime.now()
            logger.info(f"↩️ Successfully rolled back {release_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rolling back {release_name}: {e}")
            return False
    
    async def get_release_status(self, release_name: str) -> Dict[str, Any]:
        """Obtenir le status d'une release"""
        try:
            if release_name not in self.releases:
                return {"error": "Release not found"}
            
            release = self.releases[release_name]
            
            # Commande helm status
            cmd = [self.helm_binary_path, "status", release_name, "--namespace", release.namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": f"Failed to get status: {result.stderr}"}
            
            helm_status = json.loads(result.stdout)
            
            return {
                "release_name": release_name,
                "chart_name": release.chart.chart_name,
                "environment": release.environment.value,
                "namespace": release.namespace,
                "status": helm_status.get("info", {}).get("status", "unknown"),
                "revision": helm_status.get("version", 0),
                "last_deployed": helm_status.get("info", {}).get("last_deployed"),
                "notes": helm_status.get("info", {}).get("notes", "")
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting release status: {e}")
            return {"error": str(e)}
    
    def add_deployment_callback(self, callback -> None: Callable) -> None:
        """Ajouter callback de déploiement"""
        self.deployment_callbacks.append(callback)
        logger.info(f"🚀 Deployment callback added. Total: {len(self.deployment_callbacks)}")
    
    def add_chart_callback(self, callback -> None: Callable) -> None:
        """Ajouter callback de chart"""
        self.chart_callbacks.append(callback)
        logger.info(f"📦 Chart callback added. Total: {len(self.chart_callbacks)}")


# Exemple d'utilisation pour démonstration
async def main() -> None:
    """Démonstration des capacités du HelmChartManager"""
    
    manager = HelmChartManager()
    
    # Callbacks de démonstration
    async def deployment_callback(release -> None: HelmRelease) -> None:
        print(f"🚀 DEPLOYED: {release.release_name}")
        print(f"   Chart: {release.chart.chart_name}")
        print(f"   Environment: {release.environment.value}")
        print(f"   Namespace: {release.namespace}")
    
    async def chart_callback(chart -> None: HelmChart) -> None:
        print(f"📦 CHART CREATED: {chart.chart_name}")
        print(f"   Type: {chart.chart_type.value}")
        print(f"   Creator Service: {chart.creator_service.value}")
    
    manager.add_deployment_callback(deployment_callback)
    manager.add_chart_callback(chart_callback)
    
    # Création de charts pour différents créateurs
    creator_charts = [
        ("musician-audio-processor", CreatorService.MUSICIAN_AUDIO_SERVICE, "Audio processing for musicians"),
        ("blogger-content-generator", CreatorService.BLOGGER_CONTENT_SERVICE, "Content generation for bloggers"),
        ("photographer-image-enhancer", CreatorService.PHOTOGRAPHER_IMAGE_SERVICE, "Image enhancement for photographers"),
        ("influencer-analytics-dashboard", CreatorService.INFLUENCER_ANALYTICS_SERVICE, "Analytics for influencers"),
        ("comedian-performance-analyzer", CreatorService.COMEDIAN_PERFORMANCE_SERVICE, "Performance analysis for comedians")
    ]
    
    print("📦 Creating Helm charts...")
    created_charts = []
    for chart_name, creator_service, description in creator_charts:
        try:
            chart = await manager.create_chart(
                chart_name=chart_name,
                creator_service=creator_service,
                app_version="1.0.0",
                description=description
            )
            created_charts.append(chart)
            print(f"   ✅ Created {chart_name}")
        except Exception as e:
            print(f"   ❌ Failed to create {chart_name}: {e}")
    
    # Simulation de déploiements (sans vraie exécution helm)
    print(f"\n🚀 Simulating deployments...")
    for chart in created_charts[:2]:  # Première 2 pour la démo
        for env in [DeploymentEnvironment.DEVELOPMENT, DeploymentEnvironment.STAGING]:
            release_name = f"{chart.chart_name}-{env.value}"
            
            try:
                # Note: Ceci échouerait sans un cluster Kubernetes réel
                print(f"   📋 Would deploy {release_name} to {env.value}")
                
                # Simulation du status
                status = {
                    "release_name": release_name,
                    "chart_name": chart.chart_name,
                    "environment": env.value,
                    "namespace": "default",
                    "status": "deployed",
                    "revision": 1
                }
                print(f"   📊 Simulated status: {status['status']}")
                
            except Exception as e:
                print(f"   ❌ Deployment simulation error: {e}")
    
    # Affichage des charts créés
    print(f"\n📋 Created Charts Summary:")
    for chart_name, chart in manager.charts.items():
        print(f"   📦 {chart_name}:")
        print(f"      Type: {chart.chart_type.value}")
        print(f"      Creator: {chart.creator_service.value}")
        print(f"      Path: {chart.chart_path}")
        print(f"      Values files: {len(chart.values_files)}")
    
    print(f"\n✅ HelmChartManager demonstration completed")
    print(f"📁 Charts created in: {manager.charts_directory}")


if __name__ == "__main__":
    asyncio.run(main())