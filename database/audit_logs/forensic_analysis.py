"""
Forensic Analysis Module

Enterprise-grade forensic analysis for IA Influencer Agent platform.
Provides deep forensic investigation capabilities for security incidents and compliance violations.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer & Digital Forensics Specialist

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the EXCLUSIVE property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Contact: mlaiel@live.de for authorization.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import logging
import hashlib
from dataclasses import dataclass, asdict
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, Float, Index, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()


class ForensicEventType(Enum):
    """Types of forensic events and investigations."""
    
    # Digital Evidence Collection
    EVIDENCE_ACQUISITION = "evidence_acquisition"
    LOG_ANALYSIS = "log_analysis"
    NETWORK_ANALYSIS = "network_analysis"
    FILE_SYSTEM_ANALYSIS = "file_system_analysis"
    MEMORY_ANALYSIS = "memory_analysis"
    DATABASE_ANALYSIS = "database_analysis"
    
    # Incident Investigation
    SECURITY_INCIDENT = "security_incident"
    DATA_BREACH_INVESTIGATION = "data_breach_investigation"
    FRAUD_INVESTIGATION = "fraud_investigation"
    INSIDER_THREAT = "insider_threat"
    MALWARE_ANALYSIS = "malware_analysis"
    
    # Content Forensics
    CONTENT_AUTHENTICITY = "content_authenticity"
    COPYRIGHT_INVESTIGATION = "copyright_investigation"
    DEEPFAKE_DETECTION = "deepfake_detection"
    METADATA_ANALYSIS = "metadata_analysis"
    STEGANOGRAPHY_DETECTION = "steganography_detection"
    
    # User Behavior Analysis
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    TIMELINE_RECONSTRUCTION = "timeline_reconstruction"
    
    # Legal and Compliance
    LEGAL_HOLD = "legal_hold"
    EDISCOVERY = "ediscovery"
    CHAIN_OF_CUSTODY = "chain_of_custody"
    EXPERT_TESTIMONY = "expert_testimony"


class ForensicStatus(Enum):
    """Status of forensic investigations."""
    
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    EVIDENCE_COLLECTED = "evidence_collected"
    ANALYSIS_COMPLETE = "analysis_complete"
    REPORT_GENERATED = "report_generated"
    PEER_REVIEWED = "peer_reviewed"
    LEGAL_APPROVED = "legal_approved"
    CLOSED = "closed"
    ARCHIVED = "archived"


class EvidenceType(Enum):
    """Types of digital evidence."""
    
    SYSTEM_LOGS = "system_logs"
    APPLICATION_LOGS = "application_logs"
    ACCESS_LOGS = "access_logs"
    NETWORK_TRAFFIC = "network_traffic"
    DATABASE_RECORDS = "database_records"
    FILE_METADATA = "file_metadata"
    USER_ACTIVITY = "user_activity"
    SECURITY_EVENTS = "security_events"
    AUDIT_TRAILS = "audit_trails"
    SCREENSHOTS = "screenshots"
    MEMORY_DUMPS = "memory_dumps"
    DISK_IMAGES = "disk_images"
    MOBILE_DATA = "mobile_data"
    CLOUD_DATA = "cloud_data"
    COMMUNICATION_DATA = "communication_data"


class ForensicPriority(Enum):
    """Priority levels for forensic investigations."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


@dataclass
class ForensicContext:
    """Context information for forensic investigations."""
    
    incident_id: str
    investigation_scope: str
    legal_authority: Optional[str]
    preservation_order: bool
    chain_of_custody_required: bool
    expert_witness_required: bool
    confidentiality_level: str
    retention_requirements: Dict[str, Any]


