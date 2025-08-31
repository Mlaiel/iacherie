"""Content Categorizer

Advanced content categorization system for organizing and labeling content
based on multiple criteria including genre, theme, style, and purpose.

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
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from collections import Counter
import json

from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class ContentCategorizer:
    """    Enterprise-grade content categorization system.
    
    Features:
    - Multi-dimensional categorization (genre, theme, style, purpose)
    - Hierarchical category structures
    - Confidence scoring and validation
    - Custom category definitions
    - Cross-modal category consistency
    - Content tagging and labeling
    """    
    def __init__(self):
        """Initialize content categorizer."""        self.settings = get_settings()
        
        # Initialize category hierarchies
        self._init_category_hierarchies()
        
        # Configuration
        self.config = {
            'min_confidence_threshold': 0.6,
            'max_categories_per_content': 5,
            'enable_hierarchical_inference': True,
            'enable_cross_validation': True
        }

    def _init_category_hierarchies(self):
        """Initialize hierarchical category structures."""        
        # Music genre hierarchy
        self.music_genres = {
            'electronic': {
                'subgenres': ['house', 'techno', 'trance', 'dubstep', 'ambient', 'drum_and_bass'],
                'characteristics': ['synthesized', 'digital', 'rhythmic', 'produced']
            },
            'rock': {
                'subgenres': ['classic_rock', 'punk', 'metal', 'alternative', 'indie_rock', 'progressive'],
                'characteristics': ['guitar_driven', 'energetic', 'live_instruments', 'powerful']
            },
            'pop': {
                'subgenres': ['mainstream_pop', 'electropop', 'indie_pop', 'dance_pop', 'teen_pop'],
                'characteristics': ['catchy', 'commercial', 'accessible', 'radio_friendly']
            },
            'hip_hop': {
                'subgenres': ['rap', 'trap', 'old_school', 'conscious_rap', 'mumble_rap'],
                'characteristics': ['rhythmic', 'lyrical', 'urban', 'beats']
            },
            'jazz': {
                'subgenres': ['smooth_jazz', 'bebop', 'fusion', 'free_jazz', 'swing'],
                'characteristics': ['improvisation', 'complex', 'sophisticated', 'instrumental']
            },
            'classical': {
                'subgenres': ['baroque', 'romantic', 'contemporary', 'minimalist', 'orchestral'],
                'characteristics': ['orchestral', 'composed', 'traditional', 'complex']
            }
        }
        
        # Content themes
        self.content_themes = {
            'emotional': {
                'categories': ['love', 'heartbreak', 'joy', 'sadness', 'anger', 'hope', 'nostalgia'],
                'keywords': ['feel', 'heart', 'emotion', 'soul', 'love', 'pain', 'happy', 'sad']
            },
            'social': {
                'categories': ['community', 'relationships', 'family', 'friendship', 'society', 'unity'],
                'keywords': ['together', 'people', 'community', 'friend', 'family', 'social']
            },
            'inspirational': {
                'categories': ['motivation', 'success', 'achievement', 'dreams', 'perseverance'],
                'keywords': ['dream', 'achieve', 'success', 'strong', 'believe', 'overcome']
            },
            'storytelling': {
                'categories': ['narrative', 'journey', 'adventure', 'memory', 'experience'],
                'keywords': ['story', 'journey', 'remember', 'experience', 'adventure', 'tale']
            },
            'lifestyle': {
                'categories': ['party', 'celebration', 'relaxation', 'travel', 'urban', 'nature'],
                'keywords': ['party', 'celebrate', 'relax', 'travel', 'city', 'nature', 'life']
            }
        }
        
        # Content styles
        self.content_styles = {
            'visual': {
                'categories': ['minimalist', 'vintage', 'modern', 'artistic', 'commercial', 'abstract'],
                'characteristics': ['composition', 'color_palette', 'lighting', 'aesthetic']
            },
            'audio': {
                'categories': ['polished', 'raw', 'ambient', 'aggressive', 'smooth', 'experimental'],
                'characteristics': ['production_quality', 'instrumentation', 'mixing', 'mastering']
            },
            'textual': {
                'categories': ['formal', 'casual', 'poetic', 'conversational', 'technical', 'creative'],
                'characteristics': ['vocabulary', 'tone', 'structure', 'complexity']
            }
        }
        
        # Content purposes
        self.content_purposes = {
            'entertainment': {
                'subcategories': ['music', 'comedy', 'drama', 'action', 'documentary'],
                'indicators': ['fun', 'enjoy', 'entertainment', 'show', 'performance']
            },
            'educational': {
                'subcategories': ['tutorial', 'informational', 'training', 'academic', 'instructional'],
                'indicators': ['learn', 'teach', 'explain', 'guide', 'instruction', 'education']
            },
            'promotional': {
                'subcategories': ['marketing', 'advertising', 'brand', 'product', 'commercial'],
                'indicators': ['buy', 'product', 'brand', 'promotion', 'advertisement', 'sale']
            },
            'artistic': {
                'subcategories': ['creative', 'expressive', 'aesthetic', 'conceptual', 'experimental'],
                'indicators': ['art', 'creative', 'expression', 'aesthetic', 'artistic', 'concept']
            },
            'social': {
                'subcategories': ['community', 'social_media', 'communication', 'sharing', 'interaction'],
                'indicators': ['share', 'social', 'community', 'connect', 'interact', 'together']
            }
        }

    @cache_result(ttl=1800)
    @track_performance
    def categorize_content(
        self, 
        classification_results: Dict[str, Any], 
        content_type: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Categorize content based on classification results.
        
        Args:
            classification_results: Results from content classification
            content_type: Type of content (audio, video, image, text)
            options: Categorization options
            
        Returns:
            Comprehensive categorization results
        """        try:
            if not classification_results:
                raise ClassificationError("No classification results provided")
            
            # Initialize categorization results
            categorization = {
                'content_type': content_type,
                'timestamp': self._get_timestamp(),
                'primary_categories': {},
                'secondary_categories': {},
                'tags': [],
                'confidence_scores': {},
                'hierarchical_path': {},
                'cross_references': {}
            }
            
            # Extract relevant data from classification results
            classifications = classification_results.get('classifications', {})
            features = classification_results.get('features', {})
            
            # Genre categorization
            genre_category = self._categorize_genre(classifications, content_type)
            if genre_category:
                categorization['primary_categories']['genre'] = genre_category
            
            # Theme categorization
            theme_category = self._categorize_theme(classifications, features, content_type)
            if theme_category:
                categorization['primary_categories']['theme'] = theme_category
            
            # Style categorization
            style_category = self._categorize_style(classifications, features, content_type)
            if style_category:
                categorization['primary_categories']['style'] = style_category
            
            # Purpose categorization
            purpose_category = self._categorize_purpose(classifications, features)
            if purpose_category:
                categorization['primary_categories']['purpose'] = purpose_category
            
            # Generate hierarchical paths
            categorization['hierarchical_path'] = self._generate_hierarchical_paths(
                categorization['primary_categories']
            )
            
            # Extract tags
            categorization['tags'] = self._extract_content_tags(
                classifications, features, categorization['primary_categories']
            )
            
            # Calculate confidence scores
            categorization['confidence_scores'] = self._calculate_confidence_scores(
                categorization['primary_categories'], classifications
            )
            
            # Generate cross-references
            categorization['cross_references'] = self._generate_cross_references(
                categorization['primary_categories']
            )
            
            # Validate and refine categories
            if self.config['enable_cross_validation']:
                categorization = self._validate_categories(categorization, classifications)
            
            return categorization
            
        except Exception as e:
            logger.error(f"Error categorizing content: {e}")
            raise ClassificationError(f"Content categorization failed: {e}")

    def _categorize_genre(self, classifications: Dict[str, Any], content_type: str) -> Optional[Dict[str, Any]]:
        """Categorize content genre."""        try:
            # Extract genre information from classifications
            genre_data = classifications.get('genre_detection', {})
            
            if not genre_data:
                return None
            
            primary_genre = genre_data.get('primary_genre', '').lower()
            confidence = genre_data.get('genre_confidence', genre_data.get('confidence', 0))
            
            if not primary_genre or primary_genre == 'unknown':
                return None
            
            # Map to hierarchical structure
            genre_hierarchy = None
            subgenre = None
            
            # Find in music genres
            for main_genre, data in self.music_genres.items():
                if primary_genre == main_genre:
                    genre_hierarchy = main_genre
                    break
                elif primary_genre in data['subgenres']:
                    genre_hierarchy = main_genre
                    subgenre = primary_genre
                    break
            
            # If not found in hierarchy, use as is
            if not genre_hierarchy:
                genre_hierarchy = primary_genre
            
            category = {
                'primary': genre_hierarchy,
                'subgenre': subgenre,
                'confidence': float(confidence),
                'characteristics': self._get_genre_characteristics(genre_hierarchy),
                'related_genres': self._get_related_genres(genre_hierarchy)
            }
            
            return category
            
        except Exception as e:
            logger.error(f"Error categorizing genre: {e}")
            return None

    def _categorize_theme(
        self, 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Categorize content theme."""        try:
            # Extract theme-related information
            theme_scores = {}
            
            # From genre detection
            if 'genre_detection' in classifications:
                detected_themes = classifications['genre_detection'].get('detected_themes', [])
                for theme_data in detected_themes:
                    if isinstance(theme_data, dict):
                        theme = theme_data.get('topic', theme_data.get('theme'))
                        score = theme_data.get('relevance', theme_data.get('score', 0))
                        if theme:
                            theme_scores[theme] = score
            
            # From topic extraction (text content)
            if 'topic_extraction' in features:
                primary_topic = features['topic_extraction'].get('primary_topic')
                topic_confidence = features['topic_extraction'].get('topic_confidence', 0)
                if primary_topic:
                    theme_scores[primary_topic] = topic_confidence
            
            # From sentiment/emotion analysis
            if 'sentiment_analysis' in classifications:
                sentiment = classifications['sentiment_analysis'].get('primary_sentiment')
                if sentiment:
                    theme_scores[f"sentiment_{sentiment}"] = classifications['sentiment_analysis'].get('confidence', 0)
            
            if 'emotion_analysis' in classifications:
                emotion = classifications['emotion_analysis'].get('primary_emotion')
                if emotion:
                    theme_scores[f"emotion_{emotion}"] = classifications['emotion_analysis'].get('confidence', 0)
            
            # Map themes to categories
            best_theme = None
            best_score = 0
            best_category = None
            
            for theme, score in theme_scores.items():
                if score > best_score:
                    for category, data in self.content_themes.items():
                        if theme.lower() in data['categories'] or any(
                            keyword in theme.lower() for keyword in data['keywords']
                        ):
                            best_theme = theme
                            best_score = score
                            best_category = category
                            break
            
            if best_category:
                return {
                    'primary': best_category,
                    'specific_theme': best_theme,
                    'confidence': float(best_score),
                    'related_themes': self._get_related_themes(best_category),
                    'theme_intensity': self._calculate_theme_intensity(theme_scores)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error categorizing theme: {e}")
            return None

    def _categorize_style(
        self, 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Categorize content style."""        try:
            style_info = None
            confidence = 0
            
            # Content type specific style extraction
            if content_type == 'image':
                style_analysis = classifications.get('style_analysis', {})
                if style_analysis:
                    style_info = style_analysis.get('primary_style')
                    confidence = style_analysis.get('confidence', 0)
            
            elif content_type == 'audio':
                # Extract style from mood or genre characteristics
                mood_analysis = classifications.get('mood_analysis', {})
                if mood_analysis:
                    mood = mood_analysis.get('primary_mood')
                    confidence = mood_analysis.get('confidence', 0)
                    # Map mood to style
                    mood_style_map = {
                        'aggressive': 'aggressive',
                        'calm': 'smooth',
                        'energetic': 'energetic',
                        'melancholy': 'ambient',
                        'uplifting': 'polished'
                    }
                    style_info = mood_style_map.get(mood, mood)
            
            elif content_type == 'text':
                # Extract style from writing analysis
                if 'style_analysis' in features:
                    style_data = features['style_analysis']
                    style_info = style_data.get('writing_style')
                    confidence = 0.8  # Default confidence for text style
            
            elif content_type == 'video':
                # Extract style from scene analysis or quality
                scene_analysis = classifications.get('scene_analysis', {})
                if scene_analysis:
                    scene = scene_analysis.get('primary_scene')
                    # Map scene to style
                    scene_style_map = {
                        'professional_setting': 'commercial',
                        'studio_setting': 'polished',
                        'outdoor_scene': 'natural',
                        'indoor_scene': 'intimate'
                    }
                    style_info = scene_style_map.get(scene, 'modern')
                    confidence = scene_analysis.get('confidence', 0.5)
            
            if style_info and confidence > self.config['min_confidence_threshold']:
                # Map to style categories
                style_category = self._map_to_style_category(style_info, content_type)
                
                return {
                    'primary': style_category,
                    'specific_style': style_info,
                    'confidence': float(confidence),
                    'style_characteristics': self._get_style_characteristics(style_category, content_type),
                    'style_intensity': self._calculate_style_intensity(classifications, content_type)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error categorizing style: {e}")
            return None

    def _categorize_purpose(self, classifications: Dict[str, Any], features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Categorize content purpose."""        try:
            purpose_scores = {}
            
            # Analyze content type for purpose indicators
            content_type_data = classifications.get('content_type', {})
            if content_type_data:
                primary_type = content_type_data.get('primary', '').lower()
                
                # Map content types to purposes
                type_purpose_map = {
                    'music': 'entertainment',
                    'tutorial': 'educational',
                    'advertisement': 'promotional',
                    'artwork': 'artistic',
                    'social_media_post': 'social',
                    'blog_post': 'educational',
                    'album_cover': 'artistic',
                    'promotional_material': 'promotional'
                }
                
                if primary_type in type_purpose_map:
                    purpose_scores[type_purpose_map[primary_type]] = content_type_data.get('confidence', 0.7)
            
            # Analyze keywords and entities for purpose indicators
            if 'keyword_extraction' in features:
                keywords = features['keyword_extraction'].get('top_keywords', [])
                for keyword_data in keywords:
                    keyword = keyword_data.get('word', '').lower() if isinstance(keyword_data, dict) else str(keyword_data).lower()
                    
                    for purpose, data in self.content_purposes.items():
                        if keyword in data['indicators']:
                            purpose_scores[purpose] = purpose_scores.get(purpose, 0) + 0.3
            
            # Find best purpose
            if purpose_scores:
                best_purpose = max(purpose_scores.items(), key=lambda x: x[1])
                
                return {
                    'primary': best_purpose[0],
                    'confidence': float(min(best_purpose[1], 1.0)),
                    'subcategories': self.content_purposes[best_purpose[0]]['subcategories'],
                    'purpose_indicators': self._extract_purpose_indicators(best_purpose[0], features)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error categorizing purpose: {e}")
            return None

    def _generate_hierarchical_paths(self, primary_categories: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate hierarchical paths for categories."""        paths = {}
        
        try:
            # Genre hierarchy
            if 'genre' in primary_categories:
                genre_data = primary_categories['genre']
                path = [genre_data['primary']]
                if genre_data.get('subgenre'):
                    path.append(genre_data['subgenre'])
                paths['genre'] = path
            
            # Theme hierarchy
            if 'theme' in primary_categories:
                theme_data = primary_categories['theme']
                path = [theme_data['primary']]
                if theme_data.get('specific_theme'):
                    path.append(theme_data['specific_theme'])
                paths['theme'] = path
            
            # Style hierarchy
            if 'style' in primary_categories:
                style_data = primary_categories['style']
                path = [style_data['primary']]
                if style_data.get('specific_style'):
                    path.append(style_data['specific_style'])
                paths['style'] = path
            
            # Purpose hierarchy
            if 'purpose' in primary_categories:
                purpose_data = primary_categories['purpose']
                path = [purpose_data['primary']]
                paths['purpose'] = path
                
        except Exception as e:
            logger.error(f"Error generating hierarchical paths: {e}")
        
        return paths

    def _extract_content_tags(
        self, 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        primary_categories: Dict[str, Any]
    ) -> List[str]:
        """Extract relevant tags for content."""        tags = set()
        
        try:
            # Add primary category values as tags
            for category_data in primary_categories.values():
                if isinstance(category_data, dict):
                    if 'primary' in category_data:
                        tags.add(category_data['primary'])
                    if 'subgenre' in category_data and category_data['subgenre']:
                        tags.add(category_data['subgenre'])
                    if 'specific_theme' in category_data and category_data['specific_theme']:
                        tags.add(category_data['specific_theme'])
                    if 'specific_style' in category_data and category_data['specific_style']:
                        tags.add(category_data['specific_style'])
            
            # Add keywords from features
            if 'keyword_extraction' in features:
                keywords = features['keyword_extraction'].get('top_keywords', [])
                for keyword_data in keywords[:5]:  # Top 5 keywords
                    if isinstance(keyword_data, dict):
                        keyword = keyword_data.get('word')
                        if keyword and len(keyword) > 2:
                            tags.add(keyword.lower())
            
            # Add entities
            if 'entity_extraction' in features:
                entities = features['entity_extraction'].get('entities', [])
                for entity in entities[:3]:  # Top 3 entities
                    if isinstance(entity, dict):
                        entity_text = entity.get('text')
                        if entity_text and len(entity_text) > 2:
                            tags.add(entity_text.lower())
            
            # Add mood/sentiment tags
            if 'mood_analysis' in classifications:
                mood = classifications['mood_analysis'].get('primary_mood')
                if mood:
                    tags.add(f"mood_{mood}")
            
            if 'sentiment_analysis' in classifications:
                sentiment = classifications['sentiment_analysis'].get('primary_sentiment')
                if sentiment:
                    tags.add(f"sentiment_{sentiment}")
            
            # Limit tags
            return sorted(list(tags))[:15]  # Max 15 tags
            
        except Exception as e:
            logger.error(f"Error extracting content tags: {e}")
            return []

    def _calculate_confidence_scores(
        self, 
        primary_categories: Dict[str, Any], 
        classifications: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores for categories."""        confidence_scores = {}
        
        try:
            for category_name, category_data in primary_categories.items():
                if isinstance(category_data, dict) and 'confidence' in category_data:
                    confidence_scores[category_name] = float(category_data['confidence'])
            
            # Overall confidence (weighted average)
            if confidence_scores:
                weights = {'genre': 0.3, 'theme': 0.25, 'style': 0.25, 'purpose': 0.2}
                weighted_sum = sum(
                    confidence_scores.get(cat, 0) * weight 
                    for cat, weight in weights.items()
                )
                total_weight = sum(weights.get(cat, 0) for cat in confidence_scores.keys())
                
                if total_weight > 0:
                    confidence_scores['overall'] = weighted_sum / total_weight
            
        except Exception as e:
            logger.error(f"Error calculating confidence scores: {e}")
        
        return confidence_scores

    def _generate_cross_references(self, primary_categories: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate cross-references between categories."""        cross_refs = {}
        
        try:
            # Genre-Theme correlations
            if 'genre' in primary_categories and 'theme' in primary_categories:
                genre = primary_categories['genre']['primary']
                theme = primary_categories['theme']['primary']
                
                # Define some common correlations
                correlations = {
                    ('rock', 'emotional'): ['aggressive', 'energetic', 'powerful'],
                    ('pop', 'social'): ['accessible', 'mainstream', 'relatable'],
                    ('jazz', 'artistic'): ['sophisticated', 'complex', 'expressive'],
                    ('electronic', 'lifestyle'): ['modern', 'digital', 'urban']
                }
                
                correlation_key = (genre, theme)
                if correlation_key in correlations:
                    cross_refs['genre_theme'] = correlations[correlation_key]
            
            # Style-Purpose correlations
            if 'style' in primary_categories and 'purpose' in primary_categories:
                style = primary_categories['style']['primary']
                purpose = primary_categories['purpose']['primary']
                
                style_purpose_refs = {
                    ('commercial', 'promotional'): ['marketing', 'brand', 'professional'],
                    ('artistic', 'entertainment'): ['creative', 'expressive', 'aesthetic'],
                    ('polished', 'educational'): ['professional', 'clear', 'instructional']
                }
                
                sp_key = (style, purpose)
                if sp_key in style_purpose_refs:
                    cross_refs['style_purpose'] = style_purpose_refs[sp_key]
                    
        except Exception as e:
            logger.error(f"Error generating cross-references: {e}")
        
        return cross_refs

    def _validate_categories(
        self, 
        categorization: Dict[str, Any], 
        classifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and refine categories using cross-validation."""        try:
            primary_categories = categorization['primary_categories']
            
            # Check for inconsistencies
            inconsistencies = []
            
            # Genre-mood consistency check
            if 'genre' in primary_categories and 'mood_analysis' in classifications:
                genre = primary_categories['genre']['primary']
                mood = classifications['mood_analysis'].get('primary_mood')
                
                if not self._is_genre_mood_consistent(genre, mood):
                    inconsistencies.append(f"Genre '{genre}' and mood '{mood}' may be inconsistent")
            
            # Style-quality consistency check
            if 'style' in primary_categories and 'quality_metrics' in classifications:
                style = primary_categories['style']['primary']
                quality = classifications['quality_metrics'].get('overall_quality', 0)
                
                if style == 'polished' and quality < 0.7:
                    inconsistencies.append("Style 'polished' inconsistent with low quality score")
            
            # Add validation results
            categorization['validation'] = {
                'is_consistent': len(inconsistencies) == 0,
                'inconsistencies': inconsistencies,
                'confidence_adjustment': self._calculate_confidence_adjustment(inconsistencies)
            }
            
            # Adjust confidence scores based on validation
            if inconsistencies:
                adjustment = categorization['validation']['confidence_adjustment']
                for category in categorization['confidence_scores']:
                    if category != 'overall':
                        categorization['confidence_scores'][category] *= adjustment
                
                # Recalculate overall confidence
                weights = {'genre': 0.3, 'theme': 0.25, 'style': 0.25, 'purpose': 0.2}
                weighted_sum = sum(
                    categorization['confidence_scores'].get(cat, 0) * weight 
                    for cat, weight in weights.items() if cat in categorization['confidence_scores']
                )
                total_weight = sum(
                    weight for cat, weight in weights.items() 
                    if cat in categorization['confidence_scores']
                )
                
                if total_weight > 0:
                    categorization['confidence_scores']['overall'] = weighted_sum / total_weight
            
            return categorization
            
        except Exception as e:
            logger.error(f"Error validating categories: {e}")
            return categorization

    # Helper methods
    def _get_genre_characteristics(self, genre: str) -> List[str]:
        """Get characteristics for a genre."""        if genre in self.music_genres:
            return self.music_genres[genre]['characteristics']
        return []

    def _get_related_genres(self, genre: str) -> List[str]:
        """Get related genres."""        if genre in self.music_genres:
            return self.music_genres[genre]['subgenres'][:3]  # Top 3 subgenres
        return []

    def _get_related_themes(self, theme_category: str) -> List[str]:
        """Get related themes."""        if theme_category in self.content_themes:
            return self.content_themes[theme_category]['categories'][:3]  # Top 3
        return []

    def _calculate_theme_intensity(self, theme_scores: Dict[str, float]) -> float:
        """Calculate theme intensity based on scores."""        if not theme_scores:
            return 0.0
        
        max_score = max(theme_scores.values())
        avg_score = sum(theme_scores.values()) / len(theme_scores)
        
        # Intensity is based on both maximum score and average
        intensity = (max_score * 0.7 + avg_score * 0.3)
        return min(intensity, 1.0)

    def _map_to_style_category(self, style_info: str, content_type: str) -> str:
        """Map specific style to category."""        style_mappings = {
            'audio': {
                'polished': 'polished', 'raw': 'raw', 'ambient': 'ambient',
                'aggressive': 'aggressive', 'smooth': 'smooth', 'experimental': 'experimental'
            },
            'visual': {
                'minimalist': 'minimalist', 'vintage': 'vintage', 'modern': 'modern',
                'artistic': 'artistic', 'commercial': 'commercial', 'abstract': 'abstract'
            },
            'textual': {
                'formal': 'formal', 'casual': 'casual', 'poetic': 'poetic',
                'conversational': 'conversational', 'technical': 'technical', 'creative': 'creative'
            }
        }
        
        content_style_map = style_mappings.get(content_type, style_mappings.get('visual', {}))
        return content_style_map.get(style_info.lower(), style_info)

    def _get_style_characteristics(self, style_category: str, content_type: str) -> List[str]:
        """Get characteristics for a style category."""        if content_type == 'image' or content_type == 'video':
            category_data = self.content_styles['visual']
        elif content_type == 'audio':
            category_data = self.content_styles['audio']
        elif content_type == 'text':
            category_data = self.content_styles['textual']
        else:
            return []
        
        return category_data.get('characteristics', [])

    def _calculate_style_intensity(self, classifications: Dict[str, Any], content_type: str) -> float:
        """Calculate style intensity."""        # Simplified intensity calculation
        if content_type == 'audio':
            mood_data = classifications.get('mood_analysis', {})
            return mood_data.get('confidence', 0.5)
        elif content_type == 'image':
            style_data = classifications.get('style_analysis', {})
            return style_data.get('confidence', 0.5)
        else:
            return 0.5

    def _extract_purpose_indicators(self, purpose: str, features: Dict[str, Any]) -> List[str]:
        """Extract specific indicators for a purpose."""        indicators = []
        
        purpose_data = self.content_purposes.get(purpose, {})
        expected_indicators = purpose_data.get('indicators', [])
        
        # Check keywords
        if 'keyword_extraction' in features:
            keywords = features['keyword_extraction'].get('top_keywords', [])
            for keyword_data in keywords:
                keyword = keyword_data.get('word', '').lower() if isinstance(keyword_data, dict) else str(keyword_data).lower()
                if keyword in expected_indicators:
                    indicators.append(keyword)
        
        return indicators[:5]  # Top 5 indicators

    def _is_genre_mood_consistent(self, genre: str, mood: str) -> bool:
        """Check if genre and mood are consistent."""        if not mood:
            return True
        
        # Define genre-mood consistency rules
        consistency_rules = {
            'rock': ['aggressive', 'energetic', 'powerful', 'intense'],
            'pop': ['uplifting', 'happy', 'energetic', 'positive'],
            'jazz': ['smooth', 'calm', 'sophisticated', 'mellow'],
            'electronic': ['energetic', 'intense', 'hypnotic', 'futuristic'],
            'classical': ['calm', 'sophisticated', 'emotional', 'dramatic']
        }
        
        consistent_moods = consistency_rules.get(genre, [])
        return not consistent_moods or mood.lower() in consistent_moods

    def _calculate_confidence_adjustment(self, inconsistencies: List[str]) -> float:
        """Calculate confidence adjustment based on inconsistencies."""        if not inconsistencies:
            return 1.0
        
        # Reduce confidence by 10% for each inconsistency, minimum 0.5
        adjustment = max(0.5, 1.0 - (len(inconsistencies) * 0.1))
        return adjustment

    def _get_timestamp(self) -> str:
        """Get current timestamp."""        from datetime import datetime
        return datetime.now().isoformat()

    def get_category_hierarchy(self, category_type: str) -> Dict[str, Any]:
        """Get the hierarchy for a specific category type."""        hierarchies = {
            'music_genres': self.music_genres,
            'content_themes': self.content_themes,
            'content_styles': self.content_styles,
            'content_purposes': self.content_purposes
        }
        
        return hierarchies.get(category_type, {})

    def add_custom_category(
        self, 
        category_type: str, 
        category_name: str, 
        category_data: Dict[str, Any]
    ) -> bool:
        """Add a custom category to the system."""        try:
            if category_type == 'music_genres':
                self.music_genres[category_name] = category_data
            elif category_type == 'content_themes':
                self.content_themes[category_name] = category_data
            elif category_type == 'content_styles':
                if 'visual' not in category_data:
                    category_data = {'visual': category_data}
                for style_type, data in category_data.items():
                    if style_type in self.content_styles:
                        self.content_styles[style_type][category_name] = data
            elif category_type == 'content_purposes':
                self.content_purposes[category_name] = category_data
            else:
                return False
            
            logger.info(f"Added custom category '{category_name}' to {category_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom category: {e}")
            return False

    def get_categorization_summary(self, categorization: Dict[str, Any]) -> str:
        """Generate a human-readable summary of categorization results."""        try:
            summary_parts = []
            
            primary_categories = categorization.get('primary_categories', {})
            
            # Genre
            if 'genre' in primary_categories:
                genre_data = primary_categories['genre']
                genre_text = genre_data['primary']
                if genre_data.get('subgenre'):
                    genre_text += f" ({genre_data['subgenre']})"
                summary_parts.append(f"Genre: {genre_text}")
            
            # Theme
            if 'theme' in primary_categories:
                theme_data = primary_categories['theme']
                summary_parts.append(f"Theme: {theme_data['primary']}")
            
            # Style
            if 'style' in primary_categories:
                style_data = primary_categories['style']
                summary_parts.append(f"Style: {style_data['primary']}")
            
            # Purpose
            if 'purpose' in primary_categories:
                purpose_data = primary_categories['purpose']
                summary_parts.append(f"Purpose: {purpose_data['primary']}")
            
            # Overall confidence
            confidence_scores = categorization.get('confidence_scores', {})
            overall_confidence = confidence_scores.get('overall', 0)
            summary_parts.append(f"Confidence: {overall_confidence:.2f}")
            
            return " | ".join(summary_parts) if summary_parts else "No categorization available"
            
        except Exception as e:
            logger.error(f"Error generating categorization summary: {e}")
            return "Summary generation failed"
