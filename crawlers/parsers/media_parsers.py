"""
Media Parsers Module
===================

Advanced media file parsers for audio, video, image, and document processing.
Provides specialized parsing capabilities for content fingerprinting and analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import io
import mimetypes
import zipfile
import tarfile
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, BinaryIO

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    from mutagen import File as MutagenFile
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Video processing imports
try:
    import cv2
    import ffmpeg
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

# Image processing imports
try:
    from PIL import Image, ImageStat, ExifTags
    import numpy as np
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False

# Document processing imports
try:
    import PyPDF2
    import python_docx
    DOCUMENT_AVAILABLE = True
except ImportError:
    DOCUMENT_AVAILABLE = False

from .exceptions import MediaParsingError, UnsupportedFormatError, ValidationError
from .parser_config import ParserConfig, MediaFormat


class BaseMediaParser(ABC):
    """Abstract base class for media parsers"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.media_config = config.media
    
    @abstractmethod
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse media file and extract metadata/content"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[MediaFormat]:
        """Get list of supported media formats"""
        pass
    
    def _validate_file_size(self, file_path: Union[str, Path, BinaryIO]) -> bool:
        """Validate file size against configuration limits"""



        try:
            if isinstance(file_path, (str, Path)):
                file_size = Path(file_path).stat().st_size
            else:
                # For file-like objects
                current_pos = file_path.tell()
                file_path.seek(0, 2)  # Seek to end
                file_size = file_path.tell()
                file_path.seek(current_pos)  # Reset position
            
            return file_size <= self.media_config.max_file_size
        except Exception:
            return False
    
    def _detect_format(self, file_path: Union[str, Path, BinaryIO]) -> Optional[str]:
        """Detect file format from extension or MIME type"""
        if isinstance(file_path, (str, Path)):
            mime_type, _ = mimetypes.guess_type(str(file_path))
            extension = Path(file_path).suffix.lower().lstrip('.')
            return extension or (mime_type.split('/')[-1] if mime_type else None)
        
        # For file-like objects, try to detect from content
        return None
    
    def _extract_basic_metadata(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Extract basic file metadata"""
        metadata = {
            'parsed_at': datetime.now(timezone.utc).isoformat(),
            'parser_type': self.__class__.__name__
        }
        
        if isinstance(file_path, (str, Path)):
            path = Path(file_path)
            stat = path.stat()
            
            metadata.update({
                'filename': path.name,
                'file_size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                'format': self._detect_format(file_path)
            })
        
        return metadata


class AudioParser(BaseMediaParser):
    """Audio file parser with advanced analysis capabilities"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        if not AUDIO_AVAILABLE:
            raise ImportError("Audio processing dependencies not available")
    
    def get_supported_formats(self) -> List[MediaFormat]:
        return [
            MediaFormat.MP3, MediaFormat.WAV, MediaFormat.FLAC,
            MediaFormat.AAC, MediaFormat.OGG, MediaFormat.M4A
        ]
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse audio file and extract comprehensive metadata"""
        if not self._validate_file_size(file_path):
            raise MediaParsingError(
                "File size exceeds maximum limit",
                media_type="audio",
                file_size=Path(file_path).stat().st_size if isinstance(file_path, (str, Path)) else None,
                parser_type="AudioParser"
            )
        
        format_type = self._detect_format(file_path)
        if format_type and MediaFormat(format_type) not in self.get_supported_formats():
            raise UnsupportedFormatError(
                format_type, 
                [f.value for f in self.get_supported_formats()],
                parser_type="AudioParser"
            )
        
        try:
            # Extract basic metadata
            metadata = self._extract_basic_metadata(file_path)
            
            # Extract audio-specific metadata
            metadata.update(await self._extract_audio_metadata(file_path))
            
            # Perform audio analysis
            if kwargs.get('analyze_content', True):
                metadata.update(await self._analyze_audio_content(file_path))
            
            # Generate fingerprint if requested
            if kwargs.get('generate_fingerprint', False):
                metadata['fingerprint'] = await self._generate_audio_fingerprint(file_path)
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(
                f"Audio parsing failed: {str(e)}",
                media_type="audio",
                parser_type="AudioParser"
            )
    
    async def _extract_audio_metadata(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Extract audio metadata using mutagen"""



        try:
            if isinstance(file_path, (str, Path)):
                audio_file = MutagenFile(str(file_path))
            else:
                # For file-like objects, need to save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file_path.read())
                    audio_file = MutagenFile(tmp.name)
            
            if audio_file is None:
                return {}
            
            metadata = {
                'duration': getattr(audio_file.info, 'length', 0),
                'bitrate': getattr(audio_file.info, 'bitrate', 0),
                'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
                'channels': getattr(audio_file.info, 'channels', 0),
            }
            
            # Extract tags
            tags = {}
            if audio_file.tags:
                tag_mapping = {
                    'TIT2': 'title',
                    'TPE1': 'artist',
                    'TALB': 'album',
                    'TDRC': 'year',
                    'TCON': 'genre',
                    'TPE2': 'album_artist',
                    'TRCK': 'track_number'
                }
                
                for tag_id, tag_name in tag_mapping.items():
                    if tag_id in audio_file.tags:
                        tags[tag_name] = str(audio_file.tags[tag_id][0])
            
            metadata['tags'] = tags
            return metadata
            
        except Exception as e:
            return {'metadata_error': str(e)}
    
    async def _analyze_audio_content(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Analyze audio content using librosa"""



        try:
            # Load audio file
            if isinstance(file_path, (str, Path)):
                y, sr = librosa.load(str(file_path), sr=self.media_config.audio_sample_rate)
            else:
                # For file-like objects
                y, sr = librosa.load(file_path, sr=self.media_config.audio_sample_rate)
            
            # Basic audio analysis
            analysis = {
                'sample_rate': sr,
                'duration_seconds': len(y) / sr,
                'rms_energy': float(np.mean(librosa.feature.rms(y=y))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
            }
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            
            analysis.update({
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_rolloff_std': float(np.std(spectral_rolloff)),
            })
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                analysis[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
                analysis[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            analysis['tempo'] = float(tempo)
            
            # Key detection (simplified)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            analysis['key_profile'] = chroma.mean(axis=1).tolist()
            
            return {'audio_analysis': analysis}
            
        except Exception as e:
            return {'analysis_error': str(e)}
    
    async def _generate_audio_fingerprint(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Generate audio fingerprint for content identification"""



        try:
            # Load audio for fingerprinting
            if isinstance(file_path, (str, Path)):
                y, sr = librosa.load(str(file_path), sr=self.config.fingerprint.audio_sample_rate)
            else:
                y, sr = librosa.load(file_path, sr=self.config.fingerprint.audio_sample_rate)
            
            # Limit duration for fingerprinting
            max_samples = self.config.fingerprint.audio_duration_limit * sr
            if len(y) > max_samples:
                y = y[:max_samples]
            
            # Generate chromagram for fingerprinting
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=512)
            
            # Create hash from chromagram
            fingerprint_hash = hash(chroma.tobytes())
            
            return {
                'fingerprint_hash': str(fingerprint_hash),
                'duration_fingerprinted': len(y) / sr,
                'fingerprint_algorithm': 'chromagram_hash'
            }
            
        except Exception as e:
            return {'fingerprint_error': str(e)}


class VideoParser(BaseMediaParser):
    """Video file parser with frame analysis capabilities"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        if not VIDEO_AVAILABLE:
            raise ImportError("Video processing dependencies not available")
    
    def get_supported_formats(self) -> List[MediaFormat]:
        return [
            MediaFormat.MP4, MediaFormat.AVI, MediaFormat.MOV,
            MediaFormat.MKV, MediaFormat.WEBM, MediaFormat.FLV
        ]
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse video file and extract metadata"""
        if not self._validate_file_size(file_path):
            raise MediaParsingError(
                "File size exceeds maximum limit",
                media_type="video",
                parser_type="VideoParser"
            )
        
        try:
            metadata = self._extract_basic_metadata(file_path)
            metadata.update(await self._extract_video_metadata(file_path))
            
            if kwargs.get('analyze_frames', True):
                metadata.update(await self._analyze_video_frames(file_path))
            
            if kwargs.get('generate_fingerprint', False):
                metadata['fingerprint'] = await self._generate_video_fingerprint(file_path)
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(
                f"Video parsing failed: {str(e)}",
                media_type="video",
                parser_type="VideoParser"
            )
    
    async def _extract_video_metadata(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""



        try:
            if isinstance(file_path, (str, Path)):
                cap = cv2.VideoCapture(str(file_path))
            else:
                # For file-like objects, save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file_path.read())
                    cap = cv2.VideoCapture(tmp.name)
            
            if not cap.isOpened():
                return {'metadata_error': 'Could not open video file'}
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            metadata = {
                'duration_seconds': frame_count / fps if fps > 0 else 0,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'resolution': f"{width}x{height}",
                'aspect_ratio': width / height if height > 0 else 0
            }
            
            # Get codec information
            fourcc = cap.get(cv2.CAP_PROP_FOURCC)
            metadata['codec'] = ''.join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
            
            cap.release()
            return metadata
            
        except Exception as e:
            return {'metadata_error': str(e)}
    
    async def _analyze_video_frames(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Analyze video frames for content insights"""



        try:
            if isinstance(file_path, (str, Path)):
                cap = cv2.VideoCapture(str(file_path))
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file_path.read())
                    cap = cv2.VideoCapture(tmp.name)
            
            if not cap.isOpened():
                return {'analysis_error': 'Could not open video for analysis'}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames for analysis
            frame_indices = np.linspace(0, frame_count - 1, min(10, frame_count), dtype=int)
            
            brightness_values = []
            contrast_values = []
            dominant_colors = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Calculate brightness
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # Calculate contrast
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
                    
                    # Get dominant color
                    pixels = frame_rgb.reshape(-1, 3)
                    dominant_color = np.mean(pixels, axis=0)
                    dominant_colors.append(dominant_color.tolist())
            
            cap.release()
            
            return {
                'frame_analysis': {
                    'average_brightness': float(np.mean(brightness_values)) if brightness_values else 0,
                    'brightness_std': float(np.std(brightness_values)) if brightness_values else 0,
                    'average_contrast': float(np.mean(contrast_values)) if contrast_values else 0,
                    'contrast_std': float(np.std(contrast_values)) if contrast_values else 0,
                    'dominant_colors': dominant_colors,
                    'frames_analyzed': len(frame_indices)
                }
            }
            
        except Exception as e:
            return {'analysis_error': str(e)}
    
    async def _generate_video_fingerprint(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Generate video fingerprint for content identification"""



        try:
            if isinstance(file_path, (str, Path)):
                cap = cv2.VideoCapture(str(file_path))
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file_path.read())
                    cap = cv2.VideoCapture(tmp.name)
            
            frame_hashes = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames for fingerprinting
            frame_interval = self.config.fingerprint.video_frame_interval
            frame_indices = range(0, frame_count, frame_interval)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Resize frame for consistent hashing
                    frame_resized = cv2.resize(frame, (64, 64))
                    
                    # Convert to grayscale and calculate hash
                    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
                    frame_hash = hash(gray.tobytes())
                    frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Create overall fingerprint
            fingerprint_hash = hash(tuple(frame_hashes))
            
            return {
                'fingerprint_hash': str(fingerprint_hash),
                'frame_hashes': [str(h) for h in frame_hashes],
                'frames_processed': len(frame_hashes),
                'fingerprint_algorithm': 'frame_hash_sequence'
            }
            
        except Exception as e:
            return {'fingerprint_error': str(e)}


class ImageParser(BaseMediaParser):
    """Image file parser with computer vision analysis"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        if not IMAGE_AVAILABLE:
            raise ImportError("Image processing dependencies not available")
    
    def get_supported_formats(self) -> List[MediaFormat]:
        return [
            MediaFormat.JPEG, MediaFormat.JPG, MediaFormat.PNG,
            MediaFormat.WEBP, MediaFormat.GIF, MediaFormat.BMP, MediaFormat.SVG
        ]
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse image file and extract metadata"""
        if not self._validate_file_size(file_path):
            raise MediaParsingError(
                "File size exceeds maximum limit",
                media_type="image",
                parser_type="ImageParser"
            )
        
        try:
            metadata = self._extract_basic_metadata(file_path)
            metadata.update(await self._extract_image_metadata(file_path))
            
            if kwargs.get('analyze_content', True):
                metadata.update(await self._analyze_image_content(file_path))
            
            if kwargs.get('generate_fingerprint', False):
                metadata['fingerprint'] = await self._generate_image_fingerprint(file_path)
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(
                f"Image parsing failed: {str(e)}",
                media_type="image",
                parser_type="ImageParser"
            )
    
    async def _extract_image_metadata(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Extract image metadata including EXIF data"""



        try:
            if isinstance(file_path, (str, Path)):
                image = Image.open(file_path)
            else:
                image = Image.open(file_path)
            
            metadata = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format,
                'has_transparency': 'transparency' in image.info
            }
            
            # Extract EXIF data
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
            
            metadata['exif'] = exif_data
            return metadata
            
        except Exception as e:
            return {'metadata_error': str(e)}
    
    async def _analyze_image_content(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Analyze image content for visual properties"""



        try:
            if isinstance(file_path, (str, Path)):
                image = Image.open(file_path)
            else:
                image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Calculate image statistics
            stat = ImageStat.Stat(image)
            
            analysis = {
                'mean_rgb': stat.mean,
                'median_rgb': stat.median,
                'stddev_rgb': stat.stddev,
                'extrema_rgb': stat.extrema
            }
            
            # Calculate dominant colors
            image_array = np.array(image)
            pixels = image_array.reshape(-1, 3)
            
            # Get dominant color
            dominant_color = np.mean(pixels, axis=0)
            analysis['dominant_color'] = dominant_color.tolist()
            
            # Calculate color diversity
            unique_colors = len(np.unique(pixels.view(np.dtype((np.void, pixels.dtype.itemsize * pixels.shape[1])))))
            analysis['unique_colors'] = unique_colors
            
            # Calculate brightness and contrast
            gray = image.convert('L')
            gray_array = np.array(gray)
            analysis['brightness'] = float(np.mean(gray_array))
            analysis['contrast'] = float(np.std(gray_array))
            
            return {'image_analysis': analysis}
            
        except Exception as e:
            return {'analysis_error': str(e)}
    
    async def _generate_image_fingerprint(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Generate image fingerprint for content identification"""



        try:
            if isinstance(file_path, (str, Path)):
                image = Image.open(file_path)
            else:
                image = Image.open(file_path)
            
            # Resize to standard size for fingerprinting
            size = self.config.fingerprint.image_resize_dimensions
            image_resized = image.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to grayscale
            gray = image_resized.convert('L')
            
            # Calculate perceptual hash
            image_array = np.array(gray)
            fingerprint_hash = hash(image_array.tobytes())
            
            # Calculate average hash
            avg = np.mean(image_array)
            binary_str = ''.join(['1' if pixel > avg else '0' for pixel in image_array.flatten()])
            average_hash = hash(binary_str)
            
            return {
                'fingerprint_hash': str(fingerprint_hash),
                'average_hash': str(average_hash),
                'fingerprint_algorithm': 'perceptual_hash',
                'resize_dimensions': size
            }
            
        except Exception as e:
            return {'fingerprint_error': str(e)}


class TextParser(BaseMediaParser):
    """Text file parser with content analysis"""
    
    def get_supported_formats(self) -> List[MediaFormat]:
        return [
            MediaFormat.TXT, MediaFormat.MD, MediaFormat.HTML,
            MediaFormat.JSON, MediaFormat.XML, MediaFormat.CSV
        ]
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse text file and extract content"""



        try:
            metadata = self._extract_basic_metadata(file_path)
            
            # Read text content
            if isinstance(file_path, (str, Path)):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                content = file_path.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
            
            metadata.update(await self._analyze_text_content(content))
            
            if kwargs.get('generate_fingerprint', False):
                metadata['fingerprint'] = await self._generate_text_fingerprint(content)
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(
                f"Text parsing failed: {str(e)}",
                media_type="text",
                parser_type="TextParser"
            )
    
    async def _analyze_text_content(self, content: str) -> Dict[str, Any]:
        """Analyze text content"""
        analysis = {
            'character_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.splitlines()),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
        }
        
        # Basic linguistic analysis
        words = content.lower().split()
        if words:
            analysis['average_word_length'] = sum(len(word) for word in words) / len(words)
            analysis['unique_words'] = len(set(words))
            analysis['vocabulary_diversity'] = len(set(words)) / len(words)
        
        return {'text_analysis': analysis}
    
    async def _generate_text_fingerprint(self, content: str) -> Dict[str, Any]:
        """Generate text fingerprint"""
        # Simple hash-based fingerprint
        fingerprint_hash = hash(content)
        
        # Character frequency fingerprint
        char_freq = {}
        for char in content.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        freq_hash = hash(tuple(sorted(char_freq.items())))
        
        return {
            'fingerprint_hash': str(fingerprint_hash),
            'frequency_hash': str(freq_hash),
            'fingerprint_algorithm': 'text_hash'
        }


class DocumentParser(BaseMediaParser):
    """Document file parser (PDF, DOCX, etc.)"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        if not DOCUMENT_AVAILABLE:
            raise ImportError("Document processing dependencies not available")
    
    def get_supported_formats(self) -> List[str]:
        return ['pdf', 'docx', 'doc']
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse document file"""
        format_type = self._detect_format(file_path)
        
        if format_type == 'pdf':
            return await self._parse_pdf(file_path)
        elif format_type in ['docx', 'doc']:
            return await self._parse_docx(file_path)
        else:
            raise UnsupportedFormatError(format_type, self.get_supported_formats())
    
    async def _parse_pdf(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Parse PDF document"""



        try:
            if isinstance(file_path, (str, Path)):
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    page_count = len(reader.pages)
                    text_content = ''
                    for page in reader.pages:
                        text_content += page.extract_text()
            else:
                reader = PyPDF2.PdfReader(file_path)
                page_count = len(reader.pages)
                text_content = ''
                for page in reader.pages:
                    text_content += page.extract_text()
            
            metadata = self._extract_basic_metadata(file_path)
            metadata.update({
                'page_count': page_count,
                'text_content': text_content,
                'character_count': len(text_content),
                'word_count': len(text_content.split())
            })
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(f"PDF parsing failed: {str(e)}", parser_type="DocumentParser")
    
    async def _parse_docx(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Parse DOCX document"""



        try:
            if isinstance(file_path, (str, Path)):
                doc = python_docx.Document(file_path)
            else:
                doc = python_docx.Document(file_path)
            
            text_content = ''
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + '\n'
            
            metadata = self._extract_basic_metadata(file_path)
            metadata.update({
                'paragraph_count': len(doc.paragraphs),
                'text_content': text_content,
                'character_count': len(text_content),
                'word_count': len(text_content.split())
            })
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(f"DOCX parsing failed: {str(e)}", parser_type="DocumentParser")


class ArchiveParser(BaseMediaParser):
    """Archive file parser (ZIP, TAR, etc.)"""
    
    def get_supported_formats(self) -> List[str]:
        return ['zip', 'tar', 'tar.gz', 'tar.bz2']
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse archive file"""
        format_type = self._detect_format(file_path)
        
        try:
            metadata = self._extract_basic_metadata(file_path)
            
            if format_type == 'zip':
                metadata.update(await self._parse_zip(file_path))
            elif format_type.startswith('tar'):
                metadata.update(await self._parse_tar(file_path))
            
            return metadata
            
        except Exception as e:
            raise MediaParsingError(f"Archive parsing failed: {str(e)}", parser_type="ArchiveParser")
    
    async def _parse_zip(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Parse ZIP archive"""
        if isinstance(file_path, (str, Path)):
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                total_size = sum(zip_file.getinfo(name).file_size for name in file_list)
        else:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                total_size = sum(zip_file.getinfo(name).file_size for name in file_list)
        
        return {
            'file_count': len(file_list),
            'total_uncompressed_size': total_size,
            'file_list': file_list[:100]  # Limit to first 100 files
        }
    
    async def _parse_tar(self, file_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Parse TAR archive"""
        if isinstance(file_path, (str, Path)):
            with tarfile.open(file_path, 'r') as tar_file:
                file_list = tar_file.getnames()
                total_size = sum(member.size for member in tar_file.getmembers() if member.isfile())
        else:
            with tarfile.open(fileobj=file_path, mode='r') as tar_file:
                file_list = tar_file.getnames()
                total_size = sum(member.size for member in tar_file.getmembers() if member.isfile())
        
        return {
            'file_count': len(file_list),
            'total_uncompressed_size': total_size,
            'file_list': file_list[:100]  # Limit to first 100 files
        }


class StreamParser(BaseMediaParser):
    """Stream parser for real-time content"""
    
    def get_supported_formats(self) -> List[str]:
        return ['m3u8', 'mpd', 'stream']
    
    async def parse(self, file_path: Union[str, Path, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Parse streaming manifest or live stream"""
        # Implementation for streaming content parsing
        # This would handle HLS, DASH, and other streaming formats
        return {
            'stream_type': 'live',
            'parsed_at': datetime.now(timezone.utc).isoformat()
        }
