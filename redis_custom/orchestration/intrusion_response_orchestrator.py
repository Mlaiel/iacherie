#!/usr/bin/env python3
"""
🚨 Intrusion Response Orchestrator
==================================

Advanced intrusion detection and automated response system for Redis infrastructure
with AI-powered threat analysis, automated containment, and forensic capabilities.

Expert Roles Combined:
- Security Architect: Intrusion response strategy and threat modeling
- DevOps Engineer: Infrastructure response automation and monitoring  
- Backend Senior: Distributed system security and incident coordination
- ML Engineer: AI-powered threat detection and behavioral analysis

Features:
- Real-time intrusion detection and analysis
- Automated threat containment and isolation
- AI-powered behavioral anomaly detection
- Coordinated incident response workflows
- Forensic evidence collection and preservation
- Threat intelligence integration and correlation
- Adaptive response based on threat severity
- Recovery and remediation orchestration

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
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from collections import defaultdict, deque
import subprocess
import socket

logger = logging.getLogger(__name__)

class IntrusionType(Enum):
    """Types of intrusion attempts"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    COMMAND_INJECTION = "command_injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_INJECTION = "malware_injection"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    APT_ACTIVITY = "apt_activity"
    LATERAL_MOVEMENT = "lateral_movement"

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ResponseAction(Enum):
    """Available response actions"""
    MONITOR = "monitor"
    ALERT = "alert"
    BLOCK_IP = "block_ip"
    QUARANTINE_USER = "quarantine_user"
    ISOLATE_SYSTEM = "isolate_system"
    KILL_CONNECTIONS = "kill_connections"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
    COLLECT_FORENSICS = "collect_forensics"
    BACKUP_DATA = "backup_data"
    RESTORE_SERVICE = "restore_service"

class DetectionMethod(Enum):
    """Intrusion detection methods"""
    SIGNATURE_BASED = "signature_based"
    ANOMALY_BASED = "anomaly_based"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    MACHINE_LEARNING = "machine_learning"
    HEURISTIC = "heuristic"
    HONEYPOT = "honeypot"

@dataclass
class IntrusionEvent:
    """Intrusion event record"""
    event_id: str
    intrusion_type: IntrusionType
    severity: ThreatSeverity
    detection_method: DetectionMethod
    source_ip: str
    target_resource: str
    user_id: Optional[str]
    session_id: Optional[str]
    detected_at: datetime
    indicators: List[str]
    confidence_score: float  # 0.0 to 1.0
    raw_data: Dict[str, Any]
    correlation_id: Optional[str] = None
    false_positive_probability: float = 0.0

@dataclass
class ResponsePlan:
    """Automated response plan"""
    plan_id: str
    name: str
    description: str
    trigger_conditions: List[Dict[str, Any]]
    response_actions: List[ResponseAction]
    severity_threshold: ThreatSeverity
    auto_execute: bool = True
    approval_required: bool = False
    timeout_minutes: int = 30
    rollback_actions: List[ResponseAction] = field(default_factory=list)

@dataclass
class ThreatProfile:
    """Threat actor profiling"""
    profile_id: str
    source_ips: Set[str]
    attack_patterns: List[IntrusionType]
    time_patterns: List[str]
    target_resources: Set[str]
    techniques: List[str]
    first_seen: datetime
    last_seen: datetime
    activity_count: int = 0
    threat_level: ThreatSeverity = ThreatSeverity.LOW

@dataclass
class IntrusionMetrics:
    """Intrusion response metrics"""
    total_events: int = 0
    events_today: int = 0
    critical_events: int = 0
    false_positives: int = 0
    successful_blocks: int = 0
    average_detection_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    active_threats: int = 0
    containment_success_rate: float = 100.0
    timestamp: datetime = field(default_factory=datetime.now)

