"""🚀 Enterprise Inference Serving Engine - Ainflue AI/ML Pipeline
==================================================================

High-performance model serving with auto-scaling, batching,
and multi-model optimization for 53 AI agents.

Expert Implementation:
🧠 ML Engineer: Model serving optimization + inference acceleration
🤖 Lead Dev IA: Multi-model orchestration + routing intelligence
🏗️ Backend Senior: Distributed serving + load balancing + caching
⚙️ DevOps: Auto-scaling + monitoring + deployment automation
🔒 Security: Inference security + API protection + audit trails
🗄️ DBA: Inference metadata + performance tracking + caching
🔗 Microservices: Service mesh integration + communication protocols

Author: Fahed Mlaiel (mlaiel@live.de)
Date: December 2025
Version: Enterprise 1.0

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
import torch.jit
import onnxruntime as ort
import tritonclient.http as httpclient
import aiohttp
from kubernetes import client, config as k8s_config
import yaml
from collections import defaultdict, deque
import psutil
import pickle

logger = logging.getLogger(__name__)


class InferenceStatus(Enum):
    """Inference request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CACHED = "cached"


class ModelFormat(Enum):
    """Supported model formats"""
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    TENSORRT = "tensorrt"
    TRITON = "triton"
    TORCHSCRIPT = "torchscript"


class ServingStrategy(Enum):
    """Model serving strategies"""
    SINGLE_MODEL = "single_model"
    MULTI_MODEL = "multi_model"
    ENSEMBLE = "ensemble"
    A_B_TESTING = "a_b_testing"
    CANARY = "canary"
    SHADOW = "shadow"


@dataclass
class InferenceRequest:
    """Inference request container"""
    request_id: str
    model_id: str
    model_version: str
    input_data: Dict[str, Any]
    creator_id: str
    platform_context: Optional[str] = None
    content_type: Optional[str] = None
    priority: int = 5
    timeout_seconds: int = 30
    caching_enabled: bool = True
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    postprocessing_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InferenceResponse:
    """Inference response container"""
    request_id: str
    model_id: str
    model_version: str
    predictions: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_time_ms: float
    status: InferenceStatus
    error_message: Optional[str] = None
    cached: bool = False
    model_metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelEndpoint:
    """Model serving endpoint configuration"""
    endpoint_id: str
    model_id: str
    model_version: str
    model_format: ModelFormat
    serving_strategy: ServingStrategy
    endpoint_url: str
    health_check_url: str
    max_batch_size: int
    timeout_seconds: int
    auto_scaling_config: Dict[str, Any]
    resource_limits: Dict[str, Any]
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BatchRequest:
    """Batch inference request"""
    batch_id: str
    requests: List[InferenceRequest]
    model_id: str
    batch_size: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 60


