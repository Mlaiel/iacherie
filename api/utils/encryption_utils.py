"""Encryption and Security Utilities for IA Influencer Agent Platform
Advanced cryptographic operations, secure storage, and data protection

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import hashlib
import hmac
import secrets
import base64
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import jwt
import bcrypt
import os
import json
from pathlib import Path
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"


class HashAlgorithm(Enum):
    """Hash algorithm enumeration"""    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    SCRYPT = "scrypt"
    BCRYPT = "bcrypt"


@dataclass
class EncryptedData:
    """Encrypted data container"""    ciphertext: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    nonce: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            'ciphertext': base64.b64encode(self.ciphertext).decode(),
            'algorithm': self.algorithm.value,
            'key_id': self.key_id,
            'nonce': base64.b64encode(self.nonce).decode() if self.nonce else None,
            'tag': base64.b64encode(self.tag).decode() if self.tag else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedData':
        """Create from dictionary"""        return cls(
            ciphertext=base64.b64decode(data['ciphertext']),
            algorithm=EncryptionAlgorithm(data['algorithm']),
            key_id=data['key_id'],
            nonce=base64.b64decode(data['nonce']) if data.get('nonce') else None,
            tag=base64.b64decode(data['tag']) if data.get('tag') else None,
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class KeyPair:
    """RSA key pair container"""    private_key: bytes
    public_key: bytes
    key_id: str
    key_size: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_private_key_object(self):
        """Get private key object"""        return serialization.load_pem_private_key(
            self.private_key, password=None
        )
    
    def get_public_key_object(self):
        """Get public key object"""        return serialization.load_pem_public_key(self.public_key)


class EncryptionManager:
    """Advanced encryption and decryption management"""    
    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or self._generate_master_key()
        self.encryption_keys = {}
        self.key_pairs = {}
        self.fernet_instance = None
        self._initialize_fernet()
        
    def _generate_master_key(self) -> bytes:
        """Generate secure master key"""        return secrets.token_bytes(32)  # 256-bit key
    
    def _initialize_fernet(self):
        """Initialize Fernet instance with master key"""        # Derive Fernet key from master key
        fernet_key = base64.urlsafe_b64encode(self.master_key)
        self.fernet_instance = Fernet(fernet_key)
    
    async def encrypt_data(self, 
                         data: Union[str, bytes], 
                         algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
                         key_id: Optional[str] = None) -> EncryptedData:
        """Encrypt data using specified algorithm"""        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == EncryptionAlgorithm.FERNET:
                return await self._encrypt_fernet(data, key_id)
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._encrypt_aes_gcm(data, key_id)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._encrypt_aes_cbc(data, key_id)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                return await self._encrypt_rsa(data, algorithm, key_id)
            else:
                raise EncryptionError(f"Unsupported encryption algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    async def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using stored algorithm and parameters"""        try:
            algorithm = encrypted_data.algorithm
            
            if algorithm == EncryptionAlgorithm.FERNET:
                return await self._decrypt_fernet(encrypted_data)
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._decrypt_aes_gcm(encrypted_data)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._decrypt_aes_cbc(encrypted_data)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                return await self._decrypt_rsa(encrypted_data)
            else:
                raise EncryptionError(f"Unsupported decryption algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    async def _encrypt_fernet(self, data: bytes, key_id: Optional[str]) -> EncryptedData:
        """Encrypt using Fernet (AES 128 CBC + HMAC SHA256)"""        if not key_id:
            key_id = "fernet_master"
        
        ciphertext = self.fernet_instance.encrypt(data)
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.FERNET,
            key_id=key_id
        )
    
    async def _decrypt_fernet(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt using Fernet"""        return self.fernet_instance.decrypt(encrypted_data.ciphertext)
    
    async def _encrypt_aes_gcm(self, data: bytes, key_id: Optional[str]) -> EncryptedData:
        """Encrypt using AES-256-GCM"""        if not key_id:
            key_id = f"aes_gcm_{secrets.token_hex(8)}"
        
        # Generate or get encryption key
        if key_id not in self.encryption_keys:
            self.encryption_keys[key_id] = secrets.token_bytes(32)  # 256-bit key
        
        key = self.encryption_keys[key_id]
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=key_id,
            nonce=nonce,
            tag=encryptor.tag
        )
    
    async def _decrypt_aes_gcm(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt using AES-256-GCM"""        if encrypted_data.key_id not in self.encryption_keys:
            raise EncryptionError(f"Encryption key not found: {encrypted_data.key_id}")
        
        key = self.encryption_keys[encrypted_data.key_id]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key), 
            modes.GCM(encrypted_data.nonce, encrypted_data.tag)
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        return plaintext
    
    async def _encrypt_aes_cbc(self, data: bytes, key_id: Optional[str]) -> EncryptedData:
        """Encrypt using AES-256-CBC"""        if not key_id:
            key_id = f"aes_cbc_{secrets.token_hex(8)}"
        
        # Generate or get encryption key
        if key_id not in self.encryption_keys:
            self.encryption_keys[key_id] = secrets.token_bytes(32)  # 256-bit key
        
        key = self.encryption_keys[key_id]
        iv = secrets.token_bytes(16)  # 128-bit IV for CBC
        
        # Pad data to block size
        padded_data = self._pad_data(data, 16)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            key_id=key_id,
            nonce=iv
        )
    
    async def _decrypt_aes_cbc(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt using AES-256-CBC"""        if encrypted_data.key_id not in self.encryption_keys:
            raise EncryptionError(f"Encryption key not found: {encrypted_data.key_id}")
        
        key = self.encryption_keys[encrypted_data.key_id]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(encrypted_data.nonce))
        decryptor = cipher.decryptor()
        
        # Decrypt data
        padded_plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        # Remove padding
        plaintext = self._unpad_data(padded_plaintext)
        
        return plaintext
    
    async def _encrypt_rsa(self, data: bytes, algorithm: EncryptionAlgorithm, 
                         key_id: Optional[str]) -> EncryptedData:
        """Encrypt using RSA"""        key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
        
        if not key_id:
            key_id = f"rsa_{key_size}_{secrets.token_hex(8)}"
        
        # Generate or get RSA key pair
        if key_id not in self.key_pairs:
            await self._generate_rsa_keypair(key_id, key_size)
        
        key_pair = self.key_pairs[key_id]
        public_key = key_pair.get_public_key_object()
        
        # RSA can only encrypt small amounts of data, so we use hybrid encryption
        # Generate AES key for actual data encryption
        aes_key = secrets.token_bytes(32)
        
        # Encrypt data with AES
        aes_encrypted = await self._encrypt_aes_gcm_with_key(data, aes_key)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine encrypted key and data
        combined_data = encrypted_aes_key + aes_encrypted.ciphertext
        
        return EncryptedData(
            ciphertext=combined_data,
            algorithm=algorithm,
            key_id=key_id,
            nonce=aes_encrypted.nonce,
            tag=aes_encrypted.tag,
            metadata={'aes_key_length': len(encrypted_aes_key)}
        )
    
    async def _decrypt_rsa(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt using RSA"""        if encrypted_data.key_id not in self.key_pairs:
            raise EncryptionError(f"RSA key pair not found: {encrypted_data.key_id}")
        
        key_pair = self.key_pairs[encrypted_data.key_id]
        private_key = key_pair.get_private_key_object()
        
        # Extract encrypted AES key and data
        aes_key_length = encrypted_data.metadata.get('aes_key_length', 256)
        encrypted_aes_key = encrypted_data.ciphertext[:aes_key_length]
        encrypted_data_part = encrypted_data.ciphertext[aes_key_length:]
        
        # Decrypt AES key with RSA
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data with AES
        aes_encrypted_data = EncryptedData(
            ciphertext=encrypted_data_part,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=f"temp_{encrypted_data.key_id}",
            nonce=encrypted_data.nonce,
            tag=encrypted_data.tag
        )
        
        # Temporarily store AES key
        temp_key_id = f"temp_{encrypted_data.key_id}"
        self.encryption_keys[temp_key_id] = aes_key
        
        try:
            plaintext = await self._decrypt_aes_gcm(aes_encrypted_data)
        finally:
            # Clean up temporary key
            self.encryption_keys.pop(temp_key_id, None)
        
        return plaintext
    
    async def _encrypt_aes_gcm_with_key(self, data: bytes, key: bytes) -> EncryptedData:
        """Encrypt with provided AES key"""        nonce = secrets.token_bytes(12)
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id="temp",
            nonce=nonce,
            tag=encryptor.tag
        )
    
    async def _generate_rsa_keypair(self, key_id: str, key_size: int):
        """Generate RSA key pair"""        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Store key pair
        self.key_pairs[key_id] = KeyPair(
            private_key=private_pem,
            public_key=public_pem,
            key_id=key_id,
            key_size=key_size
        )
    
    def _pad_data(self, data: bytes, block_size: int) -> bytes:
        """PKCS7 padding"""        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding"""        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    def export_key(self, key_id: str, password: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Export encryption key or key pair"""        if key_id in self.encryption_keys:
            # For symmetric keys, we can't export safely without encryption
            if password:
                # Encrypt key with password-derived key
                salt = secrets.token_bytes(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000
                )
                derived_key = kdf.derive(password.encode())
                
                fernet_key = base64.urlsafe_b64encode(derived_key)
                f = Fernet(fernet_key)
                
                encrypted_key = f.encrypt(self.encryption_keys[key_id])
                
                return {
                    'key_id': key_id,
                    'encrypted_key': base64.b64encode(encrypted_key).decode(),
                    'salt': base64.b64encode(salt).decode(),
                    'type': 'symmetric'
                }
            else:
                return None  # Cannot export without password
        
        elif key_id in self.key_pairs:
            key_pair = self.key_pairs[key_id]
            return {
                'key_id': key_id,
                'private_key': base64.b64encode(key_pair.private_key).decode(),
                'public_key': base64.b64encode(key_pair.public_key).decode(),
                'key_size': key_pair.key_size,
                'type': 'asymmetric'
            }
        
        return None


