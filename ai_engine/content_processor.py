"""Advanced Content Processing Engine
Multi-format content processing with AI enhancement and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import io
import hashlib
from typing import Dict, Any, List, Optional, Union, BinaryIO
from pathlib import Path
import mimetypes
from datetime import datetime

# Audio processing
import librosa
import soundfile as sf
from pydub import AudioSegment

# Video processing  
import cv2
import numpy as np
from moviepy.editor import VideoFileClip

# Image processing
from PIL import Image, ImageEnhance, ImageFilter
import pillow_heif

# Text processing
import fitz  # PyMuPDF
from docx import Document
import chardet

# ML/AI imports
import torch
import tensorflow as tf
from transformers import pipeline, AutoTokenizer, AutoModel

from ..config import settings
from ..core.logging import logger


class AudioProcessor:
    """Advanced audio processing and enhancement"""    
    def __init__(self):
        self.supported_formats = settings.ai.supported_audio_formats
        self.sample_rate = 22050
        self.max_duration = 600  # 10 minutes max
    
    async def process_audio(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process audio file and extract features"""        try:
            # Load audio data
            audio_io = io.BytesIO(file_data)
            
            # Convert to standardized format
            audio_segment = AudioSegment.from_file(audio_io)
            
            # Limit duration
            if len(audio_segment) > self.max_duration * 1000:
                audio_segment = audio_segment[:self.max_duration * 1000]
            
            # Convert to numpy array for analysis
            audio_array = np.array(audio_segment.get_array_of_samples())
            if audio_segment.channels == 2:
                audio_array = audio_array.reshape((-1, 2))
                audio_array = audio_array.mean(axis=1)
            
            # Normalize audio
            audio_array = audio_array.astype(np.float32) / np.max(np.abs(audio_array))
            
            # Extract features using librosa
            features = await self._extract_audio_features(audio_array, self.sample_rate)
            
            # Generate optimized versions
            optimized_versions = await self._generate_audio_versions(audio_segment)
            
            return {
                "original_filename": filename,
                "file_size": len(file_data),
                "duration_seconds": len(audio_segment) / 1000,
                "sample_rate": audio_segment.frame_rate,
                "channels": audio_segment.channels,
                "features": features,
                "optimized_versions": optimized_versions,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise Exception(f"Audio processing failed: {str(e)}")
    
    async def _extract_audio_features(self, audio_array: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""        features = {}
        
        # Basic features
        features["rms_energy"] = float(np.sqrt(np.mean(audio_array**2)))
        features["zero_crossing_rate"] = float(np.mean(librosa.feature.zero_crossing_rate(audio_array)))
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_array, sr=sr)
        features["spectral_centroid"] = float(np.mean(spectral_centroids))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sr)
        features["spectral_rolloff"] = float(np.mean(spectral_rolloff))
        
        # MFCC features
        mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
        features["mfcc"] = mfccs.mean(axis=1).tolist()
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_array, sr=sr)
        features["chroma"] = chroma.mean(axis=1).tolist()
        
        # Tempo detection
        tempo, _ = librosa.beat.beat_track(y=audio_array, sr=sr)
        features["tempo"] = float(tempo)
        
        return features
    
    async def _generate_audio_versions(self, audio_segment: AudioSegment) -> Dict[str, Dict]:
        """Generate platform-optimized audio versions"""        versions = {}
        
        # High quality version (for Spotify, Apple Music)
        hq_version = audio_segment.set_frame_rate(44100).set_channels(2)
        versions["high_quality"] = {
            "format": "flac",
            "sample_rate": 44100,
            "channels": 2,
            "bitrate": None,
            "use_case": ["spotify", "apple_music", "tidal"]
        }
        
        # Standard quality (for most platforms)
        std_version = audio_segment.set_frame_rate(44100).set_channels(2)
        versions["standard"] = {
            "format": "mp3",
            "sample_rate": 44100,
            "channels": 2,
            "bitrate": 320,
            "use_case": ["youtube", "soundcloud", "bandcamp"]
        }
        
        # Mobile optimized (for social media)
        mobile_version = audio_segment.set_frame_rate(22050).set_channels(1)
        versions["mobile"] = {
            "format": "mp3",
            "sample_rate": 22050,
            "channels": 1,
            "bitrate": 128,
            "use_case": ["instagram", "tiktok", "twitter"]
        }
        
        return versions


