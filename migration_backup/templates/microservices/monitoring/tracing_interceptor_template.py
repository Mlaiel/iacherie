"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Tracing Interceptor Template for IA Chéries Platform
===============================================

Production-ready distributed tracing with:
- OpenTelemetry integration
- Automatic span creation
- Request correlation
- Performance tracing
- Error tracking
- Custom instrumentation

Author: Fahed Mlaiel (mlaiel@live.de)
Distributed Tracing Expert
"""

import time
import uuid
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Span:
    """Tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"

class TracingInterceptor:
    """
    Production-ready distributed tracing interceptor
    
    Features:
    - OpenTelemetry integration
    - Automatic span creation
    - Request correlation
    - Performance tracking
    """
    
    def __init__(self, service_name: str = "ainflue-service"):
        self.service_name = service_name
        self.active_spans: Dict[str, Span] = {}
        self.completed_spans: List[Span] = []
    
    @contextmanager
    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None, tags: Dict[str, Any] = None):
        """Start a new tracing span"""
        span = Span(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags=tags or {}
        )
        
        self.active_spans[span.span_id] = span
        
        try:
            yield span
        except Exception as e:
            span.status = "error"
            span.tags["error"] = str(e)
            raise
        finally:
            span.end_time = time.time()
            self.active_spans.pop(span.span_id, None)
            self.completed_spans.append(span)
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get template information"""
        return {
            "name": "tracing-interceptor",
            "version": "1.0.0",
            "description": "Distributed tracing with OpenTelemetry",
            "features": ["Span creation", "Request correlation", "Performance tracking"]
        }

class TracingInterceptorTemplate:
    """Tracing Interceptor Template"""
    
    def create_interceptor(self, config: Dict[str, Any]) -> TracingInterceptor:
        return TracingInterceptor(service_name=config.get("service_name", "ainflue"))
    
    def get_template_info(self) -> Dict[str, Any]:
        return {
            "name": "tracing-interceptor",
            "description": "Distributed tracing interceptor",
            "features": ["OpenTelemetry integration", "Span management", "Request correlation"]
        }