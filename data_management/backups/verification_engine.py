"""🔍 Verification Engine - Advanced Backup Integrity System
=========================================================
Module: backend/data_management/backups/verification_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Verification System - Enterprise Production-Ready
Responsibility: Vérification intégrité et validation sauvegardes
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""import asyncio
import logging
import hashlib
import os
import json
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, BinaryIO, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import mimetypes
import struct

from .models import BackupMetadata, BackupStatus
from .exceptions import VerificationException, IntegrityException

logger = logging.getLogger(__name__)


class VerificationLevel(Enum):
    """Niveaux de vérification d'intégrité"""    BASIC = "basic"              # Checksum simple
    STANDARD = "standard"        # Checksum + métadonnées
    ADVANCED = "advanced"        # Checksum + structure + contenu
    PARANOID = "paranoid"        # Vérification complète + tests


class HashAlgorithm(Enum):
    """Algorithmes de hachage disponibles"""    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    CRC32 = "crc32"


@dataclass
class IntegrityChecksum:
    """Empreinte d'intégrité d'un fichier"""    file_path: str
    algorithm: HashAlgorithm
    checksum: str
    file_size: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "file_path": self.file_path,
            "algorithm": self.algorithm.value,
            "checksum": self.checksum,
            "file_size": self.file_size,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrityChecksum':
        """Crée depuis un dictionnaire"""        return cls(
            file_path=data["file_path"],
            algorithm=HashAlgorithm(data["algorithm"]),
            checksum=data["checksum"],
            file_size=data["file_size"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class VerificationResult:
    """Résultat de vérification d'intégrité"""    file_path: str
    is_valid: bool
    verification_level: VerificationLevel
    checksums: List[IntegrityChecksum]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration: float = 0.0
    verified_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "file_path": self.file_path,
            "is_valid": self.is_valid,
            "verification_level": self.verification_level.value,
            "checksums": [c.to_dict() for c in self.checksums],
            "errors": self.errors,
            "warnings": self.warnings,
            "duration": self.duration,
            "verified_at": self.verified_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class VerificationConfig:
    """Configuration de vérification"""    level: VerificationLevel = VerificationLevel.STANDARD
    algorithms: List[HashAlgorithm] = field(default_factory=lambda: [HashAlgorithm.SHA256])
    parallel_workers: int = 4
    chunk_size: int = 64 * 1024  # 64KB
    verify_metadata: bool = True
    verify_structure: bool = True
    content_verification: bool = False
    deep_scan: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "level": self.level.value,
            "algorithms": [a.value for a in self.algorithms],
            "parallel_workers": self.parallel_workers,
            "chunk_size": self.chunk_size,
            "verify_metadata": self.verify_metadata,
            "verify_structure": self.verify_structure,
            "content_verification": self.content_verification,
            "deep_scan": self.deep_scan
        }


class VerificationEngine:
    """    Moteur de vérification d'intégrité des sauvegardes
    
    Fonctionnalités:
    - Calcul checksums multi-algorithmes
    - Vérification intégrité à plusieurs niveaux
    - Validation structure fichiers
    - Détection corruption/altération
    - Vérification contenu spécialisée
    - Monitoring et reporting
    - Parallélisation et optimisation
    """    
    def __init__(self, config: Optional[VerificationConfig] = None):
        self.config = config or VerificationConfig()
        
        # Cache des checksums calculés
        self.checksum_cache: Dict[str, Dict[str, IntegrityChecksum]] = {}
        
        # Statistiques de vérification
        self.verification_stats = {
            "total_files_verified": 0,
            "total_bytes_verified": 0,
            "verification_failures": 0,
            "corruption_detected": 0,
            "cache_hits": 0,
            "average_verification_time": 0.0
        }
        
        # Historique des vérifications
        self.verification_history: List[VerificationResult] = []
        
        logger.info(f"VerificationEngine initialized with level {self.config.level.value}")
    
    async def verify_file(
        self,
        file_path: Path,
        reference_checksums: Optional[List[IntegrityChecksum]] = None,
        level: Optional[VerificationLevel] = None
    ) -> VerificationResult:
        """        Vérifie l'intégrité d'un fichier
        
        Args:
            file_path: Chemin du fichier à vérifier
            reference_checksums: Checksums de référence (optionnel)
            level: Niveau de vérification (optionnel)
            
        Returns:
            VerificationResult: Résultat de la vérification
        """        start_time = time.time()
        verification_level = level or self.config.level
        
        try:
            if not file_path.exists():
                return VerificationResult(
                    file_path=str(file_path),
                    is_valid=False,
                    verification_level=verification_level,
                    checksums=[],
                    errors=[f"File not found: {file_path}"]
                )
            
            logger.debug(f"Starting verification of {file_path} at level {verification_level.value}")
            
            # Calcul des checksums actuels
            current_checksums = await self._calculate_checksums(file_path)
            
            # Vérification selon le niveau
            result = VerificationResult(
                file_path=str(file_path),
                is_valid=True,
                verification_level=verification_level,
                checksums=current_checksums
            )
            
            if verification_level == VerificationLevel.BASIC:
                await self._verify_basic(file_path, current_checksums, reference_checksums, result)
            elif verification_level == VerificationLevel.STANDARD:
                await self._verify_standard(file_path, current_checksums, reference_checksums, result)
            elif verification_level == VerificationLevel.ADVANCED:
                await self._verify_advanced(file_path, current_checksums, reference_checksums, result)
            elif verification_level == VerificationLevel.PARANOID:
                await self._verify_paranoid(file_path, current_checksums, reference_checksums, result)
            
            # Finalisation
            result.duration = time.time() - start_time
            
            # Mise à jour statistiques
            self._update_verification_stats(result)
            
            # Ajout à l'historique
            self.verification_history.append(result)
            
            # Limitation historique (garde les 1000 derniers)
            if len(self.verification_history) > 1000:
                self.verification_history = self.verification_history[-1000:]
            
            logger.info(f"Verification completed for {file_path.name}: {'VALID' if result.is_valid else 'INVALID'}")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Verification failed for {file_path}: {e}")
            
            result = VerificationResult(
                file_path=str(file_path),
                is_valid=False,
                verification_level=verification_level,
                checksums=[],
                errors=[f"Verification error: {e}"],
                duration=duration
            )
            
            self._update_verification_stats(result)
            return result
    
    async def _calculate_checksums(self, file_path: Path) -> List[IntegrityChecksum]:
        """        Calcule les checksums d'un fichier selon les algorithmes configurés
        
        Args:
            file_path: Fichier à traiter
            
        Returns:
            List[IntegrityChecksum]: Checksums calculés
        """        file_key = f"{file_path}:{file_path.stat().st_mtime}"
        
        # Vérification cache
        if file_key in self.checksum_cache:
            self.verification_stats["cache_hits"] += 1
            return list(self.checksum_cache[file_key].values())
        
        checksums = []
        file_size = file_path.stat().st_size
        
        # Initialisation des hashers
        hashers = {}
        for algorithm in self.config.algorithms:
            if algorithm == HashAlgorithm.MD5:
                hashers[algorithm] = hashlib.md5()
            elif algorithm == HashAlgorithm.SHA1:
                hashers[algorithm] = hashlib.sha1()
            elif algorithm == HashAlgorithm.SHA256:
                hashers[algorithm] = hashlib.sha256()
            elif algorithm == HashAlgorithm.SHA512:
                hashers[algorithm] = hashlib.sha512()
            elif algorithm == HashAlgorithm.BLAKE2B:
                hashers[algorithm] = hashlib.blake2b()
            elif algorithm == HashAlgorithm.CRC32:
                hashers[algorithm] = None  # Traitement spécial pour CRC32
        
        # Lecture et calcul par chunks
        crc32_value = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.config.chunk_size)
                if not chunk:
                    break
                
                # Mise à jour hashers
                for algorithm, hasher in hashers.items():
                    if algorithm == HashAlgorithm.CRC32:
                        import zlib
                        crc32_value = zlib.crc32(chunk, crc32_value)
                    else:
                        hasher.update(chunk)
        
        # Finalisation et création objets checksum
        for algorithm, hasher in hashers.items():
            if algorithm == HashAlgorithm.CRC32:
                checksum_value = format(crc32_value & 0xffffffff, '08x')
            else:
                checksum_value = hasher.hexdigest()
            
            checksum = IntegrityChecksum(
                file_path=str(file_path),
                algorithm=algorithm,
                checksum=checksum_value,
                file_size=file_size,
                timestamp=datetime.now(),
                metadata={
                    "mime_type": mimetypes.guess_type(str(file_path))[0],
                    "modification_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
            )
            checksums.append(checksum)
        
        # Mise en cache
        self.checksum_cache[file_key] = {c.algorithm.value: c for c in checksums}
        
        return checksums
    
    async def _verify_basic(
        self,
        file_path: Path,
        current_checksums: List[IntegrityChecksum],
        reference_checksums: Optional[List[IntegrityChecksum]],
        result: VerificationResult
    ):
        """Vérification de base : comparaison checksums"""        if not reference_checksums:
            # Pas de référence = fichier valide par défaut
            result.warnings.append("No reference checksums provided for comparison")
            return
        
        # Comparaison des checksums principaux
        ref_checksums_map = {c.algorithm: c for c in reference_checksums}
        current_checksums_map = {c.algorithm: c for c in current_checksums}
        
        mismatches = []
        
        for algorithm, ref_checksum in ref_checksums_map.items():
            if algorithm not in current_checksums_map:
                result.warnings.append(f"Missing algorithm {algorithm.value} in current checksums")
                continue
            
            current_checksum = current_checksums_map[algorithm]
            
            if ref_checksum.checksum != current_checksum.checksum:
                mismatches.append(f"{algorithm.value}: expected {ref_checksum.checksum}, got {current_checksum.checksum}")
        
        if mismatches:
            result.is_valid = False
            result.errors.extend(mismatches)
            logger.warning(f"Checksum mismatches detected in {file_path}: {mismatches}")
    
    async def _verify_standard(
        self,
        file_path: Path,
        current_checksums: List[IntegrityChecksum],
        reference_checksums: Optional[List[IntegrityChecksum]],
        result: VerificationResult
    ):
        """Vérification standard : checksums + métadonnées"""        # Vérification de base
        await self._verify_basic(file_path, current_checksums, reference_checksums, result)
        
        if not self.config.verify_metadata:
            return
        
        # Vérification des métadonnées
        if reference_checksums:
            ref_checksum = reference_checksums[0]  # Premier comme référence
            current_checksum = current_checksums[0] if current_checksums else None
            
            if current_checksum:
                # Vérification taille fichier
                if ref_checksum.file_size != current_checksum.file_size:
                    result.errors.append(
                        f"File size mismatch: expected {ref_checksum.file_size}, got {current_checksum.file_size}"
                    )
                    result.is_valid = False
        
        # Vérification intégrité du fichier
        await self._verify_file_integrity(file_path, result)
    
    async def _verify_advanced(
        self,
        file_path: Path,
        current_checksums: List[IntegrityChecksum],
        reference_checksums: Optional[List[IntegrityChecksum]],
        result: VerificationResult
    ):
        """Vérification avancée : checksums + structure + contenu"""        # Vérification standard
        await self._verify_standard(file_path, current_checksums, reference_checksums, result)
        
        if not result.is_valid:
            return  # Arrêt si déjà invalide
        
        # Vérification structure fichier
        if self.config.verify_structure:
            await self._verify_file_structure(file_path, result)
        
        # Vérification contenu spécialisée
        if self.config.content_verification:
            await self._verify_file_content(file_path, result)
    
    async def _verify_paranoid(
        self,
        file_path: Path,
        current_checksums: List[IntegrityChecksum],
        reference_checksums: Optional[List[IntegrityChecksum]],
        result: VerificationResult
    ):
        """Vérification paranoïaque : vérification complète + tests"""        # Vérification avancée
        await self._verify_advanced(file_path, current_checksums, reference_checksums, result)
        
        if not result.is_valid:
            return
        
        # Scan profond
        if self.config.deep_scan:
            await self._deep_scan_file(file_path, result)
        
        # Tests supplémentaires
        await self._additional_tests(file_path, result)
    
    async def _verify_file_integrity(self, file_path: Path, result: VerificationResult):
        """Vérifie l'intégrité basique du fichier"""        try:
            # Test de lecture
            with open(file_path, 'rb') as f:
                # Lecture par chunks pour détecter erreurs I/O
                while True:
                    chunk = f.read(self.config.chunk_size)
                    if not chunk:
                        break
            
            # Vérification permissions
            if not os.access(file_path, os.R_OK):
                result.warnings.append("File not readable")
            
        except PermissionError:
            result.errors.append("Permission denied reading file")
            result.is_valid = False
        except IOError as e:
            result.errors.append(f"I/O error reading file: {e}")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Unexpected error during integrity check: {e}")
            result.is_valid = False
    
    async def _verify_file_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure du fichier selon son type"""        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            if not mime_type:
                result.warnings.append("Unknown file type, skipping structure verification")
                return
            
            # Vérification selon le type
            if mime_type.startswith('image/'):
                await self._verify_image_structure(file_path, result)
            elif mime_type.startswith('audio/'):
                await self._verify_audio_structure(file_path, result)
            elif mime_type.startswith('video/'):
                await self._verify_video_structure(file_path, result)
            elif mime_type.startswith('text/'):
                await self._verify_text_structure(file_path, result)
            elif mime_type == 'application/json':
                await self._verify_json_structure(file_path, result)
            else:
                result.metadata["structure_verification"] = "skipped_unknown_type"
                
        except Exception as e:
            result.warnings.append(f"Structure verification failed: {e}")
    
    async def _verify_image_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure d'un fichier image"""        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                # Vérification header image
                if not img.format:
                    result.errors.append("Invalid image format")
                    result.is_valid = False
                    return
                
                # Vérification dimensions
                if img.size[0] <= 0 or img.size[1] <= 0:
                    result.errors.append("Invalid image dimensions")
                    result.is_valid = False
                
                # Tentative de chargement complet
                img.load()
                
                result.metadata["image_verification"] = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode
                }
                
        except ImportError:
            result.warnings.append("PIL not available for image verification")
        except Exception as e:
            result.errors.append(f"Image structure verification failed: {e}")
            result.is_valid = False
    
    async def _verify_audio_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure d'un fichier audio"""        try:
            import mutagen
            
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                result.errors.append("Invalid audio file format")
                result.is_valid = False
                return
            
            # Vérification métadonnées audio
            duration = getattr(audio_file, 'info', None)
            if duration and hasattr(duration, 'length'):
                if duration.length <= 0:
                    result.warnings.append("Audio file has zero duration")
            
            result.metadata["audio_verification"] = {
                "format": audio_file.mime[0] if audio_file.mime else "unknown",
                "duration": duration.length if duration and hasattr(duration, 'length') else None
            }
            
        except ImportError:
            result.warnings.append("Mutagen not available for audio verification")
        except Exception as e:
            result.warnings.append(f"Audio structure verification failed: {e}")
    
    async def _verify_video_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure d'un fichier vidéo"""        try:
            # Vérification basique du header
            with open(file_path, 'rb') as f:
                header = f.read(32)
                
                # Détection format via magic bytes
                if header.startswith(b'\x00\x00\x00'):
                    # Possible MP4/MOV
                    f.seek(4)
                    ftyp = f.read(4)
                    if ftyp != b'ftyp':
                        result.warnings.append("Invalid MP4 file structure")
                elif header.startswith(b'RIFF'):
                    # AVI format
                    f.seek(8)
                    avi_header = f.read(4)
                    if avi_header != b'AVI ':
                        result.warnings.append("Invalid AVI file structure")
            
            result.metadata["video_verification"] = {
                "header_check": "completed"
            }
            
        except Exception as e:
            result.warnings.append(f"Video structure verification failed: {e}")
    
    async def _verify_text_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure d'un fichier texte"""        try:
            # Détection encodage et validation
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Test UTF-8
            try:
                decoded = raw_data.decode('utf-8')
                encoding = 'utf-8'
            except UnicodeDecodeError:
                # Test autres encodages
                for enc in ['latin1', 'cp1252', 'ascii']:
                    try:
                        decoded = raw_data.decode(enc)
                        encoding = enc
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    result.warnings.append("Unable to decode text file")
                    return
            
            # Statistiques texte
            lines = decoded.count('\n') + 1
            chars = len(decoded)
            
            result.metadata["text_verification"] = {
                "encoding": encoding,
                "lines": lines,
                "characters": chars
            }
            
        except Exception as e:
            result.warnings.append(f"Text structure verification failed: {e}")
    
    async def _verify_json_structure(self, file_path: Path, result: VerificationResult):
        """Vérifie la structure d'un fichier JSON"""        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validation JSON réussie
            result.metadata["json_verification"] = {
                "valid_json": True,
                "type": type(data).__name__
            }
            
            if isinstance(data, dict):
                result.metadata["json_verification"]["keys"] = len(data.keys())
            elif isinstance(data, list):
                result.metadata["json_verification"]["items"] = len(data)
            
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON structure: {e}")
            result.is_valid = False
        except Exception as e:
            result.warnings.append(f"JSON structure verification failed: {e}")
    
    async def _verify_file_content(self, file_path: Path, result: VerificationResult):
        """Vérification spécialisée du contenu"""        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            if mime_type and mime_type.startswith('image/'):
                await self._verify_image_content(file_path, result)
            elif mime_type and mime_type.startswith('audio/'):
                await self._verify_audio_content(file_path, result)
            
        except Exception as e:
            result.warnings.append(f"Content verification failed: {e}")
    
    async def _verify_image_content(self, file_path: Path, result: VerificationResult):
        """Vérification contenu image"""        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                # Vérification pixels corrompus
                pixels = list(img.getdata())
                
                # Détection patterns suspects
                if len(set(pixels)) == 1:
                    result.warnings.append("Image appears to be solid color (possible corruption)")
                
                # Vérification EXIF si disponible
                if hasattr(img, '_getexif') and img._getexif():
                    result.metadata["exif_data"] = "present"
                
        except ImportError:
            pass
        except Exception as e:
            result.warnings.append(f"Image content verification failed: {e}")
    
    async def _verify_audio_content(self, file_path: Path, result: VerificationResult):
        """Vérification contenu audio"""        try:
            # Vérification silence/corruption audio basique
            file_size = file_path.stat().st_size
            
            # Fichiers audio très petits suspects
            if file_size < 1024:  # Moins de 1KB
                result.warnings.append("Audio file suspiciously small")
            
            # Patterns de corruption (séquences répétitives)
            with open(file_path, 'rb') as f:
                chunk = f.read(4096)
                if len(set(chunk)) < 10:  # Trop peu de variance
                    result.warnings.append("Audio file may be corrupted (low entropy)")
            
        except Exception as e:
            result.warnings.append(f"Audio content verification failed: {e}")
    
    async def _deep_scan_file(self, file_path: Path, result: VerificationResult):
        """Scan profond pour détecter corruptions subtiles"""        try:
            file_size = file_path.stat().st_size
            sample_size = min(file_size, 1024 * 1024)  # 1MB max
            
            # Analyse entropie
            entropy = await self._calculate_entropy(file_path, sample_size)
            
            if entropy < 1.0:  # Très faible entropie
                result.warnings.append(f"Low file entropy detected: {entropy:.2f}")
            
            result.metadata["deep_scan"] = {
                "entropy": entropy,
                "sample_size": sample_size
            }
            
        except Exception as e:
            result.warnings.append(f"Deep scan failed: {e}")
    
    async def _calculate_entropy(self, file_path: Path, sample_size: int) -> float:
        """Calcule l'entropie d'un échantillon de fichier"""        import math
        from collections import Counter
        
        with open(file_path, 'rb') as f:
            data = f.read(sample_size)
        
        if not data:
            return 0.0
        
        # Comptage fréquences bytes
        byte_counts = Counter(data)
        
        # Calcul entropie Shannon
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    async def _additional_tests(self, file_path: Path, result: VerificationResult):
        """Tests supplémentaires pour vérification paranoïaque"""        try:
            # Test accès concurrent
            try:
                with open(file_path, 'rb') as f1, open(file_path, 'rb') as f2:
                    chunk1 = f1.read(1024)
                    chunk2 = f2.read(1024)
                    
                    if chunk1 != chunk2:
                        result.errors.append("Concurrent read inconsistency detected")
                        result.is_valid = False
            except Exception:
                result.warnings.append("Could not perform concurrent read test")
            
            # Test stabilité temporelle (petit délai)
            await asyncio.sleep(0.1)
            
            # Nouveau checksum pour comparaison
            current_checksums = await self._calculate_checksums(file_path)
            
            if result.checksums and current_checksums:
                original_checksum = result.checksums[0].checksum
                new_checksum = current_checksums[0].checksum
                
                if original_checksum != new_checksum:
                    result.errors.append("File changed during verification")
                    result.is_valid = False
            
            result.metadata["additional_tests"] = "completed"
            
        except Exception as e:
            result.warnings.append(f"Additional tests failed: {e}")
    
    def _update_verification_stats(self, result: VerificationResult):
        """Met à jour les statistiques de vérification"""        self.verification_stats["total_files_verified"] += 1
        
        if not result.is_valid:
            self.verification_stats["verification_failures"] += 1
            
            # Détection corruption vs erreur
            corruption_indicators = ["mismatch", "corruption", "invalid", "damaged"]
            if any(indicator in error.lower() for error in result.errors for indicator in corruption_indicators):
                self.verification_stats["corruption_detected"] += 1
        
        # Calcul bytes vérifiés
        if result.checksums:
            self.verification_stats["total_bytes_verified"] += result.checksums[0].file_size
        
        # Mise à jour temps moyen
        current_avg = self.verification_stats["average_verification_time"]
        total_files = self.verification_stats["total_files_verified"]
        
        new_avg = ((current_avg * (total_files - 1)) + result.duration) / total_files
        self.verification_stats["average_verification_time"] = new_avg
    
    async def verify_backup_set(
        self,
        backup_metadata: BackupMetadata,
        reference_manifest: Optional[Dict[str, Any]] = None
    ) -> Dict[str, VerificationResult]:
        """        Vérifie un ensemble complet de sauvegarde
        
        Args:
            backup_metadata: Métadonnées de la sauvegarde
            reference_manifest: Manifeste de référence
            
        Returns:
            Dict[str, VerificationResult]: Résultats par fichier
        """        results = {}
        
        try:
            files_to_verify = backup_metadata.files
            
            if not files_to_verify:
                logger.warning("No files to verify in backup set")
                return results
            
            # Vérification parallèle avec semaphore
            semaphore = asyncio.Semaphore(self.config.parallel_workers)
            
            async def verify_single_file(file_info):
                async with semaphore:
                    file_path = Path(file_info["path"])
                    
                    # Récupération checksums de référence si disponibles
                    reference_checksums = None
                    if reference_manifest and str(file_path) in reference_manifest:
                        ref_data = reference_manifest[str(file_path)]
                        if "checksums" in ref_data:
                            reference_checksums = [
                                IntegrityChecksum.from_dict(c) for c in ref_data["checksums"]
                            ]
                    
                    return str(file_path), await self.verify_file(file_path, reference_checksums)
            
            # Exécution parallèle
            tasks = [verify_single_file(file_info) for file_info in files_to_verify]
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Traitement résultats
            for task_result in completed_tasks:
                if isinstance(task_result, Exception):
                    logger.error(f"Verification task failed: {task_result}")
                    continue
                
                file_path, verification_result = task_result
                results[file_path] = verification_result
            
            logger.info(f"Verified {len(results)} files in backup set")
            
        except Exception as e:
            logger.error(f"Backup set verification failed: {e}")
            raise VerificationException(f"Backup set verification failed: {e}")
        
        return results
    
    def generate_integrity_manifest(
        self,
        verification_results: Dict[str, VerificationResult]
    ) -> Dict[str, Any]:
        """        Génère un manifeste d'intégrité
        
        Args:
            verification_results: Résultats de vérification
            
        Returns:
            Dict[str, Any]: Manifeste d'intégrité
        """        manifest = {
            "created_at": datetime.now().isoformat(),
            "verification_engine_version": "1.0.0",
            "total_files": len(verification_results),
            "valid_files": sum(1 for r in verification_results.values() if r.is_valid),
            "invalid_files": sum(1 for r in verification_results.values() if not r.is_valid),
            "files": {}
        }
        
        for file_path, result in verification_results.items():
            manifest["files"][file_path] = {
                "is_valid": result.is_valid,
                "verification_level": result.verification_level.value,
                "checksums": [c.to_dict() for c in result.checksums],
                "errors": result.errors,
                "warnings": result.warnings,
                "verified_at": result.verified_at.isoformat(),
                "duration": result.duration,
                "metadata": result.metadata
            }
        
        return manifest
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """        Récupère les statistiques de vérification
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """        stats = self.verification_stats.copy()
        
        # Calculs additionnels
        if stats["total_files_verified"] > 0:
            stats["success_rate"] = (
                (stats["total_files_verified"] - stats["verification_failures"]) 
                / stats["total_files_verified"]
            ) * 100
            
            stats["corruption_rate"] = (
                stats["corruption_detected"] / stats["total_files_verified"]
            ) * 100
        
        stats["cache_hit_rate"] = (
            stats["cache_hits"] / max(stats["total_files_verified"], 1)
        ) * 100
        
        stats["total_gb_verified"] = stats["total_bytes_verified"] / (1024**3)
        
        return stats
    
    def clear_cache(self):
        """Vide le cache des checksums"""        self.checksum_cache.clear()
        logger.info("Checksum cache cleared")
    
    def get_recent_verifications(self, count: int = 10) -> List[VerificationResult]:
        """        Récupère les vérifications récentes
        
        Args:
            count: Nombre de résultats à retourner
            
        Returns:
            List[VerificationResult]: Vérifications récentes
        """        return sorted(
            self.verification_history,
            key=lambda x: x.verified_at,
            reverse=True
        )[:count]


