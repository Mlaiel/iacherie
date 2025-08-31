"""
Ainflue Platform Main Entry Point with Advanced Data Protection
Run the complete AI-powered content protection and monetization platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Enhanced with:
- AES-256 encryption for data at rest
- TLS 1.3 for data in transit  
- End-to-end encryption for communications
- HSM-based key management
"""

import asyncio
import sys
import os
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import the secure app first
try:
    from security.secure_middleware import get_secure_app, create_secure_app
    from security.tls_config import configure_secure_server
    from security.hsm_integration import initialize_hsm, HSMBackend
    SECURE_MODE_AVAILABLE = True
    print("✓ Secure mode available with advanced data protection")
except ImportError as e:
    print(f"⚠️  Secure mode not available: {e}")
    SECURE_MODE_AVAILABLE = False

# Fallback to original app
try:
    from api.asgi import app as original_app
    print("✓ Successfully imported api.asgi app")
    MAIN_APP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import api.asgi app: {e}")
    MAIN_APP_AVAILABLE = False

# Try to import config
try:
    import simple_config
    settings = simple_config.settings
    print("✓ Successfully imported simple_config.py")
    print(f"✓ Environment: {settings.app.environment}")
    print(f"✓ Debug mode: {settings.app.debug}")
    print(f"✓ Host: {settings.app.host}")
    print(f"✓ Port: {settings.app.port}")
except ImportError as e:
    try:
        import app_config
        settings = app_config.settings
        print("✓ Successfully imported app_config.py as fallback")
        print(f"✓ Environment: {settings.app.environment}")
        print(f"✓ Debug mode: {settings.app.debug}")
        print(f"✓ Host: {settings.app.host}")
        print(f"✓ Port: {settings.app.port}")
    except Exception as e:
        print(f"❌ Failed to import any config: {e}")
        # Create minimal fallback settings
        class MockSettings:
            class App:
                environment = "development"
                debug = True
                host = "127.0.0.1"
                port = 8000
            app = App()
        settings = MockSettings()
        print("⚠️  Using minimal fallback settings")

# Create secure configuration
def get_security_config() -> Dict[str, Any]:
    """Get security configuration based on environment."""
    config = {
        'encryption_enabled': True,
        'e2e_enabled': True,
        'hsm_enabled': settings.app.environment != 'development',  # Disable HSM in dev
        'hsm_backend': 'local',  # Use local HSM for development
        'hsm_config': {
            'storage_path': './keys'
        },
        'debug': settings.app.debug,
        'tls_enabled': settings.app.environment != 'development',
        'cert_path': './certs'
    }
    
    # Environment-specific configurations
    if settings.app.environment == 'production':
        config.update({
            'hsm_enabled': True,
            'hsm_backend': os.getenv('HSM_BACKEND', 'aws_kms'),
            'hsm_config': {
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY')
            },
            'tls_enabled': True,
            'cert_path': os.getenv('TLS_CERT_PATH', '/etc/ssl/certs'),
            'encryption_enabled': True,
            'e2e_enabled': True
        })
    elif settings.app.environment == 'staging':
        config.update({
            'hsm_enabled': True,
            'hsm_backend': 'local',
            'tls_enabled': True
        })
    
    return config

# Create the appropriate app instance
if SECURE_MODE_AVAILABLE:
    security_config = get_security_config()
    app = get_secure_app(security_config)
    print("✓ Using secure application with advanced data protection")
    print(f"  - AES-256 encryption: {'enabled' if security_config['encryption_enabled'] else 'disabled'}")
    print(f"  - TLS 1.3: {'enabled' if security_config['tls_enabled'] else 'disabled'}")
    print(f"  - End-to-end encryption: {'enabled' if security_config['e2e_enabled'] else 'disabled'}")
    print(f"  - HSM integration: {'enabled' if security_config['hsm_enabled'] else 'disabled'}")
    if security_config['hsm_enabled']:
        print(f"  - HSM backend: {security_config['hsm_backend']}")
elif MAIN_APP_AVAILABLE:
    app = original_app
    print("⚠️  Using original application without enhanced security")
