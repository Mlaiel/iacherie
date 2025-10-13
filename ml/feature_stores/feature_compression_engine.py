"""🗜️ Feature Compression Engine - Storage Optimization
=====================================================================
Module: ml/feature_stores/feature_compression_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FEATURE COMPRESSION & STORAGE OPTIMIZATION
Advanced compression techniques for feature storage optimization
- Multi-algorithm compression (LZ4, ZSTD, Gzip, Brotli)
- Feature-type specific compression strategies
- Lossy compression pour high-volume features
- Creator-specific compression profiles
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import gzip
import lz4.frame
import zstandard as zstd
import brotli
from pathlib import Path
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import io
import hashlib

# Configuration
logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Algorithmes de compression"""
    
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    CUSTOM_FEATURE = "custom_feature"  # Compression spécialisée features

class CompressionMode(Enum):
    """Modes de compression"""
    
    LOSSLESS = "lossless"      # Compression sans perte
    LOSSY = "lossy"            # Compression avec perte contrôlée
    ADAPTIVE = "adaptive"       # Adaptation automatique
    CREATOR_OPTIMIZED = "creator_optimized"  # Optimisé par creator type

class FeatureDataType(Enum):
    """Types de données features"""
    
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TIME_SERIES = "time_series"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    SPARSE = "sparse"

@dataclass
class CompressionProfile:
    """Profil de compression"""
    
    algorithm: CompressionAlgorithm
    mode: CompressionMode
    level: int = 6  # Niveau de compression (1-9)
    chunk_size: int = 64 * 1024  # 64KB chunks
    enable_preprocessing: bool = True
    lossy_tolerance: float = 0.01  # 1% tolerance pour lossy
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompressionResult:
    """Résultat de compression"""
    
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm_used: CompressionAlgorithm
    compression_time_ms: float
    decompression_time_ms: float = 0.0
    quality_score: float = 1.0  # 1.0 = parfait, <1.0 = avec perte
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def space_saved_percent(self) -> float:
        """Pourcentage d'espace économisé"""
        return (1 - (self.compressed_size / self.original_size)) * 100

@dataclass
class CompressionStats:
    """Statistiques de compression"""
    
    total_features: int = 0
    total_original_bytes: int = 0
    total_compressed_bytes: int = 0
    avg_compression_ratio: float = 0.0
    total_compression_time_ms: float = 0.0
    algorithm_usage: Dict[str, int] = field(default_factory=dict)
    creator_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)

class BaseCompressor(ABC):
    """Compresseur de base"""
    
    @abstractmethod
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """Compresser des données"""
        pass
    
    @abstractmethod
    async def decompress(self, data: bytes) -> bytes:
        """Décompresser des données"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du compresseur"""
        pass

class GzipCompressor(BaseCompressor):
    """Compresseur Gzip"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        return gzip.compress(data, compresslevel=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)
    
    @property
    def name(self) -> str:
        return "gzip"

class LZ4Compressor(BaseCompressor):
    """Compresseur LZ4 (rapide)"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        return lz4.frame.compress(data, compression_level=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return lz4.frame.decompress(data)
    
    @property
    def name(self) -> str:
        return "lz4"

class ZstdCompressor(BaseCompressor):
    """Compresseur Zstandard (équilibré)"""
    
    def __init__(self):
        self.compressor = zstd.ZstdCompressor()
        self.decompressor = zstd.ZstdDecompressor()
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        compressor = zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    
    async def decompress(self, data: bytes) -> bytes:
        return self.decompressor.decompress(data)
    
    @property
    def name(self) -> str:
        return "zstd"

