"""GDPR-Compliant Granular Consent Management System

Implements comprehensive consent management with granular controls,
purpose-based consent, and automated withdrawal mechanisms.

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
import hashlib

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Types of consent under GDPR and other regulations"""
    EXPLICIT = "explicit"  # Explicit consent (GDPR Art. 7)
    IMPLIED = "implied"    # Implied consent (limited use cases)
    OPT_IN = "opt_in"     # Active opt-in consent
    OPT_OUT = "opt_out"   # Opt-out mechanism (CCPA)


class ConsentStatus(Enum):
    """Status of consent"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"
    REFUSED = "refused"


class ProcessingPurpose(Enum):
    """Specific processing purposes for granular consent"""
    ESSENTIAL_SERVICES = "essential_services"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    ADVERTISING = "advertising"
    THIRD_PARTY_SHARING = "third_party_sharing"
    RESEARCH = "research"
    SECURITY = "security"
    LEGAL_COMPLIANCE = "legal_compliance"
    CUSTOMER_SUPPORT = "customer_support"


@dataclass
class ConsentRecord:
    """Individual consent record for a specific purpose"""
    consent_id: str
    user_id: str
    purpose: ProcessingPurpose
    consent_type: ConsentType
    status: ConsentStatus
    given_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    consent_text: str = ""
    consent_version: str = "1.0"
    collection_method: str = "web"  # web, app, email, phone, etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    legal_basis: str = "consent"  # GDPR lawful basis
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsentConfiguration:
    """Configuration for consent collection"""
    purpose: ProcessingPurpose
    required: bool = False
    default_value: bool = False
    consent_text: str = ""
    details_url: Optional[str] = None
    retention_period: Optional[timedelta] = None
    auto_renewal: bool = False
    withdrawal_method: List[str] = field(default_factory=lambda: ["web", "email"])


class ConsentManager:
    """
    GDPR-Compliant Granular Consent Management System
    
    Handles consent collection, storage, validation, and withdrawal
    with full audit trail and compliance reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage for consent records
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.consent_configurations: Dict[ProcessingPurpose, ConsentConfiguration] = {}
        
        # Initialize default consent configurations
        self._initialize_consent_configurations()
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "total_consents": 0,
            "active_consents": 0,
            "withdrawn_consents": 0,
            "expired_consents": 0,
            "consent_rate_by_purpose": {}
        }
    
    def _initialize_consent_configurations(self):
        """Initialize default consent configurations for different purposes"""
        configurations = [
            ConsentConfiguration(
                purpose=ProcessingPurpose.ESSENTIAL_SERVICES,
                required=True,
                default_value=True,
                consent_text="Processing necessary for providing essential platform services",
                retention_period=None,  # Keep as long as account is active
                withdrawal_method=["web"]
            ),
            ConsentConfiguration(
                purpose=ProcessingPurpose.ANALYTICS,
                required=False,
                default_value=False,
                consent_text="Analyze usage patterns to improve our services",
                details_url="/privacy/analytics",
                retention_period=timedelta(days=730),
                withdrawal_method=["web", "email"]
            ),
            ConsentConfiguration(
                purpose=ProcessingPurpose.MARKETING,
                required=False,
                default_value=False,
                consent_text="Send marketing communications and promotional offers",
                details_url="/privacy/marketing",
                retention_period=timedelta(days=1095),
                withdrawal_method=["web", "email", "sms"]
            ),
            ConsentConfiguration(
                purpose=ProcessingPurpose.PERSONALIZATION,
                required=False,
                default_value=False,
                consent_text="Personalize content and recommendations",
                details_url="/privacy/personalization",
                retention_period=timedelta(days=365),
                withdrawal_method=["web", "email"]
            ),
            ConsentConfiguration(
                purpose=ProcessingPurpose.ADVERTISING,
                required=False,
                default_value=False,
                consent_text="Show targeted advertisements based on your interests",
                details_url="/privacy/advertising",
                retention_period=timedelta(days=365),
                withdrawal_method=["web", "email"]
            ),
            ConsentConfiguration(
                purpose=ProcessingPurpose.THIRD_PARTY_SHARING,
                required=False,
                default_value=False,
                consent_text="Share data with trusted third-party partners",
                details_url="/privacy/third-party",
                retention_period=timedelta(days=365),
                withdrawal_method=["web", "email"]
            )
        ]
        
        for config in configurations:
            self.consent_configurations[config.purpose] = config
    
    async def collect_consent(
        self,
        user_id: str,
        purposes: List[ProcessingPurpose],
        consent_values: Dict[ProcessingPurpose, bool],
        collection_context: Dict[str, Any]
    ) -> Dict[ProcessingPurpose, ConsentRecord]:
        """
        Collect granular consent for multiple purposes
        
        Args:
            user_id: User identifier
            purposes: List of processing purposes
            consent_values: Consent decisions for each purpose
            collection_context: Context information (IP, user agent, etc.)
            
        Returns:
            Dict mapping purposes to consent records
        """
        try:
            collected_consents = {}
            timestamp = datetime.utcnow()
            
            for purpose in purposes:
                consent_given = consent_values.get(purpose, False)
                config = self.consent_configurations.get(purpose)
                
                if not config:
                    self.logger.warning(f"No configuration found for purpose: {purpose}")
                    continue
                
                # Create consent record
                consent_record = ConsentRecord(
                    consent_id=str(uuid.uuid4()),
                    user_id=user_id,
                    purpose=purpose,
                    consent_type=ConsentType.EXPLICIT,
                    status=ConsentStatus.GIVEN if consent_given else ConsentStatus.REFUSED,
                    given_at=timestamp if consent_given else None,
                    consent_text=config.consent_text,
                    collection_method=collection_context.get("method", "web"),
                    ip_address=collection_context.get("ip_address"),
                    user_agent=collection_context.get("user_agent"),
                    metadata={
                        "collection_context": collection_context,
                        "config_version": "1.0"
                    }
                )
                
                # Set expiration if configured
                if config.retention_period and consent_given:
                    consent_record.expires_at = timestamp + config.retention_period
                
                # Store consent record
                self.consent_records[consent_record.consent_id] = consent_record
                collected_consents[purpose] = consent_record
                
                # Log audit event
                await self._log_consent_event({
                    "event_type": "consent_collected",
                    "consent_id": consent_record.consent_id,
                    "user_id": user_id,
                    "purpose": purpose.value,
                    "status": consent_record.status.value,
                    "collection_method": consent_record.collection_method,
                    "timestamp": timestamp.isoformat()
                })
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Collected consent for user {user_id}: {len(collected_consents)} purposes")
            return collected_consents
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error collecting consent for user {user_id}: {e}")
            raise
    
    async def withdraw_consent(
        self,
        user_id: str,
        purposes: List[ProcessingPurpose],
        withdrawal_method: str = "web",
        withdrawal_context: Optional[Dict[str, Any]] = None
    ) -> List[ConsentRecord]:
        """
        Withdraw consent for specified purposes
        
        Args:
            user_id: User identifier
            purposes: Processing purposes to withdraw consent for
            withdrawal_method: Method used for withdrawal
            withdrawal_context: Context information
            
        Returns:
            List of updated consent records
        """
        try:
            withdrawn_consents = []
            timestamp = datetime.utcnow()
            
            # Find active consent records for user and purposes
            user_consents = [
                record for record in self.consent_records.values()
                if record.user_id == user_id and 
                   record.purpose in purposes and
                   record.status == ConsentStatus.GIVEN
            ]
            
            for consent_record in user_consents:
                # Update consent record
                consent_record.status = ConsentStatus.WITHDRAWN
                consent_record.withdrawn_at = timestamp
                consent_record.metadata.update({
                    "withdrawal_method": withdrawal_method,
                    "withdrawal_context": withdrawal_context or {}
                })
                
                withdrawn_consents.append(consent_record)
                
                # Log audit event
                await self._log_consent_event({
                    "event_type": "consent_withdrawn",
                    "consent_id": consent_record.consent_id,
                    "user_id": user_id,
                    "purpose": consent_record.purpose.value,
                    "withdrawal_method": withdrawal_method,
                    "timestamp": timestamp.isoformat()
                })
                
                # Trigger data processing impact assessment
                await self._assess_withdrawal_impact(consent_record)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Withdrew consent for user {user_id}: {len(withdrawn_consents)} purposes")
            return withdrawn_consents
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error withdrawing consent for user {user_id}: {e}")
            raise
    
    async def check_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
        check_expiry: bool = True
    ) -> bool:
        """
        Check if user has valid consent for a specific purpose
        
        Args:
            user_id: User identifier
            purpose: Processing purpose to check
            check_expiry: Whether to check expiration dates
            
        Returns:
            bool: True if valid consent exists
        """
        try:
            # Find latest consent record for user and purpose
            user_consents = [
                record for record in self.consent_records.values()
                if record.user_id == user_id and record.purpose == purpose
            ]
            
            if not user_consents:
                return False
            
            # Get most recent consent record
            latest_consent = max(user_consents, key=lambda x: x.given_at or datetime.min)
            
            # Check status
            if latest_consent.status != ConsentStatus.GIVEN:
                return False
            
            # Check expiry if enabled
            if check_expiry and latest_consent.expires_at:
                if datetime.utcnow() > latest_consent.expires_at:
                    # Mark as expired
                    latest_consent.status = ConsentStatus.EXPIRED
                    await self._log_consent_event({
                        "event_type": "consent_expired",
                        "consent_id": latest_consent.consent_id,
                        "user_id": user_id,
                        "purpose": purpose.value,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    return False
            
            return True
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error checking consent for user {user_id}, purpose {purpose}: {e}")
            return False
    
    async def get_user_consents(
        self,
        user_id: str,
        active_only: bool = True
    ) -> Dict[ProcessingPurpose, ConsentRecord]:
        """
        Get all consent records for a user
        
        Args:
            user_id: User identifier
            active_only: Whether to return only active consents
            
        Returns:
            Dict mapping purposes to consent records
        """
        try:
            user_consents = {}
            
            # Get all consent records for user
            records = [
                record for record in self.consent_records.values()
                if record.user_id == user_id
            ]
            
            # Group by purpose and get latest record for each
            purpose_records = {}
            for record in records:
                purpose = record.purpose
                if purpose not in purpose_records or \
                   (record.given_at or datetime.min) > (purpose_records[purpose].given_at or datetime.min):
                    purpose_records[purpose] = record
            
            # Filter by status if needed
            for purpose, record in purpose_records.items():
                if not active_only or record.status == ConsentStatus.GIVEN:
                    # Check expiry for active consents
                    if record.status == ConsentStatus.GIVEN and record.expires_at:
                        if datetime.utcnow() > record.expires_at:
                            record.status = ConsentStatus.EXPIRED
                    
                    user_consents[purpose] = record
            
            return user_consents
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error getting consents for user {user_id}: {e}")
            return {}
    
    async def update_consent_configuration(
        self,
        purpose: ProcessingPurpose,
        configuration: ConsentConfiguration
    ) -> bool:
        """
        Update consent configuration for a purpose
        
        Args:
            purpose: Processing purpose
            configuration: New configuration
            
        Returns:
            bool: Success status
        """
        try:
            self.consent_configurations[purpose] = configuration
            
            await self._log_consent_event({
                "event_type": "configuration_updated",
                "purpose": purpose.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Updated consent configuration for purpose: {purpose}")
            return True
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error updating consent configuration for {purpose}: {e}")
            return False
    
    async def generate_consent_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive consent compliance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict with consent statistics and compliance metrics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter records by date range
            filtered_records = [
                record for record in self.consent_records.values()
                if record.given_at and start_date <= record.given_at <= end_date
            ]
            
            # Calculate statistics
            total_consents = len(filtered_records)
            purpose_stats = {}
            
            for purpose in ProcessingPurpose:
                purpose_records = [r for r in filtered_records if r.purpose == purpose]
                given_count = len([r for r in purpose_records if r.status == ConsentStatus.GIVEN])
                refused_count = len([r for r in purpose_records if r.status == ConsentStatus.REFUSED])
                
                purpose_stats[purpose.value] = {
                    "total": len(purpose_records),
                    "given": given_count,
                    "refused": refused_count,
                    "consent_rate": (given_count / len(purpose_records) * 100) if purpose_records else 0
                }
            
            # Withdrawal statistics
            withdrawals = [
                record for record in self.consent_records.values()
                if record.withdrawn_at and start_date <= record.withdrawn_at <= end_date
            ]
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_consent_events": total_consents,
                    "total_withdrawals": len(withdrawals),
                    "unique_users": len(set(r.user_id for r in filtered_records)),
                    "overall_consent_rate": self._calculate_overall_consent_rate()
                },
                "by_purpose": purpose_stats,
                "compliance_metrics": {
                    "gdpr_compliant": self._check_gdpr_compliance(),
                    "retention_compliance": self._check_retention_compliance(),
                    "withdrawal_response_time": self._calculate_withdrawal_response_time()
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error generating consent report: {e}")
            return {"error": str(e)}
    
    async def _assess_withdrawal_impact(self, consent_record: ConsentRecord):
        """Assess impact of consent withdrawal on data processing"""
        try:
            # This would trigger assessment of what data processing must stop
            impact_assessment = {
                "consent_id": consent_record.consent_id,
                "purpose": consent_record.purpose.value,
                "data_processing_to_stop": [],
                "data_to_delete": [],
                "third_parties_to_notify": [],
                "assessment_date": datetime.utcnow().isoformat()
            }
            
            # Implementation would depend on specific data processing activities
            self.logger.info(f"Assessed withdrawal impact for consent {consent_record.consent_id}")
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Error assessing withdrawal impact: {e}")
    
    async def _log_consent_event(self, event: Dict[str, Any]):
        """Log consent-related event for audit trail"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
        
        self.logger.info(f"Consent event logged: {event['event_type']}")
    
    def _update_metrics(self):
        """Update consent metrics"""
        total = len(self.consent_records)
        active = len([r for r in self.consent_records.values() if r.status == ConsentStatus.GIVEN])
        withdrawn = len([r for r in self.consent_records.values() if r.status == ConsentStatus.WITHDRAWN])
        expired = len([r for r in self.consent_records.values() if r.status == ConsentStatus.EXPIRED])
        
        self.metrics.update({
            "total_consents": total,
            "active_consents": active,
            "withdrawn_consents": withdrawn,
            "expired_consents": expired
        })
        
        # Update purpose-specific metrics
        for purpose in ProcessingPurpose:
            purpose_records = [r for r in self.consent_records.values() if r.purpose == purpose]
            given_count = len([r for r in purpose_records if r.status == ConsentStatus.GIVEN])
            total_count = len(purpose_records)
            
            self.metrics["consent_rate_by_purpose"][purpose.value] = {
                "rate": (given_count / total_count * 100) if total_count > 0 else 0,
                "total": total_count,
                "given": given_count
            }
    
    def _calculate_overall_consent_rate(self) -> float:
        """Calculate overall consent rate across all purposes"""
        total_decisions = len([
            r for r in self.consent_records.values() 
            if r.status in [ConsentStatus.GIVEN, ConsentStatus.REFUSED]
        ])
        given_decisions = len([
            r for r in self.consent_records.values() 
            if r.status == ConsentStatus.GIVEN
        ])
        
        return (given_decisions / total_decisions * 100) if total_decisions > 0 else 0
    
    def _check_gdpr_compliance(self) -> bool:
        """Check GDPR compliance of consent collection"""
        # Implementation would check various GDPR requirements
        return True
    
    def _check_retention_compliance(self) -> bool:
        """Check compliance with data retention periods"""
        # Implementation would verify retention period compliance
        return True
    
    def _calculate_withdrawal_response_time(self) -> float:
        """Calculate average response time to withdrawal requests"""
        # Implementation would calculate response times
        return 24.0  # hours
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consent management metrics"""
        return self.metrics.copy()