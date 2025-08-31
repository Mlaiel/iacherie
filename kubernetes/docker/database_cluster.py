"""🗄️ Database Cluster Docker Configuration - IA-Influencer-Agent Platform
=========================================================================
Expert: Database Administrator + Performance Tuning + Replication Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional database cluster Docker configuration for high-availability
PostgreSQL with read replicas and performance optimization.
"""
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class DatabaseClusterDockerConfig:
    """Enterprise Database Cluster Docker configuration"""    
    # Container Configuration
    postgres_image: str = "postgres:15-alpine"
    postgres_tag: str = "15.5"
    container_prefix: str = "ia-influencer-postgres"
    
    # Database Configuration
    database_name: str = "ia_influencer"
    database_user: str = "ia_user"
    database_password: str = "ultra_secure_db_password_2024"
    postgres_port: int = 5432
    
    # Cluster Configuration
    enable_replication: bool = True
    replica_count: int = 2
    max_connections: int = 500
    shared_buffers: str = "2GB"
    effective_cache_size: str = "6GB"
    work_mem: str = "64MB"
    maintenance_work_mem: str = "512MB"
    
    # Performance Configuration
    checkpoint_completion_target: float = 0.9
    wal_buffers: str = "64MB"
    default_statistics_target: int = 500
    random_page_cost: float = 1.1
    effective_io_concurrency: int = 200
    
    # Environment Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Backup Configuration
    enable_backups: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    wal_backup_enabled: bool = True
    
    # Monitoring Configuration
    enable_monitoring: bool = True
    postgres_exporter_port: int = 9187
    
    # Security Configuration
    ssl_enabled: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/postgres.crt"
    ssl_key_path: str = "/etc/ssl/private/postgres.key"
    
    # Resource Limits
    master_cpu_limit: str = "4000m"
    master_memory_limit: str = "8Gi"
    replica_cpu_limit: str = "2000m"
    replica_memory_limit: str = "4Gi"
    
    # Storage Configuration
    storage_class: str = "fast-ssd"
    master_storage_size: str = "500Gi"
    replica_storage_size: str = "500Gi"
    
    # Extensions
    postgres_extensions: List[str] = field(default_factory=lambda: [
        "pg_stat_statements",
        "pg_buffercache", 
        "pgcrypto",
        "uuid-ossp",
        "btree_gin",
        "btree_gist",
        "pg_trgm",
        "fuzzystrmatch",
        "unaccent"
    ])
    
    def generate_master_dockerfile(self) -> str:
        """Generate Dockerfile for PostgreSQL master"""        return f"""# IA-Influencer PostgreSQL Master - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# High-performance PostgreSQL with optimizations

FROM {self.postgres_image}

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.postgres_tag}"
LABEL service="postgres-master"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"

# Install additional tools and extensions
RUN apk add --no-cache \\
    postgresql-contrib \\
    postgresql-dev \\
    pg_cron \\
    curl \\
    wget \\
    && rm -rf /var/cache/apk/*

# Create necessary directories
RUN mkdir -p /docker-entrypoint-initdb.d /etc/postgresql/ssl

# Copy initialization scripts
COPY init-scripts/ /docker-entrypoint-initdb.d/
COPY ssl/ /etc/postgresql/ssl/

# Set proper permissions
RUN chmod 600 /etc/postgresql/ssl/postgres.key || true
RUN chown postgres:postgres /etc/postgresql/ssl/* || true

# Environment variables
ENV POSTGRES_DB={self.database_name}
ENV POSTGRES_USER={self.database_user}
ENV POSTGRES_PASSWORD={self.database_password}
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=en_US.UTF-8"

# Performance environment variables
ENV POSTGRES_SHARED_BUFFERS={self.shared_buffers}
ENV POSTGRES_EFFECTIVE_CACHE_SIZE={self.effective_cache_size}
ENV POSTGRES_WORK_MEM={self.work_mem}
ENV POSTGRES_MAINTENANCE_WORK_MEM={self.maintenance_work_mem}
ENV POSTGRES_MAX_CONNECTIONS={self.max_connections}
ENV POSTGRES_WAL_BUFFERS={self.wal_buffers}
ENV POSTGRES_CHECKPOINT_COMPLETION_TARGET={self.checkpoint_completion_target}
ENV POSTGRES_DEFAULT_STATISTICS_TARGET={self.default_statistics_target}
ENV POSTGRES_RANDOM_PAGE_COST={self.random_page_cost}
ENV POSTGRES_EFFECTIVE_IO_CONCURRENCY={self.effective_io_concurrency}

# SSL Configuration
ENV POSTGRES_SSL_ENABLED={str(self.ssl_enabled).lower()}
ENV POSTGRES_SSL_CERT_FILE={self.ssl_cert_path}
ENV POSTGRES_SSL_KEY_FILE={self.ssl_key_path}

# Replication Configuration
ENV POSTGRES_REPLICATION_USER=replicator
ENV POSTGRES_REPLICATION_PASSWORD=replication_secure_password

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD pg_isready -U {self.database_user} -d {self.database_name} || exit 1

EXPOSE {self.postgres_port}

# Custom entrypoint for advanced configuration
COPY custom-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

ENTRYPOINT ["custom-entrypoint.sh"]
CMD ["postgres"]
"""
    def generate_replica_dockerfile(self) -> str:
        """Generate Dockerfile for PostgreSQL replica"""        return f"""# IA-Influencer PostgreSQL Replica - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Read-only replica with streaming replication

FROM {self.postgres_image}

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.postgres_tag}"
LABEL service="postgres-replica"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"

# Install additional tools
RUN apk add --no-cache \\
    postgresql-contrib \\
    curl \\
    wget \\
    && rm -rf /var/cache/apk/*

# Create necessary directories
RUN mkdir -p /docker-entrypoint-initdb.d /etc/postgresql/ssl

# Copy SSL certificates
COPY ssl/ /etc/postgresql/ssl/

# Set proper permissions
RUN chmod 600 /etc/postgresql/ssl/postgres.key || true
RUN chown postgres:postgres /etc/postgresql/ssl/* || true

# Environment variables
ENV POSTGRES_USER={self.database_user}
ENV POSTGRES_PASSWORD={self.database_password}
ENV POSTGRES_DB={self.database_name}

# Replication Configuration
ENV POSTGRES_MASTER_HOST=postgres-master
ENV POSTGRES_MASTER_PORT={self.postgres_port}
ENV POSTGRES_REPLICATION_USER=replicator
ENV POSTGRES_REPLICATION_PASSWORD=replication_secure_password

# Performance Configuration
ENV POSTGRES_SHARED_BUFFERS={self.shared_buffers}
ENV POSTGRES_EFFECTIVE_CACHE_SIZE={self.effective_cache_size}
ENV POSTGRES_MAX_CONNECTIONS={self.max_connections}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \\
    CMD pg_isready -U {self.database_user} -d {self.database_name} || exit 1

EXPOSE {self.postgres_port}

# Replica-specific entrypoint
COPY replica-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/replica-entrypoint.sh

ENTRYPOINT ["replica-entrypoint.sh"]
CMD ["postgres"]
"""
    def generate_docker_compose_services(self) -> Dict[str, Any]:
        """Generate docker-compose services for database cluster"""        services = {}
        
        # PostgreSQL Master
        services["postgres-master"] = {
            "image": f"{self.container_prefix}-master:{self.postgres_tag}",
            "container_name": f"{self.container_prefix}-master",
            "restart": "unless-stopped",
            "ports": [f"{self.postgres_port}:{self.postgres_port}"],
            "environment": {
                "POSTGRES_DB": self.database_name,
                "POSTGRES_USER": self.database_user,
                "POSTGRES_PASSWORD": self.database_password,
                "POSTGRES_REPLICATION_USER": "replicator",
                "POSTGRES_REPLICATION_PASSWORD": "replication_secure_password",
                "POSTGRES_SHARED_BUFFERS": self.shared_buffers,
                "POSTGRES_EFFECTIVE_CACHE_SIZE": self.effective_cache_size,
                "POSTGRES_WORK_MEM": self.work_mem,
                "POSTGRES_MAINTENANCE_WORK_MEM": self.maintenance_work_mem,
                "POSTGRES_MAX_CONNECTIONS": str(self.max_connections),
                "POSTGRES_WAL_BUFFERS": self.wal_buffers,
                "POSTGRES_CHECKPOINT_COMPLETION_TARGET": str(self.checkpoint_completion_target),
                "POSTGRES_DEFAULT_STATISTICS_TARGET": str(self.default_statistics_target),
                "POSTGRES_RANDOM_PAGE_COST": str(self.random_page_cost),
                "POSTGRES_EFFECTIVE_IO_CONCURRENCY": str(self.effective_io_concurrency),
                "POSTGRES_SSL_ENABLED": str(self.ssl_enabled).lower()
            },
            "volumes": [
                "postgres_master_data:/var/lib/postgresql/data",
                "./config/postgres/master:/etc/postgresql:ro",
                "./ssl:/etc/postgresql/ssl:ro",
                "./logs/postgres:/var/log/postgresql"
            ],
            "networks": ["ia-influencer-network"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": self.master_cpu_limit,
                        "memory": self.master_memory_limit
                    },
                    "reservations": {
                        "cpus": "2000m",
                        "memory": "4Gi"
                    }
                }
            },
            "healthcheck": {
                "test": f"pg_isready -U {self.database_user} -d {self.database_name}",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"],
            "cap_add": ["SETUID", "SETGID", "DAC_OVERRIDE"]
        }
        
        # PostgreSQL Replicas
        if self.enable_replication:
            for i in range(1, self.replica_count + 1):
                services[f"postgres-replica-{i}"] = {
                    "image": f"{self.container_prefix}-replica:{self.postgres_tag}",
                    "container_name": f"{self.container_prefix}-replica-{i}",
                    "restart": "unless-stopped",
                    "ports": [f"{self.postgres_port + i}:{self.postgres_port}"],
                    "environment": {
                        "POSTGRES_DB": self.database_name,
                        "POSTGRES_USER": self.database_user,
                        "POSTGRES_PASSWORD": self.database_password,
                        "POSTGRES_MASTER_HOST": "postgres-master",
                        "POSTGRES_MASTER_PORT": str(self.postgres_port),
                        "POSTGRES_REPLICATION_USER": "replicator",
                        "POSTGRES_REPLICATION_PASSWORD": "replication_secure_password",
                        "POSTGRES_SHARED_BUFFERS": self.shared_buffers,
                        "POSTGRES_EFFECTIVE_CACHE_SIZE": self.effective_cache_size,
                        "POSTGRES_MAX_CONNECTIONS": str(self.max_connections)
                    },
                    "volumes": [
                        f"postgres_replica_{i}_data:/var/lib/postgresql/data",
                        "./config/postgres/replica:/etc/postgresql:ro",
                        "./ssl:/etc/postgresql/ssl:ro",
                        f"./logs/postgres-replica-{i}:/var/log/postgresql"
                    ],
                    "networks": ["ia-influencer-network"],
                    "depends_on": ["postgres-master"],
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": self.replica_cpu_limit,
                                "memory": self.replica_memory_limit
                            },
                            "reservations": {
                                "cpus": "1000m",
                                "memory": "2Gi"
                            }
                        }
                    },
                    "healthcheck": {
                        "test": f"pg_isready -U {self.database_user} -d {self.database_name}",
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "90s"
                    },
                    "security_opt": [
                        "no-new-privileges:true"
                    ],
                    "cap_drop": ["ALL"],
                    "cap_add": ["SETUID", "SETGID", "DAC_OVERRIDE"]
                }
        
        # PostgreSQL Exporter for monitoring
        if self.enable_monitoring:
            services["postgres-exporter"] = {
                "image": "prometheuscommunity/postgres-exporter:v0.15.0",
                "container_name": f"{self.container_prefix}-exporter",
                "restart": "unless-stopped",
                "ports": [f"{self.postgres_exporter_port}:{self.postgres_exporter_port}"],
                "environment": {
                    "DATA_SOURCE_NAME": f"postgresql://{self.database_user}:{self.database_password}@postgres-master:{self.postgres_port}/{self.database_name}?sslmode=prefer"
                },
                "networks": ["ia-influencer-network"],
                "depends_on": ["postgres-master"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "200m",
                            "memory": "256Mi"
                        }
                    }
                }
            }
        
        # Backup service
        if self.enable_backups:
            services["postgres-backup"] = {
                "image": "prodrigestivill/postgres-backup-local:15",
                "container_name": f"{self.container_prefix}-backup",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_HOST": "postgres-master",
                    "POSTGRES_DB": self.database_name,
                    "POSTGRES_USER": self.database_user,
                    "POSTGRES_PASSWORD": self.database_password,
                    "POSTGRES_EXTRA_OPTS": "-Z9 --schema=public --blobs",
                    "SCHEDULE": self.backup_schedule,
                    "BACKUP_KEEP_DAYS": str(self.backup_retention_days),
                    "BACKUP_KEEP_WEEKS": "4",
                    "BACKUP_KEEP_MONTHS": "6",
                    "HEALTHCHECK_PORT": "8080"
                },
                "volumes": [
                    "./backups/postgres:/backups"
                ],
                "networks": ["ia-influencer-network"],
                "depends_on": ["postgres-master"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            }
        
        return services

    def generate_postgres_config(self) -> str:
        """Generate optimized PostgreSQL configuration"""        return f"""# IA-Influencer PostgreSQL Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>
# High-performance production configuration

# CONNECTIONS AND AUTHENTICATION
listen_addresses = '*'
port = {self.postgres_port}
max_connections = {self.max_connections}
superuser_reserved_connections = 3

# SSL CONFIGURATION
ssl = {'on' if self.ssl_enabled else 'off'}
ssl_cert_file = '{self.ssl_cert_path}'
ssl_key_file = '{self.ssl_key_path}'
ssl_protocols = 'TLSv1.2,TLSv1.3'

# MEMORY
shared_buffers = {self.shared_buffers}
effective_cache_size = {self.effective_cache_size}
work_mem = {self.work_mem}
maintenance_work_mem = {self.maintenance_work_mem}
dynamic_shared_memory_type = posix

# WAL
wal_buffers = {self.wal_buffers}
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = {self.checkpoint_completion_target}
checkpoint_timeout = 15min

# REPLICATION
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on
hot_standby_feedback = on

# QUERY TUNING
default_statistics_target = {self.default_statistics_target}
random_page_cost = {self.random_page_cost}
effective_io_concurrency = {self.effective_io_concurrency}
seq_page_cost = 1.0

# LOGGING
log_destination = 'stderr,csvlog'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_file_mode = 0600
log_truncate_on_rotation = on
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 10MB
log_autovacuum_min_duration = 0
log_error_verbosity = default
log_min_duration_statement = 1000

# AUTOVACUUM
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 30s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1
autovacuum_vacuum_cost_delay = 10ms
autovacuum_vacuum_cost_limit = 1000

# EXTENSIONS
shared_preload_libraries = 'pg_stat_statements,pg_buffercache'

# PERFORMANCE MONITORING
track_activities = on
track_counts = on
track_io_timing = on
track_functions = all
"""
    def generate_init_script(self) -> str:
        """Generate database initialization script"""        return f"""#!/bin/bash
# IA-Influencer Database Initialization Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "Initializing IA-Influencer database..."

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    {chr(10).join(f"CREATE EXTENSION IF NOT EXISTS {ext};" for ext in self.postgres_extensions)}
    
    -- Create replication user
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replication_secure_password';
    
    -- Create application schemas
    CREATE SCHEMA IF NOT EXISTS content_protection;
    CREATE SCHEMA IF NOT EXISTS monetization;
    CREATE SCHEMA IF NOT EXISTS analytics;
    CREATE SCHEMA IF NOT EXISTS fingerprinting;
    CREATE SCHEMA IF NOT EXISTS ai_processing;
    
    -- Grant permissions
    GRANT CONNECT ON DATABASE {self.database_name} TO {self.database_user};
    GRANT USAGE ON SCHEMA public TO {self.database_user};
    GRANT USAGE ON SCHEMA content_protection TO {self.database_user};
    GRANT USAGE ON SCHEMA monetization TO {self.database_user};
    GRANT USAGE ON SCHEMA analytics TO {self.database_user};
    GRANT USAGE ON SCHEMA fingerprinting TO {self.database_user};
    GRANT USAGE ON SCHEMA ai_processing TO {self.database_user};
    
    -- Create performance monitoring views
    CREATE OR REPLACE VIEW performance_stats AS
    SELECT 
        schemaname,
        tablename,
        attname,
        n_distinct,
        correlation
    FROM pg_stats
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog');
    
    -- Create replication monitoring view
    CREATE OR REPLACE VIEW replication_status AS
    SELECT 
        client_addr,
        state,
        sent_lsn,
        write_lsn,
        flush_lsn,
        replay_lsn,
        write_lag,
        flush_lag,
        replay_lag
    FROM pg_stat_replication;
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_performance_monitoring ON pg_stat_user_tables(relname);
    
EOSQL

echo "Database initialization completed successfully."
"""
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all configuration files to output directory"""        import os
        from pathlib import Path
        
        config_dir = Path(output_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Master Dockerfile
        master_dockerfile_path = config_dir / "Dockerfile.master"
        with open(master_dockerfile_path, 'w') as f:
            f.write(self.generate_master_dockerfile())
        files_created.append(str(master_dockerfile_path))
        
        # Save Replica Dockerfile
        replica_dockerfile_path = config_dir / "Dockerfile.replica"
        with open(replica_dockerfile_path, 'w') as f:
            f.write(self.generate_replica_dockerfile())
        files_created.append(str(replica_dockerfile_path))
        
        # Save PostgreSQL configuration
        postgres_config_path = config_dir / "postgresql.conf"
        with open(postgres_config_path, 'w') as f:
            f.write(self.generate_postgres_config())
        files_created.append(str(postgres_config_path))
        
        # Save initialization script
        init_script_path = config_dir / "init-database.sql"
        with open(init_script_path, 'w') as f:
            f.write(self.generate_init_script())
        files_created.append(str(init_script_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.database.yml"
        
        # Generate volumes
        volumes = {"postgres_master_data": {}}
        if self.enable_replication:
            for i in range(1, self.replica_count + 1):
                volumes[f"postgres_replica_{i}_data"] = {}
        
        service_config = {
            "version": "3.8",
            "services": self.generate_docker_compose_services(),
            "volumes": volumes
        }
        
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f"✅ Database Cluster configuration files saved: {files_created}")
        return files_created