class IntegrityDatabase:
    """    Base de données d'intégrité pour persistance des checksums
    
    Fonctionnalités:
    - Stockage persistant des checksums
    - Historique des vérifications
    - Requêtes et indexation
    - Import/export manifestes
    """    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("integrity.db")
        self.checksums: Dict[str, List[IntegrityChecksum]] = {}
        self.verification_history: List[VerificationResult] = []
        
        # Chargement données existantes
        self.load_database()
        
        logger.info(f"IntegrityDatabase initialized at {self.db_path}")
    
    def store_checksums(self, file_path: str, checksums: List[IntegrityChecksum]):
        """Stocke les checksums d'un fichier"""        self.checksums[file_path] = checksums
        self.save_database()
    
    def get_checksums(self, file_path: str) -> Optional[List[IntegrityChecksum]]:
        """Récupère les checksums d'un fichier"""        return self.checksums.get(file_path)
    
    def store_verification_result(self, result: VerificationResult):
        """Stocke un résultat de vérification"""        self.verification_history.append(result)
        
        # Limitation historique
        if len(self.verification_history) > 10000:
            self.verification_history = self.verification_history[-10000:]
        
        self.save_database()
    
    def load_database(self):
        """Charge la base de données depuis le disque"""        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                
                # Reconstruction objets
                for file_path, checksum_data in data.get("checksums", {}).items():
                    self.checksums[file_path] = [
                        IntegrityChecksum.from_dict(c) for c in checksum_data
                    ]
                
                logger.info(f"Loaded {len(self.checksums)} checksum records")
                
        except Exception as e:
            logger.warning(f"Could not load integrity database: {e}")
    
    def save_database(self):
        """Sauvegarde la base de données sur disque"""        try:
            data = {
                "checksums": {
                    file_path: [c.to_dict() for c in checksums]
                    for file_path, checksums in self.checksums.items()
                },
                "saved_at": datetime.now().isoformat()
            }
            
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save integrity database: {e}")


# Export des classes principales
__all__ = [
    'VerificationEngine',
    'IntegrityChecksum',
    'VerificationResult',
    'VerificationConfig',
    'VerificationLevel',
    'HashAlgorithm',
    'IntegrityDatabase'
]
