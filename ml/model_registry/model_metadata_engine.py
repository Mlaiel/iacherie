"""🚀 Model Metadata Engine - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/model_metadata_engine.py
Author: Fahed Mlaiel (mlaiel@live.de) - DBA + Security Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MOTEUR DE MÉTADONNÉES DE MODÈLES
Gestion complète des métadonnées de modèles ML avec tracking business impact
- Performance metrics et business impact tracking
- Creator-specific model metadata
- Model lineage et dependency tracking
- Business ROI et engagement metrics
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

# Configuration
logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Types de créateurs supportés"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class MetricType(Enum):
    """Types de métriques"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    BUSINESS_ROI = "business_roi"
    ENGAGEMENT_RATE = "engagement_rate"
    CREATOR_SATISFACTION = "creator_satisfaction"

@dataclass
class ModelMetadata:
    """Métadonnées complètes d'un modèle"""
    model_id: str
    model_name: str
    version: str
    creator_type: CreatorType
    created_at: datetime
    updated_at: datetime
    author: str
    description: str
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    
    # Business metrics
    business_roi: float
    engagement_improvement: float
    creator_satisfaction_score: float
    revenue_impact: float
    
    # Technical metadata
    framework: str
    model_size_mb: float
    inference_latency_ms: float
    training_time_hours: float
    
    # Dependencies and lineage
    parent_models: List[str] = field(default_factory=list)
    child_models: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    feature_dependencies: List[str] = field(default_factory=list)
    
    # Creator-specific metadata
    content_types: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    
    # Tags and classification
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Custom metadata
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

