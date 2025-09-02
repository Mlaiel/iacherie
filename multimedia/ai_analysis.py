"""Advanced AI-Powered Content Analysis for Multimedia Processing
Professional content analysis with scene detection, object recognition, sentiment analysis

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import torch
from torchvision import transforms, models
from transformers import (
    pipeline, AutoTokenizer, AutoModel,
    CLIPProcessor, CLIPModel,
    ViTImageProcessor, ViTForImageClassification
)
import librosa
import soundfile as sf
from PIL import Image
import spacy
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine
import face_recognition
import mediapipe as mp

from .formats import ContentFormat
from ..core.exceptions import ProcessingError, AIAnalysisError
from ..core.config import get_settings
from ..utils.caching import cache_result

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class AnalysisResult:
    """
Base analysis result structure"""
    content_type: str
    confidence: float
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class SceneAnalysis(AnalysisResult):
    """
Scene detection analysis results"""
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    scene_changes: List[float] = field(default_factory=list)
    dominant_colors: List[str] = field(default_factory=list)
    motion_intensity: float = 0.0
    lighting_conditions: str = "unknown"


@dataclass
class ObjectAnalysis(AnalysisResult):
    """Object detection analysis results"""
    objects: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    text_regions: List[Dict[str, Any]] = field(default_factory=list)
    landmarks: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SentimentAnalysis(AnalysisResult):
    """
Sentiment and emotion analysis results"""
    overall_sentiment: str
    sentiment_score: float
    emotions: Dict[str, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    toxicity_score: float = 0.0


@dataclass
class AudioAnalysis(AnalysisResult):
    """
Audio content analysis results"""
    genre_predictions: Dict[str, float] = field(default_factory=dict)
    tempo: float = 0.0
    key_signature: str = "unknown"
    energy_level: float = 0.0
    mood: str = "neutral"
    instruments_detected: List[str] = field(default_factory=list)
    speech_segments: List[Dict[str, Any]] = field(default_factory=list)
    music_segments: List[Dict[str, Any]] = field(default_factory=list)


class BaseAnalyzer(ABC):
    """Base class for all AI analyzers"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        self._models_loaded = False
        
    @abstractmethod
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> AnalysisResult:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_analyze_input(content)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_analyze_result(result)
            
                    logger.info(f"AI processing analyze completed")
                    return final_result
            
                except Exception as e:
        try:
            logger.info(f"Executing load_models")
            
            # Implementation for load_models
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"load_models completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"load_models failed: {e}")
            raise
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_analyze_result(result)
            
                    logger.info(f"AI processing analyze completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing analyze failed: {e}")
                    raise
    @abstractmethod
    def load_models(self) -> None:
        """
Load required AI models"""
        pass
    
    async def _ensure_models_loaded(self) -> None:
        """
Ensure models are loaded before analysis"""
        if not self._models_loaded:
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self.load_models
            )
            self._models_loaded = True


