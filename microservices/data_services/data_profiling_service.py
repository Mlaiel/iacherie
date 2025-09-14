#!/usr/bin/env python3
"""
📊 Data Profiling Service - Enterprise Data Management
Service de profilage de données enterprise pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🗄️ DBA + Data Engineer Implementation
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import hashlib
import statistics
import re

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataType(Enum):
    """Types de données"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"
    UNKNOWN = "unknown"

class QualityIssue(Enum):
    """Types de problèmes qualité"""
    NULL_VALUES = "null_values"
    DUPLICATES = "duplicates"
    OUTLIERS = "outliers"
    INVALID_FORMAT = "invalid_format"
    INCONSISTENT_CASE = "inconsistent_case"
    SPECIAL_CHARACTERS = "special_characters"
    LENGTH_VIOLATION = "length_violation"
    REFERENTIAL_INTEGRITY = "referential_integrity"

@dataclass
class ColumnProfile:
    """Profil d'une colonne"""
    column_name: str
    data_type: DataType
    total_count: int
    non_null_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    duplicate_count: int
    min_value: Any = None
    max_value: Any = None
    mean_value: float = None
    median_value: float = None
    std_deviation: float = None
    min_length: int = None
    max_length: int = None
    avg_length: float = None
    patterns: List[str] = None
    quality_issues: List[str] = None
    sample_values: List[Any] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.quality_issues is None:
            self.quality_issues = []
        if self.sample_values is None:
            self.sample_values = []

@dataclass
class TableProfile:
    """Profil d'une table"""
    table_name: str
    database_name: str
    schema_name: str
    total_rows: int
    total_columns: int
    column_profiles: List[ColumnProfile]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    data_quality_score: float
    profile_timestamp: datetime
    profiling_duration: float
    
    def __post_init__(self):
        if not self.column_profiles:
            self.column_profiles = []
        if not self.primary_keys:
            self.primary_keys = []
        if not self.foreign_keys:
            self.foreign_keys = []
        if not self.indexes:
            self.indexes = []
        if not self.constraints:
            self.constraints = []

@dataclass
class DatasetProfile:
    """Profil d'un dataset complet"""
    dataset_id: str
    dataset_name: str
    source_type: str  # database, file, api, stream
    table_profiles: List[TableProfile]
    relationships: List[Dict[str, Any]]
    overall_quality_score: float
    total_records: int
    total_columns: int
    profiled_at: datetime
    profile_config: Dict[str, Any]
    
    def __post_init__(self):
        if not self.table_profiles:
            self.table_profiles = []
        if not self.relationships:
            self.relationships = []
        if not self.profile_config:
            self.profile_config = {}

@dataclass
class ProfilingJob:
    """Job de profilage"""
    job_id: str
    dataset_id: str
    job_type: str  # full, incremental, sample
    status: str  # pending, running, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    config: Dict[str, Any] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}

