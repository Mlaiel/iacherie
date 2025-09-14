"""
Ainflue Platform - Takedown Automation Monitor
==============================================

Enterprise-grade automated takedown request monitoring and processing system
for copyright infringement and policy violations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

# Metrics
takedown_requests_total = Counter('ainflue_takedown_requests_total',
                                'Total takedown requests processed', ['type', 'status', 'platform'])
takedown_processing_duration = Histogram('ainflue_takedown_processing_duration_seconds',
                                       'Time spent processing takedown requests')
active_takedown_requests = Gauge('ainflue_active_takedown_requests',
                               'Number of active takedown requests', ['platform'])

class TakedownType(Enum):
    """Types of takedown requests."""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    DEFAMATION = "defamation"
    HARASSMENT = "harassment"
    SPAM = "spam"
    MALWARE = "malware"
    POLICY_VIOLATION = "policy_violation"

class TakedownStatus(Enum):
    """Status of takedown requests."""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    COUNTER_NOTIFIED = "counter_notified"

class Platform(Enum):
    """Supported platforms for takedown requests."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    BANDCAMP = "bandcamp"
    GENERIC = "generic"

class ViolationSeverity(Enum):
    """Severity levels for violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TakedownRequest:
    """Takedown request structure."""
    request_id: str
    takedown_type: TakedownType
    platform: Platform
    infringing_url: str
    original_content_id: str
    complainant_id: str
    complainant_email: str
    violation_description: str
    evidence_urls: List[str]
    severity: ViolationSeverity
    automated: bool
    created_at: datetime
    updated_at: datetime
    status: TakedownStatus
    response_deadline: datetime
    platform_response: Optional[Dict[str, Any]] = None

@dataclass
class TakedownEvidence:
    """Evidence for takedown request."""
    evidence_id: str
    evidence_type: str
    file_url: str
    description: str
    timestamp: datetime
    verified: bool
    hash_value: str

@dataclass
class CounterNotice:
    """Counter-notice for disputed takedown."""
    notice_id: str
    takedown_request_id: str
    respondent_id: str
    respondent_email: str
    counter_statement: str
    good_faith_belief: bool
    penalty_acknowledgment: bool
    signature: str
    submitted_at: datetime

class TakedownAutomationMonitor:
    """Enterprise takedown automation monitoring system."""
    
    def __init__(self) -> None:
        self.takedown_requests = {}
        self.platform_clients = {}
        self.evidence_storage = {}
        self.automation_rules = {}
        self.processing_queue = asyncio.Queue()
        self.counter_notices = {}
        
    async def initialize_platform_clients(self, platform_configs -> None: Dict[Platform, Dict[str, Any]]) -> None:
        """Initialize platform API clients for takedown automation."""
        
        for platform, config in platform_configs.items():
            try:
                client_config = {
                    'api_key': config.get('api_key'),
                    'api_secret': config.get('api_secret'),
                    'base_url': config.get('base_url'),
                    'timeout': config.get('timeout', 30)
                }
                
                self.platform_clients[platform] = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=client_config['timeout'])
                )
                
                logger.info(f"Initialized platform client: {platform.value}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {platform.value} client: {str(e)}")
    
    async def submit_takedown_request(self, content_id: str, infringing_url: str,
                                    takedown_type: TakedownType, platform: Platform,
                                    complainant_id: str, complainant_email: str,
                                    violation_description: str,
                                    evidence_urls: Optional[List[str]] = None,
                                    severity: ViolationSeverity = ViolationSeverity.MEDIUM) -> str:
        """Submit a new takedown request."""
        start_time = time.time()
        
        try:
            # Generate request ID
            request_id = f"td_{int(time.time())}_{hashlib.md5(infringing_url.encode()).hexdigest()[:8]}"
            
            # Calculate response deadline based on platform and severity
            response_deadline = await self._calculate_response_deadline(platform, severity)
            
            # Create takedown request
            takedown_request = TakedownRequest(
                request_id=request_id,
                takedown_type=takedown_type,
                platform=platform,
                infringing_url=infringing_url,
                original_content_id=content_id,
                complainant_id=complainant_id,
                complainant_email=complainant_email,
                violation_description=violation_description,
                evidence_urls=evidence_urls or [],
                severity=severity,
                automated=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status=TakedownStatus.PENDING,
                response_deadline=response_deadline
            )
            
            # Store request
            self.takedown_requests[request_id] = takedown_request
            
            # Add to processing queue
            await self.processing_queue.put(request_id)
            
            # Update metrics
            takedown_requests_total.labels(
                type=takedown_type.value,
                status='submitted',
                platform=platform.value
            ).inc()
            
            active_takedown_requests.labels(platform=platform.value).inc()
            
            logger.info(f"Takedown request submitted: {request_id} for {infringing_url}")
            return request_id
            
        except Exception as e:
            logger.error(f"Takedown request submission failed: {str(e)}")
            raise
    
    async def _calculate_response_deadline(self, platform: Platform,
                                         severity: ViolationSeverity) -> datetime:
        """Calculate response deadline based on platform and severity."""
        
        # Platform-specific response times (in hours)
        platform_response_times = {
            Platform.YOUTUBE: 24,
            Platform.SPOTIFY: 48,
            Platform.SOUNDCLOUD: 72,
            Platform.APPLE_MUSIC: 48,
            Platform.INSTAGRAM: 24,
            Platform.TIKTOK: 24,
            Platform.FACEBOOK: 24,
            Platform.TWITTER: 24,
            Platform.BANDCAMP: 72,
            Platform.GENERIC: 168  # 1 week
        }
        
        # Severity multipliers
        severity_multipliers = {
            ViolationSeverity.CRITICAL: 0.5,
            ViolationSeverity.HIGH: 0.75,
            ViolationSeverity.MEDIUM: 1.0,
            ViolationSeverity.LOW: 1.5
        }
        
        base_hours = platform_response_times.get(platform, 168)
        multiplier = severity_multipliers.get(severity, 1.0)
        
        deadline_hours = base_hours * multiplier
        return datetime.now() + timedelta(hours=deadline_hours)
    
    async def process_takedown_queue(self) -> None:
        """Process pending takedown requests."""
        
        while True:
            try:
                # Get request from queue (with timeout)
                request_id = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=10.0
                )
                
                # Process the request
                await self._process_takedown_request(request_id)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except asyncio.TimeoutError:
                # No requests in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing takedown queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_takedown_request(self, request_id -> None: str) -> None:
        """Process individual takedown request."""
        start_time = time.time()
        
        try:
            takedown_request = self.takedown_requests.get(request_id)
            if not takedown_request:
                logger.warning(f"Takedown request not found: {request_id}")
                return
            
            # Update status to processing
            takedown_request.status = TakedownStatus.PROCESSING
            takedown_request.updated_at = datetime.now()
            
            # Validate request
            validation_result = await self._validate_takedown_request(takedown_request)
            
            if not validation_result['valid']:
                takedown_request.status = TakedownStatus.REJECTED
                takedown_request.platform_response = validation_result
                logger.warning(f"Takedown request validation failed: {request_id}")
                return
            
            # Collect and verify evidence
            evidence_verification = await self._verify_evidence(takedown_request)
            
            if not evidence_verification['sufficient']:
                takedown_request.status = TakedownStatus.REJECTED
                takedown_request.platform_response = evidence_verification
                logger.warning(f"Insufficient evidence for takedown: {request_id}")
                return
            
            # Submit to platform
            platform_response = await self._submit_to_platform(takedown_request)
            
            # Update request with platform response
            takedown_request.platform_response = platform_response
            
            if platform_response.get('success'):
                takedown_request.status = TakedownStatus.APPROVED
                logger.info(f"Takedown request approved: {request_id}")
            else:
                takedown_request.status = TakedownStatus.REJECTED
                logger.warning(f"Takedown request rejected by platform: {request_id}")
            
            # Update metrics
            processing_time = time.time() - start_time
            takedown_processing_duration.observe(processing_time)
            
            takedown_requests_total.labels(
                type=takedown_request.takedown_type.value,
                status=takedown_request.status.value,
                platform=takedown_request.platform.value
            ).inc()
            
        except Exception as e:
            logger.error(f"Takedown request processing failed: {str(e)}")
            
            # Update request status
            if request_id in self.takedown_requests:
                self.takedown_requests[request_id].status = TakedownStatus.FAILED
                self.takedown_requests[request_id].platform_response = {'error': str(e)}
    
    async def _validate_takedown_request(self, takedown_request: TakedownRequest) -> Dict[str, Any]:
        """Validate takedown request before processing."""
        
        validation_errors = []
        
        # Validate URL format
        if not self._is_valid_url(takedown_request.infringing_url):
            validation_errors.append("Invalid infringing URL format")
        
        # Validate email format
        if not self._is_valid_email(takedown_request.complainant_email):
            validation_errors.append("Invalid complainant email format")
        
        # Validate description length
        if len(takedown_request.violation_description) < 50:
            validation_errors.append("Violation description too short (minimum 50 characters)")
        
        # Check for duplicate requests
        duplicate = await self._check_duplicate_request(takedown_request)
        if duplicate:
            validation_errors.append(f"Duplicate request found: {duplicate}")
        
        # Validate platform compatibility
        platform_compatible = await self._check_platform_compatibility(
            takedown_request.infringing_url, takedown_request.platform
        )
        if not platform_compatible:
            validation_errors.append("URL not compatible with specified platform")
        
        return {
            'valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'validated_at': datetime.now().isoformat()
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))
    
    async def _check_duplicate_request(self, takedown_request: TakedownRequest) -> Optional[str]:
        """Check for duplicate takedown requests."""
        
        for existing_id, existing_request in self.takedown_requests.items():
            if (existing_request.infringing_url == takedown_request.infringing_url and
                existing_request.original_content_id == takedown_request.original_content_id and
                existing_request.status in [TakedownStatus.PENDING, TakedownStatus.PROCESSING, TakedownStatus.APPROVED]):
                
                return existing_id
        
        return None
    
    async def _check_platform_compatibility(self, url: str, platform: Platform) -> bool:
        """Check if URL is compatible with specified platform."""
        
        platform_domains = {
            Platform.YOUTUBE: ['youtube.com', 'youtu.be'],
            Platform.SPOTIFY: ['spotify.com', 'open.spotify.com'],
            Platform.SOUNDCLOUD: ['soundcloud.com'],
            Platform.APPLE_MUSIC: ['music.apple.com'],
            Platform.INSTAGRAM: ['instagram.com'],
            Platform.TIKTOK: ['tiktok.com'],
            Platform.FACEBOOK: ['facebook.com', 'fb.com'],
            Platform.TWITTER: ['twitter.com', 'x.com'],
            Platform.BANDCAMP: ['bandcamp.com']
        }
        
        if platform == Platform.GENERIC:
            return True
        
        domains = platform_domains.get(platform, [])
        return any(domain in url.lower() for domain in domains)
    
    async def _verify_evidence(self, takedown_request: TakedownRequest) -> Dict[str, Any]:
        """Verify evidence for takedown request."""
        
        verification_results = {
            'sufficient': False,
            'verified_evidence': [],
            'verification_errors': [],
            'verified_at': datetime.now().isoformat()
        }
        
        # Check if evidence URLs are provided
        if not takedown_request.evidence_urls:
            verification_results['verification_errors'].append("No evidence URLs provided")
            return verification_results
        
        verified_count = 0
        
        for evidence_url in takedown_request.evidence_urls:
            try:
                evidence_result = await self._verify_single_evidence(evidence_url, takedown_request)
                
                if evidence_result['valid']:
                    verified_count += 1
                    verification_results['verified_evidence'].append(evidence_result)
                else:
                    verification_results['verification_errors'].append(
                        f"Evidence verification failed for {evidence_url}: {evidence_result.get('error', 'Unknown error')}"
                    )
                    
            except Exception as e:
                verification_results['verification_errors'].append(
                    f"Evidence verification error for {evidence_url}: {str(e)}"
                )
        
        # Determine if evidence is sufficient
        minimum_evidence = self._get_minimum_evidence_requirement(takedown_request.takedown_type)
        verification_results['sufficient'] = verified_count >= minimum_evidence
        
        return verification_results
    
    async def _verify_single_evidence(self, evidence_url: str,
                                    takedown_request: TakedownRequest) -> Dict[str, Any]:
        """Verify a single piece of evidence."""
        
        try:
            # Download and analyze evidence
            evidence_data = await self._download_evidence(evidence_url)
            
            if not evidence_data:
                return {'valid': False, 'error': 'Could not download evidence'}
            
            # Generate evidence hash
            evidence_hash = hashlib.sha256(evidence_data).hexdigest()
            
            # Create evidence record
            evidence_id = f"ev_{int(time.time())}_{evidence_hash[:8]}"
            
            evidence = TakedownEvidence(
                evidence_id=evidence_id,
                evidence_type=self._detect_evidence_type(evidence_data),
                file_url=evidence_url,
                description=f"Evidence for takedown {takedown_request.request_id}",
                timestamp=datetime.now(),
                verified=True,
                hash_value=evidence_hash
            )
            
            # Store evidence
            self.evidence_storage[evidence_id] = evidence
            
            return {
                'valid': True,
                'evidence_id': evidence_id,
                'evidence_type': evidence.evidence_type,
                'hash': evidence_hash,
                'verified_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    async def _download_evidence(self, evidence_url: str) -> Optional[bytes]:
        """Download evidence file."""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(evidence_url, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.warning(f"Failed to download evidence: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Evidence download error: {str(e)}")
            return None
    
    def _detect_evidence_type(self, evidence_data: bytes) -> str:
        """Detect type of evidence file."""
        
        # Check file signatures
        if evidence_data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif evidence_data.startswith(b'\x89PNG'):
            return 'image/png'
        elif evidence_data.startswith(b'%PDF'):
            return 'application/pdf'
        elif evidence_data.startswith(b'ID3') or evidence_data[4:8] == b'ftyp':
            return 'audio'
        elif b'<html' in evidence_data[:100].lower():
            return 'text/html'
        else:
            return 'application/octet-stream'
    
    def _get_minimum_evidence_requirement(self, takedown_type: TakedownType) -> int:
        """Get minimum evidence requirement for takedown type."""
        
        requirements = {
            TakedownType.COPYRIGHT_INFRINGEMENT: 2,
            TakedownType.TRADEMARK_VIOLATION: 2,
            TakedownType.PRIVACY_VIOLATION: 1,
            TakedownType.DEFAMATION: 2,
            TakedownType.HARASSMENT: 1,
            TakedownType.SPAM: 1,
            TakedownType.MALWARE: 1,
            TakedownType.POLICY_VIOLATION: 1
        }
        
        return requirements.get(takedown_type, 1)
    
    async def _submit_to_platform(self, takedown_request: TakedownRequest) -> Dict[str, Any]:
        """Submit takedown request to platform."""
        
        platform = takedown_request.platform
        
        if platform not in self.platform_clients:
            return {
                'success': False,
                'error': f'Platform {platform.value} not configured',
                'submitted_at': datetime.now().isoformat()
            }
        
        try:
            # Prepare platform-specific payload
            payload = await self._prepare_platform_payload(takedown_request)
            
            # Submit to platform API
            response = await self._call_platform_api(platform, payload)
            
            return {
                'success': response.get('accepted', False),
                'platform_id': response.get('request_id'),
                'platform_status': response.get('status'),
                'platform_message': response.get('message'),
                'submitted_at': datetime.now().isoformat(),
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Platform submission failed for {platform.value}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'submitted_at': datetime.now().isoformat()
            }
    
    async def _prepare_platform_payload(self, takedown_request: TakedownRequest) -> Dict[str, Any]:
        """Prepare platform-specific payload."""
        
        base_payload = {
            'type': takedown_request.takedown_type.value,
            'infringing_url': takedown_request.infringing_url,
            'description': takedown_request.violation_description,
            'complainant_email': takedown_request.complainant_email,
            'evidence_urls': takedown_request.evidence_urls,
            'severity': takedown_request.severity.value,
            'request_id': takedown_request.request_id
        }
        
        platform = takedown_request.platform
        
        # Platform-specific customizations
        if platform == Platform.YOUTUBE:
            base_payload.update({
                'content_type': 'video',
                'reason_code': self._map_to_youtube_reason(takedown_request.takedown_type)
            })
        elif platform == Platform.SPOTIFY:
            base_payload.update({
                'content_type': 'audio',
                'track_info': self._extract_spotify_info(takedown_request.infringing_url)
            })
        # Add more platform-specific customizations as needed
        
        return base_payload
    
    def _map_to_youtube_reason(self, takedown_type: TakedownType) -> str:
        """Map takedown type to YouTube reason code."""
        
        mapping = {
            TakedownType.COPYRIGHT_INFRINGEMENT: 'copyright',
            TakedownType.TRADEMARK_VIOLATION: 'trademark',
            TakedownType.PRIVACY_VIOLATION: 'privacy',
            TakedownType.DEFAMATION: 'defamation',
            TakedownType.HARASSMENT: 'harassment',
            TakedownType.SPAM: 'spam',
            TakedownType.POLICY_VIOLATION: 'community_guidelines'
        }
        
        return mapping.get(takedown_type, 'other')
    
    def _extract_spotify_info(self, url: str) -> Dict[str, Any]:
        """Extract track information from Spotify URL."""
        
        # Simple URL parsing for Spotify tracks
        import re
        
        track_match = re.search(r'/track/([a-zA-Z0-9]+)', url)
        album_match = re.search(r'/album/([a-zA-Z0-9]+)', url)
        
        info = {}
        if track_match:
            info['track_id'] = track_match.group(1)
        if album_match:
            info['album_id'] = album_match.group(1)
        
        return info
    
    async def _call_platform_api(self, platform: Platform, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call platform API to submit takedown request."""
        
        # Simulate platform API calls
        # In real implementation, would make actual API calls to each platform
        
        await asyncio.sleep(0.1)  # Simulate API call delay
        
        # Simulate different platform responses
        if platform in [Platform.YOUTUBE, Platform.SPOTIFY, Platform.INSTAGRAM]:
            # Simulate high success rate for major platforms
            success = hash(payload['request_id']) % 10 < 8  # 80% success rate
        else:
            # Simulate lower success rate for other platforms
            success = hash(payload['request_id']) % 10 < 6  # 60% success rate
        
        if success:
            return {
                'accepted': True,
                'request_id': f"{platform.value}_{payload['request_id']}",
                'status': 'submitted',
                'message': 'Takedown request submitted successfully',
                'estimated_processing_time': '24-48 hours'
            }
        else:
            return {
                'accepted': False,
                'status': 'rejected',
                'message': 'Takedown request rejected due to insufficient evidence',
                'error_code': 'INSUFFICIENT_EVIDENCE'
            }
    
    async def handle_counter_notice(self, takedown_request_id: str,
                                  respondent_id: str, respondent_email: str,
                                  counter_statement: str, signature: str) -> str:
        """Handle counter-notice for disputed takedown."""
        
        try:
            if takedown_request_id not in self.takedown_requests:
                raise ValueError(f"Takedown request not found: {takedown_request_id}")
            
            takedown_request = self.takedown_requests[takedown_request_id]
            
            # Create counter notice
            notice_id = f"cn_{int(time.time())}_{hashlib.md5(respondent_email.encode()).hexdigest()[:8]}"
            
            counter_notice = CounterNotice(
                notice_id=notice_id,
                takedown_request_id=takedown_request_id,
                respondent_id=respondent_id,
                respondent_email=respondent_email,
                counter_statement=counter_statement,
                good_faith_belief=True,  # Assumed from form submission
                penalty_acknowledgment=True,  # Assumed from form submission
                signature=signature,
                submitted_at=datetime.now()
            )
            
            # Store counter notice
            self.counter_notices[notice_id] = counter_notice
            
            # Update takedown request status
            takedown_request.status = TakedownStatus.COUNTER_NOTIFIED
            takedown_request.updated_at = datetime.now()
            
            # Notify original complainant
            await self._notify_complainant_of_counter(takedown_request, counter_notice)
            
            logger.info(f"Counter-notice submitted: {notice_id} for takedown {takedown_request_id}")
            return notice_id
            
        except Exception as e:
            logger.error(f"Counter-notice handling failed: {str(e)}")
            raise
    
    async def _notify_complainant_of_counter(self, takedown_request -> None: TakedownRequest,
                                           counter_notice -> None: CounterNotice) -> None:
        """Notify original complainant of counter-notice."""
        
        notification = {
            'type': 'counter_notice_received',
            'takedown_request_id': takedown_request.request_id,
            'counter_notice_id': counter_notice.notice_id,
            'respondent_statement': counter_notice.counter_statement,
            'complainant_email': takedown_request.complainant_email,
            'deadline_to_respond': (datetime.now() + timedelta(days=14)).isoformat(),
            'notification_sent_at': datetime.now().isoformat()
        }
        
        # In real implementation, would send email notification
        logger.info(f"Counter-notice notification prepared for {takedown_request.complainant_email}")
    
    async def check_takedown_deadlines(self) -> None:
        """Check for takedown requests approaching deadlines."""
        
        current_time = datetime.now()
        approaching_deadline = []
        overdue = []
        
        for request_id, takedown_request in self.takedown_requests.items():
            if takedown_request.status in [TakedownStatus.PENDING, TakedownStatus.PROCESSING]:
                time_to_deadline = (takedown_request.response_deadline - current_time).total_seconds()
                
                if time_to_deadline < 0:
                    overdue.append(takedown_request)
                elif time_to_deadline < 3600:  # Less than 1 hour
                    approaching_deadline.append(takedown_request)
        
        # Handle overdue requests
        for request in overdue:
            await self._handle_overdue_request(request)
        
        # Send deadline warnings
        for request in approaching_deadline:
            await self._send_deadline_warning(request)
        
        return {
            'approaching_deadline': len(approaching_deadline),
            'overdue': len(overdue),
            'checked_at': current_time.isoformat()
        }
    
    async def _handle_overdue_request(self, takedown_request -> None: TakedownRequest) -> None:
        """Handle overdue takedown request."""
        
        takedown_request.status = TakedownStatus.FAILED
        takedown_request.updated_at = datetime.now()
        takedown_request.platform_response = {
            'error': 'Request exceeded response deadline',
            'deadline_exceeded_at': datetime.now().isoformat()
        }
        
        # Update metrics
        active_takedown_requests.labels(platform=takedown_request.platform.value).dec()
        
        logger.warning(f"Takedown request exceeded deadline: {takedown_request.request_id}")
    
    async def _send_deadline_warning(self, takedown_request -> None: TakedownRequest) -> None:
        """Send deadline warning for takedown request."""
        
        warning = {
            'type': 'deadline_warning',
            'request_id': takedown_request.request_id,
            'deadline': takedown_request.response_deadline.isoformat(),
            'time_remaining': (takedown_request.response_deadline - datetime.now()).total_seconds(),
            'warning_sent_at': datetime.now().isoformat()
        }
        
        logger.warning(f"Takedown deadline approaching: {takedown_request.request_id}")
    
    def get_takedown_stats(self) -> Dict[str, Any]:
        """Get takedown automation statistics."""
        
        total_requests = len(self.takedown_requests)
        
        # Status distribution
        status_counts = {}
        for request in self.takedown_requests.values():
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Platform distribution
        platform_counts = {}
        for request in self.takedown_requests.values():
            platform = request.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Type distribution
        type_counts = {}
        for request in self.takedown_requests.values():
            req_type = request.takedown_type.value
            type_counts[req_type] = type_counts.get(req_type, 0) + 1
        
        # Success rate calculation
        completed = status_counts.get('completed', 0) + status_counts.get('approved', 0)
        total_processed = total_requests - status_counts.get('pending', 0) - status_counts.get('processing', 0)
        success_rate = (completed / total_processed * 100) if total_processed > 0 else 0
        
        return {
            'total_requests': total_requests,
            'status_distribution': status_counts,
            'platform_distribution': platform_counts,
            'type_distribution': type_counts,
            'success_rate_percentage': success_rate,
            'total_counter_notices': len(self.counter_notices),
            'queue_size': self.processing_queue.qsize()
        }

# Global takedown automation monitor instance
takedown_automation_monitor = TakedownAutomationMonitor()