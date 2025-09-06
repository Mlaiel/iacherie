"""Audit Trail Collector for Events Security

Comprehensive audit trail collection with compliance and forensics capabilities.
Provides immutable audit storage and real-time compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit trail detail levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    FORENSIC = "forensic"


class ComplianceRegulation(Enum):
    """Supported compliance regulations"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"


@dataclass
class AuditRecord:
    """Immutable audit record"""
    audit_id: str
    event_id: str
    event_type: str
    user_id: str
    timestamp: datetime
    action: str
    resource: str
    outcome: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    business_context: Dict[str, Any] = None
    security_context: Dict[str, Any] = None
    compliance_tags: List[str] = None
    risk_score: float = 0.0
    data_hash: Optional[str] = None
    previous_record_hash: Optional[str] = None
    
    def __post_init__(self):
        if self.business_context is None:
            self.business_context = {}
        if self.security_context is None:
            self.security_context = {}
        if self.compliance_tags is None:
            self.compliance_tags = []
        
        # Generate data hash for integrity
        if self.data_hash is None:
            self.data_hash = self._generate_data_hash()
    
    def _generate_data_hash(self) -> str:
        """Generate hash for data integrity verification"""
        
        # Create hashable content excluding the hash fields
        hashable_data = {
            'audit_id': self.audit_id,
            'event_id': self.event_id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'resource': self.resource,
            'outcome': self.outcome,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'business_context': json.dumps(self.business_context, sort_keys=True),
            'security_context': json.dumps(self.security_context, sort_keys=True),
            'compliance_tags': sorted(self.compliance_tags),
            'risk_score': self.risk_score
        }
        
        content = json.dumps(hashable_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class ComplianceValidation:
    """Compliance validation result"""
    regulation: ComplianceRegulation
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    retention_period: timedelta
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ForensicAnalysis:
    """Forensic analysis result"""
    analysis_id: str
    event_chain: List[str]
    suspicious_patterns: List[str]
    correlation_events: List[str]
    timeline: List[Dict[str, Any]]
    confidence_score: float
    findings: str


class AuditTrailCollector:
    """
    Advanced audit trail collector for compliance and forensic analysis.
    Provides immutable storage with blockchain-style validation.
    """
    
    def __init__(self):
        self.enabled = True
        self.audit_level = AuditLevel.STANDARD
        self.audit_storage = []  # In-memory storage for demo
        self.compliance_rules = self._initialize_compliance_rules()
        self.last_record_hash = None
        self.audit_index = {}  # Fast lookup index
        self.compliance_cache = {}
        logger.info("AuditTrailCollector initialized")
    
    async def collect_event_audit(self,
                                event: Any,
                                user_id: str,
                                action: str,
                                outcome: str,
                                security_context: Dict[str, Any] = None,
                                business_context: Dict[str, Any] = None,
                                request_metadata: Dict[str, Any] = None) -> AuditRecord:
        """
        Collect comprehensive audit trail for an event.
        
        Args:
            event: Domain event being audited
            user_id: User performing the action
            action: Action being performed
            outcome: Result of the action
            security_context: Security-related context
            business_context: Business-related context
            request_metadata: HTTP request metadata
            
        Returns:
            AuditRecord with complete audit information
        """
        if not self.enabled:
            return self._create_minimal_audit_record(event, user_id, action, outcome)
        
        try:
            # Extract event details
            event_id = getattr(event, 'event_id', f'unknown_{datetime.utcnow().timestamp()}')
            event_type = getattr(event, 'event_type', 'unknown')
            
            # Create comprehensive audit record
            audit_record = await self._create_comprehensive_audit_record(
                event_id, event_type, user_id, action, outcome,
                security_context, business_context, request_metadata
            )
            
            # Enrich with business context
            enriched_record = await self._enrich_with_business_context(
                audit_record, business_context
            )
            
            # Apply compliance validation
            compliance_validation = await self._validate_compliance(enriched_record)
            enriched_record.compliance_tags.extend(self._extract_compliance_tags(compliance_validation))
            
            # Store with blockchain-style linking
            stored_record = await self._store_audit_record_immutable(enriched_record)
            
            # Update indexes for fast retrieval
            self._update_audit_indexes(stored_record)
            
            # Real-time compliance monitoring
            await self._monitor_compliance_violations(stored_record, compliance_validation)
            
            logger.debug(f"Audit trail collected for event {event_id}")
            return stored_record
            
        except Exception as e:
            logger.error(f"Error collecting audit trail: {str(e)}")
            return self._create_error_audit_record(event, user_id, action, str(e))
    
    async def _create_comprehensive_audit_record(self,
                                               event_id: str,
                                               event_type: str,
                                               user_id: str,
                                               action: str,
                                               outcome: str,
                                               security_context: Dict[str, Any],
                                               business_context: Dict[str, Any],
                                               request_metadata: Dict[str, Any]) -> AuditRecord:
        """Create comprehensive audit record with all context"""
        
        # Generate unique audit ID
        audit_id = f"audit_{datetime.utcnow().timestamp()}_{event_id}"
        
        # Extract request metadata
        request_metadata = request_metadata or {}
        ip_address = request_metadata.get('ip_address')
        user_agent = request_metadata.get('user_agent')
        session_id = request_metadata.get('session_id')
        
        # Determine resource from event type
        resource = self._extract_resource_from_event_type(event_type)
        
        # Calculate risk score
        risk_score = await self._calculate_audit_risk_score(
            event_type, action, outcome, security_context, business_context
        )
        
        # Create base audit record
        audit_record = AuditRecord(
            audit_id=audit_id,
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            action=action,
            resource=resource,
            outcome=outcome,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            business_context=business_context or {},
            security_context=security_context or {},
            risk_score=risk_score,
            previous_record_hash=self.last_record_hash
        )
        
        return audit_record
    
    async def _enrich_with_business_context(self,
                                          audit_record: AuditRecord,
                                          business_context: Dict[str, Any]) -> AuditRecord:
        """Enrich audit record with additional business context"""
        
        if not business_context:
            return audit_record
        
        # Add business metadata based on event type
        if audit_record.event_type.startswith("content."):
            audit_record.business_context.update({
                'content_type': business_context.get('content_type', 'unknown'),
                'content_size': business_context.get('file_size', 0),
                'processing_type': business_context.get('processing_type', 'standard')
            })
        
        elif audit_record.event_type.startswith("collaboration."):
            audit_record.business_context.update({
                'collaboration_type': business_context.get('collaboration_type', 'standard'),
                'participants_count': business_context.get('participants_count', 0),
                'revenue_sharing': business_context.get('revenue_sharing_active', False)
            })
        
        elif audit_record.event_type.startswith("monetization."):
            audit_record.business_context.update({
                'transaction_amount': business_context.get('amount', 0),
                'currency': business_context.get('currency', 'USD'),
                'cross_border': business_context.get('cross_border', False),
                'payment_method': business_context.get('payment_method', 'unknown')
            })
        
        # Add user context
        audit_record.business_context.update({
            'user_region': business_context.get('user_region', 'unknown'),
            'user_tier': business_context.get('user_tier', 'basic'),
            'account_age_days': business_context.get('account_age_days', 0)
        })
        
        # Regenerate hash after enrichment
        audit_record.data_hash = audit_record._generate_data_hash()
        
        return audit_record
    
    async def _validate_compliance(self, audit_record: AuditRecord) -> List[ComplianceValidation]:
        """Validate audit record against compliance regulations"""
        
        validations = []
        
        # GDPR validation
        gdpr_validation = await self._validate_gdpr_compliance(audit_record)
        validations.append(gdpr_validation)
        
        # CCPA validation
        ccpa_validation = await self._validate_ccpa_compliance(audit_record)
        validations.append(ccpa_validation)
        
        # Financial regulations (SOX, PCI-DSS)
        if audit_record.event_type.startswith("monetization."):
            sox_validation = await self._validate_sox_compliance(audit_record)
            validations.append(sox_validation)
            
            pci_validation = await self._validate_pci_compliance(audit_record)
            validations.append(pci_validation)
        
        return validations
    
    async def _validate_gdpr_compliance(self, audit_record: AuditRecord) -> ComplianceValidation:
        """Validate GDPR compliance"""
        
        violations = []
        recommendations = []
        
        # Check for EU user data processing
        user_region = audit_record.business_context.get('user_region', '')
        is_eu_user = user_region in ['EU', 'UK', 'DE', 'FR', 'IT', 'ES']
        
        if is_eu_user:
            # Check for data processing events
            if audit_record.event_type in ['user.data.export', 'user.data.delete']:
                if audit_record.outcome != 'success':
                    violations.append("Failed GDPR data subject rights request")
                    recommendations.append("Ensure GDPR data subject rights are properly fulfilled")
            
            # Check for data retention
            if 'data.retention' not in audit_record.compliance_tags:
                recommendations.append("Apply GDPR data retention policies")
            
            # Check for consent tracking
            if audit_record.event_type.startswith("user.consent"):
                if 'consent_timestamp' not in audit_record.business_context:
                    violations.append("Missing consent timestamp for GDPR compliance")
                    recommendations.append("Record explicit consent timestamps")
        
        compliant = len(violations) == 0
        retention_period = timedelta(days=2555)  # 7 years for GDPR
        
        return ComplianceValidation(
            regulation=ComplianceRegulation.GDPR,
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            retention_period=retention_period
        )
    
    async def _validate_ccpa_compliance(self, audit_record: AuditRecord) -> ComplianceValidation:
        """Validate CCPA compliance"""
        
        violations = []
        recommendations = []
        
        # Check for California user data processing
        user_region = audit_record.business_context.get('user_region', '')
        is_ca_user = user_region in ['CA', 'US-CA']
        
        if is_ca_user:
            # Check for data sale events
            if 'data.sale' in audit_record.event_type:
                if 'opt_out_verified' not in audit_record.business_context:
                    violations.append("CCPA data sale without opt-out verification")
                    recommendations.append("Verify user opt-out status before data sales")
            
            # Check for personal information collection
            if 'personal_info' in audit_record.business_context:
                if 'purpose_disclosed' not in audit_record.business_context:
                    violations.append("Personal information collection without disclosed purpose")
                    recommendations.append("Disclose purpose of personal information collection")
        
        compliant = len(violations) == 0
        retention_period = timedelta(days=1095)  # 3 years for CCPA
        
        return ComplianceValidation(
            regulation=ComplianceRegulation.CCPA,
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            retention_period=retention_period
        )
    
    async def _validate_sox_compliance(self, audit_record: AuditRecord) -> ComplianceValidation:
        """Validate SOX compliance for financial events"""
        
        violations = []
        recommendations = []
        
        # Check for financial transaction controls
        transaction_amount = audit_record.business_context.get('transaction_amount', 0)
        
        if transaction_amount > 10000:  # High-value transactions
            if 'approval_trail' not in audit_record.business_context:
                violations.append("High-value transaction without approval trail")
                recommendations.append("Maintain complete approval trail for high-value transactions")
            
            if 'segregation_of_duties' not in audit_record.security_context:
                violations.append("Missing segregation of duties verification")
                recommendations.append("Implement segregation of duties controls")
        
        # Check for financial access controls
        if audit_record.action in ['financial.approve', 'financial.execute']:
            if 'dual_authorization' not in audit_record.security_context:
                violations.append("Financial action without dual authorization")
                recommendations.append("Require dual authorization for financial actions")
        
        compliant = len(violations) == 0
        retention_period = timedelta(days=2555)  # 7 years for SOX
        
        return ComplianceValidation(
            regulation=ComplianceRegulation.SOX,
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            retention_period=retention_period
        )
    
    async def _validate_pci_compliance(self, audit_record: AuditRecord) -> ComplianceValidation:
        """Validate PCI-DSS compliance for payment events"""
        
        violations = []
        recommendations = []
        
        # Check for payment data handling
        payment_method = audit_record.business_context.get('payment_method', '')
        
        if 'card' in payment_method.lower():
            # Check for card data security
            if 'pci_compliant_processor' not in audit_record.security_context:
                violations.append("Card payment without PCI-compliant processor verification")
                recommendations.append("Ensure all card payments use PCI-compliant processors")
            
            # Check for data encryption
            if 'data_encrypted' not in audit_record.security_context:
                violations.append("Payment data without encryption verification")
                recommendations.append("Verify encryption of all payment data")
            
            # Check for access logging
            if audit_record.action == 'payment.view' and audit_record.outcome == 'success':
                if 'justification' not in audit_record.business_context:
                    violations.append("Payment data access without business justification")
                    recommendations.append("Record business justification for payment data access")
        
        compliant = len(violations) == 0
        retention_period = timedelta(days=365)  # 1 year for PCI-DSS
        
        return ComplianceValidation(
            regulation=ComplianceRegulation.PCI_DSS,
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            retention_period=retention_period
        )
    
    async def _store_audit_record_immutable(self, audit_record: AuditRecord) -> AuditRecord:
        """Store audit record with immutable blockchain-style linking"""
        
        # Link to previous record
        audit_record.previous_record_hash = self.last_record_hash
        
        # Regenerate hash with previous record link
        audit_record.data_hash = audit_record._generate_data_hash()
        
        # Store record
        self.audit_storage.append(audit_record)
        
        # Update last record hash
        self.last_record_hash = audit_record.data_hash
        
        return audit_record
    
    def _update_audit_indexes(self, audit_record: AuditRecord):
        """Update indexes for fast audit trail retrieval"""
        
        # User index
        user_id = audit_record.user_id
        if user_id not in self.audit_index:
            self.audit_index[user_id] = {'records': [], 'event_types': set()}
        
        self.audit_index[user_id]['records'].append(audit_record.audit_id)
        self.audit_index[user_id]['event_types'].add(audit_record.event_type)
        
        # Event type index
        event_type = audit_record.event_type
        if f"event_type_{event_type}" not in self.audit_index:
            self.audit_index[f"event_type_{event_type}"] = []
        
        self.audit_index[f"event_type_{event_type}"].append(audit_record.audit_id)
        
        # Date index
        date_key = f"date_{audit_record.timestamp.date()}"
        if date_key not in self.audit_index:
            self.audit_index[date_key] = []
        
        self.audit_index[date_key].append(audit_record.audit_id)
    
    async def _monitor_compliance_violations(self,
                                           audit_record: AuditRecord,
                                           compliance_validations: List[ComplianceValidation]):
        """Monitor for compliance violations in real-time"""
        
        for validation in compliance_validations:
            if not validation.compliant:
                # Log violations
                logger.warning(f"Compliance violation detected: {validation.regulation.value}")
                logger.warning(f"Violations: {', '.join(validation.violations)}")
                
                # In a real implementation, this would trigger alerts
                await self._trigger_compliance_alert(audit_record, validation)
    
    async def _trigger_compliance_alert(self,
                                      audit_record: AuditRecord,
                                      violation: ComplianceValidation):
        """Trigger alerts for compliance violations"""
        
        # In a real implementation, this would send alerts to compliance team
        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'audit_id': audit_record.audit_id,
            'user_id': audit_record.user_id,
            'regulation': violation.regulation.value,
            'violations': violation.violations,
            'recommendations': violation.recommendations
        }
        
        logger.error(f"COMPLIANCE ALERT: {json.dumps(alert_data, indent=2)}")
    
    async def perform_forensic_analysis(self,
                                      event_id: str,
                                      time_window: timedelta = None) -> ForensicAnalysis:
        """
        Perform forensic analysis around a specific event.
        
        Args:
            event_id: Event to analyze
            time_window: Time window around event to analyze
            
        Returns:
            ForensicAnalysis with findings
        """
        time_window = time_window or timedelta(hours=24)
        
        try:
            # Find the target event
            target_record = self._find_audit_record_by_event(event_id)
            if not target_record:
                raise ValueError(f"Event {event_id} not found in audit trail")
            
            # Get related events in time window
            related_events = await self._get_related_events(target_record, time_window)
            
            # Analyze event chain
            event_chain = await self._analyze_event_chain(target_record, related_events)
            
            # Detect suspicious patterns
            suspicious_patterns = await self._detect_suspicious_patterns(related_events)
            
            # Find correlation events
            correlation_events = await self._find_correlation_events(target_record, related_events)
            
            # Build timeline
            timeline = self._build_forensic_timeline(related_events)
            
            # Calculate confidence score
            confidence_score = self._calculate_forensic_confidence(
                event_chain, suspicious_patterns, correlation_events
            )
            
            # Generate findings
            findings = await self._generate_forensic_findings(
                target_record, event_chain, suspicious_patterns, correlation_events
            )
            
            analysis_id = f"forensic_{datetime.utcnow().timestamp()}_{event_id}"
            
            return ForensicAnalysis(
                analysis_id=analysis_id,
                event_chain=event_chain,
                suspicious_patterns=suspicious_patterns,
                correlation_events=correlation_events,
                timeline=timeline,
                confidence_score=confidence_score,
                findings=findings
            )
            
        except Exception as e:
            logger.error(f"Error in forensic analysis: {str(e)}")
            raise
    
    async def _get_related_events(self,
                                target_record: AuditRecord,
                                time_window: timedelta) -> List[AuditRecord]:
        """Get events related to target event within time window"""
        
        start_time = target_record.timestamp - time_window
        end_time = target_record.timestamp + time_window
        
        related_events = []
        
        for record in self.audit_storage:
            if start_time <= record.timestamp <= end_time:
                # Include events from same user
                if record.user_id == target_record.user_id:
                    related_events.append(record)
                
                # Include events from same session
                elif (record.session_id and target_record.session_id and 
                      record.session_id == target_record.session_id):
                    related_events.append(record)
                
                # Include events from same IP
                elif (record.ip_address and target_record.ip_address and
                      record.ip_address == target_record.ip_address):
                    related_events.append(record)
        
        return sorted(related_events, key=lambda x: x.timestamp)
    
    async def _analyze_event_chain(self,
                                 target_record: AuditRecord,
                                 related_events: List[AuditRecord]) -> List[str]:
        """Analyze the chain of events leading to and from target event"""
        
        event_chain = []
        
        # Events before target
        before_events = [e for e in related_events if e.timestamp < target_record.timestamp]
        before_events = sorted(before_events, key=lambda x: x.timestamp)
        
        # Events after target
        after_events = [e for e in related_events if e.timestamp > target_record.timestamp]
        after_events = sorted(after_events, key=lambda x: x.timestamp)
        
        # Build chain description
        for event in before_events[-5:]:  # Last 5 events before
            event_chain.append(f"BEFORE: {event.event_type} - {event.action} ({event.outcome})")
        
        event_chain.append(f"TARGET: {target_record.event_type} - {target_record.action} ({target_record.outcome})")
        
        for event in after_events[:5]:  # First 5 events after
            event_chain.append(f"AFTER: {event.event_type} - {event.action} ({event.outcome})")
        
        return event_chain
    
    async def _detect_suspicious_patterns(self, events: List[AuditRecord]) -> List[str]:
        """Detect suspicious patterns in event sequence"""
        
        patterns = []
        
        # Rapid succession of failed events
        failed_events = [e for e in events if e.outcome == 'failure']
        if len(failed_events) > 5:
            patterns.append(f"High failure rate: {len(failed_events)} failed events")
        
        # Multiple IP addresses for same user
        user_events = {}
        for event in events:
            if event.user_id not in user_events:
                user_events[event.user_id] = {'ips': set(), 'sessions': set()}
            
            if event.ip_address:
                user_events[event.user_id]['ips'].add(event.ip_address)
            if event.session_id:
                user_events[event.user_id]['sessions'].add(event.session_id)
        
        for user_id, data in user_events.items():
            if len(data['ips']) > 3:
                patterns.append(f"User {user_id} accessed from {len(data['ips'])} different IPs")
        
        # Unusual time patterns
        hours = [e.timestamp.hour for e in events]
        if any(hour < 6 or hour > 22 for hour in hours):
            patterns.append("Activity during unusual hours (night/early morning)")
        
        # High-risk event types
        high_risk_events = [e for e in events if e.risk_score > 0.7]
        if len(high_risk_events) > 3:
            patterns.append(f"Multiple high-risk events: {len(high_risk_events)} events with risk > 0.7")
        
        return patterns
    
    async def _find_correlation_events(self,
                                     target_record: AuditRecord,
                                     related_events: List[AuditRecord]) -> List[str]:
        """Find events that correlate with the target event"""
        
        correlations = []
        
        # Same resource access
        same_resource_events = [
            e for e in related_events 
            if e.resource == target_record.resource and e.audit_id != target_record.audit_id
        ]
        
        if same_resource_events:
            correlations.append(f"Same resource accessed {len(same_resource_events)} times")
        
        # Similar business context
        target_context = target_record.business_context
        for event in related_events:
            if event.audit_id != target_record.audit_id:
                # Check for similar transaction amounts
                if ('transaction_amount' in target_context and 
                    'transaction_amount' in event.business_context):
                    target_amount = target_context['transaction_amount']
                    event_amount = event.business_context['transaction_amount']
                    if abs(target_amount - event_amount) < target_amount * 0.1:  # Within 10%
                        correlations.append(f"Similar transaction amount: {event_amount}")
        
        return correlations
    
    def _build_forensic_timeline(self, events: List[AuditRecord]) -> List[Dict[str, Any]]:
        """Build forensic timeline of events"""
        
        timeline = []
        
        for event in sorted(events, key=lambda x: x.timestamp):
            timeline.append({
                'timestamp': event.timestamp.isoformat(),
                'event_id': event.event_id,
                'event_type': event.event_type,
                'action': event.action,
                'outcome': event.outcome,
                'user_id': event.user_id,
                'ip_address': event.ip_address,
                'risk_score': event.risk_score
            })
        
        return timeline
    
    def _calculate_forensic_confidence(self,
                                     event_chain: List[str],
                                     suspicious_patterns: List[str],
                                     correlation_events: List[str]) -> float:
        """Calculate confidence score for forensic analysis"""
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence based on evidence
        if len(event_chain) > 5:
            confidence += 0.1
        
        if len(suspicious_patterns) > 0:
            confidence += min(0.3, len(suspicious_patterns) * 0.1)
        
        if len(correlation_events) > 0:
            confidence += min(0.2, len(correlation_events) * 0.05)
        
        return min(confidence, 1.0)
    
    async def _generate_forensic_findings(self,
                                        target_record: AuditRecord,
                                        event_chain: List[str],
                                        suspicious_patterns: List[str],
                                        correlation_events: List[str]) -> str:
        """Generate forensic findings summary"""
        
        findings_parts = []
        
        findings_parts.append(f"FORENSIC ANALYSIS FOR EVENT: {target_record.event_id}")
        findings_parts.append(f"Event Type: {target_record.event_type}")
        findings_parts.append(f"User: {target_record.user_id}")
        findings_parts.append(f"Timestamp: {target_record.timestamp}")
        findings_parts.append(f"Outcome: {target_record.outcome}")
        findings_parts.append(f"Risk Score: {target_record.risk_score}")
        
        if suspicious_patterns:
            findings_parts.append("\nSUSPICIOUS PATTERNS DETECTED:")
            for pattern in suspicious_patterns:
                findings_parts.append(f"- {pattern}")
        
        if correlation_events:
            findings_parts.append("\nCORRELATED EVENTS:")
            for correlation in correlation_events:
                findings_parts.append(f"- {correlation}")
        
        findings_parts.append(f"\nEVENT CHAIN ANALYSIS:")
        findings_parts.append(f"Total events in chain: {len(event_chain)}")
        
        if len(suspicious_patterns) > 3:
            findings_parts.append("\nRECOMMENDATION: High suspicious activity detected. Manual investigation recommended.")
        elif len(suspicious_patterns) > 1:
            findings_parts.append("\nRECOMMENDATION: Moderate suspicious activity. Monitor closely.")
        else:
            findings_parts.append("\nRECOMMENDATION: Normal activity pattern detected.")
        
        return "\n".join(findings_parts)
    
    def _extract_resource_from_event_type(self, event_type: str) -> str:
        """Extract resource type from event type"""
        
        if event_type.startswith("content."):
            return "content"
        elif event_type.startswith("user."):
            return "user_account"
        elif event_type.startswith("collaboration."):
            return "collaboration"
        elif event_type.startswith("monetization."):
            return "financial_transaction"
        elif event_type.startswith("distribution."):
            return "distribution_channel"
        else:
            return "system"
    
    async def _calculate_audit_risk_score(self,
                                        event_type: str,
                                        action: str,
                                        outcome: str,
                                        security_context: Dict[str, Any],
                                        business_context: Dict[str, Any]) -> float:
        """Calculate risk score for audit event"""
        
        risk_score = 0.0
        
        # Base risk by event type
        event_risk_map = {
            'user.auth.failed': 0.6,
            'monetization.payment': 0.7,
            'user.data.export': 0.5,
            'content.upload': 0.3,
            'collaboration.initiate': 0.2
        }
        
        risk_score = event_risk_map.get(event_type, 0.1)
        
        # Increase risk for failures
        if outcome == 'failure':
            risk_score += 0.3
        
        # Increase risk for high-value transactions
        if business_context:
            amount = business_context.get('transaction_amount', 0)
            if amount > 10000:
                risk_score += 0.2
            
            # Cross-border transactions
            if business_context.get('cross_border', False):
                risk_score += 0.1
        
        # Security context factors
        if security_context:
            # No MFA
            if not security_context.get('mfa_verified', False):
                risk_score += 0.1
            
            # Unusual location
            if security_context.get('unusual_location', False):
                risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _extract_compliance_tags(self, validations: List[ComplianceValidation]) -> List[str]:
        """Extract compliance tags from validations"""
        
        tags = []
        
        for validation in validations:
            regulation = validation.regulation.value
            
            if validation.compliant:
                tags.append(f"{regulation}_compliant")
            else:
                tags.append(f"{regulation}_violation")
            
            # Add retention tag
            retention_days = validation.retention_period.days
            tags.append(f"retention_{retention_days}days")
        
        return tags
    
    def _find_audit_record_by_event(self, event_id: str) -> Optional[AuditRecord]:
        """Find audit record by event ID"""
        
        for record in self.audit_storage:
            if record.event_id == event_id:
                return record
        
        return None
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance rules and regulations"""
        
        return {
            'gdpr': {
                'data_retention_days': 2555,  # 7 years
                'required_fields': ['user_consent', 'data_purpose'],
                'data_subject_rights': ['access', 'rectification', 'erasure', 'portability']
            },
            'ccpa': {
                'data_retention_days': 1095,  # 3 years
                'required_fields': ['opt_out_status', 'purpose_disclosure'],
                'consumer_rights': ['know', 'delete', 'opt_out', 'non_discrimination']
            },
            'sox': {
                'data_retention_days': 2555,  # 7 years
                'required_controls': ['segregation_of_duties', 'approval_trail'],
                'financial_thresholds': {'high_value': 10000}
            },
            'pci_dss': {
                'data_retention_days': 365,  # 1 year
                'required_controls': ['encryption', 'access_logging', 'compliance_verification'],
                'scope': ['card_payments', 'cardholder_data']
            }
        }
    
    def _create_minimal_audit_record(self,
                                   event: Any,
                                   user_id: str,
                                   action: str,
                                   outcome: str) -> AuditRecord:
        """Create minimal audit record when auditing is disabled"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        event_type = getattr(event, 'event_type', 'unknown')
        
        return AuditRecord(
            audit_id=f"minimal_{datetime.utcnow().timestamp()}",
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            action=action,
            resource="unknown",
            outcome=outcome,
            business_context={'auditing': 'disabled'},
            security_context={'level': 'minimal'}
        )
    
    def _create_error_audit_record(self,
                                 event: Any,
                                 user_id: str,
                                 action: str,
                                 error_message: str) -> AuditRecord:
        """Create error audit record when collection fails"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        event_type = getattr(event, 'event_type', 'unknown')
        
        return AuditRecord(
            audit_id=f"error_{datetime.utcnow().timestamp()}",
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            action=action,
            resource="audit_system",
            outcome="error",
            business_context={'error': error_message},
            security_context={'audit_failed': True},
            risk_score=0.5  # Medium risk when audit fails
        )
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics"""
        
        if not self.audit_storage:
            return {
                'total_records': 0,
                'compliance_violations': 0,
                'high_risk_events': 0,
                'last_audit': None
            }
        
        total_records = len(self.audit_storage)
        compliance_violations = len([r for r in self.audit_storage if any('violation' in tag for tag in r.compliance_tags)])
        high_risk_events = len([r for r in self.audit_storage if r.risk_score > 0.7])
        last_audit = max(self.audit_storage, key=lambda x: x.timestamp).timestamp
        
        return {
            'total_records': total_records,
            'compliance_violations': compliance_violations,
            'high_risk_events': high_risk_events,
            'last_audit': last_audit,
            'storage_integrity': self._verify_storage_integrity()
        }
    
    def _verify_storage_integrity(self) -> bool:
        """Verify integrity of audit storage using blockchain-style hashing"""
        
        if not self.audit_storage:
            return True
        
        previous_hash = None
        
        for record in self.audit_storage:
            # Verify previous record hash link
            if record.previous_record_hash != previous_hash:
                logger.error(f"Integrity violation: {record.audit_id} has incorrect previous hash")
                return False
            
            # Verify record's own hash
            expected_hash = record._generate_data_hash()
            if record.data_hash != expected_hash:
                logger.error(f"Integrity violation: {record.audit_id} has incorrect data hash")
                return False
            
            previous_hash = record.data_hash
        
        return True
    
    def enable_auditing(self, level: AuditLevel = AuditLevel.STANDARD):
        """Enable audit trail collection"""
        self.enabled = True
        self.audit_level = level
        logger.info(f"Audit trail collection enabled at {level.value} level")
    
    def disable_auditing(self):
        """Disable audit trail collection"""
        self.enabled = False
        logger.info("Audit trail collection disabled")


# Export for module use
__all__ = ['AuditTrailCollector', 'AuditRecord', 'ComplianceValidation', 'ForensicAnalysis', 'AuditLevel']