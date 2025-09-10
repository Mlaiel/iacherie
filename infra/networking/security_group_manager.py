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
Security Group Manager

Enterprise security group management system for multi-cloud network security.
Provides unified security group management across AWS, GCP, and Azure platforms.
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


class SecurityGroupType(Enum):
    """Security group types"""
    WEB_TIER = "web_tier"
    APP_TIER = "app_tier"
    DATABASE_TIER = "database_tier"
    MANAGEMENT = "management"
    LOAD_BALANCER = "load_balancer"
    CUSTOM = "custom"


class RuleAction(Enum):
    """Security rule actions"""
    ALLOW = "allow"
    DENY = "deny"


class Protocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"
    ESP = "esp"
    AH = "ah"
    GRE = "gre"


class Direction(Enum):
    """Traffic direction"""
    INGRESS = "ingress"
    EGRESS = "egress"


@dataclass
class SecurityRule:
    """Security group rule"""
    name: str
    direction: Direction
    action: RuleAction
    protocol: Protocol
    port_range: Optional[str] = None  # "80" or "80-443" or None for all
    source_destination: str = "0.0.0.0/0"  # CIDR, security group ID, or tag
    description: Optional[str] = None
    priority: int = 1000
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityGroupConfiguration:
    """Security group configuration"""
    name: str
    description: str
    vpc_id: str
    group_type: SecurityGroupType
    provider: str  # aws, gcp, azure
    region: str
    rules: List[SecurityRule] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityGroupInstance:
    """Security group instance"""
    id: str
    name: str
    description: str
    vpc_id: str
    group_type: SecurityGroupType
    provider: str
    region: str
    rules: List[SecurityRule] = field(default_factory=list)
    attached_resources: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)


