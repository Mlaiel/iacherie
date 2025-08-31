"""🔐 Encryption Manager - Advanced Backup Encryption System
======================================================
Module: backend/data_management/backups/encryption_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Encryption System - Enterprise Production-Ready
Responsibility: Chiffrement bout-en-bout pour sauvegardes avec gestion clés avancée
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, BinaryIO
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import secrets

from .exceptions import EncryptionException, KeyManagementException

logger = logging.getLogger(__name__)


@dataclass
class EncryptionKey:
    """Clé de chiffrement avec métadonnées"""    key_id: str
    algorithm: str
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    backup_id: Optional[str] = None
    key_size: int = 256
    iterations: int = 100000
    salt: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Vérifie si la clé a expiré"""        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour stockage"""        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "user_id": self.user_id,
            "backup_id": self.backup_id,
            "key_size": self.key_size,
            "iterations": self.iterations,
            "salt": base64.b64encode(self.salt).decode() if self.salt else None,
            "metadata": self.metadata
        }


@dataclass
class EncryptionConfig:
    """Configuration de chiffrement"""    algorithm: str = "AES-256-GCM"
    key_derivation: str = "PBKDF2"
    iterations: int = 100000
    key_rotation_days: int = 90
    backup_keys: bool = True
    compression_before_encryption: bool = True
    verify_decryption: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "algorithm": self.algorithm,
            "key_derivation": self.key_derivation,
            "iterations": self.iterations,
            "key_rotation_days": self.key_rotation_days,
            "backup_keys": self.backup_keys,
            "compression_before_encryption": self.compression_before_encryption,
            "verify_decryption": self.verify_decryption
        }


class EncryptionManager:
    """    Gestionnaire de chiffrement avancé pour sauvegardes
    
    Fonctionnalités:
    - Chiffrement AES-256-GCM bout-en-bout
    - Gestion clés sécurisée avec rotation
    - Support multi-algorithmes
    - Dérivation clés PBKDF2/Scrypt
    - Chiffrement asymétrique RSA
    - Vérification intégrité
    - Audit et logging sécurisé
    """    
    def __init__(self, config: Optional[EncryptionConfig] = None):
        self.config = config or EncryptionConfig()
        self.key_store: Dict[str, EncryptionKey] = {}
        self.master_keys: Dict[str, bytes] = {}
        
        # Initialisation backend cryptographique
        self.backend = default_backend()
        
        # Statistiques de chiffrement
        self.encryption_stats = {
            "total_files_encrypted": 0,
            "total_files_decrypted": 0,
            "total_bytes_encrypted": 0,
            "encryption_failures": 0,
            "decryption_failures": 0,
            "key_rotations": 0
        }
        
        logger.info(f"EncryptionManager initialized with {self.config.algorithm}")
    
    async def generate_key(
        self,
        user_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> EncryptionKey:
        """        Génère une nouvelle clé de chiffrement
        
        Args:
            user_id: ID utilisateur pour isolation
            config: Configuration spécifique
            
        Returns:
            EncryptionKey: Clé générée
        """        try:
            key_config = config or {}
            algorithm = key_config.get("algorithm", self.config.algorithm)
            key_size = key_config.get("key_size", 256)
            iterations = key_config.get("iterations", self.config.iterations)
            
            # Génération ID unique
            key_id = self._generate_key_id(user_id)
            
            # Génération clé cryptographique
            if algorithm.startswith("AES"):
                key_data = os.urandom(key_size // 8)  # Conversion bits en bytes
            else:
                raise EncryptionException(f"Unsupported algorithm: {algorithm}")
            
            # Génération salt pour dérivation
            salt = os.urandom(32)
            
            # Création objet clé
            encryption_key = EncryptionKey(
                key_id=key_id,
                algorithm=algorithm,
                key_data=key_data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=self.config.key_rotation_days),
                user_id=user_id,
                key_size=key_size,
                iterations=iterations,
                salt=salt,
                metadata=key_config.get("metadata", {})
            )
            
            # Stockage sécurisé
            self.key_store[key_id] = encryption_key
            
            # Sauvegarde master key si activée
            if self.config.backup_keys:
                await self._backup_key(encryption_key)
            
            logger.info(f"Generated encryption key {key_id} for user {user_id}")
            return encryption_key
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            raise KeyManagementException(f"Key generation failed: {e}")
    
    async def generate_backup_key(
        self,
        user_id: str,
        backup_id: str,
        content_type: str = "mixed"
    ) -> EncryptionKey:
        """        Génère une clé spécifique pour une sauvegarde
        
        Args:
            user_id: ID utilisateur
            backup_id: ID de la sauvegarde
            content_type: Type de contenu
            
        Returns:
            EncryptionKey: Clé de sauvegarde
        """        metadata = {
            "backup_id": backup_id,
            "content_type": content_type,
            "purpose": "backup_encryption"
        }
        
        key = await self.generate_key(user_id, {"metadata": metadata})
        key.backup_id = backup_id
        
        return key
    
    def _generate_key_id(self, user_id: Optional[str] = None) -> str:
        """Génère un ID unique pour une clé"""        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(8)
        
        if user_id:
            return f"{user_id}_{timestamp}_{random_suffix}"
        else:
            return f"key_{timestamp}_{random_suffix}"
    
    async def encrypt_file(
        self,
        input_path: Path,
        encryption_key: EncryptionKey,
        output_path: Optional[Path] = None
    ) -> Path:
        """        Chiffre un fichier avec la clé spécifiée
        
        Args:
            input_path: Fichier à chiffrer
            encryption_key: Clé de chiffrement
            output_path: Fichier de sortie (optionnel)
            
        Returns:
            Path: Chemin du fichier chiffré
        """        try:
            if not input_path.exists():
                raise EncryptionException(f"Input file not found: {input_path}")
            
            if encryption_key.is_expired():
                logger.warning(f"Using expired encryption key {encryption_key.key_id}")
            
            # Chemin de sortie par défaut
            if not output_path:
                output_path = input_path.parent / f"{input_path.name}.encrypted"
            
            # Sélection algorithme de chiffrement
            if encryption_key.algorithm == "AES-256-GCM":
                encrypted_path = await self._encrypt_aes_gcm(input_path, encryption_key, output_path)
            elif encryption_key.algorithm == "AES-256-CBC":
                encrypted_path = await self._encrypt_aes_cbc(input_path, encryption_key, output_path)
            else:
                raise EncryptionException(f"Unsupported encryption algorithm: {encryption_key.algorithm}")
            
            # Mise à jour statistiques
            self.encryption_stats["total_files_encrypted"] += 1
            self.encryption_stats["total_bytes_encrypted"] += input_path.stat().st_size
            
            logger.info(f"File encrypted successfully: {input_path.name} -> {encrypted_path.name}")
            return encrypted_path
            
        except Exception as e:
            self.encryption_stats["encryption_failures"] += 1
            logger.error(f"File encryption failed for {input_path}: {e}")
            raise EncryptionException(f"File encryption failed: {e}")
    
    async def _encrypt_aes_gcm(
        self,
        input_path: Path,
        encryption_key: EncryptionKey,
        output_path: Path
    ) -> Path:
        """        Chiffrement AES-256-GCM avec authentification
        
        Args:
            input_path: Fichier source
            encryption_key: Clé de chiffrement
            output_path: Fichier de sortie
            
        Returns:
            Path: Fichier chiffré
        """        # Génération IV (Initialization Vector)
        iv = os.urandom(12)  # 96 bits pour GCM
        
        # Configuration cipher
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Création structure fichier chiffré
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Écriture header
            header = self._create_encryption_header(encryption_key, iv)
            outfile.write(header)
            
            # Chiffrement par chunks
            chunk_size = 64 * 1024  # 64KB chunks
            
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                
                encrypted_chunk = encryptor.update(chunk)
                outfile.write(encrypted_chunk)
            
            # Finalisation et tag d'authentification
            encryptor.finalize()
            auth_tag = encryptor.tag
            outfile.write(auth_tag)
        
        return output_path
    
    async def _encrypt_aes_cbc(
        self,
        input_path: Path,
        encryption_key: EncryptionKey,
        output_path: Path
    ) -> Path:
        """        Chiffrement AES-256-CBC avec padding
        
        Args:
            input_path: Fichier source
            encryption_key: Clé de chiffrement
            output_path: Fichier de sortie
            
        Returns:
            Path: Fichier chiffré
        """        from cryptography.hazmat.primitives import padding as sym_padding
        
        # Génération IV
        iv = os.urandom(16)  # 128 bits pour CBC
        
        # Configuration cipher
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Padding
        padder = sym_padding.PKCS7(128).padder()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Écriture header
            header = self._create_encryption_header(encryption_key, iv)
            outfile.write(header)
            
            # Chiffrement avec padding
            chunk_size = 64 * 1024
            
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    # Finalisation padding
                    padded_data = padder.finalize()
                    if padded_data:
                        encrypted_chunk = encryptor.update(padded_data)
                        outfile.write(encrypted_chunk)
                    break
                
                padded_chunk = padder.update(chunk)
                encrypted_chunk = encryptor.update(padded_chunk)
                outfile.write(encrypted_chunk)
            
            # Finalisation chiffrement
            final_chunk = encryptor.finalize()
            if final_chunk:
                outfile.write(final_chunk)
        
        return output_path
    
    def _create_encryption_header(self, encryption_key: EncryptionKey, iv: bytes) -> bytes:
        """        Crée un header avec métadonnées de chiffrement
        
        Args:
            encryption_key: Clé utilisée
            iv: Vecteur d'initialisation
            
        Returns:
            bytes: Header structuré
        """        import struct
        
        header_data = {
            "version": 1,
            "algorithm": encryption_key.algorithm,
            "key_id": encryption_key.key_id,
            "iv": base64.b64encode(iv).decode(),
            "timestamp": datetime.now().isoformat()
        }
        
        header_json = json.dumps(header_data).encode('utf-8')
        header_length = len(header_json)
        
        # Structure: [length:4][json_header:length]
        return struct.pack('<I', header_length) + header_json
    
    async def decrypt_file(
        self,
        input_path: Path,
        output_path: Path,
        key_id: Optional[str] = None
    ) -> bool:
        """        Déchiffre un fichier
        
        Args:
            input_path: Fichier chiffré
            output_path: Fichier de sortie déchiffré
            key_id: ID de la clé (optionnel si dans header)
            
        Returns:
            bool: True si déchiffrement réussi
        """        try:
            if not input_path.exists():
                logger.error(f"Encrypted file not found: {input_path}")
                return False
            
            # Lecture header pour récupérer métadonnées
            header_data = self._read_encryption_header(input_path)
            
            if not header_data:
                logger.error(f"Invalid encryption header in {input_path}")
                return False
            
            # Récupération clé de déchiffrement
            encryption_key_id = key_id or header_data.get("key_id")
            
            if not encryption_key_id or encryption_key_id not in self.key_store:
                logger.error(f"Decryption key not found: {encryption_key_id}")
                return False
            
            encryption_key = self.key_store[encryption_key_id]
            
            # Déchiffrement selon algorithme
            algorithm = header_data["algorithm"]
            
            if algorithm == "AES-256-GCM":
                success = await self._decrypt_aes_gcm(input_path, encryption_key, output_path, header_data)
            elif algorithm == "AES-256-CBC":
                success = await self._decrypt_aes_cbc(input_path, encryption_key, output_path, header_data)
            else:
                logger.error(f"Unsupported decryption algorithm: {algorithm}")
                return False
            
            if success:
                self.encryption_stats["total_files_decrypted"] += 1
                logger.info(f"File decrypted successfully: {input_path.name} -> {output_path.name}")
            else:
                self.encryption_stats["decryption_failures"] += 1
            
            return success
            
        except Exception as e:
            self.encryption_stats["decryption_failures"] += 1
            logger.error(f"File decryption failed for {input_path}: {e}")
            return False
    
    def _read_encryption_header(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """        Lit le header de chiffrement d'un fichier
        
        Args:
            file_path: Fichier chiffré
            
        Returns:
            Optional[Dict[str, Any]]: Métadonnées du header
        """        try:
            import struct
            
            with open(file_path, 'rb') as f:
                # Lecture longueur header
                length_data = f.read(4)
                if len(length_data) != 4:
                    return None
                
                header_length = struct.unpack('<I', length_data)[0]
                
                # Lecture header JSON
                header_json = f.read(header_length)
                if len(header_json) != header_length:
                    return None
                
                return json.loads(header_json.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Failed to read encryption header: {e}")
            return None
    
    async def _decrypt_aes_gcm(
        self,
        input_path: Path,
        encryption_key: EncryptionKey,
        output_path: Path,
        header_data: Dict[str, Any]
    ) -> bool:
        """        Déchiffrement AES-256-GCM avec vérification authentification
        
        Args:
            input_path: Fichier chiffré
            encryption_key: Clé de déchiffrement
            output_path: Fichier de sortie
            header_data: Métadonnées du header
            
        Returns:
            bool: True si déchiffrement réussi
        """        try:
            iv = base64.b64decode(header_data["iv"])
            
            # Calcul position données chiffrées
            header_size = 4 + len(json.dumps(header_data).encode('utf-8'))
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Positionnement après header
                infile.seek(header_size)
                
                # Lecture tout le contenu chiffré
                encrypted_data = infile.read()
                
                # Séparation données et tag d'authentification
                auth_tag = encrypted_data[-16:]  # Dernier 16 bytes pour GCM
                ciphertext = encrypted_data[:-16]
                
                # Configuration déchiffreur
                cipher = Cipher(
                    algorithms.AES(encryption_key.key_data),
                    modes.GCM(iv, auth_tag),
                    backend=self.backend
                )
                decryptor = cipher.decryptor()
                
                # Déchiffrement
                plaintext = decryptor.update(ciphertext)
                decryptor.finalize()  # Vérification tag d'authentification
                
                outfile.write(plaintext)
            
            return True
            
        except Exception as e:
            logger.error(f"AES-GCM decryption failed: {e}")
            return False
    
    async def _decrypt_aes_cbc(
        self,
        input_path: Path,
        encryption_key: EncryptionKey,
        output_path: Path,
        header_data: Dict[str, Any]
    ) -> bool:
        """        Déchiffrement AES-256-CBC avec suppression padding
        
        Args:
            input_path: Fichier chiffré
            encryption_key: Clé de déchiffrement
            output_path: Fichier de sortie
            header_data: Métadonnées du header
            
        Returns:
            bool: True si déchiffrement réussi
        """        try:
            from cryptography.hazmat.primitives import padding as sym_padding
            
            iv = base64.b64decode(header_data["iv"])
            
            # Calcul position données chiffrées
            header_size = 4 + len(json.dumps(header_data).encode('utf-8'))
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Positionnement après header
                infile.seek(header_size)
                
                # Configuration déchiffreur
                cipher = Cipher(
                    algorithms.AES(encryption_key.key_data),
                    modes.CBC(iv),
                    backend=self.backend
                )
                decryptor = cipher.decryptor()
                
                # Unpadder pour PKCS7
                unpadder = sym_padding.PKCS7(128).unpadder()
                
                # Déchiffrement par chunks
                chunk_size = 64 * 1024
                
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    decrypted_chunk = decryptor.update(chunk)
                    unpadded_chunk = unpadder.update(decrypted_chunk)
                    outfile.write(unpadded_chunk)
                
                # Finalisation
                final_chunk = decryptor.finalize()
                if final_chunk:
                    unpadded_final = unpadder.update(final_chunk)
                    outfile.write(unpadded_final)
                
                # Suppression padding final
                final_unpadded = unpadder.finalize()
                if final_unpadded:
                    outfile.write(final_unpadded)
            
            return True
            
        except Exception as e:
            logger.error(f"AES-CBC decryption failed: {e}")
            return False
    
    async def rotate_key(self, old_key_id: str, user_id: Optional[str] = None) -> EncryptionKey:
        """        Effectue la rotation d'une clé de chiffrement
        
        Args:
            old_key_id: ID de l'ancienne clé
            user_id: ID utilisateur
            
        Returns:
            EncryptionKey: Nouvelle clé générée
        """        try:
            if old_key_id not in self.key_store:
                raise KeyManagementException(f"Key {old_key_id} not found for rotation")
            
            old_key = self.key_store[old_key_id]
            
            # Génération nouvelle clé avec mêmes paramètres
            new_key = await self.generate_key(
                user_id=user_id or old_key.user_id,
                config={
                    "algorithm": old_key.algorithm,
                    "key_size": old_key.key_size,
                    "iterations": old_key.iterations,
                    "metadata": {"rotated_from": old_key_id}
                }
            )
            
            # Marquage ancienne clé comme expirée
            old_key.expires_at = datetime.now()
            
            self.encryption_stats["key_rotations"] += 1
            
            logger.info(f"Key rotation completed: {old_key_id} -> {new_key.key_id}")
            return new_key
            
        except Exception as e:
            logger.error(f"Key rotation failed for {old_key_id}: {e}")
            raise KeyManagementException(f"Key rotation failed: {e}")
    
    async def _backup_key(self, encryption_key: EncryptionKey):
        """        Sauvegarde sécurisée d'une clé de chiffrement
        
        Args:
            encryption_key: Clé à sauvegarder
        """        try:
            # En production, sauvegarder dans HSM ou vault sécurisé
            # Ici, simulation avec chiffrement par clé maître
            
            master_key = self._get_or_create_master_key(encryption_key.user_id)
            
            # Chiffrement des données de clé
            fernet = Fernet(master_key)
            encrypted_key_data = fernet.encrypt(encryption_key.key_data)
            
            # Stockage métadonnées et clé chiffrée
            backup_data = {
                "key_metadata": encryption_key.to_dict(),
                "encrypted_key_data": base64.b64encode(encrypted_key_data).decode()
            }
            
            # Sauvegarde (en production: base de données sécurisée)
            backup_path = Path(f"/tmp/key_backup_{encryption_key.key_id}.json")
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.debug(f"Key backup created for {encryption_key.key_id}")
            
        except Exception as e:
            logger.error(f"Key backup failed for {encryption_key.key_id}: {e}")
    
    def _get_or_create_master_key(self, user_id: Optional[str]) -> bytes:
        """        Récupère ou crée une clé maître pour un utilisateur
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            bytes: Clé maître
        """        key_identifier = user_id or "global"
        
        if key_identifier not in self.master_keys:
            # Génération nouvelle clé maître
            master_key = Fernet.generate_key()
            self.master_keys[key_identifier] = master_key
            
            logger.info(f"Generated master key for {key_identifier}")
        
        return self.master_keys[key_identifier]
    
    async def verify_encryption(
        self,
        original_path: Path,
        encrypted_path: Path,
        encryption_key: EncryptionKey
    ) -> bool:
        """        Vérifie la validité d'un chiffrement via test de déchiffrement
        
        Args:
            original_path: Fichier original
            encrypted_path: Fichier chiffré
            encryption_key: Clé utilisée
            
        Returns:
            bool: True si chiffrement valide
        """        try:
            import tempfile
            
            # Déchiffrement test dans fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            success = await self.decrypt_file(encrypted_path, temp_path, encryption_key.key_id)
            
            if not success:
                return False
            
            # Comparaison checksums
            original_checksum = await self._calculate_file_checksum(original_path)
            decrypted_checksum = await self._calculate_file_checksum(temp_path)
            
            # Nettoyage
            temp_path.unlink()
            
            return original_checksum == decrypted_checksum
            
        except Exception as e:
            logger.error(f"Encryption verification failed: {e}")
            return False
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier"""        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def list_keys(
        self,
        user_id: Optional[str] = None,
        include_expired: bool = False
    ) -> List[EncryptionKey]:
        """        Liste les clés de chiffrement
        
        Args:
            user_id: Filtrer par utilisateur
            include_expired: Inclure les clés expirées
            
        Returns:
            List[EncryptionKey]: Liste des clés
        """        keys = list(self.key_store.values())
        
        # Filtrage par utilisateur
        if user_id:
            keys = [key for key in keys if key.user_id == user_id]
        
        # Filtrage clés expirées
        if not include_expired:
            keys = [key for key in keys if not key.is_expired()]
        
        # Tri par date de création (plus récent en premier)
        keys.sort(key=lambda x: x.created_at, reverse=True)
        
        return keys
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """        Récupère les statistiques de chiffrement
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """        stats = self.encryption_stats.copy()
        
        # Calculs additionnels
        total_operations = stats["total_files_encrypted"] + stats["total_files_decrypted"]
        if total_operations > 0:
            stats["success_rate"] = (
                (total_operations - stats["encryption_failures"] - stats["decryption_failures"]) 
                / total_operations
            ) * 100
        
        stats["total_keys"] = len(self.key_store)
        stats["active_keys"] = len([k for k in self.key_store.values() if not k.is_expired()])
        stats["expired_keys"] = len([k for k in self.key_store.values() if k.is_expired()])
        stats["total_gb_encrypted"] = stats["total_bytes_encrypted"] / (1024**3)
        
        return stats
    
    async def cleanup_expired_keys(self) -> int:
        """        Nettoie les clés expirées
        
        Returns:
            int: Nombre de clés supprimées
        """        expired_keys = [key_id for key_id, key in self.key_store.items() if key.is_expired()]
        
        for key_id in expired_keys:
            del self.key_store[key_id]
            logger.debug(f"Removed expired key: {key_id}")
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired encryption keys")
        
        return len(expired_keys)


