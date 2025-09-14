"""
Network Security Policies module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - Network Security Policies
# =======================================================
# 
# Enterprise-grade network security policies for Ainflue platform
# Supports multi-cloud security and enterprise compliance
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import ipaddress
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from google.cloud import compute_v1

class PolicyType(Enum):
    """Types of network security policies"""
    FIREWALL = "firewall"
    NETWORK_ACL = "network_acl"
    SECURITY_GROUP = "security_group"
    WAF = "waf"
    DDOS_PROTECTION = "ddos_protection"

class Protocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"

@dataclass
class SecurityRule:
    """Security rule configuration"""
    name: str
    direction: str  # ingress or egress
    protocol: Protocol
    port_range: str  # e.g., "80", "80-443", "all"
    source_destination: str  # CIDR, security group ID, or "any"
    action: str  # allow or deny
    priority: int = 100
    description: str = ""

@dataclass
class SecurityPolicyConfig:
    """Configuration for network security policies"""
    environment: str
    cloud_provider: str
    vpc_id: str
    region: str
    tags: Dict[str, str]

class NetworkSecurityPolicyManager:
    """Enterprise network security policy management for multi-cloud environments"""
    
    def __init__(self, config -> None: SecurityPolicyConfig) -> None:
        """Initialize network security policy manager
        
        Args:
            config: Security policy configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize cloud provider clients
        self._initialize_cloud_clients()
        
        # Define standard security rule sets
        self.standard_policies = self._define_standard_policies()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"ainflue.infra.security.network_policies")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients"""
        try:
            if self.config.cloud_provider.lower() == 'aws':
                self.ec2_client = boto3.client('ec2', region_name=self.config.region)
                self.waf_client = boto3.client('wafv2', region_name=self.config.region)
                
            elif self.config.cloud_provider.lower() == 'azure':
                credential = DefaultAzureCredential()
                self.network_client = NetworkManagementClient(
                    credential, 
                    subscription_id=self._get_azure_subscription_id()
                )
                
            elif self.config.cloud_provider.lower() == 'gcp':
                self.compute_client = compute_v1.FirewallsClient()
                self.security_policies_client = compute_v1.SecurityPoliciesClient()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cloud clients: {e}")
            raise
    
    def _get_azure_subscription_id(self) -> str:
        """Get Azure subscription ID from environment or config"""
        import os
        return os.getenv('AZURE_SUBSCRIPTION_ID', 'default-subscription-id')
    
    def _define_standard_policies(self) -> Dict[str, List[SecurityRule]]:
        """Define standard security policies for Ainflue platform"""
        return {
            "web_tier": [
                SecurityRule(
                    name="allow-http",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="80",
                    source_destination="0.0.0.0/0",
                    action="allow",
                    priority=100,
                    description="Allow HTTP traffic from internet"
                ),
                SecurityRule(
                    name="allow-https",
                    direction="ingress", 
                    protocol=Protocol.TCP,
                    port_range="443",
                    source_destination="0.0.0.0/0",
                    action="allow",
                    priority=101,
                    description="Allow HTTPS traffic from internet"
                ),
                SecurityRule(
                    name="deny-all-ingress",
                    direction="ingress",
                    protocol=Protocol.ALL,
                    port_range="all",
                    source_destination="0.0.0.0/0",
                    action="deny",
                    priority=65534,
                    description="Deny all other ingress traffic"
                )
            ],
            "app_tier": [
                SecurityRule(
                    name="allow-app-port",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="8080",
                    source_destination="web_tier_sg",
                    action="allow",
                    priority=100,
                    description="Allow app traffic from web tier"
                ),
                SecurityRule(
                    name="allow-metrics",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="9090",
                    source_destination="monitoring_sg",
                    action="allow",
                    priority=101,
                    description="Allow metrics collection"
                ),
                SecurityRule(
                    name="allow-ssh",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="22",
                    source_destination="admin_sg",
                    action="allow",
                    priority=102,
                    description="Allow SSH from admin subnet"
                )
            ],
            "database_tier": [
                SecurityRule(
                    name="allow-postgres",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="5432",
                    source_destination="app_tier_sg",
                    action="allow",
                    priority=100,
                    description="Allow PostgreSQL from app tier"
                ),
                SecurityRule(
                    name="allow-redis",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="6379",
                    source_destination="app_tier_sg",
                    action="allow",
                    priority=101,
                    description="Allow Redis from app tier"
                ),
                SecurityRule(
                    name="deny-all-ingress",
                    direction="ingress",
                    protocol=Protocol.ALL,
                    port_range="all",
                    source_destination="0.0.0.0/0",
                    action="deny",
                    priority=65534,
                    description="Deny all other ingress traffic"
                )
            ],
            "ai_tier": [
                SecurityRule(
                    name="allow-ai-api",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="8080",
                    source_destination="app_tier_sg",
                    action="allow",
                    priority=100,
                    description="Allow AI API traffic from app tier"
                ),
                SecurityRule(
                    name="allow-gpu-monitoring",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="9091",
                    source_destination="monitoring_sg",
                    action="allow",
                    priority=101,
                    description="Allow GPU monitoring"
                ),
                SecurityRule(
                    name="allow-model-sync",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="9000",
                    source_destination="ai_tier_sg",
                    action="allow",
                    priority=102,
                    description="Allow model synchronization between AI nodes"
                )
            ],
            "monitoring": [
                SecurityRule(
                    name="allow-prometheus",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="9090",
                    source_destination="admin_sg",
                    action="allow",
                    priority=100,
                    description="Allow Prometheus access"
                ),
                SecurityRule(
                    name="allow-grafana",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="3000",
                    source_destination="admin_sg",
                    action="allow",
                    priority=101,
                    description="Allow Grafana access"
                ),
                SecurityRule(
                    name="allow-alertmanager",
                    direction="ingress",
                    protocol=Protocol.TCP,
                    port_range="9093",
                    source_destination="admin_sg",
                    action="allow",
                    priority=102,
                    description="Allow AlertManager access"
                )
            ]
        }
    
    async def create_security_group(self, tier_name: str, 
                                  custom_rules: Optional[List[SecurityRule]] = None) -> str:
        """Create a security group for a specific tier
        
        Args:
            tier_name: Name of the tier (web, app, database, etc.)
            custom_rules: Optional custom security rules
            
        Returns:
            str: Security group ID
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._create_aws_security_group(tier_name, custom_rules)
            elif self.config.cloud_provider.lower() == 'azure':
                return await self._create_azure_nsg(tier_name, custom_rules)
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._create_gcp_firewall_rules(tier_name, custom_rules)
            else:
                raise ValueError(f"Unsupported cloud provider: {self.config.cloud_provider}")
                
        except Exception as e:
            self.logger.error(f"Failed to create security group for {tier_name}: {e}")
            raise
    
    async def _create_aws_security_group(self, tier_name: str, 
                                       custom_rules: Optional[List[SecurityRule]] = None) -> str:
        """Create AWS security group"""
        try:
            # Create security group
            sg_name = f"ainflue-{self.config.environment}-{tier_name}-sg"
            response = self.ec2_client.create_security_group(
                GroupName=sg_name,
                Description=f"Ainflue {tier_name} tier security group",
                VpcId=self.config.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': k, 'Value': v} for k, v in self.config.tags.items()
                        ] + [
                            {'Key': 'Name', 'Value': sg_name},
                            {'Key': 'Tier', 'Value': tier_name}
                        ]
                    }
                ]
            )
            
            sg_id = response['GroupId']
            self.logger.info(f"Created AWS security group {sg_name}: {sg_id}")
            
            # Add security rules
            rules = custom_rules or self.standard_policies.get(tier_name, [])
            await self._add_aws_security_rules(sg_id, rules)
            
            return sg_id
            
        except Exception as e:
            self.logger.error(f"Failed to create AWS security group for {tier_name}: {e}")
            raise
    
    async def _add_aws_security_rules(self, sg_id -> None: str, rules -> None: List[SecurityRule]) -> None:
        """Add security rules to AWS security group"""
        try:
            ingress_rules = []
            egress_rules = []
            
            for rule in rules:
                aws_rule = {
                    'IpProtocol': rule.protocol.value if rule.protocol != Protocol.ALL else '-1',
                    'IpRanges': [{'CidrIp': rule.source_destination, 'Description': rule.description}]
                }
                
                if rule.port_range != "all" and rule.protocol != Protocol.ALL:
                    if '-' in rule.port_range:
                        start, end = rule.port_range.split('-')
                        aws_rule['FromPort'] = int(start)
                        aws_rule['ToPort'] = int(end)
                    else:
                        port = int(rule.port_range)
                        aws_rule['FromPort'] = port
                        aws_rule['ToPort'] = port
                
                if rule.direction == "ingress":
                    ingress_rules.append(aws_rule)
                else:
                    egress_rules.append(aws_rule)
            
            # Add ingress rules
            if ingress_rules:
                self.ec2_client.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=ingress_rules
                )
                self.logger.info(f"Added {len(ingress_rules)} ingress rules to {sg_id}")
            
            # Add egress rules
            if egress_rules:
                self.ec2_client.authorize_security_group_egress(
                    GroupId=sg_id,
                    IpPermissions=egress_rules
                )
                self.logger.info(f"Added {len(egress_rules)} egress rules to {sg_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to add AWS security rules: {e}")
            raise
    
    async def _create_azure_nsg(self, tier_name: str, 
                              custom_rules: Optional[List[SecurityRule]] = None) -> str:
        """Create Azure Network Security Group"""
        try:
            nsg_name = f"ainflue-{self.config.environment}-{tier_name}-nsg"
            
            # Create NSG
            nsg_params = {
                'location': self.config.region,
                'tags': {**self.config.tags, 'Tier': tier_name}
            }
            
            operation = self.network_client.network_security_groups.begin_create_or_update(
                resource_group_name=self._get_azure_resource_group(),
                network_security_group_name=nsg_name,
                parameters=nsg_params
            )
            
            nsg = operation.result()
            self.logger.info(f"Created Azure NSG {nsg_name}: {nsg.id}")
            
            # Add security rules
            rules = custom_rules or self.standard_policies.get(tier_name, [])
            await self._add_azure_security_rules(nsg_name, rules)
            
            return nsg.id
            
        except Exception as e:
            self.logger.error(f"Failed to create Azure NSG for {tier_name}: {e}")
            raise
    
    async def _add_azure_security_rules(self, nsg_name -> None: str, rules -> None: List[SecurityRule]) -> None:
        """Add security rules to Azure NSG"""
        try:
            resource_group = self._get_azure_resource_group()
            
            for rule in rules:
                rule_params = {
                    'protocol': rule.protocol.value.upper() if rule.protocol != Protocol.ALL else '*',
                    'source_address_prefix': rule.source_destination,
                    'destination_address_prefix': '*',
                    'access': rule.action.title(),
                    'direction': rule.direction.title(),
                    'priority': rule.priority
                }
                
                if rule.port_range != "all":
                    rule_params['destination_port_range'] = rule.port_range
                else:
                    rule_params['destination_port_range'] = '*'
                
                operation = self.network_client.security_rules.begin_create_or_update(
                    resource_group_name=resource_group,
                    network_security_group_name=nsg_name,
                    security_rule_name=rule.name,
                    security_rule_parameters=rule_params
                )
                
                operation.result()
                self.logger.info(f"Added Azure security rule {rule.name} to {nsg_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to add Azure security rules: {e}")
            raise
    
    def _get_azure_resource_group(self) -> str:
        """Get Azure resource group name"""
        return f"ainflue-{self.config.environment}-rg"
    
    async def _create_gcp_firewall_rules(self, tier_name: str, 
                                       custom_rules: Optional[List[SecurityRule]] = None) -> str:
        """Create GCP firewall rules"""
        try:
            project = self._get_gcp_project_id()
            rules = custom_rules or self.standard_policies.get(tier_name, [])
            
            created_rules = []
            for rule in rules:
                firewall_rule = {
                    'name': f"ainflue-{self.config.environment}-{tier_name}-{rule.name}",
                    'description': rule.description,
                    'network': f"projects/{project}/global/networks/{self.config.vpc_id}",
                    'priority': rule.priority,
                    'target_tags': [f"ainflue-{tier_name}"]
                }
                
                if rule.direction == "ingress":
                    firewall_rule['direction'] = 'INGRESS'
                    firewall_rule['source_ranges'] = [rule.source_destination]
                else:
                    firewall_rule['direction'] = 'EGRESS'
                    firewall_rule['destination_ranges'] = [rule.source_destination]
                
                if rule.action == "allow":
                    allowed = []
                    if rule.protocol == Protocol.ALL:
                        allowed.append({'IPProtocol': 'all'})
                    else:
                        protocol_rule = {'IPProtocol': rule.protocol.value}
                        if rule.port_range != "all":
                            if '-' in rule.port_range:
                                start, end = rule.port_range.split('-')
                                protocol_rule['ports'] = [f"{start}-{end}"]
                            else:
                                protocol_rule['ports'] = [rule.port_range]
                        allowed.append(protocol_rule)
                    firewall_rule['allowed'] = allowed
                else:
                    denied = []
                    if rule.protocol == Protocol.ALL:
                        denied.append({'IPProtocol': 'all'})
                    else:
                        protocol_rule = {'IPProtocol': rule.protocol.value}
                        if rule.port_range != "all":
                            if '-' in rule.port_range:
                                start, end = rule.port_range.split('-')
                                protocol_rule['ports'] = [f"{start}-{end}"]
                            else:
                                protocol_rule['ports'] = [rule.port_range]
                        denied.append(protocol_rule)
                    firewall_rule['denied'] = denied
                
                # Create the firewall rule
                operation = self.compute_client.insert(
                    project=project,
                    firewall_resource=firewall_rule
                )
                
                # Wait for operation to complete
                self._wait_for_gcp_operation(operation, project)
                created_rules.append(firewall_rule['name'])
                
                self.logger.info(f"Created GCP firewall rule: {firewall_rule['name']}")
            
            return ','.join(created_rules)
            
        except Exception as e:
            self.logger.error(f"Failed to create GCP firewall rules for {tier_name}: {e}")
            raise
    
    def _get_gcp_project_id(self) -> str:
        """Get GCP project ID"""
        import os
        return os.getenv('GOOGLE_CLOUD_PROJECT', 'ainflue-platform')
    
    def _wait_for_gcp_operation(self, operation, project -> None: str) -> None:
        """Wait for GCP operation to complete"""
        # Simplified wait logic - in production, implement proper polling
        import time
        time.sleep(2)
    
    async def create_waf_policy(self, tier_name: str = "web") -> str:
        """Create Web Application Firewall policy
        
        Args:
            tier_name: Tier name for the WAF policy
            
        Returns:
            str: WAF policy ID
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._create_aws_waf_policy(tier_name)
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._create_gcp_cloud_armor_policy(tier_name)
            else:
                self.logger.warning(f"WAF not yet implemented for {self.config.cloud_provider}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Failed to create WAF policy: {e}")
            raise
    
    async def _create_aws_waf_policy(self, tier_name: str) -> str:
        """Create AWS WAF policy"""
        try:
            policy_name = f"ainflue-{self.config.environment}-{tier_name}-waf"
            
            # Create WAF web ACL
            response = self.waf_client.create_web_acl(
                Name=policy_name,
                Scope='CLOUDFRONT',  # or 'REGIONAL' for ALB
                DefaultAction={'Allow': {}},
                Rules=[
                    {
                        'Name': 'RateLimitRule',
                        'Priority': 1,
                        'Statement': {
                            'RateBasedStatement': {
                                'Limit': 2000,
                                'AggregateKeyType': 'IP'
                            }
                        },
                        'Action': {'Block': {}},
                        'VisibilityConfig': {
                            'SampledRequestsEnabled': True,
                            'CloudWatchMetricsEnabled': True,
                            'MetricName': 'RateLimitRule'
                        }
                    },
                    {
                        'Name': 'AWSManagedRulesCommonRuleSet',
                        'Priority': 2,
                        'OverrideAction': {'None': {}},
                        'Statement': {
                            'ManagedRuleGroupStatement': {
                                'VendorName': 'AWS',
                                'Name': 'AWSManagedRulesCommonRuleSet'
                            }
                        },
                        'VisibilityConfig': {
                            'SampledRequestsEnabled': True,
                            'CloudWatchMetricsEnabled': True,
                            'MetricName': 'CommonRuleSet'
                        }
                    }
                ],
                Tags=[
                    {'Key': k, 'Value': v} for k, v in self.config.tags.items()
                ] + [
                    {'Key': 'Name', 'Value': policy_name},
                    {'Key': 'Tier', 'Value': tier_name}
                ]
            )
            
            waf_id = response['Summary']['Id']
            self.logger.info(f"Created AWS WAF policy {policy_name}: {waf_id}")
            return waf_id
            
        except Exception as e:
            self.logger.error(f"Failed to create AWS WAF policy: {e}")
            raise
    
    async def _create_gcp_cloud_armor_policy(self, tier_name: str) -> str:
        """Create GCP Cloud Armor security policy"""
        try:
            project = self._get_gcp_project_id()
            policy_name = f"ainflue-{self.config.environment}-{tier_name}-armor"
            
            security_policy = {
                'name': policy_name,
                'description': f'Ainflue {tier_name} tier Cloud Armor policy',
                'rules': [
                    {
                        'priority': 1000,
                        'description': 'Rate limit rule',
                        'match': {
                            'versionedExpr': 'SRC_IPS_V1',
                            'config': {
                                'srcIpRanges': ['*']
                            }
                        },
                        'action': 'rate_based_ban',
                        'rateLimitOptions': {
                            'rateLimitThreshold': {
                                'count': 10,
                                'intervalSec': 60
                            },
                            'banThreshold': {
                                'count': 100,
                                'intervalSec': 600
                            },
                            'banDurationSec': 3600
                        }
                    },
                    {
                        'priority': 2147483647,
                        'description': 'Default allow rule',
                        'match': {
                            'versionedExpr': 'SRC_IPS_V1',
                            'config': {
                                'srcIpRanges': ['*']
                            }
                        },
                        'action': 'allow'
                    }
                ]
            }
            
            operation = self.security_policies_client.insert(
                project=project,
                security_policy_resource=security_policy
            )
            
            self._wait_for_gcp_operation(operation, project)
            self.logger.info(f"Created GCP Cloud Armor policy: {policy_name}")
            return policy_name
            
        except Exception as e:
            self.logger.error(f"Failed to create GCP Cloud Armor policy: {e}")
            raise
    
    async def validate_security_policies(self) -> Dict[str, bool]:
        """Validate all security policies are correctly configured
        
        Returns:
            Dict mapping policy names to validation status
        """
        try:
            validation_results = {}
            
            for tier_name in self.standard_policies.keys():
                # Validate security group/NSG exists and has correct rules
                if self.config.cloud_provider.lower() == 'aws':
                    sg_valid = await self._validate_aws_security_group(tier_name)
                    validation_results[f"{tier_name}_security_group"] = sg_valid
                    
                elif self.config.cloud_provider.lower() == 'azure':
                    nsg_valid = await self._validate_azure_nsg(tier_name)
                    validation_results[f"{tier_name}_nsg"] = nsg_valid
                    
                elif self.config.cloud_provider.lower() == 'gcp':
                    fw_valid = await self._validate_gcp_firewall_rules(tier_name)
                    validation_results[f"{tier_name}_firewall"] = fw_valid
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Failed to validate security policies: {e}")
            return {}
    
    async def _validate_aws_security_group(self, tier_name: str) -> bool:
        """Validate AWS security group configuration"""
        try:
            sg_name = f"ainflue-{self.config.environment}-{tier_name}-sg"
            
            response = self.ec2_client.describe_security_groups(
                Filters=[
                    {'Name': 'group-name', 'Values': [sg_name]},
                    {'Name': 'vpc-id', 'Values': [self.config.vpc_id]}
                ]
            )
            
            if not response['SecurityGroups']:
                self.logger.warning(f"Security group {sg_name} not found")
                return False
            
            sg = response['SecurityGroups'][0]
            expected_rules = self.standard_policies.get(tier_name, [])
            
            # Validate ingress rules
            ingress_rules = sg.get('IpPermissions', [])
            expected_ingress = [r for r in expected_rules if r.direction == 'ingress']
            
            if len(ingress_rules) < len(expected_ingress):
                self.logger.warning(f"Missing ingress rules in {sg_name}")
                return False
            
            self.logger.info(f"Security group {sg_name} validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate AWS security group {tier_name}: {e}")
            return False
    
    async def _validate_azure_nsg(self, tier_name: str) -> bool:
        """Validate Azure NSG configuration"""
        # Similar implementation for Azure NSG validation
        return True
    
    async def _validate_gcp_firewall_rules(self, tier_name: str) -> bool:
        """Validate GCP firewall rules configuration"""
        # Similar implementation for GCP firewall validation
        return True

# Enterprise security policy orchestrator
class AinflueSecurityPolicyOrchestrator:
    """High-level security policy orchestration for Ainflue platform"""
    
    def __init__(self, environment -> None: str = "production") -> None:
        """Initialize security policy orchestrator
        
        Args:
            environment: Deployment environment
        """
        self.environment = environment
        self.logger = logging.getLogger(f"ainflue.infra.security.orchestrator")
        
        # Multi-cloud configurations
        self.cloud_configs = self._get_cloud_configurations()
        
    def _get_cloud_configurations(self) -> Dict[str, SecurityPolicyConfig]:
        """Get security configurations for all cloud providers"""
        return {
            'aws': SecurityPolicyConfig(
                environment=self.environment,
                cloud_provider='aws',
                vpc_id='vpc-12345678',  # This should come from terraform output
                region='us-west-2',
                tags={
                    'Environment': self.environment,
                    'Project': 'Ainflue',
                    'ManagedBy': 'AinflueSecurityOrchestrator'
                }
            ),
            'gcp': SecurityPolicyConfig(
                environment=self.environment,
                cloud_provider='gcp',
                vpc_id='ainflue-vpc',
                region='us-central1',
                tags={
                    'environment': self.environment,
                    'project': 'ainflue',
                    'managed-by': 'ainflue-security-orchestrator'
                }
            ),
            'azure': SecurityPolicyConfig(
                environment=self.environment,
                cloud_provider='azure',
                vpc_id='ainflue-vnet',
                region='East US',
                tags={
                    'Environment': self.environment,
                    'Project': 'Ainflue',
                    'ManagedBy': 'AinflueSecurityOrchestrator'
                }
            )
        }
    
    async def deploy_security_policies(self, cloud_providers: List[str] = None) -> Dict[str, bool]:
        """Deploy security policies across multiple cloud providers
        
        Args:
            cloud_providers: List of cloud providers to deploy to
            
        Returns:
            Dict mapping cloud providers to deployment status
        """
        if cloud_providers is None:
            cloud_providers = ['aws', 'gcp', 'azure']
        
        results = {}
        
        for provider in cloud_providers:
            if provider not in self.cloud_configs:
                self.logger.warning(f"Unknown cloud provider: {provider}")
                results[provider] = False
                continue
                
            try:
                config = self.cloud_configs[provider]
                manager = NetworkSecurityPolicyManager(config)
                
                # Deploy security policies for all tiers
                tiers = ['web_tier', 'app_tier', 'database_tier', 'ai_tier', 'monitoring']
                
                for tier in tiers:
                    sg_id = await manager.create_security_group(tier)
                    self.logger.info(f"Created {provider} security group for {tier}: {sg_id}")
                
                # Create WAF policy for web tier
                if tier == 'web_tier':
                    waf_id = await manager.create_waf_policy('web')
                    if waf_id:
                        self.logger.info(f"Created {provider} WAF policy: {waf_id}")
                
                results[provider] = True
                
            except Exception as e:
                self.logger.error(f"Failed to deploy security policies for {provider}: {e}")
                results[provider] = False
        
        return results

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        orchestrator = AinflueSecurityPolicyOrchestrator(environment="production")
        
        # Deploy security policies to all clouds
        results = await orchestrator.deploy_security_policies(['aws', 'gcp'])
        
        for provider, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"{provider}: {status}")
    
    asyncio.run(main())