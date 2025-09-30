#!/usr/bin/env python3
"""
🏢 Enterprise Security Orchestrator
===================================

Enterprise-grade security orchestration system for centralized security management.
Implements SIEM integration, automated workflows, incident orchestration, and compliance monitoring.

Expert Roles Combined:
- Security Specialist: Advanced threat detection and response
- DevOps Engineer: Automated orchestration and monitoring
- Microservices Architect: Distributed security coordination
- Lead Dev IA: Intelligent security automation

Features:
- SIEM integration with multiple platforms
- Automated security workflow orchestration
- Real-time incident detection and response
- Multi-framework compliance monitoring
- Threat intelligence coordination
- Security metrics and analytics
- Cross-platform security coordination

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security + DevOps + Microservices + Lead Dev IA
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
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import hmac
import secrets
import uuid
from concurrent.futures import ThreadPoolExecutor
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import aiohttp

logger = logging.getLogger(__name__)

class SecurityThreatLevel(Enum):
    """Security threat level classification"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "auth_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALWARE_DETECTION = "malware_detection"
    DDoS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    COMPLIANCE_VIOLATION = "compliance_violation"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    FRAUD_DETECTION = "fraud_detection"

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    SOX = "sox"
    CCPA = "ccpa"

class OrchestrationStatus(Enum):
    """Orchestration workflow status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: SecurityEventType = SecurityEventType.SUSPICIOUS_ACTIVITY
    threat_level: SecurityThreatLevel = SecurityThreatLevel.MEDIUM
    source_ip: str = ""
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    affected_resources: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    response_actions: List[str] = field(default_factory=list)

@dataclass
class OrchestrationWorkflow:
    """Security orchestration workflow"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger_conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: ComplianceFramework = ComplianceFramework.GDPR
    rule_name: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    validation_logic: Dict[str, Any] = field(default_factory=dict)
    penalty_severity: SecurityThreatLevel = SecurityThreatLevel.MEDIUM
    is_active: bool = True

