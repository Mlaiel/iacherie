"""Kubernetes Deployment Management for AI Processing Infrastructure
===============================================================

Enterprise-grade Kubernetes deployment orchestration for AI processing systems
with auto-scaling, service mesh integration, and production-ready configurations.

Features:
- Automated Kubernetes deployment management
- Horizontal Pod Autoscaling (HPA) with custom metrics
- Service mesh integration (Istio/Linkerd)
- Advanced resource management and optimization
- Rolling updates and blue-green deployments

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
import yaml
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import uuid

from kubernetes import client as k8s_client, config as k8s_config, watch
from kubernetes.client.rest import ApiException
import jinja2
from prometheus_client import Counter, Histogram, Gauge

from .core import ProcessingConfig, AIModelType
from .monitoring import AlertManager, HealthMonitor

# Metrics
k8s_deployments_total = Counter('k8s_deployments_total', 'Total Kubernetes deployments', ['status'])
k8s_scaling_operations = Counter('k8s_scaling_operations_total', 'Kubernetes scaling operations', ['direction'])
k8s_deployment_time = Histogram('k8s_deployment_time_seconds', 'Kubernetes deployment time')
k8s_pod_count = Gauge('k8s_pod_count', 'Number of pods', ['deployment', 'status'])

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Kubernetes deployment strategies."""    ROLLING_UPDATE = "RollingUpdate"
    RECREATE = "Recreate"
    BLUE_GREEN = "BlueGreen"
    CANARY = "Canary"


class PodStatus(Enum):
    """Pod status enumeration."""    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class ScalingDirection(Enum):
    """Scaling direction."""    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class ResourceRequirements:
    """Kubernetes resource requirements."""    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "256Mi"
    memory_limit: str = "2Gi"
    gpu_limit: int = 0
    ephemeral_storage_request: str = "1Gi"
    ephemeral_storage_limit: str = "10Gi"


@dataclass
class AutoScalingConfig:
    """Horizontal Pod Autoscaler configuration."""    enabled: bool = True
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_up_stabilization_window: int = 60
    scale_down_stabilization_window: int = 300
    custom_metrics: List[Dict[str, Any]] = None


@dataclass
class ServiceConfig:
    """Kubernetes service configuration."""    name: str
    type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    ports: List[Dict[str, Any]] = None
    selector: Dict[str, str] = None
    annotations: Dict[str, str] = None


@dataclass
class IngressConfig:
    """Kubernetes ingress configuration."""    enabled: bool = False
    host: str = ""
    path: str = "/"
    tls_enabled: bool = False
    tls_secret_name: str = ""
    annotations: Dict[str, str] = None


@dataclass
class DeploymentConfig:
    """Complete Kubernetes deployment configuration."""    name: str
    namespace: str = "default"
    image: str = ""
    replicas: int = 3
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    resources: ResourceRequirements = None
    auto_scaling: AutoScalingConfig = None
    service: ServiceConfig = None
    ingress: IngressConfig = None
    environment_variables: Dict[str, str] = None
    config_maps: List[str] = None
    secrets: List[str] = None
    volumes: List[Dict[str, Any]] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    node_selector: Dict[str, str] = None
    tolerations: List[Dict[str, Any]] = None
    affinity: Dict[str, Any] = None