class DataProfilingService:
    """Service de profilage de données Enterprise"""
    
    def __init__(self):
        self.service_name = "data-profiling-service"
        self.version = "1.0.0"
        
        # Jobs et profils
        self.profiling_jobs: Dict[str, ProfilingJob] = {}
        self.dataset_profiles: Dict[str, DatasetProfile] = {}
        self.active_jobs: Set[str] = set()
        
        # Configuration
        self.max_concurrent_jobs = 3
        self.sample_size = 10000
        self.enable_statistical_analysis = True
        self.enable_pattern_detection = True
        
        # Métriques
        self.metrics = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'datasets_profiled': 0,
            'tables_profiled': 0,
            'columns_profiled': 0,
            'quality_issues_detected': 0,
            'avg_profiling_time': 0.0
        }
        
        # Patterns communs
        self.common_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^[\+]?[1-9]?[\d\s\-\(\)]{10,}$',
            'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            'ip_address': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            'credit_card': r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$',
            'ssn': r'^\d{3}-?\d{2}-?\d{4}$',
            'date_iso': r'^\d{4}-\d{2}-\d{2}$',
            'datetime_iso': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        }
        
        logger.info(f"📊 {self.service_name} v{self.version} - Initialisation")
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation du service"""
        try:
            logger.info("🚀 Initialisation Data Profiling Service...")
            
            if config is None:
                config = {}
            
            # Configuration
            self.max_concurrent_jobs = config.get('max_concurrent_jobs', 3)
            self.sample_size = config.get('sample_size', 10000)
            self.enable_statistical_analysis = config.get('statistical_analysis', True)
            self.enable_pattern_detection = config.get('pattern_detection', True)
            
            # Démarrage monitoring
            asyncio.create_task(self._monitoring_loop())
            
            # Tâches de maintenance
            asyncio.create_task(self._maintenance_loop())
            
            logger.info("✅ Data Profiling Service initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def create_profiling_job(self, 
                                 dataset_id: str,
                                 job_type: str = "full",
                                 config: Dict[str, Any] = None) -> str:
        """Création job de profilage"""
        try:
            job_id = f"prof_{int(time.time())}_{len(self.profiling_jobs)}"
            
            job = ProfilingJob(
                job_id=job_id,
                dataset_id=dataset_id,
                job_type=job_type,
                status="pending",
                started_at=datetime.now(),
                config=config or {}
            )
            
            self.profiling_jobs[job_id] = job
            self.metrics['total_jobs'] += 1
            
            # Démarrage asynchrone
            asyncio.create_task(self._execute_profiling_job(job_id))
            
            logger.info(f"✅ Job profilage créé: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création job: {e}")
            raise
    
    async def _execute_profiling_job(self, job_id: str):
        """Exécution job de profilage"""
        try:
            if len(self.active_jobs) >= self.max_concurrent_jobs:
                logger.warning("⚠️ Limite jobs simultanés atteinte")
                return
            
            self.active_jobs.add(job_id)
            job = self.profiling_jobs[job_id]
            
            job.status = "running"
            start_time = time.time()
            
            logger.info(f"🚀 Début profilage: {job_id}")
            
            # Simulation profilage (en production, connecter aux vraies sources)
            dataset_profile = await self._profile_dataset(job.dataset_id, job.config)
            
            if dataset_profile:
                self.dataset_profiles[job.dataset_id] = dataset_profile
                job.status = "completed"
                self.metrics['completed_jobs'] += 1
                self.metrics['datasets_profiled'] += 1
            else:
                job.status = "failed"
                job.error_message = "Échec profilage dataset"
                self.metrics['failed_jobs'] += 1
            
            # Durée
            duration = time.time() - start_time
            job.completed_at = datetime.now()
            
            # Mise à jour moyenne
            if self.metrics['completed_jobs'] > 0:
                current_avg = self.metrics['avg_profiling_time']
                new_avg = ((current_avg * (self.metrics['completed_jobs'] - 1)) + duration) / self.metrics['completed_jobs']
                self.metrics['avg_profiling_time'] = new_avg
            
            logger.info(f"✅ Profilage terminé: {job_id} en {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution profilage {job_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            self.metrics['failed_jobs'] += 1
            
        finally:
            self.active_jobs.discard(job_id)
    
    async def _profile_dataset(self, dataset_id: str, config: Dict[str, Any]) -> Optional[DatasetProfile]:
        """Profilage d'un dataset"""
        try:
            # Simulation dataset (en production, récupérer depuis source réelle)
            tables_data = await self._get_dataset_tables(dataset_id)
            
            table_profiles = []
            total_records = 0
            total_columns = 0
            quality_scores = []
            
            for table_name, table_data in tables_data.items():
                table_profile = await self._profile_table(table_name, table_data, dataset_id)
                
                if table_profile:
                    table_profiles.append(table_profile)
                    total_records += table_profile.total_rows
                    total_columns += table_profile.total_columns
                    quality_scores.append(table_profile.data_quality_score)
                    
                    self.metrics['tables_profiled'] += 1
                    self.metrics['columns_profiled'] += table_profile.total_columns
            
            # Score qualité global
            overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            # Détection relations entre tables
            relationships = await self._detect_relationships(table_profiles)
            
            dataset_profile = DatasetProfile(
                dataset_id=dataset_id,
                dataset_name=f"Dataset {dataset_id}",
                source_type="database",
                table_profiles=table_profiles,
                relationships=relationships,
                overall_quality_score=overall_quality,
                total_records=total_records,
                total_columns=total_columns,
                profiled_at=datetime.now(),
                profile_config=config
            )
            
            return dataset_profile
            
        except Exception as e:
            logger.error(f"❌ Erreur profilage dataset {dataset_id}: {e}")
            return None
    
    async def _get_dataset_tables(self, dataset_id: str) -> Dict[str, pd.DataFrame]:
        """Récupération tables du dataset (simulation)"""
        try:
            # Simulation données pour test
            tables = {}
            
            # Table users
            users_data = {
                'user_id': [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
                'email': ['user1@test.com', 'user2@test.com', 'invalid-email', 'user4@test.com', None, 
                         'user6@test.com', 'user7@test.com', 'user8@test.com', 'user9@test.com', 'user10@test.com'],
                'age': [25, 30, 35, None, 45, 50, 22, 28, 33, 41],
                'created_at': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                              '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'],
                'status': ['active', 'active', 'inactive', 'active', 'suspended', 
                          'active', 'active', 'inactive', 'active', 'active']
            }
            tables['users'] = pd.DataFrame(users_data)
            
            # Table orders
            orders_data = {
                'order_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                'user_id': [1, 2, 1, 3, None, 4, 5, 1, 2, 3],
                'amount': [29.99, 45.50, 15.75, 89.99, 120.00, 33.25, 67.80, 12.99, 55.40, 78.90],
                'order_date': ['2023-02-01', '2023-02-02', '2023-02-03', '2023-02-04', '2023-02-05',
                              '2023-02-06', '2023-02-07', '2023-02-08', '2023-02-09', '2023-02-10'],
                'payment_method': ['credit_card', 'paypal', 'credit_card', 'bank_transfer', 'credit_card',
                                  'paypal', 'credit_card', 'paypal', 'credit_card', 'bank_transfer']
            }
            tables['orders'] = pd.DataFrame(orders_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération tables: {e}")
            return {}
    
    async def _profile_table(self, table_name: str, table_data: pd.DataFrame, dataset_id: str) -> Optional[TableProfile]:
        """Profilage d'une table"""
        try:
            column_profiles = []
            quality_scores = []
            
            for column_name in table_data.columns:
                column_profile = await self._profile_column(column_name, table_data[column_name])
                column_profiles.append(column_profile)
                
                # Score qualité colonne (basé sur pourcentage valeurs non nulles)
                quality_score = (column_profile.non_null_count / column_profile.total_count) * 100
                if column_profile.quality_issues:
                    quality_score -= len(column_profile.quality_issues) * 5  # Pénalité pour problèmes
                quality_scores.append(max(quality_score, 0))
            
            # Score qualité table
            table_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            # Détection clés primaires (simulation)
            primary_keys = self._detect_primary_keys(table_data)
            
            # Détection clés étrangères (simulation)
            foreign_keys = self._detect_foreign_keys(table_name, table_data)
            
            # Index et contraintes (simulation)
            indexes = self._detect_indexes(table_data)
            constraints = self._detect_constraints(table_data)
            
            table_profile = TableProfile(
                table_name=table_name,
                database_name=dataset_id,
                schema_name="public",
                total_rows=len(table_data),
                total_columns=len(table_data.columns),
                column_profiles=column_profiles,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                indexes=indexes,
                constraints=constraints,
                data_quality_score=table_quality_score,
                profile_timestamp=datetime.now(),
                profiling_duration=0.5  # Simulation
            )
            
            return table_profile
            
        except Exception as e:
            logger.error(f"❌ Erreur profilage table {table_name}: {e}")
            return None
    
    async def _profile_column(self, column_name: str, column_data: pd.Series) -> ColumnProfile:
        """Profilage d'une colonne"""
        try:
            # Statistiques de base
            total_count = len(column_data)
            non_null_count = column_data.notna().sum()
            null_count = column_data.isna().sum()
            null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
            unique_count = column_data.nunique()
            duplicate_count = total_count - unique_count
            
            # Détection type de données
            data_type = self._detect_data_type(column_data)
            
            # Statistiques spécialisées selon le type
            min_value = None
            max_value = None
            mean_value = None
            median_value = None
            std_deviation = None
            min_length = None
            max_length = None
            avg_length = None
            
            if data_type in [DataType.INTEGER, DataType.FLOAT]:
                numeric_data = pd.to_numeric(column_data, errors='coerce').dropna()
                if len(numeric_data) > 0:
                    min_value = float(numeric_data.min())
                    max_value = float(numeric_data.max())
                    mean_value = float(numeric_data.mean())
                    median_value = float(numeric_data.median())
                    std_deviation = float(numeric_data.std())
            
            elif data_type == DataType.STRING:
                string_data = column_data.dropna().astype(str)
                if len(string_data) > 0:
                    lengths = string_data.str.len()
                    min_length = int(lengths.min())
                    max_length = int(lengths.max())
                    avg_length = float(lengths.mean())
            
            # Détection patterns
            patterns = []
            if self.enable_pattern_detection and data_type == DataType.STRING:
                patterns = self._detect_patterns(column_data)
            
            # Détection problèmes qualité
            quality_issues = self._detect_quality_issues(column_data, data_type)
            
            # Échantillon valeurs
            sample_values = self._get_sample_values(column_data, 5)
            
            return ColumnProfile(
                column_name=column_name,
                data_type=data_type,
                total_count=total_count,
                non_null_count=non_null_count,
                null_count=null_count,
                null_percentage=null_percentage,
                unique_count=unique_count,
                duplicate_count=duplicate_count,
                min_value=min_value,
                max_value=max_value,
                mean_value=mean_value,
                median_value=median_value,
                std_deviation=std_deviation,
                min_length=min_length,
                max_length=max_length,
                avg_length=avg_length,
                patterns=patterns,
                quality_issues=quality_issues,
                sample_values=sample_values
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur profilage colonne {column_name}: {e}")
            return ColumnProfile(
                column_name=column_name,
                data_type=DataType.UNKNOWN,
                total_count=0,
                non_null_count=0,
                null_count=0,
                null_percentage=0,
                unique_count=0,
                duplicate_count=0
            )
    
    def _detect_data_type(self, column_data: pd.Series) -> DataType:
        """Détection type de données"""
        try:
            # Éliminer les valeurs nulles pour l'analyse
            clean_data = column_data.dropna()
            
            if len(clean_data) == 0:
                return DataType.UNKNOWN
            
            # Test boolean
            if clean_data.dtype == 'bool' or all(val in [True, False, 0, 1, 'true', 'false', 'True', 'False'] for val in clean_data.head(10)):
                return DataType.BOOLEAN
            
            # Test numérique integer
            try:
                numeric_test = pd.to_numeric(clean_data, errors='coerce')
                if numeric_test.notna().all():
                    if all(float(val).is_integer() for val in numeric_test.head(10)):
                        return DataType.INTEGER
                    else:
                        return DataType.FLOAT
            except:
                pass
            
            # Test date/datetime
            try:
                date_test = pd.to_datetime(clean_data.head(10), errors='coerce')
                if date_test.notna().all():
                    sample_str = str(clean_data.iloc[0])
                    if 'T' in sample_str or ':' in sample_str:
                        return DataType.DATETIME
                    else:
                        return DataType.DATE
            except:
                pass
            
            # Test JSON
            try:
                for val in clean_data.head(5):
                    json.loads(str(val))
                return DataType.JSON
            except:
                pass
            
            # Par défaut string
            return DataType.STRING
            
        except Exception as e:
            logger.error(f"❌ Erreur détection type: {e}")
            return DataType.UNKNOWN
    
    def _detect_patterns(self, column_data: pd.Series) -> List[str]:
        """Détection patterns dans les données"""
        try:
            patterns_found = []
            clean_data = column_data.dropna().astype(str)
            
            if len(clean_data) == 0:
                return patterns_found
            
            # Test chaque pattern
            for pattern_name, pattern_regex in self.common_patterns.items():
                matches = 0
                for value in clean_data.head(20):  # Test sur échantillon
                    if re.match(pattern_regex, value):
                        matches += 1
                
                # Si >80% correspondent, considérer comme pattern
                if matches / min(len(clean_data), 20) > 0.8:
                    patterns_found.append(pattern_name)
            
            return patterns_found
            
        except Exception as e:
            logger.error(f"❌ Erreur détection patterns: {e}")
            return []
    
    def _detect_quality_issues(self, column_data: pd.Series, data_type: DataType) -> List[str]:
        """Détection problèmes qualité"""
        try:
            issues = []
            
            # Valeurs nulles excessives
            null_percentage = (column_data.isna().sum() / len(column_data)) * 100
            if null_percentage > 20:
                issues.append(QualityIssue.NULL_VALUES.value)
                self.metrics['quality_issues_detected'] += 1
            
            # Doublons excessifs
            if column_data.nunique() < len(column_data) * 0.5:
                issues.append(QualityIssue.DUPLICATES.value)
                self.metrics['quality_issues_detected'] += 1
            
            # Problèmes spécifiques selon type
            if data_type == DataType.STRING:
                string_data = column_data.dropna().astype(str)
                
                # Casse incohérente
                if len(string_data) > 0:
                    mixed_case = sum(1 for val in string_data.head(10) 
                                   if val != val.lower() and val != val.upper())
                    if mixed_case > len(string_data.head(10)) * 0.3:
                        issues.append(QualityIssue.INCONSISTENT_CASE.value)
                        self.metrics['quality_issues_detected'] += 1
                
                # Caractères spéciaux suspects
                special_chars = sum(1 for val in string_data.head(10)
                                  if any(char in val for char in ['<', '>', '{', '}', '[', ']']))
                if special_chars > 0:
                    issues.append(QualityIssue.SPECIAL_CHARACTERS.value)
                    self.metrics['quality_issues_detected'] += 1
            
            elif data_type in [DataType.INTEGER, DataType.FLOAT]:
                numeric_data = pd.to_numeric(column_data, errors='coerce').dropna()
                
                if len(numeric_data) > 0:
                    # Outliers (valeurs aberrantes)
                    Q1 = numeric_data.quantile(0.25)
                    Q3 = numeric_data.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = numeric_data[(numeric_data < Q1 - 1.5 * IQR) | (numeric_data > Q3 + 1.5 * IQR)]
                    
                    if len(outliers) / len(numeric_data) > 0.05:  # >5% outliers
                        issues.append(QualityIssue.OUTLIERS.value)
                        self.metrics['quality_issues_detected'] += 1
            
            return issues
            
        except Exception as e:
            logger.error(f"❌ Erreur détection problèmes qualité: {e}")
            return []
    
    def _get_sample_values(self, column_data: pd.Series, count: int) -> List[Any]:
        """Récupération échantillon de valeurs"""
        try:
            clean_data = column_data.dropna()
            if len(clean_data) == 0:
                return []
            
            sample_size = min(count, len(clean_data))
            sample = clean_data.sample(n=sample_size).tolist()
            
            # Conversion en types JSON sérialisables
            json_sample = []
            for val in sample:
                try:
                    if pd.isna(val):
                        json_sample.append(None)
                    elif isinstance(val, (int, float, str, bool)):
                        json_sample.append(val)
                    else:
                        json_sample.append(str(val))
                except:
                    json_sample.append(str(val))
            
            return json_sample
            
        except Exception as e:
            logger.error(f"❌ Erreur échantillon valeurs: {e}")
            return []
    
    def _detect_primary_keys(self, table_data: pd.DataFrame) -> List[str]:
        """Détection clés primaires (simulation)"""
        try:
            primary_keys = []
            
            for column in table_data.columns:
                # Critères pour clé primaire: unique + non null
                if (table_data[column].nunique() == len(table_data) and 
                    table_data[column].notna().all()):
                    
                    # Bonus si nom contient 'id'
                    if 'id' in column.lower():
                        primary_keys.append(column)
                        break  # Une seule clé primaire normalement
            
            return primary_keys
            
        except Exception as e:
            logger.error(f"❌ Erreur détection clés primaires: {e}")
            return []
    
    def _detect_foreign_keys(self, table_name: str, table_data: pd.DataFrame) -> List[Dict[str, str]]:
        """Détection clés étrangères (simulation)"""
        try:
            foreign_keys = []
            
            for column in table_data.columns:
                # Si colonne se termine par '_id' et n'est pas clé primaire
                if column.endswith('_id') and column != f"{table_name}_id":
                    referenced_table = column.replace('_id', 's')  # users_id -> users
                    
                    foreign_keys.append({
                        'column': column,
                        'referenced_table': referenced_table,
                        'referenced_column': column
                    })
            
            return foreign_keys
            
        except Exception as e:
            logger.error(f"❌ Erreur détection clés étrangères: {e}")
            return []
    
    def _detect_indexes(self, table_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Détection index (simulation)"""
        try:
            indexes = []
            
            # Simulation index sur colonnes avec 'id' ou beaucoup de valeurs uniques
            for column in table_data.columns:
                unique_ratio = table_data[column].nunique() / len(table_data)
                
                if 'id' in column.lower() or unique_ratio > 0.8:
                    indexes.append({
                        'name': f"idx_{column}",
                        'columns': [column],
                        'type': 'btree',
                        'unique': unique_ratio == 1.0
                    })
            
            return indexes
            
        except Exception as e:
            logger.error(f"❌ Erreur détection index: {e}")
            return []
    
    def _detect_constraints(self, table_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Détection contraintes (simulation)"""
        try:
            constraints = []
            
            for column in table_data.columns:
                # Contrainte NOT NULL
                if table_data[column].notna().all():
                    constraints.append({
                        'type': 'not_null',
                        'column': column,
                        'description': f'{column} NOT NULL'
                    })
                
                # Contrainte UNIQUE
                if table_data[column].nunique() == len(table_data):
                    constraints.append({
                        'type': 'unique',
                        'column': column,
                        'description': f'{column} UNIQUE'
                    })
            
            return constraints
            
        except Exception as e:
            logger.error(f"❌ Erreur détection contraintes: {e}")
            return []
    
    async def _detect_relationships(self, table_profiles: List[TableProfile]) -> List[Dict[str, Any]]:
        """Détection relations entre tables"""
        try:
            relationships = []
            
            # Créer un mapping table -> clés primaires
            pk_mapping = {}
            for table_profile in table_profiles:
                if table_profile.primary_keys:
                    pk_mapping[table_profile.table_name] = table_profile.primary_keys[0]
            
            # Détecter relations basées sur clés étrangères
            for table_profile in table_profiles:
                for fk in table_profile.foreign_keys:
                    referenced_table = fk['referenced_table']
                    
                    if referenced_table in pk_mapping:
                        relationships.append({
                            'type': 'foreign_key',
                            'source_table': table_profile.table_name,
                            'source_column': fk['column'],
                            'target_table': referenced_table,
                            'target_column': fk['referenced_column'],
                            'relationship': 'many_to_one'
                        })
            
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Erreur détection relations: {e}")
            return []
    
    async def get_dataset_profile(self, dataset_id: str) -> Optional[DatasetProfile]:
        """Récupération profil dataset"""
        try:
            return self.dataset_profiles.get(dataset_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération profil: {e}")
            return None
    
    async def get_table_profile(self, dataset_id: str, table_name: str) -> Optional[TableProfile]:
        """Récupération profil table"""
        try:
            dataset_profile = self.dataset_profiles.get(dataset_id)
            if not dataset_profile:
                return None
            
            for table_profile in dataset_profile.table_profiles:
                if table_profile.table_name == table_name:
                    return table_profile
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération profil table: {e}")
            return None
    
    async def get_column_profile(self, dataset_id: str, table_name: str, column_name: str) -> Optional[ColumnProfile]:
        """Récupération profil colonne"""
        try:
            table_profile = await self.get_table_profile(dataset_id, table_name)
            if not table_profile:
                return None
            
            for column_profile in table_profile.column_profiles:
                if column_profile.column_name == column_name:
                    return column_profile
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération profil colonne: {e}")
            return None
    
    async def get_quality_report(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Rapport qualité dataset"""
        try:
            dataset_profile = self.dataset_profiles.get(dataset_id)
            if not dataset_profile:
                return None
            
            # Compilation problèmes qualité
            quality_issues = {}
            column_issues = []
            
            for table_profile in dataset_profile.table_profiles:
                for column_profile in table_profile.column_profiles:
                    for issue in column_profile.quality_issues:
                        if issue not in quality_issues:
                            quality_issues[issue] = 0
                        quality_issues[issue] += 1
                        
                        column_issues.append({
                            'table': table_profile.table_name,
                            'column': column_profile.column_name,
                            'issue': issue,
                            'null_percentage': column_profile.null_percentage
                        })
            
            # Statistiques globales
            total_columns = sum(len(tp.column_profiles) for tp in dataset_profile.table_profiles)
            issues_count = sum(quality_issues.values())
            
            return {
                'dataset_id': dataset_id,
                'overall_quality_score': dataset_profile.overall_quality_score,
                'total_tables': len(dataset_profile.table_profiles),
                'total_columns': total_columns,
                'total_records': dataset_profile.total_records,
                'quality_issues_summary': quality_issues,
                'issues_percentage': (issues_count / total_columns) * 100 if total_columns > 0 else 0,
                'column_issues': column_issues[:50],  # Limiter pour performance
                'recommendations': self._generate_quality_recommendations(quality_issues),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur rapport qualité: {e}")
            return None
    
    def _generate_quality_recommendations(self, quality_issues: Dict[str, int]) -> List[str]:
        """Génération recommandations qualité"""
        try:
            recommendations = []
            
            if QualityIssue.NULL_VALUES.value in quality_issues:
                recommendations.append("🔧 Implémenter validation NOT NULL pour colonnes critiques")
                recommendations.append("📊 Analyser sources de données nulles et corriger en amont")
            
            if QualityIssue.DUPLICATES.value in quality_issues:
                recommendations.append("🧹 Nettoyer doublons avec scripts de déduplication")
                recommendations.append("🔒 Ajouter contraintes UNIQUE sur colonnes identifiantes")
            
            if QualityIssue.OUTLIERS.value in quality_issues:
                recommendations.append("📈 Analyser valeurs aberrantes et définir règles métier")
                recommendations.append("⚡ Implémenter validation de plage pour données numériques")
            
            if QualityIssue.INCONSISTENT_CASE.value in quality_issues:
                recommendations.append("🎯 Standardiser casse des données textuelles")
                recommendations.append("🔧 Implémenter normalisation automatique en amont")
            
            if not recommendations:
                recommendations.append("✅ Qualité de données acceptable - Maintenir bonnes pratiques")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur génération recommandations: {e}")
            return []
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while True:
            try:
                await asyncio.sleep(60)
                
                # Mise à jour métriques
                self.metrics['datasets_profiled'] = len(self.dataset_profiles)
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring: {e}")
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 heure
                
                # Nettoyage anciens jobs
                await self._cleanup_old_jobs()
                
                # Archivage anciens profils
                await self._archive_old_profiles()
                
            except Exception as e:
                logger.error(f"❌ Erreur maintenance: {e}")
    
    async def _cleanup_old_jobs(self):
        """Nettoyage anciens jobs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            old_jobs = []
            for job_id, job in self.profiling_jobs.items():
                if (job.completed_at and job.completed_at < cutoff_date and
                    job.status in ['completed', 'failed']):
                    old_jobs.append(job_id)
            
            for job_id in old_jobs:
                del self.profiling_jobs[job_id]
            
            if old_jobs:
                logger.info(f"🧹 {len(old_jobs)} anciens jobs supprimés")
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage jobs: {e}")
    
    async def _archive_old_profiles(self):
        """Archivage anciens profils"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            old_profiles = []
            for dataset_id, profile in self.dataset_profiles.items():
                if profile.profiled_at < cutoff_date:
                    old_profiles.append(dataset_id)
            
            # En production, archiver vers stockage long terme
            for dataset_id in old_profiles:
                # await archive_service.archive_profile(self.dataset_profiles[dataset_id])
                del self.dataset_profiles[dataset_id]
            
            if old_profiles:
                logger.info(f"📦 {len(old_profiles)} profils archivés")
                
        except Exception as e:
            logger.error(f"❌ Erreur archivage profils: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        try:
            return {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics,
                'components': {
                    'profiling_engine': True,
                    'quality_analysis': self.enable_statistical_analysis,
                    'pattern_detection': self.enable_pattern_detection,
                    'statistics_calculation': True
                },
                'resource_usage': {
                    'active_jobs': len(self.active_jobs),
                    'total_jobs': len(self.profiling_jobs),
                    'profiles_stored': len(self.dataset_profiles),
                    'max_concurrent': self.max_concurrent_jobs
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé service"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'configuration': {
                    'max_concurrent_jobs': self.max_concurrent_jobs,
                    'sample_size': self.sample_size,
                    'statistical_analysis': self.enable_statistical_analysis,
                    'pattern_detection': self.enable_pattern_detection
                },
                'performance_metrics': self.metrics,
                'profiling_overview': {
                    'total_jobs': len(self.profiling_jobs),
                    'active_jobs': len(self.active_jobs),
                    'datasets_profiled': len(self.dataset_profiles),
                    'patterns_detected': len(self.common_patterns)
                },
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut service: {e}")
            return {'error': str(e)}

# Instance globale
data_profiling_service = DataProfilingService()

async def main():
    """Test du service"""
    try:
        print("📊 Test Data Profiling Service")
        
        success = await data_profiling_service.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test profilage dataset
        job_id = await data_profiling_service.create_profiling_job(
            dataset_id="test_db_001",
            job_type="full",
            config={'enable_quality_analysis': True}
        )
        
        print(f"🚀 Job profilage créé: {job_id}")
        
        # Attendre completion
        await asyncio.sleep(3)
        
        # Récupération profil
        dataset_profile = await data_profiling_service.get_dataset_profile("test_db_001")
        if dataset_profile:
            print(f"📊 Dataset profilé: {dataset_profile.dataset_name}")
            print(f"   Tables: {len(dataset_profile.table_profiles)}")
            print(f"   Score qualité: {dataset_profile.overall_quality_score:.1f}%")
        
        # Rapport qualité
        quality_report = await data_profiling_service.get_quality_report("test_db_001")
        if quality_report:
            print(f"📋 Rapport qualité: {quality_report}")
        
        # Statut service
        status = await data_profiling_service.get_service_status()
        print(f"📊 Statut service: {status}")
        
        print("✅ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())