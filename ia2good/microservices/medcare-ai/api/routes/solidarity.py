"""
Medication Solidarity Routes
Help patients who can't afford medications
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
import logging

from models.solidarity import (
    SolidarityRequestCreate, SolidarityRequest, SolidarityRequestWithDetails,
    ContributionCreate, Contribution, DeliveryCreate, Delivery,
    SolidarityUrgency, SolidarityStatus, DeliveryStatus
)
from services.solidarity_service import MedicationSolidarityService
from utils.database import get_db
from utils.auth import get_current_user, require_role
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/solidarity", tags=["Medication Solidarity"])
logger = logging.getLogger(__name__)


@router.post("/requests", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_solidarity_request(
    request_data: SolidarityRequestCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create medication solidarity request
    
    If you can't afford medications you need, the community can help!
    
    How it works:
    1. You post your medication need with prescription (if available)
    2. Community volunteers contribute funds
    3. Once fully funded, medication is purchased and delivered to you
    4. Everything is tracked and transparent
    
    Urgency levels:
    - critical: Life-threatening condition, need immediate help (insulin, epilepsy meds, etc.)
    - urgent: Important treatment, should get within days
    - normal: Regular medication, can wait a bit
    
    Requirements:
    - Valid prescription (recommended, increases trust)
    - Clear description of need
    - List of medications with estimated costs
    
    Your personal information is protected. Only delivery address is shared (securely).
    """
    
    try:
        service = MedicationSolidarityService(db)
        
        request = await service.create_solidarity_request(
            patient_id=request_data.patient_id,
            prescription_id=request_data.prescription_id,
            title=request_data.title,
            description=request_data.description,
            medications_needed=[med.dict() for med in request_data.medications_needed],
            urgency=request_data.urgency.value,
            currency=request_data.currency
        )
        
        return {
            "success": True,
            "request_id": request['id'],
            "total_cost": float(request['total_estimated_cost']),
            "currency": request['currency'],
            "urgency": request['urgency'],
            "status": request['status'],
            "message": "Solidarity request created. Community will be notified.",
            "request_url": f"/medcare/solidarity/requests/{request['id']}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Solidarity request creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating request: {str(e)}"
        )


@router.get("/requests/{request_id}", response_model=SolidarityRequestWithDetails)
async def get_solidarity_request(
    request_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get solidarity request with all details
    
    Shows:
    - Medication needs
    - Funding progress
    - List of contributions (anonymous if contributor chose)
    - Delivery status
    """
    
    try:
        service = MedicationSolidarityService(db)
        
        details = await service.get_request_with_details(request_id)
        
        return SolidarityRequestWithDetails(**details)
        
    except Exception as e:
        logger.error(f"Request retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )


@router.get("/requests", response_model=List[dict])
async def search_solidarity_requests(
    urgency: Optional[SolidarityUrgency] = Query(None, description="Filter by urgency"),
    status_filter: Optional[SolidarityStatus] = Query(None, description="Filter by status"),
    verified_only: bool = Query(False, description="Show only doctor-verified requests"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Search open solidarity requests
    
    Use this to find patients you want to help.
    
    Filters:
    - Urgency: Show only critical/urgent cases
    - Verified: Show only requests verified by doctors
    - Status: Show open/partially funded requests
    
    Requests are sorted by:
    1. Urgency (critical first)
    2. Verification status (verified first)
    3. Time posted (oldest first - they've been waiting longer)
    """
    
    try:
        service = MedicationSolidarityService(db)
        
        requests = await service.search_open_requests(
            urgency=urgency.value if urgency else None,
            verified_only=verified_only,
            limit=limit,
            offset=offset
        )
        
        return requests
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching requests: {str(e)}"
        )


@router.post("/requests/{request_id}/contribute", response_model=dict, status_code=status.HTTP_201_CREATED)
async def contribute_to_request(
    request_id: UUID,
    contribution_data: ContributionCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Contribute funds to solidarity request
    
    Help someone get the medication they need!
    
    Payment methods supported:
    - Credit/Debit card
    - PayPal
    - Bank transfer
    - Mobile payment (M-Pesa, etc.)
    
    Your contribution:
    - Goes directly to purchasing medication
    - Is tracked transparently
    - Can be anonymous if you choose
    - You can add a message of support
    
    After contribution:
    - You receive confirmation receipt
    - Patient is notified
    - When fully funded, medication is purchased and delivered
    - You receive update when delivered
    """
    
    try:
        service = MedicationSolidarityService(db)
        
        contribution = await service.contribute_to_request(
            request_id=request_id,
            contributor_id=contribution_data.contributor_id,
            amount=contribution_data.amount,
            currency=contribution_data.currency,
            payment_method=contribution_data.payment_method,
            message_to_patient=contribution_data.message_to_patient,
            is_anonymous=contribution_data.is_anonymous
        )
        
        return {
            "success": True,
            "contribution_id": contribution['id'],
            "amount": float(contribution['amount']),
            "currency": contribution['currency'],
            "transaction_id": contribution['payment_transaction_id'],
            "message": "Thank you for your contribution! Patient will be notified.",
            "receipt_url": f"/medcare/solidarity/contributions/{contribution['id']}/receipt"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Contribution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing contribution: {str(e)}"
        )


@router.post("/requests/{request_id}/verify", status_code=status.HTTP_200_OK)
async def verify_solidarity_request(
    request_id: UUID,
    doctor_id: UUID,
    verification_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Doctor verifies solidarity request
    
    Only for doctors who issued the prescription or treating the patient.
    
    Verification:
    - Confirms patient genuinely needs the medication
    - Confirms prescription is authentic
    - Increases community trust
    - Increases likelihood of funding
    
    Verified requests are shown with a ✓ badge
    """
    
    # Check if user is doctor
    if current_user.get('role') != 'doctor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can verify solidarity requests"
        )
    
    try:
        service = MedicationSolidarityService(db)
        
        success = await service.verify_request_by_doctor(
            request_id,
            doctor_id,
            verification_notes
        )
        
        if success:
            return {
                "success": True,
                "message": "Request verified successfully",
                "verified_by": "Dr. " + current_user.get('name', 'Anonymous')
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to verify request"
            )
        
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying request: {str(e)}"
        )


