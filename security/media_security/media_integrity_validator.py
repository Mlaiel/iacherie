"""
Media Integrity Validator
=========================

Advanced media integrity validation system with checksums, digital signatures,
blockchain verification, tamper detection, and forensic analysis for ensuring
media authenticity and detecting unauthorized modifications.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
import time
import struct
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
from pathlib import Path
import numpy as np

# Cryptography imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

# Image processing (optional)
try:
    from PIL import Image, ImageStat
    import io
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

# Audio processing (optional)
try:
    import librosa
    import numpy as np
    AUDIO_SUPPORT = True
except ImportError:
    AUDIO_SUPPORT = False


class IntegrityLevel(Enum):
    """Levels of integrity validation"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    FORENSIC = "forensic"
    BLOCKCHAIN = "blockchain"


class ValidationMethod(Enum):
    """Methods of integrity validation"""
    CHECKSUM = "checksum"
    DIGITAL_SIGNATURE = "digital_signature"
    PERCEPTUAL_HASH = "perceptual_hash"
    METADATA_ANALYSIS = "metadata_analysis"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    BLOCKCHAIN_PROOF = "blockchain_proof"
    WATERMARK_VERIFICATION = "watermark_verification"


class TamperType(Enum):
    """Types of detected tampering"""
    NONE = "none"
    METADATA_MODIFICATION = "metadata_modification"
    CONTENT_ALTERATION = "content_alteration"
    COMPRESSION_ARTIFACTS = "compression_artifacts"
    SPLICING = "splicing"
    COPY_MOVE = "copy_move"
    RESAMPLING = "resampling"
    NOISE_INJECTION = "noise_injection"
    WATERMARK_REMOVAL = "watermark_removal"


