"""Machine Learning APIs Configuration - IA-Influencer Agent Platform
================================================================
Professional ML APIs configuration for AI model serving, training,
inference pipelines, and MLOps automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️ PROPRIÉTÉ EXCLUSIVE DE FAHED MLAIEL
Toute tentative de copie, vol ou réutilisation sans autorisation écrite
de Fahed Mlaiel (mlaiel@live.de) sera poursuivie en justice selon la loi allemande.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from decimal import Decimal


class MLFramework(Enum):
    """
Machine Learning frameworks enumeration."""

    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    HUGGING_FACE = "hugging_face"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"


class ModelType(Enum):
    """AI model types enumeration."""

    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    IMAGE_FINGERPRINT = "image_fingerprint"
    TEXT_SIMILARITY = "text_similarity"
    CONTENT_CLASSIFICATION = "content_classification"
    MUSIC_ANALYSIS = "music_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    FRAUD_DETECTION = "fraud_detection"


class DeploymentTarget(Enum):
    """Model deployment targets."""

    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    EDGE = "edge"
    MOBILE = "mobile"
    CLOUD = "cloud"


@dataclass
class ModelEndpointConfig:
    """ML model endpoint configuration."""
    model_name: str
    model_version: str
    framework: MLFramework
    model_type: ModelType
    endpoint_url: str
    api_key: str
    deployment_target: DeploymentTarget
    batch_size: int
    max_sequence_length: Optional[int]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    preprocessing_steps: List[str]
    postprocessing_steps: List[str]
    timeout_seconds: int
    retry_count: int
    rate_limit: int
    cache_enabled: bool
    cache_ttl: int
    monitoring_enabled: bool
    logging_level: str
    performance_metrics: List[str]
    health_check_endpoint: str
    scaling_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceConfig:
    """
ML inference configuration."""
    batch_inference: bool
    streaming_inference: bool
    real_time_inference: bool
    async_inference: bool
    parallel_processing: bool
    gpu_acceleration: bool
    mixed_precision: bool
    dynamic_batching: bool
    model_ensemble: bool
    a_b_testing: bool
    shadow_mode: bool
    canary_deployment: bool


@dataclass
class MLPipelineConfig:
    """
ML pipeline configuration."""
    pipeline_name: str
    stages: List[str]
    input_sources: List[str]
    output_destinations: List[str]
    data_validation: bool
    feature_engineering: bool
    model_training: bool
    model_evaluation: bool
    model_deployment: bool
    monitoring: bool
    alerting: bool
    auto_scaling: bool
    cost_optimization: bool


class MLAPIsConfig:
    """
Professional Machine Learning APIs configuration."""
    
    def __init__(self):
        """
Initialize ML APIs configuration."""
        self.model_endpoints = self._get_model_endpoints()
        self.inference_configs = self._get_inference_configs()
        self.pipeline_configs = self._get_pipeline_configs()
        self.serving_configs = self._get_serving_configs()
        self.training_configs = self._get_training_configs()
        self.monitoring_configs = self._get_monitoring_configs()
    
    def _get_model_endpoints(self) -> Dict[str, ModelEndpointConfig]:
        """
