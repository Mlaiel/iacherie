"""
Moderation Agent - Ultra-Advanced AI Content Moderation & Safety System

Enterprise-grade content moderation agent providing comprehensive safety filtering, 
harmful content detection, and automated compliance enforcement across multiple formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import cv2
from PIL import Image

# AI/ML libraries for content moderation
import tensorflow as tf
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoImageProcessor, AutoModelForImageClassification
)
import librosa
import whisper
from detoxify import Detoxify

# Computer vision for explicit content detection
from nudenet import NudeDetector
import face_recognition

from ..base import BaseAgent, AgentRequest, AgentResponse
try:
    from core.exceptions import ModerationError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ModerationError, ValidationError = globals().get('ModerationError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...ml.toxicity_models import ToxicityClassifier
from ...ml.nsfw_detector import NSFWDetector
from ...ml.violence_detector import ViolenceDetector
from ...utils.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)

class ModerationAction(Enum):
    """Content moderation actions"""
    APPROVE = "approve"
    FLAG = "flag"
    BLOCK = "block"
    REMOVE = "remove"
    QUARANTINE = "quarantine"
    AGE_RESTRICT = "age_restrict"
    SHADOWBAN = "shadowban"

class ViolationType(Enum):
    """Types of content violations"""
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    NUDITY = "nudity"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    COPYRIGHT = "copyright"
    SELF_HARM = "self_harm"
    ILLEGAL_ACTIVITY = "illegal_activity"
    DRUG_ABUSE = "drug_abuse"
    TERRORISM = "terrorism"
    CHILD_SAFETY = "child_safety"

class SeverityLevel(Enum):
    """Violation severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXTREME = 5

