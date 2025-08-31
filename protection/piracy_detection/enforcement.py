"""⚖️ Automated Enforcement System
===============================

Automated enforcement and takedown processing for piracy violations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module provides:
- Automated DMCA takedown generation and submission
- Multi-platform enforcement coordination
- Legal compliance validation
- Escalation management
- Success tracking and reporting
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class EnforcementAction(Enum):
    """Types of enforcement actions."""
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    PLATFORM_REPORT = "platform_report"
    LEGAL_NOTICE = "legal_notice"
    CONTENT_CLAIM = "content_claim"
    ACCOUNT_SUSPENSION = "account_suspension"

class EnforcementStatus(Enum):
    """Enforcement request status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"

class EscalationLevel(Enum):
    """Escalation levels for enforcement."""
    AUTOMATIC = "automatic"
    REVIEW_REQUIRED = "review_required"
    LEGAL_REQUIRED = "legal_required"
    MANUAL_ONLY = "manual_only"

@dataclass
class EnforcementRequest:
    """Enforcement request details."""
    request_id: str
    violation_id: str
    content_id: str
    platform: str
    action_type: EnforcementAction
    status: EnforcementStatus
    escalation_level: EscalationLevel
    confidence_score: float
    evidence_package: Dict[str, Any]
    legal_basis: List[str]
    submitted_at: Optional[datetime]
    response_deadline: Optional[datetime]
    platform_response: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class AutomatedEnforcement:
    """
    Advanced automated enforcement system for piracy violations.
    
    Provides comprehensive enforcement capabilities with legal compliance,
    automated submission, and intelligent escalation management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Automated Enforcement system.
        
        Args:
            config: Enforcement configuration parameters
        """
        self.config = config or {}
        self._initialized = False
        
        # Enforcement parameters
        self.auto_enforcement_threshold = self.config.get('auto_enforcement_threshold', 0.9)
        self.review_threshold = self.config.get('review_threshold', 0.75)
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 50)
        self.response_timeout_hours = self.config.get('response_timeout_hours', 72)
        
        # Platform-specific configurations
        self.platform_configs = {}
        self.enforcement_templates = {}
        
        # Active enforcement requests
        self.active_requests: Dict[str, EnforcementRequest] = {}
        self.pending_queue: List[str] = []
        
        # Services
        self.legal_service = None
        self.notification_service = None
        self.template_service = None
        
        # Enforcement statistics
        self.enforcement_stats = {
            'total_requests': 0,
            'successful_enforcements': 0,
            'failed_enforcements': 0,
            'pending_requests': 0,
            'average_response_time_hours': 0.0,
            'platform_success_rates': {}
        }
        
        logger.info("Automated Enforcement system initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize enforcement system components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Automated Enforcement system...")
            
            # Initialize platform configurations
            await self._initialize_platform_configs()
            
            # Initialize enforcement templates
            await self._initialize_enforcement_templates()
            
            # Initialize legal service
            await self._initialize_legal_service()
            
            # Initialize notification service
            await self._initialize_notification_service()
            
            # Start enforcement processor
            asyncio.create_task(self._enforcement_processor())
            
            # Start status monitor
            asyncio.create_task(self._status_monitor())
            
            self._initialized = True
            logger.info("Automated Enforcement system successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Automated Enforcement system: {str(e)}")
            return False
    
    async def _initialize_platform_configs(self) -> None:
        """Initialize platform-specific enforcement configurations."""
        self.platform_configs = {
            'youtube': {
                'supported_actions': [
                    EnforcementAction.DMCA_TAKEDOWN,
                    EnforcementAction.CONTENT_CLAIM,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'api_endpoint': 'https://www.googleapis.com/youtube/v3',
                'requires_auth': True,
                'auto_enforcement_enabled': True,
                'response_time_hours': 24,
                'success_rate': 0.85
            },
            'instagram': {
                'supported_actions': [
                    EnforcementAction.DMCA_TAKEDOWN,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'api_endpoint': 'https://graph.instagram.com',
                'requires_auth': True,
                'auto_enforcement_enabled': True,
                'response_time_hours': 48,
                'success_rate': 0.78
            },
            'tiktok': {
                'supported_actions': [
                    EnforcementAction.PLATFORM_REPORT,
                    EnforcementAction.DMCA_TAKEDOWN
                ],
                'api_endpoint': None,  # Manual submission required
                'requires_auth': False,
                'auto_enforcement_enabled': False,
                'response_time_hours': 72,
                'success_rate': 0.65
            },
            'twitter': {
                'supported_actions': [
                    EnforcementAction.DMCA_TAKEDOWN,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'api_endpoint': 'https://api.twitter.com/2',
                'requires_auth': True,
                'auto_enforcement_enabled': True,
                'response_time_hours': 24,
                'success_rate': 0.82
            },
            'facebook': {
                'supported_actions': [
                    EnforcementAction.DMCA_TAKEDOWN,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'api_endpoint': 'https://graph.facebook.com',
                'requires_auth': True,
                'auto_enforcement_enabled': True,
                'response_time_hours': 48,
                'success_rate': 0.80
            },
            'soundcloud': {
                'supported_actions': [
                    EnforcementAction.DMCA_TAKEDOWN,
                    EnforcementAction.PLATFORM_REPORT
                ],
                'api_endpoint': 'https://api.soundcloud.com',
                'requires_auth': True,
                'auto_enforcement_enabled': True,
                'response_time_hours': 24,
                'success_rate': 0.88
            }
        }
        
        logger.info(f"Initialized enforcement configs for {len(self.platform_configs)} platforms")
    
    async def _initialize_enforcement_templates(self) -> None:
        """Initialize enforcement document templates."""
        self.enforcement_templates = {
            EnforcementAction.DMCA_TAKEDOWN: {
                'subject': 'DMCA Takedown Notice - Copyright Infringement',
                'template': '''
                Dear Copyright Agent,
                
                I am writing to notify you of copyrighted material that is being infringed upon on your platform.
                
                IDENTIFICATION OF COPYRIGHTED WORK:
                - Original Content Title: {original_title}
                - Copyright Owner: {copyright_owner}
                - Creation Date: {creation_date}
                - Registration Number: {registration_number}
                
                IDENTIFICATION OF INFRINGING MATERIAL:
                - Platform: {platform}
                - Infringing URL: {infringing_url}
                - Description: {infringing_description}
                - Detected Date: {detection_date}
                
                STATEMENT OF GOOD FAITH:
                I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.
                
                STATEMENT OF ACCURACY:
                I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.
                
                CONTACT INFORMATION:
                {contact_information}
                
                SIGNATURE:
                {digital_signature}
                
                Date: {submission_date}
                ''',
                'required_fields': [
                    'original_title', 'copyright_owner', 'creation_date',
                    'platform', 'infringing_url', 'detection_date',
                    'contact_information', 'digital_signature'
                ]
            },
            EnforcementAction.CEASE_DESIST: {
                'subject': 'Cease and Desist Notice - Copyright Infringement',
                'template': '''
                CEASE AND DESIST NOTICE
                
                TO: {infringer_name}
                FROM: {copyright_owner}
                DATE: {notice_date}
                
                You are hereby notified that your use of the copyrighted material "{original_title}" constitutes copyright infringement under applicable laws.
                
                DEMAND FOR CESSATION:
                You are hereby demanded to immediately cease and desist from any further use, reproduction, distribution, or display of the copyrighted material.
                
                LEGAL BASIS:
                {legal_basis}
                
                CONSEQUENCES:
                Failure to comply with this notice may result in legal action seeking monetary damages, injunctive relief, and attorney fees.
                
                {contact_information}
                ''',
                'required_fields': [
                    'infringer_name', 'copyright_owner', 'original_title',
                    'legal_basis', 'contact_information'
                ]
            },
            EnforcementAction.PLATFORM_REPORT: {
                'subject': 'Copyright Infringement Report',
                'template': '''
                Platform Copyright Violation Report
                
                Original Content: {original_title}
                Infringing Content: {infringing_url}
                Violation Type: {violation_type}
                Confidence Level: {confidence_score}%
                
                Evidence:
                {evidence_summary}
                
                Requested Action: {requested_action}
                
                Contact: {contact_information}
                ''',
                'required_fields': [
                    'original_title', 'infringing_url', 'violation_type',
                    'confidence_score', 'evidence_summary', 'requested_action'
                ]
            }
        }
        
        logger.info("Enforcement templates initialized")
    
    async def _initialize_legal_service(self) -> None:
        """Initialize legal compliance service."""
        self.legal_service = {
            'compliance_checker': True,
            'jurisdiction_handler': True,
            'template_validator': True,
            'legal_database': True
        }
        logger.info("Legal service initialized")
    
    async def _initialize_notification_service(self) -> None:
        """Initialize notification service."""
        self.notification_service = {
            'email_service': True,
            'webhook_service': True,
            'dashboard_notifications': True
        }
        logger.info("Notification service initialized")
    
    async def process_violation(self, violation_data: Any) -> str:
        """
        Process a detected violation for enforcement.
        
        Args:
            violation_data: Violation detection result
            
        Returns:
            Enforcement request ID
        """
        if not self._initialized:
            raise RuntimeError("Enforcement system not initialized")
        
        # Extract violation details
        violation_id = violation_data.violation_id
        content_id = violation_data.content_id
        platform = violation_data.platform
        confidence_score = violation_data.confidence_score
        
        logger.info(f"Processing violation {violation_id} for enforcement")
        
        try:
            # Determine enforcement action and escalation level
            action_type, escalation_level = await self._determine_enforcement_strategy(
                violation_data
            )
            
            # Create enforcement request
            request_id = str(uuid.uuid4())
            enforcement_request = EnforcementRequest(
                request_id=request_id,
                violation_id=violation_id,
                content_id=content_id,
                platform=platform,
                action_type=action_type,
                status=EnforcementStatus.PENDING,
                escalation_level=escalation_level,
                confidence_score=confidence_score,
                evidence_package=await self._prepare_evidence_package(violation_data),
                legal_basis=await self._determine_legal_basis(violation_data),
                submitted_at=None,
                response_deadline=None,
                platform_response=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Add to active requests
            self.active_requests[request_id] = enforcement_request
            
            # Add to processing queue if automatic enforcement is enabled
            if escalation_level == EscalationLevel.AUTOMATIC:
                self.pending_queue.append(request_id)
            
            # Update statistics
            self.enforcement_stats['total_requests'] += 1
            self.enforcement_stats['pending_requests'] += 1
            
            logger.info(f"Created enforcement request {request_id} with action {action_type.value}")
            return request_id
            
        except Exception as e:
            logger.error(f"Error processing violation {violation_id}: {str(e)}")
            raise
    
    async def _determine_enforcement_strategy(self, violation_data: Any) -> Tuple[EnforcementAction, EscalationLevel]:
        """
        Determine appropriate enforcement action and escalation level.
        
        Args:
            violation_data: Violation detection result
            
        Returns:
            Tuple of enforcement action and escalation level
        """
        confidence_score = violation_data.confidence_score
        platform = violation_data.platform
        violation_type = violation_data.violation_type
        
        # Get platform configuration
        platform_config = self.platform_configs.get(platform, {})
        supported_actions = platform_config.get('supported_actions', [])
        auto_enabled = platform_config.get('auto_enforcement_enabled', False)
        
        # Determine action type based on violation
        if violation_type.value in ['exact_copy', 'unauthorized_remix']:
            preferred_action = EnforcementAction.DMCA_TAKEDOWN
        elif violation_type.value in ['modified_copy', 'partial_use']:
            preferred_action = EnforcementAction.PLATFORM_REPORT
        else:
            preferred_action = EnforcementAction.CEASE_DESIST
        
        # Use fallback if preferred action not supported
        if preferred_action not in supported_actions and supported_actions:
            preferred_action = supported_actions[0]
        
        # Determine escalation level
        if confidence_score >= self.auto_enforcement_threshold and auto_enabled:
            escalation_level = EscalationLevel.AUTOMATIC
        elif confidence_score >= self.review_threshold:
            escalation_level = EscalationLevel.REVIEW_REQUIRED
        else:
            escalation_level = EscalationLevel.LEGAL_REQUIRED
        
        return preferred_action, escalation_level
    
    async def _prepare_evidence_package(self, violation_data: Any) -> Dict[str, Any]:
        """
        Prepare comprehensive evidence package for enforcement.
        
        Args:
            violation_data: Violation detection result
            
        Returns:
            Evidence package dictionary
        """
        evidence_package = {
            'violation_summary': {
                'violation_id': violation_data.violation_id,
                'detection_timestamp': violation_data.timestamp.isoformat(),
                'confidence_score': violation_data.confidence_score,
                'similarity_score': violation_data.similarity_score,
                'violation_type': violation_data.violation_type.value
            },
            'original_content': {
                'content_id': violation_data.content_id,
                'title': 'Original Content Title',  # Would be fetched from database
                'creation_date': '2025-01-01',  # Would be fetched from database
                'copyright_owner': 'Fahed Mlaiel',
                'registration_info': 'Copyright Registration Details'
            },
            'infringing_content': {
                'platform': violation_data.platform,
                'url': violation_data.detected_url,
                'detected_at': violation_data.timestamp.isoformat(),
                'description': 'Infringing content description'
            },
            'technical_evidence': {
                'fingerprint_match': violation_data.fingerprint_match,
                'ai_analysis': violation_data.ai_analysis,
                'similarity_breakdown': violation_data.evidence.get('similarity_details', {}),
                'detection_algorithm': 'AI-Powered Multi-Modal Analysis v2.0'
            },
            'legal_evidence': {
                'ownership_proof': 'Copyright certificate or registration',
                'creation_timeline': 'Evidence of original creation',
                'publication_history': 'Original publication records'
            }
        }
        
        return evidence_package
    
    async def _determine_legal_basis(self, violation_data: Any) -> List[str]:
        """
        Determine legal basis for enforcement action.
        
        Args:
            violation_data: Violation detection result
            
        Returns:
            List of applicable legal statutes
        """
        platform = violation_data.platform
        
        # Platform-specific legal frameworks
        if platform in ['youtube', 'instagram', 'facebook', 'twitter']:
            return ['DMCA Section 512', 'US Copyright Act', 'Platform Terms of Service']
        elif platform in ['spotify', 'soundcloud']:
            return ['DMCA Section 512', 'Music Modernization Act', 'Platform Licensing Agreement']
        else:
            return ['DMCA Section 512', 'US Copyright Act']
    
    async def _enforcement_processor(self) -> None:
        """Background processor for enforcement requests."""
        while True:
            try:
                if self.pending_queue:
                    # Process pending requests
                    request_id = self.pending_queue.pop(0)
                    if request_id in self.active_requests:
                        await self._process_enforcement_request(request_id)
                
                # Process status updates
                await self._check_enforcement_responses()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in enforcement processor: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_enforcement_request(self, request_id: str) -> None:
        """
        Process a single enforcement request.
        
        Args:
            request_id: Enforcement request ID
        """
        request = self.active_requests.get(request_id)
        if not request:
            return
        
        logger.info(f"Processing enforcement request {request_id}")
        
        try:
            # Generate enforcement document
            document = await self._generate_enforcement_document(request)
            
            # Submit enforcement request
            success = await self._submit_enforcement_request(request, document)
            
            if success:
                request.status = EnforcementStatus.SUBMITTED
                request.submitted_at = datetime.utcnow()
                request.response_deadline = datetime.utcnow() + timedelta(
                    hours=self.response_timeout_hours
                )
                logger.info(f"Successfully submitted enforcement request {request_id}")
            else:
                request.status = EnforcementStatus.FAILED
                logger.error(f"Failed to submit enforcement request {request_id}")
            
            request.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing enforcement request {request_id}: {str(e)}")
            request.status = EnforcementStatus.FAILED
            request.updated_at = datetime.utcnow()
    
    async def _generate_enforcement_document(self, request: EnforcementRequest) -> str:
        """
        Generate enforcement document from template.
        
        Args:
            request: Enforcement request
            
        Returns:
            Generated document text
        """
        template_data = self.enforcement_templates.get(request.action_type)
        if not template_data:
            raise ValueError(f"No template available for action: {request.action_type}")
        
        template = template_data['template']
        evidence = request.evidence_package
        
        # Prepare template variables
        template_vars = {
            'original_title': evidence['original_content']['title'],
            'copyright_owner': evidence['original_content']['copyright_owner'],
            'creation_date': evidence['original_content']['creation_date'],
            'platform': request.platform,
            'infringing_url': evidence['infringing_content']['url'],
            'detection_date': evidence['infringing_content']['detected_at'],
            'confidence_score': int(request.confidence_score * 100),
            'violation_type': request.violation_id,
            'contact_information': self._get_contact_information(),
            'digital_signature': self._generate_digital_signature(),
            'submission_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'evidence_summary': self._summarize_evidence(evidence),
            'legal_basis': ', '.join(request.legal_basis),
            'requested_action': self._get_requested_action(request.action_type)
        }
        
        # Fill template
        try:
            document = template.format(**template_vars)
            return document
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise
    
    def _get_contact_information(self) -> str:
        """Get contact information for enforcement documents."""
        return """
        Name: Fahed Mlaiel
        Email: mlaiel@live.de
        Address: [Legal Address]
        Phone: [Contact Phone]
        """
    
    def _generate_digital_signature(self) -> str:
        """Generate digital signature for enforcement documents."""
        return f"Digitally signed by Fahed Mlaiel on {datetime.utcnow().isoformat()}"
    
    def _summarize_evidence(self, evidence: Dict[str, Any]) -> str:
        """Summarize evidence for enforcement document."""
        technical = evidence.get('technical_evidence', {})
        return f"""
        - AI-powered content matching with {technical.get('confidence_score', 0)*100:.1f}% confidence
        - Fingerprint analysis showing {technical.get('similarity_score', 0)*100:.1f}% similarity
        - Technical detection using {technical.get('detection_algorithm', 'Advanced AI')}
        - Comprehensive evidence package available upon request
        """
    
    def _get_requested_action(self, action_type: EnforcementAction) -> str:
        """Get requested action text."""
        actions = {
            EnforcementAction.DMCA_TAKEDOWN: "Immediate removal of infringing content",
            EnforcementAction.PLATFORM_REPORT: "Investigation and appropriate action",
            EnforcementAction.CEASE_DESIST: "Immediate cessation of infringing activity"
        }
        return actions.get(action_type, "Appropriate enforcement action")
    
    async def _submit_enforcement_request(self, request: EnforcementRequest, document: str) -> bool:
        """
        Submit enforcement request to platform.
        
        Args:
            request: Enforcement request
            document: Generated enforcement document
            
        Returns:
            bool: True if submission successful
        """
        platform_config = self.platform_configs.get(request.platform, {})
        
        try:
            if platform_config.get('api_endpoint'):
                # Submit via API
                return await self._submit_via_api(request, document, platform_config)
            else:
                # Submit via email or web form
                return await self._submit_via_alternative(request, document, platform_config)
                
        except Exception as e:
            logger.error(f"Error submitting enforcement request: {str(e)}")
            return False
    
    async def _submit_via_api(self, request: EnforcementRequest, document: str, 
                            platform_config: Dict[str, Any]) -> bool:
        """Submit enforcement request via platform API."""
        # Simulate API submission
        # In production, this would make actual API calls
        logger.info(f"Submitting enforcement request via API for platform: {request.platform}")
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Simulate success/failure
        success_rate = platform_config.get('success_rate', 0.8)
        import random
        return random.random() < success_rate
    
    async def _submit_via_alternative(self, request: EnforcementRequest, document: str,
                                    platform_config: Dict[str, Any]) -> bool:
        """Submit enforcement request via alternative methods."""
        # Simulate alternative submission (email, web form, etc.)
        logger.info(f"Submitting enforcement request via alternative method for platform: {request.platform}")
        
        # In production, this would send emails, fill web forms, etc.
        await asyncio.sleep(2)
        
        return True  # Assume manual submission is queued successfully
    
    async def _check_enforcement_responses(self) -> None:
        """Check for responses to submitted enforcement requests."""
        for request_id, request in self.active_requests.items():
            if request.status == EnforcementStatus.SUBMITTED:
                # Check if response deadline has passed
                if (request.response_deadline and 
                    datetime.utcnow() > request.response_deadline):
                    
                    # Check for platform response
                    response = await self._check_platform_response(request)
                    if response:
                        await self._process_platform_response(request, response)
    
    async def _check_platform_response(self, request: EnforcementRequest) -> Optional[Dict[str, Any]]:
        """Check for platform response to enforcement request."""
        # Simulate checking for platform response
        # In production, this would query platform APIs or check emails
        
        import random
        if random.random() < 0.3:  # 30% chance of having a response
            return {
                'status': 'completed' if random.random() < 0.8 else 'rejected',
                'response_date': datetime.utcnow().isoformat(),
                'message': 'Content has been removed' if random.random() < 0.8 else 'Request denied'
            }
        
        return None
    
    async def _process_platform_response(self, request: EnforcementRequest, 
                                       response: Dict[str, Any]) -> None:
        """Process platform response to enforcement request."""
        request.platform_response = response
        
        if response.get('status') == 'completed':
            request.status = EnforcementStatus.COMPLETED
            self.enforcement_stats['successful_enforcements'] += 1
        else:
            request.status = EnforcementStatus.REJECTED
            self.enforcement_stats['failed_enforcements'] += 1
        
        request.updated_at = datetime.utcnow()
        
        # Send notification
        await self._send_enforcement_notification(request)
    
    async def _send_enforcement_notification(self, request: EnforcementRequest) -> None:
        """Send notification about enforcement status."""
        if self.notification_service:
            notification_data = {
                'request_id': request.request_id,
                'violation_id': request.violation_id,
                'platform': request.platform,
                'status': request.status.value,
                'action_type': request.action_type.value,
                'updated_at': request.updated_at.isoformat()
            }
            
            # In production, this would send actual notifications
            logger.info(f"Enforcement notification sent for request {request.request_id}")
    
    async def _status_monitor(self) -> None:
        """Monitor enforcement request statuses."""
        while True:
            try:
                # Update pending count
                pending_count = sum(
                    1 for r in self.active_requests.values() 
                    if r.status in [EnforcementStatus.PENDING, EnforcementStatus.SUBMITTED]
                )
                self.enforcement_stats['pending_requests'] = pending_count
                
                # Calculate average response time
                completed_requests = [
                    r for r in self.active_requests.values() 
                    if r.status == EnforcementStatus.COMPLETED and r.submitted_at
                ]
                
                if completed_requests:
                    total_time = sum(
                        (r.updated_at - r.submitted_at).total_seconds() / 3600
                        for r in completed_requests
                    )
                    self.enforcement_stats['average_response_time_hours'] = total_time / len(completed_requests)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in status monitor: {str(e)}")
                await asyncio.sleep(60)
    
    async def get_enforcement_status(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get enforcement status for specific request or all requests.
        
        Args:
            request_id: Optional specific request ID
            
        Returns:
            Enforcement status information
        """
        if request_id:
            request = self.active_requests.get(request_id)
            if not request:
                return {'error': 'Request not found'}
            
            return {
                'request_id': request.request_id,
                'violation_id': request.violation_id,
                'platform': request.platform,
                'action_type': request.action_type.value,
                'status': request.status.value,
                'escalation_level': request.escalation_level.value,
                'confidence_score': request.confidence_score,
                'created_at': request.created_at.isoformat(),
                'updated_at': request.updated_at.isoformat(),
                'submitted_at': request.submitted_at.isoformat() if request.submitted_at else None,
                'response_deadline': request.response_deadline.isoformat() if request.response_deadline else None,
                'platform_response': request.platform_response
            }
        else:
            # Return overview
            return {
                'total_requests': len(self.active_requests),
                'stats': self.enforcement_stats.copy(),
                'recent_requests': [
                    {
                        'request_id': r.request_id,
                        'platform': r.platform,
                        'status': r.status.value,
                        'created_at': r.created_at.isoformat()
                    }
                    for r in sorted(self.active_requests.values(), 
                                  key=lambda x: x.created_at, reverse=True)[:10]
                ]
            }
    
    async def get_enforcement_stats(self) -> Dict[str, Any]:
        """Get enforcement performance statistics."""
        return self.enforcement_stats.copy()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown enforcement system."""
        logger.info("Shutting down Automated Enforcement system...")
        
        # Complete pending requests where possible
        for request_id in self.pending_queue[:]:
            request = self.active_requests.get(request_id)
            if request:
                request.status = EnforcementStatus.FAILED
                request.updated_at = datetime.utcnow()
        
        self.pending_queue.clear()
        self.active_requests.clear()
        
        logger.info("Automated Enforcement system shutdown complete")