class RedisIntrusionResponseOrchestrator:
    """
    Advanced Intrusion Response Orchestrator for Redis Infrastructure
    
    Comprehensive intrusion detection and automated response with AI-powered
    threat analysis and coordinated incident response workflows.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Intrusion response management
        self.intrusion_events: Dict[str, IntrusionEvent] = {}
        self.response_plans: Dict[str, ResponsePlan] = {}
        self.threat_profiles: Dict[str, ThreatProfile] = {}
        self.active_responses: Dict[str, Any] = {}
        
        # Intrusion metrics
        self.metrics = IntrusionMetrics()
        
        # Detection engines
        self.signature_rules: List[Dict[str, Any]] = []
        self.anomaly_baselines: Dict[str, Any] = {}
        self.behavioral_models: Dict[str, Any] = {}
        
        # Response configuration
        self.auto_response_enabled = config.get('auto_response_enabled', True)
        self.max_response_time = config.get('max_response_time', 60)  # seconds
        self.forensic_collection = config.get('forensic_collection', True)
        
        # AI/ML configuration
        self.ml_enabled = config.get('ml_enabled', True)
        self.anomaly_threshold = config.get('anomaly_threshold', 2.0)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        # Threat intelligence
        self.threat_feeds: Dict[str, Any] = {}
        self.ioc_database: Dict[str, Any] = {}
        
        logger.info("Intrusion Response Orchestrator initialized")
    
    async def initialize(self):
        """Initialize intrusion response orchestrator"""
        try:
            # Setup Redis connection
            await self._setup_redis_connection()
            
            # Load detection rules and models
            await self._load_detection_rules()
            
            # Load response plans
            await self._load_response_plans()
            
            # Initialize default plans
            await self._initialize_default_plans()
            
            # Load threat intelligence
            await self._load_threat_intelligence()
            
            # Initialize ML models
            if self.ml_enabled:
                await self._initialize_ml_models()
            
            # Start detection engines
            asyncio.create_task(self._start_signature_detection())
            asyncio.create_task(self._start_anomaly_detection())
            asyncio.create_task(self._start_behavioral_analysis())
            
            # Start threat profiling
            asyncio.create_task(self._start_threat_profiling())
            
            # Start response coordination
            asyncio.create_task(self._start_response_coordination())
            
            logger.info("Intrusion Response Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize intrusion response orchestrator: {e}")
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
            
            logger.info("Redis connection established for intrusion response")
            
        except Exception as e:
            logger.error(f"Failed to setup Redis connection: {e}")
            raise
    
    async def _load_detection_rules(self):
        """Load intrusion detection rules"""
        try:
            # Load signature-based rules
            signature_rules = [
                {
                    'rule_id': 'redis_brute_force',
                    'name': 'Redis Brute Force Detection',
                    'pattern': 'failed_authentication',
                    'threshold': 5,
                    'time_window': 300,  # 5 minutes
                    'intrusion_type': IntrusionType.BRUTE_FORCE,
                    'severity': ThreatSeverity.HIGH
                },
                {
                    'rule_id': 'dangerous_commands',
                    'name': 'Dangerous Redis Commands',
                    'pattern': ['FLUSHDB', 'FLUSHALL', 'EVAL', 'SCRIPT', 'SHUTDOWN'],
                    'intrusion_type': IntrusionType.COMMAND_INJECTION,
                    'severity': ThreatSeverity.CRITICAL
                },
                {
                    'rule_id': 'unusual_data_access',
                    'name': 'Unusual Data Access Pattern',
                    'pattern': 'bulk_data_access',
                    'threshold': 1000,  # operations per minute
                    'time_window': 60,
                    'intrusion_type': IntrusionType.DATA_EXFILTRATION,
                    'severity': ThreatSeverity.HIGH
                },
                {
                    'rule_id': 'privilege_escalation',
                    'name': 'Privilege Escalation Attempt',
                    'pattern': 'admin_command_non_admin',
                    'intrusion_type': IntrusionType.PRIVILEGE_ESCALATION,
                    'severity': ThreatSeverity.CRITICAL
                }
            ]
            
            self.signature_rules = signature_rules
            logger.info(f"Loaded {len(signature_rules)} detection rules")
            
        except Exception as e:
            logger.error(f"Error loading detection rules: {e}")
    
    async def _load_response_plans(self):
        """Load automated response plans"""
        try:
            stored_plans = await self.redis_client.hgetall("intrusion:response_plans")
            
            for plan_id, plan_data in stored_plans.items():
                try:
                    plan_dict = json.loads(plan_data)
                    plan = ResponsePlan(**plan_dict)
                    self.response_plans[plan_id.decode()] = plan
                except Exception as e:
                    logger.error(f"Error loading response plan {plan_id}: {e}")
            
            logger.info(f"Loaded {len(self.response_plans)} response plans")
            
        except Exception as e:
            logger.error(f"Error loading response plans: {e}")
    
    async def _initialize_default_plans(self):
        """Initialize default response plans"""
        try:
            default_plans = [
                ResponsePlan(
                    plan_id="brute_force_response",
                    name="Brute Force Response Plan",
                    description="Automated response to brute force attacks",
                    trigger_conditions=[
                        {'intrusion_type': IntrusionType.BRUTE_FORCE.value},
                        {'severity': ThreatSeverity.HIGH.value}
                    ],
                    response_actions=[
                        ResponseAction.BLOCK_IP,
                        ResponseAction.ALERT,
                        ResponseAction.COLLECT_FORENSICS
                    ],
                    severity_threshold=ThreatSeverity.HIGH,
                    auto_execute=True,
                    timeout_minutes=15
                ),
                ResponsePlan(
                    plan_id="critical_threat_response",
                    name="Critical Threat Response Plan",
                    description="Response to critical security threats",
                    trigger_conditions=[
                        {'severity': ThreatSeverity.CRITICAL.value}
                    ],
                    response_actions=[
                        ResponseAction.ISOLATE_SYSTEM,
                        ResponseAction.KILL_CONNECTIONS,
                        ResponseAction.BACKUP_DATA,
                        ResponseAction.ALERT,
                        ResponseAction.COLLECT_FORENSICS
                    ],
                    severity_threshold=ThreatSeverity.CRITICAL,
                    auto_execute=True,
                    approval_required=False,
                    timeout_minutes=10
                ),
                ResponsePlan(
                    plan_id="data_exfiltration_response",
                    name="Data Exfiltration Response Plan",
                    description="Response to data exfiltration attempts",
                    trigger_conditions=[
                        {'intrusion_type': IntrusionType.DATA_EXFILTRATION.value}
                    ],
                    response_actions=[
                        ResponseAction.QUARANTINE_USER,
                        ResponseAction.MONITOR,
                        ResponseAction.COLLECT_FORENSICS,
                        ResponseAction.ALERT
                    ],
                    severity_threshold=ThreatSeverity.HIGH,
                    auto_execute=True,
                    timeout_minutes=20
                ),
                ResponsePlan(
                    plan_id="emergency_response",
                    name="Emergency Response Plan",
                    description="Emergency response for severe threats",
                    trigger_conditions=[
                        {'severity': ThreatSeverity.EMERGENCY.value}
                    ],
                    response_actions=[
                        ResponseAction.EMERGENCY_SHUTDOWN,
                        ResponseAction.BACKUP_DATA,
                        ResponseAction.ALERT,
                        ResponseAction.COLLECT_FORENSICS
                    ],
                    severity_threshold=ThreatSeverity.EMERGENCY,
                    auto_execute=False,
                    approval_required=True,
                    timeout_minutes=5
                )
            ]
            
            for plan in default_plans:
                if plan.plan_id not in self.response_plans:
                    self.response_plans[plan.plan_id] = plan
                    await self._store_response_plan(plan)
            
            logger.info("Default response plans initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default plans: {e}")
    
    async def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        try:
            # Load IOC database
            stored_iocs = await self.redis_client.hgetall("intrusion:ioc_database")
            for ioc_type, ioc_data in stored_iocs.items():
                self.ioc_database[ioc_type.decode()] = json.loads(ioc_data)
            
            logger.info(f"Loaded threat intelligence: {len(self.ioc_database)} IOC types")
            
        except Exception as e:
            logger.error(f"Error loading threat intelligence: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize machine learning models for threat detection"""
        try:
            # Initialize anomaly detection models
            self.anomaly_baselines = {
                'connection_rate': {'mean': 10.0, 'std': 3.0},
                'command_frequency': {'mean': 50.0, 'std': 15.0},
                'data_volume': {'mean': 1024.0, 'std': 512.0}
            }
            
            # Initialize behavioral models
            self.behavioral_models = {
                'user_behavior': {},
                'system_behavior': {},
                'network_behavior': {}
            }
            
            logger.info("ML models initialized for threat detection")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def _start_signature_detection(self):
        """Start signature-based intrusion detection"""
        logger.info("Starting signature-based detection")
        
        while True:
            try:
                # Check security logs for signature matches
                await self._check_signature_matches()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in signature detection: {e}")
                await asyncio.sleep(30)
    
    async def _check_signature_matches(self):
        """Check for signature-based intrusion patterns"""
        try:
            # Get recent security events
            recent_events = await self.redis_client.lrange("security:events", 0, 1000)
            
            for rule in self.signature_rules:
                await self._apply_signature_rule(rule, recent_events)
                
        except Exception as e:
            logger.error(f"Error checking signature matches: {e}")
    
    async def _apply_signature_rule(self, rule: Dict[str, Any], events: List[Any]):
        """Apply signature rule to events"""
        try:
            rule_id = rule['rule_id']
            pattern = rule['pattern']
            intrusion_type = IntrusionType(rule['intrusion_type'])
            severity = ThreatSeverity(rule['severity'])
            
            if rule_id == 'redis_brute_force':
                await self._detect_brute_force(rule, events)
            elif rule_id == 'dangerous_commands':
                await self._detect_dangerous_commands(rule, events)
            elif rule_id == 'unusual_data_access':
                await self._detect_unusual_data_access(rule, events)
            elif rule_id == 'privilege_escalation':
                await self._detect_privilege_escalation(rule, events)
            
        except Exception as e:
            logger.error(f"Error applying signature rule: {e}")
    
    async def _detect_brute_force(self, rule: Dict[str, Any], events: List[Any]):
        """Detect brute force attacks"""
        try:
            threshold = rule['threshold']
            time_window = rule['time_window']
            current_time = time.time()
            
            # Group failed authentication attempts by IP
            failed_attempts = defaultdict(list)
            
            for event in events:
                try:
                    event_data = json.loads(event)
                    if (event_data.get('event_type') == 'authentication' and
                        event_data.get('result') == 'failure'):
                        
                        event_time = datetime.fromisoformat(event_data.get('timestamp', ''))
                        if (current_time - event_time.timestamp()) <= time_window:
                            source_ip = event_data.get('source_ip', 'unknown')
                            failed_attempts[source_ip].append(event_data)
                except Exception:
                    continue
            
            # Check for brute force patterns
            for source_ip, attempts in failed_attempts.items():
                if len(attempts) >= threshold:
                    await self._create_intrusion_event(
                        intrusion_type=IntrusionType.BRUTE_FORCE,
                        severity=ThreatSeverity.HIGH,
                        source_ip=source_ip,
                        indicators=[f"Failed login attempts: {len(attempts)}"],
                        raw_data={'attempts': attempts}
                    )
            
        except Exception as e:
            logger.error(f"Error detecting brute force: {e}")
    
    async def _detect_dangerous_commands(self, rule: Dict[str, Any], events: List[Any]):
        """Detect dangerous Redis commands"""
        try:
            dangerous_patterns = rule['pattern']
            
            for event in events:
                try:
                    event_data = json.loads(event)
                    command = event_data.get('command', '').upper()
                    
                    if any(pattern in command for pattern in dangerous_patterns):
                        await self._create_intrusion_event(
                            intrusion_type=IntrusionType.COMMAND_INJECTION,
                            severity=ThreatSeverity.CRITICAL,
                            source_ip=event_data.get('source_ip', 'unknown'),
                            user_id=event_data.get('user_id'),
                            indicators=[f"Dangerous command: {command}"],
                            raw_data=event_data
                        )
                except Exception:
                    continue
            
        except Exception as e:
            logger.error(f"Error detecting dangerous commands: {e}")
    
    async def _detect_unusual_data_access(self, rule: Dict[str, Any], events: List[Any]):
        """Detect unusual data access patterns"""
        try:
            threshold = rule['threshold']
            time_window = rule['time_window']
            current_time = time.time()
            
            # Count data access operations by user/IP
            access_counts = defaultdict(int)
            
            for event in events:
                try:
                    event_data = json.loads(event)
                    if event_data.get('event_type') == 'data_access':
                        event_time = datetime.fromisoformat(event_data.get('timestamp', ''))
                        if (current_time - event_time.timestamp()) <= time_window:
                            identifier = event_data.get('user_id') or event_data.get('source_ip')
                            access_counts[identifier] += 1
                except Exception:
                    continue
            
            # Check for unusual patterns
            for identifier, count in access_counts.items():
                if count >= threshold:
                    await self._create_intrusion_event(
                        intrusion_type=IntrusionType.DATA_EXFILTRATION,
                        severity=ThreatSeverity.HIGH,
                        source_ip=identifier if '.' in identifier else 'unknown',
                        user_id=identifier if '.' not in identifier else None,
                        indicators=[f"Excessive data access: {count} operations"],
                        raw_data={'access_count': count, 'time_window': time_window}
                    )
            
        except Exception as e:
            logger.error(f"Error detecting unusual data access: {e}")
    
    async def _detect_privilege_escalation(self, rule: Dict[str, Any], events: List[Any]):
        """Detect privilege escalation attempts"""
        try:
            for event in events:
                try:
                    event_data = json.loads(event)
                    if (event_data.get('event_type') == 'authorization' and
                        event_data.get('result') == 'denied' and
                        event_data.get('action') in ['CONFIG', 'DEBUG', 'SHUTDOWN']):
                        
                        await self._create_intrusion_event(
                            intrusion_type=IntrusionType.PRIVILEGE_ESCALATION,
                            severity=ThreatSeverity.CRITICAL,
                            source_ip=event_data.get('source_ip', 'unknown'),
                            user_id=event_data.get('user_id'),
                            indicators=[f"Privilege escalation attempt: {event_data.get('action')}"],
                            raw_data=event_data
                        )
                except Exception:
                    continue
            
        except Exception as e:
            logger.error(f"Error detecting privilege escalation: {e}")
    
    async def _create_intrusion_event(self, intrusion_type: IntrusionType, 
                                    severity: ThreatSeverity, source_ip: str,
                                    indicators: List[str], raw_data: Dict[str, Any],
                                    user_id: Optional[str] = None,
                                    session_id: Optional[str] = None,
                                    confidence_score: float = 0.8) -> str:
        """Create intrusion event and trigger response"""
        try:
            event_id = str(uuid.uuid4())
            
            # Create intrusion event
            event = IntrusionEvent(
                event_id=event_id,
                intrusion_type=intrusion_type,
                severity=severity,
                detection_method=DetectionMethod.SIGNATURE_BASED,
                source_ip=source_ip,
                target_resource="redis_server",
                user_id=user_id,
                session_id=session_id,
                detected_at=datetime.now(),
                indicators=indicators,
                confidence_score=confidence_score,
                raw_data=raw_data
            )
            
            # Store event
            self.intrusion_events[event_id] = event
            await self._store_intrusion_event(event)
            
            # Update metrics
            self.metrics.total_events += 1
            self.metrics.events_today += 1
            if severity == ThreatSeverity.CRITICAL:
                self.metrics.critical_events += 1
            
            # Trigger automated response
            if self.auto_response_enabled:
                await self._trigger_automated_response(event)
            
            # Update threat profiling
            await self._update_threat_profiling(event)
            
            logger.warning(f"Intrusion detected: {intrusion_type.value} from {source_ip} (severity: {severity.value})")
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating intrusion event: {e}")
            return ""
    
    async def _trigger_automated_response(self, event: IntrusionEvent):
        """Trigger automated response to intrusion"""
        try:
            # Find matching response plans
            matching_plans = []
            
            for plan in self.response_plans.values():
                if await self._plan_matches_event(plan, event):
                    matching_plans.append(plan)
            
            # Sort by severity threshold (highest first)
            matching_plans.sort(key=lambda p: p.severity_threshold.value, reverse=True)
            
            # Execute the most appropriate plan
            if matching_plans:
                plan = matching_plans[0]
                await self._execute_response_plan(plan, event)
            
        except Exception as e:
            logger.error(f"Error triggering automated response: {e}")
    
    async def _plan_matches_event(self, plan: ResponsePlan, event: IntrusionEvent) -> bool:
        """Check if response plan matches intrusion event"""
        try:
            # Check severity threshold
            severity_order = {
                ThreatSeverity.LOW: 1,
                ThreatSeverity.MEDIUM: 2,
                ThreatSeverity.HIGH: 3,
                ThreatSeverity.CRITICAL: 4,
                ThreatSeverity.EMERGENCY: 5
            }
            
            if severity_order.get(event.severity, 0) < severity_order.get(plan.severity_threshold, 0):
                return False
            
            # Check trigger conditions
            for condition in plan.trigger_conditions:
                if 'intrusion_type' in condition:
                    if event.intrusion_type.value != condition['intrusion_type']:
                        return False
                
                if 'severity' in condition:
                    if event.severity.value != condition['severity']:
                        return False
                
                if 'confidence_threshold' in condition:
                    if event.confidence_score < condition['confidence_threshold']:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching plan to event: {e}")
            return False
    
    async def _execute_response_plan(self, plan: ResponsePlan, event: IntrusionEvent):
        """Execute response plan"""
        try:
            response_id = str(uuid.uuid4())
            
            logger.info(f"Executing response plan: {plan.name} for event: {event.event_id}")
            
            # Record response start
            response_start = time.time()
            
            # Execute response actions
            for action in plan.response_actions:
                try:
                    await self._execute_response_action(action, event, plan)
                except Exception as e:
                    logger.error(f"Error executing response action {action}: {e}")
            
            # Record response completion
            response_time = (time.time() - response_start) * 1000
            self._update_average_response_time(response_time)
            
            # Store response record
            response_record = {
                'response_id': response_id,
                'plan_id': plan.plan_id,
                'event_id': event.event_id,
                'executed_at': datetime.now().isoformat(),
                'response_time_ms': response_time,
                'actions_executed': [action.value for action in plan.response_actions],
                'status': 'completed'
            }
            
            await self.redis_client.hset(
                "intrusion:responses",
                response_id,
                json.dumps(response_record)
            )
            
            logger.info(f"Response plan executed: {plan.name} in {response_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error executing response plan: {e}")
    
    async def _execute_response_action(self, action: ResponseAction, 
                                     event: IntrusionEvent, plan: ResponsePlan):
        """Execute specific response action"""
        try:
            if action == ResponseAction.BLOCK_IP:
                await self._block_ip_address(event.source_ip)
            
            elif action == ResponseAction.QUARANTINE_USER:
                if event.user_id:
                    await self._quarantine_user(event.user_id)
            
            elif action == ResponseAction.ISOLATE_SYSTEM:
                await self._isolate_system(event.target_resource)
            
            elif action == ResponseAction.KILL_CONNECTIONS:
                await self._kill_connections(event.source_ip)
            
            elif action == ResponseAction.EMERGENCY_SHUTDOWN:
                await self._emergency_shutdown()
            
            elif action == ResponseAction.COLLECT_FORENSICS:
                await self._collect_forensic_evidence(event)
            
            elif action == ResponseAction.BACKUP_DATA:
                await self._backup_critical_data()
            
            elif action == ResponseAction.ALERT:
                await self._send_security_alert(event, plan)
            
            elif action == ResponseAction.MONITOR:
                await self._enhance_monitoring(event)
            
            elif action == ResponseAction.RESTORE_SERVICE:
                await self._restore_service()
            
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
    
    async def _block_ip_address(self, ip_address: str):
        """Block IP address"""
        try:
            # Add to blocked IPs list
            await self.redis_client.sadd("intrusion:blocked_ips", ip_address)
            
            # Set expiration (24 hours)
            await self.redis_client.expire("intrusion:blocked_ips", 86400)
            
            # Add to security blocked IPs
            await self.redis_client.sadd("security:blocked_ips", ip_address)
            
            self.metrics.successful_blocks += 1
            
            logger.info(f"Blocked IP address: {ip_address}")
            
        except Exception as e:
            logger.error(f"Error blocking IP address: {e}")
    
    async def _quarantine_user(self, user_id: str):
        """Quarantine user account"""
        try:
            quarantine_data = {
                'user_id': user_id,
                'quarantined_at': datetime.now().isoformat(),
                'reason': 'Intrusion detection',
                'status': 'quarantined'
            }
            
            await self.redis_client.hset(
                "intrusion:quarantined_users",
                user_id,
                json.dumps(quarantine_data)
            )
            
            logger.info(f"Quarantined user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error quarantining user: {e}")
    
    async def _isolate_system(self, system: str):
        """Isolate system component"""
        try:
            isolation_data = {
                'system': system,
                'isolated_at': datetime.now().isoformat(),
                'reason': 'Intrusion response',
                'status': 'isolated'
            }
            
            await self.redis_client.hset(
                "intrusion:isolated_systems",
                system,
                json.dumps(isolation_data)
            )
            
            logger.info(f"Isolated system: {system}")
            
        except Exception as e:
            logger.error(f"Error isolating system: {e}")
    
    async def _kill_connections(self, source_ip: str):
        """Kill active connections from source IP"""
        try:
            # Get active connections
            connections = await self.redis_client.client_list()
            
            killed_count = 0
            for conn_info in connections:
                if source_ip in conn_info.get('addr', ''):
                    client_id = conn_info.get('id')
                    if client_id:
                        await self.redis_client.client_kill_filter(
                            _id=client_id
                        )
                        killed_count += 1
            
            logger.info(f"Killed {killed_count} connections from {source_ip}")
            
        except Exception as e:
            logger.error(f"Error killing connections: {e}")
    
    async def _emergency_shutdown(self):
        """Emergency shutdown (placeholder)"""
        try:
            # This would implement emergency procedures
            # For safety, this is just logged
            
            shutdown_data = {
                'initiated_at': datetime.now().isoformat(),
                'reason': 'Emergency intrusion response',
                'status': 'initiated'
            }
            
            await self.redis_client.set(
                "intrusion:emergency_shutdown",
                json.dumps(shutdown_data),
                ex=3600
            )
            
            logger.critical("EMERGENCY SHUTDOWN INITIATED")
            
        except Exception as e:
            logger.error(f"Error in emergency shutdown: {e}")
    
    async def _collect_forensic_evidence(self, event: IntrusionEvent):
        """Collect forensic evidence"""
        try:
            if not self.forensic_collection:
                return
            
            evidence = {
                'event_id': event.event_id,
                'collected_at': datetime.now().isoformat(),
                'system_state': await self._capture_system_state(),
                'network_connections': await self._capture_network_state(),
                'redis_logs': await self._capture_redis_logs(),
                'memory_dump': await self._capture_memory_info()
            }
            
            await self.redis_client.hset(
                "intrusion:forensic_evidence",
                event.event_id,
                json.dumps(evidence)
            )
            
            logger.info(f"Collected forensic evidence for event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error collecting forensic evidence: {e}")
    
    async def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'redis_info': await self.redis_client.info(),
                'active_clients': len(await self.redis_client.client_list()),
                'memory_usage': (await self.redis_client.info('memory')).get('used_memory_human', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error capturing system state: {e}")
            return {}
    
    async def _capture_network_state(self) -> Dict[str, Any]:
        """Capture network connection state"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'client_connections': await self.redis_client.client_list(),
                'active_channels': await self.redis_client.pubsub_channels()
            }
        except Exception as e:
            logger.error(f"Error capturing network state: {e}")
            return {}
    
    async def _capture_redis_logs(self) -> List[str]:
        """Capture recent Redis logs"""
        try:
            # Get recent command logs
            recent_logs = await self.redis_client.lrange("redis:command_log", 0, 1000)
            return [log.decode() if isinstance(log, bytes) else log for log in recent_logs]
        except Exception as e:
            logger.error(f"Error capturing Redis logs: {e}")
            return []
    
    async def _capture_memory_info(self) -> Dict[str, Any]:
        """Capture memory information"""
        try:
            memory_info = await self.redis_client.info('memory')
            return {
                'used_memory': memory_info.get('used_memory', 0),
                'used_memory_peak': memory_info.get('used_memory_peak', 0),
                'memory_fragmentation_ratio': memory_info.get('mem_fragmentation_ratio', 0)
            }
        except Exception as e:
            logger.error(f"Error capturing memory info: {e}")
            return {}
    
    async def _send_security_alert(self, event: IntrusionEvent, plan: ResponsePlan):
        """Send security alert"""
        try:
            alert_data = {
                'alert_id': str(uuid.uuid4()),
                'event_id': event.event_id,
                'intrusion_type': event.intrusion_type.value,
                'severity': event.severity.value,
                'source_ip': event.source_ip,
                'plan_executed': plan.name,
                'detected_at': event.detected_at.isoformat(),
                'indicators': event.indicators,
                'requires_attention': event.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EMERGENCY]
            }
            
            await self.redis_client.lpush(
                "intrusion:security_alerts",
                json.dumps(alert_data)
            )
            
            # Publish to alert channel
            await self.redis_client.publish(
                "intrusion_alerts",
                json.dumps(alert_data)
            )
            
            logger.info(f"Security alert sent for event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
    
    async def _start_anomaly_detection(self):
        """Start anomaly-based detection"""
        logger.info("Starting anomaly-based detection")
        
        while True:
            try:
                if self.ml_enabled:
                    await self._detect_anomalies()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in anomaly detection: {e}")
                await asyncio.sleep(120)
    
    async def _detect_anomalies(self):
        """Detect statistical anomalies"""
        try:
            # Get recent metrics
            current_metrics = await self._get_current_metrics()
            
            # Check for anomalies
            for metric_name, current_value in current_metrics.items():
                if metric_name in self.anomaly_baselines:
                    baseline = self.anomaly_baselines[metric_name]
                    z_score = abs(current_value - baseline['mean']) / baseline['std']
                    
                    if z_score > self.anomaly_threshold:
                        await self._create_anomaly_event(metric_name, current_value, z_score)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        try:
            info = await self.redis_client.info()
            return {
                'connection_rate': float(info.get('connected_clients', 0)),
                'command_frequency': float(info.get('total_commands_processed', 0)),
                'data_volume': float(info.get('used_memory', 0))
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}
    
    async def _create_anomaly_event(self, metric_name: str, current_value: float, z_score: float):
        """Create anomaly-based intrusion event"""
        try:
            # Determine intrusion type based on metric
            intrusion_type = IntrusionType.DENIAL_OF_SERVICE
            if metric_name == 'data_volume':
                intrusion_type = IntrusionType.DATA_EXFILTRATION
            
            # Determine severity based on z-score
            if z_score > 5.0:
                severity = ThreatSeverity.CRITICAL
            elif z_score > 3.0:
                severity = ThreatSeverity.HIGH
            else:
                severity = ThreatSeverity.MEDIUM
            
            await self._create_intrusion_event(
                intrusion_type=intrusion_type,
                severity=severity,
                source_ip="unknown",
                indicators=[f"Anomaly in {metric_name}: {current_value} (z-score: {z_score:.2f})"],
                raw_data={'metric': metric_name, 'value': current_value, 'z_score': z_score},
                confidence_score=min(z_score / 5.0, 1.0)
            )
            
        except Exception as e:
            logger.error(f"Error creating anomaly event: {e}")
    
    async def _start_behavioral_analysis(self):
        """Start behavioral analysis"""
        logger.info("Starting behavioral analysis")
        
        while True:
            try:
                await self._analyze_user_behavior()
                await self._analyze_system_behavior()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in behavioral analysis: {e}")
                await asyncio.sleep(120)
    
    async def _analyze_user_behavior(self):
        """Analyze user behavior patterns"""
        try:
            # Get recent user activities
            recent_activities = await self.redis_client.lrange("security:user_activities", 0, 1000)
            
            user_patterns = defaultdict(list)
            for activity in recent_activities:
                try:
                    activity_data = json.loads(activity)
                    user_id = activity_data.get('user_id')
                    if user_id:
                        user_patterns[user_id].append(activity_data)
                except Exception:
                    continue
            
            # Analyze patterns for each user
            for user_id, activities in user_patterns.items():
                await self._check_user_behavioral_anomalies(user_id, activities)
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
    
    async def _check_user_behavioral_anomalies(self, user_id: str, activities: List[Dict[str, Any]]):
        """Check for behavioral anomalies in user activities"""
        try:
            # Check for unusual activity times
            activity_hours = [
                datetime.fromisoformat(a.get('timestamp', '')).hour
                for a in activities if a.get('timestamp')
            ]
            
            if activity_hours:
                # Check for activities outside normal hours (assuming 9-17)
                unusual_hours = [h for h in activity_hours if h < 9 or h > 17]
                if len(unusual_hours) > len(activity_hours) * 0.5:  # More than 50% outside hours
                    await self._create_intrusion_event(
                        intrusion_type=IntrusionType.INSIDER_THREAT,
                        severity=ThreatSeverity.MEDIUM,
                        source_ip="unknown",
                        user_id=user_id,
                        indicators=[f"Unusual activity hours: {unusual_hours}"],
                        raw_data={'user_activities': activities},
                        confidence_score=0.6
                    )
            
        except Exception as e:
            logger.error(f"Error checking user behavioral anomalies: {e}")
    
    async def _start_threat_profiling(self):
        """Start threat actor profiling"""
        logger.info("Starting threat profiling")
        
        while True:
            try:
                await self._update_threat_profiles()
                await self._correlate_threat_activities()
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in threat profiling: {e}")
                await asyncio.sleep(300)
    
    async def _update_threat_profiling(self, event: IntrusionEvent):
        """Update threat profiling based on new event"""
        try:
            # Create or update threat profile for source IP
            profile_id = f"profile_{hashlib.sha256(event.source_ip.encode()).hexdigest()[:16]}"
            
            if profile_id in self.threat_profiles:
                profile = self.threat_profiles[profile_id]
            else:
                profile = ThreatProfile(
                    profile_id=profile_id,
                    source_ips={event.source_ip},
                    attack_patterns=[],
                    time_patterns=[],
                    target_resources=set(),
                    techniques=[],
                    first_seen=event.detected_at,
                    last_seen=event.detected_at
                )
                self.threat_profiles[profile_id] = profile
            
            # Update profile
            profile.source_ips.add(event.source_ip)
            if event.intrusion_type not in profile.attack_patterns:
                profile.attack_patterns.append(event.intrusion_type)
            profile.target_resources.add(event.target_resource)
            profile.last_seen = event.detected_at
            profile.activity_count += 1
            
            # Update threat level
            if profile.activity_count > 10:
                profile.threat_level = ThreatSeverity.HIGH
            elif profile.activity_count > 5:
                profile.threat_level = ThreatSeverity.MEDIUM
            
            # Store profile
            await self._store_threat_profile(profile)
            
        except Exception as e:
            logger.error(f"Error updating threat profiling: {e}")
    
    def _update_average_response_time(self, response_time_ms: float):
        """Update average response time metric"""
        if self.metrics.average_response_time_ms == 0:
            self.metrics.average_response_time_ms = response_time_ms
        else:
            # Exponential moving average
            self.metrics.average_response_time_ms = (
                0.9 * self.metrics.average_response_time_ms + 0.1 * response_time_ms
            )
    
    async def _store_intrusion_event(self, event: IntrusionEvent):
        """Store intrusion event"""
        try:
            event_data = {
                'event_id': event.event_id,
                'intrusion_type': event.intrusion_type.value,
                'severity': event.severity.value,
                'detection_method': event.detection_method.value,
                'source_ip': event.source_ip,
                'target_resource': event.target_resource,
                'user_id': event.user_id,
                'session_id': event.session_id,
                'detected_at': event.detected_at.isoformat(),
                'indicators': event.indicators,
                'confidence_score': event.confidence_score,
                'raw_data': event.raw_data,
                'correlation_id': event.correlation_id,
                'false_positive_probability': event.false_positive_probability
            }
            
            await self.redis_client.hset(
                "intrusion:events",
                event.event_id,
                json.dumps(event_data)
            )
            
            # Add to timeline
            await self.redis_client.zadd(
                "intrusion:timeline",
                {event.event_id: time.time()}
            )
            
        except Exception as e:
            logger.error(f"Error storing intrusion event: {e}")
    
    async def _store_response_plan(self, plan: ResponsePlan):
        """Store response plan"""
        try:
            plan_data = {
                'plan_id': plan.plan_id,
                'name': plan.name,
                'description': plan.description,
                'trigger_conditions': plan.trigger_conditions,
                'response_actions': [action.value for action in plan.response_actions],
                'severity_threshold': plan.severity_threshold.value,
                'auto_execute': plan.auto_execute,
                'approval_required': plan.approval_required,
                'timeout_minutes': plan.timeout_minutes,
                'rollback_actions': [action.value for action in plan.rollback_actions]
            }
            
            await self.redis_client.hset(
                "intrusion:response_plans",
                plan.plan_id,
                json.dumps(plan_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing response plan: {e}")
    
    async def _store_threat_profile(self, profile: ThreatProfile):
        """Store threat profile"""
        try:
            profile_data = {
                'profile_id': profile.profile_id,
                'source_ips': list(profile.source_ips),
                'attack_patterns': [ap.value for ap in profile.attack_patterns],
                'time_patterns': profile.time_patterns,
                'target_resources': list(profile.target_resources),
                'techniques': profile.techniques,
                'first_seen': profile.first_seen.isoformat(),
                'last_seen': profile.last_seen.isoformat(),
                'activity_count': profile.activity_count,
                'threat_level': profile.threat_level.value
            }
            
            await self.redis_client.hset(
                "intrusion:threat_profiles",
                profile.profile_id,
                json.dumps(profile_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing threat profile: {e}")
    
    async def close(self):
        """Close intrusion response orchestrator"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            logger.info("Intrusion Response Orchestrator closed")
            
        except Exception as e:
            logger.error(f"Error closing intrusion response orchestrator: {e}")

# Configuration schema for intrusion response orchestrator
@dataclass
class IntrusionResponseOrchestratorConfig:
    """Intrusion response orchestrator configuration"""
    redis_url: str
    redis_password: Optional[str] = None
    ssl_enabled: bool = True
    max_connections: int = 100
    auto_response_enabled: bool = True
    max_response_time: int = 60
    forensic_collection: bool = True
    ml_enabled: bool = True
    anomaly_threshold: float = 2.0
    confidence_threshold: float = 0.7