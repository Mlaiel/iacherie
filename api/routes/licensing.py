"""Licensing API Routes
Advanced licensing and rights management endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import json

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monetization.licensing_manager import LicensingManager
from ...monetization.licensing_engine import LicensingEngine


# Enums
class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNCHRONIZATION = "synchronization"
    MASTER = "master"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    PRINT = "print"
    DIGITAL = "digital"


class LicenseStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class Territory(str, Enum):
    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"


# Pydantic models
class LicenseAgreement(BaseModel):
    license_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    licensee_name: str = Field(..., min_length=1, max_length=200)
    licensee_email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    licensee_company: Optional[str] = None
    license_type: LicenseType
    territory: Territory = Field(default=Territory.WORLDWIDE)
    duration_months: int = Field(..., gt=0, le=240)
    total_amount: Decimal = Field(..., gt=0)
    advance_amount: Decimal = Field(default=0, ge=0)
    royalty_rate: float = Field(..., ge=0, le=100)
    usage_rights: List[str] = Field(..., min_items=1)
    restrictions: List[str] = Field(default=[])
    payment_terms: Dict[str, Any]
    custom_terms: Optional[str] = None
    auto_renewal: bool = Field(default=False)


class LicenseTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    license_type: LicenseType
    default_territory: Territory
    default_duration_months: int = Field(default=12, gt=0, le=240)
    default_royalty_rate: float = Field(default=10.0, ge=0, le=100)
    standard_usage_rights: List[str]
    standard_restrictions: List[str]
    template_terms: str
    is_public: bool = Field(default=False)


class RoyaltyPayment(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_id: str
    period_start: datetime
    period_end: datetime
    units_sold: int = Field(..., ge=0)
    gross_revenue: Decimal = Field(..., ge=0)
    royalty_amount: Decimal = Field(..., ge=0)
    deductions: Optional[Dict[str, Decimal]] = None
    net_payment: Decimal = Field(..., ge=0)
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None


class LicenseReport(BaseModel):
    report_id: str
    license_id: str
    report_period: Dict[str, str]
    usage_data: Dict[str, Any]
    revenue_data: Dict[str, Any]
    compliance_status: str
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime


class UsageTracking(BaseModel):
    tracking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_id: str
    usage_date: datetime
    platform: str
    usage_type: str  # stream, download, broadcast, etc.
    quantity: int = Field(..., ge=1)
    revenue_generated: Optional[Decimal] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize licensing components
licensing_manager = LicensingManager()
licensing_engine = LicensingEngine()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/agreements", response_model=Dict[str, str])
async def create_license_agreement(
    agreement: LicenseAgreement,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create a new licensing agreement"""    try:
        # Verify content ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT content_id, metadata
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (agreement.content_id, user['user_id']))
            
            content_info = result.fetchone()
            if not content_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found or access denied"
                )
        
        # Validate licensing terms
        validation_result = await licensing_engine.validate_licensing_terms(agreement)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid licensing terms: {validation_result['errors']}"
            )
        
        # Calculate payment schedule
        payment_schedule = await licensing_engine.calculate_payment_schedule(
            agreement.total_amount, agreement.advance_amount, agreement.payment_terms
        )
        
        # Create license agreement
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO license_agreements (license_id, user_id, content_id, licensee_name,
                                              licensee_email, licensee_company, license_type,
                                              territory, duration_months, total_amount,
                                              advance_amount, royalty_rate, usage_rights,
                                              restrictions, payment_terms, payment_schedule,
                                              custom_terms, auto_renewal, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                agreement.license_id, user['user_id'], agreement.content_id,
                agreement.licensee_name, agreement.licensee_email, agreement.licensee_company,
                agreement.license_type.value, agreement.territory.value, agreement.duration_months,
                agreement.total_amount, agreement.advance_amount, agreement.royalty_rate,
                agreement.usage_rights, agreement.restrictions, agreement.payment_terms,
                payment_schedule, agreement.custom_terms, agreement.auto_renewal,
                LicenseStatus.DRAFT.value, datetime.utcnow()
            ))
            await session.commit()
        
        # Generate contract document
        background_tasks.add_task(
            _generate_license_contract, agreement.license_id, agreement, user
        )
        
        logger.info(f"License agreement created: {agreement.license_id} by user {user['user_id']}")
        
        return {
            "license_id": agreement.license_id,
            "status": "draft",
            "message": "License agreement created successfully",
            "contract_generation": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Create license agreement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create license agreement"
        )


