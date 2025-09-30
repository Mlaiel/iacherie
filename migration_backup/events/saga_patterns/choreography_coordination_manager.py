#!/usr/bin/env python3
"""Choreography Coordination Manager - Event-Driven Saga Management
==================================================================

Event-driven choreography coordination for decentralized saga execution.
Manages saga workflows through event correlation and autonomous service
coordination without central orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ChoreographyStatus(Enum):
    """Choreography execution status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    STALLED = "stalled"


@dataclass
class DomainEvent:
    """Domain event for choreography communication"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_service: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Simple event bus for choreography coordination"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.published_events: List[DomainEvent] = []
    
    async def publish(self, event: DomainEvent):
        """Publish event to all subscribers"""
        self.published_events.append(event)
        
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event.event_type}: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)


class CorrelationService:
    """Service for tracking event correlations"""
    
    def __init__(self):
        self.correlations: Dict[str, Dict[str, Any]] = {}
    
    def create_correlation(self, correlation_id: str, context: Dict[str, Any]):
        """Create new correlation context"""
        self.correlations[correlation_id] = {
            "created_at": datetime.now(timezone.utc),
            "context": context,
            "events": [],
            "status": "active"
        }
    
    def add_event(self, correlation_id: str, event: DomainEvent):
        """Add event to correlation"""
        if correlation_id in self.correlations:
            self.correlations[correlation_id]["events"].append(event)
    
    def get_correlation(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get correlation data"""
        return self.correlations.get(correlation_id)


class ContentProcessingChoreography:
    """Choreography for content processing workflow"""
    
    def __init__(self, correlation_id: str, creator_id: str, content_id: str):
        self.correlation_id = correlation_id
        self.creator_id = creator_id
        self.content_id = content_id
        self.ai_analysis_completed = False
        self.protection_completed = False
        self.seo_completed = False
        self.distribution_ready = False
        self.started_at = datetime.now(timezone.utc)
    
    def is_ready_for_distribution(self) -> bool:
        """Check if ready for distribution step"""
        return self.ai_analysis_completed and self.protection_completed and self.seo_completed
    
    def mark_ai_completed(self):
        """Mark AI analysis as completed"""
        self.ai_analysis_completed = True
    
    def mark_protection_completed(self):
        """Mark protection as completed"""
        self.protection_completed = True
    
    def mark_seo_completed(self):
        """Mark SEO as completed"""
        self.seo_completed = True


class CollaborationWorkflowChoreography:
    """Choreography for collaboration workflow"""
    
    def __init__(self, correlation_id: str, requester_id: str):
        self.correlation_id = correlation_id
        self.requester_id = requester_id
        self.matches_found = False
        self.notifications_sent = False
        self.responses_received = False
        self.agreements_processed = False
        self.started_at = datetime.now(timezone.utc)


