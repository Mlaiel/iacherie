"""Multimedia Metadata Extraction Module
Comprehensive metadata extraction for all multimedia formats

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer, Backend Senior Engineer, ML Engineer, 
              Database Administrator, Security Expert, Microservices Architect,
              Multimedia Processing Specialist, DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
import hashlib
import json
from abc import ABC, abstractmethod

import librosa
import soundfile as sf
import mutagen
from mutagen.id3 import ID3
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import cv2
from moviepy import VideoFileClip
import ffmpeg
import numpy as np

from .formats import ContentFormat, AudioFormat, VideoFormat, ImageFormat, SupportedFormats

logger = logging.getLogger(__name__)


@dataclass
class BaseMetadata:
    """
Base metadata structure for all content types"""
    content_id: str
    file_path: Optional[Path] = None
    filename: Optional[str] = None
    file_size: int = 0
    mime_type: Optional[str] = None
    format: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioMetadata(BaseMetadata):
    """
Comprehensive audio metadata"""
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    
    # ID3/Tag metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    album_artist: Optional[str] = None
    composer: Optional[str] = None
    copyright: Optional[str] = None
    comment: Optional[str] = None
    
    # Technical analysis
    tempo: Optional[float] = None
    key: Optional[str] = None
    loudness: Optional[float] = None  # LUFS
    dynamic_range: Optional[float] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    
    # Quality metrics
    quality_score: float = 0.0
    has_clipping: bool = False
    signal_to_noise_ratio: Optional[float] = None
    
    # Additional features
    mfcc_features: Optional[List[float]] = None
    chroma_features: Optional[List[float]] = None
    spectral_features: Dict[str, float] = field(default_factory=dict)
    
    # Embedded artwork
    has_artwork: bool = False
    artwork_format: Optional[str] = None
    artwork_size: Optional[Tuple[int, int]] = None


@dataclass
class VideoMetadata(BaseMetadata):
    """
Comprehensive video metadata"""
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    fps: Optional[float] = None
    total_frames: Optional[int] = None
    
    # Video codec information
    video_codec: Optional[str] = None
    video_bitrate: Optional[int] = None
    pixel_format: Optional[str] = None
    color_space: Optional[str] = None
    color_profile: Optional[str] = None
    
    # Audio track information
    has_audio: bool = False
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    
    # Container metadata
    container_format: Optional[str] = None
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    subtitles: List[Dict[str, str]] = field(default_factory=list)
    
    # Technical analysis
    scene_changes: List[float] = field(default_factory=list)
    motion_vectors: List[Dict[str, float]] = field(default_factory=list)
    keyframe_intervals: List[float] = field(default_factory=list)
    
    # Quality metrics
    quality_score: float = 0.0
    average_bitrate: Optional[int] = None
    compression_ratio: Optional[float] = None
    
    # Visual analysis
    brightness_histogram: Optional[List[float]] = None
    color_histogram: Optional[Dict[str, List[float]]] = None
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    
    # HDR/Advanced features
    hdr_metadata: Optional[Dict[str, Any]] = None
    dolby_vision: bool = False
    hdr10_plus: bool = False


@dataclass
class ImageMetadata(BaseMetadata):
    """
Comprehensive image metadata"""
    width: Optional[int] = None
    height: Optional[int] = None
    color_mode: Optional[str] = None
    bit_depth: Optional[int] = None
    compression: Optional[str] = None
    
    # EXIF metadata
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash_used: Optional[bool] = None
    
    # GPS metadata
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None
    location_name: Optional[str] = None
    
    # Timestamp metadata
    date_taken: Optional[datetime] = None
    date_digitized: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    
    # Image analysis
    quality_score: float = 0.0
    sharpness_score: float = 0.0
    noise_level: float = 0.0
    contrast_score: float = 0.0
    saturation_level: float = 0.0
    brightness_level: float = 0.0
    
    # Color analysis
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_temperature: Optional[int] = None
    color_histogram: Optional[Dict[str, List[float]]] = None
    
    # Feature analysis
    face_count: int = 0
    object_count: int = 0
    text_regions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Technical features
    has_transparency: bool = False
    has_animation: bool = False
    has_layers: bool = False
    icc_profile: Optional[str] = None
    
    # Thumbnail information
    has_thumbnail: bool = False
    thumbnail_size: Optional[Tuple[int, int]] = None


@dataclass
class MultimediaMetadata:
    """
Combined metadata for multimodal content"""
    content_id: str
    primary_format: ContentFormat
    audio_metadata: Optional[AudioMetadata] = None
    video_metadata: Optional[VideoMetadata] = None
    image_metadata: Optional[ImageMetadata] = None
    
    # Cross-modal analysis
    synchronization_offset: Optional[float] = None
    audio_video_alignment: Optional[float] = None
    content_coherence_score: float = 0.0
    
    # Combined metrics
    total_duration: Optional[float] = None
    total_size: int = 0
    overall_quality_score: float = 0.0
    
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


class MetadataExtractor(ABC):
    """
