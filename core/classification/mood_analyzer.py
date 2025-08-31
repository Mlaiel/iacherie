"""Mood Analyzer

Advanced AI-powered mood and emotional state analysis for multimedia content
with support for cross-modal emotion detection and sentiment analysis.

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
"""import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from collections import Counter, defaultdict
import re

from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class MoodAnalyzer:
    """    Enterprise-grade mood and emotional analysis system.
    
    Features:
    - Multi-modal emotion detection (audio, text, visual)
    - Valence-arousal mapping
    - Temporal mood analysis
    - Cultural emotion variations
    - Composite emotion detection
    - Mood transition analysis
    - Contextual emotion understanding
    """    
    def __init__(self):
        """Initialize mood analyzer."""        self.settings = get_settings()
        
        # Initialize emotion models and mappings
        self._init_emotion_models()
        
        # Analysis configuration
        self.config = {
            'min_confidence_threshold': 0.5,
            'max_emotions_per_analysis': 5,
            'enable_temporal_analysis': True,
            'enable_cultural_adaptation': True,
            'valence_weight': 0.6,
            'arousal_weight': 0.4,
            'context_sensitivity': 0.3
        }

    def _init_emotion_models(self):
        """Initialize emotion models and mapping systems."""        
        # Primary emotion categories (Plutchik's wheel extended)
        self.primary_emotions = {
            'joy': {
                'valence': 0.8, 'arousal': 0.7,
                'synonyms': ['happiness', 'delight', 'pleasure', 'elation', 'bliss'],
                'indicators': ['happy', 'joyful', 'cheerful', 'upbeat', 'positive', 'bright'],
                'audio_features': ['major_key', 'fast_tempo', 'high_energy', 'bright_timbre'],
                'visual_features': ['bright_colors', 'upward_movement', 'smiling', 'open_gestures']
            },
            'sadness': {
                'valence': 0.2, 'arousal': 0.3,
                'synonyms': ['melancholy', 'sorrow', 'grief', 'depression', 'despair'],
                'indicators': ['sad', 'melancholy', 'depressed', 'gloomy', 'down', 'blue'],
                'audio_features': ['minor_key', 'slow_tempo', 'low_energy', 'dark_timbre'],
                'visual_features': ['dark_colors', 'downward_movement', 'tears', 'closed_posture']
            },
            'anger': {
                'valence': 0.2, 'arousal': 0.9,
                'synonyms': ['rage', 'fury', 'irritation', 'hostility', 'wrath'],
                'indicators': ['angry', 'mad', 'furious', 'irritated', 'hostile', 'aggressive'],
                'audio_features': ['dissonance', 'fast_tempo', 'high_energy', 'harsh_timbre'],
                'visual_features': ['red_colors', 'sharp_movements', 'frowning', 'tense_posture']
            },
            'fear': {
                'valence': 0.3, 'arousal': 0.8,
                'synonyms': ['anxiety', 'terror', 'dread', 'panic', 'worry'],
                'indicators': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'fearful'],
                'audio_features': ['minor_key', 'irregular_rhythm', 'tension', 'dissonance'],
                'visual_features': ['dark_colors', 'hiding', 'wide_eyes', 'defensive_posture']
            },
            'surprise': {
                'valence': 0.6, 'arousal': 0.8,
                'synonyms': ['amazement', 'astonishment', 'wonder', 'shock'],
                'indicators': ['surprised', 'amazed', 'astonished', 'shocked', 'unexpected'],
                'audio_features': ['sudden_changes', 'dynamic_contrasts', 'unexpected_harmonies'],
                'visual_features': ['bright_contrasts', 'wide_eyes', 'open_mouth', 'sudden_movements']
            },
            'disgust': {
                'valence': 0.2, 'arousal': 0.5,
                'synonyms': ['revulsion', 'aversion', 'repugnance', 'loathing'],
                'indicators': ['disgusted', 'repulsed', 'revolted', 'sick', 'nauseated'],
                'audio_features': ['dissonance', 'harsh_timbre', 'irregular_patterns'],
                'visual_features': ['unpleasant_imagery', 'wrinkled_nose', 'turned_away']
            },
            'anticipation': {
                'valence': 0.7, 'arousal': 0.6,
                'synonyms': ['expectation', 'excitement', 'eagerness', 'hope'],
                'indicators': ['excited', 'eager', 'expectant', 'hopeful', 'anticipating'],
                'audio_features': ['building_tension', 'crescendo', 'acceleration'],
                'visual_features': ['forward_leaning', 'focused_gaze', 'preparation_gestures']
            },
            'trust': {
                'valence': 0.7, 'arousal': 0.4,
                'synonyms': ['confidence', 'faith', 'reliance', 'acceptance'],
                'indicators': ['trusting', 'confident', 'secure', 'peaceful', 'calm'],
                'audio_features': ['consonance', 'steady_rhythm', 'warm_timbre'],
                'visual_features': ['open_posture', 'eye_contact', 'relaxed_expression']
            }
        }
        
        # Complex emotions (combinations)
        self.complex_emotions = {
            'love': {
                'components': [('joy', 0.6), ('trust', 0.4)],
                'valence': 0.9, 'arousal': 0.6,
                'indicators': ['love', 'affection', 'romantic', 'tender', 'caring', 'devoted']
            },
            'guilt': {
                'components': [('fear', 0.4), ('sadness', 0.6)],
                'valence': 0.2, 'arousal': 0.4,
                'indicators': ['guilty', 'ashamed', 'regretful', 'remorseful']
            },
            'pride': {
                'components': [('joy', 0.7), ('anger', 0.3)],
                'valence': 0.8, 'arousal': 0.5,
                'indicators': ['proud', 'confident', 'accomplished', 'satisfied']
            },
            'envy': {
                'components': [('anger', 0.5), ('sadness', 0.5)],
                'valence': 0.3, 'arousal': 0.6,
                'indicators': ['envious', 'jealous', 'resentful', 'covetous']
            },
            'nostalgia': {
                'components': [('sadness', 0.4), ('joy', 0.4), ('trust', 0.2)],
                'valence': 0.5, 'arousal': 0.3,
                'indicators': ['nostalgic', 'wistful', 'reminiscent', 'sentimental']
            },
            'contempt': {
                'components': [('anger', 0.5), ('disgust', 0.5)],
                'valence': 0.2, 'arousal': 0.6,
                'indicators': ['contemptuous', 'scornful', 'disdainful', 'superior']
            }
        }
        
        # Mood states (longer-term emotional states)
        self.mood_states = {
            'euphoric': {
                'dominant_emotions': ['joy', 'excitement'],
                'duration': 'extended',
                'intensity': 'high',
                'stability': 'low'
            },
            'depressed': {
                'dominant_emotions': ['sadness', 'despair'],
                'duration': 'extended',
                'intensity': 'moderate_to_high',
                'stability': 'high'
            },
            'anxious': {
                'dominant_emotions': ['fear', 'worry'],
                'duration': 'variable',
                'intensity': 'moderate_to_high',
                'stability': 'low'
            },
            'peaceful': {
                'dominant_emotions': ['trust', 'contentment'],
                'duration': 'extended',
                'intensity': 'low_to_moderate',
                'stability': 'high'
            },
            'energetic': {
                'dominant_emotions': ['excitement', 'anticipation'],
                'duration': 'short_to_moderate',
                'intensity': 'high',
                'stability': 'moderate'
            },
            'melancholic': {
                'dominant_emotions': ['sadness', 'nostalgia'],
                'duration': 'extended',
                'intensity': 'moderate',
                'stability': 'high'
            },
            'aggressive': {
                'dominant_emotions': ['anger', 'hostility'],
                'duration': 'short_to_moderate',
                'intensity': 'high',
                'stability': 'low'
            },
            'contemplative': {
                'dominant_emotions': ['pensiveness', 'curiosity'],
                'duration': 'moderate_to_extended',
                'intensity': 'low_to_moderate',
                'stability': 'moderate'
            }
        }
        
        # Cultural emotion variations
        self.cultural_variations = {
            'western': {
                'emotion_expression': 'direct',
                'intensity_preference': 'moderate_to_high',
                'primary_emotions': ['joy', 'anger', 'sadness', 'fear']
            },
            'eastern': {
                'emotion_expression': 'subtle',
                'intensity_preference': 'moderate',
                'primary_emotions': ['harmony', 'respect', 'contemplation']
            },
            'latin': {
                'emotion_expression': 'expressive',
                'intensity_preference': 'high',
                'primary_emotions': ['passion', 'joy', 'family_bonds']
            },
            'nordic': {
                'emotion_expression': 'reserved',
                'intensity_preference': 'low_to_moderate',
                'primary_emotions': ['melancholy', 'contemplation', 'nature_connection']
            }
        }

    @cache_result(ttl=1800)
    @track_performance
    def analyze_mood(
        self, 
        content_data: Dict[str, Any], 
        content_type: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Comprehensive mood and emotion analysis.
        
        Args:
            content_data: Analyzed content data
            content_type: Type of content (audio, text, image, video)
            options: Analysis options
            
        Returns:
            Detailed mood analysis results
        """        try:
            if not content_data:
                raise ClassificationError("No content data provided")
            
            # Initialize analysis results
            analysis = {
                'content_type': content_type,
                'timestamp': self._get_timestamp(),
                'primary_emotion': None,
                'emotion_scores': {},
                'mood_state': None,
                'valence_arousal': {'valence': 0.5, 'arousal': 0.5},
                'emotion_complexity': 0.0,
                'emotional_transitions': [],
                'cultural_context': {},
                'confidence_scores': {},
                'emotional_keywords': [],
                'emotion_indicators': []
            }
            
            # Extract emotion indicators from content
            emotion_indicators = self._extract_emotion_indicators(content_data, content_type)
            analysis['emotion_indicators'] = emotion_indicators
            
            # Analyze primary emotions
            emotion_analysis = self._analyze_primary_emotions(emotion_indicators, content_type)
            analysis.update(emotion_analysis)
            
            # Analyze complex emotions
            complex_analysis = self._analyze_complex_emotions(emotion_indicators, analysis['emotion_scores'])
            analysis['complex_emotions'] = complex_analysis
            
            # Determine mood state
            mood_analysis = self._determine_mood_state(analysis['emotion_scores'], emotion_indicators)
            analysis.update(mood_analysis)
            
            # Valence-arousal mapping
            valence_arousal = self._calculate_valence_arousal(analysis['emotion_scores'])
            analysis['valence_arousal'] = valence_arousal
            
            # Temporal analysis (if applicable)
            if self.config['enable_temporal_analysis']:
                temporal_analysis = self._analyze_temporal_emotions(emotion_indicators)
                analysis['temporal_analysis'] = temporal_analysis
            
            # Cultural context analysis
            if self.config['enable_cultural_adaptation']:
                cultural_analysis = self._analyze_cultural_context(emotion_indicators)
                analysis['cultural_context'] = cultural_analysis
            
            # Calculate emotion complexity
            analysis['emotion_complexity'] = self._calculate_emotion_complexity(analysis['emotion_scores'])
            
            # Overall confidence
            analysis['confidence_scores']['overall'] = self._calculate_overall_confidence(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing mood: {e}")
            raise ClassificationError(f"Mood analysis failed: {e}")

    def _extract_emotion_indicators(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Extract emotion indicators from content analysis data."""        try:
            indicators = {
                'keywords': [],
                'sentiment': None,
                'tone': None,
                'energy_level': None,
                'tempo': None,
                'key_mode': None,
                'color_palette': [],
                'facial_expressions': [],
                'vocal_characteristics': {},
                'textual_emotions': [],
                'contextual_cues': []
            }
            
            # Extract from classifications
            classifications = content_data.get('classifications', {})
            features = content_data.get('features', {})
            
            # Sentiment analysis results
            if 'sentiment_analysis' in classifications:
                sentiment_data = classifications['sentiment_analysis']
                indicators['sentiment'] = sentiment_data.get('primary_sentiment')
                indicators['sentiment_confidence'] = sentiment_data.get('confidence', 0)
            
            # Emotion analysis results (if already present)
            if 'emotion_analysis' in classifications:
                emotion_data = classifications['emotion_analysis']
                indicators['existing_emotions'] = emotion_data.get('emotions', [])
                indicators['primary_emotion'] = emotion_data.get('primary_emotion')
            
            # Extract keywords
            if 'keyword_extraction' in features:
                keywords_data = features['keyword_extraction'].get('top_keywords', [])
                for kw_data in keywords_data:
                    if isinstance(kw_data, dict):
                        indicators['keywords'].append(kw_data.get('word', '').lower())
                    else:
                        indicators['keywords'].append(str(kw_data).lower())
            
            # Content type specific extraction
            if content_type == 'audio':
                indicators.update(self._extract_audio_emotion_indicators(classifications, features))
            elif content_type == 'text':
                indicators.update(self._extract_text_emotion_indicators(classifications, features))
            elif content_type in ['image', 'video']:
                indicators.update(self._extract_visual_emotion_indicators(classifications, features))
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error extracting emotion indicators: {e}")
            return {}

    def _extract_audio_emotion_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract audio-specific emotion indicators."""        indicators = {}
        
        try:
            # Tempo analysis
            if 'tempo_analysis' in features:
                tempo_data = features['tempo_analysis']
                indicators['tempo'] = tempo_data.get('bpm', tempo_data.get('tempo'))
            
            # Key and mode analysis
            if 'key_analysis' in features:
                key_data = features['key_analysis']
                indicators['key_mode'] = key_data.get('mode', 'unknown')  # major/minor
                indicators['musical_key'] = key_data.get('key')
            
            # Energy analysis
            if 'energy_analysis' in features:
                energy_data = features['energy_analysis']
                indicators['energy_level'] = energy_data.get('energy_level', energy_data.get('energy'))
            
            # Vocal characteristics
            if 'vocal_analysis' in features:
                vocal_data = features['vocal_analysis']
                indicators['vocal_characteristics'] = {
                    'pitch': vocal_data.get('pitch_mean'),
                    'pitch_variance': vocal_data.get('pitch_variance'),
                    'speaking_rate': vocal_data.get('speaking_rate'),
                    'vocal_quality': vocal_data.get('quality')
                }
            
            # Spectral characteristics for emotion
            if 'spectral_analysis' in features:
                spectral = features['spectral_analysis']
                indicators['spectral_emotions'] = {
                    'brightness': spectral.get('spectral_centroid', 0),
                    'warmth': spectral.get('spectral_rolloff', 0),
                    'roughness': spectral.get('spectral_roughness', 0)
                }
            
            # Rhythm patterns
            if 'rhythm_analysis' in features:
                rhythm = features['rhythm_analysis']
                indicators['rhythm_emotions'] = {
                    'regularity': rhythm.get('regularity', 0),
                    'complexity': rhythm.get('complexity', 0),
                    'groove': rhythm.get('groove_strength', 0)
                }
            
        except Exception as e:
            logger.error(f"Error extracting audio emotion indicators: {e}")
        
        return indicators

    def _extract_text_emotion_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract text-specific emotion indicators."""        indicators = {}
        
        try:
            # Sentiment details
            if 'sentiment_analysis' in classifications:
                sentiment = classifications['sentiment_analysis']
                indicators['sentiment_scores'] = sentiment.get('sentiment_scores', {})
                indicators['sentiment_intensity'] = sentiment.get('intensity', 0)
            
            # Emotion keywords from text
            if 'emotion_keywords' in features:
                emotion_kw = features['emotion_keywords']
                indicators['textual_emotions'] = emotion_kw.get('emotions', [])
            
            # Topic analysis for emotional context
            if 'topic_extraction' in features:
                topics = features['topic_extraction'].get('all_topics', [])
                emotional_topics = []
                for topic in topics:
                    # Check if topic relates to emotions
                    if any(emotion in topic.lower() for emotion in ['love', 'death', 'loss', 'success', 'failure']):
                        emotional_topics.append(topic)
                indicators['emotional_topics'] = emotional_topics
            
            # Language style analysis
            if 'style_analysis' in features:
                style = features['style_analysis']
                indicators['writing_style'] = {
                    'formality': style.get('formality_level', 0),
                    'intensity': style.get('intensity_level', 0),
                    'emotion_density': style.get('emotion_density', 0)
                }
            
            # Punctuation and caps analysis (for intensity)
            text_content = features.get('raw_text', '')
            if text_content:
                indicators['text_intensity_markers'] = {
                    'exclamation_marks': text_content.count('!'),
                    'question_marks': text_content.count('?'),
                    'caps_ratio': sum(1 for c in text_content if c.isupper()) / len(text_content) if text_content else 0,
                    'ellipsis_count': text_content.count('...')
                }
            
        except Exception as e:
            logger.error(f"Error extracting text emotion indicators: {e}")
        
        return indicators

    def _extract_visual_emotion_indicators(self, classifications: Dict, features: Dict) -> Dict[str, Any]:
        """Extract visual-specific emotion indicators."""        indicators = {}
        
        try:
            # Color analysis for emotions
            if 'color_analysis' in features:
                color_data = features['color_analysis']
                dominant_colors = color_data.get('dominant_colors', [])
                
                # Analyze emotional impact of colors
                emotional_colors = self._analyze_color_emotions(dominant_colors)
                indicators['color_emotions'] = emotional_colors
                indicators['color_palette'] = [color.get('hex', '') for color in dominant_colors[:5]]
            
            # Face detection and expression analysis
            if 'face_detection' in classifications:
                face_data = classifications['face_detection']
                faces = face_data.get('faces', [])
                
                facial_emotions = []
                for face in faces:
                    if 'emotions' in face:
                        facial_emotions.extend(face['emotions'])
                    if 'expression' in face:
                        facial_emotions.append(face['expression'])
                
                indicators['facial_expressions'] = facial_emotions
            
            # Scene analysis for emotional context
            if 'scene_analysis' in classifications:
                scene = classifications['scene_analysis']
                scene_type = scene.get('scene_type', '')
                
                # Map scenes to emotions
                scene_emotions = self._map_scene_to_emotions(scene_type)
                indicators['scene_emotions'] = scene_emotions
            
            # Object detection for emotional context
            if 'object_detection' in classifications:
                objects = classifications['object_detection'].get('objects', [])
                emotional_objects = []
                
                for obj in objects:
                    if isinstance(obj, dict):
                        obj_name = obj.get('object', '').lower()
                        # Check for emotionally charged objects
                        if any(emotional_obj in obj_name for emotional_obj in ['smile', 'tear', 'flower', 'weapon', 'heart']):
                            emotional_objects.append(obj_name)
                
                indicators['emotional_objects'] = emotional_objects
            
            # Composition analysis
            if 'composition_analysis' in features:
                composition = features['composition_analysis']
                indicators['visual_composition'] = {
                    'balance': composition.get('balance', 0),
                    'movement': composition.get('movement_direction', 'static'),
                    'focus': composition.get('focal_point_strength', 0)
                }
            
        except Exception as e:
            logger.error(f"Error extracting visual emotion indicators: {e}")
        
        return indicators

    def _analyze_primary_emotions(
        self, 
        indicators: Dict[str, Any], 
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze primary emotions from indicators."""        try:
            emotion_scores = {}
            emotion_keywords = []
            
            # Score each primary emotion
            for emotion, emotion_data in self.primary_emotions.items():
                score = 0
                
                # Keyword matching
                keywords = indicators.get('keywords', [])
                emotion_indicators = emotion_data.get('indicators', [])
                
                for keyword in keywords:
                    if keyword in emotion_indicators:
                        score += 0.4
                        emotion_keywords.append(keyword)
                    elif any(indicator in keyword or keyword in indicator for indicator in emotion_indicators):
                        score += 0.2
                        emotion_keywords.append(keyword)
                
                # Sentiment alignment
                sentiment = indicators.get('sentiment')
                if sentiment:
                    sentiment_emotion_mapping = {
                        'positive': ['joy', 'surprise', 'trust', 'anticipation'],
                        'negative': ['sadness', 'anger', 'fear', 'disgust'],
                        'neutral': ['trust']
                    }
                    
                    if emotion in sentiment_emotion_mapping.get(sentiment, []):
                        score += 0.3
                
                # Content type specific scoring
                if content_type == 'audio':
                    score += self._score_audio_emotion(emotion, indicators)
                elif content_type == 'text':
                    score += self._score_text_emotion(emotion, indicators)
                elif content_type in ['image', 'video']:
                    score += self._score_visual_emotion(emotion, indicators)
                
                # Existing emotion alignment
                if 'existing_emotions' in indicators:
                    existing_emotions = indicators['existing_emotions']
                    if emotion in [e.lower() for e in existing_emotions]:
                        score += 0.5
                
                if score > 0:
                    emotion_scores[emotion] = min(score, 1.0)
            
            # Determine primary emotion
            primary_emotion = None
            primary_confidence = 0
            
            if emotion_scores:
                primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
                primary_confidence = primary_emotion[1]
                primary_emotion = primary_emotion[0]
            
            return {
                'primary_emotion': primary_emotion,
                'emotion_scores': emotion_scores,
                'emotional_keywords': list(set(emotion_keywords)),
                'confidence_scores': {'primary_emotion': primary_confidence}
            }
            
        except Exception as e:
            logger.error(f"Error analyzing primary emotions: {e}")
            return {}

    def _score_audio_emotion(self, emotion: str, indicators: Dict[str, Any]) -> float:
        """Score emotion based on audio characteristics."""        score = 0
        emotion_data = self.primary_emotions[emotion]
        audio_features = emotion_data.get('audio_features', [])
        
        try:
            # Tempo-based scoring
            tempo = indicators.get('tempo')
            if tempo:
                if emotion == 'joy' and tempo > 120:
                    score += 0.3
                elif emotion == 'sadness' and tempo < 80:
                    score += 0.3
                elif emotion == 'anger' and tempo > 140:
                    score += 0.3
                elif emotion == 'fear' and 60 < tempo < 100:
                    score += 0.2
            
            # Key mode scoring
            key_mode = indicators.get('key_mode')
            if key_mode:
                if key_mode == 'major' and emotion in ['joy', 'surprise', 'trust']:
                    score += 0.3
                elif key_mode == 'minor' and emotion in ['sadness', 'fear', 'anger']:
                    score += 0.3
            
            # Energy level scoring
            energy_level = indicators.get('energy_level')
            if energy_level is not None:
                if energy_level > 0.7 and emotion in ['joy', 'anger', 'surprise']:
                    score += 0.2
                elif energy_level < 0.3 and emotion in ['sadness', 'trust']:
                    score += 0.2
            
            # Vocal characteristics
            vocal_chars = indicators.get('vocal_characteristics', {})
            if vocal_chars:
                pitch_variance = vocal_chars.get('pitch_variance', 0)
                if pitch_variance > 0.7 and emotion in ['anger', 'fear', 'surprise']:
                    score += 0.2
                elif pitch_variance < 0.3 and emotion in ['sadness', 'trust']:
                    score += 0.2
            
        except Exception as e:
            logger.error(f"Error scoring audio emotion {emotion}: {e}")
        
        return score

    def _score_text_emotion(self, emotion: str, indicators: Dict[str, Any]) -> float:
        """Score emotion based on text characteristics."""        score = 0
        
        try:
            # Sentiment scores alignment
            sentiment_scores = indicators.get('sentiment_scores', {})
            if sentiment_scores:
                if emotion == 'joy' and sentiment_scores.get('positive', 0) > 0.7:
                    score += 0.4
                elif emotion == 'sadness' and sentiment_scores.get('negative', 0) > 0.7:
                    score += 0.4
                elif emotion == 'anger' and sentiment_scores.get('negative', 0) > 0.8:
                    score += 0.3
            
            # Textual emotions
            textual_emotions = indicators.get('textual_emotions', [])
            if emotion in [e.lower() for e in textual_emotions]:
                score += 0.5
            
            # Text intensity markers
            intensity_markers = indicators.get('text_intensity_markers', {})
            if intensity_markers:
                exclamation_count = intensity_markers.get('exclamation_marks', 0)
                caps_ratio = intensity_markers.get('caps_ratio', 0)
                
                if emotion in ['anger', 'surprise', 'joy'] and (exclamation_count > 0 or caps_ratio > 0.1):
                    score += 0.2
                elif emotion in ['sadness', 'fear'] and intensity_markers.get('ellipsis_count', 0) > 0:
                    score += 0.2
            
            # Writing style
            writing_style = indicators.get('writing_style', {})
            if writing_style:
                emotion_density = writing_style.get('emotion_density', 0)
                if emotion_density > 0.5:
                    score += 0.2
            
        except Exception as e:
            logger.error(f"Error scoring text emotion {emotion}: {e}")
        
        return score

    def _score_visual_emotion(self, emotion: str, indicators: Dict[str, Any]) -> float:
        """Score emotion based on visual characteristics."""        score = 0
        
        try:
            # Color emotions
            color_emotions = indicators.get('color_emotions', {})
            if emotion in color_emotions:
                score += color_emotions[emotion] * 0.4
            
            # Facial expressions
            facial_expressions = indicators.get('facial_expressions', [])
            if emotion in [expr.lower() for expr in facial_expressions]:
                score += 0.5
            
            # Scene emotions
            scene_emotions = indicators.get('scene_emotions', [])
            if emotion in scene_emotions:
                score += 0.3
            
            # Emotional objects
            emotional_objects = indicators.get('emotional_objects', [])
            emotion_object_mapping = {
                'joy': ['smile', 'flower', 'heart', 'celebration'],
                'sadness': ['tear', 'rain', 'grave'],
                'anger': ['weapon', 'fire', 'storm'],
                'fear': ['darkness', 'shadow', 'weapon']
            }
            
            mapped_objects = emotion_object_mapping.get(emotion, [])
            for obj in emotional_objects:
                if any(mapped_obj in obj for mapped_obj in mapped_objects):
                    score += 0.2
            
            # Visual composition
            composition = indicators.get('visual_composition', {})
            if composition:
                balance = composition.get('balance', 0)
                movement = composition.get('movement', 'static')
                
                if emotion == 'trust' and balance > 0.7:
                    score += 0.2
                elif emotion in ['anger', 'fear'] and movement in ['chaotic', 'aggressive']:
                    score += 0.2
                elif emotion in ['joy', 'surprise'] and movement in ['upward', 'dynamic']:
                    score += 0.2
            
        except Exception as e:
            logger.error(f"Error scoring visual emotion {emotion}: {e}")
        
        return score

    def _analyze_complex_emotions(
        self, 
        indicators: Dict[str, Any], 
        emotion_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze complex emotions from primary emotion combinations."""        try:
            complex_emotions = {}
            
            for complex_emotion, emotion_data in self.complex_emotions.items():
                components = emotion_data.get('components', [])
                
                # Calculate complex emotion score
                component_scores = []
                for component_emotion, weight in components:
                    if component_emotion in emotion_scores:
                        component_scores.append(emotion_scores[component_emotion] * weight)
                
                if component_scores:
                    # Complex emotion score is the weighted average of components
                    complex_score = sum(component_scores) / len(components)
                    
                    # Bonus for keyword matching
                    keywords = indicators.get('keywords', [])
                    emotion_indicators = emotion_data.get('indicators', [])
                    
                    keyword_bonus = 0
                    for keyword in keywords:
                        if keyword in emotion_indicators:
                            keyword_bonus += 0.2
                    
                    final_score = min(complex_score + keyword_bonus, 1.0)
                    
                    if final_score > self.config['min_confidence_threshold']:
                        complex_emotions[complex_emotion] = {
                            'score': final_score,
                            'components': dict(components),
                            'component_scores': dict(zip([c[0] for c in components], component_scores)),
                            'valence': emotion_data.get('valence', 0.5),
                            'arousal': emotion_data.get('arousal', 0.5)
                        }
            
            return complex_emotions
            
        except Exception as e:
            logger.error(f"Error analyzing complex emotions: {e}")
            return {}

    def _determine_mood_state(
        self, 
        emotion_scores: Dict[str, float], 
        indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine overall mood state from emotions."""        try:
            mood_scores = {}
            
            for mood_state, mood_data in self.mood_states.items():
                dominant_emotions = mood_data.get('dominant_emotions', [])
                
                # Calculate mood score based on dominant emotions
                mood_score = 0
                emotion_matches = 0
                
                for emotion in dominant_emotions:
                    if emotion in emotion_scores:
                        mood_score += emotion_scores[emotion]
                        emotion_matches += 1
                
                if emotion_matches > 0:
                    mood_score = mood_score / emotion_matches
                    
                    # Intensity adjustment
                    intensity = mood_data.get('intensity', 'moderate')
                    if intensity == 'high':
                        # High intensity moods require higher emotion scores
                        mood_score *= 0.8 if mood_score < 0.7 else 1.1
                    elif intensity == 'low_to_moderate':
                        # Low intensity moods are easier to achieve
                        mood_score *= 1.2
                    
                    if mood_score > 0:
                        mood_scores[mood_state] = min(mood_score, 1.0)
            
            # Determine primary mood
            primary_mood = None
            mood_confidence = 0
            
            if mood_scores:
                primary_mood = max(mood_scores.items(), key=lambda x: x[1])
                mood_confidence = primary_mood[1]
                primary_mood = primary_mood[0]
            
            return {
                'mood_state': primary_mood,
                'mood_scores': mood_scores,
                'confidence_scores': {'mood_state': mood_confidence}
            }
            
        except Exception as e:
            logger.error(f"Error determining mood state: {e}")
            return {}

    def _calculate_valence_arousal(self, emotion_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate valence and arousal dimensions."""        try:
            if not emotion_scores:
                return {'valence': 0.5, 'arousal': 0.5}
            
            total_valence = 0
            total_arousal = 0
            total_weight = 0
            
            for emotion, score in emotion_scores.items():
                if emotion in self.primary_emotions:
                    emotion_data = self.primary_emotions[emotion]
                    valence = emotion_data.get('valence', 0.5)
                    arousal = emotion_data.get('arousal', 0.5)
                    
                    total_valence += valence * score
                    total_arousal += arousal * score
                    total_weight += score
            
            if total_weight > 0:
                avg_valence = total_valence / total_weight
                avg_arousal = total_arousal / total_weight
            else:
                avg_valence = 0.5
                avg_arousal = 0.5
            
            return {
                'valence': avg_valence,
                'arousal': avg_arousal,
                'quadrant': self._get_emotion_quadrant(avg_valence, avg_arousal)
            }
            
        except Exception as e:
            logger.error(f"Error calculating valence-arousal: {e}")
            return {'valence': 0.5, 'arousal': 0.5}

    def _get_emotion_quadrant(self, valence: float, arousal: float) -> str:
        """Get emotion quadrant based on valence-arousal."""        if valence >= 0.5 and arousal >= 0.5:
            return 'high_positive'  # Joy, excitement
        elif valence >= 0.5 and arousal < 0.5:
            return 'low_positive'   # Calm, content
        elif valence < 0.5 and arousal >= 0.5:
            return 'high_negative'  # Anger, fear
        else:
            return 'low_negative'   # Sadness, depression

    def _analyze_temporal_emotions(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal emotion patterns."""        try:
            temporal_analysis = {
                'emotion_stability': 0.5,
                'emotion_intensity_trend': 'stable',
                'dominant_emotion_duration': 'unknown'
            }
            
            # This would require time-series data in a real implementation
            # For now, we'll analyze indicators for temporal cues
            
            # Energy level changes might indicate emotion transitions
            energy_level = indicators.get('energy_level')
            if energy_level is not None:
                if energy_level > 0.8:
                    temporal_analysis['emotion_intensity_trend'] = 'increasing'
                elif energy_level < 0.3:
                    temporal_analysis['emotion_intensity_trend'] = 'decreasing'
            
            # Tempo changes (for audio)
            tempo = indicators.get('tempo')
            if tempo:
                # Fast tempo might indicate short-duration intense emotions
                if tempo > 140:
                    temporal_analysis['dominant_emotion_duration'] = 'short'
                elif tempo < 80:
                    temporal_analysis['dominant_emotion_duration'] = 'extended'
            
            return temporal_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing temporal emotions: {e}")
            return {}

    def _analyze_cultural_context(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cultural context of emotions."""        try:
            cultural_analysis = {
                'detected_culture': None,
                'cultural_confidence': 0.0,
                'cultural_adaptations': []
            }
            
            # Language-based cultural detection
            language = indicators.get('language')
            if language:
                culture_mapping = {
                    'english': 'western',
                    'spanish': 'latin',
                    'mandarin': 'eastern',
                    'japanese': 'eastern',
                    'korean': 'eastern',
                    'arabic': 'middle_eastern',
                    'french': 'western',
                    'german': 'western',
                    'swedish': 'nordic',
                    'norwegian': 'nordic'
                }
                
                detected_culture = culture_mapping.get(language.lower())
                if detected_culture:
                    cultural_analysis['detected_culture'] = detected_culture
                    cultural_analysis['cultural_confidence'] = 0.7
            
            # Cultural markers from content
            cultural_markers = indicators.get('cultural_markers', [])
            if cultural_markers:
                # Analyze markers for cultural indicators
                for marker in cultural_markers:
                    for culture, culture_data in self.cultural_variations.items():
                        if culture.lower() in marker.lower():
                            cultural_analysis['detected_culture'] = culture
                            cultural_analysis['cultural_confidence'] += 0.2
            
            # Suggest cultural adaptations
            if cultural_analysis['detected_culture']:
                culture_data = self.cultural_variations.get(cultural_analysis['detected_culture'], {})
                cultural_analysis['cultural_adaptations'] = [
                    f"Expression style: {culture_data.get('emotion_expression', 'unknown')}",
                    f"Intensity preference: {culture_data.get('intensity_preference', 'unknown')}"
                ]
            
            return cultural_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cultural context: {e}")
            return {}

    def _calculate_emotion_complexity(self, emotion_scores: Dict[str, float]) -> float:
        """Calculate emotion complexity score."""        try:
            if not emotion_scores:
                return 0.0
            
            # Number of emotions above threshold
            significant_emotions = len([score for score in emotion_scores.values() if score > 0.3])
            
            # Entropy-based complexity
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                normalized_scores = [score / total_score for score in emotion_scores.values()]
                entropy = -sum(p * np.log2(p) for p in normalized_scores if p > 0)
                max_entropy = np.log2(len(emotion_scores))
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            else:
                normalized_entropy = 0
            
            # Combine factors
            complexity = (significant_emotions / 8) * 0.5 + normalized_entropy * 0.5
            
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating emotion complexity: {e}")
            return 0.0

    def _calculate_overall_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in mood analysis."""        try:
            confidence_scores = analysis.get('confidence_scores', {})
            
            # Weight factors
            primary_emotion_conf = confidence_scores.get('primary_emotion', 0) * 0.5
            mood_state_conf = confidence_scores.get('mood_state', 0) * 0.3
            
            # Indicator strength
            emotion_indicators = analysis.get('emotion_indicators', {})
            indicator_strength = 0
            
            # Count available indicators
            available_indicators = sum(1 for key, value in emotion_indicators.items() 
                                     if value is not None and value != [] and value != {})
            max_indicators = 10  # Expected number of indicator types
            indicator_strength = available_indicators / max_indicators
            
            # Emotion complexity bonus (more emotions = more confidence in analysis)
            complexity_bonus = analysis.get('emotion_complexity', 0) * 0.1
            
            overall_confidence = primary_emotion_conf + mood_state_conf + (indicator_strength * 0.2) + complexity_bonus
            
            return min(overall_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.0

    # Helper methods
    def _analyze_color_emotions(self, dominant_colors: List[Dict]) -> Dict[str, float]:
        """Analyze emotional impact of colors."""        color_emotions = defaultdict(float)
        
        try:
            color_emotion_mapping = {
                'red': {'anger': 0.7, 'passion': 0.6, 'energy': 0.5},
                'blue': {'trust': 0.6, 'calm': 0.7, 'sadness': 0.4},
                'yellow': {'joy': 0.8, 'energy': 0.6, 'optimism': 0.7},
                'green': {'trust': 0.5, 'calm': 0.6, 'nature': 0.7},
                'purple': {'mystery': 0.6, 'luxury': 0.5, 'creativity': 0.6},
                'orange': {'energy': 0.7, 'warmth': 0.6, 'enthusiasm': 0.6},
                'black': {'power': 0.6, 'mystery': 0.7, 'elegance': 0.5},
                'white': {'purity': 0.8, 'peace': 0.7, 'simplicity': 0.6}
            }
            
            for color_data in dominant_colors[:3]:  # Top 3 colors
                hex_color = color_data.get('hex', '').lower()
                percentage = color_data.get('percentage', 0) / 100
                
                # Simple color name detection (would need more sophisticated mapping)
                color_name = self._hex_to_color_name(hex_color)
                
                if color_name in color_emotion_mapping:
                    emotions = color_emotion_mapping[color_name]
                    for emotion, strength in emotions.items():
                        color_emotions[emotion] += strength * percentage
            
            return dict(color_emotions)
            
        except Exception as e:
            logger.error(f"Error analyzing color emotions: {e}")
            return {}

    def _hex_to_color_name(self, hex_color: str) -> str:
        """Convert hex color to basic color name."""        # Simplified color mapping
        try:
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Simple color classification
            if r > 200 and g < 100 and b < 100:
                return 'red'
            elif r < 100 and g < 100 and b > 200:
                return 'blue'
            elif r > 200 and g > 200 and b < 100:
                return 'yellow'
            elif r < 100 and g > 200 and b < 100:
                return 'green'
            elif r > 150 and g < 100 and b > 150:
                return 'purple'
            elif r > 200 and g > 100 and b < 100:
                return 'orange'
            elif r < 50 and g < 50 and b < 50:
                return 'black'
            elif r > 200 and g > 200 and b > 200:
                return 'white'
            else:
                return 'mixed'
                
        except Exception:
            return 'unknown'

    def _map_scene_to_emotions(self, scene_type: str) -> List[str]:
        """Map scene types to emotions."""        scene_emotion_mapping = {
            'beach': ['joy', 'calm', 'relaxation'],
            'forest': ['peace', 'tranquility', 'mystery'],
            'city': ['energy', 'excitement', 'stress'],
            'sunset': ['romance', 'peace', 'nostalgia'],
            'storm': ['fear', 'power', 'chaos'],
            'party': ['joy', 'excitement', 'social'],
            'funeral': ['sadness', 'grief', 'solemnity'],
            'wedding': ['joy', 'love', 'celebration']
        }
        
        return scene_emotion_mapping.get(scene_type.lower(), [])

    def _get_timestamp(self) -> str:
        """Get current timestamp."""        from datetime import datetime
        return datetime.now().isoformat()

    def get_emotion_info(self, emotion: str) -> Dict[str, Any]:
        """Get detailed information about a specific emotion."""        try:
            emotion = emotion.lower()
            
            # Check primary emotions
            if emotion in self.primary_emotions:
                emotion_data = self.primary_emotions[emotion].copy()
                emotion_data['emotion_name'] = emotion
                emotion_data['emotion_type'] = 'primary'
                return emotion_data
            
            # Check complex emotions
            if emotion in self.complex_emotions:
                emotion_data = self.complex_emotions[emotion].copy()
                emotion_data['emotion_name'] = emotion
                emotion_data['emotion_type'] = 'complex'
                return emotion_data
            
            return {'error': f'Emotion "{emotion}" not found in database'}
            
        except Exception as e:
            logger.error(f"Error getting emotion info: {e}")
            return {'error': str(e)}

    def get_mood_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations based on mood analysis."""        try:
            recommendations = []
            
            primary_emotion = analysis.get('primary_emotion')
            mood_state = analysis.get('mood_state')
            valence_arousal = analysis.get('valence_arousal', {})
            
            # Emotion-based recommendations
            if primary_emotion == 'sadness':
                recommendations.extend([
                    "Consider uplifting content or activities",
                    "Connect with supportive community",
                    "Explore creative expression as emotional outlet"
                ])
            elif primary_emotion == 'anger':
                recommendations.extend([
                    "Consider calming activities before content creation",
                    "Channel intensity into powerful creative work",
                    "Ensure content aligns with brand values"
                ])
            elif primary_emotion == 'joy':
                recommendations.extend([
                    "Great time for engaging, energetic content",
                    "Consider sharing positive experiences",
                    "Leverage high energy for creative projects"
                ])
            
            # Valence-arousal based recommendations
            quadrant = valence_arousal.get('quadrant')
            if quadrant == 'high_positive':
                recommendations.append("Perfect energy for dynamic, engaging content")
            elif quadrant == 'low_positive':
                recommendations.append("Good state for thoughtful, reflective content")
            elif quadrant == 'high_negative':
                recommendations.append("Consider waiting or channeling intensity carefully")
            elif quadrant == 'low_negative':
                recommendations.append("May benefit from uplifting activities first")
            
            # Complexity-based recommendations
            complexity = analysis.get('emotion_complexity', 0)
            if complexity > 0.7:
                recommendations.append("Complex emotional state - good for nuanced, artistic content")
            
            return recommendations[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Error generating mood recommendations: {e}")
            return []

    def compare_moods(self, analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two mood analyses."""        try:
            comparison = {
                'emotion_similarity': 0.0,
                'valence_difference': 0.0,
                'arousal_difference': 0.0,
                'mood_compatibility': 'unknown',
                'dominant_emotion_match': False
            }
            
            # Compare primary emotions
            emotion1 = analysis1.get('primary_emotion')
            emotion2 = analysis2.get('primary_emotion')
            
            if emotion1 and emotion2:
                comparison['dominant_emotion_match'] = emotion1 == emotion2
            
            # Compare emotion scores
            scores1 = analysis1.get('emotion_scores', {})
            scores2 = analysis2.get('emotion_scores', {})
            
            if scores1 and scores2:
                # Calculate cosine similarity
                all_emotions = set(scores1.keys()) | set(scores2.keys())
                vec1 = [scores1.get(emotion, 0) for emotion in all_emotions]
                vec2 = [scores2.get(emotion, 0) for emotion in all_emotions]
                
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = sum(a * a for a in vec1) ** 0.5
                norm2 = sum(b * b for b in vec2) ** 0.5
                
                if norm1 > 0 and norm2 > 0:
                    comparison['emotion_similarity'] = dot_product / (norm1 * norm2)
            
            # Compare valence-arousal
            va1 = analysis1.get('valence_arousal', {})
            va2 = analysis2.get('valence_arousal', {})
            
            if va1 and va2:
                comparison['valence_difference'] = abs(va1.get('valence', 0.5) - va2.get('valence', 0.5))
                comparison['arousal_difference'] = abs(va1.get('arousal', 0.5) - va2.get('arousal', 0.5))
            
            # Determine compatibility
            if comparison['emotion_similarity'] > 0.7:
                comparison['mood_compatibility'] = 'high'
            elif comparison['emotion_similarity'] > 0.4:
                comparison['mood_compatibility'] = 'moderate'
            else:
                comparison['mood_compatibility'] = 'low'
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing moods: {e}")
            return {}

    def get_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary of mood analysis."""        try:
            summary_parts = []
            
            # Primary emotion
            primary_emotion = analysis.get('primary_emotion')
            if primary_emotion:
                confidence = analysis.get('confidence_scores', {}).get('primary_emotion', 0)
                summary_parts.append(f"Primary emotion: {primary_emotion} ({confidence:.2f})")
            
            # Mood state
            mood_state = analysis.get('mood_state')
            if mood_state:
                summary_parts.append(f"Mood: {mood_state}")
            
            # Valence-arousal
            va = analysis.get('valence_arousal', {})
            if va:
                valence = va.get('valence', 0.5)
                arousal = va.get('arousal', 0.5)
                quadrant = va.get('quadrant', 'neutral')
                summary_parts.append(f"Energy: {quadrant} (valence: {valence:.2f}, arousal: {arousal:.2f})")
            
            # Complexity
            complexity = analysis.get('emotion_complexity', 0)
            if complexity > 0.7:
                summary_parts.append(f"Complex emotional state ({complexity:.2f})")
            
            # Cultural context
            cultural = analysis.get('cultural_context', {})
            detected_culture = cultural.get('detected_culture')
            if detected_culture:
                summary_parts.append(f"Cultural context: {detected_culture}")
            
            return " | ".join(summary_parts) if summary_parts else "No mood detected"
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {e}")
            return "Summary generation failed"
