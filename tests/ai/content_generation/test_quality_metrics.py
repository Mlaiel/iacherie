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

"""Quality Metrics Tests

Comprehensive tests for quality metrics system that evaluates
content quality, readability, SEO, and overall content effectiveness.

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

from ai.content_generation.quality_metrics import (
    QualityMetrics, 
    ContentQualityAnalyzer
)
from ai.content_generation.content_models import ContentType, Platform


class TestQualityMetrics:
    """Test suite for QualityMetrics"""
    
    @pytest.fixture
    def quality_metrics(self):
        """Create a quality metrics instance"""
        return QualityMetrics()
    
    @pytest.fixture
    def sample_content(self):
        """Create sample content for quality analysis"""
        return {
            "title": "The Ultimate Guide to AI Content Creation: 10 Tools That Will Transform Your Workflow",
            "content": """# The Ultimate Guide to AI Content Creation: 10 Tools That Will Transform Your Workflow

Artificial intelligence has revolutionized the way we create, optimize, and distribute content. In today's fast-paced digital landscape, content creators who leverage AI tools gain a significant competitive advantage.

## Introduction

Content creation used to be a time-consuming process that required extensive manual effort. Writers would spend hours researching, drafting, editing, and optimizing their work. Today, AI tools can automate many of these tasks, allowing creators to focus on strategy and creativity.

This comprehensive guide explores the top 10 AI tools that are transforming content creation workflows. We'll examine their features, benefits, and practical applications to help you choose the right tools for your needs.

## 1. GPT-4 for Content Generation

OpenAI's GPT-4 represents a breakthrough in natural language processing. This powerful model can generate high-quality content across various formats, from blog posts to social media updates.

**Key Features:**
- Advanced language understanding and generation
- Context-aware responses
- Multi-format content creation
- Integration capabilities with existing workflows

**Best Use Cases:**
- Blog post drafting
- Social media content
- Email marketing campaigns
- Product descriptions

## 2. Jasper AI for Marketing Content

Jasper AI specializes in marketing-focused content creation. It's designed to understand brand voice and generate content that aligns with your marketing objectives.

**Key Features:**
- Brand voice training
- Template library for marketing content
- Collaboration tools for teams
- Performance tracking and optimization

## Conclusion

AI tools are not replacing human creativity—they're enhancing it. By incorporating these 10 AI tools into your content creation workflow, you can increase productivity, improve quality, and scale your content operations effectively.

The future of content creation lies in the synergy between human creativity and artificial intelligence. Start experimenting with these tools today to stay ahead of the competition.
""",
            "meta_description": "Discover the top 10 AI tools that will revolutionize your content creation workflow. Learn how to leverage artificial intelligence for better, faster content.",
            "tags": ["AI", "Content Creation", "Artificial Intelligence", "Productivity", "Marketing"],
            "target_keywords": ["AI content creation", "content creation tools", "artificial intelligence writing"],
            "author": "Fahed Mlaiel",
            "platform": Platform.LINKEDIN,
            "content_type": ContentType.ARTICLE,
            "target_audience": "content creators and marketers",
            "word_count": 1847
        }
    
    @pytest.fixture
    def low_quality_content(self):
        """Create low quality content for testing"""
        return {
            "title": "ai tools",
            "content": """ai is good. it helps with writing stuff. here are some tools:

chatgpt - writes things
jasper - also writes
copy.ai - writes too

these are good tools. you should use them. they make writing easier and faster.

ai will change everything. it is the future. content creation will be different. 

