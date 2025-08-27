"""
🔧 Redis Cluster Configuration - IA-Influencer-Agent Platform
=============================================================
Expert: Backend Senior + Cache Specialist + Performance Engineer
Creator: Fahed Mlaiel <mlaiel@live.de>
=============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

High-performance Redis cluster configuration for caching,
session management, and real-time data processing.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class RedisClusterDockerConfig:
    """Production Redis Cluster Configuration"""
    
    # Redis Configuration
    redis_version: str = "7.2.3-alpine"
    cluster_replicas: int = 1
    cluster_nodes: int = 6
    max_memory: str = "4gb"
    max_memory_policy: str = "allkeys-lru"
    
    # Security Configuration
    enable_auth: bool = True
    redis_password: str = "ultra_secure_redis_password_2024"
    enable_tls: bool = True
    
    # Performance Configuration
    save_intervals: List[str] = field(default_factory=lambda: ["900 1", "300 10", "60 10000"])
    tcp_keepalive: int = 300
    timeout: int = 0
    
    # Monitoring Configuration
    enable_monitoring: bool = True
    log_level: str = "notice"
    
    def generate_redis_config(self) -> str:
        """Generate Redis configuration file"""
        config = f"""
# Redis Configuration for IA-Influencer Platform
# High-performance caching and session management
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Network Configuration
bind 0.0.0.0
port 6379
tcp-backlog 511
tcp-keepalive {self.tcp_keepalive}
timeout {self.timeout}

# General Configuration
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel {self.log_level}
logfile ""
databases 16

# Security Configuration
{'requirepass ' + self.redis_password if self.enable_auth else '# No authentication'}
{'protected-mode yes' if self.enable_auth else 'protected-mode no'}

# Memory Management
maxmemory {self.max_memory}
maxmemory-policy {self.max_memory_policy}

# Persistence Configuration
"""
        
        # Add save intervals
        for interval in self.save_intervals:
            config += f"save {interval}\n"
        
        config += f"""
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Append Only File
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes

# Slow Log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Latency Monitoring
latency-monitor-threshold 100

# Advanced Configuration
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes

# Client Configuration
timeout 0
tcp-keepalive {self.tcp_keepalive}
maxclients 10000

# Memory Optimization
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100

# Modules
# loadmodule /usr/lib/redis/modules/redisearch.so
# loadmodule /usr/lib/redis/modules/redisjson.so
# loadmodule /usr/lib/redis/modules/redistimeseries.so