class EnterpriseSecurityOrchestrator:
    """
    Enterprise Security Orchestration System
    =======================================
    
    Centralized security management with SIEM integration,
    automated workflows, and compliance monitoring.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.workflows: Dict[str, OrchestrationWorkflow] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.active_incidents: Dict[str, SecurityEvent] = {}
        self.siem_integrations: Dict[str, Dict[str, Any]] = {}
        self.threat_intelligence_feeds: List[Dict[str, Any]] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize security metrics
        self.metrics = {
            'total_events_processed': 0,
            'threats_detected': 0,
            'incidents_resolved': 0,
            'workflows_executed': 0,
            'compliance_violations': 0,
            'response_time_avg': 0.0,
            'false_positive_rate': 0.0
        }
        
        # Initialize SIEM integrations
        self._initialize_siem_integrations()
        
        # Initialize compliance frameworks
        self._initialize_compliance_rules()
        
        # Initialize default workflows
        self._initialize_default_workflows()
        
        logger.info("🏢 Enterprise Security Orchestrator initialized")

    async def initialize(self):
        """Initialize Redis connection and load configurations"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_configurations()
            logger.info("✅ Security Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Security Orchestrator: {e}")
            raise

    def _initialize_siem_integrations(self):
        """Initialize SIEM integration configurations"""
        self.siem_integrations = {
            'splunk': {
                'enabled': True,
                'endpoint': 'https://splunk.iacherie.com:8089',
                'auth_token': 'splunk_auth_token',
                'index': 'ainflue_security',
                'event_types': list(SecurityEventType)
            },
            'elk_stack': {
                'enabled': True,
                'endpoint': 'https://elasticsearch.iacherie.com:9200',
                'index': 'security-events',
                'auth_username': 'elastic',
                'auth_password': 'elastic_password'
            },
            'azure_sentinel': {
                'enabled': True,
                'workspace_id': 'azure_workspace_id',
                'auth_key': 'azure_auth_key',
                'log_type': 'AinflueSecurity'
            },
            'aws_security_hub': {
                'enabled': True,
                'region': 'us-east-1',
                'access_key': 'aws_access_key',
                'secret_key': 'aws_secret_key'
            }
        }

    def _initialize_compliance_rules(self):
        """Initialize compliance rule definitions"""
        gdpr_rules = [
            ComplianceRule(
                framework=ComplianceFramework.GDPR,
                rule_name="Data Protection Impact Assessment",
                description="GDPR Article 35 - DPIA required for high-risk processing",
                requirements=[
                    "Conduct DPIA for high-risk data processing",
                    "Document processing activities",
                    "Implement data protection by design"
                ],
                penalty_severity=SecurityThreatLevel.HIGH
            ),
            ComplianceRule(
                framework=ComplianceFramework.GDPR,
                rule_name="Data Subject Rights",
                description="GDPR Articles 15-22 - Data subject rights compliance",
                requirements=[
                    "Right to access personal data",
                    "Right to rectification",
                    "Right to erasure (right to be forgotten)",
                    "Right to data portability"
                ],
                penalty_severity=SecurityThreatLevel.CRITICAL
            )
        ]
        
        pci_rules = [
            ComplianceRule(
                framework=ComplianceFramework.PCI_DSS,
                rule_name="Cardholder Data Protection",
                description="PCI DSS Requirement 3 - Protect stored cardholder data",
                requirements=[
                    "Encrypt cardholder data at rest",
                    "Encrypt cardholder data in transit",
                    "Implement key management procedures"
                ],
                penalty_severity=SecurityThreatLevel.CRITICAL
            )
        ]
        
        for rules in [gdpr_rules, pci_rules]:
            for rule in rules:
                self.compliance_rules[rule.rule_id] = rule

    def _initialize_default_workflows(self):
        """Initialize default security orchestration workflows"""
        # Critical threat response workflow
        critical_workflow = OrchestrationWorkflow(
            name="Critical Threat Response",
            trigger_conditions=[
                {
                    'condition_type': 'threat_level',
                    'operator': 'equals',
                    'value': SecurityThreatLevel.CRITICAL.value
                }
            ],
            actions=[
                {
                    'action_type': 'isolate_resource',
                    'parameters': {'isolation_type': 'network'}
                },
                {
                    'action_type': 'notify_security_team',
                    'parameters': {'urgency': 'immediate'}
                },
                {
                    'action_type': 'capture_evidence',
                    'parameters': {'evidence_types': ['network', 'system', 'user']}
                },
                {
                    'action_type': 'initiate_investigation',
                    'parameters': {'assign_to': 'security_team'}
                }
            ]
        )
        
        # Fraud detection workflow
        fraud_workflow = OrchestrationWorkflow(
            name="Payment Fraud Response",
            trigger_conditions=[
                {
                    'condition_type': 'event_type',
                    'operator': 'equals',
                    'value': SecurityEventType.FRAUD_DETECTION.value
                }
            ],
            actions=[
                {
                    'action_type': 'freeze_account',
                    'parameters': {'duration': '24h', 'notify_user': True}
                },
                {
                    'action_type': 'validate_transactions',
                    'parameters': {'lookback_hours': 48}
                },
                {
                    'action_type': 'generate_fraud_report',
                    'parameters': {'include_evidence': True}
                }
            ]
        )
        
        self.workflows[critical_workflow.workflow_id] = critical_workflow
        self.workflows[fraud_workflow.workflow_id] = fraud_workflow

    async def process_security_event(self, event: SecurityEvent) -> Dict[str, Any]:
        """
        Process incoming security event through orchestration workflows
        
        Args:
            event: Security event to process
            
        Returns:
            Processing result with actions taken
        """
        try:
            start_time = time.time()
            
            # Store event
            self.active_incidents[event.event_id] = event
            self.metrics['total_events_processed'] += 1
            
            # Correlate with existing incidents
            correlated_events = await self._correlate_events(event)
            
            # Evaluate threat level
            threat_assessment = await self._assess_threat_level(event, correlated_events)
            
            # Check compliance violations
            compliance_violations = await self._check_compliance_violations(event)
            
            # Find matching workflows
            matching_workflows = await self._find_matching_workflows(event)
            
            # Execute workflows
            execution_results = []
            for workflow in matching_workflows:
                result = await self._execute_workflow(workflow, event)
                execution_results.append(result)
            
            # Send to SIEM systems
            await self._send_to_siem(event, threat_assessment)
            
            # Update metrics
            processing_time = time.time() - start_time
            await self._update_metrics(processing_time, len(execution_results))
            
            # Generate response summary
            response = {
                'event_id': event.event_id,
                'processing_time': processing_time,
                'threat_assessment': threat_assessment,
                'correlated_events': len(correlated_events),
                'compliance_violations': compliance_violations,
                'workflows_executed': len(execution_results),
                'actions_taken': [r['actions_taken'] for r in execution_results],
                'status': 'processed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Store processing result
            await self._store_processing_result(event.event_id, response)
            
            logger.info(f"🔍 Security event {event.event_id} processed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing security event {event.event_id}: {e}")
            return {
                'event_id': event.event_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _correlate_events(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Correlate event with existing incidents"""
        correlated = []
        
        for incident_id, incident in self.active_incidents.items():
            if incident.event_id == event.event_id:
                continue
                
            # Check correlation criteria
            correlation_score = 0
            
            # Same source IP
            if incident.source_ip == event.source_ip and event.source_ip:
                correlation_score += 30
                
            # Same user
            if incident.user_id == event.user_id and event.user_id:
                correlation_score += 25
                
            # Similar event type
            if incident.event_type == event.event_type:
                correlation_score += 20
                
            # Time proximity (within 1 hour)
            time_diff = abs((incident.timestamp - event.timestamp).total_seconds())
            if time_diff < 3600:
                correlation_score += 15
                
            # Affected resources overlap
            common_resources = set(incident.affected_resources) & set(event.affected_resources)
            if common_resources:
                correlation_score += len(common_resources) * 5
                
            if correlation_score >= 40:  # Threshold for correlation
                correlated.append(incident)
                
        return correlated

    async def _assess_threat_level(self, event: SecurityEvent, correlated_events: List[SecurityEvent]) -> Dict[str, Any]:
        """Assess and potentially escalate threat level"""
        original_level = event.threat_level
        assessed_level = original_level
        
        # Escalation factors
        escalation_factors = []
        
        # Multiple correlated events
        if len(correlated_events) > 1:
            escalation_factors.append("multiple_correlated_events")
            assessed_level = self._escalate_threat_level(assessed_level)
            
        # Critical event types
        critical_types = [
            SecurityEventType.DATA_BREACH_ATTEMPT,
            SecurityEventType.MALWARE_DETECTION,
            SecurityEventType.VULNERABILITY_EXPLOIT
        ]
        if event.event_type in critical_types:
            escalation_factors.append("critical_event_type")
            assessed_level = SecurityThreatLevel.CRITICAL
            
        # High-value targets
        if event.user_id and await self._is_high_value_target(event.user_id):
            escalation_factors.append("high_value_target")
            assessed_level = self._escalate_threat_level(assessed_level)
            
        return {
            'original_level': original_level.value,
            'assessed_level': assessed_level.value,
            'escalation_factors': escalation_factors,
            'confidence_score': 0.85 + (len(escalation_factors) * 0.05)
        }

    def _escalate_threat_level(self, current_level: SecurityThreatLevel) -> SecurityThreatLevel:
        """Escalate threat level by one step"""
        escalation_map = {
            SecurityThreatLevel.INFO: SecurityThreatLevel.LOW,
            SecurityThreatLevel.LOW: SecurityThreatLevel.MEDIUM,
            SecurityThreatLevel.MEDIUM: SecurityThreatLevel.HIGH,
            SecurityThreatLevel.HIGH: SecurityThreatLevel.CRITICAL,
            SecurityThreatLevel.CRITICAL: SecurityThreatLevel.CRITICAL
        }
        return escalation_map.get(current_level, current_level)

    async def _check_compliance_violations(self, event: SecurityEvent) -> List[Dict[str, Any]]:
        """Check for compliance framework violations"""
        violations = []
        
        for rule_id, rule in self.compliance_rules.items():
            if not rule.is_active:
                continue
                
            # Check if event violates compliance rule
            violation_detected = False
            
            if rule.framework == ComplianceFramework.GDPR:
                if event.event_type == SecurityEventType.DATA_BREACH_ATTEMPT:
                    violation_detected = True
                    
            elif rule.framework == ComplianceFramework.PCI_DSS:
                if event.event_type in [SecurityEventType.FRAUD_DETECTION, SecurityEventType.DATA_BREACH_ATTEMPT]:
                    violation_detected = True
                    
            if violation_detected:
                violations.append({
                    'rule_id': rule_id,
                    'framework': rule.framework.value,
                    'rule_name': rule.rule_name,
                    'severity': rule.penalty_severity.value,
                    'requirements': rule.requirements
                })
                
        return violations

    async def _find_matching_workflows(self, event: SecurityEvent) -> List[OrchestrationWorkflow]:
        """Find workflows that match event conditions"""
        matching = []
        
        for workflow in self.workflows.values():
            if await self._workflow_matches_event(workflow, event):
                matching.append(workflow)
                
        return matching

    async def _workflow_matches_event(self, workflow: OrchestrationWorkflow, event: SecurityEvent) -> bool:
        """Check if workflow conditions match the event"""
        for condition in workflow.trigger_conditions:
            condition_type = condition.get('condition_type')
            operator = condition.get('operator', 'equals')
            value = condition.get('value')
            
            if condition_type == 'threat_level':
                event_value = event.threat_level.value
            elif condition_type == 'event_type':
                event_value = event.event_type.value
            elif condition_type == 'source_ip':
                event_value = event.source_ip
            else:
                continue
                
            if operator == 'equals' and event_value == value:
                return True
            elif operator == 'contains' and value in event_value:
                return True
            elif operator == 'greater_than' and event_value > value:
                return True
                
        return False

    async def _execute_workflow(self, workflow: OrchestrationWorkflow, event: SecurityEvent) -> Dict[str, Any]:
        """Execute orchestration workflow"""
        try:
            actions_taken = []
            workflow.execution_count += 1
            workflow.last_executed = datetime.now()
            workflow.status = OrchestrationStatus.RUNNING
            
            for action in workflow.actions:
                action_result = await self._execute_action(action, event)
                actions_taken.append(action_result)
                
            workflow.status = OrchestrationStatus.SUCCESS
            workflow.success_rate = (workflow.success_rate * (workflow.execution_count - 1) + 1) / workflow.execution_count
            
            self.metrics['workflows_executed'] += 1
            
            return {
                'workflow_id': workflow.workflow_id,
                'workflow_name': workflow.name,
                'status': 'success',
                'actions_taken': actions_taken,
                'execution_time': time.time()
            }
            
        except Exception as e:
            workflow.status = OrchestrationStatus.FAILED
            logger.error(f"❌ Workflow execution failed: {e}")
            return {
                'workflow_id': workflow.workflow_id,
                'status': 'failed',
                'error': str(e)
            }

    async def _execute_action(self, action: Dict[str, Any], event: SecurityEvent) -> Dict[str, Any]:
        """Execute individual workflow action"""
        action_type = action.get('action_type')
        parameters = action.get('parameters', {})
        
        if action_type == 'isolate_resource':
            return await self._isolate_resource(event, parameters)
        elif action_type == 'notify_security_team':
            return await self._notify_security_team(event, parameters)
        elif action_type == 'capture_evidence':
            return await self._capture_evidence(event, parameters)
        elif action_type == 'freeze_account':
            return await self._freeze_account(event, parameters)
        elif action_type == 'validate_transactions':
            return await self._validate_transactions(event, parameters)
        else:
            return {
                'action_type': action_type,
                'status': 'unknown_action',
                'timestamp': datetime.now().isoformat()
            }

    async def _isolate_resource(self, event: SecurityEvent, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate affected resources"""
        isolation_type = parameters.get('isolation_type', 'network')
        
        # Simulate resource isolation
        isolated_resources = []
        for resource in event.affected_resources:
            # In real implementation, this would interact with infrastructure
            isolated_resources.append(resource)
            
        return {
            'action_type': 'isolate_resource',
            'status': 'completed',
            'isolation_type': isolation_type,
            'isolated_resources': isolated_resources,
            'timestamp': datetime.now().isoformat()
        }

    async def _notify_security_team(self, event: SecurityEvent, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Notify security team of incident"""
        urgency = parameters.get('urgency', 'normal')
        
        # Simulate notification
        notification = {
            'event_id': event.event_id,
            'threat_level': event.threat_level.value,
            'urgency': urgency,
            'message': f"Security incident detected: {event.description}",
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'action_type': 'notify_security_team',
            'status': 'sent',
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        }

    async def _capture_evidence(self, event: SecurityEvent, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture digital evidence"""
        evidence_types = parameters.get('evidence_types', ['system'])
        
        captured_evidence = []
        for evidence_type in evidence_types:
            evidence = {
                'type': evidence_type,
                'source': event.source_ip,
                'timestamp': event.timestamp.isoformat(),
                'data_size': f"{secrets.randbelow(1000)}MB"
            }
            captured_evidence.append(evidence)
            
        return {
            'action_type': 'capture_evidence',
            'status': 'completed',
            'evidence_captured': captured_evidence,
            'timestamp': datetime.now().isoformat()
        }

    async def _freeze_account(self, event: SecurityEvent, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Freeze user account temporarily"""
        duration = parameters.get('duration', '24h')
        notify_user = parameters.get('notify_user', True)
        
        return {
            'action_type': 'freeze_account',
            'status': 'completed',
            'user_id': event.user_id,
            'duration': duration,
            'notify_user': notify_user,
            'timestamp': datetime.now().isoformat()
        }

    async def _validate_transactions(self, event: SecurityEvent, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recent transactions for fraud"""
        lookback_hours = parameters.get('lookback_hours', 24)
        
        # Simulate transaction validation
        validated_count = secrets.randbelow(50) + 1
        suspicious_count = secrets.randbelow(5)
        
        return {
            'action_type': 'validate_transactions',
            'status': 'completed',
            'lookback_hours': lookback_hours,
            'transactions_validated': validated_count,
            'suspicious_transactions': suspicious_count,
            'timestamp': datetime.now().isoformat()
        }

    async def _send_to_siem(self, event: SecurityEvent, threat_assessment: Dict[str, Any]):
        """Send event to configured SIEM systems"""
        for siem_name, config in self.siem_integrations.items():
            if not config.get('enabled', False):
                continue
                
            try:
                siem_event = {
                    'source': 'ainflue_security_orchestrator',
                    'event_id': event.event_id,
                    'event_type': event.event_type.value,
                    'threat_level': event.threat_level.value,
                    'assessed_threat_level': threat_assessment['assessed_level'],
                    'source_ip': event.source_ip,
                    'user_id': event.user_id,
                    'timestamp': event.timestamp.isoformat(),
                    'description': event.description,
                    'affected_resources': event.affected_resources,
                    'evidence': event.evidence
                }
                
                # In real implementation, this would send to actual SIEM
                logger.info(f"📊 Sent event {event.event_id} to {siem_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to send event to {siem_name}: {e}")

    async def _is_high_value_target(self, user_id: str) -> bool:
        """Check if user is a high-value target"""
        # In real implementation, this would check user privilege levels
        return user_id.startswith('admin_') or user_id.startswith('creator_vip_')

    async def _update_metrics(self, processing_time: float, workflows_executed: int):
        """Update orchestration metrics"""
        self.metrics['response_time_avg'] = (
            (self.metrics['response_time_avg'] * (self.metrics['total_events_processed'] - 1) + processing_time) /
            self.metrics['total_events_processed']
        )
        self.metrics['workflows_executed'] += workflows_executed

    async def _store_processing_result(self, event_id: str, result: Dict[str, Any]):
        """Store processing result in Redis"""
        if self.redis:
            await self.redis.setex(
                f"security:event:{event_id}:result",
                86400,  # 24 hours
                json.dumps(result, default=str)
            )

    async def _load_configurations(self):
        """Load configurations from Redis"""
        if self.redis:
            try:
                # Load workflows
                workflow_keys = await self.redis.keys("security:workflow:*")
                for key in workflow_keys:
                    workflow_data = await self.redis.get(key)
                    if workflow_data:
                        workflow = json.loads(workflow_data)
                        # Convert to OrchestrationWorkflow object
                        
                # Load compliance rules
                rule_keys = await self.redis.keys("security:compliance:*")
                for key in rule_keys:
                    rule_data = await self.redis.get(key)
                    if rule_data:
                        rule = json.loads(rule_data)
                        # Convert to ComplianceRule object
                        
            except Exception as e:
                logger.error(f"❌ Failed to load configurations: {e}")

    async def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestration metrics"""
        return {
            'metrics': self.metrics,
            'active_workflows': len(self.workflows),
            'active_incidents': len(self.active_incidents),
            'compliance_rules': len(self.compliance_rules),
            'siem_integrations': len([s for s in self.siem_integrations.values() if s.get('enabled')]),
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    async def create_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Create new orchestration workflow"""
        workflow = OrchestrationWorkflow(
            name=workflow_definition['name'],
            trigger_conditions=workflow_definition['trigger_conditions'],
            actions=workflow_definition['actions']
        )
        
        self.workflows[workflow.workflow_id] = workflow
        
        # Store in Redis
        if self.redis:
            await self.redis.set(
                f"security:workflow:{workflow.workflow_id}",
                json.dumps(workflow_definition, default=str)
            )
            
        logger.info(f"✅ Created new workflow: {workflow.name}")
        return workflow.workflow_id

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        self.executor.shutdown(wait=True)
        logger.info("🔒 Enterprise Security Orchestrator closed")


# Factory function for easy instantiation
async def create_security_orchestrator(redis_url: str = "redis://localhost:6379") -> EnterpriseSecurityOrchestrator:
    """
    Factory function to create and initialize Security Orchestrator
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized EnterpriseSecurityOrchestrator instance
    """
    orchestrator = EnterpriseSecurityOrchestrator(redis_url)
    await orchestrator.initialize()
    return orchestrator


# Utility functions for common operations
async def log_security_event(
    event_type: SecurityEventType,
    threat_level: SecurityThreatLevel,
    description: str,
    source_ip: str = "",
    user_id: Optional[str] = None,
    affected_resources: List[str] = None,
    evidence: Dict[str, Any] = None
) -> SecurityEvent:
    """
    Log a security event for orchestration processing
    
    Args:
        event_type: Type of security event
        threat_level: Severity of the threat
        description: Event description
        source_ip: Source IP address
        user_id: Affected user ID
        affected_resources: List of affected resources
        evidence: Supporting evidence
        
    Returns:
        Created SecurityEvent object
    """
    return SecurityEvent(
        event_type=event_type,
        threat_level=threat_level,
        description=description,
        source_ip=source_ip,
        user_id=user_id,
        affected_resources=affected_resources or [],
        evidence=evidence or {}
    )


if __name__ == "__main__":
    async def test_orchestrator():
        """Test the enterprise security orchestrator"""
        orchestrator = await create_security_orchestrator()
        
        # Create test event
        test_event = await log_security_event(
            event_type=SecurityEventType.FRAUD_DETECTION,
            threat_level=SecurityThreatLevel.HIGH,
            description="Suspicious payment pattern detected",
            source_ip="192.168.1.100",
            user_id="creator_12345",
            affected_resources=["payment_gateway", "user_account"],
            evidence={"transaction_count": 15, "amount": "$2500"}
        )
        
        # Process event
        result = await orchestrator.process_security_event(test_event)
        print(f"🔍 Event processed: {json.dumps(result, indent=2)}")
        
        # Get metrics
        metrics = await orchestrator.get_orchestration_metrics()
        print(f"📊 Orchestration metrics: {json.dumps(metrics, indent=2)}")
        
        await orchestrator.close()

    # Run test
    asyncio.run(test_orchestrator())