class KubernetesTemplateManager:
    """    Intelligent Kubernetes manifest template manager with
    Jinja2 templating and validation.
    """    
    def __init__(self, template_dir: str = "/templates/kubernetes"):
        """Initialize template manager."""        self.template_dir = Path(template_dir)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=True
        )
        self._ensure_template_directory()
    
    def _ensure_template_directory(self):
        """Ensure template directory exists with default templates."""        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default Kubernetes manifest templates."""        # Deployment template
        deployment_template = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ name }}
  namespace: {{ namespace }}
  labels:
    app: {{ name }}
    component: ai-processing
    {% for key, value in labels.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
  {% if annotations %}
  annotations:
    {% for key, value in annotations.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
  {% endif %}
spec:
  replicas: {{ replicas }}
  strategy:
    type: {{ strategy }}
    {% if strategy == "RollingUpdate" %}
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    {% endif %}
  selector:
    matchLabels:
      app: {{ name }}
  template:
    metadata:
      labels:
        app: {{ name }}
        component: ai-processing
        {% for key, value in labels.items() %}
        {{ key }}: {{ value }}
        {% endfor %}
    spec:
      {% if node_selector %}
      nodeSelector:
        {% for key, value in node_selector.items() %}
        {{ key }}: {{ value }}
        {% endfor %}
      {% endif %}
      
      {% if tolerations %}
      tolerations:
      {% for toleration in tolerations %}
      - key: {{ toleration.key }}
        operator: {{ toleration.operator | default("Equal") }}
        value: {{ toleration.value | default("") }}
        effect: {{ toleration.effect }}
      {% endfor %}
      {% endif %}
      
      {% if affinity %}
      affinity: {{ affinity | tojson }}
      {% endif %}
      
      containers:
      - name: {{ name }}
        image: {{ image }}
        imagePullPolicy: Always
        
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        - containerPort: 8080
          name: metrics
          protocol: TCP
        
        {% if environment_variables %}
        env:
        {% for key, value in environment_variables.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        {% endif %}
        
        resources:
          requests:
            cpu: {{ resources.cpu_request }}
            memory: {{ resources.memory_request }}
            ephemeral-storage: {{ resources.ephemeral_storage_request }}
          limits:
            cpu: {{ resources.cpu_limit }}
            memory: {{ resources.memory_limit }}
            ephemeral-storage: {{ resources.ephemeral_storage_limit }}
            {% if resources.gpu_limit > 0 %}
            nvidia.com/gpu: {{ resources.gpu_limit }}
            {% endif %}
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        {% if volumes %}
        volumeMounts:
        {% for volume in volumes %}
        - name: {{ volume.name }}
          mountPath: {{ volume.mount_path }}
          {% if volume.read_only %}
          readOnly: true
          {% endif %}
        {% endfor %}
        {% endif %}
      
      {% if volumes %}
      volumes:
      {% for volume in volumes %}
      - name: {{ volume.name }}
        {% if volume.type == "configMap" %}
        configMap:
          name: {{ volume.config_map_name }}
        {% elif volume.type == "secret" %}
        secret:
          secretName: {{ volume.secret_name }}
        {% elif volume.type == "persistentVolumeClaim" %}
        persistentVolumeClaim:
          claimName: {{ volume.pvc_name }}
        {% elif volume.type == "emptyDir" %}
        emptyDir: {}
        {% endif %}
      {% endfor %}
      {% endif %}
"""        
        # Service template
        service_template = """apiVersion: v1
kind: Service
metadata:
  name: {{ service.name }}
  namespace: {{ namespace }}
  labels:
    app: {{ name }}
    component: ai-processing
  {% if service.annotations %}
  annotations:
    {% for key, value in service.annotations.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
  {% endif %}
spec:
  type: {{ service.type }}
  ports:
  {% for port in service.ports %}
  - port: {{ port.port }}
    targetPort: {{ port.target_port }}
    protocol: {{ port.protocol | default("TCP") }}
    name: {{ port.name }}
    {% if service.type == "NodePort" and port.node_port %}
    nodePort: {{ port.node_port }}
    {% endif %}
  {% endfor %}
  selector:
    {% for key, value in service.selector.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
"""        
        # HPA template
        hpa_template = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ name }}-hpa
  namespace: {{ namespace }}
  labels:
    app: {{ name }}
    component: ai-processing
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ name }}
  minReplicas: {{ auto_scaling.min_replicas }}
  maxReplicas: {{ auto_scaling.max_replicas }}
  
  behavior:
    scaleUp:
      stabilizationWindowSeconds: {{ auto_scaling.scale_up_stabilization_window }}
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: {{ auto_scaling.scale_down_stabilization_window }}
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      selectPolicy: Min
  
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ auto_scaling.target_cpu_utilization }}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {{ auto_scaling.target_memory_utilization }}
  
  {% if auto_scaling.custom_metrics %}
  {% for metric in auto_scaling.custom_metrics %}
  - type: {{ metric.type }}
    {% if metric.type == "Pods" %}
    pods:
      metric:
        name: {{ metric.name }}
      target:
        type: AverageValue
        averageValue: {{ metric.target_value }}
    {% elif metric.type == "Object" %}
    object:
      metric:
        name: {{ metric.name }}
      describedObject:
        apiVersion: {{ metric.api_version }}
        kind: {{ metric.kind }}
        name: {{ metric.object_name }}
      target:
        type: Value
        value: {{ metric.target_value }}
    {% endif %}
  {% endfor %}
  {% endif %}
