#!/usr/bin/env python3
"""
🔍 Distributed Tracing Engine - Enterprise MLOps Platform
OpenTelemetry-based distributed tracing for Creator Economy microservices
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  PROPRIETARY SOFTWARE - COPYRIGHT NOTICE
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violations will result in immediate legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team training included

Logique métier Ainflue: Créateurs multi-format → IA processing → Protection → 
Monétisation → Collaboration & Gamification → SEO → Distribution
"""

import asyncio
import logging
import time
import json
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, ContextManager
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
from collections import defaultdict, deque
import warnings

# Suppress non-critical warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Optional OpenTelemetry dependencies
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    OPENTELEMETRY_AVAILABLE = True
    logger.info("✅ OpenTelemetry libraries available")
except ImportError:
    logger.warning("⚠️  OpenTelemetry not available. Tracing will use fallback implementation.")
    OPENTELEMETRY_AVAILABLE = False
    # Mock classes for fallback
    class trace:
        @staticmethod
        def get_tracer(*args, **kwargs):
            return MockTracer()
    
    class MockTracer:
        def start_span(self, *args, **kwargs):
            return MockSpan()
    
    class MockSpan:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def set_attribute(self, *args):
            pass
        def set_status(self, *args):
            pass
        def add_event(self, *args):
            pass

# Creator Economy types
class CreatorType(Enum):
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ALL = "all"

class SpanType(Enum):
    """Types de spans pour le tracing"""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    ML_INFERENCE = "ml_inference"
    AUDIO_PROCESSING = "audio_processing"
    IMAGE_PROCESSING = "image_processing"
    TEXT_PROCESSING = "text_processing"
    CACHE_OPERATION = "cache_operation"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    CREATOR_WORKFLOW = "creator_workflow"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    SEO_PROCESSING = "seo_processing"
    DISTRIBUTION = "distribution"

