#!/usr/bin/env python3
"""
📊 Feature Lineage Tracker - Enterprise Data Lineage for ML Features
DBA Implementation - Comprehensive Feature Governance & Tracking

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise-grade feature lineage tracking with complete data governance,
impact analysis, and compliance monitoring for ML feature pipelines.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
import networkx as nx
import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import pickle
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class LineageEventType(Enum):
    """Types of lineage events"""
    FEATURE_CREATED = "feature_created"
    FEATURE_TRANSFORMED = "feature_transformed"
    FEATURE_COMBINED = "feature_combined"
    FEATURE_DELETED = "feature_deleted"
    DATA_SOURCE_ADDED = "data_source_added"
    MODEL_TRAINED = "model_trained"
    FEATURE_SELECTED = "feature_selected"
    QUALITY_CHECK = "quality_check"
    COMPLIANCE_AUDIT = "compliance_audit"

class DataSourceType(Enum):
    """Types of data sources"""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    STREAM = "stream"
    FEATURE_STORE = "feature_store"
    EXTERNAL_SERVICE = "external_service"
    USER_INPUT = "user_input"

class PrivacyLevel(Enum):
    """Privacy levels for data governance"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information

@dataclass
class DataSource:
    """Data source information"""
    source_id: str
    name: str
    source_type: DataSourceType
    location: str
    privacy_level: PrivacyLevel
    owner: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"
    retention_policy_days: int = 365
    encryption_enabled: bool = False
    backup_enabled: bool = True
    compliance_tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'source_id': self.source_id,
            'name': self.name,
            'source_type': self.source_type.value,
            'location': self.location,
            'privacy_level': self.privacy_level.value,
            'owner': self.owner,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'schema_version': self.schema_version,
            'retention_policy_days': self.retention_policy_days,
            'encryption_enabled': self.encryption_enabled,
            'backup_enabled': self.backup_enabled,
            'compliance_tags': self.compliance_tags
        }

@dataclass
class FeatureLineage:
    """Feature lineage information"""
    feature_id: str
    feature_name: str
    feature_type: str
    creator_type: str
    source_features: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    transformation_code: str = ""
    transformation_type: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    model_usage: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    compliance_status: str = "pending"
    business_context: str = ""
    documentation: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'feature_id': self.feature_id,
            'feature_name': self.feature_name,
            'feature_type': self.feature_type,
            'creator_type': self.creator_type,
            'source_features': self.source_features,
            'data_sources': self.data_sources,
            'transformation_code': self.transformation_code,
            'transformation_type': self.transformation_type,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'model_usage': self.model_usage,
            'quality_score': self.quality_score,
            'privacy_level': self.privacy_level.value,
            'compliance_status': self.compliance_status,
            'business_context': self.business_context,
            'documentation': self.documentation,
            'tags': self.tags
        }

