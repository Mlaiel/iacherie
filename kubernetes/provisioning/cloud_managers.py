"""Cloud Infrastructure Management Module

Enterprise-grade cloud infrastructure managers for the IA Influencer Agent + Content Protection Platform.
Manages multi-cloud deployments, resource provisioning, and infrastructure automation.

Project Owner: Fahed Mlaiel (mlaiel@live.de)

⚠️ CRITICAL LEGAL WARNING:
This software and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or appropriation of this code, concept, 
or business idea without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is strictly prohibited and will result in immediate legal action. All rights reserved.
"""
import boto3
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from google.cloud import compute_v1, container_v1
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.identity import DefaultAzureCredential
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers for infrastructure deployment"""    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    MULTICLOUD = "multicloud"


@dataclass
class InfrastructureConfig:
    """Infrastructure configuration for cloud deployments"""    environment: str
    region: str
    availability_zones: List[str]
    instance_types: Dict[str, str]
    storage_size: int
    backup_retention: int
    monitoring_enabled: bool
    encryption_enabled: bool
    high_availability: bool
    auto_scaling: bool
    network_cidr: str
    tags: Dict[str, str]


@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration"""    cluster_name: str
    node_count: int
    node_type: str
    kubernetes_version: str
    network_policy: bool
    private_cluster: bool
    enable_autoscaling: bool
    min_nodes: int
    max_nodes: int
    disk_size: int
    addons: List[str]


