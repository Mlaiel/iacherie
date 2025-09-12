#!/usr/bin/env python3
"""
Model CDN Manager for Ainflue ML Models
Content delivery network integration for global model distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CDNNode:
    """CDN node configuration"""
    node_id: str
    region: str
    endpoint_url: str
    capacity_gb: float
    current_usage_gb: float
    latency_ms: float
    bandwidth_mbps: float
    status: str  # ACTIVE, MAINTENANCE, OFFLINE
    last_health_check: datetime

@dataclass
class ModelDistribution:
    """Model distribution configuration"""
    model_id: str
    model_version: str
    model_size_gb: float
    distribution_strategy: str  # GLOBAL, REGIONAL, EDGE
    replicas_count: int
    cache_ttl_hours: int
    priority_level: str  # HIGH, MEDIUM, LOW
    creator_type: str
    deployed_nodes: List[str]
    distribution_status: str
    created_at: datetime

@dataclass
class CDNMetrics:
    """CDN performance metrics"""
    node_id: str
    cache_hit_ratio: float
    avg_response_time_ms: float
    bandwidth_utilization: float
    request_count: int
    error_count: int
    data_transferred_gb: float
    timestamp: datetime

class CDNProvider(ABC):
    """Abstract base class for CDN providers"""
    
    @abstractmethod
    async def upload_model(self, model_id: str, model_data: bytes, metadata: Dict[str, Any]) -> bool:
        """Upload model to CDN"""
        pass
    
    @abstractmethod
    async def get_model_url(self, model_id: str, region: str) -> str:
        """Get optimal CDN URL for model"""
        pass
    
    @abstractmethod
    async def invalidate_cache(self, model_id: str) -> bool:
        """Invalidate cached model"""
        pass

class AWSCloudFrontProvider(CDNProvider):
    """AWS CloudFront CDN provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.distribution_id = config.get('distribution_id')
        self.bucket_name = config.get('s3_bucket')
    
    async def upload_model(self, model_id: str, model_data: bytes, metadata: Dict[str, Any]) -> bool:
        """Upload model to S3 and distribute via CloudFront"""
        try:
            logger.info(f"📤 Uploading model {model_id} to AWS CloudFront")
            
            # Simulate S3 upload
            s3_key = f"models/{model_id}/{metadata.get('version', 'latest')}/model.bin"
            
            # Calculate checksum
            checksum = hashlib.sha256(model_data).hexdigest()
            
            # Simulate upload success
            upload_success = True
            
            if upload_success:
                logger.info(f"   ✅ Model uploaded to S3: s3://{self.bucket_name}/{s3_key}")
                logger.info(f"   📊 Size: {len(model_data)/1024/1024:.1f} MB")
                logger.info(f"   🔐 Checksum: {checksum[:16]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error uploading to AWS CloudFront: {e}")
            return False
    
    async def get_model_url(self, model_id: str, region: str) -> str:
        """Get CloudFront URL optimized for region"""
        try:
            # Generate region-optimized URL
            base_url = f"https://{self.distribution_id}.cloudfront.net"
            model_path = f"models/{model_id}/latest/model.bin"
            
            # Add region-specific parameters
            region_params = {
                'us-east-1': 'edge=us-east',
                'eu-west-1': 'edge=eu-west',
                'ap-southeast-1': 'edge=ap-southeast'
            }
            
            params = region_params.get(region, 'edge=global')
            url = f"{base_url}/{model_path}?{params}"
            
            return url
            
        except Exception as e:
            logger.error(f"Error generating CloudFront URL: {e}")
            return ""
    
    async def invalidate_cache(self, model_id: str) -> bool:
        """Invalidate CloudFront cache for model"""
        try:
            logger.info(f"🔄 Invalidating CloudFront cache for model {model_id}")
            
            # Simulate cache invalidation
            invalidation_paths = [f"/models/{model_id}/*"]
            
            # Simulate invalidation success
            invalidation_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"   ✅ Cache invalidation initiated: {invalidation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating CloudFront cache: {e}")
            return False

