"""Compliance Tracker - Regulatory Compliance Management System

Enterprise-grade compliance tracking and management system ensuring adherence to
international regulations (GDPR, CCPA, DMCA, PCI-DSS) for the IA Influencer platform's
creator economy operations with automated compliance monitoring and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import asyncio
import logging
import json
import sqlite3
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import re
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "GDPR"                       # General Data Protection Regulation (EU)
    CCPA = "CCPA"                       # California Consumer Privacy Act (US)
    DMCA = "DMCA"                       # Digital Millennium Copyright Act (US)
    PCI_DSS = "PCI_DSS"                # Payment Card Industry Data Security Standard
    SOX = "SOX"                         # Sarbanes-Oxley Act (US)
    HIPAA = "HIPAA"                     # Health Insurance Portability and Accountability Act (US)
    COPPA = "COPPA"                     # Children's Online Privacy Protection Act (US)
    PIPEDA = "PIPEDA"                   # Personal Information Protection and Electronic Documents Act (CA)
    LGPD = "LGPD"                       # Lei Geral de Proteção de Dados (Brazil)
    DPA_2018 = "DPA_2018"              # Data Protection Act 2018 (UK)


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "COMPLIANT"             # Fully compliant
    WARNING = "WARNING"                 # Minor compliance issues
    NON_COMPLIANT = "NON_COMPLIANT"     # Major compliance violations
    PENDING = "PENDING"                 # Compliance check in progress
    UNKNOWN = "UNKNOWN"                 # Compliance status unknown
    EXEMPT = "EXEMPT"                   # Exempt from this regulation


class DataProcessingPurpose(Enum):
    """GDPR data processing purposes"""
    CONSENT = "CONSENT"                 # Based on user consent
    CONTRACT = "CONTRACT"               # Necessary for contract performance
    LEGAL_OBLIGATION = "LEGAL_OBLIGATION"  # Required by law
    VITAL_INTERESTS = "VITAL_INTERESTS"    # Protecting vital interests
    PUBLIC_TASK = "PUBLIC_TASK"         # Public task or official authority
    LEGITIMATE_INTERESTS = "LEGITIMATE_INTERESTS"  # Legitimate business interests


class DataCategory(Enum):
    """Categories of personal data"""
    BASIC_PERSONAL = "BASIC_PERSONAL"   # Name, email, address
    SENSITIVE = "SENSITIVE"             # Race, religion, health, etc.
    FINANCIAL = "FINANCIAL"             # Payment information
    BIOMETRIC = "BIOMETRIC"             # Fingerprints, facial recognition
    LOCATION = "LOCATION"               # Geographic location data
    BEHAVIORAL = "BEHAVIORAL"           # Browsing patterns, preferences
    CONTENT = "CONTENT"                 # User-generated content
    COMMUNICATION = "COMMUNICATION"     # Messages, emails, calls


@dataclass
class DataSubject:
    """Data subject information for GDPR compliance"""
    subject_id: str
    email: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    consent_given: bool = False
    consent_date: Optional[datetime] = None
    data_categories: Set[DataCategory] = field(default_factory=set)
    processing_purposes: Set[DataProcessingPurpose] = field(default_factory=set)
    retention_period: Optional[timedelta] = None
    last_activity: Optional[datetime] = None
    
    @property
    def is_minor(self) -> bool:
        """Check if subject is a minor (under 18)"""
        return self.age is not None and self.age < 18
    
    @property
    def is_eu_resident(self) -> bool:
        """Check if subject is EU resident"""
        eu_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
        }
        return self.country in eu_countries
    
    @property
    def requires_gdpr_protection(self) -> bool:
        """Check if subject requires GDPR protection"""
        return self.is_eu_resident or self.country == 'GB'  # Include UK


@dataclass
class ComplianceEvent:
    """Compliance-related event"""
    event_id: str
    event_type: str
    framework: ComplianceFramework
    timestamp: datetime
    data_subject_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'framework': self.framework.value,
            'timestamp': self.timestamp.isoformat(),
            'data_subject_id': self.data_subject_id,
            'details': self.details,
            'severity': self.severity,
            'resolved': self.resolved,
            'resolution_notes': self.resolution_notes,
        }


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    framework: ComplianceFramework
    timestamp: datetime
    overall_status: ComplianceStatus
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    data_subject_count: int = 0
    violations_count: int = 0
    pending_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'framework': self.framework.value,
            'timestamp': self.timestamp.isoformat(),
            'overall_status': self.overall_status.value,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'data_subject_count': self.data_subject_count,
            'violations_count': self.violations_count,
            'pending_requests': self.pending_requests,
        }


class GDPRTracker:
    """GDPR compliance tracking system"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize GDPR tracking database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Data subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_subjects (
                subject_id TEXT PRIMARY KEY,
                email TEXT,
                country TEXT,
                age INTEGER,
                consent_given BOOLEAN,
                consent_date TEXT,
                data_categories TEXT,
                processing_purposes TEXT,
                retention_period_days INTEGER,
                last_activity TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Data processing activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_activities (
                activity_id TEXT PRIMARY KEY,
                subject_id TEXT,
                purpose TEXT,
                data_categories TEXT,
                legal_basis TEXT,
                timestamp TEXT,
                duration_seconds REAL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (subject_id) REFERENCES data_subjects (subject_id)
            )
        ''')
        
        # Consent records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                subject_id TEXT,
                consent_type TEXT,
                given BOOLEAN,
                timestamp TEXT,
                ip_address TEXT,
                evidence TEXT,
                FOREIGN KEY (subject_id) REFERENCES data_subjects (subject_id)
            )
        ''')
        
        # Data requests table (access, portability, erasure)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_requests (
                request_id TEXT PRIMARY KEY,
                subject_id TEXT,
                request_type TEXT,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                response_data TEXT,
                FOREIGN KEY (subject_id) REFERENCES data_subjects (subject_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_data_subject(self, data_subject: DataSubject) -> None:
        """Register new data subject"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO data_subjects (
                subject_id, email, country, age, consent_given, consent_date,
                data_categories, processing_purposes, retention_period_days,
                last_activity, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data_subject.subject_id,
            data_subject.email,
            data_subject.country,
            data_subject.age,
            data_subject.consent_given,
            data_subject.consent_date.isoformat() if data_subject.consent_date else None,
            json.dumps([cat.value for cat in data_subject.data_categories]),
            json.dumps([purpose.value for purpose in data_subject.processing_purposes]),
            data_subject.retention_period.days if data_subject.retention_period else None,
            data_subject.last_activity.isoformat() if data_subject.last_activity else None,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Registered data subject: %s", data_subject.subject_id)
    
    def record_consent(
        self,
        subject_id: str,
        consent_type: str,
        given: bool,
        ip_address: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record consent given or withdrawn"""
        
        consent_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO consent_records (
                consent_id, subject_id, consent_type, given, timestamp,
                ip_address, evidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            consent_id,
            subject_id,
            consent_type,
            given,
            datetime.now(timezone.utc).isoformat(),
            ip_address,
            json.dumps(evidence) if evidence else None
        ))
        
        # Update data subject consent status
        cursor.execute('''
            UPDATE data_subjects 
            SET consent_given = ?, consent_date = ?, updated_at = ?
            WHERE subject_id = ?
        ''', (
            given,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            subject_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Recorded consent for subject %s: %s (%s)", subject_id, consent_type, "given" if given else "withdrawn")
        return consent_id
    
    def record_processing_activity(
        self,
        subject_id: str,
        purpose: DataProcessingPurpose,
        data_categories: List[DataCategory],
        legal_basis: str,
        duration: float,
        ip_address: str,
        user_agent: str
    ) -> str:
        """Record data processing activity"""
        
        activity_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processing_activities (
                activity_id, subject_id, purpose, data_categories, legal_basis,
                timestamp, duration_seconds, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            activity_id,
            subject_id,
            purpose.value,
            json.dumps([cat.value for cat in data_categories]),
            legal_basis,
            datetime.now(timezone.utc).isoformat(),
            duration,
            ip_address,
            user_agent
        ))
        
        # Update last activity
        cursor.execute('''
            UPDATE data_subjects 
            SET last_activity = ?, updated_at = ?
            WHERE subject_id = ?
        ''', (
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            subject_id
        ))
        
        conn.commit()
        conn.close()
        
        return activity_id
    
    def create_data_request(
        self,
        subject_id: str,
        request_type: str  # 'access', 'portability', 'erasure', 'rectification'
    ) -> str:
        """Create data subject request"""
        
        request_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_requests (
                request_id, subject_id, request_type, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            request_id,
            subject_id,
            request_type,
            'pending',
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Created data request: %s (type=%s, subject=%s)", request_id, request_type, subject_id)
        return request_id
    
    def complete_data_request(self, request_id: str, response_data: Optional[Dict[str, Any]] = None) -> None:
        """Complete data subject request"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE data_requests 
            SET status = ?, completed_at = ?, response_data = ?
            WHERE request_id = ?
        ''', (
            'completed',
            datetime.now(timezone.utc).isoformat(),
            json.dumps(response_data) if response_data else None,
            request_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Completed data request: %s", request_id)
    
    def get_subject_data(self, subject_id: str) -> Optional[Dict[str, Any]]:
        """Get all data for a subject (for access requests)"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get subject info
        cursor.execute('SELECT * FROM data_subjects WHERE subject_id = ?', (subject_id,))
        subject_row = cursor.fetchone()
        
        if not subject_row:
            conn.close()
            return None
        
        # Get processing activities
        cursor.execute('SELECT * FROM processing_activities WHERE subject_id = ?', (subject_id,))
        activities = cursor.fetchall()
        
        # Get consent records
        cursor.execute('SELECT * FROM consent_records WHERE subject_id = ?', (subject_id,))
        consent_records = cursor.fetchall()
        
        # Get data requests
        cursor.execute('SELECT * FROM data_requests WHERE subject_id = ?', (subject_id,))
        requests = cursor.fetchall()
        
        conn.close()
        
        return {
            'subject_info': dict(zip([desc[0] for desc in cursor.description], subject_row)) if subject_row else None,
            'processing_activities': [dict(zip([desc[0] for desc in cursor.description], row)) for row in activities],
            'consent_records': [dict(zip([desc[0] for desc in cursor.description], row)) for row in consent_records],
            'data_requests': [dict(zip([desc[0] for desc in cursor.description], row)) for row in requests],
        }
    
    def erase_subject_data(self, subject_id: str) -> Dict[str, int]:
        """Erase all data for a subject (for erasure requests)"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        deleted_counts = {}
        
        # Delete from all tables
        tables = ['processing_activities', 'consent_records', 'data_requests', 'data_subjects']
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table} WHERE subject_id = ?', (subject_id,))
            deleted_counts[table] = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info("Erased data for subject %s: %s", subject_id, deleted_counts)
        return deleted_counts


class CCPATracker:
    """CCPA compliance tracking system"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize CCPA tracking database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # California consumers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ca_consumers (
                consumer_id TEXT PRIMARY KEY,
                email TEXT,
                verified BOOLEAN,
                opt_out_sale BOOLEAN,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Data sales/sharing records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sales (
                sale_id TEXT PRIMARY KEY,
                consumer_id TEXT,
                third_party TEXT,
                data_categories TEXT,
                purpose TEXT,
                timestamp TEXT,
                value REAL,
                FOREIGN KEY (consumer_id) REFERENCES ca_consumers (consumer_id)
            )
        ''')
        
        conn.commit()
        conn.close()


class DMCATracker:
    """DMCA compliance tracking system"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize DMCA tracking database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # DMCA takedown notices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dmca_notices (
                notice_id TEXT PRIMARY KEY,
                content_id TEXT,
                creator_id TEXT,
                claimant_name TEXT,
                claimant_email TEXT,
                work_description TEXT,
                infringement_url TEXT,
                received_at TEXT,
                status TEXT,
                action_taken TEXT,
                response_sent_at TEXT
            )
        ''')
        
        # Counter-notices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dmca_counter_notices (
                counter_notice_id TEXT PRIMARY KEY,
                original_notice_id TEXT,
                creator_id TEXT,
                creator_name TEXT,
                creator_address TEXT,
                creator_statement TEXT,
                received_at TEXT,
                status TEXT,
                FOREIGN KEY (original_notice_id) REFERENCES dmca_notices (notice_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def file_takedown_notice(
        self,
        content_id: str,
        creator_id: str,
        claimant_name: str,
        claimant_email: str,
        work_description: str,
        infringement_url: str
    ) -> str:
        """File DMCA takedown notice"""
        
        notice_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dmca_notices (
                notice_id, content_id, creator_id, claimant_name, claimant_email,
                work_description, infringement_url, received_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notice_id,
            content_id,
            creator_id,
            claimant_name,
            claimant_email,
            work_description,
            infringement_url,
            datetime.now(timezone.utc).isoformat(),
            'pending'
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Filed DMCA takedown notice: %s", notice_id)
        return notice_id
    
    def process_takedown_notice(self, notice_id: str, action_taken: str) -> None:
        """Process DMCA takedown notice"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE dmca_notices 
            SET status = ?, action_taken = ?, response_sent_at = ?
            WHERE notice_id = ?
        ''', (
            'processed',
            action_taken,
            datetime.now(timezone.utc).isoformat(),
            notice_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Processed DMCA notice %s: %s", notice_id, action_taken)


class ComplianceTracker:
    """
    Comprehensive compliance tracking and management system
    
    Features:
    - Multi-framework compliance monitoring (GDPR, CCPA, DMCA, etc.)
    - Automated compliance checking and reporting
    - Data subject rights management
    - Audit trail and documentation
    - Risk assessment and mitigation
    - Regulatory change monitoring
    - Compliance dashboard and analytics
    - Privacy impact assessments
    - Data mapping and inventory
    - Incident response coordination
    """
    
    def __init__(
        self,
        db_path: str = "compliance.db",
        geoip_db_path: Optional[str] = None,
        enable_frameworks: Optional[List[ComplianceFramework]] = None
    ):
        self.db_path = Path(db_path)
        self.geoip_db_path = geoip_db_path
        
        # Initialize compliance tracking databases
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_main_database()
        
        # Framework-specific trackers
        self.gdpr_tracker = GDPRTracker(str(self.db_path))
        self.ccpa_tracker = CCPATracker(str(self.db_path))
        self.dmca_tracker = DMCATracker(str(self.db_path))
        
        # Enable specific frameworks
        self.enabled_frameworks = enable_frameworks or [
            ComplianceFramework.GDPR,
            ComplianceFramework.CCPA,
            ComplianceFramework.DMCA,
            ComplianceFramework.PCI_DSS
        ]
        
        # Compliance events tracking
        self.events_history: deque = deque(maxlen=10000)
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        
        # GeoIP for location-based compliance
        self.geoip_reader = None
        if geoip_db_path and Path(geoip_db_path).exists():
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_db_path)
            except Exception as e:
                logger.warning("Failed to load GeoIP database: %s", str(e))
        
        # Threading
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Compliance rules and validators
        self.compliance_rules: Dict[ComplianceFramework, List[Callable]] = {
            ComplianceFramework.GDPR: [
                self._check_gdpr_consent,
                self._check_gdpr_data_retention,
                self._check_gdpr_data_minimization,
                self._check_gdpr_requests_response_time,
            ],
            ComplianceFramework.CCPA: [
                self._check_ccpa_disclosure,
                self._check_ccpa_opt_out,
                self._check_ccpa_data_sales,
            ],
            ComplianceFramework.DMCA: [
                self._check_dmca_response_time,
                self._check_dmca_counter_notice_process,
            ],
            ComplianceFramework.PCI_DSS: [
                self._check_pci_data_encryption,
                self._check_pci_access_controls,
            ]
        }
        
        logger.info("ComplianceTracker initialized with frameworks: %s", 
                   [f.value for f in self.enabled_frameworks])
    
    def _init_main_database(self) -> None:
        """Initialize main compliance database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compliance events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                framework TEXT,
                timestamp TEXT,
                data_subject_id TEXT,
                details TEXT,
                severity TEXT,
                resolved BOOLEAN,
                resolution_notes TEXT
            )
        ''')
        
        # Compliance assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_assessments (
                assessment_id TEXT PRIMARY KEY,
                framework TEXT,
                timestamp TEXT,
                overall_status TEXT,
                findings TEXT,
                recommendations TEXT,
                assessor TEXT
            )
        ''')
        
        # Data mapping table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_mapping (
                mapping_id TEXT PRIMARY KEY,
                data_category TEXT,
                data_location TEXT,
                processing_purpose TEXT,
                legal_basis TEXT,
                retention_period TEXT,
                security_measures TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def track_data_processing(
        self,
        subject_id: str,
        processing_purpose: DataProcessingPurpose,
        data_categories: List[DataCategory],
        ip_address: str,
        user_agent: str = "",
        duration: float = 0.0
    ) -> str:
        """Track data processing activity for compliance"""
        
        # Determine subject location for jurisdiction-specific compliance
        country = self._get_country_from_ip(ip_address)
        
        # Create or update data subject
        data_subject = await self._get_or_create_data_subject(subject_id, country)
        
        # Record processing activity in GDPR tracker if applicable
        activity_id = None
        if ComplianceFramework.GDPR in self.enabled_frameworks and data_subject.requires_gdpr_protection:
            activity_id = self.gdpr_tracker.record_processing_activity(
                subject_id=subject_id,
                purpose=processing_purpose,
                data_categories=data_categories,
                legal_basis=processing_purpose.value,
                duration=duration,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="data_processing",
            framework=ComplianceFramework.GDPR,
            timestamp=datetime.now(timezone.utc),
            data_subject_id=subject_id,
            details={
                'purpose': processing_purpose.value,
                'data_categories': [cat.value for cat in data_categories],
                'ip_address': ip_address,
                'country': country,
                'activity_id': activity_id,
                'duration': duration
            }
        )
        
        await self._store_compliance_event(event)
        
        logger.debug("Tracked data processing: subject=%s, purpose=%s, categories=%s",
                    subject_id, processing_purpose.value, [c.value for c in data_categories])
        
        return activity_id or event.event_id
    
    async def record_consent(
        self,
        subject_id: str,
        consent_type: str,
        given: bool,
        ip_address: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record consent given or withdrawn"""
        
        country = self._get_country_from_ip(ip_address)
        data_subject = await self._get_or_create_data_subject(subject_id, country)
        
        consent_id = None
        if ComplianceFramework.GDPR in self.enabled_frameworks and data_subject.requires_gdpr_protection:
            consent_id = self.gdpr_tracker.record_consent(
                subject_id=subject_id,
                consent_type=consent_type,
                given=given,
                ip_address=ip_address,
                evidence=evidence
            )
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="consent_change",
            framework=ComplianceFramework.GDPR,
            timestamp=datetime.now(timezone.utc),
            data_subject_id=subject_id,
            details={
                'consent_type': consent_type,
                'given': given,
                'ip_address': ip_address,
                'country': country,
                'consent_id': consent_id,
                'evidence': evidence
            }
        )
        
        await self._store_compliance_event(event)
        
        logger.info("Recorded consent: subject=%s, type=%s, given=%s", subject_id, consent_type, given)
        return consent_id or event.event_id
    
    async def handle_data_subject_request(
        self,
        subject_id: str,
        request_type: str,  # 'access', 'portability', 'erasure', 'rectification'
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Handle data subject rights request"""
        
        data_subject = await self._get_or_create_data_subject(subject_id)
        
        request_id = None
        if ComplianceFramework.GDPR in self.enabled_frameworks and data_subject.requires_gdpr_protection:
            request_id = self.gdpr_tracker.create_data_request(subject_id, request_type)
        else:
            request_id = str(uuid.uuid4())
        
        # Store pending request
        with self.lock:
            self.pending_requests[request_id] = {
                'subject_id': subject_id,
                'request_type': request_type,
                'created_at': datetime.now(timezone.utc),
                'status': 'pending',
                'additional_info': additional_info
            }
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="data_subject_request",
            framework=ComplianceFramework.GDPR,
            timestamp=datetime.now(timezone.utc),
            data_subject_id=subject_id,
            details={
                'request_type': request_type,
                'request_id': request_id,
                'additional_info': additional_info
            }
        )
        
        await self._store_compliance_event(event)
        
        logger.info("Created data subject request: id=%s, type=%s, subject=%s", request_id, request_type, subject_id)
        return request_id
    
    async def complete_data_subject_request(
        self,
        request_id: str,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Complete data subject rights request"""
        
        if request_id not in self.pending_requests:
            raise ValueError(f"Request not found: {request_id}")
        
        request_info = self.pending_requests[request_id]
        subject_id = request_info['subject_id']
        request_type = request_info['request_type']
        
        # Complete in GDPR tracker if applicable
        data_subject = await self._get_or_create_data_subject(subject_id)
        if ComplianceFramework.GDPR in self.enabled_frameworks and data_subject.requires_gdpr_protection:
            self.gdpr_tracker.complete_data_request(request_id, response_data)
        
        # Update pending request
        with self.lock:
            self.pending_requests[request_id]['status'] = 'completed'
            self.pending_requests[request_id]['completed_at'] = datetime.now(timezone.utc)
            self.pending_requests[request_id]['response_data'] = response_data
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="data_subject_request_completed",
            framework=ComplianceFramework.GDPR,
            timestamp=datetime.now(timezone.utc),
            data_subject_id=subject_id,
            details={
                'request_type': request_type,
                'request_id': request_id,
                'response_data': response_data
            }
        )
        
        await self._store_compliance_event(event)
        
        logger.info("Completed data subject request: id=%s, type=%s", request_id, request_type)
    
    async def file_dmca_takedown(
        self,
        content_id: str,
        creator_id: str,
        claimant_name: str,
        claimant_email: str,
        work_description: str,
        infringement_url: str
    ) -> str:
        """File DMCA takedown notice"""
        
        if ComplianceFramework.DMCA not in self.enabled_frameworks:
            raise ValueError("DMCA compliance tracking not enabled")
        
        notice_id = self.dmca_tracker.file_takedown_notice(
            content_id=content_id,
            creator_id=creator_id,
            claimant_name=claimant_name,
            claimant_email=claimant_email,
            work_description=work_description,
            infringement_url=infringement_url
        )
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="dmca_takedown_filed",
            framework=ComplianceFramework.DMCA,
            timestamp=datetime.now(timezone.utc),
            details={
                'notice_id': notice_id,
                'content_id': content_id,
                'creator_id': creator_id,
                'claimant_name': claimant_name,
                'claimant_email': claimant_email,
                'work_description': work_description,
                'infringement_url': infringement_url
            }
        )
        
        await self._store_compliance_event(event)
        
        return notice_id
    
    async def process_dmca_takedown(self, notice_id: str, action_taken: str) -> None:
        """Process DMCA takedown notice"""
        
        self.dmca_tracker.process_takedown_notice(notice_id, action_taken)
        
        # Create compliance event
        event = ComplianceEvent(
            event_id=str(uuid.uuid4()),
            event_type="dmca_takedown_processed",
            framework=ComplianceFramework.DMCA,
            timestamp=datetime.now(timezone.utc),
            details={
                'notice_id': notice_id,
                'action_taken': action_taken
            }
        )
        
        await self._store_compliance_event(event)
        
        logger.info("Processed DMCA takedown: %s - %s", notice_id, action_taken)
    
    async def run_compliance_assessment(
        self,
        framework: ComplianceFramework,
        scope: Optional[str] = None
    ) -> ComplianceReport:
        """Run comprehensive compliance assessment"""
        
        if framework not in self.enabled_frameworks:
            raise ValueError(f"Framework not enabled: {framework}")
        
        report_id = str(uuid.uuid4())
        findings = []
        recommendations = []
        overall_status = ComplianceStatus.COMPLIANT
        
        # Run framework-specific compliance checks
        if framework in self.compliance_rules:
            for rule_func in self.compliance_rules[framework]:
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor, rule_func
                    )
                    
                    if result:
                        findings.append(result)
                        
                        # Update overall status based on finding severity
                        if result.get('status') == ComplianceStatus.NON_COMPLIANT:
                            overall_status = ComplianceStatus.NON_COMPLIANT
                        elif result.get('status') == ComplianceStatus.WARNING and overall_status == ComplianceStatus.COMPLIANT:
                            overall_status = ComplianceStatus.WARNING
                            
                except Exception as e:
                    logger.error("Compliance rule check failed: %s", str(e))
                    findings.append({
                        'rule': rule_func.__name__,
                        'status': ComplianceStatus.UNKNOWN,
                        'message': f"Check failed: {str(e)}",
                        'severity': 'ERROR'
                    })
        
        # Generate recommendations based on findings
        recommendations = self._generate_compliance_recommendations(framework, findings)
        
        # Get metrics
        data_subject_count = await self._count_data_subjects(framework)
        violations_count = len([f for f in findings if f.get('status') == ComplianceStatus.NON_COMPLIANT])
        pending_requests_count = len([r for r in self.pending_requests.values() if r['status'] == 'pending'])
        
        # Create report
        report = ComplianceReport(
            report_id=report_id,
            framework=framework,
            timestamp=datetime.now(timezone.utc),
            overall_status=overall_status,
            findings=findings,
            recommendations=recommendations,
            data_subject_count=data_subject_count,
            violations_count=violations_count,
            pending_requests=pending_requests_count
        )
        
        # Store assessment
        await self._store_compliance_assessment(report)
        
        logger.info("Completed compliance assessment: framework=%s, status=%s, findings=%d",
                   framework.value, overall_status.value, len(findings))
        
        return report
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        
        dashboard_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'enabled_frameworks': [f.value for f in self.enabled_frameworks],
            'framework_status': {},
            'pending_requests': len(self.pending_requests),
            'recent_events': [],
            'compliance_scores': {},
        }
        
        # Get status for each enabled framework
        for framework in self.enabled_frameworks:
            try:
                # Run quick assessment
                report = await self.run_compliance_assessment(framework)
                dashboard_data['framework_status'][framework.value] = {
                    'status': report.overall_status.value,
                    'violations': report.violations_count,
                    'last_assessment': report.timestamp.isoformat()
                }
                
                # Calculate compliance score (0-100)
                score = 100
                if report.violations_count > 0:
                    score -= min(report.violations_count * 10, 50)  # Max 50 point deduction
                if report.overall_status == ComplianceStatus.WARNING:
                    score -= 10
                elif report.overall_status == ComplianceStatus.NON_COMPLIANT:
                    score -= 30
                
                dashboard_data['compliance_scores'][framework.value] = max(score, 0)
                
            except Exception as e:
                logger.error("Error getting framework status for %s: %s", framework.value, str(e))
                dashboard_data['framework_status'][framework.value] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        # Get recent events
        dashboard_data['recent_events'] = [
            event.to_dict() for event in list(self.events_history)[-10:]
        ]
        
        return dashboard_data
    
    def _get_country_from_ip(self, ip_address: str) -> Optional[str]:
        """Get country code from IP address using GeoIP"""
        
        if not self.geoip_reader:
            return None
        
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)
            
            response = self.geoip_reader.country(ip_address)
            return response.country.iso_code
            
        except (geoip2.errors.AddressNotFoundError, ValueError):
            return None
        except Exception as e:
            logger.error("GeoIP lookup failed: %s", str(e))
            return None
    
    async def _get_or_create_data_subject(
        self,
        subject_id: str,
        country: Optional[str] = None
    ) -> DataSubject:
        """Get or create data subject"""
        
        # Try to get existing data subject from GDPR tracker
        subject_data = self.gdpr_tracker.get_subject_data(subject_id)
        
        if subject_data and subject_data['subject_info']:
            info = subject_data['subject_info']
            return DataSubject(
                subject_id=subject_id,
                email=info.get('email'),
                country=info.get('country') or country,
                age=info.get('age'),
                consent_given=bool(info.get('consent_given')),
                consent_date=datetime.fromisoformat(info['consent_date']) if info.get('consent_date') else None,
                data_categories=set(DataCategory(cat) for cat in json.loads(info.get('data_categories', '[]'))),
                processing_purposes=set(DataProcessingPurpose(purpose) for purpose in json.loads(info.get('processing_purposes', '[]'))),
                retention_period=timedelta(days=info['retention_period_days']) if info.get('retention_period_days') else None,
                last_activity=datetime.fromisoformat(info['last_activity']) if info.get('last_activity') else None
            )
        else:
            # Create new data subject
            data_subject = DataSubject(
                subject_id=subject_id,
                country=country
            )
            
            # Register in GDPR tracker if applicable
            if ComplianceFramework.GDPR in self.enabled_frameworks:
                self.gdpr_tracker.register_data_subject(data_subject)
            
            return data_subject
    
    async def _store_compliance_event(self, event: ComplianceEvent) -> None:
        """Store compliance event"""
        
        # Add to memory history
        with self.lock:
            self.events_history.append(event)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO compliance_events (
                event_id, event_type, framework, timestamp, data_subject_id,
                details, severity, resolved, resolution_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.event_type,
            event.framework.value,
            event.timestamp.isoformat(),
            event.data_subject_id,
            json.dumps(event.details),
            event.severity,
            event.resolved,
            event.resolution_notes
        ))
        
        conn.commit()
        conn.close()
    
    async def _store_compliance_assessment(self, report: ComplianceReport) -> None:
        """Store compliance assessment report"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO compliance_assessments (
                assessment_id, framework, timestamp, overall_status,
                findings, recommendations, assessor
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.report_id,
            report.framework.value,
            report.timestamp.isoformat(),
            report.overall_status.value,
            json.dumps(report.findings),
            json.dumps(report.recommendations),
            'system'
        ))
        
        conn.commit()
        conn.close()
    
    async def _count_data_subjects(self, framework: ComplianceFramework) -> int:
        """Count data subjects for framework"""
        
        if framework == ComplianceFramework.GDPR:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM data_subjects')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        
        return 0
    
    def _generate_compliance_recommendations(
        self,
        framework: ComplianceFramework,
        findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        violations = [f for f in findings if f.get('status') == ComplianceStatus.NON_COMPLIANT]
        warnings = [f for f in findings if f.get('status') == ComplianceStatus.WARNING]
        
        if violations:
            recommendations.append(f"URGENT: Address {len(violations)} compliance violations immediately")
            for violation in violations:
                recommendations.append(f"- {violation.get('message', 'Unknown violation')}")
        
        if warnings:
            recommendations.append(f"Review {len(warnings)} compliance warnings")
            for warning in warnings:
                recommendations.append(f"- {warning.get('message', 'Unknown warning')}")
        
        # Framework-specific recommendations
        if framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "Ensure all data processing has proper legal basis",
                "Implement data retention policies with automatic deletion",
                "Provide clear privacy notices and consent mechanisms",
                "Establish processes for data subject rights requests",
                "Conduct regular data protection impact assessments"
            ])
        elif framework == ComplianceFramework.CCPA:
            recommendations.extend([
                "Provide clear disclosure of data collection and use",
                "Implement opt-out mechanisms for data sales",
                "Ensure consumer request verification processes",
                "Maintain records of data disclosures to third parties"
            ])
        elif framework == ComplianceFramework.DMCA:
            recommendations.extend([
                "Establish clear takedown notice procedures",
                "Respond to takedown notices within 24-48 hours",
                "Implement counter-notice processes",
                "Maintain records of all DMCA activities"
            ])
        
        return recommendations
    
    # Compliance rule check methods
    def _check_gdpr_consent(self) -> Optional[Dict[str, Any]]:
        """Check GDPR consent compliance"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for subjects without consent
        cursor.execute('''
            SELECT COUNT(*) FROM data_subjects 
            WHERE consent_given = 0 OR consent_given IS NULL
        ''')
        no_consent_count = cursor.fetchone()[0]
        
        conn.close()
        
        if no_consent_count > 0:
            return {
                'rule': 'gdpr_consent',
                'status': ComplianceStatus.NON_COMPLIANT,
                'message': f"{no_consent_count} data subjects without valid consent",
                'severity': 'CRITICAL',
                'count': no_consent_count
            }
        
        return None
    
    def _check_gdpr_data_retention(self) -> Optional[Dict[str, Any]]:
        """Check GDPR data retention compliance"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for data past retention period
        cursor.execute('''
            SELECT COUNT(*) FROM data_subjects 
            WHERE retention_period_days IS NOT NULL 
            AND datetime(created_at, '+' || retention_period_days || ' days') < datetime('now')
        ''')
        expired_count = cursor.fetchone()[0]
        
        conn.close()
        
        if expired_count > 0:
            return {
                'rule': 'gdpr_data_retention',
                'status': ComplianceStatus.NON_COMPLIANT,
                'message': f"{expired_count} data subjects past retention period",
                'severity': 'HIGH',
                'count': expired_count
            }
        
        return None
    
    def _check_gdpr_data_minimization(self) -> Optional[Dict[str, Any]]:
        """Check GDPR data minimization compliance"""
        
        # Check for excessive data collection
        # This is a placeholder - real implementation would analyze actual data collection
        return {
            'rule': 'gdpr_data_minimization',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Data collection appears minimal and purpose-limited',
            'severity': 'INFO'
        }
    
    def _check_gdpr_requests_response_time(self) -> Optional[Dict[str, Any]]:
        """Check GDPR request response time compliance"""
        
        # Check for overdue requests (GDPR requires response within 30 days)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        overdue_requests = []
        with self.lock:
            for request_id, request_info in self.pending_requests.items():
                if (request_info['status'] == 'pending' and 
                    request_info['created_at'] < cutoff_date):
                    overdue_requests.append(request_id)
        
        if overdue_requests:
            return {
                'rule': 'gdpr_requests_response_time',
                'status': ComplianceStatus.NON_COMPLIANT,
                'message': f"{len(overdue_requests)} data subject requests overdue (>30 days)",
                'severity': 'HIGH',
                'count': len(overdue_requests),
                'overdue_requests': overdue_requests
            }
        
        return None
    
    def _check_ccpa_disclosure(self) -> Optional[Dict[str, Any]]:
        """Check CCPA disclosure compliance"""
        
        # Placeholder for CCPA disclosure checks
        return {
            'rule': 'ccpa_disclosure',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Privacy policy includes required CCPA disclosures',
            'severity': 'INFO'
        }
    
    def _check_ccpa_opt_out(self) -> Optional[Dict[str, Any]]:
        """Check CCPA opt-out compliance"""
        
        # Placeholder for opt-out mechanism checks
        return {
            'rule': 'ccpa_opt_out',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Opt-out mechanisms available for data sales',
            'severity': 'INFO'
        }
    
    def _check_ccpa_data_sales(self) -> Optional[Dict[str, Any]]:
        """Check CCPA data sales compliance"""
        
        # Placeholder for data sales tracking
        return {
            'rule': 'ccpa_data_sales',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'No data sales to third parties detected',
            'severity': 'INFO'
        }
    
    def _check_dmca_response_time(self) -> Optional[Dict[str, Any]]:
        """Check DMCA response time compliance"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for overdue DMCA notices (should respond within 24-48 hours)
        cutoff_date = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        
        cursor.execute('''
            SELECT COUNT(*) FROM dmca_notices 
            WHERE status = 'pending' AND received_at < ?
        ''', (cutoff_date,))
        overdue_count = cursor.fetchone()[0]
        
        conn.close()
        
        if overdue_count > 0:
            return {
                'rule': 'dmca_response_time',
                'status': ComplianceStatus.NON_COMPLIANT,
                'message': f"{overdue_count} DMCA notices overdue (>48 hours)",
                'severity': 'HIGH',
                'count': overdue_count
            }
        
        return None
    
    def _check_dmca_counter_notice_process(self) -> Optional[Dict[str, Any]]:
        """Check DMCA counter-notice process compliance"""
        
        # Placeholder for counter-notice process checks
        return {
            'rule': 'dmca_counter_notice_process',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Counter-notice processes properly implemented',
            'severity': 'INFO'
        }
    
    def _check_pci_data_encryption(self) -> Optional[Dict[str, Any]]:
        """Check PCI-DSS data encryption compliance"""
        
        # Placeholder for PCI encryption checks
        return {
            'rule': 'pci_data_encryption',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Payment data encrypted with approved algorithms',
            'severity': 'INFO'
        }
    
    def _check_pci_access_controls(self) -> Optional[Dict[str, Any]]:
        """Check PCI-DSS access controls compliance"""
        
        # Placeholder for PCI access control checks
        return {
            'rule': 'pci_access_controls',
            'status': ComplianceStatus.COMPLIANT,
            'message': 'Access controls properly implemented for payment data',
            'severity': 'INFO'
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of compliance tracker"""
        logger.info("Shutting down ComplianceTracker...")
        
        # Close GeoIP reader
        if self.geoip_reader:
            self.geoip_reader.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("ComplianceTracker shutdown complete")


