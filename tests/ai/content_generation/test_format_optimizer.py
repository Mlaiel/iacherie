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
Format Optimizer Tests

Comprehensive tests for the FormatOptimizer class that handles
platform-specific content formatting and optimization.

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

from ai.content_generation.format_optimizer import (
    FormatOptimizer
)
from ai.content_generation.content_models import ContentType, Platform


class TestFormatOptimizer:
    """Test suite for FormatOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a format optimizer instance"""
        return FormatOptimizer()
    
    @pytest.fixture
    def sample_content(self):
        """Create sample content for formatting"""
        return """
        # The Future of AI Technology
        
        Artificial Intelligence is revolutionizing our world. Here are the key points:
        
        * Machine Learning advancements
        * Natural Language Processing improvements
        * Computer Vision breakthroughs
        * Robotics integration
        
        ## Benefits of AI
        
        AI technology offers numerous advantages:
        
        1. Increased efficiency
        2. Better decision making
        3. Cost reduction
        4. Enhanced user experience
        
        Visit our website: https://example.com/ai-guide
        Contact us: info@example.com
        
        #AI #Technology #Innovation #MachineLearning
        """
    
    @pytest.fixture
    def blog_content(self):
        """Create blog content for formatting"""
        return """
        # Complete Guide to AI in Business
        
        ## Introduction
        
        Artificial Intelligence (AI) is transforming the business landscape. This comprehensive guide explores how organizations can leverage AI technologies to drive growth and innovation.
        
        ## What is Business AI?
        
        Business AI refers to the application of artificial intelligence technologies in business operations. It includes:
        
        - **Machine Learning**: Algorithms that learn from data
        - **Natural Language Processing**: Understanding human language
        - **Computer Vision**: Analyzing visual content
        - **Predictive Analytics**: Forecasting future trends
        
        ## Implementation Strategies
        
        ### 1. Assessment Phase
        
        Before implementing AI, assess your current capabilities:
        
        - Data infrastructure
        - Technical expertise
        - Budget constraints
        - Business objectives
        
        ### 2. Pilot Projects
        
        Start with small, manageable projects:
        
        1. Identify use cases
        2. Select appropriate technologies
        3. Measure success metrics
        4. Scale successful implementations
        
        ## Conclusion
        
        AI implementation requires careful planning and execution. Start small, measure results, and scale gradually for best outcomes.
        """
    
    def test_optimizer_initialization(self, optimizer):
        """Test format optimizer initialization"""
        assert optimizer is not None
        assert hasattr(optimizer, 'platform_rules')
        assert hasattr(optimizer, 'formatting_engine')
        assert hasattr(optimizer, 'layout_templates')
        assert hasattr(optimizer, 'optimization_cache')
        
        # Check platform rules exist
        assert Platform.INSTAGRAM in optimizer.platform_rules
        assert Platform.LINKEDIN in optimizer.platform_rules
        assert Platform.TWITTER in optimizer.platform_rules
    
    @pytest.mark.asyncio
    async def test_instagram_formatting(self, optimizer, sample_content):
        """Test Instagram-specific formatting"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": """🚀 The Future of AI Technology
                
✨ AI is revolutionizing our world! Key points:

🤖 Machine Learning advancements
💬 Natural Language Processing improvements  
👁️ Computer Vision breakthroughs
🦾 Robotics integration

💡 Benefits of AI:
• Increased efficiency
• Better decision making
• Cost reduction  
• Enhanced user experience

🔗 Link in bio for full guide

#AI #Technology #Innovation #MachineLearning #FutureOfWork #ArtificialIntelligence""",
                "optimizations_applied": [
                    "added_emojis",
                    "shortened_sentences",
                    "optimized_hashtags",
                    "link_placement"
                ],
                "character_count": 445,
                "hashtag_count": 6
            }
            
            result = await optimizer.format_for_platform(
                content=sample_content,
                platform=Platform.INSTAGRAM,
                style="engaging"
            )
            
            assert result["success"] is True
            assert result["character_count"] <= 2200  # Instagram limit
            assert "emojis" in str(result["optimizations_applied"])
    
    @pytest.mark.asyncio
    async def test_linkedin_formatting(self, optimizer, blog_content):
        """Test LinkedIn-specific formatting"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": """🎯 Complete Guide to AI in Business