@router.get("/agreements", response_model=List[Dict[str, Any]])
async def get_license_agreements(
    status: Optional[LicenseStatus] = None,
    license_type: Optional[LicenseType] = None,
    limit: int = Field(default=50, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get user's license agreements"""    try:
        query = """            SELECT la.license_id, la.content_id, la.licensee_name, la.licensee_email,
                   la.license_type, la.territory, la.duration_months, la.total_amount,
                   la.royalty_rate, la.status, la.created_at, la.expires_at,
                   uf.original_filename, uf.metadata
            FROM license_agreements la
            JOIN uploaded_files uf ON la.content_id = uf.file_id
            WHERE la.user_id = %s
        """        params = [user['user_id']]
        
        if status:
            query += " AND la.status = %s"
            params.append(status.value)
        
        if license_type:
            query += " AND la.license_type = %s"
            params.append(license_type.value)
            
        query += " ORDER BY la.created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            agreements = result.fetchall()
        
        agreement_list = []
        for agreement in agreements:
            agreement_list.append({
                "license_id": agreement[0],
                "content_id": agreement[1],
                "licensee_name": agreement[2],
                "licensee_email": agreement[3],
                "license_type": agreement[4],
                "territory": agreement[5],
                "duration_months": agreement[6],
                "total_amount": float(agreement[7]),
                "royalty_rate": agreement[8],
                "status": agreement[9],
                "created_at": agreement[10],
                "expires_at": agreement[11],
                "content_filename": agreement[12],
                "content_metadata": agreement[13]
            })
        
        return agreement_list
        
    except Exception as e:
        logger.error(f"Get license agreements failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get license agreements"
        )


@router.post("/templates", response_model=Dict[str, str])
async def create_license_template(
    template: LicenseTemplate,
    user: dict = Depends(get_current_user)
):
    """Create a license template"""    try:
        # Create license template
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO license_templates (template_id, user_id, name, description,
                                             license_type, default_territory, default_duration_months,
                                             default_royalty_rate, standard_usage_rights,
                                             standard_restrictions, template_terms, is_public,
                                             created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template.template_id, user['user_id'], template.name, template.description,
                template.license_type.value, template.default_territory.value,
                template.default_duration_months, template.default_royalty_rate,
                template.standard_usage_rights, template.standard_restrictions,
                template.template_terms, template.is_public, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"License template created: {template.template_id} by user {user['user_id']}")
        
        return {
            "template_id": template.template_id,
            "message": "License template created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create license template failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create license template"
        )


@router.post("/royalties", response_model=Dict[str, str])
async def record_royalty_payment(
    payment: RoyaltyPayment,
    user: dict = Depends(get_current_user)
):
    """Record a royalty payment"""    try:
        # Verify license ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT license_id, royalty_rate, status
                FROM license_agreements
                WHERE license_id = %s AND user_id = %s
            """, (payment.license_id, user['user_id']))
            
            license_info = result.fetchone()
            if not license_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="License not found or access denied"
                )
            
            if license_info[2] != LicenseStatus.ACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="License is not active"
                )
        
        # Validate royalty calculation
        expected_royalty = (payment.gross_revenue * Decimal(license_info[1]) / 100)
        if abs(payment.royalty_amount - expected_royalty) > Decimal('0.01'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Royalty amount does not match expected calculation"
            )
        
        # Record royalty payment
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO royalty_payments (payment_id, license_id, user_id, period_start,
                                            period_end, units_sold, gross_revenue, royalty_amount,
                                            deductions, net_payment, payment_date, payment_reference,
                                            created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                payment.payment_id, payment.license_id, user['user_id'], payment.period_start,
                payment.period_end, payment.units_sold, payment.gross_revenue,
                payment.royalty_amount, payment.deductions, payment.net_payment,
                payment.payment_date, payment.payment_reference, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Royalty payment recorded: {payment.payment_id}")
        
        return {
            "payment_id": payment.payment_id,
            "message": "Royalty payment recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Record royalty payment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record royalty payment"
        )


@router.post("/usage", response_model=Dict[str, str])
async def track_usage(
    usage: UsageTracking,
    user: dict = Depends(get_current_user)
):
    """Track content usage for licensing"""    try:
        # Verify license exists and is active
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT la.license_id, la.licensee_name
                FROM license_agreements la
                WHERE la.license_id = %s AND la.user_id = %s AND la.status = %s
            """, (usage.license_id, user['user_id'], LicenseStatus.ACTIVE.value))
            
            license_info = result.fetchone()
            if not license_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active license not found or access denied"
                )
        
        # Record usage tracking
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO usage_tracking (tracking_id, license_id, user_id, usage_date,
                                          platform, usage_type, quantity, revenue_generated,
                                          location, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                usage.tracking_id, usage.license_id, user['user_id'], usage.usage_date,
                usage.platform, usage.usage_type, usage.quantity, usage.revenue_generated,
                usage.location, usage.metadata, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Usage tracked: {usage.tracking_id} for license {usage.license_id}")
        
        return {
            "tracking_id": usage.tracking_id,
            "message": "Usage tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Track usage failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track usage"
        )


@router.get("/reports/{license_id}", response_model=LicenseReport)
async def generate_license_report(
    license_id: str,
    period_start: datetime,
    period_end: datetime,
    user: dict = Depends(get_current_user)
):
    """Generate license usage and compliance report"""    try:
        # Verify license ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT license_id, licensee_name, license_type, usage_rights, restrictions
                FROM license_agreements
                WHERE license_id = %s AND user_id = %s
            """, (license_id, user['user_id']))
            
            license_info = result.fetchone()
            if not license_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="License not found or access denied"
                )
        
        report_id = str(uuid.uuid4())
        
        # Gather usage data
        async with database_manager.get_postgres_session() as session:
            # Usage statistics
            result = await session.execute("""                SELECT platform, usage_type, SUM(quantity) as total_usage,
                       COALESCE(SUM(revenue_generated), 0) as total_revenue
                FROM usage_tracking
                WHERE license_id = %s AND usage_date >= %s AND usage_date <= %s
                GROUP BY platform, usage_type
            """, (license_id, period_start, period_end))
            
            usage_stats = [
                {
                    "platform": row[0],
                    "usage_type": row[1],
                    "total_usage": row[2],
                    "total_revenue": float(row[3])
                }
                for row in result.fetchall()
            ]
            
            # Revenue data
            result = await session.execute("""                SELECT SUM(gross_revenue) as total_gross,
                       SUM(royalty_amount) as total_royalties,
                       SUM(net_payment) as total_net
                FROM royalty_payments
                WHERE license_id = %s AND period_start >= %s AND period_end <= %s
            """, (license_id, period_start, period_end))
            
            revenue_data = result.fetchone()
        
        # Compliance analysis
        compliance_status, violations = await licensing_engine.analyze_compliance(
            license_id, license_info, usage_stats
        )
        
        # Generate recommendations
        recommendations = await licensing_engine.generate_recommendations(
            license_id, usage_stats, revenue_data, violations
        )
        
        report = LicenseReport(
            report_id=report_id,
            license_id=license_id,
            report_period={
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            usage_data={
                "total_usage": sum(stat['total_usage'] for stat in usage_stats),
                "platforms": list(set(stat['platform'] for stat in usage_stats)),
                "usage_breakdown": usage_stats
            },
            revenue_data={
                "total_gross_revenue": float(revenue_data[0] or 0),
                "total_royalties": float(revenue_data[1] or 0),
                "total_net_payment": float(revenue_data[2] or 0)
            },
            compliance_status=compliance_status,
            violations=violations,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
        
        # Store report
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO license_reports (report_id, license_id, user_id, report_data,
                                           period_start, period_end, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                report_id, license_id, user['user_id'], report.dict(),
                period_start, period_end, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"License report generated: {report_id}")
        
        return report
        
    except Exception as e:
        logger.error(f"Generate license report failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate license report"
        )


@router.put("/agreements/{license_id}/status", response_model=Dict[str, str])
async def update_license_status(
    license_id: str,
    new_status: LicenseStatus,
    reason: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Update license agreement status"""    try:
        async with database_manager.get_postgres_session() as session:
            # Verify ownership
            result = await session.execute("""                SELECT status FROM license_agreements
                WHERE license_id = %s AND user_id = %s
            """, (license_id, user['user_id']))
            
            current_status = result.fetchone()
            if not current_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="License not found or access denied"
                )
            
            # Validate status transition
            if not _validate_status_transition(current_status[0], new_status.value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status transition"
                )
            
            # Update status
            await session.execute("""                UPDATE license_agreements 
                SET status = %s, status_updated_at = %s, status_reason = %s
                WHERE license_id = %s
            """, (new_status.value, datetime.utcnow(), reason, license_id))
            
            # Log status change
            await session.execute("""                INSERT INTO license_status_history (license_id, old_status, new_status,
                                                   reason, changed_by, changed_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                license_id, current_status[0], new_status.value,
                reason, user['user_id'], datetime.utcnow()
            ))
            
            await session.commit()
        
        logger.info(f"License status updated: {license_id} to {new_status.value}")
        
        return {
            "license_id": license_id,
            "new_status": new_status.value,
            "message": "License status updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Update license status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update license status"
        )


@router.get("/analytics/dashboard", response_model=Dict[str, Any])
async def get_licensing_dashboard(
    days: int = Field(default=30, ge=1, le=365),
    user: dict = Depends(get_current_user)
):
    """Get licensing analytics dashboard"""    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        async with database_manager.get_postgres_session() as session:
            # Active licenses count
            result = await session.execute("""                SELECT COUNT(*) FROM license_agreements
                WHERE user_id = %s AND status = %s
            """, (user['user_id'], LicenseStatus.ACTIVE.value))
            active_licenses = result.fetchone()[0]
            
            # Total revenue
            result = await session.execute("""                SELECT COALESCE(SUM(net_payment), 0) FROM royalty_payments
                WHERE user_id = %s AND created_at >= %s
            """, (user['user_id'], start_date))
            total_revenue = float(result.fetchone()[0])
            
            # License types distribution
            result = await session.execute("""                SELECT license_type, COUNT(*) FROM license_agreements
                WHERE user_id = %s AND created_at >= %s
                GROUP BY license_type
            """, (user['user_id'], start_date))
            license_types = {row[0]: row[1] for row in result.fetchall()}
            
            # Territory distribution
            result = await session.execute("""                SELECT territory, COUNT(*) FROM license_agreements
                WHERE user_id = %s AND created_at >= %s
                GROUP BY territory
            """, (user['user_id'], start_date))
            territories = {row[0]: row[1] for row in result.fetchall()}
            
            # Recent activity
            result = await session.execute("""                SELECT la.license_id, la.licensee_name, la.license_type,
                       la.total_amount, la.created_at
                FROM license_agreements la
                WHERE la.user_id = %s
                ORDER BY la.created_at DESC
                LIMIT 10
            """, (user['user_id'],))
            recent_licenses = [
                {
                    "license_id": row[0],
                    "licensee_name": row[1],
                    "license_type": row[2],
                    "total_amount": float(row[3]),
                    "created_at": row[4]
                }
                for row in result.fetchall()
            ]
        
        dashboard_data = {
            "summary": {
                "active_licenses": active_licenses,
                "total_revenue": total_revenue,
                "period_days": days
            },
            "distributions": {
                "license_types": license_types,
                "territories": territories
            },
            "recent_activity": recent_licenses,
            "metrics": {
                "average_license_value": total_revenue / max(active_licenses, 1),
                "revenue_per_day": total_revenue / days
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Get licensing dashboard failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get licensing dashboard"
        )


@router.delete("/agreements/{license_id}")
async def delete_license_agreement(
    license_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a license agreement (only if draft status)"""    try:
        async with database_manager.get_postgres_session() as session:
            # Check status
            result = await session.execute("""                SELECT status FROM license_agreements
                WHERE license_id = %s AND user_id = %s
            """, (license_id, user['user_id']))
            
            license_status = result.fetchone()
            if not license_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="License not found or access denied"
                )
            
            if license_status[0] != LicenseStatus.DRAFT.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only draft licenses can be deleted"
                )
            
            # Delete license
            await session.execute("""                DELETE FROM license_agreements WHERE license_id = %s
            """, (license_id,))
            await session.commit()
        
        logger.info(f"License agreement deleted: {license_id}")
        
        return {"message": "License agreement deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete license agreement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete license agreement"
        )


