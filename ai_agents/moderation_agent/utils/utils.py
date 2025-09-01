"""Moderation Agent Utilities - Advanced Content Processing Utilities

Enterprise-grade utility functions for content preprocessing, feature extraction,
and analysis supporting the ultra-advanced moderation system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import re
import cv2
import numpy as np
import librosa
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Tuple, Any, Optional, Union
import torch
import torchvision.transforms as transforms
from urllib.parse import urlparse
import hashlib
import base64
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

class ContentPreprocessor:
    """
    Advanced content preprocessor for preparing multi-format content for analysis
    
    Handles text normalization, image preprocessing, audio feature extraction,
    and video frame extraction with optimized performance.
    """
    
    def __init__(self):
        # Image preprocessing transforms
        self.image_transforms = {
            'standard': transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ]),
            
            'nsfw_detection': transforms.Compose([
                transforms.Resize((299, 299)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.5, 0.5, 0.5],
                    std=[0.5, 0.5, 0.5]
                )
            ]),
            
            'violence_detection': transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ColorJitter(brightness=0.1, contrast=0.1),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        }
        
        # Text preprocessing patterns
        self.text_patterns = {
            'url_pattern': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'email_pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'mention_pattern': re.compile(r'@[A-Za-z0-9_]+'),
            'hashtag_pattern': re.compile(r'#[A-Za-z0-9_]+'),
            'phone_pattern': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'profanity_pattern': re.compile(r'\b(?:fuck|shit|damn|hell|ass|bitch)\b', re.IGNORECASE),
            'caps_pattern': re.compile(r'\b[A-Z]{3,}\b'),
            'repeated_chars': re.compile(r'(.)\1{2,}'),
            'excessive_punctuation': re.compile(r'[!?]{2,}')
        }
    
    def preprocess_text(self, text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive text preprocessing with feature extraction
        
        Args:
            text: Input text to preprocess
            options: Preprocessing options
            
        Returns:
            Preprocessed text with extracted features
        """
        if not text or not isinstance(text, str):
            return {
                'clean_text': '',
                'original_length': 0,
                'features': {},
                'flags': []
            }
        
        original_text = text
        original_length = len(text)
        flags = []
        features = {}
        
        try:
            # Basic normalization
            text = text.strip()
            
            # Extract URLs and replace with placeholder
            urls = self.text_patterns['url_pattern'].findall(text)
            if urls:
                text = self.text_patterns['url_pattern'].sub('[URL]', text)
                features['urls'] = urls
                flags.append('contains_urls')
            
            # Extract emails and replace with placeholder
            emails = self.text_patterns['email_pattern'].findall(text)
            if emails:
                text = self.text_patterns['email_pattern'].sub('[EMAIL]', text)
                features['emails'] = emails
                flags.append('contains_emails')
            
            # Extract mentions
            mentions = self.text_patterns['mention_pattern'].findall(text)
            if mentions:
                features['mentions'] = mentions
            
            # Extract hashtags
            hashtags = self.text_patterns['hashtag_pattern'].findall(text)
            if hashtags:
                features['hashtags'] = hashtags
            
            # Extract phone numbers
            phones = self.text_patterns['phone_pattern'].findall(text)
            if phones:
                text = self.text_patterns['phone_pattern'].sub('[PHONE]', text)
                features['phones'] = phones
                flags.append('contains_phones')
            
            # Analyze text characteristics
            features.update(self._extract_text_features(original_text))
            
            # Detect potential issues
            if self.text_patterns['profanity_pattern'].search(original_text):
                flags.append('contains_profanity')
            
            caps_matches = self.text_patterns['caps_pattern'].findall(original_text)
            if caps_matches:
                features['caps_words'] = caps_matches
                if len(caps_matches) / len(original_text.split()) > 0.3:
                    flags.append('excessive_caps')
            
            repeated_matches = self.text_patterns['repeated_chars'].findall(original_text)
            if repeated_matches and len(repeated_matches) > 3:
                flags.append('repeated_characters')
            
            punct_matches = self.text_patterns['excessive_punctuation'].findall(original_text)
            if punct_matches:
                flags.append('excessive_punctuation')
            
            # Language detection
            features['detected_language'] = self._detect_language(original_text)
            
            # Readability metrics
            features['readability'] = self._calculate_readability(original_text)
            
            return {
                'clean_text': text,
                'original_text': original_text,
                'original_length': original_length,
                'clean_length': len(text),
                'features': features,
                'flags': flags
            }
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return {
                'clean_text': original_text,
                'original_length': original_length,
                'features': {},
                'flags': ['preprocessing_error'],
                'error': str(e)
            }
    
    def preprocess_image(self, image_input: Union[str, np.ndarray, Image.Image], 
                        transform_type: str = 'standard') -> Dict[str, Any]:
        """
        Advanced image preprocessing with quality enhancement and feature extraction
        
        Args:
            image_input: Image file path, numpy array, or PIL Image
            transform_type: Type of preprocessing transformation
            
        Returns:
            Preprocessed image tensor and metadata
        """
        try:
            # Load image
            if isinstance(image_input, str):
                image = Image.open(image_input).convert('RGB')
                image_path = image_input
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(image_input).convert('RGB')
                image_path = None
            elif isinstance(image_input, Image.Image):
                image = image_input.convert('RGB')
                image_path = None
            else:
                raise ValueError("Unsupported image input type")
            
            # Extract image metadata
            metadata = self._extract_image_metadata(image, image_path)
            
            # Image quality enhancement
            enhanced_image = self._enhance_image_quality(image)
            
            # Apply preprocessing transforms
            transform = self.image_transforms.get(transform_type, self.image_transforms['standard'])
            processed_tensor = transform(enhanced_image).unsqueeze(0)  # Add batch dimension
            
            # Extract visual features
            features = self._extract_visual_features(image)
            
            return {
                'tensor': processed_tensor,
                'original_image': image,
                'enhanced_image': enhanced_image,
                'metadata': metadata,
                'features': features,
                'transform_type': transform_type,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return {
                'tensor': None,
                'success': False,
                'error': str(e)
            }
    
    def preprocess_audio(self, audio_input: Union[str, np.ndarray], 
                        sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Advanced audio preprocessing with feature extraction
        
        Args:
            audio_input: Audio file path or numpy array
            sample_rate: Target sample rate
            
        Returns:
            Processed audio features and metadata
        """
        try:
            # Load audio
            if isinstance(audio_input, str):
                audio, sr = librosa.load(audio_input, sr=sample_rate)
                audio_path = audio_input
            elif isinstance(audio_input, np.ndarray):
                audio = audio_input
                sr = sample_rate
                audio_path = None
            else:
                raise ValueError("Unsupported audio input type")
            
            # Audio normalization
            audio = librosa.util.normalize(audio)
            
            # Extract comprehensive audio features
            features = self._extract_audio_features(audio, sr)
            
            # Convert to spectrograms
            spectrograms = self._generate_spectrograms(audio, sr)
            
            # Audio quality metrics
            quality_metrics = self._analyze_audio_quality(audio, sr)
            
            return {
                'audio_data': audio,
                'sample_rate': sr,
                'duration': len(audio) / sr,
                'features': features,
                'spectrograms': spectrograms,
                'quality_metrics': quality_metrics,
                'audio_path': audio_path,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""
        if not text:
            return {}
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0,
            'unique_words': len(set(word.lower() for word in words)),
            'lexical_diversity': len(set(word.lower() for word in words)) / len(words) if words else 0,
            'punctuation_ratio': sum(1 for char in text if char in '.,!?;:') / len(text) if text else 0,
            'uppercase_ratio': sum(1 for char in text if char.isupper()) / len(text) if text else 0,
            'digit_ratio': sum(1 for char in text if char.isdigit()) / len(text) if text else 0,
            'whitespace_ratio': sum(1 for char in text if char.isspace()) / len(text) if text else 0
        }
    
    def _detect_language(self, text: str) -> str:
        """
Simple language detection based on character patterns"""
        try:
            # Simple heuristic-based language detection
            if re.search(r'[äöüÄÖÜß]', text):
                return 'de'
            elif re.search(r'[àâäçéèêëïîôùûüÿ]', text):
                return 'fr'
            elif re.search(r'[áéíóúñü¿¡]', text):
                return 'es'
            elif re.search(r'[àèéìíîòóùú]', text):
                return 'it'
            elif re.search(r'[ąćęłńóśźż]', text):
                return 'pl'
            elif re.search(r'[а-я]', text.lower()):
                return 'ru'
            elif re.search(r'[ひらがなカタカナ漢字]', text):
                return 'ja'
            elif re.search(r'[가-힣]', text):
                return 'ko'
            elif re.search(r'[一-龯]', text):
                return 'zh'
            else:
                return 'en'  # Default to English
        except:
            return 'unknown'
    
    def _calculate_readability(self, text: str) -> Dict[str, float]:
        """
Calculate text readability metrics"""
        if not text:
            return {}
        
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return {}
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        
        return {
            'flesch_reading_ease': max(0, min(100, flesch_score)),
            'avg_words_per_sentence': avg_words_per_sentence,
            'avg_syllables_per_word': avg_syllables_per_word
        }
    
    def _count_syllables(self, word: str) -> int:
        """
Simple syllable counting"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel
        
        # Handle special cases
        if word.endswith('e'):
            syllable_count -= 1
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _extract_image_metadata(self, image: Image.Image, image_path: Optional[str]) -> Dict[str, Any]:
        """Extract comprehensive image metadata"""
        metadata = {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'aspect_ratio': image.width / image.height if image.height > 0 else 0,
            'total_pixels': image.width * image.height
        }
        
        if image_path:
            metadata['file_path'] = image_path
            metadata['file_extension'] = image_path.split('.')[-1].lower() if '.' in image_path else None
        
        # Extract EXIF data if available
        try:
            exif_data = image.getexif()
            if exif_data:
                metadata['exif'] = dict(exif_data)
        except:
            pass
        
        return metadata
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """
Enhance image quality for better analysis"""
        try:
            # Brightness and contrast enhancement
            enhancer = ImageEnhance.Brightness(image)
            enhanced = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.05)
            
            # Sharpness enhancement
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Noise reduction
            enhanced = enhanced.filter(ImageFilter.MedianFilter(size=3))
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image
    
    def _extract_visual_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract visual features from image"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Color analysis
            color_features = self._analyze_colors(img_array)
            
            # Texture analysis
            texture_features = self._analyze_texture(img_array)
            
            # Edge analysis
            edge_features = self._analyze_edges(img_array)
            
            return {
                'colors': color_features,
                'texture': texture_features,
                'edges': edge_features
            }
            
        except Exception as e:
            logger.error(f"Visual feature extraction failed: {e}")
            return {}
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution in image"""
        # Calculate color histograms
        hist_r = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([image], [2], None, [256], [0, 256])
        
        # Color statistics
        mean_colors = np.mean(image, axis=(0, 1))
        std_colors = np.std(image, axis=(0, 1))
        
        # Dominant colors (simplified)
        pixels = image.reshape(-1, 3)
        dominant_color = np.mean(pixels, axis=0)
        
        return {
            'mean_rgb': mean_colors.tolist(),
            'std_rgb': std_colors.tolist(),
            'dominant_color': dominant_color.tolist(),
            'brightness': np.mean(mean_colors),
            'contrast': np.mean(std_colors)
        }
    
    def _analyze_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """
Analyze texture features in image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate texture measures
        # Local Binary Pattern (simplified)
        lbp_var = np.var(gray)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'texture_variance': float(lbp_var),
            'edge_density': float(edge_density),
            'smoothness': 1.0 - min(lbp_var / 10000, 1.0)
        }
    
    def _analyze_edges(self, image: np.ndarray) -> Dict[str, Any]:
        """
Analyze edge features in image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Edge statistics
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        edge_ratio = edge_pixels / total_pixels
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return {
            'edge_ratio': float(edge_ratio),
            'num_contours': len(contours),
            'total_edge_pixels': int(edge_pixels)
        }
    
    def _extract_audio_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Extract comprehensive audio features"""
        try:
            features = {}
            
            # Spectral features
            features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
            features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr)))
            features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr)))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # Zero crossing rate
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
            # RMS energy
            features['rms_energy'] = float(np.sqrt(np.mean(audio**2)))
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            features['tempo'] = float(tempo)
            
            # Pitch features
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = pitches[magnitudes > np.median(magnitudes)]
            if len(pitch_values) > 0:
                features['pitch_mean'] = float(np.mean(pitch_values[pitch_values > 0]))
                features['pitch_std'] = float(np.std(pitch_values[pitch_values > 0]))
            else:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    def _generate_spectrograms(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Generate different types of spectrograms"""
        try:
            spectrograms = {}
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr)
            spectrograms['mel_spectrogram'] = librosa.power_to_db(mel_spec)
            
            # STFT spectrogram
            stft = librosa.stft(audio)
            spectrograms['stft_spectrogram'] = np.abs(stft)
            
            # Chromagram
            spectrograms['chromagram'] = librosa.feature.chroma_stft(y=audio, sr=sr)
            
            return spectrograms
            
        except Exception as e:
            logger.error(f"Spectrogram generation failed: {e}")
            return {}
    
    def _analyze_audio_quality(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze audio quality metrics"""
        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio**2)
            noise_estimate = np.var(audio - np.convolve(audio, np.ones(5)/5, mode='same'))
            snr = 10 * np.log10(signal_power / max(noise_estimate, 1e-10))
            
            # Dynamic range
            dynamic_range = np.max(np.abs(audio)) - np.min(np.abs(audio))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio) > 0.95) / len(audio)
            
            return {
                'snr_db': float(snr),
                'dynamic_range': float(dynamic_range),
                'clipping_ratio': float(clipping_ratio),
                'peak_amplitude': float(np.max(np.abs(audio))),
                'rms_level': float(np.sqrt(np.mean(audio**2)))
            }
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            return {}