class ModelMetadataEngine:
    """🔧 Moteur de gestion des métadonnées de modèles"""
    
    def __init__(self, 
                 db_url -> None: str = "postgresql -> None://user -> None:pass@localhost -> None:5432/ainflue_ml",
                 redis_url -> None: str = "redis -> None://localhost -> None:6379/0") -> None:
        self.db_url = db_url
        self.redis_url = redis_url
        self.engine = None
        self.redis_client = None
        self.session_maker = None
        
        # Métriques et monitoring
        self.metadata_operations = 0
        self.query_cache_hits = 0
        self.query_cache_misses = 0
        
    async def initialize(self) -> None:
        """Initialise les connexions et la base de données"""
        try:
            # Database connection
            self.engine = create_engine(self.db_url, echo=False)
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Redis connection pour cache
            self.redis_client = redis.from_url(self.redis_url)
            
            # Créer les tables si nécessaire
            await self._create_tables()
            
            logger.info("ModelMetadataEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ModelMetadataEngine: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crée les tables de métadonnées"""
        try:
            Base = declarative_base()
            
            # Table des métadonnées de modèles
            metadata_table = Table(
                'model_metadata',
                Base.metadata,
                Column('model_id', String(50), primary_key=True),
                Column('model_name', String(200)),
                Column('version', String(20)),
                Column('creator_type', String(20)),
                Column('created_at', DateTime),
                Column('updated_at', DateTime),
                Column('author', String(100)),
                Column('description', Text),
                Column('accuracy', Float),
                Column('precision', Float),
                Column('recall', Float),
                Column('f1_score', Float),
                Column('business_roi', Float),
                Column('engagement_improvement', Float),
                Column('creator_satisfaction_score', Float),
                Column('revenue_impact', Float),
                Column('framework', String(50)),
                Column('model_size_mb', Float),
                Column('inference_latency_ms', Float),
                Column('training_time_hours', Float),
                Column('parent_models', JSON),
                Column('child_models', JSON),
                Column('data_sources', JSON),
                Column('feature_dependencies', JSON),
                Column('content_types', JSON),
                Column('supported_formats', JSON),
                Column('target_audience', JSON),
                Column('tags', JSON),
                Column('categories', JSON),
                Column('custom_metadata', JSON)
            )
            
            Base.metadata.create_all(self.engine)
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def store_metadata(self, metadata: ModelMetadata) -> bool:
        """Stocke les métadonnées d'un modèle"""
        try:
            session: Session = self.session_maker()
            
            # Convertir en format DB
            metadata_dict = {
                'model_id': metadata.model_id,
                'model_name': metadata.model_name,
                'version': metadata.version,
                'creator_type': metadata.creator_type.value,
                'created_at': metadata.created_at,
                'updated_at': metadata.updated_at,
                'author': metadata.author,
                'description': metadata.description,
                'accuracy': metadata.accuracy,
                'precision': metadata.precision,
                'recall': metadata.recall,
                'f1_score': metadata.f1_score,
                'business_roi': metadata.business_roi,
                'engagement_improvement': metadata.engagement_improvement,
                'creator_satisfaction_score': metadata.creator_satisfaction_score,
                'revenue_impact': metadata.revenue_impact,
                'framework': metadata.framework,
                'model_size_mb': metadata.model_size_mb,
                'inference_latency_ms': metadata.inference_latency_ms,
                'training_time_hours': metadata.training_time_hours,
                'parent_models': json.dumps(metadata.parent_models),
                'child_models': json.dumps(metadata.child_models),
                'data_sources': json.dumps(metadata.data_sources),
                'feature_dependencies': json.dumps(metadata.feature_dependencies),
                'content_types': json.dumps(metadata.content_types),
                'supported_formats': json.dumps(metadata.supported_formats),
                'target_audience': json.dumps(metadata.target_audience),
                'tags': json.dumps(metadata.tags),
                'categories': json.dumps(metadata.categories),
                'custom_metadata': json.dumps(metadata.custom_metadata)
            }
            
            # Insert or update
            session.execute(
                "INSERT INTO model_metadata VALUES (:model_id, :model_name, :version, :creator_type, "
                ":created_at, :updated_at, :author, :description, :accuracy, :precision, :recall, "
                ":f1_score, :business_roi, :engagement_improvement, :creator_satisfaction_score, "
                ":revenue_impact, :framework, :model_size_mb, :inference_latency_ms, "
                ":training_time_hours, :parent_models, :child_models, :data_sources, "
                ":feature_dependencies, :content_types, :supported_formats, :target_audience, "
                ":tags, :categories, :custom_metadata) "
                "ON CONFLICT (model_id) DO UPDATE SET "
                "updated_at = :updated_at, accuracy = :accuracy, precision = :precision, "
                "recall = :recall, f1_score = :f1_score, business_roi = :business_roi",
                metadata_dict
            )
            
            session.commit()
            session.close()
            
            # Cache dans Redis
            cache_key = f"metadata:{metadata.model_id}"
            await self._cache_metadata(cache_key, metadata)
            
            self.metadata_operations += 1
            logger.info(f"Stored metadata for model {metadata.model_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
            return False
    
    async def get_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Récupère les métadonnées d'un modèle"""
        try:
            # Vérifier le cache Redis d'abord
            cache_key = f"metadata:{model_id}"
            cached_metadata = await self._get_cached_metadata(cache_key)
            
            if cached_metadata:
                self.query_cache_hits += 1
                return cached_metadata
            
            # Requête base de données
            session: Session = self.session_maker()
            result = session.execute(
                "SELECT * FROM model_metadata WHERE model_id = :model_id",
                {"model_id": model_id}
            ).fetchone()
            
            session.close()
            
            if not result:
                self.query_cache_misses += 1
                return None
            
            # Convertir en ModelMetadata
            metadata = self._row_to_metadata(result)
            
            # Cache le résultat
            await self._cache_metadata(cache_key, metadata)
            
            self.query_cache_misses += 1
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {model_id}: {e}")
            return None
    
    async def search_models(self, 
                          creator_type: Optional[CreatorType] = None,
                          tags: Optional[List[str]] = None,
                          min_accuracy: Optional[float] = None,
                          min_business_roi: Optional[float] = None) -> List[ModelMetadata]:
        """Recherche de modèles par critères"""
        try:
            session: Session = self.session_maker()
            
            query = "SELECT * FROM model_metadata WHERE 1=1"
            params = {}
            
            if creator_type:
                query += " AND creator_type = :creator_type"
                params["creator_type"] = creator_type.value
            
            if min_accuracy:
                query += " AND accuracy >= :min_accuracy"
                params["min_accuracy"] = min_accuracy
            
            if min_business_roi:
                query += " AND business_roi >= :min_business_roi"
                params["min_business_roi"] = min_business_roi
            
            if tags:
                # Recherche dans les tags JSON
                for i, tag in enumerate(tags):
                    query += f" AND tags LIKE :tag_{i}"
                    params[f"tag_{i}"] = f"%{tag}%"
            
            query += " ORDER BY updated_at DESC"
            
            results = session.execute(query, params).fetchall()
            session.close()
            
            models = [self._row_to_metadata(row) for row in results]
            
            logger.info(f"Found {len(models)} models matching criteria")
            return models
            
        except Exception as e:
            logger.error(f"Failed to search models: {e}")
            return []
    
    async def get_model_lineage(self, model_id: str) -> Dict[str, List[str]]:
        """Obtient la lignée complète d'un modèle"""
        try:
            metadata = await self.get_metadata(model_id)
            if not metadata:
                return {}
            
            lineage = {
                "parents": metadata.parent_models,
                "children": metadata.child_models,
                "data_sources": metadata.data_sources,
                "feature_dependencies": metadata.feature_dependencies
            }
            
            # Récursion pour les parents
            for parent_id in metadata.parent_models:
                parent_lineage = await self.get_model_lineage(parent_id)
                lineage["ancestors"] = lineage.get("ancestors", []) + parent_lineage.get("parents", [])
            
            return lineage
            
        except Exception as e:
            logger.error(f"Failed to get model lineage: {e}")
            return {}
    
    async def update_business_metrics(self, model_id: str, 
                                    business_roi: Optional[float] = None,
                                    engagement_improvement: Optional[float] = None,
                                    creator_satisfaction: Optional[float] = None,
                                    revenue_impact: Optional[float] = None) -> bool:
        """Met à jour les métriques business d'un modèle"""
        try:
            session: Session = self.session_maker()
            
            updates = []
            params = {"model_id": model_id}
            
            if business_roi is not None:
                updates.append("business_roi = :business_roi")
                params["business_roi"] = business_roi
            
            if engagement_improvement is not None:
                updates.append("engagement_improvement = :engagement_improvement")
                params["engagement_improvement"] = engagement_improvement
            
            if creator_satisfaction is not None:
                updates.append("creator_satisfaction_score = :creator_satisfaction")
                params["creator_satisfaction"] = creator_satisfaction
            
            if revenue_impact is not None:
                updates.append("revenue_impact = :revenue_impact")
                params["revenue_impact"] = revenue_impact
            
            if updates:
                updates.append("updated_at = :updated_at")
                params["updated_at"] = datetime.utcnow()
                
                query = f"UPDATE model_metadata SET {', '.join(updates)} WHERE model_id = :model_id"
                session.execute(query, params)
                session.commit()
            
            session.close()
            
            # Invalider le cache
            cache_key = f"metadata:{model_id}"
            self.redis_client.delete(cache_key)
            
            logger.info(f"Updated business metrics for model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update business metrics: {e}")
            return False
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques de performance du moteur"""
        try:
            total_queries = self.query_cache_hits + self.query_cache_misses
            cache_hit_rate = (self.query_cache_hits / total_queries * 100) if total_queries > 0 else 0
            
            # Statistiques DB
            session: Session = self.session_maker()
            total_models = session.execute("SELECT COUNT(*) FROM model_metadata").scalar()
            
            # Top creator types
            creator_stats = session.execute(
                "SELECT creator_type, COUNT(*) as count FROM model_metadata GROUP BY creator_type"
            ).fetchall()
            
            session.close()
            
            stats = {
                "total_models": total_models,
                "metadata_operations": self.metadata_operations,
                "cache_hit_rate": cache_hit_rate,
                "query_cache_hits": self.query_cache_hits,
                "query_cache_misses": self.query_cache_misses,
                "creator_distribution": {row[0]: row[1] for row in creator_stats}
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}
    
    async def _cache_metadata(self, cache_key -> None: str, metadata -> None: ModelMetadata) -> None:
        """Cache les métadonnées dans Redis"""
        try:
            serialized = pickle.dumps(metadata)
            self.redis_client.setex(cache_key, 3600, serialized)  # 1 heure
        except Exception as e:
            logger.error(f"Failed to cache metadata: {e}")
    
    async def _get_cached_metadata(self, cache_key: str) -> Optional[ModelMetadata]:
        """Récupère les métadonnées du cache Redis"""
        try:
            serialized = self.redis_client.get(cache_key)
            if serialized:
                return pickle.loads(serialized)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached metadata: {e}")
            return None
    
    def _row_to_metadata(self, row) -> ModelMetadata:
        """Convertit une ligne DB en ModelMetadata"""
        return ModelMetadata(
            model_id=row[0],
            model_name=row[1],
            version=row[2],
            creator_type=CreatorType(row[3]),
            created_at=row[4],
            updated_at=row[5],
            author=row[6],
            description=row[7],
            accuracy=row[8],
            precision=row[9],
            recall=row[10],
            f1_score=row[11],
            business_roi=row[12],
            engagement_improvement=row[13],
            creator_satisfaction_score=row[14],
            revenue_impact=row[15],
            framework=row[16],
            model_size_mb=row[17],
            inference_latency_ms=row[18],
            training_time_hours=row[19],
            parent_models=json.loads(row[20]) if row[20] else [],
            child_models=json.loads(row[21]) if row[21] else [],
            data_sources=json.loads(row[22]) if row[22] else [],
            feature_dependencies=json.loads(row[23]) if row[23] else [],
            content_types=json.loads(row[24]) if row[24] else [],
            supported_formats=json.loads(row[25]) if row[25] else [],
            target_audience=json.loads(row[26]) if row[26] else {},
            tags=json.loads(row[27]) if row[27] else [],
            categories=json.loads(row[28]) if row[28] else [],
            custom_metadata=json.loads(row[29]) if row[29] else {}
        )

# Usage example
async def demo_metadata_engine() -> None:
    """Démo du moteur de métadonnées"""
    engine = ModelMetadataEngine()
    await engine.initialize()
    
    # Créer des métadonnées de modèle
    metadata = ModelMetadata(
        model_id="musician-classifier-v1.0",
        model_name="Musician Content Classifier",
        version="1.0",
        creator_type=CreatorType.MUSICIAN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        author="fahed@ainflue.com",
        description="Classificateur de contenu musical avec analyse d'engagement",
        accuracy=0.92,
        precision=0.89,
        recall=0.94,
        f1_score=0.91,
        business_roi=1.35,
        engagement_improvement=0.28,
        creator_satisfaction_score=0.85,
        revenue_impact=15000.0,
        framework="pytorch",
        model_size_mb=45.2,
        inference_latency_ms=78,
        training_time_hours=12.5,
        content_types=["audio", "metadata", "lyrics"],
        supported_formats=["mp3", "wav", "flac"],
        tags=["music", "classification", "engagement", "creator"],
        categories=["content_analysis", "musician_tools"]
    )
    
    # Stocker les métadonnées
    success = await engine.store_metadata(metadata)
    print(f"✅ Metadata stored: {success}")
    
    # Récupérer les métadonnées
    retrieved = await engine.get_metadata("musician-classifier-v1.0")
    print(f"✅ Metadata retrieved: {retrieved.model_name if retrieved else 'Not found'}")
    
    # Rechercher des modèles
    models = await engine.search_models(
        creator_type=CreatorType.MUSICIAN,
        min_accuracy=0.90
    )
    print(f"✅ Found {len(models)} models for musicians with >90% accuracy")
    
    # Mettre à jour les métriques business
    await engine.update_business_metrics(
        "musician-classifier-v1.0",
        business_roi=1.42,
        engagement_improvement=0.31
    )
    
    # Statistiques
    stats = await engine.get_performance_stats()
    print(f"✅ Performance stats: {stats}")

if __name__ == "__main__":
    asyncio.run(demo_metadata_engine())