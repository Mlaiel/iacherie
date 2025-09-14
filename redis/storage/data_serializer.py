#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Serialization Engine - Moteur Sérialisation Multi-Format Enterprise
======================================================================

Moteur enterprise de sérialisation multi-format avec optimisation automatique,
compression intelligente et support formats avancés pour cache haute performance.

**Rôles Experts:**
- **Backend Senior**: Architecture sérialisation haute performance multi-format
- **DBA**: Optimisation stockage, indexation, compression données
- **Lead Dev IA**: Optimisation intelligente format et compression
- **Sécurité**: Chiffrement sérialisation, validation intégrité données

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import pickle
import msgpack
import zlib
import lz4.frame
import brotli
from typing import Dict, Any, Optional, List, Union, Tuple, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
import aioredis
from collections import defaultdict, deque
import hashlib
import base64
import struct
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
import orjson  # Fast JSON serialization
import cbor2  # Concise Binary Object Representation
import avro.schema
import avro.io

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerializationFormat(Enum):
    """Formats de sérialisation supportés"""
    JSON = "json"
    ORJSON = "orjson"  # JSON optimisé
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    CBOR = "cbor"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    CUSTOM_BINARY = "custom_binary"
    XML = "xml"
    YAML = "yaml"

class CompressionType(Enum):
    """Types de compression"""
    NONE = "none"
    ZLIB = "zlib"
    LZ4 = "lz4"
    BROTLI = "brotli"
    GZIP = "gzip"
    ZSTD = "zstd"

class SerializationStrategy(Enum):
    """Stratégies de sérialisation"""
    SPEED_OPTIMIZED = "speed_optimized"  # Vitesse maximale
    SIZE_OPTIMIZED = "size_optimized"  # Taille minimale
    BALANCED = "balanced"  # Équilibré
    SECURE = "secure"  # Sécurité maximale
    ADAPTIVE = "adaptive"  # Adaptatif intelligent

@dataclass
class SerializationMetrics:
    """Métriques sérialisation"""
    format_name: str
    compression_type: str
    original_size: int
    serialized_size: int
    compressed_size: int
    serialization_time_ms: float
    compression_time_ms: float
    deserialization_time_ms: float
    decompression_time_ms: float
    compression_ratio: float
    total_time_ms: float

@dataclass
class SerializationProfile:
    """Profil performance format"""
    format: SerializationFormat
    compression: CompressionType
    avg_serialization_time: float = 0.0
    avg_compression_ratio: float = 0.0
    avg_size_reduction: float = 0.0
    success_rate: float = 1.0
    data_type_compatibility: Dict[str, float] = field(default_factory=dict)
    use_count: int = 0

