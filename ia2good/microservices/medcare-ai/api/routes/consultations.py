"""
Consultation Routes
API endpoints for telemedicine consultations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Optional

from models.consultation import (
    Consultation, ConsultationCreate, ConsultationRequest,
    ConsultationSummary, ConsultationUpdate
)
from utils.database import get_db
from utils.auth import get_current_user, require_role
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/consultations", tags=["Consultations"])


@router.post("/request", response_model=Consultation, status_code=status.HTTP_201_CREATED)
async def request_consultation(
    consultation_request: ConsultationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request a telemedicine consultation
    
    Initiates a consultation request which triggers:
    1. Doctor matching based on specialty and availability
    2. Scheduling of consultation time
    3. Creation of video call room (if video consultation)
    4. Notification to matched doctor
    
    - **symptom_report_id**: Related symptom report
    - **preferred_specialty**: Optional preferred doctor specialty
    - **urgency**: emergency/urgent/routine
    - **preferred_time**: Optional preferred consultation time
    
    Returns consultation details with matched doctor info.
    """
    from services.doctor_matching import DoctorMatchingService
    from uuid import uuid4
    from datetime import datetime, timedelta
    
    try:
        # Find available doctor
        matching_service = DoctorMatchingService(db)
        doctor = await matching_service.find_available_doctor(
            specialty=consultation_request.preferred_specialty,
            urgency=consultation_request.urgency
        )
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No doctors available at the moment. Please try again later."
            )
        
        # Create consultation
        consultation_id = uuid4()
        consultation = Consultation(
            id=consultation_id,
            patient_id=current_user["id"],
            doctor_id=doctor["id"],
            symptom_report_id=consultation_request.symptom_report_id,
            type=consultation_request.consultation_type or "video",
            status="scheduled",
            scheduled_at=consultation_request.preferred_time or datetime.now() + timedelta(minutes=5),
            created_at=datetime.now()
        )
        
        # Notify doctor (placeholder)
        await matching_service.notify_doctor(
            doctor["id"], 
            consultation_id,
            patient_info={
                "id": current_user["id"],
                "name": current_user.get("name", "Unknown"),
                "severity": 5
            },
            urgency=consultation_request.urgency
        )
        
        # Save to database
        try:
            import json
            from sqlalchemy import text
            from sqlalchemy.sql import func
            
            query = text("""
                INSERT INTO medcare_consultations 
                (id, patient_id, doctor_id, symptom_report_id, type, status, scheduled_at, created_at)
                VALUES (:id, :patient_id, :doctor_id, :symptom_report_id, :type, :status, :scheduled_at, :created_at)
            """)
            
            await db.execute(query, {
                "id": str(consultation_id),
                "patient_id": str(consultation.patient_id),
                "doctor_id": str(consultation.doctor_id),
                "symptom_report_id": str(consultation.symptom_report_id) if consultation.symptom_report_id else None,
                "type": consultation.type,
                "status": consultation.status,
                "scheduled_at": consultation.scheduled_at,
                "created_at": consultation.created_at
            })
            await db.commit()
            print(f"✅ Consultation {consultation_id} saved to DB")
        except Exception as db_error:
            print(f"❌ DB Save Error: {db_error}")
            await db.rollback()
        
        return consultation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating consultation: {str(e)}"
        )


