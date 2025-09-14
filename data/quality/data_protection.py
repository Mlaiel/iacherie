"""
🛡️ DATA PROTECTION - PRIVACY & ENCRYPTION MANAGEMENT
Data Quality Module - Phase 3 Implementation

🚨 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - TOUS DROITS RÉSERVÉS
Toute utilisation non autorisée sera poursuivie en justice.

Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import hashlib
import hmac
import secrets
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path

# Cryptographie avancée
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Anonymisation
import faker


class DataClassification(str, Enum):
    """Classification des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class PrivacyLevel(str, Enum):
    """Niveaux de confidentialité"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class EncryptionMethod(str, Enum):
    """Méthodes de chiffrement"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"
    HYBRID = "hybrid"


class PIIType(str, Enum):
    """Types d'informations personnelles"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"
    IP_ADDRESS = "ip_address"
    USER_ID = "user_id"
    BIOMETRIC = "biometric"
    FINANCIAL = "financial"


@dataclass
class EncryptionKey:
    """Clé de chiffrement"""
    key_id: str
    algorithm: EncryptionMethod
    key_data: bytes
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PIIField:
    """Champ contenant des données personnelles"""
    field_name: str
    pii_type: PIIType
    classification: DataClassification
    original_value: str
    encrypted_value: Optional[str] = None
    anonymized_value: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    retention_period: Optional[timedelta] = None


@dataclass
class DataProtectionResult:
    """Résultat de protection de données"""
    protected_fields: List[PIIField]
    encryption_applied: bool
    anonymization_applied: bool
    classification_level: DataClassification
    protection_score: float
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PIIDetector:
    """Détecteur d'informations personnelles"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        
        # Patterns de détection PII
        self.patterns = {
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.PHONE: r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
        # Noms communs (pour détection de noms)
        self.common_names = {
            'first_names': ['john', 'jane', 'michael', 'sarah', 'david', 'emma'],
            'last_names': ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia']
        }
    
    def detect_pii_in_text(self, text: str) -> List[PIIField]:
        """Détection PII dans un texte"""
        detected_fields = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                field = PIIField(
                    field_name=f"{pii_type.value}_detected",
                    pii_type=pii_type,
                    classification=self._classify_pii_type(pii_type),
                    original_value=match.group(),
                    retention_period=self._get_retention_period(pii_type)
                )
                detected_fields.append(field)
        
        # Détection de noms (heuristique)
        words = text.split()
        for word in words:
            if self._is_likely_name(word):
                field = PIIField(
                    field_name="name_detected",
                    pii_type=PIIType.NAME,
                    classification=DataClassification.CONFIDENTIAL,
                    original_value=word,
                    retention_period=timedelta(days=2555)  # 7 ans
                )
                detected_fields.append(field)
        
        return detected_fields
    
    def detect_pii_in_data(self, data: Dict[str, Any]) -> List[PIIField]:
        """Détection PII dans structure de données"""
        detected_fields = []
        
        for field_name, value in data.items():
            if not isinstance(value, str):
                continue
            
            # Détection par nom de champ
            field_pii_type = self._classify_field_name(field_name)
            if field_pii_type:
                field = PIIField(
                    field_name=field_name,
                    pii_type=field_pii_type,
                    classification=self._classify_pii_type(field_pii_type),
                    original_value=value,
                    retention_period=self._get_retention_period(field_pii_type)
                )
                detected_fields.append(field)
            
            # Détection par contenu
            content_fields = self.detect_pii_in_text(value)
            for content_field in content_fields:
                content_field.field_name = field_name
                detected_fields.append(content_field)
        
        return detected_fields
    
    def _classify_field_name(self, field_name: str) -> Optional[PIIType]:
        """Classification par nom de champ"""
        field_lower = field_name.lower()
        
        if any(keyword in field_lower for keyword in ['email', 'mail']):
            return PIIType.EMAIL
        elif any(keyword in field_lower for keyword in ['phone', 'tel', 'mobile']):
            return PIIType.PHONE
        elif any(keyword in field_lower for keyword in ['name', 'firstname', 'lastname']):
            return PIIType.NAME
        elif any(keyword in field_lower for keyword in ['address', 'street', 'city']):
            return PIIType.ADDRESS
        elif any(keyword in field_lower for keyword in ['user_id', 'userid', 'id']):
            return PIIType.USER_ID
        elif any(keyword in field_lower for keyword in ['ip', 'ip_address']):
            return PIIType.IP_ADDRESS
        
        return None
    
    def _classify_pii_type(self, pii_type: PIIType) -> DataClassification:
        """Classification par type PII"""
        classifications = {
            PIIType.EMAIL: DataClassification.CONFIDENTIAL,
            PIIType.PHONE: DataClassification.CONFIDENTIAL,
            PIIType.SSN: DataClassification.RESTRICTED,
            PIIType.CREDIT_CARD: DataClassification.RESTRICTED,
            PIIType.NAME: DataClassification.CONFIDENTIAL,
            PIIType.ADDRESS: DataClassification.CONFIDENTIAL,
            PIIType.IP_ADDRESS: DataClassification.INTERNAL,
            PIIType.USER_ID: DataClassification.INTERNAL,
            PIIType.BIOMETRIC: DataClassification.TOP_SECRET,
            PIIType.FINANCIAL: DataClassification.RESTRICTED
        }
        return classifications.get(pii_type, DataClassification.INTERNAL)
    
    def _get_retention_period(self, pii_type: PIIType) -> timedelta:
        """Période de rétention par type PII"""
        periods = {
            PIIType.EMAIL: timedelta(days=2555),      # 7 ans
            PIIType.PHONE: timedelta(days=2555),      # 7 ans
            PIIType.SSN: timedelta(days=3650),        # 10 ans
            PIIType.CREDIT_CARD: timedelta(days=1095), # 3 ans
            PIIType.NAME: timedelta(days=2555),       # 7 ans
            PIIType.ADDRESS: timedelta(days=2555),    # 7 ans
            PIIType.IP_ADDRESS: timedelta(days=90),   # 3 mois
            PIIType.USER_ID: timedelta(days=365),     # 1 an
            PIIType.BIOMETRIC: timedelta(days=3650),  # 10 ans
            PIIType.FINANCIAL: timedelta(days=2555)   # 7 ans
        }
        return periods.get(pii_type, timedelta(days=365))
    
    def _is_likely_name(self, word: str) -> bool:
        """Détection heuristique de nom"""
        word_lower = word.lower()
        
        # Vérification dans listes de noms communs
        if word_lower in self.common_names['first_names'] or word_lower in self.common_names['last_names']:
            return True
        
        # Heuristiques: majuscule initiale, longueur, caractères
        if len(word) >= 2 and word[0].isupper() and word[1:].islower() and word.isalpha():
            return True
        
        return False


class AdvancedEncryption:
    """Système de chiffrement avancé"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.keys: Dict[str, EncryptionKey] = {}
        self.default_method = EncryptionMethod.AES_256_GCM
    
    def generate_key(self, method: EncryptionMethod = None, 
                    key_id: Optional[str] = None) -> EncryptionKey:
        """Génération de clé de chiffrement"""
        if method is None:
            method = self.default_method
        
        if key_id is None:
            key_id = f"key_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(4)}"
        
        if method == EncryptionMethod.AES_256_GCM:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif method == EncryptionMethod.FERNET:
            key_data = Fernet.generate_key()
        elif method == EncryptionMethod.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported encryption method: {method}")
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=method,
            key_data=key_data,
            expires_at=datetime.utcnow() + timedelta(days=365),  # 1 an par défaut
            max_usage=10000  # Limite usage
        )
        
        self.keys[key_id] = encryption_key
        return encryption_key
    
    def encrypt_data(self, data: str, key_id: Optional[str] = None) -> Tuple[str, str]:
        """Chiffrement de données"""
        if key_id is None:
            # Utiliser ou créer clé par défaut
            default_keys = [k for k in self.keys.values() if k.algorithm == self.default_method]
            if default_keys:
                encryption_key = default_keys[0]
            else:
                encryption_key = self.generate_key()
        else:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
            encryption_key = self.keys[key_id]
        
        # Vérification validité clé
        if encryption_key.expires_at and encryption_key.expires_at < datetime.utcnow():
            raise ValueError(f"Key expired: {key_id}")
        
        if encryption_key.max_usage and encryption_key.usage_count >= encryption_key.max_usage:
            raise ValueError(f"Key usage limit exceeded: {key_id}")
        
        # Chiffrement selon méthode
        if encryption_key.algorithm == EncryptionMethod.AES_256_GCM:
            encrypted_data = self._encrypt_aes_gcm(data, encryption_key.key_data)
        elif encryption_key.algorithm == EncryptionMethod.FERNET:
            encrypted_data = self._encrypt_fernet(data, encryption_key.key_data)
        elif encryption_key.algorithm == EncryptionMethod.RSA_4096:
            encrypted_data = self._encrypt_rsa(data, encryption_key.key_data)
        else:
            raise ValueError(f"Encryption method not implemented: {encryption_key.algorithm}")
        
        # Mise à jour compteur usage
        encryption_key.usage_count += 1
        
        return encrypted_data, encryption_key.key_id
    
    def decrypt_data(self, encrypted_data: str, key_id: str) -> str:
        """Déchiffrement de données"""
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
        
        encryption_key = self.keys[key_id]
        
        # Déchiffrement selon méthode
        if encryption_key.algorithm == EncryptionMethod.AES_256_GCM:
            return self._decrypt_aes_gcm(encrypted_data, encryption_key.key_data)
        elif encryption_key.algorithm == EncryptionMethod.FERNET:
            return self._decrypt_fernet(encrypted_data, encryption_key.key_data)
        elif encryption_key.algorithm == EncryptionMethod.RSA_4096:
            return self._decrypt_rsa(encrypted_data, encryption_key.key_data)
        else:
            raise ValueError(f"Decryption method not implemented: {encryption_key.algorithm}")
    
    def _encrypt_aes_gcm(self, data: str, key: bytes) -> str:
        """Chiffrement AES-256-GCM"""
        # Génération IV aléatoire
        iv = secrets.token_bytes(12)  # 96 bits pour GCM
        
        # Chiffrement
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        data_bytes = data.encode('utf-8')
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
        
        # Combinaison IV + tag + ciphertext
        encrypted = iv + encryptor.tag + ciphertext
        return base64.b64encode(encrypted).decode('ascii')
    
    def _decrypt_aes_gcm(self, encrypted_data: str, key: bytes) -> str:
        """Déchiffrement AES-256-GCM"""
        # Décodage base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        
        # Extraction IV, tag, ciphertext
        iv = encrypted_bytes[:12]
        tag = encrypted_bytes[12:28]
        ciphertext = encrypted_bytes[28:]
        
        # Déchiffrement
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')
    
    def _encrypt_fernet(self, data: str, key: bytes) -> str:
        """Chiffrement Fernet"""
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('ascii')
    
    def _decrypt_fernet(self, encrypted_data: str, key: bytes) -> str:
        """Déchiffrement Fernet"""
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def _encrypt_rsa(self, data: str, key_data: bytes) -> str:
        """Chiffrement RSA (pour petites données)"""
        private_key = serialization.load_pem_private_key(
            key_data, password=None, backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # RSA limité en taille - pour données > 446 bytes, utiliser hybride
        data_bytes = data.encode('utf-8')
        if len(data_bytes) > 446:  # Limite pratique RSA-4096
            raise ValueError("Data too large for RSA encryption. Use hybrid method.")
        
        encrypted = public_key.encrypt(
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode('ascii')
    
    def _decrypt_rsa(self, encrypted_data: str, key_data: bytes) -> str:
        """Déchiffrement RSA"""
        private_key = serialization.load_pem_private_key(
            key_data, password=None, backend=default_backend()
        )
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')
    
    def rotate_key(self, old_key_id: str) -> EncryptionKey:
        """Rotation de clé"""
        if old_key_id not in self.keys:
            raise ValueError(f"Key not found: {old_key_id}")
        
        old_key = self.keys[old_key_id]
        new_key = self.generate_key(old_key.algorithm)
        
        # Marquer ancienne clé comme expirée
        old_key.expires_at = datetime.utcnow()
        
        self.logger.info(f"Key rotated: {old_key_id} -> {new_key.key_id}")
        return new_key
    
    def cleanup_expired_keys(self) -> None:
        """Nettoyage des clés expirées"""
        now = datetime.utcnow()
        expired_keys = [
            key_id for key_id, key in self.keys.items()
            if key.expires_at and key.expires_at < now
        ]
        
        for key_id in expired_keys:
            del self.keys[key_id]
            self.logger.info(f"Expired key removed: {key_id}")
        
        return len(expired_keys)


class DataAnonymizer:
    """Anonymiseur de données"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.faker = faker.Faker()
        
        # Tables de correspondance pour préserver cohérence
        self.mapping_tables: Dict[str, Dict[str, str]] = {}
    
    def anonymize_pii_field(self, field: PIIField, preserve_format: bool = True) -> str:
        """Anonymisation d'un champ PII"""
        if field.pii_type == PIIType.EMAIL:
            return self._anonymize_email(field.original_value, preserve_format)
        elif field.pii_type == PIIType.PHONE:
            return self._anonymize_phone(field.original_value, preserve_format)
        elif field.pii_type == PIIType.NAME:
            return self._anonymize_name(field.original_value)
        elif field.pii_type == PIIType.ADDRESS:
            return self._anonymize_address(field.original_value)
        elif field.pii_type == PIIType.SSN:
            return self._anonymize_ssn(field.original_value, preserve_format)
        elif field.pii_type == PIIType.CREDIT_CARD:
            return self._anonymize_credit_card(field.original_value, preserve_format)
        elif field.pii_type == PIIType.IP_ADDRESS:
            return self._anonymize_ip(field.original_value, preserve_format)
        elif field.pii_type == PIIType.USER_ID:
            return self._anonymize_user_id(field.original_value)
        else:
            # Anonymisation générique
            return self._generic_anonymization(field.original_value)
    
    def _anonymize_email(self, email: str, preserve_format: bool) -> str:
        """Anonymisation email"""
        if not preserve_format:
            return self.faker.email()
        
        # Préserver domaine si interne
        if '@' in email:
            local, domain = email.split('@', 1)
            if domain in ['company.com', 'internal.com']:  # Domaines internes
                fake_local = self.faker.user_name()
                return f"{fake_local}@{domain}"
        
        return self.faker.email()
    
    def _anonymize_phone(self, phone: str, preserve_format: bool) -> str:
        """Anonymisation téléphone"""
        if not preserve_format:
            return self.faker.phone_number()
        
        # Préserver format mais changer chiffres
        anonymized = re.sub(r'\d', lambda x: str(self.faker.random_digit()), phone)
        return anonymized
    
    def _anonymize_name(self, name: str) -> str:
        """Anonymisation nom"""
        # Utiliser table de correspondance pour cohérence
        if name not in self.mapping_tables.get('names', {}):
            if 'names' not in self.mapping_tables:
                self.mapping_tables['names'] = {}
            self.mapping_tables['names'][name] = self.faker.name()
        
        return self.mapping_tables['names'][name]
    
    def _anonymize_address(self, address: str) -> str:
        """Anonymisation adresse"""
        return self.faker.address()
    
    def _anonymize_ssn(self, ssn: str, preserve_format: bool) -> str:
        """Anonymisation SSN"""
        if preserve_format:
            # Préserver format XXX-XX-XXXX
            return f"{self.faker.random_int(100, 999)}-{self.faker.random_int(10, 99)}-{self.faker.random_int(1000, 9999)}"
        return str(self.faker.random_int(100000000, 999999999))
    
    def _anonymize_credit_card(self, cc: str, preserve_format: bool) -> str:
        """Anonymisation carte crédit"""
        if preserve_format:
            # Garder format mais changer chiffres (sauf 4 premiers)
            digits_only = re.sub(r'\D', '', cc)
            if len(digits_only) >= 4:
                prefix = digits_only[:4]
                fake_suffix = ''.join([str(self.faker.random_digit()) for _ in range(len(digits_only) - 4)])
                fake_number = prefix + fake_suffix
                
                # Restaurer format original
                result = cc
                digit_index = 0
                for i, char in enumerate(cc):
                    if char.isdigit():
                        result = result[:i] + fake_number[digit_index] + result[i+1:]
                        digit_index += 1
                return result
        
        return self.faker.credit_card_number()
    
    def _anonymize_ip(self, ip: str, preserve_format: bool) -> str:
        """Anonymisation IP"""
        if preserve_format:
            # Préserver classe réseau mais changer hôte
            parts = ip.split('.')
            if len(parts) == 4:
                # Garder premier octet, anonymiser les autres
                return f"{parts[0]}.{self.faker.random_int(0, 255)}.{self.faker.random_int(0, 255)}.{self.faker.random_int(1, 254)}"
        
        return self.faker.ipv4()
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """Anonymisation user ID"""
        # Utiliser table de correspondance
        if user_id not in self.mapping_tables.get('user_ids', {}):
            if 'user_ids' not in self.mapping_tables:
                self.mapping_tables['user_ids'] = {}
            self.mapping_tables['user_ids'][user_id] = f"user_{secrets.token_hex(8)}"
        
        return self.mapping_tables['user_ids'][user_id]
    
    def _generic_anonymization(self, value: str) -> str:
        """Anonymisation générique"""
        # Hash avec sel pour anonymisation déterministe
        salt = b"ainflue_anonymization_salt_2025"
        hash_value = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, 100000)
        return base64.b64encode(hash_value).decode('ascii')[:16]


