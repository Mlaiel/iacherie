"""Optical Character Reader - Enterprise OCR & Text Recognition System
===================================================================

Advanced optical character recognition system with multi-language support,
text extraction, and intelligent document analysis for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import re
import json
from PIL import Image
import pytesseract
from collections import Counter

from ..base import BaseAgent, AgentStatus
try:
    from core.exceptions import OCRProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    OCRProcessingError, ValidationError = globals().get('OCRProcessingError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class OpticalCharacterReader(BaseAgent):
    """
    Enterprise-grade OCR system providing comprehensive text extraction,
    recognition, and analysis from images and documents.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="optical_character_reader",
            name="Optical Character Reader",
            version="2.1.0"
        )
        
        self.performance_monitor = PerformanceMonitor("ocr_processing")
        self.text_processor = TextProcessor()
        
        # OCR configuration
        self.confidence_threshold = 60  # Tesseract confidence threshold
        self.supported_languages = [
            'eng', 'fra', 'deu', 'spa', 'ita', 'por', 'rus', 'ara', 'chi_sim', 'jpn'
        ]
        self.default_language = 'eng'
        
        # Text processing configuration
        self.text_filters = {
            'min_word_length': 2,
            'max_line_length': 1000,
            'remove_special_chars': True,
            'normalize_whitespace': True
        }
        
        # Document analysis patterns
        self.document_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'price': r'\$\d+\.?\d*',
            'hashtag': r'#\w+',
            'mention': r'@\w+'
        }

    async def initialize(self) -> bool:
        """Initialize OCR components"""
        try:
            logger.info("Initializing Optical Character Reader...")
            
            # Test Tesseract availability
            try:
                pytesseract.get_tesseract_version()
                logger.info("Tesseract OCR engine detected")
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}")
                # Continue with limited functionality
            
            # Initialize text preprocessing parameters
            self.preprocessing_params = {
                'resize_factor': 2.0,
                'gaussian_blur_kernel': (1, 1),
                'morph_kernel_size': (2, 2),
                'dilation_iterations': 1,
                'erosion_iterations': 1
            }
            
            self.status = AgentStatus.READY
            logger.info("Optical Character Reader initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"OCR initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def extract_text(
        self, 
        image: np.ndarray,
        language: str = None,
        preprocessing: bool = True,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from image using OCR
        
        Args:
            image: Input image as numpy array
            language: Language code for OCR (e.g., 'eng', 'fra')
            preprocessing: Whether to apply image preprocessing
            include_confidence: Include confidence scores in results
            
        Returns:
            OCR extraction results with text and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting text extraction...")
            
            # Validate input
            if image is None or image.size == 0:
                raise ValidationError("Invalid input image")
            
            # Set language
            lang = language or self.default_language
            if lang not in self.supported_languages:
                logger.warning(f"Language {lang} not supported, using default")
                lang = self.default_language
            
            # Preprocess image for better OCR
            processed_image = image.copy()
            if preprocessing:
                processed_image = await self._preprocess_image(image)
            
            # Perform OCR extraction
            ocr_results = await self._perform_ocr_extraction(processed_image, lang, include_confidence)
            
            # Post-process extracted text
            processed_text = await self._post_process_text(ocr_results['raw_text'])
            
            # Analyze document structure
            document_analysis = await self._analyze_document_structure(ocr_results)
            
            # Extract structured data
            structured_data = await self._extract_structured_data(processed_text)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_ocr_quality(ocr_results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'image_dimensions': image.shape,
                'language_used': lang,
                'preprocessing_applied': preprocessing,
                'extracted_text': {
                    'raw_text': ocr_results['raw_text'],
                    'processed_text': processed_text,
                    'word_count': len(processed_text.split()) if processed_text else 0,
                    'character_count': len(processed_text) if processed_text else 0,
                    'line_count': len(processed_text.splitlines()) if processed_text else 0
                },
                'confidence_data': ocr_results.get('confidence_data', {}),
                'document_analysis': document_analysis,
                'structured_data': structured_data,
                'quality_metrics': quality_metrics
            }
            
            logger.info(
                f"Text extraction completed: {result['extracted_text']['word_count']} "
                f"words extracted in {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'extracted_text': {'raw_text': '', 'processed_text': '', 'word_count': 0}
            }

    async def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Resize image for better OCR (if too small)
            height, width = gray.shape
            if max(height, width) < 300:
                scale_factor = self.preprocessing_params['resize_factor']
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Threshold to binary image
            # Try adaptive thresholding first
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up text
            kernel = np.ones(self.preprocessing_params['morph_kernel_size'], np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    async def _perform_ocr_extraction(
        self, 
        image: np.ndarray, 
        language: str,
        include_confidence: bool
    ) -> Dict[str, Any]:
        """Perform OCR extraction with confidence scores"""
        try:
            # Configure Tesseract
            config = f'--oem 3 --psm 6 -l {language}'
            
            # Extract text
            extracted_text = pytesseract.image_to_string(image, config=config)
            
            ocr_results = {
                'raw_text': extracted_text,
                'language': language
            }
            
            if include_confidence:
                # Get detailed data with confidence scores
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Process confidence data
                confidence_data = await self._process_confidence_data(data)
                ocr_results['confidence_data'] = confidence_data
                
                # Get word-level bounding boxes
                word_boxes = await self._extract_word_boxes(data)
                ocr_results['word_boxes'] = word_boxes
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {'raw_text': '', 'language': language}

    async def _process_confidence_data(self, tesseract_data: Dict) -> Dict[str, Any]:
        """Process Tesseract confidence data"""
        try:
            confidences = [conf for conf in tesseract_data['conf'] if int(conf) > 0]
            
            if not confidences:
                return {'average_confidence': 0, 'confidence_distribution': []}
            
            confidence_stats = {
                'average_confidence': np.mean(confidences),
                'min_confidence': min(confidences),
                'max_confidence': max(confidences),
                'std_confidence': np.std(confidences),
                'high_confidence_words': len([c for c in confidences if c >= 80]),
                'low_confidence_words': len([c for c in confidences if c < self.confidence_threshold]),
                'total_words': len(confidences)
            }
            
            # Confidence distribution
            confidence_bins = [0, 20, 40, 60, 80, 100]
            confidence_dist = []
            
            for i in range(len(confidence_bins) - 1):
                count = len([c for c in confidences 
                           if confidence_bins[i] <= c < confidence_bins[i+1]])
                confidence_dist.append({
                    'range': f"{confidence_bins[i]}-{confidence_bins[i+1]}",
                    'count': count,
                    'percentage': (count / len(confidences)) * 100
                })
            
            confidence_stats['confidence_distribution'] = confidence_dist
            
            return confidence_stats
            
        except Exception as e:
            logger.error(f"Confidence data processing failed: {e}")
            return {'average_confidence': 0}

    async def _extract_word_boxes(self, tesseract_data: Dict) -> List[Dict[str, Any]]:
        """Extract word-level bounding boxes"""
        try:
            word_boxes = []
            
            for i, word in enumerate(tesseract_data['text']):
                if word.strip():  # Only non-empty words
                    confidence = int(tesseract_data['conf'][i])
                    
                    if confidence > 0:  # Valid detection
                        word_box = {
                            'word': word,
                            'confidence': confidence,
                            'bbox': {
                                'x': int(tesseract_data['left'][i]),
                                'y': int(tesseract_data['top'][i]),
                                'width': int(tesseract_data['width'][i]),
                                'height': int(tesseract_data['height'][i])
                            },
                            'block_num': int(tesseract_data['block_num'][i]),
                            'par_num': int(tesseract_data['par_num'][i]),
                            'line_num': int(tesseract_data['line_num'][i])
                        }
                        word_boxes.append(word_box)
            
            return word_boxes
            
        except Exception as e:
            logger.error(f"Word box extraction failed: {e}")
            return []

    async def _post_process_text(self, raw_text: str) -> str:
        """Post-process extracted text"""
        try:
            if not raw_text:
                return ""
            
            text = raw_text
            
            # Normalize whitespace
            if self.text_filters['normalize_whitespace']:
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
            
            # Remove very short words (likely OCR errors)
            if self.text_filters['min_word_length'] > 1:
                words = text.split()
                filtered_words = [w for w in words if len(w) >= self.text_filters['min_word_length']]
                text = ' '.join(filtered_words)
            
            # Remove excessive special characters
            if self.text_filters['remove_special_chars']:
                text = re.sub(r'[^\w\s\.,;:!?\-@#$%&()]+', '', text)
            
            # Limit line length
            if self.text_filters['max_line_length'] > 0:
                lines = text.splitlines()
                processed_lines = []
                for line in lines:
                    if len(line) <= self.text_filters['max_line_length']:
                        processed_lines.append(line)
                text = '\n'.join(processed_lines)
            
            return text
            
        except Exception as e:
            logger.error(f"Text post-processing failed: {e}")
            return raw_text

    async def _analyze_document_structure(self, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document structure from OCR results"""
        try:
            analysis = {
                'document_type': 'unknown',
                'layout_analysis': {},
                'text_regions': [],
                'reading_order': []
            }
            
            # Basic document type detection
            text = ocr_results.get('raw_text', '')
            
            if any(keyword in text.lower() for keyword in ['subject:', 'from:', 'to:', '@']):
                analysis['document_type'] = 'email'
            elif any(keyword in text.lower() for keyword in ['invoice', 'bill', 'total:', 'amount:']):
                analysis['document_type'] = 'invoice'
            elif any(keyword in text.lower() for keyword in ['dear', 'sincerely', 'regards']):
                analysis['document_type'] = 'letter'
            elif any(keyword in text.lower() for keyword in ['menu', 'price', 'order']):
                analysis['document_type'] = 'menu'
            elif len(text.split()) > 100:
                analysis['document_type'] = 'article'
            else:
                analysis['document_type'] = 'text_snippet'
            
            # Analyze text regions if word boxes available
            word_boxes = ocr_results.get('word_boxes', [])
            if word_boxes:
                regions = await self._group_text_regions(word_boxes)
                analysis['text_regions'] = regions
                analysis['layout_analysis'] = await self._analyze_layout(regions)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document structure analysis failed: {e}")
            return {'document_type': 'unknown'}

    async def _group_text_regions(self, word_boxes: List[Dict]) -> List[Dict[str, Any]]:
        """Group words into text regions"""
        try:
            # Group by line number first
            lines = {}
            for word_box in word_boxes:
                line_num = word_box['line_num']
                if line_num not in lines:
                    lines[line_num] = []
                lines[line_num].append(word_box)
            
            # Create regions from lines
            regions = []
            for line_num, words in lines.items():
                if words:
                    # Calculate bounding box for entire line
                    left = min(word['bbox']['x'] for word in words)
                    top = min(word['bbox']['y'] for word in words)
                    right = max(word['bbox']['x'] + word['bbox']['width'] for word in words)
                    bottom = max(word['bbox']['y'] + word['bbox']['height'] for word in words)
                    
                    line_text = ' '.join(word['word'] for word in words)
                    avg_confidence = np.mean([word['confidence'] for word in words])
                    
                    region = {
                        'region_id': len(regions),
                        'text': line_text,
                        'bbox': {
                            'x': left, 'y': top,
                            'width': right - left,
                            'height': bottom - top
                        },
                        'average_confidence': avg_confidence,
                        'word_count': len(words),
                        'line_number': line_num
                    }
                    regions.append(region)
            
            # Sort regions by reading order (top to bottom, left to right)
            regions.sort(key=lambda r: (r['bbox']['y'], r['bbox']['x']))
            
            return regions
            
        except Exception as e:
            logger.error(f"Text region grouping failed: {e}")
            return []

    async def _analyze_layout(self, regions: List[Dict]) -> Dict[str, Any]:
        """Analyze document layout"""
        try:
            if not regions:
                return {}
            
            layout_analysis = {
                'total_regions': len(regions),
                'average_region_height': np.mean([r['bbox']['height'] for r in regions]),
                'average_region_width': np.mean([r['bbox']['width'] for r in regions]),
                'text_alignment': 'unknown',
                'column_count': 1,
                'estimated_font_size': 12
            }
            
            # Analyze text alignment
            left_edges = [r['bbox']['x'] for r in regions]
            if len(set(left_edges)) <= 2:
                layout_analysis['text_alignment'] = 'left'
            elif all(abs(x - left_edges[0]) < 50 for x in left_edges):
                layout_analysis['text_alignment'] = 'left'
            else:
                layout_analysis['text_alignment'] = 'mixed'
            
            # Estimate column count (simplified)
            if len(regions) > 5:
                x_positions = [r['bbox']['x'] for r in regions]
                x_clusters = len(set(x // 100 for x in x_positions))  # Group by 100px
                layout_analysis['column_count'] = min(x_clusters, 3)
            
            return layout_analysis
            
        except Exception as e:
            logger.error(f"Layout analysis failed: {e}")
            return {}

    async def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text using regex patterns"""
        try:
            structured_data = {}
            
            for data_type, pattern in self.document_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Remove duplicates and clean matches
                    unique_matches = list(set(matches))
                    structured_data[data_type] = unique_matches[:10]  # Limit to 10 matches
            
            # Additional structured data extraction
            structured_data['statistics'] = {
                'total_characters': len(text),
                'total_words': len(text.split()),
                'total_sentences': len(re.split(r'[.!?]+', text)),
                'average_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0
            }
            
            # Language detection hints
            structured_data['language_hints'] = await self._detect_language_hints(text)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            return {}

    async def _detect_language_hints(self, text: str) -> Dict[str, Any]:
        """Detect language hints from text"""
        try:
            # Simple language detection based on common words
            language_indicators = {
                'english': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that'],
                'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et'],
                'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das'],
                'spanish': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un'],
            }
            
            words = text.lower().split()
            word_counter = Counter(words)
            
            language_scores = {}
            for lang, indicators in language_indicators.items():
                score = sum(word_counter.get(word, 0) for word in indicators)
                language_scores[lang] = score
            
            if language_scores:
                likely_language = max(language_scores, key=language_scores.get)
                confidence = language_scores[likely_language] / sum(language_scores.values())
            else:
                likely_language = 'unknown'
                confidence = 0.0
            
            return {
                'likely_language': likely_language,
                'confidence': confidence,
                'language_scores': language_scores
            }
            
        except Exception as e:
            logger.error(f"Language hint detection failed: {e}")
            return {'likely_language': 'unknown', 'confidence': 0.0}

    async def _calculate_ocr_quality(self, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate OCR quality metrics"""
        try:
            quality_metrics = {
                'overall_score': 0.5,
                'text_confidence': 0.0,
                'text_density': 0.0,
                'character_recognition_rate': 0.0,
                'quality_issues': []
            }
            
            # Calculate text confidence if available
            confidence_data = ocr_results.get('confidence_data', {})
            if confidence_data:
                avg_confidence = confidence_data.get('average_confidence', 0)
                quality_metrics['text_confidence'] = avg_confidence / 100.0
                
                low_conf_words = confidence_data.get('low_confidence_words', 0)
                total_words = confidence_data.get('total_words', 1)
                
                if low_conf_words / total_words > 0.3:
                    quality_metrics['quality_issues'].append('high_low_confidence_words')
            
            # Calculate text density
            text = ocr_results.get('raw_text', '')
            if text:
                # Simple text density calculation
                non_space_chars = len(text.replace(' ', '').replace('\n', ''))
                total_chars = len(text)
                quality_metrics['text_density'] = non_space_chars / total_chars if total_chars > 0 else 0
            
            # Estimate character recognition rate
            if text:
                # Count recognizable characters vs. total
                recognizable_chars = len(re.findall(r'[a-zA-Z0-9]', text))
                total_chars = len(text.replace(' ', '').replace('\n', ''))
                quality_metrics['character_recognition_rate'] = (
                    recognizable_chars / total_chars if total_chars > 0 else 0
                )
            
            # Calculate overall score
            scores = [
                quality_metrics['text_confidence'] * 0.4,
                quality_metrics['text_density'] * 0.3,
                quality_metrics['character_recognition_rate'] * 0.3
            ]
            quality_metrics['overall_score'] = np.mean([s for s in scores if s > 0])
            
            # Quality classification
            if quality_metrics['overall_score'] >= 0.8:
                quality_metrics['quality_rating'] = 'excellent'
            elif quality_metrics['overall_score'] >= 0.6:
                quality_metrics['quality_rating'] = 'good'
            elif quality_metrics['overall_score'] >= 0.4:
                quality_metrics['quality_rating'] = 'fair'
            else:
                quality_metrics['quality_rating'] = 'poor'
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"OCR quality calculation failed: {e}")
            return {'overall_score': 0.5, 'quality_rating': 'unknown'}

    async def batch_extract_text(
        self, 
        images: List[np.ndarray],
        language: str = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Extract text from multiple images concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_single(image):
            async with semaphore:
                return await self.extract_text(image, language)
        
        tasks = [extract_single(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) 
                else {'status': 'error', 'error': str(result)} 
                for result in results]

    def get_supported_languages(self) -> List[str]:
        """
Get list of supported OCR languages"""
        return self.supported_languages.copy()

    def set_confidence_threshold(self, threshold: int) -> None:
        """
Set OCR confidence threshold"""
        if 0 <= threshold <= 100:
            self.confidence_threshold = threshold
            logger.info(f"OCR confidence threshold set to {threshold}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.performance_monitor.close()
            await self.text_processor.cleanup()
            logger.info("OCR cleanup completed")
        except Exception as e:
            logger.error(f"OCR cleanup failed: {e}")

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get OCR processing capabilities"""
        return {
            'supported_languages': self.supported_languages,
            'confidence_threshold': self.confidence_threshold,
            'text_filters': self.text_filters,
            'document_types_recognized': [
                'email', 'invoice', 'letter', 'menu', 'article', 'text_snippet'
            ],
            'structured_data_extraction': list(self.document_patterns.keys()),
            'batch_processing': True,
            'quality_assessment': True
        }