Abstract base class for metadata extractors"""
    
    @abstractmethod
    async def extract(self, content_path: Path) -> BaseMetadata:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_extract_input(content_path)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_result(result)
            
                    logger.info(f"AI processing extract completed")
                    return final_result
            
                except Exception as e:
            logger.error(f"Error: {e}")
            raise

    def placeholder_method(self):
        """Placeholder method"""  
        try:
            logger.info(f"Executing supports_format")
            
            # Implementation for supports_format
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"supports_format completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"supports_format failed: {e}")
            raise
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_result(result)
            
                    logger.info(f"AI processing extract completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing extract failed: {e}")
                    raise
    @abstractmethod
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if extractor supports format"""
        pass
    
    def _calculate_file_hashes(self, file_path: Path) -> Tuple[str, str]:
        """
Calculate MD5 and SHA256 hashes"""
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
        
        return md5_hash.hexdigest(), sha256_hash.hexdigest()
    
    def _get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get basic file system metadata"""
        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        return {
            'file_size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime),
            'modified_at': datetime.fromtimestamp(stat.st_mtime),
            'mime_type': mime_type,
            'filename': file_path.name
        }


class AudioMetadataExtractor(MetadataExtractor):
    """
Professional audio metadata extractor"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if extractor supports audio format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.AUDIO
        return SupportedFormats.is_audio_format(format_type)
    
    async def extract(self, content_path: Path) -> AudioMetadata:
        """
Extract comprehensive audio metadata"""
        content_id = hashlib.sha256(str(content_path).encode()).hexdigest()[:16]
        
        # Basic file metadata
        file_metadata = self._get_file_metadata(content_path)
        md5_hash, sha256_hash = self._calculate_file_hashes(content_path)
        
        metadata = AudioMetadata(
            content_id=content_id,
            file_path=content_path,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            **file_metadata
        )
        
        try:
            # Load audio for analysis
            audio_data, sample_rate = librosa.load(str(content_path), sr=None)
            
            # Basic audio properties
            metadata.duration = len(audio_data) / sample_rate
            metadata.sample_rate = sample_rate
            metadata.channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            
            # Extract tags using mutagen
            await self._extract_audio_tags(metadata, content_path)
            
            # Technical analysis
            await self._analyze_audio_technical_properties(metadata, audio_data, sample_rate)
            
            # Quality assessment
            await self._assess_audio_quality(metadata, audio_data, sample_rate)
            
            # Feature extraction
            await self._extract_audio_features(metadata, audio_data, sample_rate)
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {str(e)}")
            metadata.custom_metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_audio_tags(self, metadata: AudioMetadata, file_path: Path):
        """Extract ID3 and other audio tags"""
        try:
            audio_file = mutagen.File(str(file_path))
            if audio_file is None:
                return
            
            # Common tag mappings
            tag_mappings = {
                'TIT2': 'title', 'TIT1': 'title',
                'TPE1': 'artist', 'TPE2': 'album_artist',
                'TALB': 'album',
                'TCON': 'genre',
                'TDRC': 'year', 'TYER': 'year',
                'TRCK': 'track_number',
                'TPOS': 'total_tracks',
                'TCOM': 'composer',
                'TCOP': 'copyright',
                'COMM::eng': 'comment'
            }
            
            # Extract tags based on file format
            if hasattr(audio_file, 'tags') and audio_file.tags:
                for key, value in audio_file.tags.items():
                    if isinstance(value, list):
                        value = value[0] if value else None
                    
                    # Map to metadata fields
                    if str(key) in tag_mappings:
                        setattr(metadata, tag_mappings[str(key)], str(value))
                    
                    # Store original tag
                    metadata.custom_metadata[f'tag_{key}'] = str(value)
            
            # Extract embedded artwork
            if 'APIC:' in audio_file.tags:
                artwork = audio_file.tags['APIC:']
                metadata.has_artwork = True
                metadata.artwork_format = artwork.mime
                
                # Try to get artwork dimensions
                try:
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(artwork.data))
                    metadata.artwork_size = img.size
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Tag extraction failed: {str(e)}")
    
    async def _analyze_audio_technical_properties(self, metadata: AudioMetadata, 
                                                audio_data: np.ndarray, sample_rate: int):
        """Analyze technical audio properties"""
        try:
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            metadata.tempo = float(tempo)
            
            # Key estimation (simplified)
            chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
            key_profile = np.mean(chroma, axis=1)
            key_index = np.argmax(key_profile)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            metadata.key = keys[key_index]
            
            # Loudness analysis (simplified LUFS approximation)
            rms_energy = librosa.feature.rms(y=audio_data)
            metadata.loudness = float(20 * np.log10(np.mean(rms_energy) + 1e-10))
            
            # Dynamic range
            peak_amplitude = np.max(np.abs(audio_data))
            rms_amplitude = np.sqrt(np.mean(audio_data**2))
            if rms_amplitude > 0:
                metadata.dynamic_range = float(20 * np.log10(peak_amplitude / rms_amplitude))
            
            # Spectral features
            metadata.spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)))
            metadata.zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
            
        except Exception as e:
            logger.warning(f"Technical analysis failed: {str(e)}")
    
    async def _assess_audio_quality(self, metadata: AudioMetadata, 
                                  audio_data: np.ndarray, sample_rate: int):
        """Assess audio quality"""
        try:
            # Clipping detection
            clipping_threshold = 0.95
            metadata.has_clipping = np.any(np.abs(audio_data) > clipping_threshold)
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data**2)
            # Estimate noise from high-frequency content
            noise_estimate = np.std(librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate))
            if noise_estimate > 0:
                metadata.signal_to_noise_ratio = float(10 * np.log10(signal_power / (noise_estimate**2)))
            
            # Overall quality score
            quality_factors = []
            
            # Sample rate quality (higher is better)
            if metadata.sample_rate:
                sr_score = min(metadata.sample_rate / 48000, 1.0)
                quality_factors.append(sr_score * 0.3)
            
            # Dynamic range quality
            if metadata.dynamic_range:
                dr_score = min(metadata.dynamic_range / 20, 1.0)
                quality_factors.append(dr_score * 0.3)
            
            # No clipping bonus
            if not metadata.has_clipping:
                quality_factors.append(0.2)
            
            # SNR quality
            if metadata.signal_to_noise_ratio:
                snr_score = min(metadata.signal_to_noise_ratio / 60, 1.0)
                quality_factors.append(snr_score * 0.2)
            
            metadata.quality_score = sum(quality_factors)
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {str(e)}")
    
    async def _extract_audio_features(self, metadata: AudioMetadata, 
                                    audio_data: np.ndarray, sample_rate: int):
        """Extract advanced audio features"""
        try:
            # MFCC coefficients
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            metadata.mfcc_features = np.mean(mfcc, axis=1).tolist()
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            metadata.chroma_features = np.mean(chroma, axis=1).tolist()
            
            # Additional spectral features
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)
            
            metadata.spectral_features = {
                'rolloff_mean': float(np.mean(spectral_rolloff)),
                'bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'flatness_mean': float(np.mean(spectral_flatness))
            }
            
        except Exception as e:
            logger.warning(f"Feature extraction failed: {str(e)}")