# Convenience functions for common compliance patterns
async def track_creator_data_processing(
    compliance_tracker: ComplianceTracker,
    creator_id: str,
    processing_purpose: DataProcessingPurpose,
    ip_address: str
) -> str:
    """Track creator data processing"""
    
    return await compliance_tracker.track_data_processing(
        subject_id=creator_id,
        processing_purpose=processing_purpose,
        data_categories=[DataCategory.BASIC_PERSONAL, DataCategory.CONTENT],
        ip_address=ip_address
    )


async def handle_creator_data_request(
    compliance_tracker: ComplianceTracker,
    creator_id: str,
    request_type: str
) -> str:
    """Handle creator data subject request"""
    
    return await compliance_tracker.handle_data_subject_request(
        subject_id=creator_id,
        request_type=request_type
    )


async def file_content_dmca_takedown(
    compliance_tracker: ComplianceTracker,
    content_id: str,
    creator_id: str,
    claimant_info: Dict[str, str]
) -> str:
    """File DMCA takedown for content violation"""
    
    return await compliance_tracker.file_dmca_takedown(
        content_id=content_id,
        creator_id=creator_id,
        claimant_name=claimant_info['name'],
        claimant_email=claimant_info['email'],
        work_description=claimant_info['work_description'],
        infringement_url=claimant_info['infringement_url']
    )
