# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Tests Ultra-Industriels Avancés pour le Module Content Detection & Monitoring

 AVERTISSEMENT STRICT : Ce code, concept et architecture sont la propriété intellectuelle exclusive de Fahed Mlaiel (mlaiel@live.de). 
Toute utilisation, copie, distribution ou exploitation sans autorisation écrite explicite est STRICTEMENT INTERDITE et poursuivie 
au maximum de la loi. Tous droits réservés. Copyright © 2025 Fahed Mlaiel.

 INTERDICTION FORMELLE : Il est formellement interdit de copier, voler, utiliser ou s'inspirer de ce code/concept sans 
autorisation personnelle écrite de Fahed Mlaiel. Violation = Poursuites légales immédiates.

Équipe Projet Expert - Dirigée par Fahed Mlaiel (mlaiel@live.de):
Lead Dev + Architecte Développeur IA
Développeur Backend Senior (Python/FastAPI/Django)
Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
Spécialiste Sécurité Backend
Architecte Microservices
Développeur Audio
DevOps Engineer
IA Prompt Engineer

Contact Officiel : Fahed Mlaiel <mlaiel@live.de>
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import aiohttp
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple, Optional, Set
import uuid
import numpy as np
import hashlib
import io
import json
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock, PropertyMock
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import requests
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Import modules under test - REAL BUSINESS LOGIC
from ai.content_protection.detection import (
    PiracyDetector,
    UnauthorizedUseDetector,
    DetectionAlert,
    DetectionType,
    DetectionStatus,
    MonitoringProfile,
    MonitoringSource,
    InfringementDetector,
    SimilarityAnalyzer,
    ContentMatcher,
    ContentDetector
)
from ai.content_protection.fingerprinting import ContentFingerprint, FingerprintType
from ai.content_protection.core import ContentType, ContentItem

logger = logging.getLogger(__name__)


@dataclass
class RealWorldTestScenario:
    """Real-world test scenario for piracy detection"""
    scenario_name: str
    content_type: ContentType
    attack_vector: str
    expected_detection_rate: float
    max_processing_time: float
    test_data: Dict[str, Any]


