"""ML Agent Index - Central Access Point & Orchestration Hub

Ultra-advanced machine learning operations orchestrator providing centralized access,
service discovery, health monitoring, and intelligent routing for all ML services
in the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This orchestration system and ML methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL (c)2025

🎯 BUSINESS LOGIC INTEGRATION:
Creator Upload → AI/ML Processing → Feature Extraction → Model Inference
→ Content Protection → SEO Optimization → Collaboration Matching
→ Distribution & Monetization → Performance Analytics

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import uuid
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import traceback
from contextlib import asynccontextmanager

# Core monitoring and metrics
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis
import psycopg2
from sqlalchemy.orm import Session

# Platform core
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import MLError, ValidationError, ServiceError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    MLError, ValidationError, ServiceError = globals().get('MLError, ValidationError, ServiceError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.health_checker import HealthChecker
from ...utils.circuit_breaker import CircuitBreaker

# ML Agent components
from .ml_agent import MLAgent, MLAgentManager
from .model_trainer import ModelTrainer, TrainingPipeline, TrainingStatus
from .model_inference import ModelInference, BatchProcessor, InferenceEngine
from .model_optimizer import ModelOptimizer, PerformanceTuner, OptimizationStrategy
from .feature_extractor import FeatureExtractor, DataPreprocessor, FeatureEngineer
from .model_registry import ModelRegistry, ModelVersion, ModelMetadata

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """
ML service operational status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    CRITICAL = "critical"

class MLServiceType(Enum):
    """Available ML service types"""

    TRAINING = "training"
    INFERENCE = "inference"
    OPTIMIZATION = "optimization"
    FEATURE_EXTRACTION = "feature_extraction"
    MODEL_REGISTRY = "model_registry"
    BATCH_PROCESSING = "batch_processing"
    REALTIME_PROCESSING = "realtime_processing"

@dataclass
class ServiceHealth:
    """Service health information"""
    service_type: MLServiceType
    status: ServiceStatus
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MLOperationRequest:
    """
Standardized ML operation request"""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_type: MLServiceType = MLServiceType.INFERENCE
    operation: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    priority: int = 5
    timeout: int = 300
    callback_url: Optional[str] = None