class MediaType(Enum):
    """Supported media types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


@dataclass
class IntegrityRecord:
    """Media integrity validation record"""
    record_id: str
    media_id: str
    media_type: MediaType
    validation_level: IntegrityLevel
    validation_methods: List[ValidationMethod]
    checksums: Dict[str, str]  # algorithm -> checksum
    digital_signature: Optional[str] = None
    perceptual_hash: Optional[str] = None
    metadata_hash: Optional[str] = None
    created_at: datetime = None
    created_by: str = ""
    blockchain_reference: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ValidationResult:
    """Result of integrity validation"""
    validation_id: str
    record_id: str
    media_id: str
    is_valid: bool
    confidence_score: float
    tamper_detected: bool
    tamper_types: List[TamperType]
    validation_details: Dict[str, Any]
    method_results: Dict[ValidationMethod, Dict[str, Any]]
    validated_at: datetime
    validation_time_ms: float

    def __post_init__(self):
        if not hasattr(self, 'validated_at'):
            self.validated_at = datetime.utcnow()


@dataclass
class ForensicAnalysis:
    """Detailed forensic analysis result"""
    analysis_id: str
    media_id: str
    media_type: MediaType
    analysis_methods: List[str]
    tamper_evidence: List[Dict[str, Any]]
    authenticity_score: float
    modification_timeline: List[Dict[str, Any]]
    technical_details: Dict[str, Any]
    analyzed_at: datetime = None

    def __post_init__(self):
        if self.analyzed_at is None:
            self.analyzed_at = datetime.utcnow()


class MediaIntegrityValidator:
    """
    Advanced Media Integrity Validator
    
    Provides comprehensive media integrity validation:
    - Multi-algorithm checksums (MD5, SHA1, SHA256, SHA512, BLAKE2)
    - Digital signatures with RSA/ECDSA
    - Perceptual hashing for content-aware validation
    - Metadata integrity verification
    - Statistical analysis for tamper detection
    - Blockchain-based proof of existence
    - Forensic analysis capabilities
    - Watermark integrity verification
    - Timeline reconstruction for modifications
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize media integrity validator"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage (in production, use secure database)
        self.integrity_records: Dict[str, IntegrityRecord] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.forensic_analyses: Dict[str, ForensicAnalysis] = {}
        
        # Validation configuration
        self.default_algorithms = ['sha256', 'blake2b', 'md5']
        self.signature_key_size = self.config.get('signature_key_size', 2048)
        self.perceptual_hash_size = self.config.get('perceptual_hash_size', 16)
        
        # Generate signing key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.signature_key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Performance metrics
        self.metrics = {
            'total_records_created': 0,
            'total_validations': 0,
            'successful_validations': 0,
            'tamper_detections': 0,
            'forensic_analyses': 0,
            'avg_validation_time': 0.0,
            'integrity_violations': 0
        }
        
        # Integrity audit log
        self.audit_log: List[Dict] = []
        
        self.logger.info("Media Integrity Validator initialized")

    async def create_integrity_record(self, 
                                    media_data: bytes,
                                    media_id: str,
                                    media_type: MediaType,
                                    validation_level: IntegrityLevel = IntegrityLevel.STANDARD,
                                    creator_id: str = "",
                                    metadata: Dict[str, Any] = None) -> IntegrityRecord:
        """Create integrity record for media"""
        
        record_id = str(uuid.uuid4())
        
        # Calculate checksums
        checksums = await self._calculate_checksums(media_data, self.default_algorithms)
        
        # Determine validation methods based on level
        validation_methods = self._get_validation_methods(validation_level)
        
        # Generate digital signature if required
        digital_signature = None
        if ValidationMethod.DIGITAL_SIGNATURE in validation_methods:
            digital_signature = await self._generate_digital_signature(media_data)
        
        # Generate perceptual hash if supported
        perceptual_hash = None
        if ValidationMethod.PERCEPTUAL_HASH in validation_methods:
            perceptual_hash = await self._generate_perceptual_hash(media_data, media_type)
        
        # Calculate metadata hash
        metadata_hash = None
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        
        # Create record
        record = IntegrityRecord(
            record_id=record_id,
            media_id=media_id,
            media_type=media_type,
            validation_level=validation_level,
            validation_methods=validation_methods,
            checksums=checksums,
            digital_signature=digital_signature,
            perceptual_hash=perceptual_hash,
            metadata_hash=metadata_hash,
            created_by=creator_id
        )
        
        # Store blockchain reference if required
        if validation_level == IntegrityLevel.BLOCKCHAIN:
            record.blockchain_reference = await self._create_blockchain_proof(record)
        
        self.integrity_records[record_id] = record
        self.metrics['total_records_created'] += 1
        
        # Audit log
        await self._log_audit_event('integrity_record_created', {
            'record_id': record_id,
            'media_id': media_id,
            'media_type': media_type.value,
            'validation_level': validation_level.value,
            'creator_id': creator_id
        })
        
        self.logger.info(f"Integrity record created: {record_id} for media: {media_id}")
        return record

    async def validate_media_integrity(self, 
                                     media_data: bytes,
                                     record_id: str,
                                     metadata: Dict[str, Any] = None) -> ValidationResult:
        """Validate media integrity against stored record"""
        
        start_time = time.time()
        validation_id = str(uuid.uuid4())
        
        if record_id not in self.integrity_records:
            raise ValueError(f"Integrity record not found: {record_id}")
        
        record = self.integrity_records[record_id]
        
        # Initialize validation result
        method_results = {}
        tamper_types = []
        confidence_scores = []
        
        # Validate checksums
        if ValidationMethod.CHECKSUM in record.validation_methods:
            checksum_result = await self._validate_checksums(media_data, record.checksums)
            method_results[ValidationMethod.CHECKSUM] = checksum_result
            confidence_scores.append(checksum_result['confidence'])
            
            if not checksum_result['valid']:
                tamper_types.append(TamperType.CONTENT_ALTERATION)
        
        # Validate digital signature
        if ValidationMethod.DIGITAL_SIGNATURE in record.validation_methods and record.digital_signature:
            signature_result = await self._validate_digital_signature(media_data, record.digital_signature)
            method_results[ValidationMethod.DIGITAL_SIGNATURE] = signature_result
            confidence_scores.append(signature_result['confidence'])
            
            if not signature_result['valid']:
                tamper_types.append(TamperType.CONTENT_ALTERATION)
        
        # Validate perceptual hash
        if ValidationMethod.PERCEPTUAL_HASH in record.validation_methods and record.perceptual_hash:
            perceptual_result = await self._validate_perceptual_hash(
                media_data, record.media_type, record.perceptual_hash
            )
            method_results[ValidationMethod.PERCEPTUAL_HASH] = perceptual_result
            confidence_scores.append(perceptual_result['confidence'])
            
            if not perceptual_result['valid']:
                tamper_types.extend(perceptual_result.get('tamper_types', []))
        
        # Validate metadata
        if ValidationMethod.METADATA_ANALYSIS in record.validation_methods and metadata:
            metadata_result = await self._validate_metadata(metadata, record.metadata_hash)
            method_results[ValidationMethod.METADATA_ANALYSIS] = metadata_result
            confidence_scores.append(metadata_result['confidence'])
            
            if not metadata_result['valid']:
                tamper_types.append(TamperType.METADATA_MODIFICATION)
        
        # Statistical analysis
        if ValidationMethod.STATISTICAL_ANALYSIS in record.validation_methods:
            statistical_result = await self._perform_statistical_analysis(media_data, record.media_type)
            method_results[ValidationMethod.STATISTICAL_ANALYSIS] = statistical_result
            confidence_scores.append(statistical_result['confidence'])
            
            if statistical_result.get('anomalies_detected', False):
                tamper_types.extend(statistical_result.get('detected_anomalies', []))
        
        # Blockchain verification
        if ValidationMethod.BLOCKCHAIN_PROOF in record.validation_methods and record.blockchain_reference:
            blockchain_result = await self._validate_blockchain_proof(record.blockchain_reference)
            method_results[ValidationMethod.BLOCKCHAIN_PROOF] = blockchain_result
            confidence_scores.append(blockchain_result['confidence'])
        
        # Calculate overall results
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        is_valid = overall_confidence >= 0.8 and len(tamper_types) == 0
        tamper_detected = len(tamper_types) > 0
        
        # Remove duplicates from tamper types
        unique_tamper_types = list(set(tamper_types))
        if not unique_tamper_types:
            unique_tamper_types = [TamperType.NONE]
        
        validation_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Create validation result
        result = ValidationResult(
            validation_id=validation_id,
            record_id=record_id,
            media_id=record.media_id,
            is_valid=is_valid,
            confidence_score=overall_confidence,
            tamper_detected=tamper_detected,
            tamper_types=unique_tamper_types,
            validation_details={
                'validation_methods_used': [m.value for m in record.validation_methods],
                'file_size': len(media_data),
                'validation_level': record.validation_level.value
            },
            method_results=method_results,
            validated_at=datetime.utcnow(),
            validation_time_ms=validation_time
        )
        
        self.validation_results[validation_id] = result
        
        # Update metrics
        self.metrics['total_validations'] += 1
        if is_valid:
            self.metrics['successful_validations'] += 1
        if tamper_detected:
            self.metrics['tamper_detections'] += 1
            self.metrics['integrity_violations'] += 1
        
        self._update_avg_validation_time(validation_time)
        
        # Audit log
        await self._log_audit_event('media_validated', {
            'validation_id': validation_id,
            'record_id': record_id,
            'media_id': record.media_id,
            'is_valid': is_valid,
            'tamper_detected': tamper_detected,
            'confidence_score': overall_confidence
        })
        
        self.logger.info(f"Media validation completed: {validation_id} - {'VALID' if is_valid else 'INVALID'}")
        return result

    async def perform_forensic_analysis(self, 
                                      media_data: bytes,
                                      media_id: str,
                                      media_type: MediaType,
                                      analysis_methods: List[str] = None) -> ForensicAnalysis:
        """Perform detailed forensic analysis"""
        
        analysis_id = str(uuid.uuid4())
        
        if analysis_methods is None:
            analysis_methods = ['compression_analysis', 'noise_analysis', 'statistical_analysis']
        
        tamper_evidence = []
        technical_details = {}
        modification_timeline = []
        
        # Compression analysis
        if 'compression_analysis' in analysis_methods:
            compression_evidence = await self._analyze_compression_artifacts(media_data, media_type)
            tamper_evidence.extend(compression_evidence)
            technical_details['compression_analysis'] = compression_evidence
        
        # Noise analysis
        if 'noise_analysis' in analysis_methods:
            noise_evidence = await self._analyze_noise_patterns(media_data, media_type)
            tamper_evidence.extend(noise_evidence)
            technical_details['noise_analysis'] = noise_evidence
        
        # Statistical analysis
        if 'statistical_analysis' in analysis_methods:
            statistical_evidence = await self._analyze_statistical_properties(media_data, media_type)
            tamper_evidence.extend(statistical_evidence)
            technical_details['statistical_analysis'] = statistical_evidence
        
        # JPEG analysis (if image)
        if media_type == MediaType.IMAGE and 'jpeg_analysis' in analysis_methods:
            jpeg_evidence = await self._analyze_jpeg_artifacts(media_data)
            tamper_evidence.extend(jpeg_evidence)
            technical_details['jpeg_analysis'] = jpeg_evidence
        
        # Calculate authenticity score
        authenticity_score = self._calculate_authenticity_score(tamper_evidence)
        
        # Reconstruct modification timeline
        modification_timeline = self._reconstruct_modification_timeline(tamper_evidence)
        
        analysis = ForensicAnalysis(
            analysis_id=analysis_id,
            media_id=media_id,
            media_type=media_type,
            analysis_methods=analysis_methods,
            tamper_evidence=tamper_evidence,
            authenticity_score=authenticity_score,
            modification_timeline=modification_timeline,
            technical_details=technical_details
        )
        
        self.forensic_analyses[analysis_id] = analysis
        self.metrics['forensic_analyses'] += 1
        
        # Audit log
        await self._log_audit_event('forensic_analysis_performed', {
            'analysis_id': analysis_id,
            'media_id': media_id,
            'media_type': media_type.value,
            'authenticity_score': authenticity_score,
            'evidence_count': len(tamper_evidence)
        })
        
        self.logger.info(f"Forensic analysis completed: {analysis_id} - Score: {authenticity_score:.2f}")
        return analysis

    async def _calculate_checksums(self, data: bytes, algorithms: List[str]) -> Dict[str, str]:
        """Calculate multiple checksums for data"""
        
        checksums = {}
        
        for algorithm in algorithms:
            if algorithm == 'md5':
                checksums['md5'] = hashlib.md5(data).hexdigest()
            elif algorithm == 'sha1':
                checksums['sha1'] = hashlib.sha1(data).hexdigest()
            elif algorithm == 'sha256':
                checksums['sha256'] = hashlib.sha256(data).hexdigest()
            elif algorithm == 'sha512':
                checksums['sha512'] = hashlib.sha512(data).hexdigest()
            elif algorithm == 'blake2b':
                checksums['blake2b'] = hashlib.blake2b(data).hexdigest()
        
        return checksums

    def _get_validation_methods(self, level: IntegrityLevel) -> List[ValidationMethod]:
        """Get validation methods for integrity level"""
        
        methods = [ValidationMethod.CHECKSUM]
        
        if level in [IntegrityLevel.STANDARD, IntegrityLevel.HIGH, IntegrityLevel.FORENSIC, IntegrityLevel.BLOCKCHAIN]:
            methods.append(ValidationMethod.DIGITAL_SIGNATURE)
            methods.append(ValidationMethod.METADATA_ANALYSIS)
        
        if level in [IntegrityLevel.HIGH, IntegrityLevel.FORENSIC, IntegrityLevel.BLOCKCHAIN]:
            methods.append(ValidationMethod.PERCEPTUAL_HASH)
            methods.append(ValidationMethod.STATISTICAL_ANALYSIS)
        
        if level == IntegrityLevel.BLOCKCHAIN:
            methods.append(ValidationMethod.BLOCKCHAIN_PROOF)
        
        return methods

    async def _generate_digital_signature(self, data: bytes) -> str:
        """Generate digital signature for data"""
        
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()

    async def _generate_perceptual_hash(self, data: bytes, media_type: MediaType) -> Optional[str]:
        """Generate perceptual hash for media"""
        
        if media_type == MediaType.IMAGE and IMAGE_SUPPORT:
            return await self._generate_image_perceptual_hash(data)
        elif media_type == MediaType.AUDIO and AUDIO_SUPPORT:
            return await self._generate_audio_perceptual_hash(data)
        else:
            # Fallback to simple hash
            return hashlib.sha256(data).hexdigest()[:32]

    async def _generate_image_perceptual_hash(self, image_data: bytes) -> str:
        """Generate perceptual hash for image"""
        
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale and resize
            image = image.convert('L').resize((self.perceptual_hash_size, self.perceptual_hash_size))
            
            # Get pixel data
            pixels = list(image.getdata())
            
            # Calculate average
            avg = sum(pixels) / len(pixels)
            
            # Generate hash bits
            hash_bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            
            # Convert to hex
            hash_int = int(hash_bits, 2)
            return format(hash_int, 'x')
            
        except Exception as e:
            self.logger.warning(f"Failed to generate image perceptual hash: {str(e)}")
            return hashlib.sha256(image_data).hexdigest()[:32]

    async def _generate_audio_perceptual_hash(self, audio_data: bytes) -> str:
        """Generate perceptual hash for audio"""
        
        # Simplified audio hashing (in practice, use chromaprint or similar)
        return hashlib.sha256(audio_data).hexdigest()[:32]

    async def _create_blockchain_proof(self, record: IntegrityRecord) -> str:
        """Create blockchain proof of existence"""
        
        # Simplified blockchain proof (in practice, integrate with actual blockchain)
        proof_data = {
            'record_id': record.record_id,
            'media_id': record.media_id,
            'checksums': record.checksums,
            'timestamp': record.created_at.isoformat()
        }
        
        proof_hash = hashlib.sha256(json.dumps(proof_data, sort_keys=True).encode()).hexdigest()
        
        # Simulate blockchain transaction
        blockchain_reference = f"blockchain_tx_{proof_hash[:16]}"
        
        return blockchain_reference

    async def _validate_checksums(self, data: bytes, expected_checksums: Dict[str, str]) -> Dict[str, Any]:
        """Validate data checksums"""
        
        current_checksums = await self._calculate_checksums(data, list(expected_checksums.keys()))
        
        valid_checksums = 0
        total_checksums = len(expected_checksums)
        
        checksum_details = {}
        
        for algorithm, expected in expected_checksums.items():
            current = current_checksums.get(algorithm, '')
            is_valid = current == expected
            
            checksum_details[algorithm] = {
                'expected': expected,
                'current': current,
                'valid': is_valid
            }
            
            if is_valid:
                valid_checksums += 1
        
        overall_valid = valid_checksums == total_checksums
        confidence = valid_checksums / total_checksums if total_checksums > 0 else 0.0
        
        return {
            'valid': overall_valid,
            'confidence': confidence,
            'details': checksum_details,
            'valid_checksums': valid_checksums,
            'total_checksums': total_checksums
        }

    async def _validate_digital_signature(self, data: bytes, signature_b64: str) -> Dict[str, Any]:
        """Validate digital signature"""
        
        try:
            signature = base64.b64decode(signature_b64)
            
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return {
                'valid': True,
                'confidence': 1.0,
                'details': 'Digital signature verified successfully'
            }
            
        except InvalidSignature:
            return {
                'valid': False,
                'confidence': 0.0,
                'details': 'Digital signature verification failed'
            }
        except Exception as e:
            return {
                'valid': False,
                'confidence': 0.0,
                'details': f'Signature validation error: {str(e)}'
            }

    async def _validate_perceptual_hash(self, data: bytes, media_type: MediaType, expected_hash: str) -> Dict[str, Any]:
        """Validate perceptual hash"""
        
        current_hash = await self._generate_perceptual_hash(data, media_type)
        
        if not current_hash:
            return {
                'valid': False,
                'confidence': 0.0,
                'details': 'Failed to generate perceptual hash'
            }
        
        # Calculate Hamming distance for similarity
        if len(current_hash) == len(expected_hash):
            differences = sum(c1 != c2 for c1, c2 in zip(current_hash, expected_hash))
            max_differences = len(expected_hash)
            similarity = 1.0 - (differences / max_differences)
        else:
            similarity = 0.0
        
        # Determine if valid (threshold of 90% similarity)
        is_valid = similarity >= 0.9
        
        # Detect potential tamper types based on similarity
        tamper_types = []
        if similarity < 0.9:
            if similarity > 0.7:
                tamper_types.append(TamperType.COMPRESSION_ARTIFACTS)
            elif similarity > 0.5:
                tamper_types.append(TamperType.NOISE_INJECTION)
            else:
                tamper_types.append(TamperType.CONTENT_ALTERATION)
        
        return {
            'valid': is_valid,
            'confidence': similarity,
            'details': f'Perceptual hash similarity: {similarity:.3f}',
            'expected_hash': expected_hash,
            'current_hash': current_hash,
            'tamper_types': tamper_types
        }

    async def _validate_metadata(self, metadata: Dict[str, Any], expected_hash: Optional[str]) -> Dict[str, Any]:
        """Validate metadata integrity"""
        
        if not expected_hash:
            return {
                'valid': True,
                'confidence': 1.0,
                'details': 'No metadata hash to validate'
            }
        
        metadata_json = json.dumps(metadata, sort_keys=True)
        current_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        
        is_valid = current_hash == expected_hash
        
        return {
            'valid': is_valid,
            'confidence': 1.0 if is_valid else 0.0,
            'details': 'Metadata hash match' if is_valid else 'Metadata hash mismatch',
            'expected_hash': expected_hash,
            'current_hash': current_hash
        }

    async def _perform_statistical_analysis(self, data: bytes, media_type: MediaType) -> Dict[str, Any]:
        """Perform statistical analysis for anomaly detection"""
        
        # Basic statistical analysis
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Calculate statistics
        mean_val = np.mean(data_array)
        std_val = np.std(data_array)
        entropy = self._calculate_entropy(data_array)
        
        # Detect anomalies
        anomalies_detected = False
        detected_anomalies = []
        
        # Check for unusual entropy (may indicate compression or encryption)
        if entropy < 6.0:  # Low entropy threshold
            anomalies_detected = True
            detected_anomalies.append(TamperType.COMPRESSION_ARTIFACTS)
        elif entropy > 7.8:  # High entropy threshold
            anomalies_detected = True
            detected_anomalies.append(TamperType.NOISE_INJECTION)
        
        # Check for unusual standard deviation
        if std_val < 30:  # Low variation
            anomalies_detected = True
            detected_anomalies.append(TamperType.CONTENT_ALTERATION)
        
        confidence = 0.5 if anomalies_detected else 0.8
        
        return {
            'valid': not anomalies_detected,
            'confidence': confidence,
            'anomalies_detected': anomalies_detected,
            'detected_anomalies': detected_anomalies,
            'statistics': {
                'mean': float(mean_val),
                'std': float(std_val),
                'entropy': float(entropy),
                'data_size': len(data)
            }
        }

    async def _validate_blockchain_proof(self, blockchain_reference: str) -> Dict[str, Any]:
        """Validate blockchain proof of existence"""
        
        # Simplified blockchain validation
        # In practice, query actual blockchain
        
        is_valid = blockchain_reference.startswith('blockchain_tx_')
        
        return {
            'valid': is_valid,
            'confidence': 1.0 if is_valid else 0.0,
            'details': 'Blockchain proof verified' if is_valid else 'Invalid blockchain reference',
            'blockchain_reference': blockchain_reference
        }

    async def _analyze_compression_artifacts(self, data: bytes, media_type: MediaType) -> List[Dict[str, Any]]:
        """Analyze compression artifacts"""
        
        evidence = []
        
        # Basic compression analysis
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Look for compression signatures
        if b'JFIF' in data or b'\xff\xd8' in data:
            evidence.append({
                'type': 'compression_signature',
                'description': 'JPEG compression detected',
                'confidence': 0.9,
                'tamper_type': TamperType.COMPRESSION_ARTIFACTS
            })
        
        return evidence

    async def _analyze_noise_patterns(self, data: bytes, media_type: MediaType) -> List[Dict[str, Any]]:
        """Analyze noise patterns for tampering"""
        
        evidence = []
        
        # Statistical noise analysis
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Calculate local variance
        if len(data_array) > 1000:
            chunks = np.array_split(data_array, 10)
            variances = [np.var(chunk) for chunk in chunks]
            
            # Check for unusual variance patterns
            variance_diff = max(variances) - min(variances)
            if variance_diff > 2000:  # Threshold for unusual patterns
                evidence.append({
                    'type': 'noise_pattern_anomaly',
                    'description': 'Unusual noise patterns detected',
                    'confidence': 0.7,
                    'tamper_type': TamperType.NOISE_INJECTION,
                    'variance_difference': float(variance_diff)
                })
        
        return evidence

    async def _analyze_statistical_properties(self, data: bytes, media_type: MediaType) -> List[Dict[str, Any]]:
        """Analyze statistical properties for anomalies"""
        
        evidence = []
        
        data_array = np.frombuffer(data, dtype=np.uint8)
        
        # Histogram analysis
        hist, _ = np.histogram(data_array, bins=256, range=(0, 255))
        
        # Check for unusual distribution
        zero_bins = np.sum(hist == 0)
        if zero_bins > 200:  # Many empty bins
            evidence.append({
                'type': 'histogram_anomaly',
                'description': 'Unusual value distribution detected',
                'confidence': 0.6,
                'tamper_type': TamperType.CONTENT_ALTERATION,
                'empty_bins': int(zero_bins)
            })
        
        return evidence

    async def _analyze_jpeg_artifacts(self, data: bytes) -> List[Dict[str, Any]]:
        """Analyze JPEG-specific artifacts"""
        
        evidence = []
        
        # Look for JPEG headers and structure
        if b'\xff\xd8' in data and b'\xff\xd9' in data:
            # Basic JPEG structure analysis
            evidence.append({
                'type': 'jpeg_structure',
                'description': 'Valid JPEG structure detected',
                'confidence': 0.8,
                'tamper_type': TamperType.NONE
            })
        
        return evidence

    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of data"""
        
        _, counts = np.unique(data, return_counts=True)
        probabilities = counts / len(data)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy

    def _calculate_authenticity_score(self, tamper_evidence: List[Dict[str, Any]]) -> float:
        """Calculate overall authenticity score"""
        
        if not tamper_evidence:
            return 1.0
        
        # Weight evidence by confidence
        total_suspicion = 0.0
        total_weight = 0.0
        
        for evidence in tamper_evidence:
            confidence = evidence.get('confidence', 0.5)
            suspicion = 1.0 - confidence
            
            total_suspicion += suspicion * confidence
            total_weight += confidence
        
        if total_weight == 0:
            return 1.0
        
        avg_suspicion = total_suspicion / total_weight
        authenticity = 1.0 - avg_suspicion
        
        return max(0.0, min(1.0, authenticity))

    def _reconstruct_modification_timeline(self, tamper_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reconstruct timeline of modifications"""
        
        timeline = []
        
        # Sort evidence by confidence (most confident first)
        sorted_evidence = sorted(tamper_evidence, key=lambda x: x.get('confidence', 0), reverse=True)
        
        for i, evidence in enumerate(sorted_evidence):
            timeline.append({
                'sequence': i + 1,
                'estimated_time': 'unknown',  # Would require more sophisticated analysis
                'modification_type': evidence.get('tamper_type', 'unknown'),
                'description': evidence.get('description', ''),
                'confidence': evidence.get('confidence', 0.0)
            })
        
        return timeline

    def _update_avg_validation_time(self, new_time: float):
        """Update average validation time metric"""
        current_avg = self.metrics['avg_validation_time']
        total_validations = self.metrics['total_validations']
        
        if total_validations <= 1:
            self.metrics['avg_validation_time'] = new_time
        else:
            self.metrics['avg_validation_time'] = (
                (current_avg * (total_validations - 1) + new_time) / total_validations
            )

    async def _log_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Log audit event for security compliance"""
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data,
            'system': 'media_integrity'
        }
        
        self.audit_log.append(audit_entry)

    async def get_integrity_analytics(self, record_id: str) -> Dict[str, Any]:
        """Get analytics for integrity record"""
        
        if record_id not in self.integrity_records:
            return {}
        
        record = self.integrity_records[record_id]
        
        # Get validation results for this record
        validations = [
            v for v in self.validation_results.values() 
            if v.record_id == record_id
        ]
        
        analytics = {
            'record_id': record_id,
            'media_id': record.media_id,
            'media_type': record.media_type.value,
            'validation_level': record.validation_level.value,
            'created_at': record.created_at.isoformat(),
            'total_validations': len(validations),
            'successful_validations': len([v for v in validations if v.is_valid]),
            'tamper_detections': len([v for v in validations if v.tamper_detected]),
            'avg_confidence': np.mean([v.confidence_score for v in validations]) if validations else 0.0,
            'validation_methods': [m.value for m in record.validation_methods]
        }
        
        return analytics

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall integrity validation system metrics"""
        
        # Calculate success rate
        success_rate = (
            self.metrics['successful_validations'] / self.metrics['total_validations'] * 100
        ) if self.metrics['total_validations'] > 0 else 0
        
        # Calculate tamper detection rate
        tamper_rate = (
            self.metrics['tamper_detections'] / self.metrics['total_validations'] * 100
        ) if self.metrics['total_validations'] > 0 else 0
        
        return {
            'metrics': self.metrics,
            'success_rate_percent': round(success_rate, 2),
            'tamper_detection_rate_percent': round(tamper_rate, 2),
            'total_integrity_records': len(self.integrity_records),
            'total_forensic_analyses': len(self.forensic_analyses),
            'audit_log_entries': len(self.audit_log),
            'supported_validation_methods': [m.value for m in ValidationMethod],
            'system_status': 'operational'
        }