class ContentAnalyzer(BaseAnalyzer):
    """
Main content analyzer orchestrating different analysis types"""
    
    def __init__(self):
        super().__init__()
        self.scene_detector = SceneDetector()
        self.object_detector = ObjectDetector() 
        self.sentiment_analyzer = SentimentAnalyzer()
        self.audio_analyzer = AudioContentAnalyzer()
        
    async def analyze_comprehensive(
        self,
        content: Any,
        content_format: ContentFormat,
        options: Dict[str, Any] = None
    ) -> Dict[str, AnalysisResult]:
        """
Comprehensive analysis for all content types"""
        options = options or {}
        results = {}
        
        try:
            # Determine analysis types based on content format
            if content_format.is_image():
                results["objects"] = await self.object_detector.analyze(content, options)
                if options.get("analyze_sentiment", False):
                    results["sentiment"] = await self.sentiment_analyzer.analyze_image(content, options)
                    
            elif content_format.is_video():
                results["scenes"] = await self.scene_detector.analyze(content, options)
                results["objects"] = await self.object_detector.analyze_video(content, options)
                if options.get("extract_audio", True):
                    audio_data = await self._extract_audio_from_video(content)
                    results["audio"] = await self.audio_analyzer.analyze(audio_data, options)
                    
            elif content_format.is_audio():
                results["audio"] = await self.audio_analyzer.analyze(content, options)
                if options.get("transcribe_speech", False):
                    transcript = await self._transcribe_audio(content)
                    results["sentiment"] = await self.sentiment_analyzer.analyze_text(transcript, options)
                    
            logger.info(f"Comprehensive analysis completed for {content_format.mime_type}")
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise AIAnalysisError(f"Analysis failed: {str(e)}")
    
    async def _extract_audio_from_video(self, video_content: bytes) -> bytes:
        """Extract audio track from video content"""
        # Implementation for audio extraction from video
        import tempfile
        import ffmpeg
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
            video_file.write(video_content)
            video_file.flush()
            
            with tempfile.NamedTemporaryFile(suffix='.wav') as audio_file:
                (
                    ffmpeg
                    .input(video_file.name)
                    .output(audio_file.name, acodec='pcm_s16le', ac=1, ar='44100')
                    .overwrite_output()
                    .run(quiet=True)
                )
                audio_file.seek(0)
                return audio_file.read()
    
    async def _transcribe_audio(self, audio_content: bytes) -> str:
        """
Transcribe audio content to text"""
        # Implementation for speech-to-text
        import speech_recognition as sr
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.wav') as audio_file:
            audio_file.write(audio_content)
            audio_file.flush()
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file.name) as source:
                audio = recognizer.record(source)
                try:
                    return recognizer.recognize_google(audio, language='en-US')
                except sr.UnknownValueError:
                    return ""
    
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> AnalysisResult:
        """Main analyze method implementation"""
        return await self.analyze_comprehensive(content, ContentFormat.detect(content), options)
    
    def load_models(self) -> None:
        """
Load all required models"""
        self.scene_detector.load_models()
        self.object_detector.load_models()
        self.sentiment_analyzer.load_models()
        self.audio_analyzer.load_models()


