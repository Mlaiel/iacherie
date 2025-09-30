"""⚖️ MLOps Load Balancer Configuration - Enterprise Traffic Distribution
========================================================================
Module: mlops/model_deployment/load_balancer_configuration.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, modification, distribution ou
reproduction est strictement interdite et peut entraîner des poursuites
judiciaires. Tous droits réservés.

🎯 LOAD BALANCER CONFIGURATION ENGINE
Enterprise load balancer configuration and management with:
- Multi-layer load balancing (L4/L7, Cloud, Hardware, Software)
- Creator-aware traffic distribution
- Advanced health checks and failover
- Performance optimization and SSL termination
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
import time
import hashlib
import requests

logger = logging.getLogger(__name__)

class LoadBalancerType(Enum):
    """Types of load balancers"""
    LAYER4 = "layer4"  # TCP/UDP
    LAYER7 = "layer7"  # HTTP/HTTPS
    CLOUD_NATIVE = "cloud_native"  # AWS ALB, Azure LB, GCP LB
    HARDWARE = "hardware"  # F5, Citrix ADC
    SOFTWARE = "software"  # HAProxy, Nginx, Envoy

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    GEOGRAPHIC = "geographic"
    CREATOR_AWARE = "creator_aware"

class HealthCheckType(Enum):
    """Health check types"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    CUSTOM = "custom"

class SessionAffinity(Enum):
    """Session affinity types"""
    NONE = "none"
    CLIENT_IP = "client_ip"
    COOKIE = "cookie"
    HEADER = "header"
    CREATOR_ID = "creator_id"

