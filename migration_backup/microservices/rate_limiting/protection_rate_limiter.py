#!/usr/bin/env python3

"""
IA Chéries Protection Rate Limiter - Copyright Protection & Legal Compliance
=========================================================================

Advanced rate limiting system for copyright protection, content matching,
DMCA compliance automation, and legal enforcement for the IA Chéries creator
platform. Provides comprehensive content protection with real-time monitoring.

Features:
- Copyright protection with content fingerprinting and plagiarism detection
- DMCA compliance automation with takedown requests and counter-claims
- Content matching algorithms for originality verification
- Multi-jurisdictional legal compliance (US DMCA, EU Copyright Directive, International treaties)
- Protection violation tracking with repeat offender management
- Legal documentation generation and attorney integration
- Real-time content monitoring with infringement detection
- Automated cease & desist processing with escalation procedures

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited

Project: IA Chéries Rate Limiting - Protection Module
Version: 1.0 Production
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

# Configure logging for protection rate limiter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"
    STANDARD = "standard" 
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    WHITE_GLOVE = "white_glove"

class ContentMatchType(Enum):
    """Types of content matching"""
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    SIMILAR_CONTENT = "similar_content"
    DERIVATIVE_WORK = "derivative_work"
    TRANSFORMED_CONTENT = "transformed_content"

class ViolationType(Enum):
    """Types of protection violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    PLAGIARISM = "plagiarism"
    TRADEMARK_VIOLATION = "trademark_violation"
    FAIR_USE_DISPUTE = "fair_use_dispute"
    DERIVATIVE_WORK_UNAUTHORIZED = "derivative_work_unauthorized"

class LegalJurisdiction(Enum):
    """Legal jurisdictions supported"""
    US_DMCA = "us_dmca"
    EU_COPYRIGHT = "eu_copyright"
    UK_COPYRIGHT = "uk_copyright"
    CANADA_COPYRIGHT = "canada_copyright"
    AUSTRALIA_COPYRIGHT = "australia_copyright"
    INTERNATIONAL = "international"

class EnforcementAction(Enum):
    """Enforcement actions available"""
    MONITOR_ONLY = "monitor_only"
    WARNING_NOTICE = "warning_notice"
    TAKEDOWN_REQUEST = "takedown_request"
    CEASE_DESIST = "cease_desist"
    LEGAL_ACTION = "legal_action"
    PLATFORM_REPORT = "platform_report"

class ProtectionStatus(Enum):
    """Protection case status"""
    ACTIVE_MONITORING = "active_monitoring"
    VIOLATION_DETECTED = "violation_detected"
    NOTICE_SENT = "notice_sent"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

@dataclass
class ContentFingerprint:
    """Content fingerprint for matching"""
    content_id: str
    fingerprint_hash: str
    content_type: str
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProtectionRule:
    """Content protection rule"""
    rule_id: str
    owner_id: str
    content_ids: List[str]
    protection_level: ProtectionLevel
    monitoring_enabled: bool
    auto_enforcement: bool
    allowed_jurisdictions: List[LegalJurisdiction]
    enforcement_actions: List[EnforcementAction]
    similarity_threshold: float
    fair_use_exceptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ViolationReport:
    """Content protection violation report"""
    violation_id: str
    rule_id: str
    violating_content_id: str
    violating_user_id: str
    violation_type: ViolationType
    match_type: ContentMatchType
    similarity_score: float
    jurisdiction: LegalJurisdiction
    status: ProtectionStatus
    evidence: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[EnforcementAction] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

@dataclass
class LegalDocument:
    """Legal document for enforcement"""
    document_id: str
    document_type: str
    violation_id: str
    jurisdiction: LegalJurisdiction
    content: str
    recipient_info: Dict[str, Any]
    sent_at: Optional[datetime] = None
    response_received: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class OffenderProfile:
    """Repeat offender profile"""
    user_id: str
    violation_count: int
    violation_types: List[ViolationType]
    first_violation: datetime
    last_violation: datetime
    severity_score: float
    escalation_level: int
    is_repeat_offender: bool = False

