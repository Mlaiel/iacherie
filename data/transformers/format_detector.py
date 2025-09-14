"""Format Detector - Intelligent format detection with ML for IA Influencer Agent Platform
========================================================================================

Advanced format detection engine using machine learning, magic bytes analysis,
and content inspection for accurate file type identification and validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, BinaryIO
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import hashlib
import mimetypes
import struct
import re

logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Format detection methods."""
    
    MAGIC_BYTES = "magic_bytes"
    FILE_EXTENSION = "file_extension"
    MIME_TYPE = "mime_type"
    CONTENT_ANALYSIS = "content_analysis"
    ML_PREDICTION = "ml_prediction"
    HYBRID = "hybrid"


class FormatCategory(Enum):
    """Format categories."""
    
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    DATA = "data"
    TEXT = "text"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence levels for detection."""
    
    VERY_LOW = "very_low"      # 0-20%
    LOW = "low"                # 20-40%
    MEDIUM = "medium"          # 40-70%
    HIGH = "high"              # 70-90%
    VERY_HIGH = "very_high"    # 90-100%


@dataclass
class FormatSignature:
    """Format signature definition."""
    
    format_name: str
    category: FormatCategory
    magic_bytes: List[bytes]
    file_extensions: List[str]
    mime_types: List[str]
    offset: int = 0  # Byte offset for magic bytes
    description: str = ""
    is_container: bool = False
    sub_formats: List[str] = field(default_factory=list)


@dataclass
class DetectionResult:
    """Format detection result."""
    
    detected_format: str
    category: FormatCategory
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    detection_method: DetectionMethod
    alternative_formats: List[Tuple[str, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_passed: bool = True
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0


@dataclass
class ContentAnalysis:
    """Content analysis result."""
    
    file_size: int
    entropy: float  # Measure of randomness
    ascii_ratio: float  # Ratio of ASCII characters
    null_byte_ratio: float
    compression_detected: bool
    encryption_detected: bool
    text_patterns: List[str] = field(default_factory=list)
    binary_patterns: List[str] = field(default_factory=list)
    structure_indicators: Dict[str, Any] = field(default_factory=dict)


class FormatDetector:
    """Intelligent format detection engine with ML capabilities."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize format detector with configuration."""
        self.config = config or {}
        
        # Format signatures database
        self.format_signatures = {}
        self._load_format_signatures()
        
        # Magic bytes lookup for fast detection
        self.magic_bytes_index = {}
        self._build_magic_bytes_index()
        
        # ML models (placeholders)
        self.ml_models = {}
        self._initialize_ml_models()
        
        # Detection statistics
        self.detection_stats = {
            "total_detections": 0,
            "method_usage": {},
            "accuracy_scores": [],
            "processing_times": []
        }
        
        logger.info("FormatDetector initialized")
    
    def _load_format_signatures(self) -> None:
        """Load format signatures for known file types."""
        signatures = [
            # Audio formats
            FormatSignature(
                format_name="mp3",
                category=FormatCategory.AUDIO,
                magic_bytes=[b'\xFF\xFB', b'ID3'],
                file_extensions=[".mp3"],
                mime_types=["audio/mpeg", "audio/mp3"],
                description="MPEG Audio Layer III"
            ),
            FormatSignature(
                format_name="wav",
                category=FormatCategory.AUDIO,
                magic_bytes=[b'RIFF'],
                file_extensions=[".wav"],
                mime_types=["audio/wav", "audio/wave"],
                description="Waveform Audio File Format"
            ),
            FormatSignature(
                format_name="flac",
                category=FormatCategory.AUDIO,
                magic_bytes=[b'fLaC'],
                file_extensions=[".flac"],
                mime_types=["audio/flac"],
                description="Free Lossless Audio Codec"
            ),
            
            # Video formats
            FormatSignature(
                format_name="mp4",
                category=FormatCategory.VIDEO,
                magic_bytes=[b'ftyp'],
                file_extensions=[".mp4", ".m4v"],
                mime_types=["video/mp4"],
                offset=4,
                description="MPEG-4 Video",
                is_container=True
            ),
            FormatSignature(
                format_name="avi",
                category=FormatCategory.VIDEO,
                magic_bytes=[b'RIFF', b'AVI '],
                file_extensions=[".avi"],
                mime_types=["video/avi", "video/x-msvideo"],
                description="Audio Video Interleave"
            ),
            FormatSignature(
                format_name="mov",
                category=FormatCategory.VIDEO,
                magic_bytes=[b'moov', b'mdat', b'free'],
                file_extensions=[".mov", ".qt"],
                mime_types=["video/quicktime"],
                description="QuickTime Movie"
            ),
            
            # Image formats
            FormatSignature(
                format_name="jpeg",
                category=FormatCategory.IMAGE,
                magic_bytes=[b'\xFF\xD8\xFF'],
                file_extensions=[".jpg", ".jpeg"],
                mime_types=["image/jpeg"],
                description="JPEG Image"
            ),
            FormatSignature(
                format_name="png",
                category=FormatCategory.IMAGE,
                magic_bytes=[b'\x89PNG\r\n\x1a\n'],
                file_extensions=[".png"],
                mime_types=["image/png"],
                description="Portable Network Graphics"
            ),
            FormatSignature(
                format_name="gif",
                category=FormatCategory.IMAGE,
                magic_bytes=[b'GIF87a', b'GIF89a'],
                file_extensions=[".gif"],
                mime_types=["image/gif"],
                description="Graphics Interchange Format"
            ),
            FormatSignature(
                format_name="webp",
                category=FormatCategory.IMAGE,
                magic_bytes=[b'RIFF', b'WEBP'],
                file_extensions=[".webp"],
                mime_types=["image/webp"],
                description="WebP Image Format"
            ),
            
            # Document formats
            FormatSignature(
                format_name="pdf",
                category=FormatCategory.DOCUMENT,
                magic_bytes=[b'%PDF'],
                file_extensions=[".pdf"],
                mime_types=["application/pdf"],
                description="Portable Document Format"
            ),
            FormatSignature(
                format_name="docx",
                category=FormatCategory.DOCUMENT,
                magic_bytes=[b'PK\x03\x04'],
                file_extensions=[".docx"],
                mime_types=["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
                description="Microsoft Word Document"
            ),
            
            # Archive formats
            FormatSignature(
                format_name="zip",
                category=FormatCategory.ARCHIVE,
                magic_bytes=[b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
                file_extensions=[".zip"],
                mime_types=["application/zip"],
                description="ZIP Archive"
            ),
            FormatSignature(
                format_name="rar",
                category=FormatCategory.ARCHIVE,
                magic_bytes=[b'Rar!\x1a\x07\x00', b'Rar!\x1a\x07\x01\x00'],
                file_extensions=[".rar"],
                mime_types=["application/x-rar-compressed"],
                description="RAR Archive"
            ),
            
            # Text formats
            FormatSignature(
                format_name="html",
                category=FormatCategory.TEXT,
                magic_bytes=[b'<!DOCTYPE html', b'<html', b'<HTML'],
                file_extensions=[".html", ".htm"],
                mime_types=["text/html"],
                description="HyperText Markup Language"
            ),
            FormatSignature(
                format_name="xml",
                category=FormatCategory.TEXT,
                magic_bytes=[b'<?xml'],
                file_extensions=[".xml"],
                mime_types=["application/xml", "text/xml"],
                description="Extensible Markup Language"
            ),
            FormatSignature(
                format_name="json",
                category=FormatCategory.TEXT,
                magic_bytes=[b'{', b'['],
                file_extensions=[".json"],
                mime_types=["application/json"],
                description="JavaScript Object Notation"
            )
        ]
        
        for signature in signatures:
            self.format_signatures[signature.format_name] = signature
    
    def _build_magic_bytes_index(self) -> None:
        """Build index for fast magic bytes lookup."""
        for format_name, signature in self.format_signatures.items():
            for magic_bytes in signature.magic_bytes:
                key = magic_bytes[:4]  # Use first 4 bytes as key
                if key not in self.magic_bytes_index:
                    self.magic_bytes_index[key] = []
                self.magic_bytes_index[key].append((format_name, magic_bytes, signature.offset))
    
    def _initialize_ml_models(self) -> None:
        """Initialize ML models for format detection."""
        # Placeholder for ML model initialization
        # In production, would load trained models
        self.ml_models = {
            "content_classifier": None,  # Content-based classification
            "entropy_analyzer": None,    # Entropy-based detection
            "pattern_recognizer": None   # Pattern recognition model
        }
        
        logger.debug("ML models initialized (placeholder mode)")
    
    async def detect_format(
        self,
        data: Union[str, Path, bytes, BinaryIO],
        filename: Optional[str] = None,
        method: DetectionMethod = DetectionMethod.HYBRID
    ) -> DetectionResult:
        """
        Detect format of input data using specified method.
        
        Args:
            data: Input data to analyze
            filename: Optional filename for extension-based detection
            method: Detection method to use
            
        Returns:
            DetectionResult with format information
        """
        start_time = time.time()
        
        try:
            # Prepare data for analysis
            file_data = await self._prepare_data(data)
            
            # Perform detection based on method
            if method == DetectionMethod.MAGIC_BYTES:
                result = await self._detect_by_magic_bytes(file_data, filename)
            elif method == DetectionMethod.FILE_EXTENSION:
                result = await self._detect_by_extension(filename or "")
            elif method == DetectionMethod.MIME_TYPE:
                result = await self._detect_by_mime_type(data, filename)
            elif method == DetectionMethod.CONTENT_ANALYSIS:
                result = await self._detect_by_content_analysis(file_data)
            elif method == DetectionMethod.ML_PREDICTION:
                result = await self._detect_by_ml(file_data)
            else:  # HYBRID
                result = await self._detect_hybrid(file_data, filename)
            
            # Post-process result
            result.processing_time = time.time() - start_time
            result.confidence_level = self._calculate_confidence_level(result.confidence)
            
            # Validate detection
            if result.detected_format != "unknown":
                result.validation_passed = await self._validate_detection(file_data, result)
            
            # Update statistics
            self._update_detection_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Format detection failed: {str(e)}")
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=method,
                warnings=[f"Detection failed: {str(e)}"],
                processing_time=time.time() - start_time
            )
    
    async def _prepare_data(self, data: Union[str, Path, bytes, BinaryIO]) -> bytes:
        """Prepare input data for analysis."""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, (str, Path)):
            path = Path(data)
            if path.exists():
                return path.read_bytes()
            else:
                raise FileNotFoundError(f"File not found: {data}")
        else:
            # File-like object
            current_pos = data.tell()
            data.seek(0)
            file_data = data.read()
            data.seek(current_pos)
            
            if isinstance(file_data, str):
                return file_data.encode('utf-8')
            return file_data
    
    async def _detect_by_magic_bytes(self, data: bytes, filename: Optional[str] = None) -> DetectionResult:
        """Detect format using magic bytes."""
        if len(data) < 4:
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.MAGIC_BYTES,
                warnings=["Insufficient data for magic bytes detection"]
            )
        
        # Check magic bytes index
        candidates = []
        
        for key_length in [4, 8, 12, 16]:
            if len(data) < key_length:
                continue
            
            key = data[:key_length]
            if key in self.magic_bytes_index:
                for format_name, magic_bytes, offset in self.magic_bytes_index[key]:
                    if offset + len(magic_bytes) <= len(data):
                        if data[offset:offset + len(magic_bytes)] == magic_bytes:
                            candidates.append((format_name, 1.0))  # High confidence for exact match
        
        # Check all signatures for partial matches
        for format_name, signature in self.format_signatures.items():
            for magic_bytes in signature.magic_bytes:
                offset = signature.offset
                if offset + len(magic_bytes) <= len(data):
                    if data[offset:offset + len(magic_bytes)] == magic_bytes:
                        if (format_name, 1.0) not in candidates:
                            candidates.append((format_name, 0.9))
                    elif magic_bytes in data[:min(1024, len(data))]:  # Check first KB
                        candidates.append((format_name, 0.7))
        
        if candidates:
            # Sort by confidence and return best match
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_format, confidence = candidates[0]
            
            signature = self.format_signatures[best_format]
            
            return DetectionResult(
                detected_format=best_format,
                category=signature.category,
                confidence=confidence,
                confidence_level=self._calculate_confidence_level(confidence),
                detection_method=DetectionMethod.MAGIC_BYTES,
                alternative_formats=candidates[1:5],  # Top 5 alternatives
                metadata={"signature_matched": True, "offset": signature.offset}
            )
        
        return DetectionResult(
            detected_format="unknown",
            category=FormatCategory.UNKNOWN,
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            detection_method=DetectionMethod.MAGIC_BYTES,
            warnings=["No magic bytes signature matched"]
        )
    
    async def _detect_by_extension(self, filename: str) -> DetectionResult:
        """Detect format using file extension."""
        if not filename:
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.FILE_EXTENSION,
                warnings=["No filename provided"]
            )
        
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        if not extension:
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.FILE_EXTENSION,
                warnings=["No file extension found"]
            )
        
        # Find matching formats by extension
        candidates = []
        for format_name, signature in self.format_signatures.items():
            if extension in signature.file_extensions:
                candidates.append((format_name, 0.8))  # Medium-high confidence for extension match
        
        if candidates:
            best_format, confidence = candidates[0]
            signature = self.format_signatures[best_format]
            
            return DetectionResult(
                detected_format=best_format,
                category=signature.category,
                confidence=confidence,
                confidence_level=self._calculate_confidence_level(confidence),
                detection_method=DetectionMethod.FILE_EXTENSION,
                alternative_formats=candidates[1:],
                metadata={"extension": extension}
            )
        
        return DetectionResult(
            detected_format="unknown",
            category=FormatCategory.UNKNOWN,
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            detection_method=DetectionMethod.FILE_EXTENSION,
            warnings=[f"Unknown file extension: {extension}"]
        )
    
    async def _detect_by_mime_type(self, data: Union[str, Path, bytes, BinaryIO], filename: Optional[str] = None) -> DetectionResult:
        """Detect format using MIME type analysis."""
        try:
            # Use mimetypes library
            if filename:
                mime_type, _ = mimetypes.guess_type(filename)
            else:
                mime_type = None
            
            if not mime_type:
                # Try to determine from content
                if isinstance(data, bytes):
                    # Basic MIME type detection from content
                    if data.startswith(b'%PDF'):
                        mime_type = 'application/pdf'
                    elif data.startswith(b'\xFF\xD8\xFF'):
                        mime_type = 'image/jpeg'
                    elif data.startswith(b'\x89PNG'):
                        mime_type = 'image/png'
                    # Add more content-based MIME detection
            
            if mime_type:
                # Find matching format by MIME type
                for format_name, signature in self.format_signatures.items():
                    if mime_type in signature.mime_types:
                        return DetectionResult(
                            detected_format=format_name,
                            category=signature.category,
                            confidence=0.7,  # Medium confidence for MIME type match
                            confidence_level=ConfidenceLevel.MEDIUM,
                            detection_method=DetectionMethod.MIME_TYPE,
                            metadata={"mime_type": mime_type}
                        )
            
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.MIME_TYPE,
                warnings=["Could not determine MIME type"]
            )
            
        except Exception as e:
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.MIME_TYPE,
                warnings=[f"MIME type detection failed: {str(e)}"]
            )
    
    async def _detect_by_content_analysis(self, data: bytes) -> DetectionResult:
        """Detect format using content analysis."""
        analysis = await self._analyze_content(data)
        
        # Heuristic-based format detection
        format_scores = {}
        
        # Text-based detection
        if analysis.ascii_ratio > 0.95 and analysis.null_byte_ratio < 0.01:
            if b'<html' in data[:1024].lower() or b'<!doctype html' in data[:1024].lower():
                format_scores['html'] = 0.9
            elif data.startswith(b'<?xml'):
                format_scores['xml'] = 0.9
            elif (data.startswith(b'{') and data.rstrip().endswith(b'}')) or \
                 (data.startswith(b'[') and data.rstrip().endswith(b']')):
                try:
                    json.loads(data.decode('utf-8'))
                    format_scores['json'] = 0.8
                except:
                    pass
            else:
                format_scores['text'] = 0.6
        
        # Binary format detection based on entropy
        elif analysis.entropy > 7.5:  # High entropy suggests compression or encryption
            if analysis.compression_detected:
                format_scores['zip'] = 0.6  # Could be various compressed formats
            elif analysis.encryption_detected:
                format_scores['encrypted'] = 0.7
        
        # Medium entropy suggests structured binary data
        elif 4.0 < analysis.entropy < 7.5:
            format_scores['binary'] = 0.5
        
        if format_scores:
            best_format = max(format_scores.items(), key=lambda x: x[1])
            format_name, confidence = best_format
            
            # Map to known categories
            category_map = {
                'html': FormatCategory.TEXT,
                'xml': FormatCategory.TEXT,
                'json': FormatCategory.TEXT,
                'text': FormatCategory.TEXT,
                'zip': FormatCategory.ARCHIVE,
                'encrypted': FormatCategory.DATA,
                'binary': FormatCategory.DATA
            }
            
            return DetectionResult(
                detected_format=format_name,
                category=category_map.get(format_name, FormatCategory.UNKNOWN),
                confidence=confidence,
                confidence_level=self._calculate_confidence_level(confidence),
                detection_method=DetectionMethod.CONTENT_ANALYSIS,
                metadata={
                    "content_analysis": {
                        "entropy": analysis.entropy,
                        "ascii_ratio": analysis.ascii_ratio,
                        "file_size": analysis.file_size
                    }
                }
            )
        
        return DetectionResult(
            detected_format="unknown",
            category=FormatCategory.UNKNOWN,
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            detection_method=DetectionMethod.CONTENT_ANALYSIS,
            warnings=["Content analysis inconclusive"]
        )
    
    async def _detect_by_ml(self, data: bytes) -> DetectionResult:
        """Detect format using ML models."""
        # Placeholder implementation - would use actual ML models
        # For now, return a basic heuristic-based result
        
        confidence = 0.3  # Low confidence for placeholder
        
        # Simple heuristics for demonstration
        if len(data) > 0:
            if data.startswith(b'\xFF\xD8\xFF'):
                detected_format = "jpeg"
                category = FormatCategory.IMAGE
                confidence = 0.85
            elif data.startswith(b'\x89PNG'):
                detected_format = "png"
                category = FormatCategory.IMAGE
                confidence = 0.85
            elif data.startswith(b'%PDF'):
                detected_format = "pdf"
                category = FormatCategory.DOCUMENT
                confidence = 0.85
            else:
                detected_format = "unknown"
                category = FormatCategory.UNKNOWN
                confidence = 0.1
        else:
            detected_format = "unknown"
            category = FormatCategory.UNKNOWN
            confidence = 0.0
        
        return DetectionResult(
            detected_format=detected_format,
            category=category,
            confidence=confidence,
            confidence_level=self._calculate_confidence_level(confidence),
            detection_method=DetectionMethod.ML_PREDICTION,
            metadata={"ml_model": "placeholder_heuristic"}
        )
    
    async def _detect_hybrid(self, data: bytes, filename: Optional[str] = None) -> DetectionResult:
        """Detect format using hybrid approach combining multiple methods."""
        # Run multiple detection methods
        results = []
        
        # Magic bytes detection (highest priority)
        magic_result = await self._detect_by_magic_bytes(data, filename)
        if magic_result.confidence > 0.8:
            results.append((magic_result, 1.0))  # High weight for magic bytes
        
        # Extension detection
        if filename:
            ext_result = await self._detect_by_extension(filename)
            if ext_result.confidence > 0.5:
                results.append((ext_result, 0.7))  # Medium weight for extension
        
        # Content analysis
        content_result = await self._detect_by_content_analysis(data)
        if content_result.confidence > 0.4:
            results.append((content_result, 0.5))  # Lower weight for content analysis
        
        # ML prediction
        ml_result = await self._detect_by_ml(data)
        if ml_result.confidence > 0.6:
            results.append((ml_result, 0.8))  # High weight for ML if confident
        
        if not results:
            return DetectionResult(
                detected_format="unknown",
                category=FormatCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detection_method=DetectionMethod.HYBRID,
                warnings=["All detection methods failed"]
            )
        
        # Weighted consensus
        format_scores = {}
        for result, weight in results:
            if result.detected_format != "unknown":
                score = result.confidence * weight
                if result.detected_format in format_scores:
                    format_scores[result.detected_format] = max(format_scores[result.detected_format], score)
                else:
                    format_scores[result.detected_format] = score
        
        if format_scores:
            best_format = max(format_scores.items(), key=lambda x: x[1])
            format_name, final_confidence = best_format
            
            # Get category from signature
            signature = self.format_signatures.get(format_name)
            category = signature.category if signature else FormatCategory.UNKNOWN
            
            # Collect alternative formats
            alternatives = [(fmt, score) for fmt, score in format_scores.items() if fmt != format_name]
            alternatives.sort(key=lambda x: x[1], reverse=True)
            
            return DetectionResult(
                detected_format=format_name,
                category=category,
                confidence=min(1.0, final_confidence),  # Cap at 1.0
                confidence_level=self._calculate_confidence_level(final_confidence),
                detection_method=DetectionMethod.HYBRID,
                alternative_formats=alternatives[:5],
                metadata={
                    "methods_used": [result.detection_method.value for result, _ in results],
                    "consensus_score": final_confidence
                }
            )
        
        # Fallback to best single result
        best_result = max(results, key=lambda x: x[0].confidence * x[1])[0]
        best_result.detection_method = DetectionMethod.HYBRID
        return best_result
    
    async def _analyze_content(self, data: bytes) -> ContentAnalysis:
        """Analyze content characteristics."""
        file_size = len(data)
        
        if file_size == 0:
            return ContentAnalysis(
                file_size=0,
                entropy=0.0,
                ascii_ratio=0.0,
                null_byte_ratio=0.0,
                compression_detected=False,
                encryption_detected=False
            )
        
        # Calculate entropy
        entropy = self._calculate_entropy(data)
        
        # Calculate ASCII ratio
        ascii_count = sum(1 for byte in data if 32 <= byte <= 126 or byte in [9, 10, 13])
        ascii_ratio = ascii_count / file_size
        
        # Calculate null byte ratio
        null_count = data.count(0)
        null_byte_ratio = null_count / file_size
        
        # Detect compression (high entropy + specific patterns)
        compression_detected = entropy > 7.5 and any(
            data.startswith(signature) for signature in [
                b'PK\x03\x04',  # ZIP
                b'\x1f\x8b',   # GZIP
                b'BZ',         # BZIP2
                b'\xfd7zXZ'    # XZ
            ]
        )
        
        # Detect encryption (very high entropy, no clear patterns)
        encryption_detected = entropy > 7.8 and ascii_ratio < 0.1 and not compression_detected
        
        # Detect text patterns
        text_patterns = []
        if ascii_ratio > 0.8:
            if b'<html' in data[:1024].lower():
                text_patterns.append("html")
            if b'<?xml' in data[:1024].lower():
                text_patterns.append("xml")
            if re.search(rb'\{.*".*".*\}', data[:1024]):
                text_patterns.append("json")
        
        return ContentAnalysis(
            file_size=file_size,
            entropy=entropy,
            ascii_ratio=ascii_ratio,
            null_byte_ratio=null_byte_ratio,
            compression_detected=compression_detected,
            encryption_detected=encryption_detected,
            text_patterns=text_patterns
        )
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _calculate_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to confidence level."""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    async def _validate_detection(self, data: bytes, result: DetectionResult) -> bool:
        """Validate detection result against file content."""
        if result.detected_format == "unknown":
            return True  # Can't validate unknown format
        
        signature = self.format_signatures.get(result.detected_format)
        if not signature:
            return False
        
        # Check if magic bytes match
        for magic_bytes in signature.magic_bytes:
            offset = signature.offset
            if offset + len(magic_bytes) <= len(data):
                if data[offset:offset + len(magic_bytes)] == magic_bytes:
                    return True
        
        # Additional format-specific validation could be added here
        
        return False
    
    def _update_detection_stats(self, result -> None: DetectionResult) -> None:
        """Update detection statistics."""
        self.detection_stats["total_detections"] += 1
        
        method = result.detection_method.value
        if method not in self.detection_stats["method_usage"]:
            self.detection_stats["method_usage"][method] = 0
        self.detection_stats["method_usage"][method] += 1
        
        self.detection_stats["processing_times"].append(result.processing_time)
        
        # Keep only recent processing times (last 1000)
        if len(self.detection_stats["processing_times"]) > 1000:
            self.detection_stats["processing_times"] = self.detection_stats["processing_times"][-1000:]
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats."""
        return list(self.format_signatures.keys())
    
    def get_format_info(self, format_name: str) -> Optional[FormatSignature]:
        """Get detailed information about a format."""
        return self.format_signatures.get(format_name)
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics."""
        stats = self.detection_stats.copy()
        
        if stats["processing_times"]:
            import statistics
            stats["average_processing_time"] = statistics.mean(stats["processing_times"])
            stats["median_processing_time"] = statistics.median(stats["processing_times"])
        
        return stats
    
    async def batch_detect(
        self, files: List[Union[str, Path]], method: DetectionMethod = DetectionMethod.HYBRID
    ) -> List[DetectionResult]:
        """Detect formats for multiple files."""
        results = []
        
        for file_path in files:
            try:
                result = await self.detect_format(file_path, str(file_path), method)
                results.append(result)
            except Exception as e:
                error_result = DetectionResult(
                    detected_format="unknown",
                    category=FormatCategory.UNKNOWN,
                    confidence=0.0,
                    confidence_level=ConfidenceLevel.VERY_LOW,
                    detection_method=method,
                    warnings=[f"Detection failed: {str(e)}"]
                )
                results.append(error_result)
        
        return results


# Export all classes for module imports
__all__ = [
    "FormatDetector",
    "DetectionMethod",
    "FormatCategory",
    "ConfidenceLevel",
    "FormatSignature",
    "DetectionResult",
    "ContentAnalysis"
]

logger.info("Format detector module loaded successfully")