Get ML model endpoints configuration."""
        return {
            'audio_fingerprint_v1': ModelEndpointConfig(
                model_name="audio_fingerprint",
                model_version="v1.2.0",
                framework=MLFramework.PYTORCH,
                model_type=ModelType.AUDIO_FINGERPRINT,
                endpoint_url=os.getenv("ML_AUDIO_FINGERPRINT_URL", ""),
                api_key=os.getenv("ML_AUDIO_FINGERPRINT_API_KEY", ""),
                deployment_target=DeploymentTarget.GPU,
                batch_size=32,
                max_sequence_length=None,
                input_schema={
                    "audio_data": {"type": "tensor", "shape": [None, 22050], "dtype": "float32"},
                    "sample_rate": {"type": "integer", "default": 22050},
                    "duration": {"type": "float", "max": 600.0}
                },
                output_schema={
                    "fingerprint": {"type": "tensor", "shape": [1024], "dtype": "float32"},
                    "confidence_score": {"type": "float", "range": [0.0, 1.0]},
                    "processing_time": {"type": "float"}
                },
                preprocessing_steps=["normalize_audio", "extract_features", "pad_sequence"],
                postprocessing_steps=["normalize_fingerprint", "calculate_confidence"],
                timeout_seconds=30,
                retry_count=3,
                rate_limit=1000,
                cache_enabled=True,
                cache_ttl=3600,
                monitoring_enabled=True,
                logging_level="INFO",
                performance_metrics=["latency", "throughput", "accuracy", "gpu_utilization"],
                health_check_endpoint="/health",
                scaling_config={
                    "min_instances": 2,
                    "max_instances": 10,
                    "target_cpu_utilization": 70,
                    "scale_up_cooldown": 300,
                    "scale_down_cooldown": 600
                }
            ),
            
            'video_fingerprint_v1': ModelEndpointConfig(
                model_name="video_fingerprint",
                model_version="v1.1.0",
                framework=MLFramework.TENSORFLOW,
                model_type=ModelType.VIDEO_FINGERPRINT,
                endpoint_url=os.getenv("ML_VIDEO_FINGERPRINT_URL", ""),
                api_key=os.getenv("ML_VIDEO_FINGERPRINT_API_KEY", ""),
                deployment_target=DeploymentTarget.GPU,
                batch_size=16,
                max_sequence_length=None,
                input_schema={
                    "video_frames": {"type": "tensor", "shape": [None, 224, 224, 3], "dtype": "uint8"},
                    "frame_rate": {"type": "integer", "default": 30},
                    "duration": {"type": "float", "max": 3600.0}
                },
                output_schema={
                    "fingerprint": {"type": "tensor", "shape": [2048], "dtype": "float32"},
                    "frame_fingerprints": {"type": "list", "item_type": "tensor"},
                    "scene_changes": {"type": "list", "item_type": "float"},
                    "confidence_score": {"type": "float", "range": [0.0, 1.0]}
                },
                preprocessing_steps=["resize_frames", "normalize_pixels", "extract_keyframes"],
                postprocessing_steps=["aggregate_features", "normalize_fingerprint"],
                timeout_seconds=60,
                retry_count=2,
                rate_limit=500,
                cache_enabled=True,
                cache_ttl=1800,
                monitoring_enabled=True,
                logging_level="INFO",
                performance_metrics=["latency", "throughput", "accuracy", "memory_usage"],
                health_check_endpoint="/health",
                scaling_config={
                    "min_instances": 1,
                    "max_instances": 5,
                    "target_gpu_utilization": 80,
                    "scale_up_cooldown": 600,
                    "scale_down_cooldown": 900
                }
            ),
            
            'text_similarity_v1': ModelEndpointConfig(
                model_name="text_similarity",
                model_version="v1.0.0",
                framework=MLFramework.HUGGING_FACE,
                model_type=ModelType.TEXT_SIMILARITY,
                endpoint_url=os.getenv("ML_TEXT_SIMILARITY_URL", ""),
                api_key=os.getenv("ML_TEXT_SIMILARITY_API_KEY", ""),
                deployment_target=DeploymentTarget.CPU,
                batch_size=64,
                max_sequence_length=512,
                input_schema={
                    "text1": {"type": "string", "max_length": 10000},
                    "text2": {"type": "string", "max_length": 10000},
                    "language": {"type": "string", "default": "auto"}
                },
                output_schema={
                    "similarity_score": {"type": "float", "range": [0.0, 1.0]},
                    "embedding1": {"type": "tensor", "shape": [768], "dtype": "float32"},
                    "embedding2": {"type": "tensor", "shape": [768], "dtype": "float32"},
                    "confidence": {"type": "float", "range": [0.0, 1.0]}
                },
                preprocessing_steps=["tokenize", "truncate", "add_special_tokens"],
                postprocessing_steps=["calculate_similarity", "normalize_scores"],
                timeout_seconds=15,
                retry_count=3,
                rate_limit=2000,
                cache_enabled=True,
                cache_ttl=7200,
                monitoring_enabled=True,
                logging_level="INFO",
                performance_metrics=["latency", "throughput", "accuracy"],
                health_check_endpoint="/health",
                scaling_config={
                    "min_instances": 3,
                    "max_instances": 15,
                    "target_cpu_utilization": 60,
                    "scale_up_cooldown": 180,
                    "scale_down_cooldown": 300
                }
            ),
            
            'music_analysis_v1': ModelEndpointConfig(
                model_name="music_analysis",
                model_version="v1.3.0",
                framework=MLFramework.PYTORCH,
                model_type=ModelType.MUSIC_ANALYSIS,
                endpoint_url=os.getenv("ML_MUSIC_ANALYSIS_URL", ""),
                api_key=os.getenv("ML_MUSIC_ANALYSIS_API_KEY", ""),
                deployment_target=DeploymentTarget.GPU,
                batch_size=8,
                max_sequence_length=None,
                input_schema={
                    "audio_data": {"type": "tensor", "shape": [None, 44100], "dtype": "float32"},
                    "analysis_type": {"type": "string", "enum": ["full", "quick", "detailed"]},
                    "extract_features": {"type": "list", "item_type": "string"}
                },
                output_schema={
                    "genre": {"type": "string"},
                    "mood": {"type": "string"},
                    "tempo": {"type": "float"},
                    "key": {"type": "string"},
                    "energy": {"type": "float", "range": [0.0, 1.0]},
                    "danceability": {"type": "float", "range": [0.0, 1.0]},
                    "valence": {"type": "float", "range": [0.0, 1.0]},
                    "acoustic_features": {"type": "dict"},
                    "harmonic_analysis": {"type": "dict"}
                },
                preprocessing_steps=["resample_audio", "normalize_volume", "extract_features"],
                postprocessing_steps=["classify_genre", "analyze_mood", "calculate_metrics"],
                timeout_seconds=45,
                retry_count=2,
                rate_limit=300,
                cache_enabled=True,
                cache_ttl=1800,
                monitoring_enabled=True,
                logging_level="INFO",
                performance_metrics=["latency", "accuracy", "feature_extraction_time"],
                health_check_endpoint="/health",
                scaling_config={
                    "min_instances": 2,
                    "max_instances": 8,
                    "target_gpu_utilization": 75,
                    "scale_up_cooldown": 300,
                    "scale_down_cooldown": 600
                }
            )
        }
    
    def _get_inference_configs(self) -> Dict[str, InferenceConfig]:
        """Get inference configurations."""
        return {
            'real_time': InferenceConfig(
                batch_inference=False,
                streaming_inference=True,
                real_time_inference=True,
                async_inference=False,
                parallel_processing=True,
                gpu_acceleration=True,
                mixed_precision=True,
                dynamic_batching=True,
                model_ensemble=False,
                a_b_testing=False,
                shadow_mode=False,
                canary_deployment=False
            ),
            
            'batch_processing': InferenceConfig(
                batch_inference=True,
                streaming_inference=False,
                real_time_inference=False,
                async_inference=True,
                parallel_processing=True,
                gpu_acceleration=True,
                mixed_precision=True,
                dynamic_batching=True,
                model_ensemble=True,
                a_b_testing=False,
                shadow_mode=False,
                canary_deployment=False
            ),
            
            'production': InferenceConfig(
                batch_inference=True,
                streaming_inference=True,
                real_time_inference=True,
                async_inference=True,
                parallel_processing=True,
                gpu_acceleration=True,
                mixed_precision=True,
                dynamic_batching=True,
                model_ensemble=True,
                a_b_testing=True,
                shadow_mode=True,
                canary_deployment=True
            )
        }
    
    def _get_pipeline_configs(self) -> Dict[str, MLPipelineConfig]:
        """
