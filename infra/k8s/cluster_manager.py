"""
Cluster Manager module
Enterprise implementation for Ainflue platform
"""

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
Kubernetes Cluster Manager

This module provides enterprise-grade Kubernetes cluster management capabilities
for the Ainflue platform infrastructure.

Features:
    - EKS/GKE/AKS cluster management
    - Node group auto-scaling
    - Cluster security configuration
    - Add-on management (CNI, CSI, monitoring)
    - Multi-cloud cluster orchestration
    - Cluster upgrades and maintenance
"""

import logging
import boto3
import json
import time
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ClusterStatus(Enum):
    """Kubernetes cluster status."""
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    FAILED = "FAILED"
    UPDATING = "UPDATING"

class NodeGroupStatus(Enum):
    """Node group status."""
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    CREATE_FAILED = "CREATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    DEGRADED = "DEGRADED"

@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration."""
    name: str
    version: str
    region: str
    vpc_id: str
    subnet_ids: List[str]
    security_group_ids: List[str]
    service_role_arn: str
    enable_logging: bool = True
    endpoint_private_access: bool = True
    endpoint_public_access: bool = True
    public_access_cidrs: List[str] = None
    enable_irsa: bool = True  # IAM Roles for Service Accounts

@dataclass
class NodeGroupConfig:
    """Node group configuration."""
    name: str
    instance_types: List[str]
    ami_type: str = "AL2_x86_64"
    capacity_type: str = "ON_DEMAND"  # ON_DEMAND or SPOT
    min_size: int = 1
    max_size: int = 10
    desired_size: int = 3
    disk_size: int = 20
    remote_access_enabled: bool = False
    ec2_ssh_key: Optional[str] = None
    source_security_groups: Optional[List[str]] = None
    labels: Optional[Dict[str, str]] = None
    taints: Optional[List[Dict[str, str]]] = None
    tags: Optional[Dict[str, str]] = None

