"""DMCA Processor - Digital Millennium Copyright Act Compliance

Automated DMCA takedown notice processing, counter-notification handling,
and platform compliance management for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass, asdict
import json
import uuid
import re

logger = logging.getLogger(__name__)


class DMCANoticeStatus(Enum):
    """DMCA notice status enumeration."""    RECEIVED = "received"
    PROCESSING = "processing"
    VALID = "valid"
    INVALID = "invalid"
    PROCESSED = "processed"
    COUNTER_RECEIVED = "counter_received"
    REINSTATED = "reinstated"
    ESCALATED = "escalated"


class NoticeType(Enum):
    """Type of DMCA notice."""    TAKEDOWN = "takedown"
    COUNTER_NOTIFICATION = "counter_notification"
    REPEAT_INFRINGER = "repeat_infringer"
    SAFE_HARBOR = "safe_harbor"


class InfringementType(Enum):
    """Type of copyright infringement."""    DIRECT_COPY = "direct_copy"
    SUBSTANTIAL_SIMILARITY = "substantial_similarity"
    UNAUTHORIZED_DERIVATIVE = "unauthorized_derivative"
    STREAMING_VIOLATION = "streaming_violation"
    DISTRIBUTION_VIOLATION = "distribution_violation"


@dataclass
class DMCANotice:
    """DMCA notice data structure."""    notice_id: str
    notice_type: NoticeType
    status: DMCANoticeStatus
    complainant_info: Dict[str, Any]
    infringing_content: Dict[str, Any]
    original_work: Dict[str, Any]
    infringement_claim: str
    sworn_statement: bool
    signature: str
    submitted_at: datetime
    processed_at: Optional[datetime]
    response_deadline: datetime
    platform_action: Optional[str]
    counter_notice_id: Optional[str]
    notes: str


@dataclass
class CounterNotification:
    """DMCA counter-notification data structure."""    counter_id: str
    original_notice_id: str
    respondent_info: Dict[str, Any]
    counter_statement: str
    good_faith_belief: bool
    jurisdiction_consent: bool
    sworn_statement: bool
    signature: str
    submitted_at: datetime
    restoration_date: datetime
    processed: bool


class DMCAProcessor:
    """    Comprehensive DMCA compliance processor.
    
    Handles takedown notices, counter-notifications, platform compliance,
    and automated response generation per DMCA requirements.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the DMCA Processor.
        
        Args:
            config: Configuration dictionary with database connections
        """        self.config = config
        self.db_config = config.get("database", {})
        self.dmca_config = config.get("dmca", {})
        
        # DMCA notice registries
        self.dmca_notices: Dict[str, DMCANotice] = {}
        self.counter_notifications: Dict[str, CounterNotification] = {}
        
        # DMCA processing settings
        self.auto_processing_enabled = self.dmca_config.get("auto_processing", True)
        self.takedown_threshold = self.dmca_config.get("validity_threshold", 0.8)
        self.restoration_delay_days = self.dmca_config.get("restoration_delay", 14)
        
        # Platform contact information
        self.platform_agent = self.dmca_config.get("designated_agent", {
            "name": "DMCA Agent",
            "email": "dmca@platform.com",
            "address": "Legal Department"
        })
        
        logger.info("DMCA Processor initialized successfully")
    
    async def process_takedown_request(
        self,
        complainant_info: Dict[str, Any],
        infringing_content: Dict[str, Any],
        original_work: Dict[str, Any],
        infringement_claim: str,
        sworn_statement: bool = True,
        signature: str = ""
    ) -> Dict[str, Any]:
        """        Process DMCA takedown request with full compliance validation.
        
        Args:
            complainant_info: Information about the copyright owner
            infringing_content: Details of allegedly infringing content
            original_work: Information about the original copyrighted work
            infringement_claim: Description of the infringement
            sworn_statement: Whether complainant provided sworn statement
            signature: Digital signature of the complainant
            
        Returns:
            DMCA processing results and actions taken
        """        try:
            # Generate unique notice ID
            notice_id = f"dmca_{uuid.uuid4().hex[:12]}"
            
            # Calculate response deadline (typically immediate for valid notices)
            response_deadline = datetime.utcnow() + timedelta(hours=24)
            
            # Create DMCA notice record
            dmca_notice = DMCANotice(
                notice_id=notice_id,
                notice_type=NoticeType.TAKEDOWN,
                status=DMCANoticeStatus.RECEIVED,
                complainant_info=complainant_info,
                infringing_content=infringing_content,
                original_work=original_work,
                infringement_claim=infringement_claim,
                sworn_statement=sworn_statement,
                signature=signature,
                submitted_at=datetime.utcnow(),
                processed_at=None,
                response_deadline=response_deadline,
                platform_action=None,
                counter_notice_id=None,
                notes=""
            )
            
            # Store notice
            self.dmca_notices[notice_id] = dmca_notice
            
            # Validate notice compliance
            validation_result = await self._validate_dmca_notice(dmca_notice)
            
            # Update notice status based on validation
            if validation_result["valid"]:
                dmca_notice.status = DMCANoticeStatus.VALID
            else:
                dmca_notice.status = DMCANoticeStatus.INVALID
                dmca_notice.notes = "; ".join(validation_result["issues"])
            
            processing_result = {
                "notice_id": notice_id,
                "status": dmca_notice.status.value,
                "submitted_at": dmca_notice.submitted_at.isoformat(),
                "validation": validation_result,
                "action_taken": False,
                "content_removed": False,
                "user_notified": False,
                "response_deadline": response_deadline.isoformat(),
                "next_steps": []
            }
            
            # Process valid notices
            if dmca_notice.status == DMCANoticeStatus.VALID:
                # Check for automatic processing eligibility
                if (self.auto_processing_enabled and 
                    validation_result["confidence_score"] >= self.takedown_threshold):
                    
                    # Execute takedown
                    takedown_result = await self._execute_takedown(dmca_notice)
                    processing_result.update(takedown_result)
                    
                    dmca_notice.status = DMCANoticeStatus.PROCESSED
                    dmca_notice.processed_at = datetime.utcnow()
                    dmca_notice.platform_action = "content_removed"
                    
                    processing_result["action_taken"] = True
                    processing_result["next_steps"] = [
                        "Content removed from platform",
                        "User notified of takedown",
                        "14-day counter-notification period begins"
                    ]
                else:
                    # Manual review required
                    processing_result["next_steps"] = [
                        "Manual review required",
                        "Legal team notified",
                        f"Response required by {response_deadline.isoformat()}"
                    ]
                    
                    # Escalate to legal team
                    await self._escalate_to_legal_team(dmca_notice)
            else:
                # Invalid notice - notify complainant
                await self._notify_invalid_notice(dmca_notice, validation_result)
                processing_result["next_steps"] = [
                    "Notice deemed invalid",
                    "Complainant notified of issues",
                    "Resubmission with corrections required"
                ]
            
            # Log DMCA processing
            await self._log_dmca_processing(dmca_notice, processing_result)
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing DMCA takedown request: {str(e)}")
            raise
    
    async def process_counter_notification(
        self,
        original_notice_id: str,
        respondent_info: Dict[str, Any],
        counter_statement: str,
        good_faith_belief: bool,
        jurisdiction_consent: bool,
        sworn_statement: bool,
        signature: str
    ) -> Dict[str, Any]:
        """        Process DMCA counter-notification.
        
        Args:
            original_notice_id: ID of the original takedown notice
            respondent_info: Information about the person submitting counter-notice
            counter_statement: Statement explaining why content should be restored
            good_faith_belief: Declaration of good faith belief
            jurisdiction_consent: Consent to jurisdiction
            sworn_statement: Sworn statement under penalty of perjury
            signature: Digital signature
            
        Returns:
            Counter-notification processing results
        """        try:
            # Verify original notice exists
            if original_notice_id not in self.dmca_notices:
                raise ValueError(f"Original DMCA notice {original_notice_id} not found")
            
            original_notice = self.dmca_notices[original_notice_id]
            
            # Generate counter-notification ID
            counter_id = f"counter_{uuid.uuid4().hex[:12]}"
            
            # Calculate restoration date (14 days from counter-notice)
            restoration_date = datetime.utcnow() + timedelta(days=self.restoration_delay_days)
            
            # Create counter-notification record
            counter_notification = CounterNotification(
                counter_id=counter_id,
                original_notice_id=original_notice_id,
                respondent_info=respondent_info,
                counter_statement=counter_statement,
                good_faith_belief=good_faith_belief,
                jurisdiction_consent=jurisdiction_consent,
                sworn_statement=sworn_statement,
                signature=signature,
                submitted_at=datetime.utcnow(),
                restoration_date=restoration_date,
                processed=False
            )
            
            # Store counter-notification
            self.counter_notifications[counter_id] = counter_notification
            
            # Update original notice status
            original_notice.status = DMCANoticeStatus.COUNTER_RECEIVED
            original_notice.counter_notice_id = counter_id
            
            # Validate counter-notification
            validation_result = await self._validate_counter_notification(counter_notification)
            
            counter_result = {
                "counter_id": counter_id,
                "original_notice_id": original_notice_id,
                "submitted_at": counter_notification.submitted_at.isoformat(),
                "restoration_date": restoration_date.isoformat(),
                "validation": validation_result,
                "complainant_notified": False,
                "restoration_scheduled": False,
                "next_steps": []
            }
            
            if validation_result["valid"]:
                # Notify original complainant
                await self._notify_complainant_of_counter(original_notice, counter_notification)
                counter_result["complainant_notified"] = True
                
                # Schedule automatic restoration
                await self._schedule_content_restoration(counter_notification)
                counter_result["restoration_scheduled"] = True
                
                counter_result["next_steps"] = [
                    f"Complainant notified of counter-notification",
                    f"Content will be restored on {restoration_date.isoformat()}",
                    "Complainant has 14 days to file lawsuit"
                ]
            else:
                counter_result["next_steps"] = [
                    "Counter-notification deemed invalid",
                    "Respondent notified of issues",
                    "Content remains removed"
                ]
            
            # Log counter-notification processing
            await self._log_counter_processing(counter_notification, counter_result)
            
            return counter_result
            
        except Exception as e:
            logger.error(f"Error processing counter-notification: {str(e)}")
            raise
    
    async def get_activity_summary(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """        Get DMCA activity summary for reporting.
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Start date for summary period
            end_date: End date for summary period
            
        Returns:
            DMCA activity summary
        """        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            summary = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "user_id": user_id,
                "notice_summary": {
                    "total_notices": 0,
                    "valid_notices": 0,
                    "invalid_notices": 0,
                    "processed_notices": 0,
                    "pending_notices": 0
                },
                "takedown_summary": {
                    "content_removed": 0,
                    "automatic_takedowns": 0,
                    "manual_review_takedowns": 0,
                    "avg_processing_time_hours": 0.0
                },
                "counter_summary": {
                    "counter_notifications": 0,
                    "content_restored": 0,
                    "pending_restorations": 0
                },
                "compliance_metrics": {
                    "response_time_compliance": 0.0,
                    "notice_validity_rate": 0.0,
                    "successful_takedowns": 0.0
                }
            }
            
            # Filter notices by criteria
            filtered_notices = self._filter_notices_by_criteria(
                user_id, start_date, end_date
            )
            filtered_counters = self._filter_counters_by_criteria(
                user_id, start_date, end_date
            )
            
            # Calculate notice summary
            summary["notice_summary"]["total_notices"] = len(filtered_notices)
            
            processing_times = []
            for notice in filtered_notices:
                if notice.status == DMCANoticeStatus.VALID:
                    summary["notice_summary"]["valid_notices"] += 1
                elif notice.status == DMCANoticeStatus.INVALID:
                    summary["notice_summary"]["invalid_notices"] += 1
                elif notice.status == DMCANoticeStatus.PROCESSED:
                    summary["notice_summary"]["processed_notices"] += 1
                    summary["takedown_summary"]["content_removed"] += 1
                    
                    # Calculate processing time
                    if notice.processed_at:
                        processing_time = (notice.processed_at - notice.submitted_at).total_seconds() / 3600
                        processing_times.append(processing_time)
                else:
                    summary["notice_summary"]["pending_notices"] += 1
            
            # Calculate average processing time
            if processing_times:
                summary["takedown_summary"]["avg_processing_time_hours"] = sum(processing_times) / len(processing_times)
            
            # Calculate counter-notification summary
            summary["counter_summary"]["counter_notifications"] = len(filtered_counters)
            summary["counter_summary"]["content_restored"] = len([
                c for c in filtered_counters if c.processed
            ])
            summary["counter_summary"]["pending_restorations"] = len([
                c for c in filtered_counters if not c.processed and c.restoration_date > datetime.utcnow()
            ])
            
            # Calculate compliance metrics
            if summary["notice_summary"]["total_notices"] > 0:
                summary["compliance_metrics"]["notice_validity_rate"] = (
                    summary["notice_summary"]["valid_notices"] / 
                    summary["notice_summary"]["total_notices"]
                ) * 100
                
                summary["compliance_metrics"]["successful_takedowns"] = (
                    summary["notice_summary"]["processed_notices"] / 
                    summary["notice_summary"]["total_notices"]
                ) * 100
            
            # Response time compliance (under 24 hours)
            on_time_responses = len([
                n for n in filtered_notices 
                if n.processed_at and (n.processed_at - n.submitted_at).total_seconds() < 86400
            ])
            
            if summary["notice_summary"]["processed_notices"] > 0:
                summary["compliance_metrics"]["response_time_compliance"] = (
                    on_time_responses / summary["notice_summary"]["processed_notices"]
                ) * 100
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating DMCA activity summary: {str(e)}")
            raise
    
    async def check_repeat_infringer(
        self,
        user_id: str,
        threshold_violations: int = 3,
        time_window_days: int = 365
    ) -> Dict[str, Any]:
        """        Check if user is a repeat infringer under DMCA.
        
        Args:
            user_id: ID of user to check
            threshold_violations: Number of violations that constitute repeat infringement
            time_window_days: Time window to check for violations
            
        Returns:
            Repeat infringer assessment
        """        try:
            # Calculate time window
            start_date = datetime.utcnow() - timedelta(days=time_window_days)
            
            # Get user's violation history
            user_violations = []
            
            for notice in self.dmca_notices.values():
                if (notice.status == DMCANoticeStatus.PROCESSED and
                    notice.infringing_content.get("uploader_id") == user_id and
                    notice.submitted_at >= start_date):
                    
                    user_violations.append({
                        "notice_id": notice.notice_id,
                        "date": notice.submitted_at.isoformat(),
                        "content_id": notice.infringing_content.get("content_id"),
                        "complainant": notice.complainant_info.get("name", "Unknown")
                    })
            
            # Check for counter-notifications that were not followed by lawsuits
            valid_violations = []
            for violation in user_violations:
                notice = self.dmca_notices[violation["notice_id"]]
                
                # If there was a counter-notification, check if lawsuit was filed
                if notice.counter_notice_id:
                    counter = self.counter_notifications.get(notice.counter_notice_id)
                    if counter and counter.processed:
                        # Content was restored, violation may not count
                        continue
                
                valid_violations.append(violation)
            
            repeat_infringer_result = {
                "user_id": user_id,
                "assessment_date": datetime.utcnow().isoformat(),
                "time_window_days": time_window_days,
                "total_violations": len(user_violations),
                "valid_violations": len(valid_violations),
                "threshold": threshold_violations,
                "is_repeat_infringer": len(valid_violations) >= threshold_violations,
                "violations": valid_violations,
                "recommended_actions": []
            }
            
            # Generate recommendations
            if repeat_infringer_result["is_repeat_infringer"]:
                repeat_infringer_result["recommended_actions"] = [
                    "Account suspension recommended",
                    "Enhanced monitoring required",
                    "Legal review of user status"
                ]
            elif len(valid_violations) >= threshold_violations - 1:
                repeat_infringer_result["recommended_actions"] = [
                    "Warning notice to user",
                    "Enhanced content monitoring",
                    "Copyright education required"
                ]
            
            return repeat_infringer_result
            
        except Exception as e:
            logger.error(f"Error checking repeat infringer status: {str(e)}")
            raise
    
    # Private helper methods
    async def _validate_dmca_notice(self, notice: DMCANotice) -> Dict[str, Any]:
        """Validate DMCA notice for compliance with requirements."""        validation_result = {
            "valid": True,
            "confidence_score": 1.0,
            "issues": [],
            "requirements_met": []
        }
        
        # Check required complainant information
        complainant = notice.complainant_info
        if not complainant.get("name"):
            validation_result["issues"].append("Complainant name missing")
            validation_result["confidence_score"] -= 0.2
        
        if not complainant.get("contact_info"):
            validation_result["issues"].append("Complainant contact information missing")
            validation_result["confidence_score"] -= 0.2
        
        # Check copyright ownership claim
        if not complainant.get("copyright_ownership_statement"):
            validation_result["issues"].append("Copyright ownership statement missing")
            validation_result["confidence_score"] -= 0.3
        else:
            validation_result["requirements_met"].append("Copyright ownership claimed")
        
        # Check infringing content identification
        if not notice.infringing_content.get("url") and not notice.infringing_content.get("content_id"):
            validation_result["issues"].append("Infringing content not properly identified")
            validation_result["confidence_score"] -= 0.3
        else:
            validation_result["requirements_met"].append("Infringing content identified")
        
        # Check original work identification
        if not notice.original_work.get("description"):
            validation_result["issues"].append("Original work not properly described")
            validation_result["confidence_score"] -= 0.2
        
        # Check sworn statement
        if not notice.sworn_statement:
            validation_result["issues"].append("Sworn statement missing")
            validation_result["confidence_score"] -= 0.3
        else:
            validation_result["requirements_met"].append("Sworn statement provided")
        
        # Check signature
        if not notice.signature:
            validation_result["issues"].append("Digital signature missing")
            validation_result["confidence_score"] -= 0.2
        
        # Determine if valid
        validation_result["valid"] = (
            validation_result["confidence_score"] >= 0.6 and 
            len(validation_result["issues"]) == 0
        )
        
        return validation_result
    
    async def _validate_counter_notification(
        self, 
        counter: CounterNotification
    ) -> Dict[str, Any]:
        """Validate counter-notification for DMCA compliance."""        validation_result = {
            "valid": True,
            "issues": [],
            "requirements_met": []
        }
        
        # Check respondent information
        if not counter.respondent_info.get("name"):
            validation_result["issues"].append("Respondent name missing")
        
        if not counter.respondent_info.get("address"):
            validation_result["issues"].append("Respondent address missing")
        
        # Check required statements
        if not counter.good_faith_belief:
            validation_result["issues"].append("Good faith belief statement missing")
        else:
            validation_result["requirements_met"].append("Good faith belief declared")
        
        if not counter.jurisdiction_consent:
            validation_result["issues"].append("Jurisdiction consent missing")
        else:
            validation_result["requirements_met"].append("Jurisdiction consent provided")
        
        if not counter.sworn_statement:
            validation_result["issues"].append("Sworn statement missing")
        else:
            validation_result["requirements_met"].append("Sworn statement provided")
        
        if not counter.signature:
            validation_result["issues"].append("Signature missing")
        
        validation_result["valid"] = len(validation_result["issues"]) == 0
        
        return validation_result
    
    async def _execute_takedown(self, notice: DMCANotice) -> Dict[str, Any]:
        """Execute content takedown based on valid DMCA notice."""        takedown_result = {
            "content_removed": False,
            "user_notified": False,
            "removal_timestamp": None,
            "backup_created": False,
            "restoration_info_preserved": False
        }
        
        try:
            content_id = notice.infringing_content.get("content_id")
            user_id = notice.infringing_content.get("uploader_id")
            
            # Remove content from platform
            removal_success = await self._remove_content_from_platform(content_id)
            takedown_result["content_removed"] = removal_success
            
            if removal_success:
                takedown_result["removal_timestamp"] = datetime.utcnow().isoformat()
                
                # Create backup for potential restoration
                backup_success = await self._create_content_backup(content_id, notice.notice_id)
                takedown_result["backup_created"] = backup_success
                
                # Notify user of takedown
                notification_success = await self._notify_user_of_takedown(user_id, notice)
                takedown_result["user_notified"] = notification_success
                
                # Preserve restoration information
                restoration_info = {
                    "content_id": content_id,
                    "original_location": notice.infringing_content.get("url"),
                    "backup_location": f"backup/{notice.notice_id}/{content_id}",
                    "notice_id": notice.notice_id,
                    "removal_date": takedown_result["removal_timestamp"]
                }
                
                preservation_success = await self._preserve_restoration_info(restoration_info)
                takedown_result["restoration_info_preserved"] = preservation_success
            
            return takedown_result
            
        except Exception as e:
            logger.error(f"Error executing takedown: {str(e)}")
            takedown_result["error"] = str(e)
            return takedown_result
    
    def _filter_notices_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[DMCANotice]:
        """Filter DMCA notices by criteria."""        filtered = []
        
        for notice in self.dmca_notices.values():
            # Filter by user (as complainant or content owner)
            if user_id:
                is_complainant = notice.complainant_info.get("user_id") == user_id
                is_content_owner = notice.infringing_content.get("uploader_id") == user_id
                if not (is_complainant or is_content_owner):
                    continue
            
            # Filter by date range
            if (notice.submitted_at < start_date or 
                notice.submitted_at > end_date):
                continue
            
            filtered.append(notice)
        
        return filtered
    
    def _filter_counters_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[CounterNotification]:
        """Filter counter-notifications by criteria."""        filtered = []
        
        for counter in self.counter_notifications.values():
            # Filter by user
            if user_id and counter.respondent_info.get("user_id") != user_id:
                continue
            
            # Filter by date range
            if (counter.submitted_at < start_date or 
                counter.submitted_at > end_date):
                continue
            
            filtered.append(counter)
        
        return filtered
    
    # Placeholder methods for platform integration
    async def _remove_content_from_platform(self, content_id: str) -> bool:
        """Remove content from platform."""        logger.info(f"Removing content {content_id} from platform")
        return True
    
    async def _create_content_backup(self, content_id: str, notice_id: str) -> bool:
        """Create backup of content for potential restoration."""        logger.info(f"Creating backup for content {content_id} (notice {notice_id})")
        return True
    
    async def _notify_user_of_takedown(self, user_id: str, notice: DMCANotice) -> bool:
        """Notify user of content takedown."""        logger.info(f"Notifying user {user_id} of DMCA takedown")
        return True
    
    async def _preserve_restoration_info(self, restoration_info: Dict[str, Any]) -> bool:
        """Preserve information needed for content restoration."""        logger.info(f"Preserving restoration info for content {restoration_info['content_id']}")
        return True
    
    async def _escalate_to_legal_team(self, notice: DMCANotice) -> None:
        """Escalate notice to legal team for manual review."""        logger.info(f"Escalating DMCA notice {notice.notice_id} to legal team")
    
    async def _notify_invalid_notice(self, notice: DMCANotice, validation_result: Dict[str, Any]) -> None:
        """Notify complainant of invalid notice."""        logger.info(f"Notifying complainant of invalid DMCA notice {notice.notice_id}")
    
    async def _notify_complainant_of_counter(
        self, 
        original_notice: DMCANotice, 
        counter: CounterNotification
    ) -> None:
        """Notify original complainant of counter-notification."""        logger.info(f"Notifying complainant of counter-notification {counter.counter_id}")
    
    async def _schedule_content_restoration(self, counter: CounterNotification) -> None:
        """Schedule automatic content restoration."""        logger.info(f"Scheduling content restoration for {counter.restoration_date}")
    
    # Logging methods
    async def _log_dmca_processing(self, notice: DMCANotice, result: Dict[str, Any]) -> None:
        """Log DMCA notice processing."""        logger.info(f"DMCA notice processed: {notice.notice_id} - Status: {notice.status.value}")
    
    async def _log_counter_processing(
        self, 
        counter: CounterNotification, 
        result: Dict[str, Any]
    ) -> None:
        """Log counter-notification processing."""        logger.info(f"Counter-notification processed: {counter.counter_id}")
