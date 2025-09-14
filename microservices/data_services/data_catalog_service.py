"""
🗂️ Data Catalog Service - Catalogue de Données Intelligent Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service de catalogue intelligent pour découverte et gouvernance des données.
Classification automatique avec IA et métadonnées enrichies pour data discovery.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass, field
from enum import Enum
import uuid

from elasticsearch import AsyncElasticsearch
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class DatasetType(Enum):
    """Types de datasets"""
    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    STREAM = "stream"
    API = "api"
    MODEL = "model"


class DataClassification(Enum):
    """Classifications de sensibilité des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"


@dataclass
class DataColumn:
    """Définition d'une colonne de données"""
    name: str
    data_type: str
    nullable: bool = True
    description: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    sample_values: List[Any] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    classification: Optional[DataClassification] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class DatasetMetadata:
    """Métadonnées complètes d'un dataset"""
    dataset_id: str
    name: str
    description: str
    dataset_type: DatasetType
    source: str
    owner: str
    columns: List[DataColumn]
    location: str
    created_at: datetime
    updated_at: datetime
    classification: DataClassification = DataClassification.INTERNAL
    tags: List[str] = field(default_factory=list)
    lineage: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"
    compliance_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataDiscoveryQuery:
    """Requête de découverte de données"""
    keywords: Optional[str] = None
    dataset_type: Optional[DatasetType] = None
    classification: Optional[DataClassification] = None
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    date_range: Optional[Dict[str, datetime]] = None
    quality_threshold: Optional[float] = None


