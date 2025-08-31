"""Quality Assessor

Professional content quality assessment system with comprehensive metrics
for multimedia content evaluation and scoring.

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
from collections import defaultdict
import re
import math

from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class QualityAssessor:
    """    Enterprise-grade quality assessment system for multimedia content.
    
    Features:
    - Multi-dimensional quality scoring
    - Technical quality metrics
    - Content quality evaluation
    - Professional standards compliance
    - Platform-specific optimization scores
    - Quality improvement recommendations
    - Benchmarking against industry standards
    """    
    def __init__(self):
        """Initialize quality assessor."""        self.settings = get_settings()
        
        # Initialize quality frameworks and standards
        self._init_quality_frameworks()
        
        # Assessment configuration
        self.config = {
            'min_quality_threshold': 0.6,
            'professional_threshold': 0.8,
            'expert_threshold': 0.9,
            'weight_technical': 0.4,
            'weight_content': 0.4,
            'weight_engagement': 0.2,
            'enable_platform_specific': True,
            'enable_benchmarking': True
        }

    def _init_quality_frameworks(self):
        """Initialize quality assessment frameworks."""        
        # Technical quality metrics by content type
        self.technical_metrics = {
            'audio': {
                'sample_rate': {'min': 44100, 'optimal': 48000, 'max': 192000},
                'bit_depth': {'min': 16, 'optimal': 24, 'max': 32},
                'dynamic_range': {'min': 20, 'optimal': 40, 'max': 60},
                'noise_floor': {'max': -60, 'optimal': -80, 'excellent': -100},
                'frequency_response': {'min': 20, 'max': 20000},
                'distortion_thd': {'max': 0.1, 'optimal': 0.01, 'excellent': 0.001},
                'peak_level': {'max': -1, 'optimal': -6, 'conservative': -12},
                'loudness_lufs': {'min': -30, 'optimal': -16, 'max': -6}
            },
            'video': {
                'resolution': {
                    'sd': {'width': 720, 'height': 480, 'score': 0.3},
                    'hd': {'width': 1280, 'height': 720, 'score': 0.6},
                    'full_hd': {'width': 1920, 'height': 1080, 'score': 0.8},
                    '4k': {'width': 3840, 'height': 2160, 'score': 1.0},
                    '8k': {'width': 7680, 'height': 4320, 'score': 1.0}
                },
                'frame_rate': {'min': 24, 'optimal': 30, 'smooth': 60, 'max': 120},
                'bitrate': {'min': 1000, 'optimal': 5000, 'high': 10000},
                'compression': {'max_artifacts': 0.1, 'optimal': 0.05},
                'color_depth': {'min': 8, 'optimal': 10, 'max': 12},
                'stabilization': {'max_shake': 2.0, 'optimal': 0.5}
            },
            'image': {
                'resolution': {'min': 1000, 'good': 2000, 'excellent': 4000},
                'dpi': {'min': 72, 'print': 300, 'professional': 600},
                'compression': {'max_artifacts': 0.1, 'optimal': 0.05},
                'noise_level': {'max': 0.2, 'optimal': 0.05},
                'sharpness': {'min': 0.3, 'optimal': 0.7, 'max': 1.0},
                'exposure': {'min': -2, 'optimal': 0, 'max': 2},
                'color_accuracy': {'min': 0.7, 'optimal': 0.9, 'max': 1.0}
            },
            'text': {
                'readability': {'min': 60, 'good': 80, 'excellent': 90},
                'grammar_score': {'min': 0.8, 'optimal': 0.95, 'max': 1.0},
                'spelling_accuracy': {'min': 0.95, 'optimal': 0.99, 'max': 1.0},
                'sentence_length': {'min': 10, 'optimal': 20, 'max': 30},
                'paragraph_length': {'min': 50, 'optimal': 150, 'max': 300},
                'vocabulary_diversity': {'min': 0.5, 'optimal': 0.7, 'max': 1.0}
            }
        }
        
        # Content quality dimensions
        self.content_dimensions = {
            'creativity': {
                'originality': {'weight': 0.3, 'metrics': ['uniqueness', 'innovation', 'fresh_perspective']},
                'artistic_value': {'weight': 0.25, 'metrics': ['aesthetic_appeal', 'composition', 'style']},
                'concept_strength': {'weight': 0.25, 'metrics': ['idea_clarity', 'message_coherence', 'theme_development']},
                'execution_quality': {'weight': 0.2, 'metrics': ['technical_skill', 'attention_detail', 'polish']}
            },
            'engagement': {
                'attention_grabbing': {'weight': 0.3, 'metrics': ['hook_strength', 'visual_appeal', 'curiosity_factor']},
                'emotional_impact': {'weight': 0.25, 'metrics': ['emotional_resonance', 'mood_creation', 'feeling_evocation']},
                'memorability': {'weight': 0.25, 'metrics': ['distinctive_elements', 'memorable_moments', 'lasting_impression']},
                'shareability': {'weight': 0.2, 'metrics': ['viral_potential', 'discussion_worthy', 'social_appeal']}
            },
            'professionalism': {
                'production_value': {'weight': 0.3, 'metrics': ['technical_execution', 'polish_level', 'professional_standards']},
                'brand_consistency': {'weight': 0.25, 'metrics': ['style_consistency', 'message_alignment', 'visual_identity']},
                'market_readiness': {'weight': 0.25, 'metrics': ['commercial_viability', 'audience_appropriateness', 'platform_optimization']},
                'competitive_advantage': {'weight': 0.2, 'metrics': ['unique_selling_point', 'differentiation', 'market_position']}
            }
        }
        
        # Platform-specific quality standards
        self.platform_standards = {
            'instagram': {
                'image': {'aspect_ratios': ['1:1', '4:5', '16:9'], 'min_resolution': [1080, 1080]},
                'video': {'max_duration': 60, 'aspect_ratios': ['9:16', '1:1', '16:9'], 'min_resolution': [1080, 1920]},
                'quality_factors': ['visual_appeal', 'hashtag_optimization', 'trend_relevance']
            },
            'youtube': {
                'video': {'min_resolution': [1280, 720], 'optimal_duration': [600, 1200], 'thumbnails': True},
                'audio': {'min_quality': 128, 'optimal_quality': 320},
                'quality_factors': ['watch_time_potential', 'click_through_rate', 'retention_curve']
            },
            'tiktok': {
                'video': {'aspect_ratio': '9:16', 'max_duration': 180, 'min_resolution': [720, 1280]},
                'quality_factors': ['trend_alignment', 'viral_potential', 'engagement_rate']
            },
            'spotify': {
                'audio': {'min_quality': 320, 'loudness_target': -14, 'format': 'ogg'},
                'quality_factors': ['mix_quality', 'mastering_level', 'genre_compliance']
            },
            'podcast': {
                'audio': {'min_quality': 128, 'optimal_quality': 256, 'mono_acceptable': True},
                'quality_factors': ['voice_clarity', 'background_noise', 'consistency']
            }
        }
        
        # Industry benchmarks
        self.industry_benchmarks = {
            'music_production': {
                'amateur': {'overall_score': 0.4, 'technical': 0.3, 'content': 0.5},
                'semi_professional': {'overall_score': 0.6, 'technical': 0.6, 'content': 0.6},
                'professional': {'overall_score': 0.8, 'technical': 0.8, 'content': 0.8},
                'industry_standard': {'overall_score': 0.9, 'technical': 0.9, 'content': 0.9}
            },
            'video_production': {
                'amateur': {'overall_score': 0.3, 'technical': 0.3, 'content': 0.4},
                'semi_professional': {'overall_score': 0.6, 'technical': 0.6, 'content': 0.6},
                'professional': {'overall_score': 0.8, 'technical': 0.8, 'content': 0.8},
                'broadcast_quality': {'overall_score': 0.95, 'technical': 0.95, 'content': 0.9}
            },
            'photography': {
                'amateur': {'overall_score': 0.4, 'technical': 0.3, 'content': 0.5},
                'enthusiast': {'overall_score': 0.6, 'technical': 0.6, 'content': 0.6},
                'professional': {'overall_score': 0.8, 'technical': 0.8, 'content': 0.8},
                'gallery_quality': {'overall_score': 0.95, 'technical': 0.9, 'content': 1.0}
            },
            'content_writing': {
                'amateur': {'overall_score': 0.4, 'technical': 0.5, 'content': 0.4},
                'blogger': {'overall_score': 0.6, 'technical': 0.7, 'content': 0.6},
                'professional': {'overall_score': 0.8, 'technical': 0.8, 'content': 0.8},
                'publication_ready': {'overall_score': 0.9, 'technical': 0.9, 'content': 0.9}
            }
        }

    @cache_result(ttl=1800)
    @track_performance
    def assess_quality(
        self, 
        content_data: Dict[str, Any], 
        content_type: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Comprehensive quality assessment of content.
        
        Args:
            content_data: Analyzed content data
            content_type: Type of content (audio, video, image, text)
            options: Assessment options
            
        Returns:
            Detailed quality assessment results
        """        try:
            if not content_data:
                raise ClassificationError("No content data provided")
            
            # Initialize assessment results
            assessment = {
                'content_type': content_type,
                'timestamp': self._get_timestamp(),
                'overall_score': 0.0,
                'technical_score': 0.0,
                'content_score': 0.0,
                'engagement_score': 0.0,
                'quality_level': 'unknown',
                'technical_metrics': {},
                'content_metrics': {},
                'platform_scores': {},
                'benchmark_comparison': {},
                'strengths': [],
                'weaknesses': [],
                'improvement_recommendations': [],
                'quality_badges': []
            }
            
            # Technical quality assessment
            technical_assessment = self._assess_technical_quality(content_data, content_type)
            assessment['technical_score'] = technical_assessment['score']
            assessment['technical_metrics'] = technical_assessment['metrics']
            
            # Content quality assessment
            content_assessment = self._assess_content_quality(content_data, content_type)
            assessment['content_score'] = content_assessment['score']
            assessment['content_metrics'] = content_assessment['metrics']
            
            # Engagement potential assessment
            engagement_assessment = self._assess_engagement_potential(content_data, content_type)
            assessment['engagement_score'] = engagement_assessment['score']
            assessment['engagement_metrics'] = engagement_assessment['metrics']
            
            # Calculate overall score
            assessment['overall_score'] = self._calculate_overall_score(
                assessment['technical_score'],
                assessment['content_score'],
                assessment['engagement_score']
            )
            
            # Platform-specific assessments
            if self.config['enable_platform_specific']:
                platform_assessments = self._assess_platform_compliance(content_data, content_type)
                assessment['platform_scores'] = platform_assessments
            
            # Benchmark comparison
            if self.config['enable_benchmarking']:
                benchmark_analysis = self._compare_to_benchmarks(assessment, content_type)
                assessment['benchmark_comparison'] = benchmark_analysis
            
            # Determine quality level
            assessment['quality_level'] = self._determine_quality_level(assessment['overall_score'])
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(assessment)
            assessment['strengths'] = strengths
            assessment['weaknesses'] = weaknesses
            
            # Generate improvement recommendations
            assessment['improvement_recommendations'] = self._generate_recommendations(assessment, content_type)
            
            # Award quality badges
            assessment['quality_badges'] = self._award_quality_badges(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing quality: {e}")
            raise ClassificationError(f"Quality assessment failed: {e}")

    def _assess_technical_quality(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Assess technical quality metrics."""        try:
            assessment = {
                'score': 0.0,
                'metrics': {},
                'details': {}
            }
            
            if content_type not in self.technical_metrics:
                logger.warning(f"No technical metrics defined for content type: {content_type}")
                return assessment
            
            metrics = self.technical_metrics[content_type]
            technical_features = content_data.get('technical_analysis', {})
            
            metric_scores = {}
            
            if content_type == 'audio':
                metric_scores.update(self._assess_audio_technical(technical_features, metrics))
            elif content_type == 'video':
                metric_scores.update(self._assess_video_technical(technical_features, metrics))
            elif content_type == 'image':
                metric_scores.update(self._assess_image_technical(technical_features, metrics))
            elif content_type == 'text':
                metric_scores.update(self._assess_text_technical(technical_features, metrics))
            
            # Calculate overall technical score
            if metric_scores:
                assessment['score'] = np.mean(list(metric_scores.values()))
                assessment['metrics'] = metric_scores
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing technical quality: {e}")
            return {'score': 0.0, 'metrics': {}, 'details': {}}

    def _assess_audio_technical(self, features: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, float]:
        """Assess audio technical quality."""        scores = {}
        
        try:
            # Sample rate assessment
            sample_rate = features.get('sample_rate', 44100)
            if sample_rate >= metrics['sample_rate']['optimal']:
                scores['sample_rate'] = 1.0
            elif sample_rate >= metrics['sample_rate']['min']:
                scores['sample_rate'] = 0.7
            else:
                scores['sample_rate'] = 0.3
            
            # Bit depth assessment
            bit_depth = features.get('bit_depth', 16)
            if bit_depth >= metrics['bit_depth']['optimal']:
                scores['bit_depth'] = 1.0
            elif bit_depth >= metrics['bit_depth']['min']:
                scores['bit_depth'] = 0.7
            else:
                scores['bit_depth'] = 0.3
            
            # Dynamic range assessment
            dynamic_range = features.get('dynamic_range', 20)
            if dynamic_range >= metrics['dynamic_range']['optimal']:
                scores['dynamic_range'] = 1.0
            elif dynamic_range >= metrics['dynamic_range']['min']:
                scores['dynamic_range'] = 0.6
            else:
                scores['dynamic_range'] = 0.2
            
            # Noise floor assessment
            noise_floor = features.get('noise_floor', -60)
            if noise_floor <= metrics['noise_floor']['excellent']:
                scores['noise_floor'] = 1.0
            elif noise_floor <= metrics['noise_floor']['optimal']:
                scores['noise_floor'] = 0.8
            elif noise_floor <= metrics['noise_floor']['max']:
                scores['noise_floor'] = 0.5
            else:
                scores['noise_floor'] = 0.2
            
            # Distortion assessment
            thd = features.get('thd', 0.1)
            if thd <= metrics['distortion_thd']['excellent']:
                scores['distortion'] = 1.0
            elif thd <= metrics['distortion_thd']['optimal']:
                scores['distortion'] = 0.8
            elif thd <= metrics['distortion_thd']['max']:
                scores['distortion'] = 0.5
            else:
                scores['distortion'] = 0.2
            
            # Peak level assessment
            peak_level = features.get('peak_level', -6)
            if peak_level <= metrics['peak_level']['optimal']:
                scores['peak_level'] = 1.0
            elif peak_level <= metrics['peak_level']['max']:
                scores['peak_level'] = 0.8
            else:
                scores['peak_level'] = 0.3  # Clipping risk
            
            # Loudness assessment (LUFS)
            loudness = features.get('loudness_lufs', -16)
            target_lufs = metrics['loudness_lufs']['optimal']
            lufs_difference = abs(loudness - target_lufs)
            
            if lufs_difference <= 2:
                scores['loudness'] = 1.0
            elif lufs_difference <= 5:
                scores['loudness'] = 0.7
            elif lufs_difference <= 10:
                scores['loudness'] = 0.4
            else:
                scores['loudness'] = 0.2
            
        except Exception as e:
            logger.error(f"Error assessing audio technical quality: {e}")
        
        return scores

    def _assess_video_technical(self, features: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, float]:
        """Assess video technical quality."""        scores = {}
        
        try:
            # Resolution assessment
            width = features.get('width', 1280)
            height = features.get('height', 720)
            
            resolution_score = 0.5  # Default
            for res_name, res_data in metrics['resolution'].items():
                if width >= res_data['width'] and height >= res_data['height']:
                    resolution_score = max(resolution_score, res_data['score'])
            
            scores['resolution'] = resolution_score
            
            # Frame rate assessment
            frame_rate = features.get('frame_rate', 30)
            if frame_rate >= metrics['frame_rate']['smooth']:
                scores['frame_rate'] = 1.0
            elif frame_rate >= metrics['frame_rate']['optimal']:
                scores['frame_rate'] = 0.8
            elif frame_rate >= metrics['frame_rate']['min']:
                scores['frame_rate'] = 0.6
            else:
                scores['frame_rate'] = 0.3
            
            # Bitrate assessment
            bitrate = features.get('bitrate', 2000)
            if bitrate >= metrics['bitrate']['high']:
                scores['bitrate'] = 1.0
            elif bitrate >= metrics['bitrate']['optimal']:
                scores['bitrate'] = 0.8
            elif bitrate >= metrics['bitrate']['min']:
                scores['bitrate'] = 0.5
            else:
                scores['bitrate'] = 0.2
            
            # Compression artifacts assessment
            compression_artifacts = features.get('compression_artifacts', 0.1)
            if compression_artifacts <= metrics['compression']['optimal']:
                scores['compression'] = 1.0
            elif compression_artifacts <= metrics['compression']['max_artifacts']:
                scores['compression'] = 0.6
            else:
                scores['compression'] = 0.2
            
            # Color depth assessment
            color_depth = features.get('color_depth', 8)
            if color_depth >= metrics['color_depth']['max']:
                scores['color_depth'] = 1.0
            elif color_depth >= metrics['color_depth']['optimal']:
                scores['color_depth'] = 0.8
            elif color_depth >= metrics['color_depth']['min']:
                scores['color_depth'] = 0.6
            else:
                scores['color_depth'] = 0.3
            
            # Stabilization assessment
            shake_level = features.get('camera_shake', 1.0)
            if shake_level <= metrics['stabilization']['optimal']:
                scores['stabilization'] = 1.0
            elif shake_level <= metrics['stabilization']['max_shake']:
                scores['stabilization'] = 0.6
            else:
                scores['stabilization'] = 0.2
            
        except Exception as e:
            logger.error(f"Error assessing video technical quality: {e}")
        
        return scores

    def _assess_image_technical(self, features: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, float]:
        """Assess image technical quality."""        scores = {}
        
        try:
            # Resolution assessment
            width = features.get('width', 1000)
            height = features.get('height', 1000)
            resolution = max(width, height)
            
            if resolution >= metrics['resolution']['excellent']:
                scores['resolution'] = 1.0
            elif resolution >= metrics['resolution']['good']:
                scores['resolution'] = 0.8
            elif resolution >= metrics['resolution']['min']:
                scores['resolution'] = 0.5
            else:
                scores['resolution'] = 0.2
            
            # DPI assessment
            dpi = features.get('dpi', 72)
            if dpi >= metrics['dpi']['professional']:
                scores['dpi'] = 1.0
            elif dpi >= metrics['dpi']['print']:
                scores['dpi'] = 0.8
            elif dpi >= metrics['dpi']['min']:
                scores['dpi'] = 0.5
            else:
                scores['dpi'] = 0.3
            
            # Compression artifacts assessment
            compression_artifacts = features.get('compression_artifacts', 0.1)
            if compression_artifacts <= metrics['compression']['optimal']:
                scores['compression'] = 1.0
            elif compression_artifacts <= metrics['compression']['max_artifacts']:
                scores['compression'] = 0.6
            else:
                scores['compression'] = 0.2
            
            # Noise level assessment
            noise_level = features.get('noise_level', 0.1)
            if noise_level <= metrics['noise_level']['optimal']:
                scores['noise'] = 1.0
            elif noise_level <= metrics['noise_level']['max']:
                scores['noise'] = 0.5
            else:
                scores['noise'] = 0.2
            
            # Sharpness assessment
            sharpness = features.get('sharpness', 0.5)
            if sharpness >= metrics['sharpness']['optimal']:
                scores['sharpness'] = 1.0
            elif sharpness >= metrics['sharpness']['min']:
                scores['sharpness'] = 0.6
            else:
                scores['sharpness'] = 0.2
            
            # Exposure assessment
            exposure = features.get('exposure', 0)
            exposure_deviation = abs(exposure - metrics['exposure']['optimal'])
            
            if exposure_deviation <= 0.5:
                scores['exposure'] = 1.0
            elif exposure_deviation <= 1.0:
                scores['exposure'] = 0.7
            elif exposure_deviation <= 2.0:
                scores['exposure'] = 0.4
            else:
                scores['exposure'] = 0.1
            
            # Color accuracy assessment
            color_accuracy = features.get('color_accuracy', 0.8)
            if color_accuracy >= metrics['color_accuracy']['optimal']:
                scores['color_accuracy'] = 1.0
            elif color_accuracy >= metrics['color_accuracy']['min']:
                scores['color_accuracy'] = 0.6
            else:
                scores['color_accuracy'] = 0.3
            
        except Exception as e:
            logger.error(f"Error assessing image technical quality: {e}")
        
        return scores

    def _assess_text_technical(self, features: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, float]:
        """Assess text technical quality."""        scores = {}
        
        try:
            # Readability assessment
            readability = features.get('readability_score', 70)
            if readability >= metrics['readability']['excellent']:
                scores['readability'] = 1.0
            elif readability >= metrics['readability']['good']:
                scores['readability'] = 0.8
            elif readability >= metrics['readability']['min']:
                scores['readability'] = 0.5
            else:
                scores['readability'] = 0.2
            
            # Grammar assessment
            grammar_score = features.get('grammar_score', 0.9)
            if grammar_score >= metrics['grammar_score']['optimal']:
                scores['grammar'] = 1.0
            elif grammar_score >= metrics['grammar_score']['min']:
                scores['grammar'] = 0.6
            else:
                scores['grammar'] = 0.2
            
            # Spelling assessment
            spelling_accuracy = features.get('spelling_accuracy', 0.98)
            if spelling_accuracy >= metrics['spelling_accuracy']['optimal']:
                scores['spelling'] = 1.0
            elif spelling_accuracy >= metrics['spelling_accuracy']['min']:
                scores['spelling'] = 0.6
            else:
                scores['spelling'] = 0.2
            
            # Sentence length assessment
            avg_sentence_length = features.get('avg_sentence_length', 20)
            if metrics['sentence_length']['min'] <= avg_sentence_length <= metrics['sentence_length']['max']:
                distance_from_optimal = abs(avg_sentence_length - metrics['sentence_length']['optimal'])
                scores['sentence_length'] = max(0.2, 1.0 - (distance_from_optimal / 20))
            else:
                scores['sentence_length'] = 0.2
            
            # Paragraph length assessment
            avg_paragraph_length = features.get('avg_paragraph_length', 150)
            if metrics['paragraph_length']['min'] <= avg_paragraph_length <= metrics['paragraph_length']['max']:
                distance_from_optimal = abs(avg_paragraph_length - metrics['paragraph_length']['optimal'])
                scores['paragraph_length'] = max(0.2, 1.0 - (distance_from_optimal / 200))
            else:
                scores['paragraph_length'] = 0.2
            
            # Vocabulary diversity assessment
            vocabulary_diversity = features.get('vocabulary_diversity', 0.6)
            if vocabulary_diversity >= metrics['vocabulary_diversity']['optimal']:
                scores['vocabulary'] = 1.0
            elif vocabulary_diversity >= metrics['vocabulary_diversity']['min']:
                scores['vocabulary'] = 0.6
            else:
                scores['vocabulary'] = 0.3
            
        except Exception as e:
            logger.error(f"Error assessing text technical quality: {e}")
        
        return scores

    def _assess_content_quality(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Assess content quality dimensions."""        try:
            assessment = {
                'score': 0.0,
                'metrics': {},
                'dimension_scores': {}
            }
            
            classifications = content_data.get('classifications', {})
            features = content_data.get('features', {})
            
            dimension_scores = {}
            
            for dimension, dimension_data in self.content_dimensions.items():
                dimension_score = self._assess_content_dimension(
                    dimension, dimension_data, classifications, features, content_type
                )
                dimension_scores[dimension] = dimension_score
            
            # Calculate overall content score
            if dimension_scores:
                assessment['score'] = np.mean(list(dimension_scores.values()))
                assessment['dimension_scores'] = dimension_scores
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            return {'score': 0.0, 'metrics': {}, 'dimension_scores': {}}

    def _assess_content_dimension(
        self, 
        dimension: str, 
        dimension_data: Dict[str, Any], 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> float:
        """Assess a specific content quality dimension."""        try:
            dimension_score = 0.0
            total_weight = 0.0
            
            for aspect, aspect_data in dimension_data.items():
                weight = aspect_data.get('weight', 0.25)
                metrics = aspect_data.get('metrics', [])
                
                aspect_score = self._evaluate_aspect_metrics(
                    aspect, metrics, classifications, features, content_type
                )
                
                dimension_score += aspect_score * weight
                total_weight += weight
            
            if total_weight > 0:
                dimension_score = dimension_score / total_weight
            
            return dimension_score
            
        except Exception as e:
            logger.error(f"Error assessing content dimension {dimension}: {e}")
            return 0.0

    def _evaluate_aspect_metrics(
        self, 
        aspect: str, 
        metrics: List[str], 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> float:
        """Evaluate specific aspect metrics."""        try:
            scores = []
            
            # Map metrics to actual data extraction
            for metric in metrics:
                score = self._extract_metric_score(metric, classifications, features, content_type)
                if score is not None:
                    scores.append(score)
            
            # Add aspect-specific evaluations
            if aspect == 'originality':
                # Check for uniqueness indicators
                if 'similarity_analysis' in features:
                    similarity = features['similarity_analysis'].get('max_similarity', 0)
                    originality_score = max(0, 1.0 - similarity)
                    scores.append(originality_score)
            
            elif aspect == 'emotional_impact':
                # Check mood analysis results
                if 'mood_analysis' in classifications:
                    mood_confidence = classifications['mood_analysis'].get('confidence', 0)
                    emotion_complexity = classifications['mood_analysis'].get('emotion_complexity', 0)
                    emotional_impact = (mood_confidence + emotion_complexity) / 2
                    scores.append(emotional_impact)
            
            elif aspect == 'attention_grabbing':
                # Evaluate based on content characteristics
                if content_type == 'image':
                    if 'color_analysis' in features:
                        color_contrast = features['color_analysis'].get('contrast_ratio', 0.5)
                        scores.append(min(color_contrast, 1.0))
                elif content_type == 'text':
                    if 'keyword_extraction' in features:
                        keyword_strength = len(features['keyword_extraction'].get('top_keywords', []))
                        scores.append(min(keyword_strength / 10, 1.0))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            logger.error(f"Error evaluating aspect metrics for {aspect}: {e}")
            return 0.5

    def _extract_metric_score(
        self, 
        metric: str, 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> Optional[float]:
        """Extract score for a specific metric."""        try:
            # Map metric names to data locations
            metric_mapping = {
                'uniqueness': ('similarity_analysis', 'uniqueness_score'),
                'innovation': ('style_analysis', 'innovation_level'),
                'aesthetic_appeal': ('style_analysis', 'aesthetic_score'),
                'composition': ('composition_analysis', 'composition_score'),
                'idea_clarity': ('concept_analysis', 'clarity_score'),
                'message_coherence': ('content_analysis', 'coherence_score'),
                'technical_skill': ('technical_analysis', 'skill_level'),
                'attention_detail': ('quality_metrics', 'detail_score'),
                'hook_strength': ('engagement_analysis', 'hook_score'),
                'visual_appeal': ('visual_analysis', 'appeal_score'),
                'emotional_resonance': ('mood_analysis', 'resonance_score'),
                'mood_creation': ('mood_analysis', 'mood_strength'),
                'distinctive_elements': ('uniqueness_analysis', 'distinctiveness'),
                'viral_potential': ('engagement_analysis', 'viral_score'),
                'social_appeal': ('social_analysis', 'appeal_score'),
                'professional_standards': ('quality_analysis', 'professional_score'),
                'brand_consistency': ('brand_analysis', 'consistency_score'),
                'commercial_viability': ('market_analysis', 'viability_score')
            }
            
            if metric in metric_mapping:
                category, field = metric_mapping[metric]
                
                # Check in classifications first
                if category in classifications:
                    return classifications[category].get(field)
                
                # Check in features
                if category in features:
                    return features[category].get(field)
            
            # Fallback to generic evaluation
            return self._generic_metric_evaluation(metric, classifications, features, content_type)
            
        except Exception as e:
            logger.error(f"Error extracting metric score for {metric}: {e}")
            return None

    def _generic_metric_evaluation(
        self, 
        metric: str, 
        classifications: Dict[str, Any], 
        features: Dict[str, Any], 
        content_type: str
    ) -> float:
        """Generic metric evaluation when specific mapping not available."""        try:
            # Basic heuristics for common metrics
            if 'quality' in metric.lower():
                return 0.7  # Assume good quality if no specific data
            elif 'appeal' in metric.lower():
                return 0.6  # Moderate appeal default
            elif 'clarity' in metric.lower():
                return 0.8  # Usually content is reasonably clear
            elif 'skill' in metric.lower():
                return 0.6  # Moderate skill assumption
            elif 'consistency' in metric.lower():
                return 0.7  # Assume reasonable consistency
            else:
                return 0.5  # Neutral score for unknown metrics
                
        except Exception:
            return 0.5

    def _assess_engagement_potential(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Assess engagement potential of content."""        try:
            assessment = {
                'score': 0.0,
                'metrics': {}
            }
            
            classifications = content_data.get('classifications', {})
            features = content_data.get('features', {})
            
            engagement_factors = {}
            
            # Emotional impact
            if 'mood_analysis' in classifications:
                mood_data = classifications['mood_analysis']
                emotion_strength = mood_data.get('confidence', 0) * mood_data.get('emotion_complexity', 0.5)
                engagement_factors['emotional_impact'] = emotion_strength
            
            # Content appeal
            if content_type == 'video':
                # Video-specific engagement factors
                if 'video_analysis' in features:
                    video_data = features['video_analysis']
                    engagement_factors['visual_appeal'] = video_data.get('visual_appeal', 0.5)
                    engagement_factors['pacing'] = video_data.get('pacing_score', 0.5)
            
            elif content_type == 'audio':
                # Audio-specific engagement factors
                if 'audio_analysis' in features:
                    audio_data = features['audio_analysis']
                    engagement_factors['audio_appeal'] = audio_data.get('appeal_score', 0.5)
                    engagement_factors['energy'] = audio_data.get('energy_level', 0.5)
            
            elif content_type == 'image':
                # Image-specific engagement factors
                if 'visual_analysis' in features:
                    visual_data = features['visual_analysis']
                    engagement_factors['visual_impact'] = visual_data.get('impact_score', 0.5)
                    engagement_factors['composition'] = visual_data.get('composition_score', 0.5)
            
            elif content_type == 'text':
                # Text-specific engagement factors
                if 'text_analysis' in features:
                    text_data = features['text_analysis']
                    engagement_factors['readability'] = text_data.get('readability_score', 70) / 100
                    engagement_factors['interest_level'] = text_data.get('interest_score', 0.5)
            
            # Trend alignment
            if 'trend_analysis' in features:
                trend_data = features['trend_analysis']
                engagement_factors['trend_alignment'] = trend_data.get('alignment_score', 0.5)
            
            # Social potential
            if 'social_analysis' in features:
                social_data = features['social_analysis']
                engagement_factors['shareability'] = social_data.get('shareability_score', 0.5)
                engagement_factors['discussion_potential'] = social_data.get('discussion_score', 0.5)
            
            # Calculate overall engagement score
            if engagement_factors:
                assessment['score'] = np.mean(list(engagement_factors.values()))
                assessment['metrics'] = engagement_factors
            else:
                # Fallback scoring based on basic characteristics
                assessment['score'] = 0.5
                assessment['metrics'] = {'default_engagement': 0.5}
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing engagement potential: {e}")
            return {'score': 0.5, 'metrics': {}}

    def _calculate_overall_score(self, technical: float, content: float, engagement: float) -> float:
        """Calculate overall quality score."""        try:
            weighted_score = (
                technical * self.config['weight_technical'] +
                content * self.config['weight_content'] +
                engagement * self.config['weight_engagement']
            )
            
            return min(weighted_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 0.0

    def _assess_platform_compliance(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Assess compliance with platform-specific standards."""        try:
            platform_scores = {}
            
            for platform, standards in self.platform_standards.items():
                if content_type in standards:
                    platform_score = self._evaluate_platform_compliance(
                        content_data, content_type, platform, standards[content_type]
                    )
                    platform_scores[platform] = platform_score
            
            return platform_scores
            
        except Exception as e:
            logger.error(f"Error assessing platform compliance: {e}")
            return {}

    def _evaluate_platform_compliance(
        self, 
        content_data: Dict[str, Any], 
        content_type: str, 
        platform: str, 
        standards: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate compliance with specific platform standards."""        try:
            compliance = {
                'overall_score': 0.0,
                'compliance_factors': {},
                'recommendations': []
            }
            
            technical_features = content_data.get('technical_analysis', {})
            scores = []
            
            if content_type == 'video':
                # Video platform compliance
                if 'min_resolution' in standards:
                    min_width, min_height = standards['min_resolution']
                    actual_width = technical_features.get('width', 0)
                    actual_height = technical_features.get('height', 0)
                    
                    if actual_width >= min_width and actual_height >= min_height:
                        compliance['compliance_factors']['resolution'] = 1.0
                        scores.append(1.0)
                    else:
                        compliance['compliance_factors']['resolution'] = 0.0
                        scores.append(0.0)
                        compliance['recommendations'].append(
                            f"Increase resolution to at least {min_width}x{min_height}"
                        )
                
                # Aspect ratio compliance
                if 'aspect_ratios' in standards:
                    # This would need actual aspect ratio calculation
                    compliance['compliance_factors']['aspect_ratio'] = 0.8
                    scores.append(0.8)
                
                # Duration compliance
                if 'max_duration' in standards:
                    duration = technical_features.get('duration', 60)
                    max_duration = standards['max_duration']
                    
                    if duration <= max_duration:
                        compliance['compliance_factors']['duration'] = 1.0
                        scores.append(1.0)
                    else:
                        compliance['compliance_factors']['duration'] = 0.0
                        scores.append(0.0)
                        compliance['recommendations'].append(
                            f"Reduce duration to maximum {max_duration} seconds"
                        )
            
            elif content_type == 'audio':
                # Audio platform compliance
                if 'min_quality' in standards:
                    bitrate = technical_features.get('bitrate', 128)
                    min_quality = standards['min_quality']
                    
                    if bitrate >= min_quality:
                        compliance['compliance_factors']['quality'] = 1.0
                        scores.append(1.0)
                    else:
                        compliance['compliance_factors']['quality'] = 0.0
                        scores.append(0.0)
                        compliance['recommendations'].append(
                            f"Increase audio quality to at least {min_quality} kbps"
                        )
                
                # Loudness compliance
                if 'loudness_target' in standards:
                    loudness = technical_features.get('loudness_lufs', -16)
                    target = standards['loudness_target']
                    difference = abs(loudness - target)
                    
                    if difference <= 2:
                        compliance['compliance_factors']['loudness'] = 1.0
                        scores.append(1.0)
                    elif difference <= 5:
                        compliance['compliance_factors']['loudness'] = 0.5
                        scores.append(0.5)
                    else:
                        compliance['compliance_factors']['loudness'] = 0.0
                        scores.append(0.0)
                        compliance['recommendations'].append(
                            f"Adjust loudness to target {target} LUFS"
                        )
            
            # Calculate overall compliance score
            if scores:
                compliance['overall_score'] = np.mean(scores)
            
            return compliance
            
        except Exception as e:
            logger.error(f"Error evaluating platform compliance for {platform}: {e}")
            return {'overall_score': 0.0, 'compliance_factors': {}, 'recommendations': []}

    def _compare_to_benchmarks(self, assessment: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Compare assessment results to industry benchmarks."""        try:
            benchmark_comparison = {
                'industry_category': 'unknown',
                'benchmark_level': 'amateur',
                'score_comparison': {},
                'percentile_rank': 0
            }
            
            # Map content type to industry category
            industry_mapping = {
                'audio': 'music_production',
                'video': 'video_production',
                'image': 'photography',
                'text': 'content_writing'
            }
            
            industry_category = industry_mapping.get(content_type)
            if not industry_category or industry_category not in self.industry_benchmarks:
                return benchmark_comparison
            
            benchmark_comparison['industry_category'] = industry_category
            benchmarks = self.industry_benchmarks[industry_category]
            
            overall_score = assessment['overall_score']
            technical_score = assessment['technical_score']
            content_score = assessment['content_score']
            
            # Determine benchmark level
            for level, level_data in reversed(list(benchmarks.items())):
                if overall_score >= level_data['overall_score']:
                    benchmark_comparison['benchmark_level'] = level
                    break
            
            # Compare to each benchmark level
            score_comparisons = {}
            for level, level_data in benchmarks.items():
                score_comparisons[level] = {
                    'overall_diff': overall_score - level_data['overall_score'],
                    'technical_diff': technical_score - level_data['technical'],
                    'content_diff': content_score - level_data['content'],
                    'meets_standard': overall_score >= level_data['overall_score']
                }
            
            benchmark_comparison['score_comparison'] = score_comparisons
            
            # Calculate percentile rank (simplified)
            all_scores = [level_data['overall_score'] for level_data in benchmarks.values()]
            all_scores.append(overall_score)
            all_scores.sort()
            
            percentile = (all_scores.index(overall_score) / (len(all_scores) - 1)) * 100
            benchmark_comparison['percentile_rank'] = percentile
            
            return benchmark_comparison
            
        except Exception as e:
            logger.error(f"Error comparing to benchmarks: {e}")
            return {}

    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score."""        if overall_score >= self.config['expert_threshold']:
            return 'expert'
        elif overall_score >= self.config['professional_threshold']:
            return 'professional'
        elif overall_score >= self.config['min_quality_threshold']:
            return 'acceptable'
        else:
            return 'needs_improvement'

    def _identify_strengths_weaknesses(self, assessment: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses from assessment."""        strengths = []
        weaknesses = []
        
        try:
            # Technical strengths/weaknesses
            technical_metrics = assessment.get('technical_metrics', {})
            for metric, score in technical_metrics.items():
                if score >= 0.8:
                    strengths.append(f"Excellent {metric.replace('_', ' ')}")
                elif score <= 0.4:
                    weaknesses.append(f"Poor {metric.replace('_', ' ')}")
            
            # Content strengths/weaknesses
            content_metrics = assessment.get('content_metrics', {})
            dimension_scores = content_metrics.get('dimension_scores', {})
            for dimension, score in dimension_scores.items():
                if score >= 0.8:
                    strengths.append(f"Strong {dimension}")
                elif score <= 0.4:
                    weaknesses.append(f"Weak {dimension}")
            
            # Overall assessment
            overall_score = assessment.get('overall_score', 0)
            if overall_score >= 0.9:
                strengths.append("Exceptional overall quality")
            elif overall_score <= 0.4:
                weaknesses.append("Overall quality needs significant improvement")
            
        except Exception as e:
            logger.error(f"Error identifying strengths/weaknesses: {e}")
        
        return strengths[:5], weaknesses[:5]  # Limit to top 5 each

    def _generate_recommendations(self, assessment: Dict[str, Any], content_type: str) -> List[str]:
        """Generate improvement recommendations."""        recommendations = []
        
        try:
            overall_score = assessment.get('overall_score', 0)
            technical_score = assessment.get('technical_score', 0)
            content_score = assessment.get('content_score', 0)
            engagement_score = assessment.get('engagement_score', 0)
            
            # Priority recommendations based on lowest scores
            scores = {
                'technical': technical_score,
                'content': content_score,
                'engagement': engagement_score
            }
            
            lowest_area = min(scores.items(), key=lambda x: x[1])
            
            if lowest_area[1] < 0.6:
                area, score = lowest_area
                recommendations.append(f"Focus on improving {area} quality (current: {score:.2f})")
            
            # Specific recommendations based on content type
            if content_type == 'audio':
                if technical_score < 0.7:
                    recommendations.extend([
                        "Consider higher quality recording equipment",
                        "Improve acoustic treatment of recording space",
                        "Pay attention to gain staging and levels"
                    ])
            
            elif content_type == 'video':
                if technical_score < 0.7:
                    recommendations.extend([
                        "Upgrade camera/recording equipment for better resolution",
                        "Improve lighting setup",
                        "Use stable camera mounting or stabilization"
                    ])
            
            elif content_type == 'image':
                if technical_score < 0.7:
                    recommendations.extend([
                        "Use higher resolution camera or increase image size",
                        "Improve lighting conditions",
                        "Check focus and sharpness"
                    ])
            
            elif content_type == 'text':
                if technical_score < 0.7:
                    recommendations.extend([
                        "Review and improve grammar and spelling",
                        "Optimize sentence and paragraph length",
                        "Enhance vocabulary diversity"
                    ])
            
            # Content improvement recommendations
            if content_score < 0.7:
                recommendations.extend([
                    "Develop stronger creative concepts",
                    "Focus on emotional engagement",
                    "Improve professional presentation"
                ])
            
            # Engagement improvement recommendations
            if engagement_score < 0.7:
                recommendations.extend([
                    "Study current trends in your content area",
                    "Analyze successful content in your niche",
                    "Consider audience feedback and preferences"
                ])
            
            # Platform-specific recommendations
            platform_scores = assessment.get('platform_scores', {})
            for platform, platform_data in platform_scores.items():
                if platform_data.get('overall_score', 1.0) < 0.8:
                    platform_recommendations = platform_data.get('recommendations', [])
                    recommendations.extend(platform_recommendations)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:10]  # Limit to top 10 recommendations

    def _award_quality_badges(self, assessment: Dict[str, Any]) -> List[str]:
        """Award quality badges based on assessment results."""        badges = []
        
        try:
            overall_score = assessment.get('overall_score', 0)
            technical_score = assessment.get('technical_score', 0)
            content_score = assessment.get('content_score', 0)
            engagement_score = assessment.get('engagement_score', 0)
            
            # Overall quality badges
            if overall_score >= 0.95:
                badges.append("Master Quality")
            elif overall_score >= 0.9:
                badges.append("Expert Quality")
            elif overall_score >= 0.8:
                badges.append("Professional Quality")
            elif overall_score >= 0.7:
                badges.append("Good Quality")
            
            # Specific area badges
            if technical_score >= 0.9:
                badges.append("Technical Excellence")
            
            if content_score >= 0.9:
                badges.append("Creative Excellence")
            
            if engagement_score >= 0.9:
                badges.append("High Engagement Potential")
            
            # Special achievement badges
            strengths = assessment.get('strengths', [])
            if len(strengths) >= 3:
                badges.append("Multi-Dimensional Strength")
            
            # Platform compliance badges
            platform_scores = assessment.get('platform_scores', {})
            high_compliance_platforms = [
                platform for platform, data in platform_scores.items()
                if data.get('overall_score', 0) >= 0.9
            ]
            
            if len(high_compliance_platforms) >= 3:
                badges.append("Multi-Platform Ready")
            
            # Benchmark badges
            benchmark_comparison = assessment.get('benchmark_comparison', {})
            benchmark_level = benchmark_comparison.get('benchmark_level')
            
            if benchmark_level == 'industry_standard':
                badges.append("Industry Standard")
            elif benchmark_level == 'professional':
                badges.append("Professional Standard")
            
        except Exception as e:
            logger.error(f"Error awarding quality badges: {e}")
        
        return badges

    def _get_timestamp(self) -> str:
        """Get current timestamp."""        from datetime import datetime
        return datetime.now().isoformat()

    def get_quality_info(self, quality_level: str) -> Dict[str, Any]:
        """Get information about a quality level."""        try:
            quality_info = {
                'needs_improvement': {
                    'score_range': '0.0 - 0.59',
                    'description': 'Content requires significant improvement',
                    'characteristics': ['Technical issues', 'Poor content quality', 'Low engagement potential'],
                    'recommendations': ['Focus on basics', 'Improve technical skills', 'Study best practices']
                },
                'acceptable': {
                    'score_range': '0.6 - 0.79',
                    'description': 'Content meets basic quality standards',
                    'characteristics': ['Adequate technical quality', 'Reasonable content', 'Some engagement'],
                    'recommendations': ['Polish technical aspects', 'Enhance creativity', 'Improve consistency']
                },
                'professional': {
                    'score_range': '0.8 - 0.89',
                    'description': 'High-quality professional content',
                    'characteristics': ['Strong technical execution', 'Good creative content', 'High engagement'],
                    'recommendations': ['Fine-tune details', 'Innovate creatively', 'Optimize for platforms']
                },
                'expert': {
                    'score_range': '0.9 - 1.0',
                    'description': 'Exceptional quality content',
                    'characteristics': ['Excellent technical quality', 'Outstanding creativity', 'Maximum engagement'],
                    'recommendations': ['Maintain standards', 'Lead trends', 'Mentor others']
                }
            }
            
            return quality_info.get(quality_level, {'error': f'Quality level "{quality_level}" not found'})
            
        except Exception as e:
            logger.error(f"Error getting quality info: {e}")
            return {'error': str(e)}

    def compare_quality(self, assessment1: Dict[str, Any], assessment2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two quality assessments."""        try:
            comparison = {
                'overall_difference': 0.0,
                'technical_difference': 0.0,
                'content_difference': 0.0,
                'engagement_difference': 0.0,
                'quality_level_comparison': {},
                'recommendation': ''
            }
            
            # Compare overall scores
            score1 = assessment1.get('overall_score', 0)
            score2 = assessment2.get('overall_score', 0)
            comparison['overall_difference'] = score1 - score2
            
            # Compare technical scores
            tech1 = assessment1.get('technical_score', 0)
            tech2 = assessment2.get('technical_score', 0)
            comparison['technical_difference'] = tech1 - tech2
            
            # Compare content scores
            content1 = assessment1.get('content_score', 0)
            content2 = assessment2.get('content_score', 0)
            comparison['content_difference'] = content1 - content2
            
            # Compare engagement scores
            engagement1 = assessment1.get('engagement_score', 0)
            engagement2 = assessment2.get('engagement_score', 0)
            comparison['engagement_difference'] = engagement1 - engagement2
            
            # Compare quality levels
            level1 = assessment1.get('quality_level', 'unknown')
            level2 = assessment2.get('quality_level', 'unknown')
            comparison['quality_level_comparison'] = {
                'first': level1,
                'second': level2,
                'improvement': level1 != level2 and score1 > score2
            }
            
            # Generate recommendation
            if comparison['overall_difference'] > 0.1:
                comparison['recommendation'] = "First content shows significantly better quality"
            elif comparison['overall_difference'] < -0.1:
                comparison['recommendation'] = "Second content shows significantly better quality"
            else:
                comparison['recommendation'] = "Both contents have similar quality levels"
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing quality assessments: {e}")
            return {}

    def get_assessment_summary(self, assessment: Dict[str, Any]) -> str:
        """Generate a human-readable summary of quality assessment."""        try:
            summary_parts = []
            
            # Overall quality
            overall_score = assessment.get('overall_score', 0)
            quality_level = assessment.get('quality_level', 'unknown')
            summary_parts.append(f"Quality: {quality_level} ({overall_score:.2f})")
            
            # Component scores
            technical_score = assessment.get('technical_score', 0)
            content_score = assessment.get('content_score', 0)
            engagement_score = assessment.get('engagement_score', 0)
            
            summary_parts.append(f"Technical: {technical_score:.2f}")
            summary_parts.append(f"Content: {content_score:.2f}")
            summary_parts.append(f"Engagement: {engagement_score:.2f}")
            
            # Quality badges
            badges = assessment.get('quality_badges', [])
            if badges:
                summary_parts.append(f"Badges: {', '.join(badges[:2])}")
            
            # Benchmark level
            benchmark_comparison = assessment.get('benchmark_comparison', {})
            benchmark_level = benchmark_comparison.get('benchmark_level')
            if benchmark_level:
                summary_parts.append(f"Level: {benchmark_level}")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating assessment summary: {e}")
            return "Summary generation failed"
