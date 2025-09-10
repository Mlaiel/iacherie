"""AI Response Processor - AI Response Standardization and Enhancement System
===========================================================================

Advanced AI response processing system that standardizes, validates, enhances,
and optimizes responses from various AI service providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import base64
from io import BytesIO
import mimetypes

import aiohttp
import aiofiles
from PIL import Image
import tiktoken
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """AI response types."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    JSON = "json"
    BINARY = "binary"
    STREAMING = "streaming"


class ContentFormat(Enum):
    """Content formats."""
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    CODE = "code"


class ProcessingStage(Enum):
    """Response processing stages."""
    RAW = "raw"
    VALIDATED = "validated"
    STANDARDIZED = "standardized"
    ENHANCED = "enhanced"
    OPTIMIZED = "optimized"
    FINALIZED = "finalized"


class QualityMetric(Enum):
    """Response quality metrics."""
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    CREATIVITY = "creativity"
    SAFETY = "safety"
    APPROPRIATENESS = "appropriateness"


@dataclass
class ResponseMetadata:
    """AI response metadata."""
    provider: str
    model: str
    service_type: str
    request_id: str
    timestamp: datetime
    processing_time_ms: float
    token_count: int
    cost: float
    quality_scores: Dict[QualityMetric, float] = field(default_factory=dict)
    safety_flags: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    language: str = "en"
    confidence_score: float = 0.0


@dataclass
class ProcessedResponse:
    """Processed AI response."""
    original_response: Any
    processed_content: str
    response_type: ResponseType
    content_format: ContentFormat
    metadata: ResponseMetadata
    processing_stage: ProcessingStage
    enhancements: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    optimization_metrics: Dict[str, float] = field(default_factory=dict)
    cached_versions: Dict[str, str] = field(default_factory=dict)


class ResponseValidator:
    """AI response validation system."""
    
    def __init__(self):
        self.safety_patterns = [
            r'\b(?:kill|murder|suicide|bomb|weapon|drug|illegal)\b',
            r'\b(?:hack|steal|fraud|scam|phish)\b',
            r'\b(?:racist|sexist|homophobic|discriminatory)\b'
        ]
        
        self.content_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }
    
    async def validate_response(self, response: str, response_type: ResponseType) -> Tuple[bool, List[str]]:
        """Validate AI response for safety and content quality."""
        errors = []
        
        try:
            # Safety validation
            safety_errors = await self._validate_safety(response)
            errors.extend(safety_errors)
            
            # Content validation
            content_errors = await self._validate_content(response, response_type)
            errors.extend(content_errors)
            
            # Format validation
            format_errors = await self._validate_format(response, response_type)
            errors.extend(format_errors)
            
            # Privacy validation
            privacy_errors = await self._validate_privacy(response)
            errors.extend(privacy_errors)
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False, [f"Validation error: {str(e)}"]
    
    async def _validate_safety(self, response: str) -> List[str]:
        """Validate response for safety concerns."""
        errors = []
        
        for pattern in self.safety_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                errors.append(f"Safety concern detected: potentially harmful content")
        
        return errors
    
    async def _validate_content(self, response: str, response_type: ResponseType) -> List[str]:
        """Validate content quality and structure."""
        errors = []
        
        # Check minimum length
        if len(response.strip()) < 10:
            errors.append("Response too short")
        
        # Check maximum length
        if len(response) > 100000:  # 100k chars
            errors.append("Response too long")
        
        # Type-specific validation
        if response_type == ResponseType.JSON:
            try:
                json.loads(response)
            except json.JSONDecodeError:
                errors.append("Invalid JSON format")
        
        elif response_type == ResponseType.TEXT:
            # Check for coherence indicators
            if response.count('.') == 0 and len(response) > 100:
                errors.append("Potentially incoherent text (no sentence endings)")
        
        return errors
    
    async def _validate_format(self, response: str, response_type: ResponseType) -> List[str]:
        """Validate response format consistency."""
        errors = []
        
        # Check encoding
        try:
            response.encode('utf-8')
        except UnicodeEncodeError:
            errors.append("Invalid character encoding")
        
        # Check for control characters
        if any(ord(char) < 32 and char not in '\n\t\r' for char in response):
            errors.append("Contains invalid control characters")
        
        return errors
    
    async def _validate_privacy(self, response: str) -> List[str]:
        """Validate response for privacy concerns."""
        errors = []
        
        for pattern_name, pattern in self.content_patterns.items():
            if re.search(pattern, response):
                errors.append(f"Potential privacy leak: {pattern_name} detected")
        
        return errors


