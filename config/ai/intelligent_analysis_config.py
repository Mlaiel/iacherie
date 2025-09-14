"""
Intelligent Analysis Configuration - Enterprise Configuration Management
Enterprise configuration for intelligent content analysis systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


class AnalysisType(str, Enum):
    """Types of intelligent analysis"""
    CONTENT_CLASSIFICATION = "content_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    TREND_ANALYSIS = "trend_analysis"
    STYLE_ANALYSIS = "style_analysis"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    PERFORMANCE_PREDICTION = "performance_prediction"
    AUDIENCE_ANALYSIS = "audience_analysis"
    MONETIZATION_OPTIMIZATION = "monetization_optimization"


class AnalysisEngine(str, Enum):
    """Analysis engine types"""
    TRANSFORMER_BASED = "transformer_based"
    CNN_BASED = "cnn_based"
    RNN_BASED = "rnn_based"
    ENSEMBLE = "ensemble"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"
    CUSTOM_ML = "custom_ml"


class AnalysisPriority(str, Enum):
    """Analysis processing priorities"""
    REAL_TIME = "real_time"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BATCH = "batch"


class AccuracyLevel(str, Enum):
    """Required accuracy levels"""
    BASIC = "basic"          # >80%
    STANDARD = "standard"    # >90%
    HIGH = "high"           # >95%
    PREMIUM = "premium"     # >98%
    ENTERPRISE = "enterprise" # >99%


@dataclass
class AnalysisModel:
    """Analysis model configuration"""
    model_name: str
    model_type: str
    engine: AnalysisEngine
    accuracy_target: float
    processing_time_ms: int
    resource_requirements: Dict[str, Any]
    preprocessing_steps: List[str]
    postprocessing_steps: List[str]


@dataclass
class AnalysisWorkflow:
    """Analysis workflow configuration"""
    workflow_name: str
    analysis_types: List[AnalysisType]
    execution_order: List[str]
    parallel_execution: bool
    error_handling: str
    timeout_seconds: int
    retry_policy: Dict[str, Any]


@dataclass
class QualityMetrics:
    """Quality assessment metrics"""
    technical_quality: Dict[str, float]
    content_quality: Dict[str, float]
    engagement_potential: Dict[str, float]
    monetization_potential: Dict[str, float]


class IntelligentAnalysisSettings:
    """Intelligent analysis configuration settings"""
    
    def __init__(self) -> None:
        # Analysis Models Configuration
        self.analysis_models = {
            "content_classifier": AnalysisModel(
                model_name="content_classifier",
                model_type="multi_class_classification",
                engine=AnalysisEngine.TRANSFORMER_BASED,
                accuracy_target=0.95,
                processing_time_ms=500,
                resource_requirements={
                    "cpu_cores": 2,
                    "memory_gb": 4,
                    "gpu_memory_mb": 2048
                },
                preprocessing_steps=["tokenization", "normalization", "feature_extraction"],
                postprocessing_steps=["confidence_scoring", "category_mapping", "result_formatting"]
            ),
            
            "sentiment_analyzer": AnalysisModel(
                model_name="sentiment_analyzer",
                model_type="sentiment_classification",
                engine=AnalysisEngine.TRANSFORMER_BASED,
                accuracy_target=0.92,
                processing_time_ms=300,
                resource_requirements={
                    "cpu_cores": 1,
                    "memory_gb": 2,
                    "gpu_memory_mb": 1024
                },
                preprocessing_steps=["text_cleaning", "tokenization", "emotion_detection"],
                postprocessing_steps=["sentiment_scoring", "emotion_mapping", "confidence_calculation"]
            ),
            
            "quality_assessor": AnalysisModel(
                model_name="quality_assessor",
                model_type="multi_modal_regression",
                engine=AnalysisEngine.ENSEMBLE,
                accuracy_target=0.88,
                processing_time_ms=1000,
                resource_requirements={
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "gpu_memory_mb": 4096
                },
                preprocessing_steps=["feature_extraction", "normalization", "quality_indicators"],
                postprocessing_steps=["score_aggregation", "quality_breakdown", "improvement_suggestions"]
            ),
            
            "engagement_predictor": AnalysisModel(
                model_name="engagement_predictor",
                model_type="engagement_regression",
                engine=AnalysisEngine.HYBRID,
                accuracy_target=0.85,
                processing_time_ms=800,
                resource_requirements={
                    "cpu_cores": 3,
                    "memory_gb": 6,
                    "gpu_memory_mb": 3072
                },
                preprocessing_steps=["content_analysis", "historical_data", "trend_analysis"],
                postprocessing_steps=["engagement_scoring", "viral_potential", "optimization_recommendations"]
            ),
            
            "style_analyzer": AnalysisModel(
                model_name="style_analyzer",
                model_type="style_classification",
                engine=AnalysisEngine.CNN_BASED,
                accuracy_target=0.90,
                processing_time_ms=600,
                resource_requirements={
                    "cpu_cores": 2,
                    "memory_gb": 4,
                    "gpu_memory_mb": 2048
                },
                preprocessing_steps=["visual_feature_extraction", "style_embedding", "pattern_recognition"],
                postprocessing_steps=["style_classification", "similarity_scoring", "style_recommendations"]
            ),
            
            "trend_analyzer": AnalysisModel(
                model_name="trend_analyzer",
                model_type="trend_prediction",
                engine=AnalysisEngine.RNN_BASED,
                accuracy_target=0.82,
                processing_time_ms=1200,
                resource_requirements={
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "gpu_memory_mb": 4096
                },
                preprocessing_steps=["time_series_preparation", "feature_engineering", "trend_extraction"],
                postprocessing_steps=["trend_scoring", "future_prediction", "trend_recommendations"]
            )
        }
        
        # Analysis Workflows
        self.analysis_workflows = {
            "comprehensive_analysis": AnalysisWorkflow(
                workflow_name="comprehensive_analysis",
                analysis_types=[
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.QUALITY_ASSESSMENT,
                    AnalysisType.SENTIMENT_ANALYSIS,
                    AnalysisType.ENGAGEMENT_PREDICTION,
                    AnalysisType.STYLE_ANALYSIS
                ],
                execution_order=[
                    "content_classification",
                    "quality_assessment",
                    "sentiment_analysis",
                    "engagement_prediction",
                    "style_analysis"
                ],
                parallel_execution=True,
                error_handling="graceful_degradation",
                timeout_seconds=30,
                retry_policy={
                    "max_retries": 2,
                    "backoff_strategy": "linear",
                    "retry_delay": 5
                }
            ),
            
            "fast_analysis": AnalysisWorkflow(
                workflow_name="fast_analysis",
                analysis_types=[
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.SENTIMENT_ANALYSIS
                ],
                execution_order=[
                    "content_classification",
                    "sentiment_analysis"
                ],
                parallel_execution=True,
                error_handling="fail_fast",
                timeout_seconds=5,
                retry_policy={
                    "max_retries": 1,
                    "backoff_strategy": "none",
                    "retry_delay": 1
                }
            ),
            
            "business_analysis": AnalysisWorkflow(
                workflow_name="business_analysis",
                analysis_types=[
                    AnalysisType.ENGAGEMENT_PREDICTION,
                    AnalysisType.MONETIZATION_OPTIMIZATION,
                    AnalysisType.TREND_ANALYSIS,
                    AnalysisType.AUDIENCE_ANALYSIS
                ],
                execution_order=[
                    "engagement_prediction",
                    "monetization_optimization",
                    "trend_analysis",
                    "audience_analysis"
                ],
                parallel_execution=False,
                error_handling="comprehensive_retry",
                timeout_seconds=60,
                retry_policy={
                    "max_retries": 3,
                    "backoff_strategy": "exponential",
                    "retry_delay": 10
                }
            )
        }
        
        # Content Type Analysis Configuration
        self.content_type_analysis = {
            "text": {
                "primary_analyses": [
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.SENTIMENT_ANALYSIS,
                    AnalysisType.QUALITY_ASSESSMENT
                ],
                "secondary_analyses": [
                    AnalysisType.ENGAGEMENT_PREDICTION,
                    AnalysisType.TREND_ANALYSIS
                ],
                "accuracy_requirements": {
                    "content_classification": 0.95,
                    "sentiment_analysis": 0.92,
                    "quality_assessment": 0.88
                }
            },
            "image": {
                "primary_analyses": [
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.QUALITY_ASSESSMENT,
                    AnalysisType.STYLE_ANALYSIS
                ],
                "secondary_analyses": [
                    AnalysisType.ENGAGEMENT_PREDICTION,
                    AnalysisType.SIMILARITY_ANALYSIS
                ],
                "accuracy_requirements": {
                    "content_classification": 0.93,
                    "quality_assessment": 0.90,
                    "style_analysis": 0.88
                }
            },
            "video": {
                "primary_analyses": [
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.QUALITY_ASSESSMENT,
                    AnalysisType.ENGAGEMENT_PREDICTION
                ],
                "secondary_analyses": [
                    AnalysisType.STYLE_ANALYSIS,
                    AnalysisType.TREND_ANALYSIS,
                    AnalysisType.AUDIENCE_ANALYSIS
                ],
                "accuracy_requirements": {
                    "content_classification": 0.91,
                    "quality_assessment": 0.89,
                    "engagement_prediction": 0.85
                }
            },
            "audio": {
                "primary_analyses": [
                    AnalysisType.CONTENT_CLASSIFICATION,
                    AnalysisType.QUALITY_ASSESSMENT,
                    AnalysisType.SENTIMENT_ANALYSIS
                ],
                "secondary_analyses": [
                    AnalysisType.STYLE_ANALYSIS,
                    AnalysisType.ENGAGEMENT_PREDICTION
                ],
                "accuracy_requirements": {
                    "content_classification": 0.92,
                    "quality_assessment": 0.87,
                    "sentiment_analysis": 0.89
                }
            }
        }
        
        # Quality Assessment Configuration
        self.quality_assessment_config = {
            "technical_quality_weights": {
                "resolution": 0.25,
                "bitrate": 0.20,
                "compression": 0.15,
                "format_compliance": 0.20,
                "metadata_completeness": 0.20
            },
            "content_quality_weights": {
                "originality": 0.30,
                "creativity": 0.25,
                "relevance": 0.20,
                "engagement_potential": 0.25
            },
            "scoring_thresholds": {
                "excellent": 0.9,
                "good": 0.8,
                "average": 0.6,
                "poor": 0.4,
                "unacceptable": 0.2
            }
        }
        
        # Performance Settings
        self.performance_settings = {
            "max_concurrent_analyses": 50,
            "batch_processing_size": 100,
            "cache_results": True,
            "cache_duration_hours": 24,
            "real_time_processing": True,
            "priority_queue_enabled": True
        }
        
        # Accuracy Requirements by Use Case
        self.accuracy_requirements = {
            "copyright_detection": 0.99,
            "content_moderation": 0.97,
            "quality_scoring": 0.90,
            "engagement_prediction": 0.85,
            "trend_analysis": 0.80,
            "style_classification": 0.88
        }
        
        # Business Intelligence Settings
        self.business_intelligence = {
            "real_time_insights": True,
            "predictive_analytics": True,
            "recommendation_generation": True,
            "performance_benchmarking": True,
            "competitive_analysis": True,
            "market_trend_tracking": True
        }
        
        # Integration Settings
        self.integration_settings = {
            "api_endpoints_enabled": True,
            "webhook_notifications": True,
            "batch_api_enabled": True,
            "streaming_api_enabled": True,
            "real_time_websockets": True
        }
        
        # Monitoring and Alerting
        self.monitoring_config = {
            "performance_monitoring": True,
            "accuracy_monitoring": True,
            "drift_detection": True,
            "alert_thresholds": {
                "accuracy_drop_percent": 5,
                "processing_delay_seconds": 10,
                "error_rate_percent": 2
            },
            "dashboard_enabled": True,
            "automated_reporting": True
        }
    
    def get_analysis_model(self, model_name: str) -> Optional[AnalysisModel]:
        """Get analysis model configuration"""
        return self.analysis_models.get(model_name)
    
    def get_workflow(self, workflow_name: str) -> Optional[AnalysisWorkflow]:
        """Get analysis workflow configuration"""
        return self.analysis_workflows.get(workflow_name)
    
    def get_content_type_config(self, content_type: str) -> Optional[Dict[str, Any]]:
        """Get analysis configuration for content type"""
        return self.content_type_analysis.get(content_type)
    
    def get_required_accuracy(self, analysis_type: str) -> float:
        """Get required accuracy for analysis type"""
        return self.accuracy_requirements.get(analysis_type, 0.85)
    
    def is_real_time_analysis_enabled(self, analysis_type: AnalysisType) -> bool:
        """Check if real-time analysis is enabled for type"""
        real_time_types = [
            AnalysisType.CONTENT_CLASSIFICATION,
            AnalysisType.SENTIMENT_ANALYSIS,
            AnalysisType.QUALITY_ASSESSMENT
        ]
        return analysis_type in real_time_types and self.performance_settings["real_time_processing"]
    
    def get_processing_priority(self, analysis_type: AnalysisType) -> AnalysisPriority:
        """Get processing priority for analysis type"""
        priority_mapping = {
            AnalysisType.CONTENT_CLASSIFICATION: AnalysisPriority.HIGH,
            AnalysisType.QUALITY_ASSESSMENT: AnalysisPriority.HIGH,
            AnalysisType.SENTIMENT_ANALYSIS: AnalysisPriority.NORMAL,
            AnalysisType.ENGAGEMENT_PREDICTION: AnalysisPriority.NORMAL,
            AnalysisType.TREND_ANALYSIS: AnalysisPriority.LOW,
            AnalysisType.STYLE_ANALYSIS: AnalysisPriority.NORMAL
        }
        return priority_mapping.get(analysis_type, AnalysisPriority.NORMAL)
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete intelligent analysis configuration"""
        errors = []
        
        # Validate analysis models
        for model_name, model in self.analysis_models.items():
            if model.accuracy_target < 0.5 or model.accuracy_target > 1.0:
                errors.append(f"Invalid accuracy target for model '{model_name}'")
            if model.processing_time_ms <= 0:
                errors.append(f"Invalid processing time for model '{model_name}'")
        
        # Validate workflows
        for workflow_name, workflow in self.analysis_workflows.items():
            if not workflow.analysis_types:
                errors.append(f"Workflow '{workflow_name}' has no analysis types")
            if workflow.timeout_seconds <= 0:
                errors.append(f"Invalid timeout for workflow '{workflow_name}'")
        
        # Validate content type configurations
        for content_type, config in self.content_type_analysis.items():
            if not config.get("primary_analyses"):
                errors.append(f"Content type '{content_type}' has no primary analyses")
        
        return errors


# Global intelligent analysis settings instance
intelligent_analysis_settings = IntelligentAnalysisSettings()

__all__ = [
    "IntelligentAnalysisSettings",
    "intelligent_analysis_settings",
    "AnalysisType",
    "AnalysisEngine",
    "AnalysisPriority",
    "AccuracyLevel",
    "AnalysisModel",
    "AnalysisWorkflow",
    "QualityMetrics"
]