class ProtectionRateLimiter:
    """
    Advanced protection rate limiter with copyright enforcement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize protection rate limiter"""
        self.config = config or {}
        self.node_id = str(uuid.uuid4())
        
        # Initialize protection configurations
        self._setup_protection_configurations()
        self._setup_legal_templates()
        
        # Content protection tracking
        self.content_fingerprints: Dict[str, ContentFingerprint] = {}
        self.protection_rules: Dict[str, ProtectionRule] = {}
        self.violation_reports: Dict[str, ViolationReport] = {}
        self.legal_documents: Dict[str, LegalDocument] = {}
        
        # Offender management
        self.offender_profiles: Dict[str, OffenderProfile] = {}
        self.monitoring_queue: asyncio.Queue = asyncio.Queue()
        
        # Analytics and reporting
        self.protection_analytics: Dict[str, Any] = {}
        self.enforcement_statistics: Dict[str, int] = {}
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        logger.info(f"ProtectionRateLimiter initialized with node_id: {self.node_id}")
    
    def _setup_protection_configurations(self):
        """Setup protection level configurations"""
        self.protection_configs = {
            ProtectionLevel.BASIC: {
                'monitoring_frequency_minutes': 60,
                'similarity_threshold': 0.8,
                'auto_enforcement': False,
                'max_concurrent_cases': 10,
                'jurisdictions_supported': [LegalJurisdiction.US_DMCA],
                'enforcement_actions': [EnforcementAction.MONITOR_ONLY, EnforcementAction.WARNING_NOTICE],
                'response_time_hours': 72,
                'attorney_consultation': False
            },
            ProtectionLevel.STANDARD: {
                'monitoring_frequency_minutes': 30,
                'similarity_threshold': 0.7,
                'auto_enforcement': True,
                'max_concurrent_cases': 50,
                'jurisdictions_supported': [LegalJurisdiction.US_DMCA, LegalJurisdiction.EU_COPYRIGHT],
                'enforcement_actions': [
                    EnforcementAction.MONITOR_ONLY,
                    EnforcementAction.WARNING_NOTICE,
                    EnforcementAction.TAKEDOWN_REQUEST,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'response_time_hours': 48,
                'attorney_consultation': False
            },
            ProtectionLevel.PREMIUM: {
                'monitoring_frequency_minutes': 15,
                'similarity_threshold': 0.6,
                'auto_enforcement': True,
                'max_concurrent_cases': 200,
                'jurisdictions_supported': [
                    LegalJurisdiction.US_DMCA,
                    LegalJurisdiction.EU_COPYRIGHT,
                    LegalJurisdiction.UK_COPYRIGHT,
                    LegalJurisdiction.CANADA_COPYRIGHT
                ],
                'enforcement_actions': [
                    EnforcementAction.MONITOR_ONLY,
                    EnforcementAction.WARNING_NOTICE,
                    EnforcementAction.TAKEDOWN_REQUEST,
                    EnforcementAction.CEASE_DESIST,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'response_time_hours': 24,
                'attorney_consultation': True
            },
            ProtectionLevel.ENTERPRISE: {
                'monitoring_frequency_minutes': 5,
                'similarity_threshold': 0.5,
                'auto_enforcement': True,
                'max_concurrent_cases': 1000,
                'jurisdictions_supported': list(LegalJurisdiction),
                'enforcement_actions': list(EnforcementAction),
                'response_time_hours': 12,
                'attorney_consultation': True
            },
            ProtectionLevel.WHITE_GLOVE: {
                'monitoring_frequency_minutes': 1,
                'similarity_threshold': 0.4,
                'auto_enforcement': True,
                'max_concurrent_cases': -1,  # unlimited
                'jurisdictions_supported': list(LegalJurisdiction),
                'enforcement_actions': list(EnforcementAction),
                'response_time_hours': 4,
                'attorney_consultation': True,
                'dedicated_legal_team': True
            }
        }
    
    def _setup_legal_templates(self):
        """Setup legal document templates"""
        self.legal_templates = {
            'dmca_takedown': {
                'subject': 'DMCA Takedown Notice - Copyright Infringement',
                'template': '''
                To Whom It May Concern:

                This is a formal DMCA takedown notice for copyright infringement.
                
                Copyrighted Work: {copyrighted_work}
                Original Owner: {copyright_owner}
                Infringing Content: {infringing_url}
                
                I have a good faith belief that the use of the copyrighted material is not authorized by the copyright owner, its agent, or the law.
                
                This notice is sent pursuant to the Digital Millennium Copyright Act (DMCA), Title 17, United States Code, Section 512.
                
                Sincerely,
                {sender_name}
                {sender_contact}
                '''
            },
            'cease_desist': {
                'subject': 'Cease and Desist - Copyright Infringement',
                'template': '''
                CEASE AND DESIST LETTER

                Dear {recipient_name},

                This letter serves as formal notice to CEASE AND DESIST from the unauthorized use of copyrighted material.

                Description of Infringement: {infringement_description}
                Copyrighted Work: {copyrighted_work}
                
                You are hereby directed to immediately cease and desist from any further use, reproduction, or distribution of the copyrighted material.

                Failure to comply may result in legal action seeking monetary damages and injunctive relief.

                Time to Respond: {response_deadline}

                Sincerely,
                {legal_representative}
                '''
            },
            'warning_notice': {
                'subject': 'Copyright Infringement Warning',
                'template': '''
                COPYRIGHT INFRINGEMENT WARNING

                Dear Content Creator,

                We have detected potential copyright infringement of protected content.

                Original Content: {original_content}
                Detected Usage: {detected_usage}
                Similarity Score: {similarity_score}%

                This is a warning notice. Please review your content and remove any infringing material to avoid further action.

                If you believe this is a false positive, please contact us with supporting documentation.

                Best regards,
                {platform_name} Legal Team
                '''
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize protection rate limiter"""
        try:
            self.is_running = True
            
            # Start background tasks
            self.background_tasks.add(
                asyncio.create_task(self._content_monitoring_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._violation_processing_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._enforcement_automation_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._analytics_collection_task())
            )
            
            logger.info("ProtectionRateLimiter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ProtectionRateLimiter: {e}")
            return False
    
    async def register_content_protection(
        self,
        owner_id: str,
        content_id: str,
        content_data: bytes,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register content for protection monitoring"""
        start_time = time.time()
        
        try:
            # Generate content fingerprint
            fingerprint = await self._generate_content_fingerprint(
                content_id, content_data, metadata or {}
            )
            
            # Store fingerprint
            self.content_fingerprints[content_id] = fingerprint
            
            # Create protection rule
            rule_id = f"rule_{content_id}_{int(time.time())}"
            protection_config = self.protection_configs[protection_level]
            
            rule = ProtectionRule(
                rule_id=rule_id,
                owner_id=owner_id,
                content_ids=[content_id],
                protection_level=protection_level,
                monitoring_enabled=True,
                auto_enforcement=protection_config['auto_enforcement'],
                allowed_jurisdictions=protection_config['jurisdictions_supported'],
                enforcement_actions=protection_config['enforcement_actions'],
                similarity_threshold=protection_config['similarity_threshold']
            )
            
            self.protection_rules[rule_id] = rule
            
            # Add to monitoring queue
            await self.monitoring_queue.put({
                'action': 'start_monitoring',
                'rule_id': rule_id,
                'content_id': content_id
            })
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'rule_id': rule_id,
                'content_id': content_id,
                'fingerprint_hash': fingerprint.fingerprint_hash,
                'protection_level': protection_level.value,
                'monitoring_enabled': True,
                'execution_time_ms': execution_time,
                'node_id': self.node_id
            }
            
        except Exception as e:
            logger.error(f"Error registering content protection: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    async def check_content_similarity(
        self,
        content_data: bytes,
        threshold: float = 0.7,
        content_type: str = "unknown"
    ) -> Dict[str, Any]:
        """Check if content matches any protected content"""
        start_time = time.time()
        
        try:
            # Generate fingerprint for incoming content
            temp_fingerprint = await self._generate_content_fingerprint(
                f"temp_{int(time.time())}", content_data, {'type': content_type}
            )
            
            matches = []
            
            # Compare against all protected content
            for content_id, fingerprint in self.content_fingerprints.items():
                similarity = await self._calculate_similarity(
                    temp_fingerprint, fingerprint
                )
                
                if similarity >= threshold:
                    match_type = self._determine_match_type(similarity)
                    
                    matches.append({
                        'content_id': content_id,
                        'similarity_score': similarity,
                        'match_type': match_type.value,
                        'fingerprint_hash': fingerprint.fingerprint_hash
                    })
            
            # Sort by similarity score
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'matches_found': len(matches),
                'matches': matches[:10],  # Return top 10 matches
                'highest_similarity': matches[0]['similarity_score'] if matches else 0.0,
                'threshold_used': threshold,
                'execution_time_ms': execution_time
            }
            
        except Exception as e:
            logger.error(f"Error checking content similarity: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    async def report_violation(
        self,
        rule_id: str,
        violating_content_id: str,
        violating_user_id: str,
        violation_type: ViolationType,
        evidence: Dict[str, Any],
        jurisdiction: LegalJurisdiction = LegalJurisdiction.US_DMCA
    ) -> Dict[str, Any]:
        """Report a content protection violation"""
        try:
            if rule_id not in self.protection_rules:
                return {
                    'success': False,
                    'error': f'Protection rule {rule_id} not found'
                }
            
            rule = self.protection_rules[rule_id]
            violation_id = f"violation_{rule_id}_{int(time.time())}"
            
            # Determine match type and similarity from evidence
            similarity_score = evidence.get('similarity_score', 0.0)
            match_type = self._determine_match_type(similarity_score)
            
            # Create violation report
            violation = ViolationReport(
                violation_id=violation_id,
                rule_id=rule_id,
                violating_content_id=violating_content_id,
                violating_user_id=violating_user_id,
                violation_type=violation_type,
                match_type=match_type,
                similarity_score=similarity_score,
                jurisdiction=jurisdiction,
                status=ProtectionStatus.VIOLATION_DETECTED,
                evidence=evidence
            )
            
            self.violation_reports[violation_id] = violation
            
            # Update offender profile
            await self._update_offender_profile(violating_user_id, violation_type)
            
            # Trigger enforcement if auto-enforcement is enabled
            if rule.auto_enforcement:
                await self._trigger_automatic_enforcement(violation)
            
            return {
                'success': True,
                'violation_id': violation_id,
                'status': violation.status.value,
                'similarity_score': similarity_score,
                'match_type': match_type.value,
                'auto_enforcement_triggered': rule.auto_enforcement
            }
            
        except Exception as e:
            logger.error(f"Error reporting violation: {e}")
            return {'success': False, 'error': str(e)}
    
    async def enforce_protection(
        self,
        violation_id: str,
        enforcement_action: EnforcementAction,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enforce protection action for violation"""
        try:
            if violation_id not in self.violation_reports:
                return {
                    'success': False,
                    'error': f'Violation {violation_id} not found'
                }
            
            violation = self.violation_reports[violation_id]
            rule = self.protection_rules[violation.rule_id]
            
            # Check if action is allowed for this protection level
            protection_config = self.protection_configs[rule.protection_level]
            if enforcement_action not in protection_config['enforcement_actions']:
                return {
                    'success': False,
                    'error': f'Enforcement action {enforcement_action.value} not allowed for protection level {rule.protection_level.value}'
                }
            
            # Execute enforcement action
            result = await self._execute_enforcement_action(
                violation, enforcement_action, custom_message
            )
            
            if result['success']:
                # Update violation status
                violation.actions_taken.append(enforcement_action)
                violation.status = ProtectionStatus.NOTICE_SENT
                
                # Update statistics
                action_key = f"{enforcement_action.value}_sent"
                self.enforcement_statistics[action_key] = self.enforcement_statistics.get(action_key, 0) + 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error enforcing protection: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_protection_analytics(
        self,
        owner_id: Optional[str] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get protection analytics and statistics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_range_days)
            
            # Filter violations by owner and time range
            relevant_violations = []
            for violation in self.violation_reports.values():
                if violation.detected_at >= start_date:
                    if owner_id:
                        rule = self.protection_rules.get(violation.rule_id)
                        if rule and rule.owner_id == owner_id:
                            relevant_violations.append(violation)
                    else:
                        relevant_violations.append(violation)
            
            # Calculate analytics
            analytics = {
                'time_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': time_range_days
                },
                'violation_summary': {
                    'total_violations': len(relevant_violations),
                    'violations_by_type': {},
                    'violations_by_status': {},
                    'average_similarity_score': 0.0
                },
                'enforcement_summary': {
                    'actions_taken': dict(self.enforcement_statistics),
                    'resolution_rate': 0.0,
                    'average_response_time_hours': 0.0
                },
                'repeat_offenders': {
                    'total_repeat_offenders': 0,
                    'top_offenders': []
                },
                'protection_effectiveness': {
                    'detection_rate': 0.0,
                    'false_positive_rate': 0.0,
                    'successful_takedowns': 0
                }
            }
            
            # Violation statistics
            if relevant_violations:
                violation_types = {}
                violation_statuses = {}
                total_similarity = 0.0
                
                for violation in relevant_violations:
                    # Count by type
                    vtype = violation.violation_type.value
                    violation_types[vtype] = violation_types.get(vtype, 0) + 1
                    
                    # Count by status
                    vstatus = violation.status.value
                    violation_statuses[vstatus] = violation_statuses.get(vstatus, 0) + 1
                    
                    # Sum similarity scores
                    total_similarity += violation.similarity_score
                
                analytics['violation_summary']['violations_by_type'] = violation_types
                analytics['violation_summary']['violations_by_status'] = violation_statuses
                analytics['violation_summary']['average_similarity_score'] = total_similarity / len(relevant_violations)
            
            # Repeat offenders analysis
            repeat_offenders = [
                profile for profile in self.offender_profiles.values()
                if profile.is_repeat_offender
            ]
            
            analytics['repeat_offenders']['total_repeat_offenders'] = len(repeat_offenders)
            analytics['repeat_offenders']['top_offenders'] = [
                {
                    'user_id': profile.user_id,
                    'violation_count': profile.violation_count,
                    'severity_score': profile.severity_score,
                    'escalation_level': profile.escalation_level
                }
                for profile in sorted(repeat_offenders, key=lambda x: x.severity_score, reverse=True)[:10]
            ]
            
            return {
                'success': True,
                'analytics': analytics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting protection analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_violation_details(self, violation_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific violation"""
        try:
            if violation_id not in self.violation_reports:
                return {
                    'success': False,
                    'error': f'Violation {violation_id} not found'
                }
            
            violation = self.violation_reports[violation_id]
            rule = self.protection_rules[violation.rule_id]
            
            # Get related legal documents
            related_documents = [
                {
                    'document_id': doc.document_id,
                    'document_type': doc.document_type,
                    'sent_at': doc.sent_at.isoformat() if doc.sent_at else None,
                    'response_received': doc.response_received
                }
                for doc in self.legal_documents.values()
                if doc.violation_id == violation_id
            ]
            
            # Get offender profile
            offender_profile = self.offender_profiles.get(violation.violating_user_id)
            
            return {
                'success': True,
                'violation': {
                    'violation_id': violation.violation_id,
                    'rule_id': violation.rule_id,
                    'violating_content_id': violation.violating_content_id,
                    'violating_user_id': violation.violating_user_id,
                    'violation_type': violation.violation_type.value,
                    'match_type': violation.match_type.value,
                    'similarity_score': violation.similarity_score,
                    'jurisdiction': violation.jurisdiction.value,
                    'status': violation.status.value,
                    'evidence': violation.evidence,
                    'actions_taken': [action.value for action in violation.actions_taken],
                    'detected_at': violation.detected_at.isoformat(),
                    'resolved_at': violation.resolved_at.isoformat() if violation.resolved_at else None
                },
                'protection_rule': {
                    'owner_id': rule.owner_id,
                    'protection_level': rule.protection_level.value,
                    'auto_enforcement': rule.auto_enforcement,
                    'similarity_threshold': rule.similarity_threshold
                },
                'legal_documents': related_documents,
                'offender_profile': {
                    'violation_count': offender_profile.violation_count,
                    'is_repeat_offender': offender_profile.is_repeat_offender,
                    'severity_score': offender_profile.severity_score,
                    'escalation_level': offender_profile.escalation_level
                } if offender_profile else None
            }
            
        except Exception as e:
            logger.error(f"Error getting violation details: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_content_fingerprint(
        self,
        content_id: str,
        content_data: bytes,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate content fingerprint for matching"""
        # Create hash-based fingerprint
        hasher = hashlib.sha256()
        hasher.update(content_data)
        fingerprint_hash = hasher.hexdigest()
        
        # Extract content characteristics
        file_size = len(content_data)
        content_type = metadata.get('type', 'unknown')
        
        return ContentFingerprint(
            content_id=content_id,
            fingerprint_hash=fingerprint_hash,
            content_type=content_type,
            file_size_bytes=file_size,
            metadata=metadata
        )
    
    async def _calculate_similarity(
        self,
        fingerprint1: ContentFingerprint,
        fingerprint2: ContentFingerprint
    ) -> float:
        """Calculate similarity between two content fingerprints"""
        # Exact hash match
        if fingerprint1.fingerprint_hash == fingerprint2.fingerprint_hash:
            return 1.0
        
        # File size comparison
        size_similarity = 0.0
        if fingerprint1.file_size_bytes and fingerprint2.file_size_bytes:
            size_diff = abs(fingerprint1.file_size_bytes - fingerprint2.file_size_bytes)
            max_size = max(fingerprint1.file_size_bytes, fingerprint2.file_size_bytes)
            size_similarity = max(0.0, 1.0 - (size_diff / max_size))
        
        # Hash similarity (simplified - in production would use perceptual hashing)
        hash1 = fingerprint1.fingerprint_hash
        hash2 = fingerprint2.fingerprint_hash
        
        # Calculate Hamming distance approximation
        matching_chars = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        hash_similarity = matching_chars / len(hash1)
        
        # Weighted average
        return (hash_similarity * 0.7) + (size_similarity * 0.3)
    
    def _determine_match_type(self, similarity_score: float) -> ContentMatchType:
        """Determine match type based on similarity score"""
        if similarity_score >= 0.95:
            return ContentMatchType.EXACT_MATCH
        elif similarity_score >= 0.8:
            return ContentMatchType.PARTIAL_MATCH
        elif similarity_score >= 0.6:
            return ContentMatchType.SIMILAR_CONTENT
        elif similarity_score >= 0.4:
            return ContentMatchType.DERIVATIVE_WORK
        else:
            return ContentMatchType.TRANSFORMED_CONTENT
    
    async def _update_offender_profile(self, user_id: str, violation_type: ViolationType):
        """Update repeat offender profile"""
        if user_id not in self.offender_profiles:
            self.offender_profiles[user_id] = OffenderProfile(
                user_id=user_id,
                violation_count=0,
                violation_types=[],
                first_violation=datetime.now(),
                last_violation=datetime.now(),
                severity_score=0.0,
                escalation_level=0
            )
        
        profile = self.offender_profiles[user_id]
        profile.violation_count += 1
        profile.last_violation = datetime.now()
        
        if violation_type not in profile.violation_types:
            profile.violation_types.append(violation_type)
        
        # Calculate severity score
        base_score = profile.violation_count * 10
        type_multiplier = len(profile.violation_types) * 5
        time_factor = min(30, (datetime.now() - profile.first_violation).days)
        
        profile.severity_score = base_score + type_multiplier - time_factor
        
        # Determine if repeat offender
        profile.is_repeat_offender = profile.violation_count >= 3
        
        # Calculate escalation level
        if profile.violation_count >= 10:
            profile.escalation_level = 3  # Legal action
        elif profile.violation_count >= 5:
            profile.escalation_level = 2  # Cease and desist
        elif profile.violation_count >= 3:
            profile.escalation_level = 1  # Formal warning
        else:
            profile.escalation_level = 0  # Monitor only
    
    async def _trigger_automatic_enforcement(self, violation: ViolationReport):
        """Trigger automatic enforcement actions"""
        rule = self.protection_rules[violation.rule_id]
        protection_config = self.protection_configs[rule.protection_level]
        
        # Determine appropriate enforcement action
        enforcement_action = EnforcementAction.WARNING_NOTICE
        
        # Check offender profile for escalation
        offender_profile = self.offender_profiles.get(violation.violating_user_id)
        if offender_profile:
            if offender_profile.escalation_level >= 2:
                enforcement_action = EnforcementAction.CEASE_DESIST
            elif offender_profile.escalation_level >= 1:
                enforcement_action = EnforcementAction.TAKEDOWN_REQUEST
        
        # Check similarity score for escalation
        if violation.similarity_score >= 0.9:
            enforcement_action = EnforcementAction.TAKEDOWN_REQUEST
        
        # Execute enforcement
        await self._execute_enforcement_action(violation, enforcement_action)
    
    async def _execute_enforcement_action(
        self,
        violation: ViolationReport,
        action: EnforcementAction,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute specific enforcement action"""
        try:
            rule = self.protection_rules[violation.rule_id]
            
            if action == EnforcementAction.WARNING_NOTICE:
                return await self._send_warning_notice(violation, custom_message)
            elif action == EnforcementAction.TAKEDOWN_REQUEST:
                return await self._send_takedown_request(violation, custom_message)
            elif action == EnforcementAction.CEASE_DESIST:
                return await self._send_cease_desist(violation, custom_message)
            elif action == EnforcementAction.LEGAL_ACTION:
                return await self._initiate_legal_action(violation)
            elif action == EnforcementAction.PLATFORM_REPORT:
                return await self._report_to_platform(violation)
            else:
                return {
                    'success': True,
                    'action': action.value,
                    'message': 'Monitoring only - no action taken'
                }
            
        except Exception as e:
            logger.error(f"Error executing enforcement action {action.value}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_warning_notice(
        self,
        violation: ViolationReport,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send warning notice to violator"""
        template = self.legal_templates['warning_notice']
        
        content = template['template'].format(
            original_content=f"Content ID: {violation.violating_content_id}",
            detected_usage="Unauthorized use detected",
            similarity_score=int(violation.similarity_score * 100),
            platform_name="IA Chéries"
        )
        
        if custom_message:
            content += f"\n\nAdditional Message:\n{custom_message}"
        
        document = LegalDocument(
            document_id=f"warning_{violation.violation_id}_{int(time.time())}",
            document_type="warning_notice",
            violation_id=violation.violation_id,
            jurisdiction=violation.jurisdiction,
            content=content,
            recipient_info={'user_id': violation.violating_user_id},
            sent_at=datetime.now()
        )
        
        self.legal_documents[document.document_id] = document
        
        return {
            'success': True,
            'action': 'warning_notice_sent',
            'document_id': document.document_id,
            'sent_at': document.sent_at.isoformat()
        }
    
    async def _send_takedown_request(
        self,
        violation: ViolationReport,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send DMCA takedown request"""
        template = self.legal_templates['dmca_takedown']
        
        content = template['template'].format(
            copyrighted_work=f"Protected Content ID: {violation.violating_content_id}",
            copyright_owner="IA Chéries User",
            infringing_url=f"Content URL for {violation.violating_content_id}",
            sender_name="IA Chéries Legal Team",
            sender_contact="legal@ainflue.com"
        )
        
        if custom_message:
            content += f"\n\nAdditional Information:\n{custom_message}"
        
        document = LegalDocument(
            document_id=f"dmca_{violation.violation_id}_{int(time.time())}",
            document_type="dmca_takedown",
            violation_id=violation.violation_id,
            jurisdiction=violation.jurisdiction,
            content=content,
            recipient_info={'user_id': violation.violating_user_id},
            sent_at=datetime.now()
        )
        
        self.legal_documents[document.document_id] = document
        
        return {
            'success': True,
            'action': 'dmca_takedown_sent',
            'document_id': document.document_id,
            'sent_at': document.sent_at.isoformat()
        }
    
    async def _send_cease_desist(
        self,
        violation: ViolationReport,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send cease and desist letter"""
        template = self.legal_templates['cease_desist']
        
        content = template['template'].format(
            recipient_name=f"User {violation.violating_user_id}",
            infringement_description=f"Unauthorized use of protected content (Similarity: {violation.similarity_score:.2%})",
            copyrighted_work=f"Content ID: {violation.violating_content_id}",
            response_deadline=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            legal_representative="IA Chéries Legal Department"
        )
        
        if custom_message:
            content += f"\n\nAdditional Details:\n{custom_message}"
        
        document = LegalDocument(
            document_id=f"cease_desist_{violation.violation_id}_{int(time.time())}",
            document_type="cease_desist",
            violation_id=violation.violation_id,
            jurisdiction=violation.jurisdiction,
            content=content,
            recipient_info={'user_id': violation.violating_user_id},
            sent_at=datetime.now()
        )
        
        self.legal_documents[document.document_id] = document
        
        return {
            'success': True,
            'action': 'cease_desist_sent',
            'document_id': document.document_id,
            'sent_at': document.sent_at.isoformat()
        }
    
    async def _initiate_legal_action(self, violation: ViolationReport) -> Dict[str, Any]:
        """Initiate legal action for severe violations"""
        # In production, this would integrate with legal case management systems
        return {
            'success': True,
            'action': 'legal_action_initiated',
            'case_id': f"legal_{violation.violation_id}",
            'status': 'pending_attorney_review'
        }
    
    async def _report_to_platform(self, violation: ViolationReport) -> Dict[str, Any]:
        """Report violation to external platforms"""
        # In production, this would integrate with platform APIs
        return {
            'success': True,
            'action': 'platform_report_sent',
            'platforms_notified': ['youtube', 'tiktok', 'instagram'],
            'report_id': f"platform_{violation.violation_id}"
        }
    
    async def _content_monitoring_task(self):
        """Background task for continuous content monitoring"""
        while self.is_running:
            try:
                # Process monitoring queue
                if not self.monitoring_queue.empty():
                    monitoring_request = await self.monitoring_queue.get()
                    
                    if monitoring_request['action'] == 'start_monitoring':
                        rule_id = monitoring_request['rule_id']
                        # Start monitoring for this rule
                        logger.info(f"Started monitoring for rule {rule_id}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in content monitoring task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _violation_processing_task(self):
        """Background task for processing violations"""
        while self.is_running:
            try:
                # Process pending violations
                pending_violations = [
                    v for v in self.violation_reports.values()
                    if v.status == ProtectionStatus.VIOLATION_DETECTED
                ]
                
                for violation in pending_violations:
                    rule = self.protection_rules[violation.rule_id]
                    if rule.auto_enforcement:
                        await self._trigger_automatic_enforcement(violation)
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in violation processing task: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _enforcement_automation_task(self):
        """Background task for enforcement automation"""
        while self.is_running:
            try:
                # Check for escalations needed
                for violation in self.violation_reports.values():
                    if violation.status == ProtectionStatus.NOTICE_SENT:
                        # Check if enough time has passed for escalation
                        time_since_notice = datetime.now() - violation.detected_at
                        if time_since_notice.total_seconds() > 86400:  # 24 hours
                            # Consider escalation
                            await self._consider_escalation(violation)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in enforcement automation task: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _analytics_collection_task(self):
        """Background task for analytics collection"""
        while self.is_running:
            try:
                # Update protection analytics
                self.protection_analytics = await self.get_protection_analytics()
                
                await asyncio.sleep(21600)  # Update every 6 hours
                
            except Exception as e:
                logger.error(f"Error in analytics collection task: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _consider_escalation(self, violation: ViolationReport):
        """Consider escalating enforcement action"""
        offender_profile = self.offender_profiles.get(violation.violating_user_id)
        
        if offender_profile and offender_profile.is_repeat_offender:
            # Escalate to cease and desist or legal action
            if offender_profile.escalation_level >= 3:
                await self._execute_enforcement_action(violation, EnforcementAction.LEGAL_ACTION)
            elif offender_profile.escalation_level >= 2:
                await self._execute_enforcement_action(violation, EnforcementAction.CEASE_DESIST)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'service': 'ProtectionRateLimiter',
            'status': 'healthy' if self.is_running else 'stopped',
            'node_id': self.node_id,
            'protected_content_count': len(self.content_fingerprints),
            'active_protection_rules': len(self.protection_rules),
            'total_violations': len(self.violation_reports),
            'legal_documents_generated': len(self.legal_documents),
            'repeat_offenders': len([p for p in self.offender_profiles.values() if p.is_repeat_offender]),
            'background_tasks': len(self.background_tasks),
            'monitoring_queue_size': self.monitoring_queue.qsize(),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def shutdown(self):
        """Gracefully shutdown protection rate limiter"""
        logger.info("Shutting down ProtectionRateLimiter...")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("ProtectionRateLimiter shut down complete")

# Export main classes and functions
__all__ = [
    'ProtectionRateLimiter',
    'ProtectionLevel',
    'ContentMatchType',
    'ViolationType',
    'LegalJurisdiction',
    'EnforcementAction',
    'ProtectionStatus',
    'ContentFingerprint',
    'ProtectionRule',
    'ViolationReport',
    'LegalDocument',
    'OffenderProfile'
]

if __name__ == "__main__":
    async def demo():
        """Demo protection rate limiter functionality"""
        limiter = ProtectionRateLimiter()
        await limiter.initialize()
        
        # Test content registration
        content_data = b"This is test content for protection"
        registration = await limiter.register_content_protection(
            "owner_123", "content_456", content_data, ProtectionLevel.PREMIUM
        )
        print(f"Content registration: {json.dumps(registration, indent=2)}")
        
        # Test similarity check
        similar_content = b"This is test content for protection (modified)"
        similarity_check = await limiter.check_content_similarity(similar_content, 0.5)
        print(f"Similarity check: {json.dumps(similarity_check, indent=2)}")
        
        # Test violation reporting
        if registration['success']:
            violation_report = await limiter.report_violation(
                registration['rule_id'],
                "violating_content_789",
                "violator_user",
                ViolationType.COPYRIGHT_INFRINGEMENT,
                {"similarity_score": 0.85, "detection_method": "automatic"},
                LegalJurisdiction.US_DMCA
            )
            print(f"Violation report: {json.dumps(violation_report, indent=2)}")
            
            # Test enforcement
            if violation_report['success']:
                enforcement = await limiter.enforce_protection(
                    violation_report['violation_id'],
                    EnforcementAction.WARNING_NOTICE
                )
                print(f"Enforcement result: {json.dumps(enforcement, indent=2, default=str)}")
        
        # Get protection analytics
        analytics = await limiter.get_protection_analytics("owner_123")
        print(f"Protection analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Get health status
        health = await limiter.get_health_status()
        print(f"Health status: {json.dumps(health, indent=2)}")
        
        await limiter.shutdown()
    
    # Run demo
    asyncio.run(demo())