"""Content Metadata Repository Module

Enterprise-grade repository for content metadata management with AI-powered
extraction, validation, enrichment, and intelligent content discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime, timedelta
import uuid
import json
from ..models.content_metadata import (
    ContentMetadata,
    MetadataType,
    MetadataSchema,
    MetadataStatus,
    ExtractorType,
    ValidationStatus,
    ConfidenceLevel
)
from ..models.user_content import UserContent
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class ContentMetadataRepository(BaseRepository[ContentMetadata]):
    """    Repository for content metadata operations with AI-powered extraction,
    validation, enrichment, and intelligent content discovery capabilities.
    """    
    def __init__(self, db_session: Session):
        """Initialize content metadata repository"""        super().__init__(db_session, ContentMetadata)
        
    def create_metadata(self,
                       content_id: int,
                       metadata_type: MetadataType,
                       schema_version: MetadataSchema,
                       extractor_type: ExtractorType,
                       metadata_value: Dict[str, Any],
                       confidence_score: float,
                       source: Optional[str] = None,
                       validation_rules: Optional[Dict[str, Any]] = None,
                       extraction_context: Optional[Dict[str, Any]] = None) -> ContentMetadata:
        """        Create content metadata with AI extraction context and validation
        
        Args:
            content_id: Associated content ID
            metadata_type: Type of metadata
            schema_version: Schema version used
            extractor_type: AI extractor used
            metadata_value: Extracted metadata values
            confidence_score: AI confidence score (0.0-1.0)
            source: Source of metadata extraction
            validation_rules: Validation rules applied
            extraction_context: AI extraction context and parameters
            
        Returns:
            Created ContentMetadata instance
        """        try:
            # Validate confidence score
            if not (0.0 <= confidence_score <= 1.0):
                raise RepositoryException("Confidence score must be between 0.0 and 1.0")
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(confidence_score)
            
            # Validate metadata against schema
            validation_result = self._validate_metadata_schema(
                metadata_value, 
                schema_version, 
                validation_rules
            )
            
            # Generate metadata ID
            metadata_id = str(uuid.uuid4())
            
            metadata_data = {
                'content_id': content_id,
                'metadata_type': metadata_type,
                'schema_version': schema_version,
                'extractor_type': extractor_type,
                'metadata_value': metadata_value,
                'confidence_score': confidence_score,
                'confidence_level': confidence_level,
                'source': source,
                'validation_status': validation_result['status'],
                'validation_errors': validation_result.get('errors', []),
                'extraction_context': extraction_context or {},
                'status': MetadataStatus.ACTIVE,
                'metadata_id': metadata_id,
                'extracted_at': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            metadata = self.create(**metadata_data)
            
            self.logger.info(
                f"Created {metadata_type.value} metadata for content {content_id} with {confidence_level.value} confidence"
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to create content metadata: {str(e)}")
            raise RepositoryException(f"Metadata creation failed: {str(e)}")
            
    def _determine_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """        Determine confidence level from numerical score
        
        Args:
            confidence_score: Numerical confidence score
            
        Returns:
            ConfidenceLevel enum value
        """        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
            
    def _validate_metadata_schema(self,
                                 metadata_value: Dict[str, Any],
                                 schema_version: MetadataSchema,
                                 validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """        Validate metadata against schema and rules
        
        Args:
            metadata_value: Metadata to validate
            schema_version: Schema version to validate against
            validation_rules: Additional validation rules
            
        Returns:
            Validation result dictionary
        """        try:
            errors = []
            
            # Schema-specific validation
            if schema_version == MetadataSchema.DUBLIN_CORE_V1:
                required_fields = ['title', 'creator', 'subject', 'description']
                for field in required_fields:
                    if field not in metadata_value:
                        errors.append(f"Missing required field: {field}")
                        
            elif schema_version == MetadataSchema.EXIF_V2:
                # EXIF validation for images
                if 'ImageWidth' in metadata_value and metadata_value['ImageWidth'] <= 0:
                    errors.append("Invalid ImageWidth value")
                    
            elif schema_version == MetadataSchema.ID3_V2:
                # ID3 validation for audio
                if 'TIT2' in metadata_value and not metadata_value['TIT2']:
                    errors.append("Title (TIT2) cannot be empty")
                    
            # Apply custom validation rules
            if validation_rules:
                for rule_name, rule_config in validation_rules.items():
                    if rule_config.get('required', False):
                        field = rule_config.get('field')
                        if field and field not in metadata_value:
                            errors.append(f"Required field missing: {field}")
            
            status = ValidationStatus.VALID if not errors else ValidationStatus.INVALID
            
            return {
                'status': status,
                'errors': errors,
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Metadata validation failed: {str(e)}")
            return {
                'status': ValidationStatus.FAILED,
                'errors': [f"Validation error: {str(e)}"],
                'validated_at': datetime.utcnow().isoformat()
            }
            
    def get_content_metadata(self,
                           content_id: int,
                           metadata_type: Optional[MetadataType] = None,
                           min_confidence: Optional[float] = None,
                           status: Optional[MetadataStatus] = None) -> List[ContentMetadata]:
        """        Get metadata for content with filtering options
        
        Args:
            content_id: Content ID to get metadata for
            metadata_type: Optional metadata type filter
            min_confidence: Optional minimum confidence threshold
            status: Optional status filter
            
        Returns:
            List of ContentMetadata instances
        """        try:
            query = self.db_session.query(ContentMetadata).filter(
                ContentMetadata.content_id == content_id
            )
            
            # Apply filters
            if metadata_type:
                query = query.filter(ContentMetadata.metadata_type == metadata_type)
            if min_confidence:
                query = query.filter(ContentMetadata.confidence_score >= min_confidence)
            if status:
                query = query.filter(ContentMetadata.status == status)
            
            # Order by confidence score (highest first) then by extraction time
            query = query.order_by(
                ContentMetadata.confidence_score.desc(),
                ContentMetadata.extracted_at.desc()
            )
            
            metadata_list = query.all()
            
            self.logger.debug(
                f"Retrieved {len(metadata_list)} metadata entries for content {content_id}"
            )
            
            return metadata_list
            
        except Exception as e:
            self.logger.error(f"Failed to get content metadata: {str(e)}")
            return []
            
    def search_by_metadata(self,
                          search_criteria: Dict[str, Any],
                          metadata_type: Optional[MetadataType] = None,
                          min_confidence: float = 0.7,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """        Search content by metadata values with intelligent matching
        
        Args:
            search_criteria: Metadata search criteria
            metadata_type: Optional metadata type filter
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            
        Returns:
            List of content with matching metadata
        """        try:
            # Build metadata search query
            query = self.db_session.query(
                ContentMetadata, UserContent
            ).join(
                UserContent,
                ContentMetadata.content_id == UserContent.id
            ).filter(
                and_(
                    ContentMetadata.confidence_score >= min_confidence,
                    ContentMetadata.status == MetadataStatus.ACTIVE
                )
            )
            
            if metadata_type:
                query = query.filter(ContentMetadata.metadata_type == metadata_type)
            
            # Apply search criteria to metadata values
            for field, value in search_criteria.items():
                if isinstance(value, str):
                    # Text search in metadata JSON
                    query = query.filter(
                        func.jsonb_path_exists(
                            ContentMetadata.metadata_value,
                            f'$.{field} ? (@ like_regex "{value}" flag "i")'
                        )
                    )
                elif isinstance(value, dict):
                    # Advanced search operations
                    for operation, operand in value.items():
                        if operation == 'contains':
                            query = query.filter(
                                func.jsonb_path_exists(
                                    ContentMetadata.metadata_value,
                                    f'$.{field} ? (@ like_regex "{operand}" flag "i")'
                                )
                            )
                        elif operation == 'equals':
                            query = query.filter(
                                ContentMetadata.metadata_value[field].astext == str(operand)
                            )
                        elif operation == 'range':
                            min_val, max_val = operand
                            query = query.filter(
                                and_(
                                    func.cast(ContentMetadata.metadata_value[field], func.numeric()) >= min_val,
                                    func.cast(ContentMetadata.metadata_value[field], func.numeric()) <= max_val
                                )
                            )
                else:
                    # Direct value match
                    query = query.filter(
                        ContentMetadata.metadata_value[field].astext == str(value)
                    )
            
            # Order by confidence and relevance
            query = query.order_by(
                ContentMetadata.confidence_score.desc(),
                UserContent.upload_date.desc()
            ).limit(limit)
            
            results = query.all()
            
            # Format results with content and metadata details
            search_results = []
            for metadata, content in results:
                search_results.append({
                    'content': content,
                    'metadata': metadata,
                    'relevance_score': metadata.confidence_score,
                    'match_details': {
                        'metadata_type': metadata.metadata_type.value,
                        'extractor_type': metadata.extractor_type.value,
                        'confidence_level': metadata.confidence_level.value
                    }
                })
            
            self.logger.debug(f"Found {len(search_results)} content items matching metadata criteria")
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Failed to search by metadata: {str(e)}")
            return []
            
    def enrich_metadata(self,
                       metadata_id: int,
                       enrichment_data: Dict[str, Any],
                       enrichment_source: str,
                       confidence_boost: float = 0.0) -> Optional[ContentMetadata]:
        """        Enrich existing metadata with additional information
        
        Args:
            metadata_id: Metadata ID to enrich
            enrichment_data: Additional metadata to merge
            enrichment_source: Source of enrichment
            confidence_boost: Confidence score adjustment
            
        Returns:
            Updated ContentMetadata instance
        """        try:
            metadata = self.get_by_id(metadata_id)
            if not metadata:
                return None
            
            # Merge enrichment data with existing metadata
            enriched_value = metadata.metadata_value.copy()
            enriched_value.update(enrichment_data)
            
            # Update confidence score
            new_confidence = min(1.0, metadata.confidence_score + confidence_boost)
            new_confidence_level = self._determine_confidence_level(new_confidence)
            
            # Update extraction context
            extraction_context = metadata.extraction_context or {}
            extraction_context['enrichment_history'] = extraction_context.get('enrichment_history', [])
            extraction_context['enrichment_history'].append({
                'source': enrichment_source,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence_boost': confidence_boost,
                'fields_added': list(enrichment_data.keys())
            })
            
            update_data = {
                'metadata_value': enriched_value,
                'confidence_score': new_confidence,
                'confidence_level': new_confidence_level,
                'extraction_context': extraction_context,
                'updated_at': datetime.utcnow()
            }
            
            updated_metadata = self.update(metadata_id, **update_data)
            
            self.logger.info(
                f"Enriched metadata {metadata_id} from {enrichment_source} with confidence boost {confidence_boost}"
            )
            
            return updated_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to enrich metadata: {str(e)}")
            raise RepositoryException(f"Metadata enrichment failed: {str(e)}")
            
    def get_metadata_statistics(self,
                              user_id: Optional[int] = None,
                              content_type: Optional[str] = None) -> Dict[str, Any]:
        """        Get comprehensive metadata statistics and insights
        
        Args:
            user_id: Optional user ID to filter statistics
            content_type: Optional content type filter
            
        Returns:
            Dictionary containing metadata statistics
        """        try:
            # Base query with content join for user filtering
            base_query = self.db_session.query(ContentMetadata).join(
                UserContent,
                ContentMetadata.content_id == UserContent.id
            )
            
            if user_id:
                base_query = base_query.filter(UserContent.user_id == user_id)
            
            if content_type:
                base_query = base_query.filter(UserContent.content_type == content_type)
            
            metadata_entries = base_query.all()
            
            if not metadata_entries:
                return {
                    'total_metadata_entries': 0,
                    'metadata_types': {},
                    'extractor_types': {},
                    'confidence_distribution': {},
                    'validation_status': {}
                }
            
            # Total counts
            total_entries = len(metadata_entries)
            
            # Metadata type distribution
            type_distribution = {}
            for metadata_type in MetadataType:
                count = sum(1 for entry in metadata_entries if entry.metadata_type == metadata_type)
                type_distribution[metadata_type.value] = count
            
            # Extractor type distribution
            extractor_distribution = {}
            for extractor_type in ExtractorType:
                count = sum(1 for entry in metadata_entries if entry.extractor_type == extractor_type)
                extractor_distribution[extractor_type.value] = count
            
            # Confidence level distribution
            confidence_distribution = {}
            for confidence_level in ConfidenceLevel:
                count = sum(1 for entry in metadata_entries if entry.confidence_level == confidence_level)
                confidence_distribution[confidence_level.value] = count
            
            # Validation status distribution
            validation_distribution = {}
            for status in ValidationStatus:
                count = sum(1 for entry in metadata_entries if entry.validation_status == status)
                validation_distribution[status.value] = count
            
            # Average confidence score
            avg_confidence = sum(entry.confidence_score for entry in metadata_entries) / total_entries
            
            # Quality metrics
            high_confidence_count = sum(
                1 for entry in metadata_entries 
                if entry.confidence_score >= 0.8
            )
            high_confidence_percentage = (high_confidence_count / total_entries) * 100
            
            # Recent extraction activity
            recent_extractions = sum(
                1 for entry in metadata_entries 
                if entry.extracted_at >= datetime.utcnow() - timedelta(days=7)
            )
            
            # Most common metadata fields
            field_frequency = {}
            for entry in metadata_entries:
                for field in entry.metadata_value.keys():
                    field_frequency[field] = field_frequency.get(field, 0) + 1
            
            top_fields = sorted(field_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            statistics = {
                'total_metadata_entries': total_entries,
                'metadata_type_distribution': type_distribution,
                'extractor_type_distribution': extractor_distribution,
                'confidence_distribution': confidence_distribution,
                'validation_distribution': validation_distribution,
                'quality_metrics': {
                    'average_confidence_score': round(avg_confidence, 3),
                    'high_confidence_percentage': round(high_confidence_percentage, 2),
                    'total_validation_errors': sum(
                        len(entry.validation_errors or []) for entry in metadata_entries
                    )
                },
                'activity_metrics': {
                    'recent_extractions_7_days': recent_extractions,
                    'extraction_rate_per_day': round(recent_extractions / 7, 2)
                },
                'field_analysis': {
                    'most_common_fields': [
                        {'field': field, 'count': count} for field, count in top_fields
                    ],
                    'unique_fields_count': len(field_frequency)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata statistics: {str(e)}")
            return {'error': str(e)}
            
    def suggest_metadata_improvements(self, content_id: int) -> List[Dict[str, Any]]:
        """        Suggest metadata improvements based on analysis
        
        Args:
            content_id: Content ID to analyze
            
        Returns:
            List of improvement suggestions
        """        try:
            metadata_entries = self.get_content_metadata(content_id)
            
            if not metadata_entries:
                return [{
                    'type': 'NO_METADATA',
                    'priority': 'HIGH',
                    'suggestion': 'No metadata found. Consider extracting basic metadata.',
                    'action': 'extract_basic_metadata'
                }]
            
            suggestions = []
            
            # Check for low confidence metadata
            low_confidence_entries = [
                entry for entry in metadata_entries 
                if entry.confidence_score < 0.6
            ]
            
            if low_confidence_entries:
                suggestions.append({
                    'type': 'LOW_CONFIDENCE',
                    'priority': 'MEDIUM',
                    'suggestion': f'{len(low_confidence_entries)} metadata entries have low confidence. Consider re-extraction or manual verification.',
                    'action': 'improve_confidence',
                    'affected_entries': len(low_confidence_entries)
                })
            
            # Check for validation errors
            invalid_entries = [
                entry for entry in metadata_entries 
                if entry.validation_status == ValidationStatus.INVALID
            ]
            
            if invalid_entries:
                suggestions.append({
                    'type': 'VALIDATION_ERRORS',
                    'priority': 'HIGH',
                    'suggestion': f'{len(invalid_entries)} metadata entries have validation errors. Review and correct the errors.',
                    'action': 'fix_validation_errors',
                    'affected_entries': len(invalid_entries)
                })
            
            # Check for missing metadata types
            existing_types = {entry.metadata_type for entry in metadata_entries}
            recommended_types = {MetadataType.TECHNICAL, MetadataType.DESCRIPTIVE, MetadataType.RIGHTS}
            missing_types = recommended_types - existing_types
            
            if missing_types:
                suggestions.append({
                    'type': 'MISSING_METADATA_TYPES',
                    'priority': 'LOW',
                    'suggestion': f'Consider extracting {", ".join(t.value for t in missing_types)} metadata.',
                    'action': 'extract_additional_types',
                    'missing_types': [t.value for t in missing_types]
                })
            
            # Check for outdated extractions
            old_entries = [
                entry for entry in metadata_entries 
                if entry.extracted_at < datetime.utcnow() - timedelta(days=90)
            ]
            
            if old_entries:
                suggestions.append({
                    'type': 'OUTDATED_METADATA',
                    'priority': 'LOW',
                    'suggestion': f'{len(old_entries)} metadata entries are over 90 days old. Consider re-extraction.',
                    'action': 'refresh_metadata',
                    'affected_entries': len(old_entries)
                })
            
            # If no issues found
            if not suggestions:
                suggestions.append({
                    'type': 'GOOD_QUALITY',
                    'priority': 'INFO',
                    'suggestion': 'Metadata quality is good. No immediate improvements needed.',
                    'action': 'maintain_current_quality'
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to suggest metadata improvements: {str(e)}")
            return [{
                'type': 'ERROR',
                'priority': 'HIGH',
                'suggestion': f'Error analyzing metadata: {str(e)}',
                'action': 'investigate_error'
            }]
            
    def bulk_update_metadata_status(self,
                                  metadata_ids: List[int],
                                  new_status: MetadataStatus,
                                  reason: Optional[str] = None) -> int:
        """        Bulk update metadata status for multiple entries
        
        Args:
            metadata_ids: List of metadata IDs to update
            new_status: New status to set
            reason: Optional reason for status change
            
        Returns:
            Number of updated metadata entries
        """        try:
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }
            
            # Add reason to extraction context if provided
            if reason:
                # This would need to be handled differently in production
                # as we can't easily update JSON fields in bulk
                pass
            
            updated_count = self.db_session.query(ContentMetadata).filter(
                ContentMetadata.id.in_(metadata_ids)
            ).update(update_data, synchronize_session=False)
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(
                f"Bulk updated {updated_count} metadata entries to status {new_status.value}"
            )
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Failed to bulk update metadata status: {str(e)}")
            raise RepositoryException(f"Bulk metadata status update failed: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