class SerializationEngine:
    """
    🔄 Moteur Sérialisation Multi-Format Enterprise
    
    **Backend Senior**: Architecture sérialisation haute performance
    **DBA**: Optimisation stockage et compression intelligente
    **Lead Dev IA**: Sélection automatique format optimal via ML
    **Sécurité**: Chiffrement et validation intégrité données
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Profiles de performance par format
        self.format_profiles: Dict[str, SerializationProfile] = {}
        self._initialize_format_profiles()
        
        # Métriques et historique
        self.serialization_history: deque = deque(maxlen=10000)
        self.performance_stats: Dict[str, List[float]] = defaultdict(list)
        
        # Cache format optimal par type de données
        self.optimal_format_cache: Dict[str, Tuple[SerializationFormat, CompressionType]] = {}
        
        # Chiffrement si activé
        self.encryption_key = None
        self.fernet = None
        if self.config.get('enable_encryption'):
            self._initialize_encryption()
        
        # Registre sérialiseurs personnalisés
        self.custom_serializers: Dict[Type, callable] = {}
        self.custom_deserializers: Dict[Type, callable] = {}
        
        # Schema registry pour formats typés
        self.schema_registry: Dict[str, Any] = {}
        
        logger.info("🔄 Serialization Engine initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration par défaut optimisée"""
        return {
            'default_format': SerializationFormat.ORJSON.value,
            'default_compression': CompressionType.LZ4.value,
            'default_strategy': SerializationStrategy.BALANCED.value,
            'enable_encryption': False,
            'enable_compression': True,
            'enable_adaptive_selection': True,
            'compression_threshold': 1024,  # Compress si > 1KB
            'max_serialization_time_ms': 1000,
            'preferred_formats_by_type': {
                'dict': 'orjson',
                'list': 'orjson',
                'str': 'json',
                'bytes': 'custom_binary',
                'numpy.ndarray': 'pickle',
                'pandas.DataFrame': 'pickle',
                'datetime': 'orjson'
            },
            'compression_levels': {
                'zlib': 6,
                'brotli': 4,
                'lz4': 0  # LZ4 n'a pas de niveaux
            },
            'enable_integrity_check': True,
            'cache_optimal_formats': True
        }
    
    def _initialize_format_profiles(self):
        """**Backend Senior**: Initialisation profils formats"""
        formats = [
            (SerializationFormat.JSON, CompressionType.NONE),
            (SerializationFormat.ORJSON, CompressionType.NONE),
            (SerializationFormat.ORJSON, CompressionType.LZ4),
            (SerializationFormat.PICKLE, CompressionType.NONE),
            (SerializationFormat.PICKLE, CompressionType.ZLIB),
            (SerializationFormat.MSGPACK, CompressionType.NONE),
            (SerializationFormat.MSGPACK, CompressionType.LZ4),
            (SerializationFormat.CBOR, CompressionType.NONE),
            (SerializationFormat.CBOR, CompressionType.BROTLI)
        ]
        
        for fmt, comp in formats:
            profile_key = f"{fmt.value}_{comp.value}"
            self.format_profiles[profile_key] = SerializationProfile(
                format=fmt,
                compression=comp,
                data_type_compatibility=self._get_initial_compatibility(fmt)
            )
    
    def _get_initial_compatibility(self, format: SerializationFormat) -> Dict[str, float]:
        """**Backend Senior**: Compatibilité initiale formats"""
        
        compatibility = {
            SerializationFormat.JSON: {
                'dict': 1.0, 'list': 1.0, 'str': 1.0, 'int': 1.0, 'float': 1.0,
                'bool': 1.0, 'NoneType': 1.0, 'bytes': 0.3, 'datetime': 0.7
            },
            SerializationFormat.ORJSON: {
                'dict': 1.0, 'list': 1.0, 'str': 1.0, 'int': 1.0, 'float': 1.0,
                'bool': 1.0, 'NoneType': 1.0, 'bytes': 0.8, 'datetime': 0.9
            },
            SerializationFormat.PICKLE: {
                'dict': 1.0, 'list': 1.0, 'str': 1.0, 'int': 1.0, 'float': 1.0,
                'bool': 1.0, 'NoneType': 1.0, 'bytes': 1.0, 'datetime': 1.0,
                'numpy.ndarray': 1.0, 'pandas.DataFrame': 1.0, 'custom_object': 1.0
            },
            SerializationFormat.MSGPACK: {
                'dict': 1.0, 'list': 1.0, 'str': 1.0, 'int': 1.0, 'float': 1.0,
                'bool': 1.0, 'NoneType': 1.0, 'bytes': 1.0, 'datetime': 0.8
            },
            SerializationFormat.CBOR: {
                'dict': 1.0, 'list': 1.0, 'str': 1.0, 'int': 1.0, 'float': 1.0,
                'bool': 1.0, 'NoneType': 1.0, 'bytes': 1.0, 'datetime': 0.9
            }
        }
        
        return compatibility.get(format, {})
    
    def _initialize_encryption(self):
        """**Sécurité**: Initialisation chiffrement sécurisé"""
        try:
            # En production, utiliser key management service
            key_material = self.config.get('encryption_key', 'default_key_ainflue_2025')
            key_hash = hashlib.sha256(key_material.encode()).digest()
            self.encryption_key = base64.urlsafe_b64encode(key_hash)
            self.fernet = Fernet(self.encryption_key)
            
            logger.info("🔐 Chiffrement sérialisation activé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation chiffrement: {e}")
            self.encryption_key = None
            self.fernet = None
    
    async def serialize(
        self,
        data: Any,
        format: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        strategy: Optional[SerializationStrategy] = None,
        encrypt: bool = False
    ) -> Tuple[bytes, SerializationMetrics]:
        """**Backend Senior**: Sérialisation haute performance avec optimisation**"""
        
        start_time = time.time()
        
        try:
            # Détection type données
            data_type = self._detect_data_type(data)
            original_size = self._estimate_data_size(data)
            
            # Sélection format optimal si non spécifié
            if not format or not compression:
                optimal_format, optimal_compression = await self._select_optimal_format(
                    data, data_type, strategy
                )
                format = format or optimal_format
                compression = compression or optimal_compression
            
            # Sérialisation
            serialization_start = time.time()
            serialized_data = await self._serialize_data(data, format)
            serialization_time = (time.time() - serialization_start) * 1000
            
            serialized_size = len(serialized_data)
            
            # Compression si activée et utile
            compression_start = time.time()
            if (self.config.get('enable_compression') and 
                compression != CompressionType.NONE and
                serialized_size > self.config.get('compression_threshold', 1024)):
                
                compressed_data = await self._compress_data(serialized_data, compression)
                compression_time = (time.time() - compression_start) * 1000
                compressed_size = len(compressed_data)
            else:
                compressed_data = serialized_data
                compression_time = 0
                compressed_size = serialized_size
            
            # Chiffrement si demandé
            if encrypt and self.fernet:
                compressed_data = self.fernet.encrypt(compressed_data)
            
            # Ajout métadonnées
            final_data = await self._add_metadata(
                compressed_data, format, compression, encrypt, data_type
            )
            
            # Calcul métriques
            total_time = (time.time() - start_time) * 1000
            compression_ratio = original_size / max(1, len(final_data))
            
            metrics = SerializationMetrics(
                format_name=format.value,
                compression_type=compression.value,
                original_size=original_size,
                serialized_size=serialized_size,
                compressed_size=compressed_size,
                serialization_time_ms=serialization_time,
                compression_time_ms=compression_time,
                deserialization_time_ms=0,  # Sera rempli au désérialization
                decompression_time_ms=0,
                compression_ratio=compression_ratio,
                total_time_ms=total_time
            )
            
            # Mise à jour profils performance
            await self._update_performance_profile(format, compression, metrics, data_type)
            
            # Historique
            self.serialization_history.append({
                'timestamp': time.time(),
                'format': format.value,
                'compression': compression.value,
                'data_type': data_type,
                'original_size': original_size,
                'final_size': len(final_data),
                'compression_ratio': compression_ratio,
                'total_time_ms': total_time
            })
            
            logger.debug(f"✅ Sérialisé: {format.value}/{compression.value} - {compression_ratio:.2f}x compression")
            
            return final_data, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur sérialisation: {e}")
            raise
    
    async def deserialize(self, data: bytes) -> Tuple[Any, SerializationMetrics]:
        """**Backend Senior**: Désérialisation haute performance**"""
        
        start_time = time.time()
        
        try:
            # Extraction métadonnées
            payload, metadata = await self._extract_metadata(data)
            
            format = SerializationFormat(metadata['format'])
            compression = CompressionType(metadata['compression'])
            encrypted = metadata.get('encrypted', False)
            data_type = metadata.get('data_type', 'unknown')
            
            # Déchiffrement si nécessaire
            if encrypted and self.fernet:
                payload = self.fernet.decrypt(payload)
            
            # Décompression
            decompression_start = time.time()
            if compression != CompressionType.NONE:
                decompressed_data = await self._decompress_data(payload, compression)
                decompression_time = (time.time() - decompression_start) * 1000
            else:
                decompressed_data = payload
                decompression_time = 0
            
            # Désérialisation
            deserialization_start = time.time()
            original_data = await self._deserialize_data(decompressed_data, format)
            deserialization_time = (time.time() - deserialization_start) * 1000
            
            # Métriques
            total_time = (time.time() - start_time) * 1000
            
            metrics = SerializationMetrics(
                format_name=format.value,
                compression_type=compression.value,
                original_size=len(data),
                serialized_size=len(decompressed_data),
                compressed_size=len(payload),
                serialization_time_ms=0,  # N/A pour désérialisation
                compression_time_ms=0,
                deserialization_time_ms=deserialization_time,
                decompression_time_ms=decompression_time,
                compression_ratio=len(data) / max(1, len(decompressed_data)),
                total_time_ms=total_time
            )
            
            logger.debug(f"✅ Désérialisé: {format.value}/{compression.value}")
            
            return original_data, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur désérialisation: {e}")
            raise
    
    def _detect_data_type(self, data: Any) -> str:
        """**Lead Dev IA**: Détection intelligente type données"""
        
        data_type = type(data).__name__
        
        # Types spéciaux
        if hasattr(data, '__module__'):
            if data.__module__ == 'numpy':
                data_type = f"numpy.{data_type}"
            elif data.__module__ == 'pandas.core.frame':
                data_type = 'pandas.DataFrame'
            elif data.__module__ == 'pandas.core.series':
                data_type = 'pandas.Series'
        
        # Types composites
        if isinstance(data, dict):
            if all(isinstance(k, str) for k in data.keys()):
                data_type = 'dict_str_keys'
            else:
                data_type = 'dict_mixed_keys'
        elif isinstance(data, list):
            if data and all(isinstance(x, type(data[0])) for x in data):
                data_type = f"list_{type(data[0]).__name__}"
            else:
                data_type = 'list_mixed'
        
        return data_type
    
    def _estimate_data_size(self, data: Any) -> int:
        """**DBA**: Estimation taille données optimisée"""
        
        try:
            # Estimation rapide sans sérialisation complète
            if isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, (int, float, bool)):
                return 8  # Estimation
            elif isinstance(data, dict):
                return sum(len(str(k)) + self._estimate_data_size(v) for k, v in data.items())
            elif isinstance(data, list):
                return sum(self._estimate_data_size(item) for item in data)
            else:
                # Fallback: pickle size estimation
                return len(pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))
                
        except:
            return 1024  # Estimation par défaut
    
    async def _select_optimal_format(
        self,
        data: Any,
        data_type: str,
        strategy: Optional[SerializationStrategy]
    ) -> Tuple[SerializationFormat, CompressionType]:
        """**Lead Dev IA**: Sélection format optimal intelligent**"""
        
        strategy = strategy or SerializationStrategy(self.config.get('default_strategy', 'balanced'))
        
        # Cache lookup
        if self.config.get('cache_optimal_formats'):
            cache_key = f"{data_type}_{strategy.value}"
            if cache_key in self.optimal_format_cache:
                return self.optimal_format_cache[cache_key]
        
        # Sélection basée sur stratégie
        if strategy == SerializationStrategy.SPEED_OPTIMIZED:
            optimal_format, optimal_compression = await self._select_fastest_format(data_type)
        elif strategy == SerializationStrategy.SIZE_OPTIMIZED:
            optimal_format, optimal_compression = await self._select_smallest_format(data_type)
        elif strategy == SerializationStrategy.SECURE:
            optimal_format, optimal_compression = await self._select_secure_format(data_type)
        elif strategy == SerializationStrategy.ADAPTIVE:
            optimal_format, optimal_compression = await self._select_adaptive_format(data, data_type)
        else:  # BALANCED
            optimal_format, optimal_compression = await self._select_balanced_format(data_type)
        
        # Cache du résultat
        if self.config.get('cache_optimal_formats'):
            self.optimal_format_cache[cache_key] = (optimal_format, optimal_compression)
        
        return optimal_format, optimal_compression
    
    async def _select_fastest_format(self, data_type: str) -> Tuple[SerializationFormat, CompressionType]:
        """**Backend Senior**: Sélection format le plus rapide"""
        
        # Priorité vitesse: ORJSON > JSON > MSGPACK
        speed_rankings = [
            (SerializationFormat.ORJSON, CompressionType.NONE),
            (SerializationFormat.JSON, CompressionType.NONE),
            (SerializationFormat.MSGPACK, CompressionType.NONE),
            (SerializationFormat.PICKLE, CompressionType.NONE)
        ]
        
        # Vérification compatibilité
        for fmt, comp in speed_rankings:
            profile_key = f"{fmt.value}_{comp.value}"
            if profile_key in self.format_profiles:
                profile = self.format_profiles[profile_key]
                compatibility = profile.data_type_compatibility.get(data_type, 0.5)
                if compatibility > 0.7:
                    return fmt, comp
        
        return SerializationFormat.PICKLE, CompressionType.NONE
    
    async def _select_smallest_format(self, data_type: str) -> Tuple[SerializationFormat, CompressionType]:
        """**DBA**: Sélection format plus compact"""
        
        # Priorité taille: MSGPACK+BROTLI > CBOR+LZ4 > PICKLE+ZLIB
        size_rankings = [
            (SerializationFormat.MSGPACK, CompressionType.BROTLI),
            (SerializationFormat.CBOR, CompressionType.LZ4),
            (SerializationFormat.PICKLE, CompressionType.ZLIB),
            (SerializationFormat.ORJSON, CompressionType.LZ4)
        ]
        
        for fmt, comp in size_rankings:
            profile_key = f"{fmt.value}_{comp.value}"
            if profile_key in self.format_profiles:
                profile = self.format_profiles[profile_key]
                compatibility = profile.data_type_compatibility.get(data_type, 0.5)
                if compatibility > 0.7:
                    return fmt, comp
        
        return SerializationFormat.MSGPACK, CompressionType.LZ4
    
    async def _select_secure_format(self, data_type: str) -> Tuple[SerializationFormat, CompressionType]:
        """**Sécurité**: Sélection format sécurisé"""
        
        # Priorité sécurité: formats avec validation + compression
        secure_rankings = [
            (SerializationFormat.CBOR, CompressionType.BROTLI),
            (SerializationFormat.MSGPACK, CompressionType.ZLIB),
            (SerializationFormat.ORJSON, CompressionType.LZ4)
        ]
        
        for fmt, comp in secure_rankings:
            profile_key = f"{fmt.value}_{comp.value}"
            if profile_key in self.format_profiles:
                profile = self.format_profiles[profile_key]
                compatibility = profile.data_type_compatibility.get(data_type, 0.5)
                if compatibility > 0.8:
                    return fmt, comp
        
        return SerializationFormat.CBOR, CompressionType.BROTLI
    
    async def _select_adaptive_format(self, data: Any, data_type: str) -> Tuple[SerializationFormat, CompressionType]:
        """**Lead Dev IA**: Sélection adaptative intelligente basée historique**"""
        
        # Analyse historique performance
        best_profile = None
        best_score = 0
        
        for profile_key, profile in self.format_profiles.items():
            # Score basé sur performance historique
            compatibility = profile.data_type_compatibility.get(data_type, 0.5)
            
            if compatibility < 0.7:
                continue
            
            # Score composite: vitesse + compression + fiabilité
            speed_score = 1.0 / max(0.1, profile.avg_serialization_time) if profile.avg_serialization_time > 0 else 1.0
            compression_score = profile.avg_compression_ratio
            reliability_score = profile.success_rate
            
            composite_score = (
                speed_score * 0.4 + 
                compression_score * 0.3 + 
                reliability_score * 0.2 + 
                compatibility * 0.1
            )
            
            if composite_score > best_score:
                best_score = composite_score
                best_profile = profile
        
        if best_profile:
            return best_profile.format, best_profile.compression
        
        # Fallback
        return SerializationFormat.ORJSON, CompressionType.LZ4
    
    async def _select_balanced_format(self, data_type: str) -> Tuple[SerializationFormat, CompressionType]:
        """**Backend Senior**: Sélection format équilibré**"""
        
        # Préférences par type de données
        preferences = self.config.get('preferred_formats_by_type', {})
        
        if data_type in preferences:
            preferred_format = SerializationFormat(preferences[data_type])
            # Compression par défaut selon format
            if preferred_format in [SerializationFormat.JSON, SerializationFormat.ORJSON]:
                return preferred_format, CompressionType.LZ4
            elif preferred_format == SerializationFormat.MSGPACK:
                return preferred_format, CompressionType.LZ4
            elif preferred_format == SerializationFormat.PICKLE:
                return preferred_format, CompressionType.ZLIB
            else:
                return preferred_format, CompressionType.NONE
        
        # Défaut équilibré
        return SerializationFormat.ORJSON, CompressionType.LZ4
    
    async def _serialize_data(self, data: Any, format: SerializationFormat) -> bytes:
        """**Backend Senior**: Sérialisation selon format**"""
        
        try:
            if format == SerializationFormat.JSON:
                return json.dumps(data, ensure_ascii=False, default=self._json_serializer).encode('utf-8')
            
            elif format == SerializationFormat.ORJSON:
                return orjson.dumps(data, default=self._orjson_serializer)
            
            elif format == SerializationFormat.PICKLE:
                return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            
            elif format == SerializationFormat.MSGPACK:
                return msgpack.packb(data, default=self._msgpack_serializer, use_bin_type=True)
            
            elif format == SerializationFormat.CBOR:
                return cbor2.dumps(data, default=self._cbor_serializer)
            
            elif format == SerializationFormat.YAML:
                return yaml.dump(data, default_flow_style=False).encode('utf-8')
            
            elif format == SerializationFormat.CUSTOM_BINARY:
                return await self._custom_binary_serialize(data)
            
            else:
                raise ValueError(f"Format de sérialisation non supporté: {format}")
                
        except Exception as e:
            logger.error(f"❌ Erreur sérialisation {format.value}: {e}")
            raise
    
    async def _deserialize_data(self, data: bytes, format: SerializationFormat) -> Any:
        """**Backend Senior**: Désérialisation selon format**"""
        
        try:
            if format == SerializationFormat.JSON:
                return json.loads(data.decode('utf-8'))
            
            elif format == SerializationFormat.ORJSON:
                return orjson.loads(data)
            
            elif format == SerializationFormat.PICKLE:
                return pickle.loads(data)
            
            elif format == SerializationFormat.MSGPACK:
                return msgpack.unpackb(data, raw=False, strict_map_key=False)
            
            elif format == SerializationFormat.CBOR:
                return cbor2.loads(data)
            
            elif format == SerializationFormat.YAML:
                return yaml.safe_load(data.decode('utf-8'))
            
            elif format == SerializationFormat.CUSTOM_BINARY:
                return await self._custom_binary_deserialize(data)
            
            else:
                raise ValueError(f"Format de désérialisation non supporté: {format}")
                
        except Exception as e:
            logger.error(f"❌ Erreur désérialisation {format.value}: {e}")
            raise
    
    def _json_serializer(self, obj):
        """**Backend Senior**: Sérialiseur JSON personnalisé**"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode('ascii')
        raise TypeError(f"Object de type {type(obj)} non sérialisable JSON")
    
    def _orjson_serializer(self, obj):
        """**Backend Senior**: Sérialiseur ORJSON personnalisé**"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        raise TypeError(f"Object de type {type(obj)} non sérialisable ORJSON")
    
    def _msgpack_serializer(self, obj):
        """**Backend Senior**: Sérialiseur MessagePack personnalisé**"""
        if isinstance(obj, datetime):
            return {'__datetime__': obj.isoformat()}
        elif isinstance(obj, np.ndarray):
            return {'__numpy__': obj.tolist(), '__dtype__': str(obj.dtype)}
        return obj
    
    def _cbor_serializer(self, encoder, obj):
        """**Backend Senior**: Sérialiseur CBOR personnalisé**"""
        if isinstance(obj, datetime):
            encoder.encode({'__datetime__': obj.isoformat()})
        elif isinstance(obj, np.ndarray):
            encoder.encode({'__numpy__': obj.tolist(), '__dtype__': str(obj.dtype)})
        else:
            return obj
    
    async def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """**DBA**: Compression optimisée**"""
        
        try:
            if compression == CompressionType.ZLIB:
                level = self.config.get('compression_levels', {}).get('zlib', 6)
                return zlib.compress(data, level)
            
            elif compression == CompressionType.LZ4:
                return lz4.frame.compress(data)
            
            elif compression == CompressionType.BROTLI:
                level = self.config.get('compression_levels', {}).get('brotli', 4)
                return brotli.compress(data, quality=level)
            
            elif compression == CompressionType.GZIP:
                import gzip
                return gzip.compress(data)
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"❌ Erreur compression {compression.value}: {e}")
            return data  # Retour données non compressées en cas d'erreur
    
    async def _decompress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """**DBA**: Décompression optimisée**"""
        
        try:
            if compression == CompressionType.ZLIB:
                return zlib.decompress(data)
            
            elif compression == CompressionType.LZ4:
                return lz4.frame.decompress(data)
            
            elif compression == CompressionType.BROTLI:
                return brotli.decompress(data)
            
            elif compression == CompressionType.GZIP:
                import gzip
                return gzip.decompress(data)
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"❌ Erreur décompression {compression.value}: {e}")
            raise
    
    async def _add_metadata(
        self,
        data: bytes,
        format: SerializationFormat,
        compression: CompressionType,
        encrypted: bool,
        data_type: str
    ) -> bytes:
        """**Backend Senior**: Ajout métadonnées sérialisation**"""
        
        metadata = {
            'format': format.value,
            'compression': compression.value,
            'encrypted': encrypted,
            'data_type': data_type,
            'version': 1,
            'timestamp': time.time()
        }
        
        # Checksum pour intégrité si activé
        if self.config.get('enable_integrity_check'):
            metadata['checksum'] = hashlib.sha256(data).hexdigest()
        
        # Sérialisation métadonnées en JSON compact
        metadata_bytes = orjson.dumps(metadata)
        metadata_length = len(metadata_bytes)
        
        # Format: [metadata_length(4 bytes)][metadata][data]
        return struct.pack('!I', metadata_length) + metadata_bytes + data
    
    async def _extract_metadata(self, data: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """**Backend Senior**: Extraction métadonnées**"""
        
        try:
            # Lecture longueur métadonnées
            if len(data) < 4:
                raise ValueError("Données trop courtes pour contenir métadonnées")
            
            metadata_length = struct.unpack('!I', data[:4])[0]
            
            if len(data) < 4 + metadata_length:
                raise ValueError("Métadonnées tronquées")
            
            # Extraction métadonnées
            metadata_bytes = data[4:4 + metadata_length]
            payload = data[4 + metadata_length:]
            
            metadata = orjson.loads(metadata_bytes)
            
            # Vérification intégrité si activé
            if (self.config.get('enable_integrity_check') and 
                'checksum' in metadata):
                
                expected_checksum = metadata['checksum']
                actual_checksum = hashlib.sha256(payload).hexdigest()
                
                if expected_checksum != actual_checksum:
                    raise ValueError("Échec vérification intégrité données")
            
            return payload, metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction métadonnées: {e}")
            raise
    
    async def _custom_binary_serialize(self, data: Any) -> bytes:
        """**Backend Senior**: Sérialisation binaire personnalisée**"""
        
        # Implémentation format binaire optimisé pour types spécifiques
        if isinstance(data, np.ndarray):
            # Format: [type_flag][shape][dtype][data]
            shape_bytes = pickle.dumps(data.shape)
            dtype_bytes = str(data.dtype).encode('utf-8')
            
            header = struct.pack('!B', 1)  # type flag numpy
            header += struct.pack('!I', len(shape_bytes)) + shape_bytes
            header += struct.pack('!I', len(dtype_bytes)) + dtype_bytes
            
            return header + data.tobytes()
        
        else:
            # Fallback vers pickle
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    async def _custom_binary_deserialize(self, data: bytes) -> Any:
        """**Backend Senior**: Désérialisation binaire personnalisée**"""
        
        try:
            if len(data) < 1:
                raise ValueError("Données binaires vides")
            
            type_flag = struct.unpack('!B', data[:1])[0]
            
            if type_flag == 1:  # numpy array
                offset = 1
                
                # Lecture shape
                shape_length = struct.unpack('!I', data[offset:offset+4])[0]
                offset += 4
                shape = pickle.loads(data[offset:offset+shape_length])
                offset += shape_length
                
                # Lecture dtype
                dtype_length = struct.unpack('!I', data[offset:offset+4])[0]
                offset += 4
                dtype_str = data[offset:offset+dtype_length].decode('utf-8')
                offset += dtype_length
                
                # Reconstruction array
                array_data = data[offset:]
                return np.frombuffer(array_data, dtype=dtype_str).reshape(shape)
            
            else:
                # Fallback pickle
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"❌ Erreur désérialisation binaire: {e}")
            raise
    
    async def _update_performance_profile(
        self,
        format: SerializationFormat,
        compression: CompressionType,
        metrics: SerializationMetrics,
        data_type: str
    ):
        """**Lead Dev IA**: Mise à jour profil performance**"""
        
        profile_key = f"{format.value}_{compression.value}"
        
        if profile_key not in self.format_profiles:
            return
        
        profile = self.format_profiles[profile_key]
        profile.use_count += 1
        
        # Mise à jour moyennes mobiles
        alpha = 0.1  # Facteur apprentissage
        
        if profile.avg_serialization_time > 0:
            profile.avg_serialization_time = (
                profile.avg_serialization_time * (1 - alpha) +
                metrics.serialization_time_ms * alpha
            )
        else:
            profile.avg_serialization_time = metrics.serialization_time_ms
        
        if profile.avg_compression_ratio > 0:
            profile.avg_compression_ratio = (
                profile.avg_compression_ratio * (1 - alpha) +
                metrics.compression_ratio * alpha
            )
        else:
            profile.avg_compression_ratio = metrics.compression_ratio
        
        # Mise à jour compatibilité type
        if data_type in profile.data_type_compatibility:
            current_compat = profile.data_type_compatibility[data_type]
            profile.data_type_compatibility[data_type] = min(1.0, current_compat + 0.1)
        else:
            profile.data_type_compatibility[data_type] = 0.8
    
    def register_custom_serializer(self, data_type: Type, serializer: callable, deserializer: callable):
        """**Backend Senior**: Enregistrement sérialiseur personnalisé**"""
        self.custom_serializers[data_type] = serializer
        self.custom_deserializers[data_type] = deserializer
        logger.info(f"📝 Sérialiseur personnalisé enregistré pour {data_type}")
    
    async def benchmark_formats(
        self,
        test_data: List[Any],
        formats: Optional[List[SerializationFormat]] = None,
        compressions: Optional[List[CompressionType]] = None
    ) -> Dict[str, Any]:
        """**DevOps**: Benchmark performance formats**"""
        
        formats = formats or [
            SerializationFormat.JSON,
            SerializationFormat.ORJSON,
            SerializationFormat.PICKLE,
            SerializationFormat.MSGPACK,
            SerializationFormat.CBOR
        ]
        
        compressions = compressions or [
            CompressionType.NONE,
            CompressionType.LZ4,
            CompressionType.ZLIB,
            CompressionType.BROTLI
        ]
        
        results = {}
        
        for data in test_data:
            data_type = self._detect_data_type(data)
            
            for format in formats:
                for compression in compressions:
                    try:
                        # Test sérialisation
                        serialized, metrics = await self.serialize(
                            data, format, compression
                        )
                        
                        # Test désérialisation
                        deserialized, deser_metrics = await self.deserialize(serialized)
                        
                        # Vérification intégrité
                        integrity_ok = str(data) == str(deserialized)  # Comparaison simple
                        
                        key = f"{format.value}_{compression.value}_{data_type}"
                        results[key] = {
                            'format': format.value,
                            'compression': compression.value,
                            'data_type': data_type,
                            'serialization_time_ms': metrics.serialization_time_ms,
                            'deserialization_time_ms': deser_metrics.deserialization_time_ms,
                            'total_time_ms': metrics.total_time_ms + deser_metrics.total_time_ms,
                            'compression_ratio': metrics.compression_ratio,
                            'size_reduction_pct': (1 - 1/metrics.compression_ratio) * 100,
                            'integrity_ok': integrity_ok
                        }
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Benchmark échec {format.value}/{compression.value}: {e}")
        
        return results
    
    async def get_serialization_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics sérialisation détaillées**"""
        
        # Distribution formats utilisés
        format_usage = defaultdict(int)
        compression_usage = defaultdict(int)
        
        for record in self.serialization_history:
            format_usage[record['format']] += 1
            compression_usage[record['compression']] += 1
        
        # Performance moyenne par format
        format_performance = {}
        for format_name in format_usage.keys():
            records = [r for r in self.serialization_history if r['format'] == format_name]
            if records:
                avg_time = sum(r['total_time_ms'] for r in records) / len(records)
                avg_ratio = sum(r['compression_ratio'] for r in records) / len(records)
                format_performance[format_name] = {
                    'average_time_ms': avg_time,
                    'average_compression_ratio': avg_ratio,
                    'usage_count': len(records)
                }
        
        # Top types de données
        data_type_stats = defaultdict(lambda: {'count': 0, 'total_size': 0})
        for record in self.serialization_history:
            data_type = record.get('data_type', 'unknown')
            data_type_stats[data_type]['count'] += 1
            data_type_stats[data_type]['total_size'] += record['original_size']
        
        return {
            'global_metrics': {
                'total_serializations': len(self.serialization_history),
                'unique_formats_used': len(format_usage),
                'unique_compressions_used': len(compression_usage),
                'average_compression_ratio': np.mean([r['compression_ratio'] for r in self.serialization_history]) if self.serialization_history else 0
            },
            'format_usage': dict(format_usage),
            'compression_usage': dict(compression_usage),
            'format_performance': format_performance,
            'data_type_statistics': dict(data_type_stats),
            'recent_serializations': list(self.serialization_history)[-20:],
            'format_profiles': {
                key: {
                    'format': profile.format.value,
                    'compression': profile.compression.value,
                    'use_count': profile.use_count,
                    'avg_serialization_time': profile.avg_serialization_time,
                    'avg_compression_ratio': profile.avg_compression_ratio,
                    'success_rate': profile.success_rate
                }
                for key, profile in self.format_profiles.items()
            },
            'configuration': {
                'default_format': self.config.get('default_format'),
                'default_compression': self.config.get('default_compression'),
                'encryption_enabled': self.config.get('enable_encryption'),
                'adaptive_selection': self.config.get('enable_adaptive_selection'),
                'compression_threshold': self.config.get('compression_threshold')
            }
        }

# Factory function
async def create_serialization_engine(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**Backend Senior**: Factory création moteur sérialisation**"""
    return SerializationEngine(redis_pool, config)

