"""Fingerprint Parsers Module
==========================

Specialized parsers for preparing content data for fingerprinting and copyright protection.
Handles audio, video, image, and text content analysis for digital rights management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""import asyncio
import hashlib
import json
import os
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

import aiofiles
import aiohttp
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

from .exceptions import FingerprintParsingError, MediaProcessingError
from .parser_config import ParserConfig

# Audio processing imports (if available)
try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Video processing imports (if available)
try:
    import ffmpeg
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False


class BaseFingerprintParser(ABC):
    """Abstract base class for fingerprint parsers"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.fingerprint_config = config.fingerprint
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def parse_for_fingerprint(self, content_path: str, **kwargs) -> Dict[str, Any]:
        """Parse content and prepare fingerprint data"""        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get the content type this parser handles"""        pass
    
    def _generate_hash(self, data: bytes, algorithm: str = "sha256") -> str:
        """Generate hash of content data"""        if algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata"""        file_stats = os.stat(file_path)
        file_path_obj = Path(file_path)
        
        return {
            'filename': file_path_obj.name,
            'file_extension': file_path_obj.suffix.lower(),
            'file_size': file_stats.st_size,
            'created_at': datetime.fromtimestamp(file_stats.st_ctime, timezone.utc).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime, timezone.utc).isoformat(),
            'mime_type': self._get_mime_type(file_path)
        }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'