class ForensicAnalysisLog(Base):
    """Forensic analysis log model."""
    
    __tablename__ = "forensic_analysis_logs"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), nullable=False, unique=True, index=True)
    investigation_id = Column(String(255), index=True)  # Groups related investigations
    
    # Case details
    event_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    priority = Column(String(50), nullable=False, index=True)
    
    # Investigation details
    case_name = Column(String(255), nullable=False)
    case_description = Column(Text)
    investigation_scope = Column(Text)
    investigation_goals = Column(Text)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    
    # Incident context
    incident_id = Column(String(255), index=True)
    incident_type = Column(String(100))
    incident_severity = Column(String(50))
    affected_systems = Column(JSON)
    affected_users = Column(JSON)
    
    # Legal context
    legal_authority = Column(String(255))
    legal_case_number = Column(String(255))
    preservation_order = Column(Boolean, default=False)
    legal_hold_active = Column(Boolean, default=False)
    court_order = Column(String(255))
    
    # Investigation team
    lead_investigator = Column(String(255), nullable=False)
    investigators = Column(JSON)  # List of investigators
    legal_counsel = Column(String(255))
    expert_witnesses = Column(JSON)
    
    # Evidence management
    evidence_collected = Column(JSON)  # List of evidence items
    evidence_chain_of_custody = Column(JSON)
    evidence_integrity_hashes = Column(JSON)
    evidence_locations = Column(JSON)
    evidence_preservation_methods = Column(JSON)
    
    # Analysis results
    findings = Column(Text)
    conclusions = Column(Text)
    recommendations = Column(Text)
    risk_assessment = Column(Text)
    impact_analysis = Column(Text)
    
    # Timeline and patterns
    timeline_events = Column(JSON)
    behavioral_patterns = Column(JSON)
    anomalies_detected = Column(JSON)
    correlation_analysis = Column(JSON)
    
    # Technical analysis
    ip_addresses = Column(JSON)
    user_accounts = Column(JSON)
    file_hashes = Column(JSON)
    network_indicators = Column(JSON)
    malware_signatures = Column(JSON)
    
    # Threat intelligence
    threat_actors = Column(JSON)
    attack_vectors = Column(JSON)
    tactics_techniques = Column(JSON)  # MITRE ATT&CK
    indicators_of_compromise = Column(JSON)
    
    # Documentation
    investigation_notes = Column(Text)
    methodology = Column(Text)
    tools_used = Column(JSON)
    procedures_followed = Column(JSON)
    quality_assurance = Column(JSON)
    
    # Reporting
    report_generated = Column(Boolean, default=False)
    report_path = Column(String(500))
    executive_summary = Column(Text)
    technical_summary = Column(Text)
    peer_review_completed = Column(Boolean, default=False)
    peer_reviewers = Column(JSON)
    
    # Compliance and certification
    certification_standards = Column(JSON)  # ISO 27037, etc.
    compliance_requirements = Column(JSON)
    audit_trail = Column(JSON)
    digital_signatures = Column(JSON)
    
    # Confidentiality and access
    confidentiality_level = Column(String(50), nullable=False)
    access_restrictions = Column(JSON)
    need_to_know_basis = Column(Boolean, default=True)
    authorized_personnel = Column(JSON)
    
    # Retention and disposal
    retention_period_years = Column(Integer)
    disposal_date = Column(DateTime(timezone=True))
    disposal_method = Column(String(100))
    disposal_certificate = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_case_status', 'status'),
        Index('idx_incident_id', 'incident_id'),
        Index('idx_lead_investigator', 'lead_investigator'),
        Index('idx_priority_timestamp', 'priority', 'timestamp'),
        Index('idx_legal_hold', 'legal_hold_active'),
        Index('idx_confidentiality', 'confidentiality_level'),
    )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {
            "id": str(self.id),
            "case_id": self.case_id,
            "investigation_id": self.investigation_id,
            "event_type": self.event_type,
            "status": self.status,
            "priority": self.priority,
            "case_name": self.case_name,
            "case_description": self.case_description,
            "investigation_scope": self.investigation_scope,
            "investigation_goals": self.investigation_goals,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "incident_id": self.incident_id,
            "incident_type": self.incident_type,
            "incident_severity": self.incident_severity,
            "affected_systems": self.affected_systems,
            "legal_authority": self.legal_authority,
            "legal_case_number": self.legal_case_number,
            "preservation_order": self.preservation_order,
            "legal_hold_active": self.legal_hold_active,
            "court_order": self.court_order,
            "lead_investigator": self.lead_investigator,
            "investigators": self.investigators,
            "legal_counsel": self.legal_counsel,
            "expert_witnesses": self.expert_witnesses,
            "findings": self.findings,
            "conclusions": self.conclusions,
            "recommendations": self.recommendations,
            "risk_assessment": self.risk_assessment,
            "impact_analysis": self.impact_analysis,
            "timeline_events": self.timeline_events,
            "behavioral_patterns": self.behavioral_patterns,
            "anomalies_detected": self.anomalies_detected,
            "correlation_analysis": self.correlation_analysis,
            "threat_actors": self.threat_actors,
            "attack_vectors": self.attack_vectors,
            "tactics_techniques": self.tactics_techniques,
            "indicators_of_compromise": self.indicators_of_compromise,
            "methodology": self.methodology,
            "tools_used": self.tools_used,
            "procedures_followed": self.procedures_followed,
            "quality_assurance": self.quality_assurance,
            "report_generated": self.report_generated,
            "report_path": self.report_path,
            "executive_summary": self.executive_summary,
            "technical_summary": self.technical_summary,
            "peer_review_completed": self.peer_review_completed,
            "peer_reviewers": self.peer_reviewers,
            "certification_standards": self.certification_standards,
            "compliance_requirements": self.compliance_requirements,
            "confidentiality_level": self.confidentiality_level,
            "access_restrictions": self.access_restrictions,
            "need_to_know_basis": self.need_to_know_basis,
            "retention_period_years": self.retention_period_years,
            "disposal_date": self.disposal_date.isoformat() if self.disposal_date else None,
            "disposal_method": self.disposal_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested and user has clearance
        if include_sensitive:
            result.update({
                "affected_users": self.affected_users,
                "evidence_collected": self.evidence_collected,
                "evidence_chain_of_custody": self.evidence_chain_of_custody,
                "evidence_integrity_hashes": self.evidence_integrity_hashes,
                "evidence_locations": self.evidence_locations,
                "investigation_notes": self.investigation_notes,
                "ip_addresses": self.ip_addresses,
                "user_accounts": self.user_accounts,
                "file_hashes": self.file_hashes,
                "network_indicators": self.network_indicators,
                "malware_signatures": self.malware_signatures,
                "authorized_personnel": self.authorized_personnel,
                "audit_trail": self.audit_trail,
                "digital_signatures": self.digital_signatures
            })
        
        return result


class ForensicAnalyzer:
    """Enterprise forensic analysis system."""
    
    def __init__(self, db_session, service_name: str = "ia_influencer_agent"):
        """
        Initialize forensic analyzer.
        
        Args:
            db_session: Database session
            service_name: Name of the service
        """
        self.db_session = db_session
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    def initiate_forensic_investigation(
        self,
        case_name: str,
        event_type: ForensicEventType,
        lead_investigator: str,
        priority: ForensicPriority,
        incident_id: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[str] = None,
        goals: Optional[str] = None,
        legal_authority: Optional[str] = None,
        legal_case_number: Optional[str] = None,
        preservation_order: bool = False,
        confidentiality_level: str = "confidential",
        deadline: Optional[datetime] = None,
        affected_systems: Optional[List[str]] = None,
        affected_users: Optional[List[str]] = None,
        investigators: Optional[List[str]] = None,
        investigation_id: Optional[str] = None
    ) -> str:
        """
        Initiate a forensic investigation.
        
        Args:
            case_name: Name of the forensic case
            event_type: Type of forensic event
            lead_investigator: Lead investigator name
            priority: Investigation priority
            incident_id: Related incident ID
            description: Case description
            scope: Investigation scope
            goals: Investigation goals
            legal_authority: Legal authority (court order, etc.)
            legal_case_number: Legal case number
            preservation_order: Whether preservation order is active
            confidentiality_level: Confidentiality level
            deadline: Investigation deadline
            affected_systems: List of affected systems
            affected_users: List of affected users
            investigators: List of investigators
            investigation_id: ID for grouping related investigations
            
        Returns:
            str: Generated case ID
        """
        try:
            case_id = f"case_{uuid.uuid4().hex[:12]}"
            
            # Generate investigation ID if not provided
            if not investigation_id:
                investigation_id = f"inv_{uuid.uuid4().hex[:10]}"
            
            forensic_case = ForensicAnalysisLog(
                case_id=case_id,
                investigation_id=investigation_id,
                event_type=event_type.value,
                status=ForensicStatus.INITIATED.value,
                priority=priority.value,
                case_name=case_name,
                case_description=description,
                investigation_scope=scope,
                investigation_goals=goals,
                start_time=datetime.now(timezone.utc),
                deadline=deadline,
                incident_id=incident_id,
                legal_authority=legal_authority,
                legal_case_number=legal_case_number,
                preservation_order=preservation_order,
                legal_hold_active=preservation_order,
                lead_investigator=lead_investigator,
                investigators=investigators or [lead_investigator],
                affected_systems=affected_systems,
                affected_users=affected_users,
                confidentiality_level=confidentiality_level,
                need_to_know_basis=True,
                authorized_personnel=[lead_investigator] + (investigators or [])
            )
            
            # Set retention period based on case type and legal requirements
            if event_type in [ForensicEventType.LEGAL_HOLD, ForensicEventType.EDISCOVERY]:
                forensic_case.retention_period_years = 7  # Standard legal retention
            elif event_type in [ForensicEventType.SECURITY_INCIDENT, ForensicEventType.DATA_BREACH_INVESTIGATION]:
                forensic_case.retention_period_years = 3  # Security incident retention
            else:
                forensic_case.retention_period_years = 2  # Standard forensic retention
            
            # Initialize evidence chain of custody
            chain_of_custody = {
                "case_id": case_id,
                "initiated_by": lead_investigator,
                "initiated_at": datetime.now(timezone.utc).isoformat(),
                "custody_log": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "action": "case_initiated",
                        "person": lead_investigator,
                        "location": "digital_evidence_system",
                        "hash": hashlib.sha256(f"{case_id}_{lead_investigator}".encode()).hexdigest()
                    }
                ]
            }
            forensic_case.evidence_chain_of_custody = chain_of_custody
            
            self.db_session.add(forensic_case)
            self.db_session.commit()
            
            # Log case initiation
            log_message = f"Forensic Investigation Initiated: {case_name} ({event_type.value})"
            
            if priority == ForensicPriority.CRITICAL:
                self.logger.critical(log_message, extra={
                    "case_id": case_id,
                    "lead_investigator": lead_investigator,
                    "priority": priority.value
                })
            elif priority == ForensicPriority.HIGH:
                self.logger.error(log_message, extra={
                    "case_id": case_id,
                    "lead_investigator": lead_investigator
                })
            else:
                self.logger.info(log_message, extra={
                    "case_id": case_id,
                    "lead_investigator": lead_investigator
                })
            
            return case_id
            
        except Exception as e:
            self.logger.error(f"Failed to initiate forensic investigation: {str(e)}")
            self.db_session.rollback()
            raise
    
    def collect_evidence(
        self,
        case_id: str,
        evidence_type: EvidenceType,
        evidence_description: str,
        evidence_source: str,
        collected_by: str,
        evidence_location: str,
        evidence_size_bytes: Optional[int] = None,
        evidence_hash: Optional[str] = None,
        preservation_method: str = "digital_copy",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect and document digital evidence.
        
        Args:
            case_id: Forensic case ID
            evidence_type: Type of evidence
            evidence_description: Description of evidence
            evidence_source: Source of evidence
            collected_by: Person who collected evidence
            evidence_location: Storage location of evidence
            evidence_size_bytes: Size of evidence in bytes
            evidence_hash: Hash of evidence for integrity
            preservation_method: Method used to preserve evidence
            metadata: Additional metadata
            
        Returns:
            str: Evidence ID
        """
        try:
            case = self.db_session.query(ForensicAnalysisLog).filter_by(case_id=case_id).first()
            
            if not case:
                raise ValueError(f"Forensic case {case_id} not found")
            
            evidence_id = f"ev_{uuid.uuid4().hex[:12]}"
            
            # Create evidence record
            evidence_record = {
                "evidence_id": evidence_id,
                "type": evidence_type.value,
                "description": evidence_description,
                "source": evidence_source,
                "collected_by": collected_by,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "location": evidence_location,
                "size_bytes": evidence_size_bytes,
                "hash": evidence_hash,
                "preservation_method": preservation_method,
                "metadata": metadata or {}
            }
            
            # Add to case evidence
            if case.evidence_collected:
                case.evidence_collected.append(evidence_record)
            else:
                case.evidence_collected = [evidence_record]
            
            # Update chain of custody
            custody_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "evidence_collected",
                "evidence_id": evidence_id,
                "person": collected_by,
                "location": evidence_location,
                "hash": evidence_hash or "no_hash_provided"
            }
            
            if case.evidence_chain_of_custody:
                case.evidence_chain_of_custody["custody_log"].append(custody_entry)
            else:
                case.evidence_chain_of_custody = {"custody_log": [custody_entry]}
            
            # Update case status if first evidence
            if case.status == ForensicStatus.INITIATED.value:
                case.status = ForensicStatus.IN_PROGRESS.value
            
            self.db_session.commit()
            
            self.logger.info(f"Evidence collected for case {case_id}: {evidence_id}")
            return evidence_id
            
        except Exception as e:
            self.logger.error(f"Failed to collect evidence: {str(e)}")
            self.db_session.rollback()
            raise
    
    def analyze_timeline(
        self,
        case_id: str,
        start_time: datetime,
        end_time: datetime,
        events: List[Dict[str, Any]],
        analyst: str
    ) -> Dict[str, Any]:
        """
        Perform timeline analysis for forensic investigation.
        
        Args:
            case_id: Forensic case ID
            start_time: Timeline start time
            end_time: Timeline end time
            events: List of events for timeline
            analyst: Analyst performing the analysis
            
        Returns:
            Dict[str, Any]: Timeline analysis results
        """
        try:
            case = self.db_session.query(ForensicAnalysisLog).filter_by(case_id=case_id).first()
            
            if not case:
                raise ValueError(f"Forensic case {case_id} not found")
            
            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
            
            # Analyze patterns and anomalies
            patterns = self._analyze_patterns(sorted_events)
            anomalies = self._detect_anomalies(sorted_events)
            correlations = self._find_correlations(sorted_events)
            
            timeline_analysis = {
                "analysis_id": f"ta_{uuid.uuid4().hex[:12]}",
                "case_id": case_id,
                "analyst": analyst,
                "analysis_time": datetime.now(timezone.utc).isoformat(),
                "timeline_start": start_time.isoformat(),
                "timeline_end": end_time.isoformat(),
                "total_events": len(sorted_events),
                "events": sorted_events,
                "patterns": patterns,
                "anomalies": anomalies,
                "correlations": correlations
            }
            
            # Update case with timeline analysis
            case.timeline_events = sorted_events
            case.behavioral_patterns = patterns
            case.anomalies_detected = anomalies
            case.correlation_analysis = correlations
            
            # Update case status
            if case.status == ForensicStatus.IN_PROGRESS.value:
                case.status = ForensicStatus.EVIDENCE_COLLECTED.value
            
            self.db_session.commit()
            
            self.logger.info(f"Timeline analysis completed for case {case_id}")
            return timeline_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze timeline: {str(e)}")
            raise
    
    def _analyze_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in timeline events."""
        patterns = {
            "frequency_analysis": {},
            "temporal_patterns": {},
            "behavioral_patterns": {}
        }
        
        # Frequency analysis
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        patterns["frequency_analysis"] = event_types
        
        # Temporal patterns (hourly distribution)
        hourly_distribution = {}
        for event in events:
            try:
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                hour = timestamp.hour
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            except:
                continue
        
        patterns["temporal_patterns"]["hourly_distribution"] = hourly_distribution
        
        return patterns
    
    def _detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in timeline events."""
        anomalies = []
        
        # Detect time gaps (>1 hour between events)
        for i in range(1, len(events)):
            try:
                prev_time = datetime.fromisoformat(events[i-1].get('timestamp', ''))
                curr_time = datetime.fromisoformat(events[i].get('timestamp', ''))
                gap = curr_time - prev_time
                
                if gap.total_seconds() > 3600:  # 1 hour gap
                    anomalies.append({
                        "type": "time_gap",
                        "description": f"Time gap of {gap.total_seconds()/3600:.1f} hours",
                        "start_event": events[i-1],
                        "end_event": events[i]
                    })
            except:
                continue
        
        # Detect burst activity (>10 events in 1 minute)
        burst_threshold = 10
        time_window = 60  # seconds
        
        for i in range(len(events)):
            try:
                base_time = datetime.fromisoformat(events[i].get('timestamp', ''))
                count = 1
                
                for j in range(i+1, len(events)):
                    event_time = datetime.fromisoformat(events[j].get('timestamp', ''))
                    if (event_time - base_time).total_seconds() <= time_window:
                        count += 1
                    else:
                        break
                
                if count > burst_threshold:
                    anomalies.append({
                        "type": "burst_activity",
                        "description": f"Burst of {count} events in {time_window} seconds",
                        "start_time": base_time.isoformat(),
                        "event_count": count
                    })
            except:
                continue
        
        return anomalies
    
    def _find_correlations(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find correlations between events."""
        correlations = {
            "user_correlations": {},
            "system_correlations": {},
            "temporal_correlations": {}
        }
        
        # User correlations
        user_events = {}
        for event in events:
            user_id = event.get('user_id')
            if user_id:
                if user_id not in user_events:
                    user_events[user_id] = []
                user_events[user_id].append(event)
        
        correlations["user_correlations"] = {
            user_id: len(events) for user_id, events in user_events.items()
        }
        
        # System correlations
        system_events = {}
        for event in events:
            system = event.get('system', event.get('source'))
            if system:
                if system not in system_events:
                    system_events[system] = []
                system_events[system].append(event)
        
        correlations["system_correlations"] = {
            system: len(events) for system, events in system_events.items()
        }
        
        return correlations
    
    def complete_analysis(
        self,
        case_id: str,
        analyst: str,
        findings: str,
        conclusions: str,
        recommendations: str,
        risk_assessment: Optional[str] = None,
        impact_analysis: Optional[str] = None
    ) -> bool:
        """
        Complete forensic analysis and generate findings.
        
        Args:
            case_id: Forensic case ID
            analyst: Analyst completing the analysis
            findings: Investigation findings
            conclusions: Analysis conclusions
            recommendations: Recommendations
            risk_assessment: Risk assessment
            impact_analysis: Impact analysis
            
        Returns:
            bool: True if successfully completed
        """
        try:
            case = self.db_session.query(ForensicAnalysisLog).filter_by(case_id=case_id).first()
            
            if not case:
                raise ValueError(f"Forensic case {case_id} not found")
            
            # Update case with analysis results
            case.findings = findings
            case.conclusions = conclusions
            case.recommendations = recommendations
            case.risk_assessment = risk_assessment
            case.impact_analysis = impact_analysis
            case.status = ForensicStatus.ANALYSIS_COMPLETE.value
            
            # Add to audit trail
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "analysis_completed",
                "analyst": analyst,
                "findings_hash": hashlib.sha256(findings.encode()).hexdigest()[:16]
            }
            
            if case.audit_trail:
                case.audit_trail.append(audit_entry)
            else:
                case.audit_trail = [audit_entry]
            
            self.db_session.commit()
            
            self.logger.info(f"Forensic analysis completed for case {case_id} by {analyst}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete analysis: {str(e)}")
            self.db_session.rollback()
            return False
    
    def generate_forensic_report(
        self,
        case_id: str,
        report_type: str = "comprehensive",
        include_technical_details: bool = True,
        include_executive_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Generate forensic investigation report.
        
        Args:
            case_id: Forensic case ID
            report_type: Type of report (comprehensive, summary, technical)
            include_technical_details: Include technical analysis
            include_executive_summary: Include executive summary
            
        Returns:
            Dict[str, Any]: Forensic report
        """
        try:
            case = self.db_session.query(ForensicAnalysisLog).filter_by(case_id=case_id).first()
            
            if not case:
                raise ValueError(f"Forensic case {case_id} not found")
            
            report = {
                "report_id": f"rep_{uuid.uuid4().hex[:12]}",
                "case_id": case_id,
                "report_type": report_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "case_information": {
                    "case_name": case.case_name,
                    "investigation_id": case.investigation_id,
                    "incident_id": case.incident_id,
                    "priority": case.priority,
                    "status": case.status,
                    "lead_investigator": case.lead_investigator,
                    "start_time": case.start_time.isoformat() if case.start_time else None,
                    "end_time": case.end_time.isoformat() if case.end_time else None
                }
            }
            
            if include_executive_summary:
                report["executive_summary"] = {
                    "case_overview": case.case_description,
                    "key_findings": case.findings,
                    "conclusions": case.conclusions,
                    "recommendations": case.recommendations,
                    "risk_assessment": case.risk_assessment,
                    "impact_analysis": case.impact_analysis
                }
            
            if include_technical_details:
                report["technical_analysis"] = {
                    "methodology": case.methodology,
                    "tools_used": case.tools_used,
                    "evidence_collected": case.evidence_collected,
                    "timeline_analysis": case.timeline_events,
                    "patterns_identified": case.behavioral_patterns,
                    "anomalies_detected": case.anomalies_detected,
                    "correlation_analysis": case.correlation_analysis,
                    "threat_indicators": case.indicators_of_compromise
                }
            
            # Legal and compliance information
            report["legal_information"] = {
                "legal_authority": case.legal_authority,
                "legal_case_number": case.legal_case_number,
                "preservation_order": case.preservation_order,
                "chain_of_custody": case.evidence_chain_of_custody,
                "confidentiality_level": case.confidentiality_level
            }
            
            # Quality assurance
            report["quality_assurance"] = {
                "peer_review_completed": case.peer_review_completed,
                "peer_reviewers": case.peer_reviewers,
                "certification_standards": case.certification_standards,
                "procedures_followed": case.procedures_followed
            }
            
            # Update case with report information
            case.report_generated = True
            case.status = ForensicStatus.REPORT_GENERATED.value
            
            self.db_session.commit()
            
            self.logger.info(f"Forensic report generated for case {case_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate forensic report: {str(e)}")
            raise
    
    def get_active_investigations(
        self,
        investigator: Optional[str] = None,
        priority: Optional[ForensicPriority] = None,
        status: Optional[ForensicStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active forensic investigations.
        
        Args:
            investigator: Filter by investigator
            priority: Filter by priority
            status: Filter by status
            
        Returns:
            List[Dict[str, Any]]: List of active investigations
        """
        try:
            query = self.db_session.query(ForensicAnalysisLog)
            
            if investigator:
                query = query.filter(ForensicAnalysisLog.lead_investigator == investigator)
            
            if priority:
                query = query.filter(ForensicAnalysisLog.priority == priority.value)
            
            if status:
                query = query.filter(ForensicAnalysisLog.status == status.value)
            else:
                # Default to active statuses
                active_statuses = [
                    ForensicStatus.INITIATED.value,
                    ForensicStatus.IN_PROGRESS.value,
                    ForensicStatus.EVIDENCE_COLLECTED.value,
                    ForensicStatus.ANALYSIS_COMPLETE.value
                ]
                query = query.filter(ForensicAnalysisLog.status.in_(active_statuses))
            
            investigations = query.order_by(ForensicAnalysisLog.timestamp.desc()).all()
            
            return [inv.to_dict() for inv in investigations]
            
        except Exception as e:
            self.logger.error(f"Failed to get active investigations: {str(e)}")
            return []


def create_forensic_analyzer(db_session, service_name: str = "ia_influencer_agent") -> ForensicAnalyzer:
    """
    Factory function to create forensic analyzer.
    
    Args:
        db_session: Database session
        service_name: Name of the service
        
    Returns:
        ForensicAnalyzer: Configured forensic analyzer
    """
    return ForensicAnalyzer(db_session, service_name)


# Export main classes and functions
__all__ = [
    "ForensicAnalysisLog",
    "ForensicAnalyzer",
    "ForensicEventType",
    "ForensicStatus",
    "EvidenceType",
    "ForensicPriority",
    "ForensicContext",
    "create_forensic_analyzer"
]
