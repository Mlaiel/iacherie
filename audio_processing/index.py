"""🎵 Audio Engine Hub - Central Audio Intelligence Orchestrator

Professional audio processing hub that coordinates all audio capabilities
across analysis, synthesis, enhancement, protection, and quality control.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

Expert Development Team:
- Lead Dev IA: Advanced AI algorithms and intelligent processing
- Backend Senior: Robust architecture and scalable systems  
- ML Engineer: Machine learning models and audio intelligence
- DBA: Optimized data storage and retrieval systems
- Security Specialist: Content protection and fingerprinting
- Microservices Architect: Distributed audio processing
- Audio Engineer: Professional audio processing and effects
- DevOps Engineer: Containerization and production deployment
- IA Prompt Engineer: Natural language audio interfaces

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import torch
import numpy as np
import time

# Import all audio modules
from . import analysis
from . import synthesis
from . import enhancement
from . import effects
from . import quality_control
from . import fingerprinting
from . import separation
from . import format_conversion

# Import specific components for central hub
from .synthesis.index import AudioSynthesisHub, get_synthesis_hub, SynthesisCapability
from .analysis import SpectralAnalyzer, AudioQualityAssessment, GenreClassifier
from .enhancement import SpatialEnhancer, NoiseRemover, AudioUpsampler
from .effects import EqualizerProcessor, CompressorProcessor, ReverbProcessor
from .quality_control import QualityAnalyzer, LoudnessAnalyzer, PeakLimiter
from .fingerprinting import AudioFingerprinter, ContentMatcher, CopyrightDetector
from .separation import VocalSeparator, InstrumentSeparator, StemExtractor
from .format_conversion import AudioConverter, CodecManager, MetadataProcessor

logger = logging.getLogger(__name__)


class AudioCapability(Enum):
    """
Available audio processing capabilities."""
    # Analysis capabilities
    SPECTRAL_ANALYSIS = "spectral_analysis"
    GENRE_CLASSIFICATION = "genre_classification"
    QUALITY_ASSESSMENT = "quality_assessment"
    MELODY_EXTRACTION = "melody_extraction"
    RHYTHM_ANALYSIS = "rhythm_analysis"
    
    # Synthesis capabilities
    NEURAL_SYNTHESIS = "neural_synthesis"
    MUSIC_GENERATION = "music_generation"
    SPEECH_SYNTHESIS = "speech_synthesis"
    VOICE_CLONING = "voice_cloning"
    
    # Enhancement capabilities
    SPATIAL_ENHANCEMENT = "spatial_enhancement"
    NOISE_REDUCTION = "noise_reduction"
    AUDIO_UPSAMPLING = "audio_upsampling"
    DYNAMIC_RANGE = "dynamic_range"
    
    # Effects capabilities
    EQUALIZATION = "equalization"
    COMPRESSION = "compression"
    REVERB = "reverb"
    CHORUS = "chorus"
    DISTORTION = "distortion"
    
    # Quality control
    LOUDNESS_ANALYSIS = "loudness_analysis"
    PEAK_LIMITING = "peak_limiting"
    MASTERING = "mastering"
    
    # Protection & fingerprinting
    FINGERPRINTING = "fingerprinting"
    COPYRIGHT_DETECTION = "copyright_detection"
    CONTENT_MATCHING = "content_matching"
    
    # Separation capabilities
    VOCAL_SEPARATION = "vocal_separation"
    INSTRUMENT_SEPARATION = "instrument_separation"
    STEM_EXTRACTION = "stem_extraction"
    
    # Format conversion
    CODEC_CONVERSION = "codec_conversion"
    METADATA_PROCESSING = "metadata_processing"


class AudioProcessingMode(Enum):
    """Audio processing execution modes."""

    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    OFFLINE = "offline"


@dataclass
class AudioRequest:
    """Unified audio processing request structure."""
    capability: AudioCapability
    input_data: Union[torch.Tensor, np.ndarray, str, Path]
    parameters: Dict[str, Any] = field(default_factory=dict)
    processing_mode: AudioProcessingMode = AudioProcessingMode.OFFLINE
    output_format: str = "wav"
    quality_target: str = "high"
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0


@dataclass
class AudioResponse:
    """Unified audio processing response structure."""
    success: bool
    output_data: Optional[Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    performance_stats: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class AudioEngineHub:
    """
    Central hub orchestrating all audio processing capabilities.
    
    This hub provides unified access to all audio engines including synthesis,
    analysis, enhancement, effects, quality control, and protection systems.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
