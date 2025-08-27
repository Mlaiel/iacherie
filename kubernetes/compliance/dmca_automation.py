"""
IA Influencer Agent - DMCA Automation System
Automated Digital Millennium Copyright Act compliance and takedown management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.dmca import DMCARequest, TakedownNotice, ContentMatch
from backend.models.content import ContentFingerprint
from backend.utils.email import send_dmca_notice
from backend.utils.web_scraping import capture_webpage_evidence
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel

logger = get_logger(__name__)


class DMCARequestType(str, Enum):
    """DMCA request types"""
    TAKEDOWN = "takedown"
    COUNTER_NOTICE = "counter_notice"
    REPEAT_INFRINGER = "repeat_infringer"
    SAFE_HARBOR = "safe_harbor"


class TakedownStatus(str, Enum):
    """DMCA takedown status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    COMPLIED = "complied"
    DISPUTED = "disputed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class InfringementType(str, Enum):
    """Copyright infringement types"""
    EXACT_COPY = "exact_copy"
    SUBSTANTIAL_SIMILARITY = "substantial_similarity"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    STREAMING = "streaming"
    DOWNLOAD = "download"


@dataclass
class InfringementEvidence:
    """Evidence of copyright infringement"""
    original_url: str
    infringing_url: str
    similarity_score: float
    fingerprint_match: bool
    screenshot_url: Optional[str]
    webpage_archive: Optional[str]
    timestamp: datetime
    detection_method: str
    metadata: Dict[str, Any]


@dataclass
class DMCANoticeTemplate:
    """DMCA takedown notice template"""
    template_id: str
    name: str
    subject_line: str
    body_template: str
    language: str
    platform_specific: bool
    platform_name: Optional[str]
    required_fields: List[str]
    optional_fields: List[str]


