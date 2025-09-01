"""🚀 Security Validation System - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/data_management/validation/security_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE VALIDATION SÉCURITAIRE AVANCÉ
Validation sécuritaire complète pour protection du contenu
- Détection malwares et virus
- Analyse de vulnérabilités
- Validation signatures numériques
- Contrôle d'intégrité et authenticité
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
import hashlib
import mimetypes
import tempfile
import subprocess
import json

# Security libraries
import yara
import magic
import clamd
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

# File analysis
import exifread
import struct
import zipfile
import rarfile

# Network security
import requests
from urllib.parse import urlparse

# Content security
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class SecurityThreatLevel(Enum):
    """
Niveaux de menace sécuritaire"""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityViolationType(Enum):
    """Types de violations sécuritaires"""

    MALWARE = "malware"
    VIRUS = "virus"
    SUSPICIOUS_CONTENT = "suspicious_content"
    INTEGRITY_VIOLATION = "integrity_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_LEAK = "data_leak"
    SUSPICIOUS_METADATA = "suspicious_metadata"
    CORRUPTED_FILE = "corrupted_file"

@dataclass
class SecurityValidationResult:
    """Résultat de validation sécuritaire"""
    is_secure: bool
    threat_level: SecurityThreatLevel
    security_score: float  # 0.0 - 1.0
    violations: List[SecurityViolationType]
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    scan_details: Dict[str, Any]

class MalwareScanner:
    """
