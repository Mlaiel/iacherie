"""
Vpn Gateway Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - VPN Gateway Manager
# ===================================================
# 
# Enterprise-grade VPN gateway management for Ainflue platform
# Supports multi-cloud VPN connectivity and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
VPN Gateway Manager
===================

Enterprise VPN gateway management for secure multi-cloud connectivity,
site-to-site VPN, and remote access VPN for creator economy platform.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import boto3
from azure.mgmt.network import NetworkManagementClient
from google.cloud import compute_v1
import ipaddress
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import yaml
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VPNType(Enum):
    """VPN connection types"""
    SITE_TO_SITE = "site_to_site"
    POINT_TO_SITE = "point_to_site"
    VPC_PEERING = "vpc_peering"
    TRANSIT_GATEWAY = "transit_gateway"
    SD_WAN = "sd_wan"


class VPNProtocol(Enum):
    """VPN protocols"""
    IPSEC = "ipsec"
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    SSTP = "sstp"
    L2TP = "l2tp"


class EncryptionStrength(Enum):
    """Encryption strength levels"""
    AES_128 = "aes_128"
    AES_256 = "aes_256"
    CHACHA20 = "chacha20"


@dataclass
class VPNEndpoint:
    """VPN endpoint configuration"""
    endpoint_id: str
    public_ip: str
    private_networks: List[str]
    location: str
    provider: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class VPNConnection:
    """VPN connection configuration"""
    connection_id: str
    vpn_type: VPNType
    protocol: VPNProtocol
    encryption: EncryptionStrength
    local_endpoint: VPNEndpoint
    remote_endpoint: VPNEndpoint
    pre_shared_key: str
    routes: List[str]
    bandwidth_limit: Optional[int] = None
    is_active: bool = False
    health_status: str = "unknown"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class VPNTunnel:
    """VPN tunnel status and metrics"""
    tunnel_id: str
    connection_id: str
    status: str
    uptime_seconds: int
    bytes_sent: int
    bytes_received: int
    packet_loss_pct: float
    latency_ms: float
    last_error: Optional[str] = None


class VPNGatewayManager:
    """
    Enterprise VPN Gateway Manager
    
    Provides comprehensive VPN management with:
    - Multi-cloud VPN gateway deployment
    - Site-to-site and point-to-site VPN
    - Automated certificate management
    - VPN tunnel monitoring and health checks
    - High availability and failover
    - Traffic analytics and optimization
    """
    
    def __init__(self, config_path -> None: str = None) -> None:
        """Initialize VPN gateway manager"""
        self.config_path = config_path
        self.providers = {}
        self.vpn_gateways = {}
        self.vpn_connections = {}
        self.vpn_tunnels = {}
        self.certificates = {}
        
        logger.info("VPN Gateway Manager initialized")
    
    async def initialize_providers(self, providers_config -> None: Dict[str, Any]) -> None:
        """Initialize cloud provider clients"""
        try:
            # Initialize AWS
            if 'aws' in providers_config:
                aws_config = providers_config['aws']
                self.providers['aws'] = {
                    'ec2': boto3.client('ec2', region_name=aws_config.get('region')),
                    'vpn': boto3.client('ec2', region_name=aws_config.get('region')),
                    'tgw': boto3.client('ec2', region_name=aws_config.get('region'))
                }
            
            # Initialize Azure
            if 'azure' in providers_config:
                azure_config = providers_config['azure']
                self.providers['azure'] = NetworkManagementClient(
                    credential=azure_config.get('credential'),
                    subscription_id=azure_config.get('subscription_id')
                )
            
            # Initialize GCP
            if 'gcp' in providers_config:
                gcp_config = providers_config['gcp']
                self.providers['gcp'] = {
                    'compute': compute_v1.InstancesClient(),
                    'vpn': compute_v1.VpnGatewaysClient()
                }
            
            logger.info(f"Initialized {len(self.providers)} cloud providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
            raise
    
    async def create_vpn_gateway(
        self,
        gateway_name: str,
        provider: str,
        region: str,
        gateway_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create VPN gateway on specified cloud provider"""
        try:
            logger.info(f"Creating VPN gateway {gateway_name} on {provider}")
            
            if provider == 'aws':
                gateway = await self._create_aws_vpn_gateway(
                    gateway_name, region, gateway_config
                )
            elif provider == 'azure':
                gateway = await self._create_azure_vpn_gateway(
                    gateway_name, region, gateway_config
                )
            elif provider == 'gcp':
                gateway = await self._create_gcp_vpn_gateway(
                    gateway_name, region, gateway_config
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Store gateway configuration
            self.vpn_gateways[gateway_name] = {
                'provider': provider,
                'region': region,
                'config': gateway_config,
                'gateway_info': gateway,
                'created_at': asyncio.get_event_loop().time()
            }
            
            # Setup monitoring for the gateway
            await self._setup_gateway_monitoring(gateway_name, gateway)
            
            logger.info(f"Successfully created VPN gateway {gateway_name}")
            return gateway
            
        except Exception as e:
            logger.error(f"Failed to create VPN gateway {gateway_name}: {e}")
            raise
    
    async def create_site_to_site_vpn(
        self,
        connection_name: str,
        local_gateway: str,
        remote_endpoint: VPNEndpoint,
        vpn_config: Dict[str, Any]
    ) -> VPNConnection:
        """Create site-to-site VPN connection"""
        try:
            logger.info(f"Creating site-to-site VPN connection {connection_name}")
            
            # Validate local gateway exists
            if local_gateway not in self.vpn_gateways:
                raise ValueError(f"Local gateway {local_gateway} not found")
            
            gateway_info = self.vpn_gateways[local_gateway]
            provider = gateway_info['provider']
            
            # Generate pre-shared key if not provided
            if 'pre_shared_key' not in vpn_config:
                vpn_config['pre_shared_key'] = await self._generate_pre_shared_key()
            
            # Create VPN connection based on provider
            if provider == 'aws':
                connection_result = await self._create_aws_site_to_site_vpn(
                    connection_name, gateway_info, remote_endpoint, vpn_config
                )
            elif provider == 'azure':
                connection_result = await self._create_azure_site_to_site_vpn(
                    connection_name, gateway_info, remote_endpoint, vpn_config
                )
            elif provider == 'gcp':
                connection_result = await self._create_gcp_site_to_site_vpn(
                    connection_name, gateway_info, remote_endpoint, vpn_config
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Create VPN connection object
            local_endpoint = VPNEndpoint(
                endpoint_id=local_gateway,
                public_ip=gateway_info['gateway_info'].get('public_ip', ''),
                private_networks=vpn_config.get('local_networks', []),
                location=gateway_info['region'],
                provider=provider
            )
            
            vpn_connection = VPNConnection(
                connection_id=connection_name,
                vpn_type=VPNType.SITE_TO_SITE,
                protocol=VPNProtocol(vpn_config.get('protocol', 'ipsec')),
                encryption=EncryptionStrength(vpn_config.get('encryption', 'aes_256')),
                local_endpoint=local_endpoint,
                remote_endpoint=remote_endpoint,
                pre_shared_key=vpn_config['pre_shared_key'],
                routes=vpn_config.get('routes', []),
                bandwidth_limit=vpn_config.get('bandwidth_limit'),
                tags=vpn_config.get('tags', {})
            )
            
            # Store connection
            self.vpn_connections[connection_name] = vpn_connection
            
            # Setup connection monitoring
            await self._setup_connection_monitoring(connection_name, connection_result)
            
            # Configure routing
            await self._configure_vpn_routing(vpn_connection)
            
            logger.info(f"Successfully created site-to-site VPN {connection_name}")
            return vpn_connection
            
        except Exception as e:
            logger.error(f"Failed to create site-to-site VPN {connection_name}: {e}")
            raise
    
    async def create_point_to_site_vpn(
        self,
        vpn_name: str,
        gateway_name: str,
        client_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create point-to-site VPN for remote access"""
        try:
            logger.info(f"Creating point-to-site VPN {vpn_name}")
            
            # Validate gateway exists
            if gateway_name not in self.vpn_gateways:
                raise ValueError(f"Gateway {gateway_name} not found")
            
            gateway_info = self.vpn_gateways[gateway_name]
            provider = gateway_info['provider']
            
            # Generate client certificates
            client_certs = await self._generate_client_certificates(
                vpn_name, client_config.get('client_count', 1)
            )
            
            # Create point-to-site VPN based on provider
            if provider == 'aws':
                vpn_result = await self._create_aws_point_to_site_vpn(
                    vpn_name, gateway_info, client_config, client_certs
                )
            elif provider == 'azure':
                vpn_result = await self._create_azure_point_to_site_vpn(
                    vpn_name, gateway_info, client_config, client_certs
                )
            elif provider == 'gcp':
                vpn_result = await self._create_gcp_point_to_site_vpn(
                    vpn_name, gateway_info, client_config, client_certs
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Store certificates
            self.certificates[vpn_name] = client_certs
            
            # Setup user management
            await self._setup_vpn_user_management(vpn_name, client_config)
            
            logger.info(f"Successfully created point-to-site VPN {vpn_name}")
            
            return {
                'vpn_name': vpn_name,
                'vpn_result': vpn_result,
                'client_certificates': client_certs,
                'client_config_files': await self._generate_client_config_files(
                    vpn_name, vpn_result, client_certs
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to create point-to-site VPN {vpn_name}: {e}")
            raise
    
    async def configure_vpn_routing(
        self,
        connection_name: str,
        routing_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure advanced VPN routing"""
        try:
            logger.info(f"Configuring VPN routing for {connection_name}")
            
            if connection_name not in self.vpn_connections:
                raise ValueError(f"VPN connection {connection_name} not found")
            
            vpn_connection = self.vpn_connections[connection_name]
            provider = vpn_connection.local_endpoint.provider
            
            # Configure provider-specific routing
            if provider == 'aws':
                routing_result = await self._configure_aws_vpn_routing(
                    vpn_connection, routing_config
                )
            elif provider == 'azure':
                routing_result = await self._configure_azure_vpn_routing(
                    vpn_connection, routing_config
                )
            elif provider == 'gcp':
                routing_result = await self._configure_gcp_vpn_routing(
                    vpn_connection, routing_config
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Update connection routes
            vpn_connection.routes.extend(routing_config.get('additional_routes', []))
            
            logger.info(f"VPN routing configured for {connection_name}")
            return routing_result
            
        except Exception as e:
            logger.error(f"Failed to configure VPN routing for {connection_name}: {e}")
            raise
    
    async def monitor_vpn_tunnels(self) -> Dict[str, List[VPNTunnel]]:
        """Monitor all VPN tunnel health and performance"""
        try:
            logger.info("Monitoring VPN tunnel health")
            
            tunnel_status = {}
            
            for connection_name, vpn_connection in self.vpn_connections.items():
                provider = vpn_connection.local_endpoint.provider
                
                # Get tunnel metrics based on provider
                if provider == 'aws':
                    tunnels = await self._monitor_aws_vpn_tunnels(connection_name)
                elif provider == 'azure':
                    tunnels = await self._monitor_azure_vpn_tunnels(connection_name)
                elif provider == 'gcp':
                    tunnels = await self._monitor_gcp_vpn_tunnels(connection_name)
                else:
                    continue
                
                tunnel_status[connection_name] = tunnels
                
                # Update tunnel health status
                for tunnel in tunnels:
                    self.vpn_tunnels[tunnel.tunnel_id] = tunnel
                    
                    # Check for issues and trigger alerts if needed
                    if tunnel.packet_loss_pct > 5.0 or tunnel.latency_ms > 200:
                        await self._trigger_tunnel_alert(tunnel)
            
            logger.info(f"Monitored {sum(len(tunnels) for tunnels in tunnel_status.values())} VPN tunnels")
            return tunnel_status
            
        except Exception as e:
            logger.error(f"VPN tunnel monitoring failed: {e}")
            raise
    
    async def optimize_vpn_performance(
        self,
        connection_name: str,
        optimization_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize VPN connection performance"""
        try:
            logger.info(f"Optimizing VPN performance for {connection_name}")
            
            if connection_name not in self.vpn_connections:
                raise ValueError(f"VPN connection {connection_name} not found")
            
            vpn_connection = self.vpn_connections[connection_name]
            
            # Analyze current performance
            performance_metrics = await self._analyze_vpn_performance(connection_name)
            
            # Generate optimization recommendations
            optimizations = await self._generate_vpn_optimizations(
                vpn_connection, performance_metrics, optimization_config or {}
            )
            
            # Apply optimizations
            optimization_results = {}
            
            for optimization in optimizations:
                try:
                    result = await self._apply_vpn_optimization(
                        connection_name, optimization
                    )
                    optimization_results[optimization['type']] = result
                except Exception as e:
                    logger.warning(f"Failed to apply optimization {optimization['type']}: {e}")
                    optimization_results[optimization['type']] = {'error': str(e)}
            
            logger.info(f"VPN performance optimization completed for {connection_name}")
            
            return {
                'connection_name': connection_name,
                'performance_metrics': performance_metrics,
                'optimizations_applied': optimization_results,
                'expected_improvements': await self._calculate_performance_improvements(
                    optimizations, performance_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"VPN performance optimization failed: {e}")
            raise
    
    async def setup_vpn_failover(
        self,
        primary_connection: str,
        backup_connection: str,
        failover_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup VPN failover between connections"""
        try:
            logger.info(f"Setting up VPN failover: {primary_connection} -> {backup_connection}")
            
            # Validate both connections exist
            if primary_connection not in self.vpn_connections:
                raise ValueError(f"Primary connection {primary_connection} not found")
            if backup_connection not in self.vpn_connections:
                raise ValueError(f"Backup connection {backup_connection} not found")
            
            primary_vpn = self.vpn_connections[primary_connection]
            backup_vpn = self.vpn_connections[backup_connection]
            
            # Configure failover monitoring
            failover_monitor = await self._setup_failover_monitoring(
                primary_connection, backup_connection, failover_config
            )
            
            # Configure automatic routing updates
            routing_automation = await self._setup_failover_routing_automation(
                primary_vpn, backup_vpn, failover_config
            )
            
            # Setup health checks
            health_checks = await self._setup_failover_health_checks(
                primary_connection, backup_connection, failover_config
            )
            
            failover_setup = {
                'primary_connection': primary_connection,
                'backup_connection': backup_connection,
                'failover_monitor': failover_monitor,
                'routing_automation': routing_automation,
                'health_checks': health_checks,
                'failover_threshold': failover_config.get('failover_threshold', 30),
                'automatic_failback': failover_config.get('automatic_failback', True)
            }
            
            logger.info(f"VPN failover setup completed")
            return failover_setup
            
        except Exception as e:
            logger.error(f"VPN failover setup failed: {e}")
            raise
    
    # AWS-specific implementations
    async def _create_aws_vpn_gateway(
        self,
        gateway_name: str,
        region: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create AWS VPN gateway"""
        try:
            ec2 = self.providers['aws']['ec2']
            
            # Create VPC if not provided
            vpc_id = config.get('vpc_id')
            if not vpc_id:
                vpc_response = ec2.create_vpc(CidrBlock=config.get('vpc_cidr', '10.0.0.0/16'))
                vpc_id = vpc_response['Vpc']['VpcId']
            
            # Create Customer Gateway for remote endpoint
            if 'customer_gateway_ip' in config:
                cgw_response = ec2.create_customer_gateway(
                    Type='ipsec.1',
                    PublicIp=config['customer_gateway_ip'],
                    BgpAsn=config.get('bgp_asn', 65000)
                )
                customer_gateway_id = cgw_response['CustomerGateway']['CustomerGatewayId']
            else:
                customer_gateway_id = None
            
            # Create VPN Gateway
            vgw_response = ec2.create_vpn_gateway(
                Type='ipsec.1',
                TagSpecifications=[{
                    'ResourceType': 'vpn-gateway',
                    'Tags': [
                        {'Key': 'Name', 'Value': gateway_name},
                        {'Key': 'Environment', 'Value': config.get('environment', 'production')}
                    ]
                }]
            )
            
            vpn_gateway_id = vgw_response['VpnGateway']['VpnGatewayId']
            
            # Attach VPN Gateway to VPC
            ec2.attach_vpn_gateway(VpcId=vpc_id, VpnGatewayId=vpn_gateway_id)
            
            return {
                'vpn_gateway_id': vpn_gateway_id,
                'vpc_id': vpc_id,
                'customer_gateway_id': customer_gateway_id,
                'state': 'pending'
            }
            
        except Exception as e:
            logger.error(f"AWS VPN gateway creation failed: {e}")
            raise
    
    async def _generate_pre_shared_key(self) -> str:
        """Generate secure pre-shared key"""
        import secrets
        import string
        
        # Generate 32-character random key
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    async def _generate_client_certificates(
        self,
        vpn_name: str,
        client_count: int
    ) -> Dict[str, Any]:
        """Generate client certificates for point-to-site VPN"""
        try:
            certificates = {}
            
            # Generate CA certificate
            ca_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            ca_cert = x509.CertificateBuilder().subject_name(
                x509.Name([
                    x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                    x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                    x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Ainflue"),
                    x509.NameAttribute(x509.NameOID.COMMON_NAME, f"{vpn_name}-ca"),
                ])
            ).issuer_name(
                x509.Name([
                    x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                    x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                    x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Ainflue"),
                    x509.NameAttribute(x509.NameOID.COMMON_NAME, f"{vpn_name}-ca"),
                ])
            ).public_key(
                ca_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=3650)  # 10 years
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).sign(ca_key, hashes.SHA256())
            
            certificates['ca'] = {
                'certificate': ca_cert.public_bytes(serialization.Encoding.PEM),
                'private_key': ca_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            }
            
            # Generate client certificates
            certificates['clients'] = []
            for i in range(client_count):
                client_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                
                client_cert = x509.CertificateBuilder().subject_name(
                    x509.Name([
                        x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                        x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                        x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Ainflue"),
                        x509.NameAttribute(x509.NameOID.COMMON_NAME, f"{vpn_name}-client-{i+1}"),
                    ])
                ).issuer_name(
                    ca_cert.subject
                ).public_key(
                    client_key.public_key()
                ).serial_number(
                    x509.random_serial_number()
                ).not_valid_before(
                    datetime.utcnow()
                ).not_valid_after(
                    datetime.utcnow() + timedelta(days=365)  # 1 year
                ).sign(ca_key, hashes.SHA256())
                
                certificates['clients'].append({
                    'client_id': f"client-{i+1}",
                    'certificate': client_cert.public_bytes(serialization.Encoding.PEM),
                    'private_key': client_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                })
            
            return certificates
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            raise
    
    async def get_vpn_analytics(
        self,
        connection_name: str = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive VPN analytics"""
        try:
            logger.info(f"Generating VPN analytics for {connection_name or 'all connections'}")
            
            analytics = {
                'time_range_hours': time_range_hours,
                'generated_at': datetime.now().isoformat(),
                'connections': {},
                'summary': {}
            }
            
            connections_to_analyze = [connection_name] if connection_name else list(self.vpn_connections.keys())
            
            total_bytes_sent = 0
            total_bytes_received = 0
            total_tunnels = 0
            active_tunnels = 0
            
            for conn_name in connections_to_analyze:
                if conn_name not in self.vpn_connections:
                    continue
                
                vpn_connection = self.vpn_connections[conn_name]
                
                # Get tunnel metrics
                tunnel_metrics = await self._get_connection_tunnel_metrics(conn_name, time_range_hours)
                
                # Calculate connection statistics
                conn_analytics = {
                    'connection_name': conn_name,
                    'connection_type': vpn_connection.vpn_type.value,
                    'protocol': vpn_connection.protocol.value,
                    'is_active': vpn_connection.is_active,
                    'tunnel_count': len(tunnel_metrics),
                    'active_tunnels': len([t for t in tunnel_metrics if t.status == 'up']),
                    'total_bytes_sent': sum(t.bytes_sent for t in tunnel_metrics),
                    'total_bytes_received': sum(t.bytes_received for t in tunnel_metrics),
                    'average_latency_ms': np.mean([t.latency_ms for t in tunnel_metrics]) if tunnel_metrics else 0,
                    'average_packet_loss_pct': np.mean([t.packet_loss_pct for t in tunnel_metrics]) if tunnel_metrics else 0,
                    'uptime_percentage': await self._calculate_connection_uptime(conn_name, time_range_hours)
                }
                
                analytics['connections'][conn_name] = conn_analytics
                
                # Update totals
                total_bytes_sent += conn_analytics['total_bytes_sent']
                total_bytes_received += conn_analytics['total_bytes_received']
                total_tunnels += conn_analytics['tunnel_count']
                active_tunnels += conn_analytics['active_tunnels']
            
            # Generate summary
            analytics['summary'] = {
                'total_connections': len(connections_to_analyze),
                'active_connections': len([
                    c for c in analytics['connections'].values() 
                    if c['is_active']
                ]),
                'total_tunnels': total_tunnels,
                'active_tunnels': active_tunnels,
                'total_data_sent_gb': total_bytes_sent / (1024**3),
                'total_data_received_gb': total_bytes_received / (1024**3),
                'overall_availability_pct': np.mean([
                    c['uptime_percentage'] for c in analytics['connections'].values()
                ]) if analytics['connections'] else 0
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"VPN analytics generation failed: {e}")
            raise
    
    async def cleanup_vpn_resources(self, connection_name: str = None) -> Dict[str, bool]:
        """Cleanup VPN resources"""
        try:
            cleanup_results = {}
            
            connections_to_cleanup = [connection_name] if connection_name else list(self.vpn_connections.keys())
            
            for conn_name in connections_to_cleanup:
                try:
                    if conn_name not in self.vpn_connections:
                        cleanup_results[conn_name] = True
                        continue
                    
                    vpn_connection = self.vpn_connections[conn_name]
                    provider = vpn_connection.local_endpoint.provider
                    
                    # Provider-specific cleanup
                    if provider == 'aws':
                        await self._cleanup_aws_vpn_resources(conn_name)
                    elif provider == 'azure':
                        await self._cleanup_azure_vpn_resources(conn_name)
                    elif provider == 'gcp':
                        await self._cleanup_gcp_vpn_resources(conn_name)
                    
                    # Remove from tracking
                    del self.vpn_connections[conn_name]
                    
                    # Remove associated tunnels
                    tunnels_to_remove = [
                        tid for tid, tunnel in self.vpn_tunnels.items()
                        if tunnel.connection_id == conn_name
                    ]
                    for tunnel_id in tunnels_to_remove:
                        del self.vpn_tunnels[tunnel_id]
                    
                    cleanup_results[conn_name] = True
                    logger.info(f"Successfully cleaned up VPN connection {conn_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to cleanup VPN connection {conn_name}: {e}")
                    cleanup_results[conn_name] = False
            
            return cleanup_results
            
        except Exception as e:
            logger.error(f"VPN cleanup failed: {e}")
            raise


# Creator Economy specific VPN configurations
CREATOR_VPN_CONFIGS = {
    'main_office': {
        'vpn_type': VPNType.SITE_TO_SITE,
        'protocol': VPNProtocol.IPSEC,
        'encryption': EncryptionStrength.AES_256,
        'bandwidth_limit': 1000,  # Mbps
        'local_networks': ['10.0.0.0/16'],
        'routes': ['172.16.0.0/12'],
        'tags': {'purpose': 'main-office', 'priority': 'high'}
    },
    'remote_workers': {
        'vpn_type': VPNType.POINT_TO_SITE,
        'protocol': VPNProtocol.OPENVPN,
        'encryption': EncryptionStrength.AES_256,
        'client_count': 100,
        'address_pool': '192.168.100.0/24',
        'tags': {'purpose': 'remote-access', 'priority': 'medium'}
    },
    'content_creators': {
        'vpn_type': VPNType.POINT_TO_SITE,
        'protocol': VPNProtocol.WIREGUARD,
        'encryption': EncryptionStrength.CHACHA20,
        'client_count': 1000,
        'address_pool': '192.168.200.0/22',
        'tags': {'purpose': 'creator-access', 'priority': 'high'}
    }
}


async def main() -> None:
    """Example usage of VPN Gateway Manager"""
    vpn_manager = VPNGatewayManager()
    
    # Initialize cloud providers
    providers_config = {
        'aws': {'region': 'us-east-1'},
        'azure': {'subscription_id': 'your-subscription'},
        'gcp': {'project_id': 'your-project'}
    }
    
    await vpn_manager.initialize_providers(providers_config)
    
    # Create VPN gateway
    gateway = await vpn_manager.create_vpn_gateway(
        'ainflue-main-gateway',
        'aws',
        'us-east-1',
        {'vpc_cidr': '10.0.0.0/16', 'environment': 'production'}
    )
    
    # Create site-to-site VPN
    remote_endpoint = VPNEndpoint(
        endpoint_id='remote-office',
        public_ip='203.0.113.1',
        private_networks=['192.168.1.0/24'],
        location='remote-office',
        provider='on-premise'
    )
    
    vpn_connection = await vpn_manager.create_site_to_site_vpn(
        'main-to-remote',
        'ainflue-main-gateway',
        remote_endpoint,
        CREATOR_VPN_CONFIGS['main_office']
    )
    
    print(f"Created VPN connection: {vpn_connection.connection_id}")


if __name__ == "__main__":
    # Fix datetime import
    from datetime import datetime, timedelta
    asyncio.run(main())