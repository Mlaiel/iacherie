"""Licensing Repository
import asyncio

==================

Professional data access layer for licensing management operations.
Handles CRUD operations, complex queries, and data validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal
import logging
from uuid import UUID

from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import (
    LicenseAgreement, RoyaltyCalculation, LicenseUsageTracking,
    PaymentRecord, ComplianceReport, RightsOwnership,
    ContractTerms, RevenueDistribution, LicenseStatus, PaymentStatus
)
from ..models.content_model import Content
from ...core.database import get_db_session
from ...core.exceptions import (
    DatabaseError, ValidationError, NotFoundError
)
from ...core.security import SecurityManager
from ...utils.validators import validate_uuid, validate_decimal
from ...utils.cache import CacheManager

logger = logging.getLogger(__name__)


class LicensingRepository:
    """
    Professional licensing data repository with advanced query capabilities,
    caching, security, and performance optimization.
    """
    
    def __init__(self, session -> None: Session = None, cache_manager -> None: CacheManager = None) -> None:
        """
Initialize repository with database session and cache"""
        self.session = session or get_db_session()
        self.cache_manager = cache_manager or CacheManager()
        self.security_manager = SecurityManager()
        self._logger = logger
    
    async def create_license_agreement(
        self,
        agreement_data: Dict[str, Any],
        user_id: UUID
    ) -> LicenseAgreement:
        """
