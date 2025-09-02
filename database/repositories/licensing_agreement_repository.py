"""Licensing Agreement Repository Module

Enterprise-grade repository for licensing agreement management with automated
contract generation, compliance tracking, and revenue sharing calculations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from ..models.licensing_agreements import (
    LicensingAgreement,
    LicenseType,
    LicenseStatus,
    UsageRight,
    RevenueModel,
    TerritoryScope,
    ComplianceStatus,
    RenewalStatus
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class LicensingAgreementRepository(BaseRepository[LicensingAgreement]):
    """
    Repository for licensing agreement operations with comprehensive contract management,
    automated compliance monitoring, and intelligent revenue distribution.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize licensing agreement repository"""
        super().__init__(db_session, LicensingAgreement)
        
    def create_agreement(self,
                        licensor_id: int,
                        licensee_id: int,
                        content_id: int,
                        license_type: LicenseType,
                        usage_rights: List[UsageRight],
                        revenue_model: RevenueModel,
                        revenue_share_percentage: Decimal,
                        territory_scope: TerritoryScope,
                        start_date: datetime,
                        end_date: Optional[datetime] = None,
                        terms_and_conditions: Optional[str] = None,
                        restrictions: Optional[Dict[str, Any]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> LicensingAgreement:
        """
        Create licensing agreement with validation and compliance checks
        
        Args:
            licensor_id: Content owner user ID
            licensee_id: License holder user ID
            content_id: Content being licensed
            license_type: Type of license
            usage_rights: List of granted usage rights
            revenue_model: Revenue sharing model
            revenue_share_percentage: Percentage for licensee
            territory_scope: Geographic scope
            start_date: Agreement start date
            end_date: Agreement end date (None for perpetual)
            terms_and_conditions: Full terms text
            restrictions: Usage restrictions
            metadata: Additional metadata
            
        Returns:
            Created LicensingAgreement instance
        """
        try:
            # Validate revenue share percentage
            if not (0 <= revenue_share_percentage <= 100):
                raise RepositoryException("Revenue share percentage must be between 0 and 100")
            
            # Validate dates
            if end_date and end_date <= start_date:
                raise RepositoryException("End date must be after start date")
            
            # Check for conflicting agreements
            conflicting_agreement = self._check_conflicting_agreements(
                content_id, start_date, end_date, usage_rights
            )
            if conflicting_agreement:
                raise RepositoryException(
                    f"Conflicting agreement exists: {conflicting_agreement.agreement_id}"
                )
            
            # Generate agreement ID and reference
            agreement_id = str(uuid.uuid4())
            agreement_reference = self._generate_agreement_reference(license_type, start_date)
            
            agreement_data = {
                'licensor_id': licensor_id,
                'licensee_id': licensee_id,
                'content_id': content_id,
                'license_type': license_type,
                'usage_rights': usage_rights,
                'revenue_model': revenue_model,
                'revenue_share_percentage': revenue_share_percentage,
                'territory_scope': territory_scope,
                'start_date': start_date,
                'end_date': end_date,
                'terms_and_conditions': terms_and_conditions,
                'restrictions': restrictions or {},
                'status': LicenseStatus.PENDING,
                'compliance_status': ComplianceStatus.COMPLIANT,
                'renewal_status': RenewalStatus.NOT_APPLICABLE if end_date is None else RenewalStatus.PENDING,
                'agreement_id': agreement_id,
                'agreement_reference': agreement_reference,
                'metadata': metadata or {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            agreement = self.create(**agreement_data)
            
            self.logger.info(
                f"Created {license_type.value} agreement {agreement_reference} between users {licensor_id} and {licensee_id}"
            )
            
            return agreement
            
        except Exception as e:
            self.logger.error(f"Failed to create licensing agreement: {str(e)}")
            raise RepositoryException(f"Agreement creation failed: {str(e)}")
            
    def _check_conflicting_agreements(self,
                                    content_id: int,
                                    start_date: datetime,
                                    end_date: Optional[datetime],
                                    usage_rights: List[UsageRight]) -> Optional[LicensingAgreement]:
        """
        Check for conflicting licensing agreements
        
        Args:
            content_id: Content ID
            start_date: Agreement start date
            end_date: Agreement end date
            usage_rights: Usage rights being granted
            
        Returns:
            Conflicting agreement if found, None otherwise
        """
        try:
            # Build date overlap condition
            if end_date:
                date_overlap = and_(
                    LicensingAgreement.start_date <= end_date,
                    or_(
                        LicensingAgreement.end_date.is_(None),
                        LicensingAgreement.end_date >= start_date
                    )
                )
            else:
                date_overlap = or_(
                    LicensingAgreement.end_date.is_(None),
                    LicensingAgreement.end_date >= start_date
                )
            
            # Find potentially conflicting agreements
            existing_agreements = self.db_session.query(LicensingAgreement).filter(
                and_(
                    LicensingAgreement.content_id == content_id,
                    LicensingAgreement.status.in_([
                        LicenseStatus.ACTIVE,
                        LicenseStatus.PENDING
                    ]),
                    date_overlap
                )
            ).all()
            
            # Check for actual conflicts (overlapping usage rights)
            for agreement in existing_agreements:
                if self._rights_conflict(agreement.usage_rights, usage_rights):
                    return agreement
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to check conflicting agreements: {str(e)}")
            return None
            
    def _rights_conflict(self,
                        existing_rights: List[UsageRight],
                        new_rights: List[UsageRight]) -> bool:
        """
        Check if usage rights conflict
        
        Args:
            existing_rights: Existing usage rights
            new_rights: New usage rights
            
        Returns:
            True if rights conflict, False otherwise
        """
        # Exclusive rights that cannot overlap
        exclusive_rights = {
            UsageRight.EXCLUSIVE_DISTRIBUTION,
            UsageRight.EXCLUSIVE_COMMERCIAL,
            UsageRight.MASTER_RIGHTS
        }
        
        existing_set = set(existing_rights)
        new_set = set(new_rights)
        
        # Check for exclusive rights conflicts
        if existing_set & exclusive_rights and new_set & exclusive_rights:
            return True
        
        # Check for commercial rights conflicts
        commercial_rights = {
            UsageRight.COMMERCIAL_USE,
            UsageRight.EXCLUSIVE_COMMERCIAL,
            UsageRight.MONETIZATION_RIGHTS
        }
        
        if (existing_set & commercial_rights and 
            new_set & commercial_rights and
            UsageRight.EXCLUSIVE_COMMERCIAL in (existing_set | new_set)):
            return True
        
        return False
        
    def _generate_agreement_reference(self,
                                    license_type: LicenseType,
                                    start_date: datetime) -> str:
        """
        Generate unique agreement reference
        
        Args:
            license_type: License type
            start_date: Agreement start date
            
        Returns:
            Agreement reference string
        """
        type_code = license_type.value[:3].upper()
        date_code = start_date.strftime("%Y%m")
        sequence = self.db_session.query(func.count(LicensingAgreement.id)).filter(
            func.extract('year', LicensingAgreement.created_at) == start_date.year,
            func.extract('month', LicensingAgreement.created_at) == start_date.month
        ).scalar() + 1
        
        return f"{type_code}-{date_code}-{sequence:04d}"
        
    def get_user_agreements(self,
                          user_id: int,
                          role: str = 'both',  # 'licensor', 'licensee', 'both'
                          status: Optional[LicenseStatus] = None,
                          license_type: Optional[LicenseType] = None,
                          active_only: bool = False) -> List[LicensingAgreement]:
        """
        Get agreements for a user in different roles
        
        Args:
            user_id: User ID
            role: User role filter ('licensor', 'licensee', 'both')
            status: Optional status filter
            license_type: Optional license type filter
            active_only: Whether to return only active agreements
            
        Returns:
            List of LicensingAgreement instances
        """
        try:
            query = self.db_session.query(LicensingAgreement)
            
            # Apply role filter
            if role == 'licensor':
                query = query.filter(LicensingAgreement.licensor_id == user_id)
            elif role == 'licensee':
                query = query.filter(LicensingAgreement.licensee_id == user_id)
            else:  # both
                query = query.filter(
                    or_(
                        LicensingAgreement.licensor_id == user_id,
                        LicensingAgreement.licensee_id == user_id
                    )
                )
            
            # Apply other filters
            if status:
                query = query.filter(LicensingAgreement.status == status)
            if license_type:
                query = query.filter(LicensingAgreement.license_type == license_type)
            if active_only:
                current_time = datetime.utcnow()
                query = query.filter(
                    and_(
                        LicensingAgreement.status == LicenseStatus.ACTIVE,
                        LicensingAgreement.start_date <= current_time,
                        or_(
                            LicensingAgreement.end_date.is_(None),
                            LicensingAgreement.end_date >= current_time
                        )
                    )
                )
            
            query = query.order_by(LicensingAgreement.created_at.desc())
            
            agreements = query.all()
            
            self.logger.debug(
                f"Retrieved {len(agreements)} agreements for user {user_id} as {role}"
            )
            
            return agreements
            
        except Exception as e:
            self.logger.error(f"Failed to get user agreements: {str(e)}")
            return []
            
    def get_content_agreements(self, content_id: int) -> List[LicensingAgreement]:
        """
        Get all agreements for a specific content
        
        Args:
            content_id: Content ID
            
        Returns:
            List of LicensingAgreement instances
        """
        try:
            agreements = self.db_session.query(LicensingAgreement).filter(
                LicensingAgreement.content_id == content_id
            ).order_by(LicensingAgreement.created_at.desc()).all()
            
            self.logger.debug(f"Retrieved {len(agreements)} agreements for content {content_id}")
            
            return agreements
            
        except Exception as e:
            self.logger.error(f"Failed to get content agreements: {str(e)}")
            return []
            
    def update_agreement_status(self,
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
    def check_expiring_agreements(self, days_ahead: int = 30) -> List[LicensingAgreement]:
        """
        Get agreements expiring within specified days
        
        Args:
            days_ahead: Number of days ahead to check
            
        Returns:
            List of expiring agreements
        """
        try:
            expiry_threshold = datetime.utcnow() + timedelta(days=days_ahead)
            
            expiring_agreements = self.db_session.query(LicensingAgreement).filter(
                and_(
                    LicensingAgreement.status == LicenseStatus.ACTIVE,
                    LicensingAgreement.end_date.isnot(None),
                    LicensingAgreement.end_date <= expiry_threshold,
                    LicensingAgreement.end_date > datetime.utcnow()
                )
            ).order_by(LicensingAgreement.end_date.asc()).all()
            
            self.logger.debug(
                f"Found {len(expiring_agreements)} agreements expiring in {days_ahead} days"
            )
            
            return expiring_agreements
            
        except Exception as e:
            self.logger.error(f"Failed to check expiring agreements: {str(e)}")
            return []
            
    def calculate_revenue_distribution(self,
                                     agreement_id: int,
                                     total_revenue: Decimal) -> Dict[str, Any]:
        """
        Calculate revenue distribution based on agreement terms
        
        Args:
            agreement_id: Agreement ID
            total_revenue: Total revenue to distribute
            
        Returns:
            Revenue distribution breakdown
        """
        try:
            agreement = self.get_by_id(agreement_id)
            if not agreement:
                raise RepositoryException(f"Agreement {agreement_id} not found")
            
            if agreement.status != LicenseStatus.ACTIVE:
                raise RepositoryException(f"Agreement {agreement_id} is not active")
            
            # Calculate shares based on revenue model
            licensee_percentage = agreement.revenue_share_percentage
            licensor_percentage = Decimal('100.00') - licensee_percentage
            
            licensee_share = (total_revenue * licensee_percentage) / Decimal('100.00')
            licensor_share = total_revenue - licensee_share
            
            # Apply any additional fees or deductions
            platform_fee_percentage = Decimal('2.50')  # Platform fee
            platform_fee = (total_revenue * platform_fee_percentage) / Decimal('100.00')
            
            # Adjust shares for platform fee
            net_revenue = total_revenue - platform_fee
            licensee_final = (net_revenue * licensee_percentage) / Decimal('100.00')
            licensor_final = net_revenue - licensee_final
            
            distribution = {
                'agreement_id': agreement_id,
                'agreement_reference': agreement.agreement_reference,
                'total_revenue': float(total_revenue),
                'platform_fee': float(platform_fee),
                'net_revenue': float(net_revenue),
                'revenue_shares': {
                    'licensor': {
                        'user_id': agreement.licensor_id,
                        'percentage': float(licensor_percentage),
                        'amount': float(licensor_final)
                    },
                    'licensee': {
                        'user_id': agreement.licensee_id,
                        'percentage': float(licensee_percentage),
                        'amount': float(licensee_final)
                    }
                },
                'revenue_model': agreement.revenue_model.value,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Failed to calculate revenue distribution: {str(e)}")
            raise RepositoryException(f"Revenue calculation failed: {str(e)}")
            
    def get_agreement_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive agreement statistics
        
        Args:
            user_id: Optional user ID to filter statistics
            
        Returns:
            Dictionary containing agreement statistics
        """
        try:
            base_query = self.db_session.query(LicensingAgreement)
            
            if user_id:
                base_query = base_query.filter(
                    or_(
                        LicensingAgreement.licensor_id == user_id,
                        LicensingAgreement.licensee_id == user_id
                    )
                )
            
            # Total counts
            total_agreements = base_query.count()
            active_agreements = base_query.filter(
                LicensingAgreement.status == LicenseStatus.ACTIVE
            ).count()
            
            # Status distribution
            status_stats = {}
            for status in LicenseStatus:
                count = base_query.filter(LicensingAgreement.status == status).count()
                status_stats[status.value] = count
            
            # License type distribution
            type_stats = {}
            for license_type in LicenseType:
                count = base_query.filter(LicensingAgreement.license_type == license_type).count()
                type_stats[license_type.value] = count
            
            # Revenue model distribution
            revenue_model_stats = {}
            for model in RevenueModel:
                count = base_query.filter(LicensingAgreement.revenue_model == model).count()
                revenue_model_stats[model.value] = count
            
            # Territory distribution
            territory_stats = {}
            for territory in TerritoryScope:
                count = base_query.filter(LicensingAgreement.territory_scope == territory).count()
                territory_stats[territory.value] = count
            
            # Recent activity
            recent_agreements = base_query.filter(
                LicensingAgreement.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Expiring soon
            expiring_soon = len(self.check_expiring_agreements(days_ahead=30))
            
            # Average revenue share
            avg_revenue_share = base_query.with_entities(
                func.avg(LicensingAgreement.revenue_share_percentage)
            ).scalar() or 0
            
            statistics = {
                'total_agreements': total_agreements,
                'active_agreements': active_agreements,
                'status_distribution': status_stats,
                'license_type_distribution': type_stats,
                'revenue_model_distribution': revenue_model_stats,
                'territory_distribution': territory_stats,
                'recent_activity': {
                    'created_last_30_days': recent_agreements,
                    'expiring_next_30_days': expiring_soon
                },
                'metrics': {
                    'average_revenue_share_percentage': round(float(avg_revenue_share), 2)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get agreement statistics: {str(e)}")
            return {'error': str(e)}
            
    def process_automatic_renewals(self) -> List[Dict[str, Any]]:
        """
        Process automatic renewals for eligible agreements
        
        Returns:
            List of renewal processing results
        """
        try:
            # Find agreements eligible for automatic renewal
            renewal_candidates = self.db_session.query(LicensingAgreement).filter(
                and_(
                    LicensingAgreement.status == LicenseStatus.ACTIVE,
                    LicensingAgreement.renewal_status == RenewalStatus.AUTO_RENEWAL,
                    LicensingAgreement.end_date.isnot(None),
                    LicensingAgreement.end_date <= datetime.utcnow() + timedelta(days=7)  # 7 days before expiry
                )
            ).all()
            
            renewal_results = []
            
            for agreement in renewal_candidates:
                try:
                    # Calculate new end date (extend by original duration)
                    original_duration = agreement.end_date - agreement.start_date
                    new_end_date = agreement.end_date + original_duration
                    
                    # Update agreement
                    update_data = {
                        'end_date': new_end_date,
                        'renewal_status': RenewalStatus.RENEWED,
                        'updated_at': datetime.utcnow()
                    }
                    
                    # Update metadata with renewal history
                    metadata = agreement.metadata or {}
                    metadata['renewal_history'] = metadata.get('renewal_history', [])
                    metadata['renewal_history'].append({
                        'previous_end_date': agreement.end_date.isoformat(),
                        'new_end_date': new_end_date.isoformat(),
                        'renewal_date': datetime.utcnow().isoformat(),
                        'renewal_type': 'automatic'
                    })
                    
                    update_data['metadata'] = metadata
                    
                    self.update(agreement.id, **update_data)
                    
                    renewal_results.append({
                        'agreement_id': agreement.id,
                        'agreement_reference': agreement.agreement_reference,
                        'status': 'success',
                        'new_end_date': new_end_date.isoformat(),
                        'message': 'Agreement automatically renewed'
                    })
                    
                    self.logger.info(
                        f"Automatically renewed agreement {agreement.agreement_reference}"
                    )
                    
                except Exception as e:
                    renewal_results.append({
                        'agreement_id': agreement.id,
                        'agreement_reference': agreement.agreement_reference,
                        'status': 'failed',
                        'error': str(e),
                        'message': 'Automatic renewal failed'
                    })
                    
                    self.logger.error(
                        f"Failed to renew agreement {agreement.agreement_reference}: {str(e)}"
                    )
            
            return renewal_results
            
        except Exception as e:
            self.logger.error(f"Failed to process automatic renewals: {str(e)}")
            return [{'status': 'error', 'message': str(e)}]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
