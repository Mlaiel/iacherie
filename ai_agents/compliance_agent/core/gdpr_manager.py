"""
GDPR Manager - Advanced Data Protection & Privacy Compliance System

Comprehensive GDPR compliance management, data protection officer automation,
and privacy rights enforcement for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Union
import json
import hashlib
import re
from pathlib import Path

import aiofiles
import redis
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import ComplianceError, ValidationError, SecurityError
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...data_management.data_processor import DataProcessor
from ...security.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Types of GDPR consent"""
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PROFILING = "profiling"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"
    COOKIES = "cookies"
    LOCATION_TRACKING = "location_tracking"

class DataSubjectRight(Enum):
    """GDPR Data Subject Rights"""
    ACCESS = "access"  # Article 15
    RECTIFICATION = "rectification"  # Article 16
    ERASURE = "erasure"  # Article 17 (Right to be forgotten)
    RESTRICTION = "restriction"  # Article 18
    PORTABILITY = "portability"  # Article 20
    OBJECTION = "objection"  # Article 21
    WITHDRAW_CONSENT = "withdraw_consent"  # Article 7(3)

class ProcessingLawfulBasis(Enum):
    """GDPR Lawful Basis for Processing"""
    CONSENT = "consent"  # Article 6(1)(a)
    CONTRACT = "contract"  # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"  # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"  # Article 6(1)(d)
    PUBLIC_TASK = "public_task"  # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Article 6(1)(f)

class DataCategory(Enum):
    """Categories of personal data"""
    BASIC_IDENTITY = "basic_identity"
    CONTACT_INFO = "contact_info"
    DEMOGRAPHIC = "demographic"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    LOCATION = "location"
    TECHNICAL = "technical"
    SPECIAL_CATEGORY = "special_category"  # Article 9

@dataclass
class ConsentRecord:
    """GDPR consent record"""
    id: str
    user_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    method: str = "explicit"  # explicit, implied, withdrawn
    granular_choices: Dict[str, bool] = field(default_factory=dict)
    expiry_date: Optional[datetime] = None
    withdrawal_timestamp: Optional[datetime] = None
    legal_basis: Optional[ProcessingLawfulBasis] = None

@dataclass
class DataSubjectRequest:
    """Data Subject Rights Request"""
    id: str
    user_id: str
    request_type: DataSubjectRight
    request_date: datetime
    description: str
    status: str  # pending, processing, completed, denied
    response_due_date: datetime
    completed_date: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    denial_reason: Optional[str] = None
    verification_status: str = "pending"
    data_affected: List[str] = field(default_factory=list)

@dataclass
class DataProcessingActivity:
    """Record of Processing Activities (Article 30)"""
    id: str
    activity_name: str
    purpose: str
    lawful_basis: ProcessingLawfulBasis
    data_categories: List[DataCategory]
    data_subjects_categories: List[str]
    recipients: List[str]
    retention_period: str
    security_measures: List[str]
    international_transfers: Dict[str, Any]
    created_date: datetime
    last_updated: datetime
    responsible_person: str
    is_active: bool = True

@dataclass
class DataBreachIncident:
    """Data Protection Breach Incident Record"""
    id: str
    incident_date: datetime
    discovery_date: datetime
    description: str
    affected_data_categories: List[DataCategory]
    affected_individuals_count: int
    breach_type: str  # confidentiality, integrity, availability
    risk_level: str  # low, medium, high
    notification_required: bool
    authority_notified: bool = False
    individuals_notified: bool = False
    notification_date: Optional[datetime] = None
    remedial_actions: List[str] = field(default_factory=list)
    lessons_learned: Optional[str] = None
    status: str = "open"  # open, investigating, resolved, closed

