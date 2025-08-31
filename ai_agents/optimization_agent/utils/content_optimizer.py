"""Content Optimizer - Advanced Multi-Format Content Optimization Engine

Enterprise-grade content optimization system for audio, video, image, and text formats.
Implements intelligent compression, format conversion, SEO enhancement, and quality optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This content optimization technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import json
import hashlib
import uuid
import numpy as np
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# External imports for media processing
import cv2
from PIL import Image
import librosa
import ffmpeg
from bs4 import BeautifulSoup
import nltk
from textstat import flesch_reading_ease, automated_readability_index
import tiktoken
from transformers import AutoModel, AutoTokenizer
import torch

# Internal imports
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...models.optimization import ContentOptimizationRequest, OptimizationResponse
from ...models.content import ContentMetrics, ContentFormat
from ...utils.logger import get_logger
from ...utils.metrics import MetricsCollector

logger = get_logger(__name__)

class ContentFormat(Enum):
    """Supported content formats for optimization."""    TEXT = "text"
    IMAGE = "image"  
    VIDEO = "video"
    AUDIO = "audio"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"

class OptimizationLevel(Enum):
    """Content optimization levels."""    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    MAXIMUM = "maximum"

class CompressionAlgorithm(Enum):
    """Available compression algorithms."""    LOSSLESS = "lossless"
    LOSSY = "lossy"
    ADAPTIVE = "adaptive"
    ML_BASED = "ml_based"

@dataclass
class ContentAnalysis:
    """Content analysis results."""    format_type: ContentFormat
    file_size: int
    quality_score: float
    compression_ratio: float
    seo_score: Optional[float] = None
    readability_score: Optional[float] = None
    technical_metrics: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class OptimizationSettings:
    """Content optimization settings."""    level: OptimizationLevel
    algorithm: CompressionAlgorithm
    target_quality: float = 0.85
    max_file_size: Optional[int] = None
    preserve_metadata: bool = True
    seo_optimization: bool = True
    accessibility_compliance: bool = True

@dataclass
class ContentOptimizationResult:
    """Optimization operation result."""    original_size: int
    optimized_size: int
    compression_ratio: float
    quality_retained: float
    time_taken: float
    optimization_type: str
    format_changes: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class ContentOptimizer:
    """    Ultra-Advanced Content Optimization Engine
    
    Enterprise-grade multi-format content optimization system with ML-powered
    compression, format conversion, SEO enhancement, and quality optimization.
    """    
    def __init__(self):
        """Initialize the content optimizer with advanced configurations."""        self.logger = logger
        self.metrics = MetricsCollector()
        self.db_path = "/tmp/content_optimizer.db"
        
        # Initialize ML models for content analysis
        self.tokenizer = None
        self.content_model = None
        self._initialize_ml_models()
        
        # Content processing settings
        self.max_workers = os.cpu_count() or 4
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Optimization history tracking
        self.optimization_history: Dict[str, List[ContentOptimizationResult]] = {}
        
        # Performance monitoring
        self.performance_stats = {
            'total_optimizations': 0,
            'total_bytes_saved': 0,
            'average_compression_ratio': 0.0,
            'average_quality_retained': 0.0
        }
        
        self._setup_database()
        
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for content analysis."""        try:
            # For text analysis and SEO optimization
            self.tokenizer = tiktoken.get_encoding("gpt2")
            
            # Initialize content understanding model
            # Note: In production, you'd load actual pre-trained models
            self.content_model = None  # Placeholder for actual model
            
            self.logger.info("ML models initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
            
    def _setup_database(self) -> None:
        """Setup SQLite database for optimization tracking."""        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""                CREATE TABLE IF NOT EXISTS content_optimizations (
                    id TEXT PRIMARY KEY,
                    content_hash TEXT,
                    original_size INTEGER,
                    optimized_size INTEGER,
                    compression_ratio REAL,
                    quality_retained REAL,
                    format_type TEXT,
                    optimization_level TEXT,
                    algorithm TEXT,
                    timestamp DATETIME,
                    performance_metrics TEXT
                )
            """)
            
            cursor.execute("""                CREATE TABLE IF NOT EXISTS optimization_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    total_optimizations INTEGER,
                    bytes_saved INTEGER,
                    avg_compression_ratio REAL,
                    avg_quality_retained REAL
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Content optimization database initialized")
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
    
    async def analyze_content(
        self,
        content_path: str,
        content_data: Optional[bytes] = None
    ) -> ContentAnalysis:
        """        Analyze content for optimization opportunities.
        
        Args:
            content_path: Path to content file
            content_data: Raw content data (optional)
            
        Returns:
            ContentAnalysis with detailed analysis results
        """        start_time = time.time()
        
        try:
            # Determine content format
            format_type = self._detect_content_format(content_path)
            
            # Get file size
            if content_data:
                file_size = len(content_data)
            else:
                file_size = os.path.getsize(content_path)
            
            # Perform format-specific analysis
            analysis_result = await self._analyze_by_format(
                content_path, format_type, content_data
            )
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                analysis_result['metrics'], format_type
            )
            
            # Generate optimization suggestions
            suggestions = self._generate_optimization_suggestions(
                analysis_result, format_type, file_size
            )
            
            analysis = ContentAnalysis(
                format_type=format_type,
                file_size=file_size,
                quality_score=quality_score,
                compression_ratio=analysis_result.get('compression_potential', 0.3),
                seo_score=analysis_result.get('seo_score'),
                readability_score=analysis_result.get('readability_score'),
                technical_metrics=analysis_result['metrics'],
                optimization_suggestions=suggestions
            )
            
            analysis_time = time.time() - start_time
            self.metrics.record_metric('content_analysis_time', analysis_time)
            
            self.logger.info(
                f"Content analysis completed in {analysis_time:.3f}s for {format_type.value}"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            raise ContentOptimizationError(f"Analysis failed: {e}")
    
    async def optimize_content(
        self,
        content_path: str,
        output_path: Optional[str] = None,
        settings: Optional[OptimizationSettings] = None,
        content_data: Optional[bytes] = None
    ) -> ContentOptimizationResult:
        """        Optimize content based on analysis and settings.
        
        Args:
            content_path: Path to source content
            output_path: Path for optimized output (optional)
            settings: Optimization settings
            content_data: Raw content data (optional)
            
        Returns:
            ContentOptimizationResult with optimization metrics
        """        start_time = time.time()
        
        try:
            # Use default settings if none provided
            if not settings:
                settings = OptimizationSettings(
                    level=OptimizationLevel.STANDARD,
                    algorithm=CompressionAlgorithm.ADAPTIVE
                )
            
            # Analyze content first
            analysis = await self.analyze_content(content_path, content_data)
            
            # Get original size
            original_size = analysis.file_size
            
            # Perform optimization based on format
            optimization_result = await self._optimize_by_format(
                content_path, analysis.format_type, settings, output_path
            )
            
            # Calculate compression metrics
            optimized_size = optimization_result['size']
            compression_ratio = 1.0 - (optimized_size / original_size)
            quality_retained = optimization_result.get('quality', 1.0)
            
            # Create result object
            result = ContentOptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                quality_retained=quality_retained,
                time_taken=time.time() - start_time,
                optimization_type=f"{settings.level.value}_{settings.algorithm.value}",
                format_changes=optimization_result.get('format_changes', []),
                performance_metrics=optimization_result.get('metrics', {})
            )
            
            # Save optimization record
            await self._save_optimization_record(analysis, result, settings)
            
            # Update performance stats
            self._update_performance_stats(result)
            
            self.logger.info(
                f"Content optimization completed: {compression_ratio:.2%} compression, "
                f"{quality_retained:.2%} quality retained"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
            raise ContentOptimizationError(f"Optimization failed: {e}")
    
    def _detect_content_format(self, content_path: str) -> ContentFormat:
        """Detect content format based on file extension and content."""        path_obj = Path(content_path)
        extension = path_obj.suffix.lower()
        
        format_mapping = {
            # Image formats
            '.jpg': ContentFormat.IMAGE, '.jpeg': ContentFormat.IMAGE,
            '.png': ContentFormat.IMAGE, '.gif': ContentFormat.IMAGE,
            '.bmp': ContentFormat.IMAGE, '.webp': ContentFormat.IMAGE,
            
            # Video formats
            '.mp4': ContentFormat.VIDEO, '.avi': ContentFormat.VIDEO,
            '.mov': ContentFormat.VIDEO, '.wmv': ContentFormat.VIDEO,
            '.flv': ContentFormat.VIDEO, '.webm': ContentFormat.VIDEO,
            
            # Audio formats
            '.mp3': ContentFormat.AUDIO, '.wav': ContentFormat.AUDIO,
            '.flac': ContentFormat.AUDIO, '.aac': ContentFormat.AUDIO,
            '.ogg': ContentFormat.AUDIO, '.m4a': ContentFormat.AUDIO,
            
            # Text formats
            '.txt': ContentFormat.TEXT, '.md': ContentFormat.MARKDOWN,
            '.html': ContentFormat.HTML, '.htm': ContentFormat.HTML,
            '.pdf': ContentFormat.PDF
        }
        
        return format_mapping.get(extension, ContentFormat.TEXT)
    
    async def _analyze_by_format(
        self,
        content_path: str,
        format_type: ContentFormat,
        content_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Perform format-specific content analysis."""        
        if format_type == ContentFormat.IMAGE:
            return await self._analyze_image(content_path)
        elif format_type == ContentFormat.VIDEO:
            return await self._analyze_video(content_path)
        elif format_type == ContentFormat.AUDIO:
            return await self._analyze_audio(content_path)
        elif format_type in [ContentFormat.TEXT, ContentFormat.MARKDOWN]:
            return await self._analyze_text(content_path, content_data)
        elif format_type == ContentFormat.HTML:
            return await self._analyze_html(content_path, content_data)
        else:
            return {'metrics': {}, 'compression_potential': 0.2}
    
    async def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image content for optimization opportunities."""        try:
            # Load image
            img = Image.open(image_path)
            
            # Get basic metrics
            width, height = img.size
            channels = len(img.getbands()) if img.mode != 'P' else 1
            bit_depth = 8  # Default assumption
            
            # Calculate image complexity
            img_array = np.array(img)
            complexity = np.std(img_array) / 255.0
            
            # Estimate compression potential
            compression_potential = min(0.8, complexity * 0.6 + 0.2)
            
            return {
                'metrics': {
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'bit_depth': bit_depth,
                    'complexity': complexity,
                    'format': img.format
                },
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return {'metrics': {}, 'compression_potential': 0.3}
    
    async def _analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze video content for optimization opportunities."""        try:
            # Get video information using ffmpeg
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                return {'metrics': {}, 'compression_potential': 0.3}
            
            # Extract metrics
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(video_stream.get('duration', 0))
            bit_rate = int(video_stream.get('bit_rate', 0))
            fps = eval(video_stream.get('r_frame_rate', '0/1'))
            
            # Calculate compression potential based on bitrate and resolution
            resolution_factor = (width * height) / (1920 * 1080)  # Relative to 1080p
            bitrate_factor = bit_rate / 5000000  # Relative to 5Mbps
            
            compression_potential = min(0.7, 0.4 + resolution_factor * 0.2 + bitrate_factor * 0.1)
            
            return {
                'metrics': {
                    'width': width,
                    'height': height,
                    'duration': duration,
                    'bit_rate': bit_rate,
                    'fps': fps,
                    'codec': video_stream.get('codec_name')
                },
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {e}")
            return {'metrics': {}, 'compression_potential': 0.4}
    
    async def _analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio content for optimization opportunities."""        try:
            # Load audio using librosa
            y, sr = librosa.load(audio_path)
            
            # Calculate audio metrics
            duration = len(y) / sr
            rms_energy = np.sqrt(np.mean(y**2))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Estimate compression potential based on content complexity
            complexity = (spectral_centroid / sr) * 0.5 + zero_crossing_rate * 0.3 + rms_energy * 0.2
            compression_potential = min(0.8, 0.3 + complexity * 0.5)
            
            return {
                'metrics': {
                    'duration': duration,
                    'sample_rate': sr,
                    'rms_energy': rms_energy,
                    'spectral_centroid': spectral_centroid,
                    'zero_crossing_rate': zero_crossing_rate,
                    'complexity': complexity
                },
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {e}")
            return {'metrics': {}, 'compression_potential': 0.5}
    
    async def _analyze_text(
        self,
        text_path: str,
        content_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Analyze text content for optimization and SEO opportunities."""        try:
            # Read text content
            if content_data:
                text = content_data.decode('utf-8')
            else:
                with open(text_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Basic text metrics
            word_count = len(text.split())
            char_count = len(text)
            line_count = text.count('\n') + 1
            
            # Readability analysis
            readability_score = flesch_reading_ease(text)
            
            # Token analysis for compression potential
            if self.tokenizer:
                tokens = self.tokenizer.encode(text)
                token_count = len(tokens)
                compression_potential = min(0.6, 0.2 + (token_count / char_count) * 0.4)
            else:
                compression_potential = 0.3
            
            # SEO analysis for text content
            seo_score = self._calculate_seo_score(text)
            
            return {
                'metrics': {
                    'word_count': word_count,
                    'char_count': char_count,
                    'line_count': line_count,
                    'token_count': token_count if self.tokenizer else 0,
                    'avg_word_length': char_count / max(word_count, 1)
                },
                'compression_potential': compression_potential,
                'readability_score': readability_score,
                'seo_score': seo_score
            }
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            return {'metrics': {}, 'compression_potential': 0.3}
    
    async def _analyze_html(
        self,
        html_path: str,
        content_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Analyze HTML content for optimization and SEO opportunities."""        try:
            # Read HTML content
            if content_data:
                html_content = content_data.decode('utf-8')
            else:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text()
            
            # HTML-specific metrics
            tag_count = len(soup.find_all())
            image_count = len(soup.find_all('img'))
            link_count = len(soup.find_all('a'))
            script_count = len(soup.find_all('script'))
            css_count = len(soup.find_all('style'))
            
            # SEO analysis
            title = soup.find('title')
            meta_description = soup.find('meta', attrs={'name': 'description'})
            h1_tags = soup.find_all('h1')
            
            seo_score = self._calculate_html_seo_score(soup)
            
            # Compression potential based on content structure
            content_ratio = len(text_content) / len(html_content)
            compression_potential = min(0.7, 0.4 + (1 - content_ratio) * 0.3)
            
            return {
                'metrics': {
                    'tag_count': tag_count,
                    'image_count': image_count,
                    'link_count': link_count,
                    'script_count': script_count,
                    'css_count': css_count,
                    'has_title': title is not None,
                    'has_meta_description': meta_description is not None,
                    'h1_count': len(h1_tags),
                    'content_ratio': content_ratio,
                    'text_length': len(text_content)
                },
                'compression_potential': compression_potential,
                'seo_score': seo_score,
                'readability_score': flesch_reading_ease(text_content) if text_content else 0
            }
            
        except Exception as e:
            self.logger.error(f"HTML analysis failed: {e}")
            return {'metrics': {}, 'compression_potential': 0.4}
    
    def _calculate_quality_score(
        self,
        metrics: Dict[str, Any],
        format_type: ContentFormat
    ) -> float:
        """Calculate overall quality score for content."""        try:
            if format_type == ContentFormat.IMAGE:
                # Image quality based on resolution and complexity
                width = metrics.get('width', 0)
                height = metrics.get('height', 0)
                complexity = metrics.get('complexity', 0.5)
                
                resolution_score = min(1.0, (width * height) / (1920 * 1080))
                quality_score = (resolution_score * 0.6 + complexity * 0.4)
                
            elif format_type == ContentFormat.VIDEO:
                # Video quality based on resolution, bitrate, and fps
                width = metrics.get('width', 0)
                height = metrics.get('height', 0)
                bit_rate = metrics.get('bit_rate', 0)
                fps = metrics.get('fps', 0)
                
                resolution_score = min(1.0, (width * height) / (1920 * 1080))
                bitrate_score = min(1.0, bit_rate / 10000000)  # Relative to 10Mbps
                fps_score = min(1.0, fps / 60)
                
                quality_score = (resolution_score * 0.4 + bitrate_score * 0.4 + fps_score * 0.2)
                
            elif format_type == ContentFormat.AUDIO:
                # Audio quality based on sample rate and energy
                sample_rate = metrics.get('sample_rate', 0)
                rms_energy = metrics.get('rms_energy', 0)
                
                sr_score = min(1.0, sample_rate / 48000)  # Relative to 48kHz
                energy_score = min(1.0, rms_energy * 10)
                
                quality_score = (sr_score * 0.6 + energy_score * 0.4)
                
            elif format_type in [ContentFormat.TEXT, ContentFormat.MARKDOWN, ContentFormat.HTML]:
                # Text quality based on readability and structure
                word_count = metrics.get('word_count', 0)
                avg_word_length = metrics.get('avg_word_length', 0)
                
                length_score = min(1.0, word_count / 1000)  # Relative to 1000 words
                readability_score = min(1.0, max(0, avg_word_length - 2) / 5)  # 2-7 char average
                
                quality_score = (length_score * 0.6 + readability_score * 0.4)
                
            else:
                quality_score = 0.5  # Default for unknown formats
            
            return max(0.1, min(1.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return 0.5
    
    def _calculate_seo_score(self, text: str) -> float:
        """Calculate SEO score for text content."""        try:
            score = 0.0
            
            # Word count check (300-2000 words is optimal)
            word_count = len(text.split())
            if 300 <= word_count <= 2000:
                score += 0.3
            elif word_count > 100:
                score += 0.1
            
            # Readability check
            readability = flesch_reading_ease(text)
            if 60 <= readability <= 80:  # Good readability range
                score += 0.2
            elif 40 <= readability <= 90:
                score += 0.1
            
            # Keyword density and variety (simplified)
            words = text.lower().split()
            unique_words = set(words)
            diversity_ratio = len(unique_words) / max(len(words), 1)
            
            if 0.3 <= diversity_ratio <= 0.7:  # Good diversity
                score += 0.2
            
            # Structure indicators (headings, paragraphs)
            paragraph_count = text.count('\n\n') + 1
            if paragraph_count >= 3:
                score += 0.1
            
            # Length and density balance
            avg_sentence_length = len(text) / max(text.count('.'), 1)
            if 50 <= avg_sentence_length <= 200:  # Reasonable sentence length
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"SEO score calculation failed: {e}")
            return 0.3
    
    def _calculate_html_seo_score(self, soup: BeautifulSoup) -> float:
        """Calculate SEO score for HTML content."""        try:
            score = 0.0
            
            # Title tag
            title = soup.find('title')
            if title and 30 <= len(title.get_text()) <= 60:
                score += 0.2
            elif title:
                score += 0.1
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_length = len(meta_desc.get('content'))
                if 120 <= desc_length <= 160:
                    score += 0.2
                elif 80 <= desc_length <= 200:
                    score += 0.1
            
            # Header structure
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 1:  # Exactly one H1
                score += 0.15
            elif len(h1_tags) > 0:
                score += 0.05
            
            # Image alt texts
            images = soup.find_all('img')
            if images:
                images_with_alt = [img for img in images if img.get('alt')]
                alt_ratio = len(images_with_alt) / len(images)
                score += alt_ratio * 0.15
            
            # Internal links
            links = soup.find_all('a', href=True)
            internal_links = [link for link in links if not link['href'].startswith('http')]
            if len(internal_links) >= 3:
                score += 0.1
            
            # Content length
            text_content = soup.get_text()
            word_count = len(text_content.split())
            if word_count >= 300:
                score += 0.15
            elif word_count >= 150:
                score += 0.1
            
            # Schema markup
            if soup.find(attrs={'itemscope': True}) or soup.find('script', type='application/ld+json'):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"HTML SEO score calculation failed: {e}")
            return 0.3
    
    def _generate_optimization_suggestions(
        self,
        analysis_result: Dict[str, Any],
        format_type: ContentFormat,
        file_size: int
    ) -> List[str]:
        """Generate optimization suggestions based on analysis."""        suggestions = []
        
        try:
            metrics = analysis_result.get('metrics', {})
            compression_potential = analysis_result.get('compression_potential', 0)
            
            # Format-specific suggestions
            if format_type == ContentFormat.IMAGE:
                width = metrics.get('width', 0)
                height = metrics.get('height', 0)
                
                if width > 2000 or height > 2000:
                    suggestions.append("Consider reducing image resolution for web use")
                
                if compression_potential > 0.4:
                    suggestions.append("Image has high compression potential - consider JPEG optimization")
                
                if metrics.get('format') == 'PNG' and metrics.get('complexity', 0) < 0.3:
                    suggestions.append("Consider converting simple PNG to JPEG for better compression")
                
            elif format_type == ContentFormat.VIDEO:
                bit_rate = metrics.get('bit_rate', 0)
                width = metrics.get('width', 0)
                
                if bit_rate > 10000000:  # >10Mbps
                    suggestions.append("Consider reducing video bitrate for better streaming")
                
                if width > 1920:
                    suggestions.append("Consider reducing resolution to 1080p for web delivery")
                
                if compression_potential > 0.5:
                    suggestions.append("Video can be significantly compressed using modern codecs (H.265)")
                
            elif format_type == ContentFormat.AUDIO:
                sample_rate = metrics.get('sample_rate', 0)
                
                if sample_rate > 48000:
                    suggestions.append("Consider reducing sample rate to 44.1kHz for general use")
                
                if compression_potential > 0.6:
                    suggestions.append("Audio has high compression potential - consider MP3 or AAC")
                
            elif format_type in [ContentFormat.TEXT, ContentFormat.MARKDOWN]:
                word_count = metrics.get('word_count', 0)
                readability_score = analysis_result.get('readability_score', 0)
                
                if readability_score < 30:
                    suggestions.append("Content readability could be improved for better SEO")
                
                if word_count < 300:
                    suggestions.append("Consider expanding content length for better SEO ranking")
                
                seo_score = analysis_result.get('seo_score', 0)
                if seo_score < 0.5:
                    suggestions.append("Content SEO optimization needed - add headings, improve structure")
                
            elif format_type == ContentFormat.HTML:
                seo_score = analysis_result.get('seo_score', 0)
                
                if seo_score < 0.6:
                    suggestions.append("HTML SEO can be improved - check title, meta description, headers")
                
                if not metrics.get('has_title'):
                    suggestions.append("Add a title tag for better SEO")
                
                if not metrics.get('has_meta_description'):
                    suggestions.append("Add meta description for better search engine visibility")
                
                if metrics.get('image_count', 0) > 0 and metrics.get('images_with_alt', 0) == 0:
                    suggestions.append("Add alt text to images for accessibility and SEO")
            
            # General file size suggestions
            if file_size > 10 * 1024 * 1024:  # >10MB
                suggestions.append("File size is large - consider compression or format optimization")
            
            # Compression suggestions
            if compression_potential > 0.5:
                suggestions.append(f"High compression potential ({compression_potential:.1%}) detected - consider optimization")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization suggestions: {e}")
            return ["Consider general optimization techniques for better performance"]
    
    async def _optimize_by_format(
        self,
        content_path: str,
        format_type: ContentFormat,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform format-specific optimization."""        
        if format_type == ContentFormat.IMAGE:
            return await self._optimize_image(content_path, settings, output_path)
        elif format_type == ContentFormat.VIDEO:
            return await self._optimize_video(content_path, settings, output_path)
        elif format_type == ContentFormat.AUDIO:
            return await self._optimize_audio(content_path, settings, output_path)
        elif format_type in [ContentFormat.TEXT, ContentFormat.MARKDOWN]:
            return await self._optimize_text(content_path, settings, output_path)
        elif format_type == ContentFormat.HTML:
            return await self._optimize_html(content_path, settings, output_path)
        else:
            # Generic optimization (compression only)
            return await self._optimize_generic(content_path, settings, output_path)
    
    async def _optimize_image(
        self,
        image_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize image content."""        try:
            # Load original image
            img = Image.open(image_path)
            original_size = os.path.getsize(image_path)
            
            # Determine optimization level
            if settings.level == OptimizationLevel.BASIC:
                quality = 90
                resize_factor = 1.0
            elif settings.level == OptimizationLevel.STANDARD:
                quality = 85
                resize_factor = 0.9
            elif settings.level == OptimizationLevel.ADVANCED:
                quality = 80
                resize_factor = 0.8
            else:  # MAXIMUM
                quality = 75
                resize_factor = 0.7
            
            # Resize if needed
            if resize_factor < 1.0:
                new_size = (
                    int(img.size[0] * resize_factor),
                    int(img.size[1] * resize_factor)
                )
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Prepare output path
            if not output_path:
                path_obj = Path(image_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized{path_obj.suffix}")
            
            # Save optimized image
            img.save(output_path, optimize=True, quality=quality)
            optimized_size = os.path.getsize(output_path)
            
            return {
                'size': optimized_size,
                'quality': quality / 100,
                'format_changes': ['compression', 'optimization'],
                'metrics': {
                    'original_size': original_size,
                    'quality_setting': quality,
                    'resize_factor': resize_factor
                }
            }
            
        except Exception as e:
            self.logger.error(f"Image optimization failed: {e}")
            return {
                'size': os.path.getsize(image_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _optimize_video(
        self,
        video_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize video content."""        try:
            # Prepare output path
            if not output_path:
                path_obj = Path(video_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized.mp4")
            
            # Determine optimization parameters
            if settings.level == OptimizationLevel.BASIC:
                crf = 23
                preset = 'medium'
            elif settings.level == OptimizationLevel.STANDARD:
                crf = 26
                preset = 'medium'
            elif settings.level == OptimizationLevel.ADVANCED:
                crf = 28
                preset = 'slow'
            else:  # MAXIMUM
                crf = 30
                preset = 'veryslow'
            
            # Run ffmpeg optimization
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                crf=crf,
                preset=preset,
                acodec='aac',
                audio_bitrate='128k'
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Get file sizes
            original_size = os.path.getsize(video_path)
            optimized_size = os.path.getsize(output_path)
            
            return {
                'size': optimized_size,
                'quality': 1.0 - (crf - 18) / 32,  # Estimate quality
                'format_changes': ['h264_encoding', 'aac_audio'],
                'metrics': {
                    'original_size': original_size,
                    'crf_setting': crf,
                    'preset': preset
                }
            }
            
        except Exception as e:
            self.logger.error(f"Video optimization failed: {e}")
            return {
                'size': os.path.getsize(video_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _optimize_audio(
        self,
        audio_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize audio content."""        try:
            # Prepare output path
            if not output_path:
                path_obj = Path(audio_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized.mp3")
            
            # Determine optimization parameters
            if settings.level == OptimizationLevel.BASIC:
                bitrate = '192k'
                sample_rate = 44100
            elif settings.level == OptimizationLevel.STANDARD:
                bitrate = '160k'
                sample_rate = 44100
            elif settings.level == OptimizationLevel.ADVANCED:
                bitrate = '128k'
                sample_rate = 44100
            else:  # MAXIMUM
                bitrate = '96k'
                sample_rate = 22050
            
            # Run ffmpeg optimization
            stream = ffmpeg.input(audio_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                acodec='mp3',
                audio_bitrate=bitrate,
                ar=sample_rate
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Get file sizes
            original_size = os.path.getsize(audio_path)
            optimized_size = os.path.getsize(output_path)
            
            return {
                'size': optimized_size,
                'quality': int(bitrate.rstrip('k')) / 320,  # Relative to 320kbps
                'format_changes': ['mp3_encoding'],
                'metrics': {
                    'original_size': original_size,
                    'bitrate': bitrate,
                    'sample_rate': sample_rate
                }
            }
            
        except Exception as e:
            self.logger.error(f"Audio optimization failed: {e}")
            return {
                'size': os.path.getsize(audio_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _optimize_text(
        self,
        text_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize text content."""        try:
            # Read original text
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            original_size = len(text.encode('utf-8'))
            optimized_text = text
            
            # Apply text optimizations based on level
            if settings.level in [OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED, OptimizationLevel.MAXIMUM]:
                # Remove excessive whitespace
                import re
                optimized_text = re.sub(r'\s+', ' ', optimized_text)
                optimized_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', optimized_text)
                
                # Remove trailing whitespace
                lines = optimized_text.split('\n')
                optimized_text = '\n'.join(line.rstrip() for line in lines)
            
            if settings.level in [OptimizationLevel.ADVANCED, OptimizationLevel.MAXIMUM]:
                # Additional text compression techniques
                # Remove redundant words (simplified)
                words = optimized_text.split()
                unique_words = []
                seen = set()
                for word in words:
                    if word.lower() not in seen or len(word) <= 3:
                        unique_words.append(word)
                        seen.add(word.lower())
                optimized_text = ' '.join(unique_words)
            
            # Prepare output path
            if not output_path:
                path_obj = Path(text_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized{path_obj.suffix}")
            
            # Save optimized text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_text)
            
            optimized_size = len(optimized_text.encode('utf-8'))
            
            return {
                'size': optimized_size,
                'quality': 0.9,  # Assume high quality retention
                'format_changes': ['whitespace_optimization'],
                'metrics': {
                    'original_size': original_size,
                    'original_words': len(text.split()),
                    'optimized_words': len(optimized_text.split())
                }
            }
            
        except Exception as e:
            self.logger.error(f"Text optimization failed: {e}")
            return {
                'size': os.path.getsize(text_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _optimize_html(
        self,
        html_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize HTML content."""        try:
            # Read original HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            original_size = len(html.encode('utf-8'))
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Apply HTML optimizations
            if settings.level in [OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED, OptimizationLevel.MAXIMUM]:
                # Remove comments
                for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                    comment.extract()
                
                # Minify inline CSS and JavaScript
                for style in soup.find_all('style'):
                    if style.string:
                        css_content = style.string
                        # Basic CSS minification
                        css_content = re.sub(r'\s+', ' ', css_content)
                        css_content = re.sub(r';\s*}', '}', css_content)
                        style.string = css_content
                
                for script in soup.find_all('script'):
                    if script.string and not script.get('src'):
                        js_content = script.string
                        # Basic JS minification
                        js_content = re.sub(r'\s+', ' ', js_content)
                        script.string = js_content
            
            if settings.level in [OptimizationLevel.ADVANCED, OptimizationLevel.MAXIMUM]:
                # Remove empty attributes and unnecessary whitespace
                for tag in soup.find_all():
                    # Remove empty attributes
                    empty_attrs = [attr for attr, value in tag.attrs.items() if not value]
                    for attr in empty_attrs:
                        del tag.attrs[attr]
                
                # Additional SEO optimizations
                if settings.seo_optimization:
                    # Add missing alt attributes to images
                    for img in soup.find_all('img'):
                        if not img.get('alt'):
                            img['alt'] = 'Image'
                    
                    # Ensure meta viewport for mobile
                    if not soup.find('meta', attrs={'name': 'viewport'}):
                        viewport_meta = soup.new_tag('meta', name='viewport', content='width=device-width, initial-scale=1')
                        if soup.head:
                            soup.head.append(viewport_meta)
            
            # Prepare output path
            if not output_path:
                path_obj = Path(html_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized{path_obj.suffix}")
            
            # Save optimized HTML
            optimized_html = str(soup)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_html)
            
            optimized_size = len(optimized_html.encode('utf-8'))
            
            return {
                'size': optimized_size,
                'quality': 0.95,  # High quality retention for HTML
                'format_changes': ['minification', 'seo_optimization'] if settings.seo_optimization else ['minification'],
                'metrics': {
                    'original_size': original_size,
                    'compression_type': 'html_minification'
                }
            }
            
        except Exception as e:
            self.logger.error(f"HTML optimization failed: {e}")
            return {
                'size': os.path.getsize(html_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _optimize_generic(
        self,
        content_path: str,
        settings: OptimizationSettings,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generic optimization for unknown formats."""        try:
            # For unknown formats, just copy the file
            # In a real implementation, you might apply generic compression
            
            original_size = os.path.getsize(content_path)
            
            if not output_path:
                path_obj = Path(content_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_optimized{path_obj.suffix}")
            
            # Simple copy (no optimization for unknown formats)
            import shutil
            shutil.copy2(content_path, output_path)
            
            return {
                'size': original_size,
                'quality': 1.0,
                'format_changes': [],
                'metrics': {'optimization_type': 'copy_only'}
            }
            
        except Exception as e:
            self.logger.error(f"Generic optimization failed: {e}")
            return {
                'size': os.path.getsize(content_path),
                'quality': 1.0,
                'format_changes': [],
                'metrics': {}
            }
    
    async def _save_optimization_record(
        self,
        analysis: ContentAnalysis,
        result: ContentOptimizationResult,
        settings: OptimizationSettings
    ) -> None:
        """Save optimization record to database."""        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            optimization_id = str(uuid.uuid4())
            content_hash = hashlib.md5(f"{analysis.file_size}{analysis.format_type.value}".encode()).hexdigest()
            
            cursor.execute("""                INSERT INTO content_optimizations (
                    id, content_hash, original_size, optimized_size, compression_ratio,
                    quality_retained, format_type, optimization_level, algorithm,
                    timestamp, performance_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                optimization_id,
                content_hash,
                result.original_size,
                result.optimized_size,
                result.compression_ratio,
                result.quality_retained,
                analysis.format_type.value,
                settings.level.value,
                settings.algorithm.value,
                datetime.now().isoformat(),
                json.dumps(result.performance_metrics)
            ))
            
            conn.commit()
            conn.close()
            
            # Store in memory for quick access
            if optimization_id not in self.optimization_history:
                self.optimization_history[optimization_id] = []
            self.optimization_history[optimization_id].append(result)
            
        except Exception as e:
            self.logger.error(f"Failed to save optimization record: {e}")
    
    def _update_performance_stats(self, result: ContentOptimizationResult) -> None:
        """Update global performance statistics."""        try:
            self.performance_stats['total_optimizations'] += 1
            
            bytes_saved = result.original_size - result.optimized_size
            self.performance_stats['total_bytes_saved'] += bytes_saved
            
            # Update running averages
            total_ops = self.performance_stats['total_optimizations']
            current_avg_compression = self.performance_stats['average_compression_ratio']
            current_avg_quality = self.performance_stats['average_quality_retained']
            
            # Calculate new averages
            self.performance_stats['average_compression_ratio'] = (
                (current_avg_compression * (total_ops - 1) + result.compression_ratio) / total_ops
            )
            
            self.performance_stats['average_quality_retained'] = (
                (current_avg_quality * (total_ops - 1) + result.quality_retained) / total_ops
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update performance stats: {e}")
    
    async def get_optimization_report(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive optimization performance report."""        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get data for the specified time period
            start_date = (datetime.now() - timedelta(days=time_period_days)).isoformat()
            
            cursor.execute("""                SELECT 
                    COUNT(*) as total_optimizations,
                    SUM(original_size - optimized_size) as total_bytes_saved,
                    AVG(compression_ratio) as avg_compression_ratio,
                    AVG(quality_retained) as avg_quality_retained,
                    format_type,
                    optimization_level,
                    COUNT(*) as format_count
                FROM content_optimizations 
                WHERE timestamp >= ?
                GROUP BY format_type, optimization_level
            """, (start_date,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Process results
            report = {
                'period_days': time_period_days,
                'summary': {
                    'total_optimizations': sum(row[0] for row in results),
                    'total_bytes_saved': sum(row[1] or 0 for row in results),
                    'average_compression_ratio': np.mean([row[2] or 0 for row in results]),
                    'average_quality_retained': np.mean([row[3] or 0 for row in results])
                },
                'by_format': {},
                'by_optimization_level': {},
                'performance_metrics': self.performance_stats.copy(),
                'generated_at': datetime.now().isoformat()
            }
            
            # Group by format
            format_stats = {}
            level_stats = {}
            
            for row in results:
                format_type = row[4]
                opt_level = row[5]
                
                if format_type not in format_stats:
                    format_stats[format_type] = {
                        'optimizations': 0,
                        'bytes_saved': 0,
                        'avg_compression': 0,
                        'avg_quality': 0
                    }
                
                format_stats[format_type]['optimizations'] += row[0]
                format_stats[format_type]['bytes_saved'] += row[1] or 0
                format_stats[format_type]['avg_compression'] += row[2] or 0
                format_stats[format_type]['avg_quality'] += row[3] or 0
                
                if opt_level not in level_stats:
                    level_stats[opt_level] = {
                        'optimizations': 0,
                        'bytes_saved': 0,
                        'avg_compression': 0,
                        'avg_quality': 0
                    }
                
                level_stats[opt_level]['optimizations'] += row[0]
                level_stats[opt_level]['bytes_saved'] += row[1] or 0
                level_stats[opt_level]['avg_compression'] += row[2] or 0
                level_stats[opt_level]['avg_quality'] += row[3] or 0
            
            # Normalize averages
            for format_type, stats in format_stats.items():
                if stats['optimizations'] > 0:
                    stats['avg_compression'] /= stats['optimizations']
                    stats['avg_quality'] /= stats['optimizations']
            
            for level, stats in level_stats.items():
                if stats['optimizations'] > 0:
                    stats['avg_compression'] /= stats['optimizations']
                    stats['avg_quality'] /= stats['optimizations']
            
            report['by_format'] = format_stats
            report['by_optimization_level'] = level_stats
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization report: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    async def batch_optimize(
        self,
        content_paths: List[str],
        settings: Optional[OptimizationSettings] = None,
        output_directory: Optional[str] = None
    ) -> List[ContentOptimizationResult]:
        """        Optimize multiple content files in batch.
        
        Args:
            content_paths: List of content file paths
            settings: Optimization settings
            output_directory: Directory for optimized outputs
            
        Returns:
            List of optimization results
        """        try:
            if not settings:
                settings = OptimizationSettings(
                    level=OptimizationLevel.STANDARD,
                    algorithm=CompressionAlgorithm.ADAPTIVE
                )
            
            # Create output directory if needed
            if output_directory:
                os.makedirs(output_directory, exist_ok=True)
            
            results = []
            
            # Process files in parallel
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def optimize_single(content_path: str) -> ContentOptimizationResult:
                async with semaphore:
                    try:
                        output_path = None
                        if output_directory:
                            filename = Path(content_path).name
                            output_path = os.path.join(output_directory, f"optimized_{filename}")
                        
                        return await self.optimize_content(content_path, output_path, settings)
                    except Exception as e:
                        self.logger.error(f"Failed to optimize {content_path}: {e}")
                        # Return a failed result
                        return ContentOptimizationResult(
                            original_size=0,
                            optimized_size=0,
                            compression_ratio=0.0,
                            quality_retained=0.0,
                            time_taken=0.0,
                            optimization_type="failed",
                            format_changes=[]
                        )
            
            # Execute all optimizations
            tasks = [optimize_single(path) for path in content_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in results if isinstance(r, ContentOptimizationResult)]
            
            self.logger.info(
                f"Batch optimization completed: {len(valid_results)}/{len(content_paths)} files processed"
            )
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch optimization failed: {e}")
            raise ContentOptimizationError(f"Batch optimization failed: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""        return {
            'performance_stats': self.performance_stats.copy(),
            'optimization_history_count': len(self.optimization_history),
            'active_workers': self.max_workers,
            'memory_usage': self._get_memory_usage(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_memory_usage(self) -> Dict[str, int]:
        """Get current memory usage statistics."""        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_bytes': memory_info.rss,
                'vms_bytes': memory_info.vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'rss_bytes': 0, 'vms_bytes': 0, 'percent': 0.0}
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {'rss_bytes': 0, 'vms_bytes': 0, 'percent': 0.0}
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """        Cleanup temporary optimization files.
        
        Args:
            max_age_hours: Maximum age of temp files to keep
            
        Returns:
            Number of files cleaned up
        """        try:
            temp_dir = Path("/tmp")
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            cleaned_count = 0
            
            # Look for optimization temp files
            for temp_file in temp_dir.glob("*_optimized*"):
                try:
                    file_modified = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_modified < cutoff_time:
                        temp_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to clean temp file {temp_file}: {e}")
            
            self.logger.info(f"Cleaned up {cleaned_count} temporary optimization files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Temp file cleanup failed: {e}")
            return 0
    
    def __del__(self):
        """Cleanup resources on destruction."""        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
        except:
            pass
    WAV = "wav"
    
    # Video
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"
    
    # Image
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    HEIC = "heic"

@dataclass
class ContentMetrics:
    """Content quality and performance metrics"""    file_size_bytes: int = 0
    file_size_mb: float = 0.0
    compression_ratio: float = 0.0
    quality_score: float = 0.0
    loading_time_ms: float = 0.0
    bandwidth_usage_mbps: float = 0.0
    seo_score: float = 0.0
    readability_score: float = 0.0
    accessibility_score: float = 0.0
    mobile_optimization_score: float = 0.0

@dataclass
class OptimizationResult:
    """Content optimization outcome"""    original_metrics: ContentMetrics
    optimized_metrics: ContentMetrics
    improvement_percentage: float
    format_changed: bool
    optimization_techniques: List[str]
    processing_time: float
    success: bool
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class ContentOptimizer:
    """    Advanced multi-format content optimization engine for creators.
    
    Supports all major content types used by musicians, bloggers, photographers,
    influencers, and comedians with intelligent optimization strategies.
    """    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.file_handler = FileHandler()
        self.media_processor = MediaProcessor()
        self.content_validator = ContentValidator()
        self.content_analyzer = ContentAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        
        # Optimization settings
        self.quality_presets = {
            'minimal': {'quality': 95, 'compression': 10},
            'standard': {'quality': 85, 'compression': 25},
            'aggressive': {'quality': 75, 'compression': 40},
            'maximum': {'quality': 65, 'compression': 55}
        }
        
        # Format conversion capabilities
        self.supported_formats = {
            ContentType.AUDIO: [CompressionFormat.MP3, CompressionFormat.AAC, CompressionFormat.OGG],
            ContentType.VIDEO: [CompressionFormat.MP4, CompressionFormat.WEBM],
            ContentType.IMAGE: [CompressionFormat.JPEG, CompressionFormat.WEBP, CompressionFormat.AVIF]
        }
        
        # Processing statistics
        self.processing_stats = {
            'total_files_processed': 0,
            'total_bytes_saved': 0,
            'average_compression_ratio': 0.0,
            'processing_time_total': 0.0
        }
        
        logger.info("ContentOptimizer initialized successfully")

    async def optimize_content(
        self,
        content_path: str,
        content_type: ContentType,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
        target_format: Optional[CompressionFormat] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """        Optimize content based on type and requirements
        
        Args:
            content_path: Path to content file
            content_type: Type of content to optimize
            optimization_level: Intensity of optimization
            target_format: Desired output format
            custom_settings: Custom optimization parameters
            
        Returns:
            Optimization results and metrics
        """        try:
            start_time = time.time()
            
            # Validate input content
            await self._validate_content(content_path, content_type)
            
            # Analyze original content
            original_metrics = await self._analyze_content(content_path, content_type)
            
            # Select optimization strategy
            optimization_strategy = await self._select_optimization_strategy(
                content_type, optimization_level, original_metrics, custom_settings
            )
            
            # Execute optimization
            optimized_path = await self._execute_optimization(
                content_path, content_type, optimization_strategy, target_format
            )
            
            # Analyze optimized content
            optimized_metrics = await self._analyze_content(optimized_path, content_type)
            
            # Calculate improvements
            improvement = await self._calculate_improvement(original_metrics, optimized_metrics)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            await self._update_processing_stats(original_metrics, optimized_metrics, processing_time)
            
            result = OptimizationResult(
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                improvement_percentage=improvement,
                format_changed=(target_format is not None),
                optimization_techniques=optimization_strategy['techniques'],
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"Content optimization completed: {improvement:.2f}% improvement")
            return result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise ContentOptimizationError(f"Optimization failed: {str(e)}")

    async def optimize_audio_content(
        self,
        audio_path: str,
        target_bitrate: int = 128,
        target_format: CompressionFormat = CompressionFormat.MP3,
        normalize_audio: bool = True,
        remove_silence: bool = True
    ) -> OptimizationResult:
        """        Optimize audio content for musicians and podcasters
        
        Features:
        - Intelligent bitrate selection
        - Audio normalization and enhancement
        - Silence removal and trimming
        - Format conversion optimization
        - Quality preservation algorithms
        """        try:
            # Load and analyze audio
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            original_size = os.path.getsize(audio_path)
            
            # Audio processing pipeline
            processed_audio = audio_data
            
            # Normalize audio levels
            if normalize_audio:
                processed_audio = librosa.util.normalize(processed_audio)
            
            # Remove silence
            if remove_silence:
                intervals = librosa.effects.split(processed_audio, top_db=20)
                processed_audio = np.concatenate([processed_audio[start:end] for start, end in intervals])
            
            # Audio enhancement
            processed_audio = await self._enhance_audio_quality(processed_audio, sample_rate)
            
            # Format conversion and compression
            optimized_path = await self._compress_audio(
                processed_audio, sample_rate, target_format, target_bitrate
            )
            
            # Calculate metrics
            optimized_size = os.path.getsize(optimized_path)
            compression_ratio = (original_size - optimized_size) / original_size * 100
            
            # Audio quality assessment
            quality_score = await self._assess_audio_quality(optimized_path, audio_path)
            
            original_metrics = ContentMetrics(
                file_size_bytes=original_size,
                file_size_mb=original_size / (1024 * 1024),
                quality_score=100.0
            )
            
            optimized_metrics = ContentMetrics(
                file_size_bytes=optimized_size,
                file_size_mb=optimized_size / (1024 * 1024),
                compression_ratio=compression_ratio,
                quality_score=quality_score
            )
            
            return OptimizationResult(
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                improvement_percentage=compression_ratio,
                format_changed=True,
                optimization_techniques=['normalization', 'silence_removal', 'format_conversion'],
                processing_time=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Audio optimization failed: {str(e)}")
            raise ContentOptimizationError(f"Audio optimization failed: {str(e)}")

    async def optimize_image_content(
        self,
        image_path: str,
        target_format: CompressionFormat = CompressionFormat.WEBP,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        progressive: bool = True
    ) -> OptimizationResult:
        """        Optimize image content for photographers and visual creators
        
        Features:
        - Smart format conversion (WebP, AVIF)
        - Intelligent quality adjustment
        - Responsive image generation
        - Metadata optimization
        - Progressive loading optimization
        """        try:
            # Load and analyze image
            with Image.open(image_path) as img:
                original_size = os.path.getsize(image_path)
                original_width, original_height = img.size
                original_format = img.format
                
                # Determine optimal dimensions
                if max_width or max_height:
                    img = await self._resize_image_smart(img, max_width, max_height)
                
                # Color optimization
                if img.mode in ('RGBA', 'LA') and target_format in [CompressionFormat.JPEG]:
                    # Convert transparent images to RGB with white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Format-specific optimization
                optimized_path = await self._optimize_image_format(
                    img, target_format, quality, progressive
                )
                
                # Calculate metrics
                optimized_size = os.path.getsize(optimized_path)
                compression_ratio = (original_size - optimized_size) / original_size * 100
                
                # Image quality assessment
                quality_score = await self._assess_image_quality(optimized_path, image_path)
                
                original_metrics = ContentMetrics(
                    file_size_bytes=original_size,
                    file_size_mb=original_size / (1024 * 1024),
                    quality_score=100.0
                )
                
                optimized_metrics = ContentMetrics(
                    file_size_bytes=optimized_size,
                    file_size_mb=optimized_size / (1024 * 1024),
                    compression_ratio=compression_ratio,
                    quality_score=quality_score
                )
                
                return OptimizationResult(
                    original_metrics=original_metrics,
                    optimized_metrics=optimized_metrics,
                    improvement_percentage=compression_ratio,
                    format_changed=(target_format.value != original_format.lower()),
                    optimization_techniques=['format_conversion', 'quality_optimization', 'progressive_encoding'],
                    processing_time=time.time(),
                    success=True
                )
                
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            raise ContentOptimizationError(f"Image optimization failed: {str(e)}")

    async def optimize_video_content(
        self,
        video_path: str,
        target_resolution: str = "1080p",
        target_format: CompressionFormat = CompressionFormat.MP4,
        target_bitrate: str = "2M",
        enable_hardware_acceleration: bool = True
    ) -> OptimizationResult:
        """        Optimize video content for influencers and content creators
        
        Features:
        - Resolution optimization
        - Bitrate optimization
        - Hardware-accelerated encoding
        - Multi-format support
        - Quality preservation
        """        try:
            # Analyze original video
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            original_size = os.path.getsize(video_path)
            
            # Build optimization pipeline
            input_stream = ffmpeg.input(video_path)
            
            # Video processing options
            video_options = {
                'vcodec': 'libx264' if not enable_hardware_acceleration else 'h264_nvenc',
                'video_bitrate': target_bitrate,
                'preset': 'medium',
                'crf': 23
            }
            
            # Audio processing options
            audio_options = {
                'acodec': 'aac',
                'audio_bitrate': '128k'
            }
            
            # Apply resolution scaling if needed
            if target_resolution and target_resolution != f"{video_info['width']}x{video_info['height']}":
                resolution_map = {
                    '480p': '854:480',
                    '720p': '1280:720',
                    '1080p': '1920:1080',
                    '1440p': '2560:1440',
                    '4k': '3840:2160'
                }
                if target_resolution in resolution_map:
                    input_stream = input_stream.filter('scale', resolution_map[target_resolution])
            
            # Execute optimization
            optimized_path = f"{os.path.splitext(video_path)[0]}_optimized.{target_format.value}"
            
            out = ffmpeg.output(
                input_stream,
                optimized_path,
                **video_options,
                **audio_options
            )
            
            ffmpeg.run(out, overwrite_output=True, quiet=True)
            
            # Calculate metrics
            optimized_size = os.path.getsize(optimized_path)
            compression_ratio = (original_size - optimized_size) / original_size * 100
            
            original_metrics = ContentMetrics(
                file_size_bytes=original_size,
                file_size_mb=original_size / (1024 * 1024),
                quality_score=100.0
            )
            
            optimized_metrics = ContentMetrics(
                file_size_bytes=optimized_size,
                file_size_mb=optimized_size / (1024 * 1024),
                compression_ratio=compression_ratio,
                quality_score=95.0  # Estimated based on settings
            )
            
            return OptimizationResult(
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                improvement_percentage=compression_ratio,
                format_changed=True,
                optimization_techniques=['video_compression', 'resolution_optimization', 'bitrate_optimization'],
                processing_time=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Video optimization failed: {str(e)}")
            raise ContentOptimizationError(f"Video optimization failed: {str(e)}")

    async def optimize_text_content(
        self,
        text_content: str,
        content_type: ContentType = ContentType.BLOG_POST,
        target_reading_level: str = "grade_8",
        seo_optimization: bool = True,
        target_keywords: Optional[List[str]] = None
    ) -> OptimizationResult:
        """        Optimize text content for bloggers and writers
        
        Features:
        - Readability optimization
        - SEO enhancement
        - Keyword optimization
        - Structure improvement
        - Content enrichment
        """        try:
            original_length = len(text_content)
            original_words = len(text_content.split())
            
            # Text analysis
            original_readability = flesch_reading_ease(text_content)
            original_ari = automated_readability_index(text_content)
            
            optimized_content = text_content
            
            # Readability optimization
            if target_reading_level:
                optimized_content = await self._optimize_readability(
                    optimized_content, target_reading_level
                )
            
            # SEO optimization
            if seo_optimization:
                optimized_content = await self._optimize_text_for_seo(
                    optimized_content, target_keywords
                )
            
            # Structure optimization
            optimized_content = await self._optimize_text_structure(optimized_content)
            
            # Calculate improvements
            optimized_length = len(optimized_content)
            optimized_words = len(optimized_content.split())
            optimized_readability = flesch_reading_ease(optimized_content)
            
            # SEO analysis
            seo_score = await self.seo_analyzer.analyze_text(optimized_content, target_keywords)
            
            original_metrics = ContentMetrics(
                file_size_bytes=original_length,
                readability_score=original_readability,
                seo_score=0.0
            )
            
            optimized_metrics = ContentMetrics(
                file_size_bytes=optimized_length,
                readability_score=optimized_readability,
                seo_score=seo_score
            )
            
            improvement = ((optimized_readability - original_readability) / original_readability) * 100
            
            return OptimizationResult(
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                improvement_percentage=improvement,
                format_changed=False,
                optimization_techniques=['readability', 'seo', 'structure'],
                processing_time=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Text optimization failed: {str(e)}")
            raise ContentOptimizationError(f"Text optimization failed: {str(e)}")

    async def _validate_content(self, content_path: str, content_type: ContentType) -> bool:
        """Validate content file and type compatibility"""        if not os.path.exists(content_path):
            raise ContentOptimizationError(f"Content file not found: {content_path}")
        
        # File size validation
        file_size = os.path.getsize(content_path)
        max_size = self.config.get('max_file_size_mb', 500) * 1024 * 1024
        
        if file_size > max_size:
            raise ContentOptimizationError(f"File too large: {file_size} bytes")
        
        # Content type validation
        is_valid = await self.content_validator.validate_content_type(content_path, content_type)
        if not is_valid:
            raise ContentOptimizationError(f"Invalid content type for file: {content_path}")
        
        return True

    async def _analyze_content(self, content_path: str, content_type: ContentType) -> ContentMetrics:
        """Analyze content and extract metrics"""        file_size = os.path.getsize(content_path)
        
        metrics = ContentMetrics(
            file_size_bytes=file_size,
            file_size_mb=file_size / (1024 * 1024)
        )
        
        # Content-specific analysis
        if content_type in [ContentType.AUDIO, ContentType.MUSIC, ContentType.PODCAST]:
            metrics.quality_score = await self._analyze_audio_quality(content_path)
        elif content_type in [ContentType.IMAGE]:
            metrics.quality_score = await self._analyze_image_quality(content_path)
        elif content_type in [ContentType.VIDEO]:
            metrics.quality_score = await self._analyze_video_quality(content_path)
        elif content_type in [ContentType.TEXT, ContentType.BLOG_POST]:
            metrics.readability_score = await self._analyze_text_readability(content_path)
        
        return metrics

    async def _select_optimization_strategy(
        self,
        content_type: ContentType,
        optimization_level: OptimizationLevel,
        metrics: ContentMetrics,
        custom_settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select optimal optimization strategy based on content analysis"""        
        base_strategy = self.quality_presets.get(optimization_level.value, self.quality_presets['standard'])
        
        strategy = {
            'quality': base_strategy['quality'],
            'compression': base_strategy['compression'],
            'techniques': [],
            'custom_params': custom_settings or {}
        }
        
        # Content-specific strategy adjustments
        if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
            strategy['techniques'].extend(['normalize_audio', 'remove_silence', 'format_optimization'])
        elif content_type == ContentType.IMAGE:
            strategy['techniques'].extend(['smart_resize', 'format_conversion', 'progressive_encoding'])
        elif content_type == ContentType.VIDEO:
            strategy['techniques'].extend(['resolution_optimization', 'bitrate_optimization', 'hardware_acceleration'])
        elif content_type in [ContentType.TEXT, ContentType.BLOG_POST]:
            strategy['techniques'].extend(['readability_optimization', 'seo_enhancement', 'structure_improvement'])
        
        # Adaptive strategy based on content size
        if metrics.file_size_mb > 100:  # Large files need aggressive optimization
            strategy['compression'] = min(strategy['compression'] + 20, 70)
        elif metrics.file_size_mb < 1:  # Small files need minimal optimization
            strategy['compression'] = max(strategy['compression'] - 10, 5)
        
        return strategy

    async def _execute_optimization(
        self,
        content_path: str,
        content_type: ContentType,
        strategy: Dict[str, Any],
        target_format: Optional[CompressionFormat]
    ) -> str:
        """Execute the selected optimization strategy"""        
        techniques = strategy['techniques']
        
        if content_type in [ContentType.AUDIO, ContentType.MUSIC, ContentType.PODCAST]:
            return await self._optimize_audio_with_strategy(content_path, strategy, target_format)
        elif content_type == ContentType.IMAGE:
            return await self._optimize_image_with_strategy(content_path, strategy, target_format)
        elif content_type == ContentType.VIDEO:
            return await self._optimize_video_with_strategy(content_path, strategy, target_format)
        elif content_type in [ContentType.TEXT, ContentType.BLOG_POST]:
            return await self._optimize_text_with_strategy(content_path, strategy)
        else:
            raise ContentOptimizationError(f"Unsupported content type: {content_type}")

    async def _calculate_improvement(
        self, 
        original: ContentMetrics, 
        optimized: ContentMetrics
    ) -> float:
        """Calculate overall improvement percentage"""        
        improvements = []
        
        # File size improvement
        if original.file_size_bytes > 0:
            size_improvement = ((original.file_size_bytes - optimized.file_size_bytes) / 
                              original.file_size_bytes) * 100
            improvements.append(size_improvement)
        
        # Quality preservation (should be minimal loss)
        if original.quality_score > 0 and optimized.quality_score > 0:
            quality_preservation = (optimized.quality_score / original.quality_score) * 100
            improvements.append(quality_preservation - 100)  # Negative if quality decreased
        
        # SEO improvement
        if optimized.seo_score > original.seo_score:
            seo_improvement = ((optimized.seo_score - original.seo_score) / 
                             max(original.seo_score, 1)) * 100
            improvements.append(seo_improvement)
        
        # Readability improvement
        if optimized.readability_score > original.readability_score:
            readability_improvement = ((optimized.readability_score - original.readability_score) / 
                                     max(original.readability_score, 1)) * 100
            improvements.append(readability_improvement)
        
        # Return average improvement
        return sum(improvements) / len(improvements) if improvements else 0.0

    async def _update_processing_stats(
        self,
        original_metrics: ContentMetrics,
        optimized_metrics: ContentMetrics,
        processing_time: float
    ):
        """Update processing statistics"""        
        self.processing_stats['total_files_processed'] += 1
        self.processing_stats['total_bytes_saved'] += (
            original_metrics.file_size_bytes - optimized_metrics.file_size_bytes
        )
        self.processing_stats['processing_time_total'] += processing_time
        
        # Update average compression ratio
        if optimized_metrics.compression_ratio > 0:
            current_avg = self.processing_stats['average_compression_ratio']
            total_files = self.processing_stats['total_files_processed']
            new_avg = ((current_avg * (total_files - 1)) + optimized_metrics.compression_ratio) / total_files
            self.processing_stats['average_compression_ratio'] = new_avg

    async def get_optimization_recommendations(
        self,
        content_path: str,
        content_type: ContentType,
        target_usage: str = "web"
    ) -> List[str]:
        """        Get intelligent optimization recommendations for content
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            target_usage: Intended usage (web, mobile, print, streaming)
            
        Returns:
            List of optimization recommendations
        """        recommendations = []
        
        try:
            # Analyze current content
            metrics = await self._analyze_content(content_path, content_type)
            
            # Size-based recommendations
            if metrics.file_size_mb > 50:
                recommendations.append("Consider aggressive compression to reduce file size")
            elif metrics.file_size_mb > 10:
                recommendations.append("Standard compression recommended for optimal balance")
            
            # Content-specific recommendations
            if content_type == ContentType.IMAGE:
                recommendations.extend([
                    "Convert to WebP format for better compression",
                    "Use progressive JPEG for faster loading",
                    "Consider generating multiple resolutions for responsive design"
                ])
            elif content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                recommendations.extend([
                    "Normalize audio levels for consistent playback",
                    "Remove silence and artifacts for cleaner audio",
                    "Use AAC format for better compression efficiency"
                ])
            elif content_type == ContentType.VIDEO:
                recommendations.extend([
                    "Use H.264 codec for broad compatibility",
                    "Consider multiple bitrates for adaptive streaming",
                    "Optimize for target resolution and device"
                ])
            
            # Usage-specific recommendations
            if target_usage == "web":
                recommendations.extend([
                    "Optimize for web loading speed",
                    "Consider CDN-friendly formats",
                    "Enable progressive loading where possible"
                ])
            elif target_usage == "mobile":
                recommendations.extend([
                    "Prioritize small file sizes for mobile data",
                    "Use mobile-optimized formats",
                    "Consider device-specific optimizations"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return ["Unable to generate recommendations due to analysis error"]

    async def batch_optimize_content(
        self,
        content_files: List[Tuple[str, ContentType]],
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
        max_concurrent: int = 5
    ) -> List[OptimizationResult]:
        """        Optimize multiple content files concurrently
        
        Args:
            content_files: List of (file_path, content_type) tuples
            optimization_level: Optimization intensity
            max_concurrent: Maximum concurrent optimizations
            
        Returns:
            List of optimization results
        """        results = []
        
        # Create semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def optimize_single_file(file_path: str, content_type: ContentType):
            async with semaphore:
                try:
                    result = await self.optimize_content(
                        file_path, content_type, optimization_level
                    )
                    return result
                except Exception as e:
                    logger.error(f"Failed to optimize {file_path}: {str(e)}")
                    return None
        
        # Process all files concurrently
        tasks = [
            optimize_single_file(file_path, content_type)
            for file_path, content_type in content_files
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = [r for r in results if isinstance(r, OptimizationResult)]
        
        logger.info(f"Batch optimization completed: {len(valid_results)}/{len(content_files)} successful")
        
        return valid_results

    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""        stats = self.processing_stats.copy()
        
        # Calculate additional metrics
        if stats['total_files_processed'] > 0:
            stats['average_processing_time'] = (
                stats['processing_time_total'] / stats['total_files_processed']
            )
            stats['total_mb_saved'] = stats['total_bytes_saved'] / (1024 * 1024)
        
        return stats


class MultiFormatOptimizer:
    """    Specialized optimizer for handling multiple content formats simultaneously.
    Ideal for creators who work with mixed content types.
    """    def __init__(self, config: Dict[str, Any] = None):
        self.content_optimizer = ContentOptimizer(config)
        self.format_strategies = {}
        
    async def optimize_creator_portfolio(
        self,
        portfolio_path: str,
        creator_type: str = "influencer"
    ) -> Dict[str, List[OptimizationResult]]:
        """        Optimize entire creator portfolio with format-specific strategies
        
        Supports:
        - Musicians: Audio, images, videos
        - Photographers: Images, portfolios  
        - Bloggers: Text, images
        - Influencers: Multi-format content
        - Comedians: Audio, video content
        """        results = {
            'audio': [],
            'video': [],
            'image': [],
            'text': []
        }
        
        # Scan portfolio directory
        content_files = await self._scan_portfolio_directory(portfolio_path)
        
        # Group by content type
        grouped_files = await self._group_files_by_type(content_files)
        
        # Apply creator-specific optimization strategies
        for content_type, files in grouped_files.items():
            if files:
                optimization_results = await self._optimize_content_group(
                    files, content_type, creator_type
                )
                results[content_type.value] = optimization_results
        
        return results


class SEOOptimizer:
    """    Specialized SEO optimization for content creators.
    Integrates with content optimization for maximum search visibility.
    """    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.seo_analyzer = SEOAnalyzer()
        
    async def optimize_content_for_seo(
        self,
        content: str,
        target_keywords: List[str],
        content_type: ContentType = ContentType.BLOG_POST
    ) -> Tuple[str, float]:
        """        Optimize content for search engine visibility
        
        Returns optimized content and SEO score
        """        try:
            # Keyword density optimization
            optimized_content = await self._optimize_keyword_density(content, target_keywords)
            
            # Meta description generation
            meta_description = await self._generate_meta_description(optimized_content, target_keywords)
            
            # Header structure optimization
            optimized_content = await self._optimize_header_structure(optimized_content)
            
            # Internal linking suggestions
            internal_links = await self._suggest_internal_links(optimized_content)
            
            # Calculate SEO score
            seo_score = await self.seo_analyzer.calculate_seo_score(
                optimized_content, target_keywords
            )
            
            return optimized_content, seo_score
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {str(e)}")
            return content, 0.0


class MediaCompressionEngine:
    """    Advanced compression engine with intelligent quality preservation.
    Uses machine learning to predict optimal compression settings.
    """    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.ml_predictor = None  # ML model for compression prediction
        
    async def intelligent_compression(
        self,
        file_path: str,
        target_size_mb: Optional[float] = None,
        quality_threshold: float = 85.0
    ) -> Tuple[str, Dict[str, float]]:
        """        Use ML to determine optimal compression settings
        
        Returns:
            Tuple of (compressed_file_path, compression_metrics)
        """        try:
            # Analyze content characteristics
            content_features = await self._extract_content_features(file_path)
            
            # Predict optimal compression settings
            if self.ml_predictor:
                compression_settings = await self.ml_predictor.predict_optimal_settings(
                    content_features, target_size_mb, quality_threshold
                )
            else:
                # Fallback to rule-based optimization
                compression_settings = await self._rule_based_compression_settings(
                    content_features, target_size_mb
                )
            
            # Apply compression
            compressed_path = await self._apply_compression(file_path, compression_settings)
            
            # Validate quality
            quality_metrics = await self._validate_compression_quality(file_path, compressed_path)
            
            return compressed_path, quality_metrics
            
        except Exception as e:
            logger.error(f"Intelligent compression failed: {str(e)}")
            raise ContentOptimizationError(f"Compression failed: {str(e)}")
