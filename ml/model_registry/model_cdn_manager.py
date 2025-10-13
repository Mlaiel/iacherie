#!/usr/bin/env python3
"""
Model CDN Manager for IA Chérie ML Platform
Content Delivery Network integration for global model distribution
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import aiohttp
import hashlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
import redis
import zipfile
import gzip
from datetime import datetime, timedelta
import ssl
import certifi

@dataclass
class CDNEndpoint:
    """CDN endpoint configuration"""
    name: str
    url: str
    region: str
    provider: str  # 'cloudflare', 'aws', 'azure', 'gcp'
    priority: int = 1
    health_check_url: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None
    max_bandwidth_mbps: Optional[float] = None
    
@dataclass
class ModelDistribution:
    """Model distribution metadata"""
    model_id: str
    model_version: str
    file_size_bytes: int
    checksum: str
    compression_type: str
    endpoints: List[CDNEndpoint] = field(default_factory=list)
    cache_ttl_hours: int = 24
    geo_restrictions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
@dataclass
class DownloadMetrics:
    """Download performance metrics"""
    endpoint_name: str
    download_time_ms: float
    bytes_downloaded: int
    bandwidth_mbps: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

class CDNHealthMonitor:
    """Monitor CDN endpoint health and performance"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.health_cache_ttl = 300  # 5 minutes
        
    async def check_endpoint_health(self, endpoint: CDNEndpoint) -> Dict[str, Any]:
        """Check health of a CDN endpoint"""
        health_key = f"cdn_health:{endpoint.name}"
        
        # Check cached health status
        cached_health = self.redis_client.get(health_key)
        if cached_health:
            return json.loads(cached_health)
        
        health_status = {
            'endpoint': endpoint.name,
            'url': endpoint.url,
            'healthy': False,
            'response_time_ms': None,
            'status_code': None,
            'error': None,
            'checked_at': datetime.utcnow().isoformat()
        }
        
        try:
            check_url = endpoint.health_check_url or f"{endpoint.url}/health"
            
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            start_time = time.time()
            async with aiohttp.ClientSession(connector=connector) as session:
                headers = endpoint.auth_headers or {}
                async with session.get(check_url, headers=headers, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    health_status.update({
                        'healthy': response.status == 200,
                        'response_time_ms': response_time,
                        'status_code': response.status
                    })
                    
        except Exception as e:
            health_status['error'] = str(e)
            self.logger.warning(f"Health check failed for {endpoint.name}: {e}")
        
        # Cache health status
        self.redis_client.setex(
            health_key, 
            self.health_cache_ttl, 
            json.dumps(health_status)
        )
        
        return health_status
    
    async def monitor_all_endpoints(self, endpoints: List[CDNEndpoint]) -> List[Dict[str, Any]]:
        """Monitor health of all CDN endpoints"""
        tasks = [self.check_endpoint_health(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks, return_exceptions=True)

class ModelCompressor:
    """Compress models for efficient CDN distribution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['gzip', 'zip', 'lz4']
    
    async def compress_model(self, model_path: Path, compression_type: str = 'gzip') -> Tuple[Path, str]:
        """Compress model file for distribution"""
        if compression_type not in self.supported_formats:
            raise ValueError(f"Unsupported compression type: {compression_type}")
        
        compressed_path = model_path.with_suffix(f"{model_path.suffix}.{compression_type}")
        
        if compression_type == 'gzip':
            with open(model_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
        
        elif compression_type == 'zip':
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(model_path, model_path.name)
        
        # Calculate checksum
        checksum = await self._calculate_checksum(compressed_path)
        
        self.logger.info(f"Compressed {model_path} to {compressed_path} ({compression_type})")
        return compressed_path, checksum
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

class CloudProviderUploader:
    """Upload models to various cloud providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def upload_to_aws_s3(self, file_path: Path, bucket: str, key: str) -> str:
        """Upload model to AWS S3"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.get('aws_access_key_id'),
                aws_secret_access_key=self.config.get('aws_secret_access_key'),
                region_name=self.config.get('aws_region', 'us-east-1')
            )
            
            # Upload with metadata
            extra_args = {
                'ContentType': 'application/octet-stream',
                'Metadata': {
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'checksum': hashlib.md5(file_path.read_bytes()).hexdigest()
                }
            }
            
            s3_client.upload_file(str(file_path), bucket, key, ExtraArgs=extra_args)
            
            # Get CloudFront URL if configured
            cloudfront_domain = self.config.get('cloudfront_domain')
            if cloudfront_domain:
                return f"https://{cloudfront_domain}/{key}"
            else:
                return f"https://{bucket}.s3.amazonaws.com/{key}"
                
        except Exception as e:
            self.logger.error(f"Failed to upload to S3: {e}")
            raise
    
    async def upload_to_azure_blob(self, file_path: Path, container: str, blob_name: str) -> str:
        """Upload model to Azure Blob Storage"""
        try:
            blob_service_client = BlobServiceClient(
                account_url=f"https://{self.config['azure_account_name']}.blob.core.windows.net",
                credential=self.config['azure_account_key']
            )
            
            blob_client = blob_service_client.get_blob_client(
                container=container, 
                blob=blob_name
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(
                    data, 
                    overwrite=True,
                    metadata={
                        'uploaded_at': datetime.utcnow().isoformat(),
                        'checksum': hashlib.md5(file_path.read_bytes()).hexdigest()
                    }
                )
            
            # Get CDN URL if configured
            cdn_endpoint = self.config.get('azure_cdn_endpoint')
            if cdn_endpoint:
                return f"https://{cdn_endpoint}/{container}/{blob_name}"
            else:
                return f"https://{self.config['azure_account_name']}.blob.core.windows.net/{container}/{blob_name}"
                
        except Exception as e:
            self.logger.error(f"Failed to upload to Azure: {e}")
            raise
    
    async def upload_to_gcp_storage(self, file_path: Path, bucket: str, object_name: str) -> str:
        """Upload model to Google Cloud Storage"""
        try:
            client = gcs.Client.from_service_account_json(
                self.config['gcp_service_account_path']
            )
            
            bucket_obj = client.bucket(bucket)
            blob = bucket_obj.blob(object_name)
            
            # Set metadata
            blob.metadata = {
                'uploaded_at': datetime.utcnow().isoformat(),
                'checksum': hashlib.md5(file_path.read_bytes()).hexdigest()
            }
            
            blob.upload_from_filename(str(file_path))
            
            # Get CDN URL if configured
            cdn_domain = self.config.get('gcp_cdn_domain')
            if cdn_domain:
                return f"https://{cdn_domain}/{object_name}"
            else:
                return f"https://storage.googleapis.com/{bucket}/{object_name}"
                
        except Exception as e:
            self.logger.error(f"Failed to upload to GCP: {e}")
            raise

class ModelCDNManager:
    """Enterprise CDN manager for global model distribution"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.health_monitor = CDNHealthMonitor(self.redis_client)
        self.compressor = ModelCompressor()
        self.uploader = CloudProviderUploader(config)
        self.endpoints = []
        self.distributions = {}
        
        # Initialize CDN endpoints
        self._initialize_endpoints()
    
    def _initialize_endpoints(self):
        """Initialize CDN endpoints from configuration"""
        endpoint_configs = self.config.get('cdn_endpoints', [])
        
        for endpoint_config in endpoint_configs:
            endpoint = CDNEndpoint(**endpoint_config)
            self.endpoints.append(endpoint)
            
        self.logger.info(f"Initialized {len(self.endpoints)} CDN endpoints")
    
    async def distribute_model(self, model_path: Path, model_id: str, 
                             model_version: str, compression_type: str = 'gzip',
                             geo_restrictions: Optional[List[str]] = None) -> ModelDistribution:
        """Distribute model to all CDN endpoints"""
        
        # Compress model
        compressed_path, checksum = await self.compressor.compress_model(
            model_path, compression_type
        )
        
        # Create distribution metadata
        distribution = ModelDistribution(
            model_id=model_id,
            model_version=model_version,
            file_size_bytes=compressed_path.stat().st_size,
            checksum=checksum,
            compression_type=compression_type,
            geo_restrictions=geo_restrictions or []
        )
        
        # Upload to healthy endpoints
        healthy_endpoints = await self._get_healthy_endpoints()
        upload_tasks = []
        
        for endpoint in healthy_endpoints:
            task = self._upload_to_endpoint(compressed_path, endpoint, model_id, model_version)
            upload_tasks.append(task)
        
        # Execute uploads concurrently
        upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
        
        # Process results
        successful_endpoints = []
        for endpoint, result in zip(healthy_endpoints, upload_results):
            if not isinstance(result, Exception):
                endpoint.url = result  # Update with actual CDN URL
                successful_endpoints.append(endpoint)
                self.logger.info(f"Successfully uploaded to {endpoint.name}: {result}")
            else:
                self.logger.error(f"Failed to upload to {endpoint.name}: {result}")
        
        distribution.endpoints = successful_endpoints
        
        # Cache distribution metadata
        self._cache_distribution(distribution)
        
        # Store in registry
        self.distributions[f"{model_id}:{model_version}"] = distribution
        
        return distribution
    
    async def _get_healthy_endpoints(self) -> List[CDNEndpoint]:
        """Get list of healthy CDN endpoints"""
        health_results = await self.health_monitor.monitor_all_endpoints(self.endpoints)
        
        healthy_endpoints = []
        for endpoint, health in zip(self.endpoints, health_results):
            if isinstance(health, dict) and health.get('healthy', False):
                healthy_endpoints.append(endpoint)
        
        return healthy_endpoints
    
    async def _upload_to_endpoint(self, file_path: Path, endpoint: CDNEndpoint,
                                model_id: str, model_version: str) -> str:
        """Upload model to specific CDN endpoint"""
        object_key = f"models/{model_id}/{model_version}/{file_path.name}"
        
        if endpoint.provider == 'aws':
            bucket = self.config.get('aws_s3_bucket')
            return await self.uploader.upload_to_aws_s3(file_path, bucket, object_key)
        
        elif endpoint.provider == 'azure':
            container = self.config.get('azure_container')
            return await self.uploader.upload_to_azure_blob(file_path, container, object_key)
        
        elif endpoint.provider == 'gcp':
            bucket = self.config.get('gcp_bucket')
            return await self.uploader.upload_to_gcp_storage(file_path, bucket, object_key)
        
        else:
            raise ValueError(f"Unsupported provider: {endpoint.provider}")
    
    def _cache_distribution(self, distribution: ModelDistribution):
        """Cache distribution metadata"""
        cache_key = f"model_distribution:{distribution.model_id}:{distribution.model_version}"
        cache_data = {
            'model_id': distribution.model_id,
            'model_version': distribution.model_version,
            'file_size_bytes': distribution.file_size_bytes,
            'checksum': distribution.checksum,
            'compression_type': distribution.compression_type,
            'endpoints': [
                {
                    'name': ep.name,
                    'url': ep.url,
                    'region': ep.region,
                    'priority': ep.priority
                }
                for ep in distribution.endpoints
            ],
            'created_at': distribution.created_at.isoformat()
        }
        
        # Cache for 24 hours
        self.redis_client.setex(
            cache_key,
            distribution.cache_ttl_hours * 3600,
            json.dumps(cache_data)
        )
    
    async def get_optimal_download_url(self, model_id: str, model_version: str,
                                     user_region: Optional[str] = None) -> Tuple[str, CDNEndpoint]:
        """Get optimal download URL based on user location and endpoint health"""
        
        distribution_key = f"{model_id}:{model_version}"
        distribution = self.distributions.get(distribution_key)
        
        if not distribution:
            # Try to load from cache
            distribution = self._load_distribution_from_cache(model_id, model_version)
            
        if not distribution:
            raise ValueError(f"Model distribution not found: {model_id}:{model_version}")
        
        # Filter endpoints by region if specified
        candidate_endpoints = distribution.endpoints
        if user_region:
            regional_endpoints = [ep for ep in candidate_endpoints if ep.region == user_region]
            if regional_endpoints:
                candidate_endpoints = regional_endpoints
        
        # Check health of candidate endpoints
        health_tasks = [
            self.health_monitor.check_endpoint_health(ep) 
            for ep in candidate_endpoints
        ]
        health_results = await asyncio.gather(*health_tasks)
        
        # Find the best endpoint (healthy + lowest response time + highest priority)
        best_endpoint = None
        best_score = float('inf')
        
        for endpoint, health in zip(candidate_endpoints, health_results):
            if not health.get('healthy', False):
                continue
                
            # Calculate score (lower is better)
            response_time = health.get('response_time_ms', 1000)
            priority_penalty = (10 - endpoint.priority) * 100  # Higher priority = lower penalty
            score = response_time + priority_penalty
            
            if score < best_score:
                best_score = score
                best_endpoint = endpoint
        
        if not best_endpoint:
            raise RuntimeError("No healthy endpoints available")
        
        return best_endpoint.url, best_endpoint
    
    def _load_distribution_from_cache(self, model_id: str, model_version: str) -> Optional[ModelDistribution]:
        """Load distribution metadata from cache"""
        cache_key = f"model_distribution:{model_id}:{model_version}"
        cached_data = self.redis_client.get(cache_key)
        
        if not cached_data:
            return None
        
        data = json.loads(cached_data)
        
        # Reconstruct endpoints
        endpoints = []
        for ep_data in data['endpoints']:
            endpoint = CDNEndpoint(
                name=ep_data['name'],
                url=ep_data['url'],
                region=ep_data['region'],
                provider='unknown',  # This would be stored in cache in real implementation
                priority=ep_data['priority']
            )
            endpoints.append(endpoint)
        
        # Reconstruct distribution
        distribution = ModelDistribution(
            model_id=data['model_id'],
            model_version=data['model_version'],
            file_size_bytes=data['file_size_bytes'],
            checksum=data['checksum'],
            compression_type=data['compression_type'],
            endpoints=endpoints,
            created_at=datetime.fromisoformat(data['created_at'])
        )
        
        return distribution
    
    async def download_model(self, model_id: str, model_version: str,
                           download_path: Path, user_region: Optional[str] = None,
                           max_retries: int = 3) -> DownloadMetrics:
        """Download model from optimal CDN endpoint"""
        
        download_url, endpoint = await self.get_optimal_download_url(
            model_id, model_version, user_region
        )
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                
                async with aiohttp.ClientSession(connector=connector) as session:
                    headers = endpoint.auth_headers or {}
                    async with session.get(download_url, headers=headers) as response:
                        response.raise_for_status()
                        
                        # Download file
                        content = await response.read()
                        download_path.write_bytes(content)
                        
                        download_time = (time.time() - start_time) * 1000
                        bandwidth = (len(content) * 8) / (download_time / 1000) / 1_000_000  # Mbps
                        
                        return DownloadMetrics(
                            endpoint_name=endpoint.name,
                            download_time_ms=download_time,
                            bytes_downloaded=len(content),
                            bandwidth_mbps=bandwidth,
                            success=True
                        )
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    return DownloadMetrics(
                        endpoint_name=endpoint.name,
                        download_time_ms=0,
                        bytes_downloaded=0,
                        bandwidth_mbps=0,
                        success=False,
                        error_message=str(e)
                    )
                
                self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def invalidate_cache(self, model_id: str, model_version: str):
        """Invalidate CDN cache for a specific model"""
        # This would integrate with CDN provider APIs to invalidate cache
        cache_key = f"model_distribution:{model_id}:{model_version}"
        self.redis_client.delete(cache_key)
        
        # Remove from local registry
        distribution_key = f"{model_id}:{model_version}"
        if distribution_key in self.distributions:
            del self.distributions[distribution_key]
        
        self.logger.info(f"Invalidated cache for {model_id}:{model_version}")
    
    async def get_distribution_analytics(self, model_id: str, 
                                       model_version: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for model distribution"""
        # This would integrate with CDN analytics APIs
        analytics = {
            'model_id': model_id,
            'model_version': model_version,
            'total_downloads': 0,
            'bandwidth_used_gb': 0,
            'geographic_distribution': {},
            'endpoint_performance': [],
            'cache_hit_ratio': 0.0,
            'average_download_time_ms': 0.0
        }
        
        # Placeholder for real analytics implementation
        return analytics
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get CDN cache status and statistics"""
        return {
            'total_distributions': len(self.distributions),
            'active_endpoints': len(self.endpoints),
            'cache_size_mb': 0,  # Would calculate actual cache size
            'uptime_percentage': 99.9,  # Would calculate from health checks
            'last_health_check': datetime.utcnow().isoformat()
        }

# Example usage and configuration
async def main():
    """Example usage of CDN manager"""
    
    # Configuration
    config = {
        'cdn_endpoints': [
            {
                'name': 'aws-us-east',
                'url': 'https://d123456789.cloudfront.net',
                'region': 'us-east-1',
                'provider': 'aws',
                'priority': 1
            },
            {
                'name': 'azure-europe',
                'url': 'https://example.azureedge.net',
                'region': 'eu-west-1',
                'provider': 'azure',
                'priority': 2
            }
        ],
        'aws_s3_bucket': 'iacherie-models',
        'azure_container': 'models',
        'gcp_bucket': 'iacherie-ml-models',
        'redis_host': 'localhost',
        'redis_port': 6379
    }
    
    # Initialize CDN manager
    cdn_manager = ModelCDNManager(config)
    
    # Example model distribution
    model_path = Path('model.pth')
    if model_path.exists():
        distribution = await cdn_manager.distribute_model(
            model_path=model_path,
            model_id='content_classifier',
            model_version='v1.2.0',
            compression_type='gzip'
        )
        
        print(f"✅ Model distributed to {len(distribution.endpoints)} endpoints")
        
        # Get optimal download URL
        download_url, endpoint = await cdn_manager.get_optimal_download_url(
            'content_classifier', 'v1.2.0', user_region='us-east-1'
        )
        
        print(f"✅ Optimal download URL: {download_url} (via {endpoint.name})")
    
    # Get cache status
    status = cdn_manager.get_cache_status()
    print(f"✅ CDN Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())