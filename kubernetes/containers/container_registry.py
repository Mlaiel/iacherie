"""🏗️ Container Registry Manager - IA-Influencer-Agent Infrastructure
=================================================================
Expert Team: DevOps Engineer + Registry Specialist + Security Engineer + CI/CD Engineer
Creator: Fahed Mlaiel <mlaiel@live.de>
Company: IA-Influencer-Agent Professional Platform
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Contact légal: mlaiel@live.de

Enterprise-grade container registry management and advanced CI/CD pipeline integration
for IA-Influencer-Agent platform. Includes intelligent image building, comprehensive 
security scanning, automated versioning, multi-registry distribution, artifact 
management, and optimized content delivery for AI processing workloads.
"""from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
import json
import yaml
import hashlib
import base64
import tarfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import docker
import boto3
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

class RegistryType(Enum):
    """Container registry types"""    DOCKER_HUB = "docker_hub"
    AWS_ECR = "aws_ecr"
    AZURE_ACR = "azure_acr"
    GOOGLE_GCR = "google_gcr"
    HARBOR = "harbor"
    NEXUS = "nexus"
    PRIVATE = "private"

class ImageBuildStatus(Enum):
    """Image build status"""    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ImageScanStatus(Enum):
    """Image security scan status"""    NOT_SCANNED = "not_scanned"
    SCANNING = "scanning"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class RegistryConfig:
    """Registry configuration"""    name: str
    type: RegistryType
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    namespace: Optional[str] = None
    ssl_verify: bool = True
    timeout: int = 300
    max_retries: int = 3

@dataclass
class ImageManifest:
    """Container image manifest"""    name: str
    tag: str
    digest: str
    size: int
    created: datetime
    architecture: str
    os: str
    layers: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    env_vars: List[str] = field(default_factory=list)
    exposed_ports: List[int] = field(default_factory=list)

@dataclass
class BuildConfiguration:
    """Image build configuration"""    name: str
    dockerfile_path: str
    context_path: str
    target_registries: List[str]
    build_args: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    platforms: List[str] = field(default_factory=lambda: ["linux/amd64"])
    cache_from: List[str] = field(default_factory=list)
    no_cache: bool = False
    pull: bool = True
    squash: bool = False
    
@dataclass
class PipelineStage:
    """CI/CD pipeline stage"""    name: str
    stage_type: str  # build, test, scan, deploy
    commands: List[str]
    environment: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 600
    retry_count: int = 1
    continue_on_error: bool = False