class TraceLevel(Enum):
    """Niveaux de trace"""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SpanData:
    """Données d'un span de trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    span_type: SpanType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "ok"
    error: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class TraceContext:
    """Contexte de trace distribué"""
    trace_id: str
    span_id: str
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)

@dataclass
class TracingConfig:
    """Configuration du tracing distribué"""
    service_name: str
    version: str = "1.0.0"
    environment: str = "production"
    
    # Sampling configuration
    sampling_rate: float = 1.0  # 100% sampling
    trace_sampling_enabled: bool = True
    
    # Export configuration
    jaeger_endpoint: Optional[str] = None
    console_export_enabled: bool = False
    custom_exporters: List[str] = field(default_factory=list)
    
    # Performance configuration
    max_queue_size: int = 2048
    export_timeout_ms: int = 30000
    max_export_batch_size: int = 512
    
    # Creator-specific configuration
    creator_workflow_tracing: bool = True
    ml_model_tracing: bool = True
    business_logic_tracing: bool = True
    performance_sensitive_tracing: bool = True
    
    # Retention and storage
    trace_retention_days: int = 7
    high_cardinality_tags_enabled: bool = False

class DistributedTracingEngine:
    """
    🔍 Moteur de tracing distribué enterprise
    
    Expertise combinée:
    - Lead Dev IA: Intelligence des traces ML et observabilité prédictive
    - Backend Senior: Architecture distribuée et performance
    - ML Engineer: Tracing des pipelines ML et monitoring modèles
    - DBA: Corrélation traces-données et optimisation requêtes
    - Sécurité: Protection des traces et audit de sécurité
    - Microservices: Tracing cross-service et circuit breakers
    - Audio: Tracing spécialisé multimédia et latence audio
    - DevOps: Infrastructure observabilité et monitoring production
    """
    
    def __init__(
        self,
        config: TracingConfig,
        creator_type: Optional[CreatorType] = None
    ):
        """
        Initialise le moteur de tracing distribué
        
        Args:
            config: Configuration du tracing
            creator_type: Type de créateur pour le tracing spécialisé
        """
        self.config = config
        self.creator_type = creator_type
        
        # État du tracing engine
        self.engine_state = {
            "initialized": False,
            "running": False,
            "spans_created": 0,
            "spans_finished": 0,
            "errors_count": 0,
            "active_traces": 0,
            "export_count": 0,
            "last_export": None
        }
        
        # Stockage des traces actives
        self.active_spans: Dict[str, SpanData] = {}
        self.completed_traces: deque = deque(maxlen=1000)  # Recent traces
        self.trace_contexts: Dict[str, TraceContext] = {}
        
        # Performance metrics
        self.performance_metrics = {
            "span_creation_latency_ms": deque(maxlen=1000),
            "trace_completion_times": deque(maxlen=1000),
            "export_latency_ms": deque(maxlen=100)
        }
        
        # OpenTelemetry components
        self.tracer_provider = None
        self.tracer = None
        self.span_processors = []
        
        # Copyright protection
        self._display_copyright_notice()
        
        # Initialize tracing infrastructure
        self._initialize_tracing_infrastructure()
        
        logger.info(f"🔍 DistributedTracingEngine initialized")
        logger.info(f"🏷️  Service: {config.service_name}")
        logger.info(f"👤 Creator: {creator_type.value if creator_type else 'All'}")
        logger.info(f"📊 Sampling rate: {config.sampling_rate * 100}%")
    
    def _display_copyright_notice(self):
        """Afficher la notice de protection des droits d'auteur"""
        logger.info("="*80)
        logger.info("🔍 Distributed Tracing Engine - Enterprise MLOps")
        logger.info("🔒 PROPRIETARY SOFTWARE - Fahed Mlaiel (mlaiel@live.de)")
        logger.info("⚠️  Unauthorized use, reproduction, or distribution is prohibited")
        logger.info("="*80)
    
    def _initialize_tracing_infrastructure(self):
        """Initialise l'infrastructure de tracing"""
        try:
            if OPENTELEMETRY_AVAILABLE:
                self._initialize_opentelemetry()
            else:
                self._initialize_fallback_tracing()
            
            # Initialize creator-specific tracing
            if self.creator_type:
                self._initialize_creator_specific_tracing()
            
            self.engine_state["initialized"] = True
            logger.info("✅ Tracing infrastructure initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize tracing infrastructure: {e}")
            self.engine_state["errors_count"] += 1
    
    def _initialize_opentelemetry(self):
        """Initialise OpenTelemetry"""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.config.service_name,
                "service.version": self.config.version,
                "deployment.environment": self.config.environment,
                "creator.type": self.creator_type.value if self.creator_type else "all",
                "platform": "ainflue_creator_economy"
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # Configure span processors and exporters
            self._configure_span_exporters()
            
            # Get tracer
            self.tracer = trace.get_tracer(
                self.config.service_name,
                self.config.version
            )
            
            logger.info("✅ OpenTelemetry initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenTelemetry: {e}")
            raise
    
    def _configure_span_exporters(self):
        """Configure les exporteurs de spans"""
        try:
            # Console exporter for development
            if self.config.console_export_enabled:
                console_exporter = ConsoleSpanExporter()
                console_processor = BatchSpanProcessor(console_exporter)
                self.tracer_provider.add_span_processor(console_processor)
                self.span_processors.append(console_processor)
                logger.info("✅ Console span exporter configured")
            
            # Jaeger exporter for production
            if self.config.jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    agent_host_name="localhost",
                    agent_port=6831,
                    collector_endpoint=self.config.jaeger_endpoint
                )
                jaeger_processor = BatchSpanProcessor(
                    jaeger_exporter,
                    max_queue_size=self.config.max_queue_size,
                    export_timeout_millis=self.config.export_timeout_ms,
                    max_export_batch_size=self.config.max_export_batch_size
                )
                self.tracer_provider.add_span_processor(jaeger_processor)
                self.span_processors.append(jaeger_processor)
                logger.info("✅ Jaeger span exporter configured")
            
            # Custom exporters
            for exporter_name in self.config.custom_exporters:
                # Placeholder for custom exporter initialization
                logger.info(f"📤 Custom exporter {exporter_name} would be configured here")
                
        except Exception as e:
            logger.error(f"❌ Failed to configure span exporters: {e}")
            raise
    
    def _initialize_fallback_tracing(self):
        """Initialise le tracing de fallback sans OpenTelemetry"""
        logger.info("🔄 Initializing fallback tracing implementation")
        
        # Create mock tracer
        self.tracer = MockTracer()
        
        # Start background thread for trace processing
        self.fallback_thread = threading.Thread(
            target=self._fallback_trace_processor,
            daemon=True
        )
        self.fallback_thread.start()
        
        logger.info("✅ Fallback tracing initialized")
    
    def _fallback_trace_processor(self):
        """Processeur de traces pour le mode fallback"""
        while True:
            try:
                # Process completed traces
                if self.completed_traces:
                    self._process_fallback_traces()
                
                time.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"❌ Error in fallback trace processor: {e}")
                time.sleep(5)  # Error recovery delay
    
    def _process_fallback_traces(self):
        """Traite les traces en mode fallback"""
        try:
            # Simple logging of traces (in production, send to external system)
            while self.completed_traces:
                trace_data = self.completed_traces.popleft()
                logger.debug(f"🔍 Trace: {trace_data['operation_name']} - {trace_data['duration_ms']:.2f}ms")
                
        except Exception as e:
            logger.error(f"❌ Error processing fallback traces: {e}")
    
    def _initialize_creator_specific_tracing(self):
        """Initialise le tracing spécifique au type de créateur"""
        
        creator_configs = {
            CreatorType.MUSICIAN: {
                "audio_processing_tracing": True,
                "genre_classification_tracing": True,
                "audio_quality_tracing": True,
                "music_recommendation_tracing": True
            },
            CreatorType.BLOGGER: {
                "text_processing_tracing": True,
                "seo_analysis_tracing": True,
                "content_quality_tracing": True,
                "readability_tracing": True
            },
            CreatorType.PHOTOGRAPHER: {
                "image_processing_tracing": True,
                "aesthetic_analysis_tracing": True,
                "composition_tracing": True,
                "quality_assessment_tracing": True
            },
            CreatorType.INFLUENCER: {
                "engagement_tracing": True,
                "reach_analysis_tracing": True,
                "sentiment_tracing": True,
                "platform_analytics_tracing": True
            },
            CreatorType.COMEDIAN: {
                "humor_analysis_tracing": True,
                "timing_tracing": True,
                "audience_reaction_tracing": True,
                "performance_metrics_tracing": True
            }
        }
        
        creator_config = creator_configs.get(self.creator_type, {})
        logger.info(f"✅ {self.creator_type.value} specific tracing configured: {list(creator_config.keys())}")
    
    @contextmanager
    def start_span(
        self,
        operation_name: str,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        parent_context: Optional[TraceContext] = None,
        tags: Optional[Dict[str, Any]] = None,
        creator_type: Optional[CreatorType] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Context manager pour créer un span de trace
        
        Args:
            operation_name: Nom de l'opération
            span_type: Type de span
            parent_context: Contexte parent
            tags: Tags additionnels
            creator_type: Type de créateur
            model_id: ID du modèle ML
            user_id: ID de l'utilisateur
        
        Yields:
            SpanData: Le span créé
        """
        span_start_time = time.time()
        
        try:
            # Create span data
            span_data = self._create_span_data(
                operation_name=operation_name,
                span_type=span_type,
                parent_context=parent_context,
                tags=tags or {},
                creator_type=creator_type or self.creator_type,
                model_id=model_id,
                user_id=user_id
            )
            
            # Track performance
            creation_time = (time.time() - span_start_time) * 1000
            self.performance_metrics["span_creation_latency_ms"].append(creation_time)
            
            # Update state
            self.engine_state["spans_created"] += 1
            self.engine_state["active_traces"] = len(self.active_spans)
            
            # Store active span
            self.active_spans[span_data.span_id] = span_data
            
            logger.debug(f"🔍 Started span: {operation_name} [{span_data.span_id}]")
            
            # Yield span for user operations
            yield span_data
            
        except Exception as e:
            logger.error(f"❌ Error in span {operation_name}: {e}")
            span_data.status = "error"
            span_data.error = str(e)
            self.engine_state["errors_count"] += 1
            
        finally:
            # Finish span
            self._finish_span(span_data)
    
    def _create_span_data(
        self,
        operation_name: str,
        span_type: SpanType,
        parent_context: Optional[TraceContext],
        tags: Dict[str, Any],
        creator_type: Optional[CreatorType],
        model_id: Optional[str],
        user_id: Optional[str]
    ) -> SpanData:
        """Crée les données d'un span"""
        
        # Generate IDs
        span_id = str(uuid.uuid4())
        
        if parent_context:
            trace_id = parent_context.trace_id
            parent_span_id = parent_context.span_id
        else:
            trace_id = str(uuid.uuid4())
            parent_span_id = None
        
        # Create span data
        span_data = SpanData(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.config.service_name,
            span_type=span_type,
            start_time=datetime.now(),
            tags=tags,
            creator_type=creator_type,
            model_id=model_id,
            user_id=user_id
        )
        
        # Add default tags
        span_data.tags.update({
            "service.name": self.config.service_name,
            "service.version": self.config.version,
            "environment": self.config.environment,
            "span.type": span_type.value
        })
        
        if creator_type:
            span_data.tags["creator.type"] = creator_type.value
        
        if model_id:
            span_data.tags["model.id"] = model_id
            
        if user_id:
            span_data.tags["user.id"] = user_id
        
        return span_data
    
    def _finish_span(self, span_data: SpanData):
        """Termine un span"""
        try:
            # Set end time and calculate duration
            span_data.end_time = datetime.now()
            duration = (span_data.end_time - span_data.start_time).total_seconds() * 1000
            span_data.duration_ms = duration
            
            # Track performance
            self.performance_metrics["trace_completion_times"].append(duration)
            
            # Update state
            self.engine_state["spans_finished"] += 1
            self.engine_state["active_traces"] = len(self.active_spans) - 1
            
            # Remove from active spans
            if span_data.span_id in self.active_spans:
                del self.active_spans[span_data.span_id]
            
            # Add to completed traces
            self.completed_traces.append({
                "trace_id": span_data.trace_id,
                "span_id": span_data.span_id,
                "operation_name": span_data.operation_name,
                "duration_ms": span_data.duration_ms,
                "status": span_data.status,
                "tags": span_data.tags,
                "timestamp": span_data.start_time.isoformat()
            })
            
            logger.debug(f"🔍 Finished span: {span_data.operation_name} [{span_data.span_id}] - {duration:.2f}ms")
            
            # Export span if needed
            self._export_span(span_data)
            
        except Exception as e:
            logger.error(f"❌ Error finishing span: {e}")
            self.engine_state["errors_count"] += 1
    
    def _export_span(self, span_data: SpanData):
        """Exporte un span vers les systèmes externes"""
        try:
            export_start = time.time()
            
            # In fallback mode, just log the span
            if not OPENTELEMETRY_AVAILABLE:
                self._export_span_fallback(span_data)
            else:
                # OpenTelemetry handles export automatically via span processors
                pass
            
            # Track export performance
            export_time = (time.time() - export_start) * 1000
            self.performance_metrics["export_latency_ms"].append(export_time)
            
            self.engine_state["export_count"] += 1
            self.engine_state["last_export"] = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error exporting span: {e}")
            self.engine_state["errors_count"] += 1
    
    def _export_span_fallback(self, span_data: SpanData):
        """Exporte un span en mode fallback"""
        # In production, this would send to external tracing system
        logger.debug(f"📤 Export span: {span_data.operation_name} - {span_data.duration_ms:.2f}ms")
    
    # High-level tracing methods for Creator Economy workflows
    
    @contextmanager
    def trace_ml_inference(
        self,
        model_name: str,
        model_version: str,
        input_size: Optional[int] = None,
        creator_type: Optional[CreatorType] = None
    ):
        """Trace une inférence ML"""
        tags = {
            "ml.model.name": model_name,
            "ml.model.version": model_version,
            "ml.operation": "inference"
        }
        
        if input_size:
            tags["ml.input.size"] = input_size
            
        with self.start_span(
            operation_name=f"ml_inference_{model_name}",
            span_type=SpanType.ML_INFERENCE,
            tags=tags,
            creator_type=creator_type
        ) as span:
            yield span
    
    @contextmanager
    def trace_creator_workflow(
        self,
        workflow_name: str,
        creator_id: str,
        content_type: str,
        creator_type: Optional[CreatorType] = None
    ):
        """Trace un workflow de créateur"""
        tags = {
            "creator.workflow": workflow_name,
            "creator.id": creator_id,
            "content.type": content_type
        }
        
        with self.start_span(
            operation_name=f"creator_workflow_{workflow_name}",
            span_type=SpanType.CREATOR_WORKFLOW,
            tags=tags,
            creator_type=creator_type,
            user_id=creator_id
        ) as span:
            yield span
    
    @contextmanager
    def trace_audio_processing(
        self,
        operation: str,
        audio_format: str,
        duration_seconds: Optional[float] = None
    ):
        """Trace le traitement audio (pour musiciens)"""
        tags = {
            "audio.operation": operation,
            "audio.format": audio_format
        }
        
        if duration_seconds:
            tags["audio.duration"] = duration_seconds
        
        with self.start_span(
            operation_name=f"audio_processing_{operation}",
            span_type=SpanType.AUDIO_PROCESSING,
            tags=tags,
            creator_type=CreatorType.MUSICIAN
        ) as span:
            yield span
    
    @contextmanager
    def trace_image_processing(
        self,
        operation: str,
        image_format: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ):
        """Trace le traitement d'image (pour photographes)"""
        tags = {
            "image.operation": operation,
            "image.format": image_format
        }
        
        if width and height:
            tags["image.width"] = width
            tags["image.height"] = height
            tags["image.pixels"] = width * height
        
        with self.start_span(
            operation_name=f"image_processing_{operation}",
            span_type=SpanType.IMAGE_PROCESSING,
            tags=tags,
            creator_type=CreatorType.PHOTOGRAPHER
        ) as span:
            yield span
    
    @contextmanager
    def trace_text_processing(
        self,
        operation: str,
        text_length: Optional[int] = None,
        language: Optional[str] = None
    ):
        """Trace le traitement de texte (pour blogueurs)"""
        tags = {
            "text.operation": operation
        }
        
        if text_length:
            tags["text.length"] = text_length
            
        if language:
            tags["text.language"] = language
        
        with self.start_span(
            operation_name=f"text_processing_{operation}",
            span_type=SpanType.TEXT_PROCESSING,
            tags=tags,
            creator_type=CreatorType.BLOGGER
        ) as span:
            yield span
    
    @contextmanager
    def trace_database_query(
        self,
        query_type: str,
        table_name: str,
        duration_hint: Optional[str] = None
    ):
        """Trace une requête base de données"""
        tags = {
            "db.operation": query_type,
            "db.table": table_name
        }
        
        if duration_hint:
            tags["db.duration_hint"] = duration_hint
        
        with self.start_span(
            operation_name=f"db_{query_type}_{table_name}",
            span_type=SpanType.DATABASE_QUERY,
            tags=tags
        ) as span:
            yield span
    
    @contextmanager
    def trace_http_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None
    ):
        """Trace une requête HTTP"""
        tags = {
            "http.method": method,
            "http.url": url
        }
        
        if status_code:
            tags["http.status_code"] = status_code
        
        with self.start_span(
            operation_name=f"http_{method}",
            span_type=SpanType.HTTP_REQUEST,
            tags=tags
        ) as span:
            yield span
    
    # Trace analysis and monitoring methods
    
    def get_tracing_metrics(self) -> Dict[str, Any]:
        """Obtient les métriques de tracing"""
        try:
            # Calculate performance statistics
            metrics = {
                "engine_state": self.engine_state.copy(),
                "performance": {}
            }
            
            for metric_name, values in self.performance_metrics.items():
                if values:
                    metrics["performance"][metric_name] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": sorted(values)[int(0.95 * (len(values) - 1))] if len(values) > 1 else values[0]
                    }
                else:
                    metrics["performance"][metric_name] = {"count": 0}
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting tracing metrics: {e}")
            return {"error": str(e)}
    
    def get_trace_summary(self, hours_back: int = 1) -> Dict[str, Any]:
        """Obtient un résumé des traces"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Analyze recent traces
            recent_traces = [
                trace for trace in self.completed_traces
                if datetime.fromisoformat(trace["timestamp"]) > cutoff_time
            ]
            
            if not recent_traces:
                return {"error": "No traces in the specified period"}
            
            # Calculate statistics
            durations = [trace["duration_ms"] for trace in recent_traces]
            operations = defaultdict(int)
            error_count = 0
            
            for trace in recent_traces:
                operations[trace["operation_name"]] += 1
                if trace["status"] == "error":
                    error_count += 1
            
            summary = {
                "period_hours": hours_back,
                "total_traces": len(recent_traces),
                "error_rate": error_count / len(recent_traces) if recent_traces else 0,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
                "p95_duration_ms": sorted(durations)[int(0.95 * (len(durations) - 1))] if len(durations) > 1 else durations[0] if durations else 0,
                "top_operations": sorted(operations.items(), key=lambda x: x[1], reverse=True)[:10],
                "creator_type": self.creator_type.value if self.creator_type else "all",
                "service_name": self.config.service_name
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating trace summary: {e}")
            return {"error": str(e)}
    
    def find_slow_traces(self, threshold_ms: float = 1000, hours_back: int = 1) -> List[Dict[str, Any]]:
        """Trouve les traces lentes"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            slow_traces = []
            for trace in self.completed_traces:
                if (datetime.fromisoformat(trace["timestamp"]) > cutoff_time and 
                    trace["duration_ms"] > threshold_ms):
                    slow_traces.append(trace)
            
            # Sort by duration (slowest first)
            slow_traces.sort(key=lambda x: x["duration_ms"], reverse=True)
            
            return slow_traces
            
        except Exception as e:
            logger.error(f"❌ Error finding slow traces: {e}")
            return []
    
    def find_error_traces(self, hours_back: int = 1) -> List[Dict[str, Any]]:
        """Trouve les traces avec erreurs"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            error_traces = []
            for trace in self.completed_traces:
                if (datetime.fromisoformat(trace["timestamp"]) > cutoff_time and 
                    trace["status"] == "error"):
                    error_traces.append(trace)
            
            return error_traces
            
        except Exception as e:
            logger.error(f"❌ Error finding error traces: {e}")
            return []
    
    def export_traces(self, filepath: str, hours_back: int = 24):
        """Exporte les traces vers un fichier"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Collect traces to export
            traces_to_export = []
            for trace in self.completed_traces:
                if datetime.fromisoformat(trace["timestamp"]) > cutoff_time:
                    traces_to_export.append(trace)
            
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "service_name": self.config.service_name,
                    "creator_type": self.creator_type.value if self.creator_type else None,
                    "period_hours": hours_back,
                    "total_traces": len(traces_to_export)
                },
                "tracing_config": {
                    "service_name": self.config.service_name,
                    "version": self.config.version,
                    "environment": self.config.environment,
                    "sampling_rate": self.config.sampling_rate
                },
                "engine_metrics": self.get_tracing_metrics(),
                "trace_summary": self.get_trace_summary(hours_back),
                "traces": traces_to_export
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"🔍 Traces exported to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting traces: {e}")
            raise
    
    def shutdown(self):
        """Arrête le moteur de tracing"""
        try:
            logger.info("⏹️  Shutting down tracing engine...")
            
            # Finish all active spans
            for span_data in list(self.active_spans.values()):
                span_data.status = "cancelled"
                self._finish_span(span_data)
            
            # Shutdown span processors
            if OPENTELEMETRY_AVAILABLE and self.span_processors:
                for processor in self.span_processors:
                    processor.shutdown()
            
            self.engine_state["running"] = False
            
            logger.info("🛑 Tracing engine shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error shutting down tracing engine: {e}")