class VideoMetadataExtractor(MetadataExtractor):
    """Professional video metadata extractor"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if extractor supports video format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.VIDEO
        return SupportedFormats.is_video_format(format_type)
    
    async def extract(self, content_path: Path) -> VideoMetadata:
        """
Extract comprehensive video metadata"""
        content_id = hashlib.sha256(str(content_path).encode()).hexdigest()[:16]
        
        # Basic file metadata
        file_metadata = self._get_file_metadata(content_path)
        md5_hash, sha256_hash = self._calculate_file_hashes(content_path)
        
        metadata = VideoMetadata(
            content_id=content_id,
            file_path=content_path,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            **file_metadata
        )
        
        try:
            # Extract using ffprobe
            await self._extract_with_ffprobe(metadata, content_path)
            
            # Extract using MoviePy for additional analysis
            await self._extract_with_moviepy(metadata, content_path)
            
            # Analyze video content
            await self._analyze_video_content(metadata, content_path)
            
            # Assess quality
            await self._assess_video_quality(metadata)
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {str(e)}")
            metadata.custom_metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_with_ffprobe(self, metadata: VideoMetadata, file_path: Path):
        """Extract metadata using ffprobe"""
        try:
            probe = ffmpeg.probe(str(file_path))
            
            # Video stream info
            video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
            if video_streams:
                video_stream = video_streams[0]
                
                metadata.width = int(video_stream.get('width', 0))
                metadata.height = int(video_stream.get('height', 0))
                
                if metadata.width and metadata.height:
                    metadata.aspect_ratio = metadata.width / metadata.height
                
                # FPS calculation
                fps_str = video_stream.get('r_frame_rate', '0/1')
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    if int(den) != 0:
                        metadata.fps = float(num) / float(den)
                
                metadata.video_codec = video_stream.get('codec_name')
                metadata.pixel_format = video_stream.get('pix_fmt')
                
                # Bitrate
                if 'bit_rate' in video_stream:
                    metadata.video_bitrate = int(video_stream['bit_rate'])
            
            # Audio stream info
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            if audio_streams:
                audio_stream = audio_streams[0]
                metadata.has_audio = True
                metadata.audio_codec = audio_stream.get('codec_name')
                metadata.audio_channels = int(audio_stream.get('channels', 0))
                metadata.audio_sample_rate = int(audio_stream.get('sample_rate', 0))
                
                if 'bit_rate' in audio_stream:
                    metadata.audio_bitrate = int(audio_stream['bit_rate'])
            
            # Format info
            if 'format' in probe:
                format_info = probe['format']
                metadata.duration = float(format_info.get('duration', 0))
                metadata.container_format = format_info.get('format_name')
                
                if 'bit_rate' in format_info:
                    metadata.average_bitrate = int(format_info['bit_rate'])
                
                # Tags
                if 'tags' in format_info:
                    for key, value in format_info['tags'].items():
                        metadata.custom_metadata[f'tag_{key.lower()}'] = value
                        
        except Exception as e:
            logger.warning(f"ffprobe extraction failed: {str(e)}")
    
    async def _extract_with_moviepy(self, metadata: VideoMetadata, file_path: Path):
        """Extract additional metadata using MoviePy"""
        try:
            video_clip = VideoFileClip(str(file_path))
            
            # Verify duration
            if not metadata.duration:
                metadata.duration = video_clip.duration
            
            # Frame count estimation
            if metadata.fps and metadata.duration:
                metadata.total_frames = int(metadata.fps * metadata.duration)
            
            # Additional audio verification
            if video_clip.audio is not None and not metadata.has_audio:
                metadata.has_audio = True
            
            video_clip.close()
            
        except Exception as e:
            logger.warning(f"MoviePy extraction failed: {str(e)}")
    
    async def _analyze_video_content(self, metadata: VideoMetadata, file_path: Path):
        """Analyze video visual content"""
        try:
            video_clip = VideoFileClip(str(file_path))
            
            if metadata.duration and metadata.duration > 0:
                # Sample frames for analysis
                sample_times = [
                    metadata.duration * 0.1,
                    metadata.duration * 0.5,
                    metadata.duration * 0.9
                ]
                
                frames = []
                for time_point in sample_times:
                    if time_point < metadata.duration:
                        frame = video_clip.get_frame(time_point)
                        frames.append(frame)
                
                if frames:
                    # Color analysis
                    await self._analyze_video_colors(metadata, frames)
                    
                    # Motion analysis
                    if len(frames) > 1:
                        await self._analyze_video_motion(metadata, frames)
                    
                    # Scene complexity
                    await self._analyze_scene_complexity(metadata, frames)
            
            video_clip.close()
            
        except Exception as e:
            logger.warning(f"Video content analysis failed: {str(e)}")
    
    async def _analyze_video_colors(self, metadata: VideoMetadata, frames: List[np.ndarray]):
        """Analyze color composition in video frames"""
        try:
            all_pixels = []
            brightness_values = []
            
            for frame in frames:
                # Collect pixels for color analysis
                pixels = frame.reshape(-1, 3)
                all_pixels.append(pixels)
                
                # Brightness analysis
                brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
                brightness_values.append(brightness)
            
            # Overall brightness histogram
            metadata.brightness_histogram = brightness_values
            
            # Dominant colors (simplified)
            if all_pixels:
                combined_pixels = np.vstack(all_pixels)
                # Sample pixels for performance
                sample_size = min(10000, len(combined_pixels))
                sample_indices = np.random.choice(len(combined_pixels), sample_size, replace=False)
                sampled_pixels = combined_pixels[sample_indices]
                
                # K-means clustering for dominant colors
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
                kmeans.fit(sampled_pixels)
                
                dominant_colors = []
                for color in kmeans.cluster_centers_:
                    dominant_colors.append((int(color[0]), int(color[1]), int(color[2])))
                
                metadata.dominant_colors = dominant_colors
                
        except Exception as e:
            logger.warning(f"Color analysis failed: {str(e)}")
    
    async def _analyze_video_motion(self, metadata: VideoMetadata, frames: List[np.ndarray]):
        """Analyze motion between video frames"""
        try:
            motion_vectors = []
            scene_changes = []
            
            for i in range(1, len(frames)):
                prev_frame = cv2.cvtColor(frames[i-1], cv2.COLOR_RGB2GRAY)
                curr_frame = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, curr_frame, 
                    np.array([[100, 100]], dtype=np.float32).reshape(-1, 1, 2),
                    None
                )
                
                if flow[0] is not None:
                    motion_magnitude = np.linalg.norm(flow[0] - np.array([[100, 100]], dtype=np.float32))
                    motion_vectors.append({
                        'magnitude': float(motion_magnitude),
                        'frame_index': i
                    })
                
                # Scene change detection (simplified)
                diff = cv2.absdiff(prev_frame, curr_frame)
                change_score = np.sum(diff > 30) / (diff.shape[0] * diff.shape[1])
                
                if change_score > 0.3:  # Threshold for scene change
                    scene_changes.append(float(i))
            
            metadata.motion_vectors = motion_vectors
            metadata.scene_changes = scene_changes
            
        except Exception as e:
            logger.warning(f"Motion analysis failed: {str(e)}")
    
    async def _analyze_scene_complexity(self, metadata: VideoMetadata, frames: List[np.ndarray]):
        """Analyze visual complexity of scenes"""
        try:
            complexity_scores = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Edge density as complexity measure
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                
                # Texture complexity using gradient magnitude
                grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                texture_complexity = np.std(gradient_magnitude)
                
                complexity_score = (edge_density * 0.5 + texture_complexity / 255 * 0.5)
                complexity_scores.append(complexity_score)
            
            # Store average complexity
            metadata.custom_metadata['scene_complexity'] = float(np.mean(complexity_scores))
            
        except Exception as e:
            logger.warning(f"Scene complexity analysis failed: {str(e)}")
    
    async def _assess_video_quality(self, metadata: VideoMetadata):
        """Assess overall video quality"""
        try:
            quality_factors = []
            
            # Resolution quality
            if metadata.width and metadata.height:
                total_pixels = metadata.width * metadata.height
                # Normalize based on 4K (3840x2160)
                resolution_score = min(total_pixels / (3840 * 2160), 1.0)
                quality_factors.append(resolution_score * 0.3)
            
            # Frame rate quality
            if metadata.fps:
                fps_score = min(metadata.fps / 60, 1.0)
                quality_factors.append(fps_score * 0.2)
            
            # Bitrate quality
            if metadata.video_bitrate:
                # Normalize based on typical high-quality bitrate
                bitrate_score = min(metadata.video_bitrate / 10000000, 1.0)  # 10 Mbps
                quality_factors.append(bitrate_score * 0.3)
            
            # Codec efficiency
            if metadata.video_codec:
                codec_scores = {
                    'h264': 0.8,
                    'h265': 0.9,
                    'hevc': 0.9,
                    'vp9': 0.85,
                    'av1': 0.95
                }
                codec_score = codec_scores.get(metadata.video_codec.lower(), 0.5)
                quality_factors.append(codec_score * 0.2)
            
            metadata.quality_score = sum(quality_factors)
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {str(e)}")


class ImageMetadataExtractor(MetadataExtractor):
    """Professional image metadata extractor"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if extractor supports image format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.IMAGE
        return SupportedFormats.is_image_format(format_type)
    
    async def extract(self, content_path: Path) -> ImageMetadata:
        """
Extract comprehensive image metadata"""
        content_id = hashlib.sha256(str(content_path).encode()).hexdigest()[:16]
        
        # Basic file metadata
        file_metadata = self._get_file_metadata(content_path)
        md5_hash, sha256_hash = self._calculate_file_hashes(content_path)
        
        metadata = ImageMetadata(
            content_id=content_id,
            file_path=content_path,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            **file_metadata
        )
        
        try:
            with Image.open(content_path) as image:
                # Basic image properties
                metadata.width = image.width
                metadata.height = image.height
                metadata.color_mode = image.mode
                metadata.format = image.format
                
                # Transparency and animation detection
                metadata.has_transparency = image.mode in ('RGBA', 'LA') or 'transparency' in image.info
                metadata.has_animation = getattr(image, 'is_animated', False)
                
                # Extract EXIF data
                await self._extract_exif_data(metadata, image)
                
                # Analyze image content
                await self._analyze_image_content(metadata, image)
                
                # Assess image quality
                await self._assess_image_quality(metadata, image)
                
                # Feature detection
                await self._detect_image_features(metadata, image)
                
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {str(e)}")
            metadata.custom_metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_exif_data(self, metadata: ImageMetadata, image: Image.Image):
        """Extract EXIF metadata from image"""
        try:
            exif = image.getexif()
            if not exif:
                return
            
            # EXIF tag mappings
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                # Map common EXIF tags to metadata fields
                if tag_name == 'Make':
                    metadata.camera_make = str(value)
                elif tag_name == 'Model':
                    metadata.camera_model = str(value)
                elif tag_name == 'LensModel':
                    metadata.lens_model = str(value)
                elif tag_name == 'FocalLength':
                    if isinstance(value, tuple):
                        metadata.focal_length = float(value[0] / value[1])
                    else:
                        metadata.focal_length = float(value)
                elif tag_name == 'FNumber':
                    if isinstance(value, tuple):
                        metadata.aperture = float(value[0] / value[1])
                    else:
                        metadata.aperture = float(value)
                elif tag_name == 'ExposureTime':
                    if isinstance(value, tuple):
                        metadata.shutter_speed = f"1/{int(value[1]/value[0])}"
                    else:
                        metadata.shutter_speed = str(value)
                elif tag_name == 'ISOSpeedRatings':
                    metadata.iso = int(value)
                elif tag_name == 'Flash':
                    metadata.flash_used = bool(value & 1)  # Check if flash fired
                elif tag_name == 'DateTime':
                    try:
                        metadata.date_taken = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                    except:
                        pass
                elif tag_name == 'DateTimeDigitized':
                    try:
                        metadata.date_digitized = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                    except:
                        pass
                
                # Store all EXIF data
                metadata.custom_metadata[f'exif_{tag_name}'] = str(value)
            
            # GPS data extraction
            gps_info = exif.get_ifd(0x8825)  # GPS IFD
            if gps_info:
                await self._extract_gps_data(metadata, gps_info)
                
        except Exception as e:
            logger.warning(f"EXIF extraction failed: {str(e)}")
    
    async def _extract_gps_data(self, metadata: ImageMetadata, gps_info):
        """Extract GPS coordinates from EXIF"""
        try:
            def convert_to_degrees(value):
                """
Convert GPS coordinates to decimal degrees"""
                if isinstance(value, tuple) and len(value) == 3:
                    degrees = float(value[0])
                    minutes = float(value[1])
                    seconds = float(value[2])
                    return degrees + (minutes / 60.0) + (seconds / 3600.0)
                return 0.0
            
            lat = gps_info.get(2)  # GPSLatitude
            lat_ref = gps_info.get(1)  # GPSLatitudeRef
            lon = gps_info.get(4)  # GPSLongitude
            lon_ref = gps_info.get(3)  # GPSLongitudeRef
            alt = gps_info.get(6)  # GPSAltitude
            
            if lat and lon:
                metadata.gps_latitude = convert_to_degrees(lat)
                if lat_ref and lat_ref.upper() == 'S':
                    metadata.gps_latitude = -metadata.gps_latitude
                
                metadata.gps_longitude = convert_to_degrees(lon)
                if lon_ref and lon_ref.upper() == 'W':
                    metadata.gps_longitude = -metadata.gps_longitude
            
            if alt:
                if isinstance(alt, tuple):
                    metadata.gps_altitude = float(alt[0] / alt[1])
                else:
                    metadata.gps_altitude = float(alt)
                    
        except Exception as e:
            logger.warning(f"GPS extraction failed: {str(e)}")
    
    async def _analyze_image_content(self, metadata: ImageMetadata, image: Image.Image):
        """Analyze image visual content"""
        try:
            # Convert to RGB for analysis
            rgb_image = image.convert('RGB')
            img_array = np.array(rgb_image)
            
            # Color analysis
            await self._analyze_image_colors(metadata, img_array)
            
            # Brightness and contrast analysis
            metadata.brightness_level = float(np.mean(img_array) / 255.0)
            metadata.contrast_score = float(np.std(img_array) / 128.0)
            
            # Saturation analysis
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            metadata.saturation_level = float(np.mean(hsv[:, :, 1]) / 255.0)
            
            # Color temperature estimation
            metadata.color_temperature = await self._estimate_color_temperature(img_array)
            
        except Exception as e:
            logger.warning(f"Image content analysis failed: {str(e)}")
    
    async def _analyze_image_colors(self, metadata: ImageMetadata, img_array: np.ndarray):
        """Analyze color composition"""
        try:
            # Reshape for color analysis
            pixels = img_array.reshape(-1, 3)
            
            # Sample pixels for performance
            sample_size = min(10000, len(pixels))
            sample_indices = np.random.choice(len(pixels), sample_size, replace=False)
            sampled_pixels = pixels[sample_indices]
            
            # K-means clustering for dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(sampled_pixels)
            
            dominant_colors = []
            for color in kmeans.cluster_centers_:
                dominant_colors.append((int(color[0]), int(color[1]), int(color[2])))
            
            metadata.dominant_colors = dominant_colors
            
            # Color histogram
            hist_r = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))[0]
            hist_g = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))[0]
            hist_b = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))[0]
            
            metadata.color_histogram = {
                'red': hist_r.tolist(),
                'green': hist_g.tolist(),
                'blue': hist_b.tolist()
            }
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {str(e)}")
    
    async def _estimate_color_temperature(self, img_array: np.ndarray) -> Optional[int]:
        """Estimate color temperature in Kelvin"""
        try:
            # Simple color temperature estimation based on R/B ratio
            avg_r = np.mean(img_array[:, :, 0])
            avg_g = np.mean(img_array[:, :, 1])
            avg_b = np.mean(img_array[:, :, 2])
            
            # Avoid division by zero
            if avg_b == 0:
                avg_b = 1
            
            rb_ratio = avg_r / avg_b
            
            # Simple mapping (rough approximation)
            if rb_ratio > 1.5:
                return 2000  # Very warm
            elif rb_ratio > 1.2:
                return 3000  # Warm
            elif rb_ratio > 1.0:
                return 4000  # Slightly warm
            elif rb_ratio > 0.9:
                return 5500  # Daylight
            elif rb_ratio > 0.8:
                return 6500  # Cool daylight
            else:
                return 8000  # Very cool
                
        except:
            return None
    
    async def _assess_image_quality(self, metadata: ImageMetadata, image: Image.Image):
        """
Assess overall image quality"""
        try:
            img_array = np.array(image.convert('RGB'))
            
            # Sharpness assessment using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            metadata.sharpness_score = float(laplacian.var() / 1000)  # Normalize
            metadata.sharpness_score = min(metadata.sharpness_score, 1.0)
            
            # Noise level estimation
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            filtered = cv2.filter2D(gray, cv2.CV_64F, kernel)
            metadata.noise_level = float(np.std(filtered) / 50)  # Normalize
            metadata.noise_level = min(metadata.noise_level, 1.0)
            
            # Overall quality score
            quality_factors = []
            
            # Resolution factor
            total_pixels = metadata.width * metadata.height
            resolution_score = min(total_pixels / (1920 * 1080), 1.0)  # Normalize to 1080p
            quality_factors.append(resolution_score * 0.3)
            
            # Sharpness factor
            quality_factors.append(metadata.sharpness_score * 0.3)
            
            # Low noise factor
            quality_factors.append((1.0 - metadata.noise_level) * 0.2)
            
            # Contrast factor
            quality_factors.append(min(metadata.contrast_score, 1.0) * 0.2)
            
            metadata.quality_score = sum(quality_factors)
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {str(e)}")
    
    async def _detect_image_features(self, metadata: ImageMetadata, image: Image.Image):
        """Detect faces, objects, and text in image"""
        try:
            img_array = np.array(image.convert('RGB'))
            
            # Simple face detection using OpenCV
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                metadata.face_count = len(faces)
            except:
                metadata.face_count = 0
            
            # Simple object detection using contours
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Count significant objects (large contours)
            significant_objects = [c for c in contours if cv2.contourArea(c) > 1000]
            metadata.object_count = len(significant_objects)
            
            # Text region detection (simplified)
            try:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            significant_objects = [c for c in contours if cv2.contourArea(c) > 1000]
            metadata.object_count = len(significant_objects)
            
            # Text region detection (simplified)
            try:
                # Use edge density to estimate text regions
                kernel = np.ones((5, 5), np.uint8)
                dilated = cv2.dilate(edges, kernel, iterations=1)
                text_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                text_regions = []
                for contour in text_contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    area = cv2.contourArea(contour)
                    
                    # Heuristic for text-like regions
                    if 0.5 < aspect_ratio < 10 and area > 500:
                        text_regions.append({
                            'bbox': [int(x), int(y), int(w), int(h)],
                            'area': float(area),
                            'aspect_ratio': float(aspect_ratio)
                        })
                
                metadata.text_regions = text_regions[:10]  # Limit to top 10
                
            except Exception as e:
                logger.warning(f"Text detection failed: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Feature detection failed: {str(e)}")


