# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
VPN Gateway Manager

Enterprise VPN gateway management system for secure remote connectivity.
Provides comprehensive VPN solution management across multiple cloud providers.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import json
import secrets
import hashlib
import boto3
from google.cloud import compute_v1
from azure.mgmt.network import NetworkManagementClient
from azure.identity import DefaultAzureCredential


class VPNType(Enum):
    """VPN gateway types"""
    SITE_TO_SITE = "site_to_site"
    POINT_TO_SITE = "point_to_site"
    CLIENTLESS_SSL = "clientless_ssl"
    IPSEC = "ipsec"
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"


class VPNProtocol(Enum):
    """VPN protocols"""
    IPSEC = "ipsec"
    SSTP = "sstp"
    IKEV2 = "ikev2"
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    L2TP = "l2tp"


class VPNStatus(Enum):
    """VPN gateway status"""
    CREATING = "creating"
    AVAILABLE = "available"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"


class AuthenticationMethod(Enum):
    """VPN authentication methods"""
    PSK = "pre_shared_key"
    CERTIFICATE = "certificate"
    RADIUS = "radius"
    LDAP = "ldap"
    LOCAL_USER = "local_user"
    TWO_FACTOR = "two_factor"


@dataclass
class VPNConfiguration:
    """VPN gateway configuration"""
    name: str
    vpn_type: VPNType
    protocol: VPNProtocol
    vpc_id: str
    subnet_id: str
    provider: str  # aws, gcp, azure
    region: str
    
    # Network configuration
    local_cidr: str  # Local network CIDR
    remote_cidr: Optional[str] = None  # Remote network CIDR (for site-to-site)
    remote_gateway_ip: Optional[str] = None  # Remote gateway IP
    
    # Authentication
    authentication_method: AuthenticationMethod = AuthenticationMethod.PSK
    pre_shared_key: Optional[str] = None
    certificate_arn: Optional[str] = None
    
    # Encryption
    encryption_algorithm: str = "AES256"
    hash_algorithm: str = "SHA256"
    dh_group: int = 14
    
    # Client configuration (for point-to-site)
    client_cidr: Optional[str] = None  # IP pool for VPN clients
    max_clients: int = 100
    
    # Advanced options
    enable_bgp: bool = False
    bgp_asn: Optional[int] = None
    enable_dead_peer_detection: bool = True
    tunnel_idle_timeout: int = 3600  # seconds
    
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class VPNTunnel:
    """VPN tunnel information"""
    id: str
    name: str
    gateway_id: str
    status: VPNStatus
    local_ip: str
    remote_ip: str
    local_cidr: str
    remote_cidr: str
    protocol: VPNProtocol
    encryption: str
    connected_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    bytes_in: int = 0
    bytes_out: int = 0
    packets_in: int = 0
    packets_out: int = 0


@dataclass
class VPNClient:
    """VPN client connection"""
    id: str
    username: str
    client_ip: str
    gateway_id: str
    connected_at: datetime
    last_activity: datetime
    bytes_transferred: int = 0
    session_duration: int = 0  # seconds
    client_certificate: Optional[str] = None
    client_os: Optional[str] = None


@dataclass
class VPNGateway:
    """VPN gateway instance"""
    id: str
    name: str
    vpn_type: VPNType
    protocol: VPNProtocol
    provider: str
    region: str
    vpc_id: str
    subnet_id: str
    status: VPNStatus
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    local_cidr: str = ""
    client_cidr: Optional[str] = None
    max_clients: int = 100
    current_clients: int = 0
    tunnels: List[VPNTunnel] = field(default_factory=list)
    connected_clients: List[VPNClient] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Security settings
    authentication_method: AuthenticationMethod = AuthenticationMethod.PSK
    encryption_algorithm: str = "AES256"
    hash_algorithm: str = "SHA256"
    
    # Monitoring
    connection_logs: List[Dict[str, Any]] = field(default_factory=list)
    bandwidth_usage: Dict[str, int] = field(default_factory=dict)


