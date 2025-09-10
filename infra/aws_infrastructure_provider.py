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
AWS Infrastructure Provider

Enterprise AWS infrastructure provider for Ainflue platform.
Provides comprehensive AWS resource management with enterprise security and optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AWSResourceConfig:
    """AWS resource configuration."""
    resource_type: str
    name: str
    region: str
    size: str
    configuration: Dict[str, Any]
    tags: Dict[str, str]

class AWSInfrastructureProvider:
    """
    Enterprise AWS infrastructure provider.
    
    Provides comprehensive AWS resource management including EC2, RDS, EKS, S3,
    with enterprise security, monitoring, and cost optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AWS infrastructure provider."""
        self.config = config or {}
        self.region = self.config.get("region", "us-west-2")
        self.profile = self.config.get("profile")
        
        # AWS clients
        self.clients = {}
        self.session = None
        
        # Resource tracking
        self.managed_resources = {}
        
        # Configuration
        self.enable_detailed_monitoring = self.config.get("enable_detailed_monitoring", True)
        self.enable_cost_optimization = self.config.get("enable_cost_optimization", True)
        self.default_security_group = self.config.get("default_security_group")
        self.default_subnet = self.config.get("default_subnet")
        self.default_vpc = self.config.get("default_vpc")
        
        # Initialize AWS session
        self._initialize_session()
        
        logger.info(f"AWSInfrastructureProvider initialized for region: {self.region}")
    
    def _initialize_session(self):
        """Initialize AWS session and clients."""
        try:
            # Create session
            if self.profile:
                self.session = boto3.Session(profile_name=self.profile)
            else:
                self.session = boto3.Session()
            
            # Initialize common clients
            self._initialize_clients()
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {str(e)}")
            raise
    
    def _initialize_clients(self):
        """Initialize AWS service clients."""
        try:
            # Core compute and storage
            self.clients['ec2'] = self.session.client('ec2', region_name=self.region)
            self.clients['s3'] = self.session.client('s3', region_name=self.region)
            self.clients['rds'] = self.session.client('rds', region_name=self.region)
            
            # Container services
            self.clients['ecs'] = self.session.client('ecs', region_name=self.region)
            self.clients['eks'] = self.session.client('eks', region_name=self.region)
            
            # Load balancing and networking
            self.clients['elbv2'] = self.session.client('elbv2', region_name=self.region)
            self.clients['route53'] = self.session.client('route53', region_name=self.region)
            self.clients['cloudfront'] = self.session.client('cloudfront', region_name=self.region)
            
            # Monitoring and security
            self.clients['cloudwatch'] = self.session.client('cloudwatch', region_name=self.region)
            self.clients['iam'] = self.session.client('iam', region_name=self.region)
            self.clients['kms'] = self.session.client('kms', region_name=self.region)
            self.clients['secretsmanager'] = self.session.client('secretsmanager', region_name=self.region)
            
            # Cost management
            self.clients['ce'] = self.session.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
            self.clients['pricing'] = self.session.client('pricing', region_name='us-east-1')
            
            logger.info(f"Initialized {len(self.clients)} AWS service clients")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
    
    async def initialize(self):
        """Initialize provider (async initialization tasks)."""
        try:
            # Validate credentials and permissions
            await self._validate_credentials()
            
            # Setup default VPC and security groups if needed
            await self._setup_default_infrastructure()
            
            logger.info("AWS provider initialization completed")
            
        except Exception as e:
            logger.error(f"AWS provider initialization failed: {str(e)}")
            raise
    
    async def _validate_credentials(self):
        """Validate AWS credentials and permissions."""
        try:
            # Test basic AWS access
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            
            logger.info(f"AWS credentials validated for: {identity.get('Arn')}")
            
            # Test required permissions
            await self._test_required_permissions()
            
        except Exception as e:
            logger.error(f"AWS credentials validation failed: {str(e)}")
            raise
    
    async def _test_required_permissions(self):
        """Test required AWS permissions."""
        try:
            # Test EC2 permissions
            self.clients['ec2'].describe_instances(MaxResults=5)
            
            # Test S3 permissions
            self.clients['s3'].list_buckets()
            
            # Test RDS permissions
            self.clients['rds'].describe_db_instances(MaxRecords=5)
            
            logger.info("Required AWS permissions validated")
            
        except ClientError as e:
            logger.error(f"Missing required AWS permissions: {str(e)}")
            raise
    
    async def _setup_default_infrastructure(self):
        """Setup default VPC and security groups if needed."""
        try:
            # Get default VPC if not specified
            if not self.default_vpc:
                vpcs = self.clients['ec2'].describe_vpcs(
                    Filters=[{'Name': 'isDefault', 'Values': ['true']}]
                )
                if vpcs['Vpcs']:
                    self.default_vpc = vpcs['Vpcs'][0]['VpcId']
                    logger.info(f"Using default VPC: {self.default_vpc}")
            
            # Create default security group if needed
            if not self.default_security_group:
                await self._create_default_security_group()
            
        except Exception as e:
            logger.error(f"Failed to setup default infrastructure: {str(e)}")
    
    async def _create_default_security_group(self):
        """Create default security group for Ainflue resources."""
        try:
            sg_name = "ainflue-default-sg"
            
            # Check if security group already exists
            try:
                sgs = self.clients['ec2'].describe_security_groups(
                    Filters=[
                        {'Name': 'group-name', 'Values': [sg_name]},
                        {'Name': 'vpc-id', 'Values': [self.default_vpc]}
                    ]
                )
                if sgs['SecurityGroups']:
                    self.default_security_group = sgs['SecurityGroups'][0]['GroupId']
                    logger.info(f"Using existing security group: {self.default_security_group}")
                    return
            except ClientError:
                pass
            
            # Create new security group
            response = self.clients['ec2'].create_security_group(
                GroupName=sg_name,
                Description="Default security group for Ainflue resources",
                VpcId=self.default_vpc,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'Name', 'Value': sg_name},
                        {'Key': 'Project', 'Value': 'Ainflue'},
                        {'Key': 'ManagedBy', 'Value': 'AWSInfrastructureProvider'}
                    ]
                }]
            )
            
            self.default_security_group = response['GroupId']
            
            # Add default ingress rules
            self.clients['ec2'].authorize_security_group_ingress(
                GroupId=self.default_security_group,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '10.0.0.0/8', 'Description': 'SSH from private networks'}]
                    }
                ]
            )
            
            logger.info(f"Created default security group: {self.default_security_group}")
            
        except Exception as e:
            logger.error(f"Failed to create default security group: {str(e)}")
    
    async def create_compute_instance(self, name: str, size: str, region: str, 
                                    configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create EC2 compute instance."""
        try:
            # Prepare instance configuration
            instance_config = {
                'ImageId': configuration.get('ami_id', 'ami-0c02fb55956c7d316'),  # Amazon Linux 2
                'InstanceType': size,
                'MinCount': 1,
                'MaxCount': 1,
                'SecurityGroupIds': [self.default_security_group],
                'TagSpecifications': [{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': k, 'Value': v} for k, v in {**tags, 'Name': name}.items()]
                }]
            }
            
            # Add key pair if specified
            if 'key_pair' in configuration:
                instance_config['KeyName'] = configuration['key_pair']
            
            # Add subnet if specified
            if 'subnet_id' in configuration:
                instance_config['SubnetId'] = configuration['subnet_id']
            elif self.default_subnet:
                instance_config['SubnetId'] = self.default_subnet
            
            # Add user data if specified
            if 'user_data' in configuration:
                instance_config['UserData'] = configuration['user_data']
            
            # Add IAM instance profile if specified
            if 'iam_instance_profile' in configuration:
                instance_config['IamInstanceProfile'] = {
                    'Name': configuration['iam_instance_profile']
                }
            
            # Enable detailed monitoring if configured
            if self.enable_detailed_monitoring:
                instance_config['Monitoring'] = {'Enabled': True}
            
            # Launch instance
            response = self.clients['ec2'].run_instances(**instance_config)
            instance = response['Instances'][0]
            
            instance_id = instance['InstanceId']
            
            # Wait for instance to be running
            await self._wait_for_instance_state(instance_id, 'running')
            
            # Get instance details
            instances = self.clients['ec2'].describe_instances(InstanceIds=[instance_id])
            instance_data = instances['Reservations'][0]['Instances'][0]
            
            # Track managed resource
            resource_info = {
                'id': instance_id,
                'name': name,
                'type': 'ec2_instance',
                'size': size,
                'region': region,
                'status': 'active',
                'created_at': datetime.now(),
                'endpoint': instance_data.get('PublicDnsName') or instance_data.get('PrivateIpAddress'),
                'metadata': {
                    'availability_zone': instance_data['Placement']['AvailabilityZone'],
                    'instance_type': instance_data['InstanceType'],
                    'vpc_id': instance_data.get('VpcId'),
                    'subnet_id': instance_data.get('SubnetId')
                }
            }
            
            self.managed_resources[instance_id] = resource_info
            
            logger.info(f"Created EC2 instance: {instance_id} ({name})")
            return resource_info
            
        except Exception as e:
            logger.error(f"Failed to create EC2 instance {name}: {str(e)}")
            raise
    
    async def create_storage_volume(self, name: str, size: str, region: str, 
                                  configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create EBS storage volume."""
        try:
            # Parse size (assuming size is in GB)
            volume_size = int(size.replace('GB', '').replace('gb', ''))
            
            # Prepare volume configuration
            volume_config = {
                'Size': volume_size,
                'VolumeType': configuration.get('volume_type', 'gp3'),
                'TagSpecifications': [{
                    'ResourceType': 'volume',
                    'Tags': [{'Key': k, 'Value': v} for k, v in {**tags, 'Name': name}.items()]
                }]
            }
            
            # Add availability zone
            if 'availability_zone' in configuration:
                volume_config['AvailabilityZone'] = configuration['availability_zone']
            else:
                # Get first AZ in region
                azs = self.clients['ec2'].describe_availability_zones()
                volume_config['AvailabilityZone'] = azs['AvailabilityZones'][0]['ZoneName']
            
            # Add encryption if specified
            if configuration.get('encrypted', True):
                volume_config['Encrypted'] = True
                if 'kms_key_id' in configuration:
                    volume_config['KmsKeyId'] = configuration['kms_key_id']
            
            # Add IOPS if specified for gp3 or io1/io2
            if volume_config['VolumeType'] in ['gp3', 'io1', 'io2'] and 'iops' in configuration:
                volume_config['Iops'] = configuration['iops']
            
            # Add throughput for gp3
            if volume_config['VolumeType'] == 'gp3' and 'throughput' in configuration:
                volume_config['Throughput'] = configuration['throughput']
            
            # Create volume
            response = self.clients['ec2'].create_volume(**volume_config)
            volume_id = response['VolumeId']
            
            # Wait for volume to be available
            await self._wait_for_volume_state(volume_id, 'available')
            
            # Track managed resource
            resource_info = {
                'id': volume_id,
                'name': name,
                'type': 'ebs_volume',
                'size': f"{volume_size}GB",
                'region': region,
                'status': 'active',
                'created_at': datetime.now(),
                'metadata': {
                    'volume_type': volume_config['VolumeType'],
                    'availability_zone': volume_config['AvailabilityZone'],
                    'encrypted': volume_config.get('Encrypted', False)
                }
            }
            
            self.managed_resources[volume_id] = resource_info
            
            logger.info(f"Created EBS volume: {volume_id} ({name})")
            return resource_info
            
        except Exception as e:
            logger.error(f"Failed to create EBS volume {name}: {str(e)}")
            raise
    
    async def create_database_instance(self, name: str, size: str, region: str, 
                                     configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create RDS database instance."""
        try:
            # Prepare RDS configuration
            db_config = {
                'DBInstanceIdentifier': name.lower().replace('_', '-'),
                'DBInstanceClass': size,
                'Engine': configuration.get('engine', 'postgres'),
                'EngineVersion': configuration.get('engine_version', '15.4'),
                'MasterUsername': configuration.get('master_username', 'admin'),
                'MasterUserPassword': configuration.get('master_password', 'ChangeMe123!'),
                'AllocatedStorage': configuration.get('allocated_storage', 20),
                'StorageType': configuration.get('storage_type', 'gp3'),
                'StorageEncrypted': configuration.get('encrypted', True),
                'VpcSecurityGroupIds': [self.default_security_group],
                'BackupRetentionPeriod': configuration.get('backup_retention_period', 7),
                'DeletionProtection': configuration.get('deletion_protection', False),
                'Tags': [{'Key': k, 'Value': v} for k, v in tags.items()]
            }
            
            # Add KMS key if specified
            if configuration.get('encrypted', True) and 'kms_key_id' in configuration:
                db_config['KmsKeyId'] = configuration['kms_key_id']
            
            # Add DB subnet group if specified
            if 'db_subnet_group' in configuration:
                db_config['DBSubnetGroupName'] = configuration['db_subnet_group']
            
            # Add parameter group if specified
            if 'parameter_group' in configuration:
                db_config['DBParameterGroupName'] = configuration['parameter_group']
            
            # Enable automated backups
            if configuration.get('automated_backup', True):
                db_config['BackupRetentionPeriod'] = configuration.get('backup_retention_period', 7)
                db_config['PreferredBackupWindow'] = configuration.get('backup_window', '03:00-04:00')
                db_config['PreferredMaintenanceWindow'] = configuration.get('maintenance_window', 'sun:04:00-sun:05:00')
            
            # Enable multi-AZ for production
            if configuration.get('multi_az', False):
                db_config['MultiAZ'] = True
            
            # Create database
            response = self.clients['rds'].create_db_instance(**db_config)
            db_instance = response['DBInstance']
            
            db_identifier = db_instance['DBInstanceIdentifier']
            
            # Wait for database to be available
            await self._wait_for_db_state(db_identifier, 'available')
            
            # Get updated instance information
            instances = self.clients['rds'].describe_db_instances(DBInstanceIdentifier=db_identifier)
            db_data = instances['DBInstances'][0]
            
            # Track managed resource
            resource_info = {
                'id': db_identifier,
                'name': name,
                'type': 'rds_instance',
                'size': size,
                'region': region,
                'status': 'active',
                'created_at': datetime.now(),
                'endpoint': db_data['Endpoint']['Address'],
                'metadata': {
                    'engine': db_data['Engine'],
                    'engine_version': db_data['EngineVersion'],
                    'port': db_data['Endpoint']['Port'],
                    'storage_encrypted': db_data['StorageEncrypted'],
                    'multi_az': db_data['MultiAZ']
                }
            }
            
            self.managed_resources[db_identifier] = resource_info
            
            logger.info(f"Created RDS instance: {db_identifier} ({name})")
            return resource_info
            
        except Exception as e:
            logger.error(f"Failed to create RDS instance {name}: {str(e)}")
            raise
    
    async def create_load_balancer(self, name: str, region: str, 
                                 configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create Application Load Balancer."""
        try:
            # Get subnets for load balancer
            subnets = configuration.get('subnets', [])
            if not subnets:
                # Get public subnets from default VPC
                subnets_response = self.clients['ec2'].describe_subnets(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [self.default_vpc]},
                        {'Name': 'map-public-ip-on-launch', 'Values': ['true']}
                    ]
                )
                subnets = [subnet['SubnetId'] for subnet in subnets_response['Subnets'][:2]]
            
            # Prepare load balancer configuration
            lb_config = {
                'Name': name.replace('_', '-'),
                'Scheme': configuration.get('scheme', 'internet-facing'),
                'Type': configuration.get('type', 'application'),
                'IpAddressType': configuration.get('ip_address_type', 'ipv4'),
                'Subnets': subnets,
                'SecurityGroups': [self.default_security_group],
                'Tags': [{'Key': k, 'Value': v} for k, v in tags.items()]
            }
            
            # Create load balancer
            response = self.clients['elbv2'].create_load_balancer(**lb_config)
            lb = response['LoadBalancers'][0]
            
            lb_arn = lb['LoadBalancerArn']
            
            # Wait for load balancer to be active
            await self._wait_for_lb_state(lb_arn, 'active')
            
            # Create default target group
            tg_response = self.clients['elbv2'].create_target_group(
                Name=f"{name}-tg".replace('_', '-'),
                Protocol='HTTP',
                Port=80,
                VpcId=self.default_vpc,
                HealthCheckProtocol='HTTP',
                HealthCheckPath='/health',
                HealthCheckIntervalSeconds=30,
                HealthyThresholdCount=2,
                UnhealthyThresholdCount=3,
                Tags=[{'Key': k, 'Value': v} for k, v in tags.items()]
            )
            
            tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
            
            # Create default listener
            self.clients['elbv2'].create_listener(
                LoadBalancerArn=lb_arn,
                Protocol='HTTP',
                Port=80,
                DefaultActions=[{
                    'Type': 'forward',
                    'TargetGroupArn': tg_arn
                }]
            )
            
            # Track managed resource
            resource_info = {
                'id': lb_arn,
                'name': name,
                'type': 'application_load_balancer',
                'size': 'standard',
                'region': region,
                'status': 'active',
                'created_at': datetime.now(),
                'endpoint': lb['DNSName'],
                'metadata': {
                    'scheme': lb['Scheme'],
                    'type': lb['Type'],
                    'vpc_id': lb['VpcId'],
                    'target_group_arn': tg_arn
                }
            }
            
            self.managed_resources[lb_arn] = resource_info
            
            logger.info(f"Created ALB: {lb_arn} ({name})")
            return resource_info
            
        except Exception as e:
            logger.error(f"Failed to create load balancer {name}: {str(e)}")
            raise
    
    async def create_resource(self, resource_type: str, name: str, size: str, region: str, 
                            configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create generic AWS resource."""
        try:
            if resource_type == "s3_bucket":
                return await self._create_s3_bucket(name, region, configuration, tags)
            elif resource_type == "eks_cluster":
                return await self._create_eks_cluster(name, region, configuration, tags)
            elif resource_type == "security_group":
                return await self._create_security_group(name, region, configuration, tags)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
                
        except Exception as e:
            logger.error(f"Failed to create resource {name} of type {resource_type}: {str(e)}")
            raise
    
    async def _create_s3_bucket(self, name: str, region: str, configuration: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Create S3 bucket."""
        try:
            bucket_config = {'Bucket': name.lower()}
            
            # Add region-specific configuration
            if region != 'us-east-1':
                bucket_config['CreateBucketConfiguration'] = {'LocationConstraint': region}
            
            # Create bucket
            self.clients['s3'].create_bucket(**bucket_config)
            
            # Enable versioning if requested
            if configuration.get('versioning', True):
                self.clients['s3'].put_bucket_versioning(
                    Bucket=name.lower(),
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            
            # Enable encryption if requested
            if configuration.get('encryption', True):
                self.clients['s3'].put_bucket_encryption(
                    Bucket=name.lower(),
                    ServerSideEncryptionConfiguration={
                        'Rules': [{
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }]
                    }
                )
            
            # Apply tags
            if tags:
                self.clients['s3'].put_bucket_tagging(
                    Bucket=name.lower(),
                    Tagging={'TagSet': [{'Key': k, 'Value': v} for k, v in tags.items()]}
                )
            
            # Track managed resource
            resource_info = {
                'id': name.lower(),
                'name': name,
                'type': 's3_bucket',
                'size': 'standard',
                'region': region,
                'status': 'active',
                'created_at': datetime.now(),
                'endpoint': f"https://{name.lower()}.s3.{region}.amazonaws.com",
                'metadata': {
                    'versioning': configuration.get('versioning', True),
                    'encryption': configuration.get('encryption', True)
                }
            }
            
            self.managed_resources[name.lower()] = resource_info
            
            logger.info(f"Created S3 bucket: {name.lower()}")
            return resource_info
            
        except Exception as e:
            logger.error(f"Failed to create S3 bucket {name}: {str(e)}")
            raise
    
    async def _wait_for_instance_state(self, instance_id: str, desired_state: str, timeout: int = 600):
        """Wait for EC2 instance to reach desired state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.clients['ec2'].describe_instances(InstanceIds=[instance_id])
                instance = response['Reservations'][0]['Instances'][0]
                
                current_state = instance['State']['Name']
                if current_state == desired_state:
                    return True
                elif current_state in ['terminated', 'stopping', 'stopped'] and desired_state != current_state:
                    raise Exception(f"Instance {instance_id} is in unexpected state: {current_state}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                if "InvalidInstanceID.NotFound" in str(e):
                    raise Exception(f"Instance {instance_id} not found")
                raise
        
        raise Exception(f"Timeout waiting for instance {instance_id} to reach state {desired_state}")
    
    async def _wait_for_volume_state(self, volume_id: str, desired_state: str, timeout: int = 300):
        """Wait for EBS volume to reach desired state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.clients['ec2'].describe_volumes(VolumeIds=[volume_id])
                volume = response['Volumes'][0]
                
                current_state = volume['State']
                if current_state == desired_state:
                    return True
                elif current_state in ['error', 'deleted']:
                    raise Exception(f"Volume {volume_id} is in error state: {current_state}")
                
                await asyncio.sleep(5)
                
            except Exception as e:
                if "InvalidVolume.NotFound" in str(e):
                    raise Exception(f"Volume {volume_id} not found")
                raise
        
        raise Exception(f"Timeout waiting for volume {volume_id} to reach state {desired_state}")
    
    async def _wait_for_db_state(self, db_identifier: str, desired_state: str, timeout: int = 1200):
        """Wait for RDS instance to reach desired state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.clients['rds'].describe_db_instances(DBInstanceIdentifier=db_identifier)
                db_instance = response['DBInstances'][0]
                
                current_state = db_instance['DBInstanceStatus']
                if current_state == desired_state:
                    return True
                elif current_state in ['failed', 'incompatible-parameters', 'incompatible-restore']:
                    raise Exception(f"DB instance {db_identifier} is in error state: {current_state}")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                if "DBInstanceNotFound" in str(e):
                    raise Exception(f"DB instance {db_identifier} not found")
                raise
        
        raise Exception(f"Timeout waiting for DB instance {db_identifier} to reach state {desired_state}")
    
    async def _wait_for_lb_state(self, lb_arn: str, desired_state: str, timeout: int = 600):
        """Wait for load balancer to reach desired state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.clients['elbv2'].describe_load_balancers(LoadBalancerArns=[lb_arn])
                lb = response['LoadBalancers'][0]
                
                current_state = lb['State']['Code']
                if current_state == desired_state:
                    return True
                elif current_state in ['failed']:
                    raise Exception(f"Load balancer {lb_arn} is in error state: {current_state}")
                
                await asyncio.sleep(15)
                
            except Exception as e:
                if "LoadBalancerNotFound" in str(e):
                    raise Exception(f"Load balancer {lb_arn} not found")
                raise
        
        raise Exception(f"Timeout waiting for load balancer {lb_arn} to reach state {desired_state}")
    
    async def scale_resource(self, resource_id: str, target_instances: int) -> bool:
        """Scale a resource (if applicable)."""
        try:
            if resource_id not in self.managed_resources:
                return False
            
            resource = self.managed_resources[resource_id]
            
            if resource['type'] == 'ec2_instance':
                # For EC2, this would involve Auto Scaling Groups
                logger.info(f"EC2 instance scaling not implemented for single instances")
                return False
            elif resource['type'] == 'rds_instance':
                # For RDS, this would involve read replicas or instance size changes
                logger.info(f"RDS scaling requires specific implementation")
                return False
            else:
                logger.warning(f"Scaling not supported for resource type: {resource['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to scale resource {resource_id}: {str(e)}")
            return False
    
    async def terminate_resource(self, resource_id: str) -> bool:
        """Terminate a resource."""
        try:
            if resource_id not in self.managed_resources:
                return False
            
            resource = self.managed_resources[resource_id]
            
            if resource['type'] == 'ec2_instance':
                self.clients['ec2'].terminate_instances(InstanceIds=[resource_id])
                await self._wait_for_instance_state(resource_id, 'terminated')
            elif resource['type'] == 'ebs_volume':
                self.clients['ec2'].delete_volume(VolumeId=resource_id)
            elif resource['type'] == 'rds_instance':
                self.clients['rds'].delete_db_instance(
                    DBInstanceIdentifier=resource_id,
                    SkipFinalSnapshot=True
                )
            elif resource['type'] == 's3_bucket':
                # Empty bucket first
                self._empty_s3_bucket(resource_id)
                self.clients['s3'].delete_bucket(Bucket=resource_id)
            elif resource['type'] == 'application_load_balancer':
                self.clients['elbv2'].delete_load_balancer(LoadBalancerArn=resource_id)
            
            # Remove from tracking
            del self.managed_resources[resource_id]
            
            logger.info(f"Terminated resource: {resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate resource {resource_id}: {str(e)}")
            return False
    
    def _empty_s3_bucket(self, bucket_name: str):
        """Empty S3 bucket before deletion."""
        try:
            # Delete all objects
            paginator = self.clients['s3'].get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name):
                if 'Contents' in page:
                    objects = [{'Key': obj['Key']} for obj in page['Contents']]
                    self.clients['s3'].delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects}
                    )
            
            # Delete all object versions if versioning is enabled
            paginator = self.clients['s3'].get_paginator('list_object_versions')
            for page in paginator.paginate(Bucket=bucket_name):
                if 'Versions' in page:
                    versions = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['Versions']]
                    self.clients['s3'].delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': versions}
                    )
                if 'DeleteMarkers' in page:
                    delete_markers = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['DeleteMarkers']]
                    self.clients['s3'].delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': delete_markers}
                    )
            
        except Exception as e:
            logger.error(f"Failed to empty S3 bucket {bucket_name}: {str(e)}")
    
    async def get_resource_metrics(self, resource_id: str) -> Dict[str, Any]:
        """Get metrics for a resource."""
        try:
            if resource_id not in self.managed_resources:
                return {}
            
            resource = self.managed_resources[resource_id]
            
            # Get CloudWatch metrics based on resource type
            if resource['type'] == 'ec2_instance':
                return await self._get_ec2_metrics(resource_id)
            elif resource['type'] == 'rds_instance':
                return await self._get_rds_metrics(resource_id)
            elif resource['type'] == 'application_load_balancer':
                return await self._get_alb_metrics(resource_id)
            else:
                return {"timestamp": datetime.now().isoformat()}
                
        except Exception as e:
            logger.error(f"Failed to get metrics for resource {resource_id}: {str(e)}")
            return {"error": str(e)}
    
    async def _get_ec2_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get EC2 instance metrics."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            # Get CPU utilization
            cpu_response = self.clients['cloudwatch'].get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            cpu_utilization = 0.0
            if cpu_response['Datapoints']:
                cpu_utilization = cpu_response['Datapoints'][-1]['Average']
            
            return {
                "instance_count": 1,
                "cpu_utilization": cpu_utilization,
                "memory_utilization": 0.0,  # Would need CloudWatch agent for memory metrics
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get EC2 metrics for {instance_id}: {str(e)}")
            return {"timestamp": datetime.now().isoformat()}
    
    async def _get_rds_metrics(self, db_identifier: str) -> Dict[str, Any]:
        """Get RDS metrics."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            # Get CPU utilization
            cpu_response = self.clients['cloudwatch'].get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            cpu_utilization = 0.0
            if cpu_response['Datapoints']:
                cpu_utilization = cpu_response['Datapoints'][-1]['Average']
            
            # Get database connections
            connections_response = self.clients['cloudwatch'].get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='DatabaseConnections',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            connections = 0.0
            if connections_response['Datapoints']:
                connections = connections_response['Datapoints'][-1]['Average']
            
            return {
                "cpu_utilization": cpu_utilization,
                "database_connections": connections,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get RDS metrics for {db_identifier}: {str(e)}")
            return {"timestamp": datetime.now().isoformat()}
    
    async def _get_alb_metrics(self, lb_arn: str) -> Dict[str, Any]:
        """Get ALB metrics."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            # Extract load balancer name from ARN
            lb_name = lb_arn.split('/')[-1]
            
            # Get request count
            requests_response = self.clients['cloudwatch'].get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='RequestCount',
                Dimensions=[{'Name': 'LoadBalancer', 'Value': lb_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            request_count = 0.0
            if requests_response['Datapoints']:
                request_count = requests_response['Datapoints'][-1]['Sum']
            
            return {
                "request_count": request_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get ALB metrics for {lb_arn}: {str(e)}")
            return {"timestamp": datetime.now().isoformat()}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get overall provider metrics."""
        try:
            # Count resources by type
            resource_counts = {}
            total_cost = 0.0
            
            for resource in self.managed_resources.values():
                resource_type = resource['type']
                resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
                
                # Estimate cost (this would integrate with AWS Cost Explorer in production)
                total_cost += self._estimate_resource_cost(resource)
            
            return {
                "provider": "aws",
                "region": self.region,
                "total_resources": len(self.managed_resources),
                "resource_counts": resource_counts,
                "estimated_cost": total_cost,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get AWS provider metrics: {str(e)}")
            return {"error": str(e)}
    
    def _estimate_resource_cost(self, resource: Dict[str, Any]) -> float:
        """Estimate cost for a resource (simplified)."""
        # This is a simplified cost estimation
        # In production, this would use AWS Pricing API or Cost Explorer
        
        cost_per_hour = {
            'ec2_instance': 0.05,  # Average small instance
            'rds_instance': 0.03,  # Average small RDS
            'ebs_volume': 0.001,   # Per GB per hour
            's3_bucket': 0.001,    # Minimal cost
            'application_load_balancer': 0.025
        }
        
        base_cost = cost_per_hour.get(resource['type'], 0.01)
        
        # Calculate uptime hours
        uptime = datetime.now() - resource['created_at']
        hours = uptime.total_seconds() / 3600
        
        return base_cost * hours
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on AWS provider."""
        try:
            # Test basic connectivity
            self.clients['ec2'].describe_regions()
            
            # Count healthy vs unhealthy resources
            healthy_resources = 0
            unhealthy_resources = 0
            
            for resource in self.managed_resources.values():
                if resource['status'] == 'active':
                    healthy_resources += 1
                else:
                    unhealthy_resources += 1
            
            health_status = "healthy" if unhealthy_resources == 0 else "degraded"
            
            return {
                "healthy": health_status == "healthy",
                "status": health_status,
                "total_resources": len(self.managed_resources),
                "healthy_resources": healthy_resources,
                "unhealthy_resources": unhealthy_resources,
                "region": self.region,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AWS health check failed: {str(e)}")
            return {
                "healthy": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Export the main class
__all__ = ["AWSInfrastructureProvider", "AWSResourceConfig"]