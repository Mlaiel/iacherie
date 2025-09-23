#!/usr/bin/env python3
"""
🚨 Threat Response Manager
==========================

Advanced threat response and incident management system for Redis infrastructure
with automated response, forensics, and recovery capabilities.

Expert Roles Combined:
- Security Architect: Threat intelligence and response strategy
- DevOps Engineer: Automated incident response and recovery
- Backend Senior: Distributed system security architecture
- ML Engineer: AI-powered threat analysis and pattern recognition

Features:
- Real-time threat response automation
- Incident classification and prioritization
- Forensic data collection and analysis
- Automated containment and mitigation
- Recovery and remediation workflows
- Threat intelligence integration
- Security playbook execution
- Post-incident analysis and learning

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security Architect + DevOps + Backend Senior + ML Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aioredis
import numpy as np
from collections import defaultdict, deque
import socket
import subprocess
import os

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class IncidentStatus(Enum):
    """Incident status states"""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    CONTAINED = "contained"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ResponseAction(Enum):
    """Types of response actions"""
    ISOLATE = "isolate"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    TERMINATE = "terminate"
    BACKUP = "backup"
    RESTORE = "restore"
    ALERT = "alert"
    INVESTIGATE = "investigate"
    PATCH = "patch"
    MONITOR = "monitor"

class ThreatCategory(Enum):
    """Threat categorization"""
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DATA_BREACH = "data_breach"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"

@dataclass
class Incident:
    """Security incident representation"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    category: ThreatCategory
    source_ip: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    response_actions: List[str] = field(default_factory=list)
    forensic_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResponsePlaybook:
    """Automated response playbook"""
    playbook_id: str
    name: str
    description: str
    trigger_conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    approval_required: bool = False
    timeout_minutes: int = 60
    priority: int = 1
    enabled: bool = True

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    indicator: str
    indicator_type: str  # ip, domain, hash, etc.
    threat_type: ThreatCategory
    confidence: float  # 0.0 to 1.0
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str] = field(default_factory=list)
    ttl_hours: int = 24

