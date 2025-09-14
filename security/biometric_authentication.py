"""
Biometric Authentication module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔐 Biometric Authentication Engine Enterprise - Advanced Identity Verification
============================================================================

Multi-role expertise demonstrated:
- Security Specialist: Advanced biometric security and identity verification
- ML Engineer: Machine learning algorithms for biometric pattern recognition
- Backend Senior: Secure API integration and data handling
- DevOps Engineer: Scalable infrastructure for biometric processing
- DBA: Secure storage of biometric templates and metadata

@author: Fahed Mlaiel <mlaiel@live.de>
@copyright: 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
"""

import os
import sys
import json
import base64
import hashlib
import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import cv2
import face_recognition
import speech_recognition as sr
import pyaudio
import tempfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import redis
from scipy.spatial.distance import cosine
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BiometricTemplate:
    """Biometric template data structure"""
    user_id: str
    biometric_type: str  # face, fingerprint, voice, iris, palm, gait
    template_data: bytes  # Encrypted biometric features
    template_hash: str
    quality_score: float
    enrollment_date: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BiometricSample:
    """Raw biometric sample for processing"""
    biometric_type: str
    raw_data: bytes
    quality_score: float = 0.0
    preprocessing_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class VerificationResult:
    """Biometric verification result"""
    user_id: str
    biometric_type: str
    confidence_score: float
    match_score: float
    verification_time: float
    is_match: bool
    quality_assessment: Dict[str, Any]
    liveness_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class BiometricProcessor:
    """Base class for biometric processing"""
    
    def __init__(self, biometric_type -> None: str) -> None:
        self.biometric_type = biometric_type
        self.quality_threshold = 0.7
        self.verification_threshold = 0.85
        
    def extract_features(self, sample: BiometricSample) -> np.ndarray:
        """Extract biometric features from sample"""
        raise NotImplementedError
    
    def assess_quality(self, sample: BiometricSample) -> float:
        """Assess quality of biometric sample"""
        raise NotImplementedError
    
    def verify(self, sample_features: np.ndarray, template_features: np.ndarray) -> float:
        """Verify biometric sample against template"""
        raise NotImplementedError
    
    def detect_liveness(self, sample: BiometricSample) -> float:
        """Detect if the biometric sample is from a live person"""
        raise NotImplementedError

