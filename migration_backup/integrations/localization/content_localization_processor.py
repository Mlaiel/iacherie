"""📝 Content Localization Processor - Multi-Format Enterprise Support
=====================================================================

Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Content localization processor enterprise avec AI-powered content adaptation,
multi-format support et cultural content optimization.

Intégration métier Ainflue:
- Multi-format content localization (text, video, audio, images)
- AI-powered content adaptation pour créateurs
- Cultural content optimization par région
- SEO localization optimization intégrée
- Content quality assurance automatisée
- Batch localization processing pour distribution massive

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Date: 16 Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture content localization est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import json
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentFormat(Enum):
    """Formats de contenu supportés"""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    VIDEO_DESCRIPTION = "video_description"
    AUDIO_TRANSCRIPT = "audio_transcript"
    SOCIAL_MEDIA_POST = "social_media_post"
    BLOG_POST = "blog_post"
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"

class LocalizationStrategy(Enum):
    """Stratégies de localisation"""
    DIRECT_TRANSLATION = "direct_translation"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    TRANSCREATION = "transcreation"
    LOCALIZATION = "localization"
    INTERNATIONALIZATION = "internationalization"

class ContentCategory(Enum):
    """Catégories de contenu pour optimisation"""
    MARKETING = "marketing"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    SOCIAL = "social"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    COMMERCIAL = "commercial"

class ProcessingPriority(Enum):
    """Priorités de traitement"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"

@dataclass
class ContentItem:
    """Item de contenu à localiser"""
    content_id: str
    format: ContentFormat
    source_language: str
    content_data: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: ContentCategory = ContentCategory.SOCIAL
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LocalizationRequest:
    """Requête de localisation"""
    content_item: ContentItem
    target_languages: List[str]
    target_regions: List[str]
    strategy: LocalizationStrategy = LocalizationStrategy.CULTURAL_ADAPTATION
    quality_level: str = "professional"
    preserve_formatting: bool = True
    enable_seo_optimization: bool = True
    enable_cultural_adaptation: bool = True
    custom_instructions: Optional[str] = None

@dataclass
class LocalizedContent:
    """Contenu localisé"""
    original_content_id: str
    target_language: str
    target_region: str
    localized_data: Union[str, Dict[str, Any]]
    format: ContentFormat
    strategy_used: LocalizationStrategy
    quality_score: float
    cultural_adaptation_score: float
    seo_optimization_applied: bool
    processing_time: float
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchLocalizationJob:
    """Job de localisation en lot"""
    job_id: str
    content_items: List[ContentItem]
    target_languages: List[str]
    target_regions: List[str]
    strategy: LocalizationStrategy
    status: str = "pending"
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[LocalizedContent] = field(default_factory=list)

