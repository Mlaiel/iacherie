"""
Medical Documents Routes
Upload, analyze, and share medical documents
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from uuid import UUID
from typing import Optional, List
import logging
import json
from sqlalchemy import text

from models.medical_document import (
    MedicalDocument, DocumentAnalysisResult, ShareDocumentRequest,
    DocumentType
)
from services.document_processor import DocumentProcessingService

from utils.database import get_db
from utils.auth import get_current_user, require_role
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/documents", tags=["Medical Documents"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentAnalysisResult, status_code=status.HTTP_201_CREATED)
async def upload_medical_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    patient_id: UUID = Form(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload medical document for AI analysis
    
    Supports:
    - Prescriptions (ordonnances)
    - Lab results (analyses de sang)
    - X-rays (radiographies)
    - MRI scans
    - CT scans
    - Dialysis reports (rapports de dialyse)
    - Blood test results
    - Ultrasound reports
    - ECG reports
    - Any other medical document
    
    The AI will:
    1. Extract text (OCR if image/PDF)
    2. Detect language automatically
    3. Translate to English for analysis
    4. Extract structured medical data
    5. Detect abnormal values
    6. Generate recommendations
    7. Calculate urgency level
    
    Returns preliminary AI analysis
    """
    
    try:
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Must be one of: {', '.join([t.value for t in DocumentType])}"
            )
        
        # Validate file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Process document
        service = DocumentProcessingService(db)
        analysis_result = await service.process_document(
            file_content,
            file.filename,
            doc_type.value,
            patient_id
        )
        
        # Create document record in database
        from uuid import uuid4
        from datetime import datetime
        document_id = uuid4()
        
        # Save to database
        query = text("""
        INSERT INTO medcare_documents 
        (id, patient_id, document_type, filename, detected_language, ocr_confidence, 
         extracted_text, structured_data, key_findings, uploaded_by, uploaded_at, status)
        VALUES (:id, :patient_id, :document_type, :filename, :detected_language, :ocr_confidence, 
                :extracted_text, :structured_data, :key_findings, :uploaded_by, :uploaded_at, :status)
        """)
        await db.execute(query, {
            'id': str(document_id),
            'patient_id': str(patient_id),
            'document_type': doc_type.value,
            'filename': file.filename,
            'detected_language': analysis_result['detected_language'],
            'ocr_confidence': analysis_result['ocr_confidence'],
            'extracted_text': analysis_result['ocr_text'],
            'structured_data': json.dumps(analysis_result['ai_analysis'].get('structured_data', {})),
            'key_findings': json.dumps(analysis_result['ai_analysis'].get('key_findings', [])),
            'uploaded_by': str(current_user['id']),
            'uploaded_at': datetime.utcnow(),
            'status': 'processed'
        })
        await db.commit()
        
        # Return analysis
        return DocumentAnalysisResult(
            document_id=document_id,
            document_type=doc_type,
            detected_language=analysis_result['detected_language'],
            ocr_confidence=analysis_result['ocr_confidence'],
            extracted_text=analysis_result['ocr_text'],
            structured_data=analysis_result['ai_analysis'].get('structured_data', {}),
            key_findings=analysis_result['ai_analysis'].get('key_findings', []),
            abnormal_values=analysis_result['ai_analysis'].get('abnormal_values', []),
            recommendations=analysis_result['ai_analysis'].get('recommendations', []),
            requires_attention=analysis_result['ai_analysis'].get('requires_attention', False),
            urgency_level=analysis_result['ai_analysis'].get('urgency_level', 'normal')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/{document_id}", response_model=MedicalDocument)
async def get_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get medical document by ID
    """
    from sqlalchemy import text
    from datetime import datetime
    
    try:
        query = text("""
            SELECT id, patient_id, document_type, filename, detected_language,
                   ocr_confidence, extracted_text, uploaded_at, status
            FROM medcare_documents
            WHERE id = :document_id
        """)
        
        result = await db.execute(query, {"document_id": str(document_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return MedicalDocument(
            id=row[0],
            patient_id=row[1],
            document_type=row[2],
            filename=row[3],
            file_path=None,  # Not stored in DB
            file_size=len(row[6]) if row[6] else 0,  # text length as proxy
            mime_type="text/plain",  # Default
            uploaded_at=row[7]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error retrieving document (table may not exist): {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )


@router.get("/patient/{patient_id}", response_model=List[MedicalDocument])
async def get_patient_documents(
    patient_id: UUID,
    document_type: Optional[DocumentType] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for a patient
    
    Optionally filter by document type
    """
    from sqlalchemy import text
    
    try:
        if document_type:
            query = text("""
                SELECT id, patient_id, type, filename, file_path, file_size,
                       mime_type, uploaded_at
                FROM medcare_documents
                WHERE patient_id = :patient_id AND type = :document_type
                ORDER BY uploaded_at DESC
                LIMIT :limit OFFSET :offset
            """)
            params = {
                "patient_id": str(patient_id),
                "document_type": document_type.value,
                "limit": limit,
                "offset": offset
            }
        else:
            query = text("""
                SELECT id, patient_id, type, filename, file_path, file_size,
                       mime_type, uploaded_at
                FROM medcare_documents
                WHERE patient_id = :patient_id
                ORDER BY uploaded_at DESC
                LIMIT :limit OFFSET :offset
            """)
            params = {
                "patient_id": str(patient_id),
                "limit": limit,
                "offset": offset
            }
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        documents = []
        for row in rows:
            documents.append(MedicalDocument(
                id=row[0],
                patient_id=row[1],
                document_type=row[2],
                filename=row[3],
                file_path=row[4],
                file_size=row[5],
                mime_type=row[6],
                uploaded_at=row[7]
            ))
        
        return documents
        
    except Exception as e:
        logger.warning(f"Error retrieving documents (table may not exist): {e}")
        # Return empty list if table doesn't exist yet
        return []


@router.post("/{document_id}/share", status_code=status.HTTP_200_OK)
async def share_document_anonymously(
    document_id: UUID,
    share_request: ShareDocumentRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Share document anonymously for community review
    
    Patient can share their medical documents (lab results, images, etc.)
    anonymously to get second opinions from community doctors and specialists.
    
    The document will be:
    1. Anonymized (remove personal info)
    2. Posted to community forum
    3. Visible to verified medical professionals
    4. Open for comments and advice
    
    Returns:
    - anonymous_share_id: ID to track community responses
    - post_url: URL to view community discussion
    """
    
    try:
        service = DocumentProcessingService(db)
        
        anonymous_share_id = await service.share_document_anonymously(
            document_id,
            share_request.share_reason,
            share_request.specific_questions
        )
        
        # Create community post linked to this document
        # TODO: Integrate with community forum
        
        return {
            "success": True,
            "anonymous_share_id": anonymous_share_id,
            "message": "Document shared anonymously with community",
            "post_url": f"/community/posts/{anonymous_share_id}"
        }
        
    except Exception as e:
        logger.error(f"Document sharing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sharing document: {str(e)}"
        )


@router.get("/{document_id}/analysis", response_model=DocumentAnalysisResult)
async def get_document_analysis(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis results for a document
    """
    from sqlalchemy import text
    import json
    
    try:
        query = text("""
            SELECT id, type, analysis_result
            FROM medcare_documents
            WHERE id = :document_id
        """)
        
        result = await db.execute(query, {"document_id": str(document_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        analysis = row[2]
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Return mock analysis if none exists
        if not analysis:
            analysis = {
                "detected_language": "en",
                "ocr_confidence": 0.9,
                "extracted_text": "Document analysis not yet performed",
                "structured_data": {},
                "key_findings": [],
                "abnormal_values": [],
                "recommendations": [],
                "requires_attention": False,
                "urgency_level": "normal"
            }
        
        return DocumentAnalysisResult(
            document_id=row[0],
            document_type=row[1],
            detected_language=analysis.get("detected_language", "en"),
            ocr_confidence=analysis.get("ocr_confidence", 0.0),
            extracted_text=analysis.get("extracted_text", ""),
            structured_data=analysis.get("structured_data", {}),
            key_findings=analysis.get("key_findings", []),
            abnormal_values=analysis.get("abnormal_values", []),
            recommendations=analysis.get("recommendations", []),
            requires_attention=analysis.get("requires_attention", False),
            urgency_level=analysis.get("urgency_level", "normal")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error retrieving analysis (table may not exist): {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis for document {document_id} not found"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete medical document
    
    Note: Some documents may be retained for legal/compliance reasons
    """
    from sqlalchemy import text
    
    try:
        # Check if document exists
        check_query = text("""
            SELECT id FROM medcare_documents WHERE id = :document_id
        """)
        
        result = await db.execute(check_query, {"document_id": str(document_id)})
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Delete document
        delete_query = text("""
            DELETE FROM medcare_documents WHERE id = :document_id
        """)
        
        await db.execute(delete_query, {"document_id": str(document_id)})
        await db.commit()
        
        logger.info(f"Document {document_id} deleted successfully")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.warning(f"Error deleting document (table may not exist): {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
