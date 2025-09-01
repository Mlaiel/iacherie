"""Text Content Generator - Advanced AI text generation engine

Professional text content generator for influencers and content creators
supporting multiple formats, styles, and platforms.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import our enhanced OpenAI client
from ..ai_service_clients import OpenAIClient

from .base_generator import BaseContentGenerator, ContentGenerationContext
from .social_templates import SocialMediaTemplates
from .blog_templates import BlogTemplates
from .seo_optimizer import SEOOptimizer


class TextGenerationOptions:
    """
Configuration options for text generation"""
    
    def __init__(self, **kwargs):
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.temperature = kwargs.get('temperature', 0.7)
        self.top_p = kwargs.get('top_p', 0.9)
        self.frequency_penalty = kwargs.get('frequency_penalty', 0.1)
        self.presence_penalty = kwargs.get('presence_penalty', 0.1)
        self.stop_sequences = kwargs.get('stop_sequences', [])
        self.model_name = kwargs.get('model_name', 'gpt-4-turbo')
        self.style = kwargs.get('style', 'professional')
        self.tone = kwargs.get('tone', 'engaging')
        self.format_type = kwargs.get('format_type', 'general')
        self.target_length = kwargs.get('target_length', 'medium')
        self.include_hashtags = kwargs.get('include_hashtags', True)
        self.include_cta = kwargs.get('include_cta', True)
        self.language = kwargs.get('language', 'en')


class TextContentGenerator(BaseContentGenerator):
    """
    Advanced text content generator that creates high-quality text content
    for various platforms and purposes including:
    - Social media posts (Instagram, TikTok, Twitter, Facebook)
    - Blog articles and SEO content
    - Marketing copy and advertisements
    - Captions and descriptions
    - Email content and newsletters
    - Product descriptions
    - Scripts for audio/video content
    """
    
    def _setup_models(self) -> None:
        """
Setup AI models and dependencies"""
        try:
            # Initialize OpenAI client
            self.openai_client = openai.AsyncOpenAI(
                api_key=self.config.get('openai_api_key')
            )
            
            # Initialize tokenizer for token counting
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            # Initialize templates
            self.social_templates = SocialMediaTemplates()
            self.blog_templates = BlogTemplates()
            
            # Initialize SEO optimizer
            self.seo_optimizer = SEOOptimizer()
            
            # Supported text formats
            self.supported_formats = {
                'instagram_post', 'instagram_story', 'instagram_reel',
                'tiktok_caption', 'twitter_post', 'facebook_post',
                'youtube_description', 'blog_article', 'product_description',
                'email_newsletter', 'marketing_copy', 'script', 'hashtags'
            }
            
            self.logger.info("Text generator models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text models: {str(e)}")
            raise
    
    def _setup_resources(self) -> None:
        """Setup computational resources"""
        # Text generation doesn't require heavy computational resources
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 10)
        self.request_timeout = self.config.get('request_timeout', 60)
        
        # Rate limiting
        self.rate_limit_rpm = self.config.get('rate_limit_rpm', 100)
        self.rate_limit_tpm = self.config.get('rate_limit_tpm', 50000)
    
    def _setup_validation_rules(self) -> None:
        """
