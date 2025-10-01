#!/usr/bin/env python3
"""
⚓ Helm Chart Template - IA Chéries Creator Economy Platform
========================================================

Enterprise Kubernetes Helm Chart Templates for Creator Economy Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: DevOps Engineer + Kubernetes Specialist + Microservices Architect

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de> - TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
"""

import yaml
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class ServiceType(Enum):
    """Creator Economy service types"""
    CREATOR_API = "creator-api"
    AI_PROCESSOR = "ai-processor"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    CONTENT_PROTECTION = "content-protection"
    SEO_OPTIMIZER = "seo-optimizer"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    FRONTEND = "frontend"

class EnvironmentType(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class HelmChartConfig:
    """Configuration for Helm chart generation"""
    chart_name: str
    version: str
    app_version: str
    description: str
    environment: EnvironmentType
    namespace: str = "ainflue"
    enable_ingress: bool = True
    enable_monitoring: bool = True
    enable_autoscaling: bool = True
    enable_persistence: bool = True
    replica_count: int = 3

class HelmChartTemplate:
    """
    Enterprise Helm Chart Template Generator for Creator Economy Platform
    
    Features:
    - Multi-service Kubernetes deployments
    - Creator economy specific configurations
    - Auto-scaling based on creator activity
    - Persistent storage for content
    - Ingress configuration for multi-domain
    - Monitoring and observability integration
    - Secret management integration
    - Environment-specific configurations
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.author = "Fahed Mlaiel <mlaiel@live.de>"
        
    def generate_helm_chart(self, config: HelmChartConfig) -> Dict[str, Any]:
        """Generate complete Helm chart structure"""
        
        chart_structure = {
            "Chart.yaml": self._generate_chart_yaml(config),
            "values.yaml": self._generate_values_yaml(config),
            "values-dev.yaml": self._generate_environment_values(config, EnvironmentType.DEVELOPMENT),
            "values-staging.yaml": self._generate_environment_values(config, EnvironmentType.STAGING),
            "values-prod.yaml": self._generate_environment_values(config, EnvironmentType.PRODUCTION),
            "templates": {
                "deployment.yaml": self._generate_deployment_template(config),
                "service.yaml": self._generate_service_template(config),
                "configmap.yaml": self._generate_configmap_template(config),
                "secrets.yaml": self._generate_secrets_template(config),
                "ingress.yaml": self._generate_ingress_template(config),
                "hpa.yaml": self._generate_hpa_template(config),
                "pvc.yaml": self._generate_pvc_template(config),
                "serviceaccount.yaml": self._generate_serviceaccount_template(config),
                "rbac.yaml": self._generate_rbac_template(config),
                "servicemonitor.yaml": self._generate_servicemonitor_template(config),
                "_helpers.tpl": self._generate_helpers_template(config)
            }
        }
        
        return chart_structure
    
    def _generate_chart_yaml(self, config: HelmChartConfig) -> Dict[str, Any]:
        """Generate Chart.yaml file"""
        return {
            "apiVersion": "v2",
            "name": config.chart_name,
            "description": config.description,
            "type": "application",
            "version": config.version,
            "appVersion": config.app_version,
            "keywords": [
                "creator-economy",
                "ai-processing",
                "monetization", 
                "collaboration",
                "content-creation",
                "ainflue"
            ],
            "home": "https://ainflue.com",
            "sources": [
                "https://github.com/Mlaiel/IA Chéries"
            ],
            "maintainers": [
                {
                    "name": "Fahed Mlaiel",
                    "email": "mlaiel@live.de",
                    "url": "https://ainflue.com"
                }
            ],
            "dependencies": [
                {
                    "name": "postgresql",
                    "version": "12.x.x",
                    "repository": "https://charts.bitnami.com/bitnami",
                    "condition": "postgresql.enabled"
                },
                {
                    "name": "redis",
                    "version": "17.x.x", 
                    "repository": "https://charts.bitnami.com/bitnami",
                    "condition": "redis.enabled"
                },
                {
                    "name": "elasticsearch",
                    "version": "19.x.x",
                    "repository": "https://charts.bitnami.com/bitnami",
                    "condition": "elasticsearch.enabled"
                },
                {
                    "name": "prometheus",
                    "version": "15.x.x",
                    "repository": "https://prometheus-community.github.io/helm-charts",
                    "condition": "monitoring.prometheus.enabled"
                }
            ],
            "annotations": {
                "category": "Creator Economy Platform",
                "artifacthub.io/license": "Proprietary",
                "artifacthub.io/links": "[{\"name\": \"Documentation\", \"url\": \"https://docs.ainflue.com\"}]"
            }
        }
    
    def _generate_values_yaml(self, config: HelmChartConfig) -> Dict[str, Any]:
        """Generate main values.yaml file"""
        return {
            # Global settings
            "global": {
                "imageRegistry": "registry.ainflue.com",
                "imagePullSecrets": ["ainflue-registry-secret"],
                "storageClass": "fast-ssd"
            },
            
            # Creator API Service
            "creatorApi": {
                "enabled": True,
                "image": {
                    "repository": "ainflue/creator-api",
                    "tag": config.app_version,
                    "pullPolicy": "IfNotPresent"
                },
                "replicaCount": config.replica_count,
                "service": {
                    "type": "ClusterIP",
                    "port": 8000,
                    "targetPort": 8000
                },
                "resources": {
                    "requests": {
                        "memory": "512Mi",
                        "cpu": "250m"
                    },
                    "limits": {
                        "memory": "2Gi",
                        "cpu": "1000m"
                    }
                },
                "env": {
                    "DATABASE_URL": "postgresql://creator:password@postgresql:5432/creator_db",
                    "REDIS_URL": "redis://redis:6379/0",
                    "AI_PROCESSING_QUEUE": "creator_ai_queue",
                    "CONTENT_STORAGE_BUCKET": "ainflue-creator-content"
                }
            },
            
            # AI Processing Service
            "aiProcessor": {
                "enabled": True,
                "image": {
                    "repository": "ainflue/ai-processor",
                    "tag": config.app_version,
                    "pullPolicy": "IfNotPresent"
                },
                "replicaCount": 2,
                "service": {
                    "type": "ClusterIP",
                    "port": 8001,
                    "targetPort": 8001
                },
                "resources": {
                    "requests": {
                        "memory": "2Gi",
                        "cpu": "1000m",
                        "nvidia.com/gpu": 1
                    },
                    "limits": {
                        "memory": "8Gi",
                        "cpu": "4000m",
                        "nvidia.com/gpu": 1
                    }
                },
                "nodeSelector": {
                    "gpu": "nvidia"
                },
                "tolerations": [
                    {
                        "key": "nvidia.com/gpu",
                        "operator": "Equal",
                        "value": "true",
                        "effect": "NoSchedule"
                    }
                ]
            },
            
            # Monetization Service
            "monetization": {
                "enabled": True,
                "image": {
                    "repository": "ainflue/monetization",
                    "tag": config.app_version,
                    "pullPolicy": "IfNotPresent"
                },
                "replicaCount": config.replica_count,
                "service": {
                    "type": "ClusterIP",
                    "port": 8002,
                    "targetPort": 8002
                },
                "resources": {
                    "requests": {
                        "memory": "256Mi",
                        "cpu": "100m"
                    },
                    "limits": {
                        "memory": "1Gi",
                        "cpu": "500m"
                    }
                },
                "env": {
                    "STRIPE_SECRET_KEY": "",
                    "PAYPAL_CLIENT_ID": "",
                    "REVENUE_SHARE_PERCENTAGE": "70"
                }
            },
            
            # Collaboration Service
            "collaboration": {
                "enabled": True,
                "image": {
                    "repository": "ainflue/collaboration",
                    "tag": config.app_version,
                    "pullPolicy": "IfNotPresent"
                },
                "replicaCount": 2,
                "service": {
                    "type": "ClusterIP",
                    "port": 8003,
                    "targetPort": 8003
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
                }
            },
            
            # Frontend Service
            "frontend": {
                "enabled": True,
                "image": {
                    "repository": "ainflue/creator-dashboard",
                    "tag": config.app_version,
                    "pullPolicy": "IfNotPresent"
                },
                "replicaCount": config.replica_count,
                "service": {
                    "type": "ClusterIP",
                    "port": 80,
                    "targetPort": 3000
                },
                "resources": {
                    "requests": {
                        "memory": "128Mi",
                        "cpu": "50m"
                    },
                    "limits": {
                        "memory": "512Mi",
                        "cpu": "200m"
                    }
                }
            },
            
            # Database Configuration
            "postgresql": {
                "enabled": True,
                "auth": {
                    "postgresPassword": "secure-postgres-password",
                    "username": "creator",
                    "password": "secure-creator-password",
                    "database": "creator_db"
                },
                "primary": {
                    "persistence": {
                        "enabled": config.enable_persistence,
                        "size": "50Gi",
                        "storageClass": "fast-ssd"
                    },
                    "resources": {
                        "requests": {
                            "memory": "1Gi",
                            "cpu": "500m"
                        },
                        "limits": {
                            "memory": "4Gi",
                            "cpu": "2000m"
                        }
                    }
                }
            },
            
            # Redis Configuration
            "redis": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "password": "secure-redis-password"
                },
                "master": {
                    "persistence": {
                        "enabled": config.enable_persistence,
                        "size": "10Gi"
                    },
                    "resources": {
                        "requests": {
                            "memory": "256Mi",
                            "cpu": "100m"
                        },
                        "limits": {
                            "memory": "1Gi",
                            "cpu": "500m"
                        }
                    }
                }
            },
            
            # Ingress Configuration
            "ingress": {
                "enabled": config.enable_ingress,
                "className": "nginx",
                "annotations": {
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                },
                "hosts": [
                    {
                        "host": f"{config.environment.value}.ainflue.com" if config.environment != EnvironmentType.PRODUCTION else "ainflue.com",
                        "paths": [
                            {"path": "/", "pathType": "Prefix", "service": "frontend"},
                            {"path": "/api/creator", "pathType": "Prefix", "service": "creator-api"},
                            {"path": "/api/ai", "pathType": "Prefix", "service": "ai-processor"},
                            {"path": "/api/monetization", "pathType": "Prefix", "service": "monetization"},
                            {"path": "/api/collaboration", "pathType": "Prefix", "service": "collaboration"}
                        ]
                    }
                ],
                "tls": [
                    {
                        "secretName": "ainflue-tls",
                        "hosts": [f"{config.environment.value}.ainflue.com" if config.environment != EnvironmentType.PRODUCTION else "ainflue.com"]
                    }
                ]
            },
            
            # Auto-scaling Configuration
            "autoscaling": {
                "enabled": config.enable_autoscaling,
                "minReplicas": 2 if config.environment == EnvironmentType.PRODUCTION else 1,
                "maxReplicas": 20 if config.environment == EnvironmentType.PRODUCTION else 5,
                "targetCPUUtilizationPercentage": 70,
                "targetMemoryUtilizationPercentage": 80
            },
            
            # Monitoring Configuration
            "monitoring": {
                "enabled": config.enable_monitoring,
                "prometheus": {
                    "enabled": True,
                    "scrapeInterval": "30s"
                },
                "grafana": {
                    "enabled": True,
                    "adminPassword": "secure-grafana-password"
                },
                "serviceMonitor": {
                    "enabled": True,
                    "labels": {
                        "prometheus": "ainflue"
                    }
                }
            },
            
            # Persistence Configuration
            "persistence": {
                "enabled": config.enable_persistence,
                "storageClass": "fast-ssd",
                "accessModes": ["ReadWriteOnce"],
                "sizes": {
                    "content": "100Gi",
                    "models": "50Gi",
                    "cache": "20Gi"
                }
            },
            
            # Security Configuration
            "security": {
                "podSecurityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1001,
                    "fsGroup": 1001
                },
                "securityContext": {
                    "allowPrivilegeEscalation": False,
                    "readOnlyRootFilesystem": True,
                    "capabilities": {
                        "drop": ["ALL"]
                    }
                },
                "networkPolicy": {
                    "enabled": True
                }
            }
        }
    
    def _generate_environment_values(self, config: HelmChartConfig, env: EnvironmentType) -> Dict[str, Any]:
        """Generate environment-specific values"""
        base_values = {
            "global": {
                "imageRegistry": "registry.ainflue.com"
            }
        }
        
        if env == EnvironmentType.DEVELOPMENT:
            base_values.update({
                "creatorApi": {
                    "replicaCount": 1,
                    "resources": {
                        "requests": {"memory": "256Mi", "cpu": "100m"},
                        "limits": {"memory": "1Gi", "cpu": "500m"}
                    }
                },
                "autoscaling": {
                    "enabled": False
                },
                "monitoring": {
                    "enabled": False
                }
            })
        elif env == EnvironmentType.STAGING:
            base_values.update({
                "creatorApi": {
                    "replicaCount": 2
                },
                "autoscaling": {
                    "minReplicas": 1,
                    "maxReplicas": 5
                }
            })
        elif env == EnvironmentType.PRODUCTION:
            base_values.update({
                "creatorApi": {
                    "replicaCount": 5,
                    "resources": {
                        "requests": {"memory": "1Gi", "cpu": "500m"},
                        "limits": {"memory": "4Gi", "cpu": "2000m"}
                    }
                },
                "autoscaling": {
                    "minReplicas": 3,
                    "maxReplicas": 50
                }
            })
        
        return base_values
    
    def _generate_deployment_template(self, config: HelmChartConfig) -> str:
        """Generate Kubernetes deployment template"""
        return """{{- range $service, $values := dict "creator-api" .Values.creatorApi "ai-processor" .Values.aiProcessor "monetization" .Values.monetization "collaboration" .Values.collaboration "frontend" .Values.frontend }}
{{- if $values.enabled }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "ainflue.fullname" $ }}-{{ $service }}
  labels:
    {{- include "ainflue.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $service }}
spec:
  {{- if not $.Values.autoscaling.enabled }}
  replicas: {{ $values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "ainflue.selectorLabels" $ | nindent 6 }}
      app.kubernetes.io/component: {{ $service }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") $ | sha256sum }}
      labels:
        {{- include "ainflue.selectorLabels" $ | nindent 8 }}
        app.kubernetes.io/component: {{ $service }}
    spec:
      {{- with $.Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "ainflue.serviceAccountName" $ }}
      securityContext:
        {{- toYaml $.Values.security.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ $service }}
          securityContext:
            {{- toYaml $.Values.security.securityContext | nindent 12 }}
          image: "{{ $.Values.global.imageRegistry }}/{{ $values.image.repository }}:{{ $values.image.tag | default $.Chart.AppVersion }}"
          imagePullPolicy: {{ $values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ $values.service.targetPort }}
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
          env:
            {{- range $key, $value := $values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
            - name: SERVICE_NAME
              value: {{ $service }}
            - name: NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          resources:
            {{- toYaml $values.resources | nindent 12 }}
          {{- if $values.volumeMounts }}
          volumeMounts:
            {{- toYaml $values.volumeMounts | nindent 12 }}
          {{- end }}
      {{- with $values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with $values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with $values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- if $values.volumes }}
      volumes:
        {{- toYaml $values.volumes | nindent 8 }}
      {{- end }}
{{- end }}
{{- end }}"""
    
    def _generate_service_template(self, config: HelmChartConfig) -> str:
        """Generate Kubernetes service template"""
        return """{{- range $service, $values := dict "creator-api" .Values.creatorApi "ai-processor" .Values.aiProcessor "monetization" .Values.monetization "collaboration" .Values.collaboration "frontend" .Values.frontend }}
{{- if $values.enabled }}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ include "ainflue.fullname" $ }}-{{ $service }}
  labels:
    {{- include "ainflue.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $service }}
spec:
  type: {{ $values.service.type }}
  ports:
    - port: {{ $values.service.port }}
      targetPort: {{ $values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "ainflue.selectorLabels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $service }}
{{- end }}
{{- end }}"""
    
    def _generate_hpa_template(self, config: HelmChartConfig) -> str:
        """Generate HPA template"""
        return """{{- if .Values.autoscaling.enabled }}
{{- range $service, $values := dict "creator-api" .Values.creatorApi "ai-processor" .Values.aiProcessor "monetization" .Values.monetization "collaboration" .Values.collaboration }}
{{- if $values.enabled }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "ainflue.fullname" $ }}-{{ $service }}
  labels:
    {{- include "ainflue.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $service }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "ainflue.fullname" $ }}-{{ $service }}
  minReplicas: {{ $.Values.autoscaling.minReplicas }}
  maxReplicas: {{ $.Values.autoscaling.maxReplicas }}
  metrics:
    {{- if $.Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ $.Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if $.Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ $.Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
{{- end }}
{{- end }}"""
    
    def _generate_helpers_template(self, config: HelmChartConfig) -> str:
        """Generate Helm helpers template"""
        return """{{/*
Expand the name of the chart.
*/}}
{{- define "ainflue.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ainflue.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ainflue.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ainflue.labels" -}}
helm.sh/chart: {{ include "ainflue.chart" . }}
{{ include "ainflue.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: ainflue-creator-economy
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ainflue.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ainflue.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ainflue.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ainflue.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}"""
    
    def export_helm_chart(self, chart_structure: Dict[str, Any], output_dir: str) -> str:
        """Export Helm chart to directory structure"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create main chart files
        for filename, content in chart_structure.items():
            if filename == "templates":
                continue
                
            file_path = output_path / filename
            with open(file_path, 'w') as f:
                if isinstance(content, dict):
                    yaml.dump(content, f, default_flow_style=False, indent=2)
                else:
                    f.write(content)
        
        # Create templates directory
        templates_dir = output_path / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        for template_name, template_content in chart_structure["templates"].items():
            template_path = templates_dir / template_name
            with open(template_path, 'w') as f:
                f.write(template_content)
        
        return str(output_path)

# Example usage
def main():
    """Example usage of Helm Chart Template"""
    template = HelmChartTemplate()
    
    # Generate Helm charts for different environments
    environments = [EnvironmentType.DEVELOPMENT, EnvironmentType.STAGING, EnvironmentType.PRODUCTION]
    
    for env in environments:
        config = HelmChartConfig(
            chart_name="ainflue-creator-economy",
            version="1.0.0",
            app_version="2.0.0",
            description="IA Chéries Creator Economy Platform - Complete Kubernetes Deployment",
            environment=env,
            namespace="ainflue",
            enable_autoscaling=env == EnvironmentType.PRODUCTION,
            replica_count=5 if env == EnvironmentType.PRODUCTION else 2
        )
        
        chart_structure = template.generate_helm_chart(config)
        output_dir = f"helm-chart-{env.value}"
        template.export_helm_chart(chart_structure, output_dir)
        
        print(f"✅ Generated Helm chart for {env.value}: {output_dir}")

if __name__ == "__main__":
    main()