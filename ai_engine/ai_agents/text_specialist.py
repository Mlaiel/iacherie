"""Text Specialist Agent

AI-powered text content creation, editing, and optimization agent for influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import re

from .base_agent import BaseAIAgent, AgentCapability, AgentStatus, AgentConfiguration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """
Text content types"""

    SOCIAL_MEDIA_POST = "social_media_post"
    BLOG_ARTICLE = "blog_article"
    VIDEO_SCRIPT = "video_script"
    PODCAST_SCRIPT = "podcast_script"
    CAPTION = "caption"
    HASHTAG_SET = "hashtag_set"
    EMAIL_NEWSLETTER = "email_newsletter"
    PRODUCT_DESCRIPTION = "product_description"
    PRESS_RELEASE = "press_release"
    BIO = "bio"

class WritingStyle(Enum):
    """Writing style categories"""

    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    PERSUASIVE = "persuasive"
    INSPIRATIONAL = "inspirational"
    INFORMATIVE = "informative"
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"

class ToneOfVoice(Enum):
    """Tone of voice options"""

    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    ENTHUSIASTIC = "enthusiastic"
    PROFESSIONAL = "professional"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    CONFIDENT = "confident"
    WARM = "warm"
    WITTY = "witty"

@dataclass
class TextProject:
    """Text content project"""
    project_id: str
    title: str
    content_type: ContentType
    style: WritingStyle
    tone: ToneOfVoice
    target_audience: str
    target_platforms: List[str]
    word_count_target: int
    keywords: List[str] = field(default_factory=list)
    status: str = "created"
    created_at: datetime = field(default_factory=datetime.now)
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentRequirements:
    """Content creation requirements"""
    topic: str
    key_points: List[str]
    target_length: int
    seo_keywords: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None
    brand_voice: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentOptimization:
    """
