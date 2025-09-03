"""DMCA Handler - Gestion DMCA

DMCA and legal protection service consolidating existing DMCA functionality.
Provides automated DMCA takedown notice generation and legal protection services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime in a timezone-aware manner"""
    return datetime.now(timezone.utc)


class NoticeType(Enum):
    """Types of legal notices"""
    DMCA_TAKEDOWN = "dmca_takedown"
    COUNTER_NOTICE = "counter_notice"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_CLAIM = "copyright_claim"
    TRADEMARK_CLAIM = "trademark_claim"


class NoticeStatus(Enum):
    """Status of legal notices"""
    DRAFT = "draft"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    COMPLIED = "complied"
    DISPUTED = "disputed"
    ESCALATED = "escalated"


class InfringementType(Enum):
    """Types of copyright infringement"""
    UNAUTHORIZED_USE = "unauthorized_use"
    PLAGIARISM = "plagiarism"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    DERIVATIVE_WORK = "derivative_work"


@dataclass
class InfringementEvidence:
    """Evidence of copyright infringement"""
    evidence_type: str
    description: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    timestamp: datetime = field(default_factory=utc_now)
    hash_signature: Optional[str] = None


@dataclass
class DMCANotice:
    """DMCA takedown notice"""
    notice_id: str
    notice_type: NoticeType
    status: NoticeStatus
    created_at: datetime
    
    # Copyright holder information
    copyright_holder: str
    copyright_holder_contact: Dict[str, str]
    
    # Infringement details
    infringement_type: InfringementType
    original_work_description: str
    original_work_url: Optional[str]
    infringing_url: str
    infringing_description: str
    
    # Platform/recipient information
    platform_name: str
    platform_contact: Dict[str, str]
    
    # Evidence
    evidence: List[InfringementEvidence] = field(default_factory=list)
    
    # Notice text
    notice_text: Optional[str] = None
    
    # Response tracking
    sent_at: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    response_received_at: Optional[datetime] = None
    compliance_confirmed_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CounterNotice:
    """DMCA counter-notice"""
    counter_notice_id: str
    original_notice_id: str
    created_at: datetime
    
    # Counter-claimant information
    counter_claimant: str
    counter_claimant_contact: Dict[str, str]
    
    # Counter-claim details
    disputed_claim: str
    good_faith_belief: str
    penalty_acknowledgment: bool
    
    # Response
    counter_notice_text: Optional[str] = None
    sent_at: Optional[datetime] = None


class DMCAHandler:
    """
    DMCA and legal protection service.
    Consolidates functionality from ai_engine/content_protection/dmca.py
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.config = config or {}
        
        # Storage for notices (use database in production)
        self.dmca_notices: Dict[str, DMCANotice] = {}
        self.counter_notices: Dict[str, CounterNotice] = {}
        
        # Configuration
        self.auto_send = self.config.get('auto_send', False)
        self.response_deadline_days = self.config.get('response_deadline_days', 7)
        
        # Legal templates and contacts
        self._load_legal_templates()
    
    def _load_legal_templates(self):
        """Load legal notice templates"""
        self.templates = {
            NoticeType.DMCA_TAKEDOWN: """
DMCA TAKEDOWN NOTICE

To: {platform_name}
Contact: {platform_contact}

I am writing to notify you of copyright infringement occurring on your platform.

COPYRIGHT HOLDER INFORMATION:
Name: {copyright_holder}
Contact: {copyright_holder_contact}

COPYRIGHTED WORK:
Description: {original_work_description}
Original Location: {original_work_url}

INFRINGING MATERIAL:
Location: {infringing_url}
Description: {infringing_description}

GOOD FAITH BELIEF:
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the copyright owner.

SIGNATURE:
{copyright_holder}
Date: {date}

This notice is sent in accordance with the Digital Millennium Copyright Act (DMCA).
""",
            NoticeType.COUNTER_NOTICE: """
DMCA COUNTER-NOTICE

To: {platform_name}

I am responding to the DMCA takedown notice regarding content that was removed from your platform.

COUNTER-CLAIMANT INFORMATION:
Name: {counter_claimant}
Contact: {counter_claimant_contact}

DISPUTED CLAIM:
{disputed_claim}

GOOD FAITH BELIEF:
{good_faith_belief}

PENALTY ACKNOWLEDGMENT:
I consent to the jurisdiction of Federal District Court for the judicial district in which my address is located, and I will accept service of process from the person who provided the DMCA notification.

