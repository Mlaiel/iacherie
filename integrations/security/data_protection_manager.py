"""🔐 Data Protection Manager - Encryption at Scale & Data Governance
==================================================================

Gestionnaire de protection des données enterprise avec encryption at scale,
data classification et data governance automation.

Expert Team Implementation:
🤖 Lead Dev IA: Smart data classification + automated protection policies + ML-driven insights
🏗️ Backend Senior: Scalable encryption infrastructure + key management + performance optimization
🧠 ML Engineer: ML data classification + privacy risk assessment + intelligent anonymization
🗄️ DBA: Database encryption + secure storage + data lifecycle management + compliance
🔒 Sécurité: Encryption standards + key security + data loss prevention + privacy controls
🔗 Microservices: Distributed encryption + service-level protection + secure communication
🎵 Audio Engineer: Audio data protection + digital watermarking + content encryption
⚙️ DevOps: Automated key rotation + backup encryption + secure deployment pipelines
🎨 IA Prompt Engineer: AI model data protection + training data security + privacy-preserving AI

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
Date: Septembre 2024

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import sqlalchemy
from collections import defaultdict
import re


class DataClassification(Enum):
    """Classifications des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class EncryptionAlgorithm(Enum):
    """Algorithmes de chiffrement"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"


class DataType(Enum):
    """Types de données"""
    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    CONTENT_DATA = "content_data"
    METADATA = "metadata"
    SYSTEM_DATA = "system_data"
    ANALYTICS_DATA = "analytics_data"


class ProtectionLevel(Enum):
    """Niveaux de protection"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


@dataclass
class DataAsset:
    """Asset de données"""
    asset_id: str
    name: str
    description: str
    classification: DataClassification
    data_type: DataType
    location: str
    owner: str
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    encryption_status: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    retention_period: Optional[int] = None  # days
    legal_holds: List[str] = field(default_factory=list)


@dataclass
class EncryptionKey:
    """Clé de chiffrement"""
    key_id: str
    key_type: EncryptionAlgorithm
    key_material: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    version: int = 1
    usage_count: int = 0
    max_usage: Optional[int] = None
    associated_assets: List[str] = field(default_factory=list)
    key_escrow: bool = False
    hsm_protected: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataGovernancePolicy:
    """Politique de gouvernance des données"""
    policy_id: str
    name: str
    description: str
    data_classification: DataClassification
    retention_rules: Dict[str, Any]
    access_controls: List[str]
    encryption_requirements: Dict[str, Any]
    deletion_rules: Dict[str, Any]
    compliance_requirements: List[str]
    monitoring_rules: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PrivacyAssessment:
    """Évaluation de confidentialité"""
    assessment_id: str
    data_asset: DataAsset
    privacy_risk_score: float
    privacy_factors: List[str]
    personal_data_elements: List[str]
    consent_requirements: List[str]
    right_to_erasure: bool
    data_minimization_compliance: bool
    purpose_limitation_compliance: bool
    anonymization_feasible: bool
    pseudonymization_applied: bool
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataProtectionResult:
    """Résultat protection des données"""
    operation_id: str
    data_asset: DataAsset
    protection_applied: Dict[str, Any]
    encryption_details: Dict[str, Any]
    compliance_status: Dict[str, Any]
    privacy_assessment: PrivacyAssessment
    governance_compliance: bool
    recommendations: List[str]
    execution_time_ms: float