class BrotliCompressor(BaseCompressor):
    """Compresseur Brotli (optimal)"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        return brotli.compress(data, quality=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return brotli.decompress(data)
    
    @property
    def name(self) -> str:
        return "brotli"

class FeatureSpecificCompressor(BaseCompressor):
    """Compresseur spécialisé pour features"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        # Détecter le type de feature et appliquer une compression spécialisée
        try:
            # Essayer de désérialiser pour détecter le type
            obj = pickle.loads(data)
            
            if isinstance(obj, np.ndarray):
                return await self._compress_numpy(obj, level)
            elif isinstance(obj, pd.DataFrame):
                return await self._compress_dataframe(obj, level)
            elif isinstance(obj, dict):
                return await self._compress_dict(obj, level)
            else:
                # Fallback vers compression générique
                return await self._generic_compress(data, level)
        except:
            return await self._generic_compress(data, level)
    
    async def decompress(self, data: bytes) -> bytes:
        # La décompression dépend du format utilisé
        # Pour simplifier, on utilise pickle
        return data  # À implémenter selon le format
    
    async def _compress_numpy(self, array: np.ndarray, level: int) -> bytes:
        """Compression spécialisée pour numpy arrays"""
        
        # Utiliser la compression native de numpy avec optimisations
        buffer = io.BytesIO()
        
        # Sauvegarder avec compression
        np.savez_compressed(buffer, array=array)
        compressed_data = buffer.getvalue()
        
        # Ajouter une compression supplémentaire si nécessaire
        if level > 6:
            compressor = zstd.ZstdCompressor(level=level)
            compressed_data = compressor.compress(compressed_data)
        
        return compressed_data
    
    async def _compress_dataframe(self, df: pd.DataFrame, level: int) -> bytes:
        """Compression spécialisée pour DataFrames"""
        
        # Utiliser parquet avec compression
        buffer = io.BytesIO()
        df.to_parquet(buffer, compression='snappy' if level <= 6 else 'gzip')
        return buffer.getvalue()
    
    async def _compress_dict(self, data: dict, level: int) -> bytes:
        """Compression spécialisée pour dictionnaires"""
        
        # Optimiser la sérialisation JSON puis compresser
        json_data = json.dumps(data, separators=(',', ':')).encode('utf-8')
        
        if level <= 3:
            return lz4.frame.compress(json_data)
        elif level <= 6:
            compressor = zstd.ZstdCompressor(level=level)
            return compressor.compress(json_data)
        else:
            return brotli.compress(json_data, quality=level)
    
    async def _generic_compress(self, data: bytes, level: int) -> bytes:
        """Compression générique"""
        
        if level <= 3:
            return lz4.frame.compress(data)
        elif level <= 6:
            compressor = zstd.ZstdCompressor(level=level)
            return compressor.compress(data)
        else:
            return brotli.compress(data, quality=level)
    
    @property
    def name(self) -> str:
        return "feature_specific"

