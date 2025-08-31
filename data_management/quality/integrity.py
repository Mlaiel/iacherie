"""Integrity Controller - Data Integrity and Consistency Validation
===============================================================

Enterprise-grade data integrity checking system for comprehensive content validation.
Ensures data consistency, corruption detection, format verification, and metadata validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Content upload → Integrity verification → Corruption detection → 
Metadata validation → Consistency checking → Data authenticity verification
"""import logging
import hashlib
import hmac
import json
import struct
import os
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import magic
import zipfile
import tarfile

# Cryptographic libraries
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Content analysis libraries
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat
    import librosa
    import soundfile as sf
    from mutagen import File as MutagenFile
    HAS_MEDIA_LIBS = True
except ImportError:
    HAS_MEDIA_LIBS = False


class IntegrityLevel(Enum):
    """Integrity check levels"""    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRYPTOGRAPHIC = "cryptographic"


class IntegrityStatus(Enum):
    """Integrity verification status"""    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    CORRUPTED = "corrupted"
    UNKNOWN = "unknown"


@dataclass
class IntegrityResult:
    """Data integrity check result"""    status: IntegrityStatus
    score: float
    checks_performed: List[str]
    issues_found: List[Dict[str, Any]]
    metadata_verification: Dict[str, Any]
    checksum_verification: Dict[str, Any]
    format_verification: Dict[str, Any]
    content_analysis: Dict[str, Any]
    authenticity_indicators: Dict[str, Any]
    recommendations: List[str]
    confidence_level: float
    processing_time: float