class UniversalMetadataExtractor:
    """Universal metadata extractor for all multimedia formats"""
    
    def __init__(self):
        self.extractors = {
            ContentFormat.AUDIO: AudioMetadataExtractor(),
            ContentFormat.VIDEO: VideoMetadataExtractor(),
            ContentFormat.IMAGE: ImageMetadataExtractor()
        }
    
    async def extract(self, content_path: Path, 
                     content_type: Optional[Union[str, ContentFormat]] = None) -> BaseMetadata:
        """
Extract metadata from any supported multimedia format"""
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content_path)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate extractor
        extractor = self.extractors.get(content_type)
        if extractor is None:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Extract metadata
        return await extractor.extract(content_path)
    
    def _detect_content_type(self, content_path: Path) -> ContentFormat:
        """Auto-detect content type from file extension"""
        extension = content_path.suffix.lower().lstrip('.')
        format_enum = SupportedFormats.get_format_by_extension(extension)
        
        if format_enum:
            if isinstance(format_enum, AudioFormat):
                return ContentFormat.AUDIO
            elif isinstance(format_enum, VideoFormat):
                return ContentFormat.VIDEO
            elif isinstance(format_enum, ImageFormat):
                return ContentFormat.IMAGE
        
        raise ValueError(f"Unable to detect content type for extension: {extension}")
    
    def get_supported_formats(self) -> Dict[ContentFormat, List[str]]:
        """Get all supported formats by content type"""
        return {
            ContentFormat.AUDIO: [fmt.value for fmt in AudioFormat],
            ContentFormat.VIDEO: [fmt.value for fmt in VideoFormat],
            ContentFormat.IMAGE: [fmt.value for fmt in ImageFormat]
        }
    
    async def extract_multimodal(self, content_paths: Dict[ContentFormat, Path]) -> MultimediaMetadata:
        """
Extract metadata from multimodal content"""
        
        # Generate combined content ID
        path_strings = [str(path) for path in content_paths.values()]
        combined_id = hashlib.sha256('_'.join(path_strings).encode()).hexdigest()[:16]
        
        # Determine primary format (video > audio > image)
        primary_format = ContentFormat.IMAGE
        if ContentFormat.VIDEO in content_paths:
            primary_format = ContentFormat.VIDEO
        elif ContentFormat.AUDIO in content_paths:
            primary_format = ContentFormat.AUDIO
        
        metadata = MultimediaMetadata(
            content_id=combined_id,
            primary_format=primary_format
        )
        
        # Extract metadata for each content type
        total_size = 0
        durations = []
        quality_scores = []
        
        for content_type, path in content_paths.items():
            try:
                extracted_metadata = await self.extract(path, content_type)
                
                if content_type == ContentFormat.AUDIO:
                    metadata.audio_metadata = extracted_metadata
                elif content_type == ContentFormat.VIDEO:
                    metadata.video_metadata = extracted_metadata
                elif content_type == ContentFormat.IMAGE:
                    metadata.image_metadata = extracted_metadata
                
                # Aggregate metrics
                total_size += extracted_metadata.file_size
                
                if hasattr(extracted_metadata, 'duration') and extracted_metadata.duration:
                    durations.append(extracted_metadata.duration)
                
                if hasattr(extracted_metadata, 'quality_score') and extracted_metadata.quality_score:
                    quality_scores.append(extracted_metadata.quality_score)
                    
            except Exception as e:
                logger.error(f"Failed to extract metadata for {content_type}: {str(e)}")
                metadata.processing_metadata[f'{content_type.value}_error'] = str(e)
        
        # Calculate combined metrics
        metadata.total_size = total_size
        
        if durations:
            metadata.total_duration = max(durations)  # Use longest duration
        
        if quality_scores:
            metadata.overall_quality_score = sum(quality_scores) / len(quality_scores)
        
        # Analyze cross-modal coherence
        await self._analyze_cross_modal_coherence(metadata)
        
        return metadata
    
    async def _analyze_cross_modal_coherence(self, metadata: MultimediaMetadata):
        """Analyze coherence between different modalities"""
        try:
            coherence_factors = []
            
            # Audio-video synchronization (if both present)
            if metadata.audio_metadata and metadata.video_metadata:
                audio_duration = metadata.audio_metadata.duration or 0
                video_duration = metadata.video_metadata.duration or 0
                
                if audio_duration > 0 and video_duration > 0:
                    duration_ratio = min(audio_duration, video_duration) / max(audio_duration, video_duration)
                    coherence_factors.append(duration_ratio * 0.4)
                    
                    # Store synchronization offset
                    metadata.synchronization_offset = abs(audio_duration - video_duration)
                    metadata.audio_video_alignment = duration_ratio
            
            # Quality consistency
            quality_scores = []
            if metadata.audio_metadata and hasattr(metadata.audio_metadata, 'quality_score'):
                quality_scores.append(metadata.audio_metadata.quality_score)
            if metadata.video_metadata and hasattr(metadata.video_metadata, 'quality_score'):
                quality_scores.append(metadata.video_metadata.quality_score)
            if metadata.image_metadata and hasattr(metadata.image_metadata, 'quality_score'):
                quality_scores.append(metadata.image_metadata.quality_score)
            
            if len(quality_scores) > 1:
                quality_consistency = 1.0 - (np.std(quality_scores) / np.mean(quality_scores))
                coherence_factors.append(quality_consistency * 0.3)
            
            # Resolution consistency (video and image)
            if metadata.video_metadata and metadata.image_metadata:
                video_res = (metadata.video_metadata.width or 0) * (metadata.video_metadata.height or 0)
                image_res = (metadata.image_metadata.width or 0) * (metadata.image_metadata.height or 0)
                
                if video_res > 0 and image_res > 0:
                    resolution_ratio = min(video_res, image_res) / max(video_res, image_res)
                    coherence_factors.append(resolution_ratio * 0.3)
            
            # Calculate overall coherence score
            if coherence_factors:
                metadata.content_coherence_score = sum(coherence_factors)
            else:
                metadata.content_coherence_score = 1.0  # Single modality is perfectly coherent
                
        except Exception as e:
            logger.warning(f"Cross-modal coherence analysis failed: {str(e)}")
            metadata.content_coherence_score = 0.5  # Default moderate coherence
