"""
Consolidated Content AI Agents - IA Influencer Platform
=======================================================

This module consolidates all content-related AI agents:
- Content Optimizer Agent
- Hashtag Generator Agent  
- Caption Writer Agent
- Story Teller Agent
- Reply Generator Agent
- Viral Predictor Agent
- Content Scheduler Agent
- Additional content creation agents

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import random

logger = logging.getLogger(__name__)

# ============================================================================
# CORE ENUMS AND DATA STRUCTURES
# ============================================================================

class ContentType(Enum):
    """Types de contenu supportés"""
    TEXT = "text"
    IMAGE = "image"  
    VIDEO = "video"
    AUDIO = "audio"
    STORY = "story"
    CAPTION = "caption"
    HASHTAG_SET = "hashtag_set"
    REPLY = "reply"
    POST = "post"
    ARTICLE = "article"
    SCRIPT = "script"

class Platform(Enum):
    """Plateformes sociales supportées"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"

class ContentStyle(Enum):
    """Styles de contenu"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    HUMOROUS = "humorous"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    STORYTELLING = "storytelling"
    VIRAL = "viral"
    TRENDY = "trendy"

class ViralPotential(Enum):
    """Niveaux de potentiel viral"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXPLOSIVE = "explosive"

@dataclass
class ContentRequest:
    """Structure de requête pour création de contenu"""
    content_type: ContentType
    platform: Platform
    style: ContentStyle
    target_audience: str
    topic: str
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentResult:
    """Résultat de génération de contenu"""
    request_id: str
    content_type: ContentType
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    viral_potential: ViralPotential
    engagement_prediction: float
    hashtags: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ScheduleRequest:
    """Requête de programmation de contenu"""
    content: str
    platform: Platform
    scheduled_time: datetime
    timezone_str: str = "UTC"
    repeat_interval: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# CONTENT OPTIMIZER AGENT
# ============================================================================

