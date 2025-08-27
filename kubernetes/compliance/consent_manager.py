"""
IA Influencer Agent - Consent Management System
Enterprise-grade consent orchestration and tracking system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

This module provides comprehensive consent management functionality including:
- Granular consent tracking and management
- Multi-purpose consent orchestration
- Consent withdrawal processing
- Privacy preference centers
- Compliance-ready consent documentation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.compliance import ConsentRecord, ConsentHistory, PrivacyPreference
from backend.models.user import User
from backend.core.security import encrypt_data, decrypt_data
from backend.utils.email import send_email
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel

logger = get_logger(__name__)


class ConsentType(str, Enum):
    """Types of user consent"""
    ESSENTIAL = "essential"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    THIRD_PARTY_SHARING = "third_party_sharing"
    AI_PROCESSING = "ai_processing"
    LOCATION_TRACKING = "location_tracking"
    BIOMETRIC_DATA = "biometric_data"
    SENSITIVE_CATEGORIES = "sensitive_categories"


class ConsentStatus(str, Enum):
    """Consent status values"""
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"
    INVALID = "invalid"
    RENEWED = "renewed"


class ConsentMethod(str, Enum):
    """Methods of consent collection"""
    EXPLICIT_CHECKBOX = "explicit_checkbox"
    DIGITAL_SIGNATURE = "digital_signature"
    EMAIL_CONFIRMATION = "email_confirmation"
    BIOMETRIC_VERIFICATION = "biometric_verification"
    VERBAL_CONFIRMATION = "verbal_confirmation"
    IMPLIED_CONSENT = "implied_consent"
    OPT_IN_FORM = "opt_in_form"
    COOKIE_BANNER = "cookie_banner"


class ProcessingPurpose(str, Enum):
    """Data processing purposes"""
    SERVICE_PROVISION = "service_provision"
    CONTENT_PERSONALIZATION = "content_personalization"
    ANALYTICS_INSIGHTS = "analytics_insights"
    MARKETING_CAMPAIGNS = "marketing_campaigns"
    FRAUD_PREVENTION = "fraud_prevention"
    LEGAL_COMPLIANCE = "legal_compliance"
    RESEARCH_DEVELOPMENT = "research_development"
    PLATFORM_IMPROVEMENT = "platform_improvement"
    THIRD_PARTY_INTEGRATION = "third_party_integration"
    AI_MODEL_TRAINING = "ai_model_training"


@dataclass
class ConsentDetails:
    """Detailed consent information"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    purpose: ProcessingPurpose
    status: ConsentStatus
    method: ConsentMethod
    timestamp: datetime
    expiry_date: Optional[datetime]
    legal_basis: str
    data_categories: List[str]
    third_parties: List[str]
    withdrawal_method: Optional[str]
    evidence_url: Optional[str]
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any]


@dataclass
class ConsentBundle:
    """Bundle of related consents"""
    bundle_id: str
    user_id: str
    bundle_name: str
    consents: List[ConsentDetails]
    created_at: datetime
    updated_at: datetime
    version: str
    is_active: bool


@dataclass
class PrivacyPreferences:
    """User privacy preferences"""
    user_id: str
    communication_preferences: Dict[str, bool]
    data_sharing_preferences: Dict[str, bool]
    retention_preferences: Dict[str, int]
    marketing_preferences: Dict[str, bool]
    analytics_preferences: Dict[str, bool]
    third_party_preferences: Dict[str, bool]
    created_at: datetime
    updated_at: datetime


