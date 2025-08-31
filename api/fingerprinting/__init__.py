"""IA Influencer Agent - Fingerprinting Module
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- ML Engineer: Advanced AI/ML Systems & Computer Vision  
- Database Administrator: Enterprise PostgreSQL & Vector DB
- Security Expert: Cybersecurity & Digital Rights Protection
- Microservices Architect: Scalable Enterprise Architecture
- Audio Engineer: Advanced Audio Processing & Analysis
- DevOps Engineer: Kubernetes & Cloud Infrastructure
- AI Prompt Engineer: Large Language Models & NLP Systems

Contact: mlaiel@live.de

Advanced content fingerprinting and protection system for multi-format content
"""# Core fingerprinting processors
from .audio_processor import AudioFingerprintProcessor, AudioFingerprint
from .video_processor import VideoFingerprintProcessor, VideoFingerprint
from .image_processor import ImageFingerprintProcessor, ImageFingerprint
from .text_processor import TextFingerprintProcessor, TextFingerprint

# Database and storage
from .database_manager import DatabaseManager

# Main protection service
from .protection_service import ContentProtectionService

# Configuration and utilities
from .config_manager import FingerprintConfig, get_global_config
from .performance_monitor import get_global_metrics, get_global_monitor
from .fingerprint_utils import (
    FingerprintUtils, FileTypeDetector, DataValidator,
    hash_content, get_file_type, calculate_similarity
)

# Legacy modules (maintained for backward compatibility)
from .engines import FingerprintEngine
from .monitoring import FingerprintMonitor
from .vector_matching import VectorMatcher

__all__ = [
    # New advanced processors
    'AudioFingerprintProcessor',
    'AudioFingerprint',
    'VideoFingerprintProcessor', 
    'VideoFingerprint',
    'ImageFingerprintProcessor',
    'ImageFingerprint',
    'TextFingerprintProcessor',
    'TextFingerprint',
    'DatabaseManager',
    'ContentProtectionService',
    
    # Storage and indexing
    'EnterpriseStorageService',
    'StorageProvider',
    'S3StorageProvider',
    'LocalStorageProvider',
    'IndexManager',
    'StorageConfig',
    'StoredFile',
    'FileIndex',
    'FileType',
    'StorageType',
    'get_storage_service',
    
    # Configuration and utilities
    'FingerprintConfig',
    'get_global_config',
    'get_global_metrics',
    'get_global_monitor',
    'FingerprintUtils',
    'FileTypeDetector',
    'DataValidator',
    'hash_content',
    'get_file_type',
    'calculate_similarity',
    
    # Legacy compatibility
    'FingerprintEngine',
    'FingerprintMonitor',
    'VectorMatcher'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Quick access factory functions
def create_protection_service(config=None):
    """
    Factory function to create a content protection service
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ContentProtectionService instance
    """
    return ContentProtectionService(config)

def create_audio_processor(config=None):
    """Create an audio fingerprint processor"""
    return AudioFingerprintProcessor(config)

def create_video_processor(config=None):
    """Create a video fingerprint processor"""
    return VideoFingerprintProcessor(config)

def create_image_processor(config=None):
    """Create an image fingerprint processor"""
    return ImageFingerprintProcessor(config)

def create_text_processor(config=None):
    """Create a text fingerprint processor"""
    return TextFingerprintProcessor(config)

def create_database_manager(config=None):
    """Create a database manager"""
    return DatabaseManager(config)
    ContentType
)

# Vector matching and similarity imports
from .vector_matching import (
    VectorMatcher,
    AdvancedVectorMatcher,
    IndexManager,
    VectorMatchConfig,
    MatchResult,
    SimilarityCalculator
)

# Monitoring and protection imports
from .monitoring import (
    ProtectionMonitor,
    ContentScanner,
    AlertManager,
    ViolationAlert,
    AlertSeverity,
    AlertStatus,
    PlatformType,
    MonitoringConfig
)

# Processor imports
from .processors import (
    AudioProcessor,
    VideoProcessor,
    ImageProcessor,
    TextProcessor,
    ProcessorConfig,
    ProcessingResult
)

# Similarity matching imports  
from .similarity import (
    SimilarityMatcher,
    CrossModalAnalyzer,
    SimilarityAlgorithms,
    MatchingStrategy,
    SimilarityConfig
)

# Storage and indexing imports
from .storage import (
    EnterpriseStorageService,
    StorageProvider,
    S3StorageProvider,
    LocalStorageProvider,
    IndexManager,
    StorageConfig,
    StoredFile,
    FileIndex,
    FileType,
    StorageType,
    get_storage_service
)