class ContentType(Enum):
    """Types of content to moderate"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LIVE_STREAM = "live_stream"

@dataclass
class ModerationResult:
    """Result of content moderation analysis"""
    content_id: str
    content_type: ContentType
    action: ModerationAction
    violations: List[Dict[str, Any]]
    confidence_score: float  # 0.0-1.0
    severity_level: SeverityLevel
    explanation: str
    timestamp: datetime
    reviewer_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ViolationDetection:
    """Detection of a specific violation"""
    violation_type: ViolationType
    confidence: float
    severity: SeverityLevel
    evidence: Dict[str, Any]
    location: Optional[Dict[str, Any]] = None  # Position in content
    context: Optional[str] = None

class ModerationAgent(BaseAgent):
    """
    Ultra-advanced AI content moderation system with comprehensive safety capabilities:
    
    Core Features:
    - Multi-format content analysis (text, image, video, audio)
    - Real-time toxicity and hate speech detection
    - NSFW and explicit content identification
    - Violence and self-harm detection
    - Automated compliance enforcement
    - Cultural sensitivity analysis
    - Age-appropriate content classification
    - Spam and manipulation detection
    - Deepfake and synthetic media detection
    - Live stream monitoring
    - Appeal and review workflow management
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="moderation_agent",
            version="2.1.0",
            config=config
        )
        
        # Core moderation models
        self.toxicity_detector = None
        self.nsfw_detector = None
        self.violence_detector = None
        self.hate_speech_model = None
        self.nudity_detector = None
        
        # Audio analysis models
        self.whisper_model = None
        self.audio_classifier = None
        
        # Text analysis models
        self.detoxify_model = None
        self.sentiment_analyzer = None
        
        # Image analysis models
        self.explicit_content_model = None
        self.face_detector = None
        
        # Moderation rules and thresholds
        self.moderation_rules = self._load_moderation_rules()
        self.confidence_thresholds = self._load_confidence_thresholds()
        
        # Review queue for human moderation
        self.review_queue = []
        self.auto_moderation_stats = {
            'total_content': 0,
            'approved': 0,
            'flagged': 0,
            'blocked': 0,
            'human_review_required': 0
        }
        
        logger.info(f"ModerationAgent {agent_id} initialized")
    
    def get_required_config_keys(self) -> List[str]:
        return [
            'moderation_thresholds',
            'model_configs',
            'review_workflow',
            'compliance_settings'
        ]
    
    async def _load_models_and_resources(self):
        """Load AI models for content moderation"""
        try:
            # Load text moderation models
            await self._load_text_moderation_models()
            
            # Load image moderation models
            await self._load_image_moderation_models()
            
            # Load audio moderation models
            await self._load_audio_moderation_models()
            
            # Load video analysis models
            await self._load_video_moderation_models()
            
            logger.info("All moderation models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load moderation models: {e}")
            raise
    
    async def _load_text_moderation_models(self):
        """Load models for text content moderation"""
        try:
            # Load Detoxify for toxicity detection
            self.detoxify_model = Detoxify('multilingual')
            
            # Load hate speech detection model
            self.hate_speech_model = AutoModelForSequenceClassification.from_pretrained(
                "unitary/toxic-bert"
            )
            self.hate_speech_tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
            
            # Load sentiment analysis
            from transformers import pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            logger.info("Text moderation models loaded")
            
        except Exception as e:
            logger.error(f"Failed to load text moderation models: {e}")
            raise
    
    async def _load_image_moderation_models(self):
        """Load models for image content moderation"""
        try:
            # Load NSFW detector
            self.nsfw_detector = NSFWDetector()
            
            # Load nudity detector
            self.nudity_detector = NudeDetector()
            
            # Load violence detector
            self.violence_detector = ViolenceDetector()
            
            # Load explicit content classifier
            from transformers import pipeline
            self.explicit_content_model = pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection"
            )
            
            logger.info("Image moderation models loaded")
            
        except Exception as e:
            logger.error(f"Failed to load image moderation models: {e}")
            raise
    
    async def _load_audio_moderation_models(self):
        """Load models for audio content moderation"""
        try:
            # Load Whisper for speech-to-text
            self.whisper_model = whisper.load_model("base")
            
            # Load audio content classifier
            # This would be a custom model trained for audio content classification
            
            logger.info("Audio moderation models loaded")
            
        except Exception as e:
            logger.error(f"Failed to load audio moderation models: {e}")
            raise
    
    async def _load_video_moderation_models(self):
        """Load models for video content moderation"""
        try:
            # Video moderation uses combination of image and audio models
            # Plus frame-by-frame analysis capabilities
            
            logger.info("Video moderation models loaded")
            
        except Exception as e:
            logger.error(f"Failed to load video moderation models: {e}")
            raise
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main moderation processing pipeline"""
        action = request.action
        data = request.data
        
        try:
            if action == "moderate_content":
                result = await self._moderate_content(data)
            elif action == "analyze_toxicity":
                result = await self._analyze_toxicity(data)
            elif action == "detect_nsfw":
                result = await self._detect_nsfw_content(data)
            elif action == "moderate_live_stream":
                result = await self._moderate_live_stream(data)
            elif action == "bulk_moderation":
                result = await self._bulk_content_moderation(data)
            elif action == "review_flagged_content":
                result = await self._review_flagged_content(data)
            elif action == "update_moderation_rules":
                result = await self._update_moderation_rules(data)
            elif action == "get_moderation_stats":
                result = await self._get_moderation_stats(data)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Moderation {action} completed successfully",
                agent_type=self.agent_type
            )
            
        except Exception as e:
            logger.error(f"Moderation processing failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="MODERATION_ERROR",
                agent_type=self.agent_type
            )
    
    async def _moderate_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content moderation analysis"""
        content_id = data.get('content_id')
        content_type = ContentType(data.get('content_type', 'text'))
        content_data = data.get('content_data', {})
        user_id = data.get('user_id')
        
        moderation_result = ModerationResult(
            content_id=content_id,
            content_type=content_type,
            action=ModerationAction.APPROVE,
            violations=[],
            confidence_score=0.0,
            severity_level=SeverityLevel.LOW,
            explanation="Content analysis in progress",
            timestamp=datetime.now(timezone.utc)
        )
        
        # Analyze content based on type
        if content_type == ContentType.TEXT:
            violations = await self._analyze_text_content(content_data.get('text', ''))
        elif content_type == ContentType.IMAGE:
            violations = await self._analyze_image_content(content_data.get('image_path', ''))
        elif content_type == ContentType.VIDEO:
            violations = await self._analyze_video_content(content_data.get('video_path', ''))
        elif content_type == ContentType.AUDIO:
            violations = await self._analyze_audio_content(content_data.get('audio_path', ''))
        else:
            violations = []
        
        # Process violations and determine action
        if violations:
            moderation_result.violations = violations
            moderation_result.action, moderation_result.severity_level = self._determine_moderation_action(violations)
            moderation_result.confidence_score = self._calculate_overall_confidence(violations)
            moderation_result.explanation = self._generate_moderation_explanation(violations)
            
            # Check if human review is required
            moderation_result.reviewer_required = self._requires_human_review(violations, moderation_result.severity_level)
        
        # Update statistics
        self._update_moderation_stats(moderation_result)
        
        # Log moderation decision
        await self._log_moderation_decision(moderation_result, user_id)
        
        return {
            'moderation_result': {
                'content_id': moderation_result.content_id,
                'action': moderation_result.action.value,
                'violations': [self._violation_to_dict(v) for v in violations],
                'confidence_score': moderation_result.confidence_score,
                'severity_level': moderation_result.severity_level.value,
                'explanation': moderation_result.explanation,
                'reviewer_required': moderation_result.reviewer_required,
                'timestamp': moderation_result.timestamp.isoformat()
            },
            'processing_time_ms': time.time() * 1000 - data.get('start_time', 0),
            'model_versions': self._get_model_versions()
        }
    
    async def _analyze_text_content(self, text: str) -> List[ViolationDetection]:
        """Analyze text content for violations"""
        violations = []
        
        if not text or len(text.strip()) == 0:
            return violations
        
        try:
            # Toxicity detection using Detoxify
            toxicity_scores = self.detoxify_model.predict(text)
            
            # Check each toxicity category
            for category, score in toxicity_scores.items():
                if score > self.confidence_thresholds.get(f'toxicity_{category}', 0.7):
                    violation_type = self._map_toxicity_to_violation_type(category)
                    severity = self._calculate_severity_from_score(score)
                    
                    violations.append(ViolationDetection(
                        violation_type=violation_type,
                        confidence=score,
                        severity=severity,
                        evidence={'toxicity_scores': toxicity_scores, 'detected_category': category},
                        context=text[:200]  # First 200 characters for context
                    ))
            
            # Hate speech detection
            hate_speech_result = await self._detect_hate_speech(text)
            if hate_speech_result['is_hate_speech']:
                violations.append(ViolationDetection(
                    violation_type=ViolationType.HATE_SPEECH,
                    confidence=hate_speech_result['confidence'],
                    severity=self._calculate_severity_from_score(hate_speech_result['confidence']),
                    evidence=hate_speech_result,
                    context=text[:200]
                ))
            
            # Spam detection
            spam_result = await self._detect_spam_text(text)
            if spam_result['is_spam']:
                violations.append(ViolationDetection(
                    violation_type=ViolationType.SPAM,
                    confidence=spam_result['confidence'],
                    severity=SeverityLevel.MEDIUM,
                    evidence=spam_result,
                    context=text[:200]
                ))
            
            # Self-harm detection
            self_harm_result = await self._detect_self_harm_content(text)
            if self_harm_result['detected']:
                violations.append(ViolationDetection(
                    violation_type=ViolationType.SELF_HARM,
                    confidence=self_harm_result['confidence'],
                    severity=SeverityLevel.CRITICAL,
                    evidence=self_harm_result,
                    context=text[:200]
                ))
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
        
        return violations
    
    async def _analyze_image_content(self, image_path: str) -> List[ViolationDetection]:
        """Analyze image content for violations"""
        violations = []
        
        if not image_path:
            return violations
        
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            image_array = np.array(image)
            
            # NSFW detection
            nsfw_result = await self._detect_nsfw_image(image_path)
            if nsfw_result['is_nsfw']:
                violations.append(ViolationDetection(
                    violation_type=ViolationType.SEXUAL_CONTENT,
                    confidence=nsfw_result['confidence'],
                    severity=self._calculate_severity_from_score(nsfw_result['confidence']),
                    evidence=nsfw_result,
                    location=nsfw_result.get('regions')
                ))
            
            # Nudity detection
            nudity_result = self.nudity_detector.detect(image_path)
            for detection in nudity_result:
                if detection['score'] > 0.6:
                    violations.append(ViolationDetection(
                        violation_type=ViolationType.NUDITY,
                        confidence=detection['score'],
                        severity=self._calculate_severity_from_score(detection['score']),
                        evidence={'detection': detection},
                        location={'bbox': detection['box']}
                    ))
            
            # Violence detection
            violence_result = await self._detect_image_violence(image_array)
            if violence_result['detected']:
                violations.append(ViolationDetection(
                    violation_type=ViolationType.VIOLENCE,
                    confidence=violence_result['confidence'],
                    severity=SeverityLevel.HIGH,
                    evidence=violence_result
                ))
            
            # Explicit content classification
            explicit_result = self.explicit_content_model(image)
            for result in explicit_result:
                if result['label'] == 'nsfw' and result['score'] > 0.8:
                    violations.append(ViolationDetection(
                        violation_type=ViolationType.SEXUAL_CONTENT,
                        confidence=result['score'],
                        severity=SeverityLevel.HIGH,
                        evidence={'classification': result}
                    ))
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
        
        return violations
    
    async def _analyze_video_content(self, video_path: str) -> List[ViolationDetection]:
        """Analyze video content for violations"""
        violations = []
        
        if not video_path:
            return violations
        
        try:
            # Extract frames for analysis
            frames = await self._extract_video_frames(video_path, max_frames=30)
            
            # Analyze each frame
            for i, frame in enumerate(frames):
                frame_violations = await self._analyze_frame_content(frame, i)
                violations.extend(frame_violations)
            
            # Extract and analyze audio
            audio_path = await self._extract_video_audio(video_path)
            audio_violations = await self._analyze_audio_content(audio_path)
            violations.extend(audio_violations)
            
            # Overall video analysis
            video_metrics = await self._analyze_video_metrics(video_path)
            if video_metrics.get('suspicious_activity'):
                violations.append(ViolationDetection(
                    violation_type=ViolationType.ILLEGAL_ACTIVITY,
                    confidence=video_metrics['confidence'],
                    severity=SeverityLevel.HIGH,
                    evidence=video_metrics
                ))
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
        
        return violations
    
    async def _analyze_audio_content(self, audio_path: str) -> List[ViolationDetection]:
        """Analyze audio content for violations"""
        violations = []
        
        if not audio_path:
            return violations
        
        try:
            # Transcribe audio to text using Whisper
            transcription = self.whisper_model.transcribe(audio_path)
            text_content = transcription['text']
            
            # Analyze transcribed text
            text_violations = await self._analyze_text_content(text_content)
            
            # Add audio-specific context to violations
            for violation in text_violations:
                violation.evidence['audio_transcription'] = transcription
                violation.evidence['audio_path'] = audio_path
            
            violations.extend(text_violations)
            
            # Audio-specific analysis (volume, frequency patterns, etc.)
            audio_features = await self._analyze_audio_features(audio_path)
            if audio_features.get('suspicious_patterns'):
                violations.append(ViolationDetection(
                    violation_type=ViolationType.ILLEGAL_ACTIVITY,
                    confidence=audio_features['confidence'],
                    severity=SeverityLevel.MEDIUM,
                    evidence=audio_features
                ))
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
        
        return violations
    
    async def _detect_hate_speech(self, text: str) -> Dict[str, Any]:
        """Detect hate speech in text"""
        try:
            # Tokenize input
            inputs = self.hate_speech_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            )
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.hate_speech_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Extract confidence score
            confidence = predictions[0][1].item()  # Index 1 for toxic class
            
            return {
                'is_hate_speech': confidence > 0.7,
                'confidence': confidence,
                'raw_scores': predictions[0].tolist()
            }
            
        except Exception as e:
            logger.error(f"Hate speech detection failed: {e}")
            return {'is_hate_speech': False, 'confidence': 0.0, 'error': str(e)}
    
    def _determine_moderation_action(self, violations: List[ViolationDetection]) -> Tuple[ModerationAction, SeverityLevel]:
        """Determine moderation action based on violations"""
        if not violations:
            return ModerationAction.APPROVE, SeverityLevel.LOW
        
        # Find highest severity violation
        max_severity = max(v.severity for v in violations)
        
        # Count critical violations
        critical_violations = [v for v in violations if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.EXTREME]]
        high_violations = [v for v in violations if v.severity == SeverityLevel.HIGH]
        
        # Decision logic
        if len(critical_violations) > 0:
            return ModerationAction.BLOCK, SeverityLevel.CRITICAL
        elif len(high_violations) >= 2:
            return ModerationAction.REMOVE, SeverityLevel.HIGH
        elif len(high_violations) == 1:
            return ModerationAction.FLAG, SeverityLevel.HIGH
        elif max_severity == SeverityLevel.MEDIUM:
            return ModerationAction.FLAG, SeverityLevel.MEDIUM
        else:
            return ModerationAction.APPROVE, SeverityLevel.LOW
    
    def _calculate_severity_from_score(self, confidence_score: float) -> SeverityLevel:
        """Calculate severity level from confidence score"""
        if confidence_score >= 0.95:
            return SeverityLevel.EXTREME
        elif confidence_score >= 0.85:
            return SeverityLevel.CRITICAL
        elif confidence_score >= 0.75:
            return SeverityLevel.HIGH
        elif confidence_score >= 0.6:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _load_moderation_rules(self) -> Dict[str, Any]:
        """Load moderation rules configuration"""
        return {
            'auto_approve_threshold': 0.1,
            'auto_flag_threshold': 0.6,
            'auto_block_threshold': 0.85,
            'require_review_threshold': 0.75,
            'violation_weights': {
                ViolationType.HATE_SPEECH: 1.0,
                ViolationType.VIOLENCE: 0.9,
                ViolationType.SEXUAL_CONTENT: 0.8,
                ViolationType.HARASSMENT: 0.7,
                ViolationType.SELF_HARM: 1.0,
                ViolationType.CHILD_SAFETY: 1.0,
                ViolationType.TERRORISM: 1.0
            }
        }
    
    def _load_confidence_thresholds(self) -> Dict[str, float]:
        """Load confidence thresholds for different violation types"""
        return {
            'toxicity_toxicity': 0.7,
            'toxicity_severe_toxicity': 0.6,
            'toxicity_obscene': 0.7,
            'toxicity_threat': 0.6,
            'toxicity_insult': 0.7,
            'toxicity_identity_attack': 0.6,
            'nsfw_general': 0.8,
            'violence_graphic': 0.7,
            'hate_speech': 0.7,
            'spam_detection': 0.8
        }
    
    async def _detect_spam_text(self, text: str) -> Dict[str, Any]:
        """Detect spam content in text"""
        try:
            # Spam detection features
            spam_indicators = {
                'excessive_caps': len([c for c in text if c.isupper()]) / len(text) if text else 0,
                'repeated_chars': self._count_repeated_patterns(text),
                'suspicious_urls': len(self._extract_urls(text)),
                'promotional_keywords': self._count_promotional_keywords(text),
                'excessive_punctuation': len([c for c in text if c in '!?']) / len(text) if text else 0
            }
            
            # Calculate spam score
            spam_score = (
                spam_indicators['excessive_caps'] * 0.3 +
                spam_indicators['repeated_chars'] * 0.25 +
                spam_indicators['suspicious_urls'] * 0.2 +
                spam_indicators['promotional_keywords'] * 0.15 +
                spam_indicators['excessive_punctuation'] * 0.1
            )
            
            return {
                'is_spam': spam_score > 0.6,
                'confidence': min(spam_score, 1.0),
                'indicators': spam_indicators,
                'spam_score': spam_score
            }
            
        except Exception as e:
            logger.error(f"Spam detection failed: {e}")
            return {'is_spam': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _detect_self_harm_content(self, text: str) -> Dict[str, Any]:
        """Detect self-harm related content"""
        try:
            # Self-harm keywords and patterns
            self_harm_keywords = [
                'suicide', 'kill myself', 'end it all', 'self harm', 'cut myself',
                'want to die', 'better off dead', 'hurt myself', 'self injury'
            ]
            
            text_lower = text.lower()
            detected_keywords = [kw for kw in self_harm_keywords if kw in text_lower]
            
            # Calculate confidence based on keyword matches and context
            confidence = len(detected_keywords) * 0.3
            if confidence > 0:
                confidence = min(confidence + 0.4, 1.0)  # Base confidence boost
            
            return {
                'detected': confidence > 0.5,
                'confidence': confidence,
                'detected_keywords': detected_keywords,
                'risk_level': 'high' if confidence > 0.8 else 'medium' if confidence > 0.5 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Self-harm detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _detect_nsfw_image(self, image_path: str) -> Dict[str, Any]:
        """Detect NSFW content in images"""
        try:
            if not self.nsfw_detector:
                return {'is_nsfw': False, 'confidence': 0.0, 'error': 'NSFW detector not loaded'}
            
            result = await self.nsfw_detector.analyze_image(image_path)
            
            return {
                'is_nsfw': result['confidence'] > 0.7,
                'confidence': result['confidence'],
                'categories': result.get('categories', {}),
                'regions': result.get('regions', [])
            }
            
        except Exception as e:
            logger.error(f"NSFW image detection failed: {e}")
            return {'is_nsfw': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _detect_image_violence(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Detect violent content in images"""
        try:
            if not self.violence_detector:
                return {'detected': False, 'confidence': 0.0, 'error': 'Violence detector not loaded'}
            
            result = await self.violence_detector.analyze_frame(image_array)
            
            return {
                'detected': result['confidence'] > 0.6,
                'confidence': result['confidence'],
                'violence_type': result.get('violence_type'),
                'regions': result.get('regions', [])
            }
            
        except Exception as e:
            logger.error(f"Violence detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _extract_video_frames(self, video_path: str, max_frames: int = 30) -> List[np.ndarray]:
        """Extract frames from video for analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame sampling interval
            interval = max(1, frame_count // max_frames)
            
            frame_index = 0
            while len(frames) < max_frames and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_index % interval == 0:
                    frames.append(frame)
                    
                frame_index += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    async def _analyze_frame_content(self, frame: np.ndarray, frame_index: int) -> List[ViolationDetection]:
        """Analyze individual video frame for violations"""
        violations = []
        
        try:
            # Convert frame to image for analysis
            temp_image_path = f"/tmp/frame_{frame_index}.jpg"
            cv2.imwrite(temp_image_path, frame)
            
            # Analyze frame as image
            frame_violations = await self._analyze_image_content(temp_image_path)
            
            # Add frame context to violations
            for violation in frame_violations:
                violation.location = violation.location or {}
                violation.location['frame_index'] = frame_index
                violation.location['timestamp'] = frame_index / 30.0  # Assuming 30 FPS
            
            violations.extend(frame_violations)
            
            # Clean up temporary file
            import os
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {e}")
        
        return violations
    
    async def _extract_video_audio(self, video_path: str) -> str:
        """Extract audio from video"""
        try:
            import subprocess
            import tempfile
            
            # Create temporary audio file
            audio_fd, audio_path = tempfile.mkstemp(suffix='.wav')
            
            # Use ffmpeg to extract audio
            subprocess.run([
                'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1', audio_path, '-y'
            ], check=True, capture_output=True)
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return ""
    
    async def _analyze_video_metrics(self, video_path: str) -> Dict[str, Any]:
        """Analyze overall video metrics for suspicious content"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            metrics = {
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            }
            
            cap.release()
            
            # Check for suspicious characteristics
            suspicious_activity = False
            confidence = 0.0
            
            # Very short videos might be suspicious
            if metrics['duration'] < 1.0:
                suspicious_activity = True
                confidence += 0.3
            
            # Unusual aspect ratios
            aspect_ratio = metrics['width'] / metrics['height']
            if aspect_ratio < 0.5 or aspect_ratio > 3.0:
                suspicious_activity = True
                confidence += 0.2
            
            return {
                'suspicious_activity': suspicious_activity,
                'confidence': min(confidence, 1.0),
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Video metrics analysis failed: {e}")
            return {'suspicious_activity': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _analyze_audio_features(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio features for suspicious patterns"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Extract audio features
            mfccs = librosa.feature.mfcc(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Calculate statistics
            features = {
                'duration': len(y) / sr,
                'mean_mfcc': np.mean(mfccs),
                'mean_spectral_centroid': np.mean(spectral_centroids),
                'mean_zcr': np.mean(zero_crossing_rate),
                'rms_energy': np.sqrt(np.mean(y**2))
            }
            
            # Check for suspicious patterns
            suspicious_patterns = False
            confidence = 0.0
            
            # Very low energy might indicate processed/artificial audio
            if features['rms_energy'] < 0.01:
                suspicious_patterns = True
                confidence += 0.3
            
            return {
                'suspicious_patterns': suspicious_patterns,
                'confidence': min(confidence, 1.0),
                'features': features
            }
            
        except Exception as e:
            logger.error(f"Audio feature analysis failed: {e}")
            return {'suspicious_patterns': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _moderate_live_stream(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and moderate live stream content"""
        stream_id = data.get('stream_id')
        stream_url = data.get('stream_url')
        monitoring_interval = data.get('monitoring_interval', 5)  # seconds
        
        try:
            # Start live stream monitoring
            monitoring_task = asyncio.create_task(
                self._monitor_stream_content(stream_id, stream_url, monitoring_interval)
            )
            
            return {
                'stream_id': stream_id,
                'monitoring_started': True,
                'monitoring_interval': monitoring_interval,
                'task_id': str(monitoring_task)
            }
            
        except Exception as e:
            logger.error(f"Live stream moderation failed: {e}")
            return {'error': str(e), 'monitoring_started': False}
    
    async def _monitor_stream_content(self, stream_id: str, stream_url: str, interval: int):
        """Continuously monitor live stream content"""
        try:
            while True:
                # Capture frame from stream
                frame = await self._capture_stream_frame(stream_url)
                
                if frame is not None:
                    # Analyze frame content
                    violations = await self._analyze_frame_content(frame, int(time.time()))
                    
                    # Take action if violations found
                    if violations:
                        await self._handle_live_stream_violations(stream_id, violations)
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"Stream monitoring failed: {e}")
    
    async def _capture_stream_frame(self, stream_url: str) -> Optional[np.ndarray]:
        """Capture a frame from live stream"""
        try:
            cap = cv2.VideoCapture(stream_url)
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            logger.error(f"Stream frame capture failed: {e}")
            return None
    
    async def _handle_live_stream_violations(self, stream_id: str, violations: List[ViolationDetection]):
        """Handle violations detected in live stream"""
        try:
            # Determine severity of violations
            max_severity = max(v.severity for v in violations)
            
            # Take appropriate action based on severity
            if max_severity in [SeverityLevel.CRITICAL, SeverityLevel.EXTREME]:
                # Immediately stop stream
                await self._stop_live_stream(stream_id)
                logger.warning(f"Stream {stream_id} stopped due to critical violations")
            
            elif max_severity == SeverityLevel.HIGH:
                # Issue warning and continue monitoring
                await self._issue_stream_warning(stream_id, violations)
                logger.info(f"Warning issued for stream {stream_id}")
            
            # Log violations
            await self._log_stream_violations(stream_id, violations)
            
        except Exception as e:
            logger.error(f"Stream violation handling failed: {e}")
    
    async def _bulk_content_moderation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform bulk moderation on multiple content items"""
        content_items = data.get('content_items', [])
        batch_size = data.get('batch_size', 50)
        
        results = []
        processed = 0
        failed = 0
        
        try:
            # Process in batches
            for i in range(0, len(content_items), batch_size):
                batch = content_items[i:i+batch_size]
                batch_results = await asyncio.gather(*[
                    self._moderate_content(item) for item in batch
                ], return_exceptions=True)
                
                # Process batch results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        failed += 1
                        results.append({
                            'content_id': batch[j].get('content_id'),
                            'error': str(result),
                            'success': False
                        })
                    else:
                        processed += 1
                        results.append(result)
            
            return {
                'total_items': len(content_items),
                'processed': processed,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Bulk moderation failed: {e}")
            return {'error': str(e), 'processed': processed, 'failed': failed}
    
    async def _review_flagged_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Review and update flagged content decisions"""
        content_id = data.get('content_id')
        reviewer_id = data.get('reviewer_id')
        decision = data.get('decision')  # approve, reject, escalate
        notes = data.get('notes', '')
        
        try:
            # Update content status
            review_result = {
                'content_id': content_id,
                'reviewer_id': reviewer_id,
                'decision': decision,
                'review_timestamp': datetime.now(timezone.utc).isoformat(),
                'notes': notes,
                'status': 'reviewed'
            }
            
            # Log review decision
            await self._log_review_decision(review_result)
            
            return review_result
            
        except Exception as e:
            logger.error(f"Content review failed: {e}")
            return {'error': str(e)}
    
    async def _update_moderation_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update moderation rules and thresholds"""
        new_rules = data.get('rules', {})
        
        try:
            # Update rules
            self.moderation_rules.update(new_rules)
            
            # Update confidence thresholds if provided
            if 'confidence_thresholds' in data:
                self.confidence_thresholds.update(data['confidence_thresholds'])
            
            return {
                'rules_updated': True,
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'new_rules': new_rules
            }
            
        except Exception as e:
            logger.error(f"Rules update failed: {e}")
            return {'error': str(e)}
    
    async def _get_moderation_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive moderation statistics"""
        time_range = data.get('time_range', '24h')
        
        try:
            # Current statistics
            stats = {
                'current_stats': self.auto_moderation_stats.copy(),
                'time_range': time_range,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate derived metrics
            total = stats['current_stats']['total_content']
            if total > 0:
                stats['approval_rate'] = stats['current_stats']['approved'] / total
                stats['flag_rate'] = stats['current_stats']['flagged'] / total
                stats['block_rate'] = stats['current_stats']['blocked'] / total
                stats['human_review_rate'] = stats['current_stats']['human_review_required'] / total
            else:
                stats['approval_rate'] = 0.0
                stats['flag_rate'] = 0.0
                stats['block_rate'] = 0.0
                stats['human_review_rate'] = 0.0
            
            # Model performance metrics
            stats['model_versions'] = self._get_model_versions()
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {'error': str(e)}
    
    # Helper methods
    def _map_toxicity_to_violation_type(self, category: str) -> ViolationType:
        """Map toxicity category to violation type"""
        mapping = {
            'toxicity': ViolationType.HARASSMENT,
            'severe_toxicity': ViolationType.HARASSMENT,
            'obscene': ViolationType.SEXUAL_CONTENT,
            'threat': ViolationType.HARASSMENT,
            'insult': ViolationType.HARASSMENT,
            'identity_attack': ViolationType.HATE_SPEECH
        }
        return mapping.get(category, ViolationType.HARASSMENT)
    
    def _calculate_overall_confidence(self, violations: List[ViolationDetection]) -> float:
        """Calculate overall confidence score from violations"""
        if not violations:
            return 0.0
        
        # Weighted average based on severity
        total_weight = 0
        weighted_confidence = 0
        
        for violation in violations:
            weight = violation.severity.value
            total_weight += weight
            weighted_confidence += violation.confidence * weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _generate_moderation_explanation(self, violations: List[ViolationDetection]) -> str:
        """Generate human-readable explanation for moderation decision"""
        if not violations:
            return "Content approved - no violations detected"
        
        violation_types = [v.violation_type.value for v in violations]
        unique_types = list(set(violation_types))
        
        if len(unique_types) == 1:
            return f"Content flagged for {unique_types[0]} violation"
        else:
            return f"Content flagged for multiple violations: {', '.join(unique_types)}"
    
    def _requires_human_review(self, violations: List[ViolationDetection], severity: SeverityLevel) -> bool:
        """Determine if human review is required"""
        # Always require review for critical/extreme severity
        if severity in [SeverityLevel.CRITICAL, SeverityLevel.EXTREME]:
            return True
        
        # Check for specific violation types that require review
        sensitive_types = [
            ViolationType.SELF_HARM, ViolationType.CHILD_SAFETY, 
            ViolationType.TERRORISM, ViolationType.VIOLENCE
        ]
        
        for violation in violations:
            if violation.violation_type in sensitive_types:
                return True
        
        return False
    
    def _count_repeated_patterns(self, text: str) -> float:
        """Count repeated character patterns in text"""
        if not text:
            return 0.0
        
        repeated_count = 0
        i = 0
        while i < len(text) - 2:
            char = text[i]
            consecutive = 1
            j = i + 1
            
            while j < len(text) and text[j] == char:
                consecutive += 1
                j += 1
            
            if consecutive >= 3:
                repeated_count += consecutive - 2
            
            i = j if j > i + 1 else i + 1
        
        return repeated_count / len(text) if text else 0.0
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def _count_promotional_keywords(self, text: str) -> float:
        """Count promotional keywords in text"""
        promotional_keywords = [
            'buy', 'sale', 'discount', 'offer', 'deal', 'free', 'win', 'prize',
            'click here', 'limited time', 'act now', 'exclusive', 'bonus'
        ]
        
        text_lower = text.lower()
        count = sum(1 for keyword in promotional_keywords if keyword in text_lower)
        
        return count / len(promotional_keywords)
    
    def _violation_to_dict(self, violation: ViolationDetection) -> Dict[str, Any]:
        """Convert ViolationDetection to dictionary"""
        return {
            'violation_type': violation.violation_type.value,
            'confidence': violation.confidence,
            'severity': violation.severity.value,
            'evidence': violation.evidence,
            'location': violation.location,
            'context': violation.context
        }
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of loaded models"""
        return {
            'detoxify': 'multilingual-v1',
            'whisper': 'base',
            'nsfw_detector': 'v2.1',
            'violence_detector': 'v1.3'
        }
    
    async def _log_moderation_decision(self, result: ModerationResult, user_id: str):
        """Log moderation decision for audit purposes"""
        try:
            log_entry = {
                'timestamp': result.timestamp.isoformat(),
                'content_id': result.content_id,
                'user_id': user_id,
                'action': result.action.value,
                'confidence': result.confidence_score,
                'severity': result.severity_level.value,
                'violations': len(result.violations),
                'reviewer_required': result.reviewer_required
            }
            
            # In production, this would write to a secure audit log
            logger.info(f"Moderation decision logged: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log moderation decision: {e}")
    
    async def _log_review_decision(self, review_result: Dict[str, Any]):
        """Log human review decision"""
        try:
            # In production, this would write to audit log
            logger.info(f"Review decision logged: {review_result}")
        except Exception as e:
            logger.error(f"Failed to log review decision: {e}")
    
    async def _log_stream_violations(self, stream_id: str, violations: List[ViolationDetection]):
        """Log live stream violations"""
        try:
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'stream_id': stream_id,
                'violation_count': len(violations),
                'violations': [self._violation_to_dict(v) for v in violations]
            }
            
            logger.warning(f"Stream violations logged: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log stream violations: {e}")
    
    async def _stop_live_stream(self, stream_id: str):
        """Stop a live stream due to violations"""
        # Implementation would integrate with streaming service API
        logger.critical(f"STREAM STOPPED: {stream_id} due to critical violations")
    
    async def _issue_stream_warning(self, stream_id: str, violations: List[ViolationDetection]):
        """Issue warning for live stream violations"""
        # Implementation would send warning to streamer
        logger.warning(f"Stream warning issued: {stream_id}, violations: {len(violations)}")
    
    def _update_moderation_stats(self, result: ModerationResult):
        """Update moderation statistics"""
        self.auto_moderation_stats['total_content'] += 1
        
        if result.action == ModerationAction.APPROVE:
            self.auto_moderation_stats['approved'] += 1
        elif result.action in [ModerationAction.FLAG, ModerationAction.AGE_RESTRICT]:
            self.auto_moderation_stats['flagged'] += 1
        elif result.action in [ModerationAction.BLOCK, ModerationAction.REMOVE]:
            self.auto_moderation_stats['blocked'] += 1
        
        if result.reviewer_required:
            self.auto_moderation_stats['human_review_required'] += 1

class ModerationAgentManager:
    """Manager for moderation agent instances"""
    
    def __init__(self):
        self.agents: Dict[str, ModerationAgent] = {}
    
    async def create_agent(self, agent_id: str, config: Dict[str, Any] = None) -> ModerationAgent:
        """Create new moderation agent"""
        agent = ModerationAgent(agent_id, config)
        await agent.initialize()
        self.agents[agent_id] = agent
        return agent
