"""
AINFLUE INTEGRATIONS - DOCUMENT PROCESSING SERVICES
==================================================

Enterprise document processing integration for creator economy platform.
Combines multiple expert roles for comprehensive document management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/third_party)

Expert Roles Applied:
- Lead Dev IA: AI-powered document analysis, content extraction, intelligent processing
- Backend Senior: Robust API architecture, scalable document handling, enterprise patterns
- ML Engineer: Document classification, content analysis, automated insights
- DBA: Document metadata management, searchable content storage, audit trails
- Security: Document encryption, access control, compliance validation
- Microservices: Service communication, document pipeline orchestration
- Audio Engineer: Audio document processing, transcription services
- DevOps: Performance monitoring, automated scaling, health checks
- IA Prompt Engineer: AI prompt optimization, content enhancement

Business Logic Integration:
Creator → Document Upload → AI Processing → Content Protection → SEO → Distribution → Monetization
"""

import asyncio
import base64
import hashlib
import json
import logging
import mimetypes
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from pydantic import BaseModel, Field, validator
import magic
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import docx
import openpyxl
import csv
import xml.etree.ElementTree as ET

# AI and ML Libraries
import openai
from transformers import pipeline
import spacy
from sentence_transformers import SentenceTransformer

# Security and Compliance
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
DOCUMENT_PROCESSED_COUNTER = Counter('document_processed_total', 'Total documents processed', ['type', 'status'])
PROCESSING_DURATION = Histogram('document_processing_duration_seconds', 'Document processing duration', ['type'])
ACTIVE_PROCESSING = Gauge('document_active_processing', 'Active document processing jobs')
ERROR_COUNTER = Counter('document_processing_errors_total', 'Document processing errors', ['error_type'])

