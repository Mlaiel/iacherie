# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Comprehensive Tests for Configuration Management

Industrial-grade testing for configuration handling, validation,
environment management, and dynamic configuration updates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import os
import tempfile
import json
import yaml
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

from ai.ai_agents.config import (
    ConfigManager,
    AgentConfig,
    SystemConfig,
    DatabaseConfig,
    SecurityConfig,
    MonitoringConfig,
    ConfigValidator,
    ConfigLoader,
    ConfigWatcher,
    Environment
)

logger = logging.getLogger(__name__)


class TestAgentConfig:
    """Test agent configuration management"""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration"""
        config = AgentConfig(
            agent_id="test_agent_001",
            agent_type="ContentCreatorAgent",
            max_concurrent_tasks=5,
            timeout_seconds=300,
            retry_attempts=3,
            capabilities=[
                "content_generation",
                "image_creation",
                "video_editing"
            ],
            custom_settings={
                "quality_preset": "high",
                "output_format": "mp4",
                "resolution": "1080p"
            }
        )
        
        assert config.agent_id == "test_agent_001"
        assert config.agent_type == "ContentCreatorAgent"
        assert config.max_concurrent_tasks == 5
        assert config.timeout_seconds == 300
        assert config.retry_attempts == 3
        assert "content_generation" in config.capabilities
        assert config.custom_settings["quality_preset"] == "high"
    
    def test_agent_config_validation(self):
        """Test agent configuration validation"""
        # Valid configuration
        valid_config = AgentConfig(
            agent_id="valid_agent",
            agent_type="TestAgent",
            max_concurrent_tasks=10,
            timeout_seconds=600
        )
        
        validation_result = valid_config.validate()
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Invalid configuration - negative values
        with pytest.raises(ValueError):
            AgentConfig(
                agent_id="invalid_agent",
                agent_type="TestAgent",
                max_concurrent_tasks=-1,  # Invalid negative value
                timeout_seconds=300
            )
    
    def test_agent_config_serialization(self):
        """Test agent configuration serialization"""
        config = AgentConfig(
            agent_id="serialization_test",
            agent_type="ContentCreatorAgent",
            max_concurrent_tasks=8,
            timeout_seconds=450,
            capabilities=["content_generation", "optimization"],
            custom_settings={"test_setting": "test_value"}
        )
        
        # Serialize to dictionary
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["agent_id"] == "serialization_test"
        assert config_dict["max_concurrent_tasks"] == 8
        
        # Deserialize from dictionary
        restored_config = AgentConfig.from_dict(config_dict)
        assert restored_config.agent_id == config.agent_id
        assert restored_config.agent_type == config.agent_type
        assert restored_config.capabilities == config.capabilities
        
        # Serialize to JSON
        config_json = config.to_json()
        assert isinstance(config_json, str)
        
        # Deserialize from JSON
        json_restored = AgentConfig.from_json(config_json)
        assert json_restored.agent_id == config.agent_id
    
    def test_agent_config_merging(self):
        """Test merging agent configurations"""
        base_config = AgentConfig(
            agent_id="base_agent",
            agent_type="BaseAgent",
            max_concurrent_tasks=5,
            timeout_seconds=300,
            capabilities=["base_capability"],
            custom_settings={"base_setting": "base_value"}
        )
        
        override_config = AgentConfig(
            agent_id="base_agent",  # Same agent
            agent_type="BaseAgent",
            max_concurrent_tasks=10,  # Override
            retry_attempts=5,  # New setting
            capabilities=["base_capability", "new_capability"],  # Extended
            custom_settings={"base_setting": "new_value", "new_setting": "new_value"}
        )
        
        merged_config = base_config.merge(override_config)
        
        assert merged_config.max_concurrent_tasks == 10  # Overridden
        assert merged_config.retry_attempts == 5  # Added
        assert "new_capability" in merged_config.capabilities  # Extended
        assert merged_config.custom_settings["base_setting"] == "new_value"  # Overridden
        assert merged_config.custom_settings["new_setting"] == "new_value"  # Added
    
    def test_agent_config_environment_variables(self):
        """Test loading configuration from environment variables"""
        # Set environment variables
        os.environ["AGENT_MAX_CONCURRENT_TASKS"] = "15"
        os.environ["AGENT_TIMEOUT_SECONDS"] = "900"
        os.environ["AGENT_RETRY_ATTEMPTS"] = "5"
        
        try:
            config = AgentConfig.from_environment(
                agent_id="env_agent",
                agent_type="EnvironmentAgent"
            )
            
            assert config.max_concurrent_tasks == 15
            assert config.timeout_seconds == 900
            assert config.retry_attempts == 5
            
        finally:
            # Clean up environment variables
            for key in ["AGENT_MAX_CONCURRENT_TASKS", "AGENT_TIMEOUT_SECONDS", "AGENT_RETRY_ATTEMPTS"]:
                if key in os.environ:
                    del os.environ[key]


class TestSystemConfig:
    """Test system configuration management"""
    
    def test_system_config_creation(self):
        """Test creating system configuration"""
        config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            debug_mode=True,
            log_level="DEBUG",
            max_agents=100,
            max_concurrent_workflows=50,
            database_config=DatabaseConfig(
                host="localhost",
                port=5432,
                database="test_db",
                username="test_user",
                password="test_password"
            ),
            security_config=SecurityConfig(
                encryption_enabled=True,
                jwt_secret="test_secret",
                session_timeout=3600
            ),
            monitoring_config=MonitoringConfig(
                metrics_enabled=True,
                health_check_interval=30,
                performance_monitoring=True
            )
        )
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug_mode is True
        assert config.max_agents == 100
        assert config.database_config.host == "localhost"
        assert config.security_config.encryption_enabled is True
        assert config.monitoring_config.metrics_enabled is True
    
    def test_system_config_validation(self):
        """Test system configuration validation"""
        # Valid configuration
        valid_config = SystemConfig(
            environment=Environment.PRODUCTION,
            max_agents=200,
            max_concurrent_workflows=100
        )
        
        validation_result = valid_config.validate()
        assert validation_result["valid"] is True
        
        # Invalid configuration
        invalid_config = SystemConfig(
            environment=Environment.PRODUCTION,
            max_agents=0,  # Invalid
            max_concurrent_workflows=-1  # Invalid
        )
        
        validation_result = invalid_config.validate()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_environment_specific_configs(self):
        """Test environment-specific configuration loading"""
        # Development environment
        dev_config = SystemConfig.for_environment(Environment.DEVELOPMENT)
        assert dev_config.environment == Environment.DEVELOPMENT
        assert dev_config.debug_mode is True
        assert dev_config.log_level == "DEBUG"
        
        # Production environment
        prod_config = SystemConfig.for_environment(Environment.PRODUCTION)
        assert prod_config.environment == Environment.PRODUCTION
        assert prod_config.debug_mode is False
        assert prod_config.log_level == "INFO"
        
        # Testing environment
        test_config = SystemConfig.for_environment(Environment.TESTING)
        assert test_config.environment == Environment.TESTING
        assert test_config.log_level == "DEBUG"
    
    def test_config_inheritance(self):
        """Test configuration inheritance and overrides"""
        base_config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            max_agents=50,
            debug_mode=True
        )
        
        # Create production config inheriting from base
        prod_overrides = {
            "environment": Environment.PRODUCTION,
            "debug_mode": False,
            "log_level": "ERROR",
            "max_agents": 500  # Increased for production
        }
        
        prod_config = base_config.inherit(prod_overrides)
        
        assert prod_config.environment == Environment.PRODUCTION
        assert prod_config.debug_mode is False
        assert prod_config.log_level == "ERROR"
        assert prod_config.max_agents == 500


class TestDatabaseConfig:
    """Test database configuration management"""
    
    def test_database_config_creation(self):
        """Test creating database configuration"""
        config = DatabaseConfig(
            host="db.example.com",
            port=5432,
            database="production_db",
            username="db_user",
            password="secure_password",
            ssl_enabled=True,
            connection_pool_size=20,
            connection_timeout=30,
            query_timeout=60
        )
        
        assert config.host == "db.example.com"
        assert config.port == 5432
        assert config.database == "production_db"
        assert config.ssl_enabled is True
        assert config.connection_pool_size == 20
    
    def test_database_connection_string(self):
        """Test database connection string generation"""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        connection_string = config.get_connection_string()
        expected = "postgresql://test_user:test_pass@localhost:5432/test_db"
        assert connection_string == expected
        
        # Test with SSL
        config.ssl_enabled = True
        ssl_connection_string = config.get_connection_string()
        assert "sslmode=require" in ssl_connection_string
    
    def test_database_config_security(self):
        """Test database configuration security features"""
        config = DatabaseConfig(
            host="secure-db.example.com",
            port=5432,
            database="secure_db",
            username="secure_user",
            password="very_secure_password",
            ssl_enabled=True,
            encrypt_credentials=True
        )
        
        # Test credential encryption
        if config.encrypt_credentials:
            encrypted_config = config.encrypt_sensitive_data()
            assert encrypted_config.password != "very_secure_password"
            
            # Test decryption
            decrypted_config = encrypted_config.decrypt_sensitive_data()
            assert decrypted_config.password == "very_secure_password"
    
    def test_database_config_validation(self):
        """Test database configuration validation"""
        # Valid configuration
        valid_config = DatabaseConfig(
            host="valid-host",
            port=5432,
            database="valid_db",
            username="valid_user",
            password="valid_password"
        )
        
        validation_result = valid_config.validate()
        assert validation_result["valid"] is True
        
        # Invalid configuration - missing required fields
        with pytest.raises(ValueError):
            DatabaseConfig(
                host="",  # Empty host
                port=5432,
                database="test_db",
                username="user",
                password="pass"
            )
        
        # Invalid port
        with pytest.raises(ValueError):
            DatabaseConfig(
                host="localhost",
                port=70000,  # Invalid port
                database="test_db",
                username="user",
                password="pass"
            )


class TestSecurityConfig:
    """Test security configuration management"""
    
    def test_security_config_creation(self):
        """Test creating security configuration"""
        config = SecurityConfig(
            encryption_enabled=True,
            jwt_secret="super_secret_jwt_key",
            session_timeout=7200,
            password_policy={
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_symbols": True
            },
            api_rate_limit=1000,
            cors_origins=["https://example.com", "https://app.example.com"],
            csrf_protection=True
        )
        
        assert config.encryption_enabled is True
        assert config.jwt_secret == "super_secret_jwt_key"
        assert config.session_timeout == 7200
        assert config.password_policy["min_length"] == 12
        assert config.api_rate_limit == 1000
        assert "https://example.com" in config.cors_origins
        assert config.csrf_protection is True
    
    def test_security_config_validation(self):
        """Test security configuration validation"""
        # Valid configuration
        valid_config = SecurityConfig(
            encryption_enabled=True,
            jwt_secret="secure_secret_key_with_sufficient_length",
            session_timeout=3600
        )
        
        validation_result = valid_config.validate()
        assert validation_result["valid"] is True
        
        # Invalid configuration - weak JWT secret
        invalid_config = SecurityConfig(
            encryption_enabled=True,
            jwt_secret="weak",  # Too short
            session_timeout=3600
        )
        
        validation_result = invalid_config.validate()
        assert validation_result["valid"] is False
        assert any("jwt_secret" in error.lower() for error in validation_result["errors"])
    
    def test_password_policy_validation(self):
        """Test password policy validation"""
        config = SecurityConfig(
            password_policy={
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_symbols": False
            }
        )
        
        # Valid passwords
        valid_passwords = [
            "MyPassword123",
            "SecurePass456",
            "ComplexPassword789"
        ]
        
        for password in valid_passwords:
            assert config.validate_password(password) is True
        
        # Invalid passwords
        invalid_passwords = [
            "short",  # Too short
            "nouppercasehere123",  # No uppercase
            "NOLOWERCASEHERE123",  # No lowercase
            "NoNumbersHere",  # No numbers
        ]
        
        for password in invalid_passwords:
            assert config.validate_password(password) is False
    
    def test_jwt_token_operations(self):
        """Test JWT token operations"""
        config = SecurityConfig(
            jwt_secret="test_jwt_secret_key_for_testing_purposes",
            session_timeout=3600
        )
        
        # Generate token
        payload = {"user_id": 123, "role": "admin"}
        token = config.generate_jwt_token(payload)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Validate token
        decoded_payload = config.validate_jwt_token(token)
        assert decoded_payload is not None
        assert decoded_payload["user_id"] == 123
        assert decoded_payload["role"] == "admin"
        
        # Test expired token
        import time
        config.session_timeout = 1  # 1 second
        expired_token = config.generate_jwt_token(payload)
        time.sleep(2)  # Wait for expiration
        
        expired_payload = config.validate_jwt_token(expired_token)
        assert expired_payload is None  # Should be None for expired token


class TestConfigManager:
    """Test configuration manager functionality"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for configuration files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    async def config_manager(self, temp_config_dir) -> ConfigManager:
        """Create configuration manager for testing"""
        manager = ConfigManager(config_directory=temp_config_dir)
        await manager.initialize()
        
        yield manager
        
        await manager.shutdown()
    
    async def test_config_manager_initialization(self, temp_config_dir):
        """Test configuration manager initialization"""
        manager = ConfigManager(config_directory=temp_config_dir)
        
        assert not manager.initialized
        
        await manager.initialize()
        assert manager.initialized
        
        await manager.shutdown()
        assert not manager.initialized
    
    async def test_config_loading_and_saving(self, config_manager, temp_config_dir):
        """Test loading and saving configurations"""
        # Create test configuration
        test_config = SystemConfig(
            environment=Environment.TESTING,
            max_agents=25,
            debug_mode=True
        )
        
        # Save configuration
        save_result = await config_manager.save_config("test_system", test_config)
        assert save_result["success"] is True
        
        # Verify file was created
        config_file = temp_config_dir / "test_system.json"
        assert config_file.exists()
        
        # Load configuration
        loaded_config = await config_manager.load_config("test_system", SystemConfig)
        assert loaded_config is not None
        assert loaded_config.environment == Environment.TESTING
        assert loaded_config.max_agents == 25
        assert loaded_config.debug_mode is True
    
    async def test_config_file_formats(self, config_manager, temp_config_dir):
        """Test different configuration file formats"""
        test_config = AgentConfig(
            agent_id="format_test_agent",
            agent_type="TestAgent",
            max_concurrent_tasks=10
        )
        
        # Test JSON format
        await config_manager.save_config("test_agent.json", test_config, format="json")
        json_loaded = await config_manager.load_config("test_agent.json", AgentConfig)
        assert json_loaded.agent_id == "format_test_agent"
        
        # Test YAML format
        await config_manager.save_config("test_agent.yaml", test_config, format="yaml")
        yaml_loaded = await config_manager.load_config("test_agent.yaml", AgentConfig)
        assert yaml_loaded.agent_id == "format_test_agent"
    
    async def test_config_validation_on_load(self, config_manager, temp_config_dir):
        """Test configuration validation during loading"""
        # Create invalid configuration file
        invalid_config_data = {
            "agent_id": "invalid_agent",
            "agent_type": "TestAgent",
            "max_concurrent_tasks": -5,  # Invalid negative value
            "timeout_seconds": -100  # Invalid negative value
        }
        
        config_file = temp_config_dir / "invalid_config.json"
        with open(config_file, 'w') as f:
            json.dump(invalid_config_data, f)
        
        # Attempt to load invalid configuration
        with pytest.raises(ValueError):
            await config_manager.load_config("invalid_config.json", AgentConfig)
    
    async def test_config_hot_reloading(self, config_manager, temp_config_dir):
        """Test hot reloading of configuration changes"""
        # Create initial configuration
        initial_config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            max_agents=50
        )
        
        await config_manager.save_config("hot_reload_test", initial_config)
        
        # Enable hot reloading
        await config_manager.enable_hot_reload("hot_reload_test", SystemConfig)
        
        # Modify configuration file
        modified_config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            max_agents=100  # Changed value
        )
        
        await config_manager.save_config("hot_reload_test", modified_config)
        
        # Wait for hot reload
        await asyncio.sleep(1)
        
        # Verify configuration was reloaded
        current_config = await config_manager.get_current_config("hot_reload_test")
        assert current_config.max_agents == 100
    
    async def test_config_backup_and_restore(self, config_manager, temp_config_dir):
        """Test configuration backup and restore functionality"""
        # Create configuration
        original_config = AgentConfig(
            agent_id="backup_test_agent",
            agent_type="TestAgent",
            max_concurrent_tasks=15,
            custom_settings={"test_setting": "original_value"}
        )
        
        await config_manager.save_config("backup_test", original_config)
        
        # Create backup
        backup_result = await config_manager.create_backup("backup_test")
        assert backup_result["success"] is True
        backup_id = backup_result["backup_id"]
        
        # Modify configuration
        modified_config = AgentConfig(
            agent_id="backup_test_agent",
            agent_type="TestAgent",
            max_concurrent_tasks=25,
            custom_settings={"test_setting": "modified_value"}
        )
        
        await config_manager.save_config("backup_test", modified_config)
        
        # Restore from backup
        restore_result = await config_manager.restore_backup(backup_id)
        assert restore_result["success"] is True
        
        # Verify restoration
        restored_config = await config_manager.load_config("backup_test", AgentConfig)
        assert restored_config.max_concurrent_tasks == 15
        assert restored_config.custom_settings["test_setting"] == "original_value"
    
    async def test_config_environment_overrides(self, config_manager):
        """Test environment-based configuration overrides"""
        # Set environment variables
        os.environ["CONFIG_MAX_AGENTS"] = "200"
        os.environ["CONFIG_DEBUG_MODE"] = "false"
        os.environ["CONFIG_LOG_LEVEL"] = "ERROR"
        
        try:
            # Load configuration with environment overrides
            base_config = SystemConfig(
                environment=Environment.PRODUCTION,
                max_agents=100,
                debug_mode=True,
                log_level="INFO"
            )
            
            overridden_config = await config_manager.apply_environment_overrides(base_config)
            
            assert overridden_config.max_agents == 200  # From environment
            assert overridden_config.debug_mode is False  # From environment
            assert overridden_config.log_level == "ERROR"  # From environment
            
        finally:
            # Clean up environment variables
            for key in ["CONFIG_MAX_AGENTS", "CONFIG_DEBUG_MODE", "CONFIG_LOG_LEVEL"]:
                if key in os.environ:
                    del os.environ[key]
    
    async def test_config_encryption(self, config_manager, temp_config_dir):
        """Test configuration encryption for sensitive data"""
        # Create configuration with sensitive data
        sensitive_config = SecurityConfig(
            encryption_enabled=True,
            jwt_secret="super_secret_jwt_key",
            database_password="very_secret_password",
            api_keys={
                "openai": "sk-secret-key",
                "aws": "aws-secret-access-key"
            }
        )
        
        # Save encrypted configuration
        save_result = await config_manager.save_encrypted_config(
            "sensitive_config", 
            sensitive_config,
            encryption_key="test_encryption_key"
        )
        assert save_result["success"] is True
        
        # Verify file content is encrypted
        config_file = temp_config_dir / "sensitive_config.enc"
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            encrypted_content = f.read()
            assert "super_secret_jwt_key" not in encrypted_content  # Should be encrypted
        
        # Load and decrypt configuration
        decrypted_config = await config_manager.load_encrypted_config(
            "sensitive_config",
            SecurityConfig,
            encryption_key="test_encryption_key"
        )
        
        assert decrypted_config.jwt_secret == "super_secret_jwt_key"
        assert decrypted_config.api_keys["openai"] == "sk-secret-key"
    
    async def test_config_versioning(self, config_manager):
        """Test configuration versioning"""
        # Create initial version
        v1_config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            max_agents=50,
            version="1.0.0"
        )
        
        version_result = await config_manager.save_versioned_config("versioned_config", v1_config)
        assert version_result["success"] is True
        version_1_id = version_result["version_id"]
        
        # Create updated version
        v2_config = SystemConfig(
            environment=Environment.DEVELOPMENT,
            max_agents=100,
            version="2.0.0"
        )
        
        version_result = await config_manager.save_versioned_config("versioned_config", v2_config)
        version_2_id = version_result["version_id"]
        
        # Get version history
        version_history = await config_manager.get_config_versions("versioned_config")
        assert len(version_history) == 2
        
        # Load specific version
        v1_loaded = await config_manager.load_config_version(version_1_id, SystemConfig)
        assert v1_loaded.max_agents == 50
        assert v1_loaded.version == "1.0.0"
        
        v2_loaded = await config_manager.load_config_version(version_2_id, SystemConfig)
        assert v2_loaded.max_agents == 100
        assert v2_loaded.version == "2.0.0"
    
    @pytest.mark.performance
    async def test_config_performance(self, config_manager, assert_performance):
        """Test configuration management performance"""
        # Test configuration loading performance
        test_config = SystemConfig(
            environment=Environment.TESTING,
            max_agents=100
        )
        
        await config_manager.save_config("perf_test", test_config)
        
        # Test load performance
        start_time = datetime.now(timezone.utc)
        for _ in range(10):
            await config_manager.load_config("perf_test", SystemConfig)
        load_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        assert load_time < 5.0  # Should load 10 configs within 5 seconds
        assert_performance("config_loading", max_time=5.0)