class FeatureCompressionEngine:
    """
    🗜️ Feature Compression Engine
    
    Moteur de compression intelligent avec:
    - Multi-algorithmes avec sélection automatique
    - Compression spécialisée par type de feature
    - Profils creator-specific
    - Analytics et optimisation continue
    """
    
    def __init__(
        self,
        default_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD,
        enable_adaptive: bool = True,
        benchmark_interval: int = 100,  # Benchmark tous les 100 compressions
        enable_analytics: bool = True
    ):
        self.default_algorithm = default_algorithm
        self.enable_adaptive = enable_adaptive
        self.benchmark_interval = benchmark_interval
        self.enable_analytics = enable_analytics
        
        # Compresseurs disponibles
        self.compressors: Dict[CompressionAlgorithm, BaseCompressor] = {
            CompressionAlgorithm.GZIP: GzipCompressor(),
            CompressionAlgorithm.LZ4: LZ4Compressor(),
            CompressionAlgorithm.ZSTD: ZstdCompressor(),
            CompressionAlgorithm.BROTLI: BrotliCompressor(),
            CompressionAlgorithm.CUSTOM_FEATURE: FeatureSpecificCompressor()
        }
        
        # Profils de compression par creator type
        self.creator_profiles: Dict[str, CompressionProfile] = {
            'musician': CompressionProfile(
                algorithm=CompressionAlgorithm.ZSTD,
                mode=CompressionMode.LOSSLESS,
                level=6,
                enable_preprocessing=True
            ),
            'blogger': CompressionProfile(
                algorithm=CompressionAlgorithm.BROTLI,
                mode=CompressionMode.LOSSLESS,
                level=8,
                enable_preprocessing=True
            ),
            'photographer': CompressionProfile(
                algorithm=CompressionAlgorithm.CUSTOM_FEATURE,
                mode=CompressionMode.LOSSY,
                level=7,
                lossy_tolerance=0.05  # 5% pour images
            ),
            'influencer': CompressionProfile(
                algorithm=CompressionAlgorithm.LZ4,
                mode=CompressionMode.LOSSLESS,
                level=4,  # Rapidité prioritaire
                enable_preprocessing=False
            )
        }
        
        # Profils par type de feature
        self.feature_type_profiles: Dict[FeatureDataType, CompressionProfile] = {
            FeatureDataType.EMBEDDING: CompressionProfile(
                algorithm=CompressionAlgorithm.CUSTOM_FEATURE,
                mode=CompressionMode.LOSSY,
                level=6,
                lossy_tolerance=0.02
            ),
            FeatureDataType.TIME_SERIES: CompressionProfile(
                algorithm=CompressionAlgorithm.ZSTD,
                mode=CompressionMode.LOSSLESS,
                level=8
            ),
            FeatureDataType.CATEGORICAL: CompressionProfile(
                algorithm=CompressionAlgorithm.BROTLI,
                mode=CompressionMode.LOSSLESS,
                level=9
            ),
            FeatureDataType.SPARSE: CompressionProfile(
                algorithm=CompressionAlgorithm.CUSTOM_FEATURE,
                mode=CompressionMode.LOSSLESS,
                level=7
            )
        }
        
        # Statistiques et benchmarks
        self.stats = CompressionStats()
        self.algorithm_benchmarks: Dict[CompressionAlgorithm, List[float]] = defaultdict(list)
        self.compression_history: List[CompressionResult] = []
        
        # Cache pour les profils optimisés
        self.optimized_profiles: Dict[str, CompressionProfile] = {}
        
        logger.info("🗜️ Feature Compression Engine initialized")
    
    async def compress_feature(
        self,
        feature_name: str,
        feature_data: Any,
        creator_type: Optional[str] = None,
        feature_type: Optional[FeatureDataType] = None,
        profile: Optional[CompressionProfile] = None
    ) -> Tuple[bytes, CompressionResult]:
        """Compresser une feature"""
        
        start_time = time.time()
        
        # Sérialiser les données
        if isinstance(feature_data, bytes):
            serialized_data = feature_data
        else:
            serialized_data = pickle.dumps(feature_data)
        
        original_size = len(serialized_data)
        
        # Déterminer le profil de compression
        if profile is None:
            profile = self._select_compression_profile(
                feature_name, creator_type, feature_type, original_size
            )
        
        # Préprocessing si activé
        if profile.enable_preprocessing:
            serialized_data = await self._preprocess_data(serialized_data, feature_type)
        
        # Compresser
        compressor = self.compressors[profile.algorithm]
        
        try:
            if profile.algorithm == CompressionAlgorithm.NONE:
                compressed_data = serialized_data
            else:
                compressed_data = await compressor.compress(serialized_data, profile.level)
            
            compression_time = (time.time() - start_time) * 1000
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            # Créer le résultat
            result = CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm_used=profile.algorithm,
                compression_time_ms=compression_time,
                quality_score=1.0 if profile.mode == CompressionMode.LOSSLESS else (1.0 - profile.lossy_tolerance),
                metadata={
                    'feature_name': feature_name,
                    'creator_type': creator_type,
                    'feature_type': feature_type.value if feature_type else None,
                    'profile_used': profile.__dict__
                }
            )
            
            # Mettre à jour les statistiques
            await self._update_compression_stats(result, creator_type)
            
            # Benchmark périodique
            if len(self.compression_history) % self.benchmark_interval == 0:
                await self._run_adaptive_benchmark(serialized_data[:1024])  # Sample 1KB
            
            logger.debug(f"🗜️ Compressed {feature_name}: {original_size} → {compressed_size} bytes ({compression_ratio:.2f}x)")
            
            return compressed_data, result
            
        except Exception as e:
            logger.error(f"❌ Compression failed for {feature_name}: {e}")
            # Fallback vers pas de compression
            result = CompressionResult(
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                algorithm_used=CompressionAlgorithm.NONE,
                compression_time_ms=(time.time() - start_time) * 1000,
                metadata={'error': str(e)}
            )
            return serialized_data, result
    
    async def decompress_feature(
        self,
        compressed_data: bytes,
        compression_result: CompressionResult
    ) -> Any:
        """Décompresser une feature"""
        
        start_time = time.time()
        
        try:
            # Décompresser
            algorithm = compression_result.algorithm_used
            
            if algorithm == CompressionAlgorithm.NONE:
                decompressed_data = compressed_data
            else:
                compressor = self.compressors[algorithm]
                decompressed_data = await compressor.decompress(compressed_data)
            
            # Désérialiser
            feature_data = pickle.loads(decompressed_data)
            
            # Mettre à jour le temps de décompression
            compression_result.decompression_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(f"🔓 Decompressed feature in {compression_result.decompression_time_ms:.2f}ms")
            
            return feature_data
            
        except Exception as e:
            logger.error(f"❌ Decompression failed: {e}")
            raise
    
    def _select_compression_profile(
        self,
        feature_name: str,
        creator_type: Optional[str],
        feature_type: Optional[FeatureDataType],
        data_size: int
    ) -> CompressionProfile:
        """Sélectionner le profil de compression optimal"""
        
        # Vérifier le cache des profils optimisés
        cache_key = f"{creator_type}_{feature_type}_{data_size//1024//1024}"  # Par MB
        if cache_key in self.optimized_profiles:
            return self.optimized_profiles[cache_key]
        
        # Priorité: creator_type > feature_type > default
        if creator_type and creator_type in self.creator_profiles:
            base_profile = self.creator_profiles[creator_type]
        elif feature_type and feature_type in self.feature_type_profiles:
            base_profile = self.feature_type_profiles[feature_type]
        else:
            base_profile = CompressionProfile(
                algorithm=self.default_algorithm,
                mode=CompressionMode.LOSSLESS,
                level=6
            )
        
        # Adaptations basées sur la taille
        adapted_profile = self._adapt_profile_for_size(base_profile, data_size)
        
        # Cache le profil adapté
        self.optimized_profiles[cache_key] = adapted_profile
        
        return adapted_profile
    
    def _adapt_profile_for_size(
        self,
        base_profile: CompressionProfile,
        data_size: int
    ) -> CompressionProfile:
        """Adapter le profil selon la taille des données"""
        
        adapted = CompressionProfile(**base_profile.__dict__)
        
        # Petites features (< 1KB) → compression rapide
        if data_size < 1024:
            adapted.algorithm = CompressionAlgorithm.LZ4
            adapted.level = 1
        
        # Moyennes features (1KB - 1MB) → équilibré
        elif data_size < 1024 * 1024:
            if adapted.algorithm == CompressionAlgorithm.BROTLI:
                adapted.level = min(adapted.level, 6)  # Réduire pour vitesse
        
        # Grosses features (> 1MB) → compression maximale
        else:
            if adapted.algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.ZSTD]:
                adapted.level = 9
            adapted.chunk_size = 256 * 1024  # Plus gros chunks
        
        return adapted
    
    async def _preprocess_data(
        self,
        data: bytes,
        feature_type: Optional[FeatureDataType]
    ) -> bytes:
        """Préprocessing des données avant compression"""
        
        if feature_type == FeatureDataType.NUMERICAL:
            # Optimiser les arrays numériques
            try:
                obj = pickle.loads(data)
                if isinstance(obj, np.ndarray) and obj.dtype == np.float64:
                    # Convertir en float32 si possible
                    if np.allclose(obj.astype(np.float32), obj):
                        obj = obj.astype(np.float32)
                        data = pickle.dumps(obj)
            except:
                pass
        
        elif feature_type == FeatureDataType.CATEGORICAL:
            # Optimiser les données catégorielles
            try:
                obj = pickle.loads(data)
                if isinstance(obj, pd.Series) and obj.dtype == 'object':
                    # Convertir en category si avantageux
                    if len(obj.unique()) < len(obj) * 0.5:
                        obj = obj.astype('category')
                        data = pickle.dumps(obj)
            except:
                pass
        
        return data
    
    async def _update_compression_stats(
        self,
        result: CompressionResult,
        creator_type: Optional[str]
    ):
        """Mettre à jour les statistiques"""
        
        self.stats.total_features += 1
        self.stats.total_original_bytes += result.original_size
        self.stats.total_compressed_bytes += result.compressed_size
        self.stats.total_compression_time_ms += result.compression_time_ms
        
        # Moyenne mobile du ratio de compression
        alpha = 0.1
        self.stats.avg_compression_ratio = (
            alpha * result.compression_ratio + 
            (1 - alpha) * self.stats.avg_compression_ratio
        )
        
        # Statistiques par algorithme
        algo_name = result.algorithm_used.value
        self.stats.algorithm_usage[algo_name] = self.stats.algorithm_usage.get(algo_name, 0) + 1
        
        # Statistiques par creator
        if creator_type:
            if creator_type not in self.stats.creator_stats:
                self.stats.creator_stats[creator_type] = {
                    'features': 0,
                    'avg_ratio': 0.0,
                    'total_savings_mb': 0.0
                }
            
            creator_stat = self.stats.creator_stats[creator_type]
            creator_stat['features'] += 1
            creator_stat['avg_ratio'] = (
                alpha * result.compression_ratio + 
                (1 - alpha) * creator_stat['avg_ratio']
            )
            savings_bytes = result.original_size - result.compressed_size
            creator_stat['total_savings_mb'] += savings_bytes / 1024 / 1024
        
        # Garder un historique limité
        self.compression_history.append(result)
        if len(self.compression_history) > 1000:
            self.compression_history = self.compression_history[-1000:]
    
    async def _run_adaptive_benchmark(self, sample_data: bytes):
        """Lancer un benchmark adaptatif"""
        
        if not self.enable_adaptive:
            return
        
        benchmark_results = {}
        
        # Tester tous les algorithmes sur l'échantillon
        for algorithm, compressor in self.compressors.items():
            if algorithm == CompressionAlgorithm.NONE:
                continue
            
            try:
                start_time = time.time()
                compressed = await compressor.compress(sample_data, 6)
                compression_time = (time.time() - start_time) * 1000
                
                compression_ratio = len(sample_data) / len(compressed)
                
                # Score composite: ratio * (1 / temps)
                score = compression_ratio * (1000 / max(compression_time, 1))
                
                benchmark_results[algorithm] = {
                    'score': score,
                    'ratio': compression_ratio,
                    'time_ms': compression_time
                }
                
                # Mettre à jour l'historique des benchmarks
                self.algorithm_benchmarks[algorithm].append(score)
                if len(self.algorithm_benchmarks[algorithm]) > 100:
                    self.algorithm_benchmarks[algorithm] = self.algorithm_benchmarks[algorithm][-100:]
                
            except Exception as e:
                logger.warning(f"Benchmark failed for {algorithm}: {e}")
        
        # Adapter les profils selon les résultats
        if benchmark_results:
            best_algorithm = max(benchmark_results.keys(), key=lambda a: benchmark_results[a]['score'])
            
            # Mettre à jour le profil par défaut si un algorithme est clairement meilleur
            current_score = benchmark_results.get(self.default_algorithm, {}).get('score', 0)
            best_score = benchmark_results[best_algorithm]['score']
            
            if best_score > current_score * 1.2:  # 20% d'amélioration
                logger.info(f"🔄 Adapting default algorithm: {self.default_algorithm} → {best_algorithm}")
                self.default_algorithm = best_algorithm
    
    async def get_compression_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics de compression"""
        
        total_savings = self.stats.total_original_bytes - self.stats.total_compressed_bytes
        
        # Top algorithmes
        top_algorithms = sorted(
            self.stats.algorithm_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Performance par créateur
        creator_performance = {}
        for creator_type, stats in self.stats.creator_stats.items():
            creator_performance[creator_type] = {
                'features_compressed': stats['features'],
                'avg_compression_ratio': stats['avg_ratio'],
                'total_savings_mb': stats['total_savings_mb'],
                'efficiency_score': stats['avg_ratio'] * stats['features']
            }
        
        # Tendances récentes
        recent_results = self.compression_history[-100:] if self.compression_history else []
        recent_avg_ratio = np.mean([r.compression_ratio for r in recent_results]) if recent_results else 0
        
        return {
            'summary': {
                'total_features_compressed': self.stats.total_features,
                'total_space_saved_mb': total_savings / 1024 / 1024,
                'average_compression_ratio': self.stats.avg_compression_ratio,
                'total_compression_time_hours': self.stats.total_compression_time_ms / 1000 / 3600
            },
            'algorithms': {
                'usage_distribution': dict(top_algorithms),
                'current_default': self.default_algorithm.value,
                'performance_scores': {
                    algo.value: np.mean(scores) if scores else 0
                    for algo, scores in self.algorithm_benchmarks.items()
                }
            },
            'creators': creator_performance,
            'trends': {
                'recent_compression_ratio': recent_avg_ratio,
                'efficiency_trend': 'improving' if recent_avg_ratio > self.stats.avg_compression_ratio else 'stable'
            },
            'recommendations': await self._generate_recommendations()
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Générer des recommandations d'optimisation"""
        
        recommendations = []
        
        # Analyser les patterns d'usage
        if self.stats.avg_compression_ratio < 2.0:
            recommendations.append(
                "Consider enabling lossy compression for embedding features to improve compression ratio"
            )
        
        # Analyser les performances par creator
        for creator_type, stats in self.stats.creator_stats.items():
            if stats['avg_ratio'] < 1.5:
                recommendations.append(
                    f"Creator type '{creator_type}' shows low compression ratio - consider specialized preprocessing"
                )
        
        # Analyser les algorithmes
        if self.stats.algorithm_usage.get('lz4', 0) > self.stats.total_features * 0.5:
            recommendations.append(
                "High LZ4 usage detected - consider ZSTD for better compression on non-latency-critical features"
            )
        
        return recommendations

