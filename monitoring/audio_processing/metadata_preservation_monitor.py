"""
Ainflue Platform - Metadata Preservation Monitor
================================================

Enterprise monitoring for metadata preservation during audio processing,
ensuring critical information retention across format conversions,
quality transformations, and distribution workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib

logger = logging.getLogger(__name__)

class MetadataType(Enum):
    """Types of metadata to preserve."""
    ID3_TAGS = "id3_tags"
    VORBIS_COMMENTS = "vorbis_comments"
    APE_TAGS = "ape_tags"
    TECHNICAL_INFO = "technical_info"
    EMBEDDED_ARTWORK = "embedded_artwork"
    LYRICS = "lyrics"
    COPYRIGHT_INFO = "copyright_info"
    CUSTOM_FIELDS = "custom_fields"
    TIMESTAMPED_METADATA = "timestamped_metadata"
    STREAMING_METADATA = "streaming_metadata"

class PreservationStatus(Enum):
    """Status of metadata preservation."""
    PRESERVED = "preserved"
    PARTIALLY_PRESERVED = "partially_preserved"
    LOST = "lost"
    CORRUPTED = "corrupted"
    ENHANCED = "enhanced"
    CONVERTED = "converted"

@dataclass
class MetadataField:
    """Individual metadata field information."""
    field_name: str
    field_type: str
    original_value: Any
    preserved_value: Any
    preservation_status: PreservationStatus
    size_bytes: int
    encoding: str
    is_critical: bool = False

@dataclass
class MetadataPreservationReport:
    """Report on metadata preservation for a processing operation."""
    report_id: str
    audio_file_id: str
    operation_type: str
    input_format: str
    output_format: str
    metadata_fields: List[MetadataField]
    preservation_score: float
    critical_fields_preserved: int
    total_critical_fields: int
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class MetadataPreservationMonitor:
    """
    Enterprise metadata preservation monitoring system.
    
    Monitors:
    - Metadata retention across format conversions
    - Critical field preservation tracking
    - Encoding compatibility validation
    - Custom metadata handling
    - Artwork and embedded content preservation
    - Compliance with industry standards
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.preservation_reports: List[MetadataPreservationReport] = []
        self.critical_fields = self._define_critical_fields()
        self.format_capabilities = self._initialize_format_capabilities()
        self._initialize_preservation_rules()
        
        logger.info("Metadata Preservation Monitor initialized")
    
    def _define_critical_fields(self) -> Set[str]:
        """Define critical metadata fields that must be preserved."""
        return {
            'title', 'artist', 'album', 'album_artist', 'track_number',
            'disc_number', 'year', 'genre', 'duration', 'sample_rate',
            'bit_depth', 'channels', 'copyright', 'isrc', 'upc',
            'publisher', 'composer', 'original_artist', 'bpm'
        }
    
    def _initialize_format_capabilities(self) -> Dict[str, Dict[str, bool]]:
        """Initialize metadata capabilities for different audio formats."""
        return {
            'mp3': {
                'id3_v1': True, 'id3_v2': True, 'embedded_artwork': True,
                'lyrics': True, 'custom_fields': True, 'unicode': True
            },
            'flac': {
                'vorbis_comments': True, 'embedded_artwork': True,
                'lyrics': True, 'custom_fields': True, 'unicode': True,
                'cue_sheets': True, 'application_tags': True
            },
            'wav': {
                'list_info': True, 'bext_chunk': True, 'cart_chunk': True,
                'embedded_artwork': False, 'unicode': False
            },
            'aac': {
                'mp4_tags': True, 'embedded_artwork': True,
                'lyrics': True, 'custom_fields': True, 'unicode': True
            },
            'ogg': {
                'vorbis_comments': True, 'embedded_artwork': True,
                'lyrics': True, 'custom_fields': True, 'unicode': True
            },
            'opus': {
                'vorbis_comments': True, 'embedded_artwork': True,
                'custom_fields': True, 'unicode': True
            }
        }
    
    def _initialize_preservation_rules(self) -> None:
        """Initialize metadata preservation rules."""
        self.preservation_rules = {
            'always_preserve': self.critical_fields,
            'format_specific_mapping': {
                ('mp3', 'flac'): {
                    'id3_to_vorbis': True,
                    'preserve_artwork': True,
                    'preserve_lyrics': True
                },
                ('flac', 'mp3'): {
                    'vorbis_to_id3': True,
                    'preserve_artwork': True,
                    'preserve_lyrics': True
                },
                ('wav', 'flac'): {
                    'preserve_technical': True,
                    'add_compression_metadata': True
                }
            },
            'quality_thresholds': {
                'minimum_preservation_score': 0.8,
                'critical_field_preservation_rate': 0.95
            }
        }
    
    async def monitor_metadata_preservation(self, audio_file_id: str,
                                          operation_type: str,
                                          input_format: str,
                                          output_format: str,
                                          original_metadata: Dict[str, Any],
                                          processed_metadata: Dict[str, Any],
                                          processing_time_ms: float) -> str:
        """Monitor metadata preservation for an audio processing operation."""
        report_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Analyze metadata preservation
        metadata_fields = await self._analyze_metadata_preservation(
            original_metadata, processed_metadata, input_format, output_format
        )
        
        # Calculate preservation metrics
        preservation_score = self._calculate_preservation_score(metadata_fields)
        critical_preserved, total_critical = self._count_critical_field_preservation(metadata_fields)
        
        # Create preservation report
        report = MetadataPreservationReport(
            report_id=report_id,
            audio_file_id=audio_file_id,
            operation_type=operation_type,
            input_format=input_format,
            output_format=output_format,
            metadata_fields=metadata_fields,
            preservation_score=preservation_score,
            critical_fields_preserved=critical_preserved,
            total_critical_fields=total_critical,
            processing_time_ms=processing_time_ms
        )
        
        self.preservation_reports.append(report)
        
        # Check for preservation issues
        await self._check_preservation_quality(report)
        
        logger.info(f"Metadata preservation monitored: {report_id} "
                   f"(score={preservation_score:.3f}, critical={critical_preserved}/{total_critical})")
        
        return report_id
    
    async def _analyze_metadata_preservation(self, original_metadata: Dict[str, Any],
                                           processed_metadata: Dict[str, Any],
                                           input_format: str,
                                           output_format: str) -> List[MetadataField]:
        """Analyze preservation status for each metadata field."""
        metadata_fields = []
        
        # Check all fields from original metadata
        for field_name, original_value in original_metadata.items():
            preserved_value = processed_metadata.get(field_name)
            
            # Determine preservation status
            status = self._determine_preservation_status(
                original_value, preserved_value, field_name, input_format, output_format
            )
            
            metadata_field = MetadataField(
                field_name=field_name,
                field_type=type(original_value).__name__,
                original_value=original_value,
                preserved_value=preserved_value,
                preservation_status=status,
                size_bytes=self._calculate_field_size(original_value),
                encoding=self._detect_encoding(original_value),
                is_critical=field_name.lower() in self.critical_fields
            )
            
            metadata_fields.append(metadata_field)
        
        # Check for new fields added during processing
        for field_name, new_value in processed_metadata.items():
            if field_name not in original_metadata:
                metadata_field = MetadataField(
                    field_name=field_name,
                    field_type=type(new_value).__name__,
                    original_value=None,
                    preserved_value=new_value,
                    preservation_status=PreservationStatus.ENHANCED,
                    size_bytes=self._calculate_field_size(new_value),
                    encoding=self._detect_encoding(new_value),
                    is_critical=field_name.lower() in self.critical_fields
                )
                metadata_fields.append(metadata_field)
        
        return metadata_fields
    
    def _determine_preservation_status(self, original_value: Any, preserved_value: Any,
                                     field_name: str, input_format: str, 
                                     output_format: str) -> PreservationStatus:
        """Determine the preservation status of a metadata field."""
        if preserved_value is None:
            return PreservationStatus.LOST
        
        if original_value == preserved_value:
            return PreservationStatus.PRESERVED
        
        # Check for format-specific conversions
        if self._is_valid_conversion(original_value, preserved_value, field_name, 
                                   input_format, output_format):
            return PreservationStatus.CONVERTED
        
        # Check for partial preservation (e.g., truncated strings)
        if isinstance(original_value, str) and isinstance(preserved_value, str):
            if preserved_value in original_value or original_value in preserved_value:
                return PreservationStatus.PARTIALLY_PRESERVED
        
        # Check for corruption
        if self._is_corrupted(original_value, preserved_value):
            return PreservationStatus.CORRUPTED
        
        return PreservationStatus.PARTIALLY_PRESERVED
    
    def _is_valid_conversion(self, original_value: Any, preserved_value: Any,
                           field_name: str, input_format: str, output_format: str) -> bool:
        """Check if the value change represents a valid format conversion."""
        conversion_key = (input_format.lower(), output_format.lower())
        
        if conversion_key not in self.preservation_rules['format_specific_mapping']:
            return False
        
        # Handle specific conversion scenarios
        if field_name.lower() == 'genre':
            # Genre mapping between formats
            return isinstance(original_value, str) and isinstance(preserved_value, str)
        
        if field_name.lower() in ['track_number', 'disc_number']:
            # Number format conversions
            try:
                return int(str(original_value).split('/')[0]) == int(str(preserved_value).split('/')[0])
            except (ValueError, AttributeError):
                return False
        
        return False
    
    def _is_corrupted(self, original_value: Any, preserved_value: Any) -> bool:
        """Check if preserved value appears corrupted."""
        if type(original_value) != type(preserved_value):
            return True
        
        if isinstance(original_value, str):
            # Check for encoding issues
            try:
                preserved_value.encode('utf-8')
                return False
            except UnicodeEncodeError:
                return True
        
        return False
    
    def _calculate_field_size(self, value: Any) -> int:
        """Calculate the size of a metadata field in bytes."""
        if value is None:
            return 0
        
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, bytes):
            return len(value)
        elif isinstance(value, (int, float)):
            return 8  # Approximate
        else:
            return len(str(value).encode('utf-8'))
    
    def _detect_encoding(self, value: Any) -> str:
        """Detect the encoding of a metadata value."""
        if isinstance(value, str):
            try:
                value.encode('ascii')
                return 'ascii'
            except UnicodeEncodeError:
                return 'utf-8'
        elif isinstance(value, bytes):
            return 'binary'
        else:
            return 'other'
    
    def _calculate_preservation_score(self, metadata_fields: List[MetadataField]) -> float:
        """Calculate overall preservation score."""
        if not metadata_fields:
            return 1.0
        
        total_weight = 0
        preserved_weight = 0
        
        for field in metadata_fields:
            # Weight critical fields more heavily
            weight = 3.0 if field.is_critical else 1.0
            total_weight += weight
            
            # Score based on preservation status
            if field.preservation_status == PreservationStatus.PRESERVED:
                preserved_weight += weight
            elif field.preservation_status == PreservationStatus.CONVERTED:
                preserved_weight += weight * 0.9
            elif field.preservation_status == PreservationStatus.ENHANCED:
                preserved_weight += weight * 1.1  # Bonus for enhancement
            elif field.preservation_status == PreservationStatus.PARTIALLY_PRESERVED:
                preserved_weight += weight * 0.5
            elif field.preservation_status == PreservationStatus.CORRUPTED:
                preserved_weight += weight * 0.1
            # LOST fields contribute 0
        
        return min(1.0, preserved_weight / total_weight) if total_weight > 0 else 1.0
    
    def _count_critical_field_preservation(self, metadata_fields: List[MetadataField]) -> tuple:
        """Count critical field preservation."""
        critical_fields = [f for f in metadata_fields if f.is_critical]
        preserved_critical = len([
            f for f in critical_fields 
            if f.preservation_status in [PreservationStatus.PRESERVED, PreservationStatus.CONVERTED]
        ])
        
        return preserved_critical, len(critical_fields)
    
    async def _check_preservation_quality(self, report -> None: MetadataPreservationReport) -> None:
        """Check preservation quality and alert if needed."""
        min_score = self.preservation_rules['quality_thresholds']['minimum_preservation_score']
        min_critical_rate = self.preservation_rules['quality_thresholds']['critical_field_preservation_rate']
        
        if report.preservation_score < min_score:
            logger.warning(f"Low metadata preservation score: {report.preservation_score:.3f} "
                          f"for {report.report_id}")
        
        critical_rate = (report.critical_fields_preserved / report.total_critical_fields 
                        if report.total_critical_fields > 0 else 1.0)
        
        if critical_rate < min_critical_rate:
            logger.warning(f"Low critical field preservation: {critical_rate:.3f} "
                          f"for {report.report_id}")
        
        # Check for specific issues
        lost_fields = [f for f in report.metadata_fields 
                      if f.preservation_status == PreservationStatus.LOST and f.is_critical]
        if lost_fields:
            logger.error(f"Critical metadata fields lost: {[f.field_name for f in lost_fields]} "
                        f"in {report.report_id}")
    
    def get_preservation_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get metadata preservation statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_reports = [
            report for report in self.preservation_reports
            if report.timestamp >= cutoff_time
        ]
        
        if not recent_reports:
            return {"message": f"No preservation reports in last {hours} hours"}
        
        # Calculate overall statistics
        total_reports = len(recent_reports)
        avg_score = sum(r.preservation_score for r in recent_reports) / total_reports
        
        # Status distribution
        all_fields = [field for report in recent_reports for field in report.metadata_fields]
        status_counts = {}
        for status in PreservationStatus:
            status_counts[status.value] = len([f for f in all_fields if f.preservation_status == status])
        
        # Format conversion statistics
        conversion_stats = {}
        for report in recent_reports:
            conversion_key = f"{report.input_format} -> {report.output_format}"
            if conversion_key not in conversion_stats:
                conversion_stats[conversion_key] = {
                    'count': 0,
                    'avg_score': 0,
                    'scores': []
                }
            conversion_stats[conversion_key]['count'] += 1
            conversion_stats[conversion_key]['scores'].append(report.preservation_score)
        
        # Calculate averages for conversions
        for conversion, stats in conversion_stats.items():
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            del stats['scores']  # Remove raw scores to save space
        
        # Critical field statistics
        total_critical_fields = sum(r.total_critical_fields for r in recent_reports)
        preserved_critical_fields = sum(r.critical_fields_preserved for r in recent_reports)
        critical_preservation_rate = (preserved_critical_fields / total_critical_fields 
                                    if total_critical_fields > 0 else 1.0)
        
        return {
            'period_hours': hours,
            'total_operations': total_reports,
            'average_preservation_score': avg_score,
            'critical_field_preservation_rate': critical_preservation_rate,
            'preservation_status_distribution': status_counts,
            'format_conversion_stats': conversion_stats,
            'quality_alerts': {
                'low_score_operations': len([r for r in recent_reports 
                                           if r.preservation_score < 0.8]),
                'critical_field_losses': len([r for r in recent_reports 
                                             if r.critical_fields_preserved < r.total_critical_fields])
            }
        }
    
    def get_field_preservation_analysis(self, field_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get detailed preservation analysis for a specific field."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        relevant_fields = []
        for report in self.preservation_reports:
            if report.timestamp >= cutoff_time:
                for field in report.metadata_fields:
                    if field.field_name.lower() == field_name.lower():
                        relevant_fields.append((field, report))
        
        if not relevant_fields:
            return {"message": f"No data for field '{field_name}' in last {hours} hours"}
        
        # Analyze preservation patterns
        status_counts = {}
        for status in PreservationStatus:
            status_counts[status.value] = len([f for f, _ in relevant_fields 
                                             if f.preservation_status == status])
        
        # Format-specific analysis
        format_analysis = {}
        for field, report in relevant_fields:
            conversion_key = f"{report.input_format} -> {report.output_format}"
            if conversion_key not in format_analysis:
                format_analysis[conversion_key] = []
            format_analysis[conversion_key].append(field.preservation_status.value)
        
        return {
            'field_name': field_name,
            'period_hours': hours,
            'total_occurrences': len(relevant_fields),
            'is_critical_field': field_name.lower() in self.critical_fields,
            'preservation_status_distribution': status_counts,
            'format_specific_analysis': format_analysis,
            'preservation_rate': (status_counts.get('preserved', 0) + 
                                status_counts.get('converted', 0)) / len(relevant_fields)
        }

# Global metadata preservation monitor instance
metadata_preservation_monitor = MetadataPreservationMonitor()

# Export main components
__all__ = [
    'MetadataPreservationMonitor',
    'MetadataField',
    'MetadataPreservationReport',
    'MetadataType',
    'PreservationStatus',
    'metadata_preservation_monitor'
]