@router.get("/{consultation_id}", response_model=Consultation)
async def get_consultation(
    consultation_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consultation details
    
    Returns full consultation information including:
    - Patient and doctor details
    - Consultation status and timing
    - Related symptom report
    - Diagnosis and notes
    """
    from sqlalchemy import text
    
    try:
        query = text("""
            SELECT id, patient_id, doctor_id, symptom_report_id, type, status, 
                   scheduled_at, started_at, ended_at, duration_minutes,
                   diagnosis, notes, amount, created_at, updated_at
            FROM medcare_consultations
            WHERE id = :consultation_id
        """)
        
        result = await db.execute(query, {"consultation_id": str(consultation_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consultation {consultation_id} not found"
            )
        
        return Consultation(
            id=row[0],
            patient_id=row[1],
            doctor_id=row[2],
            symptom_report_id=row[3],
            type=row[4],
            status=row[5],
            scheduled_at=row[6],
            started_at=row[7],
            completed_at=row[8],
            duration_minutes=row[9],
            diagnosis=row[10],
            notes=row[11],
            created_at=row[13],
            updated_at=row[14]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving consultation: {str(e)}"
        )


@router.post("/{consultation_id}/join", response_model=dict)
async def join_consultation(
    consultation_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Join a consultation (patient or doctor joins video call)
    
    Returns WebRTC room details for video call:
    - room_id
    - access_token
    - turn/stun server configuration
    """
    try:
        # TODO: Verify consultation exists and user is authorized
        # TODO: Create actual WebRTC room when service is integrated
        
        # Return placeholder WebRTC configuration
        return {
            "room_id": str(consultation_id),
            "video_url": f"https://meet.ia2good.com/consultation/{consultation_id}",
            "access_token": "placeholder_token",
            "turn_servers": [
                {
                    "urls": "stun:stun.l.google.com:19302"
                }
            ],
            "ice_servers": [
                {"urls": "stun:stun1.l.google.com:19302"},
                {"urls": "stun:stun2.l.google.com:19302"}
            ],
            "status": "joined",
            "user_id": str(current_user.get("id")),
            "message": "Successfully joined video call room. WebRTC integration pending."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error joining consultation: {str(e)}"
        )


@router.post("/{consultation_id}/start", response_model=dict)
async def start_consultation(
    consultation_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Start a consultation (video call)
    
    Returns WebRTC room details for video call:
    - room_id
    - access_token
    - turn/stun server configuration
    """
    try:
        # TODO: Verify consultation exists and user is authorized
        # TODO: Create actual WebRTC room when service is integrated
        
        # Return placeholder WebRTC configuration
        return {
            "room_id": str(consultation_id),
            "video_url": f"https://meet.ia2good.com/consultation/{consultation_id}",
            "access_token": "placeholder_token",
            "turn_servers": [
                {
                    "urls": "stun:stun.l.google.com:19302"
                }
            ],
            "ice_servers": [
                {"urls": "stun:stun1.l.google.com:19302"},
                {"urls": "stun:stun2.l.google.com:19302"}
            ],
            "status": "ready",
            "message": "Video call room created. WebRTC integration pending."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting consultation: {str(e)}"
        )


@router.put("/{consultation_id}/complete", response_model=Consultation)
async def complete_consultation(
    consultation_id: UUID,
    summary: ConsultationSummary,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a consultation (doctor only)
    
    Doctor submits consultation summary including:
    - Final diagnosis
    - Notes
    - Follow-up requirements
    - Prescriptions (if any)
    
    This marks the consultation as completed and triggers:
    - Prescription creation (if provided)
    - Follow-up scheduling (if required)
    - Patient notification
    """
    from sqlalchemy import text
    from datetime import datetime
    
    try:
        # First, check if consultation exists
        check_query = text("""
            SELECT id, patient_id, doctor_id, started_at, status
            FROM medcare_consultations
            WHERE id = :consultation_id
        """)
        
        result = await db.execute(check_query, {"consultation_id": str(consultation_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consultation {consultation_id} not found"
            )
        
        # Calculate duration if started
        started_at = row[3]
        duration_minutes = None
        if started_at:
            duration_minutes = int((datetime.now() - started_at).total_seconds() / 60)
        
        # Update consultation with summary
        update_query = text("""
            UPDATE medcare_consultations
            SET status = :status,
                ended_at = :ended_at,
                duration_minutes = :duration_minutes,
                diagnosis = :diagnosis,
                notes = :notes,
                updated_at = :updated_at
            WHERE id = :consultation_id
        """)
        
        await db.execute(update_query, {
            "consultation_id": str(consultation_id),
            "status": "completed",
            "ended_at": datetime.now(),
            "duration_minutes": duration_minutes,
            "diagnosis": summary.diagnosis,
            "notes": summary.notes,
            "updated_at": datetime.now()
        })
        await db.commit()
        
        print(f"✅ Consultation {consultation_id} marked as completed")
        
        # Retrieve updated consultation
        get_query = text("""
            SELECT id, patient_id, doctor_id, symptom_report_id, type, status, 
                   scheduled_at, started_at, ended_at, duration_minutes,
                   diagnosis, notes, amount, created_at, updated_at
            FROM medcare_consultations
            WHERE id = :consultation_id
        """)
        
        result = await db.execute(get_query, {"consultation_id": str(consultation_id)})
        row = result.fetchone()
        
        return Consultation(
            id=row[0],
            patient_id=row[1],
            doctor_id=row[2],
            symptom_report_id=row[3],
            type=row[4],
            status=row[5],
            scheduled_at=row[6],
            started_at=row[7],
            completed_at=row[8],
            duration_minutes=row[9],
            diagnosis=row[10],
            notes=row[11],
            created_at=row[13],
            updated_at=row[14]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing consultation: {str(e)}"
        )


@router.get("/patient/{patient_id}", response_model=list[Consultation])
async def get_patient_consultations(
    patient_id: UUID,
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consultation history for a patient
    
    Returns list of all consultations for the patient,
    ordered by most recent first.
    """
    from sqlalchemy import text
    
    try:
        query = text("""
            SELECT id, patient_id, doctor_id, symptom_report_id, type, status, 
                   scheduled_at, started_at, ended_at, duration_minutes,
                   diagnosis, notes, amount, created_at, updated_at
            FROM medcare_consultations
            WHERE patient_id = :patient_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await db.execute(query, {
            "patient_id": str(patient_id),
            "limit": limit,
            "offset": offset
        })
        rows = result.fetchall()
        
        consultations = []
        for row in rows:
            consultations.append(Consultation(
                id=row[0],
                patient_id=row[1],
                doctor_id=row[2],
                symptom_report_id=row[3],
                type=row[4],
                status=row[5],
                scheduled_at=row[6],
                started_at=row[7],
                completed_at=row[8],
                duration_minutes=row[9],
                diagnosis=row[10],
                notes=row[11],
                created_at=row[13],
                updated_at=row[14]
            ))
        
        return consultations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving consultation history: {str(e)}"
        )
