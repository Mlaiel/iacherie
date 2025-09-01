# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
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
Comprehensive Tests for NLP Generators Module

Industrial-grade tests for AdvancedContentGenerator covering content generation,
optimization, and platform-specific adaptation with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, List, Any
from unittest.mock import patch, AsyncMock
import logging

from ai.nlp.generators import (
    SocialPostGenerator, ContentGenerationPipeline, GenerationRequest,
    GenerationResult, ContentTemplate, ContentType, ToneType
)
try:
    from ai.nlp.utils import Platform, Language
except ImportError:
    # Fallback definitions
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})

logger = logging.getLogger(__name__)

class TestAdvancedContentGenerator:
    """
Comprehensive tests for AdvancedContentGenerator"""
    
    @pytest.mark.asyncio
    async def test_generator_initialization(self, content_generator):
        """
Test generator initialization and configuration"""
        assert content_generator is not None
        assert hasattr(content_generator, 'config')
        assert hasattr(content_generator, 'models')
        assert hasattr(content_generator, 'templates')
        
        # Test configuration
        config = content_generator.config
        assert 'generation_models' in config
        assert 'platforms' in config
        assert 'languages' in config

    @pytest.mark.asyncio
    async def test_content_generation_basic(self, content_generator):
        """
Test basic content generation"""
        prompt = "Create content about sustainable fashion"
        
        generated = await content_generator.generate_content(
            prompt=prompt,
            content_type=ContentType.POST,
            platform=Platform.INSTAGRAM,
            language='en',
            options={
                'creativity_level': 0.7,
                'length': 'medium',
                'include_hashtags': True,
                'include_emojis': True
            }
        )
        
        # Verify generated content structure
        assert generated is not None
        assert isinstance(generated, dict)
        assert 'content' in generated
        assert 'metadata' in generated
        
        content = generated['content']
        assert isinstance(content, str)
        assert len(content) > 0
        
        # Should include hashtags and emojis as requested
        metadata = generated['metadata']
        assert 'has_hashtags' in metadata
        assert 'has_emojis' in metadata

    @pytest.mark.asyncio
    async def test_platform_specific_generation(self, content_generator):
        """Test platform-specific content generation"""
        platforms_to_test = [
            (Platform.INSTAGRAM, "Share your daily skincare routine"),
            (Platform.TIKTOK, "Create a viral dance challenge"),
            (Platform.TWITTER, "Tweet about climate change awareness"),
            (Platform.YOUTUBE, "Explain quantum computing basics"),
            (Platform.LINKEDIN, "Share professional networking tips")
        ]
        
        for platform, prompt in platforms_to_test:
            generated = await content_generator.generate_for_platform(
                prompt=prompt,
                platform=platform,
                language='en',
                options={
                    'optimize_for_platform': True,
                    'follow_best_practices': True,
                    'include_call_to_action': True
                }
            )
            
            assert generated is not None
            assert 'content' in generated
            assert 'platform_optimization' in generated
            
            content = generated['content']
            optimization = generated['platform_optimization']
            
            # Platform-specific validations
            if platform == Platform.TWITTER:
                # Should respect character limit
                assert len(content) <= 280
                assert optimization['character_count'] <= 280
            
            elif platform == Platform.INSTAGRAM:
                # Should include relevant hashtags
                assert '#' in content or 'hashtags' in generated
                assert optimization['hashtag_count'] >= 0
            
            elif platform == Platform.LINKEDIN:
                # Should be professional tone
                assert optimization['tone'] in ['professional', 'formal', 'business']
            
            elif platform == Platform.TIKTOK:
                # Should be engaging and trend-focused
                assert optimization['engagement_score'] > 0.5
                assert 'viral_elements' in optimization

    @pytest.mark.asyncio
    async def test_multilingual_generation(self, content_generator):
        """Test multilingual content generation"""
        languages_to_test = ['en', 'de', 'fr', 'es']
        prompt = "Create content about healthy cooking"
        
        for language in languages_to_test:
            generated = await content_generator.generate_content(
                prompt=prompt,
                content_type=ContentType.POST,
                platform=Platform.INSTAGRAM,
                language=language,
                options={
                    'cultural_adaptation': True,
                    'local_trends': True
                }
            )
            
            assert generated is not None
            assert 'content' in generated
            assert 'language_info' in generated
            
            content = generated['content']
            language_info = generated['language_info']
            
            # Verify language
            assert language_info['generated_language'] == language
            assert language_info['confidence'] > 0.7
            
            # Content should be appropriate length
            assert len(content) > 10
            
            # Should include cultural elements for non-English
            if language != 'en':
                assert language_info['cultural_adaptation'] is True

    @pytest.mark.asyncio
    async def test_content_variation_generation(self, content_generator):
        """Test generation of content variations"""
        base_content = "Discover the latest trends in sustainable fashion"
        
        variations = await content_generator.generate_variations(
            base_content=base_content,
            num_variations=5,
            platform=Platform.INSTAGRAM,
            options={
                'variation_type': 'diverse',
                'maintain_core_message': True,
                'different_styles': True
            }
        )
        
        assert variations is not None
        assert isinstance(variations, list)
        assert len(variations) == 5
        
        # Each variation should be different but related
        for i, variation in enumerate(variations):
            assert 'content' in variation
            assert 'variation_id' in variation
            assert 'style' in variation
            
            content = variation['content']
            assert len(content) > 0
            assert content != base_content  # Should be different from original
            
            # Should maintain core message about sustainable fashion
            assert any(word in content.lower() for word in ['sustainable', 'fashion', 'trend'])

    @pytest.mark.asyncio
    async def test_hashtag_generation(self, content_generator):
        """Test hashtag generation functionality"""
        content = "Just finished an amazing workout session at the gym!"
        
        hashtags = await content_generator.generate_hashtags(
            content=content,
            platform=Platform.INSTAGRAM,
            options={
                'num_hashtags': 10,
                'trending_hashtags': True,
                'niche_hashtags': True,
                'broad_hashtags': True
            }
        )
        
        assert hashtags is not None
        assert isinstance(hashtags, dict)
        assert 'hashtags' in hashtags
        assert 'categories' in hashtags
        
        hashtag_list = hashtags['hashtags']
        categories = hashtags['categories']
        
        # Should generate requested number of hashtags
        assert len(hashtag_list) <= 10
        assert all(tag.startswith('#') for tag in hashtag_list)
        
        # Should categorize hashtags
        assert isinstance(categories, dict)
        expected_categories = ['trending', 'niche', 'broad']
        assert any(cat in categories for cat in expected_categories)
        
        # Should be relevant to fitness/workout content
        workout_related = ['#fitness', '#gym', '#workout', '#training', '#exercise']
        assert any(any(keyword in tag.lower() for keyword in ['fitness', 'gym', 'workout', 'training', 'exercise']) 
                  for tag in hashtag_list)

    @pytest.mark.asyncio
    async def test_caption_generation(self, content_generator):
        """Test caption generation for different content types"""
        content_scenarios = [
            {
                'scenario': 'food_photo',
                'context': 'Photo of homemade pasta with fresh tomatoes',
                'platform': Platform.INSTAGRAM,
                'expected_elements': ['food', 'pasta', 'homemade']
            },
            {
                'scenario': 'travel_video',
                'context': 'Video from beach vacation in Bali',
                'platform': Platform.TIKTOK,
                'expected_elements': ['travel', 'beach', 'vacation', 'bali']
            },
            {
                'scenario': 'product_launch',
                'context': 'Launching new eco-friendly skincare line',
                'platform': Platform.LINKEDIN,
                'expected_elements': ['launch', 'skincare', 'eco-friendly']
            }
        ]
        
        for scenario in content_scenarios:
            caption = await content_generator.generate_caption(
                context=scenario['context'],
                platform=scenario['platform'],
                options={
                    'tone': 'engaging',
                    'include_call_to_action': True,
                    'optimize_engagement': True
                }
            )
            
            assert caption is not None
            assert isinstance(caption, dict)
            assert 'caption' in caption
            assert 'engagement_elements' in caption
            
            caption_text = caption['caption']
            engagement_elements = caption['engagement_elements']
            
            # Should include relevant keywords
            expected_elements = scenario['expected_elements']
            assert any(element in caption_text.lower() for element in expected_elements)
            
            # Should have engagement elements
            assert 'call_to_action' in engagement_elements
            assert engagement_elements['call_to_action'] is True

    @pytest.mark.asyncio
    async def test_story_generation(self, content_generator):
        """
Test story content generation"""
        story_prompts = [
            "Behind the scenes of product photoshoot",
            "Daily morning routine for productivity",
            "Quick recipe tutorial"
        ]
        
        for prompt in story_prompts:
            story = await content_generator.generate_story_content(
                prompt=prompt,
                platform=Platform.INSTAGRAM,
                options={
                    'story_type': 'tutorial',
                    'include_interactive_elements': True,
                    'optimize_for_retention': True
                }
            )
            
            assert story is not None
            assert isinstance(story, dict)
            assert 'story_content' in story
            assert 'interactive_elements' in story
            assert 'retention_tips' in story
            
            story_content = story['story_content']
            interactive_elements = story['interactive_elements']
            
            # Should have engaging story content
            assert len(story_content) > 0
            
            # Should suggest interactive elements
            assert isinstance(interactive_elements, list)
            if len(interactive_elements) > 0:
                element = interactive_elements[0]
                assert 'type' in element
                assert 'description' in element

    @pytest.mark.asyncio
    async def test_thread_generation(self, content_generator):
        """Test Twitter thread generation"""
        topic = "The future of artificial intelligence in creative industries"
        
        thread = await content_generator.generate_twitter_thread(
            topic=topic,
            num_tweets=5,
            options={
                'educational_tone': True,
                'include_examples': True,
                'engage_audience': True
            }
        )
        
        assert thread is not None
        assert isinstance(thread, dict)
        assert 'tweets' in thread
        assert 'thread_metadata' in thread
        
        tweets = thread['tweets']
        metadata = thread['thread_metadata']
        
        # Should generate requested number of tweets
        assert len(tweets) == 5
        
        # Each tweet should be within character limit
        for i, tweet in enumerate(tweets):
            assert 'content' in tweet
            assert 'tweet_number' in tweet
            assert len(tweet['content']) <= 280
            
            # First tweet should introduce the topic
            if i == 0:
                assert any(word in tweet['content'].lower() for word in ['ai', 'artificial', 'intelligence', 'creative'])

    @pytest.mark.asyncio
    async def test_content_optimization(self, content_generator):
        """Test content optimization for engagement"""
        base_content = "Check out my new blog post about productivity tips"
        
        optimized = await content_generator.optimize_content(
            content=base_content,
            platform=Platform.INSTAGRAM,
            optimization_goals=['engagement', 'reach', 'conversion'],
            options={
                'a_b_test_variants': True,
                'include_trends': True,
                'optimize_timing': True
            }
        )
        
        assert optimized is not None
        assert isinstance(optimized, dict)
        assert 'optimized_content' in optimized
        assert 'optimization_score' in optimized
        assert 'suggestions' in optimized
        
        optimized_content = optimized['optimized_content']
        optimization_score = optimized['optimization_score']
        suggestions = optimized['suggestions']
        
        # Should improve upon original content
        assert len(optimized_content) > len(base_content)
        assert 0.0 <= optimization_score <= 1.0
        
        # Should provide actionable suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_batch_generation(self, content_generator, performance_test_data):
        """Test batch content generation"""
        prompts = [
            "Create content about morning routines",
            "Share healthy recipe ideas", 
            "Discuss remote work productivity",
            "Review latest tech gadgets",
            "Promote sustainable living"
        ]
        
        start_time = time.time()
        batch_results = await content_generator.generate_batch(
            prompts=prompts,
            content_type=ContentType.POST,
            platform=Platform.INSTAGRAM,
            language='en',
            options={
                'parallel_processing': True,
                'consistent_style': True
            }
        )
        batch_time = time.time() - start_time
        
        # Verify batch generation
        assert len(batch_results) == len(prompts)
        assert all(result is not None for result in batch_results)
        
        # Check consistency across generated content
        styles = [result['metadata']['style'] for result in batch_results if 'style' in result.get('metadata', {})]
        if len(styles) > 1:
            # Should maintain consistent style
            assert len(set(styles)) <= 2  # Allow some variation
        
        # Should be efficient
        avg_time_per_item = batch_time / len(prompts)
        assert avg_time_per_item < 5.0  # Should generate each item reasonably quickly

    @pytest.mark.asyncio
    async def test_template_based_generation(self, content_generator):
        """Test template-based content generation"""
        templates_to_test = [
            {
                'template_type': 'product_showcase',
                'variables': {
                    'product_name': 'Organic Face Cream',
                    'key_benefit': 'hydration',
                    'price': '$29.99'
                },
                'platform': Platform.INSTAGRAM
            },
            {
                'template_type': 'tutorial_intro',
                'variables': {
                    'skill': 'photography',
                    'difficulty': 'beginner',
                    'duration': '10 minutes'
                },
                'platform': Platform.YOUTUBE
            }
        ]
        
        for template_config in templates_to_test:
            generated = await content_generator.generate_from_template(
                template_type=template_config['template_type'],
                variables=template_config['variables'],
                platform=template_config['platform'],
                options={
                    'customize_tone': True,
                    'add_personal_touch': True
                }
            )
            
            assert generated is not None
            assert 'content' in generated
            assert 'template_info' in generated
            
            content = generated['content']
            template_info = generated['template_info']
            
            # Should include provided variables
            variables = template_config['variables']
            for key, value in variables.items():
                if isinstance(value, str):
                    assert value.lower() in content.lower()

    @pytest.mark.asyncio
    async def test_ai_model_integration(self, content_generator):
        """
Test AI model integration for generation"""
        prompt = "Create engaging content about climate change awareness"
        
        # Test with different AI models
        models_to_test = ['gpt', 'claude', 'local']
        
        for model in models_to_test:
            try:
                generated = await content_generator.generate_with_model(
                    prompt=prompt,
                    model=model,
                    platform=Platform.INSTAGRAM,
                    options={
                        'temperature': 0.7,
                        'max_tokens': 500,
                        'creativity_boost': True
                    }
                )
                
                assert generated is not None
                assert 'content' in generated
                assert 'model_info' in generated
                
                model_info = generated['model_info']
                assert model_info['model_used'] == model
                assert 'generation_time' in model_info
                
            except Exception as e:
                # Some models might not be available in test environment
                logger.warning(f"Model {model} not available: {e}")

    @pytest.mark.asyncio
    async def test_content_personalization(self, content_generator):
        """Test content personalization features"""
        user_profile = {
            'interests': ['fitness', 'healthy_eating', 'travel'],
            'tone_preference': 'casual',
            'platform_activity': {
                Platform.INSTAGRAM: 'high',
                Platform.TIKTOK: 'medium'
            },
            'audience_demographics': {
                'age_group': '25-35',
                'primary_language': 'en'
            }
        }
        
        prompt = "Create content about weekend activities"
        
        personalized = await content_generator.generate_personalized_content(
            prompt=prompt,
            user_profile=user_profile,
            platform=Platform.INSTAGRAM,
            options={
                'use_interests': True,
                'match_tone': True,
                'target_audience': True
            }
        )
        
        assert personalized is not None
        assert 'content' in personalized
        assert 'personalization_info' in personalized
        
        content = personalized['content']
        personalization_info = personalized['personalization_info']
        
        # Should incorporate user interests
        interests = user_profile['interests']
        interest_found = any(interest in content.lower() for interest in interests)
        assert interest_found or personalization_info['interests_incorporated'] > 0
        
        # Should match tone preference
        assert personalization_info['tone_match'] == 'casual'

    @pytest.mark.asyncio
    async def test_content_scheduling_optimization(self, content_generator):
        """Test content scheduling and timing optimization"""
        content = "Sharing my morning workout routine!"
        
        schedule_optimization = await content_generator.optimize_posting_schedule(
            content=content,
            platform=Platform.INSTAGRAM,
            timezone='UTC',
            target_audience='fitness_enthusiasts',
            options={
                'analyze_optimal_times': True,
                'consider_audience_activity': True,
                'suggest_best_days': True
            }
        )
        
        assert schedule_optimization is not None
        assert 'optimal_times' in schedule_optimization
        assert 'best_days' in schedule_optimization
        assert 'audience_activity' in schedule_optimization
        
        optimal_times = schedule_optimization['optimal_times']
        best_days = schedule_optimization['best_days']
        
        # Should suggest reasonable posting times
        assert isinstance(optimal_times, list)
        assert len(optimal_times) > 0
        assert all(0 <= time <= 23 for time in optimal_times)
        
        # Should suggest appropriate days
        assert isinstance(best_days, list)
        assert len(best_days) > 0
        assert all(day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] 
                  for day in best_days)

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, content_generator, benchmark_config):
        """Test generator performance benchmarks"""
        # Test single generation performance
        prompt = "Create content about digital marketing trends"
        
        start_time = time.time()
        generated = await content_generator.generate_content(
            prompt=prompt,
            content_type=ContentType.POST,
            platform=Platform.LINKEDIN,
            language='en'
        )
        generation_time = time.time() - start_time
        
        # Should meet performance requirements
        max_time = benchmark_config['max_processing_time'] * 3  # Allow more time for generation
        assert generation_time < max_time, f"Generation took {generation_time:.3f}s, max: {max_time}s"
        
        # Test batch generation performance
        prompts = [f"Content idea {i}" for i in range(10)]
        
        start_time = time.time()
        batch_results = await content_generator.generate_batch(
            prompts=prompts,
            content_type=ContentType.POST,
            platform=Platform.INSTAGRAM,
            language='en',
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(prompts) / batch_time
        min_throughput = 2  # 2 generations per second minimum
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, content_generator):
        """Test error handling and edge cases"""
        # Test empty prompt
        generated = await content_generator.generate_content(
            prompt="",
            content_type=ContentType.POST,
            platform=Platform.INSTAGRAM,
            language='en'
        )
        assert generated is not None  # Should handle gracefully
        
        # Test very long prompt
        long_prompt = "Create content about " + "sustainability " * 100
        
        generated = await content_generator.generate_content(
            prompt=long_prompt,
            content_type=ContentType.POST,
            platform=Platform.TWITTER,
            language='en'
        )
        assert generated is not None
        
        # Test invalid language
        generated = await content_generator.generate_content(
            prompt="Test prompt",
            content_type=ContentType.POST,
            platform=Platform.INSTAGRAM,
            language='invalid'
        )
        assert generated is not None  # Should default to English

