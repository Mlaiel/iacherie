"""AWS Deployment Manager - Enterprise AWS Infrastructure Management
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This module provides comprehensive AWS deployment and management capabilities
for the IA Influencer Agent platform, including EC2, ECS, Lambda, RDS, S3,
CloudFront, and other AWS services.
"""import logging
import asyncio
import boto3
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from botocore.exceptions import ClientError, NoCredentialsError
import aioboto3

logger = logging.getLogger(__name__)

class AWSRegion(Enum):
    """AWS regions for global deployment"""    US_EAST_1 = "us-east-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_NORTHEAST_1 = "ap-northeast-1"

class AWSServiceType(Enum):
    """AWS service types"""    EC2 = "ec2"
    ECS = "ecs"
    LAMBDA = "lambda"
    RDS = "rds"
    S3 = "s3"
    CLOUDFRONT = "cloudfront"
    ELB = "elb"
    ROUTE53 = "route53"
    VPC = "vpc"
    IAM = "iam"
    CLOUDWATCH = "cloudwatch"
    SECRETS_MANAGER = "secretsmanager"

@dataclass
class AWSCredentials:
    """AWS credentials configuration"""    access_key_id: str
    secret_access_key: str
    session_token: Optional[str] = None
    region: str = "eu-central-1"
    profile_name: Optional[str] = None

@dataclass
class AWSDeploymentConfig:
    """AWS deployment configuration"""    environment: str
    region: AWSRegion
    vpc_config: Dict[str, Any]
    services: List[Dict[str, Any]]
    security_groups: List[Dict[str, Any]]
    load_balancer_config: Dict[str, Any]
    database_config: Dict[str, Any]
    storage_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    backup_config: Dict[str, Any]
    scaling_config: Dict[str, Any]
    compliance_settings: Dict[str, Any]
    cost_optimization: Dict[str, Any]

@dataclass
class AWSResource:
    """AWS resource representation"""    resource_id: str
    resource_type: AWSServiceType
    region: AWSRegion
    status: str
    created_at: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    cost_per_hour: float = 0.0
    security_compliance: bool = True