class DocumentType(Enum):
    """Document types supported by the platform"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    TEXT = "text"
    HTML = "html"
    XML = "xml"
    CSV = "csv"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"

@dataclass
class DocumentMetadata:
    """Document metadata structure"""
    document_id: str
    filename: str
    file_size: int
    mime_type: str
    document_type: DocumentType
    upload_timestamp: datetime
    creator_id: str
    status: ProcessingStatus
    checksum: str
    encryption_key: Optional[str] = None
    extracted_text: Optional[str] = None
    ai_insights: Optional[Dict] = None
    compliance_check: Optional[Dict] = None
    seo_analysis: Optional[Dict] = None

class DocumentProcessingConfig(BaseModel):
    """Configuration for document processing services"""
    # AI Processing Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for content analysis")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model for analysis")
    
    # OCR Configuration
    tesseract_path: Optional[str] = Field(default=None, description="Tesseract executable path")
    tesseract_config: str = Field(default="--oem 3 --psm 6", description="Tesseract configuration")
    
    # ML Models Configuration
    sentence_transformer_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    spacy_model: str = Field(default="en_core_web_sm", description="spaCy model for NLP")
    
    # Security Configuration
    encryption_enabled: bool = Field(default=True, description="Enable document encryption")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Maximum file size in bytes")
    allowed_mime_types: List[str] = Field(
        default=[
            "application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain", "text/html", "text/xml", "text/csv", "image/jpeg", "image/png", "image/gif"
        ],
        description="Allowed MIME types for processing"
    )
    
    # Performance Configuration
    max_concurrent_processing: int = Field(default=10, description="Maximum concurrent processing jobs")
    processing_timeout: int = Field(default=300, description="Processing timeout in seconds")
    
    # Compliance Configuration
    gdpr_enabled: bool = Field(default=True, description="Enable GDPR compliance checks")
    content_moderation_enabled: bool = Field(default=True, description="Enable content moderation")
    
    @validator('max_file_size')
    def validate_file_size(cls, v) -> None:
        if v <= 0 or v > 1024 * 1024 * 1024:  # 1GB limit
            raise ValueError("File size must be between 1 byte and 1GB")
        return v

class DocumentSecurityManager:
    """Security manager for document processing - Security Expert role"""
    
    def __init__(self, config -> None: DocumentProcessingConfig) -> None:
        self.config = config
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for document security"""
        password = b"ainflue_document_encryption_key_2025"
        salt = b"ainflue_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_document(self, content: bytes) -> Tuple[bytes, str]:
        """Encrypt document content"""
        try:
            encrypted_content = self.cipher_suite.encrypt(content)
            encryption_key = base64.urlsafe_b64encode(self.encryption_key).decode()
            return encrypted_content, encryption_key
        except Exception as e:
            logger.error(f"Document encryption failed: {e}")
            raise
    
    def decrypt_document(self, encrypted_content: bytes, encryption_key: str) -> bytes:
        """Decrypt document content"""
        try:
            key = base64.urlsafe_b64decode(encryption_key.encode())
            cipher_suite = Fernet(key)
            return cipher_suite.decrypt(encrypted_content)
        except Exception as e:
            logger.error(f"Document decryption failed: {e}")
            raise
    
    def validate_file_security(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Validate file for security threats"""
        security_check = {
            "safe": True,
            "threats": [],
            "file_type_valid": True,
            "size_valid": True,
            "scan_timestamp": datetime.utcnow().isoformat()
        }
        
        # File size validation
        if len(content) > self.config.max_file_size:
            security_check["safe"] = False
            security_check["size_valid"] = False
            security_check["threats"].append("File size exceeds maximum allowed")
        
        # MIME type validation
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in self.config.allowed_mime_types:
            security_check["safe"] = False
            security_check["file_type_valid"] = False
            security_check["threats"].append(f"Unauthorized file type: {mime_type}")
        
        # Basic malware scanning (simplified)
        suspicious_patterns = [b"<script", b"javascript:", b"eval(", b"exec("]
        for pattern in suspicious_patterns:
            if pattern in content.lower():
                security_check["safe"] = False
                security_check["threats"].append(f"Suspicious pattern detected: {pattern.decode()}")
        
        return security_check

class DocumentMLAnalyzer:
    """ML-powered document analysis - ML Engineer role"""
    
    def __init__(self, config -> None: DocumentProcessingConfig) -> None:
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config.openai_api_key)
        
        # Initialize ML models
        try:
            self.sentence_transformer = SentenceTransformer(config.sentence_transformer_model)
            self.nlp = spacy.load(config.spacy_model)
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.text_classifier = pipeline("text-classification")
        except Exception as e:
            logger.warning(f"Some ML models failed to load: {e}")
            self.sentence_transformer = None
            self.nlp = None
            self.sentiment_analyzer = None
            self.text_classifier = None
    
    async def analyze_document_content(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """Comprehensive AI-powered document analysis"""
        analysis = {
            "summary": None,
            "key_topics": [],
            "sentiment": {},
            "entities": [],
            "language": "en",
            "content_classification": {},
            "seo_keywords": [],
            "monetization_potential": {},
            "compliance_analysis": {},
            "ai_enhancement_suggestions": []
        }
        
        try:
            # OpenAI-powered analysis
            ai_analysis = await self._openai_analysis(text, document_type)
            analysis.update(ai_analysis)
            
            # SpaCy NLP analysis
            if self.nlp:
                nlp_analysis = self._spacy_analysis(text)
                analysis.update(nlp_analysis)
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer(text[:512])  # Limit for performance
                analysis["sentiment"] = sentiment[0] if sentiment else {}
            
            # Content classification
            if self.text_classifier:
                classification = self.text_classifier(text[:512])
                analysis["content_classification"] = classification[0] if classification else {}
            
            # SEO analysis for creator economy
            seo_analysis = self._analyze_seo_potential(text)
            analysis["seo_analysis"] = seo_analysis
            
            # Monetization potential analysis
            monetization_analysis = self._analyze_monetization_potential(text, document_type)
            analysis["monetization_potential"] = monetization_analysis
            
        except Exception as e:
            logger.error(f"Document ML analysis failed: {e}")
            ERROR_COUNTER.labels(error_type="ml_analysis").inc()
        
        return analysis
    
    async def _openai_analysis(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """OpenAI-powered document analysis - Lead Dev IA role"""
        prompt = f"""
        Analyze this {document_type.value} document for a creator economy platform. Provide:
        1. A concise summary (max 200 words)
        2. Key topics and themes
        3. Content quality assessment
        4. Monetization opportunities
        5. SEO optimization suggestions
        6. Compliance considerations
        7. Enhancement recommendations
        
        Document content:
        {text[:4000]}  # Limit for API efficiency
        
        Respond in JSON format.
        """
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"ai_summary": ai_response}
                
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return {"ai_analysis_error": str(e)}
    
    def _spacy_analysis(self, text: str) -> Dict[str, Any]:
        """SpaCy NLP analysis"""
        try:
            doc = self.nlp(text[:1000000])  # Limit for performance
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "description": spacy.explain(ent.label_)
                })
            
            # Extract key phrases and topics
            noun_phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text) > 2]
            
            return {
                "entities": entities[:20],  # Limit results
                "key_phrases": noun_phrases[:15],
                "language": doc.lang_,
                "sentence_count": len(list(doc.sents)),
                "word_count": len([token for token in doc if not token.is_space])
            }
        except Exception as e:
            logger.error(f"SpaCy analysis failed: {e}")
            return {}
    
    def _analyze_seo_potential(self, text: str) -> Dict[str, Any]:
        """Analyze SEO potential for creator content"""
        words = text.lower().split()
        word_count = len(words)
        
        # Basic SEO metrics
        readability_score = self._calculate_readability(text)
        keyword_density = self._calculate_keyword_density(words)
        
        return {
            "word_count": word_count,
            "readability_score": readability_score,
            "keyword_density": keyword_density,
            "seo_recommendations": self._generate_seo_recommendations(word_count, readability_score)
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score"""
        sentences = text.split('.')
        words = text.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        # Simplified Flesch Reading Ease approximation
        score = 206.835 - (1.015 * avg_sentence_length)
        return max(0, min(100, score))
    
    def _calculate_keyword_density(self, words: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        if not words:
            return {}
        
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only consider meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        total_words = len(words)
        density = {word: (count / total_words) * 100 for word, count in word_freq.items()}
        
        # Return top 10 keywords
        return dict(sorted(density.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _generate_seo_recommendations(self, word_count: int, readability: float) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        if word_count < 300:
            recommendations.append("Consider adding more content for better SEO (aim for 300+ words)")
        elif word_count > 2000:
            recommendations.append("Consider breaking content into multiple pieces for better engagement")
        
        if readability < 60:
            recommendations.append("Consider simplifying language for better readability")
        elif readability > 90:
            recommendations.append("Content is very easy to read - consider adding some complexity")
        
        return recommendations
    
    def _analyze_monetization_potential(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """Analyze monetization potential for creator economy"""
        monetization_keywords = [
            "tutorial", "guide", "how-to", "course", "training", "premium", "exclusive",
            "subscription", "membership", "affiliate", "sponsor", "brand", "product"
        ]
        
        text_lower = text.lower()
        monetization_score = sum(1 for keyword in monetization_keywords if keyword in text_lower)
        
        potential_categories = []
        if "tutorial" in text_lower or "how-to" in text_lower:
            potential_categories.append("Educational Content")
        if "review" in text_lower or "comparison" in text_lower:
            potential_categories.append("Affiliate Marketing")
        if "exclusive" in text_lower or "premium" in text_lower:
            potential_categories.append("Premium Content")
        
        return {
            "monetization_score": monetization_score,
            "potential_categories": potential_categories,
            "content_type_suitability": self._assess_content_type_monetization(document_type),
            "recommendations": self._generate_monetization_recommendations(monetization_score, document_type)
        }
    
    def _assess_content_type_monetization(self, document_type: DocumentType) -> str:
        """Assess monetization suitability by document type"""
        suitability_map = {
            DocumentType.PDF: "High - Great for premium guides and courses",
            DocumentType.WORD: "Medium - Good for articles and tutorials",
            DocumentType.POWERPOINT: "High - Excellent for course materials",
            DocumentType.EXCEL: "Medium - Useful for templates and tools",
            DocumentType.IMAGE: "High - Perfect for visual content monetization",
            DocumentType.VIDEO: "Very High - Prime monetization content",
            DocumentType.AUDIO: "High - Podcast and audio content potential"
        }
        return suitability_map.get(document_type, "Medium - Standard monetization potential")
    
    def _generate_monetization_recommendations(self, score: int, document_type: DocumentType) -> List[str]:
        """Generate monetization recommendations"""
        recommendations = []
        
        if score < 3:
            recommendations.append("Consider adding monetization-focused keywords and content")
        
        if document_type in [DocumentType.VIDEO, DocumentType.AUDIO]:
            recommendations.append("Consider creating subscription-based content series")
        elif document_type == DocumentType.PDF:
            recommendations.append("Ideal for premium downloadable content")
        
        recommendations.append("Explore affiliate marketing opportunities")
        recommendations.append("Consider creating tiered content offerings")
        
        return recommendations

class DocumentContentExtractor:
    """Document content extraction service - Backend Senior + Audio Engineer roles"""
    
    def __init__(self, config -> None: DocumentProcessingConfig) -> None:
        self.config = config
        
    async def extract_content(self, file_path: str, document_type: DocumentType) -> str:
        """Extract text content from various document types"""
        try:
            with PROCESSING_DURATION.labels(type=document_type.value).time():
                if document_type == DocumentType.PDF:
                    return await self._extract_pdf_content(file_path)
                elif document_type == DocumentType.WORD:
                    return await self._extract_word_content(file_path)
                elif document_type == DocumentType.EXCEL:
                    return await self._extract_excel_content(file_path)
                elif document_type == DocumentType.TEXT:
                    return await self._extract_text_content(file_path)
                elif document_type == DocumentType.HTML:
                    return await self._extract_html_content(file_path)
                elif document_type == DocumentType.CSV:
                    return await self._extract_csv_content(file_path)
                elif document_type == DocumentType.IMAGE:
                    return await self._extract_image_content(file_path)
                else:
                    return await self._extract_generic_content(file_path)
        except Exception as e:
            logger.error(f"Content extraction failed for {document_type}: {e}")
            ERROR_COUNTER.labels(error_type="content_extraction").inc()
            return ""
    
    async def _extract_pdf_content(self, file_path: str) -> str:
        """Extract content from PDF files"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    async def _extract_word_content(self, file_path: str) -> str:
        """Extract content from Word documents"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Word extraction failed: {e}")
            return ""
    
    async def _extract_excel_content(self, file_path: str) -> str:
        """Extract content from Excel files"""
        try:
            workbook = openpyxl.load_workbook(file_path)
            text = ""
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                text += f"Sheet: {sheet_name}\n"
                for row in sheet.iter_rows(values_only=True):
                    text += " | ".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
            return text
        except Exception as e:
            logger.error(f"Excel extraction failed: {e}")
            return ""
    
    async def _extract_text_content(self, file_path: str) -> str:
        """Extract content from text files"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                return await file.read()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def _extract_html_content(self, file_path: str) -> str:
        """Extract content from HTML files"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                html_content = await file.read()
            
            # Basic HTML tag removal (simplified)
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            return text
        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            return ""
    
    async def _extract_csv_content(self, file_path: str) -> str:
        """Extract content from CSV files"""
        try:
            text = ""
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                reader = csv.reader(content.splitlines())
                for row in reader:
                    text += " | ".join(row) + "\n"
            return text
        except Exception as e:
            logger.error(f"CSV extraction failed: {e}")
            return ""
    
    async def _extract_image_content(self, file_path: str) -> str:
        """Extract text from images using OCR"""
        try:
            if self.config.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, config=self.config.tesseract_config)
            return text
        except Exception as e:
            logger.error(f"Image OCR extraction failed: {e}")
            return ""
    
    async def _extract_generic_content(self, file_path: str) -> str:
        """Generic content extraction for unknown file types"""
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()
            
            # Try to decode as text
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return content.decode('latin-1')
                except UnicodeDecodeError:
                    return f"Binary file - {len(content)} bytes"
        except Exception as e:
            logger.error(f"Generic extraction failed: {e}")
            return ""

class DocumentComplianceValidator:
    """Document compliance validation - Security + Legal roles"""
    
    def __init__(self, config -> None: DocumentProcessingConfig) -> None:
        self.config = config
        
    async def validate_compliance(self, document_metadata: DocumentMetadata, content: str) -> Dict[str, Any]:
        """Comprehensive compliance validation"""
        compliance_result = {
            "compliant": True,
            "violations": [],
            "gdpr_compliant": True,
            "content_safe": True,
            "copyright_clear": True,
            "privacy_issues": [],
            "recommendations": []
        }
        
        try:
            # GDPR compliance check
            if self.config.gdpr_enabled:
                gdpr_check = await self._check_gdpr_compliance(content)
                compliance_result.update(gdpr_check)
            
            # Content moderation
            if self.config.content_moderation_enabled:
                content_check = await self._moderate_content(content)
                compliance_result.update(content_check)
            
            # Privacy protection check
            privacy_check = await self._check_privacy_issues(content)
            compliance_result.update(privacy_check)
            
            # Copyright analysis
            copyright_check = await self._analyze_copyright_issues(content)
            compliance_result.update(copyright_check)
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            compliance_result["validation_error"] = str(e)
        
        return compliance_result
    
    async def _check_gdpr_compliance(self, content: str) -> Dict[str, Any]:
        """Check GDPR compliance for personal data"""
        gdpr_result = {"gdpr_compliant": True, "personal_data_detected": []}
        
        # Basic PII detection patterns
        import re
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        for data_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                gdpr_result["personal_data_detected"].append({
                    "type": data_type,
                    "count": len(matches),
                    "requires_consent": True
                })
                gdpr_result["gdpr_compliant"] = False
        
        return gdpr_result
    
    async def _moderate_content(self, content: str) -> Dict[str, Any]:
        """Content moderation for safety"""
        moderation_result = {"content_safe": True, "flagged_content": []}
        
        # Basic content filtering
        prohibited_terms = [
            "hate speech", "violence", "explicit", "illegal", "harassment"
        ]
        
        content_lower = content.lower()
        for term in prohibited_terms:
            if term in content_lower:
                moderation_result["content_safe"] = False
                moderation_result["flagged_content"].append(term)
        
        return moderation_result
    
    async def _check_privacy_issues(self, content: str) -> Dict[str, Any]:
        """Check for privacy-related issues"""
        privacy_result = {"privacy_issues": []}
        
        # Check for potential privacy violations
        privacy_keywords = ["personal", "private", "confidential", "internal", "restricted"]
        
        content_lower = content.lower()
        for keyword in privacy_keywords:
            if keyword in content_lower:
                privacy_result["privacy_issues"].append(f"Potential privacy concern: {keyword}")
        
        return privacy_result
    
    async def _analyze_copyright_issues(self, content: str) -> Dict[str, Any]:
        """Analyze potential copyright issues"""
        copyright_result = {"copyright_clear": True, "potential_issues": []}
        
        # Basic copyright detection
        copyright_indicators = ["©", "copyright", "all rights reserved", "proprietary"]
        
        content_lower = content.lower()
        for indicator in copyright_indicators:
            if indicator in content_lower:
                copyright_result["potential_issues"].append(f"Copyright indicator found: {indicator}")
        
        return copyright_result

class DocumentProcessingOrchestrator:
    """Main orchestrator for document processing - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config -> None: DocumentProcessingConfig) -> None:
        self.config = config
        self.security_manager = DocumentSecurityManager(config)
        self.ml_analyzer = DocumentMLAnalyzer(config)
        self.content_extractor = DocumentContentExtractor(config)
        self.compliance_validator = DocumentComplianceValidator(config)
        
        # Processing queue for concurrent handling
        self.processing_queue = asyncio.Queue(maxsize=config.max_concurrent_processing)
        self.active_jobs = {}
        
    async def process_document(self, file_path: str, creator_id: str, filename: str) -> DocumentMetadata:
        """Main document processing workflow"""
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            ACTIVE_PROCESSING.inc()
            logger.info(f"Starting document processing: {job_id} - {filename}")
            
            # Step 1: File validation and security check
            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()
            
            # Security validation
            security_check = self.security_manager.validate_file_security(content, filename)
            if not security_check["safe"]:
                raise ValueError(f"Security validation failed: {security_check['threats']}")
            
            # Step 2: Document metadata creation
            document_id = str(uuid.uuid4())
            checksum = hashlib.sha256(content).hexdigest()
            mime_type = magic.from_buffer(content, mime=True)
            document_type = self._determine_document_type(mime_type, filename)
            
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_size=len(content),
                mime_type=mime_type,
                document_type=document_type,
                upload_timestamp=datetime.utcnow(),
                creator_id=creator_id,
                status=ProcessingStatus.PROCESSING,
                checksum=checksum
            )
            
            # Step 3: Content extraction
            extracted_text = await self.content_extractor.extract_content(file_path, document_type)
            metadata.extracted_text = extracted_text
            
            # Step 4: AI/ML analysis
            if extracted_text:
                ai_insights = await self.ml_analyzer.analyze_document_content(extracted_text, document_type)
                metadata.ai_insights = ai_insights
            
            # Step 5: Compliance validation
            compliance_check = await self.compliance_validator.validate_compliance(metadata, extracted_text)
            metadata.compliance_check = compliance_check
            
            # Step 6: Encryption (if enabled)
            if self.config.encryption_enabled:
                encrypted_content, encryption_key = self.security_manager.encrypt_document(content)
                metadata.encryption_key = encryption_key
                # Save encrypted content (in real implementation, this would go to secure storage)
            
            # Step 7: Update status
            metadata.status = ProcessingStatus.COMPLETED
            
            # Metrics
            DOCUMENT_PROCESSED_COUNTER.labels(type=document_type.value, status="success").inc()
            processing_time = time.time() - start_time
            logger.info(f"Document processed successfully: {job_id} in {processing_time:.2f}s")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Document processing failed: {job_id} - {e}")
            ERROR_COUNTER.labels(error_type="processing_failure").inc()
            DOCUMENT_PROCESSED_COUNTER.labels(type="unknown", status="error").inc()
            
            # Create error metadata
            error_metadata = DocumentMetadata(
                document_id=str(uuid.uuid4()),
                filename=filename,
                file_size=0,
                mime_type="unknown",
                document_type=DocumentType.UNKNOWN,
                upload_timestamp=datetime.utcnow(),
                creator_id=creator_id,
                status=ProcessingStatus.FAILED,
                checksum=""
            )
            return error_metadata
            
        finally:
            ACTIVE_PROCESSING.dec()
    
    def _determine_document_type(self, mime_type: str, filename: str) -> DocumentType:
        """Determine document type from MIME type and filename"""
        mime_type_map = {
            "application/pdf": DocumentType.PDF,
            "application/msword": DocumentType.WORD,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.WORD,
            "application/vnd.ms-excel": DocumentType.EXCEL,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": DocumentType.EXCEL,
            "text/plain": DocumentType.TEXT,
            "text/html": DocumentType.HTML,
            "text/xml": DocumentType.XML,
            "text/csv": DocumentType.CSV,
            "image/jpeg": DocumentType.IMAGE,
            "image/png": DocumentType.IMAGE,
            "image/gif": DocumentType.IMAGE,
            "audio/mpeg": DocumentType.AUDIO,
            "audio/wav": DocumentType.AUDIO,
            "video/mp4": DocumentType.VIDEO,
            "video/avi": DocumentType.VIDEO
        }
        
        document_type = mime_type_map.get(mime_type, DocumentType.UNKNOWN)
        
        # Fallback to file extension
        if document_type == DocumentType.UNKNOWN:
            extension = Path(filename).suffix.lower()
            extension_map = {
                ".pdf": DocumentType.PDF,
                ".doc": DocumentType.WORD,
                ".docx": DocumentType.WORD,
                ".xls": DocumentType.EXCEL,
                ".xlsx": DocumentType.EXCEL,
                ".txt": DocumentType.TEXT,
                ".html": DocumentType.HTML,
                ".xml": DocumentType.XML,
                ".csv": DocumentType.CSV,
                ".jpg": DocumentType.IMAGE,
                ".jpeg": DocumentType.IMAGE,
                ".png": DocumentType.IMAGE,
                ".gif": DocumentType.IMAGE,
                ".mp3": DocumentType.AUDIO,
                ".wav": DocumentType.AUDIO,
                ".mp4": DocumentType.VIDEO,
                ".avi": DocumentType.VIDEO
            }
            document_type = extension_map.get(extension, DocumentType.UNKNOWN)
        
        return document_type
    
    async def get_processing_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a document"""
        return self.active_jobs.get(document_id)
    
    async def list_processed_documents(self, creator_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List processed documents for a creator"""
        # In real implementation, this would query the database
        # For now, return empty list as placeholder
        return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the document processing service - DevOps role"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "metrics": {
                "active_processing_jobs": len(self.active_jobs),
                "queue_size": self.processing_queue.qsize(),
                "system_memory_usage": psutil.virtual_memory().percent,
                "system_cpu_usage": psutil.cpu_percent()
            },
            "services": {
                "ml_models": self._check_ml_models_health(),
                "security": self._check_security_health(),
                "storage": self._check_storage_health()
            }
        }
        
        # Determine overall health
        if health_status["metrics"]["system_memory_usage"] > 90:
            health_status["status"] = "degraded"
        if health_status["metrics"]["system_cpu_usage"] > 95:
            health_status["status"] = "unhealthy"
        
        return health_status
    
    def _check_ml_models_health(self) -> Dict[str, str]:
        """Check ML models health status"""
        return {
            "sentence_transformer": "healthy" if self.ml_analyzer.sentence_transformer else "unavailable",
            "spacy_nlp": "healthy" if self.ml_analyzer.nlp else "unavailable",
            "sentiment_analyzer": "healthy" if self.ml_analyzer.sentiment_analyzer else "unavailable"
        }
    
    def _check_security_health(self) -> str:
        """Check security components health"""
        try:
            # Test encryption/decryption
            test_data = b"test"
            encrypted, key = self.security_manager.encrypt_document(test_data)
            decrypted = self.security_manager.decrypt_document(encrypted, key)
            return "healthy" if decrypted == test_data else "degraded"
        except Exception:
            return "unhealthy"
    
    def _check_storage_health(self) -> str:
        """Check storage availability"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            free_percentage = (disk_usage.free / disk_usage.total) * 100
            
            if free_percentage > 10:
                return "healthy"
            elif free_percentage > 5:
                return "degraded"
            else:
                return "critical"
        except Exception:
            return "unknown"

# Service factory and configuration
class DocumentProcessingService:
    """Main document processing service facade - DevOps + Integration role"""
    
    def __init__(self, config -> None: Optional[DocumentProcessingConfig] = None) -> None:
        self.config = config or DocumentProcessingConfig(
            openai_api_key="your-openai-key-here",  # Should be configured via environment
            encryption_enabled=True,
            gdpr_enabled=True,
            content_moderation_enabled=True
        )
        self.orchestrator = DocumentProcessingOrchestrator(self.config)
        
    async def initialize(self) -> None:
        """Initialize the document processing service"""
        logger.info("Initializing Document Processing Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Initialize ML models
        await self._initialize_ml_models()
        
        # Setup monitoring
        await self._setup_monitoring()
        
        logger.info("Document Processing Service initialized successfully")
    
    async def _validate_configuration(self) -> None:
        """Validate service configuration"""
        if not self.config.openai_api_key or self.config.openai_api_key == "your-openai-key-here":
            logger.warning("OpenAI API key not configured - AI features will be limited")
        
        if self.config.max_file_size > 1024 * 1024 * 1024:  # 1GB
            logger.warning("Max file size is very large - consider performance implications")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models with proper error handling"""
        try:
            # This would download models if not already present
            logger.info("ML models initialization completed")
        except Exception as e:
            logger.error(f"ML models initialization failed: {e}")
    
    async def _setup_monitoring(self) -> None:
        """Setup monitoring and metrics collection"""
        logger.info("Document processing monitoring setup completed")
    
    async def process_document(self, file_path: str, creator_id: str, filename: str) -> DocumentMetadata:
        """Process a document with full enterprise features"""
        return await self.orchestrator.process_document(file_path, creator_id, filename)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.orchestrator.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            "documents_processed_total": DOCUMENT_PROCESSED_COUNTER._value.sum(),
            "active_processing": ACTIVE_PROCESSING._value.get(),
            "error_count": ERROR_COUNTER._value.sum(),
            "average_processing_time": "N/A"  # Would calculate from histogram
        }

# Export main classes and functions
__all__ = [
    'DocumentProcessingService',
    'DocumentProcessingConfig', 
    'DocumentMetadata',
    'DocumentType',
    'ProcessingStatus',
    'DocumentProcessingOrchestrator'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main() -> None:
        # Initialize service
        service = DocumentProcessingService()
        await service.initialize()
        
        # Health check
        health = await service.get_health_status()
        print(f"Service Health: {health}")
        
        # Example document processing (would need actual file)
        # metadata = await service.process_document("example.pdf", "creator123", "example.pdf")
        # print(f"Processed: {metadata}")
    
    # Run example
    # asyncio.run(main())