Get ML pipeline configurations."""
        return {
            'content_protection_pipeline': MLPipelineConfig(
                pipeline_name="content_protection",
                stages=[
                    "data_ingestion",
                    "preprocessing",
                    "feature_extraction",
                    "fingerprint_generation",
                    "similarity_matching",
                    "violation_detection",
                    "notification"
                ],
                input_sources=["s3_uploads", "api_submissions", "crawled_content"],
                output_destinations=["postgresql", "elasticsearch", "notification_service"],
                data_validation=True,
                feature_engineering=True,
                model_training=False,
                model_evaluation=True,
                model_deployment=False,
                monitoring=True,
                alerting=True,
                auto_scaling=True,
                cost_optimization=True
            ),
            
            'music_analysis_pipeline': MLPipelineConfig(
                pipeline_name="music_analysis",
                stages=[
                    "audio_ingestion",
                    "audio_preprocessing",
                    "feature_extraction",
                    "genre_classification",
                    "mood_analysis",
                    "acoustic_analysis",
                    "result_aggregation"
                ],
                input_sources=["spotify_api", "user_uploads", "streaming_services"],
                output_destinations=["postgresql", "redis_cache", "analytics_service"],
                data_validation=True,
                feature_engineering=True,
                model_training=True,
                model_evaluation=True,
                model_deployment=True,
                monitoring=True,
                alerting=True,
                auto_scaling=True,
                cost_optimization=True
            )
        }
    
    def _get_serving_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get model serving configurations."""
        return {
            'tensorflow_serving': {
                'base_path': '/models',
                'model_config_file': '/config/models.config',
                'monitoring_config_file': '/config/monitoring.config',
                'batching_parameters': {
                    'max_batch_size': 32,
                    'batch_timeout_micros': 100000,
                    'max_enqueued_batches': 100,
                    'num_batch_threads': 4
                },
                'model_server_config': {
                    'rest_api_port': 8501,
                    'grpc_port': 8500,
                    'enable_batching': True,
                    'enable_model_warmup': True
                }
            },
            
            'torchserve': {
                'model_store': '/models',
                'workflow_store': '/workflows',
                'metrics_config': '/config/metrics.yaml',
                'default_workers_per_model': 2,
                'max_workers': 8,
                'batch_size': 16,
                'max_batch_delay': 100,
                'response_timeout': 300,
                'management_address': 'http://0.0.0.0:8081',
                'inference_address': 'http://0.0.0.0:8080',
                'metrics_address': 'http://0.0.0.0:8082'
            },
            
            'triton_inference_server': {
                'model_repository': '/models',
                'backend_directory': '/opt/tritonserver/backends',
                'min_supported_compute_capability': '6.0',
                'strict_model_config': True,
                'strict_readiness': True,
                'http_port': 8000,
                'grpc_port': 8001,
                'metrics_port': 8002,
                'allow_http': True,
                'allow_grpc': True,
                'allow_metrics': True,
                'allow_gpu_metrics': True,
                'allow_cpu_metrics': True
            }
        }
    
    def _get_training_configs(self) -> Dict[str, Dict[str, Any]]:
        """
Get model training configurations."""
        return {
            'distributed_training': {
                'strategy': 'mirrored',
                'num_gpus': 4,
                'num_workers': 2,
                'batch_size_per_replica': 32,
                'global_batch_size': 128,
                'learning_rate': 0.001,
                'learning_rate_schedule': 'cosine_decay',
                'optimizer': 'adamw',
                'gradient_clipping': 1.0,
                'mixed_precision': True,
                'checkpoint_frequency': 1000,
                'evaluation_frequency': 500
            },
            
            'hyperparameter_tuning': {
                'algorithm': 'bayesian_optimization',
                'max_trials': 100,
                'objective': 'val_accuracy',
                'direction': 'maximize',
                'hyperparameters': {
                    'learning_rate': {'min_value': 1e-5, 'max_value': 1e-2, 'sampling': 'log'},
                    'batch_size': {'values': [16, 32, 64, 128]},
                    'dropout_rate': {'min_value': 0.1, 'max_value': 0.5, 'step': 0.1},
                    'hidden_units': {'min_value': 64, 'max_value': 512, 'step': 64}
                },
                'early_stopping': {
                    'patience': 10,
                    'min_delta': 0.001,
                    'restore_best_weights': True
                }
            }
        }
    
    def _get_monitoring_configs(self) -> Dict[str, Dict[str, Any]]:
        """
Get ML monitoring configurations."""
        return {
            'model_monitoring': {
                'metrics': [
                    'prediction_latency',
                    'prediction_accuracy',
                    'data_drift',
                    'model_drift',
                    'feature_importance',
                    'prediction_distribution'
                ],
                'thresholds': {
                    'max_latency_ms': 1000,
                    'min_accuracy': 0.85,
                    'max_drift_score': 0.3,
                    'max_error_rate': 0.05
                },
                'alerting': {
                    'channels': ['email', 'slack', 'pagerduty'],
                    'severity_levels': ['low', 'medium', 'high', 'critical'],
                    'escalation_rules': {
                        'response_time': 300,
                        'auto_rollback': True,
                        'canary_analysis': True
                    }
                }
            },
            
            'data_monitoring': {
                'quality_checks': [
                    'null_values',
                    'data_types',
                    'value_ranges',
                    'schema_validation',
                    'duplicate_detection'
                ],
                'drift_detection': {
                    'methods': ['ks_test', 'chi_square', 'population_stability_index'],
                    'sensitivity': 0.05,
                    'window_size': 1000,
                    'baseline_period': '7d'
                },
                'profiling': {
                    'statistical_metrics': True,
                    'correlation_analysis': True,
                    'outlier_detection': True,
                    'feature_importance': True
                }
            }
        }
    
    def get_model_endpoint(self, model_name: str) -> Optional[ModelEndpointConfig]:
        """
Get model endpoint configuration."""
        return self.model_endpoints.get(model_name)
    
    def get_inference_config(self, config_type: str) -> Optional[InferenceConfig]:
        """
Get inference configuration."""
        return self.inference_configs.get(config_type)
    
    def get_pipeline_config(self, pipeline_name: str) -> Optional[MLPipelineConfig]:
        """
Get ML pipeline configuration."""
        return self.pipeline_configs.get(pipeline_name)


# Global configuration instance
ml_apis_config = MLAPIsConfig()


def get_ml_model_endpoint(model_name: str) -> Optional[ModelEndpointConfig]:
    """
Get ML model endpoint configuration."""
    return ml_apis_config.get_model_endpoint(model_name)


def get_ml_inference_config(config_type: str = 'production') -> Optional[InferenceConfig]:
    """
Get ML inference configuration."""
    return ml_apis_config.get_inference_config(config_type)


def get_ml_pipeline_config(pipeline_name: str) -> Optional[MLPipelineConfig]:
    """
Get ML pipeline configuration."""
    return ml_apis_config.get_pipeline_config(pipeline_name)
