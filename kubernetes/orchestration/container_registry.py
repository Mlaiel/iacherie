"""IA Influencer Agent - Container Registry Management
Enterprise container image management and security scanning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Multi-cloud container registry management
- Image security scanning and vulnerability detection
- Image lifecycle management and cleanup
- Registry mirroring and replication
- Access control and authentication
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import base64

import docker
import prometheus_client
from kubernetes import client

# Note: Import paths adjusted for actual deployment structure
from .base_manager import BaseDeploymentManager

# Mock classes for standalone operation
class VulnerabilityScanner:
    """
Mock vulnerability scanner."""
    def __init__(self) -> None:
        """
Initialize vulnerability scanner with security databases"""
        self.logger = logging.getLogger(f"{__name__}.VulnerabilityScanner")
        self.vulnerability_databases = ['CVE', 'NVD', 'OSV', 'GitHub_Advisory']
        self.scan_engines = ['trivy', 'clair', 'snyk', 'aqua']
        self.severity_levels = ['low', 'medium', 'high', 'critical']
        self.scan_timeout = 300  # 5 minutes
        self.last_db_update = None
        self.logger.info("VulnerabilityScanner initialized with security databases")
    
    async def scan_image(self, image_id -> None: str, name -> None: str, tag -> None: str) -> None:
        """Mock scan returning empty vulnerabilities."""
        return []

class MetricsCollector:
    """
Mock metrics collector."""
    def __init__(self) -> None:
        """
Initialize metrics collector with monitoring endpoints"""
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.metrics_endpoints = ['prometheus', 'grafana', 'datadog', 'newrelic']
        self.collection_interval = 60  # seconds
        self.metric_types = ['counter', 'gauge', 'histogram', 'summary']
        self.retention_period = 7  # days
        self.alert_thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'error_rate': 5
        }
        self.logger.info("MetricsCollector initialized with monitoring endpoints")


class RegistryType(Enum):
    """Container registry types."""

    DOCKER_HUB = "docker_hub"
    AWS_ECR = "aws_ecr"
    GCP_GCR = "gcp_gcr"
    AZURE_ACR = "azure_acr"
    HARBOR = "harbor"
    GITLAB = "gitlab"
    ARTIFACTORY = "artifactory"


class ImageStatus(Enum):
    """Container image status."""

    BUILDING = "building"
    BUILT = "built"
    SCANNING = "scanning"
    SCANNED = "scanned"
    PUBLISHED = "published"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class ScanSeverity(Enum):
    """Vulnerability scan severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class RegistryConfig:
    """Container registry configuration."""
    name: str
    registry_type: RegistryType
    url: str
    username: str
    password: str
    namespace: str
    region: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


@dataclass
class ImageConfig:
    """
Container image configuration."""
    name: str
    tag: str
    dockerfile_path: str
    build_context: str
    build_args: Dict[str, str]
    labels: Dict[str, str]
    platforms: List[str]
    registry: str
    namespace: str


@dataclass
class ScanResult:
    """
Security scan result."""
    image_id: str
    scan_id: str
    timestamp: datetime
    vulnerabilities: List[Dict[str, Any]]
    total_count: int
    severity_counts: Dict[ScanSeverity, int]
    compliant: bool
    scan_duration: float


@dataclass
class ImageInfo:
    """
Container image information."""
    name: str
    tag: str
    digest: str
    size_bytes: int
    created_at: datetime
    pushed_at: datetime
    status: ImageStatus
    scan_result: Optional[ScanResult]
    metadata: Dict[str, Any]


