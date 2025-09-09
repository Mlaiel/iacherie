"""Encryption Utilities
Enterprise-grade encryption and cryptographic operations for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import base64
import hashlib
import hmac
import secrets
from typing import Union, Optional, Tuple, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionUtilities:
    """
    Enterprise-grade encryption utilities with symmetric/asymmetric encryption,
    key derivation, digital signatures, and secure random generation.
    """
    
    def __init__(self):
        self.backend = default_backend()
        logger.info("EncryptionUtilities initialized")
    
    # Symmetric Encryption (Fernet - AES 128)
    
    def generate_key(self) -> bytes:
        """Generate a new Fernet encryption key"""
        return Fernet.generate_key()
    
    def encrypt_symmetric(self, data: Union[str, bytes], key: bytes) -> bytes:
        """
        Encrypt data using symmetric encryption (Fernet)
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Encrypted data
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            f = Fernet(key)
            encrypted_data = f.encrypt(data)
            
            logger.debug("Data encrypted successfully with symmetric encryption")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Symmetric encryption failed: {e}")
            raise
    
    def decrypt_symmetric(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data using symmetric encryption (Fernet)
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            
        Returns:
            Decrypted data
        """
        try:
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data)
            
            logger.debug("Data decrypted successfully with symmetric encryption")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Symmetric decryption failed: {e}")
            raise
    
    # Advanced Symmetric Encryption (AES)
    
    def encrypt_aes_gcm(self, data: Union[str, bytes], key: bytes, 
                       associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data using AES-GCM (authenticated encryption)
        
        Args:
            data: Data to encrypt
            key: 32-byte encryption key
            associated_data: Optional associated data for authentication
            
        Returns:
            Tuple of (nonce, ciphertext, tag)
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Generate a random 96-bit IV
            nonce = os.urandom(12)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Add associated data if provided
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # Encrypt and finalize
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            logger.debug("Data encrypted successfully with AES-GCM")
            return nonce, ciphertext, encryptor.tag
            
        except Exception as e:
            logger.error(f"AES-GCM encryption failed: {e}")
            raise
    
    def decrypt_aes_gcm(self, nonce: bytes, ciphertext: bytes, tag: bytes, 
                       key: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-GCM
        
        Args:
            nonce: Nonce used for encryption
            ciphertext: Encrypted data
            tag: Authentication tag
            key: Decryption key
            associated_data: Associated data used during encryption
            
        Returns:
            Decrypted data
        """
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Add associated data if provided
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            # Decrypt and finalize
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            logger.debug("Data decrypted successfully with AES-GCM")
            return plaintext
            
        except Exception as e:
            logger.error(f"AES-GCM decryption failed: {e}")
            raise
    
    # Asymmetric Encryption (RSA)
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair
        
        Args:
            key_size: Key size in bits (2048, 3072, or 4096)
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=self.backend
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys to PEM format
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.info(f"RSA key pair generated successfully ({key_size} bits)")
            return private_pem, public_pem
            
        except Exception as e:
            logger.error(f"RSA key generation failed: {e}")
            raise
    
    def encrypt_rsa(self, data: Union[str, bytes], public_key_pem: bytes) -> bytes:
        """
        Encrypt data using RSA public key
        
        Args:
            data: Data to encrypt (max 190 bytes for 2048-bit key)
            public_key_pem: RSA public key in PEM format
            
        Returns:
            Encrypted data
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=self.backend
            )
            
            # Encrypt data
            encrypted_data = public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug("Data encrypted successfully with RSA")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"RSA encryption failed: {e}")
            raise
    
    def decrypt_rsa(self, encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """
        Decrypt data using RSA private key
        
        Args:
            encrypted_data: RSA encrypted data
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Decrypted data
        """
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Decrypt data
            decrypted_data = private_key.decrypt(
                encrypted_data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug("Data decrypted successfully with RSA")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            raise
    
    # Key Derivation Functions
    
    def derive_key_pbkdf2(self, password: Union[str, bytes], salt: bytes, 
                         iterations: int = 100000, key_length: int = 32) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Random salt
            iterations: Number of iterations
            key_length: Length of derived key in bytes
            
        Returns:
            Derived key
        """
        try:
            if isinstance(password, str):
                password = password.encode('utf-8')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=key_length,
                salt=salt,
                iterations=iterations,
                backend=self.backend
            )
            
            key = kdf.derive(password)
            
            logger.debug(f"Key derived successfully using PBKDF2 ({iterations} iterations)")
            return key
            
        except Exception as e:
            logger.error(f"PBKDF2 key derivation failed: {e}")
            raise
    
    def derive_key_scrypt(self, password: Union[str, bytes], salt: bytes,
                         n: int = 2**14, r: int = 8, p: int = 1, 
                         key_length: int = 32) -> bytes:
        """
        Derive encryption key from password using Scrypt
        
        Args:
            password: Password to derive key from
            salt: Random salt
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            key_length: Length of derived key in bytes
            
        Returns:
            Derived key
        """
        try:
            if isinstance(password, str):
                password = password.encode('utf-8')
            
            kdf = Scrypt(
                algorithm=hashes.SHA256(),
                length=key_length,
                salt=salt,
                n=n,
                r=r,
                p=p,
                backend=self.backend
            )
            
            key = kdf.derive(password)
            
            logger.debug(f"Key derived successfully using Scrypt (n={n}, r={r}, p={p})")
            return key
            
        except Exception as e:
            logger.error(f"Scrypt key derivation failed: {e}")
            raise
    
    # Hashing Functions
    
    def hash_sha256(self, data: Union[str, bytes]) -> str:
        """Generate SHA-256 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_object = hashlib.sha256(data)
        return hash_object.hexdigest()
    
    def hash_sha512(self, data: Union[str, bytes]) -> str:
        """Generate SHA-512 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_object = hashlib.sha512(data)
        return hash_object.hexdigest()
    
    def hash_blake2b(self, data: Union[str, bytes], key: Optional[bytes] = None) -> str:
        """Generate BLAKE2b hash (optionally keyed)"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_object = hashlib.blake2b(data, key=key)
        return hash_object.hexdigest()
    
    # HMAC Functions
    
    def hmac_sha256(self, data: Union[str, bytes], key: bytes) -> str:
        """Generate HMAC-SHA256"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        mac = hmac.new(key, data, hashlib.sha256)
        return mac.hexdigest()
    
    def verify_hmac_sha256(self, data: Union[str, bytes], key: bytes, expected_mac: str) -> bool:
        """Verify HMAC-SHA256"""
        calculated_mac = self.hmac_sha256(data, key)
        return hmac.compare_digest(calculated_mac, expected_mac)
    
    # Random Generation
    
    def generate_salt(self, length: int = 32) -> bytes:
        """Generate cryptographically secure random salt"""
        return os.urandom(length)
    
    def generate_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def generate_password(self, length: int = 16, include_symbols: bool = True) -> str:
        """Generate cryptographically secure random password"""
        import string
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    # Base64 Encoding/Decoding
    
    def base64_encode(self, data: Union[str, bytes]) -> str:
        """Encode data to base64"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return base64.b64encode(data).decode('ascii')
    
    def base64_decode(self, encoded_data: str) -> bytes:
        """Decode base64 data"""
        return base64.b64decode(encoded_data)
    
    def base64url_encode(self, data: Union[str, bytes]) -> str:
        """Encode data to base64url (URL-safe)"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')
    
    def base64url_decode(self, encoded_data: str) -> bytes:
        """Decode base64url data"""
        # Add padding if needed
        padding = '=' * (4 - len(encoded_data) % 4)
        return base64.urlsafe_b64decode(encoded_data + padding)
    
    # Digital Signatures
    
    def sign_rsa(self, data: Union[str, bytes], private_key_pem: bytes) -> bytes:
        """Create RSA digital signature"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Create signature
            signature = private_key.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug("Data signed successfully with RSA")
            return signature
            
        except Exception as e:
            logger.error(f"RSA signing failed: {e}")
            raise
    
    def verify_rsa_signature(self, data: Union[str, bytes], signature: bytes, 
                           public_key_pem: bytes) -> bool:
        """Verify RSA digital signature"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=self.backend
            )
            
            # Verify signature
            public_key.verify(
                signature,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug("RSA signature verified successfully")
            return True
            
        except Exception as e:
            logger.debug(f"RSA signature verification failed: {e}")
            return False


# Password hashing utilities using modern algorithms

class PasswordUtilities:
    """Secure password hashing and verification utilities"""
    
    def __init__(self):
        self.encryption_utils = EncryptionUtilities()
    
    def hash_password(self, password: str, method: str = "scrypt") -> str:
        """
        Hash password using specified method
        
        Args:
            password: Plain text password
            method: Hashing method ('scrypt', 'pbkdf2', 'argon2')
            
        Returns:
            Hashed password with salt and parameters
        """
        salt = self.encryption_utils.generate_salt(32)
        
        if method == "scrypt":
            key = self.encryption_utils.derive_key_scrypt(password, salt)
            # Format: scrypt$n$r$p$salt$hash
            encoded_salt = base64.b64encode(salt).decode('ascii')
            encoded_hash = base64.b64encode(key).decode('ascii')
            return f"scrypt$16384$8$1${encoded_salt}${encoded_hash}"
        
        elif method == "pbkdf2":
            key = self.encryption_utils.derive_key_pbkdf2(password, salt, iterations=100000)
            # Format: pbkdf2$iterations$salt$hash
            encoded_salt = base64.b64encode(salt).decode('ascii')
            encoded_hash = base64.b64encode(key).decode('ascii')
            return f"pbkdf2$100000${encoded_salt}${encoded_hash}"
        
        else:
            raise ValueError(f"Unsupported hashing method: {method}")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed_password: Stored hash with parameters
            
        Returns:
            True if password matches
        """
        try:
            parts = hashed_password.split('$')
            method = parts[0]
            
            if method == "scrypt":
                n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
                salt = base64.b64decode(parts[4])
                stored_hash = base64.b64decode(parts[5])
                
                key = self.encryption_utils.derive_key_scrypt(password, salt, n=n, r=r, p=p)
                return hmac.compare_digest(key, stored_hash)
            
            elif method == "pbkdf2":
                iterations = int(parts[1])
                salt = base64.b64decode(parts[2])
                stored_hash = base64.b64decode(parts[3])
                
                key = self.encryption_utils.derive_key_pbkdf2(password, salt, iterations=iterations)
                return hmac.compare_digest(key, stored_hash)
            
            else:
                return False
                
        except (IndexError, ValueError):
            return False


# Global instances
_global_encryption_utils: Optional[EncryptionUtilities] = None
_global_password_utils: Optional[PasswordUtilities] = None


def get_encryption_utils() -> EncryptionUtilities:
    """Get global encryption utilities instance"""
    global _global_encryption_utils
    if _global_encryption_utils is None:
        _global_encryption_utils = EncryptionUtilities()
    return _global_encryption_utils


def get_password_utils() -> PasswordUtilities:
    """Get global password utilities instance"""
    global _global_password_utils
    if _global_password_utils is None:
        _global_password_utils = PasswordUtilities()
    return _global_password_utils


# Convenience functions
def encrypt_data(data: Union[str, bytes], key: bytes) -> bytes:
    """Quick symmetric encryption"""
    return get_encryption_utils().encrypt_symmetric(data, key)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Quick symmetric decryption"""
    return get_encryption_utils().decrypt_symmetric(encrypted_data, key)


def hash_password(password: str) -> str:
    """Quick password hashing"""
    return get_password_utils().hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Quick password verification"""
    return get_password_utils().verify_password(password, hashed_password)