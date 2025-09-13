"""
🎵 ADVANCED AUDIO PROCESSING TEMPLATE - AUDIO ENGINEER EXPERT IMPLEMENTATION
===========================================================================

Enterprise-grade audio processing template with:
- Real-time audio processing and streaming
- Multi-format audio encoding/decoding
- Advanced DSP algorithms and effects
- Audio transcription and speech recognition
- Music analysis and feature extraction
- Spatial audio and 3D sound processing
- Professional audio mixing and mastering
- Audio fingerprinting and copyright detection

Author: Audio Engineer Expert
Version: 1.0.0
"""

import asyncio
import logging
import numpy as np
import scipy.signal as signal
import librosa
import soundfile as sf
import pyaudio
import wave
import threading
import queue
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import subprocess
import tempfile
import io
import base64
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
import aiofiles
import httpx
from concurrent.futures import ThreadPoolExecutor
import websockets
import uvloop
import torch
import torchaudio
import transformers
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import whisper
import openai
import pyloudnorm as pyln
import essentia
import essentia.standard as es
from scipy.fft import fft, ifft, fftfreq
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import replace


class AudioFormat:
    """Audio format enumeration"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WEBM = "webm"
    PCM = "pcm"


class AudioQuality:
    """Audio quality enumeration"""
    LOW = "low"          # 64 kbps
    MEDIUM = "medium"    # 128 kbps
    HIGH = "high"        # 256 kbps
    LOSSLESS = "lossless"  # Original quality


class ProcessingMode:
    """Audio processing mode"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    # Basic audio settings
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    buffer_size: int = 1024
    
    # Processing settings
    processing_mode: ProcessingMode = ProcessingMode.BATCH
    enable_real_time: bool = False
    max_duration_seconds: int = 3600  # 1 hour max
    
    # Quality settings
    default_quality: AudioQuality = AudioQuality.HIGH
    enable_normalization: bool = True
    target_lufs: float = -23.0  # EBU R128 standard
    
    # AI/ML settings
    enable_transcription: bool = True
    transcription_model: str = "whisper-base"
    enable_music_analysis: bool = True
    enable_noise_reduction: bool = True
    
    # Effects and processing
    enable_eq: bool = True
    enable_compressor: bool = True
    enable_reverb: bool = False
    enable_spatial_audio: bool = False
    
    # Real-time settings
    latency_ms: int = 10
    enable_monitoring: bool = True
    
    # Storage and caching
    temp_dir: str = "/tmp/audio_processing"
    cache_processed_audio: bool = True
    cache_ttl_hours: int = 24
    
    # External services
    redis_url: str = "redis://localhost:6379"
    enable_cloud_processing: bool = False
    cloud_provider: str = "aws"  # aws, gcp, azure


@dataclass
class AudioMetadata:
    """Audio file metadata"""
    filename: str
    format: str
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    file_size: int
    
    # Technical metadata
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    lufs: Optional[float] = None
    peak_level: Optional[float] = None
    dynamic_range: Optional[float] = None
    
    # Content metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    
    # Processing metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processing_time_ms: Optional[float] = None
    
    # Analysis results
    tempo: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    danceability: Optional[float] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    
    # Fingerprinting
    audio_fingerprint: Optional[str] = None
    chromaprint: Optional[str] = None