if __name__ == "__main__":
    async def demo():
        """Démonstration Serialization Engine"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                return AsyncMock()
        
        # Création engine
        engine = await create_serialization_engine(MockRedisPool())
        
        # Test données variées
        test_data = [
            {'name': 'Alice', 'age': 30, 'skills': ['Python', 'Redis']},
            [1, 2, 3, 4, 5] * 100,  # Liste grande
            'Une chaîne de caractères assez longue pour tester la compression',
            np.random.rand(100, 100),  # Array NumPy
            datetime.now()
        ]
        
        print("🔄 Test sérialisation multi-format...")
        
        for i, data in enumerate(test_data):
            print(f"\n--- Test {i+1}: {type(data).__name__} ---")
            
            # Test avec format adaptatif
            serialized, metrics = await engine.serialize(
                data, 
                strategy=SerializationStrategy.ADAPTIVE
            )
            
            print(f"Format: {metrics.format_name}/{metrics.compression_type}")
            print(f"Compression: {metrics.compression_ratio:.2f}x")
            print(f"Temps: {metrics.total_time_ms:.2f}ms")
            
            # Test désérialisation
            deserialized, deser_metrics = await engine.deserialize(serialized)
            print(f"Désérialisation: {deser_metrics.total_time_ms:.2f}ms")
            
            # Vérification intégrité
            print(f"Intégrité: {'✅' if str(data) == str(deserialized) else '❌'}")
        
        # Analytics
        analytics = await engine.get_serialization_analytics()
        print(f"\n📊 Analytics: {analytics['global_metrics']}")
    
    asyncio.run(demo())