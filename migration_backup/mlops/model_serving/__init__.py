"""
Model Serving Module
Enterprise model serving and inference infrastructure

Components:
- Real-time and batch inference engines
- Model routing and load balancing
- Inference optimization and caching
- Performance monitoring and metrics
- Adaptive serving controllers

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .inference_server_manager import InferenceServerManager
from .realtime_inference_engine import RealtimeInferenceEngine
from .batch_inference_processor import BatchInferenceProcessor
from .latency_monitor import LatencyMonitor
from .throughput_analyzer import ThroughputAnalyzer
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker
from .model_router import ModelRouter
from .serving_analytics import ServingAnalytics
from .model_cache_manager import ModelCacheManager
from .load_balancer_serving import LoadBalancerServing
from .prediction_aggregator import PredictionAggregator
from .serving_optimization import ServingOptimization
from .edge_inference_manager import EdgeInferenceManager
from .serving_metrics_collector import ServingMetricsCollector
from .adaptive_serving_controller import AdaptiveServingController

__version__ = "1.0.0"
__all__ = [
    "InferenceServerManager",
    "RealtimeInferenceEngine",
    "BatchInferenceProcessor",
    "LatencyMonitor",
    "ThroughputAnalyzer",
    "RateLimiter",
    "CircuitBreaker",
    "ModelRouter",
    "ServingAnalytics",
    "ModelCacheManager",
    "LoadBalancerServing",
    "PredictionAggregator",
    "ServingOptimization",
    "EdgeInferenceManager",
    "ServingMetricsCollector",
    "AdaptiveServingController"
]