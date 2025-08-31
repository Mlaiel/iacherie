"""Data Metadata Management System

Comprehensive metadata management for data governance including
data cataloging, schema management, and metadata lineage tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""
import logging
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

from ...core.base import BaseManager
from ...core.exceptions import MetadataError, ValidationError


class DataType(Enum):
    """Data type classifications"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    BINARY = "binary"
    COMPOSITE = "composite"


class SchemaType(Enum):
    """Schema definition types"""
    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    PARQUET = "parquet"
    CUSTOM = "custom"


class MetadataCategory(Enum):
    """Metadata categories"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    QUALITY = "quality"
    SECURITY = "security"
    LINEAGE = "lineage"
    COMPLIANCE = "compliance"


class SensitivityLevel(Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


@dataclass
class DataSchema:
    """Data schema definition"""
    schema_id: str
    name: str
    version: str
    schema_type: SchemaType
    definition: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class BusinessGlossaryTerm:
    """Business glossary term definition"""
    term_id: str
    name: str
    definition: str
    category: str
    synonyms: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    steward: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataAssetMetadata:
    """Comprehensive data asset metadata"""
    asset_id: str
    name: str
    description: str
    data_type: DataType
    schema_id: Optional[str] = None
    
    # Technical metadata
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    encoding: Optional[str] = None
    compression: Optional[str] = None
    checksum: Optional[str] = None
    
    # Business metadata
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    domain: Optional[str] = None
    purpose: Optional[str] = None
    business_terms: List[str] = field(default_factory=list)
    
    # Operational metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    source_system: Optional[str] = None
    location: Optional[str] = None
    
    # Quality metadata
    quality_score: Optional[float] = None
    completeness: Optional[float] = None
    accuracy: Optional[float] = None
    consistency: Optional[float] = None
    validity: Optional[float] = None
    
    # Security metadata
    sensitivity_level: SensitivityLevel = SensitivityLevel.INTERNAL
    contains_pii: bool = False
    encryption_status: Optional[str] = None
    access_restrictions: List[str] = field(default_factory=list)
    
    # Compliance metadata
    regulatory_requirements: List[str] = field(default_factory=list)
    retention_period: Optional[int] = None  # days
    compliance_status: Optional[str] = None
    
    # Lineage metadata
    upstream_assets: List[str] = field(default_factory=list)
    downstream_assets: List[str] = field(default_factory=list)
    transformation_rules: List[str] = field(default_factory=list)
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    is_active: bool = True


@dataclass
class MetadataLineage:
    """Metadata lineage relationship"""
    lineage_id: str
    source_asset_id: str
    target_asset_id: str
    relationship_type: str  # "derives_from", "transforms_to", "references", etc.
    transformation_description: Optional[str] = None
    transformation_logic: Optional[str] = None
    confidence_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataCatalogEntry:
    """Data catalog entry combining asset and metadata"""
    catalog_id: str
    asset_metadata: DataAssetMetadata
    schema: Optional[DataSchema] = None
    lineage: List[MetadataLineage] = field(default_factory=list)
    business_terms: List[BusinessGlossaryTerm] = field(default_factory=list)
    indexed_at: datetime = field(default_factory=datetime.utcnow)
    search_keywords: List[str] = field(default_factory=list)


class SchemaManager:
    """
    Manages data schemas and schema evolution
    
    Handles schema definition, versioning, validation,
    and compatibility checking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Schema storage
        self.schemas: Dict[str, DataSchema] = {}
        self.schema_versions: Dict[str, List[DataSchema]] = {}
    
    async def create_schema(
        self,
        name: str,
        schema_type: SchemaType,
        definition: Dict[str, Any],
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> DataSchema:
        """
        Create a new data schema
        
        Args:
            name: Schema name
            schema_type: Type of schema
            definition: Schema definition
            description: Optional description
            created_by: Schema creator
            
        Returns:
            DataSchema: Created schema
        """
        try:
            # Validate schema definition
            await self._validate_schema_definition(schema_type, definition)
            
            # Generate schema ID
            schema_id = f"{name}_v1.0_{datetime.utcnow().timestamp()}"
            
            # Create schema
            schema = DataSchema(
                schema_id=schema_id,
                name=name,
                version="1.0",
                schema_type=schema_type,
                definition=definition,
                description=description,
                created_by=created_by
            )
            
            # Store schema
            self.schemas[schema_id] = schema
            
            # Initialize version list
            if name not in self.schema_versions:
                self.schema_versions[name] = []
            self.schema_versions[name].append(schema)
            
            self.logger.info(f"Created schema: {schema_id}")
            return schema
            
        except Exception as e:
            self.logger.error(f"Error creating schema {name}: {e}")
            raise MetadataError(f"Schema creation failed: {e}")
    
    async def update_schema(
        self,
        schema_name: str,
        definition: Dict[str, Any],
        description: Optional[str] = None,
        updated_by: str = "system"
    ) -> DataSchema:
        """
        Update an existing schema (creates new version)
        
        Args:
            schema_name: Name of schema to update
            definition: New schema definition
            description: Optional description
            updated_by: User updating schema
            
        Returns:
            DataSchema: New schema version
        """
        try:
            # Get current schema versions
            versions = self.schema_versions.get(schema_name, [])
            if not versions:
                raise MetadataError(f"Schema {schema_name} not found")
            
            # Get latest version
            latest_schema = max(versions, key=lambda s: s.version)
            
            # Calculate new version
            major, minor = map(int, latest_schema.version.split('.'))
            new_version = f"{major}.{minor + 1}"
            
            # Check compatibility
            is_compatible = await self._check_schema_compatibility(
                latest_schema.definition, definition
            )
            
            if not is_compatible:
                # Breaking change - increment major version
                new_version = f"{major + 1}.0"
            
            # Validate new definition
            await self._validate_schema_definition(latest_schema.schema_type, definition)
            
            # Create new schema version
            new_schema_id = f"{schema_name}_v{new_version}_{datetime.utcnow().timestamp()}"
            new_schema = DataSchema(
                schema_id=new_schema_id,
                name=schema_name,
                version=new_version,
                schema_type=latest_schema.schema_type,
                definition=definition,
                description=description or latest_schema.description,
                created_by=updated_by,
                tags=latest_schema.tags.copy()
            )
            
            # Store new schema
            self.schemas[new_schema_id] = new_schema
            self.schema_versions[schema_name].append(new_schema)
            
            # Deactivate old version
            latest_schema.is_active = False
            
            self.logger.info(f"Updated schema {schema_name} to version {new_version}")
            return new_schema
            
        except Exception as e:
            self.logger.error(f"Error updating schema {schema_name}: {e}")
            raise MetadataError(f"Schema update failed: {e}")
    
    async def get_schema(
        self,
        schema_id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None
    ) -> Optional[DataSchema]:
        """
        Get schema by ID or name/version
        
        Args:
            schema_id: Schema ID
            name: Schema name
            version: Schema version
            
        Returns:
            DataSchema or None
        """
        if schema_id:
            return self.schemas.get(schema_id)
        
        if name:
            versions = self.schema_versions.get(name, [])
            if version:
                for schema in versions:
                    if schema.version == version:
                        return schema
            else:
                # Return latest active version
                active_versions = [s for s in versions if s.is_active]
                if active_versions:
                    return max(active_versions, key=lambda s: s.version)
        
        return None
    
    async def validate_data_against_schema(
        self,
        data: Any,
        schema_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema_id: Schema ID
            
        Returns:
            Tuple[bool, List[str]]: Validation result and errors
        """
        try:
            schema = self.schemas.get(schema_id)
            if not schema:
                return False, [f"Schema {schema_id} not found"]
            
            # Perform validation based on schema type
            if schema.schema_type == SchemaType.JSON_SCHEMA:
                return await self._validate_json_schema(data, schema.definition)
            else:
                # Placeholder for other schema types
                return True, []
            
        except Exception as e:
            self.logger.error(f"Error validating data against schema {schema_id}: {e}")
            return False, [f"Validation error: {e}"]
    
    async def _validate_schema_definition(
        self,
        schema_type: SchemaType,
        definition: Dict[str, Any]
    ) -> None:
        """Validate schema definition"""
        if schema_type == SchemaType.JSON_SCHEMA:
            required_fields = ["type"]
            for field in required_fields:
                if field not in definition:
                    raise ValidationError(f"Missing required field: {field}")
    
    async def _check_schema_compatibility(
        self,
        old_definition: Dict[str, Any],
        new_definition: Dict[str, Any]
    ) -> bool:
        """Check if new schema is backward compatible"""
        # Simplified compatibility check
        # Real implementation would be more sophisticated
        return True
    
    async def _validate_json_schema(
        self,
        data: Any,
        schema_definition: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate data against JSON schema"""
        # Simplified validation - real implementation would use jsonschema library
        errors = []
        
        if "type" in schema_definition:
            expected_type = schema_definition["type"]
            if expected_type == "object" and not isinstance(data, dict):
                errors.append(f"Expected object, got {type(data).__name__}")
            elif expected_type == "array" and not isinstance(data, list):
                errors.append(f"Expected array, got {type(data).__name__}")
            elif expected_type == "string" and not isinstance(data, str):
                errors.append(f"Expected string, got {type(data).__name__}")
        
        return len(errors) == 0, errors


class BusinessGlossaryManager:
    """
    Manages business glossary and terminology
    
    Maintains business terms, definitions, and relationships
    to enable consistent understanding of data assets.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Glossary storage
        self.terms: Dict[str, BusinessGlossaryTerm] = {}
        self.term_categories: Dict[str, List[str]] = {}
        self.term_domains: Dict[str, List[str]] = {}
    
    async def create_term(
        self,
        name: str,
        definition: str,
        category: str,
        synonyms: Optional[List[str]] = None,
        domain: Optional[str] = None,
        steward: Optional[str] = None
    ) -> BusinessGlossaryTerm:
        """
        Create a new business glossary term
        
        Args:
            name: Term name
            definition: Term definition
            category: Term category
            synonyms: Optional synonyms
            domain: Optional domain
            steward: Optional data steward
            
        Returns:
            BusinessGlossaryTerm: Created term
        """
        try:
            # Generate term ID
            term_id = f"term_{name.lower().replace(' ', '_')}_{datetime.utcnow().timestamp()}"
            
            # Create term
            term = BusinessGlossaryTerm(
                term_id=term_id,
                name=name,
                definition=definition,
                category=category,
                synonyms=synonyms or [],
                domain=domain,
                steward=steward
            )
            
            # Store term
            self.terms[term_id] = term
            
            # Update category index
            if category not in self.term_categories:
                self.term_categories[category] = []
            self.term_categories[category].append(term_id)
            
            # Update domain index
            if domain:
                if domain not in self.term_domains:
                    self.term_domains[domain] = []
                self.term_domains[domain].append(term_id)
            
            self.logger.info(f"Created business term: {name}")
            return term
            
        except Exception as e:
            self.logger.error(f"Error creating business term {name}: {e}")
            raise MetadataError(f"Term creation failed: {e}")
    
    async def search_terms(
        self,
        query: str,
        category: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[BusinessGlossaryTerm]:
        """
        Search business glossary terms
        
        Args:
            query: Search query
            category: Optional category filter
            domain: Optional domain filter
            
        Returns:
            List of matching terms
        """
        results = []
        query_lower = query.lower()
        
        for term in self.terms.values():
            # Check name and definition
            if (query_lower in term.name.lower() or 
                query_lower in term.definition.lower()):
                
                # Apply filters
                if category and term.category != category:
                    continue
                if domain and term.domain != domain:
                    continue
                
                results.append(term)
            
            # Check synonyms
            elif any(query_lower in synonym.lower() for synonym in term.synonyms):
                if category and term.category != category:
                    continue
                if domain and term.domain != domain:
                    continue
                
                results.append(term)
        
        return results
    
    async def link_related_terms(self, term_id: str, related_term_ids: List[str]) -> None:
        """Link related business terms"""
        term = self.terms.get(term_id)
        if not term:
            raise MetadataError(f"Term {term_id} not found")
        
        # Add bidirectional relationships
        for related_id in related_term_ids:
            if related_id not in term.related_terms:
                term.related_terms.append(related_id)
            
            # Add reverse relationship
            related_term = self.terms.get(related_id)
            if related_term and term_id not in related_term.related_terms:
                related_term.related_terms.append(term_id)


class DataCatalogManager:
    """
    Central data catalog management system
    
    Maintains comprehensive catalog of all data assets with
    rich metadata, lineage, and discoverability features.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Catalog storage
        self.catalog_entries: Dict[str, DataCatalogEntry] = {}
        self.asset_metadata: Dict[str, DataAssetMetadata] = {}
        self.lineage_relationships: List[MetadataLineage] = []
        
        # Search indexes
        self.keyword_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.domain_index: Dict[str, Set[str]] = {}
        
        # Managers
        self.schema_manager = SchemaManager(config)
        self.glossary_manager = BusinessGlossaryManager(config)
    
    async def register_data_asset(
        self,
        asset_id: str,
        name: str,
        description: str,
        data_type: DataType,
        **metadata_kwargs
    ) -> DataAssetMetadata:
        """
        Register a new data asset in the catalog
        
        Args:
            asset_id: Unique asset identifier
            name: Asset name
            description: Asset description
            data_type: Type of data
            **metadata_kwargs: Additional metadata
            
        Returns:
            DataAssetMetadata: Created asset metadata
        """
        try:
            # Create asset metadata
            asset_metadata = DataAssetMetadata(
                asset_id=asset_id,
                name=name,
                description=description,
                data_type=data_type,
                **metadata_kwargs
            )
            
            # Store metadata
            self.asset_metadata[asset_id] = asset_metadata
            
            # Create catalog entry
            catalog_entry = DataCatalogEntry(
                catalog_id=f"catalog_{asset_id}",
                asset_metadata=asset_metadata,
                search_keywords=self._generate_search_keywords(asset_metadata)
            )
            
            # Store catalog entry
            self.catalog_entries[asset_id] = catalog_entry
            
            # Update search indexes
            await self._update_search_indexes(asset_metadata)
            
            self.logger.info(f"Registered data asset: {asset_id}")
            return asset_metadata
            
        except Exception as e:
            self.logger.error(f"Error registering data asset {asset_id}: {e}")
            raise MetadataError(f"Asset registration failed: {e}")
    
    async def update_asset_metadata(
        self,
        asset_id: str,
        updates: Dict[str, Any]
    ) -> DataAssetMetadata:
        """
        Update asset metadata
        
        Args:
            asset_id: Asset identifier
            updates: Metadata updates
            
        Returns:
            DataAssetMetadata: Updated metadata
        """
        try:
            asset_metadata = self.asset_metadata.get(asset_id)
            if not asset_metadata:
                raise MetadataError(f"Asset {asset_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(asset_metadata, key):
                    setattr(asset_metadata, key, value)
            
            # Update timestamp
            asset_metadata.updated_at = datetime.utcnow()
            
            # Update catalog entry
            catalog_entry = self.catalog_entries[asset_id]
            catalog_entry.search_keywords = self._generate_search_keywords(asset_metadata)
            catalog_entry.indexed_at = datetime.utcnow()
            
            # Update search indexes
            await self._update_search_indexes(asset_metadata)
            
            self.logger.info(f"Updated metadata for asset: {asset_id}")
            return asset_metadata
            
        except Exception as e:
            self.logger.error(f"Error updating asset metadata {asset_id}: {e}")
            raise MetadataError(f"Metadata update failed: {e}")
    
    async def add_lineage_relationship(
        self,
        source_asset_id: str,
        target_asset_id: str,
        relationship_type: str,
        transformation_description: Optional[str] = None,
        transformation_logic: Optional[str] = None
    ) -> MetadataLineage:
        """
        Add lineage relationship between assets
        
        Args:
            source_asset_id: Source asset ID
            target_asset_id: Target asset ID
            relationship_type: Type of relationship
            transformation_description: Optional description
            transformation_logic: Optional transformation logic
            
        Returns:
            MetadataLineage: Created lineage relationship
        """
        try:
            # Generate lineage ID
            lineage_id = f"lineage_{source_asset_id}_{target_asset_id}_{datetime.utcnow().timestamp()}"
            
            # Create lineage relationship
            lineage = MetadataLineage(
                lineage_id=lineage_id,
                source_asset_id=source_asset_id,
                target_asset_id=target_asset_id,
                relationship_type=relationship_type,
                transformation_description=transformation_description,
                transformation_logic=transformation_logic
            )
            
            # Store lineage
            self.lineage_relationships.append(lineage)
            
            # Update asset metadata
            source_metadata = self.asset_metadata.get(source_asset_id)
            if source_metadata and target_asset_id not in source_metadata.downstream_assets:
                source_metadata.downstream_assets.append(target_asset_id)
            
            target_metadata = self.asset_metadata.get(target_asset_id)
            if target_metadata and source_asset_id not in target_metadata.upstream_assets:
                target_metadata.upstream_assets.append(source_asset_id)
            
            # Update catalog entries
            if source_asset_id in self.catalog_entries:
                self.catalog_entries[source_asset_id].lineage.append(lineage)
            
            if target_asset_id in self.catalog_entries:
                self.catalog_entries[target_asset_id].lineage.append(lineage)
            
            self.logger.info(f"Added lineage relationship: {source_asset_id} -> {target_asset_id}")
            return lineage
            
        except Exception as e:
            self.logger.error(f"Error adding lineage relationship: {e}")
            raise MetadataError(f"Lineage creation failed: {e}")
    
    async def search_catalog(
        self,
        query: str,
        data_type: Optional[DataType] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sensitivity_level: Optional[SensitivityLevel] = None
    ) -> List[DataCatalogEntry]:
        """
        Search the data catalog
        
        Args:
            query: Search query
            data_type: Optional data type filter
            domain: Optional domain filter
            tags: Optional tag filters
            sensitivity_level: Optional sensitivity filter
            
        Returns:
            List of matching catalog entries
        """
        try:
            results = []
            query_lower = query.lower()
            
            for entry in self.catalog_entries.values():
                asset = entry.asset_metadata
                
                # Text search
                if (query_lower in asset.name.lower() or
                    query_lower in asset.description.lower() or
                    any(query_lower in keyword.lower() for keyword in entry.search_keywords)):
                    
                    # Apply filters
                    if data_type and asset.data_type != data_type:
                        continue
                    if domain and asset.domain != domain:
                        continue
                    if sensitivity_level and asset.sensitivity_level != sensitivity_level:
                        continue
                    if tags and not any(tag in asset.tags for tag in tags):
                        continue
                    
                    results.append(entry)
            
            # Sort by relevance (simplified)
            results.sort(key=lambda e: e.asset_metadata.access_count, reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching catalog: {e}")
            return []
    
    async def get_asset_lineage(
        self,
        asset_id: str,
        direction: str = "both"  # "upstream", "downstream", "both"
    ) -> Dict[str, List[MetadataLineage]]:
        """
        Get lineage relationships for an asset
        
        Args:
            asset_id: Asset identifier
            direction: Lineage direction
            
        Returns:
            Dict with upstream and downstream lineage
        """
        upstream = []
        downstream = []
        
        for lineage in self.lineage_relationships:
            if lineage.target_asset_id == asset_id and direction in ["upstream", "both"]:
                upstream.append(lineage)
            elif lineage.source_asset_id == asset_id and direction in ["downstream", "both"]:
                downstream.append(lineage)
        
        return {
            "upstream": upstream,
            "downstream": downstream
        }
    
    async def get_catalog_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        total_assets = len(self.asset_metadata)
        
        # Count by data type
        type_counts = {}
        for asset in self.asset_metadata.values():
            data_type = asset.data_type.value
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        
        # Count by sensitivity level
        sensitivity_counts = {}
        for asset in self.asset_metadata.values():
            level = asset.sensitivity_level.value
            sensitivity_counts[level] = sensitivity_counts.get(level, 0) + 1
        
        # Count assets with PII
        pii_assets = len([a for a in self.asset_metadata.values() if a.contains_pii])
        
        return {
            "total_assets": total_assets,
            "total_schemas": len(self.schema_manager.schemas),
            "total_business_terms": len(self.glossary_manager.terms),
            "total_lineage_relationships": len(self.lineage_relationships),
            "assets_by_type": type_counts,
            "assets_by_sensitivity": sensitivity_counts,
            "assets_with_pii": pii_assets,
            "catalog_health": {
                "assets_with_schema": len([a for a in self.asset_metadata.values() if a.schema_id]),
                "assets_with_owner": len([a for a in self.asset_metadata.values() if a.business_owner]),
                "assets_with_description": len([a for a in self.asset_metadata.values() if a.description])
            }
        }
    
    def _generate_search_keywords(self, asset_metadata: DataAssetMetadata) -> List[str]:
        """Generate search keywords for an asset"""
        keywords = []
        
        # Add name and description words
        keywords.extend(asset_metadata.name.lower().split())
        keywords.extend(asset_metadata.description.lower().split())
        
        # Add tags
        keywords.extend([tag.lower() for tag in asset_metadata.tags])
        
        # Add business terms
        keywords.extend([term.lower() for term in asset_metadata.business_terms])
        
        # Add data type
        keywords.append(asset_metadata.data_type.value.lower())
        
        # Add domain
        if asset_metadata.domain:
            keywords.append(asset_metadata.domain.lower())
        
        # Remove duplicates and filter empty strings
        return list(set([k for k in keywords if k and len(k) > 2]))
    
    async def _update_search_indexes(self, asset_metadata: DataAssetMetadata) -> None:
        """Update search indexes for an asset"""
        asset_id = asset_metadata.asset_id
        
        # Update keyword index
        for keyword in self._generate_search_keywords(asset_metadata):
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = set()
            self.keyword_index[keyword].add(asset_id)
        
        # Update tag index
        for tag in asset_metadata.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(asset_id)
        
        # Update domain index
        if asset_metadata.domain:
            if asset_metadata.domain not in self.domain_index:
                self.domain_index[asset_metadata.domain] = set()
            self.domain_index[asset_metadata.domain].add(asset_id)


class MetadataManager(BaseManager):
    """
    Central metadata management system
    
    Coordinates schema management, business glossary, and data catalog
    to provide comprehensive metadata services for data governance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the metadata manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.catalog_manager = DataCatalogManager(config)
        self.schema_manager = self.catalog_manager.schema_manager
        self.glossary_manager = self.catalog_manager.glossary_manager
        
        # Performance metrics
        self.metrics = {
            "assets_registered": 0,
            "schemas_created": 0,
            "terms_created": 0,
            "lineage_relationships": 0,
            "catalog_searches": 0
        }
    
    async def initialize(self) -> None:
        """Initialize the metadata manager"""
        try:
            self.logger.info("Metadata manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metadata manager: {e}")
            raise MetadataError(f"Metadata manager initialization failed: {e}")
    
    async def register_data_asset(
        self,
        asset_id: str,
        name: str,
        description: str,
        data_type: DataType,
        **metadata_kwargs
    ) -> DataAssetMetadata:
        """Register a new data asset"""
        asset_metadata = await self.catalog_manager.register_data_asset(
            asset_id, name, description, data_type, **metadata_kwargs
        )
        self.metrics["assets_registered"] += 1
        return asset_metadata
    
    async def create_schema(
        self,
        name: str,
        schema_type: SchemaType,
        definition: Dict[str, Any],
        description: Optional[str] = None
    ) -> DataSchema:
        """Create a new data schema"""
        schema = await self.schema_manager.create_schema(
            name, schema_type, definition, description
        )
        self.metrics["schemas_created"] += 1
        return schema
    
    async def create_business_term(
        self,
        name: str,
        definition: str,
        category: str,
        **term_kwargs
    ) -> BusinessGlossaryTerm:
        """Create a new business glossary term"""
        term = await self.glossary_manager.create_term(
            name, definition, category, **term_kwargs
        )
        self.metrics["terms_created"] += 1
        return term
    
    async def add_lineage_relationship(
        self,
        source_asset_id: str,
        target_asset_id: str,
        relationship_type: str,
        **lineage_kwargs
    ) -> MetadataLineage:
        """Add lineage relationship between assets"""
        lineage = await self.catalog_manager.add_lineage_relationship(
            source_asset_id, target_asset_id, relationship_type, **lineage_kwargs
        )
        self.metrics["lineage_relationships"] += 1
        return lineage
    
    async def search_catalog(
        self,
        query: str,
        **search_kwargs
    ) -> List[DataCatalogEntry]:
        """Search the data catalog"""
        results = await self.catalog_manager.search_catalog(query, **search_kwargs)
        self.metrics["catalog_searches"] += 1
        return results
    
    async def get_metadata_summary(self) -> Dict[str, Any]:
        """Get comprehensive metadata summary"""
        catalog_stats = await self.catalog_manager.get_catalog_statistics()
        
        return {
            "catalog_statistics": catalog_stats,
            "performance_metrics": self.metrics,
            "system_health": {
                "schema_coverage": (
                    catalog_stats["catalog_health"]["assets_with_schema"] /
                    max(catalog_stats["total_assets"], 1) * 100
                ),
                "ownership_coverage": (
                    catalog_stats["catalog_health"]["assets_with_owner"] /
                    max(catalog_stats["total_assets"], 1) * 100
                ),
                "description_coverage": (
                    catalog_stats["catalog_health"]["assets_with_description"] /
                    max(catalog_stats["total_assets"], 1) * 100
                )
            }
        }
