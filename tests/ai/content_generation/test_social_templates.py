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
Social Media Templates Tests

Comprehensive tests for social media template system that handles
platform-specific content templates and generation.

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

from ai.content_generation.social_templates import (
    SocialMediaTemplates, 
    TemplateEngine, 
    InstagramTemplate
)
from ai.content_generation.content_models import ContentType, Platform


class TestSocialMediaTemplates:
    """Test suite for SocialMediaTemplates"""
    
    @pytest.fixture
    def templates(self):
        """Create a social media templates instance"""



        return SocialMediaTemplates()
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample template variables"""



        return {
            "title": "The Future of AI Technology",
            "description": "Exploring how artificial intelligence will transform our world",
            "author": "Fahed Mlaiel",
            "date": "2025-01-31",
            "hashtags": ["#AI", "#Technology", "#Innovation"],
            "call_to_action": "Learn more in our latest blog post",
            "website": "https://example.com",
            "brand_name": "TechInnovate"
        }
    
    @pytest.fixture
    def instagram_data(self):
        """Create Instagram-specific data"""



        return {
            "image_url": "https://example.com/ai-image.jpg",
            "story_highlights": ["Tech", "AI", "Innovation"],
            "location": "San Francisco, CA",
            "mentions": ["@techexpert", "@ainews"],
            "carousel_images": [
                "https://example.com/slide1.jpg",
                "https://example.com/slide2.jpg",
                "https://example.com/slide3.jpg"
            ]
        }
    
    def test_templates_initialization(self, templates):
        """Test social media templates initialization"""
        assert templates is not None
        assert hasattr(templates, 'instagram_templates')
        assert hasattr(templates, 'twitter_templates')
        assert hasattr(templates, 'linkedin_templates')
        assert hasattr(templates, 'tiktok_templates')
        
        # Check platform templates exist
        assert len(templates.instagram_templates) > 0
        assert len(templates.twitter_templates) > 0
        assert len(templates.linkedin_templates) > 0
        assert len(templates.tiktok_templates) > 0
    
    @pytest.mark.asyncio
    async def test_instagram_post_template(self, templates, sample_variables, instagram_data):
        """Test Instagram post template generation"""
        with patch.object(templates, '_generate_from_template') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "content": """ The Future of AI Technology

Exploring how artificial intelligence will transform our world 

Key insights:
• Revolutionary changes ahead
• Impact on daily life
• Opportunities for innovation

Learn more in our latest blog post 

#AI #Technology #Innovation #FutureOfWork #ArtificialIntelligence

 San Francisco, CA
 @techexpert @ainews""",
                "template_used": "instagram_standard_post",
                "character_count": 365,
                "hashtag_count": 5,
                "mention_count": 2
            }
            
            merged_data = {**sample_variables, **instagram_data}
            
            result = await templates.generate_instagram_post(
                template_type="standard_post",
                variables=merged_data,
                style="engaging"
            )
            
            assert result["success"] is True
            assert result["character_count"] <= 2200  # Instagram limit
            assert result["hashtag_count"] <= 30  # Instagram limit
    
    @pytest.mark.asyncio
    async def test_instagram_story_template(self, templates, sample_variables):
        """Test Instagram story template generation"""
        with patch.object(templates, '_generate_from_template') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "stories": [
                    {
                        "slide": 1,
                        "content": " The Future of AI\n\nSwipe for key insights →",
                        "background": "gradient_tech",
                        "text_position": "center"
                    },
                    {
                        "slide": 2,
                        "content": " AI will transform:\n\n• How we work\n• How we learn\n• How we live",
                        "background": "solid_dark",
                        "text_position": "bottom"
                    },
                    {
                        "slide": 3,
                        "content": "Learn more \nLink in bio",
                        "background": "brand_colors",
                        "text_position": "center"
                    }
                ],
                "template_used": "instagram_story_series",
                "slide_count": 3,
                "duration": "15s_each"
            }
            
            result = await templates.generate_instagram_story(
                template_type="story_series",
                variables=sample_variables,
                slide_count=3
            )
            
            assert result["success"] is True
            assert len(result["stories"]) == 3
            assert result["slide_count"] == 3
    
    @pytest.mark.asyncio
    async def test_twitter_thread_template(self, templates, sample_variables):
        """Test Twitter thread template generation"""
        with patch.object(templates, '_generate_from_template') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "thread": [
                    "🧵 Thread: The Future of AI Technology\n\nAI is about to transform our world in ways we can barely imagine. Here's what you need to know \n\n1/5",
                    " Key Areas of Transformation:\n\n• Workplace automation\n• Healthcare innovation\n• Educational personalization\n• Creative industries\n\nEach will see revolutionary changes in the next 5 years.\n\n2/5",
                    " What This Means for You:\n\n→ New job opportunities\n→ Enhanced productivity tools\n→ Personalized experiences\n→ Faster problem-solving\n\nAdaptation is key to thriving.\n\n3/5",
                    " Getting Prepared:\n\n1. Stay informed about AI trends\n2. Develop AI-adjacent skills\n3. Experiment with AI tools\n4. Network with AI professionals\n\nThe future belongs to the prepared.\n\n4/5",
                    "That's a wrap! \n\nRT the first tweet if this was helpful!\n\nFor more AI insights, follow @TechInnovate\n\n#AI #Technology #Innovation\n\n5/5"
                ],
                "template_used": "twitter_educational_thread",
                "tweet_count": 5,
                "total_characters": 1156
            }
            
            result = await templates.generate_twitter_thread(
                template_type="educational_thread",
                variables=sample_variables,
                max_tweets=5
            )
            
            assert result["success"] is True
            assert result["tweet_count"] == 5
            assert all(len(tweet) <= 280 for tweet in result["thread"])
    
    @pytest.mark.asyncio
    async def test_linkedin_post_template(self, templates, sample_variables):
        """Test LinkedIn post template generation"""
        with patch.object(templates, '_generate_from_template') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "content": """ The Future of AI Technology: What Every Professional Should Know

