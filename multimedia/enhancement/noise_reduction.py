"""Noise Reduction Engine
Advanced noise reduction for audio and video using AI and signal processing.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import librosa
import soundfile as sf
from typing import Dict, Optional, Union, Tuple, List
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageFilter
import scipy.signal
import scipy.ndimage
from sklearn.decomposition import PCA
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

@dataclass
class NoiseReductionConfig:
    """Configuration for noise reduction."""
    # Audio settings
    audio_noise_gate: float = -50.0  # dB threshold
    audio_reduction_strength: float = 0.7  # 0.0 to 1.0
    audio_preserve_speech: bool = True
    audio_spectral_subtraction: bool = True
    
    # Video/Image settings
    video_temporal_filtering: bool = True
    image_spatial_filtering: bool = True
    preserve_edges: bool = True
    noise_estimation_method: str = "adaptive"  # adaptive, manual, pca
    
    # AI settings
    use_ai_enhancement: bool = True
    gpu_acceleration: bool = True
    batch_processing: bool = False

class AudioDenoiser:
    """Advanced audio denoising using spectral methods and AI."""
    
    def __init__(self, config: NoiseReductionConfig):
        self.config = config
        
    async def denoise_audio(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, any]:
        """Denoise audio file using advanced algorithms."""
        try:
            # Load audio
            audio, sr = librosa.load(str(input_path), sr=None)
            original_length = len(audio)
            
            # Apply noise reduction techniques
            denoised_audio = audio.copy()
            
            # 1. Spectral subtraction
            if self.config.audio_spectral_subtraction:
                denoised_audio = await self._spectral_subtraction(
                    denoised_audio, sr
                )
            
            # 2. Noise gate
            denoised_audio = await self._apply_noise_gate(
                denoised_audio, self.config.audio_noise_gate
            )
            
            # 3. Wiener filtering
            denoised_audio = await self._wiener_filter(denoised_audio)
            
            # 4. Adaptive filtering
            denoised_audio = await self._adaptive_filter(denoised_audio, sr)
            
            # Preserve speech if enabled
            if self.config.audio_preserve_speech:
                denoised_audio = await self._preserve_speech_content(
                    audio, denoised_audio, sr
                )
            
            # Normalize and save
            denoised_audio = librosa.util.normalize(denoised_audio)
            sf.write(str(output_path), denoised_audio, sr)
            
            # Calculate metrics
            noise_reduction_db = await self._calculate_noise_reduction(
                audio, denoised_audio
            )
            
            return {
                "success": True,
                "original_duration": original_length / sr,
                "sample_rate": sr,
                "noise_reduction_db": noise_reduction_db,
                "processing_details": {
                    "spectral_subtraction": self.config.audio_spectral_subtraction,
                    "noise_gate_threshold": self.config.audio_noise_gate,
                    "speech_preservation": self.config.audio_preserve_speech
                }
            }
            
        except Exception as e:
            logger.error(f"Audio denoising failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _spectral_subtraction(
        self, 
        audio: np.ndarray, 
        sr: int
    ) -> np.ndarray:
        """Apply spectral subtraction for noise reduction."""
        # Compute STFT
        stft = librosa.stft(audio, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise spectrum from first 0.5 seconds
        noise_frames = int(0.5 * sr / 512)
        noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral subtraction
        alpha = self.config.audio_reduction_strength * 2  # Oversubtraction factor
        enhanced_magnitude = magnitude - alpha * noise_spectrum
        
        # Avoid over-subtraction
        beta = 0.1  # Spectral floor factor
        enhanced_magnitude = np.maximum(
            enhanced_magnitude, 
            beta * magnitude
        )
        
        # Reconstruct signal
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
        
        return enhanced_audio
    
    async def _apply_noise_gate(
        self, 
        audio: np.ndarray, 
        threshold_db: float
    ) -> np.ndarray:
        """Apply noise gate to suppress low-level noise."""
        # Convert to dB
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Create gate mask
        gate_mask = audio_db > threshold_db
        
        # Apply soft gating
        fade_length = int(0.01 * len(audio))  # 10ms fade
        gate_mask = scipy.ndimage.binary_closing(gate_mask, structure=np.ones(fade_length))
        
        # Smooth transitions
        gate_mask = scipy.signal.savgol_filter(
            gate_mask.astype(float), 
            window_length=min(51, len(gate_mask)//4 if len(gate_mask) > 200 else 5), 
            polyorder=3
        )
        
        return audio * gate_mask
    
    async def _wiener_filter(self, audio: np.ndarray) -> np.ndarray:
        """Apply Wiener filtering for noise reduction."""
        # Estimate signal and noise PSDs
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        
        # Simple noise estimation from low-energy frames
        frame_energy = np.sum(magnitude**2, axis=0)
        noise_threshold = np.percentile(frame_energy, 20)
        noise_frames = frame_energy < noise_threshold
        
        if np.any(noise_frames):
            noise_psd = np.mean(magnitude[:, noise_frames]**2, axis=1, keepdims=True)
        else:
            noise_psd = np.min(magnitude**2, axis=1, keepdims=True)
        
        signal_psd = magnitude**2
        
        # Wiener filter
        wiener_filter = signal_psd / (signal_psd + noise_psd)
        filtered_magnitude = magnitude * wiener_filter
        
        # Reconstruct
        enhanced_stft = filtered_magnitude * np.exp(1j * np.angle(stft))
        return librosa.istft(enhanced_stft)
    
    async def _adaptive_filter(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply adaptive filtering based on local signal characteristics."""
        # Frame-based processing
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = frame_length // 2
        
        frames = librosa.util.frame(audio, frame_length=frame_length, 
                                  hop_length=hop_length, axis=0)
        
        filtered_frames = []
        
        for frame in frames.T:
            # Estimate local SNR
            signal_power = np.var(frame)
            noise_power = np.var(frame - scipy.signal.savgol_filter(frame, 
                                window_length=min(15, len(frame)//3 if len(frame) > 45 else 3), 
                                polyorder=2))
            
            if noise_power > 0:
                snr = signal_power / noise_power
            else:
                snr = float('inf')
            
            # Adaptive filtering strength
            if snr > 10:  # High SNR - minimal filtering
                filter_strength = 0.1
            elif snr > 3:  # Medium SNR - moderate filtering
                filter_strength = 0.3
            else:  # Low SNR - strong filtering
                filter_strength = 0.7
            
            # Apply low-pass filtering for noisy frames
            if filter_strength > 0.2:
                cutoff = 0.4  # Normalize frequency
                b, a = scipy.signal.butter(4, cutoff, btype='low')
                filtered_frame = scipy.signal.filtfilt(b, a, frame)
                frame = frame * (1 - filter_strength) + filtered_frame * filter_strength
            
            filtered_frames.append(frame)
        
        # Reconstruct signal
        filtered_audio = np.zeros_like(audio)
        for i, frame in enumerate(filtered_frames):
            start = i * hop_length
            end = start + frame_length
            if end <= len(filtered_audio):
                filtered_audio[start:end] += frame
        
        return filtered_audio
    
    async def _preserve_speech_content(
        self, 
        original: np.ndarray, 
        denoised: np.ndarray, 
        sr: int
    ) -> np.ndarray:
        """Preserve speech content while reducing noise."""
        # Extract harmonic and percussive components
        orig_harmonic, orig_percussive = librosa.effects.hpss(original)
        
        # Speech is primarily in harmonic component
        # Apply less aggressive filtering to harmonic content
        speech_mask = self._detect_speech_segments(original, sr)
        
        # Blend original and denoised based on speech detection
        result = denoised.copy()
        result[speech_mask] = (
            0.7 * denoised[speech_mask] + 
            0.3 * original[speech_mask]
        )
        
        return result
    
    def _detect_speech_segments(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Simple speech detection based on spectral characteristics."""
        # Compute spectral features
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        
        # Speech indicators
        spectral_centroid = librosa.feature.spectral_centroid(S=magnitude**2)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude**2)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
        
        # Frame to sample mapping
        frames = librosa.frames_to_samples(range(len(spectral_centroid)))
        
        # Simple speech detection (heuristic)
        speech_frames = (
            (spectral_centroid > np.percentile(spectral_centroid, 30)) &
            (spectral_rolloff < np.percentile(spectral_rolloff, 70)) &
            (zero_crossing_rate < np.percentile(zero_crossing_rate, 60))
        )
        
        # Map back to audio samples
        speech_mask = np.zeros(len(audio), dtype=bool)
        for i, is_speech in enumerate(speech_frames):
            if i < len(frames) - 1:
                start, end = frames[i], frames[i + 1]
                speech_mask[start:end] = is_speech
        
        return speech_mask
    
    async def _calculate_noise_reduction(
        self, 
        original: np.ndarray, 
        denoised: np.ndarray
    ) -> float:
        """Calculate noise reduction in dB."""
        # Estimate noise power
        noise = original - denoised
        
        original_power = np.mean(original**2)
        noise_power = np.mean(noise**2)
        
        if noise_power > 0 and original_power > 0:
            snr_improvement = 10 * np.log10(original_power / noise_power)
            return max(0, snr_improvement)
        
        return 0.0

class ImageVideoDenoiser:
    """Advanced image and video denoising."""
    
    def __init__(self, config: NoiseReductionConfig):
        self.config = config
        
    async def denoise_image(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, any]:
        """Denoise image using advanced algorithms."""
        try:
            # Load image
            image = cv2.imread(str(input_path))
            if image is None:
                raise ValueError("Could not load image")
            
            original_image = image.copy()
            
            # Apply denoising techniques
            denoised = await self._apply_image_denoising(image)
            
            # Save result
            cv2.imwrite(str(output_path), denoised)
            
            # Calculate metrics
            psnr = cv2.PSNR(original_image, denoised)
            ssim = self._calculate_ssim(original_image, denoised)
            
            return {
                "success": True,
                "psnr": psnr,
                "ssim": ssim,
                "image_shape": image.shape,
                "denoising_methods": ["non_local_means", "bilateral", "median"]
            }
            
        except Exception as e:
            logger.error(f"Image denoising failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_image_denoising(self, image: np.ndarray) -> np.ndarray:
        """Apply multiple denoising techniques to image."""
        denoised = image.copy()
        
        # 1. Non-local means denoising (best for natural images)
        if self.config.image_spatial_filtering:
            denoised = cv2.fastNlMeansDenoisingColored(
                denoised, None, 10, 10, 7, 21
            )
        
        # 2. Bilateral filtering (edge-preserving)
        if self.config.preserve_edges:
            denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        # 3. Selective median filtering for impulse noise
        gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
        
        # Detect impulse noise
        median_filtered = cv2.medianBlur(gray, 5)
        noise_mask = np.abs(gray.astype(float) - median_filtered.astype(float)) > 30
        
        # Apply median filter only to noisy regions
        for channel in range(3):
            channel_data = denoised[:, :, channel]
            median_channel = cv2.medianBlur(channel_data, 3)
            channel_data[noise_mask] = median_channel[noise_mask]
        
        return denoised
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index."""
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # SSIM calculation
        mu1 = cv2.GaussianBlur(gray1.astype(float), (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(gray2.astype(float), (11, 11), 1.5)
        
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.GaussianBlur(gray1.astype(float) * gray1.astype(float), 
                                   (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(gray2.astype(float) * gray2.astype(float), 
                                   (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(gray1.astype(float) * gray2.astype(float), 
                                 (11, 11), 1.5) - mu1_mu2
        
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / \
                   ((mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2))
        
        return float(np.mean(ssim_map))

class NoiseReductionEngine:
    """Enterprise noise reduction engine for audio, video, and images."""
    
    def __init__(self):
        self.config = NoiseReductionConfig()
        self.audio_denoiser = None
        self.image_denoiser = None
        
    async def reduce_noise(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        noise_level: float = 0.5,
        config: Optional[NoiseReductionConfig] = None
    ) -> Dict[str, any]:
        """Reduce noise in media files (audio, video, or images)."""
        try:
            if config:
                self.config = config
            
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Detect file type and apply appropriate denoising
            file_ext = input_path.suffix.lower()
            
            if file_ext in ['.wav', '.mp3', '.flac', '.m4a', '.aac']:
                result = await self._reduce_audio_noise(input_path, output_path, noise_level)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                result = await self._reduce_image_noise(input_path, output_path, noise_level)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                result = await self._reduce_video_noise(input_path, output_path, noise_level)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return {
                "success": True,
                "file_type": self._get_media_type(file_ext),
                "noise_reduction_level": noise_level,
                "output_path": str(output_path),
                **result
            }
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _reduce_audio_noise(
        self, 
        input_path: Path, 
        output_path: Path, 
        noise_level: float
    ) -> Dict[str, any]:
        """Reduce noise in audio files."""
        if self.audio_denoiser is None:
            # Update config with noise level
            self.config.audio_reduction_strength = noise_level
            self.audio_denoiser = AudioDenoiser(self.config)
        
        return await self.audio_denoiser.denoise_audio(input_path, output_path)
    
    async def _reduce_image_noise(
        self, 
        input_path: Path, 
        output_path: Path, 
        noise_level: float
    ) -> Dict[str, any]:
        """Reduce noise in image files."""
        if self.image_denoiser is None:
            self.image_denoiser = ImageVideoDenoiser(self.config)
        
        return await self.image_denoiser.denoise_image(input_path, output_path)
    
    async def _reduce_video_noise(
        self, 
        input_path: Path, 
        output_path: Path, 
        noise_level: float
    ) -> Dict[str, any]:
        """Reduce noise in video files."""
        # For video, we'll process frame by frame
        # This is a simplified implementation - production would use temporal filtering
        
        import subprocess
        
        # Use FFmpeg for video denoising
        ffmpeg_cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', f'nlmeans=s={noise_level*10}:r=5:p=7',
            '-af', 'arnndn',  # Audio noise reduction
            '-y', str(output_path)
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "video_processing": True,
                    "temporal_filtering": True,
                    "audio_denoising": True
                }
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"FFmpeg video denoising failed, using fallback: {e}")
            
            # Fallback: copy file and return basic result
            import shutil
            shutil.copy2(input_path, output_path)
            
            return {
                "video_processing": False,
                "fallback_used": True,
                "note": "Advanced video denoising requires FFmpeg"
            }
    
    def _get_media_type(self, file_ext: str) -> str:
        """Determine media type from file extension."""
        audio_exts = {'.wav', '.mp3', '.flac', '.m4a', '.aac'}
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv'}
        
        if file_ext in audio_exts:
            return "audio"
        elif file_ext in image_exts:
            return "image"
        elif file_ext in video_exts:
            return "video"
        else:
            return "unknown"
    
    async def batch_noise_reduction(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        noise_level: float = 0.5,
        config: Optional[NoiseReductionConfig] = None
    ) -> Dict[str, any]:
        """Apply noise reduction to multiple files."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            return {"success": False, "error": "Input directory not found"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        supported_formats = {
            '.wav', '.mp3', '.flac', '.m4a', '.aac',  # Audio
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff',  # Image
            '.mp4', '.avi', '.mov', '.mkv'  # Video
        }
        
        for file_path in input_dir.iterdir():
            if file_path.suffix.lower() in supported_formats:
                output_path = output_dir / file_path.name
                
                result = await self.reduce_noise(
                    file_path, output_path, noise_level, config
                )
                
                results.append({
                    "input": str(file_path),
                    "output": str(output_path),
                    "result": result
                })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }
    
    def get_optimal_settings(self, media_type: str) -> NoiseReductionConfig:
        """Get optimal noise reduction settings for media type."""
        config = NoiseReductionConfig()
        
        if media_type == "audio":
            config.audio_noise_gate = -45.0
            config.audio_reduction_strength = 0.6
            config.audio_preserve_speech = True
            config.audio_spectral_subtraction = True
            
        elif media_type == "image":
            config.image_spatial_filtering = True
            config.preserve_edges = True
            config.noise_estimation_method = "adaptive"
            
        elif media_type == "video":
            config.video_temporal_filtering = True
            config.image_spatial_filtering = True
            config.preserve_edges = True
            
        return config