"""Secure Communication Management for Deployment Security

Provides secure communication channels, message encryption, and protocol
validation for the IA Influencer Agent platform deployment infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""import asyncio
import ssl
import json
import hmac
import hashlib
import logging
import websockets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import aiohttp
import redis.asyncio as aioredis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class SecureMessage:
    """Secure message container"""    id: str
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: datetime
    signature: str
    encryption_type: str
    ttl: Optional[int] = None


@dataclass
class ChannelConfig:
    """Secure channel configuration"""    channel_id: str
    encryption_key: bytes
    signing_key: bytes
    allowed_participants: List[str]
    message_ttl: int
    max_message_size: int
    protocol: str
    authentication_required: bool


class MessageEncryption:
    """    Advanced message encryption and signing system
    """    
    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or Fernet.generate_key()
        self._fernet = Fernet(self.master_key)
        
        # Generate RSA key pair for asymmetric encryption
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
        
        logger.info("Message encryption system initialized")
    
    def encrypt_symmetric(self, message: str, key: Optional[bytes] = None) -> str:
        """        Encrypt message using symmetric encryption
        
        Args:
            message: Message to encrypt
            key: Encryption key (uses master key if None)
            
        Returns:
            Encrypted message
        """        try:
            if key:
                fernet = Fernet(key)
                encrypted = fernet.encrypt(message.encode())
            else:
                encrypted = self._fernet.encrypt(message.encode())
            
            return encrypted.decode()
            
        except Exception as e:
            logger.error(f"Symmetric encryption failed: {e}")
            raise
    
    def decrypt_symmetric(self, encrypted_message: str, key: Optional[bytes] = None) -> str:
        """        Decrypt message using symmetric encryption
        
        Args:
            encrypted_message: Encrypted message
            key: Decryption key (uses master key if None)
            
        Returns:
            Decrypted message
        """        try:
            if key:
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted_message.encode())
            else:
                decrypted = self._fernet.decrypt(encrypted_message.encode())
            
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Symmetric decryption failed: {e}")
            raise
    
    def encrypt_asymmetric(self, message: str, public_key: Optional[Any] = None) -> bytes:
        """        Encrypt message using asymmetric encryption
        
        Args:
            message: Message to encrypt
            public_key: Public key for encryption
            
        Returns:
            Encrypted message bytes
        """        try:
            key = public_key or self._public_key
            
            encrypted = key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Asymmetric encryption failed: {e}")
            raise
    
    def decrypt_asymmetric(self, encrypted_message: bytes, private_key: Optional[Any] = None) -> str:
        """        Decrypt message using asymmetric encryption
        
        Args:
            encrypted_message: Encrypted message bytes
            private_key: Private key for decryption
            
        Returns:
            Decrypted message
        """        try:
            key = private_key or self._private_key
            
            decrypted = key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Asymmetric decryption failed: {e}")
            raise
    
    def sign_message(self, message: str, private_key: Optional[Any] = None) -> bytes:
        """        Sign message with digital signature
        
        Args:
            message: Message to sign
            private_key: Private key for signing
            
        Returns:
            Digital signature
        """        try:
            key = private_key or self._private_key
            
            signature = key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature
            
        except Exception as e:
            logger.error(f"Message signing failed: {e}")
            raise
    
    def verify_signature(
        self,
        message: str,
        signature: bytes,
        public_key: Optional[Any] = None
    ) -> bool:
        """        Verify message digital signature
        
        Args:
            message: Original message
            signature: Digital signature
            public_key: Public key for verification
            
        Returns:
            True if signature is valid
        """        try:
            key = public_key or self._public_key
            
            key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception:
            return False
    
    def create_hmac_signature(self, message: str, secret_key: bytes) -> str:
        """        Create HMAC signature for message
        
        Args:
            message: Message to sign
            secret_key: Secret key for HMAC
            
        Returns:
            HMAC signature
        """        try:
            signature = hmac.new(
                secret_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            logger.error(f"HMAC signature creation failed: {e}")
            raise
    
    def verify_hmac_signature(self, message: str, signature: str, secret_key: bytes) -> bool:
        """        Verify HMAC signature
        
        Args:
            message: Original message
            signature: HMAC signature
            secret_key: Secret key for verification
            
        Returns:
            True if signature is valid
        """        try:
            expected_signature = hmac.new(
                secret_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"HMAC verification failed: {e}")
            return False


class ProtocolValidator:
    """    Protocol validation and security enforcement
    """    
    ALLOWED_PROTOCOLS = ["https", "wss", "grpc", "amqp"]
    SECURE_CIPHER_SUITES = [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384"
    ]
    
    def __init__(self):
        self.validation_rules = {}
        logger.info("Protocol validator initialized")
    
    def register_validation_rule(
        self,
        protocol: str,
        validator: Callable[[Dict[str, Any]], bool]
    ):
        """        Register custom validation rule for protocol
        
        Args:
            protocol: Protocol name
            validator: Validation function
        """        self.validation_rules[protocol] = validator
        logger.info(f"Registered validation rule for protocol: {protocol}")
    
    def validate_tls_config(self, tls_config: Dict[str, Any]) -> Dict[str, Any]:
        """        Validate TLS configuration security
        
        Args:
            tls_config: TLS configuration
            
        Returns:
            Validation results
        """        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'security_score': 100
        }
        
        try:
            # Check minimum TLS version
            min_version = tls_config.get('min_version', '').lower()
            if min_version not in ['tlsv1.2', 'tlsv1.3']:
                results['errors'].append("Minimum TLS version must be 1.2 or 1.3")
                results['is_valid'] = False
                results['security_score'] -= 30
            
            # Check cipher suites
            cipher_suites = tls_config.get('cipher_suites', [])
            if not cipher_suites:
                results['warnings'].append("No cipher suites specified")
                results['security_score'] -= 10
            else:
                secure_ciphers = set(cipher_suites) & set(self.SECURE_CIPHER_SUITES)
                if not secure_ciphers:
                    results['warnings'].append("No secure cipher suites found")
                    results['security_score'] -= 20
            
            # Check certificate validation
            verify_mode = tls_config.get('verify_mode', '').upper()
            if verify_mode != 'CERT_REQUIRED':
                results['warnings'].append("Certificate verification should be required")
                results['security_score'] -= 15
            
            # Check client authentication
            client_auth = tls_config.get('client_auth', False)
            if not client_auth:
                results['warnings'].append("Consider enabling client authentication")
                results['security_score'] -= 5
            
            return results
            
        except Exception as e:
            logger.error(f"TLS validation failed: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'security_score': 0
            }
    
    def validate_websocket_config(self, ws_config: Dict[str, Any]) -> Dict[str, Any]:
        """        Validate WebSocket configuration
        
        Args:
            ws_config: WebSocket configuration
            
        Returns:
            Validation results
        """        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'security_score': 100
        }
        
        try:
            # Check if using secure WebSocket (WSS)
            protocol = ws_config.get('protocol', '').lower()
            if protocol != 'wss':
                results['errors'].append("Use secure WebSocket (wss://) protocol")
                results['is_valid'] = False
                results['security_score'] -= 40
            
            # Check authentication
            auth_method = ws_config.get('authentication')
            if not auth_method:
                results['warnings'].append("No authentication method specified")
                results['security_score'] -= 20
            
            # Check origin validation
            origin_validation = ws_config.get('origin_validation', False)
            if not origin_validation:
                results['warnings'].append("Enable origin validation")
                results['security_score'] -= 15
            
            # Check rate limiting
            rate_limit = ws_config.get('rate_limit')
            if not rate_limit:
                results['warnings'].append("Configure rate limiting")
                results['security_score'] -= 10
            
            return results
            
        except Exception as e:
            logger.error(f"WebSocket validation failed: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'security_score': 0
            }
    
    def validate_protocol_url(self, url: str) -> bool:
        """        Validate if URL uses secure protocol
        
        Args:
            url: URL to validate
            
        Returns:
            True if protocol is secure
        """        try:
            protocol = url.split('://')[0].lower()
            is_secure = protocol in self.ALLOWED_PROTOCOLS
            
            if not is_secure:
                logger.warning(f"Insecure protocol detected: {protocol}")
            
            return is_secure
            
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False


class SecureChannelManager:
    """    Secure communication channel management system
    """    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption: Optional[MessageEncryption] = None,
        validator: Optional[ProtocolValidator] = None
    ):
        self.redis_url = redis_url
        self.encryption = encryption or MessageEncryption()
        self.validator = validator or ProtocolValidator()
        
        # Channel configurations
        self.channels: Dict[str, ChannelConfig] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Connection pools
        self._redis_pool = None
        self._websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        logger.info("Secure channel manager initialized")
    
    async def initialize_redis_pool(self):
        """Initialize Redis connection pool"""        try:
            self._redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            raise
    
    def create_secure_channel(
        self,
        channel_id: str,
        participants: List[str],
        protocol: str = "websocket",
        message_ttl: int = 3600,
        max_message_size: int = 1024 * 1024  # 1MB
    ) -> ChannelConfig:
        """        Create secure communication channel
        
        Args:
            channel_id: Unique channel identifier
            participants: List of allowed participants
            protocol: Communication protocol
            message_ttl: Message time-to-live in seconds
            max_message_size: Maximum message size in bytes
            
        Returns:
            Channel configuration
        """        try:
            # Generate channel keys
            encryption_key = Fernet.generate_key()
            signing_key = Fernet.generate_key()
            
            config = ChannelConfig(
                channel_id=channel_id,
                encryption_key=encryption_key,
                signing_key=signing_key,
                allowed_participants=participants,
                message_ttl=message_ttl,
                max_message_size=max_message_size,
                protocol=protocol,
                authentication_required=True
            )
            
            self.channels[channel_id] = config
            logger.info(f"Created secure channel: {channel_id}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to create secure channel: {e}")
            raise
    
    async def send_secure_message(
        self,
        channel_id: str,
        sender: str,
        content: Dict[str, Any],
        recipient: Optional[str] = None
    ) -> str:
        """        Send encrypted message through secure channel
        
        Args:
            channel_id: Channel identifier
            sender: Message sender
            content: Message content
            recipient: Specific recipient (optional)
            
        Returns:
            Message ID
        """        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel not found: {channel_id}")
            
            channel = self.channels[channel_id]
            
            # Validate sender
            if sender not in channel.allowed_participants:
                raise ValueError(f"Sender not authorized: {sender}")
            
            # Create message
            message_id = hashlib.sha256(
                f"{channel_id}:{sender}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            message = SecureMessage(
                id=message_id,
                sender=sender,
                recipient=recipient or "broadcast",
                content=content,
                timestamp=datetime.utcnow(),
                signature="",
                encryption_type="symmetric",
                ttl=channel.message_ttl
            )
            
            # Serialize and encrypt message
            message_json = json.dumps(asdict(message), default=str)
            encrypted_content = self.encryption.encrypt_symmetric(
                message_json,
                channel.encryption_key
            )
            
            # Create signature
            signature = self.encryption.create_hmac_signature(
                message_json,
                channel.signing_key
            )
            
            # Store in Redis with TTL
            if self._redis_pool is None:
                await self.initialize_redis_pool()
            
            redis_client = aioredis.Redis(connection_pool=self._redis_pool)
            
            # Store encrypted message
            message_key = f"channel:{channel_id}:message:{message_id}"
            message_data = {
                'content': encrypted_content,
                'signature': signature,
                'sender': sender,
                'timestamp': message.timestamp.isoformat(),
                'recipient': message.recipient
            }
            
            await redis_client.hset(message_key, mapping=message_data)
            await redis_client.expire(message_key, channel.message_ttl)
            
            # Publish to channel subscribers
            channel_key = f"channel:{channel_id}"
            await redis_client.publish(channel_key, message_id)
            
            logger.info(f"Sent secure message: {message_id} in channel {channel_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send secure message: {e}")
            raise
    
    async def receive_secure_message(
        self,
        channel_id: str,
        message_id: str,
        recipient: str
    ) -> Optional[SecureMessage]:
        """        Receive and decrypt message from secure channel
        
        Args:
            channel_id: Channel identifier
            message_id: Message identifier
            recipient: Message recipient
            
        Returns:
            Decrypted message or None
        """        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel not found: {channel_id}")
            
            channel = self.channels[channel_id]
            
            # Validate recipient
            if recipient not in channel.allowed_participants:
                raise ValueError(f"Recipient not authorized: {recipient}")
            
            # Retrieve message from Redis
            if self._redis_pool is None:
                await self.initialize_redis_pool()
            
            redis_client = aioredis.Redis(connection_pool=self._redis_pool)
            message_key = f"channel:{channel_id}:message:{message_id}"
            
            message_data = await redis_client.hgetall(message_key)
            
            if not message_data:
                logger.warning(f"Message not found: {message_id}")
                return None
            
            # Decrypt message
            encrypted_content = message_data[b'content'].decode()
            signature = message_data[b'signature'].decode()
            
            decrypted_content = self.encryption.decrypt_symmetric(
                encrypted_content,
                channel.encryption_key
            )
            
            # Verify signature
            is_valid = self.encryption.verify_hmac_signature(
                decrypted_content,
                signature,
                channel.signing_key
            )
            
            if not is_valid:
                logger.error(f"Invalid message signature: {message_id}")
                return None
            
            # Parse message
            message_dict = json.loads(decrypted_content)
            message = SecureMessage(**message_dict)
            
            logger.info(f"Received secure message: {message_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to receive secure message: {e}")
            return None
    
    async def start_websocket_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        ssl_context: Optional[ssl.SSLContext] = None
    ):
        """        Start secure WebSocket server
        
        Args:
            host: Server host
            port: Server port
            ssl_context: SSL context for secure connections
        """        try:
            async def handle_websocket(websocket, path):
                """Handle WebSocket connection"""                try:
                    # Authenticate connection
                    auth_message = await websocket.recv()
                    auth_data = json.loads(auth_message)
                    
                    # Simple token-based authentication
                    token = auth_data.get('token')
                    if not self._validate_auth_token(token):
                        await websocket.close(code=4001, reason="Authentication failed")
                        return
                    
                    # Register connection
                    client_id = auth_data.get('client_id')
                    self._websocket_connections[client_id] = websocket
                    
                    logger.info(f"WebSocket client connected: {client_id}")
                    
                    # Handle messages
                    async for message in websocket:
                        await self._handle_websocket_message(client_id, message)
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"WebSocket client disconnected: {client_id}")
                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                finally:
                    # Cleanup connection
                    if client_id in self._websocket_connections:
                        del self._websocket_connections[client_id]
            
            # Start server
            server = await websockets.serve(
                handle_websocket,
                host,
                port,
                ssl=ssl_context
            )
            
            logger.info(f"WebSocket server started on {host}:{port}")
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    def _validate_auth_token(self, token: str) -> bool:
        """Validate authentication token"""        # Implement token validation logic
        return token is not None and len(token) > 10
    
    async def _handle_websocket_message(self, client_id: str, message: str):
        """Handle incoming WebSocket message"""        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'channel_message':
                # Handle channel message
                channel_id = data.get('channel_id')
                content = data.get('content')
                
                await self.send_secure_message(
                    channel_id=channel_id,
                    sender=client_id,
                    content=content
                )
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket message: {e}")
    
    async def cleanup_expired_messages(self):
        """Cleanup expired messages from Redis"""        try:
            if self._redis_pool is None:
                await self.initialize_redis_pool()
            
            redis_client = aioredis.Redis(connection_pool=self._redis_pool)
            
            # Find expired message keys
            pattern = "channel:*:message:*"
            keys = await redis_client.keys(pattern)
            
            expired_count = 0
            for key in keys:
                ttl = await redis_client.ttl(key)
                if ttl == -2:  # Key expired
                    await redis_client.delete(key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired messages")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired messages: {e}")
    
    async def get_channel_statistics(self, channel_id: str) -> Dict[str, Any]:
        """        Get channel statistics
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            Channel statistics
        """        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel not found: {channel_id}")
            
            if self._redis_pool is None:
                await self.initialize_redis_pool()
            
            redis_client = aioredis.Redis(connection_pool=self._redis_pool)
            
            # Count messages in channel
            pattern = f"channel:{channel_id}:message:*"
            message_keys = await redis_client.keys(pattern)
            
            # Get channel info
            channel = self.channels[channel_id]
            
            statistics = {
                'channel_id': channel_id,
                'total_messages': len(message_keys),
                'participants': len(channel.allowed_participants),
                'protocol': channel.protocol,
                'created_at': datetime.utcnow().isoformat(),
                'message_ttl': channel.message_ttl,
                'max_message_size': channel.max_message_size
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get channel statistics: {e}")
            return {}
