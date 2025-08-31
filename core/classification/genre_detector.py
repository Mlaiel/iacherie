"""Genre Detector

Specialized AI-powered genre detection system for music and content classification
with support for hierarchical genre structures and cross-genre analysis.

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
import re

from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class GenreDetector:
    """    Enterprise-grade genre detection system.
    
    Features:
    - Hierarchical genre classification
    - Multi-modal genre detection (audio, text, visual)
    - Cross-genre and fusion genre identification
    - Confidence scoring and uncertainty handling
    - Temporal genre evolution tracking
    - Regional and cultural genre variations
    """    
    def __init__(self):
        """Initialize genre detector."""        self.settings = get_settings()
        
        # Initialize genre knowledge base
        self._init_genre_database()
        
        # Detection configuration
        self.config = {
            'min_confidence_threshold': 0.6,
            'max_genres_per_content': 3,
            'enable_fusion_detection': True,
            'enable_subgenre_detection': True,
            'temporal_weight': 0.3,
            'cultural_weight': 0.2
        }

    def _init_genre_database(self):
        """Initialize comprehensive genre database."""        
        # Main music genre hierarchy
        self.music_genres = {
            'electronic': {
                'subgenres': {
                    'house': {
                        'characteristics': ['four_on_floor', 'repetitive', 'danceable', 'synthesized'],
                        'tempo_range': [120, 130],
                        'keywords': ['house', 'dance', 'club', 'beat', 'electronic']
                    },
                    'techno': {
                        'characteristics': ['industrial', 'mechanical', 'hypnotic', 'minimal'],
                        'tempo_range': [120, 150],
                        'keywords': ['techno', 'industrial', 'machine', 'underground']
                    },
                    'trance': {
                        'characteristics': ['melodic', 'uplifting', 'euphoric', 'atmospheric'],
                        'tempo_range': [125, 140],
                        'keywords': ['trance', 'uplifting', 'euphoric', 'melodic']
                    },
                    'dubstep': {
                        'characteristics': ['bass_heavy', 'syncopated', 'aggressive', 'wobbly'],
                        'tempo_range': [140, 145],
                        'keywords': ['dubstep', 'bass', 'drop', 'wobble', 'heavy']
                    },
                    'ambient': {
                        'characteristics': ['atmospheric', 'ethereal', 'meditative', 'spacious'],
                        'tempo_range': [60, 90],
                        'keywords': ['ambient', 'atmospheric', 'chill', 'space', 'meditative']
                    }
                },
                'characteristics': ['synthesized', 'digital', 'programmed', 'electronic'],
                'era': '1970s-present',
                'regions': ['global']
            },
            
            'rock': {
                'subgenres': {
                    'classic_rock': {
                        'characteristics': ['guitar_driven', 'blues_based', 'powerful', 'melodic'],
                        'tempo_range': [90, 140],
                        'keywords': ['rock', 'guitar', 'classic', 'blues', 'power']
                    },
                    'punk': {
                        'characteristics': ['fast', 'aggressive', 'raw', 'rebellious'],
                        'tempo_range': [150, 200],
                        'keywords': ['punk', 'fast', 'aggressive', 'rebel', 'raw']
                    },
                    'metal': {
                        'characteristics': ['heavy', 'distorted', 'powerful', 'intense'],
                        'tempo_range': [100, 180],
                        'keywords': ['metal', 'heavy', 'distorted', 'intense', 'power']
                    },
                    'alternative': {
                        'characteristics': ['innovative', 'non_mainstream', 'diverse', 'creative'],
                        'tempo_range': [80, 160],
                        'keywords': ['alternative', 'indie', 'different', 'creative']
                    }
                },
                'characteristics': ['guitar_based', 'live_instruments', 'energetic', 'powerful'],
                'era': '1950s-present',
                'regions': ['western', 'global']
            },
            
            'pop': {
                'subgenres': {
                    'mainstream_pop': {
                        'characteristics': ['catchy', 'commercial', 'accessible', 'polished'],
                        'tempo_range': [100, 130],
                        'keywords': ['pop', 'catchy', 'hit', 'mainstream', 'radio']
                    },
                    'electropop': {
                        'characteristics': ['synthesized', 'catchy', 'danceable', 'modern'],
                        'tempo_range': [110, 140],
                        'keywords': ['electropop', 'synth', 'electronic', 'dance', 'pop']
                    },
                    'indie_pop': {
                        'characteristics': ['independent', 'quirky', 'melodic', 'alternative'],
                        'tempo_range': [90, 130],
                        'keywords': ['indie', 'independent', 'quirky', 'alternative']
                    }
                },
                'characteristics': ['melodic', 'commercial', 'accessible', 'catchy'],
                'era': '1950s-present',
                'regions': ['global']
            },
            
            'hip_hop': {
                'subgenres': {
                    'rap': {
                        'characteristics': ['rhythmic_speech', 'lyrical', 'beats', 'urban'],
                        'tempo_range': [70, 140],
                        'keywords': ['rap', 'hip', 'hop', 'beats', 'rhyme', 'urban']
                    },
                    'trap': {
                        'characteristics': ['heavy_bass', 'hi_hats', 'dark', 'atmospheric'],
                        'tempo_range': [140, 180],
                        'keywords': ['trap', 'bass', 'dark', 'heavy', 'street']
                    },
                    'old_school': {
                        'characteristics': ['classic', 'simple_beats', 'clear_vocals', 'funky'],
                        'tempo_range': [90, 110],
                        'keywords': ['old', 'school', 'classic', 'funk', 'original']
                    }
                },
                'characteristics': ['rhythmic', 'lyrical', 'urban', 'cultural'],
                'era': '1970s-present',
                'regions': ['urban', 'global']
            },
            
            'jazz': {
                'subgenres': {
                    'smooth_jazz': {
                        'characteristics': ['mellow', 'sophisticated', 'relaxing', 'polished'],
                        'tempo_range': [80, 120],
                        'keywords': ['smooth', 'jazz', 'mellow', 'sophisticated']
                    },
                    'bebop': {
                        'characteristics': ['complex', 'fast', 'improvised', 'technical'],
                        'tempo_range': [120, 200],
                        'keywords': ['bebop', 'complex', 'improvisation', 'fast']
                    },
                    'fusion': {
                        'characteristics': ['jazz_rock', 'electric', 'innovative', 'mixed'],
                        'tempo_range': [100, 160],
                        'keywords': ['fusion', 'jazz', 'rock', 'electric', 'mixed']
                    }
                },
                'characteristics': ['improvisation', 'complex', 'sophisticated', 'swing'],
                'era': '1900s-present',
                'regions': ['american', 'global']
            },
            
            'classical': {
                'subgenres': {
                    'baroque': {
                        'characteristics': ['ornate', 'complex', 'structured', 'harpsichord'],
                        'tempo_range': [60, 140],
                        'keywords': ['baroque', 'classical', 'ornate', 'complex']
                    },
                    'romantic': {
                        'characteristics': ['emotional', 'expressive', 'dramatic', 'orchestral'],
                        'tempo_range': [50, 160],
                        'keywords': ['romantic', 'emotional', 'expressive', 'dramatic']
                    },
                    'contemporary': {
                        'characteristics': ['modern', 'experimental', 'innovative', 'diverse'],
                        'tempo_range': [40, 180],
                        'keywords': ['contemporary', 'modern', 'experimental']
                    }
                },
                'characteristics': ['orchestral', 'composed', 'formal', 'traditional'],
                'era': '1600s-present',
                'regions': ['european', 'global']
            }
        }
        
        # Cross-genre and fusion patterns
        self.fusion_patterns = {
            'jazz_rock': ['jazz', 'rock'],
            'electro_swing': ['electronic', 'jazz'],
            'nu_metal': ['metal', 'hip_hop'],
            'folk_rock': ['folk', 'rock'],
            'country_pop': ['country', 'pop'],
            'latin_jazz': ['latin', 'jazz'],
            'reggae_pop': ['reggae', 'pop'],
            'punk_rock': ['punk', 'rock']
        }
        
        # Regional variations
        self.regional_genres = {
            'k_pop': {'region': 'korean', 'base_genre': 'pop', 'characteristics': ['korean', 'manufactured', 'polished']},
            'j_pop': {'region': 'japanese', 'base_genre': 'pop', 'characteristics': ['japanese', 'anime', 'cute']},
            'reggaeton': {'region': 'latin', 'base_genre': 'hip_hop', 'characteristics': ['latin', 'rhythm', 'urban']},
            'afrobeat': {'region': 'african', 'base_genre': 'world', 'characteristics': ['african', 'rhythmic', 'traditional']},
            'bollywood': {'region': 'indian', 'base_genre': 'world', 'characteristics': ['indian', 'dramatic', 'musical']}
        }

    @cache_result(ttl=1800)
    @track_performance
    def detect_genre(
        self, 
        content_data: Dict[str, Any], 
        content_type: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Detect genre from content analysis data.
        
        Args:
            content_data: Analyzed content data (classifications, features, etc.)
            content_type: Type of content (audio, text, image, video)
            options: Detection options
            
        Returns:
            Comprehensive genre detection results
        """        try:
            if not content_data:
                raise ClassificationError("No content data provided")
            
            # Initialize detection results
            detection = {
                'content_type': content_type,
                'timestamp': self._get_timestamp(),
                'primary_genre': None,
                'genre_hierarchy': [],
                'confidence_scores': {},
                'subgenres': [],
                'fusion_analysis': {},
                'regional_analysis': {},
                'temporal_analysis': {},
                'characteristics': []
            }
            
            # Extract genre indicators from content data
            genre_indicators = self._extract_genre_indicators(content_data, content_type)
            
            # Perform main genre detection
            primary_detection = self._detect_primary_genre(genre_indicators, content_type)
            if primary_detection:
                detection['primary_genre'] = primary_detection['genre']
                detection['confidence_scores']['primary'] = primary_detection['confidence']
                detection['characteristics'] = primary_detection.get('characteristics', [])
            
            # Subgenre detection
            if self.config['enable_subgenre_detection'] and detection['primary_genre']:
                subgenre_detection = self._detect_subgenres(
                    detection['primary_genre'], 
                    genre_indicators, 
                    content_type
                )
                detection['subgenres'] = subgenre_detection
            
            # Fusion genre analysis
            if self.config['enable_fusion_detection']:
                fusion_analysis = self._analyze_fusion_genres(genre_indicators, content_type)
                detection['fusion_analysis'] = fusion_analysis
            
            # Regional genre analysis
            regional_analysis = self._analyze_regional_genres(genre_indicators, content_type)
            detection['regional_analysis'] = regional_analysis
            
            # Temporal analysis (era/period detection)
            temporal_analysis = self._analyze_temporal_characteristics(genre_indicators)
            detection['temporal_analysis'] = temporal_analysis
            
            # Build genre hierarchy
            detection['genre_hierarchy'] = self._build_genre_hierarchy(detection)
            
            # Calculate overall confidence
            detection['confidence_scores']['overall'] = self._calculate_overall_confidence(detection)
            
            return detection
            
        except Exception as e:
            logger.error(f"Error detecting genre: {e}")
            raise ClassificationError(f"Genre detection failed: {e}")

    def _extract_genre_indicators(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Extract genre indicators from content analysis data."""        try:
            indicators = {
                'keywords': [],
                'characteristics': [],
                'tempo': None,
                'mood': None,
                'style': None,
                'instruments': [],
                'language': None,
                'cultural_markers': []
            }
            
            # Extract from classifications
            classifications = content_data.get('classifications', {})
            
            # Genre detection if already present
            existing_genre = classifications.get('genre_detection', {})
            if existing_genre:
                indicators['existing_genre'] = existing_genre.get('primary_genre')
                indicators['existing_confidence'] = existing_genre.get('confidence', 0)
            
            # Extract keywords
            features = content_data.get('features', {})
            if 'keyword_extraction' in features:
                keywords_data = features['keyword_extraction'].get('top_keywords', [])
                for kw_data in keywords_data:
                    if isinstance(kw_data, dict):
                        indicators['keywords'].append(kw_data.get('word', '').lower())
                    else:
                        indicators['keywords'].append(str(kw_data).lower())
            
            # Content type specific extraction
            if content_type == 'audio':
                indicators.update(self._extract_audio_indicators(classifications, features))
            elif content_type == 'text':
                indicators.update(self._extract_text_indicators(classifications, features))
            elif content_type == 'image' or content_type == 'video':
                indicators.update(self._extract_visual_indicators(classifications, features))
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error extracting genre indicators: {e}")
            return {}

    def _extract_audio_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract audio-specific genre indicators."""        indicators = {}
        
        try:
            # Tempo from audio analysis
            if 'tempo_analysis' in features:
                tempo_data = features['tempo_analysis']
                indicators['tempo'] = tempo_data.get('bpm', tempo_data.get('tempo'))
            
            # Mood analysis
            if 'mood_analysis' in classifications:
                mood_data = classifications['mood_analysis']
                indicators['mood'] = mood_data.get('primary_mood')
                indicators['mood_confidence'] = mood_data.get('confidence', 0)
            
            # Spectral characteristics
            if 'spectral_analysis' in features:
                spectral = features['spectral_analysis']
                indicators['spectral_characteristics'] = [
                    'bass_heavy' if spectral.get('bass_energy', 0) > 0.7 else None,
                    'bright' if spectral.get('treble_energy', 0) > 0.7 else None,
                    'dynamic' if spectral.get('dynamic_range', 0) > 0.6 else None
                ]
                indicators['spectral_characteristics'] = [c for c in indicators['spectral_characteristics'] if c]
            
            # Instrument detection
            if 'instrument_detection' in features:
                instruments = features['instrument_detection'].get('detected_instruments', [])
                indicators['instruments'] = instruments
            
        except Exception as e:
            logger.error(f"Error extracting audio indicators: {e}")
        
        return indicators

    def _extract_text_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract text-specific genre indicators."""        indicators = {}
        
        try:
            # Language detection
            if 'language_detection' in classifications:
                lang_data = classifications['language_detection']
                indicators['language'] = lang_data.get('primary_language')
            
            # Sentiment and emotion
            if 'sentiment_analysis' in classifications:
                sentiment = classifications['sentiment_analysis']
                indicators['sentiment'] = sentiment.get('primary_sentiment')
            
            if 'emotion_analysis' in classifications:
                emotion = classifications['emotion_analysis']
                indicators['emotion'] = emotion.get('primary_emotion')
            
            # Topic analysis
            if 'topic_extraction' in features:
                topic_data = features['topic_extraction']
                indicators['topics'] = topic_data.get('all_topics', [])
            
            # Cultural markers from entities
            if 'entity_extraction' in features:
                entities = features['entity_extraction'].get('entities', [])
                cultural_markers = []
                for entity in entities:
                    if isinstance(entity, dict):
                        entity_type = entity.get('label', '')
                        entity_text = entity.get('text', '')
                        if entity_type in ['GPE', 'NORP', 'ORG'] and entity_text:
                            cultural_markers.append(entity_text.lower())
                indicators['cultural_markers'] = cultural_markers
            
        except Exception as e:
            logger.error(f"Error extracting text indicators: {e}")
        
        return indicators

    def _extract_visual_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract visual-specific genre indicators."""        indicators = {}
        
        try:
            # Style analysis
            if 'style_analysis' in classifications:
                style_data = classifications['style_analysis']
                indicators['visual_style'] = style_data.get('primary_style')
            
            # Color analysis
            if 'color_analysis' in features:
                color_data = features['color_analysis']
                dominant_colors = color_data.get('dominant_colors', [])
                if dominant_colors:
                    # Analyze color schemes for genre indicators
                    colors = [color.get('hex', '') for color in dominant_colors[:3]]
                    indicators['color_scheme'] = self._analyze_color_scheme_for_genre(colors)
            
            # Object detection for music-related items
            if 'object_detection' in classifications:
                objects = classifications['object_detection'].get('objects', [])
                music_objects = []
                for obj in objects:
                    if isinstance(obj, dict):
                        obj_name = obj.get('object', '').lower()
                        if any(instrument in obj_name for instrument in ['guitar', 'piano', 'drum', 'microphone', 'instrument']):
                            music_objects.append(obj_name)
                indicators['visual_instruments'] = music_objects
            
        except Exception as e:
            logger.error(f"Error extracting visual indicators: {e}")
        
        return indicators

    def _detect_primary_genre(self, indicators: Dict[str, Any], content_type: str) -> Optional[Dict[str, Any]]:
        """Detect primary genre from indicators."""        try:
            genre_scores = {}
            
            # If existing genre classification exists, use it with high weight
            if 'existing_genre' in indicators and indicators['existing_genre']:
                existing_genre = indicators['existing_genre'].lower()
                existing_confidence = indicators.get('existing_confidence', 0)
                
                # Map to our genre hierarchy
                mapped_genre = self._map_to_main_genre(existing_genre)
                if mapped_genre:
                    genre_scores[mapped_genre] = existing_confidence * 0.8
            
            # Keyword-based detection
            keyword_scores = self._score_genres_by_keywords(indicators.get('keywords', []))
            for genre, score in keyword_scores.items():
                genre_scores[genre] = genre_scores.get(genre, 0) + score * 0.6
            
            # Characteristic-based detection
            char_scores = self._score_genres_by_characteristics(indicators)
            for genre, score in char_scores.items():
                genre_scores[genre] = genre_scores.get(genre, 0) + score * 0.5
            
            # Tempo-based detection (for audio)
            if content_type == 'audio' and indicators.get('tempo'):
                tempo_scores = self._score_genres_by_tempo(indicators['tempo'])
                for genre, score in tempo_scores.items():
                    genre_scores[genre] = genre_scores.get(genre, 0) + score * 0.4
            
            # Mood-based detection
            if indicators.get('mood'):
                mood_scores = self._score_genres_by_mood(indicators['mood'])
                for genre, score in mood_scores.items():
                    genre_scores[genre] = genre_scores.get(genre, 0) + score * 0.3
            
            # Find best genre
            if genre_scores:
                best_genre = max(genre_scores.items(), key=lambda x: x[1])
                
                if best_genre[1] > self.config['min_confidence_threshold']:
                    return {
                        'genre': best_genre[0],
                        'confidence': min(best_genre[1], 1.0),
                        'characteristics': self._get_genre_characteristics(best_genre[0]),
                        'score_breakdown': genre_scores
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting primary genre: {e}")
            return None

    def _score_genres_by_keywords(self, keywords: List[str]) -> Dict[str, float]:
        """Score genres based on keyword matches."""        scores = {}
        
        for genre, genre_data in self.music_genres.items():
            score = 0
            
            # Check main genre keywords
            genre_keywords = genre_data.get('keywords', [])
            for keyword in keywords:
                if keyword in genre_keywords:
                    score += 0.3
                # Partial matches
                elif any(kw in keyword or keyword in kw for kw in genre_keywords):
                    score += 0.1
            
            # Check subgenre keywords
            subgenres = genre_data.get('subgenres', {})
            for subgenre, subgenre_data in subgenres.items():
                subgenre_keywords = subgenre_data.get('keywords', [])
                for keyword in keywords:
                    if keyword in subgenre_keywords:
                        score += 0.2
                    elif any(kw in keyword or keyword in kw for kw in subgenre_keywords):
                        score += 0.05
            
            if score > 0:
                scores[genre] = score
        
        return scores

    def _score_genres_by_characteristics(self, indicators: Dict[str, Any]) -> Dict[str, float]:
        """Score genres based on musical/content characteristics."""        scores = {}
        
        for genre, genre_data in self.music_genres.items():
            score = 0
            
            # Main genre characteristics
            characteristics = genre_data.get('characteristics', [])
            
            # Check mood mapping
            mood = indicators.get('mood')
            if mood:
                mood_genre_mapping = {
                    'aggressive': ['rock', 'hip_hop'],
                    'energetic': ['rock', 'electronic', 'pop'],
                    'calm': ['jazz', 'classical'],
                    'melancholy': ['jazz', 'classical'],
                    'uplifting': ['pop', 'electronic']
                }
                
                if genre in mood_genre_mapping.get(mood, []):
                    score += 0.4
            
            # Check instruments (for audio/visual content)
            instruments = indicators.get('instruments', []) + indicators.get('visual_instruments', [])
            if instruments:
                instrument_genre_mapping = {
                    'guitar': ['rock'],
                    'piano': ['jazz', 'classical', 'pop'],
                    'drums': ['rock', 'hip_hop'],
                    'synthesizer': ['electronic', 'pop'],
                    'violin': ['classical']
                }
                
                for instrument in instruments:
                    for instr_key, mapped_genres in instrument_genre_mapping.items():
                        if instr_key in instrument.lower() and genre in mapped_genres:
                            score += 0.3
            
            # Check style characteristics
            visual_style = indicators.get('visual_style')
            if visual_style:
                style_genre_mapping = {
                    'vintage': ['rock', 'jazz'],
                    'modern': ['electronic', 'pop'],
                    'artistic': ['jazz', 'classical'],
                    'commercial': ['pop']
                }
                
                if genre in style_genre_mapping.get(visual_style, []):
                    score += 0.2
            
            if score > 0:
                scores[genre] = score
        
        return scores

    def _score_genres_by_tempo(self, tempo: float) -> Dict[str, float]:
        """Score genres based on tempo (BPM)."""        scores = {}
        
        for genre, genre_data in self.music_genres.items():
            subgenres = genre_data.get('subgenres', {})
            
            # Check if tempo falls within any subgenre range
            best_subgenre_score = 0
            
            for subgenre, subgenre_data in subgenres.items():
                tempo_range = subgenre_data.get('tempo_range', [])
                if len(tempo_range) == 2:
                    min_tempo, max_tempo = tempo_range
                    
                    if min_tempo <= tempo <= max_tempo:
                        # Perfect match
                        best_subgenre_score = max(best_subgenre_score, 1.0)
                    else:
                        # Proximity score
                        if tempo < min_tempo:
                            distance = min_tempo - tempo
                        else:
                            distance = tempo - max_tempo
                        
                        # Score decreases with distance
                        proximity_score = max(0, 1 - (distance / 30))  # 30 BPM tolerance
                        best_subgenre_score = max(best_subgenre_score, proximity_score)
            
            if best_subgenre_score > 0:
                scores[genre] = best_subgenre_score
        
        return scores

    def _score_genres_by_mood(self, mood: str) -> Dict[str, float]:
        """Score genres based on mood/emotion."""        mood_genre_mapping = {
            'aggressive': {'rock': 0.8, 'hip_hop': 0.7, 'electronic': 0.5},
            'energetic': {'rock': 0.7, 'electronic': 0.8, 'pop': 0.6, 'hip_hop': 0.5},
            'calm': {'jazz': 0.8, 'classical': 0.9, 'electronic': 0.4},
            'melancholy': {'jazz': 0.6, 'classical': 0.7, 'rock': 0.4},
            'uplifting': {'pop': 0.8, 'electronic': 0.7, 'rock': 0.5},
            'smooth': {'jazz': 0.9, 'pop': 0.5},
            'intense': {'rock': 0.8, 'hip_hop': 0.7, 'electronic': 0.6},
            'peaceful': {'classical': 0.9, 'jazz': 0.7},
            'powerful': {'rock': 0.9, 'hip_hop': 0.6}
        }
        
        return mood_genre_mapping.get(mood.lower(), {})

    def _detect_subgenres(
        self, 
        primary_genre: str, 
        indicators: Dict[str, Any], 
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Detect subgenres within the primary genre."""        try:
            subgenres = []
            
            if primary_genre not in self.music_genres:
                return subgenres
            
            genre_data = self.music_genres[primary_genre]
            available_subgenres = genre_data.get('subgenres', {})
            
            subgenre_scores = {}
            
            # Score each subgenre
            for subgenre, subgenre_data in available_subgenres.items():
                score = 0
                
                # Keyword matching
                keywords = indicators.get('keywords', [])
                subgenre_keywords = subgenre_data.get('keywords', [])
                
                for keyword in keywords:
                    if keyword in subgenre_keywords:
                        score += 0.4
                    elif any(kw in keyword or keyword in kw for kw in subgenre_keywords):
                        score += 0.2
                
                # Tempo matching (for audio)
                if content_type == 'audio' and indicators.get('tempo'):
                    tempo = indicators['tempo']
                    tempo_range = subgenre_data.get('tempo_range', [])
                    
                    if len(tempo_range) == 2:
                        min_tempo, max_tempo = tempo_range
                        if min_tempo <= tempo <= max_tempo:
                            score += 0.6
                        else:
                            # Proximity bonus
                            distance = min(abs(tempo - min_tempo), abs(tempo - max_tempo))
                            proximity_bonus = max(0, 0.3 - (distance / 100))
                            score += proximity_bonus
                
                # Characteristic matching
                characteristics = subgenre_data.get('characteristics', [])
                content_characteristics = indicators.get('characteristics', []) + indicators.get('spectral_characteristics', [])
                
                for char in content_characteristics:
                    if char and char in characteristics:
                        score += 0.3
                
                if score > 0:
                    subgenre_scores[subgenre] = score
            
            # Select top subgenres
            sorted_subgenres = sorted(subgenre_scores.items(), key=lambda x: x[1], reverse=True)
            
            for subgenre, score in sorted_subgenres[:self.config['max_genres_per_content']]:
                if score > self.config['min_confidence_threshold']:
                    subgenres.append({
                        'subgenre': subgenre,
                        'confidence': min(score, 1.0),
                        'characteristics': available_subgenres[subgenre].get('characteristics', []),
                        'parent_genre': primary_genre
                    })
            
            return subgenres
            
        except Exception as e:
            logger.error(f"Error detecting subgenres: {e}")
            return []

    def _analyze_fusion_genres(self, indicators: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Analyze potential fusion/cross-genre characteristics."""        try:
            fusion_analysis = {
                'detected_fusions': [],
                'genre_mixing_score': 0.0,
                'fusion_confidence': 0.0
            }
            
            # Detect multiple genre indicators
            genre_scores = {}
            
            # Score all genres
            keyword_scores = self._score_genres_by_keywords(indicators.get('keywords', []))
            char_scores = self._score_genres_by_characteristics(indicators)
            
            # Combine scores
            for genre, score in keyword_scores.items():
                genre_scores[genre] = score
            
            for genre, score in char_scores.items():
                genre_scores[genre] = genre_scores.get(genre, 0) + score
            
            # Look for multiple high-scoring genres
            high_scoring_genres = [genre for genre, score in genre_scores.items() if score > 0.3]
            
            if len(high_scoring_genres) >= 2:
                # Check known fusion patterns
                for fusion_name, component_genres in self.fusion_patterns.items():
                    if all(genre in high_scoring_genres for genre in component_genres):
                        fusion_confidence = min([genre_scores[genre] for genre in component_genres])
                        fusion_analysis['detected_fusions'].append({
                            'fusion_type': fusion_name,
                            'component_genres': component_genres,
                            'confidence': fusion_confidence
                        })
                
                # Calculate genre mixing score
                fusion_analysis['genre_mixing_score'] = min(1.0, len(high_scoring_genres) / 3)
                
                # Overall fusion confidence
                if fusion_analysis['detected_fusions']:
                    avg_confidence = np.mean([f['confidence'] for f in fusion_analysis['detected_fusions']])
                    fusion_analysis['fusion_confidence'] = avg_confidence
            
            return fusion_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing fusion genres: {e}")
            return {}

    def _analyze_regional_genres(self, indicators: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Analyze regional genre characteristics."""        try:
            regional_analysis = {
                'detected_regions': [],
                'cultural_confidence': 0.0
            }
            
            # Check cultural markers
            cultural_markers = indicators.get('cultural_markers', [])
            language = indicators.get('language')
            
            # Analyze regional genres
            for regional_genre, genre_data in self.regional_genres.items():
                score = 0
                
                # Language matching
                if language:
                    if genre_data['region'] in language.lower() or language.lower() in genre_data['region']:
                        score += 0.6
                
                # Cultural marker matching
                characteristics = genre_data.get('characteristics', [])
                for marker in cultural_markers:
                    if any(char in marker.lower() or marker.lower() in char for char in characteristics):
                        score += 0.3
                
                # Keywords matching
                keywords = indicators.get('keywords', [])
                for keyword in keywords:
                    if any(char in keyword or keyword in char for char in characteristics):
                        score += 0.2
                
                if score > 0.4:  # Threshold for regional detection
                    regional_analysis['detected_regions'].append({
                        'regional_genre': regional_genre,
                        'region': genre_data['region'],
                        'base_genre': genre_data['base_genre'],
                        'confidence': min(score, 1.0),
                        'characteristics': characteristics
                    })
            
            # Calculate overall cultural confidence
            if regional_analysis['detected_regions']:
                avg_confidence = np.mean([r['confidence'] for r in regional_analysis['detected_regions']])
                regional_analysis['cultural_confidence'] = avg_confidence
            
            return regional_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing regional genres: {e}")
            return {}

    def _analyze_temporal_characteristics(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal/era characteristics of the content."""        try:
            temporal_analysis = {
                'detected_era': None,
                'era_confidence': 0.0,
                'temporal_indicators': []
            }
            
            # Era indicators in keywords
            era_keywords = {
                'vintage': ['vintage', 'retro', 'old', 'classic', 'traditional'],
                'modern': ['modern', 'contemporary', 'current', 'new', 'fresh'],
                'futuristic': ['future', 'electronic', 'digital', 'synthetic', 'cyber']
            }
            
            keywords = indicators.get('keywords', [])
            era_scores = {}
            
            for era, era_words in era_keywords.items():
                score = 0
                matched_words = []
                
                for keyword in keywords:
                    for era_word in era_words:
                        if era_word in keyword.lower() or keyword.lower() in era_word:
                            score += 0.3
                            matched_words.append(keyword)
                
                if score > 0:
                    era_scores[era] = score
                    temporal_analysis['temporal_indicators'].extend(matched_words)
            
            # Determine primary era
            if era_scores:
                best_era = max(era_scores.items(), key=lambda x: x[1])
                temporal_analysis['detected_era'] = best_era[0]
                temporal_analysis['era_confidence'] = min(best_era[1], 1.0)
            
            return temporal_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing temporal characteristics: {e}")
            return {}

    def _build_genre_hierarchy(self, detection: Dict[str, Any]) -> List[str]:
        """Build hierarchical genre path."""        hierarchy = []
        
        try:
            # Primary genre
            if detection['primary_genre']:
                hierarchy.append(detection['primary_genre'])
                
                # Add best subgenre if available
                subgenres = detection.get('subgenres', [])
                if subgenres:
                    best_subgenre = max(subgenres, key=lambda x: x['confidence'])
                    hierarchy.append(best_subgenre['subgenre'])
                
                # Add fusion information if relevant
                fusion_analysis = detection.get('fusion_analysis', {})
                if fusion_analysis.get('detected_fusions'):
                    best_fusion = max(fusion_analysis['detected_fusions'], key=lambda x: x['confidence'])
                    hierarchy.append(f"fusion_{best_fusion['fusion_type']}")
                
                # Add regional modifier if relevant
                regional_analysis = detection.get('regional_analysis', {})
                if regional_analysis.get('detected_regions'):
                    best_regional = max(regional_analysis['detected_regions'], key=lambda x: x['confidence'])
                    hierarchy.append(f"regional_{best_regional['regional_genre']}")
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error building genre hierarchy: {e}")
            return hierarchy

    def _calculate_overall_confidence(self, detection: Dict[str, Any]) -> float:
        """Calculate overall confidence in genre detection."""        try:
            confidence_scores = detection.get('confidence_scores', {})
            primary_confidence = confidence_scores.get('primary', 0)
            
            # Weight factors
            weights = {
                'primary': 0.6,
                'subgenre': 0.2,
                'fusion': 0.1,
                'regional': 0.1
            }
            
            total_confidence = primary_confidence * weights['primary']
            total_weight = weights['primary']
            
            # Add subgenre confidence
            subgenres = detection.get('subgenres', [])
            if subgenres:
                avg_subgenre_conf = np.mean([sg['confidence'] for sg in subgenres])
                total_confidence += avg_subgenre_conf * weights['subgenre']
                total_weight += weights['subgenre']
            
            # Add fusion confidence
            fusion_analysis = detection.get('fusion_analysis', {})
            fusion_confidence = fusion_analysis.get('fusion_confidence', 0)
            if fusion_confidence > 0:
                total_confidence += fusion_confidence * weights['fusion']
                total_weight += weights['fusion']
            
            # Add regional confidence
            regional_analysis = detection.get('regional_analysis', {})
            cultural_confidence = regional_analysis.get('cultural_confidence', 0)
            if cultural_confidence > 0:
                total_confidence += cultural_confidence * weights['regional']
                total_weight += weights['regional']
            
            # Calculate weighted average
            overall_confidence = total_confidence / total_weight if total_weight > 0 else 0
            
            return min(overall_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.0

    # Helper methods
    def _map_to_main_genre(self, genre_name: str) -> Optional[str]:
        """Map a genre name to main genre categories."""        genre_name = genre_name.lower()
        
        # Direct mapping
        if genre_name in self.music_genres:
            return genre_name
        
        # Check subgenres
        for main_genre, genre_data in self.music_genres.items():
            subgenres = genre_data.get('subgenres', {})
            if genre_name in subgenres:
                return main_genre
        
        # Fuzzy matching
        for main_genre in self.music_genres:
            if genre_name in main_genre or main_genre in genre_name:
                return main_genre
        
        return None

    def _get_genre_characteristics(self, genre: str) -> List[str]:
        """Get characteristics for a genre."""        if genre in self.music_genres:
            return self.music_genres[genre].get('characteristics', [])
        return []

    def _analyze_color_scheme_for_genre(self, colors: List[str]) -> Optional[str]:
        """Analyze color scheme for genre indicators."""        try:
            # Simple color-genre associations
            color_genre_mapping = {
                'dark': ['rock', 'metal', 'gothic'],
                'bright': ['pop', 'electronic'],
                'warm': ['jazz', 'soul'],
                'cool': ['electronic', 'ambient'],
                'monochrome': ['classical', 'minimalist']
            }
            
            # Analyze color properties (simplified)
            # This would need more sophisticated color analysis in production
            if len(colors) <= 2:
                return 'monochrome'
            
            # Placeholder logic
            return 'mixed'
            
        except Exception:
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp."""        from datetime import datetime
        return datetime.now().isoformat()

    def get_genre_info(self, genre: str) -> Dict[str, Any]:
        """Get detailed information about a specific genre."""        try:
            genre = genre.lower()
            
            if genre in self.music_genres:
                genre_data = self.music_genres[genre].copy()
                genre_data['genre_name'] = genre
                genre_data['is_main_genre'] = True
                return genre_data
            
            # Check if it's a subgenre
            for main_genre, main_data in self.music_genres.items():
                subgenres = main_data.get('subgenres', {})
                if genre in subgenres:
                    subgenre_data = subgenres[genre].copy()
                    subgenre_data['genre_name'] = genre
                    subgenre_data['parent_genre'] = main_genre
                    subgenre_data['is_main_genre'] = False
                    return subgenre_data
            
            # Check regional genres
            if genre in self.regional_genres:
                regional_data = self.regional_genres[genre].copy()
                regional_data['genre_name'] = genre
                regional_data['is_regional'] = True
                return regional_data
            
            return {'error': f'Genre "{genre}" not found in database'}
            
        except Exception as e:
            logger.error(f"Error getting genre info: {e}")
            return {'error': str(e)}

    def get_all_genres(self) -> Dict[str, List[str]]:
        """Get list of all available genres."""        try:
            all_genres = {
                'main_genres': list(self.music_genres.keys()),
                'subgenres': {},
                'regional_genres': list(self.regional_genres.keys()),
                'fusion_patterns': list(self.fusion_patterns.keys())
            }
            
            # Collect all subgenres
            for main_genre, genre_data in self.music_genres.items():
                subgenres = list(genre_data.get('subgenres', {}).keys())
                if subgenres:
                    all_genres['subgenres'][main_genre] = subgenres
            
            return all_genres
            
        except Exception as e:
            logger.error(f"Error getting all genres: {e}")
            return {}

    def add_custom_genre(
        self, 
        genre_name: str, 
        genre_data: Dict[str, Any], 
        parent_genre: Optional[str] = None
    ) -> bool:
        """Add a custom genre to the system."""        try:
            genre_name = genre_name.lower()
            
            if parent_genre:
                # Add as subgenre
                parent_genre = parent_genre.lower()
                if parent_genre in self.music_genres:
                    if 'subgenres' not in self.music_genres[parent_genre]:
                        self.music_genres[parent_genre]['subgenres'] = {}
                    
                    self.music_genres[parent_genre]['subgenres'][genre_name] = genre_data
                    logger.info(f"Added custom subgenre '{genre_name}' under '{parent_genre}'")
                    return True
                else:
                    logger.error(f"Parent genre '{parent_genre}' not found")
                    return False
            else:
                # Add as main genre
                self.music_genres[genre_name] = genre_data
                logger.info(f"Added custom main genre '{genre_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Error adding custom genre: {e}")
            return False

    def get_detection_summary(self, detection: Dict[str, Any]) -> str:
        """Generate a human-readable summary of genre detection results."""        try:
            summary_parts = []
            
            # Primary genre
            if detection.get('primary_genre'):
                primary = detection['primary_genre']
                confidence = detection.get('confidence_scores', {}).get('primary', 0)
                summary_parts.append(f"Genre: {primary} ({confidence:.2f})")
            
            # Subgenres
            subgenres = detection.get('subgenres', [])
            if subgenres:
                best_subgenre = max(subgenres, key=lambda x: x['confidence'])
                summary_parts.append(f"Subgenre: {best_subgenre['subgenre']}")
            
            # Fusion
            fusion_analysis = detection.get('fusion_analysis', {})
            if fusion_analysis.get('detected_fusions'):
                best_fusion = max(fusion_analysis['detected_fusions'], key=lambda x: x['confidence'])
                summary_parts.append(f"Fusion: {best_fusion['fusion_type']}")
            
            # Regional
            regional_analysis = detection.get('regional_analysis', {})
            if regional_analysis.get('detected_regions'):
                best_regional = max(regional_analysis['detected_regions'], key=lambda x: x['confidence'])
                summary_parts.append(f"Regional: {best_regional['regional_genre']}")
            
            # Overall confidence
            overall_confidence = detection.get('confidence_scores', {}).get('overall', 0)
            summary_parts.append(f"Overall confidence: {overall_confidence:.2f}")
            
            return " | ".join(summary_parts) if summary_parts else "No genre detected"
            
        except Exception as e:
            logger.error(f"Error generating detection summary: {e}")
            return "Summary generation failed"
