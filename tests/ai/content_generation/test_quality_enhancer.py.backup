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

"""Quality Enhancer Tests

Comprehensive tests for the QualityEnhancer class that handles
content quality improvement and validation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.quality_enhancer import (
    QualityEnhancer
)
from ai.content_generation.content_models import ContentType, Platform


class TestQualityEnhancer:
    """Test suite for QualityEnhancer"""
    
    @pytest.fixture
    def enhancer(self):
        """Create a quality enhancer instance"""
        return QualityEnhancer()
    
    @pytest.fixture
    def sample_content(self):
        """Create sample content for quality analysis"""
        return """
        The artficial inteligence revoluton is here. It's transforming how we work, live, and interact with technology.
        
        AI systms can now understnd natural language, recognize images, and even create art. This technoogy has many aplications across diferent industries.
        
        However, their are still challenges. Privacy concerns, ethical considerations, and the need for human oversight are importent factors to consider.
        
        The future of AI is bright, but we must procede with caution and responsibility.
        """
    
    @pytest.fixture
    def high_quality_content(self):
        """Create high-quality content for comparison"""
        return """
        The artificial intelligence revolution is here. It's transforming how we work, live, and interact with technology.
        
        AI systems can now understand natural language, recognize images, and even create art. This technology has many applications across different industries.
        
        However, there are still challenges. Privacy concerns, ethical considerations, and the need for human oversight are important factors to consider.
        
        The future of AI is bright, but we must proceed with caution and responsibility.
        """
    
    def test_enhancer_initialization(self, enhancer):
        """Test quality enhancer initialization"""
        assert enhancer is not None
        assert hasattr(enhancer, 'grammar_checker')
        assert hasattr(enhancer, 'style_analyzer')
        assert hasattr(enhancer, 'readability_analyzer')
        assert hasattr(enhancer, 'fact_checker')
        assert hasattr(enhancer, 'tone_analyzer')
        assert hasattr(enhancer, 'quality_cache')
    
    @pytest.mark.asyncio
    async def test_comprehensive_quality_analysis(self, enhancer, sample_content):
        """Test comprehensive quality analysis"""
        with patch.object(enhancer, '_analyze_quality') as mock_analysis:
            mock_analysis.return_value = {
                "success": True,
                "overall_score": 72.5,
                "components": {
                    "grammar": 65,
                    "spelling": 70,
                    "readability": 78,
                    "style_consistency": 75,
                    "tone_consistency": 82,
                    "factual_accuracy": 90
                },
                "issues_found": {
                    "spelling_errors": 8,
                    "grammar_errors": 5,
                    "style_inconsistencies": 3,
                    "tone_variations": 2
                },
                "processing_time": 2.3
            }
            
            result = await enhancer.analyze_quality(
                content=sample_content,
                content_type=ContentType.BLOG_POST,
                target_audience="general",
                analysis_depth="comprehensive"
            )
            
            assert result["success"] is True
            assert result["overall_score"] == 72.5
            assert result["components"]["grammar"] == 65
            assert result["issues_found"]["spelling_errors"] == 8
    
    @pytest.mark.asyncio
    async def test_grammar_and_spelling_correction(self, enhancer, sample_content):
        """Test grammar and spelling correction"""
        with patch.object(enhancer, '_correct_grammar_spelling') as mock_correction:
            mock_correction.return_value = {
                "success": True,
                "corrected_content": sample_content.replace("artficial", "artificial").replace("inteligence", "intelligence"),
                "corrections": [
                    {"type": "spelling", "original": "artficial", "corrected": "artificial", "position": 4},
                    {"type": "spelling", "original": "inteligence", "corrected": "intelligence", "position": 15},
                    {"type": "grammar", "original": "their are", "corrected": "there are", "position": 245}
                ],
                "confidence_scores": [0.98, 0.97, 0.95],
                "improvement_score": 15.2
            }
            
            result = await enhancer.correct_grammar_spelling(
                content=sample_content,
                language="en",
                preserve_style=True,
                auto_apply=True
            )
            
            assert result["success"] is True
            assert len(result["corrections"]) == 3
            assert result["improvement_score"] == 15.2
            assert "artificial" in result["corrected_content"]
    
    @pytest.mark.asyncio
    async def test_readability_improvement(self, enhancer, sample_content):
        """Test readability improvement"""
        with patch.object(enhancer, '_improve_readability') as mock_readability:
            mock_readability.return_value = {
                "success": True,
                "improved_content": """
                The artificial intelligence revolution is here. It's changing how we work, live, and use technology.
                
                AI systems can understand language, recognize images, and create art. This technology works in many industries.
                
                But there are challenges. Privacy concerns and ethical issues need attention. Human oversight is also important.
                
                AI's future looks bright. However, we must move forward carefully and responsibly.
                """,
                "readability_scores": {
                    "before": {"flesch_kincaid": 12.5, "gunning_fog": 14.2},
                    "after": {"flesch_kincaid": 8.5, "gunning_fog": 9.1}
                },
                "improvements": {
                    "sentences_simplified": 4,
                    "complex_words_replaced": 7,
                    "average_sentence_length_reduced": 3.2
                }
            }
            
            result = await enhancer.improve_readability(
                content=sample_content,
                target_grade_level=8,
                preserve_meaning=True,
                simplify_vocabulary=True
            )
            
            assert result["success"] is True
            assert result["readability_scores"]["after"]["flesch_kincaid"] == 8.5
            assert result["improvements"]["sentences_simplified"] == 4
    
    @pytest.mark.asyncio
    async def test_style_consistency_analysis(self, enhancer, sample_content):
        """Test style consistency analysis"""
        with patch.object(enhancer, '_analyze_style_consistency') as mock_style:
            mock_style.return_value = {
                "success": True,
                "consistency_score": 76.5,
                "style_elements": {
                    "voice": {"consistency": 82, "detected_voice": "informative"},
                    "tense": {"consistency": 75, "primary_tense": "present"},
                    "person": {"consistency": 90, "primary_person": "third"},
                    "formality": {"consistency": 70, "level": "semi-formal"}
                },
                "inconsistencies": [
                    {"type": "tense", "location": "paragraph 3", "issue": "mixed past/present"},
                    {"type": "formality", "location": "paragraph 2", "issue": "informal language in formal context"}
                ],
                "recommendations": [
                    "Maintain consistent present tense throughout",
                    "Use consistent formality level"
                ]
            }
            
            result = await enhancer.analyze_style_consistency(
                content=sample_content,
                style_guide="professional",
                content_type=ContentType.BLOG_POST
            )
            
            assert result["success"] is True
            assert result["consistency_score"] == 76.5
            assert len(result["inconsistencies"]) == 2
            assert result["style_elements"]["voice"]["detected_voice"] == "informative"
    
    @pytest.mark.asyncio
    async def test_tone_adjustment(self, enhancer, sample_content):
        """Test tone adjustment functionality"""
        target_tone = "professional_friendly"
        
        with patch.object(enhancer, '_adjust_tone') as mock_tone:
            mock_tone.return_value = {
                "success": True,
                "adjusted_content": sample_content.replace("revolution is here", "revolution has arrived"),
                "tone_analysis": {
                    "original_tone": "neutral_informative",
                    "target_tone": "professional_friendly",
                    "adjustment_strength": 0.7,
                    "tone_consistency": 88.5
                },
                "modifications": [
                    {"type": "word_choice", "original": "revolution is here", "modified": "revolution has arrived"},
                    {"type": "sentence_structure", "count": 3}
                ]
            }
            
            result = await enhancer.adjust_tone(
                content=sample_content,
                target_tone=target_tone,
                intensity=0.7,
                preserve_meaning=True
            )
            
            assert result["success"] is True
            assert result["tone_analysis"]["target_tone"] == "professional_friendly"
            assert result["tone_analysis"]["tone_consistency"] == 88.5
    
    @pytest.mark.asyncio
    async def test_fact_checking(self, enhancer):
        """Test fact-checking functionality"""
        content_with_facts = """
        The speed of light is approximately 299,792,458 meters per second.
        The human brain contains about 86 billion neurons.
        Python was created by Guido van Rossum in 1991.
        The Earth's circumference is approximately 40,075 kilometers.
        """
        
        with patch.object(enhancer, '_check_facts') as mock_facts:
            mock_facts.return_value = {
                "success": True,
                "fact_checks": [
                    {
                        "claim": "speed of light is approximately 299,792,458 meters per second",
                        "accuracy": "correct",
                        "confidence": 0.99,
                        "source": "NIST"
                    },
                    {
                        "claim": "human brain contains about 86 billion neurons",
                        "accuracy": "correct",
                        "confidence": 0.95,
                        "source": "neuroscience research"
                    },
                    {
                        "claim": "Python was created by Guido van Rossum in 1991",
                        "accuracy": "correct",
                        "confidence": 0.98,
                        "source": "Python Software Foundation"
                    }
                ],
                "overall_accuracy": 98.5,
                "verified_claims": 3,
                "disputed_claims": 0
            }
            
            result = await enhancer.check_facts(
                content=content_with_facts,
                source_verification=True,
                confidence_threshold=0.8
            )
            
            assert result["success"] is True
            assert result["overall_accuracy"] == 98.5
            assert result["verified_claims"] == 3
            assert len(result["fact_checks"]) == 3
    
    @pytest.mark.asyncio
    async def test_plagiarism_detection(self, enhancer, sample_content):
        """Test plagiarism detection"""
        with patch.object(enhancer, '_detect_plagiarism') as mock_plagiarism:
            mock_plagiarism.return_value = {
                "success": True,
                "plagiarism_score": 5.2,  # Low plagiarism
                "similarity_matches": [
                    {
                        "source": "wikipedia.org",
                        "similarity": 15.5,
                        "matched_text": "artificial intelligence revolution",
                        "url": "https://en.wikipedia.org/wiki/AI"
                    }
                ],
                "originality_score": 94.8,
                "safe_to_publish": True,
                "recommendations": [
                    "Consider rephrasing common phrases",
                    "Add more original insights"
                ]
            }
            
            result = await enhancer.detect_plagiarism(
                content=sample_content,
                check_web=True,
                check_academic=True,
                similarity_threshold=20
            )
            
            assert result["success"] is True
            assert result["plagiarism_score"] == 5.2
            assert result["originality_score"] == 94.8
            assert result["safe_to_publish"] is True
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, enhancer, sample_content):
        """Test sentiment analysis"""
        with patch.object(enhancer, '_analyze_sentiment') as mock_sentiment:
            mock_sentiment.return_value = {
                "success": True,
                "overall_sentiment": {
                    "polarity": 0.15,  # Slightly positive
                    "subjectivity": 0.45,
                    "classification": "neutral_positive"
                },
                "sentence_sentiments": [
                    {"sentence": 1, "polarity": 0.2, "classification": "positive"},
                    {"sentence": 2, "polarity": 0.1, "classification": "neutral"},
                    {"sentence": 3, "polarity": -0.05, "classification": "neutral"},
                    {"sentence": 4, "polarity": 0.3, "classification": "positive"}
                ],
                "emotion_analysis": {
                    "joy": 0.15,
                    "optimism": 0.25,
                    "trust": 0.35,
                    "anticipation": 0.20,
                    "fear": 0.05
                }
            }
            
            result = await enhancer.analyze_sentiment(
                content=sample_content,
                include_emotions=True,
                granular_analysis=True
            )
            
            assert result["success"] is True
            assert result["overall_sentiment"]["classification"] == "neutral_positive"
            assert len(result["sentence_sentiments"]) == 4
            assert result["emotion_analysis"]["trust"] == 0.35
    
    @pytest.mark.asyncio
    async def test_content_enhancement_suggestions(self, enhancer, sample_content):
        """Test content enhancement suggestions"""
        with patch.object(enhancer, '_generate_suggestions') as mock_suggestions:
            mock_suggestions.return_value = {
                "success": True,
                "suggestions": [
                    {
                        "type": "structure",
                        "priority": "high",
                        "suggestion": "Add subheadings to improve readability",
                        "impact_score": 8.5
                    },
                    {
                        "type": "content",
                        "priority": "medium",
                        "suggestion": "Include specific examples of AI applications",
                        "impact_score": 7.2
                    },
                    {
                        "type": "style",
                        "priority": "low",
                        "suggestion": "Use more active voice constructions",
                        "impact_score": 5.8
                    }
                ],
                "enhancement_potential": 18.5,
                "estimated_improvement": "25% quality increase"
            }
            
            result = await enhancer.generate_enhancement_suggestions(
                content=sample_content,
                content_type=ContentType.BLOG_POST,
                target_audience="general",
                improvement_focus="readability"
            )
            
            assert result["success"] is True
            assert len(result["suggestions"]) == 3
            assert result["enhancement_potential"] == 18.5
            assert result["suggestions"][0]["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_automated_content_improvement(self, enhancer, sample_content):
        """Test automated content improvement"""
        with patch.object(enhancer, '_auto_improve_content') as mock_improve:
            mock_improve.return_value = {
                "success": True,
                "improved_content": sample_content.replace("artficial inteligence", "artificial intelligence"),
                "improvements_applied": [
                    {"type": "spelling", "count": 8},
                    {"type": "grammar", "count": 5},
                    {"type": "readability", "count": 3},
                    {"type": "style", "count": 2}
                ],
                "quality_improvement": {
                    "before_score": 72.5,
                    "after_score": 89.2,
                    "improvement": 16.7
                },
                "processing_time": 4.7
            }
            
            result = await enhancer.auto_improve_content(
                content=sample_content,
                improvement_level="aggressive",
                preserve_voice=True,
                target_quality_score=85
            )
            
            assert result["success"] is True
            assert result["quality_improvement"]["after_score"] == 89.2
            assert result["quality_improvement"]["improvement"] == 16.7
            assert len(result["improvements_applied"]) == 4
    
    @pytest.mark.asyncio
    async def test_brand_voice_consistency(self, enhancer, sample_content):
        """Test brand voice consistency checking"""
        brand_guidelines = {
            "voice": "professional yet approachable",
            "tone": "confident and helpful",
            "style": "clear and concise",
            "vocabulary": "technical but accessible",
            "personality": "expert and trustworthy"
        }
        
        with patch.object(enhancer, '_check_brand_voice') as mock_brand:
            mock_brand.return_value = {
                "success": True,
                "consistency_score": 84.3,
                "voice_alignment": {
                    "professional": 0.88,
                    "approachable": 0.79,
                    "confident": 0.85,
                    "helpful": 0.82
                },
                "deviations": [
                    {
                        "aspect": "tone",
                        "location": "paragraph 2",
                        "issue": "slightly too casual for brand guidelines",
                        "severity": "minor"
                    }
                ],
                "recommendations": [
                    "Maintain more formal tone in technical explanations",
                    "Use more industry-specific terminology"
                ]
            }
            
            result = await enhancer.check_brand_voice_consistency(
                content=sample_content,
                brand_guidelines=brand_guidelines,
                strictness_level="medium"
            )
            
            assert result["success"] is True
            assert result["consistency_score"] == 84.3
            assert len(result["deviations"]) == 1
            assert result["voice_alignment"]["professional"] == 0.88
    
    @pytest.mark.asyncio
    async def test_content_accessibility_check(self, enhancer, sample_content):
        """Test content accessibility checking"""
        with patch.object(enhancer, '_check_accessibility') as mock_accessibility:
            mock_accessibility.return_value = {
                "success": True,
                "accessibility_score": 78.5,
                "wcag_compliance": {
                    "level_a": True,
                    "level_aa": False,
                    "level_aaa": False
                },
                "issues": [
                    {
                        "type": "readability",
                        "description": "Some sentences are too complex",
                        "wcag_criterion": "3.1.5",
                        "severity": "medium"
                    },
                    {
                        "type": "structure",
                        "description": "Missing clear heading hierarchy",
                        "wcag_criterion": "1.3.1",
                        "severity": "low"
                    }
                ],
                "recommendations": [
                    "Simplify complex sentences",
                    "Add proper heading structure",
                    "Include alt text for any images"
                ]
            }
            
            result = await enhancer.check_accessibility(
                content=sample_content,
                wcag_level="AA",
                include_recommendations=True
            )
            
            assert result["success"] is True
            assert result["accessibility_score"] == 78.5
            assert result["wcag_compliance"]["level_a"] is True
            assert len(result["issues"]) == 2
    
    @pytest.mark.asyncio
    async def test_multilingual_quality_check(self, enhancer):
        """Test multilingual quality checking"""
        multilingual_content = {
            "en": "The artificial intelligence revolution is transforming our world.",
            "es": "La revolución de la inteligencia artificial está transformando nuestro mundo.",
            "fr": "La révolution de l'intelligence artificielle transforme notre monde.",
            "de": "Die Revolution der künstlichen Intelligenz verändert unsere Welt."
        }
        
        with patch.object(enhancer, '_check_multilingual_quality') as mock_multilingual:
            mock_multilingual.return_value = {
                "success": True,
                "language_scores": {
                    "en": {"grammar": 95, "style": 88, "readability": 82},
                    "es": {"grammar": 92, "style": 85, "readability": 80},
                    "fr": {"grammar": 90, "style": 87, "readability": 78},
                    "de": {"grammar": 88, "style": 84, "readability": 75}
                },
                "consistency_check": {
                    "meaning_preservation": 0.94,
                    "tone_consistency": 0.91,
                    "style_alignment": 0.89
                },
                "translation_quality": 91.5
            }
            
            result = await enhancer.check_multilingual_quality(
                content_versions=multilingual_content,
                source_language="en",
                check_consistency=True
            )
            
            assert result["success"] is True
            assert result["language_scores"]["en"]["grammar"] == 95
            assert result["consistency_check"]["meaning_preservation"] == 0.94
            assert result["translation_quality"] == 91.5
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, enhancer, sample_content):
        """Test performance monitoring for quality enhancement"""
        with patch.object(enhancer, '_analyze_quality') as mock_analysis:
            mock_analysis.return_value = {
                "success": True,
                "overall_score": 85.2,
                "processing_metrics": {
                    "analysis_time": 2.3,
                    "memory_usage": 128.5,
                    "cpu_utilization": 45.2,
                    "cache_hits": 15,
                    "cache_misses": 3
                }
            }
            
            result = await enhancer.analyze_quality(
                content=sample_content,
                track_performance=True,
                use_cache=True
            )
            
            assert result["success"] is True
            assert "processing_metrics" in result
            assert result["processing_metrics"]["analysis_time"] == 2.3
            
            # Test performance metrics collection
            metrics = await enhancer.get_performance_metrics()
            assert "average_processing_time" in metrics
            assert "cache_efficiency" in metrics


class TestQualityMetrics:
    """Test suite for QualityMetrics model"""
    
    def test_quality_metrics_creation(self):
        """Test quality metrics creation"""
        metrics = QualityMetrics(
            grammar_score=85.5,
            spelling_score=92.3,
            readability_score=78.9,
            style_consistency=88.1,
            tone_consistency=91.7,
            factual_accuracy=95.2
        )
        
        assert metrics.grammar_score == 85.5
        assert metrics.spelling_score == 92.3
        assert metrics.readability_score == 78.9
        assert metrics.style_consistency == 88.1
        assert metrics.tone_consistency == 91.7
        assert metrics.factual_accuracy == 95.2


class TestGrammarCheck:
    """Test suite for GrammarCheck model"""
    
    def test_grammar_check_creation(self):
        """Test grammar check result creation"""
        check = GrammarCheck(
            error_count=5,
            corrections=[
                {"type": "subject_verb", "original": "They was", "corrected": "They were"},
                {"type": "punctuation", "original": "Hello world", "corrected": "Hello, world"}
            ],
            confidence_score=0.95
        )
        
        assert check.error_count == 5
        assert len(check.corrections) == 2
        assert check.confidence_score == 0.95


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