# Factory functions for easy usage

def create_distributed_tracer(
    service_name: str,
    creator_type: str,
    environment: str = "production",
    sampling_rate: float = 1.0,
    jaeger_endpoint: Optional[str] = None
) -> DistributedTracingEngine:
    """
    Factory function pour créer un moteur de tracing distribué
    
    Args:
        service_name: Nom du service
        creator_type: Type de créateur
        environment: Environnement (dev, staging, production)
        sampling_rate: Taux d'échantillonnage (0.0 à 1.0)
        jaeger_endpoint: Endpoint Jaeger pour l'export
    
    Returns:
        Instance configurée de DistributedTracingEngine
    """
    
    # Convert string to enum
    try:
        creator_enum = CreatorType(creator_type.lower())
    except ValueError:
        logger.warning(f"⚠️  Unknown creator type: {creator_type}, using ALL")
        creator_enum = CreatorType.ALL
    
    # Create configuration
    config = TracingConfig(
        service_name=service_name,
        environment=environment,
        sampling_rate=sampling_rate,
        jaeger_endpoint=jaeger_endpoint,
        console_export_enabled=(environment != "production")
    )
    
    # Create tracing engine
    tracer = DistributedTracingEngine(
        config=config,
        creator_type=creator_enum
    )
    
    logger.info(f"🔍 Created distributed tracer for {creator_type} service {service_name}")
    
    return tracer