Artificial Intelligence is transforming the business landscape. Here's how organizations can leverage AI for growth:

📊 What is Business AI?

Business AI encompasses:
→ Machine Learning: Algorithms that learn from data
→ Natural Language Processing: Understanding human language  
→ Computer Vision: Analyzing visual content
→ Predictive Analytics: Forecasting future trends

🚀 Implementation Strategies

1️⃣ Assessment Phase
• Data infrastructure evaluation
• Technical expertise review
• Budget analysis
• Business objectives alignment

2️⃣ Pilot Projects
• Identify use cases
• Select appropriate technologies
• Measure success metrics
• Scale successful implementations

💡 Key Takeaway: AI implementation requires careful planning. Start small, measure results, and scale gradually for optimal outcomes.

What's your experience with AI in business? Share your thoughts below! 👇

#ArtificialIntelligence #BusinessStrategy #DigitalTransformation #Innovation #Technology""",
                "optimizations_applied": [
                    "professional_tone",
                    "bullet_points",
                    "call_to_action",
                    "engagement_hooks"
                ],
                "character_count": 1250,
                "engagement_score": 8.7
            }
            
            result = await optimizer.format_for_platform(
                content=blog_content,
                platform=Platform.LINKEDIN,
                style="professional"
            )
            
            assert result["success"] is True
            assert result["character_count"] <= 3000  # LinkedIn recommended limit
            assert result["engagement_score"] > 8.0
    
    @pytest.mark.asyncio
    async def test_twitter_thread_formatting(self, optimizer, blog_content):
        """Test Twitter thread formatting"""
        with patch.object(optimizer, '_format_as_thread') as mock_thread:
            mock_thread.return_value = {
                "success": True,
                "thread_tweets": [
                    "🧵 Thread: Complete Guide to AI in Business\n\nAI is transforming business. Here's how to leverage it for growth 👇\n\n1/7",
                    "📊 What is Business AI?\n\n→ Machine Learning: Algorithms that learn\n→ NLP: Understanding language\n→ Computer Vision: Analyzing visuals\n→ Predictive Analytics: Forecasting\n\n2/7",
                    "🚀 Implementation Strategy #1: Assessment\n\n• Data infrastructure\n• Technical expertise\n• Budget constraints\n• Business objectives\n\nStart here before diving into AI solutions.\n\n3/7",
                    "🎯 Implementation Strategy #2: Pilot Projects\n\n1. Identify use cases\n2. Select technologies\n3. Measure metrics\n4. Scale successes\n\nSmall steps lead to big wins!\n\n4/7",
                    "💡 Key Takeaway:\n\nAI implementation = careful planning + execution\n\nFormula for success:\n→ Start small\n→ Measure results\n→ Scale gradually\n\n5/7",
                    "🤔 What's your experience with AI in business?\n\nDrop your thoughts below! I'd love to hear your success stories and challenges.\n\n6/7",
                    "That's a wrap! 🎬\n\nRT the first tweet if this was helpful!\n\nFor more AI insights, follow @YourHandle\n\n#AI #Business #Innovation\n\n7/7"
                ],
                "tweet_count": 7,
                "total_characters": 1456,
                "thread_engagement_potential": 9.2
            }
            
            result = await optimizer.format_as_twitter_thread(
                content=blog_content,
                max_tweets=10,
                style="engaging"
            )
            
            assert result["success"] is True
            assert result["tweet_count"] == 7
            assert all(len(tweet) <= 280 for tweet in result["thread_tweets"])
    
    @pytest.mark.asyncio
    async def test_tiktok_formatting(self, optimizer, sample_content):
        """Test TikTok-specific formatting"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": """🤖 AI is CHANGING EVERYTHING! 

Here's what's happening RIGHT NOW:

🧠 Machine Learning = computers that learn
💬 NLP = computers that understand us  
👀 Computer Vision = computers that see
🤖 Robotics = computers that move

WHY THIS MATTERS:
✅ Work gets easier
✅ Decisions get smarter  
✅ Costs go down
✅ Life gets better

The future is HERE! 🚀

What AI tool do you use? Tell me! ⬇️

