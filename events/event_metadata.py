"""🚀 Event Metadata System - IA Influencer Agent Platform
==========================================================
Module: events/event_metadata.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 CONTEXTUAL METADATA MANAGEMENT
Advanced event metadata and context management system
- Rich metadata collection and management
- Context propagation across service boundaries
- Tracing and correlation support
- Performance and debugging information
- Business context preservation
"""

import logging
import platform
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json

from .core.base_event import BaseEvent

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata"""
    SYSTEM = "system"
    BUSINESS = "business"
    TECHNICAL = "technical"
    TRACING = "tracing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER = "user"


@dataclass
class TracingContext:
    """Distributed tracing context"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)
    
    def create_child_span(self) -> 'TracingContext':
        """Create a child span context"""
        return TracingContext(
            trace_id=self.trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=self.span_id,
            baggage=self.baggage.copy()
        )


@dataclass
class PerformanceMetadata:
    """Performance-related metadata"""
    processing_start: Optional[datetime] = None
    processing_end: Optional[datetime] = None
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    network_calls: int = 0
    database_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate processing duration in milliseconds"""
        if self.processing_start and self.processing_end:
            duration = (self.processing_end - self.processing_start).total_seconds() * 1000
            self.duration_ms = duration
            return duration
        return None


@dataclass
class SystemMetadata:
    """System-level metadata"""
    hostname: str = field(default_factory=lambda: platform.node())
    platform: str = field(default_factory=lambda: platform.platform())
    python_version: str = field(default_factory=lambda: platform.python_version())
    process_id: int = field(default_factory=lambda: os.getpid())
    timezone: str = field(default_factory=lambda: str(datetime.now().astimezone().tzinfo))
    environment: Optional[str] = None
    service_name: Optional[str] = None
    service_version: Optional[str] = None
    deployment_id: Optional[str] = None


@dataclass
class BusinessMetadata:
    """Business context metadata"""
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    workflow_id: Optional[str] = None
    campaign_id: Optional[str] = None
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    business_tags: List[str] = field(default_factory=list)


class EventMetadataManager:
    """Advanced event metadata management system"""
    
    def __init__(self,
                 auto_collect_system -> None: bool = True,
                 auto_collect_performance -> None: bool = True,
                 enable_tracing -> None: bool = True) -> None:
        """Initialize metadata manager
        
        Args:
            auto_collect_system: Automatically collect system metadata
            auto_collect_performance: Automatically collect performance metadata
            enable_tracing: Enable distributed tracing
        """
        self.auto_collect_system = auto_collect_system
        self.auto_collect_performance = auto_collect_performance
        self.enable_tracing = enable_tracing
        
        # Metadata providers
        self.metadata_providers: Dict[str, callable] = {}
        
        # Current context
        self.current_tracing_context: Optional[TracingContext] = None
        self.current_business_context: Optional[BusinessMetadata] = None
        
        # System metadata (cached)
        self._system_metadata: Optional[SystemMetadata] = None
        
        logger.info("Event metadata manager initialized")
    
    def create_metadata(self,
                       event: BaseEvent,
                       additional_metadata: Optional[Dict[str, Any]] = None,
                       include_performance: bool = None,
                       include_tracing: bool = None) -> Dict[str, Any]:
        """Create comprehensive metadata for an event
        
        Args:
            event: Event to create metadata for
            additional_metadata: Additional custom metadata
            include_performance: Override performance collection
            include_tracing: Override tracing collection
            
        Returns:
            Complete metadata dictionary
        """
        metadata = {}
        
        # Start with existing metadata
        if event.metadata:
            metadata.update(event.metadata)
        
        # Add system metadata
        if self.auto_collect_system:
            system_meta = self.get_system_metadata()
            metadata["system"] = asdict(system_meta)
        
        # Add performance metadata
        if include_performance or (include_performance is None and self.auto_collect_performance):
            perf_meta = self.create_performance_metadata()
            metadata["performance"] = asdict(perf_meta)
        
        # Add tracing metadata
        if include_tracing or (include_tracing is None and self.enable_tracing):
            trace_meta = self.get_tracing_metadata()
            if trace_meta:
                metadata["tracing"] = asdict(trace_meta)
        
        # Add business context
        if self.current_business_context:
            metadata["business"] = asdict(self.current_business_context)
        
        # Add timestamp metadata
        metadata["timestamps"] = {
            "created_at": datetime.utcnow().isoformat(),
            "timezone": str(datetime.now().astimezone().tzinfo)
        }
        
        # Add event-specific metadata
        metadata["event"] = {
            "source": event.source or "unknown",
            "correlation_id": event.correlation_id,
            "causation_id": event.causation_id,
            "aggregate_id": event.aggregate_id,
            "aggregate_version": event.aggregate_version
        }
        
        # Add custom metadata providers
        for provider_name, provider_func in self.metadata_providers.items():
            try:
                provider_metadata = provider_func(event)
                if provider_metadata:
                    metadata[provider_name] = provider_metadata
            except Exception as e:
                logger.error(f"Metadata provider {provider_name} failed: {e}")
        
        # Add additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    def enrich_event(self,
                    event: BaseEvent,
                    additional_metadata: Optional[Dict[str, Any]] = None) -> BaseEvent:
        """Enrich an event with comprehensive metadata
        
        Args:
            event: Event to enrich
            additional_metadata: Additional custom metadata
            
        Returns:
            Event with enriched metadata
        """
        enriched_metadata = self.create_metadata(event, additional_metadata)
        event.metadata = enriched_metadata
        return event
    
    def set_tracing_context(self, context: TracingContext) -> None:
        """Set current tracing context"""
        self.current_tracing_context = context
        logger.debug(f"Tracing context set: {context.trace_id}")
    
    def create_tracing_context(self,
                              trace_id: Optional[str] = None,
                              span_id: Optional[str] = None) -> TracingContext:
        """Create new tracing context"""
        context = TracingContext(
            trace_id=trace_id or str(uuid.uuid4()),
            span_id=span_id or str(uuid.uuid4())
        )
        self.set_tracing_context(context)
        return context
    
    def get_tracing_metadata(self) -> Optional[TracingContext]:
        """Get current tracing metadata"""
        return self.current_tracing_context
    
    def set_business_context(self, context: BusinessMetadata) -> None:
        """Set current business context"""
        self.current_business_context = context
        logger.debug(f"Business context set for user: {context.user_id}")
    
    def create_business_context(self,
                               user_id: Optional[str] = None,
                               tenant_id: Optional[str] = None,
                               session_id: Optional[str] = None,
                               **kwargs) -> BusinessMetadata:
        """Create business context"""
        context = BusinessMetadata(
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            **kwargs
        )
        self.set_business_context(context)
        return context
    
    def get_system_metadata(self) -> SystemMetadata:
        """Get system metadata (cached)"""
        if self._system_metadata is None:
            self._system_metadata = SystemMetadata()
        return self._system_metadata
    
    def create_performance_metadata(self) -> PerformanceMetadata:
        """Create performance metadata"""
        return PerformanceMetadata(
            processing_start=datetime.utcnow()
        )
    
    def register_metadata_provider(self,
                                  name: str,
                                  provider_func: callable) -> None:
        """Register a custom metadata provider
        
        Args:
            name: Provider name
            provider_func: Function that takes an event and returns metadata dict
        """
        self.metadata_providers[name] = provider_func
        logger.info(f"Metadata provider registered: {name}")
    
    def unregister_metadata_provider(self, name: str) -> bool:
        """Unregister a metadata provider
        
        Args:
            name: Provider name
            
        Returns:
            True if provider was removed
        """
        if name in self.metadata_providers:
            del self.metadata_providers[name]
            logger.info(f"Metadata provider unregistered: {name}")
            return True
        return False
    
    def extract_correlation_chain(self, event: BaseEvent) -> List[str]:
        """Extract correlation chain from event metadata
        
        Args:
            event: Event to analyze
            
        Returns:
            List of correlation IDs in chain
        """
        chain = []
        
        if event.correlation_id:
            chain.append(event.correlation_id)
        
        if event.causation_id:
            chain.append(event.causation_id)
        
        # Look for additional correlation IDs in metadata
        if event.metadata:
            trace_meta = event.metadata.get("tracing", {})
            if isinstance(trace_meta, dict):
                if "trace_id" in trace_meta:
                    chain.append(trace_meta["trace_id"])
        
        return chain
    
    def create_correlation_id(self) -> str:
        """Create a new correlation ID"""
        return str(uuid.uuid4())
    
    def propagate_context(self,
                         source_event: BaseEvent,
                         target_event: BaseEvent) -> BaseEvent:
        """Propagate context from source to target event
        
        Args:
            source_event: Source event with context
            target_event: Target event to receive context
            
        Returns:
            Target event with propagated context
        """
        # Propagate correlation information
        if source_event.correlation_id:
            target_event.correlation_id = source_event.correlation_id
        
        target_event.causation_id = source_event.event_id
        
        # Propagate tracing context
        if source_event.metadata and "tracing" in source_event.metadata:
            trace_data = source_event.metadata["tracing"]
            if isinstance(trace_data, dict):
                # Create child span
                child_context = TracingContext(
                    trace_id=trace_data.get("trace_id", str(uuid.uuid4())),
                    span_id=str(uuid.uuid4()),
                    parent_span_id=trace_data.get("span_id"),
                    baggage=trace_data.get("baggage", {})
                )
                
                if not target_event.metadata:
                    target_event.metadata = {}
                target_event.metadata["tracing"] = asdict(child_context)
        
        # Propagate business context
        if source_event.metadata and "business" in source_event.metadata:
            if not target_event.metadata:
                target_event.metadata = {}
            target_event.metadata["business"] = source_event.metadata["business"]
        
        return target_event
    
    def get_metadata_summary(self, event: BaseEvent) -> Dict[str, Any]:
        """Get summary of event metadata
        
        Args:
            event: Event to summarize
            
        Returns:
            Metadata summary
        """
        if not event.metadata:
            return {"has_metadata": False}
        
        summary = {
            "has_metadata": True,
            "metadata_keys": list(event.metadata.keys()),
            "metadata_size_bytes": len(json.dumps(event.metadata)),
            "correlation_chain": self.extract_correlation_chain(event)
        }
        
        # Add specific metadata info
        if "system" in event.metadata:
            summary["has_system_metadata"] = True
        if "performance" in event.metadata:
            summary["has_performance_metadata"] = True
        if "tracing" in event.metadata:
            summary["has_tracing_metadata"] = True
        if "business" in event.metadata:
            summary["has_business_metadata"] = True
        
        return summary
    
    def clean_sensitive_metadata(self, event: BaseEvent, 
                                sensitive_keys: List[str] = None) -> BaseEvent:
        """Remove sensitive information from event metadata
        
        Args:
            event: Event to clean
            sensitive_keys: List of sensitive keys to remove
            
        Returns:
            Event with cleaned metadata
        """
        if not event.metadata:
            return event
        
        default_sensitive_keys = [
            "password", "token", "secret", "key", "credential",
            "authorization", "cookie", "session_key"
        ]
        
        keys_to_remove = set(sensitive_keys or default_sensitive_keys)
        
        def clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            cleaned = {}
            for k, v in d.items():
                if any(sensitive in k.lower() for sensitive in keys_to_remove):
                    cleaned[k] = "[REDACTED]"
                elif isinstance(v, dict):
                    cleaned[k] = clean_dict(v)
                elif isinstance(v, list):
                    cleaned[k] = [
                        clean_dict(item) if isinstance(item, dict) else item
                        for item in v
                    ]
                else:
                    cleaned[k] = v
            return cleaned
        
        event.metadata = clean_dict(event.metadata)
        return event


# Global metadata manager instance
_global_metadata_manager: Optional[EventMetadataManager] = None


def get_global_metadata_manager() -> EventMetadataManager:
    """Get or create global metadata manager instance"""
    global _global_metadata_manager
    if _global_metadata_manager is None:
        _global_metadata_manager = EventMetadataManager()
    return _global_metadata_manager


def enrich_event_metadata(event: BaseEvent, **kwargs) -> BaseEvent:
    """Convenience function to enrich event metadata globally"""
    manager = get_global_metadata_manager()
    return manager.enrich_event(event, **kwargs)


def create_tracing_context(trace_id: Optional[str] = None) -> TracingContext:
    """Convenience function to create tracing context globally"""
    manager = get_global_metadata_manager()
    return manager.create_tracing_context(trace_id=trace_id)


def propagate_context(source: BaseEvent, target: BaseEvent) -> BaseEvent:
    """Convenience function to propagate context globally"""
    manager = get_global_metadata_manager()
    return manager.propagate_context(source, target)