class ContainerRegistryManager(BaseDeploymentManager):
    """
    Enterprise container registry management.
    
    Manages container images across multiple registries with security
    scanning, lifecycle management, and automated compliance checks.
    """
    def __init__(
        self,
        vulnerability_scanner -> None: Optional[VulnerabilityScanner] = None,
        metrics_collector -> None: Optional[MetricsCollector] = None
    ) -> None:
        super().__init__()
        self.vulnerability_scanner = vulnerability_scanner or VulnerabilityScanner()
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Registry connections
        self.registries: Dict[str, RegistryConfig] = {}
        self.docker_clients: Dict[str, docker.DockerClient] = {}
        
        # Image tracking
        self.images: Dict[str, ImageInfo] = {}
        self.build_queue: List[ImageConfig] = []
        self.scan_queue: List[str] = []
        
        # Security policies
        self.security_policies = {
            "max_critical_vulnerabilities": 0,
            "max_high_vulnerabilities": 5,
            "required_scans": True,
            "block_deprecated_images": True,
            "retention_days": 90
        }
        
        # Metrics
        self.build_metrics = prometheus_client.Counter(
            'container_builds_total',
            'Total number of container builds',
            ['registry', 'image', 'status']
        )
        
        self.vulnerability_metrics = prometheus_client.Gauge(
            'container_vulnerabilities_total',
            'Total number of vulnerabilities',
            ['registry', 'image', 'severity']
        )

    async def register_registry(self, config: RegistryConfig) -> bool:
        """
        Register container registry.
        
        Args:
            config: Registry configuration
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate registry configuration
            if not self._validate_registry_config(config):
                return False
            
            # Test registry connection
            connection_ok = await self._test_registry_connection(config)
            if not connection_ok:
                return False
            
            # Create Docker client
            docker_client = self._create_docker_client(config)
            if not docker_client:
                return False
            
            # Store configuration
            self.registries[config.name] = config
            self.docker_clients[config.name] = docker_client
            
            self.logger.info(f"Registry '{config.name}' registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register registry '{config.name}': {e}")
            return False

    def _validate_registry_config(self, config: RegistryConfig) -> bool:
        """Validate registry configuration."""
        if not config.name or not config.url:
            self.logger.error("Registry name and URL are required")
            return False
        
        if not config.username or not config.password:
            self.logger.error("Registry credentials are required")
            return False
        
        return True

    async def _test_registry_connection(self, config: RegistryConfig) -> bool:
        """Test registry connection."""
        try:
            # Implementation would test actual registry connection
            self.logger.info(f"Testing connection to registry '{config.name}'")
            await asyncio.sleep(0.5)  # Simulate connection test
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to registry '{config.name}': {e}")
            return False

    def _create_docker_client(self, config: RegistryConfig) -> Optional[docker.DockerClient]:
        """Create Docker client for registry."""
        try:
            # Create Docker client with registry configuration
            client = docker.from_env()
            
            # Login to registry
            client.login(
                username=config.username,
                password=config.password,
                registry=config.url
            )
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create Docker client for registry '{config.name}': {e}")
            return None

    async def build_image(self, config: ImageConfig) -> Optional[str]:
        """
        Build container image.
        
        Args:
            config: Image configuration
            
        Returns:
            Image ID if build successful, None otherwise
        """
        try:
            # Validate build configuration
            if not self._validate_image_config(config):
                return None
            
            # Check if registry exists
            if config.registry not in self.registries:
                self.logger.error(f"Registry '{config.registry}' not found")
                return None
            
            docker_client = self.docker_clients[config.registry]
            
            # Create image info
            image_key = f"{config.registry}/{config.namespace}/{config.name}:{config.tag}"
            image_info = ImageInfo(
                name=config.name,
                tag=config.tag,
                digest="",
                size_bytes=0,
                created_at=datetime.now(),
                pushed_at=datetime.now(),
                status=ImageStatus.BUILDING,
                scan_result=None,
                metadata={
                    "registry": config.registry,
                    "namespace": config.namespace,
                    "build_args": config.build_args,
                    "labels": config.labels
                }
            )
            
            self.images[image_key] = image_info
            
            # Build image
            self.logger.info(f"Building image '{image_key}'")
            
            image, build_logs = docker_client.images.build(
                path=config.build_context,
                dockerfile=config.dockerfile_path,
                tag=image_key,
                buildargs=config.build_args,
                labels=config.labels,
                platform=config.platforms[0] if config.platforms else None
            )
            
            # Update image info
            image_info.digest = image.id
            image_info.size_bytes = len(image.history())
            image_info.status = ImageStatus.BUILT
            
            # Log build metrics
            self.build_metrics.labels(
                registry=config.registry,
                image=config.name,
                status='success'
            ).inc()
            
            self.logger.info(f"Image '{image_key}' built successfully")
            
            # Queue for security scanning
            self.scan_queue.append(image_key)
            
            return image.id
            
        except Exception as e:
            # Log build failure
            self.build_metrics.labels(
                registry=config.registry,
                image=config.name,
                status='failed'
            ).inc()
            
            self.logger.error(f"Failed to build image '{config.name}': {e}")
            return None

    def _validate_image_config(self, config: ImageConfig) -> bool:
        """Validate image configuration."""
        if not config.name or not config.tag:
            self.logger.error("Image name and tag are required")
            return False
        
        if not config.dockerfile_path or not config.build_context:
            self.logger.error("Dockerfile path and build context are required")
            return False
        
        return True

    async def scan_image(self, image_key: str) -> Optional[ScanResult]:
        """
        Scan image for security vulnerabilities.
        
        Args:
            image_key: Image identifier
            
        Returns:
            Scan result or None if scan failed
        """
        try:
            if image_key not in self.images:
                self.logger.error(f"Image '{image_key}' not found")
                return None
            
            image_info = self.images[image_key]
            image_info.status = ImageStatus.SCANNING
            
            self.logger.info(f"Scanning image '{image_key}' for vulnerabilities")
            
            # Perform vulnerability scan
            scan_start = datetime.now()
            
            # Use vulnerability scanner
            vulnerabilities = await self.vulnerability_scanner.scan_image(
                image_info.digest,
                image_info.name,
                image_info.tag
            )
            
            scan_duration = (datetime.now() - scan_start).total_seconds()
            
            # Process scan results
            severity_counts = {severity: 0 for severity in ScanSeverity}
            
            for vuln in vulnerabilities:
                severity = ScanSeverity(vuln.get("severity", "unknown").lower())
                severity_counts[severity] += 1
            
            # Create scan result
            scan_result = ScanResult(
                image_id=image_info.digest,
                scan_id=f"scan-{hashlib.md5(image_key.encode()).hexdigest()[:8]}",
                timestamp=datetime.now(),
                vulnerabilities=vulnerabilities,
                total_count=len(vulnerabilities),
                severity_counts=severity_counts,
                compliant=self._check_compliance(severity_counts),
                scan_duration=scan_duration
            )
            
            # Update image info
            image_info.scan_result = scan_result
            image_info.status = ImageStatus.SCANNED
            
            # Update vulnerability metrics
            for severity, count in severity_counts.items():
                self.vulnerability_metrics.labels(
                    registry=image_info.metadata["registry"],
                    image=image_info.name,
                    severity=severity.value
                ).set(count)
            
            self.logger.info(f"Image '{image_key}' scanned: {len(vulnerabilities)} vulnerabilities found")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Failed to scan image '{image_key}': {e}")
            return None

    def _check_compliance(self, severity_counts: Dict[ScanSeverity, int]) -> bool:
        """Check if image meets security compliance requirements."""
        if severity_counts[ScanSeverity.CRITICAL] > self.security_policies["max_critical_vulnerabilities"]:
            return False
        
        if severity_counts[ScanSeverity.HIGH] > self.security_policies["max_high_vulnerabilities"]:
            return False
        
        return True

    async def push_image(self, image_key: str, force: bool = False) -> bool:
        """
        Push image to registry.
        
        Args:
            image_key: Image identifier
            force: Force push even if compliance check fails
            
        Returns:
            True if push successful, False otherwise
        """
        try:
            if image_key not in self.images:
                self.logger.error(f"Image '{image_key}' not found")
                return False
            
            image_info = self.images[image_key]
            
            # Check compliance
            if not force and image_info.scan_result and not image_info.scan_result.compliant:
                self.logger.error(f"Image '{image_key}' does not meet security compliance requirements")
                return False
            
            # Get Docker client
            registry_config = self.registries[image_info.metadata["registry"]]
            docker_client = self.docker_clients[registry_config.name]
            
            # Push image
            self.logger.info(f"Pushing image '{image_key}' to registry")
            
            push_result = docker_client.images.push(
                repository=image_key,
                stream=True,
                decode=True
            )
            
            # Process push result
            for line in push_result:
                if 'error' in line:
                    self.logger.error(f"Push error: {line['error']}")
                    return False
                elif 'status' in line and 'digest' in line:
                    image_info.digest = line['digest']
            
            # Update image status
            image_info.status = ImageStatus.PUBLISHED
            image_info.pushed_at = datetime.now()
            
            self.logger.info(f"Image '{image_key}' pushed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to push image '{image_key}': {e}")
            return False

    async def pull_image(self, image_key: str, registry_name: str) -> bool:
        """
        Pull image from registry.
        
        Args:
            image_key: Image identifier
            registry_name: Registry name
            
        Returns:
            True if pull successful, False otherwise
        """
        try:
            if registry_name not in self.registries:
                self.logger.error(f"Registry '{registry_name}' not found")
                return False
            
            docker_client = self.docker_clients[registry_name]
            
            self.logger.info(f"Pulling image '{image_key}' from registry '{registry_name}'")
            
            # Pull image
            image = docker_client.images.pull(image_key)
            
            # Create image info if not exists
            if image_key not in self.images:
                self.images[image_key] = ImageInfo(
                    name=image_key.split(':')[0].split('/')[-1],
                    tag=image_key.split(':')[1] if ':' in image_key else 'latest',
                    digest=image.id,
                    size_bytes=image.attrs.get('Size', 0),
                    created_at=datetime.fromisoformat(image.attrs.get('Created', datetime.now().isoformat())),
                    pushed_at=datetime.now(),
                    status=ImageStatus.BUILT,
                    scan_result=None,
                    metadata={"registry": registry_name}
                )
            
            self.logger.info(f"Image '{image_key}' pulled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull image '{image_key}': {e}")
            return False

    async def delete_image(self, image_key: str, force: bool = False) -> bool:
        """
        Delete image from registry and local storage.
        
        Args:
            image_key: Image identifier
            force: Force deletion even if image is in use
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if image_key not in self.images:
                self.logger.error(f"Image '{image_key}' not found")
                return False
            
            image_info = self.images[image_key]
            
            # Check if image is in use
            if not force:
                in_use = await self._check_image_in_use(image_key)
                if in_use:
                    self.logger.error(f"Image '{image_key}' is in use. Use force=True to delete anyway.")
                    return False
            
            # Get Docker client
            registry_config = self.registries[image_info.metadata["registry"]]
            docker_client = self.docker_clients[registry_config.name]
            
            # Delete from local Docker
            try:
                docker_client.images.remove(image_key, force=force)
            except docker.errors.ImageNotFound:
                pass  # Image not found locally
            
            # Remove from tracking
            del self.images[image_key]
            
            self.logger.info(f"Image '{image_key}' deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete image '{image_key}': {e}")
            return False

    async def _check_image_in_use(self, image_key: str) -> bool:
        """Check if image is currently in use by running containers."""
        try:
            # This would check Kubernetes deployments, running containers, etc.
            # For now, we'll simulate the check
            await asyncio.sleep(0.1)
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check if image '{image_key}' is in use: {e}")
            return False

    async def list_images(self, registry_name: Optional[str] = None) -> List[ImageInfo]:
        """
        List container images.
        
        Args:
            registry_name: Optional filter by registry
            
        Returns:
            List of image information
        """
        images = list(self.images.values())
        
        if registry_name:
            images = [img for img in images if img.metadata.get("registry") == registry_name]
        
        return images

    async def cleanup_old_images(self, retention_days: Optional[int] = None) -> int:
        """
        Cleanup old and unused images.
        
        Args:
            retention_days: Number of days to retain images (uses policy default if None)
            
        Returns:
            Number of images cleaned up
        """
        try:
            retention_days = retention_days or self.security_policies["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            images_to_delete = []
            
            for image_key, image_info in self.images.items():
                # Skip if image is too recent
                if image_info.created_at > cutoff_date:
                    continue
                
                # Skip if image is in use
                in_use = await self._check_image_in_use(image_key)
                if in_use:
                    continue
                
                # Skip if image is not deprecated or failed
                if image_info.status not in [ImageStatus.DEPRECATED, ImageStatus.FAILED]:
                    continue
                
                images_to_delete.append(image_key)
            
            # Delete old images
            cleanup_count = 0
            for image_key in images_to_delete:
                deleted = await self.delete_image(image_key, force=True)
                if deleted:
                    cleanup_count += 1
            
            self.logger.info(f"Cleaned up {cleanup_count} old images")
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old images: {e}")
            return 0

    async def mirror_image(self, source_image: str, target_registry: str, target_tag: Optional[str] = None) -> bool:
        """
        Mirror image between registries.
        
        Args:
            source_image: Source image identifier
            target_registry: Target registry name
            target_tag: Optional target tag (uses source tag if None)
            
        Returns:
            True if mirroring successful, False otherwise
        """
        try:
            if target_registry not in self.registries:
                self.logger.error(f"Target registry '{target_registry}' not found")
                return False
            
            # Parse source image
            source_parts = source_image.split(':')
            source_name = source_parts[0]
            source_tag = source_parts[1] if len(source_parts) > 1 else 'latest'
            
            target_tag = target_tag or source_tag
            target_registry_config = self.registries[target_registry]
            target_image = f"{target_registry_config.url}/{target_registry_config.namespace}/{source_name.split('/')[-1]}:{target_tag}"
            
            # Pull source image
            source_registry = self._detect_source_registry(source_image)
            if source_registry and source_registry in self.docker_clients:
                docker_client = self.docker_clients[source_registry]
            else:
                # Use default Docker Hub
                docker_client = docker.from_env()
            
            self.logger.info(f"Mirroring image from '{source_image}' to '{target_image}'")
            
            # Pull source
            source_img = docker_client.images.pull(source_image)
            
            # Tag for target registry
            source_img.tag(target_image)
            
            # Push to target registry
            target_client = self.docker_clients[target_registry]
            push_result = target_client.images.push(target_image)
            
            self.logger.info(f"Image mirrored successfully: '{source_image}' -> '{target_image}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mirror image '{source_image}': {e}")
            return False

    def _detect_source_registry(self, image: str) -> Optional[str]:
        """Detect source registry from image name."""
        for registry_name, config in self.registries.items():
            if image.startswith(config.url):
                return registry_name
        return None

    async def generate_image_report(self, registry_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive image security and usage report.
        
        Args:
            registry_name: Optional filter by registry
            
        Returns:
            Report data
        """
        try:
            images = await self.list_images(registry_name)
            
            # Calculate statistics
            total_images = len(images)
            total_vulnerabilities = 0
            severity_totals = {severity: 0 for severity in ScanSeverity}
            compliant_images = 0
            
            for image in images:
                if image.scan_result:
                    total_vulnerabilities += image.scan_result.total_count
                    for severity, count in image.scan_result.severity_counts.items():
                        severity_totals[severity] += count
                    
                    if image.scan_result.compliant:
                        compliant_images += 1
            
            report = {
                "report_generated": datetime.now().isoformat(),
                "registry_filter": registry_name,
                "summary": {
                    "total_images": total_images,
                    "compliant_images": compliant_images,
                    "compliance_rate": (compliant_images / total_images * 100) if total_images > 0 else 0,
                    "total_vulnerabilities": total_vulnerabilities
                },
                "vulnerabilities_by_severity": {
                    severity.value: count for severity, count in severity_totals.items()
                },
                "images": [
                    {
                        "name": img.name,
                        "tag": img.tag,
                        "size_mb": round(img.size_bytes / (1024 * 1024), 2),
                        "created": img.created_at.isoformat(),
                        "status": img.status.value,
                        "vulnerabilities": img.scan_result.total_count if img.scan_result else None,
                        "compliant": img.scan_result.compliant if img.scan_result else None
                    }
                    for img in images
                ]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate image report: {e}")
            return {}

    async def process_scan_queue(self) -> None:
        """Process pending image scans."""
        while self.scan_queue:
            image_key = self.scan_queue.pop(0)
            scan_result = await self.scan_image(image_key)
            
            if scan_result:
                self.logger.info(f"Scan completed for '{image_key}'")
            else:
                self.logger.error(f"Scan failed for '{image_key}'")
            
            # Small delay to prevent overwhelming the scanner
            await asyncio.sleep(1)

    async def set_security_policy(self, policy_name: str, value: Any) -> bool:
        """
        Update security policy.
        
        Args:
            policy_name: Policy name
            value: Policy value
            
        Returns:
            True if policy updated successfully, False otherwise
        """
        try:
            if policy_name in self.security_policies:
                self.security_policies[policy_name] = value
                self.logger.info(f"Security policy '{policy_name}' updated to: {value}")
                return True
            else:
                self.logger.error(f"Unknown security policy: '{policy_name}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update security policy '{policy_name}': {e}")
            return False

    async def cleanup(self) -> bool:
        """
        Cleanup container registry manager.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            # Close Docker clients
            for client in self.docker_clients.values():
                client.close()
            
            # Clear registries and images
            self.registries.clear()
            self.docker_clients.clear()
            self.images.clear()
            
            self.logger.info("Container registry manager cleaned up successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup container registry manager: {e}")
            return False
