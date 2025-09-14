"""
Enterprise Audio Processing Engine for MLOps
Audio Engineer + Lead Dev IA implementation with advanced audio ML pipelines
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
from pathlib import Path
import warnings

# Optional audio processing libraries
try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    warnings.warn("librosa not available. Advanced audio processing will be limited.")

try:
    import scipy.signal
    import scipy.fft
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available. Signal processing will be limited.")

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    warnings.warn("TensorFlow not available. Audio ML models will be limited.")

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"


class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"          # 128 kbps
    MEDIUM = "medium"    # 192 kbps
    HIGH = "high"        # 256 kbps
    LOSSLESS = "lossless"  # FLAC/WAV


class ProcessingType(Enum):
    """Types of audio processing"""
    FEATURE_EXTRACTION = "feature_extraction"
    ENHANCEMENT = "enhancement"
    TRANSCRIPTION = "transcription"
    SEPARATION = "separation"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    MASTERING = "mastering"
    MIXING = "mixing"


class GenreClassification(Enum):
    """Music genre classifications"""
    ELECTRONIC = "electronic"
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    HIP_HOP = "hip_hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    FOLK = "folk"
    UNKNOWN = "unknown"


@dataclass
class AudioMetadata:
    """Comprehensive audio metadata"""
    file_id: str
    filename: str
    format: AudioFormat
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int]
    file_size_bytes: int
    checksum: str
    created_at: datetime = field(default_factory=datetime.now)
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class AudioFeatures:
    """Extracted audio features"""
    feature_id: str
    file_id: str
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    
    # Temporal features
    tempo: Optional[float] = None
    beat_times: List[float] = field(default_factory=list)
    onset_times: List[float] = field(default_factory=list)
    
    # Spectral features
    mfcc: Optional[np.ndarray] = None
    chroma: Optional[np.ndarray] = None
    mel_spectrogram: Optional[np.ndarray] = None
    spectral_centroid: Optional[np.ndarray] = None
    spectral_rolloff: Optional[np.ndarray] = None
    zero_crossing_rate: Optional[np.ndarray] = None
    
    # Harmonic features
    harmonic: Optional[np.ndarray] = None
    percussive: Optional[np.ndarray] = None
    
    # High-level features
    energy: Optional[float] = None
    valence: Optional[float] = None
    danceability: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None
    
    # Custom features for creators
    emotional_intensity: Optional[float] = None
    commercial_potential: Optional[float] = None
    creativity_score: Optional[float] = None


@dataclass
class AudioProcessingJob:
    """Audio processing job configuration"""
    job_id: str
    file_id: str
    processing_type: ProcessingType
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    priority: int = 1  # 1-10, higher is more priority


class EnterpriseAudioEngine:
    """
    Enterprise Audio Processing Engine for MLOps
    Audio Engineer + Lead Dev IA comprehensive implementation
    """
    
    def __init__(
        self,
        workspace_path: str,
        model_cache_size: int = 5,
        max_concurrent_jobs: int = 4,
        enable_gpu_acceleration: bool = True
    ):
        """Initialize Enterprise Audio Engine
        
        Args:
            workspace_path: Path to audio workspace directory
            model_cache_size: Number of ML models to keep in cache
            max_concurrent_jobs: Maximum concurrent processing jobs
            enable_gpu_acceleration: Enable GPU acceleration if available
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        
        self.model_cache_size = model_cache_size
        self.max_concurrent_jobs = max_concurrent_jobs
        self.enable_gpu_acceleration = enable_gpu_acceleration
        
        # Audio storage
        self.audio_files: Dict[str, AudioMetadata] = {}
        self.audio_features: Dict[str, AudioFeatures] = {}
        self.processing_jobs: Dict[str, AudioProcessingJob] = {}
        
        # ML Models cache
        self.ml_models: Dict[str, Any] = {}
        self.model_load_times: Dict[str, datetime] = {}
        
        # Processing queue
        self.job_queue: asyncio.Queue = asyncio.Queue()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
        # Audio processing configurations
        self.default_sample_rate = 22050
        self.default_hop_length = 512
        self.default_n_fft = 2048
        
        # Creator-specific configurations
        self.creator_configs = {
            "musician": {
                "priority_features": ["tempo", "key", "energy", "valence", "danceability"],
                "quality_threshold": 0.9,
                "enhancement_presets": ["studio_master", "streaming_optimized"]
            },
            "podcast": {
                "priority_features": ["speechiness", "clarity", "noise_level"],
                "quality_threshold": 0.85,
                "enhancement_presets": ["voice_enhance", "noise_reduction"]
            },
            "content_creator": {
                "priority_features": ["energy", "commercial_potential", "emotional_intensity"],
                "quality_threshold": 0.8,
                "enhancement_presets": ["social_media", "broadcast_ready"]
            }
        }
        
        logger.info(f"Initialized Enterprise Audio Engine at {workspace_path}")
        
        # Initialize ML models
        asyncio.create_task(self._initialize_models())

    async def _initialize_models(self) -> None:
        """Initialize core ML models for audio processing"""
        try:
            if TF_AVAILABLE:
                # Load pre-trained models for audio analysis
                await self._load_genre_classifier()
                await self._load_mood_analyzer()
                await self._load_quality_assessor()
                await self._load_transcription_model()
            
            logger.info("Audio ML models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")

    async def _load_genre_classifier(self) -> None:
        """Load genre classification model"""
        try:
            # In production, would load actual pre-trained model
            self.ml_models["genre_classifier"] = {
                "model": "placeholder_genre_model",
                "classes": [genre.value for genre in GenreClassification],
                "loaded_at": datetime.now()
            }
            logger.info("Genre classifier loaded")
        except Exception as e:
            logger.error(f"Failed to load genre classifier: {e}")

    async def _load_mood_analyzer(self) -> None:
        """Load mood analysis model"""
        try:
            self.ml_models["mood_analyzer"] = {
                "model": "placeholder_mood_model",
                "dimensions": ["valence", "energy", "tension", "happiness"],
                "loaded_at": datetime.now()
            }
            logger.info("Mood analyzer loaded")
        except Exception as e:
            logger.error(f"Failed to load mood analyzer: {e}")

    async def _load_quality_assessor(self) -> None:
        """Load audio quality assessment model"""
        try:
            self.ml_models["quality_assessor"] = {
                "model": "placeholder_quality_model",
                "metrics": ["clarity", "loudness", "distortion", "noise_level"],
                "loaded_at": datetime.now()
            }
            logger.info("Quality assessor loaded")
        except Exception as e:
            logger.error(f"Failed to load quality assessor: {e}")

    async def _load_transcription_model(self) -> None:
        """Load speech-to-text transcription model"""
        try:
            self.ml_models["transcription"] = {
                "model": "placeholder_transcription_model",
                "languages": ["en", "fr", "es", "de"],
                "loaded_at": datetime.now()
            }
            logger.info("Transcription model loaded")
        except Exception as e:
            logger.error(f"Failed to load transcription model: {e}")

    async def upload_audio_file(
        self,
        file_data: bytes,
        filename: str,
        creator_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Upload and register audio file
        
        Args:
            file_data: Audio file binary data
            filename: Original filename
            creator_type: Type of creator (musician, podcast, etc.)
            metadata: Additional metadata
            
        Returns:
            File ID
        """
        try:
            file_id = str(uuid.uuid4())
            file_path = self.workspace_path / f"{file_id}_{filename}"
            
            # Save file to workspace
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Extract basic metadata
            if LIBROSA_AVAILABLE:
                try:
                    y, sr = librosa.load(file_path, sr=None)
                    duration = librosa.get_duration(y=y, sr=sr)
                    sample_rate = sr
                    channels = 1 if len(y.shape) == 1 else y.shape[0]
                except Exception as e:
                    logger.warning(f"Failed to extract audio metadata with librosa: {e}")
                    duration = 0.0
                    sample_rate = self.default_sample_rate
                    channels = 1
            else:
                duration = 0.0
                sample_rate = self.default_sample_rate
                channels = 1
            
            # Create checksum
            checksum = hashlib.md5(file_data).hexdigest()
            
            # Determine format from filename
            file_extension = Path(filename).suffix.lower().lstrip('.')
            try:
                audio_format = AudioFormat(file_extension)
            except ValueError:
                audio_format = AudioFormat.WAV  # Default
            
            # Create metadata object
            audio_metadata = AudioMetadata(
                file_id=file_id,
                filename=filename,
                format=audio_format,
                duration_seconds=duration,
                sample_rate=sample_rate,
                channels=channels,
                file_size_bytes=len(file_data),
                checksum=checksum
            )
            
            # Add additional metadata if provided
            if metadata:
                audio_metadata.artist = metadata.get("artist")
                audio_metadata.title = metadata.get("title")
                audio_metadata.album = metadata.get("album")
                audio_metadata.genre = metadata.get("genre")
                audio_metadata.tags = metadata.get("tags", [])
            
            # Add creator type tag
            if creator_type:
                audio_metadata.tags.append(f"creator_type:{creator_type}")
            
            self.audio_files[file_id] = audio_metadata
            
            # Automatically queue feature extraction
            await self.queue_feature_extraction(file_id)
            
            logger.info(f"Uploaded audio file: {filename} -> {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to upload audio file {filename}: {e}")
            raise

    async def queue_feature_extraction(self, file_id: str, priority: int = 5) -> str:
        """Queue feature extraction job
        
        Args:
            file_id: Audio file ID
            priority: Job priority (1-10)
            
        Returns:
            Job ID
        """
        try:
            job_id = str(uuid.uuid4())
            
            job = AudioProcessingJob(
                job_id=job_id,
                file_id=file_id,
                processing_type=ProcessingType.FEATURE_EXTRACTION,
                parameters={
                    "extract_mfcc": True,
                    "extract_chroma": True,
                    "extract_mel": True,
                    "extract_tempo": True,
                    "extract_beats": True,
                    "extract_onsets": True,
                    "extract_spectral": True,
                    "extract_harmonic": True,
                    "extract_high_level": True
                },
                priority=priority
            )
            
            self.processing_jobs[job_id] = job
            await self.job_queue.put(job)
            
            logger.info(f"Queued feature extraction for file {file_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to queue feature extraction: {e}")
            raise

    async def start_processing_worker(self) -> None:
        """Start background worker for processing jobs"""
        try:
            while True:
                try:
                    # Wait for next job
                    job = await self.job_queue.get()
                    
                    # Check if we have capacity
                    if len(self.active_jobs) >= self.max_concurrent_jobs:
                        # Put job back and wait
                        await self.job_queue.put(job)
                        await asyncio.sleep(1)
                        continue
                    
                    # Start processing job
                    task = asyncio.create_task(self._process_job(job))
                    self.active_jobs[job.job_id] = task
                    
                except Exception as e:
                    logger.error(f"Error in processing worker: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info("Processing worker stopped")

    async def _process_job(self, job: AudioProcessingJob) -> None:
        """Process individual audio job"""
        try:
            job.status = "processing"
            job.started_at = datetime.now()
            
            if job.processing_type == ProcessingType.FEATURE_EXTRACTION:
                await self._extract_features(job)
            elif job.processing_type == ProcessingType.ENHANCEMENT:
                await self._enhance_audio(job)
            elif job.processing_type == ProcessingType.ANALYSIS:
                await self._analyze_audio(job)
            elif job.processing_type == ProcessingType.TRANSCRIPTION:
                await self._transcribe_audio(job)
            else:
                raise ValueError(f"Unknown processing type: {job.processing_type}")
            
            job.status = "completed"
            job.completed_at = datetime.now()
            
            logger.info(f"Completed job {job.job_id} ({job.processing_type.value})")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            logger.error(f"Job {job.job_id} failed: {e}")
            
        finally:
            # Remove from active jobs
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]

    async def _extract_features(self, job: AudioProcessingJob) -> None:
        """Extract comprehensive audio features"""
        try:
            file_id = job.file_id
            
            if file_id not in self.audio_files:
                raise ValueError(f"Audio file {file_id} not found")
            
            audio_metadata = self.audio_files[file_id]
            file_path = self.workspace_path / f"{file_id}_{audio_metadata.filename}"
            
            if not LIBROSA_AVAILABLE:
                raise RuntimeError("librosa not available for feature extraction")
            
            # Load audio
            y, sr = librosa.load(file_path, sr=self.default_sample_rate)
            
            # Initialize features object
            features = AudioFeatures(
                feature_id=str(uuid.uuid4()),
                file_id=file_id
            )
            
            # Extract temporal features
            if job.parameters.get("extract_tempo", True):
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                features.tempo = float(tempo)
                features.beat_times = beats.tolist()
            
            if job.parameters.get("extract_onsets", True):
                onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
                features.onset_times = librosa.onset.frames_to_time(onset_frames, sr=sr).tolist()
            
            # Extract spectral features
            if job.parameters.get("extract_mfcc", True):
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features.mfcc = mfcc
            
            if job.parameters.get("extract_chroma", True):
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                features.chroma = chroma
            
            if job.parameters.get("extract_mel", True):
                mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
                features.mel_spectrogram = mel_spec
            
            if job.parameters.get("extract_spectral", True):
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                features.spectral_centroid = spectral_centroids
                
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                features.spectral_rolloff = spectral_rolloff
                
                zcr = librosa.feature.zero_crossing_rate(y)
                features.zero_crossing_rate = zcr
            
            # Extract harmonic features
            if job.parameters.get("extract_harmonic", True):
                harmonic, percussive = librosa.effects.hpss(y)
                features.harmonic = harmonic
                features.percussive = percussive
            
            # Extract high-level features using ML models
            if job.parameters.get("extract_high_level", True):
                await self._extract_high_level_features(y, sr, features)
            
            # Store features
            self.audio_features[file_id] = features
            
            # Update job result
            job.result_data = {
                "feature_id": features.feature_id,
                "features_extracted": [
                    name for name, value in features.__dict__.items()
                    if value is not None and name not in ["feature_id", "file_id", "extraction_timestamp"]
                ]
            }
            
            logger.info(f"Extracted {len(job.result_data['features_extracted'])} features for file {file_id}")
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise

    async def _extract_high_level_features(self, y: np.ndarray, sr: int, features: AudioFeatures) -> None:
        """Extract high-level semantic features using ML models"""
        try:
            # Energy calculation
            energy = np.sum(y ** 2) / len(y)
            features.energy = float(energy)
            
            # Valence estimation (mood positivity)
            if features.chroma is not None and features.mfcc is not None:
                # Simplified valence estimation based on harmonic content
                chroma_var = np.var(features.chroma, axis=1)
                valence = float(np.mean(chroma_var))
                features.valence = min(max(valence, 0.0), 1.0)
            
            # Danceability estimation
            if features.tempo is not None and features.beat_times is not None:
                # Simplified danceability based on tempo and beat regularity
                tempo_factor = 1.0 if 90 <= features.tempo <= 140 else 0.5
                beat_regularity = 1.0 / (1.0 + np.std(np.diff(features.beat_times)))
                features.danceability = float(tempo_factor * beat_regularity)
            
            # Acousticness estimation
            if features.harmonic is not None and features.percussive is not None:
                harmonic_energy = np.sum(features.harmonic ** 2)
                percussive_energy = np.sum(features.percussive ** 2)
                total_energy = harmonic_energy + percussive_energy
                
                if total_energy > 0:
                    features.acousticness = float(harmonic_energy / total_energy)
            
            # Speechiness estimation
            if features.zero_crossing_rate is not None:
                zcr_mean = np.mean(features.zero_crossing_rate)
                features.speechiness = float(min(zcr_mean * 10, 1.0))  # Normalized
            
            # Creator-specific features
            await self._extract_creator_features(y, sr, features)
            
        except Exception as e:
            logger.warning(f"High-level feature extraction partial failure: {e}")

    async def _extract_creator_features(self, y: np.ndarray, sr: int, features: AudioFeatures) -> None:
        """Extract creator-specific features for Ainflue platform"""
        try:
            # Emotional intensity (combination of energy and spectral features)
            if features.energy is not None and features.spectral_centroid is not None:
                spectral_mean = np.mean(features.spectral_centroid)
                emotional_intensity = features.energy * (spectral_mean / sr) * 2
                features.emotional_intensity = float(min(emotional_intensity, 1.0))
            
            # Commercial potential (based on audio characteristics favored in commercial music)
            commercial_score = 0.0
            
            if features.tempo is not None:
                # Commercial music often has tempo in 120-140 BPM range
                tempo_score = 1.0 if 120 <= features.tempo <= 140 else 0.5
                commercial_score += tempo_score * 0.3
            
            if features.energy is not None:
                # High energy is often commercial
                energy_score = min(features.energy * 2, 1.0)
                commercial_score += energy_score * 0.3
            
            if features.danceability is not None:
                # Danceability adds commercial appeal
                commercial_score += features.danceability * 0.4
            
            features.commercial_potential = float(min(commercial_score, 1.0))
            
            # Creativity score (based on uniqueness and complexity)
            creativity_score = 0.0
            
            if features.spectral_centroid is not None:
                # Spectral variety indicates creativity
                spectral_var = np.var(features.spectral_centroid)
                creativity_score += min(spectral_var / 1000, 1.0) * 0.4
            
            if features.chroma is not None:
                # Harmonic complexity indicates creativity
                chroma_complexity = np.mean(np.var(features.chroma, axis=1))
                creativity_score += min(chroma_complexity * 5, 1.0) * 0.3
            
            if features.tempo is not None:
                # Unconventional tempos can indicate creativity
                tempo_creativity = 1.0 if features.tempo < 80 or features.tempo > 160 else 0.5
                creativity_score += tempo_creativity * 0.3
            
            features.creativity_score = float(min(creativity_score, 1.0))
            
        except Exception as e:
            logger.warning(f"Creator features extraction failed: {e}")

    async def _enhance_audio(self, job: AudioProcessingJob) -> None:
        """Enhance audio quality using ML models"""
        try:
            file_id = job.file_id
            
            if file_id not in self.audio_files:
                raise ValueError(f"Audio file {file_id} not found")
            
            audio_metadata = self.audio_files[file_id]
            file_path = self.workspace_path / f"{file_id}_{audio_metadata.filename}"
            
            if not LIBROSA_AVAILABLE:
                raise RuntimeError("librosa not available for audio enhancement")
            
            # Load audio
            y, sr = librosa.load(file_path, sr=None)
            
            # Apply enhancements based on parameters
            enhanced_audio = y.copy()
            enhancements_applied = []
            
            # Noise reduction
            if job.parameters.get("noise_reduction", False):
                enhanced_audio = await self._apply_noise_reduction(enhanced_audio, sr)
                enhancements_applied.append("noise_reduction")
            
            # Dynamic range compression
            if job.parameters.get("compression", False):
                enhanced_audio = await self._apply_compression(enhanced_audio)
                enhancements_applied.append("compression")
            
            # EQ enhancement
            if job.parameters.get("eq_enhancement", False):
                enhanced_audio = await self._apply_eq_enhancement(enhanced_audio, sr)
                enhancements_applied.append("eq_enhancement")
            
            # Stereo enhancement
            if job.parameters.get("stereo_enhancement", False) and audio_metadata.channels > 1:
                enhanced_audio = await self._apply_stereo_enhancement(enhanced_audio)
                enhancements_applied.append("stereo_enhancement")
            
            # Save enhanced audio
            enhanced_filename = f"enhanced_{audio_metadata.filename}"
            enhanced_path = self.workspace_path / f"{file_id}_{enhanced_filename}"
            
            sf.write(enhanced_path, enhanced_audio, sr)
            
            job.result_data = {
                "enhanced_file_path": str(enhanced_path),
                "enhancements_applied": enhancements_applied,
                "original_duration": audio_metadata.duration_seconds,
                "enhanced_duration": len(enhanced_audio) / sr
            }
            
            logger.info(f"Enhanced audio file {file_id} with {len(enhancements_applied)} enhancements")
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            raise

    async def _apply_noise_reduction(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction using spectral subtraction"""
        try:
            if not SCIPY_AVAILABLE:
                return y
            
            # Simple spectral subtraction noise reduction
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * sr / 512)  # 512 is default hop_length
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Apply spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            enhanced_magnitude = magnitude - alpha * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
            
            # Reconstruct audio
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = librosa.istft(enhanced_stft)
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return y

    async def _apply_compression(self, y: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Simple compression algorithm
            threshold = 0.5
            ratio = 4.0
            
            # Apply compression
            compressed = np.where(
                np.abs(y) > threshold,
                np.sign(y) * (threshold + (np.abs(y) - threshold) / ratio),
                y
            )
            
            # Normalize
            compressed = compressed / np.max(np.abs(compressed))
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return y

    async def _apply_eq_enhancement(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply EQ enhancement"""
        try:
            if not SCIPY_AVAILABLE:
                return y
            
            # Simple EQ: slight bass boost and high-frequency enhancement
            from scipy.signal import butter, filtfilt
            
            # Bass boost (80Hz)
            nyquist = sr / 2
            low_cutoff = 80 / nyquist
            b_low, a_low = butter(2, low_cutoff, btype='high')
            bass_enhanced = filtfilt(b_low, a_low, y)
            
            # High frequency enhancement (8kHz)
            high_cutoff = 8000 / nyquist
            b_high, a_high = butter(2, high_cutoff, btype='low')
            treble_enhanced = filtfilt(b_high, a_high, y)
            
            # Combine
            enhanced = 0.7 * y + 0.2 * bass_enhanced + 0.1 * treble_enhanced
            
            # Normalize
            enhanced = enhanced / np.max(np.abs(enhanced))
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"EQ enhancement failed: {e}")
            return y

    async def _apply_stereo_enhancement(self, y: np.ndarray) -> np.ndarray:
        """Apply stereo enhancement"""
        try:
            if len(y.shape) < 2:
                return y
            
            # Simple stereo widening
            left = y[0]
            right = y[1]
            
            # Create mid and side signals
            mid = (left + right) / 2
            side = (left - right) / 2
            
            # Enhance side signal
            side_enhanced = side * 1.2
            
            # Reconstruct stereo
            left_enhanced = mid + side_enhanced
            right_enhanced = mid - side_enhanced
            
            enhanced = np.stack([left_enhanced, right_enhanced])
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Stereo enhancement failed: {e}")
            return y

    async def _analyze_audio(self, job: AudioProcessingJob) -> None:
        """Perform comprehensive audio analysis"""
        try:
            file_id = job.file_id
            
            if file_id not in self.audio_features:
                # Extract features first if not available
                await self.queue_feature_extraction(file_id)
                # Wait for feature extraction to complete
                await asyncio.sleep(2)
            
            if file_id not in self.audio_features:
                raise ValueError(f"Features not available for file {file_id}")
            
            features = self.audio_features[file_id]
            analysis_results = {}
            
            # Genre classification
            if "genre_classifier" in self.ml_models:
                genre = await self._classify_genre(features)
                analysis_results["genre"] = genre
            
            # Mood analysis
            if "mood_analyzer" in self.ml_models:
                mood = await self._analyze_mood(features)
                analysis_results["mood"] = mood
            
            # Quality assessment
            if "quality_assessor" in self.ml_models:
                quality = await self._assess_quality(features)
                analysis_results["quality"] = quality
            
            # Musical key detection
            if features.chroma is not None:
                key = await self._detect_key(features.chroma)
                analysis_results["key"] = key
            
            # Structural analysis
            structure = await self._analyze_structure(features)
            analysis_results["structure"] = structure
            
            # Creator-specific analysis
            creator_analysis = await self._creator_specific_analysis(features)
            analysis_results["creator_insights"] = creator_analysis
            
            job.result_data = analysis_results
            
            logger.info(f"Completed audio analysis for file {file_id}")
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise

    async def _classify_genre(self, features: AudioFeatures) -> str:
        """Classify music genre using ML model"""
        try:
            # Simplified genre classification based on features
            if features.tempo is not None and features.energy is not None:
                if features.tempo > 140 and features.energy > 0.8:
                    return GenreClassification.ELECTRONIC.value
                elif 120 <= features.tempo <= 140 and features.energy > 0.6:
                    return GenreClassification.POP.value
                elif features.tempo < 90 and features.acousticness and features.acousticness > 0.7:
                    return GenreClassification.FOLK.value
                elif features.tempo > 150 and features.energy > 0.7:
                    return GenreClassification.ROCK.value
                else:
                    return GenreClassification.UNKNOWN.value
            
            return GenreClassification.UNKNOWN.value
            
        except Exception as e:
            logger.warning(f"Genre classification failed: {e}")
            return GenreClassification.UNKNOWN.value

    async def _analyze_mood(self, features: AudioFeatures) -> Dict[str, float]:
        """Analyze emotional mood of audio"""
        try:
            mood = {
                "valence": features.valence or 0.5,
                "energy": features.energy or 0.5,
                "tension": 0.5,
                "happiness": 0.5
            }
            
            # Calculate tension based on spectral features
            if features.spectral_centroid is not None:
                spectral_var = np.var(features.spectral_centroid)
                mood["tension"] = min(spectral_var / 1000, 1.0)
            
            # Calculate happiness based on valence and energy
            if features.valence is not None and features.energy is not None:
                mood["happiness"] = (features.valence + features.energy) / 2
            
            return mood
            
        except Exception as e:
            logger.warning(f"Mood analysis failed: {e}")
            return {"valence": 0.5, "energy": 0.5, "tension": 0.5, "happiness": 0.5}

    async def _assess_quality(self, features: AudioFeatures) -> Dict[str, float]:
        """Assess audio quality metrics"""
        try:
            quality = {
                "clarity": 0.8,  # Default values
                "loudness": 0.7,
                "distortion": 0.1,
                "noise_level": 0.2,
                "overall_score": 0.8
            }
            
            # Assess clarity based on spectral features
            if features.spectral_centroid is not None:
                clarity = min(np.mean(features.spectral_centroid) / 2000, 1.0)
                quality["clarity"] = clarity
            
            # Assess loudness based on energy
            if features.energy is not None:
                quality["loudness"] = features.energy
            
            # Calculate overall score
            overall = (quality["clarity"] + quality["loudness"] + 
                      (1 - quality["distortion"]) + (1 - quality["noise_level"])) / 4
            quality["overall_score"] = overall
            
            return quality
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return {"clarity": 0.8, "loudness": 0.7, "distortion": 0.1, 
                   "noise_level": 0.2, "overall_score": 0.8}

    async def _detect_key(self, chroma: np.ndarray) -> str:
        """Detect musical key from chroma features"""
        try:
            # Key templates (major and minor)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            # Average chroma over time
            chroma_mean = np.mean(chroma, axis=1)
            
            # Find the strongest chroma bin
            strongest_bin = np.argmax(chroma_mean)
            detected_key = key_names[strongest_bin]
            
            # Simple major/minor detection based on chord patterns
            # This is simplified - in practice would use more sophisticated algorithms
            if chroma_mean[strongest_bin] > 0.7:
                return f"{detected_key} major"
            else:
                return f"{detected_key} minor"
                
        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            return "Unknown"

    async def _analyze_structure(self, features: AudioFeatures) -> Dict[str, Any]:
        """Analyze musical structure"""
        try:
            structure = {
                "sections": [],
                "total_duration": 0.0,
                "has_intro": False,
                "has_outro": False,
                "repetitive_structure": False
            }
            
            if features.onset_times and features.beat_times:
                # Simple structure analysis based on onset density
                total_time = max(features.onset_times) if features.onset_times else 0
                structure["total_duration"] = total_time
                
                # Detect sections based on onset density changes
                if len(features.onset_times) > 10:
                    section_length = total_time / 4  # Divide into 4 sections
                    for i in range(4):
                        start_time = i * section_length
                        end_time = (i + 1) * section_length
                        
                        section_onsets = [
                            onset for onset in features.onset_times
                            if start_time <= onset <= end_time
                        ]
                        
                        structure["sections"].append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "onset_density": len(section_onsets) / section_length,
                            "section_type": "verse" if i % 2 == 0 else "chorus"
                        })
                
                # Detect intro/outro (low onset density at beginning/end)
                if structure["sections"]:
                    first_section = structure["sections"][0]
                    last_section = structure["sections"][-1]
                    
                    avg_density = np.mean([s["onset_density"] for s in structure["sections"]])
                    
                    structure["has_intro"] = first_section["onset_density"] < avg_density * 0.5
                    structure["has_outro"] = last_section["onset_density"] < avg_density * 0.5
            
            return structure
            
        except Exception as e:
            logger.warning(f"Structure analysis failed: {e}")
            return {"sections": [], "total_duration": 0.0}

    async def _creator_specific_analysis(self, features: AudioFeatures) -> Dict[str, Any]:
        """Perform creator-specific analysis for Ainflue platform"""
        try:
            insights = {
                "commercial_viability": 0.0,
                "social_media_potential": 0.0,
                "streaming_optimization": {},
                "collaboration_opportunities": [],
                "improvement_suggestions": []
            }
            
            # Commercial viability
            if features.commercial_potential is not None:
                insights["commercial_viability"] = features.commercial_potential
            
            # Social media potential (based on energy and catchiness)
            if features.energy is not None and features.danceability is not None:
                social_score = (features.energy + features.danceability) / 2
                insights["social_media_potential"] = social_score
            
            # Streaming optimization recommendations
            if features.tempo is not None:
                insights["streaming_optimization"] = {
                    "recommended_platforms": [],
                    "genre_tags": [],
                    "target_audience": ""
                }
                
                # Platform recommendations based on tempo and genre
                if 120 <= features.tempo <= 140:
                    insights["streaming_optimization"]["recommended_platforms"].extend([
                        "Spotify", "Apple Music", "TikTok"
                    ])
                
                if features.energy and features.energy > 0.7:
                    insights["streaming_optimization"]["recommended_platforms"].append("YouTube")
            
            # Collaboration opportunities
            if features.acousticness is not None:
                if features.acousticness > 0.7:
                    insights["collaboration_opportunities"].append("acoustic_artists")
                if features.energy and features.energy > 0.8:
                    insights["collaboration_opportunities"].append("electronic_producers")
            
            # Improvement suggestions
            suggestions = []
            
            if features.energy is not None and features.energy < 0.5:
                suggestions.append("Consider adding more dynamic elements to increase energy")
            
            if features.commercial_potential is not None and features.commercial_potential < 0.6:
                suggestions.append("Optimize tempo and structure for commercial appeal")
            
            if features.creativity_score is not None and features.creativity_score > 0.8:
                suggestions.append("High creativity detected - consider artistic/experimental platforms")
            
            insights["improvement_suggestions"] = suggestions
            
            return insights
            
        except Exception as e:
            logger.warning(f"Creator-specific analysis failed: {e}")
            return {}

    async def _transcribe_audio(self, job: AudioProcessingJob) -> None:
        """Transcribe speech in audio to text"""
        try:
            file_id = job.file_id
            
            if file_id not in self.audio_files:
                raise ValueError(f"Audio file {file_id} not found")
            
            # Simplified transcription - in production would use actual STT model
            transcription_result = {
                "text": "This is a placeholder transcription. In production, this would use a real speech-to-text model.",
                "confidence": 0.85,
                "language": "en",
                "segments": [
                    {
                        "start_time": 0.0,
                        "end_time": 5.0,
                        "text": "This is a placeholder transcription.",
                        "confidence": 0.85
                    }
                ],
                "speaker_count": 1,
                "contains_speech": True
            }
            
            job.result_data = transcription_result
            
            logger.info(f"Transcribed audio file {file_id}")
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise

    # API methods for external integration
    def get_file_metadata(self, file_id: str) -> Optional[AudioMetadata]:
        """Get metadata for audio file"""
        return self.audio_files.get(file_id)

    def get_file_features(self, file_id: str) -> Optional[AudioFeatures]:
        """Get extracted features for audio file"""
        return self.audio_features.get(file_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        if job_id not in self.processing_jobs:
            return None
        
        job = self.processing_jobs[job_id]
        return {
            "job_id": job.job_id,
            "file_id": job.file_id,
            "processing_type": job.processing_type.value,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "result_data": job.result_data
        }

    def search_audio_files(self, query: str, filters: Optional[Dict] = None) -> List[AudioMetadata]:
        """Search audio files by metadata"""
        try:
            results = []
            query_lower = query.lower()
            
            for file_metadata in self.audio_files.values():
                # Search in filename, artist, title, album
                searchable_fields = [
                    file_metadata.filename,
                    file_metadata.artist or "",
                    file_metadata.title or "",
                    file_metadata.album or "",
                    file_metadata.genre or ""
                ]
                
                if any(query_lower in field.lower() for field in searchable_fields):
                    results.append(file_metadata)
                    continue
                
                # Search in tags
                if any(query_lower in tag.lower() for tag in file_metadata.tags):
                    results.append(file_metadata)
            
            # Apply filters
            if filters:
                filtered_results = []
                for metadata in results:
                    match = True
                    
                    if "format" in filters and metadata.format.value != filters["format"]:
                        match = False
                    
                    if "min_duration" in filters and metadata.duration_seconds < filters["min_duration"]:
                        match = False
                    
                    if "max_duration" in filters and metadata.duration_seconds > filters["max_duration"]:
                        match = False
                    
                    if "genre" in filters and metadata.genre != filters["genre"]:
                        match = False
                    
                    if match:
                        filtered_results.append(metadata)
                
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Audio search failed: {e}")
            return []

    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        try:
            total_files = len(self.audio_files)
            total_features = len(self.audio_features)
            total_jobs = len(self.processing_jobs)
            active_jobs = len(self.active_jobs)
            
            # Calculate total duration and file sizes
            total_duration = sum(metadata.duration_seconds for metadata in self.audio_files.values())
            total_size = sum(metadata.file_size_bytes for metadata in self.audio_files.values())
            
            # Job statistics
            completed_jobs = len([job for job in self.processing_jobs.values() if job.status == "completed"])
            failed_jobs = len([job for job in self.processing_jobs.values() if job.status == "failed"])
            
            # Format distribution
            format_distribution = {}
            for metadata in self.audio_files.values():
                format_name = metadata.format.value
                format_distribution[format_name] = format_distribution.get(format_name, 0) + 1
            
            return {
                "timestamp": datetime.now().isoformat(),
                "files": {
                    "total_files": total_files,
                    "total_duration_seconds": total_duration,
                    "total_size_bytes": total_size,
                    "format_distribution": format_distribution
                },
                "features": {
                    "total_extracted": total_features,
                    "extraction_rate": (total_features / total_files * 100) if total_files > 0 else 0
                },
                "processing": {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "completed_jobs": completed_jobs,
                    "failed_jobs": failed_jobs,
                    "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
                },
                "models": {
                    "loaded_models": len(self.ml_models),
                    "model_names": list(self.ml_models.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine statistics: {e}")
            return {}

    async def shutdown(self) -> None:
        """Gracefully shutdown the audio engine"""
        try:
            # Cancel all active jobs
            for task in self.active_jobs.values():
                if not task.done():
                    task.cancel()
            
            # Wait for jobs to complete
            if self.active_jobs:
                await asyncio.gather(*self.active_jobs.values(), return_exceptions=True)
            
            logger.info("Enterprise Audio Engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during audio engine shutdown: {e}")