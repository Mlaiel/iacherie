"""Multimodal Content Classification System

Advanced AI-powered multimodal classification combining audio, video, image, and text analysis
for comprehensive content understanding and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

⚠️ STRONG WARNING: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted
to the full extent of the law.
"""
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from pathlib import Path
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .audio_classifier import AudioContentClassifier
from .video_classifier import VideoContentClassifier
from .image_classifier import ImageContentClassifier
from .text_classifier import TextContentClassifier
from ..engines.ml_engine import MLEngine
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError, UnsupportedFormatError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class MultimodalContentClassifier:
    """
    Enterprise-grade multimodal content classification system.
    
    Features:
    - Unified classification across audio, video, image, and text content
    - Cross-modal analysis and correlation
    - Content coherence validation
    - Comprehensive similarity matching
    - Multi-format copyright detection
    - Quality assessment across all modalities
    - Intelligent content fusion and summarization
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize multimodal classifier with all component classifiers."""
        self.settings = get_settings()
        self.ml_engine = MLEngine()
        
        # Initialize component classifiers
        self._init_classifiers(model_path)
        
        # Content type mappings
        self._init_content_mappings()
        
        # Multimodal thresholds
        self.thresholds = {
            'content_coherence': 0.75,
            'cross_modal_similarity': 0.70,
            'quality_consistency': 0.65,
            'copyright_risk': 0.80
        }

    def _init_classifiers(self, model_path: Optional[str]):
        """Initialize all content type classifiers."""
        try:
            self.audio_classifier = AudioContentClassifier(model_path)
            self.video_classifier = VideoContentClassifier(model_path)
            self.image_classifier = ImageContentClassifier(model_path)
            self.text_classifier = TextContentClassifier(model_path)
            
            logger.info("All multimodal classifiers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing classifiers: {e}")
            raise ClassificationError(f"Failed to initialize multimodal classifiers: {e}")

    def _init_content_mappings(self):
        """Initialize content type and format mappings."""
        self.content_type_map = {
            'audio': {
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma'],
                'mime_types': ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg']
            },
            'video': {
                'extensions': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
                'mime_types': ['video/mp4', 'video/avi', 'video/quicktime', 'video/webm']
            },
            'image': {
                'extensions': ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'],
                'mime_types': ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff']
            },
            'text': {
                'extensions': ['.txt', '.md', '.rtf', '.docx', '.pdf'],
                'mime_types': ['text/plain', 'text/markdown', 'application/rtf', 'application/pdf']
            }
        }
        
        # Cross-modal content relationships
        self.content_relationships = {
            'music_video': ['audio', 'video'],
            'album_cover': ['image', 'text'],
            'lyric_video': ['video', 'text', 'audio'],
            'podcast': ['audio', 'text'],
            'social_media_post': ['image', 'text'],
            'blog_post': ['text', 'image'],
            'music_album': ['audio', 'image', 'text']
        }

    @cache_result(ttl=3600)
    @track_performance
    async def classify_multimodal_content(
        self, 
        content_paths: Dict[str, Union[str, List[str]]], 
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive multimodal content classification.
        
        Args:
            content_paths: Dictionary mapping content types to file paths
                          e.g., {'audio': 'song.mp3', 'image': 'cover.jpg', 'text': 'lyrics.txt'}
            options: Classification options and parameters
            
        Returns:
            Unified multimodal classification results
        """
        try:
            if not content_paths:
                raise ClassificationError("No content paths provided")
            
            # Validate and organize content
            organized_content = await self._organize_content(content_paths)
            
            # Initialize results structure
            results = {
                'content_summary': {
                    'total_files': sum(len(files) if isinstance(files, list) else 1 
                                     for files in content_paths.values()),
                    'content_types': list(organized_content.keys()),
                    'is_multimodal': len(organized_content) > 1
                },
                'individual_results': {},
                'cross_modal_analysis': {},
                'unified_classification': {},
                'quality_assessment': {},
                'similarity_analysis': {},
                'timestamp': self._get_timestamp()
            }
            
            # Process each content type
            individual_results = await self._process_all_content_types(organized_content, options)
            results['individual_results'] = individual_results
            
            # Perform cross-modal analysis
            if len(organized_content) > 1:
                cross_modal = await self._perform_cross_modal_analysis(individual_results)
                results['cross_modal_analysis'] = cross_modal
            
            # Generate unified classification
            unified = self._generate_unified_classification(individual_results, results.get('cross_modal_analysis', {}))
            results['unified_classification'] = unified
            
            # Assess overall quality
            quality = self._assess_multimodal_quality(individual_results)
            results['quality_assessment'] = quality
            
            # Comprehensive similarity analysis
            similarity = await self._analyze_multimodal_similarity(individual_results)
            results['similarity_analysis'] = similarity
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multimodal classification: {e}")
            raise ClassificationError(f"Multimodal classification failed: {e}")

    async def _organize_content(self, content_paths: Dict[str, Union[str, List[str]]]) -> Dict[str, List[str]]:
        """Organize and validate content paths by type."""
        organized = {}
        
        for content_type, paths in content_paths.items():
            if isinstance(paths, str):
                paths = [paths]
            
            validated_paths = []
            for path in paths:
                file_path = Path(path)
                
                # Validate file exists
                if not file_path.exists():
                    logger.warning(f"File not found: {path}")
                    continue
                
                # Validate content type
                detected_type = self._detect_content_type(path)
                if detected_type != content_type:
                    logger.warning(f"Content type mismatch for {path}: expected {content_type}, got {detected_type}")
                    # Use detected type instead
                    if detected_type not in organized:
                        organized[detected_type] = []
                    organized[detected_type].append(path)
                else:
                    validated_paths.append(path)
            
            if validated_paths:
                organized[content_type] = validated_paths
        
        return organized

    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file extension and MIME type."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Try MIME type detection
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                for content_type, config in self.content_type_map.items():
                    if mime_type in config['mime_types']:
                        return content_type
        except Exception:
            pass
        
        # Fallback to extension
        for content_type, config in self.content_type_map.items():
            if extension in config['extensions']:
                return content_type
        
        raise UnsupportedFormatError(f"Unsupported file format: {extension}")

    async def _process_all_content_types(
        self, 
        organized_content: Dict[str, List[str]], 
        options: Optional[Dict]
    ) -> Dict[str, Any]:
        """Process all content types in parallel."""
        results = {}
        
        # Create tasks for parallel processing
        tasks = []
        
        for content_type, file_paths in organized_content.items():
            for file_path in file_paths:
                task = self._process_single_content(content_type, file_path, options)
                tasks.append((content_type, file_path, task))
        
        # Execute tasks
        for content_type, file_path, task in tasks:
            try:
                result = await task
                
                if content_type not in results:
                    results[content_type] = {}
                
                results[content_type][file_path] = result
                
            except Exception as e:
                logger.error(f"Error processing {content_type} file {file_path}: {e}")
                if content_type not in results:
                    results[content_type] = {}
                results[content_type][file_path] = {'error': str(e)}
        
        return results

    async def _process_single_content(
        self, 
        content_type: str, 
        file_path: str, 
        options: Optional[Dict]
    ) -> Dict[str, Any]:
        """Process a single content file."""
        try:
            if content_type == 'audio':
                return self.audio_classifier.classify_audio(file_path, options)
            elif content_type == 'video':
                return self.video_classifier.classify_video(file_path, options)
            elif content_type == 'image':
                return self.image_classifier.classify_image(file_path, options)
            elif content_type == 'text':
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                return self.text_classifier.classify_text(text_content, options)
            else:
                raise UnsupportedFormatError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error processing {content_type} content: {e}")
            raise

    async def _perform_cross_modal_analysis(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-modal analysis to find relationships between content types."""
        try:
            cross_modal = {
                'content_coherence': {},
                'thematic_consistency': {},
                'quality_correlation': {},
                'temporal_alignment': {},
                'semantic_relationships': {}
            }
            
            content_types = list(individual_results.keys())
            
            # Analyze coherence between pairs of content types
            for i, type1 in enumerate(content_types):
                for type2 in content_types[i+1:]:
                    coherence_key = f"{type1}_{type2}"
                    
                    # Content coherence analysis
                    coherence = await self._analyze_content_coherence(
                        individual_results[type1], 
                        individual_results[type2],
                        type1, 
                        type2
                    )
                    cross_modal['content_coherence'][coherence_key] = coherence
                    
                    # Thematic consistency
                    thematic = self._analyze_thematic_consistency(
                        individual_results[type1], 
                        individual_results[type2]
                    )
                    cross_modal['thematic_consistency'][coherence_key] = thematic
                    
                    # Quality correlation
                    quality_corr = self._analyze_quality_correlation(
                        individual_results[type1], 
                        individual_results[type2]
                    )
                    cross_modal['quality_correlation'][coherence_key] = quality_corr
            
            # Overall cross-modal metrics
            cross_modal['overall_coherence'] = self._calculate_overall_coherence(cross_modal)
            cross_modal['multimodal_consistency'] = self._assess_multimodal_consistency(cross_modal)
            
            return cross_modal
            
        except Exception as e:
            logger.error(f"Error in cross-modal analysis: {e}")
            return {}

    async def _analyze_content_coherence(
        self, 
        results1: Dict[str, Any], 
        results2: Dict[str, Any],
        type1: str, 
        type2: str
    ) -> Dict[str, Any]:
        """Analyze coherence between two content types."""
        try:
            # Extract content themes and classifications
            themes1 = self._extract_content_themes(results1, type1)
            themes2 = self._extract_content_themes(results2, type2)
            
            # Calculate thematic overlap
            overlap_score = self._calculate_thematic_overlap(themes1, themes2)
            
            # Analyze mood/sentiment consistency
            mood_consistency = self._analyze_mood_consistency(results1, results2, type1, type2)
            
            # Content type relationship score
            relationship_score = self._calculate_relationship_score(type1, type2)
            
            # Overall coherence
            coherence_score = (overlap_score * 0.4 + mood_consistency * 0.3 + relationship_score * 0.3)
            
            return {
                'coherence_score': float(coherence_score),
                'thematic_overlap': float(overlap_score),
                'mood_consistency': float(mood_consistency),
                'relationship_strength': float(relationship_score),
                'is_coherent': coherence_score > self.thresholds['content_coherence']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content coherence: {e}")
            return {'coherence_score': 0.0, 'is_coherent': False}

    def _extract_content_themes(self, results: Dict[str, Any], content_type: str) -> List[str]:
        """Extract themes and topics from content classification results."""
        themes = []
        
        try:
            # Get first result (assuming single file per type for now)
            first_result = next(iter(results.values())) if results else {}
            
            if content_type == 'audio':
                # Extract music genres, moods
                classifications = first_result.get('classifications', {})
                genre = classifications.get('genre_detection', {}).get('primary_genre')
                mood = classifications.get('mood_analysis', {}).get('primary_mood')
                if genre:
                    themes.append(genre)
                if mood:
                    themes.append(mood)
                    
            elif content_type == 'video':
                # Extract scene types, activities
                classifications = first_result.get('classifications', {})
                scene = classifications.get('scene_analysis', {}).get('primary_scene')
                activity = classifications.get('activity_detection', {}).get('primary_activity')
                if scene:
                    themes.append(scene)
                if activity:
                    themes.append(activity)
                    
            elif content_type == 'image':
                # Extract content types, styles
                classifications = first_result.get('classifications', {})
                content_style = classifications.get('content_type', {}).get('primary')
                image_style = classifications.get('style_analysis', {}).get('primary_style')
                if content_style:
                    themes.append(content_style)
                if image_style:
                    themes.append(image_style)
                    
            elif content_type == 'text':
                # Extract topics, genres
                classifications = first_result.get('classifications', {})
                text_type = classifications.get('content_type', {}).get('primary')
                genre = classifications.get('genre_detection', {}).get('primary_genre')
                topic = first_result.get('features', {}).get('topic_extraction', {}).get('primary_topic')
                if text_type:
                    themes.append(text_type)
                if genre:
                    themes.append(genre)
                if topic:
                    themes.append(topic)
            
            return themes
            
        except Exception as e:
            logger.error(f"Error extracting themes from {content_type}: {e}")
            return []

    def _calculate_thematic_overlap(self, themes1: List[str], themes2: List[str]) -> float:
        """Calculate thematic overlap between two sets of themes."""
        if not themes1 or not themes2:
            return 0.0
        
        # Convert to sets for intersection
        set1 = set(theme.lower() for theme in themes1)
        set2 = set(theme.lower() for theme in themes2)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def _analyze_mood_consistency(
        self, 
        results1: Dict[str, Any], 
        results2: Dict[str, Any],
        type1: str, 
        type2: str
    ) -> float:
        """Analyze mood/sentiment consistency between content types."""
        try:
            # Extract mood/sentiment from each type
            mood1 = self._extract_mood(results1, type1)
            mood2 = self._extract_mood(results2, type2)
            
            if not mood1 or not mood2:
                return 0.5  # Neutral if mood unavailable
            
            # Define mood categories and their relationships
            mood_categories = {
                'positive': ['happy', 'joy', 'excitement', 'love', 'positive', 'uplifting'],
                'negative': ['sad', 'angry', 'fear', 'negative', 'melancholy', 'dark'],
                'neutral': ['neutral', 'calm', 'peaceful', 'contemplative'],
                'energetic': ['energetic', 'aggressive', 'intense', 'powerful'],
                'mellow': ['mellow', 'relaxed', 'soft', 'gentle']
            }
            
            # Categorize moods
            category1 = self._categorize_mood(mood1.lower(), mood_categories)
            category2 = self._categorize_mood(mood2.lower(), mood_categories)
            
            # Calculate consistency
            if category1 == category2:
                return 1.0  # Perfect match
            elif self._are_compatible_moods(category1, category2):
                return 0.7  # Compatible
            else:
                return 0.3  # Inconsistent
                
        except Exception as e:
            logger.error(f"Error analyzing mood consistency: {e}")
            return 0.5

    def _extract_mood(self, results: Dict[str, Any], content_type: str) -> Optional[str]:
        """Extract mood/sentiment from content results."""
        try:
            first_result = next(iter(results.values())) if results else {}
            
            if content_type in ['audio', 'video']:
                return first_result.get('classifications', {}).get('mood_analysis', {}).get('primary_mood')
            elif content_type == 'text':
                sentiment = first_result.get('classifications', {}).get('sentiment_analysis', {}).get('primary_sentiment')
                emotion = first_result.get('classifications', {}).get('emotion_analysis', {}).get('primary_emotion')
                return emotion or sentiment
            elif content_type == 'image':
                return first_result.get('classifications', {}).get('style_analysis', {}).get('primary_style')
            
            return None
            
        except Exception:
            return None

    def _categorize_mood(self, mood: str, mood_categories: Dict[str, List[str]]) -> str:
        """Categorize a mood into broader categories."""
        for category, moods in mood_categories.items():
            if mood in moods:
                return category
        return 'unknown'

    def _are_compatible_moods(self, category1: str, category2: str) -> bool:
        """Check if two mood categories are compatible."""
        compatible_pairs = [
            ('positive', 'energetic'),
            ('mellow', 'neutral'),
            ('negative', 'mellow'),
            ('energetic', 'neutral')
        ]
        
        return (category1, category2) in compatible_pairs or (category2, category1) in compatible_pairs

    def _calculate_relationship_score(self, type1: str, type2: str) -> float:
        """Calculate relationship strength between content types."""
        # Check if types have known relationships
        for relationship, types in self.content_relationships.items():
            if type1 in types and type2 in types:
                return 1.0  # Strong relationship
        
        # Natural relationships
        natural_relationships = {
            ('audio', 'video'): 0.9,  # Music videos
            ('image', 'text'): 0.8,   # Album covers with descriptions
            ('audio', 'text'): 0.7,   # Songs with lyrics
            ('video', 'text'): 0.6,   # Videos with descriptions
            ('audio', 'image'): 0.5,  # Songs with artwork
            ('video', 'image'): 0.4   # Videos with thumbnails
        }
        
        key = (type1, type2) if (type1, type2) in natural_relationships else (type2, type1)
        return natural_relationships.get(key, 0.2)

    def _analyze_thematic_consistency(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze thematic consistency between content types."""
        try:
            # Extract themes
            themes1 = []
            themes2 = []
            
            # Simple theme extraction (can be expanded)
            for results, themes in [(results1, themes1), (results2, themes2)]:
                first_result = next(iter(results.values())) if results else {}
                classifications = first_result.get('classifications', {})
                
                # Extract various thematic elements
                for key in ['content_type', 'genre_detection', 'style_analysis']:
                    if key in classifications:
                        primary = classifications[key].get('primary', classifications[key].get('primary_genre', classifications[key].get('primary_style')))
                        if primary:
                            themes.append(primary)
            
            # Calculate consistency
            overlap = self._calculate_thematic_overlap(themes1, themes2)
            
            return {
                'thematic_overlap': float(overlap),
                'themes_1': themes1,
                'themes_2': themes2,
                'is_consistent': overlap > 0.5
            }
            
        except Exception as e:
            logger.error(f"Error analyzing thematic consistency: {e}")
            return {'thematic_overlap': 0.0, 'is_consistent': False}

    def _analyze_quality_correlation(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quality correlation between content types."""
        try:
            # Extract quality scores
            quality1 = self._extract_quality_score(results1)
            quality2 = self._extract_quality_score(results2)
            
            if quality1 is None or quality2 is None:
                return {'correlation': 0.0, 'quality_difference': 1.0}
            
            # Calculate correlation and difference
            difference = abs(quality1 - quality2)
            correlation = 1 - difference  # Simple correlation measure
            
            return {
                'quality_1': float(quality1),
                'quality_2': float(quality2),
                'correlation': float(correlation),
                'quality_difference': float(difference),
                'is_consistent': difference < 0.3
            }
            
        except Exception as e:
            logger.error(f"Error analyzing quality correlation: {e}")
            return {'correlation': 0.0}

    def _extract_quality_score(self, results: Dict[str, Any]) -> Optional[float]:
        """Extract quality score from content results."""
        try:
            first_result = next(iter(results.values())) if results else {}
            quality_metrics = first_result.get('quality_metrics', {})
            
            return quality_metrics.get('overall_quality')
            
        except Exception:
            return None

    def _calculate_overall_coherence(self, cross_modal: Dict[str, Any]) -> float:
        """Calculate overall coherence across all modalities."""
        try:
            coherence_scores = []
            
            # Extract all coherence scores
            for coherence_data in cross_modal.get('content_coherence', {}).values():
                if isinstance(coherence_data, dict) and 'coherence_score' in coherence_data:
                    coherence_scores.append(coherence_data['coherence_score'])
            
            if not coherence_scores:
                return 0.0
            
            return float(np.mean(coherence_scores))
            
        except Exception:
            return 0.0

    def _assess_multimodal_consistency(self, cross_modal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall multimodal consistency."""
        try:
            # Collect consistency metrics
            coherence_scores = []
            thematic_scores = []
            quality_correlations = []
            
            for coherence_data in cross_modal.get('content_coherence', {}).values():
                if isinstance(coherence_data, dict):
                    coherence_scores.append(coherence_data.get('coherence_score', 0))
            
            for thematic_data in cross_modal.get('thematic_consistency', {}).values():
                if isinstance(thematic_data, dict):
                    thematic_scores.append(thematic_data.get('thematic_overlap', 0))
            
            for quality_data in cross_modal.get('quality_correlation', {}).values():
                if isinstance(quality_data, dict):
                    quality_correlations.append(quality_data.get('correlation', 0))
            
            # Calculate overall consistency
            avg_coherence = np.mean(coherence_scores) if coherence_scores else 0
            avg_thematic = np.mean(thematic_scores) if thematic_scores else 0
            avg_quality = np.mean(quality_correlations) if quality_correlations else 0
            
            overall_consistency = (avg_coherence * 0.5 + avg_thematic * 0.3 + avg_quality * 0.2)
            
            return {
                'overall_consistency': float(overall_consistency),
                'coherence_average': float(avg_coherence),
                'thematic_average': float(avg_thematic),
                'quality_average': float(avg_quality),
                'is_consistent': overall_consistency > 0.7,
                'consistency_level': self._get_consistency_level(overall_consistency)
            }
            
        except Exception as e:
            logger.error(f"Error assessing multimodal consistency: {e}")
            return {'overall_consistency': 0.0, 'is_consistent': False}

    def _get_consistency_level(self, score: float) -> str:
        """Convert consistency score to descriptive level."""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.75:
            return 'good'
        elif score >= 0.6:
            return 'fair'
        elif score >= 0.4:
            return 'poor'
        else:
            return 'very_poor'

    def _generate_unified_classification(
        self, 
        individual_results: Dict[str, Any], 
        cross_modal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate unified classification across all modalities."""
        try:
            # Aggregate classifications from all modalities
            unified = {
                'content_type': self._determine_unified_content_type(individual_results),
                'genre_theme': self._determine_unified_genre(individual_results),
                'mood_sentiment': self._determine_unified_mood(individual_results),
                'quality_level': self._determine_unified_quality(individual_results),
                'coherence_assessment': cross_modal.get('multimodal_consistency', {}),
                'content_category': self._determine_content_category(individual_results),
                'protection_level': self._determine_protection_level(individual_results)
            }
            
            return unified
            
        except Exception as e:
            logger.error(f"Error generating unified classification: {e}")
            return {}

    def _determine_unified_content_type(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine unified content type across modalities."""
        try:
            # Collect content types from all modalities
            content_types = []
            
            for content_type, results in individual_results.items():
                for result in results.values():
                    if isinstance(result, dict) and 'classifications' in result:
                        classifications = result['classifications']
                        
                        # Extract primary content type based on modality
                        if content_type == 'text':
                            primary = classifications.get('content_type', {}).get('primary')
                        elif content_type == 'audio':
                            primary = classifications.get('content_type', {}).get('primary', 'music')
                        elif content_type == 'video':
                            primary = classifications.get('content_type', {}).get('primary', 'video')
                        elif content_type == 'image':
                            primary = classifications.get('content_type', {}).get('primary')
                        else:
                            primary = None
                        
                        if primary:
                            content_types.append((content_type, primary))
            
            # Determine most likely unified type
            if content_types:
                # Simple heuristic: if we have audio + video = music video
                modalities = [ct[0] for ct in content_types]
                if 'audio' in modalities and 'video' in modalities:
                    unified_type = 'music_video'
                elif 'audio' in modalities and 'text' in modalities:
                    unified_type = 'music_with_lyrics'
                elif 'image' in modalities and 'text' in modalities:
                    unified_type = 'visual_content_with_text'
                else:
                    # Use most confident classification
                    unified_type = content_types[0][1]
            else:
                unified_type = 'unknown'
            
            return {
                'unified_type': unified_type,
                'component_types': content_types,
                'confidence': self._calculate_type_confidence(content_types)
            }
            
        except Exception as e:
            logger.error(f"Error determining unified content type: {e}")
            return {'unified_type': 'unknown', 'confidence': 0.0}

    def _determine_unified_genre(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine unified genre/theme across modalities."""
        try:
            genres = []
            
            for content_type, results in individual_results.items():
                for result in results.values():
                    if isinstance(result, dict) and 'classifications' in result:
                        classifications = result['classifications']
                        
                        # Extract genre information
                        genre_data = classifications.get('genre_detection', {})
                        if genre_data:
                            primary_genre = genre_data.get('primary_genre', genre_data.get('primary'))
                            confidence = genre_data.get('genre_confidence', genre_data.get('confidence', 0))
                            
                            if primary_genre and primary_genre != 'unknown':
                                genres.append((primary_genre, confidence, content_type))
            
            if genres:
                # Sort by confidence and select best
                genres.sort(key=lambda x: x[1], reverse=True)
                best_genre = genres[0]
                
                return {
                    'primary_genre': best_genre[0],
                    'confidence': float(best_genre[1]),
                    'source_modality': best_genre[2],
                    'all_detected_genres': [(g[0], g[1]) for g in genres[:3]]
                }
            else:
                return {'primary_genre': 'unknown', 'confidence': 0.0}
                
        except Exception as e:
            logger.error(f"Error determining unified genre: {e}")
            return {'primary_genre': 'unknown', 'confidence': 0.0}

    def _determine_unified_mood(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine unified mood/sentiment across modalities."""
        try:
            moods = []
            
            for content_type, results in individual_results.items():
                for result in results.values():
                    if isinstance(result, dict) and 'classifications' in result:
                        classifications = result['classifications']
                        
                        # Extract mood/sentiment
                        if content_type in ['audio', 'video']:
                            mood_data = classifications.get('mood_analysis', {})
                            if mood_data:
                                mood = mood_data.get('primary_mood')
                                confidence = mood_data.get('confidence', 0)
                                if mood:
                                    moods.append((mood, confidence, content_type))
                        
                        elif content_type == 'text':
                            sentiment_data = classifications.get('sentiment_analysis', {})
                            emotion_data = classifications.get('emotion_analysis', {})
                            
                            if sentiment_data:
                                sentiment = sentiment_data.get('primary_sentiment')
                                confidence = sentiment_data.get('confidence', 0)
                                if sentiment:
                                    moods.append((sentiment, confidence, content_type))
                            
                            if emotion_data:
                                emotion = emotion_data.get('primary_emotion')
                                confidence = emotion_data.get('confidence', 0)
                                if emotion:
                                    moods.append((emotion, confidence, content_type))
            
            if moods:
                # Sort by confidence
                moods.sort(key=lambda x: x[1], reverse=True)
                primary_mood = moods[0]
                
                return {
                    'primary_mood': primary_mood[0],
                    'confidence': float(primary_mood[1]),
                    'source_modality': primary_mood[2],
                    'mood_consistency': self._calculate_mood_consistency(moods)
                }
            else:
                return {'primary_mood': 'neutral', 'confidence': 0.0}
                
        except Exception as e:
            logger.error(f"Error determining unified mood: {e}")
            return {'primary_mood': 'neutral', 'confidence': 0.0}

    def _calculate_mood_consistency(self, moods: List[Tuple[str, float, str]]) -> float:
        """Calculate consistency of moods across modalities."""
        if len(moods) <= 1:
            return 1.0
        
        # Simple consistency: check if most moods are in the same category
        mood_categories = {}
        for mood, confidence, _ in moods:
            category = self._categorize_mood(mood.lower(), {
                'positive': ['happy', 'joy', 'positive', 'uplifting', 'excitement'],
                'negative': ['sad', 'angry', 'negative', 'fear', 'melancholy'],
                'neutral': ['neutral', 'calm', 'peaceful']
            })
            
            mood_categories[category] = mood_categories.get(category, 0) + confidence
        
        # Calculate consistency as dominance of most frequent category
        if mood_categories:
            max_score = max(mood_categories.values())
            total_score = sum(mood_categories.values())
            return max_score / total_score if total_score > 0 else 0.0
        
        return 0.0

    def _determine_unified_quality(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine unified quality assessment across modalities."""
        try:
            quality_scores = []
            
            for content_type, results in individual_results.items():
                for result in results.values():
                    if isinstance(result, dict) and 'quality_metrics' in result:
                        quality = result['quality_metrics'].get('overall_quality')
                        if quality is not None:
                            quality_scores.append((quality, content_type))
            
            if quality_scores:
                scores = [q[0] for q in quality_scores]
                avg_quality = np.mean(scores)
                min_quality = min(scores)
                max_quality = max(scores)
                
                # Quality consistency
                quality_std = np.std(scores) if len(scores) > 1 else 0
                consistency = 1 - min(quality_std, 0.5) / 0.5  # Normalize std to 0-1
                
                return {
                    'average_quality': float(avg_quality),
                    'minimum_quality': float(min_quality),
                    'maximum_quality': float(max_quality),
                    'quality_consistency': float(consistency),
                    'quality_grade': self._get_quality_grade(avg_quality),
                    'modality_scores': [(content_type, float(score)) for score, content_type in quality_scores]
                }
            else:
                return {'average_quality': 0.0, 'quality_grade': 'unknown'}
                
        except Exception as e:
            logger.error(f"Error determining unified quality: {e}")
            return {'average_quality': 0.0, 'quality_grade': 'unknown'}

    def _determine_content_category(self, individual_results: Dict[str, Any]) -> str:
        """Determine overall content category."""
        modalities = list(individual_results.keys())
        
        # Categorize based on modality combination
        if 'audio' in modalities and 'video' in modalities:
            return 'multimedia_music'
        elif 'audio' in modalities and 'text' in modalities:
            return 'music_with_lyrics'
        elif 'image' in modalities and 'text' in modalities:
            return 'visual_content'
        elif 'audio' in modalities:
            return 'audio_content'
        elif 'video' in modalities:
            return 'video_content'
        elif 'image' in modalities:
            return 'image_content'
        elif 'text' in modalities:
            return 'text_content'
        else:
            return 'unknown'

    def _determine_protection_level(self, individual_results: Dict[str, Any]) -> str:
        """Determine required protection level based on content analysis."""
        # This is a simplified version - in production, this would be more sophisticated
        modality_count = len(individual_results)
        
        if modality_count >= 3:
            return 'high'  # Complex multimodal content needs high protection
        elif modality_count == 2:
            return 'medium'
        else:
            return 'standard'

    def _assess_multimodal_quality(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality across all modalities."""
        return self._determine_unified_quality(individual_results)

    async def _analyze_multimodal_similarity(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze similarity signatures across all modalities."""
        try:
            similarity_data = {
                'hash_signatures': {},
                'feature_vectors': {},
                'similarity_matrix': {},
                'protection_hashes': {}
            }
            
            # Collect hash signatures from each modality
            for content_type, results in individual_results.items():
                for file_path, result in results.items():
                    if isinstance(result, dict) and 'similarity_hashes' in result:
                        hashes = result['similarity_hashes']
                        
                        key = f"{content_type}_{Path(file_path).name}"
                        similarity_data['hash_signatures'][key] = hashes
            
            # Generate unified protection hash
            all_hashes = []
            for signatures in similarity_data['hash_signatures'].values():
                all_hashes.extend(signatures.values())
            
            if all_hashes:
                # Create combined hash for multimodal content
                combined_hash_input = ''.join(sorted(all_hashes))
                import hashlib
                combined_hash = hashlib.sha256(combined_hash_input.encode()).hexdigest()
                similarity_data['protection_hashes']['multimodal_hash'] = combined_hash
            
            return similarity_data
            
        except Exception as e:
            logger.error(f"Error analyzing multimodal similarity: {e}")
            return {}

    def _calculate_type_confidence(self, content_types: List[Tuple[str, str]]) -> float:
        """Calculate confidence in unified content type classification."""
        if not content_types:
            return 0.0
        
        # Simple confidence based on consistency
        unique_types = set(ct[1] for ct in content_types)
        consistency = 1.0 / len(unique_types)  # More unique types = less confidence
        
        return min(consistency, 1.0)

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C+'
        elif score >= 0.4:
            return 'C'
        else:
            return 'D'

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    async def compare_multimodal_content(
        self, 
        content1_paths: Dict[str, Union[str, List[str]]], 
        content2_paths: Dict[str, Union[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Compare two sets of multimodal content for similarity.
        
        Args:
            content1_paths: First content set
            content2_paths: Second content set
            
        Returns:
            Comprehensive similarity analysis
        """
        try:
            # Classify both content sets
            results1 = await self.classify_multimodal_content(content1_paths)
            results2 = await self.classify_multimodal_content(content2_paths)
            
            # Compare results
            comparison = {
                'overall_similarity': 0.0,
                'modality_similarities': {},
                'cross_modal_correlation': {},
                'content_match_assessment': {},
                'timestamp': self._get_timestamp()
            }
            
            # Compare each modality if present in both sets
            modalities1 = set(results1['individual_results'].keys())
            modalities2 = set(results2['individual_results'].keys())
            common_modalities = modalities1.intersection(modalities2)
            
            modality_scores = []
            
            for modality in common_modalities:
                # Compare individual modality results
                mod_similarity = await self._compare_modality_results(
                    results1['individual_results'][modality],
                    results2['individual_results'][modality],
                    modality
                )
                
                comparison['modality_similarities'][modality] = mod_similarity
                modality_scores.append(mod_similarity.get('similarity_score', 0))
            
            # Calculate overall similarity
            if modality_scores:
                comparison['overall_similarity'] = float(np.mean(modality_scores))
            
            # Cross-modal correlation comparison
            if 'cross_modal_analysis' in results1 and 'cross_modal_analysis' in results2:
                correlation_comparison = self._compare_cross_modal_analysis(
                    results1['cross_modal_analysis'],
                    results2['cross_modal_analysis']
                )
                comparison['cross_modal_correlation'] = correlation_comparison
            
            # Content match assessment
            comparison['content_match_assessment'] = {
                'is_likely_match': comparison['overall_similarity'] > 0.8,
                'confidence_level': self._get_similarity_confidence(comparison['overall_similarity']),
                'match_type': self._determine_match_type(comparison),
                'requires_manual_review': comparison['overall_similarity'] > 0.6
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing multimodal content: {e}")
            raise ClassificationError(f"Multimodal comparison failed: {e}")

    async def _compare_modality_results(
        self, 
        results1: Dict[str, Any], 
        results2: Dict[str, Any], 
        modality: str
    ) -> Dict[str, Any]:
        """Compare results for a specific modality."""
        try:
            # For now, compare the first file from each set
            result1 = next(iter(results1.values())) if results1 else {}
            result2 = next(iter(results2.values())) if results2 else {}
            
            if not result1 or not result2:
                return {'similarity_score': 0.0, 'comparison_method': 'unavailable'}
            
            # Use appropriate comparison method based on modality
            if modality == 'audio':
                return await self._compare_audio_results(result1, result2)
            elif modality == 'video':
                return await self._compare_video_results(result1, result2)
            elif modality == 'image':
                return await self._compare_image_results(result1, result2)
            elif modality == 'text':
                return await self._compare_text_results(result1, result2)
            else:
                return {'similarity_score': 0.0, 'comparison_method': 'unsupported'}
                
        except Exception as e:
            logger.error(f"Error comparing {modality} results: {e}")
            return {'similarity_score': 0.0, 'error': str(e)}

    async def _compare_audio_results(self, result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare audio classification results."""
        # Extract key features for comparison
        features1 = result1.get('features', {})
        features2 = result2.get('features', {})
        
        # Compare spectral features if available
        spectral_sim = self._compare_spectral_features(features1, features2)
        
        # Compare classifications
        class_sim = self._compare_classifications(
            result1.get('classifications', {}),
            result2.get('classifications', {})
        )
        
        # Overall similarity
        similarity = (spectral_sim * 0.6 + class_sim * 0.4)
        
        return {
            'similarity_score': float(similarity),
            'spectral_similarity': float(spectral_sim),
            'classification_similarity': float(class_sim),
            'comparison_method': 'audio_features'
        }

    async def _compare_video_results(self, result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare video classification results."""
        # Compare visual features
        features1 = result1.get('features', {})
        features2 = result2.get('features', {})
        
        visual_sim = self._compare_visual_features(features1, features2)
        
        # Compare scene analysis
        class_sim = self._compare_classifications(
            result1.get('classifications', {}),
            result2.get('classifications', {})
        )
        
        similarity = (visual_sim * 0.6 + class_sim * 0.4)
        
        return {
            'similarity_score': float(similarity),
            'visual_similarity': float(visual_sim),
            'classification_similarity': float(class_sim),
            'comparison_method': 'video_features'
        }

    async def _compare_image_results(self, result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare image classification results."""
        # Compare hashes
        hashes1 = result1.get('similarity_hashes', {})
        hashes2 = result2.get('similarity_hashes', {})
        
        hash_sim = self._compare_image_hashes(hashes1, hashes2)
        
        # Compare color features
        features1 = result1.get('features', {})
        features2 = result2.get('features', {})
        
        color_sim = self._compare_color_features(features1, features2)
        
        similarity = (hash_sim * 0.7 + color_sim * 0.3)
        
        return {
            'similarity_score': float(similarity),
            'hash_similarity': float(hash_sim),
            'color_similarity': float(color_sim),
            'comparison_method': 'image_hashes_features'
        }

    async def _compare_text_results(self, result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare text classification results."""
        # Compare semantic hashes
        hashes1 = result1.get('similarity_hashes', {})
        hashes2 = result2.get('similarity_hashes', {})
        
        hash_sim = self._compare_text_hashes(hashes1, hashes2)
        
        # Compare semantic features
        class_sim = self._compare_classifications(
            result1.get('classifications', {}),
            result2.get('classifications', {})
        )
        
        similarity = (hash_sim * 0.6 + class_sim * 0.4)
        
        return {
            'similarity_score': float(similarity),
            'hash_similarity': float(hash_sim),
            'classification_similarity': float(class_sim),
            'comparison_method': 'text_semantic'
        }

    def _compare_spectral_features(self, features1: Dict, features2: Dict) -> float:
        """Compare spectral features between audio files."""
        # Simplified comparison - in production this would be more sophisticated
        return 0.5  # Placeholder

    def _compare_visual_features(self, features1: Dict, features2: Dict) -> float:
        """Compare visual features between video files."""
        # Simplified comparison
        return 0.5  # Placeholder

    def _compare_image_hashes(self, hashes1: Dict, hashes2: Dict) -> float:
        """Compare image perceptual hashes."""
        if not hashes1 or not hashes2:
            return 0.0
        
        # Compare available hashes
        similarities = []
        
        for hash_type in ['phash', 'dhash', 'whash', 'average_hash']:
            if hash_type in hashes1 and hash_type in hashes2:
                # Simple string comparison (in production, use proper hash distance)
                if hashes1[hash_type] == hashes2[hash_type]:
                    similarities.append(1.0)
                else:
                    similarities.append(0.0)
        
        return np.mean(similarities) if similarities else 0.0

    def _compare_color_features(self, features1: Dict, features2: Dict) -> float:
        """Compare color features between images."""
        # Simplified color comparison
        colors1 = features1.get('color_analysis', {}).get('dominant_colors', [])
        colors2 = features2.get('color_analysis', {}).get('dominant_colors', [])
        
        if not colors1 or not colors2:
            return 0.0
        
        # Compare primary colors
        primary1 = colors1[0] if colors1 else {}
        primary2 = colors2[0] if colors2 else {}
        
        if primary1.get('hex') == primary2.get('hex'):
            return 1.0
        else:
            return 0.0

    def _compare_text_hashes(self, hashes1: Dict, hashes2: Dict) -> float:
        """Compare text hashes."""
        if not hashes1 or not hashes2:
            return 0.0
        
        # Compare semantic hash
        if 'semantic_hash' in hashes1 and 'semantic_hash' in hashes2:
            return 1.0 if hashes1['semantic_hash'] == hashes2['semantic_hash'] else 0.0
        
        # Fallback to normalized hash
        if 'normalized_hash' in hashes1 and 'normalized_hash' in hashes2:
            return 1.0 if hashes1['normalized_hash'] == hashes2['normalized_hash'] else 0.0
        
        return 0.0

    def _compare_classifications(self, class1: Dict, class2: Dict) -> float:
        """Compare classification results."""
        if not class1 or not class2:
            return 0.0
        
        # Simple comparison of primary classifications
        similarities = []
        
        # Compare content types
        type1 = class1.get('content_type', {}).get('primary')
        type2 = class2.get('content_type', {}).get('primary')
        if type1 and type2:
            similarities.append(1.0 if type1 == type2 else 0.0)
        
        # Compare genres
        genre1 = class1.get('genre_detection', {}).get('primary_genre')
        genre2 = class2.get('genre_detection', {}).get('primary_genre')
        if genre1 and genre2:
            similarities.append(1.0 if genre1 == genre2 else 0.0)
        
        return np.mean(similarities) if similarities else 0.0

    def _compare_cross_modal_analysis(self, cross1: Dict, cross2: Dict) -> Dict[str, Any]:
        """Compare cross-modal analysis between two content sets."""
        # Simplified comparison
        coherence1 = cross1.get('overall_coherence', 0)
        coherence2 = cross2.get('overall_coherence', 0)
        
        coherence_diff = abs(coherence1 - coherence2)
        coherence_similarity = 1 - coherence_diff
        
        return {
            'coherence_similarity': float(coherence_similarity),
            'cross_modal_match': coherence_similarity > 0.8
        }

    def _get_similarity_confidence(self, similarity: float) -> str:
        """Get confidence level for similarity score."""
        if similarity >= 0.9:
            return 'very_high'
        elif similarity >= 0.8:
            return 'high'
        elif similarity >= 0.6:
            return 'medium'
        elif similarity >= 0.4:
            return 'low'
        else:
            return 'very_low'

    def _determine_match_type(self, comparison: Dict) -> str:
        """Determine the type of match between content sets."""
        overall_sim = comparison.get('overall_similarity', 0)
        
        if overall_sim >= 0.95:
            return 'exact_match'
        elif overall_sim >= 0.85:
            return 'strong_match'
        elif overall_sim >= 0.7:
            return 'partial_match'
        elif overall_sim >= 0.5:
            return 'weak_match'
        else:
            return 'no_match'

    def get_multimodal_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of multimodal classification results."""
        try:
            summary_parts = []
            
            # Content summary
            content_summary = results.get('content_summary', {})
            if content_summary.get('content_types'):
                types = ', '.join(content_summary['content_types'])
                summary_parts.append(f"Content types: {types}")
            
            # Unified classification
            unified = results.get('unified_classification', {})
            if unified.get('content_type', {}).get('unified_type'):
                unified_type = unified['content_type']['unified_type']
                summary_parts.append(f"Unified type: {unified_type}")
            
            # Quality assessment
            quality = results.get('quality_assessment', {})
            if quality.get('quality_grade'):
                grade = quality['quality_grade']
                avg_quality = quality.get('average_quality', 0)
                summary_parts.append(f"Quality: {grade} ({avg_quality:.2f})")
            
            # Cross-modal coherence
            cross_modal = results.get('cross_modal_analysis', {})
            if cross_modal.get('multimodal_consistency', {}).get('consistency_level'):
                consistency = cross_modal['multimodal_consistency']['consistency_level']
                summary_parts.append(f"Coherence: {consistency}")
            
            return " | ".join(summary_parts) if summary_parts else "Multimodal content analyzed"
            
        except Exception as e:
            logger.error(f"Error generating multimodal summary: {e}")
            return "Summary generation failed"
