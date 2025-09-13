"""
🤖 AI SERVICES MODULE - ENTERPRISE AI & ML SERVICES
=====================================================

© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE
⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT

AI Services module exports and orchestration.
Provides centralized access to all AI & ML services.

Services exported:
-----------------
- ai_inference_service         - Real-time AI inference
- ai_training_service          - Model training and retraining  
- ai_orchestration_service     - AI workflow orchestration
- ai_validation_service        - Model validation and testing
- ai_model_management_service  - Model lifecycle management
- audio_processing_service     - AI-powered audio processing
- content_classification_service - AI content classification
- ai_performance_optimizer     - AI performance optimization
- ai_pipeline_orchestrator     - AI pipeline orchestration
- ai_model_serving            - Distributed model serving
- ai_experiment_tracker       - ML experiment tracking
- ai_metrics_collector        - AI metrics collection
- ai_security_validator       - AI security validation
- ai_deployment_manager       - Multi-cloud AI deployment
- ai_resource_allocator       - AI resource allocation
- ai_lifecycle_manager        - AI model lifecycle management

Contact: Fahed Mlaiel (mlaiel@live.de)
Team: AI & ML Services Team (6 experts)
"""

# Import existing AI services
from .ai_inference_service import AIInferenceService
from .ai_training_service import AITrainingService  
from .ai_orchestration_service import AIOrchestrationService
from .ai_validation_service import AIValidationService
from .ai_model_management_service import AIModelManagementService
from .audio_processing_service import AudioProcessingService
from .content_classification_service import ContentClassificationService

# Import new AI services (will be created)
try:
    from .ai_performance_optimizer import AIPerformanceOptimizer
    from .ai_pipeline_orchestrator import AIPipelineOrchestrator
    from .ai_model_serving import AIModelServing
    from .ai_experiment_tracker import AIExperimentTracker
    from .ai_metrics_collector import AIMetricsCollector
    from .ai_security_validator import AISecurityValidator
    from .ai_deployment_manager import AIDeploymentManager
    from .ai_resource_allocator import AIResourceAllocator
    from .ai_lifecycle_manager import AILifecycleManager
except ImportError:
    # Services not yet created - will be added progressively
    pass

# Export all services
__all__ = [
    'AIInferenceService',
    'AITrainingService', 
    'AIOrchestrationService',
    'AIValidationService',
    'AIModelManagementService',
    'AudioProcessingService',
    'ContentClassificationService',
    # New services will be added here as they are created
]

def get_services():
    """Get list of all available AI services."""
    return [
        'ai_inference_service.py',
        'ai_training_service.py',
        'ai_orchestration_service.py', 
        'ai_validation_service.py',
        'ai_model_management_service.py',
        'audio_processing_service.py',
        'content_classification_service.py',
        'ai_performance_optimizer.py',
        'ai_pipeline_orchestrator.py',
        'ai_model_serving.py',
        'ai_experiment_tracker.py',
        'ai_metrics_collector.py',
        'ai_security_validator.py',
        'ai_deployment_manager.py',
        'ai_resource_allocator.py',
        'ai_lifecycle_manager.py'
    ]

async def start_services():
    """Start all AI services."""
    # Initialize and start AI services
    pass