"""
Content Generators Module for IA Influencer Agent Platform

AI-powered content generation capabilities for creating engaging posts,
captions, descriptions, and multi-format content for influencers and creators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import random
import re
from enum import Enum

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type enumeration"""
    SOCIAL_POST = "social_post"
    CAPTION = "caption"
    DESCRIPTION = "description"
    HASHTAGS = "hashtags"
    TITLE = "title"
    BIO = "bio"
    SCRIPT = "script"
    EMAIL = "email"
    BLOG_POST = "blog_post"

class ToneType(Enum):
    """Tone type enumeration"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"

@dataclass
class GenerationRequest:
    """Content generation request"""
    content_type: ContentType
    topic: str
    tone: ToneType
    target_audience: str
    platform: str = "general"
    length: str = "medium"  # short, medium, long
    keywords: List[str] = field(default_factory=list)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    max_length: Optional[int] = None
    include_hashtags: bool = True
    include_call_to_action: bool = True

@dataclass
class GenerationResult:
    """Content generation result"""
    request_id: str
    generated_content: str
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    engagement_prediction: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ContentTemplate:
    """Content template structure"""
    
    def __init__(self, template_type: str, structure: List[str], variables: List[str]):
        self.template_type = template_type
        self.structure = structure
        self.variables = variables
        self.usage_count = 0
        self.success_rate = 0.0

class ContentGenerator(ABC):
    """Abstract base class for content generators"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.templates = {}
        self.generation_history = []
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate content based on request"""
        pass
    
    def _generate_request_id(self, request: GenerationRequest) -> str:
        """Generate unique request ID"""
        import hashlib
        content_hash = hashlib.md5(f"{request.topic}{request.content_type.value}{datetime.utcnow()}".encode()).hexdigest()
        return content_hash[:12]

class SocialPostGenerator(ContentGenerator):
    """
    Social media post generator
    
    Capabilities:
    - Platform-specific optimization
    - Engagement-driven content
    - Hashtag generation
    - Call-to-action integration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.platform_configs = self._load_platform_configs()
        self.engagement_patterns = self._load_engagement_patterns()
        self.hashtag_database = self._load_hashtag_database()
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        request_id = self._generate_request_id(request)
        
        try:
            # Get platform-specific constraints
            platform_config = self.platform_configs.get(request.platform, self.platform_configs['general'])
            
            # Generate main content
            main_content = await self._generate_main_content(request, platform_config)
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(request) if request.include_hashtags else []
            
            # Generate call-to-action
            cta = await self._generate_call_to_action(request) if request.include_call_to_action else ""
            
            # Combine content
            full_content = self._combine_content_elements(main_content, hashtags, cta, platform_config)
            
            # Generate alternatives
            alternatives = await self._generate_alternatives(request, platform_config)
            
            # Predict engagement
            engagement_prediction = await self._predict_engagement(full_content, request)
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(full_content, request)
            
            return GenerationResult(
                request_id=request_id,
                generated_content=full_content,
                alternatives=alternatives,
                metadata={
                    'platform': request.platform,
                    'content_length': len(full_content),
                    'hashtag_count': len(hashtags),
                    'has_cta': bool(cta),
                    'tone_confidence': 0.85,
                    'platform_optimization': self._assess_platform_optimization(full_content, platform_config)
                },
                quality_score=quality_score,
                engagement_prediction=engagement_prediction
            )
            
        except Exception as e:
            logger.error(f"Social post generation failed: {str(e)}")
            return GenerationResult(
                request_id=request_id,
                generated_content="",
                metadata={'error': str(e)}
            )
    
    async def _generate_main_content(self, request: GenerationRequest, platform_config: Dict[str, Any]) -> str:
        """Generate main content body"""
        # Content templates based on tone and topic
        templates = self._get_content_templates(request.tone, request.content_type)
        
        if not templates:
            return await self._generate_fallback_content(request)
        
        # Select best template
        template = self._select_best_template(templates, request)
        
        # Fill template with dynamic content
        content = await self._fill_template(template, request)
        
        # Apply tone adjustments
        content = await self._apply_tone_adjustments(content, request.tone)
        
        # Ensure platform compliance
        content = self._ensure_platform_compliance(content, platform_config)
        
        return content
    
    async def _generate_hashtags(self, request: GenerationRequest) -> List[str]:
        """Generate relevant hashtags"""
        hashtags = []
        
        # Topic-based hashtags
        topic_hashtags = self._get_topic_hashtags(request.topic)
        hashtags.extend(topic_hashtags[:5])
        
        # Niche-specific hashtags
        if request.context.get('niche'):
            niche_hashtags = self._get_niche_hashtags(request.context['niche'])
            hashtags.extend(niche_hashtags[:3])
        
        # Trending hashtags
        trending = self._get_trending_hashtags(request.platform)
        if trending:
            hashtags.extend(trending[:2])
        
        # Platform-specific hashtags
        platform_hashtags = self._get_platform_hashtags(request.platform)
        hashtags.extend(platform_hashtags[:2])
        
        # Remove duplicates and format
        unique_hashtags = list(dict.fromkeys(hashtags))
        formatted_hashtags = [f"#{tag.replace('#', '').replace(' ', '')}" for tag in unique_hashtags]
        
        # Limit based on platform
        max_hashtags = self.platform_configs.get(request.platform, {}).get('max_hashtags', 10)
        return formatted_hashtags[:max_hashtags]
    
    async def _generate_call_to_action(self, request: GenerationRequest) -> str:
        """Generate call-to-action"""
        cta_templates = {
            ToneType.PROFESSIONAL: [
                "Share your thoughts in the comments below.",
                "What's your experience with this? Let me know!",
                "Tag someone who needs to see this.",
                "Follow for more professional insights."
            ],
            ToneType.CASUAL: [
                "What do you think? Drop a comment! 💭",
                "Tag your bestie who needs this! 👥",
                "Double tap if you agree! ❤️",
                "Save this for later! 📌"
            ],
            ToneType.ENTHUSIASTIC: [
                "Let me know what you think in the comments! 🔥",
                "Tag someone who NEEDS to see this! 👇",
                "Smash that like button if you agree! ❤️",
                "Share this with your squad! 🙌"
            ],
            ToneType.EDUCATIONAL: [
                "Save this post for future reference! 📚",
                "Share this with someone who's learning! 🎓",
                "What questions do you have? Ask below! 🤔",
                "Follow for more educational content! 📖"
            ]
        }
        
        tone_ctas = cta_templates.get(request.tone, cta_templates[ToneType.CASUAL])
        return random.choice(tone_ctas)
    
    def _combine_content_elements(self, main_content: str, hashtags: List[str], cta: str, platform_config: Dict[str, Any]) -> str:
        """Combine all content elements"""
        elements = [main_content]
        
        if cta:
            elements.append(f"\n\n{cta}")
        
        if hashtags:
            hashtag_str = " ".join(hashtags)
            elements.append(f"\n\n{hashtag_str}")
        
        full_content = "".join(elements)
        
        # Ensure length compliance
        max_length = platform_config.get('max_length', 2200)
        if len(full_content) > max_length:
            # Trim hashtags first, then CTA, then main content
            if hashtags and len(full_content) > max_length:
                reduced_hashtags = hashtags[:5]
                hashtag_str = " ".join(reduced_hashtags)
                full_content = main_content + (f"\n\n{cta}" if cta else "") + f"\n\n{hashtag_str}"
            
            if len(full_content) > max_length:
                available_length = max_length - len(cta) - len(hashtag_str) - 4  # Account for newlines
                trimmed_main = main_content[:available_length] + "..."
                full_content = trimmed_main + (f"\n\n{cta}" if cta else "") + (f"\n\n{hashtag_str}" if hashtags else "")
        
        return full_content
    
    async def _generate_alternatives(self, request: GenerationRequest, platform_config: Dict[str, Any]) -> List[str]:
        """Generate alternative versions"""
        alternatives = []
        
        # Generate 3 alternative versions with different approaches
        for i in range(3):
            # Modify the request slightly for variety
            alt_request = GenerationRequest(
                content_type=request.content_type,
                topic=request.topic,
                tone=request.tone,
                target_audience=request.target_audience,
                platform=request.platform,
                length=request.length,
                keywords=request.keywords,
                brand_guidelines=request.brand_guidelines,
                context=request.context,
                include_hashtags=request.include_hashtags,
                include_call_to_action=request.include_call_to_action
            )
            
            # Use different templates or approaches
            main_content = await self._generate_main_content(alt_request, platform_config)
            hashtags = await self._generate_hashtags(alt_request) if alt_request.include_hashtags else []
            cta = await self._generate_call_to_action(alt_request) if alt_request.include_call_to_action else ""
            
            alternative = self._combine_content_elements(main_content, hashtags, cta, platform_config)
            alternatives.append(alternative)
        
        return alternatives
    
    async def _predict_engagement(self, content: str, request: GenerationRequest) -> Dict[str, float]:
        """Predict engagement metrics"""
        # Simplified engagement prediction model
        base_engagement = 0.5
        
        # Factor in content characteristics
        length_factor = self._calculate_length_factor(content, request.platform)
        hashtag_factor = self._calculate_hashtag_factor(content)
        cta_factor = self._calculate_cta_factor(content)
        tone_factor = self._calculate_tone_factor(request.tone, request.target_audience)
        
        # Platform-specific adjustments
        platform_factor = self.platform_configs.get(request.platform, {}).get('engagement_multiplier', 1.0)
        
        predicted_engagement = base_engagement * length_factor * hashtag_factor * cta_factor * tone_factor * platform_factor
        
        return {
            'overall_engagement': min(1.0, predicted_engagement),
            'likes_prediction': min(1.0, predicted_engagement * 1.2),
            'comments_prediction': min(1.0, predicted_engagement * 0.8),
            'shares_prediction': min(1.0, predicted_engagement * 0.6),
            'saves_prediction': min(1.0, predicted_engagement * 0.7)
        }
    
    async def _calculate_quality_score(self, content: str, request: GenerationRequest) -> float:
        """Calculate content quality score"""
        quality_factors = []
        
        # Content length appropriateness
        ideal_length = self.platform_configs.get(request.platform, {}).get('ideal_length', 150)
        length_score = 1.0 - abs(len(content) - ideal_length) / ideal_length
        quality_factors.append(max(0.0, min(1.0, length_score)))
        
        # Hashtag quality
        hashtag_count = len(re.findall(r'#\w+', content))
        optimal_hashtags = self.platform_configs.get(request.platform, {}).get('optimal_hashtags', 8)
        hashtag_score = 1.0 - abs(hashtag_count - optimal_hashtags) / optimal_hashtags
        quality_factors.append(max(0.0, min(1.0, hashtag_score)))
        
        # Content structure
        has_hook = self._has_engaging_hook(content)
        has_cta = self._has_call_to_action(content)
        structure_score = (0.6 if has_hook else 0.0) + (0.4 if has_cta else 0.0)
        quality_factors.append(structure_score)
        
        # Readability
        readability_score = self._calculate_readability_score(content)
        quality_factors.append(readability_score)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _load_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific configurations"""
        return {
            'instagram': {
                'max_length': 2200,
                'ideal_length': 150,
                'max_hashtags': 30,
                'optimal_hashtags': 8,
                'engagement_multiplier': 1.2,
                'supports_stories': True,
                'supports_reels': True
            },
            'twitter': {
                'max_length': 280,
                'ideal_length': 120,
                'max_hashtags': 5,
                'optimal_hashtags': 2,
                'engagement_multiplier': 1.0,
                'supports_threads': True
            },
            'facebook': {
                'max_length': 63206,
                'ideal_length': 200,
                'max_hashtags': 10,
                'optimal_hashtags': 3,
                'engagement_multiplier': 0.8,
                'supports_stories': True
            },
            'linkedin': {
                'max_length': 3000,
                'ideal_length': 300,
                'max_hashtags': 10,
                'optimal_hashtags': 5,
                'engagement_multiplier': 1.1,
                'professional_tone_preferred': True
            },
            'tiktok': {
                'max_length': 2200,
                'ideal_length': 100,
                'max_hashtags': 20,
                'optimal_hashtags': 6,
                'engagement_multiplier': 1.5,
                'trending_focus': True
            },
            'youtube': {
                'max_length': 5000,
                'ideal_length': 500,
                'max_hashtags': 15,
                'optimal_hashtags': 8,
                'engagement_multiplier': 1.0,
                'supports_timestamps': True
            },
            'general': {
                'max_length': 2200,
                'ideal_length': 150,
                'max_hashtags': 10,
                'optimal_hashtags': 5,
                'engagement_multiplier': 1.0
            }
        }
    
    def _load_engagement_patterns(self) -> Dict[str, List[str]]:
        """Load engagement-driving patterns"""
        return {
            'hooks': [
                "Did you know that...",
                "Here's what nobody tells you about...",
                "The secret to... is...",
                "Stop doing this if you want...",
                "3 things that changed my...",
                "Why everyone is talking about...",
                "The truth about...",
                "What I wish I knew about..."
            ],
            'questions': [
                "What's your experience with this?",
                "Which one do you prefer?",
                "Have you tried this before?",
                "What would you add to this list?",
                "Do you agree with this?",
                "What's your biggest challenge with...?",
                "How do you handle...?",
                "What's your favorite...?"
            ],
            'emotional_triggers': [
                "incredible", "amazing", "shocking", "unbelievable",
                "life-changing", "game-changer", "mind-blowing",
                "surprising", "inspiring", "powerful"
            ]
        }
    
    def _load_hashtag_database(self) -> Dict[str, List[str]]:
        """Load hashtag database by topic/niche"""
        return {
            'lifestyle': [
                'lifestyle', 'dailylife', 'goodvibes', 'positivity',
                'selfcare', 'mindfulness', 'wellness', 'balance'
            ],
            'fashion': [
                'fashion', 'style', 'ootd', 'fashionista',
                'trendy', 'streetstyle', 'outfit', 'stylish'
            ],
            'beauty': [
                'beauty', 'makeup', 'skincare', 'beautytips',
                'glam', 'cosmetics', 'selfcare', 'beautycare'
            ],
            'fitness': [
                'fitness', 'workout', 'gym', 'health',
                'fitlife', 'training', 'exercise', 'wellness'
            ],
            'food': [
                'food', 'foodie', 'recipe', 'cooking',
                'delicious', 'yummy', 'foodlover', 'chef'
            ],
            'travel': [
                'travel', 'wanderlust', 'explore', 'adventure',
                'vacation', 'trip', 'discover', 'journey'
            ],
            'technology': [
                'tech', 'technology', 'innovation', 'digital',
                'gadgets', 'AI', 'future', 'startup'
            ],
            'business': [
                'business', 'entrepreneur', 'success', 'leadership',
                'motivation', 'growth', 'hustle', 'mindset'
            ]
        }
    
    def _get_content_templates(self, tone: ToneType, content_type: ContentType) -> List[ContentTemplate]:
        """Get content templates based on tone and type"""
        templates = []
        
        if tone == ToneType.PROFESSIONAL:
            templates.extend([
                ContentTemplate(
                    "professional_insight",
                    [
                        "In my experience with {topic}, I've learned that {insight}.",
                        "Here are {number} key takeaways that have shaped my understanding:",
                        "{list_items}",
                        "What has your experience been like?"
                    ],
                    ["topic", "insight", "number", "list_items"]
                ),
                ContentTemplate(
                    "professional_tips",
                    [
                        "{number} essential tips for {topic}:",
                        "{list_items}",
                        "Which tip resonates most with you?"
                    ],
                    ["number", "topic", "list_items"]
                )
            ])
        
        elif tone == ToneType.CASUAL:
            templates.extend([
                ContentTemplate(
                    "casual_share",
                    [
                        "Hey everyone! 👋",
                        "Just wanted to share something cool about {topic}...",
                        "{main_content}",
                        "Anyone else into this? Let me know! 😊"
                    ],
                    ["topic", "main_content"]
                ),
                ContentTemplate(
                    "casual_story",
                    [
                        "So, funny story about {topic}... 😄",
                        "{story_content}",
                        "Have you ever had something like this happen? 🤔"
                    ],
                    ["topic", "story_content"]
                )
            ])
        
        elif tone == ToneType.INSPIRATIONAL:
            templates.extend([
                ContentTemplate(
                    "motivational_quote",
                    [
                        "✨ {quote} ✨",
                        "",
                        "This really resonates with me when it comes to {topic}.",
                        "{personal_reflection}",
                        "What motivates you today? 💪"
                    ],
                    ["quote", "topic", "personal_reflection"]
                ),
                ContentTemplate(
                    "transformation_story",
                    [
                        "A year ago, I {past_situation}.",
                        "Today, I {current_situation}.",
                        "",
                        "The journey wasn't easy, but {lesson_learned}.",
                        "What's one thing you're working on transforming? 🌟"
                    ],
                    ["past_situation", "current_situation", "lesson_learned"]
                )
            ])
        
        return templates
    
    def _select_best_template(self, templates: List[ContentTemplate], request: GenerationRequest) -> ContentTemplate:
        """Select the best template for the request"""
        # Simple selection based on usage success rate and variety
        if not templates:
            return None
        
        # Prefer templates with higher success rates but also consider variety
        scored_templates = []
        for template in templates:
            variety_bonus = 1.0 if template.usage_count < 5 else 0.8
            score = template.success_rate * variety_bonus
            scored_templates.append((score, template))
        
        scored_templates.sort(key=lambda x: x[0], reverse=True)
        selected_template = scored_templates[0][1]
        selected_template.usage_count += 1
        
        return selected_template
    
    async def _fill_template(self, template: ContentTemplate, request: GenerationRequest) -> str:
        """Fill template with dynamic content"""
        if not template:
            return await self._generate_fallback_content(request)
        
        # Generate content for template variables
        variable_content = {}
        
        for variable in template.variables:
            if variable == "topic":
                variable_content[variable] = request.topic
            elif variable == "number":
                variable_content[variable] = str(random.randint(3, 7))
            elif variable == "insight":
                variable_content[variable] = self._generate_insight(request.topic)
            elif variable == "list_items":
                variable_content[variable] = self._generate_list_items(request.topic)
            elif variable == "main_content":
                variable_content[variable] = self._generate_main_narrative(request.topic)
            elif variable == "story_content":
                variable_content[variable] = self._generate_story_content(request.topic)
            elif variable == "quote":
                variable_content[variable] = self._generate_inspirational_quote(request.topic)
            elif variable == "personal_reflection":
                variable_content[variable] = self._generate_personal_reflection(request.topic)
            elif variable == "past_situation":
                variable_content[variable] = self._generate_past_situation(request.topic)
            elif variable == "current_situation":
                variable_content[variable] = self._generate_current_situation(request.topic)
            elif variable == "lesson_learned":
                variable_content[variable] = self._generate_lesson(request.topic)
            else:
                variable_content[variable] = f"[{variable}]"  # Placeholder
        
        # Fill template
        content_parts = []
        for part in template.structure:
            filled_part = part.format(**variable_content)
            content_parts.append(filled_part)
        
        return "\n".join(content_parts)
    
    async def _generate_fallback_content(self, request: GenerationRequest) -> str:
        """Generate fallback content when templates fail"""
        fallback_patterns = {
            ToneType.PROFESSIONAL: f"Today I want to share some thoughts on {request.topic}. In my experience, this is an area that requires careful consideration and strategic thinking.",
            ToneType.CASUAL: f"Hey everyone! 👋 Let's talk about {request.topic} for a minute. I've been thinking about this lately and wanted to get your thoughts!",
            ToneType.ENTHUSIASTIC: f"I'm SO excited to talk about {request.topic} today! 🔥 This is something I'm really passionate about and I know you're going to love it too!",
            ToneType.INSPIRATIONAL: f"✨ Sometimes the most powerful transformations come from understanding {request.topic} differently. Let me share what I've learned on this journey.",
            ToneType.EDUCATIONAL: f"Let's dive into {request.topic} today! 📚 I'll break down the key concepts you need to know and share some practical insights."
        }
        
        return fallback_patterns.get(request.tone, f"Let's explore {request.topic} together!")
    
    def _generate_insight(self, topic: str) -> str:
        """Generate an insight about the topic"""
        insights = [
            f"the key to success with {topic} is consistency and patience",
            f"most people overlook the fundamentals when it comes to {topic}",
            f"there's a common misconception about {topic} that I want to address",
            f"the biggest game-changer for me in {topic} was changing my mindset",
            f"quality always trumps quantity when dealing with {topic}"
        ]
        return random.choice(insights)
    
    def _generate_list_items(self, topic: str) -> str:
        """Generate list items for the topic"""
        items = [
            f"• Start with the basics - master the fundamentals of {topic}",
            f"• Stay consistent - small daily actions in {topic} compound over time",
            f"• Learn from others - find mentors and communities focused on {topic}",
            f"• Track your progress - measure what matters in your {topic} journey",
            f"• Be patient - real results in {topic} take time to develop"
        ]
        return "\n".join(random.sample(items, min(3, len(items))))
    
    def _generate_main_narrative(self, topic: str) -> str:
        """Generate main narrative content"""
        narratives = [
            f"I've been diving deep into {topic} lately, and it's been such an eye-opening experience. The more I learn, the more I realize how much there is to discover.",
            f"You know what's fascinating about {topic}? It's how it connects to so many other aspects of life. I never expected to find these connections.",
            f"I used to think {topic} was straightforward, but I've learned it's much more nuanced than I initially thought. Here's what changed my perspective."
        ]
        return random.choice(narratives)
    
    def _generate_story_content(self, topic: str) -> str:
        """Generate story content"""
        stories = [
            f"I was working on {topic} yesterday when something unexpected happened that completely changed my approach.",
            f"Last week, I had a conversation about {topic} that really made me think differently about the whole thing.",
            f"So I was researching {topic} and stumbled upon this insight that I just had to share with you all."
        ]
        return random.choice(stories)
    
    def _generate_inspirational_quote(self, topic: str) -> str:
        """Generate inspirational quote"""
        quotes = [
            f"Success in {topic} isn't about perfection, it's about progress.",
            f"Every expert in {topic} was once a beginner who never gave up.",
            f"The journey of mastering {topic} teaches us more about ourselves than we ever imagined.",
            f"In {topic}, as in life, the small consistent steps create the biggest transformations."
        ]
        return random.choice(quotes)
    
    def _generate_personal_reflection(self, topic: str) -> str:
        """Generate personal reflection"""
        reflections = [
            f"My journey with {topic} has taught me so much about persistence and growth.",
            f"Looking back on my {topic} experience, I'm grateful for every challenge that made me stronger.",
            f"The lessons I've learned from {topic} have shaped not just my skills, but my entire mindset."
        ]
        return random.choice(reflections)
    
    def _generate_past_situation(self, topic: str) -> str:
        """Generate past situation for transformation story"""
        situations = [
            f"struggled with understanding the basics of {topic}",
            f"felt overwhelmed by all the information about {topic}",
            f"didn't know where to start with {topic}",
            f"was intimidated by the complexity of {topic}"
        ]
        return random.choice(situations)
    
    def _generate_current_situation(self, topic: str) -> str:
        """Generate current situation for transformation story"""
        situations = [
            f"I feel confident and knowledgeable about {topic}",
            f"I'm helping others navigate their {topic} journey",
            f"I've developed a systematic approach to {topic}",
            f"I see {topic} as an exciting opportunity for growth"
        ]
        return random.choice(situations)
    
    def _generate_lesson(self, topic: str) -> str:
        """Generate lesson learned"""
        lessons = [
            f"consistency in {topic} matters more than intensity",
            f"the key to {topic} is starting before you feel ready",
            f"progress in {topic} is rarely linear, and that's okay",
            f"community and support make all the difference in {topic}"
        ]
        return random.choice(lessons)
    
    async def _apply_tone_adjustments(self, content: str, tone: ToneType) -> str:
        """Apply tone-specific adjustments to content"""
        if tone == ToneType.ENTHUSIASTIC:
            # Add more exclamation marks and emojis
            content = re.sub(r'\.', '!', content, count=2)
            if '🔥' not in content and '✨' not in content:
                content += " 🔥"
        
        elif tone == ToneType.PROFESSIONAL:
            # Remove excessive punctuation and casual language
            content = re.sub(r'!+', '.', content)
            content = re.sub(r'emoji:\w+:', '', content)
        
        elif tone == ToneType.CASUAL:
            # Add casual connectors and friendly language
            if not any(emoji in content for emoji in ['😊', '👋', '🤔']):
                content += " 😊"
        
        return content
    
    def _ensure_platform_compliance(self, content: str, platform_config: Dict[str, Any]) -> str:
        """Ensure content complies with platform requirements"""
        max_length = platform_config.get('max_length', 2200)
        
        if len(content) > max_length:
            # Trim content while preserving structure
            content = content[:max_length-3] + "..."
        
        # Platform-specific adjustments
        if platform_config.get('professional_tone_preferred'):
            # Remove excessive emojis for professional platforms
            emoji_count = len(re.findall(r'[😀-🿿]', content))
            if emoji_count > 3:
                content = re.sub(r'[😀-🿿]', '', content, count=emoji_count-2)
        
        return content
    
    def _get_topic_hashtags(self, topic: str) -> List[str]:
        """Get hashtags related to the topic"""
        topic_lower = topic.lower()
        
        # Direct topic hashtags
        hashtags = [topic_lower.replace(' ', '')]
        
        # Related hashtags from database
        for category, tags in self.hashtag_database.items():
            if any(keyword in topic_lower for keyword in [category]):
                hashtags.extend(tags[:3])
        
        return hashtags
    
    def _get_niche_hashtags(self, niche: str) -> List[str]:
        """Get niche-specific hashtags"""
        return self.hashtag_database.get(niche.lower(), [])
    
    def _get_trending_hashtags(self, platform: str) -> List[str]:
        """Get trending hashtags for platform"""
        # Simplified trending hashtags - in production, fetch from APIs
        trending_by_platform = {
            'instagram': ['trending', 'viral', 'explore'],
            'tiktok': ['fyp', 'foryou', 'trending'],
            'twitter': ['trending', 'viral', 'discussion'],
            'linkedin': ['professional', 'networking', 'growth']
        }
        return trending_by_platform.get(platform, ['trending'])
    
    def _get_platform_hashtags(self, platform: str) -> List[str]:
        """Get platform-specific hashtags"""
        platform_hashtags = {
            'instagram': ['insta', 'instagood', 'instadaily'],
            'tiktok': ['tiktok', 'tiktokviral'],
            'linkedin': ['linkedin', 'professional'],
            'youtube': ['youtube', 'youtuber']
        }
        return platform_hashtags.get(platform, [])
    
    def _calculate_length_factor(self, content: str, platform: str) -> float:
        """Calculate engagement factor based on content length"""
        ideal_length = self.platform_configs.get(platform, {}).get('ideal_length', 150)
        current_length = len(content)
        
        # Optimal engagement around ideal length
        if current_length <= ideal_length:
            return current_length / ideal_length
        else:
            # Diminishing returns for longer content
            excess_ratio = (current_length - ideal_length) / ideal_length
            return max(0.5, 1.0 - excess_ratio * 0.3)
    
    def _calculate_hashtag_factor(self, content: str) -> float:
        """Calculate engagement factor based on hashtag usage"""
        hashtag_count = len(re.findall(r'#\w+', content))
        
        if hashtag_count == 0:
            return 0.7
        elif hashtag_count <= 5:
            return 1.0
        elif hashtag_count <= 10:
            return 0.9
        else:
            return 0.8  # Too many hashtags can hurt engagement
    
    def _calculate_cta_factor(self, content: str) -> float:
        """Calculate engagement factor based on call-to-action presence"""
        cta_indicators = [
            'comment', 'share', 'like', 'follow', 'tag',
            'thoughts', 'opinion', 'experience', 'think'
        ]
        
        content_lower = content.lower()
        has_cta = any(indicator in content_lower for indicator in cta_indicators)
        
        return 1.2 if has_cta else 0.8
    
    def _calculate_tone_factor(self, tone: ToneType, target_audience: str) -> float:
        """Calculate engagement factor based on tone-audience fit"""
        tone_audience_fit = {
            (ToneType.PROFESSIONAL, 'business'): 1.2,
            (ToneType.PROFESSIONAL, 'corporate'): 1.3,
            (ToneType.CASUAL, 'young_adults'): 1.2,
            (ToneType.CASUAL, 'general'): 1.1,
            (ToneType.ENTHUSIASTIC, 'young_adults'): 1.3,
            (ToneType.INSPIRATIONAL, 'self_improvement'): 1.2,
            (ToneType.EDUCATIONAL, 'students'): 1.2
        }
        
        return tone_audience_fit.get((tone, target_audience), 1.0)
    
    def _assess_platform_optimization(self, content: str, platform_config: Dict[str, Any]) -> Dict[str, float]:
        """Assess how well content is optimized for the platform"""
        optimization_scores = {}
        
        # Length optimization
        ideal_length = platform_config.get('ideal_length', 150)
        length_diff = abs(len(content) - ideal_length) / ideal_length
        optimization_scores['length'] = max(0.0, 1.0 - length_diff)
        
        # Hashtag optimization
        hashtag_count = len(re.findall(r'#\w+', content))
        optimal_hashtags = platform_config.get('optimal_hashtags', 5)
        hashtag_diff = abs(hashtag_count - optimal_hashtags) / optimal_hashtags
        optimization_scores['hashtags'] = max(0.0, 1.0 - hashtag_diff)
        
        # Format optimization
        has_structure = bool(re.search(r'[•\-\d+\.]\s', content))  # Lists or numbered points
        optimization_scores['structure'] = 1.0 if has_structure else 0.7
        
        # Overall optimization
        optimization_scores['overall'] = sum(optimization_scores.values()) / len(optimization_scores)
        
        return optimization_scores
    
    def _has_engaging_hook(self, content: str) -> bool:
        """Check if content has an engaging hook"""
        hooks = self.engagement_patterns.get('hooks', [])
        content_start = content[:100].lower()
        
        return any(hook.lower()[:20] in content_start for hook in hooks)
    
    def _has_call_to_action(self, content: str) -> bool:
        """Check if content has a call to action"""
        cta_indicators = [
            'comment', 'share', 'like', 'follow', 'tag',
            'thoughts', 'opinion', 'experience', 'think',
            'let me know', 'what do you', 'tell me'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in cta_indicators)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score"""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Optimal sentence length for social media: 15-20 words
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        else:
            return 0.6

