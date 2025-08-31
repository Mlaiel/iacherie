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
Comprehensive Tests for NLP Fingerprinting Module

Industrial-grade tests for AdvancedFingerprintEngine covering copyright protection,
content similarity detection, and plagiarism prevention with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import hashlib
from typing import Dict, List, Any
from unittest.mock import patch, AsyncMock
import logging

from ai.nlp.fingerprinting import (
    AdvancedContentFingerprinter, ContentProtectionSystem, ContentFingerprint,
    SimilarityMatch, CopyrightViolation, HashFingerprintGenerator
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedContentFingerprinter:
    """Comprehensive tests for AdvancedFingerprintEngine"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, fingerprint_engine):
        """Test fingerprint engine initialization"""
        assert fingerprint_engine is not None
        assert hasattr(fingerprint_engine, 'config')
        assert hasattr(fingerprint_engine, 'similarity_matcher')
        assert hasattr(fingerprint_engine, 'plagiarism_detector')
        
        # Test configuration
        config = fingerprint_engine.config
        assert 'similarity_threshold' in config
        assert 'hash_algorithms' in config
        assert 'detection_methods' in config

    @pytest.mark.asyncio
    async def test_content_fingerprint_generation(self, fingerprint_engine, sample_texts):
        """Test content fingerprint generation"""
        for language, texts in sample_texts.items():
            text = texts[0]
            
            fingerprint = await fingerprint_engine.generate_fingerprint(
                content=text,
                content_type=ContentType.POST,
                metadata={
                    'author': 'Fahed Mlaiel',
                    'platform': Platform.INSTAGRAM.value,
                    'language': language[:2]
                }
            )
            
            # Verify fingerprint structure
            assert fingerprint is not None
            assert isinstance(fingerprint, dict)
            assert 'content_hash' in fingerprint
            assert 'similarity_hash' in fingerprint
            assert 'metadata' in fingerprint
            assert 'fingerprint_id' in fingerprint
            
            # Verify hash properties
            content_hash = fingerprint['content_hash']
            similarity_hash = fingerprint['similarity_hash']
            
            assert isinstance(content_hash, str)
            assert isinstance(similarity_hash, str)
            assert len(content_hash) > 0
            assert len(similarity_hash) > 0
            
            # Hashes should be deterministic
            fingerprint2 = await fingerprint_engine.generate_fingerprint(
                content=text,
                content_type=ContentType.POST,
                metadata={
                    'author': 'Fahed Mlaiel',
                    'platform': Platform.INSTAGRAM.value,
                    'language': language[:2]
                }
            )
            
            assert fingerprint['content_hash'] == fingerprint2['content_hash']
            assert fingerprint['similarity_hash'] == fingerprint2['similarity_hash']

    @pytest.mark.asyncio
    async def test_similarity_detection(self, fingerprint_engine):
        """Test content similarity detection"""
        # Create similar contents
        original_content = "This is an amazing product that will change your life! 🌟"
        similar_content = "This is a fantastic product that will transform your life! ✨"
        different_content = "Today I went to the grocery store and bought some apples."
        
        # Generate fingerprints
        original_fp = await fingerprint_engine.generate_fingerprint(
            content=original_content,
            content_type=ContentType.POST
        )
        
        similar_fp = await fingerprint_engine.generate_fingerprint(
            content=similar_content,
            content_type=ContentType.POST
        )
        
        different_fp = await fingerprint_engine.generate_fingerprint(
            content=different_content,
            content_type=ContentType.POST
        )
        
        # Test similarity comparison
        similarity_score = await fingerprint_engine.calculate_similarity(
            fingerprint1=original_fp,
            fingerprint2=similar_fp,
            options={'detailed_analysis': True}
        )
        
        assert similarity_score is not None
        assert isinstance(similarity_score, dict)
        assert 'similarity_score' in similarity_score
        assert 'similarity_details' in similarity_score
        
        # Similar content should have high similarity
        score = similarity_score['similarity_score']
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should detect similarity
        
        # Different content should have low similarity
        different_similarity = await fingerprint_engine.calculate_similarity(
            fingerprint1=original_fp,
            fingerprint2=different_fp
        )
        
        different_score = different_similarity['similarity_score']
        assert different_score < 0.3  # Should be dissimilar

    @pytest.mark.asyncio
    async def test_plagiarism_detection(self, fingerprint_engine, sample_social_content):
        """Test plagiarism detection capabilities"""
        # Original content
        original_content = sample_social_content['instagram']['post']
        
        # Create plagiarized versions
        direct_copy = original_content
        paraphrased = original_content.replace("amazing", "incredible").replace("love", "adore")
        
        # Minor modifications
        minor_changes = original_content + " #newhashtag"
        
        # Generate fingerprints
        original_fp = await fingerprint_engine.generate_fingerprint(
            content=original_content,
            content_type=ContentType.POST,
            metadata={'author': 'Fahed Mlaiel', 'timestamp': '2025-01-01'}
        )
        
        # Test direct plagiarism
        plagiarism_result = await fingerprint_engine.detect_plagiarism(
            content=direct_copy,
            reference_fingerprints=[original_fp],
            options={
                'strict_mode': True,
                'detailed_report': True
            }
        )
        
        assert plagiarism_result is not None
        assert isinstance(plagiarism_result, dict)
        assert 'is_plagiarized' in plagiarism_result
        assert 'confidence' in plagiarism_result
        assert 'matches' in plagiarism_result
        
        # Should detect direct copy
        assert plagiarism_result['is_plagiarized'] is True
        assert plagiarism_result['confidence'] > 0.9
        
        # Test paraphrased content
        paraphrased_result = await fingerprint_engine.detect_plagiarism(
            content=paraphrased,
            reference_fingerprints=[original_fp],
            options={'semantic_analysis': True}
        )
        
        # Should detect paraphrasing with moderate confidence
        assert paraphrased_result['confidence'] > 0.5

    @pytest.mark.asyncio
    async def test_copyright_protection(self, fingerprint_engine):
        """Test copyright protection features"""
        protected_content = """
        Exclusive content created by Fahed Mlaiel for IA Influencer Agent Platform.
        This innovative approach to content creation represents months of research and development.
        The methodology described here is proprietary and confidential.
        """
        
        # Register copyright
        copyright_registration = await fingerprint_engine.register_copyright(
            content=protected_content,
            owner_info={
                'name': 'Fahed Mlaiel',
                'email': 'mlaiel@live.de',
                'organization': 'IA Influencer Agent Platform'
            },
            protection_level='maximum',
            options={
                'generate_certificate': True,
                'blockchain_registration': False,  # Skip for tests
                'legal_metadata': True
            }
        )
        
        assert copyright_registration is not None
        assert 'registration_id' in copyright_registration
        assert 'certificate' in copyright_registration
        assert 'legal_metadata' in copyright_registration
        assert 'protection_level' in copyright_registration
        
        # Test unauthorized use detection
        unauthorized_use = protected_content + " Modified slightly for unauthorized use."
        
        violation_check = await fingerprint_engine.check_copyright_violation(
            content=unauthorized_use,
            registered_fingerprints=[copyright_registration['fingerprint']],
            options={'legal_analysis': True}
        )
        
        assert violation_check is not None
        assert 'is_violation' in violation_check
        assert 'severity' in violation_check
        assert 'legal_recommendations' in violation_check
        
        # Should detect violation
        assert violation_check['is_violation'] is True
        assert violation_check['severity'] in ['low', 'medium', 'high', 'critical']

    @pytest.mark.asyncio
    async def test_content_versioning(self, fingerprint_engine):
        """Test content versioning and evolution tracking"""
        # Original version
        v1_content = "Original content about digital marketing strategies."
        
        # Version 2 - minor updates
        v2_content = "Updated content about digital marketing strategies and trends."
        
        # Version 3 - major revision
        v3_content = "Comprehensive guide to digital marketing strategies, trends, and best practices."
        
        versions = [v1_content, v2_content, v3_content]
        fingerprints = []
        
        # Generate fingerprints for each version
        for i, content in enumerate(versions):
            fp = await fingerprint_engine.generate_fingerprint(
                content=content,
                content_type=ContentType.POST,
                metadata={
                    'version': f'v{i+1}',
                    'author': 'Fahed Mlaiel',
                    'evolution_tracking': True
                }
            )
            fingerprints.append(fp)
        
        # Track content evolution
        evolution = await fingerprint_engine.track_content_evolution(
            fingerprints=fingerprints,
            options={
                'calculate_changes': True,
                'identify_patterns': True
            }
        )
        
        assert evolution is not None
        assert 'evolution_timeline' in evolution
        assert 'change_analysis' in evolution
        assert 'version_relationships' in evolution
        
        timeline = evolution['evolution_timeline']
        assert len(timeline) == 3
        
        # Should show progression
        for i, version_info in enumerate(timeline):
            assert version_info['version'] == f'v{i+1}'
            if i > 0:
                assert 'similarity_to_previous' in version_info

    @pytest.mark.asyncio
    async def test_batch_fingerprinting(self, fingerprint_engine, performance_test_data):
        """Test batch fingerprinting capabilities"""
        texts = performance_test_data['small_batch']
        
        start_time = time.time()
        batch_fingerprints = await fingerprint_engine.generate_batch_fingerprints(
            contents=texts,
            content_type=ContentType.POST,
            options={
                'parallel_processing': True,
                'include_metadata': True
            }
        )
        batch_time = time.time() - start_time
        
        # Verify batch processing
        assert len(batch_fingerprints) == len(texts)
        assert all(fp is not None for fp in batch_fingerprints)
        
        # Check fingerprint structure
        for fp in batch_fingerprints:
            assert 'content_hash' in fp
            assert 'similarity_hash' in fp
            assert 'fingerprint_id' in fp
        
        # Should be efficient
        avg_time_per_item = batch_time / len(texts)
        assert avg_time_per_item < 0.5  # Should fingerprint quickly

    @pytest.mark.asyncio
    async def test_advanced_similarity_algorithms(self, fingerprint_engine):
        """Test advanced similarity detection algorithms"""
        # Test with different types of content modifications
        test_cases = [
            {
                'original': "The quick brown fox jumps over the lazy dog.",
                'modified': "A fast brown fox leaps over the sleepy dog.",
                'expected_similarity': 'high'  # Semantic similarity
            },
            {
                'original': "Check out my new blog post about AI trends!",
                'modified': "Look at my latest article on artificial intelligence trends!",
                'expected_similarity': 'high'  # Paraphrasing
            },
            {
                'original': "Beautiful sunset at the beach 🌅",
                'modified': "Gorgeous sunrise at the mountains ⛰️",
                'expected_similarity': 'medium'  # Similar structure, different content
            },
            {
                'original': "Programming in Python is fun and efficient.",
                'modified': "Cooking pasta requires water and heat.",
                'expected_similarity': 'low'  # Completely different
            }
        ]
        
        for test_case in test_cases:
            original_fp = await fingerprint_engine.generate_fingerprint(
                content=test_case['original'],
                content_type=ContentType.POST
            )
            
            modified_fp = await fingerprint_engine.generate_fingerprint(
                content=test_case['modified'],
                content_type=ContentType.POST
            )
            
            similarity = await fingerprint_engine.calculate_similarity(
                fingerprint1=original_fp,
                fingerprint2=modified_fp,
                options={
                    'algorithm': 'advanced',
                    'semantic_analysis': True,
                    'structural_analysis': True
                }
            )
            
            score = similarity['similarity_score']
            expected = test_case['expected_similarity']
            
            if expected == 'high':
                assert score > 0.6, f"Expected high similarity, got {score}"
            elif expected == 'medium':
                assert 0.3 <= score <= 0.7, f"Expected medium similarity, got {score}"
            elif expected == 'low':
                assert score < 0.4, f"Expected low similarity, got {score}"

    @pytest.mark.asyncio
    async def test_multilingual_fingerprinting(self, fingerprint_engine, sample_texts):
        """Test multilingual content fingerprinting"""
        # Test same content in different languages
        english_text = "I love this amazing product! It's fantastic!"
        german_text = "Ich liebe dieses erstaunliche Produkt! Es ist fantastisch!"
        french_text = "J'adore ce produit incroyable! C'est fantastique!"
        
        multilingual_contents = [
            ('en', english_text),
            ('de', german_text),
            ('fr', french_text)
        ]
        
        fingerprints = []
        
        for lang, content in multilingual_contents:
            fp = await fingerprint_engine.generate_fingerprint(
                content=content,
                content_type=ContentType.POST,
                metadata={'language': lang},
                options={
                    'multilingual_analysis': True,
                    'cross_language_detection': True
                }
            )
            fingerprints.append(fp)
        
        # Test cross-language similarity
        en_de_similarity = await fingerprint_engine.calculate_similarity(
            fingerprint1=fingerprints[0],  # English
            fingerprint2=fingerprints[1],  # German
            options={
                'cross_language': True,
                'semantic_translation': True
            }
        )
        
        # Should detect semantic similarity across languages
        cross_lang_score = en_de_similarity['similarity_score']
        assert cross_lang_score > 0.4  # Should detect translation similarity

    @pytest.mark.asyncio
    async def test_content_authenticity_verification(self, fingerprint_engine):
        """Test content authenticity verification"""
        # Original authentic content
        authentic_content = """
        Original research findings from our IA Influencer Agent Platform study.
        Methodology: We analyzed 10,000 social media posts across multiple platforms.
        Results: 85% improvement in engagement when using AI-optimized content.
        Conclusion: AI-assisted content creation significantly enhances performance.
        """
        
        # Register as authentic
        authenticity_registration = await fingerprint_engine.register_authentic_content(
            content=authentic_content,
            author_info={
                'name': 'Fahed Mlaiel',
                'credentials': 'Lead AI Developer',
                'verification_method': 'digital_signature'
            },
            options={
                'blockchain_verification': False,  # Skip for tests
                'timestamp_verification': True,
                'source_verification': True
            }
        )
        
        assert authenticity_registration is not None
        assert 'authenticity_certificate' in authenticity_registration
        assert 'verification_id' in authenticity_registration
        
        # Test authenticity verification
        verification_result = await fingerprint_engine.verify_authenticity(
            content=authentic_content,
            registered_certificates=[authenticity_registration['authenticity_certificate']],
            options={'detailed_verification': True}
        )
        
        assert verification_result is not None
        assert 'is_authentic' in verification_result
        assert 'confidence' in verification_result
        assert 'verification_details' in verification_result
        
        # Should verify as authentic
        assert verification_result['is_authentic'] is True
        assert verification_result['confidence'] > 0.9

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, fingerprint_engine, benchmark_config):
        """Test fingerprinting performance benchmarks"""
        # Test single fingerprint generation performance
        content = "Test content for performance benchmarking of fingerprint generation."
        
        start_time = time.time()
        fingerprint = await fingerprint_engine.generate_fingerprint(
            content=content,
            content_type=ContentType.POST
        )
        generation_time = time.time() - start_time
        
        # Should meet performance requirements
        max_time = benchmark_config['max_processing_time']
        assert generation_time < max_time, f"Fingerprinting took {generation_time:.3f}s, max: {max_time}s"
        
        # Test batch performance
        batch_contents = [f"Content {i} for batch performance testing." for i in range(20)]
        
        start_time = time.time()
        batch_fingerprints = await fingerprint_engine.generate_batch_fingerprints(
            contents=batch_contents,
            content_type=ContentType.POST,
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(batch_contents) / batch_time
        min_throughput = benchmark_config['throughput_threshold']
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, fingerprint_engine):
        """Test error handling and edge cases"""
        # Test empty content
        fingerprint = await fingerprint_engine.generate_fingerprint(
            content="",
            content_type=ContentType.POST
        )
        assert fingerprint is not None  # Should handle gracefully
        
        # Test very long content
        long_content = "Long content " * 10000
        
        fingerprint = await fingerprint_engine.generate_fingerprint(
            content=long_content,
            content_type=ContentType.POST
        )
        assert fingerprint is not None
        assert 'content_hash' in fingerprint
        
        # Test special characters
        special_content = "Content with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?"
        
        fingerprint = await fingerprint_engine.generate_fingerprint(
            content=special_content,
            content_type=ContentType.POST
        )
        assert fingerprint is not None

    @pytest.mark.asyncio
    async def test_fingerprint_database_operations(self, fingerprint_engine):
        """Test fingerprint database operations"""
        # Generate test fingerprints
        test_contents = [
            "Content 1 for database testing",
            "Content 2 for database testing", 
            "Content 3 for database testing"
        ]
        
        fingerprints = []
        for content in test_contents:
            fp = await fingerprint_engine.generate_fingerprint(
                content=content,
                content_type=ContentType.POST
            )
            fingerprints.append(fp)
        
        # Test storage
        storage_result = await fingerprint_engine.store_fingerprints(
            fingerprints=fingerprints,
            options={'batch_insert': True}
        )
        
        assert storage_result is not None
        assert 'stored_count' in storage_result
        assert storage_result['stored_count'] == len(fingerprints)
        
        # Test retrieval
        for fp in fingerprints:
            retrieved = await fingerprint_engine.retrieve_fingerprint(
                fingerprint_id=fp['fingerprint_id']
            )
            
            assert retrieved is not None
            assert retrieved['fingerprint_id'] == fp['fingerprint_id']
            assert retrieved['content_hash'] == fp['content_hash']

class TestContentFingerprint:
    """Test content fingerprint data structure"""
    
    def test_fingerprint_creation(self):
        """Test fingerprint creation"""
        fingerprint = ContentFingerprint(
            content_hash="abcd1234",
            similarity_hash="efgh5678",
            metadata={'author': 'Fahed Mlaiel'},
            timestamp=time.time()
        )
        
        assert fingerprint.content_hash == "abcd1234"
        assert fingerprint.similarity_hash == "efgh5678"
        assert fingerprint.metadata['author'] == 'Fahed Mlaiel'

class TestSimilarityMatcher:
    """Test similarity matcher"""
    
    @pytest.mark.asyncio
    async def test_similarity_matcher_initialization(self):
        """Test similarity matcher initialization"""
        matcher = SimilarityMatcher()
        assert matcher is not None
        assert hasattr(matcher, 'calculate_similarity')

class TestPlagiarismDetector:
    """Test plagiarism detector"""
    
    @pytest.mark.asyncio
    async def test_plagiarism_detector_initialization(self):
        """Test plagiarism detector initialization"""
        detector = PlagiarismDetector()
        assert detector is not None
        assert hasattr(detector, 'detect_plagiarism')

class TestFingerprintConfig:
    """Test fingerprint configuration"""
    
    def test_config_creation(self):
        """Test fingerprint configuration creation"""
        config = FingerprintConfig(
            similarity_threshold=0.8,
            hash_algorithms=['md5', 'sha256'],
            detection_methods=['exact', 'fuzzy', 'semantic']
        )
        
        assert config.similarity_threshold == 0.8
        assert 'md5' in config.hash_algorithms
        assert 'semantic' in config.detection_methods
