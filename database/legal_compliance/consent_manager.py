"""Consent Manager - GDPR and Privacy Consent Management

Advanced consent management system providing granular consent tracking,
withdrawal processing, and compliance verification for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import uuid
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Types of consent that can be managed."""    ESSENTIAL = "essential"  # Required for basic functionality
    FUNCTIONAL = "functional"  # For enhanced functionality
    ANALYTICS = "analytics"  # For analytics and performance
    MARKETING = "marketing"  # For marketing communications
    PERSONALIZATION = "personalization"  # For personalized content
    THIRD_PARTY = "third_party"  # For third-party integrations
    BIOMETRIC = "biometric"  # For biometric data processing
    FINANCIAL = "financial"  # For financial data processing
    HEALTH = "health"  # For health-related data
    LOCATION = "location"  # For location tracking


class ConsentStatus(Enum):
    """Consent status values."""    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"


class ConsentMethod(Enum):
    """Method by which consent was obtained."""    EXPLICIT = "explicit"  # Clear affirmative action
    IMPLIED = "implied"  # Implied from behavior
    OPT_IN = "opt_in"  # Active opt-in
    OPT_OUT = "opt_out"  # Default with opt-out option
    COOKIE_BANNER = "cookie_banner"  # Via cookie banner
    FORM_SUBMISSION = "form_submission"  # Via form
    API = "api"  # Programmatically via API


class DataCategory(Enum):
    """Categories of data for consent management."""    PERSONAL_IDENTIFIERS = "personal_identifiers"
    CONTACT_INFORMATION = "contact_information"
    DEMOGRAPHIC_DATA = "demographic_data"
    BEHAVIORAL_DATA = "behavioral_data"
    PREFERENCES = "preferences"
    USAGE_DATA = "usage_data"
    DEVICE_DATA = "device_data"
    LOCATION_DATA = "location_data"
    BIOMETRIC_DATA = "biometric_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    CONTENT_DATA = "content_data"


@dataclass
class ConsentPurpose:
    """Specific purpose for data processing consent."""    purpose_id: str
    name: str
    description: str
    data_categories: List[DataCategory]
    legal_basis: str
    retention_period_days: Optional[int]
    third_parties: List[str]
    required: bool


@dataclass
class ConsentRecord:
    """Individual consent record."""    consent_id: str
    user_id: str
    consent_type: ConsentType
    purpose: ConsentPurpose
    status: ConsentStatus
    method: ConsentMethod
    granted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    ip_address: Optional[str]
    user_agent: Optional[str]
    evidence: Dict[str, Any]
    metadata: Dict[str, Any]
    version: str


@dataclass
class ConsentWithdrawal:
    """Consent withdrawal request."""    withdrawal_id: str
    consent_id: str
    user_id: str
    requested_at: datetime
    processed_at: Optional[datetime]
    method: ConsentMethod
    reason: Optional[str]
    status: str
    data_deletion_required: bool
    evidence: Dict[str, Any]


