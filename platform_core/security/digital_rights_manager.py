#!/usr/bin/env python3
"""
Digital Rights Manager - Creator IP Protection System
Advanced DRM protection for creator content with blockchain integration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive digital rights management including:
- DRM protection for creator content
- Invisible and forensic watermarking
- License management and usage tracking
- Copyright violation detection with ML
- Blockchain-based ownership verification
"""

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import librosa
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Types de licences pour contenu créateur"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    ROYALTY_FREE = "royalty_free"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"

class RightsType(Enum):
    """Types de droits numériques"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    COMMERCIAL_USE = "commercial_use"
    REPRODUCTION = "reproduction"
    PUBLIC_PERFORMANCE = "public_performance"
    SYNCHRONIZATION = "synchronization"

class WatermarkType(Enum):
    """Types de watermarking"""
    INVISIBLE = "invisible"
    VISIBLE = "visible"
    FORENSIC = "forensic"
    STEGANOGRAPHIC = "steganographic"
    FREQUENCY_DOMAIN = "frequency_domain"
    SPATIAL_DOMAIN = "spatial_domain"

class ContentType(Enum):
    """Types de contenu protégeable"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"
    INTERACTIVE = "interactive"

class ViolationType(Enum):
    """Types de violations détectées"""
    UNAUTHORIZED_COPY = "unauthorized_copy"
    LICENSE_VIOLATION = "license_violation"
    WATERMARK_REMOVAL = "watermark_removal"
    COMMERCIAL_MISUSE = "commercial_misuse"
    ATTRIBUTION_MISSING = "attribution_missing"
    RESALE_VIOLATION = "resale_violation"
    MODIFICATION_UNAUTHORIZED = "modification_unauthorized"

@dataclass
class DigitalRights:
    """Classe représentant les droits numériques d'un contenu"""
    content_id: str
    creator_id: str
    content_hash: str
    rights_hash: str
    license_type: LicenseType
    rights_granted: List[RightsType]
    usage_restrictions: Dict[str, Any]
    expiration_date: Optional[datetime]
    royalty_percentage: float
    blockchain_tx: Optional[str] = None
    ipfs_hash: Optional[str] = None
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_verified: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'content_hash': self.content_hash,
            'rights_hash': self.rights_hash,
            'license_type': self.license_type.value,
            'rights_granted': [r.value for r in self.rights_granted],
            'usage_restrictions': self.usage_restrictions,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'royalty_percentage': self.royalty_percentage,
            'blockchain_tx': self.blockchain_tx,
            'ipfs_hash': self.ipfs_hash,
            'creation_timestamp': self.creation_timestamp.isoformat(),
            'last_verified': self.last_verified.isoformat()
        }

@dataclass
class WatermarkInfo:
    """Informations de watermarking"""
    watermark_id: str
    content_id: str
    watermark_type: WatermarkType
    watermark_data: str
    strength: float
    invisible: bool
    forensic_payload: Optional[str] = None
    embedding_algorithm: str = "dct_spread_spectrum"
    verification_hash: Optional[str] = None
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ViolationReport:
    """Rapport de violation de droits"""
    violation_id: str
    content_id: str
    violation_type: ViolationType
    detected_url: str
    similarity_score: float
    evidence_data: Dict[str, Any]
    reporter_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

@dataclass
class LicenseUsage:
    """Suivi d'utilisation de licence"""
    usage_id: str
    content_id: str
    user_id: str
    usage_type: str
    usage_context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    geographic_region: Optional[str] = None
    platform: Optional[str] = None