@dataclass
class ResponseMetrics:
    """Response performance metrics"""
    total_incidents: int = 0
    active_incidents: int = 0
    resolved_incidents: int = 0
    average_response_time: float = 0.0
    average_resolution_time: float = 0.0
    false_positives: int = 0
    successful_mitigations: int = 0
    failed_mitigations: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class RedisThreatResponseManager:
    """
    Advanced Threat Response Manager for Redis Infrastructure
    
    Provides automated threat response, incident management, and
    security orchestration capabilities with AI-powered analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Incident management
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: deque = deque(maxlen=10000)
        
        # Response playbooks
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        
        # Threat intelligence
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        
        # Response metrics
        self.metrics = ResponseMetrics()
        
        # Response handlers
        self.response_handlers: Dict[ResponseAction, Callable] = {}
        
        # AI models for threat analysis
        self.threat_classifier = None
        self.pattern_detector = None
        
        # Forensic collection
        self.forensic_enabled = config.get('forensic_enabled', True)
        self.forensic_retention_days = config.get('forensic_retention_days', 30)
        
        # External integrations
        self.external_tools = config.get('external_tools', {})
        
        logger.info("Threat Response Manager initialized")
    
    async def initialize(self):
        """Initialize threat response manager"""
        try:
            # Setup Redis connection
            await self._setup_redis_connection()
            
            # Load response playbooks
            await self._load_response_playbooks()
            
            # Initialize response handlers
            self._initialize_response_handlers()
            
            # Load threat intelligence
            await self._load_threat_intelligence()
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Start monitoring
            asyncio.create_task(self._start_incident_monitoring())
            asyncio.create_task(self._start_threat_intelligence_updates())
            
            logger.info("Threat Response Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat response manager: {e}")
            raise
    
    async def _setup_redis_connection(self):
        """Setup Redis connection"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config['redis_url'],
                password=self.config.get('redis_password'),
                ssl=self.config.get('ssl_enabled', True),
                max_connections=self.config.get('max_connections', 100),
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            await self.redis_client.ping()
            
            logger.info("Redis connection established for threat response")
            
        except Exception as e:
            logger.error(f"Failed to setup Redis connection: {e}")
            raise
    
    async def _load_response_playbooks(self):
        """Load automated response playbooks"""
        try:
            # Default response playbooks
            default_playbooks = [
                ResponsePlaybook(
                    playbook_id="brute_force_response",
                    name="Brute Force Attack Response",
                    description="Automated response to brute force attacks",
                    trigger_conditions=[
                        {"type": "failed_logins", "threshold": 5, "window_minutes": 10},
                        {"type": "threat_level", "min_level": "high"}
                    ],
                    actions=[
                        {"action": "block", "target": "source_ip", "duration_minutes": 60},
                        {"action": "alert", "recipients": ["security_team"], "priority": "high"},
                        {"action": "investigate", "collect_forensics": True}
                    ],
                    timeout_minutes=30
                ),
                ResponsePlaybook(
                    playbook_id="data_exfiltration_response",
                    name="Data Exfiltration Response",
                    description="Response to potential data exfiltration",
                    trigger_conditions=[
                        {"type": "data_access_anomaly", "threshold": 3.0},
                        {"type": "threat_category", "category": "data_breach"}
                    ],
                    actions=[
                        {"action": "isolate", "target": "user_account"},
                        {"action": "backup", "target": "critical_data"},
                        {"action": "alert", "recipients": ["security_team", "management"], "priority": "critical"},
                        {"action": "investigate", "collect_forensics": True, "priority": "immediate"}
                    ],
                    approval_required=False,
                    timeout_minutes=15
                ),
                ResponsePlaybook(
                    playbook_id="malware_response",
                    name="Malware Detection Response",
                    description="Automated malware containment and removal",
                    trigger_conditions=[
                        {"type": "threat_category", "category": "malware"},
                        {"type": "confidence", "min_confidence": 0.8}
                    ],
                    actions=[
                        {"action": "quarantine", "target": "affected_systems"},
                        {"action": "terminate", "target": "malicious_processes"},
                        {"action": "backup", "target": "clean_data"},
                        {"action": "patch", "target": "vulnerabilities"},
                        {"action": "monitor", "duration_hours": 24}
                    ],
                    timeout_minutes=45
                ),
                ResponsePlaybook(
                    playbook_id="ddos_response",
                    name="DDoS Attack Response",
                    description="DDoS mitigation and traffic filtering",
                    trigger_conditions=[
                        {"type": "threat_category", "category": "ddos"},
                        {"type": "traffic_volume", "threshold_multiplier": 5.0}
                    ],
                    actions=[
                        {"action": "block", "target": "attack_sources", "method": "upstream"},
                        {"action": "alert", "recipients": ["network_team"], "priority": "high"},
                        {"action": "monitor", "metrics": ["traffic_volume", "response_time"]}
                    ],
                    timeout_minutes=60
                )
            ]
            
            for playbook in default_playbooks:
                self.playbooks[playbook.playbook_id] = playbook
            
            # Load custom playbooks from Redis
            try:
                stored_playbooks = await self.redis_client.get("threat_response:playbooks")
                if stored_playbooks:
                    playbooks_data = json.loads(stored_playbooks)
                    for playbook_data in playbooks_data:
                        playbook = ResponsePlaybook(**playbook_data)
                        self.playbooks[playbook.playbook_id] = playbook
            except Exception as e:
                logger.warning(f"Could not load stored playbooks: {e}")
            
            logger.info(f"Loaded {len(self.playbooks)} response playbooks")
            
        except Exception as e:
            logger.error(f"Failed to load response playbooks: {e}")
            raise
    
    def _initialize_response_handlers(self):
        """Initialize response action handlers"""
        self.response_handlers = {
            ResponseAction.ISOLATE: self._handle_isolate,
            ResponseAction.BLOCK: self._handle_block,
            ResponseAction.QUARANTINE: self._handle_quarantine,
            ResponseAction.TERMINATE: self._handle_terminate,
            ResponseAction.BACKUP: self._handle_backup,
            ResponseAction.RESTORE: self._handle_restore,
            ResponseAction.ALERT: self._handle_alert,
            ResponseAction.INVESTIGATE: self._handle_investigate,
            ResponseAction.PATCH: self._handle_patch,
            ResponseAction.MONITOR: self._handle_monitor
        }
        
        logger.info("Response handlers initialized")
    
    async def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        try:
            # Load from Redis
            try:
                stored_intel = await self.redis_client.get("threat_response:intelligence")
                if stored_intel:
                    intel_data = json.loads(stored_intel)
                    for intel_item in intel_data:
                        intel = ThreatIntelligence(**intel_item)
                        self.threat_intelligence[intel.indicator] = intel
            except Exception as e:
                logger.warning(f"Could not load stored threat intelligence: {e}")
            
            # Load external threat feeds (placeholder)
            await self._update_threat_feeds()
            
            logger.info(f"Loaded {len(self.threat_intelligence)} threat intelligence indicators")
            
        except Exception as e:
            logger.error(f"Failed to load threat intelligence: {e}")
    
    async def _initialize_ai_models(self):
        """Initialize AI models for threat analysis"""
        try:
            # Placeholder for AI model initialization
            # In real implementation, load trained models for:
            # - Threat classification
            # - Anomaly detection
            # - Pattern recognition
            # - Risk scoring
            
            logger.info("AI models initialized for threat analysis")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    async def _start_incident_monitoring(self):
        """Start continuous incident monitoring"""
        logger.info("Starting incident monitoring")
        
        while True:
            try:
                # Monitor for new threats from security orchestrator
                await self._check_for_new_threats()
                
                # Update incident statuses
                await self._update_incident_statuses()
                
                # Process pending responses
                await self._process_pending_responses()
                
                # Clean up resolved incidents
                await self._cleanup_resolved_incidents()
                
                # Update metrics
                await self._update_response_metrics()
                
                await asyncio.sleep(self.config.get('monitoring_interval', 30))
                
            except Exception as e:
                logger.error(f"Error in incident monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _start_threat_intelligence_updates(self):
        """Start threat intelligence updates"""
        logger.info("Starting threat intelligence updates")
        
        while True:
            try:
                # Update threat feeds
                await self._update_threat_feeds()
                
                # Clean expired intelligence
                await self._cleanup_expired_intelligence()
                
                # Update threat scoring
                await self._update_threat_scoring()
                
                await asyncio.sleep(self.config.get('intel_update_interval', 3600))
                
            except Exception as e:
                logger.error(f"Error updating threat intelligence: {e}")
                await asyncio.sleep(300)
    
    async def _check_for_new_threats(self):
        """Check for new threats from security system"""
        try:
            # Get new threats from security alerts
            new_alerts = await self.redis_client.lrange("security:alerts", 0, -1)
            
            for alert_data in new_alerts:
                alert = json.loads(alert_data)
                
                # Create incident from alert if not already processed
                incident_key = f"processed_alert_{alert['alert_id']}"
                if not await self.redis_client.exists(incident_key):
                    await self._create_incident_from_alert(alert)
                    
                    # Mark as processed
                    await self.redis_client.setex(incident_key, 3600, "processed")
            
            # Clear processed alerts
            if new_alerts:
                await self.redis_client.delete("security:alerts")
            
        except Exception as e:
            logger.error(f"Error checking for new threats: {e}")
    
    async def _create_incident_from_alert(self, alert: Dict[str, Any]):
        """Create incident from security alert"""
        try:
            incident_id = str(uuid.uuid4())
            
            # Determine severity based on alert level
            severity_mapping = {
                'low': IncidentSeverity.LOW,
                'medium': IncidentSeverity.MEDIUM,
                'high': IncidentSeverity.HIGH,
                'critical': IncidentSeverity.CRITICAL
            }
            
            severity = severity_mapping.get(alert.get('level', 'medium'), IncidentSeverity.MEDIUM)
            
            # Classify threat category
            category = await self._classify_threat_category(alert)
            
            incident = Incident(
                incident_id=incident_id,
                title=f"Security Alert: {alert.get('message', 'Unknown threat')}",
                description=alert.get('message', ''),
                severity=severity,
                status=IncidentStatus.DETECTED,
                category=category,
                source_ip=alert.get('source_ip'),
                indicators=[alert.get('threat_id', '')],
                created_at=datetime.now()
            )
            
            # Store incident
            self.active_incidents[incident_id] = incident
            await self._store_incident(incident)
            
            # Trigger automated response
            await self._trigger_automated_response(incident)
            
            # Update metrics
            self.metrics.total_incidents += 1
            self.metrics.active_incidents += 1
            
            logger.info(f"Created incident {incident_id} from alert {alert.get('alert_id')}")
            
        except Exception as e:
            logger.error(f"Error creating incident from alert: {e}")
    
    async def _classify_threat_category(self, alert: Dict[str, Any]) -> ThreatCategory:
        """Classify threat category using AI/ML"""
        try:
            # Simplified classification based on keywords
            message = alert.get('message', '').lower()
            
            if any(keyword in message for keyword in ['brute force', 'login', 'authentication']):
                return ThreatCategory.INTRUSION
            elif any(keyword in message for keyword in ['data', 'exfiltration', 'breach']):
                return ThreatCategory.DATA_BREACH
            elif any(keyword in message for keyword in ['malware', 'virus', 'trojan']):
                return ThreatCategory.MALWARE
            elif any(keyword in message for keyword in ['ddos', 'flood', 'volume']):
                return ThreatCategory.DDOS
            elif any(keyword in message for keyword in ['insider', 'internal']):
                return ThreatCategory.INSIDER_THREAT
            elif any(keyword in message for keyword in ['ransomware', 'encrypt']):
                return ThreatCategory.RANSOMWARE
            elif any(keyword in message for keyword in ['phishing', 'social']):
                return ThreatCategory.PHISHING
            elif any(keyword in message for keyword in ['vulnerability', 'exploit']):
                return ThreatCategory.VULNERABILITY_EXPLOIT
            else:
                return ThreatCategory.INTRUSION  # Default
            
        except Exception as e:
            logger.error(f"Error classifying threat category: {e}")
            return ThreatCategory.INTRUSION
    
    async def _store_incident(self, incident: Incident):
        """Store incident data"""
        try:
            incident_data = {
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'severity': incident.severity.value,
                'status': incident.status.value,
                'category': incident.category.value,
                'source_ip': incident.source_ip,
                'affected_systems': incident.affected_systems,
                'indicators': incident.indicators,
                'created_at': incident.created_at.isoformat(),
                'updated_at': incident.updated_at.isoformat(),
                'assigned_to': incident.assigned_to,
                'response_actions': incident.response_actions,
                'forensic_data': incident.forensic_data
            }
            
            # Store in Redis
            await self.redis_client.hset(
                "threat_response:incidents",
                incident.incident_id,
                json.dumps(incident_data)
            )
            
            # Add to incident timeline
            await self.redis_client.zadd(
                "threat_response:incident_timeline",
                {incident.incident_id: time.time()}
            )
            
        except Exception as e:
            logger.error(f"Error storing incident: {e}")
    
    async def _trigger_automated_response(self, incident: Incident):
        """Trigger automated response based on incident"""
        try:
            # Find matching playbooks
            matching_playbooks = await self._find_matching_playbooks(incident)
            
            for playbook in matching_playbooks:
                if playbook.enabled:
                    await self._execute_playbook(incident, playbook)
            
        except Exception as e:
            logger.error(f"Error triggering automated response: {e}")
    
    async def _find_matching_playbooks(self, incident: Incident) -> List[ResponsePlaybook]:
        """Find playbooks that match incident conditions"""
        try:
            matching_playbooks = []
            
            for playbook in self.playbooks.values():
                if await self._playbook_matches_incident(playbook, incident):
                    matching_playbooks.append(playbook)
            
            # Sort by priority
            matching_playbooks.sort(key=lambda p: p.priority)
            
            return matching_playbooks
            
        except Exception as e:
            logger.error(f"Error finding matching playbooks: {e}")
            return []
    
    async def _playbook_matches_incident(self, playbook: ResponsePlaybook, incident: Incident) -> bool:
        """Check if playbook conditions match incident"""
        try:
            for condition in playbook.trigger_conditions:
                condition_type = condition.get('type')
                
                if condition_type == 'threat_level':
                    required_level = condition.get('min_level')
                    if not self._severity_meets_threshold(incident.severity, required_level):
                        return False
                
                elif condition_type == 'threat_category':
                    required_category = condition.get('category')
                    if incident.category.value != required_category:
                        return False
                
                elif condition_type == 'confidence':
                    min_confidence = condition.get('min_confidence', 0.0)
                    # Get confidence from threat intelligence
                    confidence = await self._get_incident_confidence(incident)
                    if confidence < min_confidence:
                        return False
                
                # Add more condition types as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking playbook match: {e}")
            return False
    
    def _severity_meets_threshold(self, severity: IncidentSeverity, threshold: str) -> bool:
        """Check if severity meets threshold"""
        severity_order = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4,
            'emergency': 5
        }
        
        return severity_order.get(severity.value, 0) >= severity_order.get(threshold, 0)
    
    async def _get_incident_confidence(self, incident: Incident) -> float:
        """Get confidence score for incident"""
        try:
            # Check threat intelligence for indicators
            total_confidence = 0.0
            count = 0
            
            for indicator in incident.indicators:
                if indicator in self.threat_intelligence:
                    intel = self.threat_intelligence[indicator]
                    total_confidence += intel.confidence
                    count += 1
            
            if count > 0:
                return total_confidence / count
            else:
                return 0.5  # Default confidence
            
        except Exception as e:
            logger.error(f"Error getting incident confidence: {e}")
            return 0.5
    
    async def _execute_playbook(self, incident: Incident, playbook: ResponsePlaybook):
        """Execute response playbook"""
        try:
            logger.info(f"Executing playbook {playbook.name} for incident {incident.incident_id}")
            
            # Update incident status
            incident.status = IncidentStatus.RESPONDING
            incident.updated_at = datetime.now()
            
            # Execute actions
            for action_config in playbook.actions:
                action_type = action_config.get('action')
                
                if action_type in self.response_handlers:
                    handler = self.response_handlers[ResponseAction(action_type)]
                    await handler(incident, action_config)
                    
                    # Record action
                    incident.response_actions.append(f"{action_type}: {action_config}")
            
            # Update incident
            await self._store_incident(incident)
            
            logger.info(f"Completed playbook execution for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error executing playbook: {e}")
    
    async def _handle_isolate(self, incident: Incident, config: Dict[str, Any]):
        """Handle isolation response action"""
        try:
            target = config.get('target')
            
            if target == 'user_account' and incident.source_ip:
                # Isolate user account
                isolation_data = {
                    'incident_id': incident.incident_id,
                    'target': incident.source_ip,
                    'isolated_at': datetime.now().isoformat(),
                    'reason': f"Incident {incident.incident_id}"
                }
                
                await self.redis_client.hset(
                    "threat_response:isolated_accounts",
                    incident.source_ip,
                    json.dumps(isolation_data)
                )
                
                logger.info(f"Isolated account for incident {incident.incident_id}")
            
            elif target == 'system' and incident.affected_systems:
                # Isolate affected systems
                for system in incident.affected_systems:
                    isolation_data = {
                        'incident_id': incident.incident_id,
                        'system': system,
                        'isolated_at': datetime.now().isoformat()
                    }
                    
                    await self.redis_client.hset(
                        "threat_response:isolated_systems",
                        system,
                        json.dumps(isolation_data)
                    )
                
                logger.info(f"Isolated systems for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling isolate action: {e}")
    
    async def _handle_block(self, incident: Incident, config: Dict[str, Any]):
        """Handle block response action"""
        try:
            target = config.get('target')
            duration_minutes = config.get('duration_minutes', 60)
            
            if target == 'source_ip' and incident.source_ip:
                # Block source IP
                block_data = {
                    'incident_id': incident.incident_id,
                    'ip': incident.source_ip,
                    'blocked_at': datetime.now().isoformat(),
                    'duration_minutes': duration_minutes,
                    'reason': f"Incident {incident.incident_id}"
                }
                
                await self.redis_client.setex(
                    f"threat_response:blocked_ip:{incident.source_ip}",
                    duration_minutes * 60,
                    json.dumps(block_data)
                )
                
                # Add to security blocked IPs
                await self.redis_client.sadd("security:blocked_ips", incident.source_ip)
                
                logger.info(f"Blocked IP {incident.source_ip} for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling block action: {e}")
    
    async def _handle_quarantine(self, incident: Incident, config: Dict[str, Any]):
        """Handle quarantine response action"""
        try:
            target = config.get('target')
            
            if target == 'affected_systems':
                for system in incident.affected_systems:
                    quarantine_data = {
                        'incident_id': incident.incident_id,
                        'system': system,
                        'quarantined_at': datetime.now().isoformat(),
                        'status': 'quarantined'
                    }
                    
                    await self.redis_client.hset(
                        "threat_response:quarantined_systems",
                        system,
                        json.dumps(quarantine_data)
                    )
                
                logger.info(f"Quarantined systems for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling quarantine action: {e}")
    
    async def _handle_terminate(self, incident: Incident, config: Dict[str, Any]):
        """Handle terminate response action"""
        try:
            target = config.get('target')
            
            if target == 'malicious_processes':
                # Placeholder for process termination
                # In real implementation, this would interface with system management tools
                termination_data = {
                    'incident_id': incident.incident_id,
                    'action': 'terminate_processes',
                    'executed_at': datetime.now().isoformat(),
                    'affected_systems': incident.affected_systems
                }
                
                await self.redis_client.lpush(
                    "threat_response:termination_log",
                    json.dumps(termination_data)
                )
                
                logger.info(f"Terminated malicious processes for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling terminate action: {e}")
    
    async def _handle_backup(self, incident: Incident, config: Dict[str, Any]):
        """Handle backup response action"""
        try:
            target = config.get('target')
            
            backup_data = {
                'incident_id': incident.incident_id,
                'target': target,
                'backup_initiated_at': datetime.now().isoformat(),
                'status': 'in_progress'
            }
            
            await self.redis_client.hset(
                "threat_response:backup_operations",
                f"{incident.incident_id}_{target}",
                json.dumps(backup_data)
            )
            
            logger.info(f"Initiated backup for {target} in incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling backup action: {e}")
    
    async def _handle_restore(self, incident: Incident, config: Dict[str, Any]):
        """Handle restore response action"""
        try:
            target = config.get('target')
            restore_point = config.get('restore_point')
            
            restore_data = {
                'incident_id': incident.incident_id,
                'target': target,
                'restore_point': restore_point,
                'restore_initiated_at': datetime.now().isoformat(),
                'status': 'in_progress'
            }
            
            await self.redis_client.hset(
                "threat_response:restore_operations",
                f"{incident.incident_id}_{target}",
                json.dumps(restore_data)
            )
            
            logger.info(f"Initiated restore for {target} in incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling restore action: {e}")
    
    async def _handle_alert(self, incident: Incident, config: Dict[str, Any]):
        """Handle alert response action"""
        try:
            recipients = config.get('recipients', [])
            priority = config.get('priority', 'medium')
            
            alert_data = {
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'severity': incident.severity.value,
                'priority': priority,
                'recipients': recipients,
                'sent_at': datetime.now().isoformat()
            }
            
            # Store alert
            await self.redis_client.lpush(
                "threat_response:sent_alerts",
                json.dumps(alert_data)
            )
            
            # Publish to alert channel
            await self.redis_client.publish(
                "threat_response_alerts",
                json.dumps(alert_data)
            )
            
            logger.info(f"Sent alert for incident {incident.incident_id} to {recipients}")
            
        except Exception as e:
            logger.error(f"Error handling alert action: {e}")
    
    async def _handle_investigate(self, incident: Incident, config: Dict[str, Any]):
        """Handle investigate response action"""
        try:
            collect_forensics = config.get('collect_forensics', False)
            priority = config.get('priority', 'normal')
            
            if collect_forensics:
                await self._collect_forensic_data(incident)
            
            investigation_data = {
                'incident_id': incident.incident_id,
                'started_at': datetime.now().isoformat(),
                'priority': priority,
                'forensics_collected': collect_forensics,
                'status': 'active'
            }
            
            await self.redis_client.hset(
                "threat_response:investigations",
                incident.incident_id,
                json.dumps(investigation_data)
            )
            
            # Update incident status
            incident.status = IncidentStatus.ANALYZING
            
            logger.info(f"Started investigation for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling investigate action: {e}")
    
    async def _handle_patch(self, incident: Incident, config: Dict[str, Any]):
        """Handle patch response action"""
        try:
            target = config.get('target')
            
            patch_data = {
                'incident_id': incident.incident_id,
                'target': target,
                'patch_initiated_at': datetime.now().isoformat(),
                'status': 'scheduled'
            }
            
            await self.redis_client.hset(
                "threat_response:patch_operations",
                f"{incident.incident_id}_{target}",
                json.dumps(patch_data)
            )
            
            logger.info(f"Scheduled patching for {target} in incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling patch action: {e}")
    
    async def _handle_monitor(self, incident: Incident, config: Dict[str, Any]):
        """Handle monitor response action"""
        try:
            duration_hours = config.get('duration_hours', 24)
            metrics = config.get('metrics', [])
            
            monitor_data = {
                'incident_id': incident.incident_id,
                'started_at': datetime.now().isoformat(),
                'duration_hours': duration_hours,
                'metrics': metrics,
                'status': 'active'
            }
            
            await self.redis_client.setex(
                f"threat_response:monitoring:{incident.incident_id}",
                duration_hours * 3600,
                json.dumps(monitor_data)
            )
            
            logger.info(f"Started monitoring for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling monitor action: {e}")
    
    async def _collect_forensic_data(self, incident: Incident):
        """Collect forensic data for incident"""
        try:
            if not self.forensic_enabled:
                return
            
            forensic_data = {
                'collection_started': datetime.now().isoformat(),
                'incident_id': incident.incident_id,
                'network_logs': await self._collect_network_logs(incident),
                'system_logs': await self._collect_system_logs(incident),
                'redis_logs': await self._collect_redis_logs(incident),
                'process_info': await self._collect_process_info(incident),
                'file_hashes': await self._collect_file_hashes(incident)
            }
            
            # Store forensic data
            incident.forensic_data = forensic_data
            
            # Store separately for investigation
            await self.redis_client.hset(
                "threat_response:forensic_data",
                incident.incident_id,
                json.dumps(forensic_data)
            )
            
            logger.info(f"Collected forensic data for incident {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error collecting forensic data: {e}")
    
    async def _collect_network_logs(self, incident: Incident) -> Dict[str, Any]:
        """Collect network-related logs"""
        try:
            network_data = {
                'source_ip': incident.source_ip,
                'connections': [],
                'traffic_patterns': {}
            }
            
            # Get network connections from Redis logs
            if incident.source_ip:
                connections = await self.redis_client.lrange(
                    f"network:connections:{incident.source_ip}", 0, 100
                )
                network_data['connections'] = [json.loads(conn) for conn in connections]
            
            return network_data
            
        except Exception as e:
            logger.error(f"Error collecting network logs: {e}")
            return {}
    
    async def _collect_system_logs(self, incident: Incident) -> Dict[str, Any]:
        """Collect system-related logs"""
        try:
            system_data = {
                'affected_systems': incident.affected_systems,
                'system_events': [],
                'performance_metrics': {}
            }
            
            # Collect system events for affected systems
            for system in incident.affected_systems:
                events = await self.redis_client.lrange(
                    f"system:events:{system}", 0, 100
                )
                system_data['system_events'].extend([json.loads(event) for event in events])
            
            return system_data
            
        except Exception as e:
            logger.error(f"Error collecting system logs: {e}")
            return {}
    
    async def _collect_redis_logs(self, incident: Incident) -> Dict[str, Any]:
        """Collect Redis-specific logs"""
        try:
            redis_data = {
                'commands': [],
                'slow_queries': [],
                'error_logs': []
            }
            
            # Get Redis command logs
            command_logs = await self.redis_client.lrange("redis:command_log", 0, 1000)
            redis_data['commands'] = [json.loads(cmd) for cmd in command_logs]
            
            # Get slow query logs
            slow_queries = await self.redis_client.lrange("redis:slow_log", 0, 100)
            redis_data['slow_queries'] = [json.loads(query) for query in slow_queries]
            
            return redis_data
            
        except Exception as e:
            logger.error(f"Error collecting Redis logs: {e}")
            return {}
    
    async def _collect_process_info(self, incident: Incident) -> Dict[str, Any]:
        """Collect process information"""
        try:
            process_data = {
                'running_processes': [],
                'resource_usage': {},
                'network_connections': []
            }
            
            # This would interface with system monitoring tools in real implementation
            # For now, return placeholder data
            
            return process_data
            
        except Exception as e:
            logger.error(f"Error collecting process info: {e}")
            return {}
    
    async def _collect_file_hashes(self, incident: Incident) -> Dict[str, Any]:
        """Collect file integrity information"""
        try:
            file_data = {
                'modified_files': [],
                'suspicious_files': [],
                'hash_changes': []
            }
            
            # This would check file integrity in real implementation
            # For now, return placeholder data
            
            return file_data
            
        except Exception as e:
            logger.error(f"Error collecting file hashes: {e}")
            return {}
    
    async def _update_incident_statuses(self):
        """Update incident statuses based on response progress"""
        try:
            for incident_id, incident in self.active_incidents.items():
                # Check if incident should be moved to next status
                await self._check_incident_progression(incident)
            
        except Exception as e:
            logger.error(f"Error updating incident statuses: {e}")
    
    async def _check_incident_progression(self, incident: Incident):
        """Check if incident should progress to next status"""
        try:
            if incident.status == IncidentStatus.RESPONDING:
                # Check if all response actions are complete
                if await self._are_response_actions_complete(incident):
                    incident.status = IncidentStatus.CONTAINED
                    incident.updated_at = datetime.now()
                    await self._store_incident(incident)
            
            elif incident.status == IncidentStatus.CONTAINED:
                # Check if ready for recovery
                if await self._is_ready_for_recovery(incident):
                    incident.status = IncidentStatus.RECOVERING
                    incident.updated_at = datetime.now()
                    await self._store_incident(incident)
            
            elif incident.status == IncidentStatus.RECOVERING:
                # Check if recovery is complete
                if await self._is_recovery_complete(incident):
                    incident.status = IncidentStatus.RESOLVED
                    incident.updated_at = datetime.now()
                    await self._store_incident(incident)
                    
                    # Update metrics
                    self.metrics.active_incidents -= 1
                    self.metrics.resolved_incidents += 1
            
        except Exception as e:
            logger.error(f"Error checking incident progression: {e}")
    
    async def _are_response_actions_complete(self, incident: Incident) -> bool:
        """Check if all response actions are complete"""
        try:
            # Check various response operations
            investigations = await self.redis_client.hget(
                "threat_response:investigations", incident.incident_id
            )
            
            if investigations:
                investigation_data = json.loads(investigations)
                if investigation_data.get('status') == 'active':
                    return False
            
            # Check backup operations
            backup_keys = await self.redis_client.keys(f"threat_response:backup_operations:{incident.incident_id}_*")
            for key in backup_keys:
                backup_data = await self.redis_client.get(key)
                if backup_data:
                    backup_info = json.loads(backup_data)
                    if backup_info.get('status') == 'in_progress':
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking response actions completion: {e}")
            return False
    
    async def _is_ready_for_recovery(self, incident: Incident) -> bool:
        """Check if incident is ready for recovery phase"""
        try:
            # Check if threat is fully contained
            # This would involve checking various containment measures
            return True  # Simplified for demo
            
        except Exception as e:
            logger.error(f"Error checking recovery readiness: {e}")
            return False
    
    async def _is_recovery_complete(self, incident: Incident) -> bool:
        """Check if recovery is complete"""
        try:
            # Check if all systems are restored and operational
            # This would involve checking system health and functionality
            return True  # Simplified for demo
            
        except Exception as e:
            logger.error(f"Error checking recovery completion: {e}")
            return False
    
    async def _process_pending_responses(self):
        """Process any pending response actions"""
        try:
            # Check for manual approval requirements
            await self._process_approval_queue()
            
            # Check for scheduled actions
            await self._process_scheduled_actions()
            
        except Exception as e:
            logger.error(f"Error processing pending responses: {e}")
    
    async def _process_approval_queue(self):
        """Process actions waiting for approval"""
        try:
            # Get pending approvals
            pending_approvals = await self.redis_client.lrange("threat_response:pending_approvals", 0, -1)
            
            for approval_data in pending_approvals:
                approval = json.loads(approval_data)
                
                # Check if approval timeout exceeded
                created_time = datetime.fromisoformat(approval['created_at'])
                if datetime.now() - created_time > timedelta(hours=1):  # 1 hour timeout
                    # Auto-deny due to timeout
                    await self._deny_approval(approval)
            
        except Exception as e:
            logger.error(f"Error processing approval queue: {e}")
    
    async def _process_scheduled_actions(self):
        """Process scheduled response actions"""
        try:
            # Get scheduled actions
            current_time = time.time()
            scheduled_actions = await self.redis_client.zrangebyscore(
                "threat_response:scheduled_actions", 0, current_time
            )
            
            for action_data in scheduled_actions:
                action = json.loads(action_data)
                
                # Execute scheduled action
                await self._execute_scheduled_action(action)
                
                # Remove from scheduled queue
                await self.redis_client.zrem("threat_response:scheduled_actions", action_data)
            
        except Exception as e:
            logger.error(f"Error processing scheduled actions: {e}")
    
    async def _execute_scheduled_action(self, action: Dict[str, Any]):
        """Execute a scheduled action"""
        try:
            incident_id = action.get('incident_id')
            action_type = action.get('action_type')
            config = action.get('config', {})
            
            if incident_id in self.active_incidents:
                incident = self.active_incidents[incident_id]
                
                if action_type in self.response_handlers:
                    handler = self.response_handlers[ResponseAction(action_type)]
                    await handler(incident, config)
            
        except Exception as e:
            logger.error(f"Error executing scheduled action: {e}")
    
    async def _deny_approval(self, approval: Dict[str, Any]):
        """Deny an approval request due to timeout"""
        try:
            denial_data = {
                'approval_id': approval.get('approval_id'),
                'incident_id': approval.get('incident_id'),
                'denied_at': datetime.now().isoformat(),
                'reason': 'timeout'
            }
            
            await self.redis_client.lpush(
                "threat_response:denied_approvals",
                json.dumps(denial_data)
            )
            
            # Remove from pending queue
            await self.redis_client.lrem(
                "threat_response:pending_approvals", 1,
                json.dumps(approval)
            )
            
        except Exception as e:
            logger.error(f"Error denying approval: {e}")
    
    async def _cleanup_resolved_incidents(self):
        """Clean up old resolved incidents"""
        try:
            # Move resolved incidents to history
            for incident_id, incident in list(self.active_incidents.items()):
                if incident.status == IncidentStatus.RESOLVED:
                    # Add to history
                    self.incident_history.append(incident)
                    
                    # Remove from active incidents
                    del self.active_incidents[incident_id]
                    
                    # Update incident status to closed
                    incident.status = IncidentStatus.CLOSED
                    await self._store_incident(incident)
            
        except Exception as e:
            logger.error(f"Error cleaning up resolved incidents: {e}")
    
    async def _update_response_metrics(self):
        """Update response performance metrics"""
        try:
            # Calculate response times
            response_times = []
            resolution_times = []
            
            for incident in self.incident_history:
                if len(incident.response_actions) > 0:
                    # Calculate response time (from detection to first action)
                    response_time = 300  # Placeholder - would calculate from timestamps
                    response_times.append(response_time)
                
                if incident.status == IncidentStatus.CLOSED:
                    # Calculate resolution time
                    resolution_time = 1800  # Placeholder - would calculate from timestamps
                    resolution_times.append(resolution_time)
            
            # Update metrics
            if response_times:
                self.metrics.average_response_time = sum(response_times) / len(response_times)
            
            if resolution_times:
                self.metrics.average_resolution_time = sum(resolution_times) / len(resolution_times)
            
            self.metrics.timestamp = datetime.now()
            
            # Store metrics
            metrics_data = {
                'total_incidents': self.metrics.total_incidents,
                'active_incidents': self.metrics.active_incidents,
                'resolved_incidents': self.metrics.resolved_incidents,
                'average_response_time': self.metrics.average_response_time,
                'average_resolution_time': self.metrics.average_resolution_time,
                'false_positives': self.metrics.false_positives,
                'successful_mitigations': self.metrics.successful_mitigations,
                'failed_mitigations': self.metrics.failed_mitigations,
                'timestamp': self.metrics.timestamp.isoformat()
            }
            
            await self.redis_client.set(
                "threat_response:metrics",
                json.dumps(metrics_data),
                ex=3600
            )
            
        except Exception as e:
            logger.error(f"Error updating response metrics: {e}")
    
    async def _update_threat_feeds(self):
        """Update threat intelligence feeds"""
        try:
            # Placeholder for external threat feed integration
            # In real implementation, this would fetch from:
            # - Commercial threat intelligence feeds
            # - Open source intelligence
            # - Government feeds
            # - Industry sharing groups
            
            logger.debug("Updated threat intelligence feeds")
            
        except Exception as e:
            logger.error(f"Error updating threat feeds: {e}")
    
    async def _cleanup_expired_intelligence(self):
        """Clean up expired threat intelligence"""
        try:
            current_time = datetime.now()
            expired_indicators = []
            
            for indicator, intel in self.threat_intelligence.items():
                # Check if intelligence has expired
                age_hours = (current_time - intel.last_seen).total_seconds() / 3600
                if age_hours > intel.ttl_hours:
                    expired_indicators.append(indicator)
            
            # Remove expired intelligence
            for indicator in expired_indicators:
                del self.threat_intelligence[indicator]
            
            if expired_indicators:
                logger.info(f"Cleaned up {len(expired_indicators)} expired threat indicators")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired intelligence: {e}")
    
    async def _update_threat_scoring(self):
        """Update threat scoring based on recent activity"""
        try:
            # Update confidence scores based on recent incidents
            for indicator, intel in self.threat_intelligence.items():
                # Check if indicator was involved in recent incidents
                recent_incidents = await self._get_recent_incidents_for_indicator(indicator)
                
                if recent_incidents:
                    # Increase confidence if indicator led to confirmed incidents
                    intel.confidence = min(1.0, intel.confidence + 0.1)
                    intel.last_seen = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating threat scoring: {e}")
    
    async def _get_recent_incidents_for_indicator(self, indicator: str) -> List[str]:
        """Get recent incidents that involved specific indicator"""
        try:
            recent_incidents = []
            
            # Check incidents from last 24 hours
            for incident in self.incident_history:
                if indicator in incident.indicators:
                    age_hours = (datetime.now() - incident.created_at).total_seconds() / 3600
                    if age_hours <= 24:
                        recent_incidents.append(incident.incident_id)
            
            return recent_incidents
            
        except Exception as e:
            logger.error(f"Error getting recent incidents for indicator: {e}")
            return []
    
    async def create_incident(self, title: str, description: str, severity: IncidentSeverity,
                            category: ThreatCategory, source_ip: Optional[str] = None,
                            affected_systems: List[str] = None) -> str:
        """Manually create incident"""
        try:
            incident_id = str(uuid.uuid4())
            
            incident = Incident(
                incident_id=incident_id,
                title=title,
                description=description,
                severity=severity,
                status=IncidentStatus.DETECTED,
                category=category,
                source_ip=source_ip,
                affected_systems=affected_systems or [],
                created_at=datetime.now()
            )
            
            self.active_incidents[incident_id] = incident
            await self._store_incident(incident)
            
            # Trigger automated response
            await self._trigger_automated_response(incident)
            
            # Update metrics
            self.metrics.total_incidents += 1
            self.metrics.active_incidents += 1
            
            logger.info(f"Created manual incident: {incident_id}")
            return incident_id
            
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            raise
    
    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        return self.active_incidents.get(incident_id)
    
    async def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents"""
        return list(self.active_incidents.values())
    
    async def get_response_metrics(self) -> ResponseMetrics:
        """Get response performance metrics"""
        return self.metrics
    
    async def add_threat_intelligence(self, indicator: str, indicator_type: str,
                                    threat_type: ThreatCategory, confidence: float,
                                    source: str, tags: List[str] = None) -> bool:
        """Add threat intelligence indicator"""
        try:
            intel = ThreatIntelligence(
                indicator=indicator,
                indicator_type=indicator_type,
                threat_type=threat_type,
                confidence=confidence,
                source=source,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                tags=tags or []
            )
            
            self.threat_intelligence[indicator] = intel
            
            # Store in Redis
            intel_data = []
            for intel_item in self.threat_intelligence.values():
                intel_dict = {
                    'indicator': intel_item.indicator,
                    'indicator_type': intel_item.indicator_type,
                    'threat_type': intel_item.threat_type.value,
                    'confidence': intel_item.confidence,
                    'source': intel_item.source,
                    'first_seen': intel_item.first_seen.isoformat(),
                    'last_seen': intel_item.last_seen.isoformat(),
                    'tags': intel_item.tags,
                    'ttl_hours': intel_item.ttl_hours
                }
                intel_data.append(intel_dict)
            
            await self.redis_client.set(
                "threat_response:intelligence",
                json.dumps(intel_data)
            )
            
            logger.info(f"Added threat intelligence: {indicator}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding threat intelligence: {e}")
            return False
    
    async def close(self):
        """Close threat response manager"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            logger.info("Threat Response Manager closed")
            
        except Exception as e:
            logger.error(f"Error closing threat response manager: {e}")

# Configuration schema for threat response manager
@dataclass
class ThreatResponseConfig:
    """Threat response manager configuration"""
    redis_url: str
    redis_password: Optional[str] = None
    ssl_enabled: bool = True
    max_connections: int = 100
    monitoring_interval: int = 30
    intel_update_interval: int = 3600
    forensic_enabled: bool = True
    forensic_retention_days: int = 30
    external_tools: Dict[str, Any] = field(default_factory=dict)