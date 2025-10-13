"""
Image Analysis Routes
API endpoints for medical image analysis using AI
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from uuid import UUID
from typing import Optional, List
import logging
import json
from sqlalchemy import text

from utils.database import get_db
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/images", tags=["Image Analysis"])
logger = logging.getLogger(__name__)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_medical_image(
    image: UploadFile = File(...),
    image_type: str = "skin",  # skin, xray, mri, ct_scan
    symptom_report_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze medical image using AI
    
    Supports multiple image types:
    - **skin**: Skin conditions (eczema, psoriasis, acne, melanoma, rash, burn)
    - **xray**: X-ray images (pneumonia, fractures, TB)
    - **mri**: MRI scans (requires specialized model)
    - **ct_scan**: CT scan images (requires specialized model)
    
    Process:
    1. Validate image format (JPEG, PNG)
    2. Preprocess image for ML model
    3. Run inference using appropriate model
    4. Return classification results with confidence scores
    5. Save image and analysis to database
    
    Returns:
    - **detected_condition**: Primary detected condition
    - **confidence**: Confidence score (0-1)
    - **alternative_conditions**: Other possible conditions with scores
    - **recommendations**: Suggested actions
    - **medical_disclaimer**: Important warning about AI limitations
    
    **IMPORTANT DISCLAIMER**: This is a preliminary AI analysis.
    Always consult with a qualified healthcare professional for
    accurate diagnosis and treatment.
    """
    from services.image_analyzer import MedicalImageAnalyzer
    from uuid import uuid4
    from datetime import datetime
    import os
    import tempfile
    
    # Validate image type
    if image_type not in ["skin", "xray", "mri", "ct_scan"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {image_type}. Supported: skin, xray, mri, ct_scan"
        )
    
    # Validate file is an image
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG)"
        )
    
    try:
        # Save image temporarily for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as tmp_file:
            content = await image.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Analyze image
        analyzer = MedicalImageAnalyzer()
        
        if image_type == "skin":
            analysis = analyzer.analyze_skin_condition(tmp_path)
        elif image_type == "xray":
            analysis = analyzer.analyze_xray(tmp_path)
        else:
            # MRI and CT scan not yet implemented
            analysis = {
                "detected_condition": "analysis_pending",
                "confidence": 0.0,
                "alternatives": [],
                "recommendations": [f"{image_type.upper()} analysis requires specialized model integration"],
                "requires_urgent_care": False,
                "medical_disclaimer": "AI analysis for this image type is not yet available."
            }
        
        # Cleanup temporary file
        os.unlink(tmp_path)
        
        # Add metadata
        image_id = uuid4()
        analyzed_at = datetime.now()
        
        # Save to database
        query = text("""
        INSERT INTO medcare_images 
        (id, patient_id, image_type, filename, detected_condition, confidence, 
         alternative_conditions, recommendations, analyzed_at, analyzed_by, symptom_report_id)
        VALUES (:id, :patient_id, :image_type, :filename, :detected_condition, :confidence, 
                :alternative_conditions, :recommendations, :analyzed_at, :analyzed_by, :symptom_report_id)
        """)
        await db.execute(query, {
            'id': str(image_id),
            'patient_id': str(current_user["id"]),
            'image_type': image_type,
            'filename': image.filename,
            'detected_condition': analysis.get("detected_condition"),
            'confidence': analysis.get("confidence", 0.0),
            'alternative_conditions': json.dumps(analysis.get("alternatives", [])),
            'recommendations': json.dumps(analysis.get("recommendations", [])),
            'analyzed_at': analyzed_at,
            'analyzed_by': str(current_user["id"]),
            'symptom_report_id': str(symptom_report_id) if symptom_report_id else None
        })
        await db.commit()
        
        analysis["image_id"] = str(image_id)
        analysis["image_type"] = image_type
        analysis["patient_id"] = str(current_user["id"])
        analysis["analyzed_at"] = analyzed_at.isoformat()
        analysis["symptom_report_id"] = str(symptom_report_id) if symptom_report_id else None
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}"
        )


@router.get("/{image_id}")
async def get_medical_image_analysis(
    image_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get medical image and analysis results
    
    Returns previously analyzed image with AI results.
    """
    from sqlalchemy import text
    import json
    
    try:
        query = text("""
            SELECT id, patient_id, image_type, analysis_result, analyzed_at
            FROM medcare_images
            WHERE id = :image_id
        """)
        
        result = await db.execute(query, {"image_id": str(image_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical image {image_id} not found"
            )
        
        analysis = row[3]
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        return {
            "image_id": str(row[0]),
            "patient_id": str(row[1]),
            "image_type": row[2],
            "analysis": analysis,
            "analyzed_at": row[4].isoformat() if row[4] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error retrieving image (table may not exist): {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical image {image_id} not found"
        )


@router.get("/patient/{patient_id}")
async def get_patient_medical_images(
    patient_id: UUID,
    image_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get medical image history for a patient
    
    Returns list of all medical images analyzed for the patient.
    Can filter by image type.
    """
    from sqlalchemy import text
    import json
    
    try:
        if image_type:
            query = text("""
                SELECT id, patient_id, image_type, analysis_result, analyzed_at
                FROM medcare_images
                WHERE patient_id = :patient_id AND image_type = :image_type
                ORDER BY analyzed_at DESC
                LIMIT :limit OFFSET :offset
            """)
            params = {
                "patient_id": str(patient_id),
                "image_type": image_type,
                "limit": limit,
                "offset": offset
            }
        else:
            query = text("""
                SELECT id, patient_id, image_type, analysis_result, analyzed_at
                FROM medcare_images
                WHERE patient_id = :patient_id
                ORDER BY analyzed_at DESC
                LIMIT :limit OFFSET :offset
            """)
            params = {
                "patient_id": str(patient_id),
                "limit": limit,
                "offset": offset
            }
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        images = []
        for row in rows:
            analysis = row[3]
            if isinstance(analysis, str):
                analysis = json.loads(analysis)
            
            images.append({
                "image_id": str(row[0]),
                "patient_id": str(row[1]),
                "image_type": row[2],
                "analysis": analysis,
                "analyzed_at": row[4].isoformat() if row[4] else None
            })
        
        return images
        
    except Exception as e:
        logger.warning(f"Error retrieving images (table may not exist): {e}")
        # Return empty list if table doesn't exist yet
        return []
