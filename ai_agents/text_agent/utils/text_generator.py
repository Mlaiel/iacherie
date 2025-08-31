"""
AI Text Generator - Advanced Content Generation and Synthesis Engine

Industrial-grade AI-powered text generation, content synthesis, and creative writing
for content creators with enterprise-level quality control and customization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import openai
from transformers import (
    GPT2LMHeadModel, GPT2Tokenizer, 
    T5ForConditionalGeneration, T5Tokenizer,
    BartForConditionalGeneration, BartTokenizer,
    pipeline
)
import torch
from torch.nn.functional import softmax
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ValidationError, ProcessingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ValidationError, ProcessingError = globals().get('ValidationError, ProcessingError', Exception)
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)

class GenerationType(Enum):
    """Text generation types"""
    CREATIVE = "creative"
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    MARKETING = "marketing"
    ACADEMIC = "academic"
    STORYTELLING = "storytelling"

class WritingStyle(Enum):
    """Writing style variations"""
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"
    POETIC = "poetic"

class ContentFormat(Enum):
    """Content format types"""
    PARAGRAPH = "paragraph"
    LIST = "list"
    BULLET_POINTS = "bullet_points"
    ARTICLE = "article"
    SUMMARY = "summary"
    HEADLINE = "headline"
    DESCRIPTION = "description"
    SCRIPT = "script"

@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    max_length: int = 500
    min_length: int = 50
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    num_return_sequences: int = 1
    do_sample: bool = True
    generation_type: GenerationType = GenerationType.INFORMATIVE
    writing_style: WritingStyle = WritingStyle.PROFESSIONAL
    content_format: ContentFormat = ContentFormat.PARAGRAPH
    target_audience: str = "general"
    language: str = "en"
    include_keywords: List[str] = field(default_factory=list)
    exclude_phrases: List[str] = field(default_factory=list)
    tone_keywords: List[str] = field(default_factory=list)

@dataclass
class GenerationResult:
    """Text generation result with metadata"""
    generation_id: str
    prompt: str
    generated_text: str
    config_used: GenerationConfig
    quality_score: float
    creativity_score: float
    relevance_score: float
    generation_time: float
    model_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class AITextGenerator:
    """
    Industrial-grade AI text generation system with multiple models and advanced controls
    """
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize generation models
        self._init_generation_models()
        
        # Quality control components
        self.quality_thresholds = {
            'minimum_quality': 0.6,
            'minimum_relevance': 0.7,
            'maximum_repetition': 0.3
        }
        
        # Generation statistics
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "average_quality_score": 0.0,
            "total_words_generated": 0,
            "model_usage": {}
        }
        
        logger.info("AITextGenerator initialized with advanced models")
    
    def _init_generation_models(self):
        """Initialize text generation models"""



        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            # Initialize GPT-2 model for creative generation
            self.gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2-medium")
            self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
            self.gpt2_model.to(device)
            self.gpt2_tokenizer.pad_token = self.gpt2_tokenizer.eos_token
            
            # Initialize T5 model for conditional generation
            self.t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
            self.t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
            self.t5_model.to(device)
            
            # Initialize BART model for summarization and paraphrasing
            self.bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large")
            self.bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")
            self.bart_model.to(device)
            
            # Initialize specialized pipelines
            self.summarization_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.paraphrase_pipeline = pipeline(
                "text2text-generation",
                model="ramsrigouthamg/t5_paraphraser",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.device = device
            logger.info(f"Generation models initialized on device: {device}")
            
        except Exception as e:
            logger.error(f"Error initializing generation models: {e}")
            raise ProcessingError(f"Failed to initialize generation models: {e}")
    
    async def generate_content(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        Generate AI-powered text content with advanced controls
        
        Args:
            prompt: Generation prompt
            config: Generation configuration
            
        Returns:
            GenerationResult: Generated content with metadata
        """
        start_time = time.time()
        generation_id = str(uuid.uuid4())
        config = config or GenerationConfig()
        
        try:
            # Validate prompt
            await self._validate_prompt(prompt, config)
            
            # Enhance prompt based on configuration
            enhanced_prompt = await self._enhance_prompt(prompt, config)
            
            # Select appropriate model based on generation type
            model_name = await self._select_model(config)
            
            # Generate content
            generated_text = await self._generate_with_model(
                enhanced_prompt, config, model_name
            )
            
            # Post-process generated content
            generated_text = await self._post_process_content(generated_text, config)
            
            # Quality assessment
            quality_score = await self._assess_content_quality(generated_text, prompt)
            creativity_score = await self._assess_creativity(generated_text, prompt)
            relevance_score = await self._assess_relevance(generated_text, prompt)
            
            # Check quality thresholds
            if quality_score < self.quality_thresholds['minimum_quality']:
                logger.warning(f"Generated content quality below threshold: {quality_score}")
                # Retry generation with adjusted parameters
                config.temperature = min(config.temperature + 0.1, 1.0)
                return await self.generate_content(prompt, config)
            
            generation_time = time.time() - start_time
            
            result = GenerationResult(
                generation_id=generation_id,
                prompt=prompt,
                generated_text=generated_text,
                config_used=config,
                quality_score=quality_score,
                creativity_score=creativity_score,
                relevance_score=relevance_score,
                generation_time=generation_time,
                model_used=model_name,
                metadata={
                    'enhanced_prompt': enhanced_prompt,
                    'word_count': len(generated_text.split()),
                    'character_count': len(generated_text),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Update statistics
            await self._update_generation_stats(result)
            
            logger.info(f"Content generated successfully: {generation_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise ProcessingError(f"Content generation failed: {e}")
    
    async def generate_variations(
        self,
        original_text: str,
        num_variations: int = 3,
        variation_strength: float = 0.5
    ) -> List[str]:
        """
        Generate multiple variations of existing text
        
        Args:
            original_text: Original text to create variations from
            num_variations: Number of variations to generate
            variation_strength: How different the variations should be (0.0-1.0)
            
        Returns:
            List of text variations
        """



        try:
            variations = []
            
            for i in range(num_variations):
                # Adjust temperature based on variation strength
                temperature = 0.5 + (variation_strength * 0.4)
                
                # Create variation using paraphrasing
                if hasattr(self, 'paraphrase_pipeline'):
                    paraphrase_input = f"paraphrase: {original_text}"
                    result = self.paraphrase_pipeline(
                        paraphrase_input,
                        max_length=len(original_text.split()) + 20,
                        temperature=temperature,
                        do_sample=True
                    )
                    if result and len(result) > 0:
                        variations.append(result[0]['generated_text'])
                
                # Generate variation using GPT-2 with modified prompt
                variation_prompt = f"Rewrite the following text: {original_text}"
                config = GenerationConfig(
                    max_length=len(original_text.split()) + 50,
                    temperature=temperature,
                    generation_type=GenerationType.CREATIVE
                )
                
                variation_result = await self.generate_content(variation_prompt, config)
                variations.append(variation_result.generated_text)
            
            # Remove duplicates and original text
            unique_variations = []
            for variation in variations:
                similarity = await self._calculate_text_similarity(original_text, variation)
                if similarity < 0.9 and variation not in unique_variations:
                    unique_variations.append(variation)
            
            return unique_variations[:num_variations]
            
        except Exception as e:
            logger.error(f"Error generating variations: {e}")
            return []
    
    async def _validate_prompt(self, prompt: str, config: GenerationConfig):
        """Validate generation prompt"""
        if not prompt or len(prompt.strip()) < 3:
            raise ValidationError("Generation prompt too short")
        
        if len(prompt) > 1000:
            raise ValidationError("Generation prompt too long")
        
        # Check for excluded phrases
        for phrase in config.exclude_phrases:
            if phrase.lower() in prompt.lower():
                raise ValidationError(f"Prompt contains excluded phrase: {phrase}")
    
    async def _enhance_prompt(self, prompt: str, config: GenerationConfig) -> str:
        """Enhance prompt based on configuration"""
        enhanced_prompt = prompt
        
        # Add style instructions
        style_instructions = {
            WritingStyle.FORMAL: "Write in a formal, professional tone.",
            WritingStyle.CASUAL: "Write in a casual, conversational tone.",
            WritingStyle.FRIENDLY: "Write in a friendly, approachable tone.",
            WritingStyle.AUTHORITATIVE: "Write with authority and expertise.",
            WritingStyle.HUMOROUS: "Write with humor and wit.",
            WritingStyle.DRAMATIC: "Write with dramatic flair and emotion.",
            WritingStyle.POETIC: "Write with poetic language and imagery."
        }
        
        if config.writing_style in style_instructions:
            enhanced_prompt = f"{style_instructions[config.writing_style]} {enhanced_prompt}"
        
        # Add format instructions
        format_instructions = {
            ContentFormat.LIST: "Format as a numbered or bulleted list.",
            ContentFormat.BULLET_POINTS: "Format with bullet points.",
            ContentFormat.ARTICLE: "Write as a complete article with introduction and conclusion.",
            ContentFormat.SUMMARY: "Provide a concise summary.",
            ContentFormat.HEADLINE: "Create an engaging headline.",
            ContentFormat.DESCRIPTION: "Write a detailed description."
        }
        
        if config.content_format in format_instructions:
            enhanced_prompt = f"{format_instructions[config.content_format]} {enhanced_prompt}"
        
        # Add keyword requirements
        if config.include_keywords:
            keywords_text = ", ".join(config.include_keywords)
            enhanced_prompt = f"{enhanced_prompt} Include these keywords: {keywords_text}."
        
        # Add tone keywords
        if config.tone_keywords:
            tone_text = ", ".join(config.tone_keywords)
            enhanced_prompt = f"{enhanced_prompt} Use a tone that conveys: {tone_text}."
        
        # Add target audience information
        if config.target_audience != "general":
            enhanced_prompt = f"Write for {config.target_audience}. {enhanced_prompt}"
        
        return enhanced_prompt
    
    async def _select_model(self, config: GenerationConfig) -> str:
        """Select appropriate model based on generation type"""
        model_selection = {
            GenerationType.CREATIVE: "gpt2",
            GenerationType.INFORMATIVE: "t5",
            GenerationType.PERSUASIVE: "gpt2",
            GenerationType.TECHNICAL: "t5",
            GenerationType.CONVERSATIONAL: "gpt2",
            GenerationType.MARKETING: "gpt2",
            GenerationType.ACADEMIC: "t5",
            GenerationType.STORYTELLING: "gpt2"
        }
        
        return model_selection.get(config.generation_type, "gpt2")
    
    async def _generate_with_model(
        self,
        prompt: str,
        config: GenerationConfig,
        model_name: str
    ) -> str:
        """Generate text using specified model"""



        try:
            if model_name == "gpt2":
                return await self._generate_with_gpt2(prompt, config)
            elif model_name == "t5":
                return await self._generate_with_t5(prompt, config)
            elif model_name == "bart":
                return await self._generate_with_bart(prompt, config)
            else:
                return await self._generate_with_gpt2(prompt, config)  # Default fallback
                
        except Exception as e:
            logger.error(f"Error generating with model {model_name}: {e}")
            # Fallback to GPT-2
            return await self._generate_with_gpt2(prompt, config)
    
    async def _generate_with_gpt2(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using GPT-2 model"""



        try:
            # Tokenize input
            inputs = self.gpt2_tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.gpt2_model.generate(
                    inputs,
                    max_length=min(inputs.shape[1] + config.max_length, 1024),
                    min_length=inputs.shape[1] + config.min_length,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    repetition_penalty=config.repetition_penalty,
                    num_return_sequences=config.num_return_sequences,
                    do_sample=config.do_sample,
                    pad_token_id=self.gpt2_tokenizer.eos_token_id
                )
            
            # Decode generated text
            generated_text = self.gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the generated text
            generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"GPT-2 generation failed: {e}")
            return f"Generated content based on: {prompt}"
    
    async def _generate_with_t5(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using T5 model"""



        try:
            # Format prompt for T5
            t5_prompt = f"generate text: {prompt}"
            
            # Tokenize input
            inputs = self.t5_tokenizer.encode(t5_prompt, return_tensors='pt').to(self.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.t5_model.generate(
                    inputs,
                    max_length=config.max_length,
                    min_length=config.min_length,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    repetition_penalty=config.repetition_penalty,
                    num_return_sequences=config.num_return_sequences,
                    do_sample=config.do_sample
                )
            
            # Decode generated text
            generated_text = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"T5 generation failed: {e}")
            return f"Generated content based on: {prompt}"
    
    async def _generate_with_bart(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using BART model"""



        try:
            # Tokenize input
            inputs = self.bart_tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.bart_model.generate(
                    inputs,
                    max_length=config.max_length,
                    min_length=config.min_length,
                    temperature=config.temperature,
                    repetition_penalty=config.repetition_penalty,
                    num_return_sequences=config.num_return_sequences,
                    do_sample=config.do_sample
                )
            
            # Decode generated text
            generated_text = self.bart_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"BART generation failed: {e}")
            return f"Generated content based on: {prompt}"
    
    async def _post_process_content(self, text: str, config: GenerationConfig) -> str:
        """Post-process generated content"""
        # Remove repetitive content
        text = await self._remove_repetitions(text)
        
        # Apply text processing for cleanup
        processing_result = await self.text_processor.process_text(text)
        processed_text = processing_result.processed_text
        
        # Ensure proper formatting based on content format
        if config.content_format == ContentFormat.LIST:
            processed_text = await self._format_as_list(processed_text)
        elif config.content_format == ContentFormat.BULLET_POINTS:
            processed_text = await self._format_as_bullets(processed_text)
        
        # Ensure length constraints
        words = processed_text.split()
        if len(words) > config.max_length:
            processed_text = ' '.join(words[:config.max_length])
        elif len(words) < config.min_length:
            # Pad if too short (this shouldn't happen often)
            padding = "Additional content to meet minimum length requirements."
            processed_text = f"{processed_text} {padding}"
        
        return processed_text.strip()
    
    async def _remove_repetitions(self, text: str) -> str:
        """Remove repetitive content from generated text"""
        sentences = text.split('.')
        unique_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                # Check for similar sentences
                is_similar = False
                for existing in unique_sentences:
                    similarity = await self._calculate_text_similarity(sentence, existing)
                    if similarity > 0.8:
                        is_similar = True
                        break
                
                if not is_similar:
                    unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences)
    
    async def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""



        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    async def _assess_content_quality(self, generated_text: str, prompt: str) -> float:
        """Assess quality of generated content"""



        try:
            # Basic quality metrics
            word_count = len(generated_text.split())
            sentence_count = len(generated_text.split('.'))
            
            # Length appropriateness (0.0-1.0)
            length_score = min(1.0, word_count / 100) if word_count < 100 else 1.0
            
            # Coherence (simplified - based on sentence structure)
            coherence_score = min(1.0, sentence_count / max(1, word_count / 15))
            
            # Relevance to prompt
            relevance_score = await self._calculate_text_similarity(generated_text, prompt)
            
            # Combined quality score
            quality_score = (length_score * 0.3 + coherence_score * 0.3 + relevance_score * 0.4)
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return 0.5
    
    async def _assess_creativity(self, generated_text: str, prompt: str) -> float:
        """Assess creativity of generated content"""



        try:
            # Measure diversity of vocabulary
            words = generated_text.lower().split()
            unique_words = set(words)
            vocabulary_diversity = len(unique_words) / len(words) if words else 0
            
            # Measure sentence structure variety
            sentences = generated_text.split('.')
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            length_variance = np.var(sentence_lengths) if sentence_lengths else 0
            
            # Normalize and combine scores
            creativity_score = (
                vocabulary_diversity * 0.6 +
                min(1.0, length_variance / 20) * 0.4
            )
            
            return max(0.0, min(1.0, creativity_score))
            
        except Exception as e:
            logger.warning(f"Creativity assessment failed: {e}")
            return 0.5
    
    async def _assess_relevance(self, generated_text: str, prompt: str) -> float:
        """Assess relevance of generated content to prompt"""



        return await self._calculate_text_similarity(generated_text, prompt)
    
    async def _update_generation_stats(self, result: GenerationResult):
        """Update generation statistics"""
        self.generation_stats["total_generations"] += 1
        if result.quality_score >= self.quality_thresholds['minimum_quality']:
            self.generation_stats["successful_generations"] += 1
        
        # Update average quality score
        total_quality = (
            self.generation_stats["average_quality_score"] * 
            (self.generation_stats["total_generations"] - 1) +
            result.quality_score
        )
        self.generation_stats["average_quality_score"] = total_quality / self.generation_stats["total_generations"]
        
        # Update word count
        self.generation_stats["total_words_generated"] += len(result.generated_text.split())
        
        # Update model usage
        model = result.model_used
        self.generation_stats["model_usage"][model] = self.generation_stats["model_usage"].get(model, 0) + 1
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""



        return {
            **self.generation_stats,
            "success_rate": (
                self.generation_stats["successful_generations"] / 
                max(1, self.generation_stats["total_generations"])
            )
        }


class ContentSynthesizer:
    """
    Advanced content synthesis system for combining and transforming text content
    """
    
    def __init__(self):
        self.generator = AITextGenerator()
        self.processor = TextProcessor()
        logger.info("ContentSynthesizer initialized")
    
    async def synthesize_content(
        self,
        source_texts: List[str],
        synthesis_type: str = "summary",
        target_length: int = 300
    ) -> Dict[str, Any]:
        """
        Synthesize content from multiple source texts
        
        Args:
            source_texts: List of source texts to synthesize
            synthesis_type: Type of synthesis (summary, comparison, fusion)
            target_length: Target length of synthesized content
            
        Returns:
            Dict containing synthesized content and metadata
        """



        try:
            if not source_texts:
                raise ValidationError("No source texts provided for synthesis")
            
            synthesis_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Process source texts
            processed_sources = []
            for text in source_texts:
                processed = await self.processor.process_text(text)
                processed_sources.append(processed.processed_text)
            
            # Generate synthesis based on type
            if synthesis_type == "summary":
                synthesized_content = await self._synthesize_summary(processed_sources, target_length)
            elif synthesis_type == "comparison":
                synthesized_content = await self._synthesize_comparison(processed_sources, target_length)
            elif synthesis_type == "fusion":
                synthesized_content = await self._synthesize_fusion(processed_sources, target_length)
            else:
                synthesized_content = await self._synthesize_summary(processed_sources, target_length)
            
            synthesis_time = time.time() - start_time
            
            result = {
                'synthesis_id': synthesis_id,
                'synthesized_content': synthesized_content,
                'source_count': len(source_texts),
                'synthesis_type': synthesis_type,
                'target_length': target_length,
                'actual_length': len(synthesized_content.split()),
                'synthesis_time': synthesis_time,
                'metadata': {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_lengths': [len(text.split()) for text in source_texts]
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error synthesizing content: {e}")
            raise ProcessingError(f"Content synthesis failed: {e}")
    
    async def _synthesize_summary(self, sources: List[str], target_length: int) -> str:
        """Synthesize content by creating a comprehensive summary"""
        # Combine all sources
        combined_text = " ".join(sources)
        
        # Generate summary using BART model
        if hasattr(self.generator, 'summarization_pipeline'):
            summary = self.generator.summarization_pipeline(
                combined_text,
                max_length=target_length,
                min_length=target_length // 2,
                do_sample=False
            )
            if summary and len(summary) > 0:
                return summary[0]['summary_text']
        
        # Fallback: Extract key sentences
        return await self._extract_key_sentences(combined_text, target_length)
    
    async def _synthesize_comparison(self, sources: List[str], target_length: int) -> str:
        """Synthesize content by comparing sources"""
        comparison_prompt = f"""
        Compare and contrast the following texts, highlighting key similarities and differences:
        
        Text 1: {sources[0]}
        Text 2: {sources[1] if len(sources) > 1 else "No second text"}
        
        Provide a balanced comparison in approximately {target_length} words.
        """
        
        config = GenerationConfig(
            max_length=target_length + 50,
            min_length=target_length - 50,
            generation_type=GenerationType.INFORMATIVE,
            writing_style=WritingStyle.PROFESSIONAL
        )
        
        result = await self.generator.generate_content(comparison_prompt, config)
        return result.generated_text
    
    async def _synthesize_fusion(self, sources: List[str], target_length: int) -> str:
        """Synthesize content by fusing sources into coherent narrative"""
        fusion_prompt = f"""
        Create a coherent narrative that incorporates elements from the following texts:
        
        {' '.join(f'Source {i+1}: {text}' for i, text in enumerate(sources))}
        
        Blend these sources into a unified text of approximately {target_length} words.
        """
        
        config = GenerationConfig(
            max_length=target_length + 50,
            min_length=target_length - 50,
            generation_type=GenerationType.CREATIVE,
            writing_style=WritingStyle.PROFESSIONAL
        )
        
        result = await self.generator.generate_content(fusion_prompt, config)
        return result.generated_text
    
    async def _extract_key_sentences(self, text: str, target_length: int) -> str:
        """Extract key sentences to reach target length"""
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple extraction based on position and length
        key_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_length + sentence_words <= target_length:
                key_sentences.append(sentence)
                current_length += sentence_words
            else:
                break
        
        return '. '.join(key_sentences) + '.' if key_sentences else text[:target_length*5]