else:
    print("📦 Creating minimal FastAPI app for testing")
    
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    app = FastAPI(
        title="Ainflue AI Platform",
        description="AI-Powered Content Protection & Monetization Platform",
        version="1.0.0"
    )
    
    class StatusResponse(BaseModel):
        message: str
        status: str
        environment: str
        security_level: str
    
    @app.get("/", response_model=StatusResponse)
    async def root():
        return StatusResponse(
            message="Ainflue AI Platform is running!",
            status="success",
            environment=settings.app.environment,
            security_level="basic"
        )
    
    @app.get("/health", response_model=StatusResponse)
    async def health_check():
        return StatusResponse(
            message="Platform is healthy",
            status="operational",
            environment=settings.app.environment,
            security_level="basic"
        )

# Try to import optional components
try:
    from database.schema import create_tables
    CREATE_TABLES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database schema not available: {e}")
    CREATE_TABLES_AVAILABLE = False

try:
    from core.logging import logger
    LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Core logging not available: {e}")
    import logging
    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False

import uvicorn


async def initialize_platform():
    """Initialize the platform with security components."""
    try:
        logger.info("Initializing Ainflue platform with advanced security...")
        
        # Initialize HSM if secure mode is available and enabled
        if SECURE_MODE_AVAILABLE:
            security_config = get_security_config()
            if security_config.get('hsm_enabled'):
                try:
                    hsm_backend = HSMBackend(security_config['hsm_backend'])
                    hsm_config = security_config['hsm_config']
                    hsm_manager = await initialize_hsm(hsm_backend, hsm_config)
                    
                    # Create master key if it doesn't exist
                    try:
                        master_key_id = await hsm_manager.create_master_key()
                        logger.info(f"Master encryption key initialized: {master_key_id}")
                    except Exception as e:
                        logger.warning(f"Master key creation failed (may already exist): {e}")
                    
                    logger.info("HSM key management initialized successfully")
                except Exception as e:
                    logger.error(f"HSM initialization failed: {e}")
                    if settings.app.environment == 'production':
                        raise  # Fail in production if HSM is required
        
        # Create database tables if available
        if CREATE_TABLES_AVAILABLE:
            await create_tables()
            logger.info("Database tables created successfully")
        else:
            logger.info("Database initialization skipped (not available)")
        
        logger.info("Platform initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Platform initialization failed: {str(e)}")
        raise


def main():
    """Main entry point with secure server configuration."""
    logger.info("Starting Ainflue AI Platform with Advanced Data Protection")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    try:
        # Initialize platform if needed
        if settings.app.environment in ["development", "staging"]:
            if CREATE_TABLES_AVAILABLE or SECURE_MODE_AVAILABLE:
                asyncio.run(initialize_platform())
            else:
                logger.info("Platform initialization skipped (components not available)")
        
        # Configure server based on security requirements
        if SECURE_MODE_AVAILABLE:
            security_config = get_security_config()
            
            if security_config.get('tls_enabled'):
                # Use secure server with TLS 1.3
                server_config = configure_secure_server(
                    app,
                    host=settings.app.host,
                    port=settings.app.port,
                    cert_file=security_config.get('cert_file'),
                    key_file=security_config.get('key_file')
                )
                
                logger.info("Starting secure server with TLS 1.3 encryption")
                uvicorn.run(**server_config)
            else:
                # Development mode without TLS
                logger.info("Starting development server (TLS disabled)")
                uvicorn.run(
                    app,
                    host=settings.app.host,
                    port=settings.app.port,
                    reload=False,
                    log_level="info",
                    access_log=True
                )
        else:
            # Fallback to basic server
            logger.info("Starting basic server (enhanced security not available)")
            uvicorn.run(
                "main:app",
                host=settings.app.host,
                port=settings.app.port,
                reload=False,
                log_level="info",
                access_log=True,
                workers=1
            )
        
    except KeyboardInterrupt:
        logger.info("Platform stopped by user")
    except Exception as e:
        logger.error(f"Platform startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()