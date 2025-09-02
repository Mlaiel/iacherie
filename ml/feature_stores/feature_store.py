"""
Centralized Feature Store with Versioning
Implements a comprehensive feature store for ML feature management
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import logging
from pathlib import Path
import sqlite3
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Types of features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TEXT = "text"
    DATETIME = "datetime"
    EMBEDDING = "embedding"


class ComputeMode(Enum):
    """Feature computation modes"""
    BATCH = "batch"
    STREAMING = "streaming"
    ON_DEMAND = "on_demand"


class FeatureStatus(Enum):
    """Feature status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"


@dataclass
class FeatureSchema:
    """Schema definition for a feature"""
    name: str
    feature_type: FeatureType
    description: str
    data_type: str  # pandas dtype
    nullable: bool = True
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureGroup:
    """Group of related features"""
    name: str
    description: str
    features: List[FeatureSchema]
    version: str
    status: FeatureStatus = FeatureStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    compute_mode: ComputeMode = ComputeMode.BATCH
    refresh_frequency: Optional[str] = None  # e.g., "1h", "1d", "1w"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureValue:
    """A feature value with metadata"""
    feature_name: str
    entity_id: str
    value: Any
    timestamp: datetime
    version: str
    metadata: Optional[Dict[str, Any]] = None