#AI #Tech #Future #Innovation #MachineLearning #TechTok #FYP""",
                "optimizations_applied": [
                    "short_sentences",
                    "caps_emphasis",
                    "trending_hashtags",
                    "engagement_hooks"
                ],
                "character_count": 520,
                "virality_score": 8.9
            }
            
            result = await optimizer.format_for_platform(
                content=sample_content,
                platform=Platform.TIKTOK,
                style="viral"
            )
            
            assert result["success"] is True
            assert result["character_count"] <= 2200
            assert result["virality_score"] > 8.0
    
    @pytest.mark.asyncio
    async def test_youtube_description_formatting(self, optimizer, blog_content):
        """Test YouTube description formatting"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": """🎯 Complete Guide to AI in Business | Everything You Need to Know

In this comprehensive video, we dive deep into how Artificial Intelligence is transforming the business landscape and how your organization can leverage AI technologies for growth and innovation.

📋 WHAT YOU'LL LEARN:
• What is Business AI and why it matters
• Key AI technologies: ML, NLP, Computer Vision, Predictive Analytics
• Step-by-step implementation strategies
• Assessment phase best practices
• How to run successful pilot projects
• Scaling strategies for maximum impact

⏰ TIMESTAMPS:
00:00 Introduction
02:15 What is Business AI?
05:30 Key Technologies Overview
08:45 Implementation Strategies
12:20 Assessment Phase
15:10 Pilot Projects
18:30 Scaling Your Success
21:00 Conclusion & Next Steps

🔗 USEFUL LINKS:
• AI Implementation Checklist: https://example.com/checklist
• Free AI Assessment Tool: https://example.com/assessment
• Join our AI Community: https://example.com/community

💡 RELATED VIDEOS:
• Machine Learning Basics: [Link]
• AI Tools for Small Business: [Link]
• Future of Work with AI: [Link]

👍 If this video helped you, please LIKE and SUBSCRIBE for more AI business content!

🔔 Ring the bell to get notified when we post new videos!

💬 QUESTIONS? Drop them in the comments below - I read and respond to every one!

#ArtificialIntelligence #BusinessAI #MachineLearning #DigitalTransformation #Innovation #Technology #Business #Entrepreneurship""",
                "optimizations_applied": [
                    "structured_sections",
                    "timestamps",
                    "call_to_action",
                    "keyword_optimization"
                ],
                "character_count": 1456,
                "seo_score": 9.1
            }
            
            result = await optimizer.format_for_platform(
                content=blog_content,
                platform=Platform.YOUTUBE,
                style="educational",
                include_timestamps=True
            )
            
            assert result["success"] is True
            assert "TIMESTAMPS:" in result["formatted_content"]
            assert result["seo_score"] > 9.0
    
    @pytest.mark.asyncio
    async def test_email_formatting(self, optimizer, blog_content):
        """Test email newsletter formatting"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": """Subject: 🚀 Your Complete Guide to AI in Business (7-minute read)

Hi [First Name],

Hope you're having a great week! 

I've been getting lots of questions about implementing AI in business, so I put together this comprehensive guide for you.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WHAT IS BUSINESS AI?

Business AI is the application of artificial intelligence in business operations. It includes:

→ Machine Learning: Algorithms that learn from data
→ Natural Language Processing: Understanding human language
→ Computer Vision: Analyzing visual content  
→ Predictive Analytics: Forecasting future trends

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 IMPLEMENTATION STRATEGIES

**Phase 1: Assessment**
• Evaluate your data infrastructure
• Review technical expertise
• Analyze budget constraints
• Align with business objectives

**Phase 2: Pilot Projects**
1. Identify specific use cases
2. Select appropriate technologies
3. Define success metrics
4. Scale successful implementations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 KEY TAKEAWAY

AI implementation requires careful planning and execution. The winning formula:

Start small → Measure results → Scale gradually

This approach minimizes risk while maximizing your chances of success.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 WHAT'S NEXT?

Want to dive deeper? Here are your next steps:

1. **Download our AI Readiness Checklist** → [Link]
2. **Join our free AI Masterclass** → [Link]  
3. **Book a strategy call** → [Link]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

That's all for today! Reply and let me know - what's your biggest AI challenge right now?

