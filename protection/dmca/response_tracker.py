"""📊 Response Tracking & Compliance Monitoring System
=================================================

Enterprise-grade response tracking system for DMCA notice compliance monitoring and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

This module provides:
- Real-time response tracking
- Compliance status monitoring
- Automated response parsing
- Performance analytics
- Legal compliance reporting
"""import asyncio
import logging
import re
import secrets
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import json
import aioredis
import aiofiles
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import email.utils
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of platform responses"""    ACKNOWLEDGMENT = "acknowledgment"
    TAKEDOWN_CONFIRMATION = "takedown_confirmation"
    REJECTION = "rejection"
    COUNTER_NOTICE = "counter_notice"
    PARTIAL_COMPLIANCE = "partial_compliance"
    ESCALATION_RESPONSE = "escalation_response"
    AUTOMATED_RESPONSE = "automated_response"
    MANUAL_REVIEW = "manual_review"


class ComplianceStatus(Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    DISPUTED = "disputed"
    PENDING = "pending"
    EXPIRED = "expired"


class ResponseChannel(Enum):
    """Response communication channels"""    EMAIL = "email"
    API_WEBHOOK = "api_webhook"
    PLATFORM_PORTAL = "platform_portal"
    WEB_SCRAPING = "web_scraping"
    MANUAL_INPUT = "manual_input"
    AUTOMATED_CHECK = "automated_check"


@dataclass
class ResponseMetadata:
    """Response metadata and context"""    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    authentication_method: Optional[str] = None
    response_time_ms: Optional[int] = None
    content_length: Optional[int] = None
    content_type: Optional[str] = None
    language: Optional[str] = None
    platform_version: Optional[str] = None
    api_version: Optional[str] = None
    additional_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class PlatformResponse:
    """Platform response to DMCA notice"""    response_id: str
    notice_id: str
    platform: str
    response_type: ResponseType
    compliance_status: ComplianceStatus
    channel: ResponseChannel
    
    # Content and timing
    content: str
    subject: Optional[str] = None
    received_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # Response details
    action_taken: Optional[str] = None
    content_removed: bool = False
    content_urls_affected: List[str] = field(default_factory=list)
    removal_confirmation_urls: List[str] = field(default_factory=list)
    
    # Legal and compliance
    legal_reasoning: Optional[str] = None
    fair_use_claim: bool = False
    counter_notice_attached: bool = False
    appeal_deadline: Optional[datetime] = None
    
    # Technical metadata
    metadata: ResponseMetadata = field(default_factory=ResponseMetadata)
    confidence_score: float = 0.0
    
    # Processing flags
    auto_processed: bool = True
    requires_manual_review: bool = False
    verified: bool = False
    
    def __post_init__(self):
        if not self.response_id:
            self.response_id = f"resp-{secrets.token_hex(8)}"


@dataclass
class ComplianceReport:
    """Compliance status report"""    report_id: str
    notice_id: str
    platform: str
    generated_at: datetime
    
    # Compliance metrics
    overall_status: ComplianceStatus
    compliance_score: float
    response_time_hours: Optional[float] = None
    
    # Response analysis
    total_responses: int = 0
    response_breakdown: Dict[ResponseType, int] = field(default_factory=dict)
    action_summary: List[str] = field(default_factory=list)
    
    # Legal assessment
    legal_risks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    
    # Performance metrics
    platform_response_rating: Optional[float] = None
    efficiency_score: Optional[float] = None


class ResponseParser:
    """Intelligent response content parser"""    
    def __init__(self):
        self.patterns = self._load_response_patterns()
        self.ml_classifier = None  # Placeholder for ML-based classification
    
    def _load_response_patterns(self) -> Dict[str, List[str]]:
        """Load response parsing patterns"""        return {
            'takedown_confirmation': [
                r'content has been removed',
                r'video.*deleted',
                r'post.*taken down',
                r'material.*disabled',
                r'access.*blocked',
                r'removed.*copyright',
                r'complied.*request',
                r'action taken.*remove'
            ],
            'rejection': [
                r'rejected.*claim',
                r'no.*infringement.*found',
                r'fair use',
                r'not.*copyright.*violation',
                r'claim.*denied',
                r'insufficient.*evidence',
                r'does not.*constitute.*infringement'
            ],
            'counter_notice': [
                r'counter.*notification',
                r'dmca.*counter',
                r'dispute.*claim',
                r'counter.*notice',
                r'challenging.*takedown',
                r'good faith.*belief.*removed'
            ],
            'partial_compliance': [
                r'partially.*removed',
                r'some.*content.*removed',
                r'portion.*disabled',
                r'limited.*action',
                r'restricted.*access'
            ],
            'manual_review': [
                r'manual.*review',
                r'human.*review',
                r'under.*investigation',
                r'reviewing.*claim',
                r'further.*analysis.*required'
            ]
        }
    
    async def parse_response(self, content: str, subject: str = None) -> Dict[str, Any]:
        """Parse platform response content"""        
        try:
            # Normalize content
            normalized_content = self._normalize_content(content)
            
            # Extract response type
            response_type = await self._classify_response_type(normalized_content, subject)
            
            # Extract compliance status
            compliance_status = await self._determine_compliance_status(
                normalized_content, response_type
            )
            
            # Extract action details
            actions_taken = await self._extract_actions_taken(normalized_content)
            
            # Extract URLs and references
            urls_affected = self._extract_urls(normalized_content)
            
            # Extract legal reasoning
            legal_reasoning = await self._extract_legal_reasoning(normalized_content)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                normalized_content, response_type, compliance_status
            )
            
            return {
                'response_type': response_type,
                'compliance_status': compliance_status,
                'actions_taken': actions_taken,
                'urls_affected': urls_affected,
                'legal_reasoning': legal_reasoning,
                'confidence_score': confidence_score,
                'content_removed': self._check_content_removed(normalized_content),
                'counter_notice_attached': self._check_counter_notice(normalized_content),
                'fair_use_claim': self._check_fair_use_claim(normalized_content),
                'requires_manual_review': confidence_score < 0.8
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                'response_type': ResponseType.MANUAL_REVIEW,
                'compliance_status': ComplianceStatus.UNDER_REVIEW,
                'confidence_score': 0.0,
                'requires_manual_review': True,
                'error': str(e)
            }
    
    def _normalize_content(self, content: str) -> str:
        """Normalize response content for analysis"""        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Convert to lowercase for pattern matching
        return content.lower().strip()
    
    async def _classify_response_type(self, content: str, subject: str = None) -> ResponseType:
        """Classify the type of response"""        
        # Check subject line first if available
        if subject:
            subject_lower = subject.lower()
            if any(word in subject_lower for word in ['removed', 'deleted', 'disabled']):
                return ResponseType.TAKEDOWN_CONFIRMATION
            elif any(word in subject_lower for word in ['rejected', 'denied', 'declined']):
                return ResponseType.REJECTION
            elif 'counter' in subject_lower:
                return ResponseType.COUNTER_NOTICE
        
        # Pattern-based classification
        for response_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return ResponseType(response_type.upper())
        
        # Default classification
        if any(word in content for word in ['acknowledge', 'received', 'processing']):
            return ResponseType.ACKNOWLEDGMENT
        
        return ResponseType.MANUAL_REVIEW
    
    async def _determine_compliance_status(self, content: str, 
                                         response_type: ResponseType) -> ComplianceStatus:
        """Determine compliance status from response"""        
        if response_type == ResponseType.TAKEDOWN_CONFIRMATION:
            return ComplianceStatus.COMPLIANT
        elif response_type == ResponseType.PARTIAL_COMPLIANCE:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif response_type == ResponseType.REJECTION:
            return ComplianceStatus.NON_COMPLIANT
        elif response_type == ResponseType.COUNTER_NOTICE:
            return ComplianceStatus.DISPUTED
        elif response_type == ResponseType.ACKNOWLEDGMENT:
            return ComplianceStatus.PENDING
        elif response_type == ResponseType.MANUAL_REVIEW:
            return ComplianceStatus.UNDER_REVIEW
        else:
            return ComplianceStatus.UNDER_REVIEW
    
    async def _extract_actions_taken(self, content: str) -> List[str]:
        """Extract specific actions taken by platform"""        
        actions = []
        
        # Action patterns
        action_patterns = {
            'content_removed': r'(content|video|post|material).*removed',
            'access_disabled': r'access.*disabled',
            'account_suspended': r'account.*suspended',
            'monetization_disabled': r'monetization.*disabled',
            'content_age_restricted': r'age.*restricted',
            'content_geo_blocked': r'geo.*blocked',
            'appeal_process_initiated': r'appeal.*process',
            'manual_review_scheduled': r'manual.*review.*scheduled'
        }
        
        for action_type, pattern in action_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                actions.append(action_type.replace('_', ' ').title())
        
        return actions
    
    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from response content"""        
        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        urls = re.findall(url_pattern, content)
        return list(set(urls))  # Remove duplicates
    
    async def _extract_legal_reasoning(self, content: str) -> Optional[str]:
        """Extract legal reasoning from response"""        
        # Look for legal reasoning patterns
        legal_patterns = [
            r'pursuant to.*copyright.*act',
            r'under.*section.*\d+',
            r'fair use.*analysis',
            r'copyright.*owner.*rights',
            r'dmca.*provisions',
            r'intellectual.*property.*laws'
        ]
        
        for pattern in legal_patterns:
            match = re.search(f'{pattern}.{{0,200}}', content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0).strip()
        
        return None
    
    async def _calculate_confidence_score(self, content: str, 
                                        response_type: ResponseType,
                                        compliance_status: ComplianceStatus) -> float:
        """Calculate confidence score for parsed response"""        
        score = 0.0
        
        # Base score from pattern matching
        if response_type != ResponseType.MANUAL_REVIEW:
            score += 0.4
        
        # Content length and quality indicators
        if len(content) > 100:
            score += 0.1
        if len(content) > 500:
            score += 0.1
        
        # Specific keyword presence
        high_confidence_keywords = [
            'removed', 'deleted', 'disabled', 'confirmed', 'rejected', 'denied'
        ]
        
        keyword_matches = sum(1 for keyword in high_confidence_keywords 
                            if keyword in content.lower())
        score += min(0.3, keyword_matches * 0.1)
        
        # Legal language presence
        legal_keywords = ['pursuant', 'section', 'copyright', 'dmca', 'infringement']
        legal_matches = sum(1 for keyword in legal_keywords 
                          if keyword in content.lower())
        score += min(0.1, legal_matches * 0.02)
        
        return min(1.0, score)
    
    def _check_content_removed(self, content: str) -> bool:
        """Check if content was actually removed"""        removal_indicators = [
            'content removed', 'video deleted', 'post taken down',
            'material disabled', 'access blocked', 'no longer available'
        ]
        
        return any(indicator in content for indicator in removal_indicators)
    
    def _check_counter_notice(self, content: str) -> bool:
        """Check if response includes counter-notice"""        counter_indicators = [
            'counter notification', 'counter notice', 'dmca counter',
            'dispute claim', 'challenging takedown'
        ]
        
        return any(indicator in content for indicator in counter_indicators)
    
    def _check_fair_use_claim(self, content: str) -> bool:
        """Check if response claims fair use"""        fair_use_indicators = [
            'fair use', 'fair dealing', 'educational use',
            'criticism', 'commentary', 'parody', 'transformative'
        ]
        
        return any(indicator in content for indicator in fair_use_indicators)