class VPNGatewayManager:
    """
    Enterprise VPN gateway management system
    
    Provides comprehensive VPN gateway management including:
    - Multi-cloud VPN gateway provisioning
    - Site-to-site and point-to-site VPN connections
    - Client certificate management
    - Connection monitoring and analytics
    - Security policy enforcement
    - Bandwidth management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.gateways: Dict[str, VPNGateway] = {}
        
        # Initialize cloud provider clients
        self._initialize_cloud_clients()
        
        # Certificate management
        self.certificates: Dict[str, Dict[str, Any]] = {}
        
        # Connection tracking
        self.active_connections: Dict[str, VPNClient] = {}
        
        # Configuration
        self.max_log_entries = self.config.get('max_log_entries', 10000)
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
    
    def _initialize_cloud_clients(self):
        """Initialize cloud provider clients"""
        
        # AWS client
        try:
            aws_config = self.config.get('aws', {})
            self.aws_ec2 = boto3.client(
                'ec2',
                region_name=aws_config.get('region', 'us-east-1'),
                aws_access_key_id=aws_config.get('access_key_id'),
                aws_secret_access_key=aws_config.get('secret_access_key')
            )
            self.logger.info("AWS EC2 client initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize AWS client: {str(e)}")
            self.aws_ec2 = None
        
        # GCP client
        try:
            gcp_config = self.config.get('gcp', {})
            if gcp_config.get('project_id'):
                self.gcp_compute = compute_v1.VpnGatewaysClient()
                self.gcp_project_id = gcp_config['project_id']
                self.logger.info("GCP Compute client initialized")
            else:
                self.gcp_compute = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize GCP client: {str(e)}")
            self.gcp_compute = None
        
        # Azure client
        try:
            azure_config = self.config.get('azure', {})
            if azure_config.get('subscription_id'):
                credential = DefaultAzureCredential()
                self.azure_network = NetworkManagementClient(
                    credential, 
                    azure_config['subscription_id']
                )
                self.azure_subscription_id = azure_config['subscription_id']
                self.logger.info("Azure Network client initialized")
            else:
                self.azure_network = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize Azure client: {str(e)}")
            self.azure_network = None
    
    async def create_vpn_gateway(self, config: VPNConfiguration) -> VPNGateway:
        """
        Create a new VPN gateway
        
        Args:
            config: VPN gateway configuration
            
        Returns:
            Created VPN gateway instance
        """
        self.logger.info(f"Creating VPN gateway '{config.name}' in {config.provider}")
        
        # Validate configuration
        self._validate_vpn_configuration(config)
        
        # Generate pre-shared key if not provided
        if config.authentication_method == AuthenticationMethod.PSK and not config.pre_shared_key:
            config.pre_shared_key = self._generate_pre_shared_key()
        
        # Create VPN gateway based on provider
        if config.provider == "aws":
            gateway = await self._create_aws_vpn_gateway(config)
        elif config.provider == "gcp":
            gateway = await self._create_gcp_vpn_gateway(config)
        elif config.provider == "azure":
            gateway = await self._create_azure_vpn_gateway(config)
        else:
            raise ValueError(f"Unsupported cloud provider: {config.provider}")
        
        # Store gateway instance
        self.gateways[gateway.id] = gateway
        
        # Start monitoring if enabled
        if self.monitoring_enabled:
            asyncio.create_task(self._monitor_gateway(gateway.id))
        
        self.logger.info(f"Successfully created VPN gateway {gateway.id} ({gateway.name})")
        
        return gateway
    
    def _validate_vpn_configuration(self, config: VPNConfiguration):
        """Validate VPN configuration"""
        
        # Validate CIDR blocks
        try:
            ipaddress.ip_network(config.local_cidr, strict=False)
        except ValueError:
            raise ValueError(f"Invalid local CIDR: {config.local_cidr}")
        
        if config.remote_cidr:
            try:
                ipaddress.ip_network(config.remote_cidr, strict=False)
            except ValueError:
                raise ValueError(f"Invalid remote CIDR: {config.remote_cidr}")
        
        if config.client_cidr:
            try:
                ipaddress.ip_network(config.client_cidr, strict=False)
            except ValueError:
                raise ValueError(f"Invalid client CIDR: {config.client_cidr}")
        
        # Validate remote gateway IP
        if config.remote_gateway_ip:
            try:
                ipaddress.ip_address(config.remote_gateway_ip)
            except ValueError:
                raise ValueError(f"Invalid remote gateway IP: {config.remote_gateway_ip}")
        
        # Validate BGP ASN
        if config.enable_bgp and config.bgp_asn:
            if not (1 <= config.bgp_asn <= 4294967295):
                raise ValueError("BGP ASN must be between 1 and 4294967295")
        
        # Validate max clients
        if config.max_clients <= 0 or config.max_clients > 10000:
            raise ValueError("Max clients must be between 1 and 10000")
    
    def _generate_pre_shared_key(self) -> str:
        """Generate a secure pre-shared key"""
        return secrets.token_urlsafe(32)
    
    async def _create_aws_vpn_gateway(self, config: VPNConfiguration) -> VPNGateway:
        """Create AWS VPN gateway"""
        
        if not self.aws_ec2:
            raise RuntimeError("AWS client not initialized")
        
        try:
            if config.vpn_type == VPNType.SITE_TO_SITE:
                # Create Virtual Private Gateway
                vpn_gw_response = self.aws_ec2.create_vpn_gateway(
                    Type='ipsec.1',
                    TagSpecifications=[{
                        'ResourceType': 'vpn-gateway',
                        'Tags': [
                            {'Key': 'Name', 'Value': config.name},
                            *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                        ]
                    }]
                )
                vpn_gw_id = vpn_gw_response['VpnGateway']['VpnGatewayId']
                
                # Attach to VPC
                self.aws_ec2.attach_vpn_gateway(
                    VpnGatewayId=vpn_gw_id,
                    VpcId=config.vpc_id
                )
                
                # Create Customer Gateway if remote IP provided
                cgw_id = None
                if config.remote_gateway_ip:
                    cgw_response = self.aws_ec2.create_customer_gateway(
                        Type='ipsec.1',
                        PublicIp=config.remote_gateway_ip,
                        BgpAsn=config.bgp_asn or 65000,
                        TagSpecifications=[{
                            'ResourceType': 'customer-gateway',
                            'Tags': [
                                {'Key': 'Name', 'Value': f"{config.name}-cgw"},
                                *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                            ]
                        }]
                    )
                    cgw_id = cgw_response['CustomerGateway']['CustomerGatewayId']
                    
                    # Create VPN Connection
                    vpn_conn_response = self.aws_ec2.create_vpn_connection(
                        Type='ipsec.1',
                        CustomerGatewayId=cgw_id,
                        VpnGatewayId=vpn_gw_id,
                        StaticRoutesOnly=not config.enable_bgp,
                        TagSpecifications=[{
                            'ResourceType': 'vpn-connection',
                            'Tags': [
                                {'Key': 'Name', 'Value': f"{config.name}-conn"},
                                *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                            ]
                        }]
                    )
                
                gateway = VPNGateway(
                    id=vpn_gw_id,
                    name=config.name,
                    vpn_type=config.vpn_type,
                    protocol=config.protocol,
                    provider="aws",
                    region=config.region,
                    vpc_id=config.vpc_id,
                    subnet_id=config.subnet_id,
                    status=VPNStatus.CREATING,
                    local_cidr=config.local_cidr,
                    authentication_method=config.authentication_method,
                    encryption_algorithm=config.encryption_algorithm,
                    hash_algorithm=config.hash_algorithm,
                    tags=config.tags
                )
            
            elif config.vpn_type == VPNType.POINT_TO_SITE:
                # For point-to-site, use Client VPN endpoint
                client_vpn_response = self.aws_ec2.create_client_vpn_endpoint(
                    ClientCidrBlock=config.client_cidr or "10.0.0.0/16",
                    ServerCertificateArn=config.certificate_arn or "arn:aws:acm:region:account:certificate/cert-id",
                    AuthenticationOptions=[{
                        'Type': 'certificate-authentication',
                        'MutualAuthentication': {
                            'ClientRootCertificateChainArn': config.certificate_arn or "arn:aws:acm:region:account:certificate/cert-id"
                        }
                    }],
                    ConnectionLogOptions={
                        'Enabled': True
                    },
                    TagSpecifications=[{
                        'ResourceType': 'client-vpn-endpoint',
                        'Tags': [
                            {'Key': 'Name', 'Value': config.name},
                            *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                        ]
                    }]
                )
                
                endpoint_id = client_vpn_response['ClientVpnEndpointId']
                
                gateway = VPNGateway(
                    id=endpoint_id,
                    name=config.name,
                    vpn_type=config.vpn_type,
                    protocol=config.protocol,
                    provider="aws",
                    region=config.region,
                    vpc_id=config.vpc_id,
                    subnet_id=config.subnet_id,
                    status=VPNStatus.CREATING,
                    local_cidr=config.local_cidr,
                    client_cidr=config.client_cidr,
                    max_clients=config.max_clients,
                    authentication_method=config.authentication_method,
                    encryption_algorithm=config.encryption_algorithm,
                    hash_algorithm=config.hash_algorithm,
                    tags=config.tags
                )
            
            else:
                raise ValueError(f"VPN type {config.vpn_type} not supported for AWS")
            
            return gateway
        
        except Exception as e:
            self.logger.error(f"Failed to create AWS VPN gateway: {str(e)}")
            raise
    
    async def _create_gcp_vpn_gateway(self, config: VPNConfiguration) -> VPNGateway:
        """Create GCP VPN gateway"""
        
        if not self.gcp_compute:
            raise RuntimeError("GCP client not initialized")
        
        try:
            # Create VPN Gateway
            gateway_body = {
                "name": config.name.replace("_", "-").lower(),
                "description": f"VPN Gateway for {config.name}",
                "network": f"projects/{self.gcp_project_id}/global/networks/{config.vpc_id}",
                "region": config.region
            }
            
            operation = self.gcp_compute.insert(
                project=self.gcp_project_id,
                region=config.region,
                vpn_gateway_resource=gateway_body
            )
            
            # Wait for operation to complete
            await self._wait_for_gcp_operation(operation)
            
            # Get the created gateway
            vpn_gateway = self.gcp_compute.get(
                project=self.gcp_project_id,
                region=config.region,
                vpn_gateway=gateway_body["name"]
            )
            
            gateway = VPNGateway(
                id=str(vpn_gateway.id),
                name=config.name,
                vpn_type=config.vpn_type,
                protocol=config.protocol,
                provider="gcp",
                region=config.region,
                vpc_id=config.vpc_id,
                subnet_id=config.subnet_id,
                status=VPNStatus.CREATING,
                local_cidr=config.local_cidr,
                authentication_method=config.authentication_method,
                encryption_algorithm=config.encryption_algorithm,
                hash_algorithm=config.hash_algorithm,
                tags=config.tags
            )
            
            return gateway
        
        except Exception as e:
            self.logger.error(f"Failed to create GCP VPN gateway: {str(e)}")
            raise
    
    async def _create_azure_vpn_gateway(self, config: VPNConfiguration) -> VPNGateway:
        """Create Azure VPN gateway"""
        
        if not self.azure_network:
            raise RuntimeError("Azure client not initialized")
        
        try:
            resource_group_name = config.tags.get('resource_group', f"rg-{config.vpc_id}")
            
            # Create Virtual Network Gateway
            gateway_params = {
                'location': config.region,
                'gateway_type': 'Vpn',
                'vpn_type': 'RouteBased',
                'enable_bgp': config.enable_bgp,
                'sku': {
                    'name': 'VpnGw1',
                    'tier': 'VpnGw1'
                },
                'ip_configurations': [{
                    'name': 'default',
                    'subnet': {
                        'id': f"/subscriptions/{self.azure_subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{config.vpc_id}/subnets/{config.subnet_id}"
                    },
                    'public_ip_address': {
                        'id': f"/subscriptions/{self.azure_subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/publicIPAddresses/{config.name}-pip"
                    }
                }],
                'tags': config.tags
            }
            
            operation = self.azure_network.virtual_network_gateways.begin_create_or_update(
                resource_group_name,
                config.name,
                gateway_params
            )
            
            # Wait for operation to complete
            vpn_gateway = operation.result()
            
            gateway = VPNGateway(
                id=vpn_gateway.id,
                name=config.name,
                vpn_type=config.vpn_type,
                protocol=config.protocol,
                provider="azure",
                region=config.region,
                vpc_id=config.vpc_id,
                subnet_id=config.subnet_id,
                status=VPNStatus.CREATING,
                local_cidr=config.local_cidr,
                authentication_method=config.authentication_method,
                encryption_algorithm=config.encryption_algorithm,
                hash_algorithm=config.hash_algorithm,
                tags=config.tags
            )
            
            return gateway
        
        except Exception as e:
            self.logger.error(f"Failed to create Azure VPN gateway: {str(e)}")
            raise
    
    async def _wait_for_gcp_operation(self, operation):
        """Wait for GCP operation to complete"""
        # Simplified implementation
        await asyncio.sleep(2)
    
    async def delete_vpn_gateway(self, gateway_id: str) -> bool:
        """
        Delete a VPN gateway
        
        Args:
            gateway_id: VPN gateway ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        if gateway_id not in self.gateways:
            raise ValueError(f"VPN gateway {gateway_id} not found")
        
        gateway = self.gateways[gateway_id]
        
        self.logger.info(f"Deleting VPN gateway {gateway_id} ({gateway.name}) from {gateway.provider}")
        
        try:
            gateway.status = VPNStatus.DELETING
            
            if gateway.provider == "aws":
                success = await self._delete_aws_vpn_gateway(gateway)
            elif gateway.provider == "gcp":
                success = await self._delete_gcp_vpn_gateway(gateway)
            elif gateway.provider == "azure":
                success = await self._delete_azure_vpn_gateway(gateway)
            else:
                success = False
            
            if success:
                gateway.status = VPNStatus.DELETED
                del self.gateways[gateway_id]
                self.logger.info(f"Successfully deleted VPN gateway {gateway_id}")
            else:
                gateway.status = VPNStatus.FAILED
                self.logger.error(f"Failed to delete VPN gateway {gateway_id}")
            
            return success
        
        except Exception as e:
            gateway.status = VPNStatus.FAILED
            self.logger.error(f"Error deleting VPN gateway {gateway_id}: {str(e)}")
            return False
    
    async def _delete_aws_vpn_gateway(self, gateway: VPNGateway) -> bool:
        """Delete AWS VPN gateway"""
        
        try:
            if gateway.vpn_type == VPNType.SITE_TO_SITE:
                # Detach from VPC
                self.aws_ec2.detach_vpn_gateway(
                    VpnGatewayId=gateway.id,
                    VpcId=gateway.vpc_id
                )
                
                # Delete VPN gateway
                self.aws_ec2.delete_vpn_gateway(VpnGatewayId=gateway.id)
            
            elif gateway.vpn_type == VPNType.POINT_TO_SITE:
                # Delete Client VPN endpoint
                self.aws_ec2.delete_client_vpn_endpoint(ClientVpnEndpointId=gateway.id)
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting AWS VPN gateway: {str(e)}")
            return False
    
    async def _delete_gcp_vpn_gateway(self, gateway: VPNGateway) -> bool:
        """Delete GCP VPN gateway"""
        
        try:
            operation = self.gcp_compute.delete(
                project=self.gcp_project_id,
                region=gateway.region,
                vpn_gateway=gateway.name.replace("_", "-").lower()
            )
            
            await self._wait_for_gcp_operation(operation)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting GCP VPN gateway: {str(e)}")
            return False
    
    async def _delete_azure_vpn_gateway(self, gateway: VPNGateway) -> bool:
        """Delete Azure VPN gateway"""
        
        try:
            resource_group_name = gateway.tags.get('resource_group', f"rg-{gateway.vpc_id}")
            
            operation = self.azure_network.virtual_network_gateways.begin_delete(
                resource_group_name,
                gateway.name
            )
            
            operation.result()  # Wait for completion
            return True
        except Exception as e:
            self.logger.error(f"Error deleting Azure VPN gateway: {str(e)}")
            return False
    
    async def connect_client(self, gateway_id: str, username: str, client_ip: str, client_certificate: Optional[str] = None) -> VPNClient:
        """Connect a VPN client"""
        
        if gateway_id not in self.gateways:
            raise ValueError(f"VPN gateway {gateway_id} not found")
        
        gateway = self.gateways[gateway_id]
        
        if gateway.current_clients >= gateway.max_clients:
            raise Exception("Maximum number of clients reached")
        
        # Create client connection
        client = VPNClient(
            id=f"client_{hashlib.sha256(f'{username}_{client_ip}_{datetime.utcnow()}'.encode()).hexdigest()[:12]}",
            username=username,
            client_ip=client_ip,
            gateway_id=gateway_id,
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            client_certificate=client_certificate
        )
        
        # Add to gateway
        gateway.connected_clients.append(client)
        gateway.current_clients += 1
        
        # Track globally
        self.active_connections[client.id] = client
        
        # Log connection
        self._log_connection_event(gateway, "client_connected", {
            "client_id": client.id,
            "username": username,
            "client_ip": client_ip
        })
        
        self.logger.info(f"Client {username} connected to VPN gateway {gateway_id}")
        
        return client
    
    async def disconnect_client(self, client_id: str):
        """Disconnect a VPN client"""
        
        if client_id not in self.active_connections:
            raise ValueError(f"Client {client_id} not found")
        
        client = self.active_connections[client_id]
        gateway = self.gateways[client.gateway_id]
        
        # Calculate session duration
        session_duration = (datetime.utcnow() - client.connected_at).total_seconds()
        client.session_duration = int(session_duration)
        
        # Remove from gateway
        gateway.connected_clients = [c for c in gateway.connected_clients if c.id != client_id]
        gateway.current_clients -= 1
        
        # Remove from global tracking
        del self.active_connections[client_id]
        
        # Log disconnection
        self._log_connection_event(gateway, "client_disconnected", {
            "client_id": client.id,
            "username": client.username,
            "session_duration": session_duration,
            "bytes_transferred": client.bytes_transferred
        })
        
        self.logger.info(f"Client {client.username} disconnected from VPN gateway {client.gateway_id}")
    
    def _log_connection_event(self, gateway: VPNGateway, event_type: str, details: Dict[str, Any]):
        """Log VPN connection event"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "gateway_id": gateway.id,
            "gateway_name": gateway.name,
            **details
        }
        
        gateway.connection_logs.append(log_entry)
        
        # Maintain log limit
        if len(gateway.connection_logs) > self.max_log_entries:
            gateway.connection_logs = gateway.connection_logs[-self.max_log_entries:]
    
    async def _monitor_gateway(self, gateway_id: str):
        """Monitor VPN gateway status and metrics"""
        
        while gateway_id in self.gateways:
            try:
                gateway = self.gateways[gateway_id]
                
                # Update gateway status
                await self._update_gateway_status(gateway)
                
                # Update bandwidth usage
                await self._update_bandwidth_usage(gateway)
                
                # Check client activity
                await self._check_client_activity(gateway)
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring gateway {gateway_id}: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _update_gateway_status(self, gateway: VPNGateway):
        """Update VPN gateway status"""
        
        try:
            if gateway.provider == "aws":
                if gateway.vpn_type == VPNType.SITE_TO_SITE:
                    response = self.aws_ec2.describe_vpn_gateways(VpnGatewayIds=[gateway.id])
                    if response['VpnGateways']:
                        aws_state = response['VpnGateways'][0]['State']
                        gateway.status = VPNStatus.AVAILABLE if aws_state == 'available' else VPNStatus.CREATING
                
                elif gateway.vpn_type == VPNType.POINT_TO_SITE:
                    response = self.aws_ec2.describe_client_vpn_endpoints(ClientVpnEndpointIds=[gateway.id])
                    if response['ClientVpnEndpoints']:
                        aws_state = response['ClientVpnEndpoints'][0]['Status']['Code']
                        gateway.status = VPNStatus.AVAILABLE if aws_state == 'available' else VPNStatus.CREATING
            
            # Update timestamp
            gateway.updated_at = datetime.utcnow()
            
        except Exception as e:
            self.logger.debug(f"Could not update gateway status: {str(e)}")
    
    async def _update_bandwidth_usage(self, gateway: VPNGateway):
        """Update bandwidth usage statistics"""
        
        # This would integrate with cloud provider monitoring APIs
        # For now, simulate some usage data
        
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        
        # Simulate bandwidth usage
        bytes_in = sum(client.bytes_transferred for client in gateway.connected_clients) // 2
        bytes_out = sum(client.bytes_transferred for client in gateway.connected_clients) // 2
        
        gateway.bandwidth_usage[current_time] = {
            'bytes_in': bytes_in,
            'bytes_out': bytes_out,
            'total': bytes_in + bytes_out
        }
        
        # Keep only last 24 hours of data
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        gateway.bandwidth_usage = {
            k: v for k, v in gateway.bandwidth_usage.items()
            if datetime.strptime(k, '%Y-%m-%d %H:%M') >= cutoff_time
        }
    
    async def _check_client_activity(self, gateway: VPNGateway):
        """Check client activity and handle timeouts"""
        
        current_time = datetime.utcnow()
        timeout_threshold = timedelta(seconds=gateway.tags.get('client_timeout', 3600))
        
        clients_to_disconnect = []
        
        for client in gateway.connected_clients:
            if current_time - client.last_activity > timeout_threshold:
                clients_to_disconnect.append(client.id)
        
        # Disconnect inactive clients
        for client_id in clients_to_disconnect:
            try:
                await self.disconnect_client(client_id)
                self.logger.info(f"Disconnected inactive client: {client_id}")
            except Exception as e:
                self.logger.error(f"Error disconnecting client {client_id}: {str(e)}")
    
    def list_vpn_gateways(
        self,
        vpc_id: Optional[str] = None,
        vpn_type: Optional[VPNType] = None,
        provider: Optional[str] = None,
        status: Optional[VPNStatus] = None
    ) -> List[VPNGateway]:
        """List VPN gateways with optional filters"""
        
        gateways = list(self.gateways.values())
        
        if vpc_id:
            gateways = [gw for gw in gateways if gw.vpc_id == vpc_id]
        
        if vpn_type:
            gateways = [gw for gw in gateways if gw.vpn_type == vpn_type]
        
        if provider:
            gateways = [gw for gw in gateways if gw.provider == provider]
        
        if status:
            gateways = [gw for gw in gateways if gw.status == status]
        
        return gateways
    
    def get_vpn_gateway(self, gateway_id: str) -> Optional[VPNGateway]:
        """Get VPN gateway by ID"""
        return self.gateways.get(gateway_id)
    
    def get_gateway_statistics(self, gateway_id: str) -> Dict[str, Any]:
        """Get VPN gateway statistics"""
        
        if gateway_id not in self.gateways:
            raise ValueError(f"VPN gateway {gateway_id} not found")
        
        gateway = self.gateways[gateway_id]
        
        # Calculate statistics
        total_connections = len(gateway.connection_logs)
        current_connections = len(gateway.connected_clients)
        
        # Connection events in last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_connections = len([
            log for log in gateway.connection_logs
            if datetime.fromisoformat(log['timestamp']) >= last_24h
            and log['event_type'] == 'client_connected'
        ])
        
        # Total bandwidth
        total_bandwidth = sum(usage['total'] for usage in gateway.bandwidth_usage.values())
        
        # Average session duration
        session_durations = [
            log.get('session_duration', 0) for log in gateway.connection_logs
            if log['event_type'] == 'client_disconnected' and 'session_duration' in log
        ]
        avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
        
        return {
            'gateway_id': gateway_id,
            'gateway_name': gateway.name,
            'status': gateway.status.value,
            'vpn_type': gateway.vpn_type.value,
            'provider': gateway.provider,
            'current_connections': current_connections,
            'max_connections': gateway.max_clients,
            'utilization_percentage': (current_connections / gateway.max_clients * 100) if gateway.max_clients > 0 else 0,
            'total_connections_all_time': total_connections,
            'connections_last_24h': recent_connections,
            'total_bandwidth_bytes': total_bandwidth,
            'average_session_duration_seconds': avg_session_duration,
            'uptime_hours': (datetime.utcnow() - gateway.created_at).total_seconds() / 3600
        }
    
    def get_vpn_summary(self) -> Dict[str, Any]:
        """Get VPN system summary statistics"""
        
        total_gateways = len(self.gateways)
        
        if total_gateways == 0:
            return {'total_gateways': 0}
        
        # Provider breakdown
        provider_counts = {}
        providers = set(gw.provider for gw in self.gateways.values())
        for provider in providers:
            provider_counts[provider] = len([
                gw for gw in self.gateways.values() if gw.provider == provider
            ])
        
        # VPN type breakdown
        type_counts = {}
        for vpn_type in VPNType:
            type_counts[vpn_type.value] = len([
                gw for gw in self.gateways.values() if gw.vpn_type == vpn_type
            ])
        
        # Status breakdown
        status_counts = {}
        for status in VPNStatus:
            status_counts[status.value] = len([
                gw for gw in self.gateways.values() if gw.status == status
            ])
        
        # Connection statistics
        total_current_connections = sum(gw.current_clients for gw in self.gateways.values())
        total_max_connections = sum(gw.max_clients for gw in self.gateways.values())
        
        # Active clients
        active_clients = len(self.active_connections)
        
        return {
            'total_gateways': total_gateways,
            'provider_breakdown': provider_counts,
            'vpn_type_breakdown': type_counts,
            'status_breakdown': status_counts,
            'connection_statistics': {
                'total_current_connections': total_current_connections,
                'total_max_connections': total_max_connections,
                'utilization_percentage': (total_current_connections / total_max_connections * 100) if total_max_connections > 0 else 0,
                'active_clients': active_clients
            }
        }


# Export main classes
__all__ = ['VPNGatewayManager', 'VPNConfiguration', 'VPNGateway', 'VPNTunnel', 'VPNClient', 'VPNType', 'VPNProtocol', 'VPNStatus', 'AuthenticationMethod']