Content optimization suggestions"""
    readability_score: float
    seo_score: float
    engagement_score: float
    suggestions: List[str]
    optimized_version: str = ""

class TextSpecialistAgent(BaseAIAgent):
    """AI agent for text content creation, editing, and optimization"""
    
    def __init__(self, config: AgentConfiguration):
        super().__init__(config)
        self.name = "TextSpecialistAgent"
        self.capabilities = [
            AgentCapability.CONTENT_CREATION,
            AgentCapability.ANALYSIS,
            AgentCapability.OPTIMIZATION,
            AgentCapability.COMMUNICATION
        ]
        
        # Text processing state
        self.active_projects: Dict[str, TextProject] = {}
        self.content_templates: Dict[str, str] = {}
        self.brand_voices: Dict[str, Dict[str, Any]] = {}
        
        # Text processing tools
        self.writing_guidelines = self._load_writing_guidelines()
        self.platform_requirements = self._load_platform_requirements()
        self.content_formulas = self._initialize_content_formulas()
        
        logger.info("Text Specialist Agent initialized successfully")
    
    async def create_text_project(self, title: str, content_type: ContentType, style: WritingStyle,
                                tone: ToneOfVoice, target_audience: str, target_platforms: List[str],
                                word_count: int) -> TextProject:
        """Create a new text content project"""
        try:
            project = TextProject(
                project_id=f"text_project_{datetime.now().timestamp()}",
                title=title,
                content_type=content_type,
                style=style,
                tone=tone,
                target_audience=target_audience,
                target_platforms=target_platforms,
                word_count_target=word_count
            )
            
            self.active_projects[project.project_id] = project
            
            logger.info(f"Created text project: {project.title} ({project.project_id})")
            return project
            
        except Exception as e:
            logger.error(f"Error creating text project: {str(e)}")
            return None
    
    async def generate_content(self, project_id: str, requirements: ContentRequirements) -> str:
        """Generate text content based on project and requirements"""
        try:
            if project_id not in self.active_projects:
                return ""
            
            project = self.active_projects[project_id]
            
            # Generate content outline
            outline = await self._create_content_outline(project, requirements)
            
            # Generate content sections
            content_sections = []
            for section in outline:
                section_content = await self._generate_content_section(section, project, requirements)
                content_sections.append(section_content)
            
            # Combine sections
            generated_content = await self._combine_content_sections(content_sections, project)
            
            # Apply style and tone
            styled_content = await self._apply_style_and_tone(generated_content, project)
            
            project.content = styled_content
            project.status = "generated"
            
            logger.info(f"Generated content for project {project_id}")
            return styled_content
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return ""
    
    async def optimize_content(self, content: str, platform: str, objectives: List[str]) -> ContentOptimization:
        """Optimize content for specific platform and objectives"""
        try:
            optimization = ContentOptimization(
                readability_score=await self._calculate_readability(content),
                seo_score=await self._calculate_seo_score(content, platform),
                engagement_score=await self._predict_engagement(content, platform),
                suggestions=await self._generate_optimization_suggestions(content, platform, objectives)
            )
            
            # Create optimized version
            optimization.optimized_version = await self._apply_optimizations(content, optimization.suggestions)
            
            logger.info(f"Content optimization completed for {platform}")
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return ContentOptimization(0.0, 0.0, 0.0, [])
    
    async def generate_hashtags(self, content: str, platform: str, count: int = 20) -> List[str]:
        """Generate relevant hashtags for content"""
        try:
            # Extract key topics and themes
            key_topics = await self._extract_key_topics(content)
            
            # Generate hashtags based on topics
            hashtags = []
            
            # Add topic-based hashtags
            for topic in key_topics:
                topic_hashtags = await self._generate_topic_hashtags(topic, platform)
                hashtags.extend(topic_hashtags)
            
            # Add platform-specific trending hashtags
            trending = await self._get_trending_hashtags(platform)
            hashtags.extend(trending)
            
            # Add generic engagement hashtags
            generic = await self._get_generic_hashtags(platform)
            hashtags.extend(generic)
            
            # Remove duplicates and limit count
            unique_hashtags = list(set(hashtags))[:count]
            
            logger.info(f"Generated {len(unique_hashtags)} hashtags for {platform}")
            return unique_hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return []
    
    async def create_content_variations(self, base_content: str, variation_count: int = 3) -> List[str]:
        """Create variations of base content for A/B testing"""
        try:
            variations = []
            
            for i in range(variation_count):
                if i == 0:
                    # Hook variation
                    variation = await self._create_hook_variation(base_content)
                elif i == 1:
                    # Style variation
                    variation = await self._create_style_variation(base_content)
                else:
                    # CTA variation
                    variation = await self._create_cta_variation(base_content)
                
                variations.append(variation)
            
            logger.info(f"Created {len(variations)} content variations")
            return variations
            
        except Exception as e:
            logger.error(f"Error creating content variations: {str(e)}")
            return []
    
    async def analyze_content_performance(self, content: str, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content performance and provide insights"""
        try:
            analysis = {
                "content_metrics": await self._analyze_content_metrics(content),
                "engagement_analysis": await self._analyze_engagement_patterns(engagement_data),
                "performance_insights": await self._generate_performance_insights(content, engagement_data),
                "improvement_recommendations": await self._generate_improvement_recommendations(content, engagement_data)
            }
            
            logger.info("Content performance analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            return {}
    
    async def create_content_series(self, theme: str, series_length: int, content_type: ContentType) -> List[TextProject]:
        """Create a series of related content pieces"""
        try:
            series_projects = []
            
            # Generate series outline
            series_outline = await self._create_series_outline(theme, series_length, content_type)
            
            for i, topic in enumerate(series_outline):
                project = await self.create_text_project(
                    title=f"{theme} Series - Part {i+1}: {topic['title']}",
                    content_type=content_type,
                    style=WritingStyle.EDUCATIONAL,
                    tone=ToneOfVoice.FRIENDLY,
                    target_audience="general",
                    target_platforms=["instagram", "linkedin"],
                    word_count=topic['word_count']
                )
                
                if project:
                    project.metadata["series_info"] = {
                        "theme": theme,
                        "part_number": i + 1,
                        "total_parts": series_length,
                        "topic": topic
                    }
                    series_projects.append(project)
            
            logger.info(f"Created content series with {len(series_projects)} parts")
            return series_projects
            
        except Exception as e:
            logger.error(f"Error creating content series: {str(e)}")
            return []
    
    # Helper methods for content generation
    async def _create_content_outline(self, project: TextProject, requirements: ContentRequirements) -> List[str]:
        """Create content outline based on project and requirements"""
        if project.content_type == ContentType.BLOG_ARTICLE:
            return [
                "Introduction",
                "Main Point 1",
                "Main Point 2", 
                "Main Point 3",
                "Conclusion"
            ]
        elif project.content_type == ContentType.SOCIAL_MEDIA_POST:
            return [
                "Hook",
                "Main Content",
                "Call to Action"
            ]
        else:
            return ["Opening", "Body", "Closing"]
    
    async def _generate_content_section(self, section: str, project: TextProject, requirements: ContentRequirements) -> str:
        """Generate content for a specific section"""
        # Simulate content generation based on section type
        if section == "Hook":
            return f"🔥 Did you know that {requirements.topic} can change everything? Here's what you need to know..."
        elif section == "Introduction":
            return f"In today's post, we're diving deep into {requirements.topic}. This comprehensive guide will help you understand..."
        elif section == "Main Content" or section.startswith("Main Point"):
            if requirements.key_points:
                point = requirements.key_points[0] if requirements.key_points else requirements.topic
                return f"Let's explore {point}. This is crucial because it impacts your daily life in ways you might not expect..."
            return f"The key aspect of {requirements.topic} that everyone should understand is..."
        elif section == "Call to Action":
            return requirements.call_to_action or "What do you think? Share your thoughts in the comments below! 💭"
        elif section == "Conclusion":
            return f"To wrap up, {requirements.topic} is essential for anyone looking to improve their situation. Remember these key takeaways..."
        else:
            return f"Content for {section} related to {requirements.topic}..."
    
    async def _combine_content_sections(self, sections: List[str], project: TextProject) -> str:
        """Combine content sections into cohesive text"""
        if project.content_type == ContentType.SOCIAL_MEDIA_POST:
            return "\n\n".join(sections)
        elif project.content_type == ContentType.BLOG_ARTICLE:
            return "\n\n".join(sections)
        else:
            return " ".join(sections)
    
    async def _apply_style_and_tone(self, content: str, project: TextProject) -> str:
        """Apply writing style and tone to content"""
        # Simulate style and tone application
        if project.style == WritingStyle.CONVERSATIONAL:
            # Add conversational elements
            content = content.replace("you should", "you might want to")
            content = content.replace("it is important", "here's the thing")
        
        if project.tone == ToneOfVoice.ENTHUSIASTIC:
            # Add enthusiasm markers
            content = content.replace(".", "! 🎉")
            content = content.replace("good", "amazing")
        
        return content
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculate readability score"""
        # Simple readability calculation
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = words / sentences
        readability = max(0, 1 - (avg_words_per_sentence - 15) / 20)
        return min(1.0, readability)
    
    async def _calculate_seo_score(self, content: str, platform: str) -> float:
        """
Calculate SEO optimization score"""
        # Simulate SEO score calculation
        import random
        return random.uniform(0.6, 0.95)
    
    async def _predict_engagement(self, content: str, platform: str) -> float:
        """
Predict engagement potential"""
        # Simple engagement prediction based on content features
        score = 0.5
        
        # Check for engagement elements
        if "?" in content:
            score += 0.1  # Questions increase engagement
        if any(emoji in content for emoji in ["🔥", "💭", "❤️", "👇", "🎉"]):
            score += 0.15  # Emojis increase engagement
        if len(content.split()) < 50:
            score += 0.1  # Shorter content often performs better
        if "comment" in content.lower() or "share" in content.lower():
            score += 0.2  # CTA increases engagement
        
        return min(1.0, score)
    
    async def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from content"""
        # Simple keyword extraction
        words = content.lower().split()
        
        # Remove common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "a", "an"}
        
        topics = [word for word in words if len(word) > 4 and word not in common_words]
        
        # Return most frequent topics
        from collections import Counter
        topic_counts = Counter(topics)
        return [topic for topic, count in topic_counts.most_common(5)]
    
    async def _generate_topic_hashtags(self, topic: str, platform: str) -> List[str]:
        """Generate hashtags for a specific topic"""
        base_hashtags = [
            f"#{topic}",
            f"#{topic}tips",
            f"#{topic}guide",
            f"learn{topic}",
            f"{topic}life"
        ]
        return base_hashtags
    
    async def _get_trending_hashtags(self, platform: str) -> List[str]:
        """Get trending hashtags for platform"""
        trending_map = {
            "instagram": ["#instagood", "#photooftheday", "#love", "#beautiful", "#happy"],
            "twitter": ["#trending", "#viral", "#breaking", "#news", "#update"],
            "linkedin": ["#professional", "#career", "#business", "#networking", "#growth"],
            "tiktok": ["#fyp", "#foryou", "#viral", "#trending", "#tiktok"]
        }
        return trending_map.get(platform, ["#trending", "#viral"])
    
    async def _get_generic_hashtags(self, platform: str) -> List[str]:
        """Get generic engagement hashtags"""
        return ["#follow", "#like", "#comment", "#share", "#engage", "#community"]
    
    def _load_writing_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load writing guidelines for different content types"""
        return {
            "social_media_post": {
                "max_length": 280,
                "use_emojis": True,
                "include_hashtags": True,
                "call_to_action": True
            },
            "blog_article": {
                "min_length": 800,
                "use_headings": True,
                "include_keywords": True,
                "seo_optimized": True
            },
            "video_script": {
                "conversational_tone": True,
                "include_pauses": True,
                "visual_cues": True,
                "engaging_intro": True
            }
        }
    
    def _load_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific content requirements"""
        return {
            "instagram": {
                "max_caption_length": 2200,
                "max_hashtags": 30,
                "optimal_posting_times": ["11:00", "13:00", "17:00"]
            },
            "twitter": {
                "max_length": 280,
                "max_hashtags": 2,
                "optimal_posting_times": ["12:00", "18:00", "21:00"]
            },
            "linkedin": {
                "max_length": 3000,
                "professional_tone": True,
                "optimal_posting_times": ["08:00", "12:00", "17:00"]
            }
        }
    
    def _initialize_content_formulas(self) -> Dict[str, str]:
        """Initialize proven content formulas"""
        return {
            "problem_solution": "Problem + Agitation + Solution + Call to Action",
            "story_formula": "Context + Conflict + Resolution + Lesson",
            "list_format": "Number + Benefit + List Items + Summary",
            "how_to": "Goal + Steps + Tips + Conclusion",
            "comparison": "Option A vs Option B + Pros/Cons + Recommendation"
        }

# Export the agent class
__all__ = ["TextSpecialistAgent", "ContentType", "WritingStyle", "ToneOfVoice", "TextProject", "ContentRequirements", "ContentOptimization"]

logger.info("Text Specialist Agent module loaded successfully")