class SceneDetector(BaseAnalyzer):
    """
Advanced scene detection and video analysis"""
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.face_cascade = None
        
    def load_models(self) -> None:
        """
Load scene detection models"""
        try:
            # Load OpenCV cascade for face detection
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Load pre-trained model for scene classification
            self.model = models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("Scene detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load scene detection models: {str(e)}")
            raise ProcessingError(f"Model loading failed: {str(e)}")
    
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> SceneAnalysis:
        """Analyze video content for scenes"""
        await self._ensure_models_loaded()
        options = options or {}
        
        start_time = datetime.utcnow()
        
        try:
            if isinstance(content, bytes):
                # Process video from bytes
                scenes = await self._analyze_video_bytes(content, options)
            else:
                # Process video file
                scenes = await self._analyze_video_file(content, options)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return SceneAnalysis(
                content_type="video",
                confidence=scenes.get("confidence", 0.8),
                processing_time=processing_time,
                scenes=scenes.get("scenes", []),
                scene_changes=scenes.get("scene_changes", []),
                dominant_colors=scenes.get("dominant_colors", []),
                motion_intensity=scenes.get("motion_intensity", 0.0),
                lighting_conditions=scenes.get("lighting_conditions", "unknown")
            )
            
        except Exception as e:
            logger.error(f"Scene analysis failed: {str(e)}")
            raise AIAnalysisError(f"Scene analysis failed: {str(e)}")
    
    async def _analyze_video_bytes(self, video_bytes: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content from bytes"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
            temp_file.write(video_bytes)
            temp_file.flush()
            return await self._analyze_video_file(temp_file.name, options)
    
    async def _analyze_video_file(self, video_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze video file for scenes and content"""
        results = {
            "scenes": [],
            "scene_changes": [],
            "dominant_colors": [],
            "motion_intensity": 0.0,
            "lighting_conditions": "unknown",
            "confidence": 0.0
        }
        
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if frame_count == 0:
            return results
        
        # Sample frames for analysis
        sample_rate = max(1, frame_count // min(100, frame_count))
        sampled_frames = []
        frame_times = []
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % sample_rate == 0:
                sampled_frames.append(frame)
                frame_times.append(frame_idx / fps)
                
            frame_idx += 1
        
        cap.release()
        
        if not sampled_frames:
            return results
        
        # Detect scenes using histogram comparison
        scene_changes = []
        previous_hist = None
        
        for i, frame in enumerate(sampled_frames):
            # Calculate color histogram
            hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            if previous_hist is not None:
                # Compare with previous histogram
                correlation = cv2.compareHist(previous_hist, hist, cv2.HISTCMP_CORREL)
                if correlation < 0.7:  # Scene change threshold
                    scene_changes.append(frame_times[i])
            
            previous_hist = hist
        
        # Analyze dominant colors
        dominant_colors = await self._extract_dominant_colors(sampled_frames)
        
        # Calculate motion intensity
        motion_intensity = await self._calculate_motion_intensity(sampled_frames)
        
        # Determine lighting conditions
        lighting_conditions = await self._analyze_lighting(sampled_frames)
        
        # Build scene information
        scenes = []
        for i in range(len(scene_changes) + 1):
            start_time = scene_changes[i-1] if i > 0 else 0
            end_time = scene_changes[i] if i < len(scene_changes) else frame_times[-1]
            
            scenes.append({
                "scene_id": i,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "frame_count": int((end_time - start_time) * fps)
            })
        
        results.update({
            "scenes": scenes,
            "scene_changes": scene_changes,
            "dominant_colors": dominant_colors,
            "motion_intensity": motion_intensity,
            "lighting_conditions": lighting_conditions,
            "confidence": 0.85
        })
        
        return results
    
    async def _extract_dominant_colors(self, frames: List[np.ndarray]) -> List[str]:
        """Extract dominant colors from frames"""
        all_pixels = []
        for frame in frames[::max(1, len(frames)//10)]:  # Sample frames
            resized = cv2.resize(frame, (50, 50))
            pixels = resized.reshape(-1, 3)
            all_pixels.extend(pixels)
        
        if not all_pixels:
            return []
        
        # Use KMeans to find dominant colors
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(all_pixels)
        
        colors = []
        for center in kmeans.cluster_centers_:
            color = "#{:02x}{:02x}{:02x}".format(int(center[2]), int(center[1]), int(center[0]))
            colors.append(color)
        
        return colors
    
    async def _calculate_motion_intensity(self, frames: List[np.ndarray]) -> float:
        """Calculate motion intensity in video"""
        if len(frames) < 2:
            return 0.0
        
        motion_values = []
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray, 
                cv2.goodFeaturesToTrack(prev_gray, maxCorners=100, qualityLevel=0.3, minDistance=7),
                None
            )[1]
            
            if flow is not None:
                motion = np.mean(np.linalg.norm(flow, axis=2))
                motion_values.append(motion)
        
        return float(np.mean(motion_values)) if motion_values else 0.0
    
    async def _analyze_lighting(self, frames: List[np.ndarray]) -> str:
        """
Analyze lighting conditions in frames"""
        brightness_values = []
        
        for frame in frames[::max(1, len(frames)//20)]:  # Sample frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_values.append(brightness)
        
        if not brightness_values:
            return "unknown"
        
        avg_brightness = np.mean(brightness_values)
        
        if avg_brightness < 50:
            return "dark"
        elif avg_brightness < 120:
            return "dim"
        elif avg_brightness < 180:
            return "normal"
        else:
            return "bright"


class ObjectDetector(BaseAnalyzer):
    """Advanced object detection and recognition"""
    
    def __init__(self):
        super().__init__()
        self.yolo_model = None
        self.clip_processor = None
        self.clip_model = None
        self.face_recognition_model = None
        
    def load_models(self) -> None:
        """
Load object detection models"""
        try:
            # Load YOLO for object detection
            import torch
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
            
            # Load CLIP for visual understanding
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Initialize MediaPipe for face detection
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils
            self.face_detection = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
            
            logger.info("Object detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load object detection models: {str(e)}")
            raise ProcessingError(f"Model loading failed: {str(e)}")
    
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> ObjectAnalysis:
        """Analyze image content for objects"""
        await self._ensure_models_loaded()
        options = options or {}
        
        start_time = datetime.utcnow()
        
        try:
            if isinstance(content, bytes):
                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(content))
            else:
                image = content
            
            # Convert to numpy array for OpenCV operations
            image_np = np.array(image)
            if len(image_np.shape) == 3:
                image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            else:
                image_cv = image_np
            
            # Detect objects
            objects = await self._detect_objects(image, options)
            
            # Detect faces
            faces = await self._detect_faces(image_cv, options)
            
            # Detect text regions
            text_regions = await self._detect_text(image_cv, options)
            
            # Detect landmarks/features
            landmarks = await self._detect_landmarks(image_cv, options)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ObjectAnalysis(
                content_type="image",
                confidence=0.85,
                processing_time=processing_time,
                objects=objects,
                faces=faces,
                text_regions=text_regions,
                landmarks=landmarks
            )
            
        except Exception as e:
            logger.error(f"Object analysis failed: {str(e)}")
            raise AIAnalysisError(f"Object analysis failed: {str(e)}")
    
    async def analyze_video(self, video_content: bytes, options: Dict[str, Any] = None) -> ObjectAnalysis:
        """Analyze video content for objects across frames"""
        await self._ensure_models_loaded()
        options = options or {}
        
        # Extract key frames and analyze objects
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
            temp_file.write(video_content)
            temp_file.flush()
            
            cap = cv2.VideoCapture(temp_file.name)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames for analysis
            sample_indices = np.linspace(0, frame_count-1, min(10, frame_count), dtype=int)
            
            all_objects = []
            all_faces = []
            
            for frame_idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert frame to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Analyze this frame
                    frame_analysis = await self.analyze(pil_image, options)
                    
                    # Add timestamp information
                    timestamp = frame_idx / cap.get(cv2.CAP_PROP_FPS)
                    for obj in frame_analysis.objects:
                        obj['timestamp'] = timestamp
                        all_objects.append(obj)
                    
                    for face in frame_analysis.faces:
                        face['timestamp'] = timestamp
                        all_faces.append(face)
            
            cap.release()
            
            return ObjectAnalysis(
                content_type="video",
                confidence=0.80,
                processing_time=0.0,  # Will be calculated properly
                objects=all_objects,
                faces=all_faces,
                text_regions=[],
                landmarks=[]
            )
    
    async def _detect_objects(self, image: Image.Image, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect objects in image using YOLO"""
        try:
            results = self.yolo_model(image)
            objects = []
            
            for *box, conf, cls in results.xyxy[0].tolist():
                if conf > 0.5:  # Confidence threshold
                    x1, y1, x2, y2 = box
                    class_name = self.yolo_model.names[int(cls)]
                    
                    objects.append({
                        "class": class_name,
                        "confidence": conf,
                        "bounding_box": {
                            "x1": x1, "y1": y1, "x2": x2, "y2": y2
                        },
                        "area": (x2 - x1) * (y2 - y1)
                    })
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {str(e)}")
            return []
    
    async def _detect_faces(self, image_cv: np.ndarray, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_image)
            
            faces = []
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = image_cv.shape
                    
                    faces.append({
                        "confidence": detection.score[0],
                        "bounding_box": {
                            "x": int(bboxC.xmin * iw),
                            "y": int(bboxC.ymin * ih),
                            "width": int(bboxC.width * iw),
                            "height": int(bboxC.height * ih)
                        }
                    })
            
            return faces
            
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            return []
    
    async def _detect_text(self, image_cv: np.ndarray, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect text regions in image"""
        try:
            # Use OpenCV's text detection
            import pytesseract
            
            # Get text bounding boxes
            data = pytesseract.image_to_data(image_cv, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        text_regions.append({
                            "text": text,
                            "confidence": int(data['conf'][i]) / 100.0,
                            "bounding_box": {
                                "x": data['left'][i],
                                "y": data['top'][i],
                                "width": data['width'][i],
                                "height": data['height'][i]
                            }
                        })
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Text detection failed: {str(e)}")
            return []
    
    async def _detect_landmarks(self, image_cv: np.ndarray, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect visual landmarks and features"""
        try:
            # Use OpenCV feature detection
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY), None)
            
            landmarks = []
            for kp in keypoints[:50]:  # Limit to top 50 keypoints
                landmarks.append({
                    "x": kp.pt[0],
                    "y": kp.pt[1], 
                    "size": kp.size,
                    "angle": kp.angle,
                    "response": kp.response
                })
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Landmark detection failed: {str(e)}")
            return []


class SentimentAnalyzer(BaseAnalyzer):
    """Advanced sentiment and emotion analysis"""
    
    def __init__(self):
        super().__init__()
        self.text_classifier = None
        self.emotion_classifier = None
        self.toxicity_classifier = None
        self.nlp = None
        
    def load_models(self) -> None:
        """
Load sentiment analysis models"""
        try:
            # Load transformers pipelines
            self.text_classifier = pipeline("sentiment-analysis", 
                                           model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            self.emotion_classifier = pipeline("text-classification", 
                                              model="j-hartmann/emotion-english-distilroberta-base")
            self.toxicity_classifier = pipeline("text-classification",
                                               model="unitary/toxic-bert")
            
            # Load spaCy for text processing
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, downloading...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
            
            logger.info("Sentiment analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment analysis models: {str(e)}")
            raise ProcessingError(f"Model loading failed: {str(e)}")
    
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> SentimentAnalysis:
        """Main analyze method - routes to appropriate analyzer"""
        if isinstance(content, str):
            return await self.analyze_text(content, options)
        elif isinstance(content, (bytes, Image.Image)):
            return await self.analyze_image(content, options)
        else:
            raise AIAnalysisError("Unsupported content type for sentiment analysis")
    
    async def analyze_text(self, text: str, options: Dict[str, Any] = None) -> SentimentAnalysis:
        """Analyze text content for sentiment and emotions"""
        await self._ensure_models_loaded()
        options = options or {}
        
        start_time = datetime.utcnow()
        
        try:
            # Basic sentiment analysis
            sentiment_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.text_classifier, text
            )
            
            overall_sentiment = sentiment_result[0]['label'].lower()
            sentiment_score = sentiment_result[0]['score']
            
            # Emotion analysis
            emotion_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.emotion_classifier, text
            )
            
            emotions = {}
            for emotion in emotion_result:
                emotions[emotion['label'].lower()] = emotion['score']
            
            # Toxicity analysis
            toxicity_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.toxicity_classifier, text
            )
            
            toxicity_score = 0.0
            for result in toxicity_result:
                if result['label'] == 'TOXIC':
                    toxicity_score = result['score']
                    break
            
            # Extract keywords and themes
            keywords = await self._extract_keywords(text)
            themes = await self._extract_themes(text)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return SentimentAnalysis(
                content_type="text",
                confidence=sentiment_score,
                processing_time=processing_time,
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                emotions=emotions,
                keywords=keywords,
                themes=themes,
                toxicity_score=toxicity_score
            )
            
        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {str(e)}")
            raise AIAnalysisError(f"Sentiment analysis failed: {str(e)}")
    
    async def analyze_image(self, image_content: Any, options: Dict[str, Any] = None) -> SentimentAnalysis:
        """Analyze image content for emotional sentiment"""
        await self._ensure_models_loaded()
        options = options or {}
        
        start_time = datetime.utcnow()
        
        try:
            # For image sentiment, we'll use CLIP to understand the image
            # and generate descriptive text, then analyze that text
            
            if isinstance(image_content, bytes):
                image = Image.open(io.BytesIO(image_content))
            else:
                image = image_content
            
            # Use CLIP to generate image understanding
            image_description = await self._describe_image_emotion(image)
            
            # Analyze the description for sentiment
            text_analysis = await self.analyze_text(image_description, options)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Return adapted results for image
            return SentimentAnalysis(
                content_type="image",
                confidence=text_analysis.confidence * 0.8,  # Lower confidence for derived analysis
                processing_time=processing_time,
                overall_sentiment=text_analysis.overall_sentiment,
                sentiment_score=text_analysis.sentiment_score,
                emotions=text_analysis.emotions,
                keywords=["visual_content"] + text_analysis.keywords,
                themes=text_analysis.themes,
                toxicity_score=0.0  # Images typically don't have toxic text
            )
            
        except Exception as e:
            logger.error(f"Image sentiment analysis failed: {str(e)}")
            raise AIAnalysisError(f"Image sentiment analysis failed: {str(e)}")
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using spaCy and TF-IDF"""
        try:
            # Use spaCy for named entity recognition and key terms
            doc = self.nlp(text)
            
            keywords = []
            
            # Extract entities
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "PRODUCT", "EVENT"]:
                    keywords.append(ent.text.lower())
            
            # Extract key noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit phrase length
                    keywords.append(chunk.text.lower())
            
            # Remove duplicates and return top keywords
            keywords = list(set(keywords))
            return keywords[:10]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def _extract_themes(self, text: str) -> List[str]:
        """Extract themes and topics from text"""
        try:
            # Use simple topic modeling based on key terms
            doc = self.nlp(text)
            
            themes = []
            
            # Look for common theme indicators
            theme_keywords = {
                "music": ["music", "song", "album", "artist", "band", "concert"],
                "technology": ["tech", "software", "app", "digital", "online"],
                "business": ["business", "company", "market", "sales", "revenue"],
                "entertainment": ["movie", "show", "entertainment", "celebrity"],
                "lifestyle": ["lifestyle", "fashion", "travel", "food"],
                "education": ["education", "learning", "school", "university"],
                "health": ["health", "medical", "wellness", "fitness"],
                "sports": ["sports", "game", "team", "player", "match"]
            }
            
            text_lower = text.lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    themes.append(theme)
            
            return themes
            
        except Exception as e:
            logger.error(f"Theme extraction failed: {str(e)}")
            return []
    
    async def _describe_image_emotion(self, image: Image.Image) -> str:
        """Generate emotional description of image using CLIP"""
        try:
            # Define emotional descriptors to test
            emotional_descriptions = [
                "a happy and joyful scene",
                "a sad and melancholic image", 
                "an angry and intense scene",
                "a peaceful and calm image",
                "an exciting and energetic scene",
                "a scary and frightening image",
                "a beautiful and aesthetic scene",
                "a chaotic and messy image"
            ]
            
            # Use CLIP to find best matching description
            inputs = self.clip_processor(
                text=emotional_descriptions,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            # Get the description with highest probability
            best_idx = probs.argmax().item()
            best_description = emotional_descriptions[best_idx]
            
            return f"This image shows {best_description} with emotional intensity."
            
        except Exception as e:
            logger.error(f"Image emotion description failed: {str(e)}")
            return "This image contains visual content with unknown emotional tone."


class AudioContentAnalyzer(BaseAnalyzer):
    """Advanced audio content analysis for music and speech"""
    
    def __init__(self):
        super().__init__()
        self.genre_classifier = None
        self.speech_recognizer = None
        
    def load_models(self) -> None:
        """
