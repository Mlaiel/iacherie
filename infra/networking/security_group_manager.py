"""
Security Group Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Security Group Management for Multi-Cloud Infrastructure
# Advanced security group automation with compliance and best practices
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from google.cloud import compute_v1
import ipaddress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityGroupDirection(Enum):
    """Security group rule direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class Protocol(Enum):
    """Network protocols."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "-1"

class RiskLevel(Enum):
    """Risk level for security group rules."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityGroupRule:
    """Security group rule definition."""
    direction: SecurityGroupDirection
    protocol: Protocol
    port_range: Tuple[int, int]  # (from_port, to_port)
    source_destination: str  # CIDR, security group ID, or "any"
    description: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    compliance_tags: List[str] = field(default_factory=list)

@dataclass
class SecurityGroup:
    """Security group definition."""
    id: str
    name: str
    description: str
    vpc_id: str
    provider: str
    rules: List[SecurityGroupRule] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None

@dataclass
class SecurityGroupAnalysis:
    """Security group analysis results."""
    group_id: str
    risk_score: float
    violations: List[str]
    recommendations: List[str]
    compliance_status: Dict[str, bool]
    analyzed_at: datetime

class SecurityGroupManager:
    """
    Enterprise-grade security group management system.
    
    Provides comprehensive security group management across AWS, Azure, and GCP
    with automated compliance checking, risk assessment, and best practices enforcement.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize security group manager."""
        self.config = config
        self.security_groups = {}
        self.compliance_rules = self._load_compliance_rules()
        
        # Cloud clients
        self.aws_clients = {}
        self.azure_clients = {}
        self.gcp_clients = {}
        
        self._initialize_cloud_clients()
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS clients
            if self.config.get('aws', {}).get('enabled', False):
                session = boto3.Session(
                    aws_access_key_id=self.config['aws'].get('access_key'),
                    aws_secret_access_key=self.config['aws'].get('secret_key'),
                    region_name=self.config['aws'].get('region', 'us-east-1')
                )
                
                self.aws_clients = {
                    'ec2': session.client('ec2'),
                    'vpc': session.client('ec2')  # VPC is part of EC2
                }
            
            # Azure clients
            if self.config.get('azure', {}).get('enabled', False):
                credential = DefaultAzureCredential()
                subscription_id = self.config['azure']['subscription_id']
                
                self.azure_clients = {
                    'network': NetworkManagementClient(credential, subscription_id)
                }
            
            # GCP clients
            if self.config.get('gcp', {}).get('enabled', False):
                self.gcp_clients = {
                    'compute': compute_v1.FirewallsClient(),
                    'instances': compute_v1.InstancesClient()
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud clients: {e}")
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules for security groups."""
        return {
            "no_wide_open_ssh": {
                "description": "SSH (port 22) should not be open to 0.0.0.0/0",
                "port": 22,
                "protocol": "tcp",
                "max_cidr": "0.0.0.0/0"
            },
            "no_wide_open_rdp": {
                "description": "RDP (port 3389) should not be open to 0.0.0.0/0",
                "port": 3389,
                "protocol": "tcp",
                "max_cidr": "0.0.0.0/0"
            },
            "no_wide_open_http": {
                "description": "HTTP (port 80) from anywhere should be carefully reviewed",
                "port": 80,
                "protocol": "tcp",
                "risk_level": "medium"
            },
            "require_https": {
                "description": "HTTPS (port 443) should be preferred over HTTP",
                "port": 443,
                "protocol": "tcp",
                "preferred": True
            },
            "database_ports_restricted": {
                "description": "Database ports should not be open to the internet",
                "ports": [3306, 5432, 1433, 1521, 27017],
                "max_cidr": "0.0.0.0/0"
            }
        }
    
    async def create_security_group(self, 
                                  provider: str,
                                  name: str,
                                  description: str,
                                  vpc_id: str,
                                  rules: List[SecurityGroupRule],
                                  tags: Optional[Dict[str, str]] = None) -> SecurityGroup:
        """Create a new security group."""
        try:
            if provider.lower() == 'aws':
                return await self._create_aws_security_group(name, description, vpc_id, rules, tags)
            elif provider.lower() == 'azure':
                return await self._create_azure_security_group(name, description, vpc_id, rules, tags)
            elif provider.lower() == 'gcp':
                return await self._create_gcp_security_group(name, description, vpc_id, rules, tags)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to create security group: {e}")
            raise
    
    async def _create_aws_security_group(self,
                                       name: str,
                                       description: str,
                                       vpc_id: str,
                                       rules: List[SecurityGroupRule],
                                       tags: Optional[Dict[str, str]] = None) -> SecurityGroup:
        """Create AWS security group."""
        try:
            ec2_client = self.aws_clients['ec2']
            
            # Create security group
            response = ec2_client.create_security_group(
                GroupName=name,
                Description=description,
                VpcId=vpc_id
            )
            
            group_id = response['GroupId']
            
            # Add tags
            if tags:
                tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
                ec2_client.create_tags(
                    Resources=[group_id],
                    Tags=tag_list
                )
            
            # Add rules
            await self._add_aws_security_group_rules(group_id, rules)
            
            # Create security group object
            security_group = SecurityGroup(
                id=group_id,
                name=name,
                description=description,
                vpc_id=vpc_id,
                provider="aws",
                rules=rules,
                tags=tags or {},
                created_at=datetime.utcnow()
            )
            
            self.security_groups[group_id] = security_group
            logger.info(f"Created AWS security group: {name} ({group_id})")
            
            return security_group
            
        except Exception as e:
            logger.error(f"Failed to create AWS security group: {e}")
            raise
    
    async def _add_aws_security_group_rules(self,
                                          group_id -> None: str,
                                          rules -> None: List[SecurityGroupRule]) -> None:
        """Add rules to AWS security group."""
        try:
            ec2_client = self.aws_clients['ec2']
            
            inbound_rules = []
            outbound_rules = []
            
            for rule in rules:
                aws_rule = {
                    'IpProtocol': rule.protocol.value,
                    'FromPort': rule.port_range[0],
                    'ToPort': rule.port_range[1]
                }
                
                # Handle source/destination
                if rule.source_destination.startswith('sg-'):
                    aws_rule['UserIdGroupPairs'] = [{'GroupId': rule.source_destination}]
                else:
                    aws_rule['IpRanges'] = [{'CidrIp': rule.source_destination, 'Description': rule.description}]
                
                if rule.direction == SecurityGroupDirection.INBOUND:
                    inbound_rules.append(aws_rule)
                else:
                    outbound_rules.append(aws_rule)
            
            # Add inbound rules
            if inbound_rules:
                ec2_client.authorize_security_group_ingress(
                    GroupId=group_id,
                    IpPermissions=inbound_rules
                )
            
            # Add outbound rules
            if outbound_rules:
                ec2_client.authorize_security_group_egress(
                    GroupId=group_id,
                    IpPermissions=outbound_rules
                )
                
        except Exception as e:
            logger.error(f"Failed to add AWS security group rules: {e}")
            raise
    
    async def _create_azure_security_group(self,
                                         name: str,
                                         description: str,
                                         vpc_id: str,
                                         rules: List[SecurityGroupRule],
                                         tags: Optional[Dict[str, str]] = None) -> SecurityGroup:
        """Create Azure Network Security Group."""
        try:
            network_client = self.azure_clients['network']
            resource_group = self.config['azure']['resource_group']
            location = self.config['azure']['location']
            
            # Convert rules to Azure format
            azure_rules = []
            priority = 100
            
            for rule in rules:
                azure_rule = {
                    'name': f"rule-{priority}",
                    'protocol': rule.protocol.value.upper(),
                    'source_address_prefix': rule.source_destination,
                    'destination_address_prefix': '*',
                    'access': 'Allow',
                    'priority': priority,
                    'direction': 'Inbound' if rule.direction == SecurityGroupDirection.INBOUND else 'Outbound'
                }
                
                if rule.port_range[0] == rule.port_range[1]:
                    azure_rule['destination_port_range'] = str(rule.port_range[0])
                else:
                    azure_rule['destination_port_range'] = f"{rule.port_range[0]}-{rule.port_range[1]}"
                
                azure_rules.append(azure_rule)
                priority += 10
            
            # Create NSG
            nsg_params = {
                'location': location,
                'security_rules': azure_rules,
                'tags': tags or {}
            }
            
            operation = network_client.network_security_groups.begin_create_or_update(
                resource_group,
                name,
                nsg_params
            )
            
            nsg = operation.result()
            
            # Create security group object
            security_group = SecurityGroup(
                id=nsg.id,
                name=name,
                description=description,
                vpc_id=vpc_id,
                provider="azure",
                rules=rules,
                tags=tags or {},
                created_at=datetime.utcnow()
            )
            
            self.security_groups[nsg.id] = security_group
            logger.info(f"Created Azure NSG: {name}")
            
            return security_group
            
        except Exception as e:
            logger.error(f"Failed to create Azure NSG: {e}")
            raise
    
    async def _create_gcp_security_group(self,
                                       name: str,
                                       description: str,
                                       vpc_id: str,
                                       rules: List[SecurityGroupRule],
                                       tags: Optional[Dict[str, str]] = None) -> SecurityGroup:
        """Create GCP Firewall Rules (equivalent to security groups)."""
        try:
            firewall_client = self.gcp_clients['compute']
            project_id = self.config['gcp']['project_id']
            
            # GCP uses separate firewall rules instead of security groups
            firewall_rules = []
            
            for i, rule in enumerate(rules):
                firewall_rule = {
                    'name': f"{name}-rule-{i}",
                    'description': rule.description,
                    'network': f"projects/{project_id}/global/networks/{vpc_id}",
                    'priority': 1000,
                    'target_tags': [name]
                }
                
                if rule.direction == SecurityGroupDirection.INBOUND:
                    firewall_rule['direction'] = 'INGRESS'
                    firewall_rule['source_ranges'] = [rule.source_destination]
                else:
                    firewall_rule['direction'] = 'EGRESS'
                    firewall_rule['destination_ranges'] = [rule.source_destination]
                
                # Add allowed protocols and ports
                allowed = []
                if rule.protocol == Protocol.ALL:
                    allowed.append({'IP_protocol': 'all'})
                else:
                    port_spec = {
                        'IP_protocol': rule.protocol.value
                    }
                    if rule.port_range[0] != -1:
                        if rule.port_range[0] == rule.port_range[1]:
                            port_spec['ports'] = [str(rule.port_range[0])]
                        else:
                            port_spec['ports'] = [f"{rule.port_range[0]}-{rule.port_range[1]}"]
                    
                    allowed.append(port_spec)
                
                firewall_rule['allowed'] = allowed
                firewall_rules.append(firewall_rule)
                
                # Create firewall rule
                operation = firewall_client.insert(
                    project=project_id,
                    firewall_resource=firewall_rule
                )
                
                # Wait for operation to complete
                # Note: In real implementation, you'd wait for the operation
            
            # Create security group object
            security_group = SecurityGroup(
                id=f"gcp-{name}",
                name=name,
                description=description,
                vpc_id=vpc_id,
                provider="gcp",
                rules=rules,
                tags=tags or {},
                created_at=datetime.utcnow()
            )
            
            self.security_groups[f"gcp-{name}"] = security_group
            logger.info(f"Created GCP firewall rules for: {name}")
            
            return security_group
            
        except Exception as e:
            logger.error(f"Failed to create GCP firewall rules: {e}")
            raise
    
    async def analyze_security_group(self, group_id: str) -> SecurityGroupAnalysis:
        """Analyze security group for risks and compliance."""
        try:
            if group_id not in self.security_groups:
                raise ValueError(f"Security group not found: {group_id}")
            
            security_group = self.security_groups[group_id]
            violations = []
            recommendations = []
            risk_score = 0.0
            compliance_status = {}
            
            for rule in security_group.rules:
                # Check for wide open SSH
                if (rule.port_range[0] <= 22 <= rule.port_range[1] and 
                    rule.source_destination == "0.0.0.0/0"):
                    violations.append("SSH (port 22) is open to the internet")
                    recommendations.append("Restrict SSH access to specific IP ranges")
                    risk_score += 30.0
                
                # Check for wide open RDP
                if (rule.port_range[0] <= 3389 <= rule.port_range[1] and 
                    rule.source_destination == "0.0.0.0/0"):
                    violations.append("RDP (port 3389) is open to the internet")
                    recommendations.append("Restrict RDP access to specific IP ranges")
                    risk_score += 30.0
                
                # Check for database ports
                db_ports = [3306, 5432, 1433, 1521, 27017]
                for db_port in db_ports:
                    if (rule.port_range[0] <= db_port <= rule.port_range[1] and 
                        rule.source_destination == "0.0.0.0/0"):
                        violations.append(f"Database port {db_port} is open to the internet")
                        recommendations.append(f"Restrict database port {db_port} access")
                        risk_score += 25.0
                
                # Check for overly broad CIDR ranges
                if rule.source_destination != "0.0.0.0/0":
                    try:
                        network = ipaddress.ip_network(rule.source_destination, strict=False)
                        if network.num_addresses > 1000000:  # Large network
                            violations.append(f"Very broad CIDR range: {rule.source_destination}")
                            recommendations.append("Use more specific CIDR ranges")
                            risk_score += 10.0
                    except:
                        pass  # Not a CIDR range
            
            # Check compliance
            compliance_status = {
                "ssh_restricted": not any("SSH" in v for v in violations),
                "rdp_restricted": not any("RDP" in v for v in violations),
                "database_secure": not any("Database" in v for v in violations),
                "cidr_appropriate": not any("broad CIDR" in v for v in violations)
            }
            
            # Additional recommendations
            if not violations:
                recommendations.append("Security group follows best practices")
            else:
                recommendations.append("Review and restrict overly permissive rules")
            
            # Cap risk score at 100
            risk_score = min(risk_score, 100.0)
            
            analysis = SecurityGroupAnalysis(
                group_id=group_id,
                risk_score=risk_score,
                violations=violations,
                recommendations=recommendations,
                compliance_status=compliance_status,
                analyzed_at=datetime.utcnow()
            )
            
            logger.info(f"Analyzed security group {group_id}: Risk score {risk_score:.1f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze security group: {e}")
            raise
    
    async def get_security_groups(self, provider: str) -> List[SecurityGroup]:
        """Get all security groups for a provider."""
        try:
            if provider.lower() == 'aws':
                return await self._get_aws_security_groups()
            elif provider.lower() == 'azure':
                return await self._get_azure_security_groups()
            elif provider.lower() == 'gcp':
                return await self._get_gcp_security_groups()
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to get security groups: {e}")
            raise
    
    async def _get_aws_security_groups(self) -> List[SecurityGroup]:
        """Get AWS security groups."""
        try:
            ec2_client = self.aws_clients['ec2']
            response = ec2_client.describe_security_groups()
            
            security_groups = []
            for sg in response['SecurityGroups']:
                # Convert AWS rules to our format
                rules = []
                
                # Inbound rules
                for rule in sg['IpPermissions']:
                    for ip_range in rule.get('IpRanges', []):
                        sg_rule = SecurityGroupRule(
                            direction=SecurityGroupDirection.INBOUND,
                            protocol=Protocol(rule['IpProtocol']) if rule['IpProtocol'] != '-1' else Protocol.ALL,
                            port_range=(rule.get('FromPort', -1), rule.get('ToPort', -1)),
                            source_destination=ip_range['CidrIp'],
                            description=ip_range.get('Description', ''),
                            risk_level=self._assess_rule_risk(rule)
                        )
                        rules.append(sg_rule)
                
                # Outbound rules
                for rule in sg['IpPermissionsEgress']:
                    for ip_range in rule.get('IpRanges', []):
                        sg_rule = SecurityGroupRule(
                            direction=SecurityGroupDirection.OUTBOUND,
                            protocol=Protocol(rule['IpProtocol']) if rule['IpProtocol'] != '-1' else Protocol.ALL,
                            port_range=(rule.get('FromPort', -1), rule.get('ToPort', -1)),
                            source_destination=ip_range['CidrIp'],
                            description=ip_range.get('Description', ''),
                            risk_level=self._assess_rule_risk(rule)
                        )
                        rules.append(sg_rule)
                
                # Convert tags
                tags = {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])}
                
                security_group = SecurityGroup(
                    id=sg['GroupId'],
                    name=sg['GroupName'],
                    description=sg['Description'],
                    vpc_id=sg['VpcId'],
                    provider="aws",
                    rules=rules,
                    tags=tags
                )
                
                security_groups.append(security_group)
                self.security_groups[sg['GroupId']] = security_group
            
            logger.info(f"Retrieved {len(security_groups)} AWS security groups")
            return security_groups
            
        except Exception as e:
            logger.error(f"Failed to get AWS security groups: {e}")
            raise
    
    async def _get_azure_security_groups(self) -> List[SecurityGroup]:
        """Get Azure Network Security Groups."""
        try:
            network_client = self.azure_clients['network']
            resource_group = self.config['azure']['resource_group']
            
            nsgs = network_client.network_security_groups.list(resource_group)
            security_groups = []
            
            for nsg in nsgs:
                # Convert Azure rules to our format
                rules = []
                
                for rule in nsg.security_rules:
                    # Determine direction
                    direction = (SecurityGroupDirection.INBOUND 
                               if rule.direction.lower() == 'inbound' 
                               else SecurityGroupDirection.OUTBOUND)
                    
                    # Parse port range
                    if rule.destination_port_range:
                        if '-' in rule.destination_port_range:
                            from_port, to_port = map(int, rule.destination_port_range.split('-'))
                        else:
                            from_port = to_port = int(rule.destination_port_range)
                    else:
                        from_port = to_port = -1
                    
                    sg_rule = SecurityGroupRule(
                        direction=direction,
                        protocol=Protocol(rule.protocol.lower()),
                        port_range=(from_port, to_port),
                        source_destination=rule.source_address_prefix,
                        description=f"Azure rule: {rule.name}",
                        risk_level=RiskLevel.MEDIUM
                    )
                    rules.append(sg_rule)
                
                security_group = SecurityGroup(
                    id=nsg.id,
                    name=nsg.name,
                    description=f"Azure NSG: {nsg.name}",
                    vpc_id="azure-vnet",  # Azure uses VNets
                    provider="azure",
                    rules=rules,
                    tags=nsg.tags or {}
                )
                
                security_groups.append(security_group)
                self.security_groups[nsg.id] = security_group
            
            logger.info(f"Retrieved {len(security_groups)} Azure NSGs")
            return security_groups
            
        except Exception as e:
            logger.error(f"Failed to get Azure NSGs: {e}")
            raise
    
    async def _get_gcp_security_groups(self) -> List[SecurityGroup]:
        """Get GCP Firewall Rules."""
        try:
            firewall_client = self.gcp_clients['compute']
            project_id = self.config['gcp']['project_id']
            
            firewall_rules = firewall_client.list(project=project_id)
            security_groups = []
            
            # Group firewall rules by target tags (simulating security groups)
            grouped_rules = {}
            
            for rule in firewall_rules:
                target_tag = rule.target_tags[0] if rule.target_tags else 'default'
                if target_tag not in grouped_rules:
                    grouped_rules[target_tag] = []
                grouped_rules[target_tag].append(rule)
            
            for tag, rules in grouped_rules.items():
                sg_rules = []
                
                for rule in rules:
                    # Convert GCP rule to our format
                    direction = (SecurityGroupDirection.INBOUND 
                               if rule.direction == 'INGRESS' 
                               else SecurityGroupDirection.OUTBOUND)
                    
                    for allowed in rule.allowed:
                        protocol = Protocol(allowed.ip_protocol.lower()) if allowed.ip_protocol != 'all' else Protocol.ALL
                        
                        if allowed.ports:
                            for port_range in allowed.ports:
                                if '-' in port_range:
                                    from_port, to_port = map(int, port_range.split('-'))
                                else:
                                    from_port = to_port = int(port_range)
                                
                                sg_rule = SecurityGroupRule(
                                    direction=direction,
                                    protocol=protocol,
                                    port_range=(from_port, to_port),
                                    source_destination=rule.source_ranges[0] if rule.source_ranges else "0.0.0.0/0",
                                    description=rule.description or "",
                                    risk_level=RiskLevel.MEDIUM
                                )
                                sg_rules.append(sg_rule)
                        else:
                            sg_rule = SecurityGroupRule(
                                direction=direction,
                                protocol=protocol,
                                port_range=(-1, -1),
                                source_destination=rule.source_ranges[0] if rule.source_ranges else "0.0.0.0/0",
                                description=rule.description or "",
                                risk_level=RiskLevel.MEDIUM
                            )
                            sg_rules.append(sg_rule)
                
                security_group = SecurityGroup(
                    id=f"gcp-{tag}",
                    name=f"firewall-{tag}",
                    description=f"GCP firewall rules for tag: {tag}",
                    vpc_id="gcp-vpc",
                    provider="gcp",
                    rules=sg_rules,
                    tags={}
                )
                
                security_groups.append(security_group)
                self.security_groups[f"gcp-{tag}"] = security_group
            
            logger.info(f"Retrieved {len(security_groups)} GCP firewall rule groups")
            return security_groups
            
        except Exception as e:
            logger.error(f"Failed to get GCP firewall rules: {e}")
            raise
    
    def _assess_rule_risk(self, rule: Dict[str, Any]) -> RiskLevel:
        """Assess risk level of a security group rule."""
        # Simple risk assessment based on port and source
        from_port = rule.get('FromPort', -1)
        to_port = rule.get('ToPort', -1)
        
        # High risk ports open to internet
        high_risk_ports = [22, 3389, 3306, 5432, 1433, 1521, 27017]
        if any(from_port <= port <= to_port for port in high_risk_ports):
            return RiskLevel.HIGH
        
        # Medium risk for common service ports
        medium_risk_ports = [80, 443, 8080, 8443]
        if any(from_port <= port <= to_port for port in medium_risk_ports):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    async def update_security_group(self,
                                  group_id: str,
                                  rules: List[SecurityGroupRule]) -> SecurityGroup:
        """Update security group rules."""
        try:
            if group_id not in self.security_groups:
                raise ValueError(f"Security group not found: {group_id}")
            
            security_group = self.security_groups[group_id]
            
            if security_group.provider == 'aws':
                return await self._update_aws_security_group(group_id, rules)
            elif security_group.provider == 'azure':
                return await self._update_azure_security_group(group_id, rules)
            elif security_group.provider == 'gcp':
                return await self._update_gcp_security_group(group_id, rules)
            else:
                raise ValueError(f"Unsupported provider: {security_group.provider}")
                
        except Exception as e:
            logger.error(f"Failed to update security group: {e}")
            raise
    
    async def _update_aws_security_group(self,
                                       group_id: str,
                                       rules: List[SecurityGroupRule]) -> SecurityGroup:
        """Update AWS security group."""
        try:
            ec2_client = self.aws_clients['ec2']
            
            # First, remove all existing rules
            sg_response = ec2_client.describe_security_groups(GroupIds=[group_id])
            sg = sg_response['SecurityGroups'][0]
            
            # Remove inbound rules
            if sg['IpPermissions']:
                ec2_client.revoke_security_group_ingress(
                    GroupId=group_id,
                    IpPermissions=sg['IpPermissions']
                )
            
            # Remove outbound rules (except default)
            if sg['IpPermissionsEgress']:
                ec2_client.revoke_security_group_egress(
                    GroupId=group_id,
                    IpPermissions=sg['IpPermissionsEgress']
                )
            
            # Add new rules
            await self._add_aws_security_group_rules(group_id, rules)
            
            # Update our record
            security_group = self.security_groups[group_id]
            security_group.rules = rules
            security_group.last_modified = datetime.utcnow()
            
            logger.info(f"Updated AWS security group: {group_id}")
            return security_group
            
        except Exception as e:
            logger.error(f"Failed to update AWS security group: {e}")
            raise
    
    async def _update_azure_security_group(self,
                                         group_id: str,
                                         rules: List[SecurityGroupRule]) -> SecurityGroup:
        """Update Azure Network Security Group."""
        # Implementation would update Azure NSG rules
        pass
    
    async def _update_gcp_security_group(self,
                                       group_id: str,
                                       rules: List[SecurityGroupRule]) -> SecurityGroup:
        """Update GCP Firewall Rules."""
        # Implementation would update GCP firewall rules
        pass
    
    async def delete_security_group(self, group_id: str) -> bool:
        """Delete security group."""
        try:
            if group_id not in self.security_groups:
                raise ValueError(f"Security group not found: {group_id}")
            
            security_group = self.security_groups[group_id]
            
            if security_group.provider == 'aws':
                success = await self._delete_aws_security_group(group_id)
            elif security_group.provider == 'azure':
                success = await self._delete_azure_security_group(group_id)
            elif security_group.provider == 'gcp':
                success = await self._delete_gcp_security_group(group_id)
            else:
                raise ValueError(f"Unsupported provider: {security_group.provider}")
            
            if success:
                del self.security_groups[group_id]
                logger.info(f"Deleted security group: {group_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete security group: {e}")
            raise
    
    async def _delete_aws_security_group(self, group_id: str) -> bool:
        """Delete AWS security group."""
        try:
            ec2_client = self.aws_clients['ec2']
            ec2_client.delete_security_group(GroupId=group_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete AWS security group: {e}")
            return False
    
    async def _delete_azure_security_group(self, group_id: str) -> bool:
        """Delete Azure Network Security Group."""
        # Implementation would delete Azure NSG
        return True
    
    async def _delete_gcp_security_group(self, group_id: str) -> bool:
        """Delete GCP Firewall Rules."""
        # Implementation would delete GCP firewall rules
        return True
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report for all security groups."""
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_groups": len(self.security_groups),
                "provider_breakdown": {},
                "risk_analysis": {},
                "compliance_summary": {},
                "recommendations": []
            }
            
            provider_counts = {}
            risk_levels = {}
            total_violations = 0
            
            for group_id, security_group in self.security_groups.items():
                # Count by provider
                provider = security_group.provider
                if provider not in provider_counts:
                    provider_counts[provider] = 0
                provider_counts[provider] += 1
                
                # Analyze each group
                analysis = await self.analyze_security_group(group_id)
                
                # Count risk levels
                if analysis.risk_score < 25:
                    risk_level = "low"
                elif analysis.risk_score < 50:
                    risk_level = "medium"
                elif analysis.risk_score < 75:
                    risk_level = "high"
                else:
                    risk_level = "critical"
                
                if risk_level not in risk_levels:
                    risk_levels[risk_level] = 0
                risk_levels[risk_level] += 1
                
                total_violations += len(analysis.violations)
            
            report["provider_breakdown"] = provider_counts
            report["risk_analysis"] = risk_levels
            report["compliance_summary"] = {
                "total_violations": total_violations,
                "average_risk_score": sum(
                    (await self.analyze_security_group(gid)).risk_score 
                    for gid in self.security_groups.keys()
                ) / len(self.security_groups) if self.security_groups else 0
            }
            
            # Generate top recommendations
            if total_violations > 0:
                report["recommendations"] = [
                    "Review and restrict overly permissive security group rules",
                    "Implement least privilege access principles",
                    "Regularly audit security group configurations",
                    "Use security group references instead of CIDR ranges where possible",
                    "Enable logging and monitoring for security group changes"
                ]
            else:
                report["recommendations"] = [
                    "Security groups follow best practices",
                    "Continue regular compliance monitoring"
                ]
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "aws": {
            "enabled": True,
            "region": "us-east-1"
        },
        "azure": {
            "enabled": True,
            "subscription_id": "your-subscription-id",
            "resource_group": "your-resource-group",
            "location": "East US"
        },
        "gcp": {
            "enabled": True,
            "project_id": "your-project-id"
        }
    }
    
    async def main() -> None:
        # Initialize security group manager
        manager = SecurityGroupManager(config)
        
        # Create example security group rules
        rules = [
            SecurityGroupRule(
                direction=SecurityGroupDirection.INBOUND,
                protocol=Protocol.TCP,
                port_range=(443, 443),
                source_destination="0.0.0.0/0",
                description="HTTPS access",
                risk_level=RiskLevel.LOW
            ),
            SecurityGroupRule(
                direction=SecurityGroupDirection.INBOUND,
                protocol=Protocol.TCP,
                port_range=(22, 22),
                source_destination="10.0.0.0/8",
                description="SSH access from private network",
                risk_level=RiskLevel.LOW
            )
        ]
        
        # Create security group
        sg = await manager.create_security_group(
            provider="aws",
            name="ainflue-web-sg",
            description="Security group for Ainflue web servers",
            vpc_id="vpc-12345678",
            rules=rules,
            tags={"Environment": "production", "Application": "ainflue"}
        )
        
        print(f"Created security group: {sg.name}")
        
        # Analyze security group
        analysis = await manager.analyze_security_group(sg.id)
        print(f"Risk score: {analysis.risk_score}")
        print(f"Violations: {analysis.violations}")
        
        # Generate compliance report
        report = await manager.generate_compliance_report()
        print(f"Total violations: {report['compliance_summary']['total_violations']}")
    
    # Run the example
    asyncio.run(main())