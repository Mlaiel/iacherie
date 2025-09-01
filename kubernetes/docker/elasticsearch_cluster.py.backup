"""🔍 Elasticsearch Cluster Configuration - IA-Influencer-Agent Platform
======================================================================
Expert: Search Engineer + Data Specialist + Performance Analyst
Creator: Fahed Mlaiel <mlaiel@live.de>
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Production-ready Elasticsearch cluster for search, analytics,
and content indexing with optimal performance configuration.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class ElasticsearchClusterDockerConfig:
    """Production Elasticsearch Cluster Configuration"""
    
    # Elasticsearch Configuration
    es_version: str = "8.11.0"
    cluster_name: str = "ia-influencer-cluster"
    node_name: str = "ia-influencer-es-node"
    
    # Cluster Configuration
    cluster_nodes: int = 3
    master_nodes: int = 2
    data_nodes: int = 3
    
    # Memory Configuration
    heap_size: str = "2g"
    max_memory: str = "4Gi"
    
    # Security Configuration
    enable_security: bool = True
    enable_ssl: bool = True
    elastic_password: str = "ultra_secure_elastic_password_2024"
    
    # Performance Configuration
    indices_memory_index_buffer_size: str = "10%"
    indices_queries_cache_size: str = "10%"
    indices_fielddata_cache_size: str = "20%"
    
    def generate_elasticsearch_config(self) -> str:
        """Generate Elasticsearch configuration file"""
        config = f"""# Elasticsearch Configuration for IA-Influencer Platform
# High-performance search and analytics engine
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Cluster Configuration
cluster.name: {self.cluster_name}
node.name: {self.node_name}
node.roles: [ data, master, ingest, ml ]

# Network Configuration
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# Discovery Configuration
discovery.type: single-node
# discovery.seed_hosts: ["es-node-1", "es-node-2", "es-node-3"]
# cluster.initial_master_nodes: ["es-node-1", "es-node-2"]

# Path Configuration
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs
path.repo: ["/usr/share/elasticsearch/backups"]

# Memory Configuration
bootstrap.memory_lock: true
indices.memory.index_buffer_size: {self.indices_memory_index_buffer_size}
indices.queries.cache.size: {self.indices_queries_cache_size}
indices.fielddata.cache.size: {self.indices_fielddata_cache_size}

# Performance Configuration
thread_pool.write.queue_size: 1000
thread_pool.search.queue_size: 1000
thread_pool.get.queue_size: 1000

# Index Configuration
index.number_of_shards: 1
index.number_of_replicas: 1
index.refresh_interval: 30s
index.translog.flush_threshold_size: 1gb

# Security Configuration
xpack.security.enabled: {str(self.enable_security).lower()}
xpack.security.enrollment.enabled: {str(self.enable_security).lower()}
xpack.security.http.ssl.enabled: {str(self.enable_ssl).lower()}
xpack.security.transport.ssl.enabled: {str(self.enable_ssl).lower()}

# Monitoring Configuration
xpack.monitoring.collection.enabled: true
xpack.monitoring.collection.interval: 30s

# Machine Learning Configuration
xpack.ml.enabled: true
xpack.ml.max_machine_memory_percent: 30

# Watcher Configuration (Alerting)
xpack.watcher.enabled: true

# SQL Configuration
xpack.sql.enabled: true

# License Configuration
xpack.license.self_generated.type: basic

# HTTP Configuration
http.max_content_length: 100mb
http.compression: true
http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-headers: "X-Requested-With,Content-Type,Content-Length,Authorization"

# Circuit Breaker Configuration
indices.breaker.total.limit: 70%
indices.breaker.fielddata.limit: 40%
indices.breaker.request.limit: 40%

# Logging Configuration
logger.level: INFO
logger.org.elasticsearch.discovery: WARN
logger.org.elasticsearch.cluster.service: WARN

# Action Configuration
action.destructive_requires_name: true
action.auto_create_index: true

