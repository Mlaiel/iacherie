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
VPC Manager

Enterprise Virtual Private Cloud (VPC) management system for multi-cloud networking.
Provides unified VPC management across AWS, GCP, and Azure platforms.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import json
import boto3
from google.cloud import compute_v1
from azure.mgmt.network import NetworkManagementClient
from azure.identity import DefaultAzureCredential


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class VPCStatus(Enum):
    """VPC status states"""
    CREATING = "creating"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"


@dataclass
class VPCConfiguration:
    """VPC configuration specification"""
    name: str
    cidr_block: str
    provider: CloudProvider
    region: str
    availability_zones: List[str]
    enable_dns_hostnames: bool = True
    enable_dns_resolution: bool = True
    enable_internet_gateway: bool = True
    enable_nat_gateway: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    tenancy: str = "default"  # default, dedicated
    flow_logs_enabled: bool = True
    flow_logs_destination: str = "cloudwatch"  # cloudwatch, s3


@dataclass
class VPCInstance:
    """VPC instance representation"""
    id: str
    name: str
    cidr_block: str
    provider: CloudProvider
    region: str
    status: VPCStatus
    availability_zones: List[str] = field(default_factory=list)
    internet_gateway_id: Optional[str] = None
    nat_gateway_ids: List[str] = field(default_factory=list)
    route_table_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    dns_hostnames_enabled: bool = True
    dns_resolution_enabled: bool = True
    flow_logs_enabled: bool = False
    flow_logs_id: Optional[str] = None


@dataclass
class VPCPeeringConnection:
    """VPC peering connection"""
    id: str
    vpc_id: str
    peer_vpc_id: str
    peer_region: Optional[str] = None
    peer_account_id: Optional[str] = None
    status: str = "pending-acceptance"
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)