class ConsentManager:
    """
    Enterprise-grade consent management system providing comprehensive
    consent orchestration, tracking, and compliance functionality.
    """

    def __init__(self):
        self.audit_logger = AuditLogger()
        self.session_cache = {}
        self.consent_templates = {}
        self.withdrawal_handlers = {}

    async def grant_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: ProcessingPurpose,
        method: ConsentMethod,
        legal_basis: str,
        data_categories: List[str] = None,
        third_parties: List[str] = None,
        expiry_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None,
        request_context: Dict[str, Any] = None
    ) -> ConsentDetails:
        """
        Grant user consent with comprehensive tracking
        
        Args:
            user_id: User identifier
            consent_type: Type of consent being granted
            purpose: Purpose of data processing
            method: Method used to collect consent
            legal_basis: Legal basis for processing
            data_categories: Categories of data involved
            third_parties: Third parties with access
            expiry_date: Optional expiry date
            metadata: Additional metadata
            request_context: Request context information
            
        Returns:
            ConsentDetails: Detailed consent record
        """
        try:
            async with get_db_session() as session:
                # Validate user exists
                user = await session.get(User, user_id)
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                # Create consent record
                consent_id = f"consent_{user_id}_{consent_type.value}_{int(datetime.now().timestamp())}"
                
                consent_details = ConsentDetails(
                    consent_id=consent_id,
                    user_id=user_id,
                    consent_type=consent_type,
                    purpose=purpose,
                    status=ConsentStatus.GRANTED,
                    method=method,
                    timestamp=datetime.now(),
                    expiry_date=expiry_date,
                    legal_basis=legal_basis,
                    data_categories=data_categories or [],
                    third_parties=third_parties or [],
                    withdrawal_method=None,
                    evidence_url=None,
                    ip_address=request_context.get("ip_address", "") if request_context else "",
                    user_agent=request_context.get("user_agent", "") if request_context else "",
                    metadata=metadata or {}
                )

                # Store in database
                consent_record = ConsentRecord(
                    consent_id=consent_id,
                    user_id=user_id,
                    consent_type=consent_type.value,
                    purpose=purpose.value,
                    status=ConsentStatus.GRANTED.value,
                    method=method.value,
                    legal_basis=legal_basis,
                    data_categories=json.dumps(data_categories or []),
                    third_parties=json.dumps(third_parties or []),
                    expiry_date=expiry_date,
                    metadata=json.dumps(metadata or {}),
                    ip_address=consent_details.ip_address,
                    user_agent=consent_details.user_agent
                )

                session.add(consent_record)
                await session.commit()

                # Log consent granting
                await self.audit_logger.log_event(
                    category=AuditCategory.CONSENT_MANAGEMENT,
                    level=AuditLevel.INFO,
                    event_type="consent_granted",
                    user_id=user_id,
                    details={
                        "consent_id": consent_id,
                        "consent_type": consent_type.value,
                        "purpose": purpose.value,
                        "method": method.value,
                        "legal_basis": legal_basis,
                        "expiry_date": expiry_date.isoformat() if expiry_date else None
                    }
                )

                # Send confirmation if required
                if method in [ConsentMethod.EMAIL_CONFIRMATION]:
                    await self._send_consent_confirmation(user, consent_details)

                return consent_details

        except Exception as e:
            logger.error(f"Failed to grant consent: {str(e)}")
            await self.audit_logger.log_event(
                category=AuditCategory.CONSENT_MANAGEMENT,
                level=AuditLevel.ERROR,
                event_type="consent_grant_failed",
                user_id=user_id,
                details={"error": str(e), "consent_type": consent_type.value}
            )
            raise

    async def withdraw_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        withdrawal_method: str,
        reason: Optional[str] = None,
        request_context: Dict[str, Any] = None
    ) -> bool:
        """
        Withdraw user consent with audit trail
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to withdraw
            withdrawal_method: Method used for withdrawal
            reason: Optional reason for withdrawal
            request_context: Request context information
            
        Returns:
            bool: Success status
        """
        try:
            async with get_db_session() as session:
                # Find active consent
                query = select(ConsentRecord).where(
                    and_(
                        ConsentRecord.user_id == user_id,
                        ConsentRecord.consent_type == consent_type.value,
                        ConsentRecord.status == ConsentStatus.GRANTED.value
                    )
                )
                result = await session.execute(query)
                consent_record = result.scalar_one_or_none()

                if not consent_record:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"No active consent found for type: {consent_type.value}"
                    )

                # Update consent status
                consent_record.status = ConsentStatus.WITHDRAWN.value
                consent_record.withdrawal_date = datetime.now()
                consent_record.withdrawal_method = withdrawal_method
                consent_record.withdrawal_reason = reason

                await session.commit()

                # Process withdrawal implications
                await self._process_consent_withdrawal(user_id, consent_type, session)

                # Log consent withdrawal
                await self.audit_logger.log_event(
                    category=AuditCategory.CONSENT_MANAGEMENT,
                    level=AuditLevel.INFO,
                    event_type="consent_withdrawn",
                    user_id=user_id,
                    details={
                        "consent_id": consent_record.consent_id,
                        "consent_type": consent_type.value,
                        "withdrawal_method": withdrawal_method,
                        "reason": reason
                    }
                )

                return True

        except Exception as e:
            logger.error(f"Failed to withdraw consent: {str(e)}")
            await self.audit_logger.log_event(
                category=AuditCategory.CONSENT_MANAGEMENT,
                level=AuditLevel.ERROR,
                event_type="consent_withdrawal_failed",
                user_id=user_id,
                details={"error": str(e), "consent_type": consent_type.value}
            )
            raise

    async def get_user_consents(
        self,
        user_id: str,
        status_filter: Optional[ConsentStatus] = None,
        include_history: bool = False
    ) -> List[ConsentDetails]:
        """
        Retrieve user consents with optional filtering
        
        Args:
            user_id: User identifier
            status_filter: Optional status filter
            include_history: Include consent history
            
        Returns:
            List[ConsentDetails]: User consent records
        """
        try:
            async with get_db_session() as session:
                query = select(ConsentRecord).where(ConsentRecord.user_id == user_id)
                
                if status_filter:
                    query = query.where(ConsentRecord.status == status_filter.value)

                result = await session.execute(query)
                consent_records = result.scalars().all()

                consents = []
                for record in consent_records:
                    consent_details = ConsentDetails(
                        consent_id=record.consent_id,
                        user_id=record.user_id,
                        consent_type=ConsentType(record.consent_type),
                        purpose=ProcessingPurpose(record.purpose),
                        status=ConsentStatus(record.status),
                        method=ConsentMethod(record.method),
                        timestamp=record.created_at,
                        expiry_date=record.expiry_date,
                        legal_basis=record.legal_basis,
                        data_categories=json.loads(record.data_categories or "[]"),
                        third_parties=json.loads(record.third_parties or "[]"),
                        withdrawal_method=record.withdrawal_method,
                        evidence_url=record.evidence_url,
                        ip_address=record.ip_address or "",
                        user_agent=record.user_agent or "",
                        metadata=json.loads(record.metadata or "{}")
                    )
                    consents.append(consent_details)

                return consents

        except Exception as e:
            logger.error(f"Failed to retrieve user consents: {str(e)}")
            raise

    async def check_consent_validity(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: ProcessingPurpose
    ) -> bool:
        """
        Check if user has valid consent for specific purpose
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            purpose: Purpose to validate
            
        Returns:
            bool: Consent validity status
        """
        try:
            async with get_db_session() as session:
                query = select(ConsentRecord).where(
                    and_(
                        ConsentRecord.user_id == user_id,
                        ConsentRecord.consent_type == consent_type.value,
                        ConsentRecord.purpose == purpose.value,
                        ConsentRecord.status == ConsentStatus.GRANTED.value,
                        or_(
                            ConsentRecord.expiry_date.is_(None),
                            ConsentRecord.expiry_date > datetime.now()
                        )
                    )
                )
                result = await session.execute(query)
                consent_record = result.scalar_one_or_none()

                return consent_record is not None

        except Exception as e:
            logger.error(f"Failed to check consent validity: {str(e)}")
            return False

    async def update_privacy_preferences(
        self,
        user_id: str,
        preferences: PrivacyPreferences
    ) -> bool:
        """
        Update user privacy preferences
        
        Args:
            user_id: User identifier
            preferences: Privacy preference settings
            
        Returns:
            bool: Update success status
        """
        try:
            async with get_db_session() as session:
                # Find or create privacy preference record
                query = select(PrivacyPreference).where(PrivacyPreference.user_id == user_id)
                result = await session.execute(query)
                pref_record = result.scalar_one_or_none()

                if pref_record:
                    # Update existing
                    pref_record.communication_preferences = json.dumps(preferences.communication_preferences)
                    pref_record.data_sharing_preferences = json.dumps(preferences.data_sharing_preferences)
                    pref_record.retention_preferences = json.dumps(preferences.retention_preferences)
                    pref_record.marketing_preferences = json.dumps(preferences.marketing_preferences)
                    pref_record.analytics_preferences = json.dumps(preferences.analytics_preferences)
                    pref_record.third_party_preferences = json.dumps(preferences.third_party_preferences)
                    pref_record.updated_at = datetime.now()
                else:
                    # Create new
                    pref_record = PrivacyPreference(
                        user_id=user_id,
                        communication_preferences=json.dumps(preferences.communication_preferences),
                        data_sharing_preferences=json.dumps(preferences.data_sharing_preferences),
                        retention_preferences=json.dumps(preferences.retention_preferences),
                        marketing_preferences=json.dumps(preferences.marketing_preferences),
                        analytics_preferences=json.dumps(preferences.analytics_preferences),
                        third_party_preferences=json.dumps(preferences.third_party_preferences)
                    )
                    session.add(pref_record)

                await session.commit()

                # Log preference update
                await self.audit_logger.log_event(
                    category=AuditCategory.PRIVACY_MANAGEMENT,
                    level=AuditLevel.INFO,
                    event_type="privacy_preferences_updated",
                    user_id=user_id,
                    details={"preferences_updated": True}
                )

                return True

        except Exception as e:
            logger.error(f"Failed to update privacy preferences: {str(e)}")
            return False

    async def generate_consent_report(
        self,
        user_id: Optional[str] = None,
        date_range: Optional[tuple] = None,
        consent_types: Optional[List[ConsentType]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive consent report
        
        Args:
            user_id: Optional user filter
            date_range: Optional date range filter
            consent_types: Optional consent type filter
            
        Returns:
            Dict[str, Any]: Comprehensive consent report
        """
        try:
            async with get_db_session() as session:
                # Build base query
                query = select(ConsentRecord)
                
                if user_id:
                    query = query.where(ConsentRecord.user_id == user_id)
                
                if date_range:
                    start_date, end_date = date_range
                    query = query.where(
                        and_(
                            ConsentRecord.created_at >= start_date,
                            ConsentRecord.created_at <= end_date
                        )
                    )
                
                if consent_types:
                    type_values = [ct.value for ct in consent_types]
                    query = query.where(ConsentRecord.consent_type.in_(type_values))

                result = await session.execute(query)
                consent_records = result.scalars().all()

                # Generate report statistics
                report = {
                    "report_id": f"consent_report_{int(datetime.now().timestamp())}",
                    "generated_at": datetime.now().isoformat(),
                    "total_consents": len(consent_records),
                    "consent_breakdown": {},
                    "status_breakdown": {},
                    "method_breakdown": {},
                    "purpose_breakdown": {},
                    "expiry_analysis": {},
                    "compliance_metrics": {}
                }

                # Analyze consent data
                for record in consent_records:
                    # Consent type breakdown
                    consent_type = record.consent_type
                    report["consent_breakdown"][consent_type] = report["consent_breakdown"].get(consent_type, 0) + 1

                    # Status breakdown
                    status = record.status
                    report["status_breakdown"][status] = report["status_breakdown"].get(status, 0) + 1

                    # Method breakdown
                    method = record.method
                    report["method_breakdown"][method] = report["method_breakdown"].get(method, 0) + 1

                    # Purpose breakdown
                    purpose = record.purpose
                    report["purpose_breakdown"][purpose] = report["purpose_breakdown"].get(purpose, 0) + 1

                # Calculate compliance metrics
                total_active = report["status_breakdown"].get("granted", 0)
                total_withdrawn = report["status_breakdown"].get("withdrawn", 0)
                
                report["compliance_metrics"] = {
                    "consent_rate": (total_active / len(consent_records)) * 100 if consent_records else 0,
                    "withdrawal_rate": (total_withdrawn / len(consent_records)) * 100 if consent_records else 0,
                    "total_users_tracked": len(set([r.user_id for r in consent_records])),
                    "average_consents_per_user": len(consent_records) / len(set([r.user_id for r in consent_records])) if consent_records else 0
                }

                return report

        except Exception as e:
            logger.error(f"Failed to generate consent report: {str(e)}")
            raise

    async def _process_consent_withdrawal(
        self,
        user_id: str,
        consent_type: ConsentType,
        session: AsyncSession
    ) -> None:
        """Process implications of consent withdrawal"""
        try:
            # Handle withdrawal implications based on consent type
            if consent_type == ConsentType.ANALYTICS:
                await self._stop_analytics_tracking(user_id)
            elif consent_type == ConsentType.MARKETING:
                await self._remove_from_marketing_lists(user_id)
            elif consent_type == ConsentType.PERSONALIZATION:
                await self._reset_personalization_data(user_id)
            elif consent_type == ConsentType.CONTENT_PROTECTION:
                await self._adjust_protection_settings(user_id)

        except Exception as e:
            logger.error(f"Failed to process consent withdrawal implications: {str(e)}")

    async def _send_consent_confirmation(
        self,
        user: User,
        consent_details: ConsentDetails
    ) -> None:
        """Send consent confirmation email"""
        try:
            subject = f"Consent Confirmation - {consent_details.consent_type.value.title()}"
            template_data = {
                "user_name": user.full_name,
                "consent_type": consent_details.consent_type.value,
                "purpose": consent_details.purpose.value,
                "timestamp": consent_details.timestamp.isoformat(),
                "consent_id": consent_details.consent_id
            }
            
            await send_email(
                to_email=user.email,
                subject=subject,
                template="consent_confirmation",
                template_data=template_data
            )

        except Exception as e:
            logger.error(f"Failed to send consent confirmation: {str(e)}")

    async def _stop_analytics_tracking(self, user_id: str) -> None:
        """Stop analytics tracking for user"""
        # Implementation for stopping analytics tracking
        pass

    async def _remove_from_marketing_lists(self, user_id: str) -> None:
        """Remove user from marketing lists"""
        # Implementation for removing from marketing lists
        pass

    async def _reset_personalization_data(self, user_id: str) -> None:
        """Reset personalization data for user"""
        # Implementation for resetting personalization data
        pass

    async def _adjust_protection_settings(self, user_id: str) -> None:
        """Adjust content protection settings"""
        # Implementation for adjusting protection settings
        pass


# Export classes
__all__ = [
    "ConsentManager",
    "ConsentType",
    "ConsentStatus",
    "ConsentMethod",
    "ProcessingPurpose",
    "ConsentDetails",
    "ConsentBundle",
    "PrivacyPreferences"
]