Initialize the Audio Engine Hub."""
        self.config_path = config_path or Path("config/audio_hub.yaml")
        
        # Component managers
        self.synthesis_hub = None
        self.analysis_engine = None
        self.enhancement_engine = None
        self.effects_engine = None
        self.quality_engine = None
        self.fingerprint_engine = None
        self.separation_engine = None
        self.conversion_engine = None
        
        # Capability registry
        self.capabilities: Dict[AudioCapability, bool] = {}
        
        # Performance monitoring
        self.total_requests = 0
        self.successful_requests = 0
        self.total_processing_time = 0.0
        self.capability_usage: Dict[AudioCapability, int] = {}
        
        # Resource monitoring
        self.active_processes = 0
        self.max_concurrent_processes = 8
        
        # Initialize hub
        self._initialize_hub()
        
    def _initialize_hub(self) -> None:
        """Initialize all audio processing engines."""
        try:
            logger.info("Initializing Audio Engine Hub...")
            
            # Initialize synthesis hub
            self.synthesis_hub = get_synthesis_hub()
            
            # Initialize analysis engine
            self._initialize_analysis_engine()
            
            # Initialize enhancement engine
            self._initialize_enhancement_engine()
            
            # Initialize effects engine
            self._initialize_effects_engine()
            
            # Initialize quality control engine
            self._initialize_quality_engine()
            
            # Initialize fingerprinting engine
            self._initialize_fingerprint_engine()
            
            # Initialize separation engine
            self._initialize_separation_engine()
            
            # Initialize conversion engine
            self._initialize_conversion_engine()
            
            # Register capabilities
            self._register_capabilities()
            
            logger.info("Audio Engine Hub initialized successfully")
            logger.info(f"Available capabilities: {len([c for c, a in self.capabilities.items() if a])}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Audio Engine Hub: {e}")
            raise
            
    def _initialize_analysis_engine(self) -> None:
        """Initialize audio analysis components."""
        try:
            self.analysis_engine = {
                'spectral_analyzer': SpectralAnalyzer(),
                'quality_assessor': AudioQualityAssessment(),
                'genre_classifier': GenreClassifier()
            }
            logger.info("Analysis engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analysis engine: {e}")
            
    def _initialize_enhancement_engine(self) -> None:
        """Initialize audio enhancement components."""
        try:
            self.enhancement_engine = {
                'spatial_enhancer': SpatialEnhancer(),
                'noise_remover': NoiseRemover(),
                'upsampler': AudioUpsampler()
            }
            logger.info("Enhancement engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize enhancement engine: {e}")
            
    def _initialize_effects_engine(self) -> None:
        """Initialize audio effects components."""
        try:
            self.effects_engine = {
                'equalizer': EqualizerProcessor(),
                'compressor': CompressorProcessor(),
                'reverb': ReverbProcessor()
            }
            logger.info("Effects engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize effects engine: {e}")
            
    def _initialize_quality_engine(self) -> None:
        """Initialize quality control components."""
        try:
            self.quality_engine = {
                'quality_analyzer': QualityAnalyzer(),
                'loudness_analyzer': LoudnessAnalyzer(),
                'peak_limiter': PeakLimiter()
            }
            logger.info("Quality control engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize quality engine: {e}")
            
    def _initialize_fingerprint_engine(self) -> None:
        """Initialize fingerprinting and protection components."""
        try:
            self.fingerprint_engine = {
                'fingerprinter': AudioFingerprinter(),
                'content_matcher': ContentMatcher(),
                'copyright_detector': CopyrightDetector()
            }
            logger.info("Fingerprinting engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize fingerprint engine: {e}")
            
    def _initialize_separation_engine(self) -> None:
        """Initialize audio separation components."""
        try:
            self.separation_engine = {
                'vocal_separator': VocalSeparator(),
                'instrument_separator': InstrumentSeparator(),
                'stem_extractor': StemExtractor()
            }
            logger.info("Separation engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize separation engine: {e}")
            
    def _initialize_conversion_engine(self) -> None:
        """Initialize format conversion components."""
        try:
            self.conversion_engine = {
                'audio_converter': AudioConverter(),
                'codec_manager': CodecManager(),
                'metadata_processor': MetadataProcessor()
            }
            logger.info("Conversion engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize conversion engine: {e}")
            
    def _register_capabilities(self) -> None:
        """Register available audio processing capabilities."""
        self.capabilities = {
            # Analysis capabilities
            AudioCapability.SPECTRAL_ANALYSIS: self.analysis_engine is not None,
            AudioCapability.GENRE_CLASSIFICATION: self.analysis_engine is not None,
            AudioCapability.QUALITY_ASSESSMENT: self.analysis_engine is not None,
            AudioCapability.MELODY_EXTRACTION: self.analysis_engine is not None,
            AudioCapability.RHYTHM_ANALYSIS: self.analysis_engine is not None,
            
            # Synthesis capabilities (delegated to synthesis hub)
            AudioCapability.NEURAL_SYNTHESIS: self.synthesis_hub is not None,
            AudioCapability.MUSIC_GENERATION: self.synthesis_hub is not None,
            AudioCapability.SPEECH_SYNTHESIS: self.synthesis_hub is not None,
            AudioCapability.VOICE_CLONING: self.synthesis_hub is not None,
            
            # Enhancement capabilities
            AudioCapability.SPATIAL_ENHANCEMENT: self.enhancement_engine is not None,
            AudioCapability.NOISE_REDUCTION: self.enhancement_engine is not None,
            AudioCapability.AUDIO_UPSAMPLING: self.enhancement_engine is not None,
            
            # Effects capabilities
            AudioCapability.EQUALIZATION: self.effects_engine is not None,
            AudioCapability.COMPRESSION: self.effects_engine is not None,
            AudioCapability.REVERB: self.effects_engine is not None,
            
            # Quality control
            AudioCapability.LOUDNESS_ANALYSIS: self.quality_engine is not None,
            AudioCapability.PEAK_LIMITING: self.quality_engine is not None,
            AudioCapability.MASTERING: self.quality_engine is not None,
            
            # Protection & fingerprinting
            AudioCapability.FINGERPRINTING: self.fingerprint_engine is not None,
            AudioCapability.COPYRIGHT_DETECTION: self.fingerprint_engine is not None,
            AudioCapability.CONTENT_MATCHING: self.fingerprint_engine is not None,
            
            # Separation capabilities
            AudioCapability.VOCAL_SEPARATION: self.separation_engine is not None,
            AudioCapability.INSTRUMENT_SEPARATION: self.separation_engine is not None,
            AudioCapability.STEM_EXTRACTION: self.separation_engine is not None,
            
            # Format conversion
            AudioCapability.CODEC_CONVERSION: self.conversion_engine is not None,
            AudioCapability.METADATA_PROCESSING: self.conversion_engine is not None,
        }
        
        # Initialize usage counters
        for capability in AudioCapability:
            self.capability_usage[capability] = 0
            
    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        """
        Main audio processing method - routes requests to appropriate engines.
        
        Args:
            request: Audio processing request with capability and parameters
            
        Returns:
            AudioResponse with processed audio and metadata
        """
        if self.active_processes >= self.max_concurrent_processes:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message="Maximum concurrent processes reached"
            )
            
        self.active_processes += 1
        self.total_requests += 1
        
        start_time = time.time()
        
        try:
            # Validate capability
            if not self.capabilities.get(request.capability, False):
                raise ValueError(f"Capability {request.capability.value} not available")
                
            # Update usage statistics
            self.capability_usage[request.capability] += 1
            
            # Route to appropriate engine
            if request.capability in [AudioCapability.NEURAL_SYNTHESIS, AudioCapability.MUSIC_GENERATION, 
                                    AudioCapability.SPEECH_SYNTHESIS, AudioCapability.VOICE_CLONING]:
                response = await self._handle_synthesis_request(request)
                
            elif request.capability in [AudioCapability.SPECTRAL_ANALYSIS, AudioCapability.GENRE_CLASSIFICATION,
                                      AudioCapability.QUALITY_ASSESSMENT]:
                response = await self._handle_analysis_request(request)
                
            elif request.capability in [AudioCapability.SPATIAL_ENHANCEMENT, AudioCapability.NOISE_REDUCTION,
                                      AudioCapability.AUDIO_UPSAMPLING]:
                response = await self._handle_enhancement_request(request)
                
            elif request.capability in [AudioCapability.EQUALIZATION, AudioCapability.COMPRESSION,
                                      AudioCapability.REVERB]:
                response = await self._handle_effects_request(request)
                
            elif request.capability in [AudioCapability.LOUDNESS_ANALYSIS, AudioCapability.PEAK_LIMITING,
                                      AudioCapability.MASTERING]:
                response = await self._handle_quality_request(request)
                
            elif request.capability in [AudioCapability.FINGERPRINTING, AudioCapability.COPYRIGHT_DETECTION,
                                      AudioCapability.CONTENT_MATCHING]:
                response = await self._handle_fingerprint_request(request)
                
            elif request.capability in [AudioCapability.VOCAL_SEPARATION, AudioCapability.INSTRUMENT_SEPARATION,
                                      AudioCapability.STEM_EXTRACTION]:
                response = await self._handle_separation_request(request)
                
            elif request.capability in [AudioCapability.CODEC_CONVERSION, AudioCapability.METADATA_PROCESSING]:
                response = await self._handle_conversion_request(request)
                
            else:
                raise ValueError(f"Unhandled capability: {request.capability.value}")
                
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            self.total_processing_time += processing_time
            
            if response.success:
                self.successful_requests += 1
                
            return response
            
        except Exception as e:
            logger.error(f"Audio processing failed for {request.capability.value}: {e}")
            
            return AudioResponse(
                success=False,
                output_data=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
            
        finally:
            self.active_processes -= 1
            
    async def _handle_synthesis_request(self, request: AudioRequest) -> AudioResponse:
        """Handle synthesis requests by delegating to synthesis hub."""
        # Map AudioCapability to SynthesisCapability
        capability_mapping = {
            AudioCapability.NEURAL_SYNTHESIS: SynthesisCapability.NEURAL_VOCODER,
            AudioCapability.MUSIC_GENERATION: SynthesisCapability.MUSIC_GENERATION,
            AudioCapability.SPEECH_SYNTHESIS: SynthesisCapability.SPEECH_SYNTHESIS,
            AudioCapability.VOICE_CLONING: SynthesisCapability.VOICE_CLONING
        }
        
        synthesis_capability = capability_mapping[request.capability]
        
        from .synthesis.index import SynthesisRequest
        synthesis_request = SynthesisRequest(
            capability=synthesis_capability,
            input_data=request.input_data,
            parameters=request.parameters
        )
        
        synthesis_response = await self.synthesis_hub.synthesize(synthesis_request)
        
        return AudioResponse(
            success=synthesis_response.success,
            output_data=synthesis_response.audio_data,
            metadata=synthesis_response.metadata,
            quality_metrics=synthesis_response.quality_metrics,
            error_message=synthesis_response.error_message
        )
        
    async def _handle_analysis_request(self, request: AudioRequest) -> AudioResponse:
        """