class FeatureStore(ABC):
    """Abstract base class for feature stores"""
    
    @abstractmethod
    def create_feature_group(self, feature_group: FeatureGroup) -> bool:
        try:
            logger.info(f"Executing create_feature_group")
            
            # Implementation for create_feature_group
            # TODO: Add specific business logic here
        try:
                    # Request validation
                    if not name:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_feature_group_request(name)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
            logger.info(f"Executing read_features")
            
            # Implementation for read_features
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"read_features completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"read_features failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"write_features failed: {e}")
            raise
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_feature_group failed: {e}")
                    return {"status": "error", "message": str(e)}
            logger.info(f"create_feature_group completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"create_feature_group failed: {e}")
            raise
    @abstractmethod
    def get_feature_group(self, name: str, version: Optional[str] = None) -> Optional[FeatureGroup]:
        """Get a feature group"""
        pass
    
    @abstractmethod
    def write_features(self, feature_group_name: str, features_df: pd.DataFrame, version: str) -> bool:
        """Write features to the store"""
        pass
    
    @abstractmethod
    def read_features(
        self,
        feature_group_name: str,
        feature_names: Optional[List[str]] = None,
        entity_ids: Optional[List[str]] = None,
        version: Optional[str] = None,
        timestamp_range: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """Read features from the store"""
        pass


class SQLiteFeatureStore(FeatureStore):
    """SQLite-based feature store implementation"""
    
    def __init__(self, db_path: str = "feature_store.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Create tables
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_groups (
                name TEXT,
                version TEXT,
                description TEXT,
                schema_json TEXT,
                status TEXT,
                created_at TEXT,
                created_by TEXT,
                compute_mode TEXT,
                refresh_frequency TEXT,
                dependencies_json TEXT,
                tags_json TEXT,
                metadata_json TEXT,
                PRIMARY KEY (name, version)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_values (
                feature_group_name TEXT,
                feature_name TEXT,
                entity_id TEXT,
                value TEXT,
                value_type TEXT,
                timestamp TEXT,
                version TEXT,
                metadata_json TEXT,
                PRIMARY KEY (feature_group_name, feature_name, entity_id, version, timestamp)
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_values_lookup 
            ON feature_values(feature_group_name, entity_id, version, timestamp)
        """)
        
        self.conn.commit()
        logger.info(f"Initialized SQLite feature store at {self.db_path}")
    
    def create_feature_group(self, feature_group: FeatureGroup) -> bool:
        """Create a new feature group"""
        try:
            schema_json = json.dumps([f.__dict__ for f in feature_group.features], default=str)
            
            self.conn.execute("""
                INSERT OR REPLACE INTO feature_groups 
                (name, version, description, schema_json, status, created_at, created_by, 
                 compute_mode, refresh_frequency, dependencies_json, tags_json, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feature_group.name,
                feature_group.version,
                feature_group.description,
                schema_json,
                feature_group.status.value,
                feature_group.created_at.isoformat(),
                feature_group.created_by,
                feature_group.compute_mode.value,
                feature_group.refresh_frequency,
                json.dumps(feature_group.dependencies),
                json.dumps(feature_group.tags),
                json.dumps(feature_group.metadata, default=str)
            ))
            
            self.conn.commit()
            logger.info(f"Created feature group {feature_group.name} v{feature_group.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating feature group: {str(e)}")
            return False
    
    def get_feature_group(self, name: str, version: Optional[str] = None) -> Optional[FeatureGroup]:
        """Get a feature group"""
        try:
            if version:
                cursor = self.conn.execute(
                    "SELECT * FROM feature_groups WHERE name = ? AND version = ?",
                    (name, version)
                )
            else:
                # Get latest version
                cursor = self.conn.execute(
                    "SELECT * FROM feature_groups WHERE name = ? ORDER BY created_at DESC LIMIT 1",
                    (name,)
                )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse the row data
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
            
            # Reconstruct feature schemas
            features_data = json.loads(data['schema_json'])
            features = []
            for f_data in features_data:
                feature = FeatureSchema(
                    name=f_data['name'],
                    feature_type=FeatureType(f_data['feature_type']),
                    description=f_data['description'],
                    data_type=f_data['data_type'],
                    nullable=f_data.get('nullable', True),
                    default_value=f_data.get('default_value'),
                    validation_rules=f_data.get('validation_rules'),
                    tags=f_data.get('tags', []),
                    metadata=f_data.get('metadata', {})
                )
                features.append(feature)
            
            feature_group = FeatureGroup(
                name=data['name'],
                description=data['description'],
                features=features,
                version=data['version'],
                status=FeatureStatus(data['status']),
                created_at=datetime.fromisoformat(data['created_at']),
                created_by=data['created_by'],
                compute_mode=ComputeMode(data['compute_mode']),
                refresh_frequency=data['refresh_frequency'],
                dependencies=json.loads(data['dependencies_json']),
                tags=json.loads(data['tags_json']),
                metadata=json.loads(data['metadata_json'])
            )
            
            return feature_group
            
        except Exception as e:
            logger.error(f"Error getting feature group: {str(e)}")
            return None
    
    def write_features(self, feature_group_name: str, features_df: pd.DataFrame, version: str) -> bool:
        """Write features to the store"""
        try:
            timestamp = datetime.now().isoformat()
            
            for idx, row in features_df.iterrows():
                entity_id = str(row.get('entity_id', idx))
                
                for feature_name in features_df.columns:
                    if feature_name == 'entity_id':
                        continue
                    
                    value = row[feature_name]
                    value_type = str(type(value).__name__)
                    
                    # Convert value to string for storage
                    if pd.isna(value):
                        value_str = None
                    elif isinstance(value, (list, dict)):
                        value_str = json.dumps(value, default=str)
                    else:
                        value_str = str(value)
                    
                    self.conn.execute("""
                        INSERT OR REPLACE INTO feature_values 
                        (feature_group_name, feature_name, entity_id, value, value_type, 
                         timestamp, version, metadata_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        feature_group_name,
                        feature_name,
                        entity_id,
                        value_str,
                        value_type,
                        timestamp,
                        version,
                        json.dumps({})
                    ))
            
            self.conn.commit()
            logger.info(f"Written {len(features_df)} rows to feature group {feature_group_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing features: {str(e)}")
            return False
    
    def read_features(
        self,
        feature_group_name: str,
        feature_names: Optional[List[str]] = None,
        entity_ids: Optional[List[str]] = None,
        version: Optional[str] = None,
        timestamp_range: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """Read features from the store"""
        try:
            # Build query
            query = "SELECT * FROM feature_values WHERE feature_group_name = ?"
            params = [feature_group_name]
            
            if feature_names:
                placeholders = ','.join(['?'] * len(feature_names))
                query += f" AND feature_name IN ({placeholders})"
                params.extend(feature_names)
            
            if entity_ids:
                placeholders = ','.join(['?'] * len(entity_ids))
                query += f" AND entity_id IN ({placeholders})"
                params.extend(entity_ids)
            
            if version:
                query += " AND version = ?"
                params.append(version)
            else:
                # Get latest version for each feature/entity combination
                query = f"""
                    SELECT * FROM ({query}) t1
                    WHERE timestamp = (
                        SELECT MAX(timestamp) FROM feature_values t2 
                        WHERE t2.feature_group_name = t1.feature_group_name 
                        AND t2.feature_name = t1.feature_name 
                        AND t2.entity_id = t1.entity_id
                    )
                """
            
            if timestamp_range:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([ts.isoformat() for ts in timestamp_range])
            
            # Execute query
            cursor = self.conn.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if not rows:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df_data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                
                # Parse value based on type
                value_str = row_dict['value']
                value_type = row_dict['value_type']
                
                if value_str is None:
                    parsed_value = None
                elif value_type == 'str':
                    parsed_value = value_str
                elif value_type in ['int', 'int64']:
                    parsed_value = int(value_str)
                elif value_type in ['float', 'float64']:
                    parsed_value = float(value_str)
                elif value_type == 'bool':
                    parsed_value = value_str.lower() == 'true'
                elif value_type in ['list', 'dict']:
                    parsed_value = json.loads(value_str)
                else:
                    parsed_value = value_str
                
                df_data.append({
                    'entity_id': row_dict['entity_id'],
                    'feature_name': row_dict['feature_name'],
                    'value': parsed_value,
                    'timestamp': row_dict['timestamp'],
                    'version': row_dict['version']
                })
            
            df = pd.DataFrame(df_data)
            
            # Pivot to get features as columns
            if not df.empty:
                result_df = df.pivot_table(
                    index=['entity_id', 'timestamp', 'version'],
                    columns='feature_name',
                    values='value',
                    aggfunc='first'
                ).reset_index()
                
                # Flatten column names
                result_df.columns.name = None
                
                return result_df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error reading features: {str(e)}")
            return pd.DataFrame()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()


class FeatureTransformation:
    """Feature transformation pipeline"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.transformations: List[Callable] = []
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def add_transformation(self, func: Callable, description: str = ""):
        """Add a transformation function"""
        func._description = description
        self.transformations.append(func)
        logger.info(f"Added transformation to {self.name}: {description}")
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all transformations to the DataFrame"""
        result_df = df.copy()
        
        for transform_func in self.transformations:
            try:
                result_df = transform_func(result_df)
                logger.debug(f"Applied transformation: {getattr(transform_func, '_description', 'unnamed')}")
            except Exception as e:
                logger.error(f"Error applying transformation {transform_func.__name__}: {str(e)}")
                raise
        
        return result_df
    
    def get_transformation_info(self) -> Dict[str, Any]:
        """Get information about transformations"""
        return {
            "name": self.name,
            "description": self.description,
            "transformation_count": len(self.transformations),
            "transformations": [
                {
                    "function": func.__name__,
                    "description": getattr(func, '_description', 'No description')
                }
                for func in self.transformations
            ]
        }


class FeatureValidator:
    """Feature validation engine"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        self.validation_rules: Dict[str, List[Callable]] = {}
    
    def add_rule(self, feature_name: str, rule_func: Callable, description: str = ""):
        """Add a validation rule for a feature"""
        if feature_name not in self.validation_rules:
            self.validation_rules[feature_name] = []
        
        rule_func._description = description
        self.validation_rules[feature_name].append(rule_func)
        logger.info(f"Added validation rule for {feature_name}: {description}")
    
    def validate_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate features in DataFrame"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "feature_validations": {}
        }
        
        for feature_name, rules in self.validation_rules.items():
            if feature_name not in df.columns:
                validation_results["warnings"].append(f"Feature {feature_name} not found in data")
                continue
            
            feature_results = {"passed": [], "failed": []}
            
            for rule in rules:
                try:
                    is_valid = rule(df[feature_name])
                    rule_description = getattr(rule, '_description', rule.__name__)
                    
                    if is_valid:
                        feature_results["passed"].append(rule_description)
                    else:
                        feature_results["failed"].append(rule_description)
                        validation_results["is_valid"] = False
                        validation_results["errors"].append(f"Validation failed for {feature_name}: {rule_description}")
                        
                except Exception as e:
                    error_msg = f"Error validating {feature_name} with rule {rule.__name__}: {str(e)}"
                    validation_results["errors"].append(error_msg)
                    validation_results["is_valid"] = False
            
            validation_results["feature_validations"][feature_name] = feature_results
        
        return validation_results


class FeatureLineage:
    """Track feature lineage and dependencies"""
    
    def __init__(self):
        self.lineage_graph: Dict[str, Dict] = {}
    
    def add_feature_dependency(
        self,
        feature_name: str,
        source_features: List[str],
        transformation: str,
        metadata: Optional[Dict] = None
    ):
        """Add feature dependency information"""
        self.lineage_graph[feature_name] = {
            "source_features": source_features,
            "transformation": transformation,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        logger.info(f"Added lineage for {feature_name} from {source_features}")
    
    def get_feature_lineage(self, feature_name: str, depth: int = 3) -> Dict[str, Any]:
        """Get lineage for a specific feature"""
        if feature_name not in self.lineage_graph:
            return {"error": f"No lineage found for {feature_name}"}
        
        def trace_lineage(fname: str, current_depth: int) -> Dict:
            if current_depth <= 0 or fname not in self.lineage_graph:
                return {"feature": fname, "source": "base"}
            
            lineage_info = self.lineage_graph[fname]
            source_lineages = []
            
            for source_feature in lineage_info["source_features"]:
                source_lineages.append(trace_lineage(source_feature, current_depth - 1))
            
            return {
                "feature": fname,
                "transformation": lineage_info["transformation"],
                "sources": source_lineages,
                "created_at": lineage_info["created_at"],
                "metadata": lineage_info["metadata"]
            }
        
        return trace_lineage(feature_name, depth)
    
    def get_downstream_features(self, feature_name: str) -> List[str]:
        """Get features that depend on the given feature"""
        downstream = []
        for fname, lineage_info in self.lineage_graph.items():
            if feature_name in lineage_info["source_features"]:
                downstream.append(fname)
        return downstream
    
    def get_impact_analysis(self, feature_name: str) -> Dict[str, Any]:
        """Analyze the impact of changing a feature"""
        downstream_features = self.get_downstream_features(feature_name)
        
        impact_tree = {}
        for downstream_feature in downstream_features:
            impact_tree[downstream_feature] = self.get_downstream_features(downstream_feature)
        
        return {
            "source_feature": feature_name,
            "direct_impact": downstream_features,
            "impact_tree": impact_tree,
            "total_impacted_features": len(set([
                f for f_list in impact_tree.values() for f in f_list
            ] + downstream_features))
        }


class AdvancedFeatureStore:
    """Advanced feature store with transformations, validation, and lineage"""
    
    def __init__(self, base_store: FeatureStore):
        self.base_store = base_store
        self.transformations: Dict[str, FeatureTransformation] = {}
        self.validator = FeatureValidator()
        self.lineage = FeatureLineage()
        self.feature_stats: Dict[str, Dict] = {}
    
    def register_transformation(self, transformation: FeatureTransformation):
        """Register a feature transformation"""
        self.transformations[transformation.name] = transformation
        logger.info(f"Registered transformation: {transformation.name}")
    
    def create_feature_group_with_transformation(
        self,
        feature_group: FeatureGroup,
        source_data: pd.DataFrame,
        transformation_name: Optional[str] = None
    ) -> bool:
        """Create feature group with optional transformation"""
        
        # Apply transformation if specified
        if transformation_name and transformation_name in self.transformations:
            transformation = self.transformations[transformation_name]
            transformed_data = transformation.apply(source_data)
            
            # Track lineage
            for feature_name in feature_group.features:
                if hasattr(feature_name, 'name'):
                    self.lineage.add_feature_dependency(
                        feature_name.name,
                        list(source_data.columns),
                        transformation_name,
                        {"feature_group": feature_group.name}
                    )
        else:
            transformed_data = source_data
        
        # Validate features
        validation_result = self.validator.validate_features(transformed_data)
        if not validation_result["is_valid"]:
            logger.error(f"Feature validation failed: {validation_result['errors']}")
            return False
        
        # Calculate feature statistics
        self._calculate_feature_stats(feature_group.name, transformed_data)
        
        # Create feature group and write data
        if self.base_store.create_feature_group(feature_group):
            return self.base_store.write_features(feature_group.name, transformed_data, feature_group.version)
        
        return False
    
    def read_features_with_validation(
        self,
        feature_group_name: str,
        feature_names: Optional[List[str]] = None,
        entity_ids: Optional[List[str]] = None,
        version: Optional[str] = None,
        validate: bool = True
    ) -> Tuple[pd.DataFrame, Optional[Dict]]:
        """Read features with optional validation"""
        
        df = self.base_store.read_features(
            feature_group_name, feature_names, entity_ids, version
        )
        
        validation_result = None
        if validate and not df.empty:
            validation_result = self.validator.validate_features(df)
            if not validation_result["is_valid"]:
                logger.warning(f"Validation warnings for {feature_group_name}: {validation_result['warnings']}")
        
        return df, validation_result
    
    def get_feature_statistics(self, feature_group_name: str) -> Optional[Dict]:
        """Get feature statistics"""
        return self.feature_stats.get(feature_group_name)
    
    def _calculate_feature_stats(self, feature_group_name: str, df: pd.DataFrame):
        """Calculate and store feature statistics"""
        stats = {}
        
        for column in df.columns:
            if column == 'entity_id':
                continue
            
            col_stats = {
                "count": len(df[column]),
                "null_count": df[column].isnull().sum(),
                "null_percentage": (df[column].isnull().sum() / len(df[column])) * 100,
                "data_type": str(df[column].dtype)
            }
            
            if df[column].dtype in ['int64', 'float64']:
                col_stats.update({
                    "mean": df[column].mean(),
                    "std": df[column].std(),
                    "min": df[column].min(),
                    "max": df[column].max(),
                    "median": df[column].median(),
                    "quantiles": {
                        "25%": df[column].quantile(0.25),
                        "75%": df[column].quantile(0.75)
                    }
                })
            elif df[column].dtype == 'object':
                col_stats.update({
                    "unique_count": df[column].nunique(),
                    "most_frequent": df[column].mode().iloc[0] if not df[column].mode().empty else None,
                    "value_counts": df[column].value_counts().head(10).to_dict()
                })
            
            stats[column] = col_stats
        
        self.feature_stats[feature_group_name] = {
            "statistics": stats,
            "calculated_at": datetime.now().isoformat(),
            "sample_size": len(df)
        }
    
    def get_lineage_report(self, feature_name: str) -> Dict[str, Any]:
        """Get comprehensive lineage report"""
        lineage = self.lineage.get_feature_lineage(feature_name)
        impact = self.lineage.get_impact_analysis(feature_name)
        
        return {
            "feature_name": feature_name,
            "lineage": lineage,
            "impact_analysis": impact,
            "generated_at": datetime.now().isoformat()
        }
    
    def export_feature_catalog(self) -> Dict[str, Any]:
        """Export complete feature catalog"""
        catalog = {
            "export_timestamp": datetime.now().isoformat(),
            "feature_groups": {},
            "transformations": {},
            "statistics": self.feature_stats,
            "lineage_graph": self.lineage.lineage_graph
        }
        
        # This would iterate through all feature groups in a real implementation
        # For now, return the structure
        
        return catalog
    
    def close(self):
        """Close the feature store"""
        self.base_store.close()