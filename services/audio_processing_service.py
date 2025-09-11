"""
Audio Processing Service - Professional Audio Engineering & DSP
==============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Audio Engineer & ML Engineer
**Module**: Media Processing Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Professional audio processing with advanced DSP, real-time effects,
format conversion, and intelligent audio analysis for content creators.
"""

import asyncio
import json
import logging
import hashlib
import time
import numpy as np
import wave
import struct
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import aiohttp
import base64
import io
from scipy import signal
from scipy.io import wavfile
import librosa


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
    LOW = "low"          # 64 kbps
    MEDIUM = "medium"    # 128 kbps
    HIGH = "high"        # 256 kbps
    LOSSLESS = "lossless"  # Original quality


class AudioEffect(Enum):
    """Available audio effects"""
    NORMALIZE = "normalize"
    NOISE_REDUCTION = "noise_reduction"
    REVERB = "reverb"
    ECHO = "echo"
    COMPRESSION = "compression"
    EQUALIZATION = "equalization"
    PITCH_SHIFT = "pitch_shift"
    TIME_STRETCH = "time_stretch"
    VOICE_ENHANCEMENT = "voice_enhancement"
    BASS_BOOST = "bass_boost"
    TREBLE_BOOST = "treble_boost"


class ProcessingType(Enum):
    """Types of audio processing"""
    ENHANCEMENT = "enhancement"
    CONVERSION = "conversion"
    ANALYSIS = "analysis"
    EFFECTS = "effects"
    MASTERING = "mastering"
    RESTORATION = "restoration"