Best regards,
[Your Name]

P.S. Forward this email to anyone who could benefit from implementing AI in their business!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 Need help? Just reply to this email
🌐 Visit our website: [Link]
📱 Follow us: [Social Links]

Unsubscribe | Update Preferences""",
                "optimizations_applied": [
                    "personal_tone",
                    "clear_structure",
                    "call_to_action",
                    "mobile_friendly"
                ],
                "character_count": 1789,
                "readability_score": 8.5
            }
            
            result = await optimizer.format_for_platform(
                content=blog_content,
                platform=Platform.EMAIL,
                style="newsletter",
                personalization=True
            )
            
            assert result["success"] is True
            assert "Subject:" in result["formatted_content"]
            assert result["readability_score"] > 8.0
    
    @pytest.mark.asyncio
    async def test_responsive_formatting(self, optimizer, sample_content):
        """Test responsive formatting for multiple devices"""
        with patch.object(optimizer, '_create_responsive_format') as mock_responsive:
            mock_responsive.return_value = {
                "success": True,
                "formats": {
                    "mobile": {
                        "content": "Short, punchy mobile version...",
                        "layout": "single_column",
                        "font_size": "16px",
                        "line_height": "1.5"
                    },
                    "tablet": {
                        "content": "Medium-length tablet version...",
                        "layout": "two_column",
                        "font_size": "18px",
                        "line_height": "1.6"
                    },
                    "desktop": {
                        "content": "Full desktop version...",
                        "layout": "multi_column",
                        "font_size": "16px",
                        "line_height": "1.7"
                    }
                },
                "breakpoints": {
                    "mobile": "320px-768px",
                    "tablet": "768px-1024px", 
                    "desktop": "1024px+"
                }
            }
            
            result = await optimizer.create_responsive_format(
                content=sample_content,
                target_devices=["mobile", "tablet", "desktop"],
                adaptive_layout=True
            )
            
            assert result["success"] is True
            assert len(result["formats"]) == 3
            assert "mobile" in result["formats"]
            assert "breakpoints" in result
    
    @pytest.mark.asyncio
    async def test_accessibility_formatting(self, optimizer, sample_content):
        """Test accessibility-focused formatting"""
        with patch.object(optimizer, '_format_for_accessibility') as mock_accessibility:
            mock_accessibility.return_value = {
                "success": True,
                "accessible_content": """<article role="main">
<h1>The Future of AI Technology</h1>

<p>Artificial Intelligence is revolutionizing our world. Here are the key points:</p>

<ul role="list">
<li>Machine Learning advancements</li>
<li>Natural Language Processing improvements</li>
<li>Computer Vision breakthroughs</li>
<li>Robotics integration</li>
</ul>

<h2>Benefits of <abbr title="Artificial Intelligence">AI</abbr></h2>

<p><abbr title="Artificial Intelligence">AI</abbr> technology offers numerous advantages:</p>

<ol role="list">
<li>Increased efficiency</li>
<li>Better decision making</li>
<li>Cost reduction</li>
<li>Enhanced user experience</li>
</ol>

<p>Visit our website: <a href="https://example.com/ai-guide" aria-label="AI Guide on our website">https://example.com/ai-guide</a></p>
<p>Contact us: <a href="mailto:info@example.com" aria-label="Email us at info@example.com">info@example.com</a></p>

