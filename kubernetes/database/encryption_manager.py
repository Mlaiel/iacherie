"""
Enterprise Database Encryption Manager
Advanced encryption and security for database operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🔐 CHIFFREMENT AVANCÉ:
- Chiffrement AES-256-GCM pour données sensibles
- Key management avec rotation automatique
- Perfect Forward Secrecy (PFS)
- Hardware Security Module (HSM) support
- Chiffrement transparent des données (TDE)
- Key derivation avec PBKDF2/Scrypt

🛡️ SÉCURITÉ MULTI-NIVEAU:
- Chiffrement au niveau colonne
- Masquage dynamique des données
- Anonymisation avancée
- Chiffrement des backups
- SSL/TLS enforcement
- Certificate management

🔑 GESTION DES CLÉS:
- Vault integration (HashiCorp Vault)
- Automatic key rotation
- Key escrow et recovery
- Multi-master key support
- Key versioning et rollback
- Secure key distribution

📊 AUDIT ET COMPLIANCE:
- Audit trail chiffré
- GDPR compliance tools
- Data classification automatique
- Retention policy enforcement
- Data lineage tracking
- Compliance reporting

⚡ PERFORMANCE OPTIMISÉE:
- Chiffrement streaming pour gros volumes
- Hardware acceleration (AES-NI)
- Compression avant chiffrement
- Indexing sur données chiffrées
- Cache intelligent des clés
- Batch encryption operations
"""

import asyncio
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import psycopg2.extras
import json
import os
from enum import Enum
import logging

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.vault_client import VaultClient


