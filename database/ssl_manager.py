"""Database SSL/TLS Security Configuration Manager
=================================================

Production-ready SSL/TLS configuration for secure database connections
with certificate management and security validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import ssl
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
try:
    import asyncpg
except ImportError:
    asyncpg = None
import subprocess
import tempfile
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SSLMode(Enum):
    """SSL connection modes"""
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"

class CertificateType(Enum):
    """Certificate types"""
    SERVER = "server"
    CLIENT = "client"
    CA = "ca"

@dataclass
class SSLConfig:
    """SSL/TLS configuration for database connections"""
    ssl_mode: SSLMode = SSLMode.REQUIRE
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    ssl_ca_file: Optional[str] = None
    ssl_crl_file: Optional[str] = None
    ssl_cipher_suites: List[str] = field(default_factory=lambda: [
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES256-SHA384',
        'ECDHE-RSA-AES128-SHA256'
    ])
    min_protocol_version: str = "TLSv1.2"
    max_protocol_version: str = "TLSv1.3"
    verify_hostname: bool = True
    certificate_validity_days: int = 365
    require_client_cert: bool = False

@dataclass
class CertificateInfo:
    """Certificate information and metadata"""
    path: str
    cert_type: CertificateType
    subject: str
    issuer: str
    valid_from: datetime
    valid_until: datetime
    fingerprint: str
    is_expired: bool
    expires_soon: bool  # Within 30 days

class DatabaseSSLManager:
    """Comprehensive SSL/TLS manager for database connections"""
    
    def __init__(self, config: SSLConfig, cert_base_path: str = "/etc/ssl/ainflue"):
        self.config = config
        self.cert_base_path = Path(cert_base_path)
        self.cert_base_path.mkdir(parents=True, exist_ok=True)
        
        # Certificate paths
        self.ca_cert_path = self.cert_base_path / "ca-cert.pem"
        self.server_cert_path = self.cert_base_path / "server-cert.pem"
        self.server_key_path = self.cert_base_path / "server-key.pem"
        self.client_cert_path = self.cert_base_path / "client-cert.pem"
        self.client_key_path = self.cert_base_path / "client-key.pem"
        
    async def setup_ssl_infrastructure(self) -> Dict[str, Any]:
        """Setup complete SSL infrastructure for production"""
        try:
            results = {}
            
            # 1. Generate CA certificate if not exists
            if not self.ca_cert_path.exists():
                ca_result = await self._generate_ca_certificate()
                results["ca_certificate"] = ca_result
            else:
                results["ca_certificate"] = {"status": "existing", "path": str(self.ca_cert_path)}
            
            # 2. Generate server certificate
            if not self.server_cert_path.exists():
                server_result = await self._generate_server_certificate()
                results["server_certificate"] = server_result
            else:
                results["server_certificate"] = {"status": "existing", "path": str(self.server_cert_path)}
            
            # 3. Generate client certificate if required
            if self.config.require_client_cert and not self.client_cert_path.exists():
                client_result = await self._generate_client_certificate()
                results["client_certificate"] = client_result
            else:
                results["client_certificate"] = {"status": "not_required"}
            
            # 4. Configure PostgreSQL SSL settings
            pg_config_result = await self._configure_postgresql_ssl()
            results["postgresql_config"] = pg_config_result
            
            # 5. Create secure connection strings
            connection_strings = self._create_secure_connection_strings()
            results["connection_strings"] = connection_strings
            
            # 6. Validate SSL setup
            validation_result = await self._validate_ssl_setup()
            results["validation"] = validation_result
            
            logger.info("SSL infrastructure setup completed successfully")
            return {
                "success": True,
                "results": results,
                "ssl_mode": self.config.ssl_mode.value,
                "setup_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SSL infrastructure setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ssl_mode": self.config.ssl_mode.value
            }
    
    async def _generate_ca_certificate(self) -> Dict[str, Any]:
        """Generate Certificate Authority certificate"""
        try:
            logger.info("Generating CA certificate")
            
            # Generate private key for CA
            ca_key_path = self.cert_base_path / "ca-key.pem"
            
            # OpenSSL commands for CA generation
            commands = [
                # Generate CA private key
                [
                    "openssl", "genpkey", "-algorithm", "RSA", 
                    "-out", str(ca_key_path), "-pkcs8", "-aes256",
                    "-pass", "pass:ainflue_ca_2025"
                ],
                # Generate CA certificate
                [
                    "openssl", "req", "-new", "-x509", 
                    "-key", str(ca_key_path), 
                    "-out", str(self.ca_cert_path),
                    "-days", str(self.config.certificate_validity_days),
                    "-passin", "pass:ainflue_ca_2025",
                    "-subj", "/C=DE/ST=Berlin/L=Berlin/O=Ainflue/OU=Database/CN=Ainflue-CA"
                ]
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Command failed: {' '.join(cmd)}\nError: {result.stderr}")
            
            # Set secure permissions
            os.chmod(ca_key_path, 0o600)
            os.chmod(self.ca_cert_path, 0o644)
            
            return {
                "status": "generated",
                "ca_cert_path": str(self.ca_cert_path),
                "ca_key_path": str(ca_key_path),
                "validity_days": self.config.certificate_validity_days
            }
            
        except Exception as e:
            logger.error(f"CA certificate generation failed: {e}")
            raise
    
    async def _generate_server_certificate(self) -> Dict[str, Any]:
        """Generate server certificate signed by CA"""
        try:
            logger.info("Generating server certificate")
            
            # Generate server private key
            server_key_cmd = [
                "openssl", "genpkey", "-algorithm", "RSA",
                "-out", str(self.server_key_path)
            ]
            subprocess.run(server_key_cmd, check=True, capture_output=True)
            
            # Generate certificate signing request
            csr_path = self.cert_base_path / "server.csr"
            csr_cmd = [
                "openssl", "req", "-new",
                "-key", str(self.server_key_path),
                "-out", str(csr_path),
                "-subj", "/C=DE/ST=Berlin/L=Berlin/O=Ainflue/OU=Database/CN=ainflue-db"
            ]
            subprocess.run(csr_cmd, check=True, capture_output=True)
            
            # Sign certificate with CA
            ca_key_path = self.cert_base_path / "ca-key.pem"
            sign_cmd = [
                "openssl", "x509", "-req",
                "-in", str(csr_path),
                "-CA", str(self.ca_cert_path),
                "-CAkey", str(ca_key_path),
                "-CAcreateserial",
                "-out", str(self.server_cert_path),
                "-days", str(self.config.certificate_validity_days),
                "-passin", "pass:ainflue_ca_2025"
            ]
            subprocess.run(sign_cmd, check=True, capture_output=True)
            
            # Set secure permissions
            os.chmod(self.server_key_path, 0o600)
            os.chmod(self.server_cert_path, 0o644)
            
            # Clean up CSR
            csr_path.unlink()
            
            return {
                "status": "generated",
                "server_cert_path": str(self.server_cert_path),
                "server_key_path": str(self.server_key_path),
                "validity_days": self.config.certificate_validity_days
            }
            
        except Exception as e:
            logger.error(f"Server certificate generation failed: {e}")
            raise
    
    async def _generate_client_certificate(self) -> Dict[str, Any]:
        """Generate client certificate for mutual TLS"""
        try:
            logger.info("Generating client certificate")
            
            # Generate client private key
            client_key_cmd = [
                "openssl", "genpkey", "-algorithm", "RSA",
                "-out", str(self.client_key_path)
            ]
            subprocess.run(client_key_cmd, check=True, capture_output=True)
            
            # Generate certificate signing request
            csr_path = self.cert_base_path / "client.csr"
            csr_cmd = [
                "openssl", "req", "-new",
                "-key", str(self.client_key_path),
                "-out", str(csr_path),
                "-subj", "/C=DE/ST=Berlin/L=Berlin/O=Ainflue/OU=Application/CN=ainflue-client"
            ]
            subprocess.run(csr_cmd, check=True, capture_output=True)
            
            # Sign certificate with CA
            ca_key_path = self.cert_base_path / "ca-key.pem"
            sign_cmd = [
                "openssl", "x509", "-req",
                "-in", str(csr_path),
                "-CA", str(self.ca_cert_path),
                "-CAkey", str(ca_key_path),
                "-CAcreateserial",
                "-out", str(self.client_cert_path),
                "-days", str(self.config.certificate_validity_days),
                "-passin", "pass:ainflue_ca_2025"
            ]
            subprocess.run(sign_cmd, check=True, capture_output=True)
            
            # Set secure permissions
            os.chmod(self.client_key_path, 0o600)
            os.chmod(self.client_cert_path, 0o644)
            
            # Clean up CSR
            csr_path.unlink()
            
            return {
                "status": "generated",
                "client_cert_path": str(self.client_cert_path),
                "client_key_path": str(self.client_key_path),
                "validity_days": self.config.certificate_validity_days
            }
            
        except Exception as e:
            logger.error(f"Client certificate generation failed: {e}")
            raise
    
    async def _configure_postgresql_ssl(self) -> Dict[str, Any]:
        """Configure PostgreSQL SSL settings"""
        try:
            # Update PostgreSQL configuration
            ssl_config = f"""
