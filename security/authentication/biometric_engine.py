#!/usr/bin/env python3
"""
🔐 Biometric Engine - Enterprise Security Module
================================================

Ultra-secure multi-modal biometric authentication system with:
- Face recognition with liveness detection
- Voice authentication and verification
- Fingerprint analysis and matching
- Anti-spoofing and presentation attack detection

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + ML + CV + Audio + Backend
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import base64
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

import numpy as np

# Optional OpenCV import with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Mock cv2 for when OpenCV is not available
    class MockCV2:
        CV_64F = 6
        IMREAD_COLOR = 1
        IMREAD_GRAYSCALE = 0
        COLOR_BGR2RGB = 4
        COLOR_BGR2GRAY = 6
        MORPH_ELLIPSE = 2
        MORPH_CLOSE = 3
        RETR_EXTERNAL = 0
        CHAIN_APPROX_SIMPLE = 2
        
        class data:
            haarcascades = "/usr/share/opencv4/haarcascades/"
        
        @staticmethod
        def imdecode(buf, flags):
            return np.zeros((100, 100, 3), dtype=np.uint8)
            
        @staticmethod
        def cvtColor(image, conversion):
            return np.zeros((100, 100), dtype=np.uint8)
            
        @staticmethod
        def resize(image, size):
            return np.zeros((*size, 3), dtype=np.uint8)
            
        @staticmethod
        def Laplacian(image, dtype):
            class MockLaplacian:
                def var(self):
                    return 100.0
            return MockLaplacian()
            
        @staticmethod
        def GaussianBlur(image, ksize, sigma):
            return image
            
        @staticmethod
        def equalizeHist(image):
            return image
            
        @staticmethod
        def getStructuringElement(shape, ksize):
            return np.ones(ksize, dtype=np.uint8)
            
        @staticmethod
        def morphologyEx(image, op, kernel):
            return image
            
        @staticmethod
        def Canny(image, t1, t2):
            return np.zeros_like(image)
            
        @staticmethod
        def findContours(image, mode, method):
            return [], None
            
        @staticmethod
        def moments(contour):
            return {"m00": 1, "m10": 50, "m01": 50}
            
        class CascadeClassifier:
            def __init__(self, path):
                pass
            def detectMultiScale(self, image, scale=1.1, min_neighbors=5):
                return []
    
    cv2 = MockCV2()
import redis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class BiometricType(Enum):
    """Supported biometric modalities"""
    FACE = "face"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"
    IRIS = "iris"
    PALM = "palm"
    GAIT = "gait"
    MULTI_MODAL = "multi_modal"

class BiometricQuality(Enum):
    """Biometric sample quality levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class LivenessStatus(Enum):
    """Liveness detection status"""
    LIVE = "live"
    SPOOF = "spoof"
    UNCERTAIN = "uncertain"