class FaceProcessor(BiometricProcessor):
    """Face recognition processor with liveness detection"""
    
    def __init__(self) -> None:
        super().__init__("face")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
    def extract_features(self, sample: BiometricSample) -> np.ndarray:
        """Extract face encoding features"""
        try:
            # Convert bytes to image
            nparr = np.frombuffer(sample.raw_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_image)
            if not face_locations:
                raise ValueError("No face detected in image")
            
            # Use the first (largest) face found
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            if not face_encodings:
                raise ValueError("Unable to extract face encoding")
            
            return face_encodings[0]
        
        except Exception as e:
            logger.error(f"Face feature extraction failed: {e}")
            raise
    
    def assess_quality(self, sample: BiometricSample) -> float:
        """Assess face image quality"""
        try:
            nparr = np.frombuffer(sample.raw_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            quality_factors = []
            
            # Check image resolution
            height, width = gray.shape
            resolution_score = min(1.0, (height * width) / (640 * 480))
            quality_factors.append(resolution_score)
            
            # Check face detection confidence
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 1:
                quality_factors.append(1.0)
            elif len(faces) == 0:
                quality_factors.append(0.0)
            else:
                quality_factors.append(0.7)  # Multiple faces detected
            
            # Check eye detection
            eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 4)
            eye_score = min(1.0, len(eyes) / 2.0)  # Expect 2 eyes
            quality_factors.append(eye_score)
            
            # Check image sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000.0)
            quality_factors.append(sharpness_score)
            
            # Check brightness
            mean_brightness = np.mean(gray)
            brightness_score = 1.0 - abs(mean_brightness - 128) / 128.0
            quality_factors.append(brightness_score)
            
            return np.mean(quality_factors)
        
        except Exception as e:
            logger.error(f"Face quality assessment failed: {e}")
            return 0.0
    
    def verify(self, sample_features: np.ndarray, template_features: np.ndarray) -> float:
        """Verify face encoding against template"""
        try:
            # Calculate Euclidean distance
            distance = np.linalg.norm(sample_features - template_features)
            
            # Convert distance to similarity score (0-1)
            # Face recognition typically uses 0.6 as threshold
            similarity = max(0, 1 - (distance / 0.6))
            
            return similarity
        
        except Exception as e:
            logger.error(f"Face verification failed: {e}")
            return 0.0
    
    def detect_liveness(self, sample: BiometricSample) -> float:
        """Detect face liveness using multiple techniques"""
        try:
            nparr = np.frombuffer(sample.raw_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            liveness_scores = []
            
            # Eye blink detection (simplified)
            eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 4)
            if len(eyes) >= 2:
                liveness_scores.append(0.8)  # Eyes detected
            else:
                liveness_scores.append(0.3)
            
            # Texture analysis (LBP - Local Binary Patterns)
            lbp_score = self._analyze_texture(gray)
            liveness_scores.append(lbp_score)
            
            # Edge analysis for print attack detection
            edge_score = self._analyze_edges(gray)
            liveness_scores.append(edge_score)
            
            return np.mean(liveness_scores)
        
        except Exception as e:
            logger.error(f"Liveness detection failed: {e}")
            return 0.0
    
    def _analyze_texture(self, gray_image: np.ndarray) -> float:
        """Analyze image texture for liveness"""
        try:
            # Simple texture analysis using standard deviation
            std_dev = np.std(gray_image)
            
            # Real faces typically have more texture variation
            texture_score = min(1.0, std_dev / 50.0)
            
            return texture_score
        except:
            return 0.5
    
    def _analyze_edges(self, gray_image: np.ndarray) -> float:
        """Analyze edges for print attack detection"""
        try:
            # Detect edges
            edges = cv2.Canny(gray_image, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Real faces have moderate edge density
            if 0.02 <= edge_density <= 0.15:
                return 1.0
            elif edge_density > 0.15:
                return 0.3  # Possibly printed image
            else:
                return 0.5  # Low edge density
        except:
            return 0.5

class VoiceProcessor(BiometricProcessor):
    """Voice recognition processor with anti-spoofing"""
    
    def __init__(self) -> None:
        super().__init__("voice")
        self.sample_rate = 16000
        self.frame_duration = 0.025  # 25ms frames
        self.frame_step = 0.010     # 10ms step
        
    def extract_features(self, sample: BiometricSample) -> np.ndarray:
        """Extract voice features (MFCC, pitch, etc.)"""
        try:
            import librosa
            
            # Load audio from bytes
            audio_data = np.frombuffer(sample.raw_data, dtype=np.float32)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_data, 
                sr=self.sample_rate, 
                n_mfcc=13,
                n_fft=int(self.sample_rate * self.frame_duration),
                hop_length=int(self.sample_rate * self.frame_step)
            )
            
            # Extract pitch features
            pitches, magnitudes = librosa.piptrack(
                y=audio_data, 
                sr=self.sample_rate
            )
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Combine features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1),
                [np.mean(spectral_centroids), np.std(spectral_centroids)],
                [np.mean(spectral_rolloff), np.std(spectral_rolloff)],
                [np.mean(zero_crossing_rate), np.std(zero_crossing_rate)]
            ])
            
            return features
        
        except Exception as e:
            logger.error(f"Voice feature extraction failed: {e}")
            raise
    
    def assess_quality(self, sample: BiometricSample) -> float:
        """Assess voice sample quality"""
        try:
            audio_data = np.frombuffer(sample.raw_data, dtype=np.float32)
            
            quality_factors = []
            
            # Check signal-to-noise ratio
            signal_power = np.mean(audio_data ** 2)
            noise_floor = np.percentile(audio_data ** 2, 10)
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))
            snr_score = min(1.0, max(0.0, (snr - 10) / 20))  # 10-30 dB range
            quality_factors.append(snr_score)
            
            # Check duration
            duration = len(audio_data) / self.sample_rate
            duration_score = min(1.0, max(0.0, (duration - 1.0) / 3.0))  # 1-4 seconds optimal
            quality_factors.append(duration_score)
            
            # Check clipping
            max_amplitude = np.max(np.abs(audio_data))
            clipping_score = 1.0 if max_amplitude < 0.95 else 0.5
            quality_factors.append(clipping_score)
            
            return np.mean(quality_factors)
        
        except Exception as e:
            logger.error(f"Voice quality assessment failed: {e}")
            return 0.0
    
    def verify(self, sample_features: np.ndarray, template_features: np.ndarray) -> float:
        """Verify voice features against template"""
        try:
            # Calculate cosine similarity
            similarity = 1 - cosine(sample_features, template_features)
            
            # Ensure similarity is between 0 and 1
            similarity = max(0, min(1, similarity))
            
            return similarity
        
        except Exception as e:
            logger.error(f"Voice verification failed: {e}")
            return 0.0
    
    def detect_liveness(self, sample: BiometricSample) -> float:
        """Detect voice liveness and anti-spoofing"""
        try:
            audio_data = np.frombuffer(sample.raw_data, dtype=np.float32)
            
            liveness_scores = []
            
            # Check for natural speech patterns
            # Real speech has characteristic formant structures
            speech_score = self._analyze_speech_patterns(audio_data)
            liveness_scores.append(speech_score)
            
            # Check for replay attack indicators
            replay_score = self._detect_replay_attack(audio_data)
            liveness_scores.append(replay_score)
            
            # Check for synthesis artifacts
            synthesis_score = self._detect_synthesis_artifacts(audio_data)
            liveness_scores.append(synthesis_score)
            
            return np.mean(liveness_scores)
        
        except Exception as e:
            logger.error(f"Voice liveness detection failed: {e}")
            return 0.0
    
    def _analyze_speech_patterns(self, audio_data: np.ndarray) -> float:
        """Analyze natural speech patterns"""
        try:
            import librosa
            
            # Extract formants (simplified)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            
            # Check for natural formant structure
            formant_variation = np.std(mfccs, axis=1)
            natural_score = min(1.0, np.mean(formant_variation) / 10.0)
            
            return natural_score
        except:
            return 0.5
    
    def _detect_replay_attack(self, audio_data: np.ndarray) -> float:
        """Detect replay attack indicators"""
        try:
            # Check for channel artifacts (simplified)
            # Real recordings have different channel characteristics than replays
            spectral_flatness = np.var(np.abs(np.fft.fft(audio_data)))
            
            # Normalize score
            replay_score = min(1.0, spectral_flatness / 1000.0)
            
            return replay_score
        except:
            return 0.5
    
    def _detect_synthesis_artifacts(self, audio_data: np.ndarray) -> float:
        """Detect synthetic speech artifacts"""
        try:
            # Check for typical synthesis artifacts
            # Synthetic speech often has different spectral characteristics
            import librosa
            
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)
            
            # Natural speech has characteristic spectral properties
            centroid_variance = np.var(spectral_centroid)
            bandwidth_variance = np.var(spectral_bandwidth)
            
            synthesis_score = min(1.0, (centroid_variance + bandwidth_variance) / 1000.0)
            
            return synthesis_score
        except:
            return 0.5