# SSL Configuration - Generated by Ainflue SSL Manager
ssl = on
ssl_cert_file = '{self.server_cert_path}'
ssl_key_file = '{self.server_key_path}'
ssl_ca_file = '{self.ca_cert_path}'

# SSL Security Settings
ssl_prefer_server_ciphers = on
ssl_ciphers = '{":".join(self.config.ssl_cipher_suites)}'
ssl_min_protocol_version = '{self.config.min_protocol_version}'
ssl_max_protocol_version = '{self.config.max_protocol_version}'

# Client Certificate Settings
{'ssl_ca_file = "' + str(self.ca_cert_path) + '"' if self.config.require_client_cert else ''}

# Connection Security
password_encryption = scram-sha-256
"""
            
            # Write SSL configuration to file
            ssl_config_path = self.cert_base_path / "postgresql_ssl.conf"
            with open(ssl_config_path, 'w') as f:
                f.write(ssl_config)
            
            # Update pg_hba.conf for SSL connections
            hba_config = f"""
# SSL-required connections - Generated by Ainflue SSL Manager
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Require SSL for all connections
hostssl all             all             0.0.0.0/0               scram-sha-256
hostssl all             all             ::0/0                   scram-sha-256

# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Deny non-SSL connections
hostnossl all           all             0.0.0.0/0               reject
hostnossl all           all             ::0/0                   reject
"""
            
            hba_config_path = self.cert_base_path / "pg_hba_ssl.conf"
            with open(hba_config_path, 'w') as f:
                f.write(hba_config)
            
            return {
                "status": "configured",
                "ssl_config_path": str(ssl_config_path),
                "hba_config_path": str(hba_config_path),
                "ssl_mode": self.config.ssl_mode.value,
                "require_client_cert": self.config.require_client_cert
            }
            
        except Exception as e:
            logger.error(f"PostgreSQL SSL configuration failed: {e}")
            raise
    
    def _create_secure_connection_strings(self) -> Dict[str, str]:
        """Create secure connection strings for different scenarios"""
        base_params = {
            "host": "localhost",
            "port": "5432",
            "dbname": "ainflue_prod",
            "sslmode": self.config.ssl_mode.value,
        }
        
        # Add SSL certificate parameters
        if self.config.ssl_mode in [SSLMode.VERIFY_CA, SSLMode.VERIFY_FULL]:
            base_params["sslrootcert"] = str(self.ca_cert_path)
        
        if self.config.require_client_cert:
            base_params["sslcert"] = str(self.client_cert_path)
            base_params["sslkey"] = str(self.client_key_path)
        
        # Connection strings for different users/scenarios
        connection_strings = {}
        
        # Application connection
        app_params = base_params.copy()
        app_params["user"] = "ainflue_app"
        connection_strings["application"] = self._format_connection_string(app_params)
        
        # Read-only connection
        readonly_params = base_params.copy()
        readonly_params["user"] = "ainflue_readonly"
        connection_strings["readonly"] = self._format_connection_string(readonly_params)
        
        # Admin connection
        admin_params = base_params.copy()
        admin_params["user"] = "ainflue_admin"
        connection_strings["admin"] = self._format_connection_string(admin_params)
        
        # Backup connection
        backup_params = base_params.copy()
        backup_params["user"] = "ainflue_backup"
        connection_strings["backup"] = self._format_connection_string(backup_params)
        
        return connection_strings
    
    def _format_connection_string(self, params: Dict[str, str]) -> str:
        """Format connection parameters into connection string"""
        param_list = [f"{key}={value}" for key, value in params.items()]
        return " ".join(param_list)
    
    async def _validate_ssl_setup(self) -> Dict[str, Any]:
        """Validate SSL setup and certificate chain"""
        try:
            validation_results = {}
            
            # 1. Verify certificate files exist and are readable
            cert_checks = {
                "ca_certificate": self.ca_cert_path,
                "server_certificate": self.server_cert_path,
                "server_key": self.server_key_path
            }
            
            if self.config.require_client_cert:
                cert_checks["client_certificate"] = self.client_cert_path
                cert_checks["client_key"] = self.client_key_path
            
            for cert_name, cert_path in cert_checks.items():
                validation_results[cert_name] = {
                    "exists": cert_path.exists(),
                    "readable": cert_path.exists() and os.access(cert_path, os.R_OK),
                    "path": str(cert_path)
                }
            
            # 2. Verify certificate validity and chain
            if self.server_cert_path.exists() and self.ca_cert_path.exists():
                cert_info = await self._get_certificate_info(str(self.server_cert_path))
                validation_results["server_cert_info"] = cert_info
                
                # Verify certificate chain
                chain_valid = await self._verify_certificate_chain()
                validation_results["certificate_chain_valid"] = chain_valid
            
            # 3. Test SSL connection
            try:
                ssl_test_result = await self._test_ssl_connection()
                validation_results["ssl_connection_test"] = ssl_test_result
            except Exception as e:
                validation_results["ssl_connection_test"] = {
                    "success": False,
                    "error": str(e)
                }
            
            return {
                "validation_passed": all(
                    result.get("exists", False) and result.get("readable", False)
                    for result in validation_results.values()
                    if isinstance(result, dict) and "exists" in result
                ),
                "details": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SSL validation failed: {e}")
            return {
                "validation_passed": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_certificate_info(self, cert_path: str) -> Dict[str, Any]:
        """Get detailed certificate information"""
        try:
            # Use openssl to get certificate info
            cmd = ["openssl", "x509", "-in", cert_path, "-text", "-noout"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse certificate dates
            date_cmd = ["openssl", "x509", "-in", cert_path, "-dates", "-noout"]
            date_result = subprocess.run(date_cmd, capture_output=True, text=True, check=True)
            
            # Extract validity dates
            date_lines = date_result.stdout.strip().split('\n')
            valid_from = None
            valid_until = None
            
            for line in date_lines:
                if line.startswith("notBefore="):
                    valid_from = line.split("=", 1)[1]
                elif line.startswith("notAfter="):
                    valid_until = line.split("=", 1)[1]
            
            # Get fingerprint
            fingerprint_cmd = ["openssl", "x509", "-in", cert_path, "-fingerprint", "-sha256", "-noout"]
            fingerprint_result = subprocess.run(fingerprint_cmd, capture_output=True, text=True, check=True)
            fingerprint = fingerprint_result.stdout.strip().split("=", 1)[1] if "=" in fingerprint_result.stdout else ""
            
            return {
                "path": cert_path,
                "valid_from": valid_from,
                "valid_until": valid_until,
                "fingerprint": fingerprint,
                "details": result.stdout
            }
            
        except Exception as e:
            logger.error(f"Failed to get certificate info: {e}")
            return {"error": str(e)}
    
    async def _verify_certificate_chain(self) -> bool:
        """Verify certificate chain validity"""
        try:
            # Verify server certificate against CA
            cmd = [
                "openssl", "verify",
                "-CAfile", str(self.ca_cert_path),
                str(self.server_cert_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and "OK" in result.stdout
            
        except Exception as e:
            logger.error(f"Certificate chain verification failed: {e}")
            return False
    
    async def _test_ssl_connection(self) -> Dict[str, Any]:
        """Test SSL connection to database"""
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.check_hostname = self.config.verify_hostname
            
            if self.config.ssl_mode in [SSLMode.VERIFY_CA, SSLMode.VERIFY_FULL]:
                ssl_context.load_verify_locations(str(self.ca_cert_path))
            
            if self.config.require_client_cert:
                ssl_context.load_cert_chain(str(self.client_cert_path), str(self.client_key_path))
            
            # Test connection
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                database="ainflue_prod",
                user="ainflue_app",
                ssl=ssl_context,
                timeout=10
            )
            
            # Test query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            return {
                "success": True,
                "ssl_mode": self.config.ssl_mode.value,
                "query_result": result,
                "message": "SSL connection test successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ssl_mode": self.config.ssl_mode.value
            }
    
    async def get_certificate_status(self) -> Dict[str, Any]:
        """Get status of all certificates"""
        try:
            certificates = {}
            
            cert_files = {
                "ca": self.ca_cert_path,
                "server": self.server_cert_path,
                "client": self.client_cert_path if self.config.require_client_cert else None
            }
            
            for cert_name, cert_path in cert_files.items():
                if cert_path and cert_path.exists():
                    cert_info = await self._get_certificate_info(str(cert_path))
                    certificates[cert_name] = cert_info
                else:
                    certificates[cert_name] = {"status": "missing" if cert_path else "not_required"}
            
            return {
                "certificates": certificates,
                "ssl_mode": self.config.ssl_mode.value,
                "require_client_cert": self.config.require_client_cert,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get certificate status: {e}")
            return {"error": str(e)}
    
    async def rotate_certificates(self) -> Dict[str, Any]:
        """Rotate all certificates (for security best practices)"""
        try:
            logger.info("Starting certificate rotation")
            
            # Backup existing certificates
            backup_dir = self.cert_base_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            
            cert_files = [self.ca_cert_path, self.server_cert_path, self.server_key_path]
            if self.config.require_client_cert:
                cert_files.extend([self.client_cert_path, self.client_key_path])
            
            # Backup existing certificates
            for cert_file in cert_files:
                if cert_file.exists():
                    backup_path = backup_dir / cert_file.name
                    cert_file.rename(backup_path)
            
            # Generate new certificates
            setup_result = await self.setup_ssl_infrastructure()
            
            if setup_result["success"]:
                return {
                    "success": True,
                    "backup_location": str(backup_dir),
                    "rotation_timestamp": datetime.utcnow().isoformat(),
                    "setup_results": setup_result["results"]
                }
            else:
                # Restore backup if generation failed
                for cert_file in backup_dir.iterdir():
                    restore_path = self.cert_base_path / cert_file.name
                    cert_file.rename(restore_path)
                
                return {
                    "success": False,
                    "error": "Certificate generation failed, restored backup",
                    "setup_error": setup_result.get("error")
                }
                
        except Exception as e:
            logger.error(f"Certificate rotation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }