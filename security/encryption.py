"""
Security and Encryption Module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced AES-256 encryption implementation for data protection.
"""

import os
import base64
import secrets
from typing import Dict, Optional, Tuple, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import logging

logger = logging.getLogger(__name__)


class AES256Encryption:
    """
    Advanced AES-256 encryption implementation with GCM mode for authenticated encryption.
    Provides data protection for repositories and content storage.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize AES-256 encryption with master key.
        
        Args:
            master_key: 32-byte master key. If None, generates a new one.
        """
        if master_key is None:
            self.master_key = secrets.token_bytes(32)  # 256 bits
        else:
            if len(master_key) != 32:
                raise ValueError("Master key must be exactly 32 bytes (256 bits)")
            self.master_key = master_key
    
    def generate_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Generate encryption key from password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation. If None, generates a new one.
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,  # OWASP recommended minimum
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def derive_key(self, context: str) -> bytes:
        """
        Derive a specific key from master key using HKDF.
        
        Args:
            context: Context string for key derivation
            
        Returns:
            Derived 32-byte key
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=context.encode('utf-8'),
            backend=default_backend()
        )
        return hkdf.derive(self.master_key)
    
    def encrypt(self, plaintext: bytes, key: Optional[bytes] = None, 
                associated_data: Optional[bytes] = None) -> Dict[str, bytes]:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key. If None, uses master key.
            associated_data: Additional authenticated data (AAD)
            
        Returns:
            Dictionary containing encrypted data, nonce, and tag
        """
        try:
            if key is None:
                key = self.master_key
            
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96 bits for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Add associated data if provided
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # Encrypt data
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            return {
                'ciphertext': ciphertext,
                'nonce': nonce,
                'tag': encryptor.tag,
                'associated_data': associated_data
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: Dict[str, bytes], key: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            encrypted_data: Dictionary containing ciphertext, nonce, tag, and optional AAD
            key: Decryption key. If None, uses master key.
            
        Returns:
            Decrypted plaintext
        """
        try:
            if key is None:
                key = self.master_key
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(encrypted_data['nonce'], encrypted_data['tag']),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Add associated data if present
            if encrypted_data.get('associated_data'):
                decryptor.authenticate_additional_data(encrypted_data['associated_data'])
            
            # Decrypt data
            plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: str, 
                     key: Optional[bytes] = None, chunk_size: int = 64 * 1024) -> Dict[str, Any]:
        """
        Encrypt a file using AES-256-GCM with chunked processing.
        
        Args:
            file_path: Path to input file
            output_path: Path for encrypted output
            key: Encryption key. If None, uses master key.
            chunk_size: Size of chunks for processing large files
            
        Returns:
            Dictionary with encryption metadata
        """
        try:
            if key is None:
                key = self.master_key
            
            # Generate file-specific nonce
            nonce = secrets.token_bytes(12)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Read and encrypt file in chunks
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Write nonce to beginning of file
                outfile.write(nonce)
                
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    encrypted_chunk = encryptor.update(chunk)
                    outfile.write(encrypted_chunk)
                
                # Finalize and write tag
                encryptor.finalize()
                outfile.write(encryptor.tag)
            
            # Return metadata
            file_size = os.path.getsize(file_path)
            encrypted_size = os.path.getsize(output_path)
            
            return {
                'original_size': file_size,
                'encrypted_size': encrypted_size,
                'nonce': nonce,
                'tag': encryptor.tag,
                'algorithm': 'AES-256-GCM',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def decrypt_file(self, encrypted_path: str, output_path: str, 
                     key: Optional[bytes] = None, chunk_size: int = 64 * 1024) -> Dict[str, Any]:
        """
        Decrypt a file encrypted with encrypt_file.
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Path for decrypted output
            key: Decryption key. If None, uses master key.
            chunk_size: Size of chunks for processing large files
            
        Returns:
            Dictionary with decryption results
        """
        try:
            if key is None:
                key = self.master_key
            
            with open(encrypted_path, 'rb') as infile:
                # Read nonce from beginning of file
                nonce = infile.read(12)
                
                # Read tag from end of file
                infile.seek(-16, 2)  # GCM tag is 16 bytes
                tag = infile.read(16)
                
                # Reset to data start
                infile.seek(12)
                
                # Create cipher
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(nonce, tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                
                # Decrypt file in chunks
                with open(output_path, 'wb') as outfile:
                    while True:
                        # Calculate remaining data (excluding tag)
                        current_pos = infile.tell()
                        infile.seek(0, 2)  # Go to end
                        end_pos = infile.tell() - 16  # Exclude tag
                        infile.seek(current_pos)  # Return to current position
                        
                        remaining = end_pos - current_pos
                        if remaining <= 0:
                            break
                        
                        read_size = min(chunk_size, remaining)
                        chunk = infile.read(read_size)
                        if not chunk:
                            break
                        
                        decrypted_chunk = decryptor.update(chunk)
                        outfile.write(decrypted_chunk)
                
                # Finalize decryption
                decryptor.finalize()
            
            return {
                'success': True,
                'decrypted_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            return {'success': False, 'error': str(e)}


class ContentEncryption:
    """
    Content encryption utilities for different content types.
    Enhanced implementation with AES-256 encryption.
    """
    
    def __init__(self):
        self.aes_cipher = AES256Encryption()
    
    def encrypt_content(self, content: bytes, key: Optional[str] = None, 
                       content_type: str = "binary") -> Dict[str, Any]:
        """
        Encrypt content data with metadata preservation.
        
        Args:
            content: Content bytes to encrypt
            key: Optional encryption key (string)
            content_type: Type of content for context
            
        Returns:
            Dictionary with encrypted content and metadata
        """
        try:
            # Derive key if password provided, otherwise use master key
            if key:
                encryption_key, salt = self.aes_cipher.generate_key(key)
            else:
                encryption_key = self.aes_cipher.derive_key(f"content_{content_type}")
                salt = None
            
            # Add content type as associated data for integrity
            associated_data = f"content_type:{content_type}".encode('utf-8')
            
            # Encrypt content
            encrypted_data = self.aes_cipher.encrypt(
                content, 
                encryption_key, 
                associated_data
            )
            
            # Encode for storage/transmission
            result = {
                'encrypted_content': base64.b64encode(encrypted_data['ciphertext']).decode('utf-8'),
                'nonce': base64.b64encode(encrypted_data['nonce']).decode('utf-8'),
                'tag': base64.b64encode(encrypted_data['tag']).decode('utf-8'),
                'content_type': content_type,
                'algorithm': 'AES-256-GCM',
                'version': '1.0'
            }
            
            if salt:
                result['salt'] = base64.b64encode(salt).decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"Content encryption failed: {str(e)}")
            raise
    
    def decrypt_content(self, encrypted_content: Dict[str, Any], 
                       key: Optional[str] = None) -> bytes:
        """
        Decrypt content data.
        
        Args:
            encrypted_content: Dictionary with encrypted content and metadata
            key: Optional decryption key (string)
            
        Returns:
            Decrypted content bytes
        """
        try:
            content_type = encrypted_content.get('content_type', 'binary')
            
            # Derive key if password provided, otherwise use master key
            if key and 'salt' in encrypted_content:
                salt = base64.b64decode(encrypted_content['salt'])
                decryption_key, _ = self.aes_cipher.generate_key(key, salt)
            else:
                decryption_key = self.aes_cipher.derive_key(f"content_{content_type}")
            
            # Reconstruct encrypted data structure
            encrypted_data = {
                'ciphertext': base64.b64decode(encrypted_content['encrypted_content']),
                'nonce': base64.b64decode(encrypted_content['nonce']),
                'tag': base64.b64decode(encrypted_content['tag']),
                'associated_data': f"content_type:{content_type}".encode('utf-8')
            }
            
            # Decrypt content
            plaintext = self.aes_cipher.decrypt(encrypted_data, decryption_key)
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Content decryption failed: {str(e)}")
            raise


class DatabaseEncryption:
    """
    Database field encryption for sensitive data at rest.
    """
    
    def __init__(self):
        self.aes_cipher = AES256Encryption()
    
    def encrypt_field(self, value: str, field_name: str, table_name: str) -> str:
        """
        Encrypt a database field value.
        
        Args:
            value: Field value to encrypt
            field_name: Name of the database field
            table_name: Name of the database table
            
        Returns:
            Base64 encoded encrypted value
        """
        try:
            # Derive field-specific key
            context = f"db_{table_name}_{field_name}"
            field_key = self.aes_cipher.derive_key(context)
            
            # Encrypt value
            encrypted_data = self.aes_cipher.encrypt(
                value.encode('utf-8'),
                field_key,
                f"{table_name}.{field_name}".encode('utf-8')
            )
            
            # Create storage format
            storage_data = {
                'c': base64.b64encode(encrypted_data['ciphertext']).decode('utf-8'),
                'n': base64.b64encode(encrypted_data['nonce']).decode('utf-8'),
                't': base64.b64encode(encrypted_data['tag']).decode('utf-8'),
                'v': '1'  # Version
            }
            
            # Encode as JSON-like string for database storage
            import json
            return base64.b64encode(json.dumps(storage_data).encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Database field encryption failed: {str(e)}")
            raise
    
    def decrypt_field(self, encrypted_value: str, field_name: str, table_name: str) -> str:
        """
        Decrypt a database field value.
        
        Args:
            encrypted_value: Base64 encoded encrypted value
            field_name: Name of the database field
            table_name: Name of the database table
            
        Returns:
            Decrypted field value
        """
        try:
            # Decode storage format
            import json
            storage_data = json.loads(base64.b64decode(encrypted_value).decode('utf-8'))
            
            # Derive field-specific key
            context = f"db_{table_name}_{field_name}"
            field_key = self.aes_cipher.derive_key(context)
            
            # Reconstruct encrypted data
            encrypted_data = {
                'ciphertext': base64.b64decode(storage_data['c']),
                'nonce': base64.b64decode(storage_data['n']),
                'tag': base64.b64decode(storage_data['t']),
                'associated_data': f"{table_name}.{field_name}".encode('utf-8')
            }
            
            # Decrypt value
            plaintext = self.aes_cipher.decrypt(encrypted_data, field_key)
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Database field decryption failed: {str(e)}")
            raise


# Global instances for easy access
content_encryption = ContentEncryption()
database_encryption = DatabaseEncryption()
aes256_encryption = AES256Encryption()


def get_content_encryption() -> ContentEncryption:
    """Get content encryption instance."""
    return content_encryption


def get_database_encryption() -> DatabaseEncryption:
    """Get database encryption instance."""
    return database_encryption


def get_aes256_encryption() -> AES256Encryption:
    """Get AES-256 encryption instance."""
    return aes256_encryption