class ResponseEnhancer:
    """AI response enhancement system."""
    
    def __init__(self):
        self.enhancement_rules = {
            'markdown_formatting': self._enhance_markdown,
            'link_enrichment': self._enhance_links,
            'structure_improvement': self._enhance_structure,
            'readability_optimization': self._enhance_readability,
            'multilingual_support': self._enhance_multilingual
        }
    
    async def enhance_response(self, response: str, content_format: ContentFormat) -> Tuple[str, List[str]]:
        """Enhance AI response with formatting and structure improvements."""
        enhanced_response = response
        enhancements = []
        
        try:
            for enhancement_name, enhancement_func in self.enhancement_rules.items():
                try:
                    enhanced_response, enhancement_applied = await enhancement_func(enhanced_response, content_format)
                    if enhancement_applied:
                        enhancements.append(enhancement_name)
                        
                except Exception as e:
                    logger.warning(f"Enhancement {enhancement_name} failed: {str(e)}")
                    continue
            
            return enhanced_response, enhancements
            
        except Exception as e:
            logger.error(f"Response enhancement failed: {str(e)}")
            return response, []
    
    async def _enhance_markdown(self, response: str, content_format: ContentFormat) -> Tuple[str, bool]:
        """Enhance with markdown formatting."""
        if content_format != ContentFormat.MARKDOWN:
            return response, False
        
        enhanced = response
        enhanced_flag = False
        
        # Add headers for sections
        lines = enhanced.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 50:
                # Check if it looks like a section header
                if stripped.endswith(':') and len(stripped.split()) <= 6:
                    processed_lines.append(f"## {stripped[:-1]}")
                    enhanced_flag = True
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        enhanced = '\n'.join(processed_lines)
        
        # Add code blocks for code snippets
        if '```' not in enhanced and ('def ' in enhanced or 'function ' in enhanced or 'class ' in enhanced):
            enhanced = re.sub(
                r'(def .+?:\n(?:    .+\n)*)',
                r'```python\n\1```\n',
                enhanced,
                flags=re.MULTILINE
            )
            enhanced_flag = True
        
        return enhanced, enhanced_flag
    
    async def _enhance_links(self, response: str, content_format: ContentFormat) -> Tuple[str, bool]:
        """Enhance with clickable links."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        
        def make_link(match):
            url = match.group()
            if content_format == ContentFormat.MARKDOWN:
                return f"[{url}]({url})"
            elif content_format == ContentFormat.HTML:
                return f'<a href="{url}">{url}</a>'
            return url
        
        enhanced = re.sub(url_pattern, make_link, response)
        return enhanced, enhanced != response
    
    async def _enhance_structure(self, response: str, content_format: ContentFormat) -> Tuple[str, bool]:
        """Enhance response structure."""
        enhanced = response
        enhanced_flag = False
        
        # Add bullet points for lists
        lines = enhanced.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect list items
            if (stripped and not stripped.startswith(('-', '*', '•', '1.')) and 
                len(stripped) < 100 and 
                stripped.count(',') < 3):
                
                # Check if previous line was also a list item
                if in_list or (len(processed_lines) > 0 and 
                              processed_lines[-1].strip().startswith(('-', '*', '•'))):
                    processed_lines.append(f"- {stripped}")
                    enhanced_flag = True
                    in_list = True
                else:
                    processed_lines.append(line)
                    in_list = False
            else:
                processed_lines.append(line)
                in_list = False
        
        enhanced = '\n'.join(processed_lines)
        return enhanced, enhanced_flag
    
    async def _enhance_readability(self, response: str, content_format: ContentFormat) -> Tuple[str, bool]:
        """Enhance readability with better formatting."""
        enhanced = response
        enhanced_flag = False
        
        # Add spacing between paragraphs
        paragraphs = enhanced.split('\n\n')
        if len(paragraphs) > 1:
            enhanced = '\n\n'.join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
            enhanced_flag = True
        
        # Fix sentence spacing
        enhanced = re.sub(r'\.([A-Z])', r'. \1', enhanced)
        if enhanced != response:
            enhanced_flag = True
        
        return enhanced, enhanced_flag
    
    async def _enhance_multilingual(self, response: str, content_format: ContentFormat) -> Tuple[str, bool]:
        """Enhance multilingual content."""
        # For now, just ensure proper UTF-8 encoding
        try:
            enhanced = response.encode('utf-8').decode('utf-8')
            return enhanced, enhanced != response
        except UnicodeError:
            return response, False


class ResponseOptimizer:
    """AI response optimization system."""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def optimize_response(self, response: str, target_length: Optional[int] = None) -> Tuple[str, Dict[str, float]]:
        """Optimize response for length, quality, and performance."""
        optimization_metrics = {}
        optimized_response = response
        
        try:
            # Calculate initial metrics
            initial_tokens = len(self.encoding.encode(response))
            initial_chars = len(response)
            
            # Length optimization
            if target_length and initial_chars > target_length:
                optimized_response = await self._optimize_length(optimized_response, target_length)
            
            # Content optimization
            optimized_response = await self._optimize_content(optimized_response)
            
            # Performance optimization
            optimized_response = await self._optimize_performance(optimized_response)
            
            # Calculate final metrics
            final_tokens = len(self.encoding.encode(optimized_response))
            final_chars = len(optimized_response)
            
            optimization_metrics = {
                'token_reduction': (initial_tokens - final_tokens) / initial_tokens if initial_tokens > 0 else 0,
                'char_reduction': (initial_chars - final_chars) / initial_chars if initial_chars > 0 else 0,
                'compression_ratio': final_chars / initial_chars if initial_chars > 0 else 1,
                'readability_score': await self._calculate_readability(optimized_response)
            }
            
            return optimized_response, optimization_metrics
            
        except Exception as e:
            logger.error(f"Response optimization failed: {str(e)}")
            return response, {}
    
    async def _optimize_length(self, response: str, target_length: int) -> str:
        """Optimize response length by removing redundancy."""
        if len(response) <= target_length:
            return response
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', response)
        
        # Remove redundant sentences
        unique_sentences = []
        seen_content = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Simple similarity check
            sentence_words = set(sentence.lower().split())
            if not any(len(sentence_words & existing) > len(sentence_words) * 0.8 
                      for existing in seen_content):
                unique_sentences.append(sentence)
                seen_content.add(sentence_words)
                
                # Check if we're approaching target length
                current_length = len('. '.join(unique_sentences))
                if current_length >= target_length * 0.9:
                    break
        
        return '. '.join(unique_sentences) + '.'
    
    async def _optimize_content(self, response: str) -> str:
        """Optimize content quality and clarity."""
        optimized = response
        
        # Remove excessive whitespace
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = re.sub(r'\n\s*\n', '\n\n', optimized)
        
        # Fix common grammar issues
        optimized = re.sub(r'\s+([,.!?;:])', r'\1', optimized)
        optimized = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', optimized)
        
        # Remove redundant phrases
        redundant_phrases = [
            r'\b(very|really|quite|rather|pretty)\s+',
            r'\b(I think|I believe|In my opinion)\s+',
            r'\b(obviously|clearly|evidently)\s+',
            r'\b(basically|essentially|fundamentally)\s+'
        ]
        
        for pattern in redundant_phrases:
            optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
        
        return optimized.strip()
    
    async def _optimize_performance(self, response: str) -> str:
        """Optimize response for performance."""
        # Remove unnecessary unicode characters
        optimized = response.encode('ascii', 'ignore').decode('ascii')
        
        # If too much content was lost, keep original
        if len(optimized) < len(response) * 0.8:
            optimized = response
        
        return optimized
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculate simple readability score."""
        if not text:
            return 0.0
        
        # Simple readability metric based on sentence and word length
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Score based on ideal sentence length (15-20 words)
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        elif 5 <= avg_sentence_length <= 30:
            return 0.6
        else:
            return 0.4


