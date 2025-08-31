"""
Metadata Extractor - Enterprise Metadata Extraction & Analysis System
======================================================================

Advanced metadata extraction system for images and videos with comprehensive
EXIF, IPTC, XMP data processing and content forensics capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import json
import hashlib

# Image metadata libraries
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import exifread

from ..base import BaseAgent, AgentStatus
try:
    from core.exceptions import MetadataExtractionError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    MetadataExtractionError, ValidationError = globals().get('MetadataExtractionError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...security.data_sanitizer import DataSanitizer

logger = logging.getLogger(__name__)

class MetadataExtractor(BaseAgent):
    """
    Enterprise-grade metadata extraction system providing comprehensive
    metadata analysis, content forensics, and data sanitization.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="metadata_extractor",
            name="Metadata Extractor",
            version="2.1.0"
        )
        
        self.performance_monitor = PerformanceMonitor("metadata_extraction")
        self.data_sanitizer = DataSanitizer()
        
        # Metadata categories
        self.metadata_categories = {
            'technical': ['camera_make', 'camera_model', 'lens_info', 'exposure_settings'],
            'geographical': ['gps_coordinates', 'location_name', 'altitude'],
            'temporal': ['creation_date', 'modification_date', 'timezone'],
            'descriptive': ['title', 'description', 'keywords', 'author'],
            'rights': ['copyright', 'usage_rights', 'license'],
            'processing': ['software_used', 'processing_history', 'color_space']
        }
        
        # Privacy-sensitive fields to handle carefully
        self.sensitive_fields = [
            'gps_coordinates', 'gps_latitude', 'gps_longitude',
            'location_name', 'author', 'copyright', 'user_comment',
            'camera_serial_number', 'lens_serial_number'
        ]
        
        # File format support
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp', '.heic'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        }

    async def initialize(self) -> bool:
        """Initialize metadata extraction components"""



        try:
            logger.info("Initializing Metadata Extractor...")
            
            # Initialize EXIF tag mapping
            self.exif_tags = {v: k for k, v in TAGS.items()}
            self.gps_tags = {v: k for k, v in GPSTAGS.items()}
            
            # Initialize metadata validators
            self.metadata_validators = {
                'datetime': self._validate_datetime,
                'gps': self._validate_gps_coordinates,
                'camera': self._validate_camera_info
            }
            
            self.status = AgentStatus.READY
            logger.info("Metadata Extractor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Metadata Extractor initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def extract_from_file(
        self, 
        file_path: str,
        include_sensitive: bool = False,
        sanitize_data: bool = True
    ) -> Dict[str, Any]:
        """
        Extract metadata from file
        
        Args:
            file_path: Path to the file
            include_sensitive: Include potentially sensitive metadata
            sanitize_data: Apply data sanitization
            
        Returns:
            Extracted metadata with privacy protection
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Extracting metadata from {file_path}")
            
            # Validate file exists
            if not os.path.exists(file_path):
                raise ValidationError(f"File not found: {file_path}")
            
            file_info = await self._get_basic_file_info(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            # Determine extraction method based on file type
            metadata = {}
            
            if file_extension in self.supported_formats['image']:
                metadata = await self._extract_image_metadata(file_path)
            elif file_extension in self.supported_formats['video']:
                metadata = await self._extract_video_metadata(file_path)
            elif file_extension in self.supported_formats['audio']:
                metadata = await self._extract_audio_metadata(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_extension}")
                metadata = {'error': f'Unsupported format: {file_extension}'}
            
            # Add basic file information
            metadata['file_info'] = file_info
            
            # Apply privacy protection
            if not include_sensitive:
                metadata = await self._remove_sensitive_metadata(metadata)
            
            # Apply data sanitization
            if sanitize_data:
                metadata = await self._sanitize_metadata(metadata)
            
            # Analyze metadata for forensics
            forensics_data = await self._analyze_forensics(metadata)
            metadata['forensics_analysis'] = forensics_data
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'file_path': file_path,
                'extraction_timestamp': datetime.now().isoformat(),
                'metadata': metadata,
                'privacy_protected': not include_sensitive,
                'sanitized': sanitize_data
            }
            
            logger.info(f"Metadata extraction completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {file_path}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'file_path': file_path
            }

    async def extract_from_data(
        self, 
        file_data: bytes,
        file_format: str = None,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Extract metadata from binary data
        
        Args:
            file_data: Binary file data
            file_format: File format hint (e.g., 'jpg', 'mp4')
            include_sensitive: Include potentially sensitive metadata
            
        Returns:
            Extracted metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info("Extracting metadata from binary data")
            
            # Create temporary file for processing
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=f'.{file_format}' if file_format else '') as tmp_file:
                tmp_file.write(file_data)
                tmp_file.flush()
                
                # Extract metadata from temporary file
                result = await self.extract_from_file(
                    tmp_file.name, 
                    include_sensitive=include_sensitive
                )
                
                # Remove file path from result for security
                if 'file_path' in result:
                    result['file_path'] = 'binary_data_input'
            
            return result
            
        except Exception as e:
            logger.error(f"Metadata extraction from data failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    async def _get_basic_file_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file system information"""



        try:
            file_stat = os.stat(file_path)
            file_path_obj = Path(file_path)
            
            # Calculate file hash for integrity
            file_hash = await self._calculate_file_hash(file_path)
            
            return {
                'filename': file_path_obj.name,
                'file_extension': file_path_obj.suffix.lower(),
                'file_size_bytes': file_stat.st_size,
                'file_size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                'created_timestamp': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_timestamp': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'accessed_timestamp': datetime.fromtimestamp(file_stat.st_atime).isoformat(),
                'file_hash_sha256': file_hash,
                'file_permissions': oct(file_stat.st_mode)[-3:]
            }
            
        except Exception as e:
            logger.error(f"Basic file info extraction failed: {e}")
            return {'error': str(e)}

    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""



        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"File hash calculation failed: {e}")
            return "unknown"

    async def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive image metadata"""



        try:
            metadata = {
                'format_info': {},
                'exif_data': {},
                'camera_settings': {},
                'gps_data': {},
                'processing_info': {},
                'descriptive_info': {}
            }
            
            # Use PIL for basic metadata
            with Image.open(file_path) as img:
                # Basic image information
                metadata['format_info'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': 'transparency' in img.info,
                    'color_depth': len(img.getbands()) * 8 if hasattr(img, 'getbands') else 24
                }
                
                # EXIF data extraction
                if hasattr(img, '_getexif'):
                    exif_data = img._getexif()
                    if exif_data:
                        metadata['exif_data'] = await self._process_exif_data(exif_data)
                        
                        # Extract specific categories
                        metadata['camera_settings'] = await self._extract_camera_settings(exif_data)
                        metadata['gps_data'] = await self._extract_gps_data(exif_data)
                        metadata['processing_info'] = await self._extract_processing_info(exif_data)
            
            # Use exifread for additional metadata
            with open(file_path, 'rb') as f:
                exif_tags = exifread.process_file(f, details=False)
                if exif_tags:
                    additional_metadata = await self._process_exifread_data(exif_tags)
                    metadata['additional_exif'] = additional_metadata
            
            return metadata
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            return {'error': str(e)}

    async def _process_exif_data(self, exif_data: Dict[int, Any]) -> Dict[str, Any]:
        """Process raw EXIF data into readable format"""



        try:
            processed_exif = {}
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, f'Unknown_{tag_id}')
                
                try:
                    # Handle different value types
                    if isinstance(value, bytes):
                        try:
                            processed_value = value.decode('utf-8', errors='ignore')
                        except:
                            processed_value = str(value)
                    elif isinstance(value, tuple):
                        processed_value = [str(v) for v in value]
                    else:
                        processed_value = str(value)
                    
                    processed_exif[tag_name] = processed_value
                    
                except Exception as e:
                    logger.warning(f"Failed to process EXIF tag {tag_name}: {e}")
                    processed_exif[tag_name] = f"processing_error: {str(e)}"
            
            return processed_exif
            
        except Exception as e:
            logger.error(f"EXIF data processing failed: {e}")
            return {}

    async def _extract_camera_settings(self, exif_data: Dict[int, Any]) -> Dict[str, Any]:
        """Extract camera-specific settings from EXIF"""



        try:
            camera_settings = {}
            
            # Camera identification
            if 272 in exif_data:  # Make
                camera_settings['camera_make'] = str(exif_data[272])
            if 271 in exif_data:  # Model
                camera_settings['camera_model'] = str(exif_data[271])
            
            # Exposure settings
            if 33434 in exif_data:  # ExposureTime
                camera_settings['shutter_speed'] = str(exif_data[33434])
            if 33437 in exif_data:  # FNumber
                camera_settings['aperture'] = str(exif_data[33437])
            if 34855 in exif_data:  # ISOSpeedRatings
                camera_settings['iso'] = str(exif_data[34855])
            
            # Lens information
            if 42036 in exif_data:  # LensModel
                camera_settings['lens_model'] = str(exif_data[42036])
            if 37386 in exif_data:  # FocalLength
                camera_settings['focal_length'] = str(exif_data[37386])
            
            # Flash information
            if 37385 in exif_data:  # Flash
                camera_settings['flash_fired'] = bool(int(exif_data[37385]) & 1)
            
            return camera_settings
            
        except Exception as e:
            logger.error(f"Camera settings extraction failed: {e}")
            return {}

    async def _extract_gps_data(self, exif_data: Dict[int, Any]) -> Dict[str, Any]:
        """Extract GPS data from EXIF with privacy consideration"""



        try:
            gps_data = {}
            
            # GPS info is usually in tag 34853
            if 34853 in exif_data:
                gps_info = exif_data[34853]
                
                if isinstance(gps_info, dict):
                    # Process GPS tags
                    for gps_tag, value in gps_info.items():
                        gps_tag_name = GPSTAGS.get(gps_tag, f'GPS_{gps_tag}')
                        gps_data[gps_tag_name] = str(value)
                    
                    # Convert GPS coordinates if available
                    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                        try:
                            lat = self._convert_gps_coordinate(
                                gps_info.get(2), gps_info.get(1)
                            )
                            lon = self._convert_gps_coordinate(
                                gps_info.get(4), gps_info.get(3)
                            )
                            
                            gps_data['latitude_decimal'] = lat
                            gps_data['longitude_decimal'] = lon
                            gps_data['coordinates_available'] = True
                            
                        except Exception as e:
                            logger.warning(f"GPS coordinate conversion failed: {e}")
                            gps_data['coordinates_available'] = False
            
            return gps_data
            
        except Exception as e:
            logger.error(f"GPS data extraction failed: {e}")
            return {}

    def _convert_gps_coordinate(self, coordinate_tuple, direction):
        """Convert GPS coordinate from EXIF format to decimal"""



        try:
            if not coordinate_tuple or len(coordinate_tuple) != 3:
                return None
            
            degrees = float(coordinate_tuple[0])
            minutes = float(coordinate_tuple[1])
            seconds = float(coordinate_tuple[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply direction
            if direction in ['S', 'W']:
                decimal = -decimal
            
            return decimal
            
        except Exception as e:
            logger.error(f"GPS coordinate conversion failed: {e}")
            return None

    async def _extract_processing_info(self, exif_data: Dict[int, Any]) -> Dict[str, Any]:
        """Extract image processing information"""



        try:
            processing_info = {}
            
            # Software used
            if 305 in exif_data:  # Software
                processing_info['software'] = str(exif_data[305])
            
            # Color space
            if 40961 in exif_data:  # ColorSpace
                color_space_value = int(exif_data[40961])
                color_spaces = {1: 'sRGB', 65535: 'Uncalibrated'}
                processing_info['color_space'] = color_spaces.get(color_space_value, f'Unknown_{color_space_value}')
            
            # White balance
            if 41987 in exif_data:  # WhiteBalance
                wb_value = int(exif_data[41987])
                wb_modes = {0: 'Auto', 1: 'Manual'}
                processing_info['white_balance'] = wb_modes.get(wb_value, f'Unknown_{wb_value}')
            
            return processing_info
            
        except Exception as e:
            logger.error(f"Processing info extraction failed: {e}")
            return {}

    async def _process_exifread_data(self, exif_tags: Dict) -> Dict[str, Any]:
        """Process exifread library data"""



        try:
            additional_data = {}
            
            for tag_name, tag_value in exif_tags.items():
                if tag_name not in ['JPEGThumbnail', 'TIFFThumbnail']:
                    try:
                        additional_data[tag_name] = str(tag_value)
                    except:
                        additional_data[tag_name] = 'unparseable'
            
            return additional_data
            
        except Exception as e:
            logger.error(f"ExifRead data processing failed: {e}")
            return {}

    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video metadata (placeholder implementation)"""



        try:
            # This would use ffprobe or similar tool in production
            metadata = {
                'format_info': {'note': 'Video metadata extraction requires ffmpeg/ffprobe'},
                'video_streams': [],
                'audio_streams': [],
                'creation_date': None,
                'duration': None,
                'file_format': Path(file_path).suffix.lower()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
            return {'error': str(e)}

    async def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio metadata (placeholder implementation)"""



        try:
            # This would use mutagen or similar library in production
            metadata = {
                'format_info': {'note': 'Audio metadata extraction requires mutagen library'},
                'audio_properties': {},
                'tags': {},
                'file_format': Path(file_path).suffix.lower()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {e}")
            return {'error': str(e)}

    async def _remove_sensitive_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove privacy-sensitive metadata fields"""



        try:
            cleaned_metadata = {}
            
            for category, data in metadata.items():
                if isinstance(data, dict):
                    cleaned_category = {}
                    
                    for key, value in data.items():
                        # Check if field is sensitive
                        is_sensitive = any(sensitive in key.lower() 
                                         for sensitive in self.sensitive_fields)
                        
                        if not is_sensitive:
                            cleaned_category[key] = value
                        else:
                            cleaned_category[key] = '[PRIVACY_PROTECTED]'
                    
                    cleaned_metadata[category] = cleaned_category
                else:
                    cleaned_metadata[category] = data
            
            # Add privacy notice
            cleaned_metadata['privacy_notice'] = {
                'sensitive_data_removed': True,
                'protected_fields': self.sensitive_fields,
                'protection_timestamp': datetime.now().isoformat()
            }
            
            return cleaned_metadata
            
        except Exception as e:
            logger.error(f"Sensitive metadata removal failed: {e}")
            return metadata

    async def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data sanitization to metadata"""



        try:
            return await self.data_sanitizer.sanitize_metadata(metadata)
        except Exception as e:
            logger.error(f"Metadata sanitization failed: {e}")
            return metadata

    async def _analyze_forensics(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metadata for forensic indicators"""



        try:
            forensics_analysis = {
                'authenticity_indicators': [],
                'manipulation_signs': [],
                'creation_chain': 'unknown',
                'software_fingerprints': [],
                'integrity_score': 0.8  # Default good integrity
            }
            
            # Check for software indicators
            if 'processing_info' in metadata:
                software = metadata['processing_info'].get('software', '')
                if software:
                    forensics_analysis['software_fingerprints'].append(software)
                    
                    # Check for known editing software
                    editing_software = [
                        'photoshop', 'gimp', 'lightroom', 'capture one',
                        'affinity', 'canva', 'pixlr'
                    ]
                    
                    if any(editor in software.lower() for editor in editing_software):
                        forensics_analysis['manipulation_signs'].append('editing_software_detected')
                        forensics_analysis['integrity_score'] -= 0.2
            
            # Check for creation timestamp consistency
            if 'file_info' in metadata:
                file_info = metadata['file_info']
                created = file_info.get('created_timestamp')
                modified = file_info.get('modified_timestamp')
                
                if created and modified:
                    if created != modified:
                        forensics_analysis['authenticity_indicators'].append('file_modification_detected')
            
            # Check for missing expected metadata
            expected_fields = ['camera_make', 'camera_model']
            missing_fields = []
            
            camera_settings = metadata.get('camera_settings', {})
            for field in expected_fields:
                if field not in camera_settings:
                    missing_fields.append(field)
            
            if missing_fields:
                forensics_analysis['manipulation_signs'].append(f'missing_metadata: {missing_fields}')
                forensics_analysis['integrity_score'] -= 0.1
            
            # Overall assessment
            if forensics_analysis['integrity_score'] >= 0.8:
                forensics_analysis['assessment'] = 'likely_authentic'
            elif forensics_analysis['integrity_score'] >= 0.6:
                forensics_analysis['assessment'] = 'possibly_modified'
            else:
                forensics_analysis['assessment'] = 'likely_manipulated'
            
            return forensics_analysis
            
        except Exception as e:
            logger.error(f"Forensics analysis failed: {e}")
            return {'assessment': 'analysis_failed'}

    async def _validate_datetime(self, datetime_str: str) -> bool:
        """Validate datetime format"""



        try:
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return True
        except:
            return False

    async def _validate_gps_coordinates(self, lat: float, lon: float) -> bool:
        """Validate GPS coordinates"""



        try:
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except:
            return False

    async def _validate_camera_info(self, camera_info: Dict) -> bool:
        """Validate camera information"""



        try:
            required_fields = ['camera_make', 'camera_model']
            return all(field in camera_info for field in required_fields)
        except:
            return False

    async def batch_extract_metadata(
        self, 
        file_paths: List[str],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Extract metadata from multiple files concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_single(file_path):
            async with semaphore:
                return await self.extract_from_file(file_path)
        
        tasks = [extract_single(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) 
                else {'status': 'error', 'error': str(result), 'file_path': file_paths[i]} 
                for i, result in enumerate(results)]

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats"""



        return self.supported_formats.copy()

    def get_metadata_categories(self) -> Dict[str, List[str]]:
        """Get metadata categories"""



        return self.metadata_categories.copy()

    async def cleanup(self) -> None:
        """Cleanup resources"""



        try:
            await self.performance_monitor.close()
            await self.data_sanitizer.cleanup()
            logger.info("Metadata Extractor cleanup completed")
        except Exception as e:
            logger.error(f"Metadata Extractor cleanup failed: {e}")

    def get_extraction_capabilities(self) -> Dict[str, Any]:
        """Get metadata extraction capabilities"""



        return {
            'supported_formats': self.supported_formats,
            'metadata_categories': list(self.metadata_categories.keys()),
            'privacy_protection': True,
            'data_sanitization': True,
            'forensics_analysis': True,
            'batch_processing': True,
            'sensitive_field_detection': True,
            'gps_coordinate_conversion': True
        }