class ResponseTracker:
    """Main response tracking and monitoring system"""    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.redis_client: Optional[aioredis.Redis] = None
        self.parser = ResponseParser()
        self.active_monitors: Dict[str, asyncio.Task] = {}
        
        # Response storage
        self.responses: Dict[str, PlatformResponse] = {}
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
    
    async def initialize(self) -> bool:
        """Initialize response tracking system"""        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            
            # Load existing responses from storage
            await self._load_stored_responses()
            
            logger.info("Response tracking system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing response tracker: {e}")
            return False
    
    async def track_response(self, notice_id: str, platform: str,
                           content: str, channel: ResponseChannel = ResponseChannel.EMAIL,
                           metadata: ResponseMetadata = None) -> PlatformResponse:
        """Track a new platform response"""        
        try:
            # Parse response content
            parsed_data = await self.parser.parse_response(content)
            
            # Create response object
            response = PlatformResponse(
                response_id=f"resp-{secrets.token_hex(8)}",
                notice_id=notice_id,
                platform=platform,
                response_type=parsed_data['response_type'],
                compliance_status=parsed_data['compliance_status'],
                channel=channel,
                content=content,
                action_taken=", ".join(parsed_data.get('actions_taken', [])),
                content_removed=parsed_data.get('content_removed', False),
                content_urls_affected=parsed_data.get('urls_affected', []),
                legal_reasoning=parsed_data.get('legal_reasoning'),
                fair_use_claim=parsed_data.get('fair_use_claim', False),
                counter_notice_attached=parsed_data.get('counter_notice_attached', False),
                metadata=metadata or ResponseMetadata(),
                confidence_score=parsed_data.get('confidence_score', 0.0),
                requires_manual_review=parsed_data.get('requires_manual_review', False),
                processed_at=datetime.utcnow()
            )
            
            # Store response
            self.responses[response.response_id] = response
            await self._persist_response(response)
            
            # Update compliance tracking
            await self._update_compliance_tracking(response)
            
            # Generate alerts if needed
            await self._check_response_alerts(response)
            
            logger.info(f"Tracked response {response.response_id} for notice {notice_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error tracking response for notice {notice_id}: {e}")
            raise
    
    async def get_notice_responses(self, notice_id: str) -> List[PlatformResponse]:
        """Get all responses for a specific notice"""        
        responses = [
            response for response in self.responses.values()
            if response.notice_id == notice_id
        ]
        
        # Sort by received time
        responses.sort(key=lambda r: r.received_at)
        
        return responses
    
    async def get_compliance_status(self, notice_id: str) -> Dict[str, Any]:
        """Get overall compliance status for a notice"""        
        responses = await self.get_notice_responses(notice_id)
        
        if not responses:
            return {
                'notice_id': notice_id,
                'overall_status': ComplianceStatus.PENDING.value,
                'response_count': 0,
                'platforms_responded': [],
                'compliance_score': 0.0
            }
        
        # Analyze responses
        platforms_responded = list(set(r.platform for r in responses))
        
        # Determine overall compliance
        compliance_statuses = [r.compliance_status for r in responses]
        
        if ComplianceStatus.COMPLIANT in compliance_statuses:
            overall_status = ComplianceStatus.COMPLIANT
        elif ComplianceStatus.PARTIALLY_COMPLIANT in compliance_statuses:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        elif ComplianceStatus.DISPUTED in compliance_statuses:
            overall_status = ComplianceStatus.DISPUTED
        elif ComplianceStatus.NON_COMPLIANT in compliance_statuses:
            overall_status = ComplianceStatus.NON_COMPLIANT
        else:
            overall_status = ComplianceStatus.UNDER_REVIEW
        
        # Calculate compliance score
        compliance_score = await self._calculate_compliance_score(responses)
        
        return {
            'notice_id': notice_id,
            'overall_status': overall_status.value,
            'response_count': len(responses),
            'platforms_responded': platforms_responded,
            'compliance_score': compliance_score,
            'last_response_at': max(r.received_at for r in responses).isoformat(),
            'responses': [
                {
                    'platform': r.platform,
                    'status': r.compliance_status.value,
                    'content_removed': r.content_removed,
                    'confidence': r.confidence_score
                }
                for r in responses
            ]
        }
    
    async def generate_compliance_report(self, notice_id: str) -> ComplianceReport:
        """Generate comprehensive compliance report"""        
        responses = await self.get_notice_responses(notice_id)
        
        if not responses:
            return ComplianceReport(
                report_id=f"report-{secrets.token_hex(8)}",
                notice_id=notice_id,
                platform="N/A",
                generated_at=datetime.utcnow(),
                overall_status=ComplianceStatus.PENDING,
                compliance_score=0.0
            )
        
        # Analyze responses
        response_breakdown = defaultdict(int)
        for response in responses:
            response_breakdown[response.response_type] += 1
        
        # Calculate metrics
        compliance_status = await self.get_compliance_status(notice_id)
        overall_status = ComplianceStatus(compliance_status['overall_status'])
        compliance_score = compliance_status['compliance_score']
        
        # Calculate response time
        first_response = min(responses, key=lambda r: r.received_at)
        # Assuming notice was sent before first response
        response_time_hours = 24.0  # Default estimate
        
        # Generate action summary
        action_summary = []
        for response in responses:
            if response.action_taken:
                action_summary.append(f"{response.platform}: {response.action_taken}")
        
        # Risk assessment
        legal_risks = await self._assess_legal_risks(responses)
        
        # Recommendations
        recommendations = await self._generate_recommendations(responses, overall_status)
        
        # Next actions
        next_actions = await self._determine_next_actions(responses, overall_status)
        
        report = ComplianceReport(
            report_id=f"report-{secrets.token_hex(8)}",
            notice_id=notice_id,
            platform=", ".join(set(r.platform for r in responses)),
            generated_at=datetime.utcnow(),
            overall_status=overall_status,
            compliance_score=compliance_score,
            response_time_hours=response_time_hours,
            total_responses=len(responses),
            response_breakdown=dict(response_breakdown),
            action_summary=action_summary,
            legal_risks=legal_risks,
            recommendations=recommendations,
            next_actions=next_actions,
            platform_response_rating=await self._rate_platform_responses(responses),
            efficiency_score=await self._calculate_efficiency_score(responses)
        )
        
        # Store report
        self.compliance_reports[report.report_id] = report
        await self._persist_compliance_report(report)
        
        return report
    
    async def monitor_pending_responses(self, notice_id: str, 
                                      timeout_hours: int = 72) -> bool:
        """Monitor for responses to a notice with timeout"""        
        try:
            monitor_task = asyncio.create_task(
                self._response_monitor_task(notice_id, timeout_hours)
            )
            
            self.active_monitors[notice_id] = monitor_task
            
            # Wait for completion or timeout
            result = await monitor_task
            
            # Clean up
            if notice_id in self.active_monitors:
                del self.active_monitors[notice_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Error monitoring responses for notice {notice_id}: {e}")
            return False
    
    async def _response_monitor_task(self, notice_id: str, timeout_hours: int) -> bool:
        """Background task to monitor for responses"""        
        start_time = datetime.utcnow()
        timeout_time = start_time + timedelta(hours=timeout_hours)
        
        while datetime.utcnow() < timeout_time:
            # Check for new responses
            responses = await self.get_notice_responses(notice_id)
            
            if responses:
                # Check if we have sufficient responses
                compliance_status = await self.get_compliance_status(notice_id)
                
                if compliance_status['overall_status'] in [
                    ComplianceStatus.COMPLIANT.value,
                    ComplianceStatus.NON_COMPLIANT.value,
                    ComplianceStatus.DISPUTED.value
                ]:
                    logger.info(f"Monitoring complete for notice {notice_id}: "
                              f"{compliance_status['overall_status']}")
                    return True
            
            # Wait before next check
            await asyncio.sleep(3600)  # Check every hour
        
        # Timeout reached
        logger.warning(f"Response monitoring timeout for notice {notice_id}")
        return False
    
    async def _calculate_compliance_score(self, responses: List[PlatformResponse]) -> float:
        """Calculate overall compliance score"""        
        if not responses:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for response in responses:
            # Weight by confidence score
            weight = response.confidence_score
            
            # Score by compliance status
            status_scores = {
                ComplianceStatus.COMPLIANT: 1.0,
                ComplianceStatus.PARTIALLY_COMPLIANT: 0.6,
                ComplianceStatus.PENDING: 0.3,
                ComplianceStatus.UNDER_REVIEW: 0.2,
                ComplianceStatus.DISPUTED: 0.1,
                ComplianceStatus.NON_COMPLIANT: 0.0
            }
            
            score = status_scores.get(response.compliance_status, 0.0)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _assess_legal_risks(self, responses: List[PlatformResponse]) -> List[str]:
        """Assess legal risks from responses"""        
        risks = []
        
        # Check for counter-notices
        counter_notices = [r for r in responses if r.counter_notice_attached]
        if counter_notices:
            risks.append("Counter-notice received - may require legal response within 10 days")
        
        # Check for fair use claims
        fair_use_claims = [r for r in responses if r.fair_use_claim]
        if fair_use_claims:
            risks.append("Fair use defense claimed - may need stronger evidence")
        
        # Check for non-compliance
        non_compliant = [r for r in responses 
                        if r.compliance_status == ComplianceStatus.NON_COMPLIANT]
        if non_compliant:
            risks.append("Platform non-compliance - may require escalation or litigation")
        
        # Check for delayed responses
        delayed_responses = [r for r in responses 
                           if (datetime.utcnow() - r.received_at).days > 14]
        if delayed_responses:
            risks.append("Delayed platform response - may indicate resistance")
        
        return risks
    
    async def _generate_recommendations(self, responses: List[PlatformResponse],
                                      overall_status: ComplianceStatus) -> List[str]:
        """Generate actionable recommendations"""        
        recommendations = []
        
        if overall_status == ComplianceStatus.COMPLIANT:
            recommendations.append("Monitor for re-upload of infringing content")
            recommendations.append("Document successful takedown for future reference")
        
        elif overall_status == ComplianceStatus.PARTIALLY_COMPLIANT:
            recommendations.append("Follow up on remaining infringing content")
            recommendations.append("Provide additional evidence if requested")
        
        elif overall_status == ComplianceStatus.NON_COMPLIANT:
            recommendations.append("Consider formal escalation to platform legal team")
            recommendations.append("Evaluate potential for litigation")
            recommendations.append("Document platform non-compliance for legal proceedings")
        
        elif overall_status == ComplianceStatus.DISPUTED:
            recommendations.append("Prepare counter-notice response within 10 days")
            recommendations.append("Gather additional evidence to support claim")
            recommendations.append("Consider legal consultation")
        
        # Low confidence responses
        low_confidence = [r for r in responses if r.confidence_score < 0.6]
        if low_confidence:
            recommendations.append("Manual review of low-confidence responses recommended")
        
        return recommendations
    
    async def _determine_next_actions(self, responses: List[PlatformResponse],
                                    overall_status: ComplianceStatus) -> List[str]:
        """Determine specific next actions"""        
        next_actions = []
        
        # Time-sensitive actions
        counter_notices = [r for r in responses if r.counter_notice_attached]
        if counter_notices:
            next_actions.append("Respond to counter-notice within 10 business days")
        
        # Follow-up actions
        if overall_status == ComplianceStatus.PENDING:
            next_actions.append("Continue monitoring for platform response")
        
        if overall_status == ComplianceStatus.NON_COMPLIANT:
            next_actions.append("Send escalation notice to platform")
            next_actions.append("Consider DMCA repeat infringer policy")
        
        # Manual review requirements
        manual_review_needed = [r for r in responses if r.requires_manual_review]
        if manual_review_needed:
            next_actions.append("Schedule manual review of flagged responses")
        
        return next_actions
    
    async def _rate_platform_responses(self, responses: List[PlatformResponse]) -> float:
        """Rate platform response quality"""        
        if not responses:
            return 0.0
        
        total_rating = 0.0
        
        for response in responses:
            rating = 0.0
            
            # Response time (faster = better)
            if (datetime.utcnow() - response.received_at).days <= 7:
                rating += 0.3
            elif (datetime.utcnow() - response.received_at).days <= 14:
                rating += 0.2
            else:
                rating += 0.1
            
            # Compliance
            if response.compliance_status == ComplianceStatus.COMPLIANT:
                rating += 0.4
            elif response.compliance_status == ComplianceStatus.PARTIALLY_COMPLIANT:
                rating += 0.2
            
            # Communication quality
            if response.legal_reasoning:
                rating += 0.1
            
            if response.action_taken:
                rating += 0.1
            
            # Confidence in parsing
            rating += response.confidence_score * 0.1
            
            total_rating += rating
        
        return min(1.0, total_rating / len(responses))
    
    async def _calculate_efficiency_score(self, responses: List[PlatformResponse]) -> float:
        """Calculate efficiency score for the process"""        
        if not responses:
            return 0.0
        
        # Factors: response time, automation rate, accuracy
        efficiency_factors = []
        
        # Average response time
        avg_response_time = sum(
            (r.processed_at - r.received_at).total_seconds() 
            for r in responses if r.processed_at
        ) / len(responses)
        
        # Faster processing = higher efficiency
        time_efficiency = max(0, 1 - (avg_response_time / 3600))  # Normalize to hours
        efficiency_factors.append(time_efficiency)
        
        # Automation rate
        auto_processed = sum(1 for r in responses if r.auto_processed)
        automation_rate = auto_processed / len(responses)
        efficiency_factors.append(automation_rate)
        
        # Confidence/accuracy
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        efficiency_factors.append(avg_confidence)
        
        return sum(efficiency_factors) / len(efficiency_factors)
    
    async def _update_compliance_tracking(self, response: PlatformResponse):
        """Update compliance tracking metrics"""        
        # Store in Redis for real-time access
        key = f"compliance:{response.notice_id}"
        
        compliance_data = {
            'notice_id': response.notice_id,
            'last_updated': datetime.utcnow().isoformat(),
            'status': response.compliance_status.value,
            'platform': response.platform,
            'content_removed': response.content_removed
        }
        
        await self.redis_client.hset(key, mapping=compliance_data)
        await self.redis_client.expire(key, 86400 * 30)  # Expire after 30 days
    
    async def _check_response_alerts(self, response: PlatformResponse):
        """Check if response triggers any alerts"""        
        alerts = []
        
        # High-priority alerts
        if response.counter_notice_attached:
            alerts.append({
                'type': 'counter_notice',
                'priority': 'high',
                'message': f'Counter-notice received for {response.notice_id}',
                'deadline': datetime.utcnow() + timedelta(days=10)
            })
        
        if response.compliance_status == ComplianceStatus.NON_COMPLIANT:
            alerts.append({
                'type': 'non_compliance',
                'priority': 'medium',
                'message': f'Platform non-compliance for {response.notice_id}',
                'deadline': datetime.utcnow() + timedelta(days=7)
            })
        
        if response.requires_manual_review:
            alerts.append({
                'type': 'manual_review',
                'priority': 'low',
                'message': f'Manual review required for {response.notice_id}',
                'deadline': datetime.utcnow() + timedelta(days=3)
            })
        
        # Store alerts
        for alert in alerts:
            alert_key = f"alert:{response.notice_id}:{alert['type']}"
            await self.redis_client.setex(
                alert_key, 86400 * 30, json.dumps(alert, default=str)
            )
    
    async def _persist_response(self, response: PlatformResponse):
        """Persist response to storage"""        
        try:
            # Store in Redis
            key = f"response:{response.response_id}"
            data = asdict(response)
            
            # Convert datetime objects to ISO strings
            for field in ['received_at', 'processed_at', 'appeal_deadline']:
                if data.get(field):
                    data[field] = data[field].isoformat()
            
            await self.redis_client.setex(
                key, 86400 * 90, json.dumps(data, default=str)  # 90 days retention
            )
            
            # Also store file backup
            await self._store_response_file(response)
            
        except Exception as e:
            logger.error(f"Error persisting response {response.response_id}: {e}")
    
    async def _store_response_file(self, response: PlatformResponse):
        """Store response as file backup"""        
        storage_dir = Path("storage/responses")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = storage_dir / f"{response.response_id}.json"
        
        async with aiofiles.open(file_path, 'w') as f:
            data = asdict(response)
            # Convert datetime objects
            for field in ['received_at', 'processed_at', 'appeal_deadline']:
                if data.get(field):
                    data[field] = data[field].isoformat()
            
            await f.write(json.dumps(data, indent=2, default=str))
    
    async def _persist_compliance_report(self, report: ComplianceReport):
        """Persist compliance report"""        
        try:
            key = f"report:{report.report_id}"
            data = asdict(report)
            data['generated_at'] = data['generated_at'].isoformat()
            
            await self.redis_client.setex(
                key, 86400 * 365, json.dumps(data, default=str)  # 1 year retention
            )
            
        except Exception as e:
            logger.error(f"Error persisting report {report.report_id}: {e}")
    
    async def _load_stored_responses(self):
        """Load responses from storage on startup"""        
        try:
            # Load from Redis
            keys = await self.redis_client.keys("response:*")
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    response_data = json.loads(data)
                    
                    # Convert ISO strings back to datetime
                    for field in ['received_at', 'processed_at', 'appeal_deadline']:
                        if response_data.get(field):
                            response_data[field] = datetime.fromisoformat(response_data[field])
                    
                    # Reconstruct enums
                    response_data['response_type'] = ResponseType(response_data['response_type'])
                    response_data['compliance_status'] = ComplianceStatus(response_data['compliance_status'])
                    response_data['channel'] = ResponseChannel(response_data['channel'])
                    
                    # Reconstruct metadata
                    if response_data.get('metadata'):
                        response_data['metadata'] = ResponseMetadata(**response_data['metadata'])
                    
                    response = PlatformResponse(**response_data)
                    self.responses[response.response_id] = response
            
            logger.info(f"Loaded {len(self.responses)} responses from storage")
            
        except Exception as e:
            logger.error(f"Error loading stored responses: {e}")
    
    async def get_analytics_summary(self, date_range: Tuple[datetime, datetime] = None) -> Dict[str, Any]:
        """Get analytics summary for response tracking"""        
        if date_range:
            start_date, end_date = date_range
            filtered_responses = [
                r for r in self.responses.values()
                if start_date <= r.received_at <= end_date
            ]
        else:
            filtered_responses = list(self.responses.values())
        
        if not filtered_responses:
            return {'message': 'No responses in date range'}
        
        # Platform breakdown
        platform_stats = defaultdict(lambda: defaultdict(int))
        for response in filtered_responses:
            platform_stats[response.platform]['total'] += 1
            platform_stats[response.platform][response.compliance_status.value] += 1
        
        # Response type breakdown
        type_stats = defaultdict(int)
        for response in filtered_responses:
            type_stats[response.response_type.value] += 1
        
        # Performance metrics
        avg_confidence = sum(r.confidence_score for r in filtered_responses) / len(filtered_responses)
        
        automation_rate = sum(1 for r in filtered_responses if r.auto_processed) / len(filtered_responses)
        
        # Compliance rate
        compliant_responses = sum(
            1 for r in filtered_responses 
            if r.compliance_status == ComplianceStatus.COMPLIANT
        )
        compliance_rate = compliant_responses / len(filtered_responses)
        
        return {
            'summary': {
                'total_responses': len(filtered_responses),
                'compliance_rate': round(compliance_rate * 100, 1),
                'automation_rate': round(automation_rate * 100, 1),
                'average_confidence': round(avg_confidence, 2)
            },
            'platform_breakdown': dict(platform_stats),
            'response_type_breakdown': dict(type_stats),
            'period': {
                'start': min(r.received_at for r in filtered_responses).isoformat(),
                'end': max(r.received_at for r in filtered_responses).isoformat()
            }
        }
    
    async def cleanup(self):
        """Clean up resources"""        
        # Cancel active monitors
        for task in self.active_monitors.values():
            task.cancel()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Response tracker cleaned up")


# Factory function
def create_response_tracker(redis_url: str = None) -> ResponseTracker:
    """Create new response tracker instance"""    return ResponseTracker(redis_url)


__all__ = [
    'ResponseTracker',
    'ResponseParser',
    'PlatformResponse',
    'ComplianceReport',
    'ResponseMetadata',
    'ResponseType',
    'ComplianceStatus',
    'ResponseChannel',
    'create_response_tracker'
]