class ContentHasher:
    """
    Advanced content hashing for duplicate detection and content tracking
    
    Provides perceptual hashing for images, audio fingerprinting,
    and text similarity hashing.
    """
    
    @staticmethod
    def hash_text(text: str, algorithm: str = 'sha256') -> str:
        """
Generate hash for text content"""
        if not text:
            return ""
        
        # Normalize text for consistent hashing
        normalized_text = text.lower().strip()
        normalized_text = re.sub(r'\s+', ' ', normalized_text)
        
        if algorithm == 'sha256':
            return hashlib.sha256(normalized_text.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(normalized_text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def hash_image(image: Union[Image.Image, np.ndarray]) -> str:
        """Generate perceptual hash for image"""
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Resize to standard size
            image = image.resize((32, 32))
            image = image.convert('L')  # Convert to grayscale
            
            # Convert to numpy array
            pixels = np.array(image)
            
            # Calculate average
            avg = np.mean(pixels)
            
            # Generate hash
            hash_bits = pixels > avg
            hash_string = ''.join(['1' if bit else '0' for bit in hash_bits.flatten()])
            
            # Convert to hex
            hash_int = int(hash_string, 2)
            return hex(hash_int)[2:]
            
        except Exception as e:
            logger.error(f"Image hashing failed: {e}")
            return ""
    
    @staticmethod
    def hash_audio(audio: np.ndarray, sr: int) -> str:
        """Generate audio fingerprint hash"""
        try:
            # Extract spectral features
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=12)
            
            # Calculate hash based on MFCC features
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Normalize and discretize
            mfcc_norm = (mfcc_mean - np.min(mfcc_mean)) / (np.max(mfcc_mean) - np.min(mfcc_mean))
            mfcc_discrete = (mfcc_norm * 255).astype(np.uint8)
            
            # Generate hash
            hash_bytes = mfcc_discrete.tobytes()
            return hashlib.sha256(hash_bytes).hexdigest()
            
        except Exception as e:
            logger.error(f"Audio hashing failed: {e}")
            return ""

class ViolationReporter:
    """
    Advanced violation reporting and evidence collection system
    
    Generates comprehensive reports for content violations with
    detailed evidence, context, and recommendations.
    """
    
    def __init__(self):
        self.report_templates = {
            'toxicity': "Content contains toxic language with {confidence:.2%} confidence. Detected categories: {categories}",
            'nsfw': "Visual content contains explicit material with {confidence:.2%} confidence. Detected regions: {regions}",
            'violence': "Content depicts violent imagery with {confidence:.2%} confidence. Violence type: {violence_type}",
            'hate_speech': "Text contains hate speech targeting {target_group} with {confidence:.2%} confidence",
            'harassment': "Content demonstrates harassment patterns with {confidence:.2%} confidence",
            'spam': "Content identified as spam with {confidence:.2%} confidence. Spam indicators: {indicators}"
        }
    
    def generate_violation_report(self, violations: List[Dict[str, Any]], 
                                content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive violation report
        
        Args:
            violations: List of detected violations
            content_metadata: Metadata about the content
            
        Returns:
            Detailed violation report
        """
        report = {
            'report_id': self._generate_report_id(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content_metadata': content_metadata,
            'total_violations': len(violations),
            'severity_level': self._calculate_overall_severity(violations),
            'violations': [],
            'recommendations': [],
            'evidence': {}
        }
        
        for violation in violations:
            violation_report = {
                'type': violation.get('violation_type', 'unknown'),
                'confidence': violation.get('confidence', 0.0),
                'severity': violation.get('severity', 'low'),
                'description': self._generate_violation_description(violation),
                'evidence': violation.get('evidence', {}),
                'location': violation.get('location'),
                'context': violation.get('context')
            }
            
            report['violations'].append(violation_report)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(violations)
        
        # Collect evidence
        report['evidence'] = self._collect_evidence(violations, content_metadata)
        
        return report
    
    def _generate_report_id(self) -> str:
        """
Generate unique report ID"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"MOD_{timestamp}_{random_suffix}"
    
    def _calculate_overall_severity(self, violations: List[Dict[str, Any]]) -> str:
        """Calculate overall severity level"""
        if not violations:
            return 'none'
        
        severity_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4, 'extreme': 5}
        max_score = max(severity_scores.get(v.get('severity', 'low'), 1) for v in violations)
        
        for severity, score in severity_scores.items():
            if score == max_score:
                return severity
        
        return 'low'
    
    def _generate_violation_description(self, violation: Dict[str, Any]) -> str:
        """
Generate human-readable violation description"""
        violation_type = violation.get('violation_type', 'unknown')
        template = self.report_templates.get(violation_type, "Violation of type {type} detected with {confidence:.2%} confidence")
        
        return template.format(
            confidence=violation.get('confidence', 0.0),
            categories=violation.get('evidence', {}).get('detected_categories', []),
            regions=len(violation.get('evidence', {}).get('regions', [])),
            violence_type=violation.get('evidence', {}).get('violence_type', 'general'),
            target_group=violation.get('evidence', {}).get('target_group', 'unknown'),
            indicators=list(violation.get('evidence', {}).get('indicators', {}).keys()),
            type=violation_type
        )
    
    def _generate_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        violation_types = set(v.get('violation_type') for v in violations)
        
        if 'toxicity' in violation_types or 'hate_speech' in violation_types:
            recommendations.append("Content requires immediate review and likely removal")
            recommendations.append("Consider user education about community guidelines")
        
        if 'nsfw' in violation_types:
            recommendations.append("Apply age restriction or content warning")
            recommendations.append("Review content distribution settings")
        
        if 'violence' in violation_types:
            recommendations.append("Content should be removed or heavily restricted")
            recommendations.append("Monitor user for pattern of violent content")
        
        if len(violations) > 3:
            recommendations.append("Multiple violations detected - consider account review")
        
        return recommendations
    
    def _collect_evidence(self, violations: List[Dict[str, Any]], 
                         content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and organize evidence"""
        evidence = {
            'violation_count': len(violations),
            'confidence_scores': [v.get('confidence', 0.0) for v in violations],
            'violation_types': list(set(v.get('violation_type') for v in violations)),
            'content_features': content_metadata.get('features', {}),
            'processing_metadata': {
                'models_used': content_metadata.get('models_used', []),
                'processing_time': content_metadata.get('processing_time'),
                'content_type': content_metadata.get('content_type')
            }
        }
        
        return evidence