# Cluster Configuration (if clustering enabled)
# cluster-enabled yes
# cluster-config-file nodes.conf
# cluster-node-timeout 15000
# cluster-slave-validity-factor 10
# cluster-migration-barrier 1
# cluster-require-full-coverage yes
"""
        
        return config.strip()
    
    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate Redis Docker Compose service"""
        service = {
            "image": f"redis:{self.redis_version}",
            "container_name": "ia-influencer-redis",
            "restart": "unless-stopped",
            "ports": ["6379:6379"],
            "command": [
                "redis-server",
                "/usr/local/etc/redis/redis.conf"
            ],
            "volumes": [
                "redis_data:/data",
                "./config/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro",
                "./logs/redis:/var/log/redis"
            ],
            "networks": ["ia-influencer-network"],
            "environment": {
                "REDIS_REPLICATION_MODE": "master",
                "REDIS_PASSWORD": self.redis_password if self.enable_auth else "",
                "REDIS_DISABLE_COMMANDS": "FLUSHDB,FLUSHALL,CONFIG"
            },
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "4Gi"
                    },
                    "reservations": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            },
            "healthcheck": {
                "test": f"redis-cli {'--pass ' + self.redis_password if self.enable_auth else ''} ping || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "10s"
            },
            "logging": {
                "driver": "json-file",
                "options": {
                    "max-size": "100m",
                    "max-file": "3"
                }
            }
        }
        
        return service
    
    def generate_redis_sentinel_service(self) -> Dict[str, Any]:
        """Generate Redis Sentinel service for high availability"""
        return {
            "image": f"redis:{self.redis_version}",
            "container_name": "ia-influencer-redis-sentinel",
            "restart": "unless-stopped",
            "ports": ["26379:26379"],
            "command": [
                "redis-sentinel",
                "/usr/local/etc/redis/sentinel.conf"
            ],
            "volumes": [
                "./config/redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf:ro",
                "./logs/redis:/var/log/redis"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["redis"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "512Mi"
                    }
                }
            },
            "healthcheck": {
                "test": "redis-cli -p 26379 ping || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def generate_sentinel_config(self) -> str:
        """Generate Redis Sentinel configuration"""
        return f"""
# Redis Sentinel Configuration for IA-Influencer Platform
# High availability Redis monitoring
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Port configuration
port 26379
bind 0.0.0.0

# Sentinel monitoring
sentinel monitor ia-influencer-master redis 6379 2
sentinel auth-pass ia-influencer-master {self.redis_password}
sentinel down-after-milliseconds ia-influencer-master 30000
sentinel parallel-syncs ia-influencer-master 1
sentinel failover-timeout ia-influencer-master 180000

# Logging
logfile /var/log/redis/sentinel.log
loglevel notice

# Security
{'requirepass ' + self.redis_password if self.enable_auth else '# No authentication'}
"""
    
    def generate_dockerfile(self) -> str:
        """Generate custom Redis Dockerfile with optimizations"""
        return f"""
# IA-Influencer Redis Cluster Dockerfile
# High-performance Redis with custom optimizations
# Creator: Fahed Mlaiel <mlaiel@live.de>

FROM redis:{self.redis_version}

# Install additional tools
RUN apk add --no-cache \\
    curl \\
    nano \\
    htop \\
    redis-tools

# Create directories
RUN mkdir -p /usr/local/etc/redis \\
    && mkdir -p /var/log/redis \\
    && mkdir -p /data

# Copy configurations
COPY redis.conf /usr/local/etc/redis/redis.conf
COPY sentinel.conf /usr/local/etc/redis/sentinel.conf

# Set permissions
RUN chown -R redis:redis /usr/local/etc/redis \\
    && chown -R redis:redis /var/log/redis \\
    && chown -R redis:redis /data \\
    && chmod 640 /usr/local/etc/redis/redis.conf \\
    && chmod 640 /usr/local/etc/redis/sentinel.conf

# Health check script
COPY healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/healthcheck.sh

# Expose ports
EXPOSE 6379 26379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD /usr/local/bin/healthcheck.sh

# Default command
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
"""
    
    def generate_healthcheck_script(self) -> str:
        """Generate Redis health check script"""
        return f"""#!/bin/sh
# Redis Health Check Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Check Redis connectivity
if [ "{self.enable_auth}" = "True" ]; then
    redis-cli --pass {self.redis_password} ping
else
    redis-cli ping
fi

PING_RESULT=$?

# Check Redis info
if [ $PING_RESULT -eq 0 ]; then
    if [ "{self.enable_auth}" = "True" ]; then
        MEMORY_USAGE=$(redis-cli --pass {self.redis_password} INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\\r')
        CONNECTED_CLIENTS=$(redis-cli --pass {self.redis_password} INFO clients | grep connected_clients | cut -d: -f2 | tr -d '\\r')
    else
        MEMORY_USAGE=$(redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\\r')
        CONNECTED_CLIENTS=$(redis-cli INFO clients | grep connected_clients | cut -d: -f2 | tr -d '\\r')
    fi
    
    echo "Redis is healthy - Memory: $MEMORY_USAGE, Clients: $CONNECTED_CLIENTS"
    exit 0
else
    echo "Redis is not responding"
    exit 1
fi
"""
    
    def generate_redis_exporter_service(self) -> Dict[str, Any]:
        """Generate Redis Exporter service for Prometheus monitoring"""
        return {
            "image": "oliver006/redis_exporter:latest",
            "container_name": "ia-influencer-redis-exporter",
            "restart": "unless-stopped",
            "ports": ["9121:9121"],
            "environment": {
                "REDIS_ADDR": f"redis://redis:6379",
                "REDIS_PASSWORD": self.redis_password if self.enable_auth else "",
                "REDIS_EXPORTER_LOG_FORMAT": "json"
            },
            "networks": ["ia-influencer-network"],
            "depends_on": ["redis"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "200m",
                        "memory": "128Mi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:9121/metrics || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all Redis configuration files"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Redis configuration
        config_file = output_path / "redis.conf"
        with open(config_file, 'w') as f:
            f.write(self.generate_redis_config())
        files_created.append(str(config_file))
        
        # Sentinel configuration
        sentinel_file = output_path / "sentinel.conf"
        with open(sentinel_file, 'w') as f:
            f.write(self.generate_sentinel_config())
        files_created.append(str(sentinel_file))
        
        # Dockerfile
        dockerfile = output_path / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile))
        
        # Health check script
        healthcheck_file = output_path / "healthcheck.sh"
        with open(healthcheck_file, 'w') as f:
            f.write(self.generate_healthcheck_script())
        healthcheck_file.chmod(0o755)
        files_created.append(str(healthcheck_file))
        
        # Docker compose for Redis cluster
        compose_file = output_path / "docker-compose.redis.yml"
        with open(compose_file, 'w') as f:
            import yaml
            compose_config = {
                "version": "3.8",
                "services": {
                    "redis": self.generate_docker_compose_service(),
                    "redis-sentinel": self.generate_redis_sentinel_service(),
                    "redis-exporter": self.generate_redis_exporter_service()
                },
                "volumes": {
                    "redis_data": {}
                },
                "networks": {
                    "ia-influencer-network": {
                        "external": True
                    }
                }
            }
            yaml.dump(compose_config, f, default_flow_style=False, indent=2)
        files_created.append(str(compose_file))
        
        logger.info(f"✅ Redis cluster configuration saved: {len(files_created)} files created")
        return files_created
