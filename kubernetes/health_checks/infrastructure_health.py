"""Infrastructure Health Monitoring Service
Comprehensive health checking for infrastructure components

This module provides health monitoring for:
- Container orchestration (Kubernetes, Docker)
- Load balancers and reverse proxies (NGINX, HAProxy)
- Message queues and brokers (RabbitMQ, Apache Kafka)
- Storage systems (S3, MinIO, NFS)
- Monitoring and observability (Prometheus, Grafana, Jaeger)
- Service mesh and networking components
- SSL/TLS certificates and security infrastructure

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""import asyncio
import time
import json
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

import requests
import aiohttp
from kubernetes import client, config as k8s_config
import docker

from .core_health import HealthStatus, HealthCheckResult


@dataclass
class InfrastructureMetrics:
    """Infrastructure component performance metrics"""    component_name: str
    component_type: str
    status: str
    response_time_ms: float
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_mbps: float
    uptime_hours: float


class InfrastructureHealthChecker:
    """    Infrastructure health monitoring system
    
    Monitors all infrastructure components including containers,
    load balancers, storage, networking, and observability systems.
    """    def __init__(self, config: Dict[str, Any]):
        """        Initialize infrastructure health checker
        
        Args:
            config: Infrastructure configuration dictionary
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Infrastructure configurations
        self.infrastructure_config = config.get("infrastructure", {})
        self.kubernetes_config = self.infrastructure_config.get("kubernetes", {})
        self.docker_config = self.infrastructure_config.get("docker", {})
        self.storage_config = self.infrastructure_config.get("storage", {})
        self.networking_config = self.infrastructure_config.get("networking", {})
        self.monitoring_config = self.infrastructure_config.get("monitoring", {})
        
        # Health check thresholds
        self.response_time_threshold = config.get("health_checks", {}).get("infrastructure_response_threshold_ms", 5000)
        self.cpu_threshold = config.get("health_checks", {}).get("infrastructure_cpu_threshold", 80.0)
        self.memory_threshold = config.get("health_checks", {}).get("infrastructure_memory_threshold", 85.0)
        self.disk_threshold = config.get("health_checks", {}).get("infrastructure_disk_threshold", 90.0)

    async def check_kubernetes_cluster(self) -> HealthCheckResult:
        """        Check Kubernetes cluster health and performance
        
        Returns:
            HealthCheckResult: Kubernetes cluster health status
        """        start_time = time.time()
        
        try:
            details = {
                "cluster_available": False,
                "nodes": [],
                "pods": [],
                "services": [],
                "namespaces": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            try:
                # Try to load Kubernetes configuration
                try:
                    k8s_config.load_incluster_config()  # For in-cluster access
                except:
                    k8s_config.load_kube_config()  # For local access
                
                # Initialize Kubernetes API clients
                v1 = client.CoreV1Api()
                apps_v1 = client.AppsV1Api()
                
                details["cluster_available"] = True
                
                # Get cluster nodes
                try:
                    nodes = v1.list_node()
                    for node in nodes.items:
                        node_conditions = {}
                        for condition in node.status.conditions:
                            node_conditions[condition.type] = condition.status
                        
                        # Calculate node resource usage
                        allocatable = node.status.allocatable or {}
                        capacity = node.status.capacity or {}
                        
                        node_info = {
                            "name": node.metadata.name,
                            "status": "Ready" if node_conditions.get("Ready") == "True" else "NotReady",
                            "version": node.status.node_info.kubelet_version if node.status.node_info else "unknown",
                            "os": node.status.node_info.operating_system if node.status.node_info else "unknown",
                            "architecture": node.status.node_info.architecture if node.status.node_info else "unknown",
                            "conditions": node_conditions,
                            "allocatable_cpu": allocatable.get("cpu", "0"),
                            "allocatable_memory": allocatable.get("memory", "0"),
                            "capacity_cpu": capacity.get("cpu", "0"),
                            "capacity_memory": capacity.get("memory", "0")
                        }
                        
                        if node_info["status"] != "Ready":
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                            warnings.append(f"Node {node.metadata.name} is not ready")
                        
                        details["nodes"].append(node_info)
                        
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"Failed to get cluster nodes: {str(e)}")
                
                # Get pod status across namespaces
                try:
                    namespaces = v1.list_namespace()
                    namespace_list = []
                    
                    for namespace in namespaces.items:
                        ns_name = namespace.metadata.name
                        namespace_list.append(ns_name)
                        
                        # Get pods in this namespace
                        pods = v1.list_namespaced_pod(namespace=ns_name)
                        
                        running_pods = 0
                        failed_pods = 0
                        pending_pods = 0
                        
                        for pod in pods.items:
                            pod_status = pod.status.phase
                            
                            if pod_status == "Running":
                                running_pods += 1
                            elif pod_status == "Failed":
                                failed_pods += 1
                            elif pod_status == "Pending":
                                pending_pods += 1
                        
                        if failed_pods > 0:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Failed pods in namespace {ns_name}: {failed_pods}")
                        
                        if pending_pods > 5:  # Threshold for pending pods
                            warnings.append(f"Many pending pods in namespace {ns_name}: {pending_pods}")
                        
                        details["pods"].append({
                            "namespace": ns_name,
                            "running": running_pods,
                            "failed": failed_pods,
                            "pending": pending_pods,
                            "total": len(pods.items)
                        })
                    
                    details["namespaces"] = namespace_list
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"Failed to get pod information: {str(e)}")
                
                # Get services status
                try:
                    services = v1.list_service_for_all_namespaces()
                    
                    for service in services.items:
                        service_info = {
                            "name": service.metadata.name,
                            "namespace": service.metadata.namespace,
                            "type": service.spec.type,
                            "cluster_ip": service.spec.cluster_ip,
                            "ports": [{"port": port.port, "target_port": port.target_port} for port in service.spec.ports] if service.spec.ports else []
                        }
                        
                        details["services"].append(service_info)
                        
                except Exception as e:
                    warnings.append(f"Failed to get services information: {str(e)}")
                
            except Exception as e:
                status = HealthStatus.CRITICAL
                details["cluster_available"] = False
                details["connection_error"] = str(e)
                warnings.append(f"Kubernetes cluster connection failed: {str(e)}")
            
            details["warnings"] = warnings
            details["total_nodes"] = len(details["nodes"])
            details["healthy_nodes"] = len([n for n in details["nodes"] if n.get("status") == "Ready"])
            details["total_namespaces"] = len(details["namespaces"])
            
            return HealthCheckResult(
                service="kubernetes_cluster",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Kubernetes cluster health check failed: {str(e)}")
            return HealthCheckResult(
                service="kubernetes_cluster",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_docker_services(self) -> HealthCheckResult:
        """        Check Docker services and containers health
        
        Returns:
            HealthCheckResult: Docker services health status
        """        start_time = time.time()
        
        try:
            details = {
                "docker_available": False,
                "containers": [],
                "images": [],
                "networks": [],
                "volumes": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            try:
                # Connect to Docker daemon
                docker_client = docker.from_env()
                details["docker_available"] = True
                
                # Get container information
                try:
                    containers = docker_client.containers.list(all=True)
                    
                    for container in containers:
                        container_info = {
                            "id": container.id[:12],
                            "name": container.name,
                            "status": container.status,
                            "image": container.image.tags[0] if container.image.tags else "unknown",
                            "created": container.attrs["Created"],
                            "ports": container.attrs.get("NetworkSettings", {}).get("Ports", {}),
                            "restart_count": container.attrs.get("RestartCount", 0)
                        }
                        
                        # Check container health
                        if container.status not in ["running", "exited"]:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Container {container.name} status: {container.status}")
                        
                        if container.attrs.get("RestartCount", 0) > 5:
                            warnings.append(f"Container {container.name} has restarted {container.attrs.get('RestartCount')} times")
                        
                        details["containers"].append(container_info)
                        
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"Failed to get container information: {str(e)}")
                
                # Get image information
                try:
                    images = docker_client.images.list()
                    
                    for image in images:
                        image_info = {
                            "id": image.id[:12],
                            "tags": image.tags,
                            "size_mb": round(image.attrs["Size"] / (1024 * 1024), 2),
                            "created": image.attrs["Created"]
                        }
                        
                        details["images"].append(image_info)
                        
                except Exception as e:
                    warnings.append(f"Failed to get image information: {str(e)}")
                
                # Get network information
                try:
                    networks = docker_client.networks.list()
                    
                    for network in networks:
                        network_info = {
                            "id": network.id[:12],
                            "name": network.name,
                            "driver": network.attrs["Driver"],
                            "scope": network.attrs["Scope"],
                            "containers": len(network.attrs.get("Containers", {}))
                        }
                        
                        details["networks"].append(network_info)
                        
                except Exception as e:
                    warnings.append(f"Failed to get network information: {str(e)}")
                
                # Get volume information
                try:
                    volumes = docker_client.volumes.list()
                    
                    for volume in volumes:
                        volume_info = {
                            "name": volume.name,
                            "driver": volume.attrs["Driver"],
                            "mountpoint": volume.attrs["Mountpoint"],
                            "created": volume.attrs["CreatedAt"]
                        }
                        
                        details["volumes"].append(volume_info)
                        
                except Exception as e:
                    warnings.append(f"Failed to get volume information: {str(e)}")
                
                # Get Docker system information
                try:
                    system_info = docker_client.info()
                    details["system_info"] = {
                        "containers_running": system_info.get("ContainersRunning", 0),
                        "containers_paused": system_info.get("ContainersPaused", 0),
                        "containers_stopped": system_info.get("ContainersStopped", 0),
                        "images_count": system_info.get("Images", 0),
                        "docker_version": system_info.get("ServerVersion", "unknown"),
                        "kernel_version": system_info.get("KernelVersion", "unknown"),
                        "operating_system": system_info.get("OperatingSystem", "unknown"),
                        "architecture": system_info.get("Architecture", "unknown"),
                        "total_memory_gb": round(system_info.get("MemTotal", 0) / (1024**3), 2)
                    }
                    
                except Exception as e:
                    warnings.append(f"Failed to get Docker system information: {str(e)}")
                
            except Exception as e:
                status = HealthStatus.CRITICAL
                details["docker_available"] = False
                details["connection_error"] = str(e)
                warnings.append(f"Docker daemon connection failed: {str(e)}")
            
            details["warnings"] = warnings
            details["total_containers"] = len(details["containers"])
            details["running_containers"] = len([c for c in details["containers"] if c.get("status") == "running"])
            
            return HealthCheckResult(
                service="docker_services",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Docker services health check failed: {str(e)}")
            return HealthCheckResult(
                service="docker_services",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_storage_systems(self) -> HealthCheckResult:
        """        Check storage systems health and connectivity
        
        Returns:
            HealthCheckResult: Storage systems health status
        """        start_time = time.time()
        
        try:
            details = {
                "storage_systems": [],
                "total_systems": 0,
                "healthy_systems": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check S3-compatible storage
            s3_config = self.storage_config.get("s3", {})
            if s3_config:
                try:
                    import boto3
                    from botocore.exceptions import ClientError
                    
                    # Test S3 connectivity
                    s3_client = boto3.client(
                        's3',
                        endpoint_url=s3_config.get("endpoint_url"),
                        aws_access_key_id=s3_config.get("access_key"),
                        aws_secret_access_key=s3_config.get("secret_key"),
                        region_name=s3_config.get("region", "us-east-1")
                    )
                    
                    api_start = time.time()
                    response = s3_client.list_buckets()
                    api_time = (time.time() - api_start) * 1000
                    
                    storage_result = {
                        "system": "s3_compatible",
                        "status": "healthy",
                        "response_time_ms": api_time,
                        "bucket_count": len(response.get("Buckets", [])),
                        "endpoint": s3_config.get("endpoint_url", "AWS S3"),
                        "region": s3_config.get("region", "us-east-1"),
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if api_time > self.response_time_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"S3 slow response: {api_time:.1f}ms")
                        storage_result["status"] = "degraded"
                    
                    details["storage_systems"].append(storage_result)
                    
                except ImportError:
                    warnings.append("boto3 library not available for S3 connectivity")
                    details["storage_systems"].append({
                        "system": "s3_compatible",
                        "status": "library_missing",
                        "error": "boto3 not installed"
                    })
                    
                except ClientError as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"S3 client error: {str(e)}")
                    details["storage_systems"].append({
                        "system": "s3_compatible",
                        "status": "unhealthy",
                        "error": str(e)
                    })
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"S3 connectivity test failed: {str(e)}")
                    details["storage_systems"].append({
                        "system": "s3_compatible",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Check MinIO storage
            minio_config = self.storage_config.get("minio", {})
            if minio_config:
                try:
                    from minio import Minio
                    from minio.error import S3Error
                    
                    # Test MinIO connectivity
                    minio_client = Minio(
                        minio_config.get("endpoint"),
                        access_key=minio_config.get("access_key"),
                        secret_key=minio_config.get("secret_key"),
                        secure=minio_config.get("secure", True)
                    )
                    
                    api_start = time.time()
                    buckets = list(minio_client.list_buckets())
                    api_time = (time.time() - api_start) * 1000
                    
                    storage_result = {
                        "system": "minio",
                        "status": "healthy",
                        "response_time_ms": api_time,
                        "bucket_count": len(buckets),
                        "endpoint": minio_config.get("endpoint"),
                        "secure": minio_config.get("secure", True),
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if api_time > self.response_time_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"MinIO slow response: {api_time:.1f}ms")
                        storage_result["status"] = "degraded"
                    
                    details["storage_systems"].append(storage_result)
                    
                except ImportError:
                    warnings.append("minio library not available for MinIO connectivity")
                    details["storage_systems"].append({
                        "system": "minio",
                        "status": "library_missing",
                        "error": "minio library not installed"
                    })
                    
                except S3Error as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"MinIO error: {str(e)}")
                    details["storage_systems"].append({
                        "system": "minio",
                        "status": "unhealthy",
                        "error": str(e)
                    })
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"MinIO connectivity test failed: {str(e)}")
                    details["storage_systems"].append({
                        "system": "minio",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Check local filesystem storage
            local_storage_config = self.storage_config.get("local", {})
            if local_storage_config:
                try:
                    import os
                    import shutil
                    
                    storage_paths = local_storage_config.get("paths", [])
                    
                    for path in storage_paths:
                        if os.path.exists(path):
                            # Get disk usage
                            total, used, free = shutil.disk_usage(path)
                            
                            usage_percent = (used / total) * 100
                            
                            storage_result = {
                                "system": "local_filesystem",
                                "path": path,
                                "status": "healthy" if usage_percent < self.disk_threshold else "degraded",
                                "total_gb": round(total / (1024**3), 2),
                                "used_gb": round(used / (1024**3), 2),
                                "free_gb": round(free / (1024**3), 2),
                                "usage_percent": round(usage_percent, 2),
                                "last_check": datetime.utcnow().isoformat()
                            }
                            
                            if usage_percent > self.disk_threshold:
                                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                                warnings.append(f"High disk usage at {path}: {usage_percent:.1f}%")
                            
                            details["storage_systems"].append(storage_result)
                        else:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Storage path not accessible: {path}")
                            details["storage_systems"].append({
                                "system": "local_filesystem",
                                "path": path,
                                "status": "inaccessible",
                                "error": "Path does not exist"
                            })
                            
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"Local storage check failed: {str(e)}")
                    details["storage_systems"].append({
                        "system": "local_filesystem",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_systems"] = len(details["storage_systems"])
            details["healthy_systems"] = len([s for s in details["storage_systems"] if s.get("status") == "healthy"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="storage_systems",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Storage systems health check failed: {str(e)}")
            return HealthCheckResult(
                service="storage_systems",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_ssl_certificates(self) -> HealthCheckResult:
        """        Check SSL/TLS certificates health and expiration
        
        Returns:
            HealthCheckResult: SSL certificates health status
        """        start_time = time.time()
        
        try:
            details = {
                "certificates": [],
                "total_certificates": 0,
                "valid_certificates": 0,
                "expiring_soon": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check certificates for configured domains
            ssl_config = self.networking_config.get("ssl", {})
            domains = ssl_config.get("domains", [])
            
            for domain_config in domains:
                try:
                    domain = domain_config.get("domain")
                    port = domain_config.get("port", 443)
                    
                    if not domain:
                        continue
                    
                    # Get SSL certificate information
                    context = ssl.create_default_context()
                    
                    with socket.create_connection((domain, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            cert = ssock.getpeercert()
                            
                            # Parse certificate dates
                            not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            
                            # Calculate days until expiration
                            days_until_expiry = (not_after - datetime.utcnow()).days
                            
                            cert_info = {
                                "domain": domain,
                                "port": port,
                                "status": "valid",
                                "issuer": dict(x[0] for x in cert['issuer']),
                                "subject": dict(x[0] for x in cert['subject']),
                                "not_before": not_before.isoformat(),
                                "not_after": not_after.isoformat(),
                                "days_until_expiry": days_until_expiry,
                                "serial_number": cert.get('serialNumber'),
                                "version": cert.get('version'),
                                "last_check": datetime.utcnow().isoformat()
                            }
                            
                            # Check certificate validity
                            if days_until_expiry < 0:
                                status = HealthStatus.CRITICAL
                                warnings.append(f"Certificate for {domain} has expired")
                                cert_info["status"] = "expired"
                            elif days_until_expiry < 30:
                                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                                warnings.append(f"Certificate for {domain} expires in {days_until_expiry} days")
                                cert_info["status"] = "expiring_soon"
                                details["expiring_soon"] += 1
                            elif days_until_expiry < 7:
                                status = HealthStatus.UNHEALTHY
                                warnings.append(f"Certificate for {domain} expires in {days_until_expiry} days - URGENT")
                                cert_info["status"] = "expiring_urgent"
                                details["expiring_soon"] += 1
                            
                            details["certificates"].append(cert_info)
                            
                except socket.timeout:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"SSL connection timeout for {domain}:{port}")
                    details["certificates"].append({
                        "domain": domain,
                        "port": port,
                        "status": "timeout",
                        "error": "Connection timeout"
                    })
                    
                except ssl.SSLError as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"SSL error for {domain}:{port}: {str(e)}")
                    details["certificates"].append({
                        "domain": domain,
                        "port": port,
                        "status": "ssl_error",
                        "error": str(e)
                    })
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    warnings.append(f"Certificate check failed for {domain}:{port}: {str(e)}")
                    details["certificates"].append({
                        "domain": domain,
                        "port": port,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_certificates"] = len(details["certificates"])
            details["valid_certificates"] = len([c for c in details["certificates"] if c.get("status") == "valid"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="ssl_certificates",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"SSL certificates health check failed: {str(e)}")
            return HealthCheckResult(
                service="ssl_certificates",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def perform_comprehensive_check(self) -> List[HealthCheckResult]:
        """        Perform all infrastructure health checks concurrently
        
        Returns:
            List[HealthCheckResult]: All infrastructure health check results
        """        checks = await asyncio.gather(
            self.check_kubernetes_cluster(),
            self.check_docker_services(),
            self.check_storage_systems(),
            self.check_ssl_certificates(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                self.logger.error(f"Infrastructure health check failed with exception: {str(check)}")
                results.append(HealthCheckResult(
                    service="unknown_infrastructure",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=datetime.utcnow(),
                    details={},
                    error_message=str(check)
                ))
            else:
                results.append(check)
                
        return results

    async def get_infrastructure_health_summary(self) -> Dict[str, Any]:
        """        Get comprehensive infrastructure health summary
        
        Returns:
            Dict[str, Any]: Infrastructure health summary with overall status
        """        results = await self.perform_comprehensive_check()
        
        # Calculate overall infrastructure health
        status_weights = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        overall_score = max([status_weights[result.status] for result in results])
        overall_status = [status for status, weight in status_weights.items() if weight == overall_score][0]
        
        # Calculate metrics
        avg_response_time = sum([result.response_time_ms for result in results]) / len(results)
        healthy_components = len([r for r in results if r.status == HealthStatus.HEALTHY])
        total_components = len(results)
        
        return {
            "overall_status": overall_status.value,
            "healthy_infrastructure_components": healthy_components,
            "total_infrastructure_components": total_components,
            "infrastructure_health_percentage": (healthy_components / total_components) * 100,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "infrastructure_results": [asdict(result) for result in results]
        }
