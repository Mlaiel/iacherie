"""Metadata Transformer - Professional metadata processing for IA Influencer Agent Platform
========================================================================================

Advanced metadata extraction, transformation, and standardization capabilities
for creators' content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom
import yaml
import hashlib
from datetime import datetime, timezone

try:
    from exifread import process_file
    import mutagen
    from mutagen.id3 import ID3
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    METADATA_LIBS_AVAILABLE = True
except ImportError:
    METADATA_LIBS_AVAILABLE = False
    logging.warning("Metadata processing libraries not available. Some features may be limited.")

logger = logging.getLogger(__name__)


class MetadataFormat(Enum):
    """Supported metadata formats."""

    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    RDF = "rdf"
    DUBLIN_CORE = "dc"


class MetadataStandard(Enum):
    """Metadata standards."""

    DUBLIN_CORE = "dublin_core"
    EXIF = "exif"
    ID3 = "id3"
    IPTC = "iptc"
    XMP = "xmp"
    CUSTOM = "custom"


@dataclass
class MetadataSchema:
    """Metadata schema definition."""
    title: Optional[str] = None
    creator: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    contributor: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None
    format: Optional[str] = None
    identifier: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    relation: Optional[str] = None
    coverage: Optional[str] = None
    rights: Optional[str] = None
    
    # Technical metadata
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    content_type: Optional[str] = None
    encoding: Optional[str] = None
    
    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class MetadataSettings:
    """