# Configuration and schemas
from .config import (
    FingerprintingSettings,
    DatabaseSettings,
    ProcessingSettings,
    MonitoringSettings
)

from .schemas import (
    FingerprintRequest,
    FingerprintResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    MonitoringRequest,
    MonitoringResponse,
    ContentAnalysisRequest,
    ContentAnalysisResponse
)

# Utility functions
from .utils import (
    FeatureExtractor,
    ContentValidator,
    FormatConverter,
    MetadataExtractor,
    QualityAssessment
)
from transformers import CLIPProcessor, CLIPModel

# Video processing imports
import ffmpeg

# Text processing imports
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch

from ..core.exceptions import FingerprintException, ProcessingException


class FingerprintType(Enum):
    """Fingerprint algorithm types."""
    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    MFCC_HASH = "mfcc_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    FEATURE_HASH = "feature_hash"
    CLIP_EMBEDDING = "clip_embedding"
    SEMANTIC_HASH = "semantic_hash"
    STRUCTURAL_HASH = "structural_hash"
    BERT_EMBEDDING = "bert_embedding"


class ProcessingQuality(Enum):
    """Content processing quality levels."""
    FAST = "fast"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class FingerprintResult:
    """Fingerprint generation result."""
    fingerprint_id: str
    content_id: str
    fingerprint_type: FingerprintType
    hash_value: str
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class AudioFingerprintEngine:
    """
    Advanced audio fingerprinting engine supporting multiple algorithms.
    
    Provides high-precision audio fingerprinting using:
    - Chromaprint for acoustic fingerprinting
    - Spectral hashing for frequency domain analysis
    - MFCC (Mel-frequency cepstral coefficients) for timbral analysis
    - Custom neural fingerprinting models
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("fingerprint.audio")
        
        # Audio processing settings
        self.sample_rate = self.config.get("sample_rate", 44100)
        self.chunk_duration = self.config.get("chunk_duration", 30.0)  # seconds
        self.overlap_ratio = self.config.get("overlap_ratio", 0.5)
        self.quality = ProcessingQuality(self.config.get("quality", "standard"))
        
        # Initialize engines
        self._initialize_audio_engines()
        
        self.logger.info("AudioFingerprintEngine initialized successfully")
    
    def _initialize_audio_engines(self):
        """Initialize audio processing engines."""
        try:
            # Chromaprint fingerprinter
            self.chromaprint = Chromaprint()
            
            # Essentia algorithms for advanced audio analysis
            self.windowing = es.Windowing(type='hann')
            self.spectrum = es.Spectrum()
            self.mfcc = es.MFCC(numberCoefficients=13)
            self.spectral_peaks = es.SpectralPeaks()
            self.spectral_whitening = es.SpectralWhitening()
            
            # Neural fingerprinting model (placeholder for custom model)
            self.neural_model = None  # Would load trained model in production
            
            self.logger.info("Audio engines initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio engines: {e}")
            raise FingerprintException(f"Audio engine initialization failed: {e}")
    
    async def generate_fingerprint(
        self,
        audio_path: Union[str, Path, BinaryIO],
        fingerprint_types: List[FingerprintType] = None
    ) -> Dict[str, FingerprintResult]:
        """
        Generate comprehensive audio fingerprints.
        
        Creates multiple types of fingerprints for robust content identification
        and matching across different audio processing scenarios.
        """
        start_time = datetime.utcnow()
        
        if fingerprint_types is None:
            fingerprint_types = [
                FingerprintType.CHROMAPRINT,
                FingerprintType.SPECTRAL_HASH,
                FingerprintType.MFCC_HASH
            ]
        
        self.logger.info(f"Generating audio fingerprints: {len(fingerprint_types)} types")
        
        try:
            # Load audio data
            audio_data, sr = await self._load_audio_data(audio_path)
            content_id = self._generate_content_id(audio_path)
            
            fingerprint_results = {}
            
            # Generate each requested fingerprint type
            for fp_type in fingerprint_types:
                try:
                    if fp_type == FingerprintType.CHROMAPRINT:
                        result = await self._generate_chromaprint(audio_data, sr, content_id)
                    elif fp_type == FingerprintType.SPECTRAL_HASH:
                        result = await self._generate_spectral_hash(audio_data, sr, content_id)
                    elif fp_type == FingerprintType.MFCC_HASH:
                        result = await self._generate_mfcc_hash(audio_data, sr, content_id)
                    else:
                        self.logger.warning(f"Unsupported fingerprint type: {fp_type}")
                        continue
                    
                    fingerprint_results[fp_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate {fp_type.value} fingerprint: {e}")
                    continue
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Audio fingerprinting completed in {processing_time:.2f}s")
            
            return fingerprint_results
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint generation failed: {e}")
            raise FingerprintException(f"Audio fingerprinting error: {e}")
    
    async def _load_audio_data(
        self,
        audio_path: Union[str, Path, BinaryIO]
    ) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio data."""
        try:
            # Load audio using librosa with appropriate settings
            audio_data, sr = librosa.load(
                audio_path,
                sr=self.sample_rate,
                duration=None,  # Load full file
                mono=True,
                dtype=np.float32
            )
            
            # Normalize audio
            audio_data = librosa.util.normalize(audio_data)
            
            return audio_data, sr
            
        except Exception as e:
            self.logger.error(f"Audio loading failed: {e}")
            raise ProcessingException(f"Audio loading error: {e}")
    
    async def _generate_chromaprint(
        self,
        audio_data: np.ndarray,
        sr: int,
        content_id: str
    ) -> FingerprintResult:
        """Generate Chromaprint acoustic fingerprint."""
        start_time = datetime.utcnow()
        
        try:
            # Convert to format expected by Chromaprint
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Generate fingerprint
            fingerprint = self.chromaprint.fingerprint(audio_int16.tobytes(), sr)
            
            # Create hash
            hash_value = hashlib.sha256(fingerprint.encode()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"chromaprint_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.CHROMAPRINT,
                hash_value=hash_value,
                confidence_score=0.95,  # Chromaprint is highly reliable
                processing_time=processing_time,
                metadata={
                    "algorithm": "chromaprint",
                    "sample_rate": sr,
                    "duration": len(audio_data) / sr,
                    "raw_fingerprint": fingerprint[:100]  # Store truncated version
                }
            )
            
        except Exception as e:
            self.logger.error(f"Chromaprint generation failed: {e}")
            raise FingerprintException(f"Chromaprint error: {e}")
    
    async def _generate_spectral_hash(
        self,
        audio_data: np.ndarray,
        sr: int,
        content_id: str
    ) -> FingerprintResult:
        """Generate spectral hash using frequency domain analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Compute short-time Fourier transform
            stft = librosa.stft(
                audio_data,
                hop_length=512,
                n_fft=2048,
                window='hann'
            )
            
            # Compute spectral centroid, rolloff, and other features
            spectral_centroids = librosa.feature.spectral_centroid(S=np.abs(stft), sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=np.abs(stft), sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(S=np.abs(stft), sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Create feature vector
            features = np.concatenate([
                spectral_centroids,
                spectral_rolloff,
                spectral_bandwidth,
                zero_crossing_rate
            ])
            
            # Quantize features to create hash
            quantized_features = np.round(features * 1000).astype(np.int32)
            hash_input = quantized_features.tobytes()
            hash_value = hashlib.sha256(hash_input).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"spectral_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.SPECTRAL_HASH,
                hash_value=hash_value,
                confidence_score=0.88,
                processing_time=processing_time,
                metadata={
                    "algorithm": "spectral_features",
                    "feature_count": len(features),
                    "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                    "spectral_rolloff_mean": float(np.mean(spectral_rolloff))
                }
            )
            
        except Exception as e:
            self.logger.error(f"Spectral hash generation failed: {e}")
            raise FingerprintException(f"Spectral hash error: {e}")
    
    async def _generate_mfcc_hash(
        self,
        audio_data: np.ndarray,
        sr: int,
        content_id: str
    ) -> FingerprintResult:
        """Generate MFCC-based fingerprint for timbral analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Compute MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_data,
                sr=sr,
                n_mfcc=13,
                hop_length=512,
                n_fft=2048
            )
            
            # Compute delta and delta-delta features
            mfcc_delta = librosa.feature.delta(mfccs)
            mfcc_delta2 = librosa.feature.delta(mfccs, order=2)
            
            # Combine all MFCC features
            combined_mfcc = np.vstack([mfccs, mfcc_delta, mfcc_delta2])
            
            # Compute statistical moments
            mfcc_mean = np.mean(combined_mfcc, axis=1)
            mfcc_std = np.std(combined_mfcc, axis=1)
            
            # Create feature vector
            feature_vector = np.concatenate([mfcc_mean, mfcc_std])
            
            # Generate hash
            quantized_features = np.round(feature_vector * 10000).astype(np.int32)
            hash_input = quantized_features.tobytes()
            hash_value = hashlib.sha256(hash_input).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"mfcc_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.MFCC_HASH,
                hash_value=hash_value,
                confidence_score=0.85,
                processing_time=processing_time,
                metadata={
                    "algorithm": "mfcc_statistical",
                    "n_mfcc": 13,
                    "feature_dimensions": len(feature_vector),
                    "mfcc_mean_first": float(mfcc_mean[0]),
                    "temporal_frames": combined_mfcc.shape[1]
                }
            )
            
        except Exception as e:
            self.logger.error(f"MFCC hash generation failed: {e}")
            raise FingerprintException(f"MFCC hash error: {e}")
    
    def _generate_content_id(self, content_path: Union[str, Path, BinaryIO]) -> str:
        """Generate unique content identifier."""
        if hasattr(content_path, 'read'):
            # For file-like objects, generate ID from current position
            return f"audio_{uuid.uuid4().hex[:12]}"
        else:
            # For file paths, use path-based ID
            path_str = str(content_path)
            return hashlib.md5(path_str.encode()).hexdigest()[:12]
    
    async def apply_watermark(
        self,
        audio_path: Union[str, Path],
        watermark_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply digital watermark to audio content."""
        try:
            # Load audio
            audio_data, sr = await self._load_audio_data(audio_path)
            
            # Generate watermark signal (simplified implementation)
            watermark_signal = self._generate_watermark_signal(
                watermark_data,
                len(audio_data),
                sr
            )
            
            # Embed watermark (additive with low amplitude)
            watermarked_audio = audio_data + (watermark_signal * 0.001)
            
            # Ensure no clipping
            watermarked_audio = np.clip(watermarked_audio, -1.0, 1.0)
            
            # Save watermarked audio (placeholder - would save to output path)
            output_path = f"watermarked_{Path(audio_path).stem}.wav"
            
            return {
                "success": True,
                "output_path": output_path,
                "watermark_strength": 0.001,
                "watermark_data": watermark_data
            }
            
        except Exception as e:
            self.logger.error(f"Audio watermarking failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_watermark_signal(
        self,
        watermark_data: Dict[str, Any],
        signal_length: int,
        sr: int
    ) -> np.ndarray:
        """Generate watermark signal from data."""
        # Convert watermark data to binary
        data_str = json.dumps(watermark_data, sort_keys=True)
        data_bytes = data_str.encode('utf-8')
        data_bits = ''.join(format(byte, '08b') for byte in data_bytes)
        
        # Generate pseudorandom signal based on data
        np.random.seed(hash(data_str) % (2**32))
        watermark_signal = np.random.normal(0, 1, signal_length)
        
        return watermark_signal.astype(np.float32)


class ImageFingerprintEngine:
    """
    Advanced image fingerprinting engine with multiple algorithms.
    
    Provides high-precision image fingerprinting using:
    - Perceptual hashing (pHash, dHash, aHash)
    - Feature-based hashing (ORB, SIFT)
    - Deep learning embeddings (CLIP)
    - Custom neural fingerprinting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("fingerprint.image")
        
        # Image processing settings
        self.resize_dimensions = tuple(self.config.get("resize_dimensions", (256, 256)))
        self.quality = ProcessingQuality(self.config.get("quality", "standard"))
        
        # Initialize engines
        self._initialize_image_engines()
        
        self.logger.info("ImageFingerprintEngine initialized successfully")
    
    def _initialize_image_engines(self):
        """Initialize image processing engines."""
        try:
            # OpenCV feature detectors
            self.orb = cv2.ORB_create(nfeatures=500)
            self.sift = cv2.SIFT_create(nfeatures=500)
            
            # CLIP model for semantic embeddings
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            self.logger.info("Image engines initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize image engines: {e}")
            raise FingerprintException(f"Image engine initialization failed: {e}")
    
    async def generate_fingerprint(
        self,
        image_path: Union[str, Path, BinaryIO],
        fingerprint_types: List[FingerprintType] = None
    ) -> Dict[str, FingerprintResult]:
        """Generate comprehensive image fingerprints."""
        start_time = datetime.utcnow()
        
        if fingerprint_types is None:
            fingerprint_types = [
                FingerprintType.PERCEPTUAL_HASH,
                FingerprintType.FEATURE_HASH,
                FingerprintType.CLIP_EMBEDDING
            ]
        
        self.logger.info(f"Generating image fingerprints: {len(fingerprint_types)} types")
        
        try:
            # Load image data
            image_data = await self._load_image_data(image_path)
            content_id = self._generate_content_id(image_path)
            
            fingerprint_results = {}
            
            # Generate each requested fingerprint type
            for fp_type in fingerprint_types:
                try:
                    if fp_type == FingerprintType.PERCEPTUAL_HASH:
                        result = await self._generate_perceptual_hash(image_data, content_id)
                    elif fp_type == FingerprintType.FEATURE_HASH:
                        result = await self._generate_feature_hash(image_data, content_id)
                    elif fp_type == FingerprintType.CLIP_EMBEDDING:
                        result = await self._generate_clip_embedding(image_data, content_id)
                    else:
                        self.logger.warning(f"Unsupported fingerprint type: {fp_type}")
                        continue
                    
                    fingerprint_results[fp_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate {fp_type.value} fingerprint: {e}")
                    continue
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Image fingerprinting completed in {processing_time:.2f}s")
            
            return fingerprint_results
            
        except Exception as e:
            self.logger.error(f"Image fingerprint generation failed: {e}")
            raise FingerprintException(f"Image fingerprinting error: {e}")
    
    async def _load_image_data(self, image_path: Union[str, Path, BinaryIO]) -> np.ndarray:
        """Load and preprocess image data."""
        try:
            if hasattr(image_path, 'read'):
                # Handle file-like objects
                image_data = np.frombuffer(image_path.read(), np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            else:
                # Handle file paths
                image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            
            if image is None:
                raise ProcessingException("Failed to load image")
            
            # Convert BGR to RGB for consistency
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Image loading failed: {e}")
            raise ProcessingException(f"Image loading error: {e}")
    
    async def _generate_perceptual_hash(
        self,
        image_data: np.ndarray,
        content_id: str
    ) -> FingerprintResult:
        """Generate perceptual hash using multiple algorithms."""
        start_time = datetime.utcnow()
        
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image_data)
            
            # Generate multiple perceptual hashes
            phash = imagehash.phash(pil_image, hash_size=16)
            dhash = imagehash.dhash(pil_image, hash_size=16)
            ahash = imagehash.average_hash(pil_image, hash_size=16)
            whash = imagehash.whash(pil_image, hash_size=16)
            
            # Combine hashes
            combined_hash = str(phash) + str(dhash) + str(ahash) + str(whash)
            hash_value = hashlib.sha256(combined_hash.encode()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"perceptual_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                hash_value=hash_value,
                confidence_score=0.92,
                processing_time=processing_time,
                metadata={
                    "algorithm": "combined_perceptual_hash",
                    "phash": str(phash),
                    "dhash": str(dhash),
                    "ahash": str(ahash),
                    "whash": str(whash),
                    "image_dimensions": image_data.shape[:2]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Perceptual hash generation failed: {e}")
            raise FingerprintException(f"Perceptual hash error: {e}")
    
    async def _generate_feature_hash(
        self,
        image_data: np.ndarray,
        content_id: str
    ) -> FingerprintResult:
        """Generate feature-based hash using ORB/SIFT descriptors."""
        start_time = datetime.utcnow()
        
        try:
            # Convert to grayscale for feature detection
            gray_image = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            
            # Detect ORB features
            keypoints_orb, descriptors_orb = self.orb.detectAndCompute(gray_image, None)
            
            # Detect SIFT features (if available)
            try:
                keypoints_sift, descriptors_sift = self.sift.detectAndCompute(gray_image, None)
            except:
                keypoints_sift, descriptors_sift = [], None
            
            # Create feature hash from descriptors
            feature_data = []
            
            if descriptors_orb is not None:
                # Use statistical properties of ORB descriptors
                orb_mean = np.mean(descriptors_orb, axis=0)
                orb_std = np.std(descriptors_orb, axis=0)
                feature_data.extend(orb_mean.tolist())
                feature_data.extend(orb_std.tolist())
            
            if descriptors_sift is not None:
                # Use statistical properties of SIFT descriptors
                sift_mean = np.mean(descriptors_sift, axis=0)
                feature_data.extend(sift_mean.tolist())
            
            # Generate hash from features
            if feature_data:
                feature_array = np.array(feature_data, dtype=np.float32)
                quantized_features = np.round(feature_array * 1000).astype(np.int32)
                hash_input = quantized_features.tobytes()
                hash_value = hashlib.sha256(hash_input).hexdigest()
                confidence = 0.88
            else:
                # Fallback to simple image statistics
                hash_value = hashlib.sha256(gray_image.tobytes()).hexdigest()
                confidence = 0.5
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"feature_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                confidence_score=confidence,
                processing_time=processing_time,
                metadata={
                    "algorithm": "orb_sift_features",
                    "orb_keypoints": len(keypoints_orb),
                    "sift_keypoints": len(keypoints_sift),
                    "feature_count": len(feature_data),
                    "image_size": gray_image.shape
                }
            )
            
        except Exception as e:
            self.logger.error(f"Feature hash generation failed: {e}")
            raise FingerprintException(f"Feature hash error: {e}")
    
    async def _generate_clip_embedding(
        self,
        image_data: np.ndarray,
        content_id: str
    ) -> FingerprintResult:
        """Generate CLIP-based semantic embedding."""
        start_time = datetime.utcnow()
        
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image_data)
            
            # Process image with CLIP
            inputs = self.clip_processor(images=pil_image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            # Convert to numpy and normalize
            embedding = image_features.numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)
            
            # Quantize embedding for hashing
            quantized_embedding = np.round(embedding * 10000).astype(np.int32)
            hash_value = hashlib.sha256(quantized_embedding.tobytes()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"clip_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.CLIP_EMBEDDING,
                hash_value=hash_value,
                confidence_score=0.94,
                processing_time=processing_time,
                metadata={
                    "algorithm": "clip_vit_base",
                    "embedding_dimension": len(embedding),
                    "embedding_norm": float(np.linalg.norm(embedding)),
                    "model_name": "openai/clip-vit-base-patch32"
                }
            )
            
        except Exception as e:
            self.logger.error(f"CLIP embedding generation failed: {e}")
            raise FingerprintException(f"CLIP embedding error: {e}")
    
    def _generate_content_id(self, image_path: Union[str, Path, BinaryIO]) -> str:
        """Generate unique content identifier."""
        if hasattr(image_path, 'read'):
            return f"image_{uuid.uuid4().hex[:12]}"
        else:
            path_str = str(image_path)
            return hashlib.md5(path_str.encode()).hexdigest()[:12]
    
    async def apply_watermark(
        self,
        image_path: Union[str, Path],
        watermark_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply digital watermark to image content."""
        try:
            # Load image
            image_data = await self._load_image_data(image_path)
            
            # Generate watermark pattern
            watermark_pattern = self._generate_watermark_pattern(
                watermark_data,
                image_data.shape[:2]
            )
            
            # Apply watermark in frequency domain (DCT)
            watermarked_image = self._embed_frequency_watermark(
                image_data,
                watermark_pattern
            )
            
            output_path = f"watermarked_{Path(image_path).stem}.png"
            
            return {
                "success": True,
                "output_path": output_path,
                "watermark_strength": 0.1,
                "watermark_data": watermark_data
            }
            
        except Exception as e:
            self.logger.error(f"Image watermarking failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_watermark_pattern(
        self,
        watermark_data: Dict[str, Any],
        image_shape: Tuple[int, int]
    ) -> np.ndarray:
        """Generate watermark pattern for image."""
        data_str = json.dumps(watermark_data, sort_keys=True)
        np.random.seed(hash(data_str) % (2**32))
        
        # Generate pseudorandom pattern
        pattern = np.random.normal(0, 1, image_shape).astype(np.float32)
        return pattern
    
    def _embed_frequency_watermark(
        self,
        image: np.ndarray,
        watermark: np.ndarray
    ) -> np.ndarray:
        """Embed watermark in frequency domain."""
        # Convert to float
        image_float = image.astype(np.float32) / 255.0
        
        # Apply DCT to each channel
        watermarked = image_float.copy()
        
        for channel in range(image_float.shape[2]):
            # DCT transform
            dct_coeffs = cv2.dct(image_float[:, :, channel])
            
            # Embed watermark in mid-frequency coefficients
            dct_coeffs += watermark * 0.01
            
            # Inverse DCT
            watermarked[:, :, channel] = cv2.idct(dct_coeffs)
        
        # Convert back to uint8
        watermarked = np.clip(watermarked * 255, 0, 255).astype(np.uint8)
        
        return watermarked


class TextFingerprintEngine:
    """
    Advanced text fingerprinting engine with semantic analysis.
    
    Provides high-precision text fingerprinting using:
    - Semantic embeddings (BERT, RoBERTa, Sentence Transformers)
    - Structural analysis (syntax trees, n-grams)
    - Stylometric features (writing style analysis)
    - Custom neural text fingerprinting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("fingerprint.text")
        
        # Text processing settings
        self.max_length = self.config.get("max_length", 512)
        self.chunk_size = self.config.get("chunk_size", 200)
        self.overlap_size = self.config.get("overlap_size", 50)
        
        # Initialize engines
        self._initialize_text_engines()
        
        self.logger.info("TextFingerprintEngine initialized successfully")
    
    def _initialize_text_engines(self):
        """Initialize text processing engines."""
        try:
            # Sentence transformer for semantic embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # BERT model for contextual embeddings
            self.bert_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = AutoModel.from_pretrained('bert-base-uncased')
            
            self.logger.info("Text engines initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text engines: {e}")
            raise FingerprintException(f"Text engine initialization failed: {e}")
    
    async def generate_fingerprint(
        self,
        text_content: Union[str, Path, BinaryIO],
        fingerprint_types: List[FingerprintType] = None
    ) -> Dict[str, FingerprintResult]:
        """Generate comprehensive text fingerprints."""
        start_time = datetime.utcnow()
        
        if fingerprint_types is None:
            fingerprint_types = [
                FingerprintType.SEMANTIC_HASH,
                FingerprintType.STRUCTURAL_HASH,
                FingerprintType.BERT_EMBEDDING
            ]
        
        self.logger.info(f"Generating text fingerprints: {len(fingerprint_types)} types")
        
        try:
            # Load text data
            text_data = await self._load_text_data(text_content)
            content_id = self._generate_content_id(text_content)
            
            fingerprint_results = {}
            
            # Generate each requested fingerprint type
            for fp_type in fingerprint_types:
                try:
                    if fp_type == FingerprintType.SEMANTIC_HASH:
                        result = await self._generate_semantic_hash(text_data, content_id)
                    elif fp_type == FingerprintType.STRUCTURAL_HASH:
                        result = await self._generate_structural_hash(text_data, content_id)
                    elif fp_type == FingerprintType.BERT_EMBEDDING:
                        result = await self._generate_bert_embedding(text_data, content_id)
                    else:
                        self.logger.warning(f"Unsupported fingerprint type: {fp_type}")
                        continue
                    
                    fingerprint_results[fp_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate {fp_type.value} fingerprint: {e}")
                    continue
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Text fingerprinting completed in {processing_time:.2f}s")
            
            return fingerprint_results
            
        except Exception as e:
            self.logger.error(f"Text fingerprint generation failed: {e}")
            raise FingerprintException(f"Text fingerprinting error: {e}")
    
    async def _load_text_data(self, text_content: Union[str, Path, BinaryIO]) -> str:
        """Load and preprocess text data."""
        try:
            if isinstance(text_content, str):
                if len(text_content) < 1000:  # Likely a file path
                    try:
                        with open(text_content, 'r', encoding='utf-8') as f:
                            text_data = f.read()
                    except:
                        # If file reading fails, treat as content
                        text_data = text_content
                else:
                    text_data = text_content
            elif hasattr(text_content, 'read'):
                text_data = text_content.read()
                if isinstance(text_data, bytes):
                    text_data = text_data.decode('utf-8')
            else:
                with open(text_content, 'r', encoding='utf-8') as f:
                    text_data = f.read()
            
            # Basic text cleaning
            text_data = text_data.strip()
            
            return text_data
            
        except Exception as e:
            self.logger.error(f"Text loading failed: {e}")
            raise ProcessingException(f"Text loading error: {e}")
    
    async def _generate_semantic_hash(
        self,
        text_data: str,
        content_id: str
    ) -> FingerprintResult:
        """Generate semantic hash using sentence embeddings."""
        start_time = datetime.utcnow()
        
        try:
            # Split text into chunks for processing
            chunks = self._split_text_into_chunks(text_data)
            
            # Generate embeddings for each chunk
            chunk_embeddings = []
            for chunk in chunks:
                embedding = self.sentence_model.encode([chunk])[0]
                chunk_embeddings.append(embedding)
            
            # Aggregate embeddings (mean pooling)
            if chunk_embeddings:
                aggregated_embedding = np.mean(chunk_embeddings, axis=0)
            else:
                # Fallback for empty or very short text
                aggregated_embedding = self.sentence_model.encode([text_data[:100]])[0]
            
            # Normalize embedding
            aggregated_embedding = aggregated_embedding / np.linalg.norm(aggregated_embedding)
            
            # Generate hash from embedding
            quantized_embedding = np.round(aggregated_embedding * 10000).astype(np.int32)
            hash_value = hashlib.sha256(quantized_embedding.tobytes()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"semantic_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.SEMANTIC_HASH,
                hash_value=hash_value,
                confidence_score=0.90,
                processing_time=processing_time,
                metadata={
                    "algorithm": "sentence_transformer",
                    "model_name": "all-MiniLM-L6-v2",
                    "text_length": len(text_data),
                    "chunks_processed": len(chunks),
                    "embedding_dimension": len(aggregated_embedding),
                    "embedding_norm": float(np.linalg.norm(aggregated_embedding))
                }
            )
            
        except Exception as e:
            self.logger.error(f"Semantic hash generation failed: {e}")
            raise FingerprintException(f"Semantic hash error: {e}")
    
    async def _generate_structural_hash(
        self,
        text_data: str,
        content_id: str
    ) -> FingerprintResult:
        """Generate structural hash using text analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Basic structural features
            word_count = len(text_data.split())
            char_count = len(text_data)
            sentence_count = len(text_data.split('.'))
            paragraph_count = len(text_data.split('\n\n'))
            
            # Character frequency analysis
            char_freq = {}
            for char in text_data.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # N-gram analysis (trigrams)
            trigrams = []
            words = text_data.lower().split()
            for i in range(len(words) - 2):
                trigram = ' '.join(words[i:i+3])
                trigrams.append(trigram)
            
            trigram_freq = {}
            for trigram in trigrams:
                trigram_freq[trigram] = trigram_freq.get(trigram, 0) + 1
            
            # Create structural feature vector
            structural_features = [
                word_count, char_count, sentence_count, paragraph_count,
                len(char_freq), len(trigram_freq)
            ]
            
            # Add top character frequencies
            sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            for char, freq in sorted_chars:
                structural_features.append(freq)
            
            # Pad or truncate to fixed size
            structural_features = structural_features[:20]
            while len(structural_features) < 20:
                structural_features.append(0)
            
            # Generate hash
            feature_array = np.array(structural_features, dtype=np.float32)
            quantized_features = np.round(feature_array).astype(np.int32)
            hash_value = hashlib.sha256(quantized_features.tobytes()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"structural_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.STRUCTURAL_HASH,
                hash_value=hash_value,
                confidence_score=0.82,
                processing_time=processing_time,
                metadata={
                    "algorithm": "structural_analysis",
                    "word_count": word_count,
                    "char_count": char_count,
                    "sentence_count": sentence_count,
                    "unique_trigrams": len(trigram_freq),
                    "feature_count": len(structural_features)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Structural hash generation failed: {e}")
            raise FingerprintException(f"Structural hash error: {e}")
    
    async def _generate_bert_embedding(
        self,
        text_data: str,
        content_id: str
    ) -> FingerprintResult:
        """Generate BERT-based contextual embedding."""
        start_time = datetime.utcnow()
        
        try:
            # Truncate text to model's maximum length
            truncated_text = text_data[:self.max_length * 4]  # Rough character limit
            
            # Tokenize text
            inputs = self.bert_tokenizer(
                truncated_text,
                return_tensors='pt',
                max_length=self.max_length,
                truncation=True,
                padding=True
            )
            
            # Generate BERT embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                
                # Use pooled output (CLS token)
                pooled_output = outputs.pooler_output
                
                # Convert to numpy
                embedding = pooled_output.numpy().flatten()
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            # Generate hash
            quantized_embedding = np.round(embedding * 10000).astype(np.int32)
            hash_value = hashlib.sha256(quantized_embedding.tobytes()).hexdigest()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_id=f"bert_{uuid.uuid4().hex[:8]}",
                content_id=content_id,
                fingerprint_type=FingerprintType.BERT_EMBEDDING,
                hash_value=hash_value,
                confidence_score=0.93,
                processing_time=processing_time,
                metadata={
                    "algorithm": "bert_base_uncased",
                    "text_length": len(text_data),
                    "truncated_length": len(truncated_text),
                    "embedding_dimension": len(embedding),
                    "token_count": len(inputs['input_ids'][0]),
                    "embedding_norm": float(np.linalg.norm(embedding))
                }
            )
            
        except Exception as e:
            self.logger.error(f"BERT embedding generation failed: {e}")
            raise FingerprintException(f"BERT embedding error: {e}")
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks for processing."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap_size):
            chunk_words = words[i:i + self.chunk_size]
            if chunk_words:  # Only add non-empty chunks
                chunks.append(' '.join(chunk_words))
        
        return chunks if chunks else [text]  # Return original if no chunks
    
    def _generate_content_id(self, text_content: Union[str, Path, BinaryIO]) -> str:
        """Generate unique content identifier."""
        if isinstance(text_content, str) and len(text_content) > 1000:
            # For large strings (content), use hash of first 1000 chars
            return hashlib.md5(text_content[:1000].encode()).hexdigest()[:12]
        elif hasattr(text_content, 'read'):
            return f"text_{uuid.uuid4().hex[:12]}"
        else:
            path_str = str(text_content)
            return hashlib.md5(path_str.encode()).hexdigest()[:12]
