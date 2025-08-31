"""DMCA Compliance Handler - Digital Millennium Copyright Act Enforcement

This module provides comprehensive DMCA compliance management for content protection,
automated takedown notice processing, counter-notifications, and safe harbor provisions.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  WARNING: Unauthorized use, reproduction, or distribution of this code is strictly prohibited.
    This system is proprietary and protected by international copyright laws.
    Violations will be prosecuted to the full extent of the law.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..security.encryption import EncryptionService
from ..utils.email_sender import EmailService
from ..models.dmca_models import DMCANotice, DMCAStatus, CounterNotification


class DMCANoticeType(Enum):
    """Types of DMCA notices"""    TAKEDOWN = "takedown"
    COUNTER_NOTIFICATION = "counter_notification"
    REPEAT_INFRINGER = "repeat_infringer"
    SAFE_HARBOR = "safe_harbor"


class DMCACompliance(Enum):
    """DMCA compliance levels"""    FULL_COMPLIANCE = "full_compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NON_COMPLIANCE = "non_compliance"
    PENDING_REVIEW = "pending_review"


class TakedownAction(Enum):
    """Actions for takedown notices"""    REMOVE_CONTENT = "remove_content"
    DISABLE_ACCESS = "disable_access"
    FORWARD_TO_USER = "forward_to_user"
    REJECT_INVALID = "reject_invalid"


@dataclass
class DMCARequest:
    """DMCA takedown request structure"""    content_id: str
    content_url: str
    infringing_url: str
    complainant_name: str
    complainant_email: str
    complainant_address: str
    copyright_owner: str
    copyrighted_work: str
    description: str
    good_faith_statement: bool
    accuracy_statement: bool
    electronic_signature: str
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default_factory=lambda: hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16])


@dataclass
class DMCAResponse:
    """DMCA response structure"""    request_id: str
    notice_id: str
    status: DMCACompliance
    action_taken: TakedownAction
    compliance_score: float
    response_time: float
    legal_review_required: bool
    auto_processed: bool
    timestamp: datetime = field(default_factory=datetime.now)


class DMCAHandler:
    """    Digital Millennium Copyright Act (DMCA) Compliance Handler
    
    Provides automated DMCA takedown processing, counter-notifications,
    safe harbor compliance, and repeat infringer management.
    """    
    def __init__(self, 
                 db_manager: DatabaseManager,
                 cache_manager: CacheManager,
                 encryption_service: EncryptionService,
                 email_service: EmailService):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.encryption_service = encryption_service
        self.email_service = email_service
        self.logger = logging.getLogger(__name__)
        
        # DMCA compliance configuration
        self.config = {
            "auto_process_threshold": 0.8,
            "legal_review_threshold": 0.6,
            "response_time_sla": 24,  # hours
            "repeat_infringer_strikes": 3,
            "safe_harbor_enabled": True,
            "counter_notification_period": 14,  # days
            "automated_takedown": True
        }
        
        # Active DMCA cases cache
        self.active_cases = {}
        
        # Email templates
        self.templates = {
            "takedown_notice": "dmca_takedown_notice.html",
            "counter_notification": "dmca_counter_notification.html",
            "infringement_warning": "dmca_infringement_warning.html",
            "compliance_report": "dmca_compliance_report.html"
        }
    
    async def process_takedown_request(self, request: DMCARequest) -> DMCAResponse:
        """        Process DMCA takedown request with automated validation and action
        
        Args:
            request: DMCA takedown request data
            
        Returns:
            DMCAResponse: Processing result with compliance status
        """        start_time = datetime.now()
        
        try:
            # Validate DMCA notice completeness
            validation_result = await self._validate_dmca_notice(request)
            
            if not validation_result["valid"]:
                return DMCAResponse(
                    request_id=request.request_id,
                    notice_id="",
                    status=DMCACompliance.NON_COMPLIANCE,
                    action_taken=TakedownAction.REJECT_INVALID,
                    compliance_score=0.0,
                    response_time=0.0,
                    legal_review_required=False,
                    auto_processed=True
                )
            
            # Create DMCA notice record
            notice_id = await self._create_dmca_notice(request)
            
            # Assess compliance level
            compliance_assessment = await self._assess_compliance_level(request)
            
            # Determine action based on compliance
            action = await self._determine_takedown_action(request, compliance_assessment)
            
            # Execute takedown action if required
            if action != TakedownAction.REJECT_INVALID:
                await self._execute_takedown_action(request, action)
            
            # Send notifications
            await self._send_dmca_notifications(request, notice_id, action)
            
            # Update case tracking
            response_time = (datetime.now() - start_time).total_seconds() / 3600
            
            response = DMCAResponse(
                request_id=request.request_id,
                notice_id=notice_id,
                status=compliance_assessment["status"],
                action_taken=action,
                compliance_score=compliance_assessment["score"],
                response_time=response_time,
                legal_review_required=compliance_assessment["legal_review"],
                auto_processed=compliance_assessment["score"] >= self.config["auto_process_threshold"]
            )
            
            # Cache active case
            self.active_cases[request.request_id] = response
            
            self.logger.info(f"DMCA takedown processed: {request.request_id} -> {action.value}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing DMCA takedown: {str(e)}")
            return DMCAResponse(
                request_id=request.request_id,
                notice_id="",
                status=DMCACompliance.NON_COMPLIANCE,
                action_taken=TakedownAction.REJECT_INVALID,
                compliance_score=0.0,
                response_time=0.0,
                legal_review_required=True,
                auto_processed=False
            )
    
    async def process_counter_notification(self, 
                                         notice_id: str, 
                                         counter_data: Dict[str, Any]) -> Dict[str, Any]:
        """        Process DMCA counter-notification under safe harbor provisions
        
        Args:
            notice_id: Original DMCA notice ID
            counter_data: Counter-notification data
            
        Returns:
            Dict: Counter-notification processing result
        """        try:
            # Validate counter-notification requirements
            validation = await self._validate_counter_notification(counter_data)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "reason": validation["errors"],
                    "action": "rejected"
                }
            
            # Check if within time limit
            notice = await self._get_dmca_notice(notice_id)
            if not notice:
                return {
                    "success": False,
                    "reason": "Original notice not found",
                    "action": "rejected"
                }
            
            time_elapsed = (datetime.now() - notice.created_at).days
            if time_elapsed > self.config["counter_notification_period"]:
                return {
                    "success": False,
                    "reason": "Counter-notification period expired",
                    "action": "rejected"
                }
            
            # Create counter-notification record
            counter_id = await self._create_counter_notification(notice_id, counter_data)
            
            # Schedule content restoration (10-14 business days)
            await self._schedule_content_restoration(notice_id, counter_id)
            
            # Notify original complainant
            await self._notify_original_complainant(notice_id, counter_id)
            
            self.logger.info(f"Counter-notification processed: {counter_id}")
            
            return {
                "success": True,
                "counter_id": counter_id,
                "action": "accepted",
                "restoration_date": datetime.now() + timedelta(days=14)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing counter-notification: {str(e)}")
            return {
                "success": False,
                "reason": str(e),
                "action": "error"
            }
    
    async def check_repeat_infringer(self, user_id: int) -> Dict[str, Any]:
        """        Check if user qualifies as repeat infringer under DMCA
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dict: Repeat infringer assessment
        """        try:
            # Get user's DMCA history
            with self.db_manager.get_session() as session:
                notices = session.query(DMCANotice).filter(
                    and_(
                        DMCANotice.target_user_id == user_id,
                        DMCANotice.status == DMCAStatus.VALID,
                        DMCANotice.created_at >= datetime.now() - timedelta(days=365)
                    )
                ).order_by(desc(DMCANotice.created_at)).all()
            
            strikes = len(notices)
            is_repeat_infringer = strikes >= self.config["repeat_infringer_strikes"]
            
            assessment = {
                "user_id": user_id,
                "total_strikes": strikes,
                "is_repeat_infringer": is_repeat_infringer,
                "recent_notices": [
                    {
                        "notice_id": notice.id,
                        "created_at": notice.created_at.isoformat(),
                        "content_type": notice.content_type,
                        "action_taken": notice.action_taken
                    }
                    for notice in notices[:5]  # Last 5 notices
                ],
                "recommended_action": "account_suspension" if is_repeat_infringer else "continue_monitoring"
            }
            
            # Cache assessment
            cache_key = f"repeat_infringer:{user_id}"
            await self.cache_manager.set(cache_key, assessment, ttl=3600)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error checking repeat infringer: {str(e)}")
            return {
                "user_id": user_id,
                "error": str(e),
                "is_repeat_infringer": False
            }
    
    async def generate_safe_harbor_report(self, period_days: int = 30) -> Dict[str, Any]:
        """        Generate DMCA safe harbor compliance report
        
        Args:
            period_days: Reporting period in days
            
        Returns:
            Dict: Comprehensive compliance report
        """        try:
            start_date = datetime.now() - timedelta(days=period_days)
            
            with self.db_manager.get_session() as session:
                # Get all DMCA notices in period
                notices = session.query(DMCANotice).filter(
                    DMCANotice.created_at >= start_date
                ).all()
                
                # Calculate metrics
                total_notices = len(notices)
                valid_notices = len([n for n in notices if n.status == DMCAStatus.VALID])
                auto_processed = len([n for n in notices if n.auto_processed])
                response_times = [n.response_time_hours for n in notices if n.response_time_hours]
                
                # Get counter-notifications
                counter_notifications = session.query(CounterNotification).filter(
                    CounterNotification.created_at >= start_date
                ).all()
                
                # Generate report
                report = {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": datetime.now().isoformat(),
                        "days": period_days
                    },
                    "takedown_notices": {
                        "total": total_notices,
                        "valid": valid_notices,
                        "invalid": total_notices - valid_notices,
                        "auto_processed": auto_processed,
                        "manual_review": total_notices - auto_processed
                    },
                    "response_metrics": {
                        "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
                        "sla_compliance": len([rt for rt in response_times if rt <= self.config["response_time_sla"]]) / len(response_times) if response_times else 0,
                        "fastest_response": min(response_times) if response_times else 0,
                        "slowest_response": max(response_times) if response_times else 0
                    },
                    "counter_notifications": {
                        "total": len(counter_notifications),
                        "accepted": len([cn for cn in counter_notifications if cn.status == "accepted"]),
                        "rejected": len([cn for cn in counter_notifications if cn.status == "rejected"])
                    },
                    "compliance_status": {
                        "safe_harbor_compliant": True,
                        "policy_url": "/dmca-policy",
                        "agent_contact": "dmca@ia-influencer.com",
                        "repeat_infringer_policy": True
                    },
                    "generated_at": datetime.now().isoformat()
                }
                
                return report
                
        except Exception as e:
            self.logger.error(f"Error generating safe harbor report: {str(e)}")
            return {"error": str(e)}
    
    async def _validate_dmca_notice(self, request: DMCARequest) -> Dict[str, Any]:
        """Validate DMCA notice completeness and legal requirements"""        errors = []
        
        # Required fields validation
        required_fields = [
            "complainant_name", "complainant_email", "complainant_address",
            "copyright_owner", "copyrighted_work", "description",
            "electronic_signature"
        ]
        
        for field in required_fields:
            if not getattr(request, field, None):
                errors.append(f"Missing required field: {field}")
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if request.complainant_email and not re.match(email_pattern, request.complainant_email):
            errors.append("Invalid email format")
        
        # Good faith and accuracy statements
        if not request.good_faith_statement:
            errors.append("Good faith statement required")
        
        if not request.accuracy_statement:
            errors.append("Accuracy statement required")
        
        # URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if request.content_url and not re.match(url_pattern, request.content_url):
            errors.append("Invalid content URL format")
        
        if request.infringing_url and not re.match(url_pattern, request.infringing_url):
            errors.append("Invalid infringing URL format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "score": max(0, 1 - (len(errors) * 0.1))
        }
    
    async def _assess_compliance_level(self, request: DMCARequest) -> Dict[str, Any]:
        """Assess DMCA compliance level and required actions"""        score = 0.0
        factors = []
        
        # Completeness score (40%)
        validation = await self._validate_dmca_notice(request)
        completeness_score = validation["score"]
        score += completeness_score * 0.4
        factors.append(f"Completeness: {completeness_score:.2f}")
        
        # Signature verification (20%)
        signature_score = 1.0 if request.electronic_signature else 0.0
        score += signature_score * 0.2
        factors.append(f"Signature: {signature_score:.2f}")
        
        # Good faith assessment (20%)
        good_faith_score = 1.0 if request.good_faith_statement else 0.0
        score += good_faith_score * 0.2
        factors.append(f"Good faith: {good_faith_score:.2f}")
        
        # Content specificity (20%)
        description_score = min(1.0, len(request.description) / 100)
        score += description_score * 0.2
        factors.append(f"Description: {description_score:.2f}")
        
        # Determine status
        if score >= 0.8:
            status = DMCACompliance.FULL_COMPLIANCE
        elif score >= 0.6:
            status = DMCACompliance.PARTIAL_COMPLIANCE
        else:
            status = DMCACompliance.NON_COMPLIANCE
        
        return {
            "score": score,
            "status": status,
            "factors": factors,
            "legal_review": score < self.config["legal_review_threshold"]
        }
    
    async def _determine_takedown_action(self, 
                                       request: DMCARequest, 
                                       assessment: Dict[str, Any]) -> TakedownAction:
        """Determine appropriate takedown action based on compliance assessment"""        if assessment["status"] == DMCACompliance.NON_COMPLIANCE:
            return TakedownAction.REJECT_INVALID
        
        if assessment["score"] >= self.config["auto_process_threshold"]:
            if self.config["automated_takedown"]:
                return TakedownAction.REMOVE_CONTENT
            else:
                return TakedownAction.DISABLE_ACCESS
        
        if assessment["legal_review"]:
            return TakedownAction.FORWARD_TO_USER
        
        return TakedownAction.DISABLE_ACCESS
    
    async def _create_dmca_notice(self, request: DMCARequest) -> str:
        """Create DMCA notice record in database"""        try:
            with self.db_manager.get_session() as session:
                notice = DMCANotice(
                    request_id=request.request_id,
                    content_id=request.content_id,
                    content_url=request.content_url,
                    infringing_url=request.infringing_url,
                    complainant_name=request.complainant_name,
                    complainant_email=request.complainant_email,
                    complainant_address=self.encryption_service.encrypt(request.complainant_address),
                    copyright_owner=request.copyright_owner,
                    copyrighted_work=request.copyrighted_work,
                    description=request.description,
                    good_faith_statement=request.good_faith_statement,
                    accuracy_statement=request.accuracy_statement,
                    electronic_signature=request.electronic_signature,
                    status=DMCAStatus.PENDING,
                    created_at=datetime.now()
                )
                
                session.add(notice)
                session.commit()
                session.refresh(notice)
                
                return notice.id
                
        except Exception as e:
            self.logger.error(f"Error creating DMCA notice: {str(e)}")
            raise
    
    async def _execute_takedown_action(self, request: DMCARequest, action: TakedownAction):
        """Execute the determined takedown action"""        try:
            if action == TakedownAction.REMOVE_CONTENT:
                # Remove content from all platforms
                await self._remove_content(request.content_id)
            
            elif action == TakedownAction.DISABLE_ACCESS:
                # Disable access but keep content
                await self._disable_content_access(request.content_id)
            
            elif action == TakedownAction.FORWARD_TO_USER:
                # Forward notice to content owner
                await self._forward_notice_to_user(request)
            
            self.logger.info(f"Executed takedown action: {action.value} for {request.content_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing takedown action: {str(e)}")
            raise
    
    async def _send_dmca_notifications(self, 
                                     request: DMCARequest, 
                                     notice_id: str, 
                                     action: TakedownAction):
        """Send DMCA-related notifications to relevant parties"""        try:
            # Notify complainant
            await self.email_service.send_templated_email(
                to_email=request.complainant_email,
                template=self.templates["takedown_notice"],
                context={
                    "notice_id": notice_id,
                    "action_taken": action.value,
                    "content_url": request.content_url,
                    "timestamp": datetime.now()
                }
            )
            
            # Notify content owner if action taken
            if action in [TakedownAction.REMOVE_CONTENT, TakedownAction.DISABLE_ACCESS]:
                await self._notify_content_owner(request, notice_id, action)
            
        except Exception as e:
            self.logger.error(f"Error sending DMCA notifications: {str(e)}")
    
    async def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive DMCA compliance metrics"""        try:
            cache_key = "dmca_metrics"
            cached_metrics = await self.cache_manager.get(cache_key)
            
            if cached_metrics:
                return cached_metrics
            
            # Calculate fresh metrics
            with self.db_manager.get_session() as session:
                # Last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                
                total_notices = session.query(DMCANotice).filter(
                    DMCANotice.created_at >= thirty_days_ago
                ).count()
                
                valid_notices = session.query(DMCANotice).filter(
                    and_(
                        DMCANotice.created_at >= thirty_days_ago,
                        DMCANotice.status == DMCAStatus.VALID
                    )
                ).count()
                
                auto_processed = session.query(DMCANotice).filter(
                    and_(
                        DMCANotice.created_at >= thirty_days_ago,
                        DMCANotice.auto_processed == True
                    )
                ).count()
                
                metrics = {
                    "total_notices_30d": total_notices,
                    "valid_notices_30d": valid_notices,
                    "auto_processed_30d": auto_processed,
                    "validity_rate": valid_notices / total_notices if total_notices > 0 else 0,
                    "automation_rate": auto_processed / total_notices if total_notices > 0 else 0,
                    "active_cases": len(self.active_cases),
                    "last_updated": datetime.now().isoformat()
                }
                
                # Cache for 1 hour
                await self.cache_manager.set(cache_key, metrics, ttl=3600)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error getting compliance metrics: {str(e)}")
            return {"error": str(e)}
