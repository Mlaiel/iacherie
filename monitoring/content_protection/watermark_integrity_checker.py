"""
Ainflue Platform - Watermark Integrity Checker
==============================================

Enterprise-grade watermark integrity monitoring and validation system
for protecting content authenticity and ownership verification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import hashlib
import numpy as np
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Metrics
watermark_checks_total = Counter('ainflue_watermark_checks_total',
                                'Total watermark integrity checks', ['content_type', 'result'])
watermark_check_duration = Histogram('ainflue_watermark_check_duration_seconds',
                                    'Time spent checking watermark integrity')
watermark_integrity_score = Gauge('ainflue_watermark_integrity_score',
                                 'Watermark integrity score', ['content_id'])

class WatermarkType(Enum):
    """Types of watermarks supported."""
    VISIBLE_TEXT = "visible_text"
    VISIBLE_LOGO = "visible_logo"
    INVISIBLE_LSB = "invisible_lsb"
    INVISIBLE_DCT = "invisible_dct"
    INVISIBLE_DWT = "invisible_dwt"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_ECHO = "audio_echo"
    VIDEO_FRAME = "video_frame"
    BLOCKCHAIN_HASH = "blockchain_hash"

class IntegrityLevel(Enum):
    """Watermark integrity levels."""
    INTACT = "intact"
    PARTIALLY_DAMAGED = "partially_damaged"
    HEAVILY_DAMAGED = "heavily_damaged"
    REMOVED = "removed"
    TAMPERED = "tampered"
    UNKNOWN = "unknown"

class AttackType(Enum):
    """Types of watermark attacks detected."""
    COMPRESSION_ATTACK = "compression_attack"
    SCALING_ATTACK = "scaling_attack"
    ROTATION_ATTACK = "rotation_attack"
    CROPPING_ATTACK = "cropping_attack"
    NOISE_ATTACK = "noise_attack"
    FILTERING_ATTACK = "filtering_attack"
    COLLUSION_ATTACK = "collusion_attack"
    GEOMETRIC_ATTACK = "geometric_attack"
    REMOVAL_ATTACK = "removal_attack"

@dataclass
class WatermarkInfo:
    """Watermark information structure."""
    watermark_id: str
    watermark_type: WatermarkType
    creator_id: str
    content_hash: str
    embedding_strength: float
    embedding_key: str
    embedding_location: Optional[Dict[str, Any]]
    creation_timestamp: datetime
    expected_payload: str
    robustness_level: str

@dataclass
class IntegrityResult:
    """Watermark integrity check result."""
    content_id: str
    watermark_id: str
    integrity_level: IntegrityLevel
    integrity_score: float
    detected_payload: Optional[str]
    expected_payload: str
    payload_match: bool
    detected_attacks: List[AttackType]
    degradation_factors: List[str]
    confidence_score: float
    check_timestamp: datetime
    processing_time: float

class WatermarkIntegrityChecker:
    """Enterprise watermark integrity monitoring system."""
    
    def __init__(self) -> None:
        self.watermark_database = {}
        self.integrity_cache = {}
        self.attack_detectors = {}
        self.extraction_algorithms = {}
        
    async def register_watermark(self, content_id: str, watermark_info: WatermarkInfo) -> bool:
        """Register watermark information for integrity monitoring."""
        
        try:
            # Store watermark info
            self.watermark_database[content_id] = watermark_info
            
            # Initialize integrity monitoring
            await self._initialize_watermark_monitoring(content_id, watermark_info)
            
            logger.info(f"Watermark registered for content {content_id}: {watermark_info.watermark_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Watermark registration failed: {str(e)}")
            return False
    
    async def _initialize_watermark_monitoring(self, content_id: str,
                                             watermark_info: WatermarkInfo) -> None:
        """Initialize watermark monitoring for content."""
        
        # Set up extraction algorithm based on watermark type
        self.extraction_algorithms[content_id] = await self._get_extraction_algorithm(
            watermark_info.watermark_type
        )
        
        # Initialize attack detectors
        self.attack_detectors[content_id] = await self._initialize_attack_detectors(
            watermark_info.watermark_type
        )
        
        logger.debug(f"Watermark monitoring initialized for {content_id}")
    
    async def _get_extraction_algorithm(self, watermark_type: WatermarkType) -> Dict[str, Any]:
        """Get appropriate extraction algorithm for watermark type."""
        
        algorithms = {
            WatermarkType.VISIBLE_TEXT: {
                'method': 'ocr_extraction',
                'parameters': {'confidence_threshold': 0.8}
            },
            WatermarkType.VISIBLE_LOGO: {
                'method': 'template_matching',
                'parameters': {'match_threshold': 0.7}
            },
            WatermarkType.INVISIBLE_LSB: {
                'method': 'lsb_extraction',
                'parameters': {'bit_plane': 0}
            },
            WatermarkType.INVISIBLE_DCT: {
                'method': 'dct_extraction',
                'parameters': {'frequency_band': 'mid'}
            },
            WatermarkType.INVISIBLE_DWT: {
                'method': 'dwt_extraction',
                'parameters': {'wavelet': 'haar', 'levels': 3}
            },
            WatermarkType.AUDIO_SPECTRAL: {
                'method': 'spectral_extraction',
                'parameters': {'frequency_range': [1000, 8000]}
            },
            WatermarkType.AUDIO_ECHO: {
                'method': 'echo_extraction',
                'parameters': {'delay_range': [0.001, 0.1]}
            },
            WatermarkType.VIDEO_FRAME: {
                'method': 'frame_extraction',
                'parameters': {'frame_interval': 30}
            },
            WatermarkType.BLOCKCHAIN_HASH: {
                'method': 'hash_verification',
                'parameters': {'hash_algorithm': 'sha256'}
            }
        }
        
        return algorithms.get(watermark_type, {
            'method': 'generic_extraction',
            'parameters': {}
        })
    
    async def _initialize_attack_detectors(self, watermark_type: WatermarkType) -> List[AttackType]:
        """Initialize attack detectors based on watermark type."""
        
        # Define which attacks each watermark type is vulnerable to
        vulnerability_map = {
            WatermarkType.VISIBLE_TEXT: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.SCALING_ATTACK,
                AttackType.CROPPING_ATTACK,
                AttackType.REMOVAL_ATTACK
            ],
            WatermarkType.VISIBLE_LOGO: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.SCALING_ATTACK,
                AttackType.ROTATION_ATTACK,
                AttackType.CROPPING_ATTACK,
                AttackType.REMOVAL_ATTACK
            ],
            WatermarkType.INVISIBLE_LSB: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.NOISE_ATTACK,
                AttackType.FILTERING_ATTACK,
                AttackType.REMOVAL_ATTACK
            ],
            WatermarkType.INVISIBLE_DCT: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.SCALING_ATTACK,
                AttackType.FILTERING_ATTACK,
                AttackType.GEOMETRIC_ATTACK
            ],
            WatermarkType.INVISIBLE_DWT: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.SCALING_ATTACK,
                AttackType.NOISE_ATTACK,
                AttackType.GEOMETRIC_ATTACK
            ],
            WatermarkType.AUDIO_SPECTRAL: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.NOISE_ATTACK,
                AttackType.FILTERING_ATTACK,
                AttackType.REMOVAL_ATTACK
            ],
            WatermarkType.AUDIO_ECHO: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.NOISE_ATTACK,
                AttackType.FILTERING_ATTACK
            ],
            WatermarkType.VIDEO_FRAME: [
                AttackType.COMPRESSION_ATTACK,
                AttackType.SCALING_ATTACK,
                AttackType.CROPPING_ATTACK,
                AttackType.REMOVAL_ATTACK
            ],
            WatermarkType.BLOCKCHAIN_HASH: [
                AttackType.TAMPERING_ATTACK
            ]
        }
        
        return vulnerability_map.get(watermark_type, [])
    
    async def check_watermark_integrity(self, content_id: str,
                                       content_data: bytes,
                                       metadata: Optional[Dict[str, Any]] = None) -> IntegrityResult:
        """Perform comprehensive watermark integrity check."""
        start_time = time.time()
        
        try:
            # Get watermark information
            if content_id not in self.watermark_database:
                raise ValueError(f"No watermark registered for content {content_id}")
            
            watermark_info = self.watermark_database[content_id]
            
            # Extract watermark
            extracted_payload = await self._extract_watermark(
                content_data, watermark_info, metadata
            )
            
            # Calculate integrity score
            integrity_score = await self._calculate_integrity_score(
                extracted_payload, watermark_info.expected_payload
            )
            
            # Determine integrity level
            integrity_level = await self._determine_integrity_level(integrity_score)
            
            # Check payload match
            payload_match = extracted_payload == watermark_info.expected_payload
            
            # Detect attacks
            detected_attacks = await self._detect_attacks(
                content_data, watermark_info, extracted_payload, metadata
            )
            
            # Analyze degradation factors
            degradation_factors = await self._analyze_degradation_factors(
                content_data, watermark_info, metadata
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                integrity_score, payload_match, detected_attacks
            )
            
            # Create result
            result = IntegrityResult(
                content_id=content_id,
                watermark_id=watermark_info.watermark_id,
                integrity_level=integrity_level,
                integrity_score=integrity_score,
                detected_payload=extracted_payload,
                expected_payload=watermark_info.expected_payload,
                payload_match=payload_match,
                detected_attacks=detected_attacks,
                degradation_factors=degradation_factors,
                confidence_score=confidence_score,
                check_timestamp=datetime.now(),
                processing_time=time.time() - start_time
            )
            
            # Cache result
            self.integrity_cache[content_id] = result
            
            # Update metrics
            watermark_check_duration.observe(result.processing_time)
            watermark_checks_total.labels(
                content_type=metadata.get('type', 'unknown') if metadata else 'unknown',
                result=integrity_level.value
            ).inc()
            watermark_integrity_score.labels(content_id=content_id).set(integrity_score)
            
            logger.info(f"Watermark integrity checked for {content_id}: "
                       f"{integrity_level.value} (score: {integrity_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Watermark integrity check failed: {str(e)}")
            raise
    
    async def _extract_watermark(self, content_data: bytes,
                               watermark_info: WatermarkInfo,
                               metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract watermark from content data."""
        
        try:
            watermark_type = watermark_info.watermark_type
            
            if watermark_type == WatermarkType.VISIBLE_TEXT:
                return await self._extract_visible_text_watermark(content_data)
            elif watermark_type == WatermarkType.VISIBLE_LOGO:
                return await self._extract_visible_logo_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.INVISIBLE_LSB:
                return await self._extract_lsb_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.INVISIBLE_DCT:
                return await self._extract_dct_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.INVISIBLE_DWT:
                return await self._extract_dwt_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.AUDIO_SPECTRAL:
                return await self._extract_audio_spectral_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.AUDIO_ECHO:
                return await self._extract_audio_echo_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.VIDEO_FRAME:
                return await self._extract_video_frame_watermark(content_data, watermark_info)
            elif watermark_type == WatermarkType.BLOCKCHAIN_HASH:
                return await self._extract_blockchain_hash_watermark(content_data, watermark_info)
            else:
                logger.warning(f"Unknown watermark type: {watermark_type}")
                return None
                
        except Exception as e:
            logger.error(f"Watermark extraction failed: {str(e)}")
            return None
    
    async def _extract_visible_text_watermark(self, content_data: bytes) -> Optional[str]:
        """Extract visible text watermark using OCR."""
        # Simulate OCR extraction
        # In real implementation, would use OCR library like Tesseract
        
        # Simple pattern detection
        if b'copyright' in content_data.lower():
            return "copyright_detected"
        elif b'watermark' in content_data.lower():
            return "watermark_detected"
        
        return None
    
    async def _extract_visible_logo_watermark(self, content_data: bytes,
                                            watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract visible logo watermark using template matching."""
        # Simulate template matching
        # In real implementation, would use OpenCV template matching
        
        # Simple hash-based detection
        content_hash = hashlib.md5(content_data[:1024]).hexdigest()
        if content_hash[0] in '0123456789abcdef'[:8]:  # Simulate 50% detection rate
            return f"logo_{watermark_info.watermark_id}"
        
        return None
    
    async def _extract_lsb_watermark(self, content_data: bytes,
                                   watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract LSB (Least Significant Bit) watermark."""
        try:
            # Simulate LSB extraction
            # In real implementation, would extract bits from LSB planes
            
            # Extract bits from every 8th byte's LSB
            extracted_bits = []
            for i in range(0, min(len(content_data), 1000), 8):
                bit = content_data[i] & 1
                extracted_bits.append(str(bit))
            
            # Convert bits to string
            bit_string = ''.join(extracted_bits)
            
            # Try to decode as ASCII
            if len(bit_string) >= 8:
                # Group into bytes and convert
                payload_bytes = []
                for i in range(0, len(bit_string) - 7, 8):
                    byte_bits = bit_string[i:i+8]
                    byte_value = int(byte_bits, 2)
                    if 32 <= byte_value <= 126:  # Printable ASCII
                        payload_bytes.append(chr(byte_value))
                    else:
                        break
                
                if payload_bytes:
                    return ''.join(payload_bytes)
            
            return bit_string[:32] if bit_string else None
            
        except Exception as e:
            logger.error(f"LSB extraction failed: {str(e)}")
            return None
    
    async def _extract_dct_watermark(self, content_data: bytes,
                                   watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract DCT (Discrete Cosine Transform) watermark."""
        try:
            # Simulate DCT extraction
            # In real implementation, would use DCT coefficients
            
            # Simple frequency domain analysis simulation
            data_array = np.frombuffer(content_data[:1024], dtype=np.uint8)
            
            # Simulate DCT analysis
            dct_coeffs = np.fft.fft(data_array.astype(float))
            mid_freq_coeffs = dct_coeffs[len(dct_coeffs)//4:len(dct_coeffs)//2]
            
            # Extract watermark from coefficient phases
            phases = np.angle(mid_freq_coeffs)
            normalized_phases = (phases + np.pi) / (2 * np.pi)
            
            # Convert to binary
            binary_data = (normalized_phases > 0.5).astype(int)
            binary_string = ''.join(map(str, binary_data[:32]))
            
            return binary_string
            
        except Exception as e:
            logger.error(f"DCT extraction failed: {str(e)}")
            return None
    
    async def _extract_dwt_watermark(self, content_data: bytes,
                                   watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract DWT (Discrete Wavelet Transform) watermark."""
        try:
            # Simulate DWT extraction
            # In real implementation, would use wavelet transforms
            
            data_array = np.frombuffer(content_data[:1024], dtype=np.uint8)
            
            # Simple wavelet simulation using differences
            level1 = data_array[::2] - data_array[1::2]
            level2 = level1[::2] - level1[1::2]
            
            # Extract watermark from wavelet coefficients
            watermark_coeffs = level2[:16]
            binary_data = (watermark_coeffs > np.mean(watermark_coeffs)).astype(int)
            binary_string = ''.join(map(str, binary_data))
            
            return binary_string
            
        except Exception as e:
            logger.error(f"DWT extraction failed: {str(e)}")
            return None
    
    async def _extract_audio_spectral_watermark(self, content_data: bytes,
                                              watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract spectral watermark from audio."""
        try:
            # Simulate audio spectral analysis
            # In real implementation, would use FFT on audio samples
            
            audio_samples = np.frombuffer(content_data[:4096], dtype=np.int16)
            
            # Simulate FFT
            spectrum = np.fft.fft(audio_samples.astype(float))
            
            # Extract watermark from specific frequency bins
            freq_range = slice(100, 132)  # 32 frequency bins
            watermark_bins = spectrum[freq_range]
            
            # Convert magnitude to binary
            magnitudes = np.abs(watermark_bins)
            threshold = np.mean(magnitudes)
            binary_data = (magnitudes > threshold).astype(int)
            
            return ''.join(map(str, binary_data))
            
        except Exception as e:
            logger.error(f"Audio spectral extraction failed: {str(e)}")
            return None
    
    async def _extract_audio_echo_watermark(self, content_data: bytes,
                                          watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract echo watermark from audio."""
        try:
            # Simulate echo detection
            # In real implementation, would detect echo patterns
            
            audio_samples = np.frombuffer(content_data[:4096], dtype=np.int16)
            
            # Look for echo patterns at different delays
            delays = [44, 88, 132, 176]  # Sample delays
            echo_strengths = []
            
            for delay in delays:
                if len(audio_samples) > delay:
                    correlation = np.corrcoef(
                        audio_samples[:-delay],
                        audio_samples[delay:]
                    )[0, 1]
                    echo_strengths.append(correlation)
                else:
                    echo_strengths.append(0)
            
            # Convert echo pattern to binary
            threshold = 0.1
            binary_data = (np.array(echo_strengths) > threshold).astype(int)
            
            return ''.join(map(str, binary_data))
            
        except Exception as e:
            logger.error(f"Audio echo extraction failed: {str(e)}")
            return None
    
    async def _extract_video_frame_watermark(self, content_data: bytes,
                                           watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract watermark from video frames."""
        try:
            # Simulate video frame analysis
            # In real implementation, would extract frames and analyze
            
            # Simple frame-based pattern detection
            frame_size = 1024
            num_frames = len(content_data) // frame_size
            
            frame_hashes = []
            for i in range(min(num_frames, 8)):
                frame_start = i * frame_size
                frame_data = content_data[frame_start:frame_start + frame_size]
                frame_hash = hashlib.md5(frame_data).hexdigest()
                frame_hashes.append(frame_hash)
            
            # Extract pattern from frame hashes
            if frame_hashes:
                pattern = ''.join([h[0] for h in frame_hashes])
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Video frame extraction failed: {str(e)}")
            return None
    
    async def _extract_blockchain_hash_watermark(self, content_data: bytes,
                                               watermark_info: WatermarkInfo) -> Optional[str]:
        """Extract blockchain hash watermark."""
        try:
            # Calculate content hash
            content_hash = hashlib.sha256(content_data).hexdigest()
            
            # Compare with expected blockchain hash
            if watermark_info.expected_payload:
                return content_hash
            
            return None
            
        except Exception as e:
            logger.error(f"Blockchain hash extraction failed: {str(e)}")
            return None
    
    async def _calculate_integrity_score(self, extracted_payload: Optional[str],
                                       expected_payload: str) -> float:
        """Calculate watermark integrity score."""
        
        if not extracted_payload:
            return 0.0
        
        if not expected_payload:
            return 0.5  # Neutral if no expected payload
        
        # Calculate similarity between extracted and expected
        if extracted_payload == expected_payload:
            return 1.0
        
        # Calculate approximate match using edit distance
        min_len = min(len(extracted_payload), len(expected_payload))
        max_len = max(len(extracted_payload), len(expected_payload))
        
        if min_len == 0:
            return 0.0
        
        # Simple character-by-character comparison
        matches = sum(1 for i in range(min_len)
                     if extracted_payload[i] == expected_payload[i])
        
        base_score = matches / max_len
        
        # Penalize length differences
        length_penalty = 1.0 - abs(len(extracted_payload) - len(expected_payload)) / max_len
        
        return base_score * length_penalty
    
    async def _determine_integrity_level(self, integrity_score: float) -> IntegrityLevel:
        """Determine integrity level from score."""
        
        if integrity_score >= 0.95:
            return IntegrityLevel.INTACT
        elif integrity_score >= 0.7:
            return IntegrityLevel.PARTIALLY_DAMAGED
        elif integrity_score >= 0.3:
            return IntegrityLevel.HEAVILY_DAMAGED
        elif integrity_score > 0.0:
            return IntegrityLevel.TAMPERED
        else:
            return IntegrityLevel.REMOVED
    
    async def _detect_attacks(self, content_data: bytes,
                            watermark_info: WatermarkInfo,
                            extracted_payload: Optional[str],
                            metadata: Optional[Dict[str, Any]]) -> List[AttackType]:
        """Detect watermark attacks."""
        
        detected_attacks = []
        
        try:
            # Check for compression artifacts
            if await self._detect_compression_attack(content_data, metadata):
                detected_attacks.append(AttackType.COMPRESSION_ATTACK)
            
            # Check for scaling/resizing
            if await self._detect_scaling_attack(content_data, metadata):
                detected_attacks.append(AttackType.SCALING_ATTACK)
            
            # Check for rotation
            if await self._detect_rotation_attack(content_data, metadata):
                detected_attacks.append(AttackType.ROTATION_ATTACK)
            
            # Check for cropping
            if await self._detect_cropping_attack(content_data, metadata):
                detected_attacks.append(AttackType.CROPPING_ATTACK)
            
            # Check for noise addition
            if await self._detect_noise_attack(content_data):
                detected_attacks.append(AttackType.NOISE_ATTACK)
            
            # Check for filtering
            if await self._detect_filtering_attack(content_data):
                detected_attacks.append(AttackType.FILTERING_ATTACK)
            
            # Check for removal attempts
            if not extracted_payload:
                detected_attacks.append(AttackType.REMOVAL_ATTACK)
            
        except Exception as e:
            logger.error(f"Attack detection failed: {str(e)}")
        
        return detected_attacks
    
    async def _detect_compression_attack(self, content_data: bytes,
                                       metadata: Optional[Dict[str, Any]]) -> bool:
        """Detect compression attack indicators."""
        
        # Check metadata for compression indicators
        if metadata:
            quality = metadata.get('quality', 100)
            if quality < 80:
                return True
            
            compression_ratio = metadata.get('compression_ratio', 1.0)
            if compression_ratio > 10:
                return True
        
        # Analyze content for compression artifacts
        # Simple entropy-based detection
        if len(content_data) > 1024:
            sample = content_data[:1024]
            entropy = self._calculate_entropy(sample)
            if entropy < 6.0:  # Low entropy might indicate compression
                return True
        
        return False
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    async def _detect_scaling_attack(self, content_data: bytes,
                                   metadata: Optional[Dict[str, Any]]) -> bool:
        """Detect scaling/resizing attack."""
        
        if metadata:
            original_width = metadata.get('original_width')
            original_height = metadata.get('original_height')
            current_width = metadata.get('width')
            current_height = metadata.get('height')
            
            if all([original_width, original_height, current_width, current_height]):
                width_ratio = current_width / original_width
                height_ratio = current_height / original_height
                
                # Detect significant scaling
                if abs(width_ratio - 1.0) > 0.1 or abs(height_ratio - 1.0) > 0.1:
                    return True
        
        return False
    
    async def _detect_rotation_attack(self, content_data: bytes,
                                    metadata: Optional[Dict[str, Any]]) -> bool:
        """Detect rotation attack."""
        
        # Simple rotation detection based on metadata
        if metadata:
            rotation = metadata.get('rotation', 0)
            if rotation != 0:
                return True
        
        return False
    
    async def _detect_cropping_attack(self, content_data: bytes,
                                    metadata: Optional[Dict[str, Any]]) -> bool:
        """Detect cropping attack."""
        
        if metadata:
            # Check if content dimensions are smaller than expected
            original_size = metadata.get('original_file_size')
            current_size = len(content_data)
            
            if original_size and current_size < original_size * 0.8:
                return True
        
        return False
    
    async def _detect_noise_attack(self, content_data: bytes) -> bool:
        """Detect noise addition attack."""
        
        # Analyze data for noise patterns
        if len(content_data) > 1024:
            sample = content_data[:1024]
            
            # Calculate variance as noise indicator
            data_array = np.frombuffer(sample, dtype=np.uint8)
            variance = np.var(data_array.astype(float))
            
            # High variance might indicate added noise
            if variance > 2000:
                return True
        
        return False
    
    async def _detect_filtering_attack(self, content_data: bytes) -> bool:
        """Detect filtering attack."""
        
        # Simple filtering detection based on data smoothness
        if len(content_data) > 1024:
            sample = content_data[:1024]
            data_array = np.frombuffer(sample, dtype=np.uint8)
            
            # Calculate gradient to detect smoothing
            if len(data_array) > 1:
                gradient = np.gradient(data_array.astype(float))
                avg_gradient = np.mean(np.abs(gradient))
                
                # Low gradient might indicate filtering
                if avg_gradient < 5.0:
                    return True
        
        return False
    
    async def _analyze_degradation_factors(self, content_data: bytes,
                                         watermark_info: WatermarkInfo,
                                         metadata: Optional[Dict[str, Any]]) -> List[str]:
        """Analyze factors causing watermark degradation."""
        
        factors = []
        
        # Check file format changes
        if metadata:
            original_format = metadata.get('original_format')
            current_format = metadata.get('format')
            
            if original_format and current_format and original_format != current_format:
                factors.append(f"Format conversion: {original_format} → {current_format}")
        
        # Check quality degradation
        if metadata:
            quality = metadata.get('quality')
            if quality and quality < 90:
                factors.append(f"Quality reduction: {quality}%")
        
        # Check processing history
        if metadata:
            processing_history = metadata.get('processing_history', [])
            for operation in processing_history:
                factors.append(f"Processing: {operation}")
        
        # Age-related degradation
        content_age = datetime.now() - watermark_info.creation_timestamp
        if content_age.days > 365:
            factors.append(f"Age-related degradation: {content_age.days} days")
        
        return factors
    
    async def _calculate_confidence_score(self, integrity_score: float,
                                        payload_match: bool,
                                        detected_attacks: List[AttackType]) -> float:
        """Calculate confidence in watermark integrity assessment."""
        
        # Base confidence from integrity score
        confidence = integrity_score
        
        # Boost confidence for exact payload match
        if payload_match:
            confidence = min(confidence + 0.1, 1.0)
        
        # Reduce confidence based on detected attacks
        attack_penalty = len(detected_attacks) * 0.05
        confidence = max(confidence - attack_penalty, 0.0)
        
        # Consider watermark type robustness
        # More robust watermark types get higher confidence
        robust_types = [
            WatermarkType.INVISIBLE_DCT,
            WatermarkType.INVISIBLE_DWT,
            WatermarkType.BLOCKCHAIN_HASH
        ]
        
        if any(wtype in str(self.watermark_database) for wtype in robust_types):
            confidence = min(confidence + 0.05, 1.0)
        
        return confidence
    
    async def get_cached_integrity_result(self, content_id: str) -> Optional[IntegrityResult]:
        """Get cached integrity check result."""
        return self.integrity_cache.get(content_id)
    
    async def invalidate_integrity_cache(self, content_id: str) -> None:
        """Invalidate cached integrity result."""
        if content_id in self.integrity_cache:
            del self.integrity_cache[content_id]
    
    def get_watermark_stats(self) -> Dict[str, Any]:
        """Get watermark monitoring statistics."""
        
        total_watermarks = len(self.watermark_database)
        total_checks = len(self.integrity_cache)
        
        # Analyze integrity levels
        integrity_levels = {}
        avg_integrity_score = 0.0
        
        if self.integrity_cache:
            for result in self.integrity_cache.values():
                level = result.integrity_level.value
                integrity_levels[level] = integrity_levels.get(level, 0) + 1
                avg_integrity_score += result.integrity_score
            
            avg_integrity_score /= len(self.integrity_cache)
        
        # Analyze attack types
        attack_frequency = {}
        for result in self.integrity_cache.values():
            for attack in result.detected_attacks:
                attack_frequency[attack.value] = attack_frequency.get(attack.value, 0) + 1
        
        return {
            'total_watermarks': total_watermarks,
            'total_integrity_checks': total_checks,
            'integrity_levels': integrity_levels,
            'average_integrity_score': avg_integrity_score,
            'attack_frequency': attack_frequency,
            'monitoring_active': True
        }

# Global watermark integrity checker instance
watermark_integrity_checker = WatermarkIntegrityChecker()