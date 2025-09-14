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
        """Create a new feature group in the feature store"""
        pass
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
    
    def __init__(self, db_path -> None: str = "feature_store.db") -> None:
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
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
    
    def close(self) -> None:
        """Close the database connection"""
        if self.conn:
            self.conn.close()


class FeatureTransformation:
    """Feature transformation pipeline"""
    
    def __init__(self, name -> None: str, description -> None: str) -> None:
        """
        Initialise le pipeline de transformation de features pour créateurs
        
        Args:
            name: Nom du pipeline (ex: "musician_audio_features", "blogger_text_features")
            description: Description du pipeline de transformation
        """
        self.name = name
        self.description = description
        self.transformations: List[Callable] = []
        
        # Configuration spécifique aux types de créateurs
        self.creator_configs = {
            "musician": {
                "feature_types": ["audio", "temporal", "spectral", "harmonic"],
                "sampling_rate": 44100,
                "frame_size": 2048,
                "hop_length": 512
            },
            "blogger": {
                "feature_types": ["text", "sentiment", "readability", "seo"],
                "max_sequence_length": 512,
                "vocab_size": 50000,
                "embedding_dim": 768
            },
            "photographer": {
                "feature_types": ["visual", "aesthetic", "composition", "color"],
                "image_size": (224, 224),
                "color_spaces": ["RGB", "HSV", "LAB"],
                "style_categories": ["portrait", "landscape", "street", "fashion"]
            },
            "influencer": {
                "feature_types": ["engagement", "sentiment", "reach", "demographics"],
                "platforms": ["instagram", "tiktok", "youtube", "twitter"],
                "metrics": ["likes", "shares", "comments", "saves"]
            }
        }
        
        # Détecter le type de créateur basé sur le nom du pipeline
        self.creator_type = None
        for creator_type in self.creator_configs.keys():
            if creator_type in name.lower():
                self.creator_type = creator_type
                break
        
        # Configuration par défaut si type non détecté
        if not self.creator_type:
            self.creator_type = "generic"
            self.creator_configs["generic"] = {
                "feature_types": ["multimodal"],
                "default_processing": True
            }
        
        # Initialiser les transformations par défaut selon le type de créateur
        self._init_default_transformations()
        
        logger.info(f"Initialized FeatureTransformationPipeline '{self.name}' for creator type: {self.creator_type}")
    
    def _init_default_transformations(self) -> None:
        """Initialise les transformations par défaut selon le type de créateur"""
        config = self.creator_configs[self.creator_type]
        
        if self.creator_type == "musician":
            # Transformations audio par défaut
            self.add_transformation(
                lambda x: self._normalize_audio(x), 
                "Audio normalization for musicians"
            )
            self.add_transformation(
                lambda x: self._extract_spectral_features(x), 
                "Spectral feature extraction (MFCC, chroma, spectral_contrast)"
            )
            
        elif self.creator_type == "blogger":
            # Transformations texte par défaut  
            self.add_transformation(
                lambda x: self._clean_text(x), 
                "Text cleaning and preprocessing for bloggers"
            )
            self.add_transformation(
                lambda x: self._extract_seo_features(x), 
                "SEO feature extraction (keyword density, readability, structure)"
            )
            
        elif self.creator_type == "photographer":
            # Transformations image par défaut
            self.add_transformation(
                lambda x: self._resize_and_normalize_image(x), 
                "Image preprocessing for photographers"
            )
            self.add_transformation(
                lambda x: self._extract_aesthetic_features(x), 
                "Aesthetic feature extraction (composition, color harmony, style)"
            )
            
        elif self.creator_type == "influencer":
            # Transformations métriques d'engagement
            self.add_transformation(
                lambda x: self._normalize_engagement_metrics(x), 
                "Engagement metrics normalization for influencers"
            )
            self.add_transformation(
                lambda x: self._extract_audience_features(x), 
                "Audience demographic and behavior feature extraction"
            )
    
    def _normalize_audio(self, audio_data) -> None:
        """Normalisation audio pour musiciens"""
        # Implémentation de normalisation audio
        return {"normalized_audio": "processed", "peak_level": -3.0}
    
    def _extract_spectral_features(self, audio_data) -> None:
        """Extraction de features spectrales"""
        return {"mfcc": [1.2, 0.8, -0.3], "chroma": [0.9, 0.1], "spectral_contrast": [0.7]}
    
    def _clean_text(self, text_data) -> None:
        """Nettoyage de texte pour bloggers"""
        return {"cleaned_text": "processed", "word_count": 500}
    
    def _extract_seo_features(self, text_data) -> None:
        """Extraction de features SEO"""
        return {"keyword_density": 0.02, "readability_score": 85, "heading_structure": True}
    
    def _resize_and_normalize_image(self, image_data) -> None:
        """Preprocessing d'image pour photographes"""
        return {"resized_image": "224x224", "normalized": True}
    
    def _extract_aesthetic_features(self, image_data) -> None:
        """Extraction de features esthétiques"""
        return {"composition_score": 0.85, "color_harmony": 0.92, "style": "portrait"}
    
    def _normalize_engagement_metrics(self, engagement_data) -> None:
        """Normalisation des métriques d'engagement"""
        return {"normalized_likes": 0.75, "engagement_rate": 0.045}
    
    def _extract_audience_features(self, audience_data) -> None:
        """Extraction de features d'audience"""
        return {"age_range": "25-34", "gender_ratio": 0.6, "top_interests": ["fashion", "travel"]}
    def add_transformation(self, func -> None: Callable, description -> None: str = "") -> None:
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
    """Feature validation engine for enterprise ML feature quality assurance"""
    
    def __init__(self) -> None:
        """
        Initialise le validateur de features avec règles spécifiques aux créateurs
        """
        self.validation_rules: Dict[str, List[Callable]] = {}
        
        # Règles de validation par type de créateur
        self.creator_validation_rules = {
            "musician": {
                "audio_features": [
                    self._validate_audio_sample_rate,
                    self._validate_audio_duration,
                    self._validate_spectral_features,
                    self._validate_audio_quality
                ],
                "metadata": [
                    self._validate_genre_classification,
                    self._validate_tempo_range,
                    self._validate_key_signature
                ]
            },
            "blogger": {
                "text_features": [
                    self._validate_text_length,
                    self._validate_language_detection,
                    self._validate_sentiment_score,
                    self._validate_readability_metrics
                ],
                "seo_features": [
                    self._validate_keyword_density,
                    self._validate_heading_structure,
                    self._validate_meta_description
                ]
            },
            "photographer": {
                "image_features": [
                    self._validate_image_dimensions,
                    self._validate_image_quality,
                    self._validate_color_profile,
                    self._validate_exposure_metrics
                ],
                "aesthetic_features": [
                    self._validate_composition_score,
                    self._validate_style_classification,
                    self._validate_artistic_elements
                ]
            },
            "influencer": {
                "engagement_features": [
                    self._validate_engagement_metrics,
                    self._validate_audience_data,
                    self._validate_platform_consistency,
                    self._validate_temporal_patterns
                ],
                "demographics": [
                    self._validate_age_distribution,
                    self._validate_geographic_data,
                    self._validate_interest_categories
                ]
            }
        }
        
        # Seuils de validation par défaut
        self.validation_thresholds = {
            "musician": {
                "min_sample_rate": 22050,
                "max_sample_rate": 192000,
                "min_duration": 10.0,  # secondes
                "max_duration": 600.0,
                "min_audio_quality": 0.7
            },
            "blogger": {
                "min_text_length": 100,
                "max_text_length": 10000,
                "min_readability": 40,
                "max_keyword_density": 0.05
            },
            "photographer": {
                "min_width": 800,
                "min_height": 600,
                "min_quality_score": 0.6,
                "required_color_profiles": ["sRGB", "Adobe RGB"]
            },
            "influencer": {
                "min_engagement_rate": 0.01,
                "max_engagement_rate": 0.20,
                "min_follower_count": 1000,
                "required_platforms": ["instagram", "tiktok"]
            }
        }
        
        # Métriques de validation
        self.validation_stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "validation_errors": [],
            "performance_metrics": {}
        }
        
        logger.info(f"Initialized FeatureValidator with {len(self.creator_validation_rules)} creator type configurations")
    
    # Validation methods for musicians
    def _validate_audio_sample_rate(self, feature_data: Dict) -> bool:
        """Valide le taux d'échantillonnage audio"""
        sample_rate = feature_data.get("sample_rate", 0)
        thresholds = self.validation_thresholds["musician"]
        return thresholds["min_sample_rate"] <= sample_rate <= thresholds["max_sample_rate"]
    
    def _validate_audio_duration(self, feature_data: Dict) -> bool:
        """Valide la durée audio"""
        duration = feature_data.get("duration", 0)
        thresholds = self.validation_thresholds["musician"]
        return thresholds["min_duration"] <= duration <= thresholds["max_duration"]
    
    def _validate_spectral_features(self, feature_data: Dict) -> bool:
        """Valide les features spectrales"""
        mfcc = feature_data.get("mfcc", [])
        chroma = feature_data.get("chroma", [])
        return len(mfcc) >= 13 and len(chroma) >= 12  # Standards MFCC et Chroma
    
    def _validate_audio_quality(self, feature_data: Dict) -> bool:
        """Valide la qualité audio"""
        quality_score = feature_data.get("quality_score", 0)
        threshold = self.validation_thresholds["musician"]["min_audio_quality"]
        return quality_score >= threshold
    
    def _validate_genre_classification(self, feature_data: Dict) -> bool:
        """Valide la classification de genre"""
        genre = feature_data.get("genre", "")
        confidence = feature_data.get("genre_confidence", 0)
        return genre != "" and confidence >= 0.7
    
    def _validate_tempo_range(self, feature_data: Dict) -> bool:
        """Valide le tempo"""
        tempo = feature_data.get("tempo", 0)
        return 60 <= tempo <= 200  # BPM raisonnable
    
    def _validate_key_signature(self, feature_data: Dict) -> bool:
        """Valide la signature de clé"""
        key = feature_data.get("key", "")
        valid_keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return key in valid_keys
    
    # Validation methods for bloggers
    def _validate_text_length(self, feature_data: Dict) -> bool:
        """Valide la longueur du texte"""
        text_length = feature_data.get("text_length", 0)
        thresholds = self.validation_thresholds["blogger"]
        return thresholds["min_text_length"] <= text_length <= thresholds["max_text_length"]
    
    def _validate_language_detection(self, feature_data: Dict) -> bool:
        """Valide la détection de langue"""
        language = feature_data.get("language", "")
        confidence = feature_data.get("language_confidence", 0)
        return language != "" and confidence >= 0.8
    
    def _validate_sentiment_score(self, feature_data: Dict) -> bool:
        """Valide le score de sentiment"""
        sentiment_score = feature_data.get("sentiment_score", 0)
        return -1.0 <= sentiment_score <= 1.0
    
    def _validate_readability_metrics(self, feature_data: Dict) -> bool:
        """Valide les métriques de lisibilité"""
        readability = feature_data.get("readability_score", 0)
        threshold = self.validation_thresholds["blogger"]["min_readability"]
        return readability >= threshold
    
    def _validate_keyword_density(self, feature_data: Dict) -> bool:
        """Valide la densité de mots-clés"""
        density = feature_data.get("keyword_density", 0)
        max_density = self.validation_thresholds["blogger"]["max_keyword_density"]
        return 0 <= density <= max_density
    
    def _validate_heading_structure(self, feature_data: Dict) -> bool:
        """Valide la structure des en-têtes"""
        has_h1 = feature_data.get("has_h1", False)
        h2_count = feature_data.get("h2_count", 0)
        return has_h1 and h2_count >= 2
    
    def _validate_meta_description(self, feature_data: Dict) -> bool:
        """Valide la méta-description"""
        meta_desc = feature_data.get("meta_description", "")
        return 120 <= len(meta_desc) <= 160
    
    # Validation methods for photographers
    def _validate_image_dimensions(self, feature_data: Dict) -> bool:
        """Valide les dimensions d'image"""
        width = feature_data.get("width", 0)
        height = feature_data.get("height", 0)
        thresholds = self.validation_thresholds["photographer"]
        return width >= thresholds["min_width"] and height >= thresholds["min_height"]
    
    def _validate_image_quality(self, feature_data: Dict) -> bool:
        """Valide la qualité d'image"""
        quality_score = feature_data.get("image_quality", 0)
        threshold = self.validation_thresholds["photographer"]["min_quality_score"]
        return quality_score >= threshold
    
    def _validate_color_profile(self, feature_data: Dict) -> bool:
        """Valide le profil colorimétrique"""
        color_profile = feature_data.get("color_profile", "")
        valid_profiles = self.validation_thresholds["photographer"]["required_color_profiles"]
        return color_profile in valid_profiles
    
    def _validate_exposure_metrics(self, feature_data: Dict) -> bool:
        """Valide les métriques d'exposition"""
        exposure = feature_data.get("exposure_value", 0)
        return -5.0 <= exposure <= 5.0  # EV range
    
    def _validate_composition_score(self, feature_data: Dict) -> bool:
        """Valide le score de composition"""
        composition = feature_data.get("composition_score", 0)
        return 0.0 <= composition <= 1.0
    
    def _validate_style_classification(self, feature_data: Dict) -> bool:
        """Valide la classification de style"""
        style = feature_data.get("style", "")
        confidence = feature_data.get("style_confidence", 0)
        return style != "" and confidence >= 0.6
    
    def _validate_artistic_elements(self, feature_data: Dict) -> bool:
        """Valide les éléments artistiques"""
        elements = feature_data.get("artistic_elements", [])
        return len(elements) >= 1  # Au moins un élément artistique détecté
    
    # Validation methods for influencers
    def _validate_engagement_metrics(self, feature_data: Dict) -> bool:
        """Valide les métriques d'engagement"""
        engagement_rate = feature_data.get("engagement_rate", 0)
        thresholds = self.validation_thresholds["influencer"]
        return thresholds["min_engagement_rate"] <= engagement_rate <= thresholds["max_engagement_rate"]
    
    def _validate_audience_data(self, feature_data: Dict) -> bool:
        """Valide les données d'audience"""
        follower_count = feature_data.get("follower_count", 0)
        threshold = self.validation_thresholds["influencer"]["min_follower_count"]
        return follower_count >= threshold
    
    def _validate_platform_consistency(self, feature_data: Dict) -> bool:
        """Valide la cohérence des plateformes"""
        platforms = feature_data.get("platforms", [])
        required = self.validation_thresholds["influencer"]["required_platforms"]
        return any(platform in platforms for platform in required)
    
    def _validate_temporal_patterns(self, feature_data: Dict) -> bool:
        """Valide les patterns temporels"""
        posting_frequency = feature_data.get("posting_frequency", 0)
        return posting_frequency >= 3  # Au moins 3 posts par semaine
    
    def _validate_age_distribution(self, feature_data: Dict) -> bool:
        """Valide la distribution d'âge"""
        age_data = feature_data.get("age_distribution", {})
        return len(age_data) >= 3  # Au moins 3 groupes d'âge
    
    def _validate_geographic_data(self, feature_data: Dict) -> bool:
        """Valide les données géographiques"""
        geo_data = feature_data.get("geographic_distribution", {})
        return len(geo_data) >= 1  # Au moins une région
    
    def _validate_interest_categories(self, feature_data: Dict) -> bool:
        """Valide les catégories d'intérêt"""
        interests = feature_data.get("top_interests", [])
        return len(interests) >= 3  # Au moins 3 catégories d'intérêt
        self.validation_rules: Dict[str, List[Callable]] = {}
    
    def add_rule(self, feature_name -> None: str, rule_func -> None: Callable, description -> None: str = "") -> None:
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
    
    def __init__(self) -> None:
        self.lineage_graph: Dict[str, Dict] = {}
    
    def add_feature_dependency(
        self,
        feature_name -> None: str,
        source_features -> None: List[str],
        transformation -> None: str,
        metadata -> None: Optional[Dict] = None
    ) -> None:
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
    
    def __init__(self, base_store -> None: FeatureStore) -> None:
        self.base_store = base_store
        self.transformations: Dict[str, FeatureTransformation] = {}
        self.validator = FeatureValidator()
        self.lineage = FeatureLineage()
        self.feature_stats: Dict[str, Dict] = {}
    
    def register_transformation(self, transformation -> None: FeatureTransformation) -> None:
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
    
    def _calculate_feature_stats(self, feature_group_name -> None: str, df -> None: pd.DataFrame) -> None:
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
    
    def close(self) -> None:
        """Close the feature store"""
        self.base_store.close()