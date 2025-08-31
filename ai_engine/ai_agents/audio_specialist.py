"""Audio Specialist Agent

Advanced AI agent specialized in audio processing, analysis, enhancement,
and protection for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import asyncio
import json
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from .base_agent import BaseAIAgent, AgentCapability, AgentConfiguration, AgentTask
from ..audio.signal_processing import AudioSignalProcessor
from ..audio.music_analysis import MusicAnalyzer
from ..audio.enhancement import AudioEnhancer
from ..audio.fingerprinting import AudioFingerprinter
from ..content_protection.copyright_detector import CopyrightDetector

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
    LOW = "low"          # 64-128 kbps
    MEDIUM = "medium"    # 128-256 kbps
    HIGH = "high"        # 256-320 kbps
    LOSSLESS = "lossless"  # FLAC, WAV


class ProcessingMode(Enum):
    """Audio processing modes"""
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    CONVERSION = "conversion"
    FINGERPRINTING = "fingerprinting"
    NOISE_REDUCTION = "noise_reduction"
    MASTERING = "mastering"
    STEM_SEPARATION = "stem_separation"
    PITCH_CORRECTION = "pitch_correction"


@dataclass
class AudioMetadata:
    """Comprehensive audio metadata"""
    # Basic properties
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    format: AudioFormat = AudioFormat.WAV
    bitrate: Optional[int] = None
    file_size_bytes: int = 0
    
    # Musical properties
    key: Optional[str] = None
    tempo_bpm: Optional[float] = None
    time_signature: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    
    # Technical analysis
    dynamic_range: Optional[float] = None
    peak_level: Optional[float] = None
    rms_level: Optional[float] = None
    frequency_spectrum: Optional[Dict[str, float]] = None
    harmonic_content: Optional[Dict[str, float]] = None
    
    # Content identification
    fingerprint: Optional[str] = None
    copyright_matches: List[Dict[str, Any]] = field(default_factory=list)
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    
    # Quality metrics
    quality_score: float = 0.0
    noise_level: float = 0.0
    distortion_level: float = 0.0
    clipping_detected: bool = False


@dataclass
class AudioProcessingRequest:
    """Request for audio processing"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = ""
    processing_mode: ProcessingMode = ProcessingMode.ANALYSIS
    output_format: AudioFormat = AudioFormat.WAV
    output_quality: AudioQuality = AudioQuality.HIGH
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Enhancement options
    noise_reduction: bool = False
    normalize_volume: bool = False
    enhance_bass: bool = False
    enhance_treble: bool = False
    stereo_widening: bool = False
    dynamic_range_compression: bool = False
    
    # Analysis options
    extract_features: bool = True
    identify_copyright: bool = True
    generate_fingerprint: bool = True
    analyze_music_theory: bool = False
    
    # Output options
    preserve_original: bool = True
    create_previews: bool = False
    generate_waveform: bool = False


@dataclass
class AudioProcessingResult:
    """Result of audio processing"""
    request_id: str
    success: bool
    output_file_path: Optional[str] = None
    metadata: Optional[AudioMetadata] = None
    processing_time_seconds: float = 0.0
    quality_improvements: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    preview_files: List[str] = field(default_factory=list)
    waveform_data: Optional[Dict[str, Any]] = None
    analysis_data: Dict[str, Any] = field(default_factory=dict)


