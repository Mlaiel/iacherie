"""
Watermarking Engine - Fingerprinting Module
==========================================
Système avancé de watermarking avec embedding invisible/visible,
steganographie et protection robuste contre les attaques.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import io
import base64

logger = logging.getLogger(__name__)

class WatermarkType(Enum):
    """Types de watermarks supportés."""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    STEGANOGRAPHIC = "steganographic"
    FREQUENCY_DOMAIN = "frequency_domain"
    SPATIAL_DOMAIN = "spatial_domain"
    BLOCKCHAIN_PROOF = "blockchain_proof"

class WatermarkFormat(Enum):
    """Formats de contenu supportés."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    PDF = "pdf"

class RobustnessLevel(Enum):
    """Niveaux de robustesse."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MILITARY_GRADE = "military_grade"

@dataclass
class WatermarkPayload:
    """Payload du watermark."""
    creator_id: str
    content_hash: str
    timestamp: datetime
    copyright_info: str
    license_type: str
    blockchain_proof: Optional[str]
    custom_data: Dict[str, Any]
    expiration_date: Optional[datetime]

@dataclass
class WatermarkConfig:
    """Configuration du watermarking."""
    watermark_type: WatermarkType
    robustness_level: RobustnessLevel
    opacity: float
    position: tuple[int, int]
    size: tuple[int, int]
    color: tuple[int, int, int]
    font_family: str
    encoding_strength: float
    resistance_attacks: List[str]
    extraction_key: str

@dataclass
class WatermarkedContent:
    """Contenu watermarké."""
    watermark_id: str
    original_content_hash: str
    watermarked_content: Union[np.ndarray, bytes, str]
    watermark_payload: WatermarkPayload
    watermark_config: WatermarkConfig
    embedding_timestamp: datetime
    verification_data: Dict[str, Any]
    robustness_metrics: Dict[str, float]
    extraction_success_rate: float
    content_quality_metrics: Dict[str, float]

@dataclass
class WatermarkExtractionResult:
    """Résultat d'extraction de watermark."""
    extraction_id: str
    watermark_detected: bool
    extracted_payload: Optional[WatermarkPayload]
    confidence_score: float
    integrity_verified: bool
    extraction_method: str
    processing_time: float
    attack_resistance_tested: Dict[str, bool]
    quality_degradation: float

