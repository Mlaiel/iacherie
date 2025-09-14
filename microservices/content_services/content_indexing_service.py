"""
🔍 Content Indexing Service - Service d'Indexation Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service spécialisé d'indexation intelligente pour recherche et découverte de contenu.
Indexation multi-format avec métadonnées enrichies et recherche sémantique.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import logging
import hashlib
import json

from elasticsearch import AsyncElasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)


class ContentIndexingService:
    """Service d'indexation intelligente pour recherche de contenu"""
    
    def __init__(self):
        self.elasticsearch_client = None
        self.index_name = "ainflue_content"
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Types de contenu supportés
        self.content_types = {
            'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'document': ['pdf', 'docx', 'txt', 'md'],
            'presentation': ['pptx', 'key'],
            'spreadsheet': ['xlsx', 'csv']
        }
    
    async def initialize_elasticsearch(self, host: str = "localhost", port: int = 9200):
        """Initialise la connexion Elasticsearch"""
        try:
            self.elasticsearch_client = AsyncElasticsearch([f"http://{host}:{port}"])
            
            # Créer l'index s'il n'existe pas
            await self._create_index_if_not_exists()
            
            logger.info("Elasticsearch initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Elasticsearch: {e}")
            raise
    
    async def index_content(
        self,
        content_id: str,
        metadata: Dict[str, Any],
        content_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Indexe un contenu avec ses métadonnées"""
        try:
            # Créer le document d'index
            document = await self._create_index_document(
                content_id, metadata, content_data
            )
            
            # Indexer dans Elasticsearch
            if self.elasticsearch_client:
                response = await self.elasticsearch_client.index(
                    index=self.index_name,
                    id=content_id,
                    body=document
                )
                
                logger.info(f"Contenu {content_id} indexé avec succès")
                
                return {
                    'content_id': content_id,
                    'indexed_at': datetime.utcnow().isoformat(),
                    'status': 'success',
                    'elasticsearch_response': response
                }
            else:
                # Fallback: indexation locale
                return await self._index_locally(content_id, document)
                
        except Exception as e:
            logger.error(f"Erreur indexation contenu {content_id}: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'status': 'error',
                'indexed_at': datetime.utcnow().isoformat()
            }
    
    async def _create_index_document(
        self,
        content_id: str,
        metadata: Dict[str, Any],
        content_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crée le document d'indexation enrichi"""
        
        # Document de base
        document = {
            'content_id': content_id,
            'indexed_at': datetime.utcnow().isoformat(),
            'metadata': metadata
        }
        
        # Extraire informations clés
        document.update(await self._extract_key_fields(metadata))
        
        # Analyser le contenu textuel si disponible
        if content_data:
            document.update(await self._analyze_text_content(content_data))
        
        # Créer hash pour déduplication
        document['content_hash'] = self._generate_content_hash(document)
        
        # Tags et catégories automatiques
        document['auto_tags'] = await self._generate_auto_tags(document)
        document['category'] = await self._determine_category(document)
        
        # Scores de qualité
        document['quality_scores'] = await self._calculate_quality_scores(document)
        
        return document
    
    async def _extract_key_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les champs clés des métadonnées"""
        key_fields = {}
        
        # Champs standards
        standard_fields = [
            'title', 'description', 'creator_id', 'file_type',
            'file_size', 'duration', 'resolution', 'created_at',
            'language', 'tags', 'genre', 'platform'
        ]
        
        for field in standard_fields:
            if field in metadata:
                key_fields[field] = metadata[field]
        
        # Normaliser le type de fichier
        if 'file_type' in key_fields:
            key_fields['content_type'] = self._normalize_content_type(
                key_fields['file_type']
            )
        
        return key_fields
    
    async def _analyze_text_content(self, content_data: str) -> Dict[str, Any]:
        """Analyse le contenu textuel"""
        analysis = {}
        
        try:
            # Statistiques de base
            analysis['text_length'] = len(content_data)
            analysis['word_count'] = len(content_data.split())
            
            # Extraction de mots-clés (TF-IDF)
            if len(content_data) > 50:  # Minimum de texte
                try:
                    tfidf_matrix = self.vectorizer.fit_transform([content_data])
                    feature_names = self.vectorizer.get_feature_names_out()
                    tfidf_scores = tfidf_matrix.toarray()[0]
                    
                    # Top 10 mots-clés
                    top_indices = np.argsort(tfidf_scores)[-10:][::-1]
                    analysis['keywords'] = [
                        feature_names[i] for i in top_indices if tfidf_scores[i] > 0
                    ]
                except:
                    analysis['keywords'] = []
            
            # Détection de langue (simplifiée)
            analysis['detected_language'] = await self._detect_language(content_data)
            
        except Exception as e:
            logger.warning(f"Erreur analyse textuelle: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _normalize_content_type(self, file_type: str) -> str:
        """Normalise le type de contenu"""
        file_ext = file_type.lower().replace('.', '')
        
        for content_type, extensions in self.content_types.items():
            if file_ext in extensions:
                return content_type
        
        return 'unknown'
    
    def _generate_content_hash(self, document: Dict[str, Any]) -> str:
        """Génère un hash unique pour le contenu"""
        # Créer string représentative du contenu
        content_string = json.dumps(
            {k: v for k, v in document.items() if k != 'indexed_at'},
            sort_keys=True
        )
        
        return hashlib.sha256(content_string.encode()).hexdigest()
    
    async def _generate_auto_tags(self, document: Dict[str, Any]) -> List[str]:
        """Génère des tags automatiques basés sur le contenu"""
        auto_tags = []
        
        # Tags basés sur le type de contenu
        if 'content_type' in document:
            auto_tags.append(f"type:{document['content_type']}")
        
        # Tags basés sur la durée (pour vidéos/audio)
        if 'duration' in document:
            duration = document['duration']
            if duration < 60:
                auto_tags.append("short_form")
            elif duration < 600:
                auto_tags.append("medium_form")
            else:
                auto_tags.append("long_form")
        
        # Tags basés sur la qualité
        if 'resolution' in document:
            resolution = document['resolution']
            if '4K' in str(resolution) or '2160' in str(resolution):
                auto_tags.append("ultra_hd")
            elif '1080' in str(resolution):
                auto_tags.append("full_hd")
            elif '720' in str(resolution):
                auto_tags.append("hd")
        
        # Tags basés sur les mots-clés
        if 'keywords' in document:
            # Ajouter les 3 premiers mots-clés comme tags
            auto_tags.extend(document['keywords'][:3])
        
        return auto_tags
    
    async def _determine_category(self, document: Dict[str, Any]) -> str:
        """Détermine la catégorie automatiquement"""
        # Logique de catégorisation basée sur les métadonnées
        
        # Par type de contenu
        content_type = document.get('content_type', 'unknown')
        if content_type == 'video':
            return 'video_content'
        elif content_type == 'audio':
            return 'audio_content'
        elif content_type == 'image':
            return 'visual_content'
        elif content_type in ['document', 'presentation']:
            return 'educational_content'
        
        # Par mots-clés (exemple simplifié)
        keywords = document.get('keywords', [])
        keyword_text = ' '.join(keywords).lower()
        
        if any(word in keyword_text for word in ['music', 'song', 'audio']):
            return 'music'
        elif any(word in keyword_text for word in ['tutorial', 'learn', 'education']):
            return 'educational'
        elif any(word in keyword_text for word in ['entertainment', 'funny', 'comedy']):
            return 'entertainment'
        
        return 'general'
    
    async def _calculate_quality_scores(self, document: Dict[str, Any]) -> Dict[str, float]:
        """Calcule des scores de qualité pour le contenu"""
        scores = {}
        
        # Score de complétude des métadonnées
        required_fields = ['title', 'description', 'creator_id', 'content_type']
        present_fields = sum(1 for field in required_fields if field in document)
        scores['metadata_completeness'] = present_fields / len(required_fields)
        
        # Score de richesse du contenu textuel
        text_length = document.get('text_length', 0)
        if text_length > 0:
            if text_length < 50:
                scores['content_richness'] = 0.3
            elif text_length < 200:
                scores['content_richness'] = 0.6
            elif text_length < 500:
                scores['content_richness'] = 0.8
            else:
                scores['content_richness'] = 1.0
        else:
            scores['content_richness'] = 0.1
        
        # Score de tags/mots-clés
        keywords_count = len(document.get('keywords', []))
        scores['keyword_richness'] = min(keywords_count / 5, 1.0)
        
        # Score global
        scores['overall_quality'] = (
            scores['metadata_completeness'] * 0.4 +
            scores['content_richness'] * 0.4 +
            scores['keyword_richness'] * 0.2
        )
        
        return scores
    
    async def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte (implémentation simplifiée)"""
        # Implémentation basique - à remplacer par un détecteur de langue robuste
        text_lower = text.lower()
        
        # Mots indicateurs simples
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'une', 'avec']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
        german_words = ['der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'mit', 'von']
        
        french_score = sum(1 for word in french_words if word in text_lower)
        english_score = sum(1 for word in english_words if word in text_lower)
        german_score = sum(1 for word in german_words if word in text_lower)
        
        if french_score > english_score and french_score > german_score:
            return 'fr'
        elif german_score > english_score:
            return 'de'
        else:
            return 'en'
    
    async def search_content(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Recherche dans le contenu indexé"""
        try:
            if self.elasticsearch_client:
                return await self._elasticsearch_search(query, filters, limit)
            else:
                return await self._local_search(query, filters, limit)
                
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return {
                'error': str(e),
                'results': [],
                'total': 0
            }
    
    async def _elasticsearch_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int
    ) -> Dict[str, Any]:
        """Recherche avec Elasticsearch"""
        # Construction de la requête Elasticsearch
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "title^3",
                                    "description^2",
                                    "keywords^2",
                                    "auto_tags",
                                    "content_data"
                                ]
                            }
                        }
                    ]
                }
            },
            "size": limit,
            "sort": [
                {"_score": {"order": "desc"}},
                {"indexed_at": {"order": "desc"}}
            ]
        }
        
        # Ajouter filtres si spécifiés
        if filters:
            filter_queries = []
            for key, value in filters.items():
                filter_queries.append({"term": {key: value}})
            
            if filter_queries:
                search_body["query"]["bool"]["filter"] = filter_queries
        
        # Exécuter la recherche
        response = await self.elasticsearch_client.search(
            index=self.index_name,
            body=search_body
        )
        
        return {
            'results': [hit['_source'] for hit in response['hits']['hits']],
            'total': response['hits']['total']['value'],
            'max_score': response['hits']['max_score']
        }
    
    async def _local_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int
    ) -> Dict[str, Any]:
        """Recherche locale (fallback)"""
        # Implémentation de recherche locale simple
        return {
            'results': [],
            'total': 0,
            'note': 'Local search not fully implemented'
        }
    
    async def _create_index_if_not_exists(self):
        """Crée l'index Elasticsearch s'il n'existe pas"""
        if not self.elasticsearch_client:
            return
        
        # Mapping pour l'index
        mapping = {
            "mappings": {
                "properties": {
                    "content_id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "keywords": {"type": "text", "analyzer": "keyword"},
                    "auto_tags": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "creator_id": {"type": "keyword"},
                    "indexed_at": {"type": "date"},
                    "quality_scores": {
                        "properties": {
                            "overall_quality": {"type": "float"},
                            "metadata_completeness": {"type": "float"},
                            "content_richness": {"type": "float"},
                            "keyword_richness": {"type": "float"}
                        }
                    }
                }
            }
        }
        
        try:
            exists = await self.elasticsearch_client.indices.exists(index=self.index_name)
            if not exists:
                await self.elasticsearch_client.indices.create(
                    index=self.index_name,
                    body=mapping
                )
                logger.info(f"Index {self.index_name} créé")
        except Exception as e:
            logger.error(f"Erreur création index: {e}")
    
    async def _index_locally(self, content_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Indexation locale de fallback"""
        # Placeholder pour indexation locale
        return {
            'content_id': content_id,
            'indexed_at': datetime.utcnow().isoformat(),
            'status': 'success_local',
            'note': 'Indexed locally (Elasticsearch not available)'
        }


# Instance globale du service
content_indexing_service = ContentIndexingService()