class AzureCDNProvider(CDNProvider):
    """Azure CDN provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.profile_name = config.get('profile_name')
        self.endpoint_name = config.get('endpoint_name')
    
    async def upload_model(self, model_id: str, model_data: bytes, metadata: Dict[str, Any]) -> bool:
        """Upload model to Azure Blob Storage and distribute via Azure CDN"""
        try:
            logger.info(f"📤 Uploading model {model_id} to Azure CDN")
            
            # Simulate Azure Blob Storage upload
            blob_path = f"models/{model_id}/{metadata.get('version', 'latest')}/model.bin"
            
            # Simulate upload success
            upload_success = True
            
            if upload_success:
                logger.info(f"   ✅ Model uploaded to Azure Blob Storage: {blob_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error uploading to Azure CDN: {e}")
            return False
    
    async def get_model_url(self, model_id: str, region: str) -> str:
        """Get Azure CDN URL optimized for region"""
        try:
            base_url = f"https://{self.endpoint_name}.azureedge.net"
            model_path = f"models/{model_id}/latest/model.bin"
            
            return f"{base_url}/{model_path}"
            
        except Exception as e:
            logger.error(f"Error generating Azure CDN URL: {e}")
            return ""
    
    async def invalidate_cache(self, model_id: str) -> bool:
        """Purge Azure CDN cache for model"""
        try:
            logger.info(f"🔄 Purging Azure CDN cache for model {model_id}")
            
            # Simulate cache purge
            purge_paths = [f"/models/{model_id}/*"]
            
            logger.info(f"   ✅ Cache purge initiated for paths: {purge_paths}")
            return True
            
        except Exception as e:
            logger.error(f"Error purging Azure CDN cache: {e}")
            return False

class ModelCDNManager:
    """
    Enterprise model CDN manager for global model distribution
    
    🎖️ EXPERT MULTI-ROLE IMPLEMENTATION:
    - Lead Dev IA: Orchestration of global CDN distribution strategy
    - Backend Senior: High-performance CDN integration and caching
    - DevOps: Multi-cloud CDN deployment and management
    - Security: CDN security and model protection
    - Audio Engineer: Creator-specific model distribution optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize model CDN manager"""
        self.config = config or {}
        
        # CDN providers
        self.cdn_providers = {
            'aws': AWSCloudFrontProvider(self.config.get('aws', {})),
            'azure': AzureCDNProvider(self.config.get('azure', {}))
        }
        
        # CDN nodes configuration
        self.cdn_nodes = self._initialize_cdn_nodes()
        
        # Model distribution configurations
        self.model_distributions = {}
        
        # Creator-specific distribution strategies
        self.creator_distribution_strategies = {
            'musician': {
                'strategy': 'GLOBAL',
                'priority': 'HIGH',
                'cache_ttl_hours': 24,
                'preferred_regions': ['us-east-1', 'eu-west-1', 'ap-southeast-1']
            },
            'blogger': {
                'strategy': 'REGIONAL',
                'priority': 'MEDIUM',
                'cache_ttl_hours': 12,
                'preferred_regions': ['us-east-1', 'eu-west-1']
            },
            'photographer': {
                'strategy': 'GLOBAL',
                'priority': 'HIGH',
                'cache_ttl_hours': 48,
                'preferred_regions': ['us-east-1', 'eu-west-1', 'ap-southeast-1']
            },
            'influencer': {
                'strategy': 'EDGE',
                'priority': 'HIGH',
                'cache_ttl_hours': 6,
                'preferred_regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
            },
            'comedian': {
                'strategy': 'REGIONAL',
                'priority': 'MEDIUM',
                'cache_ttl_hours': 24,
                'preferred_regions': ['us-east-1', 'eu-west-1']
            }
        }
        
        logger.info("✅ Model CDN Manager initialized")
    
    def _initialize_cdn_nodes(self) -> List[CDNNode]:
        """Initialize CDN node configurations"""
        nodes = [
            CDNNode(
                node_id='us-east-1-cdn',
                region='us-east-1',
                endpoint_url='https://d1234567890.cloudfront.net',
                capacity_gb=1000.0,
                current_usage_gb=250.0,
                latency_ms=15.0,
                bandwidth_mbps=10000.0,
                status='ACTIVE',
                last_health_check=datetime.now()
            ),
            CDNNode(
                node_id='eu-west-1-cdn',
                region='eu-west-1',
                endpoint_url='https://d0987654321.cloudfront.net',
                capacity_gb=800.0,
                current_usage_gb=200.0,
                latency_ms=20.0,
                bandwidth_mbps=8000.0,
                status='ACTIVE',
                last_health_check=datetime.now()
            ),
            CDNNode(
                node_id='ap-southeast-1-cdn',
                region='ap-southeast-1',
                endpoint_url='https://d1122334455.cloudfront.net',
                capacity_gb=600.0,
                current_usage_gb=150.0,
                latency_ms=25.0,
                bandwidth_mbps=6000.0,
                status='ACTIVE',
                last_health_check=datetime.now()
            )
        ]
        return nodes
    
    async def distribute_model(self, 
                              model_id: str,
                              model_data: bytes,
                              metadata: Dict[str, Any]) -> ModelDistribution:
        """
        Distribute model across CDN network
        
        🎖️ LEAD DEV IA: Orchestration of model distribution strategy
        """
        try:
            logger.info(f"🌐 Distributing model {model_id} across CDN network")
            
            creator_type = metadata.get('creator_type', 'musician')
            model_version = metadata.get('version', '1.0.0')
            model_size_gb = len(model_data) / (1024 ** 3)
            
            # Get distribution strategy for creator type
            strategy_config = self.creator_distribution_strategies.get(
                creator_type, self.creator_distribution_strategies['musician']
            )
            
            # Select optimal CDN nodes
            selected_nodes = await self._select_cdn_nodes(
                strategy_config, model_size_gb
            )
            
            # Distribute to selected providers
            distribution_success = await self._distribute_to_providers(
                model_id, model_data, metadata, selected_nodes
            )
            
            if not distribution_success:
                raise Exception("Failed to distribute model to CDN providers")
            
            # Create distribution record
            distribution = ModelDistribution(
                model_id=model_id,
                model_version=model_version,
                model_size_gb=model_size_gb,
                distribution_strategy=strategy_config['strategy'],
                replicas_count=len(selected_nodes),
                cache_ttl_hours=strategy_config['cache_ttl_hours'],
                priority_level=strategy_config['priority'],
                creator_type=creator_type,
                deployed_nodes=[node.node_id for node in selected_nodes],
                distribution_status='DISTRIBUTED',
                created_at=datetime.now()
            )
            
            # Store distribution configuration
            self.model_distributions[model_id] = distribution
            
            # Monitor distribution health
            await self._schedule_health_monitoring(model_id)
            
            logger.info(f"✅ Model {model_id} successfully distributed")
            logger.info(f"   Strategy: {distribution.distribution_strategy}")
            logger.info(f"   Replicas: {distribution.replicas_count}")
            logger.info(f"   Nodes: {distribution.deployed_nodes}")
            
            return distribution
            
        except Exception as e:
            logger.error(f"❌ Error distributing model: {e}")
            raise
    
    async def _select_cdn_nodes(self, 
                               strategy_config: Dict[str, Any],
                               model_size_gb: float) -> List[CDNNode]:
        """
        Select optimal CDN nodes based on distribution strategy
        
        🛡️ BACKEND SENIOR: Intelligent node selection and load balancing
        """
        try:
            strategy = strategy_config['strategy']
            preferred_regions = strategy_config['preferred_regions']
            
            # Filter available nodes
            available_nodes = [
                node for node in self.cdn_nodes 
                if node.status == 'ACTIVE' and 
                   node.current_usage_gb + model_size_gb <= node.capacity_gb
            ]
            
            selected_nodes = []
            
            if strategy == 'GLOBAL':
                # Select nodes from all preferred regions
                for region in preferred_regions:
                    region_nodes = [n for n in available_nodes if n.region == region]
                    if region_nodes:
                        # Select node with lowest latency and usage
                        best_node = min(region_nodes, 
                                       key=lambda n: n.latency_ms + (n.current_usage_gb / n.capacity_gb) * 100)
                        selected_nodes.append(best_node)
            
            elif strategy == 'REGIONAL':
                # Select 1-2 nodes from primary regions
                primary_regions = preferred_regions[:2]
                for region in primary_regions:
                    region_nodes = [n for n in available_nodes if n.region == region]
                    if region_nodes:
                        best_node = min(region_nodes, key=lambda n: n.current_usage_gb / n.capacity_gb)
                        selected_nodes.append(best_node)
            
            elif strategy == 'EDGE':
                # Select all available nodes for maximum edge coverage
                selected_nodes = available_nodes[:4]  # Limit to 4 for cost control
            
            if not selected_nodes:
                # Fallback: select at least one available node
                if available_nodes:
                    selected_nodes = [available_nodes[0]]
                else:
                    raise Exception("No available CDN nodes with sufficient capacity")
            
            return selected_nodes
            
        except Exception as e:
            logger.error(f"Error selecting CDN nodes: {e}")
            raise
    
    async def _distribute_to_providers(self, 
                                     model_id: str,
                                     model_data: bytes,
                                     metadata: Dict[str, Any],
                                     selected_nodes: List[CDNNode]) -> bool:
        """
        Distribute model to CDN providers
        
        ⚙️ DEVOPS: Multi-cloud CDN deployment orchestration
        """
        try:
            distribution_tasks = []
            
            # Distribute to primary provider (AWS)
            aws_task = self.cdn_providers['aws'].upload_model(
                model_id, model_data, metadata
            )
            distribution_tasks.append(aws_task)
            
            # Distribute to secondary provider (Azure) for redundancy
            azure_task = self.cdn_providers['azure'].upload_model(
                model_id, model_data, metadata
            )
            distribution_tasks.append(azure_task)
            
            # Execute distribution tasks
            results = await asyncio.gather(*distribution_tasks, return_exceptions=True)
            
            # Check results
            successful_distributions = sum(1 for result in results if result is True)
            
            if successful_distributions == 0:
                logger.error("❌ Failed to distribute to any CDN provider")
                return False
            elif successful_distributions < len(distribution_tasks):
                logger.warning(f"⚠️ Partial distribution success: {successful_distributions}/{len(distribution_tasks)}")
            else:
                logger.info(f"✅ Full distribution success: {successful_distributions}/{len(distribution_tasks)}")
            
            # Update node usage
            model_size_gb = len(model_data) / (1024 ** 3)
            for node in selected_nodes:
                node.current_usage_gb += model_size_gb
            
            return successful_distributions > 0
            
        except Exception as e:
            logger.error(f"Error distributing to providers: {e}")
            return False
    
    async def get_optimal_model_url(self, 
                                   model_id: str,
                                   user_region: str,
                                   creator_type: Optional[str] = None) -> str:
        """
        Get optimal model URL for user location
        
        🎵 AUDIO ENGINEER: Creator-specific URL optimization
        """
        try:
            logger.info(f"🎯 Getting optimal URL for model {model_id} in region {user_region}")
            
            # Check if model is distributed
            if model_id not in self.model_distributions:
                raise ValueError(f"Model {model_id} not found in CDN")
            
            distribution = self.model_distributions[model_id]
            
            # Find nearest CDN node
            nearest_node = await self._find_nearest_node(user_region, distribution.deployed_nodes)
            
            # Get URL from appropriate provider
            provider_preference = self._get_provider_preference(creator_type)
            
            url = await self.cdn_providers[provider_preference].get_model_url(
                model_id, user_region
            )
            
            # Add cache optimization parameters
            cache_params = self._get_cache_optimization_params(distribution)
            if cache_params:
                separator = '&' if '?' in url else '?'
                url += separator + cache_params
            
            logger.info(f"   ✅ Optimal URL: {url[:50]}...")
            return url
            
        except Exception as e:
            logger.error(f"Error getting optimal model URL: {e}")
            raise
    
    def _get_provider_preference(self, creator_type: Optional[str]) -> str:
        """
        Get preferred CDN provider for creator type
        
        🎵 AUDIO ENGINEER: Creator-specific provider optimization
        """
        # Creator-specific provider preferences
        creator_preferences = {
            'musician': 'aws',      # AWS has better audio processing edge locations
            'blogger': 'azure',     # Azure has better text processing capabilities
            'photographer': 'aws',  # AWS has better image processing edge locations
            'influencer': 'aws',    # AWS has broader global coverage
            'comedian': 'azure'     # Azure has good video processing support
        }
        
        return creator_preferences.get(creator_type, 'aws')
    
    async def _find_nearest_node(self, user_region: str, deployed_nodes: List[str]) -> CDNNode:
        """Find nearest CDN node to user region"""
        try:
            # Region proximity mapping
            region_proximity = {
                'us-east-1': ['us-east-1', 'us-west-2', 'eu-west-1'],
                'us-west-2': ['us-west-2', 'us-east-1', 'ap-southeast-1'],
                'eu-west-1': ['eu-west-1', 'us-east-1', 'ap-southeast-1'],
                'ap-southeast-1': ['ap-southeast-1', 'us-west-2', 'eu-west-1']
            }
            
            preferred_regions = region_proximity.get(user_region, ['us-east-1'])
            
            # Find deployed node in preferred order
            for preferred_region in preferred_regions:
                for node in self.cdn_nodes:
                    if node.node_id in deployed_nodes and node.region == preferred_region:
                        return node
            
            # Fallback: return first deployed node
            for node in self.cdn_nodes:
                if node.node_id in deployed_nodes:
                    return node
            
            raise ValueError("No deployed nodes found")
            
        except Exception as e:
            logger.error(f"Error finding nearest node: {e}")
            raise
    
    def _get_cache_optimization_params(self, distribution: ModelDistribution) -> str:
        """Get cache optimization parameters"""
        params = []
        
        # Cache TTL
        params.append(f"cache_ttl={distribution.cache_ttl_hours}h")
        
        # Priority level
        if distribution.priority_level == 'HIGH':
            params.append("priority=1")
        elif distribution.priority_level == 'MEDIUM':
            params.append("priority=2")
        else:
            params.append("priority=3")
        
        # Creator type optimization
        if distribution.creator_type:
            params.append(f"creator_type={distribution.creator_type}")
        
        return "&".join(params)
    
    async def invalidate_model_cache(self, model_id: str) -> bool:
        """
        Invalidate model cache across all CDN providers
        
        🔄 CACHE MANAGEMENT: Global cache invalidation
        """
        try:
            logger.info(f"🔄 Invalidating cache for model {model_id}")
            
            # Invalidate across all providers
            invalidation_tasks = []
            for provider_name, provider in self.cdn_providers.items():
                task = provider.invalidate_cache(model_id)
                invalidation_tasks.append(task)
            
            results = await asyncio.gather(*invalidation_tasks, return_exceptions=True)
            
            successful_invalidations = sum(1 for result in results if result is True)
            
            if successful_invalidations > 0:
                logger.info(f"✅ Cache invalidated on {successful_invalidations}/{len(self.cdn_providers)} providers")
                return True
            else:
                logger.error("❌ Failed to invalidate cache on any provider")
                return False
            
        except Exception as e:
            logger.error(f"Error invalidating model cache: {e}")
            return False
    
    async def _schedule_health_monitoring(self, model_id: str):
        """
        Schedule health monitoring for distributed model
        
        📊 MONITORING: CDN health and performance monitoring
        """
        try:
            logger.info(f"📊 Scheduling health monitoring for model {model_id}")
            
            # In production, this would schedule periodic health checks
            # For now, just log the scheduling
            
        except Exception as e:
            logger.error(f"Error scheduling health monitoring: {e}")
    
    async def get_cdn_metrics(self, time_range: timedelta = timedelta(hours=24)) -> List[CDNMetrics]:
        """
        Get CDN performance metrics
        
        📈 ANALYTICS: CDN performance analysis
        """
        try:
            logger.info(f"📈 Collecting CDN metrics for {time_range.total_seconds()/3600:.1f} hours")
            
            metrics = []
            
            # Generate simulated metrics for each node
            for node in self.cdn_nodes:
                if node.status == 'ACTIVE':
                    metric = CDNMetrics(
                        node_id=node.node_id,
                        cache_hit_ratio=0.85 + (hash(node.node_id) % 100) / 1000,  # 85-95%
                        avg_response_time_ms=node.latency_ms + (hash(node.node_id) % 20),
                        bandwidth_utilization=(node.current_usage_gb / node.capacity_gb) * 100,
                        request_count=10000 + (hash(node.node_id) % 50000),
                        error_count=50 + (hash(node.node_id) % 100),
                        data_transferred_gb=node.current_usage_gb * 0.1,  # 10% of stored data
                        timestamp=datetime.now()
                    )
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting CDN metrics: {e}")
            return []
    
    async def get_distribution_report(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive distribution report
        
        📊 REPORTING: Distribution analytics and insights
        """
        try:
            logger.info(f"📊 Generating distribution report")
            
            if model_id:
                distributions = [self.model_distributions.get(model_id)]
                distributions = [d for d in distributions if d is not None]
            else:
                distributions = list(self.model_distributions.values())
            
            # Calculate summary statistics
            total_models = len(distributions)
            total_size_gb = sum(d.model_size_gb for d in distributions)
            total_replicas = sum(d.replicas_count for d in distributions)
            
            # Distribution by strategy
            strategy_counts = {}
            for distribution in distributions:
                strategy = distribution.distribution_strategy
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            # Distribution by creator type
            creator_counts = {}
            for distribution in distributions:
                creator_type = distribution.creator_type
                creator_counts[creator_type] = creator_counts.get(creator_type, 0) + 1
            
            # Node utilization
            node_utilization = {}
            for node in self.cdn_nodes:
                utilization_pct = (node.current_usage_gb / node.capacity_gb) * 100
                node_utilization[node.node_id] = {
                    'region': node.region,
                    'utilization_percent': utilization_pct,
                    'available_gb': node.capacity_gb - node.current_usage_gb,
                    'status': node.status
                }
            
            report = {
                'summary': {
                    'total_models': total_models,
                    'total_size_gb': total_size_gb,
                    'total_replicas': total_replicas,
                    'avg_replicas_per_model': total_replicas / max(total_models, 1)
                },
                'distribution_strategies': strategy_counts,
                'creator_type_distribution': creator_counts,
                'node_utilization': node_utilization,
                'recent_distributions': [
                    {
                        'model_id': d.model_id,
                        'creator_type': d.creator_type,
                        'strategy': d.distribution_strategy,
                        'replicas': d.replicas_count,
                        'size_gb': d.model_size_gb,
                        'created_at': d.created_at.isoformat()
                    }
                    for d in sorted(distributions, key=lambda x: x.created_at, reverse=True)[:10]
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating distribution report: {e}")
            raise

# Example usage and testing
async def main():
    """Example usage of model CDN manager"""
    try:
        # Initialize CDN manager
        config = {
            'aws': {
                'distribution_id': 'E1234567890ABC',
                's3_bucket': 'ainflue-ml-models'
            },
            'azure': {
                'profile_name': 'ainflue-cdn',
                'endpoint_name': 'ainflue-models'
            }
        }
        
        cdn_manager = ModelCDNManager(config)
        
        # Simulate model data
        model_data = b"fake_model_data" * 1000  # ~15KB fake model
        metadata = {
            'creator_type': 'musician',
            'version': '2.1.0',
            'model_type': 'engagement_predictor',
            'training_date': '2025-01-15'
        }
        
        # Distribute model
        distribution = await cdn_manager.distribute_model(
            model_id='musician-engagement-predictor-v2',
            model_data=model_data,
            metadata=metadata
        )
        
        print(f"\n🌐 Model Distribution Results:")
        print(f"   Model ID: {distribution.model_id}")
        print(f"   Strategy: {distribution.distribution_strategy}")
        print(f"   Replicas: {distribution.replicas_count}")
        print(f"   Deployed Nodes: {distribution.deployed_nodes}")
        print(f"   Cache TTL: {distribution.cache_ttl_hours} hours")
        
        # Get optimal URL
        optimal_url = await cdn_manager.get_optimal_model_url(
            model_id='musician-engagement-predictor-v2',
            user_region='us-east-1',
            creator_type='musician'
        )
        
        print(f"\n🎯 Optimal URL for US East:")
        print(f"   {optimal_url}")
        
        # Get CDN metrics
        metrics = await cdn_manager.get_cdn_metrics()
        print(f"\n📊 CDN Metrics ({len(metrics)} nodes):")
        for metric in metrics:
            print(f"   {metric.node_id}: {metric.cache_hit_ratio:.1%} hit ratio, "
                  f"{metric.avg_response_time_ms:.0f}ms response time")
        
        # Get distribution report
        report = await cdn_manager.get_distribution_report()
        print(f"\n📊 Distribution Report:")
        print(f"   Total Models: {report['summary']['total_models']}")
        print(f"   Total Size: {report['summary']['total_size_gb']:.3f} GB")
        print(f"   Average Replicas: {report['summary']['avg_replicas_per_model']:.1f}")
        
        # Invalidate cache
        await cdn_manager.invalidate_model_cache('musician-engagement-predictor-v2')
        
        print("\n✅ Model CDN management demonstration complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in model CDN management: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())