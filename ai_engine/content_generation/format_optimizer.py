"""Format Optimizer - Advanced platform-specific content formatting

Professional content formatting system that optimizes content for different
platforms, formats, and presentation requirements.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json


class FormatOptimizer:
    """
    Advanced format optimizer that adapts content for different platforms and formats:
    
    - Social media platforms (Instagram, Twitter, LinkedIn, TikTok)
    - Blog and website formats
    - Email marketing formats
    - Print and PDF formats
    - Mobile and responsive formats
    - Accessibility optimization
    - Multi-language formatting
    """
    
    def __init__(self):
        """
Initialize the format optimizer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Platform specifications
        self.platform_specs = {
            'instagram_post': {
                'max_length': 2200,
                'max_hashtags': 30,
                'line_breaks': True,
                'emojis': True,
                'optimal_length': 150,
                'engagement_elements': ['questions', 'calls_to_action']
            },
            'instagram_story': {
                'max_length': 100,
                'max_hashtags': 10,
                'line_breaks': False,
                'emojis': True,
                'optimal_length': 50,
                'engagement_elements': ['polls', 'questions']
            },
            'twitter_post': {
                'max_length': 280,
                'max_hashtags': 3,
                'line_breaks': False,
                'emojis': True,
                'optimal_length': 200,
                'engagement_elements': ['mentions', 'hashtags']
            },
            'linkedin_post': {
                'max_length': 3000,
                'max_hashtags': 5,
                'line_breaks': True,
                'emojis': False,
                'optimal_length': 1300,
                'engagement_elements': ['professional_questions', 'insights']
            },
            'tiktok_caption': {
                'max_length': 150,
                'max_hashtags': 5,
                'line_breaks': False,
                'emojis': True,
                'optimal_length': 100,
                'engagement_elements': ['trends', 'challenges']
            },
            'youtube_description': {
                'max_length': 5000,
                'max_hashtags': 15,
                'line_breaks': True,
                'emojis': True,
                'optimal_length': 200,
                'engagement_elements': ['timestamps', 'links']
            },
            'blog_post': {
                'max_length': 10000,
                'max_hashtags': 0,
                'line_breaks': True,
                'emojis': False,
                'optimal_length': 2000,
                'engagement_elements': ['headings', 'bullet_points']
            },
            'email_marketing': {
                'max_length': 1000,
                'max_hashtags': 0,
                'line_breaks': True,
                'emojis': False,
                'optimal_length': 500,
                'engagement_elements': ['personalization', 'call_to_action']
            }
        }
        
        # Format templates
        self.format_templates = {
            'social_hook': [
                "💡 Did you know that {fact}?",
                "🔥 Hot take: {opinion}",
                "✨ Pro tip: {advice}",
                "❓ Question for you: {question}",
                "🚀 Ready to {action}?"
            ],
            'blog_structure': [
                "# {title}\n\n## Introduction\n\n{intro}\n\n## Main Content\n\n{content}\n\n## Conclusion\n\n{conclusion}",
                "# {title}\n\n{hook}\n\n## Key Points\n\n{points}\n\n## Final Thoughts\n\n{conclusion}"
            ],
            'email_structure': [
                "Subject: {subject}\n\nHi {name},\n\n{opening}\n\n{main_content}\n\n{call_to_action}\n\nBest regards,\n{sender}",
                "Subject: {subject}\n\nDear {name},\n\n{personalization}\n\n{value_proposition}\n\n{social_proof}\n\n{call_to_action}\n\nSincerely,\n{sender}"
            ]
        }
        
        # Emoji mappings for different contexts
        self.emoji_mappings = {
            'positive': ['✨', '🚀', '💡', '🔥', '⭐', '🎯', '💪', '🌟'],
            'question': ['❓', '🤔', '💭', '🧠'],
            'celebration': ['🎉', '🎊', '🥳', '🏆', '🎈'],
            'warning': ['⚠️', '🚨', '⛔', '❌'],
            'professional': ['📊', '📈', '💼', '🎯', '⚡', '🔧']
        }
        
        # Alias for backward compatibility
        self.platform_rules = self.platform_specs
    
    async def optimize_format(
        self,
        content: Any,
        target_platform: str,
        optimization_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize content format for specific platform.
        
        Args:
            content: Content to optimize
            target_platform: Target platform (instagram_post, twitter_post, etc.)
            optimization_options: Specific optimization preferences
            
        Returns:
            Optimized content formatted for the target platform
        """
        try:
            # Extract text content
            text_content = self._extract_text_content(content)
            
            # Get platform specifications
            platform_spec = self.platform_specs.get(
                target_platform, 
                self.platform_specs['blog_post']
            )
            
            # Parse optimization options
            options = optimization_options or {}
            
            # Apply platform-specific optimizations
            if target_platform.startswith('instagram'):
                optimized_content = await self._optimize_for_instagram(
                    text_content, platform_spec, options
                )
            elif target_platform.startswith('twitter'):
                optimized_content = await self._optimize_for_twitter(
                    text_content, platform_spec, options
                )
            elif target_platform.startswith('linkedin'):
                optimized_content = await self._optimize_for_linkedin(
                    text_content, platform_spec, options
                )
            elif target_platform.startswith('tiktok'):
                optimized_content = await self._optimize_for_tiktok(
                    text_content, platform_spec, options
                )
            elif target_platform.startswith('youtube'):
                optimized_content = await self._optimize_for_youtube(
                    text_content, platform_spec, options
                )
            elif target_platform == 'blog_post':
                optimized_content = await self._optimize_for_blog(
                    text_content, platform_spec, options
                )
            elif target_platform == 'email_marketing':
                optimized_content = await self._optimize_for_email(
                    text_content, platform_spec, options
                )
            else:
                optimized_content = await self._optimize_general_format(
                    text_content, platform_spec, options
                )
            
            # Calculate optimization metrics
            optimization_metrics = await self._calculate_optimization_metrics(
                text_content, optimized_content, platform_spec
            )
            
            return {
                'optimized_content': optimized_content,
                'original_content': text_content,
                'platform_spec': platform_spec,
                'optimization_metrics': optimization_metrics,
                'format_changes': await self._get_format_changes(
                    text_content, optimized_content
                )
            }
            
        except Exception as e:
            self.logger.error(f"Format optimization failed: {str(e)}")
            return {
                'optimized_content': content,
                'original_content': content,
                'platform_spec': {},
                'optimization_metrics': {},
                'format_changes': []
            }
    
    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from various content types"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if 'content' in content:
                return str(content['content'])
            elif 'text' in content:
                return str(content['text'])
            elif 'body' in content:
                return str(content['body'])
            else:
                return ' '.join([str(v) for v in content.values() if isinstance(v, str)])
        else:
            return str(content)
    
    async def _optimize_for_instagram(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for Instagram"""
        optimized = content
        
        # Add engaging hook if missing
        if not self._has_engaging_hook(optimized):
            hook = await self._generate_social_hook(optimized, 'instagram')
            optimized = f"{hook}\n\n{optimized}"
        
        # Optimize length
        if len(optimized) > platform_spec['max_length']:
            optimized = await self._truncate_content(
                optimized, platform_spec['max_length'] - 50
            )
        
        # Add line breaks for readability
        optimized = await self._add_instagram_line_breaks(optimized)
        
        # Add hashtags
        hashtags = await self._generate_hashtags(optimized, platform_spec['max_hashtags'])
        if hashtags:
            optimized += f"\n\n{hashtags}"
        
        # Add emojis if enabled
        if platform_spec.get('emojis', False):
            optimized = await self._add_contextual_emojis(optimized, 'instagram')
        
        # Add engagement elements
        optimized = await self._add_engagement_elements(
            optimized, platform_spec['engagement_elements']
        )
        
        return optimized
    
    async def _optimize_for_twitter(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Optimize content for Twitter"""
        optimized = content
        
        # Ensure content fits Twitter limit
        if len(optimized) > platform_spec['max_length']:
            optimized = await self._create_twitter_thread(optimized, platform_spec)
        else:
            # Single tweet optimization
            optimized = await self._optimize_single_tweet(optimized, platform_spec)
        
        return optimized
    
    async def _optimize_for_linkedin(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for LinkedIn"""
        optimized = content
        
        # Add professional hook
        if not self._has_professional_hook(optimized):
            hook = await self._generate_professional_hook(optimized)
            optimized = f"{hook}\n\n{optimized}"
        
        # Optimize for professional tone
        optimized = await self._professionalize_tone(optimized)
        
        # Add LinkedIn-style formatting
        optimized = await self._add_linkedin_formatting(optimized)
        
        # Add professional hashtags
        hashtags = await self._generate_professional_hashtags(
            optimized, platform_spec['max_hashtags']
        )
        if hashtags:
            optimized += f"\n\n{hashtags}"
        
        return optimized
    
    async def _optimize_for_tiktok(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Optimize content for TikTok"""
        optimized = content
        
        # Keep it short and punchy
        if len(optimized) > platform_spec['max_length']:
            optimized = await self._create_punchy_caption(optimized, platform_spec)
        
        # Add trending elements
        optimized = await self._add_trending_elements(optimized)
        
        # Add TikTok-style emojis
        optimized = await self._add_contextual_emojis(optimized, 'tiktok')
        
        return optimized
    
    async def _optimize_for_youtube(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for YouTube"""
        optimized = content
        
        # Create structured description
        optimized = await self._create_youtube_description(optimized)
        
        # Add timestamps if content is long
        if len(optimized) > 500:
            optimized = await self._add_timestamps(optimized)
        
        # Add YouTube-specific CTAs
        optimized = await self._add_youtube_ctas(optimized)
        
        return optimized
    
    async def _optimize_for_blog(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for blog format"""
        optimized = content
        
        # Add proper blog structure
        optimized = await self._add_blog_structure(optimized)
        
        # Improve readability
        optimized = await self._improve_blog_readability(optimized)
        
        # Add SEO elements
        optimized = await self._add_blog_seo_elements(optimized)
        
        return optimized
    
    async def _optimize_for_email(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for email marketing"""
        optimized = content
        
        # Add email structure
        optimized = await self._add_email_structure(optimized)
        
        # Add personalization placeholders
        optimized = await self._add_personalization(optimized)
        
        # Add email-specific CTAs
        optimized = await self._add_email_ctas(optimized)
        
        return optimized
    
    async def _optimize_general_format(
        self,
        content: str,
        platform_spec: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Optimize content for general format"""
        optimized = content
        
        # Apply basic formatting improvements
        optimized = await self._apply_basic_formatting(optimized)
        
        # Ensure proper length
        if len(optimized) > platform_spec.get('max_length', 5000):
            optimized = await self._truncate_content(
                optimized, platform_spec.get('max_length', 5000)
            )
        
        return optimized
    
    def _has_engaging_hook(self, content: str) -> bool:
        """
Check if content has an engaging hook"""
        first_line = content.split('\n')[0].lower()
        hook_indicators = ['did you know', 'imagine', 'what if', '💡', '🔥', '✨']
        return any(indicator in first_line for indicator in hook_indicators)
    
    async def _generate_social_hook(self, content: str, platform: str) -> str:
        """
Generate an engaging social media hook"""
        hooks = {
            'instagram': [
                "✨ Ready to transform your perspective?",
                "💡 Here's something that might surprise you:",
                "🔥 Hot take coming your way:",
                "🚀 Let's dive into something amazing:"
            ],
            'twitter': [
                "🧵 Thread time:",
                "💭 Unpopular opinion:",
                "🔥 Hot take:",
                "💡 Quick insight:"
            ]
        }
        
        platform_hooks = hooks.get(platform, hooks['instagram'])
        return platform_hooks[0]  # Use first hook for simplicity
    
    async def _truncate_content(self, content: str, max_length: int) -> str:
        """Intelligently truncate content"""
        if len(content) <= max_length:
            return content
        
        # Try to truncate at sentence boundary
        sentences = content.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '.') <= max_length - 3:
                truncated += sentence + '.'
            else:
                break
        
        if not truncated:
            truncated = content[:max_length - 3]
        
        return truncated.strip() + "..."
    
    async def _add_instagram_line_breaks(self, content: str) -> str:
        """Add Instagram-style line breaks"""
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            sentences = paragraph.split('.')
            if len(sentences) > 2:
                # Add line breaks every 2 sentences
                formatted_sentences = []
                for i, sentence in enumerate(sentences):
                    formatted_sentences.append(sentence.strip())
                    if i > 0 and i % 2 == 0 and sentence.strip():
                        formatted_sentences.append('\n')
                formatted_paragraphs.append('.'.join(formatted_sentences))
            else:
                formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    async def _generate_hashtags(self, content: str, max_hashtags: int) -> str:
        """
Generate relevant hashtags"""
        # Extract keywords for hashtags
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Common hashtags for different topics
        common_hashtags = {
            'business': ['#business', '#entrepreneur', '#success', '#motivation'],
            'tech': ['#technology', '#innovation', '#digital', '#tech'],
            'lifestyle': ['#lifestyle', '#inspiration', '#wellness', '#mindset'],
            'marketing': ['#marketing', '#socialmedia', '#branding', '#content']
        }
        
        # Simple keyword-based hashtag generation
        hashtags = []
        if any(word in words for word in ['business', 'entrepreneur', 'success']):
            hashtags.extend(common_hashtags['business'][:max_hashtags//2])
        if any(word in words for word in ['tech', 'technology', 'digital']):
            hashtags.extend(common_hashtags['tech'][:max_hashtags//2])
        
        # Add generic hashtags if needed
        if len(hashtags) < max_hashtags:
            hashtags.extend(['#content', '#socialmedia', '#engagement'])
        
        return ' '.join(hashtags[:max_hashtags])
    
    async def _add_contextual_emojis(self, content: str, platform: str) -> str:
        """
Add contextual emojis to content"""
        content_lower = content.lower()
        
        # Add emojis based on content sentiment and context
        if any(word in content_lower for word in ['success', 'win', 'achieve']):
            content = '🎯 ' + content
        elif any(word in content_lower for word in ['idea', 'think', 'insight']):
            content = '💡 ' + content
        elif any(word in content_lower for word in ['grow', 'improve', 'better']):
            content = '🚀 ' + content
        
        return content
    
    async def _add_engagement_elements(
        self, 
        content: str, 
        elements: List[str]
    ) -> str:
        """
Add engagement elements to content"""
        enhanced = content
        
        if 'questions' in elements and '?' not in enhanced:
            enhanced += "\n\nWhat's your experience with this? Share in the comments! 👇"
        
        if 'calls_to_action' in elements:
            if not any(cta in enhanced.lower() for cta in ['follow', 'like', 'share', 'comment']):
                enhanced += "\n\n💝 Double-tap if you found this helpful!"
        
        return enhanced
    
    async def _create_twitter_thread(
        self, 
        content: str, 
        platform_spec: Dict[str, Any]
    ) -> str:
        """Create Twitter thread from long content"""
        max_tweet_length = platform_spec['max_length'] - 10  # Leave space for thread numbers
        
        sentences = content.split('.')
        tweets = []
        current_tweet = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_tweet + sentence + '.') <= max_tweet_length:
                current_tweet += sentence + '.'
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = sentence + '.'
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Format as thread
        thread = []
        for i, tweet in enumerate(tweets):
            if i == 0:
                thread.append(f"{tweet} (1/{len(tweets)})")
            else:
                thread.append(f"({i+1}/{len(tweets)}) {tweet}")
        
        return '\n\n'.join(thread)
    
    async def _optimize_single_tweet(
        self, 
        content: str, 
        platform_spec: Dict[str, Any]
    ) -> str:
        """Optimize content for single tweet"""
        optimized = content
        
        # Add Twitter-style formatting
        if not optimized.startswith(('💭', '🧵', '🔥', '💡')):
            optimized = f"💭 {optimized}"
        
        # Add hashtags if space allows
        remaining_space = platform_spec['max_length'] - len(optimized)
        if remaining_space > 20:
            hashtags = await self._generate_hashtags(optimized, 2)
            if hashtags:
                optimized += f" {hashtags}"
        
        return optimized
    
    def _has_professional_hook(self, content: str) -> bool:
        """Check if content has professional hook"""
        first_line = content.split('\n')[0].lower()
        professional_indicators = ['insight', 'analysis', 'strategy', 'industry', 'professional']
        return any(indicator in first_line for indicator in professional_indicators)
    
    async def _generate_professional_hook(self, content: str) -> str:
        """
Generate professional hook for LinkedIn"""
        hooks = [
            "💼 Professional insight:",
            "📊 Industry analysis:",
            "🎯 Strategic perspective:",
            "⚡ Business insight:"
        ]
        return hooks[0]
    
    async def _professionalize_tone(self, content: str) -> str:
        """Make content tone more professional"""
        # Replace casual words with professional alternatives
        replacements = {
            'awesome': 'excellent',
            'cool': 'impressive',
            'great': 'outstanding',
            'super': 'highly',
            'really': 'significantly'
        }
        
        professional = content
        for casual, formal in replacements.items():
            professional = re.sub(
                r'\b' + casual + r'\b', 
                formal, 
                professional, 
                flags=re.IGNORECASE
            )
        
        return professional
    
    async def _add_linkedin_formatting(self, content: str) -> str:
        """
Add LinkedIn-style formatting"""
        paragraphs = content.split('\n\n')
        
        # Add line breaks for better mobile readability
        formatted_paragraphs = []
        for paragraph in paragraphs:
            if len(paragraph) > 200:
                sentences = paragraph.split('.')
                mid_point = len(sentences) // 2
                formatted_paragraph = (
                    '.'.join(sentences[:mid_point]) + '.\n\n' +
                    '.'.join(sentences[mid_point:])
                )
                formatted_paragraphs.append(formatted_paragraph)
            else:
                formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    async def _generate_professional_hashtags(self, content: str, max_hashtags: int) -> str:
        """
Generate professional hashtags for LinkedIn"""
        professional_hashtags = [
            '#leadership', '#business', '#strategy', '#innovation',
            '#growth', '#management', '#professional', '#industry',
            '#insights', '#success', '#development', '#excellence'
        ]
        
        # Select hashtags based on content
        selected = professional_hashtags[:max_hashtags]
        return ' '.join(selected)
    
    async def _create_punchy_caption(
        self, 
        content: str, 
        platform_spec: Dict[str, Any]
    ) -> str:
        """
Create punchy TikTok caption"""
        # Extract the most engaging part
        sentences = content.split('.')
        if sentences:
            # Use first sentence as base
            punchy = sentences[0].strip()
            
            # Make it more engaging
            if not punchy.endswith(('!', '?')):
                punchy += '!'
                
            # Ensure it fits
            if len(punchy) > platform_spec['max_length']:
                punchy = punchy[:platform_spec['max_length'] - 3] + '...'
                
            return punchy
        
        return content[:platform_spec['max_length']]
    
    async def _add_trending_elements(self, content: str) -> str:
        """
Add trending elements for TikTok"""
        trending_words = ['viral', 'trending', 'POV', 'aesthetic', 'mood']
        
        if not any(word in content.lower() for word in trending_words):
            content = f"POV: {content}"
        
        return content
    
    async def _create_youtube_description(self, content: str) -> str:
        """Create structured YouTube description"""
        structure = f"""📖 {content}

🔔 SUBSCRIBE for more content like this!
👍 LIKE if this helped you
💬 COMMENT your thoughts below

📱 FOLLOW US:
• Website: [Your Website]
• Instagram: @youraccount
• Twitter: @youraccount

#YouTube #Content #Education"""
        
        return structure
    
    async def _add_timestamps(self, content: str) -> str:
        """
Add timestamps to YouTube description"""
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) > 3:
            timestamped = "📚 TIMESTAMPS:\n"
            timestamped += "0:00 Introduction\n"
            
            time_increment = 60  # 1 minute per section
            current_time = time_increment
            
            for i, paragraph in enumerate(paragraphs[1:-1], 1):
                minutes = current_time // 60
                seconds = current_time % 60
                timestamped += f"{minutes}:{seconds:02d} Section {i}\n"
                current_time += time_increment
            
            timestamped += f"\n{content}"
            return timestamped
        
        return content
    
    async def _add_youtube_ctas(self, content: str) -> str:
        """Add YouTube-specific calls to action"""
        if 'subscribe' not in content.lower():
            content += "\n\n🔔 Don't forget to SUBSCRIBE and turn on notifications!"
        
        return content
    
    async def _add_blog_structure(self, content: str) -> str:
        """Add proper blog structure"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return content
        
        # Add headers for long content
        structured = f"# {paragraphs[0]}\n\n"
        
        current_section = []
        for paragraph in paragraphs[1:]:
            current_section.append(paragraph)
            
            # Add section header every 2-3 paragraphs
            if len(current_section) >= 3:
                structured += '\n\n'.join(current_section) + '\n\n'
                current_section = []
        
        # Add remaining paragraphs
        if current_section:
            structured += '\n\n'.join(current_section)
        
        return structured
    
    async def _improve_blog_readability(self, content: str) -> str:
        """Improve blog readability"""
        # Add bullet points for lists
        lines = content.split('\n')
        improved_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith(('#', '*', '-')):
                # Check if line looks like a list item
                if any(line.strip().startswith(word) for word in ['First', 'Second', 'Third', 'Also', 'Additionally']):
                    improved_lines.append(f"• {line.strip()}")
                else:
                    improved_lines.append(line)
            else:
                improved_lines.append(line)
        
        return '\n'.join(improved_lines)
    
    async def _add_blog_seo_elements(self, content: str) -> str:
        """Add SEO elements to blog content"""
        # Add meta description comment
        seo_content = f"<!-- Meta Description: {content[:150]}... -->\n\n{content}"
        
        return seo_content
    
    async def _add_email_structure(self, content: str) -> str:
        """Add email marketing structure"""
        # Basic email template
        structured = f"""
Subject: Important Update

Hi [Name],

{content}

Best regards,
[Your Name]

---
Unsubscribe | Update Preferences | Contact Us"""
        
        return structured
    
    async def _add_personalization(self, content: str) -> str:
        """
Add personalization placeholders"""
        personalized = content.replace('you', '[Name]', 1)  # Replace first occurrence
        return personalized
    
    async def _add_email_ctas(self, content: str) -> str:
        """
Add email-specific calls to action"""
        if not any(cta in content.lower() for cta in ['click', 'visit', 'download', 'contact']):
            content += "\n\n👉 [CALL TO ACTION BUTTON]"
        
        return content
    
    async def _apply_basic_formatting(self, content: str) -> str:
        """Apply basic formatting improvements"""
        # Fix spacing
        formatted = re.sub(r'\s+', ' ', content)  # Multiple spaces
        formatted = re.sub(r'\n\s*\n\s*\n', '\n\n', formatted)  # Multiple line breaks
        
        # Ensure proper punctuation spacing
        formatted = re.sub(r'([.!?])([A-Z])', r'\1 \2', formatted)
        
        return formatted.strip()
    
    async def _calculate_optimization_metrics(
        self,
        original: str,
        optimized: str,
        platform_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Calculate optimization metrics"""
        return {
            'length_optimization': {
                'original_length': len(original),
                'optimized_length': len(optimized),
                'within_limits': len(optimized) <= platform_spec.get('max_length', float('inf')),
                'optimal_range': (
                    platform_spec.get('optimal_length', 0) * 0.8 <= 
                    len(optimized) <= 
                    platform_spec.get('optimal_length', float('inf')) * 1.2
                )
            },
            'engagement_optimization': {
                'added_emojis': len(re.findall(r'[\U0001F600-\U0001F64F]', optimized)) > len(re.findall(r'[\U0001F600-\U0001F64F]', original)),
                'added_hashtags': optimized.count('#') > original.count('#'),
                'added_questions': optimized.count('?') > original.count('?'),
                'added_calls_to_action': any(cta in optimized.lower() for cta in ['follow', 'like', 'share', 'comment', 'subscribe'])
            },
            'structure_optimization': {
                'added_line_breaks': optimized.count('\n') > original.count('\n'),
                'added_headers': optimized.count('#') > original.count('#'),
                'improved_formatting': len(optimized.split('\n\n')) > len(original.split('\n\n'))
            }
        }
    
    async def _get_format_changes(self, original: str, optimized: str) -> List[str]:
        """
Get list of format changes applied"""
        changes = []
        
        if len(optimized) != len(original):
            changes.append("Length optimization")
        
        if optimized.count('\n') > original.count('\n'):
            changes.append("Added line breaks")
        
        if optimized.count('#') > original.count('#'):
            changes.append("Added hashtags or headers")
        
        if optimized.count('?') > original.count('?'):
            changes.append("Added engagement questions")
        
        emoji_pattern = r'[\U0001F600-\U0001F64F]'
        if len(re.findall(emoji_pattern, optimized)) > len(re.findall(emoji_pattern, original)):
            changes.append("Added emojis")
        
        return changes
