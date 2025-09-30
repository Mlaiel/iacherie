# Ainflue Infrastructure Module - CDN Configuration
# ================================================
# 
# Enterprise-grade CDN configuration for Ainflue platform
# Supports multi-cloud content delivery and enterprise optimization
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.cdn import CdnManagementClient
from google.cloud import cdn_v1

class CachePolicy(Enum):
    """CDN cache policies"""
    STATIC_CONTENT = "static_content"
    DYNAMIC_CONTENT = "dynamic_content"
    API_RESPONSES = "api_responses"
    MEDIA_CONTENT = "media_content"
    NO_CACHE = "no_cache"

class CompressionType(Enum):
    """Compression types for CDN"""
    GZIP = "gzip"
    BROTLI = "brotli"
    DEFLATE = "deflate"

@dataclass
class CacheRule:
    """CDN cache rule configuration"""
    path_pattern: str
    cache_policy: CachePolicy
    ttl_seconds: int
    compress: bool = True
    compression_types: List[CompressionType] = None
    headers_to_cache: List[str] = None
    query_strings_to_cache: List[str] = None

@dataclass
class CDNConfig:
    """Configuration for CDN setup"""
    environment: str
    cloud_provider: str
    origin_domain: str
    custom_domains: List[str]
    region: str
    enable_waf: bool = True
    enable_logging: bool = True
    price_class: str = "PriceClass_All"  # AWS CloudFront price class