# Utility functions
async def generate_social_post(topic: str, platform: str = "instagram", tone: str = "casual") -> str:
    """Quick social post generation"""
    generator = SocialPostGenerator()
    
    request = GenerationRequest(
        content_type=ContentType.SOCIAL_POST,
        topic=topic,
        tone=ToneType(tone),
        target_audience="general",
        platform=platform
    )
    
    result = await generator.generate(request)
    return result.generated_content

async def generate_hashtags(topic: str, count: int = 10) -> List[str]:
    """Quick hashtag generation"""
    generator = SocialPostGenerator()
    
    request = GenerationRequest(
        content_type=ContentType.HASHTAGS,
        topic=topic,
        tone=ToneType.CASUAL,
        target_audience="general",
        include_hashtags=True,
        include_call_to_action=False
    )
    
    hashtags = await generator._generate_hashtags(request)
    return hashtags[:count]

# Content generation pipeline
class ContentGenerationPipeline:
    """Pipeline for comprehensive content generation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.generators = {
            'social_post': SocialPostGenerator(config)
        }
        self.generation_stats = {
            'total_generated': 0,
            'avg_quality_score': 0.0,
            'success_rate': 0.0
        }
    
    async def generate_multi_format_content(self, topic: str, platforms: List[str]) -> Dict[str, GenerationResult]:
        """Generate content optimized for multiple platforms"""
        results = {}
        
        base_request = GenerationRequest(
            content_type=ContentType.SOCIAL_POST,
            topic=topic,
            tone=ToneType.CASUAL,
            target_audience="general"
        )
        
        tasks = []
        for platform in platforms:
            platform_request = GenerationRequest(
                content_type=base_request.content_type,
                topic=base_request.topic,
                tone=base_request.tone,
                target_audience=base_request.target_audience,
                platform=platform,
                keywords=base_request.keywords,
                brand_guidelines=base_request.brand_guidelines,
                context=base_request.context,
                include_hashtags=base_request.include_hashtags,
                include_call_to_action=base_request.include_call_to_action
            )
            
            tasks.append((platform, self.generators['social_post'].generate(platform_request)))
        
        # Generate content for all platforms in parallel
        generation_results = await asyncio.gather(
            *[task[1] for task in tasks],
            return_exceptions=True
        )
        
        # Compile results
        for i, (platform, _) in enumerate(tasks):
            result = generation_results[i]
            if isinstance(result, Exception):
                logger.error(f"Generation failed for {platform}: {str(result)}")
                results[platform] = GenerationResult(
                    request_id="error",
                    generated_content="",
                    metadata={'error': str(result)}
                )
            else:
                results[platform] = result
        
        # Update stats
        self._update_generation_stats(results)
        
        return results
    
    def _update_generation_stats(self, results: Dict[str, GenerationResult]):
        """Update generation statistics"""
        successful_results = [r for r in results.values() if r.generated_content and 'error' not in r.metadata]
        
        if successful_results:
            self.generation_stats['total_generated'] += len(successful_results)
            
            # Update average quality score
            current_avg = self.generation_stats['avg_quality_score']
            total_generated = self.generation_stats['total_generated']
            
            new_scores = [r.quality_score for r in successful_results]
            avg_new_score = sum(new_scores) / len(new_scores)
            
            # Calculate rolling average
            if total_generated > len(successful_results):
                prev_total = total_generated - len(successful_results)
                self.generation_stats['avg_quality_score'] = (
                    (current_avg * prev_total + avg_new_score * len(successful_results)) / total_generated
                )
            else:
                self.generation_stats['avg_quality_score'] = avg_new_score
        
        # Update success rate
        total_attempts = len(results)
        successful_attempts = len(successful_results)
        self.generation_stats['success_rate'] = successful_attempts / total_attempts if total_attempts > 0 else 0.0
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.generation_stats.copy()
