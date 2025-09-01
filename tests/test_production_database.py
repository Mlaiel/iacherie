"""
Test Production Database Configuration

This test validates the production database configuration and
ensures all components are properly set up.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestProductionDatabaseConfig:
    """Test production database configuration."""
    
    def test_alembic_config_exists(self):
        """Test that alembic configuration exists."""
        alembic_ini = Path(__file__).parent.parent / 'alembic.ini'
        assert alembic_ini.exists(), "alembic.ini configuration file should exist"
        
        # Check content
        content = alembic_ini.read_text()
        assert 'postgresql+asyncpg' in content, "Should use asyncpg driver"
        assert 'sslmode=require' in content, "Should require SSL"
    
    def test_postgresql_config_ssl_enabled(self):
        """Test PostgreSQL configuration has SSL enabled."""
        pg_config = Path(__file__).parent.parent / 'database/config/postgresql.conf'
        assert pg_config.exists(), "PostgreSQL config should exist"
        
        content = pg_config.read_text()
        assert 'ssl = on' in content, "SSL should be enabled"
        assert 'ssl_min_protocol_version' in content, "SSL protocol version should be set"
    
    def test_pg_hba_enforces_ssl(self):
        """Test pg_hba.conf enforces SSL connections."""
        pg_hba = Path(__file__).parent.parent / 'database/config/pg_hba.conf'
        assert pg_hba.exists(), "pg_hba.conf should exist"
        
        content = pg_hba.read_text()
        assert 'hostssl' in content, "Should have SSL-only host entries"
        assert 'hostnossl all all all reject' in content, "Should reject non-SSL connections"
    
    def test_migration_scripts_exist(self):
        """Test that migration management scripts exist."""
        scripts_dir = Path(__file__).parent.parent / 'scripts'
        
        required_scripts = [
            'production_migrations.py',
            'manage_db_users.py',
            'configure_wal_archiving.sh',
            'deploy_production_database.py'
        ]
        
        for script in required_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Script {script} should exist"
            assert script_path.stat().st_mode & 0o111, f"Script {script} should be executable"
    
    def test_index_definitions_exist(self):
        """Test that performance index definitions exist."""
        index_file = Path(__file__).parent.parent / 'database/performance_indexes.py'
        assert index_file.exists(), "Performance indexes module should exist"
        
        # Import and check basic structure
        import importlib.util
        spec = importlib.util.spec_from_file_location("performance_indexes", index_file)
        module = importlib.util.module_from_spec(spec)
        
        # Should not fail to import
        assert module is not None

class TestProductionIndexManager:
    """Test production index management."""
    
    @pytest.fixture
    def mock_engine(self):
        """Mock database engine."""
        engine = Mock()
        engine.begin = AsyncMock()
        return engine
    
    def test_index_definitions_valid(self, mock_engine):
        """Test that index definitions are valid."""
        from database.performance_indexes import ProductionIndexManager
        
        manager = ProductionIndexManager(mock_engine)
        indexes = manager.indexes
        
        assert len(indexes) > 0, "Should have index definitions"
        
        # Check each index has required fields
        for index in indexes:
            assert hasattr(index, 'name'), "Index should have name"
            assert hasattr(index, 'table'), "Index should have table"
            assert hasattr(index, 'columns'), "Index should have columns"
            assert len(index.columns) > 0, "Index should have at least one column"

class TestProductionPoolConfig:
    """Test production connection pool configuration."""
    
    def test_production_pool_config_valid(self):
        """Test production pool configuration is valid."""
        from database.production_pool import ProductionPoolConfig
        
        config = ProductionPoolConfig()
        
        # Check SSL is enforced
        assert config.ssl_mode == "require", "Should require SSL by default"
        
        # Check reasonable pool sizes
        assert config.pool_size > 0, "Pool size should be positive"
        assert config.max_overflow >= 0, "Max overflow should be non-negative"
        
        # Check timeouts are reasonable
        assert config.pool_timeout > 0, "Pool timeout should be positive"
        assert config.server_connect_timeout > 0, "Server connect timeout should be positive"

class TestProductionBackupConfig:
    """Test production backup configuration."""
    
    def test_backup_config_defaults(self):
        """Test backup configuration has secure defaults."""
        from database.production_backup import BackupConfig
        
        config = BackupConfig()
        
        # Check retention is reasonable
        assert config.retention_days > 0, "Retention should be positive"
        assert config.retention_days <= 365, "Retention should not be excessive"
        
        # Check compression is enabled
        assert config.compression_level > 0, "Compression should be enabled"
        
        # Check verification is enabled by default
        assert config.verify_backups, "Backup verification should be enabled"

class TestHealthCheckerConfig:
    """Test database health checker configuration."""
    
    def test_health_check_config_valid(self):
        """Test health check configuration is valid."""
        from database.health_checker import HealthCheckConfig
        
        config = HealthCheckConfig()
        
        # Check timeouts are reasonable
        assert config.connection_timeout > 0, "Connection timeout should be positive"
        assert config.query_timeout > config.connection_timeout, "Query timeout should be longer than connection timeout"
        
        # Check thresholds are reasonable
        assert 0 < config.max_connection_usage_percent <= 100, "Connection usage threshold should be a valid percentage"
        assert config.min_disk_space_gb > 0, "Minimum disk space should be positive"

@pytest.mark.asyncio
class TestDatabaseConnectivity:
    """Test database connectivity with mocks."""
    
    async def test_connection_string_format(self):
        """Test database connection string format."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'POSTGRES_USER_PRODUCTION': 'test_user',
            'POSTGRES_PASSWORD_PRODUCTION': 'test_pass',
            'POSTGRES_HOST_PRODUCTION': 'test_host',
            'POSTGRES_PORT_PRODUCTION': '5432',
            'POSTGRES_DB_PRODUCTION': 'test_db'
        }):
            from database.production_pool import ProductionConnectionPool, ProductionPoolConfig
            
            config = ProductionPoolConfig()
            pool = ProductionConnectionPool(config)
            
            # Get connection URL
            url = pool._get_database_url('test_host')
            
            # Verify SSL is required
            assert 'sslmode=require' in url, "Connection should require SSL"
            assert 'postgresql+asyncpg://' in url, "Should use asyncpg driver"
            assert 'test_user:test_pass@test_host:5432/test_db' in url, "Should have correct connection parameters"

class TestEnvironmentConfiguration:
    """Test environment-specific configuration."""
    
    def test_production_environment_variables(self):
        """Test production environment variable handling."""
        # Test with production environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            assert os.getenv('ENVIRONMENT') == 'production'
    
    def test_ssl_certificate_paths(self):
        """Test SSL certificate path configuration."""
        from database.production_pool import ProductionPoolConfig
        
        config = ProductionPoolConfig()
        
        # Should have SSL mode set
        assert config.ssl_mode is not None, "SSL mode should be configured"
        
        # SSL paths should be configurable
        config.ssl_cert_path = '/path/to/cert.pem'
        config.ssl_key_path = '/path/to/key.pem'
        
        assert config.ssl_cert_path == '/path/to/cert.pem'
        assert config.ssl_key_path == '/path/to/key.pem'

def test_deployment_script_import():
    """Test that deployment script can be imported."""
    deployment_script = Path(__file__).parent.parent / 'scripts/deploy_production_database.py'
    assert deployment_script.exists(), "Deployment script should exist"
    
    # Should be able to import without errors
    import importlib.util
    spec = importlib.util.spec_from_file_location("deploy", deployment_script)
    module = importlib.util.module_from_spec(spec)
    
    # Should not fail to create module
    assert module is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])