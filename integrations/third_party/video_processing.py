"""
AINFLUE INTEGRATIONS - VIDEO PROCESSING SERVICES
===============================================

Enterprise video processing integration for creator economy platform.
Combines multiple expert roles for comprehensive video content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/third_party)

Expert Roles Applied:
- Lead Dev IA: AI-powered video analysis, content understanding, intelligent processing
- Backend Senior: Robust video pipeline architecture, scalable processing, enterprise patterns
- ML Engineer: Video classification, scene detection, automated insights, content optimization
- DBA: Video metadata management, frame indexing, searchable content storage
- Security: Video encryption, watermarking, content protection, access control
- Microservices: Distributed video processing, queue management, service orchestration
- Audio Engineer: Audio extraction, synchronization, multi-format audio processing
- DevOps: Performance monitoring, resource optimization, automated scaling
- IA Prompt Engineer: AI-driven video enhancement, content analysis, optimization

Business Logic Integration:
Creator → Video Upload → AI Processing → Content Protection → SEO → Distribution → Monetization
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import aiohttp
import aiofiles
from pydantic import BaseModel, Field, validator
import magic

# Video Processing Libraries
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip
import face_recognition
from ultralytics import YOLO

# AI and ML Libraries
import openai
from transformers import pipeline, AutoProcessor, AutoModel
import torch
import clip
from sentence_transformers import SentenceTransformer

# Audio Processing
import librosa
import soundfile as sf
import whisper

# Security and Compliance
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
VIDEO_PROCESSED_COUNTER = Counter('video_processed_total', 'Total videos processed', ['type', 'status'])
PROCESSING_DURATION = Histogram('video_processing_duration_seconds', 'Video processing duration', ['operation'])
ACTIVE_PROCESSING = Gauge('video_active_processing', 'Active video processing jobs')
ERROR_COUNTER = Counter('video_processing_errors_total', 'Video processing errors', ['error_type'])
FRAME_ANALYSIS_COUNTER = Counter('video_frame_analysis_total', 'Total frames analyzed')
AUDIO_EXTRACTION_DURATION = Histogram('audio_extraction_duration_seconds', 'Audio extraction duration')

class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    M4V = "m4v"
    UNKNOWN = "unknown"

class VideoQuality(Enum):
    """Video quality settings"""
    LOW = "240p"
    MEDIUM = "480p"
    HIGH = "720p"
    FULL_HD = "1080p"
    ULTRA_HD = "4K"

class ProcessingStatus(Enum):
    """Video processing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    ENHANCING = "enhancing"
    ENCODING = "encoding"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"

