"""
Audio Processor Module
=====================

Enterprise-grade audio processing for music creators and influencers.
Handles audio analysis, fingerprinting, enhancement, and transformation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Professional audio analysis and fingerprinting
- Real-time audio enhancement and noise reduction  
- Multi-format audio conversion and optimization
- Spectral analysis and feature extraction
- Audio quality assessment and improvement
- Batch processing for large audio collections
"""

import asyncio
import logging
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

# Audio processing libraries
try:
    import essentia
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    ESSENTIA_AVAILABLE = False
    logging.warning("Essentia not available - some audio features will be limited")

try:
    import chromaprint
    CHROMAPRINT_AVAILABLE = True
except ImportError:
    CHROMAPRINT_AVAILABLE = False
    logging.warning("Chromaprint not available - audio fingerprinting will be limited")

logger = logging.getLogger(__name__)

@dataclass
class AudioMetadata:
    """Audio metadata container"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    file_size: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None

@dataclass
class AudioFeatures:
    """Audio feature extraction results"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    tempo: float
    key: str
    energy: float
    loudness: float

@dataclass
class AudioFingerprint:
    """Audio fingerprint data"""
    chromaprint_hash: Optional[str] = None
    spectral_hash: Optional[str] = None
    mfcc_hash: Optional[str] = None
    duration_hash: Optional[str] = None
    combined_hash: Optional[str] = None

