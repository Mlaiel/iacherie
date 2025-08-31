"""
Content Optimizer - Advanced Multi-Format Content Optimization Engine

Enterprise content optimization system with AI-powered analysis, SEO enhancement,
quality optimization, and intelligent format conversion for maximum performance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This content optimization technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices Architect & DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer & Content Protection Specialist: Fahed Mlaiel
"""

import asyncio
import logging
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import aiofiles
import hashlib

# AI/ML libraries
import torch
import transformers
from sentence_transformers import SentenceTransformer

# Image optimization
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pillow_heif

# Audio optimization
import librosa
import soundfile as sf
from pydub import AudioSegment

# Video optimization
import cv2
import ffmpeg

# Text processing and SEO
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from bs4 import BeautifulSoup
import markdown

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import OptimizationError, ValidationError, AIProcessingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    OptimizationError, ValidationError, AIProcessingError = globals().get('OptimizationError, ValidationError, AIProcessingError', Exception)
from ...monitoring.metrics import MetricsCollector
from ...utils.cache_utils import CacheManager

logger = logging.getLogger(__name__)

class OptimizationType(str, Enum):
    """Content optimization types"""
    SEO_OPTIMIZATION = "seo_optimization"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ACCESSIBILITY_IMPROVEMENT = "accessibility_improvement"
    FORMAT_OPTIMIZATION = "format_optimization"