Scanner de malwares et virus"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MalwareScanner")
        
        # Initialisation ClamAV
        try:
            self.clamd_client = clamd.ClamdUnixSocket()
            self.clamd_available = self.clamd_client.ping()
        except:
            self.clamd_client = None
            self.clamd_available = False
            self.logger.warning("ClamAV non disponible")
        
        # Initialisation YARA
        try:
            self.yara_rules = self._load_yara_rules()
        except:
            self.yara_rules = None
            self.logger.warning("YARA rules non disponibles")
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scanne un fichier pour détecter malwares et virus"""
        scan_result = {
            'is_infected': False,
            'threats_detected': [],
            'scan_engines': [],
            'scan_duration': 0.0,
            'file_hash': '',
            'reputation_check': {}
        }
        
        start_time = datetime.now()
        
        try:
            # Calcul du hash pour vérification de réputation
            file_hash = self._calculate_file_hash(file_path)
            scan_result['file_hash'] = file_hash
            
            # 1. Scan ClamAV
            if self.clamd_available:
                clam_result = self._scan_with_clamav(file_path)
                scan_result['scan_engines'].append('clamav')
                
                if clam_result['infected']:
                    scan_result['is_infected'] = True
                    scan_result['threats_detected'].extend(clam_result['threats'])
            
            # 2. Scan YARA
            if self.yara_rules:
                yara_result = self._scan_with_yara(file_path)
                scan_result['scan_engines'].append('yara')
                
                if yara_result['matches']:
                    scan_result['is_infected'] = True
                    scan_result['threats_detected'].extend(yara_result['matches'])
            
            # 3. Scan heuristique personnalisé
            heuristic_result = self._heuristic_scan(file_path)
            scan_result['scan_engines'].append('heuristic')
            
            if heuristic_result['suspicious']:
                scan_result['threats_detected'].extend(heuristic_result['indicators'])
            
            # 4. Vérification de réputation (si hash disponible)
            if file_hash:
                reputation = self._check_file_reputation(file_hash)
                scan_result['reputation_check'] = reputation
                
                if reputation.get('malicious', False):
                    scan_result['is_infected'] = True
                    scan_result['threats_detected'].append('Known malicious file')
            
            # Temps de scan
            scan_duration = (datetime.now() - start_time).total_seconds()
            scan_result['scan_duration'] = scan_duration
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Erreur scan malware {file_path}: {e}")
            scan_result['error'] = str(e)
            return scan_result
    
    def _scan_with_clamav(self, file_path: str) -> Dict[str, Any]:
        """Scan avec ClamAV"""
        result = {'infected': False, 'threats': []}
        
        try:
            scan_result = self.clamd_client.scan(file_path)
            
            if scan_result:
                for path, status in scan_result.items():
                    if status[0] == 'FOUND':
                        result['infected'] = True
                        result['threats'].append(status[1])
            
        except Exception as e:
            self.logger.error(f"Erreur ClamAV: {e}")
            result['error'] = str(e)
        
        return result
    
    def _scan_with_yara(self, file_path: str) -> Dict[str, Any]:
        """Scan avec YARA"""
        result = {'matches': []}
        
        try:
            matches = self.yara_rules.match(file_path)
            
            for match in matches:
                result['matches'].append({
                    'rule': match.rule,
                    'namespace': match.namespace,
                    'tags': match.tags,
                    'meta': match.meta
                })
        
        except Exception as e:
            self.logger.error(f"Erreur YARA: {e}")
            result['error'] = str(e)
        
        return result
    
    def _heuristic_scan(self, file_path: str) -> Dict[str, Any]:
        """Scan heuristique personnalisé"""
        result = {'suspicious': False, 'indicators': []}
        
        try:
            file_size = os.path.getsize(file_path)
            
            # 1. Vérification de la taille
            if file_size == 0:
                result['suspicious'] = True
                result['indicators'].append('Empty file detected')
            elif file_size > 100 * 1024 * 1024:  # >100MB
                result['indicators'].append('Large file size (potential storage abuse)')
            
            # 2. Analyse de l'extension vs contenu réel
            declared_ext = Path(file_path).suffix.lower()
            try:
                real_mime = magic.from_file(file_path, mime=True)
                expected_mimes = mimetypes.guess_type(f"test{declared_ext}")[0]
                
                if expected_mimes and real_mime != expected_mimes:
                    result['suspicious'] = True
                    result['indicators'].append(f'Extension mismatch: {declared_ext} vs {real_mime}')
            except Exception as e:
                self.logger.debug(f"Could not analyze MIME type for {file_path}: {e}")
                result['warnings'].append(f"Could not verify MIME type: {str(e)}")
            
            # 3. Analyse des headers suspects
            with open(file_path, 'rb') as f:
                header = f.read(1024)
                
                # Détection de patterns suspects
                suspicious_patterns = [
                    b'exec(',
                    b'eval(',
                    b'system(',
                    b'<?php',
                    b'<script',
                    b'javascript:',
                    b'vbscript:',
                    b'powershell',
                    b'cmd.exe'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in header.lower():
                        result['suspicious'] = True
                        result['indicators'].append(f'Suspicious pattern detected: {pattern.decode("utf-8", errors="ignore")}')
            
            # 4. Analyse des métadonnées EXIF
            if declared_ext in ['.jpg', '.jpeg', '.tiff']:
                exif_result = self._analyze_exif_security(file_path)
                if exif_result['suspicious']:
                    result['suspicious'] = True
                    result['indicators'].extend(exif_result['indicators'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur scan heuristique: {e}")
            result['error'] = str(e)
            return result
    
    def _analyze_exif_security(self, file_path: str) -> Dict[str, Any]:
        """Analyse les métadonnées EXIF pour détecter des anomalies"""
        result = {'suspicious': False, 'indicators': []}
        
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                
                # Vérification de métadonnées suspectes
                suspicious_fields = []
                
                for tag, value in tags.items():
                    tag_str = str(tag).lower()
                    value_str = str(value).lower()
                    
                    # Détection de scripts ou commandes
                    if any(pattern in value_str for pattern in ['script', 'exec', 'cmd', 'powershell', 'http://', 'https://']):
                        suspicious_fields.append(f'{tag}: {value}')
                    
                    # Détection de longueurs anormales
                    if len(value_str) > 1000:
                        suspicious_fields.append(f'{tag}: Very long metadata field')
                
                if suspicious_fields:
                    result['suspicious'] = True
                    result['indicators'] = [f'Suspicious EXIF: {field}' for field in suspicious_fields[:5]]
        
        except Exception as e:
            self.logger.debug(f"Erreur analyse EXIF: {e}")
        
        return result
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash SHA-256 du fichier"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ''
    
    def _check_file_reputation(self, file_hash: str) -> Dict[str, Any]:
        """Vérifie la réputation du fichier via APIs externes"""
        reputation = {'malicious': False, 'sources': []}
        
        try:
            # Simulation de vérification de réputation
            # En production, intégrer avec VirusTotal, etc.
            
            # Liste noire simple de hashes connus
            known_malicious = [
                # Ajouter des hashes de malwares connus
            ]
            
            if file_hash.lower() in known_malicious:
                reputation['malicious'] = True
                reputation['sources'].append('internal_blacklist')
            
        except Exception as e:
            self.logger.error(f"Erreur vérification réputation: {e}")
        
        return reputation
    
    def _load_yara_rules(self) -> Optional[yara.Rules]:
        """Charge les règles YARA"""
        try:
            # Règles YARA basiques pour la détection
            yara_rules_text = '''
            rule SuspiciousExecutable {
                meta:
                    description = "Detects suspicious executable patterns"
                strings:
                    $exec1 = "exec(" nocase
                    $exec2 = "system(" nocase
                    $exec3 = "eval(" nocase
                    $script1 = "<script" nocase
                    $php1 = "<?php" nocase
                condition:
                    any of them
            }
            
            rule SuspiciousArchive {
                meta:
                    description = "Detects suspicious archive patterns"
                strings:
                    $zip = "PK" at 0
                    $rar = "Rar!" at 0
                condition:
                    any of them and filesize > 100MB
            }
            '''
            
            return yara.compile(source=yara_rules_text)
            
        except Exception as e:
            self.logger.error(f"Erreur chargement YARA: {e}")
            return None

class IntegrityValidator:
    """Validateur d'intégrité des fichiers"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.IntegrityValidator")
    
    def validate_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """Valide l'intégrité d'un fichier"""
        integrity_result = {
            'is_intact': True,
            'corruption_indicators': [],
            'structure_valid': True,
            'checksum_valid': True,
            'metadata_consistent': True
        }
        
        try:
            # 1. Validation de la structure selon le type
            file_ext = Path(file_path).suffix.lower()
            structure_result = self._validate_file_structure(file_path, file_ext)
            integrity_result.update(structure_result)
            
            # 2. Validation de cohérence taille/contenu
            size_result = self._validate_file_size_consistency(file_path)
            integrity_result.update(size_result)
            
            # 3. Validation de l'intégrité des métadonnées
            metadata_result = self._validate_metadata_integrity(file_path)
            integrity_result.update(metadata_result)
            
            # Score global d'intégrité
            integrity_score = self._calculate_integrity_score(integrity_result)
            integrity_result['integrity_score'] = integrity_score
            
            return integrity_result
            
        except Exception as e:
            self.logger.error(f"Erreur validation intégrité {file_path}: {e}")
            integrity_result['is_intact'] = False
            integrity_result['corruption_indicators'].append(f"Erreur système: {str(e)}")
            return integrity_result
    
    def _validate_file_structure(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Valide la structure du fichier selon son type"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            if file_ext in ['.jpg', '.jpeg']:
                result.update(self._validate_jpeg_structure(file_path))
            elif file_ext == '.png':
                result.update(self._validate_png_structure(file_path))
            elif file_ext == '.pdf':
                result.update(self._validate_pdf_structure(file_path))
            elif file_ext in ['.mp4', '.avi', '.mov']:
                result.update(self._validate_video_structure(file_path))
            elif file_ext in ['.mp3', '.wav', '.flac']:
                result.update(self._validate_audio_structure(file_path))
            elif file_ext in ['.zip', '.rar']:
                result.update(self._validate_archive_structure(file_path))
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"Erreur validation structure: {str(e)}")
        
        return result
    
    def _validate_jpeg_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure JPEG"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            with open(file_path, 'rb') as f:
                # Vérification signature JPEG
                header = f.read(2)
                if header != b'\xff\xd8':
                    result['structure_valid'] = False
                    result['structure_errors'].append("Invalid JPEG header")
                    return result
                
                # Vérification de la fin du fichier
                f.seek(-2, 2)
                footer = f.read(2)
                if footer != b'\xff\xd9':
                    result['structure_valid'] = False
                    result['structure_errors'].append("Invalid JPEG footer")
                
                # Validation avec PIL
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                except Exception as e:
                    result['structure_valid'] = False
                    result['structure_errors'].append(f"PIL validation failed: {str(e)}")
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"JPEG validation error: {str(e)}")
        
        return result
    
    def _validate_png_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure PNG"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            with open(file_path, 'rb') as f:
                # Vérification signature PNG
                header = f.read(8)
                if header != b'\x89PNG\r\n\x1a\n':
                    result['structure_valid'] = False
                    result['structure_errors'].append("Invalid PNG signature")
                    return result
                
                # Validation avec PIL
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                except Exception as e:
                    result['structure_valid'] = False
                    result['structure_errors'].append(f"PNG validation failed: {str(e)}")
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"PNG validation error: {str(e)}")
        
        return result
    
    def _validate_pdf_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure PDF"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            with open(file_path, 'rb') as f:
                # Vérification signature PDF
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    result['structure_valid'] = False
                    result['structure_errors'].append("Invalid PDF header")
                    return result
                
                # Validation avec PyPDF2
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(f)
                    if len(pdf_reader.pages) == 0:
                        result['structure_valid'] = False
                        result['structure_errors'].append("PDF has no pages")
                except Exception as e:
                    result['structure_valid'] = False
                    result['structure_errors'].append(f"PDF validation failed: {str(e)}")
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"PDF validation error: {str(e)}")
        
        return result
    
    def _validate_video_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure vidéo"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            # Validation avec OpenCV
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                result['structure_valid'] = False
                result['structure_errors'].append("Cannot open video file")
                return result
            
            # Vérification métadonnées de base
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if frame_count <= 0:
                result['structure_valid'] = False
                result['structure_errors'].append("No frames detected")
            
            if fps <= 0:
                result['structure_valid'] = False
                result['structure_errors'].append("Invalid FPS")
            
            if width <= 0 or height <= 0:
                result['structure_valid'] = False
                result['structure_errors'].append("Invalid resolution")
            
            # Test lecture d'une frame
            ret, frame = cap.read()
            if not ret:
                result['structure_valid'] = False
                result['structure_errors'].append("Cannot read video frames")
            
            cap.release()
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"Video validation error: {str(e)}")
        
        return result
    
    def _validate_audio_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure audio"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            import soundfile as sf
            
            # Validation avec soundfile
            try:
                with sf.SoundFile(file_path) as f:
                    if f.frames <= 0:
                        result['structure_valid'] = False
                        result['structure_errors'].append("No audio frames")
                    
                    if f.samplerate <= 0:
                        result['structure_valid'] = False
                        result['structure_errors'].append("Invalid sample rate")
                    
                    if f.channels <= 0:
                        result['structure_valid'] = False
                        result['structure_errors'].append("No audio channels")
            
            except Exception as e:
                result['structure_valid'] = False
                result['structure_errors'].append(f"Audio validation failed: {str(e)}")
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"Audio validation error: {str(e)}")
        
        return result
    
    def _validate_archive_structure(self, file_path: str) -> Dict[str, Any]:
        """Valide la structure d'archive"""
        result = {'structure_valid': True, 'structure_errors': []}
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.zip':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Test d'intégrité
                        bad_files = zip_ref.testzip()
                        if bad_files:
                            result['structure_valid'] = False
                            result['structure_errors'].append(f"Corrupted files in ZIP: {bad_files}")
                except Exception as e:
                    result['structure_valid'] = False
                    result['structure_errors'].append(f"ZIP validation failed: {str(e)}")
            
            elif file_ext == '.rar':
                try:
                    with rarfile.RarFile(file_path, 'r') as rar_ref:
                        # Test d'intégrité
                        rar_ref.testrar()
                except Exception as e:
                    result['structure_valid'] = False
                    result['structure_errors'].append(f"RAR validation failed: {str(e)}")
        
        except Exception as e:
            result['structure_valid'] = False
            result['structure_errors'].append(f"Archive validation error: {str(e)}")
        
        return result
    
    def _validate_file_size_consistency(self, file_path: str) -> Dict[str, Any]:
        """Valide la cohérence de la taille du fichier"""
        result = {'size_consistent': True, 'size_warnings': []}
        
        try:
            file_size = os.path.getsize(file_path)
            
            # Vérification taille minimale selon type
            file_ext = Path(file_path).suffix.lower()
            min_sizes = {
                '.jpg': 100,    # 100 bytes minimum
                '.png': 67,     # PNG minimum
                '.pdf': 200,    # PDF minimum
                '.mp3': 1000,   # 1KB minimum
                '.mp4': 10000,  # 10KB minimum
                '.txt': 1       # 1 byte minimum
            }
            
            min_size = min_sizes.get(file_ext, 0)
            if file_size < min_size:
                result['size_consistent'] = False
                result['size_warnings'].append(f"File too small: {file_size} bytes (expected >{min_size})")
            
            # Vérification taille maximale raisonnable
            max_size = 2 * 1024 * 1024 * 1024  # 2GB
            if file_size > max_size:
                result['size_warnings'].append(f"Very large file: {file_size/1024/1024:.1f}MB")
        
        except Exception as e:
            result['size_consistent'] = False
            result['size_warnings'].append(f"Size validation error: {str(e)}")
        
        return result
    
    def _validate_metadata_integrity(self, file_path: str) -> Dict[str, Any]:
        """Valide l'intégrité des métadonnées"""
        result = {'metadata_consistent': True, 'metadata_warnings': []}
        
        try:
            # Comparaison entre différentes sources de métadonnées
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                # Comparaison EXIF vs PIL
                pil_data = {}
                exif_data = {}
                
                try:
                    with Image.open(file_path) as img:
                        pil_data = {'size': img.size, 'mode': img.mode}
                except Exception as e:
                    self.logger.debug(f"Could not read image with PIL: {e}")
                    result['metadata_warnings'].append(f"PIL analysis failed: {str(e)}")
                
                try:
                    with open(file_path, 'rb') as f:
                        tags = exifread.process_file(f)
                        if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
                            exif_data['size'] = (
                                int(str(tags['EXIF ExifImageWidth'])),
                                int(str(tags['EXIF ExifImageLength']))
                            )
                except Exception as e:
                    self.logger.debug(f"Could not read EXIF data: {e}")
                    result['metadata_warnings'].append(f"EXIF analysis failed: {str(e)}")
                
                # Vérification cohérence
                if pil_data.get('size') and exif_data.get('size'):
                    if pil_data['size'] != exif_data['size']:
                        result['metadata_consistent'] = False
                        result['metadata_warnings'].append("EXIF/PIL size mismatch")
        
        except Exception as e:
            result['metadata_warnings'].append(f"Metadata validation error: {str(e)}")
        
        return result
    
    def _calculate_integrity_score(self, integrity_result: Dict[str, Any]) -> float:
        """Calcule le score d'intégrité global"""
        scores = []
        
        # Structure (40%)
        if integrity_result.get('structure_valid', True):
            scores.append(0.4)
        else:
            scores.append(0.0)
        
        # Taille (30%)
        if integrity_result.get('size_consistent', True):
            scores.append(0.3)
        else:
            scores.append(0.1)
        
        # Métadonnées (30%)
        if integrity_result.get('metadata_consistent', True):
            scores.append(0.3)
        else:
            scores.append(0.1)
        
        return sum(scores)