class AudioProcessor:
    """Professional audio processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize audio processing engines
        self._initialize_engines()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default audio processing configuration"""
        return {
            'sample_rate': 44100,
            'bit_depth': 16,
            'channels': 2,
            'format': 'wav',
            'quality': 'high',
            'noise_reduction': True,
            'normalization': True,
            'enhancement': True,
            'fingerprinting': True,
            'feature_extraction': True,
            'spectral_analysis': True,
            'tempo_detection': True,
            'key_detection': True,
            'batch_size': 1024,
            'overlap': 512
        }
    
    def _initialize_engines(self):
        """Initialize audio processing engines"""
        try:
            # Initialize Essentia algorithms if available
            if ESSENTIA_AVAILABLE:
                self.windowing = es.Windowing(type='hann')
                self.spectrum = es.Spectrum()
                self.mfcc = es.MFCC()
                self.spectral_peaks = es.SpectralPeaks()
                self.pitch_detection = es.PitchYinFFT()
                self.beat_tracker = es.BeatTrackerMultiFeature()
                self.key_detector = es.KeyExtractor()
                self.loudness = es.Loudness()
                
                self.logger.info("Essentia audio engines initialized")
            
            # Initialize other audio tools
            self.logger.info("Audio processor engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing audio engines: {str(e)}")
            raise
    
    async def process(
        self,
        audio_data: Union[bytes, np.ndarray, str],
        format_hint: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main audio processing pipeline
        
        Args:
            audio_data: Audio data as bytes, numpy array, or file path
            format_hint: Optional format hint for processing
            config: Optional processing configuration override
        
        Returns:
            Dict containing processed audio data and analysis results
        """
        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Load and prepare audio
            audio_array, sample_rate = await self._load_audio(audio_data, format_hint)
            
            # Extract metadata
            metadata = await self._extract_metadata(audio_array, sample_rate)
            
            # Process audio in parallel
            tasks = []
            
            if processing_config.get('enhancement', True):
                tasks.append(self._enhance_audio(audio_array, sample_rate))
            
            if processing_config.get('feature_extraction', True):
                tasks.append(self._extract_features(audio_array, sample_rate))
            
            if processing_config.get('fingerprinting', True):
                tasks.append(self._generate_fingerprint(audio_array, sample_rate))
            
            if processing_config.get('spectral_analysis', True):
                tasks.append(self._spectral_analysis(audio_array, sample_rate))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compile final result
            result = {
                'success': True,
                'metadata': metadata,
                'original_audio': audio_array,
                'sample_rate': sample_rate,
                'processing_config': processing_config,
                'timestamp': np.datetime64('now').isoformat()
            }
            
            # Add processing results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    self.logger.error(f"Task {i} failed: {str(task_result)}")
                else:
                    result.update(task_result)
            
            self.logger.info("Audio processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': np.datetime64('now').isoformat()
            }
    
    async def _load_audio(
        self,
        audio_data: Union[bytes, np.ndarray, str],
        format_hint: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """Load audio data from various sources"""
        try:
            if isinstance(audio_data, str):
                # Load from file path
                audio_array, sample_rate = librosa.load(
                    audio_data,
                    sr=self.config['sample_rate'],
                    mono=False
                )
                
            elif isinstance(audio_data, bytes):
                # Load from bytes
                # Save temporarily and load with librosa
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(
                    suffix=f".{format_hint or 'wav'}", 
                    delete=False
                ) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                try:
                    audio_array, sample_rate = librosa.load(
                        tmp_path,
                        sr=self.config['sample_rate'],
                        mono=False
                    )
                finally:
                    os.unlink(tmp_path)
                    
            elif isinstance(audio_data, np.ndarray):
                # Already numpy array
                audio_array = audio_data
                sample_rate = self.config['sample_rate']
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
            
            # Ensure proper shape
            if audio_array.ndim == 1:
                audio_array = audio_array.reshape(1, -1)
            
            self.logger.debug(f"Loaded audio: shape={audio_array.shape}, sr={sample_rate}")
            return audio_array, sample_rate
            
        except Exception as e:
            self.logger.error(f"Error loading audio: {str(e)}")
            raise
    
    async def _extract_metadata(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> AudioMetadata:
        """Extract comprehensive audio metadata"""
        try:
            duration = audio_array.shape[-1] / sample_rate
            channels = audio_array.shape[0] if audio_array.ndim > 1 else 1
            
            metadata = AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=self.config['bit_depth'],
                format=self.config['format'],
                file_size=audio_array.nbytes
            )
            
            self.logger.debug(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            raise
    
    async def _enhance_audio(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Apply audio enhancement algorithms"""
        try:
            enhanced_audio = audio_array.copy()
            
            # Noise reduction using spectral gating
            if self.config.get('noise_reduction', True):
                enhanced_audio = await self._noise_reduction(enhanced_audio, sample_rate)
            
            # Audio normalization
            if self.config.get('normalization', True):
                enhanced_audio = await self._normalize_audio(enhanced_audio)
            
            # Dynamic range compression
            if self.config.get('compression', False):
                enhanced_audio = await self._compress_audio(enhanced_audio, sample_rate)
            
            # EQ enhancement
            if self.config.get('eq_enhancement', False):
                enhanced_audio = await self._eq_enhancement(enhanced_audio, sample_rate)
            
            return {
                'enhanced_audio': enhanced_audio,
                'enhancement_applied': True,
                'enhancement_algorithms': ['noise_reduction', 'normalization']
            }
            
        except Exception as e:
            self.logger.error(f"Audio enhancement failed: {str(e)}")
            return {
                'enhanced_audio': audio_array,
                'enhancement_applied': False,
                'error': str(e)
            }
    
    async def _extract_features(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Extract comprehensive audio features"""
        try:
            # Convert to mono for feature extraction
            if audio_array.ndim > 1:
                audio_mono = np.mean(audio_array, axis=0)
            else:
                audio_mono = audio_array
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=audio_mono,
                sr=sample_rate,
                n_mfcc=13
            )
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_mono,
                sr=sample_rate
            )
            
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_mono,
                sr=sample_rate
            )
            
            # Extract rhythm features
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_mono)
            
            # Extract harmonic features
            chroma = librosa.feature.chroma_stft(
                y=audio_mono,
                sr=sample_rate
            )
            
            # Tempo detection
            tempo, beats = librosa.beat.beat_track(
                y=audio_mono,
                sr=sample_rate
            )
            
            # Key detection (simplified)
            key = await self._detect_key(audio_mono, sample_rate)
            
            # Energy and loudness
            energy = np.sum(audio_mono ** 2) / len(audio_mono)
            loudness = librosa.feature.rms(y=audio_mono)[0].mean()
            
            features = AudioFeatures(
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                chroma=chroma,
                tempo=float(tempo),
                key=key,
                energy=float(energy),
                loudness=float(loudness)
            )
            
            return {
                'features': features,
                'feature_extraction_success': True,
                'feature_statistics': {
                    'mfcc_mean': np.mean(mfcc),
                    'spectral_centroid_mean': np.mean(spectral_centroid),
                    'tempo': float(tempo),
                    'key': key,
                    'energy': float(energy),
                    'loudness': float(loudness)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            return {
                'features': None,
                'feature_extraction_success': False,
                'error': str(e)
            }
    
    async def _generate_fingerprint(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Generate comprehensive audio fingerprint"""
        try:
            fingerprint = AudioFingerprint()
            
            # Convert to mono for fingerprinting
            if audio_array.ndim > 1:
                audio_mono = np.mean(audio_array, axis=0)
            else:
                audio_mono = audio_array
            
            # Chromaprint fingerprint (if available)
            if CHROMAPRINT_AVAILABLE:
                try:
                    # Convert to int16 for chromaprint
                    audio_int16 = (audio_mono * 32767).astype(np.int16)
                    
                    fingerprint.chromaprint_hash = chromaprint.encode(
                        audio_int16,
                        sample_rate
                    )
                except Exception as e:
                    self.logger.warning(f"Chromaprint fingerprinting failed: {str(e)}")
            
            # Spectral hash
            stft = librosa.stft(audio_mono)
            spectral_features = np.abs(stft).mean(axis=1)
            fingerprint.spectral_hash = hashlib.md5(
                spectral_features.tobytes()
            ).hexdigest()
            
            # MFCC hash
            mfcc = librosa.feature.mfcc(y=audio_mono, sr=sample_rate, n_mfcc=13)
            mfcc_features = mfcc.mean(axis=1)
            fingerprint.mfcc_hash = hashlib.md5(
                mfcc_features.tobytes()
            ).hexdigest()
            
            # Duration hash
            duration_str = f"{len(audio_mono)/sample_rate:.3f}"
            fingerprint.duration_hash = hashlib.md5(
                duration_str.encode()
            ).hexdigest()
            
            # Combined hash
            combined_data = (
                (fingerprint.spectral_hash or '') +
                (fingerprint.mfcc_hash or '') +
                (fingerprint.duration_hash or '')
            )
            fingerprint.combined_hash = hashlib.sha256(
                combined_data.encode()
            ).hexdigest()
            
            return {
                'fingerprint': fingerprint,
                'fingerprint_success': True,
                'fingerprint_algorithms': ['spectral', 'mfcc', 'duration', 'combined']
            }
            
        except Exception as e:
            self.logger.error(f"Audio fingerprinting failed: {str(e)}")
            return {
                'fingerprint': None,
                'fingerprint_success': False,
                'error': str(e)
            }
    
    async def _spectral_analysis(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Perform detailed spectral analysis"""
        try:
            # Convert to mono
            if audio_array.ndim > 1:
                audio_mono = np.mean(audio_array, axis=0)
            else:
                audio_mono = audio_array
            
            # STFT analysis
            stft = librosa.stft(
                audio_mono,
                hop_length=self.config.get('overlap', 512),
                n_fft=self.config.get('batch_size', 1024)
            )
            
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Spectral statistics
            spectral_mean = np.mean(magnitude, axis=1)
            spectral_std = np.std(magnitude, axis=1)
            spectral_max = np.max(magnitude, axis=1)
            
            # Frequency analysis
            freqs = librosa.fft_frequencies(sr=sample_rate)
            dominant_freq_idx = np.argmax(spectral_mean)
            dominant_frequency = freqs[dominant_freq_idx]
            
            # Harmonic analysis
            harmonic, percussive = librosa.effects.hpss(audio_mono)
            harmonic_ratio = np.sum(harmonic**2) / np.sum(audio_mono**2)
            
            return {
                'spectral_analysis': {
                    'magnitude_spectrum': magnitude,
                    'phase_spectrum': phase,
                    'spectral_mean': spectral_mean,
                    'spectral_std': spectral_std,
                    'spectral_max': spectral_max,
                    'dominant_frequency': float(dominant_frequency),
                    'harmonic_ratio': float(harmonic_ratio),
                    'frequency_range': [float(freqs[0]), float(freqs[-1])]
                },
                'spectral_analysis_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Spectral analysis failed: {str(e)}")
            return {
                'spectral_analysis': None,
                'spectral_analysis_success': False,
                'error': str(e)
            }
    
    async def _noise_reduction(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
        noise_factor: float = 0.1
    ) -> np.ndarray:
        """Apply noise reduction using spectral gating"""
        try:
            # Professional spectral subtraction noise reduction
            stft = librosa.stft(audio_array)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Apply spectral subtraction
            clean_magnitude = magnitude - noise_factor * noise_floor
            clean_magnitude = np.maximum(clean_magnitude, 0.1 * magnitude)
            
            # Reconstruct audio
            clean_stft = clean_magnitude * np.exp(1j * phase)
            clean_audio = librosa.istft(clean_stft)
            
            return clean_audio
            
        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {str(e)}")
            return audio_array
    
    async def _normalize_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        try:
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:
                return audio_array / max_val * 0.95
            return audio_array
            
        except Exception as e:
            self.logger.warning(f"Audio normalization failed: {str(e)}")
            return audio_array
    
    async def _compress_audio(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
        threshold: float = 0.5,
        ratio: float = 4.0
    ) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Professional compression algorithm
            compressed = audio_array.copy()
            
            # Find peaks above threshold
            above_threshold = np.abs(compressed) > threshold
            
            # Apply compression ratio
            compressed[above_threshold] = (
                np.sign(compressed[above_threshold]) * 
                (threshold + (np.abs(compressed[above_threshold]) - threshold) / ratio)
            )
            
            return compressed
            
        except Exception as e:
            self.logger.warning(f"Audio compression failed: {str(e)}")
            return audio_array
    
    async def _eq_enhancement(
        self,
        audio_array: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """Apply EQ enhancement"""
        try:
            # Professional EQ using filtering
            # This is a placeholder for more sophisticated EQ
            enhanced = audio_array.copy()
            
            # Apply gentle high-pass filter to remove rumble
            enhanced = librosa.effects.preemphasis(enhanced)
            
            return enhanced
            
        except Exception as e:
            self.logger.warning(f"EQ enhancement failed: {str(e)}")
            return audio_array
    
    async def _detect_key(self, audio_mono: np.ndarray, sample_rate: int) -> str:
        """Detect musical key (simplified implementation)"""
        try:
            if ESSENTIA_AVAILABLE:
                # Use Essentia for key detection
                key_extractor = es.KeyExtractor()
                key, scale, strength = key_extractor(audio_mono.astype(np.float32))
                return f"{key} {scale}"
            else:
                # Simplified chroma-based key detection
                chroma = librosa.feature.chroma_stft(y=audio_mono, sr=sample_rate)
                chroma_mean = np.mean(chroma, axis=1)
                key_idx = np.argmax(chroma_mean)
                
                keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                return keys[key_idx]
                
        except Exception as e:
            self.logger.warning(f"Key detection failed: {str(e)}")
            return "Unknown"
    
    async def convert_format(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
        target_format: str,
        output_path: Optional[str] = None
    ) -> Union[bytes, str]:
        """Convert audio to different format"""
        try:
            if output_path:
                # Save to file
                sf.write(output_path, audio_array.T, sample_rate)
                return output_path
            else:
                # Return as bytes
                import io
                buffer = io.BytesIO()
                sf.write(buffer, audio_array.T, sample_rate, format=target_format.upper())
                return buffer.getvalue()
                
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            raise
    
    async def batch_process(
        self,
        audio_files: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple audio files in batch"""
        tasks = []
        for file_path in audio_files:
            task = self.process(file_path, config=config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'file': audio_files[i]}
            for i, result in enumerate(results)
        ]
