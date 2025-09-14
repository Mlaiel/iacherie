"""
Vault Service for Ainflue Microservices
Secure secrets management and configuration storage

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from cryptography.fernet import Fernet
from fastapi import HTTPException
import aiofiles

logger = logging.getLogger(__name__)


class VaultService:
    """Enterprise-grade vault service for secrets management"""

    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.vault_path = os.getenv("VAULT_PATH", "/tmp/vault")
        self.secrets_cache = {}
        self.lease_duration = timedelta(hours=24)
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_path = os.getenv("VAULT_KEY_PATH", "/tmp/vault.key")
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    async def store_secret(self, path: str, secret: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store encrypted secret in vault"""
        try:
            # Encrypt the secret
            secret_data = {
                "data": secret,
                "created_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat() if ttl else None
            }
            
            encrypted_data = self.cipher_suite.encrypt(
                json.dumps(secret_data).encode('utf-8')
            )
            
            # Store to file
            full_path = os.path.join(self.vault_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            async with aiofiles.open(full_path, 'wb') as f:
                await f.write(encrypted_data)
            
            # Cache for quick access
            self.secrets_cache[path] = secret_data
            
            logger.info(f"Secret stored successfully at path: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret at {path}: {str(e)}")
            return False

    async def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt secret from vault"""
        try:
            # Check cache first
            if path in self.secrets_cache:
                secret_data = self.secrets_cache[path]
                
                # Check if expired
                if secret_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(secret_data["expires_at"])
                    if datetime.utcnow() > expires_at:
                        await self.delete_secret(path)
                        return None
                
                return secret_data["data"]
            
            # Read from file
            full_path = os.path.join(self.vault_path, path)
            
            if not os.path.exists(full_path):
                return None
            
            async with aiofiles.open(full_path, 'rb') as f:
                encrypted_data = await f.read()
            
            # Decrypt
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Check if expired
            if secret_data.get("expires_at"):
                expires_at = datetime.fromisoformat(secret_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    await self.delete_secret(path)
                    return None
            
            # Update cache
            self.secrets_cache[path] = secret_data
            
            return secret_data["data"]
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret from {path}: {str(e)}")
            return None

    async def delete_secret(self, path: str) -> bool:
        """Delete secret from vault"""
        try:
            # Remove from cache
            if path in self.secrets_cache:
                del self.secrets_cache[path]
            
            # Remove file
            full_path = os.path.join(self.vault_path, path)
            if os.path.exists(full_path):
                os.remove(full_path)
            
            logger.info(f"Secret deleted successfully from path: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret from {path}: {str(e)}")
            return False

    async def list_secrets(self, prefix: str = "") -> list:
        """List all secret paths with given prefix"""
        try:
            secrets = []
            vault_prefix = os.path.join(self.vault_path, prefix)
            
            if os.path.exists(vault_prefix):
                for root, dirs, files in os.walk(vault_prefix):
                    for file in files:
                        relative_path = os.path.relpath(
                            os.path.join(root, file), 
                            self.vault_path
                        )
                        secrets.append(relative_path)
            
            return secrets
            
        except Exception as e:
            logger.error(f"Failed to list secrets with prefix {prefix}: {str(e)}")
            return []

    async def rotate_key(self) -> bool:
        """Rotate vault encryption key"""
        try:
            # Generate new key
            new_key = Fernet.generate_key()
            new_cipher = Fernet(new_key)
            
            # Re-encrypt all secrets
            secrets = await self.list_secrets()
            
            for secret_path in secrets:
                secret_data = await self.get_secret(secret_path)
                if secret_data:
                    # Delete old
                    await self.delete_secret(secret_path)
                    
                    # Store with new key
                    old_cipher = self.cipher_suite
                    self.cipher_suite = new_cipher
                    await self.store_secret(secret_path, secret_data)
            
            # Update key file
            key_path = os.getenv("VAULT_KEY_PATH", "/tmp/vault.key")
            with open(key_path, 'wb') as key_file:
                key_file.write(new_key)
            
            self.encryption_key = new_key
            
            logger.info("Vault key rotation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate vault key: {str(e)}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check vault service health"""
        try:
            test_secret = {"test": "health_check"}
            test_path = "health/test"
            
            # Test store
            store_success = await self.store_secret(test_path, test_secret, ttl=60)
            
            # Test retrieve
            retrieved = await self.get_secret(test_path)
            retrieve_success = retrieved == test_secret
            
            # Clean up
            await self.delete_secret(test_path)
            
            return {
                "status": "healthy" if store_success and retrieve_success else "unhealthy",
                "store_test": store_success,
                "retrieve_test": retrieve_success,
                "cached_secrets": len(self.secrets_cache),
                "vault_path": self.vault_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vault health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global vault service instance
vault_service = VaultService()


async def get_secret(path: str) -> Optional[Dict[str, Any]]:
    """Get secret from vault"""
    return await vault_service.get_secret(path)


async def store_secret(path: str, secret: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    """Store secret in vault"""
    return await vault_service.store_secret(path, secret, ttl)


async def delete_secret(path: str) -> bool:
    """Delete secret from vault"""
    return await vault_service.delete_secret(path)


if __name__ == "__main__":
    async def test_vault():
        """Test vault service functionality"""
        print("Testing Vault Service...")
        
        # Test store
        test_secret = {
            "api_key": "test_key_123",
            "password": "secure_password",
            "config": {"setting1": "value1"}
        }
        
        result = await store_secret("test/api_keys", test_secret, ttl=3600)
        print(f"Store result: {result}")
        
        # Test retrieve
        retrieved = await get_secret("test/api_keys")
        print(f"Retrieved: {retrieved}")
        
        # Test health
        health = await vault_service.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_vault())