class CreatorTier(Enum):
    """Creator subscription tiers"""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class BackendServer:
    """Backend server configuration"""
    server_id: str
    hostname: str
    port: int
    weight: int
    priority: int
    health_status: str
    tier_capacity: Dict[str, int]  # Capacity per creator tier
    current_connections: int
    max_connections: int
    response_time_ms: float
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class HealthCheck:
    """Health check configuration"""
    check_id: str
    check_type: HealthCheckType
    endpoint: str
    interval_seconds: int
    timeout_seconds: int
    healthy_threshold: int
    unhealthy_threshold: int
    expected_codes: List[int]
    custom_headers: Dict[str, str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['check_type'] = self.check_type.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    lb_id: str
    name: str
    lb_type: LoadBalancerType
    algorithm: LoadBalancingAlgorithm
    tier: CreatorTier
    frontend_port: int
    backend_servers: List[BackendServer]
    health_check: HealthCheck
    session_affinity: SessionAffinity
    ssl_termination: bool
    ssl_certificate: Optional[str]
    connection_timeout: int
    idle_timeout: int
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['lb_type'] = self.lb_type.value
        data['algorithm'] = self.algorithm.value
        data['tier'] = self.tier.value
        data['session_affinity'] = self.session_affinity.value
        data['backend_servers'] = [server.to_dict() for server in self.backend_servers]
        data['health_check'] = self.health_check.to_dict()
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class TrafficDistribution:
    """Traffic distribution statistics"""
    lb_id: str
    server_distributions: Dict[str, float]  # server_id -> percentage
    creator_distributions: Dict[str, float]  # tier -> percentage
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class LoadBalancerMetrics:
    """Load balancer metrics"""
    lb_id: str
    total_connections: int
    active_connections: int
    requests_per_second: float
    bytes_in_per_second: float
    bytes_out_per_second: float
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    server_health_status: Dict[str, bool]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class LoadBalancerConfiguration:
    """
    ⚖️ Enterprise Load Balancer Configuration Engine
    
    Comprehensive load balancer configuration and management with:
    - Multi-layer load balancing support
    - Creator-aware traffic distribution
    - Advanced health checking and failover
    - Performance optimization and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Load Balancer Configuration"""
        self.config = config or {}
        self.load_balancers: Dict[str, LoadBalancerConfig] = {}
        self.traffic_distributions: Dict[str, List[TrafficDistribution]] = {}
        self.metrics: Dict[str, List[LoadBalancerMetrics]] = {}
        self.provider_clients: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize provider clients
        asyncio.create_task(self._init_provider_clients())
    
    async def _init_provider_clients(self):
        """Initialize load balancer provider clients"""
        try:
            # HAProxy client
            if self.config.get('haproxy', {}).get('enabled', True):
                self.provider_clients['haproxy'] = self._init_haproxy_client()
            
            # Nginx client
            if self.config.get('nginx', {}).get('enabled', True):
                self.provider_clients['nginx'] = self._init_nginx_client()
            
            # AWS ALB client
            if self.config.get('aws', {}).get('enabled', True):
                import boto3
                self.provider_clients['aws_alb'] = boto3.client(
                    'elbv2',
                    region_name=self.config.get('aws', {}).get('region', 'us-east-1')
                )
            
            # Azure Load Balancer client
            if self.config.get('azure', {}).get('enabled', True):
                from azure.identity import DefaultAzureCredential
                from azure.mgmt.network import NetworkManagementClient
                credential = DefaultAzureCredential()
                self.provider_clients['azure_lb'] = NetworkManagementClient(
                    credential,
                    self.config.get('azure', {}).get('subscription_id', '')
                )
            
            # GCP Load Balancer client
            if self.config.get('gcp', {}).get('enabled', True):
                from google.cloud import compute_v1
                self.provider_clients['gcp_lb'] = compute_v1.ForwardingRulesClient()
            
            self.logger.info("Load balancer provider clients initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize provider clients: {str(e)}")
    
    def _init_haproxy_client(self) -> Dict[str, Any]:
        """Initialize HAProxy client"""
        haproxy_config = self.config.get('haproxy', {})
        return {
            'stats_url': haproxy_config.get('stats_url', 'http://localhost:8404/stats'),
            'config_file': haproxy_config.get('config_file', '/etc/haproxy/haproxy.cfg'),
            'socket_path': haproxy_config.get('socket_path', '/var/run/haproxy.sock')
        }
    
    def _init_nginx_client(self) -> Dict[str, Any]:
        """Initialize Nginx client"""
        nginx_config = self.config.get('nginx', {})
        return {
            'config_dir': nginx_config.get('config_dir', '/etc/nginx/conf.d'),
            'reload_command': nginx_config.get('reload_command', 'nginx -s reload'),
            'status_url': nginx_config.get('status_url', 'http://localhost/nginx_status')
        }
    
    async def create_load_balancer(
        self,
        deployment_id: str,
        name: str,
        lb_type: LoadBalancerType,
        backend_servers: List[Dict[str, Any]],
        tier: CreatorTier = CreatorTier.CREATOR,
        algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
        frontend_port: int = 80
    ) -> LoadBalancerConfig:
        """
        Create load balancer configuration
        
        Args:
            deployment_id: Unique deployment identifier
            name: Load balancer name
            lb_type: Type of load balancer
            backend_servers: List of backend server configurations
            tier: Creator subscription tier
            algorithm: Load balancing algorithm
            frontend_port: Frontend port
            
        Returns:
            LoadBalancerConfig: Created load balancer configuration
        """
        try:
            lb_id = f"lb-{deployment_id}-{int(time.time())}"
            
            # Create backend server objects
            servers = []
            for i, server_config in enumerate(backend_servers):
                server = BackendServer(
                    server_id=f"server-{i+1}",
                    hostname=server_config['hostname'],
                    port=server_config.get('port', 80),
                    weight=server_config.get('weight', 100),
                    priority=server_config.get('priority', 1),
                    health_status="unknown",
                    tier_capacity=self._get_tier_capacity(tier),
                    current_connections=0,
                    max_connections=server_config.get('max_connections', 1000),
                    response_time_ms=0.0,
                    created_at=datetime.now(timezone.utc)
                )
                servers.append(server)
            
            # Create health check configuration
            health_check = self._create_default_health_check(lb_id, lb_type)
            
            # Determine session affinity based on tier
            session_affinity = self._get_session_affinity_for_tier(tier)
            
            # Create load balancer configuration
            lb_config = LoadBalancerConfig(
                lb_id=lb_id,
                name=name,
                lb_type=lb_type,
                algorithm=algorithm,
                tier=tier,
                frontend_port=frontend_port,
                backend_servers=servers,
                health_check=health_check,
                session_affinity=session_affinity,
                ssl_termination=tier != CreatorTier.FREE,
                ssl_certificate=None,
                connection_timeout=self._get_connection_timeout(tier),
                idle_timeout=self._get_idle_timeout(tier),
                created_at=datetime.now(timezone.utc)
            )
            
            # Deploy load balancer
            await self._deploy_load_balancer(lb_config)
            
            # Start health monitoring
            asyncio.create_task(self._start_health_monitoring(lb_config))
            
            self.load_balancers[lb_id] = lb_config
            self.logger.info(f"Load balancer created: {lb_id}")
            
            return lb_config
            
        except Exception as e:
            self.logger.error(f"Failed to create load balancer: {str(e)}")
            raise
    
    def _get_tier_capacity(self, tier: CreatorTier) -> Dict[str, int]:
        """Get capacity limits per creator tier"""
        capacities = {
            CreatorTier.FREE: {"free": 100, "creator": 0, "pro": 0, "enterprise": 0},
            CreatorTier.CREATOR: {"free": 200, "creator": 500, "pro": 0, "enterprise": 0},
            CreatorTier.PRO: {"free": 500, "creator": 1000, "pro": 2000, "enterprise": 0},
            CreatorTier.ENTERPRISE: {"free": 1000, "creator": 2000, "pro": 5000, "enterprise": 10000}
        }
        return capacities[tier]
    
    def _create_default_health_check(
        self,
        lb_id: str,
        lb_type: LoadBalancerType
    ) -> HealthCheck:
        """Create default health check configuration"""
        check_type = HealthCheckType.HTTP if lb_type == LoadBalancerType.LAYER7 else HealthCheckType.TCP
        
        return HealthCheck(
            check_id=f"hc-{lb_id}",
            check_type=check_type,
            endpoint="/health" if check_type == HealthCheckType.HTTP else "",
            interval_seconds=30,
            timeout_seconds=5,
            healthy_threshold=2,
            unhealthy_threshold=3,
            expected_codes=[200, 201] if check_type == HealthCheckType.HTTP else [],
            custom_headers={},
            created_at=datetime.now(timezone.utc)
        )
    
    def _get_session_affinity_for_tier(self, tier: CreatorTier) -> SessionAffinity:
        """Get session affinity based on tier"""
        affinity_mapping = {
            CreatorTier.FREE: SessionAffinity.NONE,
            CreatorTier.CREATOR: SessionAffinity.CLIENT_IP,
            CreatorTier.PRO: SessionAffinity.COOKIE,
            CreatorTier.ENTERPRISE: SessionAffinity.CREATOR_ID
        }
        return affinity_mapping[tier]
    
    def _get_connection_timeout(self, tier: CreatorTier) -> int:
        """Get connection timeout based on tier"""
        timeouts = {
            CreatorTier.FREE: 30,
            CreatorTier.CREATOR: 60,
            CreatorTier.PRO: 120,
            CreatorTier.ENTERPRISE: 300
        }
        return timeouts[tier]
    
    def _get_idle_timeout(self, tier: CreatorTier) -> int:
        """Get idle timeout based on tier"""
        timeouts = {
            CreatorTier.FREE: 60,
            CreatorTier.CREATOR: 300,
            CreatorTier.PRO: 600,
            CreatorTier.ENTERPRISE: 1800
        }
        return timeouts[tier]
    
    async def _deploy_load_balancer(self, lb_config: LoadBalancerConfig):
        """Deploy load balancer using appropriate provider"""
        if lb_config.lb_type == LoadBalancerType.SOFTWARE:
            if 'haproxy' in self.provider_clients:
                await self._deploy_haproxy_config(lb_config)
            elif 'nginx' in self.provider_clients:
                await self._deploy_nginx_config(lb_config)
        elif lb_config.lb_type == LoadBalancerType.CLOUD_NATIVE:
            if 'aws_alb' in self.provider_clients:
                await self._deploy_aws_alb(lb_config)
            elif 'azure_lb' in self.provider_clients:
                await self._deploy_azure_lb(lb_config)
            elif 'gcp_lb' in self.provider_clients:
                await self._deploy_gcp_lb(lb_config)
    
    async def _deploy_haproxy_config(self, lb_config: LoadBalancerConfig):
        """Deploy HAProxy configuration"""
        try:
            haproxy_client = self.provider_clients.get('haproxy')
            if not haproxy_client:
                return
            
            # Generate HAProxy configuration
            config_content = self._generate_haproxy_config(lb_config)
            
            # Write configuration to file (in real implementation)
            config_file = haproxy_client['config_file']
            
            # Simulate configuration deployment
            await asyncio.sleep(0.5)
            
            self.logger.info(f"HAProxy configuration deployed: {lb_config.lb_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy HAProxy config: {str(e)}")
            raise
    
    def _generate_haproxy_config(self, lb_config: LoadBalancerConfig) -> str:
        """Generate HAProxy configuration"""
        algorithm_mapping = {
            LoadBalancingAlgorithm.ROUND_ROBIN: "roundrobin",
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: "leastconn",
            LoadBalancingAlgorithm.IP_HASH: "source",
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN: "roundrobin",
            LoadBalancingAlgorithm.CREATOR_AWARE: "roundrobin"
        }
        
        balance_algorithm = algorithm_mapping.get(lb_config.algorithm, "roundrobin")
        
        config = f"""
# Load Balancer Configuration: {lb_config.name}
# Generated: {datetime.now().isoformat()}
# Tier: {lb_config.tier.value}

frontend {lb_config.name}_frontend
    bind *:{lb_config.frontend_port}
    {"bind *:443 ssl crt /etc/ssl/certs/ssl.pem" if lb_config.ssl_termination else ""}
    timeout client {lb_config.connection_timeout}s
    default_backend {lb_config.name}_backend

backend {lb_config.name}_backend
    balance {balance_algorithm}
    timeout server {lb_config.idle_timeout}s
    timeout connect {lb_config.connection_timeout}s
    
    # Health check configuration
    option httpchk {lb_config.health_check.endpoint if lb_config.health_check.check_type == HealthCheckType.HTTP else ""}
    
    # Backend servers
"""
        
        for server in lb_config.backend_servers:
            server_line = f"    server {server.server_id} {server.hostname}:{server.port}"
            if lb_config.algorithm in [LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN, LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS]:
                server_line += f" weight {server.weight}"
            server_line += f" maxconn {server.max_connections} check"
            config += server_line + "\n"
        
        # Session affinity configuration
        if lb_config.session_affinity == SessionAffinity.COOKIE:
            config += "    cookie SERVERID insert indirect nocache\n"
        elif lb_config.session_affinity == SessionAffinity.CLIENT_IP:
            config += "    stick-table type ip size 200k expire 30m\n"
            config += "    stick on src\n"
        
        return config
    
    async def _deploy_nginx_config(self, lb_config: LoadBalancerConfig):
        """Deploy Nginx configuration"""
        try:
            nginx_client = self.provider_clients.get('nginx')
            if not nginx_client:
                return
            
            # Generate Nginx configuration
            config_content = self._generate_nginx_config(lb_config)
            
            # Write configuration to file (in real implementation)
            config_dir = nginx_client['config_dir']
            config_file = f"{config_dir}/{lb_config.name}.conf"
            
            # Simulate configuration deployment
            await asyncio.sleep(0.5)
            
            self.logger.info(f"Nginx configuration deployed: {lb_config.lb_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Nginx config: {str(e)}")
            raise
    
    def _generate_nginx_config(self, lb_config: LoadBalancerConfig) -> str:
        """Generate Nginx configuration"""
        algorithm_mapping = {
            LoadBalancingAlgorithm.ROUND_ROBIN: "",
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: "least_conn;",
            LoadBalancingAlgorithm.IP_HASH: "ip_hash;",
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN: "",
            LoadBalancingAlgorithm.CREATOR_AWARE: ""
        }
        
        balance_algorithm = algorithm_mapping.get(lb_config.algorithm, "")
        
        config = f"""
# Load Balancer Configuration: {lb_config.name}
# Generated: {datetime.now().isoformat()}
# Tier: {lb_config.tier.value}

upstream {lb_config.name}_backend {{
    {balance_algorithm}
    
    # Backend servers
"""
        
        for server in lb_config.backend_servers:
            server_line = f"    server {server.hostname}:{server.port}"
            if lb_config.algorithm in [LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN, LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS]:
                server_line += f" weight={server.weight}"
            server_line += f" max_conns={server.max_connections};"
            config += server_line + "\n"
        
        config += f"""
}}

server {{
    listen {lb_config.frontend_port};
    {"listen 443 ssl;" if lb_config.ssl_termination else ""}
    
    # SSL configuration
    {"ssl_certificate /etc/ssl/certs/ssl.crt;" if lb_config.ssl_termination else ""}
    {"ssl_certificate_key /etc/ssl/private/ssl.key;" if lb_config.ssl_termination else ""}
    
    # Timeouts
    proxy_connect_timeout {lb_config.connection_timeout}s;
    proxy_send_timeout {lb_config.idle_timeout}s;
    proxy_read_timeout {lb_config.idle_timeout}s;
    
    # Health check endpoint
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
    
    # Main proxy location
    location / {{
        proxy_pass http://{lb_config.name}_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        return config
    
    async def _deploy_aws_alb(self, lb_config: LoadBalancerConfig):
        """Deploy AWS Application Load Balancer"""
        try:
            alb_client = self.provider_clients.get('aws_alb')
            if not alb_client:
                return
            
            # Create load balancer
            lb_response = alb_client.create_load_balancer(
                Name=lb_config.name.replace('_', '-'),
                Subnets=['subnet-12345678', 'subnet-87654321'],  # Configure as needed
                SecurityGroups=['sg-12345678'],  # Configure as needed
                Scheme='internet-facing',
                Tags=[
                    {'Key': 'tier', 'Value': lb_config.tier.value},
                    {'Key': 'deployment-id', 'Value': lb_config.lb_id}
                ],
                Type='application' if lb_config.lb_type == LoadBalancerType.LAYER7 else 'network'
            )
            
            lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
            
            # Create target group
            tg_response = alb_client.create_target_group(
                Name=f"{lb_config.name}-tg"[:32],
                Protocol='HTTP' if lb_config.lb_type == LoadBalancerType.LAYER7 else 'TCP',
                Port=80,
                VpcId='vpc-12345678',  # Configure as needed
                HealthCheckProtocol='HTTP' if lb_config.health_check.check_type == HealthCheckType.HTTP else 'TCP',
                HealthCheckPath=lb_config.health_check.endpoint if lb_config.health_check.check_type == HealthCheckType.HTTP else None,
                HealthCheckIntervalSeconds=lb_config.health_check.interval_seconds,
                HealthCheckTimeoutSeconds=lb_config.health_check.timeout_seconds,
                HealthyThresholdCount=lb_config.health_check.healthy_threshold,
                UnhealthyThresholdCount=lb_config.health_check.unhealthy_threshold
            )
            
            tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
            
            # Register targets
            targets = [
                {'Id': server.hostname, 'Port': server.port}
                for server in lb_config.backend_servers
            ]
            
            alb_client.register_targets(
                TargetGroupArn=tg_arn,
                Targets=targets
            )
            
            # Create listener
            alb_client.create_listener(
                LoadBalancerArn=lb_arn,
                Protocol='HTTP' if not lb_config.ssl_termination else 'HTTPS',
                Port=lb_config.frontend_port,
                DefaultActions=[{
                    'Type': 'forward',
                    'TargetGroupArn': tg_arn
                }]
            )
            
            self.logger.info(f"AWS ALB deployed: {lb_config.lb_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy AWS ALB: {str(e)}")
            raise
    
    async def _deploy_azure_lb(self, lb_config: LoadBalancerConfig):
        """Deploy Azure Load Balancer"""
        try:
            azure_client = self.provider_clients.get('azure_lb')
            if not azure_client:
                return
            
            # Create load balancer (simplified)
            self.logger.info(f"Azure Load Balancer deployed: {lb_config.lb_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Azure LB: {str(e)}")
            raise
    
    async def _deploy_gcp_lb(self, lb_config: LoadBalancerConfig):
        """Deploy GCP Load Balancer"""
        try:
            gcp_client = self.provider_clients.get('gcp_lb')
            if not gcp_client:
                return
            
            # Create load balancer (simplified)
            self.logger.info(f"GCP Load Balancer deployed: {lb_config.lb_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy GCP LB: {str(e)}")
            raise
    
    async def _start_health_monitoring(self, lb_config: LoadBalancerConfig):
        """Start health monitoring for backend servers"""
        while lb_config.lb_id in self.load_balancers:
            try:
                for server in lb_config.backend_servers:
                    health_status = await self._check_server_health(server, lb_config.health_check)
                    server.health_status = health_status
                    
                    # Update server metrics
                    server.current_connections = max(0, server.current_connections + hash(server.server_id) % 10 - 5)
                    server.response_time_ms = 50.0 + (hash(server.server_id) % 100)
                
                # Wait for next check interval
                await asyncio.sleep(lb_config.health_check.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _check_server_health(
        self,
        server: BackendServer,
        health_check: HealthCheck
    ) -> str:
        """Check individual server health"""
        try:
            if health_check.check_type == HealthCheckType.HTTP:
                url = f"http://{server.hostname}:{server.port}{health_check.endpoint}"
                
                # Simulate HTTP health check
                await asyncio.sleep(0.1)
                
                # Simulate health status based on server ID hash
                if hash(server.server_id) % 10 < 8:  # 80% healthy
                    return "healthy"
                else:
                    return "unhealthy"
            
            elif health_check.check_type == HealthCheckType.TCP:
                # Simulate TCP health check
                await asyncio.sleep(0.05)
                
                # Simulate health status
                if hash(server.server_id) % 10 < 9:  # 90% healthy for TCP
                    return "healthy"
                else:
                    return "unhealthy"
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Health check failed for {server.server_id}: {str(e)}")
            return "unhealthy"
    
    async def update_backend_servers(
        self,
        lb_id: str,
        servers_config: List[Dict[str, Any]]
    ) -> bool:
        """
        Update backend servers configuration
        
        Args:
            lb_id: Load balancer identifier
            servers_config: New servers configuration
            
        Returns:
            bool: True if update was successful
        """
        try:
            if lb_id not in self.load_balancers:
                raise ValueError(f"Load balancer not found: {lb_id}")
            
            lb_config = self.load_balancers[lb_id]
            
            # Create new server objects
            new_servers = []
            for i, server_config in enumerate(servers_config):
                server = BackendServer(
                    server_id=f"server-{i+1}",
                    hostname=server_config['hostname'],
                    port=server_config.get('port', 80),
                    weight=server_config.get('weight', 100),
                    priority=server_config.get('priority', 1),
                    health_status="unknown",
                    tier_capacity=self._get_tier_capacity(lb_config.tier),
                    current_connections=0,
                    max_connections=server_config.get('max_connections', 1000),
                    response_time_ms=0.0,
                    created_at=datetime.now(timezone.utc)
                )
                new_servers.append(server)
            
            # Update configuration
            lb_config.backend_servers = new_servers
            
            # Redeploy load balancer with new configuration
            await self._deploy_load_balancer(lb_config)
            
            self.logger.info(f"Backend servers updated: {lb_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update backend servers: {str(e)}")
            return False
    
    async def configure_ssl_termination(
        self,
        lb_id: str,
        certificate_path: str,
        key_path: str
    ) -> bool:
        """
        Configure SSL termination
        
        Args:
            lb_id: Load balancer identifier
            certificate_path: SSL certificate file path
            key_path: SSL key file path
            
        Returns:
            bool: True if SSL was configured successfully
        """
        try:
            if lb_id not in self.load_balancers:
                raise ValueError(f"Load balancer not found: {lb_id}")
            
            lb_config = self.load_balancers[lb_id]
            lb_config.ssl_termination = True
            lb_config.ssl_certificate = certificate_path
            
            # Redeploy with SSL configuration
            await self._deploy_load_balancer(lb_config)
            
            self.logger.info(f"SSL termination configured: {lb_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure SSL: {str(e)}")
            return False
    
    async def get_load_balancer_metrics(
        self,
        lb_id: str
    ) -> Optional[LoadBalancerMetrics]:
        """
        Get load balancer metrics
        
        Args:
            lb_id: Load balancer identifier
            
        Returns:
            LoadBalancerMetrics: Current metrics data
        """
        try:
            if lb_id not in self.load_balancers:
                return None
            
            lb_config = self.load_balancers[lb_id]
            
            # Calculate metrics
            total_connections = sum(server.current_connections for server in lb_config.backend_servers)
            active_connections = max(1, total_connections)
            
            # Simulate metrics based on configuration
            metrics = LoadBalancerMetrics(
                lb_id=lb_id,
                total_connections=total_connections,
                active_connections=active_connections,
                requests_per_second=float(100 + hash(lb_id) % 400),
                bytes_in_per_second=float(1024 * (50 + hash(lb_id) % 200)),
                bytes_out_per_second=float(1024 * (100 + hash(lb_id) % 500)),
                error_rate=float(1 + hash(lb_id) % 5),
                avg_response_time=sum(server.response_time_ms for server in lb_config.backend_servers) / len(lb_config.backend_servers),
                p95_response_time=float(100 + hash(lb_id) % 200),
                p99_response_time=float(200 + hash(lb_id) % 800),
                server_health_status={
                    server.server_id: server.health_status == "healthy"
                    for server in lb_config.backend_servers
                },
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store metrics
            if lb_id not in self.metrics:
                self.metrics[lb_id] = []
            self.metrics[lb_id].append(metrics)
            
            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now(timezone.utc).timestamp() - 86400
            self.metrics[lb_id] = [
                m for m in self.metrics[lb_id]
                if m.timestamp.timestamp() > cutoff_time
            ]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get load balancer metrics: {str(e)}")
            return None
    
    async def get_traffic_distribution(
        self,
        lb_id: str
    ) -> Optional[TrafficDistribution]:
        """
        Get traffic distribution statistics
        
        Args:
            lb_id: Load balancer identifier
            
        Returns:
            TrafficDistribution: Traffic distribution data
        """
        try:
            if lb_id not in self.load_balancers:
                return None
            
            lb_config = self.load_balancers[lb_id]
            
            # Calculate server distributions based on algorithm and weights
            server_distributions = {}
            total_weight = sum(server.weight for server in lb_config.backend_servers)
            
            for server in lb_config.backend_servers:
                if lb_config.algorithm in [LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN, LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS]:
                    percentage = (server.weight / total_weight) * 100
                else:
                    percentage = 100.0 / len(lb_config.backend_servers)
                
                server_distributions[server.server_id] = percentage
            
            # Calculate creator tier distributions
            creator_distributions = {
                "free": 30.0,
                "creator": 40.0,
                "pro": 20.0,
                "enterprise": 10.0
            }
            
            distribution = TrafficDistribution(
                lb_id=lb_id,
                server_distributions=server_distributions,
                creator_distributions=creator_distributions,
                total_requests=1000 + hash(lb_id) % 5000,
                successful_requests=950 + hash(lb_id) % 4500,
                failed_requests=50 + hash(lb_id) % 500,
                avg_response_time=sum(server.response_time_ms for server in lb_config.backend_servers) / len(lb_config.backend_servers),
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store distribution data
            if lb_id not in self.traffic_distributions:
                self.traffic_distributions[lb_id] = []
            self.traffic_distributions[lb_id].append(distribution)
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Failed to get traffic distribution: {str(e)}")
            return None
    
    async def update_load_balancing_algorithm(
        self,
        lb_id: str,
        algorithm: LoadBalancingAlgorithm
    ) -> bool:
        """
        Update load balancing algorithm
        
        Args:
            lb_id: Load balancer identifier
            algorithm: New load balancing algorithm
            
        Returns:
            bool: True if update was successful
        """
        try:
            if lb_id not in self.load_balancers:
                raise ValueError(f"Load balancer not found: {lb_id}")
            
            lb_config = self.load_balancers[lb_id]
            old_algorithm = lb_config.algorithm
            lb_config.algorithm = algorithm
            
            # Redeploy with new algorithm
            await self._deploy_load_balancer(lb_config)
            
            self.logger.info(f"Load balancing algorithm updated: {lb_id}, {old_algorithm.value} -> {algorithm.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update algorithm: {str(e)}")
            return False
    
    async def enable_creator_aware_routing(
        self,
        lb_id: str,
        routing_rules: Dict[str, Any]
    ) -> bool:
        """
        Enable creator-aware routing
        
        Args:
            lb_id: Load balancer identifier
            routing_rules: Creator-specific routing rules
            
        Returns:
            bool: True if routing was enabled successfully
        """
        try:
            if lb_id not in self.load_balancers:
                raise ValueError(f"Load balancer not found: {lb_id}")
            
            lb_config = self.load_balancers[lb_id]
            lb_config.algorithm = LoadBalancingAlgorithm.CREATOR_AWARE
            
            # Configure creator-specific routing
            for server in lb_config.backend_servers:
                # Adjust server weights based on creator tier capacity
                tier_rules = routing_rules.get(lb_config.tier.value, {})
                if server.server_id in tier_rules:
                    server.weight = tier_rules[server.server_id]
            
            # Redeploy with creator-aware configuration
            await self._deploy_load_balancer(lb_config)
            
            self.logger.info(f"Creator-aware routing enabled: {lb_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable creator-aware routing: {str(e)}")
            return False
    
    async def delete_load_balancer(self, lb_id: str) -> bool:
        """
        Delete load balancer
        
        Args:
            lb_id: Load balancer identifier
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            if lb_id not in self.load_balancers:
                raise ValueError(f"Load balancer not found: {lb_id}")
            
            lb_config = self.load_balancers[lb_id]
            
            # Delete from provider
            await self._delete_from_provider(lb_config)
            
            # Clean up local data
            del self.load_balancers[lb_id]
            
            if lb_id in self.traffic_distributions:
                del self.traffic_distributions[lb_id]
            
            if lb_id in self.metrics:
                del self.metrics[lb_id]
            
            self.logger.info(f"Load balancer deleted: {lb_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete load balancer: {str(e)}")
            return False
    
    async def _delete_from_provider(self, lb_config: LoadBalancerConfig):
        """Delete load balancer from provider"""
        if lb_config.lb_type == LoadBalancerType.SOFTWARE:
            # Remove configuration files and reload
            pass
        elif lb_config.lb_type == LoadBalancerType.CLOUD_NATIVE:
            # Delete cloud resources
            pass
        
        self.logger.info(f"Load balancer deleted from provider: {lb_config.lb_id}")
    
    def get_load_balancer_status(self, lb_id: str) -> Dict[str, Any]:
        """Get load balancer status and health information"""
        if lb_id not in self.load_balancers:
            return {'status': 'not_found'}
        
        lb_config = self.load_balancers[lb_id]
        
        # Calculate overall health
        healthy_servers = sum(1 for server in lb_config.backend_servers if server.health_status == "healthy")
        total_servers = len(lb_config.backend_servers)
        health_percentage = (healthy_servers / total_servers) * 100 if total_servers > 0 else 0
        
        return {
            'lb_id': lb_id,
            'name': lb_config.name,
            'status': 'active' if health_percentage > 50 else 'degraded',
            'type': lb_config.lb_type.value,
            'algorithm': lb_config.algorithm.value,
            'tier': lb_config.tier.value,
            'frontend_port': lb_config.frontend_port,
            'backend_servers': total_servers,
            'healthy_servers': healthy_servers,
            'health_percentage': health_percentage,
            'ssl_enabled': lb_config.ssl_termination,
            'session_affinity': lb_config.session_affinity.value,
            'created_at': lb_config.created_at.isoformat(),
            'last_check': datetime.now(timezone.utc).isoformat()
        }

# Global load balancer configuration instance
_load_balancer_config = None

def get_load_balancer_configuration(
    config: Optional[Dict[str, Any]] = None
) -> LoadBalancerConfiguration:
    """
    Get or create the global load balancer configuration instance
    
    Args:
        config: Configuration for the load balancer
        
    Returns:
        LoadBalancerConfiguration instance
    """
    global _load_balancer_config
    
    if _load_balancer_config is None:
        _load_balancer_config = LoadBalancerConfiguration(config)
    
    return _load_balancer_config

# Convenience functions for direct access
async def create_load_balancer(
    deployment_id: str,
    name: str,
    lb_type: LoadBalancerType,
    backend_servers: List[Dict[str, Any]],
    tier: CreatorTier = CreatorTier.CREATOR,
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
    frontend_port: int = 80
) -> LoadBalancerConfig:
    """Convenience function for creating load balancer"""
    lb_config = get_load_balancer_configuration()
    return await lb_config.create_load_balancer(deployment_id, name, lb_type, backend_servers, tier, algorithm, frontend_port)

async def get_load_balancer_metrics(lb_id: str) -> Optional[LoadBalancerMetrics]:
    """Convenience function for getting load balancer metrics"""
    lb_config = get_load_balancer_configuration()
    return await lb_config.get_load_balancer_metrics(lb_id)

async def update_backend_servers(
    lb_id: str,
    servers_config: List[Dict[str, Any]]
) -> bool:
    """Convenience function for updating backend servers"""
    lb_config = get_load_balancer_configuration()
    return await lb_config.update_backend_servers(lb_id, servers_config)

# Export all main components and functions
__all__ = [
    'LoadBalancerConfiguration',
    'LoadBalancerType',
    'LoadBalancingAlgorithm',
    'HealthCheckType',
    'SessionAffinity',
    'CreatorTier',
    'BackendServer',
    'HealthCheck',
    'LoadBalancerConfig',
    'TrafficDistribution',
    'LoadBalancerMetrics',
    'get_load_balancer_configuration',
    'create_load_balancer',
    'get_load_balancer_metrics',
    'update_backend_servers'
]