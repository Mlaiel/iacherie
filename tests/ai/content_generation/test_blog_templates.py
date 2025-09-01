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
Blog Templates Tests

Comprehensive tests for blog template system that handles
article structure, SEO optimization, and content formatting.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

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

from ai.content_generation.blog_templates import BlogTemplates, ArticleTemplate
from ai.content_generation.content_models import ContentType


class TestBlogTemplates:
    """Test suite for BlogTemplates"""
    
    @pytest.fixture
    def blog_templates(self):
        """
Create a blog templates instance"""
        return BlogTemplates()
    
    @pytest.fixture
    def article_data(self):
        """
Create sample article data"""
        return {
            "title": "The Complete Guide to AI in Content Creation",
            "subtitle": "How Artificial Intelligence is Revolutionizing Digital Content",
            "author": "Fahed Mlaiel",
            "author_bio": "AI Expert and Content Strategist",
            "date": "2025-01-31",
            "category": "Technology",
            "tags": ["AI", "Content Creation", "Digital Marketing", "Automation"],
            "featured_image": "https://example.com/ai-content-guide.jpg",
            "reading_time": 8,
            "meta_description": "Discover how AI is transforming content creation with practical tips, tools, and strategies for modern marketers.",
            "target_keywords": ["AI content creation", "artificial intelligence marketing", "automated content"],
            "word_count_target": 2500,
            "tone": "professional",
            "audience": "marketers"
        }
    
    @pytest.fixture
    def tutorial_data(self):
        """Create sample tutorial data"""
        return {
            "title": "How to Build an AI-Powered Content Pipeline",
            "difficulty": "Intermediate",
            "time_required": "45 minutes",
            "prerequisites": ["Basic understanding of AI", "Content marketing experience"],
            "tools_needed": ["Python", "OpenAI API", "Content management system"],
            "steps": [
                "Set up your development environment",
                "Configure AI model integration",
                "Design content templates",
                "Implement automation workflows",
                "Test and optimize the pipeline"
            ],
            "expected_outcome": "A fully functional AI content generation system"
        }
    
    def test_blog_templates_initialization(self, blog_templates):
        """Test blog templates initialization"""
        assert blog_templates is not None
        assert hasattr(blog_templates, 'tutorial_templates')
        assert hasattr(blog_templates, 'list_templates')
        assert hasattr(blog_templates, 'news_templates')
        assert hasattr(blog_templates, 'seo_structures')
        
        # Check default templates exist
        assert len(blog_templates.tutorial_templates) > 0
    
    @pytest.mark.asyncio
    async def test_generate_article_structure(self, blog_templates, article_data):
        """
Test article structure generation"""
        with patch.object(blog_templates, '_generate_structure') as mock_structure:
            mock_structure.return_value = {
                "success": True,
                "structure": {
                    "introduction": {
                        "hook": "In 2025, 73% of marketers are using AI for content creation",
                        "problem_statement": "Traditional content creation is becoming too slow and expensive",
                        "thesis": "AI-powered content creation is the future of digital marketing",
                        "preview": "This guide covers tools, strategies, and implementation"
                    },
                    "main_sections": [
                        {
                            "title": "Understanding AI Content Creation",
                            "subsections": [
                                "What is AI Content Creation?",
                                "Types of AI Content Tools",
                                "Benefits and Limitations"
                            ],
                            "word_count": 600
                        },
                        {
                            "title": "Choosing the Right AI Tools",
                            "subsections": [
                                "Text Generation Tools",
                                "Image Creation Platforms",
                                "Video Production AI"
                            ],
                            "word_count": 700
                        },
                        {
                            "title": "Implementation Strategies",
                            "subsections": [
                                "Workflow Integration",
                                "Quality Control",
                                "Team Training"
                            ],
                            "word_count": 800
                        },
                        {
                            "title": "Measuring Success",
                            "subsections": [
                                "Key Performance Indicators",
                                "ROI Calculation",
                                "Optimization Techniques"
                            ],
                            "word_count": 400
                        }
                    ],
                    "conclusion": {
                        "summary": "Key takeaways and action items",
                        "call_to_action": "Start implementing AI in your content strategy today",
                        "word_count": 200
                    }
                },
                "total_sections": 4,
                "estimated_word_count": 2700,
                "reading_time": 11,
                "seo_score": 92.5
            }
            
            result = await blog_templates.generate_article_structure(
                title=article_data["title"],
                target_keywords=article_data["target_keywords"],
                word_count=article_data["word_count_target"],
                audience=article_data["audience"]
            )
            
            assert result["success"] is True
            assert result["total_sections"] == 4
            assert result["estimated_word_count"] >= 2500
            assert result["seo_score"] > 90.0
    
    @pytest.mark.asyncio
    async def test_tutorial_template_generation(self, blog_templates, tutorial_data):
        """Test tutorial template generation"""
        with patch.object(blog_templates, '_generate_tutorial') as mock_tutorial:
            mock_tutorial.return_value = {
                "success": True,
                "tutorial_content": {
                    "header": {
                        "title": "How to Build an AI-Powered Content Pipeline",
                        "difficulty_badge": "⚡ Intermediate",
                        "time_estimate": "⏱️ 45 minutes",
                        "requirements": "✅ Prerequisites and tools needed"
                    },
                    "introduction": """In this comprehensive tutorial, you'll learn how to build a complete AI-powered content pipeline that can automate your content creation process. By the end, you'll have a functional system that generates, optimizes, and publishes content automatically.

🎯 **What You'll Achieve:**
- Automated content generation
- SEO-optimized articles
- Multi-platform publishing
- Performance tracking

📋 **Prerequisites:**
• Basic understanding of AI concepts
• Content marketing experience
• Python programming knowledge (beginner level)

🛠️ **Tools We'll Use:**
• Python and required libraries
• OpenAI API for content generation
• Content management system integration
""",
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Set up your development environment",
                            "content": "Install Python, create virtual environment, install dependencies",
                            "code_example": "pip install openai requests beautifulsoup4",
                            "duration": "10 minutes",
                            "tips": ["Use virtual environments", "Keep dependencies updated"]
                        },
                        {
                            "step_number": 2,
                            "title": "Configure AI model integration",
                            "content": "Set up OpenAI API, configure models, test connection",
                            "code_example": "import openai\nopenai.api_key = 'your-api-key'",
                            "duration": "15 minutes",
                            "tips": ["Secure your API keys", "Test with small requests first"]
                        },
                        {
                            "step_number": 3,
                            "title": "Design content templates",
                            "content": "Create reusable templates for different content types",
                            "duration": "10 minutes",
                            "tips": ["Make templates flexible", "Include SEO elements"]
                        },
                        {
                            "step_number": 4,
                            "title": "Implement automation workflows",
                            "content": "Connect all components into automated pipeline",
                            "duration": "15 minutes",
                            "tips": ["Include error handling", "Add logging for debugging"]
                        },
                        {
                            "step_number": 5,
                            "title": "Test and optimize the pipeline",
                            "content": "Run tests, monitor performance, make improvements",
                            "duration": "10 minutes",
                            "tips": ["Start with small batches", "Monitor quality metrics"]
                        }
                    ],
                    "conclusion": {
                        "summary": "You now have a complete AI content pipeline",
                        "next_steps": ["Scale your content production", "Add more platforms", "Optimize for performance"],
                        "troubleshooting": ["Common issues and solutions", "Performance optimization tips"]
                    }
                },
                "template_type": "step_by_step_tutorial",
                "estimated_completion": 45,
                "difficulty_score": 6.5,
                "engagement_score": 8.9
            }
            
            result = await blog_templates.generate_tutorial(
                tutorial_data=tutorial_data,
                include_code_examples=True,
                add_troubleshooting=True
            )
            
            assert result["success"] is True
            assert len(result["tutorial_content"]["steps"]) == 5
            assert result["difficulty_score"] > 6.0
            assert result["engagement_score"] > 8.0
    
    @pytest.mark.asyncio
    async def test_listicle_template_generation(self, blog_templates, article_data):
        """Test listicle template generation"""
        listicle_data = {
            "title": "10 AI Tools Every Content Creator Should Know",
            "list_items": [
                "ChatGPT for text generation",
                "DALL-E for image creation", 
                "Jasper for marketing copy",
                "Copy.ai for social media",
                "Grammarly for editing",
                "Canva AI for design",
                "Loom for video",
                "Notion AI for organization",
                "Zapier for automation",
                "Analytics tools for tracking"
            ]
        }
        
        with patch.object(blog_templates, '_generate_listicle') as mock_listicle:
            mock_listicle.return_value = {
                "success": True,
                "listicle_content": {
                    "introduction": "Content creation has never been easier thanks to AI. Here are 10 essential tools that will transform your workflow.",
                    "items": [
                        {
                            "number": 1,
                            "title": "ChatGPT - The Ultimate Writing Assistant",
                            "description": "Generate articles, headlines, and creative content with OpenAI's powerful language model.",
                            "pros": ["Versatile", "Fast generation", "Multiple languages"],
                            "cons": ["Requires fact-checking", "Can be repetitive"],
                            "rating": 9.5,
                            "price": "Free tier available"
                        },
                        {
                            "number": 2,
                            "title": "DALL-E - AI Image Generation",
                            "description": "Create stunning visuals from text descriptions in seconds.",
                            "pros": ["High quality images", "Creative flexibility", "Commercial use"],
                            "cons": ["Credit-based pricing", "Learning curve"],
                            "rating": 9.0,
                            "price": "Pay per image"
                        }
                        # ... more items
                    ],
                    "conclusion": "These AI tools represent the future of content creation. Start with one or two that match your immediate needs.",
                    "call_to_action": "Which tool will you try first? Let us know in the comments!"
                },
                "template_type": "numbered_listicle",
                "list_count": 10,
                "engagement_potential": 9.2,
                "shareability_score": 8.8
            }
            
            result = await blog_templates.generate_listicle(
                title=listicle_data["title"],
                items=listicle_data["list_items"],
                include_ratings=True,
                add_pros_cons=True
            )
            
            assert result["success"] is True
            assert result["list_count"] == 10
            assert result["engagement_potential"] > 9.0
            assert len(result["listicle_content"]["items"]) >= 2
    
    @pytest.mark.asyncio
    async def test_news_article_template(self, blog_templates):
        """Test news article template generation"""
        news_data = {
            "headline": "OpenAI Releases Revolutionary GPT-5 with Advanced Reasoning",
            "lead": "New model shows 40% improvement in complex problem-solving tasks",
            "who": "OpenAI",
            "what": "Released GPT-5 AI model",
            "when": "January 31, 2025",
            "where": "San Francisco, CA",
            "why": "To advance AI capabilities for complex reasoning",
            "how": "Through improved training methods and architecture",
            "quotes": [
                {
                    "speaker": "Sam Altman, CEO OpenAI",
                    "quote": "GPT-5 represents a quantum leap in AI reasoning capabilities"
                },
                {
                    "speaker": "Dr. Sarah Chen, AI Researcher",
                    "quote": "This could revolutionize how we approach complex problem-solving"
                }
            ],
            "background_info": "Previous GPT models have shown steady improvement in language tasks",
            "implications": "May accelerate AI adoption across industries"
        }
        
        with patch.object(blog_templates, '_generate_news_article') as mock_news:
            mock_news.return_value = {
                "success": True,
                "article_content": {
                    "headline": "OpenAI Releases Revolutionary GPT-5 with Advanced Reasoning",
                    "byline": "By Fahed Mlaiel | January 31, 2025",
                    "lead_paragraph": """OpenAI announced today the release of GPT-5, its most advanced artificial intelligence model to date, featuring breakthrough capabilities in complex reasoning and problem-solving. The new model demonstrates a 40% improvement over its predecessor in handling multi-step logical challenges.
""",
                    "body_paragraphs": [
                        "The San Francisco-based company unveiled GPT-5 during a live demonstration showcasing the model's ability to solve intricate mathematical problems, analyze complex business scenarios, and provide nuanced reasoning across multiple domains.",
                        '"GPT-5 represents a quantum leap in AI reasoning capabilities," said Sam Altman, CEO of OpenAI, during the announcement. "We\'re moving closer to artificial general intelligence with each iteration."',
                        "The model's enhanced reasoning stems from improved training methodologies and architectural innovations that allow for better understanding of context and logical relationships.",
                        "Industry experts predict the release could accelerate AI adoption across sectors including healthcare, finance, and scientific research."
                    ],
                    "conclusion": "GPT-5 is expected to be available to enterprise customers next month, with broader public access planned for later this year."
                },
                "template_type": "breaking_news",
                "word_count": 425,
                "readability_score": 8.7,
                "fact_check_status": "verified"
            }
            
            result = await blog_templates.generate_news_article(
                news_data=news_data,
                style="professional",
                include_quotes=True
            )
            
            assert result["success"] is True
            assert result["word_count"] > 400
            assert result["readability_score"] > 8.0
            assert "Sam Altman" in str(result["article_content"])
    
    @pytest.mark.asyncio
    async def test_opinion_piece_template(self, blog_templates):
        """Test opinion piece template generation"""
        opinion_data = {
            "thesis": "AI content creation tools are making human creativity more important, not less",
            "arguments": [
                "AI handles routine tasks, freeing humans for creative strategy",
                "Human oversight ensures quality and authenticity",
                "Emotional intelligence remains uniquely human",
                "Creative vision and storytelling can't be replicated"
            ],
            "counterarguments": [
                "AI is becoming increasingly sophisticated",
                "Some creative tasks are already automated",
                "Cost pressures favor automation"
            ],
            "personal_experience": "As a content strategist, I've seen AI enhance rather than replace human creativity",
            "call_to_action": "Embrace AI as a creative partner, not a replacement"
        }
        
        with patch.object(blog_templates, '_generate_opinion_piece') as mock_opinion:
            mock_opinion.return_value = {
                "success": True,
                "opinion_content": {
                    "title": "Why AI Makes Human Creativity More Valuable, Not Less",
                    "introduction": """There's a growing fear that AI will replace human creativity in content creation. I believe the opposite is true. After working with AI tools for the past two years, I've discovered that artificial intelligence doesn't diminish human creativity—it amplifies it.
""",
                    "thesis_statement": "AI content creation tools are making human creativity more important, not less, by handling routine tasks and allowing humans to focus on strategic thinking and emotional connection.",
                    "main_arguments": [
                        {
                            "point": "AI handles routine tasks, freeing humans for creative strategy",
                            "evidence": "Studies show content creators spend 60% less time on basic writing tasks when using AI",
                            "example": "Instead of writing product descriptions, marketers can focus on campaign strategy"
                        },
                        {
                            "point": "Human oversight ensures quality and authenticity",
                            "evidence": "AI-generated content requires human editing for tone and accuracy",
                            "example": "Brand voice and emotional nuance still require human touch"
                        }
                    ],
                    "counterargument_section": """Critics argue that AI is becoming sophisticated enough to handle creative tasks independently. While this is partially true, the most successful content still requires human insight, empathy, and strategic thinking that AI cannot replicate.
""",
                    "conclusion": """The future of content creation isn't human versus AI—it's human with AI. Those who learn to leverage AI as a creative partner will produce better content faster than ever before. The key is embracing AI while doubling down on uniquely human skills.
""",
                    "call_to_action": "Start experimenting with AI tools today, but remember: your creativity and strategic thinking are what make the difference."
                },
                "template_type": "persuasive_opinion",
                "argument_strength": 8.5,
                "persuasiveness_score": 9.1,
                "controversy_level": "moderate"
            }
            
            result = await blog_templates.generate_opinion_piece(
                opinion_data=opinion_data,
                style="persuasive",
                include_counterarguments=True
            )
            
            assert result["success"] is True
            assert result["argument_strength"] > 8.0
            assert result["persuasiveness_score"] > 9.0
            assert "thesis_statement" in result["opinion_content"]
    
    @pytest.mark.asyncio
    async def test_seo_optimization(self, blog_templates, article_data):
        """Test SEO optimization for blog templates"""
        with patch.object(blog_templates, '_optimize_for_seo') as mock_seo:
            mock_seo.return_value = {
                "success": True,
                "seo_optimized_content": {
                    "title": "AI Content Creation Guide: 10 Tools & Strategies for 2025",
                    "meta_description": "Master AI content creation with our comprehensive guide. Discover top tools, proven strategies, and expert tips for automated content that converts.",
                    "h1": "The Complete AI Content Creation Guide for 2025",
                    "h2_tags": [
                        "What is AI Content Creation?",
                        "Top 10 AI Content Creation Tools",
                        "Best Practices for AI Content Strategy",
                        "Measuring AI Content Performance"
                    ],
                    "keyword_density": {
                        "ai content creation": 2.1,
                        "artificial intelligence": 1.8,
                        "content automation": 1.5
                    },
                    "internal_links": [
                        {"text": "content marketing strategy", "url": "/content-marketing-guide"},
                        {"text": "AI tools comparison", "url": "/ai-tools-review"}
                    ],
                    "featured_snippet_optimization": "AI content creation uses artificial intelligence to generate, optimize, and distribute content automatically...",
                    "schema_markup": {
                        "type": "Article",
                        "headline": "The Complete AI Content Creation Guide for 2025",
                        "author": "Fahed Mlaiel",
                        "datePublished": "2025-01-31"
                    }
                },
                "seo_score": 94.5,
                "keyword_optimization": 92.0,
                "technical_seo": 96.0,
                "content_quality": 93.5
            }
            
            result = await blog_templates.optimize_for_seo(
                content=article_data,
                target_keywords=article_data["target_keywords"],
                competitor_analysis=True
            )
            
            assert result["success"] is True
            assert result["seo_score"] > 94.0
            assert result["keyword_optimization"] > 90.0
            assert len(result["seo_optimized_content"]["h2_tags"]) >= 4
    
    @pytest.mark.asyncio
    async def test_blog_series_generation(self, blog_templates):
        """Test blog series generation"""
        series_data = {
            "series_title": "Mastering AI Content Creation",
            "series_description": "A comprehensive series on using AI for content marketing",
            "number_of_posts": 5,
            "target_audience": "content marketers",
            "progression": "beginner_to_advanced"
        }
        
        with patch.object(blog_templates, '_generate_blog_series') as mock_series:
            mock_series.return_value = {
                "success": True,
                "series_outline": {
                    "series_title": "Mastering AI Content Creation: A 5-Part Series",
                    "posts": [
                        {
                            "post_number": 1,
                            "title": "AI Content Creation 101: Getting Started",
                            "focus": "Introduction and basic concepts",
                            "word_count": 2000,
                            "difficulty": "beginner"
                        },
                        {
                            "post_number": 2,
                            "title": "Choosing the Right AI Tools for Your Content Strategy",
                            "focus": "Tool selection and evaluation",
                            "word_count": 2500,
                            "difficulty": "beginner-intermediate"
                        },
                        {
                            "post_number": 3,
                            "title": "Advanced AI Prompting Techniques for Better Content",
                            "focus": "Prompt engineering and optimization",
                            "word_count": 3000,
                            "difficulty": "intermediate"
                        },
                        {
                            "post_number": 4,
                            "title": "Building Automated Content Workflows with AI",
                            "focus": "Automation and integration",
                            "word_count": 3500,
                            "difficulty": "intermediate-advanced"
                        },
                        {
                            "post_number": 5,
                            "title": "Scaling AI Content: Enterprise Strategies and Best Practices",
                            "focus": "Enterprise implementation",
                            "word_count": 3000,
                            "difficulty": "advanced"
                        }
                    ],
                    "cross_references": [
                        "Each post links to relevant sections in other posts",
                        "Progressive skill building throughout series",
                        "Comprehensive resource library"
                    ]
                },
                "total_word_count": 14000,
                "estimated_reading_time": 56,
                "series_coherence_score": 95.5
            }
            
            result = await blog_templates.generate_blog_series(
                series_data=series_data,
                create_cross_references=True,
                progressive_difficulty=True
            )
            
            assert result["success"] is True
            assert len(result["series_outline"]["posts"]) == 5
            assert result["total_word_count"] > 10000
            assert result["series_coherence_score"] > 95.0
    
    @pytest.mark.asyncio
    async def test_content_repurposing(self, blog_templates, article_data):
        """Test content repurposing from blog articles"""
        with patch.object(blog_templates, '_repurpose_content') as mock_repurpose:
            mock_repurpose.return_value = {
                "success": True,
                "repurposed_content": {
                    "social_media_posts": [
                        {
                            "platform": "LinkedIn",
                            "content": "🚀 AI is transforming content creation...",
                            "character_count": 1200
                        },
                        {
                            "platform": "Twitter",
                            "content": "Thread: Why AI content creation is game-changing...",
                            "tweet_count": 5
                        }
                    ],
                    "email_newsletter": {
                        "subject": "Weekly AI Update: Content Creation Revolution",
                        "preview": "This week's insights on AI content tools...",
                        "content": "Formatted newsletter version..."
                    },
                    "infographic_outline": {
                        "title": "10 AI Content Creation Statistics",
                        "data_points": ["73% of marketers use AI", "40% time savings"],
                        "visual_elements": ["Charts", "Icons", "Timeline"]
                    },
                    "podcast_script": {
                        "intro": "Welcome to today's episode on AI content creation...",
                        "main_points": ["Tool overview", "Implementation tips"],
                        "duration": "15 minutes"
                    }
                },
                "repurposing_efficiency": 87.5,
                "content_variants": 8
            }
            
            result = await blog_templates.repurpose_content(
                source_article=article_data,
                target_formats=["social", "email", "infographic", "podcast"],
                maintain_core_message=True
            )
            
            assert result["success"] is True
            assert result["content_variants"] >= 8
            assert result["repurposing_efficiency"] > 85.0
            assert "social_media_posts" in result["repurposed_content"]


class TestArticleTemplate:
    """Test suite for ArticleTemplate"""
    
    def test_article_template_creation(self):
        """
Test article template creation"""
        template = ArticleTemplate(
            template_id="article_001",
            name="Standard Article",
            category=BlogCategory.TUTORIAL,
            min_word_count=1500,
            max_word_count=3000,
            sections=["introduction", "main_content", "conclusion"],
            seo_optimized=True
        )
        
        assert template.template_id == "article_001"
        assert template.name == "Standard Article"
        assert template.category == BlogCategory.TUTORIAL
        assert template.min_word_count == 1500
        assert template.seo_optimized is True


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