class ConsentManager:
    """    Comprehensive consent management system for GDPR compliance.
    
    Manages granular consent collection, tracking, withdrawal,
    and automated compliance verification across all data processing activities.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the Consent Manager.
        
        Args:
            config: Configuration dictionary with consent settings
        """        self.config = config
        self.consent_config = config.get("consent", {})
        
        # Consent data storage
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.consent_withdrawals: Dict[str, ConsentWithdrawal] = {}
        self.consent_purposes: Dict[str, ConsentPurpose] = {}
        
        # Consent tracking
        self.user_consents: Dict[str, List[str]] = {}  # user_id -> consent_ids
        
        # Load configured consent purposes
        self._initialize_consent_purposes()
        
        # Consent settings
        self.auto_expiry_enabled = self.consent_config.get("auto_expiry_enabled", True)
        self.default_expiry_days = self.consent_config.get("default_expiry_days", 365)
        self.withdrawal_grace_period_hours = self.consent_config.get("withdrawal_grace_period_hours", 72)
        
        logger.info("Consent Manager initialized successfully")
    
    def _initialize_consent_purposes(self) -> None:
        """Initialize predefined consent purposes."""        default_purposes = [
            ConsentPurpose(
                purpose_id="essential_services",
                name="Essential Services",
                description="Core platform functionality and user account management",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS, DataCategory.CONTACT_INFORMATION],
                legal_basis="contract",
                retention_period_days=None,  # Retained while account active
                third_parties=[],
                required=True
            ),
            ConsentPurpose(
                purpose_id="content_analytics",
                name="Content Analytics",
                description="Analysis of content performance and user engagement",
                data_categories=[DataCategory.BEHAVIORAL_DATA, DataCategory.USAGE_DATA],
                legal_basis="legitimate_interest",
                retention_period_days=730,  # 2 years
                third_parties=["analytics_provider"],
                required=False
            ),
            ConsentPurpose(
                purpose_id="personalized_recommendations",
                name="Personalized Recommendations",
                description="Providing personalized content and feature recommendations",
                data_categories=[DataCategory.PREFERENCES, DataCategory.BEHAVIORAL_DATA],
                legal_basis="consent",
                retention_period_days=365,
                third_parties=["recommendation_engine"],
                required=False
            ),
            ConsentPurpose(
                purpose_id="marketing_communications",
                name="Marketing Communications",
                description="Sending promotional content and platform updates",
                data_categories=[DataCategory.CONTACT_INFORMATION, DataCategory.PREFERENCES],
                legal_basis="consent",
                retention_period_days=1095,  # 3 years
                third_parties=["email_service"],
                required=False
            ),
            ConsentPurpose(
                purpose_id="monetization_tracking",
                name="Monetization Tracking",
                description="Tracking revenue generation and payment processing",
                data_categories=[DataCategory.FINANCIAL_DATA, DataCategory.USAGE_DATA],
                legal_basis="contract",
                retention_period_days=2555,  # 7 years for financial records
                third_parties=["payment_processor"],
                required=True
            )
        ]
        
        for purpose in default_purposes:
            self.consent_purposes[purpose.purpose_id] = purpose
        
        # Load custom purposes from config
        custom_purposes = self.consent_config.get("custom_purposes", [])
        for purpose_data in custom_purposes:
            purpose = ConsentPurpose(**purpose_data)
            self.consent_purposes[purpose.purpose_id] = purpose
    
    async def collect_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose_id: str,
        method: ConsentMethod,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        custom_expiry: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """        Collect and record user consent for a specific purpose.
        
        Args:
            user_id: ID of the user providing consent
            consent_type: Type of consent being collected
            purpose_id: ID of the consent purpose
            method: Method by which consent was obtained
            ip_address: IP address when consent was given
            user_agent: User agent when consent was given
            evidence: Additional evidence of consent
            custom_expiry: Custom expiry date (if not using default)
            
        Returns:
            Consent collection results
        """        try:
            if purpose_id not in self.consent_purposes:
                raise ValueError(f"Unknown consent purpose: {purpose_id}")
            
            purpose = self.consent_purposes[purpose_id]
            consent_id = f"consent_{uuid.uuid4().hex[:16]}"
            
            # Calculate expiry date
            expires_at = None
            if self.auto_expiry_enabled:
                if custom_expiry:
                    expires_at = custom_expiry
                elif purpose.retention_period_days:
                    expires_at = datetime.utcnow() + timedelta(days=purpose.retention_period_days)
                else:
                    expires_at = datetime.utcnow() + timedelta(days=self.default_expiry_days)
            
            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                consent_type=consent_type,
                purpose=purpose,
                status=ConsentStatus.GRANTED,
                method=method,
                granted_at=datetime.utcnow(),
                withdrawn_at=None,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
                evidence=evidence or {},
                metadata={
                    "collection_timestamp": datetime.utcnow().isoformat(),
                    "collection_method": method.value,
                    "purpose_version": "1.0"
                },
                version="1.0"
            )
            
            # Store consent record
            self.consent_records[consent_id] = consent_record
            
            # Update user consent tracking
            if user_id not in self.user_consents:
                self.user_consents[user_id] = []
            self.user_consents[user_id].append(consent_id)
            
            # Check for conflicts with existing consents
            conflicts = await self._check_consent_conflicts(user_id, purpose_id)
            
            result = {
                "consent_id": consent_id,
                "status": "granted",
                "granted_at": consent_record.granted_at.isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "purpose": {
                    "id": purpose.purpose_id,
                    "name": purpose.name,
                    "description": purpose.description
                },
                "conflicts_resolved": len(conflicts),
                "legal_basis": purpose.legal_basis,
                "data_categories": [cat.value for cat in purpose.data_categories]
            }
            
            logger.info(f"Consent collected: {consent_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error collecting consent: {str(e)}")
            raise
    
    async def withdraw_consent(
        self,
        user_id: str,
        consent_id: str,
        method: ConsentMethod,
        reason: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Process consent withdrawal request.
        
        Args:
            user_id: ID of the user withdrawing consent
            consent_id: ID of the consent to withdraw
            method: Method by which withdrawal was requested
            reason: Optional reason for withdrawal
            evidence: Additional evidence of withdrawal
            
        Returns:
            Withdrawal processing results
        """        try:
            if consent_id not in self.consent_records:
                raise ValueError(f"Consent record {consent_id} not found")
            
            consent = self.consent_records[consent_id]
            
            if consent.user_id != user_id:
                raise ValueError("User not authorized to withdraw this consent")
            
            if consent.status in [ConsentStatus.WITHDRAWN, ConsentStatus.REVOKED]:
                raise ValueError("Consent already withdrawn or revoked")
            
            withdrawal_id = f"withdrawal_{uuid.uuid4().hex[:16]}"
            
            # Create withdrawal record
            withdrawal = ConsentWithdrawal(
                withdrawal_id=withdrawal_id,
                consent_id=consent_id,
                user_id=user_id,
                requested_at=datetime.utcnow(),
                processed_at=None,
                method=method,
                reason=reason,
                status="pending",
                data_deletion_required=self._requires_data_deletion(consent),
                evidence=evidence or {}
            )
            
            # Process withdrawal immediately for most cases
            await self._process_withdrawal(withdrawal)
            
            # Update consent status
            consent.status = ConsentStatus.WITHDRAWN
            consent.withdrawn_at = datetime.utcnow()
            
            # Store withdrawal record
            self.consent_withdrawals[withdrawal_id] = withdrawal
            
            result = {
                "withdrawal_id": withdrawal_id,
                "consent_id": consent_id,
                "status": "processed",
                "withdrawn_at": consent.withdrawn_at.isoformat(),
                "data_deletion_required": withdrawal.data_deletion_required,
                "grace_period_ends": (
                    datetime.utcnow() + timedelta(hours=self.withdrawal_grace_period_hours)
                ).isoformat(),
                "purpose": {
                    "id": consent.purpose.purpose_id,
                    "name": consent.purpose.name
                }
            }
            
            logger.info(f"Consent withdrawn: {consent_id} by user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error withdrawing consent: {str(e)}")
            raise
    
    async def check_consent_status(
        self,
        user_id: str,
        purpose_id: Optional[str] = None,
        consent_type: Optional[ConsentType] = None
    ) -> Dict[str, Any]:
        """        Check current consent status for user and purpose.
        
        Args:
            user_id: ID of the user
            purpose_id: Optional specific purpose to check
            consent_type: Optional consent type to filter by
            
        Returns:
            Current consent status
        """        try:
            if user_id not in self.user_consents:
                return {
                    "user_id": user_id,
                    "overall_status": "no_consents",
                    "consents": [],
                    "expired_consents": [],
                    "missing_required": self._get_required_purposes()
                }
            
            user_consent_ids = self.user_consents[user_id]
            current_consents = []
            expired_consents = []
            
            for consent_id in user_consent_ids:
                if consent_id not in self.consent_records:
                    continue
                
                consent = self.consent_records[consent_id]
                
                # Apply filters
                if purpose_id and consent.purpose.purpose_id != purpose_id:
                    continue
                if consent_type and consent.consent_type != consent_type:
                    continue
                
                # Check expiry
                is_expired = self._is_consent_expired(consent)
                
                consent_info = {
                    "consent_id": consent_id,
                    "purpose_id": consent.purpose.purpose_id,
                    "purpose_name": consent.purpose.name,
                    "consent_type": consent.consent_type.value,
                    "status": consent.status.value,
                    "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                    "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                    "is_expired": is_expired,
                    "legal_basis": consent.purpose.legal_basis
                }
                
                if is_expired:
                    expired_consents.append(consent_info)
                else:
                    current_consents.append(consent_info)
            
            # Check for missing required consents
            missing_required = []
            for purpose in self.consent_purposes.values():
                if purpose.required:
                    has_valid_consent = any(
                        c["purpose_id"] == purpose.purpose_id and 
                        c["status"] == "granted" and 
                        not c["is_expired"]
                        for c in current_consents
                    )
                    if not has_valid_consent:
                        missing_required.append({
                            "purpose_id": purpose.purpose_id,
                            "purpose_name": purpose.name,
                            "description": purpose.description
                        })
            
            # Determine overall status
            overall_status = "compliant"
            if missing_required:
                overall_status = "missing_required"
            elif expired_consents:
                overall_status = "has_expired"
            elif not current_consents:
                overall_status = "no_valid_consents"
            
            return {
                "user_id": user_id,
                "overall_status": overall_status,
                "consents": current_consents,
                "expired_consents": expired_consents,
                "missing_required": missing_required,
                "compliance_score": self._calculate_compliance_score(
                    current_consents, missing_required
                )
            }
            
        except Exception as e:
            logger.error(f"Error checking consent status: {str(e)}")
            raise
    
    async def refresh_expired_consents(self, user_id: str) -> Dict[str, Any]:
        """        Identify and handle expired consents for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Refresh results
        """        try:
            if user_id not in self.user_consents:
                return {"user_id": user_id, "expired_consents": [], "actions_taken": []}
            
            expired_consents = []
            actions_taken = []
            
            for consent_id in self.user_consents[user_id]:
                if consent_id not in self.consent_records:
                    continue
                
                consent = self.consent_records[consent_id]
                
                if self._is_consent_expired(consent) and consent.status == ConsentStatus.GRANTED:
                    # Update status to expired
                    consent.status = ConsentStatus.EXPIRED
                    
                    expired_consents.append({
                        "consent_id": consent_id,
                        "purpose_id": consent.purpose.purpose_id,
                        "purpose_name": consent.purpose.name,
                        "expired_at": consent.expires_at.isoformat() if consent.expires_at else None
                    })
                    
                    actions_taken.append(f"Marked consent {consent_id} as expired")
                    
                    # Handle data retention based on purpose
                    if consent.purpose.retention_period_days:
                        actions_taken.append(f"Scheduled data review for purpose {consent.purpose.purpose_id}")
            
            return {
                "user_id": user_id,
                "expired_consents": expired_consents,
                "actions_taken": actions_taken,
                "refresh_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error refreshing expired consents: {str(e)}")
            raise
    
    async def generate_consent_report(
        self,
        user_id: Optional[str] = None,
        purpose_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """        Generate comprehensive consent report.
        
        Args:
            user_id: Optional user to report on
            purpose_id: Optional purpose to filter by
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            Comprehensive consent report
        """        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter consents based on criteria
            filtered_consents = []
            for consent in self.consent_records.values():
                # Apply filters
                if user_id and consent.user_id != user_id:
                    continue
                if purpose_id and consent.purpose.purpose_id != purpose_id:
                    continue
                if consent.granted_at and (consent.granted_at < start_date or consent.granted_at > end_date):
                    continue
                
                filtered_consents.append(consent)
            
            # Generate statistics
            stats = self._generate_consent_statistics(filtered_consents)
            
            # Compliance analysis
            compliance_analysis = self._analyze_compliance_trends(filtered_consents)
            
            # Purpose breakdown
            purpose_breakdown = self._analyze_purpose_distribution(filtered_consents)
            
            report = {
                "report_id": f"consent_report_{uuid.uuid4().hex[:12]}",
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "filters": {
                    "user_id": user_id,
                    "purpose_id": purpose_id
                },
                "summary": {
                    "total_consents": len(filtered_consents),
                    "active_consents": stats["active_count"],
                    "withdrawn_consents": stats["withdrawn_count"],
                    "expired_consents": stats["expired_count"],
                    "unique_users": stats["unique_users"]
                },
                "statistics": stats,
                "compliance_analysis": compliance_analysis,
                "purpose_breakdown": purpose_breakdown,
                "recommendations": self._generate_consent_recommendations(stats, compliance_analysis)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating consent report: {str(e)}")
            raise
    
    async def export_user_consents(self, user_id: str) -> Dict[str, Any]:
        """        Export all consent data for a specific user (GDPR Article 20).
        
        Args:
            user_id: ID of the user
            
        Returns:
            Complete consent data export
        """        try:
            if user_id not in self.user_consents:
                return {
                    "user_id": user_id,
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "consents": [],
                    "withdrawals": []
                }
            
            # Export consent records
            user_consent_exports = []
            for consent_id in self.user_consents[user_id]:
                if consent_id in self.consent_records:
                    consent = self.consent_records[consent_id]
                    user_consent_exports.append({
                        "consent_id": consent_id,
                        "purpose": {
                            "id": consent.purpose.purpose_id,
                            "name": consent.purpose.name,
                            "description": consent.purpose.description,
                            "legal_basis": consent.purpose.legal_basis,
                            "data_categories": [cat.value for cat in consent.purpose.data_categories]
                        },
                        "consent_type": consent.consent_type.value,
                        "status": consent.status.value,
                        "method": consent.method.value,
                        "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                        "withdrawn_at": consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
                        "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                        "evidence": consent.evidence,
                        "version": consent.version
                    })
            
            # Export withdrawal records
            user_withdrawal_exports = []
            for withdrawal in self.consent_withdrawals.values():
                if withdrawal.user_id == user_id:
                    user_withdrawal_exports.append({
                        "withdrawal_id": withdrawal.withdrawal_id,
                        "consent_id": withdrawal.consent_id,
                        "requested_at": withdrawal.requested_at.isoformat(),
                        "processed_at": withdrawal.processed_at.isoformat() if withdrawal.processed_at else None,
                        "method": withdrawal.method.value,
                        "reason": withdrawal.reason,
                        "status": withdrawal.status,
                        "data_deletion_required": withdrawal.data_deletion_required
                    })
            
            export_data = {
                "user_id": user_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "data_controller": "IA Influencer Agent Platform",
                "consents": user_consent_exports,
                "withdrawals": user_withdrawal_exports,
                "export_format": "JSON",
                "data_protection_notice": "This export contains your complete consent history as processed by our platform."
            }
            
            logger.info(f"Consent data exported for user {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting user consents: {str(e)}")
            raise
    
    # Private helper methods
    async def _check_consent_conflicts(self, user_id: str, purpose_id: str) -> List[str]:
        """Check for and resolve consent conflicts."""        conflicts = []
        
        if user_id in self.user_consents:
            for consent_id in self.user_consents[user_id]:
                if consent_id in self.consent_records:
                    consent = self.consent_records[consent_id]
                    if (consent.purpose.purpose_id == purpose_id and 
                        consent.status == ConsentStatus.GRANTED):
                        # Mark previous consent as superseded
                        consent.status = ConsentStatus.REVOKED
                        conflicts.append(consent_id)
        
        return conflicts
    
    def _requires_data_deletion(self, consent: ConsentRecord) -> bool:
        """Determine if consent withdrawal requires data deletion."""        # Required if consent was the only legal basis for processing
        return consent.purpose.legal_basis == "consent"
    
    async def _process_withdrawal(self, withdrawal: ConsentWithdrawal) -> None:
        """Process withdrawal actions."""        withdrawal.processed_at = datetime.utcnow()
        withdrawal.status = "processed"
        
        # Trigger data deletion if required
        if withdrawal.data_deletion_required:
            # Would trigger data deletion process
            logger.info(f"Data deletion triggered for withdrawal {withdrawal.withdrawal_id}")
    
    def _is_consent_expired(self, consent: ConsentRecord) -> bool:
        """Check if consent has expired."""        if not consent.expires_at:
            return False
        return datetime.utcnow() > consent.expires_at
    
    def _get_required_purposes(self) -> List[Dict[str, str]]:
        """Get list of required consent purposes."""        return [
            {
                "purpose_id": purpose.purpose_id,
                "purpose_name": purpose.name,
                "description": purpose.description
            }
            for purpose in self.consent_purposes.values()
            if purpose.required
        ]
    
    def _calculate_compliance_score(
        self, 
        current_consents: List[Dict[str, Any]], 
        missing_required: List[Dict[str, Any]]
    ) -> float:
        """Calculate compliance score based on consent status."""        if not self.consent_purposes:
            return 1.0
        
        total_purposes = len(self.consent_purposes)
        valid_consents = len(current_consents)
        missing_count = len(missing_required)
        
        # Penalize missing required consents more heavily
        penalty = missing_count * 2 if missing_required else 0
        
        score = max(0.0, (valid_consents - penalty) / total_purposes)
        return min(1.0, score)
    
    def _generate_consent_statistics(self, consents: List[ConsentRecord]) -> Dict[str, Any]:
        """Generate statistical analysis of consents."""        if not consents:
            return {
                "active_count": 0,
                "withdrawn_count": 0,
                "expired_count": 0,
                "unique_users": 0,
                "avg_consent_lifetime_days": 0
            }
        
        active_count = len([c for c in consents if c.status == ConsentStatus.GRANTED])
        withdrawn_count = len([c for c in consents if c.status == ConsentStatus.WITHDRAWN])
        expired_count = len([c for c in consents if c.status == ConsentStatus.EXPIRED])
        
        unique_users = len(set(c.user_id for c in consents))
        
        # Calculate average consent lifetime
        completed_consents = [c for c in consents if c.withdrawn_at]
        if completed_consents:
            lifetimes = [
                (c.withdrawn_at - c.granted_at).days 
                for c in completed_consents 
                if c.granted_at and c.withdrawn_at
            ]
            avg_lifetime = sum(lifetimes) / len(lifetimes) if lifetimes else 0
        else:
            avg_lifetime = 0
        
        return {
            "active_count": active_count,
            "withdrawn_count": withdrawn_count,
            "expired_count": expired_count,
            "unique_users": unique_users,
            "avg_consent_lifetime_days": round(avg_lifetime, 2)
        }
    
    def _analyze_compliance_trends(self, consents: List[ConsentRecord]) -> Dict[str, Any]:
        """Analyze compliance trends over time."""        # Group consents by month
        monthly_data = {}
        for consent in consents:
            if consent.granted_at:
                month_key = consent.granted_at.strftime("%Y-%m")
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"granted": 0, "withdrawn": 0}
                monthly_data[month_key]["granted"] += 1
        
        # Add withdrawal data
        for consent in consents:
            if consent.withdrawn_at:
                month_key = consent.withdrawn_at.strftime("%Y-%m")
                if month_key in monthly_data:
                    monthly_data[month_key]["withdrawn"] += 1
        
        return {
            "monthly_trends": monthly_data,
            "total_months": len(monthly_data),
            "peak_consent_month": max(monthly_data.items(), key=lambda x: x[1]["granted"])[0] if monthly_data else None
        }
    
    def _analyze_purpose_distribution(self, consents: List[ConsentRecord]) -> Dict[str, Any]:
        """Analyze distribution of consents by purpose."""        purpose_stats = {}
        
        for consent in consents:
            purpose_id = consent.purpose.purpose_id
            if purpose_id not in purpose_stats:
                purpose_stats[purpose_id] = {
                    "purpose_name": consent.purpose.name,
                    "total_consents": 0,
                    "active_consents": 0,
                    "withdrawn_consents": 0
                }
            
            purpose_stats[purpose_id]["total_consents"] += 1
            if consent.status == ConsentStatus.GRANTED:
                purpose_stats[purpose_id]["active_consents"] += 1
            elif consent.status == ConsentStatus.WITHDRAWN:
                purpose_stats[purpose_id]["withdrawn_consents"] += 1
        
        return purpose_stats
    
    def _generate_consent_recommendations(
        self, 
        stats: Dict[str, Any], 
        compliance_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on consent analysis."""        recommendations = []
        
        withdrawal_rate = (stats["withdrawn_count"] / 
                          max(1, stats["active_count"] + stats["withdrawn_count"]))
        
        if withdrawal_rate > 0.2:  # 20% withdrawal rate
            recommendations.append("High withdrawal rate detected - review consent collection practices")
        
        if stats["expired_count"] > stats["active_count"]:
            recommendations.append("Many expired consents - implement proactive renewal process")
        
        if stats["avg_consent_lifetime_days"] < 30:
            recommendations.append("Short consent lifetime - review user experience and value proposition")
        
        return recommendations
