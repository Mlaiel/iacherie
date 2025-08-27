"""
Archival Metadata Management Module

Comprehensive metadata management system for archived content with advanced
indexing, search capabilities, schema management, and content classification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import re

from ..models import ArchiveEntry
from .exceptions import ArchivalError


logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata"""
    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    ADMINISTRATIVE = "administrative"
    PRESERVATION = "preservation"
    RIGHTS = "rights"
    STRUCTURAL = "structural"


class IndexingStrategy(Enum):
    """Metadata indexing strategies"""
    FULL_TEXT = "full_text"
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"
    TIME_SERIES = "time_series"
    GEOSPATIAL = "geospatial"


class SearchOperator(Enum):
    """Search operators for metadata queries"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"


@dataclass
class MetadataField:
    """Definition of a metadata field"""
    field_name: str
    field_type: str  # string, integer, float, boolean, datetime, json
    description: str
    
    # Validation rules
    required: bool = False
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None  # Regex pattern
    enum_values: Optional[List[str]] = None
    
    # Indexing configuration
    indexed: bool = True
    indexing_strategy: IndexingStrategy = IndexingStrategy.KEYWORD
    searchable: bool = True
    
    # Display and formatting
    display_name: str = ""
    display_order: int = 0
    format_hint: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.display_name:
            self.display_name = self.field_name.replace('_', ' ').title()


@dataclass
class MetadataSchema:
    """Schema definition for metadata"""
    schema_id: str
    name: str
    description: str
    version: str
    
    # Field definitions
    fields: Dict[str, MetadataField] = field(default_factory=dict)
    
    # Schema properties
    content_types: Set[str] = field(default_factory=set)
    metadata_types: Set[MetadataType] = field(default_factory=set)
    
    # Validation settings
    strict_validation: bool = True
    allow_additional_fields: bool = False
    
    # Inheritance
    parent_schema_id: Optional[str] = None
    extends_schemas: List[str] = field(default_factory=list)
    
    # Lifecycle
    active: bool = True
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: str = "system"


@dataclass
class MetadataEntry:
    """Metadata entry for archived content"""
    entry_id: str
    archive_id: str
    schema_id: str
    
    # Content metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Classification
    content_type: str = "unknown"
    metadata_type: MetadataType = MetadataType.DESCRIPTIVE
    tags: Set[str] = field(default_factory=set)
    
    # Quality and validation
    validation_status: str = "pending"  # pending, valid, invalid
    validation_errors: List[str] = field(default_factory=list)
    quality_score: float = 1.0
    
    # Provenance
    source: str = "system"
    extraction_method: str = "manual"
    confidence_score: float = 1.0
    
    # Versioning
    version: int = 1
    previous_version_id: Optional[str] = None
    
    # Access control
    visibility: str = "private"  # private, public, restricted
    access_permissions: List[str] = field(default_factory=list)
    
    # Temporal information
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class SearchCriteria:
    """Search criteria for metadata queries"""
    query_id: str
    
    # Basic search
    keywords: Optional[str] = None
    content_types: List[str] = field(default_factory=list)
    metadata_types: List[MetadataType] = field(default_factory=list)
    
    # Field-specific filters
    field_filters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Date range filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Advanced filters
    tags: List[str] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    min_quality_score: Optional[float] = None
    
    # Search configuration
    case_sensitive: bool = False
    exact_match: bool = False
    fuzzy_search: bool = True
    fuzzy_threshold: float = 0.8
    
    # Result configuration
    max_results: int = 100
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"  # asc, desc
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchResult:
    """Search result entry"""
    entry_id: str
    archive_id: str
    schema_id: str
    
    # Match information
    relevance_score: float
    match_fields: List[str] = field(default_factory=list)
    match_snippets: Dict[str, str] = field(default_factory=dict)
    
    # Entry summary
    content_type: str = "unknown"
    metadata_summary: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    # Temporal information
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MetadataValidator:
    """Validator for metadata against schemas"""
    
    def __init__(self):
        self.validation_cache: Dict[str, bool] = {}
        logger.info("Metadata validator initialized")
    
    async def validate_metadata(
        self,
        metadata: Dict[str, Any],
        schema: MetadataSchema
    ) -> Tuple[bool, List[str]]:
        """
        Validate metadata against schema.
        
        Args:
            metadata: Metadata to validate
            schema: Schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            # Check required fields
            for field_name, field_def in schema.fields.items():
                if field_def.required and field_name not in metadata:
                    errors.append(f"Required field missing: {field_name}")
            
            # Validate present fields
            for field_name, value in metadata.items():
                if field_name in schema.fields:
                    field_errors = await self._validate_field(
                        field_name, value, schema.fields[field_name]
                    )
                    errors.extend(field_errors)
                elif not schema.allow_additional_fields:
                    errors.append(f"Additional field not allowed: {field_name}")
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Metadata validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    async def _validate_field(
        self,
        field_name: str,
        value: Any,
        field_def: MetadataField
    ) -> List[str]:
        """Validate individual field"""
        errors = []
        
        try:
            # Type validation
            if not await self._validate_type(value, field_def.field_type):
                errors.append(f"Invalid type for {field_name}: expected {field_def.field_type}")
                return errors
            
            # String validations
            if field_def.field_type == "string" and isinstance(value, str):
                if field_def.max_length and len(value) > field_def.max_length:
                    errors.append(f"{field_name} exceeds max length: {field_def.max_length}")
                
                if field_def.pattern:
                    if not re.match(field_def.pattern, value):
                        errors.append(f"{field_name} does not match pattern: {field_def.pattern}")
                
                if field_def.enum_values and value not in field_def.enum_values:
                    errors.append(f"{field_name} not in allowed values: {field_def.enum_values}")
            
            # Numeric validations
            elif field_def.field_type in ["integer", "float"] and isinstance(value, (int, float)):
                if field_def.min_value is not None and value < field_def.min_value:
                    errors.append(f"{field_name} below minimum: {field_def.min_value}")
                
                if field_def.max_value is not None and value > field_def.max_value:
                    errors.append(f"{field_name} above maximum: {field_def.max_value}")
            
            return errors
            
        except Exception as e:
            logger.error(f"Field validation failed for {field_name}: {e}")
            return [f"Field validation error: {e}"]
    
    async def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_map = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "datetime": datetime,
            "json": (dict, list)
        }
        
        expected_python_type = type_map.get(expected_type)
        if not expected_python_type:
            return True  # Unknown type, skip validation
        
        return isinstance(value, expected_python_type)