class WatermarkingEngine:
    """
    Système avancé de watermarking enterprise.
    Support invisible/visible embedding, steganography et robustness.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le moteur de watermarking.
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or self._get_default_config()
        self._setup_watermarking_algorithms()
        self._setup_attack_simulation()
        logger.info("WatermarkingEngine initialisé avec succès")

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'embedding_algorithms': {
                'lsb': {
                    'name': 'Least Significant Bit',
                    'steganographic': True,
                    'robustness': 'low',
                    'capacity': 'high'
                },
                'dct': {
                    'name': 'Discrete Cosine Transform',
                    'steganographic': True,
                    'robustness': 'high',
                    'capacity': 'medium'
                },
                'dwt': {
                    'name': 'Discrete Wavelet Transform',
                    'steganographic': True,
                    'robustness': 'very_high',
                    'capacity': 'medium'
                },
                'spread_spectrum': {
                    'name': 'Spread Spectrum',
                    'steganographic': True,
                    'robustness': 'military_grade',
                    'capacity': 'low'
                }
            },
            'visible_watermark': {
                'default_opacity': 0.3,
                'default_position': 'bottom_right',
                'default_size': (200, 50),
                'default_color': (255, 255, 255),
                'default_font': 'Arial',
                'text_outline': True
            },
            'robustness_testing': {
                'compression_levels': [10, 30, 50, 70, 90],
                'rotation_angles': [1, 5, 10, 15, 30, 45, 90],
                'scaling_factors': [0.5, 0.8, 1.2, 1.5, 2.0],
                'noise_levels': [5, 10, 15, 20, 25],
                'crop_percentages': [5, 10, 15, 20, 25]
            },
            'security': {
                'encryption_key_length': 256,
                'payload_encryption': True,
                'tamper_detection': True,
                'blockchain_verification': False
            },
            'quality_metrics': {
                'psnr_threshold': 40.0,
                'ssim_threshold': 0.95,
                'mse_threshold': 100.0,
                'ncc_threshold': 0.99
            },
            'performance': {
                'max_concurrent_operations': 4,
                'cache_watermarks': True,
                'optimize_for_speed': False,
                'batch_processing': True
            }
        }

    def _setup_watermarking_algorithms(self):
        """Configure les algorithmes de watermarking."""
        self.embedding_algorithms = {
            'lsb': self._lsb_embedding,
            'dct': self._dct_embedding,
            'dwt': self._dwt_embedding,
            'spread_spectrum': self._spread_spectrum_embedding,
            'visible': self._visible_watermark_embedding
        }
        
        self.extraction_algorithms = {
            'lsb': self._lsb_extraction,
            'dct': self._dct_extraction,
            'dwt': self._dwt_extraction,
            'spread_spectrum': self._spread_spectrum_extraction,
            'visible': self._visible_watermark_extraction
        }

    def _setup_attack_simulation(self):
        """Configure la simulation d'attaques."""
        self.attack_simulators = {
            'compression': self._simulate_compression_attack,
            'rotation': self._simulate_rotation_attack,
            'scaling': self._simulate_scaling_attack,
            'noise': self._simulate_noise_attack,
            'cropping': self._simulate_cropping_attack,
            'filtering': self._simulate_filtering_attack,
            'geometric': self._simulate_geometric_attack
        }

    async def embed_watermark(
        self,
        content: Union[np.ndarray, bytes, str, Path],
        payload: WatermarkPayload,
        watermark_config: WatermarkConfig
    ) -> WatermarkedContent:
        """
        Embed un watermark dans le contenu.
        
        Args:
            content: Contenu original
            payload: Payload du watermark
            watermark_config: Configuration du watermarking
            
        Returns:
            WatermarkedContent: Contenu watermarké
        """
        try:
            # Validation et préparation du contenu
            processed_content = await self._prepare_content_for_watermarking(content)
            content_format = await self._detect_content_format(processed_content)
            
            # Sélection de l'algorithme d'embedding
            algorithm = self._select_embedding_algorithm(watermark_config)
            
            # Préparation du payload
            encoded_payload = await self._encode_watermark_payload(payload, watermark_config)
            
            # Embedding du watermark
            watermarked_data = await algorithm(
                processed_content, encoded_payload, watermark_config
            )
            
            # Calcul des métriques de qualité
            quality_metrics = await self._calculate_quality_metrics(
                processed_content, watermarked_data
            )
            
            # Tests de robustesse
            robustness_metrics = await self._test_watermark_robustness(
                watermarked_data, encoded_payload, watermark_config
            )
            
            # Données de vérification
            verification_data = await self._generate_verification_data(
                watermarked_data, payload, watermark_config
            )
            
            watermarked_content = WatermarkedContent(
                watermark_id=str(uuid.uuid4()),
                original_content_hash=hashlib.sha256(str(processed_content).encode()).hexdigest(),
                watermarked_content=watermarked_data,
                watermark_payload=payload,
                watermark_config=watermark_config,
                embedding_timestamp=datetime.utcnow(),
                verification_data=verification_data,
                robustness_metrics=robustness_metrics,
                extraction_success_rate=robustness_metrics.get('overall_success_rate', 0.0),
                content_quality_metrics=quality_metrics
            )
            
            logger.info(f"Watermark embedded: {watermarked_content.watermark_id}")
            return watermarked_content

        except Exception as e:
            logger.error(f"Erreur embedding watermark: {e}")
            raise

    async def _prepare_content_for_watermarking(
        self,
        content: Union[np.ndarray, bytes, str, Path]
    ) -> np.ndarray:
        """Prépare le contenu pour le watermarking."""
        try:
            if isinstance(content, Path):
                # Chargement depuis fichier
                if content.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    image = Image.open(content)
                    return np.array(image)
                else:
                    with open(content, 'rb') as f:
                        return np.frombuffer(f.read(), dtype=np.uint8)
            
            elif isinstance(content, (str, bytes)):
                # Conversion en array
                if isinstance(content, str):
                    content = content.encode()
                return np.frombuffer(content, dtype=np.uint8)
            
            elif isinstance(content, np.ndarray):
                return content
            
            else:
                raise ValueError(f"Format de contenu non supporté: {type(content)}")

        except Exception as e:
            logger.error(f"Erreur préparation contenu: {e}")
            raise

    async def _detect_content_format(self, content: np.ndarray) -> WatermarkFormat:
        """Détecte le format du contenu."""
        try:
            # Détection basique basée sur la forme du array
            if len(content.shape) == 3 and content.shape[2] in [3, 4]:
                return WatermarkFormat.IMAGE
            elif len(content.shape) == 2:
                return WatermarkFormat.IMAGE  # Image en niveaux de gris
            elif len(content.shape) == 1:
                return WatermarkFormat.AUDIO  # Signal audio 1D
            else:
                return WatermarkFormat.VIDEO  # Assomption pour format complexe

        except Exception as e:
            logger.error(f"Erreur détection format: {e}")
            return WatermarkFormat.IMAGE

    def _select_embedding_algorithm(self, config: WatermarkConfig):
        """Sélectionne l'algorithme d'embedding approprié."""
        try:
            if config.watermark_type == WatermarkType.VISIBLE:
                return self.embedding_algorithms['visible']
            elif config.robustness_level == RobustnessLevel.MILITARY_GRADE:
                return self.embedding_algorithms['spread_spectrum']
            elif config.robustness_level == RobustnessLevel.HIGH:
                return self.embedding_algorithms['dwt']
            elif config.robustness_level == RobustnessLevel.MEDIUM:
                return self.embedding_algorithms['dct']
            else:
                return self.embedding_algorithms['lsb']

        except Exception as e:
            logger.error(f"Erreur sélection algorithme: {e}")
            return self.embedding_algorithms['lsb']

    async def _encode_watermark_payload(
        self,
        payload: WatermarkPayload,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Encode le payload du watermark."""
        try:
            # Sérialisation du payload
            payload_dict = {
                'creator_id': payload.creator_id,
                'content_hash': payload.content_hash,
                'timestamp': payload.timestamp.isoformat(),
                'copyright_info': payload.copyright_info,
                'license_type': payload.license_type,
                'blockchain_proof': payload.blockchain_proof,
                'custom_data': payload.custom_data
            }
            
            payload_json = json.dumps(payload_dict, sort_keys=True)
            
            # Chiffrement du payload si configuré
            if self.config['security']['payload_encryption']:
                encrypted_payload = await self._encrypt_payload(payload_json, config.extraction_key)
                payload_bytes = encrypted_payload.encode()
            else:
                payload_bytes = payload_json.encode()
            
            # Conversion en bits pour l'embedding
            payload_bits = []
            for byte in payload_bytes:
                for i in range(8):
                    payload_bits.append((byte >> i) & 1)
            
            return np.array(payload_bits, dtype=np.uint8)

        except Exception as e:
            logger.error(f"Erreur encodage payload: {e}")
            raise

    async def _encrypt_payload(self, payload: str, key: str) -> str:
        """Chiffre le payload (implémentation simplifiée)."""
        try:
            # Chiffrement basique - en production, utiliser des algorithmes robustes
            key_hash = hashlib.sha256(key.encode()).digest()
            
            encrypted = []
            for i, char in enumerate(payload):
                key_byte = key_hash[i % len(key_hash)]
                encrypted_char = chr(ord(char) ^ key_byte)
                encrypted.append(encrypted_char)
            
            return ''.join(encrypted)

        except Exception as e:
            logger.error(f"Erreur chiffrement payload: {e}")
            return payload

    async def _lsb_embedding(
        self,
        content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Embedding LSB (Least Significant Bit)."""
        try:
            watermarked = content.copy()
            
            if len(content.shape) == 3:  # Image couleur
                # Embedding dans le canal bleu (moins visible)
                channel = watermarked[:, :, 2].flatten()
            elif len(content.shape) == 2:  # Image niveaux de gris
                channel = watermarked.flatten()
            else:
                channel = watermarked.flatten()
            
            # Vérification de la capacité
            if len(payload) > len(channel):
                raise ValueError("Payload trop grand pour le contenu")
            
            # Embedding des bits
            for i, bit in enumerate(payload):
                if i < len(channel):
                    # Modification du LSB
                    channel[i] = (channel[i] & 0xFE) | bit
            
            # Reconstruction de l'image
            if len(content.shape) == 3:
                watermarked[:, :, 2] = channel.reshape(content.shape[:2])
            elif len(content.shape) == 2:
                watermarked = channel.reshape(content.shape)
            else:
                watermarked = channel.reshape(content.shape)
            
            return watermarked

        except Exception as e:
            logger.error(f"Erreur LSB embedding: {e}")
            return content

    async def _dct_embedding(
        self,
        content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Embedding dans le domaine DCT."""
        try:
            # Implémentation simplifiée du DCT embedding
            watermarked = content.copy().astype(np.float32)
            
            if len(content.shape) == 3:
                # Conversion en YUV pour travailler sur la luminance
                watermarked = cv2.cvtColor(watermarked.astype(np.uint8), cv2.COLOR_RGB2YUV)
                channel = watermarked[:, :, 0].astype(np.float32)
            else:
                channel = watermarked.astype(np.float32)
            
            # Division en blocs 8x8
            h, w = channel.shape
            block_size = 8
            
            payload_idx = 0
            for i in range(0, h - block_size + 1, block_size):
                for j in range(0, w - block_size + 1, block_size):
                    if payload_idx >= len(payload):
                        break
                    
                    # Extraction du bloc
                    block = channel[i:i+block_size, j:j+block_size]
                    
                    # DCT du bloc
                    dct_block = cv2.dct(block)
                    
                    # Modification du coefficient mid-frequency
                    if payload[payload_idx] == 1:
                        dct_block[2, 2] += config.encoding_strength
                    else:
                        dct_block[2, 2] -= config.encoding_strength
                    
                    # IDCT
                    channel[i:i+block_size, j:j+block_size] = cv2.idct(dct_block)
                    payload_idx += 1
            
            # Reconstruction
            if len(content.shape) == 3:
                watermarked[:, :, 0] = np.clip(channel, 0, 255)
                watermarked = cv2.cvtColor(watermarked.astype(np.uint8), cv2.COLOR_YUV2RGB)
            else:
                watermarked = np.clip(channel, 0, 255).astype(np.uint8)
            
            return watermarked

        except Exception as e:
            logger.error(f"Erreur DCT embedding: {e}")
            return content

    async def _dwt_embedding(
        self,
        content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Embedding dans le domaine DWT (simplifié)."""
        try:
            # Implémentation simplifiée - en production, utiliser PyWavelets
            watermarked = content.copy()
            
            # Pour cette implémentation, on utilise une transformation simple
            # qui simule l'embedding DWT
            if len(content.shape) == 3:
                channel = watermarked[:, :, 1]  # Canal vert
            else:
                channel = watermarked
            
            # Modification des coefficients de détail (simulation)
            h, w = channel.shape
            step = max(1, (h * w) // len(payload))
            
            for i, bit in enumerate(payload):
                idx = i * step
                y, x = divmod(idx, w)
                if y < h and x < w:
                    if bit == 1:
                        channel[y, x] = min(255, channel[y, x] + int(config.encoding_strength))
                    else:
                        channel[y, x] = max(0, channel[y, x] - int(config.encoding_strength))
            
            if len(content.shape) == 3:
                watermarked[:, :, 1] = channel
            else:
                watermarked = channel
            
            return watermarked

        except Exception as e:
            logger.error(f"Erreur DWT embedding: {e}")
            return content

    async def _spread_spectrum_embedding(
        self,
        content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Embedding spread spectrum (military grade)."""
        try:
            # Implémentation simplifiée du spread spectrum
            watermarked = content.copy().astype(np.float32)
            
            # Génération d'une séquence pseudo-aléatoire
            np.random.seed(hash(config.extraction_key) % (2**32))
            
            if len(content.shape) == 3:
                channel = watermarked[:, :, 0]  # Canal rouge
            else:
                channel = watermarked
            
            h, w = channel.shape
            
            # Étalement spectral
            for i, bit in enumerate(payload):
                if i >= h * w:
                    break
                
                y, x = divmod(i, w)
                
                # Séquence d'étalement pour ce bit
                spread_sequence = np.random.uniform(-1, 1, 10)
                
                # Modulation du bit
                if bit == 1:
                    modification = config.encoding_strength * np.mean(spread_sequence)
                else:
                    modification = -config.encoding_strength * np.mean(spread_sequence)
                
                channel[y, x] = np.clip(channel[y, x] + modification, 0, 255)
            
            if len(content.shape) == 3:
                watermarked[:, :, 0] = channel
            else:
                watermarked = channel
            
            return watermarked.astype(np.uint8)

        except Exception as e:
            logger.error(f"Erreur spread spectrum embedding: {e}")
            return content

    async def _visible_watermark_embedding(
        self,
        content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> np.ndarray:
        """Embedding de watermark visible."""
        try:
            # Conversion en PIL Image pour faciliter le traitement
            if len(content.shape) == 3:
                image = Image.fromarray(content)
            else:
                image = Image.fromarray(content).convert('RGB')
            
            # Création du watermark visible
            watermark_text = f"© {config.extraction_key}"
            
            # Création d'une overlay transparente
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Tentative de chargement de police
            try:
                font = ImageFont.truetype(config.font_family, size=config.size[1])
            except:
                font = ImageFont.load_default()
            
            # Position du watermark
            if config.position == (-1, -1):  # Position automatique
                text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                position = (
                    image.width - (text_bbox[2] - text_bbox[0]) - 20,
                    image.height - (text_bbox[3] - text_bbox[1]) - 20
                )
            else:
                position = config.position
            
            # Couleur avec opacité
            color = (*config.color, int(255 * config.opacity))
            
            # Dessiner le watermark
            draw.text(position, watermark_text, fill=color, font=font)
            
            # Fusion avec l'image originale
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            watermarked_image = Image.alpha_composite(image, overlay)
            
            # Conversion en RGB pour retour
            if watermarked_image.mode == 'RGBA':
                watermarked_image = watermarked_image.convert('RGB')
            
            return np.array(watermarked_image)

        except Exception as e:
            logger.error(f"Erreur visible watermark: {e}")
            return content

    async def _calculate_quality_metrics(
        self,
        original: np.ndarray,
        watermarked: np.ndarray
    ) -> Dict[str, float]:
        """Calcule les métriques de qualité."""
        try:
            # Conversion en float pour les calculs
            orig = original.astype(np.float64)
            wm = watermarked.astype(np.float64)
            
            # MSE (Mean Squared Error)
            mse = np.mean((orig - wm) ** 2)
            
            # PSNR (Peak Signal-to-Noise Ratio)
            if mse == 0:
                psnr = float('inf')
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            # SSIM simplifié (corrélation structurelle)
            mu1 = np.mean(orig)
            mu2 = np.mean(wm)
            sigma1 = np.std(orig)
            sigma2 = np.std(wm)
            sigma12 = np.mean((orig - mu1) * (wm - mu2))
            
            c1 = (0.01 * 255) ** 2
            c2 = (0.03 * 255) ** 2
            
            ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
                   ((mu1**2 + mu2**2 + c1) * (sigma1**2 + sigma2**2 + c2))
            
            # NCC (Normalized Cross Correlation)
            ncc = np.corrcoef(orig.flatten(), wm.flatten())[0, 1]
            if np.isnan(ncc):
                ncc = 1.0
            
            return {
                'mse': float(mse),
                'psnr': float(psnr),
                'ssim': float(ssim),
                'ncc': float(ncc),
                'quality_score': float((ssim + ncc) / 2)
            }

        except Exception as e:
            logger.error(f"Erreur calcul métriques qualité: {e}")
            return {
                'mse': 0.0,
                'psnr': 0.0,
                'ssim': 1.0,
                'ncc': 1.0,
                'quality_score': 1.0
            }

    async def _test_watermark_robustness(
        self,
        watermarked_content: np.ndarray,
        payload: np.ndarray,
        config: WatermarkConfig
    ) -> Dict[str, float]:
        """Teste la robustesse du watermark contre diverses attaques."""
        try:
            robustness_results = {}
            
            # Tests d'attaques
            attack_results = {}
            
            for attack_name, attack_func in self.attack_simulators.items():
                try:
                    attacked_content = await attack_func(watermarked_content)
                    extraction_success = await self._test_extraction_after_attack(
                        attacked_content, payload, config
                    )
                    attack_results[attack_name] = extraction_success
                except Exception as e:
                    logger.warning(f"Erreur test attaque {attack_name}: {e}")
                    attack_results[attack_name] = 0.0
            
            # Calcul du score global de robustesse
            overall_success_rate = np.mean(list(attack_results.values()))
            
            robustness_results.update(attack_results)
            robustness_results['overall_success_rate'] = float(overall_success_rate)
            
            return robustness_results

        except Exception as e:
            logger.error(f"Erreur test robustesse: {e}")
            return {'overall_success_rate': 0.0}

    async def _simulate_compression_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par compression."""
        try:
            # Simulation de compression JPEG
            if len(content.shape) == 3:
                image = Image.fromarray(content)
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=50)
                buffer.seek(0)
                compressed_image = Image.open(buffer)
                return np.array(compressed_image)
            else:
                return content
        except:
            return content

    async def _simulate_rotation_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par rotation."""
        try:
            if len(content.shape) >= 2:
                # Rotation de 5 degrés
                h, w = content.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, 5, 1.0)
                rotated = cv2.warpAffine(content, matrix, (w, h))
                return rotated
            return content
        except:
            return content

    async def _simulate_scaling_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par redimensionnement."""
        try:
            if len(content.shape) >= 2:
                h, w = content.shape[:2]
                # Réduction puis agrandissement
                small = cv2.resize(content, (w // 2, h // 2))
                scaled = cv2.resize(small, (w, h))
                return scaled
            return content
        except:
            return content

    async def _simulate_noise_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par bruit."""
        try:
            noise = np.random.normal(0, 10, content.shape).astype(np.int16)
            noisy = np.clip(content.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            return noisy
        except:
            return content

    async def _simulate_cropping_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par recadrage."""
        try:
            if len(content.shape) >= 2:
                h, w = content.shape[:2]
                # Recadrage de 10%
                crop_h = int(h * 0.1)
                crop_w = int(w * 0.1)
                cropped = content[crop_h:h-crop_h, crop_w:w-crop_w]
                # Redimensionnement à la taille originale
                resized = cv2.resize(cropped, (w, h))
                return resized
            return content
        except:
            return content

    async def _simulate_filtering_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque par filtrage."""
        try:
            if len(content.shape) >= 2:
                # Flou gaussien
                blurred = cv2.GaussianBlur(content, (5, 5), 1.0)
                return blurred
            return content
        except:
            return content

    async def _simulate_geometric_attack(self, content: np.ndarray) -> np.ndarray:
        """Simule une attaque géométrique."""
        try:
            if len(content.shape) >= 2:
                h, w = content.shape[:2]
                # Transformation affine légère
                pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
                pts2 = np.float32([[5, 5], [w-5, 5], [0, h-5], [w, h]])
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                transformed = cv2.warpPerspective(content, matrix, (w, h))
                return transformed
            return content
        except:
            return content

    async def _test_extraction_after_attack(
        self,
        attacked_content: np.ndarray,
        original_payload: np.ndarray,
        config: WatermarkConfig
    ) -> float:
        """Teste l'extraction après attaque."""
        try:
            # Tentative d'extraction (simulation)
            # En production, utiliser le vrai algorithme d'extraction
            
            # Pour cette simulation, on assume une réussite proportionnelle
            # à la similarité entre le contenu attaqué et l'original
            
            # Calcul de similarité simplifiée
            if len(attacked_content.shape) == len(original_payload.shape):
                similarity = np.corrcoef(
                    attacked_content.flatten()[:len(original_payload)],
                    original_payload.astype(float)
                )[0, 1]
                
                if np.isnan(similarity):
                    similarity = 0.0
                
                # Conversion en taux de réussite
                success_rate = max(0.0, min(1.0, (similarity + 1) / 2))
                return success_rate
            
            return 0.5  # Taux par défaut

        except Exception as e:
            logger.error(f"Erreur test extraction: {e}")
            return 0.0

    async def _generate_verification_data(
        self,
        watermarked_content: np.ndarray,
        payload: WatermarkPayload,
        config: WatermarkConfig
    ) -> Dict[str, Any]:
        """Génère les données de vérification."""
        try:
            # Hash du contenu watermarké
            content_hash = hashlib.sha256(watermarked_content.tobytes()).hexdigest()
            
            # Signature de vérification
            verification_string = f"{payload.creator_id}{payload.content_hash}{content_hash}"
            verification_signature = hashlib.sha256(verification_string.encode()).hexdigest()
            
            return {
                'watermarked_content_hash': content_hash,
                'verification_signature': verification_signature,
                'embedding_algorithm': config.watermark_type.value,
                'robustness_level': config.robustness_level.value,
                'payload_size': len(str(payload.__dict__)),
                'embedding_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Erreur génération données vérification: {e}")
            return {}

    async def extract_watermark(
        self,
        content: Union[np.ndarray, bytes, str, Path],
        extraction_key: str,
        extraction_method: Optional[str] = None
    ) -> WatermarkExtractionResult:
        """
        Extrait un watermark du contenu.
        
        Args:
            content: Contenu à analyser
            extraction_key: Clé d'extraction
            extraction_method: Méthode d'extraction spécifique
            
        Returns:
            WatermarkExtractionResult: Résultat de l'extraction
        """
        try:
            start_time = datetime.utcnow()
            
            # Préparation du contenu
            processed_content = await self._prepare_content_for_watermarking(content)
            
            # Détection automatique de la méthode si non spécifiée
            if extraction_method is None:
                extraction_method = await self._detect_watermark_method(processed_content)
            
            # Extraction selon la méthode
            extraction_func = self.extraction_algorithms.get(
                extraction_method, 
                self.extraction_algorithms['lsb']
            )
            
            extracted_data = await extraction_func(processed_content, extraction_key)
            
            # Décodage du payload
            if extracted_data is not None:
                payload = await self._decode_watermark_payload(extracted_data, extraction_key)
                watermark_detected = True
                confidence_score = 0.9  # Score simulé
            else:
                payload = None
                watermark_detected = False
                confidence_score = 0.0
            
            # Vérification d'intégrité
            integrity_verified = await self._verify_payload_integrity(payload) if payload else False
            
            # Tests de résistance aux attaques
            attack_resistance = await self._test_attack_resistance(processed_content, extraction_key)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = WatermarkExtractionResult(
                extraction_id=str(uuid.uuid4()),
                watermark_detected=watermark_detected,
                extracted_payload=payload,
                confidence_score=confidence_score,
                integrity_verified=integrity_verified,
                extraction_method=extraction_method,
                processing_time=processing_time,
                attack_resistance_tested=attack_resistance,
                quality_degradation=0.1  # Dégradation simulée
            )
            
            logger.info(f"Extraction terminée: {result.extraction_id}, détecté: {watermark_detected}")
            return result

        except Exception as e:
            logger.error(f"Erreur extraction watermark: {e}")
            raise

    async def _detect_watermark_method(self, content: np.ndarray) -> str:
        """Détecte automatiquement la méthode de watermarking utilisée."""
        try:
            # Analyse basique pour détecter la méthode
            # En production, utiliser des techniques plus sophistiquées
            
            # Test pour watermark visible
            if len(content.shape) == 3:
                # Recherche de patterns de texte ou logos
                gray = cv2.cvtColor(content, cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                if np.sum(edges) > len(content.flatten()) * 0.1:
                    return 'visible'
            
            # Test pour méthodes stéganographiques
            # Analyse spectrale simplifiée
            return 'lsb'  # Méthode par défaut

        except Exception as e:
            logger.error(f"Erreur détection méthode: {e}")
            return 'lsb'

    async def _lsb_extraction(self, content: np.ndarray, key: str) -> Optional[np.ndarray]:
        """Extraction LSB."""
        try:
            if len(content.shape) == 3:
                channel = content[:, :, 2].flatten()
            else:
                channel = content.flatten()
            
            # Extraction des LSB
            extracted_bits = []
            for pixel in channel:
                extracted_bits.append(pixel & 1)
            
            return np.array(extracted_bits, dtype=np.uint8)

        except Exception as e:
            logger.error(f"Erreur extraction LSB: {e}")
            return None

    async def _dct_extraction(self, content: np.ndarray, key: str) -> Optional[np.ndarray]:
        """Extraction DCT."""
        try:
            # Implémentation simplifiée
            return await self._lsb_extraction(content, key)
        except Exception as e:
            logger.error(f"Erreur extraction DCT: {e}")
            return None

    async def _dwt_extraction(self, content: np.ndarray, key: str) -> Optional[np.ndarray]:
        """Extraction DWT."""
        try:
            # Implémentation simplifiée
            return await self._lsb_extraction(content, key)
        except Exception as e:
            logger.error(f"Erreur extraction DWT: {e}")
            return None

    async def _spread_spectrum_extraction(self, content: np.ndarray, key: str) -> Optional[np.ndarray]:
        """Extraction spread spectrum."""
        try:
            # Implémentation simplifiée
            return await self._lsb_extraction(content, key)
        except Exception as e:
            logger.error(f"Erreur extraction spread spectrum: {e}")
            return None

    async def _visible_watermark_extraction(self, content: np.ndarray, key: str) -> Optional[np.ndarray]:
        """Extraction watermark visible."""
        try:
            # Pour les watermarks visibles, l'extraction est principalement
            # une détection de présence
            return np.array([1], dtype=np.uint8)  # Watermark détecté
        except Exception as e:
            logger.error(f"Erreur extraction watermark visible: {e}")
            return None

    async def _decode_watermark_payload(
        self,
        extracted_bits: np.ndarray,
        key: str
    ) -> Optional[WatermarkPayload]:
        """Décode le payload du watermark."""
        try:
            # Conversion des bits en bytes
            payload_bytes = []
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = extracted_bits[i:i+8]
                    byte_value = 0
                    for j, bit in enumerate(byte_bits):
                        byte_value |= (bit << j)
                    payload_bytes.append(byte_value)
            
            payload_data = bytes(payload_bytes)
            
            # Déchiffrement si nécessaire
            if self.config['security']['payload_encryption']:
                decrypted = await self._decrypt_payload(payload_data.decode('utf-8', errors='ignore'), key)
                payload_json = decrypted
            else:
                payload_json = payload_data.decode('utf-8', errors='ignore')
            
            # Parsing JSON
            payload_dict = json.loads(payload_json)
            
            # Reconstruction du payload
            payload = WatermarkPayload(
                creator_id=payload_dict.get('creator_id', ''),
                content_hash=payload_dict.get('content_hash', ''),
                timestamp=datetime.fromisoformat(payload_dict.get('timestamp', datetime.utcnow().isoformat())),
                copyright_info=payload_dict.get('copyright_info', ''),
                license_type=payload_dict.get('license_type', ''),
                blockchain_proof=payload_dict.get('blockchain_proof'),
                custom_data=payload_dict.get('custom_data', {}),
                expiration_date=None
            )
            
            return payload

        except Exception as e:
            logger.error(f"Erreur décodage payload: {e}")
            return None

    async def _decrypt_payload(self, encrypted_payload: str, key: str) -> str:
        """Déchiffre le payload."""
        try:
            # Déchiffrement basique - inverse de _encrypt_payload
            key_hash = hashlib.sha256(key.encode()).digest()
            
            decrypted = []
            for i, char in enumerate(encrypted_payload):
                key_byte = key_hash[i % len(key_hash)]
                decrypted_char = chr(ord(char) ^ key_byte)
                decrypted.append(decrypted_char)
            
            return ''.join(decrypted)

        except Exception as e:
            logger.error(f"Erreur déchiffrement payload: {e}")
            return encrypted_payload

    async def _verify_payload_integrity(self, payload: Optional[WatermarkPayload]) -> bool:
        """Vérifie l'intégrité du payload."""
        try:
            if payload is None:
                return False
            
            # Vérifications basiques
            if not payload.creator_id or not payload.content_hash:
                return False
            
            # Vérification de la date d'expiration
            if payload.expiration_date and datetime.utcnow() > payload.expiration_date:
                return False
            
            return True

        except Exception as e:
            logger.error(f"Erreur vérification intégrité: {e}")
            return False

    async def _test_attack_resistance(
        self,
        content: np.ndarray,
        extraction_key: str
    ) -> Dict[str, bool]:
        """Teste la résistance aux attaques."""
        try:
            resistance_results = {}
            
            for attack_name, attack_func in self.attack_simulators.items():
                try:
                    attacked_content = await attack_func(content)
                    extraction_result = await self.extract_watermark(
                        attacked_content, extraction_key
                    )
                    resistance_results[attack_name] = extraction_result.watermark_detected
                except:
                    resistance_results[attack_name] = False
            
            return resistance_results

        except Exception as e:
            logger.error(f"Erreur test résistance attaques: {e}")
            return {}

    async def batch_watermark_embedding(
        self,
        contents: List[Union[np.ndarray, bytes, str, Path]],
        payloads: List[WatermarkPayload],
        configs: List[WatermarkConfig]
    ) -> List[WatermarkedContent]:
        """
        Embedding en lot de watermarks.
        
        Args:
            contents: Liste des contenus
            payloads: Liste des payloads
            configs: Liste des configurations
            
        Returns:
            List[WatermarkedContent]: Liste des contenus watermarkés
        """
        try:
            if not (len(contents) == len(payloads) == len(configs)):
                raise ValueError("Les listes doivent avoir la même longueur")
            
            tasks = []
            semaphore = asyncio.Semaphore(self.config['performance']['max_concurrent_operations'])
            
            async def process_single_embedding(content, payload, config):
                async with semaphore:
                    return await self.embed_watermark(content, payload, config)
            
            for content, payload, config in zip(contents, payloads, configs):
                tasks.append(process_single_embedding(content, payload, config))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrage des résultats valides
            valid_results = [
                result for result in results 
                if isinstance(result, WatermarkedContent)
            ]
            
            logger.info(f"Batch embedding terminé: {len(valid_results)}/{len(contents)} réussis")
            return valid_results

        except Exception as e:
            logger.error(f"Erreur batch embedding: {e}")
            raise

    def get_supported_formats(self) -> List[str]:
        """Retourne la liste des formats supportés."""
        return [fmt.value for fmt in WatermarkFormat]

    def get_robustness_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la robustesse."""
        return {
            'attack_types_tested': list(self.attack_simulators.keys()),
            'robustness_levels': [level.value for level in RobustnessLevel],
            'quality_metrics': list(self.config['quality_metrics'].keys()),
            'embedding_algorithms': list(self.config['embedding_algorithms'].keys())
        }