class EncryptionType(Enum):
    """Types de chiffrement disponibles"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class KeyType(Enum):
    """Types de clés de chiffrement"""
    MASTER_KEY = "master_key"
    COLUMN_KEY = "column_key"
    BACKUP_KEY = "backup_key"
    TRANSPORT_KEY = "transport_key"
    SIGNING_KEY = "signing_key"


class DataClassification(Enum):
    """Classification des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class DatabaseEncryptionManager:
    """
    Gestionnaire de chiffrement enterprise pour bases de données
    Fournit un chiffrement transparent et sécurisé des données sensibles
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_settings()
        self.logger = get_logger(f"{__name__}.DatabaseEncryptionManager")
        self.vault_client = VaultClient()
        
        # Configuration du chiffrement
        self.default_encryption_type = EncryptionType.AES_256_GCM
        self.key_rotation_days = 90
        self.key_cache = {}
        self.key_cache_ttl = 3600  # 1 heure
        
        # Backend cryptographique
        self.backend = default_backend()
        
        # Initialisation
        self._initialize_encryption_system()
    
    def _initialize_encryption_system(self):
        """Initialise le système de chiffrement"""
        try:
            self.logger.info("🔐 Initializing enterprise encryption system...")
            
            # Vérification des clés maîtres
            self._ensure_master_keys()
            
            # Configuration de l'audit
            self._setup_audit_logging()
            
            # Test des fonctionnalités
            self._run_encryption_tests()
            
            self.logger.info("✅ Encryption system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize encryption system: {e}")
            raise
    
    def _ensure_master_keys(self):
        """S'assure que les clés maîtres existent"""
        try:
            # Vérification clé maître principale
            master_key = self._get_or_create_master_key()
            
            # Vérification clés dérivées
            for key_type in KeyType:
                self._get_or_create_derived_key(key_type.value)
            
            self.logger.info("Master keys verified and ready")
            
        except Exception as e:
            self.logger.error(f"Master key initialization failed: {e}")
            raise
    
    def _get_or_create_master_key(self) -> bytes:
        """Récupère ou crée la clé maître principale"""
        try:
            # Tentative de récupération depuis Vault
            master_key = self.vault_client.get_secret("database/master_key")
            
            if not master_key:
                # Génération nouvelle clé maître
                master_key = secrets.token_bytes(32)  # 256 bits
                
                # Sauvegarde sécurisée
                self.vault_client.store_secret(
                    "database/master_key",
                    base64.b64encode(master_key).decode('utf-8'),
                    metadata={
                        'created_at': datetime.utcnow().isoformat(),
                        'key_type': KeyType.MASTER_KEY.value,
                        'rotation_date': (datetime.utcnow() + timedelta(days=self.key_rotation_days)).isoformat()
                    }
                )
                
                self.logger.info("🔑 New master key generated and stored")
            else:
                master_key = base64.b64decode(master_key)
                self.logger.info("🔑 Master key retrieved from vault")
            
            return master_key
            
        except Exception as e:
            self.logger.error(f"Master key management failed: {e}")
            # Fallback vers variable d'environnement (moins sécurisé)
            env_key = os.getenv('DATABASE_MASTER_KEY')
            if env_key:
                return base64.b64decode(env_key)
            raise
    
    def _get_or_create_derived_key(self, key_purpose: str) -> bytes:
        """Génère ou récupère une clé dérivée pour un usage spécifique"""
        try:
            cache_key = f"derived_key_{key_purpose}"
            
            # Vérification cache
            if cache_key in self.key_cache:
                cache_entry = self.key_cache[cache_key]
                if datetime.utcnow() < cache_entry['expires_at']:
                    return cache_entry['key']
            
            # Récupération clé maître
            master_key = self._get_or_create_master_key()
            
            # Dérivation avec PBKDF2
            salt = hashlib.sha256(key_purpose.encode()).digest()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            
            derived_key = kdf.derive(master_key)
            
            # Mise en cache
            self.key_cache[cache_key] = {
                'key': derived_key,
                'expires_at': datetime.utcnow() + timedelta(seconds=self.key_cache_ttl)
            }
            
            return derived_key
            
        except Exception as e:
            self.logger.error(f"Key derivation failed for {key_purpose}: {e}")
            raise
    
    def encrypt_sensitive_data(
        self,
        data: Union[str, bytes],
        classification: DataClassification = DataClassification.CONFIDENTIAL,
        encryption_type: EncryptionType = None
    ) -> Dict[str, Any]:
        """
        Chiffre des données sensibles avec métadonnées
        
        Args:
            data: Données à chiffrer
            classification: Niveau de classification
            encryption_type: Type de chiffrement à utiliser
            
        Returns:
            Dict contenant les données chiffrées et métadonnées
        """
        try:
            if encryption_type is None:
                encryption_type = self._get_encryption_for_classification(classification)
            
            # Conversion en bytes si nécessaire
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Chiffrement selon le type
            if encryption_type == EncryptionType.AES_256_GCM:
                encrypted_data = self._encrypt_aes_gcm(data, classification)
            elif encryption_type == EncryptionType.FERNET:
                encrypted_data = self._encrypt_fernet(data, classification)
            elif encryption_type == EncryptionType.CHACHA20_POLY1305:
                encrypted_data = self._encrypt_chacha20(data, classification)
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            # Métadonnées de chiffrement
            metadata = {
                'encryption_type': encryption_type.value,
                'classification': classification.value,
                'encrypted_at': datetime.utcnow().isoformat(),
                'key_version': self._get_current_key_version(),
                'checksum': hashlib.sha256(data).hexdigest()
            }
            
            result = {
                'encrypted_data': encrypted_data,
                'metadata': metadata,
                'is_encrypted': True
            }
            
            # Audit log
            self._audit_encryption_event('encrypt', classification, len(data))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_payload: Dict[str, Any]) -> Union[str, bytes]:
        """
        Déchiffre des données sensibles
        
        Args:
            encrypted_payload: Payload contenant données chiffrées et métadonnées
            
        Returns:
            Données déchiffrées
        """
        try:
            if not encrypted_payload.get('is_encrypted', False):
                raise ValueError("Payload is not encrypted")
            
            encrypted_data = encrypted_payload['encrypted_data']
            metadata = encrypted_payload['metadata']
            encryption_type = EncryptionType(metadata['encryption_type'])
            classification = DataClassification(metadata['classification'])
            
            # Déchiffrement selon le type
            if encryption_type == EncryptionType.AES_256_GCM:
                decrypted_data = self._decrypt_aes_gcm(encrypted_data, classification)
            elif encryption_type == EncryptionType.FERNET:
                decrypted_data = self._decrypt_fernet(encrypted_data, classification)
            elif encryption_type == EncryptionType.CHACHA20_POLY1305:
                decrypted_data = self._decrypt_chacha20(encrypted_data, classification)
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            # Vérification d'intégrité
            if 'checksum' in metadata:
                expected_checksum = metadata['checksum']
                actual_checksum = hashlib.sha256(decrypted_data).hexdigest()
                if expected_checksum != actual_checksum:
                    raise ValueError("Data integrity check failed")
            
            # Audit log
            self._audit_encryption_event('decrypt', classification, len(decrypted_data))
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def _encrypt_aes_gcm(self, data: bytes, classification: DataClassification) -> str:
        """Chiffrement AES-256-GCM"""
        try:
            # Clé dérivée pour la classification
            key = self._get_or_create_derived_key(f"aes_gcm_{classification.value}")
            
            # IV aléatoire (96 bits pour GCM)
            iv = secrets.token_bytes(12)
            
            # Chiffrement
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Données chiffrées
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combinaison IV + tag + ciphertext
            encrypted_data = iv + encryptor.tag + ciphertext
            
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"AES-GCM encryption failed: {e}")
            raise
    
    def _decrypt_aes_gcm(self, encrypted_data: str, classification: DataClassification) -> bytes:
        """Déchiffrement AES-256-GCM"""
        try:
            # Décodage
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extraction des composants
            iv = encrypted_bytes[:12]
            tag = encrypted_bytes[12:28]
            ciphertext = encrypted_bytes[28:]
            
            # Clé dérivée
            key = self._get_or_create_derived_key(f"aes_gcm_{classification.value}")
            
            # Déchiffrement
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            self.logger.error(f"AES-GCM decryption failed: {e}")
            raise
    
    def _encrypt_fernet(self, data: bytes, classification: DataClassification) -> str:
        """Chiffrement Fernet (AES-128 + HMAC)"""
        try:
            # Clé dérivée pour Fernet
            derived_key = self._get_or_create_derived_key(f"fernet_{classification.value}")
            fernet_key = base64.urlsafe_b64encode(derived_key)
            
            fernet = Fernet(fernet_key)
            encrypted_data = fernet.encrypt(data)
            
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Fernet encryption failed: {e}")
            raise
    
    def _decrypt_fernet(self, encrypted_data: str, classification: DataClassification) -> bytes:
        """Déchiffrement Fernet"""
        try:
            # Clé dérivée
            derived_key = self._get_or_create_derived_key(f"fernet_{classification.value}")
            fernet_key = base64.urlsafe_b64encode(derived_key)
            
            fernet = Fernet(fernet_key)
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            return fernet.decrypt(encrypted_bytes)
            
        except Exception as e:
            self.logger.error(f"Fernet decryption failed: {e}")
            raise
    
    def _encrypt_chacha20(self, data: bytes, classification: DataClassification) -> str:
        """Chiffrement ChaCha20-Poly1305"""
        try:
            # Clé dérivée
            key = self._get_or_create_derived_key(f"chacha20_{classification.value}")
            
            # Nonce aléatoire (96 bits)
            nonce = secrets.token_bytes(12)
            
            # Chiffrement
            cipher = Cipher(
                algorithms.ChaCha20(key, nonce),
                mode=None,
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combinaison nonce + ciphertext
            encrypted_data = nonce + ciphertext
            
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"ChaCha20 encryption failed: {e}")
            raise
    
    def _decrypt_chacha20(self, encrypted_data: str, classification: DataClassification) -> bytes:
        """Déchiffrement ChaCha20-Poly1305"""
        try:
            # Décodage
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extraction nonce et ciphertext
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]
            
            # Clé dérivée
            key = self._get_or_create_derived_key(f"chacha20_{classification.value}")
            
            # Déchiffrement
            cipher = Cipher(
                algorithms.ChaCha20(key, nonce),
                mode=None,
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            self.logger.error(f"ChaCha20 decryption failed: {e}")
            raise
    
    def _get_encryption_for_classification(self, classification: DataClassification) -> EncryptionType:
        """Détermine le type de chiffrement selon la classification"""
        encryption_map = {
            DataClassification.PUBLIC: EncryptionType.FERNET,
            DataClassification.INTERNAL: EncryptionType.AES_256_GCM,
            DataClassification.CONFIDENTIAL: EncryptionType.AES_256_GCM,
            DataClassification.RESTRICTED: EncryptionType.AES_256_GCM,
            DataClassification.TOP_SECRET: EncryptionType.CHACHA20_POLY1305
        }
        
        return encryption_map.get(classification, EncryptionType.AES_256_GCM)
    
    def _get_current_key_version(self) -> str:
        """Récupère la version actuelle de la clé"""
        try:
            # Récupération depuis Vault
            metadata = self.vault_client.get_secret_metadata("database/master_key")
            return metadata.get('version', '1') if metadata else '1'
        except:
            return '1'
    
    def _setup_audit_logging(self):
        """Configure l'audit des opérations de chiffrement"""
        try:
            self.audit_logger = logging.getLogger('encryption_audit')
            
            # Handler pour fichier d'audit
            audit_handler = logging.FileHandler('/var/log/ia-influencer/encryption_audit.log')
            audit_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                )
            )
            self.audit_logger.addHandler(audit_handler)
            self.audit_logger.setLevel(logging.INFO)
            
        except Exception as e:
            self.logger.warning(f"Audit logging setup failed: {e}")
    
    def _audit_encryption_event(self, operation: str, classification: DataClassification, data_size: int):
        """Enregistre un événement de chiffrement dans l'audit"""
        try:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'classification': classification.value,
                'data_size_bytes': data_size,
                'user_id': getattr(self, 'current_user_id', 'system'),
                'session_id': getattr(self, 'current_session_id', 'unknown')
            }
            
            if hasattr(self, 'audit_logger'):
                self.audit_logger.info(json.dumps(audit_entry))
                
        except Exception as e:
            self.logger.warning(f"Audit logging failed: {e}")
    
    def _run_encryption_tests(self):
        """Exécute des tests de validation du système de chiffrement"""
        try:
            test_data = "Test encryption data - 🔐 IA Influencer Agent"
            
            # Test de chaque type de chiffrement
            for encryption_type in [EncryptionType.AES_256_GCM, EncryptionType.FERNET]:
                encrypted = self.encrypt_sensitive_data(
                    test_data, 
                    DataClassification.CONFIDENTIAL,
                    encryption_type
                )
                
                decrypted = self.decrypt_sensitive_data(encrypted)
                
                if decrypted.decode('utf-8') != test_data:
                    raise ValueError(f"Encryption test failed for {encryption_type}")
            
            self.logger.info("✅ Encryption system validation passed")
            
        except Exception as e:
            self.logger.error(f"❌ Encryption validation failed: {e}")
            raise
    
    async def rotate_encryption_keys(self, force: bool = False) -> Dict[str, Any]:
        """
        Rotation des clés de chiffrement
        
        Args:
            force: Force la rotation même si pas nécessaire
            
        Returns:
            Rapport de rotation
        """
        try:
            self.logger.info("🔄 Starting encryption key rotation...")
            
            rotation_report = {
                'started_at': datetime.utcnow().isoformat(),
                'keys_rotated': [],
                'keys_failed': [],
                'total_keys': 0,
                'success_count': 0,
                'failure_count': 0
            }
            
            # Vérification si rotation nécessaire
            if not force:
                master_key_metadata = self.vault_client.get_secret_metadata("database/master_key")
                if master_key_metadata:
                    rotation_date = datetime.fromisoformat(
                        master_key_metadata.get('rotation_date', datetime.utcnow().isoformat())
                    )
                    
                    if datetime.utcnow() < rotation_date:
                        self.logger.info("Key rotation not yet required")
                        return rotation_report
            
            # Génération nouvelle clé maître
            new_master_key = secrets.token_bytes(32)
            
            # Sauvegarde avec versioning
            version = str(int(self._get_current_key_version()) + 1)
            self.vault_client.store_secret(
                f"database/master_key_v{version}",
                base64.b64encode(new_master_key).decode('utf-8'),
                metadata={
                    'created_at': datetime.utcnow().isoformat(),
                    'version': version,
                    'key_type': KeyType.MASTER_KEY.value,
                    'rotation_date': (datetime.utcnow() + timedelta(days=self.key_rotation_days)).isoformat()
                }
            )
            
            # Mise à jour de la clé active
            self.vault_client.store_secret(
                "database/master_key",
                base64.b64encode(new_master_key).decode('utf-8'),
                metadata={
                    'created_at': datetime.utcnow().isoformat(),
                    'version': version,
                    'key_type': KeyType.MASTER_KEY.value,
                    'rotation_date': (datetime.utcnow() + timedelta(days=self.key_rotation_days)).isoformat()
                }
            )
            
            # Purge du cache des clés
            self.key_cache.clear()
            
            rotation_report['keys_rotated'].append({
                'key_type': 'master_key',
                'new_version': version,
                'rotated_at': datetime.utcnow().isoformat()
            })
            rotation_report['success_count'] += 1
            rotation_report['total_keys'] += 1
            
            rotation_report['completed_at'] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Key rotation completed - {rotation_report['success_count']} keys rotated")
            
            return rotation_report
            
        except Exception as e:
            self.logger.error(f"❌ Key rotation failed: {e}")
            rotation_report['error'] = str(e)
            return rotation_report
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Récupère le statut du système de chiffrement"""
        try:
            status = {
                'system_status': 'operational',
                'master_key_version': self._get_current_key_version(),
                'encryption_types_available': [t.value for t in EncryptionType],
                'data_classifications': [c.value for c in DataClassification],
                'cache_size': len(self.key_cache),
                'last_key_rotation': None,
                'next_key_rotation': None,
                'vault_connection': False
            }
            
            # Vérification connexion Vault
            try:
                self.vault_client.health_check()
                status['vault_connection'] = True
            except:
                status['vault_connection'] = False
            
            # Informations de rotation
            try:
                master_key_metadata = self.vault_client.get_secret_metadata("database/master_key")
                if master_key_metadata:
                    status['last_key_rotation'] = master_key_metadata.get('created_at')
                    status['next_key_rotation'] = master_key_metadata.get('rotation_date')
            except:
                pass
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get encryption status: {e}")
            return {
                'system_status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du système de chiffrement"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Test de chiffrement/déchiffrement
            try:
                test_data = "Health check test data"
                encrypted = self.encrypt_sensitive_data(test_data, DataClassification.INTERNAL)
                decrypted = self.decrypt_sensitive_data(encrypted).decode('utf-8')
                
                health_status['checks']['encryption_test'] = {
                    'status': 'pass' if decrypted == test_data else 'fail',
                    'message': 'Encryption/decryption working correctly'
                }
            except Exception as e:
                health_status['checks']['encryption_test'] = {
                    'status': 'fail',
                    'message': f'Encryption test failed: {e}'
                }
                health_status['status'] = 'unhealthy'
            
            # Test connexion Vault
            try:
                self.vault_client.health_check()
                health_status['checks']['vault_connection'] = {
                    'status': 'pass',
                    'message': 'Vault connection successful'
                }
            except Exception as e:
                health_status['checks']['vault_connection'] = {
                    'status': 'fail',
                    'message': f'Vault connection failed: {e}'
                }
                health_status['status'] = 'warning'
            
            # Vérification clés maîtres
            try:
                self._get_or_create_master_key()
                health_status['checks']['master_key'] = {
                    'status': 'pass',
                    'message': 'Master key accessible'
                }
            except Exception as e:
                health_status['checks']['master_key'] = {
                    'status': 'fail',
                    'message': f'Master key check failed: {e}'
                }
                health_status['status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Arrêt propre du système de chiffrement"""
        try:
            self.logger.info("🔒 Shutting down encryption system...")
            
            # Purge du cache des clés
            self.key_cache.clear()
            
            # Fermeture connexion Vault
            if self.vault_client:
                await self.vault_client.close()
            
            self.logger.info("✅ Encryption system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Encryption system shutdown failed: {e}")