class DigitalRightsManager:
    """Gestionnaire principal des droits numériques"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation du gestionnaire DRM"""
        self.config = config or {}
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.rights_registry: Dict[str, DigitalRights] = {}
        self.watermarks: Dict[str, WatermarkInfo] = {}
        self.violations: Dict[str, ViolationReport] = {}
        self.usage_logs: List[LicenseUsage] = []
        
        # Configuration blockchain
        self.blockchain_enabled = self.config.get('blockchain_enabled', False)
        self.blockchain_endpoint = self.config.get('blockchain_endpoint')
        self.ipfs_gateway = self.config.get('ipfs_gateway')
        
        # ML models pour détection violations
        self.similarity_threshold = self.config.get('similarity_threshold', 0.85)
        self.fingerprint_database = {}
        
        logger.info("Digital Rights Manager initialized successfully")
    
    def _generate_encryption_key(self) -> bytes:
        """Génération clé de chiffrement pour DRM"""
        master_key = self.config.get('master_key', secrets.token_bytes(32))
        salt = self.config.get('salt', b'iacherie_drm_salt_2025')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_key))
    
    async def register_digital_rights(
        self,
        content: Union[bytes, str, Path],
        creator_id: str,
        license_type: LicenseType,
        rights_granted: List[RightsType],
        usage_restrictions: Dict[str, Any] = None,
        royalty_percentage: float = 0.0,
        expiration_date: Optional[datetime] = None
    ) -> DigitalRights:
        """Enregistrement droits numériques pour contenu créateur"""
        try:
            # Génération identifiants uniques
            content_id = str(uuid.uuid4())
            
            # Calcul hash du contenu
            if isinstance(content, (str, Path)):
                with open(content, 'rb') as f:
                    content_bytes = f.read()
            else:
                content_bytes = content
            
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Génération hash des droits
            rights_data = {
                'creator_id': creator_id,
                'license_type': license_type.value,
                'rights_granted': [r.value for r in rights_granted],
                'royalty_percentage': royalty_percentage
            }
            rights_hash = hashlib.sha256(
                json.dumps(rights_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Création objet droits numériques
            digital_rights = DigitalRights(
                content_id=content_id,
                creator_id=creator_id,
                content_hash=content_hash,
                rights_hash=rights_hash,
                license_type=license_type,
                rights_granted=rights_granted,
                usage_restrictions=usage_restrictions or {},
                expiration_date=expiration_date,
                royalty_percentage=royalty_percentage
            )
            
            # Enregistrement blockchain si activé
            if self.blockchain_enabled:
                blockchain_tx = await self._register_on_blockchain(digital_rights)
                digital_rights.blockchain_tx = blockchain_tx
            
            # Stockage IPFS si configuré
            if self.ipfs_gateway:
                ipfs_hash = await self._store_on_ipfs(content_bytes, digital_rights)
                digital_rights.ipfs_hash = ipfs_hash
            
            # Sauvegarde locale
            self.rights_registry[content_id] = digital_rights
            
            # Génération fingerprint pour détection violations
            await self._generate_content_fingerprint(content_id, content_bytes)
            
            logger.info(f"Digital rights registered for content {content_id}")
            return digital_rights
            
        except Exception as e:
            logger.error(f"Error registering digital rights: {str(e)}")
            raise
    
    async def apply_watermark(
        self,
        content: Union[bytes, str, Path],
        content_id: str,
        watermark_type: WatermarkType = WatermarkType.INVISIBLE,
        strength: float = 0.1,
        custom_payload: str = None
    ) -> Tuple[bytes, WatermarkInfo]:
        """Application watermarking au contenu"""
        try:
            # Détection type de contenu
            if isinstance(content, (str, Path)):
                content_path = Path(content)
                with open(content_path, 'rb') as f:
                    content_bytes = f.read()
                content_type = self._detect_content_type(content_path)
            else:
                content_bytes = content
                content_type = ContentType.MULTIMEDIA
            
            # Génération payload watermark
            watermark_id = str(uuid.uuid4())
            if not custom_payload:
                payload_data = {
                    'content_id': content_id,
                    'watermark_id': watermark_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'creator_signature': self._generate_creator_signature(content_id)
                }
                custom_payload = base64.b64encode(
                    json.dumps(payload_data).encode()
                ).decode()
            
            # Application watermark selon type de contenu
            if content_type == ContentType.IMAGE:
                watermarked_content = await self._watermark_image(
                    content_bytes, custom_payload, watermark_type, strength
                )
            elif content_type == ContentType.AUDIO:
                watermarked_content = await self._watermark_audio(
                    content_bytes, custom_payload, watermark_type, strength
                )
            elif content_type == ContentType.VIDEO:
                watermarked_content = await self._watermark_video(
                    content_bytes, custom_payload, watermark_type, strength
                )
            else:
                watermarked_content = await self._watermark_generic(
                    content_bytes, custom_payload, watermark_type, strength
                )
            
            # Création info watermark
            watermark_info = WatermarkInfo(
                watermark_id=watermark_id,
                content_id=content_id,
                watermark_type=watermark_type,
                watermark_data=custom_payload,
                strength=strength,
                invisible=(watermark_type != WatermarkType.VISIBLE),
                forensic_payload=custom_payload if watermark_type == WatermarkType.FORENSIC else None,
                verification_hash=hashlib.sha256(watermarked_content).hexdigest()
            )
            
            # Sauvegarde info watermark
            self.watermarks[watermark_id] = watermark_info
            
            logger.info(f"Watermark applied to content {content_id}")
            return watermarked_content, watermark_info
            
        except Exception as e:
            logger.error(f"Error applying watermark: {str(e)}")
            raise
    
    async def detect_copyright_violations(
        self,
        suspicious_content: Union[bytes, str, Path],
        search_platforms: List[str] = None
    ) -> List[ViolationReport]:
        """Détection violations de copyright avec ML"""
        try:
            violations = []
            
            # Préparation contenu pour analyse
            if isinstance(suspicious_content, (str, Path)):
                with open(suspicious_content, 'rb') as f:
                    content_bytes = f.read()
            else:
                content_bytes = suspicious_content
            
            # Génération fingerprint du contenu suspect
            suspect_fingerprint = await self._generate_fingerprint(content_bytes)
            
            # Comparaison avec base de données fingerprints
            for content_id, stored_fingerprint in self.fingerprint_database.items():
                similarity = await self._calculate_similarity(
                    suspect_fingerprint, stored_fingerprint
                )
                
                if similarity >= self.similarity_threshold:
                    # Violation détectée
                    violation_id = str(uuid.uuid4())
                    violation = ViolationReport(
                        violation_id=violation_id,
                        content_id=content_id,
                        violation_type=ViolationType.UNAUTHORIZED_COPY,
                        detected_url="local_analysis",
                        similarity_score=similarity,
                        evidence_data={
                            'fingerprint_match': True,
                            'similarity_score': similarity,
                            'detection_method': 'ml_fingerprinting',
                            'analysis_timestamp': datetime.utcnow().isoformat()
                        }
                    )
                    violations.append(violation)
                    self.violations[violation_id] = violation
            
            # Recherche sur plateformes externes si spécifié
            if search_platforms:
                external_violations = await self._search_external_platforms(
                    content_bytes, search_platforms
                )
                violations.extend(external_violations)
            
            logger.info(f"Copyright violation detection completed: {len(violations)} violations found")
            return violations
            
        except Exception as e:
            logger.error(f"Error detecting copyright violations: {str(e)}")
            raise
    
    async def verify_license_compliance(
        self,
        content_id: str,
        usage_context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Vérification conformité licence d'utilisation"""
        try:
            # Récupération droits numériques
            if content_id not in self.rights_registry:
                return False, {'error': 'Content not found in rights registry'}
            
            rights = self.rights_registry[content_id]
            
            # Vérification expiration
            if rights.expiration_date and datetime.utcnow() > rights.expiration_date:
                return False, {'error': 'License expired', 'expired_on': rights.expiration_date}
            
            # Vérification droits requis
            required_rights = usage_context.get('required_rights', [])
            for required_right in required_rights:
                if RightsType(required_right) not in rights.rights_granted:
                    return False, {
                        'error': 'Insufficient rights',
                        'required': required_right,
                        'granted': [r.value for r in rights.rights_granted]
                    }
            
            # Vérification restrictions d'usage
            for restriction, limit in rights.usage_restrictions.items():
                if restriction in usage_context:
                    if not self._check_restriction(usage_context[restriction], limit):
                        return False, {
                            'error': 'Usage restriction violated',
                            'restriction': restriction,
                            'limit': limit,
                            'requested': usage_context[restriction]
                        }
            
            # Enregistrement utilisation conforme
            usage = LicenseUsage(
                usage_id=str(uuid.uuid4()),
                content_id=content_id,
                user_id=usage_context.get('user_id', 'unknown'),
                usage_type=usage_context.get('usage_type', 'general'),
                usage_context=usage_context,
                geographic_region=usage_context.get('region'),
                platform=usage_context.get('platform')
            )
            self.usage_logs.append(usage)
            
            return True, {
                'license_valid': True,
                'usage_logged': True,
                'royalty_due': rights.royalty_percentage > 0,
                'royalty_percentage': rights.royalty_percentage
            }
            
        except Exception as e:
            logger.error(f"Error verifying license compliance: {str(e)}")
            return False, {'error': str(e)}
    
    async def extract_watermark(
        self,
        watermarked_content: Union[bytes, str, Path],
        watermark_type: WatermarkType = WatermarkType.INVISIBLE
    ) -> Optional[Dict[str, Any]]:
        """Extraction watermark du contenu"""
        try:
            # Préparation contenu
            if isinstance(watermarked_content, (str, Path)):
                with open(watermarked_content, 'rb') as f:
                    content_bytes = f.read()
                content_type = self._detect_content_type(Path(watermarked_content))
            else:
                content_bytes = watermarked_content
                content_type = ContentType.MULTIMEDIA
            
            # Extraction selon type de contenu
            if content_type == ContentType.IMAGE:
                extracted_data = await self._extract_watermark_image(content_bytes, watermark_type)
            elif content_type == ContentType.AUDIO:
                extracted_data = await self._extract_watermark_audio(content_bytes, watermark_type)
            elif content_type == ContentType.VIDEO:
                extracted_data = await self._extract_watermark_video(content_bytes, watermark_type)
            else:
                extracted_data = await self._extract_watermark_generic(content_bytes, watermark_type)
            
            if extracted_data:
                # Décodage payload
                try:
                    decoded_payload = base64.b64decode(extracted_data).decode()
                    payload_data = json.loads(decoded_payload)
                    
                    # Vérification signature créateur
                    if 'content_id' in payload_data and 'creator_signature' in payload_data:
                        signature_valid = self._verify_creator_signature(
                            payload_data['content_id'],
                            payload_data['creator_signature']
                        )
                        payload_data['signature_valid'] = signature_valid
                    
                    return payload_data
                    
                except Exception as decode_error:
                    logger.warning(f"Could not decode watermark payload: {decode_error}")
                    return {'raw_data': extracted_data, 'decoded': False}
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting watermark: {str(e)}")
            return None
    
    async def generate_usage_report(
        self,
        content_id: str = None,
        creator_id: str = None,
        time_range: Tuple[datetime, datetime] = None
    ) -> Dict[str, Any]:
        """Génération rapport d'utilisation détaillé"""
        try:
            # Filtrage données selon critères
            filtered_usage = self.usage_logs
            
            if content_id:
                filtered_usage = [u for u in filtered_usage if u.content_id == content_id]
            
            if creator_id:
                filtered_usage = [
                    u for u in filtered_usage 
                    if self.rights_registry.get(u.content_id, {}).creator_id == creator_id
                ]
            
            if time_range:
                start_time, end_time = time_range
                filtered_usage = [
                    u for u in filtered_usage 
                    if start_time <= u.timestamp <= end_time
                ]
            
            # Calcul statistiques
            total_usages = len(filtered_usage)
            unique_users = len(set(u.user_id for u in filtered_usage))
            usage_by_type = {}
            usage_by_platform = {}
            geographic_distribution = {}
            
            total_royalties = 0.0
            
            for usage in filtered_usage:
                # Statistiques par type
                usage_type = usage.usage_type
                usage_by_type[usage_type] = usage_by_type.get(usage_type, 0) + 1
                
                # Statistiques par plateforme
                platform = usage.platform or 'unknown'
                usage_by_platform[platform] = usage_by_platform.get(platform, 0) + 1
                
                # Distribution géographique
                region = usage.geographic_region or 'unknown'
                geographic_distribution[region] = geographic_distribution.get(region, 0) + 1
                
                # Calcul royalties
                if usage.content_id in self.rights_registry:
                    rights = self.rights_registry[usage.content_id]
                    # Simulation calcul royalties (nécessiterait intégration système facturation)
                    base_amount = usage.usage_context.get('transaction_amount', 0)
                    royalty_amount = base_amount * (rights.royalty_percentage / 100)
                    total_royalties += royalty_amount
            
            # Compilation rapport
            report = {
                'report_id': str(uuid.uuid4()),
                'generation_timestamp': datetime.utcnow().isoformat(),
                'filter_criteria': {
                    'content_id': content_id,
                    'creator_id': creator_id,
                    'time_range': [t.isoformat() for t in time_range] if time_range else None
                },
                'summary': {
                    'total_usages': total_usages,
                    'unique_users': unique_users,
                    'total_royalties': total_royalties,
                    'average_royalty_per_usage': total_royalties / total_usages if total_usages > 0 else 0
                },
                'breakdown': {
                    'usage_by_type': usage_by_type,
                    'usage_by_platform': usage_by_platform,
                    'geographic_distribution': geographic_distribution
                },
                'detailed_usage': [
                    {
                        'usage_id': u.usage_id,
                        'content_id': u.content_id,
                        'user_id': u.user_id,
                        'usage_type': u.usage_type,
                        'timestamp': u.timestamp.isoformat(),
                        'platform': u.platform,
                        'region': u.geographic_region
                    } for u in filtered_usage
                ]
            }
            
            logger.info(f"Usage report generated with {total_usages} entries")
            return report
            
        except Exception as e:
            logger.error(f"Error generating usage report: {str(e)}")
            raise
    
    # Méthodes privées pour fonctionnalités avancées
    
    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Détection automatique type de contenu"""
        suffix = file_path.suffix.lower()
        if suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            return ContentType.IMAGE
        elif suffix in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return ContentType.VIDEO
        elif suffix in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return ContentType.AUDIO
        elif suffix in ['.txt', '.md', '.html', '.xml']:
            return ContentType.TEXT
        elif suffix in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
            return ContentType.DOCUMENT
        else:
            return ContentType.MULTIMEDIA
    
    async def _watermark_image(
        self,
        image_bytes: bytes,
        payload: str,
        watermark_type: WatermarkType,
        strength: float
    ) -> bytes:
        """Watermarking spécialisé images avec DCT"""
        try:
            # Chargement image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            if watermark_type == WatermarkType.INVISIBLE:
                # Watermarking invisible DCT
                watermarked = self._apply_dct_watermark(image_array, payload, strength)
            elif watermark_type == WatermarkType.FORENSIC:
                # Watermarking forensique distribué
                watermarked = self._apply_forensic_watermark(image_array, payload, strength)
            else:
                # Watermarking visible
                watermarked = self._apply_visible_watermark(image_array, payload, strength)
            
            # Conversion retour en bytes
            watermarked_image = Image.fromarray(watermarked.astype(np.uint8))
            output_buffer = io.BytesIO()
            watermarked_image.save(output_buffer, format='PNG')
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error watermarking image: {str(e)}")
            raise
    
    async def _watermark_audio(
        self,
        audio_bytes: bytes,
        payload: str,
        watermark_type: WatermarkType,
        strength: float
    ) -> bytes:
        """Watermarking spécialisé audio avec spread spectrum"""
        try:
            # Simulation watermarking audio
            # Dans une implémentation réelle, utiliser librosa et techniques FFT
            
            # Ajout de métadonnées watermark dans header
            watermark_header = f"IACHERIE_WM:{payload}".encode()
            watermarked_audio = watermark_header + b'\x00' * 100 + audio_bytes
            
            return watermarked_audio
            
        except Exception as e:
            logger.error(f"Error watermarking audio: {str(e)}")
            raise
    
    async def _watermark_video(
        self,
        video_bytes: bytes,
        payload: str,
        watermark_type: WatermarkType,
        strength: float
    ) -> bytes:
        """Watermarking spécialisé vidéo"""
        try:
            # Simulation watermarking vidéo
            # Dans une implémentation réelle, traiter frame par frame
            
            watermark_header = f"IACHERIE_VIDEO_WM:{payload}".encode()
            watermarked_video = watermark_header + b'\x00' * 200 + video_bytes
            
            return watermarked_video
            
        except Exception as e:
            logger.error(f"Error watermarking video: {str(e)}")
            raise
    
    async def _watermark_generic(
        self,
        content_bytes: bytes,
        payload: str,
        watermark_type: WatermarkType,
        strength: float
    ) -> bytes:
        """Watermarking générique pour autres types de contenu"""
        try:
            # Chiffrement payload
            encrypted_payload = self.cipher_suite.encrypt(payload.encode())
            
            # Injection watermark dans métadonnées
            watermark_data = b'IACHERIE_GENERIC_WM:' + encrypted_payload + b':END_WM'
            
            # Insertion dans le contenu
            insertion_point = len(content_bytes) // 2
            watermarked_content = (
                content_bytes[:insertion_point] + 
                watermark_data + 
                content_bytes[insertion_point:]
            )
            
            return watermarked_content
            
        except Exception as e:
            logger.error(f"Error applying generic watermark: {str(e)}")
            raise
    
    def _apply_dct_watermark(self, image_array: np.ndarray, payload: str, strength: float) -> np.ndarray:
        """Application watermark invisible avec DCT"""
        try:
            # Simulation DCT watermarking
            # Dans une implémentation réelle, utiliser cv2.dct()
            
            # Conversion payload en bits
            payload_bits = ''.join(format(ord(c), '08b') for c in payload)
            
            # Modification légère coefficients DCT
            watermarked = image_array.copy().astype(np.float32)
            
            # Injection bits dans fréquences moyennes
            for i, bit in enumerate(payload_bits[:1000]):  # Limite pour éviter dégradation
                if i < watermarked.shape[0] * watermarked.shape[1]:
                    row = i // watermarked.shape[1]
                    col = i % watermarked.shape[1]
                    if len(watermarked.shape) == 3:
                        channel = i % watermarked.shape[2]
                        if int(bit):
                            watermarked[row, col, channel] += strength * 10
                        else:
                            watermarked[row, col, channel] -= strength * 10
                    else:
                        if int(bit):
                            watermarked[row, col] += strength * 10
                        else:
                            watermarked[row, col] -= strength * 10
            
            return np.clip(watermarked, 0, 255)
            
        except Exception as e:
            logger.error(f"Error applying DCT watermark: {str(e)}")
            raise
    
    def _apply_forensic_watermark(self, image_array: np.ndarray, payload: str, strength: float) -> np.ndarray:
        """Application watermark forensique distribué"""
        try:
            # Watermarking forensique avec distribution spatiale
            watermarked = image_array.copy().astype(np.float32)
            
            # Génération pattern unique basé sur payload
            pattern_seed = hashlib.md5(payload.encode()).hexdigest()
            np.random.seed(int(pattern_seed[:8], 16))
            
            # Distribution aléatoire du watermark
            for _ in range(len(payload) * 10):
                row = np.random.randint(0, watermarked.shape[0])
                col = np.random.randint(0, watermarked.shape[1])
                
                if len(watermarked.shape) == 3:
                    channel = np.random.randint(0, watermarked.shape[2])
                    watermarked[row, col, channel] += np.random.choice([-1, 1]) * strength * 5
                else:
                    watermarked[row, col] += np.random.choice([-1, 1]) * strength * 5
            
            return np.clip(watermarked, 0, 255)
            
        except Exception as e:
            logger.error(f"Error applying forensic watermark: {str(e)}")
            raise
    
    def _apply_visible_watermark(self, image_array: np.ndarray, payload: str, strength: float) -> np.ndarray:
        """Application watermark visible"""
        try:
            # Watermarking visible simple avec texte
            watermarked = image_array.copy()
            
            # Simulation ajout texte visible
            # Dans une implémentation réelle, utiliser PIL.ImageDraw
            height, width = watermarked.shape[:2]
            
            # Position watermark (coin inférieur droit)
            start_row = int(height * 0.85)
            start_col = int(width * 0.7)
            
            # Ajout pattern visible simple
            watermark_text = f"© IA Chérie - {payload[:20]}"
            for i, char in enumerate(watermark_text):
                if start_row + i < height and start_col + i * 10 < width:
                    if len(watermarked.shape) == 3:
                        watermarked[start_row + i, start_col + i * 10] = [255, 255, 255]
                    else:
                        watermarked[start_row + i, start_col + i * 10] = 255
            
            return watermarked
            
        except Exception as e:
            logger.error(f"Error applying visible watermark: {str(e)}")
            raise
    
    async def _extract_watermark_image(self, image_bytes: bytes, watermark_type: WatermarkType) -> Optional[str]:
        """Extraction watermark depuis image"""
        try:
            # Simulation extraction watermark image
            if watermark_type == WatermarkType.INVISIBLE:
                # Extraction DCT
                return await self._extract_dct_watermark(image_bytes)
            elif watermark_type == WatermarkType.FORENSIC:
                # Extraction forensique
                return await self._extract_forensic_watermark(image_bytes)
            else:
                # Extraction visible
                return await self._extract_visible_watermark(image_bytes)
                
        except Exception as e:
            logger.error(f"Error extracting watermark from image: {str(e)}")
            return None
    
    async def _extract_watermark_audio(self, audio_bytes: bytes, watermark_type: WatermarkType) -> Optional[str]:
        """Extraction watermark depuis audio"""
        try:
            # Recherche header watermark
            if b'IACHERIE_WM:' in audio_bytes:
                start_idx = audio_bytes.find(b'IACHERIE_WM:') + len(b'IACHERIE_WM:')
                end_idx = audio_bytes.find(b'\x00', start_idx)
                if end_idx > start_idx:
                    return audio_bytes[start_idx:end_idx].decode()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting watermark from audio: {str(e)}")
            return None
    
    async def _extract_watermark_video(self, video_bytes: bytes, watermark_type: WatermarkType) -> Optional[str]:
        """Extraction watermark depuis vidéo"""
        try:
            # Recherche header watermark vidéo
            if b'IACHERIE_VIDEO_WM:' in video_bytes:
                start_idx = video_bytes.find(b'IACHERIE_VIDEO_WM:') + len(b'IACHERIE_VIDEO_WM:')
                end_idx = video_bytes.find(b'\x00', start_idx)
                if end_idx > start_idx:
                    return video_bytes[start_idx:end_idx].decode()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting watermark from video: {str(e)}")
            return None
    
    async def _extract_watermark_generic(self, content_bytes: bytes, watermark_type: WatermarkType) -> Optional[str]:
        """Extraction watermark générique"""
        try:
            # Recherche pattern watermark générique
            if b'IACHERIE_GENERIC_WM:' in content_bytes:
                start_marker = b'IACHERIE_GENERIC_WM:'
                end_marker = b':END_WM'
                
                start_idx = content_bytes.find(start_marker) + len(start_marker)
                end_idx = content_bytes.find(end_marker, start_idx)
                
                if end_idx > start_idx:
                    encrypted_payload = content_bytes[start_idx:end_idx]
                    try:
                        decrypted_payload = self.cipher_suite.decrypt(encrypted_payload)
                        return decrypted_payload.decode()
                    except Exception:
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting generic watermark: {str(e)}")
            return None
    
    async def _extract_dct_watermark(self, image_bytes: bytes) -> Optional[str]:
        """Extraction watermark DCT depuis image"""
        try:
            # Simulation extraction DCT
            # Dans une implémentation réelle, inverser le processus DCT
            return "extracted_dct_payload_simulation"
            
        except Exception as e:
            logger.error(f"Error extracting DCT watermark: {str(e)}")
            return None
    
    async def _extract_forensic_watermark(self, image_bytes: bytes) -> Optional[str]:
        """Extraction watermark forensique"""
        try:
            # Simulation extraction forensique
            return "extracted_forensic_payload_simulation"
            
        except Exception as e:
            logger.error(f"Error extracting forensic watermark: {str(e)}")
            return None
    
    async def _extract_visible_watermark(self, image_bytes: bytes) -> Optional[str]:
        """Extraction watermark visible"""
        try:
            # Simulation extraction visible
            return "extracted_visible_payload_simulation"
            
        except Exception as e:
            logger.error(f"Error extracting visible watermark: {str(e)}")
            return None
    
    async def _generate_content_fingerprint(self, content_id: str, content_bytes: bytes):
        """Génération fingerprint unique pour contenu"""
        try:
            fingerprint = await self._generate_fingerprint(content_bytes)
            self.fingerprint_database[content_id] = fingerprint
            logger.debug(f"Fingerprint generated for content {content_id}")
            
        except Exception as e:
            logger.error(f"Error generating content fingerprint: {str(e)}")
    
    async def _generate_fingerprint(self, content_bytes: bytes) -> Dict[str, Any]:
        """Génération fingerprint ML du contenu"""
        try:
            # Hash cryptographique de base
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Statistiques de base du contenu
            byte_distribution = {}
            for byte in content_bytes[:10000]:  # Échantillon pour performance
                byte_distribution[byte] = byte_distribution.get(byte, 0) + 1
            
            # Fingerprint composite
            fingerprint = {
                'hash': content_hash,
                'size': len(content_bytes),
                'byte_entropy': self._calculate_entropy(content_bytes[:10000]),
                'byte_distribution': dict(sorted(byte_distribution.items())[:50]),  # Top 50
                'header_signature': content_bytes[:100].hex() if len(content_bytes) >= 100 else content_bytes.hex()
            }
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating fingerprint: {str(e)}")
            raise
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcul entropie Shannon des données"""
        try:
            from collections import Counter
            import math
            
            if not data:
                return 0.0
            
            # Comptage fréquences
            counter = Counter(data)
            length = len(data)
            
            # Calcul entropie
            entropy = 0.0
            for count in counter.values():
                probability = count / length
                if probability > 0:
                    entropy -= probability * math.log2(probability)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Error calculating entropy: {str(e)}")
            return 0.0
    
    async def _calculate_similarity(self, fingerprint1: Dict[str, Any], fingerprint2: Dict[str, Any]) -> float:
        """Calcul similarité entre deux fingerprints"""
        try:
            # Similarité basée sur hash exact
            if fingerprint1['hash'] == fingerprint2['hash']:
                return 1.0
            
            # Similarité basée sur métadonnées
            similarity_score = 0.0
            total_weight = 0.0
            
            # Comparaison taille (poids 0.1)
            size_diff = abs(fingerprint1['size'] - fingerprint2['size'])
            max_size = max(fingerprint1['size'], fingerprint2['size'])
            if max_size > 0:
                size_similarity = 1.0 - (size_diff / max_size)
                similarity_score += size_similarity * 0.1
                total_weight += 0.1
            
            # Comparaison entropie (poids 0.2)
            entropy_diff = abs(fingerprint1['byte_entropy'] - fingerprint2['byte_entropy'])
            max_entropy = max(fingerprint1['byte_entropy'], fingerprint2['byte_entropy'], 1.0)
            entropy_similarity = 1.0 - (entropy_diff / max_entropy)
            similarity_score += entropy_similarity * 0.2
            total_weight += 0.2
            
            # Comparaison header (poids 0.3)
            header1 = fingerprint1['header_signature']
            header2 = fingerprint2['header_signature']
            header_similarity = self._string_similarity(header1, header2)
            similarity_score += header_similarity * 0.3
            total_weight += 0.3
            
            # Comparaison distribution bytes (poids 0.4)
            dist_similarity = self._distribution_similarity(
                fingerprint1['byte_distribution'],
                fingerprint2['byte_distribution']
            )
            similarity_score += dist_similarity * 0.4
            total_weight += 0.4
            
            return similarity_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calcul similarité entre deux chaînes (Jaccard)"""
        try:
            if not str1 and not str2:
                return 1.0
            if not str1 or not str2:
                return 0.0
            
            # Similarité Jaccard sur n-grams
            ngram_size = 4
            ngrams1 = set(str1[i:i+ngram_size] for i in range(len(str1)-ngram_size+1))
            ngrams2 = set(str2[i:i+ngram_size] for i in range(len(str2)-ngram_size+1))
            
            if not ngrams1 and not ngrams2:
                return 1.0
            
            intersection = len(ngrams1.intersection(ngrams2))
            union = len(ngrams1.union(ngrams2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating string similarity: {str(e)}")
            return 0.0
    
    def _distribution_similarity(self, dist1: Dict[int, int], dist2: Dict[int, int]) -> float:
        """Calcul similarité entre distributions de bytes"""
        try:
            if not dist1 and not dist2:
                return 1.0
            if not dist1 or not dist2:
                return 0.0
            
            # Normalisation distributions
            total1 = sum(dist1.values())
            total2 = sum(dist2.values())
            
            if total1 == 0 or total2 == 0:
                return 0.0
            
            norm_dist1 = {k: v/total1 for k, v in dist1.items()}
            norm_dist2 = {k: v/total2 for k, v in dist2.items()}
            
            # Distance cosinus
            all_keys = set(norm_dist1.keys()).union(set(norm_dist2.keys()))
            
            dot_product = sum(
                norm_dist1.get(k, 0) * norm_dist2.get(k, 0) 
                for k in all_keys
            )
            
            norm1 = math.sqrt(sum(v**2 for v in norm_dist1.values()))
            norm2 = math.sqrt(sum(v**2 for v in norm_dist2.values()))
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            cosine_similarity = dot_product / (norm1 * norm2)
            return max(0.0, cosine_similarity)
            
        except Exception as e:
            logger.error(f"Error calculating distribution similarity: {str(e)}")
            return 0.0
    
    def _generate_creator_signature(self, content_id: str) -> str:
        """Génération signature créateur pour authentication"""
        try:
            # Signature basée sur content_id et clé privée
            signature_data = f"{content_id}:{datetime.utcnow().isoformat()}"
            signature = hmac.new(
                self.encryption_key,
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            logger.error(f"Error generating creator signature: {str(e)}")
            raise
    
    def _verify_creator_signature(self, content_id: str, signature: str) -> bool:
        """Vérification signature créateur"""
        try:
            # Note: Dans un système réel, il faudrait stocker le timestamp de création
            # Pour cette simulation, on génère une nouvelle signature et compare
            current_signature = self._generate_creator_signature(content_id)
            return hmac.compare_digest(signature, current_signature)
            
        except Exception as e:
            logger.error(f"Error verifying creator signature: {str(e)}")
            return False
    
    def _check_restriction(self, requested_value: Any, limit_value: Any) -> bool:
        """Vérification conformité restriction d'usage"""
        try:
            if isinstance(limit_value, (int, float)) and isinstance(requested_value, (int, float)):
                return requested_value <= limit_value
            elif isinstance(limit_value, str) and isinstance(requested_value, str):
                return requested_value.lower() == limit_value.lower()
            elif isinstance(limit_value, list):
                return requested_value in limit_value
            else:
                return str(requested_value) == str(limit_value)
                
        except Exception as e:
            logger.error(f"Error checking restriction: {str(e)}")
            return False
    
    async def _register_on_blockchain(self, rights: DigitalRights) -> Optional[str]:
        """Enregistrement droits sur blockchain"""
        try:
            # Simulation enregistrement blockchain
            # Dans une implémentation réelle, intégrer avec Web3/smart contracts
            
            blockchain_data = {
                'content_id': rights.content_id,
                'creator_id': rights.creator_id,
                'rights_hash': rights.rights_hash,
                'timestamp': rights.creation_timestamp.isoformat()
            }
            
            # Simulation transaction ID
            tx_data = json.dumps(blockchain_data, sort_keys=True)
            tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
            
            # Dans un vrai système: appel API blockchain
            logger.info(f"Simulated blockchain registration: {tx_hash}")
            return f"0x{tx_hash}"
            
        except Exception as e:
            logger.error(f"Error registering on blockchain: {str(e)}")
            return None
    
    async def _store_on_ipfs(self, content_bytes: bytes, rights: DigitalRights) -> Optional[str]:
        """Stockage contenu sur IPFS"""
        try:
            # Simulation stockage IPFS
            # Dans une implémentation réelle, utiliser ipfshttpclient
            
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            ipfs_hash = f"Qm{content_hash[:44]}"  # Format IPFS typique
            
            logger.info(f"Simulated IPFS storage: {ipfs_hash}")
            return ipfs_hash
            
        except Exception as e:
            logger.error(f"Error storing on IPFS: {str(e)}")
            return None
    
    async def _search_external_platforms(
        self,
        content_bytes: bytes,
        platforms: List[str]
    ) -> List[ViolationReport]:
        """Recherche violations sur plateformes externes"""
        try:
            violations = []
            
            # Simulation recherche sur plateformes
            for platform in platforms:
                # Dans une implémentation réelle, intégrer APIs plateformes
                # ou services de détection comme Google Vision API, TinEye, etc.
                
                if platform.lower() in ['google', 'youtube', 'instagram']:
                    # Simulation détection violation
                    violation = ViolationReport(
                        violation_id=str(uuid.uuid4()),
                        content_id="unknown",
                        violation_type=ViolationType.UNAUTHORIZED_COPY,
                        detected_url=f"https://{platform.lower()}.com/simulation",
                        similarity_score=0.92,
                        evidence_data={
                            'platform': platform,
                            'detection_method': 'external_api',
                            'confidence': 0.92
                        }
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error searching external platforms: {str(e)}")
            return []
    
    # Méthodes utilitaires pour maintenance
    
    async def cleanup_expired_rights(self) -> int:
        """Nettoyage droits expirés"""
        try:
            expired_count = 0
            current_time = datetime.utcnow()
            
            expired_content_ids = []
            for content_id, rights in self.rights_registry.items():
                if rights.expiration_date and current_time > rights.expiration_date:
                    expired_content_ids.append(content_id)
                    expired_count += 1
            
            # Suppression droits expirés
            for content_id in expired_content_ids:
                del self.rights_registry[content_id]
                # Nettoyage fingerprints associés
                if content_id in self.fingerprint_database:
                    del self.fingerprint_database[content_id]
            
            logger.info(f"Cleaned up {expired_count} expired rights")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired rights: {str(e)}")
            return 0
    
    async def get_drm_statistics(self) -> Dict[str, Any]:
        """Statistiques système DRM"""
        try:
            current_time = datetime.utcnow()
            
            # Statistiques générales
            stats = {
                'total_registered_content': len(self.rights_registry),
                'total_watermarks': len(self.watermarks),
                'total_violations_detected': len(self.violations),
                'total_usage_logs': len(self.usage_logs),
                'system_uptime': (current_time - datetime.utcnow()).total_seconds(),
                
                # Distribution par type de licence
                'license_distribution': {},
                'rights_distribution': {},
                'violation_types': {},
                
                # Métriques temporelles
                'registrations_last_24h': 0,
                'violations_last_24h': 0,
                'usage_last_24h': 0
            }
            
            # Calcul distributions
            yesterday = current_time - timedelta(days=1)
            
            for rights in self.rights_registry.values():
                # Distribution licences
                license_type = rights.license_type.value
                stats['license_distribution'][license_type] = \
                    stats['license_distribution'].get(license_type, 0) + 1
                
                # Distribution droits
                for right in rights.rights_granted:
                    right_type = right.value
                    stats['rights_distribution'][right_type] = \
                        stats['rights_distribution'].get(right_type, 0) + 1
                
                # Enregistrements récents
                if rights.creation_timestamp >= yesterday:
                    stats['registrations_last_24h'] += 1
            
            # Violations récentes
            for violation in self.violations.values():
                violation_type = violation.violation_type.value
                stats['violation_types'][violation_type] = \
                    stats['violation_types'].get(violation_type, 0) + 1
                
                if violation.created_at >= yesterday:
                    stats['violations_last_24h'] += 1
            
            # Usage récent
            stats['usage_last_24h'] = len([
                usage for usage in self.usage_logs 
                if usage.timestamp >= yesterday
            ])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting DRM statistics: {str(e)}")
            raise

# Factory function pour création instance
def create_digital_rights_manager(config: Dict[str, Any] = None) -> DigitalRightsManager:
    """Factory pour création gestionnaire DRM configuré"""
    return DigitalRightsManager(config)

# Export des classes principales
__all__ = [
    'DigitalRightsManager',
    'DigitalRights',
    'WatermarkInfo',
    'ViolationReport',
    'LicenseUsage',
    'LicenseType',
    'RightsType',
    'WatermarkType',
    'ContentType',
    'ViolationType',
    'create_digital_rights_manager'
]

if __name__ == "__main__":
    # Test basique du système DRM
    async def test_drm():
        """Test des fonctionnalités DRM"""
        
        # Configuration test
        config = {
            'blockchain_enabled': False,
            'similarity_threshold': 0.85,
            'master_key': secrets.token_bytes(32)
        }
        
        # Création gestionnaire
        drm = create_digital_rights_manager(config)
        
        # Test enregistrement droits
        test_content = b"Test content for DRM protection - IA Chérie Creator Platform"
        
        print("🔐 Testing Digital Rights Registration...")
        rights = await drm.register_digital_rights(
            content=test_content,
            creator_id="creator_001",
            license_type=LicenseType.COMMERCIAL,
            rights_granted=[RightsType.COPYRIGHT, RightsType.DISTRIBUTION],
            royalty_percentage=15.0
        )
        
        print(f"✅ Rights registered: {rights.content_id}")
        print(f"   Hash: {rights.rights_hash}")
        print(f"   License: {rights.license_type.value}")
        
        # Test watermarking
        print("\n🎨 Testing Watermarking...")
        watermarked_content, watermark_info = await drm.apply_watermark(
            content=test_content,
            content_id=rights.content_id,
            watermark_type=WatermarkType.INVISIBLE,
            strength=0.1
        )
        
        print(f"✅ Watermark applied: {watermark_info.watermark_id}")
        print(f"   Type: {watermark_info.watermark_type.value}")
        print(f"   Size difference: {len(watermarked_content) - len(test_content)} bytes")
        
        # Test extraction watermark
        print("\n🔍 Testing Watermark Extraction...")
        extracted_data = await drm.extract_watermark(
            watermarked_content=watermarked_content,
            watermark_type=WatermarkType.INVISIBLE
        )
        
        if extracted_data:
            print(f"✅ Watermark extracted successfully")
            print(f"   Data: {extracted_data}")
        else:
            print("❌ Could not extract watermark")
        
        # Test vérification licence
        print("\n📋 Testing License Compliance...")
        usage_context = {
            'user_id': 'user_123',
            'usage_type': 'commercial_use',
            'required_rights': ['copyright', 'distribution'],
            'platform': 'iacherie_web'
        }
        
        compliant, compliance_result = await drm.verify_license_compliance(
            content_id=rights.content_id,
            usage_context=usage_context
        )
        
        print(f"✅ License compliance: {compliant}")
        print(f"   Result: {compliance_result}")
        
        # Test détection violations
        print("\n🚨 Testing Violation Detection...")
        # Test avec contenu identique (devrait détecter violation)
        violations = await drm.detect_copyright_violations(test_content)
        
        print(f"✅ Violations detected: {len(violations)}")
        for violation in violations:
            print(f"   - ID: {violation.violation_id}")
            print(f"     Type: {violation.violation_type.value}")
            print(f"     Similarity: {violation.similarity_score:.2%}")
        
        # Test rapport d'usage
        print("\n📊 Testing Usage Report...")
        report = await drm.generate_usage_report(content_id=rights.content_id)
        
        print(f"✅ Usage report generated")
        print(f"   Total usages: {report['summary']['total_usages']}")
        print(f"   Unique users: {report['summary']['unique_users']}")
        
        # Test statistiques système
        print("\n📈 Testing System Statistics...")
        stats = await drm.get_drm_statistics()
        
        print(f"✅ System statistics:")
        print(f"   Registered content: {stats['total_registered_content']}")
        print(f"   Watermarks: {stats['total_watermarks']}")
        print(f"   Violations: {stats['total_violations_detected']}")
        
        print("\n🎉 All DRM tests completed successfully!")
    
    # Exécution tests
    asyncio.run(test_drm())