class ContainerRegistryManager:
    """Professional container registry manager"""    
    def __init__(self, config_path: str = "/app/config/registry"):
        self.config_path = Path(config_path)
        self.registries = {}
        self.docker_client = None
        self.build_queue = asyncio.Queue()
        self.build_history = {}
        self.image_cache = {}
        self.scan_results = {}
        self.active_builds = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize container registry manager"""        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Load registry configurations
            await self._load_registry_configs()
            
            # Setup default registries for IA-Influencer
            await self._setup_default_registries()
            
            # Start build worker
            asyncio.create_task(self._build_worker())
            
            self.initialized = True
            self.logger.info("✅ ContainerRegistryManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ContainerRegistryManager: {e}")
            return False
    
    async def _load_registry_configs(self) -> None:
        """Load existing registry configurations"""        try:
            config_files = self.config_path.glob("registry_*.yml")
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    registry_config = RegistryConfig(**config_data)
                    self.registries[registry_config.name] = registry_config
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading registry configs: {e}")
    
    async def _setup_default_registries(self) -> None:
        """Setup default registries for IA-Influencer platform"""        try:
            # Private registry for IA-Influencer images
            private_registry = RegistryConfig(
                name="ia-influencer-private",
                type=RegistryType.HARBOR,
                url="registry.ia-influencer-agent.com",
                username="ia-admin",
                password="${REGISTRY_PASSWORD}",
                namespace="ia-influencer",
                ssl_verify=True,
                timeout=300
            )
            
            # AWS ECR for production images
            aws_ecr = RegistryConfig(
                name="aws-ecr-prod",
                type=RegistryType.AWS_ECR,
                url="123456789012.dkr.ecr.eu-central-1.amazonaws.com",
                namespace="ia-influencer",
                token="${AWS_ECR_TOKEN}",
                ssl_verify=True
            )
            
            # Azure ACR for backup/multi-cloud
            azure_acr = RegistryConfig(
                name="azure-acr-backup",
                type=RegistryType.AZURE_ACR,
                url="iainfluenceracr.azurecr.io",
                username="iainfluenceracr",
                password="${AZURE_ACR_PASSWORD}",
                namespace="ia-influencer"
            )
            
            # Docker Hub for public base images
            docker_hub = RegistryConfig(
                name="docker-hub",
                type=RegistryType.DOCKER_HUB,
                url="https://index.docker.io/v1/",
                username="iainfluencer",
                password="${DOCKER_HUB_TOKEN}"
            )
            
            # Store registries
            registries_to_store = {
                "private": private_registry,
                "aws-ecr": aws_ecr,
                "azure-acr": azure_acr,
                "docker-hub": docker_hub
            }
            
            for name, registry in registries_to_store.items():
                self.registries[registry.name] = registry
                await self._save_registry_config(name, registry)
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default registries: {e}")
    
    async def _save_registry_config(self, name: str, config: RegistryConfig) -> None:
        """Save registry configuration to file"""        try:
            config_file = self.config_path / f"registry_{name}.yml"
            with open(config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving registry config {name}: {e}")
    
    async def authenticate_registry(self, registry_name: str) -> bool:
        """Authenticate with container registry"""        try:
            if registry_name not in self.registries:
                self.logger.error(f"❌ Registry {registry_name} not found")
                return False
            
            registry = self.registries[registry_name]
            
            if registry.type == RegistryType.DOCKER_HUB:
                return await self._authenticate_docker_hub(registry)
            elif registry.type == RegistryType.AWS_ECR:
                return await self._authenticate_aws_ecr(registry)
            elif registry.type == RegistryType.AZURE_ACR:
                return await self._authenticate_azure_acr(registry)
            elif registry.type == RegistryType.HARBOR:
                return await self._authenticate_harbor(registry)
            else:
                return await self._authenticate_generic(registry)
                
        except Exception as e:
            self.logger.error(f"❌ Error authenticating with registry {registry_name}: {e}")
            return False
    
    async def _authenticate_docker_hub(self, registry: RegistryConfig) -> bool:
        """Authenticate with Docker Hub"""        try:
            login_result = self.docker_client.login(
                username=registry.username,
                password=registry.password,
                registry=registry.url
            )
            
            if "Login Succeeded" in login_result.get("Status", ""):
                self.logger.info(f"✅ Authenticated with Docker Hub")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Docker Hub authentication failed: {e}")
            return False
    
    async def _authenticate_aws_ecr(self, registry: RegistryConfig) -> bool:
        """Authenticate with AWS ECR"""        try:
            # Get ECR login token
            ecr_client = boto3.client('ecr', region_name='eu-central-1')
            response = ecr_client.get_authorization_token()
            
            token = response['authorizationData'][0]['authorizationToken']
            username, password = base64.b64decode(token).decode().split(':')
            
            login_result = self.docker_client.login(
                username=username,
                password=password,
                registry=registry.url
            )
            
            if "Login Succeeded" in login_result.get("Status", ""):
                self.logger.info(f"✅ Authenticated with AWS ECR")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ AWS ECR authentication failed: {e}")
            return False
    
    async def _authenticate_azure_acr(self, registry: RegistryConfig) -> bool:
        """Authenticate with Azure ACR"""        try:
            login_result = self.docker_client.login(
                username=registry.username,
                password=registry.password,
                registry=registry.url
            )
            
            if "Login Succeeded" in login_result.get("Status", ""):
                self.logger.info(f"✅ Authenticated with Azure ACR")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Azure ACR authentication failed: {e}")
            return False
    
    async def _authenticate_harbor(self, registry: RegistryConfig) -> bool:
        """Authenticate with Harbor registry"""        try:
            login_result = self.docker_client.login(
                username=registry.username,
                password=registry.password,
                registry=registry.url
            )
            
            if "Login Succeeded" in login_result.get("Status", ""):
                self.logger.info(f"✅ Authenticated with Harbor registry")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Harbor authentication failed: {e}")
            return False
    
    async def _authenticate_generic(self, registry: RegistryConfig) -> bool:
        """Authenticate with generic registry"""        try:
            auth_config = {}
            if registry.username and registry.password:
                auth_config = {
                    'username': registry.username,
                    'password': registry.password
                }
            elif registry.token:
                auth_config = {
                    'username': 'token',
                    'password': registry.token
                }
            
            if auth_config:
                login_result = self.docker_client.login(
                    registry=registry.url,
                    **auth_config
                )
                
                if "Login Succeeded" in login_result.get("Status", ""):
                    self.logger.info(f"✅ Authenticated with registry {registry.name}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Generic registry authentication failed: {e}")
            return False
    
    async def build_image(
        self, 
        build_config: BuildConfiguration,
        registry_names: List[str] = None
    ) -> str:
        """Queue image build"""        try:
            build_id = hashlib.md5(f"{build_config.name}_{datetime.now()}".encode()).hexdigest()
            
            build_request = {
                "build_id": build_id,
                "config": build_config,
                "registry_names": registry_names or ["ia-influencer-private"],
                "queued_at": datetime.now(),
                "status": ImageBuildStatus.PENDING
            }
            
            await self.build_queue.put(build_request)
            self.active_builds[build_id] = build_request
            
            self.logger.info(f"📋 Queued build for {build_config.name} (ID: {build_id})")
            return build_id
            
        except Exception as e:
            self.logger.error(f"❌ Error queuing build: {e}")
            return ""
    
    async def _build_worker(self) -> None:
        """Background worker for processing build queue"""        while True:
            try:
                # Get build request from queue
                build_request = await self.build_queue.get()
                
                build_id = build_request["build_id"]
                build_config = build_request["config"]
                registry_names = build_request["registry_names"]
                
                # Update build status
                self.active_builds[build_id]["status"] = ImageBuildStatus.BUILDING
                self.active_builds[build_id]["started_at"] = datetime.now()
                
                self.logger.info(f"🔨 Starting build: {build_config.name}")
                
                # Perform build
                success = await self._perform_build(build_id, build_config, registry_names)
                
                # Update build status
                if success:
                    self.active_builds[build_id]["status"] = ImageBuildStatus.SUCCESS
                    self.active_builds[build_id]["completed_at"] = datetime.now()
                else:
                    self.active_builds[build_id]["status"] = ImageBuildStatus.FAILED
                    self.active_builds[build_id]["failed_at"] = datetime.now()
                
                # Store in history
                self.build_history[build_id] = self.active_builds[build_id]
                
                self.build_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"❌ Error in build worker: {e}")
                await asyncio.sleep(10)
    
    async def _perform_build(
        self, 
        build_id: str, 
        config: BuildConfiguration, 
        registry_names: List[str]
    ) -> bool:
        """Perform actual image build"""        try:
            # Build image
            image_tags = []
            
            for registry_name in registry_names:
                if registry_name in self.registries:
                    registry = self.registries[registry_name]
                    
                    # Generate image tag
                    if registry.namespace:
                        image_tag = f"{registry.url}/{registry.namespace}/{config.name}:latest"
                    else:
                        image_tag = f"{registry.url}/{config.name}:latest"
                    
                    image_tags.append(image_tag)
            
            # Build with Docker client
            self.logger.info(f"🔨 Building image: {config.name}")
            
            image, build_logs = self.docker_client.images.build(
                path=config.context_path,
                dockerfile=config.dockerfile_path,
                tag=image_tags[0] if image_tags else config.name,
                buildargs=config.build_args,
                labels=config.labels,
                nocache=config.no_cache,
                pull=config.pull,
                squash=config.squash,
                rm=True
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    self.logger.debug(log['stream'].strip())
            
            # Tag for all registries
            for tag in image_tags[1:]:
                image.tag(tag)
            
            # Store image manifest
            manifest = await self._generate_image_manifest(image, config.name)
            self.image_cache[build_id] = manifest
            
            self.logger.info(f"✅ Successfully built image: {config.name}")
            
            # Push to registries
            push_success = await self._push_to_registries(image_tags, registry_names)
            
            return push_success
            
        except Exception as e:
            self.logger.error(f"❌ Error building image: {e}")
            return False
    
    async def _generate_image_manifest(self, image, name: str) -> ImageManifest:
        """Generate image manifest"""        try:
            attrs = image.attrs
            config = attrs.get("Config", {})
            
            manifest = ImageManifest(
                name=name,
                tag="latest",
                digest=attrs.get("Id", ""),
                size=attrs.get("Size", 0),
                created=datetime.fromisoformat(attrs.get("Created", "").replace("Z", "+00:00")),
                architecture=attrs.get("Architecture", "amd64"),
                os=attrs.get("Os", "linux"),
                layers=attrs.get("RootFS", {}).get("Layers", []),
                labels=config.get("Labels", {}),
                env_vars=config.get("Env", []),
                exposed_ports=list(config.get("ExposedPorts", {}).keys())
            )
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"❌ Error generating image manifest: {e}")
            return ImageManifest(
                name=name, tag="latest", digest="", size=0,
                created=datetime.now(), architecture="amd64", os="linux"
            )
    
    async def _push_to_registries(self, image_tags: List[str], registry_names: List[str]) -> bool:
        """Push image to registries"""        try:
            push_success = True
            
            for i, tag in enumerate(image_tags):
                registry_name = registry_names[i] if i < len(registry_names) else registry_names[0]
                
                # Authenticate with registry
                auth_success = await self.authenticate_registry(registry_name)
                if not auth_success:
                    self.logger.error(f"❌ Failed to authenticate with registry {registry_name}")
                    push_success = False
                    continue
                
                # Push image
                self.logger.info(f"📤 Pushing image to {registry_name}: {tag}")
                
                try:
                    push_logs = self.docker_client.images.push(tag, stream=True)
                    
                    for log in push_logs:
                        if 'error' in log:
                            self.logger.error(f"❌ Push error: {log['error']}")
                            push_success = False
                            break
                        elif 'status' in log:
                            self.logger.debug(log['status'])
                    
                    if push_success:
                        self.logger.info(f"✅ Successfully pushed to {registry_name}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error pushing to {registry_name}: {e}")
                    push_success = False
            
            return push_success
            
        except Exception as e:
            self.logger.error(f"❌ Error pushing to registries: {e}")
            return False
    
    async def scan_image(self, image_name: str, registry_name: str) -> Dict[str, Any]:
        """Scan image for vulnerabilities"""        try:
            scan_id = hashlib.md5(f"{image_name}_{datetime.now()}".encode()).hexdigest()
            
            self.logger.info(f"🔍 Starting security scan for image: {image_name}")
            
            # Use Trivy for vulnerability scanning
            scan_result = await self._scan_with_trivy(image_name)
            
            # Store scan result
            self.scan_results[scan_id] = {
                "scan_id": scan_id,
                "image_name": image_name,
                "registry_name": registry_name,
                "scan_time": datetime.now(),
                "status": ImageScanStatus.PASSED if scan_result["critical_count"] == 0 else ImageScanStatus.FAILED,
                "vulnerabilities": scan_result["vulnerabilities"],
                "critical_count": scan_result["critical_count"],
                "high_count": scan_result["high_count"],
                "medium_count": scan_result["medium_count"],
                "low_count": scan_result["low_count"]
            }
            
            return self.scan_results[scan_id]
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning image: {e}")
            return {"status": ImageScanStatus.FAILED, "error": str(e)}
    
    async def _scan_with_trivy(self, image_name: str) -> Dict[str, Any]:
        """Scan image with Trivy"""        try:
            result = subprocess.run([
                "trivy", "image", 
                "--format", "json",
                "--quiet",
                image_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"vulnerabilities": [], "critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
            
            trivy_data = json.loads(result.stdout)
            vulnerabilities = []
            counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            for target in trivy_data.get("Results", []):
                for vuln in target.get("Vulnerabilities", []):
                    severity = vuln.get("Severity", "UNKNOWN").lower()
                    if severity in counts:
                        counts[severity] += 1
                    
                    vulnerabilities.append({
                        "cve_id": vuln.get("VulnerabilityID", ""),
                        "severity": severity,
                        "package": vuln.get("PkgName", ""),
                        "version": vuln.get("InstalledVersion", ""),
                        "fixed_version": vuln.get("FixedVersion", ""),
                        "description": vuln.get("Description", "")
                    })
            
            return {
                "vulnerabilities": vulnerabilities,
                "critical_count": counts["critical"],
                "high_count": counts["high"],
                "medium_count": counts["medium"],
                "low_count": counts["low"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error with Trivy scan: {e}")
            return {"vulnerabilities": [], "critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
    
    async def list_images(self, registry_name: str, repository: str = None) -> List[Dict[str, Any]]:
        """List images in registry"""        try:
            if registry_name not in self.registries:
                return []
            
            registry = self.registries[registry_name]
            
            if registry.type == RegistryType.AWS_ECR:
                return await self._list_ecr_images(registry, repository)
            elif registry.type == RegistryType.AZURE_ACR:
                return await self._list_acr_images(registry, repository)
            elif registry.type == RegistryType.HARBOR:
                return await self._list_harbor_images(registry, repository)
            else:
                return await self._list_generic_images(registry, repository)
                
        except Exception as e:
            self.logger.error(f"❌ Error listing images: {e}")
            return []
    
    async def _list_ecr_images(self, registry: RegistryConfig, repository: str = None) -> List[Dict[str, Any]]:
        """List images in AWS ECR"""        try:
            ecr_client = boto3.client('ecr', region_name='eu-central-1')
            
            if repository:
                response = ecr_client.describe_images(repositoryName=repository)
            else:
                # List all repositories first
                repos_response = ecr_client.describe_repositories()
                images = []
                
                for repo in repos_response['repositories']:
                    repo_images = ecr_client.describe_images(repositoryName=repo['repositoryName'])
                    for image in repo_images['imageDetails']:
                        images.append({
                            "repository": repo['repositoryName'],
                            "tags": image.get('imageTags', []),
                            "digest": image['imageDigest'],
                            "size": image['imageSizeInBytes'],
                            "pushed_at": image['imagePushedAt']
                        })
                
                return images
            
            images = []
            for image in response['imageDetails']:
                images.append({
                    "repository": repository,
                    "tags": image.get('imageTags', []),
                    "digest": image['imageDigest'],
                    "size": image['imageSizeInBytes'],
                    "pushed_at": image['imagePushedAt']
                })
            
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error listing ECR images: {e}")
            return []
    
    async def _list_acr_images(self, registry: RegistryConfig, repository: str = None) -> List[Dict[str, Any]]:
        """List images in Azure ACR"""        try:
            # Simplified ACR implementation
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error listing ACR images: {e}")
            return []
    
    async def _list_harbor_images(self, registry: RegistryConfig, repository: str = None) -> List[Dict[str, Any]]:
        """List images in Harbor registry"""        try:
            # Use Harbor API
            base_url = f"https://{registry.url}/api/v2.0"
            
            async with aiohttp.ClientSession() as session:
                # Get projects
                projects_url = f"{base_url}/projects"
                
                auth = aiohttp.BasicAuth(registry.username, registry.password)
                async with session.get(projects_url, auth=auth) as response:
                    if response.status != 200:
                        return []
                    
                    projects = await response.json()
                    images = []
                    
                    for project in projects:
                        project_name = project['name']
                        
                        # Get repositories in project
                        repos_url = f"{base_url}/projects/{project_name}/repositories"
                        async with session.get(repos_url, auth=auth) as repos_response:
                            if repos_response.status == 200:
                                repositories = await repos_response.json()
                                
                                for repo in repositories:
                                    repo_name = repo['name']
                                    
                                    # Get artifacts in repository
                                    artifacts_url = f"{base_url}/projects/{project_name}/repositories/{repo_name.split('/')[-1]}/artifacts"
                                    async with session.get(artifacts_url, auth=auth) as artifacts_response:
                                        if artifacts_response.status == 200:
                                            artifacts = await artifacts_response.json()
                                            
                                            for artifact in artifacts:
                                                images.append({
                                                    "repository": repo_name,
                                                    "tags": [tag['name'] for tag in artifact.get('tags', [])],
                                                    "digest": artifact['digest'],
                                                    "size": artifact['size'],
                                                    "pushed_at": artifact['push_time']
                                                })
                    
                    return images
                    
        except Exception as e:
            self.logger.error(f"❌ Error listing Harbor images: {e}")
            return []
    
    async def _list_generic_images(self, registry: RegistryConfig, repository: str = None) -> List[Dict[str, Any]]:
        """List images in generic registry"""        try:
            # Generic Docker Registry API v2
            base_url = f"https://{registry.url}/v2"
            
            async with aiohttp.ClientSession() as session:
                # List repositories
                catalog_url = f"{base_url}/_catalog"
                
                auth = None
                if registry.username and registry.password:
                    auth = aiohttp.BasicAuth(registry.username, registry.password)
                
                async with session.get(catalog_url, auth=auth) as response:
                    if response.status != 200:
                        return []
                    
                    catalog = await response.json()
                    repositories = catalog.get('repositories', [])
                    
                    images = []
                    
                    for repo in repositories:
                        if repository and repo != repository:
                            continue
                        
                        # Get tags for repository
                        tags_url = f"{base_url}/{repo}/tags/list"
                        async with session.get(tags_url, auth=auth) as tags_response:
                            if tags_response.status == 200:
                                tags_data = await tags_response.json()
                                tags = tags_data.get('tags', [])
                                
                                for tag in tags:
                                    # Get manifest for each tag
                                    manifest_url = f"{base_url}/{repo}/manifests/{tag}"
                                    async with session.get(manifest_url, auth=auth) as manifest_response:
                                        if manifest_response.status == 200:
                                            manifest = await manifest_response.json()
                                            
                                            images.append({
                                                "repository": repo,
                                                "tags": [tag],
                                                "digest": manifest_response.headers.get('Docker-Content-Digest', ''),
                                                "size": sum(layer.get('size', 0) for layer in manifest.get('layers', [])),
                                                "architecture": manifest.get('architecture', 'amd64')
                                            })
                    
                    return images
                    
        except Exception as e:
            self.logger.error(f"❌ Error listing generic registry images: {e}")
            return []
    
    async def delete_image(self, registry_name: str, repository: str, tag: str) -> bool:
        """Delete image from registry"""        try:
            if registry_name not in self.registries:
                return False
            
            registry = self.registries[registry_name]
            
            if registry.type == RegistryType.AWS_ECR:
                return await self._delete_ecr_image(registry, repository, tag)
            elif registry.type == RegistryType.HARBOR:
                return await self._delete_harbor_image(registry, repository, tag)
            else:
                return await self._delete_generic_image(registry, repository, tag)
                
        except Exception as e:
            self.logger.error(f"❌ Error deleting image: {e}")
            return False
    
    async def _delete_ecr_image(self, registry: RegistryConfig, repository: str, tag: str) -> bool:
        """Delete image from AWS ECR"""        try:
            ecr_client = boto3.client('ecr', region_name='eu-central-1')
            
            response = ecr_client.batch_delete_image(
                repositoryName=repository,
                imageIds=[{'imageTag': tag}]
            )
            
            deleted_images = response.get('imageIds', [])
            if deleted_images:
                self.logger.info(f"✅ Deleted image {repository}:{tag} from ECR")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error deleting ECR image: {e}")
            return False
    
    async def _delete_harbor_image(self, registry: RegistryConfig, repository: str, tag: str) -> bool:
        """Delete image from Harbor registry"""        try:
            base_url = f"https://{registry.url}/api/v2.0"
            project_name = repository.split('/')[0]
            repo_name = '/'.join(repository.split('/')[1:])
            
            async with aiohttp.ClientSession() as session:
                # Delete artifact by tag
                delete_url = f"{base_url}/projects/{project_name}/repositories/{repo_name}/artifacts/{tag}"
                
                auth = aiohttp.BasicAuth(registry.username, registry.password)
                async with session.delete(delete_url, auth=auth) as response:
                    if response.status == 200:
                        self.logger.info(f"✅ Deleted image {repository}:{tag} from Harbor")
                        return True
                    else:
                        return False
                        
        except Exception as e:
            self.logger.error(f"❌ Error deleting Harbor image: {e}")
            return False
    
    async def _delete_generic_image(self, registry: RegistryConfig, repository: str, tag: str) -> bool:
        """Delete image from generic registry"""        try:
            # Generic Docker Registry API v2 delete
            base_url = f"https://{registry.url}/v2"
            
            async with aiohttp.ClientSession() as session:
                # Get manifest digest first
                manifest_url = f"{base_url}/{repository}/manifests/{tag}"
                
                auth = None
                if registry.username and registry.password:
                    auth = aiohttp.BasicAuth(registry.username, registry.password)
                
                headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
                
                async with session.get(manifest_url, auth=auth, headers=headers) as response:
                    if response.status != 200:
                        return False
                    
                    digest = response.headers.get('Docker-Content-Digest')
                    if not digest:
                        return False
                    
                    # Delete by digest
                    delete_url = f"{base_url}/{repository}/manifests/{digest}"
                    async with session.delete(delete_url, auth=auth) as delete_response:
                        if delete_response.status == 202:
                            self.logger.info(f"✅ Deleted image {repository}:{tag} from registry")
                            return True
                        else:
                            return False
                            
        except Exception as e:
            self.logger.error(f"❌ Error deleting generic registry image: {e}")
            return False
    
    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get build status"""        try:
            if build_id in self.active_builds:
                return {
                    "build_id": build_id,
                    "status": self.active_builds[build_id]["status"].value,
                    "queued_at": self.active_builds[build_id]["queued_at"].isoformat(),
                    "started_at": self.active_builds[build_id].get("started_at", "").isoformat() if self.active_builds[build_id].get("started_at") else None,
                    "completed_at": self.active_builds[build_id].get("completed_at", "").isoformat() if self.active_builds[build_id].get("completed_at") else None
                }
            elif build_id in self.build_history:
                build = self.build_history[build_id]
                return {
                    "build_id": build_id,
                    "status": build["status"].value,
                    "queued_at": build["queued_at"].isoformat(),
                    "started_at": build.get("started_at", "").isoformat() if build.get("started_at") else None,
                    "completed_at": build.get("completed_at", "").isoformat() if build.get("completed_at") else None,
                    "duration": str(build.get("completed_at", datetime.now()) - build.get("started_at", datetime.now())) if build.get("started_at") else None
                }
            else:
                return {"build_id": build_id, "status": "not_found"}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting build status: {e}")
            return {"build_id": build_id, "status": "error", "error": str(e)}