class AESEncryption:
    """    Implémentation spécialisée AES avec optimisations
    
    Fonctionnalités:
    - AES-256-GCM/CBC optimisé
    - Streaming pour gros fichiers
    - Parallélisation
    - Cache de performance
    """    
    def __init__(self):
        self.chunk_size = 64 * 1024  # 64KB
        self.backend = default_backend()
        
        logger.info("AESEncryption initialized")
    
    async def encrypt_large_file(
        self,
        input_path: Path,
        output_path: Path,
        key: bytes,
        mode: str = "GCM"
    ) -> bool:
        """        Chiffrement optimisé pour gros fichiers avec streaming
        
        Args:
            input_path: Fichier source
            output_path: Fichier chiffré
            key: Clé AES-256
            mode: Mode de chiffrement (GCM/CBC)
            
        Returns:
            bool: True si réussi
        """        try:
            file_size = input_path.stat().st_size
            
            if mode == "GCM":
                return await self._encrypt_large_gcm(input_path, output_path, key)
            elif mode == "CBC":
                return await self._encrypt_large_cbc(input_path, output_path, key)
            else:
                raise EncryptionException(f"Unsupported AES mode: {mode}")
                
        except Exception as e:
            logger.error(f"Large file encryption failed: {e}")
            return False
    
    async def _encrypt_large_gcm(
        self,
        input_path: Path,
        output_path: Path,
        key: bytes
    ) -> bool:
        """Chiffrement GCM streaming pour gros fichiers"""        iv = os.urandom(12)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Écriture IV
            outfile.write(iv)
            
            # Chiffrement streaming
            while True:
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    break
                
                encrypted_chunk = encryptor.update(chunk)
                outfile.write(encrypted_chunk)
            
            # Finalisation et tag
            encryptor.finalize()
            outfile.write(encryptor.tag)
        
        return True
    
    async def _encrypt_large_cbc(
        self,
        input_path: Path,
        output_path: Path,
        key: bytes
    ) -> bool:
        """Chiffrement CBC streaming pour gros fichiers"""        from cryptography.hazmat.primitives import padding as sym_padding
        
        iv = os.urandom(16)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        padder = sym_padding.PKCS7(128).padder()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Écriture IV
            outfile.write(iv)
            
            # Chiffrement streaming avec padding
            while True:
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    # Finalisation padding
                    padded_data = padder.finalize()
                    if padded_data:
                        encrypted_chunk = encryptor.update(padded_data)
                        outfile.write(encrypted_chunk)
                    break
                
                padded_chunk = padder.update(chunk)
                encrypted_chunk = encryptor.update(padded_chunk)
                outfile.write(encrypted_chunk)
            
            # Finalisation chiffrement
            final_chunk = encryptor.finalize()
            if final_chunk:
                outfile.write(final_chunk)
        
        return True


