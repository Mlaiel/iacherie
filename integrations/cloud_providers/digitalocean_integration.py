"""DigitalOcean Integration
==========================

Enterprise-grade DigitalOcean integration supporting droplets,
spaces, databases, and cloud services for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

import httpx
import boto3  # For S3-compatible Spaces API
from botocore.exceptions import ClientError, NoCredentialsError


class DOServiceType(Enum):
    """DigitalOcean service types."""
    DROPLETS = "droplets"
    SPACES = "spaces"
    DATABASES = "databases"
    LOAD_BALANCERS = "load_balancers"
    VOLUMES = "volumes"
    KUBERNETES = "kubernetes"
    APP_PLATFORM = "app_platform"
    CDN = "cdn"
    MONITORING = "monitoring"


class DORegion(Enum):
    """DigitalOcean regions."""
    NYC1 = "nyc1"
    NYC3 = "nyc3"
    AMS3 = "ams3"
    SFO3 = "sfo3"
    SGP1 = "sgp1"
    LON1 = "lon1"
    FRA1 = "fra1"
    TOR1 = "tor1"
    BLR1 = "blr1"
    SYD1 = "syd1"


class DODropletSize(Enum):
    """DigitalOcean droplet sizes."""
    S_1VCPU_1GB = "s-1vcpu-1gb"
    S_1VCPU_2GB = "s-1vcpu-2gb"
    S_2VCPU_2GB = "s-2vcpu-2gb"
    S_2VCPU_4GB = "s-2vcpu-4gb"
    S_4VCPU_8GB = "s-4vcpu-8gb"
    S_8VCPU_16GB = "s-8vcpu-16gb"
    C_2 = "c-2"
    C_4 = "c-4"
    C_8 = "c-8"
    M_2VCPU_16GB = "m-2vcpu-16gb"
    M_4VCPU_32GB = "m-4vcpu-32gb"


@dataclass
class DODropletRequest:
    """DigitalOcean droplet request."""
    name: str
    region: DORegion
    size: DODropletSize
    image: str
    operation: str  # create, start, stop, delete, resize
    ssh_keys: Optional[List[str]] = None
    backups: bool = False
    ipv6: bool = False
    monitoring: bool = True
    user_data: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class DOSpacesRequest:
    """DigitalOcean Spaces request."""
    space_name: str
    key: str
    operation: str  # upload, download, delete, list
    local_file_path: Optional[str] = None
    content: Optional[bytes] = None
    metadata: Optional[Dict[str, str]] = None
    acl: str = "private"
    content_type: Optional[str] = None


@dataclass
class DODatabaseRequest:
    """DigitalOcean database request."""
    name: str
    engine: str  # postgresql, mysql, redis, mongodb
    region: DORegion
    size: str
    num_nodes: int = 1
    operation: str  # create, resize, backup, restore, delete
    version: Optional[str] = None
    private_network_uuid: Optional[str] = None
    tags: Optional[List[str]] = None


class DigitalOceanIntegration:
    """Enterprise DigitalOcean integration for Ainflue.
    
    Features:
    - Droplets for scalable virtual machines
    - Spaces for object storage (S3-compatible)
    - Managed databases (PostgreSQL, MySQL, Redis, MongoDB)
    - Load balancers for high availability
    - Block storage volumes
    - Kubernetes clusters
    - App Platform for containerized applications
    - CDN for global content delivery
    - Monitoring and alerting
    - Auto-scaling and load distribution
    - Simple and predictable pricing
    - Developer-friendly APIs
    """
    
    def __init__(
        self,
        api_token -> None: str,
        spaces_key -> None: Optional[str] = None,
        spaces_secret -> None: Optional[str] = None,
        default_region -> None: DORegion = DORegion.NYC3
    ) -> None:
        """Initialize DigitalOcean integration.
        
        Args:
            api_token: DigitalOcean API token
            spaces_key: Spaces access key
            spaces_secret: Spaces secret key
            default_region: Default region
        """
        self.api_token = api_token
        self.spaces_key = spaces_key
        self.spaces_secret = spaces_secret
        self.default_region = default_region
        
        # Base API URL
        self.api_base_url = "https://api.digitalocean.com/v2"
        
        # Initialize Spaces client (S3-compatible)
        self.spaces_client = None
        if spaces_key and spaces_secret:
            self._init_spaces_client()
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    def _init_spaces_client(self) -> None:
        """Initialize DigitalOcean Spaces client."""
        try:
            self.spaces_client = boto3.client(
                's3',
                region_name=self.default_region.value,
                endpoint_url=f'https://{self.default_region.value}.digitaloceanspaces.com',
                aws_access_key_id=self.spaces_key,
                aws_secret_access_key=self.spaces_secret
            )
            self.logger.info("Initialized DigitalOcean Spaces client")
        except Exception as e:
            self.logger.error(f"Failed to initialize Spaces client: {e}")

    async def create_droplet(
        self,
        droplet_request: DODropletRequest
    ) -> Dict[str, Any]:
        """Create DigitalOcean droplet.
        
        Args:
            droplet_request: Droplet creation request
            
        Returns:
            Dict containing droplet details
        """
        try:
            payload = {
                "name": droplet_request.name,
                "region": droplet_request.region.value,
                "size": droplet_request.size.value,
                "image": droplet_request.image,
                "backups": droplet_request.backups,
                "ipv6": droplet_request.ipv6,
                "monitoring": droplet_request.monitoring
            }
            
            if droplet_request.ssh_keys:
                payload["ssh_keys"] = droplet_request.ssh_keys
            if droplet_request.user_data:
                payload["user_data"] = droplet_request.user_data
            if droplet_request.tags:
                payload["tags"] = droplet_request.tags
            
            response = await self.session.post(
                f"{self.api_base_url}/droplets",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            droplet = result["droplet"]
            
            droplet_info = {
                "id": droplet["id"],
                "name": droplet["name"],
                "status": droplet["status"],
                "region": droplet["region"]["name"],
                "size": droplet["size"]["slug"],
                "image": droplet["image"]["name"],
                "created_at": droplet["created_at"],
                "public_ipv4": None,
                "private_ipv4": None,
                "public_ipv6": None
            }
            
            # Extract network information
            for network in droplet.get("networks", {}).get("v4", []):
                if network["type"] == "public":
                    droplet_info["public_ipv4"] = network["ip_address"]
                elif network["type"] == "private":
                    droplet_info["private_ipv4"] = network["ip_address"]
            
            for network in droplet.get("networks", {}).get("v6", []):
                if network["type"] == "public":
                    droplet_info["public_ipv6"] = network["ip_address"]
            
            self.logger.info(f"Created DigitalOcean droplet: {droplet_request.name}")
            return droplet_info
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create droplet: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating droplet: {e}")
            raise

    async def get_droplet(
        self,
        droplet_id: int
    ) -> Dict[str, Any]:
        """Get droplet information by ID.
        
        Args:
            droplet_id: Droplet ID
            
        Returns:
            Dict containing droplet details
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/droplets/{droplet_id}"
            )
            response.raise_for_status()
            
            result = response.json()
            droplet = result["droplet"]
            
            self.logger.info(f"Retrieved droplet info: {droplet_id}")
            return droplet
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get droplet: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting droplet: {e}")
            raise

    async def list_droplets(
        self,
        tag_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all droplets.
        
        Args:
            tag_name: Filter by tag name
            
        Returns:
            List of droplet information
        """
        try:
            url = f"{self.api_base_url}/droplets"
            if tag_name:
                url += f"?tag_name={tag_name}"
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            droplets = result["droplets"]
            
            self.logger.info(f"Listed {len(droplets)} droplets")
            return droplets
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to list droplets: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error listing droplets: {e}")
            raise

    async def delete_droplet(
        self,
        droplet_id: int
    ) -> bool:
        """Delete droplet by ID.
        
        Args:
            droplet_id: Droplet ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.session.delete(
                f"{self.api_base_url}/droplets/{droplet_id}"
            )
            response.raise_for_status()
            
            self.logger.info(f"Deleted droplet: {droplet_id}")
            return True
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to delete droplet: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting droplet: {e}")
            return False

    async def upload_to_spaces(
        self,
        spaces_request: DOSpacesRequest
    ) -> Dict[str, Any]:
        """Upload file to DigitalOcean Spaces.
        
        Args:
            spaces_request: Spaces upload request
            
        Returns:
            Dict containing upload result
        """
        try:
            if not self.spaces_client:
                raise ValueError("Spaces client not initialized")
            
            # Prepare upload arguments
            upload_args = {
                'Bucket': spaces_request.space_name,
                'Key': spaces_request.key,
                'ACL': spaces_request.acl
            }
            
            if spaces_request.content_type:
                upload_args['ContentType'] = spaces_request.content_type
            
            if spaces_request.metadata:
                upload_args['Metadata'] = spaces_request.metadata
            
            # Upload content
            if spaces_request.local_file_path:
                self.spaces_client.upload_file(
                    spaces_request.local_file_path,
                    spaces_request.space_name,
                    spaces_request.key,
                    ExtraArgs={k: v for k, v in upload_args.items() if k not in ['Bucket', 'Key']}
                )
            elif spaces_request.content:
                upload_args['Body'] = spaces_request.content
                self.spaces_client.put_object(**upload_args)
            else:
                raise ValueError("Either local_file_path or content must be provided")
            
            # Generate public URL
            public_url = f"https://{spaces_request.space_name}.{self.default_region.value}.digitaloceanspaces.com/{spaces_request.key}"
            
            # Generate presigned URL for private access
            presigned_url = None
            if spaces_request.acl == "private":
                presigned_url = self.spaces_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': spaces_request.space_name, 'Key': spaces_request.key},
                    ExpiresIn=3600  # 1 hour
                )
            
            result = {
                "space_name": spaces_request.space_name,
                "key": spaces_request.key,
                "public_url": public_url if spaces_request.acl == "public-read" else None,
                "presigned_url": presigned_url,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Uploaded to Spaces: {spaces_request.key}")
            return result
            
        except ClientError as e:
            self.logger.error(f"Failed to upload to Spaces: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error uploading to Spaces: {e}")
            raise

    async def download_from_spaces(
        self,
        spaces_request: DOSpacesRequest
    ) -> bytes:
        """Download file from DigitalOcean Spaces.
        
        Args:
            spaces_request: Spaces download request
            
        Returns:
            File content as bytes
        """
        try:
            if not self.spaces_client:
                raise ValueError("Spaces client not initialized")
            
            if spaces_request.local_file_path:
                self.spaces_client.download_file(
                    spaces_request.space_name,
                    spaces_request.key,
                    spaces_request.local_file_path
                )
                
                with open(spaces_request.local_file_path, 'rb') as f:
                    content = f.read()
            else:
                response = self.spaces_client.get_object(
                    Bucket=spaces_request.space_name,
                    Key=spaces_request.key
                )
                content = response['Body'].read()
            
            self.logger.info(f"Downloaded from Spaces: {spaces_request.key}")
            return content
            
        except ClientError as e:
            self.logger.error(f"Failed to download from Spaces: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error downloading from Spaces: {e}")
            raise

    async def delete_from_spaces(
        self,
        space_name: str,
        key: str
    ) -> bool:
        """Delete file from DigitalOcean Spaces.
        
        Args:
            space_name: Space name
            key: Object key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.spaces_client:
                raise ValueError("Spaces client not initialized")
            
            self.spaces_client.delete_object(
                Bucket=space_name,
                Key=key
            )
            
            self.logger.info(f"Deleted from Spaces: {key}")
            return True
            
        except ClientError as e:
            self.logger.error(f"Failed to delete from Spaces: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting from Spaces: {e}")
            return False

    async def create_database(
        self,
        database_request: DODatabaseRequest
    ) -> Dict[str, Any]:
        """Create DigitalOcean managed database.
        
        Args:
            database_request: Database creation request
            
        Returns:
            Dict containing database details
        """
        try:
            payload = {
                "name": database_request.name,
                "engine": database_request.engine,
                "region": database_request.region.value,
                "size": database_request.size,
                "num_nodes": database_request.num_nodes
            }
            
            if database_request.version:
                payload["version"] = database_request.version
            if database_request.private_network_uuid:
                payload["private_network_uuid"] = database_request.private_network_uuid
            if database_request.tags:
                payload["tags"] = database_request.tags
            
            response = await self.session.post(
                f"{self.api_base_url}/databases",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            database = result["database"]
            
            database_info = {
                "id": database["id"],
                "name": database["name"],
                "engine": database["engine"],
                "version": database["version"],
                "status": database["status"],
                "region": database["region"]["name"],
                "size": database["size"],
                "num_nodes": database["num_nodes"],
                "created_at": database["created_at"],
                "connection": database.get("connection", {})
            }
            
            self.logger.info(f"Created DigitalOcean database: {database_request.name}")
            return database_info
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating database: {e}")
            raise

    async def create_load_balancer(
        self,
        name: str,
        algorithm: str,
        region: DORegion,
        forwarding_rules: List[Dict[str, Any]],
        health_check: Dict[str, Any],
        droplet_ids: Optional[List[int]] = None,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create DigitalOcean load balancer.
        
        Args:
            name: Load balancer name
            algorithm: Load balancing algorithm
            region: Region
            forwarding_rules: List of forwarding rules
            health_check: Health check configuration
            droplet_ids: List of droplet IDs to balance
            tag: Tag to automatically include tagged droplets
            
        Returns:
            Dict containing load balancer details
        """
        try:
            payload = {
                "name": name,
                "algorithm": algorithm,
                "region": region.value,
                "forwarding_rules": forwarding_rules,
                "health_check": health_check
            }
            
            if droplet_ids:
                payload["droplet_ids"] = droplet_ids
            if tag:
                payload["tag"] = tag
            
            response = await self.session.post(
                f"{self.api_base_url}/load_balancers",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            load_balancer = result["load_balancer"]
            
            self.logger.info(f"Created load balancer: {name}")
            return load_balancer
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create load balancer: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating load balancer: {e}")
            raise

    async def create_kubernetes_cluster(
        self,
        name: str,
        region: DORegion,
        version: str,
        node_pools: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        vpc_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create DigitalOcean Kubernetes cluster.
        
        Args:
            name: Cluster name
            region: Region
            version: Kubernetes version
            node_pools: List of node pool configurations
            tags: Cluster tags
            vpc_uuid: VPC UUID
            
        Returns:
            Dict containing cluster details
        """
        try:
            payload = {
                "name": name,
                "region": region.value,
                "version": version,
                "node_pools": node_pools
            }
            
            if tags:
                payload["tags"] = tags
            if vpc_uuid:
                payload["vpc_uuid"] = vpc_uuid
            
            response = await self.session.post(
                f"{self.api_base_url}/kubernetes/clusters",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            cluster = result["kubernetes_cluster"]
            
            self.logger.info(f"Created Kubernetes cluster: {name}")
            return cluster
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create Kubernetes cluster: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating Kubernetes cluster: {e}")
            raise

    async def get_account_info(self) -> Dict[str, Any]:
        """Get DigitalOcean account information.
        
        Returns:
            Dict containing account details
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/account"
            )
            response.raise_for_status()
            
            result = response.json()
            account = result["account"]
            
            self.logger.info("Retrieved account information")
            return account
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get account info: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting account info: {e}")
            raise

    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance information.
        
        Returns:
            Dict containing balance details
        """
        try:
            response = await self.session.get(
                f"{self.api_base_url}/customers/my/balance"
            )
            response.raise_for_status()
            
            result = response.json()
            
            self.logger.info("Retrieved account balance")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get balance: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting balance: {e}")
            raise

    async def get_monitoring_metrics(
        self,
        host_id: str,
        start: datetime,
        end: datetime,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Get monitoring metrics for a host.
        
        Args:
            host_id: Host ID (droplet ID)
            start: Start time
            end: End time
            metrics: List of metrics to retrieve
            
        Returns:
            Dict containing metrics data
        """
        try:
            params = {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "host_id": host_id
            }
            
            # Add metrics as separate parameters
            for metric in metrics:
                params[f"metrics[]"] = metric
            
            response = await self.session.get(
                f"{self.api_base_url}/monitoring/metrics/droplet/bandwidth",
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            self.logger.info(f"Retrieved monitoring metrics for host: {host_id}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get monitoring metrics: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting monitoring metrics: {e}")
            raise

    async def close(self) -> None:
        """Close HTTP session."""
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator infrastructure specific functions
async def setup_creator_infrastructure(
    do: DigitalOceanIntegration,
    creator_id: str,
    scale_tier: str = "basic"
) -> Dict[str, Any]:
    """Setup DigitalOcean infrastructure for creator.
    
    Args:
        do: DigitalOcean integration instance
        creator_id: Creator identifier
        scale_tier: Infrastructure scale tier
        
    Returns:
        Dict containing infrastructure setup details
    """
    infrastructure = {
        "creator_id": creator_id,
        "scale_tier": scale_tier,
        "components": {},
        "endpoints": {},
        "costs": {}
    }
    
    # Basic tier: Single droplet + Spaces
    if scale_tier == "basic":
        # Create content processing droplet
        droplet = await do.create_droplet(
            DODropletRequest(
                name=f"creator-{creator_id}-processor",
                region=DORegion.NYC3,
                size=DODropletSize.S_2VCPU_2GB,
                image="ubuntu-20-04-x64",
                tags=[f"creator:{creator_id}", "processor"],
                monitoring=True,
                user_data=f"""#!/bin/bash
                # Setup creator content processing environment
                apt-get update
                apt-get install -y docker.io nginx certbot python3-certbot-nginx
                systemctl enable docker
                systemctl start docker
                
                # Create creator workspace
                mkdir -p /opt/creator-{creator_id}
                echo "Creator {creator_id} processing node" > /opt/creator-{creator_id}/info.txt
                """
            )
        )
        infrastructure["components"]["processor_droplet"] = droplet
        
        # Setup Spaces for content storage
        space_name = f"creator-{creator_id}-content"
        infrastructure["components"]["content_storage"] = {
            "space_name": space_name,
            "endpoint": f"https://{space_name}.nyc3.digitaloceanspaces.com",
            "regions": ["nyc3"]
        }
        
        infrastructure["endpoints"]["api"] = f"http://{droplet.get('public_ipv4')}"
        infrastructure["endpoints"]["storage"] = f"https://{space_name}.nyc3.digitaloceanspaces.com"
        
        infrastructure["costs"]["monthly_estimate"] = {
            "droplet": 12.0,  # $12/month for s-2vcpu-2gb
            "spaces": 5.0,    # $5/month for 250GB
            "bandwidth": 0.0, # First 1TB free
            "total": 17.0
        }
    
    # Professional tier: Multiple droplets + Load balancer + Database
    elif scale_tier == "professional":
        # Create multiple processing droplets
        droplets = []
        for i in range(2):
            droplet = await do.create_droplet(
                DODropletRequest(
                    name=f"creator-{creator_id}-processor-{i+1}",
                    region=DORegion.NYC3,
                    size=DODropletSize.S_4VCPU_8GB,
                    image="ubuntu-20-04-x64",
                    tags=[f"creator:{creator_id}", "processor", "cluster"],
                    monitoring=True
                )
            )
            droplets.append(droplet)
        
        infrastructure["components"]["processor_droplets"] = droplets
        
        # Create load balancer
        load_balancer = await do.create_load_balancer(
            name=f"creator-{creator_id}-lb",
            algorithm="round_robin",
            region=DORegion.NYC3,
            forwarding_rules=[
                {
                    "entry_protocol": "http",
                    "entry_port": 80,
                    "target_protocol": "http",
                    "target_port": 80
                },
                {
                    "entry_protocol": "https",
                    "entry_port": 443,
                    "target_protocol": "http",
                    "target_port": 80,
                    "tls_passthrough": False
                }
            ],
            health_check={
                "protocol": "http",
                "port": 80,
                "path": "/health",
                "check_interval_seconds": 10,
                "response_timeout_seconds": 5,
                "healthy_threshold": 3,
                "unhealthy_threshold": 3
            },
            droplet_ids=[d["id"] for d in droplets]
        )
        infrastructure["components"]["load_balancer"] = load_balancer
        
        # Create managed database
        database = await do.create_database(
            DODatabaseRequest(
                name=f"creator-{creator_id}-db",
                engine="postgresql",
                region=DORegion.NYC3,
                size="db-s-1vcpu-1gb",
                tags=[f"creator:{creator_id}", "database"]
            )
        )
        infrastructure["components"]["database"] = database
        
        infrastructure["endpoints"]["api"] = f"http://{load_balancer.get('ip')}"
        infrastructure["endpoints"]["database"] = database.get("connection", {}).get("uri")
        
        infrastructure["costs"]["monthly_estimate"] = {
            "droplets": 48.0,      # 2 x $24/month for s-4vcpu-8gb
            "load_balancer": 12.0, # $12/month
            "database": 15.0,      # $15/month for db-s-1vcpu-1gb
            "spaces": 5.0,         # $5/month for 250GB
            "bandwidth": 0.0,      # First 1TB free
            "total": 80.0
        }
    
    return infrastructure


async def deploy_creator_app(
    do: DigitalOceanIntegration,
    creator_id: str,
    app_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Deploy creator application using DigitalOcean App Platform.
    
    Args:
        do: DigitalOcean integration instance
        creator_id: Creator identifier
        app_config: Application configuration
        
    Returns:
        Dict containing deployment details
    """
    app_spec = {
        "name": f"creator-{creator_id}-app",
        "region": "nyc",
        "services": [
            {
                "name": "web",
                "source_dir": "/",
                "github": {
                    "repo": app_config.get("repo", "creator/default-template"),
                    "branch": app_config.get("branch", "main")
                },
                "run_command": app_config.get("run_command", "npm start"),
                "environment_slug": "node-js",
                "instance_count": app_config.get("instance_count", 1),
                "instance_size_slug": app_config.get("instance_size", "basic-xxs"),
                "http_port": 8080,
                "routes": [
                    {
                        "path": "/"
                    }
                ],
                "health_check": {
                    "http_path": "/health"
                },
                "env": [
                    {
                        "key": "CREATOR_ID",
                        "value": creator_id
                    },
                    {
                        "key": "NODE_ENV",
                        "value": "production"
                    }
                ]
            }
        ]
    }
    
    # Add environment variables from config
    if "env_vars" in app_config:
        for key, value in app_config["env_vars"].items():
            app_spec["services"][0]["env"].append({
                "key": key,
                "value": value
            })
    
    # Note: This would use the App Platform API in a real implementation
    deployment_result = {
        "app_id": f"app-{uuid.uuid4()}",
        "creator_id": creator_id,
        "app_spec": app_spec,
        "status": "deploying",
        "url": f"https://creator-{creator_id}-app-random.ondigitalocean.app",
        "deployed_at": datetime.utcnow().isoformat()
    }
    
    return deployment_result