class GDPRManager:
    """
    Comprehensive GDPR compliance management system
    
    Manages consent, data subject rights, processing records, breach notifications,
    and automated compliance monitoring for content protection platforms.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize GDPR manager with advanced privacy controls"""
        self.config = config or {}
        self.encryption = ContentEncryption()
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
        self.audit_logger = AuditLogger()
        
        # Core data stores
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        self.processing_activities: Dict[str, DataProcessingActivity] = {}
        self.breach_incidents: Dict[str, DataBreachIncident] = {}
        
        # User data mappings
        self.user_data_mappings: Dict[str, Set[str]] = {}  # user_id -> data_locations
        self.consent_by_user: Dict[str, Dict[ConsentType, ConsentRecord]] = {}
        
        # Redis for session and cache management
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
        
        # Initialize processing activities
        asyncio.create_task(self.initialize_processing_activities())
        
        logger.info("GDPRManager initialized successfully")
    
    async def initialize_processing_activities(self):
        """Initialize standard processing activities for the platform"""
        try:
            activities = [
                DataProcessingActivity(
                    id="user_registration",
                    activity_name="User Account Registration",
                    purpose="Provide platform access and user identification",
                    lawful_basis=ProcessingLawfulBasis.CONTRACT,
                    data_categories=[DataCategory.BASIC_IDENTITY, DataCategory.CONTACT_INFO],
                    data_subjects_categories=["Platform Users", "Content Creators"],
                    recipients=["Internal Systems", "Authentication Services"],
                    retention_period="Account lifetime + 2 years",
                    security_measures=["Encryption at rest", "Access controls", "Audit logging"],
                    international_transfers={"transfers": False},
                    created_date=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc),
                    responsible_person="Data Protection Officer"
                ),
                DataProcessingActivity(
                    id="content_protection",
                    activity_name="Content Protection and Rights Management",
                    purpose="Protect intellectual property and prevent piracy",
                    lawful_basis=ProcessingLawfulBasis.LEGITIMATE_INTERESTS,
                    data_categories=[DataCategory.BEHAVIORAL, DataCategory.TECHNICAL],
                    data_subjects_categories=["Content Creators", "Content Consumers"],
                    recipients=["Content Management Systems", "Anti-Piracy Services"],
                    retention_period="7 years (legal requirements)",
                    security_measures=["End-to-end encryption", "Access logs", "Data masking"],
                    international_transfers={"transfers": True, "adequacy_decision": True},
                    created_date=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc),
                    responsible_person="Content Protection Team Lead"
                ),
                DataProcessingActivity(
                    id="analytics_processing",
                    activity_name="Platform Analytics and Insights",
                    purpose="Improve platform performance and user experience",
                    lawful_basis=ProcessingLawfulBasis.CONSENT,
                    data_categories=[DataCategory.BEHAVIORAL, DataCategory.TECHNICAL, DataCategory.DEMOGRAPHIC],
                    data_subjects_categories=["All Platform Users"],
                    recipients=["Analytics Systems", "Third-party Analytics Providers"],
                    retention_period="2 years from last activity",
                    security_measures=["Data anonymization", "Aggregation", "Secure storage"],
                    international_transfers={"transfers": True, "safeguards": "Standard Contractual Clauses"},
                    created_date=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc),
                    responsible_person="Analytics Team Lead"
                ),
                DataProcessingActivity(
                    id="marketing_communications",
                    activity_name="Marketing and Communication",
                    purpose="Send promotional content and platform updates",
                    lawful_basis=ProcessingLawfulBasis.CONSENT,
                    data_categories=[DataCategory.CONTACT_INFO, DataCategory.BEHAVIORAL],
                    data_subjects_categories=["Opted-in Users"],
                    recipients=["Marketing Systems", "Email Service Providers"],
                    retention_period="Until consent withdrawal + 1 year",
                    security_measures=["List segmentation", "Encryption", "Access controls"],
                    international_transfers={"transfers": False},
                    created_date=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc),
                    responsible_person="Marketing Team Lead"
                )
            ]
            
            for activity in activities:
                self.processing_activities[activity.id] = activity
            
            logger.info(f"Initialized {len(activities)} processing activities")
            
        except Exception as e:
            logger.error(f"Failed to initialize processing activities: {e}")
    
    async def record_consent(self, user_id: str, consent_type: ConsentType,
                           granted: bool, version: str = "1.0",
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None,
                           granular_choices: Optional[Dict[str, bool]] = None) -> ConsentRecord:
        """Record user consent with full GDPR compliance"""
        try:
            consent_id = str(uuid.uuid4())
            
            # Set expiry date (consent should be renewed periodically)
            expiry_date = datetime.now(timezone.utc) + timedelta(days=365 * 2)  # 2 years
            
            consent = ConsentRecord(
                id=consent_id,
                user_id=user_id,
                consent_type=consent_type,
                granted=granted,
                timestamp=datetime.now(timezone.utc),
                version=version,
                ip_address=ip_address,
                user_agent=user_agent,
                method="explicit",
                granular_choices=granular_choices or {},
                expiry_date=expiry_date
            )
            
            # Store consent record
            self.consent_records[consent_id] = consent
            
            # Update user consent mapping
            if user_id not in self.consent_by_user:
                self.consent_by_user[user_id] = {}
            self.consent_by_user[user_id][consent_type] = consent
            
            # Cache in Redis for quick access
            if self.redis_client:
                await self._cache_consent_record(consent)
            
            # Log consent event
            await self.audit_logger.log_event(
                event_type="gdpr_consent_recorded",
                entity_type="user",
                entity_id=user_id,
                details={
                    'consent_id': consent_id,
                    'consent_type': consent_type.value,
                    'granted': granted,
                    'version': version,
                    'method': 'explicit'
                }
            )
            
            logger.info(f"Recorded consent for user {user_id}: {consent_type.value} = {granted}")
            return consent
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise ComplianceError(f"Consent recording failed: {e}")
    
    async def withdraw_consent(self, user_id: str, consent_type: ConsentType,
                             reason: Optional[str] = None) -> bool:
        """Process consent withdrawal"""
        try:
            # Find current consent record
            user_consents = self.consent_by_user.get(user_id, {})
            current_consent = user_consents.get(consent_type)
            
            if not current_consent or not current_consent.granted:
                logger.warning(f"No active consent found for user {user_id}, type {consent_type.value}")
                return False
            
            # Create withdrawal record
            withdrawal_consent = ConsentRecord(
                id=str(uuid.uuid4()),
                user_id=user_id,
                consent_type=consent_type,
                granted=False,
                timestamp=datetime.now(timezone.utc),
                version=current_consent.version,
                method="withdrawal",
                withdrawal_timestamp=datetime.now(timezone.utc)
            )
            
            # Update records
            self.consent_records[withdrawal_consent.id] = withdrawal_consent
            self.consent_by_user[user_id][consent_type] = withdrawal_consent
            
            # Update cache
            if self.redis_client:
                await self._cache_consent_record(withdrawal_consent)
            
            # Trigger data processing changes based on withdrawal
            await self._process_consent_withdrawal(user_id, consent_type)
            
            # Log withdrawal
            await self.audit_logger.log_event(
                event_type="gdpr_consent_withdrawn",
                entity_type="user",
                entity_id=user_id,
                details={
                    'consent_type': consent_type.value,
                    'reason': reason,
                    'original_consent_id': current_consent.id,
                    'withdrawal_id': withdrawal_consent.id
                }
            )
            
            logger.info(f"Processed consent withdrawal for user {user_id}: {consent_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            raise ComplianceError(f"Consent withdrawal failed: {e}")
    
    async def get_user_consent(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user consent status"""
        try:
            user_consents = self.consent_by_user.get(user_id, {})
            consent_status = {}
            
            for consent_type, consent_record in user_consents.items():
                # Check if consent is still valid (not expired)
                is_valid = True
                if consent_record.expiry_date and consent_record.expiry_date < datetime.now(timezone.utc):
                    is_valid = False
                
                consent_status[consent_type.value] = {
                    'granted': consent_record.granted and is_valid,
                    'timestamp': consent_record.timestamp.isoformat(),
                    'version': consent_record.version,
                    'method': consent_record.method,
                    'expires': consent_record.expiry_date.isoformat() if consent_record.expiry_date else None,
                    'expired': not is_valid,
                    'granular_choices': consent_record.granular_choices
                }
            
            # Add missing consent types as not granted
            for consent_type in ConsentType:
                if consent_type.value not in consent_status:
                    consent_status[consent_type.value] = {
                        'granted': False,
                        'timestamp': None,
                        'version': None,
                        'method': None,
                        'expires': None,
                        'expired': False,
                        'granular_choices': {}
                    }
            
            return consent_status
            
        except Exception as e:
            logger.error(f"Failed to get user consent: {e}")
            raise ComplianceError(f"Consent retrieval failed: {e}")
    
    async def submit_data_subject_request(self, user_id: str, request_type: DataSubjectRight,
                                        description: str, user_email: Optional[str] = None) -> DataSubjectRequest:
        """Submit a data subject rights request"""
        try:
            request_id = str(uuid.uuid4())
            
            # Calculate response due date (1 month under GDPR)
            due_date = datetime.now(timezone.utc) + timedelta(days=30)
            
            request = DataSubjectRequest(
                id=request_id,
                user_id=user_id,
                request_type=request_type,
                request_date=datetime.now(timezone.utc),
                description=description,
                status="pending",
                response_due_date=due_date,
                verification_status="pending"
            )
            
            # Store request
            self.data_subject_requests[request_id] = request
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_data_subject_request(request)
            
            # Send verification email if provided
            if user_email:
                await self._send_verification_email(request, user_email)
            
            # Start automated processing for applicable request types
            if request_type in [DataSubjectRight.ACCESS, DataSubjectRight.PORTABILITY]:
                asyncio.create_task(self._process_data_access_request(request))
            
            # Log request submission
            await self.audit_logger.log_event(
                event_type="gdpr_data_subject_request",
                entity_type="user",
                entity_id=user_id,
                details={
                    'request_id': request_id,
                    'request_type': request_type.value,
                    'description': description,
                    'due_date': due_date.isoformat()
                }
            )
            
            logger.info(f"Submitted data subject request {request_id}: {request_type.value}")
            return request
            
        except Exception as e:
            logger.error(f"Failed to submit data subject request: {e}")
            raise ComplianceError(f"Request submission failed: {e}")
    
    async def _process_data_access_request(self, request: DataSubjectRequest):
        """Automatically process data access and portability requests"""
        try:
            request.status = "processing"
            
            # Collect user data from all systems
            user_data = await self._collect_user_data(request.user_id)
            
            # Format data according to request type
            if request.request_type == DataSubjectRight.ACCESS:
                # Article 15 - Right of access
                formatted_data = await self._format_access_response(user_data)
            elif request.request_type == DataSubjectRight.PORTABILITY:
                # Article 20 - Right to data portability
                formatted_data = await self._format_portability_response(user_data)
            else:
                formatted_data = user_data
            
            # Store response data
            request.response_data = {
                'data': formatted_data,
                'collection_timestamp': datetime.now(timezone.utc).isoformat(),
                'format': 'json',
                'data_sources': list(self.user_data_mappings.get(request.user_id, set()))
            }
            
            request.status = "completed"
            request.completed_date = datetime.now(timezone.utc)
            
            # Update cache
            if self.redis_client:
                await self._cache_data_subject_request(request)
            
            # Notify user (implementation would send actual notification)
            await self._notify_user_request_completed(request)
            
            logger.info(f"Completed data access request {request.id}")
            
        except Exception as e:
            logger.error(f"Failed to process data access request {request.id}: {e}")
            request.status = "error"
            request.denial_reason = f"Processing error: {str(e)}"
    
    async def process_erasure_request(self, request_id: str, verified: bool = True) -> bool:
        """Process right to erasure (right to be forgotten) request"""
        try:
            request = self.data_subject_requests.get(request_id)
            if not request or request.request_type != DataSubjectRight.ERASURE:
                return False
            
            if not verified:
                request.status = "denied"
                request.denial_reason = "Identity verification failed"
                return False
            
            request.status = "processing"
            user_id = request.user_id
            
            # Check if erasure is legally possible
            erasure_allowed, restrictions = await self._check_erasure_restrictions(user_id)
            
            if not erasure_allowed:
                request.status = "denied"
                request.denial_reason = f"Erasure not permitted: {', '.join(restrictions)}"
                return False
            
            # Execute data erasure across all systems
            erasure_results = await self._execute_data_erasure(user_id)
            
            # Verify erasure completion
            verification_passed = await self._verify_erasure_completion(user_id, erasure_results)
            
            if verification_passed:
                request.status = "completed"
                request.completed_date = datetime.now(timezone.utc)
                request.response_data = {
                    'erasure_completed': True,
                    'systems_processed': erasure_results.get('systems', []),
                    'verification_passed': True,
                    'completion_timestamp': datetime.now(timezone.utc).isoformat()
                }
            else:
                request.status = "error"
                request.denial_reason = "Erasure verification failed"
            
            # Log erasure completion
            await self.audit_logger.log_event(
                event_type="gdpr_data_erasure",
                entity_type="user",
                entity_id=user_id,
                details={
                    'request_id': request_id,
                    'status': request.status,
                    'verification_passed': verification_passed,
                    'erasure_results': erasure_results
                }
            )
            
            return verification_passed
            
        except Exception as e:
            logger.error(f"Failed to process erasure request {request_id}: {e}")
            return False
    
    async def report_data_breach(self, description: str, affected_data_categories: List[DataCategory],
                               affected_individuals_count: int, breach_type: str,
                               discovery_date: Optional[datetime] = None) -> DataBreachIncident:
        """Report a data protection breach incident"""
        try:
            incident_id = str(uuid.uuid4())
            incident_date = discovery_date or datetime.now(timezone.utc)
            
            # Assess risk level
            risk_level = await self._assess_breach_risk(
                affected_data_categories, affected_individuals_count, breach_type
            )
            
            # Determine notification requirements
            notification_required = await self._assess_notification_requirements(
                risk_level, affected_data_categories, affected_individuals_count
            )
            
            incident = DataBreachIncident(
                id=incident_id,
                incident_date=incident_date,
                discovery_date=datetime.now(timezone.utc),
                description=description,
                affected_data_categories=affected_data_categories,
                affected_individuals_count=affected_individuals_count,
                breach_type=breach_type,
                risk_level=risk_level,
                notification_required=notification_required
            )
            
            # Store incident
            self.breach_incidents[incident_id] = incident
            
            # If high risk and notification required, trigger immediate notifications
            if notification_required and risk_level in ['medium', 'high']:
                asyncio.create_task(self._handle_breach_notifications(incident))
            
            # Log breach incident
            await self.audit_logger.log_event(
                event_type="gdpr_data_breach_reported",
                entity_type="system",
                entity_id="platform",
                details={
                    'incident_id': incident_id,
                    'risk_level': risk_level,
                    'affected_count': affected_individuals_count,
                    'notification_required': notification_required,
                    'breach_type': breach_type
                }
            )
            
            logger.critical(f"Data breach incident reported: {incident_id} (Risk: {risk_level})")
            return incident
            
        except Exception as e:
            logger.error(f"Failed to report data breach: {e}")
            raise ComplianceError(f"Breach reporting failed: {e}")
    
    async def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all user data from various systems"""
        try:
            user_data = {
                'user_profile': {},
                'content_data': {},
                'behavioral_data': {},
                'technical_data': {},
                'consent_records': {},
                'request_history': []
            }
            
            # Get user profile data
            # This would integrate with actual user management systems
            user_data['user_profile'] = await self._get_user_profile_data(user_id)
            
            # Get content data
            user_data['content_data'] = await self._get_user_content_data(user_id)
            
            # Get behavioral/analytics data
            user_data['behavioral_data'] = await self._get_user_behavioral_data(user_id)
            
            # Get technical data (logs, sessions, etc.)
            user_data['technical_data'] = await self._get_user_technical_data(user_id)
            
            # Get consent records
            user_data['consent_records'] = await self.get_user_consent(user_id)
            
            # Get request history
            user_requests = [req for req in self.data_subject_requests.values() if req.user_id == user_id]
            user_data['request_history'] = [
                {
                    'request_id': req.id,
                    'type': req.request_type.value,
                    'date': req.request_date.isoformat(),
                    'status': req.status
                }
                for req in user_requests
            ]
            
            return user_data
            
        except Exception as e:
            logger.error(f"Failed to collect user data for {user_id}: {e}")
            return {}
    
    async def _get_user_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Get user profile data"""
        # Placeholder - would integrate with actual user system
        return {
            'user_id': user_id,
            'registration_date': '2025-01-01T00:00:00Z',
            'last_login': '2025-08-10T12:00:00Z',
            'account_type': 'content_creator',
            'status': 'active'
        }
    
    async def _get_user_content_data(self, user_id: str) -> Dict[str, Any]:
        """Get user content data"""
        # Placeholder - would integrate with content management system
        return {
            'total_uploads': 0,
            'content_types': [],
            'storage_used': '0 GB',
            'protection_settings': {}
        }
    
    async def _get_user_behavioral_data(self, user_id: str) -> Dict[str, Any]:
        """Get user behavioral/analytics data"""
        # Placeholder - would integrate with analytics systems
        return {
            'session_count': 0,
            'page_views': 0,
            'feature_usage': {},
            'preferences': {}
        }
    
    async def _get_user_technical_data(self, user_id: str) -> Dict[str, Any]:
        """Get user technical data (logs, IPs, etc.)"""
        # Placeholder - would integrate with logging systems
        return {
            'ip_addresses': [],
            'user_agents': [],
            'api_calls': 0,
            'error_logs': []
        }
    
    async def _format_access_response(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for Article 15 access response"""
        return {
            'data_subject_information': user_data.get('user_profile', {}),
            'processing_purposes': [
                'Account management',
                'Content protection',
                'Platform analytics',
                'Communication'
            ],
            'data_categories': [
                'Identity data',
                'Contact information',
                'Behavioral data',
                'Technical data'
            ],
            'data_recipients': [
                'Internal systems',
                'Analytics providers',
                'Communication services'
            ],
            'retention_periods': {
                'account_data': 'Account lifetime + 2 years',
                'behavioral_data': '2 years from last activity',
                'technical_logs': '1 year'
            },
            'data_subject_rights': [
                'Right to rectification',
                'Right to erasure',
                'Right to restrict processing',
                'Right to data portability',
                'Right to object'
            ],
            'user_data': user_data
        }
    
    async def _format_portability_response(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for Article 20 portability response"""
        portable_data = {
            'user_profile': user_data.get('user_profile', {}),
            'content_metadata': user_data.get('content_data', {}),
            'preferences': user_data.get('behavioral_data', {}).get('preferences', {}),
            'consent_history': user_data.get('consent_records', {})
        }
        
        # Remove non-portable system data
        if 'technical_data' in portable_data:
            del portable_data['technical_data']
        
        return {
            'format': 'JSON',
            'encoding': 'UTF-8',
            'data_export_date': datetime.now(timezone.utc).isoformat(),
            'portable_data': portable_data
        }
    
    async def _check_erasure_restrictions(self, user_id: str) -> Tuple[bool, List[str]]:
        """Check if data erasure is legally possible"""
        restrictions = []
        
        # Check for legal obligations (Article 17(3))
        # Example: ongoing legal proceedings, regulatory requirements
        
        # Check for legitimate interests that override erasure
        # Example: fraud prevention, security logs
        
        # Check for contract obligations
        # Example: ongoing service provision, payment processing
        
        # For this implementation, we'll allow erasure with some restrictions
        if len(restrictions) == 0:
            # Add standard restrictions that might apply
            restrictions_to_check = [
                # Would check actual business logic here
            ]
        
        return len(restrictions) == 0, restrictions
    
    async def _execute_data_erasure(self, user_id: str) -> Dict[str, Any]:
        """Execute data erasure across all systems"""
        try:
            erasure_results = {
                'systems': [],
                'success_count': 0,
                'failure_count': 0,
                'errors': []
            }
            
            # List of systems where user data might be stored
            systems_to_process = [
                'user_database',
                'content_storage',
                'analytics_database',
                'session_cache',
                'backup_systems',
                'log_aggregators'
            ]
            
            for system in systems_to_process:
                try:
                    # Placeholder for actual system integration
                    await self._erase_from_system(system, user_id)
                    erasure_results['systems'].append(system)
                    erasure_results['success_count'] += 1
                except Exception as e:
                    erasure_results['failure_count'] += 1
                    erasure_results['errors'].append(f"{system}: {str(e)}")
                    logger.error(f"Erasure failed for system {system}: {e}")
            
            # Remove user from internal mappings
            if user_id in self.consent_by_user:
                del self.consent_by_user[user_id]
            
            if user_id in self.user_data_mappings:
                del self.user_data_mappings[user_id]
            
            # Clear Redis cache
            if self.redis_client:
                await self._clear_user_cache(user_id)
            
            return erasure_results
            
        except Exception as e:
            logger.error(f"Data erasure execution failed: {e}")
            return {'error': str(e)}
    
    async def _erase_from_system(self, system: str, user_id: str):
        """Erase user data from specific system"""
        # Placeholder for actual system integration
        logger.info(f"Erasing user {user_id} data from {system}")
        await asyncio.sleep(0.1)  # Simulate processing time
    
    async def _verify_erasure_completion(self, user_id: str, erasure_results: Dict[str, Any]) -> bool:
        """Verify that data erasure was completed successfully"""
        try:
            # Check if any critical systems failed
            if erasure_results.get('failure_count', 0) > 0:
                critical_failures = []
                for error in erasure_results.get('errors', []):
                    if 'user_database' in error or 'content_storage' in error:
                        critical_failures.append(error)
                
                if critical_failures:
                    logger.error(f"Critical erasure failures: {critical_failures}")
                    return False
            
            # Verify data is actually removed (sampling check)
            verification_passed = True
            
            # Check key systems
            for system in ['user_database', 'content_storage']:
                if system in erasure_results.get('systems', []):
                    # Placeholder for actual verification
                    system_verified = await self._verify_system_erasure(system, user_id)
                    if not system_verified:
                        verification_passed = False
                        break
            
            return verification_passed
            
        except Exception as e:
            logger.error(f"Erasure verification failed: {e}")
            return False
    
    async def _verify_system_erasure(self, system: str, user_id: str) -> bool:
        """Verify erasure from specific system"""
        # Placeholder for actual verification logic
        logger.info(f"Verifying erasure of user {user_id} from {system}")
        return True
    
    async def _assess_breach_risk(self, data_categories: List[DataCategory],
                                affected_count: int, breach_type: str) -> str:
        """Assess data breach risk level"""
        risk_score = 0
        
        # Risk factors based on data categories
        high_risk_categories = [DataCategory.SPECIAL_CATEGORY, DataCategory.BIOMETRIC, 
                              DataCategory.FINANCIAL, DataCategory.HEALTH]
        medium_risk_categories = [DataCategory.BASIC_IDENTITY, DataCategory.CONTACT_INFO]
        
        for category in data_categories:
            if category in high_risk_categories:
                risk_score += 3
            elif category in medium_risk_categories:
                risk_score += 2
            else:
                risk_score += 1
        
        # Risk factors based on affected individuals
        if affected_count > 1000:
            risk_score += 3
        elif affected_count > 100:
            risk_score += 2
        elif affected_count > 10:
            risk_score += 1
        
        # Risk factors based on breach type
        if breach_type in ['confidentiality', 'unauthorized_access']:
            risk_score += 2
        elif breach_type in ['integrity', 'data_corruption']:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 8:
            return 'high'
        elif risk_score >= 5:
            return 'medium'
        else:
            return 'low'
    
    async def _assess_notification_requirements(self, risk_level: str,
                                              data_categories: List[DataCategory],
                                              affected_count: int) -> bool:
        """Assess whether breach notification is required"""
        # Article 33 - Notification requirements
        if risk_level == 'high':
            return True
        
        if risk_level == 'medium' and affected_count > 100:
            return True
        
        # Special category data always requires notification
        special_categories = [DataCategory.SPECIAL_CATEGORY, DataCategory.BIOMETRIC,
                            DataCategory.HEALTH, DataCategory.FINANCIAL]
        
        if any(cat in data_categories for cat in special_categories):
            return True
        
        return False
    
    async def _handle_breach_notifications(self, incident: DataBreachIncident):
        """Handle breach notification requirements"""
        try:
            # Article 33 - Notification to supervisory authority (72 hours)
            if incident.notification_required and not incident.authority_notified:
                await self._notify_supervisory_authority(incident)
                incident.authority_notified = True
                incident.notification_date = datetime.now(timezone.utc)
            
            # Article 34 - Notification to data subjects (if high risk)
            if incident.risk_level == 'high' and not incident.individuals_notified:
                await self._notify_affected_individuals(incident)
                incident.individuals_notified = True
            
            logger.info(f"Breach notifications processed for incident {incident.id}")
            
        except Exception as e:
            logger.error(f"Failed to handle breach notifications: {e}")
    
    async def _notify_supervisory_authority(self, incident: DataBreachIncident):
        """Notify supervisory authority of breach (Article 33)"""
        # Placeholder for actual authority notification
        logger.critical(f"GDPR Article 33: Notifying supervisory authority of breach {incident.id}")
    
    async def _notify_affected_individuals(self, incident: DataBreachIncident):
        """Notify affected individuals of breach (Article 34)"""
        # Placeholder for individual notifications
        logger.critical(f"GDPR Article 34: Notifying {incident.affected_individuals_count} individuals of breach {incident.id}")
    
    async def _cache_consent_record(self, consent: ConsentRecord):
        """Cache consent record in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_data = {
                'user_id': consent.user_id,
                'consent_type': consent.consent_type.value,
                'granted': consent.granted,
                'timestamp': consent.timestamp.isoformat(),
                'expires': consent.expiry_date.isoformat() if consent.expiry_date else None
            }
            
            key = f"gdpr_consent:{consent.user_id}:{consent.consent_type.value}"
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, key, 86400, json.dumps(cache_data)  # 24 hours
            )
        except Exception as e:
            logger.warning(f"Failed to cache consent record: {e}")
    
    async def _cache_data_subject_request(self, request: DataSubjectRequest):
        """Cache data subject request in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_data = {
                'id': request.id,
                'user_id': request.user_id,
                'type': request.request_type.value,
                'status': request.status,
                'request_date': request.request_date.isoformat(),
                'due_date': request.response_due_date.isoformat()
            }
            
            key = f"gdpr_request:{request.id}"
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, key, 86400 * 30, json.dumps(cache_data)  # 30 days
            )
        except Exception as e:
            logger.warning(f"Failed to cache data subject request: {e}")
    
    async def _clear_user_cache(self, user_id: str):
        """Clear all user-related cache entries"""
        if not self.redis_client:
            return
        
        try:
            # Pattern to match all user-related keys
            patterns = [
                f"gdpr_consent:{user_id}:*",
                f"gdpr_request:*",  # Would need more specific pattern in production
                f"user_data:{user_id}:*"
            ]
            
            for pattern in patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            
        except Exception as e:
            logger.warning(f"Failed to clear user cache: {e}")
    
    async def _process_consent_withdrawal(self, user_id: str, consent_type: ConsentType):
        """Process data handling changes after consent withdrawal"""
        try:
            if consent_type == ConsentType.MARKETING:
                # Remove from marketing lists
                await self._remove_from_marketing_lists(user_id)
            
            elif consent_type == ConsentType.ANALYTICS:
                # Stop analytics collection
                await self._stop_analytics_collection(user_id)
            
            elif consent_type == ConsentType.THIRD_PARTY_SHARING:
                # Stop data sharing with third parties
                await self._stop_third_party_sharing(user_id)
            
            elif consent_type == ConsentType.PROFILING:
                # Remove user from profiling activities
                await self._remove_from_profiling(user_id)
            
            logger.info(f"Processed consent withdrawal actions for user {user_id}, type {consent_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to process consent withdrawal actions: {e}")
    
    async def _remove_from_marketing_lists(self, user_id: str):
        """Remove user from marketing communications"""
        # Placeholder for marketing system integration
        logger.info(f"Removing user {user_id} from marketing lists")
    
    async def _stop_analytics_collection(self, user_id: str):
        """Stop analytics data collection for user"""
        # Placeholder for analytics system integration
        logger.info(f"Stopping analytics collection for user {user_id}")
    
    async def _stop_third_party_sharing(self, user_id: str):
        """Stop sharing user data with third parties"""
        # Placeholder for third-party integration
        logger.info(f"Stopping third-party data sharing for user {user_id}")
    
    async def _remove_from_profiling(self, user_id: str):
        """Remove user from profiling activities"""
        # Placeholder for profiling system integration
        logger.info(f"Removing user {user_id} from profiling activities")
    
    async def _send_verification_email(self, request: DataSubjectRequest, email: str):
        """Send verification email for data subject request"""
        # Placeholder for email service integration
        logger.info(f"Sending verification email for request {request.id} to {email}")
    
    async def _notify_user_request_completed(self, request: DataSubjectRequest):
        """Notify user that their request has been completed"""
        # Placeholder for notification service integration
        logger.info(f"Notifying user of completed request {request.id}")


class DataProtectionOfficer:
    """
    Automated Data Protection Officer functions and compliance monitoring
    """
    
    def __init__(self, gdpr_manager: GDPRManager):
        self.gdpr_manager = gdpr_manager
        self.compliance_metrics = {}
        
    async def generate_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive GDPR compliance dashboard"""
        try:
            # Get current metrics
            total_users = len(self.gdpr_manager.consent_by_user)
            active_requests = len([r for r in self.gdpr_manager.data_subject_requests.values() 
                                 if r.status in ['pending', 'processing']])
            overdue_requests = len([r for r in self.gdpr_manager.data_subject_requests.values() 
                                  if r.response_due_date < datetime.now(timezone.utc) and r.status != 'completed'])
            
            breach_count = len(self.gdpr_manager.breach_incidents)
            high_risk_breaches = len([b for b in self.gdpr_manager.breach_incidents.values() 
                                    if b.risk_level == 'high'])
            
            # Consent analysis
            consent_stats = {}
            for user_id, consents in self.gdpr_manager.consent_by_user.items():
                for consent_type, consent_record in consents.items():
                    if consent_type.value not in consent_stats:
                        consent_stats[consent_type.value] = {'granted': 0, 'total': 0}
                    
                    consent_stats[consent_type.value]['total'] += 1
                    if consent_record.granted:
                        consent_stats[consent_type.value]['granted'] += 1
            
            return {
                'overview': {
                    'total_users': total_users,
                    'active_requests': active_requests,
                    'overdue_requests': overdue_requests,
                    'breach_incidents': breach_count,
                    'high_risk_breaches': high_risk_breaches
                },
                'consent_statistics': consent_stats,
                'processing_activities': len(self.gdpr_manager.processing_activities),
                'compliance_score': await self._calculate_compliance_score(),
                'alerts': await self._get_compliance_alerts(),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance dashboard: {e}")
            return {'error': str(e)}
    
    async def _calculate_compliance_score(self) -> float:
        """Calculate overall GDPR compliance score"""
        try:
            score_components = {
                'consent_management': 0,
                'request_handling': 0,
                'breach_management': 0,
                'documentation': 0
            }
            
            # Consent management score (25%)
            total_consents = sum(len(consents) for consents in self.gdpr_manager.consent_by_user.values())
            if total_consents > 0:
                valid_consents = 0
                for consents in self.gdpr_manager.consent_by_user.values():
                    for consent in consents.values():
                        if consent.granted and (not consent.expiry_date or 
                                              consent.expiry_date > datetime.now(timezone.utc)):
                            valid_consents += 1
                score_components['consent_management'] = (valid_consents / total_consents) * 25
            else:
                score_components['consent_management'] = 25  # No consents required yet
            
            # Request handling score (25%)
            total_requests = len(self.gdpr_manager.data_subject_requests)
            if total_requests > 0:
                completed_on_time = len([r for r in self.gdpr_manager.data_subject_requests.values()
                                       if r.status == 'completed' and 
                                       (not r.completed_date or r.completed_date <= r.response_due_date)])
                score_components['request_handling'] = (completed_on_time / total_requests) * 25
            else:
                score_components['request_handling'] = 25  # No requests yet
            
            # Breach management score (25%)
            total_breaches = len(self.gdpr_manager.breach_incidents)
            if total_breaches > 0:
                properly_handled = len([b for b in self.gdpr_manager.breach_incidents.values()
                                      if b.authority_notified or not b.notification_required])
                score_components['breach_management'] = (properly_handled / total_breaches) * 25
            else:
                score_components['breach_management'] = 25  # No breaches
            
            # Documentation score (25%)
            required_activities = ['user_registration', 'content_protection', 'analytics_processing']
            documented_activities = len([a for a in self.gdpr_manager.processing_activities.keys()
                                       if a in required_activities])
            score_components['documentation'] = (documented_activities / len(required_activities)) * 25
            
            total_score = sum(score_components.values())
            return min(100.0, max(0.0, total_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate compliance score: {e}")
            return 0.0
    
    async def _get_compliance_alerts(self) -> List[Dict[str, Any]]:
        """Get current compliance alerts and issues"""
        alerts = []
        
        # Overdue requests
        overdue_requests = [r for r in self.gdpr_manager.data_subject_requests.values()
                          if r.response_due_date < datetime.now(timezone.utc) and r.status != 'completed']
        
        for request in overdue_requests:
            alerts.append({
                'type': 'overdue_request',
                'severity': 'high',
                'message': f"Data subject request {request.id} is overdue",
                'details': {
                    'request_id': request.id,
                    'request_type': request.request_type.value,
                    'due_date': request.response_due_date.isoformat(),
                    'days_overdue': (datetime.now(timezone.utc) - request.response_due_date).days
                }
            })
        
        # Expired consents
        for user_id, consents in self.gdpr_manager.consent_by_user.items():
            for consent in consents.values():
                if (consent.expiry_date and 
                    consent.expiry_date < datetime.now(timezone.utc) and 
                    consent.granted):
                    alerts.append({
                        'type': 'expired_consent',
                        'severity': 'medium',
                        'message': f"User consent expired for {consent.consent_type.value}",
                        'details': {
                            'user_id': user_id,
                            'consent_type': consent.consent_type.value,
                            'expired_date': consent.expiry_date.isoformat()
                        }
                    })
        
        # High risk breaches
        high_risk_breaches = [b for b in self.gdpr_manager.breach_incidents.values()
                            if b.risk_level == 'high' and b.status == 'open']
        
        for breach in high_risk_breaches:
            alerts.append({
                'type': 'high_risk_breach',
                'severity': 'critical',
                'message': f"High risk data breach incident {breach.id}",
                'details': {
                    'incident_id': breach.id,
                    'affected_count': breach.affected_individuals_count,
                    'discovery_date': breach.discovery_date.isoformat(),
                    'notification_required': breach.notification_required
                }
            })
        
        return sorted(alerts, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['severity']])
