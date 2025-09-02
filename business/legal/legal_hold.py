"""Legal Hold Management System

Implements comprehensive legal hold procedures for litigation,
regulatory investigations, and content preservation requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class LegalHoldType(Enum):
    """Types of legal holds"""
    LITIGATION = "litigation"
    REGULATORY_INVESTIGATION = "regulatory_investigation"
    INTERNAL_INVESTIGATION = "internal_investigation"
    EMPLOYMENT_DISPUTE = "employment_dispute"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    DATA_BREACH_INVESTIGATION = "data_breach_investigation"
    CRIMINAL_INVESTIGATION = "criminal_investigation"
    COMPLIANCE_AUDIT = "compliance_audit"


class LegalHoldStatus(Enum):
    """Status of legal hold"""
    PENDING = "pending"
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class DataType(Enum):
    """Types of data subject to legal hold"""
    EMAIL = "email"
    DOCUMENTS = "documents"
    CHAT_MESSAGES = "chat_messages"
    AUDIO_RECORDINGS = "audio_recordings"
    VIDEO_CONTENT = "video_content"
    DATABASE_RECORDS = "database_records"
    SYSTEM_LOGS = "system_logs"
    METADATA = "metadata"
    BACKUP_DATA = "backup_data"
    ARCHIVED_DATA = "archived_data"


class PreservationMethod(Enum):
    """Methods for data preservation"""
    IN_PLACE = "in_place"  # Preserve data in original location
    COPY_TO_SECURE = "copy_to_secure"  # Copy to secure preservation system
    EXPORT_AND_STORE = "export_and_store"  # Export and store separately
    FORENSIC_IMAGE = "forensic_image"  # Create forensic bit-for-bit copy


@dataclass
class LegalHoldCustodian:
    """Individual or entity whose data is subject to legal hold"""
    custodian_id: str
    name: str
    email: str
    department: Optional[str] = None
    role: Optional[str] = None
    manager: Optional[str] = None
    active: bool = True
    data_sources: List[str] = field(default_factory=list)
    notification_sent: bool = False
    acknowledgment_received: bool = False
    acknowledgment_date: Optional[datetime] = None


@dataclass
class PreservationTarget:
    """Specific data target for preservation"""
    target_id: str
    data_type: DataType
    source_system: str
    location: str
    custodian_id: Optional[str] = None
    preservation_method: PreservationMethod = PreservationMethod.IN_PLACE
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    keywords: List[str] = field(default_factory=list)
    status: str = "pending"
    preservation_date: Optional[datetime] = None
    preserved_size: Optional[int] = None
    preservation_path: Optional[str] = None
    verification_hash: Optional[str] = None


@dataclass
class LegalHold:
    """Legal hold record"""
    hold_id: str
    title: str
    description: str
    hold_type: LegalHoldType
    status: LegalHoldStatus = LegalHoldStatus.PENDING
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    release_date: Optional[datetime] = None
    matter_name: str = ""
    matter_number: Optional[str] = None
    legal_team: List[str] = field(default_factory=list)
    custodians: List[LegalHoldCustodian] = field(default_factory=list)
    preservation_targets: List[PreservationTarget] = field(default_factory=list)
    preservation_instructions: str = ""
    notification_template: Optional[str] = None
    periodic_review_interval: int = 90  # days
    next_review_date: Optional[datetime] = None
    auto_release_conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LegalHoldManager:
    """
    Legal Hold Management System
    
    Manages legal hold processes including custodian notifications,
    data preservation, compliance monitoring, and release procedures.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage for legal holds
        self.legal_holds: Dict[str, LegalHold] = {}
        self.preservation_queue: List[PreservationTarget] = []
        
        # Configuration
        self.notification_templates = self._load_notification_templates()
        self.preservation_policies = self._load_preservation_policies()
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "active_holds": 0,
            "total_custodians": 0,
            "data_preserved_gb": 0.0,
            "compliance_rate": 100.0,
            "pending_notifications": 0,
            "overdue_reviews": 0
        }
    
    def _load_notification_templates(self) -> Dict[str, str]:
        """Load legal hold notification templates"""
        return {
            "litigation": """
LEGAL HOLD NOTICE - IMMEDIATE ACTION REQUIRED

Dear {custodian_name},

You are receiving this notice because you may be a custodian of documents, 
data, or information relevant to pending or anticipated litigation involving 
{company_name} in the matter of {matter_name}.

PRESERVATION OBLIGATION:
You must immediately preserve all documents, electronic data, and information 
in your possession, custody, or control that relate to this matter, including 
but not limited to:

{preservation_targets}

This legal hold obligation supersedes any routine document retention or 
destruction policies. You must not delete, destroy, or alter any potentially 
relevant information, regardless of whether it is stored on company systems, 
personal devices, or cloud storage services.

DURATION:
This legal hold will remain in effect until you receive written notice that 
it has been released. Periodic reminders will be sent to ensure compliance.

COMPLIANCE:
Failure to comply with this legal hold notice may result in serious legal 
consequences for both you and the company, including sanctions, adverse 
inference instructions, and monetary penalties.

If you have any questions about this legal hold, please contact the Legal 
Department immediately at {legal_contact}.

Please acknowledge receipt of this notice by replying to this email or 
accessing the legal hold system at {acknowledgment_url}.

Legal Department
{company_name}
Date: {issue_date}
            """,
            "regulatory": """
REGULATORY INVESTIGATION - DATA PRESERVATION NOTICE

Dear {custodian_name},

{company_name} is subject to a regulatory investigation/audit by {regulator_name}. 
As a result, all relevant documents and data must be preserved.

IMMEDIATE ACTIONS REQUIRED:
1. Preserve all documents and electronic data related to {investigation_scope}
2. Do not delete, modify, or destroy any potentially relevant information
3. Notify the Legal Department if you become aware of any data destruction

This notice is effective immediately and will remain in place until further notice.

Contact: {legal_contact}
            """
        }
    
    def _load_preservation_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load data preservation policies"""
        return {
            "email": {
                "method": PreservationMethod.COPY_TO_SECURE,
                "retention_years": 7,
                "encryption_required": True,
                "forensic_collection": True
            },
            "documents": {
                "method": PreservationMethod.IN_PLACE,
                "retention_years": 7,
                "encryption_required": True,
                "forensic_collection": False
            },
            "database_records": {
                "method": PreservationMethod.EXPORT_AND_STORE,
                "retention_years": 10,
                "encryption_required": True,
                "forensic_collection": True
            }
        }
    
    async def create_legal_hold(
        self,
        title: str,
        description: str,
        hold_type: LegalHoldType,
        matter_name: str,
        created_by: str,
        custodians: List[Dict[str, Any]],
        preservation_targets: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """
        Create a new legal hold
        
        Args:
            title: Title of the legal hold
            description: Detailed description
            hold_type: Type of legal hold
            matter_name: Name of the legal matter
            created_by: User creating the hold
            custodians: List of custodian information
            preservation_targets: List of data preservation targets
            **kwargs: Additional parameters
            
        Returns:
            str: Legal hold ID
        """
        try:
            hold_id = str(uuid.uuid4())
            
            # Create custodian objects
            hold_custodians = []
            for custodian_data in custodians:
                custodian = LegalHoldCustodian(
                    custodian_id=str(uuid.uuid4()),
                    name=custodian_data["name"],
                    email=custodian_data["email"],
                    department=custodian_data.get("department"),
                    role=custodian_data.get("role"),
                    data_sources=custodian_data.get("data_sources", [])
                )
                hold_custodians.append(custodian)
            
            # Create preservation target objects
            hold_targets = []
            for target_data in preservation_targets:
                target = PreservationTarget(
                    target_id=str(uuid.uuid4()),
                    data_type=DataType(target_data["data_type"]),
                    source_system=target_data["source_system"],
                    location=target_data["location"],
                    custodian_id=target_data.get("custodian_id"),
                    preservation_method=PreservationMethod(
                        target_data.get("preservation_method", "in_place")
                    ),
                    date_range_start=target_data.get("date_range_start"),
                    date_range_end=target_data.get("date_range_end"),
                    keywords=target_data.get("keywords", [])
                )
                hold_targets.append(target)
            
            # Calculate next review date
            review_interval = kwargs.get("review_interval", 90)
            next_review = datetime.utcnow() + timedelta(days=review_interval)
            
            # Create legal hold
            legal_hold = LegalHold(
                hold_id=hold_id,
                title=title,
                description=description,
                hold_type=hold_type,
                created_by=created_by,
                matter_name=matter_name,
                matter_number=kwargs.get("matter_number"),
                legal_team=kwargs.get("legal_team", []),
                custodians=hold_custodians,
                preservation_targets=hold_targets,
                preservation_instructions=kwargs.get("preservation_instructions", ""),
                periodic_review_interval=review_interval,
                next_review_date=next_review,
                auto_release_conditions=kwargs.get("auto_release_conditions", []),
                metadata=kwargs.get("metadata", {})
            )
            
            self.legal_holds[hold_id] = legal_hold
            
            # Log creation
            await self._log_audit_event({
                "event_type": "legal_hold_created",
                "hold_id": hold_id,
                "title": title,
                "hold_type": hold_type.value,
                "created_by": created_by,
                "custodian_count": len(hold_custodians),
                "target_count": len(hold_targets),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Initiate notifications and preservation
            await self._initiate_legal_hold_process(legal_hold)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Legal hold created: {hold_id} ({title})")
            return hold_id
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error creating legal hold: {e}")
            raise
    
    async def _initiate_legal_hold_process(self, legal_hold: LegalHold):
        """Initiate the legal hold process"""
        try:
            # Send custodian notifications
            await self._send_custodian_notifications(legal_hold)
            
            # Queue data preservation tasks
            await self._queue_preservation_tasks(legal_hold)
            
            # Activate the hold
            legal_hold.status = LegalHoldStatus.ACTIVE
            
            await self._log_audit_event({
                "event_type": "legal_hold_activated",
                "hold_id": legal_hold.hold_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error initiating legal hold process: {e}")
            raise
    
    async def _send_custodian_notifications(self, legal_hold: LegalHold):
        """Send legal hold notifications to custodians"""
        try:
            template = self.notification_templates.get(
                legal_hold.hold_type.value, 
                self.notification_templates["litigation"]
            )
            
            for custodian in legal_hold.custodians:
                # Generate personalized notification
                notification_content = template.format(
                    custodian_name=custodian.name,
                    company_name=self.config.get("company_name", "Company"),
                    matter_name=legal_hold.matter_name,
                    preservation_targets=self._format_preservation_targets(legal_hold.preservation_targets),
                    legal_contact=self.config.get("legal_contact", "legal@company.com"),
                    acknowledgment_url=f"{self.config.get('base_url', '')}/legal-hold/{legal_hold.hold_id}/acknowledge",
                    issue_date=datetime.utcnow().strftime("%Y-%m-%d")
                )
                
                # Send notification (implementation would use email service)
                await self._send_notification(custodian.email, notification_content)
                
                custodian.notification_sent = True
                
                await self._log_audit_event({
                    "event_type": "custodian_notification_sent",
                    "hold_id": legal_hold.hold_id,
                    "custodian_id": custodian.custodian_id,
                    "custodian_email": custodian.email,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error sending custodian notifications: {e}")
            raise
    
    async def _queue_preservation_tasks(self, legal_hold: LegalHold):
        """Queue data preservation tasks"""
        try:
            for target in legal_hold.preservation_targets:
                # Add to preservation queue
                self.preservation_queue.append(target)
                
                # Start preservation process
                await self._preserve_data_target(target)
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error queuing preservation tasks: {e}")
            raise
    
    async def _preserve_data_target(self, target: PreservationTarget):
        """Preserve a specific data target"""
        try:
            preservation_started = datetime.utcnow()
            
            # Implementation would perform actual data preservation
            # based on the preservation method and data type
            
            if target.preservation_method == PreservationMethod.COPY_TO_SECURE:
                # Copy data to secure preservation location
                preservation_result = await self._copy_to_secure_location(target)
            elif target.preservation_method == PreservationMethod.IN_PLACE:
                # Mark data for in-place preservation
                preservation_result = await self._mark_for_in_place_preservation(target)
            elif target.preservation_method == PreservationMethod.EXPORT_AND_STORE:
                # Export and store in preservation system
                preservation_result = await self._export_and_store(target)
            elif target.preservation_method == PreservationMethod.FORENSIC_IMAGE:
                # Create forensic image
                preservation_result = await self._create_forensic_image(target)
            
            # Update target status
            target.status = "preserved"
            target.preservation_date = preservation_started
            target.preserved_size = preservation_result.get("size")
            target.preservation_path = preservation_result.get("path")
            target.verification_hash = preservation_result.get("hash")
            
            await self._log_audit_event({
                "event_type": "data_preserved",
                "target_id": target.target_id,
                "data_type": target.data_type.value,
                "preservation_method": target.preservation_method.value,
                "preserved_size": target.preserved_size,
                "timestamp": preservation_started.isoformat()
            })
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error preserving data target {target.target_id}: {e}")
            target.status = "failed"
    
    async def acknowledge_legal_hold(
        self,
        hold_id: str,
        custodian_email: str,
        acknowledgment_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record custodian acknowledgment of legal hold
        
        Args:
            hold_id: Legal hold identifier
            custodian_email: Email of acknowledging custodian
            acknowledgment_data: Additional acknowledgment information
            
        Returns:
            bool: Success status
        """
        try:
            legal_hold = self.legal_holds.get(hold_id)
            if not legal_hold:
                return False
            
            # Find custodian
            custodian = None
            for c in legal_hold.custodians:
                if c.email == custodian_email:
                    custodian = c
                    break
            
            if not custodian:
                return False
            
            # Record acknowledgment
            custodian.acknowledgment_received = True
            custodian.acknowledgment_date = datetime.utcnow()
            
            await self._log_audit_event({
                "event_type": "legal_hold_acknowledged",
                "hold_id": hold_id,
                "custodian_id": custodian.custodian_id,
                "custodian_email": custodian_email,
                "acknowledgment_data": acknowledgment_data or {},
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Legal hold acknowledged: {hold_id} by {custodian_email}")
            return True
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error recording legal hold acknowledgment: {e}")
            return False
    
    async def release_legal_hold(
        self,
        hold_id: str,
        released_by: str,
        release_reason: str,
        release_all_data: bool = True
    ) -> bool:
        """
        Release a legal hold
        
        Args:
            hold_id: Legal hold identifier
            released_by: User releasing the hold
            release_reason: Reason for release
            release_all_data: Whether to release all preserved data
            
        Returns:
            bool: Success status
        """
        try:
            legal_hold = self.legal_holds.get(hold_id)
            if not legal_hold:
                return False
            
            # Update hold status
            legal_hold.status = LegalHoldStatus.RELEASED
            legal_hold.release_date = datetime.utcnow()
            legal_hold.metadata.update({
                "released_by": released_by,
                "release_reason": release_reason,
                "release_all_data": release_all_data
            })
            
            # Send release notifications to custodians
            await self._send_release_notifications(legal_hold)
            
            # Handle data release if requested
            if release_all_data:
                await self._release_preserved_data(legal_hold)
            
            await self._log_audit_event({
                "event_type": "legal_hold_released",
                "hold_id": hold_id,
                "released_by": released_by,
                "release_reason": release_reason,
                "release_all_data": release_all_data,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Legal hold released: {hold_id}")
            return True
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error releasing legal hold {hold_id}: {e}")
            return False
    
    async def get_legal_hold_status(self, hold_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a legal hold"""
        legal_hold = self.legal_holds.get(hold_id)
        if not legal_hold:
            return None
        
        # Calculate compliance metrics
        total_custodians = len(legal_hold.custodians)
        acknowledged_custodians = len([c for c in legal_hold.custodians if c.acknowledgment_received])
        total_targets = len(legal_hold.preservation_targets)
        preserved_targets = len([t for t in legal_hold.preservation_targets if t.status == "preserved"])
        
        return {
            "hold_id": hold_id,
            "title": legal_hold.title,
            "status": legal_hold.status.value,
            "hold_type": legal_hold.hold_type.value,
            "matter_name": legal_hold.matter_name,
            "created_at": legal_hold.created_at.isoformat(),
            "effective_date": legal_hold.effective_date.isoformat(),
            "release_date": legal_hold.release_date.isoformat() if legal_hold.release_date else None,
            "next_review_date": legal_hold.next_review_date.isoformat() if legal_hold.next_review_date else None,
            "custodian_compliance": {
                "total": total_custodians,
                "acknowledged": acknowledged_custodians,
                "compliance_rate": (acknowledged_custodians / total_custodians * 100) if total_custodians > 0 else 100
            },
            "preservation_status": {
                "total_targets": total_targets,
                "preserved_targets": preserved_targets,
                "completion_rate": (preserved_targets / total_targets * 100) if total_targets > 0 else 100
            },
            "days_active": (datetime.utcnow() - legal_hold.created_at).days
        }
    
    async def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate legal hold compliance report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=90)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter holds by date range
            filtered_holds = [
                hold for hold in self.legal_holds.values()
                if start_date <= hold.created_at <= end_date
            ]
            
            # Calculate metrics
            total_holds = len(filtered_holds)
            active_holds = len([h for h in filtered_holds if h.status == LegalHoldStatus.ACTIVE])
            released_holds = len([h for h in filtered_holds if h.status == LegalHoldStatus.RELEASED])
            
            # Custodian compliance
            total_custodians = sum(len(h.custodians) for h in filtered_holds)
            acknowledged_custodians = sum(
                len([c for c in h.custodians if c.acknowledgment_received])
                for h in filtered_holds
            )
            
            # Preservation compliance
            total_targets = sum(len(h.preservation_targets) for h in filtered_holds)
            preserved_targets = sum(
                len([t for t in h.preservation_targets if t.status == "preserved"])
                for h in filtered_holds
            )
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_legal_holds": total_holds,
                    "active_holds": active_holds,
                    "released_holds": released_holds,
                    "custodian_compliance_rate": (acknowledged_custodians / total_custodians * 100) if total_custodians > 0 else 100,
                    "preservation_completion_rate": (preserved_targets / total_targets * 100) if total_targets > 0 else 100
                },
                "by_hold_type": {
                    hold_type.value: len([h for h in filtered_holds if h.hold_type == hold_type])
                    for hold_type in LegalHoldType
                },
                "by_status": {
                    status.value: len([h for h in filtered_holds if h.status == status])
                    for status in LegalHoldStatus
                },
                "overdue_reviews": self._get_overdue_reviews(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error generating legal hold compliance report: {e}")
            return {"error": str(e)}
    
    # Helper methods (simplified implementations)
    
    def _format_preservation_targets(self, targets: List[PreservationTarget]) -> str:
        """Format preservation targets for notification"""
        target_descriptions = []
        for target in targets:
            desc = f"- {target.data_type.value.replace('_', ' ').title()}"
            if target.keywords:
                desc += f" (containing: {', '.join(target.keywords)})"
            target_descriptions.append(desc)
        return "\n".join(target_descriptions)
    
    async def _send_notification(self, email: str, content: str):
        """Send notification email"""
        # Implementation would use actual email service
        self.logger.info(f"Legal hold notification sent to {email}")
    
    async def _copy_to_secure_location(self, target: PreservationTarget) -> Dict[str, Any]:
        """Copy data to secure preservation location"""
        # Implementation would perform actual data copying
        return {
            "size": 1024 * 1024 * 100,  # 100MB
            "path": f"/secure/preservation/{target.target_id}",
            "hash": "sha256:abcd1234..."
        }
    
    async def _mark_for_in_place_preservation(self, target: PreservationTarget) -> Dict[str, Any]:
        """Mark data for in-place preservation"""
        # Implementation would set preservation flags
        return {
            "size": 0,
            "path": target.location,
            "hash": "preservation_flag_set"
        }
    
    async def _export_and_store(self, target: PreservationTarget) -> Dict[str, Any]:
        """Export and store data"""
        # Implementation would export data
        return {
            "size": 1024 * 1024 * 50,  # 50MB
            "path": f"/exports/{target.target_id}",
            "hash": "sha256:efgh5678..."
        }
    
    async def _create_forensic_image(self, target: PreservationTarget) -> Dict[str, Any]:
        """Create forensic image"""
        # Implementation would create bit-for-bit copy
        return {
            "size": 1024 * 1024 * 200,  # 200MB
            "path": f"/forensic/{target.target_id}.img",
            "hash": "sha256:ijkl9012..."
        }
    
    async def _send_release_notifications(self, legal_hold: LegalHold):
        """Send release notifications to custodians"""
        for custodian in legal_hold.custodians:
            # Implementation would send release notification
            self.logger.info(f"Release notification sent to {custodian.email}")
    
    async def _release_preserved_data(self, legal_hold: LegalHold):
        """Release preserved data"""
        for target in legal_hold.preservation_targets:
            # Implementation would release preserved data
            target.status = "released"
    
    def _get_overdue_reviews(self) -> List[Dict[str, Any]]:
        """Get legal holds with overdue reviews"""
        overdue = []
        current_time = datetime.utcnow()
        
        for hold in self.legal_holds.values():
            if (hold.status == LegalHoldStatus.ACTIVE and 
                hold.next_review_date and 
                current_time > hold.next_review_date):
                overdue.append({
                    "hold_id": hold.hold_id,
                    "title": hold.title,
                    "next_review_date": hold.next_review_date.isoformat(),
                    "days_overdue": (current_time - hold.next_review_date).days
                })
        
        return overdue
    
    async def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
    
    def _update_metrics(self):
        """Update legal hold metrics"""
        total_holds = len(self.legal_holds)
        active_holds = len([h for h in self.legal_holds.values() if h.status == LegalHoldStatus.ACTIVE])
        total_custodians = sum(len(h.custodians) for h in self.legal_holds.values())
        
        # Calculate preserved data size
        total_preserved_gb = 0.0
        for hold in self.legal_holds.values():
            for target in hold.preservation_targets:
                if target.preserved_size:
                    total_preserved_gb += target.preserved_size / (1024 * 1024 * 1024)
        
        self.metrics.update({
            "active_holds": active_holds,
            "total_custodians": total_custodians,
            "data_preserved_gb": total_preserved_gb,
            "overdue_reviews": len(self._get_overdue_reviews())
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get legal hold metrics"""
        return self.metrics.copy()