Artificial intelligence isn't just coming—it's here, and it's reshaping how we work, innovate, and solve complex problems.

 Key Transformation Areas:

→ Automated Decision Making: AI systems processing data faster than ever
→ Predictive Analytics: Forecasting trends with unprecedented accuracy  
→ Personalized Experiences: Tailoring solutions to individual needs
→ Enhanced Productivity: Streamlining workflows and eliminating repetitive tasks

 Strategic Implications for Leaders:

• Invest in AI literacy across your organization
• Identify high-impact use cases for your industry
• Develop ethical AI governance frameworks
• Foster a culture of continuous learning and adaptation

 The organizations that embrace AI thoughtfully today will lead their industries tomorrow.

What's your organization's AI strategy? Share your thoughts in the comments—I'd love to hear about your experiences and challenges.

#ArtificialIntelligence #Leadership #DigitalTransformation #Innovation #BusinessStrategy""",
                "template_used": "linkedin_thought_leadership",
                "character_count": 1247,
                "engagement_potential": 9.2,
                "professional_score": 9.5
            }
            
            result = await templates.generate_linkedin_post(
                template_type="thought_leadership",
                variables=sample_variables,
                style="professional"
            )
            
            assert result["success"] is True
            assert result["character_count"] <= 3000  # LinkedIn limit
            assert result["professional_score"] > 9.0
    
    @pytest.mark.asyncio
    async def test_tiktok_script_template(self, templates, sample_variables):
        """Test TikTok script template generation"""
        with patch.object(templates, '_generate_from_template') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "script": {
                    "hook": "🤖 AI is literally changing EVERYTHING and you need to know THIS! (0-3s)",
                    "problem": "Most people think AI is just ChatGPT... but it's SO much more! (3-8s)",
                    "solution": "Here are 3 ways AI is already transforming your life: (8-12s)",
                    "points": [
                        "1. Your phone's camera uses AI to make your photos look amazing (12-18s)",
                        "2. Netflix uses AI to recommend shows you'll actually love (18-24s)", 
                        "3. Your GPS uses AI to find the fastest route in real-time (24-30s)"
                    ],
                    "call_to_action": "Follow for more AI facts that'll blow your mind! (30-35s)",
                    "outro": "What AI tool do you use daily? Tell me in the comments! (35-40s)"
                },
                "template_used": "tiktok_educational_hook",
                "duration": "40_seconds",
                "virality_score": 8.7,
                "trending_elements": ["hook", "countdown", "engagement"]
            }
            
            result = await templates.generate_tiktok_script(
                template_type="educational_hook",
                variables=sample_variables,
                duration=40
            )
            
            assert result["success"] is True
            assert result["duration"] == "40_seconds"
            assert result["virality_score"] > 8.0
    
    @pytest.mark.asyncio
    async def test_template_customization(self, templates, sample_variables):
        """Test template customization functionality"""
        custom_template = {
            "name": "custom_tech_post",
            "platform": Platform.INSTAGRAM,
            "structure": [
                " {title}",
                "",
                "{description}",
                "",
                "Key highlights:",
                "• {highlight_1}",
                "• {highlight_2}",
                "• {highlight_3}",
                "",
                "{call_to_action}",
                "",
                "{hashtags}"
            ],
            "variables": ["title", "description", "highlight_1", "highlight_2", "highlight_3", "call_to_action", "hashtags"],
            "style_rules": {
                "emoji_usage": "minimal",
                "tone": "professional",
                "max_length": 1500
            }
        }
        
        with patch.object(templates, '_create_custom_template') as mock_custom:
            mock_custom.return_value = {
                "success": True,
                "template_id": "custom_tech_post_001",
                "template_saved": True,
                "preview": " The Future of AI Technology\n\nExploring how artificial intelligence...",
                "validation_score": 95.5
            }
            
            result = await templates.create_custom_template(
                template_config=custom_template,
                validate_template=True,
                save_template=True
            )
            
            assert result["success"] is True
            assert result["template_saved"] is True
            assert result["validation_score"] > 95.0
    
    @pytest.mark.asyncio
    async def test_template_analytics(self, templates):
        """Test template performance analytics"""
        with patch.object(templates, '_analyze_template_performance') as mock_analytics:
            mock_analytics.return_value = {
                "success": True,
                "template_stats": {
                    "instagram_standard_post": {
                        "usage_count": 156,
                        "avg_engagement": 8.7,
                        "success_rate": 0.92,
                        "top_performing_variables": ["title", "hashtags"]
                    },
                    "twitter_educational_thread": {
                        "usage_count": 89,
                        "avg_engagement": 9.1,
                        "success_rate": 0.88,
                        "top_performing_variables": ["hook", "thread_structure"]
                    }
                },
                "recommendations": [
                    "Increase emoji usage in Instagram templates",
                    "Optimize hashtag placement for better reach",
                    "Test shorter thread lengths for Twitter"
                ]
            }
            
            result = await templates.analyze_template_performance(
                time_period="30_days",
                platforms=[Platform.INSTAGRAM, Platform.TWITTER],
                include_recommendations=True
            )
            
            assert result["success"] is True
            assert len(result["template_stats"]) == 2
            assert len(result["recommendations"]) == 3
    
    @pytest.mark.asyncio
    async def test_multi_platform_template_generation(self, templates, sample_variables):
        """Test generating content for multiple platforms from one template"""
        platforms = [Platform.INSTAGRAM, Platform.LINKEDIN, Platform.TWITTER]
        
        with patch.object(templates, '_generate_multi_platform') as mock_multi:
            mock_multi.return_value = {
                "success": True,
                "platform_content": {
                    Platform.INSTAGRAM.value: {
                        "content": " Instagram optimized content...",
                        "character_count": 445,
                        "engagement_score": 8.7
                    },
                    Platform.LINKEDIN.value: {
                        "content": "Professional LinkedIn content...",
                        "character_count": 1247,
                        "engagement_score": 9.2
                    },
                    Platform.TWITTER.value: {
                        "content": "Twitter optimized content...",
                        "character_count": 276,
                        "engagement_score": 8.9
                    }
                },
                "consistency_score": 92.5,
                "adaptation_time": 2.3
            }
            
            result = await templates.generate_for_multiple_platforms(
                base_template="tech_announcement",
                platforms=platforms,
                variables=sample_variables,
                maintain_core_message=True
            )
            
            assert result["success"] is True
            assert len(result["platform_content"]) == 3
            assert result["consistency_score"] > 90.0
    
    @pytest.mark.asyncio
    async def test_template_a_b_testing(self, templates, sample_variables):
        """Test A/B testing for templates"""
        with patch.object(templates, '_run_ab_test') as mock_ab_test:
            mock_ab_test.return_value = {
                "success": True,
                "test_results": {
                    "template_a": {
                        "name": "emoji_heavy",
                        "engagement_rate": 0.087,
                        "click_through_rate": 0.032,
                        "conversion_rate": 0.015
                    },
                    "template_b": {
                        "name": "minimal_emoji",
                        "engagement_rate": 0.094,
                        "click_through_rate": 0.028,
                        "conversion_rate": 0.018
                    }
                },
                "winner": "template_b",
                "confidence_level": 0.95,
                "improvement": "6.9% engagement increase"
            }
            
            result = await templates.run_template_ab_test(
                template_a="emoji_heavy",
                template_b="minimal_emoji",
                variables=sample_variables,
                platform=Platform.INSTAGRAM,
                test_duration_hours=48
            )
            
            assert result["success"] is True
            assert result["winner"] == "template_b"
            assert result["confidence_level"] == 0.95
    
    @pytest.mark.asyncio
    async def test_seasonal_template_adaptation(self, templates, sample_variables):
        """Test seasonal template adaptation"""
        with patch.object(templates, '_adapt_for_season') as mock_seasonal:
            mock_seasonal.return_value = {
                "success": True,
                "adapted_content": """ New Year, New AI Possibilities!

As we kick off 2025, artificial intelligence is set to transform our world in unprecedented ways.

 What's coming this year:
• Advanced AI assistants
• Smarter automation
• Personalized experiences
• Revolutionary breakthroughs

Ready to embrace the AI revolution? Learn more in our latest blog post!

#AI #Technology #2025Goals #Innovation #NewYear""",
                "seasonal_elements": ["new_year_theme", "2025_focus", "resolution_angle"],
                "adaptation_score": 88.5,
                "seasonal_hashtags": ["#2025Goals", "#NewYear"]
            }
            
            result = await templates.adapt_for_season(
                base_template="tech_announcement",
                variables=sample_variables,
                season="new_year",
                platform=Platform.INSTAGRAM
            )
            
            assert result["success"] is True
            assert result["adaptation_score"] > 85.0
            assert "#NewYear" in result["seasonal_hashtags"]
    
    @pytest.mark.asyncio
    async def test_template_validation(self, templates):
        """Test template validation functionality"""
        invalid_template = {
            "name": "test_template",
            "platform": Platform.INSTAGRAM,
            "structure": ["Too many characters " * 100],  # Exceeds Instagram limit
            "variables": ["missing_var"]  # References undefined variable
        }
        
        with patch.object(templates, '_validate_template') as mock_validation:
            mock_validation.return_value = {
                "success": False,
                "valid": False,
                "errors": [
                    "Template exceeds platform character limit",
                    "Undefined variable 'missing_var' referenced",
                    "Missing required variables: title, description"
                ],
                "warnings": [
                    "Consider adding hashtags for better reach",
                    "Call-to-action not present"
                ],
                "validation_score": 35.2
            }
            
            result = await templates.validate_template(
                template_config=invalid_template,
                strict_validation=True
            )
            
            assert result["success"] is False
            assert result["valid"] is False
            assert len(result["errors"]) == 3
            assert result["validation_score"] < 50.0