# Enterprise usage example
if __name__ == "__main__":
    """
    Exemple d'utilisation enterprise du moteur de tracing distribué
    """
    
    # Create tracer for musician service
    tracer = create_distributed_tracer(
        service_name="ainflue_music_service",
        creator_type="musician",
        environment="development",
        sampling_rate=1.0
    )
    
    try:
        logger.info("🎵 Starting distributed tracing demo...")
        
        # Simulate musician workflow
        with tracer.trace_creator_workflow(
            workflow_name="music_upload_processing",
            creator_id="musician_123",
            content_type="audio",
            creator_type=CreatorType.MUSICIAN
        ) as workflow_span:
            
            workflow_span.tags["workflow.step"] = "audio_upload"
            workflow_span.logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "audio_file_received",
                "file_size_mb": 25.4
            })
            
            # Simulate audio processing
            with tracer.trace_audio_processing(
                operation="quality_analysis",
                audio_format="mp3",
                duration_seconds=180.5
            ) as audio_span:
                
                audio_span.tags["quality_score"] = 0.89
                time.sleep(0.1)  # Simulate processing time
            
            # Simulate ML inference
            with tracer.trace_ml_inference(
                model_name="genre_classifier",
                model_version="v2.1",
                input_size=1024,
                creator_type=CreatorType.MUSICIAN
            ) as ml_span:
                
                ml_span.tags["predicted_genre"] = "electronic"
                ml_span.tags["confidence"] = 0.94
                time.sleep(0.05)  # Simulate inference time
            
            # Simulate database operations
            with tracer.trace_database_query(
                query_type="INSERT",
                table_name="music_tracks"
            ) as db_span:
                
                db_span.tags["rows_affected"] = 1
                time.sleep(0.02)  # Simulate DB time
            
            workflow_span.tags["workflow.status"] = "completed"
            workflow_span.logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_completed",
                "processing_time_ms": 152.3
            })
        
        # Simulate some more operations
        for i in range(5):
            with tracer.trace_http_request(
                method="POST",
                url=f"/api/music/recommendations/{i}",
                status_code=200
            ):
                time.sleep(0.01)  # Simulate request time
        
        # Wait for processing
        time.sleep(2)
        
        # Get tracing metrics
        metrics = tracer.get_tracing_metrics()
        logger.info(f"📊 Tracing Metrics: {json.dumps(metrics, indent=2, default=str)}")
        
        # Get trace summary
        summary = tracer.get_trace_summary(hours_back=1)
        logger.info(f"📈 Trace Summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Find slow traces
        slow_traces = tracer.find_slow_traces(threshold_ms=50)
        if slow_traces:
            logger.info(f"🐌 Found {len(slow_traces)} slow traces")
        
        # Export traces
        tracer.export_traces("/tmp/traces_export.json", hours_back=1)
        
    finally:
        # Shutdown tracer
        tracer.shutdown()
        logger.info("✅ Distributed tracing demo completed successfully")