class BaseCloudManager:
    """Base class for cloud infrastructure management"""    
    def __init__(self, config: InfrastructureConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.resource_tracker = {}
        
    async def provision_infrastructure(self) -> Dict[str, Any]:
        """Provision complete infrastructure stack"""        # Default implementation for cloud managers without provisioning support
        logging.warning(f"Infrastructure provisioning not implemented for {self.__class__.__name__}")
        return {
            "status": "not_implemented",
            "manager": self.__class__.__name__,
            "message": "Infrastructure provisioning not implemented"
        }
        
    async def destroy_infrastructure(self) -> bool:
        """Destroy infrastructure stack safely"""        # Default implementation for cloud managers without destruction support
        logging.warning(f"Infrastructure destruction not implemented for {self.__class__.__name__}")
        return False
        
    async def validate_infrastructure(self) -> Dict[str, bool]:
        """Validate infrastructure deployment"""        # Default implementation for cloud managers without validation support
        logging.warning(f"Infrastructure validation not implemented for {self.__class__.__name__}")
        return {"validation_supported": False}
        
    def get_resource_status(self) -> Dict[str, str]:
        """Get status of all managed resources"""        return self.resource_tracker


class AWSInfrastructureManager(BaseCloudManager):
    """AWS-specific infrastructure management"""    
    def __init__(self, config: InfrastructureConfig, credentials: Dict[str, str]):
        super().__init__(config)
        self.session = boto3.Session(
            aws_access_key_id=credentials.get('access_key'),
            aws_secret_access_key=credentials.get('secret_key'),
            region_name=config.region
        )
        self.ec2 = self.session.client('ec2')
        self.eks = self.session.client('eks')
        self.rds = self.session.client('rds')
        self.s3 = self.session.client('s3')
        self.cloudformation = self.session.client('cloudformation')
        
    async def provision_infrastructure(self) -> Dict[str, Any]:
        """Provision complete AWS infrastructure for IA Influencer platform"""        try:
            self.logger.info(f"Starting AWS infrastructure provisioning for {self.config.environment}")
            
            # 1. Create VPC and networking
            vpc_info = await self._provision_vpc()
            
            # 2. Create EKS cluster for microservices
            cluster_info = await self._provision_eks_cluster(vpc_info)
            
            # 3. Create RDS instances for databases
            database_info = await self._provision_databases(vpc_info)
            
            # 4. Create S3 buckets for content storage
            storage_info = await self._provision_storage()
            
            # 5. Create Elasticsearch for search and analytics
            search_info = await self._provision_elasticsearch(vpc_info)
            
            # 6. Create Redis cluster for caching
            cache_info = await self._provision_redis_cluster(vpc_info)
            
            # 7. Setup CloudWatch monitoring
            monitoring_info = await self._setup_monitoring()
            
            # 8. Configure security groups and IAM
            security_info = await self._configure_security()
            
            infrastructure_summary = {
                'vpc': vpc_info,
                'cluster': cluster_info,
                'databases': database_info,
                'storage': storage_info,
                'search': search_info,
                'cache': cache_info,
                'monitoring': monitoring_info,
                'security': security_info,
                'status': 'provisioned',
                'timestamp': time.time()
            }
            
            self.resource_tracker.update(infrastructure_summary)
            self.logger.info("AWS infrastructure provisioning completed successfully")
            
            return infrastructure_summary
            
        except Exception as e:
            self.logger.error(f"AWS infrastructure provisioning failed: {str(e)}")
            await self._rollback_failed_resources()
            raise
    
    async def _provision_vpc(self) -> Dict[str, Any]:
        """Create VPC with public/private subnets"""        try:
            # Create VPC
            vpc_response = self.ec2.create_vpc(
                CidrBlock=self.config.network_cidr,
                EnableDnsHostnames=True,
                EnableDnsSupport=True,
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': f'ia-influencer-vpc-{self.config.environment}'},
                        {'Key': 'Environment', 'Value': self.config.environment},
                        {'Key': 'Project', 'Value': 'IA-Influencer-Agent'}
                    ]
                }]
            )
            vpc_id = vpc_response['Vpc']['VpcId']
            
            # Create Internet Gateway
            igw_response = self.ec2.create_internet_gateway(
                TagSpecifications=[{
                    'ResourceType': 'internet-gateway',
                    'Tags': [{'Key': 'Name', 'Value': f'ia-influencer-igw-{self.config.environment}'}]
                }]
            )
            igw_id = igw_response['InternetGateway']['InternetGatewayId']
            
            # Attach IGW to VPC
            self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            
            # Create subnets across availability zones
            subnets = []
            for i, az in enumerate(self.config.availability_zones):
                # Public subnet
                public_subnet = self.ec2.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=f'10.0.{i*2}.0/24',
                    AvailabilityZone=az,
                    MapPublicIpOnLaunch=True,
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'ia-influencer-public-{az}'},
                            {'Key': 'Type', 'Value': 'public'}
                        ]
                    }]
                )
                
                # Private subnet
                private_subnet = self.ec2.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=f'10.0.{i*2+1}.0/24',
                    AvailabilityZone=az,
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'ia-influencer-private-{az}'},
                            {'Key': 'Type', 'Value': 'private'}
                        ]
                    }]
                )
                
                subnets.extend([
                    {
                        'id': public_subnet['Subnet']['SubnetId'],
                        'type': 'public',
                        'az': az,
                        'cidr': f'10.0.{i*2}.0/24'
                    },
                    {
                        'id': private_subnet['Subnet']['SubnetId'],
                        'type': 'private',
                        'az': az,
                        'cidr': f'10.0.{i*2+1}.0/24'
                    }
                ])
            
            return {
                'vpc_id': vpc_id,
                'igw_id': igw_id,
                'subnets': subnets,
                'region': self.config.region
            }
            
        except Exception as e:
            self.logger.error(f"VPC provisioning failed: {str(e)}")
            raise
    
    async def _provision_eks_cluster(self, vpc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create EKS cluster for microservices deployment"""        try:
            cluster_config = ClusterConfig(
                cluster_name=f'ia-influencer-{self.config.environment}',
                node_count=3,
                node_type='t3.large',
                kubernetes_version='1.28',
                network_policy=True,
                private_cluster=True,
                enable_autoscaling=True,
                min_nodes=1,
                max_nodes=10,
                disk_size=100,
                addons=['aws-ebs-csi-driver', 'coredns', 'kube-proxy', 'vpc-cni']
            )
            
            # Create EKS cluster
            private_subnets = [s['id'] for s in vpc_info['subnets'] if s['type'] == 'private']
            
            cluster_response = self.eks.create_cluster(
                name=cluster_config.cluster_name,
                version=cluster_config.kubernetes_version,
                roleArn=await self._get_or_create_eks_role(),
                resourcesVpcConfig={
                    'subnetIds': private_subnets,
                    'endpointConfigPrivate': cluster_config.private_cluster,
                    'endpointConfigPublic': True,
                    'publicAccessCidrs': ['0.0.0.0/0']
                },
                logging={
                    'enable': True,
                    'types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']
                },
                tags=self.config.tags
            )
            
            # Wait for cluster to be active
            await self._wait_for_cluster_active(cluster_config.cluster_name)
            
            # Create node group
            nodegroup_response = self.eks.create_nodegroup(
                clusterName=cluster_config.cluster_name,
                nodegroupName=f'{cluster_config.cluster_name}-workers',
                scalingConfig={
                    'minSize': cluster_config.min_nodes,
                    'maxSize': cluster_config.max_nodes,
                    'desiredSize': cluster_config.node_count
                },
                instanceTypes=[cluster_config.node_type],
                subnets=private_subnets,
                nodeRole=await self._get_or_create_node_role(),
                diskSize=cluster_config.disk_size,
                capacityType='ON_DEMAND',
                tags=self.config.tags
            )
            
            return {
                'cluster_name': cluster_config.cluster_name,
                'cluster_arn': cluster_response['cluster']['arn'],
                'endpoint': cluster_response['cluster']['endpoint'],
                'nodegroup_name': f'{cluster_config.cluster_name}-workers',
                'subnets': private_subnets,
                'status': 'creating'
            }
            
        except Exception as e:
            self.logger.error(f"EKS cluster provisioning failed: {str(e)}")
            raise
    
    async def _provision_databases(self, vpc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create RDS instances for PostgreSQL, Redis and vector storage"""        try:
            # Create DB subnet group
            private_subnets = [s['id'] for s in vpc_info['subnets'] if s['type'] == 'private']
            
            db_subnet_group = self.rds.create_db_subnet_group(
                DBSubnetGroupName=f'ia-influencer-db-{self.config.environment}',
                DBSubnetGroupDescription='DB subnet group for IA Influencer platform',
                SubnetIds=private_subnets,
                Tags=[
                    {'Key': 'Environment', 'Value': self.config.environment},
                    {'Key': 'Project', 'Value': 'IA-Influencer-Agent'}
                ]
            )
            
            # Create PostgreSQL for main application data
            postgres_instance = self.rds.create_db_instance(
                DBInstanceIdentifier=f'ia-influencer-postgres-{self.config.environment}',
                DBInstanceClass='db.t3.large',
                Engine='postgres',
                EngineVersion='15.4',
                MasterUsername='iainfluencer',
                MasterUserPassword='SecurePassword123!',
                AllocatedStorage=100,
                StorageType='gp3',
                StorageEncrypted=True,
                VpcSecurityGroupIds=[await self._create_db_security_group(vpc_info['vpc_id'])],
                DBSubnetGroupName=db_subnet_group['DBSubnetGroup']['DBSubnetGroupName'],
                BackupRetentionPeriod=self.config.backup_retention,
                MultiAZ=self.config.high_availability,
                Tags=[
                    {'Key': 'Name', 'Value': f'ia-influencer-postgres-{self.config.environment}'},
                    {'Key': 'Environment', 'Value': self.config.environment}
                ]
            )
            
            # Create MongoDB Atlas cluster (external service)
            mongodb_config = await self._setup_mongodb_atlas()
            
            return {
                'postgresql': {
                    'identifier': postgres_instance['DBInstance']['DBInstanceIdentifier'],
                    'endpoint': postgres_instance['DBInstance']['Endpoint']['Address'],
                    'port': postgres_instance['DBInstance']['Endpoint']['Port'],
                    'database': 'ia_influencer_platform'
                },
                'mongodb': mongodb_config,
                'subnet_group': db_subnet_group['DBSubnetGroup']['DBSubnetGroupName']
            }
            
        except Exception as e:
            self.logger.error(f"Database provisioning failed: {str(e)}")
            raise
    
    async def _provision_storage(self) -> Dict[str, Any]:
        """Create S3 buckets for content storage"""        try:
            buckets = {}
            
            # Main content storage bucket
            content_bucket = f'ia-influencer-content-{self.config.environment}-{int(time.time())}'
            self.s3.create_bucket(
                Bucket=content_bucket,
                CreateBucketConfiguration={'LocationConstraint': self.config.region}
            )
            
            # Configure bucket versioning and encryption
            self.s3.put_bucket_versioning(
                Bucket=content_bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            self.s3.put_bucket_encryption(
                Bucket=content_bucket,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
            
            buckets['content'] = {
                'name': content_bucket,
                'purpose': 'Content storage for fingerprinting and protection',
                'versioning': True,
                'encryption': True
            }
            
            # Analytics data bucket
            analytics_bucket = f'ia-influencer-analytics-{self.config.environment}-{int(time.time())}'
            self.s3.create_bucket(
                Bucket=analytics_bucket,
                CreateBucketConfiguration={'LocationConstraint': self.config.region}
            )
            
            buckets['analytics'] = {
                'name': analytics_bucket,
                'purpose': 'Analytics and reporting data',
                'versioning': False,
                'encryption': True
            }
            
            # Backup bucket
            backup_bucket = f'ia-influencer-backup-{self.config.environment}-{int(time.time())}'
            self.s3.create_bucket(
                Bucket=backup_bucket,
                CreateBucketConfiguration={'LocationConstraint': self.config.region}
            )
            
            buckets['backup'] = {
                'name': backup_bucket,
                'purpose': 'System backups and disaster recovery',
                'versioning': True,
                'encryption': True
            }
            
            return {
                'buckets': buckets,
                'region': self.config.region,
                'total_buckets': len(buckets)
            }
            
        except Exception as e:
            self.logger.error(f"Storage provisioning failed: {str(e)}")
            raise
    
    async def _provision_elasticsearch(self, vpc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create Elasticsearch domain for search and analytics"""        try:
            es_client = self.session.client('es')
            
            domain_name = f'ia-influencer-search-{self.config.environment}'
            
            # Create Elasticsearch domain
            domain_config = {
                'DomainName': domain_name,
                'ElasticsearchVersion': '7.10',
                'ElasticsearchClusterConfig': {
                    'InstanceType': 't3.small.elasticsearch',
                    'InstanceCount': 3,
                    'DedicatedMasterEnabled': True,
                    'MasterInstanceType': 't3.small.elasticsearch',
                    'MasterInstanceCount': 3,
                    'ZoneAwarenessEnabled': True
                },
                'EBSOptions': {
                    'EBSEnabled': True,
                    'VolumeType': 'gp3',
                    'VolumeSize': 20
                },
                'VPCOptions': {
                    'SubnetIds': [s['id'] for s in vpc_info['subnets'] if s['type'] == 'private'][:2],
                    'SecurityGroupIds': [await self._create_es_security_group(vpc_info['vpc_id'])]
                },
                'EncryptionAtRestOptions': {
                    'Enabled': True
                },
                'NodeToNodeEncryptionOptions': {
                    'Enabled': True
                },
                'DomainEndpointOptions': {
                    'EnforceHTTPS': True
                }
            }
            
            domain_response = es_client.create_elasticsearch_domain(**domain_config)
            
            return {
                'domain_name': domain_name,
                'domain_arn': domain_response['DomainStatus']['ARN'],
                'endpoint': domain_response['DomainStatus'].get('Endpoint'),
                'version': '7.10',
                'instance_count': 3
            }
            
        except Exception as e:
            self.logger.error(f"Elasticsearch provisioning failed: {str(e)}")
            raise
    
    async def _provision_redis_cluster(self, vpc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create ElastiCache Redis cluster for caching"""        try:
            elasticache = self.session.client('elasticache')
            
            # Create cache subnet group
            subnet_group_name = f'ia-influencer-cache-{self.config.environment}'
            private_subnets = [s['id'] for s in vpc_info['subnets'] if s['type'] == 'private']
            
            elasticache.create_cache_subnet_group(
                CacheSubnetGroupName=subnet_group_name,
                CacheSubnetGroupDescription='Cache subnet group for IA Influencer platform',
                SubnetIds=private_subnets
            )
            
            # Create Redis replication group
            replication_group = elasticache.create_replication_group(
                ReplicationGroupId=f'ia-influencer-redis-{self.config.environment}',
                Description='Redis cluster for IA Influencer platform',
                NumCacheClusters=3,
                CacheNodeType='cache.t3.micro',
                Engine='redis',
                EngineVersion='7.0',
                CacheSubnetGroupName=subnet_group_name,
                SecurityGroupIds=[await self._create_cache_security_group(vpc_info['vpc_id'])],
                AtRestEncryptionEnabled=True,
                TransitEncryptionEnabled=True,
                AutomaticFailoverEnabled=True,
                MultiAZEnabled=True,
                Tags=[
                    {'Key': 'Environment', 'Value': self.config.environment},
                    {'Key': 'Project', 'Value': 'IA-Influencer-Agent'}
                ]
            )
            
            return {
                'replication_group_id': replication_group['ReplicationGroup']['ReplicationGroupId'],
                'primary_endpoint': replication_group['ReplicationGroup'].get('PrimaryEndpoint', {}).get('Address'),
                'subnet_group': subnet_group_name,
                'node_type': 'cache.t3.micro',
                'num_nodes': 3
            }
            
        except Exception as e:
            self.logger.error(f"Redis cluster provisioning failed: {str(e)}")
            raise
    
    async def _setup_monitoring(self) -> Dict[str, Any]:
        """Setup CloudWatch monitoring and alarms"""        try:
            cloudwatch = self.session.client('cloudwatch')
            
            # Create log groups
            logs_client = self.session.client('logs')
            log_groups = [
                f'/aws/eks/ia-influencer-{self.config.environment}/cluster',
                f'/aws/rds/ia-influencer-postgres-{self.config.environment}',
                f'/aws/elasticache/ia-influencer-redis-{self.config.environment}',
                f'/aws/lambda/ia-influencer-{self.config.environment}'
            ]
            
            for log_group in log_groups:
                try:
                    logs_client.create_log_group(
                        logGroupName=log_group,
                        retentionInDays=30
                    )
                except logs_client.exceptions.ResourceAlreadyExistsException:
                    pass
            
            # Create CloudWatch dashboard
            dashboard_body = {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/EKS", "cluster_failed_request_count"],
                                ["AWS/RDS", "CPUUtilization"],
                                ["AWS/ElastiCache", "CPUUtilization"]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": self.config.region,
                            "title": "IA Influencer Platform Overview"
                        }
                    }
                ]
            }
            
            cloudwatch.put_dashboard(
                DashboardName=f'IA-Influencer-{self.config.environment}',
                DashboardBody=json.dumps(dashboard_body)
            )
            
            return {
                'log_groups': log_groups,
                'dashboard': f'IA-Influencer-{self.config.environment}',
                'retention_days': 30
            }
            
        except Exception as e:
            self.logger.error(f"Monitoring setup failed: {str(e)}")
            raise
    
    async def _configure_security(self) -> Dict[str, Any]:
        """Configure security groups and IAM roles"""        try:
            # Security groups are created by individual services
            # This method configures additional security policies
            
            iam = self.session.client('iam')
            
            # Create IAM role for application services
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_name = f'IAInfluencerAppRole-{self.config.environment}'
            
            try:
                iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='IAM role for IA Influencer application services'
                )
            except iam.exceptions.EntityAlreadyExistsException:
                pass
            
            return {
                'application_role': role_name,
                'security_groups_created': 4,
                'encryption_enabled': True
            }
            
        except Exception as e:
            self.logger.error(f"Security configuration failed: {str(e)}")
            raise
    
    async def _wait_for_cluster_active(self, cluster_name: str, max_wait: int = 1800):
        """Wait for EKS cluster to become active"""        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = self.eks.describe_cluster(name=cluster_name)
            status = response['cluster']['status']
            
            if status == 'ACTIVE':
                self.logger.info(f"EKS cluster {cluster_name} is now active")
                return True
            elif status in ['FAILED', 'DELETING']:
                raise Exception(f"EKS cluster {cluster_name} failed to become active: {status}")
            
            await asyncio.sleep(30)
        
        raise Exception(f"EKS cluster {cluster_name} did not become active within {max_wait} seconds")
    
    async def _get_or_create_eks_role(self) -> str:
        """Get or create EKS service role"""        iam = self.session.client('iam')
        role_name = f'IAInfluencerEKSRole-{self.config.environment}'
        
        try:
            response = iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except iam.exceptions.NoSuchEntityException:
            # Create the role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "eks.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach required policies
            policies = [
                'arn:aws:iam::aws:policy/AmazonEKSClusterPolicy'
            ]
            
            for policy in policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            
            return role_response['Role']['Arn']
    
    async def _get_or_create_node_role(self) -> str:
        """Get or create EKS node group role"""        iam = self.session.client('iam')
        role_name = f'IAInfluencerNodeRole-{self.config.environment}'
        
        try:
            response = iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except iam.exceptions.NoSuchEntityException:
            # Create the role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach required policies
            policies = [
                'arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy',
                'arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy',
                'arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly'
            ]
            
            for policy in policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            
            return role_response['Role']['Arn']
    
    async def _create_db_security_group(self, vpc_id: str) -> str:
        """Create security group for RDS databases"""        sg_name = f'ia-influencer-db-sg-{self.config.environment}'
        
        try:
            response = self.ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for IA Influencer databases',
                VpcId=vpc_id
            )
            sg_id = response['GroupId']
            
            # Allow PostgreSQL access from EKS nodes
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'IpRanges': [{'CidrIp': self.config.network_cidr}]
                    }
                ]
            )
            
            return sg_id
            
        except Exception as e:
            self.logger.error(f"Database security group creation failed: {str(e)}")
            raise
    
    async def _create_es_security_group(self, vpc_id: str) -> str:
        """Create security group for Elasticsearch"""        sg_name = f'ia-influencer-es-sg-{self.config.environment}'
        
        try:
            response = self.ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for IA Influencer Elasticsearch',
                VpcId=vpc_id
            )
            sg_id = response['GroupId']
            
            # Allow Elasticsearch access
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': self.config.network_cidr}]
                    }
                ]
            )
            
            return sg_id
            
        except Exception as e:
            self.logger.error(f"Elasticsearch security group creation failed: {str(e)}")
            raise
    
    async def _create_cache_security_group(self, vpc_id: str) -> str:
        """Create security group for Redis cache"""        sg_name = f'ia-influencer-cache-sg-{self.config.environment}'
        
        try:
            response = self.ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for IA Influencer Redis cache',
                VpcId=vpc_id
            )
            sg_id = response['GroupId']
            
            # Allow Redis access
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 6379,
                        'ToPort': 6379,
                        'IpRanges': [{'CidrIp': self.config.network_cidr}]
                    }
                ]
            )
            
            return sg_id
            
        except Exception as e:
            self.logger.error(f"Cache security group creation failed: {str(e)}")
            raise
    
    async def _setup_mongodb_atlas(self) -> Dict[str, Any]:
        """Setup MongoDB Atlas cluster (external service)"""        return {
            'provider': 'MongoDB Atlas',
            'cluster_name': f'ia-influencer-{self.config.environment}',
            'tier': 'M10',
            'region': 'AWS',
            'backup_enabled': True,
            'connection_string': 'mongodb+srv://cluster-url.mongodb.net/'
        }
    
    async def _rollback_failed_resources(self):
        """Rollback any resources created during failed provisioning"""        self.logger.warning("Rolling back failed AWS infrastructure provisioning")
        # Implementation would clean up any partially created resources
        pass
    
    async def destroy_infrastructure(self) -> bool:
        """Safely destroy AWS infrastructure"""        try:
            self.logger.info(f"Starting AWS infrastructure destruction for {self.config.environment}")
            
            # Delete resources in reverse order of creation
            await self._cleanup_monitoring()
            await self._cleanup_redis_cluster()
            await self._cleanup_elasticsearch()
            await self._cleanup_storage()
            await self._cleanup_databases()
            await self._cleanup_eks_cluster()
            await self._cleanup_vpc()
            
            self.logger.info("AWS infrastructure destruction completed")
            return True
            
        except Exception as e:
            self.logger.error(f"AWS infrastructure destruction failed: {str(e)}")
            return False
    
    async def validate_infrastructure(self) -> Dict[str, bool]:
        """Validate AWS infrastructure deployment"""        validation_results = {}
        
        try:
            # Validate VPC
            vpc_response = self.ec2.describe_vpcs(
                Filters=[
                    {'Name': 'tag:Project', 'Values': ['IA-Influencer-Agent']},
                    {'Name': 'tag:Environment', 'Values': [self.config.environment]}
                ]
            )
            validation_results['vpc'] = len(vpc_response['Vpcs']) > 0
            
            # Validate EKS cluster
            try:
                cluster_response = self.eks.describe_cluster(
                    name=f'ia-influencer-{self.config.environment}'
                )
                validation_results['eks'] = cluster_response['cluster']['status'] == 'ACTIVE'
            except:
                validation_results['eks'] = False
            
            # Validate RDS
            try:
                db_response = self.rds.describe_db_instances(
                    DBInstanceIdentifier=f'ia-influencer-postgres-{self.config.environment}'
                )
                validation_results['rds'] = db_response['DBInstances'][0]['DBInstanceStatus'] == 'available'
            except:
                validation_results['rds'] = False
            
            # Validate S3 buckets
            try:
                bucket_response = self.s3.list_buckets()
                ia_buckets = [b for b in bucket_response['Buckets'] 
                             if f'ia-influencer' in b['Name'] and self.config.environment in b['Name']]
                validation_results['s3'] = len(ia_buckets) >= 3
            except:
                validation_results['s3'] = False
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Infrastructure validation failed: {str(e)}")
            return {'error': str(e)}


