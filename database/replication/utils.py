"""Replication Utilities - IA Influencer Agent Platform

Common utilities and helper functions for database replication operations.
Provides data validation, transformation, encryption, and networking utilities
for the content creator platform's replication infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import hashlib
import hmac
import base64
import json
import gzip
import zlib
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import ipaddress
import socket
import ssl
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets


@dataclass
class ValidationResult:
    """Data validation result"""    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class NetworkInfo:
    """Network connection information"""    host: str
    port: int
    is_reachable: bool
    latency_ms: float
    ssl_valid: bool = False
    ssl_expiry: Optional[datetime] = None


class ReplicationUtils:
    """    Comprehensive utilities for database replication operations.
    
    Provides data validation, encryption, compression, networking,
    and other common utilities for the IA Influencer Agent platform's
    replication infrastructure.
    """    
    def __init__(self, config):
        """Initialize replication utilities"""        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationUtils")
        
        # Encryption configuration
        self.encryption_key = self._derive_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Network configuration
        self.connection_timeout = config.get("timeout", 30)
        self.ssl_context = self._create_ssl_context()
        
        # Data validation rules
        self.validation_rules = {
            "users": {
                "required_fields": ["id", "email", "created_at"],
                "field_types": {
                    "id": (int, str),
                    "email": str,
                    "created_at": (str, datetime)
                }
            },
            "content_fingerprints": {
                "required_fields": ["id", "user_id", "content_type", "fingerprint_hash"],
                "field_types": {
                    "id": (int, str),
                    "user_id": (int, str),
                    "content_type": str,
                    "fingerprint_hash": str
                }
            },
            "revenue_tracking": {
                "required_fields": ["id", "user_id", "revenue_amount", "currency"],
                "field_types": {
                    "id": (int, str),
                    "user_id": (int, str),
                    "revenue_amount": (int, float),
                    "currency": str
                }
            }
        }
        
        self.logger.info("ReplicationUtils initialized")
    
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from configuration"""        try:
            # Get master key from config or environment
            master_key = self.config.get_security_config().get("master_key", "default_key_change_me")
            salt = b"replication_salt_ia_influencer"
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            return key
            
        except Exception as e:
            self.logger.error(f"Error deriving encryption key: {e}")
            # Fallback to generated key
            return Fernet.generate_key()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure connections"""        context = ssl.create_default_context()
        
        # Configure based on security settings
        security_config = self.config.get_security_config()
        
        if not security_config.get("certificate_validation", True):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        # Set TLS version
        tls_version = security_config.get("tls_version", "1.3")
        if tls_version == "1.3":
            context.minimum_version = ssl.TLSVersion.TLSv1_3
        elif tls_version == "1.2":
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        return context
    
    # Data Validation Methods
    
    def validate_record_data(self, table_name: str, data: Dict[str, Any]) -> ValidationResult:
        """        Validate record data against schema rules.
        
        Args:
            table_name: Name of the table/collection
            data: Record data to validate
            
        Returns:
            ValidationResult: Validation result with errors and warnings
        """        errors = []
        warnings = []
        metadata = {}
        
        try:
            # Get validation rules for table
            rules = self.validation_rules.get(table_name, {})
            
            # Check required fields
            required_fields = rules.get("required_fields", [])
            for field in required_fields:
                if field not in data or data[field] is None:
                    errors.append(f"Missing required field: {field}")
            
            # Check field types
            field_types = rules.get("field_types", {})
            for field, expected_types in field_types.items():
                if field in data and data[field] is not None:
                    if not isinstance(data[field], expected_types):
                        errors.append(f"Invalid type for field {field}: expected {expected_types}, got {type(data[field])}")
            
            # Check data size
            data_size = len(json.dumps(data, default=str))
            if data_size > 1024 * 1024:  # 1MB limit
                warnings.append(f"Large record size: {data_size} bytes")
            
            # Validate specific fields
            if "email" in data:
                if not self._validate_email(data["email"]):
                    errors.append(f"Invalid email format: {data['email']}")
            
            if "content_type" in data:
                valid_content_types = ["audio", "video", "image", "text"]
                if data["content_type"] not in valid_content_types:
                    errors.append(f"Invalid content type: {data['content_type']}")
            
            if "currency" in data:
                valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
                if data["currency"] not in valid_currencies:
                    warnings.append(f"Uncommon currency: {data['currency']}")
            
            metadata["record_size"] = data_size
            metadata["field_count"] = len(data)
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""        try:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False
    
    def validate_replication_record(self, record: Dict[str, Any]) -> ValidationResult:
        """        Validate replication record structure.
        
        Args:
            record: Replication record to validate
            
        Returns:
            ValidationResult: Validation result
        """        errors = []
        warnings = []
        metadata = {}
        
        try:
            required_fields = ["id", "database_type", "table_name", "operation", "data", "timestamp", "checksum"]
            
            for field in required_fields:
                if field not in record:
                    errors.append(f"Missing required replication field: {field}")
            
            # Validate checksum
            if "data" in record and "checksum" in record:
                calculated_checksum = self.calculate_data_checksum(record["data"])
                if calculated_checksum != record["checksum"]:
                    errors.append("Checksum validation failed")
            
            # Validate timestamp
            if "timestamp" in record:
                try:
                    if isinstance(record["timestamp"], str):
                        datetime.fromisoformat(record["timestamp"])
                    elif not isinstance(record["timestamp"], datetime):
                        errors.append("Invalid timestamp format")
                except Exception:
                    errors.append("Invalid timestamp format")
            
            # Validate operation
            valid_operations = ["insert", "update", "delete", "bulk_sync"]
            if "operation" in record and record["operation"] not in valid_operations:
                errors.append(f"Invalid operation: {record['operation']}")
            
            metadata["has_data"] = "data" in record and record["data"] is not None
            metadata["data_size"] = len(json.dumps(record.get("data", {}), default=str))
            
        except Exception as e:
            errors.append(f"Record validation error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )
    
    # Data Transformation Methods
    
    def normalize_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """        Normalize data types for cross-database compatibility.
        
        Args:
            data: Data to normalize
            
        Returns:
            Dict: Normalized data
        """        try:
            normalized = {}
            
            for key, value in data.items():
                if isinstance(value, datetime):
                    # Convert datetime to ISO string
                    normalized[key] = value.isoformat()
                elif isinstance(value, bytes):
                    # Convert bytes to base64 string
                    normalized[key] = base64.b64encode(value).decode()
                elif isinstance(value, (set, tuple)):
                    # Convert sets and tuples to lists
                    normalized[key] = list(value)
                elif isinstance(value, dict):
                    # Recursively normalize nested dictionaries
                    normalized[key] = self.normalize_data_types(value)
                elif value is None:
                    # Keep None values
                    normalized[key] = None
                else:
                    # Keep other types as-is
                    normalized[key] = value
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing data types: {e}")
            return data
    
    def transform_for_database(self, data: Dict[str, Any], database_type: str) -> Dict[str, Any]:
        """        Transform data for specific database type.
        
        Args:
            data: Data to transform
            database_type: Target database type
            
        Returns:
            Dict: Transformed data
        """        try:
            transformed = data.copy()
            
            if database_type == "mongodb":
                # MongoDB-specific transformations
                if "id" in transformed and not isinstance(transformed["id"], str):
                    transformed["_id"] = str(transformed["id"])
                    del transformed["id"]
                
            elif database_type == "elasticsearch":
                # Elasticsearch-specific transformations
                if "timestamp" in transformed:
                    # Ensure timestamp is in correct format
                    if isinstance(transformed["timestamp"], str):
                        try:
                            datetime.fromisoformat(transformed["timestamp"])
                        except Exception:
                            transformed["timestamp"] = datetime.utcnow().isoformat()
                
            elif database_type == "redis":
                # Redis-specific transformations
                # Convert all values to strings for Redis
                for key, value in transformed.items():
                    if isinstance(value, (dict, list)):
                        transformed[key] = json.dumps(value)
                    elif not isinstance(value, str):
                        transformed[key] = str(value)
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming data for {database_type}: {e}")
            return data
    
    # Encryption and Security Methods
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """        Encrypt sensitive fields in data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Dict: Data with encrypted sensitive fields
        """        try:
            encrypted_data = data.copy()
            sensitive_fields = ["password", "api_key", "token", "credit_card", "ssn", "phone"]
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    encrypted_value = self.cipher.encrypt(str(encrypted_data[field]).encode())
                    encrypted_data[field] = base64.b64encode(encrypted_value).decode()
                    encrypted_data[f"{field}_encrypted"] = True
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting sensitive data: {e}")
            return data
    
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """        Decrypt sensitive fields in data.
        
        Args:
            data: Data to decrypt
            
        Returns:
            Dict: Data with decrypted sensitive fields
        """        try:
            decrypted_data = data.copy()
            
            for key, value in data.items():
                if key.endswith("_encrypted") and value:
                    field_name = key[:-10]  # Remove "_encrypted"
                    if field_name in decrypted_data:
                        encrypted_value = base64.b64decode(decrypted_data[field_name])
                        decrypted_value = self.cipher.decrypt(encrypted_value).decode()
                        decrypted_data[field_name] = decrypted_value
                        del decrypted_data[key]  # Remove encryption flag
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error decrypting sensitive data: {e}")
            return data
    
    def calculate_data_checksum(self, data: Dict[str, Any]) -> str:
        """        Calculate checksum for data integrity verification.
        
        Args:
            data: Data to calculate checksum for
            
        Returns:
            str: SHA-256 checksum
        """        try:
            # Normalize and sort data for consistent checksum
            normalized_data = self.normalize_data_types(data)
            data_string = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))
            
            # Calculate SHA-256 hash
            checksum = hashlib.sha256(data_string.encode()).hexdigest()
            return checksum
            
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def verify_data_integrity(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """        Verify data integrity using checksum.
        
        Args:
            data: Data to verify
            expected_checksum: Expected checksum
            
        Returns:
            bool: True if data integrity is valid
        """        try:
            calculated_checksum = self.calculate_data_checksum(data)
            return calculated_checksum == expected_checksum
            
        except Exception as e:
            self.logger.error(f"Error verifying data integrity: {e}")
            return False
    
    # Compression Methods
    
    def compress_data(self, data: Union[str, bytes, Dict[str, Any]]) -> bytes:
        """        Compress data for efficient transmission.
        
        Args:
            data: Data to compress
            
        Returns:
            bytes: Compressed data
        """        try:
            if isinstance(data, dict):
                data_str = json.dumps(data, separators=(',', ':'))
            elif isinstance(data, str):
                data_str = data
            else:
                data_str = str(data)
            
            compressed = gzip.compress(data_str.encode())
            
            self.logger.debug(f"Compressed {len(data_str)} bytes to {len(compressed)} bytes")
            return compressed
            
        except Exception as e:
            self.logger.error(f"Error compressing data: {e}")
            # Return original data as bytes if compression fails
            if isinstance(data, bytes):
                return data
            else:
                return str(data).encode()
    
    def decompress_data(self, compressed_data: bytes) -> str:
        """        Decompress data.
        
        Args:
            compressed_data: Compressed data
            
        Returns:
            str: Decompressed data
        """        try:
            decompressed = gzip.decompress(compressed_data)
            return decompressed.decode()
            
        except Exception as e:
            self.logger.error(f"Error decompressing data: {e}")
            # Return as string if decompression fails
            return compressed_data.decode(errors='ignore')
    
    # Network Utilities
    
    async def check_network_connectivity(self, host: str, port: int, timeout: int = None) -> NetworkInfo:
        """        Check network connectivity to a host and port.
        
        Args:
            host: Target host
            port: Target port
            timeout: Connection timeout
            
        Returns:
            NetworkInfo: Network connectivity information
        """        timeout = timeout or self.connection_timeout
        start_time = datetime.utcnow()
        
        try:
            # Test TCP connectivity
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
            
            writer.close()
            await writer.wait_closed()
            
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Test SSL if applicable
            ssl_valid = False
            ssl_expiry = None
            
            if port in [443, 5432, 6379, 27017]:  # Common SSL ports
                try:
                    ssl_info = await self._check_ssl_certificate(host, port)
                    ssl_valid = ssl_info["valid"]
                    ssl_expiry = ssl_info["expiry"]
                except Exception:
                    pass
            
            return NetworkInfo(
                host=host,
                port=port,
                is_reachable=True,
                latency_ms=latency,
                ssl_valid=ssl_valid,
                ssl_expiry=ssl_expiry
            )
            
        except Exception as e:
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return NetworkInfo(
                host=host,
                port=port,
                is_reachable=False,
                latency_ms=latency
            )
    
    async def _check_ssl_certificate(self, host: str, port: int) -> Dict[str, Any]:
        """Check SSL certificate validity"""        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiry date
                    expiry_str = cert.get('notAfter')
                    expiry_date = None
                    if expiry_str:
                        expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                    
                    return {
                        "valid": True,
                        "expiry": expiry_date,
                        "subject": cert.get('subject'),
                        "issuer": cert.get('issuer')
                    }
                    
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "expiry": None
            }
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """        Validate IP address format.
        
        Args:
            ip_address: IP address to validate
            
        Returns:
            bool: True if valid IP address
        """        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    def is_private_ip(self, ip_address: str) -> bool:
        """        Check if IP address is private.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            bool: True if private IP
        """        try:
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private
        except ValueError:
            return False
    
    def check_ip_whitelist(self, ip_address: str) -> bool:
        """        Check if IP address is in whitelist.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            bool: True if IP is whitelisted
        """        try:
            security_config = self.config.get_security_config()
            allowed_networks = security_config.get("allowed_networks", [])
            
            if not allowed_networks:
                return True  # No restrictions
            
            ip = ipaddress.ip_address(ip_address)
            
            for network_str in allowed_networks:
                try:
                    network = ipaddress.ip_network(network_str, strict=False)
                    if ip in network:
                        return True
                except ValueError:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking IP whitelist: {e}")
            return False
    
    # Utility Methods
    
    def generate_unique_id(self) -> str:
        """        Generate unique identifier.
        
        Returns:
            str: Unique identifier
        """        return f"{int(datetime.utcnow().timestamp())}_{secrets.token_hex(8)}"
    
    def parse_database_url(self, url: str) -> Dict[str, Any]:
        """        Parse database URL into components.
        
        Args:
            url: Database URL
            
        Returns:
            Dict: URL components
        """        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(url)
            
            return {
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip('/') if parsed.path else '',
                "username": parsed.username,
                "password": parsed.password,
                "query_params": dict(q.split('=') for q in parsed.query.split('&') if '=' in q)
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing database URL: {e}")
            return {}
    
    def format_bytes(self, bytes_value: int) -> str:
        """        Format bytes value to human-readable string.
        
        Args:
            bytes_value: Bytes value
            
        Returns:
            str: Formatted string
        """        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def format_duration(self, seconds: float) -> str:
        """        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            str: Formatted duration
        """        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
    
    def sanitize_table_name(self, table_name: str) -> str:
        """        Sanitize table name for safe database operations.
        
        Args:
            table_name: Table name to sanitize
            
        Returns:
            str: Sanitized table name
        """        try:
            import re
            # Remove any non-alphanumeric characters except underscores
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
            
            # Ensure it starts with a letter or underscore
            if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
                sanitized = f"t_{sanitized}"
            
            # Limit length
            if len(sanitized) > 64:
                sanitized = sanitized[:64]
            
            return sanitized or "unknown_table"
            
        except Exception as e:
            self.logger.error(f"Error sanitizing table name: {e}")
            return "unknown_table"
    
    def create_backup_filename(self, database_type: str, timestamp: datetime = None) -> str:
        """        Create standardized backup filename.
        
        Args:
            database_type: Type of database
            timestamp: Backup timestamp
            
        Returns:
            str: Backup filename
        """        timestamp = timestamp or datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"backup_{database_type}_{timestamp_str}.sql"
    
    def log_performance_metric(self, operation: str, duration: float, metadata: Dict[str, Any] = None) -> None:
        """        Log performance metric.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
            metadata: Additional metadata
        """        try:
            metric_data = {
                "operation": operation,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.logger.info(f"Performance metric: {json.dumps(metric_data)}")
            
        except Exception as e:
            self.logger.error(f"Error logging performance metric: {e}")
    
    async def retry_with_backoff(
        self,
        func: callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """        Retry function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Backoff multiplier
            
        Returns:
            Function result
        """        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()
                    
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
        
        # All retries failed
        raise last_exception or Exception("All retries failed")
