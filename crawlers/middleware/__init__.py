"""
Crawler Middleware Module
========================

Enterprise-grade middleware pipeline for IA Influencer Agent crawlers.
Implements comprehensive authentication, rate limiting, content processing,
security, fingerprinting, monitoring, error handling, and data validation.

Author: Fahed Mlaiel <mlaiel@live.de>  
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Pipeline:
Multi-format Creators → IA Protection → SEO Optimization → Collaboration Matching → Distribution

Key Components:
- Authentication: JWT/OAuth2, API keys, MFA, behavioral analysis, biometric validation
- Rate Limiting: Distributed limiting, adaptive algorithms, priority queuing, tier-based limits
- Content Processing: Multi-format processing (audio/video/image/text), AI-powered analysis
- Security: Threat detection, IP analysis, content scanning, GDPR compliance, enterprise security
- Fingerprinting: Multi-format identification, similarity detection, protection metadata
- Monitoring: Real-time metrics, alerting, performance tracking, business metrics
- Error Handling: Recovery strategies, circuit breakers, comprehensive reporting, business continuity
- Validation: Schema validation, sanitization, quality analysis, compliance checks
"""

from typing import Dict, List, Optional, Any, Callable, Union
import logging
from datetime import datetime

# Import all middleware components with enhanced functionality
from .authentication import (
    AuthenticationMiddleware,
    TokenManager,
    APIKeyManager,
    MultiFactorAuthenticator,
    BiometricAuthenticator,
    BehavioralAnalyzer,
    GeolocationValidator,
    AuthenticationRequest,
    AuthenticationResult,
    get_authentication_middleware,
    get_biometric_authenticator,
    get_behavioral_analyzer,
    get_geolocation_validator,
    require_auth,
    require_api_key,
    require_mfa,
    require_permissions
)

from .rate_limiting import (
    RateLimitingMiddleware,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    AdaptiveLimiter,
    PriorityQueueLimiter,
    GeolocationBasedLimiter,
    RateLimitRequest,
    RateLimitResult,
    RateLimitConfig,
    RateLimitStrategy,
    RateLimitLevel,
    UserTier,
    get_rate_limiting_middleware,
    rate_limit,
    priority_rate_limit,
    tier_based_rate_limit
)

from .content_processing import (
    ContentProcessingMiddleware,
    AudioProcessor,
    VideoProcessor,
    ImageProcessor,
    TextProcessor,
    MultiFormatProcessor,
    ContentProcessingRequest,
    ProcessingResult,
    ContentType,
    ProcessingStage,
    ProcessingStatus,
    get_content_processing_middleware,
    get_audio_processor,
    get_video_processor,
    get_image_processor,
    get_text_processor,
    process_content,
    batch_process_content
)

from .security import (
    SecurityMiddleware,
    IPSecurityAnalyzer,
    ContentSecurityScanner,
    ThreatDetectionEngine,
    ComplianceValidator,
    EncryptionManager,
    SecurityRequest,
    SecurityResult,
    ThreatLevel,
    SecurityAction,
    AttackType,
    ComplianceStandard,
    get_security_middleware,
    get_threat_detector,
    get_compliance_validator,
    validate_security,
    scan_content_security,
    check_compliance
)

from .fingerprinting import (
    FingerprintingMiddleware,
    AudioFingerprinter,
    VideoFingerprinter,
    ImageFingerprinter,
    TextFingerprinter,
    UniversalFingerprintEngine,
    SimilarityDetector,
    FingerprintRequest,
    FingerprintResult,
    FingerprintType,
    ContentProtectionLevel,
    get_fingerprinting_middleware,
    get_audio_fingerprinter,
    get_video_fingerprinter,
    get_image_fingerprinter,
    get_text_fingerprinter,
    generate_fingerprint,
    detect_similarity,
    batch_fingerprint
)