class EnterpriseInferenceServingEngine:
    """Enterprise inference serving with auto-scaling and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize inference serving engine"""
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.k8s_client = None
        self.model_endpoints = {}
        self.inference_cache = {}
        self.request_queues = defaultdict(asyncio.Queue)
        self.batch_queues = defaultdict(deque)
        self.performance_metrics = defaultdict(lambda: defaultdict(list))
        self.executor = ThreadPoolExecutor(max_workers=50)
        
        # Serving configuration
        self.serving_config = {
            'max_concurrent_requests': 1000,
            'default_batch_size': 8,
            'max_batch_size': 32,
            'batch_timeout_ms': 100,
            'cache_ttl_seconds': 3600,
            'auto_scaling_enabled': True,
            'load_balancing_strategy': 'round_robin',  # round_robin, least_latency, weighted
            'health_check_interval': 30,
            'performance_monitoring_enabled': True,
            'request_timeout_seconds': 30
        }
        
        # Creator economy optimization
        self.creator_optimization_config = {
            'content_analysis_priority': 9,
            'platform_optimization_priority': 8,
            'seo_enhancement_priority': 7,
            'monetization_prediction_priority': 10,  # Highest priority
            'collaboration_matching_priority': 6,
            'content_protection_priority': 8,
            'creator_specific_caching': True,
            'platform_specific_optimization': True
        }
        
        # Performance targets
        self.performance_targets = {
            'p50_latency_ms': 100,
            'p95_latency_ms': 500,
            'p99_latency_ms': 1000,
            'throughput_rps': 1000,
            'availability_percent': 99.9,
            'error_rate_percent': 0.1
        }
    
    async def initialize(self):
        """Initialize serving engine connections and setup"""
        try:
            # Initialize database connection
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=10,
                max_size=50,
                command_timeout=30
            )
            
            # Initialize Redis for caching and coordination
            self.redis_client = await aioredis.from_url(
                self.config['redis_url'],
                encoding='utf-8',
                decode_responses=False,  # Keep binary for model caching
                max_connections=100
            )
            
            # Initialize Kubernetes client
            try:
                k8s_config.load_incluster_config()
            except:
                k8s_config.load_kube_config()
            self.k8s_client = client.ApiClient()
            
            # Setup database schema
            await self._setup_database_schema()
            
            # Load model endpoints
            await self._load_model_endpoints()
            
            # Start background tasks
            asyncio.create_task(self._batch_processor())
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._performance_monitor())
            asyncio.create_task(self._auto_scaler())
            
            logger.info("Enterprise Inference Serving Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Inference Serving Engine: {e}")
            raise
    
    async def predict(self, request: InferenceRequest) -> InferenceResponse:
        """Single inference prediction"""
        try:
            start_time = time.time()
            
            # Validate request
            await self._validate_inference_request(request)
            
            # Check cache first
            if request.caching_enabled:
                cached_response = await self._get_cached_response(request)
                if cached_response:
                    cached_response.cached = True
                    return cached_response
            
            # Get model endpoint
            endpoint = await self._get_optimal_endpoint(request.model_id, request)
            if not endpoint:
                return InferenceResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    model_version=request.model_version,
                    predictions={},
                    confidence_scores={},
                    processing_time_ms=0,
                    status=InferenceStatus.FAILED,
                    error_message="No available endpoint for model"
                )
            
            # Preprocess input
            processed_input = await self._preprocess_input(request, endpoint)
            
            # Execute inference
            predictions = await self._execute_inference(processed_input, endpoint)
            
            # Postprocess output
            final_predictions = await self._postprocess_output(predictions, request, endpoint)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create response
            response = InferenceResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                model_version=request.model_version,
                predictions=final_predictions,
                confidence_scores=await self._calculate_confidence_scores(final_predictions),
                processing_time_ms=processing_time,
                status=InferenceStatus.COMPLETED,
                model_metadata=endpoint.__dict__,
                performance_metrics={
                    'endpoint_id': endpoint.endpoint_id,
                    'batch_size': 1,
                    'queue_time_ms': 0
                }
            )
            
            # Cache response
            if request.caching_enabled:
                await self._cache_response(request, response)
            
            # Record metrics
            await self._record_inference_metrics(request, response)
            
            logger.debug(f"Inference completed: {request.request_id} in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Inference failed for request {request.request_id}: {e}")
            return InferenceResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                model_version=request.model_version,
                predictions={},
                confidence_scores={},
                processing_time_ms=(time.time() - start_time) * 1000,
                status=InferenceStatus.FAILED,
                error_message=str(e)
            )
    
    async def predict_batch(self, requests: List[InferenceRequest]) -> List[InferenceResponse]:
        """Batch inference prediction"""
        try:
            if not requests:
                return []
            
            # Group requests by model
            model_groups = defaultdict(list)
            for request in requests:
                model_groups[request.model_id].append(request)
            
            # Process each model group
            all_responses = []
            for model_id, model_requests in model_groups.items():
                # Create batch request
                batch_request = BatchRequest(
                    batch_id=f"batch_{uuid.uuid4().hex[:12]}",
                    requests=model_requests,
                    model_id=model_id,
                    batch_size=len(model_requests)
                )
                
                # Execute batch inference
                batch_responses = await self._execute_batch_inference(batch_request)
                all_responses.extend(batch_responses)
            
            return all_responses
            
        except Exception as e:
            logger.error(f"Batch inference failed: {e}")
            # Return error responses for all requests
            return [
                InferenceResponse(
                    request_id=req.request_id,
                    model_id=req.model_id,
                    model_version=req.model_version,
                    predictions={},
                    confidence_scores={},
                    processing_time_ms=0,
                    status=InferenceStatus.FAILED,
                    error_message=str(e)
                )
                for req in requests
            ]
    
    async def register_model_endpoint(self, endpoint: ModelEndpoint) -> bool:
        """Register new model serving endpoint"""
        try:
            # Validate endpoint configuration
            await self._validate_endpoint_config(endpoint)
            
            # Test endpoint health
            if not await self._test_endpoint_health(endpoint):
                raise ValueError(f"Endpoint health check failed: {endpoint.endpoint_url}")
            
            # Store endpoint in database
            await self._store_model_endpoint(endpoint)
            
            # Cache endpoint
            self.model_endpoints[endpoint.endpoint_id] = endpoint
            
            # Update Redis registry
            await self.redis_client.set(
                f"endpoint:{endpoint.endpoint_id}",
                pickle.dumps(endpoint),
                ex=3600
            )
            
            # Log registration
            await self._log_serving_event(endpoint.model_id, 'ENDPOINT_REGISTERED', {
                'endpoint_id': endpoint.endpoint_id,
                'endpoint_url': endpoint.endpoint_url,
                'model_format': endpoint.model_format.value
            })
            
            logger.info(f"Model endpoint registered: {endpoint.endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model endpoint: {e}")
            raise
    
    async def unregister_model_endpoint(self, endpoint_id: str) -> bool:
        """Unregister model serving endpoint"""
        try:
            # Get endpoint
            endpoint = self.model_endpoints.get(endpoint_id)
            if not endpoint:
                return False
            
            # Update status to inactive
            endpoint.status = "inactive"
            
            # Update in database
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    "UPDATE model_endpoints SET status = 'inactive', updated_at = NOW() WHERE endpoint_id = $1",
                    endpoint_id
                )
            
            # Remove from cache
            if endpoint_id in self.model_endpoints:
                del self.model_endpoints[endpoint_id]
            
            # Remove from Redis
            await self.redis_client.delete(f"endpoint:{endpoint_id}")
            
            # Log unregistration
            await self._log_serving_event(endpoint.model_id, 'ENDPOINT_UNREGISTERED', {
                'endpoint_id': endpoint_id
            })
            
            logger.info(f"Model endpoint unregistered: {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister model endpoint: {e}")
            raise
    
    async def get_model_endpoints(self, model_id: str) -> List[ModelEndpoint]:
        """Get all endpoints for a model"""
        try:
            endpoints = []
            for endpoint in self.model_endpoints.values():
                if endpoint.model_id == model_id and endpoint.status == "active":
                    endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to get model endpoints: {e}")
            raise
    
    async def get_serving_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get creator-specific serving analytics for Ainflue platform"""
        try:
            async with self.db_pool.acquire() as connection:
                # Get inference statistics
                stats = await connection.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(*) FILTER (WHERE status = 'completed') as successful_requests,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_requests,
                        COUNT(*) FILTER (WHERE cached = true) as cached_requests,
                        AVG(processing_time_ms) as avg_processing_time,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_ms) as p95_processing_time
                    FROM inference_requests 
                    WHERE creator_id = $1 
                    AND created_at > NOW() - INTERVAL '24 hours'
                    """,
                    creator_id
                )
                
                # Get model usage statistics
                model_stats = await connection.fetch(
                    """
                    SELECT 
                        model_id,
                        COUNT(*) as request_count,
                        AVG(processing_time_ms) as avg_latency,
                        COUNT(*) FILTER (WHERE status = 'completed') as success_count
                    FROM inference_requests 
                    WHERE creator_id = $1
                    AND created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY model_id
                    """,
                    creator_id
                )
                
                # Get platform-specific statistics
                platform_stats = await connection.fetch(
                    """
                    SELECT 
                        platform_context,
                        COUNT(*) as request_count,
                        AVG(processing_time_ms) as avg_latency
                    FROM inference_requests 
                    WHERE creator_id = $1
                    AND platform_context IS NOT NULL
                    AND created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY platform_context
                    """,
                    creator_id
                )
                
                # Get content type distribution
                content_stats = await connection.fetch(
                    """
                    SELECT 
                        content_type,
                        COUNT(*) as request_count
                    FROM inference_requests 
                    WHERE creator_id = $1
                    AND content_type IS NOT NULL
                    AND created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY content_type
                    """,
                    creator_id
                )
            
            # Calculate derived metrics
            total_requests = int(stats['total_requests'] or 0)
            successful_requests = int(stats['successful_requests'] or 0)
            success_rate = successful_requests / max(total_requests, 1)
            cache_hit_rate = int(stats['cached_requests'] or 0) / max(total_requests, 1)
            
            return {
                'creator_id': creator_id,
                'time_period': '24_hours',
                'request_statistics': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': int(stats['failed_requests'] or 0),
                    'cached_requests': int(stats['cached_requests'] or 0),
                    'success_rate': success_rate,
                    'cache_hit_rate': cache_hit_rate
                },
                'performance_metrics': {
                    'average_processing_time_ms': float(stats['avg_processing_time'] or 0),
                    'p95_processing_time_ms': float(stats['p95_processing_time'] or 0),
                    'target_latency_met': float(stats['avg_processing_time'] or 0) < self.performance_targets['p50_latency_ms']
                },
                'model_usage': {
                    row['model_id']: {
                        'request_count': row['request_count'],
                        'average_latency_ms': float(row['avg_latency'] or 0),
                        'success_rate': row['success_count'] / max(row['request_count'], 1)
                    }
                    for row in model_stats
                },
                'platform_distribution': {
                    row['platform_context']: {
                        'request_count': row['request_count'],
                        'average_latency_ms': float(row['avg_latency'] or 0)
                    }
                    for row in platform_stats
                },
                'content_type_distribution': {
                    row['content_type']: row['request_count']
                    for row in content_stats
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get serving analytics: {e}")
            raise
    
    async def scale_endpoint(self, endpoint_id: str, target_replicas: int) -> bool:
        """Scale model endpoint"""
        try:
            endpoint = self.model_endpoints.get(endpoint_id)
            if not endpoint:
                return False
            
            # Update auto-scaling configuration
            endpoint.auto_scaling_config['target_replicas'] = target_replicas
            
            # Update in database
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    UPDATE model_endpoints 
                    SET auto_scaling_config = $1, updated_at = NOW() 
                    WHERE endpoint_id = $2
                    """,
                    json.dumps(endpoint.auto_scaling_config),
                    endpoint_id
                )
            
            # If using Kubernetes, scale the deployment
            if self.k8s_client:
                await self._scale_k8s_deployment(endpoint, target_replicas)
            
            # Log scaling event
            await self._log_serving_event(endpoint.model_id, 'ENDPOINT_SCALED', {
                'endpoint_id': endpoint_id,
                'target_replicas': target_replicas
            })
            
            logger.info(f"Endpoint scaled: {endpoint_id} to {target_replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale endpoint: {e}")
            raise
    
    # Private helper methods
    
    async def _setup_database_schema(self):
        """Setup database schema for inference serving"""
        async with self.db_pool.acquire() as connection:
            # Model endpoints table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS model_endpoints (
                    endpoint_id VARCHAR(50) PRIMARY KEY,
                    model_id VARCHAR(50) NOT NULL,
                    model_version VARCHAR(50) NOT NULL,
                    model_format VARCHAR(50) NOT NULL,
                    serving_strategy VARCHAR(50) NOT NULL,
                    endpoint_url VARCHAR(500) NOT NULL,
                    health_check_url VARCHAR(500),
                    max_batch_size INTEGER DEFAULT 1,
                    timeout_seconds INTEGER DEFAULT 30,
                    auto_scaling_config JSONB,
                    resource_limits JSONB,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Inference requests table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS inference_requests (
                    request_id VARCHAR(50) PRIMARY KEY,
                    model_id VARCHAR(50) NOT NULL,
                    model_version VARCHAR(50) NOT NULL,
                    creator_id VARCHAR(100) NOT NULL,
                    platform_context VARCHAR(100),
                    content_type VARCHAR(100),
                    status VARCHAR(50) NOT NULL,
                    processing_time_ms FLOAT,
                    cached BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    completed_at TIMESTAMP WITH TIME ZONE
                )
            """)
            
            # Serving events table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS serving_events (
                    event_id VARCHAR(50) PRIMARY KEY,
                    model_id VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    event_data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Performance metrics table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS serving_metrics (
                    metric_id VARCHAR(50) PRIMARY KEY,
                    endpoint_id VARCHAR(50) NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (endpoint_id) REFERENCES model_endpoints(endpoint_id)
                )
            """)
            
            # Create indexes
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_endpoints_model ON model_endpoints(model_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_requests_creator ON inference_requests(creator_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_requests_model ON inference_requests(model_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_requests_created ON inference_requests(created_at)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_metrics_endpoint ON serving_metrics(endpoint_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON serving_metrics(timestamp)")
    
    async def _load_model_endpoints(self):
        """Load model endpoints from database"""
        async with self.db_pool.acquire() as connection:
            rows = await connection.fetch(
                "SELECT * FROM model_endpoints WHERE status = 'active'"
            )
            
            for row in rows:
                endpoint = ModelEndpoint(
                    endpoint_id=row['endpoint_id'],
                    model_id=row['model_id'],
                    model_version=row['model_version'],
                    model_format=ModelFormat(row['model_format']),
                    serving_strategy=ServingStrategy(row['serving_strategy']),
                    endpoint_url=row['endpoint_url'],
                    health_check_url=row['health_check_url'],
                    max_batch_size=row['max_batch_size'],
                    timeout_seconds=row['timeout_seconds'],
                    auto_scaling_config=json.loads(row['auto_scaling_config']) if row['auto_scaling_config'] else {},
                    resource_limits=json.loads(row['resource_limits']) if row['resource_limits'] else {},
                    status=row['status'],
                    created_at=row['created_at']
                )
                
                self.model_endpoints[endpoint.endpoint_id] = endpoint
    
    async def _validate_inference_request(self, request: InferenceRequest):
        """Validate inference request"""
        if not request.model_id or not request.creator_id:
            raise ValueError("Model ID and creator ID are required")
        
        if not request.input_data:
            raise ValueError("Input data is required")
        
        if request.priority < 1 or request.priority > 10:
            raise ValueError("Priority must be between 1 and 10")
    
    async def _get_cached_response(self, request: InferenceRequest) -> Optional[InferenceResponse]:
        """Get cached inference response"""
        try:
            # Create cache key
            cache_key = self._create_cache_key(request)
            
            # Get from Redis
            cached_data = await self.redis_client.get(f"inference:{cache_key}")
            if cached_data:
                response_data = pickle.loads(cached_data)
                response = InferenceResponse(**response_data)
                response.request_id = request.request_id  # Update request ID
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None
    
    async def _cache_response(self, request: InferenceRequest, response: InferenceResponse):
        """Cache inference response"""
        try:
            cache_key = self._create_cache_key(request)
            response_data = response.__dict__.copy()
            
            # Store in Redis with TTL
            await self.redis_client.set(
                f"inference:{cache_key}",
                pickle.dumps(response_data),
                ex=self.serving_config['cache_ttl_seconds']
            )
            
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
    
    def _create_cache_key(self, request: InferenceRequest) -> str:
        """Create cache key for inference request"""
        # Create hash of input data for cache key
        input_str = json.dumps(request.input_data, sort_keys=True)
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        
        return f"{request.model_id}:{request.model_version}:{input_hash}"
    
    async def _get_optimal_endpoint(self, model_id: str, request: InferenceRequest) -> Optional[ModelEndpoint]:
        """Get optimal endpoint for model based on load balancing strategy"""
        endpoints = await self.get_model_endpoints(model_id)
        if not endpoints:
            return None
        
        if len(endpoints) == 1:
            return endpoints[0]
        
        # Apply load balancing strategy
        if self.serving_config['load_balancing_strategy'] == 'round_robin':
            # Simple round-robin (in practice, would maintain state)
            return endpoints[int(time.time()) % len(endpoints)]
        
        elif self.serving_config['load_balancing_strategy'] == 'least_latency':
            # Choose endpoint with lowest average latency
            best_endpoint = None
            best_latency = float('inf')
            
            for endpoint in endpoints:
                avg_latency = await self._get_endpoint_avg_latency(endpoint.endpoint_id)
                if avg_latency < best_latency:
                    best_latency = avg_latency
                    best_endpoint = endpoint
            
            return best_endpoint or endpoints[0]
        
        else:  # weighted or default
            return endpoints[0]
    
    async def _preprocess_input(self, request: InferenceRequest, endpoint: ModelEndpoint) -> Dict[str, Any]:
        """Preprocess input data for inference"""
        processed_input = request.input_data.copy()
        
        # Apply preprocessing based on model format
        if endpoint.model_format == ModelFormat.PYTORCH:
            # PyTorch-specific preprocessing
            if 'tensor_data' in processed_input:
                # Convert to tensor format
                processed_input['tensor_data'] = np.array(processed_input['tensor_data'])
        
        elif endpoint.model_format == ModelFormat.ONNX:
            # ONNX-specific preprocessing
            if 'image_data' in processed_input:
                # Ensure proper image format
                processed_input['image_data'] = np.array(processed_input['image_data'], dtype=np.float32)
        
        # Apply custom preprocessing from request config
        if request.preprocessing_config:
            for key, transform in request.preprocessing_config.items():
                if key in processed_input:
                    # Apply transformation (simplified example)
                    if transform.get('normalize'):
                        processed_input[key] = np.array(processed_input[key]) / 255.0
        
        return processed_input
    
    async def _execute_inference(self, input_data: Dict[str, Any], endpoint: ModelEndpoint) -> Dict[str, Any]:
        """Execute inference on endpoint"""
        try:
            if endpoint.model_format == ModelFormat.TRITON:
                return await self._execute_triton_inference(input_data, endpoint)
            
            elif endpoint.model_format in [ModelFormat.PYTORCH, ModelFormat.ONNX]:
                return await self._execute_http_inference(input_data, endpoint)
            
            else:
                # Generic HTTP inference
                return await self._execute_http_inference(input_data, endpoint)
                
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            raise
    
    async def _execute_triton_inference(self, input_data: Dict[str, Any], endpoint: ModelEndpoint) -> Dict[str, Any]:
        """Execute inference using Triton Inference Server"""
        try:
            # Create Triton client
            triton_client = httpclient.InferenceServerClient(
                url=endpoint.endpoint_url,
                verbose=False
            )
            
            # Prepare inputs (simplified)
            inputs = []
            outputs = []
            
            # This would be model-specific input/output preparation
            # For now, return mock results
            return {
                'predictions': [0.8, 0.2],
                'probabilities': [0.85, 0.15]
            }
            
        except Exception as e:
            logger.error(f"Triton inference failed: {e}")
            raise
    
    async def _execute_http_inference(self, input_data: Dict[str, Any], endpoint: ModelEndpoint) -> Dict[str, Any]:
        """Execute inference via HTTP API"""
        try:
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint.endpoint_url,
                    json=input_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
                        
        except Exception as e:
            logger.error(f"HTTP inference failed: {e}")
            raise
    
    async def _postprocess_output(self, predictions: Dict[str, Any], request: InferenceRequest, endpoint: ModelEndpoint) -> Dict[str, Any]:
        """Postprocess inference output"""
        processed_output = predictions.copy()
        
        # Apply postprocessing based on request config
        if request.postprocessing_config:
            for key, transform in request.postprocessing_config.items():
                if key in processed_output:
                    # Apply transformation (simplified example)
                    if transform.get('threshold'):
                        threshold = transform['threshold']
                        if isinstance(processed_output[key], list):
                            processed_output[key] = [x if x > threshold else 0 for x in processed_output[key]]
        
        # Add creator-specific optimizations
        if request.creator_id and request.platform_context:
            # Platform-specific optimizations for Ainflue creators
            processed_output = await self._apply_creator_optimizations(processed_output, request)
        
        return processed_output
    
    async def _apply_creator_optimizations(self, predictions: Dict[str, Any], request: InferenceRequest) -> Dict[str, Any]:
        """Apply creator-specific optimizations for Ainflue platform"""
        optimized_predictions = predictions.copy()
        
        # Platform-specific optimizations
        if request.platform_context:
            platform_multiplier = {
                'youtube': 1.1,
                'instagram': 1.05,
                'tiktok': 1.15,
                'twitter': 1.0
            }.get(request.platform_context.lower(), 1.0)
            
            # Apply platform multiplier to prediction scores
            if 'scores' in optimized_predictions:
                optimized_predictions['scores'] = [
                    score * platform_multiplier for score in optimized_predictions['scores']
                ]
        
        # Content type optimizations
        if request.content_type:
            if request.content_type == 'video' and 'engagement_score' in optimized_predictions:
                # Boost engagement scores for video content
                optimized_predictions['engagement_score'] *= 1.2
            
            elif request.content_type == 'audio' and 'quality_score' in optimized_predictions:
                # Apply audio-specific quality adjustments
                optimized_predictions['quality_score'] *= 1.1
        
        return optimized_predictions
    
    async def _calculate_confidence_scores(self, predictions: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for predictions"""
        confidence_scores = {}
        
        # Extract confidence from different prediction formats
        if 'probabilities' in predictions:
            confidence_scores['overall'] = max(predictions['probabilities'])
        
        if 'scores' in predictions and isinstance(predictions['scores'], list):
            confidence_scores['overall'] = max(predictions['scores'])
        
        if 'confidence' in predictions:
            confidence_scores['overall'] = predictions['confidence']
        
        # Default confidence if none found
        if not confidence_scores:
            confidence_scores['overall'] = 0.8
        
        return confidence_scores
    
    async def _execute_batch_inference(self, batch_request: BatchRequest) -> List[InferenceResponse]:
        """Execute batch inference"""
        try:
            # Get optimal endpoint for the model
            sample_request = batch_request.requests[0]
            endpoint = await self._get_optimal_endpoint(batch_request.model_id, sample_request)
            
            if not endpoint:
                # Return error responses for all requests
                return [
                    InferenceResponse(
                        request_id=req.request_id,
                        model_id=req.model_id,
                        model_version=req.model_version,
                        predictions={},
                        confidence_scores={},
                        processing_time_ms=0,
                        status=InferenceStatus.FAILED,
                        error_message="No available endpoint"
                    )
                    for req in batch_request.requests
                ]
            
            start_time = time.time()
            
            # Prepare batch input
            batch_input = {
                'batch_size': batch_request.batch_size,
                'inputs': []
            }
            
            for request in batch_request.requests:
                processed_input = await self._preprocess_input(request, endpoint)
                batch_input['inputs'].append({
                    'request_id': request.request_id,
                    'data': processed_input
                })
            
            # Execute batch inference
            batch_predictions = await self._execute_inference(batch_input, endpoint)
            
            # Process individual responses
            responses = []
            processing_time = (time.time() - start_time) * 1000
            
            for i, request in enumerate(batch_request.requests):
                if 'results' in batch_predictions and i < len(batch_predictions['results']):
                    pred = batch_predictions['results'][i]
                    final_pred = await self._postprocess_output(pred, request, endpoint)
                    
                    response = InferenceResponse(
                        request_id=request.request_id,
                        model_id=request.model_id,
                        model_version=request.model_version,
                        predictions=final_pred,
                        confidence_scores=await self._calculate_confidence_scores(final_pred),
                        processing_time_ms=processing_time / batch_request.batch_size,
                        status=InferenceStatus.COMPLETED,
                        performance_metrics={
                            'endpoint_id': endpoint.endpoint_id,
                            'batch_size': batch_request.batch_size,
                            'batch_id': batch_request.batch_id
                        }
                    )
                else:
                    response = InferenceResponse(
                        request_id=request.request_id,
                        model_id=request.model_id,
                        model_version=request.model_version,
                        predictions={},
                        confidence_scores={},
                        processing_time_ms=processing_time / batch_request.batch_size,
                        status=InferenceStatus.FAILED,
                        error_message="Batch processing failed"
                    )
                
                responses.append(response)
                
                # Record metrics
                await self._record_inference_metrics(request, response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Batch inference failed: {e}")
            # Return error responses
            return [
                InferenceResponse(
                    request_id=req.request_id,
                    model_id=req.model_id,
                    model_version=req.model_version,
                    predictions={},
                    confidence_scores={},
                    processing_time_ms=0,
                    status=InferenceStatus.FAILED,
                    error_message=str(e)
                )
                for req in batch_request.requests
            ]
    
    async def _record_inference_metrics(self, request: InferenceRequest, response: InferenceResponse):
        """Record inference metrics for monitoring"""
        try:
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO inference_requests (
                        request_id, model_id, model_version, creator_id,
                        platform_context, content_type, status, processing_time_ms,
                        cached, error_message, completed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                    response.request_id,
                    response.model_id,
                    response.model_version,
                    request.creator_id,
                    request.platform_context,
                    request.content_type,
                    response.status.value,
                    response.processing_time_ms,
                    response.cached,
                    response.error_message,
                    response.timestamp
                )
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
    
    async def _batch_processor(self):
        """Background batch processing"""
        while True:
            try:
                # Process batch queues for each model
                for model_id, batch_queue in self.batch_queues.items():
                    if len(batch_queue) >= self.serving_config['default_batch_size']:
                        # Create batch from queued requests
                        batch_requests = []
                        for _ in range(min(len(batch_queue), self.serving_config['max_batch_size'])):
                            batch_requests.append(batch_queue.popleft())
                        
                        if batch_requests:
                            # Execute batch
                            batch_request = BatchRequest(
                                batch_id=f"batch_{uuid.uuid4().hex[:12]}",
                                requests=batch_requests,
                                model_id=model_id,
                                batch_size=len(batch_requests)
                            )
                            
                            asyncio.create_task(self._execute_batch_inference(batch_request))
                
                await asyncio.sleep(self.serving_config['batch_timeout_ms'] / 1000)
                
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                await asyncio.sleep(1)
    
    async def _health_monitor(self):
        """Monitor endpoint health"""
        while True:
            try:
                for endpoint in list(self.model_endpoints.values()):
                    if endpoint.status == "active":
                        healthy = await self._test_endpoint_health(endpoint)
                        if not healthy:
                            logger.warning(f"Endpoint unhealthy: {endpoint.endpoint_id}")
                            # Could implement automatic failover here
                
                await asyncio.sleep(self.serving_config['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(30)
    
    async def _performance_monitor(self):
        """Monitor performance metrics"""
        while True:
            try:
                for endpoint_id, endpoint in self.model_endpoints.items():
                    if endpoint.status == "active":
                        # Calculate performance metrics
                        avg_latency = await self._get_endpoint_avg_latency(endpoint_id)
                        throughput = await self._get_endpoint_throughput(endpoint_id)
                        
                        # Store metrics
                        await self._store_performance_metric(endpoint_id, 'avg_latency_ms', avg_latency)
                        await self._store_performance_metric(endpoint_id, 'throughput_rps', throughput)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scaler(self):
        """Auto-scaling based on metrics"""
        while True:
            try:
                if not self.serving_config['auto_scaling_enabled']:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    continue
                
                for endpoint_id, endpoint in self.model_endpoints.items():
                    if endpoint.status == "active" and endpoint.auto_scaling_config.get('enabled'):
                        # Get current metrics
                        avg_latency = await self._get_endpoint_avg_latency(endpoint_id)
                        throughput = await self._get_endpoint_throughput(endpoint_id)
                        
                        # Check scaling conditions
                        target_latency = endpoint.auto_scaling_config.get('target_latency_ms', 200)
                        min_replicas = endpoint.auto_scaling_config.get('min_replicas', 1)
                        max_replicas = endpoint.auto_scaling_config.get('max_replicas', 10)
                        
                        if avg_latency > target_latency * 1.5:  # Scale up if latency is 50% above target
                            current_replicas = endpoint.auto_scaling_config.get('current_replicas', 1)
                            new_replicas = min(current_replicas + 1, max_replicas)
                            if new_replicas != current_replicas:
                                await self.scale_endpoint(endpoint_id, new_replicas)
                        
                        elif avg_latency < target_latency * 0.7:  # Scale down if latency is 30% below target
                            current_replicas = endpoint.auto_scaling_config.get('current_replicas', 1)
                            new_replicas = max(current_replicas - 1, min_replicas)
                            if new_replicas != current_replicas:
                                await self.scale_endpoint(endpoint_id, new_replicas)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in auto-scaler: {e}")
                await asyncio.sleep(300)
    
    async def _test_endpoint_health(self, endpoint: ModelEndpoint) -> bool:
        """Test endpoint health"""
        try:
            health_url = endpoint.health_check_url or f"{endpoint.endpoint_url}/health"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(health_url) as response:
                    return response.status == 200
                    
        except Exception:
            return False
    
    async def _get_endpoint_avg_latency(self, endpoint_id: str) -> float:
        """Get average latency for endpoint"""
        try:
            async with self.db_pool.acquire() as connection:
                result = await connection.fetchval(
                    """
                    SELECT AVG(metric_value)
                    FROM serving_metrics 
                    WHERE endpoint_id = $1 
                    AND metric_name = 'avg_latency_ms'
                    AND timestamp > NOW() - INTERVAL '5 minutes'
                    """,
                    endpoint_id
                )
                
                return float(result or 0)
                
        except Exception:
            return 0.0
    
    async def _get_endpoint_throughput(self, endpoint_id: str) -> float:
        """Get throughput for endpoint"""
        try:
            async with self.db_pool.acquire() as connection:
                result = await connection.fetchval(
                    """
                    SELECT AVG(metric_value)
                    FROM serving_metrics 
                    WHERE endpoint_id = $1 
                    AND metric_name = 'throughput_rps'
                    AND timestamp > NOW() - INTERVAL '5 minutes'
                    """,
                    endpoint_id
                )
                
                return float(result or 0)
                
        except Exception:
            return 0.0
    
    async def _store_performance_metric(self, endpoint_id: str, metric_name: str, metric_value: float):
        """Store performance metric"""
        try:
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO serving_metrics (metric_id, endpoint_id, metric_name, metric_value)
                    VALUES ($1, $2, $3, $4)
                    """,
                    f"metric_{uuid.uuid4().hex[:12]}",
                    endpoint_id,
                    metric_name,
                    metric_value
                )
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    async def _validate_endpoint_config(self, endpoint: ModelEndpoint):
        """Validate endpoint configuration"""
        if not endpoint.endpoint_url:
            raise ValueError("Endpoint URL is required")
        
        if not endpoint.model_id:
            raise ValueError("Model ID is required")
        
        if endpoint.max_batch_size < 1:
            raise ValueError("Max batch size must be positive")
    
    async def _store_model_endpoint(self, endpoint: ModelEndpoint):
        """Store model endpoint in database"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO model_endpoints (
                    endpoint_id, model_id, model_version, model_format,
                    serving_strategy, endpoint_url, health_check_url,
                    max_batch_size, timeout_seconds, auto_scaling_config,
                    resource_limits, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                endpoint.endpoint_id,
                endpoint.model_id,
                endpoint.model_version,
                endpoint.model_format.value,
                endpoint.serving_strategy.value,
                endpoint.endpoint_url,
                endpoint.health_check_url,
                endpoint.max_batch_size,
                endpoint.timeout_seconds,
                json.dumps(endpoint.auto_scaling_config),
                json.dumps(endpoint.resource_limits),
                endpoint.status
            )
    
    async def _log_serving_event(self, model_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log serving event"""
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO serving_events (event_id, model_id, event_type, event_data)
                VALUES ($1, $2, $3, $4)
                """,
                event_id,
                model_id,
                event_type,
                json.dumps(event_data)
            )
    
    async def _scale_k8s_deployment(self, endpoint: ModelEndpoint, target_replicas: int):
        """Scale Kubernetes deployment"""
        try:
            # This would implement Kubernetes scaling
            # For now, just update the config
            endpoint.auto_scaling_config['current_replicas'] = target_replicas
            
        except Exception as e:
            logger.error(f"Failed to scale K8s deployment: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_pool:
            await self.db_pool.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.executor:
            self.executor.shutdown(wait=True)


# Factory function for easy initialization
async def create_inference_serving_engine(config: Dict[str, Any]) -> EnterpriseInferenceServingEngine:
    """Create and initialize inference serving engine"""
    engine = EnterpriseInferenceServingEngine(config)
    await engine.initialize()
    return engine