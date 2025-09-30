"""IA Influencer Agent - GDPR Compliance Manager
Enterprise-grade GDPR compliance automation and management

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
from sqlalchemy import select, update, delete
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.user import User
from backend.models.compliance import GDPRRequest, ConsentRecord, DataProcessingLog
from backend.core.security import encrypt_data, decrypt_data
from backend.utils.email import send_email
from backend.core.logging import get_logger

logger = get_logger(__name__)


class GDPRRequestType(str, Enum):
    """
GDPR request types"""

    ACCESS = "access"
    PORTABILITY = "portability"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    OBJECTION = "objection"


class ConsentPurpose(str, Enum):
    """Data processing consent purposes"""

    ESSENTIAL = "essential"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    THIRD_PARTY = "third_party"


class ProcessingLawfulBasis(str, Enum):
    """GDPR lawful basis for processing"""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


@dataclass
class PersonalDataInventory:
    """Personal data inventory for GDPR compliance"""
    data_category: str
    data_elements: List[str]
    processing_purpose: str
    lawful_basis: ProcessingLawfulBasis
    retention_period: int  # days
    storage_location: str
    third_party_sharing: bool
    cross_border_transfer: bool
    encryption_status: bool


@dataclass
class GDPRComplianceReport:
    """
GDPR compliance status report"""
    user_id: int
    report_date: datetime
    consent_status: Dict[str, bool]
    data_inventory: List[PersonalDataInventory]
    active_processing: List[str]
    retention_compliance: bool
    outstanding_requests: List[Dict[str, Any]]
    compliance_score: float


class GDPRComplianceManager:
    """
