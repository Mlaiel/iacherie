"""IA Influencer Agent - Advanced Indexing Engines
===============================================

High-performance indexing engines for multi-format content processing,
vector search, fingerprinting, and metadata management with enterprise-grade scalability.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import numpy as np
import faiss
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
import torch
from transformers import AutoTokenizer, AutoModel
import librosa
import cv2
from PIL import Image
import imagehash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class IndexingConfig:
    """Configuration for indexing engines"""
    vector_dimension: int = 768
    similarity_threshold: float = 0.85
    batch_size: int = 100
    max_concurrent_operations: int = 50
    index_prefix: str = "ia_influencer"
    elasticsearch_hosts: List[str] = None
    redis_url: str = "redis://localhost:6379"
    faiss_index_type: str = "IVF"
    enable_gpu: bool = True


class BaseIndexEngine(ABC):
    """Abstract base class for all indexing engines"""
    
    def __init__(self, config: IndexingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the indexing engine"""
        pass
    
    @abstractmethod
    async def index_content(self, content_id: str, data: Any) -> Dict[str, Any]:
        """Index content and return indexing result"""
        pass
    
    @abstractmethod
    async def search(self, query: Any, filters: Dict = None) -> List[Dict[str, Any]]:
        """Search indexed content"""
        pass
    
    @abstractmethod
    async def delete_index(self, content_id: str) -> bool:
        """Delete indexed content"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check engine health status"""
        return {
            "engine": self.__class__.__name__,
            "status": "healthy" if self._initialized else "not_initialized",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class VectorSearchEngine(BaseIndexEngine):
    """Advanced vector search engine with FAISS backend for similarity search"""
    
    def __init__(self, config: IndexingConfig):
        super().__init__(config)
        self.faiss_index = None
        self.vector_store = {}
        self.redis_client = None
        self.embeddings_model = None
        self.tokenizer = None
        
    async def initialize(self) -> None:
        """Initialize FAISS index and embedding models"""
        try:
            # Initialize Redis connection
            self.redis_client = Redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            
            # Initialize embedding model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.embeddings_model = AutoModel.from_pretrained(model_name)
            
            if self.config.enable_gpu and torch.cuda.is_available():
                self.embeddings_model = self.embeddings_model.cuda()
            
            # Initialize FAISS index
            if self.config.faiss_index_type == "IVF":
                quantizer = faiss.IndexFlatIP(self.config.vector_dimension)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, 
                    self.config.vector_dimension, 
                    100  # nlist
                )
            else:
                self.faiss_index = faiss.IndexFlatIP(self.config.vector_dimension)
            
            if self.config.enable_gpu and faiss.get_num_gpus() > 0:
                self.faiss_index = faiss.index_cpu_to_gpu(
                    faiss.StandardGpuResources(), 0, self.faiss_index
                )
            
            self._initialized = True
            self.logger.info("VectorSearchEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VectorSearchEngine: {e}")
            raise
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate text embedding using transformer model"""
        try:
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            if self.config.enable_gpu and torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.embeddings_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            return embeddings.cpu().numpy().flatten()
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def index_content(self, content_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Index content with vector embeddings"""
        try:
            text_content = data.get("text", "")
            metadata = data.get("metadata", {})
            
            # Generate embedding
            embedding = await self._generate_embedding(text_content)
            
            # Store in FAISS
            if not self.faiss_index.is_trained:
                if hasattr(self.faiss_index, 'train'):
                    self.faiss_index.train(embedding.reshape(1, -1))
            
            vector_id = len(self.vector_store)
            self.faiss_index.add(embedding.reshape(1, -1))
            
            # Store metadata
            self.vector_store[vector_id] = {
                "content_id": content_id,
                "text": text_content,
                "metadata": metadata,
                "embedding": embedding.tolist(),
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache in Redis
            await self.redis_client.hset(
                f"vector:{content_id}",
                mapping={
                    "vector_id": vector_id,
                    "embedding": str(embedding.tolist()),
                    "metadata": str(metadata)
                }
            )
            
            return {
                "content_id": content_id,
                "vector_id": vector_id,
                "embedding_dimension": len(embedding),
                "status": "indexed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to index content {content_id}: {e}")
            raise
    
    async def search(self, query: str, filters: Dict = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in FAISS
            scores, indices = self.faiss_index.search(
                query_embedding.reshape(1, -1), 
                top_k
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # No more results
                    break
                    
                if idx in self.vector_store:
                    result = self.vector_store[idx].copy()
                    result["similarity_score"] = float(score)
                    
                    # Apply filters if provided
                    if filters:
                        if self._apply_filters(result, filters):
                            results.append(result)
                    else:
                        results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform search: {e}")
            raise
    
    def _apply_filters(self, result: Dict, filters: Dict) -> bool:
        """Apply search filters"""
        for key, value in filters.items():
            if key in result.get("metadata", {}):
                if result["metadata"][key] != value:
                    return False
        return True
    
    async def delete_index(self, content_id: str) -> bool:
        """Delete indexed content"""
        try:
            # Find vector_id from Redis
            vector_data = await self.redis_client.hgetall(f"vector:{content_id}")
            if not vector_data:
                return False
            
            vector_id = int(vector_data.get("vector_id", -1))
            if vector_id in self.vector_store:
                del self.vector_store[vector_id]
            
            # Remove from Redis
            await self.redis_client.delete(f"vector:{content_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete index for {content_id}: {e}")
            return False


class ContentIndexEngine(BaseIndexEngine):
    """Advanced content indexing engine with Elasticsearch backend"""
    
    def __init__(self, config: IndexingConfig):
        super().__init__(config)
        self.es_client = None
        
    async def initialize(self) -> None:
        """Initialize Elasticsearch connection"""
        try:
            hosts = self.config.elasticsearch_hosts or ["http://localhost:9200"]
            self.es_client = AsyncElasticsearch(hosts=hosts)
            
            # Create index mappings
            await self._create_mappings()
            
            self._initialized = True
            self.logger.info("ContentIndexEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ContentIndexEngine: {e}")
            raise
    
    async def _create_mappings(self) -> None:
        """Create Elasticsearch index mappings"""
        mappings = {
            "mappings": {
                "properties": {
                    "content_id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "content_type": {"type": "keyword"},
                    "creator_id": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "fingerprint": {"type": "keyword"},
                    "metadata": {"type": "object"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "protection_level": {"type": "keyword"},
                    "content_vector": {"type": "dense_vector", "dims": 768}
                }
            }
        }
        
        index_name = f"{self.config.index_prefix}_content"
        
        if not await self.es_client.indices.exists(index=index_name):
            await self.es_client.indices.create(index=index_name, body=mappings)
    
    async def index_content(self, content_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Index content in Elasticsearch"""
        try:
            index_name = f"{self.config.index_prefix}_content"
            
            document = {
                "content_id": content_id,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "content_type": data.get("content_type", "unknown"),
                "creator_id": data.get("creator_id", ""),
                "tags": data.get("tags", []),
                "fingerprint": data.get("fingerprint", ""),
                "metadata": data.get("metadata", {}),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "protection_level": data.get("protection_level", "standard"),
                "content_vector": data.get("embedding", [])
            }
            
            response = await self.es_client.index(
                index=index_name,
                id=content_id,
                body=document
            )
            
            return {
                "content_id": content_id,
                "index": index_name,
                "result": response.get("result"),
                "status": "indexed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to index content {content_id}: {e}")
            raise
    
    async def search(self, query: Dict, filters: Dict = None) -> List[Dict[str, Any]]:
        """Search indexed content"""
        try:
            index_name = f"{self.config.index_prefix}_content"
            
            search_body = {
                "query": self._build_query(query, filters),
                "size": query.get("size", 50),
                "from": query.get("from", 0),
                "sort": query.get("sort", [{"created_at": {"order": "desc"}}])
            }
            
            response = await self.es_client.search(
                index=index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["score"] = hit["_score"]
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search content: {e}")
            raise
    
    def _build_query(self, query: Dict, filters: Dict = None) -> Dict:
        """Build Elasticsearch query"""
        if "text" in query:
            es_query = {
                "multi_match": {
                    "query": query["text"],
                    "fields": ["title^2", "description", "tags"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        else:
            es_query = {"match_all": {}}
        
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if isinstance(value, list):
                    filter_clauses.append({"terms": {key: value}})
                else:
                    filter_clauses.append({"term": {key: value}})
            
            if filter_clauses:
                es_query = {
                    "bool": {
                        "must": [es_query],
                        "filter": filter_clauses
                    }
                }
        
        return es_query
    
    async def delete_index(self, content_id: str) -> bool:
        """Delete indexed content"""
        try:
            index_name = f"{self.config.index_prefix}_content"
            response = await self.es_client.delete(
                index=index_name,
                id=content_id
            )
            return response.get("result") == "deleted"
            
        except Exception as e:
            self.logger.error(f"Failed to delete index for {content_id}: {e}")
            return False


class FingerprintIndexEngine(BaseIndexEngine):
    """Advanced fingerprinting engine for content protection and similarity detection"""
    
    def __init__(self, config: IndexingConfig):
        super().__init__(config)
        self.redis_client = None
        self.fingerprint_store = {}
        
    async def initialize(self) -> None:
        """Initialize fingerprint storage"""
        try:
            self.redis_client = Redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            
            self._initialized = True
            self.logger.info("FingerprintIndexEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FingerprintIndexEngine: {e}")
            raise
    
    async def index_content(self, content_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and index content fingerprints"""
        try:
            content_type = data.get("content_type", "unknown")
            fingerprints = {}
            
            if content_type == "audio":
                fingerprints.update(await self._generate_audio_fingerprint(data))
            elif content_type == "image":
                fingerprints.update(await self._generate_image_fingerprint(data))
            elif content_type == "video":
                fingerprints.update(await self._generate_video_fingerprint(data))
            elif content_type == "text":
                fingerprints.update(await self._generate_text_fingerprint(data))
            
            # Store fingerprints
            fingerprint_data = {
                "content_id": content_id,
                "content_type": content_type,
                "fingerprints": fingerprints,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": data.get("metadata", {})
            }
            
            self.fingerprint_store[content_id] = fingerprint_data
            
            # Cache in Redis
            await self.redis_client.hset(
                f"fingerprint:{content_id}",
                mapping={
                    "data": str(fingerprint_data),
                    "type": content_type
                }
            )
            
            return {
                "content_id": content_id,
                "fingerprints_generated": len(fingerprints),
                "content_type": content_type,
                "status": "fingerprinted"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate fingerprint for {content_id}: {e}")
            raise
    
    async def _generate_audio_fingerprint(self, data: Dict) -> Dict[str, str]:
        """Generate audio fingerprints using multiple algorithms"""
        fingerprints = {}
        
        try:
            audio_path = data.get("file_path")
            if audio_path:
                # Load audio
                y, sr = librosa.load(audio_path, sr=22050)
                
                # Spectral centroid fingerprint
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                fingerprints["spectral_centroid"] = hashlib.sha256(
                    spectral_centroid.tobytes()
                ).hexdigest()
                
                # MFCC fingerprint
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                fingerprints["mfcc"] = hashlib.sha256(
                    mfccs.tobytes()
                ).hexdigest()
                
                # Chroma fingerprint
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                fingerprints["chroma"] = hashlib.sha256(
                    chroma.tobytes()
                ).hexdigest()
                
        except Exception as e:
            self.logger.error(f"Failed to generate audio fingerprint: {e}")
        
        return fingerprints
    
    async def _generate_image_fingerprint(self, data: Dict) -> Dict[str, str]:
        """Generate image fingerprints using multiple algorithms"""
        fingerprints = {}
        
        try:
            image_path = data.get("file_path")
            if image_path:
                # Load image
                image = Image.open(image_path)
                
                # Perceptual hash
                fingerprints["phash"] = str(imagehash.phash(image))
                
                # Average hash
                fingerprints["ahash"] = str(imagehash.average_hash(image))
                
                # Difference hash
                fingerprints["dhash"] = str(imagehash.dhash(image))
                
                # Wavelet hash
                fingerprints["whash"] = str(imagehash.whash(image))
                
                # Color histogram
                hist = cv2.calcHist(
                    [np.array(image)], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
                )
                fingerprints["color_hist"] = hashlib.sha256(
                    hist.tobytes()
                ).hexdigest()
                
        except Exception as e:
            self.logger.error(f"Failed to generate image fingerprint: {e}")
        
        return fingerprints
    
    async def _generate_video_fingerprint(self, data: Dict) -> Dict[str, str]:
        """Generate video fingerprints"""
        fingerprints = {}
        
        try:
            video_path = data.get("file_path")
            if video_path:
                # Extract key frames and generate image fingerprints
                cap = cv2.VideoCapture(video_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Sample frames at intervals
                sample_frames = []
                for i in range(0, frame_count, max(1, frame_count // 10)):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        sample_frames.append(frame)
                
                cap.release()
                
                # Generate hash from sampled frames
                if sample_frames:
                    combined_frames = np.concatenate(sample_frames, axis=0)
                    fingerprints["frames_hash"] = hashlib.sha256(
                        combined_frames.tobytes()
                    ).hexdigest()
                
        except Exception as e:
            self.logger.error(f"Failed to generate video fingerprint: {e}")
        
        return fingerprints
    
    async def _generate_text_fingerprint(self, data: Dict) -> Dict[str, str]:
        """Generate text fingerprints"""
        fingerprints = {}
        
        try:
            text = data.get("text", "")
            if text:
                # Basic hash
                fingerprints["sha256"] = hashlib.sha256(text.encode()).hexdigest()
                
                # Normalized text hash (lowercase, no spaces)
                normalized = "".join(text.lower().split())
                fingerprints["normalized"] = hashlib.sha256(normalized.encode()).hexdigest()
                
                # N-gram fingerprints
                words = text.lower().split()
                if len(words) >= 3:
                    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
                    trigrams_text = " ".join(sorted(trigrams))
                    fingerprints["trigrams"] = hashlib.sha256(
                        trigrams_text.encode()
                    ).hexdigest()
                
        except Exception as e:
            self.logger.error(f"Failed to generate text fingerprint: {e}")
        
        return fingerprints
    
    async def search(self, query: Dict, filters: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar fingerprints"""
        try:
            query_fingerprints = query.get("fingerprints", {})
            similarity_threshold = query.get("threshold", self.config.similarity_threshold)
            
            results = []
            
            for content_id, stored_data in self.fingerprint_store.items():
                stored_fingerprints = stored_data.get("fingerprints", {})
                
                # Calculate similarity
                similarity = self._calculate_fingerprint_similarity(
                    query_fingerprints, stored_fingerprints
                )
                
                if similarity >= similarity_threshold:
                    result = stored_data.copy()
                    result["similarity"] = similarity
                    results.append(result)
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search fingerprints: {e}")
            raise
    
    def _calculate_fingerprint_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between two fingerprint sets"""
        if not fp1 or not fp2:
            return 0.0
        
        common_types = set(fp1.keys()) & set(fp2.keys())
        if not common_types:
            return 0.0
        
        similarities = []
        
        for fp_type in common_types:
            if fp_type in ["phash", "ahash", "dhash", "whash"]:
                # Hamming distance for image hashes
                hash1 = imagehash.hex_to_hash(fp1[fp_type])
                hash2 = imagehash.hex_to_hash(fp2[fp_type])
                similarity = 1.0 - (hash1 - hash2) / len(hash1.hash) ** 2
            else:
                # Exact match for other hashes
                similarity = 1.0 if fp1[fp_type] == fp2[fp_type] else 0.0
            
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities)
    
    async def delete_index(self, content_id: str) -> bool:
        """Delete fingerprint index"""
        try:
            if content_id in self.fingerprint_store:
                del self.fingerprint_store[content_id]
            
            await self.redis_client.delete(f"fingerprint:{content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete fingerprint for {content_id}: {e}")
            return False


class MetadataIndexEngine(BaseIndexEngine):
    """Advanced metadata indexing for fast filtering and aggregation"""
    
    def __init__(self, config: IndexingConfig):
        super().__init__(config)
        self.redis_client = None
        self.metadata_store = {}
        
    async def initialize(self) -> None:
        """Initialize metadata storage"""
        try:
            self.redis_client = Redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            
            self._initialized = True
            self.logger.info("MetadataIndexEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MetadataIndexEngine: {e}")
            raise
    
    async def index_content(self, content_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Index content metadata"""
        try:
            metadata = {
                "content_id": content_id,
                "creator_id": data.get("creator_id", ""),
                "content_type": data.get("content_type", "unknown"),
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "tags": data.get("tags", []),
                "category": data.get("category", ""),
                "language": data.get("language", "en"),
                "duration": data.get("duration", 0),
                "file_size": data.get("file_size", 0),
                "dimensions": data.get("dimensions", {}),
                "quality": data.get("quality", ""),
                "protection_level": data.get("protection_level", "standard"),
                "licensing": data.get("licensing", {}),
                "monetization": data.get("monetization", {}),
                "collaboration": data.get("collaboration", {}),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "custom_metadata": data.get("custom_metadata", {})
            }
            
            self.metadata_store[content_id] = metadata
            
            # Index in Redis with multiple access patterns
            await self._index_redis_metadata(content_id, metadata)
            
            return {
                "content_id": content_id,
                "metadata_fields": len(metadata),
                "status": "indexed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to index metadata for {content_id}: {e}")
            raise
    
    async def _index_redis_metadata(self, content_id: str, metadata: Dict) -> None:
        """Index metadata in Redis with multiple access patterns"""
        # Main metadata
        await self.redis_client.hset(
            f"metadata:{content_id}",
            mapping={k: str(v) for k, v in metadata.items()}
        )
        
        # Index by creator
        creator_id = metadata.get("creator_id")
        if creator_id:
            await self.redis_client.sadd(f"creator:{creator_id}:content", content_id)
        
        # Index by content type
        content_type = metadata.get("content_type")
        if content_type:
            await self.redis_client.sadd(f"type:{content_type}:content", content_id)
        
        # Index by tags
        for tag in metadata.get("tags", []):
            await self.redis_client.sadd(f"tag:{tag}:content", content_id)
        
        # Index by category
        category = metadata.get("category")
        if category:
            await self.redis_client.sadd(f"category:{category}:content", content_id)
        
        # Time-based indexing
        created_date = metadata.get("created_at", "")[:10]  # YYYY-MM-DD
        if created_date:
            await self.redis_client.sadd(f"date:{created_date}:content", content_id)
    
    async def search(self, query: Dict, filters: Dict = None) -> List[Dict[str, Any]]:
        """Search metadata with advanced filtering"""
        try:
            results = []
            content_ids = set()
            
            # Apply filters to get candidate content IDs
            if filters:
                content_ids = await self._apply_metadata_filters(filters)
            else:
                content_ids = set(self.metadata_store.keys())
            
            # Apply text search if provided
            if "text" in query:
                text_matches = await self._search_metadata_text(query["text"])
                content_ids = content_ids.intersection(text_matches) if content_ids else text_matches
            
            # Retrieve metadata for matching content
            for content_id in content_ids:
                if content_id in self.metadata_store:
                    metadata = self.metadata_store[content_id].copy()
                    metadata["relevance_score"] = 1.0  # Could implement scoring
                    results.append(metadata)
            
            # Sort results
            sort_by = query.get("sort_by", "created_at")
            reverse = query.get("sort_order", "desc") == "desc"
            
            if sort_by in ["created_at", "updated_at"]:
                results.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
            
            # Pagination
            start = query.get("from", 0)
            size = query.get("size", 50)
            
            return results[start:start + size]
            
        except Exception as e:
            self.logger.error(f"Failed to search metadata: {e}")
            raise
    
    async def _apply_metadata_filters(self, filters: Dict) -> set:
        """Apply metadata filters using Redis sets"""
        filter_sets = []
        
        for key, value in filters.items():
            if key == "creator_id":
                filter_sets.append(f"creator:{value}:content")
            elif key == "content_type":
                filter_sets.append(f"type:{value}:content")
            elif key == "category":
                filter_sets.append(f"category:{value}:content")
            elif key == "tags":
                if isinstance(value, list):
                    for tag in value:
                        filter_sets.append(f"tag:{tag}:content")
                else:
                    filter_sets.append(f"tag:{value}:content")
            elif key == "date_range":
                # Handle date range filters
                start_date = value.get("start", "")
                end_date = value.get("end", "")
                # Implementation for date range filtering
        
        if not filter_sets:
            return set()
        
        # Intersect all filter sets
        if len(filter_sets) == 1:
            result = await self.redis_client.smembers(filter_sets[0])
        else:
            # Use Redis SINTER for intersection
            temp_key = f"temp:filter:{datetime.now().timestamp()}"
            await self.redis_client.sinterstore(temp_key, *filter_sets)
            result = await self.redis_client.smembers(temp_key)
            await self.redis_client.delete(temp_key)
        
        return {item.decode() if isinstance(item, bytes) else item for item in result}
    
    async def _search_metadata_text(self, text: str) -> set:
        """Search metadata text fields"""
        matching_content = set()
        text_lower = text.lower()
        
        for content_id, metadata in self.metadata_store.items():
            # Search in title, description, tags
            searchable_text = " ".join([
                metadata.get("title", ""),
                metadata.get("description", ""),
                " ".join(metadata.get("tags", []))
            ]).lower()
            
            if text_lower in searchable_text:
                matching_content.add(content_id)
        
        return matching_content
    
    async def delete_index(self, content_id: str) -> bool:
        """Delete metadata index"""
        try:
            if content_id not in self.metadata_store:
                return False
            
            metadata = self.metadata_store[content_id]
            
            # Remove from main store
            del self.metadata_store[content_id]
            
            # Remove from Redis
            await self.redis_client.delete(f"metadata:{content_id}")
            
            # Remove from index sets
            creator_id = metadata.get("creator_id")
            if creator_id:
                await self.redis_client.srem(f"creator:{creator_id}:content", content_id)
            
            content_type = metadata.get("content_type")
            if content_type:
                await self.redis_client.srem(f"type:{content_type}:content", content_id)
            
            for tag in metadata.get("tags", []):
                await self.redis_client.srem(f"tag:{tag}:content", content_id)
            
            category = metadata.get("category")
            if category:
                await self.redis_client.srem(f"category:{category}:content", content_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete metadata for {content_id}: {e}")
            return False
    
    async def get_aggregations(self, field: str, filters: Dict = None) -> Dict[str, int]:
        """Get aggregation statistics for a field"""
        try:
            aggregations = {}
            
            # Get content IDs based on filters
            if filters:
                content_ids = await self._apply_metadata_filters(filters)
            else:
                content_ids = set(self.metadata_store.keys())
            
            # Count values for the specified field
            for content_id in content_ids:
                if content_id in self.metadata_store:
                    metadata = self.metadata_store[content_id]
                    value = metadata.get(field)
                    
                    if isinstance(value, list):
                        for item in value:
                            aggregations[item] = aggregations.get(item, 0) + 1
                    elif value:
                        aggregations[value] = aggregations.get(value, 0) + 1
            
            return dict(sorted(aggregations.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            self.logger.error(f"Failed to get aggregations for {field}: {e}")
            raise