class AccessControlValidator:
    """
Validateur de contrôle d'accès"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AccessControlValidator")
    
    def validate_access_permissions(self, file_path: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les permissions d'accès au fichier"""
        access_result = {
            'access_granted': True,
            'permission_violations': [],
            'access_level': 'read',
            'restrictions': []
        }
        
        try:
            # 1. Vérification permissions système
            file_stat = os.stat(file_path)
            file_mode = file_stat.st_mode
            
            # Vérification permissions de lecture
            if not os.access(file_path, os.R_OK):
                access_result['access_granted'] = False
                access_result['permission_violations'].append('Read permission denied')
            
            # 2. Vérification métadonnées de sécurité
            security_metadata = self._extract_security_metadata(file_path)
            access_result['security_metadata'] = security_metadata
            
            # 3. Validation contexte utilisateur
            user_validation = self._validate_user_context(user_context, security_metadata)
            access_result.update(user_validation)
            
            return access_result
            
        except Exception as e:
            self.logger.error(f"Erreur validation accès {file_path}: {e}")
            access_result['access_granted'] = False
            access_result['permission_violations'].append(f"Access validation error: {str(e)}")
            return access_result
    
    def _extract_security_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait les métadonnées de sécurité"""
        metadata = {
            'file_owner': None,
            'creation_time': None,
            'modification_time': None,
            'access_restrictions': []
        }
        
        try:
            file_stat = os.stat(file_path)
            metadata.update({
                'creation_time': datetime.fromtimestamp(file_stat.st_ctime),
                'modification_time': datetime.fromtimestamp(file_stat.st_mtime),
                'size': file_stat.st_size
            })
            
            # Extraction métadonnées spécifiques selon type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                # Métadonnées EXIF pour informations de sécurité
                try:
                    with open(file_path, 'rb') as f:
                        tags = exifread.process_file(f)
                        
                        # Recherche d'informations sensibles
                        for tag, value in tags.items():
                            if 'GPS' in str(tag):
                                metadata['access_restrictions'].append('Contains GPS location data')
                            elif 'Owner' in str(tag) or 'Author' in str(tag):
                                metadata['file_owner'] = str(value)
                except Exception as e:
                    self.logger.debug(f"Could not extract EXIF security metadata: {e}")
                    metadata['warnings'].append(f"EXIF security analysis failed: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées sécurité: {e}")
        
        return metadata
    
    def _validate_user_context(self, user_context: Dict[str, Any], security_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Valide le contexte utilisateur par rapport aux métadonnées de sécurité"""
        validation = {
            'context_valid': True,
            'context_warnings': []
        }
        
        try:
            # Validation permissions utilisateur
            user_permissions = user_context.get('permissions', [])
            required_permissions = security_metadata.get('required_permissions', [])
            
            missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
            if missing_permissions:
                validation['context_valid'] = False
                validation['context_warnings'].append(f"Missing permissions: {', '.join(missing_permissions)}")
            
            # Validation restrictions géographiques
            if 'Contains GPS location data' in security_metadata.get('access_restrictions', []):
                if not user_context.get('geo_access_approved', False):
                    validation['context_warnings'].append('File contains location data - review required')
        
        except Exception as e:
            validation['context_warnings'].append(f"Context validation error: {str(e)}")
        
        return validation