class ChoreographyCoordinationManager:
    """Manager for event-driven saga choreography"""
    
    def __init__(self, event_bus: EventBus, correlation_service: CorrelationService):
        self.event_bus = event_bus
        self.correlation_service = correlation_service
        self.active_choreographies: Dict[str, Any] = {}
        self.choreography_handlers: Dict[str, Callable] = {}
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register choreography event handlers"""
        # Content processing events
        self.event_bus.subscribe("content.uploaded", self._handle_content_uploaded)
        self.event_bus.subscribe("content.ai.analysis.completed", self._handle_ai_analysis_completed)
        self.event_bus.subscribe("content.protection.applied", self._handle_protection_applied)
        self.event_bus.subscribe("content.seo.optimized", self._handle_seo_optimized)
        self.event_bus.subscribe("content.distribution.completed", self._handle_distribution_completed)
        
        # Collaboration events
        self.event_bus.subscribe("collaboration.requested", self._handle_collaboration_requested)
        self.event_bus.subscribe("collaboration.matches.found", self._handle_matches_found)
        self.event_bus.subscribe("collaboration.notifications.sent", self._handle_notifications_sent)
        self.event_bus.subscribe("collaboration.responses.received", self._handle_responses_received)
        
        # Error events
        self.event_bus.subscribe("*.failed", self._handle_failure_event)
    
    async def start_content_processing_choreography(
        self, 
        content_upload_event: DomainEvent
    ) -> str:
        """Start content processing choreography"""
        correlation_id = str(uuid.uuid4())
        
        # Create choreography instance
        choreography = ContentProcessingChoreography(
            correlation_id=correlation_id,
            creator_id=content_upload_event.payload["creator_id"],
            content_id=content_upload_event.payload["content_id"]
        )
        
        self.active_choreographies[correlation_id] = choreography
        
        # Create correlation context
        self.correlation_service.create_correlation(correlation_id, {
            "choreography_type": "content_processing",
            "creator_id": content_upload_event.payload["creator_id"],
            "content_id": content_upload_event.payload["content_id"]
        })
        
        # Trigger AI analysis
        await self.event_bus.publish(DomainEvent(
            event_type="content.ai.analysis.requested",
            payload={
                "content_id": content_upload_event.payload["content_id"],
                "correlation_id": correlation_id,
                "analysis_type": "full"
            },
            correlation_id=correlation_id
        ))
        
        logger.info(f"Started content processing choreography: {correlation_id}")
        return correlation_id
    
    async def start_collaboration_choreography(
        self, 
        collaboration_request_event: DomainEvent
    ) -> str:
        """Start collaboration workflow choreography"""
        correlation_id = str(uuid.uuid4())
        
        choreography = CollaborationWorkflowChoreography(
            correlation_id=correlation_id,
            requester_id=collaboration_request_event.payload["requester_id"]
        )
        
        self.active_choreographies[correlation_id] = choreography
        
        # Create correlation context
        self.correlation_service.create_correlation(correlation_id, {
            "choreography_type": "collaboration_workflow",
            "requester_id": collaboration_request_event.payload["requester_id"]
        })
        
        # Trigger matching process
        await self.event_bus.publish(DomainEvent(
            event_type="collaboration.matching.requested",
            payload={
                "requester_id": collaboration_request_event.payload["requester_id"],
                "criteria": collaboration_request_event.payload.get("criteria", {}),
                "correlation_id": correlation_id
            },
            correlation_id=correlation_id
        ))
        
        logger.info(f"Started collaboration choreography: {correlation_id}")
        return correlation_id
    
    async def _handle_content_uploaded(self, event: DomainEvent):
        """Handle content uploaded event"""
        await self.start_content_processing_choreography(event)
    
    async def _handle_ai_analysis_completed(self, event: DomainEvent):
        """Handle AI analysis completed event"""
        correlation_id = event.correlation_id
        if not correlation_id or correlation_id not in self.active_choreographies:
            return
        
        choreography = self.active_choreographies[correlation_id]
        if isinstance(choreography, ContentProcessingChoreography):
            choreography.mark_ai_completed()
            
            # Trigger protection and SEO in parallel
            await asyncio.gather(
                self._trigger_content_protection(choreography, event),
                self._trigger_seo_optimization(choreography, event)
            )
    
    async def _handle_protection_applied(self, event: DomainEvent):
        """Handle content protection applied event"""
        correlation_id = event.correlation_id
        if not correlation_id or correlation_id not in self.active_choreographies:
            return
        
        choreography = self.active_choreographies[correlation_id]
        if isinstance(choreography, ContentProcessingChoreography):
            choreography.mark_protection_completed()
            await self._check_ready_for_distribution(choreography)
    
    async def _handle_seo_optimized(self, event: DomainEvent):
        """Handle SEO optimization completed event"""
        correlation_id = event.correlation_id
        if not correlation_id or correlation_id not in self.active_choreographies:
            return
        
        choreography = self.active_choreographies[correlation_id]
        if isinstance(choreography, ContentProcessingChoreography):
            choreography.mark_seo_completed()
            await self._check_ready_for_distribution(choreography)
    
    async def _handle_distribution_completed(self, event: DomainEvent):
        """Handle distribution completed event"""
        correlation_id = event.correlation_id
        if correlation_id in self.active_choreographies:
            choreography = self.active_choreographies[correlation_id]
            logger.info(f"Content processing choreography completed: {correlation_id}")
            # Mark as completed and optionally clean up
    
    async def _handle_collaboration_requested(self, event: DomainEvent):
        """Handle collaboration requested event"""
        await self.start_collaboration_choreography(event)
    
    async def _handle_matches_found(self, event: DomainEvent):
        """Handle collaboration matches found event"""
        correlation_id = event.correlation_id
        if correlation_id in self.active_choreographies:
            choreography = self.active_choreographies[correlation_id]
            if isinstance(choreography, CollaborationWorkflowChoreography):
                choreography.matches_found = True
                
                # Trigger notifications
                await self.event_bus.publish(DomainEvent(
                    event_type="collaboration.notifications.requested",
                    payload={
                        "matches": event.payload.get("matches", []),
                        "correlation_id": correlation_id
                    },
                    correlation_id=correlation_id
                ))
    
    async def _handle_notifications_sent(self, event: DomainEvent):
        """Handle collaboration notifications sent event"""
        correlation_id = event.correlation_id
        if correlation_id in self.active_choreographies:
            choreography = self.active_choreographies[correlation_id]
            if isinstance(choreography, CollaborationWorkflowChoreography):
                choreography.notifications_sent = True
    
    async def _handle_responses_received(self, event: DomainEvent):
        """Handle collaboration responses received event"""
        correlation_id = event.correlation_id
        if correlation_id in self.active_choreographies:
            choreography = self.active_choreographies[correlation_id]
            if isinstance(choreography, CollaborationWorkflowChoreography):
                choreography.responses_received = True
                
                # Trigger agreement processing
                await self.event_bus.publish(DomainEvent(
                    event_type="collaboration.agreements.requested",
                    payload={
                        "responses": event.payload.get("responses", []),
                        "correlation_id": correlation_id
                    },
                    correlation_id=correlation_id
                ))
    
    async def _handle_failure_event(self, event: DomainEvent):
        """Handle failure events for compensation"""
        correlation_id = event.correlation_id
        if correlation_id in self.active_choreographies:
            logger.error(f"Choreography failure detected: {correlation_id}, event: {event.event_type}")
            
            # Trigger compensation events
            await self.event_bus.publish(DomainEvent(
                event_type="choreography.compensation.requested",
                payload={
                    "failed_event": event.event_type,
                    "correlation_id": correlation_id,
                    "error": event.payload.get("error", "Unknown error")
                },
                correlation_id=correlation_id
            ))
    
    async def _trigger_content_protection(
        self, 
        choreography: ContentProcessingChoreography, 
        trigger_event: DomainEvent
    ):
        """Trigger content protection step"""
        await self.event_bus.publish(DomainEvent(
            event_type="content.protection.requested",
            payload={
                "content_id": choreography.content_id,
                "correlation_id": choreography.correlation_id,
                "ai_result": trigger_event.payload.get("analysis_result")
            },
            correlation_id=choreography.correlation_id
        ))
    
    async def _trigger_seo_optimization(
        self, 
        choreography: ContentProcessingChoreography, 
        trigger_event: DomainEvent
    ):
        """Trigger SEO optimization step"""
        await self.event_bus.publish(DomainEvent(
            event_type="content.seo.optimization.requested",
            payload={
                "content_id": choreography.content_id,
                "correlation_id": choreography.correlation_id,
                "ai_result": trigger_event.payload.get("analysis_result")
            },
            correlation_id=choreography.correlation_id
        ))
    
    async def _check_ready_for_distribution(
        self, 
        choreography: ContentProcessingChoreography
    ):
        """Check if ready for distribution and trigger if so"""
        if choreography.is_ready_for_distribution() and not choreography.distribution_ready:
            choreography.distribution_ready = True
            
            await self.event_bus.publish(DomainEvent(
                event_type="content.distribution.requested",
                payload={
                    "content_id": choreography.content_id,
                    "correlation_id": choreography.correlation_id,
                    "platforms": ["youtube", "spotify", "instagram"]
                },
                correlation_id=choreography.correlation_id
            ))
    
    async def get_choreography_status(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active choreography"""
        if correlation_id not in self.active_choreographies:
            return None
        
        choreography = self.active_choreographies[correlation_id]
        
        if isinstance(choreography, ContentProcessingChoreography):
            return {
                "type": "content_processing",
                "correlation_id": correlation_id,
                "content_id": choreography.content_id,
                "creator_id": choreography.creator_id,
                "ai_completed": choreography.ai_analysis_completed,
                "protection_completed": choreography.protection_completed,
                "seo_completed": choreography.seo_completed,
                "distribution_ready": choreography.distribution_ready,
                "started_at": choreography.started_at
            }
        elif isinstance(choreography, CollaborationWorkflowChoreography):
            return {
                "type": "collaboration_workflow",
                "correlation_id": correlation_id,
                "requester_id": choreography.requester_id,
                "matches_found": choreography.matches_found,
                "notifications_sent": choreography.notifications_sent,
                "responses_received": choreography.responses_received,
                "started_at": choreography.started_at
            }
        
        return None
    
    async def list_active_choreographies(self) -> List[Dict[str, Any]]:
        """List all active choreographies"""
        results = []
        for correlation_id in self.active_choreographies:
            status = await self.get_choreography_status(correlation_id)
            if status:
                results.append(status)
        return results