<div role="group" aria-label="Related hashtags">
<span class="hashtag">#AI</span>
<span class="hashtag">#Technology</span>
<span class="hashtag">#Innovation</span>
<span class="hashtag">#MachineLearning</span>
</div>
</article>""",
                "accessibility_features": [
                    "semantic_html",
                    "aria_labels",
                    "proper_headings",
                    "abbr_tags",
                    "role_attributes"
                ],
                "wcag_compliance": "AA",
                "screen_reader_friendly": True
            }
            
            result = await optimizer.format_for_accessibility(
                content=sample_content,
                wcag_level="AA",
                screen_reader_optimization=True
            )
            
            assert result["success"] is True
            assert result["wcag_compliance"] == "AA"
            assert result["screen_reader_friendly"] is True
    
    @pytest.mark.asyncio
    async def test_multi_platform_optimization(self, optimizer, sample_content):
        """Test multi-platform optimization"""
        platforms = [Platform.INSTAGRAM, Platform.LINKEDIN, Platform.TWITTER]
        
        with patch.object(optimizer, '_optimize_for_platforms') as mock_multi:
            mock_multi.return_value = {
                "success": True,
                "platform_versions": {
                    Platform.INSTAGRAM.value: {
                        "content": "Instagram optimized version...",
                        "character_count": 445,
                        "hashtags": 6,
                        "engagement_potential": 8.7
                    },
                    Platform.LINKEDIN.value: {
                        "content": "LinkedIn professional version...",
                        "character_count": 1250,
                        "engagement_potential": 9.1,
                        "professional_score": 9.5
                    },
                    Platform.TWITTER.value: {
                        "content": "Twitter thread version...",
                        "tweet_count": 5,
                        "total_characters": 1100,
                        "thread_potential": 8.9
                    }
                },
                "optimization_time": 3.2,
                "total_versions": 3
            }
            
            result = await optimizer.optimize_for_multiple_platforms(
                content=sample_content,
                platforms=platforms,
                maintain_core_message=True
            )
            
            assert result["success"] is True
            assert len(result["platform_versions"]) == 3
            assert result["total_versions"] == 3
    
    @pytest.mark.asyncio
    async def test_custom_formatting_rules(self, optimizer, sample_content):
        """Test custom formatting rules"""
        custom_rules = {
            "max_sentence_length": 20,
            "emoji_usage": "minimal",
            "link_format": "shortened",
            "hashtag_placement": "end",
            "call_to_action": "required"
        }
        
        with patch.object(optimizer, '_apply_custom_rules') as mock_custom:
            mock_custom.return_value = {
                "success": True,
                "formatted_content": "Custom formatted content...",
                "rules_applied": [
                    "sentence_length_optimized",
                    "minimal_emojis_used",
                    "links_shortened",
                    "hashtags_moved_to_end",
                    "cta_added"
                ],
                "compliance_score": 95.5
            }
            
            result = await optimizer.apply_custom_formatting(
                content=sample_content,
                rules=custom_rules,
                strict_compliance=True
            )
            
            assert result["success"] is True
            assert len(result["rules_applied"]) == 5
            assert result["compliance_score"] > 95.0
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, optimizer, sample_content):
        """Test performance optimization features"""
        with patch.object(optimizer, '_format_for_platform') as mock_format:
            mock_format.return_value = {
                "success": True,
                "formatted_content": "Optimized content...",
                "performance_metrics": {
                    "formatting_time": 0.85,
                    "memory_usage": 45.2,
                    "cache_hits": 12,
                    "cache_misses": 2
                }
            }
            
            result = await optimizer.format_for_platform(
                content=sample_content,
                platform=Platform.INSTAGRAM,
                use_cache=True,
                track_performance=True
            )
            
            assert result["success"] is True
            assert "performance_metrics" in result
            assert result["performance_metrics"]["formatting_time"] < 1.0


class TestPlatformFormat:
    """Test suite for PlatformFormat model"""
    
    def test_platform_format_creation(self):
        """Test platform format creation"""
        format_config = PlatformFormat(
            platform=Platform.INSTAGRAM,
            max_characters=2200,
            max_hashtags=30,
            supports_emojis=True,
            supports_links=True,
            optimal_length=500
        )
        
        assert format_config.platform == Platform.INSTAGRAM
        assert format_config.max_characters == 2200
        assert format_config.max_hashtags == 30
        assert format_config.supports_emojis is True
        assert format_config.optimal_length == 500


class TestOptimizationRule:
    """Test suite for OptimizationRule model"""
    
    def test_optimization_rule_creation(self):
        """Test optimization rule creation"""
        rule = OptimizationRule(
            rule_id="emoji_limit",
            description="Limit emoji usage",
            condition="emoji_count > 5",
            action="reduce_emojis",
            priority="medium"
        )
        
        assert rule.rule_id == "emoji_limit"
        assert rule.description == "Limit emoji usage"
        assert rule.condition == "emoji_count > 5"
        assert rule.action == "reduce_emojis"
        assert rule.priority == "medium"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