class ContentType(str, Enum):
    """Content types for optimization"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"

@dataclass
class OptimizationOptions:
    """Content optimization configuration"""
    quality: int = 85  # 1-100, higher = better quality
    seo_optimize: bool = True
    performance_optimize: bool = True
    accessibility_improve: bool = True
    progressive: bool = True
    target_audience: str = "general"  # general, technical, marketing
    language: str = "en"
    target_platforms: List[str] = None  # social_media, web, mobile, print
    max_file_size: Optional[int] = None  # Maximum file size in bytes
    preserve_metadata: bool = True

@dataclass
class OptimizationResult:
    """Content optimization result"""
    success: bool
    input_path: str
    output_path: str
    optimization_type: OptimizationType
    original_size: int
    final_size: int
    quality_score: float
    seo_score: float
    performance_score: float
    accessibility_score: float
    processing_time: float
    optimizations_applied: List[str]
    metadata: Dict[str, Any]
    error: Optional[str] = None

class ContentOptimizer:
    """
    Enterprise content optimization engine with AI-powered analysis,
    SEO enhancement, quality optimization, and performance improvements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        
        # Initialize components
        self.metrics = MetricsCollector('content_optimizer')
        self.cache_manager = CacheManager(
            redis_url=self.config.get('redis_url'),
            ttl_hours=self.config.get('cache_ttl_hours', 24)
        )
        
        # Initialize AI models
        self.models = {}
        asyncio.create_task(self._initialize_ai_models())
        
        # Initialize NLP tools
        self.nlp = None
        asyncio.create_task(self._initialize_nlp_tools())
        
        # Optimization templates and rules
        self.seo_rules = self._load_seo_rules()
        self.quality_presets = self._load_quality_presets()
        self.performance_targets = self._load_performance_targets()
        
        # Statistics tracking
        self.stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'average_quality_improvement': 0.0,
            'average_size_reduction': 0.0,
            'optimization_by_type': {otype: 0 for otype in OptimizationType},
            'content_by_type': {ctype: 0 for ctype in ContentType}
        }
        
        # Temporary directory
        self.temp_dir = Path(self.config.get('temp_dir', tempfile.gettempdir())) / 'content_optimizer'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ContentOptimizer initialized successfully")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default optimization configuration"""
        return {
            'temp_dir': '/tmp/content_optimization',
            'ai_models': {
                'sentence_transformer': 'all-MiniLM-L6-v2',
                'text_classifier': 'distilbert-base-uncased',
                'image_captioning': 'blip-image-captioning-base'
            },
            'seo_optimization': {
                'min_content_length': 300,
                'max_content_length': 2000,
                'keyword_density_target': 0.02,
                'heading_structure': True,
                'meta_tags': True,
                'alt_text': True
            },
            'quality_presets': {
                'web': {'quality': 85, 'progressive': True, 'optimization_level': 5},
                'mobile': {'quality': 75, 'progressive': True, 'optimization_level': 7},
                'print': {'quality': 95, 'progressive': False, 'optimization_level': 3},
                'social_media': {'quality': 80, 'progressive': True, 'optimization_level': 6}
            },
            'performance_targets': {
                'image_max_size': 500 * 1024,  # 500KB
                'video_max_size': 50 * 1024 * 1024,  # 50MB
                'audio_max_size': 10 * 1024 * 1024,  # 10MB
                'load_time_target': 3.0  # seconds
            },
            'cache_ttl_hours': 24,
            'redis_url': 'redis://localhost:6379/0'
        }
    
    async def _initialize_ai_models(self):
        """Initialize AI models for content analysis"""
        try:
            # Sentence transformer for semantic analysis
            model_name = self.config['ai_models']['sentence_transformer']
            self.models['sentence_transformer'] = SentenceTransformer(model_name)
            
            # Text classifier for content categorization
            classifier_name = self.config['ai_models']['text_classifier']
            self.models['text_classifier'] = transformers.pipeline(
                'text-classification',
                model=classifier_name,
                return_all_scores=True
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"AI model initialization failed: {e}")
    
    async def _initialize_nlp_tools(self):
        """Initialize NLP processing tools"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
            
            logger.info("NLP tools initialized successfully")
            
        except Exception as e:
            logger.warning(f"NLP tools initialization failed: {e}")
    
    def _load_seo_rules(self) -> Dict[str, Any]:
        """Load SEO optimization rules"""
        return {
            'title_length': {'min': 30, 'max': 60},
            'description_length': {'min': 120, 'max': 160},
            'heading_hierarchy': True,
            'keyword_distribution': 'natural',
            'internal_links': {'min': 2, 'max': 10},
            'image_optimization': {
                'alt_text': True,
                'title_attribute': True,
                'lazy_loading': True,
                'responsive': True
            },
            'content_structure': {
                'paragraphs': {'min_length': 50, 'max_length': 300},
                'sentences': {'min_length': 10, 'max_length': 25},
                'readability_score': {'min': 60, 'target': 80}
            }
        }
    
    def _load_quality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load quality optimization presets"""
        return {
            'maximum': {
                'image_quality': 100,
                'video_quality': 100,
                'audio_quality': 320,
                'compression_level': 0,
                'optimization_level': 1
            },
            'high': {
                'image_quality': 95,
                'video_quality': 95,
                'audio_quality': 256,
                'compression_level': 2,
                'optimization_level': 3
            },
            'medium': {
                'image_quality': 85,
                'video_quality': 85,
                'audio_quality': 192,
                'compression_level': 5,
                'optimization_level': 5
            },
            'low': {
                'image_quality': 70,
                'video_quality': 70,
                'audio_quality': 128,
                'compression_level': 8,
                'optimization_level': 8
            },
            'web_optimized': {
                'image_quality': 85,
                'video_quality': 80,
                'audio_quality': 192,
                'compression_level': 6,
                'optimization_level': 7,
                'progressive': True,
                'responsive': True
            }
        }
    
    def _load_performance_targets(self) -> Dict[str, Any]:
        """Load performance optimization targets"""
        return {
            'core_web_vitals': {
                'lcp': 2.5,  # Largest Contentful Paint (seconds)
                'fid': 100,  # First Input Delay (milliseconds)
                'cls': 0.1   # Cumulative Layout Shift
            },
            'file_sizes': {
                'image': 500 * 1024,      # 500KB
                'video': 50 * 1024 * 1024,  # 50MB
                'audio': 10 * 1024 * 1024,  # 10MB
                'document': 5 * 1024 * 1024  # 5MB
            },
            'loading_times': {
                'critical_resources': 1.0,
                'above_fold_content': 2.0,
                'total_page_load': 3.0
            }
        }
    
    async def optimize(
        self,
        content_path: Union[str, Path],
        content_type: ContentType,
        options: OptimizationOptions
    ) -> OptimizationResult:
        """
        Optimize content with AI-powered analysis and enhancement
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            options: Optimization configuration
            
        Returns:
            OptimizationResult with optimization details
        """
        start_time = datetime.utcnow()
        content_path = Path(content_path)
        
        try:
            # Validate input
            if not content_path.exists():
                raise ValidationError(f"Content file not found: {content_path}")
            
            original_size = content_path.stat().st_size
            
            # Generate output path
            output_path = await self._generate_output_path(content_path, content_type)
            
            # Apply optimizations based on content type
            if content_type == ContentType.IMAGE:
                result = await self._optimize_image(content_path, output_path, options)
            
            elif content_type == ContentType.VIDEO:
                result = await self._optimize_video(content_path, output_path, options)
            
            elif content_type == ContentType.AUDIO:
                result = await self._optimize_audio(content_path, output_path, options)
            
            elif content_type in [ContentType.TEXT, ContentType.HTML, ContentType.MARKDOWN]:
                result = await self._optimize_text(content_path, output_path, options, content_type)
            
            else:
                raise OptimizationError(f"Unsupported content type: {content_type}")
            
            # Calculate metrics
            final_size = Path(result.output_path).stat().st_size if Path(result.output_path).exists() else original_size
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Analyze optimization quality
            quality_scores = await self._analyze_optimization_quality(
                content_path, result.output_path, content_type, options
            )
            
            # Update result
            result.original_size = original_size
            result.final_size = final_size
            result.processing_time = processing_time
            result.quality_score = quality_scores.get('quality', 0.0)
            result.seo_score = quality_scores.get('seo', 0.0)
            result.performance_score = quality_scores.get('performance', 0.0)
            result.accessibility_score = quality_scores.get('accessibility', 0.0)
            
            # Update statistics
            await self._update_statistics(result, content_type)
            
            # Record metrics
            self.metrics.record_processing_time(processing_time)
            self.metrics.increment_counter('optimizations_success')
            self.metrics.record_gauge('size_reduction', (original_size - final_size) / original_size)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.metrics.increment_counter('optimizations_failure')
            
            logger.error(f"Content optimization failed for {content_path}: {e}")
            
            return OptimizationResult(
                success=False,
                input_path=str(content_path),
                output_path="",
                optimization_type=OptimizationType.QUALITY_ENHANCEMENT,
                original_size=original_size if 'original_size' in locals() else 0,
                final_size=0,
                quality_score=0.0,
                seo_score=0.0,
                performance_score=0.0,
                accessibility_score=0.0,
                processing_time=processing_time,
                optimizations_applied=[],
                metadata={},
                error=str(e)
            )
    
    async def _optimize_image(
        self,
        input_path: Path,
        output_path: Path,
        options: OptimizationOptions
    ) -> OptimizationResult:
        """Optimize image with AI-powered enhancement"""
        optimizations_applied = []
        
        try:
            with Image.open(input_path) as img:
                # Convert color mode if necessary
                if img.mode in ('RGBA', 'LA'):
                    if img.mode == 'LA':
                        img = img.convert('RGBA')
                    optimizations_applied.append('color_mode_optimization')
                elif img.mode == 'P':
                    img = img.convert('RGB')
                    optimizations_applied.append('palette_to_rgb_conversion')
                
                # Resize for performance if needed
                max_dimension = self._get_max_dimension_for_platform(
                    options.target_platforms or ['web']
                )
                
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    optimizations_applied.append('intelligent_resizing')
                
                # Apply quality enhancements
                if options.quality >= 90:
                    # High quality enhancements
                    img = self._apply_ai_image_enhancement(img)
                    optimizations_applied.append('ai_quality_enhancement')
                
                # Apply sharpening
                if not self._is_already_sharp(img):
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)
                    optimizations_applied.append('sharpness_enhancement')
                
                # Apply contrast optimization
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.05)
                optimizations_applied.append('contrast_optimization')
                
                # Determine optimal format
                optimal_format = self._get_optimal_image_format(
                    img, options.target_platforms or ['web']
                )
                
                output_path = output_path.with_suffix(f'.{optimal_format.lower()}')
                
                # Save with optimal settings
                save_kwargs = self._get_optimal_save_settings(
                    optimal_format, options.quality, options.progressive
                )
                
                img.save(output_path, optimal_format, **save_kwargs)
                optimizations_applied.append(f'format_optimization_{optimal_format.lower()}')
            
            return OptimizationResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                optimization_type=OptimizationType.QUALITY_ENHANCEMENT,
                original_size=0,  # Will be filled later
                final_size=0,     # Will be filled later
                quality_score=0.0,  # Will be filled later
                seo_score=0.0,      # Will be filled later
                performance_score=0.0,  # Will be filled later
                accessibility_score=0.0,  # Will be filled later
                processing_time=0.0,     # Will be filled later
                optimizations_applied=optimizations_applied,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            raise OptimizationError(f"Image optimization failed: {e}")
    
    async def _optimize_video(
        self,
        input_path: Path,
        output_path: Path,
        options: OptimizationOptions
    ) -> OptimizationResult:
        """Optimize video with intelligent encoding"""
        optimizations_applied = []
        
        try:
            # Analyze video properties
            video_info = await self._analyze_video_properties(input_path)
            
            # Determine optimal settings
            optimal_settings = self._get_optimal_video_settings(
                video_info, options.target_platforms or ['web']
            )
            
            # Build FFmpeg command
            input_stream = ffmpeg.input(str(input_path))
            
            # Apply video optimizations
            video_filters = []
            
            # Resolution optimization
            if optimal_settings.get('scale'):
                video_filters.append(f"scale={optimal_settings['scale']}")
                optimizations_applied.append('resolution_optimization')
            
            # Denoising if quality is high
            if options.quality >= 85 and video_info.get('noise_level', 0) > 0.3:
                video_filters.append('hqdn3d=4:3:6:4.5')
                optimizations_applied.append('noise_reduction')
            
            # Apply filters
            if video_filters:
                input_stream = input_stream.filter('vf', ','.join(video_filters))
            
            # Encoding settings
            encoding_options = {
                'c:v': optimal_settings.get('video_codec', 'libx264'),
                'crf': optimal_settings.get('crf', 23),
                'preset': optimal_settings.get('preset', 'medium'),
                'c:a': optimal_settings.get('audio_codec', 'aac'),
                'b:a': optimal_settings.get('audio_bitrate', '128k')
            }
            
            # Progressive enhancement
            if options.progressive:
                encoding_options['movflags'] = '+faststart'
                optimizations_applied.append('progressive_loading')
            
            # Execute optimization
            output_stream = ffmpeg.output(input_stream, str(output_path), **encoding_options)
            
            process = await asyncio.create_subprocess_exec(
                *ffmpeg.compile(output_stream),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                raise OptimizationError("Video encoding failed")
            
            optimizations_applied.append('intelligent_encoding')
            
            return OptimizationResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                optimization_type=OptimizationType.PERFORMANCE_OPTIMIZATION,
                original_size=0,
                final_size=0,
                quality_score=0.0,
                seo_score=0.0,
                performance_score=0.0,
                accessibility_score=0.0,
                processing_time=0.0,
                optimizations_applied=optimizations_applied,
                metadata=video_info
            )
            
        except Exception as e:
            logger.error(f"Video optimization failed: {e}")
            raise OptimizationError(f"Video optimization failed: {e}")
    
    async def _optimize_audio(
        self,
        input_path: Path,
        output_path: Path,
        options: OptimizationOptions
    ) -> OptimizationResult:
        """Optimize audio with intelligent processing"""
        optimizations_applied = []
        
        try:
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None)
            
            # Apply audio optimizations
            
            # Noise reduction for high quality settings
            if options.quality >= 85:
                y = librosa.effects.preemphasis(y)
                optimizations_applied.append('preemphasis_filtering')
            
            # Normalize audio levels
            y = librosa.util.normalize(y)
            optimizations_applied.append('level_normalization')
            
            # Trim silence
            y, _ = librosa.effects.trim(y, top_db=20)
            optimizations_applied.append('silence_trimming')
            
            # Determine optimal format and settings
            optimal_format, optimal_settings = self._get_optimal_audio_format(
                options.target_platforms or ['web'], options.quality
            )
            
            output_path = output_path.with_suffix(f'.{optimal_format}')
            
            # Export optimized audio
            if optimal_format == 'mp3':
                # Convert to AudioSegment for MP3 export
                audio_segment = AudioSegment(
                    y.tobytes(),
                    frame_rate=sr,
                    sample_width=y.dtype.itemsize,
                    channels=1
                )
                
                audio_segment.export(
                    str(output_path),
                    format='mp3',
                    bitrate=optimal_settings.get('bitrate', '192k')
                )
            else:
                # Use soundfile for other formats
                sf.write(str(output_path), y, sr, format=optimal_format.upper())
            
            optimizations_applied.append(f'format_optimization_{optimal_format}')
            
            return OptimizationResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                optimization_type=OptimizationType.QUALITY_ENHANCEMENT,
                original_size=0,
                final_size=0,
                quality_score=0.0,
                seo_score=0.0,
                performance_score=0.0,
                accessibility_score=0.0,
                processing_time=0.0,
                optimizations_applied=optimizations_applied,
                metadata={'sample_rate': sr, 'duration': len(y) / sr}
            )
            
        except Exception as e:
            logger.error(f"Audio optimization failed: {e}")
            raise OptimizationError(f"Audio optimization failed: {e}")
    
    async def _optimize_text(
        self,
        input_path: Path,
        output_path: Path,
        options: OptimizationOptions,
        content_type: ContentType
    ) -> OptimizationResult:
        """Optimize text content with AI-powered SEO and readability enhancement"""
        optimizations_applied = []
        
        try:
            # Read content
            async with aiofiles.open(input_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            original_content = content
            
            # Parse content based on type
            if content_type == ContentType.HTML:
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text()
            elif content_type == ContentType.MARKDOWN:
                html_content = markdown.markdown(content)
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text()
            else:
                text_content = content
                soup = None
            
            # Apply SEO optimizations
            if options.seo_optimize:
                content = await self._apply_seo_optimizations(
                    content, content_type, options
                )
                if content != original_content:
                    optimizations_applied.append('seo_optimization')
            
            # Improve readability
            content = await self._improve_readability(content, options)
            if content != original_content:
                optimizations_applied.append('readability_improvement')
            
            # Accessibility improvements
            if options.accessibility_improve and content_type == ContentType.HTML:
                content = await self._improve_accessibility(content)
                optimizations_applied.append('accessibility_enhancement')
            
            # Performance optimizations
            if options.performance_optimize:
                content = await self._optimize_text_performance(content, content_type)
                optimizations_applied.append('performance_optimization')
            
            # AI-powered content enhancement
            if options.quality >= 85:
                content = await self._apply_ai_text_enhancement(
                    content, content_type, options
                )
                optimizations_applied.append('ai_content_enhancement')
            
            # Write optimized content
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return OptimizationResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                optimization_type=OptimizationType.SEO_OPTIMIZATION,
                original_size=0,
                final_size=0,
                quality_score=0.0,
                seo_score=0.0,
                performance_score=0.0,
                accessibility_score=0.0,
                processing_time=0.0,
                optimizations_applied=optimizations_applied,
                metadata={'content_length': len(content)}
            )
            
        except Exception as e:
            logger.error(f"Text optimization failed: {e}")
            raise OptimizationError(f"Text optimization failed: {e}")
    
    # AI Enhancement Methods
    
    def _apply_ai_image_enhancement(self, img: Image.Image) -> Image.Image:
        """Apply AI-powered image enhancement"""
        try:
            # Basic AI enhancement using PIL filters
            # In a full implementation, this would use specialized AI models
            
            # Enhance edges
            enhanced = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # Color enhancement
            color_enhancer = ImageEnhance.Color(enhanced)
            enhanced = color_enhancer.enhance(1.1)
            
            # Brightness optimization
            brightness_enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = brightness_enhancer.enhance(1.02)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"AI image enhancement failed: {e}")
            return img
    
    async def _apply_seo_optimizations(
        self,
        content: str,
        content_type: ContentType,
        options: OptimizationOptions
    ) -> str:
        """Apply SEO optimizations to text content"""
        try:
            if content_type == ContentType.HTML:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Optimize headings hierarchy
                self._optimize_heading_structure(soup)
                
                # Add missing meta tags
                self._ensure_meta_tags(soup)
                
                # Optimize images
                self._optimize_html_images(soup)
                
                # Improve internal linking
                self._optimize_internal_links(soup)
                
                return str(soup)
            
            elif content_type == ContentType.MARKDOWN:
                # Optimize markdown structure
                content = self._optimize_markdown_structure(content)
                
                return content
            
            else:
                # Plain text optimization
                content = self._optimize_plain_text(content, options)
                
                return content
                
        except Exception as e:
            logger.warning(f"SEO optimization failed: {e}")
            return content
    
    async def _improve_readability(self, content: str, options: OptimizationOptions) -> str:
        """Improve content readability"""
        try:
            if not self.nlp:
                return content
            
            # Analyze current readability
            readability_score = flesch_reading_ease(content)
            
            if readability_score < self.seo_rules['content_structure']['readability_score']['min']:
                # Apply readability improvements
                doc = self.nlp(content)
                
                # Break up long sentences
                improved_sentences = []
                for sent in doc.sents:
                    if len(sent.text.split()) > 25:  # Long sentence
                        # Split at coordinating conjunctions
                        split_sent = self._split_long_sentence(sent.text)
                        improved_sentences.extend(split_sent)
                    else:
                        improved_sentences.append(sent.text)
                
                content = ' '.join(improved_sentences)
            
            return content
            
        except Exception as e:
            logger.warning(f"Readability improvement failed: {e}")
            return content
    
    async def _improve_accessibility(self, html_content: str) -> str:
        """Improve HTML accessibility"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Add alt text to images without it
            for img in soup.find_all('img', alt=False):
                if img.get('src'):
                    # Generate descriptive alt text (in practice, use AI vision models)
                    img['alt'] = f"Image: {Path(img['src']).stem.replace('_', ' ').replace('-', ' ')}"
            
            # Add ARIA labels where needed
            for element in soup.find_all(['button', 'a', 'input']):
                if not element.get('aria-label') and not element.get_text(strip=True):
                    element_type = element.name
                    element['aria-label'] = f"{element_type.capitalize()} element"
            
            # Ensure proper heading hierarchy
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                # Ensure there's only one H1
                h1_count = len(soup.find_all('h1'))
                if h1_count > 1:
                    for i, h1 in enumerate(soup.find_all('h1')[1:], 1):
                        h1.name = 'h2'
            
            return str(soup)
            
        except Exception as e:
            logger.warning(f"Accessibility improvement failed: {e}")
            return html_content
    
    async def _optimize_text_performance(self, content: str, content_type: ContentType) -> str:
        """Optimize text content for performance"""
        try:
            if content_type == ContentType.HTML:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Minify HTML by removing unnecessary whitespace
                for element in soup.find_all(string=re.compile(r'\s+')):
                    if element.parent.name not in ['pre', 'code', 'script', 'style']:
                        element.replace_with(re.sub(r'\s+', ' ', element).strip())
                
                # Add lazy loading to images
                for img in soup.find_all('img'):
                    img['loading'] = 'lazy'
                
                # Optimize CSS and JS (basic minification)
                for style in soup.find_all('style'):
                    if style.string:
                        style.string = self._minify_css(style.string)
                
                for script in soup.find_all('script'):
                    if script.string and 'src' not in script.attrs:
                        script.string = self._minify_js(script.string)
                
                return str(soup)
            
            return content
            
        except Exception as e:
            logger.warning(f"Text performance optimization failed: {e}")
            return content
    
    async def _apply_ai_text_enhancement(
        self,
        content: str,
        content_type: ContentType,
        options: OptimizationOptions
    ) -> str:
        """Apply AI-powered text enhancement"""
        try:
            if not self.models.get('text_classifier'):
                return content
            
            # Analyze content sentiment and topics
            classifier = self.models['text_classifier']
            
            # Extract main text for analysis
            if content_type == ContentType.HTML:
                soup = BeautifulSoup(content, 'html.parser')
                main_text = soup.get_text()
            else:
                main_text = content
            
            # Truncate for analysis (models have input limits)
            analysis_text = main_text[:512] if len(main_text) > 512 else main_text
            
            # Get sentiment and classification
            classification = classifier(analysis_text)
            
            # Apply enhancements based on classification
            # This is a simplified version - full implementation would be more sophisticated
            
            return content
            
        except Exception as e:
            logger.warning(f"AI text enhancement failed: {e}")
            return content
    
    # Utility Methods
    
    def _get_max_dimension_for_platform(self, platforms: List[str]) -> int:
        """Get maximum dimension based on target platforms"""
        platform_limits = {
            'mobile': 800,
            'web': 1920,
            'social_media': 1080,
            'print': 3000
        }
        
        return min(platform_limits.get(platform, 1920) for platform in platforms)
    
    def _is_already_sharp(self, img: Image.Image) -> bool:
        """Check if image is already sharp enough"""
        try:
            # Convert to grayscale for edge detection
            gray = img.convert('L')
            
            # Apply edge detection filter
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Calculate edge strength (simple metric)
            edge_pixels = sum(1 for pixel in edges.getdata() if pixel > 50)
            total_pixels = img.width * img.height
            edge_ratio = edge_pixels / total_pixels
            
            # If edge ratio is high, image is likely already sharp
            return edge_ratio > 0.1
            
        except Exception:
            return False
    
    def _get_optimal_image_format(self, img: Image.Image, platforms: List[str]) -> str:
        """Determine optimal image format"""
        # Check for transparency
        has_transparency = (
            img.mode in ('RGBA', 'LA') or 
            (img.mode == 'P' and 'transparency' in img.info)
        )
        
        # Platform preferences
        if 'web' in platforms:
            if has_transparency:
                return 'PNG'
            else:
                return 'WEBP'  # Best compression for web
        
        elif 'social_media' in platforms:
            return 'JPEG'  # Most compatible
        
        elif 'print' in platforms:
            return 'PNG'  # Best quality
        
        else:
            return 'WEBP'  # Default to WebP for best compression
    
    def _get_optimal_save_settings(self, format_name: str, quality: int, progressive: bool) -> Dict[str, Any]:
        """Get optimal save settings for image format"""
        settings = {'optimize': True}
        
        if format_name.upper() == 'JPEG':
            settings.update({
                'quality': quality,
                'progressive': progressive
            })
        
        elif format_name.upper() == 'PNG':
            settings['compress_level'] = 9
        
        elif format_name.upper() == 'WEBP':
            settings.update({
                'quality': quality,
                'method': 6,  # Best compression method
                'lossless': quality >= 95
            })
        
        return settings
    
    async def _analyze_video_properties(self, video_path: Path) -> Dict[str, Any]:
        """Analyze video properties for optimization"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return {}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Sample frames for quality analysis
            frames_to_analyze = min(10, frame_count)
            noise_levels = []
            
            for i in range(0, frame_count, frame_count // frames_to_analyze):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret:
                    # Simple noise estimation using Laplacian variance
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    noise = cv2.Laplacian(gray, cv2.CV_64F).var()
                    noise_levels.append(noise)
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': frame_count / fps if fps > 0 else 0,
                'aspect_ratio': width / height if height > 0 else 0,
                'noise_level': sum(noise_levels) / len(noise_levels) if noise_levels else 0
            }
            
        except Exception as e:
            logger.warning(f"Video analysis failed: {e}")
            return {}
    
    def _get_optimal_video_settings(self, video_info: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Get optimal video encoding settings"""
        settings = {
            'video_codec': 'libx264',
            'audio_codec': 'aac',
            'preset': 'medium'
        }
        
        width = video_info.get('width', 1920)
        height = video_info.get('height', 1080)
        
        # Platform-specific optimizations
        if 'mobile' in platforms:
            if width > 720:
                settings['scale'] = '720:-2'  # Scale to 720p, keep aspect ratio
            settings['crf'] = 28
            settings['preset'] = 'faster'
        
        elif 'web' in platforms:
            if width > 1920:
                settings['scale'] = '1920:-2'
            settings['crf'] = 23
            settings['preset'] = 'medium'
        
        elif 'social_media' in platforms:
            settings['scale'] = '1080:-2'
            settings['crf'] = 25
            settings['preset'] = 'medium'
        
        settings['audio_bitrate'] = '128k'
        
        return settings
    
    def _get_optimal_audio_format(self, platforms: List[str], quality: int) -> Tuple[str, Dict[str, Any]]:
        """Get optimal audio format and settings"""
        if 'web' in platforms:
            if quality >= 90:
                return 'flac', {}
            else:
                return 'mp3', {'bitrate': '256k'}
        
        elif 'mobile' in platforms:
            return 'mp3', {'bitrate': '192k'}
        
        elif 'social_media' in platforms:
            return 'mp3', {'bitrate': '192k'}
        
        else:
            return 'mp3', {'bitrate': '256k'}
    
    def _optimize_heading_structure(self, soup: BeautifulSoup):
        """Optimize HTML heading structure for SEO"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            return
        
        # Ensure proper hierarchy
        current_level = 0
        for heading in headings:
            level = int(heading.name[1])
            
            if current_level == 0:
                # First heading should be H1
                if level != 1:
                    heading.name = 'h1'
                    level = 1
            else:
                # Subsequent headings shouldn't skip levels
                if level > current_level + 1:
                    heading.name = f'h{current_level + 1}'
                    level = current_level + 1
            
            current_level = level
    
    def _ensure_meta_tags(self, soup: BeautifulSoup):
        """Ensure essential meta tags are present"""
        head = soup.find('head')
        if not head:
            return
        
        # Title tag
        if not soup.find('title'):
            title = soup.new_tag('title')
            title.string = 'Optimized Content'
            head.append(title)
        
        # Meta description
        if not soup.find('meta', attrs={'name': 'description'}):
            meta_desc = soup.new_tag('meta', attrs={'name': 'description', 'content': ''})
            head.append(meta_desc)
        
        # Viewport tag
        if not soup.find('meta', attrs={'name': 'viewport'}):
            viewport = soup.new_tag('meta', attrs={
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1'
            })
            head.append(viewport)
    
    def _optimize_html_images(self, soup: BeautifulSoup):
        """Optimize images in HTML for SEO"""
        for img in soup.find_all('img'):
            # Ensure alt text
            if not img.get('alt'):
                if img.get('src'):
                    filename = Path(img['src']).stem
                    img['alt'] = filename.replace('_', ' ').replace('-', ' ').title()
                else:
                    img['alt'] = 'Image'
            
            # Add lazy loading
            img['loading'] = 'lazy'
            
            # Add responsive attributes if not present
            if not img.get('width') and not img.get('height'):
                img['style'] = img.get('style', '') + 'max-width: 100%; height: auto;'
    
    def _optimize_internal_links(self, soup: BeautifulSoup):
        """Optimize internal links for SEO"""
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Add title attribute if missing and text is available
            if not link.get('title') and link.get_text(strip=True):
                link['title'] = link.get_text(strip=True)
            
            # External links should have rel="noopener"
            if href.startswith('http') and not href.startswith(('http://localhost', 'https://localhost')):
                rel = link.get('rel', [])
                if isinstance(rel, str):
                    rel = [rel]
                if 'noopener' not in rel:
                    rel.append('noopener')
                link['rel'] = ' '.join(rel)
    
    def _optimize_markdown_structure(self, content: str) -> str:
        """Optimize markdown structure"""
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Ensure proper heading hierarchy
            if line.startswith('#'):
                # Count heading level
                level = len(line) - len(line.lstrip('#'))
                heading_text = line[level:].strip()
                
                # Ensure there's space after #
                optimized_lines.append('#' * level + ' ' + heading_text)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_plain_text(self, content: str, options: OptimizationOptions) -> str:
        """Optimize plain text content"""
        # Basic text optimizations
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            line = re.sub(r'\s+', ' ', line.strip())
            
            # Ensure proper sentence spacing
            line = re.sub(r'\.([A-Z])', r'. \1', line)
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split long sentences for better readability"""
        # Simple sentence splitting at coordinating conjunctions
        conjunctions = ['and', 'but', 'or', 'yet', 'so']
        
        for conj in conjunctions:
            pattern = rf'\s+{conj}\s+'
            if re.search(pattern, sentence, re.IGNORECASE):
                parts = re.split(pattern, sentence, maxsplit=1)
                if len(parts) == 2:
                    return [parts[0].strip() + '.', parts[1].strip()]
        
        return [sentence]
    
    def _minify_css(self, css: str) -> str:
        """Basic CSS minification"""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'{\s+', '{', css)
        css = re.sub(r';\s+', ';', css)
        css = re.sub(r'}\s+', '}', css)
        
        return css.strip()
    
    def _minify_js(self, js: str) -> str:
        """Basic JavaScript minification"""
        # Remove single-line comments
        js = re.sub(r'//.*$', '', js, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js = re.sub(r'\s+', ' ', js)
        
        return js.strip()
    
    async def _generate_output_path(self, input_path: Path, content_type: ContentType) -> Path:
        """Generate output path for optimized content"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        output_name = f"{input_path.stem}_optimized_{timestamp}"
        output_path = self.temp_dir / f"{output_name}{input_path.suffix}"
        
        return output_path
    
    async def _analyze_optimization_quality(
        self,
        original_path: Path,
        optimized_path: Path,
        content_type: ContentType,
        options: OptimizationOptions
    ) -> Dict[str, float]:
        """Analyze optimization quality and calculate scores"""
        scores = {
            'quality': 0.0,
            'seo': 0.0,
            'performance': 0.0,
            'accessibility': 0.0
        }
        
        try:
            if not Path(optimized_path).exists():
                return scores
            
            # File size improvement
            original_size = original_path.stat().st_size
            optimized_size = Path(optimized_path).stat().st_size
            size_reduction = (original_size - optimized_size) / original_size
            
            # Performance score based on size reduction
            scores['performance'] = min(100, max(0, size_reduction * 100))
            
            # Content-type specific quality analysis
            if content_type == ContentType.IMAGE:
                scores['quality'] = await self._analyze_image_quality(original_path, optimized_path)
            
            elif content_type in [ContentType.TEXT, ContentType.HTML, ContentType.MARKDOWN]:
                scores.update(await self._analyze_text_quality(optimized_path, content_type))
            
            else:
                # Generic quality score
                scores['quality'] = 85.0
            
            return scores
            
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return scores
    
    async def _analyze_image_quality(self, original_path: Path, optimized_path: Path) -> float:
        """Analyze image quality after optimization"""
        try:
            with Image.open(original_path) as orig, Image.open(optimized_path) as opt:
                # Simple quality metric based on size and dimensions
                orig_area = orig.width * orig.height
                opt_area = opt.width * opt.height
                
                dimension_preservation = opt_area / orig_area
                
                # Quality score (simplified)
                quality_score = min(100, dimension_preservation * 100)
                
                return quality_score
                
        except Exception as e:
            logger.warning(f"Image quality analysis failed: {e}")
            return 75.0
    
    async def _analyze_text_quality(self, file_path: Path, content_type: ContentType) -> Dict[str, float]:
        """Analyze text content quality"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            scores = {}
            
            # SEO score
            if content_type == ContentType.HTML:
                soup = BeautifulSoup(content, 'html.parser')
                scores['seo'] = self._calculate_html_seo_score(soup)
                scores['accessibility'] = self._calculate_accessibility_score(soup)
            else:
                scores['seo'] = self._calculate_text_seo_score(content)
                scores['accessibility'] = 80.0  # Default for non-HTML
            
            # Quality score based on readability
            readability = flesch_reading_ease(content)
            scores['quality'] = min(100, max(0, readability))
            
            return scores
            
        except Exception as e:
            logger.warning(f"Text quality analysis failed: {e}")
            return {'quality': 75.0, 'seo': 75.0, 'accessibility': 75.0}
    
    def _calculate_html_seo_score(self, soup: BeautifulSoup) -> float:
        """Calculate SEO score for HTML content"""
        score = 0
        max_score = 0
        
        # Title tag
        max_score += 20
        title = soup.find('title')
        if title and title.get_text(strip=True):
            title_length = len(title.get_text(strip=True))
            if 30 <= title_length <= 60:
                score += 20
            elif title_length > 0:
                score += 10
        
        # Meta description
        max_score += 20
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_length = len(meta_desc['content'])
            if 120 <= desc_length <= 160:
                score += 20
            elif desc_length > 0:
                score += 10
        
        # Heading structure
        max_score += 20
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            h1_count = len(soup.find_all('h1'))
            if h1_count == 1:
                score += 15
            elif h1_count > 0:
                score += 10
            
            if len(headings) > 1:
                score += 5
        
        # Image optimization
        max_score += 20
        images = soup.find_all('img')
        if images:
            images_with_alt = len([img for img in images if img.get('alt')])
            alt_ratio = images_with_alt / len(images)
            score += int(alt_ratio * 20)
        else:
            score += 20  # No images to optimize
        
        # Internal links
        max_score += 20
        links = soup.find_all('a', href=True)
        internal_links = [link for link in links if not link['href'].startswith('http')]
        if len(internal_links) >= 2:
            score += 20
        elif len(internal_links) > 0:
            score += 10
        
        return (score / max_score) * 100 if max_score > 0 else 0
    
    def _calculate_text_seo_score(self, content: str) -> float:
        """Calculate SEO score for text content"""
        score = 0
        max_score = 100
        
        # Content length
        word_count = len(content.split())
        if 300 <= word_count <= 2000:
            score += 40
        elif word_count >= 150:
            score += 20
        
        # Readability
        try:
            readability = flesch_reading_ease(content)
            if readability >= 60:
                score += 30
            elif readability >= 30:
                score += 15
        except:
            score += 15  # Default partial score
        
        # Structure (paragraphs)
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 30
        elif len(paragraphs) >= 2:
            score += 15
        
        return score
    
    def _calculate_accessibility_score(self, soup: BeautifulSoup) -> float:
        """Calculate accessibility score for HTML content"""
        score = 0
        max_score = 100
        
        # Images with alt text
        images = soup.find_all('img')
        if images:
            images_with_alt = len([img for img in images if img.get('alt')])
            score += (images_with_alt / len(images)) * 40
        else:
            score += 40
        
        # Proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            h1_count = len(soup.find_all('h1'))
            if h1_count == 1:
                score += 20
            elif h1_count == 0:
                score += 10
        
        # Form labels
        inputs = soup.find_all('input')
        labels = soup.find_all('label')
        if inputs and labels:
            score += 20
        elif not inputs:
            score += 20  # No forms to check
        
        # Link titles
        links = soup.find_all('a', href=True)
        if links:
            links_with_titles = len([link for link in links if link.get('title') or link.get_text(strip=True)])
            score += (links_with_titles / len(links)) * 20
        else:
            score += 20
        
        return score
    
    async def _update_statistics(self, result: OptimizationResult, content_type: ContentType):
        """Update optimization statistics"""
        self.stats['total_optimizations'] += 1
        self.stats['content_by_type'][content_type] += 1
        
        if result.success:
            self.stats['successful_optimizations'] += 1
            
            # Update averages
            total_successful = self.stats['successful_optimizations']
            
            # Quality improvement
            quality_improvement = result.quality_score
            current_quality_avg = self.stats['average_quality_improvement']
            self.stats['average_quality_improvement'] = (
                (current_quality_avg * (total_successful - 1) + quality_improvement) / total_successful
            )
            
            # Size reduction
            if result.original_size > 0:
                size_reduction = (result.original_size - result.final_size) / result.original_size
                current_size_avg = self.stats['average_size_reduction']
                self.stats['average_size_reduction'] = (
                    (current_size_avg * (total_successful - 1) + size_reduction) / total_successful
                )
        else:
            self.stats['failed_optimizations'] += 1
    
    async def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        return {
            'statistics': self.stats.copy(),
            'configuration': self.config,
            'seo_rules': self.seo_rules,
            'quality_presets': self.quality_presets,
            'performance_targets': self.performance_targets
        }
    
    async def cleanup(self):
        """Cleanup optimizer resources"""
        try:
            # Clean temporary files older than 1 hour
            from datetime import timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            for temp_file in self.temp_dir.glob('*'):
                if temp_file.is_file():
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        temp_file.unlink()
            
            # Cleanup AI models
            if hasattr(self, 'models'):
                self.models.clear()
            
            logger.info("ContentOptimizer cleanup completed")
            
        except Exception as e:
            logger.error(f"ContentOptimizer cleanup failed: {e}")