# Helper functions
def _validate_status_transition(current_status: str, new_status: str) -> bool:
    """Validate license status transitions"""    valid_transitions = {
        LicenseStatus.DRAFT.value: [LicenseStatus.PENDING.value],
        LicenseStatus.PENDING.value: [LicenseStatus.ACTIVE.value, LicenseStatus.TERMINATED.value],
        LicenseStatus.ACTIVE.value: [LicenseStatus.SUSPENDED.value, LicenseStatus.TERMINATED.value, LicenseStatus.EXPIRED.value],
        LicenseStatus.SUSPENDED.value: [LicenseStatus.ACTIVE.value, LicenseStatus.TERMINATED.value],
        LicenseStatus.EXPIRED.value: [LicenseStatus.ACTIVE.value],
        LicenseStatus.TERMINATED.value: []
    }
    
    return new_status in valid_transitions.get(current_status, [])


# Background task functions
async def _generate_license_contract(license_id: str, agreement: LicenseAgreement, user: dict):
    """Generate license contract document"""    try:
        # Generate contract using licensing engine
        contract_data = await licensing_engine.generate_contract(agreement, user)
        
        # Store contract
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE license_agreements 
                SET contract_url = %s, contract_generated_at = %s
                WHERE license_id = %s
            """, (contract_data['url'], datetime.utcnow(), license_id))
            await session.commit()
        
        logger.info(f"License contract generated: {license_id}")
        
    except Exception as e:
        logger.error(f"Generate license contract failed: {e}")
        
        # Mark as failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE license_agreements 
                SET contract_generation_error = %s
                WHERE license_id = %s
            """, (str(e), license_id))
            await session.commit()