class MetadataIndexer:
    """Advanced indexer for metadata search"""
    
    def __init__(self):
        self.indexes: Dict[str, Dict[str, Set[str]]] = {}
        self.full_text_index: Dict[str, Set[str]] = {}
        self.semantic_index: Dict[str, List[Tuple[str, float]]] = {}
        
        logger.info("Metadata indexer initialized")
    
    async def index_metadata(self, entry: MetadataEntry, schema: MetadataSchema):
        """Index metadata entry for search"""
        try:
            entry_id = entry.entry_id
            
            # Index by content type
            await self._add_to_index("content_type", entry.content_type, entry_id)
            
            # Index tags
            for tag in entry.tags:
                await self._add_to_index("tags", tag, entry_id)
            
            # Index individual fields
            for field_name, value in entry.metadata.items():
                if field_name in schema.fields:
                    field_def = schema.fields[field_name]
                    await self._index_field(field_name, value, field_def, entry_id)
            
            # Full-text indexing
            await self._index_full_text(entry)
            
            logger.debug(f"Indexed metadata entry: {entry_id}")
            
        except Exception as e:
            logger.error(f"Failed to index metadata entry {entry.entry_id}: {e}")
    
    async def search_index(self, criteria: SearchCriteria) -> List[str]:
        """Search indexed metadata"""
        try:
            candidate_entry_ids = set()
            
            # Keyword search
            if criteria.keywords:
                keyword_matches = await self._search_keywords(criteria.keywords)
                if not candidate_entry_ids:
                    candidate_entry_ids = keyword_matches
                else:
                    candidate_entry_ids &= keyword_matches
            
            # Content type filter
            if criteria.content_types:
                type_matches = set()
                for content_type in criteria.content_types:
                    type_matches.update(self.indexes.get("content_type", {}).get(content_type, set()))
                
                if not candidate_entry_ids:
                    candidate_entry_ids = type_matches
                else:
                    candidate_entry_ids &= type_matches
            
            # Tag filters
            if criteria.tags:
                tag_matches = set()
                for tag in criteria.tags:
                    tag_matches.update(self.indexes.get("tags", {}).get(tag, set()))
                
                if not candidate_entry_ids:
                    candidate_entry_ids = tag_matches
                else:
                    candidate_entry_ids &= tag_matches
            
            # Field-specific filters
            for field_name, filter_config in criteria.field_filters.items():
                field_matches = await self._search_field(field_name, filter_config)
                
                if not candidate_entry_ids:
                    candidate_entry_ids = field_matches
                else:
                    candidate_entry_ids &= field_matches
            
            return list(candidate_entry_ids)
            
        except Exception as e:
            logger.error(f"Index search failed: {e}")
            return []
    
    async def _add_to_index(self, index_name: str, value: str, entry_id: str):
        """Add entry to index"""
        if index_name not in self.indexes:
            self.indexes[index_name] = {}
        
        if value not in self.indexes[index_name]:
            self.indexes[index_name][value] = set()
        
        self.indexes[index_name][value].add(entry_id)
    
    async def _index_field(
        self,
        field_name: str,
        value: Any,
        field_def: MetadataField,
        entry_id: str
    ):
        """Index individual field"""
        if not field_def.indexed:
            return
        
        # Convert value to indexable string
        if isinstance(value, (list, dict)):
            index_value = json.dumps(value, sort_keys=True)
        elif isinstance(value, datetime):
            index_value = value.isoformat()
        else:
            index_value = str(value).lower()
        
        await self._add_to_index(field_name, index_value, entry_id)
        
        # Additional indexing based on strategy
        if field_def.indexing_strategy == IndexingStrategy.FULL_TEXT:
            await self._add_to_full_text_index(index_value, entry_id)
        elif field_def.indexing_strategy == IndexingStrategy.SEMANTIC:
            await self._add_to_semantic_index(field_name, index_value, entry_id)
    
    async def _index_full_text(self, entry: MetadataEntry):
        """Index for full-text search"""
        # Combine all string values for full-text indexing
        text_content = []
        
        for value in entry.metadata.values():
            if isinstance(value, str):
                text_content.append(value)
            elif isinstance(value, (list, dict)):
                text_content.append(json.dumps(value))
            else:
                text_content.append(str(value))
        
        combined_text = " ".join(text_content).lower()
        await self._add_to_full_text_index(combined_text, entry.entry_id)
    
    async def _add_to_full_text_index(self, text: str, entry_id: str):
        """Add to full-text index"""
        # Simple word-based indexing
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word not in self.full_text_index:
                self.full_text_index[word] = set()
            self.full_text_index[word].add(entry_id)
    
    async def _add_to_semantic_index(self, field_name: str, value: str, entry_id: str):
        """Add to semantic index (simplified)"""
        # In a real implementation, this would use embeddings
        if field_name not in self.semantic_index:
            self.semantic_index[field_name] = []
        
        # Simple semantic scoring based on text similarity
        similarity_score = len(value) / 100  # Simplified
        self.semantic_index[field_name].append((entry_id, similarity_score))
    
    async def _search_keywords(self, keywords: str) -> Set[str]:
        """Search using keywords"""
        words = re.findall(r'\b\w+\b', keywords.lower())
        matching_entries = set()
        
        for word in words:
            if word in self.full_text_index:
                if not matching_entries:
                    matching_entries = self.full_text_index[word].copy()
                else:
                    matching_entries &= self.full_text_index[word]
        
        return matching_entries
    
    async def _search_field(self, field_name: str, filter_config: Dict[str, Any]) -> Set[str]:
        """Search specific field with filters"""
        operator = filter_config.get("operator", SearchOperator.EQUALS)
        value = filter_config.get("value")
        
        if field_name not in self.indexes:
            return set()
        
        field_index = self.indexes[field_name]
        matching_entries = set()
        
        if operator == SearchOperator.EQUALS:
            matching_entries = field_index.get(str(value).lower(), set())
        elif operator == SearchOperator.CONTAINS:
            for indexed_value, entry_ids in field_index.items():
                if str(value).lower() in indexed_value:
                    matching_entries.update(entry_ids)
        # Add more operators as needed
        
        return matching_entries


