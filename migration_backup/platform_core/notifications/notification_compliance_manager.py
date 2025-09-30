#!/usr/bin/env python3
"""
⚖️ Enterprise Notification Compliance Manager - Ainflue Platform Core
GDPR/CAN-SPAM/CASL/CCPA compliance and legal framework management

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import hashlib
import re

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CAN_SPAM = "can_spam"  # CAN-SPAM Act (US)
    CASL = "casl"  # Canadian Anti-Spam Legislation
    CCPA = "ccpa"  # California Consumer Privacy Act
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    PDPA = "pdpa"  # Personal Data Protection Act (Singapore)

class ConsentType(Enum):
    """Types of user consent"""
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    DOUBLE_OPT_IN = "double_opt_in"
    IMPLIED = "implied"
    EXPLICIT = "explicit"
    GRANULAR = "granular"

class NotificationCategory(Enum):
    """Notification categories for compliance"""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    PROMOTIONAL = "promotional"
    SYSTEM = "system"
    SECURITY = "security"
    LEGAL = "legal"
    OPERATIONAL = "operational"

class ComplianceViolation(Enum):
    """Types of compliance violations"""
    NO_CONSENT = "no_consent"
    EXPIRED_CONSENT = "expired_consent"
    INVALID_UNSUBSCRIBE = "invalid_unsubscribe"
    MISSING_SENDER_INFO = "missing_sender_info"
    DECEPTIVE_SUBJECT = "deceptive_subject"
    DATA_RETENTION = "data_retention"
    CROSS_BORDER = "cross_border"

@dataclass
class ConsentRecord:
    """User consent record for compliance tracking"""
    user_id: str
    email: Optional[str]
    phone: Optional[str]
    consent_type: ConsentType
    categories: List[NotificationCategory]
    frameworks: List[ComplianceFramework]
    granted_at: datetime
    expires_at: Optional[datetime]
    source: str  # Where consent was obtained
    ip_address: Optional[str]
    user_agent: Optional[str]
    double_opt_in_confirmed: bool = False
    withdrawal_method: Optional[str] = None
    withdrawn_at: Optional[datetime] = None

@dataclass
class ComplianceCheck:
    """Result of compliance verification"""
    notification_id: str
    user_id: str
    is_compliant: bool
    violations: List[ComplianceViolation]
    frameworks_checked: List[ComplianceFramework]
    consent_status: str
    required_actions: List[str]
    risk_level: str  # low, medium, high, critical
    metadata: Dict[str, Any]
    checked_at: datetime

@dataclass
class UnsubscribeRequest:
    """Unsubscribe request record"""
    id: str
    user_id: str
    email: Optional[str]
    phone: Optional[str]
    categories: List[NotificationCategory]
    method: str  # email_link, sms_reply, web_form, api
    requested_at: datetime
    processed_at: Optional[datetime]
    confirmation_sent: bool
    ip_address: Optional[str]

class NotificationComplianceManager:
    """Enterprise notification compliance manager with legal framework support"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # Compliance rules configuration
        self.compliance_rules = {
            ComplianceFramework.GDPR: {
                'consent_required': True,
                'explicit_consent': True,
                'data_retention_days': 1095,  # 3 years
                'unsubscribe_required': True,
                'sender_identification': True,
                'data_portability': True,
                'right_to_be_forgotten': True,
                'lawful_basis_required': True
            },
            ComplianceFramework.CAN_SPAM: {
                'consent_required': False,  # Opt-out model
                'sender_identification': True,
                'physical_address': True,
                'clear_unsubscribe': True,
                'unsubscribe_within_days': 10,
                'truthful_subject_lines': True,
                'commercial_identification': True
            },
            ComplianceFramework.CASL: {
                'consent_required': True,
                'express_consent': True,
                'sender_identification': True,
                'unsubscribe_mechanism': True,
                'consent_record_keeping': True,
                'business_relationship_exemption': True
            },
            ComplianceFramework.CCPA: {
                'privacy_notice': True,
                'opt_out_rights': True,
                'data_deletion_rights': True,
                'data_portability': True,
                'non_discrimination': True
            }
        }
        
        # Category-specific rules
        self.category_rules = {
            NotificationCategory.TRANSACTIONAL: {
                'consent_required': False,
                'unsubscribe_required': False,
                'frameworks_exempt': [ComplianceFramework.CAN_SPAM]
            },
            NotificationCategory.MARKETING: {
                'consent_required': True,
                'explicit_consent': True,
                'unsubscribe_required': True,
                'frequency_limits': True
            },
            NotificationCategory.SECURITY: {
                'consent_required': False,
                'override_preferences': True,
                'delivery_required': True
            }
        }
        
        # Consent storage
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.unsubscribe_requests: Dict[str, UnsubscribeRequest] = {}
        
        # Compliance templates
        self.compliance_templates = {
            'unsubscribe_footer': {
                'en': 'To unsubscribe, click here: {unsubscribe_link}',
                'fr': 'Pour vous désabonner, cliquez ici: {unsubscribe_link}',
                'de': 'Zum Abbestellen hier klicken: {unsubscribe_link}',
                'es': 'Para darse de baja, haga clic aquí: {unsubscribe_link}'
            },
            'sender_identification': {
                'en': 'This message was sent by {company_name}, {company_address}',
                'fr': 'Ce message a été envoyé par {company_name}, {company_address}',
                'de': 'Diese Nachricht wurde von {company_name}, {company_address} gesendet',
                'es': 'Este mensaje fue enviado por {company_name}, {company_address}'
            }
        }
        
        # Performance metrics
        self.metrics = {
            'compliance_checks': 0,
            'violations_detected': 0,
            'consent_records': 0,
            'unsubscribe_requests': 0,
            'blocked_notifications': 0,
            'gdpr_requests': 0,
            'data_deletions': 0,
            'consent_renewals': 0
        }

    async def initialize(self):
        """Initialize compliance manager"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ Compliance manager initialized with Redis connection")
            
            # Load existing consent records
            await self._load_consent_records()
            
            # Set up compliance monitoring
            await self._setup_compliance_monitoring()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize compliance manager: {e}")
            raise

    async def check_notification_compliance(
        self,
        notification_id: str,
        user_id: str,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        category: NotificationCategory = NotificationCategory.MARKETING,
        content: str = "",
        subject: Optional[str] = None,
        sender_info: Optional[Dict[str, Any]] = None,
        user_location: Optional[str] = None
    ) -> ComplianceCheck:
        """
        Check notification compliance against applicable frameworks
        
        Args:
            notification_id: Unique notification identifier
            user_id: Target user identifier
            recipient_email: Recipient email address
            recipient_phone: Recipient phone number
            category: Notification category
            content: Notification content
            subject: Email subject line
            sender_info: Sender identification information
            user_location: User's location for jurisdiction determination
            
        Returns:
            ComplianceCheck with compliance status and violations
        """
        self.metrics['compliance_checks'] += 1
        
        try:
            # Determine applicable frameworks
            applicable_frameworks = await self._determine_applicable_frameworks(
                user_location, recipient_email, recipient_phone
            )
            
            # Get user consent status
            consent_record = await self._get_user_consent(user_id, recipient_email, recipient_phone)
            
            # Check compliance for each framework
            violations = []
            is_compliant = True
            required_actions = []
            risk_level = "low"
            
            for framework in applicable_frameworks:
                framework_violations = await self._check_framework_compliance(
                    framework, category, consent_record, content, subject, sender_info
                )
                violations.extend(framework_violations)
            
            # Determine overall compliance status
            if violations:
                is_compliant = False
                self.metrics['violations_detected'] += 1
                
                # Calculate risk level
                risk_level = self._calculate_risk_level(violations)
                
                # Generate required actions
                required_actions = self._generate_required_actions(violations, category)
            
            # Check content compliance
            content_violations = await self._check_content_compliance(content, subject, category)
            violations.extend(content_violations)
            
            if content_violations:
                is_compliant = False
            
            # Create compliance check result
            compliance_check = ComplianceCheck(
                notification_id=notification_id,
                user_id=user_id,
                is_compliant=is_compliant,
                violations=violations,
                frameworks_checked=applicable_frameworks,
                consent_status=self._get_consent_status_string(consent_record),
                required_actions=required_actions,
                risk_level=risk_level,
                metadata={
                    'category': category.value,
                    'recipient_email': recipient_email,
                    'recipient_phone': recipient_phone,
                    'user_location': user_location,
                    'check_timestamp': datetime.utcnow().isoformat()
                },
                checked_at=datetime.utcnow()
            )
            
            # Store compliance check
            await self._store_compliance_check(compliance_check)
            
            # Block notification if not compliant and high risk
            if not is_compliant and risk_level in ['high', 'critical']:
                self.metrics['blocked_notifications'] += 1
                self.logger.warning(
                    f"⚠️ Notification blocked due to compliance violations: {notification_id}"
                )
            
            return compliance_check
            
        except Exception as e:
            self.logger.error(f"❌ Compliance check failed: {e}")
            
            # Return non-compliant status on error for safety
            return ComplianceCheck(
                notification_id=notification_id,
                user_id=user_id,
                is_compliant=False,
                violations=[ComplianceViolation.NO_CONSENT],
                frameworks_checked=[],
                consent_status="error",
                required_actions=["Review compliance manually"],
                risk_level="high",
                metadata={'error': str(e)},
                checked_at=datetime.utcnow()
            )

    async def _determine_applicable_frameworks(
        self,
        user_location: Optional[str],
        email: Optional[str],
        phone: Optional[str]
    ) -> List[ComplianceFramework]:
        """Determine which compliance frameworks apply"""
        
        frameworks = []
        
        # Location-based framework determination
        if user_location:
            location_lower = user_location.lower()
            
            if any(country in location_lower for country in ['eu', 'europe', 'germany', 'france', 'spain', 'italy']):
                frameworks.append(ComplianceFramework.GDPR)
            
            if 'us' in location_lower or 'united states' in location_lower:
                frameworks.append(ComplianceFramework.CAN_SPAM)
                
            if 'california' in location_lower:
                frameworks.append(ComplianceFramework.CCPA)
                
            if 'canada' in location_lower:
                frameworks.append(ComplianceFramework.CASL)
                
            if 'brazil' in location_lower:
                frameworks.append(ComplianceFramework.LGPD)
                
            if 'singapore' in location_lower:
                frameworks.append(ComplianceFramework.PDPA)
        
        # Email domain-based detection
        if email and not frameworks:
            domain = email.split('@')[-1].lower()
            
            eu_domains = ['.de', '.fr', '.it', '.es', '.nl', '.be', '.eu']
            if any(domain.endswith(d) for d in eu_domains):
                frameworks.append(ComplianceFramework.GDPR)
        
        # Default to most restrictive frameworks if uncertain
        if not frameworks:
            frameworks = [ComplianceFramework.GDPR, ComplianceFramework.CAN_SPAM]
        
        return frameworks

    async def _check_framework_compliance(
        self,
        framework: ComplianceFramework,
        category: NotificationCategory,
        consent_record: Optional[ConsentRecord],
        content: str,
        subject: Optional[str],
        sender_info: Optional[Dict[str, Any]]
    ) -> List[ComplianceViolation]:
        """Check compliance for specific framework"""
        
        violations = []
        rules = self.compliance_rules.get(framework, {})
        category_rules = self.category_rules.get(category, {})
        
        # Check consent requirements
        if rules.get('consent_required', False) and category_rules.get('consent_required', True):
            if not consent_record:
                violations.append(ComplianceViolation.NO_CONSENT)
            elif consent_record.withdrawn_at:
                violations.append(ComplianceViolation.NO_CONSENT)
            elif consent_record.expires_at and consent_record.expires_at < datetime.utcnow():
                violations.append(ComplianceViolation.EXPIRED_CONSENT)
            elif framework not in consent_record.frameworks:
                violations.append(ComplianceViolation.NO_CONSENT)
            elif category not in consent_record.categories:
                violations.append(ComplianceViolation.NO_CONSENT)
        
        # Check explicit consent for GDPR
        if framework == ComplianceFramework.GDPR and rules.get('explicit_consent', False):
            if consent_record and consent_record.consent_type not in [ConsentType.EXPLICIT, ConsentType.DOUBLE_OPT_IN]:
                violations.append(ComplianceViolation.NO_CONSENT)
        
        # Check sender identification
        if rules.get('sender_identification', False):
            if not sender_info or not sender_info.get('company_name'):
                violations.append(ComplianceViolation.MISSING_SENDER_INFO)
        
        # Check physical address (CAN-SPAM)
        if framework == ComplianceFramework.CAN_SPAM and rules.get('physical_address', False):
            if not sender_info or not sender_info.get('company_address'):
                violations.append(ComplianceViolation.MISSING_SENDER_INFO)
        
        # Check unsubscribe mechanism
        if rules.get('unsubscribe_required', True) and category_rules.get('unsubscribe_required', True):
            if not self._has_unsubscribe_mechanism(content):
                violations.append(ComplianceViolation.INVALID_UNSUBSCRIBE)
        
        # Check subject line (CAN-SPAM)
        if framework == ComplianceFramework.CAN_SPAM and subject:
            if self._is_deceptive_subject(subject, content):
                violations.append(ComplianceViolation.DECEPTIVE_SUBJECT)
        
        return violations

    async def _check_content_compliance(
        self,
        content: str,
        subject: Optional[str],
        category: NotificationCategory
    ) -> List[ComplianceViolation]:
        """Check content-specific compliance issues"""
        
        violations = []
        
        # Check for required unsubscribe link
        if category in [NotificationCategory.MARKETING, NotificationCategory.PROMOTIONAL]:
            if not self._has_unsubscribe_mechanism(content):
                violations.append(ComplianceViolation.INVALID_UNSUBSCRIBE)
        
        # Check for sender identification
        if not self._has_sender_identification(content):
            violations.append(ComplianceViolation.MISSING_SENDER_INFO)
        
        return violations

    def _has_unsubscribe_mechanism(self, content: str) -> bool:
        """Check if content contains unsubscribe mechanism"""
        unsubscribe_patterns = [
            r'unsubscribe',
            r'opt.?out',
            r'remove.?me',
            r'stop',
            r'désabonner',  # French
            r'abbestellen',  # German
            r'darse.?de.?baja'  # Spanish
        ]
        
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in unsubscribe_patterns)

    def _has_sender_identification(self, content: str) -> bool:
        """Check if content contains sender identification"""
        sender_patterns = [
            r'sent.?by',
            r'from:',
            r'company',
            r'organization',
            r'business'
        ]
        
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in sender_patterns)

    def _is_deceptive_subject(self, subject: str, content: str) -> bool:
        """Check if subject line is deceptive"""
        # Simple heuristic - check if subject contains misleading words
        misleading_words = [
            'free', 'urgent', 'winner', 'congratulations',
            'act now', 'limited time', 'exclusive'
        ]
        
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        # If subject contains promotional words but content doesn't, it might be deceptive
        subject_promotional = any(word in subject_lower for word in misleading_words)
        content_promotional = any(word in content_lower for word in misleading_words)
        
        return subject_promotional and not content_promotional

    async def record_user_consent(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        consent_type: ConsentType = ConsentType.OPT_IN,
        categories: List[NotificationCategory] = None,
        frameworks: List[ComplianceFramework] = None,
        source: str = "website",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_days: Optional[int] = None
    ) -> ConsentRecord:
        """Record user consent for compliance tracking"""
        
        if categories is None:
            categories = [NotificationCategory.MARKETING]
        
        if frameworks is None:
            frameworks = [ComplianceFramework.GDPR, ComplianceFramework.CAN_SPAM]
        
        # Calculate expiration date
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        consent_record = ConsentRecord(
            user_id=user_id,
            email=email,
            phone=phone,
            consent_type=consent_type,
            categories=categories,
            frameworks=frameworks,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            source=source,
            ip_address=ip_address,
            user_agent=user_agent,
            double_opt_in_confirmed=(consent_type == ConsentType.DOUBLE_OPT_IN)
        )
        
        # Store consent record
        self.consent_records[user_id] = consent_record
        await self._save_consent_record(consent_record)
        
        self.metrics['consent_records'] += 1
        
        self.logger.info(f"✅ Consent recorded for user {user_id}: {consent_type.value}")
        
        return consent_record

    async def process_unsubscribe_request(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        categories: List[NotificationCategory] = None,
        method: str = "email_link",
        ip_address: Optional[str] = None
    ) -> UnsubscribeRequest:
        """Process user unsubscribe request"""
        
        if categories is None:
            categories = list(NotificationCategory)  # Unsubscribe from all
        
        request_id = str(uuid.uuid4())
        
        unsubscribe_request = UnsubscribeRequest(
            id=request_id,
            user_id=user_id,
            email=email,
            phone=phone,
            categories=categories,
            method=method,
            requested_at=datetime.utcnow(),
            processed_at=None,
            confirmation_sent=False,
            ip_address=ip_address
        )
        
        # Process the unsubscribe
        await self._process_unsubscribe(unsubscribe_request)
        
        # Store request
        self.unsubscribe_requests[request_id] = unsubscribe_request
        await self._save_unsubscribe_request(unsubscribe_request)
        
        self.metrics['unsubscribe_requests'] += 1
        
        self.logger.info(f"✅ Unsubscribe processed for user {user_id}")
        
        return unsubscribe_request

    async def _process_unsubscribe(self, request: UnsubscribeRequest):
        """Process the actual unsubscribe"""
        
        # Update consent record
        consent_record = await self._get_user_consent(request.user_id, request.email, request.phone)
        
        if consent_record:
            # Remove categories from consent
            for category in request.categories:
                if category in consent_record.categories:
                    consent_record.categories.remove(category)
            
            # If no categories left, mark as withdrawn
            if not consent_record.categories:
                consent_record.withdrawn_at = datetime.utcnow()
                consent_record.withdrawal_method = request.method
            
            # Save updated consent
            await self._save_consent_record(consent_record)
        
        # Mark request as processed
        request.processed_at = datetime.utcnow()

    async def handle_gdpr_request(
        self,
        user_id: str,
        request_type: str,  # 'access', 'portability', 'deletion', 'rectification'
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle GDPR data subject requests"""
        
        self.metrics['gdpr_requests'] += 1
        
        if request_type == 'access':
            # Right to access personal data
            return await self._handle_data_access_request(user_id, email)
            
        elif request_type == 'portability':
            # Right to data portability
            return await self._handle_data_portability_request(user_id, email)
            
        elif request_type == 'deletion':
            # Right to be forgotten
            return await self._handle_data_deletion_request(user_id, email)
            
        elif request_type == 'rectification':
            # Right to rectification
            return await self._handle_data_rectification_request(user_id, email)
        
        else:
            return {'error': f'Unknown GDPR request type: {request_type}'}

    async def _handle_data_deletion_request(self, user_id: str, email: Optional[str]) -> Dict[str, Any]:
        """Handle right to be forgotten request"""
        
        self.metrics['data_deletions'] += 1
        
        try:
            # Delete consent records
            if user_id in self.consent_records:
                del self.consent_records[user_id]
            
            await self.redis_client.delete(f"consent:{user_id}")
            
            # Delete compliance checks
            await self.redis_client.delete(f"compliance_checks:{user_id}")
            
            # Delete unsubscribe requests
            keys_to_delete = []
            for req_id, request in self.unsubscribe_requests.items():
                if request.user_id == user_id:
                    keys_to_delete.append(req_id)
            
            for req_id in keys_to_delete:
                del self.unsubscribe_requests[req_id]
                await self.redis_client.delete(f"unsubscribe:{req_id}")
            
            self.logger.info(f"✅ Data deletion completed for user {user_id}")
            
            return {
                'status': 'completed',
                'user_id': user_id,
                'deleted_data': [
                    'consent_records',
                    'compliance_checks',
                    'unsubscribe_requests'
                ],
                'deletion_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data deletion failed for user {user_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _handle_data_access_request(self, user_id: str, email: Optional[str]) -> Dict[str, Any]:
        """Handle data access request"""
        
        data = {
            'user_id': user_id,
            'email': email,
            'consent_records': [],
            'compliance_checks': [],
            'unsubscribe_requests': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Get consent records
        consent_record = await self._get_user_consent(user_id, email, None)
        if consent_record:
            consent_dict = asdict(consent_record)
            consent_dict['granted_at'] = consent_record.granted_at.isoformat()
            if consent_record.expires_at:
                consent_dict['expires_at'] = consent_record.expires_at.isoformat()
            if consent_record.withdrawn_at:
                consent_dict['withdrawn_at'] = consent_record.withdrawn_at.isoformat()
            data['consent_records'].append(consent_dict)
        
        # Get compliance checks
        checks_data = await self.redis_client.lrange(f"compliance_checks:{user_id}", 0, -1)
        for check_json in checks_data:
            try:
                check = json.loads(check_json)
                data['compliance_checks'].append(check)
            except Exception:
                continue
        
        # Get unsubscribe requests
        for request in self.unsubscribe_requests.values():
            if request.user_id == user_id:
                request_dict = asdict(request)
                request_dict['requested_at'] = request.requested_at.isoformat()
                if request.processed_at:
                    request_dict['processed_at'] = request.processed_at.isoformat()
                data['unsubscribe_requests'].append(request_dict)
        
        return data

    async def add_compliance_footer(
        self,
        content: str,
        user_id: str,
        category: NotificationCategory,
        language: str = 'en',
        sender_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add compliance footer to notification content"""
        
        footer_parts = []
        
        # Add unsubscribe link for marketing content
        if category in [NotificationCategory.MARKETING, NotificationCategory.PROMOTIONAL]:
            unsubscribe_template = self.compliance_templates['unsubscribe_footer'].get(
                language, self.compliance_templates['unsubscribe_footer']['en']
            )
            unsubscribe_link = f"https://example.com/unsubscribe?user={user_id}&token={self._generate_unsubscribe_token(user_id)}"
            footer_parts.append(unsubscribe_template.format(unsubscribe_link=unsubscribe_link))
        
        # Add sender identification
        if sender_info:
            sender_template = self.compliance_templates['sender_identification'].get(
                language, self.compliance_templates['sender_identification']['en']
            )
            footer_parts.append(sender_template.format(**sender_info))
        
        # Combine content with footer
        if footer_parts:
            footer = '\n\n' + '\n'.join(footer_parts)
            return content + footer
        
        return content

    def _generate_unsubscribe_token(self, user_id: str) -> str:
        """Generate secure unsubscribe token"""
        data = f"{user_id}:{int(time.time())}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _get_user_consent(
        self,
        user_id: str,
        email: Optional[str],
        phone: Optional[str]
    ) -> Optional[ConsentRecord]:
        """Get user consent record"""
        
        # Check cache first
        if user_id in self.consent_records:
            return self.consent_records[user_id]
        
        # Load from Redis
        consent_data = await self.redis_client.get(f"consent:{user_id}")
        if consent_data:
            consent_dict = json.loads(consent_data)
            # Convert datetime strings back to datetime objects
            consent_dict['granted_at'] = datetime.fromisoformat(consent_dict['granted_at'])
            if consent_dict.get('expires_at'):
                consent_dict['expires_at'] = datetime.fromisoformat(consent_dict['expires_at'])
            if consent_dict.get('withdrawn_at'):
                consent_dict['withdrawn_at'] = datetime.fromisoformat(consent_dict['withdrawn_at'])
            
            # Convert enums
            consent_dict['consent_type'] = ConsentType(consent_dict['consent_type'])
            consent_dict['categories'] = [NotificationCategory(c) for c in consent_dict['categories']]
            consent_dict['frameworks'] = [ComplianceFramework(f) for f in consent_dict['frameworks']]
            
            consent_record = ConsentRecord(**consent_dict)
            self.consent_records[user_id] = consent_record
            return consent_record
        
        return None

    async def _save_consent_record(self, consent_record: ConsentRecord):
        """Save consent record to Redis"""
        try:
            consent_dict = asdict(consent_record)
            # Convert datetime objects to ISO strings
            consent_dict['granted_at'] = consent_record.granted_at.isoformat()
            if consent_record.expires_at:
                consent_dict['expires_at'] = consent_record.expires_at.isoformat()
            if consent_record.withdrawn_at:
                consent_dict['withdrawn_at'] = consent_record.withdrawn_at.isoformat()
            
            # Convert enums to strings
            consent_dict['consent_type'] = consent_record.consent_type.value
            consent_dict['categories'] = [c.value for c in consent_record.categories]
            consent_dict['frameworks'] = [f.value for f in consent_record.frameworks]
            
            await self.redis_client.setex(
                f"consent:{consent_record.user_id}",
                86400 * 1095,  # 3 years (GDPR requirement)
                json.dumps(consent_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to save consent record: {e}")

    async def _store_compliance_check(self, check: ComplianceCheck):
        """Store compliance check result"""
        try:
            check_dict = asdict(check)
            # Convert datetime and enums
            check_dict['checked_at'] = check.checked_at.isoformat()
            check_dict['violations'] = [v.value for v in check.violations]
            check_dict['frameworks_checked'] = [f.value for f in check.frameworks_checked]
            
            # Store in user-specific list
            await self.redis_client.lpush(
                f"compliance_checks:{check.user_id}",
                json.dumps(check_dict)
            )
            await self.redis_client.ltrim(f"compliance_checks:{check.user_id}", 0, 999)  # Keep last 1000
            
            # Store by notification ID
            await self.redis_client.setex(
                f"compliance_check:{check.notification_id}",
                86400 * 30,  # 30 days
                json.dumps(check_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to store compliance check: {e}")

    def _get_consent_status_string(self, consent_record: Optional[ConsentRecord]) -> str:
        """Get human-readable consent status"""
        if not consent_record:
            return "no_consent"
        
        if consent_record.withdrawn_at:
            return "withdrawn"
        
        if consent_record.expires_at and consent_record.expires_at < datetime.utcnow():
            return "expired"
        
        return f"active_{consent_record.consent_type.value}"

    def _calculate_risk_level(self, violations: List[ComplianceViolation]) -> str:
        """Calculate risk level based on violations"""
        
        if not violations:
            return "low"
        
        critical_violations = [
            ComplianceViolation.NO_CONSENT,
            ComplianceViolation.DATA_RETENTION,
            ComplianceViolation.CROSS_BORDER
        ]
        
        high_violations = [
            ComplianceViolation.EXPIRED_CONSENT,
            ComplianceViolation.DECEPTIVE_SUBJECT
        ]
        
        if any(v in critical_violations for v in violations):
            return "critical"
        elif any(v in high_violations for v in violations):
            return "high"
        elif len(violations) > 2:
            return "medium"
        else:
            return "low"

    def _generate_required_actions(
        self,
        violations: List[ComplianceViolation],
        category: NotificationCategory
    ) -> List[str]:
        """Generate required actions to resolve violations"""
        
        actions = []
        
        for violation in violations:
            if violation == ComplianceViolation.NO_CONSENT:
                actions.append("Obtain user consent before sending notifications")
            elif violation == ComplianceViolation.EXPIRED_CONSENT:
                actions.append("Renew expired user consent")
            elif violation == ComplianceViolation.INVALID_UNSUBSCRIBE:
                actions.append("Add clear unsubscribe mechanism to content")
            elif violation == ComplianceViolation.MISSING_SENDER_INFO:
                actions.append("Include sender identification and contact information")
            elif violation == ComplianceViolation.DECEPTIVE_SUBJECT:
                actions.append("Ensure subject line accurately reflects content")
        
        return list(set(actions))  # Remove duplicates

    async def get_compliance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate compliance report"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'metrics': self.metrics,
            'compliance_summary': {
                'total_checks': 0,
                'compliant_notifications': 0,
                'violation_breakdown': {},
                'framework_breakdown': {},
                'risk_level_breakdown': {}
            },
            'consent_analytics': {
                'active_consents': len(self.consent_records),
                'consent_type_breakdown': {},
                'expired_consents': 0,
                'withdrawn_consents': 0
            },
            'recommendations': []
        }
        
        # Analyze consent records
        for consent_record in self.consent_records.values():
            consent_type = consent_record.consent_type.value
            report['consent_analytics']['consent_type_breakdown'][consent_type] = \
                report['consent_analytics']['consent_type_breakdown'].get(consent_type, 0) + 1
            
            if consent_record.withdrawn_at:
                report['consent_analytics']['withdrawn_consents'] += 1
            elif consent_record.expires_at and consent_record.expires_at < datetime.utcnow():
                report['consent_analytics']['expired_consents'] += 1
        
        # Generate recommendations
        if report['consent_analytics']['expired_consents'] > 0:
            report['recommendations'].append("Review and renew expired consent records")
        
        if self.metrics['violations_detected'] > self.metrics['compliance_checks'] * 0.1:
            report['recommendations'].append("High violation rate detected - review notification processes")
        
        return report

    async def get_metrics(self) -> Dict[str, Any]:
        """Get compliance manager metrics"""
        
        return {
            **self.metrics,
            'consent_records_cached': len(self.consent_records),
            'unsubscribe_requests_cached': len(self.unsubscribe_requests),
            'supported_frameworks': len(ComplianceFramework),
            'supported_languages': len(self.compliance_templates['unsubscribe_footer']),
            'compliance_rules_configured': len(self.compliance_rules)
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("✅ Compliance manager cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_compliance_manager():
        """Test compliance manager functionality"""
        
        # Initialize manager
        manager = NotificationComplianceManager()
        await manager.initialize()
        
        # Record consent
        consent = await manager.record_user_consent(
            user_id="user123",
            email="user@example.com",
            consent_type=ConsentType.DOUBLE_OPT_IN,
            categories=[NotificationCategory.MARKETING],
            frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CAN_SPAM],
            source="website_signup"
        )
        print(f"Consent recorded: {consent.user_id} - {consent.consent_type.value}")
        
        # Check compliance
        check = await manager.check_notification_compliance(
            notification_id="notif_456",
            user_id="user123",
            recipient_email="user@example.com",
            category=NotificationCategory.MARKETING,
            content="Check out our new features! Click here to unsubscribe.",
            subject="New Features Available",
            user_location="Germany"
        )
        
        print(f"\nCompliance check:")
        print(f"- Compliant: {check.is_compliant}")
        print(f"- Violations: {[v.value for v in check.violations]}")
        print(f"- Risk level: {check.risk_level}")
        print(f"- Required actions: {check.required_actions}")
        
        # Test unsubscribe
        unsubscribe = await manager.process_unsubscribe_request(
            user_id="user123",
            email="user@example.com",
            categories=[NotificationCategory.MARKETING],
            method="email_link"
        )
        print(f"\nUnsubscribe processed: {unsubscribe.id}")
        
        # Add compliance footer
        original_content = "You have a new message waiting!"
        compliant_content = await manager.add_compliance_footer(
            content=original_content,
            user_id="user123",
            category=NotificationCategory.MARKETING,
            sender_info={"company_name": "Ainflue", "company_address": "123 Tech St, City"}
        )
        print(f"\nOriginal: {original_content}")
        print(f"With footer: {compliant_content}")
        
        # Generate report
        report = await manager.get_compliance_report(days=30)
        print(f"\nCompliance report: {json.dumps(report, indent=2)}")
        
        # Get metrics
        metrics = await manager.get_metrics()
        print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
        
        await manager.cleanup()
    
    # Run test
    asyncio.run(test_compliance_manager())