class BiometricAuthenticationEngine:
    """
    Enterprise Biometric Authentication Engine
    Advanced multi-modal biometric verification system
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize biometric authentication engine"""
        self.config = config or {}
        self.database_path = self.config.get('database_path', 'biometric_templates.db')
        self.redis_client = None
        self.encryption_key = None
        
        # Initialize processors
        self.processors = {
            'face': FaceProcessor(),
            'voice': VoiceProcessor()
        }
        
        # Initialize database
        self._initialize_database()
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Initialize Redis for caching
        self._initialize_redis()
        
        # Performance metrics
        self.metrics = {
            'enrollments': 0,
            'verifications': 0,
            'successful_verifications': 0,
            'failed_verifications': 0,
            'false_acceptance_rate': 0.0,
            'false_rejection_rate': 0.0
        }
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database for template storage"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS biometric_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    biometric_type TEXT NOT NULL,
                    template_data BLOB NOT NULL,
                    template_hash TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    enrollment_date TEXT NOT NULL,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    metadata TEXT,
                    UNIQUE(user_id, biometric_type)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    biometric_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    match_score REAL NOT NULL,
                    is_match INTEGER NOT NULL,
                    liveness_score REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Biometric database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption for template protection"""
        try:
            # Use a key derivation function for the encryption key
            password = self.config.get('encryption_password', 'default_password').encode()
            salt = self.config.get('encryption_salt', b'salt_1234567890')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.encryption_key = Fernet(key)
            
            logger.info("Encryption initialized successfully")
        
        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            raise
    
    def _initialize_redis(self) -> None:
        """Initialize Redis for caching"""
        try:
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=False
            )
            
            # Test connection
            self.redis_client.ping()
            
            logger.info("Redis connection initialized successfully")
        
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def enroll_user(self, user_id: str, biometric_samples: List[BiometricSample]) -> Dict[str, Any]:
        """
        Enroll user with biometric samples
        
        Args:
            user_id: Unique user identifier
            biometric_samples: List of biometric samples
            
        Returns:
            Dictionary with enrollment results
        """
        enrollment_results = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'enrolled_biometrics': [],
            'failed_enrollments': [],
            'overall_success': True
        }
        
        for sample in biometric_samples:
            try:
                processor = self.processors.get(sample.biometric_type)
                if not processor:
                    enrollment_results['failed_enrollments'].append({
                        'biometric_type': sample.biometric_type,
                        'error': 'Unsupported biometric type'
                    })
                    continue
                
                # Assess sample quality
                quality_score = processor.assess_quality(sample)
                if quality_score < processor.quality_threshold:
                    enrollment_results['failed_enrollments'].append({
                        'biometric_type': sample.biometric_type,
                        'error': f'Quality too low: {quality_score:.2f}'
                    })
                    continue
                
                # Extract features
                features = processor.extract_features(sample)
                
                # Create template
                template = BiometricTemplate(
                    user_id=user_id,
                    biometric_type=sample.biometric_type,
                    template_data=self._encrypt_template(features.tobytes()),
                    template_hash=hashlib.sha256(features.tobytes()).hexdigest(),
                    quality_score=quality_score,
                    enrollment_date=datetime.now()
                )
                
                # Store template
                await self._store_template(template)
                
                enrollment_results['enrolled_biometrics'].append({
                    'biometric_type': sample.biometric_type,
                    'quality_score': quality_score,
                    'template_hash': template.template_hash
                })
                
                self.metrics['enrollments'] += 1
            
            except Exception as e:
                logger.error(f"Enrollment failed for {sample.biometric_type}: {e}")
                enrollment_results['failed_enrollments'].append({
                    'biometric_type': sample.biometric_type,
                    'error': str(e)
                })
                enrollment_results['overall_success'] = False
        
        return enrollment_results
    
    async def verify_user(self, user_id: str, biometric_sample: BiometricSample, 
                         context: Dict[str, Any] = None) -> VerificationResult:
        """
        Verify user identity using biometric sample
        
        Args:
            user_id: User identifier to verify against
            biometric_sample: Biometric sample for verification
            context: Additional context (IP, user agent, etc.)
            
        Returns:
            VerificationResult object
        """
        start_time = time.time()
        
        try:
            processor = self.processors.get(biometric_sample.biometric_type)
            if not processor:
                raise ValueError(f"Unsupported biometric type: {biometric_sample.biometric_type}")
            
            # Assess sample quality
            quality_score = processor.assess_quality(biometric_sample)
            quality_assessment = {
                'quality_score': quality_score,
                'meets_threshold': quality_score >= processor.quality_threshold
            }
            
            if quality_score < processor.quality_threshold:
                return VerificationResult(
                    user_id=user_id,
                    biometric_type=biometric_sample.biometric_type,
                    confidence_score=0.0,
                    match_score=0.0,
                    verification_time=time.time() - start_time,
                    is_match=False,
                    quality_assessment=quality_assessment
                )
            
            # Detect liveness
            liveness_score = processor.detect_liveness(biometric_sample)
            if liveness_score < 0.5:  # Liveness threshold
                return VerificationResult(
                    user_id=user_id,
                    biometric_type=biometric_sample.biometric_type,
                    confidence_score=0.0,
                    match_score=0.0,
                    verification_time=time.time() - start_time,
                    is_match=False,
                    quality_assessment=quality_assessment,
                    liveness_score=liveness_score
                )
            
            # Extract features
            sample_features = processor.extract_features(biometric_sample)
            
            # Load user template
            template = await self._load_template(user_id, biometric_sample.biometric_type)
            if not template:
                return VerificationResult(
                    user_id=user_id,
                    biometric_type=biometric_sample.biometric_type,
                    confidence_score=0.0,
                    match_score=0.0,
                    verification_time=time.time() - start_time,
                    is_match=False,
                    quality_assessment=quality_assessment,
                    liveness_score=liveness_score
                )
            
            # Decrypt template features
            template_data = self._decrypt_template(template.template_data)
            template_features = np.frombuffer(template_data, dtype=np.float64)
            
            # Verify against template
            match_score = processor.verify(sample_features, template_features)
            is_match = match_score >= processor.verification_threshold
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                match_score, quality_score, liveness_score
            )
            
            # Create verification result
            result = VerificationResult(
                user_id=user_id,
                biometric_type=biometric_sample.biometric_type,
                confidence_score=confidence_score,
                match_score=match_score,
                verification_time=time.time() - start_time,
                is_match=is_match,
                quality_assessment=quality_assessment,
                liveness_score=liveness_score
            )
            
            # Log verification
            await self._log_verification(result, context)
            
            # Update metrics
            self.metrics['verifications'] += 1
            if is_match:
                self.metrics['successful_verifications'] += 1
            else:
                self.metrics['failed_verifications'] += 1
            
            # Update template usage
            await self._update_template_usage(template)
            
            return result
        
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return VerificationResult(
                user_id=user_id,
                biometric_type=biometric_sample.biometric_type,
                confidence_score=0.0,
                match_score=0.0,
                verification_time=time.time() - start_time,
                is_match=False,
                quality_assessment={'error': str(e)},
                liveness_score=0.0
            )
    
    def _encrypt_template(self, template_data: bytes) -> bytes:
        """Encrypt biometric template data"""
        return self.encryption_key.encrypt(template_data)
    
    def _decrypt_template(self, encrypted_data: bytes) -> bytes:
        """Decrypt biometric template data"""
        return self.encryption_key.decrypt(encrypted_data)
    
    async def _store_template(self, template -> None: BiometricTemplate) -> None:
        """Store biometric template in database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO biometric_templates 
                (user_id, biometric_type, template_data, template_hash, quality_score, 
                 enrollment_date, last_used, usage_count, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.user_id,
                template.biometric_type,
                template.template_data,
                template.template_hash,
                template.quality_score,
                template.enrollment_date.isoformat(),
                template.last_used.isoformat() if template.last_used else None,
                template.usage_count,
                1 if template.is_active else 0,
                json.dumps(template.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Cache in Redis if available
            if self.redis_client:
                cache_key = f"biometric_template:{template.user_id}:{template.biometric_type}"
                cache_data = {
                    'template_data': base64.b64encode(template.template_data).decode(),
                    'template_hash': template.template_hash,
                    'quality_score': template.quality_score,
                    'enrollment_date': template.enrollment_date.isoformat()
                }
                self.redis_client.setex(cache_key, 3600, json.dumps(cache_data))
            
        except Exception as e:
            logger.error(f"Template storage failed: {e}")
            raise
    
    async def _load_template(self, user_id: str, biometric_type: str) -> Optional[BiometricTemplate]:
        """Load biometric template from database or cache"""
        try:
            # Try Redis cache first
            if self.redis_client:
                cache_key = f"biometric_template:{user_id}:{biometric_type}"
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    return BiometricTemplate(
                        user_id=user_id,
                        biometric_type=biometric_type,
                        template_data=base64.b64decode(data['template_data']),
                        template_hash=data['template_hash'],
                        quality_score=data['quality_score'],
                        enrollment_date=datetime.fromisoformat(data['enrollment_date'])
                    )
            
            # Load from database
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_data, template_hash, quality_score, enrollment_date,
                       last_used, usage_count, is_active, metadata
                FROM biometric_templates
                WHERE user_id = ? AND biometric_type = ? AND is_active = 1
            ''', (user_id, biometric_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return BiometricTemplate(
                    user_id=user_id,
                    biometric_type=biometric_type,
                    template_data=row[0],
                    template_hash=row[1],
                    quality_score=row[2],
                    enrollment_date=datetime.fromisoformat(row[3]),
                    last_used=datetime.fromisoformat(row[4]) if row[4] else None,
                    usage_count=row[5],
                    is_active=bool(row[6]),
                    metadata=json.loads(row[7]) if row[7] else {}
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Template loading failed: {e}")
            return None
    
    async def _log_verification(self, result -> None: VerificationResult, context -> None: Dict[str, Any] = None) -> None:
        """Log verification attempt"""
        try:
            context = context or {}
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO verification_logs
                (user_id, biometric_type, confidence_score, match_score, is_match,
                 liveness_score, timestamp, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.user_id,
                result.biometric_type,
                result.confidence_score,
                result.match_score,
                1 if result.is_match else 0,
                result.liveness_score,
                result.timestamp.isoformat(),
                context.get('ip_address'),
                context.get('user_agent')
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Verification logging failed: {e}")
    
    async def _update_template_usage(self, template -> None: BiometricTemplate) -> None:
        """Update template usage statistics"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE biometric_templates
                SET last_used = ?, usage_count = usage_count + 1
                WHERE user_id = ? AND biometric_type = ?
            ''', (
                datetime.now().isoformat(),
                template.user_id,
                template.biometric_type
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Template usage update failed: {e}")
    
    def _calculate_confidence(self, match_score: float, quality_score: float, 
                            liveness_score: float) -> float:
        """Calculate overall confidence score"""
        # Weighted combination of factors
        weights = {
            'match': 0.6,
            'quality': 0.2,
            'liveness': 0.2
        }
        
        confidence = (
            weights['match'] * match_score +
            weights['quality'] * quality_score +
            weights['liveness'] * liveness_score
        )
        
        return min(1.0, max(0.0, confidence))
    
    async def get_user_templates(self, user_id: str) -> List[BiometricTemplate]:
        """Get all biometric templates for a user"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT biometric_type, template_data, template_hash, quality_score,
                       enrollment_date, last_used, usage_count, is_active, metadata
                FROM biometric_templates
                WHERE user_id = ?
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            templates = []
            for row in rows:
                templates.append(BiometricTemplate(
                    user_id=user_id,
                    biometric_type=row[0],
                    template_data=row[1],
                    template_hash=row[2],
                    quality_score=row[3],
                    enrollment_date=datetime.fromisoformat(row[4]),
                    last_used=datetime.fromisoformat(row[5]) if row[5] else None,
                    usage_count=row[6],
                    is_active=bool(row[7]),
                    metadata=json.loads(row[8]) if row[8] else {}
                ))
            
            return templates
        
        except Exception as e:
            logger.error(f"Template retrieval failed: {e}")
            return []
    
    async def delete_user_templates(self, user_id: str, biometric_type: str = None) -> bool:
        """Delete user's biometric templates"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            if biometric_type:
                cursor.execute('''
                    DELETE FROM biometric_templates
                    WHERE user_id = ? AND biometric_type = ?
                ''', (user_id, biometric_type))
                
                # Remove from cache
                if self.redis_client:
                    cache_key = f"biometric_template:{user_id}:{biometric_type}"
                    self.redis_client.delete(cache_key)
            else:
                cursor.execute('''
                    DELETE FROM biometric_templates
                    WHERE user_id = ?
                ''', (user_id,))
                
                # Remove all cached templates for user
                if self.redis_client:
                    pattern = f"biometric_template:{user_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            
            conn.commit()
            conn.close()
            
            return True
        
        except Exception as e:
            logger.error(f"Template deletion failed: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total_verifications = self.metrics['verifications']
        if total_verifications > 0:
            self.metrics['false_acceptance_rate'] = (
                self.metrics['failed_verifications'] / total_verifications
            )
            self.metrics['false_rejection_rate'] = (
                self.metrics['successful_verifications'] / total_verifications
            )
        
        return self.metrics.copy()

# CLI interface for testing
async def main() -> None:
    """Main function for command-line testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Biometric Authentication Engine')
    parser.add_argument('action', choices=['enroll', 'verify', 'list', 'delete'])
    parser.add_argument('--user-id', required=True, help='User ID')
    parser.add_argument('--biometric-type', choices=['face', 'voice'], help='Biometric type')
    parser.add_argument('--sample-file', help='Biometric sample file')
    parser.add_argument('--config', help='Configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize engine
    engine = BiometricAuthenticationEngine(config)
    
    try:
        if args.action == 'enroll':
            if not args.sample_file or not args.biometric_type:
                print("Error: --sample-file and --biometric-type required for enrollment")
                return
            
            with open(args.sample_file, 'rb') as f:
                sample_data = f.read()
            
            sample = BiometricSample(
                biometric_type=args.biometric_type,
                raw_data=sample_data
            )
            
            result = await engine.enroll_user(args.user_id, [sample])
            print(json.dumps(result, indent=2))
        
        elif args.action == 'verify':
            if not args.sample_file or not args.biometric_type:
                print("Error: --sample-file and --biometric-type required for verification")
                return
            
            with open(args.sample_file, 'rb') as f:
                sample_data = f.read()
            
            sample = BiometricSample(
                biometric_type=args.biometric_type,
                raw_data=sample_data
            )
            
            result = await engine.verify_user(args.user_id, sample)
            print(f"Verification Result:")
            print(f"  Match: {result.is_match}")
            print(f"  Confidence: {result.confidence_score:.3f}")
            print(f"  Match Score: {result.match_score:.3f}")
            print(f"  Liveness Score: {result.liveness_score:.3f}")
            print(f"  Time: {result.verification_time:.3f}s")
        
        elif args.action == 'list':
            templates = await engine.get_user_templates(args.user_id)
            print(f"Biometric templates for user {args.user_id}:")
            for template in templates:
                print(f"  {template.biometric_type}: Quality {template.quality_score:.3f}, "
                      f"Used {template.usage_count} times")
        
        elif args.action == 'delete':
            success = await engine.delete_user_templates(args.user_id, args.biometric_type)
            if success:
                print(f"Templates deleted for user {args.user_id}")
            else:
                print(f"Failed to delete templates for user {args.user_id}")
    
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())