"""Enterprise Classifier Factory

Advanced factory pattern implementation for creating appropriate content classifiers
based on content type, format, and analysis requirements. Provides intelligent
classifier selection, caching, and orchestration for multi-modal content analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

⚠️ STRONG WARNING: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted
to the full extent of German and international copyright law.
"""import mimetypes
from typing import Dict, List, Optional, Union, Any, Type
import logging
from pathlib import Path
from enum import Enum
import threading
from datetime import datetime, timedelta
import hashlib

from .audio_classifier import AudioContentClassifier
from .video_classifier import VideoContentClassifier
from .image_classifier import ImageContentClassifier
from .text_classifier import TextContentClassifier
from .multimodal_classifier import MultimodalContentClassifier
from .genre_detector import GenreDetector
from .mood_analyzer import MoodAnalyzer
from .quality_assessor import QualityAssessor
from .similarity_matcher import SimilarityMatcher
from .violation_detector import ViolationDetector
from ...utils.exceptions import UnsupportedFormatError, ClassificationError
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Enumeration of supported content types."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"


class ClassifierFactory:
    """    Factory for creating and managing content classifiers.
    
    Features:
    - Automatic classifier selection based on content type
    - Support for single and multimodal content
    - Optimized classifier instantiation and caching
    - Format validation and compatibility checking
    - Extensible architecture for new classifier types
    """    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize classifier factory."""        self.settings = get_settings()
        self.model_path = model_path
        
        # Classifier cache to avoid re-instantiation
        self._classifier_cache: Dict[str, Any] = {}
        
        # Initialize format mappings
        self._init_format_mappings()
        
        # Configuration for classifier selection
        self.classifier_config = {
            'cache_classifiers': True,
            'enable_multimodal': True,
            'default_options': {
                'detailed_analysis': False,
                'quality_threshold': 0.7,
                'similarity_threshold': 0.8
            }
        }

    def _init_format_mappings(self):
        """Initialize file format to content type mappings."""        self.format_mappings = {
            # Audio formats
            '.mp3': ContentType.AUDIO,
            '.wav': ContentType.AUDIO,
            '.flac': ContentType.AUDIO,
            '.aac': ContentType.AUDIO,
            '.m4a': ContentType.AUDIO,
            '.ogg': ContentType.AUDIO,
            '.wma': ContentType.AUDIO,
            '.opus': ContentType.AUDIO,
            
            # Video formats
            '.mp4': ContentType.VIDEO,
            '.avi': ContentType.VIDEO,
            '.mov': ContentType.VIDEO,
            '.mkv': ContentType.VIDEO,
            '.webm': ContentType.VIDEO,
            '.flv': ContentType.VIDEO,
            '.wmv': ContentType.VIDEO,
            '.m4v': ContentType.VIDEO,
            '.3gp': ContentType.VIDEO,
            
            # Image formats
            '.jpg': ContentType.IMAGE,
            '.jpeg': ContentType.IMAGE,
            '.png': ContentType.IMAGE,
            '.webp': ContentType.IMAGE,
            '.bmp': ContentType.IMAGE,
            '.tiff': ContentType.IMAGE,
            '.tif': ContentType.IMAGE,
            '.gif': ContentType.IMAGE,
            '.svg': ContentType.IMAGE,
            
            # Text formats
            '.txt': ContentType.TEXT,
            '.md': ContentType.TEXT,
            '.rtf': ContentType.TEXT,
            '.docx': ContentType.TEXT,
            '.pdf': ContentType.TEXT,
            '.html': ContentType.TEXT,
            '.xml': ContentType.TEXT,
            '.json': ContentType.TEXT
        }
        
        # MIME type mappings
        self.mime_mappings = {
            # Audio MIME types
            'audio/mpeg': ContentType.AUDIO,
            'audio/wav': ContentType.AUDIO,
            'audio/flac': ContentType.AUDIO,
            'audio/aac': ContentType.AUDIO,
            'audio/ogg': ContentType.AUDIO,
            'audio/x-ms-wma': ContentType.AUDIO,
            
            # Video MIME types
            'video/mp4': ContentType.VIDEO,
            'video/avi': ContentType.VIDEO,
            'video/quicktime': ContentType.VIDEO,
            'video/x-msvideo': ContentType.VIDEO,
            'video/webm': ContentType.VIDEO,
            'video/x-flv': ContentType.VIDEO,
            
            # Image MIME types
            'image/jpeg': ContentType.IMAGE,
            'image/png': ContentType.IMAGE,
            'image/webp': ContentType.IMAGE,
            'image/bmp': ContentType.IMAGE,
            'image/tiff': ContentType.IMAGE,
            'image/gif': ContentType.IMAGE,
            'image/svg+xml': ContentType.IMAGE,
            
            # Text MIME types
            'text/plain': ContentType.TEXT,
            'text/markdown': ContentType.TEXT,
            'text/html': ContentType.TEXT,
            'text/xml': ContentType.TEXT,
            'application/pdf': ContentType.TEXT,
            'application/rtf': ContentType.TEXT,
            'application/json': ContentType.TEXT
        }

    def create_classifier(
        self, 
        content_type: Union[ContentType, str, List[str]], 
        options: Optional[Dict] = None
    ) -> Any:
        """        Create appropriate classifier based on content type.
        
        Args:
            content_type: Type of content or list of file paths for auto-detection
            options: Configuration options for the classifier
            
        Returns:
            Appropriate classifier instance
        """        try:
            # Handle different input types
            if isinstance(content_type, list):
                # Auto-detect from file paths
                detected_types = self._detect_content_types(content_type)
                if len(detected_types) > 1:
                    content_type = ContentType.MULTIMODAL
                else:
                    content_type = next(iter(detected_types))
            elif isinstance(content_type, str):
                if content_type.lower() in [ct.value for ct in ContentType]:
                    content_type = ContentType(content_type.lower())
                else:
                    # Treat as file path
                    content_type = self._detect_content_type(content_type)
            
            # Create and cache classifier
            classifier_key = self._get_classifier_key(content_type, options)
            
            if self.classifier_config['cache_classifiers'] and classifier_key in self._classifier_cache:
                logger.debug(f"Using cached classifier for {content_type}")
                return self._classifier_cache[classifier_key]
            
            # Create new classifier
            classifier = self._instantiate_classifier(content_type, options)
            
            if self.classifier_config['cache_classifiers']:
                self._classifier_cache[classifier_key] = classifier
            
            logger.info(f"Created {content_type.value} classifier")
            return classifier
            
        except Exception as e:
            logger.error(f"Error creating classifier for {content_type}: {e}")
            raise ClassificationError(f"Failed to create classifier: {e}")

    def _detect_content_types(self, file_paths: List[str]) -> set:
        """Detect content types from a list of file paths."""        detected_types = set()
        
        for file_path in file_paths:
            try:
                content_type = self._detect_content_type(file_path)
                detected_types.add(content_type)
            except UnsupportedFormatError:
                logger.warning(f"Unsupported format for file: {file_path}")
                continue
        
        return detected_types

    def _detect_content_type(self, file_path: str) -> ContentType:
        """Detect content type from file path."""        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Try extension mapping first
        if extension in self.format_mappings:
            return self.format_mappings[extension]
        
        # Try MIME type detection
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type in self.mime_mappings:
                return self.mime_mappings[mime_type]
        except Exception as e:
            logger.debug(f"Could not detect MIME type for {file_path}: {e}")
        
        # Fallback analysis based on file content (basic)
        try:
            return self._analyze_file_content(file_path)
        except Exception as e:
            logger.debug(f"Could not analyze file content for {file_path}: {e}")
        
        raise UnsupportedFormatError(f"Unsupported format: {extension} for file {file_path}")

    def _analyze_file_content(self, file_path: Path) -> ContentType:
        """Analyze file content to determine type (fallback method)."""        try:
            # Read first few bytes to detect format
            with open(file_path, 'rb') as f:
                header = f.read(16)
            
            # Check common file signatures
            if header.startswith(b'\xff\xfb') or header.startswith(b'ID3'):
                return ContentType.AUDIO  # MP3
            elif header.startswith(b'RIFF') and b'WAVE' in header:
                return ContentType.AUDIO  # WAV
            elif header.startswith(b'\x00\x00\x00\x18ftypmp4') or header.startswith(b'\x00\x00\x00\x20ftypmp4'):
                return ContentType.VIDEO  # MP4
            elif header.startswith(b'\xff\xd8\xff'):
                return ContentType.IMAGE  # JPEG
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                return ContentType.IMAGE  # PNG
            elif header.startswith(b'%PDF'):
                return ContentType.TEXT  # PDF
            
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(100)
                if content.isprintable():
                    return ContentType.TEXT
            
        except Exception as e:
            logger.debug(f"Error analyzing file content: {e}")
        
        raise UnsupportedFormatError(f"Could not determine content type for {file_path}")

    def _get_classifier_key(self, content_type: ContentType, options: Optional[Dict]) -> str:
        """Generate cache key for classifier."""        options_key = ""
        if options:
            # Create a stable key from options
            sorted_items = sorted(options.items())
            options_key = str(hash(str(sorted_items)))
        
        return f"{content_type.value}_{options_key}"

    def _instantiate_classifier(self, content_type: ContentType, options: Optional[Dict]) -> Any:
        """Instantiate the appropriate classifier."""        # Merge with default options
        merged_options = {**self.classifier_config['default_options']}
        if options:
            merged_options.update(options)
        
        if content_type == ContentType.AUDIO:
            return AudioContentClassifier(self.model_path)
        elif content_type == ContentType.VIDEO:
            return VideoContentClassifier(self.model_path)
        elif content_type == ContentType.IMAGE:
            return ImageContentClassifier(self.model_path)
        elif content_type == ContentType.TEXT:
            return TextContentClassifier(self.model_path)
        elif content_type == ContentType.MULTIMODAL:
            if not self.classifier_config['enable_multimodal']:
                raise ClassificationError("Multimodal classification is disabled")
            return MultimodalContentClassifier(self.model_path)
        else:
            raise ClassificationError(f"Unsupported content type: {content_type}")

    def classify_content(
        self, 
        content_input: Union[str, List[str], Dict[str, Union[str, List[str]]]], 
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Classify content using appropriate classifier.
        
        Args:
            content_input: File path, list of paths, or multimodal content dict
            options: Classification options
            
        Returns:
            Classification results
        """        try:
            # Determine input type and create appropriate classifier
            if isinstance(content_input, str):
                # Single file
                content_type = self._detect_content_type(content_input)
                classifier = self.create_classifier(content_type, options)
                
                return self._classify_single_content(classifier, content_type, content_input, options)
                
            elif isinstance(content_input, list):
                # Multiple files - determine if multimodal
                detected_types = self._detect_content_types(content_input)
                
                if len(detected_types) == 1:
                    # All same type
                    content_type = next(iter(detected_types))
                    classifier = self.create_classifier(content_type, options)
                    
                    # Classify each file
                    results = {}
                    for file_path in content_input:
                        result = self._classify_single_content(classifier, content_type, file_path, options)
                        results[file_path] = result
                    
                    return {
                        'content_type': content_type.value,
                        'individual_results': results,
                        'batch_summary': self._generate_batch_summary(results)
                    }
                else:
                    # Multimodal content
                    classifier = self.create_classifier(ContentType.MULTIMODAL, options)
                    
                    # Organize by type
                    organized_content = self._organize_multimodal_content(content_input)
                    
                    return classifier.classify_multimodal_content(organized_content, options)
                    
            elif isinstance(content_input, dict):
                # Explicitly multimodal
                classifier = self.create_classifier(ContentType.MULTIMODAL, options)
                return classifier.classify_multimodal_content(content_input, options)
            
            else:
                raise ClassificationError(f"Unsupported content input type: {type(content_input)}")
                
        except Exception as e:
            logger.error(f"Error classifying content: {e}")
            raise ClassificationError(f"Content classification failed: {e}")

    def _classify_single_content(
        self, 
        classifier: Any, 
        content_type: ContentType, 
        file_path: str, 
        options: Optional[Dict]
    ) -> Dict[str, Any]:
        """Classify a single content file."""        try:
            if content_type == ContentType.AUDIO:
                return classifier.classify_audio(file_path, options)
            elif content_type == ContentType.VIDEO:
                return classifier.classify_video(file_path, options)
            elif content_type == ContentType.IMAGE:
                return classifier.classify_image(file_path, options)
            elif content_type == ContentType.TEXT:
                # Read text content
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                return classifier.classify_text(text_content, options)
            else:
                raise ClassificationError(f"Cannot classify single content of type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error classifying {content_type.value} content from {file_path}: {e}")
            raise

    def _organize_multimodal_content(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Organize file paths by content type for multimodal classification."""        organized = {}
        
        for file_path in file_paths:
            try:
                content_type = self._detect_content_type(file_path)
                type_key = content_type.value
                
                if type_key not in organized:
                    organized[type_key] = []
                
                organized[type_key].append(file_path)
                
            except UnsupportedFormatError as e:
                logger.warning(f"Skipping unsupported file {file_path}: {e}")
                continue
        
        return organized

    def _generate_batch_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for batch classification results."""        try:
            total_files = len(results)
            successful_classifications = sum(1 for result in results.values() 
                                           if not result.get('error'))
            
            # Aggregate quality scores
            quality_scores = []
            for result in results.values():
                if not result.get('error'):
                    quality = result.get('quality_metrics', {}).get('overall_quality')
                    if quality is not None:
                        quality_scores.append(quality)
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Count content types/genres
            content_types = {}
            genres = {}
            
            for result in results.values():
                if not result.get('error'):
                    classifications = result.get('classifications', {})
                    
                    # Content type
                    content_type = classifications.get('content_type', {}).get('primary')
                    if content_type:
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    # Genre
                    genre = classifications.get('genre_detection', {}).get('primary_genre')
                    if genre and genre != 'unknown':
                        genres[genre] = genres.get(genre, 0) + 1
            
            return {
                'total_files': total_files,
                'successful_classifications': successful_classifications,
                'success_rate': successful_classifications / total_files if total_files > 0 else 0,
                'average_quality': float(avg_quality),
                'content_type_distribution': content_types,
                'genre_distribution': genres,
                'quality_distribution': self._get_quality_distribution(quality_scores)
            }
            
        except Exception as e:
            logger.error(f"Error generating batch summary: {e}")
            return {'total_files': len(results), 'error': 'Summary generation failed'}

    def _get_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Get distribution of quality grades."""        distribution = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D': 0}
        
        for score in quality_scores:
            if score >= 0.9:
                distribution['A+'] += 1
            elif score >= 0.8:
                distribution['A'] += 1
            elif score >= 0.7:
                distribution['B+'] += 1
            elif score >= 0.6:
                distribution['B'] += 1
            elif score >= 0.5:
                distribution['C+'] += 1
            elif score >= 0.4:
                distribution['C'] += 1
            else:
                distribution['D'] += 1
        
        return distribution

    def compare_content(
        self, 
        content1: Union[str, List[str], Dict[str, Union[str, List[str]]]], 
        content2: Union[str, List[str], Dict[str, Union[str, List[str]]]], 
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """        Compare two sets of content for similarity.
        
        Args:
            content1: First content to compare
            content2: Second content to compare
            options: Comparison options
            
        Returns:
            Similarity analysis results
        """        try:
            # Determine content types
            type1 = self._determine_comparison_type(content1)
            type2 = self._determine_comparison_type(content2)
            
            if type1 != type2:
                logger.warning("Comparing different content types may produce unreliable results")
            
            # Use multimodal comparison for complex content
            if type1 == ContentType.MULTIMODAL or type2 == ContentType.MULTIMODAL:
                classifier = self.create_classifier(ContentType.MULTIMODAL, options)
                
                # Convert to multimodal format if needed
                content1_multimodal = self._to_multimodal_format(content1)
                content2_multimodal = self._to_multimodal_format(content2)
                
                return classifier.compare_multimodal_content(content1_multimodal, content2_multimodal)
            
            else:
                # Single modality comparison
                classifier = self.create_classifier(type1, options)
                return self._compare_single_modality(classifier, type1, content1, content2, options)
                
        except Exception as e:
            logger.error(f"Error comparing content: {e}")
            raise ClassificationError(f"Content comparison failed: {e}")

    def _determine_comparison_type(self, content: Union[str, List[str], Dict]) -> ContentType:
        """Determine content type for comparison."""        if isinstance(content, str):
            return self._detect_content_type(content)
        elif isinstance(content, list):
            detected_types = self._detect_content_types(content)
            return ContentType.MULTIMODAL if len(detected_types) > 1 else next(iter(detected_types))
        elif isinstance(content, dict):
            return ContentType.MULTIMODAL
        else:
            raise ClassificationError(f"Unsupported content type for comparison: {type(content)}")

    def _to_multimodal_format(self, content: Union[str, List[str], Dict]) -> Dict[str, Union[str, List[str]]]:
        """Convert content to multimodal format."""        if isinstance(content, dict):
            return content
        elif isinstance(content, str):
            content_type = self._detect_content_type(content)
            return {content_type.value: content}
        elif isinstance(content, list):
            return self._organize_multimodal_content(content)
        else:
            raise ClassificationError(f"Cannot convert to multimodal format: {type(content)}")

    def _compare_single_modality(
        self, 
        classifier: Any, 
        content_type: ContentType, 
        content1: Union[str, List[str]], 
        content2: Union[str, List[str]], 
        options: Optional[Dict]
    ) -> Dict[str, Any]:
        """Compare content within a single modality."""        try:
            # For now, handle simple string comparison
            if isinstance(content1, str) and isinstance(content2, str):
                if content_type == ContentType.TEXT:
                    # Read text files
                    with open(content1, 'r', encoding='utf-8') as f:
                        text1 = f.read()
                    with open(content2, 'r', encoding='utf-8') as f:
                        text2 = f.read()
                    return classifier.compare_texts(text1, text2)
                elif content_type == ContentType.IMAGE:
                    return classifier.compare_images(content1, content2)
                elif content_type == ContentType.AUDIO:
                    # Would need to implement in AudioContentClassifier
                    logger.warning("Audio comparison not yet implemented")
                    return {'similarity_score': 0.0, 'error': 'Audio comparison not implemented'}
                elif content_type == ContentType.VIDEO:
                    # Would need to implement in VideoContentClassifier
                    logger.warning("Video comparison not yet implemented")
                    return {'similarity_score': 0.0, 'error': 'Video comparison not implemented'}
            
            # For other cases, return basic comparison
            return {
                'similarity_score': 0.0,
                'comparison_type': 'unsupported',
                'message': 'Complex comparison not yet implemented for this content type'
            }
            
        except Exception as e:
            logger.error(f"Error in single modality comparison: {e}")
            raise

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats by content type."""        formats = {}
        
        for content_type in ContentType:
            if content_type == ContentType.MULTIMODAL:
                continue
                
            extensions = []
            for ext, ct in self.format_mappings.items():
                if ct == content_type:
                    extensions.append(ext)
            
            formats[content_type.value] = sorted(extensions)
        
        return formats

    def validate_content(self, content_input: Union[str, List[str], Dict]) -> Dict[str, Any]:
        """        Validate content before classification.
        
        Args:
            content_input: Content to validate
            
        Returns:
            Validation results
        """        try:
            validation = {
                'is_valid': True,
                'supported_files': [],
                'unsupported_files': [],
                'warnings': [],
                'content_types_detected': set()
            }
            
            # Collect all file paths
            file_paths = []
            if isinstance(content_input, str):
                file_paths = [content_input]
            elif isinstance(content_input, list):
                file_paths = content_input
            elif isinstance(content_input, dict):
                for value in content_input.values():
                    if isinstance(value, str):
                        file_paths.append(value)
                    elif isinstance(value, list):
                        file_paths.extend(value)
            
            # Validate each file
            for file_path in file_paths:
                try:
                    file_path_obj = Path(file_path)
                    
                    # Check if file exists
                    if not file_path_obj.exists():
                        validation['warnings'].append(f"File not found: {file_path}")
                        validation['unsupported_files'].append(file_path)
                        continue
                    
                    # Check if file is readable
                    if not file_path_obj.is_file():
                        validation['warnings'].append(f"Not a regular file: {file_path}")
                        validation['unsupported_files'].append(file_path)
                        continue
                    
                    # Detect content type
                    content_type = self._detect_content_type(file_path)
                    validation['content_types_detected'].add(content_type.value)
                    validation['supported_files'].append({
                        'file_path': file_path,
                        'content_type': content_type.value,
                        'file_size': file_path_obj.stat().st_size
                    })
                    
                except UnsupportedFormatError as e:
                    validation['warnings'].append(f"Unsupported format: {file_path} - {e}")
                    validation['unsupported_files'].append(file_path)
                except Exception as e:
                    validation['warnings'].append(f"Error validating {file_path}: {e}")
                    validation['unsupported_files'].append(file_path)
            
            # Set overall validity
            validation['is_valid'] = len(validation['supported_files']) > 0
            
            # Convert set to list for JSON serialization
            validation['content_types_detected'] = list(validation['content_types_detected'])
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'supported_files': [],
                'unsupported_files': [],
                'warnings': []
            }

    def clear_cache(self):
        """Clear the classifier cache."""        self._classifier_cache.clear()
        logger.info("Classifier cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached classifiers."""        return {
            'cached_classifiers': len(self._classifier_cache),
            'cache_keys': list(self._classifier_cache.keys()),
            'cache_enabled': self.classifier_config['cache_classifiers']
        }

    def set_config(self, config: Dict[str, Any]):
        """Update factory configuration."""        self.classifier_config.update(config)
        logger.info(f"Factory configuration updated: {config}")

    def get_classifier_info(self, content_type: Union[ContentType, str]) -> Dict[str, Any]:
        """Get information about a specific classifier type."""        try:
            if isinstance(content_type, str):
                content_type = ContentType(content_type.lower())
            
            classifier_classes = {
                ContentType.AUDIO: AudioContentClassifier,
                ContentType.VIDEO: VideoContentClassifier,
                ContentType.IMAGE: ImageContentClassifier,
                ContentType.TEXT: TextContentClassifier,
                ContentType.MULTIMODAL: MultimodalContentClassifier
            }
            
            classifier_class = classifier_classes.get(content_type)
            if not classifier_class:
                return {'error': f'Unknown content type: {content_type}'}
            
            # Get supported formats for this type
            supported_formats = []
            for ext, ct in self.format_mappings.items():
                if ct == content_type:
                    supported_formats.append(ext)
            
            return {
                'content_type': content_type.value,
                'classifier_class': classifier_class.__name__,
                'supported_formats': sorted(supported_formats),
                'features': self._get_classifier_features(content_type),
                'is_cached': any(content_type.value in key for key in self._classifier_cache.keys())
            }
            
        except Exception as e:
            logger.error(f"Error getting classifier info: {e}")
            return {'error': str(e)}

    def _get_classifier_features(self, content_type: ContentType) -> List[str]:
        """Get list of features supported by a classifier type."""        feature_map = {
            ContentType.AUDIO: [
                'genre_classification', 'mood_analysis', 'quality_assessment',
                'similarity_matching', 'spectral_analysis', 'tempo_detection'
            ],
            ContentType.VIDEO: [
                'scene_detection', 'object_recognition', 'activity_classification',
                'quality_assessment', 'frame_analysis', 'similarity_matching'
            ],
            ContentType.IMAGE: [
                'content_classification', 'style_analysis', 'object_detection',
                'face_recognition', 'color_analysis', 'quality_assessment'
            ],
            ContentType.TEXT: [
                'content_classification', 'sentiment_analysis', 'language_detection',
                'genre_detection', 'entity_extraction', 'similarity_matching'
            ],
            ContentType.MULTIMODAL: [
                'cross_modal_analysis', 'content_coherence', 'unified_classification',
                'multimodal_similarity', 'quality_correlation', 'thematic_consistency'
            ]
        }
        
        return feature_map.get(content_type, [])