Enterprise GDPR compliance manager with automation"""
    
    def __init__(self):
        self.logger = logger
        self.encryption_enabled = settings.ENCRYPTION_ENABLED
        self.data_retention_days = settings.GDPR_DATA_RETENTION_DAYS
        self.automated_erasure = settings.GDPR_AUTOMATED_ERASURE
        
        # Personal data inventory mapping
        self.data_inventory = {
            "user_profile": PersonalDataInventory(
                data_category="Identity Data",
                data_elements=["name", "email", "phone", "address"],
                processing_purpose="User account management",
                lawful_basis=ProcessingLawfulBasis.CONTRACT,
                retention_period=2555,  # 7 years
                storage_location="EU database",
                third_party_sharing=False,
                cross_border_transfer=False,
                encryption_status=True
            ),
            "content_metadata": PersonalDataInventory(
                data_category="Content Data",
                data_elements=["uploads", "fingerprints", "metadata"],
                processing_purpose="Content protection services",
                lawful_basis=ProcessingLawfulBasis.CONTRACT,
                retention_period=1825,  # 5 years
                storage_location="EU storage",
                third_party_sharing=True,
                cross_border_transfer=False,
                encryption_status=True
            ),
            "analytics_data": PersonalDataInventory(
                data_category="Behavioral Data",
                data_elements=["usage_patterns", "preferences", "interactions"],
                processing_purpose="Service improvement and analytics",
                lawful_basis=ProcessingLawfulBasis.CONSENT,
                retention_period=730,  # 2 years
                storage_location="EU analytics",
                third_party_sharing=False,
                cross_border_transfer=False,
                encryption_status=True
            ),
            "financial_data": PersonalDataInventory(
                data_category="Financial Data",
                data_elements=["payment_methods", "transactions", "revenue"],
                processing_purpose="Payment processing and monetization",
                lawful_basis=ProcessingLawfulBasis.CONTRACT,
                retention_period=2555,  # 7 years (legal requirement)
                storage_location="EU secure vault",
                third_party_sharing=True,
                cross_border_transfer=False,
                encryption_status=True
            )
        }
    
    async def record_consent(
        self,
        user_id: int,
        purpose: ConsentPurpose,
        granted: bool,
        ip_address: str,
        user_agent: str,
        explicit_consent: bool = False
    ) -> ConsentRecord:
        """Record user consent with full audit trail"""
        try:
            async with get_db_session() as session:
                consent_record = ConsentRecord(
                    user_id=user_id,
                    purpose=purpose.value,
                    granted=granted,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    explicit_consent=explicit_consent,
                    consent_date=datetime.utcnow(),
                    consent_version="1.0",
                    withdrawal_date=None if granted else datetime.utcnow()
                )
                
                session.add(consent_record)
                await session.commit()
                await session.refresh(consent_record)
                
                # Log data processing event
                await self._log_data_processing(
                    user_id=user_id,
                    activity="consent_recorded",
                    purpose=purpose.value,
                    lawful_basis=ProcessingLawfulBasis.CONSENT.value,
                    data_categories=["consent_data"],
                    processing_details={
                        "consent_granted": granted,
                        "explicit": explicit_consent,
                        "ip_address": ip_address
                    }
                )
                
                self.logger.info(
                    f"Consent recorded for user {user_id}: {purpose.value} = {granted}"
                )
                
                return consent_record
                
        except Exception as e:
            self.logger.error(f"Error recording consent: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to record consent")
    
    async def withdraw_consent(
        self,
        user_id: int,
        purpose: ConsentPurpose,
        ip_address: str
    ) -> bool:
        """Withdraw user consent and trigger data processing restrictions"""
        try:
            async with get_db_session() as session:
                # Update existing consent record
                stmt = update(ConsentRecord).where(
                    ConsentRecord.user_id == user_id,
                    ConsentRecord.purpose == purpose.value,
                    ConsentRecord.granted == True,
                    ConsentRecord.withdrawal_date.is_(None)
                ).values(
                    granted=False,
                    withdrawal_date=datetime.utcnow(),
                    withdrawal_ip=ip_address
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                if result.rowcount > 0:
                    # Trigger data processing restrictions
                    await self._restrict_processing_for_purpose(user_id, purpose)
                    
                    # Log withdrawal
                    await self._log_data_processing(
                        user_id=user_id,
                        activity="consent_withdrawn",
                        purpose=purpose.value,
                        lawful_basis=ProcessingLawfulBasis.CONSENT.value,
                        data_categories=["consent_data"],
                        processing_details={
                            "withdrawal_ip": ip_address,
                            "automatic_restrictions": True
                        }
                    )
                    
                    self.logger.info(
                        f"Consent withdrawn for user {user_id}: {purpose.value}"
                    )
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error withdrawing consent: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to withdraw consent")
    
    async def process_gdpr_request(
        self,
        user_id: int,
        request_type: GDPRRequestType,
        request_details: Dict[str, Any],
        requester_ip: str
    ) -> str:
        """Process GDPR data subject requests"""
        try:
            async with get_db_session() as session:
                # Create GDPR request record
                gdpr_request = GDPRRequest(
                    user_id=user_id,
                    request_type=request_type.value,
                    request_details=json.dumps(request_details),
                    requester_ip=requester_ip,
                    status="pending",
                    submitted_date=datetime.utcnow(),
                    target_completion_date=datetime.utcnow() + timedelta(days=30)
                )
                
                session.add(gdpr_request)
                await session.commit()
                await session.refresh(gdpr_request)
                
                request_id = f"GDPR-{gdpr_request.id:08d}"
                
                # Process request based on type
                if request_type == GDPRRequestType.ACCESS:
                    await self._process_access_request(user_id, request_id)
                elif request_type == GDPRRequestType.PORTABILITY:
                    await self._process_portability_request(user_id, request_id)
                elif request_type == GDPRRequestType.ERASURE:
                    await self._process_erasure_request(user_id, request_id)
                elif request_type == GDPRRequestType.RECTIFICATION:
                    await self._process_rectification_request(
                        user_id, request_id, request_details
                    )
                elif request_type == GDPRRequestType.RESTRICTION:
                    await self._process_restriction_request(user_id, request_id)
                elif request_type == GDPRRequestType.OBJECTION:
                    await self._process_objection_request(user_id, request_id)
                
                # Update request status
                await session.execute(
                    update(GDPRRequest)
                    .where(GDPRRequest.id == gdpr_request.id)
                    .values(
                        status="processing",
                        processing_start_date=datetime.utcnow()
                    )
                )
                await session.commit()
                
                # Log GDPR request
                await self._log_data_processing(
                    user_id=user_id,
                    activity="gdpr_request_submitted",
                    purpose="legal_compliance",
                    lawful_basis=ProcessingLawfulBasis.LEGAL_OBLIGATION.value,
                    data_categories=["personal_data"],
                    processing_details={
                        "request_type": request_type.value,
                        "request_id": request_id,
                        "requester_ip": requester_ip
                    }
                )
                
                self.logger.info(
                    f"GDPR request {request_id} submitted for user {user_id}: {request_type.value}"
                )
                
                return request_id
                
        except Exception as e:
            self.logger.error(f"Error processing GDPR request: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process GDPR request")
    
    async def generate_compliance_report(self, user_id: int) -> GDPRComplianceReport:
        """Generate comprehensive GDPR compliance report for user"""
        try:
            async with get_db_session() as session:
                # Get user data
                user_result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                # Get consent status
                consent_result = await session.execute(
                    select(ConsentRecord).where(
                        ConsentRecord.user_id == user_id,
                        ConsentRecord.withdrawal_date.is_(None)
                    )
                )
                consents = consent_result.scalars().all()
                
                consent_status = {}
                for purpose in ConsentPurpose:
                    user_consent = next(
                        (c for c in consents if c.purpose == purpose.value),
                        None
                    )
                    consent_status[purpose.value] = (
                        user_consent.granted if user_consent else False
                    )
                
                # Get outstanding GDPR requests
                requests_result = await session.execute(
                    select(GDPRRequest).where(
                        GDPRRequest.user_id == user_id,
                        GDPRRequest.status.in_(["pending", "processing"])
                    )
                )
                outstanding_requests = [
                    {
                        "id": f"GDPR-{req.id:08d}",
                        "type": req.request_type,
                        "submitted": req.submitted_date.isoformat(),
                        "status": req.status
                    }
                    for req in requests_result.scalars().all()
                ]
                
                # Check retention compliance
                retention_compliance = await self._check_retention_compliance(user_id)
                
                # Calculate compliance score
                compliance_score = await self._calculate_compliance_score(
                    user_id, consent_status, retention_compliance, outstanding_requests
                )
                
                # Create compliance report
                report = GDPRComplianceReport(
                    user_id=user_id,
                    report_date=datetime.utcnow(),
                    consent_status=consent_status,
                    data_inventory=list(self.data_inventory.values()),
                    active_processing=await self._get_active_processing(user_id),
                    retention_compliance=retention_compliance,
                    outstanding_requests=outstanding_requests,
                    compliance_score=compliance_score
                )
                
                self.logger.info(
                    f"GDPR compliance report generated for user {user_id}: {compliance_score:.2f}%"
                )
                
                return report
                
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate compliance report")
    
    async def automated_data_retention_cleanup(self) -> Dict[str, int]:
        """Automated data retention cleanup based on GDPR requirements"""
        try:
            cleanup_stats = {
                "users_processed": 0,
                "records_deleted": 0,
                "errors": 0
            }
            
            if not self.automated_erasure:
                self.logger.info("Automated erasure disabled, skipping cleanup")
                return cleanup_stats
            
            async with get_db_session() as session:
                # Get users with expired data
                cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_days)
                
                expired_users_result = await session.execute(
                    select(User.id).where(
                        User.last_activity < cutoff_date,
                        User.account_status == "inactive"
                    )
                )
                expired_user_ids = [row[0] for row in expired_users_result.fetchall()]
                
                for user_id in expired_user_ids:
                    try:
                        # Check if user has valid consent for retention
                        has_valid_consent = await self._has_valid_retention_consent(user_id)
                        
                        if not has_valid_consent:
                            # Perform automated erasure
                            await self._perform_automated_erasure(user_id)
                            cleanup_stats["records_deleted"] += 1
                        
                        cleanup_stats["users_processed"] += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error cleaning up user {user_id}: {str(e)}")
                        cleanup_stats["errors"] += 1
                
                self.logger.info(
                    f"Automated cleanup completed: {cleanup_stats}"
                )
                
                return cleanup_stats
                
        except Exception as e:
            self.logger.error(f"Error in automated cleanup: {str(e)}")
            return {"users_processed": 0, "records_deleted": 0, "errors": 1}
    
    async def _process_access_request(self, user_id: int, request_id: str) -> None:
        """Process data access request - provide copy of personal data"""
        try:
            # Collect all personal data for user
            personal_data = await self._collect_personal_data(user_id)
            
            # Generate secure download link or email data package
            data_package_url = await self._create_secure_data_package(
                user_id, personal_data, request_id
            )
            
            # Notify user
            await self._notify_user_gdpr_completion(
                user_id, request_id, "access", data_package_url
            )
            
        except Exception as e:
            self.logger.error(f"Error processing access request {request_id}: {str(e)}")
            raise
    
    async def _process_portability_request(self, user_id: int, request_id: str) -> None:
        """Process data portability request - provide structured data export"""
        try:
            # Export data in structured, machine-readable format
            portable_data = await self._export_portable_data(user_id)
            
            # Create download package
            export_url = await self._create_portability_package(
                user_id, portable_data, request_id
            )
            
            # Notify user
            await self._notify_user_gdpr_completion(
                user_id, request_id, "portability", export_url
            )
            
        except Exception as e:
            self.logger.error(f"Error processing portability request {request_id}: {str(e)}")
            raise
    
    async def _process_erasure_request(self, user_id: int, request_id: str) -> None:
        """Process right to erasure request - delete personal data"""
        try:
            # Check if erasure is legally permissible
            can_erase = await self._check_erasure_eligibility(user_id)
            
            if can_erase:
                # Perform data erasure
                await self._perform_data_erasure(user_id)
                
                # Notify completion
                await self._notify_user_gdpr_completion(
                    user_id, request_id, "erasure_completed"
                )
            else:
                # Notify restrictions
                await self._notify_user_gdpr_completion(
                    user_id, request_id, "erasure_restricted"
                )
            
        except Exception as e:
            self.logger.error(f"Error processing erasure request {request_id}: {str(e)}")
            raise
    
    async def _log_data_processing(
        self,
        user_id: int,
        activity: str,
        purpose: str,
        lawful_basis: str,
        data_categories: List[str],
        processing_details: Dict[str, Any]
    ) -> None:
        """Log data processing activity for GDPR audit trail"""
        try:
            async with get_db_session() as session:
                log_entry = DataProcessingLog(
                    user_id=user_id,
                    activity=activity,
                    purpose=purpose,
                    lawful_basis=lawful_basis,
                    data_categories=json.dumps(data_categories),
                    processing_details=json.dumps(processing_details),
                    timestamp=datetime.utcnow(),
                    processor_id="system",
                    retention_period=self._get_retention_period_for_purpose(purpose)
                )
                
                session.add(log_entry)
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error logging data processing: {str(e)}")
    
    async def _calculate_compliance_score(
        self,
        user_id: int,
        consent_status: Dict[str, bool],
        retention_compliance: bool,
        outstanding_requests: List[Dict]
    ) -> float:
        """Calculate GDPR compliance score for user"""
        score = 100.0
        
        # Deduct for missing essential consents
        essential_consents = sum(1 for purpose, granted in consent_status.items() 
                               if purpose in ["essential", "contract"] and granted)
        if essential_consents < 2:
            score -= 20.0
        
        # Deduct for retention non-compliance
        if not retention_compliance:
            score -= 30.0
        
        # Deduct for overdue requests
        overdue_requests = [
            req for req in outstanding_requests
            if datetime.fromisoformat(req["submitted"]) < 
               datetime.utcnow() - timedelta(days=30)
        ]
        score -= len(overdue_requests) * 10.0
        
        return max(0.0, min(100.0, score))
    
    def _get_retention_period_for_purpose(self, purpose: str) -> int:
        """Get data retention period in days for processing purpose"""
        retention_mapping = {
            "essential": 2555,  # 7 years
            "contract": 2555,   # 7 years
            "legal_compliance": 2555,  # 7 years
            "analytics": 730,   # 2 years
            "marketing": 1095,  # 3 years
            "content_protection": 1825,  # 5 years
            "monetization": 2555  # 7 years
        }
        return retention_mapping.get(purpose, 365)  # Default 1 year


# Export for use in other modules
__all__ = ["GDPRComplianceManager", "GDPRRequestType", "ConsentPurpose", "ProcessingLawfulBasis"]
