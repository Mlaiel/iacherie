"""Resource Scaling Management System

Provides comprehensive auto-scaling capabilities including horizontal pod autoscaling,
vertical pod autoscaling, cluster autoscaling, and custom metrics-based scaling.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""
import asyncio
import logging
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from kubernetes import client, config
import yaml

logger = logging.getLogger(__name__)

class ScalingType(Enum):
    """Types of scaling"""    HORIZONTAL_POD_AUTOSCALER = "hpa"
    VERTICAL_POD_AUTOSCALER = "vpa"
    CLUSTER_AUTOSCALER = "cluster"
    CUSTOM_METRICS = "custom"

class MetricType(Enum):
    """Metric types for scaling"""    CPU_UTILIZATION = "cpu"
    MEMORY_UTILIZATION = "memory"
    CUSTOM_METRIC = "custom"
    EXTERNAL_METRIC = "external"
    RESOURCE_METRIC = "resource"

class ScalingBehavior(Enum):
    """Scaling behavior types"""    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"

@dataclass
class MetricSpec:
    """Metric specification for scaling"""    name: str
    metric_type: MetricType
    target_value: Union[int, str]
    target_type: str = "Utilization"  # Utilization, AverageValue, Value
    resource_name: Optional[str] = None
    selector: Optional[Dict[str, str]] = None

@dataclass
class ScalingPolicy:
    """Scaling policy configuration"""    scaling_type: ScalingBehavior
    period_seconds: int = 60
    value: int = 1
    policy_type: str = "Pods"  # Pods, Percent

@dataclass
class HPASpec:
    """Horizontal Pod Autoscaler specification"""    name: str
    namespace: str
    target_ref: Dict[str, str]
    min_replicas: int = 1
    max_replicas: int = 10
    metrics: List[MetricSpec] = field(default_factory=list)
    behavior: Optional[Dict[str, List[ScalingPolicy]]] = None

@dataclass
class VPASpec:
    """Vertical Pod Autoscaler specification"""    name: str
    namespace: str
    target_ref: Dict[str, str]
    update_mode: str = "Auto"  # Auto, Initial, Off
    resource_policy: Optional[Dict[str, Any]] = None

@dataclass
class ClusterAutoscalerSpec:
    """Cluster Autoscaler specification"""    name: str
    namespace: str = "kube-system"
    min_nodes: int = 1
    max_nodes: int = 100
    scale_down_delay: str = "10m"
    scale_down_unneeded_time: str = "10m"
    node_groups: List[Dict[str, Any]] = field(default_factory=list)

class ResourceScalingManager:
    """Main resource scaling manager"""    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client
        self.apps_v1 = client.AppsV1Api() if k8s_client else None
        self.autoscaling_v2 = client.AutoscalingV2Api() if k8s_client else None
        self.core_v1 = client.CoreV1Api() if k8s_client else None
        self.custom_objects_api = client.CustomObjectsApi() if k8s_client else None
        
    async def create_horizontal_pod_autoscaler(self, hpa_spec: HPASpec) -> Dict[str, Any]:
        """Create Horizontal Pod Autoscaler"""        try:
            # Convert metrics to HPA format
            hpa_metrics = []
            for metric in hpa_spec.metrics:
                if metric.metric_type == MetricType.CPU_UTILIZATION:
                    hpa_metrics.append(client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="cpu",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=int(metric.target_value)
                            )
                        )
                    ))
                elif metric.metric_type == MetricType.MEMORY_UTILIZATION:
                    hpa_metrics.append(client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="memory",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=int(metric.target_value)
                            )
                        )
                    ))
                elif metric.metric_type == MetricType.CUSTOM_METRIC:
                    hpa_metrics.append(client.V2MetricSpec(
                        type="Pods",
                        pods=client.V2PodsMetricSource(
                            metric=client.V2MetricIdentifier(
                                name=metric.name,
                                selector=client.V1LabelSelector(
                                    match_labels=metric.selector
                                ) if metric.selector else None
                            ),
                            target=client.V2MetricTarget(
                                type=metric.target_type,
                                average_value=metric.target_value
                            )
                        )
                    ))
            
            # Build scaling behavior
            behavior = None
            if hpa_spec.behavior:
                scale_up_policies = []
                scale_down_policies = []
                
                for behavior_type, policies in hpa_spec.behavior.items():
                    policy_list = scale_up_policies if behavior_type == "scaleUp" else scale_down_policies
                    for policy in policies:
                        policy_list.append(client.V2HPAScalingPolicy(
                            type=policy.policy_type,
                            value=policy.value,
                            period_seconds=policy.period_seconds
                        ))
                
                behavior = client.V2HorizontalPodAutoscalerBehavior(
                    scale_up=client.V2HPAScalingRules(
                        stabilization_window_seconds=60,
                        policies=scale_up_policies
                    ) if scale_up_policies else None,
                    scale_down=client.V2HPAScalingRules(
                        stabilization_window_seconds=300,
                        policies=scale_down_policies
                    ) if scale_down_policies else None
                )
            
            # Create HPA
            hpa = client.V2HorizontalPodAutoscaler(
                metadata=client.V1ObjectMeta(
                    name=hpa_spec.name,
                    namespace=hpa_spec.namespace
                ),
                spec=client.V2HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V2CrossVersionObjectReference(
                        api_version=hpa_spec.target_ref.get('apiVersion', 'apps/v1'),
                        kind=hpa_spec.target_ref.get('kind', 'Deployment'),
                        name=hpa_spec.target_ref['name']
                    ),
                    min_replicas=hpa_spec.min_replicas,
                    max_replicas=hpa_spec.max_replicas,
                    metrics=hpa_metrics,
                    behavior=behavior
                )
            )
            
            if self.autoscaling_v2:
                result = self.autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
                    namespace=hpa_spec.namespace,
                    body=hpa
                )
                
                logger.info(f"Created HPA: {hpa_spec.name}")
                return {
                    'status': 'success',
                    'name': hpa_spec.name,
                    'min_replicas': hpa_spec.min_replicas,
                    'max_replicas': hpa_spec.max_replicas,
                    'metrics_count': len(hpa_metrics)
                }
            else:
                logger.info(f"HPA configuration prepared: {hpa_spec.name}")
                return {
                    'status': 'success',
                    'name': hpa_spec.name,
                    'configured': True
                }
                
        except Exception as e:
            logger.error(f"Failed to create HPA: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_vertical_pod_autoscaler(self, vpa_spec: VPASpec) -> Dict[str, Any]:
        """Create Vertical Pod Autoscaler"""        try:
            # VPA resource definition
            vpa_resource = {
                'apiVersion': 'autoscaling.k8s.io/v1',
                'kind': 'VerticalPodAutoscaler',
                'metadata': {
                    'name': vpa_spec.name,
                    'namespace': vpa_spec.namespace
                },
                'spec': {
                    'targetRef': {
                        'apiVersion': vpa_spec.target_ref.get('apiVersion', 'apps/v1'),
                        'kind': vpa_spec.target_ref.get('kind', 'Deployment'),
                        'name': vpa_spec.target_ref['name']
                    },
                    'updatePolicy': {
                        'updateMode': vpa_spec.update_mode
                    }
                }
            }
            
            # Add resource policy if specified
            if vpa_spec.resource_policy:
                vpa_resource['spec']['resourcePolicy'] = vpa_spec.resource_policy
            
            if self.custom_objects_api:
                result = self.custom_objects_api.create_namespaced_custom_object(
                    group='autoscaling.k8s.io',
                    version='v1',
                    namespace=vpa_spec.namespace,
                    plural='verticalpodautoscalers',
                    body=vpa_resource
                )
                
                logger.info(f"Created VPA: {vpa_spec.name}")
                return {
                    'status': 'success',
                    'name': vpa_spec.name,
                    'update_mode': vpa_spec.update_mode
                }
            else:
                logger.info(f"VPA configuration prepared: {vpa_spec.name}")
                return {
                    'status': 'success',
                    'name': vpa_spec.name,
                    'configured': True
                }
                
        except Exception as e:
            logger.error(f"Failed to create VPA: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_cluster_autoscaler(self, ca_spec: ClusterAutoscalerSpec) -> Dict[str, Any]:
        """Create Cluster Autoscaler"""        try:
            # Cluster Autoscaler deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=ca_spec.name,
                    namespace=ca_spec.namespace,
                    labels={'app': 'cluster-autoscaler'}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={'app': 'cluster-autoscaler'}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={'app': 'cluster-autoscaler'}
                        ),
                        spec=client.V1PodSpec(
                            service_account='cluster-autoscaler',
                            containers=[
                                client.V1Container(
                                    name='cluster-autoscaler',
                                    image='k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0',
                                    command=[
                                        './cluster-autoscaler',
                                        '--v=4',
                                        '--stderrthreshold=info',
                                        '--cloud-provider=aws',  # Change based on provider
                                        '--skip-nodes-with-local-storage=false',
                                        '--expander=least-waste',
                                        f'--scale-down-delay-after-add={ca_spec.scale_down_delay}',
                                        f'--scale-down-unneeded-time={ca_spec.scale_down_unneeded_time}'
                                    ] + [
                                        f"--nodes={node_group['min']}:{node_group['max']}:{node_group['name']}"
                                        for node_group in ca_spec.node_groups
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        requests={'cpu': '100m', 'memory': '300Mi'},
                                        limits={'cpu': '100m', 'memory': '300Mi'}
                                    ),
                                    env=[
                                        client.V1EnvVar(
                                            name='AWS_REGION',
                                            value='us-east-1'  # Configure based on region
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            
            # Create RBAC for Cluster Autoscaler
            await self._create_cluster_autoscaler_rbac(ca_spec.namespace)
            
            if self.apps_v1:
                self.apps_v1.create_namespaced_deployment(
                    namespace=ca_spec.namespace,
                    body=deployment
                )
                
                logger.info(f"Created Cluster Autoscaler: {ca_spec.name}")
                return {
                    'status': 'success',
                    'name': ca_spec.name,
                    'min_nodes': ca_spec.min_nodes,
                    'max_nodes': ca_spec.max_nodes,
                    'node_groups': len(ca_spec.node_groups)
                }
            else:
                logger.info(f"Cluster Autoscaler configuration prepared: {ca_spec.name}")
                return {
                    'status': 'success',
                    'name': ca_spec.name,
                    'configured': True
                }
                
        except Exception as e:
            logger.error(f"Failed to create Cluster Autoscaler: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_cluster_autoscaler_rbac(self, namespace: str) -> Dict[str, Any]:
        """Create RBAC for Cluster Autoscaler"""        try:
            # Service Account
            service_account = client.V1ServiceAccount(
                metadata=client.V1ObjectMeta(
                    name="cluster-autoscaler",
                    namespace=namespace
                )
            )
            
            # ClusterRole
            cluster_role = client.V1ClusterRole(
                metadata=client.V1ObjectMeta(name="cluster-autoscaler"),
                rules=[
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["events", "endpoints"],
                        verbs=["create", "patch"]
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["pods/eviction"],
                        verbs=["create"]
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["pods/status"],
                        verbs=["update"]
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["endpoints"],
                        resource_names=["cluster-autoscaler"],
                        verbs=["get", "update"]
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["nodes"],
                        verbs=["watch", "list", "get", "update"]
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["pods", "services", "replicationcontrollers", "persistentvolumeclaims", "persistentvolumes"],
                        verbs=["watch", "list", "get"]
                    ),
                    client.V1PolicyRule(
                        api_groups=["extensions"],
                        resources=["replicasets", "daemonsets"],
                        verbs=["watch", "list", "get"]
                    ),
                    client.V1PolicyRule(
                        api_groups=["policy"],
                        resources=["poddisruptionbudgets"],
                        verbs=["watch", "list"]
                    ),
                    client.V1PolicyRule(
                        api_groups=["apps"],
                        resources=["statefulsets", "replicasets", "daemonsets"],
                        verbs=["watch", "list", "get"]
                    ),
                    client.V1PolicyRule(
                        api_groups=["storage.k8s.io"],
                        resources=["storageclasses", "csinodes"],
                        verbs=["watch", "list", "get"]
                    ),
                    client.V1PolicyRule(
                        api_groups=["batch", "extensions"],
                        resources=["jobs"],
                        verbs=["get", "list", "watch", "patch"]
                    )
                ]
            )
            
            # ClusterRoleBinding
            cluster_role_binding = client.V1ClusterRoleBinding(
                metadata=client.V1ObjectMeta(name="cluster-autoscaler"),
                subjects=[client.V1Subject(
                    kind="ServiceAccount",
                    name="cluster-autoscaler",
                    namespace=namespace
                )],
                role_ref=client.V1RoleRef(
                    kind="ClusterRole",
                    name="cluster-autoscaler",
                    api_group="rbac.authorization.k8s.io"
                )
            )
            
            if self.core_v1:
                self.core_v1.create_namespaced_service_account(
                    namespace=namespace, body=service_account
                )
                
            if hasattr(self, 'rbac_v1'):
                self.rbac_v1.create_cluster_role(body=cluster_role)
                self.rbac_v1.create_cluster_role_binding(body=cluster_role_binding)
            
            return {'status': 'success', 'rbac': 'created'}
            
        except Exception as e:
            logger.error(f"Failed to create Cluster Autoscaler RBAC: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_ia_influencer_autoscaling(self, namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Create comprehensive autoscaling for IA Influencer platform"""        try:
            results = {}
            
            # API Server HPA
            api_hpa = HPASpec(
                name="ia-influencer-api-hpa",
                namespace=namespace,
                target_ref={
                    'kind': 'Deployment',
                    'name': 'ia-influencer-api'
                },
                min_replicas=2,
                max_replicas=20,
                metrics=[
                    MetricSpec(
                        name="cpu",
                        metric_type=MetricType.CPU_UTILIZATION,
                        target_value="70"
                    ),
                    MetricSpec(
                        name="memory",
                        metric_type=MetricType.MEMORY_UTILIZATION,
                        target_value="80"
                    ),
                    MetricSpec(
                        name="http_requests_per_second",
                        metric_type=MetricType.CUSTOM_METRIC,
                        target_value="1000",
                        target_type="AverageValue",
                        selector={'app': 'ia-influencer-api'}
                    )
                ],
                behavior={
                    'scaleUp': [
                        ScalingPolicy(
                            scaling_type=ScalingBehavior.SCALE_UP,
                            period_seconds=60,
                            value=2,
                            policy_type="Pods"
                        )
                    ],
                    'scaleDown': [
                        ScalingPolicy(
                            scaling_type=ScalingBehavior.SCALE_DOWN,
                            period_seconds=300,
                            value=1,
                            policy_type="Pods"
                        )
                    ]
                }
            )
            
            api_hpa_result = await self.create_horizontal_pod_autoscaler(api_hpa)
            results['api_hpa'] = api_hpa_result
            
            # AI Processing HPA (more aggressive scaling)
            ai_hpa = HPASpec(
                name="ia-influencer-ai-hpa",
                namespace=namespace,
                target_ref={
                    'kind': 'Deployment',
                    'name': 'ia-influencer-ai'
                },
                min_replicas=1,
                max_replicas=15,
                metrics=[
                    MetricSpec(
                        name="cpu",
                        metric_type=MetricType.CPU_UTILIZATION,
                        target_value="60"  # Lower threshold for AI workloads
                    ),
                    MetricSpec(
                        name="memory",
                        metric_type=MetricType.MEMORY_UTILIZATION,
                        target_value="70"
                    ),
                    MetricSpec(
                        name="ai_processing_queue_size",
                        metric_type=MetricType.CUSTOM_METRIC,
                        target_value="10",
                        target_type="AverageValue",
                        selector={'app': 'ia-influencer-ai'}
                    )
                ]
            )
            
            ai_hpa_result = await self.create_horizontal_pod_autoscaler(ai_hpa)
            results['ai_hpa'] = ai_hpa_result
            
            # Content Protection HPA
            protection_hpa = HPASpec(
                name="ia-influencer-protection-hpa",
                namespace=namespace,
                target_ref={
                    'kind': 'Deployment',
                    'name': 'ia-influencer-protection'
                },
                min_replicas=1,
                max_replicas=10,
                metrics=[
                    MetricSpec(
                        name="cpu",
                        metric_type=MetricType.CPU_UTILIZATION,
                        target_value="75"
                    ),
                    MetricSpec(
                        name="fingerprint_generation_rate",
                        metric_type=MetricType.CUSTOM_METRIC,
                        target_value="50",
                        target_type="AverageValue",
                        selector={'app': 'ia-influencer-protection'}
                    )
                ]
            )
            
            protection_hpa_result = await self.create_horizontal_pod_autoscaler(protection_hpa)
            results['protection_hpa'] = protection_hpa_result
            
            # Database VPA (PostgreSQL)
            db_vpa = VPASpec(
                name="postgresql-vpa",
                namespace=namespace,
                target_ref={
                    'kind': 'StatefulSet',
                    'name': 'postgresql'
                },
                update_mode="Auto",
                resource_policy={
                    'containerPolicies': [{
                        'containerName': 'postgresql',
                        'minAllowed': {
                            'memory': '1Gi',
                            'cpu': '500m'
                        },
                        'maxAllowed': {
                            'memory': '8Gi',
                            'cpu': '4000m'
                        }
                    }]
                }
            )
            
            db_vpa_result = await self.create_vertical_pod_autoscaler(db_vpa)
            results['database_vpa'] = db_vpa_result
            
            # Redis VPA
            redis_vpa = VPASpec(
                name="redis-vpa",
                namespace=namespace,
                target_ref={
                    'kind': 'Deployment',
                    'name': 'redis'
                },
                update_mode="Auto",
                resource_policy={
                    'containerPolicies': [{
                        'containerName': 'redis',
                        'minAllowed': {
                            'memory': '256Mi',
                            'cpu': '100m'
                        },
                        'maxAllowed': {
                            'memory': '4Gi',
                            'cpu': '2000m'
                        }
                    }]
                }
            )
            
            redis_vpa_result = await self.create_vertical_pod_autoscaler(redis_vpa)
            results['redis_vpa'] = redis_vpa_result
            
            # Cluster Autoscaler
            cluster_autoscaler = ClusterAutoscalerSpec(
                name="ia-influencer-cluster-autoscaler",
                namespace="kube-system",
                min_nodes=3,
                max_nodes=50,
                scale_down_delay="10m",
                scale_down_unneeded_time="10m",
                node_groups=[
                    {
                        'name': 'ia-influencer-worker-nodes',
                        'min': 3,
                        'max': 30,
                        'instance_type': 't3.large'
                    },
                    {
                        'name': 'ia-influencer-ai-nodes',
                        'min': 1,
                        'max': 10,
                        'instance_type': 'c5.2xlarge'  # CPU optimized for AI
                    },
                    {
                        'name': 'ia-influencer-gpu-nodes',
                        'min': 0,
                        'max': 5,
                        'instance_type': 'p3.2xlarge'  # GPU instances for ML
                    }
                ]
            )
            
            cluster_autoscaler_result = await self.create_cluster_autoscaler(cluster_autoscaler)
            results['cluster_autoscaler'] = cluster_autoscaler_result
            
            logger.info("Created comprehensive IA Influencer autoscaling")
            return {
                'status': 'success',
                'autoscaling_components': results
            }
            
        except Exception as e:
            logger.error(f"Failed to create IA Influencer autoscaling: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_scaling_status(self, namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Get comprehensive scaling status"""        try:
            status = {}
            
            if self.autoscaling_v2:
                # Get HPA status
                hpas = self.autoscaling_v2.list_namespaced_horizontal_pod_autoscaler(
                    namespace=namespace
                )
                
                hpa_status = []
                for hpa in hpas.items:
                    hpa_status.append({
                        'name': hpa.metadata.name,
                        'min_replicas': hpa.spec.min_replicas,
                        'max_replicas': hpa.spec.max_replicas,
                        'current_replicas': hpa.status.current_replicas,
                        'desired_replicas': hpa.status.desired_replicas,
                        'current_cpu_utilization': hpa.status.current_metrics[0].resource.current.average_utilization if hpa.status.current_metrics else None
                    })
                
                status['hpa'] = hpa_status
            
            # Get deployment replica counts
            if self.apps_v1:
                deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
                
                deployment_status = []
                for deployment in deployments.items:
                    deployment_status.append({
                        'name': deployment.metadata.name,
                        'desired_replicas': deployment.spec.replicas,
                        'ready_replicas': deployment.status.ready_replicas or 0,
                        'available_replicas': deployment.status.available_replicas or 0
                    })
                
                status['deployments'] = deployment_status
            
            return {
                'status': 'success',
                'scaling_status': status
            }
            
        except Exception as e:
            logger.error(f"Failed to get scaling status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_scaling_policy(self, name: str, namespace: str, new_spec: HPASpec) -> Dict[str, Any]:
        """Update existing HPA scaling policy"""        try:
            if self.autoscaling_v2:
                # Delete existing HPA
                self.autoscaling_v2.delete_namespaced_horizontal_pod_autoscaler(
                    name=name,
                    namespace=namespace
                )
                
                # Create new HPA with updated spec
                result = await self.create_horizontal_pod_autoscaler(new_spec)
                
                logger.info(f"Updated HPA scaling policy: {name}")
                return result
            else:
                logger.info(f"HPA scaling policy update prepared: {name}")
                return {'status': 'success', 'name': name, 'updated': True}
                
        except Exception as e:
            logger.error(f"Failed to update scaling policy: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def scale_deployment_manually(self, deployment_name: str, namespace: str, replicas: int) -> Dict[str, Any]:
        """Manually scale a deployment"""        try:
            if self.apps_v1:
                # Patch deployment with new replica count
                self.apps_v1.patch_namespaced_deployment_scale(
                    name=deployment_name,
                    namespace=namespace,
                    body={'spec': {'replicas': replicas}}
                )
                
                logger.info(f"Manually scaled deployment {deployment_name} to {replicas} replicas")
                return {
                    'status': 'success',
                    'deployment': deployment_name,
                    'replicas': replicas
                }
            else:
                logger.info(f"Manual scaling prepared for {deployment_name}: {replicas} replicas")
                return {
                    'status': 'success',
                    'deployment': deployment_name,
                    'replicas': replicas,
                    'configured': True
                }
                
        except Exception as e:
            logger.error(f"Failed to manually scale deployment: {e}")
            return {'status': 'error', 'message': str(e)}
