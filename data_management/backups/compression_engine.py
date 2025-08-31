"""🗜️ Compression Engine - Intelligent Content Compression System
============================================================
Module: backend/data_management/backups/compression_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Compression System - Enterprise Production-Ready
Responsibility: Compression avancée multi-format avec optimisation intelligente
===============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""import asyncio
import logging
import zstandard as zstd
import gzip
import bz2
import lzma
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, BinaryIO, Tuple
from pathlib import Path
from dataclasses import dataclass
import hashlib
import json
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import tempfile
import shutil

from .exceptions import CompressionException, CompressionAlgorithmException

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Résultat d'une opération de compression"""    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: str
    level: int
    processing_time_seconds: float
    checksum_original: str
    checksum_compressed: str
    metadata: Dict[str, Any]
    
    @property
    def space_saved_bytes(self) -> int:
        """Espace économisé en bytes"""        return self.original_size - self.compressed_size
    
    @property
    def space_saved_percentage(self) -> float:
        """Pourcentage d'espace économisé"""        if self.original_size == 0:
            return 0.0
        return ((self.original_size - self.compressed_size) / self.original_size) * 100


@dataclass
class CompressionConfig:
    """Configuration de compression"""    algorithm: str = "zstd"
    level: int = 6
    threads: int = 4
    content_aware: bool = True
    benchmark_mode: bool = False
    verify_integrity: bool = True
    
    # Paramètres spécifiques par algorithme
    zstd_dict_size: Optional[int] = None
    zstd_enable_ldm: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "algorithm": self.algorithm,
            "level": self.level,
            "threads": self.threads,
            "content_aware": self.content_aware,
            "benchmark_mode": self.benchmark_mode,
            "verify_integrity": self.verify_integrity,
            "zstd_dict_size": self.zstd_dict_size,
            "zstd_enable_ldm": self.zstd_enable_ldm
        }


class CompressionAlgorithm(ABC):
    """Interface abstraite pour les algorithmes de compression"""    
    @abstractmethod
    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        level: int = 6,
        **kwargs
    ) -> CompressionResult:
        """Compresse un fichier"""        pass
    
    @abstractmethod
    async def decompress(
        self,
        input_path: Path,
        output_path: Path,
        **kwargs
    ) -> bool:
        """Décompresse un fichier"""        pass
    
    @abstractmethod
    def get_optimal_level(self, content_type: str, file_size: int) -> int:
        """Retourne le niveau optimal pour le type de contenu"""        pass