"""        
        # Write templates to files
        templates = {
            'deployment.yaml': deployment_template,
            'service.yaml': service_template,
            'hpa.yaml': hpa_template
        }
        
        for filename, content in templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                template_path.write_text(content.strip())
    
    def render_manifest(self, template_name: str, config: DeploymentConfig) -> str:
        """Render Kubernetes manifest from template."""        try:
            template = self.template_env.get_template(template_name)
            
            # Convert config to dict for template rendering
            config_dict = asdict(config)
            
            # Set default values if not provided
            if config_dict.get('resources') is None:
                config_dict['resources'] = asdict(ResourceRequirements())
            
            if config_dict.get('labels') is None:
                config_dict['labels'] = {}
            
            if config_dict.get('annotations') is None:
                config_dict['annotations'] = {}
            
            if config_dict.get('environment_variables') is None:
                config_dict['environment_variables'] = {}
            
            rendered = template.render(**config_dict)
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def render_all_manifests(self, config: DeploymentConfig) -> Dict[str, str]:
        """Render all required manifests for deployment."""        manifests = {}
        
        # Always render deployment
        manifests['deployment'] = self.render_manifest('deployment.yaml', config)
        
        # Render service if configured
        if config.service:
            manifests['service'] = self.render_manifest('service.yaml', config)
        
        # Render HPA if auto-scaling is enabled
        if config.auto_scaling and config.auto_scaling.enabled:
            manifests['hpa'] = self.render_manifest('hpa.yaml', config)
        
        # Render ingress if configured
        if config.ingress and config.ingress.enabled:
            manifests['ingress'] = self._render_ingress_manifest(config)
        
        return manifests
    
    def _render_ingress_manifest(self, config: DeploymentConfig) -> str:
        """Render ingress manifest."""        ingress_template = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ name }}-ingress
  namespace: {{ namespace }}
  labels:
    app: {{ name }}
    component: ai-processing
  {% if ingress.annotations %}
  annotations:
    {% for key, value in ingress.annotations.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
  {% endif %}
spec:
  {% if ingress.tls_enabled %}
  tls:
  - hosts:
    - {{ ingress.host }}
    secretName: {{ ingress.tls_secret_name }}
  {% endif %}
  
  rules:
  - host: {{ ingress.host }}
    http:
      paths:
      - path: {{ ingress.path }}
        pathType: Prefix
        backend:
          service:
            name: {{ service.name }}
            port:
              number: {{ service.ports[0].port }}
"""        
        template = jinja2.Template(ingress_template)
        config_dict = asdict(config)
        return template.render(**config_dict)