class AdvancedDataProtection:
    """Système de protection de données avancé"""
    
    def __init__(self, privacy_level -> None: PrivacyLevel = PrivacyLevel.HIGH) -> None:
        self.privacy_level = privacy_level
        self.pii_detector = PIIDetector()
        self.encryption = AdvancedEncryption()
        self.anonymizer = DataAnonymizer()
        
        # Configuration selon niveau de confidentialité
        self.auto_encrypt_threshold = self._get_encryption_threshold()
        self.anonymization_required = privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]
        
        # Audit trail
        self.protection_log: List[DataProtectionResult] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _get_encryption_threshold(self) -> DataClassification:
        """Seuil de chiffrement automatique selon niveau confidentialité"""
        thresholds = {
            PrivacyLevel.NONE: DataClassification.TOP_SECRET,
            PrivacyLevel.BASIC: DataClassification.RESTRICTED,
            PrivacyLevel.STANDARD: DataClassification.CONFIDENTIAL,
            PrivacyLevel.HIGH: DataClassification.INTERNAL,
            PrivacyLevel.MAXIMUM: DataClassification.PUBLIC
        }
        return thresholds.get(self.privacy_level, DataClassification.CONFIDENTIAL)
    
    async def protect_data(self, data: Dict[str, Any], 
                          force_encryption: bool = False,
                          force_anonymization: bool = False) -> DataProtectionResult:
        """Protection complète des données"""
        try:
            # Détection PII
            detected_pii = self.pii_detector.detect_pii_in_data(data)
            
            protected_fields = []
            encryption_applied = False
            anonymization_applied = False
            
            # Classification niveau global
            max_classification = DataClassification.PUBLIC
            for pii_field in detected_pii:
                if self._classification_level(pii_field.classification) > self._classification_level(max_classification):
                    max_classification = pii_field.classification
            
            # Protection par champ
            for pii_field in detected_pii:
                # Décision chiffrement
                should_encrypt = (
                    force_encryption or 
                    self._classification_level(pii_field.classification) >= self._classification_level(self.auto_encrypt_threshold)
                )
                
                if should_encrypt:
                    try:
                        encrypted_value, key_id = self.encryption.encrypt_data(pii_field.original_value)
                        pii_field.encrypted_value = encrypted_value
                        pii_field.metadata = {"encryption_key_id": key_id}
                        encryption_applied = True
                    except Exception as e:
                        self.logger.error(f"Encryption failed for {pii_field.field_name}: {e}")
                
                # Décision anonymisation
                should_anonymize = (
                    force_anonymization or 
                    self.anonymization_required or
                    pii_field.classification in [DataClassification.RESTRICTED, DataClassification.TOP_SECRET]
                )
                
                if should_anonymize:
                    try:
                        anonymized_value = self.anonymizer.anonymize_pii_field(pii_field)
                        pii_field.anonymized_value = anonymized_value
                        anonymization_applied = True
                    except Exception as e:
                        self.logger.error(f"Anonymization failed for {pii_field.field_name}: {e}")
                
                protected_fields.append(pii_field)
            
            # Score de protection
            protection_score = self._calculate_protection_score(
                protected_fields, encryption_applied, anonymization_applied
            )
            
            # Recommandations
            recommendations = self._generate_recommendations(
                protected_fields, max_classification, protection_score
            )
            
            result = DataProtectionResult(
                protected_fields=protected_fields,
                encryption_applied=encryption_applied,
                anonymization_applied=anonymization_applied,
                classification_level=max_classification,
                protection_score=protection_score,
                recommendations=recommendations,
                metadata={
                    "privacy_level": self.privacy_level.value,
                    "total_fields_analyzed": len(data),
                    "pii_fields_detected": len(protected_fields),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Ajout à l'audit trail
            self.protection_log.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in data protection: {e}")
            raise
    
    def _classification_level(self, classification: DataClassification) -> int:
        """Niveau numérique de classification"""
        levels = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 1,
            DataClassification.CONFIDENTIAL: 2,
            DataClassification.RESTRICTED: 3,
            DataClassification.TOP_SECRET: 4
        }
        return levels.get(classification, 0)
    
    def _calculate_protection_score(self, protected_fields: List[PIIField],
                                  encryption_applied: bool,
                                  anonymization_applied: bool) -> float:
        """Calcul score de protection"""
        if not protected_fields:
            return 1.0  # Aucune donnée sensible détectée
        
        score = 0.0
        total_weight = 0.0
        
        for field in protected_fields:
            # Poids selon classification
            weight = self._classification_level(field.classification) + 1
            total_weight += weight
            
            field_score = 0.0
            
            # Points pour chiffrement
            if field.encrypted_value:
                field_score += 0.6
            
            # Points pour anonymisation
            if field.anonymized_value:
                field_score += 0.4
            
            # Bonus si les deux appliqués
            if field.encrypted_value and field.anonymized_value:
                field_score += 0.2
            
            score += field_score * weight
        
        return min(1.0, score / total_weight) if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, protected_fields: List[PIIField],
                                max_classification: DataClassification,
                                protection_score: float) -> List[str]:
        """Génération de recommandations"""
        recommendations = []
        
        if protection_score < 0.5:
            recommendations.append("🚨 Protection insuffisante - Activer chiffrement et anonymisation")
        elif protection_score < 0.8:
            recommendations.append("⚠️ Protection modérée - Considérer renforcement sécurité")
        else:
            recommendations.append("✅ Protection appropriée maintenue")
        
        # Recommandations par classification
        if max_classification in [DataClassification.RESTRICTED, DataClassification.TOP_SECRET]:
            recommendations.append("🔒 Données hautement sensibles - Audit de sécurité recommandé")
            recommendations.append("📋 Documenter accès et modifications")
        
        # Recommandations par champs non protégés
        unencrypted_sensitive = [
            f for f in protected_fields 
            if not f.encrypted_value and f.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]
        ]
        
        if unencrypted_sensitive:
            recommendations.append(f"🔐 Chiffrer {len(unencrypted_sensitive)} champs sensibles non protégés")
        
        # Recommandations rétention
        expired_fields = [
            f for f in protected_fields 
            if f.retention_period and datetime.utcnow() - f.detected_at > f.retention_period
        ]
        
        if expired_fields:
            recommendations.append(f"🗑️ Supprimer {len(expired_fields)} champs expirés selon politique rétention")
        
        return recommendations
    
    def create_protected_dataset(self, original_data: Dict[str, Any],
                                protection_result: DataProtectionResult,
                                mode: str = "encrypted") -> Dict[str, Any]:
        """Création dataset protégé"""
        protected_data = original_data.copy()
        
        for field in protection_result.protected_fields:
            field_name = field.field_name
            
            if mode == "encrypted" and field.encrypted_value:
                protected_data[field_name] = field.encrypted_value
            elif mode == "anonymized" and field.anonymized_value:
                protected_data[field_name] = field.anonymized_value
            elif mode == "masked":
                # Masquage simple
                value = field.original_value
                if len(value) > 4:
                    protected_data[field_name] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    protected_data[field_name] = "*" * len(value)
            elif mode == "removed":
                # Suppression complète
                if field_name in protected_data:
                    del protected_data[field_name]
        
        return protected_data
    
    def get_data_inventory(self) -> Dict[str, Any]:
        """Inventaire des données protégées"""
        if not self.protection_log:
            return {"message": "Aucune protection de données enregistrée"}
        
        # Statistiques globales
        total_protections = len(self.protection_log)
        total_fields_protected = sum(len(result.protected_fields) for result in self.protection_log)
        
        # Analyse par type PII
        pii_stats = {}
        classification_stats = {}
        
        for result in self.protection_log:
            for field in result.protected_fields:
                pii_type = field.pii_type.value
                classification = field.classification.value
                
                pii_stats[pii_type] = pii_stats.get(pii_type, 0) + 1
                classification_stats[classification] = classification_stats.get(classification, 0) + 1
        
        # Score moyen de protection
        avg_protection_score = sum(result.protection_score for result in self.protection_log) / total_protections
        
        return {
            "summary": {
                "total_protection_operations": total_protections,
                "total_fields_protected": total_fields_protected,
                "average_protection_score": round(avg_protection_score, 3),
                "privacy_level": self.privacy_level.value
            },
            "pii_type_distribution": pii_stats,
            "classification_distribution": classification_stats,
            "encryption": {
                "operations_with_encryption": len([r for r in self.protection_log if r.encryption_applied]),
                "total_keys_generated": len(self.encryption.keys)
            },
            "anonymization": {
                "operations_with_anonymization": len([r for r in self.protection_log if r.anonymization_applied]),
                "mapping_tables": len(self.anonymizer.mapping_tables)
            },
            "recommendations": [
                "Réviser politiques de protection régulièrement",
                "Effectuer audits de conformité trimestriels",
                "Former équipe sur gestion données sensibles",
                "Mettre à jour classification selon évolution métier"
            ]
        }
    
    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """Nettoyage données expirées"""
        cleanup_stats = {
            "expired_fields_found": 0,
            "expired_keys_removed": 0,
            "cleanup_timestamp": datetime.utcnow().isoformat()
        }
        
        # Nettoyage clés de chiffrement expirées
        expired_keys = self.encryption.cleanup_expired_keys()
        cleanup_stats["expired_keys_removed"] = expired_keys
        
        # Identification champs expirés (pour information)
        for result in self.protection_log:
            for field in result.protected_fields:
                if field.retention_period:
                    expiry_date = field.detected_at + field.retention_period
                    if datetime.utcnow() > expiry_date:
                        cleanup_stats["expired_fields_found"] += 1
        
        return cleanup_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé système protection"""
        return {
            "status": "healthy",
            "privacy_level": self.privacy_level.value,
            "encryption": {
                "available_keys": len(self.encryption.keys),
                "default_method": self.encryption.default_method.value
            },
            "protection_operations": len(self.protection_log),
            "anonymization_mappings": len(self.anonymizer.mapping_tables),
            "last_protection": max(
                [result.metadata.get("processing_timestamp") for result in self.protection_log], 
                default="Never"
            ),
            "recommendations": [
                "Surveillance continue activée",
                "Politiques de protection appliquées",
                "Conformité réglementaire maintenue"
            ]
        }


# Service singleton
data_protection = AdvancedDataProtection()


async def get_data_protection() -> AdvancedDataProtection:
    """Factory function pour protection de données"""
    return data_protection


# Export des classes principales
__all__ = [
    'AdvancedDataProtection',
    'PIIDetector',
    'AdvancedEncryption',
    'DataAnonymizer',
    'DataClassification',
    'PrivacyLevel',
    'EncryptionMethod',
    'PIIType',
    'EncryptionKey',
    'PIIField',
    'DataProtectionResult',
    'data_protection',
    'get_data_protection'
]


# Exemple d'utilisation
if __name__ == "__main__":
    async def main() -> None:
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialisation protection
        protection = AdvancedDataProtection(PrivacyLevel.HIGH)
        
        # Données de test contenant PII
        test_data = {
            "username": "john_doe",
            "email": "john.doe@company.com",
            "phone": "+1-555-123-4567",
            "ssn": "123-45-6789",
            "credit_card": "4532-1234-5678-9012",
            "address": "123 Main St, Anytown, USA",
            "user_id": "user_12345",
            "ip_address": "192.168.1.100",
            "description": "John Doe is a software engineer at john.doe@company.com"
        }
        
        try:
            print("=== PROTECTION DE DONNÉES ===")
            
            # Protection des données
            result = await protection.protect_data(test_data)
            
            print(f"Classification: {result.classification_level.value}")
            print(f"Score protection: {result.protection_score:.2f}")
            print(f"Chiffrement appliqué: {result.encryption_applied}")
            print(f"Anonymisation appliquée: {result.anonymization_applied}")
            print(f"Champs PII détectés: {len(result.protected_fields)}")
            
            print("\n=== CHAMPS PROTÉGÉS ===")
            for field in result.protected_fields:
                print(f"  {field.field_name} ({field.pii_type.value}):")
                print(f"    Original: {field.original_value}")
                if field.encrypted_value:
                    print(f"    Chiffré: {field.encrypted_value[:50]}...")
                if field.anonymized_value:
                    print(f"    Anonymisé: {field.anonymized_value}")
            
            print("\n=== RECOMMANDATIONS ===")
            for rec in result.recommendations:
                print(f"  - {rec}")
            
            # Création dataset protégé
            encrypted_dataset = protection.create_protected_dataset(test_data, result, "encrypted")
            anonymized_dataset = protection.create_protected_dataset(test_data, result, "anonymized")
            
            print(f"\n=== DATASETS PROTÉGÉS ===")
            print(f"Dataset chiffré: {len(encrypted_dataset)} champs")
            print(f"Dataset anonymisé: {len(anonymized_dataset)} champs")
            
            # Inventaire des données
            inventory = protection.get_data_inventory()
            print(f"\n=== INVENTAIRE ===")
            print(f"Operations protection: {inventory['summary']['total_protection_operations']}")
            print(f"Score moyen: {inventory['summary']['average_protection_score']}")
            
            # Nettoyage
            cleanup = await protection.cleanup_expired_data()
            print(f"\n=== NETTOYAGE ===")
            print(f"Clés expirées supprimées: {cleanup['expired_keys_removed']}")
            
            # Santé système
            health = await protection.health_check()
            print(f"\nStatut système: {health['status']}")
            
        except Exception as e:
            print(f"Error in data protection test: {e}")
    
    # Exécution test
    asyncio.run(main())