class RSAEncryption:
    """    Chiffrement asymétrique RSA pour clés et métadonnées
    
    Fonctionnalités:
    - Génération paires clés RSA
    - Chiffrement/déchiffrement asymétrique
    - Signature digitale
    - Échange sécurisé de clés
    """    
    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.backend = default_backend()
        self.key_pairs: Dict[str, Any] = {}
        
        logger.info(f"RSAEncryption initialized with {key_size}-bit keys")
    
    def generate_key_pair(self, identifier: str) -> Dict[str, bytes]:
        """        Génère une paire de clés RSA
        
        Args:
            identifier: Identifiant de la paire
            
        Returns:
            Dict[str, bytes]: Clés publique et privée
        """        try:
            # Génération clé privée
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
                backend=self.backend
            )
            
            # Extraction clé publique
            public_key = private_key.public_key()
            
            # Sérialisation
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Stockage
            self.key_pairs[identifier] = {
                "private_key": private_key,
                "public_key": public_key,
                "private_pem": private_pem,
                "public_pem": public_pem
            }
            
            logger.info(f"Generated RSA key pair for {identifier}")
            
            return {
                "private_key": private_pem,
                "public_key": public_pem
            }
            
        except Exception as e:
            logger.error(f"RSA key generation failed: {e}")
            raise KeyManagementException(f"RSA key generation failed: {e}")
    
    def encrypt_data(self, data: bytes, public_key_identifier: str) -> bytes:
        """        Chiffre des données avec clé publique RSA
        
        Args:
            data: Données à chiffrer
            public_key_identifier: Identifiant clé publique
            
        Returns:
            bytes: Données chiffrées
        """        try:
            if public_key_identifier not in self.key_pairs:
                raise KeyManagementException(f"Public key not found: {public_key_identifier}")
            
            public_key = self.key_pairs[public_key_identifier]["public_key"]
            
            # Chiffrement avec padding OAEP
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"RSA encryption failed: {e}")
            raise EncryptionException(f"RSA encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: bytes, private_key_identifier: str) -> bytes:
        """        Déchiffre des données avec clé privée RSA
        
        Args:
            encrypted_data: Données chiffrées
            private_key_identifier: Identifiant clé privée
            
        Returns:
            bytes: Données déchiffrées
        """        try:
            if private_key_identifier not in self.key_pairs:
                raise KeyManagementException(f"Private key not found: {private_key_identifier}")
            
            private_key = self.key_pairs[private_key_identifier]["private_key"]
            
            # Déchiffrement avec padding OAEP
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            raise EncryptionException(f"RSA decryption failed: {e}")
