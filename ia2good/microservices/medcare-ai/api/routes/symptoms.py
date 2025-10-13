"""
Symptom Analysis Routes
API endpoints for symptom reporting and AI analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Optional

from models.medical_record import (
    SymptomReportCreate, SymptomReportWithAnalysis
)
from utils.database import get_db
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/symptoms", tags=["Symptoms"])


@router.post("/report", response_model=SymptomReportWithAnalysis, status_code=status.HTTP_201_CREATED)
async def report_symptoms(
    symptom_data: SymptomReportCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Report symptoms for AI analysis
    
    Patient submits their symptoms, which are then analyzed by AI
    to generate a preliminary diagnosis and urgency assessment.
    
    - **symptoms**: Dictionary of symptoms (e.g., {"pain": {"location": "abdomen", "severity": 7}})
    - **severity**: Overall severity rating 1-10
    - **duration_hours**: How long symptoms have been present
    - **body_parts**: List of affected body parts
    - **images**: Optional list of image URLs
    
    Returns symptom report with AI analysis including:
    - Top 3 probable conditions
    - Urgency level (emergency/urgent/routine)
    - Recommended actions
    - Follow-up questions
    """
    from services.symptom_analyzer import SymptomAnalyzerService
    from uuid import uuid4
    from datetime import datetime
    
    try:
        # Create service instance
        service = SymptomAnalyzerService(db)
        
        # Prepare symptom data for analysis
        symptom_dict = {
            "symptoms": symptom_data.symptoms,
            "severity": symptom_data.severity,
            "duration_hours": symptom_data.duration_hours,
            "body_parts": symptom_data.body_parts
        }
        
        # Perform AI analysis
        analysis = service.analyze_symptoms(symptom_dict)
        
        # Create response with analysis
        report_id = uuid4()
        response = SymptomReportWithAnalysis(
            id=report_id,
            patient_id=symptom_data.patient_id,
            symptoms=symptom_data.symptoms,
            severity=symptom_data.severity,
            duration_hours=symptom_data.duration_hours,
            body_parts=symptom_data.body_parts,
            images=symptom_data.images,
            ai_analysis=analysis,
            created_at=datetime.now()
        )
        
        # Sauvegarder en base de données PostgreSQL
        try:
            import json
            from sqlalchemy import text
            query = text("""
                INSERT INTO medcare_symptom_reports 
                (id, patient_id, symptoms, severity, duration_hours, body_parts, images, ai_analysis, created_at)
                VALUES (:id, :patient_id, CAST(:symptoms AS jsonb), :severity, :duration_hours, :body_parts, :images, CAST(:ai_analysis AS jsonb), :created_at)
            """)
            
            await db.execute(query, {
                "id": str(report_id),
                "patient_id": str(symptom_data.patient_id),
                "symptoms": json.dumps(symptom_data.symptoms),
                "severity": symptom_data.severity,
                "duration_hours": symptom_data.duration_hours,
                "body_parts": symptom_data.body_parts,
                "images": symptom_data.images,
                "ai_analysis": json.dumps(analysis),
                "created_at": datetime.now()
            })
            await db.commit()
            print(f"✅ Symptom report {report_id} saved to DB")
        except Exception as db_error:
            print(f"❌ DB Save Error: {db_error}")
            await db.rollback()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing symptoms: {str(e)}"
        )


@router.get("/{report_id}", response_model=SymptomReportWithAnalysis)
async def get_symptom_report(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific symptom report by ID
    
    Returns the symptom report with AI analysis results.
    """
    from sqlalchemy import text
    from datetime import datetime
    
    try:
        query = text("""
            SELECT id, patient_id, symptoms, severity, duration_hours, 
                   body_parts, images, ai_analysis, created_at
            FROM medcare_symptom_reports
            WHERE id = :report_id
        """)
        
        result = await db.execute(query, {"report_id": str(report_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symptom report {report_id} not found"
            )
        
        return SymptomReportWithAnalysis(
            id=row[0],
            patient_id=row[1],
            symptoms=row[2],
            severity=row[3],
            duration_hours=row[4],
            body_parts=row[5] or [],
            images=row[6] or [],
            ai_analysis=row[7],
            created_at=row[8]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving symptom report: {str(e)}"
        )


@router.get("/patient/{patient_id}", response_model=list[SymptomReportWithAnalysis])
async def get_patient_symptom_history(
    patient_id: UUID,
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get symptom report history for a patient
    
    Returns list of all symptom reports for the patient,
    ordered by most recent first.
    """
    from sqlalchemy import text
    
    try:
        query = text("""
            SELECT id, patient_id, symptoms, severity, duration_hours, 
                   body_parts, images, ai_analysis, created_at
            FROM medcare_symptom_reports
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
        
        reports = []
        for row in rows:
            reports.append(SymptomReportWithAnalysis(
                id=row[0],
                patient_id=row[1],
                symptoms=row[2],
                severity=row[3],
                duration_hours=row[4],
                body_parts=row[5] or [],
                images=row[6] or [],
                ai_analysis=row[7],
                created_at=row[8]
            ))
        
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving symptom history: {str(e)}"
        )