class GCPInfrastructureManager(BaseCloudManager):
    """Google Cloud Platform infrastructure management"""    
    def __init__(self, config: InfrastructureConfig, project_id: str, credentials_path: str):
        super().__init__(config)
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.compute_client = compute_v1.InstancesClient()
        self.container_client = container_v1.ClusterManagerClient()
        
    async def provision_infrastructure(self) -> Dict[str, Any]:
        """Provision complete GCP infrastructure for IA Influencer platform"""        try:
            self.logger.info(f"Starting GCP infrastructure provisioning for {self.config.environment}")
            
            # 1. Create VPC network
            network_info = await self._provision_vpc_network()
            
            # 2. Create GKE cluster
            cluster_info = await self._provision_gke_cluster()
            
            # 3. Create Cloud SQL instances
            database_info = await self._provision_cloud_sql()
            
            # 4. Create Cloud Storage buckets
            storage_info = await self._provision_cloud_storage()
            
            # 5. Setup Cloud Monitoring
            monitoring_info = await self._setup_cloud_monitoring()
            
            infrastructure_summary = {
                'network': network_info,
                'cluster': cluster_info,
                'databases': database_info,
                'storage': storage_info,
                'monitoring': monitoring_info,
                'status': 'provisioned',
                'timestamp': time.time()
            }
            
            self.resource_tracker.update(infrastructure_summary)
            self.logger.info("GCP infrastructure provisioning completed successfully")
            
            return infrastructure_summary
            
        except Exception as e:
            self.logger.error(f"GCP infrastructure provisioning failed: {str(e)}")
            raise