class VideoProcessor:
    """Advanced video processing and enhancement"""    
    def __init__(self):
        self.supported_formats = settings.ai.supported_video_formats
        self.max_duration = 1800  # 30 minutes max
        self.frame_sample_rate = 1  # Extract 1 frame per second
    
    async def process_video(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process video file and extract features"""        try:
            # Save temporary file for processing
            temp_path = f"/tmp/{hashlib.md5(file_data).hexdigest()}.mp4"
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            # Load video
            video = VideoFileClip(temp_path)
            
            # Limit duration
            if video.duration > self.max_duration:
                video = video.subclip(0, self.max_duration)
            
            # Extract features
            features = await self._extract_video_features(video)
            
            # Extract key frames
            key_frames = await self._extract_key_frames(video)
            
            # Generate optimized versions
            optimized_versions = await self._generate_video_versions(video)
            
            # Cleanup
            video.close()
            Path(temp_path).unlink(missing_ok=True)
            
            return {
                "original_filename": filename,
                "file_size": len(file_data),
                "duration_seconds": video.duration,
                "fps": video.fps,
                "resolution": f"{video.w}x{video.h}",
                "features": features,
                "key_frames": key_frames,
                "optimized_versions": optimized_versions,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise Exception(f"Video processing failed: {str(e)}")
    
    async def _extract_video_features(self, video: VideoFileClip) -> Dict[str, Any]:
        """Extract comprehensive video features"""        features = {}
        
        # Basic properties
        features["duration"] = video.duration
        features["fps"] = video.fps
        features["width"] = video.w
        features["height"] = video.h
        features["aspect_ratio"] = video.w / video.h
        
        # Audio features if present
        if video.audio:
            audio_array = video.audio.to_soundarray()
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)
            
            features["has_audio"] = True
            features["audio_rms"] = float(np.sqrt(np.mean(audio_array**2)))
        else:
            features["has_audio"] = False
        
        # Sample frames for analysis
        frame_times = np.linspace(0, min(video.duration, 60), 10)  # Sample 10 frames
        frame_features = []
        
        for t in frame_times:
            frame = video.get_frame(t)
            
            # Color analysis
            mean_color = np.mean(frame, axis=(0, 1))
            brightness = np.mean(mean_color)
            
            # Edge detection
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray_frame, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            frame_features.append({
                "time": t,
                "brightness": float(brightness),
                "edge_density": float(edge_density),
                "mean_color": mean_color.tolist()
            })
        
        features["frame_analysis"] = frame_features
        features["average_brightness"] = np.mean([f["brightness"] for f in frame_features])
        features["average_edge_density"] = np.mean([f["edge_density"] for f in frame_features])
        
        return features
    
    async def _extract_key_frames(self, video: VideoFileClip) -> List[Dict[str, Any]]:
        """Extract key frames from video"""        key_frames = []
        
        # Extract frames at regular intervals
        num_frames = min(20, int(video.duration))
        frame_times = np.linspace(0, video.duration, num_frames)
        
        for i, t in enumerate(frame_times):
            frame = video.get_frame(t)
            
            # Convert to hash for similarity comparison
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame_resized = cv2.resize(frame_gray, (8, 8))
            frame_hash = hashlib.md5(frame_resized.tobytes()).hexdigest()
            
            key_frames.append({
                "timestamp": t,
                "frame_index": i,
                "frame_hash": frame_hash,
                "brightness": float(np.mean(frame)),
                "contrast": float(np.std(frame))
            })
        
        return key_frames
    
    async def _generate_video_versions(self, video: VideoFileClip) -> Dict[str, Dict]:
        """Generate platform-optimized video versions"""        versions = {}
        
        # High quality (YouTube, Vimeo)
        versions["high_quality"] = {
            "resolution": "1080p",
            "fps": 60,
            "format": "mp4",
            "codec": "h264",
            "bitrate": "8000k",
            "use_case": ["youtube", "vimeo", "facebook"]
        }
        
        # Standard quality (most platforms)
        versions["standard"] = {
            "resolution": "720p", 
            "fps": 30,
            "format": "mp4",
            "codec": "h264",
            "bitrate": "2500k",
            "use_case": ["instagram", "twitter", "linkedin"]
        }
        
        # Mobile optimized (TikTok, Stories)
        versions["mobile"] = {
            "resolution": "480p",
            "fps": 30,
            "format": "mp4",
            "codec": "h264",
            "bitrate": "1200k",
            "aspect_ratio": "9:16",
            "use_case": ["tiktok", "instagram_stories", "snapchat"]
        }
        
        return versions


class ImageProcessor:
    """Advanced image processing and enhancement"""    
    def __init__(self):
        self.supported_formats = settings.ai.supported_image_formats
        self.max_size = 50 * 1024 * 1024  # 50MB max
    
    async def process_image(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process image file and extract features"""        try:
            # Load image
            image = Image.open(io.BytesIO(file_data))
            
            # Convert HEIF/HEIC if needed
            if image.format in ['HEIF', 'HEIC']:
                pillow_heif.register_heif_opener()
                image = image.convert('RGB')
            
            # Extract features
            features = await self._extract_image_features(image)
            
            # Generate optimized versions
            optimized_versions = await self._generate_image_versions(image)
            
            return {
                "original_filename": filename,
                "file_size": len(file_data),
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "features": features,
                "optimized_versions": optimized_versions,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise Exception(f"Image processing failed: {str(e)}")
    
    async def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract comprehensive image features"""        features = {}
        
        # Basic properties
        features["width"] = image.width
        features["height"] = image.height
        features["aspect_ratio"] = image.width / image.height
        features["mode"] = image.mode
        
        # Convert to RGB for analysis
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
        else:
            rgb_image = image
        
        # Color analysis
        image_array = np.array(rgb_image)
        
        # Average colors
        features["average_color"] = np.mean(image_array, axis=(0, 1)).tolist()
        features["brightness"] = float(np.mean(image_array))
        
        # Color histogram
        hist_r = np.histogram(image_array[:,:,0], bins=32, range=(0, 255))[0]
        hist_g = np.histogram(image_array[:,:,1], bins=32, range=(0, 255))[0]
        hist_b = np.histogram(image_array[:,:,2], bins=32, range=(0, 255))[0]
        
        features["color_histogram"] = {
            "red": hist_r.tolist(),
            "green": hist_g.tolist(), 
            "blue": hist_b.tolist()
        }
        
        # Texture analysis using OpenCV
        gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        features["edge_density"] = float(np.sum(edges > 0) / edges.size)
        
        # Contrast and sharpness
        features["contrast"] = float(np.std(gray_image))
        
        # Blur detection using Laplacian variance
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        features["sharpness"] = float(laplacian_var)
        
        return features
    
    async def _generate_image_versions(self, image: Image.Image) -> Dict[str, Dict]:
        """Generate platform-optimized image versions"""        versions = {}
        
        # High quality (for professional platforms)
        versions["high_quality"] = {
            "format": "png",
            "quality": 95,
            "max_size": "4096x4096",
            "use_case": ["behance", "dribbble", "500px"]
        }
        
        # Web optimized (for websites and blogs)
        versions["web"] = {
            "format": "jpg",
            "quality": 85,
            "max_size": "1920x1920",
            "use_case": ["website", "blog", "portfolio"]
        }
        
        # Social media (Instagram, Facebook)
        versions["social"] = {
            "format": "jpg",
            "quality": 80,
            "max_size": "1080x1080",
            "use_case": ["instagram", "facebook", "twitter"]
        }
        
        # Thumbnail (for previews)
        versions["thumbnail"] = {
            "format": "jpg",
            "quality": 75,
            "max_size": "300x300",
            "use_case": ["thumbnail", "preview", "gallery"]
        }
        
        return versions


class TextProcessor:
    """Advanced text processing and analysis"""    
    def __init__(self):
        self.supported_formats = settings.ai.supported_text_formats
        self.max_length = 1000000  # 1M characters max
        
        # Initialize NLP models
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    
    async def process_text(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process text file and extract features"""        try:
            # Extract text content
            text_content = await self._extract_text_content(file_data, filename)
            
            # Limit length
            if len(text_content) > self.max_length:
                text_content = text_content[:self.max_length]
            
            # Extract features
            features = await self._extract_text_features(text_content)
            
            # Generate optimized versions
            optimized_versions = await self._generate_text_versions(text_content)
            
            return {
                "original_filename": filename,
                "file_size": len(file_data),
                "text_length": len(text_content),
                "content_preview": text_content[:500],
                "features": features,
                "optimized_versions": optimized_versions,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise Exception(f"Text processing failed: {str(e)}")
    
    async def _extract_text_content(self, file_data: bytes, filename: str) -> str:
        """Extract text from various file formats"""        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            # Extract from PDF
            doc = fitz.open(stream=file_data, filetype="pdf")
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            
        elif file_ext in ['.doc', '.docx']:
            # Extract from Word document
            doc = Document(io.BytesIO(file_data))
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        else:
            # Plain text files
            # Detect encoding
            detected = chardet.detect(file_data)
            encoding = detected['encoding'] or 'utf-8'
            text_content = file_data.decode(encoding, errors='ignore')
        
        return text_content
    
    async def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""        features = {}
        
        # Basic statistics
        features["character_count"] = len(text)
        features["word_count"] = len(text.split())
        features["sentence_count"] = text.count('.') + text.count('!') + text.count('?')
        features["paragraph_count"] = text.count('\n\n') + 1
        
        # Language detection
        features["detected_language"] = "en"  # Simplified for now
        
        # Sentiment analysis
        if len(text) > 10:
            sentiment_result = self.sentiment_analyzer(text[:512])  # Limit for model
            features["sentiment"] = {
                "label": sentiment_result[0]["label"],
                "score": sentiment_result[0]["score"]
            }
        
        # Readability metrics
        avg_sentence_length = features["word_count"] / max(features["sentence_count"], 1)
        features["average_sentence_length"] = avg_sentence_length
        
        # Text complexity
        unique_words = len(set(text.lower().split()))
        features["lexical_diversity"] = unique_words / max(features["word_count"], 1)
        
        return features
    
    async def _generate_text_versions(self, text: str) -> Dict[str, Dict]:
        """Generate platform-optimized text versions"""        versions = {}
        
        # Full version (for blogs, articles)
        versions["full"] = {
            "format": "markdown",
            "max_length": None,
            "use_case": ["blog", "medium", "newsletter"]
        }
        
        # Summary version (for social media)
        summary_length = min(280, len(text) // 4)
        versions["summary"] = {
            "format": "plain",
            "max_length": summary_length,
            "content": text[:summary_length] + "..." if len(text) > summary_length else text,
            "use_case": ["twitter", "facebook", "linkedin"]
        }
        
        # Snippet version (for previews)
        snippet_length = min(150, len(text) // 8)
        versions["snippet"] = {
            "format": "plain",
            "max_length": snippet_length,
            "content": text[:snippet_length] + "..." if len(text) > snippet_length else text,
            "use_case": ["preview", "teaser", "description"]
        }
        
        return versions


class ContentProcessor:
    """Main content processing orchestrator"""    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
    
    async def process_content(self, file_data: bytes, filename: str, 
                            content_type: Optional[str] = None) -> Dict[str, Any]:
        """Process content based on file type"""        try:
            # Determine content type
            if not content_type:
                content_type = self._detect_content_type(file_data, filename)
            
            logger.info(f"Processing {content_type} content: {filename}")
            
            # Route to appropriate processor
            if content_type == "audio":
                return await self.audio_processor.process_audio(file_data, filename)
            elif content_type == "video":
                return await self.video_processor.process_video(file_data, filename)
            elif content_type == "image":
                return await self.image_processor.process_image(file_data, filename)
            elif content_type == "text":
                return await self.text_processor.process_text(file_data, filename)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Content processing failed for {filename}: {str(e)}")
            raise
    
    def _detect_content_type(self, file_data: bytes, filename: str) -> str:
        """Detect content type from file data and filename"""        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type:
            if mime_type.startswith('audio/'):
                return "audio"
            elif mime_type.startswith('video/'):
                return "video"
            elif mime_type.startswith('image/'):
                return "image"
            elif mime_type.startswith('text/'):
                return "text"
        
        # Fallback to file extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        
        if file_ext in settings.ai.supported_audio_formats:
            return "audio"
        elif file_ext in settings.ai.supported_video_formats:
            return "video"
        elif file_ext in settings.ai.supported_image_formats:
            return "image"
        elif file_ext in settings.ai.supported_text_formats:
            return "text"
        
        raise ValueError(f"Unable to determine content type for {filename}")
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get all supported file formats"""        return {
            "audio": settings.ai.supported_audio_formats,
            "video": settings.ai.supported_video_formats,
            "image": settings.ai.supported_image_formats,
            "text": settings.ai.supported_text_formats
        }


# Global content processor instance
content_processor = ContentProcessor()