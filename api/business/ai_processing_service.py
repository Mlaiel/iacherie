"""AI Processing service for IA Influencer Agent platform.

This service handles all AI-powered content analysis, processing, and enhancement
for multi-format content including audio, video, images, and text.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import openai
from PIL import Image
import librosa
import numpy as np
import cv2
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.content import Content
from ..utils.ai_client import AIClient
from ..utils.content_analyzer import ContentAnalyzer
from ..utils.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)
settings = get_settings()

class AIProcessingService:
    """    Comprehensive AI processing service for multi-format content analysis.
    
    Capabilities:
    - Audio: Genre classification, mood analysis, quality assessment
    - Video: Scene detection, object recognition, content moderation
    - Images: Style analysis, quality assessment, content recognition
    - Text: Sentiment analysis, topic modeling, SEO optimization
    """    
    def __init__(self):
        self.ai_client = AIClient()
        self.content_analyzer = ContentAnalyzer()
        self.metadata_extractor = MetadataExtractor()
        openai.api_key = settings.ai.openai_api_key
    
    async def process_content_async(self, content_id: str, file_type: str) -> Dict[str, Any]:
        """        Process content asynchronously with comprehensive AI analysis.
        
        Args:
            content_id: Content unique identifier
            file_type: Type of content (audio, video, image, text)
            
        Returns:
            Processing results and analysis data
        """        try:
            logger.info(f"Starting AI processing for content: {content_id} - Type: {file_type}")
            
            # Get content from database
            db = next(get_db())
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError(f"Content not found: {content_id}")
            
            # Update processing status
            content.ai_processing_status = "processing"
            db.commit()
            
            # Process based on file type
            processing_results = {}
            
            if file_type == "audio":
                processing_results = await self._process_audio_content(content)
            elif file_type == "video":
                processing_results = await self._process_video_content(content)
            elif file_type == "image":
                processing_results = await self._process_image_content(content)
            elif file_type == "text":
                processing_results = await self._process_text_content(content)
            else:
                processing_results = await self._process_generic_content(content)
            
            # Update content with AI results
            content.ai_analysis_results = processing_results
            content.ai_processing_status = "completed"
            content.ai_processed_at = datetime.utcnow()
            
            # Generate AI-powered tags and metadata
            enhanced_metadata = await self._generate_enhanced_metadata(content, processing_results)
            content.ai_enhanced_metadata = enhanced_metadata
            
            # Calculate AI quality score
            quality_score = await self._calculate_quality_score(processing_results, file_type)
            content.ai_quality_score = quality_score
            
            db.commit()
            
            logger.info(f"AI processing completed for content: {content_id}")
            return processing_results
            
        except Exception as e:
            logger.error(f"AI processing error for content {content_id}: {str(e)}")
            
            # Update error status
            try:
                db = next(get_db())
                content = db.query(Content).filter(Content.id == content_id).first()
                if content:
                    content.ai_processing_status = "failed"
                    content.ai_error_message = str(e)
                    db.commit()
            except:
                pass
            
            raise
    
    async def _process_audio_content(self, content: Content) -> Dict[str, Any]:
        """        Process audio content with specialized audio AI analysis.
        """        try:
            file_path = content.file_path
            
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            duration = len(y) / sr
            
            # Extract audio features
            features = await self._extract_audio_features(y, sr)
            
            # AI-powered audio analysis
            audio_analysis = await self._analyze_audio_with_ai(file_path, features)
            
            # Music-specific analysis for musicians
            music_analysis = {}
            if content.owner.role == "musician":
                music_analysis = await self._analyze_music_content(y, sr)
            
            # Audio quality assessment
            quality_metrics = await self._assess_audio_quality(y, sr)
            
            # Content moderation
            moderation_results = await self._moderate_audio_content(file_path)
            
            results = {
                "analysis_type": "audio",
                "duration": duration,
                "sample_rate": sr,
                "features": features,
                "ai_analysis": audio_analysis,
                "music_analysis": music_analysis,
                "quality_metrics": quality_metrics,
                "moderation": moderation_results,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            raise
    
    async def _process_video_content(self, content: Content) -> Dict[str, Any]:
        """        Process video content with computer vision and audio analysis.
        """        try:
            file_path = content.file_path
            
            # Extract video metadata
            video_metadata = await self.metadata_extractor.extract_video_metadata(file_path)
            
            # Extract key frames for analysis
            key_frames = await self._extract_key_frames(file_path)
            
            # AI-powered scene analysis
            scene_analysis = await self._analyze_video_scenes(key_frames)
            
            # Object and face detection
            object_detection = await self._detect_objects_in_video(key_frames)
            
            # Extract and analyze audio track
            audio_analysis = {}
            if video_metadata.get("has_audio"):
                audio_track = await self._extract_audio_from_video(file_path)
                audio_analysis = await self._analyze_video_audio(audio_track)
            
            # Content moderation
            moderation_results = await self._moderate_video_content(key_frames)
            
            # Quality assessment
            quality_metrics = await self._assess_video_quality(file_path, key_frames)
            
            results = {
                "analysis_type": "video",
                "metadata": video_metadata,
                "scene_analysis": scene_analysis,
                "object_detection": object_detection,
                "audio_analysis": audio_analysis,
                "quality_metrics": quality_metrics,
                "moderation": moderation_results,
                "key_frames_analyzed": len(key_frames),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Video processing error: {str(e)}")
            raise
    
    async def _process_image_content(self, content: Content) -> Dict[str, Any]:
        """        Process image content with advanced computer vision analysis.
        """        try:
            file_path = content.file_path
            
            # Load and analyze image
            image = Image.open(file_path)
            image_array = np.array(image)
            
            # Extract image metadata
            image_metadata = await self.metadata_extractor.extract_image_metadata(file_path)
            
            # AI-powered image analysis
            image_analysis = await self._analyze_image_with_ai(file_path)
            
            # Style and composition analysis
            style_analysis = await self._analyze_image_style(image_array)
            
            # Object and scene detection
            object_detection = await self._detect_objects_in_image(image_array)
            
            # Photography-specific analysis for photographers
            photography_analysis = {}
            if content.owner.role == "photographer":
                photography_analysis = await self._analyze_photography_technique(image_array, image_metadata)
            
            # Quality and technical assessment
            quality_metrics = await self._assess_image_quality(image_array)
            
            # Content moderation
            moderation_results = await self._moderate_image_content(file_path)
            
            results = {
                "analysis_type": "image",
                "metadata": image_metadata,
                "ai_analysis": image_analysis,
                "style_analysis": style_analysis,
                "object_detection": object_detection,
                "photography_analysis": photography_analysis,
                "quality_metrics": quality_metrics,
                "moderation": moderation_results,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise
    
    async def _process_text_content(self, content: Content) -> Dict[str, Any]:
        """        Process text content with NLP and content analysis.
        """        try:
            # Read text content
            with open(content.file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Text statistics
            text_stats = await self._calculate_text_statistics(text_content)
            
            # AI-powered content analysis
            content_analysis = await self._analyze_text_with_ai(text_content)
            
            # Sentiment analysis
            sentiment_analysis = await self._analyze_text_sentiment(text_content)
            
            # Topic modeling and classification
            topic_analysis = await self._analyze_text_topics(text_content)
            
            # SEO optimization suggestions
            seo_analysis = {}
            if content.owner.role == "blogger":
                seo_analysis = await self._analyze_seo_potential(text_content, content.title)
            
            # Readability assessment
            readability_metrics = await self._assess_text_readability(text_content)
            
            # Content originality check
            originality_check = await self._check_content_originality(text_content)
            
            results = {
                "analysis_type": "text",
                "text_stats": text_stats,
                "content_analysis": content_analysis,
                "sentiment_analysis": sentiment_analysis,
                "topic_analysis": topic_analysis,
                "seo_analysis": seo_analysis,
                "readability_metrics": readability_metrics,
                "originality_check": originality_check,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            raise
    
    async def _process_generic_content(self, content: Content) -> Dict[str, Any]:
        """        Process generic content with basic analysis.
        """        try:
            # Extract basic metadata
            metadata = await self.metadata_extractor.extract_generic_metadata(content.file_path)
            
            # Basic AI analysis based on file extension and type
            basic_analysis = await self._perform_basic_ai_analysis(content)
            
            results = {
                "analysis_type": "generic",
                "metadata": metadata,
                "basic_analysis": basic_analysis,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Generic processing error: {str(e)}")
            raise
    
    # Audio-specific methods
    
    async def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""        try:
            features = {}
            
            # Spectral features
            features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfccs'] = [float(np.mean(mfcc)) for mfcc in mfccs]
            
            # Chroma and tempo
            features['chroma'] = [float(np.mean(chroma)) for chroma in librosa.feature.chroma(y=y, sr=sr)]
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            features['rhythm_strength'] = float(np.std(np.diff(beats)))
            
            # Energy and dynamics
            features['rms_energy'] = float(np.mean(librosa.feature.rms(y=y)))
            features['dynamic_range'] = float(np.max(y) - np.min(y))
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction error: {str(e)}")
            return {}
    
    async def _analyze_audio_with_ai(self, file_path: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered audio content analysis"""        try:
            # Create prompt for audio analysis
            prompt = f"""            Analyze this audio content with the following features:
            - Spectral centroid: {features.get('spectral_centroid', 'N/A')}
            - Tempo: {features.get('tempo', 'N/A')} BPM
            - RMS Energy: {features.get('rms_energy', 'N/A')}
            
            Please provide analysis on:
            1. Genre classification
            2. Mood and emotion
            3. Energy level
            4. Instrumentation (if music)
            5. Quality assessment
            6. Suggested improvements
            
            Respond in JSON format.
            """            
            response = await self.ai_client.analyze_content(prompt, "audio")
            
            return response
            
        except Exception as e:
            logger.error(f"AI audio analysis error: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_music_content(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Specialized music analysis for musicians"""        try:
            analysis = {}
            
            # Key detection
            chroma = librosa.feature.chroma(y=y, sr=sr)
            key = np.argmax(np.sum(chroma, axis=1))
            analysis['estimated_key'] = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][key]
            
            # Harmonic/percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            analysis['harmonic_strength'] = float(np.mean(np.abs(y_harmonic)))
            analysis['percussive_strength'] = float(np.mean(np.abs(y_percussive)))
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            analysis['onset_density'] = len(onset_frames) / (len(y) / sr)  # onsets per second
            
            return analysis
            
        except Exception as e:
            logger.error(f"Music analysis error: {str(e)}")
            return {}
    
    # Helper methods for other content types would be implemented similarly...
    
    async def _generate_enhanced_metadata(self, content: Content, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-enhanced metadata and tags"""        try:
            # Extract key insights from processing results
            ai_insights = processing_results.get('ai_analysis', {})
            
            # Generate smart tags based on analysis
            smart_tags = await self._generate_smart_tags(processing_results, content.owner.role)
            
            # Generate SEO-optimized description
            enhanced_description = await self._generate_seo_description(content, processing_results)
            
            enhanced_metadata = {
                "ai_generated_tags": smart_tags,
                "enhanced_description": enhanced_description,
                "ai_insights": ai_insights,
                "processing_version": "1.0",
                "confidence_scores": processing_results.get('confidence_scores', {}),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return enhanced_metadata
            
        except Exception as e:
            logger.error(f"Enhanced metadata generation error: {str(e)}")
            return {}
    
    async def _calculate_quality_score(self, processing_results: Dict[str, Any], file_type: str) -> float:
        """Calculate overall AI quality score (0-100)"""        try:
            quality_metrics = processing_results.get('quality_metrics', {})
            
            if file_type == "audio":
                # Audio quality factors
                technical_score = quality_metrics.get('technical_quality', 50)
                clarity_score = quality_metrics.get('clarity', 50)
                production_score = quality_metrics.get('production_quality', 50)
                
                overall_score = (technical_score + clarity_score + production_score) / 3
                
            elif file_type == "image":
                # Image quality factors
                resolution_score = quality_metrics.get('resolution_score', 50)
                composition_score = quality_metrics.get('composition_score', 50)
                lighting_score = quality_metrics.get('lighting_score', 50)
                
                overall_score = (resolution_score + composition_score + lighting_score) / 3
                
            elif file_type == "video":
                # Video quality factors
                visual_score = quality_metrics.get('visual_quality', 50)
                audio_score = quality_metrics.get('audio_quality', 50)
                stability_score = quality_metrics.get('stability', 50)
                
                overall_score = (visual_score + audio_score + stability_score) / 3
                
            elif file_type == "text":
                # Text quality factors
                readability_score = quality_metrics.get('readability_score', 50)
                originality_score = quality_metrics.get('originality_score', 50)
                engagement_score = quality_metrics.get('engagement_potential', 50)
                
                overall_score = (readability_score + originality_score + engagement_score) / 3
                
            else:
                overall_score = 50  # Default for unknown types
            
            return round(max(0, min(100, overall_score)), 2)
            
        except Exception as e:
            logger.error(f"Quality score calculation error: {str(e)}")
            return 50.0
    
    async def _generate_smart_tags(self, processing_results: Dict[str, Any], user_role: str) -> List[str]:
        """Generate intelligent tags based on AI analysis"""        try:
            tags = []
            
            ai_analysis = processing_results.get('ai_analysis', {})
            
            # Role-specific tag generation
            if user_role == "musician":
                genre = ai_analysis.get('genre_classification')
                mood = ai_analysis.get('mood')
                if genre:
                    tags.append(genre.lower())
                if mood:
                    tags.append(mood.lower())
                
            elif user_role == "photographer":
                style = ai_analysis.get('photography_style')
                objects = processing_results.get('object_detection', {}).get('detected_objects', [])
                if style:
                    tags.append(style.lower())
                tags.extend([obj.lower() for obj in objects[:5]])  # Top 5 objects
                
            elif user_role == "blogger":
                topics = processing_results.get('topic_analysis', {}).get('main_topics', [])
                tags.extend([topic.lower() for topic in topics[:10]])
                
            # Remove duplicates and filter
            tags = list(set(tag for tag in tags if len(tag) > 2))
            
            return tags[:20]  # Limit to 20 tags
            
        except Exception as e:
            logger.error(f"Smart tags generation error: {str(e)}")
            return []
    
    async def _generate_seo_description(self, content: Content, processing_results: Dict[str, Any]) -> str:
        """Generate SEO-optimized description"""        try:
            ai_analysis = processing_results.get('ai_analysis', {})
            
            # Create prompt for SEO description generation
            prompt = f"""            Generate an SEO-optimized description for this {content.file_type} content:
            
            Title: {content.title}
            Original Description: {content.description}
            User Role: {content.owner.role}
            AI Analysis: {json.dumps(ai_analysis, indent=2)}
            
            Create a compelling, SEO-friendly description (150-160 characters) that:
            1. Includes relevant keywords
            2. Appeals to the target audience
            3. Encourages engagement
            4. Accurately describes the content
            """            
            seo_description = await self.ai_client.generate_text(prompt)
            
            return seo_description[:160]  # Limit to 160 characters
            
        except Exception as e:
            logger.error(f"SEO description generation error: {str(e)}")
            return content.description  # Fallback to original