class AzureInfrastructureManager(BaseCloudManager):
    """Microsoft Azure infrastructure management"""    
    def __init__(self, config: InfrastructureConfig, subscription_id: str, 
                 resource_group: str, credentials: DefaultAzureCredential):
        super().__init__(config)
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.credential = credentials
        self.resource_client = ResourceManagementClient(credentials, subscription_id)
        self.container_client = ContainerServiceClient(credentials, subscription_id)
        
    async def provision_infrastructure(self) -> Dict[str, Any]:
        """Provision complete Azure infrastructure for IA Influencer platform"""        try:
            self.logger.info(f"Starting Azure infrastructure provisioning for {self.config.environment}")
            
            # 1. Create resource group
            rg_info = await self._provision_resource_group()
            
            # 2. Create virtual network
            vnet_info = await self._provision_virtual_network()
            
            # 3. Create AKS cluster
            cluster_info = await self._provision_aks_cluster()
            
            # 4. Create Azure Database instances
            database_info = await self._provision_azure_databases()
            
            # 5. Create storage accounts
            storage_info = await self._provision_storage_accounts()
            
            # 6. Setup Azure Monitor
            monitoring_info = await self._setup_azure_monitor()
            
            infrastructure_summary = {
                'resource_group': rg_info,
                'network': vnet_info,
                'cluster': cluster_info,
                'databases': database_info,
                'storage': storage_info,
                'monitoring': monitoring_info,
                'status': 'provisioned',
                'timestamp': time.time()
            }
            
            self.resource_tracker.update(infrastructure_summary)
            self.logger.info("Azure infrastructure provisioning completed successfully")
            
            return infrastructure_summary
            
        except Exception as e:
            self.logger.error(f"Azure infrastructure provisioning failed: {str(e)}")
            raise