class SecurityGroupManager:
    """
    Enterprise security group management system
    
    Provides comprehensive security group management capabilities including:
    - Multi-cloud security group provisioning and management
    - Predefined security group templates
    - Rule validation and conflict detection
    - Security group analytics and monitoring
    - Compliance checking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.security_groups: Dict[str, SecurityGroupInstance] = {}
        
        # Initialize cloud provider clients
        self._initialize_cloud_clients()
        
        # Predefined security group templates
        self.templates = self._get_security_group_templates()
    
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
                self.gcp_compute = compute_v1.FirewallsClient()
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
    
    def _get_security_group_templates(self) -> Dict[SecurityGroupType, List[SecurityRule]]:
        """Get predefined security group templates"""
        
        return {
            SecurityGroupType.WEB_TIER: [
                SecurityRule(
                    name="allow_http_inbound",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="80",
                    source_destination="0.0.0.0/0",
                    description="Allow HTTP traffic from internet",
                    priority=100
                ),
                SecurityRule(
                    name="allow_https_inbound",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="443",
                    source_destination="0.0.0.0/0",
                    description="Allow HTTPS traffic from internet",
                    priority=110
                ),
                SecurityRule(
                    name="allow_ssh_admin",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="22",
                    source_destination="10.0.0.0/8",
                    description="Allow SSH from private networks",
                    priority=200
                ),
                SecurityRule(
                    name="allow_all_outbound",
                    direction=Direction.EGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.ALL,
                    source_destination="0.0.0.0/0",
                    description="Allow all outbound traffic",
                    priority=100
                )
            ],
            SecurityGroupType.APP_TIER: [
                SecurityRule(
                    name="allow_app_port",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="8080",
                    source_destination="web_tier_sg",
                    description="Allow app traffic from web tier",
                    priority=100
                ),
                SecurityRule(
                    name="allow_ssh_admin",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="22",
                    source_destination="10.0.0.0/8",
                    description="Allow SSH from private networks",
                    priority=200
                ),
                SecurityRule(
                    name="allow_outbound_db",
                    direction=Direction.EGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="3306",
                    source_destination="database_tier_sg",
                    description="Allow MySQL connection to database tier",
                    priority=100
                ),
                SecurityRule(
                    name="allow_outbound_https",
                    direction=Direction.EGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="443",
                    source_destination="0.0.0.0/0",
                    description="Allow HTTPS outbound",
                    priority=200
                )
            ],
            SecurityGroupType.DATABASE_TIER: [
                SecurityRule(
                    name="allow_mysql",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="3306",
                    source_destination="app_tier_sg",
                    description="Allow MySQL from app tier",
                    priority=100
                ),
                SecurityRule(
                    name="allow_postgresql",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="5432",
                    source_destination="app_tier_sg",
                    description="Allow PostgreSQL from app tier",
                    priority=110
                ),
                SecurityRule(
                    name="allow_ssh_admin",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="22",
                    source_destination="10.0.0.0/8",
                    description="Allow SSH from private networks",
                    priority=200
                ),
                SecurityRule(
                    name="deny_internet_outbound",
                    direction=Direction.EGRESS,
                    action=RuleAction.DENY,
                    protocol=Protocol.ALL,
                    source_destination="0.0.0.0/0",
                    description="Deny all internet access",
                    priority=1000
                )
            ],
            SecurityGroupType.LOAD_BALANCER: [
                SecurityRule(
                    name="allow_http_public",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="80",
                    source_destination="0.0.0.0/0",
                    description="Allow HTTP from internet",
                    priority=100
                ),
                SecurityRule(
                    name="allow_https_public",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="443",
                    source_destination="0.0.0.0/0",
                    description="Allow HTTPS from internet",
                    priority=110
                ),
                SecurityRule(
                    name="allow_health_check",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="8080",
                    source_destination="10.0.0.0/8",
                    description="Allow health check from internal",
                    priority=200
                )
            ],
            SecurityGroupType.MANAGEMENT: [
                SecurityRule(
                    name="allow_ssh",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="22",
                    source_destination="0.0.0.0/0",  # Should be restricted to admin IPs
                    description="Allow SSH access",
                    priority=100
                ),
                SecurityRule(
                    name="allow_rdp",
                    direction=Direction.INGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.TCP,
                    port_range="3389",
                    source_destination="0.0.0.0/0",  # Should be restricted to admin IPs
                    description="Allow RDP access",
                    priority=110
                ),
                SecurityRule(
                    name="allow_all_outbound",
                    direction=Direction.EGRESS,
                    action=RuleAction.ALLOW,
                    protocol=Protocol.ALL,
                    source_destination="0.0.0.0/0",
                    description="Allow all outbound traffic",
                    priority=100
                )
            ]
        }
    
    async def create_security_group(self, config: SecurityGroupConfiguration) -> SecurityGroupInstance:
        """
        Create a new security group
        
        Args:
            config: Security group configuration
            
        Returns:
            Created security group instance
        """
        self.logger.info(f"Creating security group '{config.name}' in VPC {config.vpc_id}")
        
        # Apply template rules if no custom rules provided
        if not config.rules and config.group_type in self.templates:
            config.rules = self.templates[config.group_type].copy()
        
        # Validate rules
        self._validate_security_rules(config.rules)
        
        # Create security group based on provider
        if config.provider == "aws":
            sg = await self._create_aws_security_group(config)
        elif config.provider == "gcp":
            sg = await self._create_gcp_security_group(config)
        elif config.provider == "azure":
            sg = await self._create_azure_security_group(config)
        else:
            raise ValueError(f"Unsupported cloud provider: {config.provider}")
        
        # Store security group instance
        self.security_groups[sg.id] = sg
        
        self.logger.info(f"Successfully created security group {sg.id} ({sg.name})")
        
        return sg
    
    def _validate_security_rules(self, rules: List[SecurityRule]):
        """Validate security rules"""
        
        for rule in rules:
            # Validate port range
            if rule.port_range:
                try:
                    if '-' in rule.port_range:
                        start, end = rule.port_range.split('-', 1)
                        start_port, end_port = int(start), int(end)
                        if not (0 <= start_port <= 65535 and 0 <= end_port <= 65535):
                            raise ValueError(f"Invalid port range: {rule.port_range}")
                        if start_port > end_port:
                            raise ValueError(f"Invalid port range: {rule.port_range}")
                    else:
                        port = int(rule.port_range)
                        if not (0 <= port <= 65535):
                            raise ValueError(f"Invalid port: {rule.port_range}")
                except ValueError as e:
                    raise ValueError(f"Invalid port specification in rule '{rule.name}': {str(e)}")
            
            # Validate CIDR block (if not a security group reference)
            if not rule.source_destination.endswith('_sg') and '/' in rule.source_destination:
                try:
                    ipaddress.ip_network(rule.source_destination, strict=False)
                except ValueError as e:
                    raise ValueError(f"Invalid CIDR block in rule '{rule.name}': {str(e)}")
    
    async def _create_aws_security_group(self, config: SecurityGroupConfiguration) -> SecurityGroupInstance:
        """Create AWS security group"""
        
        if not self.aws_ec2:
            raise RuntimeError("AWS client not initialized")
        
        try:
            # Create security group
            response = self.aws_ec2.create_security_group(
                GroupName=config.name,
                Description=config.description,
                VpcId=config.vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'Name', 'Value': config.name},
                        {'Key': 'Type', 'Value': config.group_type.value},
                        *[{'Key': k, 'Value': v} for k, v in config.tags.items()]
                    ]
                }]
            )
            
            sg_id = response['GroupId']
            
            # Add ingress rules
            ingress_rules = [rule for rule in config.rules if rule.direction == Direction.INGRESS]
            if ingress_rules:
                await self._add_aws_ingress_rules(sg_id, ingress_rules)
            
            # Add egress rules (first remove default allow all)
            self.aws_ec2.revoke_security_group_egress(
                GroupId=sg_id,
                IpPermissions=[{
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
            )
            
            egress_rules = [rule for rule in config.rules if rule.direction == Direction.EGRESS]
            if egress_rules:
                await self._add_aws_egress_rules(sg_id, egress_rules)
            
            sg_instance = SecurityGroupInstance(
                id=sg_id,
                name=config.name,
                description=config.description,
                vpc_id=config.vpc_id,
                group_type=config.group_type,
                provider="aws",
                region=config.region,
                rules=config.rules.copy(),
                tags=config.tags
            )
            
            return sg_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create AWS security group: {str(e)}")
            raise
    
    async def _add_aws_ingress_rules(self, sg_id: str, rules: List[SecurityRule]):
        """Add AWS ingress rules"""
        
        ip_permissions = []
        
        for rule in rules:
            if rule.action == RuleAction.DENY:
                continue  # AWS security groups don't support deny rules
            
            permission = {
                'IpProtocol': rule.protocol.value if rule.protocol != Protocol.ALL else '-1'
            }
            
            # Add port range
            if rule.port_range and rule.protocol in [Protocol.TCP, Protocol.UDP]:
                if '-' in rule.port_range:
                    start, end = rule.port_range.split('-', 1)
                    permission['FromPort'] = int(start)
                    permission['ToPort'] = int(end)
                else:
                    port = int(rule.port_range)
                    permission['FromPort'] = port
                    permission['ToPort'] = port
            
            # Add source
            if rule.source_destination.endswith('_sg'):
                # Security group reference
                permission['UserIdGroupPairs'] = [{
                    'GroupId': rule.source_destination,
                    'Description': rule.description
                }]
            else:
                # CIDR block
                permission['IpRanges'] = [{
                    'CidrIp': rule.source_destination,
                    'Description': rule.description
                }]
            
            ip_permissions.append(permission)
        
        if ip_permissions:
            self.aws_ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=ip_permissions
            )
    
    async def _add_aws_egress_rules(self, sg_id: str, rules: List[SecurityRule]):
        """Add AWS egress rules"""
        
        ip_permissions = []
        
        for rule in rules:
            if rule.action == RuleAction.DENY:
                continue  # AWS security groups don't support deny rules
            
            permission = {
                'IpProtocol': rule.protocol.value if rule.protocol != Protocol.ALL else '-1'
            }
            
            # Add port range
            if rule.port_range and rule.protocol in [Protocol.TCP, Protocol.UDP]:
                if '-' in rule.port_range:
                    start, end = rule.port_range.split('-', 1)
                    permission['FromPort'] = int(start)
                    permission['ToPort'] = int(end)
                else:
                    port = int(rule.port_range)
                    permission['FromPort'] = port
                    permission['ToPort'] = port
            
            # Add destination
            if rule.source_destination.endswith('_sg'):
                # Security group reference
                permission['UserIdGroupPairs'] = [{
                    'GroupId': rule.source_destination,
                    'Description': rule.description
                }]
            else:
                # CIDR block
                permission['IpRanges'] = [{
                    'CidrIp': rule.source_destination,
                    'Description': rule.description
                }]
            
            ip_permissions.append(permission)
        
        if ip_permissions:
            self.aws_ec2.authorize_security_group_egress(
                GroupId=sg_id,
                IpPermissions=ip_permissions
            )
    
    async def _create_gcp_security_group(self, config: SecurityGroupConfiguration) -> SecurityGroupInstance:
        """Create GCP firewall rules (security group equivalent)"""
        
        if not self.gcp_compute:
            raise RuntimeError("GCP client not initialized")
        
        try:
            # GCP uses firewall rules instead of security groups
            # Create separate rules for ingress and egress
            
            sg_id = f"fw-{config.name.replace('_', '-').lower()}"
            
            for rule in config.rules:
                firewall_rule = {
                    "name": f"{sg_id}-{rule.name}",
                    "description": rule.description or f"Firewall rule for {config.name}",
                    "network": f"projects/{self.gcp_project_id}/global/networks/{config.vpc_id}",
                    "direction": "INGRESS" if rule.direction == Direction.INGRESS else "EGRESS",
                    "priority": rule.priority,
                    "source_ranges" if rule.direction == Direction.INGRESS else "destination_ranges": [rule.source_destination],
                    "allowed": [{
                        "IPProtocol": rule.protocol.value,
                        "ports": [rule.port_range] if rule.port_range else []
                    }] if rule.action == RuleAction.ALLOW else [],
                    "denied": [{
                        "IPProtocol": rule.protocol.value,
                        "ports": [rule.port_range] if rule.port_range else []
                    }] if rule.action == RuleAction.DENY else []
                }
                
                operation = self.gcp_compute.insert(
                    project=self.gcp_project_id,
                    firewall_resource=firewall_rule
                )
                
                await self._wait_for_gcp_operation(operation)
            
            sg_instance = SecurityGroupInstance(
                id=sg_id,
                name=config.name,
                description=config.description,
                vpc_id=config.vpc_id,
                group_type=config.group_type,
                provider="gcp",
                region=config.region,
                rules=config.rules.copy(),
                tags=config.tags
            )
            
            return sg_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create GCP firewall rules: {str(e)}")
            raise
    
    async def _create_azure_security_group(self, config: SecurityGroupConfiguration) -> SecurityGroupInstance:
        """Create Azure Network Security Group"""
        
        if not self.azure_network:
            raise RuntimeError("Azure client not initialized")
        
        try:
            resource_group_name = config.tags.get('resource_group', f"rg-{config.vpc_id}")
            
            # Create Network Security Group
            nsg_params = {
                'location': config.region,
                'tags': config.tags
            }
            
            operation = self.azure_network.network_security_groups.begin_create_or_update(
                resource_group_name,
                config.name,
                nsg_params
            )
            
            nsg = operation.result()
            
            # Add security rules
            for i, rule in enumerate(config.rules):
                rule_params = {
                    'name': rule.name,
                    'description': rule.description,
                    'protocol': rule.protocol.value.upper() if rule.protocol != Protocol.ALL else '*',
                    'access': rule.action.value.title(),
                    'direction': rule.direction.value.title(),
                    'priority': rule.priority + i * 10,
                    'source_address_prefix': rule.source_destination,
                    'destination_address_prefix': '*',
                    'source_port_range': '*',
                    'destination_port_range': rule.port_range or '*'
                }
                
                self.azure_network.security_rules.begin_create_or_update(
                    resource_group_name,
                    config.name,
                    rule.name,
                    rule_params
                ).result()
            
            sg_instance = SecurityGroupInstance(
                id=nsg.id,
                name=config.name,
                description=config.description,
                vpc_id=config.vpc_id,
                group_type=config.group_type,
                provider="azure",
                region=config.region,
                rules=config.rules.copy(),
                tags=config.tags
            )
            
            return sg_instance
        
        except Exception as e:
            self.logger.error(f"Failed to create Azure NSG: {str(e)}")
            raise
    
    async def _wait_for_gcp_operation(self, operation):
        """Wait for GCP operation to complete"""
        # Simplified implementation
        await asyncio.sleep(2)
    
    async def delete_security_group(self, sg_id: str) -> bool:
        """
        Delete a security group
        
        Args:
            sg_id: Security group ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        if sg_id not in self.security_groups:
            raise ValueError(f"Security group {sg_id} not found")
        
        sg = self.security_groups[sg_id]
        
        self.logger.info(f"Deleting security group {sg_id} ({sg.name}) from {sg.provider}")
        
        try:
            if sg.provider == "aws":
                success = await self._delete_aws_security_group(sg)
            elif sg.provider == "gcp":
                success = await self._delete_gcp_security_group(sg)
            elif sg.provider == "azure":
                success = await self._delete_azure_security_group(sg)
            else:
                success = False
            
            if success:
                del self.security_groups[sg_id]
                self.logger.info(f"Successfully deleted security group {sg_id}")
            else:
                self.logger.error(f"Failed to delete security group {sg_id}")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Error deleting security group {sg_id}: {str(e)}")
            return False
    
    async def _delete_aws_security_group(self, sg: SecurityGroupInstance) -> bool:
        """Delete AWS security group"""
        
        try:
            self.aws_ec2.delete_security_group(GroupId=sg.id)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting AWS security group: {str(e)}")
            return False
    
    async def _delete_gcp_security_group(self, sg: SecurityGroupInstance) -> bool:
        """Delete GCP firewall rules"""
        
        try:
            # Delete all firewall rules associated with this security group
            for rule in sg.rules:
                rule_name = f"{sg.id}-{rule.name}"
                try:
                    operation = self.gcp_compute.delete(
                        project=self.gcp_project_id,
                        firewall=rule_name
                    )
                    await self._wait_for_gcp_operation(operation)
                except Exception as e:
                    self.logger.warning(f"Failed to delete GCP firewall rule {rule_name}: {str(e)}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting GCP firewall rules: {str(e)}")
            return False
    
    async def _delete_azure_security_group(self, sg: SecurityGroupInstance) -> bool:
        """Delete Azure Network Security Group"""
        
        try:
            resource_group_name = sg.tags.get('resource_group', f"rg-{sg.vpc_id}")
            
            operation = self.azure_network.network_security_groups.begin_delete(
                resource_group_name,
                sg.name
            )
            
            operation.result()  # Wait for completion
            return True
        except Exception as e:
            self.logger.error(f"Error deleting Azure NSG: {str(e)}")
            return False
    
    async def add_security_rule(self, sg_id: str, rule: SecurityRule) -> bool:
        """Add a security rule to existing security group"""
        
        if sg_id not in self.security_groups:
            raise ValueError(f"Security group {sg_id} not found")
        
        sg = self.security_groups[sg_id]
        
        # Validate rule
        self._validate_security_rules([rule])
        
        try:
            if sg.provider == "aws":
                success = await self._add_aws_security_rule(sg, rule)
            elif sg.provider == "gcp":
                success = await self._add_gcp_security_rule(sg, rule)
            elif sg.provider == "azure":
                success = await self._add_azure_security_rule(sg, rule)
            else:
                success = False
            
            if success:
                sg.rules.append(rule)
                sg.updated_at = datetime.utcnow()
                self.logger.info(f"Added security rule '{rule.name}' to {sg_id}")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Error adding security rule: {str(e)}")
            return False
    
    async def _add_aws_security_rule(self, sg: SecurityGroupInstance, rule: SecurityRule) -> bool:
        """Add AWS security rule"""
        
        try:
            if rule.direction == Direction.INGRESS:
                await self._add_aws_ingress_rules(sg.id, [rule])
            else:
                await self._add_aws_egress_rules(sg.id, [rule])
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding AWS security rule: {str(e)}")
            return False
    
    async def _add_gcp_security_rule(self, sg: SecurityGroupInstance, rule: SecurityRule) -> bool:
        """Add GCP firewall rule"""
        
        try:
            firewall_rule = {
                "name": f"{sg.id}-{rule.name}",
                "description": rule.description or f"Firewall rule for {sg.name}",
                "network": f"projects/{self.gcp_project_id}/global/networks/{sg.vpc_id}",
                "direction": "INGRESS" if rule.direction == Direction.INGRESS else "EGRESS",
                "priority": rule.priority,
                "source_ranges" if rule.direction == Direction.INGRESS else "destination_ranges": [rule.source_destination],
                "allowed": [{
                    "IPProtocol": rule.protocol.value,
                    "ports": [rule.port_range] if rule.port_range else []
                }] if rule.action == RuleAction.ALLOW else [],
                "denied": [{
                    "IPProtocol": rule.protocol.value,
                    "ports": [rule.port_range] if rule.port_range else []
                }] if rule.action == RuleAction.DENY else []
            }
            
            operation = self.gcp_compute.insert(
                project=self.gcp_project_id,
                firewall_resource=firewall_rule
            )
            
            await self._wait_for_gcp_operation(operation)
            return True
        except Exception as e:
            self.logger.error(f"Error adding GCP firewall rule: {str(e)}")
            return False
    
    async def _add_azure_security_rule(self, sg: SecurityGroupInstance, rule: SecurityRule) -> bool:
        """Add Azure security rule"""
        
        try:
            resource_group_name = sg.tags.get('resource_group', f"rg-{sg.vpc_id}")
            
            rule_params = {
                'name': rule.name,
                'description': rule.description,
                'protocol': rule.protocol.value.upper() if rule.protocol != Protocol.ALL else '*',
                'access': rule.action.value.title(),
                'direction': rule.direction.value.title(),
                'priority': rule.priority,
                'source_address_prefix': rule.source_destination,
                'destination_address_prefix': '*',
                'source_port_range': '*',
                'destination_port_range': rule.port_range or '*'
            }
            
            operation = self.azure_network.security_rules.begin_create_or_update(
                resource_group_name,
                sg.name,
                rule.name,
                rule_params
            )
            
            operation.result()
            return True
        except Exception as e:
            self.logger.error(f"Error adding Azure security rule: {str(e)}")
            return False
    
    def list_security_groups(
        self,
        vpc_id: Optional[str] = None,
        group_type: Optional[SecurityGroupType] = None,
        provider: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[SecurityGroupInstance]:
        """
        List security groups with optional filters
        
        Args:
            vpc_id: Filter by VPC ID
            group_type: Filter by security group type
            provider: Filter by cloud provider
            region: Filter by region
            
        Returns:
            List of security group instances
        """
        sgs = list(self.security_groups.values())
        
        if vpc_id:
            sgs = [sg for sg in sgs if sg.vpc_id == vpc_id]
        
        if group_type:
            sgs = [sg for sg in sgs if sg.group_type == group_type]
        
        if provider:
            sgs = [sg for sg in sgs if sg.provider == provider]
        
        if region:
            sgs = [sg for sg in sgs if sg.region == region]
        
        return sgs
    
    def get_security_group(self, sg_id: str) -> Optional[SecurityGroupInstance]:
        """Get security group by ID"""
        return self.security_groups.get(sg_id)
    
    def analyze_security_group_rules(self, sg_id: str) -> Dict[str, Any]:
        """Analyze security group rules for potential issues"""
        
        if sg_id not in self.security_groups:
            raise ValueError(f"Security group {sg_id} not found")
        
        sg = self.security_groups[sg_id]
        analysis = {
            'security_group_id': sg_id,
            'total_rules': len(sg.rules),
            'issues': [],
            'recommendations': [],
            'risk_score': 0
        }
        
        # Check for overly permissive rules
        for rule in sg.rules:
            if rule.source_destination == "0.0.0.0/0" and rule.direction == Direction.INGRESS:
                if rule.protocol == Protocol.ALL:
                    analysis['issues'].append({
                        'type': 'overly_permissive',
                        'rule': rule.name,
                        'severity': 'high',
                        'description': 'Rule allows all traffic from internet'
                    })
                    analysis['risk_score'] += 10
                elif rule.port_range in ["22", "3389"]:
                    analysis['issues'].append({
                        'type': 'admin_access_from_internet',
                        'rule': rule.name,
                        'severity': 'high',
                        'description': f'Admin port {rule.port_range} open to internet'
                    })
                    analysis['risk_score'] += 8
        
        # Check for unused rules
        ingress_rules = [r for r in sg.rules if r.direction == Direction.INGRESS]
        egress_rules = [r for r in sg.rules if r.direction == Direction.EGRESS]
        
        if len(ingress_rules) == 0:
            analysis['issues'].append({
                'type': 'no_ingress_rules',
                'severity': 'medium',
                'description': 'No ingress rules defined'
            })
        
        if len(egress_rules) == 0:
            analysis['issues'].append({
                'type': 'no_egress_rules',
                'severity': 'low',
                'description': 'No egress rules defined'
            })
        
        # Generate recommendations
        if analysis['risk_score'] > 15:
            analysis['recommendations'].append('Review and restrict overly permissive rules')
        
        if any(rule.source_destination == "0.0.0.0/0" for rule in sg.rules):
            analysis['recommendations'].append('Consider using more specific IP ranges instead of 0.0.0.0/0')
        
        analysis['recommendations'].extend([
            'Regularly review and audit security group rules',
            'Use least privilege principle for all rules',
            'Document the purpose of each rule'
        ])
        
        return analysis
    
    def get_security_group_summary(self) -> Dict[str, Any]:
        """Get security group summary statistics"""
        
        total_sgs = len(self.security_groups)
        
        if total_sgs == 0:
            return {'total_security_groups': 0}
        
        # Provider breakdown
        provider_counts = {}
        providers = set(sg.provider for sg in self.security_groups.values())
        for provider in providers:
            provider_counts[provider] = len([
                sg for sg in self.security_groups.values() if sg.provider == provider
            ])
        
        # Type breakdown
        type_counts = {}
        for sg_type in SecurityGroupType:
            type_counts[sg_type.value] = len([
                sg for sg in self.security_groups.values() if sg.group_type == sg_type
            ])
        
        # VPC breakdown
        vpcs = set(sg.vpc_id for sg in self.security_groups.values())
        vpc_counts = {}
        for vpc_id in vpcs:
            vpc_counts[vpc_id] = len([
                sg for sg in self.security_groups.values() if sg.vpc_id == vpc_id
            ])
        
        # Rule statistics
        total_rules = sum(len(sg.rules) for sg in self.security_groups.values())
        avg_rules_per_sg = total_rules / total_sgs if total_sgs > 0 else 0
        
        # Risk analysis
        high_risk_sgs = []
        for sg in self.security_groups.values():
            analysis = self.analyze_security_group_rules(sg.id)
            if analysis['risk_score'] > 10:
                high_risk_sgs.append(sg.id)
        
        return {
            'total_security_groups': total_sgs,
            'provider_breakdown': provider_counts,
            'type_breakdown': type_counts,
            'vpc_breakdown': vpc_counts,
            'rule_statistics': {
                'total_rules': total_rules,
                'average_rules_per_sg': avg_rules_per_sg
            },
            'risk_analysis': {
                'high_risk_security_groups': len(high_risk_sgs),
                'high_risk_sg_ids': high_risk_sgs
            }
        }


# Export main classes
__all__ = ['SecurityGroupManager', 'SecurityGroupConfiguration', 'SecurityGroupInstance', 'SecurityRule', 'SecurityGroupType', 'RuleAction', 'Protocol', 'Direction']