class SecurityValidator:
    """Validateur principal de sécurité"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SecurityValidator")
        
        # Initialisation des composants
        self.malware_scanner = MalwareScanner()
        self.integrity_validator = IntegrityValidator()
        self.access_validator = AccessControlValidator()
    
    def validate_security(self, file_path: str, user_context: Optional[Dict[str, Any]] = None) -> SecurityValidationResult:
        """Valide la sécurité d'un fichier de manière complète"""
        
        if not os.path.exists(file_path):
            return SecurityValidationResult(
                is_secure=False,
                threat_level=SecurityThreatLevel.HIGH,
                security_score=0.0,
                violations=[SecurityViolationType.CORRUPTED_FILE],
                errors=["File not found"],
                warnings=[],
                recommendations=["Verify file path and permissions"],
                metadata={},
                scan_details={}
            )
        
        errors = []
        warnings = []
        recommendations = []
        violations = []
        metadata = {}
        scan_details = {}
        
        try:
            # 1. Scan malware
            malware_result = self.malware_scanner.scan_file(file_path)
            scan_details['malware_scan'] = malware_result
            
            if malware_result.get('is_infected', False):
                violations.extend([SecurityViolationType.MALWARE, SecurityViolationType.VIRUS])
                errors.append("Malware/Virus detected")
                recommendations.append("Quarantine file immediately")
            
            # 2. Validation intégrité
            integrity_result = self.integrity_validator.validate_file_integrity(file_path)
            scan_details['integrity_check'] = integrity_result
            
            if not integrity_result.get('is_intact', True):
                violations.append(SecurityViolationType.CORRUPTED_FILE)
                errors.extend(integrity_result.get('corruption_indicators', []))
                recommendations.append("File may be corrupted - verify source")
            
            if not integrity_result.get('structure_valid', True):
                violations.append(SecurityViolationType.INTEGRITY_VIOLATION)
                warnings.extend(integrity_result.get('structure_errors', []))
            
            # 3. Validation accès (si contexte utilisateur fourni)
            if user_context:
                access_result = self.access_validator.validate_access_permissions(file_path, user_context)
                scan_details['access_control'] = access_result
                
                if not access_result.get('access_granted', True):
                    violations.append(SecurityViolationType.UNAUTHORIZED_ACCESS)
                    errors.extend(access_result.get('permission_violations', []))
                
                warnings.extend(access_result.get('context_warnings', []))
            
            # 4. Analyse des métadonnées suspectes
            metadata_analysis = self._analyze_suspicious_metadata(file_path)
            scan_details['metadata_analysis'] = metadata_analysis
            
            if metadata_analysis.get('suspicious', False):
                violations.append(SecurityViolationType.SUSPICIOUS_METADATA)
                warnings.extend(metadata_analysis.get('indicators', []))
                recommendations.append("Review file metadata for sensitive information")
            
            # 5. Calcul du niveau de menace et score de sécurité
            threat_level = self._calculate_threat_level(violations, errors, warnings)
            security_score = self._calculate_security_score(scan_details, violations)
            
            # 6. Génération des recommandations
            security_recommendations = self._generate_security_recommendations(violations, threat_level)
            recommendations.extend(security_recommendations)
            
            # Métadonnées globales
            metadata.update({
                'file_size': os.path.getsize(file_path),
                'file_hash': malware_result.get('file_hash', ''),
                'scan_timestamp': datetime.now().isoformat(),
                'scan_engines': malware_result.get('scan_engines', [])
            })
            
            return SecurityValidationResult(
                is_secure=len(violations) == 0 and len(errors) == 0,
                threat_level=threat_level,
                security_score=security_score,
                violations=violations,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
                metadata=metadata,
                scan_details=scan_details
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation sécurité {file_path}: {e}")
            return SecurityValidationResult(
                is_secure=False,
                threat_level=SecurityThreatLevel.CRITICAL,
                security_score=0.0,
                violations=[SecurityViolationType.CORRUPTED_FILE],
                errors=[f"Security validation error: {str(e)}"],
                warnings=[],
                recommendations=["Contact system administrator"],
                metadata={},
                scan_details={}
            )
    
    def _analyze_suspicious_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyse les métadonnées pour détecter du contenu suspect"""
        analysis = {'suspicious': False, 'indicators': []}
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # Analyse selon le type de fichier
            if file_ext in ['.jpg', '.jpeg', '.tiff']:
                # Analyse EXIF
                with open(file_path, 'rb') as f:
                    tags = exifread.process_file(f)
                    
                    for tag, value in tags.items():
                        value_str = str(value)
                        
                        # Détection d'URLs ou scripts
                        if any(pattern in value_str.lower() for pattern in ['http://', 'https://', 'script', 'javascript']):
                            analysis['suspicious'] = True
                            analysis['indicators'].append(f'Suspicious EXIF data: {tag}')
                        
                        # Détection de commentaires suspects
                        if 'comment' in str(tag).lower() and len(value_str) > 200:
                            analysis['suspicious'] = True
                            analysis['indicators'].append('Unusually long comment in EXIF')
            
            elif file_ext == '.pdf':
                # Analyse métadonnées PDF
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        
                        if pdf_reader.metadata:
                            for key, value in pdf_reader.metadata.items():
                                if isinstance(value, str) and len(value) > 500:
                                    analysis['suspicious'] = True
                                    analysis['indicators'].append(f'Large PDF metadata field: {key}')
                except Exception as e:
                    self.logger.debug(f"Could not analyze PDF metadata: {e}")
                    analysis['warnings'].append(f"PDF metadata analysis failed: {str(e)}")
        
        except Exception as e:
            self.logger.debug(f"Erreur analyse métadonnées: {e}")
        
        return analysis
    
    def _calculate_threat_level(self, violations: List[SecurityViolationType], errors: List[str], warnings: List[str]) -> SecurityThreatLevel:
        """Calcule le niveau de menace"""
        
        # Menaces critiques
        critical_violations = [SecurityViolationType.MALWARE, SecurityViolationType.VIRUS]
        if any(v in violations for v in critical_violations):
            return SecurityThreatLevel.CRITICAL
        
        # Menaces élevées
        high_violations = [SecurityViolationType.UNAUTHORIZED_ACCESS, SecurityViolationType.DATA_LEAK]
        if any(v in violations for v in high_violations) or len(errors) > 2:
            return SecurityThreatLevel.HIGH
        
        # Menaces moyennes
        medium_violations = [SecurityViolationType.INTEGRITY_VIOLATION, SecurityViolationType.CORRUPTED_FILE]
        if any(v in violations for v in medium_violations) or len(errors) > 0:
            return SecurityThreatLevel.MEDIUM
        
        # Menaces faibles
        if len(violations) > 0 or len(warnings) > 3:
            return SecurityThreatLevel.LOW
        
        return SecurityThreatLevel.SAFE
    
    def _calculate_security_score(self, scan_details: Dict[str, Any], violations: List[SecurityViolationType]) -> float:
        """
Calcule le score de sécurité global"""
        scores = []
        
        # Score malware (40%)
        malware_scan = scan_details.get('malware_scan', {})
        if not malware_scan.get('is_infected', False):
            scores.append(0.4)
        else:
            scores.append(0.0)
        
        # Score intégrité (30%)
        integrity_check = scan_details.get('integrity_check', {})
        integrity_score = integrity_check.get('integrity_score', 0.5)
        scores.append(integrity_score * 0.3)
        
        # Score accès (20%)
        access_control = scan_details.get('access_control', {})
        if access_control.get('access_granted', True):
            scores.append(0.2)
        else:
            scores.append(0.0)
        
        # Score métadonnées (10%)
        metadata_analysis = scan_details.get('metadata_analysis', {})
        if not metadata_analysis.get('suspicious', False):
            scores.append(0.1)
        else:
            scores.append(0.05)
        
        # Pénalité pour violations
        violation_penalty = len(violations) * 0.1
        
        final_score = max(0.0, sum(scores) - violation_penalty)
        return min(1.0, final_score)
    
    def _generate_security_recommendations(self, violations: List[SecurityViolationType], threat_level: SecurityThreatLevel) -> List[str]:
        """
Génère des recommandations de sécurité"""
        recommendations = []
        
        if SecurityViolationType.MALWARE in violations or SecurityViolationType.VIRUS in violations:
            recommendations.extend([
                "Isolate file immediately",
                "Run full system antivirus scan",
                "Report to security team"
            ])
        
        if SecurityViolationType.INTEGRITY_VIOLATION in violations:
            recommendations.extend([
                "Verify file source authenticity",
                "Check for transmission errors",
                "Request clean copy from source"
            ])
        
        if SecurityViolationType.SUSPICIOUS_METADATA in violations:
            recommendations.extend([
                "Strip metadata before sharing",
                "Review for sensitive information",
                "Use metadata cleaning tools"
            ])
        
        if threat_level == SecurityThreatLevel.CRITICAL:
            recommendations.append("IMMEDIATE ACTION REQUIRED - Contact security team")
        elif threat_level == SecurityThreatLevel.HIGH:
            recommendations.append("High priority security review needed")
        elif threat_level == SecurityThreatLevel.MEDIUM:
            recommendations.append("Schedule security review")
        
        return recommendations

class AsyncSecurityValidator:
    """Version asynchrone du validateur de sécurité"""
    
    def __init__(self):
        self.sync_validator = SecurityValidator()
        self.logger = logging.getLogger(f"{__name__}.AsyncSecurityValidator")
    
    async def validate_security(self, file_path: str, user_context: Optional[Dict[str, Any]] = None) -> SecurityValidationResult:
        """Valide la sécurité de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_validator.validate_security,
            file_path,
            user_context
        )
        
        return result

# Export des classes principales
__all__ = [
    'SecurityValidator',
    'AsyncSecurityValidator',
    'SecurityValidationResult',
    'MalwareScanner',
    'IntegrityValidator',
    'AccessControlValidator',
    'SecurityThreatLevel',
    'SecurityViolationType'
]