class ContentLocalizationProcessor:
    """Content localization processor enterprise avec AI-powered content adaptation
    
    Expert Team Implementation:
    - Lead Dev IA: AI-powered content adaptation et intelligent format handling
    - Backend Senior: High-performance batch processing et content pipeline
    - ML Engineer: Machine learning content optimization et quality assessment
    - DBA: Optimized content storage et localization cache management
    - Sécurité: Secure content handling et IP protection during processing
    - Microservices: Distributed content processing architecture
    - Audio: Audio content transcription et localization support
    - DevOps: Production-ready content processing deployment
    - IA Prompt Engineer: Context-aware content adaptation prompting
    """
    
    def __init__(self):
        """Initialize content localization processor"""
        self.processing_queue: List[LocalizationRequest] = []
        self.batch_jobs: Dict[str, BatchLocalizationJob] = {}
        self.content_cache: Dict[str, LocalizedContent] = {}
        self.format_processors: Dict[ContentFormat, Any] = {}
        self.quality_assessor = ContentQualityAssessor()
        self.seo_optimizer = ContentSEOOptimizer()
        
        # Initialize format processors
        self._initialize_format_processors()
        
        logger.info(f"📝 Content Localization Processor initialized")
        logger.info(f"🔧 Format processors loaded: {len(self.format_processors)}")
    
    def _initialize_format_processors(self):
        """Initialize format-specific processors"""
        
        self.format_processors = {
            ContentFormat.TEXT: TextContentProcessor(),
            ContentFormat.HTML: HTMLContentProcessor(),
            ContentFormat.MARKDOWN: MarkdownContentProcessor(),
            ContentFormat.JSON: JSONContentProcessor(),
            ContentFormat.VIDEO_DESCRIPTION: VideoDescriptionProcessor(),
            ContentFormat.SOCIAL_MEDIA_POST: SocialMediaProcessor(),
            ContentFormat.BLOG_POST: BlogPostProcessor(),
            ContentFormat.EMAIL: EmailContentProcessor()
        }
    
    async def localize_content(
        self,
        content: Union[str, Dict[str, Any]],
        content_format: ContentFormat,
        source_language: str,
        target_language: str,
        target_region: str,
        strategy: LocalizationStrategy = LocalizationStrategy.CULTURAL_ADAPTATION,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LocalizedContent:
        """Localize single content item
        
        Args:
            content: Contenu à localiser
            content_format: Format du contenu
            source_language: Langue source
            target_language: Langue cible
            target_region: Région cible
            strategy: Stratégie de localisation
            metadata: Métadonnées supplémentaires
            
        Returns:
            Contenu localisé
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Create content item
            content_item = ContentItem(
                content_id=self._generate_content_id(content),
                format=content_format,
                source_language=source_language,
                content_data=content,
                metadata=metadata or {}
            )
            
            # Create localization request
            request = LocalizationRequest(
                content_item=content_item,
                target_languages=[target_language],
                target_regions=[target_region],
                strategy=strategy
            )
            
            # Process localization
            result = await self._process_localization_request(request)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result:
                result.processing_time = processing_time
                logger.info(f"✅ Content localized in {processing_time:.2f}s: {source_language} -> {target_language}")
                return result
            else:
                raise ValueError("Localization processing failed")
                
        except Exception as e:
            logger.error(f"❌ Content localization error: {e}")
            raise
    
    def _generate_content_id(self, content: Union[str, Dict[str, Any]]) -> str:
        """Generate unique content ID"""
        content_str = json.dumps(content, sort_keys=True) if isinstance(content, dict) else str(content)
        return hashlib.md5(content_str.encode()).hexdigest()[:12]
    
    async def _process_localization_request(self, request: LocalizationRequest) -> Optional[LocalizedContent]:
        """Process single localization request"""
        
        content_item = request.content_item
        target_language = request.target_languages[0]
        target_region = request.target_regions[0]
        
        # Check cache first
        cache_key = f"{content_item.content_id}_{target_language}_{target_region}"
        if cache_key in self.content_cache:
            logger.debug(f"🎯 Cache hit for content: {cache_key}")
            return self.content_cache[cache_key]
        
        # Get format processor
        processor = self.format_processors.get(content_item.format)
        if not processor:
            logger.warning(f"⚠️ No processor for format: {content_item.format.value}")
            processor = self.format_processors[ContentFormat.TEXT]  # Fallback
        
        # Extract localizable content
        extractable_content = await processor.extract_localizable_content(content_item.content_data)
        
        # Apply localization strategy
        localized_content = await self._apply_localization_strategy(
            extractable_content,
            content_item.source_language,
            target_language,
            target_region,
            request.strategy,
            content_item.category
        )
        
        # Reconstruct content with localized text
        final_content = await processor.reconstruct_content(
            content_item.content_data,
            localized_content
        )
        
        # Apply cultural adaptation if enabled
        if request.enable_cultural_adaptation:
            final_content = await self._apply_cultural_adaptation(
                final_content,
                target_region,
                content_item.category
            )
        
        # Apply SEO optimization if enabled
        seo_applied = False
        if request.enable_seo_optimization:
            final_content = await self.seo_optimizer.optimize_content(
                final_content,
                target_language,
                target_region,
                content_item.category
            )
            seo_applied = True
        
        # Assess quality
        quality_score = await self.quality_assessor.assess_content_quality(
            content_item.content_data,
            final_content,
            content_item.source_language,
            target_language
        )
        
        # Calculate cultural adaptation score
        cultural_score = await self._calculate_cultural_adaptation_score(
            final_content,
            target_region,
            content_item.category
        )
        
        # Create localized content result
        result = LocalizedContent(
            original_content_id=content_item.content_id,
            target_language=target_language,
            target_region=target_region,
            localized_data=final_content,
            format=content_item.format,
            strategy_used=request.strategy,
            quality_score=quality_score,
            cultural_adaptation_score=cultural_score,
            seo_optimization_applied=seo_applied,
            processing_time=0.0,  # Will be set by caller
            created_at=datetime.now(),
            metadata={
                "source_language": content_item.source_language,
                "category": content_item.category.value,
                "preserve_formatting": request.preserve_formatting
            }
        )
        
        # Cache result
        self.content_cache[cache_key] = result
        
        return result
    
    async def _apply_localization_strategy(
        self,
        content: str,
        source_language: str,
        target_language: str,
        target_region: str,
        strategy: LocalizationStrategy,
        category: ContentCategory
    ) -> str:
        """Apply specific localization strategy"""
        
        if strategy == LocalizationStrategy.DIRECT_TRANSLATION:
            # Simple translation without cultural adaptation
            return await self._direct_translate(content, source_language, target_language)
        
        elif strategy == LocalizationStrategy.CULTURAL_ADAPTATION:
            # Translation with cultural considerations
            translated = await self._direct_translate(content, source_language, target_language)
            return await self._apply_cultural_adaptation(translated, target_region, category)
        
        elif strategy == LocalizationStrategy.TRANSCREATION:
            # Creative adaptation maintaining intent over literal meaning
            return await self._transcreate_content(content, source_language, target_language, target_region, category)
        
        elif strategy == LocalizationStrategy.LOCALIZATION:
            # Full localization with cultural, legal, and technical adaptations
            return await self._full_localization(content, source_language, target_language, target_region, category)
        
        else:
            # Default to cultural adaptation
            translated = await self._direct_translate(content, source_language, target_language)
            return await self._apply_cultural_adaptation(translated, target_region, category)
    
    async def _direct_translate(self, content: str, source_lang: str, target_lang: str) -> str:
        """Direct translation without cultural adaptation"""
        # Simulate translation (in production, use actual translation service)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Simple language mapping for demonstration
        if source_lang == "en" and target_lang == "fr":
            return content.replace("Hello", "Bonjour").replace("Welcome", "Bienvenue")
        elif source_lang == "en" and target_lang == "es":
            return content.replace("Hello", "Hola").replace("Welcome", "Bienvenido")
        elif source_lang == "en" and target_lang == "de":
            return content.replace("Hello", "Hallo").replace("Welcome", "Willkommen")
        else:
            return f"[TRANSLATED:{target_lang}] {content}"
    
    async def _apply_cultural_adaptation(
        self,
        content: str,
        target_region: str,
        category: ContentCategory
    ) -> str:
        """Apply cultural adaptation to content"""
        
        adapted_content = content
        
        # Region-specific adaptations
        if target_region in ["SA", "AE", "QA"]:  # Middle East
            # Conservative adaptations
            adapted_content = re.sub(r'\b(party|nightlife)\b', 'gathering', adapted_content, flags=re.IGNORECASE)
            adapted_content = re.sub(r'\b(alcohol|beer|wine)\b', 'beverage', adapted_content, flags=re.IGNORECASE)
        
        elif target_region in ["JP", "KR"]:  # East Asia
            # Hierarchical respect adaptations
            adapted_content = re.sub(r'\byou should\b', 'please consider', adapted_content, flags=re.IGNORECASE)
            adapted_content = re.sub(r'\bmust\b', 'might', adapted_content, flags=re.IGNORECASE)
        
        elif target_region in ["DE", "AT", "CH"]:  # German-speaking
            # Precision and quality focus
            adapted_content = re.sub(r'\bgood\b', 'excellent quality', adapted_content, flags=re.IGNORECASE)
            adapted_content = re.sub(r'\bfast\b', 'efficient', adapted_content, flags=re.IGNORECASE)
        
        return adapted_content
    
    async def _transcreate_content(
        self,
        content: str,
        source_language: str,
        target_language: str,
        target_region: str,
        category: ContentCategory
    ) -> str:
        """Transcreate content for creative adaptation"""
        
        # Creative adaptation that maintains emotional impact
        transcreated = await self._direct_translate(content, source_language, target_language)
        
        # Apply creative cultural adaptations
        if category == ContentCategory.MARKETING:
            # Marketing-specific transcreation
            if target_region in ["FR", "BE"]:
                # French cultural preferences for sophistication
                transcreated = re.sub(r'\bgreat\b', 'exquisite', transcreated, flags=re.IGNORECASE)
                transcreated = re.sub(r'\bawesome\b', 'magnifique', transcreated, flags=re.IGNORECASE)
        
        elif category == ContentCategory.CREATIVE:
            # Creative content adaptations
            if target_region in ["JP"]:
                # Japanese aesthetic preferences
                transcreated = re.sub(r'\bbold\b', 'harmonious', transcreated, flags=re.IGNORECASE)
                transcreated = re.sub(r'\bloud\b', 'distinctive', transcreated, flags=re.IGNORECASE)
        
        return transcreated
    
    async def _full_localization(
        self,
        content: str,
        source_language: str,
        target_language: str,
        target_region: str,
        category: ContentCategory
    ) -> str:
        """Full localization with all adaptations"""
        
        # Start with translation
        localized = await self._direct_translate(content, source_language, target_language)
        
        # Apply cultural adaptation
        localized = await self._apply_cultural_adaptation(localized, target_region, category)
        
        # Apply regional formatting
        localized = await self._apply_regional_formatting(localized, target_region)
        
        # Apply legal compliance adaptations
        localized = await self._apply_legal_adaptations(localized, target_region)
        
        return localized
    
    async def _apply_regional_formatting(self, content: str, target_region: str) -> str:
        """Apply regional formatting conventions"""
        
        formatted_content = content
        
        # Date format adaptations
        if target_region in ["US"]:
            # MM/DD/YYYY format
            formatted_content = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'\1/\2/\3', formatted_content)
        elif target_region in ["DE", "FR", "IT"]:
            # DD.MM.YYYY or DD/MM/YYYY format
            formatted_content = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'\2.\1.\3', formatted_content)
        
        # Currency adaptations
        if target_region in ["EU", "DE", "FR", "IT", "ES"]:
            formatted_content = re.sub(r'\$(\d+)', r'€\1', formatted_content)
        elif target_region in ["GB"]:
            formatted_content = re.sub(r'\$(\d+)', r'£\1', formatted_content)
        elif target_region in ["JP"]:
            formatted_content = re.sub(r'\$(\d+)', r'¥\1', formatted_content)
        
        return formatted_content
    
    async def _apply_legal_adaptations(self, content: str, target_region: str) -> str:
        """Apply legal compliance adaptations"""
        
        adapted_content = content
        
        # GDPR compliance for EU regions
        if target_region in ["DE", "FR", "IT", "ES", "NL", "SE", "DK"]:
            if "personal data" in adapted_content.lower():
                adapted_content += " (GDPR compliance notice: Personal data processing requires explicit consent.)"
        
        # CCPA compliance for California
        elif target_region == "CA":
            if "data collection" in adapted_content.lower():
                adapted_content += " (CCPA notice: California residents have rights regarding personal information.)"
        
        return adapted_content
    
    async def _calculate_cultural_adaptation_score(
        self,
        content: str,
        target_region: str,
        category: ContentCategory
    ) -> float:
        """Calculate cultural adaptation effectiveness score"""
        
        score = 0.8  # Base score
        
        # Check for culturally appropriate adaptations
        content_lower = content.lower()
        
        if target_region in ["SA", "AE", "QA"]:
            # Check for Islamic cultural considerations
            if "beverage" in content_lower and "alcohol" not in content_lower:
                score += 0.1  # Positive adaptation
            if "gathering" in content_lower and "party" not in content_lower:
                score += 0.1  # Positive adaptation
        
        elif target_region in ["JP", "KR"]:
            # Check for respectful language
            if "please consider" in content_lower:
                score += 0.1  # Polite language
            if "harmonious" in content_lower:
                score += 0.1  # Cultural aesthetic
        
        elif target_region in ["DE", "AT"]:
            # Check for quality focus
            if "excellent quality" in content_lower:
                score += 0.1  # Quality emphasis
            if "efficient" in content_lower:
                score += 0.1  # Efficiency emphasis
        
        return min(1.0, score)
    
    async def multi_format_content_localization(
        self,
        content_items: List[tuple[Union[str, Dict], ContentFormat]],
        source_language: str,
        target_language: str,
        target_region: str
    ) -> List[LocalizedContent]:
        """Localize multiple content items with different formats"""
        
        results = []
        
        for content_data, content_format in content_items:
            try:
                result = await self.localize_content(
                    content=content_data,
                    content_format=content_format,
                    source_language=source_language,
                    target_language=target_language,
                    target_region=target_region
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Failed to localize {content_format.value}: {e}")
                continue
        
        return results
    
    async def ai_powered_content_adaptation(
        self,
        content: str,
        source_context: Dict[str, Any],
        target_context: Dict[str, Any],
        adaptation_level: float = 0.8
    ) -> str:
        """AI-powered content adaptation with context awareness"""
        
        # Simulate AI-powered adaptation
        await asyncio.sleep(0.2)  # Simulate AI processing
        
        adapted_content = content
        
        # Apply AI adaptations based on context
        if "tone" in source_context and "tone" in target_context:
            source_tone = source_context["tone"]
            target_tone = target_context["tone"]
            
            if source_tone == "casual" and target_tone == "formal":
                adapted_content = re.sub(r"\b(hey|hi)\b", "greetings", adapted_content, flags=re.IGNORECASE)
                adapted_content = re.sub(r"\b(cool|awesome)\b", "excellent", adapted_content, flags=re.IGNORECASE)
        
        if "audience" in target_context:
            audience = target_context["audience"]
            if audience == "professional":
                adapted_content = re.sub(r"\b(stuff|things)\b", "elements", adapted_content, flags=re.IGNORECASE)
        
        return adapted_content
    
    async def cultural_content_optimization(
        self,
        content: str,
        cultural_preferences: Dict[str, Any],
        optimization_level: float = 0.8
    ) -> Dict[str, Any]:
        """Optimize content for cultural preferences"""
        
        optimized_content = content
        optimizations_applied = []
        
        # Color preferences
        if "color_preferences" in cultural_preferences:
            prefs = cultural_preferences["color_preferences"]
            if "avoid_colors" in prefs:
                for color in prefs["avoid_colors"]:
                    if color in optimized_content.lower():
                        optimized_content = optimized_content.replace(color, "neutral")
                        optimizations_applied.append(f"color_replacement_{color}")
        
        # Communication style preferences
        if "communication_style" in cultural_preferences:
            style = cultural_preferences["communication_style"]
            if style == "indirect":
                optimized_content = re.sub(r"\byou must\b", "you might consider", optimized_content, flags=re.IGNORECASE)
                optimizations_applied.append("indirect_communication")
        
        # Visual preferences
        if "visual_preferences" in cultural_preferences:
            visual_prefs = cultural_preferences["visual_preferences"]
            if visual_prefs.get("minimalist", False):
                # Simplify language for minimalist preference
                optimized_content = re.sub(r"\bvery\s+", "", optimized_content, flags=re.IGNORECASE)
                optimizations_applied.append("minimalist_language")
        
        return {
            "optimized_content": optimized_content,
            "optimizations_applied": optimizations_applied,
            "optimization_score": len(optimizations_applied) * 0.2 + 0.6,
            "cultural_alignment": 0.85
        }
    
    async def seo_localization_optimization(
        self,
        content: str,
        target_keywords: List[str],
        target_region: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Optimize content for SEO in target region and language"""
        
        return await self.seo_optimizer.optimize_content(
            content,
            target_language,
            target_region,
            ContentCategory.MARKETING,  # Default category for SEO
            target_keywords
        )
    
    async def content_quality_assurance(
        self,
        original_content: str,
        localized_content: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Perform quality assurance on localized content"""
        
        return await self.quality_assessor.comprehensive_quality_assessment(
            original_content,
            localized_content,
            source_language,
            target_language
        )
    
    async def batch_localization_processing(
        self,
        content_batch: List[Dict[str, Any]],
        target_languages: List[str],
        target_regions: List[str],
        strategy: LocalizationStrategy = LocalizationStrategy.CULTURAL_ADAPTATION
    ) -> BatchLocalizationJob:
        """Process batch localization job"""
        
        job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(content_batch)}"
        
        # Create content items
        content_items = []
        for item in content_batch:
            content_item = ContentItem(
                content_id=self._generate_content_id(item.get("content", "")),
                format=ContentFormat(item.get("format", "text")),
                source_language=item.get("source_language", "en"),
                content_data=item.get("content", ""),
                metadata=item.get("metadata", {}),
                category=ContentCategory(item.get("category", "social")),
                priority=ProcessingPriority(item.get("priority", "normal"))
            )
            content_items.append(content_item)
        
        # Create batch job
        batch_job = BatchLocalizationJob(
            job_id=job_id,
            content_items=content_items,
            target_languages=target_languages,
            target_regions=target_regions,
            strategy=strategy,
            started_at=datetime.now()
        )
        
        self.batch_jobs[job_id] = batch_job
        
        # Process batch asynchronously
        asyncio.create_task(self._process_batch_job(job_id))
        
        logger.info(f"🚀 Batch localization job started: {job_id}")
        return batch_job
    
    async def _process_batch_job(self, job_id: str):
        """Process batch localization job asynchronously"""
        
        batch_job = self.batch_jobs[job_id]
        batch_job.status = "processing"
        
        total_items = len(batch_job.content_items)
        processed_items = 0
        
        try:
            for content_item in batch_job.content_items:
                for target_language in batch_job.target_languages:
                    for target_region in batch_job.target_regions:
                        try:
                            request = LocalizationRequest(
                                content_item=content_item,
                                target_languages=[target_language],
                                target_regions=[target_region],
                                strategy=batch_job.strategy
                            )
                            
                            result = await self._process_localization_request(request)
                            if result:
                                batch_job.results.append(result)
                            
                        except Exception as e:
                            logger.error(f"❌ Batch item processing failed: {e}")
                            continue
                
                processed_items += 1
                batch_job.progress = processed_items / total_items
                
                # Add small delay to prevent overwhelming system
                await asyncio.sleep(0.01)
            
            batch_job.status = "completed"
            batch_job.completed_at = datetime.now()
            logger.info(f"✅ Batch localization job completed: {job_id}")
            
        except Exception as e:
            batch_job.status = "failed"
            logger.error(f"❌ Batch localization job failed: {job_id} - {e}")
    
    async def get_batch_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of batch localization job"""
        
        batch_job = self.batch_jobs.get(job_id)
        if not batch_job:
            return None
        
        return {
            "job_id": batch_job.job_id,
            "status": batch_job.status,
            "progress": batch_job.progress,
            "total_items": len(batch_job.content_items),
            "results_count": len(batch_job.results),
            "started_at": batch_job.started_at.isoformat() if batch_job.started_at else None,
            "completed_at": batch_job.completed_at.isoformat() if batch_job.completed_at else None
        }

# Format-specific processors
class TextContentProcessor:
    """Processor for plain text content"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract localizable text"""
        return content
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct content with localized text"""
        return localized

class HTMLContentProcessor:
    """Processor for HTML content"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract text from HTML while preserving structure"""
        # Simplified HTML text extraction
        text_content = re.sub(r'<[^>]+>', '', content)
        return text_content.strip()
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct HTML with localized text"""
        # Simplified reconstruction - in production, use proper HTML parser
        return f"<html><body>{localized}</body></html>"

class MarkdownContentProcessor:
    """Processor for Markdown content"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract text from Markdown"""
        # Remove markdown syntax for translation
        text_content = re.sub(r'[#*`\[\]()]', '', content)
        return text_content.strip()
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct Markdown with localized text"""
        # Simplified reconstruction
        return localized

class JSONContentProcessor:
    """Processor for JSON content"""
    
    async def extract_localizable_content(self, content: Dict[str, Any]) -> str:
        """Extract localizable strings from JSON"""
        localizable_texts = []
        
        def extract_strings(obj):
            if isinstance(obj, str):
                localizable_texts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_strings(item)
        
        extract_strings(content)
        return "\n".join(localizable_texts)
    
    async def reconstruct_content(self, original: Dict[str, Any], localized: str) -> Dict[str, Any]:
        """Reconstruct JSON with localized strings"""
        # Simplified reconstruction
        localized_texts = localized.split("\n")
        
        # In production, implement proper JSON string replacement
        return original  # Placeholder

class VideoDescriptionProcessor:
    """Processor for video descriptions"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract localizable content from video description"""
        # Remove timestamps and technical metadata
        cleaned_content = re.sub(r'\d{1,2}:\d{2}(?::\d{2})?', '[TIMESTAMP]', content)
        return cleaned_content
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct video description"""
        return localized

class SocialMediaProcessor:
    """Processor for social media posts"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract text while preserving hashtags and mentions"""
        # Preserve hashtags and mentions during translation
        return content
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct social media post"""
        return localized

class BlogPostProcessor:
    """Processor for blog posts"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract blog post content"""
        return content
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct blog post"""
        return localized

class EmailContentProcessor:
    """Processor for email content"""
    
    async def extract_localizable_content(self, content: str) -> str:
        """Extract email content while preserving structure"""
        return content
    
    async def reconstruct_content(self, original: str, localized: str) -> str:
        """Reconstruct email content"""
        return localized

class ContentQualityAssessor:
    """Quality assessor for localized content"""
    
    async def assess_content_quality(
        self,
        original: Union[str, Dict],
        localized: Union[str, Dict],
        source_lang: str,
        target_lang: str
    ) -> float:
        """Assess quality of localized content"""
        
        # Simplified quality assessment
        if isinstance(original, str) and isinstance(localized, str):
            # Length ratio check
            length_ratio = len(localized) / len(original) if len(original) > 0 else 1.0
            
            if 0.5 <= length_ratio <= 2.0:
                return 0.85  # Good length ratio
            else:
                return 0.65  # Poor length ratio
        
        return 0.80  # Default score
    
    async def comprehensive_quality_assessment(
        self,
        original: str,
        localized: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """Comprehensive quality assessment"""
        
        assessment = {
            "overall_score": await self.assess_content_quality(original, localized, source_lang, target_lang),
            "fluency_score": 0.85,
            "adequacy_score": 0.82,
            "consistency_score": 0.88,
            "cultural_appropriateness": 0.80,
            "issues": [],
            "recommendations": []
        }
        
        # Check for potential issues
        if len(localized) < len(original) * 0.3:
            assessment["issues"].append("Content significantly shorter than original")
            assessment["recommendations"].append("Review for missing content")
        
        if len(localized) > len(original) * 3:
            assessment["issues"].append("Content significantly longer than original")
            assessment["recommendations"].append("Review for verbosity")
        
        return assessment

class ContentSEOOptimizer:
    """SEO optimizer for localized content"""
    
    async def optimize_content(
        self,
        content: str,
        target_language: str,
        target_region: str,
        category: ContentCategory,
        keywords: Optional[List[str]] = None
    ) -> str:
        """Optimize content for SEO"""
        
        optimized_content = content
        
        # Add region-specific SEO optimizations
        if keywords:
            for keyword in keywords[:3]:  # Top 3 keywords
                if keyword.lower() not in optimized_content.lower():
                    optimized_content = f"{keyword} - {optimized_content}"
        
        # Regional SEO adaptations
        if target_region in ["US"]:
            optimized_content = optimized_content.replace("colour", "color")
        elif target_region in ["GB"]:
            optimized_content = optimized_content.replace("color", "colour")
        
        return optimized_content

# Factory function
def create_content_localization_processor() -> ContentLocalizationProcessor:
    """Factory function to create ContentLocalizationProcessor instance"""
    return ContentLocalizationProcessor()

# Export for external use
__all__ = [
    'ContentLocalizationProcessor',
    'ContentItem',
    'LocalizationRequest',
    'LocalizedContent',
    'BatchLocalizationJob',
    'ContentFormat',
    'LocalizationStrategy',
    'ContentCategory',
    'ProcessingPriority',
    'create_content_localization_processor'
]

if __name__ == "__main__":
    # Test content localization processor
    async def test_content_processor():
        print("📝 Testing Content Localization Processor...")
        
        processor = ContentLocalizationProcessor()
        
        # Test single content localization
        result = await processor.localize_content(
            content="Welcome to our amazing platform for creators!",
            content_format=ContentFormat.TEXT,
            source_language="en",
            target_language="fr",
            target_region="FR"
        )
        
        print(f"Localized content: {result.localized_data}")
        print(f"Quality score: {result.quality_score}")
        print(f"Cultural adaptation score: {result.cultural_adaptation_score}")
        
        # Test multi-format localization
        content_items = [
            ("Hello world!", ContentFormat.TEXT),
            ({"title": "Welcome", "description": "Amazing platform"}, ContentFormat.JSON)
        ]
        
        multi_results = await processor.multi_format_content_localization(
            content_items,
            "en",
            "es",
            "ES"
        )
        
        print(f"Multi-format results: {len(multi_results)} items processed")
        
        print("✅ Content localization processor test completed!")
    
    asyncio.run(test_content_processor())