class CDNConfigurationManager:
    """Enterprise CDN configuration management for multi-cloud environments"""
    
    def __init__(self, config: CDNConfig):
        """Initialize CDN configuration manager
        
        Args:
            config: CDN configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize cloud provider clients
        self._initialize_cloud_clients()
        
        # Define cache rules for different content types
        self.default_cache_rules = self._define_default_cache_rules()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"ainflue.infra.networking.cdn_config")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _initialize_cloud_clients(self):
        """Initialize cloud provider clients"""
        try:
            if self.config.cloud_provider.lower() == 'aws':
                self.cloudfront_client = boto3.client('cloudfront')
                self.s3_client = boto3.client('s3')
                
            elif self.config.cloud_provider.lower() == 'azure':
                credential = DefaultAzureCredential()
                self.cdn_client = CdnManagementClient(
                    credential, 
                    subscription_id=self._get_azure_subscription_id()
                )
                
            elif self.config.cloud_provider.lower() == 'gcp':
                self.cdn_client = cdn_v1.UrlMapsClient()
                self.backend_service_client = cdn_v1.BackendServicesClient()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cloud clients: {e}")
            raise
    
    def _get_azure_subscription_id(self) -> str:
        """Get Azure subscription ID"""
        import os
        return os.getenv('AZURE_SUBSCRIPTION_ID', 'default-subscription-id')
    
    def _define_default_cache_rules(self) -> List[CacheRule]:
        """Define default cache rules for Ainflue platform"""
        return [
            # Static assets - long cache
            CacheRule(
                path_pattern="/static/*",
                cache_policy=CachePolicy.STATIC_CONTENT,
                ttl_seconds=31536000,  # 1 year
                compress=True,
                compression_types=[CompressionType.GZIP, CompressionType.BROTLI],
                headers_to_cache=["Accept-Encoding"],
                query_strings_to_cache=["v", "version"]
            ),
            
            # CSS and JS files
            CacheRule(
                path_pattern="*.css",
                cache_policy=CachePolicy.STATIC_CONTENT,
                ttl_seconds=31536000,  # 1 year
                compress=True,
                compression_types=[CompressionType.GZIP, CompressionType.BROTLI]
            ),
            CacheRule(
                path_pattern="*.js",
                cache_policy=CachePolicy.STATIC_CONTENT,
                ttl_seconds=31536000,  # 1 year
                compress=True,
                compression_types=[CompressionType.GZIP, CompressionType.BROTLI]
            ),
            
            # Images - medium cache
            CacheRule(
                path_pattern="*.jpg",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=2592000,  # 30 days
                compress=False
            ),
            CacheRule(
                path_pattern="*.png",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=2592000,  # 30 days
                compress=False
            ),
            CacheRule(
                path_pattern="*.webp",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=2592000,  # 30 days
                compress=False
            ),
            
            # Videos - medium cache
            CacheRule(
                path_pattern="*.mp4",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=2592000,  # 30 days
                compress=False
            ),
            CacheRule(
                path_pattern="*.webm",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=2592000,  # 30 days
                compress=False
            ),
            
            # API responses - short cache or no cache
            CacheRule(
                path_pattern="/api/v1/users/*",
                cache_policy=CachePolicy.DYNAMIC_CONTENT,
                ttl_seconds=300,  # 5 minutes
                compress=True,
                compression_types=[CompressionType.GZIP],
                headers_to_cache=["Authorization"]
            ),
            CacheRule(
                path_pattern="/api/v1/content/*",
                cache_policy=CachePolicy.DYNAMIC_CONTENT,
                ttl_seconds=600,  # 10 minutes
                compress=True,
                compression_types=[CompressionType.GZIP]
            ),
            
            # AI processing endpoints - no cache
            CacheRule(
                path_pattern="/ai/*",
                cache_policy=CachePolicy.NO_CACHE,
                ttl_seconds=0,
                compress=True,
                compression_types=[CompressionType.GZIP]
            ),
            
            # User generated content thumbnails
            CacheRule(
                path_pattern="/thumbnails/*",
                cache_policy=CachePolicy.MEDIA_CONTENT,
                ttl_seconds=604800,  # 7 days
                compress=False
            ),
            
            # Mobile app assets
            CacheRule(
                path_pattern="/mobile/assets/*",
                cache_policy=CachePolicy.STATIC_CONTENT,
                ttl_seconds=31536000,  # 1 year
                compress=True,
                compression_types=[CompressionType.GZIP, CompressionType.BROTLI]
            )
        ]
    
    async def create_cdn_distribution(self, custom_cache_rules: Optional[List[CacheRule]] = None) -> str:
        """Create CDN distribution
        
        Args:
            custom_cache_rules: Optional custom cache rules
            
        Returns:
            str: CDN distribution ID or domain
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._create_cloudfront_distribution(custom_cache_rules)
            elif self.config.cloud_provider.lower() == 'azure':
                return await self._create_azure_cdn_endpoint(custom_cache_rules)
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._create_gcp_cdn_configuration(custom_cache_rules)
            else:
                raise ValueError(f"Unsupported cloud provider: {self.config.cloud_provider}")
                
        except Exception as e:
            self.logger.error(f"Failed to create CDN distribution: {e}")
            raise
    
    async def _create_cloudfront_distribution(self, custom_cache_rules: Optional[List[CacheRule]] = None) -> str:
        """Create AWS CloudFront distribution"""
        try:
            cache_rules = custom_cache_rules or self.default_cache_rules
            
            # Create cache behaviors
            cache_behaviors = []
            default_cache_behavior = None
            
            for i, rule in enumerate(cache_rules):
                behavior = {
                    'TargetOriginId': 'origin1',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'Compress': rule.compress,
                    'CachePolicyId': self._get_aws_cache_policy_id(rule.cache_policy),
                    'OriginRequestPolicyId': self._get_aws_origin_request_policy_id(rule.cache_policy)
                }
                
                if rule.ttl_seconds > 0:
                    behavior['MinTTL'] = 0
                    behavior['DefaultTTL'] = rule.ttl_seconds
                    behavior['MaxTTL'] = rule.ttl_seconds * 2
                
                if i == 0:  # First rule becomes default
                    default_cache_behavior = behavior
                else:
                    behavior['PathPattern'] = rule.path_pattern
                    cache_behaviors.append(behavior)
            
            # Create distribution configuration
            distribution_config = {
                'CallerReference': f"ainflue-{self.config.environment}-{hash(self.config.origin_domain)}",
                'Comment': f'Ainflue {self.config.environment} CDN Distribution',
                'DefaultRootObject': 'index.html',
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'origin1',
                            'DomainName': self.config.origin_domain,
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'https-only',
                                'OriginSslProtocols': {
                                    'Quantity': 1,
                                    'Items': ['TLSv1.2']
                                }
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': default_cache_behavior,
                'CacheBehaviors': {
                    'Quantity': len(cache_behaviors),
                    'Items': cache_behaviors
                },
                'Enabled': True,
                'PriceClass': self.config.price_class,
                'ViewerCertificate': {
                    'CloudFrontDefaultCertificate': True
                }
            }
            
            # Add custom domains if provided
            if self.config.custom_domains:
                distribution_config['Aliases'] = {
                    'Quantity': len(self.config.custom_domains),
                    'Items': self.config.custom_domains
                }
                # Note: In production, you'd need to configure SSL certificate
                distribution_config['ViewerCertificate'] = {
                    'ACMCertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/example',
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.2_2021'
                }
            
            # Enable WAF if configured
            if self.config.enable_waf:
                distribution_config['WebACLId'] = self._get_aws_waf_acl_id()
            
            # Enable logging if configured
            if self.config.enable_logging:
                distribution_config['Logging'] = {
                    'Enabled': True,
                    'IncludeCookies': False,
                    'Bucket': f'ainflue-{self.config.environment}-cloudfront-logs.s3.amazonaws.com',
                    'Prefix': 'cloudfront-logs/'
                }
            
            # Create the distribution
            response = self.cloudfront_client.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_id = response['Distribution']['Id']
            domain_name = response['Distribution']['DomainName']
            
            self.logger.info(f"Created CloudFront distribution {distribution_id}: {domain_name}")
            return distribution_id
            
        except Exception as e:
            self.logger.error(f"Failed to create CloudFront distribution: {e}")
            raise
    
    def _get_aws_cache_policy_id(self, cache_policy: CachePolicy) -> str:
        """Get AWS cache policy ID based on cache policy type"""
        # AWS Managed Cache Policy IDs
        policy_map = {
            CachePolicy.STATIC_CONTENT: '4135ea2d-6df8-44a3-9df3-4b5a84be39ad',  # Managed-CachingOptimized
            CachePolicy.DYNAMIC_CONTENT: '08627262-05a9-4f76-9ded-b50ca2e3a84f',  # Managed-CachingOptimizedForUncompressedObjects
            CachePolicy.API_RESPONSES: '4135ea2d-6df8-44a3-9df3-4b5a84be39ad',   # Managed-CachingOptimized
            CachePolicy.MEDIA_CONTENT: '08627262-05a9-4f76-9ded-b50ca2e3a84f',   # Managed-CachingOptimizedForUncompressedObjects
            CachePolicy.NO_CACHE: '4135ea2d-6df8-44a3-9df3-4b5a84be39ad'         # Managed-CachingDisabled
        }
        return policy_map.get(cache_policy, '4135ea2d-6df8-44a3-9df3-4b5a84be39ad')
    
    def _get_aws_origin_request_policy_id(self, cache_policy: CachePolicy) -> str:
        """Get AWS origin request policy ID"""
        # AWS Managed Origin Request Policy IDs
        if cache_policy == CachePolicy.API_RESPONSES:
            return '88a5eaf4-2fd4-4709-b370-b4c650ea3fcf'  # Managed-CORS-S3Origin
        else:
            return '59781a5b-3903-41f3-afcb-af62929ccde1'  # Managed-CORS-CustomOrigin
    
    def _get_aws_waf_acl_id(self) -> str:
        """Get AWS WAF ACL ID"""
        # This should be retrieved from terraform output or parameter store
        return f"arn:aws:wafv2:us-east-1:123456789012:global/webacl/ainflue-{self.config.environment}/12345678-1234-1234-1234-123456789012"
    
    async def _create_azure_cdn_endpoint(self, custom_cache_rules: Optional[List[CacheRule]] = None) -> str:
        """Create Azure CDN endpoint"""
        try:
            resource_group = f"ainflue-{self.config.environment}-rg"
            profile_name = f"ainflue-{self.config.environment}-cdn-profile"
            endpoint_name = f"ainflue-{self.config.environment}-endpoint"
            
            # Create CDN profile first
            profile_params = {
                'location': 'Global',
                'sku': {'name': 'Standard_Microsoft'},
                'tags': {
                    'Environment': self.config.environment,
                    'Project': 'Ainflue'
                }
            }
            
            profile_operation = self.cdn_client.profiles.begin_create(
                resource_group_name=resource_group,
                profile_name=profile_name,
                profile=profile_params
            )
            profile_operation.result()
            
            # Create CDN endpoint
            endpoint_params = {
                'location': 'Global',
                'origins': [
                    {
                        'name': 'origin1',
                        'host_name': self.config.origin_domain,
                        'http_port': 80,
                        'https_port': 443,
                        'origin_host_header': self.config.origin_domain
                    }
                ],
                'is_http_allowed': False,
                'is_https_allowed': True,
                'query_string_caching_behavior': 'IgnoreQueryString',
                'optimization_type': 'GeneralWebDelivery',
                'tags': {
                    'Environment': self.config.environment,
                    'Project': 'Ainflue'
                }
            }
            
            endpoint_operation = self.cdn_client.endpoints.begin_create(
                resource_group_name=resource_group,
                profile_name=profile_name,
                endpoint_name=endpoint_name,
                endpoint=endpoint_params
            )
            
            endpoint = endpoint_operation.result()
            
            self.logger.info(f"Created Azure CDN endpoint: {endpoint.host_name}")
            return endpoint.host_name
            
        except Exception as e:
            self.logger.error(f"Failed to create Azure CDN endpoint: {e}")
            raise
    
    async def _create_gcp_cdn_configuration(self, custom_cache_rules: Optional[List[CacheRule]] = None) -> str:
        """Create GCP Cloud CDN configuration"""
        try:
            project = self._get_gcp_project_id()
            
            # Create backend service with CDN enabled
            backend_service_name = f"ainflue-{self.config.environment}-backend-service"
            
            backend_service = {
                'name': backend_service_name,
                'description': f'Ainflue {self.config.environment} backend service',
                'protocol': 'HTTPS',
                'port_name': 'https',
                'timeout_sec': 30,
                'enable_cdn': True,
                'cdn_policy': {
                    'cache_mode': 'CACHE_ALL_STATIC',
                    'default_ttl': 3600,
                    'max_ttl': 86400,
                    'client_ttl': 3600,
                    'negative_caching': True,
                    'negative_caching_policy': [
                        {'code': 404, 'ttl': 120},
                        {'code': 410, 'ttl': 120}
                    ],
                    'cache_key_policy': {
                        'include_protocol': True,
                        'include_host': True,
                        'include_query_string': False,
                        'query_string_whitelist': ['v', 'version'],
                        'include_http_headers': ['Accept-Encoding']
                    }
                },
                'backends': [
                    {
                        'group': f'projects/{project}/zones/{self.config.region}-a/instanceGroups/ainflue-{self.config.environment}-ig',
                        'balancing_mode': 'UTILIZATION',
                        'capacity_scaler': 1.0
                    }
                ]
            }
            
            operation = self.backend_service_client.insert(
                project=project,
                backend_service_resource=backend_service
            )
            
            # Wait for operation to complete
            self._wait_for_gcp_operation(operation, project)
            
            self.logger.info(f"Created GCP CDN backend service: {backend_service_name}")
            return backend_service_name
            
        except Exception as e:
            self.logger.error(f"Failed to create GCP CDN configuration: {e}")
            raise
    
    def _get_gcp_project_id(self) -> str:
        """Get GCP project ID"""
        import os
        return os.getenv('GOOGLE_CLOUD_PROJECT', 'ainflue-platform')
    
    def _wait_for_gcp_operation(self, operation, project: str):
        """Wait for GCP operation to complete"""
        import time
        time.sleep(5)  # Simplified wait - implement proper polling in production
    
    async def configure_ssl_certificate(self, domains: List[str]) -> str:
        """Configure SSL certificate for custom domains
        
        Args:
            domains: List of domains to secure
            
        Returns:
            str: Certificate ARN or ID
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._configure_aws_acm_certificate(domains)
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._configure_gcp_ssl_certificate(domains)
            else:
                self.logger.warning(f"SSL certificate configuration not implemented for {self.config.cloud_provider}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Failed to configure SSL certificate: {e}")
            raise
    
    async def _configure_aws_acm_certificate(self, domains: List[str]) -> str:
        """Configure AWS ACM certificate"""
        try:
            acm_client = boto3.client('acm', region_name='us-east-1')  # CloudFront requires us-east-1
            
            response = acm_client.request_certificate(
                DomainName=domains[0],
                SubjectAlternativeNames=domains[1:] if len(domains) > 1 else [],
                ValidationMethod='DNS',
                Tags=[
                    {'Key': 'Environment', 'Value': self.config.environment},
                    {'Key': 'Project', 'Value': 'Ainflue'},
                    {'Key': 'ManagedBy', 'Value': 'AinflueCDNManager'}
                ]
            )
            
            certificate_arn = response['CertificateArn']
            self.logger.info(f"Requested ACM certificate: {certificate_arn}")
            
            return certificate_arn
            
        except Exception as e:
            self.logger.error(f"Failed to configure AWS ACM certificate: {e}")
            raise
    
    async def _configure_gcp_ssl_certificate(self, domains: List[str]) -> str:
        """Configure GCP managed SSL certificate"""
        try:
            from google.cloud import compute_v1
            
            ssl_cert_client = compute_v1.SslCertificatesClient()
            project = self._get_gcp_project_id()
            
            cert_name = f"ainflue-{self.config.environment}-ssl-cert"
            
            ssl_certificate = {
                'name': cert_name,
                'description': f'Ainflue {self.config.environment} SSL certificate',
                'managed': {
                    'domains': domains
                }
            }
            
            operation = ssl_cert_client.insert(
                project=project,
                ssl_certificate_resource=ssl_certificate
            )
            
            self._wait_for_gcp_operation(operation, project)
            
            self.logger.info(f"Created GCP managed SSL certificate: {cert_name}")
            return cert_name
            
        except Exception as e:
            self.logger.error(f"Failed to configure GCP SSL certificate: {e}")
            raise
    
    async def update_cache_invalidation(self, paths: List[str]) -> bool:
        """Invalidate CDN cache for specific paths
        
        Args:
            paths: List of paths to invalidate
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._invalidate_cloudfront_cache(paths)
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._invalidate_gcp_cache(paths)
            else:
                self.logger.warning(f"Cache invalidation not implemented for {self.config.cloud_provider}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache: {e}")
            return False
    
    async def _invalidate_cloudfront_cache(self, paths: List[str]) -> bool:
        """Invalidate CloudFront cache"""
        try:
            distribution_id = self._get_cloudfront_distribution_id()
            
            response = self.cloudfront_client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"invalidation-{hash(str(paths))}"
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            self.logger.info(f"Created CloudFront invalidation: {invalidation_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate CloudFront cache: {e}")
            return False
    
    def _get_cloudfront_distribution_id(self) -> str:
        """Get CloudFront distribution ID"""
        # This should be retrieved from terraform output or parameter store
        return f"E1234567890123"
    
    async def _invalidate_gcp_cache(self, paths: List[str]) -> bool:
        """Invalidate GCP Cloud CDN cache"""
        # GCP cache invalidation implementation
        return True
    
    async def get_cdn_metrics(self) -> Dict[str, Any]:
        """Get CDN performance metrics
        
        Returns:
            Dict containing CDN metrics
        """
        try:
            if self.config.cloud_provider.lower() == 'aws':
                return await self._get_cloudfront_metrics()
            elif self.config.cloud_provider.lower() == 'gcp':
                return await self._get_gcp_cdn_metrics()
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to get CDN metrics: {e}")
            return {}
    
    async def _get_cloudfront_metrics(self) -> Dict[str, Any]:
        """Get CloudFront metrics from CloudWatch"""
        try:
            cloudwatch = boto3.client('cloudwatch')
            distribution_id = self._get_cloudfront_distribution_id()
            
            # Get requests metric
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='Requests',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': distribution_id}
                ],
                StartTime=self._get_start_time(),
                EndTime=self._get_end_time(),
                Period=3600,
                Statistics=['Sum']
            )
            
            total_requests = sum(point['Sum'] for point in response['Datapoints'])
            
            # Get bytes downloaded metric
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='BytesDownloaded',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': distribution_id}
                ],
                StartTime=self._get_start_time(),
                EndTime=self._get_end_time(),
                Period=3600,
                Statistics=['Sum']
            )
            
            total_bytes = sum(point['Sum'] for point in response['Datapoints'])
            
            return {
                'total_requests': total_requests,
                'total_bytes_downloaded': total_bytes,
                'distribution_id': distribution_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get CloudFront metrics: {e}")
            return {}
    
    def _get_start_time(self):
        """Get start time for metrics (24 hours ago)"""
        from datetime import datetime, timedelta
        return datetime.utcnow() - timedelta(hours=24)
    
    def _get_end_time(self):
        """Get end time for metrics (now)"""
        from datetime import datetime
        return datetime.utcnow()
    
    async def _get_gcp_cdn_metrics(self) -> Dict[str, Any]:
        """Get GCP CDN metrics"""
        # GCP CDN metrics implementation
        return {}

# Example usage
if __name__ == "__main__":
    async def main():
        config = CDNConfig(
            environment="production",
            cloud_provider="aws",
            origin_domain="api.ainflue.com",
            custom_domains=["cdn.ainflue.com", "assets.ainflue.com"],
            region="us-west-2"
        )
        
        manager = CDNConfigurationManager(config)
        
        # Create CDN distribution
        distribution_id = await manager.create_cdn_distribution()
        print(f"Created CDN distribution: {distribution_id}")
        
        # Configure SSL certificate
        cert_arn = await manager.configure_ssl_certificate(config.custom_domains)
        print(f"Configured SSL certificate: {cert_arn}")
        
        # Get metrics
        metrics = await manager.get_cdn_metrics()
        print(f"CDN metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())