class HashGenerator:
    """Advanced hashing and message authentication"""    
    def __init__(self):
        self.hash_functions = {
            HashAlgorithm.SHA256: hashlib.sha256,
            HashAlgorithm.SHA512: hashlib.sha512,
            HashAlgorithm.BLAKE2B: hashlib.blake2b
        }
    
    def generate_hash(self, data: Union[str, bytes], 
                     algorithm: HashAlgorithm = HashAlgorithm.SHA256,
                     salt: Optional[bytes] = None) -> str:
        """Generate hash with optional salt"""        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if salt:
            data = salt + data
        
        if algorithm in self.hash_functions:
            hash_func = self.hash_functions[algorithm]
            return hash_func(data).hexdigest()
        elif algorithm == HashAlgorithm.SCRYPT:
            return self._generate_scrypt_hash(data, salt)
        elif algorithm == HashAlgorithm.BCRYPT:
            return self._generate_bcrypt_hash(data)
        else:
            raise HashError(f"Unsupported hash algorithm: {algorithm}")
    
    def _generate_scrypt_hash(self, data: bytes, salt: Optional[bytes] = None) -> str:
        """Generate Scrypt hash"""        if not salt:
            salt = secrets.token_bytes(16)
        
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            n=2**14,
            r=8,
            p=1
        )
        
        key = kdf.derive(data)
        return base64.b64encode(salt + key).decode()
    
    def _generate_bcrypt_hash(self, data: bytes) -> str:
        """Generate bcrypt hash"""        return bcrypt.hashpw(data, bcrypt.gensalt()).decode()
    
    def verify_bcrypt_hash(self, data: Union[str, bytes], hashed: str) -> bool:
        """Verify bcrypt hash"""        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return bcrypt.checkpw(data, hashed.encode())
    
    def verify_scrypt_hash(self, data: Union[str, bytes], hashed: str) -> bool:
        """Verify Scrypt hash"""        if isinstance(data, str):
            data = data.encode('utf-8')
        
        decoded = base64.b64decode(hashed.encode())
        salt = decoded[:16]
        stored_key = decoded[16:]
        
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            n=2**14,
            r=8,
            p=1
        )
        
        try:
            kdf.verify(data, stored_key)
            return True
        except:
            return False
    
    def generate_hmac(self, data: Union[str, bytes], key: bytes, 
                     algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> str:
        """Generate HMAC"""        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == HashAlgorithm.SHA256:
            return hmac.new(key, data, hashlib.sha256).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hmac.new(key, data, hashlib.sha512).hexdigest()
        else:
            raise HashError(f"HMAC not supported for algorithm: {algorithm}")
    
    def verify_hmac(self, data: Union[str, bytes], key: bytes, 
                   signature: str, algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> bool:
        """Verify HMAC signature"""        expected_signature = self.generate_hmac(data, key, algorithm)
        return hmac.compare_digest(signature, expected_signature)


class TokenValidator:
    """JWT token generation and validation"""    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = 'HS256'
    
    def generate_token(self, payload: Dict[str, Any], 
                      expires_in: Optional[int] = 3600) -> str:
        """Generate JWT token"""        if expires_in:
            payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        
        payload['iat'] = datetime.utcnow()
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate and decode JWT token"""        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {str(e)}'}
    
    def refresh_token(self, token: str, expires_in: Optional[int] = 3600) -> Optional[str]:
        """Refresh JWT token"""        validation_result = self.validate_token(token)
        
        if validation_result['valid']:
            payload = validation_result['payload'].copy()
            # Remove old timestamps
            payload.pop('exp', None)
            payload.pop('iat', None)
            
            return self.generate_token(payload, expires_in)
        
        return None


class SecureStorage:
    """Secure file and data storage"""    
    def __init__(self, storage_path: str, encryption_manager: EncryptionManager):
        self.storage_path = Path(storage_path)
        self.encryption_manager = encryption_manager
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def store_encrypted_file(self, data: Union[str, bytes], filename: str,
                                 algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> Dict[str, Any]:
        """Store encrypted file"""        try:
            # Encrypt data
            encrypted_data = await self.encryption_manager.encrypt_data(data, algorithm)
            
            # Store encrypted data
            file_path = self.storage_path / filename
            
            with open(file_path, 'wb') as f:
                # Store as JSON for metadata preservation
                storage_data = encrypted_data.to_dict()
                json_data = json.dumps(storage_data, indent=2)
                f.write(json_data.encode('utf-8'))
            
            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'algorithm': algorithm.value,
                'key_id': encrypted_data.key_id
            }
            
        except Exception as e:
            logger.error(f"Secure storage failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def retrieve_encrypted_file(self, filename: str) -> Dict[str, Any]:
        """Retrieve and decrypt file"""        try:
            file_path = self.storage_path / filename
            
            if not file_path.exists():
                return {'success': False, 'error': 'File not found'}
            
            # Load encrypted data
            with open(file_path, 'rb') as f:
                json_data = f.read().decode('utf-8')
                storage_data = json.loads(json_data)
            
            # Reconstruct encrypted data object
            encrypted_data = EncryptedData.from_dict(storage_data)
            
            # Decrypt data
            decrypted_data = await self.encryption_manager.decrypt_data(encrypted_data)
            
            return {
                'success': True,
                'data': decrypted_data,
                'metadata': encrypted_data.metadata,
                'created_at': encrypted_data.created_at
            }
            
        except Exception as e:
            logger.error(f"Secure retrieval failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def list_encrypted_files(self) -> List[Dict[str, Any]]:
        """List all encrypted files"""        files = []
        
        for file_path in self.storage_path.glob('*'):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        json_data = f.read().decode('utf-8')
                        storage_data = json.loads(json_data)
                    
                    files.append({
                        'filename': file_path.name,
                        'algorithm': storage_data.get('algorithm'),
                        'key_id': storage_data.get('key_id'),
                        'created_at': storage_data.get('created_at'),
                        'size_bytes': file_path.stat().st_size
                    })
                except:
                    # Skip invalid files
                    continue
        
        return files


class CryptoHelper:
    """Cryptographic utility functions"""    
    @staticmethod
    def generate_secure_random(length: int) -> bytes:
        """Generate cryptographically secure random bytes"""        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure URL-safe token"""        return secrets.token_urlsafe(length)
    
    @staticmethod
    def constant_time_compare(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
        """Constant-time string comparison"""        if isinstance(a, str):
            a = a.encode('utf-8')
        if isinstance(b, str):
            b = b.encode('utf-8')
        
        return hmac.compare_digest(a, b)
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes, 
                               key_length: int = 32, iterations: int = 100000) -> bytes:
        """Derive encryption key from password using PBKDF2"""        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations
        )
        
        return kdf.derive(password.encode())
    
    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Generate random salt"""        return secrets.token_bytes(length)
    
    @staticmethod
    def encode_base64(data: bytes) -> str:
        """Base64 encode data"""        return base64.b64encode(data).decode('ascii')
    
    @staticmethod
    def decode_base64(data: str) -> bytes:
        """Base64 decode data"""        return base64.b64decode(data.encode('ascii'))


class EncryptionError(Exception):
    """Custom exception for encryption errors"""    pass


class HashError(Exception):
    """Custom exception for hashing errors"""    pass