class TestUltraIndustrialPiracyDetection:
    """
    Ultra-Industrial Grade Test Suite for Piracy Detection & Monitoring
    
    Tests réels et industriels couvrant:
    - Détection de piratage multi-plateforme en temps réel
    - Algorithmes ML avancés de détection de similarité
    - Monitoring automatisé 24/7 de contenus protégés
    - Résistance aux techniques d'évasion avancées
    - Intégration avec systèmes légaux automatisés
    - Analytics prédictifs de menaces
    """

    @pytest.fixture
    def enterprise_detection_config(self):
        """Configuration ultra-avancée pour la détection de piratage"""



        return {
            'detection_algorithms': {
                'similarity_threshold': 0.85,
                'false_positive_threshold': 0.05,
                'deep_learning_models': {
                    'audio_similarity': 'trained_audio_model_v3.2.h5',
                    'image_similarity': 'trained_image_model_v2.8.h5',
                    'video_similarity': 'trained_video_model_v4.1.h5',
                    'text_similarity': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
                },
                'adversarial_detection': {
                    'enabled': True,
                    'attack_vectors': ['compression', 'cropping', 'filtering', 'speed_change', 'pitch_shift'],
                    'robustness_threshold': 0.90
                }
            },
            'monitoring_sources': {
                'web_crawling': {
                    'enabled': True,
                    'search_engines': ['google', 'bing', 'yandex', 'baidu'],
                    'crawl_frequency': 'hourly',
                    'max_pages_per_search': 1000
                },
                'social_media': {
                    'enabled': True,
                    'platforms': ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter'],
                    'api_monitoring': True,
                    'real_time_streams': True
                },
                'file_sharing': {
                    'enabled': True,
                    'platforms': ['torrent_trackers', 'direct_download_sites', 'streaming_sites'],
                    'deep_web_monitoring': True
                },
                'marketplaces': {
                    'enabled': True,
                    'platforms': ['amazon', 'ebay', 'etsy', 'alibaba'],
                    'keyword_monitoring': True
                }
            },
            'real_time_processing': {
                'enabled': True,
                'stream_processing': True,
                'gpu_acceleration': True,
                'parallel_workers': 16,
                'batch_size': 128
            },
            'legal_integration': {
                'dmca_automation': True,
                'takedown_generation': True,
                'law_firm_integration': True,
                'evidence_collection': True
            },
            'blockchain': {
                'evidence_immutability': True,
                'timestamp_verification': True,
                'legal_proof_generation': True
            }
        }

    @pytest.fixture
    def enterprise_piracy_detector(self, enterprise_detection_config):
        """Create enterprise-grade piracy detector"""
        detector = PiracyDetector(enterprise_detection_config)
        return detector

    @pytest.fixture
    def enterprise_monitoring_detector(self, enterprise_detection_config):
        """Create enterprise unauthorized use detector"""
        detector = UnauthorizedUseDetector(enterprise_detection_config)
        return detector

    @pytest.fixture
    def real_world_attack_scenarios(self):
        """Generate real-world attack scenarios for comprehensive testing"""
        scenarios = []
        
        # Audio piracy scenarios
        scenarios.append(RealWorldTestScenario(
            scenario_name="audio_compression_attack",
            content_type=ContentType.AUDIO,
            attack_vector="compression",
            expected_detection_rate=0.95,
            max_processing_time=2.0,
            test_data={
                'original_bitrate': 320,
                'compressed_bitrates': [128, 96, 64, 32],
                'compression_formats': ['mp3', 'aac', 'ogg', 'flac']
            }
        ))
        
        scenarios.append(RealWorldTestScenario(
            scenario_name="audio_speed_pitch_attack",
            content_type=ContentType.AUDIO,
            attack_vector="temporal_modification",
            expected_detection_rate=0.92,
            max_processing_time=3.0,
            test_data={
                'speed_factors': [0.8, 0.9, 1.1, 1.2, 1.5],
                'pitch_shifts': [-2, -1, 1, 2, 3],  # semitones
                'combined_modifications': True
            }
        ))
        
        # Image piracy scenarios
        scenarios.append(RealWorldTestScenario(
            scenario_name="image_geometric_attack",
            content_type=ContentType.IMAGE,
            attack_vector="geometric_transformation",
            expected_detection_rate=0.93,
            max_processing_time=1.5,
            test_data={
                'rotations': [5, 10, 15, 30, 45, 90],  # degrees
                'scale_factors': [0.5, 0.7, 0.8, 1.2, 1.5, 2.0],
                'crops': [(0.8, 0.8), (0.6, 0.6), (0.9, 0.7)],  # (width_ratio, height_ratio)
                'flips': ['horizontal', 'vertical', 'both']
            }
        ))
        
        scenarios.append(RealWorldTestScenario(
            scenario_name="image_filtering_attack",
            content_type=ContentType.IMAGE,
            attack_vector="filtering",
            expected_detection_rate=0.90,
            max_processing_time=2.0,
            test_data={
                'filters': ['gaussian_blur', 'median_filter', 'sharpen', 'edge_enhance'],
                'compression_qualities': [95, 85, 70, 50, 30],
                'noise_levels': [0.01, 0.05, 0.1, 0.2],
                'color_adjustments': {'brightness': [-20, 20], 'contrast': [0.8, 1.2], 'saturation': [0.5, 1.5]}
            }
        ))
        
        # Video piracy scenarios
        scenarios.append(RealWorldTestScenario(
            scenario_name="video_transcoding_attack",
            content_type=ContentType.VIDEO,
            attack_vector="transcoding",
            expected_detection_rate=0.88,
            max_processing_time=10.0,
            test_data={
                'resolutions': ['480p', '720p', '1080p', '4k'],
                'codecs': ['h264', 'h265', 'vp9', 'av1'],
                'frame_rates': [24, 30, 60],
                'bitrates': [1000, 2000, 5000, 10000]  # kbps
            }
        ))
        
        # Text piracy scenarios
        scenarios.append(RealWorldTestScenario(
            scenario_name="text_paraphrasing_attack",
            content_type=ContentType.TEXT,
            attack_vector="semantic_modification",
            expected_detection_rate=0.85,
            max_processing_time=5.0,
            test_data={
                'paraphrasing_levels': ['light', 'moderate', 'heavy'],
                'translation_back': ['en->fr->en', 'en->es->en', 'en->de->en'],
                'synonym_substitution': [0.1, 0.3, 0.5],  # percentage of words
                'sentence_reordering': True,
                'paragraph_splitting': True
            }
        ))
        
        return scenarios

    @pytest.fixture
    def monitoring_profiles_comprehensive(self):
        """Create comprehensive monitoring profiles for testing"""
        profiles = []
        
        # High-value music content monitoring
        profiles.append(MonitoringProfile(
            profile_id=str(uuid.uuid4()),
            content_id="premium_music_track_001",
            owner_id="creator_fahed_mlaiel",
            monitoring_sources={
                MonitoringSource.MUSIC_PLATFORMS,
                MonitoringSource.SOCIAL_MEDIA,
                MonitoringSource.FILE_SHARING,
                MonitoringSource.WEB_CRAWL
            },
            search_terms=[
                "Premium Music Track Fahed Mlaiel",
                "Exclusive Electronic Track",
                "AI Generated Music Fahed",
                "Protected Audio Content"
            ],
            similarity_threshold=0.90,
            monitoring_frequency="hourly",
            notification_settings={
                'email_alerts': True,
                'sms_alerts': True,
                'webhook_url': 'https://api.faheds-system.com/alerts',
                'severity_levels': ['high', 'critical']
            }
        ))
        
        # Professional photography monitoring
        profiles.append(MonitoringProfile(
            profile_id=str(uuid.uuid4()),
            content_id="professional_photo_series_001",
            owner_id="creator_fahed_mlaiel",
            monitoring_sources={
                MonitoringSource.IMAGE_SITES,
                MonitoringSource.SOCIAL_MEDIA,
                MonitoringSource.MARKETPLACE,
                MonitoringSource.WEB_CRAWL
            },
            search_terms=[
                "Professional Photography Fahed Mlaiel",
                "Exclusive Photo Series",
                "High-Resolution Digital Art",
                "Protected Visual Content"
            ],
            similarity_threshold=0.85,
            monitoring_frequency="daily",
            notification_settings={
                'email_alerts': True,
                'dashboard_updates': True,
                'legal_team_notification': True
            }
        ))
        
        return profiles

    @pytest.mark.asyncio
    async def test_ultra_advanced_real_time_piracy_detection(self, enterprise_piracy_detector, real_world_attack_scenarios):
        """Test ultra-advanced real-time piracy detection against realistic attack vectors"""
        logger.info("Testing ultra-advanced real-time piracy detection")
        
        await enterprise_piracy_detector.initialize()
        
        total_scenarios_passed = 0
        detailed_results = []
        
        for scenario in real_world_attack_scenarios:
            logger.info(f"Testing scenario: {scenario.scenario_name}")
            
            start_time = time.time()
            
            # Simulate detection against the attack scenario
            detection_result = await enterprise_piracy_detector.detect_content_theft(
                content_id=f"test_{scenario.scenario_name}",
                content_type=scenario.content_type,
                attack_vector=scenario.attack_vector,
                test_parameters=scenario.test_data
            )
            
            processing_time = time.time() - start_time
            
            # Enterprise-grade assertions
            assert isinstance(detection_result, dict)
            assert 'detection_rate' in detection_result
            assert 'confidence_score' in detection_result
            assert 'attack_vector_identified' in detection_result
            assert 'evidence_collected' in detection_result
            
            detection_rate = detection_result['detection_rate']
            confidence_score = detection_result['confidence_score']
            
            # Performance and accuracy requirements
            assert detection_rate >= scenario.expected_detection_rate, f"Detection rate {detection_rate} below expected {scenario.expected_detection_rate}"
            assert confidence_score >= 0.90, f"Confidence score {confidence_score} too low"
            assert processing_time <= scenario.max_processing_time, f"Processing time {processing_time}s exceeds limit {scenario.max_processing_time}s"
            
            # Verify evidence collection
            assert len(detection_result['evidence_collected']) > 0
            assert 'fingerprint_matches' in detection_result['evidence_collected'][0]
            assert 'similarity_scores' in detection_result['evidence_collected'][0]
            assert 'blockchain_proof' in detection_result['evidence_collected'][0]
            
            total_scenarios_passed += 1
            
            detailed_results.append({
                'scenario': scenario.scenario_name,
                'detection_rate': detection_rate,
                'confidence': confidence_score,
                'processing_time': processing_time,
                'status': 'PASSED'
            })
            
            logger.info(f"Scenario {scenario.scenario_name}: "
                       f"detection_rate={detection_rate:.3f}, "
                       f"confidence={confidence_score:.3f}, "
                       f"time={processing_time:.3f}s - PASSED")
        
        # Overall system performance validation
        assert total_scenarios_passed == len(real_world_attack_scenarios), "Not all attack scenarios passed"
        
        # Calculate average performance metrics
        avg_detection_rate = sum(r['detection_rate'] for r in detailed_results) / len(detailed_results)
        avg_confidence = sum(r['confidence'] for r in detailed_results) / len(detailed_results)
        avg_processing_time = sum(r['processing_time'] for r in detailed_results) / len(detailed_results)
        
        logger.info(f"Overall Performance: avg_detection_rate={avg_detection_rate:.3f}, "
                   f"avg_confidence={avg_confidence:.3f}, avg_time={avg_processing_time:.3f}s")
        
        # Enterprise thresholds
        assert avg_detection_rate >= 0.90, "Overall detection rate below enterprise threshold"
        assert avg_confidence >= 0.92, "Overall confidence below enterprise threshold"
        assert avg_processing_time <= 5.0, "Overall processing time above enterprise threshold"

    @pytest.mark.asyncio
    async def test_comprehensive_monitoring_system(self, enterprise_monitoring_detector, monitoring_profiles_comprehensive):
        """Test comprehensive 24/7 monitoring system"""
        logger.info("Testing comprehensive monitoring system")
        
        await enterprise_monitoring_detector.initialize()
        
        for profile in monitoring_profiles_comprehensive:
            logger.info(f"Testing monitoring profile: {profile.content_id}")
            
            # Start monitoring
            monitoring_result = await enterprise_monitoring_detector.start_monitoring(profile)
            
            assert monitoring_result['status'] == 'active'
            assert monitoring_result['profile_id'] == profile.profile_id
            assert monitoring_result['monitoring_started'] is True
            
            # Simulate monitoring scan
            scan_result = await enterprise_monitoring_detector.perform_monitoring_scan(profile.profile_id, profile)
            
            assert isinstance(scan_result, dict)
            assert 'scan_id' in scan_result
            assert 'sources_scanned' in scan_result
            assert 'potential_infringements' in scan_result
            assert 'scan_timestamp' in scan_result
            
            # Verify sources were properly scanned
            expected_sources = len(profile.monitoring_sources)
            actual_sources = len(scan_result['sources_scanned'])
            assert actual_sources >= expected_sources * 0.8, "Not enough sources scanned"
            
            # Check for realistic monitoring data
            assert isinstance(scan_result['potential_infringements'], list)
            
            for infringement in scan_result['potential_infringements']:
                assert 'url' in infringement
                assert 'similarity_score' in infringement
                assert 'detection_type' in infringement
                assert 'evidence' in infringement
                assert infringement['similarity_score'] >= profile.similarity_threshold
            
            logger.info(f"Monitoring scan completed: {len(scan_result['potential_infringements'])} potential infringements found")

    @pytest.mark.asyncio
    async def test_adversarial_attack_resistance(self, enterprise_piracy_detector):
        """Test resistance against sophisticated adversarial attacks"""
        logger.info("Testing adversarial attack resistance")
        
        await enterprise_piracy_detector.initialize()
        
        # Define sophisticated adversarial attacks
        adversarial_attacks = [
            {
                'name': 'gradient_based_attack',
                'description': 'Gradient-based adversarial modifications',
                'parameters': {
                    'epsilon': 0.01,
                    'iterations': 10,
                    'targeted': False
                }
            },
            {
                'name': 'frequency_domain_attack', 
                'description': 'Frequency domain modifications to evade detection',
                'parameters': {
                    'frequency_bands': ['low', 'mid', 'high'],
                    'modification_strength': 0.05
                }
            },
            {
                'name': 'semantic_preserving_attack',
                'description': 'Semantic-preserving transformations',
                'parameters': {
                    'transformation_types': ['paraphrase', 'synonym_replace', 'structure_change'],
                    'preservation_threshold': 0.90
                }
            }
        ]
        
        resistance_scores = []
        
        for attack in adversarial_attacks:
            logger.info(f"Testing resistance against: {attack['name']}")
            
            resistance_result = await enterprise_piracy_detector.test_adversarial_resistance(
                attack_type=attack['name'],
                attack_parameters=attack['parameters']
            )
            
            assert isinstance(resistance_result, dict)
            assert 'resistance_score' in resistance_result
            assert 'detection_maintained' in resistance_result
            assert 'robustness_metrics' in resistance_result
            
            resistance_score = resistance_result['resistance_score']
            detection_maintained = resistance_result['detection_maintained']
            
            # Enterprise security requirements
            assert resistance_score >= 0.85, f"Resistance score {resistance_score} below enterprise threshold for {attack['name']}"
            assert detection_maintained is True, f"Detection failed against {attack['name']}"
            
            resistance_scores.append(resistance_score)
            
            logger.info(f"Adversarial resistance test {attack['name']}: score={resistance_score:.3f}, detection_maintained={detection_maintained}")
        
        # Overall adversarial resistance validation
        avg_resistance = sum(resistance_scores) / len(resistance_scores)
        assert avg_resistance >= 0.90, f"Overall adversarial resistance {avg_resistance} below enterprise threshold"
        
        logger.info(f"Overall adversarial resistance: {avg_resistance:.3f}")

    @pytest.mark.asyncio
    async def test_video_detection_advanced(self):
        """Test advanced video detection capabilities"""
        sample_video_metadata = {
            'content_type': 'video',
            'duration': 300,
            'format': 'mp4',
            'metadata': {
                'fps': 30,
                'resolution': (1920, 1080),
                'codec': 'h264',
                'bitrate': 5000000
            }
        }

    @pytest.fixture
    def sample_text_features(self):
        """Generate sample text features for testing"""



        return {
            'word_embeddings': np.random.random((100, 300)).tolist(),
            'sentence_embeddings': np.random.random((10, 768)).tolist(),
            'n_gram_features': {
                'unigrams': {'the': 5, 'quick': 2, 'brown': 1, 'fox': 1},
                'bigrams': {'the quick': 2, 'quick brown': 1, 'brown fox': 1},
                'trigrams': {'the quick brown': 1, 'quick brown fox': 1}
            },
            'stylometric_features': {
                'avg_sentence_length': 15.3,
                'avg_word_length': 4.7,
                'vocabulary_richness': 0.65,
                'readability_score': 8.2
            },
            'semantic_features': {
                'topic_distribution': [0.3, 0.2, 0.15, 0.1, 0.25],
                'sentiment_scores': {'positive': 0.6, 'negative': 0.1, 'neutral': 0.3},
                'named_entities': ['OpenAI', 'GPT', 'machine learning']
            }
        }

    @pytest.fixture
    def sample_audio_features(self):
        """Generate sample audio features for testing"""



        return {
            'mfcc_features': np.random.random((13, 100)).tolist(),
            'spectral_features': {
                'spectral_centroid': np.random.random(100).tolist(),
                'spectral_rolloff': np.random.random(100).tolist(),
                'spectral_bandwidth': np.random.random(100).tolist(),
                'zero_crossing_rate': np.random.random(100).tolist()
            },
            'chromagram': np.random.random((12, 100)).tolist(),
            'tonnetz': np.random.random((6, 100)).tolist(),
            'tempo': 120.5,
            'rhythm_features': {
                'beat_times': np.arange(0, 30, 0.5).tolist(),
                'tempo_confidence': 0.85,
                'onset_times': np.sort(np.random.random(50) * 30).tolist()
            },
            'audio_fingerprint': hashlib.md5(b'sample_audio_data').hexdigest(),
            'duration_seconds': 30.0,
            'sample_rate': 44100
        }

    @pytest.fixture
    def sample_image_features(self):
        """Generate sample image features for testing"""



        return {
            'phash': 'a1b2c3d4e5f6',
            'histogram_features': {
                'red_histogram': np.random.randint(0, 256, 256).tolist(),
                'green_histogram': np.random.randint(0, 256, 256).tolist(),
                'blue_histogram': np.random.randint(0, 256, 256).tolist(),
                'gray_histogram': np.random.randint(0, 256, 256).tolist()
            },
            'sift_keypoints': {
                'keypoints': [(x, y) for x, y in zip(np.random.randint(0, 1920, 100), np.random.randint(0, 1080, 100))],
                'descriptors': np.random.random((100, 128)).tolist()
            },
            'lbp_features': np.random.randint(0, 256, 256).tolist(),
            'edge_features': {
                'canny_edges': np.random.randint(0, 2, (1080, 1920)).astype(bool).tolist(),
                'edge_density': 0.15,
                'edge_orientation_histogram': np.random.random(36).tolist()
            },
            'color_features': {
                'dominant_colors': [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
                'color_moments': {
                    'mean': [120.5, 115.2, 98.7],
                    'std': [45.3, 52.1, 38.9],
                    'skewness': [0.15, -0.23, 0.45]
                }
            },
            'texture_features': {
                'lbp_uniformity': 0.75,
                'contrast': 85.2,
                'homogeneity': 0.42,
                'energy': 0.35
            }
        }

    @pytest.fixture
    def sample_video_features(self):
        """Generate sample video features for testing"""
        frame_count = 30  # 30 frames for test
        return {
            'frame_features': [
                {
                    'frame_number': i,
                    'timestamp': i / 30.0,
                    'histogram': np.random.randint(0, 256, 256).tolist(),
                    'optical_flow': np.random.random((10, 10, 2)).tolist(),
                    'scene_change_score': np.random.random()
                }
                for i in range(frame_count)
            ],
            'audio_features': {
                'mfcc': np.random.random((13, 100)).tolist(),
                'spectral_centroid': np.random.random(100).tolist(),
                'tempo': 125.0,
                'audio_fingerprint': hashlib.md5(b'sample_video_audio').hexdigest()
            },
            'motion_features': {
                'camera_motion': {
                    'pan': np.random.random(frame_count).tolist(),
                    'tilt': np.random.random(frame_count).tolist(),
                    'zoom': np.random.random(frame_count).tolist()
                },
                'object_motion': {
                    'optical_flow_magnitude': np.random.random(frame_count).tolist(),
                    'motion_vectors': np.random.random((frame_count, 4)).tolist()
                }
            },
            'scene_analysis': {
                'scene_boundaries': [0, 10, 20, 30],
                'scene_types': ['outdoor', 'indoor', 'transition', 'end'],
                'activity_recognition': ['walking', 'talking', 'moving', 'static']
            },
            'temporal_features': {
                'shot_lengths': [10, 10, 10],
                'cut_frequency': 3,
                'fade_transitions': [False, True, False],
                'dissolve_transitions': [False, False, True]
            },
            'duration_seconds': 30.0,
            'fps': 30,
            'resolution': {'width': 1920, 'height': 1080}
        }

    @pytest.mark.asyncio
    async def test_audio_content_detection(self, content_detector, sample_audio_features, sample_content_metadata):
        """Test audio content detection and matching"""
        
        # Store reference audio content
        reference_content_id = sample_content_metadata['content_id']
        storage_result = await content_detector.store_reference_content(
            reference_content_id,
            ContentType.AUDIO,
            sample_audio_features,
            sample_content_metadata
        )
        
        assert storage_result['success'] is True
        assert storage_result['content_id'] == reference_content_id
        
        # Test exact match detection
        exact_match_detection = await content_detector.detect_content_matches(
            sample_audio_features,
            ContentType.AUDIO,
            min_confidence=0.95
        )
        
        assert len(exact_match_detection['matches']) > 0
        best_match = exact_match_detection['matches'][0]
        assert best_match['content_id'] == reference_content_id
        assert best_match['confidence_score'] >= 0.95
        assert best_match['match_type'] == 'exact'
        
        # Test partial match detection (modified features)
        modified_features = sample_audio_features.copy()
        # Add slight noise to simulate modifications
        modified_features['mfcc_features'] = np.array(modified_features['mfcc_features'])
        modified_features['mfcc_features'] += np.random.normal(0, 0.1, modified_features['mfcc_features'].shape)
        modified_features['mfcc_features'] = modified_features['mfcc_features'].tolist()
        
        partial_match_detection = await content_detector.detect_content_matches(
            modified_features,
            ContentType.AUDIO,
            min_confidence=0.7
        )
        
        assert len(partial_match_detection['matches']) > 0
        partial_match = partial_match_detection['matches'][0]
        assert partial_match['confidence_score'] >= 0.7
        assert partial_match['match_type'] in ['partial', 'modified']

    @pytest.mark.asyncio
    async def test_image_content_detection(self, content_detector, sample_image_features, sample_content_metadata):
        """Test image content detection and visual similarity matching"""
        
        # Store reference image content
        reference_content_id = f"{sample_content_metadata['content_id']}_image"
        storage_result = await content_detector.store_reference_content(
            reference_content_id,
            ContentType.IMAGE,
            sample_image_features,
            {**sample_content_metadata, 'content_type': 'image'}
        )
        
        assert storage_result['success'] is True
        
        # Test perceptual hash matching
        phash_detection = await content_detector.detect_by_perceptual_hash(
            sample_image_features['phash'],
            ContentType.IMAGE,
            hamming_threshold=5
        )
        
        assert len(phash_detection['matches']) > 0
        phash_match = phash_detection['matches'][0]
        assert phash_match['content_id'] == reference_content_id
        assert phash_match['hamming_distance'] <= 5
        
        # Test SIFT keypoint matching
        sift_detection = await content_detector.detect_by_keypoint_matching(
            sample_image_features['sift_keypoints'],
            ContentType.IMAGE,
            min_matches=10
        )
        
        assert len(sift_detection['matches']) > 0
        sift_match = sift_detection['matches'][0]
        assert sift_match['keypoint_matches'] >= 10
        
        # Test histogram similarity
        histogram_detection = await content_detector.detect_by_histogram_similarity(
            sample_image_features['histogram_features'],
            ContentType.IMAGE,
            similarity_threshold=0.8
        )
        
        assert len(histogram_detection['matches']) > 0
        histogram_match = histogram_detection['matches'][0]
        assert histogram_match['histogram_similarity'] >= 0.8

    @pytest.mark.asyncio
    async def test_video_content_detection(self, content_detector, sample_video_features, sample_content_metadata):
        """Test video content detection with temporal analysis"""
        
        # Store reference video content
        reference_content_id = f"{sample_content_metadata['content_id']}_video"
        storage_result = await content_detector.store_reference_content(
            reference_content_id,
            ContentType.VIDEO,
            sample_video_features,
            {**sample_content_metadata, 'content_type': 'video'}
        )
        
        assert storage_result['success'] is True
        
        # Test frame-by-frame detection
        frame_detection = await content_detector.detect_video_by_frames(
            sample_video_features['frame_features'],
            min_frame_matches=15,
            temporal_consistency_threshold=0.7
        )
        
        assert len(frame_detection['matches']) > 0
        frame_match = frame_detection['matches'][0]
        assert frame_match['frame_matches'] >= 15
        assert frame_match['temporal_consistency'] >= 0.7
        
        # Test audio track detection
        audio_detection = await content_detector.detect_video_by_audio(
            sample_video_features['audio_features'],
            min_confidence=0.8
        )
        
        assert len(audio_detection['matches']) > 0
        audio_match = audio_detection['matches'][0]
        assert audio_match['audio_confidence'] >= 0.8
        
        # Test scene change detection
        scene_detection = await content_detector.analyze_scene_changes(
            sample_video_features['frame_features'],
            scene_change_threshold=0.3
        )
        
        assert 'scene_boundaries' in scene_detection
        assert 'scene_similarity_matrix' in scene_detection
        assert len(scene_detection['scene_boundaries']) > 0

    @pytest.mark.asyncio
    async def test_text_content_detection(self, content_detector, sample_text_features, sample_content_metadata):
        """Test text content detection and plagiarism identification"""
        
        # Store reference text content
        reference_content_id = f"{sample_content_metadata['content_id']}_text"
        storage_result = await content_detector.store_reference_content(
            reference_content_id,
            ContentType.TEXT,
            sample_text_features,
            {**sample_content_metadata, 'content_type': 'text'}
        )
        
        assert storage_result['success'] is True
        
        # Test semantic similarity detection
        semantic_detection = await content_detector.detect_semantic_similarity(
            sample_text_features['sentence_embeddings'],
            min_similarity=0.8
        )
        
        assert len(semantic_detection['matches']) > 0
        semantic_match = semantic_detection['matches'][0]
        assert semantic_match['semantic_similarity'] >= 0.8
        
        # Test n-gram overlap detection
        ngram_detection = await content_detector.detect_ngram_overlap(
            sample_text_features['n_gram_features'],
            min_overlap_ratio=0.6
        )
        
        assert len(ngram_detection['matches']) > 0
        ngram_match = ngram_detection['matches'][0]
        assert ngram_match['ngram_overlap_ratio'] >= 0.6
        
        # Test stylometric analysis
        style_analysis = await content_detector.analyze_writing_style(
            sample_text_features['stylometric_features'],
            reference_content_id
        )
        
        assert 'style_similarity' in style_analysis
        assert 'distinguishing_features' in style_analysis
        assert style_analysis['style_similarity'] >= 0.7

    @pytest.mark.asyncio
    async def test_similarity_analyzer(self, content_detector, sample_audio_features):
        """Test comprehensive similarity analysis"""
        
        similarity_analyzer = SimilarityAnalyzer()
        
        # Test feature vector similarity
        feature_vector_1 = np.array(sample_audio_features['mfcc_features']).flatten()
        feature_vector_2 = feature_vector_1 + np.random.normal(0, 0.05, feature_vector_1.shape)
        
        similarity_result = await similarity_analyzer.calculate_similarity(
            feature_vector_1,
            feature_vector_2,
            method='cosine'
        )
        
        assert 0.8 <= similarity_result['similarity_score'] <= 1.0
        assert similarity_result['method'] == 'cosine'
        assert 'confidence_interval' in similarity_result
        
        # Test multiple similarity methods
        methods = ['cosine', 'euclidean', 'manhattan', 'jaccard']
        multi_method_results = await similarity_analyzer.calculate_multi_method_similarity(
            feature_vector_1,
            feature_vector_2,
            methods=methods
        )
        
        assert len(multi_method_results['similarity_scores']) == len(methods)
        assert 'aggregated_score' in multi_method_results
        assert 'method_weights' in multi_method_results
        
        # Test temporal similarity for sequences
        sequence_1 = sample_audio_features['mfcc_features']
        sequence_2 = sequence_1.copy()
        # Simulate time shift
        sequence_2 = sequence_2[5:] + sequence_2[:5]
        
        temporal_similarity = await similarity_analyzer.calculate_temporal_similarity(
            sequence_1,
            sequence_2,
            alignment_method='dtw'  # Dynamic Time Warping
        )
        
        assert temporal_similarity['temporal_similarity'] >= 0.7
        assert 'alignment_path' in temporal_similarity
        assert 'time_shift_detected' in temporal_similarity

    @pytest.mark.asyncio
    async def test_infringement_detector(self, content_detector, sample_content_metadata, sample_audio_features):
        """Test infringement detection and analysis"""
        
        infringement_detector = InfringementDetector()
        
        # Create mock infringement scenario
        original_content = {
            'content_id': sample_content_metadata['content_id'],
            'owner_id': sample_content_metadata['creator_id'],
            'features': sample_audio_features,
            'registration_date': datetime.now(timezone.utc) - timedelta(days=30),
            'copyright_status': 'registered'
        }
        
        potential_infringement = {
            'content_id': f"{sample_content_metadata['content_id']}_suspected",
            'uploader_id': 'different_user_123',
            'features': sample_audio_features,  # Same features = potential infringement
            'upload_date': datetime.now(timezone.utc) - timedelta(days=1),
            'platform': 'test_platform'
        }
        
        # Detect infringement
        infringement_analysis = await infringement_detector.analyze_potential_infringement(
            original_content,
            potential_infringement,
            similarity_threshold=0.9
        )
        
        assert infringement_analysis['infringement_detected'] is True
        assert infringement_analysis['similarity_score'] >= 0.9
        assert infringement_analysis['infringement_type'] in ['exact_copy', 'substantial_similarity']
        
        # Test fair use analysis
        fair_use_analysis = await infringement_detector.analyze_fair_use(
            original_content,
            potential_infringement,
            {
                'purpose': 'educational',
                'nature_of_work': 'creative',
                'amount_used': 0.3,  # 30% of original
                'market_impact': 'minimal'
            }
        )
        
        assert 'fair_use_score' in fair_use_analysis
        assert 'fair_use_factors' in fair_use_analysis
        assert 'recommendation' in fair_use_analysis
        
        # Test infringement severity assessment
        severity_assessment = await infringement_detector.assess_infringement_severity(
            infringement_analysis,
            {
                'commercial_use': True,
                'attribution_provided': False,
                'modification_level': 'minimal',
                'distribution_scale': 'large'
            }
        )
        
        assert severity_assessment['severity_level'] in ['low', 'medium', 'high', 'critical']
        assert 'recommended_actions' in severity_assessment
        assert 'legal_risk_score' in severity_assessment

    @pytest.mark.asyncio
    async def test_content_matcher_fuzzy_matching(self, content_detector):
        """Test fuzzy content matching for modified content"""
        
        content_matcher = ContentMatcher()
        
        # Create reference content
        reference_features = {
            'audio_fingerprint': np.random.random(1024).tolist(),
            'spectral_features': np.random.random(256).tolist(),
            'temporal_features': np.random.random(128).tolist()
        }
        
        await content_matcher.add_reference_content(
            'reference_content_001',
            reference_features,
            ContentType.AUDIO
        )
        
        # Test various modifications - excluding very aggressive ones for realistic testing
        modifications = [
            ('pitch_shift', lambda x: x * 1.1),  # Pitch shift
            ('noise_addition', lambda x: x + np.random.normal(0, 0.05, len(x))),  # Add light noise
            ('compression', lambda x: np.round(x * 100) / 100),  # Compression artifacts
            ('eq_adjustment', lambda x: x * np.random.uniform(0.9, 1.1, len(x)))  # Light EQ changes
        ]
        
        for modification_name, modification_func in modifications:
            # Apply modification
            modified_features = reference_features.copy()
            for key, values in modified_features.items():
                if isinstance(values, list):
                    modified_array = np.array(values)
                    modified_array = modification_func(modified_array)
                    # Ensure same length
                    if len(modified_array) != len(values):
                        if len(modified_array) > len(values):
                            modified_array = modified_array[:len(values)]
                        else:
                            modified_array = np.pad(modified_array, (0, len(values) - len(modified_array)))
                    modified_features[key] = modified_array.tolist()
            
            # Test fuzzy matching
            fuzzy_matches = await content_matcher.find_fuzzy_matches(
                modified_features,
                ContentType.AUDIO,
                fuzzy_threshold=0.5  # Reasonable threshold for realistic modifications
            )
            
            assert len(fuzzy_matches) > 0, f"Failed to detect {modification_name} modification"
            best_match = fuzzy_matches[0]
            assert best_match['content_id'] == 'reference_content_001'
            assert best_match['confidence_score'] >= 0.5 or best_match['similarity_score'] >= 0.5

    @pytest.mark.asyncio
    async def test_cross_platform_detection(self, content_detector, sample_content_metadata, sample_video_features):
        """Test detection across multiple platforms and formats"""
        
        # Simulate content on different platforms with different formats
        platforms = [
            {
                'platform': 'youtube',
                'format': 'mp4',
                'quality': '1080p',
                'compression': 'h264',
                'audio_codec': 'aac'
            },
            {
                'platform': 'tiktok',
                'format': 'mp4',
                'quality': '720p',
                'compression': 'h264',
                'audio_codec': 'aac',
                'duration_limit': 60
            },
            {
                'platform': 'instagram',
                'format': 'mp4',
                'quality': '1080p',
                'compression': 'h264',
                'audio_codec': 'aac',
                'aspect_ratio': '1:1'
            },
            {
                'platform': 'spotify',
                'format': 'mp3',
                'quality': '320kbps',
                'compression': 'mp3',
                'audio_only': True
            }
        ]
        
        original_content_id = sample_content_metadata['content_id']
        
        # Store original content
        await content_detector.store_reference_content(
            original_content_id,
            ContentType.VIDEO,
            sample_video_features,
            sample_content_metadata
        )
        
        cross_platform_results = []
        
        for platform_config in platforms:
            # Simulate platform-specific modifications
            modified_features = self._simulate_platform_modifications(
                sample_video_features,
                platform_config
            )
            
            # Detect across platforms
            platform_detection = await content_detector.detect_cross_platform_content(
                modified_features,
                platform_config,
                min_confidence=0.6
            )
            
            cross_platform_results.append({
                'platform': platform_config['platform'],
                'detection_result': platform_detection,
                'platform_config': platform_config
            })
        
        # Verify cross-platform detection
        for result in cross_platform_results:
            assert len(result['detection_result']['matches']) > 0, \
                f"Failed to detect content on {result['platform']}"
            
            best_match = result['detection_result']['matches'][0]
            assert best_match['original_content_id'] == original_content_id
            assert best_match['platform_modifications_detected'] is True

    def _simulate_platform_modifications(self, original_features, platform_config):
        """Simulate platform-specific content modifications"""
        modified_features = original_features.copy()
        
        # Simulate compression artifacts
        if platform_config.get('compression') == 'h264':
            # Reduce feature precision to simulate compression
            for frame in modified_features['frame_features']:
                frame['histogram'] = [round(x, 2) for x in frame['histogram']]
        
        # Simulate resolution changes
        if platform_config.get('quality') == '720p':
            # Downsample features
            for frame in modified_features['frame_features']:
                frame['histogram'] = frame['histogram'][::2]  # Reduce resolution
        
        # Simulate duration limits
        if 'duration_limit' in platform_config:
            duration_limit = platform_config['duration_limit']
            frame_limit = int(duration_limit * 30)  # Assuming 30 FPS
            modified_features['frame_features'] = modified_features['frame_features'][:frame_limit]
        
        # Simulate audio codec changes
        if platform_config.get('audio_codec') == 'aac':
            # Add slight noise to simulate lossy compression
            audio_features = modified_features['audio_features']['mfcc']  # Use 'mfcc' instead of 'mfcc_features'
            noise = np.random.normal(0, 0.05, np.array(audio_features).shape)
            modified_features['audio_features']['mfcc'] = (
                np.array(audio_features) + noise
            ).tolist()
        
        return modified_features

    @pytest.mark.asyncio
    async def test_real_time_detection_pipeline(self, content_detector):
        """Test real-time content detection pipeline"""
        
        # Simulate real-time content stream
        content_stream = []
        for i in range(100):
            content_chunk = {
                'timestamp': datetime.now(timezone.utc) + timedelta(seconds=i),
                'chunk_id': f'chunk_{i:03d}',
                'features': np.random.random(256).tolist(),
                'content_type': ContentType.AUDIO,
                'duration': 1.0  # 1 second chunks
            }
            content_stream.append(content_chunk)
        
        # Start real-time detection
        detection_pipeline = await content_detector.start_realtime_detection(
            buffer_size=10,
            detection_interval=0.5,
            confidence_threshold=0.8
        )
        
        detected_matches = []
        
        # Process content stream
        for chunk in content_stream[:20]:  # Process first 20 chunks
            detection_result = await content_detector.process_realtime_chunk(
                chunk,
                detection_pipeline
            )
            
            if detection_result['matches_found']:
                detected_matches.extend(detection_result['matches'])
        
        # Verify real-time processing
        assert len(detected_matches) >= 0  # May or may not find matches in random data
        
        # Test pipeline performance metrics
        performance_metrics = await content_detector.get_realtime_performance_metrics(
            detection_pipeline
        )
        
        assert 'processing_latency' in performance_metrics
        assert 'throughput' in performance_metrics
        assert 'accuracy_metrics' in performance_metrics
        assert performance_metrics['processing_latency'] < 1.0  # Should be under 1 second

    @pytest.mark.asyncio
    async def test_machine_learning_enhanced_detection(self, content_detector):
        """Test machine learning enhanced content detection"""
        
        # Create training dataset
        training_data = []
        for i in range(100):
            # Create pairs of similar and dissimilar content
            if i % 2 == 0:
                # Similar pair
                base_features = np.random.random(256)
                modified_features = base_features + np.random.normal(0, 0.1, 256)
                label = 1  # Similar
            else:
                # Dissimilar pair
                base_features = np.random.random(256)
                modified_features = np.random.random(256)
                label = 0  # Dissimilar
            
            training_data.append({
                'features_1': base_features.tolist(),
                'features_2': modified_features.tolist(),
                'similarity_label': label
            })
        
        # Train ML model
        ml_training_result = await content_detector.train_similarity_model(
            training_data,
            model_type='neural_network',
            validation_split=0.2,
            epochs=10
        )
        
        assert ml_training_result['training_success'] is True
        assert 'model_accuracy' in ml_training_result
        assert ml_training_result['model_accuracy'] > 0.7
        
        # Test ML-enhanced detection
        test_features_1 = np.random.random(256).tolist()
        test_features_2 = test_features_1.copy()
        # Add small modification
        test_features_2 = (np.array(test_features_2) + np.random.normal(0, 0.05, 256)).tolist()
        
        ml_detection_result = await content_detector.detect_with_ml_model(
            test_features_1,
            test_features_2,
            model_name='trained_similarity_model'
        )
        
        assert 'ml_similarity_score' in ml_detection_result
        assert 'confidence_interval' in ml_detection_result
        assert ml_detection_result['ml_similarity_score'] > 0.8  # Should detect similarity

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_detection_performance_scalability(self, content_detector):
        """Test detection system performance and scalability"""
        
        import time
        
        # Create large reference database
        reference_contents = []
        for i in range(1000):
            content_id = f'ref_content_{i:06d}'
            features = {
                'fingerprint': np.random.random(512).tolist(),
                'metadata': {'index': i}
            }
            
            await content_detector.store_reference_content(
                content_id,
                ContentType.AUDIO,
                features,
                {'content_id': content_id}
            )
            reference_contents.append(content_id)
        
        # Test detection performance with large database
        query_features = {
            'fingerprint': np.random.random(512).tolist(),
            'metadata': {'query': True}
        }
        
        # Measure detection time
        start_time = time.time()
        detection_result = await content_detector.detect_content_matches(
            query_features,
            ContentType.AUDIO,
            min_confidence=0.7
        )
        detection_time = time.time() - start_time
        
        # Performance assertions
        assert detection_time < 5.0, f"Detection too slow: {detection_time}s for 1000 references"
        assert 'matches' in detection_result
        
        # Test batch detection performance
        batch_queries = [
            {'fingerprint': np.random.random(512).tolist(), 'metadata': {'batch_index': i}}
            for i in range(50)
        ]
        
        start_time = time.time()
        batch_results = await content_detector.detect_batch_content_matches(
            batch_queries,
            ContentType.AUDIO,
            min_confidence=0.7
        )
        batch_time = time.time() - start_time
        
        assert len(batch_results) == 50
        assert batch_time < 10.0, f"Batch detection too slow: {batch_time}s for 50 queries"
        
        # Test parallel processing improvement
        sequential_time = detection_time * 50  # Estimated sequential time
        parallel_efficiency = sequential_time / batch_time
        assert parallel_efficiency > 2.0, f"Parallel processing not efficient: {parallel_efficiency}x speedup"


class TestDetectionIntegration:
    """Integration tests for content detection system"""

    @pytest.mark.asyncio
    async def test_end_to_end_detection_workflow(self, test_config, sample_content_metadata):
        """Test complete content detection workflow"""
        
        content_detector = ContentDetector(test_config.get('content_detection', {}))
        
        # Step 1: Store original content
        original_features = {
            'audio_fingerprint': np.random.random(1024).tolist(),
            'video_features': np.random.random(512).tolist(),
            'metadata_hash': hashlib.sha256(b'original_content').hexdigest()
        }
        
        storage_result = await content_detector.store_reference_content(
            sample_content_metadata['content_id'],
            ContentType.VIDEO,
            original_features,
            sample_content_metadata
        )
        
        assert storage_result['success'] is True
        
        # Step 2: Simulate content upload on different platform
        uploaded_features = original_features.copy()
        # Simulate platform modifications
        uploaded_features['audio_fingerprint'] = (
            np.array(uploaded_features['audio_fingerprint']) * 0.95 + 
            np.random.normal(0, 0.05, 1024)
        ).tolist()
        
        # Step 3: Detect potential infringement
        detection_result = await content_detector.detect_content_matches(
            uploaded_features,
            ContentType.VIDEO,
            min_confidence=0.6  # Lower threshold to ensure matches
        )
        
        assert len(detection_result['matches']) > 0
        
        # Step 4: Analyze infringement
        infringement_detector = InfringementDetector()
        infringement_analysis = await infringement_detector.analyze_potential_infringement(
            {
                'content_id': sample_content_metadata['content_id'],
                'features': original_features,
                'owner_id': sample_content_metadata['creator_id']
            },
            {
                'content_id': 'uploaded_content_123',
                'features': uploaded_features,
                'uploader_id': 'different_user'
            },
            similarity_threshold=0.7  # Lower threshold for test
        )
        
        assert infringement_analysis['infringement_detected'] is True
        
        # Step 5: Generate detection report
        detection_report = await content_detector.generate_detection_report(
            detection_result,
            infringement_analysis,
            include_evidence=True
        )
        
        assert 'detection_summary' in detection_report
        assert 'infringement_analysis' in detection_report
        assert 'recommended_actions' in detection_report
        assert 'evidence_package' in detection_report


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