class AIResponseProcessor:
    """Main AI response processing system."""
    
    def __init__(self):
        self.validator = ResponseValidator()
        self.enhancer = ResponseEnhancer()
        self.optimizer = ResponseOptimizer()
        
        # Metrics
        self.processing_counter = Counter('ai_response_processing_total', 'Total response processing requests', ['provider', 'stage'])
        self.processing_duration = Histogram('ai_response_processing_duration_seconds', 'Response processing duration', ['provider', 'stage'])
        self.quality_score = Gauge('ai_response_quality_score', 'Response quality scores', ['provider', 'metric'])
        
        # Caching
        self.response_cache: Dict[str, ProcessedResponse] = {}
        self.cache_ttl = timedelta(hours=24)
    
    async def process_response(self, 
                             original_response: Any,
                             provider: str,
                             model: str,
                             service_type: str,
                             request_id: str,
                             response_type: ResponseType = ResponseType.TEXT,
                             content_format: ContentFormat = ContentFormat.PLAIN_TEXT,
                             target_length: Optional[int] = None,
                             enhance: bool = True,
                             optimize: bool = True) -> ProcessedResponse:
        """Process AI response through validation, enhancement, and optimization."""
        start_time = time.time()
        
        try:
            # Extract text content from response
            content = await self._extract_content(original_response, response_type)
            
            # Create metadata
            metadata = ResponseMetadata(
                provider=provider,
                model=model,
                service_type=service_type,
                request_id=request_id,
                timestamp=datetime.utcnow(),
                processing_time_ms=0,
                token_count=len(self.optimizer.encoding.encode(content)) if isinstance(content, str) else 0,
                cost=0.0  # Will be calculated by cost optimizer
            )
            
            # Initialize processed response
            processed_response = ProcessedResponse(
                original_response=original_response,
                processed_content=content,
                response_type=response_type,
                content_format=content_format,
                metadata=metadata,
                processing_stage=ProcessingStage.RAW
            )
            
            # Stage 1: Validation
            await self._process_validation_stage(processed_response)
            
            # Stage 2: Standardization
            await self._process_standardization_stage(processed_response)
            
            # Stage 3: Enhancement (optional)
            if enhance:
                await self._process_enhancement_stage(processed_response)
            
            # Stage 4: Optimization (optional)
            if optimize:
                await self._process_optimization_stage(processed_response, target_length)
            
            # Stage 5: Finalization
            await self._process_finalization_stage(processed_response)
            
            # Update processing time
            processing_time = (time.time() - start_time) * 1000
            processed_response.metadata.processing_time_ms = processing_time
            
            # Update metrics
            self.processing_counter.labels(provider=provider, stage='complete').inc()
            self.processing_duration.labels(provider=provider, stage='complete').observe(processing_time / 1000)
            
            # Cache response
            cache_key = hashlib.md5(f"{provider}_{model}_{request_id}".encode()).hexdigest()
            self.response_cache[cache_key] = processed_response
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Response processing failed: {str(e)}")
            # Return minimal processed response on error
            return ProcessedResponse(
                original_response=original_response,
                processed_content=str(original_response),
                response_type=response_type,
                content_format=content_format,
                metadata=ResponseMetadata(
                    provider=provider,
                    model=model,
                    service_type=service_type,
                    request_id=request_id,
                    timestamp=datetime.utcnow(),
                    processing_time_ms=(time.time() - start_time) * 1000,
                    token_count=0,
                    cost=0.0
                ),
                processing_stage=ProcessingStage.RAW,
                validation_errors=[f"Processing error: {str(e)}"]
            )
    
    async def _extract_content(self, response: Any, response_type: ResponseType) -> str:
        """Extract content from various response formats."""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            # Common AI API response formats
            if 'choices' in response and response['choices']:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                elif 'text' in choice:
                    return choice['text']
            
            if 'content' in response:
                return response['content']
            
            if 'text' in response:
                return response['text']
            
            if 'output' in response:
                return response['output']
            
            # Return JSON string for complex objects
            return json.dumps(response, indent=2)
        
        return str(response)
    
    async def _process_validation_stage(self, processed_response: ProcessedResponse):
        """Process validation stage."""
        try:
            is_valid, errors = await self.validator.validate_response(
                processed_response.processed_content,
                processed_response.response_type
            )
            
            processed_response.validation_errors = errors
            processed_response.processing_stage = ProcessingStage.VALIDATED
            
            # Update metrics
            self.processing_counter.labels(
                provider=processed_response.metadata.provider,
                stage='validation'
            ).inc()
            
        except Exception as e:
            processed_response.validation_errors.append(f"Validation stage error: {str(e)}")
    
    async def _process_standardization_stage(self, processed_response: ProcessedResponse):
        """Process standardization stage."""
        try:
            # Standardize line endings
            content = processed_response.processed_content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Standardize spacing
            content = re.sub(r' +', ' ', content)
            content = re.sub(r'\n\n+', '\n\n', content)
            
            processed_response.processed_content = content.strip()
            processed_response.processing_stage = ProcessingStage.STANDARDIZED
            
            # Update metrics
            self.processing_counter.labels(
                provider=processed_response.metadata.provider,
                stage='standardization'
            ).inc()
            
        except Exception as e:
            processed_response.validation_errors.append(f"Standardization stage error: {str(e)}")
    
    async def _process_enhancement_stage(self, processed_response: ProcessedResponse):
        """Process enhancement stage."""
        try:
            enhanced_content, enhancements = await self.enhancer.enhance_response(
                processed_response.processed_content,
                processed_response.content_format
            )
            
            processed_response.processed_content = enhanced_content
            processed_response.enhancements = enhancements
            processed_response.processing_stage = ProcessingStage.ENHANCED
            
            # Update metrics
            self.processing_counter.labels(
                provider=processed_response.metadata.provider,
                stage='enhancement'
            ).inc()
            
        except Exception as e:
            processed_response.validation_errors.append(f"Enhancement stage error: {str(e)}")
    
    async def _process_optimization_stage(self, processed_response: ProcessedResponse, target_length: Optional[int]):
        """Process optimization stage."""
        try:
            optimized_content, optimization_metrics = await self.optimizer.optimize_response(
                processed_response.processed_content,
                target_length
            )
            
            processed_response.processed_content = optimized_content
            processed_response.optimization_metrics = optimization_metrics
            processed_response.processing_stage = ProcessingStage.OPTIMIZED
            
            # Update metrics
            self.processing_counter.labels(
                provider=processed_response.metadata.provider,
                stage='optimization'
            ).inc()
            
            for metric_name, value in optimization_metrics.items():
                self.quality_score.labels(
                    provider=processed_response.metadata.provider,
                    metric=metric_name
                ).set(value)
            
        except Exception as e:
            processed_response.validation_errors.append(f"Optimization stage error: {str(e)}")
    
    async def _process_finalization_stage(self, processed_response: ProcessedResponse):
        """Process finalization stage."""
        try:
            # Calculate quality scores
            content = processed_response.processed_content
            
            quality_scores = {
                QualityMetric.COMPLETENESS: min(1.0, len(content) / 500),  # 500 chars is "complete"
                QualityMetric.COHERENCE: await self.optimizer._calculate_readability(content),
                QualityMetric.SAFETY: 1.0 if not processed_response.validation_errors else 0.5,
                QualityMetric.APPROPRIATENESS: 1.0 if len(processed_response.validation_errors) == 0 else 0.7
            }
            
            processed_response.metadata.quality_scores = quality_scores
            processed_response.processing_stage = ProcessingStage.FINALIZED
            
            # Update token count
            processed_response.metadata.token_count = len(self.optimizer.encoding.encode(content))
            
            # Update metrics
            self.processing_counter.labels(
                provider=processed_response.metadata.provider,
                stage='finalization'
            ).inc()
            
            for metric, score in quality_scores.items():
                self.quality_score.labels(
                    provider=processed_response.metadata.provider,
                    metric=metric.value
                ).set(score)
            
        except Exception as e:
            processed_response.validation_errors.append(f"Finalization stage error: {str(e)}")
    
    async def get_cached_response(self, provider: str, model: str, request_id: str) -> Optional[ProcessedResponse]:
        """Get cached processed response."""
        cache_key = hashlib.md5(f"{provider}_{model}_{request_id}".encode()).hexdigest()
        
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            
            # Check TTL
            age = datetime.utcnow() - cached_response.metadata.timestamp
            if age < self.cache_ttl:
                return cached_response
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        return None
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        stats = {
            "total_processed": sum(self.processing_counter._value.values()),
            "cache_size": len(self.response_cache),
            "average_processing_time": 0.0,
            "quality_distribution": {},
            "error_distribution": {},
            "provider_performance": {}
        }
        
        # Calculate average processing time
        durations = [response.metadata.processing_time_ms for response in self.response_cache.values()]
        if durations:
            stats["average_processing_time"] = sum(durations) / len(durations)
        
        # Quality distribution
        all_scores = []
        for response in self.response_cache.values():
            for metric, score in response.metadata.quality_scores.items():
                all_scores.append(score)
        
        if all_scores:
            stats["quality_distribution"] = {
                "mean": sum(all_scores) / len(all_scores),
                "min": min(all_scores),
                "max": max(all_scores)
            }
        
        return stats