class ContentOptimizer:
    """Agent d'optimisation de contenu"""
    
    def __init__(self):
        self.optimization_rules = {
            Platform.INSTAGRAM: {
                "max_caption_length": 2200,
                "optimal_hashtags": 11,
                "max_hashtags": 30,
                "engagement_keywords": ["love", "amazing", "beautiful", "inspiration"],
                "call_to_action": ["double tap", "comment below", "tag a friend", "save this"]
            },
            Platform.TIKTOK: {
                "max_caption_length": 150,
                "optimal_hashtags": 5,
                "trending_sounds": True,
                "engagement_keywords": ["viral", "trending", "fyp", "challenge"],
                "call_to_action": ["follow for more", "comment", "duet this", "share"]
            },
            Platform.YOUTUBE: {
                "max_title_length": 100,
                "max_description_length": 5000,
                "optimal_tags": 10,
                "engagement_keywords": ["subscribe", "notification", "exclusive"],
                "call_to_action": ["subscribe", "like", "comment", "share"]
            },
            Platform.TWITTER: {
                "max_length": 280,
                "optimal_hashtags": 2,
                "trending_topics": True,
                "engagement_keywords": ["thread", "breaking", "opinion"],
                "call_to_action": ["retweet", "reply", "quote tweet", "follow"]
            }
        }
    
    async def optimize_content(self, content: str, platform: Platform, target_metrics: List[str] = None) -> Dict[str, Any]:
        """Optimise le contenu pour une plateforme spécifique"""
        try:
            rules = self.optimization_rules.get(platform, {})
            optimized_content = content
            changes = []
            
            # Optimisation de la longueur
            max_length = rules.get("max_caption_length", rules.get("max_length", 1000))
            if len(content) > max_length:
                optimized_content = content[:max_length-3] + "..."
                changes.append(f"Tronqué à {max_length} caractères")
            
            # Ajout de mots-clés d'engagement
            engagement_keywords = rules.get("engagement_keywords", [])
            if engagement_keywords and not any(kw in content.lower() for kw in engagement_keywords):
                keyword = random.choice(engagement_keywords)
                optimized_content = f"{optimized_content} #{keyword}"
                changes.append(f"Ajouté mot-clé: {keyword}")
            
            # Ajout d'appel à l'action
            cta_options = rules.get("call_to_action", [])
            if cta_options and not any(cta in content.lower() for cta in cta_options):
                cta = random.choice(cta_options)
                optimized_content = f"{optimized_content}\n\n{cta.title()}!"
                changes.append(f"Ajouté CTA: {cta}")
            
            # Calcul du score d'optimisation
            optimization_score = self._calculate_optimization_score(optimized_content, platform)
            
            return {
                "original_content": content,
                "optimized_content": optimized_content,
                "changes": changes,
                "optimization_score": optimization_score,
                "platform": platform.value,
                "predicted_improvement": f"{min(30, len(changes) * 8)}% engagement increase"
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation contenu: {e}")
            return {"error": str(e)}
    
    def _calculate_optimization_score(self, content: str, platform: Platform) -> float:
        """Calcule le score d'optimisation"""
        score = 0.5  # Score de base
        
        # Vérification de la longueur
        rules = self.optimization_rules.get(platform, {})
        max_length = rules.get("max_caption_length", rules.get("max_length", 1000))
        if len(content) <= max_length:
            score += 0.2
        
        # Présence de mots-clés d'engagement
        engagement_keywords = rules.get("engagement_keywords", [])
        if any(kw in content.lower() for kw in engagement_keywords):
            score += 0.15
        
        # Présence d'appel à l'action
        cta_options = rules.get("call_to_action", [])
        if any(cta in content.lower() for cta in cta_options):
            score += 0.15
        
        return min(1.0, score)

# ============================================================================
# HASHTAG GENERATOR AGENT
# ============================================================================

class HashtagGenerator:
    """Agent de génération de hashtags"""
    
    def __init__(self):
        self.hashtag_database = {
            "general": ["content", "creative", "inspiration", "motivation", "life"],
            "fashion": ["style", "outfit", "fashion", "ootd", "trendy", "chic"],
            "fitness": ["fitness", "workout", "healthy", "gym", "strong", "fitlife"],
            "food": ["food", "foodie", "delicious", "recipe", "yummy", "chef"],
            "travel": ["travel", "wanderlust", "adventure", "explore", "vacation"],
            "tech": ["technology", "innovation", "digital", "future", "ai", "startup"],
            "art": ["art", "artist", "creative", "design", "beautiful", "artistic"],
            "music": ["music", "musician", "song", "artist", "sound", "melody"],
            "business": ["business", "entrepreneur", "success", "growth", "leadership"]
        }
        
        self.trending_hashtags = {
            Platform.INSTAGRAM: ["reels", "viral", "trending", "explore", "fyp"],
            Platform.TIKTOK: ["fyp", "viral", "trending", "foryou", "tiktokmademebuyit"],
            Platform.YOUTUBE: ["youtube", "subscribe", "viral", "trending", "shorts"],
            Platform.TWITTER: ["trending", "viral", "breaking", "news", "thread"]
        }
    
    async def generate_hashtags(self, content: str, platform: Platform, category: str = "general", count: int = 10) -> List[str]:
        """Génère des hashtags optimisés pour le contenu"""
        try:
            hashtags = []
            
            # Hashtags de catégorie
            category_tags = self.hashtag_database.get(category, self.hashtag_database["general"])
            hashtags.extend(random.sample(category_tags, min(4, len(category_tags))))
            
            # Hashtags trending par plateforme
            platform_trending = self.trending_hashtags.get(platform, [])
            hashtags.extend(random.sample(platform_trending, min(2, len(platform_trending))))
            
            # Hashtags extraits du contenu
            content_hashtags = self._extract_hashtags_from_content(content)
            hashtags.extend(content_hashtags[:2])
            
            # Hashtags génériques populaires
            generic_tags = ["instagood", "photooftheday", "love", "beautiful", "amazing"]
            hashtags.extend(random.sample(generic_tags, min(2, len(generic_tags))))
            
            # Nettoyer et formater
            formatted_hashtags = []
            for tag in hashtags:
                if tag not in formatted_hashtags:
                    formatted_hashtags.append(tag.lower().replace(" ", ""))
            
            return formatted_hashtags[:count]
            
        except Exception as e:
            logger.error(f"Erreur génération hashtags: {e}")
            return ["content", "creative", "ai"]
    
    def _extract_hashtags_from_content(self, content: str) -> List[str]:
        """Extrait des hashtags potentiels du contenu"""
        words = re.findall(r'\b\w+\b', content.lower())
        potential_tags = []
        
        for word in words:
            if len(word) > 3 and word.isalpha():
                potential_tags.append(word)
        
        return potential_tags[:3]
    
    async def analyze_hashtag_performance(self, hashtags: List[str], platform: Platform) -> Dict[str, Any]:
        """Analyse les performances potentielles des hashtags"""
        try:
            performance_data = {}
            
            for hashtag in hashtags:
                # Simulation d'analyse de performance
                engagement_score = random.uniform(0.3, 0.9)
                reach_score = random.uniform(0.2, 0.8)
                competition_level = random.choice(["low", "medium", "high"])
                
                performance_data[hashtag] = {
                    "engagement_score": engagement_score,
                    "reach_score": reach_score,
                    "competition_level": competition_level,
                    "recommendation": "high" if engagement_score > 0.7 else "medium" if engagement_score > 0.5 else "low"
                }
            
            return {
                "hashtag_analysis": performance_data,
                "overall_score": sum(data["engagement_score"] for data in performance_data.values()) / len(performance_data),
                "best_hashtags": [tag for tag, data in performance_data.items() if data["engagement_score"] > 0.7]
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse hashtags: {e}")
            return {"error": str(e)}

# ============================================================================
# CAPTION WRITER AGENT
# ============================================================================

class CaptionWriter:
    """Agent de rédaction de légendes"""
    
    def __init__(self):
        self.caption_templates = {
            ContentStyle.CASUAL: [
                "Just {topic}... what do you think? 💭",
                "Here's a little {topic} for your day ✨",
                "Sharing some thoughts on {topic} 🤔"
            ],
            ContentStyle.PROFESSIONAL: [
                "Insights on {topic}: {content}",
                "Professional perspective on {topic}:",
                "Industry analysis: {topic}"
            ],
            ContentStyle.HUMOROUS: [
                "When {topic} hits different 😂",
                "Me trying to understand {topic} be like...",
                "Plot twist: {topic} 🤯"
            ],
            ContentStyle.EDUCATIONAL: [
                "Did you know? {topic} 📚",
                "Let's learn about {topic} together 🎓",
                "Educational thread: {topic} 🧵"
            ],
            ContentStyle.STORYTELLING: [
                "Once upon a time, {topic}...",
                "Here's my story about {topic}:",
                "Let me tell you about {topic}..."
            ]
        }
    
    async def generate_caption(self, topic: str, style: ContentStyle, platform: Platform, length: str = "medium") -> str:
        """Génère une légende optimisée"""
        try:
            templates = self.caption_templates.get(style, self.caption_templates[ContentStyle.CASUAL])
            base_template = random.choice(templates)
            
            # Génération du contenu principal
            if style == ContentStyle.EDUCATIONAL:
                content = await self._generate_educational_content(topic)
            elif style == ContentStyle.STORYTELLING:
                content = await self._generate_story_content(topic)
            elif style == ContentStyle.HUMOROUS:
                content = await self._generate_humorous_content(topic)
            else:
                content = await self._generate_general_content(topic)
            
            # Formatage selon le template
            caption = base_template.format(topic=topic, content=content)
            
            # Adaptation selon la plateforme
            caption = await self._adapt_for_platform(caption, platform)
            
            # Ajustement de la longueur
            if length == "short":
                caption = caption[:100]
            elif length == "long":
                caption = await self._expand_caption(caption, topic)
            
            return caption
            
        except Exception as e:
            logger.error(f"Erreur génération caption: {e}")
            return f"Amazing {topic} content! ✨"
    
    async def _generate_educational_content(self, topic: str) -> str:
        """Génère du contenu éducatif"""
        educational_content = [
            f"{topic} is more complex than most people think. Here are the key points you should know:",
            f"Breaking down {topic} into simple terms that everyone can understand.",
            f"The science behind {topic} might surprise you. Let me explain:"
        ]
        return random.choice(educational_content)
    
    async def _generate_story_content(self, topic: str) -> str:
        """Génère du contenu narratif"""
        story_elements = [
            f"I never expected {topic} to change my perspective so completely.",
            f"My journey with {topic} started unexpectedly, but here's what I learned:",
            f"There's something magical about {topic} that I need to share with you."
        ]
        return random.choice(story_elements)
    
    async def _generate_humorous_content(self, topic: str) -> str:
        """Génère du contenu humoristique"""
        humorous_content = [
            f"Me: I understand {topic}\nAlso me: *completely confused* 😅",
            f"Explaining {topic} to someone: It's complicated...\nActually me: *has no idea*",
            f"Plot twist: {topic} is actually way more interesting than I thought! 🎭"
        ]
        return random.choice(humorous_content)
    
    async def _generate_general_content(self, topic: str) -> str:
        """Génère du contenu général"""
        general_content = [
            f"Exploring the fascinating world of {topic} and what it means for us.",
            f"Sharing my thoughts and experiences with {topic}.",
            f"Here's why {topic} matters more than you might think."
        ]
        return random.choice(general_content)
    
    async def _adapt_for_platform(self, caption: str, platform: Platform) -> str:
        """Adapte la légende pour la plateforme"""
        if platform == Platform.TWITTER:
            # Limiter à 280 caractères
            return caption[:277] + "..." if len(caption) > 280 else caption
        elif platform == Platform.INSTAGRAM:
            # Ajouter des emojis
            return f"{caption} ✨"
        elif platform == Platform.LINKEDIN:
            # Style plus professionnel
            return caption.replace("💭", "").replace("✨", "").strip()
        return caption
    
    async def _expand_caption(self, caption: str, topic: str) -> str:
        """Étend la légende pour un format long"""
        expansion = f"\n\nWhat are your thoughts on {topic}? I'd love to hear your perspective in the comments below! 💬"
        return caption + expansion

# ============================================================================
# STORY TELLER AGENT
# ============================================================================

class StoryTeller:
    """Agent de narration et storytelling"""
    
    def __init__(self):
        self.story_structures = {
            "hero_journey": [
                "ordinary_world",
                "call_to_adventure", 
                "challenge",
                "transformation",
                "return_with_wisdom"
            ],
            "before_after": [
                "before_situation",
                "turning_point",
                "after_situation",
                "lesson_learned"
            ],
            "problem_solution": [
                "problem_identification",
                "search_for_solution",
                "solution_discovery",
                "implementation",
                "results"
            ]
        }
    
    async def create_story(self, topic: str, structure: str = "before_after", target_audience: str = "general") -> Dict[str, Any]:
        """Crée une histoire structurée"""
        try:
            story_flow = self.story_structures.get(structure, self.story_structures["before_after"])
            story_parts = {}
            
            for part in story_flow:
                story_parts[part] = await self._generate_story_part(part, topic, target_audience)
            
            # Assemblage de l'histoire complète
            full_story = await self._assemble_story(story_parts, structure)
            
            # Analyse de l'histoire
            story_analysis = await self._analyze_story(full_story)
            
            return {
                "story": full_story,
                "structure": structure,
                "parts": story_parts,
                "analysis": story_analysis,
                "estimated_read_time": f"{len(full_story.split()) // 200 + 1} minutes",
                "engagement_score": story_analysis.get("engagement_score", 0.7)
            }
            
        except Exception as e:
            logger.error(f"Erreur création histoire: {e}")
            return {"error": str(e)}
    
    async def _generate_story_part(self, part: str, topic: str, audience: str) -> str:
        """Génère une partie spécifique de l'histoire"""
        part_templates = {
            "ordinary_world": f"Like many people, I used to think {topic} was...",
            "call_to_adventure": f"Then something happened that made me reconsider {topic}...",
            "challenge": f"The biggest challenge with {topic} was...",
            "transformation": f"But here's how {topic} changed everything...",
            "return_with_wisdom": f"Now I understand that {topic} is actually...",
            
            "before_situation": f"Before discovering {topic}, my situation was...",
            "turning_point": f"The turning point came when I realized {topic}...",
            "after_situation": f"After implementing {topic}, everything changed...",
            "lesson_learned": f"The key lesson about {topic} is...",
            
            "problem_identification": f"I noticed a problem related to {topic}...",
            "search_for_solution": f"I tried various approaches to solve {topic}...",
            "solution_discovery": f"Finally, I discovered that {topic} works when...",
            "implementation": f"Here's how I implemented {topic}...",
            "results": f"The results with {topic} were incredible..."
        }
        
        return part_templates.get(part, f"This is about {topic}...")
    
    async def _assemble_story(self, parts: Dict[str, str], structure: str) -> str:
        """Assemble les parties en histoire cohérente"""
        story_flow = self.story_structures[structure]
        assembled_story = ""
        
        for i, part in enumerate(story_flow):
            if i > 0:
                assembled_story += "\n\n"
            assembled_story += parts[part]
        
        return assembled_story
    
    async def _analyze_story(self, story: str) -> Dict[str, Any]:
        """Analyse la qualité de l'histoire"""
        word_count = len(story.split())
        sentence_count = len(re.findall(r'[.!?]+', story))
        
        # Calcul des scores
        length_score = min(1.0, word_count / 200)  # Optimal à 200 mots
        readability_score = max(0.3, 1.0 - abs(sentence_count / word_count - 0.1) * 10)
        engagement_score = (length_score + readability_score) / 2
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "length_score": length_score,
            "readability_score": readability_score,
            "engagement_score": engagement_score,
            "estimated_reading_time": f"{word_count // 200 + 1} minutes"
        }

# ============================================================================
# REPLY GENERATOR AGENT
# ============================================================================

class ReplyGenerator:
    """Agent de génération de réponses"""
    
    def __init__(self):
        self.reply_templates = {
            "positive": [
                "Thanks for sharing! {response}",
                "I love this perspective! {response}",
                "Absolutely agree! {response}",
                "This is so valuable! {response}"
            ],
            "neutral": [
                "Interesting point! {response}",
                "Thanks for your input! {response}",
                "I appreciate this! {response}",
                "Good to know! {response}"
            ],
            "question": [
                "Great question! {response}",
                "That's a thoughtful question! {response}",
                "Interesting question! {response}",
                "Thanks for asking! {response}"
            ],
            "supportive": [
                "You've got this! {response}",
                "Keep going! {response}",
                "I believe in you! {response}",
                "You're doing great! {response}"
            ]
        }
    
    async def generate_reply(self, original_content: str, comment: str, tone: str = "friendly", platform: Platform = Platform.INSTAGRAM) -> str:
        """Génère une réponse appropriée"""
        try:
            # Analyse du sentiment du commentaire
            sentiment = await self._analyze_comment_sentiment(comment)
            
            # Sélection du template approprié
            template_category = await self._select_template_category(comment, sentiment)
            templates = self.reply_templates.get(template_category, self.reply_templates["neutral"])
            template = random.choice(templates)
            
            # Génération de la réponse spécifique
            specific_response = await self._generate_specific_response(original_content, comment, sentiment)
            
            # Formatage de la réponse finale
            reply = template.format(response=specific_response)
            
            # Adaptation pour la plateforme
            reply = await self._adapt_reply_for_platform(reply, platform)
            
            return reply
            
        except Exception as e:
            logger.error(f"Erreur génération réponse: {e}")
            return "Thanks for your comment! 😊"
    
    async def _analyze_comment_sentiment(self, comment: str) -> str:
        """Analyse le sentiment d'un commentaire"""
        positive_words = ["love", "great", "amazing", "awesome", "beautiful", "perfect"]
        negative_words = ["hate", "bad", "terrible", "awful", "horrible", "worst"]
        question_words = ["what", "how", "why", "when", "where", "which"]
        
        comment_lower = comment.lower()
        
        if any(word in comment_lower for word in question_words):
            return "question"
        elif any(word in comment_lower for word in positive_words):
            return "positive"
        elif any(word in comment_lower for word in negative_words):
            return "negative"
        else:
            return "neutral"
    
    async def _select_template_category(self, comment: str, sentiment: str) -> str:
        """Sélectionne la catégorie de template appropriée"""
        if sentiment == "question":
            return "question"
        elif sentiment == "positive":
            return "positive"
        elif sentiment == "negative":
            return "supportive"
        else:
            return "neutral"
    
    async def _generate_specific_response(self, original_content: str, comment: str, sentiment: str) -> str:
        """Génère une réponse spécifique au contexte"""
        if sentiment == "question":
            return "Let me share some insights on that."
        elif sentiment == "positive":
            return "Your support means everything!"
        elif sentiment == "negative":
            return "I understand your perspective and appreciate your feedback."
        else:
            return "It's great to connect with you!"
    
    async def _adapt_reply_for_platform(self, reply: str, platform: Platform) -> str:
        """Adapte la réponse pour la plateforme"""
        if platform == Platform.INSTAGRAM:
            return f"{reply} ❤️"
        elif platform == Platform.TWITTER:
            return reply  # Plus concis
        elif platform == Platform.LINKEDIN:
            return reply.replace("😊", "").replace("❤️", "")  # Plus professionnel
        return reply

# ============================================================================
# VIRAL PREDICTOR AGENT
# ============================================================================

class ViralPredictor:
    """Agent de prédiction de potentiel viral"""
    
    def __init__(self):
        self.viral_factors = {
            "content_length": {"optimal_range": (50, 300), "weight": 0.15},
            "emotional_words": {"keywords": ["amazing", "incredible", "shocking", "unbelievable"], "weight": 0.20},
            "call_to_action": {"indicators": ["share", "tag", "comment", "save"], "weight": 0.15},
            "trending_topics": {"weight": 0.20},
            "visual_elements": {"emojis": True, "weight": 0.10},
            "timing": {"peak_hours": [18, 19, 20, 21], "weight": 0.10},
            "originality": {"weight": 0.10}
        }
    
    async def predict_viral_potential(self, content: str, platform: Platform, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prédit le potentiel viral du contenu"""
        try:
            metadata = metadata or {}
            viral_score = 0.0
            factor_scores = {}
            
            # Analyse de chaque facteur viral
            for factor, config in self.viral_factors.items():
                score = await self._analyze_viral_factor(content, factor, config, platform, metadata)
                factor_scores[factor] = score
                viral_score += score * config["weight"]
            
            # Détermination du niveau de potentiel viral
            viral_level = self._determine_viral_level(viral_score)
            
            # Prédictions d'engagement
            engagement_prediction = await self._predict_engagement_metrics(viral_score, platform)
            
            # Recommandations d'amélioration
            recommendations = await self._generate_viral_recommendations(factor_scores, content)
            
            return {
                "viral_score": viral_score,
                "viral_level": viral_level,
                "factor_scores": factor_scores,
                "engagement_prediction": engagement_prediction,
                "recommendations": recommendations,
                "optimal_posting_time": await self._suggest_optimal_time(platform),
                "confidence_level": min(1.0, viral_score + 0.2)
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction virale: {e}")
            return {"error": str(e)}
    
    async def _analyze_viral_factor(self, content: str, factor: str, config: Dict[str, Any], platform: Platform, metadata: Dict[str, Any]) -> float:
        """Analyse un facteur viral spécifique"""
        if factor == "content_length":
            length = len(content)
            optimal_range = config["optimal_range"]
            if optimal_range[0] <= length <= optimal_range[1]:
                return 1.0
            else:
                return max(0.3, 1.0 - abs(length - sum(optimal_range) / 2) / 100)
        
        elif factor == "emotional_words":
            emotional_count = sum(1 for word in config["keywords"] if word.lower() in content.lower())
            return min(1.0, emotional_count * 0.3)
        
        elif factor == "call_to_action":
            cta_count = sum(1 for indicator in config["indicators"] if indicator.lower() in content.lower())
            return min(1.0, cta_count * 0.5)
        
        elif factor == "visual_elements":
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
            has_emojis = bool(emoji_pattern.search(content))
            return 0.8 if has_emojis else 0.2
        
        elif factor == "originality":
            # Simulation d'analyse d'originalité
            return random.uniform(0.4, 0.9)
        
        elif factor == "trending_topics":
            # Simulation d'analyse de tendances
            return random.uniform(0.3, 0.8)
        
        elif factor == "timing":
            current_hour = datetime.now().hour
            peak_hours = config.get("peak_hours", [])
            return 1.0 if current_hour in peak_hours else 0.5
        
        return 0.5
    
    def _determine_viral_level(self, viral_score: float) -> ViralPotential:
        """Détermine le niveau de potentiel viral"""
        if viral_score >= 0.8:
            return ViralPotential.EXPLOSIVE
        elif viral_score >= 0.65:
            return ViralPotential.HIGH
        elif viral_score >= 0.45:
            return ViralPotential.MEDIUM
        else:
            return ViralPotential.LOW
    
    async def _predict_engagement_metrics(self, viral_score: float, platform: Platform) -> Dict[str, Any]:
        """Prédit les métriques d'engagement"""
        base_engagement = viral_score * 0.1  # 10% d'engagement au maximum
        
        platform_multipliers = {
            Platform.TIKTOK: 1.5,
            Platform.INSTAGRAM: 1.2,
            Platform.TWITTER: 1.0,
            Platform.YOUTUBE: 0.8,
            Platform.LINKEDIN: 0.6
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        predicted_engagement = base_engagement * multiplier
        
        return {
            "predicted_engagement_rate": predicted_engagement,
            "estimated_likes": int(predicted_engagement * 1000),
            "estimated_shares": int(predicted_engagement * 200),
            "estimated_comments": int(predicted_engagement * 100),
            "reach_potential": min(1.0, viral_score * 1.2)
        }
    
    async def _generate_viral_recommendations(self, factor_scores: Dict[str, float], content: str) -> List[str]:
        """Génère des recommandations pour améliorer le potentiel viral"""
        recommendations = []
        
        if factor_scores.get("content_length", 0) < 0.7:
            recommendations.append("Ajustez la longueur du contenu (50-300 caractères optimal)")
        
        if factor_scores.get("emotional_words", 0) < 0.5:
            recommendations.append("Ajoutez des mots émotionnels forts (amazing, incredible, shocking)")
        
        if factor_scores.get("call_to_action", 0) < 0.5:
            recommendations.append("Incluez un appel à l'action clair (share, comment, tag)")
        
        if factor_scores.get("visual_elements", 0) < 0.5:
            recommendations.append("Ajoutez des emojis pour plus d'impact visuel")
        
        return recommendations
    
    async def _suggest_optimal_time(self, platform: Platform) -> str:
        """Suggère le meilleur moment pour publier"""
        optimal_times = {
            Platform.INSTAGRAM: "18h-21h",
            Platform.TIKTOK: "19h-22h", 
            Platform.TWITTER: "12h-15h et 17h-20h",
            Platform.YOUTUBE: "14h-16h et 20h-22h",
            Platform.LINKEDIN: "8h-10h et 17h-19h"
        }
        
        return optimal_times.get(platform, "18h-21h")

# ============================================================================
# CONTENT SCHEDULER AGENT
# ============================================================================

class ContentScheduler:
    """Agent de programmation de contenu"""
    
    def __init__(self):
        self.scheduled_content = {}
        self.platform_optimal_times = {
            Platform.INSTAGRAM: [
                {"day": "monday", "times": ["18:00", "19:00", "20:00"]},
                {"day": "tuesday", "times": ["11:00", "18:00", "19:00"]},
                {"day": "wednesday", "times": ["11:00", "18:00", "20:00"]},
                {"day": "thursday", "times": ["11:00", "18:00", "19:00"]},
                {"day": "friday", "times": ["10:00", "11:00", "15:00"]},
                {"day": "saturday", "times": ["10:00", "11:00", "14:00"]},
                {"day": "sunday", "times": ["10:00", "14:00", "15:00"]}
            ],
            Platform.TIKTOK: [
                {"day": "tuesday", "times": ["19:00", "20:00", "21:00"]},
                {"day": "thursday", "times": ["19:00", "20:00", "21:00"]},
                {"day": "sunday", "times": ["19:00", "20:00", "21:00"]}
            ],
            Platform.YOUTUBE: [
                {"day": "tuesday", "times": ["14:00", "15:00", "20:00"]},
                {"day": "wednesday", "times": ["14:00", "15:00", "20:00"]},
                {"day": "thursday", "times": ["14:00", "15:00", "20:00"]},
                {"day": "friday", "times": ["14:00", "15:00", "20:00"]},
                {"day": "saturday", "times": ["14:00", "15:00", "20:00"]}
            ]
        }
    
    async def schedule_content(self, request: ScheduleRequest) -> Dict[str, Any]:
        """Programme du contenu pour publication"""
        try:
            schedule_id = str(uuid.uuid4())
            
            # Validation de la requête
            validation_result = await self._validate_schedule_request(request)
            if not validation_result["valid"]:
                return {"error": validation_result["error"]}
            
            # Optimisation du timing si nécessaire
            optimal_time = await self._optimize_schedule_time(request.scheduled_time, request.platform)
            
            # Création de l'entrée de programmation
            schedule_entry = {
                "id": schedule_id,
                "content": request.content,
                "platform": request.platform.value,
                "original_time": request.scheduled_time,
                "optimized_time": optimal_time,
                "timezone": request.timezone_str,
                "repeat_interval": request.repeat_interval,
                "metadata": request.metadata,
                "status": "scheduled",
                "created_at": datetime.now(timezone.utc)
            }
            
            # Stockage de la programmation
            self.scheduled_content[schedule_id] = schedule_entry
            
            # Génération du plan de publication
            publication_plan = await self._generate_publication_plan(schedule_entry)
            
            return {
                "schedule_id": schedule_id,
                "status": "scheduled",
                "original_time": request.scheduled_time.isoformat(),
                "optimized_time": optimal_time.isoformat(),
                "time_adjustment": (optimal_time - request.scheduled_time).total_seconds(),
                "publication_plan": publication_plan,
                "next_publication": optimal_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur programmation contenu: {e}")
            return {"error": str(e)}
    
    async def _validate_schedule_request(self, request: ScheduleRequest) -> Dict[str, Any]:
        """Valide une requête de programmation"""
        if request.scheduled_time <= datetime.now(timezone.utc):
            return {"valid": False, "error": "La date de programmation doit être future"}
        
        if len(request.content) == 0:
            return {"valid": False, "error": "Le contenu ne peut pas être vide"}
        
        return {"valid": True}
    
    async def _optimize_schedule_time(self, requested_time: datetime, platform: Platform) -> datetime:
        """Optimise l'heure de publication"""
        platform_times = self.platform_optimal_times.get(platform, [])
        
        if not platform_times:
            return requested_time
        
        # Trouver le jour de la semaine
        day_name = requested_time.strftime("%A").lower()
        
        # Chercher les heures optimales pour ce jour
        day_schedule = next((day for day in platform_times if day["day"] == day_name), None)
        
        if not day_schedule:
            return requested_time
        
        # Trouver l'heure optimale la plus proche
        requested_hour = requested_time.hour
        optimal_hours = [int(time.split(":")[0]) for time in day_schedule["times"]]
        
        closest_hour = min(optimal_hours, key=lambda x: abs(x - requested_hour))
        
        # Créer la nouvelle datetime optimisée
        optimized_time = requested_time.replace(hour=closest_hour, minute=0, second=0)
        
        return optimized_time
    
    async def _generate_publication_plan(self, schedule_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un plan de publication"""
        plan = {
            "primary_publication": {
                "platform": schedule_entry["platform"],
                "time": schedule_entry["optimized_time"],
                "content": schedule_entry["content"]
            },
            "cross_promotion": [],
            "follow_up_actions": []
        }
        
        # Suggestions de cross-promotion
        if schedule_entry["platform"] == Platform.INSTAGRAM.value:
            plan["cross_promotion"].append({
                "platform": Platform.TWITTER.value,
                "time": schedule_entry["optimized_time"] + timedelta(hours=2),
                "content": f"Just posted on Instagram! {schedule_entry['content'][:100]}..."
            })
        
        # Actions de suivi
        plan["follow_up_actions"].append({
            "action": "engagement_monitoring",
            "start_time": schedule_entry["optimized_time"] + timedelta(hours=1),
            "duration_hours": 24
        })
        
        return plan
    
    async def get_scheduled_content(self, platform: Platform = None, date_range: Tuple[datetime, datetime] = None) -> List[Dict[str, Any]]:
        """Récupère le contenu programmé"""
        try:
            filtered_content = []
            
            for schedule_id, entry in self.scheduled_content.items():
                # Filtre par plateforme si spécifié
                if platform and entry["platform"] != platform.value:
                    continue
                
                # Filtre par date si spécifié
                if date_range:
                    if not (date_range[0] <= entry["optimized_time"] <= date_range[1]):
                        continue
                
                filtered_content.append(entry)
            
            # Tri par date de publication
            filtered_content.sort(key=lambda x: x["optimized_time"])
            
            return filtered_content
            
        except Exception as e:
            logger.error(f"Erreur récupération contenu programmé: {e}")
            return []
    
    async def cancel_scheduled_content(self, schedule_id: str) -> Dict[str, Any]:
        """Annule du contenu programmé"""
        try:
            if schedule_id not in self.scheduled_content:
                return {"error": "Contenu programmé non trouvé"}
            
            # Marquer comme annulé
            self.scheduled_content[schedule_id]["status"] = "cancelled"
            self.scheduled_content[schedule_id]["cancelled_at"] = datetime.now(timezone.utc)
            
            return {
                "status": "cancelled",
                "schedule_id": schedule_id,
                "message": "Contenu programmé annulé avec succès"
            }
            
        except Exception as e:
            logger.error(f"Erreur annulation contenu: {e}")
            return {"error": str(e)}

# ============================================================================
# CONSOLIDATED CONTENT AGENT
# ============================================================================

class ConsolidatedContentAgent:
    """Agent consolidé pour toutes les fonctionnalités de contenu"""
    
    def __init__(self):
        # Initialisation des agents spécialisés
        self.optimizer = ContentOptimizer()
        self.hashtag_generator = HashtagGenerator()
        self.caption_writer = CaptionWriter()
        self.story_teller = StoryTeller()
        self.reply_generator = ReplyGenerator()
        self.viral_predictor = ViralPredictor()
        self.scheduler = ContentScheduler()
        
        logger.info("✅ ConsolidatedContentAgent initialisé avec 7 agents spécialisés")
    
    async def process_content_request(self, request: ContentRequest) -> ContentResult:
        """Traite une requête de contenu complète"""
        try:
            request_id = str(uuid.uuid4())
            
            # Génération du contenu principal
            if request.content_type == ContentType.CAPTION:
                content = await self.caption_writer.generate_caption(
                    request.topic, request.style, request.platform
                )
            elif request.content_type == ContentType.STORY:
                story_result = await self.story_teller.create_story(
                    request.topic, "before_after", request.target_audience
                )
                content = story_result.get("story", "")
            else:
                content = f"Contenu {request.content_type.value} sur {request.topic}"
            
            # Optimisation du contenu
            optimization_result = await self.optimizer.optimize_content(
                content, request.platform
            )
            optimized_content = optimization_result.get("optimized_content", content)
            
            # Génération des hashtags
            hashtags = await self.hashtag_generator.generate_hashtags(
                optimized_content, request.platform
            )
            
            # Prédiction virale
            viral_result = await self.viral_predictor.predict_viral_potential(
                optimized_content, request.platform
            )
            
            # Création du résultat
            result = ContentResult(
                request_id=request_id,
                content_type=request.content_type,
                content=optimized_content,
                metadata={
                    "original_content": content,
                    "optimization": optimization_result,
                    "viral_analysis": viral_result,
                    "platform": request.platform.value,
                    "style": request.style.value,
                    "target_audience": request.target_audience
                },
                quality_score=optimization_result.get("optimization_score", 0.7),
                viral_potential=viral_result.get("viral_level", ViralPotential.MEDIUM),
                engagement_prediction=viral_result.get("viral_score", 0.5),
                hashtags=hashtags
            )
            
            logger.info(f"Contenu traité avec succès: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur traitement requête contenu: {e}")
            raise
    
    async def create_complete_content_package(self, topic: str, platform: Platform, style: ContentStyle = ContentStyle.CASUAL) -> Dict[str, Any]:
        """Crée un package complet de contenu"""
        try:
            package = {}
            
            # Contenu principal
            main_request = ContentRequest(
                content_type=ContentType.CAPTION,
                platform=platform,
                style=style,
                target_audience="general",
                topic=topic
            )
            main_content = await self.process_content_request(main_request)
            package["main_content"] = main_content
            
            # Histoire associée
            story_result = await self.story_teller.create_story(topic)
            package["story"] = story_result
            
            # Hashtags optimisés
            hashtags = await self.hashtag_generator.generate_hashtags(
                main_content.content, platform, count=15
            )
            package["hashtags"] = hashtags
            
            # Analyse virale
            viral_analysis = await self.viral_predictor.predict_viral_potential(
                main_content.content, platform
            )
            package["viral_analysis"] = viral_analysis
            
            # Suggestions de réponses types
            sample_comments = ["This is amazing!", "How did you do this?", "Not sure about this..."]
            replies = []
            for comment in sample_comments:
                reply = await self.reply_generator.generate_reply(
                    main_content.content, comment, "friendly", platform
                )
                replies.append({"comment": comment, "reply": reply})
            package["sample_replies"] = replies
            
            # Suggestions de programmation
            optimal_time = datetime.now(timezone.utc) + timedelta(hours=2)
            schedule_request = ScheduleRequest(
                content=main_content.content,
                platform=platform,
                scheduled_time=optimal_time
            )
            schedule_result = await self.scheduler.schedule_content(schedule_request)
            package["schedule_suggestion"] = schedule_result
            
            return {
                "topic": topic,
                "platform": platform.value,
                "style": style.value,
                "package": package,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur création package contenu: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Récupère le statut de tous les agents"""
        return {
            "status": "active",
            "agents": {
                "content_optimizer": "active",
                "hashtag_generator": "active", 
                "caption_writer": "active",
                "story_teller": "active",
                "reply_generator": "active",
                "viral_predictor": "active",
                "content_scheduler": "active"
            },
            "capabilities": [
                "content_optimization",
                "hashtag_generation",
                "caption_writing", 
                "storytelling",
                "reply_generation",
                "viral_prediction",
                "content_scheduling"
            ],
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_content_agent() -> ConsolidatedContentAgent:
    """Factory pour créer un agent de contenu consolidé"""
    return ConsolidatedContentAgent()

async def process_content_async(topic: str, platform: str, style: str = "casual") -> Dict[str, Any]:
    """Fonction helper pour traitement asynchrone de contenu"""
    agent = create_content_agent()
    
    platform_enum = Platform(platform.lower())
    style_enum = ContentStyle(style.lower())
    
    return await agent.create_complete_content_package(topic, platform_enum, style_enum)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ConsolidatedContentAgent",
    "ContentOptimizer", 
    "HashtagGenerator",
    "CaptionWriter", 
    "StoryTeller",
    "ReplyGenerator", 
    "ViralPredictor",
    "ContentScheduler",
    "ContentRequest",
    "ContentResult", 
    "ScheduleRequest",
    "ContentType",
    "Platform",
    "ContentStyle", 
    "ViralPotential",
    "create_content_agent",
    "process_content_async"
]

logger.info("✅ Module backend.ai.content chargé avec succès")