class AudioBuffer:
    """Thread-safe audio buffer for real-time processing"""
    
    def __init__(self, max_size: int = 8192):
        self.buffer = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
        self.overflow_count = 0
    
    def put(self, data: np.ndarray) -> bool:
        """Add audio data to buffer"""
        try:
            self.buffer.put_nowait(data)
            return True
        except queue.Full:
            with self.lock:
                self.overflow_count += 1
            return False
    
    def get(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Get audio data from buffer"""
        try:
            return self.buffer.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def clear(self):
        """Clear buffer"""
        with self.lock:
            while not self.buffer.empty():
                try:
                    self.buffer.get_nowait()
                except queue.Empty:
                    break
    
    def size(self) -> int:
        """Get current buffer size"""
        return self.buffer.qsize()


class AudioProcessor:
    """Core audio processing engine"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(config.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize audio processing components
        self.eq_filter = None
        self.compressor = None
        self.loudness_meter = pyln.Meter(config.sample_rate)
        
        # Real-time processing
        self.audio_buffer = AudioBuffer()
        self.pyaudio_instance = None
        self.stream = None
        self.processing_thread = None
        self.is_processing = False
        
        # ML models
        self.transcription_model = None
        self.music_analyzer = None
        
    async def initialize(self):
        """Initialize audio processor"""
        # Load transcription model if enabled
        if self.config.enable_transcription:
            await self._load_transcription_model()
        
        # Initialize music analysis if enabled
        if self.config.enable_music_analysis:
            self._initialize_music_analyzer()
        
        # Setup real-time processing if enabled
        if self.config.enable_real_time:
            self._setup_real_time_processing()
        
        self.logger.info("Audio processor initialized")
    
    async def _load_transcription_model(self):
        """Load speech recognition model"""
        try:
            if self.config.transcription_model.startswith("whisper"):
                model_size = self.config.transcription_model.split("-")[1]
                self.transcription_model = whisper.load_model(model_size)
            else:
                # Load Wav2Vec2 model
                self.transcription_model = Wav2Vec2ForCTC.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
                self.tokenizer = Wav2Vec2Tokenizer.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
            
            self.logger.info(f"Loaded transcription model: {self.config.transcription_model}")
        except Exception as e:
            self.logger.error(f"Failed to load transcription model: {e}")
    
    def _initialize_music_analyzer(self):
        """Initialize music analysis components"""
        try:
            # Essentia extractors
            self.beat_tracker = es.BeatTrackerMultiFeature()
            self.key_extractor = es.KeyExtractor()
            self.spectral_features = es.SpectralCentroid()
            self.mfcc = es.MFCC()
            self.chroma = es.ChromaCrossSimilarity()
            
            self.logger.info("Music analyzer initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize music analyzer: {e}")
    
    def _setup_real_time_processing(self):
        """Setup real-time audio processing"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Get default input device
            device_info = self.pyaudio_instance.get_default_input_device_info()
            
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.buffer_size,
                stream_callback=self._audio_callback
            )
            
            self.logger.info("Real-time audio processing setup complete")
        except Exception as e:
            self.logger.error(f"Failed to setup real-time processing: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Real-time audio callback"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Add to buffer for processing
        self.audio_buffer.put(audio_data)
        
        return (None, pyaudio.paContinue)
    
    async def process_file(self, input_path: str, output_path: str = None, **kwargs) -> AudioMetadata:
        """Process audio file"""
        start_time = time.time()
        
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(
                input_path,
                sr=self.config.sample_rate,
                mono=self.config.channels == 1
            )
            
            # Get basic metadata
            metadata = self._extract_basic_metadata(input_path, audio_data, sample_rate)
            
            # Process audio
            processed_audio = await self._process_audio_data(audio_data, sample_rate, **kwargs)
            
            # Save processed audio if output path provided
            if output_path:
                await self._save_audio(processed_audio, output_path, sample_rate)
            
            # Update metadata
            processing_time = (time.time() - start_time) * 1000
            metadata.processed_at = datetime.utcnow()
            metadata.processing_time_ms = processing_time
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error processing file {input_path}: {e}")
            raise
    
    async def _process_audio_data(self, audio_data: np.ndarray, sample_rate: int, **kwargs) -> np.ndarray:
        """Process audio data with various effects and enhancements"""
        processed = audio_data.copy()
        
        # Noise reduction
        if self.config.enable_noise_reduction:
            processed = self._reduce_noise(processed, sample_rate)
        
        # Normalization
        if self.config.enable_normalization:
            processed = self._normalize_loudness(processed, sample_rate)
        
        # EQ
        if self.config.enable_eq and kwargs.get('eq_settings'):
            processed = self._apply_eq(processed, sample_rate, kwargs['eq_settings'])
        
        # Compression
        if self.config.enable_compressor and kwargs.get('compressor_settings'):
            processed = self._apply_compression(processed, sample_rate, kwargs['compressor_settings'])
        
        # Reverb
        if self.config.enable_reverb and kwargs.get('reverb_settings'):
            processed = self._apply_reverb(processed, sample_rate, kwargs['reverb_settings'])
        
        # Spatial audio
        if self.config.enable_spatial_audio and kwargs.get('spatial_settings'):
            processed = self._apply_spatial_processing(processed, sample_rate, kwargs['spatial_settings'])
        
        return processed
    
    def _extract_basic_metadata(self, file_path: str, audio_data: np.ndarray, sample_rate: int) -> AudioMetadata:
        """Extract basic audio metadata"""
        file_path_obj = Path(file_path)
        
        # Basic file info
        metadata = AudioMetadata(
            filename=file_path_obj.name,
            format=file_path_obj.suffix[1:].lower(),
            duration=len(audio_data) / sample_rate,
            sample_rate=sample_rate,
            channels=1 if audio_data.ndim == 1 else audio_data.shape[0],
            bit_depth=32,  # librosa loads as float32
            file_size=file_path_obj.stat().st_size
        )
        
        # Audio analysis
        try:
            # Loudness measurement
            if audio_data.ndim == 1:
                audio_for_loudness = audio_data.reshape(-1, 1)
            else:
                audio_for_loudness = audio_data.T
            
            metadata.lufs = self.loudness_meter.integrated_loudness(audio_for_loudness)
            metadata.peak_level = np.max(np.abs(audio_data))
            
            # Basic music analysis
            if self.config.enable_music_analysis:
                metadata = self._analyze_music_features(audio_data, sample_rate, metadata)
            
            # Audio fingerprinting
            metadata.audio_fingerprint = self._generate_audio_fingerprint(audio_data)
            
        except Exception as e:
            self.logger.warning(f"Error in metadata extraction: {e}")
        
        return metadata
    
    def _analyze_music_features(self, audio_data: np.ndarray, sample_rate: int, metadata: AudioMetadata) -> AudioMetadata:
        """Analyze music features"""
        try:
            # Tempo detection
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            metadata.tempo = float(tempo)
            
            # Key detection using chromagram
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            key_profile = np.sum(chroma, axis=1)
            key_idx = np.argmax(key_profile)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            metadata.key = keys[key_idx]
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            metadata.energy = float(np.mean(spectral_centroids))
            
            # MFCCs for content analysis
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Simple heuristics for music characteristics
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Estimate characteristics based on audio features
            metadata.danceability = min(1.0, tempo / 140.0) if tempo else None
            metadata.energy = float(np.mean(spectral_centroids) / (sample_rate / 2))
            metadata.acousticness = 1.0 - float(np.mean(spectral_rolloff) / (sample_rate / 2))
            metadata.speechiness = float(np.mean(zero_crossing_rate))
            
        except Exception as e:
            self.logger.warning(f"Error in music analysis: {e}")
        
        return metadata
    
    def _generate_audio_fingerprint(self, audio_data: np.ndarray) -> str:
        """Generate audio fingerprint"""
        try:
            # Simple spectral fingerprint
            stft = np.abs(librosa.stft(audio_data))
            fingerprint = np.mean(stft, axis=1)
            
            # Normalize and quantize
            fingerprint = fingerprint / np.max(fingerprint)
            fingerprint_bytes = (fingerprint * 255).astype(np.uint8).tobytes()
            
            return hashlib.md5(fingerprint_bytes).hexdigest()
        except Exception as e:
            self.logger.warning(f"Error generating fingerprint: {e}")
            return ""
    
    def _reduce_noise(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply noise reduction"""
        try:
            # Simple spectral gating noise reduction
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Apply gating
            gate_threshold = noise_floor * 3
            mask = magnitude > gate_threshold
            
            # Apply soft gating
            magnitude_cleaned = magnitude * mask
            
            # Reconstruct
            stft_cleaned = magnitude_cleaned * np.exp(1j * phase)
            audio_cleaned = librosa.istft(stft_cleaned)
            
            return audio_cleaned
        except Exception as e:
            self.logger.warning(f"Error in noise reduction: {e}")
            return audio_data
    
    def _normalize_loudness(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Normalize audio loudness to target LUFS"""
        try:
            # Prepare audio for loudness measurement
            if audio_data.ndim == 1:
                audio_for_loudness = audio_data.reshape(-1, 1)
            else:
                audio_for_loudness = audio_data.T
            
            # Measure current loudness
            current_lufs = self.loudness_meter.integrated_loudness(audio_for_loudness)
            
            if current_lufs > -70:  # Valid measurement
                # Calculate gain needed
                gain_db = self.config.target_lufs - current_lufs
                gain_linear = 10 ** (gain_db / 20)
                
                # Apply gain with limiting
                normalized = audio_data * gain_linear
                
                # Peak limiting
                peak = np.max(np.abs(normalized))
                if peak > 0.95:
                    normalized = normalized * (0.95 / peak)
                
                return normalized
            
            return audio_data
        except Exception as e:
            self.logger.warning(f"Error in loudness normalization: {e}")
            return audio_data
    
    def _apply_eq(self, audio_data: np.ndarray, sample_rate: int, eq_settings: Dict) -> np.ndarray:
        """Apply equalizer"""
        try:
            # Simple parametric EQ implementation
            processed = audio_data.copy()
            
            for band in eq_settings.get('bands', []):
                frequency = band.get('frequency', 1000)
                gain_db = band.get('gain', 0)
                q_factor = band.get('q', 1.0)
                
                if gain_db != 0:
                    # Design filter
                    gain_linear = 10 ** (gain_db / 20)
                    sos = signal.iirpeak(frequency, q_factor, sample_rate)
                    
                    # Apply filter
                    if gain_db > 0:
                        # Boost
                        filtered = signal.sosfilt(sos, processed)
                        processed = processed + (filtered - processed) * (gain_linear - 1)
                    else:
                        # Cut
                        filtered = signal.sosfilt(sos, processed)
                        processed = processed - (filtered - processed) * (1 - gain_linear)
            
            return processed
        except Exception as e:
            self.logger.warning(f"Error in EQ processing: {e}")
            return audio_data
    
    def _apply_compression(self, audio_data: np.ndarray, sample_rate: int, compressor_settings: Dict) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            threshold = compressor_settings.get('threshold', -20)  # dB
            ratio = compressor_settings.get('ratio', 4.0)
            attack_ms = compressor_settings.get('attack_ms', 5)
            release_ms = compressor_settings.get('release_ms', 50)
            
            # Convert to linear
            threshold_linear = 10 ** (threshold / 20)
            
            # Calculate attack and release coefficients
            attack_coeff = np.exp(-1 / (attack_ms * 0.001 * sample_rate))
            release_coeff = np.exp(-1 / (release_ms * 0.001 * sample_rate))
            
            # Simple peak compressor
            envelope = 0
            compressed = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Envelope follower
                abs_sample = abs(sample)
                if abs_sample > envelope:
                    envelope = abs_sample + (envelope - abs_sample) * attack_coeff
                else:
                    envelope = abs_sample + (envelope - abs_sample) * release_coeff
                
                # Compression
                if envelope > threshold_linear:
                    # Calculate compression gain
                    over_threshold = envelope / threshold_linear
                    compressed_gain = threshold_linear * (over_threshold ** (1/ratio - 1))
                    gain = compressed_gain / envelope if envelope > 0 else 1
                else:
                    gain = 1
                
                compressed[i] = sample * gain
            
            return compressed
        except Exception as e:
            self.logger.warning(f"Error in compression: {e}")
            return audio_data
    
    def _apply_reverb(self, audio_data: np.ndarray, sample_rate: int, reverb_settings: Dict) -> np.ndarray:
        """Apply reverb effect"""
        try:
            room_size = reverb_settings.get('room_size', 0.5)
            damping = reverb_settings.get('damping', 0.5)
            wet_level = reverb_settings.get('wet_level', 0.3)
            
            # Simple Schroeder reverb implementation
            # Comb filters
            comb_delays = [int(0.03 * sample_rate), int(0.05 * sample_rate), 
                          int(0.07 * sample_rate), int(0.09 * sample_rate)]
            
            reverb_signal = np.zeros_like(audio_data)
            
            for delay in comb_delays:
                delay = int(delay * room_size)
                feedback = 0.7 * (1 - damping)
                
                # Comb filter
                comb_output = np.zeros_like(audio_data)
                delay_line = np.zeros(delay)
                
                for i in range(len(audio_data)):
                    delayed_sample = delay_line[0]
                    comb_output[i] = audio_data[i] + feedback * delayed_sample
                    
                    # Shift delay line
                    delay_line[:-1] = delay_line[1:]
                    delay_line[-1] = comb_output[i]
                
                reverb_signal += comb_output / len(comb_delays)
            
            # Mix wet and dry signals
            return audio_data * (1 - wet_level) + reverb_signal * wet_level
            
        except Exception as e:
            self.logger.warning(f"Error in reverb processing: {e}")
            return audio_data
    
    def _apply_spatial_processing(self, audio_data: np.ndarray, sample_rate: int, spatial_settings: Dict) -> np.ndarray:
        """Apply spatial audio processing"""
        try:
            # Simple binaural processing for stereo enhancement
            if audio_data.ndim == 1:
                # Convert mono to pseudo-stereo
                stereo = np.zeros((2, len(audio_data)))
                
                # Apply simple HRTF-inspired filtering
                # Left channel
                stereo[0] = audio_data
                
                # Right channel with slight delay and filtering
                delay_samples = int(0.0005 * sample_rate)  # 0.5ms delay
                if delay_samples < len(audio_data):
                    stereo[1, delay_samples:] = audio_data[:-delay_samples]
                    
                    # Apply simple high-frequency roll-off for right channel
                    sos = signal.butter(4, 8000, 'low', fs=sample_rate, output='sos')
                    stereo[1] = signal.sosfilt(sos, stereo[1])
                
                return stereo
            
            return audio_data
        except Exception as e:
            self.logger.warning(f"Error in spatial processing: {e}")
            return audio_data
    
    async def _save_audio(self, audio_data: np.ndarray, output_path: str, sample_rate: int):
        """Save processed audio to file"""
        try:
            output_path_obj = Path(output_path)
            output_format = output_path_obj.suffix[1:].lower()
            
            if output_format in ['wav', 'flac']:
                sf.write(output_path, audio_data.T if audio_data.ndim > 1 else audio_data, sample_rate)
            else:
                # Use ffmpeg for other formats
                temp_wav = self.temp_dir / f"temp_{uuid.uuid4().hex}.wav"
                sf.write(temp_wav, audio_data.T if audio_data.ndim > 1 else audio_data, sample_rate)
                
                # Convert with ffmpeg
                subprocess.run([
                    'ffmpeg', '-i', str(temp_wav), '-y', output_path
                ], check=True, capture_output=True)
                
                # Clean up temp file
                temp_wav.unlink()
                
        except Exception as e:
            self.logger.error(f"Error saving audio to {output_path}: {e}")
            raise
    
    async def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int, language: str = "auto") -> Dict[str, Any]:
        """Transcribe audio to text"""
        if not self.config.enable_transcription or not self.transcription_model:
            return {"text": "", "confidence": 0.0, "segments": []}
        
        try:
            # Prepare audio for transcription
            if sample_rate != 16000:
                audio_16k = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
            else:
                audio_16k = audio_data
            
            if hasattr(self.transcription_model, 'transcribe'):
                # Whisper model
                result = self.transcription_model.transcribe(audio_16k, language=language if language != "auto" else None)
                
                return {
                    "text": result["text"],
                    "confidence": 0.95,  # Whisper doesn't provide confidence scores
                    "segments": result.get("segments", []),
                    "language": result.get("language", "unknown")
                }
            else:
                # Wav2Vec2 model
                input_values = self.tokenizer(audio_16k, return_tensors="pt", sampling_rate=16000).input_values
                
                with torch.no_grad():
                    logits = self.transcription_model(input_values).logits
                
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.tokenizer.batch_decode(predicted_ids)[0]
                
                return {
                    "text": transcription,
                    "confidence": 0.8,
                    "segments": [],
                    "language": "en"
                }
                
        except Exception as e:
            self.logger.error(f"Error in transcription: {e}")
            return {"text": "", "confidence": 0.0, "segments": [], "error": str(e)}
    
    async def detect_copyright(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Detect potential copyright content"""
        try:
            # Generate audio fingerprint
            fingerprint = self._generate_detailed_fingerprint(audio_data, sample_rate)
            
            # In a real implementation, this would check against a copyright database
            # For now, return a mock result
            return {
                "fingerprint": fingerprint,
                "matches": [],
                "copyright_detected": False,
                "confidence": 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error in copyright detection: {e}")
            return {"error": str(e)}
    
    def _generate_detailed_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate detailed audio fingerprint for copyright detection"""
        try:
            # Use chromaprint-style fingerprinting
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            
            # Quantize and create hash
            chroma_quantized = (chroma > np.mean(chroma, axis=1, keepdims=True)).astype(int)
            fingerprint_bits = chroma_quantized.flatten()
            
            # Convert to hex string
            fingerprint_bytes = np.packbits(fingerprint_bits[:len(fingerprint_bits)//8*8])
            return fingerprint_bytes.tobytes().hex()
            
        except Exception as e:
            self.logger.error(f"Error generating detailed fingerprint: {e}")
            return ""
    
    def start_real_time_processing(self):
        """Start real-time audio processing"""
        if not self.config.enable_real_time or self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._real_time_processing_loop)
        self.processing_thread.start()
        
        if self.stream:
            self.stream.start_stream()
        
        self.logger.info("Started real-time audio processing")
    
    def stop_real_time_processing(self):
        """Stop real-time audio processing"""
        self.is_processing = False
        
        if self.stream:
            self.stream.stop_stream()
        
        if self.processing_thread:
            self.processing_thread.join()
        
        self.logger.info("Stopped real-time audio processing")
    
    def _real_time_processing_loop(self):
        """Real-time processing loop"""
        while self.is_processing:
            audio_chunk = self.audio_buffer.get(timeout=0.1)
            
            if audio_chunk is not None:
                try:
                    # Process audio chunk
                    processed_chunk = asyncio.run(
                        self._process_audio_data(audio_chunk, self.config.sample_rate)
                    )
                    
                    # Here you would output the processed audio
                    # For now, we just log it
                    if self.config.enable_monitoring:
                        level = np.max(np.abs(processed_chunk))
                        if level > 0.1:  # Only log significant levels
                            self.logger.debug(f"Processed audio level: {level:.3f}")
                            
                except Exception as e:
                    self.logger.error(f"Error in real-time processing: {e}")
            
            time.sleep(0.001)  # Small delay to prevent busy waiting
    
    async def cleanup(self):
        """Cleanup audio processor"""
        self.stop_real_time_processing()
        
        if self.stream:
            self.stream.close()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        
        self.logger.info("Audio processor cleaned up")


class AudioStreamServer:
    """WebSocket server for real-time audio streaming"""
    
    def __init__(self, config: AudioConfig, processor: AudioProcessor):
        self.config = config
        self.processor = processor
        self.clients = set()
        self.logger = logging.getLogger(__name__)
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server"""
        self.logger.info(f"Starting audio stream server on {host}:{port}")
        
        async def handle_client(websocket, path):
            self.clients.add(websocket)
            try:
                await self._handle_audio_stream(websocket)
            finally:
                self.clients.remove(websocket)
        
        return await websockets.serve(handle_client, host, port)
    
    async def _handle_audio_stream(self, websocket):
        """Handle audio streaming for a client"""
        try:
            async for message in websocket:
                # Decode audio data
                audio_data = np.frombuffer(base64.b64decode(message), dtype=np.float32)
                
                # Process audio
                processed_audio = await self.processor._process_audio_data(
                    audio_data, self.config.sample_rate
                )
                
                # Send processed audio back
                processed_encoded = base64.b64encode(processed_audio.tobytes()).decode()
                await websocket.send(processed_encoded)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Client disconnected")
        except Exception as e:
            self.logger.error(f"Error handling audio stream: {e}")


# Usage example and test functions
async def main():
    """Example usage of AudioProcessor"""
    
    # Configure audio processor
    config = AudioConfig(
        sample_rate=44100,
        channels=2,
        enable_transcription=True,
        enable_music_analysis=True,
        enable_noise_reduction=True,
        enable_normalization=True
    )
    
    # Initialize processor
    processor = AudioProcessor(config)
    await processor.initialize()
    
    try:
        # Example: Process an audio file
        input_file = "example_audio.wav"
        output_file = "processed_audio.wav"
        
        if Path(input_file).exists():
            # Process with custom settings
            eq_settings = {
                "bands": [
                    {"frequency": 100, "gain": 2, "q": 1.0},    # Bass boost
                    {"frequency": 1000, "gain": -1, "q": 0.7},  # Mid cut
                    {"frequency": 8000, "gain": 3, "q": 1.5}    # Treble boost
                ]
            }
            
            compressor_settings = {
                "threshold": -18,
                "ratio": 4.0,
                "attack_ms": 5,
                "release_ms": 50
            }
            
            metadata = await processor.process_file(
                input_file,
                output_file,
                eq_settings=eq_settings,
                compressor_settings=compressor_settings
            )
            
            print(f"Processed audio file:")
            print(f"- Duration: {metadata.duration:.2f}s")
            print(f"- LUFS: {metadata.lufs:.1f}")
            print(f"- Tempo: {metadata.tempo:.1f} BPM")
            print(f"- Key: {metadata.key}")
            print(f"- Processing time: {metadata.processing_time_ms:.1f}ms")
            
            # Transcribe audio
            audio_data, sample_rate = librosa.load(input_file, sr=config.sample_rate)
            transcription = await processor.transcribe_audio(audio_data, sample_rate)
            print(f"- Transcription: {transcription['text'][:100]}...")
        
        # Example: Real-time processing
        print("\nStarting real-time processing for 5 seconds...")
        processor.start_real_time_processing()
        await asyncio.sleep(5)
        processor.stop_real_time_processing()
        
        # Example: Start streaming server
        print("\nStarting audio streaming server...")
        stream_server = AudioStreamServer(config, processor)
        server = await stream_server.start_server()
        
        print("Audio streaming server running. Press Ctrl+C to stop.")
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            server.close()
            await server.wait_closed()
        
    finally:
        await processor.cleanup()


if __name__ == "__main__":
    # Set event loop policy for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        logging.exception("Unhandled exception")