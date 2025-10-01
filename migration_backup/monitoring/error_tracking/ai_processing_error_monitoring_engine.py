"""
AI Processing Error Monitoring Engine for IA Chéries Creator Economy
Advanced error monitoring specialized for AI processing workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import json
import threading

# Conditional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """AI model types for specialized monitoring"""
    TEXT_GENERATION = "text_generation"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_PROCESSING = "image_processing"
    CONTENT_ANALYSIS = "content_analysis"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    CONTENT_PROTECTION = "content_protection"
    RECOMMENDATION = "recommendation"
    MONETIZATION_ANALYSIS = "monetization_analysis"


class AIProcessingStage(Enum):
    """AI processing pipeline stages"""
    PREPROCESSING = "preprocessing"
    MODEL_INFERENCE = "model_inference"
    POSTPROCESSING = "postprocessing"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    CACHING = "caching"


class AIErrorSeverity(Enum):
    """AI-specific error severity levels"""
    MODEL_FAILURE = "model_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    QUALITY_DEGRADATION = "quality_degradation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INPUT_VALIDATION_ERROR = "input_validation_error"
    OUTPUT_CORRUPTION = "output_corruption"


@dataclass
class AIErrorEvent:
    """AI-specific error event data"""
    error_id: str
    timestamp: datetime
    model_name: str
    model_type: AIModelType
    processing_stage: AIProcessingStage
    error_type: str
    error_message: str
    error_severity: AIErrorSeverity
    creator_id: str
    creator_tier: str
    content_type: str
    input_metadata: Dict[str, Any]
    processing_context: Dict[str, Any]
    system_metrics: Dict[str, Any]
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


class AIProcessingErrorMonitoringEngine:
    """
    Advanced AI Processing Error Monitoring Engine
    Specialized monitoring for AI/ML workflows in Creator Economy
    """
    
    def __init__(self, 
                 monitoring_interval: int = 30,
                 max_error_history: int = 10000,
                 performance_window: int = 3600):
        """
        Initialize AI Processing Error Monitoring Engine
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_error_history: Maximum number of error events to keep
            performance_window: Performance analysis window in seconds
        """
        self.monitoring_interval = monitoring_interval
        self.max_error_history = max_error_history
        self.performance_window = performance_window
        
        # Error tracking storage
        self.ai_error_events: List[AIErrorEvent] = []
        self.model_health_status: Dict[str, Dict[str, Any]] = {}
        
        # AI-specific error patterns
        self.known_ai_patterns = self._initialize_ai_patterns()
        self.model_specific_thresholds = self._initialize_model_thresholds()
        
        # Recovery strategies
        self.recovery_strategies = self._initialize_recovery_strategies()
        
        logger.info("AI Processing Error Monitoring Engine initialized")
    
    async def monitor_ai_error(self, 
                              error: Exception,
                              creator_context: Any) -> Dict[str, Any]:
        """
        Monitor and analyze AI processing error
        
        Args:
            error: Exception that occurred
            creator_context: Creator context information
            
        Returns:
            AI error monitoring analysis
        """
        try:
            # Extract AI processing context
            ai_context = creator_context.ai_processing_context or {}
            
            # Create AI error event
            ai_error_event = self._create_ai_error_event(error, creator_context, ai_context)
            
            # Store error event
            self.ai_error_events.append(ai_error_event)
            self._cleanup_old_errors()
            
            # Analyze AI-specific error
            analysis = await self._analyze_ai_error(ai_error_event, creator_context)
            
            # Update model health status
            await self._update_model_health(ai_error_event)
            
            # Attempt automatic recovery if enabled
            recovery_result = await self._attempt_ai_recovery(ai_error_event, creator_context)
            
            # Generate AI-specific recommendations
            recommendations = await self._generate_ai_recommendations(
                ai_error_event, analysis, creator_context
            )
            
            return {
                "ai_error_analysis": analysis,
                "model_health_impact": self._assess_model_health_impact(ai_error_event),
                "performance_impact": self._assess_performance_impact(ai_error_event),
                "recovery_analysis": recovery_result,
                "ai_recommendations": recommendations,
                "monitoring_metadata": {
                    "error_id": ai_error_event.error_id,
                    "monitoring_engine": "ai_processing",
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"AI error monitoring failed: {e}")
            return {"error": str(e), "fallback_analysis": self._fallback_ai_analysis(error)}
    
    def _create_ai_error_event(self, 
                              error: Exception,
                              creator_context: Any,
                              ai_context: Dict[str, Any]) -> AIErrorEvent:
        """Create AI error event from exception and context"""
        error_id = f"ai_{creator_context.creator_id}_{int(time.time() * 1000)}"
        
        # Determine AI processing details
        model_name = ai_context.get('model_name', 'unknown')
        model_type = self._determine_model_type(model_name, creator_context)
        processing_stage = self._determine_processing_stage(ai_context, creator_context)
        error_severity = self._classify_ai_error_severity(error, ai_context)
        
        # Collect system metrics
        system_metrics = self._collect_system_metrics()
        
        return AIErrorEvent(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            model_name=model_name,
            model_type=model_type,
            processing_stage=processing_stage,
            error_type=error.__class__.__name__,
            error_message=str(error),
            error_severity=error_severity,
            creator_id=creator_context.creator_id,
            creator_tier=creator_context.creator_tier.value,
            content_type=creator_context.content_type,
            input_metadata=ai_context.get('input_metadata', {}),
            processing_context=ai_context,
            system_metrics=system_metrics,
            stack_trace=self._extract_stack_trace(error),
            recovery_attempted=False,
            recovery_successful=False
        )
    
    async def _analyze_ai_error(self, 
                               ai_error_event: AIErrorEvent,
                               creator_context: Any) -> Dict[str, Any]:
        """Comprehensive AI error analysis"""
        analysis = {
            "error_classification": self._classify_ai_error_type(ai_error_event),
            "model_specific_analysis": self._analyze_model_specific_error(ai_error_event),
            "processing_stage_analysis": self._analyze_processing_stage_error(ai_error_event),
            "resource_utilization_analysis": self._analyze_resource_utilization(ai_error_event),
            "quality_impact_analysis": self._analyze_quality_impact(ai_error_event),
            "creator_tier_impact": self._analyze_creator_tier_ai_impact(ai_error_event),
            "content_type_correlation": self._analyze_content_type_correlation(ai_error_event),
            "pattern_matching": await self._match_known_ai_patterns(ai_error_event),
            "root_cause_analysis": await self._perform_root_cause_analysis(ai_error_event)
        }
        
        return analysis
    
    def _classify_ai_error_type(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Classify AI error into specific categories"""
        error_message = ai_error_event.error_message.lower()
        
        classification = {
            "primary_category": "unknown",
            "secondary_categories": [],
            "criticality": "medium",
            "immediate_action_required": False
        }
        
        # Model-related errors
        if any(keyword in error_message for keyword in ["model", "inference", "prediction"]):
            classification["primary_category"] = "model_error"
            if any(keyword in error_message for keyword in ["load", "initialize", "not found"]):
                classification["secondary_categories"].append("model_loading")
                classification["criticality"] = "high"
            elif any(keyword in error_message for keyword in ["timeout", "hung", "frozen"]):
                classification["secondary_categories"].append("model_timeout")
                classification["immediate_action_required"] = True
        
        # Resource-related errors
        elif any(keyword in error_message for keyword in ["memory", "gpu", "cuda", "resource"]):
            classification["primary_category"] = "resource_error"
            classification["criticality"] = "high"
            if "out of memory" in error_message or "oom" in error_message:
                classification["secondary_categories"].append("memory_exhaustion")
                classification["immediate_action_required"] = True
        
        # Input/Output errors
        elif any(keyword in error_message for keyword in ["input", "output", "format", "validation"]):
            classification["primary_category"] = "io_error"
            classification["criticality"] = "medium"
            if "validation" in error_message:
                classification["secondary_categories"].append("input_validation")
        
        # Quality-related errors
        elif any(keyword in error_message for keyword in ["quality", "corrupt", "degraded"]):
            classification["primary_category"] = "quality_error"
            classification["criticality"] = "high"
            classification["secondary_categories"].append("quality_degradation")
        
        return classification
    
    def _analyze_model_specific_error(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze error specific to the AI model"""
        model_name = ai_error_event.model_name
        model_type = ai_error_event.model_type
        
        # Get model-specific thresholds and characteristics
        model_config = self.model_specific_thresholds.get(model_name, {})
        
        analysis = {
            "model_name": model_name,
            "model_type": model_type.value,
            "model_characteristics": model_config.get("characteristics", {}),
            "error_context": {
                "processing_stage": ai_error_event.processing_stage.value,
                "input_size": ai_error_event.input_metadata.get("size", "unknown"),
                "expected_processing_time": model_config.get("expected_processing_time", "unknown")
            },
            "model_health_impact": self._assess_model_health_impact(ai_error_event),
            "model_specific_recommendations": self._get_model_specific_recommendations(
                model_name, ai_error_event
            )
        }
        
        return analysis
    
    def _analyze_processing_stage_error(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze error based on processing stage"""
        stage = ai_error_event.processing_stage
        
        stage_analysis = {
            "processing_stage": stage.value,
            "stage_criticality": self._get_stage_criticality(stage),
            "downstream_impact": self._assess_downstream_impact(stage),
            "recovery_complexity": self._assess_recovery_complexity(stage),
            "stage_specific_context": {}
        }
        
        # Stage-specific analysis
        if stage == AIProcessingStage.PREPROCESSING:
            stage_analysis["stage_specific_context"] = {
                "input_validation_status": "failed" if "validation" in ai_error_event.error_message.lower() else "unknown",
                "data_formatting_issues": "format" in ai_error_event.error_message.lower(),
                "preprocessing_pipeline_integrity": "compromised"
            }
        elif stage == AIProcessingStage.MODEL_INFERENCE:
            stage_analysis["stage_specific_context"] = {
                "model_load_status": "failed" if "load" in ai_error_event.error_message.lower() else "unknown",
                "inference_timeout": "timeout" in ai_error_event.error_message.lower(),
                "model_response_validity": "invalid"
            }
        elif stage == AIProcessingStage.POSTPROCESSING:
            stage_analysis["stage_specific_context"] = {
                "output_formatting_issues": "format" in ai_error_event.error_message.lower(),
                "quality_assurance_status": "failed",
                "output_validation_status": "failed"
            }
        
        return stage_analysis
    
    def _analyze_resource_utilization(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze resource utilization patterns"""
        system_metrics = ai_error_event.system_metrics
        
        analysis = {
            "cpu_utilization": system_metrics.get("cpu_percent", 0),
            "memory_utilization": system_metrics.get("memory_percent", 0),
            "gpu_utilization": system_metrics.get("gpu_utilization", 0),
            "resource_constraints": [],
            "bottleneck_analysis": {}
        }
        
        # Identify resource constraints
        if analysis["cpu_utilization"] > 90:
            analysis["resource_constraints"].append("cpu_exhaustion")
        if analysis["memory_utilization"] > 90:
            analysis["resource_constraints"].append("memory_exhaustion")
        if analysis["gpu_utilization"] > 95:
            analysis["resource_constraints"].append("gpu_exhaustion")
        
        # Bottleneck analysis
        max_utilization = max(
            analysis["cpu_utilization"],
            analysis["memory_utilization"],
            analysis["gpu_utilization"]
        )
        
        if max_utilization == analysis["gpu_utilization"]:
            analysis["bottleneck_analysis"]["primary_bottleneck"] = "gpu"
        elif max_utilization == analysis["memory_utilization"]:
            analysis["bottleneck_analysis"]["primary_bottleneck"] = "memory"
        else:
            analysis["bottleneck_analysis"]["primary_bottleneck"] = "cpu"
        
        return analysis
    
    def _analyze_quality_impact(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze impact on output quality"""
        quality_analysis = {
            "quality_degradation_risk": "unknown",
            "output_reliability": "compromised",
            "creator_experience_impact": "negative",
            "business_impact": {}
        }
        
        # Assess quality degradation risk based on error type and stage
        if ai_error_event.processing_stage in [AIProcessingStage.MODEL_INFERENCE, AIProcessingStage.POSTPROCESSING]:
            quality_analysis["quality_degradation_risk"] = "high"
        elif "quality" in ai_error_event.error_message.lower():
            quality_analysis["quality_degradation_risk"] = "critical"
        
        # Creator tier impact on quality expectations
        creator_tier = ai_error_event.creator_tier
        if creator_tier in ["professional", "enterprise"]:
            quality_analysis["creator_experience_impact"] = "severely_negative"
            quality_analysis["business_impact"] = {
                "sla_breach_risk": "high",
                "reputation_damage": "medium",
                "churn_risk": "high"
            }
        
        return quality_analysis
    
    def _analyze_creator_tier_ai_impact(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze AI error impact specific to creator tier"""
        creator_tier = ai_error_event.creator_tier
        
        tier_impact = {
            "tier": creator_tier,
            "impact_severity": "medium",
            "sla_implications": {},
            "support_requirements": {},
            "recovery_priority": "normal"
        }
        
        # Tier-specific impact assessment
        if creator_tier in ["professional", "enterprise"]:
            tier_impact["impact_severity"] = "high"
            tier_impact["sla_implications"] = {
                "sla_breach_risk": "high",
                "compensation_required": True,
                "escalation_needed": True
            }
            tier_impact["support_requirements"] = {
                "priority_support": True,
                "dedicated_engineer": True,
                "status_updates": "real_time"
            }
            tier_impact["recovery_priority"] = "critical"
        
        return tier_impact
    
    def _analyze_content_type_correlation(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Analyze correlation between content type and AI error"""
        content_type = ai_error_event.content_type
        model_type = ai_error_event.model_type
        
        # Content type and model compatibility
        compatibility_matrix = {
            "audio": {
                AIModelType.AUDIO_PROCESSING: "high",
                AIModelType.CONTENT_ANALYSIS: "medium",
                AIModelType.QUALITY_ENHANCEMENT: "high"
            },
            "video": {
                AIModelType.VIDEO_PROCESSING: "high",
                AIModelType.CONTENT_ANALYSIS: "high",
                AIModelType.QUALITY_ENHANCEMENT: "high"
            },
            "image": {
                AIModelType.IMAGE_PROCESSING: "high",
                AIModelType.CONTENT_ANALYSIS: "medium",
                AIModelType.QUALITY_ENHANCEMENT: "medium"
            },
            "text": {
                AIModelType.TEXT_GENERATION: "high",
                AIModelType.CONTENT_ANALYSIS: "high"
            }
        }
        
        content_compatibility = compatibility_matrix.get(content_type, {})
        compatibility_score = content_compatibility.get(model_type, "low")
        
        return {
            "content_type": content_type,
            "model_type": model_type.value,
            "compatibility_score": compatibility_score,
            "processing_complexity": self._assess_processing_complexity(content_type)
        }
    
    def _assess_processing_complexity(self, content_type: str) -> Dict[str, Any]:
        """Assess processing complexity for content type"""
        complexity_levels = {
            "video": {"complexity": "critical", "resource_intensive": True},
            "audio": {"complexity": "high", "resource_intensive": True},
            "image": {"complexity": "medium", "resource_intensive": False},
            "text": {"complexity": "low", "resource_intensive": False}
        }
        
        return complexity_levels.get(content_type, {"complexity": "unknown"})
    
    async def _match_known_ai_patterns(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Match error against known AI error patterns"""
        error_message = ai_error_event.error_message.lower()
        
        matched_patterns = []
        
        for pattern_name, pattern_config in self.known_ai_patterns.items():
            keywords = pattern_config.get("keywords", [])
            if any(keyword in error_message for keyword in keywords):
                matched_patterns.append({
                    "pattern_name": pattern_name,
                    "confidence": pattern_config.get("confidence", 0.5),
                    "description": pattern_config.get("description", ""),
                    "common_causes": pattern_config.get("common_causes", []),
                    "recommended_actions": pattern_config.get("recommended_actions", [])
                })
        
        return {
            "matched_patterns": matched_patterns,
            "pattern_count": len(matched_patterns),
            "highest_confidence_pattern": max(matched_patterns, key=lambda x: x["confidence"]) if matched_patterns else None
        }
    
    async def _perform_root_cause_analysis(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Perform root cause analysis for AI error"""
        root_cause_analysis = {
            "probable_root_causes": [],
            "contributing_factors": [],
            "system_state_analysis": {},
            "confidence_level": "medium"
        }
        
        error_message = ai_error_event.error_message.lower()
        system_metrics = ai_error_event.system_metrics
        
        # Analyze probable root causes
        if "memory" in error_message or "oom" in error_message:
            root_cause_analysis["probable_root_causes"].append({
                "cause": "insufficient_memory",
                "probability": 0.9,
                "evidence": ["memory error in message", "high memory utilization"]
            })
        
        if "timeout" in error_message:
            root_cause_analysis["probable_root_causes"].append({
                "cause": "processing_timeout",
                "probability": 0.8,
                "evidence": ["timeout in error message", "long processing duration"]
            })
        
        if "gpu" in error_message or "cuda" in error_message:
            root_cause_analysis["probable_root_causes"].append({
                "cause": "gpu_resource_issue",
                "probability": 0.85,
                "evidence": ["gpu-related error", "high gpu utilization"]
            })
        
        # System state analysis
        root_cause_analysis["system_state_analysis"] = {
            "system_load": "high" if system_metrics.get("cpu_percent", 0) > 70 else "normal",
            "memory_pressure": "high" if system_metrics.get("memory_percent", 0) > 80 else "normal",
            "concurrent_processing": "likely"
        }
        
        return root_cause_analysis
    
    async def _update_model_health(self, ai_error_event: AIErrorEvent):
        """Update model health status based on error"""
        model_name = ai_error_event.model_name
        
        if model_name not in self.model_health_status:
            self.model_health_status[model_name] = {
                "model_name": model_name,
                "model_type": ai_error_event.model_type.value,
                "health_score": 1.0,
                "error_count": 0,
                "last_error": None,
                "alert_level": "green"
            }
        
        health_status = self.model_health_status[model_name]
        
        # Update error tracking
        health_status["last_error"] = ai_error_event.timestamp
        health_status["error_count"] += 1
        
        # Update health score based on error severity
        if ai_error_event.error_severity == AIErrorSeverity.MODEL_FAILURE:
            health_status["health_score"] = max(0, health_status["health_score"] - 0.3)
        elif ai_error_event.error_severity == AIErrorSeverity.RESOURCE_EXHAUSTION:
            health_status["health_score"] = max(0, health_status["health_score"] - 0.2)
        else:
            health_status["health_score"] = max(0, health_status["health_score"] - 0.1)
        
        # Update alert level
        if health_status["health_score"] < 0.3:
            health_status["alert_level"] = "red"
        elif health_status["health_score"] < 0.6:
            health_status["alert_level"] = "yellow"
        else:
            health_status["alert_level"] = "green"
    
    async def _attempt_ai_recovery(self, 
                                  ai_error_event: AIErrorEvent,
                                  creator_context: Any) -> Dict[str, Any]:
        """Attempt automatic recovery for AI processing error"""
        recovery_result = {
            "recovery_attempted": False,
            "recovery_strategy": None,
            "recovery_successful": False,
            "recovery_details": {},
            "fallback_options": []
        }
        
        error_severity = ai_error_event.error_severity
        model_name = ai_error_event.model_name
        
        if error_severity == AIErrorSeverity.RESOURCE_EXHAUSTION:
            recovery_result["recovery_strategy"] = "resource_optimization"
            recovery_result["recovery_attempted"] = True
            
            recovery_result["recovery_details"] = {
                "action": "reduced_batch_size",
                "new_batch_size": "50% of original",
                "memory_freed": "estimated 40%"
            }
            
            recovery_result["recovery_successful"] = True
            
        elif error_severity == AIErrorSeverity.MODEL_FAILURE:
            recovery_result["recovery_strategy"] = "model_fallback"
            recovery_result["recovery_attempted"] = True
            
            fallback_models = self.recovery_strategies.get("model_fallback", {}).get(model_name, [])
            if fallback_models:
                recovery_result["recovery_details"] = {
                    "action": "fallback_model_activation",
                    "fallback_model": fallback_models[0],
                    "quality_trade_off": "minor reduction expected"
                }
                recovery_result["recovery_successful"] = True
            else:
                recovery_result["fallback_options"] = ["manual_intervention", "retry_later"]
        
        # Update error event with recovery information
        ai_error_event.recovery_attempted = recovery_result["recovery_attempted"]
        ai_error_event.recovery_successful = recovery_result["recovery_successful"]
        
        return recovery_result
    
    async def _generate_ai_recommendations(self, 
                                          ai_error_event: AIErrorEvent,
                                          analysis: Dict[str, Any],
                                          creator_context: Any) -> List[str]:
        """Generate AI-specific recommendations"""
        recommendations = []
        
        error_severity = ai_error_event.error_severity
        model_type = ai_error_event.model_type
        
        if error_severity == AIErrorSeverity.MODEL_FAILURE:
            recommendations.extend([
                f"🚨 CRITICAL: {ai_error_event.model_name} model failure detected",
                "Activate fallback model immediately",
                "Investigate model checkpoint integrity",
                "Review model deployment configuration",
                "Consider model version rollback if recent update"
            ])
        
        elif error_severity == AIErrorSeverity.RESOURCE_EXHAUSTION:
            recommendations.extend([
                "🔧 RESOURCE: Optimize resource allocation",
                "Reduce batch size for processing",
                "Consider horizontal scaling of AI infrastructure",
                "Implement resource monitoring alerts",
                "Review concurrent processing limits"
            ])
        
        elif error_severity == AIErrorSeverity.QUALITY_DEGRADATION:
            recommendations.extend([
                "📊 QUALITY: Monitor output quality metrics",
                "Implement quality assurance checkpoints",
                "Review model confidence thresholds",
                "Consider model retraining with recent data"
            ])
        
        # Content-type specific recommendations
        content_type = ai_error_event.content_type
        if content_type == "video" and model_type == AIModelType.VIDEO_PROCESSING:
            recommendations.extend([
                "🎥 VIDEO: Check video codec compatibility",
                "Verify video resolution limits",
                "Consider progressive processing for large files",
                "Monitor GPU memory usage during video processing"
            ])
        elif content_type == "audio" and model_type == AIModelType.AUDIO_PROCESSING:
            recommendations.extend([
                "🎵 AUDIO: Verify audio format support",
                "Check sample rate compatibility",
                "Monitor audio processing pipeline health",
                "Consider audio preprocessing optimizations"
            ])
        
        # Creator tier specific recommendations
        creator_tier = ai_error_event.creator_tier
        if creator_tier in ["professional", "enterprise"]:
            recommendations.extend([
                "🏢 ENTERPRISE: Escalate to premium AI support",
                "Activate dedicated AI processing resources",
                "Provide real-time status updates to creator",
                "Consider SLA compensation if applicable"
            ])
        
        return recommendations
    
    def get_ai_model_health_report(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive AI model health report"""
        if model_name:
            if model_name in self.model_health_status:
                return self.model_health_status[model_name]
            else:
                return {"error": f"Model {model_name} not found in health monitoring"}
        
        return {
            "total_models": len(self.model_health_status),
            "models_health": self.model_health_status,
            "overall_health_score": self._calculate_overall_health_score(),
            "critical_alerts": self._get_critical_health_alerts(),
            "report_generated_at": datetime.utcnow().isoformat()
        }
    
    def get_ai_error_analytics(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get AI error analytics for specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        recent_errors = [e for e in self.ai_error_events if e.timestamp > cutoff_time]
        
        if not recent_errors:
            return {
                "time_window_seconds": time_window,
                "total_errors": 0,
                "analytics": "No errors in specified window"
            }
        
        analytics = {
            "time_window_seconds": time_window,
            "total_errors": len(recent_errors),
            "error_by_model": Counter(e.model_name for e in recent_errors),
            "error_by_type": Counter(e.error_type for e in recent_errors),
            "error_by_severity": Counter(e.error_severity.value for e in recent_errors),
            "error_by_stage": Counter(e.processing_stage.value for e in recent_errors),
            "error_by_creator_tier": Counter(e.creator_tier for e in recent_errors),
            "error_by_content_type": Counter(e.content_type for e in recent_errors),
            "recovery_success_rate": sum(1 for e in recent_errors if e.recovery_successful) / len(recent_errors) * 100,
            "most_problematic_models": Counter(e.model_name for e in recent_errors).most_common(5),
            "analytics_generated_at": datetime.utcnow().isoformat()
        }
        
        return analytics
    
    # Helper methods
    def _determine_model_type(self, model_name: str, creator_context: Any) -> AIModelType:
        """Determine AI model type from context"""
        content_type = creator_context.content_type.lower()
        
        type_mapping = {
            "audio": AIModelType.AUDIO_PROCESSING,
            "video": AIModelType.VIDEO_PROCESSING,
            "image": AIModelType.IMAGE_PROCESSING,
            "text": AIModelType.TEXT_GENERATION
        }
        
        return type_mapping.get(content_type, AIModelType.CONTENT_ANALYSIS)
    
    def _determine_processing_stage(self, ai_context: Dict[str, Any], creator_context: Any) -> AIProcessingStage:
        """Determine processing stage from context"""
        stage_hint = ai_context.get("processing_stage", "").lower()
        
        if "preprocessing" in stage_hint or "preprocess" in stage_hint:
            return AIProcessingStage.PREPROCESSING
        elif "inference" in stage_hint or "model" in stage_hint:
            return AIProcessingStage.MODEL_INFERENCE
        elif "postprocessing" in stage_hint or "postprocess" in stage_hint:
            return AIProcessingStage.POSTPROCESSING
        elif "validation" in stage_hint:
            return AIProcessingStage.VALIDATION
        else:
            return AIProcessingStage.MODEL_INFERENCE  # Default
    
    def _classify_ai_error_severity(self, error: Exception, ai_context: Dict[str, Any]) -> AIErrorSeverity:
        """Classify AI error severity"""
        error_message = str(error).lower()
        
        if any(keyword in error_message for keyword in ["model", "load", "initialize", "not found"]):
            return AIErrorSeverity.MODEL_FAILURE
        elif any(keyword in error_message for keyword in ["memory", "oom", "resource", "gpu"]):
            return AIErrorSeverity.RESOURCE_EXHAUSTION
        elif any(keyword in error_message for keyword in ["quality", "corrupt", "degraded"]):
            return AIErrorSeverity.QUALITY_DEGRADATION
        elif any(keyword in error_message for keyword in ["timeout", "slow", "performance"]):
            return AIErrorSeverity.PERFORMANCE_DEGRADATION
        elif any(keyword in error_message for keyword in ["input", "validation", "format"]):
            return AIErrorSeverity.INPUT_VALIDATION_ERROR
        elif any(keyword in error_message for keyword in ["output", "result", "corrupt"]):
            return AIErrorSeverity.OUTPUT_CORRUPTION
        else:
            return AIErrorSeverity.PERFORMANCE_DEGRADATION  # Default
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_io": {},
                "network_io": {},
                "gpu_utilization": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "psutil not available"
            }
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {},
                "network_io": dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {},
                "gpu_utilization": 0,  # Would need GPU monitoring library
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}
    
    def _extract_stack_trace(self, error: Exception) -> Optional[str]:
        """Extract stack trace from exception"""
        import traceback
        try:
            return traceback.format_exc()
        except:
            return None
    
    def _assess_model_health_impact(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Assess impact on model health"""
        return {
            "health_degradation": "medium",
            "availability_impact": ai_error_event.error_severity == AIErrorSeverity.MODEL_FAILURE,
            "performance_impact": "negative",
            "recovery_time_estimate": "5-15 minutes"
        }
    
    def _assess_performance_impact(self, ai_error_event: AIErrorEvent) -> Dict[str, Any]:
        """Assess performance impact of error"""
        return {
            "throughput_impact": "reduced",
            "latency_impact": "increased",
            "quality_impact": "potential_degradation",
            "cost_impact": "increased_resource_usage"
        }
    
    def _get_stage_criticality(self, stage: AIProcessingStage) -> str:
        """Get criticality level of processing stage"""
        criticality_map = {
            AIProcessingStage.PREPROCESSING: "medium",
            AIProcessingStage.MODEL_INFERENCE: "critical",
            AIProcessingStage.POSTPROCESSING: "high",
            AIProcessingStage.VALIDATION: "high",
            AIProcessingStage.OPTIMIZATION: "low",
            AIProcessingStage.CACHING: "low"
        }
        return criticality_map.get(stage, "medium")
    
    def _assess_downstream_impact(self, stage: AIProcessingStage) -> List[str]:
        """Assess downstream impact of stage failure"""
        impact_map = {
            AIProcessingStage.PREPROCESSING: ["model_inference", "postprocessing", "validation"],
            AIProcessingStage.MODEL_INFERENCE: ["postprocessing", "validation"],
            AIProcessingStage.POSTPROCESSING: ["validation"],
            AIProcessingStage.VALIDATION: [],
            AIProcessingStage.OPTIMIZATION: [],
            AIProcessingStage.CACHING: []
        }
        return impact_map.get(stage, [])
    
    def _assess_recovery_complexity(self, stage: AIProcessingStage) -> str:
        """Assess recovery complexity for stage"""
        complexity_map = {
            AIProcessingStage.PREPROCESSING: "low",
            AIProcessingStage.MODEL_INFERENCE: "high",
            AIProcessingStage.POSTPROCESSING: "medium",
            AIProcessingStage.VALIDATION: "low",
            AIProcessingStage.OPTIMIZATION: "low",
            AIProcessingStage.CACHING: "low"
        }
        return complexity_map.get(stage, "medium")
    
    def _get_model_specific_recommendations(self, model_name: str, ai_error_event: AIErrorEvent) -> List[str]:
        """Get model-specific recommendations"""
        model_recommendations = {
            "text_generator": [
                "Check text model tokenization",
                "Verify input length limits",
                "Review model vocabulary"
            ],
            "audio_processor": [
                "Verify audio codec support",
                "Check sample rate compatibility",
                "Review audio buffer sizes"
            ],
            "video_processor": [
                "Check video codec support",
                "Verify frame rate compatibility",
                "Review video resolution limits"
            ],
            "image_processor": [
                "Verify image format support",
                "Check image resolution limits",
                "Review color space compatibility"
            ]
        }
        
        # Get model category from name
        for category, recommendations in model_recommendations.items():
            if category in model_name.lower():
                return recommendations
        
        return ["Review model configuration", "Check model health status"]
    
    def _calculate_overall_health_score(self) -> float:
        """Calculate overall health score across all models"""
        if not self.model_health_status:
            return 1.0
        
        total_score = sum(status["health_score"] for status in self.model_health_status.values())
        return total_score / len(self.model_health_status)
    
    def _get_critical_health_alerts(self) -> List[Dict[str, Any]]:
        """Get critical health alerts"""
        alerts = []
        
        for model_name, status in self.model_health_status.items():
            if status["alert_level"] == "red":
                alerts.append({
                    "model_name": model_name,
                    "alert_level": "critical",
                    "health_score": status["health_score"],
                    "issue": "Model health critically degraded",
                    "action_required": "immediate"
                })
            elif status["alert_level"] == "yellow":
                alerts.append({
                    "model_name": model_name,
                    "alert_level": "warning",
                    "health_score": status["health_score"],
                    "issue": "Model performance degradation detected",
                    "action_required": "monitoring"
                })
        
        return alerts
    
    def _cleanup_old_errors(self):
        """Clean up old error events"""
        if len(self.ai_error_events) > self.max_error_history:
            self.ai_error_events = self.ai_error_events[-self.max_error_history//2:]
    
    def _initialize_ai_patterns(self) -> Dict[str, Any]:
        """Initialize known AI error patterns"""
        return {
            "model_loading_failure": {
                "keywords": ["model", "load", "checkpoint", "not found"],
                "confidence": 0.9,
                "description": "AI model failed to load properly",
                "common_causes": ["corrupted model file", "missing dependencies", "insufficient permissions"],
                "recommended_actions": ["verify model file integrity", "check model path", "restart model service"]
            },
            "gpu_memory_exhaustion": {
                "keywords": ["gpu", "cuda", "memory", "oom", "out of memory"],
                "confidence": 0.95,
                "description": "GPU memory exhausted during processing",
                "common_causes": ["large batch size", "high resolution input", "memory leak"],
                "recommended_actions": ["reduce batch size", "optimize memory usage", "restart GPU service"]
            },
            "inference_timeout": {
                "keywords": ["timeout", "inference", "model", "hung"],
                "confidence": 0.8,
                "description": "Model inference took too long to complete",
                "common_causes": ["complex input", "model overload", "resource contention"],
                "recommended_actions": ["increase timeout", "optimize model", "scale resources"]
            }
        }
    
    def _initialize_model_thresholds(self) -> Dict[str, Any]:
        """Initialize model-specific thresholds"""
        return {
            "text_generator": {
                "max_processing_time": 30,
                "max_memory_usage": 4096,
                "expected_success_rate": 95,
                "characteristics": {"type": "transformer", "resource_intensive": False}
            },
            "audio_processor": {
                "max_processing_time": 120,
                "max_memory_usage": 8192,
                "expected_success_rate": 90,
                "characteristics": {"type": "signal_processing", "resource_intensive": True}
            },
            "video_processor": {
                "max_processing_time": 300,
                "max_memory_usage": 16384,
                "expected_success_rate": 85,
                "characteristics": {"type": "computer_vision", "resource_intensive": True}
            }
        }
    
    def _initialize_recovery_strategies(self) -> Dict[str, Any]:
        """Initialize recovery strategies"""
        return {
            "model_fallback": {
                "text_generator": ["text_generator_v2", "simple_text_processor"],
                "audio_processor": ["audio_processor_lite", "basic_audio_handler"],
                "video_processor": ["video_processor_fast", "simple_video_handler"],
                "image_processor": ["image_processor_lite", "basic_image_handler"]
            },
            "resource_optimization": {
                "memory_reduction": {"batch_size_multiplier": 0.5, "cache_reduction": 0.3},
                "gpu_optimization": {"precision_reduction": "fp16", "batch_size_reduction": 0.6}
            }
        }
    
    def _fallback_ai_analysis(self, error: Exception) -> Dict[str, Any]:
        """Fallback analysis when main AI analysis fails"""
        return {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "ai_context": "analysis_failed",
            "basic_classification": "ai_processing_error",
            "severity_estimate": "medium",
            "fallback_recommendations": [
                "Review AI processing logs",
                "Check AI model health status",
                "Verify AI infrastructure availability",
                "Contact AI operations team if issue persists"
            ]
        }
    
    def health_check(self) -> str:
        """Health check for AI monitoring engine"""
        try:
            # Check if core components are working
            if not isinstance(self.ai_error_events, list):
                return "unhealthy"
            if not isinstance(self.model_health_status, dict):
                return "unhealthy"
            if not isinstance(self.known_ai_patterns, dict):
                return "unhealthy"
            
            return "healthy"
        except Exception:
            return "error"


# Global AI Processing Error Monitoring Engine instance
ai_monitoring_engine = AIProcessingErrorMonitoringEngine()