# Global response processor instance
response_processor = AIResponseProcessor()


async def process_ai_response(original_response: Any,
                            provider: str,
                            model: str,
                            service_type: str,
                            request_id: str,
                            **kwargs) -> ProcessedResponse:
    """Process AI response using global processor."""
    return await response_processor.process_response(
        original_response=original_response,
        provider=provider,
        model=model,
        service_type=service_type,
        request_id=request_id,
        **kwargs
    )


# Example usage
async def main():
    """Example usage of AI response processor."""
    # Example OpenAI response
    openai_response = {
        "choices": [
            {
                "message": {
                    "content": "This is a sample AI response that needs to be processed and enhanced for better quality and standardization."
                }
            }
        ]
    }
    
    processed = await response_processor.process_response(
        original_response=openai_response,
        provider="openai",
        model="gpt-4",
        service_type="text_generation",
        request_id="test-123",
        response_type=ResponseType.TEXT,
        content_format=ContentFormat.MARKDOWN,
        enhance=True,
        optimize=True
    )
    
    print(f"Original: {openai_response}")
    print(f"Processed: {processed.processed_content}")
    print(f"Quality scores: {processed.metadata.quality_scores}")
    print(f"Enhancements: {processed.enhancements}")
    print(f"Processing time: {processed.metadata.processing_time_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())