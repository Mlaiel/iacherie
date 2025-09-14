"""
PagerDuty Client Integration for Ainflue Platform
Production-ready incident management and alerting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """PagerDuty incident severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IncidentStatus(Enum):
    """PagerDuty incident status"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class PagerDutyEvent:
    """PagerDuty event structure"""
    routing_key: str
    event_action: str  # trigger, acknowledge, resolve
    dedup_key: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    client: str = "Ainflue Platform"
    client_url: Optional[str] = None


@dataclass
class IncidentDetails:
    """Incident details for comprehensive tracking"""
    title: str
    summary: str
    severity: IncidentSeverity
    source: str
    service_name: str
    workflow_stage: str
    custom_details: Optional[Dict[str, Any]] = None
    links: Optional[List[Dict[str, str]]] = None
    images: Optional[List[Dict[str, str]]] = None


class PagerDutyClient:
    """
    Production-grade PagerDuty integration client
    Handles incident creation, updates, and intelligent routing
    """
    
    def __init__(self, integration_key -> None: Optional[str] = None, 
                 api_token -> None: Optional[str] = None) -> None:
        """
        Initialize PagerDuty client
        
        Args:
            integration_key: PagerDuty Events API integration key
            api_token: PagerDuty REST API token for advanced features
        """
        self.integration_key = integration_key or os.environ.get('PAGERDUTY_INTEGRATION_KEY')
        self.api_token = api_token or os.environ.get('PAGERDUTY_API_TOKEN')
        
        self.events_api_url = "https://events.pagerduty.com/v2/enqueue"
        self.rest_api_url = "https://api.pagerduty.com"
        
        self.session = None
        self.initialized = False
        
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available. Install with: pip install requests")
            return
            
        if not self.integration_key:
            logger.warning("PagerDuty integration key not configured. Alerting disabled.")
            return
            
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize PagerDuty client with session configuration"""
        try:
            self.session = requests.Session()
            
            # Set default headers for REST API
            if self.api_token:
                self.session.headers.update({
                    'Authorization': f'Token token={self.api_token}',
                    'Accept': 'application/vnd.pagerduty+json;version=2',
                    'Content-Type': 'application/json'
                })
            
            self.initialized = True
            logger.info("PagerDuty client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PagerDuty client: {e}")
    
    def trigger_incident(self, incident_details: IncidentDetails,
                        dedup_key: Optional[str] = None) -> Optional[str]:
        """
        Trigger new incident in PagerDuty
        
        Args:
            incident_details: Comprehensive incident information
            dedup_key: Deduplication key for grouping related incidents
            
        Returns:
            Incident key if successful
        """
        if not self.initialized:
            logger.error("PagerDuty client not initialized")
            return None
            
        try:
            # Generate dedup key if not provided
            if not dedup_key:
                dedup_key = self._generate_dedup_key(incident_details)
            
            # Prepare event payload
            event = PagerDutyEvent(
                routing_key=self.integration_key,
                event_action="trigger",
                dedup_key=dedup_key,
                payload={
                    "summary": incident_details.title,
                    "source": incident_details.source,
                    "severity": incident_details.severity.value,
                    "component": incident_details.service_name,
                    "group": incident_details.workflow_stage,
                    "class": "monitoring",
                    "custom_details": self._prepare_custom_details(incident_details)
                },
                client="Ainflue Platform",
                client_url="https://monitoring.ainflue.com"
            )
            
            # Add links if provided
            if incident_details.links:
                event.payload["links"] = incident_details.links
            
            # Add images if provided
            if incident_details.images:
                event.payload["images"] = incident_details.images
            
            # Send event to PagerDuty
            response = self._send_event(event)
            
            if response and response.get('status') == 'success':
                incident_key = response.get('dedup_key', dedup_key)
                logger.info(f"Incident triggered successfully: {incident_key}")
                return incident_key
            else:
                logger.error(f"Failed to trigger incident: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error triggering PagerDuty incident: {e}")
            return None
    
    def acknowledge_incident(self, incident_key: str, 
                           acknowledger: str = "Ainflue System") -> bool:
        """
        Acknowledge incident in PagerDuty
        
        Args:
            incident_key: Incident deduplication key
            acknowledger: Who is acknowledging the incident
            
        Returns:
            True if successful
        """
        if not self.initialized:
            logger.error("PagerDuty client not initialized")
            return False
            
        try:
            event = PagerDutyEvent(
                routing_key=self.integration_key,
                event_action="acknowledge",
                dedup_key=incident_key,
                payload={
                    "summary": f"Incident acknowledged by {acknowledger}",
                    "source": "Ainflue Platform"
                }
            )
            
            response = self._send_event(event)
            
            if response and response.get('status') == 'success':
                logger.info(f"Incident acknowledged: {incident_key}")
                return True
            else:
                logger.error(f"Failed to acknowledge incident: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error acknowledging PagerDuty incident: {e}")
            return False
    
    def resolve_incident(self, incident_key: str, 
                        resolver: str = "Ainflue System",
                        resolution_details: Optional[str] = None) -> bool:
        """
        Resolve incident in PagerDuty
        
        Args:
            incident_key: Incident deduplication key
            resolver: Who is resolving the incident
            resolution_details: Optional resolution details
            
        Returns:
            True if successful
        """
        if not self.initialized:
            logger.error("PagerDuty client not initialized")
            return False
            
        try:
            payload = {
                "summary": f"Incident resolved by {resolver}",
                "source": "Ainflue Platform"
            }
            
            if resolution_details:
                payload["custom_details"] = {
                    "resolution": resolution_details,
                    "resolved_at": datetime.utcnow().isoformat(),
                    "resolver": resolver
                }
            
            event = PagerDutyEvent(
                routing_key=self.integration_key,
                event_action="resolve",
                dedup_key=incident_key,
                payload=payload
            )
            
            response = self._send_event(event)
            
            if response and response.get('status') == 'success':
                logger.info(f"Incident resolved: {incident_key}")
                return True
            else:
                logger.error(f"Failed to resolve incident: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error resolving PagerDuty incident: {e}")
            return False
    
    def _send_event(self, event: PagerDutyEvent) -> Optional[Dict[str, Any]]:
        """Send event to PagerDuty Events API"""
        try:
            payload = asdict(event)
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response = self.session.post(
                self.events_api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 202:
                return response.json()
            else:
                logger.error(f"PagerDuty API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending PagerDuty event: {e}")
            return None
    
    def _generate_dedup_key(self, incident_details: IncidentDetails) -> str:
        """Generate deduplication key for incident grouping"""
        # Create unique key based on service, workflow, and error type
        key_parts = [
            incident_details.service_name,
            incident_details.workflow_stage,
            incident_details.severity.value,
            incident_details.title[:50]  # First 50 chars of title
        ]
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:32]
    
    def _prepare_custom_details(self, incident_details: IncidentDetails) -> Dict[str, Any]:
        """Prepare custom details for PagerDuty payload"""
        custom_details = {
            "service": incident_details.service_name,
            "workflow_stage": incident_details.workflow_stage,
            "severity": incident_details.severity.value,
            "source": incident_details.source,
            "timestamp": datetime.utcnow().isoformat(),
            "platform": "Ainflue"
        }
        
        # Add incident-specific custom details
        if incident_details.custom_details:
            custom_details.update(incident_details.custom_details)
        
        return custom_details


# Global PagerDuty client instance
pagerduty_client = PagerDutyClient()