#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Compression Optimizer - Optimiseur Compression Enterprise
==========================================================

Optimiseur intelligent de compression avec sélection automatique
d'algorithmes et niveaux pour maximiser l'efficacité cache.

**Rôles Experts:**
- **DBA**: Optimisation stockage, algorithmes compression avancés
- **Backend Senior**: Architecture compression haute performance
- **Lead Dev IA**: Sélection intelligente algorithmes via ML
- **DevOps**: Monitoring compression, métriques performance

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import zlib
import lz4.frame
import brotli
import gzip
import lzma
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import numpy as np
from collections import defaultdict, deque
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Algorithmes de compression"""
    NONE = "none"
    ZLIB = "zlib"
    LZ4 = "lz4"
    BROTLI = "brotli"
    GZIP = "gzip"
    LZMA = "lzma"
    ZSTD = "zstd"

class DataPattern(Enum):
    """Patterns de données détectés"""
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"
    REPETITIVE = "repetitive"
    RANDOM = "random"
    SPARSE = "sparse"
    STRUCTURED = "structured"

@dataclass
class CompressionProfile:
    """Profil compression par algorithme"""
    algorithm: CompressionAlgorithm
    level: int
    avg_ratio: float = 0.0
    avg_time_ms: float = 0.0
    success_rate: float = 1.0
    data_pattern_scores: Dict[str, float] = field(default_factory=dict)
    use_count: int = 0

@dataclass
class CompressionMetrics:
    """Métriques compression"""
    algorithm: str
    level: int
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time_ms: float
    decompression_time_ms: float
    pattern: str
    efficiency_score: float

class CompressionOptimizer:
    """
    ⚡ Optimiseur Compression Enterprise
    
    **DBA**: Algorithmes compression optimisés stockage
    **Backend Senior**: Architecture compression haute performance
    **Lead Dev IA**: Sélection automatique via ML et patterns
    **DevOps**: Monitoring et métriques compression temps réel
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Profils performance algorithmes
        self.profiles: Dict[str, CompressionProfile] = {}
        self._initialize_profiles()
        
        # Historique et métriques
        self.compression_history: deque = deque(maxlen=5000)
        self.pattern_cache: Dict[str, DataPattern] = {}
        
        # Cache recommandations
        self.recommendations_cache: Dict[Tuple[str, int], Tuple[CompressionAlgorithm, int]] = {}
        
        logger.info("⚡ Compression Optimizer initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration optimisée par défaut"""
        return {
            'compression_threshold': 512,  # Comprimer si > 512 bytes
            'max_compression_time_ms': 100,  # Limite temps compression
            'target_ratio': 2.0,  # Ratio cible minimum
            'enable_adaptive_level': True,
            'cache_recommendations': True,
            'algorithm_weights': {
                'speed': 0.4,
                'ratio': 0.4,
                'reliability': 0.2
            },
            'default_levels': {
                'zlib': 6,
                'brotli': 4,
                'lzma': 6,
                'gzip': 6
            },
            'pattern_detection': True,
            'benchmark_interval': 3600  # Re-benchmark chaque heure
        }
    
    def _initialize_profiles(self):
        """**Backend Senior**: Initialisation profils algorithmes"""
        algorithms = [
            (CompressionAlgorithm.LZ4, 0),
            (CompressionAlgorithm.ZLIB, 1), (CompressionAlgorithm.ZLIB, 6), (CompressionAlgorithm.ZLIB, 9),
            (CompressionAlgorithm.BROTLI, 1), (CompressionAlgorithm.BROTLI, 4), (CompressionAlgorithm.BROTLI, 8),
            (CompressionAlgorithm.GZIP, 1), (CompressionAlgorithm.GZIP, 6), (CompressionAlgorithm.GZIP, 9),
            (CompressionAlgorithm.LZMA, 1), (CompressionAlgorithm.LZMA, 6)
        ]
        
        for algorithm, level in algorithms:
            key = f"{algorithm.value}_{level}"
            self.profiles[key] = CompressionProfile(
                algorithm=algorithm,
                level=level,
                data_pattern_scores=self._get_initial_pattern_scores(algorithm)
            )
    
    def _get_initial_pattern_scores(self, algorithm: CompressionAlgorithm) -> Dict[str, float]:
        """**Lead Dev IA**: Scores initiaux patterns par algorithme"""
        
        # Scores basés sur caractéristiques algorithmes
        scores = {
            CompressionAlgorithm.LZ4: {
                'text': 0.7, 'json': 0.8, 'binary': 0.6, 'repetitive': 0.9,
                'random': 0.3, 'sparse': 0.7, 'structured': 0.8
            },
            CompressionAlgorithm.ZLIB: {
                'text': 0.8, 'json': 0.9, 'binary': 0.7, 'repetitive': 0.9,
                'random': 0.4, 'sparse': 0.8, 'structured': 0.9
            },
            CompressionAlgorithm.BROTLI: {
                'text': 0.9, 'json': 0.9, 'binary': 0.8, 'repetitive': 0.9,
                'random': 0.5, 'sparse': 0.9, 'structured': 0.9
            },
            CompressionAlgorithm.GZIP: {
                'text': 0.8, 'json': 0.8, 'binary': 0.7, 'repetitive': 0.8,
                'random': 0.4, 'sparse': 0.7, 'structured': 0.8
            },
            CompressionAlgorithm.LZMA: {
                'text': 0.9, 'json': 0.8, 'binary': 0.9, 'repetitive': 0.9,
                'random': 0.6, 'sparse': 0.9, 'structured': 0.8
            }
        }
        
        return scores.get(algorithm, {pattern.value: 0.5 for pattern in DataPattern})
    
    def detect_data_pattern(self, data: bytes) -> DataPattern:
        """**Lead Dev IA**: Détection pattern données intelligent"""
        
        # Cache pattern pour éviter re-calculs
        data_hash = hashlib.md5(data[:1024]).hexdigest()  # Hash premiers 1KB
        if data_hash in self.pattern_cache:
            return self.pattern_cache[data_hash]
        
        try:
            # Tentative décodage texte
            text_data = data.decode('utf-8')
            
            # Test JSON
            if text_data.strip().startswith(('{', '[')):
                pattern = DataPattern.JSON
            # Test répétitif
            elif self._is_repetitive_text(text_data):
                pattern = DataPattern.REPETITIVE
            # Test structuré (lignes similaires)
            elif self._is_structured_text(text_data):
                pattern = DataPattern.STRUCTURED
            else:
                pattern = DataPattern.TEXT
                
        except UnicodeDecodeError:
            # Données binaires
            if self._is_sparse_binary(data):
                pattern = DataPattern.SPARSE
            elif self._is_repetitive_binary(data):
                pattern = DataPattern.REPETITIVE
            elif self._is_random_binary(data):
                pattern = DataPattern.RANDOM
            else:
                pattern = DataPattern.BINARY
        
        # Cache résultat
        self.pattern_cache[data_hash] = pattern
        return pattern
    
    def _is_repetitive_text(self, text: str) -> bool:
        """**Lead Dev IA**: Détection texte répétitif"""
        if len(text) < 100:
            return False
        
        # Recherche patterns répétés
        for pattern_len in [2, 4, 8, 16]:
            pattern = text[:pattern_len]
            if text.count(pattern) > len(text) // (pattern_len * 2):
                return True
        return False
    
    def _is_structured_text(self, text: str) -> bool:
        """**Lead Dev IA**: Détection texte structuré"""
        lines = text.split('\n')
        if len(lines) < 3:
            return False
        
        # Vérification structure similaire entre lignes
        first_line_tokens = len(lines[0].split())
        similar_structure = sum(
            1 for line in lines[1:5]  # Test 5 premières lignes
            if abs(len(line.split()) - first_line_tokens) <= 2
        )
        
        return similar_structure >= 3
    
    def _is_sparse_binary(self, data: bytes) -> bool:
        """**DBA**: Détection données binaires éparses"""
        if len(data) < 100:
            return False
        
        # Calcul entropie simple
        zero_count = data.count(0)
        return zero_count > len(data) * 0.7  # > 70% de zéros
    
    def _is_repetitive_binary(self, data: bytes) -> bool:
        """**DBA**: Détection binaire répétitif"""
        if len(data) < 100:
            return False
        
        # Test patterns binaires courts
        for pattern_len in [1, 2, 4]:
            pattern = data[:pattern_len]
            occurrences = 0
            for i in range(0, len(data) - pattern_len, pattern_len):
                if data[i:i+pattern_len] == pattern:
                    occurrences += 1
            
            if occurrences > len(data) // (pattern_len * 4):
                return True
        return False
    
    def _is_random_binary(self, data: bytes) -> bool:
        """**DBA**: Détection données aléatoires"""
        if len(data) < 256:
            return False
        
        # Calcul entropie approximative
        byte_counts = [0] * 256
        for byte in data[:1024]:  # Test premiers 1KB
            byte_counts[byte] += 1
        
        # Distribution uniforme = entropie élevée = données aléatoires
        non_zero_counts = [c for c in byte_counts if c > 0]
        if len(non_zero_counts) < 200:
            return False
        
        # Variance des comptes
        mean_count = sum(non_zero_counts) / len(non_zero_counts)
        variance = sum((c - mean_count) ** 2 for c in non_zero_counts) / len(non_zero_counts)
        
        return variance < mean_count * 2  # Distribution relativement uniforme
    
    async def compress_optimal(
        self,
        data: bytes,
        target_ratio: Optional[float] = None,
        max_time_ms: Optional[float] = None
    ) -> Tuple[bytes, CompressionMetrics]:
        """**Backend Senior**: Compression optimale automatique"""
        
        if len(data) < self.config.get('compression_threshold', 512):
            # Pas de compression pour petites données
            return data, CompressionMetrics(
                algorithm='none', level=0, original_size=len(data),
                compressed_size=len(data), compression_ratio=1.0,
                compression_time_ms=0, decompression_time_ms=0,
                pattern='small', efficiency_score=1.0
            )
        
        start_time = time.time()
        
        # Détection pattern
        pattern = self.detect_data_pattern(data)
        
        # Sélection algorithme optimal
        algorithm, level = await self._select_optimal_algorithm(
            data, pattern, target_ratio, max_time_ms
        )
        
        # Compression
        try:
            compress_start = time.time()
            compressed_data = await self._compress_with_algorithm(data, algorithm, level)
            compression_time = (time.time() - compress_start) * 1000
            
            # Test décompression pour validation
            decompress_start = time.time()
            decompressed = await self._decompress_with_algorithm(compressed_data, algorithm)
            decompression_time = (time.time() - decompress_start) * 1000
            
            # Validation intégrité
            if decompressed != data:
                raise ValueError("Échec validation intégrité compression")
            
            # Métriques
            compression_ratio = len(data) / len(compressed_data)
            efficiency_score = self._calculate_efficiency_score(
                compression_ratio, compression_time, decompression_time
            )
            
            metrics = CompressionMetrics(
                algorithm=algorithm.value,
                level=level,
                original_size=len(data),
                compressed_size=len(compressed_data),
                compression_ratio=compression_ratio,
                compression_time_ms=compression_time,
                decompression_time_ms=decompression_time,
                pattern=pattern.value,
                efficiency_score=efficiency_score
            )
            
            # Mise à jour profils
            await self._update_profile(algorithm, level, metrics, pattern)
            
            # Historique
            self.compression_history.append({
                'timestamp': time.time(),
                'algorithm': algorithm.value,
                'level': level,
                'pattern': pattern.value,
                'original_size': len(data),
                'compressed_size': len(compressed_data),
                'ratio': compression_ratio,
                'time_ms': compression_time,
                'efficiency': efficiency_score
            })
            
            logger.debug(f"✅ Compression {algorithm.value}({level}): {compression_ratio:.2f}x")
            
            return compressed_data, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur compression {algorithm.value}: {e}")
            # Fallback: pas de compression
            return data, CompressionMetrics(
                algorithm='none', level=0, original_size=len(data),
                compressed_size=len(data), compression_ratio=1.0,
                compression_time_ms=0, decompression_time_ms=0,
                pattern=pattern.value, efficiency_score=0.0
            )
    
    async def _select_optimal_algorithm(
        self,
        data: bytes,
        pattern: DataPattern,
        target_ratio: Optional[float],
        max_time_ms: Optional[float]
    ) -> Tuple[CompressionAlgorithm, int]:
        """**Lead Dev IA**: Sélection algorithme optimal**"""
        
        target_ratio = target_ratio or self.config.get('target_ratio', 2.0)
        max_time_ms = max_time_ms or self.config.get('max_compression_time_ms', 100)
        
        # Cache lookup
        cache_key = (pattern.value, len(data) // 1024)  # KB buckets
        if (self.config.get('cache_recommendations') and 
            cache_key in self.recommendations_cache):
            return self.recommendations_cache[cache_key]
        
        # Scoring des algorithmes
        best_algorithm = CompressionAlgorithm.LZ4
        best_level = 0
        best_score = 0
        
        weights = self.config.get('algorithm_weights', {})
        
        for profile_key, profile in self.profiles.items():
            if profile.use_count == 0:
                continue  # Pas de données historiques
            
            pattern_score = profile.data_pattern_scores.get(pattern.value, 0.5)
            
            # Score composite
            speed_score = max(0, 1.0 - profile.avg_time_ms / max_time_ms)
            ratio_score = min(1.0, profile.avg_ratio / target_ratio)
            reliability_score = profile.success_rate
            
            composite_score = (
                speed_score * weights.get('speed', 0.4) +
                ratio_score * weights.get('ratio', 0.4) +
                reliability_score * weights.get('reliability', 0.2)
            ) * pattern_score
            
            if composite_score > best_score:
                best_score = composite_score
                best_algorithm = profile.algorithm
                best_level = profile.level
        
        # Cache résultat
        if self.config.get('cache_recommendations'):
            self.recommendations_cache[cache_key] = (best_algorithm, best_level)
        
        return best_algorithm, best_level
    
    async def _compress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
        level: int
    ) -> bytes:
        """**DBA**: Compression avec algorithme spécifique"""
        
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data, level)
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.compress(data)
        
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.compress(data, quality=level)
        
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=level)
        
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.compress(data, preset=level)
        
        else:
            return data
    
    async def _decompress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """**DBA**: Décompression avec algorithme spécifique"""
        
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(data)
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.decompress(data)
        
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.decompress(data)
        
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
        
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.decompress(data)
        
        else:
            return data
    
    def _calculate_efficiency_score(
        self,
        compression_ratio: float,
        compression_time: float,
        decompression_time: float
    ) -> float:
        """**Lead Dev IA**: Calcul score efficacité composite"""
        
        # Score basé sur ratio et vitesse
        ratio_score = min(1.0, compression_ratio / 3.0)  # Normalise à 3x max
        
        total_time = compression_time + decompression_time
        time_score = max(0, 1.0 - total_time / 1000.0)  # Pénalise si > 1s
        
        # Score composite
        efficiency = ratio_score * 0.6 + time_score * 0.4
        return min(1.0, efficiency)
    
    async def _update_profile(
        self,
        algorithm: CompressionAlgorithm,
        level: int,
        metrics: CompressionMetrics,
        pattern: DataPattern
    ):
        """**DevOps**: Mise à jour profil performance**"""
        
        profile_key = f"{algorithm.value}_{level}"
        if profile_key not in self.profiles:
            return
        
        profile = self.profiles[profile_key]
        profile.use_count += 1
        
        # Moyenne mobile
        alpha = 0.1
        
        if profile.avg_ratio > 0:
            profile.avg_ratio = profile.avg_ratio * (1 - alpha) + metrics.compression_ratio * alpha
        else:
            profile.avg_ratio = metrics.compression_ratio
        
        if profile.avg_time_ms > 0:
            profile.avg_time_ms = profile.avg_time_ms * (1 - alpha) + metrics.compression_time_ms * alpha
        else:
            profile.avg_time_ms = metrics.compression_time_ms
        
        # Mise à jour score pattern
        current_pattern_score = profile.data_pattern_scores.get(pattern.value, 0.5)
        new_pattern_score = min(1.0, current_pattern_score + 0.05)  # Amélioration graduelle
        profile.data_pattern_scores[pattern.value] = new_pattern_score
    
    async def decompress(self, compressed_data: bytes, algorithm: str) -> bytes:
        """**Backend Senior**: Décompression générique**"""
        
        try:
            algo_enum = CompressionAlgorithm(algorithm)
            return await self._decompress_with_algorithm(compressed_data, algo_enum)
        except ValueError:
            logger.error(f"❌ Algorithme décompression inconnu: {algorithm}")
            return compressed_data
        except Exception as e:
            logger.error(f"❌ Erreur décompression {algorithm}: {e}")
            raise
    
    async def benchmark_algorithms(
        self,
        test_data: List[bytes],
        algorithms: Optional[List[CompressionAlgorithm]] = None
    ) -> Dict[str, Any]:
        """**DevOps**: Benchmark algorithmes compression**"""
        
        algorithms = algorithms or [
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZLIB,
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.GZIP
        ]
        
        results = {}
        
        for data in test_data:
            pattern = self.detect_data_pattern(data)
            data_size_kb = len(data) // 1024
            
            for algorithm in algorithms:
                levels = [0] if algorithm == CompressionAlgorithm.LZ4 else [1, 6, 9]
                
                for level in levels:
                    try:
                        # Test compression
                        start_time = time.time()
                        compressed = await self._compress_with_algorithm(data, algorithm, level)
                        compression_time = (time.time() - start_time) * 1000
                        
                        # Test décompression
                        start_time = time.time()
                        decompressed = await self._decompress_with_algorithm(compressed, algorithm)
                        decompression_time = (time.time() - start_time) * 1000
                        
                        # Validation
                        integrity_ok = decompressed == data
                        
                        ratio = len(data) / len(compressed)
                        efficiency = self._calculate_efficiency_score(
                            ratio, compression_time, decompression_time
                        )
                        
                        key = f"{algorithm.value}_{level}_{pattern.value}_{data_size_kb}kb"
                        results[key] = {
                            'algorithm': algorithm.value,
                            'level': level,
                            'pattern': pattern.value,
                            'data_size_kb': data_size_kb,
                            'compression_ratio': ratio,
                            'compression_time_ms': compression_time,
                            'decompression_time_ms': decompression_time,
                            'total_time_ms': compression_time + decompression_time,
                            'efficiency_score': efficiency,
                            'integrity_ok': integrity_ok
                        }
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Benchmark échec {algorithm.value}({level}): {e}")
        
        return results
    
    async def get_compression_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics compression détaillées**"""
        
        # Distribution algorithmes
        algo_usage = defaultdict(int)
        pattern_distribution = defaultdict(int)
        
        for record in self.compression_history:
            algo_usage[record['algorithm']] += 1
            pattern_distribution[record['pattern']] += 1
        
        # Performance moyenne
        if self.compression_history:
            avg_ratio = np.mean([r['ratio'] for r in self.compression_history])
            avg_time = np.mean([r['time_ms'] for r in self.compression_history])
            avg_efficiency = np.mean([r['efficiency'] for r in self.compression_history])
        else:
            avg_ratio = avg_time = avg_efficiency = 0
        
        # Top algorithmes par efficacité
        algo_efficiency = defaultdict(list)
        for record in self.compression_history:
            algo_efficiency[record['algorithm']].append(record['efficiency'])
        
        top_algorithms = {}
        for algo, efficiencies in algo_efficiency.items():
            if efficiencies:
                top_algorithms[algo] = {
                    'avg_efficiency': np.mean(efficiencies),
                    'usage_count': len(efficiencies)
                }
        
        return {
            'global_metrics': {
                'total_compressions': len(self.compression_history),
                'average_compression_ratio': avg_ratio,
                'average_compression_time_ms': avg_time,
                'average_efficiency_score': avg_efficiency,
                'unique_algorithms_used': len(algo_usage),
                'unique_patterns_detected': len(pattern_distribution)
            },
            'algorithm_usage': dict(algo_usage),
            'pattern_distribution': dict(pattern_distribution),
            'algorithm_performance': top_algorithms,
            'profiles': {
                key: {
                    'algorithm': profile.algorithm.value,
                    'level': profile.level,
                    'use_count': profile.use_count,
                    'avg_ratio': profile.avg_ratio,
                    'avg_time_ms': profile.avg_time_ms,
                    'success_rate': profile.success_rate
                }
                for key, profile in self.profiles.items()
                if profile.use_count > 0
            },
            'recent_compressions': list(self.compression_history)[-20:],
            'recommendations_cached': len(self.recommendations_cache),
            'configuration': {
                'compression_threshold': self.config.get('compression_threshold'),
                'max_compression_time_ms': self.config.get('max_compression_time_ms'),
                'target_ratio': self.config.get('target_ratio'),
                'adaptive_level': self.config.get('enable_adaptive_level'),
                'pattern_detection': self.config.get('pattern_detection')
            }
        }

# Factory function
def create_compression_optimizer(config: Optional[Dict[str, Any]] = None):
    """**Backend Senior**: Factory création optimiseur compression"""
    return CompressionOptimizer(config)

if __name__ == "__main__":
    async def demo():
        """Démonstration Compression Optimizer"""
        
        # Création optimizer
        optimizer = create_compression_optimizer()
        
        # Test données variées
        test_data = [
            b'{"name": "Alice", "age": 30}' * 100,  # JSON répétitif
            b'A' * 1000,  # Données très répétitives
            open(__file__, 'rb').read(),  # Code source (texte structuré)
            bytes(range(256)) * 10,  # Données binaires pattern
        ]
        
        print("⚡ Test compression automatique...")
        
        for i, data in enumerate(test_data):
            print(f"\n--- Test {i+1}: {len(data)} bytes ---")
            
            # Compression optimale
            compressed, metrics = await optimizer.compress_optimal(data)
            
            print(f"Algorithme: {metrics.algorithm}({metrics.level})")
            print(f"Pattern: {metrics.pattern}")
            print(f"Ratio: {metrics.compression_ratio:.2f}x")
            print(f"Temps: {metrics.compression_time_ms:.2f}ms")
            print(f"Efficacité: {metrics.efficiency_score:.3f}")
            
            # Test décompression
            decompressed = await optimizer.decompress(compressed, metrics.algorithm)
            print(f"Intégrité: {'✅' if decompressed == data else '❌'}")
        
        # Analytics
        analytics = await optimizer.get_compression_analytics()
        print(f"\n📊 Analytics: {analytics['global_metrics']}")
    
    asyncio.run(demo())