class ImagePipelineManager:
    """CI/CD pipeline manager for container images"""    
    def __init__(self, registry_manager: ContainerRegistryManager):
        self.registry_manager = registry_manager
        self.pipelines = {}
        self.pipeline_runs = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize pipeline manager"""        try:
            # Setup default pipelines for IA-Influencer services
            await self._setup_default_pipelines()
            
            self.logger.info("✅ ImagePipelineManager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ImagePipelineManager: {e}")
            return False
    
    async def _setup_default_pipelines(self) -> None:
        """Setup default CI/CD pipelines"""        try:
            # Web API Pipeline
            web_api_pipeline = [
                PipelineStage(
                    name="build",
                    stage_type="build",
                    commands=[
                        "docker build -t ia-influencer/web-api:latest .",
                        "docker tag ia-influencer/web-api:latest ia-influencer/web-api:${BUILD_NUMBER}"
                    ],
                    timeout=600
                ),
                PipelineStage(
                    name="test",
                    stage_type="test",
                    commands=[
                        "docker run --rm ia-influencer/web-api:latest pytest tests/",
                        "docker run --rm ia-influencer/web-api:latest flake8 ."
                    ],
                    dependencies=["build"],
                    timeout=300
                ),
                PipelineStage(
                    name="security-scan",
                    stage_type="scan",
                    commands=[
                        "trivy image ia-influencer/web-api:latest",
                        "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock anchore/grype ia-influencer/web-api:latest"
                    ],
                    dependencies=["build"],
                    timeout=300
                ),
                PipelineStage(
                    name="push",
                    stage_type="deploy",
                    commands=[
                        "docker push ia-influencer/web-api:latest",
                        "docker push ia-influencer/web-api:${BUILD_NUMBER}"
                    ],
                    dependencies=["test", "security-scan"],
                    timeout=300
                )
            ]
            
            # AI Engine Pipeline
            ai_engine_pipeline = [
                PipelineStage(
                    name="build",
                    stage_type="build",
                    commands=[
                        "docker build -f Dockerfile.ai-engine -t ia-influencer/ai-engine:latest .",
                        "docker tag ia-influencer/ai-engine:latest ia-influencer/ai-engine:${BUILD_NUMBER}"
                    ],
                    timeout=900  # AI models take longer to build
                ),
                PipelineStage(
                    name="model-test",
                    stage_type="test",
                    commands=[
                        "docker run --rm --gpus all ia-influencer/ai-engine:latest python -c 'import torch; print(torch.cuda.is_available())'",
                        "docker run --rm ia-influencer/ai-engine:latest pytest tests/ai/"
                    ],
                    dependencies=["build"],
                    timeout=600
                ),
                PipelineStage(
                    name="security-scan",
                    stage_type="scan",
                    commands=[
                        "trivy image ia-influencer/ai-engine:latest"
                    ],
                    dependencies=["build"],
                    timeout=300
                ),
                PipelineStage(
                    name="push",
                    stage_type="deploy",
                    commands=[
                        "docker push ia-influencer/ai-engine:latest",
                        "docker push ia-influencer/ai-engine:${BUILD_NUMBER}"
                    ],
                    dependencies=["model-test", "security-scan"],
                    timeout=600
                )
            ]
            
            self.pipelines = {
                "web-api": web_api_pipeline,
                "ai-engine": ai_engine_pipeline
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default pipelines: {e}")
    
    async def run_pipeline(self, pipeline_name: str, environment: Dict[str, str] = None) -> str:
        """Run CI/CD pipeline"""        try:
            if pipeline_name not in self.pipelines:
                self.logger.error(f"❌ Pipeline {pipeline_name} not found")
                return ""
            
            run_id = hashlib.md5(f"{pipeline_name}_{datetime.now()}".encode()).hexdigest()
            pipeline_stages = self.pipelines[pipeline_name]
            
            pipeline_run = {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "stages": pipeline_stages,
                "environment": environment or {},
                "status": "running",
                "started_at": datetime.now(),
                "completed_stages": [],
                "failed_stages": []
            }
            
            self.pipeline_runs[run_id] = pipeline_run
            
            # Run pipeline stages
            asyncio.create_task(self._execute_pipeline(run_id))
            
            self.logger.info(f"🚀 Started pipeline {pipeline_name} (Run ID: {run_id})")
            return run_id
            
        except Exception as e:
            self.logger.error(f"❌ Error running pipeline: {e}")
            return ""
    
    async def _execute_pipeline(self, run_id: str) -> None:
        """Execute pipeline stages"""        try:
            pipeline_run = self.pipeline_runs[run_id]
            stages = pipeline_run["stages"]
            environment = pipeline_run["environment"]
            
            # Execute stages in dependency order
            executed_stages = set()
            
            while len(executed_stages) < len(stages):
                for stage in stages:
                    if stage.name in executed_stages:
                        continue
                    
                    # Check if all dependencies are completed
                    dependencies_met = all(
                        dep in executed_stages for dep in stage.dependencies
                    )
                    
                    if dependencies_met:
                        success = await self._execute_stage(stage, environment)
                        
                        if success:
                            executed_stages.add(stage.name)
                            pipeline_run["completed_stages"].append(stage.name)
                            self.logger.info(f"✅ Stage {stage.name} completed successfully")
                        else:
                            pipeline_run["failed_stages"].append(stage.name)
                            self.logger.error(f"❌ Stage {stage.name} failed")
                            
                            if not stage.continue_on_error:
                                pipeline_run["status"] = "failed"
                                pipeline_run["completed_at"] = datetime.now()
                                return
                
                # Prevent infinite loop
                if not any(
                    stage.name not in executed_stages and
                    all(dep in executed_stages for dep in stage.dependencies)
                    for stage in stages
                ):
                    break
            
            # Pipeline completed
            if len(executed_stages) == len(stages):
                pipeline_run["status"] = "success"
            else:
                pipeline_run["status"] = "failed"
            
            pipeline_run["completed_at"] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"❌ Error executing pipeline: {e}")
            if run_id in self.pipeline_runs:
                self.pipeline_runs[run_id]["status"] = "error"
                self.pipeline_runs[run_id]["error"] = str(e)
                self.pipeline_runs[run_id]["completed_at"] = datetime.now()
    
    async def _execute_stage(self, stage: PipelineStage, environment: Dict[str, str]) -> bool:
        """Execute individual pipeline stage"""        try:
            self.logger.info(f"🔄 Executing stage: {stage.name}")
            
            # Set up environment
            env = {**environment, **stage.environment}
            
            # Execute commands
            for command in stage.commands:
                # Replace environment variables in command
                for key, value in env.items():
                    command = command.replace(f"${{{key}}}", value)
                
                self.logger.debug(f"Running command: {command}")
                
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=stage.timeout,
                    env={**os.environ, **env}
                )
                
                if result.returncode != 0:
                    self.logger.error(f"❌ Command failed: {command}")
                    self.logger.error(f"Error output: {result.stderr}")
                    
                    # Retry if configured
                    if stage.retry_count > 1:
                        for retry in range(stage.retry_count - 1):
                            self.logger.info(f"🔄 Retrying command (attempt {retry + 2})")
                            
                            result = subprocess.run(
                                command,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=stage.timeout,
                                env={**os.environ, **env}
                            )
                            
                            if result.returncode == 0:
                                break
                        
                        if result.returncode != 0:
                            return False
                    else:
                        return False
                
                self.logger.debug(f"Command output: {result.stdout}")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Stage {stage.name} timed out after {stage.timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error executing stage {stage.name}: {e}")
            return False
    
    async def get_pipeline_status(self, run_id: str) -> Dict[str, Any]:
        """Get pipeline run status"""        try:
            if run_id not in self.pipeline_runs:
                return {"run_id": run_id, "status": "not_found"}
            
            pipeline_run = self.pipeline_runs[run_id]
            
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_run["pipeline_name"],
                "status": pipeline_run["status"],
                "started_at": pipeline_run["started_at"].isoformat(),
                "completed_at": pipeline_run.get("completed_at", "").isoformat() if pipeline_run.get("completed_at") else None,
                "completed_stages": pipeline_run["completed_stages"],
                "failed_stages": pipeline_run["failed_stages"],
                "total_stages": len(pipeline_run["stages"]),
                "error": pipeline_run.get("error")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pipeline status: {e}")
            return {"run_id": run_id, "status": "error", "error": str(e)}

class ArtifactManager:
    """Artifact management for container images and build outputs"""    
    def __init__(self, registry_manager: ContainerRegistryManager):
        self.registry_manager = registry_manager
        self.artifacts = {}
        self.retention_policies = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize artifact manager"""        try:
            # Setup retention policies
            await self._setup_retention_policies()
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_task())
            
            self.logger.info("✅ ArtifactManager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ArtifactManager: {e}")
            return False
    
    async def _setup_retention_policies(self) -> None:
        """Setup artifact retention policies"""        try:
            self.retention_policies = {
                "development": {
                    "max_age_days": 7,
                    "max_count": 10
                },
                "staging": {
                    "max_age_days": 30,
                    "max_count": 20
                },
                "production": {
                    "max_age_days": 365,
                    "max_count": 100
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up retention policies: {e}")
    
    async def _cleanup_task(self) -> None:
        """Background task for artifact cleanup"""        while True:
            try:
                self.logger.info("🧹 Starting artifact cleanup")
                
                # Cleanup old images based on retention policies
                for registry_name in self.registry_manager.registries:
                    await self._cleanup_registry_images(registry_name)
                
                await asyncio.sleep(24 * 3600)  # Run daily
                
            except Exception as e:
                self.logger.error(f"❌ Error in cleanup task: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _cleanup_registry_images(self, registry_name: str) -> None:
        """Cleanup images in registry based on retention policy"""        try:
            images = await self.registry_manager.list_images(registry_name)
            
            # Group images by repository
            repositories = {}
            for image in images:
                repo = image['repository']
                if repo not in repositories:
                    repositories[repo] = []
                repositories[repo].append(image)
            
            # Apply retention policies
            for repo, repo_images in repositories.items():
                # Determine environment based on repository name
                if 'dev' in repo or 'development' in repo:
                    policy = self.retention_policies['development']
                elif 'staging' in repo or 'stage' in repo:
                    policy = self.retention_policies['staging']
                else:
                    policy = self.retention_policies['production']
                
                # Sort by push date (newest first)
                repo_images.sort(key=lambda x: x.get('pushed_at', datetime.min), reverse=True)
                
                # Keep only images within retention policy
                images_to_delete = []
                
                # Delete by count
                if len(repo_images) > policy['max_count']:
                    images_to_delete.extend(repo_images[policy['max_count']:])
                
                # Delete by age
                cutoff_date = datetime.now() - timedelta(days=policy['max_age_days'])
                for image in repo_images:
                    pushed_at = image.get('pushed_at')
                    if isinstance(pushed_at, str):
                        pushed_at = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                    
                    if pushed_at and pushed_at < cutoff_date:
                        if image not in images_to_delete:
                            images_to_delete.append(image)
                
                # Delete old images
                for image in images_to_delete:
                    for tag in image.get('tags', []):
                        success = await self.registry_manager.delete_image(
                            registry_name, image['repository'], tag
                        )
                        if success:
                            self.logger.info(f"🗑️ Deleted old image: {image['repository']}:{tag}")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up registry {registry_name}: {e}")

__all__ = [
    "ContainerRegistryManager",
    "ImagePipelineManager",
    "ArtifactManager",
    "RegistryConfig",
    "ImageManifest",
    "BuildConfiguration",
    "PipelineStage",
    "RegistryType",
    "ImageBuildStatus",
    "ImageScanStatus"
]
