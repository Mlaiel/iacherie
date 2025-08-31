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
Text Quality Analysis Tests

Comprehensive test suite for professional text quality assessment with advanced linguistic analysis,
grammar evaluation, readability scoring, SEO optimization, and content intelligence validation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Project Team Specialties:
✅ Lead Dev + AI Developer Architect - Fahed Mlaiel
✅ Senior Backend Developer (Python/FastAPI/Django) - Fahed Mlaiel  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face) - Fahed Mlaiel
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB) - Fahed Mlaiel
✅ Backend Security Specialist - Fahed Mlaiel
✅ Microservices Architect - Fahed Mlaiel
✅ Audio Developer - Fahed Mlaiel
✅ DevOps Engineer - Fahed Mlaiel
✅ AI Prompt Engineer - Fahed Mlaiel

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

ANYONE WHO THINKS OF STEALING THE IDEA, CONCEPT, OR CODE WITHOUT MY PERSONAL, CLEAR, 
AND WRITTEN AUTHORIZATION WILL FACE SEVERE LEGAL CONSEQUENCES.

Contact: Fahed Mlaiel - mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import TestCase
from typing import Dict, List, Any, Optional

from ai.quality_assessment.text_quality import (
    TextQualityAnalyzer,
    TextQualityMetrics,
    TextQualityProfile,
    ReadabilityAnalysis,
    GrammarAnalysis,
    ContentStructure
)