class TestConfigValidator:
    """Test configuration validation functionality"""
    
    def test_schema_validation(self):
        """Test configuration schema validation"""
        validator = ConfigValidator()
        
        # Define schema for agent configuration
        agent_schema = {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "minLength": 1},
                "agent_type": {"type": "string", "minLength": 1},
                "max_concurrent_tasks": {"type": "integer", "minimum": 1},
                "timeout_seconds": {"type": "integer", "minimum": 1}
            },
            "required": ["agent_id", "agent_type"]
        }
        
        # Valid configuration
        valid_config = {
            "agent_id": "test_agent",
            "agent_type": "TestAgent",
            "max_concurrent_tasks": 5,
            "timeout_seconds": 300
        }
        
        validation_result = validator.validate_against_schema(valid_config, agent_schema)
        assert validation_result["valid"] is True
        
        # Invalid configuration
        invalid_config = {
            "agent_id": "",  # Empty string
            "max_concurrent_tasks": -1  # Negative value
            # Missing required agent_type
        }
        
        validation_result = validator.validate_against_schema(invalid_config, agent_schema)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_cross_field_validation(self):
        """Test cross-field validation rules"""
        validator = ConfigValidator()
        
        # Define validation rules
        validation_rules = [
            {
                "name": "timeout_consistency",
                "condition": lambda config: config.get("timeout_seconds", 0) >= config.get("retry_delay", 0),
                "message": "Timeout must be greater than or equal to retry delay"
            },
            {
                "name": "resource_limits",
                "condition": lambda config: config.get("max_concurrent_tasks", 1) <= config.get("max_total_tasks", 100),
                "message": "Concurrent tasks cannot exceed total task limit"
            }
        ]
        
        # Valid configuration
        valid_config = {
            "timeout_seconds": 300,
            "retry_delay": 30,
            "max_concurrent_tasks": 5,
            "max_total_tasks": 100
        }
        
        validation_result = validator.validate_cross_fields(valid_config, validation_rules)
        assert validation_result["valid"] is True
        
        # Invalid configuration
        invalid_config = {
            "timeout_seconds": 30,
            "retry_delay": 60,  # Retry delay > timeout
            "max_concurrent_tasks": 150,
            "max_total_tasks": 100  # Concurrent > total
        }
        
        validation_result = validator.validate_cross_fields(invalid_config, validation_rules)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) == 2
    
    def test_custom_validators(self):
        """Test custom validation functions"""
        validator = ConfigValidator()
        
        # Define custom validator for URL format
        def validate_url(value):
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url_pattern.match(value) is not None
        
        # Register custom validator
        validator.register_custom_validator("url", validate_url)
        
        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://localhost:8080",
            "https://api.example.com/v1"
        ]
        
        for url in valid_urls:
            assert validator.validate_custom("url", url) is True
        
        # Test invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "https://",  # Incomplete
        ]
        
        for url in invalid_urls:
            assert validator.validate_custom("url", url) is False
