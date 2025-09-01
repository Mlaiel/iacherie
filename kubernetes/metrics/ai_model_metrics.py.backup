"""IA Influencer Agent - AI Model Performance Metrics
Advanced AI/ML model monitoring and optimization metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Multi-modal AI model performance tracking
- Real-time inference monitoring
- Model accuracy drift detection
- Feature engineering metrics
- Training pipeline optimization
- A/B testing for model versions
- Resource utilization for ML workloads
- Bias and fairness metrics
"""
import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, deque
import pickle
import base64

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from .config import get_metrics_config

logger = get_logger(__name__)
metrics_config = get_metrics_config()


class ModelType(Enum):
    """AI model types"""
    # Audio models
    AUDIO_FINGERPRINT = "audio_fingerprint"
    AUDIO_CLASSIFICATION = "audio_classification"
    SPEECH_RECOGNITION = "speech_recognition"
    MUSIC_GENERATION = "music_generation"
    
    # Video models
    VIDEO_FINGERPRINT = "video_fingerprint"
    VIDEO_CLASSIFICATION = "video_classification"
    OBJECT_DETECTION = "object_detection"
    SCENE_ANALYSIS = "scene_analysis"
    
    # Image models
    IMAGE_FINGERPRINT = "image_fingerprint"
    IMAGE_CLASSIFICATION = "image_classification"
    FACIAL_RECOGNITION = "facial_recognition"
    
    # Text models
    TEXT_FINGERPRINT = "text_fingerprint"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    LANGUAGE_DETECTION = "language_detection"
    CONTENT_MODERATION = "content_moderation"
    
    # Recommendation models
    CONTENT_RECOMMENDATION = "content_recommendation"
    COLLABORATION_MATCHING = "collaboration_matching"
    REVENUE_PREDICTION = "revenue_prediction"


class ModelStage(Enum):
    """Model development stages"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class InferenceStatus(Enum):
    """Inference status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ModelMetrics:
    """Core model performance metrics"""
    model_id: str
    model_type: ModelType
    model_version: str
    stage: ModelStage
    timestamp: datetime
    
    # Performance metrics
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    
    # Inference metrics
    inference_count: int
    avg_inference_time_ms: float
    p95_inference_time_ms: float
    p99_inference_time_ms: float
    
    # Resource metrics
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_usage_percent: Optional[float]
    
    # Business metrics
    prediction_confidence: Optional[float]
    drift_score: Optional[float]
    bias_score: Optional[float]
    
    # Custom metrics
    custom_metrics: Dict[str, Any]


@dataclass
class InferenceRecord:
    """Individual inference record"""
    inference_id: str
    model_id: str
    model_version: str
    tenant_id: str
    timestamp: datetime
    
    # Input data
    input_size_bytes: int
    input_features: Optional[Dict[str, Any]]
    
    # Output data
    prediction: Any
    confidence_score: Optional[float]
    
    # Performance
    inference_time_ms: float
    status: InferenceStatus
    error_message: Optional[str]
    
    # Resource usage
    cpu_usage_percent: Optional[float]
    memory_usage_mb: Optional[float]
    gpu_usage_percent: Optional[float]


@dataclass
class ModelTrainingMetrics:
    """Model training performance metrics"""
    training_id: str
    model_id: str
    model_version: str
    timestamp: datetime
    
    # Training data
    dataset_size: int
    training_samples: int
    validation_samples: int
    test_samples: int
    
    # Training performance
    training_time_hours: float
    epochs_completed: int
    final_loss: float
    final_accuracy: float
    
    # Resource usage
    total_cpu_hours: float
    total_gpu_hours: Optional[float]
    peak_memory_gb: float
    
    # Hyperparameters
    hyperparameters: Dict[str, Any]
    
    # Validation metrics
    validation_accuracy: float
    validation_loss: float
    overfitting_score: float


