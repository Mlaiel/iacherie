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
Load Balancer Manager

This module provides enterprise-grade load balancer management capabilities
for the Ainflue platform infrastructure.

Features:
    - Application Load Balancer (ALB) management
    - Network Load Balancer (NLB) management
    - Health check configuration
    - SSL/TLS termination
    - Auto-scaling integration
    - Multi-zone deployment
"""

import logging
import boto3
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LoadBalancerType(Enum):
    """Load balancer types."""
    APPLICATION = "application"
    NETWORK = "network"
    GATEWAY = "gateway"

class TargetType(Enum):
    """Target types for load balancer."""
    INSTANCE = "instance"
    IP = "ip"
    LAMBDA = "lambda"
    ALB = "alb"

@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    enabled: bool = True
    healthy_threshold_count: int = 2
    unhealthy_threshold_count: int = 2
    health_check_timeout_seconds: int = 5
    health_check_interval_seconds: int = 30
    health_check_path: str = "/health"
    health_check_protocol: str = "HTTP"
    health_check_port: str = "traffic-port"
    matcher: str = "200"

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    name: str
    type: LoadBalancerType
    scheme: str = "internet-facing"  # internet-facing or internal
    ip_address_type: str = "ipv4"  # ipv4 or dualstack
    deletion_protection: bool = True
    idle_timeout: int = 60
    enable_cross_zone_load_balancing: bool = True

class LoadBalancerManager:
    """
    Enterprise load balancer management for high availability and scalability.
    
    Provides comprehensive load balancer management with health checks,
    SSL termination, and auto-scaling integration.
    """
    
    def __init__(self, region: str = "us-west-2"):
        """
        Initialize load balancer manager.
        
        Args:
            region: AWS region for load balancer deployment
        """
        self.region = region
        self.elbv2_client = boto3.client('elbv2', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        
    def create_application_load_balancer(self, config: LoadBalancerConfig,
                                       subnet_ids: List[str],
                                       security_group_ids: List[str],
                                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create Application Load Balancer.
        
        Args:
            config: Load balancer configuration
            subnet_ids: List of subnet IDs for load balancer
            security_group_ids: List of security group IDs
            tags: Resource tags
            
        Returns:
            Dict: Load balancer details
        """
        try:
            # Prepare load balancer attributes
            attributes = [
                {
                    'Key': 'idle_timeout.timeout_seconds',
                    'Value': str(config.idle_timeout)
                },
                {
                    'Key': 'deletion_protection.enabled',
                    'Value': str(config.deletion_protection).lower()
                }
            ]
            
            if config.type == LoadBalancerType.APPLICATION:
                attributes.append({
                    'Key': 'routing.http2.enabled',
                    'Value': 'true'
                })
            
            # Create load balancer
            response = self.elbv2_client.create_load_balancer(
                Name=config.name,
                Subnets=subnet_ids,
                SecurityGroups=security_group_ids,
                Scheme=config.scheme,
                Type=config.type.value,
                IpAddressType=config.ip_address_type,
                Tags=self._format_tags(tags or {})
            )
            
            lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
            
            # Modify load balancer attributes
            self.elbv2_client.modify_load_balancer_attributes(
                LoadBalancerArn=lb_arn,
                Attributes=attributes
            )
            
            logger.info(f"Created Application Load Balancer: {config.name}")
            return response['LoadBalancers'][0]
            
        except Exception as e:
            logger.error(f"Failed to create load balancer: {str(e)}")
            raise
    
    def create_network_load_balancer(self, config: LoadBalancerConfig,
                                   subnet_configs: List[Dict[str, str]],
                                   tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create Network Load Balancer.
        
        Args:
            config: Load balancer configuration
            subnet_configs: List of subnet configurations with static IPs
            tags: Resource tags
            
        Returns:
            Dict: Load balancer details
        """
        try:
            # Prepare subnet mappings for NLB
            subnet_mappings = []
            for subnet_config in subnet_configs:
                mapping = {'SubnetId': subnet_config['subnet_id']}
                if 'allocation_id' in subnet_config:
                    mapping['AllocationId'] = subnet_config['allocation_id']
                elif 'private_ipv4_address' in subnet_config:
                    mapping['PrivateIPv4Address'] = subnet_config['private_ipv4_address']
                subnet_mappings.append(mapping)
            
            # Prepare load balancer attributes
            attributes = [
                {
                    'Key': 'deletion_protection.enabled',
                    'Value': str(config.deletion_protection).lower()
                },
                {
                    'Key': 'load_balancing.cross_zone.enabled',
                    'Value': str(config.enable_cross_zone_load_balancing).lower()
                }
            ]
            
            # Create load balancer
            response = self.elbv2_client.create_load_balancer(
                Name=config.name,
                SubnetMappings=subnet_mappings,
                Scheme=config.scheme,
                Type=config.type.value,
                IpAddressType=config.ip_address_type,
                Tags=self._format_tags(tags or {})
            )
            
            lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
            
            # Modify load balancer attributes
            self.elbv2_client.modify_load_balancer_attributes(
                LoadBalancerArn=lb_arn,
                Attributes=attributes
            )
            
            logger.info(f"Created Network Load Balancer: {config.name}")
            return response['LoadBalancers'][0]
            
        except Exception as e:
            logger.error(f"Failed to create network load balancer: {str(e)}")
            raise
    
    def create_target_group(self, name: str, port: int, protocol: str,
                          vpc_id: str, target_type: TargetType,
                          health_check: HealthCheckConfig,
                          tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create target group for load balancer.
        
        Args:
            name: Target group name
            port: Target port
            protocol: Target protocol (HTTP, HTTPS, TCP, UDP, etc.)
            vpc_id: VPC ID
            target_type: Type of targets
            health_check: Health check configuration
            tags: Resource tags
            
        Returns:
            Dict: Target group details
        """
        try:
            # Prepare target group parameters
            params = {
                'Name': name,
                'Protocol': protocol,
                'Port': port,
                'VpcId': vpc_id,
                'TargetType': target_type.value,
                'Tags': self._format_tags(tags or {})
            }
            
            # Add health check configuration
            if health_check.enabled:
                params.update({
                    'HealthCheckEnabled': True,
                    'HealthCheckProtocol': health_check.health_check_protocol,
                    'HealthCheckPort': health_check.health_check_port,
                    'HealthCheckIntervalSeconds': health_check.health_check_interval_seconds,
                    'HealthCheckTimeoutSeconds': health_check.health_check_timeout_seconds,
                    'HealthyThresholdCount': health_check.healthy_threshold_count,
                    'UnhealthyThresholdCount': health_check.unhealthy_threshold_count
                })
                
                # Add path and matcher for HTTP/HTTPS
                if health_check.health_check_protocol in ['HTTP', 'HTTPS']:
                    params['HealthCheckPath'] = health_check.health_check_path
                    params['Matcher'] = {'HttpCode': health_check.matcher}
            
            # Create target group
            response = self.elbv2_client.create_target_group(**params)
            
            logger.info(f"Created target group: {name}")
            return response['TargetGroups'][0]
            
        except Exception as e:
            logger.error(f"Failed to create target group: {str(e)}")
            raise
    
    def create_listener(self, load_balancer_arn: str, port: int, protocol: str,
                       default_actions: List[Dict[str, Any]],
                       certificate_arn: Optional[str] = None,
                       ssl_policy: Optional[str] = None) -> Dict[str, Any]:
        """
        Create listener for load balancer.
        
        Args:
            load_balancer_arn: Load balancer ARN
            port: Listener port
            protocol: Listener protocol
            default_actions: List of default actions
            certificate_arn: SSL certificate ARN for HTTPS
            ssl_policy: SSL security policy
            
        Returns:
            Dict: Listener details
        """
        try:
            params = {
                'LoadBalancerArn': load_balancer_arn,
                'Protocol': protocol,
                'Port': port,
                'DefaultActions': default_actions
            }
            
            # Add SSL configuration for HTTPS/TLS
            if protocol in ['HTTPS', 'TLS']:
                if certificate_arn:
                    params['Certificates'] = [{'CertificateArn': certificate_arn}]
                if ssl_policy:
                    params['SslPolicy'] = ssl_policy
                else:
                    params['SslPolicy'] = 'ELBSecurityPolicy-TLS-1-2-2017-01'
            
            response = self.elbv2_client.create_listener(**params)
            
            logger.info(f"Created listener on port {port} for load balancer")
            return response['Listeners'][0]
            
        except Exception as e:
            logger.error(f"Failed to create listener: {str(e)}")
            raise
    
    def register_targets(self, target_group_arn: str,
                        targets: List[Dict[str, Union[str, int]]]) -> bool:
        """
        Register targets with target group.
        
        Args:
            target_group_arn: Target group ARN
            targets: List of targets to register
            
        Returns:
            bool: True if successful
        """
        try:
            self.elbv2_client.register_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets
            )
            
            logger.info(f"Registered {len(targets)} targets with target group")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register targets: {str(e)}")
            return False
    
    def deregister_targets(self, target_group_arn: str,
                          targets: List[Dict[str, Union[str, int]]]) -> bool:
        """
        Deregister targets from target group.
        
        Args:
            target_group_arn: Target group ARN
            targets: List of targets to deregister
            
        Returns:
            bool: True if successful
        """
        try:
            self.elbv2_client.deregister_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets
            )
            
            logger.info(f"Deregistered {len(targets)} targets from target group")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister targets: {str(e)}")
            return False
    
    def get_target_health(self, target_group_arn: str) -> List[Dict[str, Any]]:
        """
        Get health status of targets in target group.
        
        Args:
            target_group_arn: Target group ARN
            
        Returns:
            List[Dict]: List of target health descriptions
        """
        try:
            response = self.elbv2_client.describe_target_health(
                TargetGroupArn=target_group_arn
            )
            
            return response['TargetHealthDescriptions']
            
        except Exception as e:
            logger.error(f"Failed to get target health: {str(e)}")
            return []
    
    def update_listener_rules(self, listener_arn: str,
                            rules: List[Dict[str, Any]]) -> bool:
        """
        Update listener rules for advanced routing.
        
        Args:
            listener_arn: Listener ARN
            rules: List of rule configurations
            
        Returns:
            bool: True if successful
        """
        try:
            for rule in rules:
                if 'RuleArn' in rule:
                    # Modify existing rule
                    self.elbv2_client.modify_rule(
                        RuleArn=rule['RuleArn'],
                        Conditions=rule.get('Conditions', []),
                        Actions=rule.get('Actions', [])
                    )
                else:
                    # Create new rule
                    self.elbv2_client.create_rule(
                        ListenerArn=listener_arn,
                        Conditions=rule['Conditions'],
                        Actions=rule['Actions'],
                        Priority=rule['Priority']
                    )
            
            logger.info(f"Updated {len(rules)} listener rules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update listener rules: {str(e)}")
            return False
    
    def enable_access_logs(self, load_balancer_arn: str, s3_bucket: str,
                          s3_prefix: Optional[str] = None) -> bool:
        """
        Enable access logs for load balancer.
        
        Args:
            load_balancer_arn: Load balancer ARN
            s3_bucket: S3 bucket for access logs
            s3_prefix: S3 prefix for log files
            
        Returns:
            bool: True if successful
        """
        try:
            attributes = [
                {
                    'Key': 'access_logs.s3.enabled',
                    'Value': 'true'
                },
                {
                    'Key': 'access_logs.s3.bucket',
                    'Value': s3_bucket
                }
            ]
            
            if s3_prefix:
                attributes.append({
                    'Key': 'access_logs.s3.prefix',
                    'Value': s3_prefix
                })
            
            self.elbv2_client.modify_load_balancer_attributes(
                LoadBalancerArn=load_balancer_arn,
                Attributes=attributes
            )
            
            logger.info("Enabled access logs for load balancer")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable access logs: {str(e)}")
            return False
    
    def delete_load_balancer(self, load_balancer_arn: str) -> bool:
        """
        Delete load balancer.
        
        Args:
            load_balancer_arn: Load balancer ARN
            
        Returns:
            bool: True if successful
        """
        try:
            self.elbv2_client.delete_load_balancer(
                LoadBalancerArn=load_balancer_arn
            )
            
            logger.info("Deleted load balancer")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete load balancer: {str(e)}")
            return False
    
    def _format_tags(self, tags: Dict[str, str]) -> List[Dict[str, str]]:
        """Format tags for AWS API."""
        return [{'Key': key, 'Value': value} for key, value in tags.items()]
    
    def get_load_balancer_metrics(self, load_balancer_name: str,
                                start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Get CloudWatch metrics for load balancer.
        
        Args:
            load_balancer_name: Load balancer name
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            Dict: Metrics data
        """
        try:
            cloudwatch = boto3.client('cloudwatch', region_name=self.region)
            
            metrics = [
                'RequestCount',
                'TargetResponseTime',
                'HTTPCode_Target_2XX_Count',
                'HTTPCode_Target_4XX_Count',
                'HTTPCode_Target_5XX_Count',
                'HealthyHostCount',
                'UnHealthyHostCount'
            ]
            
            metric_data = {}
            
            for metric_name in metrics:
                response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/ApplicationELB',
                    MetricName=metric_name,
                    Dimensions=[
                        {
                            'Name': 'LoadBalancer',
                            'Value': load_balancer_name
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=['Sum', 'Average', 'Maximum']
                )
                
                metric_data[metric_name] = response['Datapoints']
            
            return metric_data
            
        except Exception as e:
            logger.error(f"Failed to get load balancer metrics: {str(e)}")
            return {}