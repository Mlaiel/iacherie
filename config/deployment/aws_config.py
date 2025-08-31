"""
AWS Configuration Module for IA-Influencer Agent Platform
=========================================================

Professional AWS cloud infrastructure configuration
for enterprise-grade AI-powered content protection and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import boto3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class AWSResourceConfig:
    """AWS resource configuration"""
    resource_type: str
    name: str
    region: str
    tags: Dict[str, str] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class AWSEC2Config:
    """AWS EC2 instance configuration"""
    instance_type: str
    ami_id: str
    key_name: str
    security_groups: List[str] = field(default_factory=list)
    subnets: List[str] = field(default_factory=list)
    user_data: str = ""
    storage_size: int = 20


@dataclass
class AWSRDSConfig:
    """AWS RDS database configuration"""
    engine: str
    engine_version: str
    instance_class: str
    allocated_storage: int
    multi_az: bool = False
    backup_retention: int = 7
    storage_encrypted: bool = True


class AWSConfig:
    """
    Professional AWS cloud configuration manager for IA-Influencer Agent Platform.
    
    Provides enterprise-grade AWS services integration:
    - EKS clusters for Kubernetes orchestration
    - RDS multi-database setup (PostgreSQL, Redis ElastiCache)
    - S3 buckets for content storage and AI models
    - ECS services for containerized microservices
    - Lambda functions for serverless AI processing
    - API Gateway for external integrations
    - CloudFront CDN for global content delivery
    - SageMaker for ML model training and inference
    - Rekognition/Transcribe for content analysis
    - CloudWatch monitoring and alerting
    """
    
    def __init__(self, environment: str = "development", region: str = "us-east-1"):
        self.environment = environment
        self.region = region
        self.project_name = "ia-influencer-agent"
        self.account_id = self._get_account_id()
        self.availability_zones = self._get_availability_zones()
        
        # Common tags
        self.default_tags = {
            "Project": "IA-Influencer-Agent",
            "Environment": environment,
            "Owner": "Fahed Mlaiel",
            "Email": "mlaiel@live.de",
            "ManagedBy": "Terraform",
            "CostCenter": "IA-Platform",
            "Compliance": "GDPR-CCPA"
        }
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""



        try:
            sts_client = boto3.client('sts', region_name=self.region)
            return sts_client.get_caller_identity()["Account"]
        except Exception:
            return "123456789012"  # Placeholder for template generation
    
    def _get_availability_zones(self) -> List[str]:
        """Get available AZs in region"""



        try:
            ec2_client = boto3.client('ec2', region_name=self.region)
            azs = ec2_client.describe_availability_zones()
            return [az['ZoneName'] for az in azs['AvailabilityZones'][:3]]
        except Exception:
            return [f"{self.region}a", f"{self.region}b", f"{self.region}c"]
    
    def get_vpc_configuration(self) -> Dict[str, Any]:
        """Generate VPC configuration"""



        return {
            "VPC": {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": "10.0.0.0/16",
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-vpc-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "InternetGateway": {
                "Type": "AWS::EC2::InternetGateway",
                "Properties": {
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-igw-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "VPCGatewayAttachment": {
                "Type": "AWS::EC2::VPCGatewayAttachment",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "InternetGatewayId": {"Ref": "InternetGateway"}
                }
            }
        }
    
    def get_subnet_configurations(self) -> Dict[str, Any]:
        """Generate subnet configurations"""
        subnets = {}
        
        # Public subnets for load balancers
        for i, az in enumerate(self.availability_zones):
            subnet_name = f"PublicSubnet{i+1}"
            subnets[subnet_name] = {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": f"10.0.{i+1}.0/24",
                    "AvailabilityZone": az,
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-public-{i+1}-{self.environment}"},
                        {"Key": "kubernetes.io/role/elb", "Value": "1"},
                        {"Key": "kubernetes.io/cluster/ia-influencer-cluster", "Value": "shared"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        
        # Private subnets for applications
        for i, az in enumerate(self.availability_zones):
            subnet_name = f"PrivateSubnet{i+1}"
            subnets[subnet_name] = {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": f"10.0.{i+10}.0/24",
                    "AvailabilityZone": az,
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-private-{i+1}-{self.environment}"},
                        {"Key": "kubernetes.io/role/internal-elb", "Value": "1"},
                        {"Key": "kubernetes.io/cluster/ia-influencer-cluster", "Value": "shared"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        
        # Database subnets
        for i, az in enumerate(self.availability_zones):
            subnet_name = f"DatabaseSubnet{i+1}"
            subnets[subnet_name] = {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": f"10.0.{i+20}.0/24",
                    "AvailabilityZone": az,
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-db-{i+1}-{self.environment}"},
                        {"Key": "Tier", "Value": "Database"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        
        return subnets
    
    def get_security_group_configurations(self) -> Dict[str, Any]:
        """Generate security group configurations"""
        security_groups = {}
        
        # API Load Balancer Security Group
        security_groups["ALBSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for Application Load Balancer",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "CidrIp": "0.0.0.0/0",
                        "Description": "HTTP from anywhere"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "CidrIp": "0.0.0.0/0",
                        "Description": "HTTPS from anywhere"
                    }
                ],
                "SecurityGroupEgress": [
                    {
                        "IpProtocol": "-1",
                        "CidrIp": "0.0.0.0/0"
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.project_name}-alb-sg-{self.environment}"},
                    *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                ]
            }
        }
        
        # EKS Cluster Security Group
        security_groups["EKSClusterSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for EKS cluster",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "SourceSecurityGroupId": {"Ref": "EKSNodeGroupSecurityGroup"},
                        "Description": "HTTPS from worker nodes"
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.project_name}-eks-cluster-sg-{self.environment}"},
                    *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                ]
            }
        }
        
        # EKS Node Group Security Group
        security_groups["EKSNodeGroupSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for EKS worker nodes",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 1025,
                        "ToPort": 65535,
                        "SourceSecurityGroupId": {"Ref": "EKSClusterSecurityGroup"},
                        "Description": "All traffic from cluster"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "SourceSecurityGroupId": {"Ref": "EKSClusterSecurityGroup"},
                        "Description": "HTTPS from cluster"
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.project_name}-eks-nodes-sg-{self.environment}"},
                    *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                ]
            }
        }
        
        # RDS Security Group
        security_groups["RDSSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for RDS databases",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5432,
                        "ToPort": 5432,
                        "SourceSecurityGroupId": {"Ref": "EKSNodeGroupSecurityGroup"},
                        "Description": "PostgreSQL from EKS nodes"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 6379,
                        "ToPort": 6379,
                        "SourceSecurityGroupId": {"Ref": "EKSNodeGroupSecurityGroup"},
                        "Description": "Redis from EKS nodes"
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.project_name}-rds-sg-{self.environment}"},
                    *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                ]
            }
        }
        
        return security_groups
    
    def get_eks_configuration(self) -> Dict[str, Any]:
        """Generate EKS cluster configuration"""



        return {
            "EKSClusterRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "eks.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "ManagedPolicyArns": [
                        "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
                    ],
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-eks-cluster-role-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "EKSCluster": {
                "Type": "AWS::EKS::Cluster",
                "Properties": {
                    "Name": f"{self.project_name}-cluster-{self.environment}",
                    "Version": "1.28",
                    "RoleArn": {"Fn::GetAtt": ["EKSClusterRole", "Arn"]},
                    "ResourcesVpcConfig": {
                        "SecurityGroupIds": [{"Ref": "EKSClusterSecurityGroup"}],
                        "SubnetIds": [
                            {"Ref": "PrivateSubnet1"},
                            {"Ref": "PrivateSubnet2"},
                            {"Ref": "PrivateSubnet3"},
                            {"Ref": "PublicSubnet1"},
                            {"Ref": "PublicSubnet2"},
                            {"Ref": "PublicSubnet3"}
                        ],
                        "EndpointConfigPrivate": True,
                        "EndpointConfigPublic": True,
                        "PublicAccessCidrs": ["0.0.0.0/0"]
                    },
                    "Logging": {
                        "ClusterLogging": {
                            "EnabledTypes": [
                                {"Type": "api"},
                                {"Type": "audit"},
                                {"Type": "authenticator"},
                                {"Type": "controllerManager"},
                                {"Type": "scheduler"}
                            ]
                        }
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-cluster-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        }
    
    def get_eks_node_group_configuration(self) -> Dict[str, Any]:
        """Generate EKS node group configuration"""



        return {
            "EKSNodeGroupRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "ec2.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "ManagedPolicyArns": [
                        "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
                        "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
                        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
                    ],
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-eks-node-role-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "EKSNodeGroup": {
                "Type": "AWS::EKS::Nodegroup",
                "Properties": {
                    "ClusterName": {"Ref": "EKSCluster"},
                    "NodeRole": {"Fn::GetAtt": ["EKSNodeGroupRole", "Arn"]},
                    "NodegroupName": f"{self.project_name}-nodes-{self.environment}",
                    "Subnets": [
                        {"Ref": "PrivateSubnet1"},
                        {"Ref": "PrivateSubnet2"},
                        {"Ref": "PrivateSubnet3"}
                    ],
                    "InstanceTypes": ["t3.large", "t3.xlarge"] if self.environment == "development" else ["m5.large", "m5.xlarge", "c5.xlarge"],
                    "AmiType": "AL2_x86_64",
                    "CapacityType": "ON_DEMAND",
                    "ScalingConfig": {
                        "MinSize": 1 if self.environment == "development" else 3,
                        "MaxSize": 5 if self.environment == "development" else 20,
                        "DesiredSize": 2 if self.environment == "development" else 6
                    },
                    "UpdateConfig": {
                        "MaxUnavailable": 1
                    },
                    "RemoteAccess": {
                        "Ec2SshKey": f"{self.project_name}-key-{self.environment}"
                    },
                    "Tags": {
                        "Name": f"{self.project_name}-node-{self.environment}",
                        **self.default_tags
                    }
                }
            },
            "EKSNodeGroupGPU": {
                "Type": "AWS::EKS::Nodegroup",
                "Properties": {
                    "ClusterName": {"Ref": "EKSCluster"},
                    "NodeRole": {"Fn::GetAtt": ["EKSNodeGroupRole", "Arn"]},
                    "NodegroupName": f"{self.project_name}-gpu-nodes-{self.environment}",
                    "Subnets": [
                        {"Ref": "PrivateSubnet1"},
                        {"Ref": "PrivateSubnet2"}
                    ],
                    "InstanceTypes": ["g4dn.xlarge"] if self.environment == "development" else ["g4dn.2xlarge", "p3.2xlarge"],
                    "AmiType": "AL2_x86_64_GPU",
                    "CapacityType": "ON_DEMAND",
                    "ScalingConfig": {
                        "MinSize": 0,
                        "MaxSize": 2 if self.environment == "development" else 5,
                        "DesiredSize": 1 if self.environment == "production" else 0
                    },
                    "Taints": [
                        {
                            "Key": "nvidia.com/gpu",
                            "Value": "true",
                            "Effect": "NO_SCHEDULE"
                        }
                    ],
                    "Tags": {
                        "Name": f"{self.project_name}-gpu-node-{self.environment}",
                        "NodeType": "GPU",
                        **self.default_tags
                    }
                }
            }
        }
    
    def get_rds_configuration(self) -> Dict[str, Any]:
        """Generate RDS configuration"""



        return {
            "DBSubnetGroup": {
                "Type": "AWS::RDS::DBSubnetGroup",
                "Properties": {
                    "DBSubnetGroupDescription": "Subnet group for RDS databases",
                    "SubnetIds": [
                        {"Ref": "DatabaseSubnet1"},
                        {"Ref": "DatabaseSubnet2"},
                        {"Ref": "DatabaseSubnet3"}
                    ],
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-db-subnet-group-{self.environment}"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "PostgreSQLDB": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "DBInstanceIdentifier": f"{self.project_name}-postgres-{self.environment}",
                    "DBInstanceClass": "db.t3.micro" if self.environment == "development" else "db.r5.large",
                    "Engine": "postgres",
                    "EngineVersion": "15.4",
                    "AllocatedStorage": 20 if self.environment == "development" else 100,
                    "StorageType": "gp2",
                    "StorageEncrypted": True,
                    "DBName": "ia_influencer",
                    "MasterUsername": "ia_admin",
                    "MasterUserPassword": "{{resolve:secretsmanager:ia-influencer-db-password:SecretString:password}}",
                    "VPCSecurityGroups": [{"Ref": "RDSSecurityGroup"}],
                    "DBSubnetGroupName": {"Ref": "DBSubnetGroup"},
                    "MultiAZ": False if self.environment == "development" else True,
                    "BackupRetentionPeriod": 7,
                    "PreferredBackupWindow": "03:00-04:00",
                    "PreferredMaintenanceWindow": "sun:04:00-sun:05:00",
                    "DeletionProtection": False if self.environment == "development" else True,
                    "EnablePerformanceInsights": True,
                    "MonitoringInterval": 60,
                    "MonitoringRoleArn": {"Fn::GetAtt": ["RDSMonitoringRole", "Arn"]},
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-postgres-{self.environment}"},
                        {"Key": "Engine", "Value": "PostgreSQL"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        }
    
    def get_elasticache_configuration(self) -> Dict[str, Any]:
        """Generate ElastiCache Redis configuration"""



        return {
            "ElastiCacheSubnetGroup": {
                "Type": "AWS::ElastiCache::SubnetGroup",
                "Properties": {
                    "Description": "Subnet group for ElastiCache Redis",
                    "SubnetIds": [
                        {"Ref": "DatabaseSubnet1"},
                        {"Ref": "DatabaseSubnet2"},
                        {"Ref": "DatabaseSubnet3"}
                    ]
                }
            },
            "ElastiCacheRedis": {
                "Type": "AWS::ElastiCache::CacheCluster",
                "Properties": {
                    "CacheClusterId": f"{self.project_name}-redis-{self.environment}",
                    "Engine": "redis",
                    "EngineVersion": "7.0",
                    "CacheNodeType": "cache.t3.micro" if self.environment == "development" else "cache.r6g.large",
                    "NumCacheNodes": 1,
                    "VpcSecurityGroupIds": [{"Ref": "RDSSecurityGroup"}],
                    "CacheSubnetGroupName": {"Ref": "ElastiCacheSubnetGroup"},
                    "TransitEncryptionEnabled": True,
                    "AtRestEncryptionEnabled": True,
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-redis-{self.environment}"},
                        {"Key": "Engine", "Value": "Redis"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        }
    
    def get_s3_configuration(self) -> Dict[str, Any]:
        """Generate S3 bucket configurations"""



        return {
            "ContentStorageBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": f"{self.project_name}-content-{self.environment}-{self.account_id}",
                    "VersioningConfiguration": {
                        "Status": "Enabled"
                    },
                    "BucketEncryption": {
                        "ServerSideEncryptionConfiguration": [
                            {
                                "ServerSideEncryptionByDefault": {
                                    "SSEAlgorithm": "AES256"
                                }
                            }
                        ]
                    },
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "BlockPublicPolicy": True,
                        "IgnorePublicAcls": True,
                        "RestrictPublicBuckets": True
                    },
                    "LifecycleConfiguration": {
                        "Rules": [
                            {
                                "Id": "TransitionToIA",
                                "Status": "Enabled",
                                "Transitions": [
                                    {
                                        "StorageClass": "STANDARD_IA",
                                        "TransitionInDays": 30
                                    },
                                    {
                                        "StorageClass": "GLACIER",
                                        "TransitionInDays": 90
                                    }
                                ]
                            }
                        ]
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-content-{self.environment}"},
                        {"Key": "Purpose", "Value": "Content Storage"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "AIModelsBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": f"{self.project_name}-models-{self.environment}-{self.account_id}",
                    "VersioningConfiguration": {
                        "Status": "Enabled"
                    },
                    "BucketEncryption": {
                        "ServerSideEncryptionConfiguration": [
                            {
                                "ServerSideEncryptionByDefault": {
                                    "SSEAlgorithm": "AES256"
                                }
                            }
                        ]
                    },
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "BlockPublicPolicy": True,
                        "IgnorePublicAcls": True,
                        "RestrictPublicBuckets": True
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-models-{self.environment}"},
                        {"Key": "Purpose", "Value": "AI Models Storage"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "BackupsBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": f"{self.project_name}-backups-{self.environment}-{self.account_id}",
                    "VersioningConfiguration": {
                        "Status": "Enabled"
                    },
                    "BucketEncryption": {
                        "ServerSideEncryptionConfiguration": [
                            {
                                "ServerSideEncryptionByDefault": {
                                    "SSEAlgorithm": "AES256"
                                }
                            }
                        ]
                    },
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "BlockPublicPolicy": True,
                        "IgnorePublicAcls": True,
                        "RestrictPublicBuckets": True
                    },
                    "LifecycleConfiguration": {
                        "Rules": [
                            {
                                "Id": "ArchiveBackups",
                                "Status": "Enabled",
                                "Transitions": [
                                    {
                                        "StorageClass": "GLACIER",
                                        "TransitionInDays": 7
                                    },
                                    {
                                        "StorageClass": "DEEP_ARCHIVE",
                                        "TransitionInDays": 30
                                    }
                                ]
                            }
                        ]
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-backups-{self.environment}"},
                        {"Key": "Purpose", "Value": "Backups Storage"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        }
    
    def get_lambda_configuration(self) -> Dict[str, Any]:
        """Generate Lambda function configurations"""



        return {
            "LambdaExecutionRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "lambda.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "ManagedPolicyArns": [
                        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                        "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
                    ],
                    "Policies": [
                        {
                            "PolicyName": "IAInfluencerLambdaPolicy",
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "s3:GetObject",
                                            "s3:PutObject",
                                            "rekognition:*",
                                            "transcribe:*",
                                            "comprehend:*"
                                        ],
                                        "Resource": "*"
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            "ContentAnalysisFunction": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "FunctionName": f"{self.project_name}-content-analysis-{self.environment}",
                    "Runtime": "python3.11",
                    "Handler": "index.handler",
                    "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                    "Code": {
                        "ZipFile": '''
import json
import boto3

def handler(event, context):
    """
    Lambda function for AI-powered content analysis
    Author: Fahed Mlaiel <mlaiel@live.de>
    """
    
    rekognition = boto3.client('rekognition')
    s3 = boto3.client('s3')
    
    # Extract bucket and key from event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    try:
        # Analyze image/video with Rekognition
        if key.lower().endswith(('.jpg', '.jpeg', '.png')):
            response = rekognition.detect_labels(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                MaxLabels=20,
                MinConfidence=80
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Content analysis completed',
                'labels': response.get('Labels', [])
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
                        '''
                    },
                    "Timeout": 300,
                    "MemorySize": 512,
                    "Environment": {
                        "Variables": {
                            "ENVIRONMENT": self.environment,
                            "PROJECT": self.project_name
                        }
                    },
                    "VpcConfig": {
                        "SecurityGroupIds": [{"Ref": "EKSNodeGroupSecurityGroup"}],
                        "SubnetIds": [
                            {"Ref": "PrivateSubnet1"},
                            {"Ref": "PrivateSubnet2"}
                        ]
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-content-analysis-{self.environment}"},
                        {"Key": "Purpose", "Value": "Content Analysis"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            }
        }
    
    def get_cloudfront_configuration(self) -> Dict[str, Any]:
        """Generate CloudFront CDN configuration"""



        return {
            "CloudFrontDistribution": {
                "Type": "AWS::CloudFront::Distribution",
                "Properties": {
                    "DistributionConfig": {
                        "Enabled": True,
                        "Comment": f"IA-Influencer Agent CDN - {self.environment}",
                        "DefaultRootObject": "index.html",
                        "Aliases": [f"cdn-{self.environment}.ia-influencer.com"] if self.environment != "development" else [],
                        "Origins": [
                            {
                                "Id": "S3-ContentStorage",
                                "DomainName": {"Fn::GetAtt": ["ContentStorageBucket", "RegionalDomainName"]},
                                "S3OriginConfig": {
                                    "OriginAccessIdentity": {"Fn::Sub": "origin-access-identity/cloudfront/${CloudFrontOriginAccessIdentity}"}
                                }
                            }
                        ],
                        "DefaultCacheBehavior": {
                            "TargetOriginId": "S3-ContentStorage",
                            "ViewerProtocolPolicy": "redirect-to-https",
                            "AllowedMethods": ["GET", "HEAD"],
                            "Compress": True,
                            "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"  # Managed caching optimized
                        },
                        "CacheBehaviors": [
                            {
                                "PathPattern": "/api/*",
                                "TargetOriginId": "ALB-API",
                                "ViewerProtocolPolicy": "https-only",
                                "AllowedMethods": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
                                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                                "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"
                            }
                        ],
                        "PriceClass": "PriceClass_100" if self.environment == "development" else "PriceClass_All",
                        "HttpVersion": "http2",
                        "IPV6Enabled": True,
                        "WebACLId": {"Ref": "WebACL"} if self.environment == "production" else {"Ref": "AWS::NoValue"}
                    },
                    "Tags": [
                        {"Key": "Name", "Value": f"{self.project_name}-cdn-{self.environment}"},
                        {"Key": "Purpose", "Value": "Content Delivery"},
                        *[{"Key": k, "Value": v} for k, v in self.default_tags.items()]
                    ]
                }
            },
            "CloudFrontOriginAccessIdentity": {
                "Type": "AWS::CloudFront::OriginAccessIdentity",
                "Properties": {
                    "OriginAccessIdentityConfig": {
                        "Comment": f"OAI for IA-Influencer {self.environment}"
                    }
                }
            }
        }
    
    def generate_cloudformation_template(self, output_file: str = "aws-infrastructure.yaml") -> None:
        """Generate complete CloudFormation template"""
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"IA-Influencer Agent Platform Infrastructure - {self.environment} Environment",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": self.environment,
                    "Description": "Environment name"
                },
                "KeyPairName": {
                    "Type": "AWS::EC2::KeyPair::KeyName",
                    "Description": "EC2 Key Pair for SSH access"
                }
            },
            "Resources": {}
        }
        
        # Add all resource configurations
        template["Resources"].update(self.get_vpc_configuration())
        template["Resources"].update(self.get_subnet_configurations())
        template["Resources"].update(self.get_security_group_configurations())
        template["Resources"].update(self.get_eks_configuration())
        template["Resources"].update(self.get_eks_node_group_configuration())
        template["Resources"].update(self.get_rds_configuration())
        template["Resources"].update(self.get_elasticache_configuration())
        template["Resources"].update(self.get_s3_configuration())
        template["Resources"].update(self.get_lambda_configuration())
        template["Resources"].update(self.get_cloudfront_configuration())
        
        # Add outputs
        template["Outputs"] = {
            "EKSClusterName": {
                "Description": "EKS Cluster Name",
                "Value": {"Ref": "EKSCluster"},
                "Export": {"Name": f"{self.project_name}-eks-cluster-{self.environment}"}
            },
            "PostgreSQLEndpoint": {
                "Description": "PostgreSQL Database Endpoint",
                "Value": {"Fn::GetAtt": ["PostgreSQLDB", "Endpoint.Address"]},
                "Export": {"Name": f"{self.project_name}-postgres-endpoint-{self.environment}"}
            },
            "RedisEndpoint": {
                "Description": "Redis Cache Endpoint",
                "Value": {"Fn::GetAtt": ["ElastiCacheRedis", "RedisEndpoint.Address"]},
                "Export": {"Name": f"{self.project_name}-redis-endpoint-{self.environment}"}
            },
            "ContentStorageBucketName": {
                "Description": "S3 Content Storage Bucket",
                "Value": {"Ref": "ContentStorageBucket"},
                "Export": {"Name": f"{self.project_name}-content-bucket-{self.environment}"}
            },
            "CloudFrontDistributionDomainName": {
                "Description": "CloudFront Distribution Domain Name",
                "Value": {"Fn::GetAtt": ["CloudFrontDistribution", "DomainName"]},
                "Export": {"Name": f"{self.project_name}-cdn-domain-{self.environment}"}
            }
        }
        
        # Write template to file
        with open(output_file, 'w') as f:
            f.write(f"# AWS CloudFormation Template for IA-Influencer Agent Platform\n")
            f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n")
            f.write(f"# Environment: {self.environment}\n")
            f.write(f"# Generated automatically - DO NOT EDIT MANUALLY\n\n")
            import yaml
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
    
    def get_deployment_script(self) -> str:
        """Generate AWS deployment script"""



        return f'''#!/bin/bash
# AWS deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"
REGION="{self.region}"
STACK_NAME="ia-influencer-agent-$ENVIRONMENT"
TEMPLATE_FILE="aws-infrastructure.yaml"

echo " Deploying IA-Influencer Agent to AWS..."
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Stack: $STACK_NAME"

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo " AWS CLI is not installed"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo " AWS credentials not configured"
    exit 1
fi

# Validate CloudFormation template
echo " Validating CloudFormation template..."
aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION

# Deploy stack
echo " Deploying CloudFormation stack..."
aws cloudformation deploy \\
    --template-file $TEMPLATE_FILE \\
    --stack-name $STACK_NAME \\
    --parameter-overrides \\
        Environment=$ENVIRONMENT \\
        KeyPairName=ia-influencer-key-$ENVIRONMENT \\
    --capabilities CAPABILITY_IAM \\
    --region $REGION \\
    --tags \\
        Project=IA-Influencer-Agent \\
        Environment=$ENVIRONMENT \\
        Owner="Fahed Mlaiel" \\
        Email=mlaiel@live.de

# Get stack outputs
echo " Getting stack outputs..."
aws cloudformation describe-stacks \\
    --stack-name $STACK_NAME \\
    --region $REGION \\
    --query 'Stacks[0].Outputs'

# Configure kubectl for EKS
echo " Configuring kubectl for EKS..."
aws eks update-kubeconfig \\
    --region $REGION \\
    --name ia-influencer-agent-cluster-$ENVIRONMENT

# Verify EKS connection
echo " Verifying EKS connection..."
kubectl get nodes

echo " AWS infrastructure deployed successfully!"
echo " Next steps:"
echo "1. Deploy Kubernetes manifests: kubectl apply -f k8s-manifests/"
echo "2. Configure DNS: Update Route53 records"
echo "3. Setup monitoring: Deploy Prometheus/Grafana"
echo "4. Configure CI/CD: Setup GitHub Actions with AWS"
'''