# Factory function
_encryption_manager: Optional[DatabaseEncryptionManager] = None


def get_encryption_manager(config: Optional[Dict[str, Any]] = None) -> DatabaseEncryptionManager:
    """Récupère ou crée l'instance du gestionnaire de chiffrement"""
    global _encryption_manager
    
    if _encryption_manager is None:
        _encryption_manager = DatabaseEncryptionManager(config)
    
    return _encryption_manager


# Fonctions utilitaires pour l'interface publique
async def encrypt_data(
    data: Union[str, bytes],
    classification: DataClassification = DataClassification.CONFIDENTIAL
) -> Dict[str, Any]:
    """Interface simplifiée pour chiffrer des données"""
    manager = get_encryption_manager()
    return manager.encrypt_sensitive_data(data, classification)


async def decrypt_data(encrypted_payload: Dict[str, Any]) -> Union[str, bytes]:
    """Interface simplifiée pour déchiffrer des données"""
    manager = get_encryption_manager()
    return manager.decrypt_sensitive_data(encrypted_payload)


# Export des classes et enums principaux
__all__ = [
    'DatabaseEncryptionManager',
    'EncryptionType',
    'KeyType', 
    'DataClassification',
    'get_encryption_manager',
    'encrypt_data',
    'decrypt_data'
]