# Gateway Configuration
gateway.recover_after_nodes: 1
gateway.expected_nodes: {self.cluster_nodes}
gateway.recover_after_time: 5m

# Cluster Routing
cluster.routing.allocation.disk.threshold_enabled: true
cluster.routing.allocation.disk.watermark.low: 85%
cluster.routing.allocation.disk.watermark.high: 90%
cluster.routing.allocation.disk.watermark.flood_stage: 95%
"""
        
        return config.strip()
    
    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate Elasticsearch Docker Compose service"""
        service = {
            "image": f"docker.elastic.co/elasticsearch/elasticsearch:{self.es_version}",
            "container_name": "ia-influencer-elasticsearch",
            "restart": "unless-stopped",
            "ports": ["9200:9200", "9300:9300"],
            "environment": {
                "cluster.name": self.cluster_name,
                "node.name": self.node_name,
                "discovery.type": "single-node",
                "ES_JAVA_OPTS": f"-Xms{self.heap_size} -Xmx{self.heap_size}",
                "xpack.security.enabled": str(self.enable_security).lower(),
                "xpack.security.enrollment.enabled": str(self.enable_security).lower(),
                "ELASTIC_PASSWORD": self.elastic_password if self.enable_security else "",
                "bootstrap.memory_lock": "true"
            },
            "volumes": [
                "elasticsearch_data:/usr/share/elasticsearch/data",
                "elasticsearch_logs:/usr/share/elasticsearch/logs",
                "elasticsearch_backups:/usr/share/elasticsearch/backups",
                "./config/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro",
                "./config/elasticsearch/jvm.options:/usr/share/elasticsearch/config/jvm.options:ro"
            ],
            "networks": ["ia-influencer-network"],
            "ulimits": {
                "memlock": {
                    "soft": -1,
                    "hard": -1
                },
                "nofile": {
                    "soft": 65536,
                    "hard": 65536
                }
            },
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "4000m",
                        "memory": self.max_memory
                    },
                    "reservations": {
                        "cpus": "2000m",
                        "memory": "2Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:9200/_cluster/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
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
    
    def generate_kibana_service(self) -> Dict[str, Any]:
        """Generate Kibana service for Elasticsearch visualization"""
        return {
            "image": f"docker.elastic.co/kibana/kibana:{self.es_version}",
            "container_name": "ia-influencer-kibana",
            "restart": "unless-stopped",
            "ports": ["5601:5601"],
            "environment": {
                "ELASTICSEARCH_HOSTS": "http://elasticsearch:9200",
                "ELASTICSEARCH_USERNAME": "elastic",
                "ELASTICSEARCH_PASSWORD": self.elastic_password if self.enable_security else "",
                "SERVER_NAME": "kibana.ia-influencer.com",
                "SERVER_HOST": "0.0.0.0",
                "XPACK_SECURITY_ENABLED": str(self.enable_security).lower(),
                "XPACK_MONITORING_ENABLED": "true"
            },
            "volumes": [
                "./config/kibana/kibana.yml:/usr/share/kibana/config/kibana.yml:ro",
                "kibana_data:/usr/share/kibana/data"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["elasticsearch"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "2Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:5601/api/status || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            }
        }
    
    def generate_kibana_config(self) -> str:
        """Generate Kibana configuration file"""
        return f"""# Kibana Configuration for IA-Influencer Platform
# Analytics and visualization interface
# Creator: Fahed Mlaiel <mlaiel@live.de>

server.name: kibana.ia-influencer.com
server.host: 0.0.0.0
server.port: 5601

elasticsearch.hosts: ["http://elasticsearch:9200"]
{'elasticsearch.username: elastic' if self.enable_security else ''}
{'elasticsearch.password: ' + self.elastic_password if self.enable_security else ''}

# Security Configuration
xpack.security.enabled: {str(self.enable_security).lower()}
xpack.monitoring.enabled: true
xpack.reporting.enabled: true

# UI Configuration
server.maxPayload: 1048576
server.basePath: ""
server.rewriteBasePath: false

# Logging Configuration
logging.appenders.default:
  type: console
  layout:
    type: json
logging.root:
  level: info

# Advanced Configuration
map.includeElasticMapsService: true
telemetry.enabled: false
newsfeed.enabled: false

# Dashboard Configuration
xpack.canvas.enabled: true
xpack.infra.enabled: true
xpack.apm.enabled: true
xpack.uptime.enabled: true
"""
    
    def generate_jvm_options(self) -> str:
        """Generate JVM options for Elasticsearch"""
        return f"""# JVM Options for IA-Influencer Elasticsearch
# Optimized for production performance
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Heap Size
-Xms{self.heap_size}
-Xmx{self.heap_size}

# GC Configuration
-XX:+UseG1GC
-XX:G1HeapRegionSize=16m
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap
-XX:MaxDirectMemorySize=1g

# GC Logging
-Xlog:gc*,gc+age=trace,safepoint:gc.log:utctime,pid,tid,level
-XX:+UseGCLogRotation
-XX:NumberOfGCLogFiles=32
-XX:GCLogFileSize=64m

# Exception Handling
-XX:+ExitOnOutOfMemoryError
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/usr/share/elasticsearch/logs/

# Performance Optimizations
-XX:+UnlockDiagnosticVMOptions
-XX:+DebugNonSafepoints
-XX:+PrintGCApplicationStoppedTime
-XX:+PrintGCApplicationConcurrentTime

# JIT Optimizations
-XX:+UseStringDeduplication
-XX:+OptimizeStringConcat
-XX:+UseCompressedOops

# Security
-Djava.security.policy=all.policy
-Dlog4j2.disable.jmx=true

# Network
-Djava.net.preferIPv4Stack=true

# File Encoding
-Dfile.encoding=UTF-8

# Temporary Directory
-Djava.io.tmpdir=/tmp
"""
    
    def generate_elasticsearch_exporter_service(self) -> Dict[str, Any]:
        """Generate Elasticsearch Exporter for Prometheus monitoring"""
        return {
            "image": "quay.io/prometheuscommunity/elasticsearch-exporter:latest",
            "container_name": "ia-influencer-elasticsearch-exporter",
            "restart": "unless-stopped",
            "ports": ["9114:9114"],
            "command": [
                "--es.uri=http://elasticsearch:9200",
                f"--es.username=elastic" if self.enable_security else "",
                f"--es.password={self.elastic_password}" if self.enable_security else "",
                "--es.all",
                "--es.indices",
                "--es.cluster_settings",
                "--web.listen-address=:9114"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["elasticsearch"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "200m",
                        "memory": "128Mi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:9114/metrics || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def generate_dockerfile(self) -> str:
        """Generate custom Elasticsearch Dockerfile"""
        return f"""# IA-Influencer Elasticsearch Dockerfile
# Production-optimized search engine
# Creator: Fahed Mlaiel <mlaiel@live.de>

FROM docker.elastic.co/elasticsearch/elasticsearch:{self.es_version}

# Install additional plugins
RUN elasticsearch-plugin install --batch analysis-icu
RUN elasticsearch-plugin install --batch analysis-phonetic
RUN elasticsearch-plugin install --batch analysis-smartcn
RUN elasticsearch-plugin install --batch analysis-kuromoji
RUN elasticsearch-plugin install --batch mapper-size
RUN elasticsearch-plugin install --batch mapper-murmur3

# Create directories
USER root
RUN mkdir -p /usr/share/elasticsearch/backups \\
    && chown elasticsearch:elasticsearch /usr/share/elasticsearch/backups \\
    && chmod 755 /usr/share/elasticsearch/backups

# Copy custom configurations
COPY elasticsearch.yml /usr/share/elasticsearch/config/
COPY jvm.options /usr/share/elasticsearch/config/
COPY log4j2.properties /usr/share/elasticsearch/config/

# Set permissions
RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/config/* \\
    && chmod 644 /usr/share/elasticsearch/config/*

# Health check script
COPY healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/healthcheck.sh

USER elasticsearch

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD /usr/local/bin/healthcheck.sh

# Expose ports
EXPOSE 9200 9300
"""
    
    def generate_healthcheck_script(self) -> str:
        """Generate Elasticsearch health check script"""
        return """#!/bin/bash
# Elasticsearch Health Check Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Check cluster health
HEALTH=$(curl -s http://localhost:9200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$HEALTH" = "green" ] || [ "$HEALTH" = "yellow" ]; then
    echo "Elasticsearch cluster is healthy: $HEALTH"
    exit 0
else
    echo "Elasticsearch cluster is unhealthy: $HEALTH"
    exit 1
fi
"""
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all Elasticsearch configuration files"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Elasticsearch configuration
        es_config_file = output_path / "elasticsearch.yml"
        with open(es_config_file, 'w') as f:
            f.write(self.generate_elasticsearch_config())
        files_created.append(str(es_config_file))
        
        # JVM options
        jvm_file = output_path / "jvm.options"
        with open(jvm_file, 'w') as f:
            f.write(self.generate_jvm_options())
        files_created.append(str(jvm_file))
        
        # Kibana configuration
        kibana_file = output_path / "kibana.yml"
        with open(kibana_file, 'w') as f:
            f.write(self.generate_kibana_config())
        files_created.append(str(kibana_file))
        
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
        
        # Log4j configuration
        log4j_file = output_path / "log4j2.properties"
        with open(log4j_file, 'w') as f:
            f.write(self._generate_log4j_config())
        files_created.append(str(log4j_file))
        
        # Docker compose for Elasticsearch cluster
        compose_file = output_path / "docker-compose.elasticsearch.yml"
        with open(compose_file, 'w') as f:
            import yaml
            compose_config = {
                "version": "3.8",
                "services": {
                    "elasticsearch": self.generate_docker_compose_service(),
                    "kibana": self.generate_kibana_service(),
                    "elasticsearch-exporter": self.generate_elasticsearch_exporter_service()
                },
                "volumes": {
                    "elasticsearch_data": {},
                    "elasticsearch_logs": {},
                    "elasticsearch_backups": {},
                    "kibana_data": {}
                },
                "networks": {
                    "ia-influencer-network": {
                        "external": True
                    }
                }
            }
            yaml.dump(compose_config, f, default_flow_style=False, indent=2)
        files_created.append(str(compose_file))
        
        logger.info(f"✅ Elasticsearch cluster configuration saved: {len(files_created)} files created")
        return files_created
    
    def _generate_log4j_config(self) -> str:
        """Generate Log4j configuration for Elasticsearch"""
        return """# Log4j Configuration for IA-Influencer Elasticsearch
# Optimized logging configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

status = error

appender.console.type = Console
appender.console.name = console
appender.console.layout.type = PatternLayout
appender.console.layout.pattern = [%d{ISO8601}][%-5p][%-25c{1.}] [%node_name]%marker %m%n

rootLogger.level = info
rootLogger.appenderRef.console.ref = console

logger.searchguard.name = com.floragunn.searchguard
logger.searchguard.level = info

logger.index_search_slowlog_rolling.name = index.search.slowlog
logger.index_search_slowlog_rolling.level = trace
logger.index_search_slowlog_rolling.appenderRef.index_search_slowlog_rolling.ref = index_search_slowlog_rolling
logger.index_search_slowlog_rolling.additivity = false

logger.index_indexing_slowlog.name = index.indexing.slowlog.index
logger.index_indexing_slowlog.level = trace
logger.index_indexing_slowlog.appenderRef.index_indexing_slowlog_rolling.ref = index_indexing_slowlog_rolling
logger.index_indexing_slowlog.additivity = false

logger.deprecation.name = org.elasticsearch.deprecation
logger.deprecation.level = warn
logger.deprecation.appenderRef.deprecation_rolling.ref = deprecation_rolling
logger.deprecation.additivity = false
"""