# Global coordination manager instance
_coordination_manager: Optional[ChoreographyCoordinationManager] = None


def get_choreography_coordination_manager() -> ChoreographyCoordinationManager:
    """Get global choreography coordination manager"""
    global _coordination_manager
    if _coordination_manager is None:
        event_bus = EventBus()
        correlation_service = CorrelationService()
        _coordination_manager = ChoreographyCoordinationManager(event_bus, correlation_service)
    
    return _coordination_manager


async def trigger_content_processing_choreography(
    creator_id: str, 
    content_id: str
) -> str:
    """Convenience function to trigger content processing choreography"""
    manager = get_choreography_coordination_manager()
    
    event = DomainEvent(
        event_type="content.uploaded",
        payload={
            "creator_id": creator_id,
            "content_id": content_id
        }
    )
    
    return await manager.start_content_processing_choreography(event)


async def trigger_collaboration_choreography(
    requester_id: str, 
    criteria: Dict[str, Any]
) -> str:
    """Convenience function to trigger collaboration choreography"""
    manager = get_choreography_coordination_manager()
    
    event = DomainEvent(
        event_type="collaboration.requested",
        payload={
            "requester_id": requester_id,
            "criteria": criteria
        }
    )
    
    return await manager.start_collaboration_choreography(event)


__all__ = [
    "ChoreographyCoordinationManager",
    "DomainEvent",
    "EventBus",
    "CorrelationService",
    "ContentProcessingChoreography",
    "CollaborationWorkflowChoreography",
    "ChoreographyStatus",
    "get_choreography_coordination_manager",
    "trigger_content_processing_choreography",
    "trigger_collaboration_choreography"
]