Handle audio analysis requests."""
        try:
            if request.capability == AudioCapability.SPECTRAL_ANALYSIS:
                analyzer = self.analysis_engine['spectral_analyzer']
                result = analyzer.analyze_spectrum(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.GENRE_CLASSIFICATION:
                classifier = self.analysis_engine['genre_classifier']
                result = classifier.classify_genre(request.input_data)
                
            elif request.capability == AudioCapability.QUALITY_ASSESSMENT:
                assessor = self.analysis_engine['quality_assessor']
                result = assessor.assess_quality(request.input_data)
                
            else:
                raise ValueError(f"Unknown analysis capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'analysis_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_enhancement_request(self, request: AudioRequest) -> AudioResponse:
        """Handle audio enhancement requests."""
        try:
            if request.capability == AudioCapability.SPATIAL_ENHANCEMENT:
                enhancer = self.enhancement_engine['spatial_enhancer']
                result = enhancer.enhance_spatial(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.NOISE_REDUCTION:
                denoiser = self.enhancement_engine['noise_remover']
                result = denoiser.remove_noise(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.AUDIO_UPSAMPLING:
                upsampler = self.enhancement_engine['upsampler']
                result = upsampler.upsample_audio(request.input_data, **request.parameters)
                
            else:
                raise ValueError(f"Unknown enhancement capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'enhancement_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_effects_request(self, request: AudioRequest) -> AudioResponse:
        """Handle audio effects requests."""
        try:
            if request.capability == AudioCapability.EQUALIZATION:
                eq = self.effects_engine['equalizer']
                result = eq.process_audio(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.COMPRESSION:
                comp = self.effects_engine['compressor']
                result = comp.process_audio(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.REVERB:
                rev = self.effects_engine['reverb']
                result = rev.process_audio(request.input_data, **request.parameters)
                
            else:
                raise ValueError(f"Unknown effects capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'effect_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_quality_request(self, request: AudioRequest) -> AudioResponse:
        """Handle quality control requests."""
        try:
            if request.capability == AudioCapability.LOUDNESS_ANALYSIS:
                analyzer = self.quality_engine['loudness_analyzer']
                result = analyzer.analyze_loudness(request.input_data)
                
            elif request.capability == AudioCapability.PEAK_LIMITING:
                limiter = self.quality_engine['peak_limiter']
                result = limiter.limit_peaks(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.MASTERING:
                # Combine multiple quality processors
                result = await self._apply_mastering_chain(request.input_data, request.parameters)
                
            else:
                raise ValueError(f"Unknown quality capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'quality_process': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_fingerprint_request(self, request: AudioRequest) -> AudioResponse:
        """Handle fingerprinting and protection requests."""
        try:
            if request.capability == AudioCapability.FINGERPRINTING:
                fingerprinter = self.fingerprint_engine['fingerprinter']
                result = fingerprinter.generate_fingerprint(request.input_data)
                
            elif request.capability == AudioCapability.COPYRIGHT_DETECTION:
                detector = self.fingerprint_engine['copyright_detector']
                result = detector.detect_copyright(request.input_data)
                
            elif request.capability == AudioCapability.CONTENT_MATCHING:
                matcher = self.fingerprint_engine['content_matcher']
                result = matcher.match_content(request.input_data, **request.parameters)
                
            else:
                raise ValueError(f"Unknown fingerprint capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'protection_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_separation_request(self, request: AudioRequest) -> AudioResponse:
        """Handle audio separation requests."""
        try:
            if request.capability == AudioCapability.VOCAL_SEPARATION:
                separator = self.separation_engine['vocal_separator']
                result = separator.separate_vocals(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.INSTRUMENT_SEPARATION:
                separator = self.separation_engine['instrument_separator']
                result = separator.separate_instruments(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.STEM_EXTRACTION:
                extractor = self.separation_engine['stem_extractor']
                result = extractor.extract_stems(request.input_data, **request.parameters)
                
            else:
                raise ValueError(f"Unknown separation capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'separation_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _handle_conversion_request(self, request: AudioRequest) -> AudioResponse:
        """Handle format conversion requests."""
        try:
            if request.capability == AudioCapability.CODEC_CONVERSION:
                converter = self.conversion_engine['audio_converter']
                result = converter.convert_format(request.input_data, **request.parameters)
                
            elif request.capability == AudioCapability.METADATA_PROCESSING:
                processor = self.conversion_engine['metadata_processor']
                result = processor.process_metadata(request.input_data, **request.parameters)
                
            else:
                raise ValueError(f"Unknown conversion capability: {request.capability.value}")
                
            return AudioResponse(
                success=True,
                output_data=result,
                metadata={'conversion_type': request.capability.value}
            )
            
        except Exception as e:
            return AudioResponse(
                success=False,
                output_data=None,
                error_message=str(e)
            )
            
    async def _apply_mastering_chain(self, audio_data: Any, parameters: Dict[str, Any]) -> Any:
        """Apply complete mastering processing chain."""
        # This would implement a complete mastering pipeline
        # For now, return the input data
        return audio_data
        
    def get_capabilities(self) -> List[str]:
        """