class AIModelMetricsCollector:
    """
    Advanced AI/ML model performance metrics collector
    
    Tracks model performance, inference metrics, training optimization,
    and provides insights for model improvement and resource optimization
    """
    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.logger = logger
        
        # Inference tracking
        self.inference_buffer: List[InferenceRecord] = []
        self.inference_times = defaultdict(lambda: deque(maxlen=1000))
        self.accuracy_tracking = defaultdict(lambda: deque(maxlen=100))
        
        # Model registry
        self.active_models = {}
        self.model_performance_cache = {}
        
        # Background processing
        self.processing_task = asyncio.create_task(self._start_background_processing())
    
    async def track_model_inference(
        self,
        model_id: str,
        model_version: str,
        tenant_id: str,
        input_size_bytes: int,
        prediction: Any,
        confidence_score: Optional[float],
        inference_time_ms: float,
        status: InferenceStatus = InferenceStatus.SUCCESS,
        error_message: Optional[str] = None,
        input_features: Optional[Dict[str, Any]] = None,
        resource_usage: Optional[Dict[str, float]] = None
    ) -> str:
        """Track individual model inference"""
        
        inference_id = f"inf_{int(datetime.now().timestamp())}_{model_id}"
        
        record = InferenceRecord(
            inference_id=inference_id,
            model_id=model_id,
            model_version=model_version,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc),
            input_size_bytes=input_size_bytes,
            input_features=input_features,
            prediction=prediction,
            confidence_score=confidence_score,
            inference_time_ms=inference_time_ms,
            status=status,
            error_message=error_message,
            cpu_usage_percent=resource_usage.get("cpu") if resource_usage else None,
            memory_usage_mb=resource_usage.get("memory_mb") if resource_usage else None,
            gpu_usage_percent=resource_usage.get("gpu") if resource_usage else None
        )
        
        # Store inference record
        await self._store_inference_record(record)
        
        # Update real-time tracking
        key = f"{model_id}:{model_version}"
        self.inference_times[key].append(inference_time_ms)
        
        if confidence_score is not None:
            self.accuracy_tracking[key].append(confidence_score)
        
        # Add to processing buffer
        self.inference_buffer.append(record)
        
        # Update real-time metrics in Redis
        await self._update_realtime_inference_metrics(record)
        
        return inference_id
    
    async def track_model_training(
        self,
        model_id: str,
        model_version: str,
        dataset_size: int,
        training_samples: int,
        validation_samples: int,
        test_samples: int,
        training_time_hours: float,
        epochs_completed: int,
        final_loss: float,
        final_accuracy: float,
        validation_accuracy: float,
        validation_loss: float,
        hyperparameters: Dict[str, Any],
        resource_usage: Optional[Dict[str, float]] = None
    ) -> str:
        """Track model training session"""
        
        training_id = f"train_{int(datetime.now().timestamp())}_{model_id}"
        
        # Calculate overfitting score
        overfitting_score = abs(final_accuracy - validation_accuracy) / max(final_accuracy, 0.01)
        
        metrics = ModelTrainingMetrics(
            training_id=training_id,
            model_id=model_id,
            model_version=model_version,
            timestamp=datetime.now(timezone.utc),
            dataset_size=dataset_size,
            training_samples=training_samples,
            validation_samples=validation_samples,
            test_samples=test_samples,
            training_time_hours=training_time_hours,
            epochs_completed=epochs_completed,
            final_loss=final_loss,
            final_accuracy=final_accuracy,
            validation_accuracy=validation_accuracy,
            validation_loss=validation_loss,
            overfitting_score=overfitting_score,
            hyperparameters=hyperparameters,
            total_cpu_hours=resource_usage.get("cpu_hours", 0) if resource_usage else 0,
            total_gpu_hours=resource_usage.get("gpu_hours") if resource_usage else None,
            peak_memory_gb=resource_usage.get("peak_memory_gb", 0) if resource_usage else 0
        )
        
        # Store training metrics
        await self._store_training_metrics(metrics)
        
        return training_id
    
    async def calculate_model_performance_metrics(
        self,
        model_id: str,
        model_version: str,
        time_range: str = "24h"
    ) -> ModelMetrics:
        """Calculate comprehensive model performance metrics"""
        
        try:
            # Parse time range
            if time_range == "1h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            elif time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            elif time_range == "30d":
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            async with get_database_session() as session:
                # Get inference metrics
                inference_stats = await session.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as inference_count,
                        AVG(inference_time_ms) as avg_inference_time,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY inference_time_ms) as p95_inference_time,
                        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY inference_time_ms) as p99_inference_time,
                        AVG(confidence_score) as avg_confidence,
                        AVG(cpu_usage_percent) as avg_cpu,
                        AVG(memory_usage_mb) as avg_memory,
                        AVG(gpu_usage_percent) as avg_gpu,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_inferences
                    FROM inference_records 
                    WHERE model_id = $1 AND model_version = $2 AND timestamp >= $3
                    """,
                    model_id, model_version, start_time
                )
                
                # Get latest training metrics
                training_stats = await session.fetchrow(
                    """
                    SELECT 
                        final_accuracy,
                        validation_accuracy,
                        final_loss,
                        overfitting_score
                    FROM training_metrics 
                    WHERE model_id = $1 AND model_version = $2
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    model_id, model_version
                )
                
                # Calculate performance metrics
                inference_count = inference_stats["inference_count"] or 0
                success_rate = (
                    inference_stats["successful_inferences"] / max(inference_count, 1)
                    if inference_count > 0 else 0
                )
                
                # Calculate drift score (mock implementation)
                drift_score = await self._calculate_drift_score(model_id, model_version, start_time)
                
                # Calculate bias score (mock implementation)  
                bias_score = await self._calculate_bias_score(model_id, model_version, start_time)
                
                # Determine model stage
                model_stage = await self._get_model_stage(model_id, model_version)
                
                # Get model type
                model_type = await self._get_model_type(model_id)
                
                return ModelMetrics(
                    model_id=model_id,
                    model_type=model_type,
                    model_version=model_version,
                    stage=model_stage,
                    timestamp=datetime.now(timezone.utc),
                    accuracy=float(training_stats["final_accuracy"]) if training_stats and training_stats["final_accuracy"] else None,
                    precision=None,  # Would calculate from confusion matrix
                    recall=None,     # Would calculate from confusion matrix
                    f1_score=None,   # Would calculate from precision/recall
                    inference_count=inference_count,
                    avg_inference_time_ms=float(inference_stats["avg_inference_time"] or 0),
                    p95_inference_time_ms=float(inference_stats["p95_inference_time"] or 0),
                    p99_inference_time_ms=float(inference_stats["p99_inference_time"] or 0),
                    cpu_usage_percent=float(inference_stats["avg_cpu"] or 0),
                    memory_usage_mb=float(inference_stats["avg_memory"] or 0),
                    gpu_usage_percent=float(inference_stats["avg_gpu"] or 0) if inference_stats["avg_gpu"] else None,
                    prediction_confidence=float(inference_stats["avg_confidence"] or 0),
                    drift_score=drift_score,
                    bias_score=bias_score,
                    custom_metrics={
                        "success_rate": success_rate,
                        "overfitting_score": float(training_stats["overfitting_score"]) if training_stats else None,
                        "inference_errors": inference_count - (inference_stats["successful_inferences"] or 0)
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error calculating model performance metrics: {e}")
            raise
    
    async def get_model_comparison_analysis(
        self,
        model_ids: List[str],
        metric_types: List[str] = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Compare performance across multiple models"""
        
        if metric_types is None:
            metric_types = ["accuracy", "inference_time", "resource_usage"]
        
        try:
            model_comparisons = {}
            
            for model_id in model_ids:
                # Get latest version for each model
                async with get_database_session() as session:
                    latest_version = await session.fetchval(
                        """
                        SELECT model_version 
                        FROM inference_records 
                        WHERE model_id = $1
                        ORDER BY timestamp DESC
                        LIMIT 1
                        """,
                        model_id
                    )
                
                if latest_version:
                    metrics = await self.calculate_model_performance_metrics(
                        model_id, latest_version, time_range
                    )
                    
                    model_comparisons[model_id] = {
                        "model_version": latest_version,
                        "metrics": asdict(metrics)
                    }
            
            # Calculate comparative analysis
            analysis = await self._analyze_model_performance_comparison(
                model_comparisons, metric_types
            )
            
            return {
                "time_range": time_range,
                "models_compared": len(model_ids),
                "model_comparisons": model_comparisons,
                "analysis": analysis,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model comparison analysis: {e}")
            return {}
    
    async def get_model_training_insights(
        self,
        model_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get training performance insights for model optimization"""
        
        try:
            async with get_database_session() as session:
                # Get training history
                training_history = await session.fetch(
                    """
                    SELECT 
                        training_id,
                        model_version,
                        timestamp,
                        training_time_hours,
                        epochs_completed,
                        final_accuracy,
                        validation_accuracy,
                        final_loss,
                        validation_loss,
                        overfitting_score,
                        hyperparameters,
                        total_cpu_hours,
                        total_gpu_hours,
                        peak_memory_gb
                    FROM training_metrics 
                    WHERE model_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                    """,
                    model_id, limit
                )
                
                if not training_history:
                    return {"error": "No training history found"}
                
                # Calculate training trends
                accuracies = [float(row["final_accuracy"]) for row in training_history]
                training_times = [float(row["training_time_hours"]) for row in training_history]
                
                # Best performing model
                best_model = max(training_history, key=lambda x: x["final_accuracy"])
                
                # Calculate efficiency metrics
                efficiency_scores = []
                for row in training_history:
                    if row["training_time_hours"] > 0:
                        efficiency = row["final_accuracy"] / row["training_time_hours"]
                        efficiency_scores.append(efficiency)
                
                return {
                    "model_id": model_id,
                    "training_sessions": len(training_history),
                    "best_performance": {
                        "model_version": best_model["model_version"],
                        "accuracy": float(best_model["final_accuracy"]),
                        "training_time_hours": float(best_model["training_time_hours"]),
                        "hyperparameters": json.loads(best_model["hyperparameters"]) if best_model["hyperparameters"] else {}
                    },
                    "trends": {
                        "accuracy_trend": "improving" if len(accuracies) > 1 and accuracies[0] > accuracies[-1] else "declining",
                        "avg_accuracy": statistics.mean(accuracies),
                        "avg_training_time": statistics.mean(training_times),
                        "avg_efficiency": statistics.mean(efficiency_scores) if efficiency_scores else 0
                    },
                    "optimization_recommendations": await self._generate_optimization_recommendations(
                        training_history
                    ),
                    "training_history": [
                        {
                            "model_version": row["model_version"],
                            "timestamp": row["timestamp"].isoformat(),
                            "accuracy": float(row["final_accuracy"]),
                            "validation_accuracy": float(row["validation_accuracy"]),
                            "training_time_hours": float(row["training_time_hours"]),
                            "overfitting_score": float(row["overfitting_score"])
                        }
                        for row in training_history
                    ],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting model training insights: {e}")
            return {"error": str(e)}
    
    async def get_realtime_inference_dashboard(
        self,
        model_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get real-time inference performance dashboard"""
        
        try:
            # Get recent inference data from Redis
            dashboard_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "models": []
            }
            
            # If specific model requested
            if model_id:
                model_keys = [f"inference_metrics:{model_id}:*"]
            else:
                # Get all model keys
                model_keys = await self.redis_manager.get_keys_pattern("inference_metrics:*")
            
            for key in model_keys[:10]:  # Limit to 10 models for performance
                try:
                    metrics_data = await self.redis_manager.list_range(key, -20, -1)  # Last 20 entries
                    
                    if metrics_data:
                        # Parse model info from key
                        key_parts = key.split(":")
                        if len(key_parts) >= 3:
                            current_model_id = key_parts[1]
                            current_model_version = key_parts[2] if len(key_parts) > 2 else "latest"
                            
                            # Calculate real-time metrics
                            recent_times = []
                            recent_confidences = []
                            success_count = 0
                            total_count = 0
                            
                            for entry in metrics_data:
                                try:
                                    data = json.loads(entry)
                                    recent_times.append(data.get("inference_time_ms", 0))
                                    
                                    if data.get("confidence_score"):
                                        recent_confidences.append(data["confidence_score"])
                                    
                                    if data.get("status") == "success":
                                        success_count += 1
                                    total_count += 1
                                except:
                                    continue
                            
                            # Calculate summary metrics
                            avg_response_time = statistics.mean(recent_times) if recent_times else 0
                            avg_confidence = statistics.mean(recent_confidences) if recent_confidences else 0
                            success_rate = (success_count / max(total_count, 1)) * 100
                            
                            dashboard_data["models"].append({
                                "model_id": current_model_id,
                                "model_version": current_model_version,
                                "recent_inferences": total_count,
                                "avg_response_time_ms": round(avg_response_time, 2),
                                "avg_confidence": round(avg_confidence, 3),
                                "success_rate_percent": round(success_rate, 1),
                                "status": "healthy" if success_rate > 95 and avg_response_time < 1000 else "warning"
                            })
                
                except Exception as e:
                    self.logger.error(f"Error processing model key {key}: {e}")
                    continue
            
            # Sort by recent activity
            dashboard_data["models"].sort(key=lambda x: x["recent_inferences"], reverse=True)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting real-time inference dashboard: {e}")
            return {"error": str(e)}
    
    async def _calculate_drift_score(
        self,
        model_id: str,
        model_version: str,
        start_time: datetime
    ) -> Optional[float]:
        """Calculate model drift score (mock implementation)"""
        # In production, this would compare current predictions with baseline
        # distributions to detect data drift
        return 0.05  # Mock low drift score
    
    async def _calculate_bias_score(
        self,
        model_id: str,
        model_version: str,
        start_time: datetime
    ) -> Optional[float]:
        """Calculate model bias score (mock implementation)"""
        # In production, this would analyze predictions across different
        # demographic groups to detect bias
        return 0.02  # Mock low bias score
    
    async def _get_model_stage(self, model_id: str, model_version: str) -> ModelStage:
        """Get model deployment stage"""
        # This would query model registry or deployment system
        return ModelStage.PRODUCTION  # Mock
    
    async def _get_model_type(self, model_id: str) -> ModelType:
        """Get model type from model registry"""
        # This would query model registry
        if "audio" in model_id.lower():
            return ModelType.AUDIO_FINGERPRINT
        elif "video" in model_id.lower():
            return ModelType.VIDEO_FINGERPRINT
        elif "image" in model_id.lower():
            return ModelType.IMAGE_FINGERPRINT
        elif "text" in model_id.lower():
            return ModelType.TEXT_FINGERPRINT
        else:
            return ModelType.CONTENT_RECOMMENDATION
    
    async def _analyze_model_performance_comparison(
        self,
        model_comparisons: Dict[str, Any],
        metric_types: List[str]
    ) -> Dict[str, Any]:
        """Analyze performance comparison across models"""
        
        analysis = {
            "best_performers": {},
            "performance_rankings": {},
            "insights": []
        }
        
        # Analyze each metric type
        for metric_type in metric_types:
            if metric_type == "accuracy":
                # Find best accuracy
                best_accuracy = 0
                best_model = None
                
                for model_id, data in model_comparisons.items():
                    accuracy = data["metrics"].get("accuracy")
                    if accuracy and accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model = model_id
                
                if best_model:
                    analysis["best_performers"]["accuracy"] = {
                        "model_id": best_model,
                        "score": best_accuracy
                    }
            
            elif metric_type == "inference_time":
                # Find fastest inference
                best_time = float('inf')
                best_model = None
                
                for model_id, data in model_comparisons.items():
                    inference_time = data["metrics"].get("avg_inference_time_ms")
                    if inference_time and inference_time < best_time:
                        best_time = inference_time
                        best_model = model_id
                
                if best_model:
                    analysis["best_performers"]["inference_time"] = {
                        "model_id": best_model,
                        "time_ms": best_time
                    }
        
        # Generate insights
        if len(model_comparisons) > 1:
            analysis["insights"].append("Multiple models available for comparison")
            
            # Check for performance consistency
            accuracies = [
                data["metrics"].get("accuracy", 0) 
                for data in model_comparisons.values()
                if data["metrics"].get("accuracy")
            ]
            
            if accuracies and max(accuracies) - min(accuracies) > 0.1:
                analysis["insights"].append("Significant accuracy variation detected across models")
        
        return analysis
    
    async def _generate_optimization_recommendations(
        self,
        training_history: List[Any]
    ) -> List[Dict[str, str]]:
        """Generate optimization recommendations based on training history"""
        
        recommendations = []
        
        # Check for overfitting
        for row in training_history[:3]:  # Check recent trainings
            if row["overfitting_score"] > 0.1:
                recommendations.append({
                    "type": "overfitting",
                    "message": "Model shows signs of overfitting. Consider regularization or early stopping.",
                    "priority": "high"
                })
                break
        
        # Check training efficiency
        avg_training_time = statistics.mean([
            float(row["training_time_hours"]) 
            for row in training_history
        ])
        
        if avg_training_time > 10:
            recommendations.append({
                "type": "efficiency",
                "message": "Training time is high. Consider data preprocessing or model architecture optimization.",
                "priority": "medium"
            })
        
        # Check accuracy plateau
        recent_accuracies = [
            float(row["final_accuracy"]) 
            for row in training_history[:5]
        ]
        
        if len(recent_accuracies) >= 3:
            accuracy_variance = statistics.variance(recent_accuracies)
            if accuracy_variance < 0.001:
                recommendations.append({
                    "type": "plateau",
                    "message": "Accuracy has plateaued. Consider hyperparameter tuning or architecture changes.",
                    "priority": "medium"
                })
        
        return recommendations
    
    async def _store_inference_record(self, record: InferenceRecord) -> None:
        """Store inference record in database"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    """
                    INSERT INTO inference_records 
                    (inference_id, model_id, model_version, tenant_id, timestamp,
                     input_size_bytes, input_features, prediction, confidence_score,
                     inference_time_ms, status, error_message, cpu_usage_percent,
                     memory_usage_mb, gpu_usage_percent)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    """,
                    record.inference_id,
                    record.model_id,
                    record.model_version,
                    record.tenant_id,
                    record.timestamp,
                    record.input_size_bytes,
                    json.dumps(record.input_features) if record.input_features else None,
                    json.dumps(record.prediction, default=str),
                    record.confidence_score,
                    record.inference_time_ms,
                    record.status.value,
                    record.error_message,
                    record.cpu_usage_percent,
                    record.memory_usage_mb,
                    record.gpu_usage_percent
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing inference record: {e}")
    
    async def _store_training_metrics(self, metrics: ModelTrainingMetrics) -> None:
        """Store training metrics in database"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    """
                    INSERT INTO training_metrics 
                    (training_id, model_id, model_version, timestamp, dataset_size,
                     training_samples, validation_samples, test_samples, training_time_hours,
                     epochs_completed, final_loss, final_accuracy, validation_accuracy,
                     validation_loss, overfitting_score, hyperparameters, total_cpu_hours,
                     total_gpu_hours, peak_memory_gb)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                    """,
                    metrics.training_id,
                    metrics.model_id,
                    metrics.model_version,
                    metrics.timestamp,
                    metrics.dataset_size,
                    metrics.training_samples,
                    metrics.validation_samples,
                    metrics.test_samples,
                    metrics.training_time_hours,
                    metrics.epochs_completed,
                    metrics.final_loss,
                    metrics.final_accuracy,
                    metrics.validation_accuracy,
                    metrics.validation_loss,
                    metrics.overfitting_score,
                    json.dumps(metrics.hyperparameters),
                    metrics.total_cpu_hours,
                    metrics.total_gpu_hours,
                    metrics.peak_memory_gb
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing training metrics: {e}")
    
    async def _update_realtime_inference_metrics(self, record: InferenceRecord) -> None:
        """Update real-time inference metrics in Redis"""
        try:
            # Store individual inference record
            await self.redis_manager.list_push(
                f"inference_metrics:{record.model_id}:{record.model_version}",
                json.dumps({
                    "inference_time_ms": record.inference_time_ms,
                    "confidence_score": record.confidence_score,
                    "status": record.status.value,
                    "timestamp": record.timestamp.isoformat()
                }),
                expire=3600  # 1 hour
            )
            
            # Update counters
            await self.redis_manager.increment(
                f"inference_count:{record.model_id}",
                expire=3600
            )
            
            if record.status == InferenceStatus.SUCCESS:
                await self.redis_manager.increment(
                    f"inference_success:{record.model_id}",
                    expire=3600
                )
            
        except Exception as e:
            self.logger.error(f"Error updating real-time inference metrics: {e}")
    
    async def _start_background_processing(self) -> None:
        """Start background processing tasks"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Process inference buffer
                if self.inference_buffer:
                    await self._process_inference_analytics()
                
                # Update model performance cache
                await self._update_model_performance_cache()
                
            except Exception as e:
                self.logger.error(f"Error in background processing: {e}")
                await asyncio.sleep(60)
    
    async def _process_inference_analytics(self) -> None:
        """Process inference analytics for insights"""
        try:
            # Group inferences by model for analysis
            model_groups = defaultdict(list)
            
            for record in self.inference_buffer:
                key = f"{record.model_id}:{record.model_version}"
                model_groups[key].append(record)
            
            # Analyze each model group
            for model_key, records in model_groups.items():
                # Calculate performance metrics
                # This could include trend analysis, anomaly detection, etc.
                pass
            
            # Clear buffer
            self.inference_buffer.clear()
            
        except Exception as e:
            self.logger.error(f"Error processing inference analytics: {e}")
    
    async def _update_model_performance_cache(self) -> None:
        """Update cached model performance metrics"""
        try:
            # Get list of active models
            async with get_database_session() as session:
                active_models = await session.fetch(
                    """
                    SELECT DISTINCT model_id, model_version 
                    FROM inference_records 
                    WHERE timestamp >= NOW() - INTERVAL '24 hours'
                    """
                )
            
            # Update cache for each model
            for model_row in active_models:
                model_id = model_row["model_id"]
                model_version = model_row["model_version"]
                
                try:
                    metrics = await self.calculate_model_performance_metrics(
                        model_id, model_version, "24h"
                    )
                    
                    # Cache metrics
                    cache_key = f"model_performance:{model_id}:{model_version}"
                    await self.redis_manager.set_json(
                        cache_key,
                        asdict(metrics),
                        expire=1800  # 30 minutes
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error updating cache for model {model_id}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error updating model performance cache: {e}")