class MLServiceOrchestrator:
    """
    Ultra-advanced ML service orchestrator managing all ML operations,
    service health, intelligent routing, and performance optimization.
    """
    
    def __init__(self):
        self.service_registry = {}
        self.health_monitor = HealthChecker()
        self.performance_monitor = PerformanceMonitor()
        self.circuit_breakers = {}
        self._initialize_services()
        self._setup_monitoring()
        
    def _initialize_services(self):
        """
Initialize all ML services and components"""
        try:
            # Initialize core ML components
            self.ml_agent = MLAgent()
            self.model_trainer = ModelTrainer()
            self.model_inference = ModelInference()
            self.model_optimizer = ModelOptimizer()
            self.feature_extractor = FeatureExtractor()
            self.model_registry = ModelRegistry()
            
            # Initialize specialized processors
            self.batch_processor = BatchProcessor()
            self.inference_engine = InferenceEngine()
            self.training_pipeline = TrainingPipeline()
            self.performance_tuner = PerformanceTuner()
            self.feature_engineer = FeatureEngineer()
            
            # Register services
            self._register_service(MLServiceType.TRAINING, self.model_trainer)
            self._register_service(MLServiceType.INFERENCE, self.model_inference)
            self._register_service(MLServiceType.OPTIMIZATION, self.model_optimizer)
            self._register_service(MLServiceType.FEATURE_EXTRACTION, self.feature_extractor)
            self._register_service(MLServiceType.MODEL_REGISTRY, self.model_registry)
            self._register_service(MLServiceType.BATCH_PROCESSING, self.batch_processor)
            self._register_service(MLServiceType.REALTIME_PROCESSING, self.inference_engine)
            
            logger.info("ML services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML services: {str(e)}")
            raise MLError(f"Service initialization failed: {str(e)}")
    
    def _register_service(self, service_type: MLServiceType, service_instance: Any):
        """Register a service in the registry"""
        self.service_registry[service_type] = {
            'instance': service_instance,
            'circuit_breaker': CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30,
                expected_exception=Exception
            ),
            'last_health_check': None,
            'health_status': ServiceStatus.HEALTHY
        }
        
    def _setup_monitoring(self):
        """
Setup comprehensive monitoring and metrics collection"""
        # Prometheus metrics
        self.request_counter = Counter(
            'ml_requests_total',
            'Total ML requests processed',
            ['service_type', 'operation', 'status']
        )
        
        self.request_duration = Histogram(
            'ml_request_duration_seconds',
            'ML request processing duration',
            ['service_type', 'operation']
        )
        
        self.service_health_gauge = Gauge(
            'ml_service_health',
            'ML service health status',
            ['service_type', 'status']
        )
        
        self.active_operations = Gauge(
            'ml_active_operations',
            'Number of active ML operations',
            ['service_type']
        )

    async def process_request(self, request: MLOperationRequest) -> Dict[str, Any]:
        """
        Process ML operation request with intelligent routing,
        circuit breaking, and comprehensive monitoring
        """
        start_time = time.time()
        operation_id = request.operation_id
        
        try:
            # Validate request
            await self._validate_request(request)
            
            # Route to appropriate service
            service_info = self.service_registry.get(request.service_type)
            if not service_info:
                raise MLError(f"Service type not available: {request.service_type.value}")
            
            # Check circuit breaker
            circuit_breaker = service_info['circuit_breaker']
            if circuit_breaker.state == 'OPEN':
                raise ServiceError(f"Service {request.service_type.value} temporarily unavailable")
            
            # Execute operation with monitoring
            with self.performance_monitor.measure_operation(f"ml_{request.service_type.value}"):
                result = await self._execute_operation(service_info['instance'], request)
            
            # Record success metrics
            self.request_counter.labels(
                service_type=request.service_type.value,
                operation=request.operation,
                status='success'
            ).inc()
            
            processing_time = time.time() - start_time
            self.request_duration.labels(
                service_type=request.service_type.value,
                operation=request.operation
            ).observe(processing_time)
            
            return {
                'operation_id': operation_id,
                'status': 'completed',
                'result': result,
                'processing_time': processing_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            # Record failure metrics
            self.request_counter.labels(
                service_type=request.service_type.value,
                operation=request.operation,
                status='error'
            ).inc()
            
            logger.error(f"ML operation failed [{operation_id}]: {str(e)}")
            
            return {
                'operation_id': operation_id,
                'status': 'failed',
                'error': str(e),
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    async def _validate_request(self, request: MLOperationRequest):
        """Validate incoming ML operation request"""
        if not request.operation:
            raise ValidationError("Operation type is required")
        
        if request.service_type not in self.service_registry:
            raise ValidationError(f"Unsupported service type: {request.service_type.value}")
        
        # Additional validation based on service type
        if request.service_type == MLServiceType.TRAINING:
            if 'training_data' not in request.data:
                raise ValidationError("Training data is required for training operations")
        
        elif request.service_type == MLServiceType.INFERENCE:
            if 'input_data' not in request.data:
                raise ValidationError("Input data is required for inference operations")

    async def _execute_operation(self, service_instance: Any, request: MLOperationRequest) -> Any:
        """Execute ML operation on the appropriate service instance"""
        operation_method = getattr(service_instance, request.operation, None)
        
        if not operation_method:
            raise MLError(f"Operation '{request.operation}' not available on service")
        
        if asyncio.iscoroutinefunction(operation_method):
            return await operation_method(**request.data)
        else:
            # Execute in thread pool for CPU-intensive operations
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, operation_method, **request.data)

    async def get_service_health(self, service_type: Optional[MLServiceType] = None) -> Dict[str, ServiceHealth]:
        """Get comprehensive health status for ML services"""
        health_status = {}
        
        services_to_check = [service_type] if service_type else list(self.service_registry.keys())
        
        for svc_type in services_to_check:
            if svc_type not in self.service_registry:
                continue
                
            try:
                # Perform health check
                service_info = self.service_registry[svc_type]
                instance = service_info['instance']
                
                # Check if service has health check method
                health_check = getattr(instance, 'health_check', None)
                if health_check:
                    health_result = await health_check() if asyncio.iscoroutinefunction(health_check) else health_check()
                    status = ServiceStatus.HEALTHY if health_result.get('healthy', True) else ServiceStatus.UNHEALTHY
                else:
                    status = ServiceStatus.HEALTHY
                
                # Get system metrics
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                health_status[svc_type.value] = ServiceHealth(
                    service_type=svc_type,
                    status=status,
                    response_time=0.1,  # Would be measured in real health check
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    error_rate=0.0,  # Would be calculated from metrics
                    last_check=datetime.now(timezone.utc),
                    details=health_result if 'health_result' in locals() else {}
                )
                
            except Exception as e:
                health_status[svc_type.value] = ServiceHealth(
                    service_type=svc_type,
                    status=ServiceStatus.UNHEALTHY,
                    response_time=999.9,
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    error_rate=100.0,
                    last_check=datetime.now(timezone.utc),
                    details={'error': str(e)}
                )
        
        return health_status

    async def get_service_metrics(self) -> Dict[str, Any]:
        """
Get comprehensive performance metrics for all ML services"""
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'services': {},
            'system': {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        # Collect service-specific metrics
        for service_type, service_info in self.service_registry.items():
            try:
                instance = service_info['instance']
                service_metrics = {}
                
                # Get metrics if service supports it
                if hasattr(instance, 'get_metrics'):
                    service_metrics = instance.get_metrics()
                
                metrics['services'][service_type.value] = service_metrics
                
            except Exception as e:
                logger.error(f"Error collecting metrics for {service_type.value}: {str(e)}")
                metrics['services'][service_type.value] = {'error': str(e)}
        
        return metrics

    async def shutdown(self):
        """Gracefully shutdown all ML services"""
        logger.info("Initiating ML services shutdown...")
        
        # Shutdown all services
        for service_type, service_info in self.service_registry.items():
            try:
                instance = service_info['instance']
                if hasattr(instance, 'shutdown'):
                    if asyncio.iscoroutinefunction(instance.shutdown):
                        await instance.shutdown()
                    else:
                        instance.shutdown()
                logger.info(f"Service {service_type.value} shutdown completed")
                
            except Exception as e:
                logger.error(f"Error shutting down {service_type.value}: {str(e)}")
        
        logger.info("ML services shutdown completed")

# Global orchestrator instance
ml_orchestrator = MLServiceOrchestrator()

# Convenience functions for direct service access
async def process_training_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process ML model training request"""
    request = MLOperationRequest(
        service_type=MLServiceType.TRAINING,
        operation='train_model',
        data=request_data
    )
    return await ml_orchestrator.process_request(request)

async def process_inference_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
Process ML model inference request"""
    request = MLOperationRequest(
        service_type=MLServiceType.INFERENCE,
        operation='predict',
        data=request_data
    )
    return await ml_orchestrator.process_request(request)

async def process_optimization_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
Process model optimization request"""
    request = MLOperationRequest(
        service_type=MLServiceType.OPTIMIZATION,
        operation='optimize_model',
        data=request_data
    )
    return await ml_orchestrator.process_request(request)

async def extract_features(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
Process feature extraction request"""
    request = MLOperationRequest(
        service_type=MLServiceType.FEATURE_EXTRACTION,
        operation='extract_features',
        data=request_data
    )
    return await ml_orchestrator.process_request(request)

async def get_ml_health() -> Dict[str, ServiceHealth]:
    """
Get health status of all ML services"""
    return await ml_orchestrator.get_service_health()

async def get_ml_metrics() -> Dict[str, Any]:
    """
Get comprehensive ML performance metrics"""
    return await ml_orchestrator.get_service_metrics()

# Export all components for external access
__all__ = [
    'MLServiceOrchestrator',
    'MLOperationRequest', 
    'ServiceHealth',
    'MLServiceType',
    'ServiceStatus',
    'ml_orchestrator',
    'process_training_request',
    'process_inference_request', 
    'process_optimization_request',
    'extract_features',
    'get_ml_health',
    'get_ml_metrics'
]
