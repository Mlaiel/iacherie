"""
Content Processors Module for IA Influencer Agent Platform

Advanced content processing capabilities for multi-format content handling,
text preprocessing, and content optimization for creators and influencers.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - Unauthorized use prohibited 
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import unicodedata
import html
from urllib.parse import urlparse
import markdown
from bs4 import BeautifulSoup
import ftfy  # Fix text encoding issues

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of content processing"""
    original_content: str
    processed_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_steps: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ContentProcessor(ABC):
    """Abstract base class for content processors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process content and return result"""
        pass
    
    def _log_processing_step(self, step: str, result: ProcessingResult):
        """Log processing step"""
        result.processing_steps.append(f"{self.name}: {step}")
        logger.debug(f"{self.name} - {step}")

class TextNormalizer(ContentProcessor):
    """
    Advanced text normalization processor
    
    Handles:
    - Unicode normalization
    - Encoding fixes
    - Character cleanup
    - Whitespace normalization
    """
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        result = ProcessingResult(original_content=content, processed_content=content)
        metadata = metadata or {}
        
        try:
            # Fix encoding issues
            content = ftfy.fix_text(content)
            self._log_processing_step("Fixed text encoding", result)
            
            # Unicode normalization
            content = unicodedata.normalize('NFKC', content)
            self._log_processing_step("Unicode normalization", result)
            
            # HTML entity decoding
            content = html.unescape(content)
            self._log_processing_step("HTML entity decoding", result)
            
            # Remove zero-width characters
            content = re.sub(r'[\u200b-\u200d\ufeff]', '', content)
            self._log_processing_step("Removed zero-width characters", result)
            
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            self._log_processing_step("Whitespace normalization", result)
            
            result.processed_content = content
            result.metadata.update({
                'original_length': len(result.original_content),
                'processed_length': len(content),
                'compression_ratio': len(content) / max(len(result.original_content), 1)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            result.processed_content = result.original_content
            result.metadata['error'] = str(e)
            return result

class SocialMediaProcessor(ContentProcessor):
    """
    Social media content processor
    
    Handles:
    - Hashtag extraction and normalization
    - Mention extraction
    - URL extraction and validation
    - Emoji processing
    - Social media specific cleanup
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.hashtag_pattern = re.compile(r'#(\w+)')
        self.mention_pattern = re.compile(r'@(\w+)')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002700-\U000027BF]')
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        result = ProcessingResult(original_content=content, processed_content=content)
        metadata = metadata or {}
        
        try:
            # Extract hashtags
            hashtags = self.hashtag_pattern.findall(content)
            result.metadata['hashtags'] = list(set(hashtags))
            self._log_processing_step(f"Extracted {len(hashtags)} hashtags", result)
            
            # Extract mentions
            mentions = self.mention_pattern.findall(content)
            result.metadata['mentions'] = list(set(mentions))
            self._log_processing_step(f"Extracted {len(mentions)} mentions", result)
            
            # Extract URLs
            urls = self.url_pattern.findall(content)
            result.metadata['urls'] = list(set(urls))
            self._log_processing_step(f"Extracted {len(urls)} URLs", result)
            
            # Extract emojis
            emojis = self.emoji_pattern.findall(content)
            result.metadata['emojis'] = list(set(emojis))
            result.metadata['emoji_count'] = len(emojis)
            self._log_processing_step(f"Extracted {len(emojis)} emojis", result)
            
            # Clean content for text analysis (optional)
            if self.config.get('clean_for_analysis', False):
                cleaned_content = content
                # Remove URLs
                cleaned_content = self.url_pattern.sub('', cleaned_content)
                # Normalize hashtags (keep text, remove #)
                cleaned_content = self.hashtag_pattern.sub(r'\1', cleaned_content)
                # Remove mentions for privacy
                cleaned_content = self.mention_pattern.sub('', cleaned_content)
                
                result.processed_content = cleaned_content.strip()
                self._log_processing_step("Cleaned content for analysis", result)
            
            # Calculate social media engagement metrics
            result.metadata['social_metrics'] = self._calculate_social_metrics(content)
            
            return result
            
        except Exception as e:
            logger.error(f"Social media processing failed: {str(e)}")
            result.processed_content = result.original_content
            result.metadata['error'] = str(e)
            return result
    
    def _calculate_social_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate social media specific metrics"""
        words = content.split()
        
        return {
            'hashtag_density': len(self.hashtag_pattern.findall(content)) / max(len(words), 1),
            'mention_density': len(self.mention_pattern.findall(content)) / max(len(words), 1),
            'url_density': len(self.url_pattern.findall(content)) / max(len(words), 1),
            'emoji_density': len(self.emoji_pattern.findall(content)) / max(len(content), 1),
            'engagement_potential': self._calculate_engagement_potential(content),
            'virality_score': self._calculate_virality_score(content)
        }
    
    def _calculate_engagement_potential(self, content: str) -> float:
        """Calculate potential for social media engagement"""
        engagement_triggers = [
            'what', 'how', 'why', 'when', 'where', 'who',
            'amazing', 'incredible', 'unbelievable', 'shocking',
            'tips', 'secrets', 'hack', 'trick',
            'love', 'hate', 'feel', 'think', 'believe'
        ]
        
        words = content.lower().split()
        trigger_count = sum(1 for word in words if word in engagement_triggers)
        
        # Normalize by content length
        base_score = trigger_count / max(len(words), 1)
        
        # Boost for questions
        question_boost = 1.5 if '?' in content else 1.0
        
        # Boost for calls to action
        cta_words = ['comment', 'share', 'like', 'follow', 'subscribe', 'click', 'watch']
        cta_boost = 1.3 if any(word in content.lower() for word in cta_words) else 1.0
        
        return min(1.0, base_score * question_boost * cta_boost)
    
    def _calculate_virality_score(self, content: str) -> float:
        """Calculate potential for viral spread"""
        viral_indicators = [
            'breaking', 'exclusive', 'leaked', 'revealed',
            'crazy', 'insane', 'wild', 'epic',
            'never', 'always', 'everyone', 'nobody',
            'secret', 'hidden', 'exposed', 'truth'
        ]
        
        words = content.lower().split()
        viral_count = sum(1 for word in words if word in viral_indicators)
        
        # Base virality from indicators
        base_virality = viral_count / max(len(words), 1)
        
        # Emotional intensity boost
        emotional_words = ['love', 'hate', 'angry', 'excited', 'shocked', 'amazed']
        emotion_boost = 1.4 if any(word in content.lower() for word in emotional_words) else 1.0
        
        # Urgency boost
        urgency_words = ['now', 'today', 'urgent', 'breaking', 'alert']
        urgency_boost = 1.2 if any(word in content.lower() for word in urgency_words) else 1.0
        
        return min(1.0, base_virality * emotion_boost * urgency_boost)

class MarkdownProcessor(ContentProcessor):
    """
    Markdown content processor
    
    Handles:
    - Markdown parsing and conversion
    - Structure extraction
    - Link validation
    - Code block processing
    """
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        result = ProcessingResult(original_content=content, processed_content=content)
        metadata = metadata or {}
        
        try:
            # Parse markdown
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract structure
            headers = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            result.metadata['headers'] = headers
            result.metadata['header_count'] = len(headers)
            self._log_processing_step(f"Extracted {len(headers)} headers", result)
            
            # Extract links
            links = [(a.get_text(), a.get('href')) for a in soup.find_all('a', href=True)]
            result.metadata['links'] = links
            result.metadata['link_count'] = len(links)
            self._log_processing_step(f"Extracted {len(links)} links", result)
            
            # Extract code blocks
            code_blocks = [code.get_text() for code in soup.find_all('code')]
            result.metadata['code_blocks'] = code_blocks
            result.metadata['code_block_count'] = len(code_blocks)
            self._log_processing_step(f"Extracted {len(code_blocks)} code blocks", result)
            
            # Extract images
            images = [(img.get('alt', ''), img.get('src', '')) for img in soup.find_all('img')]
            result.metadata['images'] = images
            result.metadata['image_count'] = len(images)
            self._log_processing_step(f"Extracted {len(images)} images", result)
            
            # Convert to plain text for analysis
            plain_text = soup.get_text()
            result.processed_content = plain_text
            
            # Calculate document structure metrics
            result.metadata['document_metrics'] = self._calculate_document_metrics(content, soup)
            
            return result
            
        except Exception as e:
            logger.error(f"Markdown processing failed: {str(e)}")
            result.processed_content = result.original_content
            result.metadata['error'] = str(e)
            return result
    
    def _calculate_document_metrics(self, markdown_content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Calculate document structure and quality metrics"""
        lines = markdown_content.split('\n')
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'paragraph_count': len(soup.find_all('p')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table')),
            'blockquote_count': len(soup.find_all('blockquote')),
            'structure_complexity': self._calculate_structure_complexity(soup),
            'readability_structure': self._assess_readability_structure(soup)
        }
    
    def _calculate_structure_complexity(self, soup: BeautifulSoup) -> float:
        """Calculate document structure complexity"""
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table'])
        
        if not elements:
            return 0.0
        
        # Assign complexity weights
        complexity_weights = {
            'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6,
            'p': 1, 'ul': 2, 'ol': 2, 'table': 4
        }
        
        total_complexity = sum(complexity_weights.get(elem.name, 1) for elem in elements)
        return total_complexity / len(elements)
    
    def _assess_readability_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Assess document structure for readability"""
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = soup.find_all('p')
        
        return {
            'has_clear_hierarchy': len(headers) > 0,
            'header_to_content_ratio': len(headers) / max(len(paragraphs), 1),
            'avg_paragraph_length': sum(len(p.get_text().split()) for p in paragraphs) / max(len(paragraphs), 1),
            'structure_score': min(1.0, len(headers) * 0.1 + len(paragraphs) * 0.05)
        }

class ContentSanitizer(ContentProcessor):
    """
    Content sanitization processor
    
    Handles:
    - Profanity filtering
    - Sensitive information removal
    - Content policy compliance
    - Brand safety checks
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.profanity_words = self._load_profanity_list()
        self.sensitive_patterns = self._load_sensitive_patterns()
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        result = ProcessingResult(original_content=content, processed_content=content)
        metadata = metadata or {}
        
        try:
            # Check for profanity
            profanity_issues = self._detect_profanity(content)
            result.metadata['profanity_detected'] = len(profanity_issues) > 0
            result.metadata['profanity_words'] = profanity_issues
            self._log_processing_step(f"Profanity check: {len(profanity_issues)} issues", result)
            
            # Check for sensitive information
            sensitive_info = self._detect_sensitive_info(content)
            result.metadata['sensitive_info_detected'] = len(sensitive_info) > 0
            result.metadata['sensitive_patterns'] = sensitive_info
            self._log_processing_step(f"Sensitive info check: {len(sensitive_info)} patterns", result)
            
            # Brand safety assessment
            brand_safety = self._assess_brand_safety(content)
            result.metadata['brand_safety'] = brand_safety
            self._log_processing_step(f"Brand safety score: {brand_safety['score']:.2f}", result)
            
            # Apply sanitization if configured
            if self.config.get('sanitize_content', False):
                sanitized_content = self._sanitize_content(content, profanity_issues, sensitive_info)
                result.processed_content = sanitized_content
                self._log_processing_step("Content sanitized", result)
            
            # Calculate safety score
            result.quality_score = self._calculate_safety_score(profanity_issues, sensitive_info, brand_safety)
            
            return result
            
        except Exception as e:
            logger.error(f"Content sanitization failed: {str(e)}")
            result.processed_content = result.original_content
            result.metadata['error'] = str(e)
            return result
    
    def _load_profanity_list(self) -> List[str]:
        """Load profanity word list"""
        # Basic profanity list - should be loaded from external source in production
        return [
            'damn', 'hell', 'crap', 'stupid', 'idiot',
            # Add more comprehensive list in production
        ]
    
    def _load_sensitive_patterns(self) -> List[re.Pattern]:
        """Load patterns for sensitive information detection"""
        patterns = [
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # SSN pattern
            re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # Credit card pattern
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email pattern
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),  # Phone pattern
        ]
        return patterns
    
    def _detect_profanity(self, content: str) -> List[str]:
        """Detect profanity in content"""
        words = content.lower().split()
        detected = [word for word in words if word in self.profanity_words]
        return list(set(detected))
    
    def _detect_sensitive_info(self, content: str) -> List[Dict[str, str]]:
        """Detect sensitive information patterns"""
        detected = []
        
        pattern_names = ['SSN', 'Credit Card', 'Email', 'Phone']
        
        for i, pattern in enumerate(self.sensitive_patterns):
            matches = pattern.findall(content)
            for match in matches:
                detected.append({
                    'type': pattern_names[i],
                    'pattern': match,
                    'position': content.find(match)
                })
        
        return detected
    
    def _assess_brand_safety(self, content: str) -> Dict[str, Any]:
        """Assess content for brand safety"""
        risky_topics = [
            'violence', 'hate', 'discrimination', 'illegal',
            'drugs', 'alcohol', 'gambling', 'adult'
        ]
        
        controversial_topics = [
            'politics', 'religion', 'controversial', 'debate',
            'argument', 'conflict', 'war'
        ]
        
        words = content.lower().split()
        
        risky_score = sum(1 for word in words if word in risky_topics) / max(len(words), 1)
        controversial_score = sum(1 for word in words if word in controversial_topics) / max(len(words), 1)
        
        # Calculate overall safety score (higher is safer)
        safety_score = max(0.0, 1.0 - (risky_score * 2 + controversial_score))
        
        return {
            'score': safety_score,
            'risky_content': risky_score > 0,
            'controversial_content': controversial_score > 0,
            'recommendation': self._get_safety_recommendation(safety_score)
        }
    
    def _get_safety_recommendation(self, score: float) -> str:
        """Get safety recommendation based on score"""
        if score >= 0.9:
            return "Brand safe - suitable for all audiences"
        elif score >= 0.7:
            return "Generally safe - minor review recommended"
        elif score >= 0.5:
            return "Moderate risk - review and edit recommended"
        else:
            return "High risk - significant editing required"
    
    def _sanitize_content(self, content: str, profanity: List[str], sensitive_info: List[Dict[str, str]]) -> str:
        """Sanitize content by removing/replacing problematic elements"""
        sanitized = content
        
        # Replace profanity
        for word in profanity:
            sanitized = re.sub(rf'\b{re.escape(word)}\b', '*' * len(word), sanitized, flags=re.IGNORECASE)
        
        # Remove sensitive information
        for info in sensitive_info:
            sanitized = sanitized.replace(info['pattern'], '[REDACTED]')
        
        return sanitized
    
    def _calculate_safety_score(self, profanity: List[str], sensitive_info: List[Dict[str, str]], brand_safety: Dict[str, Any]) -> float:
        """Calculate overall content safety score"""
        # Penalties for issues
        profanity_penalty = len(profanity) * 0.1
        sensitive_penalty = len(sensitive_info) * 0.2
        brand_safety_score = brand_safety['score']
        
        # Calculate final score
        final_score = brand_safety_score - profanity_penalty - sensitive_penalty
        return max(0.0, min(1.0, final_score))

class ContentProcessorPipeline:
    """
    Content processing pipeline that chains multiple processors
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.processors = []
        self.processing_stats = {
            'total_processed': 0,
            'avg_processing_time': 0.0,
            'error_count': 0
        }
    
    def add_processor(self, processor: ContentProcessor):
        """Add a processor to the pipeline"""
        self.processors.append(processor)
        logger.info(f"Added processor: {processor.name}")
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process content through the entire pipeline"""
        start_time = datetime.utcnow()
        current_content = content
        all_metadata = metadata or {}
        all_steps = []
        overall_quality = 1.0
        
        try:
            for processor in self.processors:
                result = await processor.process(current_content, all_metadata.copy())
                
                # Update content for next processor
                current_content = result.processed_content
                
                # Accumulate metadata
                all_metadata.update(result.metadata)
                all_steps.extend(result.processing_steps)
                
                # Update quality score (take minimum to be conservative)
                if result.quality_score > 0:
                    overall_quality = min(overall_quality, result.quality_score)
                
                logger.debug(f"Processed with {processor.name}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            final_result = ProcessingResult(
                original_content=content,
                processed_content=current_content,
                metadata=all_metadata,
                processing_steps=all_steps,
                quality_score=overall_quality
            )
            
            # Update stats
            self._update_stats(processing_time, success=True)
            
            return final_result
            
        except Exception as e:
            self._update_stats(0, success=False)
            logger.error(f"Pipeline processing failed: {str(e)}")
            raise
    
    def _update_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        if success:
            self.processing_stats['total_processed'] += 1
            current_avg = self.processing_stats['avg_processing_time']
            total = self.processing_stats['total_processed']
            
            # Calculate rolling average
            self.processing_stats['avg_processing_time'] = (
                (current_avg * (total - 1) + processing_time) / total
            )
        else:
            self.processing_stats['error_count'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""



        return self.processing_stats.copy()
    
    async def batch_process(self, contents: List[str], metadata_list: List[Dict[str, Any]] = None) -> List[ProcessingResult]:
        """Process multiple contents in batch"""
        if metadata_list is None:
            metadata_list = [{}] * len(contents)
        
        tasks = [
            self.process(content, metadata)
            for content, metadata in zip(contents, metadata_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing error for item {i}: {str(result)}")
                # Create error result
                error_result = ProcessingResult(
                    original_content=contents[i],
                    processed_content=contents[i],
                    metadata={'error': str(result)},
                    quality_score=0.0
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results

# Predefined pipeline configurations
def create_social_media_pipeline(config: Dict[str, Any] = None) -> ContentProcessorPipeline:
    """Create a pipeline optimized for social media content"""
    pipeline = ContentProcessorPipeline(config)
    pipeline.add_processor(TextNormalizer(config))
    pipeline.add_processor(SocialMediaProcessor(config))
    pipeline.add_processor(ContentSanitizer(config))
    return pipeline

def create_blog_pipeline(config: Dict[str, Any] = None) -> ContentProcessorPipeline:
    """Create a pipeline optimized for blog content"""
    pipeline = ContentProcessorPipeline(config)
    pipeline.add_processor(TextNormalizer(config))
    pipeline.add_processor(MarkdownProcessor(config))
    pipeline.add_processor(ContentSanitizer(config))
    return pipeline

def create_general_pipeline(config: Dict[str, Any] = None) -> ContentProcessorPipeline:
    """Create a general-purpose content processing pipeline"""
    pipeline = ContentProcessorPipeline(config)
    pipeline.add_processor(TextNormalizer(config))
    pipeline.add_processor(ContentSanitizer(config))
    return pipeline

# Utility functions
async def quick_process_social_media(content: str) -> Dict[str, Any]:
    """Quick processing for social media content"""
    pipeline = create_social_media_pipeline()
    result = await pipeline.process(content)
    return {
        'processed_content': result.processed_content,
        'hashtags': result.metadata.get('hashtags', []),
        'mentions': result.metadata.get('mentions', []),
        'social_metrics': result.metadata.get('social_metrics', {}),
        'quality_score': result.quality_score
    }

async def quick_process_blog(content: str) -> Dict[str, Any]:
    """Quick processing for blog content"""
    pipeline = create_blog_pipeline()
    result = await pipeline.process(content)
    return {
        'processed_content': result.processed_content,
        'headers': result.metadata.get('headers', []),
        'links': result.metadata.get('links', []),
        'document_metrics': result.metadata.get('document_metrics', {}),
        'quality_score': result.quality_score
    }