class IntegrityController:
    """    Enterprise data integrity and consistency validation controller.
    
    Provides comprehensive integrity checking including corruption detection,
    format verification, metadata validation, and authenticity verification.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Integrity checking configuration
        self.hash_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        self.magic_signatures = self._load_magic_signatures()
        self.metadata_validators = self._setup_metadata_validators()
        
        # Corruption detection patterns
        self.corruption_patterns = {
            'audio': [
                b'\x00' * 1024,  # Large null blocks
                b'\xFF' * 512,   # Large blocks of 0xFF
                b'RIFF' + b'\x00' * 4 + b'WAVE',  # Incomplete WAV header
            ],
            'video': [
                b'\x00' * 2048,  # Large null blocks
                b'ftyp' + b'\x00' * 4,  # Incomplete MP4 header
            ],
            'image': [
                b'\xFF\xD8\xFF\xE0' + b'\x00' * 4,  # Incomplete JPEG header
                b'\x89PNG\r\n\x1a\n' + b'\x00' * 4,  # Incomplete PNG header
            ]
        }
        
        # Known good signatures
        self.known_signatures = {
            'jpeg': [b'\xFF\xD8\xFF'],
            'png': [b'\x89PNG\r\n\x1a\n'],
            'gif': [b'GIF87a', b'GIF89a'],
            'mp4': [b'ftyp'],
            'avi': [b'RIFF', b'AVI '],
            'wav': [b'RIFF', b'WAVE'],
            'mp3': [b'ID3', b'\xFF\xFB', b'\xFF\xF3'],
            'pdf': [b'%PDF-'],
            'zip': [b'PK\x03\x04', b'PK\x05\x06']
        }
        
        self.logger.info("IntegrityController initialized successfully")
    
    def _load_magic_signatures(self) -> Dict[str, bytes]:
        """Load file magic signatures for format detection."""        return {
            'jpeg': b'\xFF\xD8\xFF',
            'png': b'\x89PNG\r\n\x1a\n',
            'gif87': b'GIF87a',
            'gif89': b'GIF89a',
            'mp4': b'\x00\x00\x00\x20ftypmp4',
            'avi': b'RIFF',
            'wav': b'RIFF',
            'mp3_id3': b'ID3',
            'mp3_frame': b'\xFF\xFB',
            'pdf': b'%PDF-',
            'zip': b'PK\x03\x04',
            'rar': b'Rar!\x1a\x07\x00',
            'tar': b'ustar',
            'bmp': b'BM',
            'webp': b'RIFF'
        }
    
    def _setup_metadata_validators(self) -> Dict[str, callable]:
        """Setup metadata validation functions."""        return {
            'exif': self._validate_exif_metadata,
            'id3': self._validate_id3_metadata,
            'xmp': self._validate_xmp_metadata,
            'iptc': self._validate_iptc_metadata
        }
    
    async def check_integrity(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        integrity_level: IntegrityLevel = IntegrityLevel.STANDARD
    ) -> IntegrityResult:
        """        Perform comprehensive data integrity checking.
        
        Args:
            content_data: Content data to verify
            content_type: Type of content
            metadata: Optional metadata for verification
            integrity_level: Level of integrity checking
            
        Returns:
            IntegrityResult: Comprehensive integrity check results
        """        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting integrity check - Type: {content_type}, Level: {integrity_level.value}")
            
            checks_performed = []
            issues_found = []
            
            # Step 1: Basic format verification
            format_verification = await self._verify_format(content_data, content_type)
            checks_performed.append('format_verification')
            
            if not format_verification.get('valid', False):
                issues_found.append({
                    'type': 'format_error',
                    'severity': 'critical',
                    'message': format_verification.get('error', 'Format verification failed')
                })
            
            # Step 2: Checksum verification
            checksum_verification = await self._verify_checksums(content_data, metadata)
            checks_performed.append('checksum_verification')
            
            # Step 3: Content structure analysis
            content_analysis = await self._analyze_content_structure(content_data, content_type)
            checks_performed.append('content_analysis')
            
            if content_analysis.get('corruption_detected', False):
                issues_found.append({
                    'type': 'corruption',
                    'severity': 'critical',
                    'message': 'Content corruption detected'
                })
            
            # Step 4: Metadata verification
            metadata_verification = await self._verify_metadata(content_data, content_type, metadata)
            checks_performed.append('metadata_verification')
            
            # Step 5: Advanced integrity checks (if comprehensive)
            authenticity_indicators = {}
            if integrity_level in [IntegrityLevel.COMPREHENSIVE, IntegrityLevel.CRYPTOGRAPHIC]:
                authenticity_indicators = await self._check_authenticity(content_data, content_type)
                checks_performed.append('authenticity_verification')
            
            # Step 6: Cryptographic verification (if cryptographic level)
            if integrity_level == IntegrityLevel.CRYPTOGRAPHIC:
                crypto_verification = await self._verify_cryptographic_integrity(content_data, metadata)
                checks_performed.append('cryptographic_verification')
                authenticity_indicators.update(crypto_verification)
            
            # Calculate overall integrity score
            integrity_score = self._calculate_integrity_score(
                format_verification, checksum_verification, content_analysis,
                metadata_verification, authenticity_indicators, issues_found
            )
            
            # Determine integrity status
            status = self._determine_integrity_status(integrity_score, issues_found)
            
            # Generate recommendations
            recommendations = self._generate_integrity_recommendations(
                issues_found, format_verification, content_analysis
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(
                checks_performed, integrity_score, issues_found
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = IntegrityResult(
                status=status,
                score=integrity_score,
                checks_performed=checks_performed,
                issues_found=issues_found,
                metadata_verification=metadata_verification,
                checksum_verification=checksum_verification,
                format_verification=format_verification,
                content_analysis=content_analysis,
                authenticity_indicators=authenticity_indicators,
                recommendations=recommendations,
                confidence_level=confidence_level,
                processing_time=processing_time
            )
            
            self.logger.info(f"Integrity check completed - Status: {status.value}, Score: {integrity_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during integrity check: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return IntegrityResult(
                status=IntegrityStatus.UNKNOWN,
                score=0.0,
                checks_performed=[],
                issues_found=[{'type': 'error', 'severity': 'critical', 'message': f'Integrity check failed: {str(e)}'}],
                metadata_verification={},
                checksum_verification={},
                format_verification={},
                content_analysis={},
                authenticity_indicators={},
                recommendations=['Review content data and retry integrity check'],
                confidence_level=0.0,
                processing_time=processing_time
            )
    
    async def _verify_format(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Verify content format and structure."""        verification = {
            'valid': True,
            'detected_format': None,
            'format_match': False,
            'signature_valid': False,
            'structure_valid': False,
            'size_valid': False
        }
        
        try:
            # Get binary data
            if isinstance(content_data, str) and os.path.exists(content_data):
                with open(content_data, 'rb') as f:
                    binary_data = f.read(8192)  # Read first 8KB for analysis
            elif isinstance(content_data, bytes):
                binary_data = content_data[:8192]
            elif isinstance(content_data, dict) and 'data' in content_data:
                if isinstance(content_data['data'], bytes):
                    binary_data = content_data['data'][:8192]
                else:
                    binary_data = str(content_data['data']).encode('utf-8')[:8192]
            else:
                binary_data = str(content_data).encode('utf-8')[:8192]
            
            if not binary_data:
                verification['valid'] = False
                verification['error'] = 'No data to verify'
                return verification
            
            # Format signature detection
            detected_format = self._detect_format_signature(binary_data)
            verification['detected_format'] = detected_format
            
            # Check if detected format matches expected content type
            format_mappings = {
                'audio': ['mp3', 'wav', 'aac', 'ogg', 'flac'],
                'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
                'image': ['jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff'],
                'document': ['pdf', 'doc', 'docx', 'zip', 'tar'],
                'text': ['txt', 'json', 'xml', 'html']
            }
            
            expected_formats = format_mappings.get(content_type, [])
            verification['format_match'] = detected_format in expected_formats or detected_format == content_type
            
            # Signature validation
            verification['signature_valid'] = self._validate_signature(binary_data, detected_format)
            
            # Structure validation
            verification['structure_valid'] = await self._validate_structure(binary_data, detected_format)
            
            # Size validation
            data_size = len(binary_data) if isinstance(content_data, bytes) else os.path.getsize(content_data) if isinstance(content_data, str) else 0
            verification['size_valid'] = self._validate_size(data_size, content_type)
            verification['size'] = data_size
            
            # Overall validity
            verification['valid'] = all([
                verification['signature_valid'],
                verification['structure_valid'],
                verification['size_valid']
            ])
            
        except Exception as e:
            verification['valid'] = False
            verification['error'] = f'Format verification error: {str(e)}'
        
        return verification
    
    def _detect_format_signature(self, binary_data: bytes) -> Optional[str]:
        """Detect format based on binary signature."""        for format_name, signature in self.magic_signatures.items():
            if binary_data.startswith(signature):
                # Map detailed signatures to general formats
                if format_name.startswith('mp3'):
                    return 'mp3'
                elif format_name.startswith('gif'):
                    return 'gif'
                else:
                    return format_name
        
        # Fallback detection using python-magic if available
        try:
            import magic
            mime_type = magic.from_buffer(binary_data, mime=True)
            return mime_type.split('/')[-1] if mime_type else None
        except ImportError:
            pass
        
        return None
    
    def _validate_signature(self, binary_data: bytes, format_name: Optional[str]) -> bool:
        """Validate binary signature matches format."""        if not format_name or format_name not in self.known_signatures:
            return False
        
        signatures = self.known_signatures[format_name]
        return any(binary_data.startswith(sig) for sig in signatures)
    
    async def _validate_structure(self, binary_data: bytes, format_name: Optional[str]) -> bool:
        """Validate internal structure of content."""        if not format_name:
            return False
        
        try:
            if format_name == 'jpeg':
                return self._validate_jpeg_structure(binary_data)
            elif format_name == 'png':
                return self._validate_png_structure(binary_data)
            elif format_name == 'mp4':
                return self._validate_mp4_structure(binary_data)
            elif format_name == 'wav':
                return self._validate_wav_structure(binary_data)
            elif format_name == 'pdf':
                return self._validate_pdf_structure(binary_data)
            else:
                # Basic validation for unknown formats
                return len(binary_data) > 0 and not all(b == 0 for b in binary_data[:100])
        except Exception:
            return False
    
    def _validate_jpeg_structure(self, data: bytes) -> bool:
        """Validate JPEG file structure."""        if not data.startswith(b'\xFF\xD8\xFF'):
            return False
        
        # Look for EOI marker
        return b'\xFF\xD9' in data
    
    def _validate_png_structure(self, data: bytes) -> bool:
        """Validate PNG file structure."""        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            return False
        
        # Check for IHDR chunk
        return b'IHDR' in data[:100]
    
    def _validate_mp4_structure(self, data: bytes) -> bool:
        """Validate MP4 file structure."""        if len(data) < 8:
            return False
        
        # Check for ftyp box
        return b'ftyp' in data[:20]
    
    def _validate_wav_structure(self, data: bytes) -> bool:
        """Validate WAV file structure."""        if not data.startswith(b'RIFF'):
            return False
        
        # Check for WAVE format
        return b'WAVE' in data[:20]
    
    def _validate_pdf_structure(self, data: bytes) -> bool:
        """Validate PDF file structure."""        if not data.startswith(b'%PDF-'):
            return False
        
        # Look for EOF marker
        return b'%%EOF' in data or b'startxref' in data
    
    def _validate_size(self, size: int, content_type: str) -> bool:
        """Validate content size is reasonable."""        size_limits = {
            'audio': (1024, 500 * 1024 * 1024),     # 1KB - 500MB
            'video': (1024, 5 * 1024 * 1024 * 1024), # 1KB - 5GB
            'image': (100, 100 * 1024 * 1024),       # 100B - 100MB
            'text': (1, 10 * 1024 * 1024),           # 1B - 10MB
            'document': (100, 200 * 1024 * 1024)     # 100B - 200MB
        }
        
        min_size, max_size = size_limits.get(content_type, (1, 1024 * 1024 * 1024))
        return min_size <= size <= max_size
    
    async def _verify_checksums(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify content checksums and hashes."""        verification = {
            'checksums_calculated': {},
            'checksums_verified': {},
            'integrity_preserved': True
        }
        
        try:
            # Get binary data for hashing
            if isinstance(content_data, str) and os.path.exists(content_data):
                with open(content_data, 'rb') as f:
                    binary_data = f.read()
            elif isinstance(content_data, bytes):
                binary_data = content_data
            elif isinstance(content_data, dict) and 'data' in content_data:
                binary_data = content_data['data'] if isinstance(content_data['data'], bytes) else str(content_data['data']).encode('utf-8')
            else:
                binary_data = str(content_data).encode('utf-8')
            
            # Calculate checksums
            for algorithm in self.hash_algorithms:
                if algorithm == 'md5':
                    hash_obj = hashlib.md5()
                elif algorithm == 'sha1':
                    hash_obj = hashlib.sha1()
                elif algorithm == 'sha256':
                    hash_obj = hashlib.sha256()
                elif algorithm == 'sha512':
                    hash_obj = hashlib.sha512()
                else:
                    continue
                
                hash_obj.update(binary_data)
                verification['checksums_calculated'][algorithm] = hash_obj.hexdigest()
            
            # Verify against provided checksums in metadata
            if metadata and 'checksums' in metadata:
                provided_checksums = metadata['checksums']
                for algorithm, expected_hash in provided_checksums.items():
                    calculated_hash = verification['checksums_calculated'].get(algorithm)
                    if calculated_hash:
                        is_valid = calculated_hash.lower() == expected_hash.lower()
                        verification['checksums_verified'][algorithm] = is_valid
                        if not is_valid:
                            verification['integrity_preserved'] = False
            
            # Generate content fingerprint
            verification['content_fingerprint'] = verification['checksums_calculated'].get('sha256', '')
            
        except Exception as e:
            verification['error'] = f'Checksum verification error: {str(e)}'
            verification['integrity_preserved'] = False
        
        return verification
    
    async def _analyze_content_structure(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze content structure for corruption detection."""        analysis = {
            'corruption_detected': False,
            'corruption_indicators': [],
            'structure_analysis': {},
            'entropy_analysis': {},
            'pattern_analysis': {}
        }
        
        try:
            # Get binary data
            if isinstance(content_data, str) and os.path.exists(content_data):
                with open(content_data, 'rb') as f:
                    binary_data = f.read()
            elif isinstance(content_data, bytes):
                binary_data = content_data
            else:
                binary_data = str(content_data).encode('utf-8')
            
            # Corruption pattern detection
            corruption_patterns = self.corruption_patterns.get(content_type, [])
            for pattern in corruption_patterns:
                if pattern in binary_data:
                    analysis['corruption_detected'] = True
                    analysis['corruption_indicators'].append(f'Corruption pattern detected: {pattern[:20].hex()}')
            
            # Entropy analysis
            entropy = self._calculate_entropy(binary_data)
            analysis['entropy_analysis'] = {
                'entropy': entropy,
                'expected_range': (4.0, 8.0),
                'suspicious': entropy < 1.0 or entropy > 7.9
            }
            
            if analysis['entropy_analysis']['suspicious']:
                analysis['corruption_indicators'].append(f'Suspicious entropy: {entropy:.2f}')
            
            # Null byte analysis
            null_sequences = self._find_null_sequences(binary_data)
            analysis['pattern_analysis']['null_sequences'] = null_sequences
            
            if null_sequences['max_length'] > 1024:
                analysis['corruption_detected'] = True
                analysis['corruption_indicators'].append(f'Large null sequence detected: {null_sequences["max_length"]} bytes')
            
            # Repeated pattern analysis
            repeated_patterns = self._find_repeated_patterns(binary_data)
            analysis['pattern_analysis']['repeated_patterns'] = repeated_patterns
            
            if repeated_patterns['max_repetition'] > 100:
                analysis['corruption_indicators'].append(f'Excessive pattern repetition detected')
            
            # Content-specific structure analysis
            if content_type == 'audio' and HAS_MEDIA_LIBS:
                analysis['structure_analysis'] = await self._analyze_audio_structure(binary_data)
            elif content_type == 'video' and HAS_MEDIA_LIBS:
                analysis['structure_analysis'] = await self._analyze_video_structure(binary_data)
            elif content_type == 'image' and HAS_MEDIA_LIBS:
                analysis['structure_analysis'] = await self._analyze_image_structure(binary_data)
            
        except Exception as e:
            analysis['error'] = f'Structure analysis error: {str(e)}'
        
        return analysis
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""        if not data:
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
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def _find_null_sequences(self, data: bytes) -> Dict[str, Any]:
        """Find null byte sequences in data."""        sequences = []
        current_length = 0
        max_length = 0
        total_nulls = 0
        
        for byte in data:
            if byte == 0:
                current_length += 1
                total_nulls += 1
            else:
                if current_length > 0:
                    sequences.append(current_length)
                    max_length = max(max_length, current_length)
                current_length = 0
        
        # Don't forget the last sequence
        if current_length > 0:
            sequences.append(current_length)
            max_length = max(max_length, current_length)
        
        return {
            'total_null_bytes': total_nulls,
            'null_percentage': total_nulls / len(data) if data else 0,
            'max_length': max_length,
            'sequence_count': len(sequences),
            'sequences': sequences[:10]  # First 10 sequences
        }
    
    def _find_repeated_patterns(self, data: bytes) -> Dict[str, Any]:
        """Find repeated byte patterns in data."""        # Sample analysis on first 64KB for performance
        sample_data = data[:65536]
        
        pattern_counts = {}
        max_repetition = 0
        
        # Check for repeated 4-byte patterns
        for i in range(len(sample_data) - 4):
            pattern = sample_data[i:i+4]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            max_repetition = max(max_repetition, pattern_counts[pattern])
        
        # Find most repeated patterns
        most_repeated = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'max_repetition': max_repetition,
            'unique_patterns': len(pattern_counts),
            'most_repeated': [(pattern.hex(), count) for pattern, count in most_repeated]
        }
    
    async def _analyze_audio_structure(self, data: bytes) -> Dict[str, Any]:
        """Analyze audio-specific structure."""        structure = {}
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.audio', delete=False) as tmp_file:
                tmp_file.write(data)
                tmp_path = tmp_file.name
            
            try:
                # Basic audio loading test
                audio_data, sample_rate = librosa.load(tmp_path, sr=None, duration=10)
                
                structure['loadable'] = True
                structure['sample_rate'] = int(sample_rate)
                structure['duration_sample'] = len(audio_data) / sample_rate
                structure['amplitude_range'] = (float(np.min(audio_data)), float(np.max(audio_data)))
                structure['rms_level'] = float(np.sqrt(np.mean(audio_data ** 2)))
                
                # Check for digital silence or clipping
                silence_threshold = 0.001
                if structure['rms_level'] < silence_threshold:
                    structure['issues'] = structure.get('issues', [])
                    structure['issues'].append('Digital silence detected')
                
                if np.any(np.abs(audio_data) > 0.99):
                    structure['issues'] = structure.get('issues', [])
                    structure['issues'].append('Audio clipping detected')
                
            except Exception as e:
                structure['loadable'] = False
                structure['load_error'] = str(e)
            
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            structure['analysis_error'] = str(e)
        
        return structure
    
    async def _analyze_video_structure(self, data: bytes) -> Dict[str, Any]:
        """Analyze video-specific structure."""        structure = {}
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.video', delete=False) as tmp_file:
                tmp_file.write(data)
                tmp_path = tmp_file.name
            
            try:
                # Basic video loading test
                cap = cv2.VideoCapture(tmp_path)
                
                if cap.isOpened():
                    structure['openable'] = True
                    structure['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    structure['fps'] = cap.get(cv2.CAP_PROP_FPS)
                    structure['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    structure['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    # Try to read first frame
                    ret, frame = cap.read()
                    if ret:
                        structure['first_frame_readable'] = True
                        structure['frame_shape'] = frame.shape
                    else:
                        structure['first_frame_readable'] = False
                        structure['issues'] = ['Cannot read first frame']
                else:
                    structure['openable'] = False
                    structure['issues'] = ['Cannot open video file']
                
                cap.release()
                
            except Exception as e:
                structure['openable'] = False
                structure['open_error'] = str(e)
            
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            structure['analysis_error'] = str(e)
        
        return structure
    
    async def _analyze_image_structure(self, data: bytes) -> Dict[str, Any]:
        """Analyze image-specific structure."""        structure = {}
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.image', delete=False) as tmp_file:
                tmp_file.write(data)
                tmp_path = tmp_file.name
            
            try:
                # Basic image loading test
                image = Image.open(tmp_path)
                
                structure['openable'] = True
                structure['size'] = image.size
                structure['mode'] = image.mode
                structure['format'] = image.format
                
                # Verify image can be processed
                try:
                    image.verify()
                    structure['verifiable'] = True
                except Exception:
                    structure['verifiable'] = False
                    structure['issues'] = structure.get('issues', [])
                    structure['issues'].append('Image verification failed')
                
                # Check for reasonable image properties
                width, height = image.size
                if width * height == 0:
                    structure['issues'] = structure.get('issues', [])
                    structure['issues'].append('Zero dimension image')
                
            except Exception as e:
                structure['openable'] = False
                structure['open_error'] = str(e)
            
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            structure['analysis_error'] = str(e)
        
        return structure
    
    async def _verify_metadata(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify content metadata integrity."""        verification = {
            'metadata_present': False,
            'metadata_valid': True,
            'extracted_metadata': {},
            'consistency_check': {},
            'tampering_indicators': []
        }
        
        try:
            # Extract embedded metadata
            embedded_metadata = await self._extract_embedded_metadata(content_data, content_type)
            verification['extracted_metadata'] = embedded_metadata
            verification['metadata_present'] = bool(embedded_metadata)
            
            # Verify against provided metadata
            if metadata:
                consistency = self._check_metadata_consistency(embedded_metadata, metadata)
                verification['consistency_check'] = consistency
                
                if not consistency.get('consistent', True):
                    verification['metadata_valid'] = False
                    verification['tampering_indicators'].extend(consistency.get('inconsistencies', []))
            
            # Check for metadata tampering indicators
            tampering_indicators = self._detect_metadata_tampering(embedded_metadata, content_type)
            verification['tampering_indicators'].extend(tampering_indicators)
            
            if tampering_indicators:
                verification['metadata_valid'] = False
            
        except Exception as e:
            verification['error'] = f'Metadata verification error: {str(e)}'
            verification['metadata_valid'] = False
        
        return verification
    
    async def _extract_embedded_metadata(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Extract embedded metadata from content."""        metadata = {}
        
        try:
            if isinstance(content_data, str) and os.path.exists(content_data):
                file_path = content_data
            else:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{content_type}') as tmp_file:
                    if isinstance(content_data, bytes):
                        tmp_file.write(content_data)
                    elif isinstance(content_data, dict) and 'data' in content_data:
                        tmp_file.write(content_data['data'])
                    else:
                        tmp_file.write(str(content_data).encode('utf-8'))
                    file_path = tmp_file.name
            
            try:
                # Use mutagen for audio/video metadata
                if content_type in ['audio', 'video'] and HAS_MEDIA_LIBS:
                    mutagen_file = MutagenFile(file_path)
                    if mutagen_file:
                        for key, value in mutagen_file.items():
                            metadata[key] = str(value[0]) if isinstance(value, list) and value else str(value)
                
                # Use PIL for image metadata
                elif content_type == 'image' and HAS_MEDIA_LIBS:
                    image = Image.open(file_path)
                    if hasattr(image, '_getexif') and image._getexif():
                        metadata['exif'] = dict(image._getexif())
                    
                    # Get basic image info
                    metadata.update({
                        'format': image.format,
                        'mode': image.mode,
                        'size': image.size
                    })
                
                # File system metadata
                stat = os.stat(file_path)
                metadata.update({
                    'file_size': stat.st_size,
                    'creation_time': datetime.fromtimestamp(stat.st_ctime),
                    'modification_time': datetime.fromtimestamp(stat.st_mtime)
                })
                
            finally:
                # Clean up temporary file
                if not (isinstance(content_data, str) and os.path.exists(content_data)):
                    os.unlink(file_path)
                    
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _check_metadata_consistency(
        self,
        embedded_metadata: Dict[str, Any],
        provided_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check consistency between embedded and provided metadata."""        consistency = {
            'consistent': True,
            'inconsistencies': [],
            'matches': [],
            'missing_fields': []
        }
        
        # Check common fields
        common_fields = ['file_size', 'format', 'creation_time']
        
        for field in common_fields:
            embedded_value = embedded_metadata.get(field)
            provided_value = provided_metadata.get(field)
            
            if embedded_value and provided_value:
                if str(embedded_value) != str(provided_value):
                    consistency['consistent'] = False
                    consistency['inconsistencies'].append(f'{field}: embedded={embedded_value}, provided={provided_value}')
                else:
                    consistency['matches'].append(field)
            elif provided_value and not embedded_value:
                consistency['missing_fields'].append(field)
        
        return consistency
    
    def _detect_metadata_tampering(
        self,
        metadata: Dict[str, Any],
        content_type: str
    ) -> List[str]:
        """Detect potential metadata tampering indicators."""        indicators = []
        
        # Check for suspicious creation/modification times
        creation_time = metadata.get('creation_time')
        modification_time = metadata.get('modification_time')
        
        if creation_time and modification_time:
            if isinstance(creation_time, datetime) and isinstance(modification_time, datetime):
                if modification_time < creation_time:
                    indicators.append('Modification time before creation time')
                
                # Check for future dates
                now = datetime.now()
                if creation_time > now or modification_time > now:
                    indicators.append('Future timestamp detected')
        
        # Check for metadata inconsistencies specific to content type
        if content_type == 'image':
            exif_data = metadata.get('exif', {})
            if exif_data:
                # Check for GPS coordinates in unexpected contexts
                if any(key for key in exif_data.keys() if 'GPS' in str(key)):
                    indicators.append('GPS metadata present')
        
        return indicators
    
    async def _check_authenticity(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """Check content authenticity indicators."""        authenticity = {
            'authentic_indicators': [],
            'suspicious_indicators': [],
            'manipulation_score': 0.0,
            'confidence': 0.7
        }
        
        try:
            # Digital signature presence
            if isinstance(content_data, dict) and 'signature' in content_data:
                authenticity['authentic_indicators'].append('Digital signature present')
            
            # Watermark detection (basic)
            watermark_detected = await self._detect_watermarks(content_data, content_type)
            if watermark_detected:
                authenticity['authentic_indicators'].append('Watermark detected')
            
            # Content-specific authenticity checks
            if content_type in ['image', 'video'] and HAS_MEDIA_LIBS:
                manipulation_indicators = await self._detect_manipulation(content_data, content_type)
                authenticity['suspicious_indicators'].extend(manipulation_indicators)
                authenticity['manipulation_score'] = len(manipulation_indicators) * 0.2
            
            # Calculate overall authenticity confidence
            authentic_count = len(authenticity['authentic_indicators'])
            suspicious_count = len(authenticity['suspicious_indicators'])
            
            if authentic_count > suspicious_count:
                authenticity['confidence'] = min(0.95, 0.7 + authentic_count * 0.1)
            elif suspicious_count > 0:
                authenticity['confidence'] = max(0.3, 0.7 - suspicious_count * 0.15)
            
        except Exception as e:
            authenticity['error'] = f'Authenticity check error: {str(e)}'
        
        return authenticity
    
    async def _detect_watermarks(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> bool:
        """Detect presence of watermarks (basic implementation)."""        # This is a placeholder for watermark detection
        # In a real implementation, this would use specialized algorithms
        
        if content_type in ['image', 'video']:
            # Look for common watermark patterns or metadata
            if isinstance(content_data, dict):
                metadata = content_data.get('metadata', {})
                return any(key.lower().find('watermark') != -1 for key in metadata.keys())
        
        return False
    
    async def _detect_manipulation(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> List[str]:
        """Detect content manipulation indicators."""        indicators = []
        
        # This is a basic implementation
        # Advanced manipulation detection would require specialized algorithms
        
        try:
            if content_type == 'image' and HAS_MEDIA_LIBS:
                # Check for obvious editing artifacts
                if isinstance(content_data, str) and os.path.exists(content_data):
                    image = Image.open(content_data)
                    
                    # Check for unusual compression artifacts
                    if image.format == 'JPEG':
                        # Very basic JPEG artifact detection
                        stat = ImageStat.Stat(image)
                        if any(var > 10000 for var in stat.var):
                            indicators.append('Unusual compression artifacts detected')
        
        except Exception:
            pass
        
        return indicators
    
    async def _verify_cryptographic_integrity(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify cryptographic signatures and integrity."""        verification = {
            'signature_valid': False,
            'certificate_valid': False,
            'chain_of_trust': False,
            'timestamp_valid': False
        }
        
        try:
            if metadata and 'digital_signature' in metadata:
                signature_data = metadata['digital_signature']
                
                # Verify digital signature (simplified)
                if 'signature' in signature_data and 'public_key' in signature_data:
                    verification['signature_valid'] = await self._verify_digital_signature(
                        content_data, signature_data['signature'], signature_data['public_key']
                    )
                
                # Check certificate validity
                if 'certificate' in signature_data:
                    verification['certificate_valid'] = self._verify_certificate(signature_data['certificate'])
                
                # Verify timestamp
                if 'timestamp' in signature_data:
                    verification['timestamp_valid'] = self._verify_timestamp(signature_data['timestamp'])
        
        except Exception as e:
            verification['error'] = f'Cryptographic verification error: {str(e)}'
        
        return verification
    
    async def _verify_digital_signature(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        signature: str,
        public_key: str
    ) -> bool:
        """Verify digital signature (simplified implementation)."""        try:
            # This is a placeholder - real implementation would use proper cryptographic verification
            # Load public key, verify signature against content hash
            
            # Get content bytes
            if isinstance(content_data, bytes):
                content_bytes = content_data
            elif isinstance(content_data, str):
                content_bytes = content_data.encode('utf-8')
            else:
                content_bytes = str(content_data).encode('utf-8')
            
            # Calculate content hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # In a real implementation, this would verify the signature
            # For now, just check if signature and key are present
            return bool(signature and public_key and len(signature) > 10)
            
        except Exception:
            return False
    
    def _verify_certificate(self, certificate: str) -> bool:
        """Verify digital certificate."""        # Placeholder for certificate verification
        return bool(certificate and len(certificate) > 50)
    
    def _verify_timestamp(self, timestamp: str) -> bool:
        """Verify timestamp validity."""        try:
            # Check if timestamp is reasonable (within last 10 years)
            ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            ten_years_ago = now - timedelta(days=365*10)
            
            return ten_years_ago <= ts <= now
        except Exception:
            return False
    
    def _calculate_integrity_score(
        self,
        format_verification: Dict[str, Any],
        checksum_verification: Dict[str, Any],
        content_analysis: Dict[str, Any],
        metadata_verification: Dict[str, Any],
        authenticity_indicators: Dict[str, Any],
        issues_found: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall integrity score."""        score_components = []
        
        # Format verification (30%)
        if format_verification.get('valid', False):
            format_score = 1.0
            if not format_verification.get('signature_valid', False):
                format_score -= 0.3
            if not format_verification.get('structure_valid', False):
                format_score -= 0.4
            if not format_verification.get('size_valid', False):
                format_score -= 0.2
        else:
            format_score = 0.0
        
        score_components.append(('format', format_score, 0.3))
        
        # Checksum verification (25%)
        checksum_score = 1.0 if checksum_verification.get('integrity_preserved', True) else 0.0
        score_components.append(('checksum', checksum_score, 0.25))
        
        # Content analysis (25%)
        if content_analysis.get('corruption_detected', False):
            content_score = 0.0
        else:
            content_score = 1.0
            # Reduce score for suspicious entropy
            if content_analysis.get('entropy_analysis', {}).get('suspicious', False):
                content_score -= 0.3
        
        score_components.append(('content', content_score, 0.25))
        
        # Metadata verification (10%)
        metadata_score = 1.0 if metadata_verification.get('metadata_valid', True) else 0.3
        score_components.append(('metadata', metadata_score, 0.1))
        
        # Authenticity (10%)
        authenticity_score = authenticity_indicators.get('confidence', 0.7)
        score_components.append(('authenticity', authenticity_score, 0.1))
        
        # Calculate weighted score
        weighted_score = sum(score * weight for _, score, weight in score_components)
        
        # Apply penalty for critical issues
        critical_issues = sum(1 for issue in issues_found if issue.get('severity') == 'critical')
        issue_penalty = min(0.5, critical_issues * 0.2)
        
        final_score = max(0.0, weighted_score - issue_penalty)
        
        return round(final_score, 3)
    
    def _determine_integrity_status(
        self,
        integrity_score: float,
        issues_found: List[Dict[str, Any]]
    ) -> IntegrityStatus:
        """Determine overall integrity status."""        critical_issues = [issue for issue in issues_found if issue.get('severity') == 'critical']
        
        if critical_issues:
            if any('corruption' in issue.get('type', '') for issue in critical_issues):
                return IntegrityStatus.CORRUPTED
            else:
                return IntegrityStatus.SUSPICIOUS
        
        if integrity_score >= 0.8:
            return IntegrityStatus.VERIFIED
        elif integrity_score >= 0.5:
            return IntegrityStatus.SUSPICIOUS
        else:
            return IntegrityStatus.CORRUPTED
    
    def _generate_integrity_recommendations(
        self,
        issues_found: List[Dict[str, Any]],
        format_verification: Dict[str, Any],
        content_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate integrity improvement recommendations."""        recommendations = []
        
        # Format-based recommendations
        if not format_verification.get('valid', True):
            recommendations.append('Verify file format and re-encode if necessary')
            
            if not format_verification.get('signature_valid', True):
                recommendations.append('File signature invalid - check file integrity')
            
            if not format_verification.get('structure_valid', True):
                recommendations.append('File structure corrupted - restore from backup')
        
        # Content-based recommendations
        if content_analysis.get('corruption_detected', False):
            recommendations.append('Content corruption detected - restore from original source')
        
        entropy_analysis = content_analysis.get('entropy_analysis', {})
        if entropy_analysis.get('suspicious', False):
            recommendations.append('Unusual data patterns detected - verify content authenticity')
        
        # Issue-specific recommendations
        for issue in issues_found:
            issue_type = issue.get('type', '')
            if issue_type == 'corruption':
                recommendations.append('Restore content from uncorrupted backup')
            elif issue_type == 'format_error':
                recommendations.append('Convert content to standard format')
            elif issue_type == 'metadata_tampering':
                recommendations.append('Verify metadata authenticity and source')
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_confidence_level(
        self,
        checks_performed: List[str],
        integrity_score: float,
        issues_found: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence level in integrity assessment."""        confidence_factors = []
        
        # Completeness of checks
        expected_checks = ['format_verification', 'checksum_verification', 'content_analysis', 'metadata_verification']
        completeness = len([check for check in expected_checks if check in checks_performed]) / len(expected_checks)
        confidence_factors.append(completeness)
        
        # Integrity score influence
        confidence_factors.append(integrity_score)
        
        # Inverse of critical issues
        critical_issues = sum(1 for issue in issues_found if issue.get('severity') == 'critical')
        issue_confidence = max(0.3, 1.0 - critical_issues * 0.2)
        confidence_factors.append(issue_confidence)
        
        return round(np.mean(confidence_factors), 3)
    
    async def _validate_exif_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate EXIF metadata structure."""        # Placeholder for EXIF validation
        return True
    
    async def _validate_id3_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate ID3 metadata structure."""        # Placeholder for ID3 validation
        return True
    
    async def _validate_xmp_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate XMP metadata structure."""        # Placeholder for XMP validation
        return True
    
    async def _validate_iptc_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate IPTC metadata structure."""        # Placeholder for IPTC validation
        return True


class ContentIntegrityVerifier:
    """    Specialized content integrity verifier for IA Influencer platform.
    
    Provides advanced content authenticity verification, tamper detection,
    and digital fingerprinting for creator content protection.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ContentIntegrityVerifier")
        
        # Content-specific integrity thresholds
        self.integrity_thresholds = {
            'min_entropy': 0.5,
            'max_compression_artifacts': 0.3,
            'min_signal_consistency': 0.8,
            'max_tampering_indicators': 3,
            'min_authenticity_score': 0.7
        }
        
        # Known content signatures for verification
        self.content_signatures = {
            'audio': {
                'natural_noise_patterns': True,
                'frequency_distribution_natural': True,
                'dynamic_range_realistic': True
            },
            'video': {
                'frame_consistency': True,
                'motion_vectors_realistic': True,
                'compression_artifacts_normal': True
            },
            'image': {
                'noise_patterns_natural': True,
                'jpeg_artifacts_consistent': True,
                'color_distribution_realistic': True
            }
        }
    
    async def verify_content_authenticity(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        expected_hash: Optional[str] = None,
        digital_signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive content authenticity verification."""        try:
            verification_result = {
                'authenticity_score': 0.0,
                'tamper_indicators': [],
                'digital_signature_valid': False,
                'hash_verification': False,
                'content_analysis': {},
                'confidence_level': 0.0,
                'recommendations': []
            }
            
            # Hash verification
            if expected_hash:
                calculated_hash = await self._calculate_content_hash(content_data)
                verification_result['hash_verification'] = calculated_hash == expected_hash
                if not verification_result['hash_verification']:
                    verification_result['tamper_indicators'].append({
                        'type': 'hash_mismatch',
                        'severity': 'critical',
                        'description': 'Content hash does not match expected value'
                    })
            
            # Digital signature verification
            if digital_signature:
                signature_valid = await self._verify_digital_signature(content_data, digital_signature)
                verification_result['digital_signature_valid'] = signature_valid
                if not signature_valid:
                    verification_result['tamper_indicators'].append({
                        'type': 'signature_invalid',
                        'severity': 'critical',
                        'description': 'Digital signature verification failed'
                    })
            
            # Content-specific analysis
            content_analysis = await self._analyze_content_authenticity(content_data, content_type)
            verification_result['content_analysis'] = content_analysis
            
            # Detect tampering indicators
            tampering_indicators = await self._detect_tampering_indicators(content_data, content_type)
            verification_result['tamper_indicators'].extend(tampering_indicators)
            
            # Calculate authenticity score
            authenticity_score = self._calculate_authenticity_score(verification_result)
            verification_result['authenticity_score'] = authenticity_score
            
            # Calculate confidence level
            confidence = self._calculate_verification_confidence(verification_result)
            verification_result['confidence_level'] = confidence
            
            # Generate recommendations
            recommendations = self._generate_authenticity_recommendations(verification_result)
            verification_result['recommendations'] = recommendations
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Content authenticity verification failed: {str(e)}")
            return {
                'error': f'Authenticity verification failed: {str(e)}',
                'authenticity_score': 0.0,
                'confidence_level': 0.0
            }
    
    async def _calculate_content_hash(self, content_data: Union[bytes, str]) -> str:
        """Calculate SHA-256 hash of content."""        if isinstance(content_data, str):
            if os.path.exists(content_data):
                with open(content_data, 'rb') as f:
                    content_bytes = f.read()
            else:
                content_bytes = content_data.encode('utf-8')
        else:
            content_bytes = content_data
        
        return hashlib.sha256(content_bytes).hexdigest()
    
    async def _verify_digital_signature(self, content_data: Union[bytes, str], signature: str) -> bool:
        """Verify digital signature of content."""        try:
            # Simplified digital signature verification
            # In a real implementation, this would use proper cryptographic libraries
            
            # Calculate content hash
            content_hash = await self._calculate_content_hash(content_data)
            
            # For demonstration, check if signature contains content hash
            # Real implementation would use RSA/DSA verification
            return content_hash in signature
            
        except Exception as e:
            self.logger.error(f"Digital signature verification failed: {str(e)}")
            return False
    
    async def _analyze_content_authenticity(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze content for authenticity indicators."""        analysis = {
            'entropy_analysis': {},
            'pattern_analysis': {},
            'compression_analysis': {},
            'metadata_consistency': {}
        }
        
        try:
            if content_type == 'audio' and HAS_MEDIA_LIBS:
                analysis = await self._analyze_audio_authenticity(content_data)
            elif content_type == 'video' and HAS_MEDIA_LIBS:
                analysis = await self._analyze_video_authenticity(content_data)
            elif content_type == 'image' and HAS_MEDIA_LIBS:
                analysis = await self._analyze_image_authenticity(content_data)
            elif content_type == 'text':
                analysis = await self._analyze_text_authenticity(content_data)
            else:
                analysis = await self._analyze_generic_authenticity(content_data)
            
        except Exception as e:
            self.logger.error(f"Content authenticity analysis failed: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_audio_authenticity(self, audio_data: Union[bytes, str]) -> Dict[str, Any]:
        """Analyze audio content for authenticity indicators."""        analysis = {}
        
        try:
            # Load audio
            if isinstance(audio_data, str):
                y, sr = librosa.load(audio_data, sr=None)
            else:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                y, sr = librosa.load(tmp_path, sr=None)
                os.unlink(tmp_path)
            
            # Entropy analysis
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            entropy = -np.sum(magnitude * np.log2(magnitude + 1e-10), axis=0)
            
            analysis['entropy_analysis'] = {
                'mean_entropy': float(np.mean(entropy)),
                'entropy_variance': float(np.var(entropy)),
                'entropy_suspicious': np.mean(entropy) < self.integrity_thresholds['min_entropy']
            }
            
            # Frequency distribution analysis
            fft = np.fft.fft(y)
            freq_magnitude = np.abs(fft)
            freq_distribution = freq_magnitude / np.sum(freq_magnitude)
            
            # Check for unnatural frequency spikes (potential tampering)
            freq_peaks = np.where(freq_distribution > np.mean(freq_distribution) + 3 * np.std(freq_distribution))[0]
            
            analysis['pattern_analysis'] = {
                'frequency_peaks': len(freq_peaks),
                'unnatural_peaks': len(freq_peaks) > 10,  # Threshold for suspicious peaks
                'frequency_distribution_natural': len(freq_peaks) <= 10
            }
            
            # Dynamic range analysis
            rms = librosa.feature.rms(y=y)[0]
            dynamic_range = np.max(rms) - np.min(rms)
            
            analysis['compression_analysis'] = {
                'dynamic_range': float(dynamic_range),
                'over_compressed': dynamic_range < 0.1,
                'compression_artifacts_detected': dynamic_range < 0.05
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_video_authenticity(self, video_data: Union[bytes, str]) -> Dict[str, Any]:
        """Analyze video content for authenticity indicators."""        analysis = {}
        
        try:
            # Load video
            if isinstance(video_data, str):
                video_path = video_data
            else:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                    tmp_file.write(video_data)
                    video_path = tmp_file.name
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                analysis['error'] = 'Could not open video file'
                return analysis
            
            # Analyze frame consistency
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, frame_count)
            frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
            
            frame_differences = []
            prev_frame = None
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret and prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(frame, prev_frame)
                    diff_mean = np.mean(diff)
                    frame_differences.append(diff_mean)
                
                prev_frame = frame
            
            cap.release()
            
            # Clean up temporary file
            if isinstance(video_data, bytes) and os.path.exists(video_path):
                os.unlink(video_path)
            
            # Analyze frame consistency
            if frame_differences:
                frame_consistency = 1.0 - (np.std(frame_differences) / np.mean(frame_differences))
                
                analysis['pattern_analysis'] = {
                    'frame_consistency': float(frame_consistency),
                    'frame_tampering_detected': frame_consistency < 0.7,
                    'consistent_motion': frame_consistency > 0.8
                }
            
            # Entropy analysis (simplified)
            analysis['entropy_analysis'] = {
                'frame_entropy_consistent': True,  # Simplified
                'compression_artifacts_normal': True
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_image_authenticity(self, image_data: Union[bytes, str]) -> Dict[str, Any]:
        """Analyze image content for authenticity indicators."""        analysis = {}
        
        try:
            # Load image
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
                pil_image = Image.open(image_data)
            else:
                image_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                pil_image = Image.open(io.BytesIO(image_data))
            
            if image is None:
                analysis['error'] = 'Could not load image'
                return analysis
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Entropy analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            prob = hist / np.sum(hist)
            entropy = -np.sum(prob * np.log2(prob + 1e-10))
            
            analysis['entropy_analysis'] = {
                'image_entropy': float(entropy),
                'entropy_suspicious': entropy < 5.0,  # Low entropy might indicate tampering
                'natural_distribution': entropy > 6.0
            }
            
            # JPEG compression analysis (if JPEG)
            if pil_image.format == 'JPEG':
                # Analyze DCT coefficients for tampering
                # Simplified analysis - real implementation would be more complex
                quality_estimate = self._estimate_jpeg_quality(image)
                
                analysis['compression_analysis'] = {
                    'estimated_quality': quality_estimate,
                    'multiple_compression_detected': quality_estimate < 70,
                    'compression_artifacts_suspicious': quality_estimate < 50
                }
            
            # Noise pattern analysis
            noise = cv2.subtract(gray, cv2.GaussianBlur(gray, (5, 5), 0))
            noise_std = np.std(noise)
            
            analysis['pattern_analysis'] = {
                'noise_consistency': float(noise_std),
                'unnatural_noise': noise_std < 5.0 or noise_std > 50.0,
                'noise_pattern_natural': 5.0 <= noise_std <= 50.0
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_text_authenticity(self, text_data: Union[bytes, str]) -> Dict[str, Any]:
        """Analyze text content for authenticity indicators."""        analysis = {}
        
        try:
            if isinstance(text_data, bytes):
                text = text_data.decode('utf-8', errors='ignore')
            else:
                text = text_data
            
            # Character distribution analysis
            char_counts = {}
            for char in text:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            # Calculate entropy
            total_chars = len(text)
            if total_chars > 0:
                entropy = -sum((count / total_chars) * np.log2(count / total_chars) 
                              for count in char_counts.values())
                
                analysis['entropy_analysis'] = {
                    'text_entropy': float(entropy),
                    'entropy_suspicious': entropy < 3.0 or entropy > 8.0,
                    'natural_distribution': 3.0 <= entropy <= 8.0
                }
            
            # Pattern analysis
            word_count = len(text.split())
            unique_words = len(set(text.lower().split()))
            lexical_diversity = unique_words / word_count if word_count > 0 else 0
            
            analysis['pattern_analysis'] = {
                'lexical_diversity': float(lexical_diversity),
                'repetitive_content': lexical_diversity < 0.3,
                'natural_variation': lexical_diversity > 0.5
            }
            
            # Check for potential AI-generated content indicators
            # Simplified analysis - real implementation would use more sophisticated methods
            sentence_lengths = [len(sent.split()) for sent in text.split('.') if sent.strip()]
            if sentence_lengths:
                avg_sentence_length = np.mean(sentence_lengths)
                sentence_length_variance = np.var(sentence_lengths)
                
                analysis['ai_detection'] = {
                    'avg_sentence_length': float(avg_sentence_length),
                    'sentence_variance': float(sentence_length_variance),
                    'potentially_ai_generated': (avg_sentence_length > 20 and sentence_length_variance < 10)
                }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_generic_authenticity(self, content_data: Union[bytes, str]) -> Dict[str, Any]:
        """Generic authenticity analysis for unknown content types."""        analysis = {}
        
        try:
            if isinstance(content_data, str):
                data_bytes = content_data.encode('utf-8')
            else:
                data_bytes = content_data
            
            # Basic entropy analysis
            byte_counts = {}
            for byte in data_bytes:
                byte_counts[byte] = byte_counts.get(byte, 0) + 1
            
            total_bytes = len(data_bytes)
            if total_bytes > 0:
                entropy = -sum((count / total_bytes) * np.log2(count / total_bytes) 
                              for count in byte_counts.values())
                
                analysis['entropy_analysis'] = {
                    'data_entropy': float(entropy),
                    'entropy_suspicious': entropy < 2.0 or entropy > 7.8,
                    'natural_distribution': 2.0 <= entropy <= 7.8
                }
            
            # Pattern analysis
            # Check for repetitive patterns
            chunk_size = min(1024, len(data_bytes) // 10)
            if chunk_size > 0:
                chunks = [data_bytes[i:i + chunk_size] for i in range(0, len(data_bytes), chunk_size)]
                unique_chunks = len(set(chunks))
                chunk_diversity = unique_chunks / len(chunks) if chunks else 0
                
                analysis['pattern_analysis'] = {
                    'chunk_diversity': float(chunk_diversity),
                    'repetitive_patterns': chunk_diversity < 0.7,
                    'natural_variation': chunk_diversity > 0.8
                }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _detect_tampering_indicators(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Detect potential tampering indicators in content."""        indicators = []
        
        try:
            # Check for metadata inconsistencies
            if content_type in ['image', 'audio', 'video']:
                metadata_indicators = await self._check_metadata_tampering(content_data, content_type)
                indicators.extend(metadata_indicators)
            
            # Check for file format inconsistencies
            format_indicators = await self._check_format_tampering(content_data, content_type)
            indicators.extend(format_indicators)
            
            # Check for compression inconsistencies
            if content_type in ['image', 'video', 'audio']:
                compression_indicators = await self._check_compression_tampering(content_data, content_type)
                indicators.extend(compression_indicators)
            
        except Exception as e:
            self.logger.error(f"Tampering detection failed: {str(e)}")
            indicators.append({
                'type': 'detection_error',
                'severity': 'warning',
                'description': f'Tampering detection failed: {str(e)}'
            })
        
        return indicators
    
    async def _check_metadata_tampering(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Check for metadata tampering indicators."""        indicators = []
        
        try:
            if content_type == 'image' and HAS_MEDIA_LIBS:
                # Check for EXIF inconsistencies
                if isinstance(content_data, str):
                    pil_image = Image.open(content_data)
                else:
                    pil_image = Image.open(io.BytesIO(content_data))
                
                exif_data = pil_image._getexif() if hasattr(pil_image, '_getexif') else None
                
                if exif_data:
                    # Check for common tampering indicators
                    if 'DateTime' in exif_data and 'DateTimeOriginal' in exif_data:
                        # Dates should be close or identical
                        # This is a simplified check
                        pass
                    
                    # Check for software signatures that might indicate editing
                    software = exif_data.get('Software', '')
                    if any(editor in software.lower() for editor in ['photoshop', 'gimp', 'editor']):
                        indicators.append({
                            'type': 'metadata_editing_software',
                            'severity': 'warning',
                            'description': f'Image processed with editing software: {software}'
                        })
                
            elif content_type == 'audio' and HAS_MEDIA_LIBS:
                # Check audio metadata for inconsistencies
                if isinstance(content_data, str):
                    mutagen_file = MutagenFile(content_data)
                    if mutagen_file:
                        # Check for encoding inconsistencies
                        # This is a simplified check
                        pass
            
        except Exception as e:
            self.logger.debug(f"Metadata tampering check failed: {str(e)}")
        
        return indicators
    
    async def _check_format_tampering(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Check for file format tampering indicators."""        indicators = []
        
        try:
            if isinstance(content_data, str):
                # Check file extension vs actual format
                file_ext = os.path.splitext(content_data)[1].lower()
                
                # Detect actual file type
                with open(content_data, 'rb') as f:
                    file_header = f.read(512)
                
                actual_type = magic.from_buffer(file_header, mime=True)
                
                # Simple format consistency check
                expected_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.mp3': 'audio/mpeg',
                    '.wav': 'audio/wav',
                    '.mp4': 'video/mp4',
                    '.avi': 'video/x-msvideo'
                }
                
                if file_ext in expected_types:
                    expected_type = expected_types[file_ext]
                    if actual_type != expected_type:
                        indicators.append({
                            'type': 'format_mismatch',
                            'severity': 'warning',
                            'description': f'File extension {file_ext} does not match detected type {actual_type}'
                        })
            
        except Exception as e:
            self.logger.debug(f"Format tampering check failed: {str(e)}")
        
        return indicators
    
    async def _check_compression_tampering(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Check for compression tampering indicators."""        indicators = []
        
        try:
            # This would implement more sophisticated compression analysis
            # For now, placeholder implementation
            pass
            
        except Exception as e:
            self.logger.debug(f"Compression tampering check failed: {str(e)}")
        
        return indicators
    
    def _estimate_jpeg_quality(self, image: np.ndarray) -> int:
        """Estimate JPEG quality from image analysis."""        # Simplified JPEG quality estimation
        # Real implementation would analyze DCT coefficients
        
        # Calculate image sharpness as proxy for quality
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Map sharpness to quality estimate (simplified)
        if laplacian_var > 1000:
            return 95
        elif laplacian_var > 500:
            return 85
        elif laplacian_var > 200:
            return 75
        elif laplacian_var > 100:
            return 65
        else:
            return 50
    
    def _calculate_authenticity_score(self, verification_result: Dict[str, Any]) -> float:
        """Calculate overall authenticity score."""        score_factors = []
        
        # Hash verification (40% weight)
        if verification_result.get('hash_verification', False):
            score_factors.append(1.0 * 0.4)
        else:
            score_factors.append(0.0 * 0.4)
        
        # Digital signature verification (30% weight)
        if verification_result.get('digital_signature_valid', False):
            score_factors.append(1.0 * 0.3)
        else:
            score_factors.append(0.5 * 0.3)  # Not having signature is not as bad as invalid signature
        
        # Content analysis (30% weight)
        content_analysis = verification_result.get('content_analysis', {})
        content_score = 0.8  # Default neutral score
        
        entropy_analysis = content_analysis.get('entropy_analysis', {})
        if 'entropy_suspicious' in entropy_analysis:
            if not entropy_analysis['entropy_suspicious']:
                content_score = max(content_score, 0.9)
            else:
                content_score = min(content_score, 0.4)
        
        score_factors.append(content_score * 0.3)
        
        # Penalty for tampering indicators
        tamper_indicators = verification_result.get('tamper_indicators', [])
        critical_indicators = sum(1 for indicator in tamper_indicators 
                                if indicator.get('severity') == 'critical')
        warning_indicators = sum(1 for indicator in tamper_indicators 
                               if indicator.get('severity') == 'warning')
        
        tampering_penalty = min(0.5, critical_indicators * 0.2 + warning_indicators * 0.1)
        
        final_score = max(0.0, sum(score_factors) - tampering_penalty)
        
        return round(final_score, 3)
    
    def _calculate_verification_confidence(self, verification_result: Dict[str, Any]) -> float:
        """Calculate confidence in verification result."""        confidence_factors = []
        
        # Data availability
        if verification_result.get('hash_verification') is not None:
            confidence_factors.append(0.3)
        if verification_result.get('digital_signature_valid') is not None:
            confidence_factors.append(0.3)
        if verification_result.get('content_analysis'):
            confidence_factors.append(0.4)
        
        # Analysis completeness
        content_analysis = verification_result.get('content_analysis', {})
        analysis_completeness = len([k for k in content_analysis.keys() if not k == 'error']) / 3
        confidence_factors.append(analysis_completeness * 0.2)
        
        # Error penalty
        if 'error' in content_analysis:
            confidence_factors = [f * 0.7 for f in confidence_factors]  # Reduce confidence
        
        return round(sum(confidence_factors), 3)
    
    def _generate_authenticity_recommendations(self, verification_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on authenticity verification."""        recommendations = []
        
        if not verification_result.get('hash_verification', True):
            recommendations.append('Content hash verification failed - verify source authenticity')
        
        if not verification_result.get('digital_signature_valid', True):
            recommendations.append('Digital signature invalid - verify content source and integrity')
        
        tamper_indicators = verification_result.get('tamper_indicators', [])
        if tamper_indicators:
            critical_count = sum(1 for indicator in tamper_indicators 
                               if indicator.get('severity') == 'critical')
            if critical_count > 0:
                recommendations.append('Critical tampering indicators detected - content may be compromised')
            else:
                recommendations.append('Potential content modifications detected - verify authenticity')
        
        authenticity_score = verification_result.get('authenticity_score', 0.0)
        if authenticity_score < 0.5:
            recommendations.append('Low authenticity score - implement additional verification measures')
        elif authenticity_score < 0.7:
            recommendations.append('Moderate authenticity concerns - consider additional validation')
        
        content_analysis = verification_result.get('content_analysis', {})
        if 'ai_detection' in content_analysis:
            ai_detection = content_analysis['ai_detection']
            if ai_detection.get('potentially_ai_generated', False):
                recommendations.append('Content may be AI-generated - verify human authorship if required')
        
        return recommendations


class MetadataIntegrityChecker:
    """    Specialized metadata integrity checker for comprehensive metadata validation.
    
    Provides advanced metadata verification, consistency checking, and preservation
    validation for all content types in the IA Influencer platform.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.MetadataIntegrityChecker")
        
        # Metadata validation rules
        self.validation_rules = {
            'required_fields': {
                'audio': ['title', 'artist', 'duration'],
                'video': ['title', 'duration', 'resolution'],
                'image': ['title', 'dimensions', 'format'],
                'text': ['title', 'author', 'word_count']
            },
            'field_formats': {
                'duration': r'^\d+(\.\d+)?$',  # Numeric duration
                'resolution': r'^\d+x\d+$',    # Width x Height
                'date': r'^\d{4}-\d{2}-\d{2}$' # YYYY-MM-DD
            },
            'allowed_encodings': ['utf-8', 'ascii', 'latin-1']
        }
    
    async def check_metadata_integrity(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        expected_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive metadata integrity checking."""        try:
            integrity_result = {
                'metadata_valid': False,
                'missing_fields': [],
                'invalid_fields': [],
                'consistency_score': 0.0,
                'preservation_score': 0.0,
                'extracted_metadata': {},
                'validation_errors': [],
                'recommendations': []
            }
            
            # Extract metadata from content
            extracted_metadata = await self._extract_metadata(content_data, content_type)
            integrity_result['extracted_metadata'] = extracted_metadata
            
            # Validate required fields
            missing_fields = await self._check_required_fields(extracted_metadata, content_type)
            integrity_result['missing_fields'] = missing_fields
            
            # Validate field formats
            invalid_fields = await self._validate_field_formats(extracted_metadata)
            integrity_result['invalid_fields'] = invalid_fields
            
            # Check metadata consistency
            consistency_score = await self._check_metadata_consistency(extracted_metadata, content_type)
            integrity_result['consistency_score'] = consistency_score
            
            # Check preservation quality
            preservation_score = await self._check_preservation_quality(extracted_metadata, expected_metadata)
            integrity_result['preservation_score'] = preservation_score
            
            # Determine overall validity
            integrity_result['metadata_valid'] = (
                len(missing_fields) == 0 and 
                len(invalid_fields) == 0 and 
                consistency_score > 0.7
            )
            
            # Generate recommendations
            recommendations = await self._generate_metadata_recommendations(integrity_result)
            integrity_result['recommendations'] = recommendations
            
            return integrity_result
            
        except Exception as e:
            self.logger.error(f"Metadata integrity check failed: {str(e)}")
            return {
                'error': f'Metadata integrity check failed: {str(e)}',
                'metadata_valid': False,
                'consistency_score': 0.0,
                'preservation_score': 0.0
            }
    
    async def _extract_metadata(
        self,
        content_data: Union[bytes, str],
        content_type: str
    ) -> Dict[str, Any]:
        """Extract metadata from content based on type."""        metadata = {}
        
        try:
            if content_type == 'audio' and HAS_MEDIA_LIBS:
                metadata = await self._extract_audio_metadata(content_data)
            elif content_type == 'video' and HAS_MEDIA_LIBS:
                metadata = await self._extract_video_metadata(content_data)
            elif content_type == 'image' and HAS_MEDIA_LIBS:
                metadata = await self._extract_image_metadata(content_data)
            elif content_type == 'text':
                metadata = await self._extract_text_metadata(content_data)
            else:
                metadata = await self._extract_generic_metadata(content_data)
                
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_audio_metadata(self, audio_data: Union[bytes, str]) -> Dict[str, Any]:
        """Extract audio metadata."""        metadata = {}
        
        try:
            if isinstance(audio_data, str):
                # File path
                mutagen_file = MutagenFile(audio_data)
                if mutagen_file:
                    metadata.update(dict(mutagen_file))
                
                # Additional librosa metadata
                y, sr = librosa.load(audio_data, sr=None)
                duration = len(y) / sr
                metadata['duration'] = duration
                metadata['sample_rate'] = sr
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    async def _extract_video_metadata(self, video_data: Union[bytes, str]) -> Dict[str, Any]:
        """Extract video metadata."""        metadata = {}
        
        try:
            if isinstance(video_data, str):
                cap = cv2.VideoCapture(video_data)
                
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    duration = frame_count / fps if fps > 0 else 0
                    
                    metadata.update({
                        'fps': fps,
                        'frame_count': frame_count,
                        'resolution': f'{width}x{height}',
                        'width': width,
                        'height': height,
                        'duration': duration
                    })
                
                cap.release()
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    async def _extract_image_metadata(self, image_data: Union[bytes, str]) -> Dict[str, Any]:
        """Extract image metadata."""        metadata = {}
        
        try:
            if isinstance(image_data, str):
                pil_image = Image.open(image_data)
            else:
                pil_image = Image.open(io.BytesIO(image_data))
            
            # Basic image properties
            metadata.update({
                'dimensions': f'{pil_image.width}x{pil_image.height}',
                'width': pil_image.width,
                'height': pil_image.height,
                'format': pil_image.format,
                'mode': pil_image.mode
            })
            
            # EXIF data
            if hasattr(pil_image, '_getexif') and pil_image._getexif():
                exif_data = pil_image._getexif()
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[f'exif_{tag}'] = value
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    async def _extract_text_metadata(self, text_data: Union[bytes, str]) -> Dict[str, Any]:
        """Extract text metadata."""        metadata = {}
        
        try:
            if isinstance(text_data, bytes):
                text = text_data.decode('utf-8', errors='ignore')
            else:
                text = text_data
            
            # Basic text properties
            word_count = len(text.split())
            char_count = len(text)
            line_count = len(text.split('\n'))
            
            metadata.update({
                'word_count': word_count,
                'character_count': char_count,
                'line_count': line_count,
                'encoding': 'utf-8'
            })
            
            # Language detection
            try:
                from langdetect import detect
                detected_language = detect(text)
                metadata['language'] = detected_language
            except:
                metadata['language'] = 'unknown'
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    async def _extract_generic_metadata(self, content_data: Union[bytes, str]) -> Dict[str, Any]:
        """Extract generic metadata."""        metadata = {}
        
        try:
            if isinstance(content_data, str):
                # File-based metadata
                if os.path.exists(content_data):
                    stat = os.stat(content_data)
                    metadata.update({
                        'file_size': stat.st_size,
                        'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    
                    # MIME type detection
                    mime_type = mimetypes.guess_type(content_data)[0]
                    if mime_type:
                        metadata['mime_type'] = mime_type
            else:
                # Bytes metadata
                metadata.update({
                    'data_size': len(content_data),
                    'data_type': 'bytes'
                })
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    async def _check_required_fields(
        self,
        metadata: Dict[str, Any],
        content_type: str
    ) -> List[str]:
        """Check for missing required metadata fields."""        missing_fields = []
        
        required_fields = self.validation_rules['required_fields'].get(content_type, [])
        
        for field in required_fields:
            if field not in metadata or metadata[field] is None:
                missing_fields.append(field)
        
        return missing_fields
    
    async def _validate_field_formats(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate metadata field formats."""        invalid_fields = []
        
        field_formats = self.validation_rules['field_formats']
        
        for field, pattern in field_formats.items():
            if field in metadata:
                value = str(metadata[field])
                if not re.match(pattern, value):
                    invalid_fields.append({
                        'field': field,
                        'value': value,
                        'expected_format': pattern
                    })
        
        return invalid_fields
    
    async def _check_metadata_consistency(
        self,
        metadata: Dict[str, Any],
        content_type: str
    ) -> float:
        """Check internal metadata consistency."""        consistency_score = 1.0
        
        try:
            # Content-specific consistency checks
            if content_type == 'audio':
                # Check if duration matches sample rate and frame count
                if all(k in metadata for k in ['duration', 'sample_rate']):
                    # Placeholder for actual consistency check
                    pass
            
            elif content_type == 'video':
                # Check if duration matches frame count and fps
                if all(k in metadata for k in ['duration', 'fps', 'frame_count']):
                    calculated_duration = metadata['frame_count'] / metadata['fps']
                    duration_diff = abs(metadata['duration'] - calculated_duration)
                    if duration_diff > 1.0:  # More than 1 second difference
                        consistency_score -= 0.2
            
            elif content_type == 'image':
                # Check if dimensions are consistent
                if 'dimensions' in metadata and 'width' in metadata and 'height' in metadata:
                    expected_dimensions = f"{metadata['width']}x{metadata['height']}"
                    if metadata['dimensions'] != expected_dimensions:
                        consistency_score -= 0.3
            
            # Date consistency checks
            date_fields = [k for k in metadata.keys() if 'date' in k.lower() or 'time' in k.lower()]
            if len(date_fields) > 1:
                # Check if dates are logical (creation <= modification)
                # Simplified check
                pass
            
        except Exception as e:
            self.logger.debug(f"Consistency check failed: {str(e)}")
            consistency_score -= 0.1
        
        return max(0.0, consistency_score)
    
    async def _check_preservation_quality(
        self,
        extracted_metadata: Dict[str, Any],
        expected_metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Check metadata preservation quality."""        if not expected_metadata:
            return 0.8  # Default good preservation if no reference
        
        preservation_score = 1.0
        
        try:
            # Check for preserved critical fields
            critical_fields = ['title', 'author', 'created_time', 'duration', 'resolution']
            
            for field in critical_fields:
                if field in expected_metadata:
                    if field not in extracted_metadata:
                        preservation_score -= 0.2  # Missing critical field
                    elif extracted_metadata[field] != expected_metadata[field]:
                        preservation_score -= 0.1  # Modified critical field
            
            # Check for additional preserved fields
            expected_fields = set(expected_metadata.keys())
            extracted_fields = set(extracted_metadata.keys())
            
            preserved_fields = expected_fields.intersection(extracted_fields)
            preservation_ratio = len(preserved_fields) / len(expected_fields) if expected_fields else 1.0
            
            # Weight preservation ratio
            preservation_score = preservation_score * 0.7 + preservation_ratio * 0.3
            
        except Exception as e:
            self.logger.debug(f"Preservation check failed: {str(e)}")
            preservation_score -= 0.1
        
        return max(0.0, preservation_score)
    
    async def _generate_metadata_recommendations(
        self,
        integrity_result: Dict[str, Any]
    ) -> List[str]:
        """Generate metadata integrity recommendations."""        recommendations = []
        
        # Missing fields recommendations
        missing_fields = integrity_result.get('missing_fields', [])
        if missing_fields:
            recommendations.append(f"Add missing required fields: {', '.join(missing_fields)}")
        
        # Invalid fields recommendations
        invalid_fields = integrity_result.get('invalid_fields', [])
        if invalid_fields:
            for invalid_field in invalid_fields:
                field = invalid_field['field']
                expected_format = invalid_field['expected_format']
                recommendations.append(f"Fix format for {field}: expected {expected_format}")
        
        # Consistency recommendations
        consistency_score = integrity_result.get('consistency_score', 1.0)
        if consistency_score < 0.7:
            recommendations.append("Review metadata consistency - some fields may be inconsistent")
        
        # Preservation recommendations
        preservation_score = integrity_result.get('preservation_score', 1.0)
        if preservation_score < 0.8:
            recommendations.append("Improve metadata preservation - some information may be lost")
        
        # General recommendations
        if not integrity_result.get('metadata_valid', False):
            recommendations.append("Address metadata validation issues before content distribution")
        
        return recommendations