class AudioSpecialistAgent(BaseAIAgent):
    """
    Advanced audio processing specialist agent
    
    Capabilities:
    - High-quality audio analysis and enhancement
    - Music theory analysis (key, tempo, harmony)
    - Audio fingerprinting and copyright detection
    - Format conversion and optimization
    - Noise reduction and mastering
    - Stem separation and vocal extraction
    - Real-time audio processing
    - Multi-platform audio optimization
    """
    
    def __init__(self, config: AgentConfiguration):
        # Ensure required capabilities
        required_capabilities = {
            AgentCapability.AUDIO_GENERATION,
            AgentCapability.CONTENT_FINGERPRINTING,
            AgentCapability.COPYRIGHT_DETECTION,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.REAL_TIME_PROCESSING
        }
        
        config.capabilities.update(required_capabilities)
        super().__init__(config)
        
        # Audio processing engines
        self.signal_processor: Optional[AudioSignalProcessor] = None
        self.music_analyzer: Optional[MusicAnalyzer] = None
        self.audio_enhancer: Optional[AudioEnhancer] = None
        self.fingerprinter: Optional[AudioFingerprinter] = None
        self.copyright_detector: Optional[CopyrightDetector] = None
        
        # Configuration
        self.supported_formats = [fmt for fmt in AudioFormat]
        self.max_file_size_mb = 500
        self.processing_queue_size = 50
        self.temp_dir = "/tmp/audio_processing"
        
        # Processing cache
        self.metadata_cache: Dict[str, AudioMetadata] = {}
        self.fingerprint_cache: Dict[str, str] = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            "min_sample_rate": 22050,
            "min_bit_depth": 16,
            "max_noise_level": 0.1,
            "max_distortion": 0.05,
            "min_dynamic_range": 6.0
        }
    
    async def _custom_initialize(self) -> None:
        """Initialize audio processing components"""
        try:
            # Initialize audio processing engines
            self.signal_processor = AudioSignalProcessor()
            await self.signal_processor.initialize()
            
            self.music_analyzer = MusicAnalyzer()
            await self.music_analyzer.initialize()
            
            self.audio_enhancer = AudioEnhancer()
            await self.audio_enhancer.initialize()
            
            self.fingerprinter = AudioFingerprinter()
            await self.fingerprinter.initialize()
            
            self.copyright_detector = CopyrightDetector()
            await self.copyright_detector.initialize()
            
            # Create temporary processing directory
            import os
            os.makedirs(self.temp_dir, exist_ok=True)
            
            self.logger.info("Audio processing components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio components: {str(e)}")
            raise
    
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Execute audio processing task"""
        task_type = task.task_type
        context = task.context
        
        if task_type == "process_audio":
            return await self._process_audio(context)
        elif task_type == "analyze_music":
            return await self._analyze_music_theory(context)
        elif task_type == "enhance_audio":
            return await self._enhance_audio_quality(context)
        elif task_type == "convert_format":
            return await self._convert_audio_format(context)
        elif task_type == "extract_stems":
            return await self._extract_audio_stems(context)
        elif task_type == "detect_copyright":
            return await self._detect_copyright_content(context)
        elif task_type == "generate_fingerprint":
            return await self._generate_audio_fingerprint(context)
        elif task_type == "real_time_analysis":
            return await self._real_time_audio_analysis(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _process_audio(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive audio processing"""
        request = AudioProcessingRequest(**context.get("request", {}))
        
        self.logger.info(f"Processing audio file: {request.file_path}")
        
        start_time = datetime.utcnow()
        
        try:
            # Validate input file
            if not await self._validate_audio_file(request.file_path):
                return {
                    "success": False,
                    "error": "Invalid audio file",
                    "request_id": request.request_id
                }
            
            # Load audio data
            audio_data, sample_rate = await self.signal_processor.load_audio(request.file_path)
            
            # Extract basic metadata
            metadata = await self._extract_basic_metadata(audio_data, sample_rate, request.file_path)
            
            # Perform analysis if requested
            analysis_data = {}
            if request.extract_features:
                analysis_data = await self._comprehensive_audio_analysis(audio_data, sample_rate)
                metadata = await self._update_metadata_from_analysis(metadata, analysis_data)
            
            # Generate fingerprint if requested
            fingerprint = None
            if request.generate_fingerprint:
                fingerprint = await self.fingerprinter.generate_fingerprint(audio_data, sample_rate)
                metadata.fingerprint = fingerprint
            
            # Copyright detection if requested
            copyright_matches = []
            if request.identify_copyright:
                copyright_matches = await self.copyright_detector.detect_matches(
                    audio_data, sample_rate, fingerprint
                )
                metadata.copyright_matches = copyright_matches
            
            # Music theory analysis if requested
            if request.analyze_music_theory:
                music_analysis = await self.music_analyzer.analyze_musical_content(
                    audio_data, sample_rate
                )
                analysis_data["music_theory"] = music_analysis
                await self._update_metadata_from_music_analysis(metadata, music_analysis)
            
            # Audio enhancement if requested
            enhanced_audio = audio_data
            quality_improvements = {}
            
            if any([request.noise_reduction, request.normalize_volume, request.enhance_bass,
                   request.enhance_treble, request.stereo_widening, request.dynamic_range_compression]):
                
                enhanced_audio, quality_improvements = await self._apply_audio_enhancements(
                    audio_data, sample_rate, request
                )
            
            # Save processed audio
            output_file_path = None
            if request.processing_mode != ProcessingMode.ANALYSIS:
                output_file_path = await self._save_processed_audio(
                    enhanced_audio, sample_rate, request
                )
            
            # Generate previews if requested
            preview_files = []
            if request.create_previews:
                preview_files = await self._generate_audio_previews(
                    enhanced_audio, sample_rate, request
                )
            
            # Generate waveform data if requested
            waveform_data = None
            if request.generate_waveform:
                waveform_data = await self._generate_waveform_data(enhanced_audio, sample_rate)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = AudioProcessingResult(
                request_id=request.request_id,
                success=True,
                output_file_path=output_file_path,
                metadata=metadata,
                processing_time_seconds=processing_time,
                quality_improvements=quality_improvements,
                preview_files=preview_files,
                waveform_data=waveform_data,
                analysis_data=analysis_data
            )
            
            self.logger.info(f"Audio processing completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "result": result.__dict__,
                "processing_time": processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request.request_id,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def _comprehensive_audio_analysis(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Perform comprehensive audio analysis"""
        analysis = {}
        
        # Signal analysis
        signal_analysis = await self.signal_processor.analyze_signal(audio_data, sample_rate)
        analysis["signal"] = signal_analysis
        
        # Frequency analysis
        frequency_analysis = await self.signal_processor.analyze_frequency_spectrum(audio_data, sample_rate)
        analysis["frequency"] = frequency_analysis
        
        # Dynamic range analysis
        dynamic_analysis = await self.signal_processor.analyze_dynamics(audio_data)
        analysis["dynamics"] = dynamic_analysis
        
        # Quality assessment
        quality_analysis = await self.signal_processor.assess_audio_quality(audio_data, sample_rate)
        analysis["quality"] = quality_analysis
        
        # Harmonic analysis
        harmonic_analysis = await self.signal_processor.analyze_harmonics(audio_data, sample_rate)
        analysis["harmonics"] = harmonic_analysis
        
        # Tempo and rhythm analysis
        rhythm_analysis = await self.music_analyzer.analyze_rhythm(audio_data, sample_rate)
        analysis["rhythm"] = rhythm_analysis
        
        return analysis
    
    async def _apply_audio_enhancements(self, audio_data: np.ndarray, sample_rate: int, 
                                      request: AudioProcessingRequest) -> Tuple[np.ndarray, Dict[str, float]]:
        """Apply audio enhancements based on request"""
        enhanced_audio = audio_data.copy()
        improvements = {}
        
        # Noise reduction
        if request.noise_reduction:
            enhanced_audio, noise_reduction = await self.audio_enhancer.reduce_noise(
                enhanced_audio, sample_rate
            )
            improvements["noise_reduction"] = noise_reduction
        
        # Volume normalization
        if request.normalize_volume:
            enhanced_audio, volume_change = await self.audio_enhancer.normalize_volume(
                enhanced_audio, target_lufs=-14.0
            )
            improvements["volume_normalization"] = volume_change
        
        # Bass enhancement
        if request.enhance_bass:
            enhanced_audio, bass_gain = await self.audio_enhancer.enhance_bass(
                enhanced_audio, sample_rate, gain_db=3.0
            )
            improvements["bass_enhancement"] = bass_gain
        
        # Treble enhancement
        if request.enhance_treble:
            enhanced_audio, treble_gain = await self.audio_enhancer.enhance_treble(
                enhanced_audio, sample_rate, gain_db=2.0
            )
            improvements["treble_enhancement"] = treble_gain
        
        # Stereo widening
        if request.stereo_widening and enhanced_audio.ndim > 1:
            enhanced_audio, width_factor = await self.audio_enhancer.widen_stereo(
                enhanced_audio, factor=1.3
            )
            improvements["stereo_widening"] = width_factor
        
        # Dynamic range compression
        if request.dynamic_range_compression:
            enhanced_audio, compression_ratio = await self.audio_enhancer.compress_dynamics(
                enhanced_audio, ratio=4.0, threshold_db=-12.0
            )
            improvements["compression"] = compression_ratio
        
        return enhanced_audio, improvements
    
    async def _extract_audio_stems(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract individual stems from mixed audio"""
        file_path = context.get("file_path", "")
        output_dir = context.get("output_dir", self.temp_dir)
        
        try:
            # Load audio
            audio_data, sample_rate = await self.signal_processor.load_audio(file_path)
            
            # Perform stem separation
            stems = await self.signal_processor.separate_stems(audio_data, sample_rate)
            
            # Save individual stems
            stem_files = {}
            for stem_name, stem_data in stems.items():
                stem_path = f"{output_dir}/stem_{stem_name}_{uuid.uuid4().hex[:8]}.wav"
                await self.signal_processor.save_audio(stem_data, sample_rate, stem_path)
                stem_files[stem_name] = stem_path
            
            return {
                "success": True,
                "stem_files": stem_files,
                "stem_count": len(stems)
            }
            
        except Exception as e:
            self.logger.error(f"Stem extraction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _detect_copyright_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect copyrighted content in audio"""
        file_path = context.get("file_path", "")
        
        try:
            # Load audio
            audio_data, sample_rate = await self.signal_processor.load_audio(file_path)
            
            # Generate fingerprint
            fingerprint = await self.fingerprinter.generate_fingerprint(audio_data, sample_rate)
            
            # Check against copyright database
            matches = await self.copyright_detector.detect_matches(audio_data, sample_rate, fingerprint)
            
            # Analyze match confidence
            high_confidence_matches = [m for m in matches if m.get("confidence", 0) > 0.8]
            
            return {
                "success": True,
                "fingerprint": fingerprint,
                "total_matches": len(matches),
                "high_confidence_matches": len(high_confidence_matches),
                "matches": matches,
                "copyright_detected": len(high_confidence_matches) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Copyright detection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_audio_file(self, file_path: str) -> bool:
        """Validate audio file"""
        try:
            import os
            
            # Check file exists
            if not os.path.exists(file_path):
                return False
            
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False
            
            # Check file format
            file_extension = file_path.split(".")[-1].lower()
            supported_extensions = [fmt.value for fmt in self.supported_formats]
            if file_extension not in supported_extensions:
                return False
            
            # Try to load audio header
            metadata = await self.signal_processor.get_audio_info(file_path)
            return metadata is not None
            
        except Exception:
            return False
    
    async def can_handle_task(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if agent can handle specific audio task"""
        supported_tasks = [
            "process_audio",
            "analyze_music",
            "enhance_audio",
            "convert_format",
            "extract_stems",
            "detect_copyright",
            "generate_fingerprint",
            "real_time_analysis"
        ]
        
        if task_type not in supported_tasks:
            return False
        
        # Check file format support
        if "file_path" in context:
            file_path = context["file_path"]
            file_extension = file_path.split(".")[-1].lower()
            supported_extensions = [fmt.value for fmt in self.supported_formats]
            return file_extension in supported_extensions
        
        return True
    
    # Additional helper methods for specific audio processing operations would be implemented here