@dataclass
class LineageEvent:
    """Lineage tracking event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: LineageEventType = LineageEventType.FEATURE_CREATED
    timestamp: datetime = field(default_factory=datetime.utcnow)
    feature_id: str = ""
    user_id: str = "system"
    details: Dict[str, Any] = field(default_factory=dict)
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    compliance_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'feature_id': self.feature_id,
            'user_id': self.user_id,
            'details': self.details,
            'impact_analysis': self.impact_analysis,
            'compliance_notes': self.compliance_notes
        }

@dataclass
class LineageConfig:
    """Configuration for lineage tracking"""
    database_path: str = "ml_lineage.db"
    enable_graph_analysis: bool = True
    enable_compliance_monitoring: bool = True
    enable_impact_analysis: bool = True
    retention_days: int = 365
    max_lineage_depth: int = 50
    enable_encryption: bool = True
    backup_frequency_hours: int = 24
    audit_log_level: str = "INFO"

class FeatureLineageTracker:
    """
    📊 Enterprise Feature Lineage Tracker
    
    Comprehensive data lineage tracking for ML features with governance,
    compliance monitoring, and impact analysis capabilities.
    """
    
    def __init__(self, config: LineageConfig):
        self.config = config
        self.db_path = Path(config.database_path)
        self.lineage_graph = nx.DiGraph()
        self.data_sources: Dict[str, DataSource] = {}
        self.feature_lineages: Dict[str, FeatureLineage] = {}
        self.events: List[LineageEvent] = []
        self.locks = {
            'db': threading.Lock(),
            'graph': threading.Lock(),
            'events': threading.Lock()
        }
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Start background tasks
        asyncio.create_task(self._background_maintenance())
        
        logger.info(f"📊 Feature Lineage Tracker initialized with database: {config.database_path}")
    
    async def _initialize_database(self):
        """Initialize SQLite database for lineage storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Data sources table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_sources (
                        source_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        source_type TEXT NOT NULL,
                        location TEXT NOT NULL,
                        privacy_level TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        schema_version TEXT,
                        retention_policy_days INTEGER,
                        encryption_enabled BOOLEAN,
                        backup_enabled BOOLEAN,
                        compliance_tags TEXT
                    )
                """)
                
                # Feature lineages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feature_lineages (
                        feature_id TEXT PRIMARY KEY,
                        feature_name TEXT NOT NULL,
                        feature_type TEXT NOT NULL,
                        creator_type TEXT NOT NULL,
                        source_features TEXT,
                        data_sources TEXT,
                        transformation_code TEXT,
                        transformation_type TEXT,
                        created_at TEXT NOT NULL,
                        created_by TEXT,
                        model_usage TEXT,
                        quality_score REAL,
                        privacy_level TEXT,
                        compliance_status TEXT,
                        business_context TEXT,
                        documentation TEXT,
                        tags TEXT
                    )
                """)
                
                # Lineage events table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lineage_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        feature_id TEXT,
                        user_id TEXT,
                        details TEXT,
                        impact_analysis TEXT,
                        compliance_notes TEXT
                    )
                """)
                
                # Lineage relationships table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lineage_relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parent_feature_id TEXT NOT NULL,
                        child_feature_id TEXT NOT NULL,
                        relationship_type TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        created_at TEXT NOT NULL,
                        UNIQUE(parent_feature_id, child_feature_id)
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feature_lineages_creator_type ON feature_lineages(creator_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_lineage_events_timestamp ON lineage_events(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_lineage_events_feature_id ON lineage_events(feature_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_lineage_relationships_parent ON lineage_relationships(parent_feature_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_lineage_relationships_child ON lineage_relationships(child_feature_id)")
                
                conn.commit()
                
            logger.info("✅ Lineage database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize lineage database: {str(e)}")
            raise
    
    async def register_data_source(
        self,
        name: str,
        source_type: DataSourceType,
        location: str,
        privacy_level: PrivacyLevel,
        owner: str,
        **kwargs
    ) -> str:
        """
        Register a new data source
        
        Args:
            name: Human-readable name
            source_type: Type of data source
            location: Source location/URI
            privacy_level: Privacy classification
            owner: Owner/responsible person
            **kwargs: Additional source metadata
            
        Returns:
            Source ID
        """
        source_id = str(uuid.uuid4())
        
        data_source = DataSource(
            source_id=source_id,
            name=name,
            source_type=source_type,
            location=location,
            privacy_level=privacy_level,
            owner=owner,
            **{k: v for k, v in kwargs.items() if hasattr(DataSource, k)}
        )
        
        self.data_sources[source_id] = data_source
        
        # Persist to database
        await self._persist_data_source(data_source)
        
        # Log event
        await self._log_event(LineageEvent(
            event_type=LineageEventType.DATA_SOURCE_ADDED,
            details={
                'source_id': source_id,
                'name': name,
                'source_type': source_type.value,
                'privacy_level': privacy_level.value
            }
        ))
        
        logger.info(f"📍 Registered data source: {name} ({source_id})")
        return source_id
    
    async def track_feature_creation(
        self,
        feature_name: str,
        feature_type: str,
        creator_type: str,
        source_features: List[str] = None,
        data_sources: List[str] = None,
        transformation_code: str = "",
        transformation_type: str = "",
        created_by: str = "system",
        privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
        business_context: str = "",
        documentation: str = "",
        tags: List[str] = None
    ) -> str:
        """
        Track the creation of a new feature
        
        Args:
            feature_name: Name of the feature
            feature_type: Type of feature (numerical, categorical, etc.)
            creator_type: Type of creator (musician, blogger, etc.)
            source_features: List of source feature IDs
            data_sources: List of data source IDs
            transformation_code: Code used for transformation
            transformation_type: Type of transformation applied
            created_by: User who created the feature
            privacy_level: Privacy classification
            business_context: Business context/purpose
            documentation: Feature documentation
            tags: Feature tags
            
        Returns:
            Feature ID
        """
        feature_id = str(uuid.uuid4())
        
        lineage = FeatureLineage(
            feature_id=feature_id,
            feature_name=feature_name,
            feature_type=feature_type,
            creator_type=creator_type,
            source_features=source_features or [],
            data_sources=data_sources or [],
            transformation_code=transformation_code,
            transformation_type=transformation_type,
            created_by=created_by,
            privacy_level=privacy_level,
            business_context=business_context,
            documentation=documentation,
            tags=tags or []
        )
        
        self.feature_lineages[feature_id] = lineage
        
        # Update lineage graph
        await self._update_lineage_graph(lineage)
        
        # Persist to database
        await self._persist_feature_lineage(lineage)
        
        # Log creation event
        await self._log_event(LineageEvent(
            event_type=LineageEventType.FEATURE_CREATED,
            feature_id=feature_id,
            user_id=created_by,
            details={
                'feature_name': feature_name,
                'feature_type': feature_type,
                'creator_type': creator_type,
                'transformation_type': transformation_type,
                'source_count': len(source_features) if source_features else 0
            }
        ))
        
        # Perform compliance check
        if self.config.enable_compliance_monitoring:
            await self._perform_compliance_check(feature_id)
        
        logger.info(f"🔍 Tracked feature creation: {feature_name} ({feature_id})")
        return feature_id
    
    async def track_feature_transformation(
        self,
        source_feature_id: str,
        new_feature_name: str,
        transformation_code: str,
        transformation_type: str,
        created_by: str = "system",
        additional_metadata: Dict[str, Any] = None
    ) -> str:
        """
        Track feature transformation from existing feature
        
        Args:
            source_feature_id: ID of source feature
            new_feature_name: Name of transformed feature
            transformation_code: Transformation code
            transformation_type: Type of transformation
            created_by: User performing transformation
            additional_metadata: Additional metadata
            
        Returns:
            New feature ID
        """
        if source_feature_id not in self.feature_lineages:
            raise ValueError(f"Source feature {source_feature_id} not found")
        
        source_lineage = self.feature_lineages[source_feature_id]
        
        # Create new feature with inherited properties
        new_feature_id = await self.track_feature_creation(
            feature_name=new_feature_name,
            feature_type=source_lineage.feature_type,
            creator_type=source_lineage.creator_type,
            source_features=[source_feature_id],
            data_sources=source_lineage.data_sources,
            transformation_code=transformation_code,
            transformation_type=transformation_type,
            created_by=created_by,
            privacy_level=source_lineage.privacy_level,
            tags=source_lineage.tags
        )
        
        # Log transformation event
        await self._log_event(LineageEvent(
            event_type=LineageEventType.FEATURE_TRANSFORMED,
            feature_id=new_feature_id,
            user_id=created_by,
            details={
                'source_feature_id': source_feature_id,
                'transformation_type': transformation_type,
                'new_feature_name': new_feature_name,
                **(additional_metadata or {})
            }
        ))
        
        logger.info(f"🔄 Tracked feature transformation: {source_lineage.feature_name} -> {new_feature_name}")
        return new_feature_id
    
    async def track_feature_combination(
        self,
        source_feature_ids: List[str],
        new_feature_name: str,
        combination_type: str,
        transformation_code: str,
        created_by: str = "system"
    ) -> str:
        """
        Track feature combination from multiple source features
        
        Args:
            source_feature_ids: List of source feature IDs
            new_feature_name: Name of combined feature
            combination_type: Type of combination
            transformation_code: Combination code
            created_by: User performing combination
            
        Returns:
            New feature ID
        """
        # Validate source features exist
        for feature_id in source_feature_ids:
            if feature_id not in self.feature_lineages:
                raise ValueError(f"Source feature {feature_id} not found")
        
        # Determine combined properties
        source_lineages = [self.feature_lineages[fid] for fid in source_feature_ids]
        
        # Use most restrictive privacy level
        privacy_levels = [lineage.privacy_level for lineage in source_lineages]
        combined_privacy = max(privacy_levels, key=lambda x: list(PrivacyLevel).index(x))
        
        # Combine data sources
        combined_data_sources = list(set(
            ds for lineage in source_lineages for ds in lineage.data_sources
        ))
        
        # Combine tags
        combined_tags = list(set(
            tag for lineage in source_lineages for tag in lineage.tags
        ))
        
        # Create combined feature
        new_feature_id = await self.track_feature_creation(
            feature_name=new_feature_name,
            feature_type="synthetic",  # Combined features are synthetic
            creator_type=source_lineages[0].creator_type,  # Use first creator type
            source_features=source_feature_ids,
            data_sources=combined_data_sources,
            transformation_code=transformation_code,
            transformation_type=combination_type,
            created_by=created_by,
            privacy_level=combined_privacy,
            tags=combined_tags
        )
        
        # Log combination event
        await self._log_event(LineageEvent(
            event_type=LineageEventType.FEATURE_COMBINED,
            feature_id=new_feature_id,
            user_id=created_by,
            details={
                'source_feature_ids': source_feature_ids,
                'combination_type': combination_type,
                'source_count': len(source_feature_ids)
            }
        ))
        
        logger.info(f"🔗 Tracked feature combination: {len(source_feature_ids)} features -> {new_feature_name}")
        return new_feature_id
    
    async def get_feature_lineage(
        self,
        feature_id: str,
        include_downstream: bool = True,
        max_depth: int = None
    ) -> Dict[str, Any]:
        """
        Get complete lineage for a feature
        
        Args:
            feature_id: Feature ID to trace
            include_downstream: Include downstream dependencies
            max_depth: Maximum depth to trace
            
        Returns:
            Complete lineage information
        """
        if feature_id not in self.feature_lineages:
            raise ValueError(f"Feature {feature_id} not found")
        
        max_depth = max_depth or self.config.max_lineage_depth
        
        # Get upstream lineage (parents)
        upstream_lineage = await self._trace_upstream_lineage(feature_id, max_depth)
        
        # Get downstream lineage (children) if requested
        downstream_lineage = {}
        if include_downstream:
            downstream_lineage = await self._trace_downstream_lineage(feature_id, max_depth)
        
        # Get feature events
        feature_events = [
            event.to_dict() for event in self.events
            if event.feature_id == feature_id
        ]
        
        # Get impact analysis
        impact_analysis = await self._analyze_feature_impact(feature_id)
        
        lineage_info = {
            'feature': self.feature_lineages[feature_id].to_dict(),
            'upstream_lineage': upstream_lineage,
            'downstream_lineage': downstream_lineage,
            'events': feature_events,
            'impact_analysis': impact_analysis,
            'lineage_metadata': {
                'traced_at': datetime.utcnow().isoformat(),
                'max_depth_used': max_depth,
                'total_upstream_features': len(upstream_lineage),
                'total_downstream_features': len(downstream_lineage)
            }
        }
        
        return lineage_info
    
    async def _trace_upstream_lineage(
        self,
        feature_id: str,
        max_depth: int,
        current_depth: int = 0,
        visited: Set[str] = None
    ) -> Dict[str, Any]:
        """Recursively trace upstream lineage"""
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or feature_id in visited:
            return {}
        
        visited.add(feature_id)
        upstream = {}
        
        if feature_id in self.feature_lineages:
            lineage = self.feature_lineages[feature_id]
            
            for source_id in lineage.source_features:
                upstream[source_id] = {
                    'feature': self.feature_lineages.get(source_id, {}).to_dict() if source_id in self.feature_lineages else {},
                    'relationship': 'direct_parent',
                    'depth': current_depth + 1,
                    'upstream': await self._trace_upstream_lineage(
                        source_id, max_depth, current_depth + 1, visited.copy()
                    )
                }
        
        return upstream
    
    async def _trace_downstream_lineage(
        self,
        feature_id: str,
        max_depth: int,
        current_depth: int = 0,
        visited: Set[str] = None
    ) -> Dict[str, Any]:
        """Recursively trace downstream lineage"""
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or feature_id in visited:
            return {}
        
        visited.add(feature_id)
        downstream = {}
        
        # Find features that use this feature as source
        for child_id, child_lineage in self.feature_lineages.items():
            if feature_id in child_lineage.source_features:
                downstream[child_id] = {
                    'feature': child_lineage.to_dict(),
                    'relationship': 'direct_child',
                    'depth': current_depth + 1,
                    'downstream': await self._trace_downstream_lineage(
                        child_id, max_depth, current_depth + 1, visited.copy()
                    )
                }
        
        return downstream
    
    async def _analyze_feature_impact(self, feature_id: str) -> Dict[str, Any]:
        """Analyze impact of feature changes"""
        if feature_id not in self.feature_lineages:
            return {}
        
        lineage = self.feature_lineages[feature_id]
        
        # Count direct and indirect dependencies
        downstream_features = await self._get_all_downstream_features(feature_id)
        
        # Count model usage
        models_using_feature = len(lineage.model_usage)
        
        # Analyze privacy implications
        privacy_impact = await self._analyze_privacy_impact(feature_id)
        
        # Calculate business impact score
        business_impact_score = await self._calculate_business_impact_score(feature_id)
        
        impact_analysis = {
            'directly_dependent_features': len([
                f for f in self.feature_lineages.values()
                if feature_id in f.source_features
            ]),
            'total_downstream_features': len(downstream_features),
            'models_using_feature': models_using_feature,
            'privacy_impact': privacy_impact,
            'business_impact_score': business_impact_score,
            'data_sources_affected': len(lineage.data_sources),
            'compliance_implications': await self._analyze_compliance_implications(feature_id)
        }
        
        return impact_analysis
    
    async def _get_all_downstream_features(
        self,
        feature_id: str,
        visited: Set[str] = None
    ) -> Set[str]:
        """Get all downstream features recursively"""
        if visited is None:
            visited = set()
        
        if feature_id in visited:
            return set()
        
        visited.add(feature_id)
        downstream = set()
        
        for child_id, child_lineage in self.feature_lineages.items():
            if feature_id in child_lineage.source_features:
                downstream.add(child_id)
                downstream.update(await self._get_all_downstream_features(child_id, visited.copy()))
        
        return downstream
    
    async def _analyze_privacy_impact(self, feature_id: str) -> Dict[str, Any]:
        """Analyze privacy implications of feature"""
        if feature_id not in self.feature_lineages:
            return {}
        
        lineage = self.feature_lineages[feature_id]
        
        # Check if feature contains PII
        contains_pii = lineage.privacy_level == PrivacyLevel.PII
        
        # Check if any source data contains PII
        source_pii_risk = any(
            self.data_sources.get(ds_id, DataSource("", "", DataSourceType.DATABASE, "", PrivacyLevel.PUBLIC, "")).privacy_level == PrivacyLevel.PII
            for ds_id in lineage.data_sources
        )
        
        return {
            'contains_pii': contains_pii,
            'source_pii_risk': source_pii_risk,
            'privacy_level': lineage.privacy_level.value,
            'requires_anonymization': contains_pii or source_pii_risk,
            'gdpr_applicable': contains_pii or source_pii_risk
        }
    
    async def _calculate_business_impact_score(self, feature_id: str) -> float:
        """Calculate business impact score for feature"""
        if feature_id not in self.feature_lineages:
            return 0.0
        
        lineage = self.feature_lineages[feature_id]
        
        # Base score components
        model_usage_score = min(len(lineage.model_usage) * 0.2, 1.0)
        quality_score = lineage.quality_score
        downstream_count = len(await self._get_all_downstream_features(feature_id))
        dependency_score = min(downstream_count * 0.1, 1.0)
        
        # Calculate weighted score
        business_impact = (
            model_usage_score * 0.4 +
            quality_score * 0.3 +
            dependency_score * 0.3
        )
        
        return round(business_impact, 3)
    
    async def _analyze_compliance_implications(self, feature_id: str) -> Dict[str, Any]:
        """Analyze compliance implications"""
        if feature_id not in self.feature_lineages:
            return {}
        
        lineage = self.feature_lineages[feature_id]
        
        implications = {
            'gdpr_relevant': lineage.privacy_level in [PrivacyLevel.PII, PrivacyLevel.RESTRICTED],
            'retention_required': True,
            'audit_trail_complete': bool(lineage.documentation),
            'data_subject_rights_applicable': lineage.privacy_level == PrivacyLevel.PII,
            'compliance_status': lineage.compliance_status,
            'required_actions': []
        }
        
        # Add required actions based on analysis
        if implications['gdpr_relevant'] and not implications['audit_trail_complete']:
            implications['required_actions'].append('Complete documentation for GDPR compliance')
        
        if lineage.privacy_level == PrivacyLevel.PII and not any('encryption' in tag for tag in lineage.tags):
            implications['required_actions'].append('Implement encryption for PII data')
        
        return implications
    
    async def _update_lineage_graph(self, lineage: FeatureLineage):
        """Update networkx graph with lineage relationships"""
        with self.locks['graph']:
            # Add feature node
            self.lineage_graph.add_node(
                lineage.feature_id,
                name=lineage.feature_name,
                feature_type=lineage.feature_type,
                creator_type=lineage.creator_type,
                privacy_level=lineage.privacy_level.value,
                created_at=lineage.created_at.isoformat()
            )
            
            # Add edges from source features
            for source_id in lineage.source_features:
                if source_id in self.feature_lineages:
                    self.lineage_graph.add_edge(
                        source_id,
                        lineage.feature_id,
                        relationship_type='derives_from',
                        transformation_type=lineage.transformation_type
                    )
            
            # Add edges from data sources
            for source_id in lineage.data_sources:
                if source_id in self.data_sources:
                    self.lineage_graph.add_edge(
                        f"ds_{source_id}",
                        lineage.feature_id,
                        relationship_type='sourced_from',
                        source_type='data_source'
                    )
    
    async def _persist_data_source(self, data_source: DataSource):
        """Persist data source to database"""
        with self.locks['db']:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO data_sources 
                        (source_id, name, source_type, location, privacy_level, owner, 
                         created_at, last_updated, schema_version, retention_policy_days,
                         encryption_enabled, backup_enabled, compliance_tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data_source.source_id,
                        data_source.name,
                        data_source.source_type.value,
                        data_source.location,
                        data_source.privacy_level.value,
                        data_source.owner,
                        data_source.created_at.isoformat(),
                        data_source.last_updated.isoformat(),
                        data_source.schema_version,
                        data_source.retention_policy_days,
                        data_source.encryption_enabled,
                        data_source.backup_enabled,
                        json.dumps(data_source.compliance_tags)
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"❌ Failed to persist data source: {str(e)}")
    
    async def _persist_feature_lineage(self, lineage: FeatureLineage):
        """Persist feature lineage to database"""
        with self.locks['db']:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO feature_lineages 
                        (feature_id, feature_name, feature_type, creator_type, source_features,
                         data_sources, transformation_code, transformation_type, created_at,
                         created_by, model_usage, quality_score, privacy_level, compliance_status,
                         business_context, documentation, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lineage.feature_id,
                        lineage.feature_name,
                        lineage.feature_type,
                        lineage.creator_type,
                        json.dumps(lineage.source_features),
                        json.dumps(lineage.data_sources),
                        lineage.transformation_code,
                        lineage.transformation_type,
                        lineage.created_at.isoformat(),
                        lineage.created_by,
                        json.dumps(lineage.model_usage),
                        lineage.quality_score,
                        lineage.privacy_level.value,
                        lineage.compliance_status,
                        lineage.business_context,
                        lineage.documentation,
                        json.dumps(lineage.tags)
                    ))
                    
                    # Store relationships
                    for source_id in lineage.source_features:
                        cursor.execute("""
                            INSERT OR REPLACE INTO lineage_relationships
                            (parent_feature_id, child_feature_id, relationship_type, created_at)
                            VALUES (?, ?, ?, ?)
                        """, (
                            source_id,
                            lineage.feature_id,
                            'derives_from',
                            lineage.created_at.isoformat()
                        ))
                    
                    conn.commit()
            except Exception as e:
                logger.error(f"❌ Failed to persist feature lineage: {str(e)}")
    
    async def _log_event(self, event: LineageEvent):
        """Log lineage event"""
        with self.locks['events']:
            self.events.append(event)
            
            # Persist to database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO lineage_events 
                        (event_id, event_type, timestamp, feature_id, user_id, 
                         details, impact_analysis, compliance_notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.event_id,
                        event.event_type.value,
                        event.timestamp.isoformat(),
                        event.feature_id,
                        event.user_id,
                        json.dumps(event.details),
                        json.dumps(event.impact_analysis),
                        event.compliance_notes
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"❌ Failed to log event: {str(e)}")
    
    async def _perform_compliance_check(self, feature_id: str):
        """Perform automated compliance check"""
        if feature_id not in self.feature_lineages:
            return
        
        lineage = self.feature_lineages[feature_id]
        compliance_issues = []
        
        # Check documentation completeness
        if not lineage.documentation:
            compliance_issues.append("Missing feature documentation")
        
        # Check PII handling
        if lineage.privacy_level == PrivacyLevel.PII:
            if not any('encryption' in tag for tag in lineage.tags):
                compliance_issues.append("PII feature lacks encryption tag")
        
        # Check data source compliance
        for ds_id in lineage.data_sources:
            if ds_id in self.data_sources:
                ds = self.data_sources[ds_id]
                if ds.privacy_level == PrivacyLevel.PII and not ds.encryption_enabled:
                    compliance_issues.append(f"Data source {ds.name} contains PII without encryption")
        
        # Update compliance status
        if not compliance_issues:
            lineage.compliance_status = "compliant"
        else:
            lineage.compliance_status = "non_compliant"
        
        # Log compliance check event
        await self._log_event(LineageEvent(
            event_type=LineageEventType.COMPLIANCE_AUDIT,
            feature_id=feature_id,
            details={
                'compliance_status': lineage.compliance_status,
                'issues_found': len(compliance_issues),
                'issues': compliance_issues
            },
            compliance_notes='; '.join(compliance_issues) if compliance_issues else "No issues found"
        ))
    
    async def _background_maintenance(self):
        """Background maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean old events
                if self.config.retention_days > 0:
                    cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
                    self.events = [e for e in self.events if e.timestamp > cutoff_date]
                
                # Perform compliance checks on new features
                for feature_id, lineage in self.feature_lineages.items():
                    if lineage.compliance_status == "pending":
                        await self._perform_compliance_check(feature_id)
                
                logger.debug("🔧 Lineage background maintenance completed")
                
            except Exception as e:
                logger.error(f"❌ Background maintenance error: {str(e)}")
    
    async def get_compliance_report(
        self,
        creator_type: Optional[str] = None,
        privacy_level: Optional[PrivacyLevel] = None
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        features_to_analyze = self.feature_lineages.values()
        
        if creator_type:
            features_to_analyze = [f for f in features_to_analyze if f.creator_type == creator_type]
        
        if privacy_level:
            features_to_analyze = [f for f in features_to_analyze if f.privacy_level == privacy_level]
        
        compliant_count = sum(1 for f in features_to_analyze if f.compliance_status == "compliant")
        total_count = len(list(features_to_analyze))
        
        compliance_report = {
            'report_timestamp': datetime.utcnow().isoformat(),
            'filters': {
                'creator_type': creator_type,
                'privacy_level': privacy_level.value if privacy_level else None
            },
            'summary': {
                'total_features': total_count,
                'compliant_features': compliant_count,
                'non_compliant_features': total_count - compliant_count,
                'compliance_rate': (compliant_count / total_count * 100) if total_count > 0 else 0
            },
            'compliance_by_creator_type': {},
            'privacy_level_distribution': {},
            'common_compliance_issues': await self._get_common_compliance_issues()
        }
        
        # Analyze by creator type
        creator_types = set(f.creator_type for f in features_to_analyze)
        for ct in creator_types:
            ct_features = [f for f in features_to_analyze if f.creator_type == ct]
            ct_compliant = sum(1 for f in ct_features if f.compliance_status == "compliant")
            compliance_report['compliance_by_creator_type'][ct] = {
                'total': len(ct_features),
                'compliant': ct_compliant,
                'compliance_rate': (ct_compliant / len(ct_features) * 100) if ct_features else 0
            }
        
        # Analyze by privacy level
        privacy_levels = set(f.privacy_level for f in features_to_analyze)
        for pl in privacy_levels:
            pl_features = [f for f in features_to_analyze if f.privacy_level == pl]
            pl_compliant = sum(1 for f in pl_features if f.compliance_status == "compliant")
            compliance_report['privacy_level_distribution'][pl.value] = {
                'total': len(pl_features),
                'compliant': pl_compliant,
                'compliance_rate': (pl_compliant / len(pl_features) * 100) if pl_features else 0
            }
        
        return compliance_report
    
    async def _get_common_compliance_issues(self) -> List[Dict[str, Any]]:
        """Get most common compliance issues"""
        issue_counts = defaultdict(int)
        
        # Analyze compliance events
        compliance_events = [e for e in self.events if e.event_type == LineageEventType.COMPLIANCE_AUDIT]
        
        for event in compliance_events:
            if 'issues' in event.details:
                for issue in event.details['issues']:
                    issue_counts[issue] += 1
        
        # Return sorted by frequency
        common_issues = [
            {'issue': issue, 'frequency': count}
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return common_issues[:10]  # Top 10 issues
    
    def export_lineage_graph(self, output_path: str, format: str = "graphml") -> str:
        """Export lineage graph to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self.locks['graph']:
            if format.lower() == "graphml":
                nx.write_graphml(self.lineage_graph, output_file)
            elif format.lower() == "gexf":
                nx.write_gexf(self.lineage_graph, output_file)
            elif format.lower() == "json":
                graph_data = nx.node_link_data(self.lineage_graph)
                with open(output_file, 'w') as f:
                    json.dump(graph_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"📊 Exported lineage graph to {output_path}")
        return str(output_file)
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get comprehensive lineage tracking summary"""
        return {
            "feature_lineage_tracker": "v1.0",
            "database": str(self.db_path),
            "statistics": {
                "total_features": len(self.feature_lineages),
                "total_data_sources": len(self.data_sources),
                "total_events": len(self.events),
                "graph_nodes": self.lineage_graph.number_of_nodes(),
                "graph_edges": self.lineage_graph.number_of_edges()
            },
            "compliance_overview": {
                "compliant_features": sum(
                    1 for f in self.feature_lineages.values() 
                    if f.compliance_status == "compliant"
                ),
                "pending_compliance": sum(
                    1 for f in self.feature_lineages.values() 
                    if f.compliance_status == "pending"
                ),
                "non_compliant_features": sum(
                    1 for f in self.feature_lineages.values() 
                    if f.compliance_status == "non_compliant"
                )
            },
            "creator_type_distribution": {
                creator_type: sum(
                    1 for f in self.feature_lineages.values()
                    if f.creator_type == creator_type
                )
                for creator_type in set(f.creator_type for f in self.feature_lineages.values())
            }
        }

async def main():
    """Example usage of Feature Lineage Tracker"""
    # Initialize tracker
    config = LineageConfig(
        database_path="/tmp/ml_lineage.db",
        enable_compliance_monitoring=True,
        enable_impact_analysis=True
    )
    tracker = FeatureLineageTracker(config)
    
    # Register data source
    audio_source_id = await tracker.register_data_source(
        name="Spotify Audio Features",
        source_type=DataSourceType.API,
        location="https://api.spotify.com/v1/audio-features",
        privacy_level=PrivacyLevel.INTERNAL,
        owner="data-team@company.com"
    )
    
    # Track feature creation
    base_feature_id = await tracker.track_feature_creation(
        feature_name="audio_tempo",
        feature_type="numerical",
        creator_type="musician",
        data_sources=[audio_source_id],
        transformation_code="librosa.beat.beat_track(y=audio)[0]",
        transformation_type="audio_analysis",
        business_context="Track tempo for music recommendation",
        documentation="Tempo extracted from audio using librosa"
    )
    
    # Track feature transformation
    transformed_feature_id = await tracker.track_feature_transformation(
        source_feature_id=base_feature_id,
        new_feature_name="tempo_category",
        transformation_code="np.where(tempo < 100, 'slow', np.where(tempo < 140, 'medium', 'fast'))",
        transformation_type="binning"
    )
    
    # Get lineage information
    lineage_info = await tracker.get_feature_lineage(
        feature_id=transformed_feature_id,
        include_downstream=True
    )
    
    print(f"📊 Feature Lineage: {json.dumps(lineage_info, indent=2)}")
    
    # Generate compliance report
    compliance_report = await tracker.get_compliance_report()
    print(f"📋 Compliance Report: {json.dumps(compliance_report, indent=2)}")
    
    # Export lineage graph
    graph_file = tracker.export_lineage_graph("/tmp/lineage_graph.json", "json")
    print(f"📈 Lineage graph exported to: {graph_file}")
    
    # Get summary
    summary = tracker.get_lineage_summary()
    print(f"📊 Lineage Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())