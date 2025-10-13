"""
Medical Document Processing Service
OCR, AI analysis, translation for uploaded medical documents
"""
import logging
import hashlib
import mimetypes
from typing import Dict, Optional, List
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """
    Service for processing medical documents with OCR and AI analysis
    
    Features:
    - OCR extraction (any language)
    - AI analysis of medical content
    - Automatic translation
    - Structured data extraction
    - Abnormality detection
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        
    async def process_document(
        self, 
        file_content: bytes,
        filename: str,
        document_type: str,
        patient_id: UUID
    ) -> Dict:
        """
        Process uploaded medical document
        
        Steps:
        1. Extract text (OCR if image/PDF)
        2. Detect language
        3. Translate to English for analysis
        4. Analyze medical content
        5. Extract structured data
        6. Detect abnormalities
        7. Generate recommendations
        """
        
        # Step 1: Detect file type and extract text
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        ocr_result = await self._extract_text(file_content, mime_type)
        
        # Step 2: Detect language
        detected_language = self._detect_language(ocr_result['text'])
        
        # Step 3: Translate if not English
        text_for_analysis = ocr_result['text']
        if detected_language != 'en':
            text_for_analysis = await self._translate_text(
                ocr_result['text'], 
                detected_language, 
                'en'
            )
        
        # Step 4: AI Analysis based on document type
        ai_analysis = await self._analyze_document_content(
            text_for_analysis,
            document_type,
            ocr_result.get('structured_data', {})
        )
        
        # Step 5: Check for abnormalities
        abnormalities = self._detect_abnormalities(
            ai_analysis.get('extracted_values', [])
        )
        
        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(
            document_type,
            ai_analysis,
            abnormalities
        )
        
        return {
            'ocr_text': ocr_result['text'],
            'ocr_confidence': ocr_result.get('confidence', 0.0),
            'detected_language': detected_language,
            'ai_analysis': {
                'document_type': document_type,
                'extracted_values': ai_analysis.get('extracted_values', []),
                'key_findings': ai_analysis.get('key_findings', []),
                'abnormal_values': abnormalities,
                'structured_data': ai_analysis.get('structured_data', {}),
                'recommendations': recommendations,
                'requires_attention': len(abnormalities) > 0,
                'urgency_level': self._calculate_urgency(abnormalities)
            }
        }
    
    async def _extract_text(self, file_content: bytes, mime_type: str) -> Dict:
        """
        Extract text from document using OCR
        
        Supports:
        - Images (JPEG, PNG): Tesseract OCR
        - PDF: PyPDF2 + OCR for scanned PDFs
        - DICOM (medical imaging): pydicom
        """
        
        if mime_type.startswith('image/'):
            return await self._ocr_image(file_content)
        elif mime_type == 'application/pdf':
            return await self._extract_from_pdf(file_content)
        elif 'dicom' in mime_type:
            return await self._extract_from_dicom(file_content)
        else:
            # Try to decode as text
            try:
                text = file_content.decode('utf-8')
                return {'text': text, 'confidence': 1.0}
            except:
                return {'text': '', 'confidence': 0.0}
    
    async def _ocr_image(self, image_bytes: bytes) -> Dict:
        """
        OCR using Tesseract
        """
        try:
            from PIL import Image
            import pytesseract
            import io
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR with multiple languages
            text = pytesseract.image_to_string(
                image, 
                lang='eng+fra+ara+spa+deu+zho_sim'  # Multiple languages
            )
            
            # Get confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text,
                'confidence': avg_confidence / 100.0
            }
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return {'text': '', 'confidence': 0.0}
    
    async def _extract_from_pdf(self, pdf_bytes: bytes) -> Dict:
        """
        Extract text from PDF
        """
        try:
            import PyPDF2
            import io
            
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # If no text extracted, it might be a scanned PDF
            if len(text.strip()) < 50:
                # Convert PDF pages to images and OCR
                return await self._ocr_pdf_pages(pdf_bytes)
            
            return {
                'text': text,
                'confidence': 0.95  # High confidence for text PDFs
            }
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {'text': '', 'confidence': 0.0}
    
    async def _ocr_pdf_pages(self, pdf_bytes: bytes) -> Dict:
        """
        OCR scanned PDF pages
        """
        try:
            from pdf2image import convert_from_bytes
            import pytesseract
            
            images = convert_from_bytes(pdf_bytes)
            
            full_text = ""
            confidences = []
            
            for image in images:
                text = pytesseract.image_to_string(
                    image,
                    lang='eng+fra+ara+spa+deu'
                )
                full_text += text + "\n"
                
                # Get confidence for this page
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                page_confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                if page_confidences:
                    confidences.append(sum(page_confidences) / len(page_confidences))
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence / 100.0
            }
        except Exception as e:
            logger.error(f"PDF OCR error: {e}")
            return {'text': '', 'confidence': 0.0}
    
    async def _extract_from_dicom(self, dicom_bytes: bytes) -> Dict:
        """
        Extract metadata and any text from DICOM medical images
        """
        try:
            import pydicom
            import io
            
            dicom = pydicom.dcmread(io.BytesIO(dicom_bytes))
            
            # Extract relevant metadata
            metadata = {
                'patient_id': str(dicom.get('PatientID', '')),
                'study_date': str(dicom.get('StudyDate', '')),
                'modality': str(dicom.get('Modality', '')),
                'body_part': str(dicom.get('BodyPartExamined', '')),
                'study_description': str(dicom.get('StudyDescription', ''))
            }
            
            text = f"DICOM Medical Image\n"
            text += f"Modality: {metadata['modality']}\n"
            text += f"Body Part: {metadata['body_part']}\n"
            text += f"Study: {metadata['study_description']}\n"
            
            return {
                'text': text,
                'confidence': 1.0,
                'structured_data': metadata
            }
        except Exception as e:
            logger.error(f"DICOM extraction error: {e}")
            return {'text': '', 'confidence': 0.0}
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language of text
        """
        try:
            from langdetect import detect
            return detect(text)
        except:
            return 'en'  # Default to English
    
    async def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using translation service
        
        In production, this will call iacherie translation API
        For now, using Google Translate as placeholder
        """
        try:
            from deep_translator import GoogleTranslator
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Translate in chunks (Google has character limits)
            max_chunk = 4500
            chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
            
            translated_chunks = []
            for chunk in chunks:
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
            
            return ' '.join(translated_chunks)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original if translation fails
    
    async def _analyze_document_content(
        self, 
        text: str, 
        document_type: str,
        structured_data: Dict
    ) -> Dict:
        """
        AI analysis of medical document content
        
        Extracts:
        - Lab values
        - Medications
        - Diagnoses
        - Procedures
        - Key findings
        """
        import re
        
        analysis = {
            'extracted_values': [],
            'key_findings': [],
            'structured_data': structured_data
        }
        
        # Extract based on document type
        if document_type in ['blood_test', 'lab_result']:
            analysis['extracted_values'] = self._extract_lab_values(text)
            analysis['key_findings'] = self._extract_key_findings_lab(text)
        
        elif document_type == 'prescription':
            analysis['medications'] = self._extract_medications(text)
            analysis['key_findings'] = [
                f"Prescription contains {len(analysis['medications'])} medication(s)"
            ]
        
        elif document_type in ['xray', 'mri', 'ct_scan']:
            analysis['key_findings'] = self._extract_imaging_findings(text)
        
        elif document_type == 'dialysis_report':
            analysis['extracted_values'] = self._extract_dialysis_metrics(text)
            analysis['key_findings'] = self._extract_key_findings_dialysis(text)
        
        return analysis
    
    def _extract_lab_values(self, text: str) -> List[Dict]:
        """
        Extract laboratory values from text
        """
        import re
        
        values = []
        
        # Common lab test patterns
        patterns = [
            # Pattern: "Test Name: Value Unit (Reference Range)"
            r'([A-Z][A-Za-z\s]+):\s*([\d.]+)\s*([a-zA-Z/]+)?\s*(?:\(([^)]+)\))?',
            # Pattern: "Test Name Value Unit"
            r'([A-Z][A-Za-z\s]+)\s+([\d.]+)\s+([a-zA-Z/]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                value_dict = {
                    'parameter': match.group(1).strip(),
                    'value': float(match.group(2)),
                    'unit': match.group(3).strip() if match.group(3) else '',
                }
                if len(match.groups()) > 3 and match.group(4):
                    value_dict['reference_range'] = match.group(4).strip()
                
                values.append(value_dict)
        
        return values
    
    def _extract_medications(self, text: str) -> List[Dict]:
        """
        Extract medication information
        """
        import re
        
        medications = []
        
        # Pattern for medication with dosage
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([\d.]+\s*(?:mg|g|ml|mcg))\s*(?:(\d+x?\s*(?:daily|per day|times? a day)))?'
        
        matches = re.finditer(pattern, text)
        for match in matches:
            medications.append({
                'name': match.group(1),
                'dosage': match.group(2),
                'frequency': match.group(3) if match.group(3) else 'as prescribed'
            })
        
        return medications
    
    def _extract_imaging_findings(self, text: str) -> List[str]:
        """
        Extract key findings from imaging reports
        """
        findings = []
        
        # Look for impression/conclusion section
        import re
        impression_match = re.search(r'(?:IMPRESSION|CONCLUSION|FINDINGS):\s*(.+?)(?:\n\n|$)', text, re.DOTALL)
        if impression_match:
            impression_text = impression_match.group(1)
            # Split into sentences
            sentences = re.split(r'[.!?]+', impression_text)
            findings = [s.strip() for s in sentences if s.strip()]
        
        return findings[:5]  # Top 5 findings
    
    def _extract_dialysis_metrics(self, text: str) -> List[Dict]:
        """
        Extract dialysis session metrics
        """
        import re
        
        metrics = []
        
        # Common dialysis parameters
        patterns = {
            'ultrafiltration': r'(?:UF|Ultrafiltration):\s*([\d.]+)\s*([Ll]|kg)',
            'duration': r'(?:Duration|Time):\s*([\d.]+)\s*(?:hours?|hrs?|h)',
            'blood_flow': r'(?:Blood Flow|QB):\s*([\d.]+)\s*(?:ml/min|mL/min)',
            'dialysate_flow': r'(?:Dialysate Flow|QD):\s*([\d.]+)\s*(?:ml/min|mL/min)',
        }
        
        for param, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics.append({
                    'parameter': param,
                    'value': float(match.group(1)),
                    'unit': match.group(2) if len(match.groups()) > 1 else ''
                })
        
        return metrics
    
    def _extract_key_findings_lab(self, text: str) -> List[str]:
        """
        Extract key findings from lab reports
        """
        findings = []
        
        # Look for abnormal flags
        if 'high' in text.lower() or 'elevated' in text.lower():
            findings.append("Elevated values detected")
        if 'low' in text.lower() or 'decreased' in text.lower():
            findings.append("Decreased values detected")
        if 'critical' in text.lower():
            findings.append("Critical values present")
        
        return findings
    
    def _extract_key_findings_dialysis(self, text: str) -> List[str]:
        """
        Extract key findings from dialysis reports
        """
        findings = []
        
        if 'complications' in text.lower():
            findings.append("Complications noted during session")
        if 'hypotension' in text.lower():
            findings.append("Hypotension occurred")
        if 'completed successfully' in text.lower():
            findings.append("Session completed without issues")
        
        return findings
    
    def _detect_abnormalities(self, extracted_values: List[Dict]) -> List[Dict]:
        """
        Detect abnormal values based on reference ranges
        
        Reference ranges for common tests
        """
        
        # Reference ranges database (simplified)
        reference_ranges = {
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'hemoglobin': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL'},
            'hematocrit': {'min': 38.8, 'max': 50.0, 'unit': '%'},
            'wbc': {'min': 4.5, 'max': 11.0, 'unit': '10^9/L'},
            'platelets': {'min': 150, 'max': 400, 'unit': '10^9/L'},
            'creatinine': {'min': 0.7, 'max': 1.3, 'unit': 'mg/dL'},
            'bun': {'min': 7, 'max': 20, 'unit': 'mg/dL'},
            'alt': {'min': 7, 'max': 56, 'unit': 'U/L'},
            'ast': {'min': 10, 'max': 40, 'unit': 'U/L'},
        }
        
        abnormalities = []
        
        for value in extracted_values:
            param = value.get('parameter', '').lower()
            val = value.get('value')
            
            # Check if we have reference range for this parameter
            for key, ranges in reference_ranges.items():
                if key in param:
                    if val < ranges['min']:
                        abnormalities.append({
                            'parameter': value['parameter'],
                            'value': val,
                            'normal_range': f"{ranges['min']}-{ranges['max']} {ranges['unit']}",
                            'severity': 'low',
                            'deviation': ((ranges['min'] - val) / ranges['min']) * 100
                        })
                    elif val > ranges['max']:
                        abnormalities.append({
                            'parameter': value['parameter'],
                            'value': val,
                            'normal_range': f"{ranges['min']}-{ranges['max']} {ranges['unit']}",
                            'severity': 'high',
                            'deviation': ((val - ranges['max']) / ranges['max']) * 100
                        })
                    break
        
        return abnormalities
    
    def _generate_recommendations(
        self,
        document_type: str,
        ai_analysis: Dict,
        abnormalities: List[Dict]
    ) -> List[str]:
        """
        Generate recommendations based on analysis
        """
        recommendations = []
        
        if len(abnormalities) == 0:
            recommendations.append("All values appear to be within normal ranges.")
            recommendations.append("Continue regular monitoring as prescribed.")
        else:
            recommendations.append(f"Found {len(abnormalities)} abnormal value(s) requiring attention.")
            
            # Check severity
            high_deviations = [a for a in abnormalities if a.get('deviation', 0) > 50]
            if high_deviations:
                recommendations.append("URGENT: Some values show significant deviation. Consult doctor immediately.")
            else:
                recommendations.append("Discuss these results with your doctor at next appointment.")
        
        if document_type == 'dialysis_report':
            recommendations.append("Maintain adequate fluid and dietary restrictions between sessions.")
        
        recommendations.append("This is an AI preliminary analysis. Always consult healthcare professional for medical decisions.")
        
        return recommendations
    
    def _calculate_urgency(self, abnormalities: List[Dict]) -> str:
        """
        Calculate urgency level based on abnormalities
        """
        if not abnormalities:
            return 'normal'
        
        # Check for critical deviations
        critical = any(a.get('deviation', 0) > 100 for a in abnormalities)
        if critical:
            return 'critical'
        
        severe = any(a.get('deviation', 0) > 50 for a in abnormalities)
        if severe:
            return 'urgent'
        
        if len(abnormalities) >= 3:
            return 'elevated'
        
        return 'elevated'
    
    async def share_document_anonymously(
        self,
        document_id: UUID,
        share_reason: str,
        specific_questions: Optional[List[str]] = None
    ) -> UUID:
        """
        Share document anonymously for community review
        
        Returns anonymous_share_id for tracking
        """
        anonymous_share_id = uuid4()
        
        # Update document record
        # In real implementation, update database
        logger.info(f"Document {document_id} shared anonymously as {anonymous_share_id}")
        logger.info(f"Reason: {share_reason}")
        if specific_questions:
            logger.info(f"Questions: {specific_questions}")
        
        return anonymous_share_id