class VPCManager:
    """
    Enterprise VPC management system
    
    Provides comprehensive VPC management capabilities including:
    - Multi-cloud VPC provisioning and management
    - VPC peering and connectivity
    - Network segmentation and isolation
    - Flow logs and monitoring
    - DNS management
    - Internet and NAT gateway management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.vpcs: Dict[str, VPCInstance] = {}
        self.peering_connections: Dict[str, VPCPeeringConnection] = {}
        
        # Initialize cloud provider clients
        self._initialize_cloud_clients()
    
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
                self.gcp_compute = compute_v1.NetworksClient()
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
    
    async def create_vpc(self, config: VPCConfiguration) -> VPCInstance:
        """
        Create a new VPC
        
        Args:
            config: VPC configuration
            
        Returns:
            Created VPC instance
        """
        self.logger.info(f"Creating VPC '{config.name}' in {config.provider.value} ({config.region})")
        
        # Validate CIDR block
        try:
            ipaddress.ip_network(config.cidr_block, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR block '{config.cidr_block}': {str(e)}")
        
        # Create VPC based on provider
        if config.provider == CloudProvider.AWS:
            vpc = await self._create_aws_vpc(config)
        elif config.provider == CloudProvider.GCP:
            vpc = await self._create_gcp_vpc(config)
        elif config.provider == CloudProvider.AZURE:
            vpc = await self._create_azure_vpc(config)
        else:
            raise ValueError(f"Unsupported cloud provider: {config.provider}")
        
        # Store VPC instance
        self.vpcs[vpc.id] = vpc
        
        self.logger.info(f"Successfully created VPC {vpc.id} ({vpc.name})")
        
        return vpc
    
    async def _create_aws_vpc(self, config: VPCConfiguration) -> VPCInstance:
        """Create AWS VPC"""
        
        if not self.aws_ec2:
            raise RuntimeError("AWS client not initialized")
        
        try:
            # Create VPC
            response = self.aws_ec2.create_vpc(
                CidrBlock=config.cidr_block,
                InstanceTenancy=config.tenancy,
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': config.name},
                        *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                    ]
                }]
            )
            
            vpc_id = response['Vpc']['VpcId']
            
            # Enable DNS support
            if config.enable_dns_hostnames:
                self.aws_ec2.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsHostnames={'Value': True}
                )
            
            if config.enable_dns_resolution:
                self.aws_ec2.modify_vpc_attribute(
                    VpcId=vpc_id,
                    EnableDnsSupport={'Value': True}
                )
            
            # Create Internet Gateway if requested
            internet_gateway_id = None
            if config.enable_internet_gateway:
                igw_response = self.aws_ec2.create_internet_gateway(
                    TagSpecifications=[{
                        'ResourceType': 'internet-gateway',
                        'Tags': [
                            {'Key': 'Name', 'Value': f"{config.name}-igw"},
                            *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                        ]
                    }]
                )
                internet_gateway_id = igw_response['InternetGateway']['InternetGatewayId']
                
                # Attach to VPC
                self.aws_ec2.attach_internet_gateway(
                    InternetGatewayId=internet_gateway_id,
                    VpcId=vpc_id
                )
            
            # Enable VPC Flow Logs if requested
            flow_logs_id = None
            if config.flow_logs_enabled:
                flow_logs_id = await self._enable_aws_flow_logs(vpc_id, config)
            
            # Create VPC instance
            vpc_instance = VPCInstance(
                id=vpc_id,
                name=config.name,
                cidr_block=config.cidr_block,
                provider=CloudProvider.AWS,
                region=config.region,
                status=VPCStatus.AVAILABLE,
                availability_zones=config.availability_zones,
                internet_gateway_id=internet_gateway_id,
                tags=config.tags,
                dns_hostnames_enabled=config.enable_dns_hostnames,
                dns_resolution_enabled=config.enable_dns_resolution,
                flow_logs_enabled=config.flow_logs_enabled,
                flow_logs_id=flow_logs_id
            )
            
            return vpc_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create AWS VPC: {str(e)}")
            raise
    
    async def _create_gcp_vpc(self, config: VPCConfiguration) -> VPCInstance:
        """Create GCP VPC (Virtual Network)"""
        
        if not self.gcp_compute:
            raise RuntimeError("GCP client not initialized")
        
        try:
            # Create VPC network
            network_body = {
                "name": config.name.replace("_", "-").lower(),
                "description": f"VPC network for {config.name}",
                "routing_config": {
                    "routing_mode": "REGIONAL"
                },
                "auto_create_subnetworks": False
            }
            
            operation = self.gcp_compute.insert(
                project=self.gcp_project_id,
                network_resource=network_body
            )
            
            # Wait for operation to complete
            await self._wait_for_gcp_operation(operation)
            
            # Get the created network
            network = self.gcp_compute.get(
                project=self.gcp_project_id,
                network=network_body["name"]
            )
            
            vpc_instance = VPCInstance(
                id=str(network.id),
                name=config.name,
                cidr_block=config.cidr_block,
                provider=CloudProvider.GCP,
                region=config.region,
                status=VPCStatus.AVAILABLE,
                availability_zones=config.availability_zones,
                tags=config.tags
            )
            
            return vpc_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create GCP VPC: {str(e)}")
            raise
    
    async def _create_azure_vpc(self, config: VPCConfiguration) -> VPCInstance:
        """Create Azure Virtual Network"""
        
        if not self.azure_network:
            raise RuntimeError("Azure client not initialized")
        
        try:
            # Create resource group if needed
            resource_group_name = config.tags.get('resource_group', f"rg-{config.name}")
            
            # Create virtual network
            vnet_params = {
                'location': config.region,
                'address_space': {
                    'address_prefixes': [config.cidr_block]
                },
                'enable_dns_resolution': config.enable_dns_resolution,
                'tags': config.tags
            }
            
            operation = self.azure_network.virtual_networks.begin_create_or_update(
                resource_group_name,
                config.name,
                vnet_params
            )
            
            # Wait for operation to complete
            vnet = operation.result()
            
            vpc_instance = VPCInstance(
                id=vnet.id,
                name=config.name,
                cidr_block=config.cidr_block,
                provider=CloudProvider.AZURE,
                region=config.region,
                status=VPCStatus.AVAILABLE,
                availability_zones=config.availability_zones,
                tags=config.tags,
                dns_resolution_enabled=config.enable_dns_resolution
            )
            
            return vpc_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create Azure VNet: {str(e)}")
            raise
    
    async def _enable_aws_flow_logs(self, vpc_id: str, config: VPCConfiguration) -> str:
        """Enable AWS VPC Flow Logs"""
        
        try:
            # Create CloudWatch log group if using CloudWatch
            if config.flow_logs_destination == "cloudwatch":
                log_group_name = f"/aws/vpc/flowlogs/{vpc_id}"
                
                # Create IAM role for flow logs (simplified)
                role_arn = f"arn:aws:iam::{self._get_aws_account_id()}:role/flowlogsRole"
                
                response = self.aws_ec2.create_flow_logs(
                    ResourceIds=[vpc_id],
                    ResourceType='VPC',
                    TrafficType='ALL',
                    LogDestinationType='cloud-watch-logs',
                    LogGroupName=log_group_name,
                    DeliverLogsPermissionArn=role_arn
                )
                
                if response['Unsuccessful']:
                    raise Exception(f"Failed to create flow logs: {response['Unsuccessful'][0]['Error']['Message']}")
                
                return response['FlowLogIds'][0]
        
        except Exception as e:
            self.logger.warning(f"Failed to enable flow logs: {str(e)}")
            return None
    
    def _get_aws_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            sts = boto3.client('sts')
            return sts.get_caller_identity()['Account']
        except:
            return "123456789012"  # Fallback
    
    async def _wait_for_gcp_operation(self, operation):
        """Wait for GCP operation to complete"""
        # Simplified implementation
        await asyncio.sleep(2)
    
    async def delete_vpc(self, vpc_id: str) -> bool:
        """
        Delete a VPC
        
        Args:
            vpc_id: VPC ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        if vpc_id not in self.vpcs:
            raise ValueError(f"VPC {vpc_id} not found")
        
        vpc = self.vpcs[vpc_id]
        
        self.logger.info(f"Deleting VPC {vpc_id} ({vpc.name}) from {vpc.provider.value}")
        
        try:
            vpc.status = VPCStatus.DELETING
            
            if vpc.provider == CloudProvider.AWS:
                success = await self._delete_aws_vpc(vpc)
            elif vpc.provider == CloudProvider.GCP:
                success = await self._delete_gcp_vpc(vpc)
            elif vpc.provider == CloudProvider.AZURE:
                success = await self._delete_azure_vpc(vpc)
            else:
                success = False
            
            if success:
                vpc.status = VPCStatus.DELETED
                del self.vpcs[vpc_id]
                self.logger.info(f"Successfully deleted VPC {vpc_id}")
            else:
                vpc.status = VPCStatus.FAILED
                self.logger.error(f"Failed to delete VPC {vpc_id}")
            
            return success
        
        except Exception as e:
            vpc.status = VPCStatus.FAILED
            self.logger.error(f"Error deleting VPC {vpc_id}: {str(e)}")
            return False
    
    async def _delete_aws_vpc(self, vpc: VPCInstance) -> bool:
        """Delete AWS VPC"""
        
        try:
            # Delete flow logs if enabled
            if vpc.flow_logs_id:
                self.aws_ec2.delete_flow_logs(FlowLogIds=[vpc.flow_logs_id])
            
            # Detach and delete internet gateway
            if vpc.internet_gateway_id:
                self.aws_ec2.detach_internet_gateway(
                    InternetGatewayId=vpc.internet_gateway_id,
                    VpcId=vpc.id
                )
                self.aws_ec2.delete_internet_gateway(
                    InternetGatewayId=vpc.internet_gateway_id
                )
            
            # Delete NAT gateways
            for nat_gateway_id in vpc.nat_gateway_ids:
                self.aws_ec2.delete_nat_gateway(NatGatewayId=nat_gateway_id)
            
            # Delete VPC
            self.aws_ec2.delete_vpc(VpcId=vpc.id)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting AWS VPC: {str(e)}")
            return False
    
    async def _delete_gcp_vpc(self, vpc: VPCInstance) -> bool:
        """Delete GCP VPC"""
        
        try:
            operation = self.gcp_compute.delete(
                project=self.gcp_project_id,
                network=vpc.name.replace("_", "-").lower()
            )
            
            await self._wait_for_gcp_operation(operation)
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting GCP VPC: {str(e)}")
            return False
    
    async def _delete_azure_vpc(self, vpc: VPCInstance) -> bool:
        """Delete Azure Virtual Network"""
        
        try:
            resource_group_name = vpc.tags.get('resource_group', f"rg-{vpc.name}")
            
            operation = self.azure_network.virtual_networks.begin_delete(
                resource_group_name,
                vpc.name
            )
            
            operation.result()  # Wait for completion
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting Azure VNet: {str(e)}")
            return False
    
    async def create_vpc_peering(
        self,
        vpc_id: str,
        peer_vpc_id: str,
        peer_region: Optional[str] = None,
        peer_account_id: Optional[str] = None
    ) -> VPCPeeringConnection:
        """
        Create VPC peering connection
        
        Args:
            vpc_id: Source VPC ID
            peer_vpc_id: Target VPC ID
            peer_region: Target VPC region (for cross-region peering)
            peer_account_id: Target account ID (for cross-account peering)
            
        Returns:
            VPC peering connection
        """
        if vpc_id not in self.vpcs:
            raise ValueError(f"VPC {vpc_id} not found")
        
        vpc = self.vpcs[vpc_id]
        
        self.logger.info(f"Creating VPC peering connection from {vpc_id} to {peer_vpc_id}")
        
        if vpc.provider == CloudProvider.AWS:
            peering = await self._create_aws_vpc_peering(vpc, peer_vpc_id, peer_region, peer_account_id)
        else:
            raise NotImplementedError(f"VPC peering not implemented for {vpc.provider.value}")
        
        self.peering_connections[peering.id] = peering
        
        return peering
    
    async def _create_aws_vpc_peering(
        self,
        vpc: VPCInstance,
        peer_vpc_id: str,
        peer_region: Optional[str] = None,
        peer_account_id: Optional[str] = None
    ) -> VPCPeeringConnection:
        """Create AWS VPC peering connection"""
        
        try:
            params = {
                'VpcId': vpc.id,
                'PeerVpcId': peer_vpc_id
            }
            
            if peer_region:
                params['PeerRegion'] = peer_region
            
            if peer_account_id:
                params['PeerOwnerId'] = peer_account_id
            
            response = self.aws_ec2.create_vpc_peering_connection(**params)
            
            peering_connection = response['VpcPeeringConnection']
            
            return VPCPeeringConnection(
                id=peering_connection['VpcPeeringConnectionId'],
                vpc_id=vpc.id,
                peer_vpc_id=peer_vpc_id,
                peer_region=peer_region,
                peer_account_id=peer_account_id,
                status=peering_connection['Status']['Code']
            )
        
        except Exception as e:
            self.logger.error(f"Failed to create AWS VPC peering: {str(e)}")
            raise
    
    async def accept_vpc_peering(self, peering_id: str) -> bool:
        """Accept VPC peering connection"""
        
        if peering_id not in self.peering_connections:
            raise ValueError(f"Peering connection {peering_id} not found")
        
        peering = self.peering_connections[peering_id]
        vpc = self.vpcs[peering.vpc_id]
        
        if vpc.provider == CloudProvider.AWS:
            return await self._accept_aws_vpc_peering(peering)
        else:
            raise NotImplementedError(f"VPC peering not implemented for {vpc.provider.value}")
    
    async def _accept_aws_vpc_peering(self, peering: VPCPeeringConnection) -> bool:
        """Accept AWS VPC peering connection"""
        
        try:
            response = self.aws_ec2.accept_vpc_peering_connection(
                VpcPeeringConnectionId=peering.id
            )
            
            peering.status = response['VpcPeeringConnection']['Status']['Code']
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to accept AWS VPC peering: {str(e)}")
            return False
    
    def list_vpcs(
        self,
        provider: Optional[CloudProvider] = None,
        region: Optional[str] = None,
        status: Optional[VPCStatus] = None
    ) -> List[VPCInstance]:
        """
        List VPCs with optional filters
        
        Args:
            provider: Filter by cloud provider
            region: Filter by region
            status: Filter by status
            
        Returns:
            List of VPC instances
        """
        vpcs = list(self.vpcs.values())
        
        if provider:
            vpcs = [vpc for vpc in vpcs if vpc.provider == provider]
        
        if region:
            vpcs = [vpc for vpc in vpcs if vpc.region == region]
        
        if status:
            vpcs = [vpc for vpc in vpcs if vpc.status == status]
        
        return vpcs
    
    def get_vpc(self, vpc_id: str) -> Optional[VPCInstance]:
        """Get VPC by ID"""
        return self.vpcs.get(vpc_id)
    
    def list_peering_connections(self, vpc_id: Optional[str] = None) -> List[VPCPeeringConnection]:
        """List VPC peering connections"""
        
        connections = list(self.peering_connections.values())
        
        if vpc_id:
            connections = [
                conn for conn in connections 
                if conn.vpc_id == vpc_id or conn.peer_vpc_id == vpc_id
            ]
        
        return connections
    
    async def get_vpc_utilization(self, vpc_id: str) -> Dict[str, Any]:
        """Get VPC resource utilization"""
        
        if vpc_id not in self.vpcs:
            raise ValueError(f"VPC {vpc_id} not found")
        
        vpc = self.vpcs[vpc_id]
        
        if vpc.provider == CloudProvider.AWS:
            return await self._get_aws_vpc_utilization(vpc)
        elif vpc.provider == CloudProvider.GCP:
            return await self._get_gcp_vpc_utilization(vpc)
        elif vpc.provider == CloudProvider.AZURE:
            return await self._get_azure_vpc_utilization(vpc)
        else:
            return {}
    
    async def _get_aws_vpc_utilization(self, vpc: VPCInstance) -> Dict[str, Any]:
        """Get AWS VPC utilization"""
        
        try:
            # Get subnets
            subnets_response = self.aws_ec2.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc.id]}]
            )
            subnets = subnets_response['Subnets']
            
            # Get security groups
            sg_response = self.aws_ec2.describe_security_groups(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc.id]}]
            )
            security_groups = sg_response['SecurityGroups']
            
            # Get route tables
            rt_response = self.aws_ec2.describe_route_tables(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc.id]}]
            )
            route_tables = rt_response['RouteTables']
            
            # Get network ACLs
            nacl_response = self.aws_ec2.describe_network_acls(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc.id]}]
            )
            network_acls = nacl_response['NetworkAcls']
            
            return {
                'vpc_id': vpc.id,
                'subnets_count': len(subnets),
                'security_groups_count': len(security_groups),
                'route_tables_count': len(route_tables),
                'network_acls_count': len(network_acls),
                'available_ips': sum(
                    2 ** (32 - int(subnet['CidrBlock'].split('/')[1])) - 5 
                    for subnet in subnets
                ),
                'subnets': [
                    {
                        'id': subnet['SubnetId'],
                        'cidr': subnet['CidrBlock'],
                        'az': subnet['AvailabilityZone'],
                        'available_ips': subnet['AvailableIpAddressCount']
                    }
                    for subnet in subnets
                ]
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get AWS VPC utilization: {str(e)}")
            return {}
    
    async def _get_gcp_vpc_utilization(self, vpc: VPCInstance) -> Dict[str, Any]:
        """Get GCP VPC utilization"""
        
        # Placeholder implementation
        return {
            'vpc_id': vpc.id,
            'provider': 'gcp',
            'utilization_data': 'not_implemented'
        }
    
    async def _get_azure_vpc_utilization(self, vpc: VPCInstance) -> Dict[str, Any]:
        """Get Azure VNet utilization"""
        
        # Placeholder implementation
        return {
            'vpc_id': vpc.id,
            'provider': 'azure',
            'utilization_data': 'not_implemented'
        }
    
    async def get_vpc_flow_logs(self, vpc_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get VPC flow logs"""
        
        if vpc_id not in self.vpcs:
            raise ValueError(f"VPC {vpc_id} not found")
        
        vpc = self.vpcs[vpc_id]
        
        if not vpc.flow_logs_enabled:
            return []
        
        if vpc.provider == CloudProvider.AWS:
            return await self._get_aws_flow_logs(vpc, start_time, end_time)
        else:
            return []
    
    async def _get_aws_flow_logs(self, vpc: VPCInstance, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get AWS VPC flow logs"""
        
        # This would integrate with CloudWatch Logs API
        # For now, return sample data
        
        return [
            {
                'timestamp': start_time.isoformat(),
                'source_ip': '10.0.1.100',
                'destination_ip': '10.0.2.200',
                'source_port': 80,
                'destination_port': 443,
                'protocol': 'TCP',
                'action': 'ACCEPT',
                'bytes': 1024
            }
        ]
    
    def get_vpc_summary(self) -> Dict[str, Any]:
        """Get VPC summary statistics"""
        
        total_vpcs = len(self.vpcs)
        
        if total_vpcs == 0:
            return {'total_vpcs': 0}
        
        # Provider breakdown
        provider_counts = {}
        for provider in CloudProvider:
            provider_counts[provider.value] = len([
                vpc for vpc in self.vpcs.values() if vpc.provider == provider
            ])
        
        # Status breakdown
        status_counts = {}
        for status in VPCStatus:
            status_counts[status.value] = len([
                vpc for vpc in self.vpcs.values() if vpc.status == status
            ])
        
        # Region breakdown
        regions = set(vpc.region for vpc in self.vpcs.values())
        region_counts = {}
        for region in regions:
            region_counts[region] = len([
                vpc for vpc in self.vpcs.values() if vpc.region == region
            ])
        
        return {
            'total_vpcs': total_vpcs,
            'total_peering_connections': len(self.peering_connections),
            'provider_breakdown': provider_counts,
            'status_breakdown': status_counts,
            'region_breakdown': region_counts,
            'flow_logs_enabled': len([
                vpc for vpc in self.vpcs.values() if vpc.flow_logs_enabled
            ])
        }


# Export main classes
__all__ = ['VPCManager', 'VPCConfiguration', 'VPCInstance', 'VPCPeeringConnection', 'CloudProvider', 'VPCStatus']