Setup content validation rules"""
        self.validation_rules = {
            'min_length': 10,
            'max_length': 10000,
            'forbidden_words': ['spam', 'fake', 'scam'],
            'required_elements': {
                'social': ['engaging_hook', 'value_proposition'],
                'blog': ['introduction', 'main_content', 'conclusion'],
                'marketing': ['headline', 'benefits', 'call_to_action']
            }
        }
    
    async def generate_content(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate text content based on context and prompt.
        
        Args:
            context: Generation context with user and platform information
            prompt: Text generation prompt
            options: Additional generation options
            
        Returns:
            Generated text content with metadata
        """
        try:
            # Parse options
            gen_options = TextGenerationOptions(**(options or {}))
            
            # Determine content format
            content_format = self._determine_content_format(context, prompt, gen_options)
            
            # Build generation prompt
            enhanced_prompt = await self._build_enhanced_prompt(
                prompt, context, gen_options, content_format
            )
            
            # Generate content using appropriate method
            if content_format in ['instagram_post', 'tiktok_caption', 'twitter_post']:
                content = await self._generate_social_content(
                    enhanced_prompt, context, gen_options, content_format
                )
            elif content_format in ['blog_article']:
                content = await self._generate_blog_content(
                    enhanced_prompt, context, gen_options
                )
            elif content_format in ['marketing_copy', 'product_description']:
                content = await self._generate_marketing_content(
                    enhanced_prompt, context, gen_options
                )
            else:
                content = await self._generate_general_content(
                    enhanced_prompt, context, gen_options
                )
            
            # Apply post-processing
            processed_content = await self._post_process_content(
                content, context, gen_options, content_format
            )
            
            return {
                'content': processed_content,
                'format': content_format,
                'metadata': {
                    'word_count': len(processed_content.split()),
                    'character_count': len(processed_content),
                    'estimated_reading_time': self._estimate_reading_time(processed_content),
                    'content_grade': await self._analyze_content_grade(processed_content),
                    'sentiment_score': await self._analyze_sentiment(processed_content),
                    'seo_score': await self._calculate_seo_score(processed_content, context)
                },
                'generation_info': {
                    'model_used': gen_options.model_name,
                    'temperature': gen_options.temperature,
                    'tokens_used': self._count_tokens(processed_content)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            raise
    
    async def validate_output(self, content: Any) -> bool:
        """
        Validate generated text content.
        
        Args:
            content: Generated text content to validate
            
        Returns:
            True if content meets quality standards
        """
        if not isinstance(content, dict):
            return False
        
        text_content = content.get('content', '')
        if not text_content or not isinstance(text_content, str):
            return False
        
        # Check length constraints
        if len(text_content) < self.validation_rules['min_length']:
            return False
        
        if len(text_content) > self.validation_rules['max_length']:
            return False
        
        # Check for forbidden content
        text_lower = text_content.lower()
        for forbidden_word in self.validation_rules['forbidden_words']:
            if forbidden_word in text_lower:
                return False
        
        # Check content quality
        if await self._check_content_quality(text_content):
            return True
        
        return False
    
    def _determine_content_format(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: TextGenerationOptions
    ) -> str:
        """
Determine the appropriate content format"""
        # Check explicit format in options
        if options.format_type and options.format_type in self.supported_formats:
            return options.format_type
        
        # Infer from platform requirements
        if context.platform_requirements:
            platform = context.platform_requirements.get('platform', '').lower()
            if 'instagram' in platform:
                return 'instagram_post'
            elif 'tiktok' in platform:
                return 'tiktok_caption'
            elif 'twitter' in platform:
                return 'twitter_post'
            elif 'facebook' in platform:
                return 'facebook_post'
            elif 'youtube' in platform:
                return 'youtube_description'
        
        # Infer from prompt content
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['blog', 'article', 'post']):
            return 'blog_article'
        elif any(word in prompt_lower for word in ['caption', 'instagram']):
            return 'instagram_post'
        elif any(word in prompt_lower for word in ['tweet', 'twitter']):
            return 'twitter_post'
        elif any(word in prompt_lower for word in ['product', 'description']):
            return 'product_description'
        
        return 'general'
    
    async def _build_enhanced_prompt(
        self,
        base_prompt: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions,
        content_format: str
    ) -> str:
        """
Build enhanced prompt with context and formatting instructions"""
        # Get format-specific template
        if content_format in ['instagram_post', 'tiktok_caption', 'twitter_post']:
            template = self.social_templates.get_template(content_format)
        elif content_format == 'blog_article':
            template = self.blog_templates.get_article_template()
        else:
            template = self._get_general_template(content_format)
        
        # Build context information
        context_info = []
        
        if context.target_audience:
            context_info.append(f"Target Audience: {context.target_audience}")
        
        if context.brand_guidelines:
            brand_voice = context.brand_guidelines.get('voice', 'professional')
            context_info.append(f"Brand Voice: {brand_voice}")
        
        if context.platform_requirements:
            platform_info = context.platform_requirements
            if 'character_limit' in platform_info:
                context_info.append(f"Character Limit: {platform_info['character_limit']}")
            if 'hashtag_limit' in platform_info:
                context_info.append(f"Hashtag Limit: {platform_info['hashtag_limit']}")
        
        # Build style instructions
        style_instructions = [
            f"Style: {options.style}",
            f"Tone: {options.tone}",
            f"Language: {options.language}",
            f"Target Length: {options.target_length}"
        ]
        
        if options.include_hashtags:
            style_instructions.append("Include relevant hashtags")
        
        if options.include_cta:
            style_instructions.append("Include call-to-action")
        
        # Combine all elements
        enhanced_prompt = f"""{template}

CONTEXT:
{chr(10).join(context_info)}

STYLE INSTRUCTIONS:
{chr(10).join(style_instructions)}

CONTENT REQUEST:
{base_prompt}

Please generate high-quality, engaging content that follows the template structure and meets all specified requirements.
"""
        
        return enhanced_prompt.strip()
    
    async def _generate_social_content(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions,
        format_type: str
    ) -> str:
        """
Generate social media specific content"""
        # Adjust parameters for social content
        social_options = {
            'model': options.model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert social media content creator specializing in engaging, viral content for influencers.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': min(options.max_tokens, 500),  # Social content is typically shorter
            'temperature': options.temperature,
            'top_p': options.top_p,
            'frequency_penalty': options.frequency_penalty,
            'presence_penalty': options.presence_penalty
        }
        
        response = await self.openai_client.chat.completions.create(**social_options)
        return response.choices[0].message.content.strip()
    
    async def _generate_blog_content(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions
    ) -> str:
        """
Generate blog article content"""
        blog_options = {
            'model': options.model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert content writer specializing in SEO-optimized blog articles and long-form content.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': options.max_tokens,
            'temperature': max(0.3, options.temperature - 0.2),  # Slightly lower temperature for articles
            'top_p': options.top_p,
            'frequency_penalty': options.frequency_penalty,
            'presence_penalty': options.presence_penalty
        }
        
        response = await self.openai_client.chat.completions.create(**blog_options)
        return response.choices[0].message.content.strip()
    
    async def _generate_marketing_content(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions
    ) -> str:
        """
Generate marketing and sales content"""
        marketing_options = {
            'model': options.model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert copywriter specializing in persuasive marketing content and sales copy.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': options.max_tokens,
            'temperature': options.temperature,
            'top_p': options.top_p,
            'frequency_penalty': options.frequency_penalty,
            'presence_penalty': options.presence_penalty
        }
        
        response = await self.openai_client.chat.completions.create(**marketing_options)
        return response.choices[0].message.content.strip()
    
    async def _generate_general_content(
        self,
        prompt: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions
    ) -> str:
        """
Generate general text content"""
        general_options = {
            'model': options.model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert content writer capable of creating high-quality text content for any purpose.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': options.max_tokens,
            'temperature': options.temperature,
            'top_p': options.top_p,
            'frequency_penalty': options.frequency_penalty,
            'presence_penalty': options.presence_penalty
        }
        
        response = await self.openai_client.chat.completions.create(**general_options)
        return response.choices[0].message.content.strip()
    
    async def _post_process_content(
        self,
        content: str,
        context: ContentGenerationContext,
        options: TextGenerationOptions,
        format_type: str
    ) -> str:
        """
Apply post-processing to generated content"""
        processed = content
        
        # Apply format-specific processing
        if format_type in ['instagram_post', 'tiktok_caption']:
            processed = await self._process_social_content(processed, options)
        elif format_type == 'blog_article':
            processed = await self._process_blog_content(processed, context)
        
        # Apply general improvements
        processed = await self._apply_general_improvements(processed, context)
        
        return processed
    
    async def _process_social_content(self, content: str, options: TextGenerationOptions) -> str:
        """
Process social media content"""
        # Ensure proper hashtag formatting
        if options.include_hashtags and '#' not in content:
            # Add relevant hashtags if none present
            content += "\n\n#content #creator #influencer"
        
        # Ensure emojis are properly spaced
        content = content.replace('  ', ' ').strip()
        
        return content
    
    async def _process_blog_content(self, content: str, context: ContentGenerationContext) -> str:
        """Process blog article content"""
        # Apply SEO optimization
        if hasattr(self, 'seo_optimizer'):
            content = await self.seo_optimizer.optimize_content(content, 'blog', context)
        
        return content
    
    async def _apply_general_improvements(self, content: str, context: ContentGenerationContext) -> str:
        """
Apply general content improvements"""
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Ensure proper sentence spacing
        content = content.replace(' .', '.').replace(' ,', ',')
        
        # Apply brand-specific formatting if available
        if context.brand_guidelines:
            # Apply brand-specific formatting rules
            pass
        
        return content
    
    def _get_general_template(self, format_type: str) -> str:
        """
Get general template for content format"""
        templates = {
            'general': "Create engaging, high-quality content that provides value to the reader.",
            'script': "Write a compelling script with clear structure: introduction, main content, and conclusion.",
            'email': "Write a professional email with clear subject, greeting, body, and call-to-action.",
            'product_description': "Create a compelling product description highlighting key features and benefits."
        }
        
        return templates.get(format_type, templates['general'])
    
    def _estimate_reading_time(self, content: str) -> float:
        """Estimate reading time in minutes"""
        word_count = len(content.split())
        # Average reading speed: 200-250 words per minute
        return round(word_count / 225, 1)
    
    async def _analyze_content_grade(self, content: str) -> str:
        """
Analyze content readability grade"""
        # Simplified readability analysis
        sentences = content.count('.') + content.count('!') + content.count('?')
        words = len(content.split())
        
        if sentences == 0:
            return "Unknown"
        
        avg_sentence_length = words / sentences
        
        if avg_sentence_length < 15:
            return "Easy"
        elif avg_sentence_length < 25:
            return "Medium"
        else:
            return "Difficult"
    
    async def _analyze_sentiment(self, content: str) -> float:
        """Analyze content sentiment (simplified)"""
        # This is a simplified sentiment analysis
        # In production, use proper sentiment analysis models
        positive_words = ['great', 'amazing', 'excellent', 'wonderful', 'fantastic', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate', 'horrible']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.5  # Neutral
        
        return positive_count / total_sentiment_words
    
    async def _calculate_seo_score(self, content: str, context: ContentGenerationContext) -> float:
        """
Calculate basic SEO score"""
        score = 0.5  # Base score
        
        # Check content length (good for SEO)
        word_count = len(content.split())
        if 300 <= word_count <= 2000:
            score += 0.2
        
        # Check for target keywords if available
        if context.metadata and 'keywords' in context.metadata:
            keywords = context.metadata['keywords']
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    score += 0.1
        
        # Check for proper structure (headings, etc.)
        if any(marker in content for marker in ['#', '##', '###']):
            score += 0.1
        
        return min(1.0, score)
    
    async def _check_content_quality(self, content: str) -> bool:
        """
Check overall content quality"""
        # Basic quality checks
        word_count = len(content.split())
        
        # Check minimum quality thresholds
        if word_count < 10:
            return False
        
        # Check for coherent sentences
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences == 0 and word_count > 20:
            return False
        
        # Check for excessive repetition
        words = content.lower().split()
        unique_words = set(words)
        if len(unique_words) < len(words) * 0.3:  # Less than 30% unique words
            return False
        
        return True
    
    def _count_tokens(self, text: str) -> int:
        """
Count tokens in text"""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback to word count approximation
            return len(text.split()) * 1.3
    
    def _supports_content_type(self, content_type: str) -> bool:
        """
Check if generator supports the specified content type"""
        return content_type == 'text'
    
    def _validate_generated_content(self, content: str) -> Dict[str, Any]:
        """
Validate generated content against rules"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 0.8
        }
        
        # Basic validation rules
        if len(content.strip()) < 10:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Content too short")
        
        if len(content) > 10000:
            validation_result['warnings'].append("Content very long")
        
        # Check for inappropriate content (mock)
        inappropriate_words = ['spam', 'scam', 'fake']
        if any(word in content.lower() for word in inappropriate_words):
            validation_result['is_valid'] = False
            validation_result['errors'].append("Inappropriate content detected")
        
        return validation_result
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return {
            'provider': 'openai',
            'model_name': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9
        }
    
    def update_model_config(self, config: Dict[str, Any]) -> bool:
        """
Update model configuration"""
        try:
            # Mock implementation - would update actual config
            self.logger.info(f"Model config updated: {config}")
            return True
        except Exception:
            return False
    
    def add_template(self, template_name: str, template_content: str) -> bool:
        """Add a content template"""
        try:
            if not hasattr(self, 'templates'):
                self.templates = {}
            self.templates[template_name] = template_content
            return True
        except Exception:
            return False
    
    def get_post_processors(self) -> List[str]:
        """
Get list of available post processors"""
        return ['grammar_check', 'spell_check', 'seo_optimize', 'readability_enhance']
    
    def get_writing_styles(self) -> List[str]:
        """
Get available writing styles"""
        return [
            "professional", "casual", "formal", "conversational",
            "persuasive", "informative", "creative", "technical",
            "friendly", "authoritative", "humorous", "inspirational"
        ]
    
    def get_content_types(self) -> List[str]:
        """Get supported content types"""
        return [
            "blog_post", "social_media", "email", "article",
            "product_description", "press_release", "newsletter",
            "advertisement", "script", "caption", "review"
        ]
    
    async def check_grammar(self, text: str) -> Dict[str, Any]:
        """Check grammar and return suggestions"""
        try:
            # Simulate grammar checking
            await asyncio.sleep(0.1)
            
            # Mock grammar issues detection
            issues = []
            if "there" in text.lower() and "their" not in text.lower():
                issues.append({
                    "type": "grammar",
                    "message": "Check 'there/their/they're' usage",
                    "suggestion": "Verify correct usage",
                    "position": text.lower().find("there")
                })
            
            if text.count('.') == 0 and len(text) > 50:
                issues.append({
                    "type": "punctuation",
                    "message": "Missing punctuation",
                    "suggestion": "Add periods or appropriate punctuation",
                    "position": len(text)
                })
            
            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "score": max(0, 100 - len(issues) * 10),
                "suggestions": [issue["suggestion"] for issue in issues]
            }
            
        except Exception as e:
            self.logger.error(f"Grammar check failed: {str(e)}")
            return {"is_valid": True, "issues": [], "score": 100, "suggestions": []}
    
    async def check_readability(self, text: str) -> Dict[str, Any]:
        """Check text readability and return metrics"""
        try:
            # Calculate basic readability metrics
            words = len(text.split())
            sentences = text.count('.') + text.count('!') + text.count('?')
            sentences = max(1, sentences)  # Avoid division by zero
            
            # Average sentence length
            avg_sentence_length = words / sentences
            
            # Simple readability score (mock Flesch score)
            if avg_sentence_length <= 10:
                readability_score = 90
                level = "Very Easy"
            elif avg_sentence_length <= 15:
                readability_score = 80
                level = "Easy"
            elif avg_sentence_length <= 20:
                readability_score = 70
                level = "Fairly Easy"
            elif avg_sentence_length <= 25:
                readability_score = 60
                level = "Standard"
            else:
                readability_score = 50
                level = "Difficult"
            
            return {
                "score": readability_score,
                "level": level,
                "metrics": {
                    "word_count": words,
                    "sentence_count": sentences,
                    "avg_sentence_length": round(avg_sentence_length, 1),
                    "syllable_count": words * 1.5,  # Mock syllable count
                    "paragraph_count": text.count('\n\n') + 1
                },
                "suggestions": [
                    "Use shorter sentences" if avg_sentence_length > 20 else "Good sentence length",
                    "Add more paragraphs" if text.count('\n\n') == 0 and words > 100 else "Good paragraph structure"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Readability check failed: {str(e)}")
            return {"score": 70, "level": "Standard", "metrics": {}, "suggestions": []}
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction (in real implementation, use NLP)
            import re
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
                'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
                'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
            }
            
            # Extract words (alphanumeric only)
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            
            # Filter out stop words and short words
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Count frequency
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_keywords[:max_keywords]]
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def generate_hashtags(self, text: str, max_hashtags: int = 10) -> List[str]:
        """Generate relevant hashtags for text content"""
        try:
            # Extract keywords first
            keywords = await self.extract_keywords(text, max_hashtags * 2)
            
            # Generate hashtags from keywords
            hashtags = []
            for keyword in keywords[:max_hashtags]:
                # Clean keyword for hashtag use
                clean_keyword = ''.join(c for c in keyword if c.isalnum())
                if len(clean_keyword) > 2:
                    hashtags.append(f"#{clean_keyword}")
            
            # Add some common/trending hashtags based on content
            text_lower = text.lower()
            if any(word in text_lower for word in ['marketing', 'business', 'strategy']):
                hashtags.extend(['#marketing', '#business', '#strategy'])
            if any(word in text_lower for word in ['content', 'social', 'media']):
                hashtags.extend(['#content', '#socialmedia', '#digitalmarketing'])
            if any(word in text_lower for word in ['tips', 'advice', 'guide']):
                hashtags.extend(['#tips', '#advice', '#howto'])
            
            # Remove duplicates and limit to max_hashtags
            return list(dict.fromkeys(hashtags))[:max_hashtags]
            
        except Exception as e:
            self.logger.error(f"Hashtag generation failed: {str(e)}")
            return ['#content', '#social', '#marketing']
    
    async def summarize_text(self, text: str, target_length: int = 100) -> str:
        """Generate a summary of the given text"""
        try:
            # Simple extractive summarization
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if not sentences:
                return ""
            
            # If text is already short, return as is
            if len(text) <= target_length:
                return text
            
            # Score sentences by word frequency (simple approach)
            word_freq = {}
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                score = 0
                words_in_sentence = sentence.lower().split()
                for word in words_in_sentence:
                    if word in word_freq:
                        score += word_freq[word]
                sentence_scores[i] = score / len(words_in_sentence) if words_in_sentence else 0
            
            # Select top sentences
            sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Build summary
            summary = ""
            for sentence_idx, score in sorted_sentences:
                if len(summary) + len(sentences[sentence_idx]) > target_length:
                    break
                summary += sentences[sentence_idx] + ". "
            
            return summary.strip()
            
        except Exception as e:
            self.logger.error(f"Text summarization failed: {str(e)}")
            return text[:target_length] + "..." if len(text) > target_length else text
    
    def _calculate_content_score(self, content: str, metrics: Dict[str, Any]) -> float:
        """Calculate overall content quality score"""
        try:
            score = 0.0
            
            # Length score (optimal length gets higher score)
            length = len(content)
            if 100 <= length <= 2000:
                score += 25
            elif 50 <= length < 100 or 2000 < length <= 3000:
                score += 15
            else:
                score += 5
            
            # Readability score
            if 'readability_score' in metrics:
                score += min(25, metrics['readability_score'] / 4)
            
            # Grammar score
            if 'grammar_score' in metrics:
                score += min(25, metrics['grammar_score'] / 4)
            
            # Engagement elements
            if any(char in content for char in '!?'):
                score += 5  # Has engaging punctuation
            
            if content.count('\n') > 0:
                score += 5  # Has paragraphs
            
            # SEO elements
            if 'seo_score' in metrics:
                score += min(20, metrics['seo_score'] / 5)
            
            return min(100.0, score)
            
        except Exception:
            return 70.0  # Default score
    
    async def _release_model_resources(self) -> None:
        """
Release model-specific resources"""
        # Close OpenAI client connections if needed
        if hasattr(self.openai_client, 'close'):
            await self.openai_client.close()
        
        self.logger.info("Text generator resources released")

    # Enhanced AI Generation Methods with GPT-4 and Multilingual Support
    
    async def generate_multilingual_content(
        self,
        prompt: str,
        target_language: str = 'en',
        content_type: str = 'social',
        cultural_adaptation: bool = True,
        context: Optional[ContentGenerationContext] = None
    ) -> Dict[str, Any]:
        """
        Generate content in specific language with cultural adaptation.
        
        Args:
            prompt: Content description or prompt
            target_language: ISO language code (en, fr, es, de, etc.)
            content_type: Type of content (social, blog, marketing, email)
            cultural_adaptation: Whether to adapt for local culture
            context: Generation context
            
        Returns:
            Dictionary with generated multilingual content
        """
        try:
            if not hasattr(self, 'openai_client') or not self.openai_client.is_available():
                return await self._generate_fallback_content(prompt, context)
            
            # Determine appropriate tone and style for content type
            tone_mapping = {
                'social': 'casual',
                'blog': 'professional', 
                'marketing': 'persuasive',
                'email': 'friendly',
                'formal': 'formal'
            }
            
            tone = tone_mapping.get(content_type, 'professional')
            
            # Generate content with GPT-4
            result = await self.openai_client.generate_text(
                prompt=prompt,
                language=target_language,
                tone=tone,
                style=content_type,
                audience='general',
                max_tokens=1000
            )
            
            if result['success']:
                content = result['content']
                
                # Apply cultural adaptation if requested
                if cultural_adaptation and target_language != 'en':
                    # Map language to culture codes
                    culture_map = {
                        'fr': 'FR', 'es': 'ES', 'de': 'DE', 'it': 'IT',
                        'pt': 'BR', 'ja': 'JP', 'ko': 'KR', 'zh': 'CN'
                    }
                    
                    if target_language in culture_map:
                        adaptation_result = await self.openai_client.adapt_content_culturally(
                            content=content,
                            target_culture=culture_map[target_language],
                            content_type=content_type
                        )
                        
                        if adaptation_result['success']:
                            content = adaptation_result['adapted_content']
                
                return {
                    'success': True,
                    'content': content,
                    'language': target_language,
                    'content_type': content_type,
                    'cultural_adaptation': cultural_adaptation,
                    'metadata': result['metadata'],
                    'quality_score': 90  # High score for GPT-4 content
                }
            else:
                return await self._generate_fallback_content(prompt, context)
                
        except Exception as e:
            self.logger.error(f"Multilingual content generation failed: {e}")
            return await self._generate_fallback_content(prompt, context)

    async def translate_and_adapt_content(
        self,
        content: str,
        source_language: str,
        target_language: str,
        preserve_style: bool = True,
        cultural_adaptation: bool = True
    ) -> Dict[str, Any]:
        """
        Translate existing content to target language with cultural adaptation.
        
        Args:
            content: Content to translate
            source_language: Source language code
            target_language: Target language code
            preserve_style: Whether to maintain original style
            cultural_adaptation: Whether to adapt culturally
            
        Returns:
            Dictionary with translated and adapted content
        """
        try:
            if not hasattr(self, 'openai_client') or not self.openai_client.is_available():
                return {
                    'success': False,
                    'error': 'Advanced translation not available',
                    'translated_content': content,
                    'metadata': {}
                }
            
            # First translate the content
            translation_result = await self.openai_client.translate_content(
                content=content,
                target_language=target_language,
                source_language=source_language,
                preserve_style=preserve_style
            )
            
            if not translation_result['success']:
                return translation_result
            
            translated_content = translation_result['translated_content']
            
            # Apply cultural adaptation if requested
            if cultural_adaptation:
                culture_map = {
                    'fr': 'FR', 'es': 'ES', 'de': 'DE', 'it': 'IT',
                    'pt': 'BR', 'ja': 'JP', 'ko': 'KR', 'zh': 'CN'
                }
                
                if target_language in culture_map:
                    adaptation_result = await self.openai_client.adapt_content_culturally(
                        content=translated_content,
                        target_culture=culture_map[target_language],
                        content_type='general'
                    )
                    
                    if adaptation_result['success']:
                        translated_content = adaptation_result['adapted_content']
            
            return {
                'success': True,
                'translated_content': translated_content,
                'source_language': source_language,
                'target_language': target_language,
                'preserve_style': preserve_style,
                'cultural_adaptation': cultural_adaptation,
                'metadata': translation_result['metadata']
            }
            
        except Exception as e:
            self.logger.error(f"Content translation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'translated_content': content,
                'metadata': {}
            }

    async def generate_social_media_captions(
        self,
        image_description: str,
        platform: str = 'instagram',
        language: str = 'en',
        hashtags: bool = True,
        call_to_action: bool = True,
        brand_voice: str = 'friendly'
    ) -> Dict[str, Any]:
        """
        Generate optimized social media captions with GPT-4.
        
        Args:
            image_description: Description of the image/video content
            platform: Social media platform (instagram, tiktok, facebook, twitter)
            language: Target language for caption
            hashtags: Whether to include relevant hashtags
            call_to_action: Whether to include call-to-action
            brand_voice: Brand voice tone
            
        Returns:
            Dictionary with generated caption and suggestions
        """
        try:
            if not hasattr(self, 'openai_client') or not self.openai_client.is_available():
                return await self._generate_fallback_social_caption(image_description, platform)
            
            # Platform-specific prompt engineering
            platform_guidelines = {
                'instagram': "Create an engaging Instagram caption that's 1-3 sentences, uses emojis naturally, and encourages engagement.",
                'tiktok': "Create a short, trendy TikTok caption that's catchy, uses relevant slang, and encourages views and shares.",
                'facebook': "Create a Facebook post that's conversational, storytelling-focused, and encourages comments and shares.",
                'twitter': "Create a concise Twitter post under 280 characters that's witty, informative, or engaging.",
                'linkedin': "Create a professional LinkedIn post that's informative, industry-relevant, and encourages professional engagement."
            }
            
            prompt = f"""
            Create a {platform} caption for content showing: {image_description}
            
            Guidelines: {platform_guidelines.get(platform, platform_guidelines['instagram'])}
            Brand voice: {brand_voice}
            Include hashtags: {hashtags}
            Include call-to-action: {call_to_action}
            """
            
            result = await self.openai_client.generate_text(
                prompt=prompt,
                language=language,
                tone=brand_voice,
                style='social',
                audience='social_media',
                max_tokens=300
            )
            
            if result['success']:
                caption = result['content']
                
                # Extract hashtags if included
                hashtag_list = []
                if hashtags and '#' in caption:
                    hashtag_list = [word for word in caption.split() if word.startswith('#')]
                
                return {
                    'success': True,
                    'caption': caption,
                    'platform': platform,
                    'language': language,
                    'hashtags': hashtag_list,
                    'brand_voice': brand_voice,
                    'metadata': result['metadata'],
                    'character_count': len(caption)
                }
            else:
                return await self._generate_fallback_social_caption(image_description, platform)
                
        except Exception as e:
            self.logger.error(f"Social media caption generation failed: {e}")
            return await self._generate_fallback_social_caption(image_description, platform)

    async def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze content quality using GPT-4 and provide improvement suggestions.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with quality analysis and suggestions
        """
        try:
            if not hasattr(self, 'openai_client') or not self.openai_client.is_available():
                return {
                    'success': False,
                    'error': 'Content quality analysis not available',
                    'analysis': {},
                    'suggestions': []
                }
            
            return await self.openai_client.check_content_quality(content)
            
        except Exception as e:
            self.logger.error(f"Content quality analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': {},
                'suggestions': []
            }

    async def _generate_fallback_content(self, prompt: str, context: Optional[ContentGenerationContext] = None) -> Dict[str, Any]:
        """Generate basic fallback content when advanced AI is not available."""
        return {
            'success': True,
            'content': f"Generated content based on: {prompt}",
            'language': 'en',
            'content_type': 'general',
            'metadata': {'fallback': True, 'timestamp': datetime.utcnow().isoformat()},
            'quality_score': 60
        }

    async def _generate_fallback_social_caption(self, description: str, platform: str) -> Dict[str, Any]:
        """Generate basic fallback social caption."""
        caption = f"Check out this amazing {description}! #{platform} #content"
        return {
            'success': True,
            'caption': caption,
            'platform': platform,
            'language': 'en',
            'hashtags': [f'#{platform}', '#content'],
            'metadata': {'fallback': True},
            'character_count': len(caption)
        }