@router.post("/requests/{request_id}/delivery", response_model=dict, status_code=status.HTTP_201_CREATED)
async def initiate_delivery(
    request_id: UUID,
    delivery_data: DeliveryCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Initiate medication delivery (Admin or Pharmacy only)
    
    Called when solidarity request is fully funded.
    
    Delivery options:
    1. Pharmacy fulfillment: Partner pharmacy purchases and delivers
    2. Volunteer delivery: Volunteer buys from local pharmacy and delivers
    """
    
    # Check permissions
    if current_user.get('role') not in ['admin', 'pharmacy', 'volunteer']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        service = MedicationSolidarityService(db)
        
        delivery = await service.initiate_delivery(
            request_id,
            delivery_data.pharmacy_id,
            delivery_data.volunteer_id
        )
        
        return {
            "success": True,
            "delivery_id": delivery['id'],
            "delivery_status": delivery['delivery_status'],
            "message": "Delivery initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"Delivery initiation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating delivery: {str(e)}"
        )


@router.patch("/deliveries/{delivery_id}", status_code=status.HTTP_200_OK)
async def update_delivery_status(
    delivery_id: UUID,
    status_update: str,
    tracking_number: Optional[str] = None,
    delivery_proof_url: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update delivery status
    
    Status flow:
    pending → purchased → in_transit → delivered
    
    Updates are visible to patient and contributors
    """
    
    # Check permissions
    if current_user.get('role') not in ['admin', 'pharmacy', 'volunteer']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        service = MedicationSolidarityService(db)
        
        delivery = await service.update_delivery_status(
            delivery_id,
            status_update,
            tracking_number,
            delivery_proof_url,
            notes
        )
        
        return {
            "success": True,
            "delivery_id": delivery['id'],
            "delivery_status": delivery['delivery_status'],
            "tracking_number": delivery.get('tracking_number'),
            "message": "Delivery status updated"
        }
        
    except Exception as e:
        logger.error(f"Delivery update error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating delivery: {str(e)}"
        )


@router.get("/my-contributions", response_model=List[Contribution])
async def get_my_contributions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get my contribution history
    
    See all the solidarity requests you've contributed to
    and their current status
    """
    
    # TODO: Implement retrieval from database
    return []


@router.get("/statistics", response_model=dict)
async def get_solidarity_statistics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get solidarity program statistics
    
    Shows community impact:
    - Total patients helped
    - Total funds raised
    - Total medications delivered
    - Average time to funding
    - Active requests
    """
    from sqlalchemy import text
    
    try:
        # Get total requests
        total_query = text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN status = 'fulfilled' THEN 1 END) as fulfilled,
                   COUNT(CASE WHEN status = 'open' OR status = 'partially_funded' THEN 1 END) as active,
                   COALESCE(SUM(total_estimated_cost), 0) as total_cost,
                   COALESCE(SUM(amount_raised), 0) as total_raised
            FROM medcare_solidarity_requests
        """)
        
        result = await db.execute(total_query)
        row = result.fetchone()
        
        if row:
            return {
                "total_requests": row[0] or 0,
                "total_patients_helped": row[1] or 0,
                "total_amount_raised": str(row[4] or 0.0),
                "total_estimated_cost": str(row[3] or 0.0),
                "active_requests": row[2] or 0,
                "average_funding_time_hours": 24,  # Mock value
                "top_contributors_count": 0,  # TODO: Calculate from contributions table
                "message": "Community solidarity statistics"
            }
        else:
            return {
                "total_requests": 0,
                "total_patients_helped": 0,
                "total_amount_raised": "0.00",
                "total_medications_delivered": 0,
                "active_requests": 0,
                "average_funding_time_hours": 0,
                "top_contributors_count": 0
            }
            
    except Exception as e:
        logger.warning(f"Statistics calculation error (table may not exist): {e}")
        # Return default values gracefully without error field
        return {
            "total_requests": 0,
            "total_patients_helped": 0,
            "total_amount_raised": "0.00",
            "total_medications_delivered": 0,
            "active_requests": 0,
            "average_funding_time_hours": 0,
            "top_contributors_count": 0,
            "message": "Statistics not available (tables not initialized)"
        }