class ZstandardAlgorithm(CompressionAlgorithm):
    """    Algorithme Zstandard - Performance et compression optimales
    
    Avantages:
    - Très bon ratio compression/vitesse
    - Support dictionnaires personnalisés
    - Parallélisation native
    - Optimisé pour contenus répétitifs
    """    
    def __init__(self):
        self.name = "zstd"
        self.extensions = [".zst"]
        
        # Niveaux optimaux par type de contenu
        self.optimal_levels = {
            "text": 9,        # Texte compresse très bien
            "image": 3,       # Images déjà compressées
            "audio": 3,       # Audio déjà compressé
            "video": 1,       # Vidéo déjà compressée
            "document": 6,    # Documents moyennement compressibles
            "archive": 1,     # Archives déjà compressées
            "other": 6        # Niveau par défaut
        }
    
    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        level: int = 6,
        **kwargs
    ) -> CompressionResult:
        """        Compresse un fichier avec Zstandard
        
        Args:
            input_path: Fichier source
            output_path: Fichier de sortie compressé
            level: Niveau de compression (1-22)
            **kwargs: Paramètres additionnels
            
        Returns:
            CompressionResult: Résultats de la compression
        """        try:
            start_time = datetime.now()
            
            # Vérification fichier source
            if not input_path.exists():
                raise CompressionException(f"Source file not found: {input_path}")
            
            original_size = input_path.stat().st_size
            
            # Configuration compresseur
            threads = kwargs.get("threads", 4)
            dict_size = kwargs.get("dict_size")
            enable_ldm = kwargs.get("enable_ldm", False)
            
            # Calcul checksum original
            checksum_original = await self._calculate_checksum(input_path)
            
            # Compression
            compressor = zstd.ZstdCompressor(
                level=level,
                threads=threads,
                write_checksum=True,
                enable_ldm=enable_ldm
            )
            
            # Si dictionnaire personnalisé
            if dict_size:
                # En production, charger/créer dictionnaire optimisé
                pass
            
            # Compression fichier
            with open(input_path, 'rb') as source:
                with open(output_path, 'wb') as dest:
                    compressor.copy_stream(source, dest)
            
            # Vérification résultat
            compressed_size = output_path.stat().st_size
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Calcul checksum compressé
            checksum_compressed = await self._calculate_checksum(output_path)
            
            # Temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Métadonnées
            metadata = {
                "algorithm": "zstd",
                "level": level,
                "threads": threads,
                "enable_ldm": enable_ldm,
                "content_type": self._detect_content_type(input_path)
            }
            
            result = CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm="zstd",
                level=level,
                processing_time_seconds=processing_time,
                checksum_original=checksum_original,
                checksum_compressed=checksum_compressed,
                metadata=metadata
            )
            
            logger.info(f"Zstd compression completed: {input_path.name} "
                       f"({original_size} -> {compressed_size} bytes, "
                       f"ratio: {compression_ratio:.3f}, time: {processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Zstd compression failed for {input_path}: {e}")
            raise CompressionException(f"Zstd compression failed: {e}")
    
    async def decompress(
        self,
        input_path: Path,
        output_path: Path,
        **kwargs
    ) -> bool:
        """        Décompresse un fichier Zstandard
        
        Args:
            input_path: Fichier compressé
            output_path: Fichier de sortie décompressé
            **kwargs: Paramètres additionnels
            
        Returns:
            bool: True si décompression réussie
        """        try:
            if not input_path.exists():
                logger.error(f"Compressed file not found: {input_path}")
                return False
            
            # Création répertoire de sortie
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Décompression
            decompressor = zstd.ZstdDecompressor()
            
            with open(input_path, 'rb') as source:
                with open(output_path, 'wb') as dest:
                    decompressor.copy_stream(source, dest)
            
            logger.info(f"Zstd decompression completed: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Zstd decompression failed for {input_path}: {e}")
            return False
    
    def get_optimal_level(self, content_type: str, file_size: int) -> int:
        """        Détermine le niveau optimal selon le type de contenu
        
        Args:
            content_type: Type de contenu
            file_size: Taille du fichier
            
        Returns:
            int: Niveau de compression optimal
        """        base_level = self.optimal_levels.get(content_type, 6)
        
        # Ajustement selon la taille
        if file_size > 1024**3:  # > 1GB
            return max(1, base_level - 2)  # Moins de compression pour gros fichiers
        elif file_size < 1024**2:  # < 1MB
            return min(22, base_level + 2)  # Plus de compression pour petits fichiers
        
        return base_level
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier"""        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Détecte le type de contenu d'un fichier"""        extension = file_path.suffix.lower()
        
        content_type_mapping = {
            # Audio
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.ogg': 'audio',
            '.m4a': 'audio', '.aiff': 'audio', '.wma': 'audio',
            
            # Vidéo
            '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video',
            '.webm': 'video', '.flv': 'video', '.wmv': 'video',
            
            # Image
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.bmp': 'image', '.tiff': 'image', '.svg': 'image', '.webp': 'image',
            
            # Texte
            '.txt': 'text', '.md': 'text', '.html': 'text', '.css': 'text',
            '.js': 'text', '.py': 'text', '.json': 'text', '.xml': 'text',
            
            # Documents
            '.pdf': 'document', '.doc': 'document', '.docx': 'document',
            '.xls': 'document', '.xlsx': 'document', '.ppt': 'document',
            
            # Archives
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive', '.tar': 'archive'
        }
        
        return content_type_mapping.get(extension, 'other')


