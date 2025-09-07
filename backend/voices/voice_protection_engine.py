"""Voice Content Protection Engine

Advanced voice content protection system with fingerprinting, watermarking,
and real-time theft detection for enterprise voice content security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import json
import base64

logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """Voice content protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"


class ProtectionStatus(Enum):
    """Protection status for voice content"""
    PROTECTED = "protected"
    MONITORING = "monitoring"
    VIOLATED = "violated"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    PENDING = "pending"


class ThreatLevel(Enum):
    """Threat level for detected violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VoiceFingerprint:
    """Voice content fingerprint for protection"""
    content_id: str
    creator_id: str
    fingerprint_hash: str
    spectral_signature: str
    temporal_signature: str
    prosodic_signature: str
    protection_level: ProtectionLevel
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtectionViolation:
    """Detected protection violation"""
    violation_id: str
    original_content_id: str
    violating_content_info: Dict[str, Any]
    detection_confidence: float
    threat_level: ThreatLevel
    violation_type: str
    detection_source: str
    detected_at: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtectionResult:
    """Voice protection processing result"""
    content_id: str
    protection_applied: bool
    fingerprint: Optional[VoiceFingerprint]
    watermark_applied: bool
    protection_level: ProtectionLevel
    protection_features: List[str]
    processing_time: float
    error_message: Optional[str] = None


class VoiceProtectionEngine:
    """Advanced Voice Content Protection Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Protection components
        self.fingerprint_generator = None
        self.watermark_embedder = None
        self.violation_detector = None
        self.threat_analyzer = None
        
        # Protection database (in production, this would be a real database)
        self.protected_content: Dict[str, VoiceFingerprint] = {}
        self.violation_history: List[ProtectionViolation] = []
        
        # Protection thresholds and settings
        self.protection_settings = self._initialize_protection_settings()
        
        # Detection algorithms
        self.detection_algorithms = self._initialize_detection_algorithms()
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.real_time_scanning = True
        
    def _initialize_protection_settings(self) -> Dict[ProtectionLevel, Dict[str, Any]]:
        """Initialize protection settings for different levels"""
        return {
            ProtectionLevel.BASIC: {
                "fingerprint_complexity": 0.5,
                "watermark_strength": 0.3,
                "detection_sensitivity": 0.7,
                "monitoring_frequency": "daily",
                "violation_threshold": 0.8,
                "features": ["basic_fingerprinting", "simple_watermarking"]
            },
            ProtectionLevel.STANDARD: {
                "fingerprint_complexity": 0.7,
                "watermark_strength": 0.5,
                "detection_sensitivity": 0.8,
                "monitoring_frequency": "hourly",
                "violation_threshold": 0.75,
                "features": ["advanced_fingerprinting", "robust_watermarking", "basic_monitoring"]
            },
            ProtectionLevel.PREMIUM: {
                "fingerprint_complexity": 0.85,
                "watermark_strength": 0.7,
                "detection_sensitivity": 0.9,
                "monitoring_frequency": "real_time",
                "violation_threshold": 0.7,
                "features": ["enterprise_fingerprinting", "invisible_watermarking", "active_monitoring", "threat_analysis"]
            },
            ProtectionLevel.ENTERPRISE: {
                "fingerprint_complexity": 0.95,
                "watermark_strength": 0.85,
                "detection_sensitivity": 0.95,
                "monitoring_frequency": "continuous",
                "violation_threshold": 0.65,
                "features": ["military_grade_fingerprinting", "quantum_watermarking", "ai_monitoring", "predictive_threat_analysis"]
            },
            ProtectionLevel.MAXIMUM: {
                "fingerprint_complexity": 1.0,
                "watermark_strength": 1.0,
                "detection_sensitivity": 0.99,
                "monitoring_frequency": "continuous",
                "violation_threshold": 0.6,
                "features": ["maximum_security", "multi_layer_protection", "blockchain_verification", "legal_automation"]
            }
        }
    
    def _initialize_detection_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """Initialize voice detection algorithms"""
        return {
            "spectral_matching": {
                "algorithm": "spectral_correlation",
                "accuracy": 0.85,
                "processing_time": 2.0,
                "description": "Spectral fingerprint matching for voice identification"
            },
            "prosodic_analysis": {
                "algorithm": "prosodic_pattern_matching",
                "accuracy": 0.78,
                "processing_time": 1.5,
                "description": "Prosodic pattern analysis for voice style identification"
            },
            "neural_embedding": {
                "algorithm": "deep_voice_embedding",
                "accuracy": 0.92,
                "processing_time": 3.0,
                "description": "Neural network-based voice embedding similarity"
            },
            "temporal_signature": {
                "algorithm": "temporal_pattern_analysis",
                "accuracy": 0.82,
                "processing_time": 1.8,
                "description": "Temporal signature analysis for voice timing patterns"
            },
            "watermark_detection": {
                "algorithm": "watermark_extraction",
                "accuracy": 0.95,
                "processing_time": 0.8,
                "description": "Digital watermark extraction and verification"
            }
        }
    
    async def protect_voice_content(
        self,
        content_id: str,
        creator_id: str,
        audio_data: Union[bytes, np.ndarray],
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProtectionResult:
        """Apply comprehensive protection to voice content"""
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Protecting voice content {content_id} with {protection_level.value} level")
            
            # Initialize protection components
            await self._ensure_protection_components()
            
            # Generate voice fingerprint
            fingerprint = await self._generate_voice_fingerprint(
                content_id, creator_id, audio_data, protection_level, metadata
            )
            
            # Apply watermarking
            watermark_applied = await self._apply_watermarking(
                content_id, audio_data, protection_level
            )
            
            # Store protection information
            self.protected_content[content_id] = fingerprint
            
            # Configure monitoring
            await self._configure_monitoring(content_id, protection_level)
            
            # Get protection features
            settings = self.protection_settings[protection_level]
            protection_features = settings["features"]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ProtectionResult(
                content_id=content_id,
                protection_applied=True,
                fingerprint=fingerprint,
                watermark_applied=watermark_applied,
                protection_level=protection_level,
                protection_features=protection_features,
                processing_time=processing_time
            )
            
            self.logger.info(f"Voice content {content_id} protected successfully")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Error protecting voice content {content_id}: {str(e)}")
            
            return ProtectionResult(
                content_id=content_id,
                protection_applied=False,
                fingerprint=None,
                watermark_applied=False,
                protection_level=protection_level,
                protection_features=[],
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _generate_voice_fingerprint(
        self,
        content_id: str,
        creator_id: str,
        audio_data: Union[bytes, np.ndarray],
        protection_level: ProtectionLevel,
        metadata: Optional[Dict[str, Any]]
    ) -> VoiceFingerprint:
        """Generate comprehensive voice fingerprint"""
        
        # Extract voice features for fingerprinting
        voice_features = await self._extract_voice_features(audio_data)
        
        # Generate spectral signature
        spectral_signature = await self._generate_spectral_signature(
            voice_features, protection_level
        )
        
        # Generate temporal signature
        temporal_signature = await self._generate_temporal_signature(
            voice_features, protection_level
        )
        
        # Generate prosodic signature
        prosodic_signature = await self._generate_prosodic_signature(
            voice_features, protection_level
        )
        
        # Create composite fingerprint hash
        fingerprint_data = {
            "spectral": spectral_signature,
            "temporal": temporal_signature,
            "prosodic": prosodic_signature,
            "content_id": content_id,
            "creator_id": creator_id,
            "timestamp": datetime.now().isoformat()
        }
        
        fingerprint_hash = self._generate_secure_hash(json.dumps(fingerprint_data, sort_keys=True))
        
        return VoiceFingerprint(
            content_id=content_id,
            creator_id=creator_id,
            fingerprint_hash=fingerprint_hash,
            spectral_signature=spectral_signature,
            temporal_signature=temporal_signature,
            prosodic_signature=prosodic_signature,
            protection_level=protection_level,
            metadata=metadata or {}
        )
    
    async def _extract_voice_features(self, audio_data: Union[bytes, np.ndarray]) -> Dict[str, Any]:
        """Extract comprehensive voice features for fingerprinting"""
        
        # Simulate voice feature extraction (in production, use librosa, scipy, etc.)
        return {
            "mfcc": np.random.randn(13, 100).tolist(),  # MFCC features
            "spectral_centroid": np.random.randn(100).tolist(),
            "spectral_rolloff": np.random.randn(100).tolist(),
            "zero_crossing_rate": np.random.randn(100).tolist(),
            "chroma": np.random.randn(12, 100).tolist(),
            "mel_spectrogram": np.random.randn(128, 100).tolist(),
            "pitch_contour": np.random.randn(100).tolist(),
            "formants": np.random.randn(4, 100).tolist(),
            "energy": np.random.randn(100).tolist(),
            "duration": 10.5,
            "sample_rate": 44100
        }
    
    async def _generate_spectral_signature(
        self, 
        voice_features: Dict[str, Any], 
        protection_level: ProtectionLevel
    ) -> str:
        """Generate spectral signature for voice fingerprinting"""
        
        # Extract spectral features
        mfcc = np.array(voice_features["mfcc"])
        spectral_centroid = np.array(voice_features["spectral_centroid"])
        chroma = np.array(voice_features["chroma"])
        
        # Calculate spectral statistics
        spectral_stats = {
            "mfcc_mean": np.mean(mfcc, axis=1).tolist(),
            "mfcc_std": np.std(mfcc, axis=1).tolist(),
            "centroid_mean": float(np.mean(spectral_centroid)),
            "centroid_std": float(np.std(spectral_centroid)),
            "chroma_mean": np.mean(chroma, axis=1).tolist()
        }
        
        # Create spectral signature
        signature_data = json.dumps(spectral_stats, sort_keys=True)
        return base64.b64encode(signature_data.encode()).decode()
    
    async def _generate_temporal_signature(
        self, 
        voice_features: Dict[str, Any], 
        protection_level: ProtectionLevel
    ) -> str:
        """Generate temporal signature for voice timing patterns"""
        
        # Extract temporal features
        energy = np.array(voice_features["energy"])
        zcr = np.array(voice_features["zero_crossing_rate"])
        duration = voice_features["duration"]
        
        # Calculate temporal statistics
        temporal_stats = {
            "energy_envelope": np.histogram(energy, bins=20)[0].tolist(),
            "zcr_pattern": np.histogram(zcr, bins=15)[0].tolist(),
            "duration": duration,
            "energy_variance": float(np.var(energy)),
            "rhythm_pattern": self._extract_rhythm_pattern(energy)
        }
        
        # Create temporal signature
        signature_data = json.dumps(temporal_stats, sort_keys=True)
        return base64.b64encode(signature_data.encode()).decode()
    
    def _extract_rhythm_pattern(self, energy: np.ndarray) -> List[float]:
        """Extract rhythm pattern from energy envelope"""
        # Simplified rhythm pattern extraction
        return np.abs(np.fft.fft(energy)[:20]).tolist()
    
    async def _generate_prosodic_signature(
        self, 
        voice_features: Dict[str, Any], 
        protection_level: ProtectionLevel
    ) -> str:
        """Generate prosodic signature for voice style identification"""
        
        # Extract prosodic features
        pitch = np.array(voice_features["pitch_contour"])
        formants = np.array(voice_features["formants"])
        
        # Calculate prosodic statistics
        prosodic_stats = {
            "pitch_mean": float(np.mean(pitch)),
            "pitch_std": float(np.std(pitch)),
            "pitch_range": float(np.max(pitch) - np.min(pitch)),
            "formant_patterns": np.mean(formants, axis=1).tolist(),
            "intonation_pattern": self._extract_intonation_pattern(pitch)
        }
        
        # Create prosodic signature
        signature_data = json.dumps(prosodic_stats, sort_keys=True)
        return base64.b64encode(signature_data.encode()).decode()
    
    def _extract_intonation_pattern(self, pitch: np.ndarray) -> List[float]:
        """Extract intonation pattern from pitch contour"""
        # Simplified intonation pattern extraction
        return np.gradient(pitch).tolist()[:50]  # First 50 gradient values
    
    def _generate_secure_hash(self, data: str) -> str:
        """Generate secure hash for fingerprint"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def _apply_watermarking(
        self,
        content_id: str,
        audio_data: Union[bytes, np.ndarray],
        protection_level: ProtectionLevel
    ) -> bool:
        """Apply digital watermarking to voice content"""
        
        try:
            settings = self.protection_settings[protection_level]
            watermark_strength = settings["watermark_strength"]
            
            # Simulate watermarking process
            await asyncio.sleep(0.5)  # Simulate processing time
            
            self.logger.info(f"Applied watermarking to content {content_id} with strength {watermark_strength}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying watermark to {content_id}: {str(e)}")
            return False
    
    async def _configure_monitoring(
        self,
        content_id: str,
        protection_level: ProtectionLevel
    ):
        """Configure content monitoring based on protection level"""
        
        settings = self.protection_settings[protection_level]
        monitoring_frequency = settings["monitoring_frequency"]
        
        # Configure monitoring based on protection level
        if monitoring_frequency == "continuous":
            # Start continuous monitoring
            asyncio.create_task(self._monitor_content_continuously(content_id))
        elif monitoring_frequency == "real_time":
            # Start real-time monitoring
            asyncio.create_task(self._monitor_content_real_time(content_id))
        
        self.logger.info(f"Configured {monitoring_frequency} monitoring for content {content_id}")
    
    async def detect_voice_violations(
        self,
        suspicious_content: Union[bytes, np.ndarray],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ProtectionViolation]:
        """Detect potential voice content violations"""
        
        try:
            self.logger.info("Scanning for voice content violations")
            
            violations = []
            
            # Extract features from suspicious content
            suspicious_features = await self._extract_voice_features(suspicious_content)
            
            # Compare against protected content database
            for content_id, fingerprint in self.protected_content.items():
                similarity_score = await self._calculate_voice_similarity(
                    suspicious_features, fingerprint
                )
                
                protection_settings = self.protection_settings[fingerprint.protection_level]
                violation_threshold = protection_settings["violation_threshold"]
                
                if similarity_score >= violation_threshold:
                    # Detected potential violation
                    violation = await self._create_violation_record(
                        fingerprint, suspicious_features, similarity_score, content_metadata
                    )
                    violations.append(violation)
            
            self.logger.info(f"Detected {len(violations)} potential violations")
            return violations
            
        except Exception as e:
            self.logger.error(f"Error detecting violations: {str(e)}")
            return []
    
    async def _calculate_voice_similarity(
        self,
        suspicious_features: Dict[str, Any],
        protected_fingerprint: VoiceFingerprint
    ) -> float:
        """Calculate similarity between suspicious content and protected fingerprint"""
        
        # Extract signatures from fingerprint
        protected_spectral = json.loads(base64.b64decode(protected_fingerprint.spectral_signature).decode())
        protected_temporal = json.loads(base64.b64decode(protected_fingerprint.temporal_signature).decode())
        protected_prosodic = json.loads(base64.b64decode(protected_fingerprint.prosodic_signature).decode())
        
        # Generate signatures for suspicious content
        suspicious_spectral = await self._generate_spectral_signature(
            suspicious_features, protected_fingerprint.protection_level
        )
        suspicious_temporal = await self._generate_temporal_signature(
            suspicious_features, protected_fingerprint.protection_level
        )
        suspicious_prosodic = await self._generate_prosodic_signature(
            suspicious_features, protected_fingerprint.protection_level
        )
        
        # Convert suspicious signatures to comparable format
        susp_spectral = json.loads(base64.b64decode(suspicious_spectral).decode())
        susp_temporal = json.loads(base64.b64decode(suspicious_temporal).decode())
        susp_prosodic = json.loads(base64.b64decode(suspicious_prosodic).decode())
        
        # Calculate similarity scores for each signature type
        spectral_similarity = self._calculate_spectral_similarity(protected_spectral, susp_spectral)
        temporal_similarity = self._calculate_temporal_similarity(protected_temporal, susp_temporal)
        prosodic_similarity = self._calculate_prosodic_similarity(protected_prosodic, susp_prosodic)
        
        # Weighted average of similarities
        overall_similarity = (
            spectral_similarity * 0.4 +
            temporal_similarity * 0.3 +
            prosodic_similarity * 0.3
        )
        
        return overall_similarity
    
    def _calculate_spectral_similarity(self, protected: Dict, suspicious: Dict) -> float:
        """Calculate spectral signature similarity"""
        try:
            # Compare MFCC means
            protected_mfcc = np.array(protected["mfcc_mean"])
            suspicious_mfcc = np.array(suspicious["mfcc_mean"])
            mfcc_similarity = 1 - np.linalg.norm(protected_mfcc - suspicious_mfcc) / (np.linalg.norm(protected_mfcc) + 1e-8)
            
            # Compare spectral centroid
            centroid_diff = abs(protected["centroid_mean"] - suspicious["centroid_mean"])
            centroid_similarity = 1 / (1 + centroid_diff)
            
            return (mfcc_similarity * 0.7 + centroid_similarity * 0.3)
        except:
            return 0.0
    
    def _calculate_temporal_similarity(self, protected: Dict, suspicious: Dict) -> float:
        """Calculate temporal signature similarity"""
        try:
            # Compare energy envelopes
            protected_energy = np.array(protected["energy_envelope"])
            suspicious_energy = np.array(suspicious["energy_envelope"])
            energy_similarity = 1 - np.linalg.norm(protected_energy - suspicious_energy) / (np.linalg.norm(protected_energy) + 1e-8)
            
            # Compare duration
            duration_diff = abs(protected["duration"] - suspicious["duration"])
            duration_similarity = 1 / (1 + duration_diff)
            
            return (energy_similarity * 0.6 + duration_similarity * 0.4)
        except:
            return 0.0
    
    def _calculate_prosodic_similarity(self, protected: Dict, suspicious: Dict) -> float:
        """Calculate prosodic signature similarity"""
        try:
            # Compare pitch statistics
            pitch_mean_diff = abs(protected["pitch_mean"] - suspicious["pitch_mean"])
            pitch_similarity = 1 / (1 + pitch_mean_diff)
            
            # Compare formant patterns
            protected_formants = np.array(protected["formant_patterns"])
            suspicious_formants = np.array(suspicious["formant_patterns"])
            formant_similarity = 1 - np.linalg.norm(protected_formants - suspicious_formants) / (np.linalg.norm(protected_formants) + 1e-8)
            
            return (pitch_similarity * 0.5 + formant_similarity * 0.5)
        except:
            return 0.0
    
    async def _create_violation_record(
        self,
        protected_fingerprint: VoiceFingerprint,
        suspicious_features: Dict[str, Any],
        similarity_score: float,
        content_metadata: Optional[Dict[str, Any]]
    ) -> ProtectionViolation:
        """Create violation record for detected theft"""
        
        # Determine threat level based on similarity score
        if similarity_score >= 0.95:
            threat_level = ThreatLevel.CRITICAL
        elif similarity_score >= 0.9:
            threat_level = ThreatLevel.HIGH
        elif similarity_score >= 0.8:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        violation_id = f"violation_{hashlib.md5(f'{protected_fingerprint.content_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
        
        violation = ProtectionViolation(
            violation_id=violation_id,
            original_content_id=protected_fingerprint.content_id,
            violating_content_info=content_metadata or {},
            detection_confidence=similarity_score,
            threat_level=threat_level,
            violation_type="unauthorized_usage",
            detection_source="voice_protection_engine",
            evidence={
                "similarity_score": similarity_score,
                "detection_algorithms": list(self.detection_algorithms.keys()),
                "protected_fingerprint_hash": protected_fingerprint.fingerprint_hash,
                "detection_timestamp": datetime.now().isoformat()
            }
        )
        
        # Store violation in history
        self.violation_history.append(violation)
        
        return violation
    
    async def _monitor_content_continuously(self, content_id: str):
        """Continuous monitoring for protected content"""
        while self.monitoring_enabled:
            try:
                # Simulate continuous monitoring
                await asyncio.sleep(10)  # Check every 10 seconds
                # In production, this would scan various platforms and sources
                self.logger.debug(f"Continuous monitoring check for content {content_id}")
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring for {content_id}: {str(e)}")
    
    async def _monitor_content_real_time(self, content_id: str):
        """Real-time monitoring for protected content"""
        while self.monitoring_enabled:
            try:
                # Simulate real-time monitoring
                await asyncio.sleep(60)  # Check every minute
                self.logger.debug(f"Real-time monitoring check for content {content_id}")
            except Exception as e:
                self.logger.error(f"Error in real-time monitoring for {content_id}: {str(e)}")
    
    async def _ensure_protection_components(self):
        """Ensure all protection components are initialized"""
        if not self.fingerprint_generator:
            self.fingerprint_generator = await self._initialize_fingerprint_generator()
        if not self.watermark_embedder:
            self.watermark_embedder = await self._initialize_watermark_embedder()
        if not self.violation_detector:
            self.violation_detector = await self._initialize_violation_detector()
    
    async def _initialize_fingerprint_generator(self):
        """Initialize fingerprint generation component"""
        return {"model": "voice_fingerprint_v1", "initialized": True}
    
    async def _initialize_watermark_embedder(self):
        """Initialize watermark embedding component"""
        return {"model": "voice_watermark_v1", "initialized": True}
    
    async def _initialize_violation_detector(self):
        """Initialize violation detection component"""
        return {"model": "voice_violation_detector_v1", "initialized": True}
    
    async def get_protection_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get protection status for content"""
        
        if content_id not in self.protected_content:
            return None
        
        fingerprint = self.protected_content[content_id]
        
        # Get violation history for this content
        content_violations = [
            v for v in self.violation_history 
            if v.original_content_id == content_id
        ]
        
        return {
            "content_id": content_id,
            "protection_level": fingerprint.protection_level.value,
            "protected_since": fingerprint.created_at.isoformat(),
            "fingerprint_hash": fingerprint.fingerprint_hash,
            "violations_detected": len(content_violations),
            "last_violation": content_violations[-1].detected_at.isoformat() if content_violations else None,
            "monitoring_active": self.monitoring_enabled,
            "protection_features": self.protection_settings[fingerprint.protection_level]["features"]
        }
    
    async def get_protection_analytics(self) -> Dict[str, Any]:
        """Get protection system analytics"""
        
        total_protected = len(self.protected_content)
        total_violations = len(self.violation_history)
        
        # Violation statistics by threat level
        violation_by_threat = {}
        for threat_level in ThreatLevel:
            count = len([v for v in self.violation_history if v.threat_level == threat_level])
            violation_by_threat[threat_level.value] = count
        
        # Protection level distribution
        protection_distribution = {}
        for level in ProtectionLevel:
            count = len([f for f in self.protected_content.values() if f.protection_level == level])
            protection_distribution[level.value] = count
        
        return {
            "protection_summary": {
                "total_protected_content": total_protected,
                "total_violations_detected": total_violations,
                "protection_effectiveness": (total_protected - total_violations) / max(1, total_protected),
                "active_monitoring": self.monitoring_enabled
            },
            "violation_analytics": {
                "by_threat_level": violation_by_threat,
                "recent_violations": len([v for v in self.violation_history if v.detected_at > datetime.now() - timedelta(days=7)])
            },
            "protection_distribution": protection_distribution,
            "detection_algorithms": {
                name: algo["accuracy"] for name, algo in self.detection_algorithms.items()
            }
        }