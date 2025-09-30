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
Object Storage Manager

This module provides enterprise-grade object storage management capabilities
for the Ainflue platform infrastructure.

Features:
    - S3-compatible object storage management
    - Multi-cloud storage abstraction
    - Content delivery integration
    - Storage lifecycle management
    - Encryption and security
    - Backup and versioning
"""

import logging
import boto3
import json
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StorageClass(Enum):
    """Storage classes for lifecycle management."""
    STANDARD = "STANDARD"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    GLACIER = "GLACIER"
    GLACIER_IR = "GLACIER_IR"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"

class ServerSideEncryption(Enum):
    """Server-side encryption options."""
    NONE = "NONE"
    AES256 = "AES256"
    KMS = "aws:kms"
    KMS_DSSE = "aws:kms:dsse"

@dataclass
class BucketConfig:
    """S3 bucket configuration."""
    name: str
    region: str
    versioning: bool = True
    encryption: ServerSideEncryption = ServerSideEncryption.AES256
    kms_key_id: Optional[str] = None
    lifecycle_enabled: bool = True
    logging_enabled: bool = True
    public_access_block: bool = True
    cors_enabled: bool = False
    website_hosting: bool = False

@dataclass
class LifecycleRule:
    """Storage lifecycle rule configuration."""
    id: str
    enabled: bool = True
    prefix: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    transitions: List[Dict[str, Union[int, str]]] = None
    expiration_days: Optional[int] = None
    noncurrent_version_expiration_days: Optional[int] = None
    abort_incomplete_multipart_upload_days: Optional[int] = 7

class ObjectStorageManager:
    """
    Enterprise object storage management for scalable content storage.
    
    Provides comprehensive S3-compatible storage management with lifecycle
    policies, encryption, versioning, and multi-cloud abstraction.
    """
    
    def __init__(self, region: str = "us-west-2"):
        """
        Initialize object storage manager.
        
        Args:
            region: AWS region for storage resources
        """
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
        self.s3_resource = boto3.resource('s3', region_name=region)
        
    def create_bucket(self, config: BucketConfig,
                     tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create S3 bucket with enterprise configuration.
        
        Args:
            config: Bucket configuration
            tags: Resource tags
            
        Returns:
            Dict: Bucket creation result
        """
        try:
            # Create bucket
            if config.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=config.name)
            else:
                self.s3_client.create_bucket(
                    Bucket=config.name,
                    CreateBucketConfiguration={
                        'LocationConstraint': config.region
                    }
                )
            
            # Configure versioning
            if config.versioning:
                self.s3_client.put_bucket_versioning(
                    Bucket=config.name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            
            # Configure encryption
            if config.encryption != ServerSideEncryption.NONE:
                encryption_config = {
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': config.encryption.value
                        }
                    }]
                }
                
                if config.encryption in [ServerSideEncryption.KMS, ServerSideEncryption.KMS_DSSE]:
                    if config.kms_key_id:
                        encryption_config['Rules'][0]['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID'] = config.kms_key_id
                
                self.s3_client.put_bucket_encryption(
                    Bucket=config.name,
                    ServerSideEncryptionConfiguration=encryption_config
                )
            
            # Configure public access block
            if config.public_access_block:
                self.s3_client.put_public_access_block(
                    Bucket=config.name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
            
            # Configure bucket policy for secure access
            self._apply_secure_bucket_policy(config.name)
            
            # Configure access logging
            if config.logging_enabled:
                self._configure_access_logging(config.name)
            
            # Configure CORS if enabled
            if config.cors_enabled:
                self._configure_cors(config.name)
            
            # Configure website hosting if enabled
            if config.website_hosting:
                self._configure_website_hosting(config.name)
            
            # Apply tags
            if tags:
                self._apply_bucket_tags(config.name, tags)
            
            logger.info(f"Created S3 bucket: {config.name}")
            
            return {
                'bucket_name': config.name,
                'region': config.region,
                'arn': f"arn:aws:s3:::{config.name}",
                'domain_name': f"{config.name}.s3.{config.region}.amazonaws.com",
                'website_endpoint': f"{config.name}.s3-website-{config.region}.amazonaws.com" if config.website_hosting else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create bucket {config.name}: {str(e)}")
            raise
    
    def configure_lifecycle_policy(self, bucket_name: str,
                                 rules: List[LifecycleRule]) -> bool:
        """
        Configure bucket lifecycle policy.
        
        Args:
            bucket_name: S3 bucket name
            rules: List of lifecycle rules
            
        Returns:
            bool: True if successful
        """
        try:
            lifecycle_rules = []
            
            for rule in rules:
                lifecycle_rule = {
                    'ID': rule.id,
                    'Status': 'Enabled' if rule.enabled else 'Disabled'
                }
                
                # Configure filter
                filter_config = {}
                if rule.prefix:
                    filter_config['Prefix'] = rule.prefix
                if rule.tags:
                    if 'Prefix' in filter_config:
                        filter_config = {
                            'And': {
                                'Prefix': rule.prefix,
                                'Tags': [{'Key': k, 'Value': v} for k, v in rule.tags.items()]
                            }
                        }
                    else:
                        filter_config['Tags'] = [{'Key': k, 'Value': v} for k, v in rule.tags.items()]
                
                if filter_config:
                    lifecycle_rule['Filter'] = filter_config
                
                # Configure transitions
                if rule.transitions:
                    lifecycle_rule['Transitions'] = []
                    for transition in rule.transitions:
                        lifecycle_rule['Transitions'].append({
                            'Days': transition['days'],
                            'StorageClass': transition['storage_class']
                        })
                
                # Configure expiration
                if rule.expiration_days:
                    lifecycle_rule['Expiration'] = {'Days': rule.expiration_days}
                
                # Configure noncurrent version expiration
                if rule.noncurrent_version_expiration_days:
                    lifecycle_rule['NoncurrentVersionExpiration'] = {
                        'NoncurrentDays': rule.noncurrent_version_expiration_days
                    }
                
                # Configure incomplete multipart upload cleanup
                if rule.abort_incomplete_multipart_upload_days:
                    lifecycle_rule['AbortIncompleteMultipartUpload'] = {
                        'DaysAfterInitiation': rule.abort_incomplete_multipart_upload_days
                    }
                
                lifecycle_rules.append(lifecycle_rule)
            
            # Apply lifecycle configuration
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={'Rules': lifecycle_rules}
            )
            
            logger.info(f"Configured lifecycle policy for bucket: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure lifecycle policy: {str(e)}")
            return False
    
    def setup_cross_region_replication(self, source_bucket: str,
                                     destination_bucket: str,
                                     destination_region: str,
                                     role_arn: str,
                                     prefix: Optional[str] = None) -> bool:
        """
        Set up cross-region replication for disaster recovery.
        
        Args:
            source_bucket: Source bucket name
            destination_bucket: Destination bucket name
            destination_region: Destination region
            role_arn: IAM role ARN for replication
            prefix: Object prefix filter
            
        Returns:
            bool: True if successful
        """
        try:
            replication_config = {
                'Role': role_arn,
                'Rules': [{
                    'ID': 'ReplicateAll',
                    'Status': 'Enabled',
                    'Priority': 1,
                    'Destination': {
                        'Bucket': f"arn:aws:s3:::{destination_bucket}",
                        'StorageClass': StorageClass.STANDARD.value
                    }
                }]
            }
            
            # Add prefix filter if specified
            if prefix:
                replication_config['Rules'][0]['Filter'] = {'Prefix': prefix}
            
            # Apply replication configuration
            self.s3_client.put_bucket_replication(
                Bucket=source_bucket,
                ReplicationConfiguration=replication_config
            )
            
            logger.info(f"Configured cross-region replication from {source_bucket} to {destination_bucket}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure replication: {str(e)}")
            return False
    
    def create_cloudfront_distribution(self, bucket_name: str,
                                     domain_name: Optional[str] = None,
                                     certificate_arn: Optional[str] = None,
                                     price_class: str = "PriceClass_100") -> Dict[str, Any]:
        """
        Create CloudFront distribution for global content delivery.
        
        Args:
            bucket_name: S3 bucket name
            domain_name: Custom domain name
            certificate_arn: SSL certificate ARN
            price_class: CloudFront price class
            
        Returns:
            Dict: CloudFront distribution details
        """
        try:
            cloudfront = boto3.client('cloudfront')
            
            # Generate caller reference
            caller_reference = f"{bucket_name}-{int(datetime.now().timestamp())}"
            
            # Configure origin
            origin_domain = f"{bucket_name}.s3.{self.region}.amazonaws.com"
            
            # Distribution configuration
            distribution_config = {
                'CallerReference': caller_reference,
                'Comment': f'CDN for {bucket_name}',
                'Enabled': True,
                'PriceClass': price_class,
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': f"{bucket_name}-origin",
                        'DomainName': origin_domain,
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''
                        }
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': f"{bucket_name}-origin",
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 86400,
                    'MaxTTL': 31536000,
                    'Compress': True
                }
            }
            
            # Add custom domain and SSL certificate
            if domain_name and certificate_arn:
                distribution_config['Aliases'] = {
                    'Quantity': 1,
                    'Items': [domain_name]
                }
                distribution_config['ViewerCertificate'] = {
                    'ACMCertificateArn': certificate_arn,
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.2_2021'
                }
            else:
                distribution_config['ViewerCertificate'] = {
                    'CloudFrontDefaultCertificate': True
                }
            
            # Create distribution
            response = cloudfront.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution = response['Distribution']
            
            logger.info(f"Created CloudFront distribution for bucket: {bucket_name}")
            
            return {
                'distribution_id': distribution['Id'],
                'domain_name': distribution['DomainName'],
                'arn': distribution['ARN'],
                'status': distribution['Status']
            }
            
        except Exception as e:
            logger.error(f"Failed to create CloudFront distribution: {str(e)}")
            raise
    
    def upload_object(self, bucket_name: str, key: str, data: Union[bytes, str],
                     content_type: Optional[str] = None,
                     metadata: Optional[Dict[str, str]] = None,
                     tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload object to S3 bucket.
        
        Args:
            bucket_name: S3 bucket name
            key: Object key
            data: Object data
            content_type: MIME content type
            metadata: Object metadata
            tags: Object tags
            
        Returns:
            Dict: Upload result
        """
        try:
            extra_args = {}
            
            if content_type:
                extra_args['ContentType'] = content_type
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            if tags:
                tag_set = [f"{k}={v}" for k, v in tags.items()]
                extra_args['Tagging'] = "&".join(tag_set)
            
            # Upload object
            if isinstance(data, str):
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=data.encode('utf-8'),
                    **extra_args
                )
            else:
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=data,
                    **extra_args
                )
            
            # Get object info
            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)
            
            logger.info(f"Uploaded object: s3://{bucket_name}/{key}")
            
            return {
                'bucket': bucket_name,
                'key': key,
                'etag': response['ETag'],
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'url': f"https://{bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            }
            
        except Exception as e:
            logger.error(f"Failed to upload object: {str(e)}")
            raise
    
    def generate_presigned_url(self, bucket_name: str, key: str,
                             expiration: int = 3600,
                             http_method: str = 'GET') -> str:
        """
        Generate presigned URL for temporary access.
        
        Args:
            bucket_name: S3 bucket name
            key: Object key
            expiration: URL expiration in seconds
            http_method: HTTP method (GET, PUT, POST, DELETE)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                http_method.lower() + '_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def _apply_secure_bucket_policy(self, bucket_name: str) -> None:
        """Apply secure bucket policy to enforce HTTPS."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DenyInsecureConnections",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
        
        self.s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
    
    def _configure_access_logging(self, bucket_name: str) -> None:
        """Configure access logging for the bucket."""
        logging_bucket = f"{bucket_name}-access-logs"
        
        try:
            # Create logging bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=logging_bucket)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=logging_bucket)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=logging_bucket,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
            
            # Configure logging
            self.s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': logging_bucket,
                        'TargetPrefix': f"{bucket_name}/access-logs/"
                    }
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to configure access logging: {str(e)}")
    
    def _configure_cors(self, bucket_name: str) -> None:
        """Configure CORS for web access."""
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3600
            }]
        }
        
        self.s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
    
    def _configure_website_hosting(self, bucket_name: str) -> None:
        """Configure static website hosting."""
        website_config = {
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'error.html'}
        }
        
        self.s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration=website_config
        )
    
    def _apply_bucket_tags(self, bucket_name: str, tags: Dict[str, str]) -> None:
        """Apply tags to bucket."""
        tag_set = [{'Key': key, 'Value': value} for key, value in tags.items()]
        
        self.s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': tag_set}
        )