class GzipAlgorithm(CompressionAlgorithm):
    """    Algorithme Gzip - Compatibilité maximale
    
    Avantages:
    - Support universel
    - Intégration web native
    - Streaming efficace
    - Décompression rapide
    """    
    def __init__(self):
        self.name = "gzip"
        self.extensions = [".gz"]
        
        self.optimal_levels = {
            "text": 9,
            "image": 1,
            "audio": 1,
            "video": 1,
            "document": 6,
            "archive": 1,
            "other": 6
        }
    
    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        level: int = 6,
        **kwargs
    ) -> CompressionResult:
        """Compresse un fichier avec Gzip"""        try:
            start_time = datetime.now()
            
            if not input_path.exists():
                raise CompressionException(f"Source file not found: {input_path}")
            
            original_size = input_path.stat().st_size
            checksum_original = await self._calculate_checksum(input_path)
            
            # Compression
            with open(input_path, 'rb') as source:
                with gzip.open(output_path, 'wb', compresslevel=level) as dest:
                    shutil.copyfileobj(source, dest)
            
            compressed_size = output_path.stat().st_size
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            checksum_compressed = await self._calculate_checksum(output_path)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "algorithm": "gzip",
                "level": level,
                "content_type": self._detect_content_type(input_path)
            }
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm="gzip",
                level=level,
                processing_time_seconds=processing_time,
                checksum_original=checksum_original,
                checksum_compressed=checksum_compressed,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Gzip compression failed for {input_path}: {e}")
            raise CompressionException(f"Gzip compression failed: {e}")
    
    async def decompress(self, input_path: Path, output_path: Path, **kwargs) -> bool:
        """Décompresse un fichier Gzip"""        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with gzip.open(input_path, 'rb') as source:
                with open(output_path, 'wb') as dest:
                    shutil.copyfileobj(source, dest)
            
            return True
            
        except Exception as e:
            logger.error(f"Gzip decompression failed for {input_path}: {e}")
            return False
    
    def get_optimal_level(self, content_type: str, file_size: int) -> int:
        """Retourne le niveau optimal pour Gzip"""        return self.optimal_levels.get(content_type, 6)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256"""        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Détecte le type de contenu"""        return ZstandardAlgorithm()._detect_content_type(file_path)


class Bzip2Algorithm(CompressionAlgorithm):
    """    Algorithme Bzip2 - Compression maximale
    
    Avantages:
    - Très bon ratio de compression
    - Adapté aux gros fichiers texte
    - Récupération d'erreurs
    - Compression déterministe
    """    
    def __init__(self):
        self.name = "bzip2"
        self.extensions = [".bz2"]
        
        self.optimal_levels = {
            "text": 9,
            "image": 1,
            "audio": 1,
            "video": 1,
            "document": 9,
            "archive": 1,
            "other": 6
        }
    
    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        level: int = 6,
        **kwargs
    ) -> CompressionResult:
        """Compresse un fichier avec Bzip2"""        try:
            start_time = datetime.now()
            
            if not input_path.exists():
                raise CompressionException(f"Source file not found: {input_path}")
            
            original_size = input_path.stat().st_size
            checksum_original = await self._calculate_checksum(input_path)
            
            # Compression
            with open(input_path, 'rb') as source:
                with bz2.open(output_path, 'wb', compresslevel=level) as dest:
                    shutil.copyfileobj(source, dest)
            
            compressed_size = output_path.stat().st_size
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            checksum_compressed = await self._calculate_checksum(output_path)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "algorithm": "bzip2",
                "level": level,
                "content_type": self._detect_content_type(input_path)
            }
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm="bzip2",
                level=level,
                processing_time_seconds=processing_time,
                checksum_original=checksum_original,
                checksum_compressed=checksum_compressed,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Bzip2 compression failed for {input_path}: {e}")
            raise CompressionException(f"Bzip2 compression failed: {e}")
    
    async def decompress(self, input_path: Path, output_path: Path, **kwargs) -> bool:
        """Décompresse un fichier Bzip2"""        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with bz2.open(input_path, 'rb') as source:
                with open(output_path, 'wb') as dest:
                    shutil.copyfileobj(source, dest)
            
            return True
            
        except Exception as e:
            logger.error(f"Bzip2 decompression failed for {input_path}: {e}")
            return False
    
    def get_optimal_level(self, content_type: str, file_size: int) -> int:
        """Retourne le niveau optimal pour Bzip2"""        return self.optimal_levels.get(content_type, 6)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256"""        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Détecte le type de contenu"""        return ZstandardAlgorithm()._detect_content_type(file_path)


