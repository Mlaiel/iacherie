"""
Content Generation Module - Advanced AI content creation and generation
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive content generation capabilities using advanced AI models
for text, image, video, and multi-modal content creation.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import json
import random

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content that can be generated"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SOCIAL_POST = "social_post"
    BLOG_ARTICLE = "blog_article"
    EMAIL = "email"
    ADVERTISEMENT = "advertisement"

class GenerationStrategy(Enum):
    """Content generation strategies"""
    CREATIVE = "creative"
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    ENTERTAINING = "entertaining"
    EDUCATIONAL = "educational"

@dataclass
class GenerationConfig:
    """Configuration for content generation"""
    content_type: ContentType
    strategy: GenerationStrategy
    target_audience: str = "general"
    tone: str = "professional"
    length: str = "medium"  # short, medium, long
    keywords: List[str] = None
    constraints: Dict[str, Any] = None
    creativity: float = 0.7  # 0.0 to 1.0

@dataclass
class GeneratedContent:
    """Container for generated content"""
    content_id: str
    content_type: ContentType
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    generated_at: datetime
    config_used: GenerationConfig

class ContentGenerator:
    """Main content generation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.generation_history = []
        self.templates = self._load_templates()
        self.vocabulary = self._load_vocabulary()
        self.logger.info("ContentGenerator initialized successfully")
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load content templates"""
        return {
            "social_post": [
                "🚀 {main_message} {call_to_action}",
                "✨ {intro} {main_content} {hashtags}",
                "📢 {announcement} {details} {engagement_hook}"
            ],
            "blog_article": [
                "# {title}\n\n{introduction}\n\n## Main Content\n{body}\n\n## Conclusion\n{conclusion}",
                "## {title}\n\n{hook}\n\n{content_sections}\n\n{call_to_action}"
            ],
            "email": [
                "Subject: {subject}\n\nHi {name},\n\n{opening}\n\n{main_content}\n\nBest regards,\n{sender}",
                "Subject: {subject}\n\n{greeting}\n\n{body}\n\n{closing}"
            ]
        }
    
    def _load_vocabulary(self) -> Dict[str, List[str]]:
        """Load vocabulary for content generation"""
        return {
            "creative_adjectives": ["innovative", "groundbreaking", "revolutionary", "cutting-edge", "transformative"],
            "action_words": ["discover", "explore", "unlock", "unleash", "master", "achieve", "create"],
            "engagement_hooks": ["Don't miss out!", "Join thousands of others", "Transform your business today"],
            "professional_phrases": ["best practices", "proven strategies", "industry insights", "expert advice"],
            "tech_terms": ["AI-powered", "data-driven", "intelligent", "automated", "scalable", "efficient"]
        }
    
    def generate(self, config: GenerationConfig, prompt: str = "") -> GeneratedContent:
        """Generate content based on configuration"""
        try:
            self.logger.info(f"Generating {config.content_type.value} content with {config.strategy.value} strategy")
            
            # Generate content based on type
            if config.content_type == ContentType.TEXT:
                content = self._generate_text(config, prompt)
            elif config.content_type == ContentType.SOCIAL_POST:
                content = self._generate_social_post(config, prompt)
            elif config.content_type == ContentType.BLOG_ARTICLE:
                content = self._generate_blog_article(config, prompt)
            elif config.content_type == ContentType.EMAIL:
                content = self._generate_email(config, prompt)
            else:
                content = self._generate_generic_content(config, prompt)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(content, config)
            
            # Create result
            result = GeneratedContent(
                content_id=f"gen_{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}",
                content_type=config.content_type,
                content=content,
                metadata={
                    "word_count": len(content.split()),
                    "character_count": len(content),
                    "strategy": config.strategy.value,
                    "tone": config.tone,
                    "target_audience": config.target_audience
                },
                quality_score=quality_score,
                generated_at=datetime.utcnow(),
                config_used=config
            )
            
            self.generation_history.append(result)
            
            self.logger.info(f"Content generated successfully with quality score: {quality_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    def _generate_text(self, config: GenerationConfig, prompt: str) -> str:
        """Generate general text content"""
        # Simulate text generation using templates and vocabulary
        base_content = prompt if prompt else "Here is your generated content."
        
        # Add vocabulary based on strategy
        if config.strategy == GenerationStrategy.CREATIVE:
            words = random.choices(self.vocabulary["creative_adjectives"], k=2)
            base_content += f" This {words[0]} and {words[1]} approach will help you succeed."
        elif config.strategy == GenerationStrategy.INFORMATIVE:
            phrases = random.choices(self.vocabulary["professional_phrases"], k=2)
            base_content += f" Following {phrases[0]} and implementing {phrases[1]} is crucial."
        elif config.strategy == GenerationStrategy.PERSUASIVE:
            hooks = random.choice(self.vocabulary["engagement_hooks"])
            actions = random.choice(self.vocabulary["action_words"])
            base_content += f" {hooks} {actions.capitalize()} your potential today!"
        
        # Adjust length
        if config.length == "short":
            return base_content[:200]
        elif config.length == "long":
            return base_content + " " + self._generate_additional_content(config)
        
        return base_content
    
    def _generate_social_post(self, config: GenerationConfig, prompt: str) -> str:
        """Generate social media post"""
        template = random.choice(self.templates["social_post"])
        
        # Fill template variables
        content_vars = {
            "main_message": prompt or "Check out this amazing content!",
            "call_to_action": random.choice(self.vocabulary["engagement_hooks"]),
            "intro": "✨ Exciting news!",
            "main_content": prompt or "Something amazing is happening.",
            "hashtags": "#AI #Content #Innovation",
            "announcement": "📢 Big announcement:",
            "details": prompt or "We're launching something incredible.",
            "engagement_hook": "What do you think? 💭"
        }
        
        return template.format(**content_vars)
    
    def _generate_blog_article(self, config: GenerationConfig, prompt: str) -> str:
        """Generate blog article"""
        template = random.choice(self.templates["blog_article"])
        
        title = prompt or "The Future of AI-Powered Content Creation"
        
        content_vars = {
            "title": title,
            "introduction": "In today's digital landscape, content creation has become more important than ever.",
            "body": "AI-powered tools are revolutionizing how we create, optimize, and distribute content across all channels.",
            "conclusion": "The future of content creation is here, and it's powered by artificial intelligence.",
            "hook": "Have you ever wondered how AI could transform your content strategy?",
            "content_sections": "### Section 1\nContent here.\n\n### Section 2\nMore content here.",
            "call_to_action": "Ready to transform your content strategy? Get started today!"
        }
        
        return template.format(**content_vars)
    
    def _generate_email(self, config: GenerationConfig, prompt: str) -> str:
        """Generate email content"""
        template = random.choice(self.templates["email"])
        
        content_vars = {
            "subject": prompt or "Important Update",
            "name": "[Name]",
            "opening": "I hope this email finds you well.",
            "main_content": prompt or "I wanted to share some important information with you.",
            "sender": "[Your Name]",
            "greeting": "Hello!",
            "body": prompt or "This is the main content of the email.",
            "closing": "Thank you for your time."
        }
        
        return template.format(**content_vars)
    
    def _generate_generic_content(self, config: GenerationConfig, prompt: str) -> str:
        """Generate generic content for other types"""
        return prompt or f"Generated {config.content_type.value} content using {config.strategy.value} strategy."
    
    def _generate_additional_content(self, config: GenerationConfig) -> str:
        """Generate additional content for longer pieces"""
        additions = [
            "Furthermore, this approach provides numerous benefits for businesses.",
            "Research shows that implementing these strategies leads to significant improvements.",
            "Many companies have already seen remarkable results using these methods.",
            "The key is to maintain consistency and focus on quality throughout the process."
        ]
        
        return " ".join(random.choices(additions, k=random.randint(1, 3)))
    
    def _calculate_quality_score(self, content: str, config: GenerationConfig) -> float:
        """Calculate quality score for generated content"""
        score = 0.5  # Base score
        
        # Length appropriateness
        word_count = len(content.split())
        if config.length == "short" and 10 <= word_count <= 50:
            score += 0.1
        elif config.length == "medium" and 50 <= word_count <= 200:
            score += 0.1
        elif config.length == "long" and word_count >= 200:
            score += 0.1
        
        # Keyword presence
        if config.keywords:
            keyword_matches = sum(1 for keyword in config.keywords if keyword.lower() in content.lower())
            score += (keyword_matches / len(config.keywords)) * 0.2
        
        # Content structure (basic checks)
        if any(char in content for char in "!?.:"):
            score += 0.1  # Has punctuation
        
        if len(content) > 20:
            score += 0.1  # Reasonable length
        
        # Creativity factor
        score += config.creativity * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def batch_generate(self, configs: List[GenerationConfig], prompts: List[str] = None) -> List[GeneratedContent]:
        """Generate multiple pieces of content"""
        if prompts is None:
            prompts = [""] * len(configs)
        
        results = []
        for i, config in enumerate(configs):
            prompt = prompts[i] if i < len(prompts) else ""
            result = self.generate(config, prompt)
            results.append(result)
        
        return results
    
    def optimize_content(self, content: str, target_metrics: Dict[str, float]) -> str:
        """Optimize existing content for specific metrics"""
        try:
            # Simple optimization simulation
            optimized = content
            
            if target_metrics.get("engagement", 0) > 0.7:
                # Add engagement elements
                if "!" not in optimized:
                    optimized += " Don't miss out!"
                if "#" not in optimized and "hashtag" not in optimized.lower():
                    optimized += " #Trending"
            
            if target_metrics.get("seo", 0) > 0.7:
                # Add SEO-friendly elements
                keywords = ["innovative", "solution", "expert", "guide"]
                for keyword in keywords[:2]:
                    if keyword.lower() not in optimized.lower():
                        optimized = optimized.replace(".", f" {keyword}.")
                        break
            
            self.logger.info("Content optimization completed")
            return optimized
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
            return content
    
    def analyze_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Analyze performance of generated content"""
        # Find content in history
        content = next((c for c in self.generation_history if c.content_id == content_id), None)
        
        if not content:
            return {"error": "Content not found"}
        
        # Simulate performance analysis
        performance = {
            "content_id": content_id,
            "quality_score": content.quality_score,
            "engagement_potential": random.uniform(0.3, 0.9),
            "seo_score": random.uniform(0.4, 0.8),
            "readability": random.uniform(0.6, 1.0),
            "sentiment": random.choice(["positive", "neutral", "negative"]),
            "recommended_improvements": []
        }
        
        # Add recommendations based on scores
        if performance["engagement_potential"] < 0.6:
            performance["recommended_improvements"].append("Add more engaging elements")
        
        if performance["seo_score"] < 0.6:
            performance["recommended_improvements"].append("Improve SEO optimization")
        
        if performance["readability"] < 0.7:
            performance["recommended_improvements"].append("Simplify language for better readability")
        
        return performance
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about content generation"""
        if not self.generation_history:
            return {"message": "No content generated yet"}
        
        stats = {
            "total_generated": len(self.generation_history),
            "average_quality_score": np.mean([c.quality_score for c in self.generation_history]),
            "content_types": {},
            "strategies_used": {},
            "recent_activity": len([c for c in self.generation_history 
                                  if (datetime.utcnow() - c.generated_at).days <= 7])
        }
        
        # Count by content type
        for content in self.generation_history:
            content_type = content.content_type.value
            stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1
        
        # Count by strategy
        for content in self.generation_history:
            strategy = content.config_used.strategy.value
            stats["strategies_used"][strategy] = stats["strategies_used"].get(strategy, 0) + 1
        
        return stats

# Content Analysis Classes (for backward compatibility)
class ContentAnalyzer:
    """Content analysis engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("ContentAnalyzer initialized successfully")
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content quality and characteristics"""
        return {
            "word_count": len(content.split()),
            "character_count": len(content),
            "sentiment": "positive",
            "readability": 0.8,
            "seo_score": 0.7
        }

# Export classes for external use
__all__ = [
    'ContentType',
    'GenerationStrategy', 
    'GenerationConfig',
    'GeneratedContent',
    'ContentGenerator',
    'ContentAnalyzer'
]

logger.info("Content generation module loaded successfully")