from .monitoring import (
    MonitoringMiddleware,
    PerformanceMonitor,
    BusinessMetricsCollector,
    AlertManager,
    MetricsAggregator,
    MonitoringEvent,
    MetricData,
    AlertRule,
    MetricType,
    AlertLevel,
    BusinessMetricType,
    MetricBuffer,
    get_monitoring_middleware,
    get_performance_monitor,
    get_alert_manager,
    collect_metrics,
    trigger_alert,
    get_business_metrics
)

from .error_handling import (
    ErrorHandlingMiddleware,
    ErrorRecoveryManager,
    CircuitBreakerManager,
    BusinessContinuityHandler,
    ErrorInfo,
    RecoveryStrategy,
    CircuitBreakerState,
    ErrorSeverity,
    ErrorCategory,
    RecoveryAction,
    BusinessImpact,
    get_error_handling_middleware,
    get_recovery_manager,
    get_circuit_breaker,
    handle_error,
    recover_from_error,
    ensure_business_continuity
)

from .validation import (
    ValidationMiddleware,
    SchemaValidator,
    ContentQualityAnalyzer,
    ComplianceValidator as DataComplianceValidator,
    BusinessRuleValidator,
    ValidationRequest,
    ValidationResult,
    ContentValidationResult,
    ValidationRule,
    ValidationLevel,
    DataType,
    SanitizationLevel,
    ContentQuality,
    get_validation_middleware,
    get_schema_validator,
    get_quality_analyzer,
    validate_data,
    sanitize_content,
    check_data_quality
)