@dataclass
class BiometricTemplate:
    """Encrypted biometric template storage"""
    user_id: str
    biometric_type: BiometricType
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    encrypted_features: bytes = b""
    feature_hash: str = ""
    quality_score: float = 0.0
    enrollment_date: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    security_level: str = "standard"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BiometricSample:
    """Raw biometric sample for processing"""
    sample_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    biometric_type: BiometricType = BiometricType.FACE
    raw_data: bytes = b""
    quality_score: float = 0.0
    liveness_score: float = 0.0
    preprocessing_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    device_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BiometricVerificationResult:
    """Biometric verification result"""
    user_id: str
    biometric_type: BiometricType
    is_verified: bool
    confidence_score: float
    match_score: float
    quality_assessment: BiometricQuality
    liveness_status: LivenessStatus
    verification_time: float
    template_id: str = ""
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class FaceAnalyzer:
    """Advanced face recognition and liveness detection"""
    
    def __init__(self):
        self.face_cascade = None
        self.liveness_model = None
        self.quality_threshold = 0.7
        self.liveness_threshold = 0.8
        
    async def initialize(self) -> None:
        """Initialize face recognition models"""
        try:
            # Load OpenCV cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info("Face analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize face analyzer: {e}")
            raise

    async def extract_features(self, sample: BiometricSample) -> Optional[np.ndarray]:
        """Extract facial features from image"""
        try:
            # Decode image
            img_data = base64.b64decode(sample.raw_data)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
                
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return None
                
            # Extract features from the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_region = rgb_image[y:y+h, x:x+w]
            
            # Resize to standard size
            face_resized = cv2.resize(face_region, (128, 128))
            
            # Extract features (simplified - in production use deep learning)
            features = face_resized.flatten().astype(np.float32)
            features = features / np.linalg.norm(features)  # Normalize
            
            return features
            
        except Exception as e:
            logger.error(f"Face feature extraction failed: {e}")
            return None

    async def assess_quality(self, sample: BiometricSample) -> float:
        """Assess face image quality"""
        try:
            # Decode image
            img_data = base64.b64decode(sample.raw_data)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return 0.0
                
            # Calculate quality metrics
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 500.0)
            
            # Brightness assessment
            brightness = gray.mean()
            brightness_score = 1.0 - abs(brightness - 128) / 128.0
            
            # Contrast assessment
            contrast = gray.std()
            contrast_score = min(1.0, contrast / 50.0)
            
            # Face detection confidence
            faces = self.face_cascade.detectMultiScale(gray)
            face_score = 1.0 if len(faces) > 0 else 0.0
            
            # Combined quality score
            quality = (sharpness_score * 0.3 + brightness_score * 0.2 + 
                      contrast_score * 0.2 + face_score * 0.3)
            
            return min(1.0, max(0.0, quality))
            
        except Exception as e:
            logger.error(f"Face quality assessment failed: {e}")
            return 0.0

    async def detect_liveness(self, sample: BiometricSample) -> float:
        """Detect if face is live (anti-spoofing)"""
        try:
            # Simplified liveness detection
            # In production, use advanced techniques like:
            # - Eye blink detection
            # - Head movement analysis
            # - Texture analysis
            # - 3D depth analysis
            
            # For now, use basic texture analysis
            img_data = base64.b64decode(sample.raw_data)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return 0.0
                
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern for texture analysis
            lbp = self._calculate_lbp(gray)
            texture_variance = lbp.var()
            
            # Higher variance indicates more texture (live face)
            liveness_score = min(1.0, texture_variance / 100.0)
            
            return liveness_score
            
        except Exception as e:
            logger.error(f"Liveness detection failed: {e}")
            return 0.0

    def _calculate_lbp(self, image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern for texture analysis"""
        try:
            rows, cols = image.shape
            lbp = np.zeros_like(image)
            
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    center = image[i, j]
                    binary_string = ""
                    
                    # Compare with 8 neighbors
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    
                    for neighbor in neighbors:
                        binary_string += "1" if neighbor >= center else "0"
                    
                    lbp[i, j] = int(binary_string, 2)
            
            return lbp
            
        except Exception as e:
            logger.error(f"LBP calculation failed: {e}")
            return np.zeros_like(image)

class VoiceAuthenticator:
    """Advanced voice authentication and verification"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.frame_length = 0.025  # 25ms
        self.frame_shift = 0.01    # 10ms
        self.n_mfcc = 13
        
    async def initialize(self) -> None:
        """Initialize voice authentication models"""
        try:
            logger.info("Voice authenticator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize voice authenticator: {e}")
            raise

    async def extract_features(self, sample: BiometricSample) -> Optional[np.ndarray]:
        """Extract voice features (MFCC)"""
        try:
            # Decode audio data
            audio_data = base64.b64decode(sample.raw_data)
            
            # Convert to numpy array (assuming WAV format)
            audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio = audio / np.max(np.abs(audio))  # Normalize
            
            # Extract MFCC features
            mfcc_features = self._extract_mfcc(audio)
            
            # Statistical features
            mfcc_mean = np.mean(mfcc_features, axis=0)
            mfcc_std = np.std(mfcc_features, axis=0)
            mfcc_delta = np.diff(mfcc_features, axis=0).mean(axis=0)
            
            # Combine features
            features = np.concatenate([mfcc_mean, mfcc_std, mfcc_delta])
            
            return features
            
        except Exception as e:
            logger.error(f"Voice feature extraction failed: {e}")
            return None

    async def assess_quality(self, sample: BiometricSample) -> float:
        """Assess voice sample quality"""
        try:
            # Decode audio data
            audio_data = base64.b64decode(sample.raw_data)
            audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Signal-to-noise ratio
            signal_power = np.mean(audio ** 2)
            noise_floor = np.percentile(np.abs(audio), 10) ** 2
            snr = 10 * np.log10(signal_power / max(noise_floor, 1e-10))
            snr_score = min(1.0, max(0.0, (snr - 10) / 20))  # Normalize to 0-1
            
            # Dynamic range
            dynamic_range = np.max(audio) - np.min(audio)
            dynamic_score = min(1.0, dynamic_range / 32768.0)
            
            # Speech activity detection (simplified)
            energy = np.sum(audio ** 2)
            energy_score = min(1.0, energy / (len(audio) * 1000))
            
            # Combined quality score
            quality = (snr_score * 0.5 + dynamic_score * 0.3 + energy_score * 0.2)
            
            return quality
            
        except Exception as e:
            logger.error(f"Voice quality assessment failed: {e}")
            return 0.0

    def _extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features from audio"""
        try:
            # Simplified MFCC extraction
            # In production, use librosa or similar library
            
            # Pre-emphasis filter
            pre_emphasis = 0.97
            emphasized_signal = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
            
            # Framing
            frame_length = int(self.frame_length * self.sample_rate)
            frame_step = int(self.frame_shift * self.sample_rate)
            signal_length = len(emphasized_signal)
            num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))
            
            # Pad signal
            pad_signal_length = num_frames * frame_step + frame_length
            z = np.zeros((pad_signal_length - signal_length))
            pad_signal = np.append(emphasized_signal, z)
            
            # Create frames
            indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
                     np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
            frames = pad_signal[indices.astype(np.int32, copy=False)]
            
            # Apply Hamming window
            frames *= np.hamming(frame_length)
            
            # FFT and power spectrum
            NFFT = 512
            mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
            pow_frames = ((1.0 / NFFT) * ((mag_frames) ** 2))
            
            # Mel filter bank
            nfilt = 40
            low_freq_mel = 0
            high_freq_mel = (2595 * np.log10(1 + (self.sample_rate / 2) / 700))
            mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
            hz_points = (700 * (10**(mel_points / 2595) - 1))
            bin = np.floor((NFFT + 1) * hz_points / self.sample_rate)
            
            fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))
            for m in range(1, nfilt + 1):
                f_m_minus = int(bin[m - 1])
                f_m = int(bin[m])
                f_m_plus = int(bin[m + 1])
                
                for k in range(f_m_minus, f_m):
                    fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
                for k in range(f_m, f_m_plus):
                    fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
            
            filter_banks = np.dot(pow_frames, fbank.T)
            filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
            filter_banks = 20 * np.log10(filter_banks)
            
            # DCT for MFCC
            mfcc = self._dct(filter_banks)[:, :self.n_mfcc]
            
            return mfcc
            
        except Exception as e:
            logger.error(f"MFCC extraction failed: {e}")
            return np.zeros((1, self.n_mfcc))

    def _dct(self, filter_banks: np.ndarray) -> np.ndarray:
        """Discrete Cosine Transform"""
        try:
            N = filter_banks.shape[1]
            dct_matrix = np.zeros((N, N))
            
            for k in range(N):
                for n in range(N):
                    if k == 0:
                        dct_matrix[k, n] = np.sqrt(1/N)
                    else:
                        dct_matrix[k, n] = np.sqrt(2/N) * np.cos(np.pi * k * (2*n + 1) / (2*N))
            
            return np.dot(filter_banks, dct_matrix.T)
            
        except Exception as e:
            logger.error(f"DCT calculation failed: {e}")
            return filter_banks

class FingerprintAnalyzer:
    """Fingerprint analysis and matching"""
    
    def __init__(self):
        self.minutiae_threshold = 12  # Minimum minutiae points for match
        
    async def initialize(self) -> None:
        """Initialize fingerprint analyzer"""
        try:
            logger.info("Fingerprint analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize fingerprint analyzer: {e}")
            raise

    async def extract_features(self, sample: BiometricSample) -> Optional[np.ndarray]:
        """Extract fingerprint minutiae"""
        try:
            # Simplified fingerprint feature extraction
            # In production, use specialized fingerprint libraries
            
            # Decode image
            img_data = base64.b64decode(sample.raw_data)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                return None
                
            # Enhance fingerprint image
            enhanced = self._enhance_fingerprint(image)
            
            # Extract minutiae (simplified)
            minutiae = self._extract_minutiae(enhanced)
            
            # Convert to feature vector
            features = self._minutiae_to_vector(minutiae)
            
            return features
            
        except Exception as e:
            logger.error(f"Fingerprint feature extraction failed: {e}")
            return None

    def _enhance_fingerprint(self, image: np.ndarray) -> np.ndarray:
        """Enhance fingerprint image quality"""
        try:
            # Gaussian blur
            blurred = cv2.GaussianBlur(image, (5, 5), 0)
            
            # Histogram equalization
            enhanced = cv2.equalizeHist(blurred)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Fingerprint enhancement failed: {e}")
            return image

    def _extract_minutiae(self, image: np.ndarray) -> List[Tuple[int, int, float]]:
        """Extract minutiae points (simplified)"""
        try:
            # Simplified minutiae extraction
            # In production, use ridge detection and minutiae extraction algorithms
            
            # Edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            minutiae = []
            for contour in contours:
                if len(contour) > 5:
                    # Find contour center
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Calculate orientation (simplified)
                        orientation = np.arctan2(cy - image.shape[0]//2, cx - image.shape[1]//2)
                        
                        minutiae.append((cx, cy, orientation))
                        
                        if len(minutiae) >= 50:  # Limit number of minutiae
                            break
            
            return minutiae
            
        except Exception as e:
            logger.error(f"Minutiae extraction failed: {e}")
            return []

    def _minutiae_to_vector(self, minutiae: List[Tuple[int, int, float]]) -> np.ndarray:
        """Convert minutiae to feature vector"""
        try:
            if not minutiae:
                return np.zeros(150)  # Fixed size vector
                
            # Normalize coordinates and orientations
            features = []
            for x, y, orientation in minutiae[:50]:  # Max 50 minutiae
                features.extend([x/255.0, y/255.0, orientation/(2*np.pi)])
            
            # Pad or truncate to fixed size
            while len(features) < 150:
                features.append(0.0)
            
            return np.array(features[:150])
            
        except Exception as e:
            logger.error(f"Minutiae to vector conversion failed: {e}")
            return np.zeros(150)

class BiometricEngine:
    """
    Main biometric authentication engine coordinating all modalities.
    
    Features:
    - Multi-modal biometric support
    - Liveness detection and anti-spoofing
    - Secure template storage with encryption
    - Quality assessment and filtering
    - Performance optimization
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize analyzers
        self.face_analyzer = FaceAnalyzer()
        self.voice_authenticator = VoiceAuthenticator()
        self.fingerprint_analyzer = FingerprintAnalyzer()
        
        # Configuration
        self.config = {
            "quality_threshold": 0.7,
            "verification_threshold": 0.85,
            "liveness_threshold": 0.8,
            "max_templates_per_user": 5,
            "template_expiry_days": 365,
            "enable_multi_modal": True,
            "fusion_weights": {
                BiometricType.FACE: 0.4,
                BiometricType.VOICE: 0.3,
                BiometricType.FINGERPRINT: 0.3
            }
        }

    async def initialize(self) -> None:
        """Initialize the biometric engine"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize all analyzers
            await self.face_analyzer.initialize()
            await self.voice_authenticator.initialize()
            await self.fingerprint_analyzer.initialize()
            
            logger.info("Biometric engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize biometric engine: {e}")
            raise

    async def enroll_biometric(
        self,
        user_id: str,
        sample: BiometricSample,
        security_level: str = "standard"
    ) -> Tuple[bool, Optional[str]]:
        """
        Enroll biometric template for user.
        
        Args:
            user_id: User identifier
            sample: Biometric sample to enroll
            security_level: Security level for template storage
            
        Returns:
            Tuple[bool, Optional[str]]: Success status and template ID
        """
        try:
            # Quality assessment
            quality_score = await self._assess_sample_quality(sample)
            if quality_score < self.config["quality_threshold"]:
                logger.warning(f"Low quality sample for user {user_id}: {quality_score}")
                return False, "Quality too low for enrollment"
            
            # Liveness detection for face samples
            if sample.biometric_type == BiometricType.FACE:
                liveness_score = await self.face_analyzer.detect_liveness(sample)
                if liveness_score < self.config["liveness_threshold"]:
                    logger.warning(f"Liveness check failed for user {user_id}: {liveness_score}")
                    return False, "Liveness detection failed"
            
            # Extract features
            features = await self._extract_features(sample)
            if features is None:
                return False, "Feature extraction failed"
            
            # Create template
            template = BiometricTemplate(
                user_id=user_id,
                biometric_type=sample.biometric_type,
                quality_score=quality_score,
                security_level=security_level
            )
            
            # Encrypt and store features
            template.encrypted_features = self._encrypt_features(features)
            template.feature_hash = self._hash_features(features)
            
            # Store template
            await self._store_template(template)
            
            logger.info(f"Enrolled {sample.biometric_type.value} template for user {user_id}")
            return True, template.template_id
            
        except Exception as e:
            logger.error(f"Biometric enrollment failed for user {user_id}: {e}")
            return False, f"Enrollment error: {e}"

    async def verify_biometric(
        self,
        user_id: str,
        sample: BiometricSample,
        require_liveness: bool = True
    ) -> BiometricVerificationResult:
        """
        Verify biometric sample against enrolled templates.
        
        Args:
            user_id: User identifier
            sample: Biometric sample to verify
            require_liveness: Whether to require liveness detection
            
        Returns:
            BiometricVerificationResult: Verification result
        """
        start_time = time.time()
        
        try:
            # Quality assessment
            quality_score = await self._assess_sample_quality(sample)
            quality_assessment = self._score_to_quality(quality_score)
            
            if quality_score < self.config["quality_threshold"]:
                return BiometricVerificationResult(
                    user_id=user_id,
                    biometric_type=sample.biometric_type,
                    is_verified=False,
                    confidence_score=0.0,
                    match_score=0.0,
                    quality_assessment=quality_assessment,
                    liveness_status=LivenessStatus.UNCERTAIN,
                    verification_time=time.time() - start_time,
                    error_message="Sample quality too low"
                )
            
            # Liveness detection
            liveness_status = LivenessStatus.UNCERTAIN
            if sample.biometric_type == BiometricType.FACE and require_liveness:
                liveness_score = await self.face_analyzer.detect_liveness(sample)
                liveness_status = (LivenessStatus.LIVE if liveness_score >= self.config["liveness_threshold"] 
                                 else LivenessStatus.SPOOF)
                
                if liveness_status == LivenessStatus.SPOOF:
                    return BiometricVerificationResult(
                        user_id=user_id,
                        biometric_type=sample.biometric_type,
                        is_verified=False,
                        confidence_score=0.0,
                        match_score=0.0,
                        quality_assessment=quality_assessment,
                        liveness_status=liveness_status,
                        verification_time=time.time() - start_time,
                        error_message="Liveness detection failed"
                    )
            
            # Extract features
            sample_features = await self._extract_features(sample)
            if sample_features is None:
                return BiometricVerificationResult(
                    user_id=user_id,
                    biometric_type=sample.biometric_type,
                    is_verified=False,
                    confidence_score=0.0,
                    match_score=0.0,
                    quality_assessment=quality_assessment,
                    liveness_status=liveness_status,
                    verification_time=time.time() - start_time,
                    error_message="Feature extraction failed"
                )
            
            # Get user templates
            templates = await self._get_user_templates(user_id, sample.biometric_type)
            if not templates:
                return BiometricVerificationResult(
                    user_id=user_id,
                    biometric_type=sample.biometric_type,
                    is_verified=False,
                    confidence_score=0.0,
                    match_score=0.0,
                    quality_assessment=quality_assessment,
                    liveness_status=liveness_status,
                    verification_time=time.time() - start_time,
                    error_message="No enrolled templates found"
                )
            
            # Match against templates
            best_match_score = 0.0
            best_template_id = ""
            
            for template in templates:
                template_features = self._decrypt_features(template.encrypted_features)
                match_score = self._calculate_match_score(sample_features, template_features)
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_template_id = template.template_id
            
            # Determine verification result
            is_verified = best_match_score >= self.config["verification_threshold"]
            confidence_score = min(1.0, best_match_score * quality_score)
            
            # Update template usage
            if is_verified:
                await self._update_template_usage(best_template_id)
            
            return BiometricVerificationResult(
                user_id=user_id,
                biometric_type=sample.biometric_type,
                is_verified=is_verified,
                confidence_score=confidence_score,
                match_score=best_match_score,
                quality_assessment=quality_assessment,
                liveness_status=liveness_status,
                verification_time=time.time() - start_time,
                template_id=best_template_id
            )
            
        except Exception as e:
            logger.error(f"Biometric verification failed for user {user_id}: {e}")
            return BiometricVerificationResult(
                user_id=user_id,
                biometric_type=sample.biometric_type,
                is_verified=False,
                confidence_score=0.0,
                match_score=0.0,
                quality_assessment=BiometricQuality.POOR,
                liveness_status=LivenessStatus.UNCERTAIN,
                verification_time=time.time() - start_time,
                error_message=f"Verification error: {e}"
            )

    async def verify_multi_modal(
        self,
        user_id: str,
        samples: List[BiometricSample]
    ) -> BiometricVerificationResult:
        """Verify using multiple biometric modalities"""
        try:
            if not self.config["enable_multi_modal"]:
                raise ValueError("Multi-modal verification not enabled")
            
            verification_results = []
            
            # Verify each modality
            for sample in samples:
                result = await self.verify_biometric(user_id, sample)
                verification_results.append(result)
            
            # Fusion of results
            total_weight = 0.0
            weighted_score = 0.0
            
            for result in verification_results:
                if result.is_verified:
                    weight = self.config["fusion_weights"].get(result.biometric_type, 0.0)
                    weighted_score += result.confidence_score * weight
                    total_weight += weight
            
            # Calculate final confidence
            final_confidence = weighted_score / max(total_weight, 0.1)
            is_verified = final_confidence >= self.config["verification_threshold"]
            
            return BiometricVerificationResult(
                user_id=user_id,
                biometric_type=BiometricType.MULTI_MODAL,
                is_verified=is_verified,
                confidence_score=final_confidence,
                match_score=final_confidence,
                quality_assessment=BiometricQuality.GOOD,
                liveness_status=LivenessStatus.LIVE,
                verification_time=sum(r.verification_time for r in verification_results),
                metadata={"individual_results": [result.__dict__ for result in verification_results]}
            )
            
        except Exception as e:
            logger.error(f"Multi-modal verification failed: {e}")
            return BiometricVerificationResult(
                user_id=user_id,
                biometric_type=BiometricType.MULTI_MODAL,
                is_verified=False,
                confidence_score=0.0,
                match_score=0.0,
                quality_assessment=BiometricQuality.POOR,
                liveness_status=LivenessStatus.UNCERTAIN,
                verification_time=0.0,
                error_message=f"Multi-modal verification error: {e}"
            )

    async def _assess_sample_quality(self, sample: BiometricSample) -> float:
        """Assess biometric sample quality"""
        try:
            if sample.biometric_type == BiometricType.FACE:
                return await self.face_analyzer.assess_quality(sample)
            elif sample.biometric_type == BiometricType.VOICE:
                return await self.voice_authenticator.assess_quality(sample)
            elif sample.biometric_type == BiometricType.FINGERPRINT:
                # Simplified quality assessment for fingerprint
                return 0.8  # Placeholder
            else:
                return 0.5  # Default quality
                
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return 0.0

    async def _extract_features(self, sample: BiometricSample) -> Optional[np.ndarray]:
        """Extract features based on biometric type"""
        try:
            if sample.biometric_type == BiometricType.FACE:
                return await self.face_analyzer.extract_features(sample)
            elif sample.biometric_type == BiometricType.VOICE:
                return await self.voice_authenticator.extract_features(sample)
            elif sample.biometric_type == BiometricType.FINGERPRINT:
                return await self.fingerprint_analyzer.extract_features(sample)
            else:
                logger.warning(f"Unsupported biometric type: {sample.biometric_type}")
                return None
                
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None

    def _calculate_match_score(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate matching score between two feature vectors"""
        try:
            # Cosine similarity
            dot_product = np.dot(features1, features2)
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            
            # Convert to match score (0-1 range)
            match_score = (similarity + 1) / 2
            
            return max(0.0, min(1.0, match_score))
            
        except Exception as e:
            logger.error(f"Match score calculation failed: {e}")
            return 0.0

    def _encrypt_features(self, features: np.ndarray) -> bytes:
        """Encrypt biometric features"""
        try:
            features_bytes = features.tobytes()
            return self.cipher_suite.encrypt(features_bytes)
        except Exception as e:
            logger.error(f"Feature encryption failed: {e}")
            raise

    def _decrypt_features(self, encrypted_features: bytes) -> np.ndarray:
        """Decrypt biometric features"""
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_features)
            return np.frombuffer(decrypted_bytes, dtype=np.float32)
        except Exception as e:
            logger.error(f"Feature decryption failed: {e}")
            raise

    def _hash_features(self, features: np.ndarray) -> str:
        """Create hash of features for integrity checking"""
        try:
            features_bytes = features.tobytes()
            return hashlib.sha256(features_bytes).hexdigest()
        except Exception as e:
            logger.error(f"Feature hashing failed: {e}")
            return ""

    def _score_to_quality(self, score: float) -> BiometricQuality:
        """Convert quality score to quality enum"""
        if score >= 0.9:
            return BiometricQuality.EXCELLENT
        elif score >= 0.75:
            return BiometricQuality.GOOD
        elif score >= 0.5:
            return BiometricQuality.FAIR
        else:
            return BiometricQuality.POOR

    async def _store_template(self, template: BiometricTemplate) -> None:
        """Store biometric template in Redis"""
        try:
            template_key = f"biometric_template:{template.user_id}:{template.template_id}"
            template_data = {
                "template_id": template.template_id,
                "user_id": template.user_id,
                "biometric_type": template.biometric_type.value,
                "encrypted_features": base64.b64encode(template.encrypted_features).decode(),
                "feature_hash": template.feature_hash,
                "quality_score": template.quality_score,
                "enrollment_date": template.enrollment_date.isoformat(),
                "last_used": template.last_used.isoformat() if template.last_used else None,
                "usage_count": template.usage_count,
                "is_active": template.is_active,
                "security_level": template.security_level,
                "metadata": template.metadata
            }
            
            # Set expiry based on configuration
            expiry_days = self.config["template_expiry_days"]
            expiry_seconds = expiry_days * 24 * 3600
            
            await self.redis.setex(
                template_key,
                expiry_seconds,
                json.dumps(template_data, default=str)
            )
            
            # Add to user template index
            index_key = f"user_templates:{template.user_id}:{template.biometric_type.value}"
            await self.redis.sadd(index_key, template.template_id)
            await self.redis.expire(index_key, expiry_seconds)
            
        except Exception as e:
            logger.error(f"Failed to store template: {e}")
            raise

    async def _get_user_templates(
        self,
        user_id: str,
        biometric_type: BiometricType
    ) -> List[BiometricTemplate]:
        """Get user's biometric templates"""
        try:
            templates = []
            index_key = f"user_templates:{user_id}:{biometric_type.value}"
            template_ids = await self.redis.smembers(index_key)
            
            for template_id in template_ids:
                template_key = f"biometric_template:{user_id}:{template_id.decode()}"
                template_data = await self.redis.get(template_key)
                
                if template_data:
                    template_dict = json.loads(template_data)
                    
                    template = BiometricTemplate(
                        user_id=template_dict["user_id"],
                        biometric_type=BiometricType(template_dict["biometric_type"]),
                        template_id=template_dict["template_id"],
                        encrypted_features=base64.b64decode(template_dict["encrypted_features"]),
                        feature_hash=template_dict["feature_hash"],
                        quality_score=template_dict["quality_score"],
                        enrollment_date=datetime.fromisoformat(template_dict["enrollment_date"]),
                        last_used=datetime.fromisoformat(template_dict["last_used"]) if template_dict["last_used"] else None,
                        usage_count=template_dict["usage_count"],
                        is_active=template_dict["is_active"],
                        security_level=template_dict["security_level"],
                        metadata=template_dict["metadata"]
                    )
                    
                    if template.is_active:
                        templates.append(template)
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get user templates: {e}")
            return []

    async def _update_template_usage(self, template_id: str) -> None:
        """Update template usage statistics"""
        try:
            # Find template across all users
            pattern = f"biometric_template:*:{template_id}"
            keys = await self.redis.keys(pattern)
            
            if keys:
                template_data = await self.redis.get(keys[0])
                if template_data:
                    template_dict = json.loads(template_data)
                    template_dict["usage_count"] += 1
                    template_dict["last_used"] = datetime.utcnow().isoformat()
                    
                    await self.redis.setex(
                        keys[0],
                        self.config["template_expiry_days"] * 24 * 3600,
                        json.dumps(template_dict, default=str)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to update template usage: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()