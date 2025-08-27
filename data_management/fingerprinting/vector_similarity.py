"""
🔍 Vector Similarity Engine - IA Influencer Agent Platform Enterprise
====================================================================
Module: backend/data_management/fingerprinting/vector_similarity.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Vector Similarity Engine - Ultra Enterprise Production-Ready
Responsibility: Advanced vector indexing, similarity search with FAISS and Elasticsearch
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC VECTOR SIMILARITY:
Content Fingerprints → Vector Extraction → FAISS Indexing → Real-time Similarity Search → 
Threshold Matching → Violation Detection → Alert Generation → Evidence Collection → 
Automated Takedown → Revenue Recovery

VECTOR SIMILARITY TECHNOLOGIES:
├── 🔍 FAISS (Facebook AI Similarity Search)
├── 🔎 Elasticsearch (Full-text + Vector Search)
├── 📊 Cosine Similarity (Angular Distance)
├── 📐 Euclidean Distance (L2 Norm)
├── 🎯 Manhattan Distance (L1 Norm)
├── ⚡ GPU Acceleration (CUDA Support)
├── 🚀 Distributed Search (Multi-node)
└── 🛡️ Real-time Monitoring (Instant Detection)
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import numpy as np
import asyncio
import logging
import pickle
import json
import time
from datetime import datetime
from pathlib import Path
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# FAISS for vector similarity
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available - install faiss-cpu or faiss-gpu")

# Elasticsearch for hybrid search
try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk, scan
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    logging.warning("Elasticsearch not available - install elasticsearch")

# Scientific computing
try:
    from scipy.spatial.distance import cosine, euclidean, cityblock
    from scipy.sparse import csr_matrix
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available - install scipy")

# Machine learning utilities
try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.preprocessing import normalize
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - install scikit-learn")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

@dataclass
class VectorSimilarityConfig:
    """Configuration avancée pour la recherche de similarité vectorielle"""
    
    # Configuration FAISS
    faiss_enabled: bool = True
    faiss_index_type: str = "IVF"  # IVF, HNSW, Flat, LSH
    faiss_nlist: int = 100  # Nombre de clusters pour IVF
    faiss_nprobe: int = 10  # Nombre de clusters à rechercher
    faiss_m: int = 16  # Paramètre pour HNSW
    faiss_ef_construction: int = 200  # Construction HNSW
    faiss_ef_search: int = 64  # Recherche HNSW
    
    # Configuration Elasticsearch
    elasticsearch_enabled: bool = True
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200
    elasticsearch_index: str = "content_fingerprints"
    elasticsearch_timeout: int = 30
    
    # Paramètres de recherche
    similarity_threshold: float = 0.75
    max_results: int = 100
    distance_metric: str = "cosine"  # cosine, euclidean, manhattan
    normalize_vectors: bool = True
    
    # Performance
    dimension_reduction: bool = False
    target_dimensions: int = 256
    batch_size: int = 1000
    max_workers: int = 8
    gpu_acceleration: bool = False
    
    # Cache et persistance
    cache_enabled: bool = True
    cache_size: int = 10000
    persistent_storage: bool = True
    index_save_path: str = "/tmp/faiss_indexes"
    
    # Monitoring
    performance_tracking: bool = True
    detailed_metrics: bool = True

class SimilarityMetric(ABC):
    """Classe de base pour les métriques de similarité"""
    
    @abstractmethod
    def compute(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calcule la similarité entre deux vecteurs"""
        pass
    
    @abstractmethod
    def batch_compute(self, vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
        """Calcule la similarité par lots"""
        pass

class CosineSimilarity(SimilarityMetric):
    """Métrique de similarité cosinus"""
    
    def compute(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calcule la similarité cosinus entre deux vecteurs"""
        if SCIPY_AVAILABLE:
            return 1.0 - cosine(vector1, vector2)
        else:
            # Implémentation manuelle
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
    
    def batch_compute(self, vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
        """Calcule la similarité cosinus par lots"""
        if SKLEARN_AVAILABLE:
            return cosine_similarity(vectors1, vectors2)
        else:
            # Implémentation manuelle pour lots
            results = []
            for v1 in vectors1:
                row = []
                for v2 in vectors2:
                    similarity = self.compute(v1, v2)
                    row.append(similarity)
                results.append(row)
            return np.array(results)

class EuclideanSimilarity(SimilarityMetric):
    """Métrique de distance euclidienne (convertie en similarité)"""
    
    def compute(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calcule la similarité basée sur la distance euclidienne"""
        if SCIPY_AVAILABLE:
            distance = euclidean(vector1, vector2)
        else:
            distance = np.linalg.norm(vector1 - vector2)
        
        # Conversion distance vers similarité (0-1)
        return 1.0 / (1.0 + distance)
    
    def batch_compute(self, vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
        """Calcule la distance euclidienne par lots"""
        if SKLEARN_AVAILABLE:
            distances = euclidean_distances(vectors1, vectors2)
            # Conversion en similarité
            return 1.0 / (1.0 + distances)
        else:
            results = []
            for v1 in vectors1:
                row = []
                for v2 in vectors2:
                    similarity = self.compute(v1, v2)
                    row.append(similarity)
                results.append(row)
            return np.array(results)

class ManhattanSimilarity(SimilarityMetric):
    """Métrique de distance de Manhattan (convertie en similarité)"""
    
    def compute(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calcule la similarité basée sur la distance de Manhattan"""
        if SCIPY_AVAILABLE:
            distance = cityblock(vector1, vector2)
        else:
            distance = np.sum(np.abs(vector1 - vector2))
        
        # Conversion distance vers similarité
        return 1.0 / (1.0 + distance)
    
    def batch_compute(self, vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
        """Calcule la distance de Manhattan par lots"""
        results = []
        for v1 in vectors1:
            row = []
            for v2 in vectors2:
                similarity = self.compute(v1, v2)
                row.append(similarity)
            results.append(row)
        return np.array(results)

@dataclass
class SearchResult:
    """Résultat d'une recherche de similarité"""
    fingerprint_id: str
    content_id: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class IndexStats:
    """Statistiques d'un index vectoriel"""
    total_vectors: int
    dimension: int
    index_size_mb: float
    last_updated: str
    index_type: str
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class FAISSIndexManager:
    """Gestionnaire d'index FAISS pour la recherche vectorielle rapide"""
    
    def __init__(self, config: VectorSimilarityConfig):
        self.config = config
        self.indexes = {}  # Stockage des index par type de contenu
        self.vector_id_mapping = {}  # Mapping ID -> position dans l'index
        self.metadata_store = {}  # Stockage des métadonnées
        self.lock = threading.RLock()
        
        # Initialisation du dossier de sauvegarde
        Path(config.index_save_path).mkdir(parents=True, exist_ok=True)
        
        if not FAISS_AVAILABLE:
            logger.error("FAISS not available - vector search will be limited")
            return
        
        # Configuration GPU si disponible
        self.use_gpu = config.gpu_acceleration and faiss.get_num_gpus() > 0
        if self.use_gpu:
            logger.info(f"GPU acceleration enabled with {faiss.get_num_gpus()} GPUs")
        
        logger.info("FAISS Index Manager initialized")
    
    def create_index(self, content_type: str, dimension: int) -> bool:
        """Crée un nouvel index FAISS pour un type de contenu"""
        if not FAISS_AVAILABLE:
            return False
        
        try:
            with self.lock:
                index_type = self.config.faiss_index_type.upper()
                
                if index_type == "FLAT":
                    index = faiss.IndexFlatIP(dimension)  # Inner Product (pour cosine)
                    
                elif index_type == "IVF":
                    quantizer = faiss.IndexFlatIP(dimension)
                    index = faiss.IndexIVFFlat(quantizer, dimension, self.config.faiss_nlist)
                    
                elif index_type == "HNSW":
                    index = faiss.IndexHNSWFlat(dimension, self.config.faiss_m)
                    index.hnsw.efConstruction = self.config.faiss_ef_construction
                    index.hnsw.efSearch = self.config.faiss_ef_search
                    
                elif index_type == "LSH":
                    index = faiss.IndexLSH(dimension, 128)  # 128 bits de hash
                    
                else:
                    logger.error(f"Unsupported index type: {index_type}")
                    return False
                
                # Configuration GPU
                if self.use_gpu:
                    res = faiss.StandardGpuResources()
                    index = faiss.index_cpu_to_gpu(res, 0, index)
                
                self.indexes[content_type] = index
                self.vector_id_mapping[content_type] = {}
                self.metadata_store[content_type] = {}
                
                logger.info(f"Created {index_type} index for {content_type} with dimension {dimension}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {e}")
            return False
    
    def add_vectors(self, content_type: str, vectors: np.ndarray, 
                   fingerprint_ids: List[str], metadata: List[Dict[str, Any]]) -> bool:
        """Ajoute des vecteurs à l'index"""
        if not FAISS_AVAILABLE or content_type not in self.indexes:
            return False
        
        try:
            with self.lock:
                index = self.indexes[content_type]
                
                # Normalisation des vecteurs si nécessaire
                if self.config.normalize_vectors:
                    vectors = normalize(vectors, norm='l2')
                
                # Entraînement de l'index si nécessaire (pour IVF)
                if hasattr(index, 'is_trained') and not index.is_trained:
                    if len(vectors) >= self.config.faiss_nlist:
                        index.train(vectors)
                        logger.info(f"Index {content_type} trained with {len(vectors)} vectors")
                
                # Ajout des vecteurs
                start_id = index.ntotal
                index.add(vectors)
                
                # Mise à jour des mappings
                for i, (fingerprint_id, meta) in enumerate(zip(fingerprint_ids, metadata)):
                    vector_position = start_id + i
                    self.vector_id_mapping[content_type][fingerprint_id] = vector_position
                    self.metadata_store[content_type][fingerprint_id] = meta
                
                logger.info(f"Added {len(vectors)} vectors to {content_type} index")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add vectors to FAISS index: {e}")
            return False
    
    def search(self, content_type: str, query_vector: np.ndarray, 
              k: int = None) -> List[SearchResult]:
        """Recherche les vecteurs les plus similaires"""
        if not FAISS_AVAILABLE or content_type not in self.indexes:
            return []
        
        k = k or self.config.max_results
        
        try:
            with self.lock:
                index = self.indexes[content_type]
                
                # Normalisation du vecteur de requête
                if self.config.normalize_vectors:
                    query_vector = normalize(query_vector.reshape(1, -1), norm='l2')[0]
                
                # Configuration de la recherche pour IVF
                if hasattr(index, 'nprobe'):
                    index.nprobe = self.config.faiss_nprobe
                
                # Recherche
                query_vector = query_vector.reshape(1, -1).astype('float32')
                distances, indices = index.search(query_vector, k)
                
                # Conversion des résultats
                results = []
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx == -1:  # Pas de résultat trouvé
                        continue
                    
                    # Recherche de l'ID du fingerprint
                    fingerprint_id = None
                    for fp_id, position in self.vector_id_mapping[content_type].items():
                        if position == idx:
                            fingerprint_id = fp_id
                            break
                    
                    if fingerprint_id:
                        # Conversion distance -> similarité (pour Inner Product)
                        similarity = float(distance)
                        
                        # Filtrage par seuil
                        if similarity >= self.config.similarity_threshold:
                            metadata = self.metadata_store[content_type].get(fingerprint_id, {})
                            
                            result = SearchResult(
                                fingerprint_id=fingerprint_id,
                                content_id=metadata.get("content_id", "unknown"),
                                similarity_score=similarity,
                                distance=float(distance),
                                metadata=metadata
                            )
                            results.append(result)
                
                # Tri par similarité décroissante
                results.sort(key=lambda x: x.similarity_score, reverse=True)
                return results
                
        except Exception as e:
            logger.error(f"Failed to search FAISS index: {e}")
            return []
    
    def save_index(self, content_type: str) -> bool:
        """Sauvegarde un index sur disque"""
        if not FAISS_AVAILABLE or content_type not in self.indexes:
            return False
        
        try:
            index_path = Path(self.config.index_save_path) / f"{content_type}_index.faiss"
            mapping_path = Path(self.config.index_save_path) / f"{content_type}_mapping.pkl"
            metadata_path = Path(self.config.index_save_path) / f"{content_type}_metadata.pkl"
            
            # Sauvegarde de l'index FAISS
            if self.use_gpu:
                # Conversion CPU pour la sauvegarde
                cpu_index = faiss.index_gpu_to_cpu(self.indexes[content_type])
                faiss.write_index(cpu_index, str(index_path))
            else:
                faiss.write_index(self.indexes[content_type], str(index_path))
            
            # Sauvegarde des mappings et métadonnées
            with open(mapping_path, 'wb') as f:
                pickle.dump(self.vector_id_mapping[content_type], f)
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata_store[content_type], f)
            
            logger.info(f"Index {content_type} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            return False
    
    def load_index(self, content_type: str, dimension: int) -> bool:
        """Charge un index depuis le disque"""
        if not FAISS_AVAILABLE:
            return False
        
        try:
            index_path = Path(self.config.index_save_path) / f"{content_type}_index.faiss"
            mapping_path = Path(self.config.index_save_path) / f"{content_type}_mapping.pkl"
            metadata_path = Path(self.config.index_save_path) / f"{content_type}_metadata.pkl"
            
            if not all(path.exists() for path in [index_path, mapping_path, metadata_path]):
                logger.info(f"Index files not found for {content_type}, creating new index")
                return self.create_index(content_type, dimension)
            
            # Chargement de l'index FAISS
            index = faiss.read_index(str(index_path))
            
            # Configuration GPU
            if self.use_gpu:
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
            
            # Chargement des mappings et métadonnées
            with open(mapping_path, 'rb') as f:
                self.vector_id_mapping[content_type] = pickle.load(f)
            
            with open(metadata_path, 'rb') as f:
                self.metadata_store[content_type] = pickle.load(f)
            
            self.indexes[content_type] = index
            
            logger.info(f"Index {content_type} loaded successfully with {index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return self.create_index(content_type, dimension)
    
    def get_stats(self, content_type: str) -> Optional[IndexStats]:
        """Retourne les statistiques d'un index"""
        if content_type not in self.indexes:
            return None
        
        try:
            index = self.indexes[content_type]
            
            # Calcul de la taille approximative
            size_mb = (index.ntotal * index.d * 4) / (1024 * 1024)  # 4 bytes par float32
            
            return IndexStats(
                total_vectors=index.ntotal,
                dimension=index.d,
                index_size_mb=size_mb,
                last_updated=datetime.now().isoformat(),
                index_type=type(index).__name__
            )
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return None

class ElasticsearchManager:
    """Gestionnaire Elasticsearch pour la recherche hybride et métadonnées"""
    
    def __init__(self, config: VectorSimilarityConfig):
        self.config = config
        self.client = None
        self.index_name = config.elasticsearch_index
        
        if not ELASTICSEARCH_AVAILABLE:
            logger.warning("Elasticsearch not available - hybrid search disabled")
            return
        
        self._initialize_client()
        self._ensure_index_exists()
    
    def _initialize_client(self):
        """Initialise le client Elasticsearch"""
        try:
            self.client = Elasticsearch(
                [{'host': self.config.elasticsearch_host, 'port': self.config.elasticsearch_port}],
                timeout=self.config.elasticsearch_timeout
            )
            
            # Test de connexion
            if self.client.ping():
                logger.info("Elasticsearch connection established")
            else:
                logger.error("Elasticsearch connection failed")
                self.client = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
            self.client = None
    
    def _ensure_index_exists(self):
        """Assure que l'index Elasticsearch existe"""
        if not self.client:
            return
        
        try:
            if not self.client.indices.exists(index=self.index_name):
                # Mapping pour les fingerprints avec support vectoriel
                mapping = {
                    "mappings": {
                        "properties": {
                            "fingerprint_id": {"type": "keyword"},
                            "content_id": {"type": "keyword"},
                            "content_type": {"type": "keyword"},
                            "creator_id": {"type": "keyword"},
                            "fingerprint_hash": {"type": "keyword"},
                            "similarity_vector": {"type": "dense_vector", "dims": 512},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "file_path": {"type": "text"},
                            "file_size": {"type": "long"},
                            "processing_time": {"type": "float"},
                            "confidence_score": {"type": "float"}
                        }
                    }
                }
                
                self.client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch index: {e}")
    
    def index_fingerprint(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Indexe un fingerprint dans Elasticsearch"""
        if not self.client:
            return False
        
        try:
            doc = {
                "fingerprint_id": fingerprint_data.get("fingerprint_id"),
                "content_id": fingerprint_data.get("content_id"),
                "content_type": fingerprint_data.get("content_type"),
                "creator_id": fingerprint_data.get("creator_id"),
                "fingerprint_hash": fingerprint_data.get("fingerprint_hash"),
                "similarity_vector": fingerprint_data.get("similarity_vector", []),
                "metadata": fingerprint_data.get("metadata", {}),
                "created_at": fingerprint_data.get("timestamp"),
                "file_path": fingerprint_data.get("file_path"),
                "file_size": fingerprint_data.get("file_size"),
                "processing_time": fingerprint_data.get("processing_time"),
                "confidence_score": fingerprint_data.get("confidence_score")
            }
            
            response = self.client.index(
                index=self.index_name,
                id=fingerprint_data.get("fingerprint_id"),
                body=doc
            )
            
            return response.get("result") in ["created", "updated"]
            
        except Exception as e:
            logger.error(f"Failed to index fingerprint in Elasticsearch: {e}")
            return False
    
    def search_by_metadata(self, query: Dict[str, Any], size: int = 100) -> List[Dict[str, Any]]:
        """Recherche par métadonnées et filtres"""
        if not self.client:
            return []
        
        try:
            response = self.client.search(
                index=self.index_name,
                body={"query": query, "size": size}
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "fingerprint_id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            return []
    
    def vector_search(self, query_vector: List[float], content_type: str = None,
                     size: int = 100) -> List[Dict[str, Any]]:
        """Recherche vectorielle avec Elasticsearch"""
        if not self.client:
            return []
        
        try:
            # Construction de la requête vectorielle
            query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'similarity_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
            
            # Ajout de filtre par type si spécifié
            if content_type:
                query["script_score"]["query"] = {
                    "term": {"content_type": content_type}
                }
            
            response = self.client.search(
                index=self.index_name,
                body={"query": query, "size": size}
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "fingerprint_id": hit["_id"],
                    "similarity_score": hit["_score"] - 1.0,  # Compensation du +1.0
                    "source": hit["_source"]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Elasticsearch vector search failed: {e}")
            return []

class SimilarityCalculator:
    """Calculateur de similarité avec multiple métriques"""
    
    def __init__(self, config: VectorSimilarityConfig):
        self.config = config
        
        # Initialisation des métriques
        self.metrics = {
            "cosine": CosineSimilarity(),
            "euclidean": EuclideanSimilarity(),
            "manhattan": ManhattanSimilarity()
        }
        
        # Sélection de la métrique par défaut
        self.default_metric = self.metrics.get(config.distance_metric, self.metrics["cosine"])
    
    def compute_similarity(self, vector1: np.ndarray, vector2: np.ndarray, 
                          metric: str = None) -> float:
        """Calcule la similarité entre deux vecteurs"""
        metric_obj = self.metrics.get(metric, self.default_metric)
        return metric_obj.compute(vector1, vector2)
    
    def batch_similarity(self, vectors1: np.ndarray, vectors2: np.ndarray,
                        metric: str = None) -> np.ndarray:
        """Calcule la similarité par lots"""
        metric_obj = self.metrics.get(metric, self.default_metric)
        return metric_obj.batch_compute(vectors1, vectors2)
    
    def find_similar_vectors(self, query_vector: np.ndarray, 
                           candidate_vectors: np.ndarray,
                           threshold: float = None) -> List[Tuple[int, float]]:
        """Trouve les vecteurs similaires dans un ensemble de candidats"""
        threshold = threshold or self.config.similarity_threshold
        
        similarities = []
        for i, candidate in enumerate(candidate_vectors):
            similarity = self.compute_similarity(query_vector, candidate)
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        # Tri par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:self.config.max_results]

class MatchingEngine:
    """Moteur de matching avancé combinant FAISS et Elasticsearch"""
    
    def __init__(self, config: VectorSimilarityConfig):
        self.config = config
        self.faiss_manager = FAISSIndexManager(config)
        self.elasticsearch_manager = ElasticsearchManager(config)
        self.similarity_calculator = SimilarityCalculator(config)
        
        # Cache pour les résultats récents
        self.cache = {} if config.cache_enabled else None
        self.cache_max_size = config.cache_size
        
        # Métriques de performance
        self.metrics = {
            "searches_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_search_time": 0.0,
            "average_search_time": 0.0
        }
    
    def index_fingerprint(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Indexe un fingerprint dans tous les systèmes"""
        success = True
        
        try:
            content_type = fingerprint_data.get("content_type")
            fingerprint_id = fingerprint_data.get("fingerprint_id")
            
            # Extraction du vecteur de similarité
            similarity_vector = self._extract_similarity_vector(fingerprint_data)
            
            if similarity_vector is not None:
                # Indexation FAISS
                if content_type not in self.faiss_manager.indexes:
                    self.faiss_manager.create_index(content_type, len(similarity_vector))
                
                faiss_success = self.faiss_manager.add_vectors(
                    content_type=content_type,
                    vectors=np.array([similarity_vector]),
                    fingerprint_ids=[fingerprint_id],
                    metadata=[fingerprint_data.get("metadata", {})]
                )
                
                success = success and faiss_success
            
            # Indexation Elasticsearch
            fingerprint_data["similarity_vector"] = similarity_vector.tolist() if similarity_vector is not None else []
            es_success = self.elasticsearch_manager.index_fingerprint(fingerprint_data)
            success = success and es_success
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index fingerprint: {e}")
            return False
    
    def find_matches(self, query_fingerprint: Dict[str, Any], 
                    content_type: str = None) -> List[SearchResult]:
        """Trouve les matches pour un fingerprint donné"""
        start_time = time.time()
        
        try:
            # Vérification du cache
            cache_key = self._generate_cache_key(query_fingerprint, content_type)
            if self.cache and cache_key in self.cache:
                self.metrics["cache_hits"] += 1
                return self.cache[cache_key]
            
            self.metrics["cache_misses"] += 1
            
            # Extraction du vecteur de requête
            query_vector = self._extract_similarity_vector(query_fingerprint)
            if query_vector is None:
                return []
            
            results = []
            
            # Recherche FAISS
            if content_type and content_type in self.faiss_manager.indexes:
                faiss_results = self.faiss_manager.search(
                    content_type=content_type,
                    query_vector=query_vector,
                    k=self.config.max_results
                )
                results.extend(faiss_results)
            
            # Recherche Elasticsearch (hybride)
            if self.elasticsearch_manager.client:
                es_results = self.elasticsearch_manager.vector_search(
                    query_vector=query_vector.tolist(),
                    content_type=content_type,
                    size=self.config.max_results
                )
                
                # Conversion des résultats Elasticsearch
                for es_result in es_results:
                    if es_result["similarity_score"] >= self.config.similarity_threshold:
                        search_result = SearchResult(
                            fingerprint_id=es_result["fingerprint_id"],
                            content_id=es_result["source"].get("content_id", "unknown"),
                            similarity_score=es_result["similarity_score"],
                            distance=1.0 - es_result["similarity_score"],
                            metadata=es_result["source"].get("metadata", {})
                        )
                        results.append(search_result)
            
            # Déduplication et tri
            results = self._deduplicate_results(results)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            results = results[:self.config.max_results]
            
            # Mise en cache
            if self.cache:
                self._update_cache(cache_key, results)
            
            # Mise à jour des métriques
            search_time = time.time() - start_time
            self.metrics["searches_performed"] += 1
            self.metrics["total_search_time"] += search_time
            self.metrics["average_search_time"] = (
                self.metrics["total_search_time"] / self.metrics["searches_performed"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Match finding failed: {e}")
            return []
    
    def _extract_similarity_vector(self, fingerprint_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extrait le vecteur de similarité d'un fingerprint"""
        # Logique pour extraire/construire un vecteur de similarité
        # basé sur les différents types de fingerprints
        
        fingerprints = fingerprint_data.get("fingerprints", {})
        vectors = []
        
        # Audio fingerprint
        if "audio" in fingerprints:
            audio_fp = fingerprints["audio"]
            if "spectral_features" in audio_fp:
                vectors.extend(audio_fp["spectral_features"][:100])  # Limitation à 100 dims
        
        # Video fingerprint
        if "video" in fingerprints:
            video_fp = fingerprints["video"]
            if "feature_vector" in video_fp:
                vectors.extend(video_fp["feature_vector"][:100])
        
        # Image fingerprint
        if "image" in fingerprints:
            image_fp = fingerprints["image"]
            if "deep_features" in image_fp:
                vectors.extend(image_fp["deep_features"][:100])
        
        # Text fingerprint
        if "text" in fingerprints:
            text_fp = fingerprints["text"]
            if "bert" in text_fp and "bert_embedding" in text_fp["bert"]:
                vectors.extend(text_fp["bert"]["bert_embedding"][:100])
        
        if vectors:
            # Padding ou troncature pour avoir une dimension fixe
            target_dim = 512  # Dimension standard
            if len(vectors) > target_dim:
                vectors = vectors[:target_dim]
            elif len(vectors) < target_dim:
                vectors.extend([0.0] * (target_dim - len(vectors)))
            
            return np.array(vectors, dtype=np.float32)
        
        return None
    
    def _generate_cache_key(self, fingerprint_data: Dict[str, Any], content_type: str) -> str:
        """Génère une clé de cache pour une requête"""
        key_data = {
            "fingerprint_hash": fingerprint_data.get("fingerprint_hash"),
            "content_type": content_type,
            "threshold": self.config.similarity_threshold
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _update_cache(self, key: str, results: List[SearchResult]):
        """Met à jour le cache avec de nouveaux résultats"""
        if not self.cache:
            return
        
        # Nettoyage du cache si nécessaire
        if len(self.cache) >= self.cache_max_size:
            # Suppression des entrées les plus anciennes (FIFO simple)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = results
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Supprime les doublons des résultats"""
        seen_fingerprints = set()
        unique_results = []
        
        for result in results:
            if result.fingerprint_id not in seen_fingerprints:
                seen_fingerprints.add(result.fingerprint_id)
                unique_results.append(result)
        
        return unique_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        cache_hit_rate = (
            self.metrics["cache_hits"] / 
            max(self.metrics["cache_hits"] + self.metrics["cache_misses"], 1)
        )
        
        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.cache) if self.cache else 0
        }

class VectorSimilarityEngine:
    """
    Moteur principal de similarité vectorielle
    
    Fonctionnalités:
    - Indexation FAISS haute performance
    - Recherche hybride avec Elasticsearch
    - Multiple métriques de similarité
    - Cache intelligent
    - Monitoring et métriques
    - Support GPU
    """
    
    def __init__(self, config: Optional[VectorSimilarityConfig] = None):
        self.config = config or VectorSimilarityConfig()
        self.matching_engine = MatchingEngine(self.config)
        
        # PCA pour réduction de dimension si activée
        self.pca = None
        if self.config.dimension_reduction and SKLEARN_AVAILABLE:
            self.pca = PCA(n_components=self.config.target_dimensions)
        
        logger.info("VectorSimilarityEngine initialized successfully")
    
    async def index_fingerprint(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Indexe un fingerprint de manière asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.matching_engine.index_fingerprint, fingerprint_data
        )
    
    async def find_similar(self, query_fingerprint: Dict[str, Any],
                          content_type: str = None) -> List[SearchResult]:
        """Trouve les fingerprints similaires de manière asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.matching_engine.find_matches, query_fingerprint, content_type
        )
    
    def save_indexes(self) -> bool:
        """Sauvegarde tous les index sur disque"""
        success = True
        for content_type in self.matching_engine.faiss_manager.indexes:
            success = success and self.matching_engine.faiss_manager.save_index(content_type)
        return success
    
    def load_indexes(self, content_types: List[str], dimensions: Dict[str, int]) -> bool:
        """Charge les index depuis le disque"""
        success = True
        for content_type in content_types:
            dimension = dimensions.get(content_type, 512)  # Dimension par défaut
            success = success and self.matching_engine.faiss_manager.load_index(content_type, dimension)
        return success
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Retourne des métriques complètes du système"""
        matching_metrics = self.matching_engine.get_metrics()
        
        # Statistiques des index
        index_stats = {}
        for content_type in self.matching_engine.faiss_manager.indexes:
            stats = self.matching_engine.faiss_manager.get_stats(content_type)
            if stats:
                index_stats[content_type] = stats.__dict__
        
        return {
            "matching_engine": matching_metrics,
            "index_statistics": index_stats,
            "configuration": {
                "faiss_enabled": self.config.faiss_enabled,
                "elasticsearch_enabled": self.config.elasticsearch_enabled,
                "gpu_acceleration": self.config.gpu_acceleration,
                "similarity_threshold": self.config.similarity_threshold,
                "max_results": self.config.max_results
            },
            "system_info": {
                "faiss_available": FAISS_AVAILABLE,
                "elasticsearch_available": ELASTICSEARCH_AVAILABLE,
                "gpu_count": faiss.get_num_gpus() if FAISS_AVAILABLE else 0
            }
        }

# Export des classes principales
__all__ = [
    "VectorSimilarityEngine",
    "VectorSimilarityConfig", 
    "FAISSIndexManager",
    "ElasticsearchManager",
    "SimilarityCalculator",
    "MatchingEngine",
    "SearchResult",
    "IndexStats"
]