class AudioFingerprintParser(BaseFingerprintParser):
    """Parser for audio content fingerprinting"""    
    def get_content_type(self) -> str:
        return "audio"
    
    async def parse_for_fingerprint(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Parse audio file for fingerprinting"""        try:
            if not AUDIO_AVAILABLE:
                raise FingerprintParsingError(
                    "Audio processing libraries not available",
                    content_type="audio",
                    parser_type="AudioFingerprintParser"
                )
            
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(audio_path)
            
            # Load audio file
            audio_data, sample_rate = await self._load_audio_file(audio_path)
            
            # Extract audio features for fingerprinting
            audio_features = await self._extract_audio_features(audio_data, sample_rate)
            
            # Generate content hash
            with open(audio_path, 'rb') as f:
                content_hash = self._generate_hash(f.read())
            
            # Extract audio fingerprint
            fingerprint_data = await self._generate_audio_fingerprint(audio_data, sample_rate)
            
            return {
                'content_type': self.get_content_type(),
                'file_metadata': file_metadata,
                'audio_properties': {
                    'duration': len(audio_data) / sample_rate,
                    'sample_rate': sample_rate,
                    'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                    'bit_depth': 16,  # Default assumption
                    'format': file_metadata['file_extension']
                },
                'content_hash': content_hash,
                'fingerprint': fingerprint_data,
                'features': audio_features,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise FingerprintParsingError(
                f"Audio fingerprint parsing failed: {str(e)}",
                content_type="audio",
                parser_type="AudioFingerprintParser"
            )
    
    async def _load_audio_file(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file using librosa"""        try:
            # Load with librosa, convert to mono and normalize
            audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
            return audio_data, sample_rate
        except Exception as e:
            raise MediaProcessingError(
                f"Failed to load audio file: {str(e)}",
                media_type="audio",
                file_path=audio_path
            )
    
    async def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract audio features for analysis"""        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            
            # Extract rhythm features
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            
            return {
                'mfcc': {
                    'coefficients': mfccs.tolist(),
                    'mean': np.mean(mfccs, axis=1).tolist(),
                    'std': np.std(mfccs, axis=1).tolist()
                },
                'spectral': {
                    'centroid_mean': float(np.mean(spectral_centroids)),
                    'rolloff_mean': float(np.mean(spectral_rolloff)),
                    'bandwidth_mean': float(np.mean(spectral_bandwidth))
                },
                'rhythm': {
                    'tempo': float(tempo),
                    'beat_frames': beats.tolist() if len(beats) <= 100 else beats[:100].tolist()
                },
                'chroma': {
                    'features': chroma.tolist(),
                    'mean': np.mean(chroma, axis=1).tolist()
                },
                'zcr': {
                    'mean': float(np.mean(zcr)),
                    'std': float(np.std(zcr))
                }
            }
            
        except Exception as e:
            raise MediaProcessingError(
                f"Audio feature extraction failed: {str(e)}",
                media_type="audio"
            )
    
    async def _generate_audio_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Generate audio fingerprint for copyright detection"""        try:
            # Simplified audio fingerprinting approach
            # In production, you'd use more sophisticated algorithms like Shazam's or Gracenote's
            
            # Extract short-time Fourier transform
            stft = librosa.stft(audio_data, hop_length=512, n_fft=2048)
            magnitude = np.abs(stft)
            
            # Generate spectral peaks
            peaks = []
            for i in range(0, magnitude.shape[1], 10):  # Sample every 10 frames
                frame = magnitude[:, i]
                peak_indices = np.argsort(frame)[-5:]  # Top 5 frequencies
                peaks.extend([(int(idx), float(frame[idx]), i) for idx in peak_indices])
            
            # Create hash-based fingerprint
            fingerprint_segments = []
            segment_length = sample_rate * 10  # 10-second segments
            
            for i in range(0, len(audio_data), segment_length):
                segment = audio_data[i:i + segment_length]
                if len(segment) >= sample_rate:  # At least 1 second
                    segment_mfcc = librosa.feature.mfcc(y=segment, sr=sample_rate, n_mfcc=12)
                    segment_hash = hashlib.md5(segment_mfcc.tobytes()).hexdigest()
                    fingerprint_segments.append({
                        'start_time': i / sample_rate,
                        'duration': len(segment) / sample_rate,
                        'hash': segment_hash,
                        'mfcc_mean': np.mean(segment_mfcc, axis=1).tolist()
                    })
            
            return {
                'algorithm': 'mfcc_spectral_peaks',
                'segments': fingerprint_segments,
                'spectral_peaks': peaks[:1000],  # Limit to prevent excessive data
                'total_segments': len(fingerprint_segments),
                'fingerprint_quality': self._assess_fingerprint_quality(audio_data, sample_rate)
            }
            
        except Exception as e:
            raise MediaProcessingError(
                f"Audio fingerprint generation failed: {str(e)}",
                media_type="audio"
            )
    
    def _assess_fingerprint_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Assess the quality of the audio for fingerprinting"""        # Signal-to-noise ratio estimation
        signal_power = np.mean(audio_data ** 2)
        noise_floor = np.percentile(np.abs(audio_data), 10)
        snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
        
        # Dynamic range
        dynamic_range = np.max(np.abs(audio_data)) - np.min(np.abs(audio_data))
        
        # Frequency content analysis
        fft = np.fft.fft(audio_data)
        freq_content = np.sum(np.abs(fft[len(fft)//4:3*len(fft)//4]))  # Mid-frequency content
        
        quality_score = min(100, max(0, (snr + 20) * 2 + dynamic_range * 50))
        
        return {
            'quality_score': float(quality_score),
            'snr_db': float(snr),
            'dynamic_range': float(dynamic_range),
            'frequency_richness': float(freq_content),
            'suitable_for_fingerprinting': quality_score > 50
        }


class VideoFingerprintParser(BaseFingerprintParser):
    """Parser for video content fingerprinting"""    
    def get_content_type(self) -> str:
        return "video"
    
    async def parse_for_fingerprint(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """Parse video file for fingerprinting"""        try:
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(video_path)
            
            # Extract video properties
            video_properties = await self._extract_video_properties(video_path)
            
            # Generate content hash
            with open(video_path, 'rb') as f:
                content_hash = self._generate_hash(f.read())
            
            # Extract visual fingerprint
            visual_fingerprint = await self._generate_visual_fingerprint(video_path)
            
            # Extract audio fingerprint if audio track exists
            audio_fingerprint = None
            if video_properties.get('has_audio', False):
                audio_fingerprint = await self._extract_video_audio_fingerprint(video_path)
            
            return {
                'content_type': self.get_content_type(),
                'file_metadata': file_metadata,
                'video_properties': video_properties,
                'content_hash': content_hash,
                'visual_fingerprint': visual_fingerprint,
                'audio_fingerprint': audio_fingerprint,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise FingerprintParsingError(
                f"Video fingerprint parsing failed: {str(e)}",
                content_type="video",
                parser_type="VideoFingerprintParser"
            )
    
    async def _extract_video_properties(self, video_path: str) -> Dict[str, Any]:
        """Extract video properties using OpenCV"""        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise MediaProcessingError(
                    "Could not open video file",
                    media_type="video",
                    file_path=video_path
                )
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'aspect_ratio': width / height if height > 0 else 0,
                'resolution': f"{width}x{height}",
                'has_audio': True  # Assume has audio, would need ffmpeg for accurate detection
            }
            
        except Exception as e:
            raise MediaProcessingError(
                f"Video property extraction failed: {str(e)}",
                media_type="video",
                file_path=video_path
            )
    
    async def _generate_visual_fingerprint(self, video_path: str) -> Dict[str, Any]:
        """Generate visual fingerprint from video frames"""        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise MediaProcessingError("Could not open video file", media_type="video")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Extract keyframes for fingerprinting
            keyframes = []
            frame_hashes = []
            
            # Sample frames every second or every 30 frames, whichever is less
            sample_interval = min(int(fps), 30) if fps > 0 else 30
            
            for frame_idx in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Generate frame fingerprint
                frame_fingerprint = self._generate_frame_fingerprint(frame)
                
                keyframes.append({
                    'frame_index': frame_idx,
                    'timestamp': frame_idx / fps if fps > 0 else 0,
                    'fingerprint': frame_fingerprint
                })
                
                # Generate perceptual hash for the frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (8, 8))
                avg = resized.mean()
                binary = resized > avg
                frame_hash = ''.join(['1' if pixel else '0' for pixel in binary.flatten()])
                frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Generate scene change detection
            scene_changes = self._detect_scene_changes(keyframes)
            
            return {
                'algorithm': 'perceptual_hash_keyframes',
                'keyframes': keyframes[:100],  # Limit to prevent excessive data
                'frame_hashes': frame_hashes[:100],
                'scene_changes': scene_changes,
                'total_keyframes': len(keyframes),
                'fingerprint_quality': self._assess_visual_fingerprint_quality(keyframes)
            }
            
        except Exception as e:
            raise MediaProcessingError(
                f"Visual fingerprint generation failed: {str(e)}",
                media_type="video"
            )
    
    def _generate_frame_fingerprint(self, frame: np.ndarray) -> Dict[str, Any]:
        """Generate fingerprint for a single frame"""        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist.flatten() / hist.sum()
        
        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate texture features using Local Binary Patterns (simplified)
        texture_score = np.std(gray)
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        return {
            'histogram': hist_normalized.tolist()[:64],  # Reduce dimensionality
            'edge_density': float(edge_density),
            'texture_score': float(texture_score),
            'brightness': float(brightness),
            'contrast': float(contrast)
        }
    
    def _detect_scene_changes(self, keyframes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect scene changes in video"""        scene_changes = []
        
        for i in range(1, len(keyframes)):
            curr_frame = keyframes[i]['fingerprint']
            prev_frame = keyframes[i-1]['fingerprint']
            
            # Calculate histogram difference
            hist_diff = np.sum(np.abs(np.array(curr_frame['histogram']) - np.array(prev_frame['histogram'])))
            
            # Calculate feature differences
            edge_diff = abs(curr_frame['edge_density'] - prev_frame['edge_density'])
            brightness_diff = abs(curr_frame['brightness'] - prev_frame['brightness'])
            
            # Simple scene change detection
            change_score = hist_diff + edge_diff * 10 + brightness_diff / 10
            
            if change_score > 0.3:  # Threshold for scene change
                scene_changes.append({
                    'timestamp': keyframes[i]['timestamp'],
                    'frame_index': keyframes[i]['frame_index'],
                    'change_score': float(change_score),
                    'change_type': 'cut' if change_score > 0.7 else 'gradual'
                })
        
        return scene_changes
    
    def _assess_visual_fingerprint_quality(self, keyframes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of visual fingerprint"""        if not keyframes:
            return {'quality_score': 0, 'suitable_for_fingerprinting': False}
        
        # Calculate average contrast and edge density
        avg_contrast = np.mean([kf['fingerprint']['contrast'] for kf in keyframes])
        avg_edge_density = np.mean([kf['fingerprint']['edge_density'] for kf in keyframes])
        
        # Calculate texture variation
        texture_scores = [kf['fingerprint']['texture_score'] for kf in keyframes]
        texture_variation = np.std(texture_scores)
        
        # Quality score based on visual richness
        quality_score = min(100, (avg_contrast / 50 + avg_edge_density * 100 + texture_variation / 10) * 20)
        
        return {
            'quality_score': float(quality_score),
            'avg_contrast': float(avg_contrast),
            'avg_edge_density': float(avg_edge_density),
            'texture_variation': float(texture_variation),
            'suitable_for_fingerprinting': quality_score > 40
        }
    
    async def _extract_video_audio_fingerprint(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Extract audio fingerprint from video file"""        if not AUDIO_AVAILABLE:
            return None
        
        try:
            # Extract audio from video (simplified approach)
            # In production, you'd use ffmpeg to extract audio properly
            audio_data, sample_rate = librosa.load(video_path, sr=None)
            
            if len(audio_data) == 0:
                return None
            
            # Create temporary audio fingerprint parser
            audio_parser = AudioFingerprintParser(self.config)
            
            # Use a subset of audio for fingerprinting (first 30 seconds)
            max_samples = sample_rate * 30
            if len(audio_data) > max_samples:
                audio_data = audio_data[:max_samples]
            
            # Generate fingerprint using the audio parser logic
            fingerprint_data = await audio_parser._generate_audio_fingerprint(audio_data, sample_rate)
            
            return {
                'extracted_from_video': True,
                'audio_duration': len(audio_data) / sample_rate,
                'fingerprint': fingerprint_data
            }
            
        except Exception as e:
            # Audio extraction failed, return None
            return None


class ImageFingerprintParser(BaseFingerprintParser):
    """Parser for image content fingerprinting"""    
    def get_content_type(self) -> str:
        return "image"
    
    async def parse_for_fingerprint(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """Parse image file for fingerprinting"""        try:
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(image_path)
            
            # Load and analyze image
            image_properties = await self._extract_image_properties(image_path)
            
            # Generate content hash
            with open(image_path, 'rb') as f:
                content_hash = self._generate_hash(f.read())
            
            # Generate visual fingerprint
            visual_fingerprint = await self._generate_image_fingerprint(image_path)
            
            return {
                'content_type': self.get_content_type(),
                'file_metadata': file_metadata,
                'image_properties': image_properties,
                'content_hash': content_hash,
                'visual_fingerprint': visual_fingerprint,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise FingerprintParsingError(
                f"Image fingerprint parsing failed: {str(e)}",
                content_type="image",
                parser_type="ImageFingerprintParser"
            )
    
    async def _extract_image_properties(self, image_path: str) -> Dict[str, Any]:
        """Extract image properties and EXIF data"""        try:
            with Image.open(image_path) as img:
                # Basic properties
                width, height = img.size
                mode = img.mode
                format_name = img.format
                
                # EXIF data
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        try:
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                        except:
                            continue
                
                # Color analysis
                if img.mode == 'RGB':
                    # Convert to numpy array for analysis
                    img_array = np.array(img)
                    
                    # Calculate color statistics
                    mean_color = np.mean(img_array, axis=(0, 1))
                    std_color = np.std(img_array, axis=(0, 1))
                    
                    # Dominant colors (simplified)
                    pixels = img_array.reshape(-1, 3)
                    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                    dominant_color = unique_colors[np.argmax(counts)]
                else:
                    mean_color = None
                    std_color = None
                    dominant_color = None
                
                return {
                    'width': width,
                    'height': height,
                    'aspect_ratio': width / height,
                    'mode': mode,
                    'format': format_name,
                    'total_pixels': width * height,
                    'exif': exif_data,
                    'color_analysis': {
                        'mean_color': mean_color.tolist() if mean_color is not None else None,
                        'std_color': std_color.tolist() if std_color is not None else None,
                        'dominant_color': dominant_color.tolist() if dominant_color is not None else None
                    }
                }
                
        except Exception as e:
            raise MediaProcessingError(
                f"Image property extraction failed: {str(e)}",
                media_type="image",
                file_path=image_path
            )
    
    async def _generate_image_fingerprint(self, image_path: str) -> Dict[str, Any]:
        """Generate perceptual fingerprint for image"""        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Generate perceptual hash
                phash = self._calculate_perceptual_hash(img)
                
                # Generate difference hash
                dhash = self._calculate_difference_hash(img)
                
                # Generate average hash
                ahash = self._calculate_average_hash(img)
                
                # Extract visual features
                visual_features = self._extract_visual_features(img)
                
                # Calculate histogram
                histogram = self._calculate_color_histogram(img)
                
                return {
                    'algorithm': 'multi_hash_features',
                    'perceptual_hash': phash,
                    'difference_hash': dhash,
                    'average_hash': ahash,
                    'visual_features': visual_features,
                    'color_histogram': histogram,
                    'fingerprint_quality': self._assess_image_fingerprint_quality(img, visual_features)
                }
                
        except Exception as e:
            raise MediaProcessingError(
                f"Image fingerprint generation failed: {str(e)}",
                media_type="image"
            )
    
    def _calculate_perceptual_hash(self, img: Image.Image, hash_size: int = 8) -> str:
        """Calculate perceptual hash (pHash)"""        # Resize to hash_size x hash_size
        img = img.resize((hash_size * 4, hash_size * 4), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)
        
        # Apply DCT
        dct = cv2.dct(img_array)
        
        # Extract top-left 8x8 region
        dct_low = dct[:hash_size, :hash_size]
        
        # Calculate median
        median = np.median(dct_low)
        
        # Generate hash
        hash_bits = dct_low > median
        
        # Convert to hex string
        hash_string = ''.join(['1' if bit else '0' for bit in hash_bits.flatten()])
        return hex(int(hash_string, 2))[2:]
    
    def _calculate_difference_hash(self, img: Image.Image, hash_size: int = 8) -> str:
        """Calculate difference hash (dHash)"""        # Resize to (hash_size + 1) x hash_size
        img = img.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Calculate differences
        diff = img_array[:, 1:] > img_array[:, :-1]
        
        # Convert to hex string
        hash_string = ''.join(['1' if bit else '0' for bit in diff.flatten()])
        return hex(int(hash_string, 2))[2:]
    
    def _calculate_average_hash(self, img: Image.Image, hash_size: int = 8) -> str:
        """Calculate average hash (aHash)"""        # Resize to hash_size x hash_size
        img = img.resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Calculate average
        avg = img_array.mean()
        
        # Generate hash
        hash_bits = img_array > avg
        
        # Convert to hex string
        hash_string = ''.join(['1' if bit else '0' for bit in hash_bits.flatten()])
        return hex(int(hash_string, 2))[2:]
    
    def _extract_visual_features(self, img: Image.Image) -> Dict[str, Any]:
        """Extract visual features from image"""        # Convert to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale for some calculations
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate texture (using standard deviation as simple measure)
        texture_score = np.std(gray)
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Calculate sharpness (using Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        return {
            'edge_density': float(edge_density),
            'texture_score': float(texture_score),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'sharpness': float(sharpness)
        }
    
    def _calculate_color_histogram(self, img: Image.Image) -> Dict[str, List[float]]:
        """Calculate color histogram"""        img_array = np.array(img)
        
        # Calculate histogram for each channel
        hist_r = np.histogram(img_array[:, :, 0], bins=16, range=(0, 256))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=16, range=(0, 256))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=16, range=(0, 256))[0]
        
        # Normalize
        total_pixels = img_array.shape[0] * img_array.shape[1]
        hist_r = hist_r / total_pixels
        hist_g = hist_g / total_pixels
        hist_b = hist_b / total_pixels
        
        return {
            'red': hist_r.tolist(),
            'green': hist_g.tolist(),
            'blue': hist_b.tolist()
        }
    
    def _assess_image_fingerprint_quality(self, img: Image.Image, visual_features: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of image fingerprint"""        # Quality based on visual complexity
        edge_density = visual_features['edge_density']
        contrast = visual_features['contrast']
        sharpness = visual_features['sharpness']
        
        # Calculate quality score
        quality_score = min(100, (edge_density * 100 + contrast / 2 + sharpness / 100) * 10)
        
        return {
            'quality_score': float(quality_score),
            'edge_density': edge_density,
            'contrast': contrast,
            'sharpness': sharpness,
            'suitable_for_fingerprinting': quality_score > 30
        }


class TextFingerprintParser(BaseFingerprintParser):
    """Parser for text content fingerprinting"""    
    def get_content_type(self) -> str:
        return "text"
    
    async def parse_for_fingerprint(self, text_path: str, **kwargs) -> Dict[str, Any]:
        """Parse text file for fingerprinting"""        try:
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(text_path)
            
            # Read text content
            async with aiofiles.open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = await f.read()
            
            # Generate content hash
            content_hash = self._generate_hash(text_content.encode('utf-8'))
            
            # Extract text properties
            text_properties = self._extract_text_properties(text_content)
            
            # Generate text fingerprint
            text_fingerprint = await self._generate_text_fingerprint(text_content)
            
            return {
                'content_type': self.get_content_type(),
                'file_metadata': file_metadata,
                'text_properties': text_properties,
                'content_hash': content_hash,
                'text_fingerprint': text_fingerprint,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise FingerprintParsingError(
                f"Text fingerprint parsing failed: {str(e)}",
                content_type="text",
                parser_type="TextFingerprintParser"
            )
    
    def _extract_text_properties(self, text: str) -> Dict[str, Any]:
        """Extract properties from text content"""        import re
        
        # Basic statistics
        char_count = len(text)
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        
        # Character frequency
        char_freq = {}
        for char in text.lower():
            if char.isalpha():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Most common words
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 2:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Language detection (simplified)
        language = self._detect_language(text)
        
        return {
            'char_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'avg_words_per_line': word_count / line_count if line_count > 0 else 0,
            'avg_chars_per_word': char_count / word_count if word_count > 0 else 0,
            'character_frequency': dict(sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]),
            'common_words': common_words,
            'detected_language': language
        }
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words"""        # Simplified language detection
        english_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'was', 'one', 'our', 'day']
        french_words = ['les', 'des', 'une', 'est', 'qui', 'sur', 'avec', 'son', 'que', 'dans', 'par', 'pour', 'pas', 'tout']
        german_words = ['der', 'die', 'und', 'von', 'den', 'des', 'mit', 'dem', 'ein', 'eine', 'ich', 'das', 'nicht', 'sie']
        spanish_words = ['que', 'de', 'no', 'el', 'la', 'un', 'en', 'es', 'se', 'te', 'lo', 'le', 'da', 'su']
        
        text_lower = text.lower()
        
        english_score = sum(1 for word in english_words if word in text_lower)
        french_score = sum(1 for word in french_words if word in text_lower)
        german_score = sum(1 for word in german_words if word in text_lower)
        spanish_score = sum(1 for word in spanish_words if word in text_lower)
        
        scores = {
            'english': english_score,
            'french': french_score,
            'german': german_score,
            'spanish': spanish_score
        }
        
        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'unknown'
    
    async def _generate_text_fingerprint(self, text: str) -> Dict[str, Any]:
        """Generate fingerprint for text content"""        try:
            import re
            
            # Clean text for fingerprinting
            cleaned_text = re.sub(r'\s+', ' ', text.lower().strip())
            
            # Generate n-gram hashes
            ngram_hashes = self._generate_ngram_hashes(cleaned_text)
            
            # Generate sentence structure fingerprint
            sentence_structure = self._analyze_sentence_structure(text)
            
            # Generate semantic fingerprint (simplified)
            semantic_features = self._extract_semantic_features(cleaned_text)
            
            # Generate shingle-based fingerprint
            shingles = self._generate_shingles(cleaned_text)
            
            return {
                'algorithm': 'ngram_semantic_shingles',
                'ngram_hashes': ngram_hashes,
                'sentence_structure': sentence_structure,
                'semantic_features': semantic_features,
                'shingles': shingles[:100],  # Limit shingles
                'fingerprint_quality': self._assess_text_fingerprint_quality(text)
            }
            
        except Exception as e:
            raise MediaProcessingError(
                f"Text fingerprint generation failed: {str(e)}",
                media_type="text"
            )
    
    def _generate_ngram_hashes(self, text: str, n: int = 3) -> List[str]:
        """Generate n-gram hashes for text"""        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i + n])
            ngram_hash = hashlib.md5(ngram.encode('utf-8')).hexdigest()[:8]
            ngrams.append(ngram_hash)
        
        return ngrams[:50]  # Limit to prevent excessive data
    
    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """Analyze sentence structure patterns"""        import re
        
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if not sentence_lengths:
            return {'avg_length': 0, 'length_pattern': []}
        
        return {
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths),
            'sentence_count': len(sentence_lengths),
            'length_variance': np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0,
            'length_pattern': sentence_lengths[:20]  # First 20 sentence lengths
        }
    
    def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extract semantic features (simplified)"""        import re
        
        # Count different types of words
        words = text.split()
        
        # Count parts of speech (very simplified)
        nouns = len(re.findall(r'\b\w+(?:tion|ness|ment|ity|er|or|ist)\b', text))
        verbs = len(re.findall(r'\b\w+(?:ing|ed|ize|ify)\b', text))
        adjectives = len(re.findall(r'\b\w+(?:ful|less|able|ive|ous)\b', text))
        
        # Count punctuation
        punctuation_count = len(re.findall(r'[.!?,:;]', text))
        
        return {
            'word_count': len(words),
            'estimated_nouns': nouns,
            'estimated_verbs': verbs,
            'estimated_adjectives': adjectives,
            'punctuation_density': punctuation_count / len(words) if words else 0,
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
    
    def _generate_shingles(self, text: str, k: int = 5) -> List[str]:
        """Generate k-shingles from text"""        # Character-based shingles
        shingles = []
        text_clean = re.sub(r'\s+', '', text)  # Remove all whitespace
        
        for i in range(len(text_clean) - k + 1):
            shingle = text_clean[i:i + k]
            shingle_hash = hashlib.md5(shingle.encode('utf-8')).hexdigest()[:8]
            shingles.append(shingle_hash)
        
        return list(set(shingles))  # Return unique shingles
    
    def _assess_text_fingerprint_quality(self, text: str) -> Dict[str, Any]:
        """Assess the quality of text fingerprint"""        words = text.split()
        unique_words = set(word.lower() for word in words)
        
        # Calculate metrics
        lexical_diversity = len(unique_words) / len(words) if words else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        text_length = len(text)
        
        # Quality score based on text complexity and uniqueness
        quality_score = min(100, (lexical_diversity * 50 + avg_word_length * 5 + min(text_length / 1000, 1) * 40))
        
        return {
            'quality_score': float(quality_score),
            'lexical_diversity': float(lexical_diversity),
            'avg_word_length': float(avg_word_length),
            'text_length': text_length,
            'suitable_for_fingerprinting': quality_score > 30 and text_length > 100
        }


# Import TAGS for EXIF data (fallback if not available)
try:
    from PIL.ExifTags import TAGS
except ImportError:
    TAGS = {}