class CompressionEngine:
    """    Moteur de compression intelligent avec sélection automatique d'algorithme
    
    Fonctionnalités:
    - Sélection automatique algorithme optimal
    - Benchmark temps réel
    - Optimisation par type de contenu
    - Compression parallèle
    - Vérification intégrité
    - Statistiques détaillées
    """    
    def __init__(self):
        self.algorithms = {
            "zstd": ZstandardAlgorithm(),
            "gzip": GzipAlgorithm(),
            "bzip2": Bzip2Algorithm()
        }
        
        self.default_algorithm = "zstd"
        self.compression_stats = {
            "total_files_compressed": 0,
            "total_bytes_processed": 0,
            "total_bytes_saved": 0,
            "average_compression_ratio": 0.0,
            "algorithm_usage": {},
            "performance_metrics": {}
        }
        
        logger.info("CompressionEngine initialized with algorithms: " + 
                   ", ".join(self.algorithms.keys()))
    
    async def compress(
        self,
        source_paths: List[Path],
        config: Optional[CompressionConfig] = None
    ) -> List[CompressionResult]:
        """        Compresse une liste de fichiers avec optimisation intelligente
        
        Args:
            source_paths: Liste des fichiers à comprimer
            config: Configuration de compression
            
        Returns:
            List[CompressionResult]: Résultats de compression
        """        config = config or CompressionConfig()
        results = []
        
        # Préparation des tâches parallèles
        tasks = []
        for source_path in source_paths:
            task = asyncio.create_task(
                self._compress_single_file(source_path, config)
            )
            tasks.append(task)
        
        # Exécution parallèle avec limitation
        semaphore = asyncio.Semaphore(config.threads)
        
        async def compress_with_semaphore(task):
            async with semaphore:
                return await task
        
        # Traitement par lots pour éviter surcharge
        batch_size = config.threads * 2
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[compress_with_semaphore(task) for task in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, CompressionResult):
                    results.append(result)
                    await self._update_compression_stats(result)
                elif isinstance(result, Exception):
                    logger.error(f"Compression task failed: {result}")
        
        logger.info(f"Completed compression of {len(results)}/{len(source_paths)} files")
        return results
    
    async def _compress_single_file(
        self,
        source_path: Path,
        config: CompressionConfig
    ) -> CompressionResult:
        """        Compresse un fichier unique avec sélection d'algorithme optimal
        
        Args:
            source_path: Fichier source
            config: Configuration de compression
            
        Returns:
            CompressionResult: Résultat de la compression
        """        try:
            # Sélection algorithme optimal
            algorithm_name = config.algorithm
            
            if config.content_aware:
                algorithm_name = await self._select_optimal_algorithm(source_path, config)
            
            algorithm = self.algorithms[algorithm_name]
            
            # Sélection niveau optimal
            content_type = algorithm._detect_content_type(source_path)
            file_size = source_path.stat().st_size
            optimal_level = algorithm.get_optimal_level(content_type, file_size)
            
            # Override du niveau si spécifié dans config
            compression_level = config.level if config.level > 0 else optimal_level
            
            # Chemin de sortie
            output_path = source_path.parent / f"{source_path.name}.{algorithm.extensions[0]}"
            
            # Benchmark si activé
            if config.benchmark_mode:
                return await self._benchmark_compression(source_path, config)
            
            # Compression
            result = await algorithm.compress(
                input_path=source_path,
                output_path=output_path,
                level=compression_level,
                threads=config.threads
            )
            
            # Vérification intégrité si activée
            if config.verify_integrity:
                integrity_valid = await self._verify_compression_integrity(
                    source_path, output_path, algorithm
                )
                result.metadata["integrity_verified"] = integrity_valid
                
                if not integrity_valid:
                    logger.warning(f"Integrity verification failed for {source_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Single file compression failed for {source_path}: {e}")
            raise CompressionException(f"File compression failed: {e}")
    
    async def _select_optimal_algorithm(
        self,
        source_path: Path,
        config: CompressionConfig
    ) -> str:
        """        Sélectionne l'algorithme optimal selon le contexte
        
        Args:
            source_path: Fichier à analyser
            config: Configuration
            
        Returns:
            str: Nom de l'algorithme optimal
        """        content_type = ZstandardAlgorithm()._detect_content_type(source_path)
        file_size = source_path.stat().st_size
        
        # Matrice de sélection basée sur type de contenu et taille
        selection_matrix = {
            "text": {
                "small": "bzip2",    # < 1MB - compression maximale
                "medium": "zstd",    # 1MB-100MB - équilibre
                "large": "zstd"      # > 100MB - vitesse prioritaire
            },
            "image": {
                "small": "gzip",     # Images déjà compressées
                "medium": "gzip",
                "large": "gzip"
            },
            "audio": {
                "small": "gzip",     # Audio déjà compressé
                "medium": "gzip", 
                "large": "zstd"      # Zstd plus rapide pour gros fichiers
            },
            "video": {
                "small": "gzip",     # Vidéo déjà compressée
                "medium": "zstd",
                "large": "zstd"      # Zstd optimal pour gros fichiers
            },
            "document": {
                "small": "bzip2",    # Documents compressent bien
                "medium": "zstd",
                "large": "zstd"
            },
            "archive": {
                "small": "gzip",     # Archives déjà compressées
                "medium": "gzip",
                "large": "gzip"
            },
            "other": {
                "small": "zstd",     # Zstd par défaut
                "medium": "zstd",
                "large": "zstd"
            }
        }
        
        # Détermination taille
        if file_size < 1024**2:  # < 1MB
            size_category = "small"
        elif file_size < 100 * 1024**2:  # < 100MB
            size_category = "medium"
        else:  # >= 100MB
            size_category = "large"
        
        # Sélection algorithme
        algorithm = selection_matrix.get(content_type, {}).get(size_category, self.default_algorithm)
        
        logger.debug(f"Selected algorithm {algorithm} for {content_type} file of size {file_size}")
        return algorithm
    
    async def _benchmark_compression(
        self,
        source_path: Path,
        config: CompressionConfig
    ) -> CompressionResult:
        """        Benchmark de tous les algorithmes pour sélectionner le meilleur
        
        Args:
            source_path: Fichier à benchmark
            config: Configuration
            
        Returns:
            CompressionResult: Meilleur résultat de compression
        """        logger.info(f"Benchmarking compression algorithms for {source_path.name}")
        
        benchmark_results = []
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Test de tous les algorithmes
            for algo_name, algorithm in self.algorithms.items():
                try:
                    temp_output = temp_dir / f"{source_path.name}.{algorithm.extensions[0]}"
                    
                    content_type = algorithm._detect_content_type(source_path)
                    file_size = source_path.stat().st_size
                    optimal_level = algorithm.get_optimal_level(content_type, file_size)
                    
                    result = await algorithm.compress(
                        input_path=source_path,
                        output_path=temp_output,
                        level=optimal_level,
                        threads=config.threads
                    )
                    
                    benchmark_results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Benchmark failed for {algo_name}: {e}")
                    continue
            
            # Sélection du meilleur résultat
            if not benchmark_results:
                raise CompressionException("All benchmark algorithms failed")
            
            # Critères de sélection: ratio de compression et vitesse
            best_result = min(
                benchmark_results,
                key=lambda r: r.compression_ratio + (r.processing_time_seconds / 100)
            )
            
            # Copie du meilleur résultat vers destination finale
            final_output = source_path.parent / f"{source_path.name}.{best_result.algorithm}"
            best_temp_file = temp_dir / f"{source_path.name}.{best_result.algorithm}"
            
            if best_temp_file.exists():
                shutil.move(str(best_temp_file), str(final_output))
            
            logger.info(f"Benchmark selected {best_result.algorithm} for {source_path.name} "
                       f"(ratio: {best_result.compression_ratio:.3f}, "
                       f"time: {best_result.processing_time_seconds:.2f}s)")
            
            return best_result
            
        finally:
            # Nettoyage fichiers temporaires
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def _verify_compression_integrity(
        self,
        original_path: Path,
        compressed_path: Path,
        algorithm: CompressionAlgorithm
    ) -> bool:
        """        Vérifie l'intégrité de la compression via décompression test
        
        Args:
            original_path: Fichier original
            compressed_path: Fichier compressé
            algorithm: Algorithme utilisé
            
        Returns:
            bool: True si intégrité vérifiée
        """        try:
            # Décompression dans fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Décompression test
            success = await algorithm.decompress(compressed_path, temp_path)
            
            if not success:
                return False
            
            # Comparaison checksums
            original_checksum = await self._calculate_file_checksum(original_path)
            decompressed_checksum = await self._calculate_file_checksum(temp_path)
            
            # Nettoyage
            temp_path.unlink()
            
            return original_checksum == decompressed_checksum
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return False
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier"""        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _update_compression_stats(self, result: CompressionResult):
        """Met à jour les statistiques globales de compression"""        self.compression_stats["total_files_compressed"] += 1
        self.compression_stats["total_bytes_processed"] += result.original_size
        self.compression_stats["total_bytes_saved"] += result.space_saved_bytes
        
        # Mise à jour ratio moyen
        total_files = self.compression_stats["total_files_compressed"]
        current_avg = self.compression_stats["average_compression_ratio"]
        new_avg = ((current_avg * (total_files - 1)) + result.compression_ratio) / total_files
        self.compression_stats["average_compression_ratio"] = new_avg
        
        # Comptage usage algorithmes
        algo = result.algorithm
        if algo not in self.compression_stats["algorithm_usage"]:
            self.compression_stats["algorithm_usage"][algo] = 0
        self.compression_stats["algorithm_usage"][algo] += 1
        
        # Métriques performance par algorithme
        if algo not in self.compression_stats["performance_metrics"]:
            self.compression_stats["performance_metrics"][algo] = {
                "total_time": 0.0,
                "total_files": 0,
                "avg_ratio": 0.0,
                "avg_speed_mbps": 0.0
            }
        
        perf = self.compression_stats["performance_metrics"][algo]
        perf["total_time"] += result.processing_time_seconds
        perf["total_files"] += 1
        
        # Calcul moyennes
        perf["avg_ratio"] = ((perf["avg_ratio"] * (perf["total_files"] - 1)) + 
                            result.compression_ratio) / perf["total_files"]
        
        if result.processing_time_seconds > 0:
            speed_mbps = (result.original_size / (1024**2)) / result.processing_time_seconds
            perf["avg_speed_mbps"] = ((perf["avg_speed_mbps"] * (perf["total_files"] - 1)) + 
                                     speed_mbps) / perf["total_files"]
    
    async def decompress(
        self,
        compressed_paths: List[Path],
        output_directory: Optional[Path] = None
    ) -> List[bool]:
        """        Décompresse une liste de fichiers
        
        Args:
            compressed_paths: Liste des fichiers compressés
            output_directory: Répertoire de sortie optionnel
            
        Returns:
            List[bool]: Résultats de décompression
        """        results = []
        
        for compressed_path in compressed_paths:
            try:
                # Détection algorithme par extension
                algorithm = self._detect_algorithm_from_extension(compressed_path)
                
                if not algorithm:
                    logger.error(f"Unknown compression format: {compressed_path}")
                    results.append(False)
                    continue
                
                # Chemin de sortie
                if output_directory:
                    output_path = output_directory / compressed_path.stem
                else:
                    output_path = compressed_path.parent / compressed_path.stem
                
                # Décompression
                success = await algorithm.decompress(compressed_path, output_path)
                results.append(success)
                
                if success:
                    logger.info(f"Decompressed: {compressed_path.name} -> {output_path.name}")
                else:
                    logger.error(f"Decompression failed: {compressed_path.name}")
                    
            except Exception as e:
                logger.error(f"Decompression error for {compressed_path}: {e}")
                results.append(False)
        
        return results
    
    def _detect_algorithm_from_extension(self, file_path: Path) -> Optional[CompressionAlgorithm]:
        """Détecte l'algorithme de compression par l'extension du fichier"""        extension = file_path.suffix.lower()
        
        for algorithm in self.algorithms.values():
            if extension in algorithm.extensions:
                return algorithm
        
        return None
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """        Récupère les statistiques de compression
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """        stats = self.compression_stats.copy()
        
        # Calculs additionnels
        if stats["total_bytes_processed"] > 0:
            stats["space_savings_percentage"] = (
                stats["total_bytes_saved"] / stats["total_bytes_processed"]
            ) * 100
            
            stats["total_gb_processed"] = stats["total_bytes_processed"] / (1024**3)
            stats["total_gb_saved"] = stats["total_bytes_saved"] / (1024**3)
        
        return stats
    
    def get_algorithm_recommendations(self, content_type: str, file_size: int) -> Dict[str, Any]:
        """        Fournit des recommandations d'algorithme pour un type de contenu
        
        Args:
            content_type: Type de contenu
            file_size: Taille du fichier
            
        Returns:
            Dict[str, Any]: Recommandations détaillées
        """        recommendations = {}
        
        for algo_name, algorithm in self.algorithms.items():
            optimal_level = algorithm.get_optimal_level(content_type, file_size)
            
            # Estimation performance basée sur type de contenu
            expected_ratio = self._estimate_compression_ratio(algo_name, content_type)
            expected_speed = self._estimate_compression_speed(algo_name, file_size)
            
            recommendations[algo_name] = {
                "optimal_level": optimal_level,
                "expected_compression_ratio": expected_ratio,
                "expected_speed_mbps": expected_speed,
                "suitable_for": self._get_suitability_description(algo_name, content_type)
            }
        
        return recommendations
    
    def _estimate_compression_ratio(self, algorithm: str, content_type: str) -> float:
        """Estime le ratio de compression selon l'algorithme et type de contenu"""        # Ratios estimés basés sur données empiriques
        ratios = {
            "zstd": {
                "text": 0.25, "image": 0.95, "audio": 0.98, "video": 0.99,
                "document": 0.40, "archive": 0.95, "other": 0.60
            },
            "gzip": {
                "text": 0.30, "image": 0.98, "audio": 0.99, "video": 0.99,
                "document": 0.50, "archive": 0.98, "other": 0.70
            },
            "bzip2": {
                "text": 0.20, "image": 0.95, "audio": 0.98, "video": 0.99,
                "document": 0.35, "archive": 0.95, "other": 0.55
            }
        }
        
        return ratios.get(algorithm, {}).get(content_type, 0.70)
    
    def _estimate_compression_speed(self, algorithm: str, file_size: int) -> float:
        """Estime la vitesse de compression en MB/s"""        # Vitesses estimées basées sur benchmarks
        base_speeds = {
            "zstd": 100,    # MB/s
            "gzip": 50,     # MB/s
            "bzip2": 10     # MB/s
        }
        
        base_speed = base_speeds.get(algorithm, 50)
        
        # Ajustement selon taille (parallélisation plus efficace sur gros fichiers)
        if file_size > 100 * 1024**2:  # > 100MB
            return base_speed * 1.2
        elif file_size < 1024**2:  # < 1MB
            return base_speed * 0.5
        
        return base_speed
    
    def _get_suitability_description(self, algorithm: str, content_type: str) -> str:
        """Fournit une description de l'adéquation de l'algorithme"""        descriptions = {
            "zstd": {
                "text": "Excellent équilibre vitesse/compression pour texte",
                "image": "Rapide pour images déjà compressées",
                "audio": "Optimal pour gros fichiers audio",
                "video": "Meilleur choix pour fichiers vidéo volumineux",
                "document": "Très bon pour documents mixtes",
                "archive": "Rapide pour archives existantes",
                "other": "Excellent choix par défaut"
            },
            "gzip": {
                "text": "Compatible universellement pour texte",
                "image": "Standard web pour images",
                "audio": "Décompression rapide pour audio",
                "video": "Compatible mais moins optimal",
                "document": "Support universel pour documents",
                "archive": "Standard pour archives web",
                "other": "Compatibilité maximale"
            },
            "bzip2": {
                "text": "Compression maximale pour texte",
                "image": "Non recommandé pour images",
                "audio": "Non adapté pour audio",
                "video": "Non adapté pour vidéo",
                "document": "Excellent pour gros documents",
                "archive": "Compression très élevée mais lente",
                "other": "Compression maximale si temps non critique"
            }
        }
        
        return descriptions.get(algorithm, {}).get(content_type, "Usage général")