Metadata processing settings."""
    format: MetadataFormat = MetadataFormat.JSON
    standard: MetadataStandard = MetadataStandard.DUBLIN_CORE
    include_technical: bool = True
    include_descriptive: bool = True
    include_administrative: bool = True
    include_custom: bool = True
    normalize_dates: bool = True
    normalize_encoding: bool = True
    extract_embedded: bool = True
    validate_schema: bool = True
    preserve_original: bool = True


class MetadataTransformer:
    """
    Professional metadata transformation engine for the IA Influencer Agent Platform.
    
    Provides advanced metadata extraction, transformation, and standardization
    capabilities optimized for creator content workflows.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize metadata transformer.
        
        Args:
            config: Configuration options
            temp_dir: Temporary directory for processing
        """
        self.config = config or {}
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "metadata_transform"
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Dublin Core mapping
        self.dublin_core_mapping = {
            'title': ['title', 'TIT2', 'TIT1', 'TITLE'],
            'creator': ['artist', 'TPE1', 'TPE2', 'ARTIST', 'ALBUMARTIST'],
            'subject': ['genre', 'TCON', 'GENRE'],
            'description': ['comment', 'COMM', 'DESCRIPTION'],
            'publisher': ['publisher', 'TPUB', 'LABEL'],
            'date': ['date', 'TDRC', 'YEAR', 'DATE'],
            'format': ['format', 'mime_type'],
            'identifier': ['musicbrainz_trackid', 'UFID'],
            'language': ['language', 'TLAN'],
            'rights': ['copyright', 'TCOP', 'COPYRIGHT']
        }
        
        logger.info("MetadataTransformer initialized")
    
    async def transform(self, request) -> Any:
        """
        Transform metadata based on request configuration.
        
        Args:
            request: Transformation request with metadata settings
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            # Parse request
            input_path = Path(request.input_path)
            settings = self._parse_metadata_settings(request)
            
            # Generate output path
            output_path = self._generate_output_path(input_path, settings, request.output_path)
            
            # Extract metadata
            metadata = await self.extract_metadata(str(input_path))
            
            # Transform metadata
            transformed_metadata = await self._transform_metadata(metadata, settings)
            
            # Save transformed metadata
            await self._save_metadata(transformed_metadata, output_path, settings)
            
            # Calculate metrics
            input_size = input_path.stat().st_size if input_path.exists() else 0
            output_size = output_path.stat().st_size if output_path.exists() else 0
            
            return type('TransformationResult', (), {
                'success': True,
                'output_path': str(output_path),
                'input_size': input_size,
                'output_size': output_size,
                'metadata': {
                    'extracted': metadata,
                    'transformed': transformed_metadata,
                    'settings': asdict(settings)
                },
                'processing_time': time.time() - start_time
            })()
            
        except Exception as e:
            logger.error(f"Metadata transformation failed: {str(e)}")
            return type('TransformationResult', (), {
                'success': False,
                'error_message': str(e),
                'processing_time': time.time() - start_time
            })()
    
    async def extract_metadata(
        self,
        file_path: str,
        include_embedded: bool = True
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from file.
        
        Args:
            file_path: File path to extract metadata from
            include_embedded: Include embedded metadata (EXIF, ID3, etc.)
            
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {}
            
            metadata = {}
            
            # Basic file metadata
            stat_info = file_path_obj.stat()
            metadata['file'] = {
                'name': file_path_obj.name,
                'size': stat_info.st_size,
                'creation_time': datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc).isoformat(),
                'modification_time': datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc).isoformat(),
                'access_time': datetime.fromtimestamp(stat_info.st_atime, tz=timezone.utc).isoformat(),
                'extension': file_path_obj.suffix.lower(),
                'mime_type': self._get_mime_type(file_path_obj)
            }
            
            # File hash
            metadata['file']['hash_md5'] = await self._calculate_file_hash(file_path_obj, 'md5')
            metadata['file']['hash_sha256'] = await self._calculate_file_hash(file_path_obj, 'sha256')
            
            # Extract embedded metadata
            if include_embedded and METADATA_LIBS_AVAILABLE:
                # Audio metadata
                if file_path_obj.suffix.lower() in ['.mp3', '.flac', '.m4a', '.ogg', '.wav']:
                    metadata['audio'] = await self._extract_audio_metadata(file_path_obj)
                
                # Image metadata (EXIF)
                elif file_path_obj.suffix.lower() in ['.jpg', '.jpeg', '.tiff', '.tif']:
                    metadata['image'] = await self._extract_image_metadata(file_path_obj)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {}
    
    async def standardize_metadata(
        self,
        metadata: Dict[str, Any],
        standard: MetadataStandard = MetadataStandard.DUBLIN_CORE
    ) -> MetadataSchema:
        """
        Standardize metadata to a specific schema.
        
        Args:
            metadata: Raw metadata dictionary
            standard: Target metadata standard
            
        Returns:
            Standardized metadata schema
        """
        try:
            schema = MetadataSchema()
            
            if standard == MetadataStandard.DUBLIN_CORE:
                schema = await self._map_to_dublin_core(metadata)
            elif standard == MetadataStandard.EXIF:
                schema = await self._map_to_exif(metadata)
            elif standard == MetadataStandard.ID3:
                schema = await self._map_to_id3(metadata)
            
            # Add technical metadata
            if 'file' in metadata:
                file_info = metadata['file']
                schema.file_size = file_info.get('size')
                schema.file_hash = file_info.get('hash_md5')
                schema.creation_date = file_info.get('creation_time')
                schema.modification_date = file_info.get('modification_time')
                schema.content_type = file_info.get('mime_type')
                schema.format = file_info.get('extension')
            
            return schema
            
        except Exception as e:
            logger.error(f"Metadata standardization failed: {str(e)}")
            return MetadataSchema()
    
    async def validate_metadata(
        self,
        metadata: Union[Dict[str, Any], MetadataSchema],
        schema_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate metadata against schema requirements.
        
        Args:
            metadata: Metadata to validate
            schema_requirements: Validation requirements
            
        Returns:
            Validation results
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'completeness_score': 0.0
            }
            
            # Convert to dict if MetadataSchema
            if isinstance(metadata, MetadataSchema):
                metadata_dict = asdict(metadata)
            else:
                metadata_dict = metadata
            
            # Default requirements for Dublin Core
            requirements = schema_requirements or {
                'required_fields': ['title', 'creator', 'date'],
                'recommended_fields': ['description', 'subject', 'format'],
                'field_types': {
                    'title': str,
                    'creator': str,
                    'date': str,
                    'file_size': int
                }
            }
            
            # Check required fields
            for field in requirements.get('required_fields', []):
                if not metadata_dict.get(field):
                    validation_result['errors'].append(f"Required field '{field}' is missing")
                    validation_result['valid'] = False
            
            # Check recommended fields
            for field in requirements.get('recommended_fields', []):
                if not metadata_dict.get(field):
                    validation_result['warnings'].append(f"Recommended field '{field}' is missing")
            
            # Check field types
            for field, expected_type in requirements.get('field_types', {}).items():
                value = metadata_dict.get(field)
                if value is not None and not isinstance(value, expected_type):
                    validation_result['errors'].append(
                        f"Field '{field}' has incorrect type. Expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                    validation_result['valid'] = False
            
            # Calculate completeness score
            total_fields = len(requirements.get('required_fields', [])) + len(requirements.get('recommended_fields', []))
            filled_fields = sum(1 for field in requirements.get('required_fields', []) + requirements.get('recommended_fields', []) 
                              if metadata_dict.get(field))
            
            if total_fields > 0:
                validation_result['completeness_score'] = filled_fields / total_fields
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Metadata validation failed: {str(e)}")
            return {'valid': False, 'errors': [str(e)], 'warnings': [], 'completeness_score': 0.0}
    
    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio metadata using mutagen."""
        try:
            audio_file = mutagen.File(str(file_path))
            if not audio_file:
                return {}
            
            metadata = {}
            
            # Common audio metadata
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata['duration'] = getattr(info, 'length', 0)
                metadata['bitrate'] = getattr(info, 'bitrate', 0)
                metadata['sample_rate'] = getattr(info, 'sample_rate', 0)
                metadata['channels'] = getattr(info, 'channels', 0)
            
            # Extract tags
            if audio_file.tags:
                tags = {}
                for key, value in audio_file.tags.items():
                    if isinstance(value, list):
                        value = value[0] if value else None
                    tags[key] = str(value) if value else None
                metadata['tags'] = tags
            
            return metadata
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata (EXIF)."""
        try:
            metadata = {}
            
            with open(file_path, 'rb') as f:
                exif_tags = process_file(f, details=False)
                
                if exif_tags:
                    exif_data = {}
                    for tag, value in exif_tags.items():
                        exif_data[str(tag)] = str(value)
                    metadata['exif'] = exif_data
            
            return metadata
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {str(e)}")
            return {}
    
    async def _map_to_dublin_core(self, metadata: Dict[str, Any]) -> MetadataSchema:
        """Map metadata to Dublin Core schema."""
        schema = MetadataSchema()
        
        try:
            # Map audio metadata if available
            if 'audio' in metadata and 'tags' in metadata['audio']:
                tags = metadata['audio']['tags']
                
                for dc_field, tag_names in self.dublin_core_mapping.items():
                    for tag_name in tag_names:
                        if tag_name in tags and tags[tag_name]:
                            setattr(schema, dc_field, tags[tag_name])
                            break
            
            # Map file metadata
            if 'file' in metadata:
                file_info = metadata['file']
                if not schema.format:
                    schema.format = file_info.get('mime_type')
                if not schema.identifier:
                    schema.identifier = file_info.get('hash_md5')
                if not schema.date:
                    schema.date = file_info.get('creation_time')
            
            return schema
            
        except Exception as e:
            logger.error(f"Dublin Core mapping failed: {str(e)}")
            return schema
    
    async def _map_to_exif(self, metadata: Dict[str, Any]) -> MetadataSchema:
        """Map metadata to EXIF-based schema."""
        schema = MetadataSchema()
        
        try:
            if 'image' in metadata and 'exif' in metadata['image']:
                exif_data = metadata['image']['exif']
                
                # Map common EXIF tags
                exif_mapping = {
                    'title': ['Image ImageDescription', 'Image DocumentName'],
                    'creator': ['Image Artist', 'Image Copyright'],
                    'date': ['Image DateTime', 'EXIF DateTimeOriginal'],
                    'description': ['Image ImageDescription'],
                }
                
                for dc_field, exif_tags in exif_mapping.items():
                    for exif_tag in exif_tags:
                        if exif_tag in exif_data:
                            setattr(schema, dc_field, exif_data[exif_tag])
                            break
            
            return schema
            
        except Exception as e:
            logger.error(f"EXIF mapping failed: {str(e)}")
            return schema
    
    async def _map_to_id3(self, metadata: Dict[str, Any]) -> MetadataSchema:
        """Map metadata to ID3-based schema."""
        schema = MetadataSchema()
        
        try:
            if 'audio' in metadata and 'tags' in metadata['audio']:
                tags = metadata['audio']['tags']
                
                # ID3 tag mapping
                id3_mapping = {
                    'title': ['TIT2', 'TIT1'],
                    'creator': ['TPE1', 'TPE2'],
                    'subject': ['TCON'],
                    'description': ['COMM::eng'],
                    'date': ['TDRC', 'TYER'],
                    'publisher': ['TPUB'],
                    'rights': ['TCOP']
                }
                
                for dc_field, id3_tags in id3_mapping.items():
                    for id3_tag in id3_tags:
                        if id3_tag in tags:
                            setattr(schema, dc_field, tags[id3_tag])
                            break
            
            return schema
            
        except Exception as e:
            logger.error(f"ID3 mapping failed: {str(e)}")
            return schema
    
    async def _transform_metadata(
        self,
        metadata: Dict[str, Any],
        settings: MetadataSettings
    ) -> Union[Dict[str, Any], MetadataSchema]:
        """Transform metadata according to settings."""
        try:
            # Standardize metadata
            if settings.standard != MetadataStandard.CUSTOM:
                standardized = await self.standardize_metadata(metadata, settings.standard)
                
                # Convert back to dict for further processing
                metadata_dict = asdict(standardized)
            else:
                metadata_dict = metadata.copy()
            
            # Normalize dates
            if settings.normalize_dates:
                metadata_dict = await self._normalize_dates(metadata_dict)
            
            # Filter metadata based on settings
            if not settings.include_technical:
                # Remove technical fields
                technical_fields = ['file_size', 'file_hash', 'encoding', 'bitrate', 'sample_rate']
                for field in technical_fields:
                    metadata_dict.pop(field, None)
            
            if not settings.include_custom:
                metadata_dict.pop('custom_fields', None)
            
            return metadata_dict
            
        except Exception as e:
            logger.error(f"Metadata transformation failed: {str(e)}")
            return metadata
    
    async def _save_metadata(
        self,
        metadata: Union[Dict[str, Any], MetadataSchema],
        output_path: Path,
        settings: MetadataSettings
    ):
        """Save metadata in specified format."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict if needed
            if isinstance(metadata, MetadataSchema):
                metadata_dict = asdict(metadata)
            else:
                metadata_dict = metadata
            
            # Remove None values
            metadata_dict = {k: v for k, v in metadata_dict.items() if v is not None}
            
            if settings.format == MetadataFormat.JSON:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_dict, f, indent=2, ensure_ascii=False, default=str)
            
            elif settings.format == MetadataFormat.XML:
                root = ET.Element('metadata')
                self._dict_to_xml(metadata_dict, root)
                
                # Pretty print XML
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = xml.dom.minidom.parseString(rough_string)
                pretty_xml = reparsed.toprettyxml(indent="  ")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)
            
            elif settings.format == MetadataFormat.YAML:
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(metadata_dict, f, default_flow_style=False, allow_unicode=True)
            
            elif settings.format == MetadataFormat.CSV:
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if metadata_dict:
                        writer = csv.DictWriter(f, fieldnames=metadata_dict.keys())
                        writer.writeheader()
                        writer.writerow(metadata_dict)
            
        except Exception as e:
            logger.error(f"Metadata save failed: {str(e)}")
            raise
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element):
        """Convert dictionary to XML elements."""
        for key, value in data.items():
            # Clean key name for XML
            clean_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
            element = ET.SubElement(parent, clean_key)
            
            if isinstance(value, dict):
                self._dict_to_xml(value, element)
            elif isinstance(value, list):
                for item in value:
                    item_element = ET.SubElement(element, 'item')
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_element)
                    else:
                        item_element.text = str(item)
            else:
                element.text = str(value)
    
    async def _normalize_dates(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
Normalize date formats in metadata."""
        try:
            date_fields = ['date', 'creation_date', 'modification_date', 'creation_time', 'modification_time']
            
            for field in date_fields:
                if field in metadata and metadata[field]:
                    try:
                        # Parse various date formats and convert to ISO format
                        date_str = str(metadata[field])
                        
                        # Try common formats
                        formats = [
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%SZ',
                            '%Y-%m-%dT%H:%M:%S%z',
                            '%Y-%m-%d',
                            '%Y',
                            '%d/%m/%Y',
                            '%m/%d/%Y'
                        ]
                        
                        parsed_date = None
                        for fmt in formats:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if parsed_date:
                            metadata[field] = parsed_date.isoformat()
                    
                    except Exception as e:
                        logger.warning(f"Could not normalize date '{metadata[field]}': {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Date normalization failed: {str(e)}")
            return metadata
    
    async def _calculate_file_hash(self, file_path: Path, algorithm: str = 'md5') -> str:
        """Calculate file hash."""
        try:
            if algorithm == 'md5':
                hash_obj = hashlib.md5()
            elif algorithm == 'sha256':
                hash_obj = hashlib.sha256()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            return ""
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'
    
    def _parse_metadata_settings(self, request) -> MetadataSettings:
        """
Parse transformation request into metadata settings."""
        settings = MetadataSettings()
        
        if hasattr(request, 'target_format') and request.target_format:
            try:
                settings.format = MetadataFormat(request.target_format)
            except ValueError:
                pass
        
        if hasattr(request, 'options') and request.options:
            options = request.options
            settings.include_technical = options.get('include_technical', True)
            settings.include_descriptive = options.get('include_descriptive', True)
            settings.include_custom = options.get('include_custom', True)
            settings.normalize_dates = options.get('normalize_dates', True)
            settings.extract_embedded = options.get('extract_embedded', True)
            settings.validate_schema = options.get('validate_schema', True)
            
            if options.get('standard'):
                try:
                    settings.standard = MetadataStandard(options['standard'])
                except ValueError:
                    pass
        
        return settings
    
    def _generate_output_path(
        self,
        input_path: Path,
        settings: MetadataSettings,
        requested_output: Optional[str] = None
    ) -> Path:
        """
Generate output file path."""
        if requested_output:
            return Path(requested_output)
        
        # Generate based on input and settings
        output_name = f"{input_path.stem}_metadata.{settings.format.value}"
        return input_path.parent / output_name
    
    async def cleanup(self):
        """Cleanup temporary files and resources."""
        try:
            # Clean temp directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("MetadataTransformer cleanup completed")
            
        except Exception as e:
            logger.error(f"MetadataTransformer cleanup failed: {str(e)}")


class MetadataExtractor:
    """Simplified metadata extractor interface."""
    
    def __init__(self, transformer: Optional[MetadataTransformer] = None):
        self.transformer = transformer or MetadataTransformer()
    
    async def extract(self, file_path: str) -> Dict[str, Any]:
        """
Extract metadata from file."""
        return await self.transformer.extract_metadata(file_path)


class MetadataStandardizer:
    """
Simplified metadata standardizer interface."""
    
    def __init__(self, transformer: Optional[MetadataTransformer] = None):
        self.transformer = transformer or MetadataTransformer()
    
    async def standardize(
        self,
        metadata: Dict[str, Any],
        standard: str = "dublin_core"
    ) -> MetadataSchema:
        """Standardize metadata to schema."""
        return await self.transformer.standardize_metadata(
            metadata, 
            MetadataStandard(standard)
        )
