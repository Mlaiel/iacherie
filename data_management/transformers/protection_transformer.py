"""
 Content Protection Transformer - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/transformers/protection_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- AI Research Expert: Fahed Mlaiel (mlaiel@live.de)
- DevOps Engineer: Fahed Mlaiel (mlaiel@live.de)
- DBA: Fahed Mlaiel (mlaiel@live.de)
- Sécurité Expert: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import tempfile

# Protection and watermarking libraries
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import librosa
import soundfile as sf
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# AI libraries for content analysis
import torch
import torchvision.transforms as transforms
from transformers import pipeline, AutoTokenizer, AutoModel
import face_recognition

from .content_fingerprint_transformer import ContentFingerprintTransformer, FingerprintConfig
from ..models.protection_models import (
    ProtectionMetadata, WatermarkConfig, EncryptionConfig,
    ProtectionResult, ViolationAlert, ContentLicense
)
from ...core.exceptions import ProtectionError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.crypto import CryptoManager

settings = get_settings()
logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Niveaux de protection du contenu"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    MILITARY = "military"

class WatermarkType(Enum):
    """Types de watermarks supportés"""
    VISIBLE_TEXT = "visible_text"
    VISIBLE_LOGO = "visible_logo"
    INVISIBLE_LSB = "invisible_lsb"
    INVISIBLE_DCT = "invisible_dct"
    INVISIBLE_DWT = "invisible_dwt"
    AUDIO_INAUDIBLE = "audio_inaudible"
    VIDEO_FRAME = "video_frame"

class EncryptionType(Enum):
    """Types de chiffrement supportés"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    HYBRID = "hybrid"
    STEGANOGRAPHY = "steganography"

class LicenseType(Enum):
    """Types de licences de contenu"""
    COPYRIGHT = "copyright"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    CUSTOM = "custom"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"

@dataclass
class ProtectionConfig:
    """Configuration de protection du contenu"""
    protection_level: ProtectionLevel
    watermark_config: Optional['WatermarkConfiguration'] = None
    encryption_config: Optional['EncryptionConfiguration'] = None
    license_config: Optional['LicenseConfiguration'] = None
    fingerprint_enabled: bool = True
    monitoring_enabled: bool = True
    creator_type: Optional[str] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WatermarkConfiguration:
    """Configuration de watermark"""
    watermark_type: WatermarkType
    visibility: float = 0.3  # 0.0 = invisible, 1.0 = fully visible
    position: str = "bottom_right"  # top_left, top_right, bottom_left, bottom_right, center
    text: Optional[str] = None
    logo_path: Optional[str] = None
    color: str = "white"
    font_size: int = 24
    frequency_band: Optional[Tuple[int, int]] = None  # For audio watermarks
    strength: float = 0.1  # Strength of invisible watermarks

@dataclass
class EncryptionConfiguration:
    """Configuration de chiffrement"""
    encryption_type: EncryptionType
    key_strength: int = 256
    password: Optional[str] = None
    key_derivation_iterations: int = 100000
    compress_before_encrypt: bool = True
    metadata_encryption: bool = True

@dataclass
class LicenseConfiguration:
    """Configuration de licence"""
    license_type: LicenseType
    owner_name: str
    owner_email: str
    usage_rights: List[str]
    restrictions: List[str]
    expiry_date: Optional[datetime] = None
    commercial_allowed: bool = False
    attribution_required: bool = True
    custom_terms: Optional[str] = None

@dataclass
class ContentProtectionResult:
    """Résultat de protection de contenu"""
    success: bool
    original_path: str
    protected_path: Optional[str]
    protection_id: str
    fingerprint_data: Optional[Dict[str, Any]]
    watermark_applied: bool
    encryption_applied: bool
    license_embedded: bool
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time: float
    errors: List[str]
    warnings: List[str]