class TestTextQualityAnalyzer(TestCase):
    """Comprehensive test suite for TextQualityAnalyzer with professional text standards."""
    
    def setUp(self):
        """Set up test environment with various text samples and configurations."""
        self.analyzer = TextQualityAnalyzer()
        
        # High-quality professional text
        self.high_quality_text = """
        Artificial intelligence represents one of the most transformative technological advances 
        of our time. As we stand at the threshold of a new era, the integration of AI systems 
        into our daily lives continues to accelerate at an unprecedented pace. From healthcare 
        diagnostics to autonomous vehicles, from personalized education to climate modeling, 
        AI applications are revolutionizing industries and reshaping our understanding of what 
        machines can accomplish.
        
        The sophisticated algorithms powering these systems demonstrate remarkable capabilities 
        in pattern recognition, natural language processing, and decision-making. However, 
        this technological revolution also brings significant challenges that society must 
        address thoughtfully and proactively.
        
        Privacy concerns, ethical considerations, and the need for transparent, accountable 
        AI systems remain paramount. As we advance into this new frontier, collaboration 
        between technologists, policymakers, and citizens will be essential to ensure that 
        artificial intelligence serves humanity's best interests while maintaining our 
        fundamental values and freedoms.
        """
        
        # Low-quality text with errors
        self.low_quality_text = """
        ai is good technology that help people alot. it make life easy and do many thing 
        for us everyday. many company use ai now for there business and its very popular.
        
        people like ai because it fast and can solve problem quick. but some people worried 
        about job and privacy issue. ai is change world and we must be ready for future.
        
        in conclusion ai will continue grow and become more important in society so we 
        should learn about it and use it wisely for better world.
        """
        
        # SEO-optimized text
        self.seo_optimized_text = """
        Digital Marketing Strategies: Complete Guide for 2025 Success
        
        Digital marketing has become essential for businesses seeking growth in today's 
        competitive landscape. This comprehensive guide explores proven digital marketing 
        strategies that drive results and maximize ROI.
        
        Key Digital Marketing Channels:
        • Search Engine Optimization (SEO) - Improve organic visibility
        • Pay-Per-Click Advertising (PPC) - Generate immediate traffic
        • Social Media Marketing - Build brand awareness and engagement
        • Content Marketing - Establish thought leadership and trust
        • Email Marketing - Nurture leads and retain customers
        
        Implementing effective digital marketing requires understanding your target audience, 
        creating valuable content, and measuring performance through analytics. Successful 
        digital marketing campaigns combine multiple channels for maximum impact.
        
        Start your digital marketing journey today and transform your business growth.
        """
        
        # Creative/artistic text
        self.creative_text = """
        Whispers of Tomorrow
        
        In the twilight's gentle embrace, where shadows dance with fading light,
        Dreams weave through the fabric of time, painting hope across the night.
        
        Each star above tells stories old, of wishes cast and dreams unfurled,
        While moonbeams trace their silver paths across our sleeping world.
        
        Tomorrow holds a promise bright, wrapped in mystery and wonder,
        Where possibilities bloom like flowers after summer thunder.
        
        So let us sleep with hearts at peace, knowing morning's grace will come,
        Bringing chances fresh and new beneath the rising sun.
        """
        
        # Technical documentation text
        self.technical_text = """
        API Authentication Implementation Guide
        
        Authentication is a critical security mechanism that verifies user identity 
        before granting access to protected resources. This guide covers JWT-based 
        authentication implementation using industry best practices.
        
        Requirements:
        - Node.js 16+ or Python 3.8+
        - Database (PostgreSQL/MongoDB)
        - Redis for session management
        - SSL/TLS certificates
        
        Implementation Steps:
        1. Configure authentication middleware
        2. Implement token generation and validation
        3. Set up secure token storage
        4. Handle token refresh mechanisms
        5. Implement logout functionality
        
        Security Considerations:
        - Use strong, randomly generated secrets
        - Implement token expiration
        - Enable HTTPS for all endpoints
        - Validate input parameters
        - Log authentication events
        
        Testing should include unit tests, integration tests, and security assessments 
        to ensure robust authentication implementation.
        """
        
        # Platform-specific content samples
        self.platform_samples = {
            'twitter': "🚀 Excited to share our latest AI breakthrough! Revolutionary technology that's changing the game. #AI #Innovation #TechNews",
            'linkedin': "I'm pleased to announce our team's successful completion of the Q4 digital transformation project. This achievement represents months of dedicated collaboration and innovative problem-solving.",
            'instagram': "Beautiful sunset vibes ✨ Nothing beats nature's perfect timing and colors. Grateful for these peaceful moments. #sunset #nature #gratitude #peaceful",
            'youtube': "Welcome back to our channel! Today we're diving deep into advanced Python programming techniques that will elevate your coding skills to the next level.",
            'blog': "Understanding the fundamentals of machine learning requires a solid grasp of mathematical concepts, programming skills, and practical application experience."
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_text_analysis(self):
        """Test comprehensive text quality analysis with all metrics."""
        analysis_result = await self.analyzer.analyze_text_quality(
            self.high_quality_text,
            platform='blog',
            content_type='article'
        )
        
        # Validate result structure
        self.assertIsInstance(analysis_result, dict)
        self.assertIn('overall_score', analysis_result)
        self.assertIn('grammar_analysis', analysis_result)
        self.assertIn('readability_analysis', analysis_result)
        self.assertIn('seo_analysis', analysis_result)
        self.assertIn('sentiment_analysis', analysis_result)
        self.assertIn('style_analysis', analysis_result)
        self.assertIn('content_structure', analysis_result)
        self.assertIn('recommendations', analysis_result)
        
        # Validate score range
        self.assertGreaterEqual(analysis_result['overall_score'], 0.0)
        self.assertLessEqual(analysis_result['overall_score'], 100.0)
        
        # High-quality text should score well
        self.assertGreater(analysis_result['overall_score'], 70.0)
    
    @pytest.mark.asyncio
    async def test_grammar_analysis_comprehensive(self):
        """Test detailed grammar analysis functionality."""
        # Test high-quality text
        hq_grammar = await self.analyzer.analyze_grammar(self.high_quality_text)
        
        # Test low-quality text
        lq_grammar = await self.analyzer.analyze_grammar(self.low_quality_text)
        
        # Validate grammar analysis structure
        for result in [hq_grammar, lq_grammar]:
            self.assertIsInstance(result, GrammarAnalysis)
            self.assertIsNotNone(result.grammar_score)
            self.assertIsNotNone(result.error_count)
            self.assertIsNotNone(result.error_types)
            self.assertIsNotNone(result.suggestions)
            
            # Validate score range
            self.assertGreaterEqual(result.grammar_score, 0.0)
            self.assertLessEqual(result.grammar_score, 100.0)
            
            # Validate error analysis
            self.assertIsInstance(result.error_types, dict)
            self.assertIsInstance(result.suggestions, list)
        
        # High-quality text should have better grammar
        self.assertGreater(hq_grammar.grammar_score, lq_grammar.grammar_score)
        self.assertLess(hq_grammar.error_count, lq_grammar.error_count)
        
        # Validate error type categories
        expected_error_types = ['spelling', 'punctuation', 'subject_verb_agreement', 'tense_consistency']
        for error_type in expected_error_types:
            self.assertIn(error_type, lq_grammar.error_types)
    
    @pytest.mark.asyncio
    async def test_readability_analysis(self):
        """Test readability analysis with multiple metrics."""
        readability_result = await self.analyzer.analyze_readability(self.high_quality_text)
        
        # Validate readability analysis structure
        self.assertIsInstance(readability_result, ReadabilityAnalysis)
        self.assertIsNotNone(readability_result.flesch_kincaid_score)
        self.assertIsNotNone(readability_result.gunning_fog_index)
        self.assertIsNotNone(readability_result.smog_index)
        self.assertIsNotNone(readability_result.coleman_liau_index)
        self.assertIsNotNone(readability_result.reading_level)
        self.assertIsNotNone(readability_result.target_audience)
        
        # Validate readability scores
        self.assertGreaterEqual(readability_result.flesch_kincaid_score, 0.0)
        self.assertLessEqual(readability_result.flesch_kincaid_score, 100.0)
        
        self.assertGreaterEqual(readability_result.gunning_fog_index, 0.0)
        self.assertGreaterEqual(readability_result.smog_index, 0.0)
        self.assertGreaterEqual(readability_result.coleman_liau_index, 0.0)
        
        # Validate reading level classification
        expected_levels = ['elementary', 'middle_school', 'high_school', 'college', 'graduate']
        self.assertIn(readability_result.reading_level, expected_levels)
        
        # Validate target audience
        expected_audiences = ['general', 'professional', 'academic', 'technical', 'casual']
        self.assertIn(readability_result.target_audience, expected_audiences)
        
        # Test sentence complexity analysis
        self.assertIn('sentence_complexity', readability_result.detailed_metrics)
        complexity = readability_result.detailed_metrics['sentence_complexity']
        self.assertIn('average_sentence_length', complexity)
        self.assertIn('complex_sentences_percentage', complexity)
        self.assertIn('passive_voice_percentage', complexity)
    
    @pytest.mark.asyncio
    async def test_seo_analysis_comprehensive(self):
        """Test comprehensive SEO analysis functionality."""
        seo_result = await self.analyzer.analyze_seo_quality(
            self.seo_optimized_text,
            target_keywords=['digital marketing', 'SEO', 'strategies']
        )
        
        # Validate SEO analysis structure
        self.assertIsInstance(seo_result, dict)
        self.assertIsNotNone(seo_result.keyword_density)
        self.assertIsNotNone(seo_result.keyword_distribution)
        self.assertIsNotNone(seo_result.meta_optimization)
        self.assertIsNotNone(seo_result.content_structure_seo)
        self.assertIsNotNone(seo_result.internal_linking_potential)
        
        # Validate keyword analysis
        keyword_density = seo_result.keyword_density
        self.assertIsInstance(keyword_density, dict)
        
        for keyword in ['digital marketing', 'SEO', 'strategies']:
            if keyword in keyword_density:
                self.assertGreaterEqual(keyword_density[keyword], 0.0)
                self.assertLessEqual(keyword_density[keyword], 100.0)
        
        # Validate content structure for SEO
        structure_seo = seo_result.content_structure_seo
        self.assertIn('heading_optimization', structure_seo)
        self.assertIn('paragraph_length', structure_seo)
        self.assertIn('bullet_points_usage', structure_seo)
        self.assertIn('call_to_action_presence', structure_seo)
        
        # Validate meta optimization suggestions
        meta_opt = seo_result.meta_optimization
        self.assertIn('title_suggestions', meta_opt)
        self.assertIn('description_suggestions', meta_opt)
        self.assertIn('keyword_placement', meta_opt)
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_detailed(self):
        """Test detailed sentiment analysis functionality."""
        # Test different sentiment texts
        test_texts = {
            'positive': "I absolutely love this amazing product! It's fantastic and exceeded all my expectations.",
            'negative': "This is terrible and disappointing. I hate everything about this experience.",
            'neutral': "The product specifications include standard features and basic functionality.",
            'mixed': "While the design is beautiful and impressive, the price is unfortunately quite expensive."
        }
        
        for sentiment_type, text in test_texts.items():
            sentiment_result = await self.analyzer.analyze_sentiment(text)
            
            # Validate sentiment analysis structure
            self.assertIsInstance(sentiment_result, SentimentAnalysis)
            self.assertIsNotNone(sentiment_result.overall_sentiment)
            self.assertIsNotNone(sentiment_result.confidence_score)
            self.assertIsNotNone(sentiment_result.emotion_breakdown)
            self.assertIsNotNone(sentiment_result.tone_analysis)
            
            # Validate sentiment classification
            self.assertIn(sentiment_result.overall_sentiment, ['positive', 'negative', 'neutral', 'mixed'])
            
            # Validate confidence score
            self.assertGreaterEqual(sentiment_result.confidence_score, 0.0)
            self.assertLessEqual(sentiment_result.confidence_score, 1.0)
            
            # Validate emotion breakdown
            emotions = sentiment_result.emotion_breakdown
            expected_emotions = ['joy', 'anger', 'sadness', 'fear', 'surprise', 'disgust']
            for emotion in expected_emotions:
                if emotion in emotions:
                    self.assertGreaterEqual(emotions[emotion], 0.0)
                    self.assertLessEqual(emotions[emotion], 1.0)
            
            # Validate tone analysis
            tone = sentiment_result.tone_analysis
            self.assertIn('formality_level', tone)
            self.assertIn('emotional_intensity', tone)
            self.assertIn('subjectivity_score', tone)
    
    @pytest.mark.asyncio
    async def test_style_analysis_comprehensive(self):
        """Test comprehensive style analysis functionality."""
        # Test different content types
        content_samples = {
            'professional': self.high_quality_text,
            'casual': self.low_quality_text,
            'creative': self.creative_text,
            'technical': self.technical_text
        }
        
        for content_type, text in content_samples.items():
            style_result = await self.analyzer.analyze_writing_style(text)
            
            # Validate style analysis structure
            self.assertIsInstance(style_result, StyleAnalysis)
            self.assertIsNotNone(style_result.writing_style)
            self.assertIsNotNone(style_result.formality_level)
            self.assertIsNotNone(style_result.tone_consistency)
            self.assertIsNotNone(style_result.vocabulary_sophistication)
            self.assertIsNotNone(style_result.sentence_variety)
            
            # Validate style classification
            expected_styles = ['academic', 'professional', 'casual', 'creative', 'technical', 'journalistic']
            self.assertIn(style_result.writing_style, expected_styles)
            
            # Validate formality level
            expected_formality = ['very_formal', 'formal', 'neutral', 'informal', 'very_informal']
            self.assertIn(style_result.formality_level, expected_formality)
            
            # Validate tone consistency
            self.assertGreaterEqual(style_result.tone_consistency, 0.0)
            self.assertLessEqual(style_result.tone_consistency, 100.0)
            
            # Validate vocabulary sophistication
            vocab = style_result.vocabulary_sophistication
            self.assertIn('complexity_score', vocab)
            self.assertIn('unique_words_percentage', vocab)
            self.assertIn('advanced_vocabulary_usage', vocab)
            
            # Validate sentence variety
            sentence_variety = style_result.sentence_variety
            self.assertIn('length_variation', sentence_variety)
            self.assertIn('structure_variation', sentence_variety)
            self.assertIn('clause_complexity', sentence_variety)
    
    @pytest.mark.asyncio
    async def test_content_structure_analysis(self):
        """Test content structure and organization analysis."""
        structure_result = await self.analyzer.analyze_content_structure(self.technical_text)
        
        # Validate content structure analysis
        self.assertIsInstance(structure_result, ContentStructureAnalysis)
        self.assertIsNotNone(structure_result.organization_score)
        self.assertIsNotNone(structure_result.logical_flow)
        self.assertIsNotNone(structure_result.paragraph_structure)
        self.assertIsNotNone(structure_result.transition_quality)
        self.assertIsNotNone(structure_result.conclusion_strength)
        
        # Validate organization score
        self.assertGreaterEqual(structure_result.organization_score, 0.0)
        self.assertLessEqual(structure_result.organization_score, 100.0)
        
        # Validate logical flow analysis
        logical_flow = structure_result.logical_flow
        self.assertIn('coherence_score', logical_flow)
        self.assertIn('progression_quality', logical_flow)
        self.assertIn('topic_consistency', logical_flow)
        
        # Validate paragraph structure
        paragraph_structure = structure_result.paragraph_structure
        self.assertIn('average_paragraph_length', paragraph_structure)
        self.assertIn('paragraph_variety', paragraph_structure)
        self.assertIn('topic_sentence_presence', paragraph_structure)
        
        # Validate transition quality
        transitions = structure_result.transition_quality
        self.assertIn('transition_word_usage', transitions)
        self.assertIn('flow_smoothness', transitions)
        self.assertIn('connection_strength', transitions)
    
    @pytest.mark.asyncio
    async def test_platform_specific_optimization(self):
        """Test platform-specific content optimization analysis."""
        for platform, content in self.platform_samples.items():
            platform_result = await self.analyzer.analyze_platform_optimization(
                content,
                platform=platform
            )
            
            # Validate platform optimization structure
            self.assertIsInstance(platform_result, dict)
            self.assertIn('platform_score', platform_result)
            self.assertIn('character_count_analysis', platform_result)
            self.assertIn('engagement_prediction', platform_result)
            self.assertIn('platform_specific_recommendations', platform_result)
            
            # Validate platform score
            self.assertGreaterEqual(platform_result['platform_score'], 0.0)
            self.assertLessEqual(platform_result['platform_score'], 100.0)
            
            # Validate character count analysis
            char_analysis = platform_result['character_count_analysis']
            self.assertIn('current_length', char_analysis)
            self.assertIn('optimal_range', char_analysis)
            self.assertIn('length_compliance', char_analysis)
            
            # Platform-specific validations
            if platform == 'twitter':
                self.assertLessEqual(char_analysis['current_length'], 280)
                self.assertIn('hashtag_analysis', platform_result)
                
            elif platform == 'linkedin':
                self.assertIn('professional_tone_score', platform_result)
                self.assertIn('industry_relevance', platform_result)
                
            elif platform == 'instagram':
                self.assertIn('visual_content_suggestion', platform_result)
                self.assertIn('hashtag_recommendations', platform_result)
    
    @pytest.mark.asyncio
    async def test_content_quality_comparison(self):
        """Test quality comparison between different text samples."""
        texts_to_compare = [
            ('high_quality', self.high_quality_text),
            ('low_quality', self.low_quality_text),
            ('seo_optimized', self.seo_optimized_text),
            ('creative', self.creative_text)
        ]
        
        results = {}
        for text_type, text_content in texts_to_compare:
            result = await self.analyzer.analyze_text_quality(text_content)
            results[text_type] = result['overall_score']
        
        # High-quality text should score highest
        self.assertGreater(results['high_quality'], results['low_quality'])
        
        # SEO-optimized text should score well
        self.assertGreater(results['seo_optimized'], 70.0)
        
        # Creative text should have good scores too (different criteria)
        self.assertGreater(results['creative'], 60.0)
        
        # All scores should be in valid range
        for score in results.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)
    
    @pytest.mark.asyncio
    async def test_multilingual_text_analysis(self):
        """Test text analysis for different languages."""
        multilingual_samples = {
            'english': "This is a comprehensive analysis of text quality using advanced algorithms.",
            'french': "Ceci est une analyse complète de la qualité du texte utilisant des algorithmes avancés.",
            'german': "Dies ist eine umfassende Analyse der Textqualität mit fortschrittlichen Algorithmen.",
            'spanish': "Este es un análisis integral de la calidad del texto utilizando algoritmos avanzados."
        }
        
        for language, text in multilingual_samples.items():
            try:
                result = await self.analyzer.analyze_text_quality(
                    text,
                    language=language
                )
                
                # Validate basic structure for all languages
                self.assertIsInstance(result, dict)
                self.assertIn('overall_score', result)
                self.assertIn('language_detected', result)
                
                # Validate language detection
                if language == 'english':
                    self.assertEqual(result['language_detected'], 'en')
                elif language == 'french':
                    self.assertEqual(result['language_detected'], 'fr')
                elif language == 'german':
                    self.assertEqual(result['language_detected'], 'de')
                elif language == 'spanish':
                    self.assertEqual(result['language_detected'], 'es')
                
            except Exception as e:
                # Some languages might not be fully supported
                self.assertIn('language not supported', str(e).lower())
    
    def test_text_quality_metrics_data_model(self):
        """Test TextQualityMetrics data model validation."""
        metrics = TextQualityMetrics(
            overall_score=86.5,
            grammar_score=92.0,
            readability_score=88.0,
            seo_score=82.0,
            sentiment_score=85.0,
            style_score=89.0,
            structure_score=87.0,
            engagement_prediction=78.0
        )
        
        # Validate metrics structure
        self.assertEqual(metrics.overall_score, 86.5)
        self.assertEqual(metrics.grammar_score, 92.0)
        self.assertEqual(metrics.readability_score, 88.0)
        
        # Test metrics serialization
        metrics_dict = metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertIn('overall_score', metrics_dict)
        
        # Test quality level classification
        quality_level = metrics.get_quality_level()
        self.assertIn(quality_level, ['excellent', 'good', 'acceptable', 'poor'])
    
    def test_text_quality_profile_functionality(self):
        """Test TextQualityProfile class with comprehensive text characteristics."""
        profile = TextQualityProfile(
            content_type='blog_article',
            platform='wordpress',
            target_audience='professionals',
            quality_requirements={
                'minimum_readability': 75.0,
                'minimum_grammar': 85.0,
                'target_reading_level': 'high_school',
                'seo_optimization': True
            }
        )
        
        # Validate profile properties
        self.assertEqual(profile.content_type, 'blog_article')
        self.assertEqual(profile.platform, 'wordpress')
        self.assertEqual(profile.target_audience, 'professionals')
        
        # Test profile validation
        test_metrics = {
            'readability_score': 78.0,
            'grammar_score': 88.0,
            'reading_level': 'high_school',
            'seo_score': 82.0
        }
        
        validation_result = profile.validate_metrics(test_metrics)
        self.assertIsInstance(validation_result, dict)
        self.assertIn('compliant', validation_result)
        self.assertIn('violations', validation_result)
    
    @pytest.mark.asyncio
    async def test_real_time_text_analysis(self):
        """Test real-time text analysis capabilities."""
        # Simulate real-time analysis with partial text
        partial_texts = [
            "Artificial intelligence",
            "Artificial intelligence represents one of the most",
            "Artificial intelligence represents one of the most transformative technological advances",
            self.high_quality_text[:200],
            self.high_quality_text
        ]
        
        scores = []
        for partial_text in partial_texts:
            result = await self.analyzer.analyze_text_quality(
                partial_text,
                real_time_mode=True
            )
            scores.append(result['overall_score'])
        
        # Scores should generally improve as text gets more complete
        # (though not necessarily monotonically due to different criteria)
        self.assertIsInstance(scores, list)
        self.assertEqual(len(scores), len(partial_texts))
        
        # All scores should be valid
        for score in scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)


if __name__ == '__main__':
    # Run comprehensive text quality test suite
    pytest.main([str(Path(__file__)), '-v', '--tb=short'])
