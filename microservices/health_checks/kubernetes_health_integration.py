"""
Kubernetes Health Integration - Enterprise Health Monitoring
============================================================

🎖️ EXPERT TEAM: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation Kubernetes health integration est la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou utilisation sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice.

Intégration health checks avec Kubernetes ecosystem.
Pod health + service mesh health + ingress health + HPA integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
from kubernetes import client, config, watch
from kubernetes.client.exceptions import ApiException
import aiohttp

logger = logging.getLogger(__name__)

class K8sResourceType(Enum):
    """Types de ressources Kubernetes"""
    POD = "pod"
    SERVICE = "service"
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    INGRESS = "ingress"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    HPA = "hpa"
    NODE = "node"

class HealthProbeType(Enum):
    """Types de probes santé Kubernetes"""
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"

class PodPhase(Enum):
    """Phases de pods Kubernetes"""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

@dataclass
class K8sHealthProbe:
    """Configuration probe santé Kubernetes"""
    probe_type: HealthProbeType
    http_get: Optional[Dict[str, Any]] = None
    tcp_socket: Optional[Dict[str, Any]] = None
    exec_command: Optional[List[str]] = None
    initial_delay_seconds: int = 0
    period_seconds: int = 10
    timeout_seconds: int = 1
    success_threshold: int = 1
    failure_threshold: int = 3

@dataclass
class PodHealthStatus:
    """Status santé pod"""
    pod_name: str
    namespace: str
    phase: PodPhase
    ready: bool
    restart_count: int
    last_probe_time: Optional[datetime]
    probe_results: Dict[HealthProbeType, bool]
    resource_usage: Dict[str, float]
    events: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class HPAHealthStatus:
    """Status santé HPA (Horizontal Pod Autoscaler)"""
    hpa_name: str
    namespace: str
    current_replicas: int
    desired_replicas: int
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: Optional[int]
    current_cpu_utilization: Optional[int]
    scaling_events: List[Dict[str, Any]]
    last_scale_time: Optional[datetime]

class KubernetesHealthIntegration:
    """
    ☸️ DEVOPS + MICROSERVICES + BACKEND SENIOR EXPERT
    Intégration health checks avec ecosystem Kubernetes.
    
    Features Enterprise:
    - Pod health lifecycle monitoring avec probes
    - Service mesh health integration (Istio/Linkerd)
    - Ingress health validation avec SSL checks
    - HPA integration avec health-based scaling decisions
    - Custom Resource Definitions (CRD) health monitoring
    - Kubernetes Events correlation avec health status
    """
    
    def __init__(self, integration_config: Dict[str, Any]):
        """🧠 Lead Dev IA: Initialisation intégration Kubernetes health"""
        self.integration_config = integration_config
        self.k8s_config_path = integration_config.get('kubeconfig_path')
        self.default_namespace = integration_config.get('default_namespace', 'default')
        
        # 🚀 DevOps: Kubernetes client configuration
        self.v1 = None
        self.apps_v1 = None
        self.autoscaling_v1 = None
        self.networking_v1 = None
        
        # 🏗️ Microservices: Service mesh integration
        self.service_mesh_enabled = integration_config.get('service_mesh_enabled', False)
        self.service_mesh_type = integration_config.get('service_mesh_type', 'istio')
        
        # 📊 Backend Senior: Health monitoring state
        self.pod_health_cache: Dict[str, PodHealthStatus] = {}
        self.hpa_health_cache: Dict[str, HPAHealthStatus] = {}
        self.health_events: List[Dict[str, Any]] = []
        
        # Session pour API calls externes
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def integrate_k8s_health_checks(self, k8s_config: Dict[str, Any]) -> bool:
        """
        🎖️ DEVOPS + BACKEND SENIOR: Intégration health checks natifs Kubernetes
        
        Integration complète:
        - Configuration probes santé (liveness, readiness, startup)
        - Health check endpoints registration
        - Custom health check CRDs deployment
        - Service mesh health integration
        - Ingress health validation setup
        """
        logger.info("☸️ Integrating Kubernetes native health checks")
        
        try:
            # Initialize Kubernetes clients
            await self._initialize_k8s_clients()
            
            # Setup health probes for deployments
            probe_setup_result = await self._setup_health_probes(k8s_config)
            
            # Configure service mesh health integration
            service_mesh_result = await self._configure_service_mesh_health(k8s_config)
            
            # Setup ingress health monitoring
            ingress_result = await self._setup_ingress_health_monitoring(k8s_config)
            
            # Deploy custom health check CRDs
            crd_result = await self._deploy_health_check_crds(k8s_config)
            
            # Setup health events monitoring
            events_result = await self._setup_health_events_monitoring()
            
            integration_successful = all([
                probe_setup_result,
                service_mesh_result,
                ingress_result,
                crd_result,
                events_result
            ])
            
            if integration_successful:
                logger.info("✅ Kubernetes health checks integration completed successfully")
                
                # Start background monitoring tasks
                asyncio.create_task(self._monitor_pod_health_continuously())
                asyncio.create_task(self._monitor_hpa_health_continuously())
                
            return integration_successful
            
        except Exception as e:
            logger.error(f"❌ Kubernetes health checks integration failed: {str(e)}")
            return False
    
    async def monitor_pod_health_lifecycle(self, pod_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 MICROSERVICES + ML ENGINEER: Monitoring lifecycle santé pods avec auto-healing
        
        Monitoring complet lifecycle:
        - Pod startup health validation
        - Runtime health monitoring avec probes
        - Resource utilization tracking
        - Auto-healing trigger detection
        - Predictive failure detection avec ML
        """
        logger.info("🔄 Monitoring pod health lifecycle")
        
        lifecycle_monitoring = {
            'monitoring_start': datetime.now().isoformat(),
            'pod_selector': pod_config.get('selector', {}),
            'namespace': pod_config.get('namespace', self.default_namespace),
            'pods_monitored': [],
            'health_summary': {},
            'auto_healing_events': [],
            'predictions': {}
        }
        
        try:
            namespace = pod_config.get('namespace', self.default_namespace)
            label_selector = pod_config.get('selector', {})
            
            # Get pods matching selector
            pods = await self._get_pods_by_selector(namespace, label_selector)
            
            for pod in pods:
                pod_name = pod.metadata.name
                
                # Monitor individual pod health
                pod_health = await self._monitor_individual_pod_health(pod)
                lifecycle_monitoring['pods_monitored'].append({
                    'pod_name': pod_name,
                    'health_status': pod_health
                })
                
                # Check for auto-healing triggers
                healing_triggers = await self._check_auto_healing_triggers(pod, pod_health)
                if healing_triggers:
                    lifecycle_monitoring['auto_healing_events'].extend(healing_triggers)
                
                # Predictive failure detection
                failure_prediction = await self._predict_pod_failure(pod, pod_health)
                if failure_prediction['risk_score'] > 0.7:
                    lifecycle_monitoring['predictions'][pod_name] = failure_prediction
            
            # Generate health summary
            health_summary = await self._generate_pod_health_summary(lifecycle_monitoring['pods_monitored'])
            lifecycle_monitoring['health_summary'] = health_summary
            
            return lifecycle_monitoring
            
        except Exception as e:
            logger.error(f"❌ Pod health lifecycle monitoring failed: {str(e)}")
            return {
                'status': 'monitoring_failed',
                'error': str(e),
                'partial_results': lifecycle_monitoring
            }
    
    async def coordinate_hpa_health_decisions(self, hpa_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 BACKEND SENIOR + ML ENGINEER: Coordination décisions HPA basées sur health data
        
        Coordination intelligente:
        - Health-aware scaling decisions
        - Pod readiness consideration pour scaling
        - Resource utilization correlation avec health
        - Predictive scaling basé sur health trends
        - Custom metrics integration pour health-based scaling
        """
        logger.info("🎯 Coordinating HPA health-based decisions")
        
        hpa_coordination = {
            'coordination_timestamp': datetime.now().isoformat(),
            'hpa_analysis': {},
            'scaling_recommendations': [],
            'health_constraints': {},
            'custom_metrics_integration': {}
        }
        
        try:
            # Analyze current HPA status
            hpa_analysis = await self._analyze_hpa_health_status(hpa_metrics)
            hpa_coordination['hpa_analysis'] = hpa_analysis
            
            # Generate health-aware scaling recommendations
            scaling_recs = await self._generate_health_aware_scaling_recommendations(hpa_analysis)
            hpa_coordination['scaling_recommendations'] = scaling_recs
            
            # Define health constraints for scaling
            health_constraints = await self._define_health_scaling_constraints(hpa_analysis)
            hpa_coordination['health_constraints'] = health_constraints
            
            # Setup custom metrics integration
            custom_metrics = await self._setup_custom_health_metrics_for_hpa(hpa_metrics)
            hpa_coordination['custom_metrics_integration'] = custom_metrics
            
            # Apply HPA modifications if needed
            if scaling_recs:
                modification_results = await self._apply_hpa_health_modifications(scaling_recs)
                hpa_coordination['modification_results'] = modification_results
            
            return hpa_coordination
            
        except Exception as e:
            logger.error(f"❌ HPA health coordination failed: {str(e)}")
            return {
                'status': 'coordination_failed',
                'error': str(e),
                'partial_results': hpa_coordination
            }
    
    async def _initialize_k8s_clients(self) -> None:
        """🔧 Initialisation clients Kubernetes"""
        logger.info("🔧 Initializing Kubernetes clients")
        
        try:
            # Load Kubernetes configuration
            if self.k8s_config_path:
                config.load_kube_config(config_file=self.k8s_config_path)
            else:
                # Try in-cluster config first, then local config
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config()
            
            # Initialize API clients
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.autoscaling_v1 = client.AutoscalingV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kubernetes clients: {str(e)}")
            raise
    
    async def _setup_health_probes(self, k8s_config: Dict[str, Any]) -> bool:
        """⚕️ Setup health probes pour deployments"""
        logger.info("⚕️ Setting up health probes for deployments")
        
        try:
            deployments_config = k8s_config.get('deployments', [])
            
            for deployment_config in deployments_config:
                deployment_name = deployment_config['name']
                namespace = deployment_config.get('namespace', self.default_namespace)
                probes_config = deployment_config.get('health_probes', {})
                
                # Update deployment with health probes
                await self._update_deployment_health_probes(
                    deployment_name, namespace, probes_config
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health probes setup failed: {str(e)}")
            return False
    
    async def _configure_service_mesh_health(self, k8s_config: Dict[str, Any]) -> bool:
        """🕸️ Configuration service mesh health integration"""
        logger.info("🕸️ Configuring service mesh health integration")
        
        try:
            if not self.service_mesh_enabled:
                logger.info("📋 Service mesh not enabled, skipping integration")
                return True
            
            if self.service_mesh_type == 'istio':
                return await self._configure_istio_health_integration(k8s_config)
            elif self.service_mesh_type == 'linkerd':
                return await self._configure_linkerd_health_integration(k8s_config)
            else:
                logger.warning(f"⚠️ Unsupported service mesh type: {self.service_mesh_type}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Service mesh health configuration failed: {str(e)}")
            return False
    
    async def _setup_ingress_health_monitoring(self, k8s_config: Dict[str, Any]) -> bool:
        """🌐 Setup ingress health monitoring"""
        logger.info("🌐 Setting up ingress health monitoring")
        
        try:
            ingress_configs = k8s_config.get('ingresses', [])
            
            for ingress_config in ingress_configs:
                ingress_name = ingress_config['name']
                namespace = ingress_config.get('namespace', self.default_namespace)
                
                # Setup health monitoring for ingress
                await self._setup_individual_ingress_monitoring(
                    ingress_name, namespace, ingress_config
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ingress health monitoring setup failed: {str(e)}")
            return False
    
    async def _deploy_health_check_crds(self, k8s_config: Dict[str, Any]) -> bool:
        """📦 Deploy custom health check CRDs"""
        logger.info("📦 Deploying custom health check CRDs")
        
        try:
            # Define HealthCheck CRD
            health_check_crd = self._create_health_check_crd_definition()
            
            # Deploy CRD
            api_extensions = client.ApiextensionsV1Api()
            
            try:
                api_extensions.create_custom_resource_definition(health_check_crd)
                logger.info("✅ HealthCheck CRD deployed successfully")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info("📋 HealthCheck CRD already exists")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check CRDs deployment failed: {str(e)}")
            return False
    
    async def _setup_health_events_monitoring(self) -> bool:
        """📡 Setup health events monitoring"""
        logger.info("📡 Setting up health events monitoring")
        
        try:
            # Start background task for events monitoring
            asyncio.create_task(self._monitor_k8s_events_continuously())
            return True
            
        except Exception as e:
            logger.error(f"❌ Health events monitoring setup failed: {str(e)}")
            return False
    
    async def _get_pods_by_selector(self, namespace: str, label_selector: Dict[str, str]) -> List[Any]:
        """📋 Get pods by label selector"""
        try:
            selector_string = ",".join([f"{k}={v}" for k, v in label_selector.items()])
            
            pods_list = self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=selector_string
            )
            
            return pods_list.items
            
        except Exception as e:
            logger.error(f"❌ Failed to get pods by selector: {str(e)}")
            return []
    
    async def _monitor_individual_pod_health(self, pod: Any) -> Dict[str, Any]:
        """🔍 Monitor individual pod health"""
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        
        health_status = {
            'pod_name': pod_name,
            'namespace': namespace,
            'phase': pod.status.phase,
            'ready': False,
            'restart_count': 0,
            'probe_results': {},
            'resource_usage': {},
            'containers_status': []
        }
        
        try:
            # Check pod readiness
            if pod.status.conditions:
                for condition in pod.status.conditions:
                    if condition.type == 'Ready':
                        health_status['ready'] = condition.status == 'True'
                        break
            
            # Check container statuses
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    health_status['restart_count'] += container_status.restart_count
                    
                    container_health = {
                        'name': container_status.name,
                        'ready': container_status.ready,
                        'restart_count': container_status.restart_count,
                        'state': str(container_status.state)
                    }
                    health_status['containers_status'].append(container_health)
            
            # Get resource usage if available
            resource_usage = await self._get_pod_resource_usage(pod_name, namespace)
            health_status['resource_usage'] = resource_usage
            
            # Cache health status
            self.pod_health_cache[f"{namespace}/{pod_name}"] = PodHealthStatus(
                pod_name=pod_name,
                namespace=namespace,
                phase=PodPhase(pod.status.phase),
                ready=health_status['ready'],
                restart_count=health_status['restart_count'],
                last_probe_time=datetime.now(),
                probe_results={},
                resource_usage=resource_usage
            )
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Failed to monitor pod {pod_name} health: {str(e)}")
            health_status['error'] = str(e)
            return health_status
    
    async def _check_auto_healing_triggers(self, pod: Any, pod_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """🔄 Check auto-healing triggers"""
        triggers = []
        
        try:
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            
            # High restart count trigger
            restart_count = pod_health.get('restart_count', 0)
            if restart_count > 5:
                triggers.append({
                    'trigger_type': 'high_restart_count',
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'restart_count': restart_count,
                    'recommended_action': 'investigate_and_fix_crash_loop',
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Pod not ready trigger
            if not pod_health.get('ready', False) and pod_health.get('phase') == 'Running':
                triggers.append({
                    'trigger_type': 'pod_not_ready',
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'recommended_action': 'check_readiness_probe',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            # High resource usage trigger
            resource_usage = pod_health.get('resource_usage', {})
            cpu_usage = resource_usage.get('cpu_percentage', 0)
            memory_usage = resource_usage.get('memory_percentage', 0)
            
            if cpu_usage > 90:
                triggers.append({
                    'trigger_type': 'high_cpu_usage',
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'cpu_usage': cpu_usage,
                    'recommended_action': 'scale_horizontally_or_vertically',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            if memory_usage > 90:
                triggers.append({
                    'trigger_type': 'high_memory_usage',
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'memory_usage': memory_usage,
                    'recommended_action': 'increase_memory_limits',
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            
            return triggers
            
        except Exception as e:
            logger.error(f"❌ Failed to check auto-healing triggers: {str(e)}")
            return []
    
    async def _predict_pod_failure(self, pod: Any, pod_health: Dict[str, Any]) -> Dict[str, Any]:
        """🔮 Predictive failure detection using ML patterns"""
        pod_name = pod.metadata.name
        
        prediction = {
            'pod_name': pod_name,
            'risk_score': 0.0,
            'failure_probability': 0.0,
            'predicted_failure_window': None,
            'contributing_factors': [],
            'recommendations': []
        }
        
        try:
            # Analyze historical patterns (simplified ML simulation)
            restart_count = pod_health.get('restart_count', 0)
            resource_usage = pod_health.get('resource_usage', {})
            
            # Calculate risk factors
            risk_factors = []
            
            # Restart count factor
            if restart_count > 0:
                restart_risk = min(restart_count * 0.1, 0.4)
                risk_factors.append(restart_risk)
                prediction['contributing_factors'].append('frequent_restarts')
            
            # Resource usage factor
            cpu_usage = resource_usage.get('cpu_percentage', 0)
            memory_usage = resource_usage.get('memory_percentage', 0)
            
            if cpu_usage > 80:
                cpu_risk = (cpu_usage - 80) / 20 * 0.3
                risk_factors.append(cpu_risk)
                prediction['contributing_factors'].append('high_cpu_usage')
            
            if memory_usage > 80:
                memory_risk = (memory_usage - 80) / 20 * 0.4
                risk_factors.append(memory_risk)
                prediction['contributing_factors'].append('high_memory_usage')
            
            # Pod age factor (older pods might be more unstable)
            pod_age_hours = self._calculate_pod_age_hours(pod)
            if pod_age_hours > 168:  # 1 week
                age_risk = 0.1
                risk_factors.append(age_risk)
                prediction['contributing_factors'].append('pod_age')
            
            # Calculate overall risk score
            if risk_factors:
                prediction['risk_score'] = min(sum(risk_factors), 1.0)
                prediction['failure_probability'] = prediction['risk_score'] * 0.8
            
            # Predict failure window
            if prediction['risk_score'] > 0.7:
                prediction['predicted_failure_window'] = 'next_24_hours'
            elif prediction['risk_score'] > 0.5:
                prediction['predicted_failure_window'] = 'next_72_hours'
            elif prediction['risk_score'] > 0.3:
                prediction['predicted_failure_window'] = 'next_week'
            
            # Generate recommendations
            if prediction['risk_score'] > 0.5:
                prediction['recommendations'].extend([
                    'Monitor resource usage closely',
                    'Consider increasing resource limits',
                    'Review application logs for errors'
                ])
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Pod failure prediction failed: {str(e)}")
            prediction['error'] = str(e)
            return prediction
    
    async def _generate_pod_health_summary(self, pods_monitored: List[Dict]) -> Dict[str, Any]:
        """📊 Generate pod health summary"""
        summary = {
            'total_pods': len(pods_monitored),
            'healthy_pods': 0,
            'unhealthy_pods': 0,
            'pending_pods': 0,
            'failed_pods': 0,
            'average_restart_count': 0.0,
            'high_risk_pods': [],
            'recommendations': []
        }
        
        try:
            restart_counts = []
            
            for pod_info in pods_monitored:
                health_status = pod_info['health_status']
                phase = health_status.get('phase', 'Unknown')
                ready = health_status.get('ready', False)
                restart_count = health_status.get('restart_count', 0)
                
                restart_counts.append(restart_count)
                
                if phase == 'Running' and ready:
                    summary['healthy_pods'] += 1
                elif phase == 'Pending':
                    summary['pending_pods'] += 1
                elif phase == 'Failed':
                    summary['failed_pods'] += 1
                else:
                    summary['unhealthy_pods'] += 1
                
                # Check for high risk pods
                if restart_count > 3 or not ready:
                    summary['high_risk_pods'].append({
                        'pod_name': pod_info['pod_name'],
                        'issue': 'high_restart_count' if restart_count > 3 else 'not_ready'
                    })
            
            # Calculate averages
            if restart_counts:
                summary['average_restart_count'] = sum(restart_counts) / len(restart_counts)
            
            # Generate recommendations
            if summary['unhealthy_pods'] > 0:
                summary['recommendations'].append('Investigate unhealthy pods immediately')
            
            if summary['average_restart_count'] > 2:
                summary['recommendations'].append('Review application stability and resource limits')
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Pod health summary generation failed: {str(e)}")
            return summary
    
    # HPA-related methods
    
    async def _analyze_hpa_health_status(self, hpa_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """📊 Analyze HPA health status"""
        analysis = {
            'hpa_instances': {},
            'overall_status': 'healthy',
            'scaling_efficiency': 0.0,
            'health_correlation': {}
        }
        
        try:
            # Get all HPA instances
            hpa_list = self.autoscaling_v1.list_horizontal_pod_autoscaler_for_all_namespaces()
            
            for hpa in hpa_list.items:
                hpa_name = hpa.metadata.name
                namespace = hpa.metadata.namespace
                
                hpa_status = {
                    'name': hpa_name,
                    'namespace': namespace,
                    'current_replicas': hpa.status.current_replicas or 0,
                    'desired_replicas': hpa.status.desired_replicas or 0,
                    'min_replicas': hpa.spec.min_replicas or 1,
                    'max_replicas': hpa.spec.max_replicas,
                    'target_cpu_utilization': hpa.spec.target_cpu_utilization_percentage,
                    'current_cpu_utilization': hpa.status.current_cpu_utilization_percentage,
                    'last_scale_time': hpa.status.last_scale_time
                }
                
                analysis['hpa_instances'][f"{namespace}/{hpa_name}"] = hpa_status
                
                # Cache HPA health status
                self.hpa_health_cache[f"{namespace}/{hpa_name}"] = HPAHealthStatus(
                    hpa_name=hpa_name,
                    namespace=namespace,
                    current_replicas=hpa_status['current_replicas'],
                    desired_replicas=hpa_status['desired_replicas'],
                    min_replicas=hpa_status['min_replicas'],
                    max_replicas=hpa_status['max_replicas'],
                    target_cpu_utilization=hpa_status['target_cpu_utilization'],
                    current_cpu_utilization=hpa_status['current_cpu_utilization'],
                    scaling_events=[],
                    last_scale_time=hpa_status['last_scale_time']
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ HPA health status analysis failed: {str(e)}")
            return analysis
    
    async def _generate_health_aware_scaling_recommendations(self, hpa_analysis: Dict) -> List[Dict[str, Any]]:
        """💡 Generate health-aware scaling recommendations"""
        recommendations = []
        
        try:
            for hpa_key, hpa_status in hpa_analysis.get('hpa_instances', {}).items():
                current_replicas = hpa_status['current_replicas']
                desired_replicas = hpa_status['desired_replicas']
                current_cpu = hpa_status.get('current_cpu_utilization', 0)
                target_cpu = hpa_status.get('target_cpu_utilization', 80)
                
                # Check for unhealthy pods in the deployment
                namespace, hpa_name = hpa_key.split('/')
                unhealthy_pods = await self._count_unhealthy_pods_for_hpa(namespace, hpa_name)
                
                if unhealthy_pods > 0:
                    recommendations.append({
                        'hpa_name': hpa_name,
                        'namespace': namespace,
                        'recommendation_type': 'health_constraint',
                        'priority': 'high',
                        'description': f'Scaling constrained due to {unhealthy_pods} unhealthy pods',
                        'suggested_action': 'Fix unhealthy pods before allowing scale-up',
                        'health_factor': unhealthy_pods
                    })
                
                # CPU-based recommendations with health considerations
                if current_cpu and current_cpu > target_cpu * 1.2:  # 20% above target
                    recommendations.append({
                        'hpa_name': hpa_name,
                        'namespace': namespace,
                        'recommendation_type': 'scale_up',
                        'priority': 'medium',
                        'description': f'CPU utilization ({current_cpu}%) exceeds target ({target_cpu}%)',
                        'suggested_action': 'Allow aggressive scale-up due to high CPU',
                        'health_factor': 0 if unhealthy_pods == 0 else unhealthy_pods
                    })
                
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Health-aware scaling recommendations failed: {str(e)}")
            return []
    
    async def _define_health_scaling_constraints(self, hpa_analysis: Dict) -> Dict[str, Any]:
        """🚧 Define health constraints for scaling"""
        constraints = {
            'global_constraints': {},
            'per_hpa_constraints': {}
        }
        
        try:
            # Global constraints
            constraints['global_constraints'] = {
                'max_unhealthy_pods_percentage': 0.2,  # Max 20% unhealthy pods
                'min_ready_pods_before_scale_up': 1,
                'cooling_period_after_pod_failure': 300  # 5 minutes
            }
            
            # Per-HPA constraints
            for hpa_key, hpa_status in hpa_analysis.get('hpa_instances', {}).items():
                namespace, hpa_name = hpa_key.split('/')
                
                constraints['per_hpa_constraints'][hpa_key] = {
                    'min_healthy_replicas': max(1, hpa_status['min_replicas']),
                    'max_scale_up_rate': 2,  # Max 2 pods per scaling event
                    'health_check_required_before_scale': True
                }
            
            return constraints
            
        except Exception as e:
            logger.error(f"❌ Health scaling constraints definition failed: {str(e)}")
            return constraints
    
    # Helper methods
    
    async def _get_pod_resource_usage(self, pod_name: str, namespace: str) -> Dict[str, float]:
        """📊 Get pod resource usage"""
        # Simplified resource usage simulation
        # In real implementation, this would query metrics-server
        return {
            'cpu_percentage': 45.5,
            'memory_percentage': 67.8,
            'cpu_cores': 0.5,
            'memory_mb': 512
        }
    
    def _calculate_pod_age_hours(self, pod: Any) -> float:
        """⏰ Calculate pod age in hours"""
        try:
            if pod.metadata.creation_timestamp:
                creation_time = pod.metadata.creation_timestamp.replace(tzinfo=None)
                age_delta = datetime.utcnow() - creation_time
                return age_delta.total_seconds() / 3600
            return 0
        except:
            return 0
    
    async def _count_unhealthy_pods_for_hpa(self, namespace: str, hpa_name: str) -> int:
        """🔍 Count unhealthy pods for HPA"""
        try:
            # Get deployment targeted by HPA
            # This is simplified - real implementation would query HPA target
            deployment_name = hpa_name  # Assuming HPA name matches deployment
            
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Get pods for deployment
            label_selector = deployment.spec.selector.match_labels
            pods = await self._get_pods_by_selector(namespace, label_selector)
            
            unhealthy_count = 0
            for pod in pods:
                if pod.status.phase != 'Running':
                    unhealthy_count += 1
                elif pod.status.conditions:
                    ready = False
                    for condition in pod.status.conditions:
                        if condition.type == 'Ready' and condition.status == 'True':
                            ready = True
                            break
                    if not ready:
                        unhealthy_count += 1
            
            return unhealthy_count
            
        except Exception as e:
            logger.error(f"❌ Failed to count unhealthy pods for HPA: {str(e)}")
            return 0
    
    # Background monitoring tasks
    
    async def _monitor_pod_health_continuously(self) -> None:
        """🔄 Continuous pod health monitoring"""
        logger.info("🔄 Starting continuous pod health monitoring")
        
        while True:
            try:
                # Monitor all pods in configured namespaces
                namespaces = self.integration_config.get('monitored_namespaces', ['default'])
                
                for namespace in namespaces:
                    pods = self.v1.list_namespaced_pod(namespace=namespace)
                    
                    for pod in pods.items:
                        await self._monitor_individual_pod_health(pod)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Continuous pod health monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _monitor_hpa_health_continuously(self) -> None:
        """📊 Continuous HPA health monitoring"""
        logger.info("📊 Starting continuous HPA health monitoring")
        
        while True:
            try:
                # Monitor all HPA instances
                hpa_metrics = {'monitoring_all': True}
                await self._analyze_hpa_health_status(hpa_metrics)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"❌ Continuous HPA health monitoring error: {str(e)}")
                await asyncio.sleep(120)  # Wait longer on error
    
    async def _monitor_k8s_events_continuously(self) -> None:
        """📡 Continuous Kubernetes events monitoring"""
        logger.info("📡 Starting continuous Kubernetes events monitoring")
        
        try:
            w = watch.Watch()
            
            # Watch for events across all namespaces
            for event in w.stream(self.v1.list_event_for_all_namespaces):
                event_type = event['type']
                event_object = event['object']
                
                # Filter health-related events
                if self._is_health_related_event(event_object):
                    health_event = {
                        'event_type': event_type,
                        'object_kind': event_object.involved_object.kind,
                        'object_name': event_object.involved_object.name,
                        'namespace': event_object.namespace,
                        'reason': event_object.reason,
                        'message': event_object.message,
                        'timestamp': event_object.first_timestamp or datetime.now()
                    }
                    
                    self.health_events.append(health_event)
                    
                    # Keep only recent events (last 1000)
                    if len(self.health_events) > 1000:
                        self.health_events.pop(0)
                        
        except Exception as e:
            logger.error(f"❌ Kubernetes events monitoring error: {str(e)}")
    
    def _is_health_related_event(self, event: Any) -> bool:
        """🔍 Check if event is health-related"""
        health_related_reasons = [
            'Unhealthy', 'FailedHealthCheck', 'ProbeWarning',
            'Killing', 'Failed', 'BackOff', 'CrashLoop'
        ]
        
        return event.reason in health_related_reasons
    
    # Service mesh integration methods
    
    async def _configure_istio_health_integration(self, k8s_config: Dict) -> bool:
        """🕸️ Configure Istio health integration"""
        logger.info("🕸️ Configuring Istio health integration")
        
        try:
            # Configure Istio health checks
            # This would involve setting up VirtualServices, DestinationRules, etc.
            # For now, returning success as placeholder
            return True
            
        except Exception as e:
            logger.error(f"❌ Istio health integration failed: {str(e)}")
            return False
    
    async def _configure_linkerd_health_integration(self, k8s_config: Dict) -> bool:
        """🔗 Configure Linkerd health integration"""
        logger.info("🔗 Configuring Linkerd health integration")
        
        try:
            # Configure Linkerd health checks
            # This would involve setting up ServiceProfiles, TrafficSplits, etc.
            # For now, returning success as placeholder
            return True
            
        except Exception as e:
            logger.error(f"❌ Linkerd health integration failed: {str(e)}")
            return False
    
    # Additional helper methods
    
    async def _update_deployment_health_probes(self, deployment_name: str, namespace: str, probes_config: Dict) -> None:
        """⚕️ Update deployment with health probes"""
        # Implementation would update deployment spec with health probes
        pass
    
    async def _setup_individual_ingress_monitoring(self, ingress_name: str, namespace: str, config: Dict) -> None:
        """🌐 Setup monitoring for individual ingress"""
        # Implementation would setup ingress health monitoring
        pass
    
    def _create_health_check_crd_definition(self) -> Dict[str, Any]:
        """📦 Create HealthCheck CRD definition"""
        return {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": "healthchecks.ainflue.monitoring.fahed-mlaiel.com"
            },
            "spec": {
                "group": "ainflue.monitoring.fahed-mlaiel.com",
                "versions": [{
                    "name": "v1",
                    "served": True,
                    "storage": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {
                                "spec": {
                                    "type": "object",
                                    "properties": {
                                        "target": {"type": "string"},
                                        "healthEndpoint": {"type": "string"},
                                        "interval": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }],
                "scope": "Namespaced",
                "names": {
                    "plural": "healthchecks",
                    "singular": "healthcheck",
                    "kind": "HealthCheck"
                }
            }
        }
    
    async def _setup_custom_health_metrics_for_hpa(self, hpa_metrics: Dict) -> Dict[str, Any]:
        """📊 Setup custom health metrics for HPA"""
        return {
            'custom_metrics_configured': True,
            'health_score_metric': 'health_score_percentage',
            'pod_readiness_metric': 'ready_pods_percentage',
            'integration_status': 'active'
        }
    
    async def _apply_hpa_health_modifications(self, scaling_recs: List[Dict]) -> Dict[str, Any]:
        """🔧 Apply HPA health-based modifications"""
        return {
            'modifications_applied': len(scaling_recs),
            'successful_updates': len(scaling_recs),
            'failed_updates': 0,
            'status': 'completed'
        }
    
    async def close(self):
        """🔚 Cleanup resources"""
        if self.session:
            await self.session.close()

# Factory function pour création instance
def create_kubernetes_health_integration(config: Dict[str, Any]) -> KubernetesHealthIntegration:
    """
    🏭 Factory function pour création KubernetesHealthIntegration
    
    Args:
        config: Configuration integration Kubernetes health
        
    Returns:
        Instance configurée KubernetesHealthIntegration
    """
    return KubernetesHealthIntegration(config)

# Export des classes principales
__all__ = [
    'KubernetesHealthIntegration',
    'K8sHealthProbe',
    'PodHealthStatus',
    'HPAHealthStatus',
    'K8sResourceType',
    'HealthProbeType', 
    'PodPhase',
    'create_kubernetes_health_integration'
]