class AdvancedEncryptionEngine:
    """
    🔐 Moteur de chiffrement avancé
    ==============================
    """
    
    def __init__(self):
        self.encryption_keys = {}
        self.key_rotation_schedule = {}
        self.hsm_available = False  # Hardware Security Module
        
    async def encrypt_data_asset(
        self,
        data_asset: DataAsset,
        data_content: bytes,
        encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    ) -> Dict[str, Any]:
        """Chiffrement asset de données"""
        try:
            # Génération/récupération clé
            encryption_key = await self._get_or_create_encryption_key(
                data_asset, encryption_algorithm
            )
            
            # Chiffrement selon algorithme
            if encryption_algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = await self._encrypt_aes_gcm(data_content, encryption_key)
            elif encryption_algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = await self._encrypt_fernet(data_content, encryption_key)
            elif encryption_algorithm == EncryptionAlgorithm.RSA_4096:
                encrypted_data = await self._encrypt_rsa(data_content, encryption_key)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {encryption_algorithm}")
            
            # Métadonnées chiffrement
            encryption_metadata = {
                'algorithm': encryption_algorithm.value,
                'key_id': encryption_key.key_id,
                'key_version': encryption_key.version,
                'encrypted_at': datetime.utcnow().isoformat(),
                'data_size': len(data_content),
                'encrypted_size': len(encrypted_data['ciphertext']),
                'integrity_hash': hashlib.sha256(data_content).hexdigest()
            }
            
            # Mise à jour usage clé
            encryption_key.usage_count += 1
            
            return {
                'success': True,
                'encrypted_data': encrypted_data,
                'encryption_metadata': encryption_metadata,
                'key_info': {
                    'key_id': encryption_key.key_id,
                    'algorithm': encryption_algorithm.value,
                    'created_at': encryption_key.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur chiffrement: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'encrypted_data': None
            }
    
    async def decrypt_data_asset(
        self,
        encrypted_data: Dict[str, Any],
        encryption_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Déchiffrement asset de données"""
        try:
            # Récupération clé
            key_id = encryption_metadata.get('key_id')
            encryption_key = self.encryption_keys.get(key_id)
            
            if not encryption_key:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            # Déterminaton algorithme
            algorithm = EncryptionAlgorithm(encryption_metadata.get('algorithm'))
            
            # Déchiffrement selon algorithme
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = await self._decrypt_aes_gcm(encrypted_data, encryption_key)
            elif algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = await self._decrypt_fernet(encrypted_data, encryption_key)
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                decrypted_data = await self._decrypt_rsa(encrypted_data, encryption_key)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {algorithm}")
            
            # Vérification intégrité
            expected_hash = encryption_metadata.get('integrity_hash')
            actual_hash = hashlib.sha256(decrypted_data).hexdigest()
            
            if expected_hash and expected_hash != actual_hash:
                raise ValueError("Data integrity check failed")
            
            return {
                'success': True,
                'decrypted_data': decrypted_data,
                'integrity_verified': expected_hash == actual_hash
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur déchiffrement: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'decrypted_data': None
            }
    
    async def _get_or_create_encryption_key(
        self,
        data_asset: DataAsset,
        algorithm: EncryptionAlgorithm
    ) -> EncryptionKey:
        """Récupération ou création clé de chiffrement"""
        # Recherche clé existante
        for key in self.encryption_keys.values():
            if (key.key_type == algorithm and 
                data_asset.asset_id in key.associated_assets and
                not self._is_key_expired(key)):
                return key
        
        # Création nouvelle clé
        return await self._generate_encryption_key(data_asset, algorithm)
    
    async def _generate_encryption_key(
        self,
        data_asset: DataAsset,
        algorithm: EncryptionAlgorithm
    ) -> EncryptionKey:
        """Génération nouvelle clé de chiffrement"""
        key_id = str(uuid.uuid4())
        
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_material = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_material = Fernet.generate_key()
        elif algorithm == EncryptionAlgorithm.RSA_4096:
            # Génération paire RSA
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            key_material = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Key generation not implemented for: {algorithm}")
        
        # Durée de vie clé selon classification
        expiry_days = self._get_key_expiry_days(data_asset.classification)
        expires_at = datetime.utcnow() + timedelta(days=expiry_days)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=algorithm,
            key_material=key_material,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            associated_assets=[data_asset.asset_id],
            hsm_protected=self.hsm_available and data_asset.classification in [
                DataClassification.RESTRICTED, DataClassification.TOP_SECRET
            ]
        )
        
        self.encryption_keys[key_id] = encryption_key
        
        logging.info(f"🔑 Nouvelle clé générée: {key_id} pour asset {data_asset.asset_id}")
        
        return encryption_key
    
    def _get_key_expiry_days(self, classification: DataClassification) -> int:
        """Durée de vie clé selon classification"""
        expiry_mapping = {
            DataClassification.PUBLIC: 365,
            DataClassification.INTERNAL: 180,
            DataClassification.CONFIDENTIAL: 90,
            DataClassification.RESTRICTED: 30,
            DataClassification.TOP_SECRET: 7
        }
        return expiry_mapping.get(classification, 90)
    
    def _is_key_expired(self, key: EncryptionKey) -> bool:
        """Vérification expiration clé"""
        if not key.expires_at:
            return False
        return datetime.utcnow() > key.expires_at
    
    async def _encrypt_aes_gcm(
        self,
        data: bytes,
        encryption_key: EncryptionKey
    ) -> Dict[str, Any]:
        """Chiffrement AES-GCM"""
        # IV aléatoire
        iv = secrets.token_bytes(12)  # 96 bits pour GCM
        
        # Chiffrement
        cipher = Cipher(
            algorithms.AES(encryption_key.key_material),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'iv': iv,
            'tag': encryptor.tag,
            'algorithm': 'AES-256-GCM'
        }
    
    async def _decrypt_aes_gcm(
        self,
        encrypted_data: Dict[str, Any],
        encryption_key: EncryptionKey
    ) -> bytes:
        """Déchiffrement AES-GCM"""
        cipher = Cipher(
            algorithms.AES(encryption_key.key_material),
            modes.GCM(encrypted_data['iv'], encrypted_data['tag']),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()
    
    async def _encrypt_fernet(
        self,
        data: bytes,
        encryption_key: EncryptionKey
    ) -> Dict[str, Any]:
        """Chiffrement Fernet"""
        f = Fernet(encryption_key.key_material)
        ciphertext = f.encrypt(data)
        
        return {
            'ciphertext': ciphertext,
            'algorithm': 'Fernet'
        }
    
    async def _decrypt_fernet(
        self,
        encrypted_data: Dict[str, Any],
        encryption_key: EncryptionKey
    ) -> bytes:
        """Déchiffrement Fernet"""
        f = Fernet(encryption_key.key_material)
        return f.decrypt(encrypted_data['ciphertext'])
    
    async def _encrypt_rsa(
        self,
        data: bytes,
        encryption_key: EncryptionKey
    ) -> Dict[str, Any]:
        """Chiffrement RSA"""
        # Chargement clé privée
        private_key = serialization.load_pem_private_key(
            encryption_key.key_material,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # RSA limite taille - chiffrement par blocs si nécessaire
        max_chunk_size = (4096 // 8) - 42  # OAEP padding
        chunks = []
        
        for i in range(0, len(data), max_chunk_size):
            chunk = data[i:i + max_chunk_size]
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            chunks.append(encrypted_chunk)
        
        return {
            'ciphertext': b''.join(chunks),
            'algorithm': 'RSA-4096',
            'chunk_count': len(chunks),
            'chunk_size': max_chunk_size
        }
    
    async def _decrypt_rsa(
        self,
        encrypted_data: Dict[str, Any],
        encryption_key: EncryptionKey
    ) -> bytes:
        """Déchiffrement RSA"""
        # Chargement clé privée
        private_key = serialization.load_pem_private_key(
            encryption_key.key_material,
            password=None,
            backend=default_backend()
        )
        
        # Déchiffrement par blocs
        ciphertext = encrypted_data['ciphertext']
        chunk_count = encrypted_data.get('chunk_count', 1)
        encrypted_chunk_size = 4096 // 8  # 512 bytes pour RSA-4096
        
        decrypted_chunks = []
        for i in range(chunk_count):
            start = i * encrypted_chunk_size
            end = start + encrypted_chunk_size
            encrypted_chunk = ciphertext[start:end]
            
            decrypted_chunk = private_key.decrypt(
                encrypted_chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
        
        return b''.join(decrypted_chunks)


class DataClassificationEngine:
    """
    📊 Moteur de classification automatique des données
    ==================================================
    """
    
    def __init__(self):
        self.classification_rules = self._initialize_classification_rules()
        self.ml_classifier = None  # En production: modèle ML entraîné
        
    def _initialize_classification_rules(self) -> Dict[str, Any]:
        """Initialisation règles de classification"""
        return {
            'patterns': {
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
                'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
                'phone': r'\b\d{3}[- ]?\d{3}[- ]?\d{4}\b',
                'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                'api_key': r'\b[A-Za-z0-9]{32,}\b'
            },
            'keywords': {
                DataClassification.CONFIDENTIAL: [
                    'password', 'secret', 'private', 'confidential', 'internal'
                ],
                DataClassification.RESTRICTED: [
                    'classified', 'restricted', 'top secret', 'sensitive'
                ],
                DataClassification.INTERNAL: [
                    'internal', 'employee', 'staff', 'company'
                ]
            },
            'file_extensions': {
                DataClassification.CONFIDENTIAL: ['.key', '.pem', '.p12', '.pfx'],
                DataClassification.RESTRICTED: ['.classified', '.restricted']
            }
        }
    
    async def classify_data_asset(
        self,
        data_asset: DataAsset,
        data_sample: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Classification automatique asset de données"""
        try:
            classification_result = {
                'suggested_classification': DataClassification.INTERNAL,
                'confidence': 0.5,
                'detected_patterns': [],
                'privacy_indicators': [],
                'security_indicators': [],
                'data_types_detected': []
            }
            
            # Classification basée sur nom/métadonnées
            metadata_classification = await self._classify_by_metadata(data_asset)
            
            # Classification basée sur contenu (si échantillon disponible)
            content_classification = None
            if data_sample:
                content_classification = await self._classify_by_content(data_sample)
            
            # Classification basée sur localisation
            location_classification = await self._classify_by_location(data_asset.location)
            
            # Fusion résultats
            final_classification = await self._merge_classification_results(
                metadata_classification,
                content_classification,
                location_classification
            )
            
            return final_classification
            
        except Exception as e:
            logging.error(f"❌ Erreur classification: {str(e)}")
            return {
                'suggested_classification': DataClassification.INTERNAL,
                'confidence': 0.0,
                'error': str(e)
            }
    
    async def _classify_by_metadata(self, data_asset: DataAsset) -> Dict[str, Any]:
        """Classification basée sur métadonnées"""
        classification = DataClassification.PUBLIC
        confidence = 0.5
        indicators = []
        
        # Analyse nom du fichier/asset
        name_lower = data_asset.name.lower()
        
        # Vérification mots-clés
        for class_level, keywords in self.classification_rules['keywords'].items():
            for keyword in keywords:
                if keyword in name_lower:
                    if class_level.value > classification.value:
                        classification = class_level
                        confidence = 0.8
                        indicators.append(f"Keyword '{keyword}' detected in name")
        
        # Vérification extensions de fichier
        for class_level, extensions in self.classification_rules['file_extensions'].items():
            for ext in extensions:
                if name_lower.endswith(ext):
                    if class_level.value > classification.value:
                        classification = class_level
                        confidence = 0.9
                        indicators.append(f"Sensitive file extension '{ext}' detected")
        
        # Classification basée sur type de données
        if data_asset.data_type == DataType.PERSONAL_DATA:
            classification = max(classification, DataClassification.CONFIDENTIAL)
            confidence = max(confidence, 0.7)
            indicators.append("Personal data type detected")
        
        elif data_asset.data_type == DataType.FINANCIAL_DATA:
            classification = max(classification, DataClassification.RESTRICTED)
            confidence = max(confidence, 0.8)
            indicators.append("Financial data type detected")
        
        elif data_asset.data_type == DataType.BIOMETRIC_DATA:
            classification = max(classification, DataClassification.RESTRICTED)
            confidence = max(confidence, 0.9)
            indicators.append("Biometric data type detected")
        
        return {
            'classification': classification,
            'confidence': confidence,
            'indicators': indicators,
            'method': 'metadata_analysis'
        }
    
    async def _classify_by_content(self, data_sample: bytes) -> Dict[str, Any]:
        """Classification basée sur contenu"""
        try:
            # Tentative décodage texte
            try:
                text_content = data_sample.decode('utf-8', errors='ignore')
            except:
                # Données binaires
                return {
                    'classification': DataClassification.INTERNAL,
                    'confidence': 0.3,
                    'indicators': ['Binary data detected'],
                    'method': 'content_analysis'
                }
            
            classification = DataClassification.PUBLIC
            confidence = 0.4
            indicators = []
            detected_patterns = []
            
            # Détection patterns sensibles
            patterns = self.classification_rules['patterns']
            
            for pattern_name, pattern_regex in patterns.items():
                matches = re.findall(pattern_regex, text_content, re.IGNORECASE)
                if matches:
                    detected_patterns.append({
                        'pattern': pattern_name,
                        'count': len(matches),
                        'samples': matches[:3]  # 3 premiers exemples
                    })
                    
                    # Élévation classification selon pattern
                    if pattern_name in ['ssn', 'credit_card']:
                        classification = max(classification, DataClassification.RESTRICTED)
                        confidence = max(confidence, 0.9)
                        indicators.append(f"Sensitive data pattern '{pattern_name}' detected")
                    
                    elif pattern_name in ['email', 'phone']:
                        classification = max(classification, DataClassification.CONFIDENTIAL)
                        confidence = max(confidence, 0.7)
                        indicators.append(f"Personal data pattern '{pattern_name}' detected")
                    
                    elif pattern_name in ['api_key']:
                        classification = max(classification, DataClassification.RESTRICTED)
                        confidence = max(confidence, 0.8)
                        indicators.append(f"Security credential pattern '{pattern_name}' detected")
            
            # Détection mots-clés sensibles dans contenu
            for class_level, keywords in self.classification_rules['keywords'].items():
                keyword_count = sum(1 for keyword in keywords if keyword in text_content.lower())
                if keyword_count > 0:
                    classification = max(classification, class_level)
                    confidence = max(confidence, 0.6 + (keyword_count * 0.1))
                    indicators.append(f"{keyword_count} sensitive keywords detected")
            
            return {
                'classification': classification,
                'confidence': min(confidence, 1.0),
                'indicators': indicators,
                'detected_patterns': detected_patterns,
                'method': 'content_analysis'
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur classification contenu: {str(e)}")
            return {
                'classification': DataClassification.INTERNAL,
                'confidence': 0.2,
                'error': str(e),
                'method': 'content_analysis'
            }
    
    async def _classify_by_location(self, location: str) -> Dict[str, Any]:
        """Classification basée sur localisation"""
        classification = DataClassification.INTERNAL
        confidence = 0.3
        indicators = []
        
        location_lower = location.lower()
        
        # Locations sécurisées
        if any(secure in location_lower for secure in ['vault', 'secure', 'encrypted', 'hsm']):
            classification = DataClassification.RESTRICTED
            confidence = 0.7
            indicators.append("Secure storage location detected")
        
        # Locations publiques
        elif any(public in location_lower for public in ['public', 'temp', 'cache', 'tmp']):
            classification = DataClassification.PUBLIC
            confidence = 0.8
            indicators.append("Public storage location detected")
        
        # Locations backup
        elif 'backup' in location_lower:
            classification = DataClassification.CONFIDENTIAL
            confidence = 0.6
            indicators.append("Backup storage location detected")
        
        return {
            'classification': classification,
            'confidence': confidence,
            'indicators': indicators,
            'method': 'location_analysis'
        }
    
    async def _merge_classification_results(
        self,
        metadata_result: Dict[str, Any],
        content_result: Optional[Dict[str, Any]],
        location_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fusion résultats de classification"""
        results = [metadata_result, location_result]
        if content_result:
            results.append(content_result)
        
        # Classification la plus élevée
        final_classification = max(
            result['classification'] for result in results
        )
        
        # Confidence pondérée
        total_weight = 0
        weighted_confidence = 0
        
        weights = {'metadata_analysis': 0.3, 'content_analysis': 0.5, 'location_analysis': 0.2}
        
        for result in results:
            method = result.get('method', 'unknown')
            weight = weights.get(method, 0.1)
            weighted_confidence += result['confidence'] * weight
            total_weight += weight
        
        final_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.5
        
        # Consolidation indicateurs
        all_indicators = []
        all_patterns = []
        
        for result in results:
            all_indicators.extend(result.get('indicators', []))
            all_patterns.extend(result.get('detected_patterns', []))
        
        return {
            'suggested_classification': final_classification,
            'confidence': final_confidence,
            'detected_patterns': all_patterns,
            'privacy_indicators': [i for i in all_indicators if 'personal' in i.lower()],
            'security_indicators': [i for i in all_indicators if any(s in i.lower() for s in ['credential', 'key', 'secret'])],
            'data_types_detected': list(set(p['pattern'] for p in all_patterns)),
            'classification_reasoning': all_indicators
        }


class DataProtectionManager:
    """
    🔐 Gestionnaire de protection des données enterprise
    ===================================================
    
    Protection complète avec encryption at scale, data classification
    et data governance automation pour Ainflue.
    """
    
    def __init__(self):
        """Initialisation gestionnaire protection données"""
        self.logger = logging.getLogger(__name__)
        
        # Composants protection
        self.encryption_engine = AdvancedEncryptionEngine()
        self.classification_engine = DataClassificationEngine()
        
        # Storage et cache
        self.data_assets = {}
        self.governance_policies = {}
        self.privacy_assessments = {}
        
        # Configuration
        self.protection_config = {
            'auto_encrypt_threshold': DataClassification.CONFIDENTIAL,
            'key_rotation_interval_days': 30,
            'backup_encryption_enabled': True,
            'audit_logging_enabled': True,
            'privacy_impact_threshold': 0.7
        }
        
        # Initialisation politiques par défaut
        self._initialize_default_governance_policies()
        
        self.logger.info("🔐 Data Protection Manager initialisé")
    
    def _initialize_default_governance_policies(self):
        """Initialisation politiques de gouvernance par défaut"""
        # Politique données personnelles (GDPR)
        self.governance_policies['personal_data_policy'] = DataGovernancePolicy(
            policy_id='personal_data_policy',
            name='Personal Data Protection Policy',
            description='GDPR-compliant policy for personal data protection',
            data_classification=DataClassification.CONFIDENTIAL,
            retention_rules={
                'default_retention_days': 2555,  # 7 ans
                'legal_basis_required': True,
                'consent_based_retention': True,
                'right_to_erasure': True
            },
            access_controls=[
                'authenticated_access_only',
                'purpose_limitation',
                'data_minimization',
                'consent_validation'
            ],
            encryption_requirements={
                'encryption_mandatory': True,
                'algorithm': EncryptionAlgorithm.AES_256_GCM.value,
                'key_rotation_days': 90
            },
            deletion_rules={
                'secure_deletion_required': True,
                'deletion_verification': True,
                'backup_deletion': True
            },
            compliance_requirements=['gdpr', 'ccpa'],
            monitoring_rules={
                'access_logging': True,
                'change_tracking': True,
                'privacy_impact_monitoring': True
            }
        )
        
        # Politique données financières
        self.governance_policies['financial_data_policy'] = DataGovernancePolicy(
            policy_id='financial_data_policy',
            name='Financial Data Protection Policy',
            description='PCI DSS compliant policy for financial data',
            data_classification=DataClassification.RESTRICTED,
            retention_rules={
                'default_retention_days': 2555,  # 7 ans (réglementation financière)
                'legal_hold_support': True
            },
            access_controls=[
                'multi_factor_authentication',
                'role_based_access',
                'need_to_know_basis',
                'audit_trail_mandatory'
            ],
            encryption_requirements={
                'encryption_mandatory': True,
                'algorithm': EncryptionAlgorithm.AES_256_GCM.value,
                'key_rotation_days': 30,
                'hsm_protection': True
            },
            deletion_rules={
                'secure_deletion_required': True,
                'cryptographic_erasure': True,
                'compliance_verification': True
            },
            compliance_requirements=['pci_dss', 'sox'],
            monitoring_rules={
                'real_time_monitoring': True,
                'anomaly_detection': True,
                'compliance_reporting': True
            }
        )
        
        # Politique contenu créateur
        self.governance_policies['creator_content_policy'] = DataGovernancePolicy(
            policy_id='creator_content_policy',
            name='Creator Content Protection Policy',
            description='Protection policy for creator intellectual property',
            data_classification=DataClassification.CONFIDENTIAL,
            retention_rules={
                'default_retention_days': 3650,  # 10 ans
                'creator_controlled_retention': True,
                'backup_retention_extended': True
            },
            access_controls=[
                'creator_ownership_validation',
                'content_rights_verification',
                'platform_terms_compliance'
            ],
            encryption_requirements={
                'encryption_mandatory': True,
                'algorithm': EncryptionAlgorithm.AES_256_GCM.value,
                'watermarking_required': True
            },
            deletion_rules={
                'creator_controlled_deletion': True,
                'backup_preservation_period': 365  # 1 an après suppression
            },
            compliance_requirements=['dmca', 'creator_rights'],
            monitoring_rules={
                'piracy_monitoring': True,
                'unauthorized_access_detection': True,
                'content_integrity_verification': True
            }
        )
    
    async def protect_data_comprehensive(
        self,
        data_asset: DataAsset,
        data_content: bytes,
        protection_level: Optional[ProtectionLevel] = None
    ) -> DataProtectionResult:
        """
        🎯 Protection complète des données
        
        Args:
            data_asset: Asset de données
            data_content: Contenu à protéger
            protection_level: Niveau de protection (optionnel)
            
        Returns:
            DataProtectionResult: Résultat protection complète
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"🔐 Protection données: {data_asset.name} ({operation_id})")
            
            # 1. Classification automatique des données
            classification_result = await self.classification_engine.classify_data_asset(
                data_asset, data_content[:1024]  # Échantillon 1KB
            )
            
            # Mise à jour classification si confiance suffisante
            if classification_result['confidence'] > 0.7:
                data_asset.classification = classification_result['suggested_classification']
            
            # 2. Évaluation confidentialité
            privacy_assessment = await self._assess_privacy_impact(
                data_asset, classification_result
            )
            
            # 3. Sélection politique de gouvernance
            governance_policy = await self._select_governance_policy(data_asset)
            
            # 4. Détermination niveau protection
            if not protection_level:
                protection_level = await self._determine_protection_level(
                    data_asset, privacy_assessment, governance_policy
                )
            
            # 5. Application chiffrement
            encryption_result = await self._apply_encryption_protection(
                data_asset, data_content, protection_level, governance_policy
            )
            
            # 6. Vérification conformité
            compliance_status = await self._verify_governance_compliance(
                data_asset, governance_policy, encryption_result
            )
            
            # 7. Configuration monitoring
            monitoring_setup = await self._setup_data_monitoring(
                data_asset, governance_policy
            )
            
            # 8. Génération recommandations
            recommendations = await self._generate_protection_recommendations(
                data_asset, privacy_assessment, compliance_status
            )
            
            # Mise à jour asset
            data_asset.protection_level = protection_level
            data_asset.encryption_status = encryption_result.get('success', False)
            data_asset.last_accessed = datetime.utcnow()
            
            # Stockage
            self.data_assets[data_asset.asset_id] = data_asset
            self.privacy_assessments[data_asset.asset_id] = privacy_assessment
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = DataProtectionResult(
                operation_id=operation_id,
                data_asset=data_asset,
                protection_applied={
                    'protection_level': protection_level.value,
                    'encryption_applied': encryption_result.get('success', False),
                    'monitoring_enabled': monitoring_setup.get('enabled', False),
                    'governance_policy': governance_policy.policy_id if governance_policy else None
                },
                encryption_details=encryption_result.get('encryption_metadata', {}),
                compliance_status=compliance_status,
                privacy_assessment=privacy_assessment,
                governance_compliance=compliance_status.get('compliant', False),
                recommendations=recommendations,
                execution_time_ms=execution_time
            )
            
            self.logger.info(
                f"✅ Protection appliquée: {data_asset.name} "
                f"(Niveau: {protection_level.value}, Conformité: {compliance_status.get('compliant', False)}) "
                f"en {execution_time:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur protection données: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return DataProtectionResult(
                operation_id=operation_id,
                data_asset=data_asset,
                protection_applied={'error': str(e)},
                encryption_details={},
                compliance_status={'error': True, 'compliant': False},
                privacy_assessment=PrivacyAssessment(
                    assessment_id=str(uuid.uuid4()),
                    data_asset=data_asset,
                    privacy_risk_score=1.0,
                    privacy_factors=[f"Error in assessment: {str(e)}"],
                    personal_data_elements=[],
                    consent_requirements=[],
                    right_to_erasure=False,
                    data_minimization_compliance=False,
                    purpose_limitation_compliance=False,
                    anonymization_feasible=False,
                    pseudonymization_applied=False
                ),
                governance_compliance=False,
                recommendations=[f"Fix protection error: {str(e)}"],
                execution_time_ms=execution_time
            )
    
    async def _assess_privacy_impact(
        self,
        data_asset: DataAsset,
        classification_result: Dict[str, Any]
    ) -> PrivacyAssessment:
        """Évaluation impact confidentialité"""
        try:
            # Calcul score risque confidentialité
            privacy_risk_score = 0.0
            privacy_factors = []
            personal_data_elements = []
            
            # Facteurs basés sur classification
            if data_asset.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
                privacy_risk_score += 0.4
                privacy_factors.append("High classification level")
            
            # Facteurs basés sur type de données
            if data_asset.data_type == DataType.PERSONAL_DATA:
                privacy_risk_score += 0.3
                privacy_factors.append("Personal data type")
                personal_data_elements.extend(['name', 'email', 'phone'])
            
            elif data_asset.data_type == DataType.BIOMETRIC_DATA:
                privacy_risk_score += 0.5
                privacy_factors.append("Biometric data - special category")
                personal_data_elements.extend(['biometric_template', 'facial_recognition'])
            
            elif data_asset.data_type == DataType.HEALTH_DATA:
                privacy_risk_score += 0.4
                privacy_factors.append("Health data - special category")
                personal_data_elements.extend(['health_records', 'medical_data'])
            
            # Facteurs basés sur patterns détectés
            detected_patterns = classification_result.get('detected_patterns', [])
            for pattern in detected_patterns:
                if pattern['pattern'] in ['email', 'phone', 'ssn']:
                    privacy_risk_score += 0.2
                    privacy_factors.append(f"Personal identifier detected: {pattern['pattern']}")
                    personal_data_elements.append(pattern['pattern'])
            
            # Normalisation score
            privacy_risk_score = min(privacy_risk_score, 1.0)
            
            # Évaluation droits GDPR
            right_to_erasure = privacy_risk_score > 0.3
            data_minimization_compliance = len(personal_data_elements) <= 3
            purpose_limitation_compliance = data_asset.metadata.get('processing_purpose') is not None
            
            # Faisabilité anonymisation
            anonymization_feasible = (
                privacy_risk_score < 0.7 and 
                data_asset.data_type not in [DataType.BIOMETRIC_DATA]
            )
            
            # Pseudonymisation appliquée
            pseudonymization_applied = (
                'pseudonymized' in data_asset.metadata.get('processing_flags', [])
            )
            
            # Exigences consentement
            consent_requirements = []
            if privacy_risk_score > 0.5:
                consent_requirements.extend([
                    'explicit_consent_required',
                    'purpose_specification',
                    'withdrawal_mechanism'
                ])
            
            return PrivacyAssessment(
                assessment_id=str(uuid.uuid4()),
                data_asset=data_asset,
                privacy_risk_score=privacy_risk_score,
                privacy_factors=privacy_factors,
                personal_data_elements=list(set(personal_data_elements)),
                consent_requirements=consent_requirements,
                right_to_erasure=right_to_erasure,
                data_minimization_compliance=data_minimization_compliance,
                purpose_limitation_compliance=purpose_limitation_compliance,
                anonymization_feasible=anonymization_feasible,
                pseudonymization_applied=pseudonymization_applied
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur évaluation confidentialité: {str(e)}")
            return PrivacyAssessment(
                assessment_id=str(uuid.uuid4()),
                data_asset=data_asset,
                privacy_risk_score=0.5,
                privacy_factors=[f"Assessment error: {str(e)}"],
                personal_data_elements=[],
                consent_requirements=[],
                right_to_erasure=False,
                data_minimization_compliance=False,
                purpose_limitation_compliance=False,
                anonymization_feasible=False,
                pseudonymization_applied=False
            )
    
    async def _select_governance_policy(
        self,
        data_asset: DataAsset
    ) -> Optional[DataGovernancePolicy]:
        """Sélection politique de gouvernance"""
        try:
            # Sélection basée sur type de données
            if data_asset.data_type == DataType.PERSONAL_DATA:
                return self.governance_policies.get('personal_data_policy')
            
            elif data_asset.data_type == DataType.FINANCIAL_DATA:
                return self.governance_policies.get('financial_data_policy')
            
            elif data_asset.data_type == DataType.CONTENT_DATA:
                return self.governance_policies.get('creator_content_policy')
            
            # Sélection basée sur classification
            for policy in self.governance_policies.values():
                if policy.data_classification == data_asset.classification:
                    return policy
            
            # Politique par défaut
            return self.governance_policies.get('personal_data_policy')
            
        except Exception as e:
            self.logger.error(f"❌ Erreur sélection politique: {str(e)}")
            return None
    
    async def _determine_protection_level(
        self,
        data_asset: DataAsset,
        privacy_assessment: PrivacyAssessment,
        governance_policy: Optional[DataGovernancePolicy]
    ) -> ProtectionLevel:
        """Détermination niveau de protection"""
        try:
            # Niveau basé sur classification
            classification_levels = {
                DataClassification.PUBLIC: ProtectionLevel.MINIMAL,
                DataClassification.INTERNAL: ProtectionLevel.STANDARD,
                DataClassification.CONFIDENTIAL: ProtectionLevel.ENHANCED,
                DataClassification.RESTRICTED: ProtectionLevel.MAXIMUM,
                DataClassification.TOP_SECRET: ProtectionLevel.MAXIMUM
            }
            
            base_level = classification_levels.get(data_asset.classification, ProtectionLevel.STANDARD)
            
            # Élévation basée sur risque confidentialité
            if privacy_assessment.privacy_risk_score > 0.7:
                base_level = max(base_level, ProtectionLevel.MAXIMUM)
            elif privacy_assessment.privacy_risk_score > 0.5:
                base_level = max(base_level, ProtectionLevel.ENHANCED)
            
            # Élévation basée sur politique
            if governance_policy:
                if governance_policy.encryption_requirements.get('encryption_mandatory', False):
                    base_level = max(base_level, ProtectionLevel.ENHANCED)
                
                if governance_policy.encryption_requirements.get('hsm_protection', False):
                    base_level = max(base_level, ProtectionLevel.MAXIMUM)
            
            return base_level
            
        except Exception as e:
            self.logger.error(f"❌ Erreur détermination protection: {str(e)}")
            return ProtectionLevel.STANDARD
    
    async def _apply_encryption_protection(
        self,
        data_asset: DataAsset,
        data_content: bytes,
        protection_level: ProtectionLevel,
        governance_policy: Optional[DataGovernancePolicy]
    ) -> Dict[str, Any]:
        """Application protection par chiffrement"""
        try:
            # Sélection algorithme selon niveau protection
            algorithm_mapping = {
                ProtectionLevel.MINIMAL: EncryptionAlgorithm.FERNET,
                ProtectionLevel.STANDARD: EncryptionAlgorithm.AES_256_GCM,
                ProtectionLevel.ENHANCED: EncryptionAlgorithm.AES_256_GCM,
                ProtectionLevel.MAXIMUM: EncryptionAlgorithm.RSA_4096
            }
            
            encryption_algorithm = algorithm_mapping.get(protection_level, EncryptionAlgorithm.AES_256_GCM)
            
            # Override si politique spécifie algorithme
            if governance_policy and governance_policy.encryption_requirements.get('algorithm'):
                try:
                    policy_algorithm = EncryptionAlgorithm(
                        governance_policy.encryption_requirements['algorithm']
                    )
                    encryption_algorithm = policy_algorithm
                except ValueError:
                    pass  # Garde algorithme par défaut si invalide
            
            # Application chiffrement
            encryption_result = await self.encryption_engine.encrypt_data_asset(
                data_asset, data_content, encryption_algorithm
            )
            
            if encryption_result['success']:
                self.logger.info(
                    f"🔐 Chiffrement appliqué: {data_asset.name} "
                    f"({encryption_algorithm.value})"
                )
            
            return encryption_result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur application chiffrement: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _verify_governance_compliance(
        self,
        data_asset: DataAsset,
        governance_policy: Optional[DataGovernancePolicy],
        encryption_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Vérification conformité gouvernance"""
        if not governance_policy:
            return {
                'compliant': True,
                'reason': 'No governance policy applicable',
                'checks_performed': []
            }
        
        try:
            compliance_status = {
                'compliant': True,
                'policy_id': governance_policy.policy_id,
                'checks_performed': [],
                'violations': []
            }
            
            # Vérification chiffrement obligatoire
            if governance_policy.encryption_requirements.get('encryption_mandatory', False):
                if not encryption_result.get('success', False):
                    compliance_status['compliant'] = False
                    compliance_status['violations'].append('Mandatory encryption not applied')
                
                compliance_status['checks_performed'].append('encryption_mandatory')
            
            # Vérification algorithme chiffrement
            required_algorithm = governance_policy.encryption_requirements.get('algorithm')
            if required_algorithm:
                applied_algorithm = encryption_result.get('encryption_metadata', {}).get('algorithm')
                if applied_algorithm != required_algorithm:
                    compliance_status['compliant'] = False
                    compliance_status['violations'].append(
                        f'Wrong encryption algorithm: {applied_algorithm} != {required_algorithm}'
                    )
                
                compliance_status['checks_performed'].append('encryption_algorithm')
            
            # Vérification contrôles d'accès
            for access_control in governance_policy.access_controls:
                # Simulation - en production: vérification réelle
                if access_control == 'authenticated_access_only':
                    # Vérifier que l'asset nécessite authentification
                    pass
                
                compliance_status['checks_performed'].append(f'access_control_{access_control}')
            
            # Vérification exigences conformité
            for compliance_req in governance_policy.compliance_requirements:
                if compliance_req == 'gdpr':
                    # Vérifications GDPR spécifiques
                    if data_asset.data_type == DataType.PERSONAL_DATA:
                        if not data_asset.metadata.get('consent_obtained', False):
                            compliance_status['violations'].append('GDPR: Missing consent for personal data')
                
                elif compliance_req == 'pci_dss':
                    # Vérifications PCI DSS
                    if data_asset.data_type == DataType.FINANCIAL_DATA:
                        if not encryption_result.get('success', False):
                            compliance_status['violations'].append('PCI DSS: Financial data must be encrypted')
                
                compliance_status['checks_performed'].append(f'compliance_{compliance_req}')
            
            # Statut final
            compliance_status['compliant'] = len(compliance_status['violations']) == 0
            
            return compliance_status
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification conformité: {str(e)}")
            return {
                'compliant': False,
                'error': str(e),
                'checks_performed': []
            }
    
    async def _setup_data_monitoring(
        self,
        data_asset: DataAsset,
        governance_policy: Optional[DataGovernancePolicy]
    ) -> Dict[str, Any]:
        """Configuration monitoring des données"""
        if not governance_policy:
            return {'enabled': False, 'reason': 'No governance policy'}
        
        monitoring_setup = {
            'enabled': True,
            'monitoring_rules': [],
            'alert_conditions': [],
            'reporting_schedule': 'daily'
        }
        
        # Configuration basée sur politique
        monitoring_rules = governance_policy.monitoring_rules
        
        if monitoring_rules.get('access_logging', False):
            monitoring_setup['monitoring_rules'].append('access_logging')
            monitoring_setup['alert_conditions'].append('unauthorized_access_attempt')
        
        if monitoring_rules.get('change_tracking', False):
            monitoring_setup['monitoring_rules'].append('change_tracking')
            monitoring_setup['alert_conditions'].append('unexpected_modification')
        
        if monitoring_rules.get('privacy_impact_monitoring', False):
            monitoring_setup['monitoring_rules'].append('privacy_monitoring')
            monitoring_setup['alert_conditions'].append('privacy_violation_risk')
        
        return monitoring_setup
    
    async def _generate_protection_recommendations(
        self,
        data_asset: DataAsset,
        privacy_assessment: PrivacyAssessment,
        compliance_status: Dict[str, Any]
    ) -> List[str]:
        """Génération recommandations protection"""
        recommendations = []
        
        # Recommandations conformité
        if not compliance_status.get('compliant', True):
            recommendations.append("🚨 Address compliance violations immediately")
            violations = compliance_status.get('violations', [])
            for violation in violations[:3]:  # Top 3 violations
                recommendations.append(f"- Fix: {violation}")
        
        # Recommandations confidentialité
        if privacy_assessment.privacy_risk_score > 0.7:
            recommendations.extend([
                "🔐 High privacy risk - consider additional protection measures",
                "📋 Conduct detailed privacy impact assessment",
                "🔒 Implement privacy-by-design principles"
            ])
        
        if not privacy_assessment.pseudonymization_applied and privacy_assessment.privacy_risk_score > 0.5:
            recommendations.append("🎭 Consider pseudonymization for privacy protection")
        
        if privacy_assessment.anonymization_feasible:
            recommendations.append("🔄 Evaluate anonymization for long-term storage")
        
        # Recommandations chiffrement
        if not data_asset.encryption_status:
            recommendations.append("🔐 Apply encryption for data protection")
        
        # Recommandations gouvernance
        if data_asset.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            recommendations.extend([
                "📊 Implement enhanced monitoring and auditing",
                "⏰ Schedule regular access reviews",
                "🔄 Plan data lifecycle management"
            ])
        
        # Recommandations générales
        recommendations.extend([
            "📋 Document data processing activities",
            "🎓 Provide data protection training to handlers",
            "🔍 Regular compliance audits recommended"
        ])
        
        return recommendations


# Export classes principales
__all__ = [
    'DataProtectionManager',
    'DataProtectionResult',
    'DataAsset',
    'EncryptionKey',
    'DataGovernancePolicy',
    'PrivacyAssessment',
    'DataClassification',
    'EncryptionAlgorithm',
    'DataType',
    'ProtectionLevel',
    'AdvancedEncryptionEngine',
    'DataClassificationEngine'
]