# Usage Example
async def main():
    """Exemple d'utilisation du Feature Compression Engine"""
    
    engine = FeatureCompressionEngine(
        default_algorithm=CompressionAlgorithm.ZSTD,
        enable_adaptive=True
    )
    
    # Données de test
    test_features = {
        'embedding': np.random.rand(512).astype(np.float32),
        'time_series': pd.Series(np.random.rand(1000)),
        'categorical': pd.Categorical(['A', 'B', 'C'] * 100),
        'sparse_dict': {str(i): np.random.rand() for i in range(0, 1000, 10)}
    }
    
    # Compresser différents types de features
    for name, data in test_features.items():
        compressed, result = await engine.compress_feature(
            feature_name=name,
            feature_data=data,
            creator_type="musician",
            feature_type=FeatureDataType.EMBEDDING if name == 'embedding' else None
        )
        
        print(f"Feature '{name}': {result.space_saved_percent:.1f}% space saved")
        
        # Décompresser pour vérifier
        decompressed = await engine.decompress_feature(compressed, result)
        print(f"Decompression successful: {type(decompressed)}")
    
    # Analytics
    analytics = await engine.get_compression_analytics()
    print(f"\nCompression Analytics:")
    print(f"Total space saved: {analytics['summary']['total_space_saved_mb']:.2f} MB")
    print(f"Average ratio: {analytics['summary']['average_compression_ratio']:.2f}x")

if __name__ == "__main__":
    asyncio.run(main())