class MiddlewarePipeline:
    """
    Enterprise-grade middleware pipeline orchestrator
    
    Coordinates all middleware components in the correct order for optimal
    performance and security while maintaining business logic compliance.
    """
    
    def __init__(self, 
                 enable_authentication: bool = True,
                 enable_rate_limiting: bool = True,
                 enable_security: bool = True,
                 enable_validation: bool = True,
                 enable_processing: bool = True,
                 enable_fingerprinting: bool = True,
                 enable_monitoring: bool = True,
                 enable_error_handling: bool = True):
        """Initialize middleware pipeline with configurable components"""
        
        self.logger = logging.getLogger(__name__)
        self.components = {}
        
        # Initialize components based on configuration
        if enable_authentication:
            self.components['authentication'] = get_authentication_middleware()
            
        if enable_rate_limiting:
            self.components['rate_limiting'] = get_rate_limiting_middleware()
            
        if enable_security:
            self.components['security'] = get_security_middleware()
            
        if enable_validation:
            self.components['validation'] = get_validation_middleware()
            
        if enable_processing:
            self.components['processing'] = get_content_processing_middleware()
            
        if enable_fingerprinting:
            self.components['fingerprinting'] = get_fingerprinting_middleware()
            
        if enable_monitoring:
            self.components['monitoring'] = get_monitoring_middleware()
            
        if enable_error_handling:
            self.components['error_handling'] = get_error_handling_middleware()
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request through complete middleware pipeline
        
        Pipeline Order:
        1. Authentication & Authorization
        2. Rate Limiting & Throttling
        3. Security Validation & Threat Detection
        4. Data Validation & Sanitization
        5. Content Processing & Enhancement
        6. Fingerprinting & Protection
        7. Monitoring & Metrics Collection
        8. Error Handling & Recovery
        """
        
        start_time = datetime.utcnow()
        pipeline_result = {
            "success": True,
            "stages_completed": [],
            "pipeline_duration": 0.0,
            "metadata": {}
        }
        
        try:
            # Stage 1: Authentication
            if 'authentication' in self.components:
                auth_result = await self.components['authentication'].authenticate(request_data)
                if not auth_result.success:
                    pipeline_result["success"] = False
                    pipeline_result["error"] = "Authentication failed"
                    return pipeline_result
                pipeline_result["stages_completed"].append("authentication")
                pipeline_result["metadata"]["auth"] = auth_result.dict()
            
            # Stage 2: Rate Limiting
            if 'rate_limiting' in self.components:
                rate_result = await self.components['rate_limiting'].check_limits(request_data)
                if not rate_result.allowed:
                    pipeline_result["success"] = False
                    pipeline_result["error"] = "Rate limit exceeded"
                    pipeline_result["retry_after"] = rate_result.retry_after
                    return pipeline_result
                pipeline_result["stages_completed"].append("rate_limiting")
                pipeline_result["metadata"]["rate_limit"] = rate_result.dict()
            
            # Stage 3: Security Validation
            if 'security' in self.components:
                security_result = await self.components['security'].validate(request_data)
                if security_result.action in ["block", "quarantine"]:
                    pipeline_result["success"] = False
                    pipeline_result["error"] = "Security validation failed"
                    pipeline_result["threat_level"] = security_result.threat_level
                    return pipeline_result
                pipeline_result["stages_completed"].append("security")
                pipeline_result["metadata"]["security"] = security_result.dict()
            
            # Stage 4: Data Validation
            if 'validation' in self.components:
                validation_result = await self.components['validation'].validate(request_data)
                if not validation_result.overall_valid:
                    pipeline_result["success"] = False
                    pipeline_result["error"] = "Data validation failed"
                    pipeline_result["validation_errors"] = validation_result.dict()
                    return pipeline_result
                pipeline_result["stages_completed"].append("validation")
                pipeline_result["metadata"]["validation"] = validation_result.dict()
            
            # Stage 5: Content Processing
            if 'processing' in self.components:
                processing_result = await self.components['processing'].process(request_data)
                if processing_result.status == "failed":
                    pipeline_result["success"] = False
                    pipeline_result["error"] = "Content processing failed"
                    return pipeline_result
                pipeline_result["stages_completed"].append("processing")
                pipeline_result["metadata"]["processing"] = processing_result.dict()
                request_data["processed_content"] = processing_result.processed_content
            
            # Stage 6: Fingerprinting
            if 'fingerprinting' in self.components:
                fingerprint_result = await self.components['fingerprinting'].generate(request_data)
                pipeline_result["stages_completed"].append("fingerprinting")
                pipeline_result["metadata"]["fingerprinting"] = fingerprint_result.dict()
                request_data["fingerprints"] = fingerprint_result.fingerprints
            
            # Stage 7: Monitoring
            if 'monitoring' in self.components:
                await self.components['monitoring'].collect_metrics(request_data, pipeline_result)
                pipeline_result["stages_completed"].append("monitoring")
            
            # Calculate total pipeline duration
            end_time = datetime.utcnow()
            pipeline_result["pipeline_duration"] = (end_time - start_time).total_seconds()
            
            return pipeline_result
            
        except Exception as e:
            # Stage 8: Error Handling
            if 'error_handling' in self.components:
                error_result = await self.components['error_handling'].handle_error(e, request_data)
                pipeline_result["error_handling"] = error_result.dict()
            
            pipeline_result["success"] = False
            pipeline_result["error"] = str(e)
            pipeline_result["pipeline_duration"] = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.error(f"Pipeline processing failed: {str(e)}")
            return pipeline_result


# Factory functions for easy initialization
def create_full_pipeline(**kwargs) -> MiddlewarePipeline:
    """Create a complete middleware pipeline with all components enabled"""
    return MiddlewarePipeline(**kwargs)


def create_basic_pipeline() -> MiddlewarePipeline:
    """Create a basic middleware pipeline with essential components only"""
    return MiddlewarePipeline(
        enable_authentication=True,
        enable_rate_limiting=True,
        enable_security=True,
        enable_validation=True,
        enable_processing=False,
        enable_fingerprinting=False,
        enable_monitoring=True,
        enable_error_handling=True
    )


def create_content_pipeline() -> MiddlewarePipeline:
    """Create a content-focused pipeline for media processing"""
    return MiddlewarePipeline(
        enable_authentication=True,
        enable_rate_limiting=True,
        enable_security=True,
        enable_validation=True,
        enable_processing=True,
        enable_fingerprinting=True,
        enable_monitoring=True,
        enable_error_handling=True
    )


# Export all public components
__all__ = [
    # Core pipeline
    "MiddlewarePipeline",
    "create_full_pipeline",
    "create_basic_pipeline", 
    "create_content_pipeline",
    
    # Authentication components
    "AuthenticationMiddleware",
    "TokenManager",
    "APIKeyManager",
    "MultiFactorAuthenticator",
    "BiometricAuthenticator",
    "BehavioralAnalyzer",
    "GeolocationValidator",
    
    # Rate limiting components
    "RateLimitingMiddleware",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    "AdaptiveLimiter",
    "PriorityQueueLimiter",
    
    # Content processing components
    "ContentProcessingMiddleware",
    "AudioProcessor",
    "VideoProcessor", 
    "ImageProcessor",
    "TextProcessor",
    "MultiFormatProcessor",
    
    # Security components
    "SecurityMiddleware",
    "IPSecurityAnalyzer",
    "ContentSecurityScanner",
    "ThreatDetectionEngine",
    "ComplianceValidator",
    
    # Fingerprinting components
    "FingerprintingMiddleware",
    "AudioFingerprinter",
    "VideoFingerprinter",
    "ImageFingerprinter",
    "TextFingerprinter",
    "SimilarityDetector",
    
    # Monitoring components
    "MonitoringMiddleware",
    "PerformanceMonitor",
    "BusinessMetricsCollector",
    "AlertManager",
    "MetricsAggregator",
    
    # Error handling components
    "ErrorHandlingMiddleware",
    "ErrorRecoveryManager",
    "CircuitBreakerManager",
    "BusinessContinuityHandler",
    
    # Validation components
    "ValidationMiddleware",
    "SchemaValidator",
    "ContentQualityAnalyzer",
    "BusinessRuleValidator",
    
    # Utility functions
    "require_auth",
    "require_api_key",
    "require_mfa",
    "rate_limit",
    "validate_security",
    "generate_fingerprint",
    "collect_metrics",
    "handle_error",
    "validate_data"
]

from .content_processing import (
    ContentProcessingMiddleware,
    AudioProcessor,
    VideoProcessor,
    ImageProcessor,
    TextProcessor,
    get_content_processing_middleware,
    process_content,
    extract_features
)

from .security import (
    SecurityMiddleware,
    IPSecurityAnalyzer,
    ContentSecurityAnalyzer,
    BehaviorAnalyzer,
    get_security_middleware,
    security_scan,
    analyze_request
)

from .fingerprinting import (
    FingerprintingMiddleware,
    AudioFingerprinter,
    VideoFingerprinter,
    ImageFingerprinter,
    TextFingerprinter,
    get_fingerprinting_middleware,
    generate_fingerprint,
    find_similar_content
)

from .monitoring import (
    MonitoringMiddleware,
    PerformanceMonitor,
    AlertManager,
    MetricsCollector,
    get_monitoring_middleware,
    monitor_performance,
    collect_metrics
)

from .error_handling import (
    ErrorHandlingMiddleware,
    ErrorRecoveryManager,
    ErrorReporter,
    ErrorInfo,
    get_error_handling_middleware,
    handle_errors,
    report_error
)

from .validation import (
    ValidationMiddleware,
    SchemaValidator,
    DataQualityAnalyzer,
    ValidationRule,
    ContentValidationResult,
    get_validation_middleware,
    validate_data,
    register_validation_schema
)

logger = logging.getLogger(__name__)


class MiddlewarePipeline:
    """
    Comprehensive middleware pipeline orchestrator.
    Coordinates all middleware components in the correct order.
    """
    
    def __init__(self):
        """Initialize middleware pipeline with all components"""
        self.authentication = get_authentication_middleware()
        self.rate_limiting = get_rate_limiting_middleware()
        self.security = get_security_middleware()
        self.validation = get_validation_middleware()
        self.content_processing = get_content_processing_middleware()
        self.fingerprinting = get_fingerprinting_middleware()
        self.monitoring = get_monitoring_middleware()
        self.error_handling = get_error_handling_middleware()
        
        # Pipeline configuration
        self.pipeline_enabled = True
        self.strict_mode = True
        
        logger.info("Middleware pipeline initialized with all components")
    
    async def process_request(self, request_data: Dict[str, Any],
                            user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process request through complete middleware pipeline.
        
        Pipeline Order:
        1. Monitoring (start tracking)
        2. Authentication  
        3. Rate Limiting
        4. Security Analysis
        5. Data Validation
        6. Content Processing
        7. Fingerprinting
        8. Monitoring (end tracking)
        """
        
        request_id = request_data.get("request_id", f"req_{int(datetime.utcnow().timestamp())}")
        
        try:
            # 1. Start monitoring
            monitoring_context = await self.monitoring.start_request_monitoring(request_id)
            
            # 2. Authentication
            auth_result = await self.authentication.authenticate_request(
                request_data, user_context
            )
            if not auth_result.get("authenticated", False):
                raise Exception(f"Authentication failed: {auth_result.get('error')}")
            
            # 3. Rate limiting
            rate_limit_result = await self.rate_limiting.check_rate_limit(
                request_data, auth_result.get("user_id")
            )
            if not rate_limit_result.get("allowed", False):
                raise Exception(f"Rate limit exceeded: {rate_limit_result.get('error')}")
            
            # 4. Security analysis
            security_result = await self.security.analyze_request(
                request_data, auth_result.get("user_id")
            )
            if not security_result.get("safe", False):
                raise Exception(f"Security threat detected: {security_result.get('threat_type')}")
            
            # 5. Data validation
            validation_result = await self.validation.validate_content(
                request_id, request_data.get("content", {})
            )
            if not validation_result.overall_valid and self.strict_mode:
                raise Exception(f"Data validation failed: {validation_result.field_results}")
            
            # 6. Content processing
            content_result = None
            if request_data.get("content"):
                content_result = await self.content_processing.process_content(
                    request_data["content"]
                )
            
            # 7. Fingerprinting
            fingerprint_result = None
            if content_result:
                fingerprint_result = await self.fingerprinting.generate_fingerprint(
                    content_result["processed_content"]
                )
            
            # 8. End monitoring
            await self.monitoring.end_request_monitoring(
                request_id, monitoring_context, success=True
            )
            
            # Compile final result
            pipeline_result = {
                "request_id": request_id,
                "success": True,
                "authentication": auth_result,
                "rate_limiting": rate_limit_result,
                "security": security_result,
                "validation": validation_result.dict() if validation_result else None,
                "content_processing": content_result,
                "fingerprinting": fingerprint_result,
                "processing_time": monitoring_context.get("processing_time", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return pipeline_result
            
        except Exception as e:
            # Handle pipeline error
            error_context = {
                "request_id": request_id,
                "pipeline_stage": "unknown",
                "user_context": user_context
            }
            
            await self.error_handling.handle_error(e, error_context)
            
            # End monitoring with error
            if 'monitoring_context' in locals():
                await self.monitoring.end_request_monitoring(
                    request_id, monitoring_context, success=False, error=str(e)
                )
            
            # Return error result
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        try:
            # Get status from all components
            auth_status = await self.authentication.get_dashboard_data()
            rate_limit_status = await self.rate_limiting.get_dashboard_data()
            security_status = await self.security.get_dashboard_data()
            validation_status = await self.validation.get_validation_statistics()
            processing_status = await self.content_processing.get_dashboard_data()
            fingerprint_status = await self.fingerprinting.get_dashboard_data()
            monitoring_status = await self.monitoring.get_dashboard_data()
            error_status = await self.error_handling.get_error_dashboard_data()
            
            return {
                "pipeline_enabled": self.pipeline_enabled,
                "strict_mode": self.strict_mode,
                "components": {
                    "authentication": auth_status,
                    "rate_limiting": rate_limit_status,
                    "security": security_status,
                    "validation": validation_status,
                    "content_processing": processing_status,
                    "fingerprinting": fingerprint_status,
                    "monitoring": monitoring_status,
                    "error_handling": error_status
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pipeline status retrieval error: {e}")
            return {
                "pipeline_enabled": self.pipeline_enabled,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def configure_pipeline(self, config: Dict[str, Any]):
        """Configure pipeline settings"""
        try:
            if "enabled" in config:
                self.pipeline_enabled = config["enabled"]
            
            if "strict_mode" in config:
                self.strict_mode = config["strict_mode"]
            
            # Configure individual components
            if "authentication" in config:
                await self.authentication.configure(config["authentication"])
            
            if "rate_limiting" in config:
                await self.rate_limiting.configure(config["rate_limiting"])
            
            if "security" in config:
                await self.security.configure(config["security"])
            
            logger.info("Pipeline configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Pipeline configuration error: {e}")
            raise


# Global pipeline instance
_middleware_pipeline = None


def get_middleware_pipeline() -> MiddlewarePipeline:
    """Get global middleware pipeline instance"""
    global _middleware_pipeline
    if _middleware_pipeline is None:
        _middleware_pipeline = MiddlewarePipeline()
    return _middleware_pipeline


# High-level convenience functions
async def process_crawler_request(request_data: Dict[str, Any],
                                user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """High-level function to process crawler request through full pipeline"""
    pipeline = get_middleware_pipeline()
    return await pipeline.process_request(request_data, user_context)


async def get_middleware_status() -> Dict[str, Any]:
    """Get comprehensive middleware status"""
    pipeline = get_middleware_pipeline()
    return await pipeline.get_pipeline_status()


async def configure_middleware(config: Dict[str, Any]):
    """Configure middleware pipeline"""
    pipeline = get_middleware_pipeline()
    await pipeline.configure_pipeline(config)


# Export all components and utilities
__all__ = [
    # Main pipeline
    "MiddlewarePipeline",
    "get_middleware_pipeline",
    "process_crawler_request",
    "get_middleware_status",
    "configure_middleware",
    
    # Authentication
    "AuthenticationMiddleware",
    "TokenManager", 
    "APIKeyManager",
    "MultiFactorAuthenticator",
    "get_authentication_middleware",
    "require_auth",
    "require_api_key",
    "require_mfa",
    
    # Rate Limiting
    "RateLimitingMiddleware",
    "SlidingWindowLimiter",
    "TokenBucketLimiter", 
    "AdaptiveLimiter",
    "PriorityQueue",
    "get_rate_limiting_middleware",
    "rate_limit",
    "priority_rate_limit",
    
    # Content Processing
    "ContentProcessingMiddleware",
    "AudioProcessor",
    "VideoProcessor",
    "ImageProcessor", 
    "TextProcessor",
    "get_content_processing_middleware",
    "process_content",
    "extract_features",
    
    # Security
    "SecurityMiddleware",
    "IPSecurityAnalyzer",
    "ContentSecurityAnalyzer",
    "BehaviorAnalyzer",
    "get_security_middleware",
    "security_scan",
    "analyze_request",
    
    # Fingerprinting
    "FingerprintingMiddleware",
    "AudioFingerprinter",
    "VideoFingerprinter", 
    "ImageFingerprinter",
    "TextFingerprinter",
    "get_fingerprinting_middleware",
    "generate_fingerprint",
    "find_similar_content",
    
    # Monitoring
    "MonitoringMiddleware",
    "PerformanceMonitor",
    "AlertManager",
    "MetricsCollector",
    "get_monitoring_middleware", 
    "monitor_performance",
    "collect_metrics",
    
    # Error Handling
    "ErrorHandlingMiddleware",
    "ErrorRecoveryManager",
    "ErrorReporter",
    "ErrorInfo",
    "get_error_handling_middleware",
    "handle_errors",
    "report_error",
    
    # Validation
    "ValidationMiddleware",
    "SchemaValidator",
    "DataQualityAnalyzer",
    "ValidationRule",
    "ContentValidationResult", 
    "get_validation_middleware",
    "validate_data",
    "register_validation_schema"
]