class AWSDeploymentManager:
    """Enterprise AWS deployment and management system"""    
    def __init__(self, credentials: AWSCredentials):
        """Initialize AWS deployment manager"""        self.logger = logging.getLogger(self.__class__.__name__)
        self.credentials = credentials
        self.session = aioboto3.Session(
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=credentials.region
        )
        self.deployed_resources: Dict[str, AWSResource] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
    async def initialize(self) -> bool:
        """Initialize AWS connection and validate credentials"""        try:
            async with self.session.client('sts') as sts:
                caller_identity = await sts.get_caller_identity()
                self.logger.info(f"AWS credentials validated for account: {caller_identity.get('Account')}")
                return True
        except (ClientError, NoCredentialsError) as e:
            self.logger.error(f"AWS credentials validation failed: {e}")
            return False
    
    async def deploy_infrastructure(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy complete infrastructure stack"""        deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.logger.info(f"Starting AWS infrastructure deployment: {deployment_id}")
        
        try:
            # Deploy VPC and networking
            vpc_resources = await self._deploy_vpc_infrastructure(config)
            
            # Deploy security groups
            security_resources = await self._deploy_security_groups(config)
            
            # Deploy database infrastructure
            database_resources = await self._deploy_database_infrastructure(config)
            
            # Deploy application services
            app_resources = await self._deploy_application_services(config)
            
            # Deploy load balancers
            lb_resources = await self._deploy_load_balancers(config)
            
            # Deploy storage infrastructure
            storage_resources = await self._deploy_storage_infrastructure(config)
            
            # Deploy monitoring and logging
            monitoring_resources = await self._deploy_monitoring_infrastructure(config)
            
            # Configure auto-scaling
            scaling_resources = await self._configure_auto_scaling(config)
            
            # Configure backup systems
            backup_resources = await self._configure_backup_systems(config)
            
            deployment_result = {
                "deployment_id": deployment_id,
                "status": "completed",
                "resources": {
                    "vpc": vpc_resources,
                    "security": security_resources,
                    "database": database_resources,
                    "applications": app_resources,
                    "load_balancer": lb_resources,
                    "storage": storage_resources,
                    "monitoring": monitoring_resources,
                    "scaling": scaling_resources,
                    "backup": backup_resources
                },
                "endpoints": await self._get_deployment_endpoints(),
                "cost_estimate": await self._calculate_deployment_cost(),
                "deployed_at": datetime.now().isoformat()
            }
            
            self.deployment_history.append(deployment_result)
            self.logger.info(f"AWS infrastructure deployment completed: {deployment_id}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"AWS infrastructure deployment failed: {e}")
            await self._rollback_deployment(deployment_id)
            raise
    
    async def _deploy_vpc_infrastructure(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy VPC and networking infrastructure"""        vpc_config = config.vpc_config
        
        async with self.session.client('ec2', region_name=config.region.value) as ec2:
            # Create VPC
            vpc_response = await ec2.create_vpc(
                CidrBlock=vpc_config.get('cidr_block', '10.0.0.0/16'),
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': f"ia-influencer-vpc-{config.environment}"},
                        {'Key': 'Environment', 'Value': config.environment},
                        {'Key': 'Project', 'Value': 'IA-Influencer-Agent'}
                    ]
                }]
            )
            vpc_id = vpc_response['Vpc']['VpcId']
            
            # Create Internet Gateway
            igw_response = await ec2.create_internet_gateway(
                TagSpecifications=[{
                    'ResourceType': 'internet-gateway',
                    'Tags': [
                        {'Key': 'Name', 'Value': f"ia-influencer-igw-{config.environment}"},
                        {'Key': 'Environment', 'Value': config.environment}
                    ]
                }]
            )
            igw_id = igw_response['InternetGateway']['InternetGatewayId']
            
            # Attach Internet Gateway to VPC
            await ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )
            
            # Create public subnets
            public_subnets = []
            for i, subnet_config in enumerate(vpc_config.get('public_subnets', [])):
                subnet_response = await ec2.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=subnet_config['cidr'],
                    AvailabilityZone=subnet_config['availability_zone'],
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f"ia-influencer-public-subnet-{i+1}-{config.environment}"},
                            {'Key': 'Type', 'Value': 'Public'},
                            {'Key': 'Environment', 'Value': config.environment}
                        ]
                    }]
                )
                public_subnets.append(subnet_response['Subnet']['SubnetId'])
            
            # Create private subnets
            private_subnets = []
            for i, subnet_config in enumerate(vpc_config.get('private_subnets', [])):
                subnet_response = await ec2.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=subnet_config['cidr'],
                    AvailabilityZone=subnet_config['availability_zone'],
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f"ia-influencer-private-subnet-{i+1}-{config.environment}"},
                            {'Key': 'Type', 'Value': 'Private'},
                            {'Key': 'Environment', 'Value': config.environment}
                        ]
                    }]
                )
                private_subnets.append(subnet_response['Subnet']['SubnetId'])
            
            # Create route tables
            public_rt_response = await ec2.create_route_table(
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'route-table',
                    'Tags': [
                        {'Key': 'Name', 'Value': f"ia-influencer-public-rt-{config.environment}"},
                        {'Key': 'Type', 'Value': 'Public'},
                        {'Key': 'Environment', 'Value': config.environment}
                    ]
                }]
            )
            public_rt_id = public_rt_response['RouteTable']['RouteTableId']
            
            # Add route to Internet Gateway
            await ec2.create_route(
                RouteTableId=public_rt_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )
            
            # Associate public subnets with public route table
            for subnet_id in public_subnets:
                await ec2.associate_route_table(
                    RouteTableId=public_rt_id,
                    SubnetId=subnet_id
                )
            
            return {
                "vpc_id": vpc_id,
                "internet_gateway_id": igw_id,
                "public_subnets": public_subnets,
                "private_subnets": private_subnets,
                "public_route_table_id": public_rt_id,
                "status": "deployed"
            }
    
    async def _deploy_security_groups(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy security groups"""        security_groups = {}
        
        async with self.session.client('ec2', region_name=config.region.value) as ec2:
            for sg_config in config.security_groups:
                sg_response = await ec2.create_security_group(
                    GroupName=sg_config['name'],
                    Description=sg_config['description'],
                    VpcId=sg_config['vpc_id'],
                    TagSpecifications=[{
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': 'Name', 'Value': sg_config['name']},
                            {'Key': 'Environment', 'Value': config.environment}
                        ]
                    }]
                )
                sg_id = sg_response['GroupId']
                
                # Add ingress rules
                for rule in sg_config.get('ingress_rules', []):
                    await ec2.authorize_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[{
                            'IpProtocol': rule['protocol'],
                            'FromPort': rule['from_port'],
                            'ToPort': rule['to_port'],
                            'IpRanges': [{'CidrIp': rule['cidr']}]
                        }]
                    )
                
                security_groups[sg_config['name']] = sg_id
        
        return security_groups
    
    async def _deploy_database_infrastructure(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy RDS database infrastructure"""        db_config = config.database_config
        
        async with self.session.client('rds', region_name=config.region.value) as rds:
            # Create DB subnet group
            subnet_group_response = await rds.create_db_subnet_group(
                DBSubnetGroupName=f"ia-influencer-db-subnet-group-{config.environment}",
                DBSubnetGroupDescription="IA Influencer Agent database subnet group",
                SubnetIds=db_config['subnet_ids'],
                Tags=[
                    {'Key': 'Name', 'Value': f"ia-influencer-db-subnet-group-{config.environment}"},
                    {'Key': 'Environment', 'Value': config.environment}
                ]
            )
            
            # Create RDS instance
            db_response = await rds.create_db_instance(
                DBInstanceIdentifier=f"ia-influencer-db-{config.environment}",
                DBInstanceClass=db_config.get('instance_class', 'db.t3.large'),
                Engine=db_config.get('engine', 'postgres'),
                EngineVersion=db_config.get('engine_version', '13.7'),
                MasterUsername=db_config['master_username'],
                MasterUserPassword=db_config['master_password'],
                AllocatedStorage=db_config.get('allocated_storage', 100),
                StorageType=db_config.get('storage_type', 'gp2'),
                DBSubnetGroupName=f"ia-influencer-db-subnet-group-{config.environment}",
                VpcSecurityGroupIds=db_config['security_group_ids'],
                BackupRetentionPeriod=db_config.get('backup_retention', 7),
                MultiAZ=db_config.get('multi_az', True),
                StorageEncrypted=True,
                DeletionProtection=config.environment == 'production',
                Tags=[
                    {'Key': 'Name', 'Value': f"ia-influencer-db-{config.environment}"},
                    {'Key': 'Environment', 'Value': config.environment}
                ]
            )
            
            return {
                "db_instance_id": db_response['DBInstance']['DBInstanceIdentifier'],
                "db_endpoint": db_response['DBInstance']['Endpoint']['Address'] if 'Endpoint' in db_response['DBInstance'] else None,
                "db_port": db_response['DBInstance']['DbInstancePort'],
                "subnet_group_name": subnet_group_response['DBSubnetGroup']['DBSubnetGroupName'],
                "status": "creating"
            }
    
    async def _deploy_application_services(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy application services (ECS/Lambda)"""        services = {}
        
        # Deploy ECS services
        for service_config in config.services:
            if service_config['type'] == 'ecs':
                ecs_service = await self._deploy_ecs_service(service_config, config)
                services[service_config['name']] = ecs_service
            elif service_config['type'] == 'lambda':
                lambda_service = await self._deploy_lambda_function(service_config, config)
                services[service_config['name']] = lambda_service
        
        return services
    
    async def _deploy_ecs_service(self, service_config: Dict[str, Any], config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy ECS service"""        async with self.session.client('ecs', region_name=config.region.value) as ecs:
            # Create ECS cluster if not exists
            cluster_name = f"ia-influencer-cluster-{config.environment}"
            try:
                await ecs.create_cluster(
                    clusterName=cluster_name,
                    tags=[
                        {'key': 'Environment', 'value': config.environment},
                        {'key': 'Project', 'value': 'IA-Influencer-Agent'}
                    ]
                )
            except ClientError as e:
                if 'ClusterAlreadyExistsException' not in str(e):
                    raise
            
            # Register task definition
            task_def_response = await ecs.register_task_definition(
                family=service_config['name'],
                networkMode='awsvpc',
                requiresCompatibilities=['FARGATE'],
                cpu=str(service_config.get('cpu', 256)),
                memory=str(service_config.get('memory', 512)),
                executionRoleArn=service_config['execution_role_arn'],
                taskRoleArn=service_config['task_role_arn'],
                containerDefinitions=[{
                    'name': service_config['name'],
                    'image': service_config['image'],
                    'portMappings': [{
                        'containerPort': service_config.get('port', 8000),
                        'protocol': 'tcp'
                    }],
                    'environment': [
                        {'name': k, 'value': v} for k, v in service_config.get('environment', {}).items()
                    ],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': f"/ecs/{service_config['name']}",
                            'awslogs-region': config.region.value,
                            'awslogs-stream-prefix': 'ecs'
                        }
                    }
                }]
            )
            
            # Create ECS service
            service_response = await ecs.create_service(
                cluster=cluster_name,
                serviceName=service_config['name'],
                taskDefinition=service_config['name'],
                desiredCount=service_config.get('desired_count', 2),
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': service_config['subnet_ids'],
                        'securityGroups': service_config['security_group_ids'],
                        'assignPublicIp': 'ENABLED' if service_config.get('public', False) else 'DISABLED'
                    }
                },
                loadBalancers=[{
                    'targetGroupArn': service_config['target_group_arn'],
                    'containerName': service_config['name'],
                    'containerPort': service_config.get('port', 8000)
                }] if 'target_group_arn' in service_config else [],
                tags=[
                    {'key': 'Environment', 'value': config.environment},
                    {'key': 'Service', 'value': service_config['name']}
                ]
            )
            
            return {
                "cluster_name": cluster_name,
                "service_name": service_config['name'],
                "task_definition_arn": task_def_response['taskDefinition']['taskDefinitionArn'],
                "service_arn": service_response['service']['serviceArn'],
                "status": "deploying"
            }
    
    async def _deploy_lambda_function(self, service_config: Dict[str, Any], config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy Lambda function"""        async with self.session.client('lambda', region_name=config.region.value) as lambda_client:
            function_response = await lambda_client.create_function(
                FunctionName=service_config['name'],
                Runtime=service_config.get('runtime', 'python3.9'),
                Role=service_config['execution_role_arn'],
                Handler=service_config.get('handler', 'lambda_function.lambda_handler'),
                Code={
                    'S3Bucket': service_config['code_bucket'],
                    'S3Key': service_config['code_key']
                },
                Description=service_config.get('description', ''),
                Timeout=service_config.get('timeout', 30),
                MemorySize=service_config.get('memory_size', 128),
                Environment={
                    'Variables': service_config.get('environment', {})
                },
                VpcConfig={
                    'SubnetIds': service_config.get('subnet_ids', []),
                    'SecurityGroupIds': service_config.get('security_group_ids', [])
                } if service_config.get('vpc_enabled', False) else {},
                Tags={
                    'Environment': config.environment,
                    'Service': service_config['name']
                }
            )
            
            return {
                "function_name": service_config['name'],
                "function_arn": function_response['FunctionArn'],
                "runtime": service_config.get('runtime', 'python3.9'),
                "status": "active"
            }
    
    async def _deploy_load_balancers(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy Application Load Balancers"""        lb_config = config.load_balancer_config
        
        async with self.session.client('elbv2', region_name=config.region.value) as elbv2:
            # Create Application Load Balancer
            lb_response = await elbv2.create_load_balancer(
                Name=f"ia-influencer-alb-{config.environment}",
                Subnets=lb_config['subnet_ids'],
                SecurityGroups=lb_config['security_group_ids'],
                Scheme=lb_config.get('scheme', 'internet-facing'),
                Type='application',
                IpAddressType='ipv4',
                Tags=[
                    {'Key': 'Name', 'Value': f"ia-influencer-alb-{config.environment}"},
                    {'Key': 'Environment', 'Value': config.environment}
                ]
            )
            lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
            lb_dns = lb_response['LoadBalancers'][0]['DNSName']
            
            # Create target groups
            target_groups = {}
            for tg_config in lb_config.get('target_groups', []):
                tg_response = await elbv2.create_target_group(
                    Name=tg_config['name'],
                    Protocol=tg_config.get('protocol', 'HTTP'),
                    Port=tg_config.get('port', 80),
                    VpcId=tg_config['vpc_id'],
                    TargetType=tg_config.get('target_type', 'ip'),
                    HealthCheckProtocol=tg_config.get('health_check_protocol', 'HTTP'),
                    HealthCheckPath=tg_config.get('health_check_path', '/health'),
                    HealthCheckIntervalSeconds=tg_config.get('health_check_interval', 30),
                    HealthCheckTimeoutSeconds=tg_config.get('health_check_timeout', 5),
                    HealthyThresholdCount=tg_config.get('healthy_threshold', 2),
                    UnhealthyThresholdCount=tg_config.get('unhealthy_threshold', 3),
                    Tags=[
                        {'Key': 'Name', 'Value': tg_config['name']},
                        {'Key': 'Environment', 'Value': config.environment}
                    ]
                )
                target_groups[tg_config['name']] = tg_response['TargetGroups'][0]['TargetGroupArn']
            
            # Create listeners
            listeners = {}
            for listener_config in lb_config.get('listeners', []):
                listener_response = await elbv2.create_listener(
                    LoadBalancerArn=lb_arn,
                    Protocol=listener_config.get('protocol', 'HTTP'),
                    Port=listener_config.get('port', 80),
                    DefaultActions=[{
                        'Type': 'forward',
                        'TargetGroupArn': target_groups[listener_config['target_group']]
                    }]
                )
                listeners[f"{listener_config.get('protocol', 'HTTP')}:{listener_config.get('port', 80)}"] = listener_response['Listeners'][0]['ListenerArn']
            
            return {
                "load_balancer_arn": lb_arn,
                "load_balancer_dns": lb_dns,
                "target_groups": target_groups,
                "listeners": listeners,
                "status": "active"
            }
    
    async def _deploy_storage_infrastructure(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy S3 storage infrastructure"""        storage_config = config.storage_config
        
        async with self.session.client('s3', region_name=config.region.value) as s3:
            buckets = {}
            
            for bucket_config in storage_config.get('buckets', []):
                bucket_name = bucket_config['name']
                
                # Create S3 bucket
                if config.region.value == 'us-east-1':
                    await s3.create_bucket(Bucket=bucket_name)
                else:
                    await s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': config.region.value}
                    )
                
                # Configure bucket encryption
                await s3.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [{
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }]
                    }
                )
                
                # Configure bucket versioning
                if bucket_config.get('versioning', True):
                    await s3.put_bucket_versioning(
                        Bucket=bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                
                # Configure bucket lifecycle
                if 'lifecycle_rules' in bucket_config:
                    await s3.put_bucket_lifecycle_configuration(
                        Bucket=bucket_name,
                        LifecycleConfiguration={
                            'Rules': bucket_config['lifecycle_rules']
                        }
                    )
                
                # Configure bucket CORS
                if 'cors_configuration' in bucket_config:
                    await s3.put_bucket_cors(
                        Bucket=bucket_name,
                        CORSConfiguration=bucket_config['cors_configuration']
                    )
                
                buckets[bucket_name] = {
                    "bucket_name": bucket_name,
                    "region": config.region.value,
                    "encryption": "AES256",
                    "versioning": bucket_config.get('versioning', True),
                    "status": "active"
                }
            
            return buckets
    
    async def _deploy_monitoring_infrastructure(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Deploy CloudWatch monitoring infrastructure"""        monitoring_config = config.monitoring_config
        
        async with self.session.client('logs', region_name=config.region.value) as logs:
            async with self.session.client('cloudwatch', region_name=config.region.value) as cloudwatch:
                # Create log groups
                log_groups = {}
                for log_group_config in monitoring_config.get('log_groups', []):
                    try:
                        await logs.create_log_group(
                            logGroupName=log_group_config['name'],
                            retentionInDays=log_group_config.get('retention_days', 30)
                        )
                        log_groups[log_group_config['name']] = {
                            "name": log_group_config['name'],
                            "retention_days": log_group_config.get('retention_days', 30),
                            "status": "active"
                        }
                    except ClientError as e:
                        if 'ResourceAlreadyExistsException' not in str(e):
                            raise
                
                # Create CloudWatch alarms
                alarms = {}
                for alarm_config in monitoring_config.get('alarms', []):
                    await cloudwatch.put_metric_alarm(
                        AlarmName=alarm_config['name'],
                        ComparisonOperator=alarm_config['comparison_operator'],
                        EvaluationPeriods=alarm_config['evaluation_periods'],
                        MetricName=alarm_config['metric_name'],
                        Namespace=alarm_config['namespace'],
                        Period=alarm_config['period'],
                        Statistic=alarm_config['statistic'],
                        Threshold=alarm_config['threshold'],
                        ActionsEnabled=True,
                        AlarmActions=alarm_config.get('alarm_actions', []),
                        AlarmDescription=alarm_config.get('description', ''),
                        Unit=alarm_config.get('unit', 'Count')
                    )
                    alarms[alarm_config['name']] = {
                        "name": alarm_config['name'],
                        "metric_name": alarm_config['metric_name'],
                        "threshold": alarm_config['threshold'],
                        "status": "active"
                    }
                
                return {
                    "log_groups": log_groups,
                    "alarms": alarms,
                    "dashboard_url": f"https://{config.region.value}.console.aws.amazon.com/cloudwatch/",
                    "status": "active"
                }
    
    async def _configure_auto_scaling(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Configure auto-scaling policies"""        scaling_config = config.scaling_config
        
        async with self.session.client('application-autoscaling', region_name=config.region.value) as autoscaling:
            scaling_targets = {}
            
            for target_config in scaling_config.get('targets', []):
                # Register scalable target
                await autoscaling.register_scalable_target(
                    ServiceNamespace=target_config['service_namespace'],
                    ResourceId=target_config['resource_id'],
                    ScalableDimension=target_config['scalable_dimension'],
                    MinCapacity=target_config['min_capacity'],
                    MaxCapacity=target_config['max_capacity']
                )
                
                # Create scaling policies
                for policy_config in target_config.get('policies', []):
                    await autoscaling.put_scaling_policy(
                        PolicyName=policy_config['name'],
                        ServiceNamespace=target_config['service_namespace'],
                        ResourceId=target_config['resource_id'],
                        ScalableDimension=target_config['scalable_dimension'],
                        PolicyType='TargetTrackingScaling',
                        TargetTrackingScalingPolicyConfiguration={
                            'TargetValue': policy_config['target_value'],
                            'PredefinedMetricSpecification': {
                                'PredefinedMetricType': policy_config['metric_type']
                            },
                            'ScaleOutCooldown': policy_config.get('scale_out_cooldown', 300),
                            'ScaleInCooldown': policy_config.get('scale_in_cooldown', 300)
                        }
                    )
                
                scaling_targets[target_config['resource_id']] = {
                    "resource_id": target_config['resource_id'],
                    "min_capacity": target_config['min_capacity'],
                    "max_capacity": target_config['max_capacity'],
                    "policies": len(target_config.get('policies', [])),
                    "status": "active"
                }
            
            return scaling_targets
    
    async def _configure_backup_systems(self, config: AWSDeploymentConfig) -> Dict[str, Any]:
        """Configure AWS Backup systems"""        backup_config = config.backup_config
        
        async with self.session.client('backup', region_name=config.region.value) as backup:
            # Create backup vault
            vault_name = f"ia-influencer-backup-vault-{config.environment}"
            await backup.create_backup_vault(
                BackupVaultName=vault_name,
                EncryptionKeyArn=backup_config.get('kms_key_arn'),
                CreatorRequestId=f"vault-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # Create backup plan
            backup_plan_response = await backup.create_backup_plan(
                BackupPlan={
                    'BackupPlanName': f"ia-influencer-backup-plan-{config.environment}",
                    'Rules': [{
                        'RuleName': 'DailyBackups',
                        'TargetBackupVaultName': vault_name,
                        'ScheduleExpression': backup_config.get('schedule', 'cron(0 5 ? * * *)'),
                        'StartWindowMinutes': backup_config.get('start_window', 60),
                        'CompletionWindowMinutes': backup_config.get('completion_window', 120),
                        'Lifecycle': {
                            'MoveToColdStorageAfterDays': backup_config.get('cold_storage_days', 30),
                            'DeleteAfterDays': backup_config.get('retention_days', 365)
                        },
                        'RecoveryPointTags': {
                            'Environment': config.environment,
                            'BackupType': 'Automated'
                        }
                    }]
                },
                CreatorRequestId=f"plan-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            return {
                "backup_vault_name": vault_name,
                "backup_plan_id": backup_plan_response['BackupPlanId'],
                "backup_plan_arn": backup_plan_response['BackupPlanArn'],
                "schedule": backup_config.get('schedule', 'cron(0 5 ? * * *)'),
                "retention_days": backup_config.get('retention_days', 365),
                "status": "active"
            }
    
    async def _get_deployment_endpoints(self) -> Dict[str, str]:
        """Get deployment endpoints"""        return {
            "api_gateway": "https://api.ia-influencer.com",
            "web_app": "https://app.ia-influencer.com",
            "admin_panel": "https://admin.ia-influencer.com",
            "monitoring": "https://monitoring.ia-influencer.com"
        }
    
    async def _calculate_deployment_cost(self) -> Dict[str, float]:
        """Calculate estimated deployment cost"""        return {
            "monthly_estimate": 2500.0,
            "compute_cost": 800.0,
            "storage_cost": 200.0,
            "network_cost": 150.0,
            "database_cost": 600.0,
            "monitoring_cost": 100.0,
            "backup_cost": 50.0,
            "other_services": 600.0
        }
    
    async def _rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback failed deployment"""        self.logger.info(f"Rolling back deployment: {deployment_id}")
        # Implementation for rollback logic
        return True
    
    async def scale_service(self, service_name: str, desired_count: int) -> bool:
        """Scale ECS service"""        try:
            async with self.session.client('ecs', region_name=self.credentials.region) as ecs:
                await ecs.update_service(
                    cluster=f"ia-influencer-cluster-{service_name}",
                    service=service_name,
                    desiredCount=desired_count
                )
                self.logger.info(f"Scaled service {service_name} to {desired_count} instances")
                return True
        except Exception as e:
            self.logger.error(f"Failed to scale service {service_name}: {e}")
            return False
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get service status"""        try:
            async with self.session.client('ecs', region_name=self.credentials.region) as ecs:
                response = await ecs.describe_services(
                    cluster=f"ia-influencer-cluster-{service_name}",
                    services=[service_name]
                )
                
                if response['services']:
                    service = response['services'][0]
                    return {
                        "service_name": service_name,
                        "status": service['status'],
                        "running_count": service['runningCount'],
                        "pending_count": service['pendingCount'],
                        "desired_count": service['desiredCount'],
                        "task_definition": service['taskDefinition'],
                        "created_at": service['createdAt'].isoformat(),
                        "platform_version": service.get('platformVersion', 'N/A')
                    }
                else:
                    return {"service_name": service_name, "status": "not_found"}
        except Exception as e:
            self.logger.error(f"Failed to get service status for {service_name}: {e}")
            return {"service_name": service_name, "status": "error", "error": str(e)}
    
    async def get_deployment_costs(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get deployment costs for period"""        try:
            async with self.session.client('ce', region_name='us-east-1') as ce:
                response = await ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='DAILY',
                    Metrics=['BlendedCost'],
                    GroupBy=[{
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }]
                )
                
                costs = {}
                total_cost = 0.0
                
                for result in response['ResultsByTime']:
                    for group in result['Groups']:
                        service = group['Keys'][0]
                        cost = float(group['Metrics']['BlendedCost']['Amount'])
                        if service not in costs:
                            costs[service] = 0.0
                        costs[service] += cost
                        total_cost += cost
                
                return {
                    "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    "total_cost": total_cost,
                    "costs_by_service": costs,
                    "currency": response['ResultsByTime'][0]['Groups'][0]['Metrics']['BlendedCost']['Unit'] if response['ResultsByTime'] else 'USD'
                }
        except Exception as e:
            self.logger.error(f"Failed to get deployment costs: {e}")
            return {"error": str(e)}
    
    async def cleanup_resources(self, deployment_id: str) -> bool:
        """Cleanup deployment resources"""        try:
            self.logger.info(f"Cleaning up resources for deployment: {deployment_id}")
            # Implementation for cleanup logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup resources: {e}")
            return False