SIGNATURE:
{counter_claimant}
Date: {date}
"""
        }
    
    async def create_dmca_notice(
        self,
        copyright_holder: str,
        copyright_holder_contact: Dict[str, str],
        original_work_description: str,
        infringing_url: str,
        infringing_description: str,
        platform_name: str,
        platform_contact: Dict[str, str],
        infringement_type: InfringementType = InfringementType.UNAUTHORIZED_USE,
        original_work_url: Optional[str] = None,
        evidence: Optional[List[InfringementEvidence]] = None
    ) -> str:
        """
        Create a DMCA takedown notice
        
        Returns:
            Notice ID
        """
        try:
            notice_id = str(uuid.uuid4())
            
            # Validate URLs
            if not self._is_valid_url(infringing_url):
                raise ValueError("Invalid infringing URL")
            
            if original_work_url and not self._is_valid_url(original_work_url):
                raise ValueError("Invalid original work URL")
            
            # Create notice
            notice = DMCANotice(
                notice_id=notice_id,
                notice_type=NoticeType.DMCA_TAKEDOWN,
                status=NoticeStatus.DRAFT,
                created_at=utc_now(),
                copyright_holder=copyright_holder,
                copyright_holder_contact=copyright_holder_contact,
                infringement_type=infringement_type,
                original_work_description=original_work_description,
                original_work_url=original_work_url,
                infringing_url=infringing_url,
                infringing_description=infringing_description,
                evidence=evidence or [],
                platform_name=platform_name,
                platform_contact=platform_contact
            )
            
            # Generate notice text
            notice.notice_text = self._generate_notice_text(notice)
            
            # Set response deadline
            notice.response_deadline = utc_now() + timedelta(days=self.response_deadline_days)
            
            # Store notice
            self.dmca_notices[notice_id] = notice
            
            self.logger.info(f"Created DMCA notice {notice_id} for {platform_name}")
            
            # Auto-send if configured
            if self.auto_send:
                await self.send_notice(notice_id)
            
            return notice_id
            
        except Exception as e:
            self.logger.error(f"Failed to create DMCA notice: {str(e)}")
            raise
    
    async def create_counter_notice(
        self,
        original_notice_id: str,
        counter_claimant: str,
        counter_claimant_contact: Dict[str, str],
        disputed_claim: str,
        good_faith_belief: str
    ) -> str:
        """
        Create a DMCA counter-notice
        
        Returns:
            Counter-notice ID
        """
        try:
            if original_notice_id not in self.dmca_notices:
                raise ValueError("Original DMCA notice not found")
            
            counter_notice_id = str(uuid.uuid4())
            
            counter_notice = CounterNotice(
                counter_notice_id=counter_notice_id,
                original_notice_id=original_notice_id,
                created_at=utc_now(),
                counter_claimant=counter_claimant,
                counter_claimant_contact=counter_claimant_contact,
                disputed_claim=disputed_claim,
                good_faith_belief=good_faith_belief,
                penalty_acknowledgment=True
            )
            
            # Generate counter-notice text
            counter_notice.counter_notice_text = self._generate_counter_notice_text(counter_notice)
            
            # Store counter-notice
            self.counter_notices[counter_notice_id] = counter_notice
            
            # Update original notice status
            original_notice = self.dmca_notices[original_notice_id]
            original_notice.status = NoticeStatus.DISPUTED
            
            self.logger.info(f"Created counter-notice {counter_notice_id} for notice {original_notice_id}")
            
            return counter_notice_id
            
        except Exception as e:
            self.logger.error(f"Failed to create counter-notice: {str(e)}")
            raise
    
    async def send_notice(self, notice_id: str) -> bool:
        """Send DMCA notice to platform"""
        try:
            if notice_id not in self.dmca_notices:
                raise ValueError("DMCA notice not found")
            
            notice = self.dmca_notices[notice_id]
            
            # Simulate sending notice (implement actual sending logic)
            success = await self._send_notice_to_platform(notice)
            
            if success:
                notice.status = NoticeStatus.SENT
                notice.sent_at = utc_now()
                
                self.logger.info(f"Sent DMCA notice {notice_id} to {notice.platform_name}")
                return True
            else:
                self.logger.error(f"Failed to send DMCA notice {notice_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error sending notice: {str(e)}")
            return False
    
    async def record_compliance(self, notice_id: str, compliance_details: Dict[str, Any]) -> bool:
        """Record compliance with DMCA notice"""
        try:
            if notice_id not in self.dmca_notices:
                return False
            
            notice = self.dmca_notices[notice_id]
            notice.status = NoticeStatus.COMPLIED
            notice.compliance_confirmed_at = utc_now()
            notice.metadata.update(compliance_details)
            
            self.logger.info(f"Recorded compliance for DMCA notice {notice_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record compliance: {str(e)}")
            return False
    
    async def add_evidence(self, notice_id: str, evidence: InfringementEvidence) -> bool:
        """Add evidence to DMCA notice"""
        try:
            if notice_id not in self.dmca_notices:
                return False
            
            notice = self.dmca_notices[notice_id]
            notice.evidence.append(evidence)
            
            self.logger.info(f"Added evidence to DMCA notice {notice_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add evidence: {str(e)}")
            return False
    
    def _generate_notice_text(self, notice: DMCANotice) -> str:
        """Generate formatted DMCA notice text"""
        template = self.templates[notice.notice_type]
        
        return template.format(
            platform_name=notice.platform_name,
            platform_contact=self._format_contact(notice.platform_contact),
            copyright_holder=notice.copyright_holder,
            copyright_holder_contact=self._format_contact(notice.copyright_holder_contact),
            original_work_description=notice.original_work_description,
            original_work_url=notice.original_work_url or "Not provided",
            infringing_url=notice.infringing_url,
            infringing_description=notice.infringing_description,
            date=notice.created_at.strftime("%Y-%m-%d")
        )
    
    def _generate_counter_notice_text(self, counter_notice: CounterNotice) -> str:
        """Generate formatted counter-notice text"""
        template = self.templates[NoticeType.COUNTER_NOTICE]
        
        return template.format(
            platform_name="Platform",  # Would get from original notice
            counter_claimant=counter_notice.counter_claimant,
            counter_claimant_contact=self._format_contact(counter_notice.counter_claimant_contact),
            disputed_claim=counter_notice.disputed_claim,
            good_faith_belief=counter_notice.good_faith_belief,
            date=counter_notice.created_at.strftime("%Y-%m-%d")
        )
    
    def _format_contact(self, contact: Dict[str, str]) -> str:
        """Format contact information"""
        formatted = []
        for key, value in contact.items():
            formatted.append(f"{key.title()}: {value}")
        return "\n".join(formatted)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    async def _send_notice_to_platform(self, notice: DMCANotice) -> bool:
        """
        Send notice to platform (implement actual sending logic)
        This would integrate with email, API, or other notification systems
        """
        # Simulate sending
        await asyncio.sleep(0.1)
        return True
    
    async def get_notice_status(self, notice_id: str) -> Optional[Dict[str, Any]]:
        """Get status of DMCA notice"""
        if notice_id not in self.dmca_notices:
            return None
        
        notice = self.dmca_notices[notice_id]
        return {
            'notice_id': notice.notice_id,
            'status': notice.status.value,
            'created_at': notice.created_at.isoformat(),
            'sent_at': notice.sent_at.isoformat() if notice.sent_at else None,
            'platform_name': notice.platform_name,
            'infringement_type': notice.infringement_type.value,
            'response_deadline': notice.response_deadline.isoformat() if notice.response_deadline else None,
            'compliance_confirmed': notice.compliance_confirmed_at is not None
        }
    
    async def get_dmca_stats(self) -> Dict[str, Any]:
        """Get DMCA service statistics"""
        total_notices = len(self.dmca_notices)
        sent_notices = sum(1 for n in self.dmca_notices.values() if n.status != NoticeStatus.DRAFT)
        complied_notices = sum(1 for n in self.dmca_notices.values() if n.status == NoticeStatus.COMPLIED)
        
        return {
            'total_notices': total_notices,
            'sent_notices': sent_notices,
            'complied_notices': complied_notices,
            'counter_notices': len(self.counter_notices),
            'compliance_rate': complied_notices / max(sent_notices, 1),
            'auto_send_enabled': self.auto_send,
            'response_deadline_days': self.response_deadline_days,
            'last_updated': utc_now().isoformat()
        }
    
    async def check_overdue_notices(self) -> List[str]:
        """Check for overdue notices that haven't received responses"""
        overdue_notices = []
        current_time = utc_now()
        
        for notice_id, notice in self.dmca_notices.items():
            if (notice.status == NoticeStatus.SENT and 
                notice.response_deadline and 
                current_time > notice.response_deadline and
                not notice.response_received_at):
                overdue_notices.append(notice_id)
        
        return overdue_notices