class KubernetesClient:
    """    Enhanced Kubernetes client with advanced deployment management,
    monitoring, and error handling capabilities.
    """    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """Initialize Kubernetes client."""        self.kubeconfig_path = kubeconfig_path
        self._load_kube_config()
        
        # Initialize API clients
        self.apps_v1 = k8s_client.AppsV1Api()
        self.core_v1 = k8s_client.CoreV1Api()
        self.autoscaling_v2 = k8s_client.AutoscalingV2Api()
        self.networking_v1 = k8s_client.NetworkingV1Api()
        self.metrics_v1beta1 = k8s_client.CustomObjectsApi()
        
        self.template_manager = KubernetesTemplateManager()
        
    def _load_kube_config(self):
        """Load Kubernetes configuration."""        try:
            if self.kubeconfig_path:
                k8s_config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                # Try in-cluster config first, then default kubeconfig
                try:
                    k8s_config.load_incluster_config()
                    logger.info("Loaded in-cluster Kubernetes configuration")
                except k8s_config.ConfigException:
                    k8s_config.load_kube_config()
                    logger.info("Loaded Kubernetes configuration from default location")
                    
        except Exception as e:
            logger.error(f"Failed to load Kubernetes configuration: {e}")
            raise
    
    async def deploy_application(self, config: DeploymentConfig) -> bool:
        """Deploy application to Kubernetes with full orchestration."""        start_time = time.time()
        
        try:
            logger.info(f"Starting deployment of {config.name} to namespace {config.namespace}")
            
            # Ensure namespace exists
            await self._ensure_namespace(config.namespace)
            
            # Render all manifests
            manifests = self.template_manager.render_all_manifests(config)
            
            # Apply manifests in order
            deployment_success = True
            
            # 1. Deploy main application
            if 'deployment' in manifests:
                success = await self._apply_deployment(manifests['deployment'], config)
                deployment_success = deployment_success and success
            
            # 2. Create service
            if 'service' in manifests:
                success = await self._apply_service(manifests['service'], config)
                deployment_success = deployment_success and success
            
            # 3. Setup auto-scaling
            if 'hpa' in manifests:
                success = await self._apply_hpa(manifests['hpa'], config)
                deployment_success = deployment_success and success
            
            # 4. Setup ingress
            if 'ingress' in manifests:
                success = await self._apply_ingress(manifests['ingress'], config)
                deployment_success = deployment_success and success
            
            # Wait for deployment to be ready
            if deployment_success:
                deployment_ready = await self._wait_for_deployment_ready(
                    config.name, config.namespace, timeout=600
                )
                deployment_success = deployment_success and deployment_ready
            
            # Update metrics
            deploy_time = time.time() - start_time
            k8s_deployment_time.observe(deploy_time)
            
            if deployment_success:
                k8s_deployments_total.labels(status='success').inc()
                logger.info(f"Successfully deployed {config.name} in {deploy_time:.2f}s")
            else:
                k8s_deployments_total.labels(status='failure').inc()
                logger.error(f"Failed to deploy {config.name}")
            
            return deployment_success
            
        except Exception as e:
            k8s_deployments_total.labels(status='error').inc()
            logger.error(f"Deployment failed with exception: {e}")
            return False
    
    async def _ensure_namespace(self, namespace: str):
        """Ensure namespace exists, create if it doesn't."""        try:
            self.core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace_manifest = k8s_client.V1Namespace(
                    metadata=k8s_client.V1ObjectMeta(
                        name=namespace,
                        labels={
                            'name': namespace,
                            'component': 'ai-processing'
                        }
                    )
                )
                self.core_v1.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
            else:
                raise
    
    async def _apply_deployment(self, manifest: str, config: DeploymentConfig) -> bool:
        """Apply deployment manifest."""        try:
            deployment_dict = yaml.safe_load(manifest)
            deployment = k8s_client.ApiClient().sanitize_for_serialization(deployment_dict)
            
            # Check if deployment exists
            try:
                existing = self.apps_v1.read_namespaced_deployment(
                    name=config.name, namespace=config.namespace
                )
                
                # Update existing deployment
                self.apps_v1.patch_namespaced_deployment(
                    name=config.name,
                    namespace=config.namespace,
                    body=deployment
                )
                logger.info(f"Updated deployment: {config.name}")
                
            except ApiException as e:
                if e.status == 404:
                    # Create new deployment
                    self.apps_v1.create_namespaced_deployment(
                        namespace=config.namespace,
                        body=deployment
                    )
                    logger.info(f"Created deployment: {config.name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply deployment: {e}")
            return False
    
    async def _apply_service(self, manifest: str, config: DeploymentConfig) -> bool:
        """Apply service manifest."""        try:
            service_dict = yaml.safe_load(manifest)
            service = k8s_client.ApiClient().sanitize_for_serialization(service_dict)
            
            # Check if service exists
            try:
                existing = self.core_v1.read_namespaced_service(
                    name=config.service.name, namespace=config.namespace
                )
                
                # Update existing service
                self.core_v1.patch_namespaced_service(
                    name=config.service.name,
                    namespace=config.namespace,
                    body=service
                )
                logger.info(f"Updated service: {config.service.name}")
                
            except ApiException as e:
                if e.status == 404:
                    # Create new service
                    self.core_v1.create_namespaced_service(
                        namespace=config.namespace,
                        body=service
                    )
                    logger.info(f"Created service: {config.service.name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply service: {e}")
            return False
    
    async def _apply_hpa(self, manifest: str, config: DeploymentConfig) -> bool:
        """Apply HPA manifest."""        try:
            hpa_dict = yaml.safe_load(manifest)
            hpa = k8s_client.ApiClient().sanitize_for_serialization(hpa_dict)
            
            hpa_name = f"{config.name}-hpa"
            
            # Check if HPA exists
            try:
                existing = self.autoscaling_v2.read_namespaced_horizontal_pod_autoscaler(
                    name=hpa_name, namespace=config.namespace
                )
                
                # Update existing HPA
                self.autoscaling_v2.patch_namespaced_horizontal_pod_autoscaler(
                    name=hpa_name,
                    namespace=config.namespace,
                    body=hpa
                )
                logger.info(f"Updated HPA: {hpa_name}")
                
            except ApiException as e:
                if e.status == 404:
                    # Create new HPA
                    self.autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
                        namespace=config.namespace,
                        body=hpa
                    )
                    logger.info(f"Created HPA: {hpa_name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply HPA: {e}")
            return False
    
    async def _apply_ingress(self, manifest: str, config: DeploymentConfig) -> bool:
        """Apply ingress manifest."""        try:
            ingress_dict = yaml.safe_load(manifest)
            ingress = k8s_client.ApiClient().sanitize_for_serialization(ingress_dict)
            
            ingress_name = f"{config.name}-ingress"
            
            # Check if ingress exists
            try:
                existing = self.networking_v1.read_namespaced_ingress(
                    name=ingress_name, namespace=config.namespace
                )
                
                # Update existing ingress
                self.networking_v1.patch_namespaced_ingress(
                    name=ingress_name,
                    namespace=config.namespace,
                    body=ingress
                )
                logger.info(f"Updated ingress: {ingress_name}")
                
            except ApiException as e:
                if e.status == 404:
                    # Create new ingress
                    self.networking_v1.create_namespaced_ingress(
                        namespace=config.namespace,
                        body=ingress
                    )
                    logger.info(f"Created ingress: {ingress_name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply ingress: {e}")
            return False
    
    async def _wait_for_deployment_ready(self, name: str, namespace: str, timeout: int = 600) -> bool:
        """Wait for deployment to be ready."""        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
                
                # Check if deployment is ready
                if (deployment.status.ready_replicas and 
                    deployment.status.ready_replicas == deployment.spec.replicas):
                    logger.info(f"Deployment {name} is ready")
                    return True
                
                await asyncio.sleep(10)
                
            except ApiException as e:
                logger.error(f"Error checking deployment status: {e}")
                await asyncio.sleep(10)
        
        logger.error(f"Timeout waiting for deployment {name} to be ready")
        return False
    
    async def scale_deployment(self, name: str, namespace: str, replicas: int) -> bool:
        """Scale deployment to specified number of replicas."""        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            current_replicas = deployment.spec.replicas
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Apply update
            self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            # Determine scaling direction
            if replicas > current_replicas:
                direction = ScalingDirection.UP
            elif replicas < current_replicas:
                direction = ScalingDirection.DOWN
            else:
                direction = ScalingDirection.STABLE
            
            # Update metrics
            k8s_scaling_operations.labels(direction=direction.value).inc()
            
            logger.info(f"Scaled deployment {name} from {current_replicas} to {replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale deployment {name}: {e}")
            return False
    
    async def get_deployment_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """Get comprehensive deployment status."""        try:
            # Get deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            # Get pods
            label_selector = f"app={name}"
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            
            # Analyze pod statuses
            pod_statuses = {}
            for status in PodStatus:
                pod_statuses[status.value] = 0
            
            for pod in pods.items:
                pod_status = pod.status.phase
                if pod_status in pod_statuses:
                    pod_statuses[pod_status] += 1
                    k8s_pod_count.labels(deployment=name, status=pod_status.lower()).set(pod_statuses[pod_status])
            
            # Get HPA status if exists
            hpa_status = None
            try:
                hpa = self.autoscaling_v2.read_namespaced_horizontal_pod_autoscaler(
                    name=f"{name}-hpa", namespace=namespace
                )
                hpa_status = {
                    'min_replicas': hpa.spec.min_replicas,
                    'max_replicas': hpa.spec.max_replicas,
                    'current_replicas': hpa.status.current_replicas,
                    'desired_replicas': hpa.status.desired_replicas,
                    'current_cpu_utilization': getattr(hpa.status, 'current_cpu_utilization_percentage', None),
                    'target_cpu_utilization': None
                }
                
                # Extract target CPU utilization from metrics
                for metric in hpa.spec.metrics:
                    if metric.type == 'Resource' and metric.resource.name == 'cpu':
                        hpa_status['target_cpu_utilization'] = metric.resource.target.average_utilization
                        break
                        
            except ApiException as e:
                if e.status != 404:
                    logger.warning(f"Failed to get HPA status: {e}")
            
            return {
                'name': name,
                'namespace': namespace,
                'replicas': {
                    'desired': deployment.spec.replicas,
                    'current': deployment.status.replicas,
                    'ready': deployment.status.ready_replicas,
                    'available': deployment.status.available_replicas,
                    'unavailable': deployment.status.unavailable_replicas
                },
                'conditions': [
                    {
                        'type': condition.type,
                        'status': condition.status,
                        'reason': condition.reason,
                        'message': condition.message,
                        'last_update_time': condition.last_update_time.isoformat() if condition.last_update_time else None
                    }
                    for condition in (deployment.status.conditions or [])
                ],
                'pod_statuses': pod_statuses,
                'hpa_status': hpa_status,
                'creation_timestamp': deployment.metadata.creation_timestamp.isoformat(),
                'labels': deployment.metadata.labels,
                'annotations': deployment.metadata.annotations
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status for {name}: {e}")
            return {}
    
    async def delete_deployment(self, name: str, namespace: str, delete_associated: bool = True) -> bool:
        """Delete deployment and optionally associated resources."""        try:
            deletion_tasks = []
            
            # Delete deployment
            try:
                self.apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
                logger.info(f"Deleted deployment: {name}")
            except ApiException as e:
                if e.status != 404:
                    logger.error(f"Failed to delete deployment {name}: {e}")
                    return False
            
            if delete_associated:
                # Delete service
                try:
                    self.core_v1.delete_namespaced_service(name=f"{name}-service", namespace=namespace)
                    logger.info(f"Deleted service: {name}-service")
                except ApiException as e:
                    if e.status != 404:
                        logger.warning(f"Failed to delete service: {e}")
                
                # Delete HPA
                try:
                    self.autoscaling_v2.delete_namespaced_horizontal_pod_autoscaler(
                        name=f"{name}-hpa", namespace=namespace
                    )
                    logger.info(f"Deleted HPA: {name}-hpa")
                except ApiException as e:
                    if e.status != 404:
                        logger.warning(f"Failed to delete HPA: {e}")
                
                # Delete ingress
                try:
                    self.networking_v1.delete_namespaced_ingress(
                        name=f"{name}-ingress", namespace=namespace
                    )
                    logger.info(f"Deleted ingress: {name}-ingress")
                except ApiException as e:
                    if e.status != 404:
                        logger.warning(f"Failed to delete ingress: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete deployment {name}: {e}")
            return False
    
    async def get_cluster_resources(self) -> Dict[str, Any]:
        """Get cluster resource information."""        try:
            # Get nodes
            nodes = self.core_v1.list_node()
            
            # Calculate cluster capacity
            total_cpu = 0
            total_memory = 0
            total_pods = 0
            
            for node in nodes.items:
                if node.status.capacity:
                    # Parse CPU (can be in cores or millicores)
                    cpu_str = node.status.capacity.get('cpu', '0')
                    if cpu_str.endswith('m'):
                        cpu_cores = int(cpu_str[:-1]) / 1000
                    else:
                        cpu_cores = int(cpu_str)
                    total_cpu += cpu_cores
                    
                    # Parse memory (convert to bytes)
                    memory_str = node.status.capacity.get('memory', '0Ki')
                    memory_bytes = self._parse_memory(memory_str)
                    total_memory += memory_bytes
                    
                    # Pods
                    pods = int(node.status.capacity.get('pods', '0'))
                    total_pods += pods
            
            # Get current resource usage
            all_pods = self.core_v1.list_pod_for_all_namespaces()
            
            used_cpu = 0
            used_memory = 0
            running_pods = 0
            
            for pod in all_pods.items:
                if pod.status.phase == 'Running':
                    running_pods += 1
                    
                    # Sum container resources
                    if pod.spec.containers:
                        for container in pod.spec.containers:
                            if container.resources and container.resources.requests:
                                # CPU
                                cpu_req = container.resources.requests.get('cpu', '0')
                                if cpu_req.endswith('m'):
                                    used_cpu += int(cpu_req[:-1]) / 1000
                                else:
                                    used_cpu += int(cpu_req) if cpu_req.isdigit() else 0
                                
                                # Memory
                                memory_req = container.resources.requests.get('memory', '0')
                                used_memory += self._parse_memory(memory_req)
            
            return {
                'cluster_capacity': {
                    'cpu_cores': total_cpu,
                    'memory_bytes': total_memory,
                    'memory_gb': total_memory / (1024**3),
                    'max_pods': total_pods
                },
                'cluster_usage': {
                    'cpu_cores': used_cpu,
                    'cpu_utilization_percent': (used_cpu / total_cpu * 100) if total_cpu > 0 else 0,
                    'memory_bytes': used_memory,
                    'memory_gb': used_memory / (1024**3),
                    'memory_utilization_percent': (used_memory / total_memory * 100) if total_memory > 0 else 0,
                    'running_pods': running_pods,
                    'pod_utilization_percent': (running_pods / total_pods * 100) if total_pods > 0 else 0
                },
                'nodes': [
                    {
                        'name': node.metadata.name,
                        'ready': any(condition.type == 'Ready' and condition.status == 'True' 
                                   for condition in node.status.conditions),
                        'cpu_capacity': node.status.capacity.get('cpu') if node.status.capacity else None,
                        'memory_capacity': node.status.capacity.get('memory') if node.status.capacity else None,
                        'pod_capacity': node.status.capacity.get('pods') if node.status.capacity else None,
                        'labels': node.metadata.labels,
                        'annotations': node.metadata.annotations
                    }
                    for node in nodes.items
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster resources: {e}")
            return {}
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse Kubernetes memory string to bytes."""        if not memory_str or memory_str == '0':
            return 0
        
        # Remove trailing whitespace
        memory_str = memory_str.strip()
        
        # Define unit multipliers
        units = {
            'Ki': 1024,
            'Mi': 1024**2,
            'Gi': 1024**3,
            'Ti': 1024**4,
            'K': 1000,
            'M': 1000**2,
            'G': 1000**3,
            'T': 1000**4
        }
        
        # Check for unit suffix
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                value = float(memory_str[:-len(unit)])
                return int(value * multiplier)
        
        # If no unit, assume bytes
        try:
            return int(memory_str)
        except ValueError:
            logger.warning(f"Could not parse memory string: {memory_str}")
            return 0


class KubernetesDeploymentManager:
    """    Complete Kubernetes deployment management system coordinating
    all aspects of AI processing infrastructure deployment.
    """    
    def __init__(self, config: ProcessingConfig):
        """Initialize deployment manager."""        self.config = config
        self.k8s_client = KubernetesClient()
        self.active_deployments: Dict[str, DeploymentConfig] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
    async def deploy_ai_processing_infrastructure(self, 
                                                tenant_id: str,
                                                deployment_config: Optional[DeploymentConfig] = None) -> bool:
        """Deploy complete AI processing infrastructure for tenant."""        try:
            logger.info(f"Deploying AI processing infrastructure for tenant: {tenant_id}")
            
            # Use provided config or create default
            if deployment_config is None:
                deployment_config = self._create_default_deployment_config(tenant_id)
            
            # Deploy main application
            success = await self.k8s_client.deploy_application(deployment_config)
            
            if success:
                # Store deployment info
                self.active_deployments[tenant_id] = deployment_config
                
                # Record deployment history
                self.deployment_history.append({
                    'tenant_id': tenant_id,
                    'deployment_name': deployment_config.name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'success',
                    'config': asdict(deployment_config)
                })
                
                logger.info(f"Successfully deployed infrastructure for tenant: {tenant_id}")
            else:
                logger.error(f"Failed to deploy infrastructure for tenant: {tenant_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Infrastructure deployment failed for {tenant_id}: {e}")
            return False
    
    def _create_default_deployment_config(self, tenant_id: str) -> DeploymentConfig:
        """Create default deployment configuration for AI processing."""        deployment_name = f"ai-processing-{tenant_id}"
        namespace = f"ai-processing"
        
        return DeploymentConfig(
            name=deployment_name,
            namespace=namespace,
            image="ai-processing:latest",
            replicas=3,
            strategy=DeploymentStrategy.ROLLING_UPDATE,
            resources=ResourceRequirements(
                cpu_request="500m",
                cpu_limit="2000m",
                memory_request="1Gi",
                memory_limit="4Gi",
                gpu_limit=1 if self.config.gpu_enabled else 0
            ),
            auto_scaling=AutoScalingConfig(
                enabled=True,
                min_replicas=2,
                max_replicas=10,
                target_cpu_utilization=70,
                target_memory_utilization=80
            ),
            service=ServiceConfig(
                name=f"{deployment_name}-service",
                type="ClusterIP",
                ports=[
                    {"name": "http", "port": 8000, "target_port": 8000, "protocol": "TCP"},
                    {"name": "metrics", "port": 8080, "target_port": 8080, "protocol": "TCP"}
                ],
                selector={"app": deployment_name}
            ),
            environment_variables={
                "TENANT_ID": tenant_id,
                "AI_PROCESSING_MODE": "production",
                "GPU_ENABLED": str(self.config.gpu_enabled),
                "MAX_WORKERS": str(self.config.max_workers),
                "REDIS_URL": "redis://redis-service:6379",
                "DATABASE_URL": "postgresql://postgres:password@postgres-service:5432/ai_processing"
            },
            labels={
                "tenant": tenant_id,
                "component": "ai-processing",
                "environment": "production"
            },
            node_selector={
                "node-type": "ai-processing"
            } if self.config.gpu_enabled else None
        )
    
    async def scale_tenant_deployment(self, tenant_id: str, replicas: int) -> bool:
        """Scale deployment for specific tenant."""        if tenant_id not in self.active_deployments:
            logger.error(f"No active deployment found for tenant: {tenant_id}")
            return False
        
        config = self.active_deployments[tenant_id]
        return await self.k8s_client.scale_deployment(config.name, config.namespace, replicas)
    
    async def get_tenant_deployment_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get deployment status for specific tenant."""        if tenant_id not in self.active_deployments:
            return {"error": f"No active deployment found for tenant: {tenant_id}"}
        
        config = self.active_deployments[tenant_id]
        return await self.k8s_client.get_deployment_status(config.name, config.namespace)
    
    async def remove_tenant_deployment(self, tenant_id: str) -> bool:
        """Remove deployment for specific tenant."""        if tenant_id not in self.active_deployments:
            logger.warning(f"No active deployment found for tenant: {tenant_id}")
            return True
        
        config = self.active_deployments[tenant_id]
        success = await self.k8s_client.delete_deployment(config.name, config.namespace)
        
        if success:
            del self.active_deployments[tenant_id]
            logger.info(f"Removed deployment for tenant: {tenant_id}")
        
        return success
    
    async def get_cluster_overview(self) -> Dict[str, Any]:
        """Get comprehensive cluster and deployment overview."""        try:
            # Get cluster resources
            cluster_resources = await self.k8s_client.get_cluster_resources()
            
            # Get status of all active deployments
            deployment_statuses = {}
            for tenant_id, config in self.active_deployments.items():
                status = await self.k8s_client.get_deployment_status(config.name, config.namespace)
                deployment_statuses[tenant_id] = status
            
            return {
                'cluster_resources': cluster_resources,
                'active_deployments': len(self.active_deployments),
                'deployment_statuses': deployment_statuses,
                'deployment_history_count': len(self.deployment_history),
                'last_deployment': self.deployment_history[-1] if self.deployment_history else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster overview: {e}")
            return {"error": str(e)}


# Factory functions for quick deployment setup
async def create_ai_processing_deployment(tenant_id: str, 
                                        config: ProcessingConfig,
                                        custom_config: Optional[DeploymentConfig] = None) -> KubernetesDeploymentManager:
    """Create and deploy AI processing infrastructure for tenant."""    manager = KubernetesDeploymentManager(config)
    
    success = await manager.deploy_ai_processing_infrastructure(tenant_id, custom_config)
    
    if not success:
        raise Exception(f"Failed to deploy AI processing infrastructure for tenant: {tenant_id}")
    
    return manager


def create_gpu_deployment_config(tenant_id: str, gpu_count: int = 1) -> DeploymentConfig:
    """Create deployment configuration optimized for GPU processing."""    deployment_name = f"ai-processing-gpu-{tenant_id}"
    
    return DeploymentConfig(
        name=deployment_name,
        namespace="ai-processing",
        image="ai-processing:gpu-latest",
        replicas=2,
        resources=ResourceRequirements(
            cpu_request="1000m",
            cpu_limit="4000m", 
            memory_request="4Gi",
            memory_limit="16Gi",
            gpu_limit=gpu_count
        ),
        auto_scaling=AutoScalingConfig(
            enabled=True,
            min_replicas=1,
            max_replicas=5,
            target_cpu_utilization=60,
            target_memory_utilization=70
        ),
        node_selector={
            "accelerator": "nvidia-tesla-v100"
        },
        tolerations=[
            {
                "key": "nvidia.com/gpu",
                "operator": "Exists",
                "effect": "NoSchedule"
            }
        ],
        labels={
            "tenant": tenant_id,
            "gpu-enabled": "true",
            "processing-type": "intensive"
        }
    )