Get list of available audio capabilities."""
        return [cap.value for cap, available in self.capabilities.items() if available]
        
    def get_hub_statistics(self) -> Dict[str, Any]:
        """
Get hub performance and usage statistics."""
        success_rate = (self.successful_requests / self.total_requests 
                       if self.total_requests > 0 else 0)
        
        avg_processing_time = (self.total_processing_time / self.total_requests 
                             if self.total_requests > 0 else 0)
        
        most_used_capability = max(self.capability_usage.items(), 
                                 key=lambda x: x[1])[0].value if self.capability_usage else "none"
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'success_rate': success_rate,
            'average_processing_time': avg_processing_time,
            'active_processes': self.active_processes,
            'available_capabilities': len([c for c, a in self.capabilities.items() if a]),
            'most_used_capability': most_used_capability,
            'capability_usage': {cap.value: count for cap, count in self.capability_usage.items()}
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all audio engines."""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'engines': {},
            'capabilities': {},
            'performance': self.get_hub_statistics()
        }
        
        # Check engine health
        engines = {
            'synthesis_hub': self.synthesis_hub,
            'analysis_engine': self.analysis_engine,
            'enhancement_engine': self.enhancement_engine,
            'effects_engine': self.effects_engine,
            'quality_engine': self.quality_engine,
            'fingerprint_engine': self.fingerprint_engine,
            'separation_engine': self.separation_engine,
            'conversion_engine': self.conversion_engine
        }
        
        for name, engine in engines.items():
            if engine is not None:
                if hasattr(engine, 'health_check'):
                    health_status['engines'][name] = engine.health_check()
                else:
                    health_status['engines'][name] = {'status': 'active'}
            else:
                health_status['engines'][name] = {'status': 'inactive'}
                health_status['status'] = 'degraded'
                
        # Check capabilities
        for capability, available in self.capabilities.items():
            health_status['capabilities'][capability.value] = available
            
        return health_status
        
    async def shutdown(self) -> None:
        """
Gracefully shutdown all audio engines."""
        logger.info("Shutting down Audio Engine Hub...")
        
        try:
            # Shutdown synthesis hub
            if self.synthesis_hub:
                await self.synthesis_hub.shutdown()
                
            # Clear all engine references
            self.analysis_engine = None
            self.enhancement_engine = None
            self.effects_engine = None
            self.quality_engine = None
            self.fingerprint_engine = None
            self.separation_engine = None
            self.conversion_engine = None
            
            logger.info("Audio Engine Hub shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global hub instance (singleton pattern)
_audio_hub_instance: Optional[AudioEngineHub] = None


def get_audio_hub(config_path: Optional[Path] = None) -> AudioEngineHub:
    """
    Get the global Audio Engine Hub instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        AudioEngineHub instance
    """
    global _audio_hub_instance
    
    if _audio_hub_instance is None:
        _audio_hub_instance = AudioEngineHub(config_path)
        
    return _audio_hub_instance


# Convenience functions for direct access
async def process_audio(capability: AudioCapability,
                       input_data: Any,
                       parameters: Dict[str, Any] = None,
                       processing_mode: AudioProcessingMode = AudioProcessingMode.OFFLINE) -> AudioResponse:
    """
    Convenience function for direct audio processing.
    
    Args:
        capability: Audio capability to use
        input_data: Input data for processing
        parameters: Processing parameters
        processing_mode: Processing execution mode
        
    Returns:
        AudioResponse with processed audio
    """
    hub = get_audio_hub()
    
    request = AudioRequest(
        capability=capability,
        input_data=input_data,
        parameters=parameters or {},
        processing_mode=processing_mode
    )
    
    return await hub.process_audio(request)


def list_audio_capabilities() -> List[str]:
    """
Get list of available audio capabilities."""
    hub = get_audio_hub()
    return hub.get_capabilities()


def get_audio_hub_health() -> Dict[str, Any]:
    """
Get audio hub health status."""
    hub = get_audio_hub()
    return hub.health_check()


def get_audio_hub_stats() -> Dict[str, Any]:
    """
Get audio hub performance statistics."""
    hub = get_audio_hub()
    return hub.get_hub_statistics()


# Export main classes and functions
__all__ = [
    # Main hub
    'AudioEngineHub',
    'get_audio_hub',
    
    # Request/Response structures  
    'AudioRequest',
    'AudioResponse',
    'AudioCapability',
    'AudioProcessingMode',
    
    # Convenience functions
    'process_audio',
    'list_audio_capabilities',
    'get_audio_hub_health',
    'get_audio_hub_stats',
]


# Module initialization
logger.info("Audio Engine Hub Index loaded successfully")
logger.info(f"Available audio capabilities: {[cap.value for cap in AudioCapability]}")
logger.info("(c) 2025 Fahed Mlaiel - Professional Audio Intelligence System")