class ArchivalMetadataManager:
    """
    Comprehensive metadata management system for archived content.
    
    Provides schema management, validation, indexing, and advanced search
    capabilities for archival metadata.
    """
    
    def __init__(self):
        self.schemas: Dict[str, MetadataSchema] = {}
        self.metadata_entries: Dict[str, MetadataEntry] = {}
        
        # Core components
        self.validator = MetadataValidator()
        self.indexer = MetadataIndexer()
        
        # Statistics
        self.total_entries = 0
        self.total_searches = 0
        self.schema_count = 0
        
        # Initialize default schemas
        asyncio.create_task(self._initialize_default_schemas())
        
        logger.info("Archival Metadata Manager initialized")
    
    async def create_schema(self, schema: MetadataSchema) -> bool:
        """Create a new metadata schema"""
        try:
            # Validate schema
            if not await self._validate_schema(schema):
                raise ArchivalError(f"Invalid schema: {schema.schema_id}")
            
            # Check for existing schema
            if schema.schema_id in self.schemas:
                raise ArchivalError(f"Schema already exists: {schema.schema_id}")
            
            # Store schema
            self.schemas[schema.schema_id] = schema
            self.schema_count += 1
            
            logger.info(f"Created metadata schema: {schema.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    async def update_schema(self, schema_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing schema"""
        try:
            if schema_id not in self.schemas:
                raise ArchivalError(f"Schema not found: {schema_id}")
            
            schema = self.schemas[schema_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(schema, key):
                    setattr(schema, key, value)
            
            schema.updated_at = datetime.utcnow()
            
            logger.info(f"Updated schema: {schema_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update schema: {e}")
            return False
    
    async def add_metadata(self, entry: MetadataEntry) -> bool:
        """Add metadata entry for archived content"""
        try:
            # Validate schema exists
            if entry.schema_id not in self.schemas:
                raise ArchivalError(f"Schema not found: {entry.schema_id}")
            
            schema = self.schemas[entry.schema_id]
            
            # Validate metadata
            is_valid, errors = await self.validator.validate_metadata(entry.metadata, schema)
            
            entry.validation_status = "valid" if is_valid else "invalid"
            entry.validation_errors = errors
            
            if not is_valid and schema.strict_validation:
                raise ArchivalError(f"Metadata validation failed: {errors}")
            
            # Store metadata entry
            self.metadata_entries[entry.entry_id] = entry
            self.total_entries += 1
            
            # Index for search
            await self.indexer.index_metadata(entry, schema)
            
            logger.info(f"Added metadata entry: {entry.entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add metadata: {e}")
            return False
    
    async def update_metadata(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing metadata entry"""
        try:
            if entry_id not in self.metadata_entries:
                raise ArchivalError(f"Metadata entry not found: {entry_id}")
            
            entry = self.metadata_entries[entry_id]
            schema = self.schemas[entry.schema_id]
            
            # Create new version
            entry.version += 1
            entry.previous_version_id = entry_id
            
            # Apply updates to metadata
            for key, value in updates.items():
                if key in ["metadata", "tags", "quality_score"]:
                    setattr(entry, key, value)
                elif key in entry.metadata:
                    entry.metadata[key] = value
            
            entry.updated_at = datetime.utcnow()
            
            # Re-validate
            is_valid, errors = await self.validator.validate_metadata(entry.metadata, schema)
            entry.validation_status = "valid" if is_valid else "invalid"
            entry.validation_errors = errors
            
            # Re-index
            await self.indexer.index_metadata(entry, schema)
            
            logger.info(f"Updated metadata entry: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
    
    async def search_metadata(self, criteria: SearchCriteria) -> Tuple[List[SearchResult], int]:
        """Search metadata with advanced criteria"""
        try:
            self.total_searches += 1
            
            # Get candidate entry IDs from index
            candidate_ids = await self.indexer.search_index(criteria)
            
            # Filter and score results
            results = []
            
            for entry_id in candidate_ids:
                if entry_id not in self.metadata_entries:
                    continue
                
                entry = self.metadata_entries[entry_id]
                
                # Apply additional filters
                if not await self._matches_criteria(entry, criteria):
                    continue
                
                # Calculate relevance score
                relevance_score = await self._calculate_relevance(entry, criteria)
                
                # Create search result
                result = SearchResult(
                    entry_id=entry_id,
                    archive_id=entry.archive_id,
                    schema_id=entry.schema_id,
                    relevance_score=relevance_score,
                    content_type=entry.content_type,
                    metadata_summary=await self._create_summary(entry),
                    tags=entry.tags,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at
                )
                
                results.append(result)
            
            # Sort and paginate
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            total_count = len(results)
            start_idx = criteria.offset
            end_idx = start_idx + criteria.max_results
            
            paginated_results = results[start_idx:end_idx]
            
            logger.info(f"Metadata search returned {len(paginated_results)} of {total_count} results")
            return paginated_results, total_count
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return [], 0
    
    async def get_metadata(self, entry_id: str) -> Optional[MetadataEntry]:
        """Get metadata entry by ID"""
        return self.metadata_entries.get(entry_id)
    
    async def get_metadata_by_archive(self, archive_id: str) -> List[MetadataEntry]:
        """Get all metadata entries for an archive"""
        return [
            entry for entry in self.metadata_entries.values()
            if entry.archive_id == archive_id
        ]
    
    async def get_schema(self, schema_id: str) -> Optional[MetadataSchema]:
        """Get schema by ID"""
        return self.schemas.get(schema_id)
    
    async def list_schemas(self) -> List[MetadataSchema]:
        """List all available schemas"""
        return list(self.schemas.values())
    
    async def get_metadata_stats(self) -> Dict[str, Any]:
        """Get comprehensive metadata statistics"""
        try:
            # Schema statistics
            active_schemas = sum(1 for s in self.schemas.values() if s.active)
            deprecated_schemas = sum(1 for s in self.schemas.values() if s.deprecated)
            
            # Entry statistics by type
            type_counts = {}
            validation_stats = {"valid": 0, "invalid": 0, "pending": 0}
            
            for entry in self.metadata_entries.values():
                # Count by content type
                content_type = entry.content_type
                type_counts[content_type] = type_counts.get(content_type, 0) + 1
                
                # Count by validation status
                validation_stats[entry.validation_status] = validation_stats.get(entry.validation_status, 0) + 1
            
            # Quality metrics
            quality_scores = [entry.quality_score for entry in self.metadata_entries.values()]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                "total_entries": self.total_entries,
                "total_schemas": self.schema_count,
                "active_schemas": active_schemas,
                "deprecated_schemas": deprecated_schemas,
                "total_searches": self.total_searches,
                "content_type_distribution": type_counts,
                "validation_status_distribution": validation_stats,
                "average_quality_score": avg_quality,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get metadata stats: {e}")
            return {}
    
    async def _validate_schema(self, schema: MetadataSchema) -> bool:
        """Validate schema definition"""
        try:
            # Basic validation
            if not schema.schema_id or not schema.name or not schema.version:
                return False
            
            # Validate fields
            for field_name, field_def in schema.fields.items():
                if not field_name or not field_def.field_type:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    async def _matches_criteria(self, entry: MetadataEntry, criteria: SearchCriteria) -> bool:
        """Check if entry matches search criteria"""
        try:
            # Date range filters
            if criteria.created_after and entry.created_at < criteria.created_after:
                return False
            if criteria.created_before and entry.created_at > criteria.created_before:
                return False
            if criteria.updated_after and entry.updated_at and entry.updated_at < criteria.updated_after:
                return False
            if criteria.updated_before and entry.updated_at and entry.updated_at > criteria.updated_before:
                return False
            
            # Quality filter
            if criteria.min_quality_score and entry.quality_score < criteria.min_quality_score:
                return False
            
            # Tag exclusions
            if criteria.exclude_tags and any(tag in entry.tags for tag in criteria.exclude_tags):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Criteria matching failed: {e}")
            return False
    
    async def _calculate_relevance(self, entry: MetadataEntry, criteria: SearchCriteria) -> float:
        """Calculate relevance score for search result"""
        try:
            score = 0.0
            
            # Base score
            score += entry.quality_score * 0.3
            score += entry.confidence_score * 0.2
            
            # Keyword relevance (simplified)
            if criteria.keywords:
                keywords = criteria.keywords.lower().split()
                metadata_text = json.dumps(entry.metadata).lower()
                
                for keyword in keywords:
                    if keyword in metadata_text:
                        score += 0.5
            
            # Tag matching
            if criteria.tags:
                matching_tags = len(set(criteria.tags) & entry.tags)
                score += matching_tags * 0.3
            
            # Recency boost
            age_days = (datetime.utcnow() - entry.created_at).days
            recency_score = max(0, 1 - (age_days / 365))  # Decay over a year
            score += recency_score * 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Relevance calculation failed: {e}")
            return 0.5  # Default score
    
    async def _create_summary(self, entry: MetadataEntry) -> Dict[str, Any]:
        """Create summary of metadata entry"""
        try:
            # Select most important fields for summary
            summary = {}
            
            # Include string fields first (most descriptive)
            for key, value in entry.metadata.items():
                if isinstance(value, str) and len(summary) < 5:
                    summary[key] = value[:100] + "..." if len(str(value)) > 100 else value
                elif isinstance(value, (int, float, bool)) and len(summary) < 5:
                    summary[key] = value
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary creation failed: {e}")
            return {}
    
    async def _initialize_default_schemas(self):
        """Initialize default metadata schemas"""
        try:
            # Audio content schema
            audio_schema = MetadataSchema(
                schema_id="audio_content_v1",
                name="Audio Content Metadata",
                description="Standard metadata schema for audio content",
                version="1.0",
                content_types={"audio/mp3", "audio/wav", "audio/flac"},
                metadata_types={MetadataType.TECHNICAL, MetadataType.DESCRIPTIVE}
            )
            
            # Add audio fields
            audio_schema.fields["title"] = MetadataField(
                field_name="title",
                field_type="string",
                description="Title of the audio content",
                required=True,
                max_length=200,
                searchable=True
            )
            
            audio_schema.fields["artist"] = MetadataField(
                field_name="artist",
                field_type="string",
                description="Artist or creator name",
                required=True,
                max_length=100,
                searchable=True
            )
            
            audio_schema.fields["duration_seconds"] = MetadataField(
                field_name="duration_seconds",
                field_type="integer",
                description="Duration in seconds",
                min_value=0,
                max_value=86400  # 24 hours
            )
            
            await self.create_schema(audio_schema)
            
            # Video content schema
            video_schema = MetadataSchema(
                schema_id="video_content_v1",
                name="Video Content Metadata",
                description="Standard metadata schema for video content",
                version="1.0",
                content_types={"video/mp4", "video/avi", "video/mov"},
                metadata_types={MetadataType.TECHNICAL, MetadataType.DESCRIPTIVE}
            )
            
            # Add video fields
            video_schema.fields["title"] = MetadataField(
                field_name="title",
                field_type="string",
                description="Title of the video content",
                required=True,
                max_length=200,
                searchable=True
            )
            
            video_schema.fields["resolution"] = MetadataField(
                field_name="resolution",
                field_type="string",
                description="Video resolution",
                enum_values=["720p", "1080p", "4K", "8K"],
                searchable=True
            )
            
            await self.create_schema(video_schema)
            
            logger.info("Initialized default metadata schemas")
            
        except Exception as e:
            logger.error(f"Failed to initialize default schemas: {e}")