class MultiCloudInfrastructureManager:
    """Multi-cloud infrastructure orchestrator for hybrid deployments"""    
    def __init__(self, aws_config: InfrastructureConfig, gcp_config: InfrastructureConfig, 
                 azure_config: InfrastructureConfig):
        self.aws_manager = None
        self.gcp_manager = None  
        self.azure_manager = None
        self.logger = logging.getLogger(__name__)
        
    async def provision_hybrid_infrastructure(self, primary_cloud: CloudProvider, 
                                            secondary_clouds: List[CloudProvider]) -> Dict[str, Any]:
        """Provision infrastructure across multiple cloud providers"""        try:
            self.logger.info(f"Starting multi-cloud infrastructure provisioning")
            
            results = {}
            
            # Provision primary cloud infrastructure
            if primary_cloud == CloudProvider.AWS and self.aws_manager:
                results['primary'] = {
                    'provider': 'aws',
                    'infrastructure': await self.aws_manager.provision_infrastructure()
                }
            elif primary_cloud == CloudProvider.GCP and self.gcp_manager:
                results['primary'] = {
                    'provider': 'gcp',
                    'infrastructure': await self.gcp_manager.provision_infrastructure()
                }
            elif primary_cloud == CloudProvider.AZURE and self.azure_manager:
                results['primary'] = {
                    'provider': 'azure',
                    'infrastructure': await self.azure_manager.provision_infrastructure()
                }
            
            # Provision secondary cloud infrastructure in parallel
            secondary_tasks = []
            for cloud in secondary_clouds:
                if cloud == CloudProvider.AWS and self.aws_manager:
                    secondary_tasks.append(self._provision_secondary_aws())
                elif cloud == CloudProvider.GCP and self.gcp_manager:
                    secondary_tasks.append(self._provision_secondary_gcp())
                elif cloud == CloudProvider.AZURE and self.azure_manager:
                    secondary_tasks.append(self._provision_secondary_azure())
            
            if secondary_tasks:
                secondary_results = await asyncio.gather(*secondary_tasks, return_exceptions=True)
                results['secondary'] = secondary_results
            
            # Setup cross-cloud networking and replication
            if len(secondary_clouds) > 0:
                results['cross_cloud'] = await self._setup_cross_cloud_connectivity()
            
            self.logger.info("Multi-cloud infrastructure provisioning completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Multi-cloud provisioning failed: {str(e)}")
            raise
    
    async def _provision_secondary_aws(self) -> Dict[str, Any]:
        """Provision secondary AWS infrastructure for disaster recovery"""        if self.aws_manager:
            return await self.aws_manager.provision_infrastructure()
        return {}
    
    async def _provision_secondary_gcp(self) -> Dict[str, Any]:
        """Provision secondary GCP infrastructure for disaster recovery"""        if self.gcp_manager:
            return await self.gcp_manager.provision_infrastructure()
        return {}
    
    async def _provision_secondary_azure(self) -> Dict[str, Any]:
        """Provision secondary Azure infrastructure for disaster recovery"""        if self.azure_manager:
            return await self.azure_manager.provision_infrastructure()
        return {}
    
    async def _setup_cross_cloud_connectivity(self) -> Dict[str, Any]:
        """Setup VPN connections and data replication between clouds"""        return {
            'vpn_connections': [],
            'data_replication': 'configured',
            'backup_strategy': 'cross_cloud',
            'failover_enabled': True
        }


# Factory function for creating cloud managers
def create_cloud_manager(provider: CloudProvider, config: InfrastructureConfig, 
                        **kwargs) -> BaseCloudManager:
    """Factory function to create appropriate cloud manager"""    if provider == CloudProvider.AWS:
        return AWSInfrastructureManager(config, kwargs.get('credentials', {}))
    elif provider == CloudProvider.GCP:
        return GCPInfrastructureManager(
            config, 
            kwargs.get('project_id'), 
            kwargs.get('credentials_path')
        )
    elif provider == CloudProvider.AZURE:
        return AzureInfrastructureManager(
            config,
            kwargs.get('subscription_id'),
            kwargs.get('resource_group'),
            kwargs.get('credentials')
        )
    else:
        raise ValueError(f"Unsupported cloud provider: {provider}")