class AdaptiveCompression(CompressionEngine):
    """    Moteur de compression adaptatif avec apprentissage automatique
    
    Fonctionnalités:
    - Apprentissage patterns de compression
    - Adaptation automatique selon usage
    - Prédiction performances
    - Optimisation continue
    """    
    def __init__(self):
        super().__init__()
        self.learning_data = {}
        self.adaptation_enabled = True
        
        logger.info("AdaptiveCompression initialized with ML optimization")
    
    async def learn_from_compression(self, source_path: Path, result: CompressionResult):
        """Apprend des résultats de compression pour améliorer les prédictions"""        content_type = result.metadata.get("content_type", "other")
        file_size = result.original_size
        
        # Stockage données d'apprentissage
        key = f"{content_type}_{self._get_size_category(file_size)}"
        
        if key not in self.learning_data:
            self.learning_data[key] = {
                "samples": [],
                "best_algorithm": result.algorithm,
                "best_ratio": result.compression_ratio
            }
        
        self.learning_data[key]["samples"].append({
            "algorithm": result.algorithm,
            "ratio": result.compression_ratio,
            "speed": result.processing_time_seconds,
            "level": result.level
        })
        
        # Mise à jour meilleur algorithme si nécessaire
        if result.compression_ratio < self.learning_data[key]["best_ratio"]:
            self.learning_data[key]["best_algorithm"] = result.algorithm
            self.learning_data[key]["best_ratio"] = result.compression_ratio
    
    def _get_size_category(self, file_size: int) -> str:
        """Catégorise la taille de fichier"""        if file_size < 1024**2:
            return "small"
        elif file_size < 100 * 1024**2:
            return "medium"
        else:
            return "large"
    
    async def _select_optimal_algorithm(self, source_path: Path, config: CompressionConfig) -> str:
        """Sélection d'algorithme basée sur l'apprentissage"""        if not self.adaptation_enabled:
            return await super()._select_optimal_algorithm(source_path, config)
        
        content_type = ZstandardAlgorithm()._detect_content_type(source_path)
        file_size = source_path.stat().st_size
        size_category = self._get_size_category(file_size)
        
        key = f"{content_type}_{size_category}"
        
        # Utilisation données apprises si disponibles
        if key in self.learning_data and len(self.learning_data[key]["samples"]) >= 3:
            best_algorithm = self.learning_data[key]["best_algorithm"]
            logger.debug(f"Using learned optimal algorithm {best_algorithm} for {key}")
            return best_algorithm
        
        # Fallback sur sélection par défaut
        return await super()._select_optimal_algorithm(source_path, config)


