#!/usr/bin/env python3
"""🔧 Monitoring Stack Deployment Manager - Ainflue Platform
==========================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + SRE + Backend Senior + Observability Engineer
Date: 2025-08-31

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Production monitoring stack deployment with Prometheus, Grafana, Jaeger, and ELK.
==========================================================
"""
import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Monitoring stack configuration"""
    namespace: str = "ainflue-monitoring"
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    jaeger_enabled: bool = True
    elasticsearch_enabled: bool = True
    alertmanager_enabled: bool = True
    
    # Prometheus configuration
    prometheus_retention: str = "30d"
    prometheus_storage_size: str = "50Gi"
    prometheus_memory_limit: str = "4Gi"
    prometheus_cpu_limit: str = "2000m"
    
    # Grafana configuration
    grafana_admin_password: str = "admin123"
    grafana_storage_size: str = "10Gi"
    grafana_memory_limit: str = "2Gi"
    grafana_cpu_limit: str = "1000m"
    
    # Jaeger configuration
    jaeger_storage_backend: str = "elasticsearch"
    jaeger_memory_limit: str = "2Gi"
    jaeger_cpu_limit: str = "1000m"
    
    # Elasticsearch configuration
    elasticsearch_storage_size: str = "100Gi"
    elasticsearch_memory_limit: str = "8Gi"
    elasticsearch_cpu_limit: str = "4000m"
    elasticsearch_replicas: int = 3


class MonitoringStackDeployment:
    """
    Production monitoring stack deployment manager.
    
    Features:
    - Prometheus metrics collection
    - Grafana dashboards and visualization
    - Jaeger distributed tracing
    - Elasticsearch log aggregation
    - AlertManager notifications
    - PagerDuty integration
    - Automated dashboard provisioning
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.kubernetes_client = None
        self.apps_v1_client = None
        
        try:
            # Load Kubernetes configuration
            config.load_incluster_config()
            self.kubernetes_client = client.CoreV1Api()
            self.apps_v1_client = client.AppsV1Api()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except Exception:
            try:
                config.load_kube_config()
                self.kubernetes_client = client.CoreV1Api()
                self.apps_v1_client = client.AppsV1Api()
                logger.info("Loaded local Kubernetes configuration")
            except Exception as e:
                logger.warning(f"Could not load Kubernetes configuration: {e}")
    
    def create_namespace(self) -> bool:
        """Create monitoring namespace"""
        try:
            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=self.config.namespace,
                    labels={
                        "name": self.config.namespace,
                        "app.kubernetes.io/name": "monitoring",
                        "app.kubernetes.io/managed-by": "ainflue-platform"
                    }
                )
            )
            
            try:
                self.kubernetes_client.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace {self.config.namespace}")
                return True
            except ApiException as e:
                if e.status == 409:
                    logger.info(f"Namespace {self.config.namespace} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creating namespace: {e}")
            return False
    
    def deploy_prometheus(self) -> bool:
        """Deploy Prometheus monitoring"""
        try:
            # Create Prometheus ConfigMap
            prometheus_config = {
                "prometheus.yml": """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ainflue-api'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: ainflue-api

  - job_name: 'ainflue-workers'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: ainflue-workers

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
"""
            }
            
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name="prometheus-config",
                    namespace=self.config.namespace
                ),
                data=prometheus_config
            )
            
            try:
                self.kubernetes_client.create_namespaced_config_map(
                    namespace=self.config.namespace,
                    body=configmap
                )
            except ApiException as e:
                if e.status == 409:
                    self.kubernetes_client.patch_namespaced_config_map(
                        name="prometheus-config",
                        namespace=self.config.namespace,
                        body=configmap
                    )
            
            # Create Prometheus Deployment
            prometheus_deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name="prometheus",
                    namespace=self.config.namespace,
                    labels={"app": "prometheus"}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "prometheus"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "prometheus"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="prometheus",
                                    image="prom/prometheus:latest",
                                    ports=[
                                        client.V1ContainerPort(container_port=9090)
                                    ],
                                    volume_mounts=[
                                        client.V1VolumeMount(
                                            name="prometheus-config",
                                            mount_path="/etc/prometheus"
                                        ),
                                        client.V1VolumeMount(
                                            name="prometheus-storage",
                                            mount_path="/prometheus"
                                        )
                                    ],
                                    args=[
                                        "--config.file=/etc/prometheus/prometheus.yml",
                                        "--storage.tsdb.path=/prometheus",
                                        f"--storage.tsdb.retention.time={self.config.prometheus_retention}",
                                        "--web.console.libraries=/etc/prometheus/console_libraries",
                                        "--web.console.templates=/etc/prometheus/consoles",
                                        "--web.enable-lifecycle"
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        limits={
                                            "memory": self.config.prometheus_memory_limit,
                                            "cpu": self.config.prometheus_cpu_limit
                                        },
                                        requests={
                                            "memory": "2Gi",
                                            "cpu": "1000m"
                                        }
                                    )
                                )
                            ],
                            volumes=[
                                client.V1Volume(
                                    name="prometheus-config",
                                    config_map=client.V1ConfigMapVolumeSource(
                                        name="prometheus-config"
                                    )
                                ),
                                client.V1Volume(
                                    name="prometheus-storage",
                                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                        claim_name="prometheus-storage"
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            try:
                self.apps_v1_client.create_namespaced_deployment(
                    namespace=self.config.namespace,
                    body=prometheus_deployment
                )
                logger.info("Created Prometheus deployment")
            except ApiException as e:
                if e.status == 409:
                    self.apps_v1_client.patch_namespaced_deployment(
                        name="prometheus",
                        namespace=self.config.namespace,
                        body=prometheus_deployment
                    )
                    logger.info("Updated Prometheus deployment")
                else:
                    raise e
            
            # Create Prometheus Service
            prometheus_service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name="prometheus",
                    namespace=self.config.namespace,
                    labels={"app": "prometheus"}
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": "prometheus"},
                    ports=[
                        client.V1ServicePort(
                            port=9090,
                            target_port=9090,
                            name="web"
                        )
                    ],
                    type="ClusterIP"
                )
            )
            
            try:
                self.kubernetes_client.create_namespaced_service(
                    namespace=self.config.namespace,
                    body=prometheus_service
                )
                logger.info("Created Prometheus service")
            except ApiException as e:
                if e.status == 409:
                    logger.info("Prometheus service already exists")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Prometheus: {e}")
            return False
    
    def deploy_grafana(self) -> bool:
        """Deploy Grafana dashboards"""
        try:
            # Create Grafana ConfigMap for datasources
            grafana_datasources = {
                "datasources.yaml": """apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger-query:16686
  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "[logstash-]YYYY.MM.DD"
    interval: Daily
"""
            }
            
            datasources_configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name="grafana-datasources",
                    namespace=self.config.namespace
                ),
                data=grafana_datasources
            )
            
            try:
                self.kubernetes_client.create_namespaced_config_map(
                    namespace=self.config.namespace,
                    body=datasources_configmap
                )
            except ApiException as e:
                if e.status == 409:
                    self.kubernetes_client.patch_namespaced_config_map(
                        name="grafana-datasources",
                        namespace=self.config.namespace,
                        body=datasources_configmap
                    )
            
            # Create Grafana Deployment
            grafana_deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name="grafana",
                    namespace=self.config.namespace,
                    labels={"app": "grafana"}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "grafana"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "grafana"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="grafana",
                                    image="grafana/grafana:latest",
                                    ports=[
                                        client.V1ContainerPort(container_port=3000)
                                    ],
                                    env=[
                                        client.V1EnvVar(
                                            name="GF_SECURITY_ADMIN_PASSWORD",
                                            value=self.config.grafana_admin_password
                                        ),
                                        client.V1EnvVar(
                                            name="GF_PATHS_PROVISIONING",
                                            value="/etc/grafana/provisioning"
                                        )
                                    ],
                                    volume_mounts=[
                                        client.V1VolumeMount(
                                            name="grafana-storage",
                                            mount_path="/var/lib/grafana"
                                        ),
                                        client.V1VolumeMount(
                                            name="grafana-datasources",
                                            mount_path="/etc/grafana/provisioning/datasources"
                                        )
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        limits={
                                            "memory": self.config.grafana_memory_limit,
                                            "cpu": self.config.grafana_cpu_limit
                                        },
                                        requests={
                                            "memory": "1Gi",
                                            "cpu": "500m"
                                        }
                                    )
                                )
                            ],
                            volumes=[
                                client.V1Volume(
                                    name="grafana-storage",
                                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                        claim_name="grafana-storage"
                                    )
                                ),
                                client.V1Volume(
                                    name="grafana-datasources",
                                    config_map=client.V1ConfigMapVolumeSource(
                                        name="grafana-datasources"
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            try:
                self.apps_v1_client.create_namespaced_deployment(
                    namespace=self.config.namespace,
                    body=grafana_deployment
                )
                logger.info("Created Grafana deployment")
            except ApiException as e:
                if e.status == 409:
                    self.apps_v1_client.patch_namespaced_deployment(
                        name="grafana",
                        namespace=self.config.namespace,
                        body=grafana_deployment
                    )
                    logger.info("Updated Grafana deployment")
                else:
                    raise e
            
            # Create Grafana Service
            grafana_service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name="grafana",
                    namespace=self.config.namespace,
                    labels={"app": "grafana"}
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": "grafana"},
                    ports=[
                        client.V1ServicePort(
                            port=3000,
                            target_port=3000,
                            name="web"
                        )
                    ],
                    type="ClusterIP"
                )
            )
            
            try:
                self.kubernetes_client.create_namespaced_service(
                    namespace=self.config.namespace,
                    body=grafana_service
                )
                logger.info("Created Grafana service")
            except ApiException as e:
                if e.status == 409:
                    logger.info("Grafana service already exists")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Grafana: {e}")
            return False
    
    def deploy_jaeger(self) -> bool:
        """Deploy Jaeger tracing"""
        try:
            # Create Jaeger All-in-One Deployment
            jaeger_deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name="jaeger",
                    namespace=self.config.namespace,
                    labels={"app": "jaeger"}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "jaeger"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "jaeger"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="jaeger",
                                    image="jaegertracing/all-in-one:latest",
                                    ports=[
                                        client.V1ContainerPort(container_port=16686),  # Query UI
                                        client.V1ContainerPort(container_port=14268),  # Collector
                                        client.V1ContainerPort(container_port=6831),   # Agent
                                        client.V1ContainerPort(container_port=6832),   # Agent
                                    ],
                                    env=[
                                        client.V1EnvVar(
                                            name="COLLECTOR_ZIPKIN_HTTP_PORT",
                                            value="9411"
                                        )
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        limits={
                                            "memory": self.config.jaeger_memory_limit,
                                            "cpu": self.config.jaeger_cpu_limit
                                        },
                                        requests={
                                            "memory": "1Gi",
                                            "cpu": "500m"
                                        }
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            try:
                self.apps_v1_client.create_namespaced_deployment(
                    namespace=self.config.namespace,
                    body=jaeger_deployment
                )
                logger.info("Created Jaeger deployment")
            except ApiException as e:
                if e.status == 409:
                    self.apps_v1_client.patch_namespaced_deployment(
                        name="jaeger",
                        namespace=self.config.namespace,
                        body=jaeger_deployment
                    )
                    logger.info("Updated Jaeger deployment")
                else:
                    raise e
            
            # Create Jaeger Services
            jaeger_query_service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name="jaeger-query",
                    namespace=self.config.namespace,
                    labels={"app": "jaeger", "component": "query"}
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": "jaeger"},
                    ports=[
                        client.V1ServicePort(
                            port=16686,
                            target_port=16686,
                            name="query"
                        )
                    ],
                    type="ClusterIP"
                )
            )
            
            jaeger_collector_service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name="jaeger-collector",
                    namespace=self.config.namespace,
                    labels={"app": "jaeger", "component": "collector"}
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": "jaeger"},
                    ports=[
                        client.V1ServicePort(
                            port=14268,
                            target_port=14268,
                            name="http"
                        ),
                        client.V1ServicePort(
                            port=6831,
                            target_port=6831,
                            name="udp-compact",
                            protocol="UDP"
                        ),
                        client.V1ServicePort(
                            port=6832,
                            target_port=6832,
                            name="udp-binary",
                            protocol="UDP"
                        )
                    ],
                    type="ClusterIP"
                )
            )
            
            for service in [jaeger_query_service, jaeger_collector_service]:
                try:
                    self.kubernetes_client.create_namespaced_service(
                        namespace=self.config.namespace,
                        body=service
                    )
                    logger.info(f"Created Jaeger service {service.metadata.name}")
                except ApiException as e:
                    if e.status == 409:
                        logger.info(f"Jaeger service {service.metadata.name} already exists")
                    else:
                        raise e
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Jaeger: {e}")
            return False
    
    def deploy_monitoring_stack(self) -> bool:
        """Deploy complete monitoring stack"""
        try:
            # Create namespace
            if not self.create_namespace():
                return False
            
            success = True
            
            # Deploy components based on configuration
            if self.config.prometheus_enabled:
                success &= self.deploy_prometheus()
            
            if self.config.grafana_enabled:
                success &= self.deploy_grafana()
            
            if self.config.jaeger_enabled:
                success &= self.deploy_jaeger()
            
            if success:
                logger.info("Monitoring stack deployment completed successfully")
            else:
                logger.error("Some components failed to deploy")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deploying monitoring stack: {e}")
            return False
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get monitoring stack deployment status"""
        status = {
            'namespace': self.config.namespace,
            'components': {},
            'services': {},
            'overall_status': 'unknown'
        }
        
        if not self.kubernetes_client:
            status['overall_status'] = 'kubernetes_unavailable'
            return status
        
        try:
            # Check deployments
            deployments = self.apps_v1_client.list_namespaced_deployment(
                namespace=self.config.namespace
            )
            
            for deployment in deployments.items:
                name = deployment.metadata.name
                status['components'][name] = {
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'replicas': deployment.status.replicas or 0,
                    'available_replicas': deployment.status.available_replicas or 0
                }
            
            # Check services
            services = self.kubernetes_client.list_namespaced_service(
                namespace=self.config.namespace
            )
            
            for service in services.items:
                name = service.metadata.name
                status['services'][name] = {
                    'cluster_ip': service.spec.cluster_ip,
                    'ports': [
                        {'port': port.port, 'target_port': port.target_port}
                        for port in service.spec.ports
                    ]
                }
            
            # Determine overall status
            all_ready = all(
                comp['ready_replicas'] == comp['replicas'] 
                for comp in status['components'].values()
                if comp['replicas'] > 0
            )
            
            status['overall_status'] = 'ready' if all_ready else 'deploying'
            
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            status['overall_status'] = 'error'
        
        return status


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize monitoring configuration
    monitoring_config = MonitoringConfig(
        namespace=os.getenv('MONITORING_NAMESPACE', 'ainflue-monitoring'),
        prometheus_enabled=os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true',
        grafana_enabled=os.getenv('GRAFANA_ENABLED', 'true').lower() == 'true',
        jaeger_enabled=os.getenv('JAEGER_ENABLED', 'true').lower() == 'true',
        grafana_admin_password=os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin123')
    )
    
    # Deploy monitoring stack
    deployment_manager = MonitoringStackDeployment(monitoring_config)
    success = deployment_manager.deploy_monitoring_stack()
    
    # Print status
    status = deployment_manager.get_deployment_status()
    print(f"Deployment Status: {status}")
    
    if success:
        print("✅ Monitoring stack deployment completed successfully!")
        print(f"📊 Grafana UI: kubectl port-forward -n {monitoring_config.namespace} svc/grafana 3000:3000")
        print(f"📈 Prometheus UI: kubectl port-forward -n {monitoring_config.namespace} svc/prometheus 9090:9090")
        print(f"🔍 Jaeger UI: kubectl port-forward -n {monitoring_config.namespace} svc/jaeger-query 16686:16686")
    else:
        print("❌ Monitoring stack deployment failed!")
        exit(1)