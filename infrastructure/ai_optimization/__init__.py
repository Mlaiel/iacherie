"""
AI Optimization Module - Enterprise AI Infrastructure Optimization
================================================================================

Expert Team: Lead Dev IA + ML Engineer + Backend Senior + DevOps
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🧠 Lead Dev IA: AI orchestration, 53 agents architecture, ML pipelines
🤖 ML Engineer: Model optimization, GPU clusters, inference optimization
🏗️ Backend Senior: Microservices integration, scalability
⚙️ DevOps: Infrastructure automation, monitoring

AI Optimization for 53 specialized agents supporting:
- Creative AI optimization for content creators
- Performance optimization for ML workloads
- GPU cluster management and allocation
- Prompt engineering and fine-tuning
- AI resource scheduling and load balancing
"""

from .ai_prompt_optimizer import AIPromptOptimizer
from .model_performance_optimizer import ModelPerformanceOptimizer
from .gpu_cluster_manager import GPUClusterManager
from .inference_optimizer import InferenceOptimizer
from .ai_workload_scheduler import AIWorkloadScheduler
from .prompt_engineering_pipeline import PromptEngineeringPipeline
from .model_serving_optimizer import ModelServingOptimizer
from .ai_performance_monitor import AIPerformanceMonitor
from .auto_scaling_ai import AutoScalingAI
from .model_cache_manager import ModelCacheManager
from .distributed_ai_coordinator import DistributedAICoordinator
from .creative_ai_optimizer import CreativeAIOptimizer
from .ai_quality_assurance import AIQualityAssurance
from .ai_resource_allocator import AIResourceAllocator

__all__ = [
    'AIPromptOptimizer',
    'ModelPerformanceOptimizer', 
    'GPUClusterManager',
    'InferenceOptimizer',
    'AIWorkloadScheduler',
    'PromptEngineeringPipeline',
    'ModelServingOptimizer',
    'AIPerformanceMonitor',
    'AutoScalingAI',
    'ModelCacheManager',
    'DistributedAICoordinator',
    'CreativeAIOptimizer',
    'AIQualityAssurance',
    'AIResourceAllocator'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise AI optimization infrastructure for 53 specialized agents"