@dataclass
class AudioMetadata:
    """Audio file metadata"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: AudioFormat
    file_size: int
    bitrate: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None


@dataclass
class AudioAnalysis:
    """Audio analysis results"""
    rms_level: float
    peak_level: float
    dynamic_range: float
    frequency_spectrum: List[float]
    tempo: Optional[float] = None
    key: Optional[str] = None
    loudness_lufs: Optional[float] = None
    silence_ratio: float = 0.0
    noise_level: float = 0.0
    quality_score: float = 0.0


@dataclass
class ProcessingJob:
    """Audio processing job"""
    job_id: str
    input_file: str
    output_file: str
    processing_type: ProcessingType
    effects: List[AudioEffect]
    parameters: Dict[str, Any]
    status: str = "queued"
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class AudioProcessingResult:
    """Audio processing result"""
    job_id: str
    success: bool
    output_metadata: Optional[AudioMetadata] = None
    analysis: Optional[AudioAnalysis] = None
    processing_time: float = 0.0
    quality_improvement: float = 0.0
    file_size_change: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class AudioProcessingService:
    """
    Professional Audio Processing Service
    
    Enterprise audio processing with:
    - Multi-format conversion and optimization
    - Professional DSP effects and enhancement
    - Real-time audio analysis and quality assessment
    - Intelligent noise reduction and restoration
    - Advanced audio mastering and normalization
    - Content creator optimization tools
    - Batch processing and automation
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Processing queue and jobs
        self.processing_jobs: Dict[str, ProcessingJob] = {}
        self.processing_queue: List[str] = []
        
        # Audio processing parameters
        self.default_sample_rate = 44100
        self.default_bit_depth = 16
        
        # Effect presets
        self.effect_presets = {
            "podcast_voice": {
                AudioEffect.NOISE_REDUCTION: {"strength": 0.7},
                AudioEffect.VOICE_ENHANCEMENT: {"clarity": 0.8},
                AudioEffect.COMPRESSION: {"ratio": 3.0, "threshold": -18},
                AudioEffect.NORMALIZE: {"target_lufs": -16}
            },
            "music_master": {
                AudioEffect.EQUALIZATION: {"low": 1.1, "mid": 1.0, "high": 1.05},
                AudioEffect.COMPRESSION: {"ratio": 2.5, "threshold": -12},
                AudioEffect.NORMALIZE: {"target_lufs": -14}
            },
            "content_creator": {
                AudioEffect.NOISE_REDUCTION: {"strength": 0.5},
                AudioEffect.VOICE_ENHANCEMENT: {"clarity": 0.6},
                AudioEffect.NORMALIZE: {"target_lufs": -18},
                AudioEffect.BASS_BOOST: {"gain": 1.2}
            }
        }
        
        # Performance metrics
        self.processing_metrics = {
            "total_jobs": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "avg_processing_time": 0.0,
            "total_audio_processed": 0.0,  # in seconds
            "quality_improvements": 0.0
        }
        
        # Audio analysis cache
        self.analysis_cache: Dict[str, AudioAnalysis] = {}
        
        self.logger.info("Audio Processing Service initialized")

    async def initialize(self):
        """Initialize audio processing service"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load existing jobs and configuration
            await self._load_processing_jobs()
            
            # Start background processing tasks
            await self._start_processing_tasks()
            
            self.logger.info("Audio Processing Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Audio Processing Service: {e}")
            raise

    async def _start_processing_tasks(self):
        """Start background audio processing tasks"""
        
        # Job processor
        asyncio.create_task(self._process_audio_queue())
        
        # Quality monitoring
        asyncio.create_task(self._monitor_audio_quality())
        
        self.logger.info("Audio processing tasks started")

    async def create_processing_job(self, input_file: str, output_file: str,
                                  processing_type: ProcessingType,
                                  effects: List[AudioEffect],
                                  parameters: Optional[Dict[str, Any]] = None) -> str:
        """Create a new audio processing job"""
        
        job_id = f"audio_{int(time.time() * 1000)}_{hashlib.md5(input_file.encode()).hexdigest()[:8]}"
        
        processing_job = ProcessingJob(
            job_id=job_id,
            input_file=input_file,
            output_file=output_file,
            processing_type=processing_type,
            effects=effects,
            parameters=parameters or {}
        )
        
        # Store job
        self.processing_jobs[job_id] = processing_job
        self.processing_queue.append(job_id)
        
        # Save to Redis
        await self._save_processing_job(processing_job)
        
        self.logger.info(f"Audio processing job created: {job_id}")
        return job_id

    async def apply_preset(self, input_file: str, output_file: str,
                         preset_name: str) -> str:
        """Apply a predefined audio processing preset"""
        
        if preset_name not in self.effect_presets:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        preset = self.effect_presets[preset_name]
        effects = list(preset.keys())
        parameters = {"preset": preset_name, "effects_config": preset}
        
        return await self.create_processing_job(
            input_file,
            output_file,
            ProcessingType.ENHANCEMENT,
            effects,
            parameters
        )

    async def analyze_audio(self, audio_file: str) -> AudioAnalysis:
        """Comprehensive audio analysis"""
        
        try:
            # Check cache first
            file_hash = hashlib.md5(audio_file.encode()).hexdigest()
            if file_hash in self.analysis_cache:
                return self.analysis_cache[file_hash]
            
            # Load audio file
            audio_data, sample_rate = await self._load_audio_file(audio_file)
            
            # Perform analysis
            analysis = await self._perform_audio_analysis(audio_data, sample_rate)
            
            # Cache result
            self.analysis_cache[file_hash] = analysis
            
            # Store in Redis
            await self._save_audio_analysis(file_hash, analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio file {audio_file}: {e}")
            raise

    async def _process_audio_queue(self):
        """Process audio jobs in queue"""
        
        while True:
            try:
                if self.processing_queue:
                    job_id = self.processing_queue.pop(0)
                    
                    if job_id in self.processing_jobs:
                        job = self.processing_jobs[job_id]
                        
                        # Process job
                        result = await self._process_audio_job(job)
                        
                        # Update metrics
                        await self._update_processing_metrics(result)
                
                await asyncio.sleep(1)  # Check queue every second
                
            except Exception as e:
                self.logger.error(f"Error processing audio queue: {e}")
                await asyncio.sleep(5)

    async def _process_audio_job(self, job: ProcessingJob) -> AudioProcessingResult:
        """Process individual audio job"""
        
        start_time = time.time()
        
        try:
            # Update job status
            job.status = "processing"
            job.started_at = datetime.utcnow()
            job.progress = 0.0
            await self._save_processing_job(job)
            
            self.logger.info(f"Processing audio job: {job.job_id}")
            
            # Load input audio
            job.progress = 0.1
            await self._save_processing_job(job)
            
            audio_data, sample_rate = await self._load_audio_file(job.input_file)
            input_metadata = await self._get_audio_metadata(job.input_file, audio_data, sample_rate)
            
            # Initial analysis
            job.progress = 0.2
            await self._save_processing_job(job)
            
            initial_analysis = await self._perform_audio_analysis(audio_data, sample_rate)
            
            # Apply effects and processing
            job.progress = 0.3
            await self._save_processing_job(job)
            
            processed_audio = await self._apply_audio_effects(
                audio_data, sample_rate, job.effects, job.parameters
            )
            
            # Quality enhancement
            job.progress = 0.7
            await self._save_processing_job(job)
            
            enhanced_audio = await self._enhance_audio_quality(
                processed_audio, sample_rate, job.processing_type
            )
            
            # Save output file
            job.progress = 0.9
            await self._save_processing_job(job)
            
            await self._save_audio_file(job.output_file, enhanced_audio, sample_rate)
            
            # Final analysis
            final_analysis = await self._perform_audio_analysis(enhanced_audio, sample_rate)
            output_metadata = await self._get_audio_metadata(job.output_file, enhanced_audio, sample_rate)
            
            # Calculate improvements
            quality_improvement = final_analysis.quality_score - initial_analysis.quality_score
            file_size_change = (output_metadata.file_size - input_metadata.file_size) / input_metadata.file_size
            
            # Generate recommendations
            recommendations = await self._generate_audio_recommendations(
                initial_analysis, final_analysis, job.effects
            )
            
            # Complete job
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.progress = 1.0
            await self._save_processing_job(job)
            
            # Create result
            result = AudioProcessingResult(
                job_id=job.job_id,
                success=True,
                output_metadata=output_metadata,
                analysis=final_analysis,
                processing_time=time.time() - start_time,
                quality_improvement=quality_improvement,
                file_size_change=file_size_change,
                recommendations=recommendations
            )
            
            self.logger.info(f"Audio job completed: {job.job_id}")
            return result
            
        except Exception as e:
            # Mark job as failed
            job.status = "failed"
            job.error_message = str(e)
            await self._save_processing_job(job)
            
            result = AudioProcessingResult(
                job_id=job.job_id,
                success=False,
                processing_time=time.time() - start_time
            )
            
            self.logger.error(f"Audio job failed {job.job_id}: {e}")
            return result

    async def _load_audio_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file into numpy array"""
        
        try:
            # Use librosa for robust audio loading
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=False)
            
            # Ensure audio is in the right format
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)  # Make it 2D (channels, samples)
            
            return audio_data, sample_rate
            
        except Exception as e:
            self.logger.error(f"Error loading audio file {file_path}: {e}")
            raise

    async def _save_audio_file(self, file_path: str, audio_data: np.ndarray, sample_rate: int):
        """Save audio data to file"""
        
        try:
            # Convert to appropriate format for saving
            if audio_data.ndim == 2 and audio_data.shape[0] == 1:
                audio_data = audio_data[0]  # Convert to mono
            
            # Save using librosa
            librosa.output.write_wav(file_path, audio_data, sample_rate)
            
        except Exception as e:
            self.logger.error(f"Error saving audio file {file_path}: {e}")
            raise

    async def _get_audio_metadata(self, file_path: str, audio_data: np.ndarray, 
                                sample_rate: int) -> AudioMetadata:
        """Extract audio metadata"""
        
        try:
            duration = len(audio_data) / sample_rate if audio_data.ndim == 1 else len(audio_data[0]) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[0]
            
            # Get file size
            try:
                import os
                file_size = os.path.getsize(file_path)
            except:
                file_size = 0
            
            # Estimate bit depth and bitrate
            bit_depth = 16  # Default for most audio
            bitrate = int(sample_rate * channels * bit_depth / 1000)  # kbps
            
            metadata = AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=bit_depth,
                format=AudioFormat.WAV,  # Default
                file_size=file_size,
                bitrate=bitrate
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
            raise

    async def _perform_audio_analysis(self, audio_data: np.ndarray, 
                                    sample_rate: int) -> AudioAnalysis:
        """Perform comprehensive audio analysis"""
        
        try:
            # Ensure mono for analysis
            if audio_data.ndim == 2:
                mono_audio = np.mean(audio_data, axis=0)
            else:
                mono_audio = audio_data
            
            # RMS and peak levels
            rms_level = float(np.sqrt(np.mean(mono_audio**2)))
            peak_level = float(np.max(np.abs(mono_audio)))
            
            # Dynamic range (simplified)
            dynamic_range = float(peak_level - rms_level) if peak_level > 0 else 0.0
            
            # Frequency spectrum
            n_fft = min(2048, len(mono_audio))
            fft = np.fft.fft(mono_audio[:n_fft])
            spectrum = np.abs(fft[:n_fft//2])
            frequency_spectrum = spectrum.tolist()
            
            # Tempo detection
            try:
                tempo, _ = librosa.beat.beat_track(y=mono_audio, sr=sample_rate)
                tempo = float(tempo) if not np.isnan(tempo) else None
            except:
                tempo = None
            
            # Key detection (simplified)
            try:
                chroma = librosa.feature.chroma_stft(y=mono_audio, sr=sample_rate)
                key_index = np.argmax(np.sum(chroma, axis=1))
                keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                key = keys[key_index]
            except:
                key = None
            
            # Silence ratio
            silence_threshold = 0.01
            silence_samples = np.sum(np.abs(mono_audio) < silence_threshold)
            silence_ratio = float(silence_samples / len(mono_audio))
            
            # Noise level (high frequency content)
            try:
                noise_level = float(np.mean(spectrum[len(spectrum)//2:]))
            except:
                noise_level = 0.0
            
            # Quality score (composite metric)
            quality_score = await self._calculate_quality_score(
                rms_level, dynamic_range, silence_ratio, noise_level
            )
            
            analysis = AudioAnalysis(
                rms_level=rms_level,
                peak_level=peak_level,
                dynamic_range=dynamic_range,
                frequency_spectrum=frequency_spectrum,
                tempo=tempo,
                key=key,
                silence_ratio=silence_ratio,
                noise_level=noise_level,
                quality_score=quality_score
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error performing audio analysis: {e}")
            raise

    async def _calculate_quality_score(self, rms_level: float, dynamic_range: float,
                                     silence_ratio: float, noise_level: float) -> float:
        """Calculate composite audio quality score"""
        
        try:
            # Normalize metrics to 0-1 range
            rms_score = min(1.0, rms_level * 10)  # Assuming good RMS around 0.1
            
            dynamic_score = min(1.0, dynamic_range * 5)  # Good dynamic range around 0.2
            
            silence_score = 1.0 - min(1.0, silence_ratio * 2)  # Penalize excessive silence
            
            noise_score = 1.0 - min(1.0, noise_level * 100)  # Penalize high noise
            
            # Weighted average
            quality_score = (
                rms_score * 0.3 +
                dynamic_score * 0.3 +
                silence_score * 0.2 +
                noise_score * 0.2
            )
            
            return float(quality_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.5

    async def _apply_audio_effects(self, audio_data: np.ndarray, sample_rate: int,
                                 effects: List[AudioEffect], 
                                 parameters: Dict[str, Any]) -> np.ndarray:
        """Apply audio effects to audio data"""
        
        processed_audio = audio_data.copy()
        
        try:
            for effect in effects:
                processed_audio = await self._apply_single_effect(
                    processed_audio, sample_rate, effect, parameters
                )
            
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Error applying audio effects: {e}")
            raise

    async def _apply_single_effect(self, audio_data: np.ndarray, sample_rate: int,
                                 effect: AudioEffect, parameters: Dict[str, Any]) -> np.ndarray:
        """Apply a single audio effect"""
        
        try:
            if effect == AudioEffect.NORMALIZE:
                return await self._normalize_audio(audio_data, parameters)
            
            elif effect == AudioEffect.NOISE_REDUCTION:
                return await self._reduce_noise(audio_data, sample_rate, parameters)
            
            elif effect == AudioEffect.COMPRESSION:
                return await self._compress_audio(audio_data, parameters)
            
            elif effect == AudioEffect.EQUALIZATION:
                return await self._equalize_audio(audio_data, sample_rate, parameters)
            
            elif effect == AudioEffect.VOICE_ENHANCEMENT:
                return await self._enhance_voice(audio_data, sample_rate, parameters)
            
            elif effect == AudioEffect.BASS_BOOST:
                return await self._boost_bass(audio_data, sample_rate, parameters)
            
            elif effect == AudioEffect.TREBLE_BOOST:
                return await self._boost_treble(audio_data, sample_rate, parameters)
            
            elif effect == AudioEffect.REVERB:
                return await self._add_reverb(audio_data, sample_rate, parameters)
            
            else:
                self.logger.warning(f"Effect {effect.value} not implemented")
                return audio_data
                
        except Exception as e:
            self.logger.error(f"Error applying effect {effect.value}: {e}")
            return audio_data

    async def _normalize_audio(self, audio_data: np.ndarray, 
                             parameters: Dict[str, Any]) -> np.ndarray:
        """Normalize audio levels"""
        
        target_lufs = parameters.get("target_lufs", -18)
        
        # Simple peak normalization (in production, use proper LUFS normalization)
        peak = np.max(np.abs(audio_data))
        if peak > 0:
            # Target peak around 0.8 for headroom
            target_peak = 0.8
            gain = target_peak / peak
            normalized = audio_data * gain
        else:
            normalized = audio_data
        
        return normalized

    async def _reduce_noise(self, audio_data: np.ndarray, sample_rate: int,
                          parameters: Dict[str, Any]) -> np.ndarray:
        """Apply noise reduction"""
        
        strength = parameters.get("strength", 0.5)
        
        # Simple spectral subtraction noise reduction
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # FFT-based noise reduction
        n_fft = 2048
        hop_length = n_fft // 4
        
        # Estimate noise floor from first 0.5 seconds
        noise_samples = int(0.5 * sample_rate)
        noise_spectrum = np.abs(np.fft.fft(mono_audio[:noise_samples], n_fft))
        
        # Process in chunks
        denoised = np.zeros_like(mono_audio)
        for i in range(0, len(mono_audio) - n_fft, hop_length):
            chunk = mono_audio[i:i+n_fft]
            chunk_fft = np.fft.fft(chunk, n_fft)
            chunk_spectrum = np.abs(chunk_fft)
            
            # Spectral subtraction
            gain = np.maximum(0.1, 1.0 - strength * (noise_spectrum / (chunk_spectrum + 1e-10)))
            denoised_fft = chunk_fft * gain
            denoised_chunk = np.real(np.fft.ifft(denoised_fft))
            
            denoised[i:i+n_fft] += denoised_chunk
        
        # Return in original format
        if audio_data.ndim == 2:
            return np.vstack([denoised, denoised])  # Stereo
        else:
            return denoised

    async def _compress_audio(self, audio_data: np.ndarray, 
                            parameters: Dict[str, Any]) -> np.ndarray:
        """Apply audio compression"""
        
        ratio = parameters.get("ratio", 3.0)
        threshold = parameters.get("threshold", -18)  # dB
        
        # Convert threshold from dB to linear
        threshold_linear = 10**(threshold / 20)
        
        # Simple compressor
        compressed = audio_data.copy()
        
        for i in range(len(compressed)):
            if audio_data.ndim == 2:
                for ch in range(audio_data.shape[0]):
                    level = abs(compressed[ch, i])
                    if level > threshold_linear:
                        excess = level - threshold_linear
                        compressed[ch, i] = np.sign(compressed[ch, i]) * (
                            threshold_linear + excess / ratio
                        )
            else:
                level = abs(compressed[i])
                if level > threshold_linear:
                    excess = level - threshold_linear
                    compressed[i] = np.sign(compressed[i]) * (
                        threshold_linear + excess / ratio
                    )
        
        return compressed

    async def _equalize_audio(self, audio_data: np.ndarray, sample_rate: int,
                            parameters: Dict[str, Any]) -> np.ndarray:
        """Apply equalization"""
        
        low_gain = parameters.get("low", 1.0)
        mid_gain = parameters.get("mid", 1.0)
        high_gain = parameters.get("high", 1.0)
        
        # Simple 3-band EQ using filters
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # Define frequency bands
        low_cutoff = 200  # Hz
        high_cutoff = 2000  # Hz
        
        # Low band
        low_sos = signal.butter(4, low_cutoff, btype='low', fs=sample_rate, output='sos')
        low_band = signal.sosfilt(low_sos, mono_audio) * low_gain
        
        # High band  
        high_sos = signal.butter(4, high_cutoff, btype='high', fs=sample_rate, output='sos')
        high_band = signal.sosfilt(high_sos, mono_audio) * high_gain
        
        # Mid band
        mid_sos = signal.butter(4, [low_cutoff, high_cutoff], btype='band', fs=sample_rate, output='sos')
        mid_band = signal.sosfilt(mid_sos, mono_audio) * mid_gain
        
        # Combine bands
        equalized = low_band + mid_band + high_band
        
        # Return in original format
        if audio_data.ndim == 2:
            return np.vstack([equalized, equalized])
        else:
            return equalized

    async def _enhance_voice(self, audio_data: np.ndarray, sample_rate: int,
                           parameters: Dict[str, Any]) -> np.ndarray:
        """Enhance voice quality"""
        
        clarity = parameters.get("clarity", 0.7)
        
        # Voice enhancement typically focuses on 300-3000 Hz range
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # Bandpass filter for voice frequencies
        voice_sos = signal.butter(4, [300, 3000], btype='band', fs=sample_rate, output='sos')
        voice_enhanced = signal.sosfilt(voice_sos, mono_audio)
        
        # Blend with original
        enhanced = mono_audio * (1 - clarity) + voice_enhanced * clarity
        
        # Return in original format
        if audio_data.ndim == 2:
            return np.vstack([enhanced, enhanced])
        else:
            return enhanced

    async def _boost_bass(self, audio_data: np.ndarray, sample_rate: int,
                        parameters: Dict[str, Any]) -> np.ndarray:
        """Boost bass frequencies"""
        
        gain = parameters.get("gain", 1.2)
        
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # Low shelf filter for bass boost
        bass_sos = signal.butter(4, 200, btype='low', fs=sample_rate, output='sos')
        bass_boosted = signal.sosfilt(bass_sos, mono_audio) * gain
        
        # High pass to preserve original highs
        high_sos = signal.butter(4, 200, btype='high', fs=sample_rate, output='sos')
        highs = signal.sosfilt(high_sos, mono_audio)
        
        enhanced = bass_boosted + highs
        
        if audio_data.ndim == 2:
            return np.vstack([enhanced, enhanced])
        else:
            return enhanced

    async def _boost_treble(self, audio_data: np.ndarray, sample_rate: int,
                          parameters: Dict[str, Any]) -> np.ndarray:
        """Boost treble frequencies"""
        
        gain = parameters.get("gain", 1.2)
        
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # High shelf filter for treble boost
        treble_sos = signal.butter(4, 2000, btype='high', fs=sample_rate, output='sos')
        treble_boosted = signal.sosfilt(treble_sos, mono_audio) * gain
        
        # Low pass to preserve original lows
        low_sos = signal.butter(4, 2000, btype='low', fs=sample_rate, output='sos')
        lows = signal.sosfilt(low_sos, mono_audio)
        
        enhanced = lows + treble_boosted
        
        if audio_data.ndim == 2:
            return np.vstack([enhanced, enhanced])
        else:
            return enhanced

    async def _add_reverb(self, audio_data: np.ndarray, sample_rate: int,
                        parameters: Dict[str, Any]) -> np.ndarray:
        """Add reverb effect"""
        
        room_size = parameters.get("room_size", 0.5)
        decay = parameters.get("decay", 0.3)
        
        # Simple reverb using delays and feedback
        if audio_data.ndim == 2:
            mono_audio = np.mean(audio_data, axis=0)
        else:
            mono_audio = audio_data
        
        # Create impulse response for reverb
        delay_samples = int(room_size * sample_rate * 0.1)  # Max 100ms delay
        impulse_length = int(decay * sample_rate)
        
        impulse = np.zeros(impulse_length)
        for i in range(0, impulse_length, delay_samples):
            if i < impulse_length:
                impulse[i] = (1 - i / impulse_length) * 0.3
        
        # Apply reverb
        reverb = signal.convolve(mono_audio, impulse, mode='same')
        
        if audio_data.ndim == 2:
            return np.vstack([reverb, reverb])
        else:
            return reverb

    async def _enhance_audio_quality(self, audio_data: np.ndarray, sample_rate: int,
                                   processing_type: ProcessingType) -> np.ndarray:
        """Apply final quality enhancement based on processing type"""
        
        if processing_type == ProcessingType.MASTERING:
            # Apply mastering chain
            enhanced = await self._apply_mastering_chain(audio_data, sample_rate)
        elif processing_type == ProcessingType.RESTORATION:
            # Apply restoration techniques
            enhanced = await self._apply_restoration(audio_data, sample_rate)
        else:
            # Basic enhancement
            enhanced = await self._apply_basic_enhancement(audio_data, sample_rate)
        
        return enhanced

    async def _apply_mastering_chain(self, audio_data: np.ndarray, 
                                   sample_rate: int) -> np.ndarray:
        """Apply professional mastering chain"""
        
        # Mastering chain: EQ -> Compression -> Limiting
        enhanced = audio_data.copy()
        
        # Gentle EQ
        enhanced = await self._equalize_audio(
            enhanced, sample_rate, 
            {"low": 1.05, "mid": 1.0, "high": 1.03}
        )
        
        # Gentle compression
        enhanced = await self._compress_audio(
            enhanced, 
            {"ratio": 2.0, "threshold": -12}
        )
        
        # Final normalization
        enhanced = await self._normalize_audio(
            enhanced, 
            {"target_lufs": -14}
        )
        
        return enhanced

    async def _apply_restoration(self, audio_data: np.ndarray, 
                               sample_rate: int) -> np.ndarray:
        """Apply audio restoration techniques"""
        
        # Restoration: Noise reduction -> Click removal -> Enhancement
        enhanced = audio_data.copy()
        
        # Aggressive noise reduction
        enhanced = await self._reduce_noise(
            enhanced, sample_rate, 
            {"strength": 0.8}
        )
        
        # Voice enhancement if present
        enhanced = await self._enhance_voice(
            enhanced, sample_rate, 
            {"clarity": 0.6}
        )
        
        return enhanced

    async def _apply_basic_enhancement(self, audio_data: np.ndarray, 
                                     sample_rate: int) -> np.ndarray:
        """Apply basic audio enhancement"""
        
        enhanced = audio_data.copy()
        
        # Basic enhancement: Normalize -> Light compression
        enhanced = await self._normalize_audio(enhanced, {"target_lufs": -18})
        enhanced = await self._compress_audio(enhanced, {"ratio": 2.5, "threshold": -15})
        
        return enhanced

    async def _generate_audio_recommendations(self, initial_analysis: AudioAnalysis,
                                            final_analysis: AudioAnalysis,
                                            effects_applied: List[AudioEffect]) -> List[str]:
        """Generate recommendations based on audio analysis"""
        
        recommendations = []
        
        # Quality improvement recommendations
        if final_analysis.quality_score > initial_analysis.quality_score:
            improvement = (final_analysis.quality_score - initial_analysis.quality_score) * 100
            recommendations.append(f"Audio quality improved by {improvement:.1f}%")
        
        # Dynamic range recommendations
        if final_analysis.dynamic_range < 0.1:
            recommendations.append("Consider reducing compression to preserve dynamic range")
        
        # Noise level recommendations
        if final_analysis.noise_level > 0.05:
            recommendations.append("Apply stronger noise reduction for cleaner audio")
        
        # Silence ratio recommendations
        if final_analysis.silence_ratio > 0.3:
            recommendations.append("Consider trimming excessive silence for better engagement")
        
        # Effect-specific recommendations
        if AudioEffect.VOICE_ENHANCEMENT not in effects_applied and final_analysis.quality_score < 0.7:
            recommendations.append("Voice enhancement could improve clarity")
        
        if AudioEffect.NORMALIZE not in effects_applied:
            recommendations.append("Normalization would ensure consistent loudness")
        
        return recommendations

    async def _monitor_audio_quality(self):
        """Monitor audio quality across processed files"""
        
        while True:
            try:
                # Calculate average quality metrics
                if self.analysis_cache:
                    avg_quality = np.mean([a.quality_score for a in self.analysis_cache.values()])
                    avg_noise = np.mean([a.noise_level for a in self.analysis_cache.values()])
                    
                    # Store quality metrics
                    await self.redis_client.setex(
                        "audio_quality_metrics",
                        3600,
                        json.dumps({
                            "avg_quality_score": avg_quality,
                            "avg_noise_level": avg_noise,
                            "total_files_analyzed": len(self.analysis_cache),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring audio quality: {e}")
                await asyncio.sleep(600)

    async def _update_processing_metrics(self, result: AudioProcessingResult):
        """Update processing metrics"""
        
        self.processing_metrics["total_jobs"] += 1
        
        if result.success:
            self.processing_metrics["successful_jobs"] += 1
            
            # Update average processing time
            current_avg = self.processing_metrics["avg_processing_time"]
            total_jobs = self.processing_metrics["successful_jobs"]
            
            self.processing_metrics["avg_processing_time"] = (
                (current_avg * (total_jobs - 1) + result.processing_time) / total_jobs
            )
            
            # Update quality improvements
            if result.quality_improvement > 0:
                self.processing_metrics["quality_improvements"] += result.quality_improvement
        else:
            self.processing_metrics["failed_jobs"] += 1

    # Redis persistence methods
    
    async def _save_processing_job(self, job: ProcessingJob):
        """Save processing job to Redis"""
        
        job_data = {
            "job_id": job.job_id,
            "input_file": job.input_file,
            "output_file": job.output_file,
            "processing_type": job.processing_type.value,
            "effects": [effect.value for effect in job.effects],
            "parameters": job.parameters,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
        
        await self.redis_client.setex(
            f"audio_job:{job.job_id}",
            86400,  # 24 hours
            json.dumps(job_data)
        )

    async def _load_processing_jobs(self):
        """Load processing jobs from Redis"""
        
        try:
            job_keys = await self.redis_client.keys("audio_job:*")
            
            for key in job_keys:
                job_data = await self.redis_client.get(key)
                if job_data:
                    data = json.loads(job_data)
                    
                    # Only load incomplete jobs
                    if data["status"] in ["queued", "processing"]:
                        effects = [AudioEffect(effect) for effect in data["effects"]]
                        
                        job = ProcessingJob(
                            job_id=data["job_id"],
                            input_file=data["input_file"],
                            output_file=data["output_file"],
                            processing_type=ProcessingType(data["processing_type"]),
                            effects=effects,
                            parameters=data["parameters"],
                            status=data["status"],
                            progress=data["progress"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            started_at=datetime.fromisoformat(data["started_at"]) if data["started_at"] else None,
                            completed_at=datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None,
                            error_message=data["error_message"]
                        )
                        
                        self.processing_jobs[job.job_id] = job
                        
                        if job.status == "queued":
                            self.processing_queue.append(job.job_id)
            
            self.logger.info(f"Loaded {len(self.processing_jobs)} audio processing jobs")
        
        except Exception as e:
            self.logger.warning(f"Could not load processing jobs: {e}")

    async def _save_audio_analysis(self, file_hash: str, analysis: AudioAnalysis):
        """Save audio analysis to Redis"""
        
        analysis_data = {
            "rms_level": analysis.rms_level,
            "peak_level": analysis.peak_level,
            "dynamic_range": analysis.dynamic_range,
            "frequency_spectrum": analysis.frequency_spectrum,
            "tempo": analysis.tempo,
            "key": analysis.key,
            "loudness_lufs": analysis.loudness_lufs,
            "silence_ratio": analysis.silence_ratio,
            "noise_level": analysis.noise_level,
            "quality_score": analysis.quality_score
        }
        
        await self.redis_client.setex(
            f"audio_analysis:{file_hash}",
            3600,  # 1 hour
            json.dumps(analysis_data)
        )

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        
        if job_id in self.processing_jobs:
            job = self.processing_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "error_message": job.error_message
            }
        
        return None

    async def get_audio_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive audio processing dashboard"""
        
        # Job statistics
        job_stats = {
            "total_jobs": len(self.processing_jobs),
            "queued": len([j for j in self.processing_jobs.values() if j.status == "queued"]),
            "processing": len([j for j in self.processing_jobs.values() if j.status == "processing"]),
            "completed": len([j for j in self.processing_jobs.values() if j.status == "completed"]),
            "failed": len([j for j in self.processing_jobs.values() if j.status == "failed"])
        }
        
        return {
            "job_statistics": job_stats,
            "processing_metrics": self.processing_metrics,
            "available_effects": [effect.value for effect in AudioEffect],
            "available_presets": list(self.effect_presets.keys()),
            "analysis_cache_size": len(self.analysis_cache),
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown audio processing service"""
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Audio Processing Service shutdown completed")


# Example usage
async def main():
    """Example usage of Audio Processing Service"""
    
    processor = AudioProcessingService()
    await processor.initialize()
    
    try:
        # Example: Apply podcast preset
        job_id = await processor.apply_preset(
            "input_audio.wav",
            "output_audio.wav",
            "podcast_voice"
        )
        
        print(f"Processing job created: {job_id}")
        
        # Wait for processing
        await asyncio.sleep(5)
        
        # Check status
        status = await processor.get_job_status(job_id)
        print(f"Job status: {status}")
        
        # Get dashboard
        dashboard = await processor.get_audio_dashboard()
        print(f"Audio dashboard: {dashboard}")
        
    finally:
        await processor.shutdown()


if __name__ == "__main__":
    asyncio.run(main())