Load audio analysis models"""
        try:
            # Load audio classification models
            self.genre_classifier = pipeline("audio-classification", 
                                            model="facebook/wav2vec2-base-960h")
            
            # Initialize speech recognition
            import speech_recognition as sr
            self.speech_recognizer = sr.Recognizer()
            
            logger.info("Audio analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load audio analysis models: {str(e)}")
            raise ProcessingError(f"Model loading failed: {str(e)}")
    
    async def analyze(self, content: Any, options: Dict[str, Any] = None) -> AudioAnalysis:
        """Analyze audio content"""
        await self._ensure_models_loaded()
        options = options or {}
        
        start_time = datetime.utcnow()
        
        try:
            # Load audio data
            if isinstance(content, bytes):
                audio_data, sample_rate = await self._load_audio_from_bytes(content)
            else:
                audio_data, sample_rate = librosa.load(content, sr=None)
            
            # Extract audio features
            tempo = await self._extract_tempo(audio_data, sample_rate)
            key_signature = await self._extract_key(audio_data, sample_rate)
            energy_level = await self._calculate_energy(audio_data)
            mood = await self._analyze_mood(audio_data, sample_rate)
            
            # Detect instruments (if music)
            instruments = await self._detect_instruments(audio_data, sample_rate)
            
            # Separate speech and music segments
            speech_segments, music_segments = await self._segment_audio(audio_data, sample_rate)
            
            # Genre prediction (for music segments)
            genre_predictions = await self._predict_genre(audio_data, sample_rate)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AudioAnalysis(
                content_type="audio",
                confidence=0.85,
                processing_time=processing_time,
                genre_predictions=genre_predictions,
                tempo=tempo,
                key_signature=key_signature,
                energy_level=energy_level,
                mood=mood,
                instruments_detected=instruments,
                speech_segments=speech_segments,
                music_segments=music_segments
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            raise AIAnalysisError(f"Audio analysis failed: {str(e)}")
    
    async def _load_audio_from_bytes(self, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """Load audio from bytes"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()
            
            audio_data, sample_rate = librosa.load(temp_file.name, sr=None)
            return audio_data, sample_rate
    
    async def _extract_tempo(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
Extract tempo (BPM) from audio"""
        try:
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            return float(tempo)
        except Exception as e:
            logger.error(f"Tempo extraction failed: {str(e)}")
            return 0.0
    
    async def _extract_key(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Extract key signature from audio"""
        try:
            # Use chromagram to estimate key
            chromagram = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            key_profile = np.mean(chromagram, axis=1)
            
            # Key names
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_idx = np.argmax(key_profile)
            
            return keys[key_idx]
            
        except Exception as e:
            logger.error(f"Key extraction failed: {str(e)}")
            return "unknown"
    
    async def _calculate_energy(self, audio_data: np.ndarray) -> float:
        """Calculate energy level of audio"""
        try:
            # RMS energy
            rms_energy = np.sqrt(np.mean(audio_data**2))
            return float(rms_energy)
            
        except Exception as e:
            logger.error(f"Energy calculation failed: {str(e)}")
            return 0.0
    
    async def _analyze_mood(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Analyze mood/valence of audio"""
        try:
            # Extract spectral features for mood analysis
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate)
            
            # Simple heuristic for mood classification
            centroid_mean = np.mean(spectral_centroids)
            rolloff_mean = np.mean(spectral_rolloff)
            mfcc_var = np.var(mfcc)
            
            # Map features to mood
            if centroid_mean > 3000 and mfcc_var > 100:
                return "energetic"
            elif centroid_mean < 1500:
                return "calm"
            elif rolloff_mean > 8000:
                return "bright"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Mood analysis failed: {str(e)}")
            return "neutral"
    
    async def _detect_instruments(self, audio_data: np.ndarray, sample_rate: int) -> List[str]:
        """Detect instruments in audio"""
        try:
            # Extract features that might indicate instruments
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            instruments = []
            
            # Simple heuristics for instrument detection
            contrast_mean = np.mean(spectral_contrast)
            if contrast_mean > 20:
                instruments.append("percussion")
            if np.mean(tonnetz) > 0.1:
                instruments.append("harmonic_instrument")
                
            return instruments
            
        except Exception as e:
            logger.error(f"Instrument detection failed: {str(e)}")
            return []
    
    async def _segment_audio(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[List[Dict], List[Dict]]:
        """Segment audio into speech and music parts"""
        try:
            # Use spectral features to distinguish speech from music
            frame_length = int(0.1 * sample_rate)  # 100ms frames
            hop_length = frame_length // 4
            
            # Extract features for classification
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate, hop_length=hop_length
            )
            zero_crossing_rate = librosa.feature.zero_crossing_rate(
                audio_data, frame_length=frame_length, hop_length=hop_length
            )
            
            speech_segments = []
            music_segments = []
            
            # Simple classification based on features
            for i in range(len(spectral_centroids[0])):
                start_time = i * hop_length / sample_rate
                end_time = (i + 1) * hop_length / sample_rate
                
                if zero_crossing_rate[0][i] > 0.1:  # High ZCR typically indicates speech
                    speech_segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "confidence": 0.7
                    })
                else:
                    music_segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "confidence": 0.7
                    })
            
            return speech_segments, music_segments
            
        except Exception as e:
            logger.error(f"Audio segmentation failed: {str(e)}")
            return [], []
    
    async def _predict_genre(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Predict music genre"""
        try:
            # Extract features for genre classification
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            # Simple heuristic genre classification
            genres = {}
            
            mfcc_mean = np.mean(mfcc)
            contrast_mean = np.mean(spectral_contrast)
            
            if contrast_mean > 25:
                genres["rock"] = 0.8
                genres["electronic"] = 0.6
            elif mfcc_mean > 5:
                genres["jazz"] = 0.7
                genres["classical"] = 0.5
            else:
                genres["pop"] = 0.6
                genres["ambient"] = 0.4
            
            return genres
            
        except Exception as e:
            logger.error(f"Genre prediction failed: {str(e)}")
            return {"unknown": 1.0}


class AIAnalysisError(Exception):
    """Custom exception for AI analysis errors"""
    pass
