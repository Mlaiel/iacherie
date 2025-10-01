# 🔒 Digital Rights Management: Blockchain-Based Copyright Protection
"""
Digital Rights Management - IA Chéries Integrations
==============================================
Enterprise digital rights management providing blockchain-based copyright protection,
NFT validation, smart contracts, and automated royalty distribution for IA Chéries
creator platform with advanced DRM and content protection systems.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import web3
from web3 import Web3
import ipfshttpclient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import redis
from celery import Celery
import boto3

# Configuration
Base = declarative_base()
logger = logging.getLogger(__name__)

class RightsType(Enum):
    """Types de droits numériques"""
    COPYRIGHT = "copyright"
    USAGE = "usage"
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    COMMERCIAL = "commercial"
    ATTRIBUTION = "attribution"

class LicenseType(Enum):
    """Types de licences"""
    ALL_RIGHTS_RESERVED = "all_rights_reserved"
    CREATIVE_COMMONS_BY = "cc_by"
    CREATIVE_COMMONS_BY_SA = "cc_by_sa"
    CREATIVE_COMMONS_BY_NC = "cc_by_nc"
    CREATIVE_COMMONS_BY_ND = "cc_by_nd"
    MIT = "mit"
    GPL = "gpl"
    CUSTOM = "custom"

class DRMAction(Enum):
    """Actions DRM"""
    REGISTER = "register"
    VERIFY = "verify"
    TRANSFER = "transfer"
    REVOKE = "revoke"
    LICENSE = "license"
    VIOLATE = "violate"

@dataclass
class DigitalRights:
    """Structure droits numériques"""
    content_id: str
    owner_id: str
    rights_hash: str
    license_type: LicenseType
    rights_granted: List[RightsType]
    usage_restrictions: Dict[str, Any]
    royalty_percentage: float
    expiration_date: Optional[datetime]
    metadata: Dict[str, Any]
    blockchain_tx: Optional[str]
    nft_token_id: Optional[str]
    created_at: datetime

@dataclass
class WatermarkInfo:
    """Information watermark"""
    watermark_id: str
    content_id: str
    watermark_type: str
    visibility: str  # visible, invisible
    position: Dict[str, Any]
    strength: float
    metadata: Dict[str, Any]

@dataclass
class ViolationReport:
    """Rapport violation copyright"""
    violation_id: str
    original_content_id: str
    infringing_url: str
    platform: str
    similarity_score: float
    violation_type: str
    status: str
    reported_at: datetime
    evidence: Dict[str, Any]

class DigitalRightsModel(Base):
    """Modèle database droits numériques"""
    __tablename__ = 'digital_rights'
    
    id = Column(Integer, primary_key=True)
    content_id = Column(String(255), nullable=False, index=True)
    owner_id = Column(String(255), nullable=False)
    rights_hash = Column(String(255), nullable=False, unique=True)
    license_type = Column(String(50), nullable=False)
    rights_granted = Column(JSON)
    usage_restrictions = Column(JSON)
    royalty_percentage = Column(Float, default=0.0)
    expiration_date = Column(DateTime)
    meta_data = Column(JSON)
    blockchain_tx = Column(String(255))
    nft_token_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class WatermarkModel(Base):
    """Modèle database watermarks"""
    __tablename__ = 'watermarks'
    
    id = Column(Integer, primary_key=True)
    watermark_id = Column(String(255), nullable=False, unique=True)
    content_id = Column(String(255), nullable=False, index=True)
    watermark_type = Column(String(50), nullable=False)
    visibility = Column(String(20), nullable=False)
    position = Column(JSON)
    strength = Column(Float, default=0.5)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ViolationModel(Base):
    """Modèle database violations"""
    __tablename__ = 'copyright_violations'
    
    id = Column(Integer, primary_key=True)
    violation_id = Column(String(255), nullable=False, unique=True)
    original_content_id = Column(String(255), nullable=False, index=True)
    infringing_url = Column(String(1000), nullable=False)
    platform = Column(String(100), nullable=False)
    similarity_score = Column(Float, nullable=False)
    violation_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    reported_at = Column(DateTime, default=datetime.utcnow)
    evidence = Column(JSON)

class DigitalRightsManager:
    """
    Gestionnaire droits numériques enterprise avec blockchain
    
    Fonctionnalités:
    - Enregistrement copyright blockchain
    - NFT validation et authentification
    - Smart contracts droits d'auteur
    - Watermarking intelligent (visible/invisible)
    - Détection violations automatisée
    - Distribution royalties automatique
    - Licensing système flexible
    - DMCA takedown automation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_engine = create_engine(config.get('database_url', 'sqlite:///digital_rights.db'))
        Base.metadata.create_all(self.db_engine)
        self.Session = sessionmaker(bind=self.db_engine)
        
        # Blockchain initialization
        self._init_blockchain()
        
        # IPFS initialization
        self._init_ipfs()
        
        # Services initialization
        self._init_services()
        
        # Encryption setup
        self._init_encryption()
        
        # Métriques
        self.metrics = {
            'total_registrations': 0,
            'violations_detected': 0,
            'royalties_distributed': 0.0,
            'nfts_created': 0,
            'watermarks_applied': 0
        }
        
        logger.info("DigitalRightsManager initialisé avec succès")
    
    def _init_blockchain(self):
        """Initialisation connexion blockchain"""
        try:
            # Web3 connection (Ethereum/Polygon)
            blockchain_url = self.config.get('blockchain_url', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
            self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
            
            # Smart contract setup
            self.contract_address = self.config.get('contract_address')
            self.contract_abi = self.config.get('contract_abi', [])
            
            if self.contract_address and self.contract_abi:
                self.drm_contract = self.w3.eth.contract(
                    address=self.contract_address,
                    abi=self.contract_abi
                )
            else:
                self.drm_contract = None
                logger.warning("Smart contract non configuré")
            
            # Wallet setup
            self.private_key = self.config.get('private_key')
            if self.private_key:
                self.account = self.w3.eth.account.from_key(self.private_key)
            else:
                self.account = None
                logger.warning("Wallet privé non configuré")
            
            logger.info(f"Blockchain connecté: {self.w3.is_connected()}")
            
        except Exception as e:
            logger.error(f"Erreur initialisation blockchain: {e}")
            self.w3 = None
            self.drm_contract = None
            self.account = None
    
    def _init_ipfs(self):
        """Initialisation IPFS"""
        try:
            # IPFS client
            ipfs_host = self.config.get('ipfs_host', '/ip4/127.0.0.1/tcp/5001/http')
            self.ipfs_client = ipfshttpclient.connect(ipfs_host)
            
            # Test connexion
            version = self.ipfs_client.version()
            logger.info(f"IPFS connecté: version {version['Version']}")
            
        except Exception as e:
            logger.error(f"Erreur connexion IPFS: {e}")
            self.ipfs_client = None
    
    def _init_services(self):
        """Initialisation services externes"""
        try:
            # Redis pour cache
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
            
            # Celery pour tasks async
            self.celery_app = Celery(
                'digital_rights',
                broker=self.config.get('celery_broker', 'redis://localhost:6379/0')
            )
            
            # AWS services
            self.s3_client = boto3.client('s3') if self.config.get('aws_enabled') else None
            
            logger.info("Services externes initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
    
    def _init_encryption(self):
        """Initialisation chiffrement"""
        try:
            # Symmetric encryption
            encryption_key = self.config.get('encryption_key')
            if encryption_key:
                self.cipher_suite = Fernet(encryption_key)
            else:
                self.cipher_suite = Fernet(Fernet.generate_key())
            
            # RSA key pair pour signatures
            self.private_key_rsa = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key_rsa = self.private_key_rsa.public_key()
            
            logger.info("Chiffrement initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation chiffrement: {e}")
    
    async def register_digital_rights(self, content_data: bytes, owner_id: str,
                                    license_type: LicenseType, rights_granted: List[RightsType],
                                    usage_restrictions: Dict[str, Any] = None,
                                    royalty_percentage: float = 0.0) -> DigitalRights:
        """
        Enregistrement droits numériques avec blockchain
        
        Args:
            content_data: Données du contenu
            owner_id: ID propriétaire
            license_type: Type de licence
            rights_granted: Droits accordés
            usage_restrictions: Restrictions d'usage
            royalty_percentage: Pourcentage royalties
            
        Returns:
            DigitalRights: Droits enregistrés
        """
        try:
            # Génération hash contenu
            content_hash = hashlib.sha256(content_data).hexdigest()
            content_id = f"content_{content_hash[:16]}"
            
            # Génération hash droits unique
            rights_data = {
                'content_hash': content_hash,
                'owner_id': owner_id,
                'license_type': license_type.value,
                'rights_granted': [r.value for r in rights_granted],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            rights_json = json.dumps(rights_data, sort_keys=True)
            rights_hash = hashlib.sha256(rights_json.encode()).hexdigest()
            
            # Upload contenu sur IPFS
            ipfs_hash = None
            if self.ipfs_client:
                try:
                    ipfs_result = self.ipfs_client.add_bytes(content_data)
                    ipfs_hash = ipfs_result
                    logger.info(f"Contenu uploadé sur IPFS: {ipfs_hash}")
                except Exception as e:
                    logger.error(f"Erreur upload IPFS: {e}")
            
            # Enregistrement blockchain
            blockchain_tx = None
            nft_token_id = None
            
            if self.drm_contract and self.account:
                try:
                    # Création transaction smart contract
                    nonce = self.w3.eth.get_transaction_count(self.account.address)
                    tx_data = self.drm_contract.functions.registerCopyright(
                        content_hash,
                        owner_id,
                        rights_hash,
                        ipfs_hash or ""
                    ).build_transaction({
                        'from': self.account.address,
                        'nonce': nonce,
                        'gas': 200000,
                        'gasPrice': self.w3.to_wei('20', 'gwei')
                    })
                    
                    # Signature et envoi
                    signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
                    tx_receipt = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    blockchain_tx = tx_receipt.hex()
                    
                    # Génération NFT si configuré
                    if self.config.get('auto_mint_nft', False):
                        nft_token_id = await self._mint_nft(content_hash, owner_id, ipfs_hash)
                    
                    logger.info(f"Droits enregistrés blockchain: {blockchain_tx}")
                    
                except Exception as e:
                    logger.error(f"Erreur enregistrement blockchain: {e}")
            
            # Création objet droits
            digital_rights = DigitalRights(
                content_id=content_id,
                owner_id=owner_id,
                rights_hash=rights_hash,
                license_type=license_type,
                rights_granted=rights_granted,
                usage_restrictions=usage_restrictions or {},
                royalty_percentage=royalty_percentage,
                expiration_date=None,
                metadata={
                    'content_hash': content_hash,
                    'ipfs_hash': ipfs_hash,
                    'original_size': len(content_data),
                    'registration_timestamp': datetime.utcnow().isoformat()
                },
                blockchain_tx=blockchain_tx,
                nft_token_id=nft_token_id,
                created_at=datetime.utcnow()
            )
            
            # Sauvegarde database
            await self._save_digital_rights(digital_rights)
            
            # Mise à jour métriques
            self.metrics['total_registrations'] += 1
            if nft_token_id:
                self.metrics['nfts_created'] += 1
            
            logger.info(f"Droits numériques enregistrés: {content_id}")
            
            return digital_rights
            
        except Exception as e:
            logger.error(f"Erreur enregistrement droits: {e}")
            raise
    
    async def apply_watermark(self, content_data: bytes, content_id: str,
                            watermark_type: str = "visible", 
                            position: Dict[str, Any] = None,
                            strength: float = 0.5) -> tuple[bytes, WatermarkInfo]:
        """
        Application watermark sur contenu
        
        Args:
            content_data: Données contenu original
            content_id: ID du contenu
            watermark_type: Type watermark (visible/invisible)
            position: Position watermark
            strength: Force watermark (0.0-1.0)
            
        Returns:
            tuple[bytes, WatermarkInfo]: Contenu watermarké et info
        """
        try:
            watermark_id = f"wm_{uuid.uuid4().hex[:12]}"
            
            if watermark_type == "visible":
                watermarked_data = await self._apply_visible_watermark(
                    content_data, content_id, position, strength
                )
            else:  # invisible
                watermarked_data = await self._apply_invisible_watermark(
                    content_data, content_id, strength
                )
            
            # Création info watermark
            watermark_info = WatermarkInfo(
                watermark_id=watermark_id,
                content_id=content_id,
                watermark_type=watermark_type,
                visibility=watermark_type,
                position=position or {},
                strength=strength,
                metadata={
                    'applied_at': datetime.utcnow().isoformat(),
                    'original_size': len(content_data),
                    'watermarked_size': len(watermarked_data)
                }
            )
            
            # Sauvegarde database
            await self._save_watermark_info(watermark_info)
            
            # Mise à jour métriques
            self.metrics['watermarks_applied'] += 1
            
            logger.info(f"Watermark appliqué: {watermark_id}")
            
            return watermarked_data, watermark_info
            
        except Exception as e:
            logger.error(f"Erreur application watermark: {e}")
            raise
    
    async def _apply_visible_watermark(self, content_data: bytes, content_id: str,
                                     position: Dict[str, Any], strength: float) -> bytes:
        """Application watermark visible"""
        try:
            # Détection type contenu
            if content_data.startswith(b'\xff\xd8\xff'):  # JPEG
                return await self._watermark_image(content_data, content_id, position, strength)
            elif content_data.startswith(b'\x89PNG'):  # PNG
                return await self._watermark_image(content_data, content_id, position, strength)
            elif b'ftyp' in content_data[:32]:  # MP4
                return await self._watermark_video(content_data, content_id, position, strength)
            else:
                # Fallback: watermark textuel
                return await self._watermark_text(content_data, content_id)
                
        except Exception as e:
            logger.error(f"Erreur watermark visible: {e}")
            return content_data
    
    async def _watermark_image(self, image_data: bytes, content_id: str,
                             position: Dict[str, Any], strength: float) -> bytes:
        """Watermark image"""
        try:
            # Ouverture image
            image = Image.open(io.BytesIO(image_data))
            
            # Création watermark text
            watermark_text = f"© IA Chéries - {content_id[:8]}"
            
            # Préparation watermark
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Création layer watermark
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # Configuration police
            try:
                font_size = max(12, min(image.size) // 40)
                # Utilisation police système basique
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Position watermark
            text_width = len(watermark_text) * 8  # Approximation
            text_height = 16
            
            if position and 'x' in position and 'y' in position:
                x, y = position['x'], position['y']
            else:
                # Position par défaut: coin bas-droit
                x = image.size[0] - text_width - 10
                y = image.size[1] - text_height - 10
            
            # Couleur avec transparence basée sur strength
            opacity = int(255 * strength)
            text_color = (255, 255, 255, opacity)
            
            # Application watermark
            draw.text((x, y), watermark_text, font=font, fill=text_color)
            
            # Composition finale
            watermarked = Image.alpha_composite(image, watermark_layer)
            
            # Conversion retour format original
            if watermarked.mode != 'RGB':
                watermarked = watermarked.convert('RGB')
            
            # Sauvegarde en bytes
            import io
            buffer = io.BytesIO()
            watermarked.save(buffer, format='JPEG', quality=95)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Erreur watermark image: {e}")
            return image_data
    
    async def _apply_invisible_watermark(self, content_data: bytes, content_id: str,
                                       strength: float) -> bytes:
        """Application watermark invisible (stéganographie)"""
        try:
            # Détection type contenu
            if content_data.startswith(b'\xff\xd8\xff') or content_data.startswith(b'\x89PNG'):
                return await self._steganography_image(content_data, content_id, strength)
            else:
                # Watermark métadonnées pour autres types
                return await self._metadata_watermark(content_data, content_id)
                
        except Exception as e:
            logger.error(f"Erreur watermark invisible: {e}")
            return content_data
    
    async def _steganography_image(self, image_data: bytes, content_id: str, strength: float) -> bytes:
        """Stéganographie sur image"""
        try:
            import io
            
            # Conversion numpy array
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            img_array = np.array(image)
            
            # Message à cacher
            watermark_message = f"IA CHÉRIES:{content_id}:{datetime.utcnow().isoformat()}"
            
            # Conversion message en binaire
            binary_message = ''.join(format(ord(char), '08b') for char in watermark_message)
            binary_message += '1111111111111110'  # Marqueur fin
            
            # Application LSB (Least Significant Bit)
            flat_img = img_array.flatten()
            
            if len(binary_message) > len(flat_img):
                logger.warning("Message trop long pour stéganographie")
                return image_data
            
            # Modification LSB
            for i, bit in enumerate(binary_message):
                flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
            
            # Reconstruction image
            watermarked_array = flat_img.reshape(img_array.shape)
            watermarked_image = Image.fromarray(watermarked_array.astype('uint8'))
            
            # Sauvegarde
            buffer = io.BytesIO()
            watermarked_image.save(buffer, format='PNG')  # PNG pour préserver qualité
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Erreur stéganographie: {e}")
            return image_data
    
    async def detect_copyright_violation(self, suspected_content: bytes,
                                       platform: str, source_url: str) -> Optional[ViolationReport]:
        """
        Détection violation copyright
        
        Args:
            suspected_content: Contenu suspect
            platform: Plateforme source
            source_url: URL source
            
        Returns:
            Optional[ViolationReport]: Rapport violation si détectée
        """
        try:
            # Hash contenu suspect
            suspected_hash = hashlib.sha256(suspected_content).hexdigest()
            
            # Recherche contenus originaux similaires
            similar_contents = await self._find_similar_content(suspected_content)
            
            if not similar_contents:
                return None
            
            # Évaluation violation pour chaque contenu similaire
            for original_content_id, similarity_score in similar_contents:
                
                if similarity_score >= 0.8:  # Seuil violation
                    
                    # Vérification droits
                    rights = await self._get_digital_rights(original_content_id)
                    if not rights:
                        continue
                    
                    # Génération rapport violation
                    violation_id = f"viol_{uuid.uuid4().hex[:12]}"
                    
                    violation_report = ViolationReport(
                        violation_id=violation_id,
                        original_content_id=original_content_id,
                        infringing_url=source_url,
                        platform=platform,
                        similarity_score=similarity_score,
                        violation_type="copyright_infringement",
                        status="detected",
                        reported_at=datetime.utcnow(),
                        evidence={
                            'original_hash': rights.metadata.get('content_hash'),
                            'suspected_hash': suspected_hash,
                            'similarity_algorithm': 'perceptual_hash',
                            'detection_timestamp': datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Sauvegarde violation
                    await self._save_violation_report(violation_report)
                    
                    # Lancement actions automatiques
                    await self._trigger_violation_actions(violation_report, rights)
                    
                    # Mise à jour métriques
                    self.metrics['violations_detected'] += 1
                    
                    logger.info(f"Violation détectée: {violation_id} (score: {similarity_score:.3f})")
                    
                    return violation_report
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection violation: {e}")
            return None
    
    async def _find_similar_content(self, content_data: bytes) -> List[tuple[str, float]]:
        """Recherche contenus similaires"""
        try:
            similar_contents = []
            
            # Hash perceptuel du contenu suspect
            if content_data.startswith(b'\xff\xd8\xff') or content_data.startswith(b'\x89PNG'):
                # Image: hash perceptuel
                import io
                from PIL import Image
                import imagehash
                
                image = Image.open(io.BytesIO(content_data))
                suspected_hash = str(imagehash.phash(image))
                
                # Comparaison avec database (simulation)
                session = self.Session()
                all_rights = session.query(DigitalRightsModel).all()
                
                for rights in all_rights:
                    # Récupération hash original (simulation)
                    original_hash = rights.metadata.get('perceptual_hash')
                    if not original_hash:
                        continue
                    
                    # Calcul distance Hamming
                    distance = sum(c1 != c2 for c1, c2 in zip(suspected_hash, original_hash))
                    max_distance = len(suspected_hash)
                    similarity = 1.0 - (distance / max_distance)
                    
                    if similarity >= 0.7:  # Seuil similarité
                        similar_contents.append((rights.content_id, similarity))
                
                session.close()
            
            else:
                # Autres types: hash standard
                suspected_hash = hashlib.sha256(content_data).hexdigest()
                
                session = self.Session()
                matching_rights = session.query(DigitalRightsModel)\
                                       .filter(DigitalRightsModel.metadata.contains(
                                           {'content_hash': suspected_hash}
                                       )).all()
                
                for rights in matching_rights:
                    similar_contents.append((rights.content_id, 1.0))  # Match exact
                
                session.close()
            
            return sorted(similar_contents, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Erreur recherche similarité: {e}")
            return []
    
    async def _trigger_violation_actions(self, violation_report: ViolationReport,
                                       rights: DigitalRights):
        """Déclenchement actions violation"""
        try:
            # DMCA takedown automatique
            if self.config.get('auto_dmca_enabled', False):
                await self._send_dmca_takedown(violation_report)
            
            # Notification propriétaire
            await self._notify_rights_owner(violation_report, rights)
            
            # Blocage contenu si configuré
            if self.config.get('auto_block_enabled', False):
                await self._block_infringing_content(violation_report)
            
            # Logging action
            logger.info(f"Actions violation déclenchées: {violation_report.violation_id}")
            
        except Exception as e:
            logger.error(f"Erreur actions violation: {e}")
    
    async def generate_license_agreement(self, content_id: str, licensee_id: str,
                                       license_terms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération accord de licence automatique
        
        Args:
            content_id: ID du contenu
            licensee_id: ID du licensié
            license_terms: Termes de la licence
            
        Returns:
            Dict[str, Any]: Accord de licence généré
        """
        try:
            # Récupération droits originaux
            rights = await self._get_digital_rights(content_id)
            if not rights:
                raise ValueError(f"Droits non trouvés pour contenu: {content_id}")
            
            # Génération ID licence unique
            license_id = f"lic_{uuid.uuid4().hex[:12]}"
            
            # Création accord de licence
            license_agreement = {
                'license_id': license_id,
                'content_id': content_id,
                'licensor_id': rights.owner_id,
                'licensee_id': licensee_id,
                'license_type': rights.license_type.value,
                'granted_rights': [r.value for r in rights.rights_granted],
                'restrictions': rights.usage_restrictions,
                'terms': license_terms,
                'royalty_percentage': rights.royalty_percentage,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': license_terms.get('expiration_date'),
                'status': 'active',
                'blockchain_tx': None  # À remplir si enregistrement blockchain
            }
            
            # Signature numérique
            agreement_json = json.dumps(license_agreement, sort_keys=True)
            signature = self._sign_document(agreement_json)
            license_agreement['digital_signature'] = signature
            
            # Enregistrement blockchain si configuré
            if self.config.get('blockchain_licensing', False):
                tx_hash = await self._register_license_blockchain(license_agreement)
                license_agreement['blockchain_tx'] = tx_hash
            
            # Sauvegarde database
            await self._save_license_agreement(license_agreement)
            
            logger.info(f"Accord de licence généré: {license_id}")
            
            return license_agreement
            
        except Exception as e:
            logger.error(f"Erreur génération licence: {e}")
            raise
    
    async def distribute_royalties(self, content_id: str, revenue: float,
                                 distribution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribution automatique des royalties
        
        Args:
            content_id: ID du contenu
            revenue: Revenus à distribuer
            distribution_data: Données distribution
            
        Returns:
            Dict[str, Any]: Résultat distribution
        """
        try:
            # Récupération droits
            rights = await self._get_digital_rights(content_id)
            if not rights:
                raise ValueError(f"Droits non trouvés: {content_id}")
            
            # Calcul royalties
            royalty_amount = revenue * (rights.royalty_percentage / 100.0)
            platform_fee = revenue - royalty_amount
            
            # Récupération licences actives
            active_licenses = await self._get_active_licenses(content_id)
            
            # Distribution aux licensiés
            distribution_result = {
                'content_id': content_id,
                'total_revenue': revenue,
                'royalty_amount': royalty_amount,
                'platform_fee': platform_fee,
                'distributions': [],
                'processed_at': datetime.utcnow().isoformat()
            }
            
            if active_licenses:
                # Distribution proportionnelle aux licensiés
                license_share = royalty_amount / len(active_licenses)
                
                for license_agreement in active_licenses:
                    distribution = {
                        'licensee_id': license_agreement['licensee_id'],
                        'license_id': license_agreement['license_id'],
                        'amount': license_share,
                        'status': 'pending'
                    }
                    
                    # Traitement paiement
                    if await self._process_royalty_payment(distribution):
                        distribution['status'] = 'completed'
                    else:
                        distribution['status'] = 'failed'
                    
                    distribution_result['distributions'].append(distribution)
            
            else:
                # Tout aux propriétaires originaux
                owner_distribution = {
                    'owner_id': rights.owner_id,
                    'amount': royalty_amount,
                    'status': 'pending'
                }
                
                if await self._process_royalty_payment(owner_distribution):
                    owner_distribution['status'] = 'completed'
                else:
                    owner_distribution['status'] = 'failed'
                
                distribution_result['distributions'].append(owner_distribution)
            
            # Sauvegarde transaction
            await self._save_royalty_distribution(distribution_result)
            
            # Mise à jour métriques
            self.metrics['royalties_distributed'] += royalty_amount
            
            logger.info(f"Royalties distribuées: {content_id} - {royalty_amount:.2f}")
            
            return distribution_result
            
        except Exception as e:
            logger.error(f"Erreur distribution royalties: {e}")
            raise
    
    def _sign_document(self, document: str) -> str:
        """Signature numérique document"""
        try:
            document_bytes = document.encode('utf-8')
            signature = self.private_key_rsa.sign(
                document_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Erreur signature document: {e}")
            return ""
    
    def verify_document_signature(self, document: str, signature: str) -> bool:
        """Vérification signature numérique"""
        try:
            document_bytes = document.encode('utf-8')
            signature_bytes = base64.b64decode(signature)
            
            self.public_key_rsa.verify(
                signature_bytes,
                document_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
            
        except Exception:
            return False
    
    async def get_content_rights_info(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Récupération informations droits contenu"""
        try:
            session = self.Session()
            
            rights_record = session.query(DigitalRightsModel)\
                                 .filter(DigitalRightsModel.content_id == content_id)\
                                 .first()
            
            if not rights_record:
                session.close()
                return None
            
            # Récupération watermarks
            watermarks = session.query(WatermarkModel)\
                              .filter(WatermarkModel.content_id == content_id)\
                              .all()
            
            # Récupération violations
            violations = session.query(ViolationModel)\
                              .filter(ViolationModel.original_content_id == content_id)\
                              .all()
            
            session.close()
            
            # Compilation informations
            rights_info = {
                'content_id': rights_record.content_id,
                'owner_id': rights_record.owner_id,
                'rights_hash': rights_record.rights_hash,
                'license_type': rights_record.license_type,
                'rights_granted': rights_record.rights_granted,
                'usage_restrictions': rights_record.usage_restrictions,
                'royalty_percentage': rights_record.royalty_percentage,
                'blockchain_tx': rights_record.blockchain_tx,
                'nft_token_id': rights_record.nft_token_id,
                'created_at': rights_record.created_at.isoformat(),
                'watermarks': [
                    {
                        'watermark_id': w.watermark_id,
                        'type': w.watermark_type,
                        'visibility': w.visibility,
                        'strength': w.strength,
                        'created_at': w.created_at.isoformat()
                    } for w in watermarks
                ],
                'violations': [
                    {
                        'violation_id': v.violation_id,
                        'infringing_url': v.infringing_url,
                        'platform': v.platform,
                        'similarity_score': v.similarity_score,
                        'status': v.status,
                        'reported_at': v.reported_at.isoformat()
                    } for v in violations
                ]
            }
            
            return rights_info
            
        except Exception as e:
            logger.error(f"Erreur récupération droits: {e}")
            return None
    
    async def get_drm_metrics(self) -> Dict[str, Any]:
        """Récupération métriques DRM"""
        try:
            session = self.Session()
            
            # Statistiques générales
            total_rights = session.query(DigitalRightsModel).count()
            total_watermarks = session.query(WatermarkModel).count()
            total_violations = session.query(ViolationModel).count()
            
            # Distribution par type de licence
            license_distribution = {}
            for license_type in LicenseType:
                count = session.query(DigitalRightsModel)\
                             .filter(DigitalRightsModel.license_type == license_type.value)\
                             .count()
                license_distribution[license_type.value] = count
            
            # Violations récentes
            recent_violations = session.query(ViolationModel)\
                                     .filter(ViolationModel.reported_at >= datetime.utcnow() - timedelta(days=7))\
                                     .count()
            
            # Blockchain stats
            blockchain_registrations = session.query(DigitalRightsModel)\
                                             .filter(DigitalRightsModel.blockchain_tx.isnot(None))\
                                             .count()
            
            nft_creations = session.query(DigitalRightsModel)\
                                 .filter(DigitalRightsModel.nft_token_id.isnot(None))\
                                 .count()
            
            session.close()
            
            return {
                'total_rights_registered': total_rights,
                'total_watermarks_applied': total_watermarks,
                'total_violations_detected': total_violations,
                'recent_violations_7d': recent_violations,
                'license_distribution': license_distribution,
                'blockchain_registrations': blockchain_registrations,
                'nft_creations': nft_creations,
                'royalties_distributed_total': self.metrics.get('royalties_distributed', 0.0),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur métriques DRM: {e}")
            return {}
    
    # Méthodes de sauvegarde et utilitaires
    async def _save_digital_rights(self, rights: DigitalRights):
        """Sauvegarde droits numériques"""
        try:
            session = self.Session()
            
            rights_record = DigitalRightsModel(
                content_id=rights.content_id,
                owner_id=rights.owner_id,
                rights_hash=rights.rights_hash,
                license_type=rights.license_type.value,
                rights_granted=[r.value for r in rights.rights_granted],
                usage_restrictions=rights.usage_restrictions,
                royalty_percentage=rights.royalty_percentage,
                expiration_date=rights.expiration_date,
                metadata=rights.metadata,
                blockchain_tx=rights.blockchain_tx,
                nft_token_id=rights.nft_token_id
            )
            
            session.add(rights_record)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde droits: {e}")
    
    async def _mint_nft(self, content_hash: str, owner_id: str, ipfs_hash: str) -> Optional[str]:
        """Mint NFT pour contenu"""
        try:
            # Simulation mint NFT (implémenter avec vraie blockchain)
            nft_token_id = f"nft_{uuid.uuid4().hex[:16]}"
            
            # Ici on appellerait le smart contract NFT
            # Exemple avec ERC-721
            
            logger.info(f"NFT minté: {nft_token_id}")
            return nft_token_id
            
        except Exception as e:
            logger.error(f"Erreur mint NFT: {e}")
            return None

# Instance globale
_drm_instance = None

def get_digital_rights_manager(config: Dict[str, Any] = None) -> DigitalRightsManager:
    """Factory pour instance DRM"""
    global _drm_instance
    
    if _drm_instance is None:
        if config is None:
            config = {
                'database_url': 'sqlite:///digital_rights.db',
                'blockchain_url': 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
                'ipfs_host': '/ip4/127.0.0.1/tcp/5001/http',
                'redis_host': 'localhost',
                'redis_port': 6379,
                'aws_enabled': False,
                'auto_mint_nft': False,
                'auto_dmca_enabled': False,
                'blockchain_licensing': False
            }
        
        _drm_instance = DigitalRightsManager(config)
    
    return _drm_instance

if __name__ == "__main__":
    # Test basique
    async def test_drm():
        drm = get_digital_rights_manager()
        
        # Test enregistrement droits
        test_content = b"Test content for DRM protection"
        rights = await drm.register_digital_rights(
            test_content,
            "creator_001",
            LicenseType.ALL_RIGHTS_RESERVED,
            [RightsType.COPYRIGHT, RightsType.DISTRIBUTION],
            royalty_percentage=10.0
        )
        
        print(f"Droits enregistrés: {rights.content_id}")
        print(f"Hash: {rights.rights_hash}")
        print(f"Blockchain TX: {rights.blockchain_tx}")
    
    # Exécution test
    asyncio.run(test_drm())