class ContentAwareCompression(CompressionEngine):
    """    Compression intelligente basée sur l'analyse de contenu
    
    Fonctionnalités:
    - Analyse profonde du contenu
    - Optimisation fine par type
    - Détection patterns spécifiques
    - Compression spécialisée
    """    
    def __init__(self):
        super().__init__()
        self.content_analyzers = self._initialize_content_analyzers()
        
        logger.info("ContentAwareCompression initialized with content analysis")
    
    def _initialize_content_analyzers(self) -> Dict[str, Any]:
        """Initialise les analyseurs de contenu spécialisés"""        return {
            "text": self._analyze_text_content,
            "image": self._analyze_image_content,
            "audio": self._analyze_audio_content,
            "video": self._analyze_video_content,
            "document": self._analyze_document_content
        }
    
    async def _analyze_text_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyse approfondie du contenu textuel"""        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(10000)  # Échantillon 10KB
            
            # Analyse caractéristiques
            char_diversity = len(set(sample)) / len(sample) if sample else 0
            repetition_rate = (len(sample) - len(set(sample.split()))) / len(sample) if sample else 0
            
            return {
                "character_diversity": char_diversity,
                "repetition_rate": repetition_rate,
                "recommended_algorithm": "bzip2" if repetition_rate > 0.3 else "zstd",
                "recommended_level": 9 if repetition_rate > 0.5 else 6
            }
            
        except Exception:
            return {"recommended_algorithm": "zstd", "recommended_level": 6}
    
    async def _analyze_image_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyse du contenu image"""        # Analyse simplifiée - en production utiliser PIL/OpenCV
        return {
            "recommended_algorithm": "gzip",
            "recommended_level": 1  # Images déjà compressées
        }
    
    async def _analyze_audio_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyse du contenu audio"""        # Analyse simplifiée - en production utiliser librosa
        return {
            "recommended_algorithm": "zstd",
            "recommended_level": 3  # Audio déjà compressé
        }
    
    async def _analyze_video_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyse du contenu vidéo"""        # Analyse simplifiée - en production utiliser ffprobe
        return {
            "recommended_algorithm": "zstd",
            "recommended_level": 1  # Vidéo déjà compressée
        }
    
    async def _analyze_document_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyse du contenu document"""        # Analyse simplifiée - en production utiliser extracteurs spécialisés
        return {
            "recommended_algorithm": "zstd",
            "recommended_level": 6
        }
    
    async def _select_optimal_algorithm(self, source_path: Path, config: CompressionConfig) -> str:
        """Sélection basée sur l'analyse de contenu"""        content_type = ZstandardAlgorithm()._detect_content_type(source_path)
        
        # Analyse approfondie si analyseur disponible
        if content_type in self.content_analyzers:
            analysis = await self.content_analyzers[content_type](source_path)
            return analysis.get("recommended_algorithm", self.default_algorithm)
        
        # Fallback sur sélection standard
        return await super()._select_optimal_algorithm(source_path, config)