class DataCatalogService:
    """Service de catalogue intelligent pour données enterprise"""
    
    def __init__(self):
        self.catalog_index = "ainflue_data_catalog"
        self.elasticsearch_client = None
        self.datasets: Dict[str, DatasetMetadata] = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classification_models = {}
        
        # Configuration des détecteurs
        self.pii_detectors = self._initialize_pii_detectors()
        self.quality_rules = self._initialize_quality_rules()
        
        # Cache pour les recherches fréquentes
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def initialize_elasticsearch(self, host: str = "localhost", port: int = 9200):
        """Initialise la connexion Elasticsearch"""
        try:
            self.elasticsearch_client = AsyncElasticsearch([f"http://{host}:{port}"])
            await self._create_catalog_index()
            logger.info("Data catalog Elasticsearch initialized")
        except Exception as e:
            logger.error(f"Error initializing Elasticsearch: {e}")
            raise
    
    async def register_dataset(
        self,
        dataset_metadata: DatasetMetadata,
        auto_classify: bool = True,
        auto_profile: bool = True
    ) -> Dict[str, Any]:
        """Enregistre un nouveau dataset dans le catalogue"""
        
        try:
            # Auto-classification si demandée
            if auto_classify:
                await self._auto_classify_dataset(dataset_metadata)
            
            # Auto-profilage si demandé
            if auto_profile:
                await self._auto_profile_dataset(dataset_metadata)
            
            # Calculer score de qualité
            dataset_metadata.quality_score = await self._calculate_quality_score(dataset_metadata)
            
            # Enrichir les métadonnées
            await self._enrich_metadata(dataset_metadata)
            
            # Stocker dans le catalogue local
            self.datasets[dataset_metadata.dataset_id] = dataset_metadata
            
            # Indexer dans Elasticsearch
            if self.elasticsearch_client:
                await self._index_dataset(dataset_metadata)
            
            logger.info(f"Dataset {dataset_metadata.dataset_id} registered successfully")
            
            return {
                'success': True,
                'dataset_id': dataset_metadata.dataset_id,
                'quality_score': dataset_metadata.quality_score,
                'classification': dataset_metadata.classification.value,
                'message': 'Dataset registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error registering dataset {dataset_metadata.dataset_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _auto_classify_dataset(self, dataset_metadata: DatasetMetadata) -> None:
        """Classification automatique du dataset"""
        
        # Classification basée sur les colonnes
        has_pii = False
        has_financial = False
        has_sensitive = False
        
        for column in dataset_metadata.columns:
            # Détection PII
            if self._is_pii_column(column):
                has_pii = True
                column.classification = DataClassification.PII
            
            # Détection données financières
            if self._is_financial_column(column):
                has_financial = True
            
            # Détection données sensibles
            if self._is_sensitive_column(column):
                has_sensitive = True
        
        # Classification du dataset global
        if has_pii:
            dataset_metadata.classification = DataClassification.RESTRICTED
        elif has_financial or has_sensitive:
            dataset_metadata.classification = DataClassification.CONFIDENTIAL
        else:
            # Classification basée sur le nom/description
            content = f"{dataset_metadata.name} {dataset_metadata.description}".lower()
            
            if any(keyword in content for keyword in ['public', 'open', 'general']):
                dataset_metadata.classification = DataClassification.PUBLIC
            elif any(keyword in content for keyword in ['internal', 'employee']):
                dataset_metadata.classification = DataClassification.INTERNAL
            else:
                dataset_metadata.classification = DataClassification.INTERNAL
    
    def _is_pii_column(self, column: DataColumn) -> bool:
        """Détecte si une colonne contient des PII"""
        
        pii_patterns = [
            'email', 'phone', 'ssn', 'social_security', 'passport',
            'driver_license', 'credit_card', 'bank_account', 'address',
            'first_name', 'last_name', 'full_name', 'birth_date', 'dob'
        ]
        
        column_name_lower = column.name.lower()
        
        return any(pattern in column_name_lower for pattern in pii_patterns)
    
    def _is_financial_column(self, column: DataColumn) -> bool:
        """Détecte si une colonne contient des données financières"""
        
        financial_patterns = [
            'salary', 'income', 'revenue', 'cost', 'price', 'amount',
            'payment', 'transaction', 'balance', 'account', 'billing'
        ]
        
        column_name_lower = column.name.lower()
        
        return any(pattern in column_name_lower for pattern in financial_patterns)
    
    def _is_sensitive_column(self, column: DataColumn) -> bool:
        """Détecte si une colonne contient des données sensibles"""
        
        sensitive_patterns = [
            'password', 'token', 'secret', 'key', 'confidential',
            'private', 'internal', 'restricted'
        ]
        
        column_name_lower = column.name.lower()
        
        return any(pattern in column_name_lower for pattern in sensitive_patterns)
    
    async def _auto_profile_dataset(self, dataset_metadata: DatasetMetadata) -> None:
        """Profilage automatique du dataset"""
        
        try:
            # Simuler le chargement d'un échantillon de données
            sample_data = await self._load_sample_data(dataset_metadata)
            
            if sample_data is not None and not sample_data.empty:
                # Profiler chaque colonne
                for column in dataset_metadata.columns:
                    if column.name in sample_data.columns:
                        await self._profile_column(column, sample_data[column.name])
                
                # Statistiques globales du dataset
                dataset_metadata.usage_stats.update({
                    'row_count': len(sample_data),
                    'column_count': len(sample_data.columns),
                    'memory_usage_mb': sample_data.memory_usage(deep=True).sum() / 1024 / 1024,
                    'null_percentage': sample_data.isnull().sum().sum() / (len(sample_data) * len(sample_data.columns))
                })
                
        except Exception as e:
            logger.warning(f"Error profiling dataset {dataset_metadata.dataset_id}: {e}")
    
    async def _load_sample_data(self, dataset_metadata: DatasetMetadata) -> Optional[pd.DataFrame]:
        """Charge un échantillon de données pour profilage"""
        
        # Simuler le chargement de données selon le type
        if dataset_metadata.dataset_type == DatasetType.TABLE:
            # Simuler données tabulaires
            np.random.seed(42)
            n_rows = 1000
            
            data = {}
            for column in dataset_metadata.columns:
                if column.data_type.lower() in ['int', 'integer', 'bigint']:
                    data[column.name] = np.random.randint(1, 1000, n_rows)
                elif column.data_type.lower() in ['float', 'double', 'decimal']:
                    data[column.name] = np.random.uniform(0, 100, n_rows)
                elif column.data_type.lower() in ['string', 'varchar', 'text']:
                    data[column.name] = [f"value_{i}" for i in range(n_rows)]
                elif column.data_type.lower() in ['date', 'datetime', 'timestamp']:
                    data[column.name] = pd.date_range('2024-01-01', periods=n_rows, freq='D')
                else:
                    data[column.name] = [f"data_{i}" for i in range(n_rows)]
            
            return pd.DataFrame(data)
        
        # Pour d'autres types, retourner None
        return None
    
    async def _profile_column(self, column: DataColumn, data: pd.Series) -> None:
        """Profile une colonne spécifique"""
        
        try:
            stats = {}
            
            # Statistiques de base
            stats['count'] = len(data)
            stats['null_count'] = data.isnull().sum()
            stats['null_percentage'] = stats['null_count'] / stats['count'] * 100
            stats['unique_count'] = data.nunique()
            stats['unique_percentage'] = stats['unique_count'] / stats['count'] * 100
            
            # Statistiques spécifiques au type
            if pd.api.types.is_numeric_dtype(data):
                stats.update({
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'mean': float(data.mean()),
                    'median': float(data.median()),
                    'std': float(data.std()),
                    'q25': float(data.quantile(0.25)),
                    'q75': float(data.quantile(0.75))
                })
            
            elif pd.api.types.is_string_dtype(data):
                stats.update({
                    'min_length': data.str.len().min(),
                    'max_length': data.str.len().max(),
                    'avg_length': data.str.len().mean()
                })
            
            # Échantillons de valeurs
            column.sample_values = data.dropna().head(10).tolist()
            
            # Mise à jour des statistiques
            column.statistics = stats
            
        except Exception as e:
            logger.warning(f"Error profiling column {column.name}: {e}")
    
    async def _calculate_quality_score(self, dataset_metadata: DatasetMetadata) -> float:
        """Calcule un score de qualité pour le dataset"""
        
        score = 100.0
        
        # Facteurs de qualité
        
        # 1. Complétude des métadonnées (30%)
        metadata_score = 0
        if dataset_metadata.description:
            metadata_score += 10
        if dataset_metadata.owner:
            metadata_score += 10
        if dataset_metadata.tags:
            metadata_score += 5
        if len(dataset_metadata.columns) > 0:
            metadata_score += 5
        
        # 2. Qualité des colonnes (40%)
        column_score = 0
        if dataset_metadata.columns:
            documented_columns = sum(1 for col in dataset_metadata.columns if col.description)
            column_score = (documented_columns / len(dataset_metadata.columns)) * 40
        
        # 3. Fraîcheur des données (20%)
        freshness_score = 20
        if dataset_metadata.updated_at:
            days_old = (datetime.utcnow() - dataset_metadata.updated_at).days
            if days_old > 365:
                freshness_score = 0
            elif days_old > 90:
                freshness_score = 10
            elif days_old > 30:
                freshness_score = 15
        
        # 4. Utilisation et popularité (10%)
        usage_score = 10
        if dataset_metadata.usage_stats.get('access_count', 0) == 0:
            usage_score = 0
        elif dataset_metadata.usage_stats.get('access_count', 0) < 10:
            usage_score = 5
        
        total_score = metadata_score + column_score + freshness_score + usage_score
        
        return min(total_score, 100.0)
    
    async def _enrich_metadata(self, dataset_metadata: DatasetMetadata) -> None:
        """Enrichit les métadonnées avec des informations automatiques"""
        
        # Tags automatiques basés sur le contenu
        auto_tags = await self._generate_auto_tags(dataset_metadata)
        dataset_metadata.tags.extend(auto_tags)
        
        # Déduplication des tags
        dataset_metadata.tags = list(set(dataset_metadata.tags))
        
        # Informations de compliance
        await self._add_compliance_info(dataset_metadata)
    
    async def _generate_auto_tags(self, dataset_metadata: DatasetMetadata) -> List[str]:
        """Génère des tags automatiques"""
        
        auto_tags = []
        
        # Tags basés sur le type
        auto_tags.append(f"type:{dataset_metadata.dataset_type.value}")
        
        # Tags basés sur la classification
        auto_tags.append(f"classification:{dataset_metadata.classification.value}")
        
        # Tags basés sur les colonnes
        column_types = set(col.data_type.lower() for col in dataset_metadata.columns)
        for col_type in column_types:
            auto_tags.append(f"contains:{col_type}")
        
        # Tags basés sur la source
        if dataset_metadata.source:
            auto_tags.append(f"source:{dataset_metadata.source.lower()}")
        
        # Tags basés sur le contenu textuel
        content = f"{dataset_metadata.name} {dataset_metadata.description}".lower()
        
        if 'user' in content or 'customer' in content:
            auto_tags.append('contains:user_data')
        if 'transaction' in content or 'payment' in content:
            auto_tags.append('contains:financial_data')
        if 'log' in content or 'event' in content:
            auto_tags.append('contains:log_data')
        
        return auto_tags
    
    async def _add_compliance_info(self, dataset_metadata: DatasetMetadata) -> None:
        """Ajoute des informations de compliance"""
        
        compliance_info = {}
        
        # GDPR
        if dataset_metadata.classification in [DataClassification.PII, DataClassification.RESTRICTED]:
            compliance_info['gdpr_applicable'] = True
            compliance_info['retention_period'] = '7_years'
            compliance_info['requires_consent'] = True
        else:
            compliance_info['gdpr_applicable'] = False
        
        # SOX (si données financières)
        has_financial = any(self._is_financial_column(col) for col in dataset_metadata.columns)
        compliance_info['sox_applicable'] = has_financial
        
        # PCI DSS (si données de carte de crédit)
        has_payment = any('credit_card' in col.name.lower() or 'payment' in col.name.lower() 
                         for col in dataset_metadata.columns)
        compliance_info['pci_applicable'] = has_payment
        
        dataset_metadata.compliance_info = compliance_info
    
    async def _index_dataset(self, dataset_metadata: DatasetMetadata) -> None:
        """Indexe le dataset dans Elasticsearch"""
        
        try:
            # Préparer le document pour l'indexation
            doc = {
                'dataset_id': dataset_metadata.dataset_id,
                'name': dataset_metadata.name,
                'description': dataset_metadata.description,
                'dataset_type': dataset_metadata.dataset_type.value,
                'source': dataset_metadata.source,
                'owner': dataset_metadata.owner,
                'classification': dataset_metadata.classification.value,
                'tags': dataset_metadata.tags,
                'lineage': dataset_metadata.lineage,
                'quality_score': dataset_metadata.quality_score,
                'created_at': dataset_metadata.created_at.isoformat(),
                'updated_at': dataset_metadata.updated_at.isoformat(),
                'column_names': [col.name for col in dataset_metadata.columns],
                'column_types': [col.data_type for col in dataset_metadata.columns],
                'usage_stats': dataset_metadata.usage_stats,
                'compliance_info': dataset_metadata.compliance_info
            }
            
            # Indexer
            await self.elasticsearch_client.index(
                index=self.catalog_index,
                id=dataset_metadata.dataset_id,
                body=doc
            )
            
        except Exception as e:
            logger.error(f"Error indexing dataset {dataset_metadata.dataset_id}: {e}")
    
    async def discover_datasets(self, query: DataDiscoveryQuery) -> Dict[str, Any]:
        """Découvre des datasets selon les critères"""
        
        try:
            # Vérifier le cache
            cache_key = self._generate_discovery_cache_key(query)
            if cache_key in self.search_cache:
                cached_result = self.search_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result['result']
            
            # Recherche dans Elasticsearch si disponible
            if self.elasticsearch_client:
                results = await self._elasticsearch_discovery(query)
            else:
                results = await self._local_discovery(query)
            
            # Enrichir les résultats
            enriched_results = await self._enrich_discovery_results(results)
            
            # Mettre en cache
            self._cache_discovery_result(cache_key, enriched_results)
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error in dataset discovery: {e}")
            return {
                'datasets': [],
                'total': 0,
                'error': str(e)
            }
    
    async def _elasticsearch_discovery(self, query: DataDiscoveryQuery) -> Dict[str, Any]:
        """Recherche avec Elasticsearch"""
        
        # Construction de la requête Elasticsearch
        search_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [
                {"quality_score": {"order": "desc"}},
                {"updated_at": {"order": "desc"}}
            ],
            "size": 50
        }
        
        # Recherche textuelle
        if query.keywords:
            search_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query.keywords,
                    "fields": [
                        "name^3",
                        "description^2", 
                        "tags^2",
                        "column_names",
                        "owner"
                    ]
                }
            })
        
        # Filtres
        if query.dataset_type:
            search_body["query"]["bool"]["filter"].append({
                "term": {"dataset_type": query.dataset_type.value}
            })
        
        if query.classification:
            search_body["query"]["bool"]["filter"].append({
                "term": {"classification": query.classification.value}
            })
        
        if query.owner:
            search_body["query"]["bool"]["filter"].append({
                "term": {"owner": query.owner}
            })
        
        if query.tags:
            search_body["query"]["bool"]["filter"].append({
                "terms": {"tags": query.tags}
            })
        
        if query.quality_threshold:
            search_body["query"]["bool"]["filter"].append({
                "range": {"quality_score": {"gte": query.quality_threshold}}
            })
        
        if query.date_range:
            date_filter = {"range": {"updated_at": {}}}
            if 'start' in query.date_range:
                date_filter["range"]["updated_at"]["gte"] = query.date_range['start'].isoformat()
            if 'end' in query.date_range:
                date_filter["range"]["updated_at"]["lte"] = query.date_range['end'].isoformat()
            search_body["query"]["bool"]["filter"].append(date_filter)
        
        # Exécuter la recherche
        response = await self.elasticsearch_client.search(
            index=self.catalog_index,
            body=search_body
        )
        
        return {
            'datasets': [hit['_source'] for hit in response['hits']['hits']],
            'total': response['hits']['total']['value'],
            'max_score': response['hits']['max_score']
        }
    
    async def _local_discovery(self, query: DataDiscoveryQuery) -> Dict[str, Any]:
        """Recherche locale (fallback)"""
        
        matching_datasets = []
        
        for dataset in self.datasets.values():
            if self._matches_query(dataset, query):
                matching_datasets.append(self._dataset_to_dict(dataset))
        
        # Trier par score de qualité
        matching_datasets.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return {
            'datasets': matching_datasets[:50],  # Limiter à 50 résultats
            'total': len(matching_datasets)
        }
    
    def _matches_query(self, dataset: DatasetMetadata, query: DataDiscoveryQuery) -> bool:
        """Vérifie si un dataset correspond à la requête"""
        
        # Filtres exacts
        if query.dataset_type and dataset.dataset_type != query.dataset_type:
            return False
        
        if query.classification and dataset.classification != query.classification:
            return False
        
        if query.owner and dataset.owner != query.owner:
            return False
        
        if query.quality_threshold and dataset.quality_score < query.quality_threshold:
            return False
        
        # Tags
        if query.tags and not any(tag in dataset.tags for tag in query.tags):
            return False
        
        # Date range
        if query.date_range:
            if 'start' in query.date_range and dataset.updated_at < query.date_range['start']:
                return False
            if 'end' in query.date_range and dataset.updated_at > query.date_range['end']:
                return False
        
        # Recherche textuelle
        if query.keywords:
            searchable_text = f"{dataset.name} {dataset.description} {' '.join(dataset.tags)}".lower()
            keywords_lower = query.keywords.lower()
            if keywords_lower not in searchable_text:
                return False
        
        return True
    
    def _dataset_to_dict(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Convertit un dataset en dictionnaire"""
        
        return {
            'dataset_id': dataset.dataset_id,
            'name': dataset.name,
            'description': dataset.description,
            'dataset_type': dataset.dataset_type.value,
            'source': dataset.source,
            'owner': dataset.owner,
            'classification': dataset.classification.value,
            'tags': dataset.tags,
            'quality_score': dataset.quality_score,
            'created_at': dataset.created_at.isoformat(),
            'updated_at': dataset.updated_at.isoformat(),
            'column_count': len(dataset.columns),
            'usage_stats': dataset.usage_stats
        }
    
    async def _enrich_discovery_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les résultats de découverte"""
        
        # Ajouter des recommandations
        recommendations = await self._generate_recommendations(results['datasets'])
        
        # Ajouter des facettes pour la navigation
        facets = await self._calculate_facets(results['datasets'])
        
        return {
            **results,
            'recommendations': recommendations,
            'facets': facets,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _generate_recommendations(self, datasets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur les résultats"""
        
        recommendations = []
        
        # Recommandations basées sur la qualité
        low_quality_datasets = [d for d in datasets if d.get('quality_score', 0) < 50]
        if low_quality_datasets:
            recommendations.append({
                'type': 'quality_improvement',
                'message': f'{len(low_quality_datasets)} datasets have low quality scores',
                'action': 'Review and improve dataset documentation',
                'datasets': [d['dataset_id'] for d in low_quality_datasets[:5]]
            })
        
        # Recommandations basées sur l'usage
        unused_datasets = [d for d in datasets if d.get('usage_stats', {}).get('access_count', 0) == 0]
        if unused_datasets:
            recommendations.append({
                'type': 'usage_promotion',
                'message': f'{len(unused_datasets)} datasets are not being used',
                'action': 'Consider promoting or archiving these datasets',
                'datasets': [d['dataset_id'] for d in unused_datasets[:5]]
            })
        
        return recommendations
    
    async def _calculate_facets(self, datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les facettes pour la navigation"""
        
        facets = {}
        
        # Facettes par type
        type_counts = {}
        for dataset in datasets:
            dataset_type = dataset.get('dataset_type', 'unknown')
            type_counts[dataset_type] = type_counts.get(dataset_type, 0) + 1
        facets['types'] = type_counts
        
        # Facettes par classification
        classification_counts = {}
        for dataset in datasets:
            classification = dataset.get('classification', 'unknown')
            classification_counts[classification] = classification_counts.get(classification, 0) + 1
        facets['classifications'] = classification_counts
        
        # Facettes par propriétaire
        owner_counts = {}
        for dataset in datasets:
            owner = dataset.get('owner', 'unknown')
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
        facets['owners'] = dict(list(owner_counts.items())[:10])  # Top 10 owners
        
        return facets
    
    def _generate_discovery_cache_key(self, query: DataDiscoveryQuery) -> str:
        """Génère une clé de cache pour la requête de découverte"""
        
        import hashlib
        
        key_components = [
            query.keywords or '',
            query.dataset_type.value if query.dataset_type else '',
            query.classification.value if query.classification else '',
            query.owner or '',
            ','.join(sorted(query.tags)),
            str(query.quality_threshold) if query.quality_threshold else '',
            json.dumps(query.date_range, default=str, sort_keys=True) if query.date_range else ''
        ]
        
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Vérifie si le résultat en cache est encore valide"""
        
        cached_time = cached_result['timestamp']
        return (datetime.utcnow() - cached_time).seconds < self.cache_ttl
    
    def _cache_discovery_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Met en cache un résultat de découverte"""
        
        self.search_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.utcnow()
        }
        
        # Limiter la taille du cache
        if len(self.search_cache) > 100:
            oldest_key = min(self.search_cache.keys(), 
                           key=lambda k: self.search_cache[k]['timestamp'])
            del self.search_cache[oldest_key]
    
    async def _create_catalog_index(self) -> None:
        """Crée l'index Elasticsearch pour le catalogue"""
        
        if not self.elasticsearch_client:
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "dataset_id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "dataset_type": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "owner": {"type": "keyword"},
                    "classification": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "lineage": {"type": "keyword"},
                    "quality_score": {"type": "float"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "column_names": {"type": "keyword"},
                    "column_types": {"type": "keyword"},
                    "usage_stats": {"type": "object"},
                    "compliance_info": {"type": "object"}
                }
            }
        }
        
        try:
            exists = await self.elasticsearch_client.indices.exists(index=self.catalog_index)
            if not exists:
                await self.elasticsearch_client.indices.create(
                    index=self.catalog_index,
                    body=mapping
                )
                logger.info(f"Catalog index {self.catalog_index} created")
        except Exception as e:
            logger.error(f"Error creating catalog index: {e}")
    
    def _initialize_pii_detectors(self) -> Dict[str, Any]:
        """Initialise les détecteurs PII"""
        
        return {
            'email_pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_pattern': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn_pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card_pattern': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }
    
    def _initialize_quality_rules(self) -> List[Dict[str, Any]]:
        """Initialise les règles de qualité"""
        
        return [
            {
                'name': 'description_required',
                'weight': 20,
                'condition': lambda dataset: bool(dataset.description)
            },
            {
                'name': 'owner_required',
                'weight': 15,
                'condition': lambda dataset: bool(dataset.owner)
            },
            {
                'name': 'tags_present',
                'weight': 10,
                'condition': lambda dataset: len(dataset.tags) > 0
            },
            {
                'name': 'columns_documented',
                'weight': 25,
                'condition': lambda dataset: all(col.description for col in dataset.columns)
            },
            {
                'name': 'recent_update',
                'weight': 15,
                'condition': lambda dataset: (datetime.utcnow() - dataset.updated_at).days < 90
            },
            {
                'name': 'has_usage',
                'weight': 15,
                'condition': lambda dataset: dataset.usage_stats.get('access_count', 0) > 0
            }
        ]


# Instance globale du service
data_catalog_service = DataCatalogService()