class KubernetesClusterManager:
    """
    Enterprise Kubernetes cluster management for container orchestration.
    
    Provides comprehensive cluster lifecycle management with security,
    monitoring, and auto-scaling capabilities.
    """
    
    def __init__(self, region -> None: str = "us-west-2") -> None:
        """
        Initialize Kubernetes cluster manager.
        
        Args:
            region: AWS region for EKS clusters
        """
        self.region = region
        self.eks_client = boto3.client('eks', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_cluster(self, config: ClusterConfig,
                      encryption_config: Optional[List[Dict[str, Any]]] = None,
                      tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create EKS cluster with enterprise configuration.
        
        Args:
            config: Cluster configuration
            encryption_config: Encryption configuration for secrets
            tags: Resource tags
            
        Returns:
            Dict: Cluster creation result
        """
        try:
            # Prepare cluster parameters
            cluster_params = {
                'name': config.name,
                'version': config.version,
                'roleArn': config.service_role_arn,
                'resourcesVpcConfig': {
                    'subnetIds': config.subnet_ids,
                    'securityGroupIds': config.security_group_ids,
                    'endpointConfigPrivate': config.endpoint_private_access,
                    'endpointConfigPublic': config.endpoint_public_access
                }
            }
            
            # Configure public access CIDRs
            if config.public_access_cidrs:
                cluster_params['resourcesVpcConfig']['publicAccessCidrs'] = config.public_access_cidrs
            
            # Configure logging
            if config.enable_logging:
                cluster_params['logging'] = {
                    'enable': [
                        {'types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']}
                    ]
                }
            
            # Configure encryption
            if encryption_config:
                cluster_params['encryptionConfig'] = encryption_config
            
            # Add tags
            if tags:
                cluster_params['tags'] = tags
            
            # Create cluster
            response = self.eks_client.create_cluster(**cluster_params)
            
            # Wait for cluster to become active
            cluster_arn = response['cluster']['arn']
            self._wait_for_cluster_active(config.name)
            
            # Configure IRSA (IAM Roles for Service Accounts)
            if config.enable_irsa:
                self._setup_irsa(config.name)
            
            # Install essential add-ons
            self._install_essential_addons(config.name)
            
            logger.info(f"Created EKS cluster: {config.name}")
            
            return {
                'cluster_name': config.name,
                'cluster_arn': cluster_arn,
                'endpoint': response['cluster']['endpoint'],
                'version': response['cluster']['version'],
                'status': response['cluster']['status']
            }
            
        except Exception as e:
            logger.error(f"Failed to create cluster {config.name}: {str(e)}")
            raise
    
    def create_node_group(self, cluster_name: str, config: NodeGroupConfig,
                         node_role_arn: str, subnet_ids: List[str]) -> Dict[str, Any]:
        """
        Create EKS node group.
        
        Args:
            cluster_name: EKS cluster name
            config: Node group configuration
            node_role_arn: IAM role ARN for nodes
            subnet_ids: Subnet IDs for node group
            
        Returns:
            Dict: Node group creation result
        """
        try:
            # Prepare node group parameters
            nodegroup_params = {
                'clusterName': cluster_name,
                'nodegroupName': config.name,
                'scalingConfig': {
                    'minSize': config.min_size,
                    'maxSize': config.max_size,
                    'desiredSize': config.desired_size
                },
                'instanceTypes': config.instance_types,
                'amiType': config.ami_type,
                'nodeRole': node_role_arn,
                'subnets': subnet_ids,
                'capacityType': config.capacity_type
            }
            
            # Configure disk size
            if config.disk_size > 20:
                nodegroup_params['diskSize'] = config.disk_size
            
            # Configure remote access
            if config.remote_access_enabled:
                remote_access = {}
                if config.ec2_ssh_key:
                    remote_access['ec2SshKey'] = config.ec2_ssh_key
                if config.source_security_groups:
                    remote_access['sourceSecurityGroups'] = config.source_security_groups
                nodegroup_params['remoteAccess'] = remote_access
            
            # Configure labels
            if config.labels:
                nodegroup_params['labels'] = config.labels
            
            # Configure taints
            if config.taints:
                nodegroup_params['taints'] = config.taints
            
            # Add tags
            if config.tags:
                nodegroup_params['tags'] = config.tags
            
            # Create node group
            response = self.eks_client.create_nodegroup(**nodegroup_params)
            
            # Wait for node group to become active
            self._wait_for_nodegroup_active(cluster_name, config.name)
            
            logger.info(f"Created node group {config.name} for cluster {cluster_name}")
            
            return {
                'nodegroup_name': config.name,
                'nodegroup_arn': response['nodegroup']['nodegroupArn'],
                'status': response['nodegroup']['status'],
                'instance_types': response['nodegroup']['instanceTypes'],
                'capacity_type': response['nodegroup']['capacityType']
            }
            
        except Exception as e:
            logger.error(f"Failed to create node group {config.name}: {str(e)}")
            raise
    
    def update_cluster_version(self, cluster_name: str, version: str) -> Dict[str, Any]:
        """
        Update EKS cluster version.
        
        Args:
            cluster_name: EKS cluster name
            version: Target Kubernetes version
            
        Returns:
            Dict: Update result
        """
        try:
            response = self.eks_client.update_cluster_version(
                name=cluster_name,
                version=version
            )
            
            # Monitor update progress
            update_id = response['update']['id']
            self._wait_for_update_complete(cluster_name, update_id)
            
            logger.info(f"Updated cluster {cluster_name} to version {version}")
            return response['update']
            
        except Exception as e:
            logger.error(f"Failed to update cluster version: {str(e)}")
            raise
    
    def scale_node_group(self, cluster_name: str, nodegroup_name: str,
                        min_size: int, max_size: int, desired_size: int) -> bool:
        """
        Scale EKS node group.
        
        Args:
            cluster_name: EKS cluster name
            nodegroup_name: Node group name
            min_size: Minimum number of nodes
            max_size: Maximum number of nodes
            desired_size: Desired number of nodes
            
        Returns:
            bool: True if successful
        """
        try:
            response = self.eks_client.update_nodegroup_config(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                scalingConfig={
                    'minSize': min_size,
                    'maxSize': max_size,
                    'desiredSize': desired_size
                }
            )
            
            # Wait for scaling to complete
            update_id = response['update']['id']
            self._wait_for_nodegroup_update_complete(cluster_name, nodegroup_name, update_id)
            
            logger.info(f"Scaled node group {nodegroup_name} to {desired_size} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale node group: {str(e)}")
            return False
    
    def install_addon(self, cluster_name: str, addon_name: str,
                     addon_version: Optional[str] = None,
                     configuration_values: Optional[Dict[str, Any]] = None,
                     resolve_conflicts: str = "OVERWRITE") -> Dict[str, Any]:
        """
        Install EKS add-on.
        
        Args:
            cluster_name: EKS cluster name
            addon_name: Add-on name (vpc-cni, coredns, kube-proxy, etc.)
            addon_version: Specific add-on version
            configuration_values: Add-on configuration
            resolve_conflicts: Conflict resolution (OVERWRITE, NONE)
            
        Returns:
            Dict: Add-on installation result
        """
        try:
            params = {
                'clusterName': cluster_name,
                'addonName': addon_name,
                'resolveConflicts': resolve_conflicts
            }
            
            if addon_version:
                params['addonVersion'] = addon_version
            
            if configuration_values:
                params['configurationValues'] = json.dumps(configuration_values)
            
            response = self.eks_client.create_addon(**params)
            
            # Wait for add-on to become active
            self._wait_for_addon_active(cluster_name, addon_name)
            
            logger.info(f"Installed add-on {addon_name} for cluster {cluster_name}")
            return response['addon']
            
        except Exception as e:
            logger.error(f"Failed to install add-on {addon_name}: {str(e)}")
            raise
    
    def get_cluster_info(self, cluster_name: str) -> Dict[str, Any]:
        """
        Get comprehensive cluster information.
        
        Args:
            cluster_name: EKS cluster name
            
        Returns:
            Dict: Cluster information
        """
        try:
            # Get cluster details
            cluster_response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = cluster_response['cluster']
            
            # Get node groups
            nodegroups_response = self.eks_client.list_nodegroups(clusterName=cluster_name)
            
            nodegroup_details = []
            for ng_name in nodegroups_response['nodegroups']:
                ng_response = self.eks_client.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=ng_name
                )
                nodegroup_details.append(ng_response['nodegroup'])
            
            # Get add-ons
            addons_response = self.eks_client.list_addons(clusterName=cluster_name)
            
            addon_details = []
            for addon_name in addons_response['addons']:
                addon_response = self.eks_client.describe_addon(
                    clusterName=cluster_name,
                    addonName=addon_name
                )
                addon_details.append(addon_response['addon'])
            
            return {
                'cluster': cluster,
                'nodegroups': nodegroup_details,
                'addons': addon_details,
                'cluster_security_group_id': cluster['resourcesVpcConfig'].get('clusterSecurityGroupId'),
                'oidc_issuer': cluster.get('identity', {}).get('oidc', {}).get('issuer')
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster info: {str(e)}")
            return {}
    
    def _wait_for_cluster_active(self, cluster_name: str, timeout: int = 1200) -> None:
        """Wait for cluster to become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_cluster(name=cluster_name)
                status = response['cluster']['status']
                
                if status == ClusterStatus.ACTIVE.value:
                    return
                elif status == ClusterStatus.FAILED.value:
                    raise Exception(f"Cluster {cluster_name} creation failed")
                
                time.sleep(30)
                
            except Exception as e:
                if "ResourceNotFoundException" in str(e):
                    time.sleep(30)
                    continue
                raise
        
        raise TimeoutError(f"Cluster {cluster_name} did not become active within {timeout} seconds")
    
    def _wait_for_nodegroup_active(self, cluster_name: str, nodegroup_name: str,
                                  timeout: int = 900) -> None:
        """Wait for node group to become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=nodegroup_name
                )
                status = response['nodegroup']['status']
                
                if status == NodeGroupStatus.ACTIVE.value:
                    return
                elif status in [NodeGroupStatus.CREATE_FAILED.value, NodeGroupStatus.DEGRADED.value]:
                    raise Exception(f"Node group {nodegroup_name} creation failed")
                
                time.sleep(30)
                
            except Exception as e:
                if "ResourceNotFoundException" in str(e):
                    time.sleep(30)
                    continue
                raise
        
        raise TimeoutError(f"Node group {nodegroup_name} did not become active within {timeout} seconds")
    
    def _wait_for_update_complete(self, cluster_name: str, update_id: str,
                                 timeout: int = 1800) -> None:
        """Wait for cluster update to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_update(
                    name=cluster_name,
                    updateId=update_id
                )
                status = response['update']['status']
                
                if status == 'Successful':
                    return
                elif status == 'Failed':
                    raise Exception(f"Cluster update {update_id} failed")
                
                time.sleep(60)
                
            except Exception as e:
                raise
        
        raise TimeoutError(f"Cluster update {update_id} did not complete within {timeout} seconds")
    
    def _wait_for_nodegroup_update_complete(self, cluster_name: str, nodegroup_name: str,
                                          update_id: str, timeout: int = 900) -> None:
        """Wait for node group update to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_update(
                    name=cluster_name,
                    nodegroupName=nodegroup_name,
                    updateId=update_id
                )
                status = response['update']['status']
                
                if status == 'Successful':
                    return
                elif status == 'Failed':
                    raise Exception(f"Node group update {update_id} failed")
                
                time.sleep(30)
                
            except Exception as e:
                raise
        
        raise TimeoutError(f"Node group update {update_id} did not complete within {timeout} seconds")
    
    def _wait_for_addon_active(self, cluster_name: str, addon_name: str,
                              timeout: int = 600) -> None:
        """Wait for add-on to become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_addon(
                    clusterName=cluster_name,
                    addonName=addon_name
                )
                status = response['addon']['status']
                
                if status == 'ACTIVE':
                    return
                elif status in ['CREATE_FAILED', 'DEGRADED']:
                    raise Exception(f"Add-on {addon_name} installation failed")
                
                time.sleep(30)
                
            except Exception as e:
                if "ResourceNotFoundException" in str(e):
                    time.sleep(30)
                    continue
                raise
        
        raise TimeoutError(f"Add-on {addon_name} did not become active within {timeout} seconds")
    
    def _setup_irsa(self, cluster_name: str) -> None:
        """Set up IAM Roles for Service Accounts (IRSA)."""
        try:
            # Get cluster OIDC issuer
            cluster_info = self.eks_client.describe_cluster(name=cluster_name)
            oidc_issuer = cluster_info['cluster']['identity']['oidc']['issuer']
            
            # Create OIDC identity provider if it doesn't exist
            issuer_url = oidc_issuer.replace('https://', '')
            
            try:
                self.iam_client.create_open_id_connect_provider(
                    Url=oidc_issuer,
                    ThumbprintList=['9e99a48a9960b14926bb7f3b02e22da2b0ab7280'],  # EKS OIDC root CA thumbprint
                    ClientIDList=['sts.amazonaws.com']
                )
                logger.info(f"Created OIDC identity provider for cluster {cluster_name}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExistsException':
                    logger.info("OIDC identity provider already exists")
                else:
                    raise
                    
        except Exception as e:
            logger.warning(f"Failed to setup IRSA: {str(e)}")
    
    def _install_essential_addons(self, cluster_name: str) -> None:
        """Install essential EKS add-ons."""
        essential_addons = [
            'vpc-cni',
            'coredns',
            'kube-proxy'
        ]
        
        for addon in essential_addons:
            try:
                self.install_addon(cluster_name, addon)
            except Exception as e:
                logger.warning(f"Failed to install add-on {addon}: {str(e)}")
    
    def delete_cluster(self, cluster_name: str, delete_nodegroups: bool = True) -> bool:
        """
        Delete EKS cluster and associated resources.
        
        Args:
            cluster_name: EKS cluster name
            delete_nodegroups: Whether to delete node groups first
            
        Returns:
            bool: True if successful
        """
        try:
            # Delete node groups first if requested
            if delete_nodegroups:
                nodegroups_response = self.eks_client.list_nodegroups(clusterName=cluster_name)
                for nodegroup_name in nodegroups_response['nodegroups']:
                    self.eks_client.delete_nodegroup(
                        clusterName=cluster_name,
                        nodegroupName=nodegroup_name
                    )
                    logger.info(f"Deleted node group: {nodegroup_name}")
            
            # Delete add-ons
            try:
                addons_response = self.eks_client.list_addons(clusterName=cluster_name)
                for addon_name in addons_response['addons']:
                    self.eks_client.delete_addon(
                        clusterName=cluster_name,
                        addonName=addon_name
                    )
                    logger.info(f"Deleted add-on: {addon_name}")
            except Exception as e:
                logger.warning(f"Failed to delete some add-ons: {str(e)}")
            
            # Delete cluster
            self.eks_client.delete_cluster(name=cluster_name)
            
            logger.info(f"Deleted EKS cluster: {cluster_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete cluster {cluster_name}: {str(e)}")
            return False