Create new license agreement with validation"""
        try:
            # Validate input data
            validated_data = await self._validate_license_agreement_data(agreement_data)
            
            # Check user permissions
            await self.security_manager.verify_permission(
                user_id, "licensing.create_agreement"
            )
            
            # Create license agreement
            agreement = LicenseAgreement(
                license_number=await self._generate_license_number(),
                licensor_id=validated_data["licensor_id"],
                licensee_id=validated_data["licensee_id"],
                content_id=validated_data["content_id"],
                license_type=validated_data["license_type"],
                title=validated_data["title"],
                description=validated_data.get("description"),
                territory=validated_data.get("territory", "worldwide"),
                usage_rights=validated_data["usage_rights"],
                exclusivity=validated_data.get("exclusivity", False),
                license_fee=Decimal(str(validated_data.get("license_fee", 0))),
                royalty_rate=validated_data.get("royalty_rate", 0.0),
                minimum_guarantee=Decimal(str(validated_data.get("minimum_guarantee", 0))),
                advance_payment=Decimal(str(validated_data.get("advance_payment", 0))),
                currency=validated_data.get("currency", "USD"),
                start_date=validated_data["start_date"],
                end_date=validated_data.get("end_date"),
                auto_renewal=validated_data.get("auto_renewal", False),
                renewal_period_months=validated_data.get("renewal_period_months", 12),
                payment_schedule=validated_data.get("payment_schedule", "monthly"),
                payment_due_days=validated_data.get("payment_due_days", 30),
                content_restrictions=validated_data.get("content_restrictions"),
                geographical_restrictions=validated_data.get("geographical_restrictions"),
                platform_restrictions=validated_data.get("platform_restrictions"),
                governing_law=validated_data.get("governing_law"),
                jurisdiction=validated_data.get("jurisdiction"),
                custom_terms=validated_data.get("custom_terms"),
                created_by=user_id
            )
            
            self.session.add(agreement)
            await self.session.commit()
            await self.session.refresh(agreement)
            
            # Cache the new agreement
            cache_key = f"license_agreement:{agreement.id}"
            await self.cache_manager.set(cache_key, agreement, ttl=3600)
            
            self._logger.info(f"Created license agreement {agreement.license_number} by user {user_id}")
            return agreement
            
        except ValidationError:
            await self.session.rollback()
            raise
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Data integrity violation: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Database error creating license agreement: {str(e)}")
    
    async def get_license_agreement(
        self,
        agreement_id: UUID,
        user_id: UUID = None,
        include_relations: bool = False
    ) -> Optional[LicenseAgreement]:
        """Get license agreement by ID with caching"""
        try:
            # Check cache first
            cache_key = f"license_agreement:{agreement_id}"
            cached_agreement = await self.cache_manager.get(cache_key)
            if cached_agreement:
                return cached_agreement
            
            # Build query
            query = self.session.query(LicenseAgreement)
            
            if include_relations:
                query = query.options(
                    selectinload(LicenseAgreement.royalty_calculations),
                    selectinload(LicenseAgreement.usage_tracking),
                    selectinload(LicenseAgreement.payment_records),
                    selectinload(LicenseAgreement.compliance_reports)
                )
            
            agreement = query.filter(LicenseAgreement.id == agreement_id).first()
            
            if agreement and user_id:
                # Check user access permissions
                has_access = await self._check_agreement_access(agreement, user_id)
                if not has_access:
                    return None
            
            if agreement:
                # Cache the result
                await self.cache_manager.set(cache_key, agreement, ttl=3600)
            
            return agreement
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error retrieving license agreement: {str(e)}")
    
    async def update_license_agreement(
        self,
        agreement_id: UUID,
        update_data: Dict[str, Any],
        user_id: UUID
    ) -> LicenseAgreement:
        """Update license agreement with validation"""
        try:
            # Get existing agreement
            agreement = await self.get_license_agreement(agreement_id, user_id)
            if not agreement:
                raise NotFoundError(f"License agreement {agreement_id} not found")
            
            # Check permissions
            await self.security_manager.verify_permission(
                user_id, "licensing.update_agreement", agreement.id
            )
            
            # Validate update data
            validated_data = await self._validate_license_update_data(update_data, agreement)
            
            # Apply updates
            for field, value in validated_data.items():
                if hasattr(agreement, field):
                    if field in ["license_fee", "minimum_guarantee", "advance_payment"]:
                        setattr(agreement, field, Decimal(str(value)))
                    else:
                        setattr(agreement, field, value)
            
            agreement.last_modified_by = user_id
            agreement.updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(agreement)
            
            # Update cache
            cache_key = f"license_agreement:{agreement.id}"
            await self.cache_manager.set(cache_key, agreement, ttl=3600)
            
            self._logger.info(f"Updated license agreement {agreement.license_number} by user {user_id}")
            return agreement
            
        except (ValidationError, NotFoundError):
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Database error updating license agreement: {str(e)}")
    
    async def get_user_license_agreements(
        self,
        user_id: UUID,
        role: str = "all",  # licensor, licensee, all
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[LicenseAgreement], int]:
        """Get user's license agreements with pagination"""
        try:
            # Build query
            query = self.session.query(LicenseAgreement)
            
            # Apply role filter
            if role == "licensor":
                query = query.filter(LicenseAgreement.licensor_id == user_id)
            elif role == "licensee":
                query = query.filter(LicenseAgreement.licensee_id == user_id)
            else:
                query = query.filter(
                    or_(
                        LicenseAgreement.licensor_id == user_id,
                        LicenseAgreement.licensee_id == user_id
                    )
                )
            
            # Apply status filter
            if status:
                query = query.filter(LicenseAgreement.status == status)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination and ordering
            agreements = query.order_by(desc(LicenseAgreement.created_at))\
                            .limit(limit)\
                            .offset(offset)\
                            .all()
            
            return agreements, total_count
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error retrieving user agreements: {str(e)}")
    
    async def create_royalty_calculation(
        self,
        calculation_data: Dict[str, Any],
        user_id: UUID
    ) -> RoyaltyCalculation:
        """Create new royalty calculation"""
        try:
            # Validate input data
            validated_data = await self._validate_royalty_calculation_data(calculation_data)
            
            # Verify license agreement exists and user has access
            license_agreement = await self.get_license_agreement(
                validated_data["license_agreement_id"], user_id
            )
            if not license_agreement:
                raise NotFoundError("License agreement not found or access denied")
            
            # Create royalty calculation
            calculation = RoyaltyCalculation(
                calculation_id=await self._generate_calculation_id(),
                license_agreement_id=validated_data["license_agreement_id"],
                reporting_period_start=validated_data["reporting_period_start"],
                reporting_period_end=validated_data["reporting_period_end"],
                gross_revenue=Decimal(str(validated_data["gross_revenue"])),
                platform_fees=Decimal(str(validated_data.get("platform_fees", 0))),
                taxes=Decimal(str(validated_data.get("taxes", 0))),
                other_deductions=Decimal(str(validated_data.get("other_deductions", 0))),
                net_revenue=Decimal(str(validated_data["net_revenue"])),
                royalty_rate=validated_data["royalty_rate"],
                royalty_amount=Decimal(str(validated_data["royalty_amount"])),
                advance_balance=Decimal(str(validated_data.get("advance_balance", 0))),
                amount_due=Decimal(str(validated_data["amount_due"])),
                total_plays=validated_data.get("total_plays", 0),
                total_streams=validated_data.get("total_streams", 0),
                total_downloads=validated_data.get("total_downloads", 0),
                unique_users=validated_data.get("unique_users", 0),
                revenue_by_territory=validated_data.get("revenue_by_territory"),
                usage_by_territory=validated_data.get("usage_by_territory"),
                revenue_by_platform=validated_data.get("revenue_by_platform"),
                usage_by_platform=validated_data.get("usage_by_platform"),
                currency=validated_data.get("currency", "USD"),
                exchange_rate=validated_data.get("exchange_rate", 1.0),
                calculation_method=validated_data.get("calculation_method"),
                calculated_by=user_id
            )
            
            self.session.add(calculation)
            await self.session.commit()
            await self.session.refresh(calculation)
            
            self._logger.info(f"Created royalty calculation {calculation.calculation_id} by user {user_id}")
            return calculation
            
        except (ValidationError, NotFoundError):
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Database error creating royalty calculation: {str(e)}")
    
    async def get_royalty_calculations(
        self,
        license_agreement_id: UUID = None,
        user_id: UUID = None,
        period_start: date = None,
        period_end: date = None,
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[RoyaltyCalculation], int]:
        """Get royalty calculations with filtering"""
        try:
            # Build query
            query = self.session.query(RoyaltyCalculation)
            
            # Apply filters
            if license_agreement_id:
                query = query.filter(RoyaltyCalculation.license_agreement_id == license_agreement_id)
            
            if user_id:
                # Join with license agreements to filter by user
                query = query.join(LicenseAgreement).filter(
                    or_(
                        LicenseAgreement.licensor_id == user_id,
                        LicenseAgreement.licensee_id == user_id
                    )
                )
            
            if period_start:
                query = query.filter(RoyaltyCalculation.reporting_period_start >= period_start)
            
            if period_end:
                query = query.filter(RoyaltyCalculation.reporting_period_end <= period_end)
            
            if status:
                query = query.filter(RoyaltyCalculation.payment_status == status)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination and ordering
            calculations = query.order_by(desc(RoyaltyCalculation.calculation_date))\
                               .limit(limit)\
                               .offset(offset)\
                               .all()
            
            return calculations, total_count
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error retrieving royalty calculations: {str(e)}")
    
    async def create_usage_tracking_record(
        self,
        tracking_data: Dict[str, Any],
        user_id: UUID = None
    ) -> LicenseUsageTracking:
        """Create usage tracking record"""
        try:
            # Validate input data
            validated_data = await self._validate_usage_tracking_data(tracking_data)
            
            # Create usage tracking record
            tracking_record = LicenseUsageTracking(
                tracking_id=await self._generate_tracking_id(),
                license_agreement_id=validated_data["license_agreement_id"],
                usage_date=validated_data.get("usage_date", datetime.utcnow()),
                usage_type=validated_data["usage_type"],
                platform=validated_data.get("platform"),
                territory=validated_data.get("territory"),
                play_count=validated_data.get("play_count", 0),
                stream_count=validated_data.get("stream_count", 0),
                download_count=validated_data.get("download_count", 0),
                view_count=validated_data.get("view_count", 0),
                impression_count=validated_data.get("impression_count", 0),
                click_count=validated_data.get("click_count", 0),
                share_count=validated_data.get("share_count", 0),
                total_play_duration=validated_data.get("total_play_duration", 0),
                average_play_duration=validated_data.get("average_play_duration", 0),
                completion_rate=validated_data.get("completion_rate", 0.0),
                revenue_generated=Decimal(str(validated_data.get("revenue_generated", 0))),
                revenue_currency=validated_data.get("revenue_currency", "USD"),
                age_group_breakdown=validated_data.get("age_group_breakdown"),
                gender_breakdown=validated_data.get("gender_breakdown"),
                device_breakdown=validated_data.get("device_breakdown"),
                ip_address=validated_data.get("ip_address"),
                user_agent=validated_data.get("user_agent"),
                referrer_url=validated_data.get("referrer_url"),
                session_id=validated_data.get("session_id"),
                custom_metadata=validated_data.get("custom_metadata"),
                tracking_source=validated_data.get("tracking_source")
            )
            
            self.session.add(tracking_record)
            await self.session.commit()
            await self.session.refresh(tracking_record)
            
            return tracking_record
            
        except ValidationError:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Database error creating usage tracking record: {str(e)}")
    
    async def get_license_usage_analytics(
        self,
        license_agreement_id: UUID,
        user_id: UUID,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Get comprehensive usage analytics for a license"""
        try:
            # Verify user has access to this license
            license_agreement = await self.get_license_agreement(license_agreement_id, user_id)
            if not license_agreement:
                raise NotFoundError("License agreement not found or access denied")
            
            # Build base query
            query = self.session.query(LicenseUsageTracking)\
                       .filter(LicenseUsageTracking.license_agreement_id == license_agreement_id)
            
            if start_date:
                query = query.filter(LicenseUsageTracking.usage_date >= start_date)
            if end_date:
                query = query.filter(LicenseUsageTracking.usage_date <= end_date)
            
            # Get aggregated metrics
            metrics = query.with_entities(
                func.sum(LicenseUsageTracking.play_count).label('total_plays'),
                func.sum(LicenseUsageTracking.stream_count).label('total_streams'),
                func.sum(LicenseUsageTracking.download_count).label('total_downloads'),
                func.sum(LicenseUsageTracking.view_count).label('total_views'),
                func.sum(LicenseUsageTracking.revenue_generated).label('total_revenue'),
                func.avg(LicenseUsageTracking.completion_rate).label('avg_completion_rate'),
                func.count(LicenseUsageTracking.id).label('total_sessions')
            ).first()
            
            # Get platform breakdown
            platform_breakdown = self.session.query(
                LicenseUsageTracking.platform,
                func.sum(LicenseUsageTracking.play_count).label('plays'),
                func.sum(LicenseUsageTracking.revenue_generated).label('revenue')
            ).filter(
                LicenseUsageTracking.license_agreement_id == license_agreement_id
            ).group_by(LicenseUsageTracking.platform).all()
            
            # Get territory breakdown
            territory_breakdown = self.session.query(
                LicenseUsageTracking.territory,
                func.sum(LicenseUsageTracking.play_count).label('plays'),
                func.sum(LicenseUsageTracking.revenue_generated).label('revenue')
            ).filter(
                LicenseUsageTracking.license_agreement_id == license_agreement_id
            ).group_by(LicenseUsageTracking.territory).all()
            
            return {
                'summary': {
                    'total_plays': int(metrics.total_plays or 0),
                    'total_streams': int(metrics.total_streams or 0),
                    'total_downloads': int(metrics.total_downloads or 0),
                    'total_views': int(metrics.total_views or 0),
                    'total_revenue': float(metrics.total_revenue or 0),
                    'average_completion_rate': float(metrics.avg_completion_rate or 0),
                    'total_sessions': int(metrics.total_sessions or 0)
                },
                'platform_breakdown': [
                    {
                        'platform': row.platform,
                        'plays': int(row.plays or 0),
                        'revenue': float(row.revenue or 0)
                    }
                    for row in platform_breakdown
                ],
                'territory_breakdown': [
                    {
                        'territory': row.territory,
                        'plays': int(row.plays or 0),
                        'revenue': float(row.revenue or 0)
                    }
                    for row in territory_breakdown
                ]
            }
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error retrieving usage analytics: {str(e)}")
    
    # Private helper methods
    
    async def _validate_license_agreement_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate license agreement data"""
        required_fields = [
            "licensor_id", "licensee_id", "content_id", 
            "license_type", "title", "usage_rights", "start_date"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate UUIDs
        for uuid_field in ["licensor_id", "licensee_id", "content_id"]:
            validate_uuid(data[uuid_field])
        
        # Validate financial fields
        for decimal_field in ["license_fee", "minimum_guarantee", "advance_payment"]:
            if decimal_field in data:
                validate_decimal(data[decimal_field])
        
        return data
    
    async def _validate_license_update_data(self, data: Dict[str, Any], agreement: LicenseAgreement) -> Dict[str, Any]:
        """Validate license agreement update data"""
        # Prevent updating immutable fields
        immutable_fields = ["id", "license_number", "licensor_id", "licensee_id", "content_id", "created_at"]
        
        for field in immutable_fields:
            if field in data:
                raise ValidationError(f"Field '{field}' is immutable and cannot be updated")
        
        # Validate status transitions
        if "status" in data:
            current_status = agreement.status
            new_status = data["status"]
            
            if not await self._is_valid_status_transition(current_status, new_status):
                raise ValidationError(f"Invalid status transition from {current_status} to {new_status}")
        
        return data
    
    async def _validate_royalty_calculation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate royalty calculation data"""
        required_fields = [
            "license_agreement_id", "reporting_period_start", "reporting_period_end",
            "gross_revenue", "net_revenue", "royalty_rate", "royalty_amount", "amount_due"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate UUID
        validate_uuid(data["license_agreement_id"])
        
        # Validate financial fields
        for decimal_field in ["gross_revenue", "net_revenue", "royalty_amount", "amount_due"]:
            validate_decimal(data[decimal_field])
        
        return data
    
    async def _validate_usage_tracking_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate usage tracking data"""
        required_fields = ["license_agreement_id", "usage_type"]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate UUID
        validate_uuid(data["license_agreement_id"])
        
        return data
    
    async def _check_agreement_access(self, agreement: LicenseAgreement, user_id: UUID) -> bool:
        """Check if user has access to license agreement"""
        return (
            str(agreement.licensor_id) == str(user_id) or 
            str(agreement.licensee_id) == str(user_id) or
            await self.security_manager.has_permission(user_id, "licensing.view_all_agreements")
        )
    
    async def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            "draft": ["pending", "active"],
            "pending": ["active", "suspended", "terminated"],
            "active": ["suspended", "expired", "terminated"],
            "suspended": ["active", "terminated"],
            "expired": ["terminated"],
            "terminated": []  # Terminal state
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    async def _generate_license_number(self) -> str:
        """Generate unique license number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        count = await self.session.query(func.count(LicenseAgreement.id)).scalar()
        return f"LIC-{timestamp}-{count + 1:06d}"
    
    async def _generate_calculation_id(self) -> str:
        """Generate unique calculation ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        count = await self.session.query(func.count(RoyaltyCalculation.id)).scalar()
        return f"CALC-{timestamp}-{count + 1:06d}"
    
    async def _generate_tracking_id(self) -> str:
        """Generate unique tracking ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        count = await self.session.query(func.count(LicenseUsageTracking.id)).scalar()
        return f"TRACK-{timestamp}-{count + 1:06d}"