class TestContentGenerator:
    """Test base content generator"""
    
    @pytest.mark.asyncio
    async def test_content_generator_initialization(self):
        """
Test content generator initialization"""
        generator = ContentGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate')

class TestCaptionGenerator:
    """
Test specialized caption generator"""
    
    @pytest.mark.asyncio
    async def test_caption_generator_initialization(self):
        """
Test caption generator initialization"""
        generator = CaptionGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_caption')

class TestHashtagGenerator:
    """
Test specialized hashtag generator"""
    
    @pytest.mark.asyncio
    async def test_hashtag_generator_initialization(self):
        """
Test hashtag generator initialization"""
        generator = HashtagGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_hashtags')

    @pytest.mark.asyncio
    async def test_hashtag_generation_specific(self):
        """
Test specific hashtag generation"""
        generator = HashtagGenerator()
        
        content = "Beautiful sunset at the beach"
        
        hashtags = await generator.generate_hashtags(
            content=content,
            platform=Platform.INSTAGRAM,
            num_hashtags=15,
            options={
                'include_trending': True,
                'include_niche': True
            }
        )
        
        assert hashtags is not None
        assert isinstance(hashtags, list)
        assert len(hashtags) <= 15
        assert all(tag.startswith('#') for tag in hashtags)

class TestGenerationConfig:
    """Test generation configuration"""
    
    def test_config_creation(self):
        """
Test generation configuration creation"""
        config = GenerationConfig(
            models=['gpt-4', 'claude'],
            platforms=[Platform.INSTAGRAM, Platform.TIKTOK],
            languages=['en', 'de'],
            creativity_level=0.8
        )
        
        assert config.models == ['gpt-4', 'claude']
        assert Platform.INSTAGRAM in config.platforms
        assert 'en' in config.languages
        assert config.creativity_level == 0.8

class TestGeneratedContent:
    """
Test generated content structure"""
    
    def test_generated_content_creation(self):
        """
Test generated content creation"""
        content = GeneratedContent(
            content="Generated content text",
            platform=Platform.INSTAGRAM,
            language='en',
            metadata={
                'generation_time': 2.5,
                'model_used': 'gpt-4',
                'creativity_score': 0.8
            }
        )
        
        assert content.content == "Generated content text"
        assert content.platform == Platform.INSTAGRAM
        assert content.language == 'en'
        assert content.metadata['generation_time'] == 2.5