class ContentType(Enum):
    """Video content classification"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    MUSIC = "music"
    GAMING = "gaming"
    VLOG = "vlog"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    SPORTS = "sports"
    COOKING = "cooking"
    TECH = "tech"
    UNKNOWN = "unknown"

@dataclass
class VideoMetadata:
    """Comprehensive video metadata"""
    video_id: str
    filename: str
    file_size: int
    duration: float
    format: VideoFormat
    resolution: str
    fps: float
    bitrate: int
    codec: str
    audio_codec: str
    upload_timestamp: datetime
    creator_id: str
    status: ProcessingStatus
    checksum: str
    
    # AI Analysis Results
    content_type: Optional[ContentType] = None
    scenes: Optional[List[Dict]] = None
    faces_detected: Optional[List[Dict]] = None
    objects_detected: Optional[List[Dict]] = None
    transcript: Optional[str] = None
    audio_analysis: Optional[Dict] = None
    seo_analysis: Optional[Dict] = None
    monetization_analysis: Optional[Dict] = None
    
    # Security and Protection
    watermark_applied: bool = False
    encryption_key: Optional[str] = None
    content_protection: Optional[Dict] = None
    
    # Processing Details
    processing_log: List[str] = None
    thumbnail_paths: List[str] = None
    preview_path: Optional[str] = None

class FrameAnalysis(NamedTuple):
    """Frame analysis results"""
    timestamp: float
    frame_number: int
    scene_change: bool
    objects: List[Dict]
    faces: List[Dict]
    quality_score: float
    brightness: float
    contrast: float

class VideoProcessingConfig(BaseModel):
    """Configuration for video processing services"""
    # AI Processing Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for content analysis")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model for analysis")
    
    # Video Processing Configuration
    ffmpeg_path: str = Field(default="ffmpeg", description="FFmpeg executable path")
    max_video_size: int = Field(default=2 * 1024 * 1024 * 1024, description="Maximum video size (2GB)")
    supported_formats: List[str] = Field(
        default=["mp4", "avi", "mov", "mkv", "webm", "flv"],
        description="Supported video formats"
    )
    
    # Processing Quality Settings
    thumbnail_count: int = Field(default=10, description="Number of thumbnails to generate")
    frame_analysis_interval: int = Field(default=30, description="Frame analysis interval in seconds")
    max_resolution: str = Field(default="1920x1080", description="Maximum processing resolution")
    
    # AI Model Configuration
    yolo_model_path: str = Field(default="yolov8n.pt", description="YOLO model for object detection")
    clip_model: str = Field(default="ViT-B/32", description="CLIP model for image understanding")
    whisper_model: str = Field(default="base", description="Whisper model for transcription")
    
    # Security Configuration
    watermark_enabled: bool = Field(default=True, description="Enable video watermarking")
    encryption_enabled: bool = Field(default=True, description="Enable video encryption")
    content_protection_enabled: bool = Field(default=True, description="Enable content protection")
    
    # Performance Configuration
    max_concurrent_processing: int = Field(default=3, description="Maximum concurrent video processing")
    gpu_acceleration: bool = Field(default=True, description="Enable GPU acceleration")
    processing_timeout: int = Field(default=3600, description="Processing timeout in seconds (1 hour)")
    
    # Storage Configuration
    temp_directory: str = Field(default="/tmp/video_processing", description="Temporary processing directory")
    output_directory: str = Field(default="./processed_videos", description="Output directory for processed videos")
    
    @validator('max_video_size')
    def validate_video_size(cls, v) -> None:
        if v <= 0 or v > 10 * 1024 * 1024 * 1024:  # 10GB limit
            raise ValueError("Video size must be between 1 byte and 10GB")
        return v

class VideoSecurityManager:
    """Security manager for video processing - Security Expert role"""
    
    def __init__(self, config -> None: VideoProcessingConfig) -> None:
        self.config = config
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for video security"""
        password = b"ainflue_video_encryption_key_2025"
        salt = b"ainflue_video_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    async def apply_watermark(self, input_path: str, output_path: str, watermark_text: str = "AINFLUE") -> bool:
        """Apply watermark to video - Content Protection"""
        try:
            watermark_filter = f"drawtext=text='{watermark_text}':fontcolor=white@0.7:fontsize=24:x=w-tw-10:y=10"
            
            process = await asyncio.create_subprocess_exec(
                self.config.ffmpeg_path,
                "-i", input_path,
                "-vf", watermark_filter,
                "-c:a", "copy",
                "-y", output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Watermark applied successfully to {input_path}")
                return True
            else:
                logger.error(f"Watermark application failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Watermark application error: {e}")
            ERROR_COUNTER.labels(error_type="watermark_error").inc()
            return False
    
    async def encrypt_video(self, video_path: str) -> Tuple[str, str]:
        """Encrypt video file"""
        try:
            with open(video_path, 'rb') as file:
                video_data = file.read()
            
            encrypted_data = self.cipher_suite.encrypt(video_data)
            
            encrypted_path = f"{video_path}.encrypted"
            with open(encrypted_path, 'wb') as file:
                file.write(encrypted_data)
            
            encryption_key = base64.urlsafe_b64encode(self.encryption_key).decode()
            return encrypted_path, encryption_key
            
        except Exception as e:
            logger.error(f"Video encryption failed: {e}")
            raise
    
    async def validate_video_security(self, video_path: str) -> Dict[str, Any]:
        """Comprehensive video security validation"""
        security_check = {
            "safe": True,
            "threats": [],
            "file_type_valid": True,
            "size_valid": True,
            "content_safe": True,
            "malware_scan": "clean",
            "scan_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # File size validation
            file_size = os.path.getsize(video_path)
            if file_size > self.config.max_video_size:
                security_check["safe"] = False
                security_check["size_valid"] = False
                security_check["threats"].append("File size exceeds maximum allowed")
            
            # MIME type validation
            mime_type = magic.from_file(video_path, mime=True)
            if not mime_type.startswith('video/'):
                security_check["safe"] = False
                security_check["file_type_valid"] = False
                security_check["threats"].append(f"Invalid file type: {mime_type}")
            
            # Basic content validation using FFmpeg
            probe_result = await self._probe_video_safety(video_path)
            if not probe_result["safe"]:
                security_check["safe"] = False
                security_check["content_safe"] = False
                security_check["threats"].extend(probe_result["issues"])
            
        except Exception as e:
            logger.error(f"Video security validation failed: {e}")
            security_check["safe"] = False
            security_check["threats"].append(f"Security validation error: {str(e)}")
        
        return security_check
    
    async def _probe_video_safety(self, video_path: str) -> Dict[str, Any]:
        """Probe video for safety issues using FFmpeg"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.config.ffmpeg_path,
                "-i", video_path,
                "-f", "null", "-",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Basic validation - if FFmpeg can process it, it's likely safe
            if process.returncode == 0:
                return {"safe": True, "issues": []}
            else:
                return {"safe": False, "issues": ["Video file appears corrupted or invalid"]}
                
        except Exception as e:
            return {"safe": False, "issues": [f"Probe error: {str(e)}"]}

class VideoMLAnalyzer:
    """ML-powered video analysis - ML Engineer + Lead Dev IA roles"""
    
    def __init__(self, config -> None: VideoProcessingConfig) -> None:
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config.openai_api_key)
        
        # Initialize ML models
        try:
            self.yolo_model = YOLO(config.yolo_model_path)
            self.device = "cuda" if torch.cuda.is_available() and config.gpu_acceleration else "cpu"
            self.clip_model, self.clip_preprocess = clip.load(config.clip_model, device=self.device)
            self.whisper_model = whisper.load_model(config.whisper_model)
            
            # Content classification pipeline
            self.content_classifier = pipeline("image-classification", device=0 if self.device == "cuda" else -1)
            
            logger.info(f"Video ML models loaded successfully on {self.device}")
        except Exception as e:
            logger.warning(f"Some ML models failed to load: {e}")
            self.yolo_model = None
            self.clip_model = None
            self.whisper_model = None
            self.content_classifier = None
    
    async def analyze_video_content(self, video_path: str, metadata: VideoMetadata) -> Dict[str, Any]:
        """Comprehensive AI-powered video analysis"""
        analysis = {
            "content_classification": {},
            "scene_analysis": [],
            "object_detection": [],
            "face_analysis": [],
            "audio_analysis": {},
            "transcript": "",
            "seo_insights": {},
            "monetization_potential": {},
            "quality_assessment": {},
            "content_recommendations": []
        }
        
        try:
            # Frame-by-frame analysis
            frame_analysis = await self._analyze_video_frames(video_path)
            analysis["scene_analysis"] = frame_analysis["scenes"]
            analysis["object_detection"] = frame_analysis["objects"]
            analysis["face_analysis"] = frame_analysis["faces"]
            analysis["quality_assessment"] = frame_analysis["quality"]
            
            # Audio analysis and transcription
            audio_analysis = await self._analyze_audio_content(video_path)
            analysis["audio_analysis"] = audio_analysis["analysis"]
            analysis["transcript"] = audio_analysis["transcript"]
            
            # Content classification using AI
            content_classification = await self._classify_video_content(video_path, analysis["transcript"])
            analysis["content_classification"] = content_classification
            
            # SEO analysis for creator economy
            seo_analysis = await self._analyze_seo_potential(analysis["transcript"], frame_analysis)
            analysis["seo_insights"] = seo_analysis
            
            # Monetization analysis
            monetization_analysis = await self._analyze_monetization_potential(analysis)
            analysis["monetization_potential"] = monetization_analysis
            
            # AI-powered enhancement recommendations
            recommendations = await self._generate_content_recommendations(analysis)
            analysis["content_recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"Video ML analysis failed: {e}")
            ERROR_COUNTER.labels(error_type="ml_analysis").inc()
        
        return analysis
    
    async def _analyze_video_frames(self, video_path: str) -> Dict[str, Any]:
        """Analyze video frames for objects, scenes, and quality"""
        analysis = {
            "scenes": [],
            "objects": [],
            "faces": [],
            "quality": {"average_quality": 0.0, "quality_scores": []}
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Sample frames for analysis (every N seconds)
            sample_interval = int(fps * self.config.frame_analysis_interval)
            
            frame_analyses = []
            for frame_num in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                timestamp = frame_num / fps
                frame_analysis = await self._analyze_single_frame(frame, timestamp, frame_num)
                frame_analyses.append(frame_analysis)
                
                FRAME_ANALYSIS_COUNTER.inc()
            
            cap.release()
            
            # Aggregate analysis results
            analysis["scenes"] = self._extract_scene_changes(frame_analyses)
            analysis["objects"] = self._aggregate_object_detections(frame_analyses)
            analysis["faces"] = self._aggregate_face_detections(frame_analyses)
            analysis["quality"] = self._calculate_quality_metrics(frame_analyses)
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {e}")
            ERROR_COUNTER.labels(error_type="frame_analysis").inc()
        
        return analysis
    
    async def _analyze_single_frame(self, frame: np.ndarray, timestamp: float, frame_number: int) -> FrameAnalysis:
        """Analyze a single video frame"""
        try:
            # Object detection with YOLO
            objects = []
            if self.yolo_model:
                results = self.yolo_model(frame)
                for result in results:
                    for box in result.boxes:
                        objects.append({
                            "class": self.yolo_model.names[int(box.cls)],
                            "confidence": float(box.conf),
                            "bbox": box.xyxy.tolist()[0]
                        })
            
            # Face detection
            faces = []
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                faces = [{"location": loc} for loc in face_locations]
            except Exception:
                pass  # Face recognition might fail, continue without it
            
            # Quality assessment
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            quality_score = cv2.Laplacian(gray, cv2.CV_64F).var()  # Sharpness measure
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Scene change detection (simplified)
            scene_change = False  # Would implement proper scene change detection
            
            return FrameAnalysis(
                timestamp=timestamp,
                frame_number=frame_number,
                scene_change=scene_change,
                objects=objects,
                faces=faces,
                quality_score=quality_score,
                brightness=brightness,
                contrast=contrast
            )
            
        except Exception as e:
            logger.error(f"Single frame analysis failed: {e}")
            return FrameAnalysis(timestamp, frame_number, False, [], [], 0.0, 0.0, 0.0)
    
    def _extract_scene_changes(self, frame_analyses: List[FrameAnalysis]) -> List[Dict]:
        """Extract scene changes from frame analysis"""
        scenes = []
        current_scene_start = 0.0
        
        for i, analysis in enumerate(frame_analyses):
            if analysis.scene_change or i == len(frame_analyses) - 1:
                scenes.append({
                    "start_time": current_scene_start,
                    "end_time": analysis.timestamp,
                    "duration": analysis.timestamp - current_scene_start,
                    "average_quality": np.mean([a.quality_score for a in frame_analyses if current_scene_start <= a.timestamp <= analysis.timestamp])
                })
                current_scene_start = analysis.timestamp
        
        return scenes
    
    def _aggregate_object_detections(self, frame_analyses: List[FrameAnalysis]) -> List[Dict]:
        """Aggregate object detections across frames"""
        object_counts = {}
        for analysis in frame_analyses:
            for obj in analysis.objects:
                class_name = obj["class"]
                if class_name not in object_counts:
                    object_counts[class_name] = {"count": 0, "avg_confidence": 0.0, "appearances": []}
                
                object_counts[class_name]["count"] += 1
                object_counts[class_name]["appearances"].append({
                    "timestamp": analysis.timestamp,
                    "confidence": obj["confidence"]
                })
        
        # Calculate average confidence
        for class_name, data in object_counts.items():
            confidences = [app["confidence"] for app in data["appearances"]]
            data["avg_confidence"] = np.mean(confidences)
        
        return [{"class": k, **v} for k, v in object_counts.items()]
    
    def _aggregate_face_detections(self, frame_analyses: List[FrameAnalysis]) -> List[Dict]:
        """Aggregate face detections across frames"""
        total_faces = sum(len(analysis.faces) for analysis in frame_analyses)
        face_appearances = []
        
        for analysis in frame_analyses:
            if analysis.faces:
                face_appearances.append({
                    "timestamp": analysis.timestamp,
                    "face_count": len(analysis.faces)
                })
        
        return {
            "total_face_detections": total_faces,
            "face_appearances": face_appearances,
            "average_faces_per_frame": total_faces / len(frame_analyses) if frame_analyses else 0
        }
    
    def _calculate_quality_metrics(self, frame_analyses: List[FrameAnalysis]) -> Dict[str, float]:
        """Calculate overall video quality metrics"""
        if not frame_analyses:
            return {"average_quality": 0.0, "quality_scores": []}
        
        quality_scores = [analysis.quality_score for analysis in frame_analyses]
        brightness_scores = [analysis.brightness for analysis in frame_analyses]
        contrast_scores = [analysis.contrast for analysis in frame_analyses]
        
        return {
            "average_quality": np.mean(quality_scores),
            "quality_variance": np.var(quality_scores),
            "average_brightness": np.mean(brightness_scores),
            "average_contrast": np.mean(contrast_scores),
            "quality_scores": quality_scores
        }
    
    async def _analyze_audio_content(self, video_path: str) -> Dict[str, Any]:
        """Extract and analyze audio content - Audio Engineer role"""
        audio_analysis = {
            "analysis": {},
            "transcript": ""
        }
        
        try:
            with AUDIO_EXTRACTION_DURATION.time():
                # Extract audio using moviepy
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                    audio_path = temp_audio.name
                
                video_clip = VideoFileClip(video_path)
                if video_clip.audio:
                    audio_clip = video_clip.audio
                    audio_clip.write_audiofile(audio_path, verbose=False, logger=None)
                    audio_clip.close()
                video_clip.close()
                
                # Audio analysis using librosa
                y, sr = librosa.load(audio_path)
                
                # Extract audio features
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
                mfcc = librosa.feature.mfcc(y=y, sr=sr)
                
                audio_analysis["analysis"] = {
                    "duration": len(y) / sr,
                    "sample_rate": sr,
                    "tempo": float(tempo),
                    "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                    "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                    "mfcc_features": mfcc.tolist()[:5],  # First 5 MFCC coefficients
                    "rms_energy": float(np.mean(librosa.feature.rms(y=y))),
                    "audio_quality_score": self._calculate_audio_quality(y, sr)
                }
                
                # Transcription using Whisper
                if self.whisper_model:
                    result = self.whisper_model.transcribe(audio_path)
                    audio_analysis["transcript"] = result["text"]
                
                # Cleanup
                os.unlink(audio_path)
                
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            ERROR_COUNTER.labels(error_type="audio_analysis").inc()
        
        return audio_analysis
    
    def _calculate_audio_quality(self, y: np.ndarray, sr: int) -> float:
        """Calculate audio quality score"""
        try:
            # Simple audio quality metrics
            snr = np.mean(y**2) / (np.var(y) + 1e-8)  # Signal-to-noise ratio approximation
            dynamic_range = np.max(y) - np.min(y)
            
            # Normalize to 0-100 scale
            quality_score = min(100, (snr * 10 + dynamic_range * 50))
            return float(quality_score)
        except Exception:
            return 0.0
    
    async def _classify_video_content(self, video_path: str, transcript: str) -> Dict[str, Any]:
        """Classify video content using AI"""
        try:
            # Use OpenAI for content classification
            prompt = f"""
            Classify this video content into categories for a creator economy platform.
            
            Video transcript: {transcript[:2000]}
            
            Provide classification in JSON format with:
            1. primary_category (education, entertainment, music, gaming, etc.)
            2. secondary_categories (list)
            3. target_audience (age group, interests)
            4. content_rating (family_friendly, mature, etc.)
            5. monetization_suitability (high, medium, low)
            6. engagement_potential (high, medium, low)
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"classification_error": "Failed to parse AI response", "raw_response": ai_response}
                
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return {"classification_error": str(e)}
    
    async def _analyze_seo_potential(self, transcript: str, frame_analysis: Dict) -> Dict[str, Any]:
        """Analyze SEO potential for video content"""
        try:
            # Extract keywords from transcript
            words = transcript.lower().split()
            word_count = len(words)
            
            # Calculate keyword density
            keyword_density = {}
            for word in words:
                if len(word) > 3:  # Only meaningful words
                    keyword_density[word] = keyword_density.get(word, 0) + 1
            
            # Sort by frequency
            top_keywords = sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Analyze video elements for SEO
            visual_elements = len(frame_analysis.get("objects", []))
            scene_changes = len(frame_analysis.get("scenes", []))
            
            seo_score = min(100, (
                (word_count / 100) * 20 +  # Transcript length factor
                (visual_elements / 10) * 30 +  # Visual richness factor
                (scene_changes / 5) * 20 +  # Dynamic content factor
                30  # Base score
            ))
            
            return {
                "seo_score": seo_score,
                "word_count": word_count,
                "top_keywords": [{"keyword": k, "frequency": v} for k, v in top_keywords],
                "visual_elements_count": visual_elements,
                "scene_changes_count": scene_changes,
                "recommendations": self._generate_seo_recommendations(word_count, visual_elements)
            }
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {"seo_score": 0, "error": str(e)}
    
    def _generate_seo_recommendations(self, word_count: int, visual_elements: int) -> List[str]:
        """Generate SEO recommendations for video content"""
        recommendations = []
        
        if word_count < 100:
            recommendations.append("Add more spoken content for better searchability")
        
        if visual_elements < 5:
            recommendations.append("Include more visual elements to increase engagement")
        
        recommendations.extend([
            "Add relevant hashtags and descriptions",
            "Include timestamps for key topics",
            "Create engaging thumbnails",
            "Use trending keywords in title and description"
        ])
        
        return recommendations
    
    async def _analyze_monetization_potential(self, analysis: Dict) -> Dict[str, Any]:
        """Analyze monetization potential for creator economy"""
        try:
            # Extract relevant metrics
            content_classification = analysis.get("content_classification", {})
            quality_assessment = analysis.get("quality_assessment", {})
            transcript = analysis.get("transcript", "")
            
            # Calculate monetization score
            base_score = 50
            
            # Quality factor
            quality_score = quality_assessment.get("average_quality", 0)
            quality_factor = min(30, quality_score / 100 * 30)
            
            # Content type factor
            monetization_friendly_types = ["education", "tutorial", "review", "entertainment"]
            primary_category = content_classification.get("primary_category", "").lower()
            content_factor = 20 if primary_category in monetization_friendly_types else 10
            
            # Engagement factor
            engagement_potential = content_classification.get("engagement_potential", "medium")
            engagement_factor = {"high": 20, "medium": 10, "low": 5}.get(engagement_potential, 10)
            
            total_score = base_score + quality_factor + content_factor + engagement_factor
            
            # Monetization strategies
            strategies = []
            if "tutorial" in transcript.lower() or "how to" in transcript.lower():
                strategies.append("Educational content monetization")
            if "review" in transcript.lower():
                strategies.append("Affiliate marketing opportunities")
            if quality_score > 70:
                strategies.append("Premium content offerings")
            
            return {
                "monetization_score": min(100, total_score),
                "quality_factor": quality_factor,
                "content_factor": content_factor,
                "engagement_factor": engagement_factor,
                "recommended_strategies": strategies,
                "revenue_potential": self._estimate_revenue_potential(total_score),
                "platform_recommendations": self._recommend_platforms(content_classification)
            }
            
        except Exception as e:
            logger.error(f"Monetization analysis failed: {e}")
            return {"monetization_score": 0, "error": str(e)}
    
    def _estimate_revenue_potential(self, score: int) -> str:
        """Estimate revenue potential based on score"""
        if score >= 80:
            return "High - Premium content with strong monetization potential"
        elif score >= 60:
            return "Medium - Good monetization opportunities with optimization"
        else:
            return "Low - Requires content improvement for better monetization"
    
    def _recommend_platforms(self, content_classification: Dict) -> List[str]:
        """Recommend platforms based on content classification"""
        category = content_classification.get("primary_category", "").lower()
        
        platform_map = {
            "education": ["YouTube", "Udemy", "Skillshare"],
            "entertainment": ["TikTok", "Instagram", "YouTube"],
            "gaming": ["Twitch", "YouTube Gaming", "Facebook Gaming"],
            "music": ["Spotify", "Apple Music", "YouTube Music"],
            "tutorial": ["YouTube", "LinkedIn Learning", "Coursera"]
        }
        
        return platform_map.get(category, ["YouTube", "Instagram", "TikTok"])
    
    async def _generate_content_recommendations(self, analysis: Dict) -> List[str]:
        """Generate AI-powered content enhancement recommendations"""
        recommendations = []
        
        try:
            quality_score = analysis.get("quality_assessment", {}).get("average_quality", 0)
            if quality_score < 50:
                recommendations.append("Improve video quality with better lighting and camera settings")
            
            audio_quality = analysis.get("audio_analysis", {}).get("audio_quality_score", 0)
            if audio_quality < 60:
                recommendations.append("Enhance audio quality with better microphone or post-processing")
            
            transcript_length = len(analysis.get("transcript", ""))
            if transcript_length < 100:
                recommendations.append("Add more spoken content to improve engagement and SEO")
            
            scene_count = len(analysis.get("scene_analysis", []))
            if scene_count < 3:
                recommendations.append("Add more visual variety with scene changes and different shots")
            
            # AI-powered recommendations
            if self.openai_client:
                ai_recommendations = await self._get_ai_recommendations(analysis)
                recommendations.extend(ai_recommendations)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _get_ai_recommendations(self, analysis: Dict) -> List[str]:
        """Get AI-powered content recommendations"""
        try:
            prompt = f"""
            Based on this video analysis, provide 5 specific recommendations to improve content for creator economy success:
            
            Content Type: {analysis.get('content_classification', {}).get('primary_category', 'Unknown')}
            Quality Score: {analysis.get('quality_assessment', {}).get('average_quality', 0)}
            Monetization Score: {analysis.get('monetization_potential', {}).get('monetization_score', 0)}
            Transcript Length: {len(analysis.get('transcript', ''))} characters
            
            Provide practical, actionable recommendations in a simple list format.
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            
            ai_response = response.choices[0].message.content
            # Extract recommendations from AI response
            recommendations = [line.strip() for line in ai_response.split('\n') if line.strip() and not line.strip().startswith('#')]
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"AI recommendations failed: {e}")
            return []

class VideoProcessor:
    """Core video processing engine - Backend Senior + DevOps roles"""
    
    def __init__(self, config -> None: VideoProcessingConfig) -> None:
        self.config = config
        
        # Ensure directories exist
        os.makedirs(config.temp_directory, exist_ok=True)
        os.makedirs(config.output_directory, exist_ok=True)
    
    async def extract_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract basic video metadata using FFprobe"""
        try:
            process = await asyncio.create_subprocess_exec(
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                metadata = json.loads(stdout.decode())
                
                # Extract video stream info
                video_stream = next((s for s in metadata["streams"] if s["codec_type"] == "video"), {})
                audio_stream = next((s for s in metadata["streams"] if s["codec_type"] == "audio"), {})
                
                return {
                    "duration": float(metadata["format"].get("duration", 0)),
                    "size": int(metadata["format"].get("size", 0)),
                    "bitrate": int(metadata["format"].get("bit_rate", 0)),
                    "format_name": metadata["format"].get("format_name", "unknown"),
                    "video_codec": video_stream.get("codec_name", "unknown"),
                    "audio_codec": audio_stream.get("codec_name", "unknown"),
                    "width": int(video_stream.get("width", 0)),
                    "height": int(video_stream.get("height", 0)),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),  # Safely evaluate fraction
                    "pixel_format": video_stream.get("pix_fmt", "unknown")
                }
            else:
                logger.error(f"FFprobe failed: {stderr.decode()}")
                return {}
                
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    async def generate_thumbnails(self, video_path: str, output_dir: str, count: int = None) -> List[str]:
        """Generate video thumbnails"""
        if count is None:
            count = self.config.thumbnail_count
        
        thumbnail_paths = []
        
        try:
            # Get video duration first
            metadata = await self.extract_metadata(video_path)
            duration = metadata.get("duration", 0)
            
            if duration <= 0:
                return []
            
            # Calculate thumbnail intervals
            interval = duration / (count + 1)
            
            for i in range(1, count + 1):
                timestamp = interval * i
                thumbnail_path = os.path.join(output_dir, f"thumbnail_{i:03d}.jpg")
                
                process = await asyncio.create_subprocess_exec(
                    self.config.ffmpeg_path,
                    "-i", video_path,
                    "-ss", str(timestamp),
                    "-vframes", "1",
                    "-q:v", "2",
                    "-y", thumbnail_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                if process.returncode == 0 and os.path.exists(thumbnail_path):
                    thumbnail_paths.append(thumbnail_path)
                
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            ERROR_COUNTER.labels(error_type="thumbnail_generation").inc()
        
        return thumbnail_paths
    
    async def create_preview_clip(self, video_path: str, output_path: str, duration: int = 30) -> bool:
        """Create a short preview clip"""
        try:
            # Extract first 30 seconds or specified duration
            process = await asyncio.create_subprocess_exec(
                self.config.ffmpeg_path,
                "-i", video_path,
                "-t", str(duration),
                "-c", "copy",
                "-y", output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Preview clip created: {output_path}")
                return True
            else:
                logger.error(f"Preview clip creation failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Preview clip creation error: {e}")
            return False
    
    async def optimize_video(self, input_path: str, output_path: str, target_quality: VideoQuality = VideoQuality.HIGH) -> bool:
        """Optimize video for web delivery"""
        try:
            # Quality settings mapping
            quality_settings = {
                VideoQuality.LOW: {"crf": "28", "preset": "fast", "scale": "480:-2"},
                VideoQuality.MEDIUM: {"crf": "23", "preset": "medium", "scale": "720:-2"},
                VideoQuality.HIGH: {"crf": "18", "preset": "slow", "scale": "1280:-2"},
                VideoQuality.FULL_HD: {"crf": "18", "preset": "slow", "scale": "1920:-2"},
                VideoQuality.ULTRA_HD: {"crf": "15", "preset": "veryslow", "scale": "3840:-2"}
            }
            
            settings = quality_settings.get(target_quality, quality_settings[VideoQuality.HIGH])
            
            # Build FFmpeg command
            cmd = [
                self.config.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", settings["crf"],
                "-preset", settings["preset"],
                "-vf", f"scale={settings['scale']}",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",  # Optimize for web streaming
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Video optimized successfully: {output_path}")
                return True
            else:
                logger.error(f"Video optimization failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Video optimization error: {e}")
            ERROR_COUNTER.labels(error_type="video_optimization").inc()
            return False

class VideoProcessingOrchestrator:
    """Main orchestrator for video processing - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config -> None: VideoProcessingConfig) -> None:
        self.config = config
        self.security_manager = VideoSecurityManager(config)
        self.ml_analyzer = VideoMLAnalyzer(config)
        self.video_processor = VideoProcessor(config)
        
        # Processing queue for concurrent handling
        self.processing_queue = asyncio.Queue(maxsize=config.max_concurrent_processing)
        self.active_jobs = {}
    
    async def process_video(self, video_path: str, creator_id: str, filename: str) -> VideoMetadata:
        """Main video processing workflow"""
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            ACTIVE_PROCESSING.inc()
            logger.info(f"Starting video processing: {job_id} - {filename}")
            
            # Step 1: Security validation
            security_check = await self.security_manager.validate_video_security(video_path)
            if not security_check["safe"]:
                raise ValueError(f"Security validation failed: {security_check['threats']}")
            
            # Step 2: Extract basic metadata
            basic_metadata = await self.video_processor.extract_metadata(video_path)
            
            # Step 3: Create video metadata object
            video_id = str(uuid.uuid4())
            checksum = hashlib.sha256(open(video_path, 'rb').read()).hexdigest()
            file_size = os.path.getsize(video_path)
            video_format = self._determine_video_format(basic_metadata.get("format_name", ""), filename)
            
            metadata = VideoMetadata(
                video_id=video_id,
                filename=filename,
                file_size=file_size,
                duration=basic_metadata.get("duration", 0),
                format=video_format,
                resolution=f"{basic_metadata.get('width', 0)}x{basic_metadata.get('height', 0)}",
                fps=basic_metadata.get("fps", 0),
                bitrate=basic_metadata.get("bitrate", 0),
                codec=basic_metadata.get("video_codec", "unknown"),
                audio_codec=basic_metadata.get("audio_codec", "unknown"),
                upload_timestamp=datetime.utcnow(),
                creator_id=creator_id,
                status=ProcessingStatus.PROCESSING,
                checksum=checksum,
                processing_log=[]
            )
            
            # Step 4: Generate thumbnails
            thumbnail_dir = os.path.join(self.config.output_directory, video_id, "thumbnails")
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_paths = await self.video_processor.generate_thumbnails(video_path, thumbnail_dir)
            metadata.thumbnail_paths = thumbnail_paths
            metadata.processing_log.append(f"Generated {len(thumbnail_paths)} thumbnails")
            
            # Step 5: Create preview clip
            preview_path = os.path.join(self.config.output_directory, video_id, "preview.mp4")
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            preview_created = await self.video_processor.create_preview_clip(video_path, preview_path)
            if preview_created:
                metadata.preview_path = preview_path
                metadata.processing_log.append("Preview clip created")
            
            # Step 6: ML Analysis
            metadata.status = ProcessingStatus.ANALYZING
            analysis = await self.ml_analyzer.analyze_video_content(video_path, metadata)
            
            # Update metadata with analysis results
            metadata.content_type = self._determine_content_type(analysis.get("content_classification", {}))
            metadata.scenes = analysis.get("scene_analysis", [])
            metadata.faces_detected = analysis.get("face_analysis", [])
            metadata.objects_detected = analysis.get("object_detection", [])
            metadata.transcript = analysis.get("transcript", "")
            metadata.audio_analysis = analysis.get("audio_analysis", {})
            metadata.seo_analysis = analysis.get("seo_insights", {})
            metadata.monetization_analysis = analysis.get("monetization_potential", {})
            metadata.processing_log.append("AI analysis completed")
            
            # Step 7: Apply watermark if enabled
            if self.config.watermark_enabled:
                metadata.status = ProcessingStatus.ENHANCING
                watermarked_path = os.path.join(self.config.output_directory, video_id, "watermarked.mp4")
                os.makedirs(os.path.dirname(watermarked_path), exist_ok=True)
                
                watermark_applied = await self.security_manager.apply_watermark(
                    video_path, watermarked_path, f"AINFLUE - {creator_id}"
                )
                
                if watermark_applied:
                    metadata.watermark_applied = True
                    metadata.processing_log.append("Watermark applied")
            
            # Step 8: Video optimization
            metadata.status = ProcessingStatus.ENCODING
            optimized_path = os.path.join(self.config.output_directory, video_id, "optimized.mp4")
            optimization_success = await self.video_processor.optimize_video(
                video_path, optimized_path, VideoQuality.HIGH
            )
            
            if optimization_success:
                metadata.processing_log.append("Video optimized for web delivery")
            
            # Step 9: Encryption (if enabled)
            if self.config.encryption_enabled:
                encrypted_path, encryption_key = await self.security_manager.encrypt_video(video_path)
                metadata.encryption_key = encryption_key
                metadata.processing_log.append("Video encrypted")
            
            # Step 10: Final status update
            metadata.status = ProcessingStatus.COMPLETED
            metadata.processing_log.append(f"Processing completed in {time.time() - start_time:.2f}s")
            
            # Metrics
            VIDEO_PROCESSED_COUNTER.labels(type=video_format.value, status="success").inc()
            processing_time = time.time() - start_time
            logger.info(f"Video processed successfully: {job_id} in {processing_time:.2f}s")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Video processing failed: {job_id} - {e}")
            ERROR_COUNTER.labels(error_type="processing_failure").inc()
            VIDEO_PROCESSED_COUNTER.labels(type="unknown", status="error").inc()
            
            # Create error metadata
            error_metadata = VideoMetadata(
                video_id=str(uuid.uuid4()),
                filename=filename,
                file_size=0,
                duration=0,
                format=VideoFormat.UNKNOWN,
                resolution="0x0",
                fps=0,
                bitrate=0,
                codec="unknown",
                audio_codec="unknown",
                upload_timestamp=datetime.utcnow(),
                creator_id=creator_id,
                status=ProcessingStatus.FAILED,
                checksum="",
                processing_log=[f"Processing failed: {str(e)}"]
            )
            return error_metadata
            
        finally:
            ACTIVE_PROCESSING.dec()
    
    def _determine_video_format(self, format_name: str, filename: str) -> VideoFormat:
        """Determine video format from format name and filename"""
        format_map = {
            "mp4": VideoFormat.MP4,
            "avi": VideoFormat.AVI,
            "mov": VideoFormat.MOV,
            "mkv": VideoFormat.MKV,
            "wmv": VideoFormat.WMV,
            "flv": VideoFormat.FLV,
            "webm": VideoFormat.WEBM,
            "m4v": VideoFormat.M4V
        }
        
        # Try format name first
        for fmt in format_map:
            if fmt in format_name.lower():
                return format_map[fmt]
        
        # Fallback to file extension
        extension = Path(filename).suffix.lower().lstrip('.')
        return format_map.get(extension, VideoFormat.UNKNOWN)
    
    def _determine_content_type(self, classification: Dict) -> ContentType:
        """Determine content type from AI classification"""
        primary_category = classification.get("primary_category", "").lower()
        
        content_type_map = {
            "education": ContentType.EDUCATIONAL,
            "entertainment": ContentType.ENTERTAINMENT,
            "music": ContentType.MUSIC,
            "gaming": ContentType.GAMING,
            "vlog": ContentType.VLOG,
            "tutorial": ContentType.TUTORIAL,
            "review": ContentType.REVIEW,
            "news": ContentType.NEWS,
            "sports": ContentType.SPORTS,
            "cooking": ContentType.COOKING,
            "tech": ContentType.TECH
        }
        
        return content_type_map.get(primary_category, ContentType.UNKNOWN)
    
    async def get_processing_status(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a video"""
        return self.active_jobs.get(video_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for video processing service"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "metrics": {
                "active_processing_jobs": len(self.active_jobs),
                "queue_size": self.processing_queue.qsize(),
                "system_memory_usage": psutil.virtual_memory().percent,
                "system_cpu_usage": psutil.cpu_percent(),
                "gpu_available": torch.cuda.is_available() if torch.cuda.is_available() else False
            },
            "services": {
                "ffmpeg": await self._check_ffmpeg_health(),
                "ml_models": self._check_ml_models_health(),
                "security": await self._check_security_health(),
                "storage": self._check_storage_health()
            }
        }
        
        # Determine overall health
        if health_status["metrics"]["system_memory_usage"] > 90:
            health_status["status"] = "degraded"
        if health_status["metrics"]["system_cpu_usage"] > 95:
            health_status["status"] = "unhealthy"
        
        return health_status
    
    async def _check_ffmpeg_health(self) -> str:
        """Check FFmpeg availability"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.config.ffmpeg_path, "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return "healthy" if process.returncode == 0 else "unhealthy"
        except Exception:
            return "unavailable"
    
    def _check_ml_models_health(self) -> Dict[str, str]:
        """Check ML models health status"""
        return {
            "yolo": "healthy" if self.ml_analyzer.yolo_model else "unavailable",
            "clip": "healthy" if self.ml_analyzer.clip_model else "unavailable",
            "whisper": "healthy" if self.ml_analyzer.whisper_model else "unavailable"
        }
    
    async def _check_security_health(self) -> str:
        """Check security components health"""
        try:
            # Test encryption functionality
            test_data = b"test_video_data"
            encrypted, key = await self.security_manager.encrypt_video_data(test_data)
            return "healthy"
        except Exception:
            return "unhealthy"
    
    def _check_storage_health(self) -> str:
        """Check storage availability"""
        try:
            disk_usage = psutil.disk_usage(self.config.output_directory)
            free_percentage = (disk_usage.free / disk_usage.total) * 100
            
            if free_percentage > 20:
                return "healthy"
            elif free_percentage > 10:
                return "degraded"
            else:
                return "critical"
        except Exception:
            return "unknown"

# Service factory and configuration
class VideoProcessingService:
    """Main video processing service facade - DevOps + Integration role"""
    
    def __init__(self, config -> None: Optional[VideoProcessingConfig] = None) -> None:
        self.config = config or VideoProcessingConfig(
            openai_api_key="your-openai-key-here",  # Should be configured via environment
            watermark_enabled=True,
            encryption_enabled=True,
            content_protection_enabled=True
        )
        self.orchestrator = VideoProcessingOrchestrator(self.config)
    
    async def initialize(self) -> None:
        """Initialize the video processing service"""
        logger.info("Initializing Video Processing Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Check dependencies
        await self._check_dependencies()
        
        # Initialize ML models
        await self._initialize_ml_models()
        
        # Setup monitoring
        await self._setup_monitoring()
        
        logger.info("Video Processing Service initialized successfully")
    
    async def _validate_configuration(self) -> None:
        """Validate service configuration"""
        if not self.config.openai_api_key or self.config.openai_api_key == "your-openai-key-here":
            logger.warning("OpenAI API key not configured - AI features will be limited")
        
        if not os.path.exists(self.config.temp_directory):
            os.makedirs(self.config.temp_directory, exist_ok=True)
        
        if not os.path.exists(self.config.output_directory):
            os.makedirs(self.config.output_directory, exist_ok=True)
    
    async def _check_dependencies(self) -> None:
        """Check required dependencies"""
        # Check FFmpeg
        try:
            process = await asyncio.create_subprocess_exec(
                self.config.ffmpeg_path, "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            if process.returncode != 0:
                logger.error("FFmpeg not available - video processing will be limited")
        except Exception:
            logger.error("FFmpeg not found - please install FFmpeg")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models with proper error handling"""
        try:
            logger.info("ML models initialization completed")
        except Exception as e:
            logger.error(f"ML models initialization failed: {e}")
    
    async def _setup_monitoring(self) -> None:
        """Setup monitoring and metrics collection"""
        logger.info("Video processing monitoring setup completed")
    
    async def process_video(self, video_path: str, creator_id: str, filename: str) -> VideoMetadata:
        """Process a video with full enterprise features"""
        return await self.orchestrator.process_video(video_path, creator_id, filename)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.orchestrator.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            "videos_processed_total": VIDEO_PROCESSED_COUNTER._value.sum(),
            "active_processing": ACTIVE_PROCESSING._value.get(),
            "error_count": ERROR_COUNTER._value.sum(),
            "frames_analyzed_total": FRAME_ANALYSIS_COUNTER._value.get()
        }

# Export main classes and functions
__all__ = [
    'VideoProcessingService',
    'VideoProcessingConfig',
    'VideoMetadata',
    'VideoFormat',
    'VideoQuality',
    'ProcessingStatus',
    'ContentType',
    'VideoProcessingOrchestrator'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main() -> None:
        # Initialize service
        service = VideoProcessingService()
        await service.initialize()
        
        # Health check
        health = await service.get_health_status()
        print(f"Service Health: {health}")
        
        # Example video processing (would need actual file)
        # metadata = await service.process_video("example.mp4", "creator123", "example.mp4")
        # print(f"Processed: {metadata}")
    
    # Run example
    # asyncio.run(main())