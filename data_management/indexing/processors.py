"""
IA Influencer Agent - Advanced Content Processors
=================================================

Multi-format content processing for indexing with specialized handlers
for audio, video, image, text, and combined multi-format processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

  INTELLECTUAL PROPERTY WARNING 
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import hashlib
import logging
import mimetypes
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import librosa
import cv2
from PIL import Image, ExifTags
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import mutagen
from mutagen.id3 import ID3
import pytesseract
from textstat import flesch_reading_ease, syllable_count
import spacy
import langdetect

logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for content processors"""
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    audio_sample_rate: int = 22050
    image_max_dimension: int = 2048
    video_fps_limit: int = 30
    text_max_length: int = 100000
    enable_gpu: bool = True
    temp_directory: str = "/tmp/ia_influencer"
    supported_audio_formats: List[str] = None
    supported_video_formats: List[str] = None
    supported_image_formats: List[str] = None


class BaseContentProcessor(ABC):
    """Abstract base class for content processors"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the processor"""
        pass
    
    @abstractmethod
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process content and extract features"""
        pass
    
    @abstractmethod
    def supports_format(self, file_path: str) -> bool:
        """Check if the processor supports the file format"""
        pass
    
    async def validate_file(self, file_path: str) -> bool:
        """Validate file before processing"""



        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            file_size = path.stat().st_size
            if file_size > self.config.max_file_size:
                self.logger.warning(f"File {file_path} exceeds size limit: {file_size}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate file {file_path}: {e}")
            return False


class AudioIndexProcessor(BaseContentProcessor):
    """Advanced audio content processor for indexing"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        self.speech_recognizer = None
        self.audio_classifier = None
        
        if not config.supported_audio_formats:
            config.supported_audio_formats = [
                ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"
            ]
    
    async def initialize(self) -> None:
        """Initialize audio processing components"""



        try:
            # Initialize speech recognition
            self.speech_recognizer = sr.Recognizer()
            
            # Initialize audio classification pipeline
            if self.config.enable_gpu and torch.cuda.is_available():
                device = 0
            else:
                device = -1
            
            self.audio_classifier = pipeline(
                "audio-classification",
                model="facebook/wav2vec2-base-960h",
                device=device
            )
            
            self._initialized = True
            self.logger.info("AudioIndexProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AudioIndexProcessor: {e}")
            raise
    
    def supports_format(self, file_path: str) -> bool:
        """Check if audio format is supported"""



        return Path(file_path).suffix.lower() in self.config.supported_audio_formats
    
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process audio file and extract comprehensive features"""



        try:
            if not await self.validate_file(file_path):
                raise ValueError(f"Invalid audio file: {file_path}")
            
            result = {
                "content_type": "audio",
                "file_path": file_path,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Extract basic metadata
            basic_metadata = await self._extract_audio_metadata(file_path)
            result.update(basic_metadata)
            
            # Load audio for analysis
            audio_data, sample_rate = librosa.load(
                file_path, 
                sr=self.config.audio_sample_rate
            )
            
            # Extract audio features
            audio_features = await self._extract_audio_features(audio_data, sample_rate)
            result.update(audio_features)
            
            # Extract spectral features
            spectral_features = await self._extract_spectral_features(audio_data, sample_rate)
            result.update(spectral_features)
            
            # Speech-to-text transcription
            transcription = await self._extract_speech_transcription(file_path)
            if transcription:
                result["transcription"] = transcription
                result["has_speech"] = True
            else:
                result["has_speech"] = False
            
            # Music analysis
            music_features = await self._extract_music_features(audio_data, sample_rate)
            result.update(music_features)
            
            # Generate searchable text
            result["searchable_text"] = self._generate_searchable_text(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process audio {file_path}: {e}")
            raise
    
    async def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic audio file metadata"""



        try:
            metadata = {}
            
            # File information
            path = Path(file_path)
            metadata["filename"] = path.name
            metadata["file_size"] = path.stat().st_size
            metadata["file_extension"] = path.suffix.lower()
            
            # Audio metadata using mutagen
            try:
                audio_file = mutagen.File(file_path)
                if audio_file:
                    metadata["duration"] = audio_file.info.length
                    metadata["bitrate"] = getattr(audio_file.info, 'bitrate', 0)
                    metadata["sample_rate"] = getattr(audio_file.info, 'sample_rate', 0)
                    metadata["channels"] = getattr(audio_file.info, 'channels', 0)
                    
                    # ID3 tags
                    if hasattr(audio_file, 'tags') and audio_file.tags:
                        metadata["title"] = str(audio_file.tags.get("TIT2", [""])[0])
                        metadata["artist"] = str(audio_file.tags.get("TPE1", [""])[0])
                        metadata["album"] = str(audio_file.tags.get("TALB", [""])[0])
                        metadata["genre"] = str(audio_file.tags.get("TCON", [""])[0])
                        metadata["year"] = str(audio_file.tags.get("TDRC", [""])[0])
            except Exception as e:
                self.logger.warning(f"Failed to extract audio metadata: {e}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio metadata: {e}")
            return {}
    
    async def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""



        try:
            features = {}
            
            # Basic audio properties
            features["audio_length"] = len(audio_data) / sample_rate
            features["sample_rate"] = sample_rate
            features["rms_energy"] = float(np.sqrt(np.mean(audio_data**2)))
            features["zero_crossing_rate"] = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features["tempo"] = float(tempo)
            features["beat_count"] = len(beats)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features["spectral_centroid_mean"] = float(np.mean(spectral_centroids))
            features["spectral_centroid_std"] = float(np.std(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            features["spectral_rolloff_mean"] = float(np.mean(spectral_rolloff))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            features["spectral_bandwidth_mean"] = float(np.mean(spectral_bandwidth))
            
            # MFCCs (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            for i in range(13):
                features[f"mfcc_{i}_mean"] = float(np.mean(mfccs[i]))
                features[f"mfcc_{i}_std"] = float(np.std(mfccs[i]))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio features: {e}")
            return {}
    
    async def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract advanced spectral features"""



        try:
            features = {}
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features["chroma_mean"] = float(np.mean(chroma))
            features["chroma_std"] = float(np.std(chroma))
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
            features["mel_spectrogram_mean"] = float(np.mean(mel_spec))
            features["mel_spectrogram_std"] = float(np.std(mel_spec))
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            features["spectral_contrast_mean"] = float(np.mean(contrast))
            features["spectral_contrast_std"] = float(np.std(contrast))
            
            # Tonnetz features
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            features["tonnetz_mean"] = float(np.mean(tonnetz))
            features["tonnetz_std"] = float(np.std(tonnetz))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract spectral features: {e}")
            return {}
    
    async def _extract_speech_transcription(self, file_path: str) -> Optional[str]:
        """Extract speech transcription from audio"""



        try:
            with sr.AudioFile(file_path) as source:
                audio = self.speech_recognizer.record(source)
                
            # Try multiple recognition services
            try:
                # Google Speech Recognition
                text = self.speech_recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
            
            try:
                # Sphinx (offline)
                text = self.speech_recognizer.recognize_sphinx(audio)
                return text
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract speech transcription: {e}")
            return None
    
    async def _extract_music_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract music-specific features"""



        try:
            features = {}
            
            # Harmonic and percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_data)
            features["harmonic_ratio"] = float(np.mean(harmonic**2) / (np.mean(audio_data**2) + 1e-10))
            features["percussive_ratio"] = float(np.mean(percussive**2) / (np.mean(audio_data**2) + 1e-10))
            
            # Key detection (simplified)
            chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
            key_profile = np.mean(chroma, axis=1)
            estimated_key = np.argmax(key_profile)
            
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            features["estimated_key"] = key_names[estimated_key]
            features["key_confidence"] = float(key_profile[estimated_key] / np.sum(key_profile))
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            features["onset_count"] = len(onset_frames)
            features["onset_density"] = float(len(onset_frames) / (len(audio_data) / sample_rate))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract music features: {e}")
            return {}
    
    def _generate_searchable_text(self, features: Dict[str, Any]) -> str:
        """Generate searchable text from audio features"""
        searchable_parts = []
        
        # Add metadata
        if "title" in features:
            searchable_parts.append(features["title"])
        if "artist" in features:
            searchable_parts.append(features["artist"])
        if "album" in features:
            searchable_parts.append(features["album"])
        if "genre" in features:
            searchable_parts.append(features["genre"])
        
        # Add transcription
        if "transcription" in features:
            searchable_parts.append(features["transcription"])
        
        # Add audio characteristics
        if features.get("has_speech"):
            searchable_parts.append("speech voice vocal")
        
        if "estimated_key" in features:
            searchable_parts.append(f"key {features['estimated_key']}")
        
        if "tempo" in features:
            tempo = features["tempo"]
            if tempo < 80:
                searchable_parts.append("slow tempo ballad")
            elif tempo > 140:
                searchable_parts.append("fast tempo upbeat")
            else:
                searchable_parts.append("medium tempo")
        
        return " ".join(searchable_parts).lower()


class VideoIndexProcessor(BaseContentProcessor):
    """Advanced video content processor for indexing"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        
        if not config.supported_video_formats:
            config.supported_video_formats = [
                ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v"
            ]
    
    async def initialize(self) -> None:
        """Initialize video processing components"""



        try:
            self._initialized = True
            self.logger.info("VideoIndexProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VideoIndexProcessor: {e}")
            raise
    
    def supports_format(self, file_path: str) -> bool:
        """Check if video format is supported"""



        return Path(file_path).suffix.lower() in self.config.supported_video_formats
    
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process video file and extract comprehensive features"""



        try:
            if not await self.validate_file(file_path):
                raise ValueError(f"Invalid video file: {file_path}")
            
            result = {
                "content_type": "video",
                "file_path": file_path,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Extract basic video metadata
            video_metadata = await self._extract_video_metadata(file_path)
            result.update(video_metadata)
            
            # Extract visual features
            visual_features = await self._extract_visual_features(file_path)
            result.update(visual_features)
            
            # Extract audio from video
            audio_features = await self._extract_video_audio_features(file_path)
            result.update(audio_features)
            
            # Scene detection
            scene_features = await self._extract_scene_features(file_path)
            result.update(scene_features)
            
            # Generate searchable text
            result["searchable_text"] = self._generate_searchable_text(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process video {file_path}: {e}")
            raise
    
    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic video metadata"""



        try:
            metadata = {}
            
            # File information
            path = Path(file_path)
            metadata["filename"] = path.name
            metadata["file_size"] = path.stat().st_size
            metadata["file_extension"] = path.suffix.lower()
            
            # Video properties using OpenCV
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                metadata["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata["fps"] = float(cap.get(cv2.CAP_PROP_FPS))
                metadata["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                metadata["duration"] = metadata["frame_count"] / metadata["fps"] if metadata["fps"] > 0 else 0
                metadata["aspect_ratio"] = metadata["width"] / metadata["height"] if metadata["height"] > 0 else 0
                cap.release()
            
            # Additional metadata using MoviePy
            try:
                with VideoFileClip(file_path) as clip:
                    metadata["has_audio"] = clip.audio is not None
                    if clip.audio:
                        metadata["audio_duration"] = clip.audio.duration
            except Exception as e:
                self.logger.warning(f"Failed to extract MoviePy metadata: {e}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract video metadata: {e}")
            return {}
    
    async def _extract_visual_features(self, file_path: str) -> Dict[str, Any]:
        """Extract visual features from video frames"""



        try:
            features = {}
            
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return features
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames for analysis
            sample_count = min(20, frame_count)
            frame_indices = np.linspace(0, frame_count - 1, sample_count, dtype=int)
            
            brightness_values = []
            contrast_values = []
            color_histograms = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert to grayscale for brightness/contrast
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Brightness (mean intensity)
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # Contrast (standard deviation)
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
                    
                    # Color histogram
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    color_histograms.append(hist.flatten())
            
            cap.release()
            
            # Calculate statistics
            if brightness_values:
                features["brightness_mean"] = float(np.mean(brightness_values))
                features["brightness_std"] = float(np.std(brightness_values))
                features["contrast_mean"] = float(np.mean(contrast_values))
                features["contrast_std"] = float(np.std(contrast_values))
            
            # Color analysis
            if color_histograms:
                avg_histogram = np.mean(color_histograms, axis=0)
                features["dominant_colors"] = avg_histogram.tolist()[:10]  # Top 10 color bins
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract visual features: {e}")
            return {}
    
    async def _extract_video_audio_features(self, file_path: str) -> Dict[str, Any]:
        """Extract audio features from video"""



        try:
            features = {}
            
            try:
                with VideoFileClip(file_path) as video_clip:
                    if video_clip.audio:
                        # Extract audio
                        temp_audio_path = f"{self.config.temp_directory}/temp_audio.wav"
                        Path(self.config.temp_directory).mkdir(parents=True, exist_ok=True)
                        
                        video_clip.audio.write_audiofile(
                            temp_audio_path, 
                            verbose=False, 
                            logger=None
                        )
                        
                        # Process audio using AudioIndexProcessor
                        audio_processor = AudioIndexProcessor(self.config)
                        await audio_processor.initialize()
                        
                        audio_result = await audio_processor.process(temp_audio_path)
                        
                        # Add audio features with prefix
                        for key, value in audio_result.items():
                            if key not in ["content_type", "file_path", "processed_at"]:
                                features[f"audio_{key}"] = value
                        
                        # Clean up temp file
                        Path(temp_audio_path).unlink(missing_ok=True)
                        
            except Exception as e:
                self.logger.warning(f"Failed to extract video audio: {e}")
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract video audio features: {e}")
            return {}
    
    async def _extract_scene_features(self, file_path: str) -> Dict[str, Any]:
        """Extract scene and motion features"""



        try:
            features = {}
            
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return features
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Motion detection
            motion_scores = []
            prev_frame = None
            
            # Sample frames for motion analysis
            sample_count = min(50, frame_count)
            frame_indices = np.linspace(0, frame_count - 1, sample_count, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    if prev_frame is not None:
                        # Calculate frame difference
                        diff = cv2.absdiff(prev_frame, gray)
                        motion_score = np.sum(diff) / (diff.shape[0] * diff.shape[1])
                        motion_scores.append(motion_score)
                    
                    prev_frame = gray
            
            cap.release()
            
            # Motion statistics
            if motion_scores:
                features["motion_mean"] = float(np.mean(motion_scores))
                features["motion_std"] = float(np.std(motion_scores))
                features["motion_max"] = float(np.max(motion_scores))
                
                # Classify motion level
                motion_mean = features["motion_mean"]
                if motion_mean < 5:
                    features["motion_level"] = "static"
                elif motion_mean < 15:
                    features["motion_level"] = "low"
                elif motion_mean < 30:
                    features["motion_level"] = "medium"
                else:
                    features["motion_level"] = "high"
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract scene features: {e}")
            return {}
    
    def _generate_searchable_text(self, features: Dict[str, Any]) -> str:
        """Generate searchable text from video features"""
        searchable_parts = []
        
        # Add filename without extension
        if "filename" in features:
            name_without_ext = Path(features["filename"]).stem
            searchable_parts.append(name_without_ext.replace("_", " ").replace("-", " "))
        
        # Add video characteristics
        if "width" in features and "height" in features:
            width, height = features["width"], features["height"]
            if width >= 1920 and height >= 1080:
                searchable_parts.append("hd high definition 1080p")
            elif width >= 1280 and height >= 720:
                searchable_parts.append("hd 720p")
        
        if "motion_level" in features:
            motion = features["motion_level"]
            searchable_parts.append(f"{motion} motion")
        
        if "has_audio" in features and features["has_audio"]:
            searchable_parts.append("audio sound")
            
            # Add audio transcription if available
            if "audio_transcription" in features:
                searchable_parts.append(features["audio_transcription"])
        
        if "duration" in features:
            duration = features["duration"]
            if duration < 30:
                searchable_parts.append("short clip")
            elif duration > 300:
                searchable_parts.append("long video")
        
        return " ".join(searchable_parts).lower()


class ImageIndexProcessor(BaseContentProcessor):
    """Advanced image content processor for indexing"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        
        if not config.supported_image_formats:
            config.supported_image_formats = [
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"
            ]
    
    async def initialize(self) -> None:
        """Initialize image processing components"""



        try:
            self._initialized = True
            self.logger.info("ImageIndexProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ImageIndexProcessor: {e}")
            raise
    
    def supports_format(self, file_path: str) -> bool:
        """Check if image format is supported"""



        return Path(file_path).suffix.lower() in self.config.supported_image_formats
    
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process image file and extract comprehensive features"""



        try:
            if not await self.validate_file(file_path):
                raise ValueError(f"Invalid image file: {file_path}")
            
            result = {
                "content_type": "image",
                "file_path": file_path,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Extract basic image metadata
            image_metadata = await self._extract_image_metadata(file_path)
            result.update(image_metadata)
            
            # Extract visual features
            visual_features = await self._extract_visual_features(file_path)
            result.update(visual_features)
            
            # OCR text extraction
            ocr_text = await self._extract_ocr_text(file_path)
            if ocr_text:
                result["ocr_text"] = ocr_text
                result["has_text"] = True
            else:
                result["has_text"] = False
            
            # Generate searchable text
            result["searchable_text"] = self._generate_searchable_text(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process image {file_path}: {e}")
            raise
    
    async def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic image metadata including EXIF"""



        try:
            metadata = {}
            
            # File information
            path = Path(file_path)
            metadata["filename"] = path.name
            metadata["file_size"] = path.stat().st_size
            metadata["file_extension"] = path.suffix.lower()
            
            # Image properties
            with Image.open(file_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["aspect_ratio"] = img.width / img.height if img.height > 0 else 0
                
                # Calculate resolution category
                total_pixels = img.width * img.height
                if total_pixels > 8000000:  # > 8MP
                    metadata["resolution_category"] = "high"
                elif total_pixels > 2000000:  # > 2MP
                    metadata["resolution_category"] = "medium"
                else:
                    metadata["resolution_category"] = "low"
                
                # EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    exif_data = {}
                    
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    
                    # Extract useful EXIF data
                    if "DateTime" in exif_data:
                        metadata["capture_date"] = str(exif_data["DateTime"])
                    if "Make" in exif_data:
                        metadata["camera_make"] = str(exif_data["Make"])
                    if "Model" in exif_data:
                        metadata["camera_model"] = str(exif_data["Model"])
                    if "GPS" in exif_data:
                        metadata["has_gps"] = True
                    
                    metadata["exif_data"] = exif_data
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract image metadata: {e}")
            return {}
    
    async def _extract_visual_features(self, file_path: str) -> Dict[str, Any]:
        """Extract visual features from image"""



        try:
            features = {}
            
            # Load image with OpenCV
            img = cv2.imread(file_path)
            if img is None:
                return features
            
            # Color analysis
            color_features = self._analyze_colors(img)
            features.update(color_features)
            
            # Texture analysis
            texture_features = self._analyze_texture(img)
            features.update(texture_features)
            
            # Edge detection
            edge_features = self._analyze_edges(img)
            features.update(edge_features)
            
            # Face detection
            face_features = self._detect_faces(img)
            features.update(face_features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract visual features: {e}")
            return {}
    
    def _analyze_colors(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of the image"""



        try:
            features = {}
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
            # Color histograms
            hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
            
            # Color statistics
            features["mean_brightness"] = float(np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
            features["std_brightness"] = float(np.std(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
            
            # Dominant colors (simplified)
            features["dominant_blue"] = float(np.argmax(hist_b))
            features["dominant_green"] = float(np.argmax(hist_g))
            features["dominant_red"] = float(np.argmax(hist_r))
            
            # Saturation analysis
            saturation = hsv[:, :, 1]
            features["mean_saturation"] = float(np.mean(saturation))
            features["std_saturation"] = float(np.std(saturation))
            
            # Color diversity (entropy of color histogram)
            combined_hist = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
            combined_hist = combined_hist / np.sum(combined_hist)  # Normalize
            entropy = -np.sum(combined_hist * np.log2(combined_hist + 1e-10))
            features["color_diversity"] = float(entropy)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to analyze colors: {e}")
            return {}
    
    def _analyze_texture(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze texture properties of the image"""



        try:
            features = {}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern (simplified)
            lbp = np.zeros_like(gray)
            for i in range(1, gray.shape[0] - 1):
                for j in range(1, gray.shape[1] - 1):
                    center = gray[i, j]
                    pattern = 0
                    pattern |= (gray[i-1, j-1] > center) << 7
                    pattern |= (gray[i-1, j] > center) << 6
                    pattern |= (gray[i-1, j+1] > center) << 5
                    pattern |= (gray[i, j+1] > center) << 4
                    pattern |= (gray[i+1, j+1] > center) << 3
                    pattern |= (gray[i+1, j] > center) << 2
                    pattern |= (gray[i+1, j-1] > center) << 1
                    pattern |= (gray[i, j-1] > center) << 0
                    lbp[i, j] = pattern
            
            # LBP histogram
            lbp_hist = cv2.calcHist([lbp], [0], None, [256], [0, 256])
            features["texture_uniformity"] = float(np.max(lbp_hist) / np.sum(lbp_hist))
            
            # Contrast and homogeneity
            features["texture_contrast"] = float(np.std(gray))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to analyze texture: {e}")
            return {}
    
    def _analyze_edges(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze edge properties of the image"""



        try:
            features = {}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Edge statistics
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_pixels = np.sum(edges > 0)
            
            features["edge_density"] = float(edge_pixels / total_pixels)
            features["edge_count"] = int(edge_pixels)
            
            # Contour detection
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features["contour_count"] = len(contours)
            
            if contours:
                # Largest contour area
                largest_contour = max(contours, key=cv2.contourArea)
                features["largest_contour_area"] = float(cv2.contourArea(largest_contour))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to analyze edges: {e}")
            return {}
    
    def _detect_faces(self, img: np.ndarray) -> Dict[str, Any]:
        """Detect faces in the image"""



        try:
            features = {}
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            features["face_count"] = len(faces)
            features["has_faces"] = len(faces) > 0
            
            if len(faces) > 0:
                # Face statistics
                face_areas = [w * h for (x, y, w, h) in faces]
                features["largest_face_area"] = float(max(face_areas))
                features["average_face_area"] = float(np.mean(face_areas))
                
                # Face positions (relative to image)
                img_area = img.shape[0] * img.shape[1]
                features["face_coverage"] = float(sum(face_areas) / img_area)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to detect faces: {e}")
            return {}
    
    async def _extract_ocr_text(self, file_path: str) -> Optional[str]:
        """Extract text from image using OCR"""



        try:
            img = cv2.imread(file_path)
            if img is None:
                return None
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to make text more readable
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(thresh)
            
            # Clean extracted text
            text = text.strip()
            if len(text) > 10:  # Only return if substantial text found
                return text
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract OCR text: {e}")
            return None
    
    def _generate_searchable_text(self, features: Dict[str, Any]) -> str:
        """Generate searchable text from image features"""
        searchable_parts = []
        
        # Add filename without extension
        if "filename" in features:
            name_without_ext = Path(features["filename"]).stem
            searchable_parts.append(name_without_ext.replace("_", " ").replace("-", " "))
        
        # Add OCR text
        if "ocr_text" in features:
            searchable_parts.append(features["ocr_text"])
        
        # Add visual characteristics
        if "has_faces" in features and features["has_faces"]:
            searchable_parts.append("face portrait person people")
        
        if "resolution_category" in features:
            resolution = features["resolution_category"]
            searchable_parts.append(f"{resolution} resolution quality")
        
        if "mean_saturation" in features:
            saturation = features["mean_saturation"]
            if saturation > 100:
                searchable_parts.append("colorful vibrant")
            elif saturation < 50:
                searchable_parts.append("muted desaturated")
        
        if "mean_brightness" in features:
            brightness = features["mean_brightness"]
            if brightness > 180:
                searchable_parts.append("bright light")
            elif brightness < 80:
                searchable_parts.append("dark moody")
        
        if "edge_density" in features:
            edge_density = features["edge_density"]
            if edge_density > 0.1:
                searchable_parts.append("detailed sharp")
            else:
                searchable_parts.append("smooth soft")
        
        return " ".join(searchable_parts).lower()


class TextIndexProcessor(BaseContentProcessor):
    """Advanced text content processor for indexing"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        self.nlp = None
        
    async def initialize(self) -> None:
        """Initialize text processing components"""



        try:
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy model not found, using basic processing")
                self.nlp = None
            
            self._initialized = True
            self.logger.info("TextIndexProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TextIndexProcessor: {e}")
            raise
    
    def supports_format(self, file_path: str) -> bool:
        """Check if text format is supported"""
        supported_formats = [".txt", ".md", ".rtf", ".doc", ".docx"]
        return Path(file_path).suffix.lower() in supported_formats
    
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process text file and extract comprehensive features"""



        try:
            if not await self.validate_file(file_path):
                raise ValueError(f"Invalid text file: {file_path}")
            
            # Read text content
            text_content = await self._read_text_file(file_path)
            if not text_content:
                raise ValueError(f"Could not extract text from {file_path}")
            
            result = {
                "content_type": "text",
                "file_path": file_path,
                "text": text_content,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Extract basic text metadata
            text_metadata = await self._extract_text_metadata(file_path, text_content)
            result.update(text_metadata)
            
            # Extract linguistic features
            linguistic_features = await self._extract_linguistic_features(text_content)
            result.update(linguistic_features)
            
            # Named entity recognition
            if self.nlp:
                entities = await self._extract_entities(text_content)
                result["entities"] = entities
            
            # Generate searchable text (already have the text)
            result["searchable_text"] = text_content.lower()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process text {file_path}: {e}")
            raise
    
    async def _read_text_file(self, file_path: str) -> str:
        """Read text content from file"""



        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            if extension in [".txt", ".md", ".rtf"]:
                # Simple text files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif extension in [".doc", ".docx"]:
                # Word documents (would need python-docx)
                self.logger.warning(f"Word document support not implemented: {file_path}")
                return ""
            else:
                # Try reading as plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
        except Exception as e:
            self.logger.error(f"Failed to read text file {file_path}: {e}")
            return ""
    
    async def _extract_text_metadata(self, file_path: str, text_content: str) -> Dict[str, Any]:
        """Extract basic text metadata"""



        try:
            metadata = {}
            
            # File information
            path = Path(file_path)
            metadata["filename"] = path.name
            metadata["file_size"] = path.stat().st_size
            metadata["file_extension"] = path.suffix.lower()
            
            # Text statistics
            metadata["character_count"] = len(text_content)
            metadata["word_count"] = len(text_content.split())
            metadata["line_count"] = len(text_content.split('\n'))
            metadata["paragraph_count"] = len([p for p in text_content.split('\n\n') if p.strip()])
            
            # Language detection
            try:
                detected_language = langdetect.detect(text_content)
                metadata["language"] = detected_language
            except:
                metadata["language"] = "unknown"
            
            # Readability scores
            try:
                metadata["flesch_reading_ease"] = flesch_reading_ease(text_content)
                metadata["syllable_count"] = syllable_count(text_content)
            except:
                pass
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract text metadata: {e}")
            return {}
    
    async def _extract_linguistic_features(self, text_content: str) -> Dict[str, Any]:
        """Extract linguistic features from text"""



        try:
            features = {}
            
            # Basic linguistic analysis
            words = text_content.split()
            sentences = text_content.split('.')
            
            if words:
                features["average_word_length"] = float(np.mean([len(word) for word in words]))
                features["max_word_length"] = max([len(word) for word in words])
            
            if sentences:
                features["average_sentence_length"] = float(np.mean([len(sentence.split()) for sentence in sentences if sentence.strip()]))
            
            # Character analysis
            features["uppercase_ratio"] = float(sum(1 for c in text_content if c.isupper()) / len(text_content))
            features["digit_ratio"] = float(sum(1 for c in text_content if c.isdigit()) / len(text_content))
            features["punctuation_ratio"] = float(sum(1 for c in text_content if not c.isalnum() and not c.isspace()) / len(text_content))
            
            # Most common words (simple frequency analysis)
            word_freq = {}
            for word in words:
                clean_word = word.lower().strip('.,!?";')
                if len(clean_word) > 3:  # Ignore short words
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Top 10 most frequent words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            features["top_words"] = [{"word": word, "count": count} for word, count in top_words]
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract linguistic features: {e}")
            return {}
    
    async def _extract_entities(self, text_content: str) -> Dict[str, List[str]]:
        """Extract named entities from text using spaCy"""



        try:
            if not self.nlp:
                return {}
            
            # Limit text length for processing
            if len(text_content) > self.config.text_max_length:
                text_content = text_content[:self.config.text_max_length]
            
            doc = self.nlp(text_content)
            
            entities = {}
            for ent in doc.ents:
                entity_type = ent.label_
                entity_text = ent.text.strip()
                
                if entity_type not in entities:
                    entities[entity_type] = []
                
                if entity_text not in entities[entity_type]:
                    entities[entity_type].append(entity_text)
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Failed to extract entities: {e}")
            return {}


class MultiFormatProcessor:
    """Unified processor for handling multiple content formats"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize specialized processors
        self.audio_processor = AudioIndexProcessor(config)
        self.video_processor = VideoIndexProcessor(config)
        self.image_processor = ImageIndexProcessor(config)
        self.text_processor = TextIndexProcessor(config)
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all processors"""



        try:
            await asyncio.gather(
                self.audio_processor.initialize(),
                self.video_processor.initialize(),
                self.image_processor.initialize(),
                self.text_processor.initialize()
            )
            
            self._initialized = True
            self.logger.info("MultiFormatProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MultiFormatProcessor: {e}")
            raise
    
    async def process(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process file with appropriate processor based on format"""



        try:
            if not self._initialized:
                await self.initialize()
            
            # Determine content type
            content_type = self._detect_content_type(file_path)
            
            # Route to appropriate processor
            if content_type == "audio" and self.audio_processor.supports_format(file_path):
                return await self.audio_processor.process(file_path, metadata)
            elif content_type == "video" and self.video_processor.supports_format(file_path):
                return await self.video_processor.process(file_path, metadata)
            elif content_type == "image" and self.image_processor.supports_format(file_path):
                return await self.image_processor.process(file_path, metadata)
            elif content_type == "text" and self.text_processor.supports_format(file_path):
                return await self.text_processor.process(file_path, metadata)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type based on file extension and MIME type"""



        try:
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type:
                if mime_type.startswith("audio/"):
                    return "audio"
                elif mime_type.startswith("video/"):
                    return "video"
                elif mime_type.startswith("image/"):
                    return "image"
                elif mime_type.startswith("text/"):
                    return "text"
            
            # Fallback to extension
            extension = Path(file_path).suffix.lower()
            
            if extension in self.audio_processor.config.supported_audio_formats:
                return "audio"
            elif extension in self.video_processor.config.supported_video_formats:
                return "video"
            elif extension in self.image_processor.config.supported_image_formats:
                return "image"
            elif extension in [".txt", ".md", ".rtf", ".doc", ".docx"]:
                return "text"
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Failed to detect content type for {file_path}: {e}")
            return "unknown"
    
    def supports_format(self, file_path: str) -> bool:
        """Check if any processor supports the file format"""



        return (
            self.audio_processor.supports_format(file_path) or
            self.video_processor.supports_format(file_path) or
            self.image_processor.supports_format(file_path) or
            self.text_processor.supports_format(file_path)
        )