end.
""",
            "meta_description": "ai tools for writing",
            "tags": ["ai"],
            "target_keywords": ["ai"],
            "author": "Anonymous",
            "platform": Platform.TWITTER,
            "content_type": ContentType.POST,
            "word_count": 67
        }
    
    def test_quality_metrics_initialization(self, quality_metrics):
        """Test quality metrics initialization"""
        assert quality_metrics is not None
        assert hasattr(quality_metrics, 'quality_dimensions')
        assert hasattr(quality_metrics, 'grade_boundaries')
        assert hasattr(quality_metrics, 'readability_formulas')
        assert hasattr(quality_metrics, 'engagement_patterns')
        
        # Check default quality standards exist
        assert len(quality_metrics.quality_dimensions) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_content_quality(self, quality_metrics, sample_content):
        """Test comprehensive content quality analysis"""
        with patch.object(quality_metrics, '_analyze_quality') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "overall_quality_score": 92.5,
                "quality_breakdown": {
                    "content_structure": {
                        "score": 95.0,
                        "elements": {
                            "has_clear_title": True,
                            "has_introduction": True,
                            "has_conclusion": True,
                            "proper_headings": True,
                            "logical_flow": True,
                            "paragraph_length": "optimal"
                        },
                        "issues": [],
                        "suggestions": ["Consider adding more subheadings for better navigation"]
                    },
                    "content_depth": {
                        "score": 89.5,
                        "elements": {
                            "word_count": 1847,
                            "topic_coverage": "comprehensive",
                            "detail_level": "appropriate",
                            "examples_provided": True,
                            "actionable_insights": True
                        },
                        "issues": ["Could benefit from more specific examples"],
                        "suggestions": ["Add case studies or real-world examples"]
                    },
                    "writing_quality": {
                        "score": 94.0,
                        "elements": {
                            "grammar_score": 98.5,
                            "spelling_score": 100.0,
                            "tone_consistency": True,
                            "voice_clarity": True,
                            "sentence_variety": True
                        },
                        "issues": [],
                        "suggestions": ["Excellent writing quality maintained throughout"]
                    },
                    "engagement_factor": {
                        "score": 87.5,
                        "elements": {
                            "hook_effectiveness": 85.0,
                            "call_to_action": "present",
                            "emotional_appeal": "moderate",
                            "interactive_elements": False,
                            "storytelling": "minimal"
                        },
                        "issues": ["Missing interactive elements"],
                        "suggestions": ["Add questions or polls to increase engagement"]
                    },
                    "originality": {
                        "score": 96.0,
                        "elements": {
                            "plagiarism_score": 0.0,
                            "unique_perspective": True,
                            "fresh_insights": True,
                            "creativity_level": "high"
                        },
                        "issues": [],
                        "suggestions": ["Maintain this high level of originality"]
                    }
                },
                "quality_grade": "A-",
                "improvement_priority": [
                    "Add more interactive elements",
                    "Include specific examples and case studies",
                    "Enhance emotional storytelling"
                ]
            }
            
            result = await quality_metrics.analyze_content_quality(
                content=sample_content,
                detailed_analysis=True,
                include_suggestions=True
            )
            
            assert result["success"] is True
            assert result["overall_quality_score"] > 90.0
            assert result["quality_grade"] == "A-"
            assert len(result["improvement_priority"]) >= 3
            assert result["quality_breakdown"]["writing_quality"]["score"] > 90.0
    
    @pytest.mark.asyncio
    async def test_readability_analysis(self, quality_metrics, sample_content):
        """Test readability analysis"""
        with patch.object(quality_metrics, '_analyze_readability') as mock_readability:
            mock_readability.return_value = {
                "success": True,
                "readability_scores": {
                    "flesch_reading_ease": 68.5,
                    "flesch_kincaid_grade": 8.2,
                    "gunning_fog_index": 9.1,
                    "smog_index": 7.8,
                    "automated_readability_index": 8.5,
                    "coleman_liau_index": 9.2
                },
                "readability_level": "Fairly Easy",
                "target_audience_match": True,
                "reading_time": {
                    "average_reader": "7.4 minutes",
                    "slow_reader": "11.1 minutes",
                    "fast_reader": "4.9 minutes"
                },
                "sentence_analysis": {
                    "average_sentence_length": 16.8,
                    "sentence_variety": "good",
                    "complex_sentences": 0.25,
                    "compound_sentences": 0.35,
                    "simple_sentences": 0.40
                },
                "vocabulary_analysis": {
                    "average_syllables_per_word": 1.7,
                    "difficult_words_percentage": 12.5,
                    "technical_terms": 8,
                    "jargon_level": "moderate"
                },
                "recommendations": [
                    "Excellent readability for target audience",
                    "Good sentence variety maintains engagement",
                    "Technical terms are appropriate for content type",
                    "Consider simplifying a few complex sentences"
                ]
            }
            
            result = await quality_metrics.analyze_readability(
                content=sample_content["content"],
                target_audience=sample_content["target_audience"]
            )
            
            assert result["success"] is True
            assert result["readability_scores"]["flesch_reading_ease"] > 60.0
            assert result["target_audience_match"] is True
            assert result["readability_level"] == "Fairly Easy"
            assert len(result["recommendations"]) >= 4
    
    @pytest.mark.asyncio
    async def test_seo_quality_analysis(self, quality_metrics, sample_content):
        """Test SEO quality analysis"""
        with patch.object(quality_metrics, '_analyze_seo') as mock_seo:
            mock_seo.return_value = {
                "success": True,
                "seo_score": 88.5,
                "seo_analysis": {
                    "title_optimization": {
                        "score": 92.0,
                        "title_length": 89,
                        "keyword_in_title": True,
                        "title_readability": "excellent",
                        "emotional_words": 2,
                        "issues": [],
                        "suggestions": ["Title length is optimal for search results"]
                    },
                    "meta_description": {
                        "score": 85.0,
                        "length": 147,
                        "keyword_presence": True,
                        "call_to_action": True,
                        "compelling_factor": 8.5,
                        "issues": ["Could be more specific about benefits"],
                        "suggestions": ["Add specific numbers or outcomes"]
                    },
                    "keyword_optimization": {
                        "score": 89.0,
                        "primary_keyword_density": 1.8,
                        "secondary_keyword_usage": "good",
                        "keyword_distribution": "natural",
                        "semantic_keywords": 12,
                        "keyword_stuffing_risk": "none",
                        "issues": [],
                        "suggestions": ["Keyword usage is well-balanced"]
                    },
                    "content_structure": {
                        "score": 91.5,
                        "heading_hierarchy": "proper",
                        "h1_optimization": True,
                        "subheading_keywords": True,
                        "bullet_points": True,
                        "internal_links": 0,
                        "issues": ["Missing internal links"],
                        "suggestions": ["Add 2-3 relevant internal links"]
                    },
                    "technical_seo": {
                        "score": 87.0,
                        "word_count": "optimal",
                        "image_alt_text": "not_applicable",
                        "url_structure": "good",
                        "schema_markup": False,
                        "mobile_optimization": True,
                        "issues": ["Missing schema markup"],
                        "suggestions": ["Add article schema markup"]
                    }
                },
                "seo_grade": "B+",
                "improvement_actions": [
                    "Add 2-3 relevant internal links",
                    "Implement article schema markup",
                    "Make meta description more specific",
                    "Consider adding FAQ section for featured snippets"
                ]
            }
            
            result = await quality_metrics.analyze_seo_quality(
                content=sample_content,
                target_keywords=sample_content["target_keywords"]
            )
            
            assert result["success"] is True
            assert result["seo_score"] > 85.0
            assert result["seo_grade"] == "B+"
            assert result["seo_analysis"]["keyword_optimization"]["score"] > 85.0
            assert len(result["improvement_actions"]) >= 4
    
    @pytest.mark.asyncio
    async def test_engagement_prediction(self, quality_metrics, sample_content):
        """Test engagement prediction based on content quality"""
        with patch.object(quality_metrics, '_predict_engagement') as mock_engagement:
            mock_engagement.return_value = {
                "success": True,
                "engagement_prediction": {
                    "overall_engagement_score": 8.7,
                    "engagement_breakdown": {
                        "likes_potential": 8.9,
                        "shares_potential": 8.2,
                        "comments_potential": 7.8,
                        "saves_potential": 9.1,
                        "click_through_potential": 8.5
                    },
                    "predicted_metrics": {
                        "estimated_reach": 15000,
                        "estimated_engagement_rate": 6.8,
                        "estimated_clicks": 1020,
                        "estimated_shares": 145,
                        "confidence_interval": [0.75, 0.92]
                    },
                    "engagement_factors": {
                        "title_appeal": 9.2,
                        "content_value": 8.8,
                        "readability": 8.5,
                        "visual_appeal": 7.0,
                        "timing_optimization": 8.0,
                        "trending_topics": 6.5
                    },
                    "optimization_suggestions": [
                        "Add compelling visuals to increase visual appeal",
                        "Include trending hashtags for better discoverability",
                        "Consider posting during peak engagement hours",
                        "Add interactive elements to boost comment potential"
                    ]
                }
            }
            
            result = await quality_metrics.predict_engagement(
                content=sample_content,
                platform=sample_content["platform"],
                posting_time="optimal"
            )
            
            assert result["success"] is True
            assert result["engagement_prediction"]["overall_engagement_score"] > 8.5
            assert result["engagement_prediction"]["predicted_metrics"]["estimated_engagement_rate"] > 6.0
            assert len(result["engagement_prediction"]["optimization_suggestions"]) >= 4
    
    @pytest.mark.asyncio
    async def test_low_quality_content_analysis(self, quality_metrics, low_quality_content):
        """Test analysis of low quality content"""
        with patch.object(quality_metrics, '_analyze_quality') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "overall_quality_score": 23.5,
                "quality_breakdown": {
                    "content_structure": {
                        "score": 15.0,
                        "elements": {
                            "has_clear_title": False,
                            "has_introduction": False,
                            "has_conclusion": False,
                            "proper_headings": False,
                            "logical_flow": False,
                            "paragraph_length": "too_short"
                        },
                        "issues": [
                            "Title lacks descriptive power",
                            "No clear introduction or conclusion",
                            "Missing proper structure",
                            "Paragraphs too short and choppy"
                        ],
                        "suggestions": [
                            "Create a compelling, descriptive title",
                            "Add proper introduction and conclusion",
                            "Use headings to organize content",
                            "Expand paragraphs with more detail"
                        ]
                    },
                    "content_depth": {
                        "score": 20.0,
                        "elements": {
                            "word_count": 67,
                            "topic_coverage": "superficial",
                            "detail_level": "insufficient",
                            "examples_provided": False,
                            "actionable_insights": False
                        },
                        "issues": [
                            "Content is too short and lacks depth",
                            "No examples or detailed explanations",
                            "Missing actionable insights"
                        ],
                        "suggestions": [
                            "Expand content to at least 300 words",
                            "Add specific examples and use cases",
                            "Provide actionable tips and strategies"
                        ]
                    },
                    "writing_quality": {
                        "score": 35.0,
                        "elements": {
                            "grammar_score": 65.0,
                            "spelling_score": 90.0,
                            "tone_consistency": False,
                            "voice_clarity": False,
                            "sentence_variety": False
                        },
                        "issues": [
                            "Inconsistent tone and voice",
                            "Lack of sentence variety",
                            "Too casual for professional content"
                        ],
                        "suggestions": [
                            "Establish consistent professional tone",
                            "Vary sentence structure and length",
                            "Improve grammar and flow"
                        ]
                    }
                },
                "quality_grade": "F",
                "improvement_priority": [
                    "Completely rewrite with proper structure",
                    "Expand content depth significantly",
                    "Improve writing quality and tone",
                    "Add valuable insights and examples"
                ]
            }
            
            result = await quality_metrics.analyze_content_quality(
                content=low_quality_content,
                detailed_analysis=True,
                include_suggestions=True
            )
            
            assert result["success"] is True
            assert result["overall_quality_score"] < 30.0
            assert result["quality_grade"] == "F"
            assert len(result["improvement_priority"]) >= 4
            assert "superficial" in str(result["quality_breakdown"])
    
    @pytest.mark.asyncio
    async def test_batch_quality_analysis(self, quality_metrics):
        """Test batch analysis of multiple content pieces"""
        content_batch = [
            {"id": "content_1", "title": "High Quality Article", "content": "Well-written comprehensive content..."},
            {"id": "content_2", "title": "Medium Quality Post", "content": "Decent content with some issues..."},
            {"id": "content_3", "title": "low quality", "content": "short bad content"}
        ]
        
        with patch.object(quality_metrics, '_analyze_batch') as mock_batch:
            mock_batch.return_value = {
                "success": True,
                "batch_analysis": {
                    "content_1": {
                        "quality_score": 91.5,
                        "grade": "A-",
                        "issues": ["Minor formatting improvements needed"]
                    },
                    "content_2": {
                        "quality_score": 72.8,
                        "grade": "C+",
                        "issues": ["Needs better structure", "Add more examples"]
                    },
                    "content_3": {
                        "quality_score": 28.2,
                        "grade": "F",
                        "issues": ["Complete rewrite required", "Insufficient content"]
                    }
                },
                "batch_summary": {
                    "total_content": 3,
                    "average_quality_score": 64.2,
                    "grade_distribution": {"A": 1, "C": 1, "F": 1},
                    "needs_improvement": 2,
                    "high_quality": 1
                },
                "recommendations": [
                    "Focus on improving low-quality content first",
                    "Develop content guidelines for consistency",
                    "Implement quality review process"
                ]
            }
            
            result = await quality_metrics.analyze_content_batch(
                content_list=content_batch,
                priority_ranking=True
            )
            
            assert result["success"] is True
            assert result["batch_summary"]["total_content"] == 3
            assert result["batch_summary"]["needs_improvement"] == 2
            assert len(result["recommendations"]) >= 3
    
    @pytest.mark.asyncio
    async def test_quality_improvement_suggestions(self, quality_metrics, sample_content):
        """Test specific improvement suggestions generation"""
        with patch.object(quality_metrics, '_generate_improvements') as mock_improvements:
            mock_improvements.return_value = {
                "success": True,
                "improvement_plan": {
                    "immediate_fixes": [
                        {
                            "issue": "Missing internal links",
                            "solution": "Add 2-3 relevant internal links to related articles",
                            "impact": "SEO improvement",
                            "effort": "low",
                            "priority": "high"
                        },
                        {
                            "issue": "No interactive elements",
                            "solution": "Add questions or polls to increase engagement",
                            "impact": "Engagement boost",
                            "effort": "medium",
                            "priority": "medium"
                        }
                    ],
                    "content_enhancements": [
                        {
                            "area": "Visual appeal",
                            "suggestion": "Add infographics or charts to illustrate key points",
                            "expected_impact": "20% engagement increase",
                            "implementation_time": "2 hours"
                        },
                        {
                            "area": "Social proof",
                            "suggestion": "Include customer testimonials or case studies",
                            "expected_impact": "15% conversion improvement",
                            "implementation_time": "1 hour"
                        }
                    ],
                    "strategic_improvements": [
                        {
                            "goal": "Increase shareability",
                            "actions": [
                                "Add quotable snippets",
                                "Create social media-friendly headlines",
                                "Include statistics and data points"
                            ],
                            "timeline": "1 week",
                            "resources_needed": ["designer", "data_researcher"]
                        }
                    ]
                },
                "roi_estimation": {
                    "effort_hours": 5.5,
                    "expected_improvement": "35% quality score increase",
                    "engagement_lift": "25%",
                    "seo_improvement": "15%"
                }
            }
            
            result = await quality_metrics.generate_improvement_suggestions(
                content=sample_content,
                current_quality_score=88.5,
                target_score=95.0
            )
            
            assert result["success"] is True
            assert len(result["improvement_plan"]["immediate_fixes"]) >= 2
            assert result["roi_estimation"]["effort_hours"] < 10
            assert "35%" in result["roi_estimation"]["expected_improvement"]


class TestContentQualityAnalyzer:
    """Test suite for ContentQualityAnalyzer"""
    
    @pytest.fixture
    def content_analyzer(self):
        """Create a content quality analyzer instance"""
        return ContentQualityAnalyzer()
    
    def test_content_analyzer_initialization(self, content_analyzer):
        """Test content analyzer initialization"""
        assert content_analyzer is not None
        assert hasattr(content_analyzer, 'quality_criteria')
        assert hasattr(content_analyzer, 'scoring_algorithm')
        assert hasattr(content_analyzer, 'improvement_engine')
    
    @pytest.mark.asyncio
    async def test_structural_analysis(self, content_analyzer):
        """Test content structural analysis"""
        content = {
            "title": "Complete Guide to AI Content Creation",
            "content": "# Introduction\n\nContent with proper structure...\n\n## Section 1\n\nDetailed content...\n\n## Conclusion\n\nSummary and next steps.",
            "word_count": 500
        }
        
        result = await content_analyzer.analyze_structure(content)
        
        assert "has_introduction" in result
        assert "proper_headings" in result
        assert "conclusion_present" in result


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