class TestTemplateEngine:
    """Test suite for TemplateEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create a template engine instance"""



        return TemplateEngine()
    
    def test_engine_initialization(self, engine):
        """Test template engine initialization"""
        assert engine is not None
        assert hasattr(engine, 'template_parser')
        assert hasattr(engine, 'variable_resolver')
        assert hasattr(engine, 'formatting_engine')
    
    @pytest.mark.asyncio
    async def test_variable_substitution(self, engine):
        """Test variable substitution in templates"""
        template = "Hello {name}, welcome to {platform}! Check out our {content_type}."
        variables = {
            "name": "Fahed",
            "platform": "Instagram", 
            "content_type": "AI guide"
        }
        
        result = await engine.substitute_variables(template, variables)
        
        expected = "Hello Fahed, welcome to Instagram! Check out our AI guide."
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_conditional_logic(self, engine):
        """Test conditional logic in templates"""
        template = """
        {%if has_image%}
         Check out this amazing visual!
        {%endif%}
        
        {title}
        
        {%if author%}
        By: {author}
        {%endif%}
        """
        
        variables = {
            "has_image": True,
            "title": "AI Technology Guide",
            "author": "Fahed Mlaiel"
        }
        
        with patch.object(engine, 'process_conditionals') as mock_conditionals:
            mock_conditionals.return_value = """ Check out this amazing visual!

AI Technology Guide

By: Fahed Mlaiel"""
            
            result = await engine.process_template(template, variables)
            
            assert " Check out this amazing visual!" in result
            assert "By: Fahed Mlaiel" in result


class TestInstagramTemplate:
    """Test suite for InstagramTemplate"""
    
    def test_instagram_template_creation(self):
        """Test Instagram template creation"""
        template = InstagramTemplate(
            template_id="ig_001",
            name="Standard Post",
            category=TemplateCategory.EDUCATIONAL,
            max_characters=2200,
            supports_carousel=True,
            optimal_hashtags=15
        )
        
        assert template.template_id == "ig_001"
        assert template.name == "Standard Post"
        assert template.max_characters == 2200
        assert template.supports_carousel is True
        assert template.optimal_hashtags == 15


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
