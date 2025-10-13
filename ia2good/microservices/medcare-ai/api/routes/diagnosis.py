"""
Diagnosis Routes
API endpoints for AI diagnosis and recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from models.medical_record import DiagnosisResponse, DiagnosisCreate

from utils.database import get_db
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/diagnosis", tags=["Diagnosis"])


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get diagnosis details
    
    Returns diagnosis information including:
    - Primary condition with confidence score
    - ICD-10 code
    - Urgency level
    - Recommendations
    - Differential diagnoses (alternative conditions)
    
    **Note**: This is a preliminary AI diagnosis. Always consult
    with a qualified healthcare professional for accurate diagnosis.
    """
    from sqlalchemy import text
    import json
    
    try:
        query = text("""
            SELECT id, symptom_report_id, condition_name, confidence, icd10_code,
                   urgency, recommendations, differential_diagnoses, created_at
            FROM medcare_diagnoses
            WHERE id = :diagnosis_id
        """)
        
        result = await db.execute(query, {"diagnosis_id": str(diagnosis_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        
        diff_diagnoses = row[7]
        if isinstance(diff_diagnoses, str):
            diff_diagnoses = json.loads(diff_diagnoses)
        
        return DiagnosisResponse(
            id=row[0],
            symptom_report_id=row[1],
            condition_name=row[2],
            confidence=row[3],
            icd10_code=row[4],
            urgency=row[5],
            recommendations=row[6],
            differential_diagnoses=diff_diagnoses,
            created_at=row[8]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving diagnosis: {str(e)}"
        )


@router.post("/", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    diagnosis_data: DiagnosisCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a diagnosis from symptom report
    
    Generates AI diagnosis based on symptom analysis or
    allows healthcare professionals to add professional assessment.
    """
    from services.diagnosis_engine import DiagnosisEngine
    from uuid import uuid4
    from datetime import datetime
    from sqlalchemy import text
    import json
    
    try:
        diagnosis_id = uuid4()
        
        # Generate AI diagnosis if symptom_report_id provided
        if diagnosis_data.symptom_report_id:
            # Fetch symptom report
            symptom_query = text("""
                SELECT symptoms, severity, body_parts
                FROM medcare_symptom_reports
                WHERE id = :symptom_id
            """)
            
            result = await db.execute(symptom_query, {
                "symptom_id": str(diagnosis_data.symptom_report_id)
            })
            symptom_row = result.fetchone()
            
            if symptom_row:
                symptoms_data = symptom_row[0]
                if isinstance(symptoms_data, str):
                    symptoms_data = json.loads(symptoms_data)
                
                # Generate AI diagnosis
                engine = DiagnosisEngine(db)
                ai_diagnosis = engine.generate_diagnosis(symptoms_data, {})
                
                condition_name = ai_diagnosis["primary_diagnosis"]["condition"]
                confidence = ai_diagnosis["primary_diagnosis"]["confidence"]
                icd10_code = ai_diagnosis["primary_diagnosis"]["icd10"]
                recommendations = "\n".join(ai_diagnosis["general_treatment_suggestions"])
                differential = ai_diagnosis["differential_diagnoses"]
            else:
                # Use provided data
                condition_name = diagnosis_data.condition_name or "Unknown"
                confidence = diagnosis_data.confidence or 0.5
                icd10_code = diagnosis_data.icd10_code or "R69"
                recommendations = diagnosis_data.recommendations or "Consult healthcare provider"
                differential = diagnosis_data.differential_diagnoses or []
        else:
            # Manual diagnosis by doctor
            condition_name = diagnosis_data.condition_name or "Unknown"
            confidence = diagnosis_data.confidence or 1.0
            icd10_code = diagnosis_data.icd10_code or "R69"
            recommendations = diagnosis_data.recommendations or ""
            differential = diagnosis_data.differential_diagnoses or []
        
        # Determine urgency
        urgency = diagnosis_data.urgency or "routine"
        
        # Save to database
        insert_query = text("""
            INSERT INTO medcare_diagnoses
            (id, symptom_report_id, condition_name, confidence, icd10_code, 
             urgency, recommendations, differential_diagnoses, created_at)
            VALUES (:id, :symptom_report_id, :condition_name, :confidence, :icd10_code,
                    :urgency, :recommendations, :differential_diagnoses, :created_at)
        """)
        
        await db.execute(insert_query, {
            "id": str(diagnosis_id),
            "symptom_report_id": str(diagnosis_data.symptom_report_id) if diagnosis_data.symptom_report_id else None,
            "condition_name": condition_name,
            "confidence": confidence,
            "icd10_code": icd10_code,
            "urgency": urgency,
            "recommendations": recommendations,
            "differential_diagnoses": json.dumps(differential),
            "created_at": datetime.now()
        })
        await db.commit()
        
        print(f"✅ Diagnosis {diagnosis_id} created successfully")
        
        return DiagnosisResponse(
            id=diagnosis_id,
            symptom_report_id=diagnosis_data.symptom_report_id,
            condition_name=condition_name,
            confidence=confidence,
            icd10_code=icd10_code,
            urgency=urgency,
            recommendations=recommendations,
            differential_diagnoses=differential,
            created_at=datetime.now()
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating diagnosis: {str(e)}"
        )