class DMCAAutomation:
    """Automated DMCA compliance and takedown system"""
    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.automated_takedowns = settings.DMCA_AUTOMATED_TAKEDOWNS
        self.similarity_threshold = settings.DMCA_SIMILARITY_THRESHOLD
        self.response_deadline_days = settings.DMCA_RESPONSE_DEADLINE_DAYS
        
        # Platform-specific takedown configurations
        self.platform_configs = {
            "youtube": {
                "api_endpoint": "https://www.youtube.com/copyright_complaint_form",
                "email": "copyright@youtube.com",
                "format": "youtube_specific",
                "response_time": 24  # hours
            },
            "instagram": {
                "api_endpoint": "https://help.instagram.com/contact/372592039493026",
                "email": "ip@facebook.com",
                "format": "facebook_specific",
                "response_time": 48
            },
            "tiktok": {
                "api_endpoint": "https://www.tiktok.com/legal/copyright-policy",
                "email": "copyright@tiktok.com",
                "format": "standard",
                "response_time": 72
            },
            "twitter": {
                "api_endpoint": "https://help.twitter.com/forms/dmca",
                "email": "copyright@twitter.com",
                "format": "twitter_specific",
                "response_time": 24
            }
        }
        
        # DMCA notice templates
        self.notice_templates = self._load_dmca_templates()
    
    async def detect_infringement(
        self,
        content_id: str,
        fingerprint_hash: str,
        monitoring_platforms: List[str] = None
    ) -> List[InfringementEvidence]:
        """Detect copyright infringement using AI fingerprinting"""
        try:
            infringements = []
            platforms = monitoring_platforms or list(self.platform_configs.keys())
            
            # Search for similar content across platforms
            for platform in platforms:
                try:
                    matches = await self._search_platform_for_matches(
                        platform, fingerprint_hash
                    )
                    
                    for match in matches:
                        if match["similarity_score"] >= self.similarity_threshold:
                            # Collect evidence
                            evidence = await self._collect_infringement_evidence(
                                content_id, match, platform
                            )
                            infringements.append(evidence)
                            
                except Exception as e:
                    self.logger.error(f"Error searching {platform} for matches: {str(e)}")
                    continue
            
            # Log detection results
            await self.audit_logger.log_audit_event(
                event_type="infringement_detection",
                category=AuditCategory.CONTENT_PROTECTION,
                level=AuditLevel.INFO,
                message=f"Infringement detection completed for content {content_id}",
                details={
                    "content_id": content_id,
                    "platforms_searched": platforms,
                    "infringements_found": len(infringements),
                    "similarity_threshold": self.similarity_threshold
                }
            )
            
            return infringements
            
        except Exception as e:
            self.logger.error(f"Error in infringement detection: {str(e)}")
            return []
    
    async def generate_takedown_notice(
        self,
        user_id: int,
        content_id: str,
        infringement_evidence: InfringementEvidence,
        platform: str,
        custom_message: str = None
    ) -> Dict[str, Any]:
        """Generate DMCA takedown notice for platform"""
        try:
            # Get content details
            async with get_db_session() as session:
                content_result = await session.execute(
                    select(ContentFingerprint).where(ContentFingerprint.id == content_id)
                )
                content = content_result.scalar_one_or_none()
                
                if not content:
                    raise HTTPException(status_code=404, detail="Content not found")
                
                # Get user details
                user_result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
            
            # Select appropriate template
            template = self._select_notice_template(platform)
            
            # Generate notice content
            notice_data = {
                "notice_id": f"DMCA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{content_id[:8]}",
                "generated_date": datetime.utcnow(),
                "copyright_owner": {
                    "name": user.full_name or user.username,
                    "email": user.email,
                    "address": user.address or "Address on file",
                    "phone": user.phone or "Phone on file"
                },
                "copyrighted_work": {
                    "title": content.title or f"Original Work {content_id}",
                    "description": content.description or "Original creative work",
                    "creation_date": content.created_at.isoformat(),
                    "original_url": content.original_url,
                    "registration_number": content.copyright_registration
                },
                "infringing_material": {
                    "url": infringement_evidence.infringing_url,
                    "description": "Unauthorized copy of copyrighted material",
                    "location": self._extract_platform_location(infringement_evidence.infringing_url),
                    "detection_date": infringement_evidence.timestamp.isoformat(),
                    "similarity_score": infringement_evidence.similarity_score
                },
                "evidence": {
                    "screenshot_url": infringement_evidence.screenshot_url,
                    "archive_url": infringement_evidence.webpage_archive,
                    "fingerprint_match": infringement_evidence.fingerprint_match,
                    "detection_method": infringement_evidence.detection_method
                },
                "good_faith_statement": True,
                "accuracy_statement": True,
                "perjury_statement": True,
                "custom_message": custom_message
            }
            
            # Format notice using template
            formatted_notice = await self._format_notice_with_template(
                template, notice_data, platform
            )
            
            # Store DMCA request
            dmca_request_id = await self._store_dmca_request(
                user_id, content_id, infringement_evidence, notice_data, formatted_notice
            )
            
            return {
                "dmca_request_id": dmca_request_id,
                "notice_id": notice_data["notice_id"],
                "platform": platform,
                "target_url": infringement_evidence.infringing_url,
                "formatted_notice": formatted_notice,
                "evidence_collected": {
                    "screenshot": bool(infringement_evidence.screenshot_url),
                    "archive": bool(infringement_evidence.webpage_archive),
                    "fingerprint_match": infringement_evidence.fingerprint_match
                },
                "next_steps": self._get_platform_submission_instructions(platform)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating takedown notice: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate takedown notice")
    
    async def submit_automated_takedown(
        self,
        dmca_request_id: str,
        platform: str,
        auto_submit: bool = None
    ) -> Dict[str, Any]:
        """Submit DMCA takedown notice automatically if configured"""
        try:
            auto_submit = auto_submit if auto_submit is not None else self.automated_takedowns
            
            if not auto_submit:
                return {"status": "manual_submission_required", "auto_submit": False}
            
            platform_config = self.platform_configs.get(platform)
            if not platform_config:
                raise ValueError(f"Platform not configured: {platform}")
            
            # Get DMCA request details
            async with get_db_session() as session:
                dmca_result = await session.execute(
                    select(DMCARequest).where(DMCARequest.request_id == dmca_request_id)
                )
                dmca_request = dmca_result.scalar_one_or_none()
                
                if not dmca_request:
                    raise HTTPException(status_code=404, detail="DMCA request not found")
            
            # Submit to platform
            submission_result = await self._submit_to_platform(
                platform, dmca_request, platform_config
            )
            
            # Update request status
            async with get_db_session() as session:
                await session.execute(
                    update(DMCARequest)
                    .where(DMCARequest.request_id == dmca_request_id)
                    .values(
                        status=TakedownStatus.SENT.value,
                        submitted_at=datetime.utcnow(),
                        platform_response=json.dumps(submission_result),
                        response_deadline=datetime.utcnow() + timedelta(
                            hours=platform_config["response_time"]
                        )
                    )
                )
                await session.commit()
            
            # Log submission
            await self.audit_logger.log_audit_event(
                event_type="dmca_takedown_submitted",
                category=AuditCategory.CONTENT_PROTECTION,
                level=AuditLevel.INFO,
                message=f"DMCA takedown submitted to {platform}",
                details={
                    "dmca_request_id": dmca_request_id,
                    "platform": platform,
                    "submission_method": "automated",
                    "platform_response": submission_result
                }
            )
            
            return {
                "status": "submitted",
                "platform": platform,
                "submission_time": datetime.utcnow().isoformat(),
                "expected_response_time": platform_config["response_time"],
                "platform_confirmation": submission_result.get("confirmation_number"),
                "tracking_url": submission_result.get("tracking_url")
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting automated takedown: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to submit takedown")
    
    async def track_takedown_status(
        self,
        dmca_request_id: str
    ) -> Dict[str, Any]:
        """Track status of DMCA takedown request"""
        try:
            async with get_db_session() as session:
                # Get DMCA request
                dmca_result = await session.execute(
                    select(DMCARequest).where(DMCARequest.request_id == dmca_request_id)
                )
                dmca_request = dmca_result.scalar_one_or_none()
                
                if not dmca_request:
                    raise HTTPException(status_code=404, detail="DMCA request not found")
                
                # Check for status updates from platform
                current_status = await self._check_platform_status(
                    dmca_request.platform, dmca_request.platform_reference_id
                )
                
                # Update status if changed
                if current_status and current_status != dmca_request.status:
                    await session.execute(
                        update(DMCARequest)
                        .where(DMCARequest.request_id == dmca_request_id)
                        .values(
                            status=current_status,
                            last_status_check=datetime.utcnow()
                        )
                    )
                    await session.commit()
                    dmca_request.status = current_status
                
                # Calculate time metrics
                now = datetime.utcnow()
                time_elapsed = (now - dmca_request.submitted_at).total_seconds() / 3600 if dmca_request.submitted_at else 0
                time_remaining = ((dmca_request.response_deadline - now).total_seconds() / 3600) if dmca_request.response_deadline else None
                
                return {
                    "dmca_request_id": dmca_request_id,
                    "status": dmca_request.status,
                    "platform": dmca_request.platform,
                    "target_url": dmca_request.infringing_url,
                    "submitted_at": dmca_request.submitted_at.isoformat() if dmca_request.submitted_at else None,
                    "response_deadline": dmca_request.response_deadline.isoformat() if dmca_request.response_deadline else None,
                    "time_elapsed_hours": round(time_elapsed, 2),
                    "time_remaining_hours": round(time_remaining, 2) if time_remaining else None,
                    "platform_reference": dmca_request.platform_reference_id,
                    "last_update": dmca_request.last_status_check.isoformat() if dmca_request.last_status_check else None,
                    "resolution_details": json.loads(dmca_request.resolution_details) if dmca_request.resolution_details else None
                }
                
        except Exception as e:
            self.logger.error(f"Error tracking takedown status: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to track takedown status")
    
    async def process_counter_notice(
        self,
        dmca_request_id: str,
        counter_notice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process DMCA counter-notice received"""
        try:
            async with get_db_session() as session:
                # Get original DMCA request
                dmca_result = await session.execute(
                    select(DMCARequest).where(DMCARequest.request_id == dmca_request_id)
                )
                dmca_request = dmca_result.scalar_one_or_none()
                
                if not dmca_request:
                    raise HTTPException(status_code=404, detail="DMCA request not found")
                
                # Create counter-notice record
                counter_notice_id = f"CN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{dmca_request_id[-8:]}"
                
                counter_notice = CounterNotice(
                    counter_notice_id=counter_notice_id,
                    original_dmca_id=dmca_request_id,
                    counter_claimant_name=counter_notice_data["claimant_name"],
                    counter_claimant_email=counter_notice_data["claimant_email"],
                    counter_claimant_address=counter_notice_data["claimant_address"],
                    good_faith_statement=counter_notice_data["good_faith_statement"],
                    consent_to_jurisdiction=counter_notice_data["consent_to_jurisdiction"],
                    perjury_statement=counter_notice_data["perjury_statement"],
                    counter_notice_text=counter_notice_data["notice_text"],
                    received_at=datetime.utcnow(),
                    processed=False
                )
                
                session.add(counter_notice)
                
                # Update original DMCA request status
                await session.execute(
                    update(DMCARequest)
                    .where(DMCARequest.request_id == dmca_request_id)
                    .values(
                        status=TakedownStatus.DISPUTED.value,
                        counter_notice_received=True,
                        counter_notice_date=datetime.utcnow()
                    )
                )
                
                await session.commit()
            
            # Log counter-notice
            await self.audit_logger.log_audit_event(
                event_type="dmca_counter_notice_received",
                category=AuditCategory.CONTENT_PROTECTION,
                level=AuditLevel.WARNING,
                message=f"DMCA counter-notice received for {dmca_request_id}",
                details={
                    "dmca_request_id": dmca_request_id,
                    "counter_notice_id": counter_notice_id,
                    "claimant": counter_notice_data["claimant_name"]
                }
            )
            
            # Notify original copyright owner
            await self._notify_copyright_owner_of_counter_notice(
                dmca_request.user_id, dmca_request_id, counter_notice_data
            )
            
            return {
                "counter_notice_id": counter_notice_id,
                "status": "received",
                "original_dmca_id": dmca_request_id,
                "next_steps": [
                    "Review counter-notice claims",
                    "Decide whether to file legal action",
                    "If no action taken within 10-14 business days, content may be restored"
                ],
                "legal_deadline": (datetime.utcnow() + timedelta(days=14)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing counter-notice: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process counter-notice")
    
    async def _search_platform_for_matches(
        self,
        platform: str,
        fingerprint_hash: str
    ) -> List[Dict[str, Any]]:
        """Search platform for content matches using fingerprint"""
        try:
            # This would integrate with platform-specific search APIs
            # or web scraping to find matching content
            matches = []
            
            # Placeholder for actual implementation
            # Real implementation would use:
            # - YouTube Data API for video searches
            # - Instagram Basic Display API
            # - TikTok Research API
            # - Twitter API v2
            # - Web scraping for platforms without APIs
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error searching platform {platform}: {str(e)}")
            return []
    
    async def _collect_infringement_evidence(
        self,
        content_id: str,
        match: Dict[str, Any],
        platform: str
    ) -> InfringementEvidence:
        """Collect evidence of copyright infringement"""
        try:
            # Capture screenshot
            screenshot_url = await capture_webpage_evidence(match["url"])
            
            # Archive webpage
            archive_url = await self._archive_infringing_page(match["url"])
            
            return InfringementEvidence(
                original_url=match.get("original_url", ""),
                infringing_url=match["url"],
                similarity_score=match["similarity_score"],
                fingerprint_match=match.get("fingerprint_match", False),
                screenshot_url=screenshot_url,
                webpage_archive=archive_url,
                timestamp=datetime.utcnow(),
                detection_method="automated_fingerprint_matching",
                metadata={
                    "platform": platform,
                    "content_id": content_id,
                    "match_details": match
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting evidence: {str(e)}")
            raise
    
    def _load_dmca_templates(self) -> Dict[str, DMCANoticeTemplate]:
        """Load DMCA notice templates for different platforms"""
        return {
            "standard": DMCANoticeTemplate(
                template_id="standard",
                name="Standard DMCA Takedown Notice",
                subject_line="DMCA Takedown Notice - Copyright Infringement",
                body_template="""
DMCA TAKEDOWN NOTICE

Date: {date}
Notice ID: {notice_id}

To: {platform_name} Copyright Agent

I, {copyright_owner_name}, am the owner of the copyrighted work described below, and I hereby request that you remove or disable access to the infringing material.

COPYRIGHTED WORK:
Title: {work_title}
Description: {work_description}
Original URL: {original_url}
Creation Date: {creation_date}

INFRINGING MATERIAL:
URL: {infringing_url}
Description: {infringement_description}
Detection Date: {detection_date}

EVIDENCE:
Similarity Score: {similarity_score}%
Fingerprint Match: {fingerprint_match}
Screenshot: {screenshot_url}
Archive: {archive_url}

GOOD FAITH STATEMENT:
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT:
The information in this notification is accurate.

PERJURY STATEMENT:
I swear, under penalty of perjury, that I am the copyright owner or authorized to act on behalf of the copyright owner.

Contact Information:
Name: {copyright_owner_name}
Email: {copyright_owner_email}
Address: {copyright_owner_address}
Phone: {copyright_owner_phone}

Signature: {signature}
                """,
                language="en",
                platform_specific=False,
                platform_name=None,
                required_fields=[
                    "copyright_owner_name", "work_title", "infringing_url",
                    "copyright_owner_email", "copyright_owner_address"
                ],
                optional_fields=["custom_message", "copyright_owner_phone"]
            )
        }


# Export for use in other modules
__all__ = ["DMCAAutomation", "DMCARequestType", "TakedownStatus", "InfringementType"]