class AudioWatermarkTransformer:
    """Transformateur de watermarks audio professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    
    def apply_inaudible_watermark(
        self,
        audio_path: str,
        watermark_config: WatermarkConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Applique un watermark inaudible dans l'audio"""



        
        try:
            # Chargement audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Génération du signal de watermark
            watermark_signal = self._generate_watermark_signal(
                len(y), sr, watermark_config
            )
            
            # Application du watermark avec force contrôlée
            watermarked_audio = y + (watermark_signal * watermark_config.strength)
            
            # Normalisation pour éviter le clipping
            watermarked_audio = librosa.util.normalize(watermarked_audio)
            
            # Sauvegarde
            sf.write(output_path, watermarked_audio, sr)
            
            return {
                'success': True,
                'watermark_strength': watermark_config.strength,
                'frequency_band': watermark_config.frequency_band,
                'original_duration': len(y) / sr,
                'watermark_type': 'inaudible_frequency'
            }
            
        except Exception as e:
            logger.error(f"Erreur watermark audio {audio_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_watermark_signal(
        self,
        length: int,
        sample_rate: int,
        config: WatermarkConfiguration
    ) -> np.ndarray:
        """Génère un signal de watermark dans une bande de fréquence spécifique"""
        
        # Fréquences par défaut (hautes fréquences moins audibles)
        freq_band = config.frequency_band or (15000, 18000)
        center_freq = (freq_band[0] + freq_band[1]) / 2
        
        # Génération d'un signal sinusoïdal modulé
        t = np.linspace(0, length / sample_rate, length, False)
        
        # Signal porteur
        carrier = np.sin(2 * np.pi * center_freq * t)
        
        # Modulation avec un motif unique (basé sur le texte du watermark)
        if config.text:
            # Conversion du texte en pattern binaire
            text_hash = hashlib.sha256(config.text.encode()).hexdigest()
            binary_pattern = ''.join(format(ord(c), '08b') for c in text_hash[:8])
            
            # Modulation du signal
            pattern_length = len(binary_pattern)
            pattern_repeat = int(np.ceil(length / (sample_rate * 0.1)))  # 0.1s per bit
            
            modulation = np.tile(
                [int(bit) * 2 - 1 for bit in binary_pattern],
                pattern_repeat
            )[:length]
            
            watermark_signal = carrier * modulation
        else:
            watermark_signal = carrier
        
        # Application d'une enveloppe pour réduire les artefacts
        envelope = np.hanning(min(sample_rate // 10, length))
        if len(envelope) < length:
            envelope = np.concatenate([
                envelope[:len(envelope)//2],
                np.ones(length - len(envelope)),
                envelope[len(envelope)//2:]
            ])[:length]
        
        return watermark_signal * envelope

class ImageWatermarkTransformer:
    """Transformateur de watermarks image professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'}
    
    def apply_visible_watermark(
        self,
        image_path: str,
        watermark_config: WatermarkConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Applique un watermark visible sur l'image"""



        
        try:
            # Chargement de l'image
            image = Image.open(image_path)
            
            # Création d'une couche de watermark
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            if watermark_config.watermark_type == WatermarkType.VISIBLE_TEXT:
                result = self._apply_text_watermark(
                    image, watermark_layer, draw, watermark_config
                )
            elif watermark_config.watermark_type == WatermarkType.VISIBLE_LOGO:
                result = self._apply_logo_watermark(
                    image, watermark_layer, watermark_config
                )
            else:
                raise ValueError(f"Type de watermark non supporté: {watermark_config.watermark_type}")
            
            # Fusion des couches
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            watermarked = Image.alpha_composite(image, watermark_layer)
            
            # Conversion pour sauvegarde si nécessaire
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                watermarked = watermarked.convert('RGB')
            
            # Sauvegarde
            watermarked.save(output_path, quality=95)
            
            result.update({
                'success': True,
                'output_path': output_path,
                'original_size': image.size,
                'watermark_position': watermark_config.position
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur watermark image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_invisible_watermark(
        self,
        image_path: str,
        watermark_config: WatermarkConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Applique un watermark invisible (LSB steganography)"""



        
        try:
            # Chargement de l'image
            image = cv2.imread(image_path)
            
            if watermark_config.watermark_type == WatermarkType.INVISIBLE_LSB:
                result = self._apply_lsb_watermark(image, watermark_config)
            elif watermark_config.watermark_type == WatermarkType.INVISIBLE_DCT:
                result = self._apply_dct_watermark(image, watermark_config)
            else:
                raise ValueError(f"Type de watermark invisible non supporté")
            
            # Sauvegarde
            cv2.imwrite(output_path, result['watermarked_image'])
            
            return {
                'success': True,
                'output_path': output_path,
                'watermark_type': 'invisible',
                'algorithm': watermark_config.watermark_type.value,
                'strength': watermark_config.strength
            }
            
        except Exception as e:
            logger.error(f"Erreur watermark invisible {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _apply_text_watermark(
        self,
        image: Image.Image,
        watermark_layer: Image.Image,
        draw: ImageDraw.Draw,
        config: WatermarkConfiguration
    ) -> Dict[str, Any]:
        """Applique un watermark texte"""
        
        # Configuration de la police
        try:
            font = ImageFont.truetype("arial.ttf", config.font_size)
        except:
            font = ImageFont.load_default()
        
        # Texte du watermark
        text = config.text or f"© {datetime.now().year}"
        
        # Calcul de la taille du texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Positionnement
        pos = self._calculate_watermark_position(
            image.size, (text_width, text_height), config.position
        )
        
        # Couleur avec transparence
        color = self._parse_color(config.color, config.visibility)
        
        # Application du texte
        draw.text(pos, text, font=font, fill=color)
        
        return {
            'text': text,
            'position': pos,
            'font_size': config.font_size,
            'color': config.color,
            'visibility': config.visibility
        }
    
    def _apply_logo_watermark(
        self,
        image: Image.Image,
        watermark_layer: Image.Image,
        config: WatermarkConfiguration
    ) -> Dict[str, Any]:
        """Applique un watermark logo"""
        
        if not config.logo_path or not Path(config.logo_path).exists():
            raise ValueError("Chemin du logo manquant ou invalide")
        
        # Chargement du logo
        logo = Image.open(config.logo_path)
        
        # Redimensionnement proportionnel (max 20% de l'image)
        max_size = (image.size[0] // 5, image.size[1] // 5)
        logo.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Positionnement
        pos = self._calculate_watermark_position(
            image.size, logo.size, config.position
        )
        
        # Application de la transparence
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Ajustement de l'opacité
        alpha = logo.split()[-1]
        alpha = alpha.point(lambda p: int(p * config.visibility))
        logo.putalpha(alpha)
        
        # Collage du logo
        watermark_layer.paste(logo, pos, logo)
        
        return {
            'logo_path': config.logo_path,
            'logo_size': logo.size,
            'position': pos,
            'visibility': config.visibility
        }
    
    def _apply_lsb_watermark(
        self,
        image: np.ndarray,
        config: WatermarkConfiguration
    ) -> Dict[str, Any]:
        """Applique un watermark par LSB steganography"""
        
        # Message à cacher
        message = config.text or f"PROTECTED_{uuid.uuid4().hex[:8]}"
        
        # Conversion du message en binaire
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        binary_message += '1111111111111110'  # Marqueur de fin
        
        # Application LSB sur le canal bleu (moins visible)
        watermarked = image.copy()
        data_index = 0
        
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if data_index < len(binary_message):
                    # Modification du LSB du canal bleu
                    pixel = watermarked[i, j]
                    pixel[0] = (pixel[0] & 0xFE) | int(binary_message[data_index])
                    watermarked[i, j] = pixel
                    data_index += 1
                else:
                    break
            if data_index >= len(binary_message):
                break
        
        return {
            'watermarked_image': watermarked,
            'message_length': len(message),
            'binary_length': len(binary_message),
            'modification_ratio': data_index / (image.shape[0] * image.shape[1])
        }
    
    def _apply_dct_watermark(
        self,
        image: np.ndarray,
        config: WatermarkConfiguration
    ) -> Dict[str, Any]:
        """Applique un watermark par DCT (Discrete Cosine Transform)"""
        
        # Conversion en YUV pour travailler sur la luminance
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        
        # Division en blocs 8x8
        h, w = y_channel.shape
        blocks_h, blocks_w = h // 8, w // 8
        
        # Génération du watermark basé sur le texte
        watermark_pattern = self._generate_watermark_pattern(config.text or "PROTECTED")
        
        # Application DCT sur chaque bloc
        watermarked_y = y_channel.copy()
        
        for i in range(0, blocks_h * 8, 8):
            for j in range(0, blocks_w * 8, 8):
                block = y_channel[i:i+8, j:j+8]
                
                # DCT
                dct_block = cv2.dct(block)
                
                # Modification des coefficients moyens-hauts
                pattern_idx = ((i // 8) * blocks_w + (j // 8)) % len(watermark_pattern)
                strength = config.strength * watermark_pattern[pattern_idx]
                
                # Modification de coefficients spécifiques
                dct_block[2, 3] += strength
                dct_block[3, 2] += strength
                
                # IDCT
                watermarked_block = cv2.idct(dct_block)
                watermarked_y[i:i+8, j:j+8] = watermarked_block
        
        # Reconstruction de l'image
        yuv[:, :, 0] = np.clip(watermarked_y, 0, 255).astype(np.uint8)
        watermarked_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        
        return {
            'watermarked_image': watermarked_image,
            'blocks_processed': blocks_h * blocks_w,
            'strength': config.strength,
            'algorithm': 'DCT'
        }
    
    def _calculate_watermark_position(
        self,
        image_size: Tuple[int, int],
        watermark_size: Tuple[int, int],
        position: str
    ) -> Tuple[int, int]:
        """Calcule la position du watermark"""
        
        img_w, img_h = image_size
        wm_w, wm_h = watermark_size
        
        margin = 20  # Marge en pixels
        
        positions = {
            'top_left': (margin, margin),
            'top_right': (img_w - wm_w - margin, margin),
            'bottom_left': (margin, img_h - wm_h - margin),
            'bottom_right': (img_w - wm_w - margin, img_h - wm_h - margin),
            'center': ((img_w - wm_w) // 2, (img_h - wm_h) // 2)
        }
        
        return positions.get(position, positions['bottom_right'])
    
    def _parse_color(self, color_str: str, visibility: float) -> Tuple[int, int, int, int]:
        """Parse une couleur et applique la visibilité"""
        
        colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        rgb = colors.get(color_str.lower(), colors['white'])
        alpha = int(255 * visibility)
        
        return rgb + (alpha,)
    
    def _generate_watermark_pattern(self, text: str) -> List[float]:
        """Génère un pattern de watermark basé sur le texte"""
        
        # Hash du texte pour générer un pattern reproductible
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Conversion en pattern numérique
        pattern = []
        for i in range(0, len(text_hash), 2):
            hex_byte = text_hash[i:i+2]
            value = int(hex_byte, 16) / 255.0  # Normalisation [0, 1]
            pattern.append(value * 2 - 1)  # Conversion [-1, 1]
        
        return pattern

class ContentEncryptionTransformer:
    """Transformateur de chiffrement de contenu professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crypto_manager = CryptoManager()
    
    def encrypt_content(
        self,
        content_path: str,
        encryption_config: EncryptionConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Chiffre le contenu selon la configuration"""



        
        try:
            # Lecture du contenu
            with open(content_path, 'rb') as f:
                content_data = f.read()
            
            # Compression optionnelle
            if encryption_config.compress_before_encrypt:
                import gzip
                content_data = gzip.compress(content_data)
            
            # Chiffrement selon le type
            if encryption_config.encryption_type == EncryptionType.AES_256:
                result = self._encrypt_aes(content_data, encryption_config)
            elif encryption_config.encryption_type == EncryptionType.HYBRID:
                result = self._encrypt_hybrid(content_data, encryption_config)
            else:
                raise ValueError(f"Type de chiffrement non supporté: {encryption_config.encryption_type}")
            
            # Sauvegarde du contenu chiffré
            with open(output_path, 'wb') as f:
                f.write(result['encrypted_data'])
            
            # Sauvegarde des métadonnées de chiffrement
            metadata_path = output_path + '.meta'
            with open(metadata_path, 'w') as f:
                json.dump(result['metadata'], f, indent=2)
            
            return {
                'success': True,
                'encrypted_path': output_path,
                'metadata_path': metadata_path,
                'encryption_type': encryption_config.encryption_type.value,
                'key_strength': encryption_config.key_strength,
                'compressed': encryption_config.compress_before_encrypt,
                'original_size': len(content_data),
                'encrypted_size': len(result['encrypted_data'])
            }
            
        except Exception as e:
            logger.error(f"Erreur chiffrement {content_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _encrypt_aes(
        self,
        data: bytes,
        config: EncryptionConfiguration
    ) -> Dict[str, Any]:
        """Chiffrement AES-256"""
        
        # Génération ou dérivation de la clé
        if config.password:
            # Dérivation de clé depuis le mot de passe
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=config.key_derivation_iterations,
            )
            key = base64.urlsafe_b64encode(kdf.derive(config.password.encode()))
        else:
            # Génération d'une clé aléatoire
            key = Fernet.generate_key()
            salt = b''
        
        # Chiffrement
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        
        return {
            'encrypted_data': encrypted_data,
            'metadata': {
                'algorithm': 'AES-256',
                'key_derivation': 'PBKDF2' if config.password else 'random',
                'salt': base64.b64encode(salt).decode() if salt else '',
                'iterations': config.key_derivation_iterations if config.password else 0,
                'key': base64.b64encode(key).decode() if not config.password else '',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _encrypt_hybrid(
        self,
        data: bytes,
        config: EncryptionConfiguration
    ) -> Dict[str, Any]:
        """Chiffrement hybride (AES + RSA)"""
        
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives import serialization
        
        # Génération des clés RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Génération d'une clé AES
        aes_key = Fernet.generate_key()
        fernet = Fernet(aes_key)
        
        # Chiffrement des données avec AES
        encrypted_data = fernet.encrypt(data)
        
        # Chiffrement de la clé AES avec RSA
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Sérialisation des clés
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Combinaison des données chiffrées
        combined_data = encrypted_aes_key + b'|SEPARATOR|' + encrypted_data
        
        return {
            'encrypted_data': combined_data,
            'metadata': {
                'algorithm': 'Hybrid-AES-RSA',
                'aes_strength': 256,
                'rsa_strength': 2048,
                'private_key': base64.b64encode(private_pem).decode(),
                'public_key': base64.b64encode(public_pem).decode(),
                'timestamp': datetime.now().isoformat()
            }
        }

class ContentLicenseTransformer:
    """Transformateur de licences de contenu professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def embed_license(
        self,
        content_path: str,
        license_config: LicenseConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Intègre les informations de licence dans le contenu"""



        
        try:
            # Génération des métadonnées de licence
            license_metadata = self._generate_license_metadata(license_config)
            
            # Intégration selon le type de fichier
            file_ext = Path(content_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.tiff']:
                result = self._embed_image_license(content_path, license_metadata, output_path)
            elif file_ext in ['.mp3', '.wav', '.flac']:
                result = self._embed_audio_license(content_path, license_metadata, output_path)
            elif file_ext in ['.mp4', '.avi', '.mov']:
                result = self._embed_video_license(content_path, license_metadata, output_path)
            else:
                # Création d'un fichier de licence séparé
                result = self._create_license_file(content_path, license_metadata, output_path)
            
            return {
                'success': True,
                'licensed_path': output_path,
                'license_type': license_config.license_type.value,
                'owner': license_config.owner_name,
                'commercial_allowed': license_config.commercial_allowed,
                'attribution_required': license_config.attribution_required,
                'embedding_method': result.get('method', 'metadata'),
                'license_id': license_metadata['license_id']
            }
            
        except Exception as e:
            logger.error(f"Erreur intégration licence {content_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_license_metadata(
        self,
        config: LicenseConfiguration
    ) -> Dict[str, Any]:
        """Génère les métadonnées de licence"""
        
        license_id = f"LIC_{uuid.uuid4().hex[:12].upper()}"
        
        return {
            'license_id': license_id,
            'license_type': config.license_type.value,
            'owner_name': config.owner_name,
            'owner_email': config.owner_email,
            'creation_date': datetime.now().isoformat(),
            'expiry_date': config.expiry_date.isoformat() if config.expiry_date else None,
            'usage_rights': config.usage_rights,
            'restrictions': config.restrictions,
            'commercial_allowed': config.commercial_allowed,
            'attribution_required': config.attribution_required,
            'custom_terms': config.custom_terms,
            'license_url': self._generate_license_url(license_id),
            'verification_hash': self._generate_verification_hash(config)
        }
    
    def _embed_image_license(
        self,
        image_path: str,
        license_metadata: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Intègre la licence dans les métadonnées EXIF de l'image"""
        
        from PIL import Image
        from PIL.ExifTags import TAGS
        import piexif
        
        # Chargement de l'image
        image = Image.open(image_path)
        
        # Préparation des données EXIF
        exif_dict = piexif.load(image_path) if hasattr(image, '_getexif') else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        # Ajout des informations de licence
        exif_dict["0th"][piexif.ImageIFD.Copyright] = f"{license_metadata['owner_name']} ({license_metadata['license_type']})"
        exif_dict["0th"][piexif.ImageIFD.Artist] = license_metadata['owner_name']
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = f"License ID: {license_metadata['license_id']}"
        
        # Conversion en bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Sauvegarde avec métadonnées
        image.save(output_path, exif=exif_bytes)
        
        return {'method': 'exif_metadata'}
    
    def _embed_audio_license(
        self,
        audio_path: str,
        license_metadata: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Intègre la licence dans les métadonnées ID3 de l'audio"""
        
        import eyed3
        
        # Copie du fichier audio
        import shutil
        shutil.copy2(audio_path, output_path)
        
        # Chargement du fichier audio
        audiofile = eyed3.load(output_path)
        
        if audiofile.tag is None:
            audiofile.initTag()
        
        # Ajout des métadonnées de licence
        audiofile.tag.copyright = f"{license_metadata['owner_name']} - {license_metadata['license_type']}"
        audiofile.tag.artist = license_metadata['owner_name']
        audiofile.tag.comments.set(f"License: {license_metadata['license_id']}")
        
        # Ajout d'un frame personnalisé pour les détails complets
        license_json = json.dumps(license_metadata)
        audiofile.tag.user_text_frames.set(license_json, "LICENSE_METADATA")
        
        # Sauvegarde
        audiofile.tag.save()
        
        return {'method': 'id3_metadata'}
    
    def _embed_video_license(
        self,
        video_path: str,
        license_metadata: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Intègre la licence dans les métadonnées du vidéo"""
        
        # Utilisation de ffmpeg pour ajouter des métadonnées
        import subprocess
        
        # Préparation des métadonnées
        metadata_args = [
            '-metadata', f'copyright={license_metadata["owner_name"]} - {license_metadata["license_type"]}',
            '-metadata', f'artist={license_metadata["owner_name"]}',
            '-metadata', f'comment=License ID: {license_metadata["license_id"]}',
            '-metadata', f'description=Licensed content - {license_metadata["license_url"]}'
        ]
        
        # Commande ffmpeg
        cmd = [
            'ffmpeg', '-i', video_path,
            *metadata_args,
            '-c', 'copy',  # Copie sans re-encodage
            '-y',  # Écrase le fichier de sortie
            output_path
        ]
        
        # Exécution
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {'method': 'ffmpeg_metadata'}
        else:
            raise Exception(f"Erreur ffmpeg: {result.stderr}")
    
    def _create_license_file(
        self,
        content_path: str,
        license_metadata: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Crée un fichier de licence séparé"""
        
        # Copie du fichier original
        import shutil
        shutil.copy2(content_path, output_path)
        
        # Création du fichier de licence
        license_file_path = output_path + '.license'
        
        with open(license_file_path, 'w', encoding='utf-8') as f:
            f.write("=== LICENCE DE CONTENU NUMÉRIQUE ===\n\n")
            f.write(f"ID de Licence: {license_metadata['license_id']}\n")
            f.write(f"Type de Licence: {license_metadata['license_type']}\n")
            f.write(f"Propriétaire: {license_metadata['owner_name']}\n")
            f.write(f"Email: {license_metadata['owner_email']}\n")
            f.write(f"Date de Création: {license_metadata['creation_date']}\n")
            
            if license_metadata['expiry_date']:
                f.write(f"Date d'Expiration: {license_metadata['expiry_date']}\n")
            
            f.write(f"\nUtilisation Commerciale: {'Autorisée' if license_metadata['commercial_allowed'] else 'Interdite'}\n")
            f.write(f"Attribution Requise: {'Oui' if license_metadata['attribution_required'] else 'Non'}\n")
            
            f.write("\nDroits d'Usage:\n")
            for right in license_metadata['usage_rights']:
                f.write(f"  - {right}\n")
            
            f.write("\nRestrictions:\n")
            for restriction in license_metadata['restrictions']:
                f.write(f"  - {restriction}\n")
            
            if license_metadata['custom_terms']:
                f.write(f"\nTermes Personnalisés:\n{license_metadata['custom_terms']}\n")
            
            f.write(f"\nURL de Vérification: {license_metadata['license_url']}\n")
            f.write(f"Hash de Vérification: {license_metadata['verification_hash']}\n")
        
        return {
            'method': 'separate_file',
            'license_file': license_file_path
        }
    
    def _generate_license_url(self, license_id: str) -> str:
        """Génère une URL de vérification de licence"""
        base_url = settings.get('LICENSE_VERIFICATION_URL', 'https://license.ia-influencer.com/verify')
        return f"{base_url}/{license_id}"
    
    def _generate_verification_hash(self, config: LicenseConfiguration) -> str:
        """Génère un hash de vérification de la licence"""
        
        verification_data = f"{config.license_type.value}{config.owner_name}{config.owner_email}"
        return hashlib.sha256(verification_data.encode()).hexdigest()[:16].upper()

class ContentProtectionTransformer:
    """Gestionnaire principal de protection de contenu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des transformateurs spécialisés
        self.fingerprint_transformer = ContentFingerprintTransformer()
        self.audio_watermark = AudioWatermarkTransformer()
        self.image_watermark = ImageWatermarkTransformer()
        self.encryption_transformer = ContentEncryptionTransformer()
        self.license_transformer = ContentLicenseTransformer()
        
        # Configuration par type de créateur
        self.creator_protection_presets = {
            'musician': {
                'protection_level': ProtectionLevel.ADVANCED,
                'watermark_enabled': True,
                'fingerprint_enabled': True,
                'encryption_enabled': False,
                'monitoring_enabled': True
            },
            'photographer': {
                'protection_level': ProtectionLevel.ADVANCED,
                'watermark_enabled': True,
                'fingerprint_enabled': True,
                'encryption_enabled': True,
                'monitoring_enabled': True
            },
            'influencer': {
                'protection_level': ProtectionLevel.STANDARD,
                'watermark_enabled': True,
                'fingerprint_enabled': True,
                'encryption_enabled': False,
                'monitoring_enabled': True
            },
            'blogger': {
                'protection_level': ProtectionLevel.BASIC,
                'watermark_enabled': False,
                'fingerprint_enabled': True,
                'encryption_enabled': False,
                'monitoring_enabled': True
            },
            'comedian': {
                'protection_level': ProtectionLevel.STANDARD,
                'watermark_enabled': True,
                'fingerprint_enabled': True,
                'encryption_enabled': False,
                'monitoring_enabled': True
            }
        }
    
    def protect_content(
        self,
        content_path: str,
        protection_config: ProtectionConfig,
        output_path: Optional[str] = None
    ) -> ContentProtectionResult:
        """Applique une protection complète au contenu"""
        
        start_time = time.time()
        protection_id = f"PROT_{uuid.uuid4().hex[:12].upper()}"
        
        if not output_path:
            output_path = self._generate_output_path(content_path, protection_id)
        
        try:
            results = {
                'fingerprint_applied': False,
                'watermark_applied': False,
                'encryption_applied': False,
                'license_embedded': False
            }
            
            current_path = content_path
            errors = []
            warnings = []
            
            # 1. Génération d'empreinte digitale
            fingerprint_data = None
            if protection_config.fingerprint_enabled:
                fingerprint_result = self._apply_fingerprinting(current_path, protection_config)
                if fingerprint_result['success']:
                    results['fingerprint_applied'] = True
                    fingerprint_data = fingerprint_result.get('fingerprint_data')
                else:
                    errors.extend(fingerprint_result.get('errors', []))
            
            # 2. Application de watermark
            if protection_config.watermark_config:
                watermark_result = self._apply_watermarking(
                    current_path, protection_config.watermark_config, output_path
                )
                if watermark_result['success']:
                    results['watermark_applied'] = True
                    current_path = output_path
                else:
                    errors.extend(watermark_result.get('errors', []))
            else:
                # Copie du fichier si pas de watermark
                import shutil
                shutil.copy2(current_path, output_path)
                current_path = output_path
            
            # 3. Chiffrement du contenu
            if protection_config.encryption_config:
                encrypted_path = output_path + '.encrypted'
                encryption_result = self.encryption_transformer.encrypt_content(
                    current_path, protection_config.encryption_config, encrypted_path
                )
                if encryption_result['success']:
                    results['encryption_applied'] = True
                    current_path = encrypted_path
                else:
                    errors.extend([encryption_result.get('error', 'Erreur chiffrement')])
            
            # 4. Intégration de licence
            if protection_config.license_config:
                license_result = self.license_transformer.embed_license(
                    current_path, protection_config.license_config, current_path
                )
                if license_result['success']:
                    results['license_embedded'] = True
                else:
                    errors.extend([license_result.get('error', 'Erreur licence')])
            
            # Calcul du score de confiance
            confidence_score = self._calculate_protection_confidence(results, protection_config)
            
            processing_time = time.time() - start_time
            
            return ContentProtectionResult(
                success=len(errors) == 0,
                original_path=content_path,
                protected_path=current_path,
                protection_id=protection_id,
                fingerprint_data=fingerprint_data,
                watermark_applied=results['watermark_applied'],
                encryption_applied=results['encryption_applied'],
                license_embedded=results['license_embedded'],
                metadata={
                    'protection_level': protection_config.protection_level.value,
                    'creator_type': protection_config.creator_type,
                    'protection_steps': results,
                    'file_size_original': Path(content_path).stat().st_size,
                    'file_size_protected': Path(current_path).stat().st_size if Path(current_path).exists() else 0
                },
                confidence_score=confidence_score,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Erreur protection contenu {content_path}: {e}")
            return ContentProtectionResult(
                success=False,
                original_path=content_path,
                protected_path=None,
                protection_id=protection_id,
                fingerprint_data=None,
                watermark_applied=False,
                encryption_applied=False,
                license_embedded=False,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[]
            )
    
    def _apply_fingerprinting(
        self,
        content_path: str,
        protection_config: ProtectionConfig
    ) -> Dict[str, Any]:
        """Applique l'empreinte digitale"""



        
        try:
            # Configuration de l'empreinte selon le type de contenu
            content_type = self._detect_content_type(content_path)
            
            if content_type == 'audio':
                fingerprint_config = FingerprintConfig(
                    algorithm=FingerprintAlgorithm.CHROMAPRINT,
                    fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                    parameters={'sample_rate': 22050, 'duration': 120}
                )
            elif content_type == 'image':
                fingerprint_config = FingerprintConfig(
                    algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                    fingerprint_type=FingerprintType.IMAGE_PHASH,
                    parameters={'detect_faces': True}
                )
            elif content_type == 'video':
                fingerprint_config = FingerprintConfig(
                    algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                    fingerprint_type=FingerprintType.VIDEO_PHASH,
                    parameters={'frame_skip': 30, 'max_frames': 100}
                )
            else:
                return {'success': False, 'errors': ['Type de contenu non supporté pour fingerprint']}
            
            # Génération de l'empreinte
            result = self.fingerprint_transformer.generate_fingerprint(
                content_path, fingerprint_config, protection_config.creator_type
            )
            
            if result.success:
                return {
                    'success': True,
                    'fingerprint_data': {
                        'fingerprint_id': f"FP_{uuid.uuid4().hex[:8].upper()}",
                        'algorithm': result.algorithm.value,
                        'fingerprint_type': result.fingerprint_type.value,
                        'fingerprint_hash': result.fingerprint_data,
                        'confidence_score': result.confidence_score,
                        'metadata': result.metadata
                    }
                }
            else:
                return {'success': False, 'errors': result.errors}
                
        except Exception as e:
            return {'success': False, 'errors': [f"Erreur fingerprinting: {str(e)}"]}
    
    def _apply_watermarking(
        self,
        content_path: str,
        watermark_config: WatermarkConfiguration,
        output_path: str
    ) -> Dict[str, Any]:
        """Applique le watermarking"""



        
        try:
            content_type = self._detect_content_type(content_path)
            
            if content_type == 'audio':
                return self.audio_watermark.apply_inaudible_watermark(
                    content_path, watermark_config, output_path
                )
            elif content_type == 'image':
                if watermark_config.watermark_type in [WatermarkType.VISIBLE_TEXT, WatermarkType.VISIBLE_LOGO]:
                    return self.image_watermark.apply_visible_watermark(
                        content_path, watermark_config, output_path
                    )
                else:
                    return self.image_watermark.apply_invisible_watermark(
                        content_path, watermark_config, output_path
                    )
            else:
                return {'success': False, 'errors': ['Type de contenu non supporté pour watermark']}
                
        except Exception as e:
            return {'success': False, 'errors': [f"Erreur watermarking: {str(e)}"]}
    
    def _detect_content_type(self, content_path: str) -> str:
        """Détecte le type de contenu"""
        
        ext = Path(content_path).suffix.lower()
        
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        image_exts = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'}
        
        if ext in audio_exts:
            return 'audio'
        elif ext in video_exts:
            return 'video'
        elif ext in image_exts:
            return 'image'
        else:
            return 'document'
    
    def _generate_output_path(self, content_path: str, protection_id: str) -> str:
        """Génère le chemin de sortie protégé"""
        
        path = Path(content_path)
        return str(path.parent / f"{path.stem}_protected_{protection_id}{path.suffix}")
    
    def _calculate_protection_confidence(
        self,
        results: Dict[str, bool],
        config: ProtectionConfig
    ) -> float:
        """Calcule le score de confiance de la protection"""
        
        base_score = 0.5
        
        # Bonus par étape de protection appliquée
        if results['fingerprint_applied']:
            base_score += 0.2
        if results['watermark_applied']:
            base_score += 0.15
        if results['encryption_applied']:
            base_score += 0.1
        if results['license_embedded']:
            base_score += 0.05
        
        # Bonus selon le niveau de protection
        level_bonus = {
            ProtectionLevel.BASIC: 0.0,
            ProtectionLevel.STANDARD: 0.05,
            ProtectionLevel.ADVANCED: 0.1,
            ProtectionLevel.MILITARY: 0.15
        }
        
        base_score += level_bonus.get(config.protection_level, 0.0)
        
        return min(1.0, base_score)
    
    def get_creator_protection_config(
        self,
        creator_type: str,
        content_path: str,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> ProtectionConfig:
        """Génère une configuration de protection optimale pour le type de créateur"""
        
        # Configuration de base par type de créateur
        preset = self.creator_protection_presets.get(creator_type, self.creator_protection_presets['influencer'])
        
        # Configuration de watermark selon le type de contenu
        content_type = self._detect_content_type(content_path)
        watermark_config = None
        
        if preset['watermark_enabled']:
            if content_type == 'image':
                watermark_config = WatermarkConfiguration(
                    watermark_type=WatermarkType.VISIBLE_TEXT,
                    text=f"© {creator_type.title()}",
                    position="bottom_right",
                    visibility=0.7,
                    color="white"
                )
            elif content_type == 'audio':
                watermark_config = WatermarkConfiguration(
                    watermark_type=WatermarkType.AUDIO_INAUDIBLE,
                    text=f"PROTECTED_{creator_type.upper()}",
                    frequency_band=(15000, 18000),
                    strength=0.1
                )
        
        # Configuration de licence par défaut
        license_config = LicenseConfiguration(
            license_type=LicenseType.COPYRIGHT,
            owner_name=f"{creator_type.title()} Creator",
            owner_email="creator@ia-influencer.com",
            usage_rights=["view", "personal_use"],
            restrictions=["no_commercial_use", "no_redistribution"],
            commercial_allowed=False,
            attribution_required=True
        )
        
        # Application des paramètres personnalisés
        if custom_settings:
            preset.update(custom_settings)
        
        return ProtectionConfig(
            protection_level=preset['protection_level'],
            watermark_config=watermark_config if preset['watermark_enabled'] else None,
            license_config=license_config,
            fingerprint_enabled=preset['fingerprint_enabled'],
            monitoring_enabled=preset['monitoring_enabled'],
            creator_type=creator_type,
            custom_parameters=custom_settings or {}
        )
    
    async def batch_protect_content(
        self,
        content_paths: List[str],
        protection_config: ProtectionConfig
    ) -> List[ContentProtectionResult]:
        """Protège plusieurs contenus en lot de manière asynchrone"""
        
        tasks = []
        for path in content_paths:
            task = asyncio.create_task(
                self._async_protect_content(path, protection_config)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erreur protection {content_paths[i]}: {result}")
                processed_results.append(ContentProtectionResult(
                    success=False,
                    original_path=content_paths[i],
                    protected_path=None,
                    protection_id=f"ERR_{uuid.uuid4().hex[:8]}",
                    fingerprint_data=None,
                    watermark_applied=False,
                    encryption_applied=False,
                    license_embedded=False,
                    metadata={},
                    confidence_score=0.0,
                    processing_time=0.0,
                    errors=[f"Exception: {str(result)}"],
                    warnings=[]
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _async_protect_content(
        self,
        content_path: str,
        protection_config: ProtectionConfig
    ) -> ContentProtectionResult:
        """Version asynchrone de la protection de contenu"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.protect_content,
            content_path,
            protection_config,
            None
        )

# Instance globale
content_protection_transformer = ContentProtectionTransformer()

# Export des classes principales
__all__ = [
    'ContentProtectionTransformer',
    'AudioWatermarkTransformer',
    'ImageWatermarkTransformer',
    'ContentEncryptionTransformer',
    'ContentLicenseTransformer',
    'ProtectionConfig',
    'WatermarkConfiguration',
    'EncryptionConfiguration',
    'LicenseConfiguration',
    'ContentProtectionResult',
    'ProtectionLevel',
    'WatermarkType',
    'EncryptionType',
    'LicenseType',
    'content_protection_transformer'
]