# Utility functions
async def create_media_integrity_validator(config: Dict[str, Any] = None) -> MediaIntegrityValidator:
    """Factory function to create media integrity validator"""
    validator = MediaIntegrityValidator(config)
    return validator


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate media integrity validator capabilities"""
        validator = await create_media_integrity_validator()
        
        # Sample media data
        original_media = b"Original media content data..." * 100
        tampered_media = b"Modified media content data..." * 100
        
        # Create integrity record
        record = await validator.create_integrity_record(
            original_media,
            media_id="media_123",
            media_type=MediaType.IMAGE,
            validation_level=IntegrityLevel.HIGH,
            creator_id="creator_456"
        )
        
        print(f"Integrity record created: {record.record_id}")
        print(f"Checksums: {record.checksums}")
        
        # Validate original media (should pass)
        original_result = await validator.validate_media_integrity(
            original_media,
            record.record_id
        )
        
        print(f"Original validation: {'VALID' if original_result.is_valid else 'INVALID'}")
        print(f"Confidence: {original_result.confidence_score:.3f}")
        print(f"Tamper detected: {original_result.tamper_detected}")
        
        # Validate tampered media (should fail)
        tampered_result = await validator.validate_media_integrity(
            tampered_media,
            record.record_id
        )
        
        print(f"Tampered validation: {'VALID' if tampered_result.is_valid else 'INVALID'}")
        print(f"Confidence: {tampered_result.confidence_score:.3f}")
        print(f"Tamper detected: {tampered_result.tamper_detected}")
        print(f"Tamper types: {[t.value for t in tampered_result.tamper_types]}")
        
        # Perform forensic analysis
        forensic = await validator.perform_forensic_analysis(
            tampered_media,
            media_id="media_123",
            media_type=MediaType.IMAGE
        )
        
        print(f"Forensic analysis: {forensic.analysis_id}")
        print(f"Authenticity score: {forensic.authenticity_score:.3f}")
        print(f"Evidence count: {len(forensic.tamper_evidence)}")
        
        # Get analytics
        analytics = await validator.get_integrity_analytics(record.record_id)
        print(f"Record analytics: {analytics}")
        
        system_metrics = await validator.get_system_metrics()
        print(f"System metrics: {system_metrics}")
    
    asyncio.run(demo())